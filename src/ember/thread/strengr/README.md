# `ember.thread.strengr/` — Strengr

**The tether.** Makes the Well usable from Spark without leaking the
network surface into Spark code. The single boundary across which
"the network failed" becomes *legible* rather than catastrophic.

**Shipped:** Phase 4, slice 1 (version 0.1.0). Unchanged in slice 2 —
the contract held across the pgvector adapter addition.
**Reads with:** `INTERFACE.md` for the public surface; `docs/architecture/DOMAIN_MAP.md` §4; `docs/architecture/DATA_FLOW.md` §2.2 (the sad path).

---

## What this subpackage owns

`tether.py` — exactly one module:

- **`open(strengr_config, brunnr_config) -> BrunnrHandle | Disconnected`** —
  attempts to acquire a live Brunnr handle, with bounded retry per
  the operator's `StrengrConfig`. Returns the live handle or a typed
  `Disconnected` value.
- **Retry-with-backoff** — `retry_attempts` and `retry_backoff_max_s`
  honoured from `StrengrConfig`. Bounded so a misbehaving Well
  doesn't lock up the REPL.
- **Health snapshot** — `health(brunnr_handle, brunnr_config) -> StrengrHealth`
  reads what `ember doctor` displays (last successful probe time,
  backend kind, count snapshot).
- **The graceful-offline contract** — `open()` returns
  `Disconnected(reason, since, detail)` rather than raising.
  Recoverable reasons (CONN_REFUSED, TIMEOUT, DNS_FAILURE) get
  backoff-retry; non-recoverable (AUTH_FAILED, CONFIG_INVALID,
  BACKEND_REPORTED_UNAVAILABLE) surface immediately.

## What this subpackage does NOT own

- **Backend-specific network protocols.** SQLite is local-only;
  pgvector uses libpq via psycopg. Each adapter handles its own
  wire-level concerns; Strengr only sees the typed `Disconnected`
  classification the adapter returns.
- **Reconnect logic during an active turn.** Strengr's retry is
  during `open()`. If a mid-turn `BrunnrError` happens, Munnr
  suppresses it (per the `add_episode` `contextlib.suppress` pattern)
  and continues; full reconnect waits for next REPL turn.
- **Persistence.** That's Brunnr.
- **What to retrieve.** That's Spark.

## The `Disconnected` value (per `ember.schemas.errors`)

```python
@dataclass(frozen=True, slots=True)
class Disconnected:
    reason: DisconnectReason     # the typed classifier
    since: datetime              # when the open failed
    detail: str | None = None    # operator-readable extra context

class DisconnectReason(StrEnum):
    CONN_REFUSED = "conn_refused"
    TIMEOUT = "timeout"
    AUTH_FAILED = "auth_failed"
    DNS_FAILURE = "dns_failure"
    CONFIG_INVALID = "config_invalid"
    BACKEND_REPORTED_UNAVAILABLE = "backend_reported_unavailable"
    UNKNOWN = "unknown"
```

Strengr maps adapter-side failures into these values per the table in
ADR 0010 §2.8 (slice-2 pgvector adapter) — same eight reasons the
sqlite_vec adapter uses.

## Retry-with-backoff (slice-1 semantics)

`StrengrConfig` knobs (defaults):

```python
@dataclass(frozen=True, slots=True)
class StrengrConfig:
    health_check_timeout_s: float = 5.0
    retry_attempts: int = 3
    retry_backoff_max_s: float = 30.0
```

`open()`:

1. Calls `brunnr_handle.open(brunnr_config)`.
2. If the result is `Disconnected` AND the reason is recoverable AND
   we've used fewer than `retry_attempts` tries, wait
   `min(2^attempt, retry_backoff_max_s)` seconds and retry.
3. If the result is `Disconnected` AND the reason is non-recoverable,
   return it immediately — no retry, no backoff.
4. Otherwise return the live `BrunnrHandle`.

Tests override `retry_backoff_max_s=0.0` to keep test runs fast.

## Layout

```
src/ember/thread/strengr/
├── README.md
├── INTERFACE.md
├── __init__.py        # re-exports open + health
└── tether.py          # the implementation
```

## Failure semantics — what Strengr never does

- **Strengr never raises a connection error.** Always returns
  `Disconnected`. Spark code is *forced* by the type system to handle
  that value.
- **Strengr never retries indefinitely.** Operator-configured bound;
  default 3 attempts.
- **Strengr never silently degrades.** Every `Disconnected` carries a
  typed `reason` so the operator can fix the right thing
  (`AUTH_FAILED` ≠ `CONN_REFUSED` ≠ `DNS_FAILURE`).
- **Strengr never modifies the Brunnr.** It opens, it reads health,
  it closes — never writes.

## Slice-2 notes

- **Phase 13 pgvector live**: Strengr handled the new adapter without
  modification. The pgvector adapter's `_classify_operational_error`
  produces the same eight `DisconnectReason` values; Strengr's
  retry-policy table treated them identically to the sqlite_vec
  adapter's classifications.
- **No new reasons added.** ADR 0013 §2.3 ratified the eight-reason
  set as canonical going into slice 3.

## Related

- `INTERFACE.md` — public surface.
- `docs/architecture/DATA_FLOW.md` §2.2 — the sad path: what happens
  when Strengr returns Disconnected mid-conversation.
- `docs/architecture/EMBER_TRUE_NAMES.md` §Strengr — what the True
  Name owns vs doesn't own.
- `docs/decisions/0010-pgvector-brunnr.md` §2.8 — how the new adapter
  classifies failures into Strengr's existing reason set.
- `tests/unit/test_strengr_tether.py` — 15 unit tests covering retry
  logic + reason classification.
- `tests/integration/test_strengr_real_backend.py` — real sqlite_vec
  smoke.
