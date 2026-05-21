"""Phase 16 CLI flags: ``--allow-tools`` / ``--no-tools``."""

from __future__ import annotations

from unittest.mock import patch

from ember.cli.main import _apply_tool_overrides, _build_parser
from ember.schemas.config import EmberConfig, ToolsConfig


def test_allow_tools_flag_flips_enabled_true() -> None:
    parser = _build_parser()
    args = parser.parse_args(["--allow-tools", "chat"])
    cfg = EmberConfig(tools=ToolsConfig(enabled=False))
    out = _apply_tool_overrides(cfg, args)
    assert out.tools.enabled is True


def test_no_tools_flag_flips_enabled_false() -> None:
    parser = _build_parser()
    args = parser.parse_args(["--no-tools", "chat"])
    cfg = EmberConfig(tools=ToolsConfig(enabled=True))
    out = _apply_tool_overrides(cfg, args)
    assert out.tools.enabled is False


def test_no_flags_leaves_config_unchanged() -> None:
    parser = _build_parser()
    args = parser.parse_args(["chat"])
    cfg = EmberConfig(tools=ToolsConfig(enabled=True))
    out = _apply_tool_overrides(cfg, args)
    assert out is cfg  # identity preserved when no flag was set


def test_allow_and_no_tools_are_mutually_exclusive() -> None:
    """argparse should refuse both flags at once."""
    parser = _build_parser()
    with patch("sys.stderr"):  # silence argparse's error message
        try:
            parser.parse_args(["--allow-tools", "--no-tools", "chat"])
        except SystemExit as exc:
            assert exc.code != 0
        else:
            raise AssertionError("expected SystemExit from mutually-exclusive flags")
