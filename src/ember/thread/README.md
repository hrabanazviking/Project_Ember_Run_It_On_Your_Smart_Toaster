# `ember.thread/` — the Thread realm

**The middle realm. The tether between Spark and Well.** Thread owns
exactly one True Name: **Strengr** ("string, cord, tether"), and
exactly one subpackage: `strengr/`. The realm exists because the
network is unreliable and the operator's experience must not be.

**Shipped:** Phase 4, slice 1 (version 0.1.0). Unchanged in slice 2 —
the slice-1 contract held.
**Reads with:** `docs/architecture/ARCHITECTURE.md` §3.2; `docs/architecture/DOMAIN_MAP.md` §4; `docs/architecture/DATA_FLOW.md` §2.2 (the sad path).

---

## What this realm owns

Just `strengr/` — the tether. See `strengr/README.md` for the per-
subpackage breakdown.

Briefly, Strengr owns:

- Opening a Brunnr handle (with retry).
- Reporting health (what `ember doctor` reads).
- Turning network failure into a typed `Disconnected(reason, since)`
  value rather than an uncaught exception.

## Why this realm has only one subpackage

Per `ARCHITECTURE.md` §3.2 and `EMBER_TRUE_NAMES.md`: Strengr is
*the* place the cross-realm network boundary is made legible. If a
second tether type ever ships (e.g. a TCP-bridged Strengr for a
hypothetical cross-Ember sync protocol), it would join Strengr as a
peer in this realm — not replace it.

Slice 2 didn't add any new tether work; the slice-1 `strengr.tether`
implementation handled the pgvector adapter's open path the same way
it handled sqlite_vec, because both backends honor the same
`BrunnrHandle.open() → BrunnrHandle | Disconnected` contract.

## What this realm does NOT own

- **Backend-specific protocols.** Inside the Brunnr adapter
  (`well.brunnr.*`).
- **Conversation memory.** That's Well content.
- **What to retrieve.** That's Spark's job.
- **Funi-side network.** Funi's own `open()` handles its endpoint
  reachability (`Unavailable(ENDPOINT_UNREACHABLE)`); Strengr is
  specifically the Well-side tether.

## How Spark reaches the Well through Thread

```
[Spark]
  Munnr.run(config) calls:
     well_result = strengr.open(config.strengr, config.brunnr)
                   # ↓
                   # [Thread]
                   # strengr.tether.open():
                   #   brunnr_handle.open(brunnr_cfg) → BrunnrHandle | Disconnected
                   #   on Disconnected: log, return; no raise
                   # ↑
  if isinstance(well_result, Disconnected):
      brunnr, disconnect = None, well_result
      # render "ungrounded" banner; continue
  else:
      brunnr, disconnect = well_result, None
```

The shape of this dance is the Vow of Graceful Offline made
mechanical. The type system *forces* Spark to handle the
`Disconnected` branch.

## Layout

```
src/ember/thread/
├── README.md
├── __init__.py
└── strengr/
    ├── README.md
    ├── INTERFACE.md
    ├── __init__.py
    └── tether.py        # open() with retry; classifies Disconnected reasons
```

## Slice-2 notes

No code changes — Strengr's slice-1 implementation worked unchanged
for pgvector. The pgvector adapter's `_classify_operational_error`
helper (ADR 0010 §2.8) produces the same eight typed `DisconnectReason`
values that Strengr's retry policy already understood.

## Related

- `docs/architecture/ARCHITECTURE.md` §3.2 — Thread realm definition.
- `docs/architecture/DOMAIN_MAP.md` §4 — ownership.
- `docs/architecture/DATA_FLOW.md` §2.2 — the sad path (what happens
  when the Well is unreachable mid-turn).
- `docs/architecture/EMBER_TRUE_NAMES.md` §Strengr.
- `strengr/INTERFACE.md` — public surface.
