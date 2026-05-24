---
codex_id: 50_HERMES_RISK_REGISTER
title: Hermes Risk Register — Operational, Security, Correctness
role: Auditor
layer: Verification
status: draft
hermes_source_refs:
  - SECURITY.md:1-332
  - agent/credential_pool.py:1-200
  - agent/redact.py:60-67
  - gateway/hooks.py:115-122
  - gateway/platform_registry.py:172-187
  - tui_gateway/entry.py:65-134
  - agent/memory_manager.py:62-224
  - agent/file_safety.py:28-104
  - hermes_cli/plugins.py:1-200
  - agent/error_classifier.py:1-90
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
cross_refs:
  - 50_verification/52_ANTIPATTERN_CATALOG
  - 50_verification/54_SECURITY_REVIEW
  - 50_verification/55_INVARIANT_LIST
  - 50_verification/53_CRASH_PROOFING_PATTERNS
  - 20_interface/24_MEMORY_INTERFACE
  - 20_interface/25_GATEWAY_INTERFACE
  - 20_interface/27_PLUGIN_INTERFACE
---

# Hermes Risk Register

*Sólrún, cataloguing: every system carries risks. Most projects pretend they do not. The risks become bugs in production. The bugs become postmortems. The postmortems are then forgotten and the cycle resumes. I will not let that happen here. Every risk gets a name, a trigger, a blast radius, a likelihood, a mitigation, and — for Ember's purposes — a verdict on whether she would inherit it.*

Each entry is graded:

- **Trigger** — the condition under which the risk realises.
- **Blast radius** — the breadth of consequence: single-turn / session / process / host / network / operator.
- **Likelihood** — Low / Medium / High in normal operation.
- **Hermes mitigation** — what is already in place.
- **Would Ember inherit?** — verdict, with reasoning.

Risks are grouped by category (operational, security, correctness). Not exhaustive — but the 17 named here are the ones an honest verifier would surface first.

---

## R-01 — Silent fan-out failure in MemoryManager

**Category:** Correctness / Operational
**Hermes source:** `agent/memory_manager.py:325-609` (every fan-out wraps provider calls in `try/except`, logs at WARNING/DEBUG, continues).
**Trigger:** A registered memory provider raises in `prefetch`, `sync_turn`, `on_session_switch`, `on_memory_write`, or any hook.
**Blast radius:** Session — the operator's memory recall is degraded for the whole session; no banner, no degraded-mode marker.
**Likelihood:** Medium. Network providers (Honcho, Hindsight, Mem0) fail intermittently. Local providers fail when their backing storage corrupts.
**Hermes mitigation:** `try/except` per call, log line, continue. *No operator-visible signal.*
**Would Ember inherit?** **No, if she follows ADR 0007 §2.2.** Ember's typed-value-over-exception discipline means a Brunnr/MemoryProvider failure must surface as a `Disconnected` value carrying a typed reason. Munnr renders a banner. The operator sees the degraded state.

---

## R-02 — `<memory-context>` fence treated as trust boundary

**Category:** Security / Correctness
**Hermes source:** `agent/memory_manager.py:43-59`, `:227-241`.
**Trigger:** A memory provider — or a model the provider's output flows through — emits content containing the `<memory-context>` fence pattern. `sanitize_context()` strips pre-wrapped fences (`agent/memory_manager.py:54-59`), but the fence is also the parsing contract for the model's downstream consumer.
**Blast radius:** Single-turn — fake "system note" smuggled past the consumer; the model could be persuaded to weight an attacker-crafted "memory" as authoritative.
**Likelihood:** Low under benign operation; Medium under adversarial input flowing through a provider.
**Hermes mitigation:** Pre-strip on output, regex-canonical fence on injection. *This is a heuristic, explicitly named non-boundary in `SECURITY.md:136-145`.*
**Would Ember inherit?** **Conditionally.** If Ember adds context injection, she must adopt the heuristic *and* document explicitly that it is parse-time, not trust-time. The trust boundary is the model assumption; the fence is the punctuation.

---

## R-03 — Streaming context leak via per-delta regex

**Category:** Correctness / Privacy
**Hermes source:** `agent/memory_manager.py:62-224` (the `StreamingContextScrubber` exists explicitly because earlier per-delta regex code leaked memory context across chunk boundaries).
**Trigger:** A model streams the `<memory-context>` open tag in one delta and the contents in another. A one-shot regex over each delta cannot match the closed pair.
**Blast radius:** Single-turn → operator visible: recalled memory bleeds into chat output.
**Likelihood:** Was *certain* in the buggy version; now Low after the scrubber lands.
**Hermes mitigation:** Stateful scrubber (`feed`/`flush`), boundary-aware open-tag detection, leak-safe-on-unterminated.
**Would Ember inherit?** **Yes, when Ember streams memory.** Slice-2 Munnr streams Funi output but does not yet stream memory injection. When she does, the scrubber pattern is the reference design.

---

## R-04 — Tool-call loop with no operator visibility

**Category:** Operational / Cost
**Hermes source:** `agent/tool_guardrails.py:1-475` — `ToolCallGuardrailController` exists; hard-stop is *opt-in* (`hard_stop_enabled: bool = False`, `agent/tool_guardrails.py:73`).
**Trigger:** The model retries the same tool call with identical arguments. Default config: a *warning* fires after 2-3 repeats; *no hard stop* unless the operator turned on `hard_stop_enabled` in `config.yaml`.
**Blast radius:** Session — token cost, API quota, time. In subagent mode, can exhaust delegation budget.
**Likelihood:** High under operator inattention; Medium under normal use.
**Hermes mitigation:** Warning by default; hard stop opt-in; iteration budget caps the worst case (`agent/iteration_budget.py:1-62`).
**Would Ember inherit?** **Yes, with default hard-stop.** Ember's Pi target makes runaway loops more painful (cost: local compute time, not money). Slice-3+ tool framework should ship with the hard-stop default *on*, with the operator able to relax it.

---

## R-05 — Redaction is opt-out by env var

**Category:** Security / Privacy
**Hermes source:** `agent/redact.py:60-67`:

```python
# Snapshot at import time so runtime env mutations (e.g. LLM-generated
# `export HERMES_REDACT_SECRETS=false`) cannot disable redaction
# mid-session.
_REDACT_ENABLED = os.getenv("HERMES_REDACT_SECRETS", "true").lower() in {"1", "true", "yes", "on"}
```

**Trigger:** Operator sets `HERMES_REDACT_SECRETS=false` (or `security.redact_secrets: false` in `config.yaml`). All secret patterns now pass through logs and gateway output.
**Blast radius:** Operator — leaked credentials in logs, in chat output, in pasted bug reports.
**Likelihood:** Medium. Power-users disable it for development; sometimes forget to re-enable. Comment at `agent/redact.py:60-66` reads: *"ON by default — secure default per issue #17691."*
**Hermes mitigation:** Default-on; import-time snapshot prevents LLM-driven runtime disable; opt-out log line at startup.
**Would Ember inherit?** **Stronger.** Ember's redact-equivalent should be `default-on, opt-out-not-allowed-via-LLM`, and the opt-out path should require an explicit flag at process start (`ember --insecure-no-redact`), not a config file the model could write.

---

## R-06 — Plugin loads arbitrary Python at install-time and import-time

**Category:** Security
**Hermes source:** `hermes_cli/plugins.py:1-200`, `gateway/hooks.py:115-122`.
**Trigger:** Operator installs a third-party plugin (`hermes plugins install ...`), or drops a file into `~/.hermes/hooks/<name>/handler.py`. The next `hermes` invocation imports it.
**Blast radius:** Host. A plugin can read every credential the agent has, call every tool, register transform hooks that rewrite model output silently.
**Likelihood:** Low under operator-only install; Medium-to-High if a user account is compromised or if a plugin source is breached.
**Hermes mitigation:** Documented in `SECURITY.md:154-168`: the boundary is operator review before install. Skills Guard scans for injection patterns but is explicitly *not a boundary*.
**Would Ember inherit?** **Yes, but with stronger defaults.** Plugins are opt-in by name in `config.yaml`. Only `~/.ember/plugins/` is the default discovery source. Manifest is contractual (per [[20_interface/27_PLUGIN_INTERFACE]]). No `transform_llm_output`-style hook that violates the Vow of Honest Memory.

---

## R-07 — Credential pool synchronization across processes

**Category:** Operational / Correctness
**Hermes source:** `agent/credential_pool.py:1-200` (1,955 lines total) — multi-credential rotation with per-credential cooldown.
**Trigger:** Two agent processes both update the same credential pool file (`~/.hermes/credential_pool.json` or equivalent). One sets `STATUS_EXHAUSTED` on a credential; the other sees stale "ok" and burns the rate limit.
**Blast radius:** Operator-wide credential exhaustion; one slow process can lock the pool while another waits.
**Likelihood:** Medium for the multi-process use case (cron + interactive, gateway + interactive).
**Hermes mitigation:** File lock on writes (per `read_credential_pool` / `write_credential_pool` in `hermes_cli/auth.py`). Cooldowns absorb stale "ok" guesses (`agent/credential_pool.py:75-77`).
**Would Ember inherit?** **Conditionally.** Ember slice-2 has no credential pool. If/when Ember grows API-key rotation, the pattern is needed; the file-lock plus typed-status approach is the reference.

---

## R-08 — Curator backup recursion / partial restore

**Category:** Correctness
**Hermes source:** `agent/curator_backup.py:1-696`. Backups exclude `.curator_backups/` (to avoid recursion bombs, `agent/curator_backup.py:63`) and `.hub/`. Restore moves the current tree to a fresh snapshot first.
**Trigger:** A snapshot taken mid-curator-pass captures inconsistent state (the curator's transactional unit is not the snapshot's). Restore puts the operator into a state that *was* never actually live.
**Blast radius:** Operator local — skill tree in inconsistent state until next curator pass repairs.
**Likelihood:** Low (Hermes does the right thing in code, but the transactional boundary is implicit).
**Hermes mitigation:** Snapshot before mutating pass; rollback creates *another* snapshot first so the rollback itself is undoable.
**Would Ember inherit?** **The pattern, yes.** Whenever Ember introduces curator-like compaction (Brunnr re-index, Smiðja re-ingest), the "snapshot-before-mutate, rollback-creates-snapshot" idiom is correct.

---

## R-09 — TUI gateway silent death via SIGPIPE

**Category:** Operational
**Hermes source:** `tui_gateway/entry.py:65-162`.
**Trigger:** A background thread (TTS playback, beep, voice status emitter) writes to stdout after the Ink TUI parent has stopped reading. Default SIGPIPE handling kills the process.
**Blast radius:** Process — the user sees "gateway exited" with no log entry.
**Likelihood:** Was certain pre-fix; now negligible.
**Hermes mitigation:** `signal.signal(signal.SIGPIPE, signal.SIG_IGN)`; broken-pipe surfaces as `BrokenPipeError` on next write which `StdioTransport` catches and returns False (`tui_gateway/transport.py:140-158`).
**Would Ember inherit?** **Yes if Ember ever subprocesses.** Slice-2 Ember is in-process; no SIGPIPE risk yet. Slice-3+ Bifröst, if a subprocess, should adopt the pattern verbatim.

---

## R-10 — Process-singleton state survives session rotation

**Category:** Correctness
**Hermes source:** `gateway/hooks.py:115-122` (handlers loaded once, module state preserved), `hermes_cli/plugins.py` (plugin `register(ctx)` runs once).
**Trigger:** Operator runs `/new` or `/reset`. Plugin/hook module-level state (cached credentials, in-flight counters, open connections) is NOT cleared.
**Blast radius:** Session — leakage of state from prior session into new one; correctness bugs in plugins that assumed reset.
**Likelihood:** High for plugins not authored with session rotation in mind.
**Hermes mitigation:** `on_session_reset` hook exists; plugin authors who care can subscribe. Plugin authors who don't subscribe leak by default.
**Would Ember inherit?** **No — by interface design.** Per [[20_interface/27_PLUGIN_INTERFACE]] §8, Ember mandates plugin `teardown()` and treats `/reset` as a teardown-and-reinit cycle for plugins. Module-singleton state is contraindicated.

---

## R-11 — File-safety denylist is a known-paths list

**Category:** Security
**Hermes source:** `agent/file_safety.py:28-104`. Denylist of exact paths + directory prefixes (~/.ssh, ~/.aws, ~/.gnupg, /etc/sudoers, etc.).
**Trigger:** A new sensitive path appears in the operator's environment that is not on the list. E.g. a new credential manager that writes to `~/.config/<vendor>/credentials.json` — not denied.
**Blast radius:** Operator file integrity.
**Likelihood:** Medium — the denylist is updated reactively (#15981 added `.env` of the root profile, per `agent/file_safety.py:39-44`).
**Hermes mitigation:** Denylist + optional `HERMES_WRITE_SAFE_ROOT` env var. The safe-root pattern is allowlist-instead-of-denylist (`agent/file_safety.py:78-103`).
**Would Ember inherit?** **The safe-root pattern, yes.** Ember's slice-2 already has read-only tools; when she adds write tools, the safe-root allowlist is the right shape. The denylist alone is a worse baseline.

---

## R-12 — `.env.example` config sprawl

**Category:** Operational
**Hermes source:** `.env.example` — 470 lines (23 KB), one `=` per line: 11 declared keys plus ~100 commented examples for optional providers.
**Trigger:** Operator missed an env var the agent silently requires for a specific feature. The feature degrades; no error.
**Blast radius:** Operator confusion → support load.
**Likelihood:** Medium for new users.
**Hermes mitigation:** `hermes setup` interactive flow; `hermes doctor` diagnoses common misconfig; per-feature error messages name the env var they expected.
**Would Ember inherit?** **No.** Ember's slice-2 has one config file (`~/.ember/config/ember.yaml`); the operator's `hermes setup`-equivalent is Hjarta. Per Vow of Public-Friendliness, env-var sprawl is the wrong shape. Keep Hjarta as the *only* configuration entry point for non-developers.

---

## R-13 — Last-writer-wins platform registry

**Category:** Security / Operational
**Hermes source:** `gateway/platform_registry.py:172-187`:

```python
if entry.name in self._entries:
    prev = self._entries[entry.name]
    logger.info(
        "Platform '%s' re-registered (was %s, now %s)",
        entry.name, prev.source, entry.source,
    )
self._entries[entry.name] = entry
```

**Trigger:** Two plugins register the same platform name. The second wins; operator sees a single log line.
**Blast radius:** Operational (wrong adapter used) or Security (a malicious plugin shadows a built-in).
**Likelihood:** Low — most platforms have unique names.
**Hermes mitigation:** Log entry; explicit comment that this is intentional ("lets plugins override built-in adapters if desired").
**Would Ember inherit?** **No.** Per [[20_interface/27_PLUGIN_INTERFACE]] proposal #3, duplicate registration is `LoadFailed`. Shadowing is never silent.

---

## R-14 — Memory tool name collision is silently dropped

**Category:** Correctness
**Hermes source:** `agent/memory_manager.py:285-296`. A tool name registered by two providers — only the first sticks.
**Trigger:** Two plugins ship a tool with the same name (`search_memory`, `recall`, `memory_get`).
**Blast radius:** Single tool absent; user sees "no such tool" if model calls the second.
**Likelihood:** Low.
**Hermes mitigation:** Warning log; first registration wins.
**Would Ember inherit?** **No.** Collision should be a load failure (or, if Ember chooses, a namespace-prefix policy: `provider_name/tool_name`).

---

## R-15 — Iteration budget shared imperfectly across delegation

**Category:** Operational
**Hermes source:** `agent/iteration_budget.py:31-62`. Each subagent gets its own independent budget; total iterations across parent + subagents can exceed the parent's cap.
**Trigger:** Parent at iter=80/90 delegates to a subagent. Subagent runs 50 iters. Total: 130.
**Blast radius:** Session — token / API cost.
**Likelihood:** Medium-High for users of delegate-style tools.
**Hermes mitigation:** Each budget is cap-limited; the *parent's* budget is consumed before delegation succeeds.
**Would Ember inherit?** **Ember has no delegation at slice 2.** If she ever does, the *aggregate* budget model is the correct shape, not per-agent.

---

## R-16 — Error classifier as the single point of recovery decision

**Category:** Correctness / Operational
**Hermes source:** `agent/error_classifier.py:1-90` (1,087 lines total). Determines retry / rotate / fallback / compress / abort.
**Trigger:** A new API error code lands that the classifier doesn't recognize (e.g. a new provider's 463 / "tier-throttled" code).
**Blast radius:** Session — wrong recovery action. A `should_compress=False` on a `context_overflow`-shaped error means infinite retries.
**Likelihood:** Medium when integrating new providers.
**Hermes mitigation:** Catch-all `unknown` reason with retry-with-backoff; tests pin individual provider error shapes.
**Would Ember inherit?** **The taxonomy, yes.** Ember's Funi/Strengr error returns already follow a typed-reason taxonomy. Extending it for retry decisions matches the pattern. The risk is naming completeness — every new provider needs new reason codes.

---

## R-17 — Hook handler import-side-effects run before any safety check

**Category:** Security
**Hermes source:** `gateway/hooks.py:115-122`. Discovery walks `~/.hermes/hooks/`; for each directory with a `HOOK.yaml` and `handler.py`, the handler is `exec_module`'d. There is no signature check, hash check, or sandboxing.
**Trigger:** An attacker who writes to `~/.hermes/hooks/` (compromised account, supply-chain in the install flow) drops a malicious `handler.py`.
**Blast radius:** Host. Arbitrary code execution with the agent's privileges.
**Likelihood:** Low under normal use; Hermes documents this as an in-scope expectation (`SECURITY.md:154-168` for plugins; same model applies to hooks).
**Hermes mitigation:** Documentation + operator review. *That is the boundary.*
**Would Ember inherit?** **Conditionally — and the boundary must be named.** If Ember supports hooks at all (per slice-3+ ADR), the contract is identical to plugins (per [[20_interface/27_PLUGIN_INTERFACE]]) — opt-in by config, manifest required, no auto-discovery without explicit operator action.

---

## R-18 — UTF-16 truncation as a non-uniform contract

**Category:** Correctness
**Hermes source:** `gateway/platforms/base.py:114-166`. The `utf16_len` / `_prefix_within_utf16_limit` pair is correct; it is *not* enforced by a type. Every send path must use it.
**Trigger:** A future maintainer adds a new send path and writes `message[:limit]`. Telegram rejects oversized; emoji at the boundary become `�`.
**Blast radius:** Per-message correctness.
**Likelihood:** Low if convention holds; rises with code churn.
**Hermes mitigation:** Existing code uses the helper consistently; tests pin the behavior.
**Would Ember inherit?** **The function pattern, yes; the discipline, replace with a type.** If Munnr ever has a max-length constraint, a `BoundedString` newtype that carries its limit is harder to violate than a function call convention.

---

## R-19 — Auth signature introspection at dispatch time

**Category:** Correctness
**Hermes source:** `agent/memory_manager.py:511-535`. `MemoryManager` introspects each provider's `on_memory_write` signature at runtime to decide whether to pass metadata as keyword, positional, or omit. Three modes; signature change silently flips a plugin into a different mode.
**Trigger:** A plugin author reorders or renames a parameter.
**Blast radius:** Plugin behavior changes silently. Metadata lands in the wrong slot or is dropped.
**Likelihood:** Medium when plugin protocols evolve.
**Hermes mitigation:** None mechanical; review-time only.
**Would Ember inherit?** **No.** Per [[20_interface/27_PLUGIN_INTERFACE]] proposal #7, version the protocol; refuse non-conformant plugins. Signature introspection at dispatch is a backward-compat workaround that should not be born.

---

## What This Means for Ember

**Subsystems affected:** All six True Names — every risk above maps to at least one. Highest cluster: Brunnr/Smiðja (memory contracts), Munnr (gateway/surface), and *any future plugin surface*.

**Vows touched:** Every Vow except Open Knowledge has at least one risk on this register.

**Concrete next steps:**

1. **Carry this register forward.** Every risk above should appear in Ember's own ongoing risk inventory under `docs/` (alongside `UNWIRED_INVENTORY.md`). Re-audit quarterly.
2. **For each risk where the verdict is "would NOT inherit": confirm the design choice survives slice 3+.** Specifically R-04 (default hard-stop), R-05 (redact opt-out hardness), R-10 (plugin teardown lifecycle), R-12 (no env-var sprawl), R-13/R-14 (no silent shadowing/collision).
3. **For each risk where the verdict is "would inherit": confirm the mitigation is on the roadmap.** Specifically R-03 (streaming scrub), R-08 (snapshot-before-mutate), R-11 (safe-root), R-16 (typed error taxonomy completeness).
4. **For the security risks (R-02, R-05, R-06, R-11, R-17): mirror `SECURITY.md`'s discipline.** Name what is a boundary, name what isn't, name what's operator responsibility. Ember does not yet have a `SECURITY.md`; she needs one before any external surface ships.

Cross-link with [[50_verification/52_ANTIPATTERN_CATALOG]] (each risk often corresponds to a Hermes pattern), [[50_verification/54_SECURITY_REVIEW]] (deep-dive on the security cluster), and [[50_verification/55_INVARIANT_LIST]] (invariants that, if held, neutralize specific risks).

A risk register is a contract with future-Ember-developers: *we knew these existed; we chose what to do about each*. The contract is more important than the prevention.
