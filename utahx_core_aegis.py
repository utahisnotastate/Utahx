"""
Utahx Aegis Protocol — edge-case hardened TCP fluid router.

Survives Slowloris, connection floods, malformed streams, and graceful restarts.
"""

from __future__ import annotations

import asyncio
import logging
import signal
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING

from fluid_dynamics import measure_flow, navier_stokes_viscosity_delay
from utahx_core import FluidRouter

if TYPE_CHECKING:
    from asyncio import StreamReader, StreamWriter

logger = logging.getLogger("AegisRouter")

DEFAULT_NETWORK_TIMEOUT = 5.0
DEFAULT_MAX_CONNECTIONS = 1000
DEFAULT_DRAIN_TIMEOUT = 30.0
DEFAULT_LOG_FILE = "utahx_access.log"


def setup_aegis_logging(log_path: str | Path = DEFAULT_LOG_FILE) -> None:
    """Enterprise logging to file and console."""
    root = logging.getLogger()
    if any(isinstance(h, logging.FileHandler) for h in root.handlers):
        return
    formatter = logging.Formatter(
        "%(asctime)s - [UTAHX] - %(levelname)s - [%(name)s] - %(message)s",
    )
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    root.setLevel(logging.INFO)
    root.addHandler(file_handler)
    root.addHandler(stream_handler)


class HardenedFluidRouter(FluidRouter):
    """
    SOTA edge-case resilient load balancer.

    Extends FluidRouter with connection caps, read/write timeouts, and graceful drain.
    """

    def __init__(
        self,
        backend_host: str,
        backend_port: int,
        max_flow_rate: int = 100,
        max_connections: int = DEFAULT_MAX_CONNECTIONS,
        network_timeout: float = DEFAULT_NETWORK_TIMEOUT,
        drain_timeout: float = DEFAULT_DRAIN_TIMEOUT,
    ) -> None:
        super().__init__(backend_host, backend_port, max_flow_rate=max_flow_rate)
        self.connection_limit = asyncio.Semaphore(max_connections)
        self.network_timeout = network_timeout
        self.drain_timeout = drain_timeout
        self.is_shutting_down = False
        self._active_handlers: set[asyncio.Task[None]] = set()

    async def apply_viscosity_gate(self) -> None:
        """Fluid dampening before backend connect (reuses Reynolds engine)."""
        self.request_timestamps.append(time.time())
        delay = self._calculate_viscosity()
        if delay > 0:
            await asyncio.sleep(delay)

    async def handle_client(
        self,
        reader: StreamReader,
        writer: StreamWriter,
    ) -> None:
        """Intercept connections with caps, timeouts, and shutdown guard."""
        if self.is_shutting_down:
            writer.close()
            await writer.wait_closed()
            return

        client_addr = writer.get_extra_info("peername")

        if self.connection_limit.locked():
            logger.warning("Connection limit reached. Dropping %s", client_addr)
            writer.close()
            await writer.wait_closed()
            return

        async with self.connection_limit:
            handler_task = asyncio.current_task()
            if handler_task is not None:
                self._active_handlers.add(handler_task)

            try:
                await self.apply_viscosity_gate()

                try:
                    backend_reader, backend_writer = await asyncio.wait_for(
                        asyncio.open_connection(
                            self.backend_host,
                            self.backend_port,
                        ),
                        timeout=self.network_timeout,
                    )
                except TimeoutError:
                    logger.error("Backend timeout for %s. Dropping.", client_addr)
                    return

                client_to_backend = asyncio.create_task(
                    self._bridge_streams(
                        reader,
                        backend_writer,
                        f"client {client_addr}",
                    ),
                )
                backend_to_client = asyncio.create_task(
                    self._bridge_streams(
                        backend_reader,
                        writer,
                        "backend",
                    ),
                )
                await asyncio.gather(client_to_backend, backend_to_client)

            except Exception as exc:
                logger.error("Stream fault for %s: %s", client_addr, exc)
            finally:
                writer.close()
                await writer.wait_closed()
                if handler_task is not None:
                    self._active_handlers.discard(handler_task)

    async def _bridge_streams(
        self,
        source: StreamReader,
        destination: StreamWriter,
        identity: str = "stream",
    ) -> None:
        """Transfer data with strict inactivity timeouts (Slowloris defense)."""
        try:
            while not self.is_shutting_down:
                data = await asyncio.wait_for(
                    source.read(8192),
                    timeout=self.network_timeout,
                )
                if not data:
                    break
                destination.write(data)
                await asyncio.wait_for(
                    destination.drain(),
                    timeout=self.network_timeout,
                )
        except TimeoutError:
            logger.warning("Timeout reading from %s. Terminating stream.", identity)
        except ConnectionResetError:
            logger.info("Connection reset by %s.", identity)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.debug("Bridge ended for %s: %s", identity, exc)
        finally:
            if destination.can_write_eof():
                try:
                    destination.write_eof()
                except (ConnectionResetError, BrokenPipeError, OSError):
                    pass

    async def shutdown(self, server: asyncio.Server | None = None) -> None:
        """
        Graceful drain: reject new clients, wait up to drain_timeout, close server.
        """
        if self.is_shutting_down:
            return
        logger.info("Shutdown signal received. Entering graceful draining mode...")
        self.is_shutting_down = True

        if server is not None:
            server.close()

        if self._active_handlers:
            logger.info(
                "Waiting up to %.0fs for %s active connection(s)...",
                self.drain_timeout,
                len(self._active_handlers),
            )
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self._active_handlers, return_exceptions=True),
                    timeout=self.drain_timeout,
                )
            except TimeoutError:
                logger.warning(
                    "Drain timeout reached; cancelling %s stuck handler(s).",
                    len(self._active_handlers),
                )
                for task in list(self._active_handlers):
                    task.cancel()

        if server is not None:
            await server.wait_closed()

        logger.info("All connections drained. Safe exit.")


async def start_hardened_server(
    listen_port: int,
    backend_port: int,
    *,
    backend_host: str = "127.0.0.1",
    host: str = "0.0.0.0",
    max_flow_rate: int = 100,
    max_connections: int = DEFAULT_MAX_CONNECTIONS,
    network_timeout: float = DEFAULT_NETWORK_TIMEOUT,
    drain_timeout: float = DEFAULT_DRAIN_TIMEOUT,
    log_path: str | Path = DEFAULT_LOG_FILE,
) -> None:
    """Start Aegis-protected Utahx TCP gateway with signal trapping."""
    setup_aegis_logging(log_path)
    router = HardenedFluidRouter(
        backend_host=backend_host,
        backend_port=backend_port,
        max_flow_rate=max_flow_rate,
        max_connections=max_connections,
        network_timeout=network_timeout,
        drain_timeout=drain_timeout,
    )
    server = await asyncio.start_server(router.handle_client, host, listen_port)
    loop = asyncio.get_running_loop()

    def _request_shutdown() -> None:
        asyncio.create_task(router.shutdown(server))

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _request_shutdown)
        except NotImplementedError:
            # Windows ProactorEventLoop has no add_signal_handler
            signal.signal(sig, lambda _s, _f: _request_shutdown())

    logger.info(
        "Aegis Engine active on %s:%s → %s:%s (max_conn=%s, timeout=%.1fs, drain=%.0fs)",
        host,
        listen_port,
        backend_host,
        backend_port,
        max_connections,
        network_timeout,
        drain_timeout,
    )
    async with server:
        try:
            await server.serve_forever()
        except asyncio.CancelledError:
            pass
        finally:
            await router.shutdown(server)


if __name__ == "__main__":
    try:
        asyncio.run(
            start_hardened_server(listen_port=8080, backend_port=5000),
        )
    except KeyboardInterrupt:
        logger.info("Aegis gateway shutdown complete.")
