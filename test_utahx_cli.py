"""CLI argument tests."""

from __future__ import annotations

import unittest

from utahx_cli import _resolve_mode, build_parser


class TestUtahxCLI(unittest.TestCase):
    def test_proxy_mode(self) -> None:
        args = build_parser().parse_args(["start", "--proxy", "5000"])
        mode, port = _resolve_mode(args)
        self.assertEqual(mode, "proxy")
        self.assertEqual(port, 5000)

    def test_static_mode(self) -> None:
        args = build_parser().parse_args(["start", "--static"])
        mode, port = _resolve_mode(args)
        self.assertEqual(mode, "static")
        self.assertIsNone(port)


if __name__ == "__main__":
    unittest.main()
