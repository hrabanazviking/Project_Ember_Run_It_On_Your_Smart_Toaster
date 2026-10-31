"""E-033 — config for humans: one surface, sane defaults, every key documented.

Pins the E-033 contract:

- The template ``config/ember.example.yaml`` documents EVERY field
  of ``EmberConfig`` (active or as a commented example) and loads
  cleanly through the real loader.
- ``.env.example`` documents exactly the environment variables the
  core reads — ``OLLAMA_HOST`` + ``EMBER_WELL_PASSWORD`` (E-013's
  live keys) — and nothing else. The Runa fossil (docket 55) is gone.
- The defaults a no-file operator gets are the sane ones: nothing
  reaches out, nothing extra starts, replies stream.
- Unknown keys — including fossil keys — are refused by name, so
  the one surface cannot silently fork.
- The excerpt files in ``config/`` state plainly that they are not
  separate config files (docket 56, core half).
"""

from __future__ import annotations

import dataclasses
import re
import typing
from pathlib import Path

import pytest

from ember.config import load_ember_config
from ember.schemas.config import EmberConfig
from ember.schemas.errors import ConfigError

REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = REPO_ROOT / "config" / "ember.example.yaml"
ENV_EXAMPLE = REPO_ROOT / ".env.example"

LIVE_ENV_VARS = {"OLLAMA_HOST", "EMBER_WELL_PASSWORD"}


def _leaf_paths(cls: type, prefix: str = "") -> list[str]:
    """Every leaf field path of a config dataclass tree."""
    hints = typing.get_type_hints(cls)
    out: list[str] = []
    for f in dataclasses.fields(cls):
        path = f"{prefix}.{f.name}" if prefix else f.name
        t = hints[f.name]
        candidates = [t, *[a for a in typing.get_args(t) if a is not type(None)]]
        nested = None
        for cand in candidates:
            if dataclasses.is_dataclass(cand) and isinstance(cand, type):
                nested = cand
            if typing.get_origin(cand) is tuple:
                for arg in typing.get_args(cand):
                    if dataclasses.is_dataclass(arg):
                        nested = arg
        if nested is not None:
            out.extend(_leaf_paths(nested, path))
        else:
            out.append(path)
    return out


def test_template_documents_every_config_key() -> None:
    text = EXAMPLE.read_text(encoding="utf-8")
    missing = []
    for path in _leaf_paths(EmberConfig):
        leaf = path.rsplit(".", 1)[-1]
        # Active key or commented example key, at any indent.
        if not re.search(rf"^\s*(?:#\s*)*-?\s*{re.escape(leaf)}\s*:", text, re.M):
            missing.append(path)
    assert missing == [], f"keys missing from ember.example.yaml: {missing}"


def test_template_loads_through_real_loader(tmp_path: Path) -> None:
    target = tmp_path / "ember.yaml"
    target.write_text(EXAMPLE.read_text(encoding="utf-8"), encoding="utf-8")
    loaded = load_ember_config(file_override=target, skip_env=True)
    defaults = EmberConfig()
    # The template states the defaults; the only deliberate
    # difference is logging, where the template shows a worked
    # file+stderr setup while the code default is no destinations.
    assert loaded.identity == defaults.identity
    assert loaded.conversation == defaults.conversation
    assert loaded.cognition == defaults.cognition
    assert loaded.funi == defaults.funi
    assert loaded.brunnr.backend == defaults.brunnr.backend
    # File-loaded paths are ~-expanded by the coercion layer (its
    # documented design); schema defaults stay unexpanded until use.
    assert loaded.brunnr.sqlite_vec is not None
    assert defaults.brunnr.sqlite_vec is not None
    assert loaded.brunnr.sqlite_vec.path == defaults.brunnr.sqlite_vec.path.expanduser()
    assert loaded.brunnr.sqlite_vec.wal_mode == defaults.brunnr.sqlite_vec.wal_mode
    assert loaded.tools.enabled is False
    assert loaded.mcp == defaults.mcp
    assert [d.kind.value for d in loaded.logging.destinations] == ["file", "stderr"]


def test_env_example_lists_exactly_the_live_vars() -> None:
    text = ENV_EXAMPLE.read_text(encoding="utf-8")
    named = set(re.findall(r"^\s*#\s*([A-Z][A-Z0-9_]*)\s*=", text, re.M))
    assert named == LIVE_ENV_VARS
    # The fossil's directions are gone: no Runa variables, no ~/.runa home.
    assert "RUNA_" not in text
    assert "~/.runa" not in text
    assert "does NOT load a .env file" in text


def test_no_file_defaults_are_sane() -> None:
    cfg = load_ember_config(None, skip_env=True)
    assert cfg == EmberConfig()
    # Nothing reaches out or starts itself on a fresh machine.
    assert cfg.tools.enabled is False
    assert cfg.mcp.enabled is False
    assert cfg.mcp.expose_self is False
    assert cfg.cognition.enabled is False
    assert cfg.tools.allow_private_addresses is False
    # The friendly defaults.
    assert cfg.funi.streaming is True
    assert cfg.funi.ollama.base_url == "http://localhost:11434"
    assert cfg.brunnr.backend.value == "sqlite_vec"
    assert cfg.conversation.resolved_token_budget == 2048  # pi profile
    assert cfg.conversation.resolved_max_episodes == 8


def test_unknown_and_fossil_keys_are_refused_by_name(tmp_path: Path) -> None:
    bad = tmp_path / "ember.toml"
    bad.write_text('openai_api_key = "sk-nope"\n', encoding="utf-8")
    with pytest.raises(ConfigError, match="openai_api_key"):
        load_ember_config(file_override=bad, skip_env=True)


def test_excerpt_files_say_they_are_not_config_files() -> None:
    for name in ("storage.example.yaml", "sources.example.yaml"):
        text = (REPO_ROOT / "config" / name).read_text(encoding="utf-8")
        assert "NOT a separate config file" in text or "NOT a config file" in text, name
