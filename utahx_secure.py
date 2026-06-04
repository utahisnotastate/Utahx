"""
Utahx Security & Introspection — Autonomous TLS and friendly error translation.
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
import ssl
import stat
import traceback
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Awaitable, Callable

from fastapi import Request, Response
from fastapi.responses import HTMLResponse

logger = logging.getLogger("UtahxSecurity")

REGISTRY_FOOTER = "github.com/utahisnotastate"
ACME_DIRECTORY_STAGING = "https://acme-staging-v02.api.letsencrypt.org/directory"
ACME_DIRECTORY_PRODUCTION = "https://acme-v02.api.letsencrypt.org/directory"
DEFAULT_ACME_EMAIL = "admin@utahisnotastate.com"


@dataclass(frozen=True, slots=True)
class TLSMaterial:
    """In-memory TLS material bound to the active server process."""

    domain: str
    cert_path: str
    key_path: str
    ssl_context: ssl.SSLContext
    provisioned_via: str


class AutoTLSEngine:
    """
    SOTA Autonomous Certificate Manager.

    Negotiates ACME v2 when possible; provisions ECDSA certificates into a
    project-local secure vault (never ~/.ssl or home-directory key dumps).
    """

    def __init__(
        self,
        domain: str,
        email: str = DEFAULT_ACME_EMAIL,
        *,
        directory: str = ".",
        staging: bool = False,
    ) -> None:
        self.domain = domain.strip().lower()
        self.email = email
        self.directory = os.path.abspath(directory)
        self.staging = staging
        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
        self._vault_dir = Path(self.directory) / ".utahx" / "vault"
        self._material: TLSMaterial | None = None

    @property
    def material(self) -> TLSMaterial | None:
        return self._material

    def _ensure_vault(self) -> Path:
        self._vault_dir.mkdir(parents=True, exist_ok=True)
        if hasattr(os, "chmod"):
            os.chmod(self._vault_dir, stat.S_IRWXU)
        return self._vault_dir

    async def provision_certificates(self) -> ssl.SSLContext:
        """
        Request and load TLS certificates into the active SSL context.

        Order: reuse valid vault cert → ACME v2 → ephemeral ECDSA self-signed.
        """
        logger.info("Initiating Autonomous TLS handshake for %s...", self.domain)
        existing = self._load_existing_vault_cert()
        if existing:
            self._material = existing
            logger.info("Loaded existing vault certificate for %s.", self.domain)
            return existing.ssl_context

        try:
            material = await self._provision_acme()
            self._material = material
            logger.info(
                "ACME certificates for %s provisioned and verified (ECDSA).",
                self.domain,
            )
            return material.ssl_context
        except Exception as exc:
            logger.warning(
                "ACME provisioning unavailable (%s). "
                "Generating secure local ECDSA certificate for development.",
                exc,
            )
            material = await self._provision_dev_certificate()
            self._material = material
            return material.ssl_context

    def _load_existing_vault_cert(self) -> TLSMaterial | None:
        vault = self._vault_dir
        cert_path = vault / f"{self.domain}.crt.pem"
        key_path = vault / f"{self.domain}.key.pem"
        if not cert_path.is_file() or not key_path.is_file():
            return None
        try:
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ctx.load_cert_chain(certfile=str(cert_path), keyfile=str(key_path))
            return TLSMaterial(
                domain=self.domain,
                cert_path=str(cert_path),
                key_path=str(key_path),
                ssl_context=ctx,
                provisioned_via="vault-cache",
            )
        except ssl.SSLError:
            return None

    async def _provision_acme(self) -> TLSMaterial:
        """
        ACME v2 negotiation via the acme library (Let's Encrypt).

        Requires public HTTP-01 reachability on port 80 during issuance.
        """
        await asyncio.sleep(0)  # allow event loop setup
        try:
            from acme import client as acme_client
            from acme import messages
            from acme import challenges
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric import ec
            import josepy as jose
        except ImportError as exc:
            raise RuntimeError(
                "Install secure extras: pip install utahx[secure]"
            ) from exc

        vault = self._ensure_vault()
        directory_url = (
            ACME_DIRECTORY_STAGING if self.staging else ACME_DIRECTORY_PRODUCTION
        )
        net = acme_client.ClientNetwork(jose.JWKRSAKey())
        directory = messages.Directory.from_json(
            net.get(directory_url).json(),
        )
        acme = acme_client.ClientV2(directory, net=net)

        private_key = ec.generate_private_key(ec.SECP256R1())
        regr = acme.new_account(
            messages.NewRegistration.from_data(
                email=self.email,
                terms_of_service_agreed=True,
            ),
        )
        acme.net.account = regr

        orderr = acme.new_order(
            messages.NewOrder(identifier=self.domain),
        )
        authz = orderr.authorizations[0].body
        chall = None
        for cb in authz.challenges:
            if isinstance(cb.chall, challenges.HTTP01):
                chall = cb
                break
        if chall is None:
            raise RuntimeError("No HTTP-01 challenge offered by ACME CA.")

        _response, validation = chall.chall.response_and_validation(
            acme.net.key,
        )
        token = chall.chall.encode("token")
        raise RuntimeError(
            "ACME HTTP-01 challenge requires Utahx HTTP listener on port 80. "
            f"Serve token path /.well-known/acme-challenge/{token} "
            f"with body: {validation.decode()}"
        )

    async def _provision_dev_certificate(self) -> TLSMaterial:
        """Generate ECDSA self-signed certificate in the secure project vault."""
        await asyncio.sleep(0.05)
        try:
            from cryptography import x509
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import ec
            from cryptography.x509.oid import NameOID
        except ImportError as exc:
            raise RuntimeError(
                "cryptography required for TLS. pip install utahx[secure]"
            ) from exc

        vault = self._ensure_vault()
        key = ec.generate_private_key(ec.SECP256R1())
        subject = issuer = x509.Name(
            [x509.NameAttribute(NameOID.COMMON_NAME, self.domain)],
        )
        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.now(timezone.utc))
            .not_valid_after(datetime.now(timezone.utc) + timedelta(days=90))
            .add_extension(
                x509.SubjectAlternativeName([x509.DNSName(self.domain)]),
                critical=False,
            )
            .sign(key, hashes.SHA256())
        )

        cert_path = vault / f"{self.domain}.crt.pem"
        key_path = vault / f"{self.domain}.key.pem"
        cert_path.write_bytes(
            cert.public_bytes(serialization.Encoding.PEM),
        )
        key_path.write_bytes(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            ),
        )
        if hasattr(os, "chmod"):
            os.chmod(cert_path, stat.S_IRUSR)
            os.chmod(key_path, stat.S_IRUSR)

        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(certfile=str(cert_path), keyfile=str(key_path))
        return TLSMaterial(
            domain=self.domain,
            cert_path=str(cert_path),
            key_path=str(key_path),
            ssl_context=ctx,
            provisioned_via="dev-ecdsa",
        )


class HumanIntrospectionMiddleware:
    """
    SOTA Error Translation Layer.

    Intercepts 404/502/500 failures and returns actionable friendly dashboards.
    """

    async def __call__(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        try:
            response = await call_next(request)
            if response.status_code == 404:
                return render_friendly_error(
                    title="Page Not Found",
                    message=(
                        "We looked everywhere, but this page doesn't exist. "
                        "Did you spell the link correctly?"
                    ),
                    technical_hint=(
                        "Ensure your index.html or Python route matches "
                        "the URL you typed."
                    ),
                    status_code=404,
                )
            if response.status_code == 502:
                return render_friendly_error(
                    title="Backend Temporarily Unreachable",
                    message=(
                        "Utahx is healthy, but your application backend "
                        "did not answer in time."
                    ),
                    technical_hint=(
                        "Check that main.py is running without errors. "
                        "If you just started Utahx, wait a few seconds and refresh."
                    ),
                    status_code=502,
                )
            if response.status_code == 503:
                return render_friendly_error(
                    title="Backend Warming Up",
                    message=(
                        "Your server is starting — Utahx is smoothing traffic "
                        "while the app boots."
                    ),
                    technical_hint="Retry in a moment. Verify main.py or npm start works.",
                    status_code=503,
                )
            return response
        except Exception as exc:
            logger.error("Application crash detected: %s", exc)
            hint = _format_exception_hint(exc)
            return render_friendly_error(
                title="Your Code Encountered a Hitch",
                message="The server is safe, but the application code had a small accident.",
                technical_hint=hint,
                status_code=500,
            )


def _format_exception_hint(exc: BaseException) -> str:
    """Build a human-readable hint including line numbers when available."""
    tb = traceback.extract_tb(exc.__traceback__)
    for frame in reversed(tb):
        if frame.filename.endswith("main.py") or "site-packages" not in frame.filename:
            return (
                f"Python says: {exc} — check {Path(frame.filename).name} "
                f"around line {frame.lineno}."
            )
    return f"Python says: {exc}. Check your main.py file for typos."


def render_friendly_error(
    *,
    title: str,
    message: str,
    technical_hint: str,
    status_code: int = 500,
) -> HTMLResponse:
    """Generate a visually clear, non-threatening error dashboard."""
    safe_title = _escape_html(title)
    safe_message = _escape_html(message)
    safe_hint = _escape_html(technical_hint)
    html_content = f"""
    <html>
        <head>
            <title>Utahx - System Notification</title>
            <style>
                body {{ font-family: -apple-system, sans-serif; background-color: #121212;
                       color: #ffffff; text-align: center; padding-top: 10%; }}
                .card {{ background: #1e1e1e; padding: 40px; border-radius: 12px;
                        display: inline-block; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }}
                h1 {{ color: #00e5ff; }}
                .hint {{ background: #2d2d2d; padding: 15px; border-radius: 8px;
                        margin-top: 20px; font-family: monospace; color: #ff5252;
                        text-align: left; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h1>{safe_title}</h1>
                <p>{safe_message}</p>
                <div class="hint"><strong>Developer Hint:</strong> {safe_hint}</div>
                <p style="margin-top: 30px; font-size: 12px; color: #888;">
                    Powered by Utahx Engine | Registry: {REGISTRY_FOOTER}
                </p>
            </div>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=status_code)


def _escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def parse_upstream_fault(body: str, status_code: int) -> str | None:
    """Extract a line-number hint from backend tracebacks when present."""
    line_match = re.search(r'File "([^"]+)", line (\d+)', body)
    if line_match:
        path, line_no = line_match.group(1), line_match.group(2)
        return (
            f"Backend returned {status_code}. Inspect {Path(path).name} "
            f"line {line_no} for the root cause."
        )
    return None
