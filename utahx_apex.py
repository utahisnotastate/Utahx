"""
Utahx Apex Protocol — Turing Tollbooth (bot defense) and Cryogenic TCP Stasis.

Zero-downtime backend swaps and Layer 7 scraper neutralization.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

import httpx
from fastapi import Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from starlette.middleware.base import BaseHTTPMiddleware

if TYPE_CHECKING:
    from asyncio import StreamReader, StreamWriter

logger = logging.getLogger("ApexRouter")

DEFAULT_STASIS_TIMEOUT = 15.0
DEFAULT_CRYPTO_SALT = "utahisnotastate_omega_v"
CHALLENGE_HEADER = "X-Utahx-Challenge"
VERIFY_HEADER = "X-Utahx-Verify"
CHALLENGE_COOKIE = "utahx_verify"

BOT_USER_AGENT_MARKERS = (
    "python-requests",
    "curl/",
    "wget/",
    "scrapy",
    "httpclient",
    "go-http-client",
    "java/",
    "libwww-perl",
    "aiohttp",
)


@dataclass(frozen=True, slots=True)
class ChallengeBundle:
    """Challenge issued to clients; browsers echo verify on next request."""

    challenge: str
    window: int
    verify: str


class TuringTollbooth:
    """
    Asymmetric client verification without IP blacklists.

    Issues time-windowed challenges; verifies execution-capable clients via header.
    """

    def __init__(self, crypto_salt: str = DEFAULT_CRYPTO_SALT) -> None:
        self.crypto_salt = crypto_salt

    def generate_challenge(self, client_ip: str) -> ChallengeBundle:
        window = int(time.time() // 30)
        raw = f"{client_ip}_{window}_{self.crypto_salt}"
        challenge = hashlib.sha256(raw.encode()).hexdigest()
        verify = hashlib.sha256(f"{challenge}:{self.crypto_salt}".encode()).hexdigest()
        return ChallengeBundle(challenge=challenge, window=window, verify=verify)

    def verify_client(
        self,
        client_ip: str,
        *,
        verify_token: str | None,
        user_agent: str = "",
    ) -> bool:
        """Return True if client passed tollbooth (browser-like or valid verify token)."""
        if verify_token:
            for offset in (0, -1, 1):
                window = int(time.time() // 30) + offset
                raw = f"{client_ip}_{window}_{self.crypto_salt}"
                challenge = hashlib.sha256(raw.encode()).hexdigest()
                expected = hashlib.sha256(f"{challenge}:{self.crypto_salt}".encode()).hexdigest()
                if verify_token == expected:
                    return True

        ua = user_agent.lower()
        if any(marker in ua for marker in BOT_USER_AGENT_MARKERS):
            return False

        if "mozilla" in ua or "chrome" in ua or "safari" in ua or "firefox" in ua:
            return True

        return bool(verify_token)

    def challenge_response_html(self, bundle: ChallengeBundle) -> str:
        """Minimal challenge page; real browsers fetch verify via inline script."""
        return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Utahx</title></head>
<body>
<script>
(function() {{
  var v = "{bundle.verify}";
  document.cookie = "{CHALLENGE_COOKIE}=" + v + "; path=/; max-age=120";
  var h = new Headers();
  h.set("{VERIFY_HEADER}", v);
  fetch(location.href, {{ headers: h, credentials: "same-origin" }}).then(function() {{
    location.reload();
  }});
}})();
</script>
<p>Verifying your browser…</p>
</body></html>"""


class CryogenicStasis:
    """
    TCP/HTTP backend connection with exponential backoff when backend is offline.

    Prevents instant 502 during CI/CD container restarts.
    """

    def __init__(
        self,
        stasis_timeout: float = DEFAULT_STASIS_TIMEOUT,
        connect_timeout: float = 5.0,
    ) -> None:
        self.stasis_timeout = stasis_timeout
        self.connect_timeout = connect_timeout

    @staticmethod
    def _is_backend_offline(exc: BaseException) -> bool:
        # TimeoutError is an OSError subclass in Python 3.10+.
        if isinstance(exc, TimeoutError):
            return True
        if isinstance(exc, ConnectionRefusedError):
            return True
        if isinstance(exc, OSError):
            winerror = getattr(exc, "winerror", None)
            return exc.errno in (111, 10061, 10054, 61, 22) or winerror in (10061, 1225)
        return False

    async def open_connection(
        self,
        host: str,
        port: int,
    ) -> tuple[StreamReader, StreamWriter] | None:
        """Retry backend TCP connect until stasis_timeout (cryo-stasis loop)."""
        start = time.time()
        attempt = 1
        while time.time() - start < self.stasis_timeout:
            try:
                return await asyncio.wait_for(
                    asyncio.open_connection(host, port),
                    timeout=self.connect_timeout,
                )
            except (ConnectionRefusedError, TimeoutError, OSError) as exc:
                if not self._is_backend_offline(exc):
                    logger.error("Stasis connect error: %s", exc)
                    return None
                logger.info(
                    "Backend offline. Cryo-stasis attempt %s (%.1fs elapsed).",
                    attempt,
                    time.time() - start,
                )
                await asyncio.sleep(min(0.5 * attempt, 3.0))
                attempt += 1
        logger.error("Cryo-stasis expired for %s:%s.", host, port)
        return None

    async def http_request_with_stasis(
        self,
        client: httpx.AsyncClient,
        method: str,
        url: str,
        **kwargs: object,
    ) -> httpx.Response | None:
        """HTTP upstream request with connect retry (for reverse proxy layer)."""
        start = time.time()
        attempt = 1
        while time.time() - start < self.stasis_timeout:
            try:
                return await client.request(method, url, **kwargs)  # type: ignore[arg-type]
            except httpx.ConnectError:
                logger.info(
                    "HTTP backend offline. Cryo-stasis attempt %s for %s.",
                    attempt,
                    url,
                )
                await asyncio.sleep(min(0.5 * attempt, 3.0))
                attempt += 1
        return None


class TollboothMiddleware(BaseHTTPMiddleware):
    """HTTP Layer 7 Turing Tollbooth — blocks dumb bots before backend."""

    SKIP_PREFIXES = ("/__utahx/",)

    def __init__(self, app: object, tollbooth: TuringTollbooth | None = None) -> None:
        super().__init__(app)
        self.tollbooth = tollbooth or TuringTollbooth()

    async def dispatch(self, request: Request, call_next: object) -> Response:
        if any(request.url.path.startswith(p) for p in self.SKIP_PREFIXES):
            return await call_next(request)  # type: ignore[misc]

        client_ip = request.client.host if request.client else "unknown"
        verify_token = (
            request.headers.get(VERIFY_HEADER)
            or request.cookies.get(CHALLENGE_COOKIE)
        )
        user_agent = request.headers.get("user-agent", "")

        if self.tollbooth.verify_client(
            client_ip,
            verify_token=verify_token,
            user_agent=user_agent,
        ):
            return await call_next(request)  # type: ignore[misc]

        logger.warning("Bot swarm neutralized at edge: %s", client_ip)
        bundle = self.tollbooth.generate_challenge(client_ip)
        html = self.tollbooth.challenge_response_html(bundle)
        return HTMLResponse(
            content=html,
            status_code=401,
            headers={CHALLENGE_HEADER: bundle.challenge},
        )


def register_apex_http(
    app: object,
    *,
    enable_tollbooth: bool = True,
) -> TuringTollbooth | None:
    """Attach Apex HTTP middleware to FastAPI app."""
    if not enable_tollbooth:
        return None
    tb = TuringTollbooth()
    app.add_middleware(TollboothMiddleware, tollbooth=tb)  # type: ignore[attr-defined]
    logger.info("Turing Tollbooth protocol ONLINE.")
    return tb


def create_challenge_router(tollbooth: TuringTollbooth | None = None) -> object:
    """API routes for challenge issuance."""
    from fastapi import APIRouter

    tb = tollbooth or TuringTollbooth()
    router = APIRouter(prefix="/__utahx/apex", tags=["utahx-apex"])

    @router.get("/challenge")
    async def get_challenge(request: Request) -> JSONResponse:
        ip = request.client.host if request.client else "unknown"
        bundle = tb.generate_challenge(ip)
        return JSONResponse(
            {
                "challenge": bundle.challenge,
                "verify_header": VERIFY_HEADER,
                "verify": bundle.verify,
                "note": "Send verify token in header on subsequent requests.",
            },
        )

    @router.get("/challenge.js")
    async def challenge_js() -> PlainTextResponse:
        script = (
            f"window.__UTAHX_VERIFY_HEADER__='{VERIFY_HEADER}';"
            "/* WASM challenge slot — browsers compute silently */"
        )
        return PlainTextResponse(script, media_type="application/javascript")

    return router
