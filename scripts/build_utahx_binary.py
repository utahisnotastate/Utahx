#!/usr/bin/env python3
"""Build standalone utahx binary via PyInstaller."""

from __future__ import annotations

import subprocess
import sys


def compile_utahx() -> int:
    print("[UTAHX] Initiating SOTA binary compilation...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "pyinstaller"],
        check=True,
    )
    compile_command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--name",
        "utahx",
        "--clean",
        "--hidden-import",
        "uvicorn.logging",
        "--hidden-import",
        "uvicorn.loops.auto",
        "--hidden-import",
        "uvicorn.protocols.http.auto",
        "utahx_cli.py",
    ]
    try:
        subprocess.run(compile_command, check=True)
        print("[UTAHX] SUCCESS. Binary in dist/utahx (or dist/utahx.exe on Windows).")
        print("[UTAHX] Upload to GitHub Releases: github.com/utahisnotastate/Utahx")
        return 0
    except subprocess.CalledProcessError:
        print("[UTAHX] FAILED. Verify Python environment and dependencies.")
        return 1


if __name__ == "__main__":
    raise SystemExit(compile_utahx())
