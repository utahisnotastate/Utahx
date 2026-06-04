"""
Utahx Semantic Cache Layer — RAM-based intent fingerprinting for API gateway.
"""

from __future__ import annotations

import hashlib
import logging
import time
from typing import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("UtahxCache")


class SemanticMemoryCore:
    """
    SOTA RAM-based caching engine.

    Intercepts repeated API requests and serves them instantly, bypassing backend processing.
    """

    def __init__(self, time_to_live_seconds: int = 60) -> None:
        self.memory_vault: dict[str, tuple[bytes, float]] = {}
        self.time_to_live = time_to_live_seconds

    def _generate_fingerprint(self, request_path: str, request_body: bytes) -> str:
        """Create a unique mathematical signature for the incoming request."""
        signature = request_path.encode("utf-8") + request_body
        return hashlib.sha256(signature).hexdigest()

    def retrieve(self, request_path: str, request_body: bytes) -> bytes | None:
        """Return cached response bytes if fingerprint is still valid."""
        fingerprint = self._generate_fingerprint(request_path, request_body)
        if fingerprint in self.memory_vault:
            data, expiration = self.memory_vault[fingerprint]
            if time.time() < expiration:
                logger.info("Semantic Cache HIT: Serving response instantly from RAM.")
                return data
            del self.memory_vault[fingerprint]
        return None

    def memorize(self, request_path: str, request_body: bytes, response_data: bytes) -> None:
        """Store processed answer in RAM for future identical requests."""
        fingerprint = self._generate_fingerprint(request_path, request_body)
        expiration = time.time() + self.time_to_live
        self.memory_vault[fingerprint] = (response_data, expiration)

    def purge_expired(self) -> int:
        """Remove expired entries; return count removed."""
        now = time.time()
        expired = [k for k, (_, exp) in self.memory_vault.items() if now >= exp]
        for key in expired:
            del self.memory_vault[key]
        return len(expired)


class SemanticCacheMiddleware(BaseHTTPMiddleware):
    """API Gateway layer: cache GET/HEAD responses by path + body fingerprint."""

    CACHEABLE_METHODS = frozenset({"GET", "HEAD"})
    SKIP_PREFIXES = ("/__utahx/",)

    def __init__(
        self,
        app: object,
        *,
        ttl_seconds: int = 60,
        cache_api_only: bool = True,
    ) -> None:
        super().__init__(app)
        self.core = SemanticMemoryCore(time_to_live_seconds=ttl_seconds)
        self.cache_api_only = cache_api_only

    def _should_cache(self, request: Request) -> bool:
        if request.method not in self.CACHEABLE_METHODS:
            return False
        if any(request.url.path.startswith(p) for p in self.SKIP_PREFIXES):
            return False
        if self.cache_api_only:
            return request.url.path.startswith("/api") or "application/json" in (
                request.headers.get("accept", "")
            )
        return True

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if not self._should_cache(request):
            return await call_next(request)

        body = await request.body()
        cached = self.core.retrieve(request.url.path, body)
        if cached is not None:
            return Response(
                content=cached,
                media_type="application/json",
                headers={"X-Utahx-Cache": "HIT"},
            )

        async def receive() -> dict[str, object]:
            return {"type": "http.request", "body": body, "more_body": False}

        replay_request = Request(request.scope, receive)
        response = await call_next(replay_request)
        if response.status_code != 200:
            return response

        chunks: list[bytes] = []
        async for chunk in response.body_iterator:
            chunks.append(chunk)
        payload = b"".join(chunks)
        self.core.memorize(request.url.path, body, payload)
        headers = dict(response.headers)
        headers["X-Utahx-Cache"] = "MISS"
        headers.pop("content-length", None)
        return Response(
            content=payload,
            status_code=response.status_code,
            headers=headers,
            media_type=response.media_type,
        )
