"""Zero-bug policy tests for Utahx Zero-Config auto-sensing."""

from __future__ import annotations

import os
import shutil
import tempfile
import unittest

from utahx_auto import ProjectScanner
from utahx_registry import RegistryStatus, UTAHX_VERSION, _version_gt


class TestUtahxAutoScanner(unittest.TestCase):
    def setUp(self) -> None:
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self) -> None:
        shutil.rmtree(self.test_dir)

    def test_identify_static_website(self) -> None:
        with open(os.path.join(self.test_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write("<h1>Hello World</h1>")
        scanner = ProjectScanner(self.test_dir)
        result = scanner.identify_project_type()
        self.assertEqual(result, "static", "Utahx failed to identify a basic HTML website.")

    def test_identify_python_backend(self) -> None:
        with open(os.path.join(self.test_dir, "requirements.txt"), "w", encoding="utf-8") as f:
            f.write("fastapi\nuvicorn")
        scanner = ProjectScanner(self.test_dir)
        result = scanner.identify_project_type()
        self.assertEqual(result, "python", "Utahx failed to identify a Python backend.")

    def test_identify_python_via_main_py(self) -> None:
        with open(os.path.join(self.test_dir, "main.py"), "w", encoding="utf-8") as f:
            f.write("app = None\n")
        scanner = ProjectScanner(self.test_dir)
        self.assertEqual(scanner.identify_project_type(), "python")

    def test_identify_nodejs_over_static(self) -> None:
        with open(os.path.join(self.test_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write("<h1>Hi</h1>")
        with open(os.path.join(self.test_dir, "package.json"), "w", encoding="utf-8") as f:
            f.write('{"name":"demo","scripts":{"start":"node server.js"}}')
        scanner = ProjectScanner(self.test_dir)
        self.assertEqual(scanner.identify_project_type(), "nodejs")

    def test_empty_directory_defaults_static(self) -> None:
        scanner = ProjectScanner(self.test_dir)
        self.assertEqual(scanner.identify_project_type(), "static")


class TestUtahxRegistry(unittest.TestCase):
    def test_version_compare(self) -> None:
        self.assertTrue(_version_gt("0.3.0", "0.2.0"))
        self.assertFalse(_version_gt("0.1.0", UTAHX_VERSION))

    def test_registry_status_dataclass(self) -> None:
        status = RegistryStatus(
            enabled=True,
            registry_url="https://github.com/utahisnotastate",
            local_version=UTAHX_VERSION,
            remote_version=None,
            update_available=False,
            message="ok",
        )
        self.assertEqual(status.registry_url, "https://github.com/utahisnotastate")


if __name__ == "__main__":
    unittest.main()
