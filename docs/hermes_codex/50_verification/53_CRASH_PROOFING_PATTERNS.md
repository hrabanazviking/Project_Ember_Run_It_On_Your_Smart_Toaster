---
codex_id: 53_CRASH_PROOFING_PATTERNS
title: Crash-Proofing Patterns — What to Lift From Hermes
role: Auditor
layer: Verification
status: draft
hermes_source_refs:
  - agent/process_bootstrap.py:63-167
  - tui_gateway/entry.py:65-247
  - tui_gateway/transport.py:1-220
  - agent/memory_manager.py:62-224
  - agent/tool_guardrails.py:1-475
  - agent/iteration_budget.py:1-62
  - agent/curator_backup.py:1-100
  - agent/error_classifier.py:1-90
  - agent/retry_utils.py
  - hermes_cli/plugins.py:88-122
  - tui_gateway/entry.py:113-123
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
cross_refs:
  - 50_verification/50_HERMES_RISK_REGISTER
  - 50_verification/55_INVARIANT_LIST
  - 50_verification/56_TESTING_STRATEGY
  - 60_synthesis/63_INTEGRATION_PATHS
---

# Crash-Proofing Patterns

*Sólrún, eyes narrowing on the good shelf: among the patterns Hermes overuses are patterns Hermes earned the hard way. The signal handlers in `tui_gateway/entry.py` are not idle ceremony; each one represents a process that died silently in production. The streaming scrubber represents memory that leaked. The iteration budget represents a turn that cost real money. The lessons are paid for. Ember can lift them at a fraction of the price.*

For each pattern I cite (a) the Hermes location, (b) what it survives, (c) the cost to lift into Ember, and (d) the cross-walk with Ember's existing `docs/python/` reliability docs.

---

## P-01 — `_SafeWriter`: stdout/stderr wrapper that swallows broken-pipe errors

**Where in Hermes:** `agent/process_bootstrap.py:63-110`.

**What it survives:**
- `OSError: [Errno 5] Input/output error` from systemd-detached or Docker-detached stdio.
- `ValueError: I/O operation on closed file` from thread-teardown races.
- `BrokenPipeError` from a parent that closed the pipe.
- Double-fault: an `except` handler calling `print()` after the pipe is dead.

**The shape:**

```python
class _SafeWriter:
    __slots__ = ("_inner",)

    def __init__(self, inner):
        object.__setattr__(self, "_inner", inner)

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

**Cost to lift:** Trivial. ~40 LOC. One install function (`_install_safe_stdio`) called once at process start.

**Cross-walk with Ember docs:** `docs/python/10-graceful-degradation.md` — `_SafeWriter` is the graceful-degradation pattern applied at the stdio boundary.

**Verdict:** **Lift verbatim.** Apply when Ember runs as systemd, Docker, or any backgrounded environment. Slice-3 candidate when an `ember chat | tee` use case surfaces.

---

## P-02 — SIGPIPE-ignore + signal-logging + grace window + os._exit fallback

**Where in Hermes:** `tui_gateway/entry.py:65-162`.

**What it survives:**
- Background-thread writes after the TUI parent stops reading.
- Termination signals delivered to the wrong thread.
- Wedged worker threads holding `_stdout_lock` past `sys.exit()`.

**The shape (key fragments):**

```python
# Ignore SIGPIPE: surface broken-pipe via write returning False, not via process death.
if hasattr(signal, "SIGPIPE"):
    signal.signal(signal.SIGPIPE, signal.SIG_IGN)

# Log every termination signal with full thread stacks BEFORE exiting.
def _log_signal(signum: int, frame) -> None:
    # ... write current frame + every active thread's stack to _CRASH_LOG
    ...
    # Daemon timer: if interpreter doesn't unwind in N seconds, os._exit.
    timer = _threading.Timer(_shutdown_grace_seconds(), lambda: os._exit(0))
    timer.daemon = True
    timer.start()
    sys.exit(0)
```

**Cost to lift:** Moderate. ~150 LOC. Worth scaling to context: Munnr is foreground-interactive and doesn't need this. Bifröst (if it becomes a subprocess or systemd unit) does.

**Cross-walk:** `docs/python/13-watchdog-timers.md` (the daemon timer is a watchdog), `docs/python/11-crash-only-software.md` (os._exit is the crash-only fallback).

**Verdict:** **Lift when Ember has a long-running subprocess.** Until then, file under "patterns we'll need."

---

## P-03 — JSON-RPC stdio transport with peer-gone classification

**Where in Hermes:** `tui_gateway/transport.py:100-180`.

**What it survives:**
- Half-closed pipe on `write` — distinguishes peer-gone from real I/O bug.
- Half-closed pipe on `flush` — same.
- ENOSPC, EACCES, and other "real" OSErrors re-raise so they hit the crash log.
- `UnicodeEncodeError` is a ValueError subclass but is *re-raised*, not swallowed.

**The shape (key invariant):**

> Returning False is the dispatcher's "broken stdout pipe" signal. Programming errors MUST NOT return False, otherwise a real bug looks like a clean disconnect. Those re-raise.

Specifically `_PEER_GONE_ERRNOS = {EPIPE, ECONNRESET, EBADF, ESHUTDOWN, WSAECONNRESET, WSAESHUTDOWN}` — anything outside the set is a real error.

**Cost to lift:** Low. ~150 LOC for a stripped-down `StdioTransport`. The errno discipline is the load-bearing detail; copy it exactly.

**Cross-walk:** `docs/python/09-timeout-patterns.md` (the flush-may-block escape hatch `_DISABLE_FLUSH`), `docs/python/24-queue-channel-patterns.md` (transport-as-channel abstraction).

**Verdict:** **Lift verbatim** when Ember introduces any JSON-line stdio protocol — likely with Bifröst's first non-CLI surface.

---

## P-04 — TeeTransport: best-effort mirroring with primary-determines-result

**Where in Hermes:** `tui_gateway/transport.py:186-220`.

**What it survives:**
- A slow sidecar publisher (WebSocket to dashboard) that would otherwise stall the main IO path.
- A failing secondary that should not affect the primary.

**The shape:**

```python
class TeeTransport:
    __slots__ = ("_primary", "_secondaries")
    def __init__(self, primary, *secondaries):
        self._primary = primary
        self._secondaries = secondaries
    def write(self, obj: dict) -> bool:
        ok = self._primary.write(obj)
        for sec in self._secondaries:
            try:
                sec.write(obj)
            except Exception:
                pass
        return ok
```

**Cost to lift:** Trivial. ~30 LOC. Useful any time Ember wants telemetry/audit-log mirroring without coupling latency.

**Cross-walk:** `docs/python/08-bulkhead-pattern.md` (primary and secondaries are bulkheaded — secondary failures don't sink the primary).

**Verdict:** **Lift when telemetry plugins arrive.** Direct port; one of the cleanest small abstractions in Hermes.

---

## P-05 — Stateful streaming scrubber for tag-boundary content

**Where in Hermes:** `agent/memory_manager.py:62-224` (`StreamingContextScrubber`), `agent/think_scrubber.py` (analogous for `<think>` tags).

**What it survives:**
- A model that opens `<memory-context>` in one delta and continues in the next — naive per-delta regex would let the body leak.
- A model that emits a closed pair across deltas.
- A model that *mentions* the tag name in normal prose ("I'll use `<think>` tags here") — boundary rule prevents incorrect suppression.
- An unterminated span at end-of-stream — discards the buffer rather than emit (leak-safe).

**The shape (key invariant from the docstring):**

> If we're still inside an unterminated span the remaining content is discarded (safer: leaking partial memory context is worse than a truncated answer).

**Cost to lift:** Low-Medium. ~200 LOC + ~200 LOC of tests. State machine is the hard part; Hermes's is correct and reusable.

**Cross-walk:** `docs/python/16-state-machines-reliability.md` (the scrubber is the canonical reliable-state-machine pattern).

**Verdict:** **Lift when Ember injects recalled context into the model.** Slice-4-likely. Apply the same shape to any future inline tag (`<source>`, `<tool>`, etc.).

---

## P-06 — IterationBudget: thread-safe consume/refund per agent

**Where in Hermes:** `agent/iteration_budget.py:1-62`.

**What it survives:**
- A runaway tool-call loop. The budget caps at `max_iterations` (default 90).
- A programmatic-tool `execute_code` turn that should not eat user-facing iterations — refund.
- Concurrent updates from multiple threads (single `threading.Lock` per budget).

**The shape:** 62 lines. Constructor, `consume() -> bool`, `refund()`, `used` and `remaining` properties.

**Cost to lift:** Trivial. ~50 LOC.

**Cross-walk:** `docs/python/20-thread-safety-python.md` (lock-guarded counter is the canonical pattern), `docs/python/09-timeout-patterns.md` (the budget is a *count*-based timeout).

**Verdict:** **Lift in slice 3.** Ember's tool framework needs this before it grows past the three-tool shipped set.

---

## P-07 — ToolCallGuardrailController: per-turn loop detection

**Where in Hermes:** `agent/tool_guardrails.py:1-475`.

**What it survives:**
- The model retrying the same tool call with identical arguments — exact-failure-count tracking.
- The same tool failing repeatedly with different arguments — per-tool failure count.
- An idempotent tool that returns the same result repeatedly — no-progress count.

**The shape (key dataclass):**

```python
@dataclass(frozen=True)
class ToolCallGuardrailConfig:
    warnings_enabled: bool = True
    hard_stop_enabled: bool = False   # opt-in!
    exact_failure_warn_after: int = 2
    exact_failure_block_after: int = 5
    same_tool_failure_warn_after: int = 3
    same_tool_failure_halt_after: int = 8
    no_progress_warn_after: int = 2
    no_progress_block_after: int = 5
    ...
```

**Cost to lift:** Medium. ~400 LOC (the controller plus the canonical-args hash plus the failure-classifier). The dataclasses port cleanly.

**Cross-walk:** `docs/python/07-circuit-breaker.md` (the per-turn controller *is* a circuit breaker), `docs/python/16-state-machines-reliability.md` (the per-turn state reset is a state machine).

**Verdict:** **Lift in slice 3** with one critical change vs Hermes: **`hard_stop_enabled` default is True**. Ember's Pi target makes runaway loops more painful than they are for cloud Hermes; default-strict, opt-out-permissive.

---

## P-08 — Snapshot-before-mutate + rollback-creates-snapshot

**Where in Hermes:** `agent/curator_backup.py:1-696`.

**What it survives:**
- A curator pass that crashes mid-mutation.
- An operator who realizes the curator did the wrong thing and wants to undo.
- The rollback itself failing — the pre-rollback state is *also* snapshotted, so the rollback can be rolled back.

**The shape (audit-relevant excerpts):**

> A pre-run snapshot of `~/.hermes/skills/` (excluding `.curator_backups/` itself) is taken before any mutating curator pass. Snapshots are tar.gz files under `~/.hermes/skills/.curator_backups/<utc-iso>/`. Rollback picks a snapshot, **moves the current `skills/` tree aside into another snapshot** so even the rollback itself is undoable, then extracts the chosen snapshot into place.

The discipline: never delete the prior state until the new state is verified.

**Cost to lift:** Medium. ~300 LOC for the snapshot/restore. The tarball-and-manifest pattern is good; the exclusion list per filesystem layout is the variable.

**Cross-walk:** `docs/python/17-saga-pattern.md` (snapshot is the compensation), `docs/python/15-self-repair-reconciliation.md` (rollback is the self-repair).

**Verdict:** **Lift when Ember adds any tree-mutating operation.** Brunnr re-index would qualify; Smiðja re-ingest would. Slice-4+ candidate.

---

## P-09 — Lazy-loaded heavy SDK with proxy class

**Where in Hermes:** `agent/process_bootstrap.py:34-60`.

**What it survives:**
- A 240ms import cost (OpenAI SDK) that would slow every `hermes --help` invocation.
- Tests that need `isinstance(client, OpenAI)` to work.
- Tests that need `patch("run_agent.OpenAI", ...)` to work.

**The shape:**

```python
class _OpenAIProxy:
    __slots__ = ()
    def __call__(self, *args, **kwargs):
        return _load_openai_cls()(*args, **kwargs)
    def __instancecheck__(self, obj):
        return isinstance(obj, _load_openai_cls())
    def __repr__(self):
        return "<lazy openai.OpenAI proxy>"

OpenAI = _OpenAIProxy()
```

**Cost to lift:** Low. ~30 LOC per heavy SDK.

**Cross-walk:** No direct Ember reliability doc; this is more of a performance pattern that has reliability implications (slow startup hides crashes in the "is it running yet?" gap).

**Verdict:** **Lift when Ember has any SDK over ~100ms cold-import.** Currently Ember keeps imports lean (per ADR 0007 stdlib-first). When `psycopg[binary]` cold-imports become an operator-visible delay, this is the answer.

---

## P-10 — `MIN_TTL`-guarded credential refresh

**Where in Hermes:** `agent/credential_pool.py` (specifically the OAuth refresh logic) — refreshes a credential when its `expires_at` is within `MIN_TTL_SECONDS` of now.

**What it survives:**
- A credential that "appears valid" but will expire mid-API-call.
- A refresh that runs concurrently from two threads — single-flight pattern with a per-credential lock.

**The shape:** Check expiry against `now() + MIN_TTL`. If too close, refresh first. Use a per-credential lock so only one refresh runs at a time.

**Cost to lift:** Low. ~100 LOC.

**Cross-walk:** `docs/python/09-timeout-patterns.md` (TTL is a soft deadline), `docs/python/22-concurrent-futures-patterns.md` (single-flight refresh).

**Verdict:** **Lift when Ember introduces auth tokens with expiry.** Slice 4+. Until then, no auth tokens, no refresh.

---

## P-11 — `try/except` + `sys.modules.pop` on import failure

**Where in Hermes:** `gateway/hooks.py:115-122`:

```python
module = importlib.util.module_from_spec(spec)
sys.modules[module_name] = module
try:
    spec.loader.exec_module(module)
except Exception:
    sys.modules.pop(module_name, None)
    raise
```

**What it survives:**
- A handler whose top-level code raises. Without the cleanup, `sys.modules` retains a half-initialized module, and any subsequent `import hermes_hook_<name>` returns the broken one.

**Cost to lift:** Trivial. ~5 LOC. A discipline, not an architecture.

**Cross-walk:** `docs/python/05-idempotency-design.md` — a clean load is idempotent only if a failed load doesn't leave state.

**Verdict:** **Lift verbatim** when Ember has any dynamic-import path (plugin loader). Slice 3+ when plugins land.

---

## P-12 — Typed error taxonomy with retry/compress/fallback hints

**Where in Hermes:** `agent/error_classifier.py:1-90`.

**What it survives:**
- An undocumented 463 status code: handled as `unknown` with retry-with-backoff.
- A `context_overflow` error: triggers compress, not retry.
- An auth failure: triggers credential rotation, not blind retry.

**The shape (key fields on `ClassifiedError`):**

```python
@dataclass
class ClassifiedError:
    reason: FailoverReason
    status_code: Optional[int] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    message: str = ""
    error_context: Dict[str, Any] = field(default_factory=dict)
    retryable: bool = True
    should_compress: bool = False
    # ... more hints on the full class
```

**Cost to lift:** Medium. ~400 LOC for a stripped-down classifier matching Ember's narrower set of providers (Ollama, Anthropic-Claude API, OpenAI-compat, llama.cpp-server-mode).

**Cross-walk:** `docs/python/06-retry-strategies.md` (the *hints* are the retry strategy inputs), `docs/python/02-result-types-vs-exceptions.md` (the typed-reason is the result-type discipline).

**Verdict:** **Lift, but extend.** Ember already has typed reasons on Brunnr `Disconnected`; widen to Funi and tools. Slice 3 candidate.

---

## P-13 — Sub-second shutdown grace with hard-exit fallback

**Where in Hermes:** `tui_gateway/entry.py:113-123` — daemon timer that calls `os._exit(0)` after the configured grace window, default 1 second.

**What it survives:**
- A worker thread holding a lock past `sys.exit()`.
- An atexit handler that deadlocks.
- An interpreter shutdown that does not progress.

**The shape:** Three lines of code plus a configurable env var (`HERMES_TUI_GATEWAY_SHUTDOWN_GRACE_S`). Daemon timer + `os._exit(0)`.

**Cost to lift:** Trivial.

**Cross-walk:** `docs/python/11-crash-only-software.md` — the "always be safe to crash" stance.

**Verdict:** **Lift when Ember subprocesses.** Until then, Munnr's interactive shutdown is dominated by user attention, not lock contention.

---

## P-14 — Discovery-time validator chain with explicit fail-closed

**Where in Hermes:** `gateway/platform_registry.py:208-256`.

**What it survives:**
- A plugin with missing dependencies (`check_fn` returns False).
- A misconfigured platform (`validate_config` returns False).
- A factory that throws an exception (`adapter_factory` raises).

**The shape:** Each guard returns None on failure; the caller's None-check is the signal. Logs the reason at WARNING.

**Cost to lift:** Low. Apply the same shape to Ember's `BrunnrBackend` / `FuniRuntime` / `EmberPlugin` discovery.

**Cross-walk:** `docs/python/03-defensive-programming-design-by-contract.md` — discovery is the precondition layer for downstream use.

**Verdict:** **Lift the shape, not the None-return convention.** Ember already uses typed results (`Disconnected`, etc.). Apply the same to discovery: `DiscoveryResult = Discovered(handle) | MissingDependency(name) | InvalidConfig(reason) | FactoryRaised(traceback)`. Caller pattern-matches.

---

## P-15 — Forensic exit-reason logging

**Where in Hermes:** `tui_gateway/entry.py:165-184` — every exit path writes a one-line reason to `_CRASH_LOG`.

**What it survives:**
- "It just died" → now reads as "gateway exit · reason=stdin EOF (TUI closed the command pipe)".

**The shape:**

```python
def _log_exit(reason: str) -> None:
    try:
        os.makedirs(os.path.dirname(_CRASH_LOG), exist_ok=True)
        with open(_CRASH_LOG, "a", encoding="utf-8") as f:
            f.write(f"\n=== gateway exit · {time.strftime('%Y-%m-%d %H:%M:%S')} · reason={reason} ===\n")
    except Exception:
        pass
    print(f"[gateway-exit] {reason}", file=sys.stderr, flush=True)
```

**Cost to lift:** Trivial. ~15 LOC. Apply uniformly to every Ember exit path.

**Cross-walk:** `docs/python/14-health-checks.md` (an exit reason is the final health check).

**Verdict:** **Lift verbatim.** Make this a *convention*: no `sys.exit()` without a paired `_log_exit("reason")` in Ember. Slice-3 contributor-doc target.

---

## Summary table

| # | Pattern | Survives | Cost | When to lift |
|---|---|---|---|---|
| P-01 | `_SafeWriter` | Broken stdio pipes | Trivial | When Ember runs detached |
| P-02 | SIGPIPE + grace + os._exit | Subprocess death modes | Moderate | When Ember subprocesses |
| P-03 | JSON-RPC stdio transport | Half-closed pipes | Low | First non-CLI surface |
| P-04 | TeeTransport | Slow sidecar publishers | Trivial | First telemetry plugin |
| P-05 | StreamingContextScrubber | Tag-boundary leaks | Low-Medium | When recalled context is injected |
| P-06 | IterationBudget | Runaway loops | Trivial | **Slice 3** |
| P-07 | ToolCallGuardrailController | Per-turn repeat-failure loops | Medium | **Slice 3** |
| P-08 | Snapshot-before-mutate | Failed mutation passes | Medium | First tree-mutating op |
| P-09 | Lazy-import proxy | Slow cold start | Low | When import cost matters |
| P-10 | MIN_TTL credential refresh | Expiring tokens | Low | When auth tokens land |
| P-11 | `sys.modules.pop` on import-fail | Half-initialized modules | Trivial | First dynamic-import path |
| P-12 | Typed error taxonomy | Unknown error codes | Medium | **Slice 3** (extend existing) |
| P-13 | Sub-second shutdown grace | Wedged threads at exit | Trivial | When subprocessing arrives |
| P-14 | Discovery validator chain | Bad plugin manifests | Low | First plugin loader |
| P-15 | Forensic exit-reason logging | "It just died" | Trivial | **Slice 3 convention** |

---

## Cross-walk with Ember's `docs/python/` reliability series

Ember already has a serious-grade reliability docs library. These Hermes patterns map cleanly:

- **`01-exception-design.md`** → P-12 (typed reasons replace string-matched exceptions).
- **`02-result-types-vs-exceptions.md`** → P-12 + P-14.
- **`03-defensive-programming-design-by-contract.md`** → P-14 (discovery as precondition).
- **`05-idempotency-design.md`** → P-11.
- **`06-retry-strategies.md`** → P-10, P-12 (the hints are retry strategy inputs).
- **`07-circuit-breaker.md`** → P-07 (the controller *is* a circuit breaker per turn).
- **`08-bulkhead-pattern.md`** → P-04 (primary and secondaries bulkheaded).
- **`09-timeout-patterns.md`** → P-03, P-06, P-10 (TTL is a timeout; iteration count is a timeout).
- **`10-graceful-degradation.md`** → P-01, P-15.
- **`11-crash-only-software.md`** → P-02, P-13.
- **`13-watchdog-timers.md`** → P-02 (daemon timer is a watchdog).
- **`14-health-checks.md`** → P-15.
- **`15-self-repair-reconciliation.md`** → P-08.
- **`16-state-machines-reliability.md`** → P-05, P-07.
- **`17-saga-pattern.md`** → P-08.
- **`20-thread-safety-python.md`** → P-06.
- **`22-concurrent-futures-patterns.md`** → P-10 (single-flight refresh).

The patterns in this catalog are the *applied* form of the docs Ember already has.

---

## What This Means for Ember

**Subsystems affected:**
- **Funi** — P-06, P-07, P-12 (iteration budget, tool guardrails, error taxonomy).
- **Strengr** — P-02, P-03, P-10, P-12 (subprocess crash-proofing, transport, credentials).
- **Brunnr** — P-08, P-12 (snapshot-before-mutate, error taxonomy on disconnect).
- **Smiðja** — P-08, P-11 (snapshots, clean dynamic import).
- **Hjarta** — P-15 (forensic exit logging during setup).
- **Munnr** — P-01, P-04, P-05, P-15 (safe stdio, telemetry tee, streaming scrub, exit logging).

**Vows touched:**
- **Vow of Modular Authorship** — every pattern except P-09 (lazy import) directly strengthens it.
- **Vow of Graceful Offline** — P-01, P-02, P-03, P-12, P-15.
- **Vow of Honest Memory** — P-05 most directly (no context leaks).
- **Vow of Smallness** — P-06, P-07 (cost guards).
- **Vow of Public-Friendliness** — P-15 (the operator sees *why*).

**Concrete next steps:**

1. **Slice 3 must-haves:** P-06 (`IterationBudget`), P-07 (`ToolCallGuardrailController` with hard-stop default-on), P-12 (typed error taxonomy expansion), P-15 (forensic exit-reason logging).
2. **Slice 3 should-haves:** P-11 (`sys.modules.pop`) when the plugin loader is drafted, P-01 (`_SafeWriter`) if any operator reports a detached-stdio bug.
3. **Slice 4+:** P-05 (streaming scrubber) when context injection lands, P-08 (snapshot-before-mutate) when the first tree-mutating Brunnr/Smiðja op lands.
4. **Lift-with-credit:** every pattern lifted from Hermes gets a comment block at the top of the Ember file: `# Lifted from agent/X.py:Y-Z under MIT license. See attribution in ORIGINS.md.`

Cross-link with [[50_verification/55_INVARIANT_LIST]] (each pattern enforces specific invariants), [[50_verification/56_TESTING_STRATEGY]] (how to verify the lifts work), and [[60_synthesis/63_INTEGRATION_PATHS]] (the Cartographer's lift-order proposal).

These patterns are paid-for engineering. Lift them with care; refuse them when the Vows demand it; but do not rebuild them from scratch when Hermes has already done the proof-of-pain.
