"""Shape and behaviour tests for ``ember.config.validate``."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

import pytest

from ember.config.validate import coerce_to_dataclass
from ember.schemas.config import (
    BrunnrBackend,
    BrunnrConfig,
    EmberConfig,
    FuniOllamaConfig,
    PgVectorConfig,
    SqliteVecConfig,
)
from ember.schemas.errors import ConfigError

# --------------------------------------------------------------------- #
# Defaults from empty input                                             #
# --------------------------------------------------------------------- #


def test_none_returns_all_defaults() -> None:
    cfg = coerce_to_dataclass(EmberConfig, None)
    assert isinstance(cfg, EmberConfig)
    assert cfg.identity.name == "Ember"


def test_empty_dict_returns_all_defaults() -> None:
    cfg = coerce_to_dataclass(EmberConfig, {})
    assert cfg.identity.name == "Ember"
    assert cfg.brunnr.backend is BrunnrBackend.SQLITE_VEC


# --------------------------------------------------------------------- #
# Partial coercion                                                      #
# --------------------------------------------------------------------- #


def test_partial_override_preserves_other_defaults() -> None:
    cfg = coerce_to_dataclass(
        EmberConfig,
        {"identity": {"name": "Spark"}},
    )
    assert cfg.identity.name == "Spark"
    # role default preserved
    assert "small" in cfg.identity.role
    # other top-level defaults preserved
    assert cfg.funi.ollama.model == "phi3:mini"


def test_nested_partial_override_works() -> None:
    cfg = coerce_to_dataclass(
        EmberConfig,
        {"funi": {"ollama": {"model": "qwen2.5:7b-instruct", "temperature": 0.3}}},
    )
    assert cfg.funi.ollama.model == "qwen2.5:7b-instruct"
    assert cfg.funi.ollama.temperature == pytest.approx(0.3)
    # other ollama defaults preserved
    assert cfg.funi.ollama.top_p == pytest.approx(0.9)


# --------------------------------------------------------------------- #
# Type coercion                                                          #
# --------------------------------------------------------------------- #


def test_string_coerces_to_str_enum() -> None:
    cfg = coerce_to_dataclass(BrunnrConfig, {"backend": "qdrant"})
    assert cfg.backend is BrunnrBackend.QDRANT


def test_string_coerces_to_path() -> None:
    cfg = coerce_to_dataclass(
        SqliteVecConfig,
        {"path": "/tmp/test.db"},
    )
    assert cfg.path == Path("/tmp/test.db")
    # Loader does NOT expanduser — consumer expands.
    cfg2 = coerce_to_dataclass(SqliteVecConfig, {"path": "~/.ember/x.db"})
    assert str(cfg2.path).startswith("~")


def test_int_coerces_to_float_field() -> None:
    cfg = coerce_to_dataclass(FuniOllamaConfig, {"temperature": 0})
    assert cfg.temperature == 0.0
    assert isinstance(cfg.temperature, float)


def test_null_satisfies_optional_field() -> None:
    cfg = coerce_to_dataclass(
        BrunnrConfig,
        {"pgvector": None},
    )
    assert cfg.pgvector is None


def test_dict_satisfies_optional_dataclass_field() -> None:
    cfg = coerce_to_dataclass(
        BrunnrConfig,
        {
            "pgvector": {
                "url": "postgresql://x@y/z",
                "secret_ref": "/tmp/x",
            }
        },
    )
    assert cfg.pgvector is not None
    assert cfg.pgvector.url == "postgresql://x@y/z"
    assert cfg.pgvector.secret_ref == Path("/tmp/x")


# --------------------------------------------------------------------- #
# Error paths                                                            #
# --------------------------------------------------------------------- #


def test_unknown_top_level_key_errors_with_path() -> None:
    with pytest.raises(ConfigError, match=r"bogus.*unknown field") as exc:
        coerce_to_dataclass(EmberConfig, {"bogus": "x"})
    assert "EmberConfig" in str(exc.value)


def test_unknown_nested_key_includes_full_path() -> None:
    with pytest.raises(ConfigError, match=r"funi\.ollama\.mdoel") as exc:
        coerce_to_dataclass(
            EmberConfig,
            {"funi": {"ollama": {"mdoel": "x"}}},
        )
    # Did-you-mean suggestion fires.
    assert "Did you mean" in str(exc.value)
    assert "`model`" in str(exc.value)


def test_invalid_enum_value_lists_valid_options() -> None:
    with pytest.raises(ConfigError, match="invalid BrunnrBackend") as exc:
        coerce_to_dataclass(BrunnrConfig, {"backend": "weaviate"})
    body = str(exc.value)
    assert "sqlite_vec" in body
    assert "pgvector" in body


def test_type_mismatch_names_path_and_value() -> None:
    with pytest.raises(ConfigError, match=r"funi\.ollama\.temperature") as exc:
        coerce_to_dataclass(
            EmberConfig,
            {"funi": {"ollama": {"temperature": "hot"}}},
        )
    assert "expected float" in str(exc.value)
    assert "'hot'" in str(exc.value)


def test_missing_required_field_in_nested_dataclass_errors() -> None:
    # PgVectorConfig requires url + secret_ref (no defaults).
    with pytest.raises(ConfigError, match="PgVectorConfig"):
        coerce_to_dataclass(PgVectorConfig, {})


def test_non_mapping_at_top_level_errors() -> None:
    with pytest.raises(ConfigError, match="expected mapping"):
        coerce_to_dataclass(EmberConfig, "not a dict")  # type: ignore[arg-type]


def test_non_string_key_errors() -> None:
    with pytest.raises(ConfigError, match="keys must be strings"):
        coerce_to_dataclass(EmberConfig, {42: "x"})  # type: ignore[dict-item]


# --------------------------------------------------------------------- #
# Tuple of dataclass items                                              #
# --------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class _Item:
    label: str


@dataclass(frozen=True, slots=True)
class _Holder:
    items: tuple[_Item, ...] = ()


def test_list_coerces_to_tuple_of_dataclasses() -> None:
    holder = coerce_to_dataclass(
        _Holder, {"items": [{"label": "a"}, {"label": "b"}]}
    )
    assert holder.items == (_Item(label="a"), _Item(label="b"))


# --------------------------------------------------------------------- #
# Strict bool / int separation                                          #
# --------------------------------------------------------------------- #


class _BoolHolder:
    pass


@dataclass(frozen=True, slots=True)
class _BoolDC:
    flag: bool = True


def test_int_does_not_silently_satisfy_bool_field() -> None:
    with pytest.raises(ConfigError, match="expected bool"):
        coerce_to_dataclass(_BoolDC, {"flag": 1})


@dataclass(frozen=True, slots=True)
class _IntDC:
    count: int = 0


def test_bool_does_not_silently_satisfy_int_field() -> None:
    with pytest.raises(ConfigError, match="expected int"):
        coerce_to_dataclass(_IntDC, {"count": True})


# --------------------------------------------------------------------- #
# Standalone enum kind in nested
# --------------------------------------------------------------------- #


class _Color(StrEnum):
    RED = "red"
    BLUE = "blue"


@dataclass(frozen=True, slots=True)
class _Painted:
    color: _Color = _Color.RED


def test_enum_round_trips_through_string() -> None:
    assert coerce_to_dataclass(_Painted, {"color": "blue"}).color is _Color.BLUE
