# E-087 — Corruption & recovery drills: what survives a crash

*Part V, slice E-087. Roadmap line: "Corruption & recovery
drills (atomicity, kill-mid-write)." The drills live in
`tests/unit/test_memory_recovery_e087.py` and run against
the one memory face (E-080) and the two bounded engines
behind it. Three defects the drills exposed are fixed in
this slice: docket 121 in `mimir-well/src/mimir_well/
core.py` (`RunaMemory.supersede`), docket 122 in
`src/ember/well/memory_face.py` (`MemoryFace._maybe_index`),
and docket 124 in mimir-well's restore path
(`RunaMemory.restore_from` + `backup.py`). One further
boundary is measured, pinned, and docketed (123), not
silently left.*

## In plain words

**We tried to break the companion's memory the way real
life breaks it — and wrote down exactly what survived.**
A drill is not a mock: a real child process was killed
with SIGKILL in the middle of writing facts and in the
middle of replacing facts; faults were injected inside
write transactions; files were garbled on disk. After
each injury the memory was reopened and asked what it
could honestly say.

The headline: **a single fact write is atomic and a
killed writer loses nothing it had committed** — the
stores are SQLite in WAL mode with `synchronous = FULL`,
and every committed fact came back whole, every time.
**Replacing a fact was not atomic, and now is** (docket
121, below). And when a whole store file is destroyed,
the face says so plainly and keeps serving the half that
lives — it never pretends, and it never invents.

## 1. The ground the drills stand on

Three stores, three writers, three failure shapes:

| Store | Writer | Durability shape |
|---|---|---|
| Living facts | mimir-well (`RunaMemory`) | One SQLite file, WAL, `synchronous = FULL`, foreign keys on; writes go through `_write` (lock + one commit) |
| Turns + fact index | Brunnr sqlite_vec adapter | One SQLite file, WAL, `synchronous = FULL` |
| Persona tags + index map | The face's `_Sidecar` | One JSON file, replaced atomically (write `.tmp`, `os.replace`) on every change; a corrupt file loads as empty — fail-closed |

Persona truth for facts lives in mimir-well itself
(`user_id` on every row, E-083); the sidecar only carries
what the engines cannot: which persona a turn belongs to,
and which Brunnr chunk indexes which fact. That split is
what makes most injuries degrade instead of destroy.

## 2. The drills

### 2.1 Kill-mid-write (SIGKILL, real child processes)

A child process opens the face on a fresh store and
writes in a tight loop, printing each committed id; the
parent reads a run of commits, then sends SIGKILL — the
kill no cleanup handler can catch. Two rounds each:

- **Fact writes.** After the kill: `PRAGMA
  integrity_check` is `ok`; every fact the child reported
  committed is present with its content whole; at most
  one further row exists (the write in flight at the
  kill), and if present it too is complete — a fact is
  never torn in half. The reopened face reports the
  mimir half live and word search returns exactly the
  rows on disk.
- **Supersede chains.** The child replaces one fact over
  and over (v0 → v1 → v2 …). After the kill: exactly one
  version is current — the newest whole one — every old
  version names its heir in `superseded_by`, and every
  heir exists. Never two current truths, never none.
  This drill is the one docket 121's fix had to earn
  (§3): against the old two-commit supersede, the same
  shape of failure is proven deterministically by the
  fault-injection drill (§2.2).

### 2.2 Atomicity under fault injection

Deterministic, in-process: a write function is replaced
by one that performs the operation's steps and raises
*inside* the transaction, or at the operation's second
write step, and the store is then closed and reopened.

- `add_memory` with a crash inside its write: the fact
  is absent whole after reopen — never half-present —
  and integrity is `ok`.
- `supersede` with a failure aimed at its second write
  step: exactly one current version after reopen, the
  chain intact. (Before the fix there *was* a second
  write step, and this drill leaves both versions
  current against that code.)

### 2.3 The sidecar injured

- **Garbled sidecar JSON** (bytes overwritten): the face
  opens, the facts are untouched — word search still
  reads mimir-well's own per-persona truth and one
  persona's facts never answer another's query — while
  meaning search resolves nothing (the chunk map is
  gone, and unmapped chunks are dropped rather than
  guessed into someone's hands) and turns fall back to
  the default persona only. Fail-closed, exactly as the
  sidecar's own docstring promises.
- **An orphan `.tmp`** (a save killed between write and
  replace): ignored. The last whole sidecar wins, tags
  and meaning search intact.

### 2.4 The stores injured

- **Garbled mimir-well file** (first 4 KiB overwritten):
  `MemoryFace.open` reports that half `unavailable`
  with the reason, never raises; `remember_fact` refuses
  with the state named; the Brunnr half still takes and
  serves turns.
- **Zeroed mimir-well file**: reopens as a NEW empty
  store — schema rebuilt, integrity `ok`, first write
  succeeds. The drill names this honestly: a zeroed
  store is not a *recovered* store; the memory in it is
  gone, and what speaks afterwards is a fresh well, not
  the old one healed.
- **Dropped FTS index** (`memories_fts` dropped by
  direct SQL): reopening rebuilds the index from the
  content tables at open, and word search finds the
  facts again.
- **Backup & restore**: a backup taken through
  `backup_to` (SQLite backup API, `quick_check`-verified
  before it is ever returned) restores the backup-time
  truth exactly — facts written after the backup are
  gone after the restore, as they should be. A garbled
  "backup" is refused by validation and the restore
  attempt changes nothing in the live store. **This
  drill failed as first written** — the restore itself
  was corrupt (docket 124, §3) — and passes only with
  that fix in.

## 3. What the drills found and this slice fixed

### Docket 121 — supersede was two commits, and crashed on refusal

`RunaMemory.supersede` inserted the new fact through
`add_memory` (commit one) and only then marked the old
fact superseded (commit two). A kill or crash between
the commits left **both versions current** — two current
truths for one fact, neither pointing at the other. The
same shape had a second edge: `add_memory` returns
`None` when its guard blocks a write, and the old code
compared that with `<` — a guard-blocked supersede
**raised `TypeError`** instead of refusing (proven by
probe before the fix: seed a fact, supersede it with
null-byte content, watch it raise).

The fix, in the member: the guard runs first, exactly as
`add_memory` runs it; then the insert and the mark
execute inside **one transaction** (one `_write`), with
ownership of the old fact re-checked inside that
transaction so a vanished or foreign old fact refuses
whole — nothing written. The audit row is written after
the commit, as `add_memory` writes it, now also naming
the superseded id. A blocked supersede returns `None`:
nothing written, the old fact still current. The face
already turns a falsy return into its plain "supersede
refused" note, so no face change was needed for this
half.

### Docket 122 — the face raised across a committed write

`MemoryFace._maybe_index` saved the sidecar *after* the
fact had committed in mimir-well and the chunk had
landed in Brunnr — and let an `OSError` from that save
propagate out of `remember_fact`. The caller was told
the remember had failed; the fact was in fact stored.
Now the save failure returns the function's honest-note
shape instead: the fact id stands, `indexed` is False,
and the note says the fact is stored, its index record
could not be saved, and word search still finds it. The
orphaned chunk (written, unmapped) stays resolvable in
the running process; after a restart it is an unmapped
orphan, which `prune_stale_index` (E-082) exists to
collect.

### Docket 124 — the restore road itself corrupted the store

`RunaMemory.restore_from` swapped the database file with
a raw copy **while its own connection and the audit
trail's connection were still open on the live file**,
and nothing removed the live file's WAL. On the next
open, SQLite replayed that stale write-ahead log into
the restored file: post-backup writes resurrected,
backup-time rows were overwritten by stale frames — a
mixed store wearing neither truth — while the restore
reported success. The drill caught it exactly: after a
restore, the store held the later fact and had lost a
backup-time one.

The fix: `restore_from` now closes every connection the
instance holds (its own and the audit trail's) *before*
the swap — closing the last connection checkpoints and
removes the WAL — and `restore_from_backup` removes any
`-wal`/`-shm` siblings still present after a copy (they
index the replaced file, never its replacement), on both
the restore and the safety-rollback path. The drill now
proves the sentence §2.4 makes: a restore returns the
backup-time truth, exactly.

## 4. The boundary the drills pin, not fix — docket 123

`MemoryFace.add_turn` writes the episode to Brunnr and
*then* saves its persona tag in the sidecar. That pair
is not one transaction and cannot be made one across
two stores; the drill pins the exact consequence:

- If the tag save fails in-process, `add_turn` raises
  the `OSError` — the caller is told, never silently
  misled (this half is deliberate and stays).
- If the process dies between the commit and the save,
  the turn survives untagged. On reopen, the docket-117
  rule serves an untagged turn to the face's **default
  persona only** — never to a named other persona, and
  never off the machine: all personae here are one
  person's own, on their own hardware. The mis-filing is
  bounded to one turn, in the wrong drawer of the same
  house.

Making this pair crash-atomic would need a write-ahead
tag journal or moving turn tags into Brunnr — a design
change, not a drill repair; it is docketed (123) for the
Part V gate (E-092) to weigh, with this drill as its
evidence. Nothing in this slice claims more than the
drill proves.

## 5. What the drills do not prove

- Power loss at the hardware layer: SIGKILL and injected
  faults stand in for it, but no drill here cuts actual
  power or faults the disk; `synchronous = FULL` is the
  engines' promise, taken as read.
- The pgvector Brunnr backend is not drilled (this
  tree's tiny-hardware shape is sqlite_vec; the gate
  environments carry no live Postgres).
- A torn file *inside* the facts table's pages (bit-rot
  in the middle of the database, header intact) is not
  drilled: SQLite's `integrity_check` would name it, and
  the honest recovery there is §2.4's backup road — the
  drill proves the road, not every wreck on it.
- Concurrency beyond the member's own lock (two
  processes writing one store) is E-083/E-088 territory,
  not claimed here.
