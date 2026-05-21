"""Recursive type coercion from parsed config dicts to dataclass instances.

Per ADR 0008 §2.6: the dataclass type tree IS the schema. This module
walks the tree, coerces each leaf value (StrEnum, Path, primitives),
recurses into nested dataclasses, and produces operator-readable
:class:`ConfigError` messages with full path-in-tree on any mismatch.

The Vow of Smallness keeps this stdlib-only. Operators who want richer
error messages opt in to ``ember-agent[validation]`` (pydantic) — a
parallel adapter lands in a follow-up phase when needed.
"""

from __future__ import annotations

import dataclasses
import difflib
import types
import typing
from collections.abc import Mapping
from enum import Enum
from pathlib import Path
from typing import Any, Union, get_args, get_origin

from ember.schemas.errors import ConfigError

_PRIMITIVES: tuple[type, ...] = (bool, int, float, str)


def coerce_to_dataclass(cls: type, data: Any, *, path: str = "") -> Any:
    """Coerce ``data`` (typically a dict from YAML/TOML) into ``cls``.

    - ``data is None`` → ``cls()`` (use defaults).
    - ``data`` is not a mapping → :class:`ConfigError`.
    - Unknown keys → :class:`ConfigError` with did-you-mean suggestion.
    - Type mismatches → :class:`ConfigError` with path, value, expected.
    - Missing required fields → :class:`ConfigError` naming the field.
    """
    if data is None:
        return _construct(cls, {}, path)
    if not isinstance(data, Mapping):
        raise ConfigError(
            _msg(path, f"expected mapping for {cls.__name__}, got {type(data).__name__}")
        )

    hints = typing.get_type_hints(cls)
    fields_by_name = {f.name: f for f in dataclasses.fields(cls)}
    known_field_names = list(fields_by_name)

    init_args: dict[str, Any] = {}
    for raw_key, raw_value in data.items():
        if not isinstance(raw_key, str):
            raise ConfigError(
                _msg(path, f"keys must be strings; got {type(raw_key).__name__}")
            )
        if raw_key not in fields_by_name:
            suggestion = _suggest(raw_key, known_field_names)
            hint = f" Did you mean `{suggestion}`?" if suggestion else ""
            raise ConfigError(
                _msg(
                    _child_path(path, raw_key),
                    f"unknown field for {cls.__name__}.{hint}",
                )
            )
        field_type = hints[raw_key]
        init_args[raw_key] = _coerce_value(
            field_type, raw_value, _child_path(path, raw_key)
        )

    return _construct(cls, init_args, path)


# --------------------------------------------------------------------- #
# Internals                                                              #
# --------------------------------------------------------------------- #


def _construct(cls: type, init_args: dict[str, Any], path: str) -> Any:
    try:
        return cls(**init_args)
    except TypeError as exc:
        # Most common cause: missing required field with no default.
        raise ConfigError(_msg(path, f"could not construct {cls.__name__}: {exc}")) from exc


def _coerce_value(  # noqa: PLR0911,PLR0912 — one return + one branch per supported type form; flattening hurts more than helps
    target_type: Any, value: Any, path: str
) -> Any:
    """Walk the annotated type and coerce ``value`` into it."""
    origin = get_origin(target_type)

    # Union / Optional — try each member; for X | None, allow None.
    if origin is Union or origin is types.UnionType:
        args = [a for a in get_args(target_type) if a is not type(None)]
        if value is None:
            return None
        if len(args) == 1:
            return _coerce_value(args[0], value, path)
        # Multi-arg union (rare in EmberConfig). Try each, accept first
        # that doesn't raise.
        for member in args:
            try:
                return _coerce_value(member, value, path)
            except ConfigError:
                continue
        raise ConfigError(_msg(path, f"value {value!r} did not match any of {args}"))

    # Tuple — coerce list -> tuple[X, ...] or tuple[X, Y, Z]
    if origin is tuple:
        args = get_args(target_type)
        if not isinstance(value, list):
            raise ConfigError(
                _msg(path, f"expected list, got {type(value).__name__}")
            )
        if len(args) == 2 and args[1] is Ellipsis:
            item_type = args[0]
            return tuple(
                _coerce_value(item_type, item, f"{path}[{i}]")
                for i, item in enumerate(value)
            )
        if len(args) != len(value):
            raise ConfigError(
                _msg(path, f"expected tuple of {len(args)} items, got {len(value)}")
            )
        return tuple(
            _coerce_value(t, v, f"{path}[{i}]")
            for i, (t, v) in enumerate(zip(args, value, strict=True))
        )

    # List
    if origin is list:
        args = get_args(target_type)
        item_type = args[0] if args else Any
        if not isinstance(value, list):
            raise ConfigError(
                _msg(path, f"expected list, got {type(value).__name__}")
            )
        return [
            _coerce_value(item_type, item, f"{path}[{i}]")
            for i, item in enumerate(value)
        ]

    # Mapping[str, X] — preserve as dict
    if origin in (dict, Mapping):
        if not isinstance(value, Mapping):
            raise ConfigError(
                _msg(path, f"expected mapping, got {type(value).__name__}")
            )
        return dict(value)

    # StrEnum / Enum
    if isinstance(target_type, type) and issubclass(target_type, Enum):
        try:
            return target_type(value)
        except ValueError as exc:
            members = ", ".join(repr(m.value) for m in target_type)
            raise ConfigError(
                _msg(
                    path,
                    f"invalid {target_type.__name__} value {value!r}; "
                    f"valid: [{members}]",
                )
            ) from exc

    # Path
    if target_type is Path:
        if not isinstance(value, (str, Path)):
            raise ConfigError(
                _msg(path, f"expected path string, got {type(value).__name__}")
            )
        # Expand ``~`` automatically so operators can write
        # ``path: "~/.ember/well/store.db"`` in YAML and have it Just
        # Work. Without this, the literal string would be treated as
        # a directory called ``~`` in the current working directory —
        # a surprising operator footgun. Hardening pass added this.
        return Path(value).expanduser()

    # Nested dataclass
    if dataclasses.is_dataclass(target_type) and isinstance(target_type, type):
        return coerce_to_dataclass(target_type, value, path=path)

    # Primitives
    if target_type in _PRIMITIVES:
        if target_type is bool and not isinstance(value, bool):
            raise ConfigError(
                _msg(path, f"expected bool, got {type(value).__name__}")
            )
        if target_type is float and isinstance(value, int) and not isinstance(value, bool):
            return float(value)
        if not isinstance(value, target_type) or (
            target_type is int and isinstance(value, bool)
        ):
            raise ConfigError(
                _msg(
                    path,
                    f"expected {target_type.__name__}, got "
                    f"{type(value).__name__} ({value!r})",
                )
            )
        return value

    # Fall-through: opaque type, accept as-is. (Used for Mapping[str, object].)
    return value


def _child_path(parent: str, key: str) -> str:
    return f"{parent}.{key}" if parent else key


def _msg(path: str, body: str) -> str:
    if path:
        return f"{path}: {body}"
    return body


def _suggest(unknown: str, known: list[str]) -> str | None:
    matches = difflib.get_close_matches(unknown, known, n=1, cutoff=0.7)
    return matches[0] if matches else None


__all__ = ["coerce_to_dataclass"]
