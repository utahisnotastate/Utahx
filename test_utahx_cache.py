"""Zero-bug policy tests for Utahx semantic cache."""

from __future__ import annotations

import time
import unittest

from utahx_cache import SemanticMemoryCore


class TestUtahxCache(unittest.TestCase):
    def setUp(self) -> None:
        self.cache = SemanticMemoryCore(time_to_live_seconds=1)

    def test_memory_storage_and_retrieval(self) -> None:
        path = "/api/data"
        body = b"user_id=123"
        server_answer = b"{'status': 'success', 'data': 'Top Secret Info'}"

        self.cache.memorize(path, body, server_answer)
        retrieved_answer = self.cache.retrieve(path, body)
        self.assertEqual(
            retrieved_answer,
            server_answer,
            "The cache failed to return the memorized data.",
        )

    def test_memory_expiration(self) -> None:
        path = "/api/temporary"
        body = b""
        server_answer = b"Expiring Data"

        self.cache.memorize(path, body, server_answer)
        time.sleep(1.1)
        retrieved_answer = self.cache.retrieve(path, body)
        self.assertIsNone(
            retrieved_answer,
            "The cache returned data that should have been deleted.",
        )

    def test_different_body_misses(self) -> None:
        path = "/api/data"
        self.cache.memorize(path, b"a=1", b"one")
        self.assertIsNone(self.cache.retrieve(path, b"a=2"))


if __name__ == "__main__":
    unittest.main()
