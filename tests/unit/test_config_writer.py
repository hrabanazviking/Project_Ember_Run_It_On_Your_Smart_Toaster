"""Tests for ``ember.config.writer`` — Hjarta's minimal YAML emission."""

from __future__ import annotations

from pathlib import Path

import pytest

from ember.config import (
    ConfigError,
    ember_config_exists,
    ember_config_path,
    load_ember_config,
    write_ember_config,
)
from ember.schemas.config import IdentityConfig


def test_path_is_under_config_subdir(tmp_path: Path) -> None:
    p = ember_config_path(tmp_path)
    assert p.parent == tmp_path / "config"
    assert p.name == "ember.yaml"


def test_exists_is_false_before_write(tmp_path: Path) -> None:
    assert ember_config_exists(tmp_path) is False


def test_write_creates_file_and_round_trips_through_loader(tmp_path: Path) -> None:
    written = write_ember_config(tmp_path, IdentityConfig(name="Spark"))
    assert written.is_file()
    assert ember_config_exists(tmp_path)

    cfg = load_ember_config(tmp_path, skip_env=True)
    assert cfg.identity.name == "Spark"
    # role default preserved from IdentityConfig().
    assert "small" in cfg.identity.role


def test_writer_quotes_strings_with_yaml_ambiguous_values(tmp_path: Path) -> None:
    # YAML 1.1 reads bare `yes`, `no`, `on`, `off` as booleans. The
    # writer always double-quotes strings to neutralise this.
    written = write_ember_config(
        tmp_path,
        IdentityConfig(name="yes", role="off"),
    )
    body = written.read_text(encoding="utf-8")
    assert 'name: "yes"' in body
    assert 'role: "off"' in body

    cfg = load_ember_config(tmp_path, skip_env=True)
    assert cfg.identity.name == "yes"
    assert cfg.identity.role == "off"


def test_writer_escapes_quotes_in_strings(tmp_path: Path) -> None:
    written = write_ember_config(
        tmp_path,
        IdentityConfig(name='Spark "the wise"'),
    )
    cfg = load_ember_config(tmp_path, skip_env=True)
    assert cfg.identity.name == 'Spark "the wise"'

    body = written.read_text(encoding="utf-8")
    assert r'\"the wise\"' in body


def test_writer_is_atomic_no_tmp_files_left(tmp_path: Path) -> None:
    write_ember_config(tmp_path, IdentityConfig())
    config_dir = tmp_path / "config"
    leftover = [p for p in config_dir.iterdir() if p.name.endswith(".tmp")]
    assert leftover == []


def test_writer_header_comment_present(tmp_path: Path) -> None:
    written = write_ember_config(tmp_path, IdentityConfig())
    body = written.read_text(encoding="utf-8")
    # Header should mention Hjarta and point at the full schema.
    assert "Hjarta" in body
    assert "ember.example.yaml" in body or "EmberConfig" in body


def test_writer_extras_section_is_emitted_and_loads(tmp_path: Path) -> None:
    written = write_ember_config(
        tmp_path,
        IdentityConfig(name="Spark"),
        extras={"strengr": {"retry_attempts": 5}},
    )
    body = written.read_text(encoding="utf-8")
    assert "strengr:" in body
    assert "retry_attempts: 5" in body

    cfg = load_ember_config(tmp_path, skip_env=True)
    assert cfg.identity.name == "Spark"
    assert cfg.strengr.retry_attempts == 5


def test_writer_rejects_unserialisable_value(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="writer cannot emit"):
        write_ember_config(
            tmp_path,
            IdentityConfig(),
            extras={"weird": {"obj": object()}},
        )
