---
codex_id: 57_FAILURE_TAXONOMY
title: Failure Taxonomy — Ranked By Impact × Likelihood, With Ember-Applicability
role: Auditor
layer: Verification
status: draft
sap_source_refs:
  - py/custom_http.py:11
  - py/comfyui_tool.py:62-67,212-214
  - py/cdp_tool.py:140-155,275-285
  - py/GeminiAsOpenAI.py:65-69
  - py/know_base.py:222-230,235-239
  - py/behavior_engine.py:85-88,184-187
  - py/live_router.py:21-27
  - py/affection_system.py:48
  - py/twitch_service.py:65-68
  - py/dify_openai.py:60-64
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
cross_refs:
  - 50_verification/50_SELF_HEALING_PATTERNS
  - 50_verification/51_CRASH_RESISTANCE
  - 50_verification/53_SECURITY_REVIEW
  - 50_verification/55_API_SIMULATION_TRAPS
  - 50_verification/56_PRIVACY_BOUNDARIES
---

# Failure Taxonomy — Ranked By Impact × Likelihood, With Ember-Applicability

> *Sólrún, voice cold and even: this is the master table. Every failure mode I have named in this codex appears here, ranked by impact × likelihood, with one explicit column: does Ember inherit this failure mode? The table is the load-bearing artifact of the verification layer — if the operator reads only one of my docs, this is the one.*

This document is the consolidated table. It does *not* re-derive the failures; it references the docs that catalog them. The format is: failure mode, where in SAP, impact rating (1-5), likelihood (1-5), Ember-applicable (Yes/Partial/No), Vow that addresses it.

Impact rating:
- **1** — annoyance; user notices, no data loss
- **2** — feature outage; restart fixes
- **3** — data loss in one subsystem
- **4** — credential exposure; widespread feature outage
- **5** — RCE, physical-world consequence, or full credential trove loss

Likelihood rating:
- **1** — requires very specific conditions
- **2** — happens in unusual configurations
- **3** — happens on a typical Tuesday
- **4** — happens on every flake
- **5** — happens on every call of the affected path

---

## 1. The Master Failure Table

| # | Failure | Where | Impact | Likelihood | I×L | Ember? | Vow |
|---|---|---|---|---|---|---|---|
| **F-01** | Pickle RCE via FAISS index file replacement | `know_base.py:228` `allow_dangerous_deserialization=True` | 5 | 2 | 10 | Yes | Cache Discipline + Defended SP |
| **F-02** | Credential leak via `os.environ` mutation | `GeminiAsOpenAI.py:65-69` | 5 | 4 | 20 | Yes | Defended System Prompt |
| **F-03** | SSRF / private-network exfil via `custom_http` | `custom_http.py:11-41` | 5 | 3 | 15 | Yes | Surface Without Surveillance |
| **F-04** | Local sandbox code-exec without auth | `code_interpreter.py:24-39` | 5 | 2 | 10 | Yes | Surface Without Surveillance |
| **F-05** | MCP server config = arbitrary subprocess (via unauth localhost API) | `mcp_clients.py:33-42` + unauth FastAPI | 5 | 3 | 15 | Yes | Defended System Prompt |
| **F-06** | `evaluate_script` → operator-session cookie exfil | `cdp_tool.py:261-288` | 5 | 3 | 15 | Yes | Surface Without Surveillance |
| **F-07** | Home Assistant prompt-injection → physical control | `settings_template.json:240-244` | 5 | 2 | 10 | Partial | Affective Restraint + new |
| **F-08** | Affection memory poisoning via livestream | `affection_system.py` + `live_router` | 4 | 3 | 12 | Yes | Tethered Forgetting + new |
| **F-09** | Settings.json plain-text credential trove | `get_setting.py:75-80` | 4 | 5 | 20 | Yes | Cache Discipline |
| **F-10** | ComfyUI hang blocks main event loop | `comfyui_tool.py:62-67` | 4 | 3 | 12 | Yes | Smallness + new |
| **F-11** | ComfyUI server allocation race | `comfyui_tool.py:125-141` | 3 | 3 | 9 | No | (Ember doesn't ship this) |
| **F-12** | ComfyUI workflow path-traversal | `comfyui_tool.py:145-149` | 3 | 2 | 6 | No | — |
| **F-13** | BM25 silent fallback to vector | `know_base.py:235-239` | 3 | 4 | 12 | Yes | Cache Discipline |
| **F-14** | Behavior engine timer reset on platform register | `behavior_engine.py:85-88` | 2 | 4 | 8 | Yes | Modular Authorship |
| **F-15** | Livestream module-globals lie about state | `live_router.py:21-27` | 2 | 4 | 8 | Yes | Modular Authorship |
| **F-16** | Display-name as identity for affection | `affection_system.py:48` | 3 | 4 | 12 | Yes | new |
| **F-17** | Cross-platform identity bleed | affection + memory | 3 | 4 | 12 | Yes | new |
| **F-18** | Dify multi-turn lobotomy (last-message-of-role wins) | `dify_openai.py:60-64` | 3 | 4 | 12 | Yes | Defended System Prompt |
| **F-19** | Bare `except:` swallows everything (~30 spots) | various | 2 | 5 | 10 | Yes | Public-Friendliness |
| **F-20** | `print()` of secrets to stdout | `custom_http.py:36-38`, `cdp_tool.py` | 4 | 4 | 16 | Yes | Cache Discipline |
| **F-21** | Twitch OAuth token leak via anonymous-nick combo | `twitch_service.py:65-68` | 4 | 5 | 20 | Yes | Defended System Prompt |
| **F-22** | `asyncio.create_task` without done callback (fire-and-forget) | scheduler, behavior_engine, live_router | 2 | 5 | 10 | Yes | Modular Authorship |
| **F-23** | Sub-agent task stuck RUNNING after launch failure | `scheduler.py:108-115` | 3 | 2 | 6 | Yes | new |
| **F-24** | Behavior engine tick partial-mutation | `behavior_engine.py:184-187` | 2 | 3 | 6 | Yes | new |
| **F-25** | YouTube polling spam on bad credential | `ytdm.py:55-61` | 1 | 4 | 4 | Yes | Graceful Offline |
| **F-26** | Dify no `usage` in response | `dify_openai.py:94-106` | 2 | 5 | 10 | Yes | Defended System Prompt |
| **F-27** | Claude cache-token loss in `usage` | `ClaudeAsOpenAI.py:206` via LiteLLM | 2 | 4 | 8 | Yes | Defended System Prompt |
| **F-28** | Tool drop in Claude tool conversion (unsupported types) | `ClaudeAsOpenAI.py:106-118` | 3 | 3 | 9 | Yes | Defended System Prompt |
| **F-29** | `evaluate_script` AI-sloppy-input janitor obscures LLM errors | `cdp_tool.py:265-273` | 2 | 4 | 8 | Yes | Public-Friendliness |
| **F-30** | Electron error-string match brittle to upgrade | `cdp_tool.py:142` | 2 | 2 | 4 | No | — |
| **F-31** | KB build partial (BM25 + vector inconsistency) | `know_base.py:127-194` | 3 | 3 | 9 | Yes | Cache Discipline |
| **F-32** | FAISS load + embedding model mismatch (silent) | `know_base.py:218-230` | 3 | 3 | 9 | Yes | Cache Discipline |
| **F-33** | Image re-hosting to operator GitHub without user consent | `settings_template.json:577-587` | 4 | 3 | 12 | No | (Ember doesn't ship) |
| **F-34** | Memory cache unbounded growth | `MEMORY_CACHE_DIR` | 2 | 4 | 8 | Yes | Cache Discipline |
| **F-35** | `uploaded_files/` unbounded growth | `UPLOAD_FILES_DIR` | 2 | 5 | 10 | Yes | Cache Discipline |
| **F-36** | Reasoning visibility default-`true` on multi-user platforms | `settings_template.json:536,547` | 3 | 5 | 15 | Yes | new |
| **F-37** | Affection per-platform race on read-modify-write | `affection_system.py:55-64` | 3 | 3 | 9 | Yes | new |
| **F-38** | Vendored `blivedm/` is frozen, no upstream sync | `py/blivedm/` | 2 | 3 | 6 | Yes | Modular Authorship |
| **F-39** | Single 30s startup timeout for all bots | per-platform bot managers | 1 | 4 | 4 | Yes | Public-Friendliness |
| **F-40** | Random Topic external service privacy leak | `settings_template.json:74` | 2 | 3 | 6 | No | (don't ship) |
| **F-41** | Web search engine choice — no least-privacy default | `settings_template.json:118-150` | 2 | 4 | 8 | Yes | Surface Without Surveillance |
| **F-42** | Snake_case vs camelCase field inconsistency | per-bot configs | 1 | 5 | 5 | Yes | Public-Friendliness |
| **F-43** | LangChain churn breakage on minor bump | `langchain-*` deps | 3 | 3 | 9 | Yes | Modular Authorship |
| **F-44** | LiteLLM stream-shape drift between versions | `litellm` dep | 3 | 3 | 9 | Yes | Defended System Prompt |
| **F-45** | MCP pre-stable spec churn | `mcp` dep | 3 | 4 | 12 | Yes | Modular Authorship |
| **F-46** | `pypdf2` legacy malformed-PDF CVEs | `pypdf2` dep | 4 | 2 | 8 | Yes | Modular Authorship |
| **F-47** | `edge-tts` reverse-engineering breaks on MS endpoint change | `edge-tts` dep | 2 | 3 | 6 | Yes | Graceful Offline |
| **F-48** | mem0 pinned-exactly-1.0.0 missing updates | `mem0ai==1.0.0` | 2 | 4 | 8 | Yes | Modular Authorship |
| **F-49** | WeChat stdout-interceptor pattern (cross-contamination) | `wechat_bot_manager.py:33-57` | 2 | 2 | 4 | No | (don't ship) |
| **F-50** | Cross-loop calls on shared globals (affection from per-platform loops) | `affection_system.py` + 8 bots | 3 | 3 | 9 | Yes | new |

50 failure modes. Six rated I×L ≥ 15: F-02, F-03, F-05, F-06, F-09, F-20, F-21, F-36 (and F-08 / F-18 at 12).

The top failures all share two properties: **(a) they cross security or privacy boundaries**, and **(b) they are easy to trigger**. The intersection of "this could leak credentials" and "this happens whenever a feature is used" is where the most Ember-relevant teaching lives.

---

## 2. Failures Ember Does Not Inherit

Several SAP failures are SAP-specific (because the architectural choice that produces them is the choice Ember rejects):

- **F-11, F-12** (ComfyUI server allocation, path traversal) — Ember does not ship a ComfyUI tool surface. Image gen is delegated, not bundled.
- **F-30** (Electron error-string match) — Ember is not Electron-bound; its UI is its own thing.
- **F-33** (image re-hosting to GitHub) — not in scope for Ember.
- **F-40** (Random Topic external) — not in scope.
- **F-49** (WeChat stdout interceptor) — Ember's WeChat path, if it ships, uses native SDK callback, not stdout interception.

The fact that ~5 of 50 failures are "doesn't apply" is itself a positive signal: Ember's deliberate-non-features avoid concrete failure modes.

---

## 3. Failures Where Ember Must Invent (No Existing Hermes Vow Suffices)

Several failures are not covered by any pre-existing Vow. The codex marks them with **new** in the Vow column:

- **F-07** Smart-home prompt injection — needs a **Physical-World Gating Vow** (operator approval per command for physical effects)
- **F-08** Memory poisoning via livestream — needs **Tethered Forgetting** Vow + **Inbound Surface Sanitizer** pattern
- **F-10** ComfyUI hang blocks loop — needs **Bounded Polling Discipline** (no `time.sleep` in async paths)
- **F-16, F-17, F-37** Identity-related — needs **Identity Provenance Tag** + **Per-Platform Identity Boundary**
- **F-23** Sub-agent stuck — needs **Task Witness with Done Callback Hook**
- **F-24** Tick partial mutation — needs **Tick Crash Isolation Wrapper**
- **F-36** Reasoning visibility default — needs **Per-Platform Reasoning Default Policy**
- **F-50** Cross-loop shared state — needs **State Ownership Discipline** (or singletons forbidden)

These eight are concentrated in the privacy and concurrency axes. They are also the most distinctive Ember inventions.

---

## 4. The Distribution of Failures by Axis

Counting failures by category:

| Axis | Count | Highest-impact |
|---|---|---|
| Security / credentials | 11 | F-01, F-02, F-03, F-05, F-06 (all I=5) |
| Privacy / identity | 8 | F-08, F-09, F-16, F-17, F-33, F-36 |
| Concurrency / state | 9 | F-10, F-22, F-37, F-50 |
| Self-healing / restart | 5 | F-23, F-24, F-25 |
| Observability | 4 | F-19, F-20, F-26 |
| Dependency churn | 6 | F-43, F-44, F-45, F-46, F-47, F-48 |
| API simulation fidelity | 5 | F-18, F-26, F-27, F-28, F-44 |
| UX / configuration drift | 2 | F-39, F-42 |

The two heaviest axes are **security/credentials** and **concurrency/state**. These are the two axes where Ember inherits the most pressure to invent rather than adopt.

---

## 5. The Compounded Failures

Several failures combine to produce worse-than-sum effects:

- **F-09 + F-02 + F-03** — settings credentials + env mutation + arbitrary HTTP = "exfil the entire credential trove on one prompt injection"
- **F-08 + F-09** — memory poisoning + persistent credentials = "the false memory persists across restarts and unlocks the same credential surface every session"
- **F-07 + F-03** — Home Assistant + custom_http = "physical-world control AND data exfiltration channel"
- **F-19 + F-20** — bare except + print to stdout = "after a credential leak, no log trail to investigate"

The compound failures are why Ember's Vows are *layered*: each Vow blocks at least one link in the chain.

---

## 6. The Pattern: Five Categories of Root Cause

Across the 50 failures, the root causes cluster into five categories:

1. **Trust the LLM** — `custom_http`, `cli_tool`, `evaluate_script`, all the unguarded tool surfaces. 12 failures.
2. **Module-level globals** — `live_router` globals, `running_comfyuiServers`, `CURRENT_SCREEN_REGION`, `behavior_engine` singleton. 8 failures.
3. **Silent fallback** — BM25 → vector, missing models → empty list, broken tool → fall through. 7 failures.
4. **`print()` as logging** — repeated across 35+ files. Foundational. 4 failures with this as primary cause; many others amplified.
5. **Pre-stable dep churn** — LangChain, MCP, mem0, fastapi-mcp, all moving targets. 6 failures.

Address these five and Ember rejects ~75% of SAP's failure modes by construction.

---

## 7. Cross-References

- [[50_SELF_HEALING_PATTERNS]] — what survives the failures in this table
- [[51_CRASH_RESISTANCE]] — per-subsystem crash mapping
- [[53_SECURITY_REVIEW]] — STRIDE for the security-axis failures
- [[55_API_SIMULATION_TRAPS]] — API fidelity failures
- [[56_PRIVACY_BOUNDARIES]] — privacy failures
- [[58_OBSERVABILITY_GAPS]] — why most of these failures cannot be diagnosed
- [[60_synthesis/57_FAILURE_TAXONOMY]] would have been the synthesis target, but I am the Auditor and the table lives here
- [[hermes:HEM-50_HERMES_RISK_REGISTER]] — Hermes's risk register

---

## What This Means for Ember

**Adopt:**
- Adopt the **Hermes risk register pattern** (referenced at [[hermes:HEM-50_HERMES_RISK_REGISTER]]) verbatim, then extend with these 50 SAP-specific entries. The register lives in Ember's repo and is updated on every PR that affects a tracked failure mode.

**Adapt:**
- Adapt the table format here into a **continuously maintained** Ember risk register. New failures append; resolved failures move to a "resolved with reference" section. CI verifies every Vow's "new" failure has a corresponding test.

**Avoid:**
- *(this doc's role is taxonomy, not avoidance — see the per-failure source docs for the Avoid lists)*

**Invent:**
- **Risk Register as Code.** Ember's risk register is a `risks.yaml` checked into the repo. Each entry has: id, name, source-ref (file:line in upstream codebase if applicable), impact, likelihood, vow-addressed, test-ref (Ember test that proves the Vow holds). PR templates require updating relevant entries. Eyes-on-failure becomes structural.
- **Compound-Failure Detector.** A static-analysis pass that looks for code paths combining unguarded surfaces (e.g. `custom_http` + a tool that reads credentials in the same context). Flags compound-failure risk before runtime. SAP would have caught F-09+F-02+F-03 with this.
- **Vow Coverage Report.** For every Vow Ember declares, the report enumerates: which failure modes the Vow blocks, which tests verify it, which subsystems implement it. Operators read the report to understand Ember's stance.
- **Failure-Mode Test Battery.** Each failure-mode entry in `risks.yaml` has a corresponding test in `tests/risks/test_RISK_<id>.py` that *attempts* the failure and asserts it is blocked. The test suite is the live proof.

The Failure Taxonomy is the bridge from "we found bugs in SAP" to "Ember structurally cannot have those bugs." Without this table, the codex would be 16 lectures; with this table, the codex is a *contract*.
