# 11 — Crash-Only Software Design

**Category:** Self-Healing & Supervision
**Runa relevance:** services architecture, kernel restart semantics, state-store recovery
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

**Crash-only software** (Candea and Fox, HotOS 2003) is a design philosophy: build systems whose *only* stop mode is to crash, and whose *only* start mode is recovery from a crash. There is no separate "shutdown" path that might leave inconsistent state; no separate "graceful shutdown" code that's tested less than the main path; no distinction between "scheduled restart" and "unexpected restart." Every restart looks the same to the system: come up, find the state on disk, reconcile, run.

The philosophy is liberating. A system that *only* knows how to crash and recover has spent all its engineering effort on the recovery path — and recovery is what determines whether the system survives the *next* unexpected event. Erlang's "let it crash" famously embodies this; so do many database engines (PostgreSQL, SQLite, LMDB) and modern container orchestration (Kubernetes treats process death as the normal lifecycle event).

For Runa, the discipline matters because Runa is long-lived on a Pi 5 that *will* have power glitches, kernel oops, OOMs, runtime upgrades, and operator-induced restarts. The agent that designs for "graceful shutdown" as a special case will fail in the inevitable not-so-graceful case. The agent designed crash-only handles all cases identically.

## 2. Technique / mechanism

**The principles:**

1. **Atomic state transitions.** All persistent state changes are atomic — either fully committed or not visible at all. SQLite transactions, atomic file writes (`os.replace` after write to temp), append-only logs.
2. **Idempotent recovery.** Starting from disk state, reconcile to a running state. Running recovery multiple times produces the same result.
3. **No shutdown-only code.** Anything you do at shutdown must work the same way after a crash. No "make sure to call cleanup()" — the system survives without it.
4. **Fast startup.** Recovery is the *normal* startup path; it should be fast. (PostgreSQL famously slow on recovery; modern systems like RocksDB and LMDB much faster.)
5. **Externalised supervision.** A separate process / system supervises and restarts. The supervised process doesn't decide its own lifecycle.

**Python-specific patterns:**

### Atomic file writes

```python
import os
import tempfile
from pathlib import Path

def atomic_write_text(path: Path, content: str) -> None:
    """Write content to path atomically. On crash, path is either old or new, never partial."""
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())  # ensure data hits disk
        os.replace(tmp_path, path)  # atomic on POSIX, near-atomic on Windows
    except:
        os.unlink(tmp_path)
        raise
```

`os.fsync` forces data through OS buffers to the disk; `os.replace` is atomic at filesystem level.

### Write-ahead log (WAL)

```python
class WriteAheadLog:
    """Append-only log of intent. Survives crashes."""
    
    def __init__(self, path: Path):
        self.path = path
        self._file = open(path, "ab")  # append, binary
    
    def append(self, entry: bytes) -> None:
        # length-prefix each entry so partial writes are recognisable
        self._file.write(len(entry).to_bytes(4, "big"))
        self._file.write(entry)
        self._file.flush()
        os.fsync(self._file.fileno())
    
    def replay(self) -> Iterator[bytes]:
        with open(self.path, "rb") as f:
            while True:
                length_bytes = f.read(4)
                if len(length_bytes) < 4:
                    return  # EOF or partial
                length = int.from_bytes(length_bytes, "big")
                entry = f.read(length)
                if len(entry) < length:
                    return  # partial write — discard
                yield entry
```

On startup, replay the WAL. Apply each entry idempotently to recover state.

### SQLite WAL mode

SQLite has built-in WAL mode (`PRAGMA journal_mode=WAL`) that gives ACID transactions even across crashes. Use it for state stores:

```python
import sqlite3

conn = sqlite3.connect("muninn.sqlite")
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA synchronous=NORMAL")  # FULL is safer, NORMAL faster
```

After a crash, the next process to open the database performs recovery automatically.

### State machine with persisted state

```python
@dataclass
class TaskState:
    task_id: UUID
    status: str  # "queued" | "in_progress" | "completed" | "failed"
    started_at: datetime | None
    ...

class TaskLedger:
    """Persistent task state. Restart-safe."""
    
    def on_startup(self):
        """Recover from disk. Idempotent."""
        with self.db.transaction():
            in_progress = self.db.select_tasks_with_status("in_progress")
            for task in in_progress:
                # Recover: mark interrupted, decide what to do
                self.db.update_task(task.task_id, status="interrupted")
                # The scheduler will decide whether to resume or abandon
```

The startup logic *is* the recovery logic. No separate "first run" vs "restart" path.

### No mandatory cleanup

```python
# BAD: relies on cleanup running
class Service:
    def __init__(self):
        self.tmpfile = tempfile.NamedTemporaryFile()
    
    def shutdown(self):
        self.tmpfile.close()  # what if we crash before shutdown?

# GOOD: no cleanup needed
class Service:
    def __init__(self):
        self.tmpdir = Path(tempfile.gettempdir()) / "service"
        self.tmpdir.mkdir(exist_ok=True)
    
    def on_startup(self):
        # On startup, clean up old tmp files (anything we left behind from a crash)
        for old in self.tmpdir.glob("*.tmp"):
            if (time.time() - old.stat().st_mtime) > 3600:
                old.unlink()
```

Cleanup happens on the next startup, not before shutdown.

### Externalised supervision

systemd, Docker, Kubernetes, supervisord — these are the "outer" supervisors that restart processes on crash. Build for them:

- Process exits non-zero on unrecoverable failure.
- Process honours SIGTERM (best-effort graceful shutdown but not relied on; see [[49-graceful-shutdown]]).
- Process startup completes quickly to satisfy health-check probes.
- Process is stateless in memory — all persistent state on disk.

### Multiple processes, each crash-safe

The agent's overall design (kernel + services + adapters in different processes — per ARCHITECTURE.md §4.4) means each process is independently crash-safe. A crashed adapter restarts; the kernel doesn't notice (or notices via the supervisor's `Crashed` event and adjusts).

## 3. Key works / libraries

- **Candea, G. and Fox, A.** "Crash-Only Software." HotOS 2003 (USENIX). The foundational paper.
- **Armstrong, J.** *Programming Erlang.* Pragmatic Bookshelf, 2007. Erlang's "let it crash" philosophy.
- **PostgreSQL WAL** — postgresql.org/docs/current/wal-intro.html. Mature WAL implementation; instructive.
- **SQLite WAL mode** — sqlite.org/wal.html.
- **LMDB** (Lightning Memory-Mapped Database) — copy-on-write design that's inherently crash-safe.
- **Kubernetes liveness probes** — model where the supervisor restarts dead/sick pods.
- **systemd `Restart=on-failure`** — the OS-level supervision standard.
- **supervisord** — Python-friendly process supervisor.

## 4. Pitfalls and gotchas

- **`os.replace` not atomic on Windows** for cross-volume moves. Same-volume usually atomic; sanity check on Windows targets.
- **`fsync` is slow.** Trade-off between durability and throughput. `synchronous=NORMAL` in SQLite, careful `fsync` placement in WAL implementations.
- **Filesystems lie.** Some filesystems delay fsync. ext4 default is mostly trustworthy; some others less so. Test in your target environment.
- **OOM-killer doesn't run cleanup.** The kernel kills the process with `kill -9`; Python doesn't get to run `atexit` handlers. Don't depend on them for correctness.
- **`atexit` doesn't run on segfault, SIGKILL, or power loss.** Design assuming it sometimes doesn't run.
- **In-memory caches need invalidation on restart.** Don't rely on a long-lived process's accumulated cache; it's gone on restart.
- **State that's "always" in-memory** during normal operation often turns out to need on-disk backing. Discover this during development, not in production.
- **Recovery time too long.** A 5-minute recovery during normal restart is annoying; during operator firefight it's painful. Optimise recovery.

## 5. Applicability to Runa

For **`runa.runtime` (process supervision)**:

- The runtime is the crash-only supervisor for the kernel and services. systemd is the supervisor for the runtime itself.
- All Runa services exit non-zero on unrecoverable error; the supervisor restarts.
- No "graceful shutdown only" code paths.

For **Muninn (memory store)**:

- SQLite WAL mode. Atomic transactions for all multi-statement writes.
- On startup: open Muninn, automatic SQLite recovery, integrity check, ready.
- Re-embedding migrations are checkpointed so a crashed migration resumes where it left off.

For **Skuld (task ledger)**:

- Append-only event log + projection (per [[22-event-sourcing-cqrs]] in research corpus).
- Tasks in `in_progress` at startup are marked `interrupted` and the resume policy ([[16-state-machines-reliability]]) decides per-task.

For **Eldhugi (emotional journal)**:

- Append-only journal file. Latest N entries loaded at startup.

For **audit log** ([[40-audit-logging-replay]] in research):

- Append-only JSONL files. No special "rotation" code at shutdown; rotation happens on first write of a new day, idempotently.

For **kernel turn state**:

- All turn state held only for the duration of the turn. No accumulated state across turns that isn't in Muninn / Skuld / Eldhugi.
- A turn interrupted by crash is *lost* — the user's input becomes a `Heard` that was never processed. The audit log records it; the kernel on restart can decide to retry (if Volmarr is still on the line) or treat as historical.

For **services restart semantics**:

- gateway, worker, voice, gui each exit non-zero on unrecoverable error.
- systemd restarts with backoff.
- Service startup is fast: <2 seconds to "accepting traffic" on Pi 5.

For **operator visibility**:

- `runa doctor` reports last restart time and reason. Frequent restarts trigger `Notified`.

What to avoid:

- Don't rely on `atexit`, `__del__`, or `finally` for correctness. They're best-effort.
- Don't write graceful-shutdown code that's the *only* path to a consistent state. Crash-only means *every* termination path is OK.
- Don't accumulate in-memory state that you can't reconstruct. If it's important, persist.
- Don't make recovery slow. Slow recovery = bad UX on every restart.

## 6. Open questions

- **Recovery time vs durability.** `fsync` everywhere is slow; `fsync` rarely loses data on crash. The right balance is workload-specific.
- **Crash-only at the agent level.** Should Runa-the-agent (not just processes) embrace "crash-only" — periodically restart kernel to clear accumulated state? Erlang-style heart-beat patterns are appealing.
- **Out-of-process LLM state.** When Runa's downstream services (Ollama, MCP servers) crash, Runa's recovery story for them is partial. The cluster-of-supervisors pattern composes; gets complex.

## 7. References (curated)

- usenix.org/conference/hotos-ix/crash-only-software — Candea and Fox paper.
- sqlite.org/wal.html — SQLite WAL documentation.
- postgresql.org/docs/current/wal-intro.html — PostgreSQL WAL.
- erlang.org/doc/design_principles/sup_princ.html — Erlang supervision.
- joeduffyblog.com/2016/02/07/the-error-model/ — Joe Duffy's essay on error models, including crash-only thinking.
- Companion docs: [[05-idempotency-design]], [[12-supervisor-trees]], [[16-state-machines-reliability]], [[49-graceful-shutdown]].
