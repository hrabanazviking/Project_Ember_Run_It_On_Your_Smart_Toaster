"""Tests for ``ember.config.overlay`` — merge_dicts + apply_env_overrides."""

from __future__ import annotations

from ember.config.overlay import (
    _normalise_ollama_host,
    apply_env_overrides,
    merge_dicts,
)
from ember.schemas.config import EmberConfig

# --------------------------------------------------------------------- #
# merge_dicts                                                           #
# --------------------------------------------------------------------- #


def test_merge_empty_overlay_returns_base_copy() -> None:
    base = {"a": 1, "b": {"c": 2}}
    out = merge_dicts(base, {})
    assert out == base
    assert out is not base  # copy


def test_merge_flat_keys_overlay_wins() -> None:
    out = merge_dicts({"a": 1, "b": 2}, {"b": 99, "c": 3})
    assert out == {"a": 1, "b": 99, "c": 3}


def test_merge_nested_dicts_recurse() -> None:
    out = merge_dicts(
        {"funi": {"ollama": {"model": "phi3:mini", "temperature": 0.7}}},
        {"funi": {"ollama": {"temperature": 0.3}}},
    )
    assert out == {"funi": {"ollama": {"model": "phi3:mini", "temperature": 0.3}}}


def test_merge_replaces_non_mapping_with_mapping() -> None:
    # If base has a scalar and overlay has a mapping at the same key,
    # overlay replaces wholesale.
    out = merge_dicts({"x": 5}, {"x": {"nested": True}})
    assert out == {"x": {"nested": True}}


# --------------------------------------------------------------------- #
# _normalise_ollama_host                                                #
# --------------------------------------------------------------------- #


def test_normalise_handles_ollama_shapes() -> None:
    assert _normalise_ollama_host("localhost") == "http://localhost:11434"
    assert _normalise_ollama_host("100.67.240.22") == "http://100.67.240.22:11434"
    assert _normalise_ollama_host("100.67.240.22:11434") == "http://100.67.240.22:11434"
    assert _normalise_ollama_host("http://x.com:8080") == "http://x.com:8080"
    assert _normalise_ollama_host("https://x.com/") == "https://x.com"
    assert _normalise_ollama_host("") == ""
    assert _normalise_ollama_host("   ") == ""


# --------------------------------------------------------------------- #
# apply_env_overrides                                                   #
# --------------------------------------------------------------------- #


def test_no_env_returns_config_unchanged() -> None:
    cfg = EmberConfig()
    assert apply_env_overrides(cfg, env={}) == cfg


def test_ollama_host_redirects_funi_and_smidja() -> None:
    cfg = EmberConfig()
    result = apply_env_overrides(cfg, env={"OLLAMA_HOST": "100.67.240.22"})
    assert result.funi.ollama.base_url == "http://100.67.240.22:11434"
    assert result.smidja.embedding.endpoint == "http://100.67.240.22:11434/api/embed"


def test_empty_env_value_is_no_op() -> None:
    cfg = EmberConfig()
    assert apply_env_overrides(cfg, env={"OLLAMA_HOST": ""}) == cfg
    assert apply_env_overrides(cfg, env={"OLLAMA_HOST": "   "}) == cfg


def test_override_is_purely_functional() -> None:
    cfg = EmberConfig()
    original_url = cfg.funi.ollama.base_url
    result = apply_env_overrides(cfg, env={"OLLAMA_HOST": "localhost"})
    # Original untouched.
    assert cfg.funi.ollama.base_url == original_url
    assert result is not cfg


def test_unrelated_fields_preserved_through_override() -> None:
    cfg = EmberConfig()
    result = apply_env_overrides(cfg, env={"OLLAMA_HOST": "localhost"})
    assert result.identity.name == "Ember"
    assert result.brunnr.embedding_dim == 768
    assert result.funi.ollama.model == "phi3:mini"
