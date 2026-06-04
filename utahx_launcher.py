"""
Utahx interactive launcher — double-click friendly domain prompt.
"""

from __future__ import annotations

import sys


def prompt_domain() -> str | None:
    print("Utahx SOTA Web Server")
    print("-" * 40)
    try:
        answer = input(
            "What is your domain name? (Leave blank if you don't have one): ",
        ).strip()
    except EOFError:
        return None
    return answer or None


def main() -> None:
    domain = prompt_domain()
    argv = ["start"]
    if domain:
        argv.extend(["--domain", domain])
    from utahx_cli import main as cli_main

    cli_main(argv)


if __name__ == "__main__":
    main()
