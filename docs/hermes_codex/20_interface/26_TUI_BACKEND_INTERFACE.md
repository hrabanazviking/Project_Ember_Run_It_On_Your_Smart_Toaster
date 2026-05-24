---
codex_id: 26_TUI_BACKEND_INTERFACE
title: TUI Backend Interface — Process Lifecycle, IO Order, Leak Surfaces
role: Auditor
layer: Interface
status: draft
hermes_source_refs:
  - tui_gateway/entry.py:1-251
  - tui_gateway/transport.py:1-220
  - tui_gateway/server.py:1-200
  - agent/process_bootstrap.py:1-167
  - tui_gateway/entry.py:65-134
  - SECURITY.md:188-191
ember_subsystem_targets: [Munnr, Funi]
cross_refs:
  - 10_domain/16_TUI_GATEWAY_BACKENDS
  - 30_execution/39_INTERRUPT_MULTILINE_TUI
  - 50_verification/53_CRASH_PROOFING_PATTERNS
  - 50_verification/55_INVARIANT_LIST
---

# TUI Backend Interface — From a Verification Perspective

*Sólrún, examining a process: a terminal backend is a contract between a parent process and a child subprocess about who owns the keyboard, the screen, the stdout pipe, and the next-to-die-on-signal trophy. Most of the bugs are in the gap between what each thinks the other should handle. I will find that gap.*

The brief asks about "terminal backend contract from a verification perspective." There are two surfaces in Hermes that carry that name, and I will treat both:

1. **The TUI gateway** — the JSON-RPC server in `tui_gateway/` that backs the Ink-rendered terminal UI. The child process; the agent runs here.
2. **Tool terminal backends** — the pluggable execution targets for the `terminal()` tool, per `SECURITY.md:64-77` (Docker, SSH, Modal, Daytona, Singularity, Vercel Sandbox).

Both are "terminal" backends; both have process-lifecycle contracts; the second carries the OS-level isolation boundary that Hermes treats as the only real security boundary. I will name what is fragile in each.

## 1. The TUI gateway: JSON-RPC over stdio

`tui_gateway/entry.py:187-247` is the gateway main loop:

```python
def main():
    _install_sidecar_publisher()
    # ...MCP discovery guarded by config...
    if not write_json({
        "jsonrpc": "2.0",
        "method": "event",
        "params": {"type": "gateway.ready", "payload": {"skin": resolve_skin()}},
    }):
        _log_exit("startup write failed (broken stdout pipe before first event)")
        sys.exit(0)

    for raw in sys.stdin:
        line = raw.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            if not write_json({"jsonrpc": "2.0", "error": ...}):
                _log_exit("parse-error-response write failed (broken stdout pipe)")
                sys.exit(0)
            continue
        method = req.get("method") if isinstance(req, dict) else None
        resp = dispatch(req)
        if resp is not None:
            if not write_json(resp):
                _log_exit(f"response write failed for method={method!r} (broken stdout pipe)")
                sys.exit(0)
```

The shape: one JSON-RPC frame per line on stdin → dispatch → one JSON-RPC frame per line on stdout. Simple to read, treacherous in detail.

### 1.1 Process-lifecycle invariants

The lifecycle has explicit invariants documented in code comments. Worth quoting:

```python
# tui_gateway/entry.py:65-83
def _log_signal(signum: int, frame) -> None:
    """Capture WHICH thread and WHERE a termination signal hit us.

    SIG_DFL for SIGPIPE kills the process silently the instant any
    background thread (TTS playback, beep, voice status emitter, etc.)
    writes to a stdout the TUI has stopped reading.  Without this
    handler the gateway-exited banner in the TUI has no trace — the
    crash log never sees a Python exception because the kernel reaps
    the process before the interpreter runs anything.
    """
```

The invariants Hermes maintains, in audit form:

| # | Invariant | Where enforced | Failure if violated |
|---|---|---|---|
| TUI-1 | SIGPIPE is ignored, not defaulted. | `tui_gateway/entry.py:151-152` | A background thread writing to a closed pipe kills the gateway silently. |
| TUI-2 | SIGTERM/SIGHUP/SIGBREAK are logged with full thread stacks. | `tui_gateway/entry.py:88-110` | "Gateway exited" with no forensic trail. |
| TUI-3 | SIGINT is ignored (Ctrl-C goes to the TUI Ink parent). | `tui_gateway/entry.py:161-162` | Double-interrupt confusion: Ink and gateway both die. |
| TUI-4 | Shutdown has a configurable grace window (default 1s), then `os._exit(0)`. | `tui_gateway/entry.py:51-62`, `:113-123` | A wedged worker holding `_stdout_lock` deadlocks the interpreter. |
| TUI-5 | Stdout writes are serialized through a single lock. | `tui_gateway/transport.py:108-180` | Interleaved JSON frames; protocol break. |
| TUI-6 | Stdout writes are JSON-serialized *outside* the lock. | `tui_gateway/transport.py:133-137` | A large payload blocks every other emitter while serializing. |
| TUI-7 | A `BrokenPipeError` on write returns `False`, not raise. | `tui_gateway/transport.py:140-158` | The dispatcher's clean-disconnect signal is corrupted by exceptions. |
| TUI-8 | `EPIPE/ECONNRESET/EBADF/ESHUTDOWN` are peer-gone; other OSError errnos re-raise. | `tui_gateway/transport.py:36-43`, `:154-158` | Real bugs (ENOSPC, EACCES) get hidden as "clean disconnect." |
| TUI-9 | Each exit path logs *why* with a string reason to `_CRASH_LOG`. | `tui_gateway/entry.py:165-184` | "Gateway exited" with no actionable clue. |
| TUI-10 | Stdio is wrapped by `_SafeWriter`, which swallows OSError/ValueError. | `agent/process_bootstrap.py:63-110` | Broken-pipe errors crash agent setup; double-fault when except handlers also print. |

That's a serious amount of operational engineering invisibly absorbing edge cases. Whoever wrote `tui_gateway/entry.py` has lost a process to each of these.

### 1.2 IO ordering guarantees

The shape on the wire: one JSON object per line. Hermes guarantees:

1. Frames are atomic at the line level (`json.dumps` then write under a lock — `tui_gateway/transport.py:137-141`).
2. The "primary" transport's success determines the result; secondaries are best-effort (`tui_gateway/transport.py:201-210`).
3. Order within a request is not declared. A `dispatch(req)` may emit *events* before returning a *response*; the consumer must distinguish `method` (event) from `id` (response).

What is **not** guaranteed:

- Order *across* requests. Two concurrent requests dispatched to the worker pool can interleave their events on stdout. The Ink TUI must reassemble.
- Bounded buffering. If the consumer stops reading, the gateway's stdout buffer fills, then writes block; the daemon-timer + `os._exit` is the fallback (`tui_gateway/entry.py:113-123`).
- Deterministic shutdown. Within the grace window the gateway tries to drain; after, it hard-exits.

For Ember, the takeaway: a JSON-RPC-over-stdio contract is implementable in 600 lines of Python — but the *crash-proofing* is 50% of those lines. Stripping the crash-proofing is the rookie mistake.

### 1.3 The transport abstraction

`tui_gateway/transport.py:67-75` defines a Transport protocol:

```python
@runtime_checkable
class Transport(Protocol):
    def write(self, obj: dict) -> bool:
        """Emit one JSON frame. Return ``False`` when the peer is gone."""
    def close(self) -> None:
        """Release any resources owned by this transport."""
```

Two implementations: `StdioTransport` and `TeeTransport`. A `TeeTransport` mirrors writes to one primary + N secondaries, with secondaries swallowing exceptions:

```python
# tui_gateway/transport.py:201-210
def write(self, obj: dict) -> bool:
    # Primary first so a slow sidecar (WS publisher) never delays Ink/stdio.
    ok = self._primary.write(obj)
    for sec in self._secondaries:
        try:
            sec.write(obj)
        except Exception:
            pass
    return ok
```

This is a clean little abstraction. It is also the entire reason a sidecar WebSocket publisher (`tui_gateway/event_publisher.py`) can mirror gateway events to a dashboard without ever blocking the Ink TUI. The pattern is worth keeping.

### 1.4 What can leak between sessions

`tui_gateway` runs one process per TUI launch. There is no per-session isolation inside the process — slash commands, MCP discovery, plugin loads, and the agent state are all shared. Specifically:

- The MCP discovery side-effect runs at startup (`tui_gateway/entry.py:204-217`). MCP servers spawned by the gateway are subprocesses; their stdout/stderr are routed to the agent. A subprocess that survives a `/new` or `/reset` keeps its environment, its credentials, and its open file descriptors.
- Memory providers are initialized at startup. `MemoryManager.on_session_switch` (`agent/memory_manager.py:457-490`) is the *only* signal a provider gets that the conversation has rotated. A provider that ignores it (or one of the "default no-op" hooks from `MemoryProvider.on_session_switch`, `agent/memory_provider.py:163-200`) keeps writing to the old session.
- Hook handlers loaded from `~/.hermes/hooks/<name>/handler.py` are imported once (`gateway/hooks.py:115-122`). Module-level state survives `/reset`. A hook that caches a credential at import time keeps it forever.

For Ember, this is a known antipattern: process-wide singleton state that survives session boundary. See [[50_verification/52_ANTIPATTERN_CATALOG]] entry "module-singleton-across-sessions."

## 2. The tool terminal backends — the *real* security boundary

`SECURITY.md:64-77` names the pluggable execution targets for the `terminal()` tool. The default backend runs commands directly on the host. Other backends — Docker, SSH, Modal, Daytona, Singularity, Vercel Sandbox — run commands inside a sandbox.

The contract is OS-level. The boundary is enforced by the kernel / hypervisor / sandbox runtime, not by Python.

### 2.1 What the contract says

The brief from `SECURITY.md:71-77`:

> "What this confines: anything the agent does by issuing shell or file operations. What this does **not** confine: everything the agent does in its own Python process. That includes the code-execution tool (spawned as a host subprocess), MCP subprocesses (spawned from the agent's environment), plugin loading, hook dispatch, and skill loading (all imported into the agent interpreter)."

That is the most honest scope statement I have seen on an LLM project's security policy. It also names the failure mode: an operator who chose terminal-backend isolation, then ran an MCP server in the host process, has chosen a posture that does not contain the MCP server.

### 2.2 The verification stance Hermes takes

The posture options (`SECURITY.md:69-119`):

- **Terminal-backend isolation** — confines shell + file tools. Does not confine MCP, plugins, hooks, skills, code-execution tool.
- **Whole-process wrapping** — confines everything. Hermes supports this via its own Docker setup or via NVIDIA OpenShell.

`SECURITY.md:106-114` is explicit: "Hermes Agent's in-process heuristics function as accident-prevention layered on top of a real boundary. This is the supported posture when the agent ingests content from surfaces the operator does not control..."

This is the right shape. The Approval Gate, the redactor, the Skills Guard, and the file-safety denylist are **heuristics**. They are not boundaries. A reporter who bypasses them is welcomed to file a bug, not a vulnerability. The boundary is the OS.

### 2.3 The shape of process spawn

For each terminal backend, the contract that matters is:

1. **Identity**: which user account runs the subprocess?
2. **Filesystem scope**: what paths can the subprocess read/write?
3. **Network scope**: what destinations can the subprocess reach?
4. **Credential scope**: what env vars are exposed?
5. **Lifecycle**: who reaps the subprocess on agent crash? On user interrupt?
6. **Stdio capture**: how does the subprocess's stdout/stderr return to the agent?
7. **Quota**: CPU / memory / disk / time limits?

Hermes's credential scoping (`SECURITY.md:121-134`) addresses #4: provider API keys and gateway tokens are stripped from the env passed to shell / MCP / code-execution children. Skills can declare additional pass-through env vars. This is the right *scope* shape: deny-by-default, declared-pass.

The other six concerns are platform-specific. Each backend implementation (Docker, SSH, Modal, etc.) must answer them.

### 2.4 Failure modes specific to the spawn surface

- **Orphaned subprocesses**: the agent crashes mid-spawn; the child survives. Docker: the container keeps running. SSH: the remote command keeps running. Modal: the function keeps consuming budget. *Audit: Hermes has lifecycle-management for some backends but not all; this surfaces in tests like `tests/test_atomic_replace_symlinks.py` and the absent-handler pattern in `tests/agent/test_curator_backup.py`.*
- **Credential leak via subprocess argv**: a tool that puts a token on the command line is visible to anyone with `ps`. Hermes's `agent/redact.py` redacts logs but cannot scrub argv from `/proc/<pid>/cmdline`. *Audit: a stance, but enforcement is via reviewer eye, not code.*
- **PATH injection**: a sandbox that inherits PATH from the agent can shadow real binaries. *Audit: documented in Hermes's container Dockerfile (sets PATH explicitly); not documented as a general rule.*

## 3. The contracts together

For Ember's purposes, the TUI gateway and the terminal backends are two interfaces with one shared trait: **they are the boundaries between processes, and process boundaries leak**.

The lessons:

1. **Every process boundary needs lifecycle ownership.** Who spawns? Who reaps? Who notices when the child dies? Hermes answers these explicitly for the TUI gateway via signal handlers and grace windows; answers them per-backend for terminal tools.
2. **Stdio is the most common protocol because it always works.** And the most fragile because half-closed pipes are subtle. The `BrokenPipeError`-returns-False shape, the daemon-timer shutdown, the lock-outside-serialization split — these are the patterns Ember should keep if she ever subprocesses anything.
3. **Heuristics inside the process do not contain the process.** Approval gates, redactors, sandboxes implemented in Python — all useful, none containers. The container is the kernel.
4. **Signal handling is not optional on Linux.** Default SIGPIPE behavior kills the process silently. Hermes ignores SIGPIPE and lets the write surface return `False`. Ember should do the same in any future subprocess scenario.
5. **Process state survives session rotation.** MCP servers, hook modules, plugin singletons — none of them automatically reset when the user runs `/new`. Hermes documents this; Ember should design for it.

## 4. What Ember can learn from `_SafeWriter`

`agent/process_bootstrap.py:63-110` is a 40-line wrapper that has earned its keep. It wraps stdout/stderr so that *any* write that hits a broken pipe returns its byte count rather than raising. The docstring (`agent/process_bootstrap.py:63-80`) explains: when hermes runs as a systemd service, a Docker container, or a thread-pool worker, the stdout pipe can disappear unpredictably. Any `print()` call would then crash a tangentially related operation.

The pattern is:

```python
class _SafeWriter:
    __slots__ = ("_inner",)
    def write(self, data):
        try:
            return self._inner.write(data)
        except (OSError, ValueError):
            return len(data) if isinstance(data, str) else 0
    def flush(self):
        try:
            self._inner.flush()
        except (OSError, ValueError):
            pass
    def fileno(self):
        return self._inner.fileno()
    def isatty(self):
        try:
            return self._inner.isatty()
        except (OSError, ValueError):
            return False
    def __getattr__(self, name):
        return getattr(self._inner, name)
```

For Ember running on a Pi over SSH or systemd, this is a directly portable pattern. Munnr should consider it for the day someone runs `ember chat | tee log` and the tee dies mid-stream.

## 5. The TUI's "interrupt without loss" pattern

Per Hermes's documentation and slice notes, the TUI supports Ctrl-C without losing the current input buffer. The Ember slice-2 streaming path already implements *partial reply persistence on Ctrl-C* (per SLICE_2_RETROSPECTIVE §"Vow of Honest Memory") — the `[interrupted by operator]` tag is exactly the right shape.

Hermes adds a layer: the input buffer survives the interrupt because the TUI (the Ink parent) owns the input state, and the gateway (the child) handles the signal differently. Munnr is in-process and does not have this split. If Ember ever grows a Bifröst-style frontend separation, the lesson is: **input state is owned by the surface; tool state is owned by the agent; the boundary is JSON-RPC** (or equivalent). See [[30_execution/39_INTERRUPT_MULTILINE_TUI]].

## What This Means for Ember

**Subsystems affected:** Munnr (CLI/surface), Funi (subprocess Ollama child if ever swapped for llama.cpp inline).

**Vows touched:**

- **Vow of Modular Authorship** — process-boundary failures must be isolated.
- **Vow of Public-Friendliness** — the operator must always know *why* something exited (Hermes's `_log_exit` pattern).
- **Vow of Graceful Offline** — when a subprocess (Ollama, future MCP, future plugin) dies, Munnr must report it, not pretend nothing happened.

**Concrete proposals:**

1. **Adopt `_SafeWriter` for Munnr.** Direct port from `agent/process_bootstrap.py:63-110`. Two-week task; one-file change.
2. **Adopt the SIGPIPE-ignore pattern** if Ember ever runs as a systemd unit. `signal.signal(signal.SIGPIPE, signal.SIG_IGN)`. Then surface broken-pipe via typed return values.
3. **Adopt the `_log_exit` pattern.** Every clean exit path writes a one-line reason to a known location. The operator sees `ember chat: exit reason=stdin EOF` instead of nothing.
4. **Design for JSON-RPC-over-stdio if Bifröst becomes a subprocess.** Pre-decide: one JSON object per line, line-atomic writes under a lock, serialize outside the lock, peer-gone errnos enumerated.
5. **No per-delta regex over LLM output without a streaming state machine.** Direct lesson from `agent/memory_manager.py:62-224` and `agent/think_scrubber.py` — Hermes had a leak. Ember's streaming Funi path already handles this via its tool-call accumulation; the principle generalizes.
6. **Treat MCP servers (if/when supported) as live subprocesses with their own lifecycle.** Reap on agent exit; log on unexpected death; refuse to inherit credentials by default.
7. **Document Ember's "stance" on process boundaries.** Explicitly: which process owns which state, who reaps whom, how identity propagates.
8. **For terminal sandboxing (if ever added): match `SECURITY.md`'s scope statement verbatim.** Name what is and isn't confined. Do not let a posture statement be implied.

Cross-link with [[50_verification/53_CRASH_PROOFING_PATTERNS]] for the consolidated set, and [[30_execution/39_INTERRUPT_MULTILINE_TUI]] for the Forge's view of the input-side mechanics.

The interface between processes is the interface where errors hide. Hermes has paid for every comment in `tui_gateway/entry.py`. Ember should pay attention to those comments before paying their cost herself.
