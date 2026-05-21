"""Logging setup driven by ``EmberConfig.logging`` — ADR-0008 follow-up.

Until Batch J the ``LoggingConfig`` dataclass existed in
``schemas/config.py`` but no code read it: operators could set
``logging.level: DEBUG`` in ``ember.yaml`` and nothing happened. This
module is the missing wire-up.

``configure_from(config.logging)`` configures Python's root logger
once per process and is idempotent (re-calls reset the handler set).
Call it early in :func:`ember.cli.main.main` — before any module that
emits log lines.

Vows honoured:

- **Smallness**: stdlib only (no structlog, no loguru).
- **Public-Friendliness**: when no destinations are configured, default
  to a single stderr handler so the operator still sees warnings —
  silence is worse than verbosity.
"""

from __future__ import annotations

import json
import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Any

from ember.schemas.config import (
    LogDestinationKind,
    LogFormat,
    LoggingConfig,
    LoggingDestination,
    LogLevel,
)

_PLAIN_FORMAT = "%(asctime)s %(levelname)-7s %(name)s | %(message)s"


def configure_from(cfg: LoggingConfig) -> None:
    """Configure Python's root logger from a :class:`LoggingConfig`.

    Idempotent: clears existing handlers on every call so a re-load
    after ``ember setup`` doesn't double-emit each line.

    Behaviour:

    - ``level``: set on the root logger
    - ``destinations``: one handler per declared destination. If the
      list is empty, one stderr handler is added so the operator still
      sees warnings.
    - ``format``: PLAIN → human-friendly single line; STRUCTURED →
      one JSON object per line (machine-parseable, ships every
      ``LogRecord`` field worth keeping)
    """
    root = logging.getLogger()
    root.setLevel(_LEVEL_MAP[cfg.level])

    # Wipe handlers we (or someone before us) attached. Important for
    # the test suite — running configure_from twice should not stack
    # handlers and emit each record twice.
    for handler in list(root.handlers):
        root.removeHandler(handler)
        handler.close()

    formatter = _build_formatter(cfg.format)
    destinations = cfg.destinations or (
        LoggingDestination(kind=LogDestinationKind.STDERR),
    )
    for dest in destinations:
        handler = _build_handler(dest)
        if handler is None:
            continue
        handler.setFormatter(formatter)
        root.addHandler(handler)


# --------------------------------------------------------------------- #
# Internals                                                              #
# --------------------------------------------------------------------- #


_LEVEL_MAP: dict[LogLevel, int] = {
    LogLevel.DEBUG: logging.DEBUG,
    LogLevel.INFO: logging.INFO,
    LogLevel.WARNING: logging.WARNING,
    LogLevel.ERROR: logging.ERROR,
}


def _build_formatter(fmt: LogFormat) -> logging.Formatter:
    if fmt is LogFormat.STRUCTURED:
        return _JSONFormatter()
    return logging.Formatter(_PLAIN_FORMAT)


def _build_handler(dest: LoggingDestination) -> logging.Handler | None:
    """Construct a Handler from one destination declaration.

    Returns None (with a stderr warning) when the destination is
    malformed — we never raise during logging setup, since logging is
    the operator's *diagnostic* surface.
    """
    if dest.kind is LogDestinationKind.STDERR:
        return logging.StreamHandler(stream=sys.stderr)
    if dest.kind is LogDestinationKind.STDOUT:
        return logging.StreamHandler(stream=sys.stdout)
    if dest.kind is LogDestinationKind.FILE:
        if dest.path is None:
            print(
                "ember.logging: file destination missing `path`; skipping",
                file=sys.stderr,
            )
            return None
        path = Path(dest.path).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        # Use RotatingFileHandler when size + keep are configured;
        # otherwise plain FileHandler.
        if dest.rotate_at_mb is not None and dest.keep is not None:
            return logging.handlers.RotatingFileHandler(
                filename=str(path),
                maxBytes=int(dest.rotate_at_mb) * 1024 * 1024,
                backupCount=int(dest.keep),
                encoding="utf-8",
            )
        return logging.FileHandler(filename=str(path), encoding="utf-8")
    # Defensive — every enum value handled above. Schema validation
    # ensures we never reach here in practice.
    print(
        f"ember.logging: unknown destination kind {dest.kind!r}; skipping",
        file=sys.stderr,
    )
    return None


class _JSONFormatter(logging.Formatter):
    """One JSON object per line.

    Ships the fields that are useful for log aggregation: timestamp,
    level, logger name, message, plus any structured ``extra=...``
    fields the call site passed in. Skips noisy internal LogRecord
    attributes that would bloat each line.
    """

    _SKIP_RECORD_ATTRS: frozenset[str] = frozenset({
        "name", "msg", "args", "levelname", "levelno", "pathname",
        "filename", "module", "exc_info", "exc_text", "stack_info",
        "lineno", "funcName", "created", "msecs", "relativeCreated",
        "thread", "threadName", "processName", "process", "message",
        "asctime", "taskName",
    })

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        # Surface any structured `extra=` fields the caller passed.
        for key, value in record.__dict__.items():
            if key in self._SKIP_RECORD_ATTRS or key.startswith("_"):
                continue
            try:
                json.dumps(value)  # probe whether it's serializable
                payload[key] = value
            except (TypeError, ValueError):
                payload[key] = repr(value)
        return json.dumps(payload, ensure_ascii=False)


__all__ = ["configure_from"]
