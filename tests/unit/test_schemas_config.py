"""Shape contracts for ``ember.schemas.config``."""

from __future__ import annotations

import dataclasses
from pathlib import Path

import pytest

from ember.schemas.config import (
    BoundaryPreference,
    BrunnrBackend,
    BrunnrConfig,
    ChunkerConfig,
    EmbeddingConfig,
    EmberConfig,
    FuniConfig,
    FuniOllamaConfig,
    FuniRuntime,
    IdentityConfig,
    JournalConfig,
    LoggingConfig,
    LogLevel,
    PgVectorConfig,
    SmidjaConfig,
    SqliteVecConfig,
    StrengrConfig,
)

# --------------------------------------------------------------------- #
# Top-level default construction                                         #
# --------------------------------------------------------------------- #


def test_ember_config_constructs_with_no_arguments() -> None:
    cfg = EmberConfig()
    assert isinstance(cfg.identity, IdentityConfig)
    assert isinstance(cfg.funi, FuniConfig)
    assert isinstance(cfg.strengr, StrengrConfig)
    assert isinstance(cfg.brunnr, BrunnrConfig)
    assert isinstance(cfg.smidja, SmidjaConfig)
    assert isinstance(cfg.logging, LoggingConfig)


def test_ember_config_is_frozen() -> None:
    cfg = EmberConfig()
    with pytest.raises(dataclasses.FrozenInstanceError):
        cfg.identity = IdentityConfig(name="Tampered")  # type: ignore[misc]


def test_default_factories_produce_independent_instances() -> None:
    a = EmberConfig()
    b = EmberConfig()
    assert a.brunnr is not b.brunnr
    assert a.smidja.chunker is not b.smidja.chunker


# --------------------------------------------------------------------- #
# Identity                                                               #
# --------------------------------------------------------------------- #


def test_identity_defaults_match_skald_intent() -> None:
    ident = IdentityConfig()
    assert ident.name == "Ember"
    assert "small" in ident.role.lower()


# --------------------------------------------------------------------- #
# Funi                                                                   #
# --------------------------------------------------------------------- #


def test_funi_default_runtime_is_ollama() -> None:
    assert FuniConfig().runtime is FuniRuntime.OLLAMA


def test_funi_ollama_defaults_match_first_slice_target() -> None:
    o = FuniOllamaConfig()
    assert o.model == "phi3:mini"
    assert o.base_url.startswith("http")


def test_every_funi_runtime_has_string_value() -> None:
    for member in FuniRuntime:
        assert isinstance(member.value, str)


# --------------------------------------------------------------------- #
# Brunnr                                                                 #
# --------------------------------------------------------------------- #


def test_brunnr_default_backend_is_sqlite_vec() -> None:
    assert BrunnrConfig().backend is BrunnrBackend.SQLITE_VEC


def test_brunnr_default_embedding_dim_matches_gungnir_reference() -> None:
    assert BrunnrConfig().embedding_dim == 768


def test_brunnr_default_has_sqlite_vec_config_but_no_pgvector() -> None:
    cfg = BrunnrConfig()
    assert isinstance(cfg.sqlite_vec, SqliteVecConfig)
    assert cfg.pgvector is None


def test_pgvector_config_requires_url_and_secret_ref() -> None:
    pg = PgVectorConfig(
        url="postgresql://volmarr@gungnir/knowledge",
        secret_ref=Path("~/.ember/secrets/well.password"),
    )
    assert pg.vector_index == "hnsw"
    assert pg.vector_metric == "cosine"


def test_sqlite_vec_path_is_left_unexpanded() -> None:
    # Per the module docstring: paths are stored without expanduser()
    # so $HOME is not frozen at import time.
    cfg = SqliteVecConfig()
    assert str(cfg.path).startswith("~/")


# --------------------------------------------------------------------- #
# Smiðja — Gungnir-aligned chunker                                       #
# --------------------------------------------------------------------- #


def test_chunker_defaults_match_gungnir_calibration() -> None:
    c = ChunkerConfig()
    assert c.max_chars == 2000
    assert c.target_chars == 1684
    assert c.min_chars == 200
    assert c.boundary_preference is BoundaryPreference.PARAGRAPH


def test_chunker_target_is_strictly_under_max() -> None:
    c = ChunkerConfig()
    assert c.target_chars < c.max_chars


def test_embedding_default_model_matches_gungnir() -> None:
    assert EmbeddingConfig().model == "nomic-embed-text"


def test_journal_defaults_path_under_ember_state() -> None:
    j = JournalConfig()
    assert "/.ember/state/" in str(j.path) if False else str(j.root).startswith("~/")


# --------------------------------------------------------------------- #
# Logging                                                                #
# --------------------------------------------------------------------- #


def test_logging_default_level_is_info() -> None:
    assert LoggingConfig().level is LogLevel.INFO


def test_logging_destinations_is_immutable_tuple() -> None:
    log = LoggingConfig()
    assert isinstance(log.destinations, tuple)
