"""
Utahx Apex Gateway — Aegis + Turing Tollbooth + Cryogenic Stasis (TCP).
"""

from __future__ import annotations

import asyncio
import logging
import signal
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from utahx_apex import VERIFY_HEADER, CryogenicStasis, TuringTollbooth
from utahx_core_aegis import (
    DEFAULT_DRAIN_TIMEOUT,
    DEFAULT_MAX_CONNECTIONS,
    DEFAULT_NETWORK_TIMEOUT,
    HardenedFluidRouter,
    setup_aegis_logging,
)

if TYPE_CHECKING:
    from asyncio import StreamReader, StreamWriter

logger = logging.getLogger("ApexRouter")


class ApexFluidRouter(HardenedFluidRouter):
    """
    Full stack: Fluid dynamics + Aegis hardening + Apex stasis + TCP tollbooth peek.
    """

    def __init__(
        self,
        backend_host: str,
        backend_port: int,
        max_flow_rate: int = 100,
        max_connections: int = DEFAULT_MAX_CONNECTIONS,
        network_timeout: float = DEFAULT_NETWORK_TIMEOUT,
        drain_timeout: float = DEFAULT_DRAIN_TIMEOUT,
        stasis_timeout: float = 15.0,
        crypto_salt: str = "utahisnotastate_omega_v",
        enable_tollbooth: bool = True,
    ) -> None:
        super().__init__(
            backend_host,
            backend_port,
            max_flow_rate=max_flow_rate,
            max_connections=max_connections,
            network_timeout=network_timeout,
            drain_timeout=drain_timeout,
        )
        self.stasis = CryogenicStasis(
            stasis_timeout=stasis_timeout,
            connect_timeout=network_timeout,
        )
        self.tollbooth = TuringTollbooth(crypto_salt=crypto_salt)
        self.enable_tollbooth = enable_tollbooth

    async def _tcp_tollbooth_check(
        self,
        reader: StreamReader,
        writer: StreamWriter,
        client_ip: str,
    ) -> bool:
        """
        Peek first HTTP bytes; block obvious automation User-Agents at TCP edge.
        """
        if not self.enable_tollbooth:
            return True
        try:
            peek = await asyncio.wait_for(reader.read(2048), timeout=2.0)
        except TimeoutError:
            return True
        if not peek:
            return True
        try:
            text = peek.decode("utf-8", errors="ignore").lower()
        except Exception:
            return True
        if any(marker in text for marker in ("python-requests", "curl/", "scrapy")):
            logger.warning("Bot swarm detected at TCP edge: %s", client_ip)
            writer.write(
                b"HTTP/1.1 401 Unauthorized\r\n"
                b"Content-Type: text/plain\r\n"
                b"Connection: close\r\n\r\n"
                b"Utahx Turing Tollbooth: automated client blocked.\r\n",
            )
            await writer.drain()
            return False
        if "x-utahx-verify" in text:
            return True
        if peek:
            writer.write(peek)
            await writer.drain()
        return True

    async def handle_client(
        self,
        reader: StreamReader,
        writer: StreamWriter,
    ) -> None:
        if self.is_shutting_down:
            writer.close()
            await writer.wait_closed()
            return

        client_addr = writer.get_extra_info("peername")
        client_ip = client_addr[0] if client_addr else "unknown"

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
                if not await self._tcp_tollbooth_check(reader, writer, client_ip):
                    return

                await self.apply_viscosity_gate()

                conn = await self.stasis.open_connection(
                    self.backend_host,
                    self.backend_port,
                )
                if conn is None:
                    writer.write(
                        b"HTTP/1.1 503 Service Unavailable\r\n"
                        b"Content-Type: text/plain\r\n"
                        b"Connection: close\r\n\r\n"
                        b"Utahx: backend warming up (cryo-stasis expired).\r\n",
                    )
                    await writer.drain()
                    return

                backend_reader, backend_writer = conn
                client_to_backend = asyncio.create_task(
                    self._bridge_streams(reader, backend_writer, f"client {client_addr}"),
                )
                backend_to_client = asyncio.create_task(
                    self._bridge_streams(backend_reader, writer, "backend"),
                )
                await asyncio.gather(client_to_backend, backend_to_client)

            except Exception as exc:
                logger.error("Apex stream fault for %s: %s", client_addr, exc)
            finally:
                writer.close()
                await writer.wait_closed()
                if handler_task is not None:
                    self._active_handlers.discard(handler_task)


async def execute_apex_engine(
    listen_port: int,
    backend_port: int,
    *,
    backend_host: str = "127.0.0.1",
    host: str = "0.0.0.0",
    max_flow_rate: int = 100,
    stasis_timeout: float = 15.0,
    log_path: str | Path = "utahx_access.log",
) -> None:
    """Start Apex + Aegis TCP gateway."""
    setup_aegis_logging(log_path)
    router = ApexFluidRouter(
        backend_host=backend_host,
        backend_port=backend_port,
        max_flow_rate=max_flow_rate,
        stasis_timeout=stasis_timeout,
    )
    server = await asyncio.start_server(router.handle_client, host, listen_port)
    loop = asyncio.get_running_loop()

    def _request_shutdown() -> None:
        asyncio.create_task(router.shutdown(server))

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _request_shutdown)
        except NotImplementedError:
            signal.signal(sig, lambda _s, _f: _request_shutdown())

    logger.info(
        "Utahx Apex Gateway active on %s:%s → %s:%s.",
        host,
        listen_port,
        backend_host,
        backend_port,
    )
    logger.info("Cryo-Stasis and Turing Tollbooth protocols ONLINE.")

    async with server:
        try:
            await server.serve_forever()
        except asyncio.CancelledError:
            pass
        finally:
            await router.shutdown(server)


if __name__ == "__main__":
    try:
        asyncio.run(execute_apex_engine(listen_port=8080, backend_port=5000))
    except KeyboardInterrupt:
        logger.info("Utahx Apex gateway shutdown complete.")
