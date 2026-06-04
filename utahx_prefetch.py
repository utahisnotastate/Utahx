"""
Utahx Semantic Pre-Fetching — predictive next-page streaming.

Analyzes pointer trajectory and page context to warm browser cache before click.
"""

from __future__ import annotations

import logging
import math
import os
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("UtahxPrefetch")

PREFETCH_SCRIPT_PATH = "/__utahx/prefetch/utahx.js"
PREFETCH_API_SIGNAL = "/__utahx/prefetch/signal"
PREFETCH_API_MANIFEST = "/__utahx/prefetch/manifest"


@dataclass(frozen=True, slots=True)
class LinkTarget:
    href: str
    text: str
    x: float
    y: float
    width: float
    height: float


class _LinkExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        attr = dict(attrs)
        href = attr.get("href") or ""
        if href and not href.startswith(("#", "javascript:", "mailto:")):
            self.links.append((href, ""))

    def handle_data(self, data: str) -> None:
        if self.links:
            href, text = self.links[-1]
            self.links[-1] = (href, (text + data).strip())


class SemanticPrefetchEngine:
    """
    Microscopic predictive model for next navigation.

    Combines page link graph, pointer position, movement vector, and hover state.
    """

    def __init__(self, site_root: str) -> None:
        self.site_root = Path(site_root).resolve()
        self._page_cache: dict[str, list[LinkTarget]] = {}

    def discover_links(self, page_path: str) -> list[LinkTarget]:
        """Extract navigable anchors from local HTML for the active page."""
        if page_path in self._page_cache:
            return self._page_cache[page_path]

        normalized = page_path.strip("/") or "index.html"
        if not normalized.endswith(".html"):
            normalized = f"{normalized}/index.html" if (self.site_root / normalized).is_dir() else normalized
        candidates = [
            self.site_root / normalized,
            self.site_root / "index.html",
        ]
        html_path = next((p for p in candidates if p.is_file()), None)
        if html_path is None:
            return []

        raw = html_path.read_text(encoding="utf-8", errors="ignore")
        parser = _LinkExtractor()
        parser.feed(raw)
        targets: list[LinkTarget] = []
        for idx, (href, text) in enumerate(parser.links):
            resolved = self._resolve_href(page_path, href)
            if not resolved:
                continue
            row = idx // 4
            col = idx % 4
            targets.append(
                LinkTarget(
                    href=resolved,
                    text=text or href,
                    x=80.0 + col * 180.0,
                    y=120.0 + row * 48.0,
                    width=160.0,
                    height=32.0,
                ),
            )
        self._page_cache[page_path] = targets
        return targets

    def _resolve_href(self, page_path: str, href: str) -> str | None:
        if href.startswith("http://") or href.startswith("https://"):
            return None
        base_parts = [p for p in page_path.strip("/").split("/") if p]
        if base_parts and base_parts[-1].endswith(".html"):
            base_parts = base_parts[:-1]
        href_parts = [p for p in href.replace("\\", "/").split("/") if p]
        parts = base_parts.copy()
        for segment in href_parts:
            if segment == "..":
                if parts:
                    parts.pop()
            elif segment != ".":
                parts.append(segment)
        return "/" + "/".join(parts) if parts else "/"

    def predict(
        self,
        *,
        page_path: str,
        mouse_x: float,
        mouse_y: float,
        viewport_w: float,
        viewport_h: float,
        velocity_x: float = 0.0,
        velocity_y: float = 0.0,
        hovered_href: str | None = None,
        limit: int = 3,
    ) -> list[dict[str, Any]]:
        """Score candidate next pages; return top URLs to pre-stream."""
        links = self.discover_links(page_path)
        if not links:
            return []

        scores: list[tuple[float, LinkTarget]] = []
        for link in links:
            score = self._score_link(
                link,
                mouse_x=mouse_x,
                mouse_y=mouse_y,
                viewport_w=viewport_w,
                viewport_h=viewport_h,
                velocity_x=velocity_x,
                velocity_y=velocity_y,
                hovered_href=hovered_href,
            )
            scores.append((score, link))

        scores.sort(key=lambda item: item[0], reverse=True)
        results: list[dict[str, Any]] = []
        seen: set[str] = set()
        for score, link in scores:
            if link.href in seen or score <= 0:
                continue
            seen.add(link.href)
            results.append(
                {
                    "url": link.href,
                    "score": round(score, 4),
                    "label": link.text,
                },
            )
            if len(results) >= limit:
                break
        return results

    def _score_link(
        self,
        link: LinkTarget,
        *,
        mouse_x: float,
        mouse_y: float,
        viewport_w: float,
        viewport_h: float,
        velocity_x: float,
        velocity_y: float,
        hovered_href: str | None,
    ) -> float:
        cx = link.x + link.width / 2
        cy = link.y + link.height / 2
        dist = math.hypot(mouse_x - cx, mouse_y - cy)
        proximity = 1.0 / (1.0 + dist / 120.0)

        direction_bonus = 0.0
        speed = math.hypot(velocity_x, velocity_y)
        if speed > 0.5:
            to_x, to_y = cx - mouse_x, cy - mouse_y
            dot = velocity_x * to_x + velocity_y * to_y
            direction_bonus = max(0.0, dot / (speed * (math.hypot(to_x, to_y) + 1.0)))

        hover_bonus = 3.0 if hovered_href and hovered_href == link.href else 0.0
        viewport_center_bias = 1.0 - (
            abs(cx - viewport_w / 2) / max(viewport_w, 1.0)
            + abs(cy - viewport_h / 2) / max(viewport_h, 1.0)
        ) * 0.25
        return proximity * 2.0 + direction_bonus * 1.5 + hover_bonus + viewport_center_bias


def create_prefetch_router(engine: SemanticPrefetchEngine) -> APIRouter:
    router = APIRouter(prefix="/__utahx/prefetch", tags=["utahx-prefetch"])

    @router.get("/manifest")
    async def manifest(path: str = "/") -> JSONResponse:
        links = engine.discover_links(path)
        return JSONResponse(
            {
                "path": path,
                "links": [
                    {"url": t.href, "label": t.text, "x": t.x, "y": t.y}
                    for t in links
                ],
            },
        )

    @router.post("/signal")
    async def signal(request: Request) -> JSONResponse:
        payload = await request.json()
        predictions = engine.predict(
            page_path=str(payload.get("path", "/")),
            mouse_x=float(payload.get("mx", 0)),
            mouse_y=float(payload.get("my", 0)),
            viewport_w=float(payload.get("vw", 1280)),
            viewport_h=float(payload.get("vh", 720)),
            velocity_x=float(payload.get("vx", 0)),
            velocity_y=float(payload.get("vy", 0)),
            hovered_href=payload.get("hovered"),
        )
        return JSONResponse({"prefetch": predictions})

    @router.get("/utahx.js")
    async def client_script() -> PlainTextResponse:
        return PlainTextResponse(
            PREFETCH_CLIENT_JS,
            media_type="application/javascript",
        )

    return router


class PrefetchInjectMiddleware(BaseHTTPMiddleware):
    """Injects semantic pre-fetch client into HTML responses."""

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        response = await call_next(request)
        if request.url.path.startswith("/__utahx/"):
            return response
        content_type = response.headers.get("content-type", "")
        if "text/html" not in content_type:
            return response
        body = b""
        async for chunk in response.body_iterator:
            body += chunk
        text = body.decode("utf-8", errors="ignore")
        if "</body>" in text.lower() and PREFETCH_SCRIPT_PATH not in text:
            injection = f'<script src="{PREFETCH_SCRIPT_PATH}" defer></script>'
            text = re.sub(
                r"</body>",
                f"{injection}</body>",
                text,
                count=1,
                flags=re.IGNORECASE,
            )
        headers = dict(response.headers)
        headers.pop("content-length", None)
        return HTMLResponse(content=text, status_code=response.status_code, headers=headers)


def register_prefetch(app: FastAPI, site_root: str, *, enabled: bool = True) -> SemanticPrefetchEngine | None:
    if not enabled:
        return None
    engine = SemanticPrefetchEngine(site_root)
    app.include_router(create_prefetch_router(engine))
    app.add_middleware(PrefetchInjectMiddleware)
    logger.info("Semantic Pre-Fetching enabled.")
    return engine


def detect_spa(site_root: str) -> bool:
    """Heuristic: SPA if index.html exists with client router markers."""
    index = Path(site_root) / "index.html"
    if not index.is_file():
        return False
    text = index.read_text(encoding="utf-8", errors="ignore").lower()
    markers = ("react", "vue", "ng-app", "single-page", "root\"></div>", "id=\"root\"")
    return any(m in text for m in markers)


PREFETCH_CLIENT_JS = """
(function () {
  var state = { mx: 0, my: 0, vx: 0, vy: 0, lastT: Date.now(), hovered: null };
  var prefetched = {};

  function tick(e) {
    var now = Date.now();
    var dt = Math.max(now - state.lastT, 1);
    state.vx = (e.clientX - state.mx) / dt;
    state.vy = (e.clientY - state.my) / dt;
    state.mx = e.clientX;
    state.my = e.clientY;
    state.lastT = now;
  }

  document.addEventListener("mousemove", tick, { passive: true });
  document.addEventListener("mouseover", function (e) {
    var a = e.target && e.target.closest ? e.target.closest("a") : null;
    state.hovered = a ? a.getAttribute("href") : null;
  }, { passive: true });

  function warm(url) {
    if (!url || prefetched[url]) return;
    prefetched[url] = true;
    var link = document.createElement("link");
    link.rel = "prefetch";
    link.href = url;
    document.head.appendChild(link);
    if (window.fetch) {
      fetch(url, { credentials: "same-origin", priority: "low" }).catch(function () {});
    }
  }

  function signal() {
    fetch("/__utahx/prefetch/signal", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        path: location.pathname,
        mx: state.mx,
        my: state.my,
        vw: window.innerWidth,
        vh: window.innerHeight,
        vx: state.vx,
        vy: state.vy,
        hovered: state.hovered
      })
    }).then(function (r) { return r.json(); })
      .then(function (data) {
        (data.prefetch || []).forEach(function (item) { warm(item.url); });
      }).catch(function () {});
  }

  setInterval(signal, 400);
  signal();
})();
""".strip()
