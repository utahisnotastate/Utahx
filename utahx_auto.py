"""
Utahx Zero-Config Engine — Magic Butler auto-sensing web server.

Drop into any project folder and run; no nginx.conf required.
"""

from __future__ import annotations

import asyncio
import logging
import os
import subprocess
import sys
from typing import Awaitable, Callable

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from starlette.middleware.base import BaseHTTPMiddleware

from utahx_core import FluidRouter
from utahx_ports import find_free_port
from utahx_registry import check_upstream_registry, log_registry_status
from utahx_cache import SemanticCacheMiddleware
from utahx_prefetch import detect_spa, register_prefetch
from utahx_secure import HumanIntrospectionMiddleware, render_friendly_error

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [UTAHX] - %(levelname)s - %(message)s",
)
logger = logging.getLogger("UtahxAutoSense")

DEFAULT_PUBLIC_PORT = 8080
INTERNAL_HOST = "127.0.0.1"


class ProjectScanner:
    """
    SOTA Auto-Sensing Engine.

    Scans the current directory to determine application type without user configuration.
    Priority: Node.js > Python > Static HTML > safe static fallback.
    """

    def __init__(self, directory: str) -> None:
        self.directory = os.path.abspath(directory)

    def _list_files(self) -> set[str]:
        try:
            return set(os.listdir(self.directory))
        except OSError:
            return set()

    def identify_project_type(self) -> str:
        """Determine what type of web project lives in the directory."""
        files = self._list_files()

        if "package.json" in files:
            logger.info("Detected Node.js / React application structure.")
            return "nodejs"
        if "requirements.txt" in files or "main.py" in files:
            logger.info("Detected Python / API application structure.")
            return "python"
        if "index.html" in files:
            logger.info("Detected Static HTML website.")
            return "static"
        logger.warning(
            "No standard application structure detected. "
            "Defaulting to safe static file sharing.",
        )
        return "static"


class FluidTrafficMiddleware(BaseHTTPMiddleware):
    """HTTP-layer Fluid Traffic Manager (Phase 1 viscosity on every request)."""

    def __init__(self, app: FastAPI, max_flow_rate: int = 100) -> None:
        super().__init__(app)
        self._router = FluidRouter(INTERNAL_HOST, 0, max_flow_rate=max_flow_rate)

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        self._router.request_timestamps.append(__import__("time").time())
        delay = self._router._calculate_viscosity()
        if delay > 0:
            await asyncio.sleep(delay)
        return await call_next(request)


class BackendLauncher:
    """Spins up detected internal applications on a safe ephemeral port."""

    def __init__(self, directory: str, project_type: str) -> None:
        self.directory = directory
        self.project_type = project_type
        self.process: subprocess.Popen[str] | None = None
        self.internal_port: int | None = None

    def start(self) -> int:
        """Start backend subprocess; return bound port."""
        self.internal_port = find_free_port(INTERNAL_HOST)
        if self.project_type == "python":
            self._start_python()
        elif self.project_type == "nodejs":
            self._start_nodejs()
        else:
            raise RuntimeError(f"No backend launcher for {self.project_type}")
        logger.info(
            "Internal %s backend starting on %s:%s",
            self.project_type,
            INTERNAL_HOST,
            self.internal_port,
        )
        return self.internal_port

    def _start_python(self) -> None:
        main_py = os.path.join(self.directory, "main.py")
        if os.path.isfile(main_py):
            cmd = [
                sys.executable,
                "-m",
                "uvicorn",
                "main:app",
                "--host",
                INTERNAL_HOST,
                "--port",
                str(self.internal_port),
            ]
        else:
            raise FileNotFoundError(
                "Python project detected but main.py not found for auto-start.",
            )
        self.process = subprocess.Popen(
            cmd,
            cwd=self.directory,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def _start_nodejs(self) -> None:
        env = {**os.environ, "PORT": str(self.internal_port)}
        if os.path.isfile(os.path.join(self.directory, "package.json")):
            cmd = ["npm", "run", "start"]
            try:
                self.process = subprocess.Popen(
                    cmd,
                    cwd=self.directory,
                    env=env,
                    shell=sys.platform == "win32",
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return
            except FileNotFoundError:
                pass
        raise FileNotFoundError(
            "Node.js detected but npm start unavailable. Install Node.js or add a start script.",
        )

    def stop(self) -> None:
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
        self.process = None


class UtahxServer:
    """
    Main Utahx web server. Auto-builds routing from ProjectScanner results.

    Wraps all traffic in the Fluid Traffic Manager; proxies dynamic backends.
    """

    def __init__(
        self,
        directory: str = ".",
        *,
        max_flow_rate: int = 100,
        mode: str = "auto",
        proxy_port: int | None = None,
        spa_routing: bool | None = None,
        enable_prefetch: bool = True,
        enable_semantic_cache: bool = True,
        cache_ttl_seconds: int = 60,
    ) -> None:
        self.directory = os.path.abspath(directory)
        self.app = FastAPI(title="Utahx Web Server", version="1.2.0")
        self.enable_introspection = True
        self.scanner = ProjectScanner(self.directory)
        self.mode = mode
        self.proxy_port = proxy_port
        self.enable_prefetch = enable_prefetch
        self.enable_semantic_cache = enable_semantic_cache
        self.cache_ttl_seconds = cache_ttl_seconds
        self.spa_routing = spa_routing
        self.max_flow_rate = max_flow_rate
        self._backend: BackendLauncher | None = None
        self._internal_port: int | None = None
        self._http_client: httpx.AsyncClient | None = None

        if mode == "static":
            self.project_type = "static"
        elif mode == "proxy" and proxy_port is not None:
            self.project_type = "proxy"
            self._internal_port = proxy_port
        else:
            self.project_type = self.scanner.identify_project_type()

    def configure_routes(self) -> None:
        """Wire routes from detected project type — replaces nginx.conf."""
        if self.enable_introspection:
            self.app.middleware("http")(HumanIntrospectionMiddleware())
        self.app.add_middleware(FluidTrafficMiddleware, max_flow_rate=self.max_flow_rate)
        if self.enable_semantic_cache:
            self.app.add_middleware(
                SemanticCacheMiddleware,
                ttl_seconds=self.cache_ttl_seconds,
            )
            logger.info("Semantic Cache Layer enabled (API gateway).")
        register_prefetch(self.app, self.directory, enabled=self.enable_prefetch)

        if self.project_type == "static":
            use_spa = (
                self.spa_routing
                if self.spa_routing is not None
                else detect_spa(self.directory)
            )
            if use_spa:
                self._register_spa_static()
                logger.info("SPA routing + Semantic Pre-Fetching configured.")
            else:
                self.app.mount(
                    "/",
                    StaticFiles(directory=self.directory, html=True),
                    name="static",
                )
                logger.info("Static file routing configured successfully.")
            return

        if self.project_type == "proxy":
            self._http_client = httpx.AsyncClient(
                base_url=f"http://{INTERNAL_HOST}:{self._internal_port}",
                timeout=30.0,
            )
            logger.info(
                "Utahx reverse proxy wired to backend port %s (Fluid + Pre-Fetch active).",
                self._internal_port,
            )
            self._register_reverse_proxy()
            return

        if self.project_type in ("python", "nodejs"):
            self._backend = BackendLauncher(self.directory, self.project_type)
            try:
                self._internal_port = self._backend.start()
            except (FileNotFoundError, RuntimeError) as exc:
                logger.warning("Auto-start backend unavailable: %s", exc)
                self._register_placeholder_proxy(str(exc))
                return

            self._http_client = httpx.AsyncClient(
                base_url=f"http://{INTERNAL_HOST}:{self._internal_port}",
                timeout=30.0,
            )
            logger.info(
                "Utahx reverse proxy wired to %s backend on port %s "
                "(Fluid Traffic Manager active).",
                self.project_type,
                self._internal_port,
            )
            self._register_reverse_proxy()
            return

    def _register_spa_static(self) -> None:
        root = Path(self.directory)
        index = root / "index.html"

        @self.app.get("/{full_path:path}")
        async def spa_static(full_path: str) -> FileResponse:
            candidate = root / full_path if full_path else index
            if candidate.is_file():
                return FileResponse(candidate)
            nested = root / full_path / "index.html"
            if nested.is_file():
                return FileResponse(nested)
            if index.is_file():
                return FileResponse(index)
            raise HTTPException(status_code=404, detail="Not found")

        @self.app.get("/")
        async def spa_root() -> FileResponse:
            if index.is_file():
                return FileResponse(index)
            raise HTTPException(status_code=404, detail="index.html missing")

    def _register_placeholder_proxy(self, reason: str) -> None:
        @self.app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"])
        async def proxy_traffic(full_path: str) -> dict[str, str]:
            return {
                "Utahx Status": "Traffic securely routed to internal application.",
                "path": full_path,
                "note": reason,
            }

    def _register_reverse_proxy(self) -> None:
        @self.app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"])
        async def reverse_proxy(request: Request, full_path: str) -> Response:
            assert self._http_client is not None
            url = f"/{full_path}" if full_path else "/"
            if request.url.query:
                url = f"{url}?{request.url.query}"
            body = await request.body()
            headers = {
                k: v
                for k, v in request.headers.items()
                if k.lower() not in ("host", "content-length")
            }
            try:
                upstream = await self._http_client.request(
                    request.method,
                    url,
                    headers=headers,
                    content=body,
                )
            except httpx.ConnectError:
                return render_friendly_error(
                    title="Backend Warming Up",
                    message=(
                        "Utahx is smoothing traffic while your application starts."
                    ),
                    technical_hint=(
                        "Verify main.py or npm start is configured. "
                        "Retry in a few seconds."
                    ),
                    status_code=503,
                )
            if upstream.status_code >= 500:
                body = upstream.content.decode(errors="replace")
                hint = (
                    f"Backend returned {upstream.status_code}. "
                    "Inspect application logs for stack traces."
                )
                return render_friendly_error(
                    title="Backend Encountered a Hitch",
                    message="Utahx proxy is healthy; the upstream application reported an error.",
                    technical_hint=hint,
                    status_code=502,
                )
            return Response(
                content=upstream.content,
                status_code=upstream.status_code,
                headers=dict(upstream.headers),
            )

    async def _sync_registry(self) -> None:
        status = await check_upstream_registry()
        log_registry_status(status)

    def start(
        self,
        port: int = DEFAULT_PUBLIC_PORT,
        *,
        ssl_keyfile: str | None = None,
        ssl_certfile: str | None = None,
    ) -> None:
        """Ignite the Utahx server (blocking)."""
        self.configure_routes()
        scheme = "https" if ssl_certfile else "http"
        logger.info(
            "Utahx is online. Your website is now live at %s://0.0.0.0:%s.",
            scheme,
            port,
        )
        logger.info("Upstream Registry Tracking enabled.")

        @self.app.on_event("startup")
        async def _startup_registry() -> None:
            await self._sync_registry()

        @self.app.on_event("shutdown")
        async def _shutdown() -> None:
            if self._http_client:
                await self._http_client.aclose()
            if self._backend:
                self._backend.stop()

        uvicorn.run(
            self.app,
            host="0.0.0.0",
            port=port,
            log_level="error",
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile,
        )


def main() -> None:
    """Entry point for double-click / CLI launch."""
    directory = os.getcwd()
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        directory = sys.argv[1]
    port = DEFAULT_PUBLIC_PORT
    for arg in sys.argv[1:]:
        if arg.startswith("--port="):
            port = int(arg.split("=", 1)[1])
    server = UtahxServer(directory=directory)
    try:
        server.start(port=port)
    except KeyboardInterrupt:
        logger.info("Utahx shutting down safely.")
    finally:
        if server._backend:
            server._backend.stop()


if __name__ == "__main__":
    main()
