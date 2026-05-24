---
codex_id: 51_EMBER_GAP_ANALYSIS
title: Ember Gap Analysis — What She Lacks, Honestly
role: Auditor
layer: Verification
status: draft
hermes_source_refs:
  - agent/conversation_loop.py:1-100
  - agent/credential_pool.py:1-50
  - agent/error_classifier.py:22-90
  - agent/curator_backup.py:1-100
  - gateway/platform_registry.py:1-260
  - mcp_serve.py:1-50
  - SECURITY.md:1-50
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
cross_refs:
  - 50_verification/50_HERMES_RISK_REGISTER
  - 50_verification/54_SECURITY_REVIEW
  - 60_synthesis/61_TRUE_NAME_REASSIGNMENT
  - 60_synthesis/64_MIGRATION_PLAN
---

# Ember Gap Analysis — What She Lacks Compared to Hermes

*Sólrún, ledger in hand: honesty is the verifier's only currency. Ember is one working-day old as a slice-2 system. Hermes is a year and 14 releases old, written by ~200 contributors, with a budget I do not know. They are not peers. The question is not "is Ember smaller?" — she should be, by Vow. The question is "where does Ember's smallness cross from virtue into deficiency?" That line is where this analysis lives.*

For each gap I cite (a) a specific Hermes file/area, (b) the specific Ember file or its absence, (c) the cost to close it, and (d) whether closing it would *strengthen* or *erode* an Ember Vow. Vow-erosion is a refusal flag, not a price tag. Anything that erodes a Vow does not get closed at any cost.

I read the Ember code at:
- `src/ember/spark/funi/` — Funi runtime + adapter + tools
- `src/ember/spark/munnr/` — CLI surface
- `src/ember/spark/hjarta/` — first-run wizard
- `src/ember/thread/strengr/` — tether
- `src/ember/well/brunnr/` — storage adapter (sqlite_vec, pgvector)
- `src/ember/well/smidja/` — ingest forge (local_files only)
- `src/ember/tools/` — three tools (search_well, read_local_file, fetch_url)
- `src/ember/mcp/` — MCP scaffold (bridge.py, client.py, runner.py, server.py)
- `src/ember/plugins/` — empty per [[hermes_codex/../UNWIRED_INVENTORY]] §5.4
- `docs/SLICE_2_RETROSPECTIVE.md`
- `docs/UNWIRED_INVENTORY.md`

---

## Gap 1 — No multi-provider failover / credential rotation

**Hermes:** `agent/credential_pool.py` (1,955 LOC), `agent/error_classifier.py` (1,087 LOC), `agent/account_usage.py`, `agent/rate_limit_tracker.py`. Multiple credentials per provider; per-credential cooldown on 401/429/402; round-robin / fill-first / least-used strategies; persistent state at `~/.hermes/credential_pool.json`.

**Ember:** Single configured-provider-at-a-time. `src/ember/spark/funi/ollama/` connects to one Ollama. `src/ember/well/brunnr/pgvector/` connects to one Postgres. No rotation, no pool, no cooldown.

**Cost to close:** Medium-High. ~600 LOC for a stripped-down `CredentialHandle` registry, `RotatingFuniHandle` decorator, `Strengr.health()` integration. Bigger if the Brunnr handle also rotates.

**Vow compatibility:** **Compatible** with all Vows. Particularly aligned with Vow of Modular Authorship (a credential failure doesn't crash the agent). Particularly aligned with Vow of Smallness (per-credential cooldown means a Pi over a flaky tether can soldier on).

**Priority:** **Slice 4 or later.** Premature for slice 3 — operators on a Pi with a local Ollama and a local Gungnir don't need rotation yet. When Ember moves to mixed-provider configurations (a remote Gungnir *plus* a paid LLM API), the gap matters.

---

## Gap 2 — No typed error classifier for API/network failures

**Hermes:** `agent/error_classifier.py:22-90` — `FailoverReason` enum with ~20 reasons (auth, billing, rate_limit, overloaded, server_error, timeout, context_overflow, payload_too_large, image_too_large, model_not_found, format_error, thinking_signature, long_context_tier, oauth_long_context_beta_forbidden, llama_cpp_grammar_pattern, unknown). Each carries `retryable: bool`, `should_compress: bool`, recovery hints.

**Ember:** `src/ember/well/brunnr/` has eight typed `Disconnected` reasons per ADR 0007 §2.2; `src/ember/spark/funi/handle.py` returns `Unavailable`; `src/ember/spark/funi/` returns `FuniReply(finish_reason=ERROR)` on adapter error. The typed-value discipline is in place. The *enumeration* is small.

**Cost to close:** Low-Medium. ~200 LOC to expand the reason taxonomy and wire retry-with-backoff into Strengr. Mostly enumeration work, not architecture.

**Vow compatibility:** **Strengthens** Vow of Graceful Offline (more granular degraded states), **Strengthens** Vow of Honest Memory (the operator knows *why*).

**Priority:** **Slice 3.** When Ember adds her second Funi runtime (lmstudio? llama.cpp?) the missing reasons become user-facing bugs. Get the enum extended now while only one runtime exists.

---

## Gap 3 — No prompt caching / context engine

**Hermes:** `agent/prompt_caching.py`, `agent/context_engine.py`, `agent/context_compressor.py`. Anthropic prompt-cache support; context engine batches references; compressor summarizes when context overflows.

**Ember:** None of this. The Funi prompt is reassembled per turn (`src/ember/spark/funi/prompt.py`). Context overflow is not yet a problem because Ember's small models have small context.

**Cost to close:** Medium. Prompt caching is provider-specific (Anthropic / Bedrock / Ollama have different caching contracts). Compression requires a *summary model* call, which compounds API cost.

**Vow compatibility:** **Compatible** with Vow of Smallness (compression saves tokens) but **strains** it (running a summary call adds latency on a Pi). Aligned with Vow of Honest Memory only if the operator knows context was compressed.

**Priority:** **Defer until slice 4+.** A Pi with `phi3:mini` or `llama3.2:3b` is constrained by *latency*, not context window. Hermes does this because Anthropic Opus has a 1M-token cache and Hermes wants to use it. Ember's operator doesn't yet have that problem.

---

## Gap 4 — No procedural memory (skills)

**Hermes:** `skills/` + `optional-skills/` — autonomous-ai-agents, blockchain, communication, creative, devops, email, finance, health, mcp, migration, mlops, productivity, research, security, software-development, web-development. Curator pass auto-creates skills from experience (`agent/curator.py`, `agent/curator_backup.py`). Skills hub at agentskills.io.

**Ember:** Nothing. Procedural memory is not a slice-2 or slice-3 concept.

**Cost to close:** High. Auto-creating skills requires (a) a skill manifest format, (b) a curator pass with snapshot/rollback infrastructure, (c) hub discovery / install, (d) safety review per `SECURITY.md:148-153`.

**Vow compatibility:** **Strains** Vow of Smallness — every skill is RAM + import-time cost. **Strains** Vow of Honest Memory if skills synthesize confidently from thin evidence. **Compatible** with the right design, dangerous with the wrong one.

**Priority:** **Slice 5+ at earliest, possibly never.** Ember's smallness implies she leans on the Well for knowledge, not on procedural skills. If skills land, they land as static, operator-reviewed bundles — never auto-created.

---

## Gap 5 — No gateway / no external surface

**Hermes:** `gateway/` (22+ platforms), `gateway/platform_registry.py`, `acp_adapter/`, `mcp_serve.py`.

**Ember:** CLI only. `src/ember/spark/munnr/chat.py` is the operator's interface. ADR 0012 reserves Bifröst as the slice-3 HTTP gateway placeholder; not ratified.

**Cost to close:** Very High. A full multi-platform gateway is hundreds of files. Even a *single-platform* (HTTP-only) Bifröst is ~1000 LOC of careful auth, allowlist, rate-limit, replay-protect work.

**Vow compatibility:** **Bifröst-as-HTTP**: compatible. **Multi-platform messaging**: erodes Vow of Public-Friendliness (now the operator has to set up Telegram bot tokens) and strains Vow of Smallness (more dependencies). Telegram/Discord adapters specifically are not in the Pi-friendly story.

**Priority:** **Bifröst-as-HTTP is slice 3+** per ADR 0012. **Multi-platform messaging is out of Ember's identity** — it's a Hermes role. If an operator wants Telegram, point them at Hermes or write a thin bridge.

---

## Gap 6 — No MCP server / no advanced MCP integration

**Hermes:** `mcp_serve.py` (31 KB) lets Hermes be both an MCP client *and* an MCP server. Tools register; clients consume.

**Ember:** `src/ember/mcp/` has `bridge.py`, `client.py`, `runner.py`, `server.py` — but per UNWIRED_INVENTORY this is scaffold-stage, and `ember mcp list/tools/ping/serve --transport` flags are wired but the actual integration depth is shallow.

**Cost to close:** Medium-High. Real MCP server work means careful tool registration, manifest export, transport hardening (stdio + WebSocket + SSE).

**Vow compatibility:** **Compatible** with all Vows if implemented small. MCP is a protocol-level integration; nothing in MCP requires a GPU.

**Priority:** **Slice 3 wishlist.** MCP-as-client is more valuable than MCP-as-server initially. Let third-party MCP tools augment Ember; only later expose Ember-as-tool to other agents.

---

## Gap 7 — No streaming context scrubber / no streaming output sanitizer

**Hermes:** `agent/memory_manager.py:62-224` (`StreamingContextScrubber`), `agent/think_scrubber.py` (`StreamingThinkScrubber`). State machines that handle `<memory-context>` and `<think>` tags across stream chunk boundaries.

**Ember:** Funi streams (slice-2 §"Streaming Funi replies"), but the stream is raw text — no inline tag scrubbing. Ember does not yet inject memory blocks into the model's context, so the leak surface doesn't exist *yet*.

**Cost to close:** Low. ~150 LOC of careful state machine, lifted directly from Hermes with attribution. Tests are the hard part.

**Vow compatibility:** **Strengthens** Vow of Honest Memory (recalled context never bleeds into output). Compatible with Smallness.

**Priority:** **Slice 4** when Ember adds context injection for the Well. Until then, the scrubber has nothing to scrub.

---

## Gap 8 — No iteration budget / no tool-call guardrails

**Hermes:** `agent/iteration_budget.py:1-62`, `agent/tool_guardrails.py:1-475`. Per-agent iteration cap; per-turn repeat-call detection; hard-stop on `N` exact failures.

**Ember:** Tool framework shipped (slice-2 ADR 0011) but no iteration budget, no loop detection. A model that retries the same tool 20 times is bounded only by the operator pressing Ctrl-C.

**Cost to close:** Low. ~100 LOC for `IterationBudget` + ~300 LOC for guardrail controller (pattern from `agent/tool_guardrails.py`).

**Vow compatibility:** **Strengthens** Vow of Smallness (Pi compute budget is real). **Strengthens** Vow of Public-Friendliness (the operator doesn't watch a 20-iteration loop).

**Priority:** **Slice 3.** This is a small, high-value addition. The pattern is well-formed in Hermes; lift with attribution.

---

## Gap 9 — No redaction of secrets in logs

**Hermes:** `agent/redact.py` (467 LOC). Vendor-prefix patterns (sk-, ghp_, ghs_, AIza..., xai-...), env-assignment patterns, JSON-field patterns, Authorization headers, JWT, private keys, DB connstrings, URL query params with sensitive names, URL userinfo, Telegram bot tokens, Discord snowflake mentions, E.164 phone numbers.

**Ember:** Slice-2 logs go through `src/ember/logging.py`. No automatic redaction; the operator must avoid putting secrets in places that get logged. The audit-log JSONL files (slice-2 §"audit logs") *could* leak.

**Cost to close:** Low-Medium. ~300 LOC for the redactor + a `RedactingFormatter` for logging. The Hermes pattern list is portable.

**Vow compatibility:** **Strengthens** Vow of Open Knowledge (the operator can paste logs into a bug report). **Strengthens** Vow of Public-Friendliness.

**Priority:** **Slice 3.** Bidirectionally important — operator pastes logs and the agent-emitted secrets in logs are both risks.

---

## Gap 10 — No `SECURITY.md`

**Hermes:** `SECURITY.md` (332 lines). Trust model, boundary statement, scope (in/out), credential scoping rules, plugin trust model, external-surface allowlist rules.

**Ember:** No `SECURITY.md`. The Vows imply some of it; `docs/security/` exists but has no policy doc that names the boundary.

**Cost to close:** Low (writing time). High (deciding time). Naming a security boundary is committing to it.

**Vow compatibility:** **Strengthens** all Vows. **Required** for any external surface (Bifröst) — until Ember has a security policy, she has no defensible position when something inevitably gets reported.

**Priority:** **Before slice 3.** Bifröst cannot ship without it. Recommend the Auditor draft slice-3-blocking, before any other slice-3 work.

---

## Gap 11 — No write-safety denylist / no safe-root allowlist for tools

**Hermes:** `agent/file_safety.py:28-104`. Denylist (.ssh, .aws, .gnupg, /etc/sudoers, etc.) + `HERMES_WRITE_SAFE_ROOT` env-var allowlist.

**Ember:** No write tools yet (per ADR 0013 §3 deferral list). `fetch_url`, `read_local_file`, `search_well` are read-side. When write-side tools land, the file-safety question becomes load-bearing.

**Cost to close:** Low. ~150 LOC for safe-root allowlist + denylist of obvious paths. Lift the `is_write_denied` logic directly.

**Vow compatibility:** **Strengthens** Vow of Modular Authorship (a write tool is failable, not catastrophic).

**Priority:** **Slice 4+** alongside the first write tool. Block the write tool on this landing — no write tool ships without a safe-root.

---

## Gap 12 — No process-level crash-proofing

**Hermes:** `agent/process_bootstrap.py:63-110` (`_SafeWriter` wraps stdout/stderr to swallow broken-pipe errors); `tui_gateway/entry.py:65-162` (SIGPIPE-ignore + signal-logging + grace-window + os._exit fallback).

**Ember:** Slice-2 Ember runs synchronously and does not subprocess. `_SafeWriter`-equivalent is unnecessary *while* Ember is single-process.

**Cost to close (if needed):** Low. The patterns lift directly.

**Vow compatibility:** Compatible.

**Priority:** **When Ember first subprocesses.** If Bifröst becomes a subprocess (per `/home/volmarr/ai/ai/ingest-viewer` integration with bifrost-viewer per UNWIRED_INVENTORY §3), apply at the same time.

---

## Gap 13 — No multi-credential / failover / cooldown for the Well

**Hermes:** Treats the Anthropic API as a pool. The Well (any external storage) is not pooled in Hermes either — Ember would be the first to formalize.

**Ember:** `BrunnrHandle` returns `Disconnected(reason)` per typed-value rule; Strengr's retry policy reads the reason. There is no concept of "try the *second* configured Brunnr." Ember either has a connected pgvector or she does not.

**Cost to close:** Medium. ~400 LOC for a `BrunnrPool` with the same `health() → ready/degraded/down` shape; ~150 LOC for Munnr to render multi-Well state.

**Vow compatibility:** **Strengthens** Vow of Graceful Offline. **Compatible** with Vow of Pluggable Storage.

**Priority:** **Slice 4+.** Slice-3 operators will have one Brunnr. The pool is for the multi-Well operator (a household Gungnir + a Pi-local sqlite_vec).

---

## Gap 14 — No "stance"-style document for output rendering

**Hermes:** `SECURITY.md:240-243` introduces "stance" — a documented expectation that consuming layers (dashboard, gateway adapter, file writer, shell) render agent output a specific way. Stance violations are in-scope under §3.1.

**Ember:** No stance doc. Munnr renders agent output as text in a terminal; the assumption is implicit.

**Cost to close:** Low (writing time).

**Vow compatibility:** **Strengthens** every Vow that touches output.

**Priority:** **Before slice 3.** A few paragraphs in `docs/security/STANCE.md` (or a section in the new `SECURITY.md`). Names what Ember promises about her own output.

---

## Gap 15 — No invariant doc / no testing-strategy doc

**Hermes:** Has a sprawling test tree (24+ subdirectories under `tests/`). Lacks a unified invariant or testing-strategy document. Each ADR carries some.

**Ember:** Slice-2 has 488 tests organized roughly. Per UNWIRED_INVENTORY there is no invariant doc; the closest is the SYSTEM_VISION §11 (Vows-Fulfilled Postscript) which lists *mechanical enforcements* per Vow.

**Cost to close:** Low (writing time). [[50_verification/55_INVARIANT_LIST]] and [[50_verification/56_TESTING_STRATEGY]] are exactly this; they sit alongside this gap analysis.

**Vow compatibility:** Strengthens all Vows.

**Priority:** **Already in flight in this Codex.**

---

## Gap 16 — No subagent / no delegation

**Hermes:** `agent/delegate_task` tool, subagent iteration budgets, parent-child memory awareness via `on_delegation`.

**Ember:** None. Single-agent only.

**Cost to close:** Very High. Delegation is a discrete capability with its own design surface; ADR-worthy.

**Vow compatibility:** **Strains** Vow of Smallness (more concurrent state, possibly more concurrent Ollama calls saturating Pi RAM). Could be **incompatible** at the Pi-5 target.

**Priority:** **Out of scope.** Ember is the small one. Delegation is a Runa-shaped concept; Ember calls Runa, not the other way around.

---

## Gap 17 — No trajectory / training data export

**Hermes:** `trajectory_compressor.py` (65 KB), `batch_runner.py` (57 KB). Generates training data from agent runs.

**Ember:** None.

**Cost to close:** N/A — it is not a thing Ember should do.

**Vow compatibility:** **Erodes** Vow of Public-Friendliness (the operator is now a data subject). **Strains** Vow of Open Knowledge unless the export is operator-controlled and operator-owned.

**Priority:** **Out of scope, period.** This is Hermes-Nous's role — they are a model-training organization. Ember is a small, tethered agent. The two needs are different.

---

## Summary table

| # | Gap | Vow effect | Priority |
|---|---|---|---|
| 1 | Multi-provider failover | Compatible (+Modular Authorship) | Slice 4+ |
| 2 | Typed error classifier expansion | Strengthens (Graceful Offline, Honest Memory) | **Slice 3** |
| 3 | Prompt caching / context engine | Strains (Smallness) | Slice 4+ |
| 4 | Procedural memory (skills) | Strains (Smallness, Honest Memory) | Slice 5+ / maybe never |
| 5 | Gateway / external surface | Multi-platform erodes; Bifröst-HTTP compatible | Bifröst = slice 3+ |
| 6 | MCP server depth | Compatible | Slice 3 wishlist |
| 7 | Streaming scrubbers | Strengthens (Honest Memory) | Slice 4 |
| 8 | Iteration budget / tool guardrails | Strengthens (Smallness, Public-Friendliness) | **Slice 3** |
| 9 | Log redaction | Strengthens (Open Knowledge, Public-Friendliness) | **Slice 3** |
| 10 | SECURITY.md | Strengthens all | **Before slice 3** |
| 11 | Write-safety denylist / safe-root | Strengthens (Modular Authorship) | Block first write tool |
| 12 | Process crash-proofing | Compatible | When subprocessing arrives |
| 13 | Multi-Well failover | Strengthens (Graceful Offline) | Slice 4+ |
| 14 | Stance doc | Strengthens all | **Before slice 3** |
| 15 | Invariant + testing-strategy docs | Strengthens all | **In this Codex** |
| 16 | Subagent / delegation | Strains-to-incompatible | Out of scope |
| 17 | Trajectory export | Erodes (Public-Friendliness) | Out of scope |

---

## What This Means for Ember

**Subsystems affected:** Every True Name has at least one gap.

**Vows touched:** The honest tension is between *Vow of Smallness* and *every other Vow*. A small system has less surface area to harden; a hardened system needs more code. The right answer is selective enrichment — pick the gaps that strengthen multiple Vows, defer those that strengthen one Vow at the cost of another.

**Concrete next steps for slice 3:**

1. **Authoring blockers**: `SECURITY.md` (Gap 10), `STANCE.md` (Gap 14), the invariant + testing-strategy docs (Gap 15). These are *writing* tasks; they cost time, not architecture.
2. **Code blockers**: typed-error taxonomy expansion (Gap 2), iteration-budget + tool-guardrails (Gap 8), log redaction (Gap 9). Each is ~200-400 LOC; each maps directly to a Hermes pattern; each strengthens multiple Vows.
3. **Defer with confidence**: credential rotation (Gap 1), prompt caching (Gap 3), multi-Well failover (Gap 13). Operators on the slice-3 target hardware do not need these yet.
4. **Refuse with confidence**: subagent (Gap 16), trajectory export (Gap 17), auto-created skills (Gap 4 in its auto-creation form). These are not Ember's identity.

Cross-link with [[50_verification/50_HERMES_RISK_REGISTER]] (each gap closure often retires a risk) and [[60_synthesis/64_MIGRATION_PLAN]] (the Cartographer's sequencing).

The gaps that close are paid for in Vow alignment. The gaps that stay open are kept open by Vow honoring. Both should be loud.
