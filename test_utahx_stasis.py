"""Tests for Utahx Cryogenic Stasis and Apex tollbooth."""

from __future__ import annotations

import asyncio
import time
import unittest

from utahx_apex import CryogenicStasis, TuringTollbooth


class TestCryogenicStasis(unittest.IsolatedAsyncioTestCase):
    async def test_backend_stasis_recovery_timing(self) -> None:
        """Prove stasis waits instead of failing instantly on dead port."""
        stasis = CryogenicStasis(stasis_timeout=3.0, connect_timeout=0.2)
        start = time.time()
        result = await stasis.open_connection("127.0.0.1", 9999)
        elapsed = time.time() - start
        self.assertIsNone(result)
        self.assertGreaterEqual(
            elapsed,
            2.5,
            "Cryogenic Stasis failed; connection dropped too quickly.",
        )
        self.assertLessEqual(
            elapsed,
            5.0,
            "Cryogenic Stasis locked up indefinitely.",
        )


class TestTuringTollbooth(unittest.TestCase):
    def test_blocks_python_requests(self) -> None:
        tb = TuringTollbooth()
        self.assertFalse(
            tb.verify_client("1.2.3.4", verify_token=None, user_agent="python-requests/2.28"),
        )

    def test_accepts_valid_verify_token(self) -> None:
        tb = TuringTollbooth()
        bundle = tb.generate_challenge("10.0.0.1")
        self.assertTrue(
            tb.verify_client("10.0.0.1", verify_token=bundle.verify, user_agent=""),
        )

    def test_accepts_browser_user_agent(self) -> None:
        tb = TuringTollbooth()
        self.assertTrue(
            tb.verify_client(
                "1.2.3.4",
                verify_token=None,
                user_agent="Mozilla/5.0 Chrome/120.0",
            ),
        )


if __name__ == "__main__":
    unittest.main()
