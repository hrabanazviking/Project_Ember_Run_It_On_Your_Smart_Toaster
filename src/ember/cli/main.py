"""The ``ember`` console-script entry point.

Per ``docs/architecture/DOMAIN_MAP.md`` §8: this module is the
thinnest possible layer — argparse plumbing only. Behaviour lives in
:mod:`ember.spark.munnr`.

The default config root is ``~/.ember/``. Operators can override per
invocation with ``--config-root`` (useful for tests and tmp_path
fixtures). Operator configuration (Funi model, Brunnr backend, etc.)
is loaded from ``<config-root>/config/ember.{yaml,toml}`` via
:func:`ember.config.load_ember_config`; environment variables (e.g.
``OLLAMA_HOST``) overlay on top.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TextIO

from ember.config import load_ember_config
from ember.schemas.errors import ConfigError
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
    # Phase 16 (ADR 0011) — per-invocation tool override. Mutually
    # exclusive; either flag wins over the config-file value.
    tool_group = parser.add_mutually_exclusive_group()
    tool_group.add_argument(
        "--allow-tools",
        action="store_true",
        help="Enable tools for this invocation (overrides config.tools.enabled).",
    )
    tool_group.add_argument(
        "--no-tools",
        action="store_true",
        help="Disable tools for this invocation (overrides config.tools.enabled).",
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


def main(  # noqa: PLR0911,PLR0912 — top-level dispatcher legitimately returns + branches from many places
    argv: list[str] | None = None,
    *,
    stdout: TextIO | None = None,
) -> int:
    stdout = stdout if stdout is not None else sys.stdout

    parser = _build_parser()
    args = parser.parse_args(argv)
    config_root = Path(args.config_root).expanduser()

    try:
        config = load_ember_config(config_root)
    except ConfigError as exc:
        stdout.write(f"Config error: {exc}\n")
        return 1
    except OSError as exc:
        # PermissionError, FileNotFoundError-on-config-dir-parent, etc.
        # These can occur when the operator's $HOME or --config-root
        # points at a path they can't read. Surface a friendly message
        # rather than letting a traceback hit the terminal.
        stdout.write(
            f"Cannot read config from {config_root}: "
            f"{type(exc).__name__}: {exc}\n"
        )
        return 1

    config = _apply_tool_overrides(config, args)

    # First-launch redirect: any subcommand that needs the operator's
    # identity launches Hjarta first if it hasn't been written yet.
    needs_identity = args.command in {"chat", "ask"}
    if needs_identity and not has_identity(config_root):
        stdout.write("First time? Let's set up.\n\n")
        outcome = setup.run(config=config, config_root=config_root, stdout=stdout)
        if outcome != 0:
            return outcome
        stdout.write("\n")
        # Hjarta wrote ember.yaml — reload so the operator's choices
        # take effect immediately for this same invocation.
        try:
            config = load_ember_config(config_root)
        except ConfigError as exc:
            stdout.write(f"Config error after setup: {exc}\n")
            return 1
        except OSError as exc:
            stdout.write(
                f"Cannot reload config after setup: "
                f"{type(exc).__name__}: {exc}\n"
            )
            return 1
        config = _apply_tool_overrides(config, args)

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


def _apply_tool_overrides(
    config,  # type: ignore[no-untyped-def]
    args: argparse.Namespace,
):
    """Apply the per-invocation ``--allow-tools`` / ``--no-tools`` flag.

    Returns the same ``EmberConfig`` if neither flag was set, or a new
    one with ``tools.enabled`` flipped. Argparse's mutually-exclusive
    group means at most one of the two flags is true.
    """
    from dataclasses import replace  # noqa: PLC0415 — narrowly scoped

    if not getattr(args, "allow_tools", False) and not getattr(args, "no_tools", False):
        return config
    enabled = bool(args.allow_tools)
    new_tools = replace(config.tools, enabled=enabled)
    return replace(config, tools=new_tools)


__all__ = ["main"]
