"""
Utahx (Utah-X) — Layer 7 fluid-dynamic reverse proxy.

Replaces static Nginx connection queues with continuous-flow routing:
Listener → Sensor → Viscosity Engine → Backend bridge.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import TYPE_CHECKING

from fluid_dynamics import FlowState, measure_flow, navier_stokes_viscosity_delay

if TYPE_CHECKING:
    from asyncio import StreamReader, StreamWriter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [UTAHX] - %(levelname)s - %(message)s",
)
logger = logging.getLogger("UtahxCore")


class FluidRouter:
    """
    SOTA dynamic load balancer based on continuous flow monitoring.

    Replaces static Nginx worker connections with a dynamic viscosity engine
    driven by Navier-Stokes Reynolds-style turbulence detection.
    """

    def __init__(
        self,
        backend_host: str,
        backend_port: int,
        max_flow_rate: int = 100,
    ) -> None:
        self.backend_host = backend_host
        self.backend_port = backend_port
        self.request_timestamps: list[float] = []
        self.max_flow_rate = max_flow_rate
        self.current_viscosity_delay = 0.0
        self._last_flow_state: FlowState | None = None

    def _calculate_viscosity(self) -> float:
        """
        Calculates network turbulence via Reynolds monitoring.

        If flow rate exceeds the maximum boundary, increases delay (viscosity)
        to smooth the traffic wave without dropping connections.
        """
        current_time = time.time()
        self.request_timestamps = [
            t for t in self.request_timestamps if current_time - t <= 1.0
        ]

        state = measure_flow(
            self.request_timestamps,
            current_time,
            float(self.max_flow_rate),
        )
        self._last_flow_state = state

        delay = navier_stokes_viscosity_delay(
            state.flow_rate,
            state.max_flow_rate,
        )
        self.current_viscosity_delay = delay

        if delay > 0:
            logger.warning(
                "Turbulence detected. Flow rate: %s/s, Re≈%.2f, "
                "turbulence=%.3f. Applying viscosity: %.3fs",
                int(state.flow_rate),
                state.reynolds,
                state.turbulence_index,
                delay,
            )
        elif state.flow_rate > 0 and logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "Laminar flow: %s/s (Re≈%.2f)",
                int(state.flow_rate),
                state.reynolds,
            )

        return self.current_viscosity_delay

    async def handle_client(
        self,
        reader: StreamReader,
        writer: StreamWriter,
    ) -> None:
        """
        Intercepts incoming connection, applies dynamic smoothing, bridges to backend.
        """
        client_addr = writer.get_extra_info("peername")
        self.request_timestamps.append(time.time())

        delay = self._calculate_viscosity()
        if delay > 0:
            await asyncio.sleep(delay)

        try:
            backend_reader, backend_writer = await asyncio.open_connection(
                self.backend_host,
                self.backend_port,
            )
            client_to_backend = asyncio.create_task(
                self._bridge_streams(reader, backend_writer),
            )
            backend_to_client = asyncio.create_task(
                self._bridge_streams(backend_reader, writer),
            )
            await asyncio.gather(client_to_backend, backend_to_client)
        except Exception as e:
            logger.error("Backend connection failed for %s: %s", client_addr, e)
        finally:
            writer.close()
            await writer.wait_closed()

    async def _bridge_streams(
        self,
        source: StreamReader,
        destination: StreamWriter,
    ) -> None:
        """Transfers raw binary data continuously between sockets."""
        try:
            while True:
                data = await source.read(4096)
                if not data:
                    break
                destination.write(data)
                await destination.drain()
        except ConnectionResetError:
            pass
        finally:
            if destination.can_write_eof():
                destination.write_eof()


async def start_utahx(
    listen_port: int,
    backend_port: int,
    *,
    backend_host: str = "127.0.0.1",
    max_flow_rate: int = 100,
    host: str = "0.0.0.0",
    aegis: bool = True,
    apex: bool = True,
    max_connections: int = 1000,
    network_timeout: float = 5.0,
    drain_timeout: float = 30.0,
    stasis_timeout: float = 15.0,
) -> None:
    """
    Start the Utahx edge gateway listener.

    apex=True (default): Aegis + Turing Tollbooth + Cryogenic Stasis.
    aegis=True without apex: hardened router only.
    """
    if apex:
        from utahx_apex_core import execute_apex_engine

        await execute_apex_engine(
            listen_port,
            backend_port,
            backend_host=backend_host,
            host=host,
            max_flow_rate=max_flow_rate,
            stasis_timeout=stasis_timeout,
        )
        return

    if aegis:
        from utahx_core_aegis import start_hardened_server

        await start_hardened_server(
            listen_port,
            backend_port,
            backend_host=backend_host,
            host=host,
            max_flow_rate=max_flow_rate,
            max_connections=max_connections,
            network_timeout=network_timeout,
            drain_timeout=drain_timeout,
        )
        return

    router = FluidRouter(
        backend_host=backend_host,
        backend_port=backend_port,
        max_flow_rate=max_flow_rate,
    )
    server = await asyncio.start_server(
        router.handle_client,
        host,
        listen_port,
    )
    logger.info(
        "Utahx Edge Gateway active on %s:%s, routing to %s:%s (max_flow=%s/s)",
        host,
        listen_port,
        backend_host,
        backend_port,
        max_flow_rate,
    )
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(start_utahx(listen_port=8080, backend_port=5000))
    except KeyboardInterrupt:
        logger.info("Utahx Gateway shutting down safely.")
