"""Zero-bug policy unit tests for Utahx fluid routing."""

from __future__ import annotations

import time
import unittest

from fluid_dynamics import FlowState, measure_flow, navier_stokes_viscosity_delay
from utahx_core import FluidRouter


class TestNavierStokesEngine(unittest.TestCase):
    def test_laminar_flow_state(self) -> None:
        now = time.time()
        stamps = [now] * 5
        state = measure_flow(stamps, now, max_flow_rate=10.0)
        self.assertEqual(state.flow_rate, 5.0)
        self.assertFalse(state.is_turbulent)

    def test_turbulent_flow_state(self) -> None:
        now = time.time()
        stamps = [now] * 15
        state = measure_flow(stamps, now, max_flow_rate=10.0)
        self.assertTrue(state.is_turbulent)
        self.assertGreater(state.turbulence_index, 0.0)

    def test_viscosity_delay_formula(self) -> None:
        delay = navier_stokes_viscosity_delay(15.0, 10.0)
        self.assertAlmostEqual(delay, 0.25, places=2)


class TestUtahxFluidRouter(unittest.IsolatedAsyncioTestCase):
    async def test_viscosity_calculation_normal_flow(self) -> None:
        router = FluidRouter("127.0.0.1", 5000, max_flow_rate=10)
        for _ in range(5):
            router.request_timestamps.append(time.time())
        delay = router._calculate_viscosity()
        self.assertEqual(delay, 0.0, "Delay should be 0.0 under normal load conditions.")

    async def test_viscosity_calculation_turbulent_flow(self) -> None:
        router = FluidRouter("127.0.0.1", 5000, max_flow_rate=10)
        for _ in range(15):
            router.request_timestamps.append(time.time())
        delay = router._calculate_viscosity()
        self.assertGreater(delay, 0.0, "Delay must be greater than 0.0 during traffic spikes.")
        self.assertAlmostEqual(delay, 0.25, places=2)

    async def test_flow_state_tracked_on_turbulence(self) -> None:
        router = FluidRouter("127.0.0.1", 5000, max_flow_rate=10)
        for _ in range(15):
            router.request_timestamps.append(time.time())
        router._calculate_viscosity()
        assert router._last_flow_state is not None
        self.assertIsInstance(router._last_flow_state, FlowState)
        self.assertTrue(router._last_flow_state.is_turbulent)


if __name__ == "__main__":
    unittest.main()
