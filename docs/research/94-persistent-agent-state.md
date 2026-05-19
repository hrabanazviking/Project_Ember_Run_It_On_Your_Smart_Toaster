# 94 — Persistent Agent State: File Systems, Snapshots, Journals

**Category:** AI Operating System
**Runa relevance:** Muninn persistence, identity store, recovery, backup
**Status:** Engineering synthesis. The disk-level foundation of cross-session being.
**Last touched:** 2026-05-17

---

## 1. Core idea

A long-lived agent that survives across sessions, machines, and years requires careful design of *what is on disk*, *how it's organised*, *how it changes safely*, and *how it can be recovered from corruption or loss*. This is the file-system layer of the AI OS. The decisions here — append-only journals, snapshot policies, backup architecture, migration support — determine whether Runa-in-five-years can read everything Runa-today wrote, whether disk corruption is catastrophic or recoverable, and whether Volmarr can move Runa from one machine to another cleanly.

The principles are not novel — database engineering, version control, and document-archival fields have decades of experience. What's distinctive is *which patterns to choose* for an agent whose state is a mix of slowly-changing prose, rapidly-changing event data, and intermittent large binary blobs (model adapters, embeddings).

## 2. Technical depth

**Categories of Runa state.**

| Category | Examples | Change rate | Format | Backup priority |
|---|---|---|---|---|
| Identity | persona.md, values.md | Slow (weeks-months) | Markdown | Highest |
| Identity journal | identity_journal.jsonl | Append-only | JSONL | Highest |
| Relationships | volmarr.json, *.bdi.jsonl | Medium | JSON/JSONL | High |
| Saga chapters | weekly/*.md | Append (immutable once written) | Markdown | High |
| Episodes (Muninn) | episodes.db | Append-fast | SQLite | High |
| Semantic graph | triplets.db | Append-with-supersession | SQLite | Medium |
| Reflections | reflections.db | Append | SQLite | Medium |
| Embeddings | embeddings.faiss / .vss | Rebuildable from text | Binary | Low (regenerable) |
| Logs | turn_log.jsonl, debug.log | Append-fast | JSONL | Low (retain N days) |
| Config | *.yaml | Slow | YAML | Medium (git-tracked) |
| Adapters | *.safetensors | Rare | Binary | High (large; tier separately) |
| Cache | various | Volatile | Various | None |

The categories have different lifecycles. *Backup priority* and *recovery strategy* differ per category.

**Append-only as a default.**

Per RULES.AI.md and the cognitive-architecture rationale ([[52-cross-session-persistent-identity]]): identity state is *append-only*. The identity_journal never deletes; the Saga chain never rewrites; even Muninn episodes are demoted, not deleted ([[57-sleep-dream-replay-consolidation]]).

This pattern is event-sourcing ([[22-event-sourcing-cqrs]]): the *log* is authoritative; *projections* (derived state) are rebuildable from the log.

**Snapshot policy.**

A *snapshot* is a checkpoint of state at a particular moment, packaged for backup or migration.

- *Cadence*: nightly snapshots of all state directories.
- *Tooling*: a `runa snapshot create` command produces a tarball + integrity hash.
- *Retention*: keep last 7 daily, last 4 weekly, last 12 monthly, last 5 annual. Pruning automated.
- *Location*: at least two locations — local disk + external (Tailscale-mounted remote disk, or cloud).

**Integrity checking.**

- Snapshots include SHA-256 of every file.
- A `runa integrity check` command verifies present state against last good snapshot.
- Corruption surfaces immediately with the divergent file.
- Periodic background integrity check (weekly) catches latent corruption.

**Migration support.**

Moving Runa from machine A to machine B:

1. Stop Runa cleanly on A (flush in-flight tasks).
2. Snapshot.
3. Transfer snapshot to B (rsync, Tailscale, USB).
4. Restore on B.
5. Verify integrity.
6. Start Runa on B.

The substrate is *machine-independent by design*: relative paths, portable database formats, configuration-driven. Per RULES.AI.md: no hard-coded paths.

**Recovery procedures.**

For each failure mode, a documented procedure:

- *File corruption*: replace from most recent good snapshot.
- *Database corruption*: restore from snapshot; replay journal from snapshot timestamp to now if log available.
- *Disk failure*: restore from off-machine backup.
- *Partial loss* (some directories): restore only those.
- *Identity rollback* (Volmarr wants to undo recent changes): restore identity files from earlier snapshot; identity_journal records the rollback as a new event (the rollback itself becomes history).

**Migration across model versions.**

When the base LLM is upgraded ([[62-identity-stability-under-change]]), state migration is *almost* the trivial case — most state is model-independent (markdown, sqlite). Adapters and embeddings are model-specific:

- Identity-LoRA adapters tied to a base model; on upgrade, either retrained from the corpus or kept as legacy if not retrained.
- Embeddings: regenerable from text. On a substantial embedding-model upgrade, full re-embedding is a one-time job.

**Storage technology choices.**

- *SQLite* for transactional structured data (episodes, triplets, reflections). Robust, single-file, append-friendly, no separate server.
- *JSONL* for append-only event logs (journal, turn logs). Trivially parseable; line-oriented.
- *Markdown* for human-readable state (persona, Saga chapters). Git-friendly; diff-able.
- *YAML* for configuration.
- *FAISS / sqlite-vss* for vector indexes. Rebuildable; not the source of truth.

This is mostly what existing Runa state uses; the convention should be maintained.

**Concurrency and locking.**

Multiple subagents writing simultaneously to the same SQLite file is a concurrency concern. SQLite supports it via WAL mode but contention is possible. Mitigation:

- *Single writer per database*: each writing subagent owns a dedicated database; readers are unrestricted.
- *Coordinated writes*: a write-coordinator process serialises critical writes (the kernel for episodes, Draumr for reflections, etc.).
- *Optimistic concurrency for non-critical writes*: retry on conflict.

**Privacy and personal data.**

Runa's state contains *Volmarr's personal data* — his messages, his projects, attributed beliefs. Treat with appropriate care:

- *Local-first*: state lives on Volmarr's machine; doesn't transit cloud without explicit opt-in.
- *Encryption at rest*: optional but recommended for backup snapshots that leave the device.
- *Selective forgetting*: a `runa forget <subject>` command marks specified entries archived-with-reason, excluded from retrieval.

## 3. Key works

- **Date, C. J.** *Database in Depth.* O'Reilly, 2005. Database theory baseline.
- **Petzold, C.** *Code.* MS Press. For file-system fundamentals.
- **Hellerstein, J. et al.** *Architecture of a Database System.* Foundations and Trends in Databases, 2007. Reference.
- **Kleppmann, M.** *Designing Data-Intensive Applications.* O'Reilly, 2017. Modern application data architecture.
- **Fowler, M.** *Event Sourcing.* (Online materials.) See [[22-event-sourcing-cqrs]].
- **SQLite documentation.** WAL mode, backup API, etc.
- **Git internals.** For inspiration on content-addressable storage and version history.
- **Tigerbeetle, FoundationDB design docs.** For ideas about how serious distributed-and-durable systems are built.
- **Packer, C. et al.** *MemGPT.* arXiv:2310.08560, 2023. Treats agent memory as paging.
- **Park, J. S. et al.** *Generative Agents.* arXiv:2304.03442, 2023. Persistent memory stream.

## 4. Empirical results

This is engineering practice rather than research:

- SQLite handles agent-scale workloads (millions of episodes over years) comfortably on consumer hardware.
- Append-only journals are robust to most failures except the underlying disk.
- Snapshot+restore tested in many production systems.
- Failure modes documented across decades of database/file-system engineering.

The specific *AI-agent state* combination is new but doesn't change the engineering fundamentals.

## 5. Applicability to Runa

For **directory structure**:

The recommended structure (refining what bootstrap docs already specify):

```
runa/
├── core/
│   ├── identity/                ← markdown + journal
│   │   ├── persona.md
│   │   ├── values.md
│   │   ├── capabilities.md
│   │   ├── self_summary.md       ← updated by reflection
│   │   └── identity_journal.jsonl
│   ├── relationships/
│   │   ├── volmarr/
│   │   │   ├── relationship.json
│   │   │   ├── values.md
│   │   │   ├── bdi.jsonl
│   │   │   └── corrections.md
│   │   └── ...
│   ├── memory/                  ← Muninn
│   │   ├── episodes.db
│   │   ├── episodes.faiss
│   │   ├── triplets.db
│   │   ├── reflections.db
│   │   └── relations.yaml
│   └── saga/
│       ├── weekly/
│       │   ├── 2026-W20.md
│       │   └── ...
│       └── annual/
├── state/                       ← runtime
│   ├── scheduler.sqlite
│   ├── eldhugi_state.json
│   └── cache/
├── config/
│   ├── runa.yaml
│   ├── schedules.yaml
│   ├── models.yaml
│   └── ...
├── logs/
│   ├── turn_log.jsonl
│   ├── boot_log.jsonl
│   └── debug.log
├── adapters/                    ← model adapters
│   └── runa_identity_lora_v3/
└── snapshots/
    ├── daily/
    └── weekly/
```

For **commands Runa needs**:

- `runa snapshot create [--label X]`
- `runa snapshot list`
- `runa snapshot restore <id>`
- `runa integrity check`
- `runa backup push [--target <name>]`  (push to remote)
- `runa backup pull [--target <name>]`
- `runa forget <subject> [--reason X]`
- `runa export [--scope X]`  (for review or for migration)
- `runa import <snapshot>`

For **scheduled jobs**:

- Daily snapshot at 03:00.
- Weekly integrity check.
- Monthly pruning (apply retention policy).

For **per RULES.AI.md compliance**:

- Cross-platform: yes — SQLite, JSONL, markdown all platform-portable.
- No hard-coded paths: yes — all paths relative to RUNA_ROOT env var.
- Robust: integrity checks, backups, snapshots.
- Modular: each store has its own concern.

For **Volmarr's review and control**:

- Markdown files Volmarr can read in any editor.
- SQLite files queryable via `sqlite3` CLI.
- Logs greppable.
- `runa state inspect <store>` summarises any store.

What to avoid:

- **Deletion as default.** Use archival + forgetting flags. Recovery is easier than reconstitution.
- **Coupling state format to a specific tool.** Markdown + SQLite + JSONL are portable; binary formats need a reason.
- **Skipping backups.** First backup before first production use.
- **Restoring without integrity check.** Verify before going live.
- **Forgetting model-specific assets in backup.** Adapters and embeddings should be included or explicitly excluded with regeneration path.

## 6. Open questions

- **Optimal snapshot cadence.** Daily is fine for most state; high-write Muninn might warrant hourly during heavy days.
- **Off-machine backup architecture.** Local-first; Tailscale-mounted remote; cloud (encrypted). Volmarr's choice.
- **Cross-Runa migration policy.** What carries across in a major upgrade vs. starts fresh.
- **Selective-forgetting semantics.** Marking-archived is clean; *true* forgetting requires not just archive but exclusion from all derived state (semantic triplets, reflections). Open.
- **Version migration of internal schemas.** When sqlite schema changes, *all* prior data must migrate. Migration tooling needs care.

## 7. References (curated)

- Kleppmann (2017), *Designing Data-Intensive Applications.* The modern reference.
- SQLite documentation — WAL mode, backup API.
- Fowler online materials on event sourcing.
- arXiv:2310.08560 — MemGPT.
- Companion docs: [[01-memgpt-os-memory-hierarchies]], [[22-event-sourcing-cqrs]], [[52-cross-session-persistent-identity]], [[62-identity-stability-under-change]], [[91-ai-os-architecture]], [[95-capability-based-security]].
