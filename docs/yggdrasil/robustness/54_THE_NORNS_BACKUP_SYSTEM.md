# 54 — The Norns Backup System

Past / present / future state snapshots. Named after the
three Norns — Urðr, Verðandi, Skuld — who weave fate at
the world-tree's root.

---

## The metaphor

The three Norns:
- **Urðr** (Wyrd) — what has been.
- **Verðandi** — what is becoming.
- **Skuld** — what should/will be.

Yggdrasil's backup system captures each:
- **Urðr** — *past snapshots*. Daily backups going back
  N days.
- **Verðandi** — *present state*. The current live data.
- **Skuld** — *future projection*. (V2; not in V1 — we
  don't predict.)

In V1 we ship Urðr + Verðandi (live data + past
snapshots). Skuld is reserved.

---

## What gets snapshotted

Every realm with operator-relevant state:

| Realm | State to snapshot |
|---|---|
| **mimir-well** | the SQLite DB |
| **Huginn (Qdrant)** | the collection (via Qdrant snapshot API) |
| **Muninn** | the Hebbian DB |
| **MemPalace** (if used) | its DB |
| **Verdandi event ring** | last N events (already in memory) |
| **Kista vault** | the encrypted vault file |
| **Yggdrasil meta-learning patterns** | the patterns DB |
| **Reconciliation receipts DB** | the receipts DB |
| **Episodes** | already in Brunnr; no separate snapshot needed |
| **identity.json + ember.yaml** | config files |

NOT snapshotted:
- Funi model weights (operator-managed; potentially huge).
- Sibling project source code (in git).
- Stofa UI state (transient).

---

## Snapshot timing

Three triggers:

### 1. Daily (during dreamstate)

A snapshot fires after each dreamstate consolidation. This
is the *Urðr daily* backup.

Retention: 30 daily snapshots by default (operator-tunable).

### 2. Pre-risky operation

Before any of these:
- Major schema migration.
- Realm version upgrade (operator runs `pip install -U …`).
- Operator-initiated "reset" actions.

A pre-operation snapshot captures the *known-good state*
to roll back to.

### 3. Manual

```bash
ember yggdrasil snapshot create --label "before-deep-refactor"
```

Operator-triggered, labeled, retained until manually
deleted.

---

## Snapshot storage

Snapshots land at:

```
~/.ember/yggdrasil/snapshots/
  2026-05-21_daily/
    mimir.db
    qdrant_collection.snapshot
    muninn.db
    mempalace_export.json
    verdandi_events.jsonl
    kista_vault.enc
    patterns.db
    receipts.db
    config/
      ember.yaml
      identity.json
    manifest.json
  2026-05-20_daily/
    ...
  pre-bifrost-2.0/      ← pre-upgrade
    ...
  manual_before_refactor/   ← operator-labeled
    ...
```

Each snapshot is a directory; `manifest.json` records what
versions of each realm were running, what was snapshotted,
checksums.

---

## Snapshot size considerations

Daily snapshots can grow:

- mimir.db: ~50MB after months of use.
- Qdrant collection: similar.
- 30 daily snapshots × ~150MB each = ~4.5GB.

We use **incremental snapshots** where possible:
- SQLite: hard-linked copies (most pages unchanged between
  days; copy-on-write at filesystem level).
- Qdrant: native incremental snapshot API.

Result: ~150MB for the first; ~20-50MB per subsequent
daily. 30 days fits in ~2GB typically.

Operators on Pi-class with small disk can reduce retention
(`retain_days: 7`) to limit footprint.

---

## How to restore from a snapshot

```bash
ember yggdrasil snapshot list
# Shows: 2026-05-21_daily, 2026-05-20_daily, ..., manual_*

ember yggdrasil snapshot restore 2026-05-20_daily
# Confirms; replaces current state from the named snapshot
# Daemons restart; operator's chat resumes from that point
```

Restore is **per-snapshot, all-or-nothing**. We don't
restore *individual realms* from one snapshot while keeping
others — that creates inconsistency.

Restoration creates a *pre-restore snapshot* of the
current state so operator can roll back if needed.

---

## What restore actually does

For each snapshotted realm:
1. Stop the realm (close handles, kill daemon if applicable).
2. Replace the realm's data files with the snapshot copy.
3. Restart the realm.
4. Verify health via gossip.

For config files:
1. Back up current `ember.yaml` + `identity.json`.
2. Replace with snapshot versions.
3. Re-load config.

After all realms restored: full Yggdrasil starts fresh
from the snapshotted state.

---

## Configuration shape

```yaml
yggdrasil:
  norns:
    enabled: true
    snapshot_dir: ~/.ember/yggdrasil/snapshots
    schedule:
      daily_during_dreamstate: true
      pre_risky_ops: true
    retention:
      daily_days: 30
      manual_snapshots: unlimited
      pre_upgrade_snapshots: 5     # keep last 5
    storage:
      use_hardlinks: true           # for SQLite
      compress_old: true            # gzip snapshots > 7 days old
```

---

## What this gives operators

### Recovery from catastrophic state corruption

If a sibling project ships a buggy update that corrupts
the Mímir DB:
- Operator notices.
- `ember yggdrasil snapshot restore <yesterday>`.
- State rolls back to yesterday.
- Operator pins the sibling version to the pre-buggy one.

### Time travel for debugging

Operator wants to understand "what was Ember thinking last
Tuesday?" — they can spin up a snapshot in a temporary
Yggdrasil instance:

```bash
ember yggdrasil snapshot inspect 2026-05-17_daily
# Opens a read-only Stofa pointed at that snapshot
# Operator browses Episodes, Well, etc. — without changing
# their live state
```

V2 feature; sketched here.

### Confidence in destructive actions

When operator considers a risky operation (re-ingesting a
huge corpus, deleting documents, etc.), they take a
snapshot first. If it goes wrong: roll back.

---

## Risk / known issues

- **Disk space.** Snapshots add up. Operators on Pi-class
  with small SD card: tune retention down.
- **Backup-of-secrets concern.** The Kista vault is in
  every snapshot. If snapshots leak (e.g., copied off-
  device unencrypted), so do the vault contents — but the
  vault is *itself* encrypted; attacker still needs the
  master key.
- **Cross-version snapshot compatibility.** Restoring a
  snapshot from V1 onto V2 might fail if schemas changed.
  Migration paths documented per release.

---

## How the Norns relate to other backup tools

Yggdrasil's snapshot system is **internal** — knows about
all realms, snapshots them coherently, restores them
together.

Operator can ALSO use external backup tools (restic, borg,
rsnapshot) for off-device backup of `~/.ember/`. The two
don't conflict.

Recommended pattern:
- Norns snapshots for *quick local rollback*.
- External tool for *off-device archive* (against disk
  failure, theft, fire).

---

## Verdandi observability

Snapshot events flow through Verdandi:
- `norns.snapshot_started` (label, trigger)
- `norns.snapshot_completed` (label, size_mb)
- `norns.snapshot_failed` (label, reason)
- `norns.restore_started` (label)
- `norns.restore_completed` (label)

Stofa's DoctorScreen surfaces snapshot status:

```
Norns Backups:
  Latest: 2026-05-21_daily (12 minutes ago, 142 MB)
  Total snapshots: 30 daily, 2 pre-upgrade, 1 manual
  Disk used: 1.8 GB
  Next: tonight during dreamstate
```

---

## Closing

The Norns Backup System gives Ember **time depth**. Today's
state is one of many possible states; yesterday's is
recoverable; tomorrow's builds from now.

Combined with self-healing playbooks, snapshots are the
**escape hatch for the rare failures playbooks can't fix
automatically**. Operator action; one command; rollback.

Fate is fully fixed (says the Hávamál), but state isn't.
The Norns keep options.
