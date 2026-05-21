"""Behaviour tests for the OLLAMA_HOST env-var override in cli/main."""

from __future__ import annotations

import pytest

from ember.cli.main import _apply_env_overrides, _normalise_ollama_host
from ember.schemas.config import EmberConfig

# --------------------------------------------------------------------- #
# _normalise_ollama_host                                                #
# --------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "input_value,expected",
    [
        ("localhost", "http://localhost:11434"),
        ("localhost:11434", "http://localhost:11434"),
        ("100.67.240.22", "http://100.67.240.22:11434"),
        ("100.67.240.22:11434", "http://100.67.240.22:11434"),
        ("http://localhost:11434", "http://localhost:11434"),
        ("http://localhost:11434/", "http://localhost:11434"),
        ("https://ollama.example.com:443", "https://ollama.example.com:443"),
    ],
)
def test_normalise_accepts_ollama_cli_shapes(input_value: str, expected: str) -> None:
    assert _normalise_ollama_host(input_value) == expected


def test_normalise_empty_returns_empty() -> None:
    assert _normalise_ollama_host("") == ""
    assert _normalise_ollama_host("   ") == ""


# --------------------------------------------------------------------- #
# _apply_env_overrides                                                  #
# --------------------------------------------------------------------- #


def test_no_env_set_returns_config_unchanged(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OLLAMA_HOST", raising=False)
    cfg = EmberConfig()
    result = _apply_env_overrides(cfg)
    assert result == cfg


def test_empty_env_returns_config_unchanged(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OLLAMA_HOST", "")
    cfg = EmberConfig()
    result = _apply_env_overrides(cfg)
    assert result == cfg


def test_ollama_host_redirects_both_funi_and_smidja(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OLLAMA_HOST", "100.67.240.22")
    result = _apply_env_overrides(EmberConfig())
    assert result.funi.ollama.base_url == "http://100.67.240.22:11434"
    assert result.smidja.embedding.endpoint == "http://100.67.240.22:11434/api/embed"


def test_ollama_host_with_explicit_scheme_is_preserved(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OLLAMA_HOST", "https://ollama.example.com:8080")
    result = _apply_env_overrides(EmberConfig())
    assert result.funi.ollama.base_url == "https://ollama.example.com:8080"
    assert (
        result.smidja.embedding.endpoint
        == "https://ollama.example.com:8080/api/embed"
    )


def test_other_config_fields_are_preserved(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OLLAMA_HOST", "localhost")
    result = _apply_env_overrides(EmberConfig())
    # Model name, sqlite path, identity name, etc. all untouched.
    assert result.funi.ollama.model == "phi3:mini"
    assert result.brunnr.embedding_dim == 768
    assert result.identity.name == "Ember"


def test_override_is_purely_functional(monkeypatch: pytest.MonkeyPatch) -> None:
    """The original EmberConfig must not be mutated."""
    monkeypatch.setenv("OLLAMA_HOST", "localhost")
    original = EmberConfig()
    original_url = original.funi.ollama.base_url
    overridden = _apply_env_overrides(original)
    assert original.funi.ollama.base_url == original_url
    assert overridden is not original
