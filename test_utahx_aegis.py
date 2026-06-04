"""Tests for Utahx Aegis hardened router."""

from __future__ import annotations

import unittest

from utahx_core_aegis import (
    DEFAULT_DRAIN_TIMEOUT,
    DEFAULT_MAX_CONNECTIONS,
    DEFAULT_NETWORK_TIMEOUT,
    HardenedFluidRouter,
)


class TestHardenedFluidRouter(unittest.TestCase):
    def test_defaults(self) -> None:
        router = HardenedFluidRouter("127.0.0.1", 5000)
        self.assertEqual(router.network_timeout, DEFAULT_NETWORK_TIMEOUT)
        self.assertEqual(router.drain_timeout, DEFAULT_DRAIN_TIMEOUT)
        self.assertFalse(router.is_shutting_down)

    def test_viscosity_inherited(self) -> None:
        router = HardenedFluidRouter("127.0.0.1", 5000, max_flow_rate=10)
        for _ in range(15):
            router.request_timestamps.append(__import__("time").time())
        delay = router._calculate_viscosity()
        self.assertGreater(delay, 0.0)

    def test_shutdown_sets_flag(self) -> None:
        router = HardenedFluidRouter("127.0.0.1", 5000)
        import asyncio

        async def run() -> None:
            await router.shutdown()
            self.assertTrue(router.is_shutting_down)

        asyncio.run(run())

    def test_connection_semaphore_capacity(self) -> None:
        router = HardenedFluidRouter(
            "127.0.0.1",
            5000,
            max_connections=2,
        )
        self.assertIsNotNone(router.connection_limit)
        self.assertFalse(router.connection_limit.locked())


if __name__ == "__main__":
    unittest.main()
