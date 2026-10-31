"""Determinism mode for tests and benchmarks (E-036).

One place decides what "run it again and get the same answer"
means for a Funi generation request:

- The mode lives in config (``funi.determinism``, see
  :class:`ember.schemas.config.DeterminismConfig`) and is OFF
  by default. Normal conversation is untouched: the operator's
  configured temperature is sent and no seed is sent.
- When the mode is ON, the *effective* options for every
  generation request carry the configured fixed ``seed`` and
  a temperature of 0.0 (greedy decoding). The operator's
  configured temperature is never mutated — adapters compute
  their effective options through :func:`effective_options`
  at open time, and switching the mode off restores the
  configured sampling exactly.
- A negative (or non-integer) seed is a configuration error,
  reported by :func:`determinism_error` so each adapter can
  refuse at open time with its typed CONFIG_INVALID shape —
  never a silent clamp, drop, or crash.

What the mode does NOT claim (stated in full in
``docs/architecture/E-036_DETERMINISM_MODE.md``): wall-clock
timestamps, generated ids (uuid call ids, journal filenames),
and a backend engine's own internal nondeterminism are
outside Ember's control. The mode makes Ember's *requests*
reproducible; whether a given model + engine build answers
byte-identically is that backend's contract, not this
module's promise. Ember's own non-generation paths are
already deterministic by construction — the core uses no
``random`` module anywhere, the chunker and the extractive
summariser are pure functions, ingest walks files in sorted
order, and retrieval ranking carries explicit id tie-breaks
(E-036) so equal scores always order the same way.
"""

from __future__ import annotations

from ember.schemas.config import FuniConfig

#: Temperature sent in determinism mode: greedy decoding.
DETERMINISTIC_TEMPERATURE = 0.0


def is_deterministic(config: FuniConfig) -> bool:
    """True when determinism mode is switched on in ``config``."""
    return bool(config.determinism.enabled)


def determinism_error(config: FuniConfig) -> str | None:
    """Why the determinism config is unusable, or None if it is fine.

    Only judged when the mode is enabled: a disabled mode sends
    no seed anywhere, so its seed value is inert data, not an
    error. A bool is not a seed (``True`` is an ``int`` in
    Python, but it is never a benchmark seed anyone meant).
    """
    if not config.determinism.enabled:
        return None
    seed = config.determinism.seed
    if isinstance(seed, bool) or not isinstance(seed, int):
        return f"determinism seed must be an integer, got {seed!r}"
    if seed < 0:
        return f"determinism seed must be non-negative, got {seed}"
    return None


def effective_options(
    base_options: dict[str, object], config: FuniConfig
) -> dict[str, object]:
    """The options a generation request must actually carry.

    Disabled mode: a copy of ``base_options``, unchanged — no
    ``seed`` key is added, so a normal request is byte-identical
    to its pre-E-036 shape.

    Enabled mode: a copy with ``temperature`` forced to
    :data:`DETERMINISTIC_TEMPERATURE` and ``seed`` set to the
    configured seed. Every other option (top_p, num_predict /
    max_tokens, timeout) rides exactly as configured.
    """
    options = dict(base_options)
    if not is_deterministic(config):
        return options
    options["temperature"] = DETERMINISTIC_TEMPERATURE
    options["seed"] = config.determinism.seed
    return options


__all__ = [
    "DETERMINISTIC_TEMPERATURE",
    "determinism_error",
    "effective_options",
    "is_deterministic",
]
