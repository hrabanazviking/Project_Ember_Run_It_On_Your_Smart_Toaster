"""The ``ember`` console-script entry point.

Per ``docs/architecture/DOMAIN_MAP.md`` §8: this module is the
thinnest possible layer — argparse plumbing only. Behaviour lives in
:mod:`ember.spark.munnr`.

The default config root is ``~/.ember/``. Operators can override per
invocation with ``--config-root`` (useful for tests and tmp_path
fixtures).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TextIO

from ember.schemas.config import EmberConfig
from ember.spark.hjarta import has_identity
from ember.spark.munnr import ask, chat, doctor, ingest, setup, status

_DEFAULT_CONFIG_ROOT = Path("~/.ember/")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ember",
        description=(
            "Ember — a small, tethered, runs-anywhere AI companion. "
            "See docs/SYSTEM_VISION.md for what Ember is."
        ),
    )
    parser.add_argument(
        "--config-root",
        type=Path,
        default=_DEFAULT_CONFIG_ROOT,
        help="Where Ember's identity, secrets, well, and state live (default: ~/.ember/).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("chat", help="Open an interactive conversation.")

    ask_p = sub.add_parser("ask", help="Ask a single question and exit.")
    ask_p.add_argument("text", help="The question to ask.")

    setup_p = sub.add_parser("setup", help="Run the first-run wizard (Hjarta).")
    setup_p.add_argument(
        "--reset",
        action="store_true",
        help="Discard any existing identity and run Hjarta from scratch.",
    )

    well_p = sub.add_parser("well", help="Manage the Well.")
    well_sub = well_p.add_subparsers(dest="well_command", required=True)
    ingest_p = well_sub.add_parser("ingest", help="Ingest a local directory.")
    ingest_p.add_argument("path", type=Path, help="Directory to walk and ingest.")
    well_sub.add_parser("status", help="Show counts and health for the Well.")

    sub.add_parser("doctor", help="Diagnose Funi + Well health.")

    return parser


def main(  # noqa: PLR0911 — top-level dispatcher legitimately returns from many branches
    argv: list[str] | None = None,
    *,
    stdout: TextIO | None = None,
) -> int:
    stdout = stdout if stdout is not None else sys.stdout

    parser = _build_parser()
    args = parser.parse_args(argv)
    config_root = Path(args.config_root).expanduser()
    config = EmberConfig()

    # First-launch redirect: any subcommand that needs the operator's
    # identity launches Hjarta first if it hasn't been written yet.
    needs_identity = args.command in {"chat", "ask"}
    if needs_identity and not has_identity(config_root):
        stdout.write("First time? Let's set up.\n\n")
        outcome = setup.run(config=config, config_root=config_root, stdout=stdout)
        if outcome != 0:
            return outcome
        stdout.write("\n")

    if args.command == "chat":
        return chat.run(config=config, config_root=config_root, stdout=stdout)
    if args.command == "ask":
        return ask.run(
            text=args.text, config=config, config_root=config_root, stdout=stdout
        )
    if args.command == "setup":
        return setup.run(
            config=config,
            config_root=config_root,
            reset=args.reset,
            stdout=stdout,
        )
    if args.command == "doctor":
        return doctor.run(config=config, stdout=stdout)
    if args.command == "well":
        if args.well_command == "ingest":
            return ingest.run(path=args.path, config=config, stdout=stdout)
        if args.well_command == "status":
            return status.run(config=config, stdout=stdout)
    # argparse with required=True should make this unreachable; defensive
    # exit-code anyway.
    parser.print_help(stdout)
    return 2


__all__ = ["main"]
