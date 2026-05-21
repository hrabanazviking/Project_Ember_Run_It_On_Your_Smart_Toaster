"""Environment-variable overlay + dict merge helpers.

Per ADR 0008 §2.3: overlay order is defaults → file → env (→ CLI).
This module owns the env layer plus a small `merge_dicts` utility for
the file-on-defaults composition done in :mod:`ember.config.loader`.

In Phase 8 the env-overlay logic mirrors what already lives in
``cli/main.py._apply_env_overrides`` (Phase-7 escape hatch). Phase 9
removes the duplicate in cli/main and routes everything through here.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import replace

from ember.schemas.config import EmberConfig

_OLLAMA_HOST_ENV = "OLLAMA_HOST"


def merge_dicts(base: Mapping, overlay: Mapping) -> dict:
    """Recursively merge ``overlay`` on top of ``base``.

    - Nested mappings merge key-wise.
    - Non-mapping values from ``overlay`` replace base values.
    - Keys present only in ``base`` are preserved.

    Used to layer file config on top of an empty defaults dict (the
    actual ``EmberConfig`` defaults come from
    :func:`ember.config.validate.coerce_to_dataclass` constructing each
    missing field from its dataclass default — this function is for
    flat-dict layering when both sides come from disk).
    """
    out: dict = dict(base)
    for key, value in overlay.items():
        if (
            isinstance(value, Mapping)
            and key in out
            and isinstance(out[key], Mapping)
        ):
            out[key] = merge_dicts(out[key], value)
        else:
            out[key] = value
    return out


def apply_env_overrides(
    config: EmberConfig,
    *,
    env: Mapping[str, str] | None = None,
) -> EmberConfig:
    """Apply environment-variable overrides on top of an EmberConfig.

    Recognised variables (Phase 8):

    - ``OLLAMA_HOST`` — redirects both ``funi.ollama.base_url`` and
      ``smidja.embedding.endpoint``. Accepts the same shapes Ollama's
      own CLI accepts (``host``, ``host:port``, full URL).

    ``env`` defaults to ``os.environ``; tests pass a mapping to avoid
    polluting the real environment.
    """
    env_map = os.environ if env is None else env

    host = (env_map.get(_OLLAMA_HOST_ENV) or "").strip()
    if not host:
        return config

    base_url = _normalise_ollama_host(host)
    if not base_url:
        return config

    new_funi = replace(
        config.funi,
        ollama=replace(config.funi.ollama, base_url=base_url),
    )
    new_smidja = replace(
        config.smidja,
        embedding=replace(
            config.smidja.embedding,
            endpoint=base_url.rstrip("/") + "/api/embed",
        ),
    )
    return replace(config, funi=new_funi, smidja=new_smidja)


def _normalise_ollama_host(value: str) -> str:
    """Turn an ``OLLAMA_HOST`` value into a base_url.

    Accepts ``HOST``, ``HOST:PORT``, ``http://HOST:PORT``,
    ``https://HOST:PORT``. Bare host/host:port is upgraded to ``http://``.
    """
    raw = value.strip()
    if not raw:
        return ""
    if raw.startswith(("http://", "https://")):
        return raw.rstrip("/")
    if ":" not in raw:
        raw = f"{raw}:11434"
    return f"http://{raw}"


__all__ = ["apply_env_overrides", "merge_dicts"]
