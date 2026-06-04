"""Tests for Utahx semantic pre-fetching."""

from __future__ import annotations

import os
import shutil
import tempfile
import unittest

from utahx_prefetch import SemanticPrefetchEngine, detect_spa


class TestSemanticPrefetch(unittest.TestCase):
    def setUp(self) -> None:
        self.test_dir = tempfile.mkdtemp()
        index = os.path.join(self.test_dir, "index.html")
        with open(index, "w", encoding="utf-8") as f:
            f.write(
                '<html><body>'
                '<a href="/about">About</a>'
                '<a href="/shop">Shop</a>'
                '</body></html>',
            )

    def tearDown(self) -> None:
        shutil.rmtree(self.test_dir)

    def test_discover_links(self) -> None:
        engine = SemanticPrefetchEngine(self.test_dir)
        links = engine.discover_links("/")
        hrefs = {link.href for link in links}
        self.assertIn("/about", hrefs)
        self.assertIn("/shop", hrefs)

    def test_predict_prefers_hover_target(self) -> None:
        engine = SemanticPrefetchEngine(self.test_dir)
        preds = engine.predict(
            page_path="/",
            mouse_x=100,
            mouse_y=130,
            viewport_w=1280,
            viewport_h=720,
            hovered_href="/shop",
        )
        self.assertTrue(preds)
        self.assertEqual(preds[0]["url"], "/shop")

    def test_detect_spa_react_marker(self) -> None:
        index = os.path.join(self.test_dir, "index.html")
        with open(index, "w", encoding="utf-8") as f:
            f.write('<div id="root"></div><script>react</script>')
        self.assertTrue(detect_spa(self.test_dir))


if __name__ == "__main__":
    unittest.main()
