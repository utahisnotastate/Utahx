"""Zero-bug policy tests for Utahx security and introspection."""

from __future__ import annotations

import asyncio
import os
import shutil
import tempfile
import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from utahx_secure import (
    AutoTLSEngine,
    HumanIntrospectionMiddleware,
    REGISTRY_FOOTER,
    render_friendly_error,
)


class TestUtahxSecurity(unittest.TestCase):
    def setUp(self) -> None:
        self.app = FastAPI()
        self.app.middleware("http")(HumanIntrospectionMiddleware())

        @self.app.get("/crash")
        async def deliberate_crash() -> None:
            raise ValueError("Zero Division or Missing Variable!")

        @self.app.get("/missing")
        async def missing_page() -> dict[str, str]:
            from fastapi import HTTPException

            raise HTTPException(status_code=404)

        self.client = TestClient(self.app)

    def test_friendly_error_translation(self) -> None:
        response = self.client.get("/crash")
        self.assertEqual(response.status_code, 500)
        self.assertIn("text/html", response.headers["content-type"])
        self.assertIn("Your Code Encountered a Hitch", response.text)
        self.assertIn("Zero Division or Missing Variable!", response.text)
        self.assertIn(REGISTRY_FOOTER, response.text)

    def test_friendly_404_translation(self) -> None:
        response = self.client.get("/does-not-exist")
        self.assertEqual(response.status_code, 404)
        self.assertIn("Page Not Found", response.text)

    def test_render_friendly_error_escapes_html(self) -> None:
        page = render_friendly_error(
            title="<script>",
            message="ok",
            technical_hint="a & b",
            status_code=500,
        )
        self.assertNotIn("<script>", page.body.decode())
        self.assertIn("a &amp; b", page.body.decode())


class TestAutoTLSEngine(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self) -> None:
        shutil.rmtree(self.test_dir, ignore_errors=True)

    async def test_provision_dev_certificate(self) -> None:
        engine = AutoTLSEngine("utahisnotastate.com", directory=self.test_dir)
        ctx = await engine.provision_certificates()
        self.assertIsNotNone(ctx)
        material = engine.material
        assert material is not None
        self.assertTrue(os.path.isfile(material.cert_path))
        self.assertTrue(os.path.isfile(material.key_path))
        vault = os.path.join(self.test_dir, ".utahx", "vault")
        self.assertTrue(os.path.isdir(vault))
        self.assertTrue(vault.startswith(self.test_dir))
        self.assertFalse(vault.endswith(".ssl"))

    async def test_vault_cache_reuse(self) -> None:
        engine = AutoTLSEngine("cache.test", directory=self.test_dir)
        await engine.provision_certificates()
        first = engine.material
        engine2 = AutoTLSEngine("cache.test", directory=self.test_dir)
        await engine2.provision_certificates()
        self.assertEqual(engine2.material.provisioned_via, "vault-cache")
        self.assertEqual(first.cert_path, engine2.material.cert_path)


if __name__ == "__main__":
    unittest.main()
