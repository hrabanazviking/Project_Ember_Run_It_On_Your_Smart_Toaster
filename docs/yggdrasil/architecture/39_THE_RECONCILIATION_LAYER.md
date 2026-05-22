# 39 — The Reconciliation Layer

When cross-realm operations partially fail, who fixes them?
The reconciliation layer is Yggdrasil's answer.

---

## The problem

Cross-realm writes aren't transactional. If Ember writes a
new chunk to Bifrǫst (fan-out to Mímir + Huginn + Muninn +
MemPalace), one backend might succeed while another fails.

Without reconciliation:
- Mímir has the chunk.
- Huginn doesn't.
- Subsequent semantic-search misses it.
- Operator thinks "I ingested that document but Ember can't
  find it."

Bad state. Hard to debug.

---

## The reconciliation principle

**Every cross-realm operation produces a Receipt.** The
Receipt records what was attempted, what succeeded, what
failed. The reconciliation layer reads Receipts and retries
failures.

```
┌──────────────┐
│ Bifrost      │
│ fan-out      │
│ write        │
└──────┬───────┘
       │
       ▼ (writes to each backend)
   ┌───┴───┬─────┬──────┐
   ▼       ▼     ▼      ▼
 Mímir  Huginn Muninn MemPalace
   ✓      ✗     ✓      ✓
                                
   (Huginn failed — Qdrant timeout)
                                
   ┌──────────────────────────┐
   │   Receipt persisted       │
   │   {op_id, succeeded:[M,Mu,MP],│
   │    failed:[H], reason:…}   │
   └────────────┬──────────────┘
                │
                ▼
   ┌──────────────────────────┐
   │ Reconciliation Worker     │
   │ (async loop)              │
   └────────────┬──────────────┘
                │
                ▼ (when Huginn comes back)
   ┌──────────────────────────┐
   │ Retry Huginn write        │
   │ Mark Receipt resolved      │
   └──────────────────────────┘
```

---

## Receipt shape

```python
@dataclass(frozen=True, slots=True)
class Receipt:
    op_id: str            # UUID
    op_type: Literal["chunk_store", "chunk_delete", "episode_persist", ...]
    timestamp: datetime
    succeeded: tuple[str, ...]    # backend names that succeeded
    failed: tuple[FailedBackend, ...]   # backend names + reason
    resolved: bool = False
    resolved_at: datetime | None = None
    payload_ref: str | None = None   # what to retry (e.g., chunk_id from succeeded backend)
```

Receipts are persisted to a small SQLite database at
`~/.ember/yggdrasil/receipts.db`. Operator-readable; visible
in the Doctor screen.

---

## The reconciliation worker

A background async task in `src/ember/yggdrasil/reconciliation/worker.py`:

```python
class ReconciliationWorker:
    """Background task that retries failed cross-realm operations."""
    
    async def run(self):
        while True:
            await asyncio.sleep(self.config.scan_interval_s)
            unresolved = self.store.list_unresolved()
            for receipt in unresolved:
                await self.try_resolve(receipt)
```

Per-receipt retry logic:

1. Identify the failed backends.
2. Check if they're now reachable (via health probe).
3. If yes: re-attempt the operation against just those
   backends. Use the payload from a successful backend (the
   data is still there).
4. If success: mark Receipt resolved.
5. If still failing: increment retry count. After N retries
   (default 5), give up and mark `failed_permanently`.
   Surface to operator via Doctor.

---

## What operations need reconciliation

| Operation | Reconciliation strategy |
|---|---|
| Bifrǫst chunk write fan-out | Receipt + retry per backend |
| Bifrǫst chunk delete fan-out | Receipt + retry per backend |
| Episode persist fan-out | Receipt + retry per backend |
| Bifrǫst metadata update | Receipt + retry |
| Cross-device state sync (Phase 4) | Receipt + retry with conflict resolution |
| Secret rotation in Kista | Receipt (because secret may be cached in process memory) |

Operations that don't need reconciliation:
- Read operations (return what's available; degraded mode).
- Single-realm operations (no fan-out, no partial failure).
- Tool calls (audit log captures; tool framework handles).

---

## Conflict resolution

If a Receipt's retry succeeds but the underlying data has
*changed* in the meantime (e.g., the operator deleted the
chunk from another realm), we have a conflict.

Conflict resolution policy:

1. **Default: keep the existing state.** The chunk that's
   now deleted shouldn't be re-added.
2. **Operator can override** via per-receipt action in the
   Doctor screen.

For Phase 4 multi-device, conflict resolution gets more
involved (CRDT-like merge for shared state). Phase 1-3
ships the simpler "keep existing" policy.

---

## Observability of reconciliation

Verdandi events:

- `reconciliation.receipt_created` (op_id, failed_count)
- `reconciliation.retry_started` (op_id, attempt)
- `reconciliation.receipt_resolved` (op_id, attempt_count)
- `reconciliation.receipt_failed_permanently` (op_id, reason)

Stofa's DoctorScreen shows reconciliation queue depth:

```
┌── Reconciliation ──────────────────────────────┐
│  Unresolved receipts: 2                         │
│  ├ chunk_store (Huginn) — 3 retries, next in 5m │
│  └ episode_persist (MemPalace) — 1 retry         │
│  Permanently failed: 0                          │
│  Press r to retry all now                       │
└─────────────────────────────────────────────────┘
```

---

## What happens when a backend stays down for hours

Receipts accumulate. The retry interval backs off
exponentially (1 min → 2 min → 4 min → ... → max 1 hour).

When the backend comes back, all pending receipts get
retried. Most resolve in one pass.

Operators can view + act on accumulated receipts via the
DoctorScreen.

---

## Configuration shape

```yaml
yggdrasil:
  reconciliation:
    enabled: true
    receipt_db: ~/.ember/yggdrasil/receipts.db
    scan_interval_s: 30
    max_retry_count: 5
    backoff:
      initial_s: 60
      max_s: 3600
      multiplier: 2.0
    permanent_failure:
      surface_to_operator: true       # show in Stofa
      log_via_verdandi: true
```

---

## Why this matters for self-healing

The reconciliation layer is the **automated half** of
self-healing:

- Transient failures (network blip, brief Qdrant restart):
  reconciliation handles silently.
- Persistent failures (Qdrant misconfigured, disk full):
  reconciliation surfaces to operator after N retries.

The operator only sees what *they* need to fix. The system
takes care of the rest.

---

## Risk / known issues

- **Receipt-DB size growth.** If the system has a lot of
  failures, the receipts DB grows. We vacuum old resolved
  receipts (default: keep 30 days).
- **Stale-payload retries.** If the operator deletes a
  chunk while a retry is queued, the retry might restore it.
  Mitigation: check current state before retry; skip if
  conflict detected.
- **Multi-device receipt coordination** (Phase 4). Devices
  share receipts via the federation layer; only one device
  performs each retry.

---

## Operator-facing example

Operator runs `ember well ingest ~/notes` (1000 documents).
Mid-ingest, Qdrant container crashes.

Without reconciliation:
- Half the documents are in Mímir + Muninn + MemPalace.
- Half are also in Huginn; the second half isn't.
- Operator's semantic search returns inconsistent results.
- Hard to recover.

With reconciliation:
- Each chunk's failure produces a Receipt.
- When Qdrant restarts, the worker walks the receipt queue.
- Each missing chunk gets re-written to Huginn.
- All backends end up consistent.
- Operator may not even notice (other than slower-than-
  usual semantic search during the outage).

If Qdrant stays down for hours: operator gets a Doctor-
screen warning. They fix the underlying issue; the queue
drains.

---

## Closing

The Reconciliation Layer is **the automatic recovery
infrastructure**. Partial failures are normal in distributed
systems; the question is whether they get *forgotten* (bad)
or *queued for retry* (good).

Yggdrasil queues. Operators get a consistent constellation
without having to manually paper over every transient
network blip.

Self-healing isn't a slogan — it's this layer doing its
work in the background.
