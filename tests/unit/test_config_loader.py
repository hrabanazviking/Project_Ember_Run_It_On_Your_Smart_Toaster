"""End-to-end tests for ``ember.config.load_ember_config``.

Covers the file probe, YAML/TOML format symmetry, partial-override
merging into defaults, env-overlay composition, and the YAML-without-
PyYAML error path.
"""

from __future__ import annotations

import warnings
from pathlib import Path

import pytest

from ember.config import load_ember_config
from ember.schemas.config import BrunnrBackend
from ember.schemas.errors import ConfigError

_SAMPLE_YAML = """\
identity:
  name: Spark
  role: tiny test companion
funi:
  ollama:
    model: qwen2.5:7b-instruct
    temperature: 0.3
brunnr:
  embedding_dim: 384
"""

_SAMPLE_TOML = """\
[identity]
name = "Spark"
role = "tiny test companion"

[funi.ollama]
model = "qwen2.5:7b-instruct"
temperature = 0.3

[brunnr]
embedding_dim = 384
"""


def _write_config(config_root: Path, filename: str, content: str) -> None:
    cfg_dir = config_root / "config"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    (cfg_dir / filename).write_text(content, encoding="utf-8")


# --------------------------------------------------------------------- #
# File probe                                                            #
# --------------------------------------------------------------------- #


def test_no_config_root_returns_defaults() -> None:
    cfg = load_ember_config(skip_env=True)
    assert cfg.identity.name == "Ember"
    assert cfg.brunnr.backend is BrunnrBackend.SQLITE_VEC


def test_missing_config_dir_returns_defaults(tmp_path: Path) -> None:
    cfg = load_ember_config(tmp_path, skip_env=True)
    assert cfg.identity.name == "Ember"


def test_yaml_file_overrides_defaults(tmp_path: Path) -> None:
    _write_config(tmp_path, "ember.yaml", _SAMPLE_YAML)
    cfg = load_ember_config(tmp_path, skip_env=True)
    assert cfg.identity.name == "Spark"
    assert cfg.funi.ollama.model == "qwen2.5:7b-instruct"
    assert cfg.funi.ollama.temperature == pytest.approx(0.3)
    assert cfg.brunnr.embedding_dim == 384
    # Other defaults preserved.
    assert cfg.funi.ollama.top_p == pytest.approx(0.9)


def test_toml_file_overrides_defaults(tmp_path: Path) -> None:
    _write_config(tmp_path, "ember.toml", _SAMPLE_TOML)
    cfg = load_ember_config(tmp_path, skip_env=True)
    assert cfg.identity.name == "Spark"
    assert cfg.funi.ollama.model == "qwen2.5:7b-instruct"
    assert cfg.brunnr.embedding_dim == 384


def test_yaml_and_toml_equivalent_load_to_same_config(tmp_path: Path) -> None:
    yaml_root = tmp_path / "yaml"
    toml_root = tmp_path / "toml"
    _write_config(yaml_root, "ember.yaml", _SAMPLE_YAML)
    _write_config(toml_root, "ember.toml", _SAMPLE_TOML)
    assert load_ember_config(yaml_root, skip_env=True) == load_ember_config(
        toml_root, skip_env=True
    )


def test_both_files_present_yaml_wins_with_warning(tmp_path: Path) -> None:
    _write_config(tmp_path, "ember.yaml", _SAMPLE_YAML)
    _write_config(
        tmp_path,
        "ember.toml",
        "[identity]\nname = 'NotChosen'\n",
    )
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        cfg = load_ember_config(tmp_path, skip_env=True)
    assert cfg.identity.name == "Spark"  # YAML's value
    assert any("YAML wins" in str(w.message) for w in caught)


# --------------------------------------------------------------------- #
# Empty file                                                            #
# --------------------------------------------------------------------- #


def test_empty_yaml_file_is_legal_returns_defaults(tmp_path: Path) -> None:
    _write_config(tmp_path, "ember.yaml", "")
    cfg = load_ember_config(tmp_path, skip_env=True)
    assert cfg.identity.name == "Ember"


def test_empty_toml_file_is_legal_returns_defaults(tmp_path: Path) -> None:
    _write_config(tmp_path, "ember.toml", "")
    cfg = load_ember_config(tmp_path, skip_env=True)
    assert cfg.identity.name == "Ember"


# --------------------------------------------------------------------- #
# file_override (test seam)                                             #
# --------------------------------------------------------------------- #


def test_file_override_bypasses_config_root_probe(tmp_path: Path) -> None:
    override = tmp_path / "weird-name.yaml"
    override.write_text(_SAMPLE_YAML, encoding="utf-8")
    cfg = load_ember_config(file_override=override, skip_env=True)
    assert cfg.identity.name == "Spark"


def test_file_override_with_unknown_extension_errors(tmp_path: Path) -> None:
    override = tmp_path / "config.ini"
    override.write_text("[identity]\nname = x\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="unrecognised config file extension"):
        load_ember_config(file_override=override, skip_env=True)


# --------------------------------------------------------------------- #
# Parse errors                                                          #
# --------------------------------------------------------------------- #


def test_malformed_yaml_raises_config_error(tmp_path: Path) -> None:
    _write_config(tmp_path, "ember.yaml", "this: is: not: valid")
    with pytest.raises(ConfigError, match="invalid YAML"):
        load_ember_config(tmp_path, skip_env=True)


def test_malformed_toml_raises_config_error(tmp_path: Path) -> None:
    _write_config(tmp_path, "ember.toml", "this is not toml = = =")
    with pytest.raises(ConfigError, match="invalid TOML"):
        load_ember_config(tmp_path, skip_env=True)


def test_unknown_key_at_load_time_includes_file_context(tmp_path: Path) -> None:
    _write_config(tmp_path, "ember.yaml", "funi:\n  ollama:\n    mdoel: phi3:mini\n")
    with pytest.raises(ConfigError, match=r"funi\.ollama\.mdoel"):
        load_ember_config(tmp_path, skip_env=True)


# --------------------------------------------------------------------- #
# Env overlay integration                                               #
# --------------------------------------------------------------------- #


def test_env_overlay_runs_by_default(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("OLLAMA_HOST", "100.67.240.22")
    _write_config(tmp_path, "ember.yaml", _SAMPLE_YAML)
    cfg = load_ember_config(tmp_path)
    # File set model + temperature; env override changed base_url.
    assert cfg.funi.ollama.model == "qwen2.5:7b-instruct"
    assert cfg.funi.ollama.base_url == "http://100.67.240.22:11434"
    assert cfg.smidja.embedding.endpoint == "http://100.67.240.22:11434/api/embed"


def test_skip_env_disables_overlay(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("OLLAMA_HOST", "100.67.240.22")
    _write_config(tmp_path, "ember.yaml", _SAMPLE_YAML)
    cfg = load_ember_config(tmp_path, skip_env=True)
    # File model still applied, but env didn't touch base_url.
    assert cfg.funi.ollama.base_url == "http://localhost:11434"
