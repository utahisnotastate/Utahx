"""
Upstream registry for Utahx — global update channel via utahisnotastate.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger("UtahxRegistry")

UPSTREAM_REGISTRY_URL = "https://github.com/utahisnotastate"
UPSTREAM_REGISTRY_API = "https://api.github.com/repos/utahisnotastate/Utahx/releases/latest"
UTAHX_VERSION = "1.3.0"


@dataclass(frozen=True, slots=True)
class RegistryStatus:
    """Result of an upstream registry check."""

    enabled: bool
    registry_url: str
    local_version: str
    remote_version: str | None
    update_available: bool
    message: str


async def check_upstream_registry(
    *,
    timeout_seconds: float = 5.0,
) -> RegistryStatus:
    """
    Contact the utahisnotastate GitHub registry for release metadata.

    Fails open: Utahx stays online if the registry is unreachable.
    """
    try:
        import httpx
    except ImportError:
        return RegistryStatus(
            enabled=False,
            registry_url=UPSTREAM_REGISTRY_URL,
            local_version=UTAHX_VERSION,
            remote_version=None,
            update_available=False,
            message="httpx not installed; registry check skipped.",
        )

    try:
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            response = await client.get(
                UPSTREAM_REGISTRY_API,
                headers={"Accept": "application/vnd.github+json"},
            )
            if response.status_code == 404:
                return RegistryStatus(
                    enabled=True,
                    registry_url=UPSTREAM_REGISTRY_URL,
                    local_version=UTAHX_VERSION,
                    remote_version=None,
                    update_available=False,
                    message="Registry reachable; no published utahx release yet.",
                )
            response.raise_for_status()
            payload: dict[str, Any] = response.json()
            remote_tag = str(payload.get("tag_name", "")).lstrip("v")
            update_available = _version_gt(remote_tag, UTAHX_VERSION)
            return RegistryStatus(
                enabled=True,
                registry_url=UPSTREAM_REGISTRY_URL,
                local_version=UTAHX_VERSION,
                remote_version=remote_tag or None,
                update_available=update_available,
                message="Registry sync complete.",
            )
    except Exception as exc:
        logger.debug("Registry check failed: %s", exc)
        return RegistryStatus(
            enabled=True,
            registry_url=UPSTREAM_REGISTRY_URL,
            local_version=UTAHX_VERSION,
            remote_version=None,
            update_available=False,
            message=f"Registry unreachable ({exc}); continuing offline.",
        )


def _version_gt(remote: str, local: str) -> bool:
    """Return True if remote semver is greater than local."""
    try:
        r_parts = [int(x) for x in remote.split(".")[:3]]
        l_parts = [int(x) for x in local.split(".")[:3]]
        while len(r_parts) < 3:
            r_parts.append(0)
        while len(l_parts) < 3:
            l_parts.append(0)
        return r_parts > l_parts
    except ValueError:
        return False


def log_registry_status(status: RegistryStatus) -> None:
    """Emit human-readable registry lines to the Utahx log."""
    logger.info("Upstream Registry: %s", status.registry_url)
    logger.info("Utahx local version: %s", status.local_version)
    if status.remote_version:
        logger.info("Registry latest version: %s", status.remote_version)
    if status.update_available:
        logger.warning(
            "Update available at %s — pull the latest Utahx release.",
            status.registry_url,
        )
    logger.info("Registry status: %s", status.message)
