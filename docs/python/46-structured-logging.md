# 46 — Structured Logging in Python: structlog, loguru, stdlib

**Category:** Observability & Operations
**Runa relevance:** every subsystem, `core/logging/`, audit log
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

Traditional logging produces *human-readable strings* — `INFO: User 42 logged in from 1.2.3.4`. Parsing those later for analysis means writing regex, fighting format drift, and losing information that wasn't in the line. **Structured logging** emits *structured records* — `{"level":"info","event":"login","user_id":42,"ip":"1.2.3.4"}` — queryable, filterable, machine-friendly. The shift is one of the highest-leverage operational improvements.

For Runa, structured logging is the substrate under both observability and audit. Same logs serve `runa logs` searches, debugging, performance analysis, audit-trail. `structlog` is the modern Python standard; the stdlib `logging` works with a JSON formatter. Either is fine.

## 2. Technique / mechanism

**structlog basics:**

```python
import structlog

log = structlog.get_logger()

log.info("login", user_id=42, ip="1.2.3.4")
# Default output: 2026-05-17T12:00:00 [info] login user_id=42 ip=1.2.3.4
```

Key-value pairs after the event name. No format strings.

**Configuration for JSON output:**

```python
import structlog
import logging

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.dict_tracebacks,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

log = structlog.get_logger()
log.info("kernel_turn_complete", turn_id="abc", duration_ms=245)
# Output: {"event":"kernel_turn_complete","level":"info","timestamp":"2026-05-17T12:00:00Z","turn_id":"abc","duration_ms":245}
```

JSON output goes to stdout/stderr; tools (jq, journalctl, structured-log searchers) parse it.

**Context binding:**

```python
log = log.bind(correlation_id=heard.event_id)
log.info("retrieving_memory")  # automatically includes correlation_id
log.info("calling_provider", provider="anthropic")  # also includes correlation_id
```

`bind` returns a new logger with added context. Avoid mutating shared loggers.

**ContextVar-based binding (works across async):**

```python
from structlog.contextvars import bind_contextvars, clear_contextvars

# In a kernel turn:
bind_contextvars(correlation_id=heard.event_id, conversation_id=heard.conv_id)
try:
    # All log calls inside this block get those keys automatically
    ...
finally:
    clear_contextvars()
```

Powerful: every deep call site picks up the context without explicit passing.

**Pretty-print for development:**

```python
import structlog

structlog.configure(
    processors=[
        ...,
        structlog.dev.ConsoleRenderer(colors=True),  # pretty, not JSON
    ],
)
```

Toggle between dev (pretty) and prod (JSON) per config.

**Stdlib `logging` with JSON formatter:**

```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps({
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "event": record.getMessage(),
            **getattr(record, "extra", {}),
        })

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logging.getLogger().addHandler(handler)
```

Or use `python-json-logger` library.

**loguru — alternative:**

```python
from loguru import logger

logger.info("login", extra={"user_id": 42, "ip": "1.2.3.4"})
```

Easier API; less flexible than structlog for advanced cases.

**Log levels:**

- **DEBUG** — verbose; helpful when investigating.
- **INFO** — normal operational events ("kernel_turn_complete").
- **WARNING** — something off but handled ("retry triggered").
- **ERROR** — something failed; investigate ("adapter quarantined").
- **CRITICAL** — agent integrity at risk.

Default INFO in production; DEBUG only when investigating.

**Performance:**

- Filtering happens before formatting in modern setups. INFO-level filter on a DEBUG call costs ~microsecond.
- JSON serialisation costs ~tens of microseconds per record. Negligible for normal log volumes; noticeable if logging in a tight loop.
- Don't log inside hot loops at INFO. Use TRACE / sample.

**Secret redaction:**

```python
def redact_secrets(_, __, event_dict):
    """Redact known secret patterns from log records."""
    for key in list(event_dict.keys()):
        if key.lower().endswith(("_key", "_token", "_password", "_secret")):
            event_dict[key] = "***REDACTED***"
    return event_dict

structlog.configure(
    processors=[
        ...,
        redact_secrets,
        ...,
    ],
)
```

A processor in the structlog chain ensures secrets never hit the log.

## 3. Key works / libraries

- **structlog** — structlog.org.
- **loguru** — github.com/Delgan/loguru.
- **python-json-logger** — github.com/madzak/python-json-logger.
- **stdlib `logging`** — docs.python.org/3/library/logging.html.
- **The Twelve-Factor App, factor 11 (logs)** — 12factor.net/logs.
- **OpenTelemetry semantic conventions for logs** — opentelemetry.io.

## 4. Pitfalls and gotchas

- **String interpolation in log calls.** `log.info(f"user {x}")` — formatting happens even if filtered. Use `log.info("user", user_id=x)`.
- **PII in logs.** Names, emails, IPs, content. Redact at source or with processors.
- **Logging exceptions without traceback.** Use `log.exception(...)` or pass `exc_info=True`.
- **Per-call configuration.** Stdlib `logging.basicConfig` runs once. Multiple calls are silently no-op.
- **Async + structlog.** Use `bind_contextvars` (works across `await`); avoid `log.bind` shared across coroutines.
- **Log rotation.** stdlib `RotatingFileHandler` / `TimedRotatingFileHandler` rotate. JSONL daily rotation pattern common.
- **JSON in non-ASCII.** `ensure_ascii=False` for proper Unicode.

## 5. Applicability to Runa

For **`core/logging/`**:

- Use `structlog`. Configure once at startup.
- JSON output to journal (systemd) / stdout (Docker / dev).
- Secret-redaction processor in the chain.
- ContextVar-based correlation_id binding per turn.

For **audit log**:

- Separate stream from operational logs. Distinct file (`~/.runa/logs/audit/YYYY-MM-DD.jsonl`).
- Stricter rules: hash-chained, retained per policy.

For **per-subsystem loggers**:

- `log = structlog.get_logger("runa.muninn")`. Module-namespaced for filterable per-subsystem log output.

For **dev vs prod**:

- Dev: ConsoleRenderer with colours.
- Prod: JSONRenderer.
- Toggle via `RUNA_LOG_FORMAT` env var.

For **runa logs CLI**:

- Reads JSONL log files; supports filtering by level / correlation_id / time / module.

What to avoid:

- Don't use f-string formatting in log calls.
- Don't log secrets unredacted.
- Don't log inside tight loops at INFO.
- Don't `print()` for diagnostic output. Use the logger.

## 6. Open questions

- **Log aggregation for multi-machine.** When Runa runs across Pi + laptop, central log aggregation (Loki, ELK, journald-remote) becomes useful. Single-Pi: local files.
- **Sampling.** High-volume events sampled instead of every-record. Trade-off with completeness.
- **Log-based tracing.** Logs with span IDs become trace events. OpenTelemetry-compatible. See [[47-distributed-tracing-opentelemetry]].

## 7. References (curated)

- structlog.org.
- github.com/Delgan/loguru.
- docs.python.org/3/library/logging.html.
- 12factor.net/logs.
- Companion docs: [[40-audit-logging-replay]] (research corpus), [[47-distributed-tracing-opentelemetry]], [[48-metrics-prometheus]].
