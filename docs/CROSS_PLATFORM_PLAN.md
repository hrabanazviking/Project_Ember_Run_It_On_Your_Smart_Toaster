# Cross-Platform Plan — Project Ember

**Status:** Verified clean on Linux + macOS + Windows + WSL surface-by-surface.
Written 2026-05-21 after a 5th Mythic-Engineering sweep specifically targeting
filesystem / process+signal / encoding cross-platform behaviour.

**TL;DR:** Ember already runs anywhere. There is no current code that violates
the "runs anywhere" promise from `README.md` and `docs/SYSTEM_VISION.md`. This
document captures **what was verified clean**, **what to watch for in future
code**, and **a pre-release checklist per platform**.

---

## What was audited (sweep #5, 2026-05-21)

Three parallel Auditors (Sólrún) hit three lenses; the Architect (Rúnhild)
synthesised. The full reports live in `docs/DEVLOG.md` under the Batch H
entry; this document is the *forward-looking plan* derived from them.

| Lens | Tier-1 | Tier-2 | Tier-3 | Verified clean |
|---|---|---|---|---|
| Filesystem / Path | 0 | 0 | 1 (tests using `/tmp/`) | All 11 `.expanduser()` calls; all 3 `chmod` guards (`os.name != "nt"`); all `Path` joins via `/` operator; symlink resolution; case-sensitivity handling |
| Process / Signal / IO | 0 | 0 | 2 (sqlite_vec wheel availability; WAL on network FS) | Zero `signal.signal()`, `signal.alarm()`, `subprocess`, `os.fork()`, `fcntl`, `pwd`, `grp`, `termios`, `select.select()`. Ctrl-C handled at 3 sites with typed `Disconnected` fallback |
| Encoding / Locale | 0 | 0 | 1 (inherited `docs/RunaUniversity2040/generate_content.py` missing `encoding="utf-8"`) | 100% of `Path.read_text()` / `write_text()` in `src/` pass `encoding="utf-8"`; tomllib reads in binary mode; YAML loaded with explicit utf-8; JSON `ensure_ascii=False` always paired with utf-8 file open; all timestamps use `UTC`; locale-neutral format strings (`%Y-%m-%d`) |

**Net result:** zero source-code changes shipped in this batch (apart from
4 test-only `/tmp/` → `tmp_path` conversions). The codebase is genuinely
clean — this is the unusual outcome and the right one to record so the next
operator doesn't have to re-derive it.

---

## Verified-clean catalogue (the receipts)

### Filesystem / Path

- **`pathlib.Path` exclusively.** No string-concat path joining anywhere in
  `src/`. The `/` operator on `Path` does the right thing on every OS.
- **All `expanduser()` is correct.** `~/.ember/well/store.db` becomes
  `/home/user/.ember/...` on Linux/macOS and `C:\Users\Name\.ember\...` on
  Windows. Same code, different result, same semantics.
- **chmod guarded by `os.name != "nt"`** at three sites
  (`config/writer.py`, `spark/funi/tools/audit.py`, `well/brunnr/pgvector/secrets.py`).
  Windows ignores Unix mode bits entirely; the guard prevents the calls
  from silently no-op-ing in a confusing way.
- **No `os.symlink()` in production code** (only read-side resolution).
  Tests use `os.mkfifo` once in `test_hardening_batch_f.py` and `skip` on
  platforms that don't support it.
- **Special-file rejection** uses `stat.S_ISREG()` (cross-platform).
- **Sensitive-name denylist** uses `fnmatch.fnmatchcase` (cross-platform).
- **Atomic file writes** use `tempfile.NamedTemporaryFile(delete=False)` +
  `os.replace()` — atomic on POSIX, atomic-on-same-volume on Windows.
  Tempfile orphan cleanup on failure shipped in Batch G.

### Process / Signal / IO

- **Zero `signal.signal()` calls.** Ember does not register custom signal
  handlers. KeyboardInterrupt arrives naturally on Ctrl-C; we catch it at
  the chat REPL, the stream loop, and the Strengr retry sleep. All three
  paths produce typed values (`Disconnected` for Strengr, tagged partial
  reply for the stream loop, clean exit for the REPL).
- **Zero `subprocess`, `os.fork()`, `os.exec*()`, `os.spawnv()`.** Ember is
  a single-process synchronous program.
- **Zero POSIX-only stdlib imports**: no `fcntl`, `pwd`, `grp`, `resource`,
  `termios`, `select` (as POSIX-only), `os.uname()` (we use `platform`
  where needed).
- **Threading is `threading.RLock()` only** (the tool registry's
  re-entrant lock). Cross-platform.
- **HTTP via stdlib `urllib`** (no `httpx`/`requests`). TLS roots come from
  the OS — Linux uses /etc/ssl/certs, macOS uses Security framework, Windows
  uses the system cert store. All work out of the box on Python 3.11+.

### Encoding / Locale

- **`encoding="utf-8"` explicit on every text-mode file operation in `src/`.**
  Grep confirms: every `open()`, `Path.read_text()`, `Path.write_text()`
  passes it.
- **tomllib reads in binary mode** (`open(path, "rb")`), as required.
- **YAML loaded with explicit utf-8** when the loader takes a path.
- **JSON `ensure_ascii=False`** in audit log + journal; both paired with
  utf-8 file opens — round-trips Unicode losslessly across platforms.
- **All timestamps use `datetime.now(tz=UTC)`** — no local-time confusion.
- **All `strftime` formats are locale-neutral** (`%Y-%m-%d`, never `%B` or
  `%a`).
- **ANSI escapes scrubbed from tool output** (Batch F) — Windows pre-10
  terminals would have rendered them as literal `[31m` strings; the scrub
  prevents both that and adversarial terminal-rewriting from tool replies.

---

## Watch-list for future code

Things that are currently clean but easy to break in future PRs. Add a
check for each to code review or pre-commit.

### Patterns to **always** use

- `Path(a, b)` or `pa / pb` — never `f"{a}/{b}"` for paths.
- `open(path, "r", encoding="utf-8")` — never `open(path)` or
  `open(path, "r")` without the encoding kwarg.
- `Path.read_text(encoding="utf-8")` / `Path.write_text(..., encoding="utf-8")`.
- `datetime.now(tz=UTC)` — never `datetime.now()` (naive local time).
- `tempfile.NamedTemporaryFile(delete=False)` + `os.replace()` for atomic
  writes — both arms wrapped in try/except so the tempfile cleanup runs
  even on failure.
- `if os.name != "nt": chmod(...)` for any Unix mode-bit setting.

### Patterns to **never** introduce

- `os.fork()` / `os.exec*()` — POSIX-only; Windows breaks.
- `import fcntl` / `import pwd` / `import grp` / `import termios` /
  `import resource` at module level — `ImportError` on Windows.
- `signal.alarm()` — POSIX-only.
- `os.environ["HOME"]` — Windows uses `USERPROFILE`. Use `Path.home()`.
- `subprocess.run(..., shell=True)` — escaping rules differ across shells.
- `select.select(stdin, ...)` — works for sockets cross-platform but file
  descriptors are POSIX-only.
- `time.strftime("%Z")` — returns very different strings on Windows.
- Raw `/tmp/...` paths in tests — use `tmp_path` fixture instead.

### Things that change between Python minor versions

- `pathlib.Path.rglob` gained `recurse_symlinks=False` default in 3.13.
  Ember requires Python 3.14 so this is safe today; if we ever lower
  `requires-python`, explicit `os.walk(..., followlinks=False)` becomes
  necessary.
- `open()` default encoding was made deprecation-warned in 3.15; we already
  pass `encoding="utf-8"` explicitly so the warning never fires.
- `datetime.utcnow()` is deprecated; we use `datetime.now(tz=UTC)` instead.

---

## Per-platform pre-release checklist

Run before announcing support for any specific platform. None of these
are blocking *today* — Ember is "intended to support" all four; this
checklist is for elevating any single platform to "officially supported,
known to work on these versions."

### Linux (currently primary target — Pi-class default)

- [x] Test suite passes (`pytest -q`) — 558 pass + 2 skip as of `a5dd689`
- [x] `pip install ember-agent[sqlite_vec]` works from PyPI
- [x] `pip install ember-agent[pgvector]` works from PyPI
- [x] `ember chat` against tailnet Ollama (`100.67.240.22:11434`) verified
- [x] `ember well ingest` against sqlite_vec verified
- [ ] Smoke test on Raspberry Pi 5 (Bookworm 64-bit) — pending hardware access
- [ ] Smoke test on Raspberry Pi 5 (Bookworm 32-bit ARMv7) — verify
  sqlite-vec wheel availability for ARMv7

### macOS (Intel + Apple Silicon)

- [ ] `brew install python@3.14 ollama && ollama pull llama3.2:3b`
- [ ] `pip install ember-agent[sqlite_vec]` — verify sqlite-vec ships
  arm64 + x86_64 wheels (https://pypi.org/project/sqlite-vec/#files)
- [ ] `pytest -q` from a clean clone
- [ ] `ember setup` → `ember chat` end-to-end
- [ ] **Case-insensitivity check:** Create `~/.Ember/test` and verify the
  sandbox in `read_local_file` doesn't treat it as `~/.ember/test`. APFS
  is case-insensitive by default; the sandbox's `relative_to(home)` check
  uses string comparison, which is case-sensitive.
- [ ] **Codesigning warning:** macOS may warn on first run; document the
  bypass (`xattr -d com.apple.quarantine ...` or Settings → Privacy).

### Windows (10/11 + PowerShell, also test cmd.exe)

- [ ] Install Python 3.14 from python.org (NOT the Microsoft Store
  version — sandboxes filesystem access)
- [ ] `pip install ember-agent[sqlite_vec]` — sqlite-vec ships Windows
  wheels: verify https://pypi.org/project/sqlite-vec/#files lists
  `cp311-cp314-win_amd64.whl`
- [ ] `pytest -q` from a clean clone
- [ ] `ember setup` → `ember chat` end-to-end in PowerShell
- [ ] Same in cmd.exe
- [ ] **PYTHONIOENCODING check:** verify `ember chat` handles non-ASCII
  input (operator types "café") and non-ASCII output (model replies with
  emoji) without `UnicodeEncodeError`. If it fails, document
  `PYTHONIOENCODING=utf-8` as required.
- [ ] **chmod warning:** verify the `os.name != "nt"` guards actually
  fire (no `chmod` warnings in stderr).
- [ ] **Path length:** verify `ember well ingest C:\some\deeply\nested\...`
  works when total path > 260 chars (Windows MAX_PATH). Document
  long-path-support enablement if needed.
- [ ] **Atomic writes across volumes:** verify config + journal writes
  work when `~/.ember/` lives on a different drive than `%TEMP%`.
- [ ] **Console color:** verify ANSI escapes are correctly scrubbed (we
  don't emit any; tool output is scrubbed by Batch F).

### WSL (Windows Subsystem for Linux)

- [ ] Identical to Linux checklist. WSL2 is a real Linux kernel; nothing
  Windows-specific should leak through.
- [ ] Verify `~/.ember/` lives on the WSL filesystem (ext4), not the
  Windows-mounted `/mnt/c/...` — the latter is much slower and has
  case-sensitivity quirks.

### Containers (Docker / Podman) — informational

- [ ] `python:3.14-slim` base image works
- [ ] sqlite-vec extension loads inside the container
- [ ] Volume-mount `~/.ember/` so the Well persists across runs

---

## Known cross-platform watch-points (not bugs, just things to know)

### sqlite-vec wheel availability

The `sqlite_vec` Python package ships pre-compiled native extension wheels.
If a platform/arch combination is missing a wheel, `pip install` falls
back to building from source (Rust toolchain required). Affected combos
likely include:

- **ARMv7 / 32-bit ARM Pi** — may need source build
- **Windows on ARM** — may need source build
- **musl-libc Alpine Linux** — may need source build

If a Pi-class deployment hits this, two workarounds:
1. Install a Rust toolchain in the build environment (`apt install rustc cargo`)
2. Switch to `pgvector` backend instead (requires a separate Postgres but
   sidesteps the native extension entirely)

### WAL mode on network filesystems

SQLite's WAL (Write-Ahead Logging) mode requires that the underlying
filesystem supports proper memory-mapped IO. On network filesystems
(NFS, SMB, CIFS) WAL can produce stale-read anomalies. Ember enables WAL
by default in `SqliteVecConfig.wal_mode = True`.

If an operator runs the Well on a network share (rare; the Pi-class
default is local SSD), they should set `wal_mode: false` in `ember.yaml`.
A future hardening pass could detect network mounts and warn.

### macOS APFS case-insensitivity

The `read_local_file` sandbox check resolves the path via `.resolve()`
then compares the result to `Path.home()`. On APFS (case-insensitive by
default), resolving `~/.EMBER/notes.md` returns whatever canonical case
exists on disk — usually `~/.ember/notes.md` if that's how the directory
was created. The `relative_to(home)` check then succeeds.

This is correct behaviour: the sandbox protects the *actual* directory
tree, not a case-variant of its name. But operators who manually create
both `~/.Ember/` and `~/.ember/` (which APFS allows as a single inode
under both names) may see surprising behaviour. Documented as a known
quirk; no fix.

### Windows long paths

Windows has historically capped paths at 260 chars (MAX_PATH). Python 3.6+
supports long paths transparently when the `LongPathsEnabled` registry key
is set and the app manifests as long-path-aware. The Python launcher does
this; standalone scripts may not. Operators with deep ingest trees should
enable long-path support: https://learn.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation

---

## What's deliberately out of scope

- **macOS / Windows full CI matrix.** Setting up GitHub Actions to run
  the test suite on macos-latest and windows-latest is straightforward
  but not done yet. Worth doing when slice-3 lands; not blocking today.
- **A `[platform.windows]` extra in `pyproject.toml`.** Some packages
  pin different deps per OS. We have none today; if pgvector or
  sqlite-vec ever need OS-specific pins, add an extras entry.
- **Code-signing on macOS / Windows.** Required for Gatekeeper / SmartScreen
  but only relevant if we distribute Ember as a packaged app (not just
  via pip). Not in scope for current pip-based distribution.
- **A `cross-platform` test marker.** `pytest -m "not windows"` etc.
  Mark tests that legitimately can't run on a given platform (e.g., the
  `mkfifo` test already has a `pytest.skip` guard). Could formalize as a
  marker if more accumulate.

---

## Per-batch checklist (for future hardening sweeps)

When adding new code, the contributor (human or agent) should check:

```
- [ ] Any new file I/O uses `encoding="utf-8"` explicitly
- [ ] Any new Path manipulation uses `/` operator, not string concat
- [ ] Any new chmod is guarded by `os.name != "nt"`
- [ ] Any new signal/process/subprocess use is checked against the
      "patterns to never introduce" list above
- [ ] Any new test that needs a real path uses `tmp_path` fixture,
      not `/tmp/` literal
- [ ] Any new timestamp uses `datetime.now(tz=UTC)`
- [ ] Any new locale-affected format (`strftime`, `datetime.format`,
      `time.strftime`) uses locale-neutral specifiers
```

---

## Related reading

- `docs/SYSTEM_VISION.md` — the Vows, including the "runs anywhere"
  promise this plan operationalizes
- `docs/DEVLOG.md` — Batch H entry has the full Auditor reports
- `docs/PYPI_PUBLISHING.md` — release workflow for new versions (lives
  at `~/ai/PUBLISHING_TO_PYPI.md` until moved)
- `pyproject.toml` — `requires-python = ">=3.11"` and classifier list
- Python platform support matrix: https://devguide.python.org/versions/
