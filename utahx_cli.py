"""
Utahx CLI — Universal entry point for the SOTA web server stack.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys

from utahx_auto import DEFAULT_PUBLIC_PORT, UtahxServer
from utahx_secure import AutoTLSEngine

logger = logging.getLogger("UtahxCLI")

DEV_HTTP_PORT = 8080
DEV_HTTPS_PORT = 8443
PROD_HTTP_PORT = 80
PROD_HTTPS_PORT = 443


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Utahx SOTA Web Server. Zero config required.",
        epilog="Registry: https://github.com/utahisnotastate/Utahx",
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=["start"],
        default="start",
        help="Start the server in the current directory.",
    )
    parser.add_argument(
        "--domain",
        type=str,
        default=None,
        help="Domain to automatically secure with HTTPS (ACME v2).",
    )
    parser.add_argument(
        "--email",
        type=str,
        default=None,
        help="ACME account email (default: admin@utahisnotastate.com).",
    )
    parser.add_argument(
        "--directory",
        type=str,
        default=".",
        help="Project directory to auto-sense (default: current directory).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Override listen port.",
    )
    parser.add_argument(
        "--proxy",
        type=int,
        metavar="PORT",
        default=None,
        help="Reverse-proxy all traffic to an existing app on PORT (e.g. 5000).",
    )
    parser.add_argument(
        "--static",
        action="store_true",
        help="Force static/SPA file serving from the directory.",
    )
    parser.add_argument(
        "--staging",
        action="store_true",
        help="Use Let's Encrypt staging ACME directory.",
    )
    return parser


def prompt_domain_interactive() -> str | None:
    """Beginner-friendly domain prompt for double-click launches."""
    if not sys.stdin.isatty():
        return None
    try:
        answer = input(
            "\nWhat is your domain name? (Leave blank if you don't have one): ",
        ).strip()
    except EOFError:
        return None
    return answer or None


def _resolve_port(domain: str | None, explicit: int | None) -> int:
    if explicit is not None:
        return explicit
    if domain:
        return PROD_HTTPS_PORT
    return DEV_HTTP_PORT


def _resolve_mode(args: argparse.Namespace) -> tuple[str, int | None]:
    if args.proxy is not None:
        return "proxy", args.proxy
    if args.static:
        return "static", None
    return "auto", None


def main(argv: list[str] | None = None) -> None:
    if argv is None and len(sys.argv) == 1:
        from utahx_launcher import main as launcher_main

        launcher_main()
        return

    args = build_parser().parse_args(argv)
    directory = os.path.abspath(args.directory)

    domain = args.domain
    if domain is None and args.command == "start":
        domain = prompt_domain_interactive()

    if args.command == "start":
        print("Igniting Utahx SOTA Engine...")
        mode, proxy_port = _resolve_mode(args)
        server = UtahxServer(
            directory=directory,
            mode=mode,
            proxy_port=proxy_port,
            spa_routing=True if args.static else None,
        )

        port = _resolve_port(domain, args.port)
        ssl_keyfile: str | None = None
        ssl_certfile: str | None = None

        if domain:
            print(f"Domain detected. Contacting ACME servers for {domain}...")
            tls_engine = AutoTLSEngine(
                domain=domain,
                email=args.email or "admin@utahisnotastate.com",
                directory=directory,
                staging=args.staging,
            )
            asyncio.run(tls_engine.provision_certificates())
            material = tls_engine.material
            if material:
                ssl_certfile = material.cert_path
                ssl_keyfile = material.key_path
                print(f"Secure sockets established for {domain}.")
                print(f"Booting on port {port} (HTTPS).")
            else:
                print("TLS material unavailable; falling back to HTTP.")
                port = args.port or DEV_HTTP_PORT
        else:
            print(
                f"No domain provided. Booting in local development mode on port {port}.",
            )

        try:
            server.start(
                port=port,
                ssl_keyfile=ssl_keyfile,
                ssl_certfile=ssl_certfile,
            )
        except PermissionError:
            fallback = DEV_HTTPS_PORT if ssl_keyfile else DEV_HTTP_PORT
            logger.warning(
                "Port %s requires elevated privileges; retrying on %s.",
                port,
                fallback,
            )
            server.start(
                port=fallback,
                ssl_keyfile=ssl_keyfile,
                ssl_certfile=ssl_certfile,
            )
        except KeyboardInterrupt:
            logger.info("Utahx shutting down safely.")
        finally:
            if server._backend:
                server._backend.stop()


if __name__ == "__main__":
    main()
