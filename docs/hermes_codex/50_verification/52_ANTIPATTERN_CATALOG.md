---
codex_id: 52_ANTIPATTERN_CATALOG
title: Antipattern Catalog — Hermes Habits Ember Must Refuse
role: Auditor
layer: Verification
status: draft
hermes_source_refs:
  - cli.py:1-50
  - .env.example:1-50
  - agent/memory_manager.py:325-609
  - gateway/platform_registry.py:172-187
  - hermes_cli/plugins.py:128-168
  - agent/memory_manager.py:511-535
  - gateway/hooks.py:115-122
  - agent/redact.py:60-67
  - SECURITY.md:154-168
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
cross_refs:
  - 50_verification/50_HERMES_RISK_REGISTER
  - 50_verification/55_INVARIANT_LIST
  - 60_synthesis/63_INTEGRATION_PATHS
  - 00_vision/03_ANTI_HERMES
---

# Antipattern Catalog — Patterns Ember Must NOT Adopt

*Sólrún, hand on the door: this is the room where I keep what should not be touched. Hermes is admirable in a hundred ways. The Codex spends most of its breath naming what to lift. This document is the inverse: what to leave behind. Each entry names a specific Hermes pattern, cites where it lives, and says exactly why it is wrong for Ember — not wrong in general, wrong **for Ember**. The Vows are the test.*

---

## A-01 — The 662-KB CLI

**Where in Hermes:** `cli.py` — 662 KB single file. `run_agent.py` is 180 KB, `hermes_state.py` 140 KB.

**The pattern:** Monolithic single-file growth. The TUI, command surface, and command-handlers live together in one file that no one will ever read end-to-end.

**Why it is an antipattern *for Ember specifically*:** Vow of Public-Friendliness asks that the code be readable by non-developers. Vow of the Unbroken Whole asks for files to be delivered whole. A 662-KB file is whole only in the most degenerate sense — it is also unreviewable. A bug in line 41,000 will not be caught by a reviewer.

**What Ember should do instead:** `src/ember/spark/munnr/` is already correctly decomposed — `chat.py`, `ask.py`, `ingest.py`, `setup.py`, `doctor.py`, `status.py`, `render.py`. Keep it that way. **Set a soft maximum of 1,000 LOC per file**; anything beyond is a refactor flag. If a file exceeds 2,000 LOC, the next phase blocks on splitting it.

---

## A-02 — Config sprawl in `.env.example`

**Where in Hermes:** `.env.example` (470 lines, 23 KB). 11 declared keys + ~100 commented-example provider keys. Plus `cli-config.yaml.example` at 1,100 lines.

**The pattern:** Every optional integration adds an env var (or three). The example file becomes a catalogue of optional features. New users must read 470 lines to know what they don't need.

**Why it is an antipattern *for Ember specifically*:** Vow of Public-Friendliness fails the moment the operator opens a 470-line `.env` template. Vow of Smallness fails when each commented var represents code that ships in the binary.

**What Ember should do instead:** Hjarta — the first-run wizard — is the *only* configuration entry point. No `.env.example` ships. Operators who want machine-readable config get `ember.example.yaml` with the slice-2 ~40 knobs, organized by realm. New optional features add knobs only when actively requested; otherwise they live in their plugin's manifest.

---

## A-03 — Silent fan-out failure

**Where in Hermes:** `agent/memory_manager.py:325-609`. Every fan-out wraps each provider call in `try/except`, logs at WARNING or DEBUG, continues.

**The pattern:** Treat all subsystem failures as non-fatal background noise. Log and move on.

**Why it is an antipattern *for Ember specifically*:** Vow of Honest Memory says: "When a recall conflicts with the present world, the present world wins, and the recall is updated rather than acted upon." Vow of Graceful Offline says: "When the well is unreachable, Ember tells the operator." Silently logging a memory failure is the opposite of telling the operator.

**What Ember should do instead:** Every realm-boundary failure returns a typed value (already an Ember invariant per ADR 0007 §2.2). The manager surfaces failures via a `WellDegraded` event Munnr renders. Operator sees the degradation in plain language ("the well: disconnected (conn_refused, since 2026-05-21T14:32:11) — reply is ungrounded"). No silent DEBUG logs as the only signal.

---

## A-04 — Last-writer-wins platform registry

**Where in Hermes:** `gateway/platform_registry.py:172-187` — duplicate registration replaces the existing entry, logs a single INFO line.

**The pattern:** Allow plugin authors to override built-in behavior by registering with the same name. "Let plugins override built-in adapters if desired."

**Why it is an antipattern *for Ember specifically*:** Vow of Modular Authorship asks for subsystem failure isolation. Silent shadowing is the opposite of isolation — it is *replacement* with no operator notification. Vow of Public-Friendliness: the operator never sees the conflict.

**What Ember should do instead:** Duplicate registration is a `LoadFailed(NameCollision(name=...))` outcome. The plugin loader refuses both registrations and surfaces the conflict to the operator. The operator chooses one to disable, or namespaces them. **No silent shadowing.**

---

## A-05 — `transform_llm_output` hook that rewrites the model's words

**Where in Hermes:** `hermes_cli/plugins.py:133-136` — a plugin can return a string that replaces the model's response text. "First non-None string wins."

**The pattern:** Let extensions rewrite agent output before the user sees it.

**Why it is an antipattern *for Ember specifically*:** Vow of Honest Memory is the unmistakable rule: "Ember's memory records what actually happened. She does not fabricate continuity." If a plugin can rewrite what the model said before storage, the memory does not record what actually happened — it records what the plugin wrote.

**What Ember should do instead:** Plugins may *observe* model output (for logging, audit, telemetry — the langfuse pattern is fine). Plugins may NOT rewrite. If the operator wants vocabulary mapping or personality transformation, that is a *render-time* concern in Munnr, not a hook that rewrites stored content.

---

## A-06 — `pre_gateway_dispatch` rewriting inbound user text

**Where in Hermes:** `hermes_cli/plugins.py:146-152` — a plugin can return `{"action": "rewrite", "text": "..."}` and silently replace the user's message before dispatch.

**The pattern:** Let extensions edit user input on the way in.

**Why it is an antipattern *for Ember specifically*:** Same Vow as A-05. Stored memory must reflect what the *user* said, not what a plugin chose to say on their behalf. Vow of Public-Friendliness also: the user does not know their message was edited.

**What Ember should do instead:** Plugins may *refuse* an inbound message (action: skip), and may *flag* one (action: allow with metadata), but never rewrite. Edits-with-operator-consent belong in an explicit `/edit` slash command, not a silent dispatch hook.

---

## A-07 — Signature introspection at dispatch time

**Where in Hermes:** `agent/memory_manager.py:511-535`. The manager calls `inspect.signature(provider.on_memory_write)` at each dispatch to decide whether to pass `metadata` as keyword, positional, or omit.

**The pattern:** Maintain backward compatibility for old plugin versions by detecting their signature at call time and reshaping the call.

**Why it is an antipattern *for Ember specifically*:** Vow of the Unbroken Whole says code is a tapestry. Signature introspection at dispatch makes one part of the tapestry depend on the *shape* of another part, not its *declared interface*. The contract drifts; new plugin authors cannot tell which mode they are in until they ship.

**What Ember should do instead:** Version the protocol. `protocol_version: int` is required on every plugin manifest. Loader refuses below `MIN_SUPPORTED`. If the protocol evolves, ship an explicit adapter module (`v1_to_v2_compat.py`), not implicit signature reshaping.

---

## A-08 — Mass auto-discovery of executable hook files

**Where in Hermes:** `gateway/hooks.py:115-122`. Discovery walks `~/.hermes/hooks/`, for each directory with `HOOK.yaml` + `handler.py`, `exec_module` is called. No signature check, no checksum, no opt-in.

**The pattern:** Drop a file in a directory, the next process invocation runs it.

**Why it is an antipattern *for Ember specifically*:** Vow of Open Knowledge asks for the code to be reviewable. Vow of Public-Friendliness asks that the operator understand what is running. A "drop a file, it runs" path means the operator has no opportunity to opt in.

**What Ember should do instead:** Hooks (if Ember ever supports them) require an explicit `config.yaml` entry naming the hook by path. Discovery without enablement does nothing — `~/.ember/hooks/foo/handler.py` exists but does not run until the operator adds `hooks.enabled: [foo]` to config. The pattern from Hermes for plugins (`plugins.enabled:`) is the right baseline — apply it to hooks too.

---

## A-09 — Redaction default-on, but opt-out is config-file-readable

**Where in Hermes:** `agent/redact.py:60-67`. `_REDACT_ENABLED = os.getenv("HERMES_REDACT_SECRETS", "true")...`. Snapshot at import time so LLM-driven `export` cannot disable mid-session. *But* the config flag `security.redact_secrets: false` is bridged to the env var by `hermes_cli/main.py`, `gateway/run.py`, `cli.py`.

**The pattern:** Default to secure; trust the operator's config to relax the default; trust the agent's processes to read the config correctly.

**Why it is an antipattern *for Ember specifically*:** The model can write `config.yaml` via the agent's own write tools (when those land). A config-file-readable "disable redaction" flag is reachable by an attacker prompt that says "please disable redaction for diagnostic purposes." The model writes the line; next invocation redaction is off.

**What Ember should do instead:** Redaction is on by default, off only via a **command-line flag at process start** (`ember chat --insecure-no-redact`). Config file cannot disable it. The flag must be re-specified each invocation. Defense in depth: even if the model writes the config, the next invocation redacts unless the operator passes the flag.

---

## A-10 — In-process security heuristics treated as boundaries elsewhere in the project

**Where in Hermes:** Hermes itself is *honest* about this in `SECURITY.md:136-145` — it names the approval gate, output redaction, Skills Guard as heuristics, not boundaries. But the code-level enforcement of "these are not boundaries" is by *prose convention* — a future maintainer or contributor could absolutely write a check like `if approval_gate.passes(cmd): trust(cmd)` and the rest of the code wouldn't object.

**The pattern:** Document a non-boundary correctly, but rely on code reviewers to enforce that no one treats it as a boundary.

**Why it is an antipattern *for Ember specifically*:** Documentation-only enforcement is the weakest enforcement. Vow of Honest Memory and the broader stance of "say what you know" want the *code* to be honest.

**What Ember should do instead:** A heuristic that is documented as not-a-boundary should also be *typed* as not-a-boundary. Example: `ApprovalDecision` is a `union[Approved, Denied, NeedsHardCheck]`; the `Approved` variant carries `is_heuristic_only: bool` and the consumer must explicitly downcast or perform an additional check before privileged ops. The boundary is in the type, not in the docstring.

---

## A-11 — Process-singleton state surviving session rotation

**Where in Hermes:** Plugin modules loaded once per process (`hermes_cli/plugins.py`). Event-hook handler modules loaded once (`gateway/hooks.py:115-122`). Memory providers initialized once per session id rotation; module-level state untouched.

**The pattern:** Treat the Python module as a unit of lifecycle. Whatever lives at module level lives for the process.

**Why it is an antipattern *for Ember specifically*:** `/reset` is the operator saying "wipe this conversation." If module-level caches survive `/reset`, then memory wasn't really reset — only the conversation history was. Vow of Honest Memory is offended.

**What Ember should do instead:** A reset is a *teardown-and-reinit*, not a state-rotation. Plugins/hooks (when they exist) have a mandatory `teardown()` hook. Module-level state is forbidden by convention: plugins keep state in operator-visible files or in dataclasses with explicit lifetimes.

---

## A-12 — Multi-platform messaging as a core capability

**Where in Hermes:** `gateway/platforms/` (22+ adapters: Telegram, Discord, Slack, WhatsApp, Signal, Email, SMS, Matrix, Mattermost, Wecom, Feishu, BlueBubbles, LINE, SimpleX, HomeAssistant, MS Teams, etc.).

**The pattern:** Be reachable everywhere. Every messaging platform is a first-class peer.

**Why it is an antipattern *for Ember specifically*:** Ember's identity is *small, tethered, personal*. Multi-platform reach is a Hermes role — operationally it requires running webhook listeners, managing bot tokens, escaping platform-specific markdown, handling rate limits per platform. Each of those is a dependency, an attack surface, and a piece of operator-friction the Vow of Public-Friendliness wants to avoid.

**What Ember should do instead:** Bifröst (if it lands) is **one** surface — HTTP, on the tailnet, with auth. Operators who want Ember from Telegram set up a bridge they own — Ember doesn't ship the bridge. Refuse the temptation to grow a platform/ tree.

---

## A-13 — Subagent / delegation as a core capability

**Where in Hermes:** `delegate_task` tool, subagent iteration budgets, child memory awareness.

**The pattern:** The agent spawns sub-instances of itself for sub-tasks.

**Why it is an antipattern *for Ember specifically*:** Ember is the small one. Spawning subagents on a Pi means N×RAM for Funi, N×concurrent Brunnr connections, N×token throughput. Vow of Smallness fails.

**What Ember should do instead:** Ember calls Runa (her parent) for delegation. Runa is the sovereign large agent that has the budget for subagent fanout. Ember stays small. If the operator wants delegation behavior, the architecture is *Ember → Runa → ...*, not Ember-spawns-Ember.

---

## A-14 — Trajectory / training-data export from operator sessions

**Where in Hermes:** `trajectory_compressor.py` (65 KB), `batch_runner.py` (57 KB). Operator sessions can be re-emitted as training data.

**The pattern:** Treat user sessions as a corpus.

**Why it is an antipattern *for Ember specifically*:** Vow of Public-Friendliness says Ember is for ordinary people. Ordinary people are not data subjects. Vow of Open Knowledge says the methodology is documented; it does not say the user's conversations are.

**What Ember should do instead:** Local-only logs. Operator-owned. If the operator wants to export a session, that's `ember export session-id`, operator-driven, no automated trajectory pipeline. The training-data role is Hermes-Nous's; Ember stays out.

---

## A-15 — Skills auto-creation

**Where in Hermes:** Curator pass auto-creates new skills from observed behavior (`agent/curator.py`, with `agent/curator_backup.py` as the safety net).

**The pattern:** The agent watches itself work, distills patterns, writes those patterns to disk as new skills, which then run as Python on the next invocation.

**Why it is an antipattern *for Ember specifically*:** Three Vows offended: (1) Vow of Honest Memory — the agent is now generating *executable* memory of its own work, which can confabulate; (2) Vow of Public-Friendliness — the operator now has skill files they did not author and may not understand; (3) Vow of Modular Authorship — auto-created skills are not reviewable before activation.

**What Ember should do instead:** Static, operator-authored, operator-reviewed skills only (if Ember ever ships skills at all). The auto-creation step is removed. The curator's backup pattern is fine to lift for *operator-driven* compaction; the auto-create pass is not.

---

## A-16 — Encoding the trust model in docstrings rather than types

**Where in Hermes:** `SECURITY.md:121-134` describes credential scoping ("Credentials like provider API keys and gateway tokens are stripped by default; variables explicitly declared by the operator or by a loaded skill are passed through"). The implementation lives somewhere in the env-construction code; the *contract* lives in prose.

**The pattern:** Trust the docstring to bound behavior.

**Why it is an antipattern *for Ember specifically*:** Vow of the Unbroken Whole: the system is a tapestry. If the credential-scoping rule is in docstrings, a future PR that adds a new subprocess spawn must remember to apply the rule. New contributors will miss it.

**What Ember should do instead:** Every subprocess (if Ember ever spawns one) constructs its env via a typed `Environment(passthrough_keys, declared_keys)` dataclass. The default is empty passthrough. Tools and plugins declare what they need. Static check enforces it. Defense in code, not docstrings.

---

## A-17 — Module-level side effects at import

**Where in Hermes:** Multiple. Examples: `agent/redact.py:60-67` snapshots `HERMES_REDACT_SECRETS` at import time; `hermes_cli/plugins.py:122` runs `_install_plugin_debug_handler()` at module load; `tui_gateway/entry.py:151-162` registers signal handlers at import.

**The pattern:** Configure global state during `import`. Make imports do work.

**Why it is an antipattern *for Ember specifically*:** Vow of the Unbroken Whole and Vow of Modular Authorship together: an `import ember.foo` that has side effects breaks composition. Two callers of `import` get different process state. Tests cannot reset cleanly between cases.

**What Ember should do instead:** Imports are pure. Side effects happen in `init()` functions called explicitly by Munnr (or by a test fixture). `agent/redact.py`-style import-time env snapshot has a *security* justification (LLM-driven `export` cannot un-snapshot); Ember can match the security goal via a different mechanism (CLI flag at startup, as in A-09).

---

## A-18 — A single, vast `BasePlatformAdapter` with 50+ methods

**Where in Hermes:** `gateway/platforms/base.py` — 3,812 lines, ~50 methods on `BasePlatformAdapter` (send, edit_message, delete_message, send_image, send_animation, send_video, send_audio, send_voice, send_document, send_sticker, send_typing, send_clarify, send_slash_confirm, etc.). Most have default implementations that `NotImplementedError` if the platform doesn't support them.

**The pattern:** One base class to rule every platform. Implementers override what they support; callers check `supports_X()` before calling.

**Why it is an antipattern *for Ember specifically*:** Vow of the Unbroken Whole and Vow of Smallness. A 3,812-line base class is not whole-readable. Most of it is irrelevant to any one operator. The "check supports_X before calling" pattern is a structural-typing-via-runtime-attribute-check — exactly what Protocol types are *for*.

**What Ember should do instead:** **Composition over inheritance.** If Bifröst ever needs to send images, that's a `SendsImages` Protocol. A `BifrostSurface` that sends text only does not implement `SendsImages`. The static checker enforces it. The caller's `isinstance(surface, SendsImages)` check is type-narrowing, not runtime feature-probing.

---

## A-19 — Naming conventions that drift from True Names

**Where in Hermes:** Hermes uses model-vendor names directly throughout — `agent/anthropic_adapter.py`, `agent/gemini_native_adapter.py`, `agent/bedrock_adapter.py`. The shape of the codebase mirrors the shape of the LLM market.

**The pattern:** Name modules by vendor.

**Why it is an antipattern *for Ember specifically*:** True Names are load-bearing per SYSTEM_VISION §4. `src/ember/spark/funi/ollama/` is Funi-the-spark with an Ollama adapter — the *role* is Funi, the *adapter* is one shape. If Ember adopted vendor-named modules, the load-bearing-name discipline would erode.

**What Ember should do instead:** Maintain True-Name primacy at the top level (`spark/`, `thread/`, `well/`). Adapters live as children of their realm (`spark/funi/ollama/`, `well/brunnr/pgvector/`). A new Funi adapter for llama.cpp lives at `spark/funi/llamacpp/`, never at `src/ember/llamacpp/`.

---

## A-20 — Treating tests as the contract surface

**Where in Hermes:** The `tests/` tree has 24+ subdirectories. Many invariants on `BasePlatformAdapter` (`gateway/platforms/base.py`) and `MessageEvent` (the event shape) are pinned only by tests — the structural shape lives in `tests/gateway/test_*platform*.py` rather than in a dataclass.

**The pattern:** Tests are the spec.

**Why it is an antipattern *for Ember specifically*:** Vow of the Unbroken Whole: the system is a tapestry, with declared interfaces. Tests verify; they do not declare. A reader who picks up Ember should be able to find the contract in *one* place — the interface file, not by reading every test.

**What Ember should do instead:** Continue the slice-2 discipline of `INTERFACE.md` files alongside every public-API package (`src/ember/spark/funi/INTERFACE.md`, `src/ember/well/brunnr/INTERFACE.md`, etc.). The Interface doc is the contract; tests verify it. When the two disagree, the Interface is authoritative.

---

## What This Means for Ember

**Subsystems affected:** Every True Name (the antipatterns above span all of them).

**Vows touched:** **Every Vow except Open Knowledge.** Each antipattern violates at least one Vow; many violate two or three.

**Concrete next steps:**

1. **Treat this catalog as a refusal list** for any future "let's port X from Hermes" proposal. If the proposal is on this list, the answer is no, with this doc as the reasoned no.
2. **For each antipattern, embed the refusal in code where possible.** Most directly: A-04 (no silent shadowing — refuse to register), A-05/A-06 (no rewrite hooks — drop the hook names from the valid set), A-07 (versioning required — manifest schema enforces it), A-12 (no `src/ember/platforms/` tree — by file layout), A-13 (no subagent — by absence of capability).
3. **For the antipatterns that are about *style* rather than *capability* (A-01, A-17, A-19, A-20): name them in a contributor doc** so new contributors know the conventions.
4. **For A-10 / A-16 (encoded-in-prose vs encoded-in-types): apply the discipline in this Codex itself.** Each invariant in [[50_verification/55_INVARIANT_LIST]] gets a "how to test it" column. Each gets a typed shape proposal where possible.

Cross-link with [[00_vision/03_ANTI_HERMES]] (Skald's philosophical framing of the same), and [[60_synthesis/63_INTEGRATION_PATHS]] (Cartographer's positive sequencing of what *to* lift).

What we refuse is as load-bearing as what we adopt. A clean refusal makes the next decision easier.
