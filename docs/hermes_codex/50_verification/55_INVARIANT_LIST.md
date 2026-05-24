---
codex_id: 55_INVARIANT_LIST
title: Invariant List — What Must Hold When Ember Borrows From Hermes
role: Auditor
layer: Verification
status: draft
hermes_source_refs:
  - agent/memory_manager.py:244-302
  - agent/memory_manager.py:62-224
  - agent/tool_guardrails.py:127-141
  - agent/iteration_budget.py:1-62
  - agent/credential_pool.py:1-200
  - agent/redact.py:60-67
  - agent/file_safety.py:28-104
  - agent/process_bootstrap.py:63-167
  - tui_gateway/entry.py:65-247
  - tui_gateway/transport.py:1-220
  - SECURITY.md:60-220
  - hermes_cli/plugins.py:128-168
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
cross_refs:
  - 50_verification/50_HERMES_RISK_REGISTER
  - 50_verification/52_ANTIPATTERN_CATALOG
  - 50_verification/53_CRASH_PROOFING_PATTERNS
  - 50_verification/56_TESTING_STRATEGY
  - 20_interface/24_MEMORY_INTERFACE
  - 20_interface/25_GATEWAY_INTERFACE
  - 20_interface/27_PLUGIN_INTERFACE
---

# Invariant List

*Sólrún, even-toned: an invariant is a property the code promises will always be true. The promise costs nothing to make and everything to break. This list catalogs the invariants Ember must maintain when she lifts Hermes patterns. Each one comes with a why and a test approach — the why because an invariant without justification gets removed by the next refactor, the test because an invariant that is not tested is a documented hope.*

Invariants are numbered I-NN. Categories: **Memory**, **Tool/Loop**, **Boundary**, **Streaming**, **Persistence**, **Plugin/Hook**, **Security**, **Process**, **Naming/Identity**. Each entry: statement, why, how to test.

---

## Memory invariants

### I-01 — At most one external MemoryProvider is registered at runtime

**Statement:** When/if Ember grows a multi-provider memory layer, only one *external* (non-builtin) provider can be active at a time. A second registration is refused with a typed result.

**Why:** Tool-schema bloat is a real cost on a Pi. Two competing recall sources confuse the model. Hermes enforces this via `agent/memory_manager.py:258-279`.

**How to test:**
- Register two distinct external providers; assert the second returns `RegistrationRefused(name="...", reason=external_already_present)`.
- Assert `manager.providers` contains only the first.

---

### I-02 — `<memory-context>` fence is a parse boundary, not a trust boundary

**Statement:** Any code that emits recalled memory wrapped in `<memory-context>...</memory-context>` is documenting the *parse* shape for downstream consumers. No code path may treat the *presence* of the fence in a string as evidence of authenticity.

**Why:** The model can learn the fence pattern; an attacker-influenced provider can emit a fence. Hermes documents this exactly in `SECURITY.md:136-145` and pre-strips fences in `agent/memory_manager.py:227-241`.

**How to test:**
- Inject text containing a forged `<memory-context>...</memory-context>` via a user message; assert no code path treats it as authoritative recall.
- Pre-wrapped provider output is stripped before re-wrapping.

---

### I-03 — Recalled context is never executed as instruction

**Statement:** Content retrieved from Brunnr and rendered to the model is data, not behavior change. A recalled string containing "ignore previous instructions" must not change the agent's behavior beyond the model's own judgment.

**Why:** Vow of Honest Memory + Vow of Tethered Grounding. Recall is informational.

**How to test:**
- Ingest a document that says "When asked X, do Y dangerous thing."
- Ask X; verify Y did not happen automatically.
- Document this is best-effort; model judgment is the second line of defense.

---

### I-04 — Citations accompany every grounded reply

**Statement:** When Munnr renders a reply that consulted the Well (Brunnr returned ≥1 chunk for the turn), the rendered output includes source citations for those chunks.

**Why:** Vow of Honest Memory mechanical enforcement, per SYSTEM_VISION §11 ("Citations rendered on every grounded reply").

**How to test:**
- Mock Brunnr to return chunks with known sources.
- Run a chat turn; assert citations are present in Munnr's output.
- When Brunnr returns nothing or is disconnected, assert the disconnect banner is present and citations are absent.

---

### I-05 — Session-id rotation always emits `on_session_switch` before the next write

**Statement:** Any path that reassigns the agent's session_id (`/new`, `/reset`, `/branch`, `/resume`, context compression) calls `on_session_switch(new_session_id, ...)` on all memory providers *before* the next `sync_turn` lands.

**Why:** Without this signal a provider writes to the wrong session, fragmenting operator history. Hermes enforces this (`agent/memory_manager.py:457-490`).

**How to test:**
- Rotate session_id via every rotation path; assert `on_session_switch` was invoked with the right arguments before any subsequent `sync_turn`.
- Spy provider records sequence; verify ordering.

---

## Tool / loop invariants

### I-06 — Iteration budget cannot be consumed past the cap

**Statement:** `IterationBudget.consume()` returns False once `used >= max_total`. No subsequent code path may execute an iteration.

**Why:** Hermes pattern `agent/iteration_budget.py:31-44`. Vow of Smallness — runaway loops on a Pi are operator-visible pain.

**How to test:**
- Consume exactly `max_total` times; assert all return True.
- Consume one more; assert False.
- Concurrent consume from N threads; assert exactly `max_total` Trues.

---

### I-07 — `execute_code`-style iterations are refunded

**Statement:** When a tool call is classified as programmatic (execute_code), the iteration budget is refunded so the budget reflects only user-facing iterations.

**Why:** Hermes pattern in the same module. Programmatic iterations should not count against the budget the operator configured.

**How to test:**
- Consume, then refund; assert `used` decreased by 1.
- Multiple refunds bring `used` down to 0, never below.

---

### I-08 — Repeated identical failed tool calls trigger hard-stop

**Statement:** With `hard_stop_enabled=True`, the same tool name + canonical-args producing failure N times (default 5) causes a `Decision(action=block)` from `before_call`. No tool execution proceeds.

**Why:** Hermes pattern `agent/tool_guardrails.py:241-283`. Loop detection prevents the model from spending forever retrying the same bad call.

**How to test:**
- Configure block_after=3; simulate 3 failures of the same `(tool, args)`; assert the 4th `before_call` returns `action="block"`.

---

### I-09 — Tool refusals are typed, not collapsed

**Statement:** Tool dispatch outcomes use a typed enum (slice-2 `ApprovalOutcome`). Distinct outcomes (approved, auto_approved, denied, invalid_arguments, forbidden, no_such_tool, timeout) are not flattened to "failed".

**Why:** SYSTEM_VISION §11 Vow of Honest Memory ("Tool refusals are audited but not executed: the audit log distinguishes…"). The audit log is the post-hoc truth surface; type erasure makes it lie.

**How to test:**
- Force each outcome class via crafted inputs.
- Assert the audit log records the typed string, not "failed".

---

## Boundary invariants

### I-10 — Realm bands honour direction

**Statement:** Spark may import Thread. Thread may import Well. Spark may import Well *only* via Thread (the inversion is not allowed). Lower bands never import upper bands.

**Why:** SYSTEM_VISION §11 "Vow of Modular Authorship — Realm bands are mechanical: higher band may import lower (Spark → Thread → Well), never the reverse. Verified by the skeleton-imports test."

**How to test:**
- The existing `tests/unit/test_skeleton_imports.py` pins this; extend per realm as new modules land.

---

### I-11 — Disconnected is a typed value, never an exception

**Statement:** Every realm-boundary `open()` and `health()` returns a typed result with explicit reason codes. Exceptions from underlying libraries are caught and folded into the typed result at the boundary.

**Why:** ADR 0007 §2.2. Discipline is already in place for Brunnr (eight reasons) and Funi (`Unavailable`). Must continue to Strengr health, tools' `ToolReply.error`, and any new boundary.

**How to test:**
- For each boundary, induce a failure (mock the underlying library to raise); assert the boundary returns a typed value, not propagates the exception.

---

### I-12 — Banner-and-instruction injection on disconnect

**Statement:** When Strengr reports Well unreachable, Munnr prepends the disconnect banner and Funi's system prompt is assembled with `well_disconnected=True`, which adds the "do not invent" instruction.

**Why:** Per SYSTEM_VISION §11 Vow of Graceful Offline mechanical enforcement.

**How to test:**
- Mock Strengr to return `Disconnected(CONN_REFUSED)`; run a chat turn; assert banner in Munnr output AND assert the assembled prompt contains the disconnect instruction.

---

### I-13 — Tool tools never see the Well credentials

**Statement:** When write tools land (slice 4+), the subprocess/environment passed to the tool's child does not include Brunnr credentials (DB password, pgvector connection string).

**Why:** `SECURITY.md:121-134` credential scoping. A tool that can write to disk should not also have the keys to the data store.

**How to test:**
- Spawn the tool's child with a spy `Environment`; assert the relevant credentials are absent.

---

## Streaming invariants

### I-14 — Unterminated `<think>` / `<memory-context>` span at end-of-stream discards content

**Statement:** A streaming scrubber that has opened a tag span but never received the close tag MUST discard the held-back buffer at flush(). Discarded content does not appear in the output.

**Why:** Hermes pattern `agent/memory_manager.py:147-161`. Leak-safe-on-unterminated.

**How to test:**
- Feed deltas that open a span, then end-of-stream; assert flush returns empty.
- Verify no content from inside the span leaked to prior feed() returns.

---

### I-15 — Streaming scrubber respects block-boundary rule on open tag

**Statement:** An open tag found in the middle of a non-empty line is NOT treated as a tag opener. Only when preceded by start-of-stream, newline-and-whitespace, or only-whitespace-on-current-line does the scrubber treat the tag as a span start.

**Why:** Prevent the scrubber from suppressing prose that mentions the tag name (e.g. "use `<think>` tags here"). Hermes pattern `agent/memory_manager.py:204-225` and analogous `agent/think_scrubber.py`.

**How to test:**
- Feed "prose mentioning `<think>` here." — assert no suppression.
- Feed "\n<think>real reasoning</think>\nback to normal" — assert real reasoning is suppressed.

---

### I-16 — Tool-call accumulation across stream chunks

**Statement:** When a Funi adapter streams via NDJSON or SSE, tool_calls emitted on intermediate frames (done=False) accumulate and are attached to the final frame's classified result.

**Why:** Slice-2 Phase-16 Ollama-streaming surprise (per SLICE_2_RETROSPECTIVE). A tool_call on frame 1 that the agent never saw means the chat loop silently terminates.

**How to test:**
- Mock Ollama to emit tool_calls on frame 1, done=True on frame 2 with no tool_calls. Assert the agent received the tool_call.

---

## Persistence invariants

### I-17 — Persistence is post-turn, failure is non-fatal

**Statement:** Episode persistence runs after the model's reply has been rendered. Persistence failure does not break the in-memory window.

**Why:** SYSTEM_VISION §11 Vow of Honest Memory.

**How to test:**
- Mock Brunnr write to fail; run a turn; assert the operator received the reply and the in-memory window contains the turn.

---

### I-18 — Interrupted partial replies persist with `[interrupted by operator]` tag

**Statement:** When the operator presses Ctrl-C mid-stream, the partial reply already streamed to the operator is persisted with the marker. No fabricated continuation, no silent loss.

**Why:** SYSTEM_VISION §11. The audit trail must reflect what actually happened.

**How to test:**
- Simulate Ctrl-C mid-stream; assert the persisted Episode contains the tag and the text the operator saw.

---

### I-19 — The streaming path persists the FINAL reply, not intermediate states

**Statement:** When the tool-loop calls the model multiple times in one turn, the persisted reply is the post-tool-loop final reply, not an intermediate one.

**Why:** "The operator's mental model of 'what Ember said' matches what's stored." (SYSTEM_VISION §11).

**How to test:**
- Run a turn with N tool calls; assert the persisted Episode contains the final response, not any intermediate.

---

## Plugin / Hook invariants

### I-20 — Plugin discovery without enablement does nothing

**Statement:** A plugin directory existing at `~/.ember/plugins/<name>/` does not cause any code to run unless `plugins.enabled: [<name>]` is in the operator's config.

**Why:** [[20_interface/27_PLUGIN_INTERFACE]] proposal #5; [[50_verification/52_ANTIPATTERN_CATALOG]] A-08.

**How to test:**
- Place a plugin in the directory without enablement; start Ember; assert the plugin's `register()` was never invoked.

---

### I-21 — Plugin manifest version is checked at load

**Statement:** The plugin loader refuses any plugin where `protocol_version < MIN_SUPPORTED` or `> MAX_SUPPORTED`. The refusal is a typed result (`IncompatibleVersion(min, max, actual)`).

**Why:** [[20_interface/27_PLUGIN_INTERFACE]] proposal #7; [[50_verification/52_ANTIPATTERN_CATALOG]] A-07.

**How to test:**
- Create plugins at v=0 and v=999; assert both refused with the typed result.

---

### I-22 — Plugin teardown is invoked on every exit path

**Statement:** Every successfully-loaded plugin's `teardown()` runs on (a) process exit, (b) `/reset`, (c) `ember plugins disable <name>`.

**Why:** [[20_interface/27_PLUGIN_INTERFACE]] proposal #4. Prevents process-singleton state surviving rotation.

**How to test:**
- Hook a teardown spy; trigger each exit path; assert teardown was called once per path.

---

### I-23 — Plugin partial-load rolls back

**Statement:** If `register(ctx)` raises after registering some tools/hooks, the loader rolls back the already-registered items and reports `LoadFailed(traceback)`. The agent runs with the plugin absent, not half-loaded.

**Why:** [[20_interface/27_PLUGIN_INTERFACE]] proposal #3.

**How to test:**
- Author a plugin that registers tool A then raises; assert tool A is not in the registry after load fails.

---

### I-24 — Duplicate plugin names refuse to load

**Statement:** Two plugins with the same `name` cannot both load. The loader refuses the second with `LoadFailed(NameCollision)`.

**Why:** No silent shadowing. [[50_verification/52_ANTIPATTERN_CATALOG]] A-04.

**How to test:**
- Provide two plugins named `foo`; assert exactly one loaded and the other returned `NameCollision`.

---

## Security invariants

### I-25 — Redaction is on by default; opt-out requires CLI flag at process start

**Statement:** Without `--insecure-no-redact` at process start, every log line, every audit-log JSONL entry, every stderr emission passes through the redact pipeline. A config-file setting cannot disable it.

**Why:** [[50_verification/52_ANTIPATTERN_CATALOG]] A-09. An LLM with write tools could otherwise edit the config to disable redaction.

**How to test:**
- Set the config flag to disable; start Ember without the CLI flag; assert redaction is still active.
- Pass the CLI flag; assert redaction disabled.

---

### I-26 — Surrogate scrub on every external-boundary write

**Statement:** Every string written to Brunnr, emitted to the audit log, sent through Bifröst, or printed by Munnr passes through `sanitize_surrogates`. Lone surrogate code points become `�`.

**Why:** Hermes `agent/message_sanitization.py:31-39` exists because lone surrogates crash `json.dumps`. The crash is correctness, not security, but the discipline crosses the boundary.

**How to test:**
- Inject lone surrogates at each write boundary; assert the persisted/emitted text has `�` and no lone surrogates.

---

### I-27 — Write-tool path checks are symlink-resolved

**Statement:** Any write tool's safe-root or denylist check runs against `os.path.realpath(os.path.expanduser(path))`, not the raw operator-supplied path.

**Why:** Hermes pattern `agent/file_safety.py:33`. Without realpath, a symlink at `~/.ember/workspace/secret -> /etc/passwd` bypasses the safe-root.

**How to test:**
- Create a symlink that points outside the safe-root; attempt to write through it; assert refusal.

---

### I-28 — `fetch_url` private-address denylist is on by default

**Statement:** The slice-2 `fetch_url` tool refuses to fetch IPv4 RFC 1918, IPv4 link-local (169.254.0.0/16), IPv6 loopback/link-local, and loopback addresses unless the operator explicitly opted in.

**Why:** SSRF prevention. Already implemented in slice 2 (`bind_allow_private_default`).

**How to test:**
- Attempt `fetch_url("http://169.254.169.254/...")`; assert refusal.
- Attempt with `allow_private=True`; assert success (where the operator opted in at config time).

---

### I-29 — Allowlist required for any non-loopback bind

**Statement:** When Bifröst (or any future network-exposed surface) lands, binding to a non-loopback address requires an operator-set allowlist. The bind refuses to start without one.

**Why:** `SECURITY.md:189-209` uniform rule. [[50_verification/54_SECURITY_REVIEW]] §2.2.

**How to test:**
- Configure Bifröst to bind on `0.0.0.0:8080` with no allowlist; assert startup refusal.
- Configure with `bifrost.allowlist: [...]`; assert startup proceeds.

---

## Process invariants

### I-30 — Stdout writes are line-atomic under contention

**Statement:** When Ember has multiple emitters (subprocess JSON-RPC, telemetry tee), each JSON frame is serialized to a string outside the stdout lock, then written under the lock. No interleaved JSON frames.

**Why:** Hermes pattern `tui_gateway/transport.py:108-180`. Interleaved frames break the JSON-line protocol.

**How to test:**
- Spawn N concurrent writers emitting large payloads; capture stdout; parse line by line; assert every line is valid JSON.

---

### I-31 — Peer-gone errnos surface as typed "disconnected", not exceptions

**Statement:** When stdio writes encounter `EPIPE`, `ECONNRESET`, `EBADF`, `ESHUTDOWN`, the transport returns False (or its Ember equivalent typed value). Other OSErrors re-raise so they hit the crash log.

**Why:** [[50_verification/53_CRASH_PROOFING_PATTERNS]] P-03. Hermes invariant in `tui_gateway/transport.py:36-43` and `:140-158`.

**How to test:**
- Mock the stream to raise OSError with each errno; assert returns False for the peer-gone set, raises for ENOSPC.

---

### I-32 — Every exit path logs a reason

**Statement:** No `sys.exit(...)` runs without a paired `_log_exit("reason")` (or equivalent) in any Ember code path that exits the process.

**Why:** [[50_verification/53_CRASH_PROOFING_PATTERNS]] P-15. Hermes pattern `tui_gateway/entry.py:165-184`.

**How to test:**
- Static check via grep / pre-commit: `sys.exit` calls must be on a line within 3 lines of a `_log_exit` (or the function containing them must call it).
- Runtime: simulate each exit reason; assert crash log contains the reason string.

---

## Naming / identity invariants

### I-33 — `session_id` is opaque; consumers do not parse it

**Statement:** Code that uses `session_id` may compare for equality, may treat it as a key, may emit it in logs (after redaction). No code path splits, slices, or pattern-matches on the string contents.

**Why:** [[20_interface/25_GATEWAY_INTERFACE]] §3. Identity strings differ by platform; assuming structure makes one platform's adapter break.

**How to test:**
- A future test that introspects code for `session_id[...]`, `session_id.split(...)`, etc. is hard to write generically; document the rule in `RULES.AI.md` and add a code-review checklist item.

---

### I-34 — True Names own their realm; modules don't leak

**Statement:** `src/ember/spark/funi/` contains only Funi code. `src/ember/well/brunnr/` contains only Brunnr code. Vendor-named modules live as children of their realm (`spark/funi/ollama/`), never at the top level.

**Why:** SYSTEM_VISION §4 — True Names are load-bearing. [[50_verification/52_ANTIPATTERN_CATALOG]] A-19.

**How to test:**
- Static layout check: assert no top-level package named after a vendor (`ollama`, `anthropic`, `openai`, `pgvector` as top-level subpackages would all fail).

---

### I-35 — Builtin memory provider is always present and always first

**Statement:** When Ember grows a memory provider system, the builtin provider is registered at construction, never removed, and always at index 0 of `manager.providers`.

**Why:** Hermes pattern (implicit in `agent/memory_manager.py:244-302`). The system prompt ordering depends on this; `on_memory_write` fan-out to externals skips the builtin precisely because it knows the builtin is the source.

**How to test:**
- Assert `manager.providers[0].name == "builtin"` after every registration sequence.
- Assert no public API can remove the builtin.

---

## Summary

35 invariants. Categories:

- Memory: 5
- Tool/loop: 4
- Boundary: 4
- Streaming: 3
- Persistence: 3
- Plugin/hook: 5
- Security: 5
- Process: 3
- Naming/identity: 3

Several Hermes patterns map to multiple invariants (e.g. `StreamingContextScrubber` underpins I-14 and I-15; the redaction pipeline underpins I-25; the typed-result discipline underpins I-11, I-12, I-21, I-23, I-24).

---

## What This Means for Ember

**Subsystems affected:** All six True Names. Specific high-traffic invariants:
- **Funi:** I-06, I-07, I-08, I-09, I-11, I-12, I-14, I-15, I-16, I-19.
- **Strengr:** I-11, I-12, I-13, I-29.
- **Brunnr:** I-04, I-11, I-13, I-17, I-26, I-27.
- **Smiðja:** I-26, I-27, I-34.
- **Hjarta:** I-25, I-27, I-29.
- **Munnr:** I-04, I-12, I-18, I-19, I-26, I-30, I-32.
- **Plugins (when they land):** I-20, I-21, I-22, I-23, I-24.

**Vows touched:** All ten Vows have invariants here.

**Concrete next steps:**

1. **Pin every applicable invariant with a test.** [[50_verification/56_TESTING_STRATEGY]] expands this into concrete suites.
2. **For invariants that are already enforced (I-04, I-05, I-10, I-12, I-17, I-18, I-19, I-26, I-28): confirm the slice-2 test suite covers them.** Cross-walk to existing tests in `tests/unit/` and `tests/integration/`.
3. **For invariants that block slice 3 (I-06, I-07, I-08, I-09, I-25, I-32): land them with the slice-3 implementation work.** No slice 3 ratification without these.
4. **For invariants that block external surfaces (I-29): land them before Bifröst.**
5. **For invariants that block the plugin loader (I-20, I-21, I-22, I-23, I-24): land them with the plugin loader.** No plugin loader merge without all five.

Cross-link with [[50_verification/50_HERMES_RISK_REGISTER]] (each invariant, if held, neutralizes specific risks), [[50_verification/56_TESTING_STRATEGY]] (how to test each one), and [[50_verification/53_CRASH_PROOFING_PATTERNS]] (the patterns that enforce these invariants).

Invariants live where the test lives. Where there is no test, there is no invariant — only a hope. Hope is not engineering.
