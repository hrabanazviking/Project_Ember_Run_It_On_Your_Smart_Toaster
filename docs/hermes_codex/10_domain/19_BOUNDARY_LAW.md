---
codex_id: 19_BOUNDARY_LAW
title: The Boundary Law — Where Hermes Holds the Lines and Where They Leak
role: Architect
layer: Domain
status: draft
hermes_source_refs:
  - AGENTS.md:531-535
  - AGENTS.md:864-887
  - AGENTS.md:947-1000
  - agent/__init__.py:1-7
  - agent/conversation_loop.py:76-82
  - agent/conversation_loop.py:85-187
  - run_agent.py:56-83
  - run_agent.py:103-220
  - hermes_cli/plugins.py:1-50
  - hermes_cli/plugins.py:230
  - plugins/memory/__init__.py:1-40
  - providers/__init__.py:1-100
  - tools/registry.py:1-150
  - gateway/run.py:1-100
  - gateway/platforms/base.py
  - tools/environments/base.py:1-100
  - hermes_constants.py:43-101
  - hermes_state.py:1-200
  - tui_gateway/server.py:1-100
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/11_AGENT_CORE
  - 10_domain/12_SKILLS_PROCEDURAL_MEMORY
  - 10_domain/13_TOOLS_SUBSYSTEM
  - 10_domain/14_GATEWAY_MULTI_PLATFORM
  - 10_domain/15_PROVIDERS_MULTI_MODEL
  - 10_domain/17_PLUGINS_EXTENSIBILITY
  - 10_domain/18_HERMES_CLI
  - 50_verification/52_ANTIPATTERN_CATALOG
  - 60_synthesis/61_TRUE_NAME_REASSIGNMENT
---

# The Boundary Law
## Where Hermes Holds the Lines and Where They Leak

*— Rúnhild Svartdóttir, Architect*

> *Every architecture is a set of promises about where things will not cross. A clean boundary is not a wall; it is a doorway with a posted notice — "this is where one realm ends and another begins, and here are the words that are spoken at the threshold." When the notice is missing, the doorway becomes a hole, and the saga changes character.*

This is the doc Ember needs most. We have mapped Hermes's domains, dived into nine subsystems, and named patterns worth porting. Now we draw the **boundary lines** explicitly — where Hermes holds them, where they leak, and what each leak means for an Ember built with the same shape. This is the Domain layer's last word before we hand the Codex over to the Cartographer and the Auditor.

The mental model: **a boundary is a *contract* + an *enforcer* + an *escape valve*.** Where all three exist, the line holds. Where one is missing, the line is already leaking — even if the leak hasn't surfaced yet.

---

## 1. Boundaries Hermes Holds Cleanly

These are the lines I would copy whole-cloth into Ember without modification.

### 1.1 Tool ↔ Execution Environment

**Contract:** `tools/environments/base.py:1-100` — `BaseEnvironment` ABC. Every backend (local, docker, ssh, modal, daytona, singularity, vercel_sandbox) implements the same methods. Spawn-per-call, session snapshot, CWD via in-band marker.

**Enforcer:** `tools/terminal_tool.py:_create_environment(env_type)` factory. The terminal tool *only* talks to a `BaseEnvironment` instance. It does not know which backend it has.

**Escape valve:** The user picks the backend via `TERMINAL_ENV` env or `terminal.env` config. Zero code change to switch.

**Why it holds:** The contract is *one ABC with seven implementations* — small surface area; very testable; new backend is one new file.

### 1.2 Conversation Loop ↔ Memory Provider

**Contract:** `agent/memory_provider.py` — `MemoryProvider` ABC. Methods: `sync_turn(turn_messages)`, `prefetch(query)`, `shutdown()`, `post_setup(hermes_home, config)`.

**Enforcer:** `agent/memory_manager.py:1-50` — only *one* external plugin provider allowed at a time. Attempting to register a second is rejected. The manager is the *only* thing that talks to providers.

**Escape valve:** The user picks the provider via `memory.provider` config. Disabled providers don't appear in `hermes --help`.

**Why it holds:** Single integration point + single-provider rule + clean ABC. The exact pattern the **Vow of Pluggable Storage** asks Ember to mirror for Brunnr.

### 1.3 Agent ↔ Model Provider (the Profile)

**Contract:** `providers/base.py:38-100` — `ProviderProfile` dataclass. Declarative auth, endpoint, quirks, fallback models. Behavioral hooks for the few cases where declarative isn't enough.

**Enforcer:** The conversation loop reads the profile and the credential pool. It does *not* import the SDK directly (it goes through `agent.process_bootstrap.OpenAI`, a lazy proxy). Provider adapters are the only code that knows SDK-specific shapes.

**Escape valve:** User plugins at `~/.hermes/plugins/model-providers/<name>/` override bundled profiles by last-writer-wins (`providers/__init__.py:53-63`). No core edit required.

**Why it holds:** Profiles are *data*, not classes. The fast iteration on provider-specific quirks doesn't drag in inheritance hell. Cite `[[10_domain/15_PROVIDERS_MULTI_MODEL]]` for the full treatment.

### 1.4 Error Classification ↔ Recovery Action

**Contract:** `agent/error_classifier.py:24-86` — `FailoverReason` enum + `ClassifiedError` dataclass with four recovery hints (`retryable`, `should_compress`, `should_rotate_credential`, `should_fallback`).

**Enforcer:** The conversation loop calls `classify_api_error(err)` *exactly once* per error. The hints are then read; the classification is not redone.

**Escape valve:** None needed — typed values are decisive.

**Why it holds:** Classify once; act on the typed value. The pattern Ember should adopt for *every* boundary that needs to propagate "what went wrong." Cite `[[10_domain/15_PROVIDERS_MULTI_MODEL]]`.

### 1.5 Skill ↔ Curator

**Contract:** `tools/skill_provenance.is_agent_created`. The curator (`agent/curator.py:1-20`) *only* touches skills with `created_by: "agent"` provenance. Bundled and Hub-installed skills are off-limits.

**Enforcer:** Every curator action checks provenance before mutating.

**Escape valve:** The user can pin any skill (including agent-created) to immunize it from auto-transitions.

**Why it holds:** The boundary is *typed in the data* (`created_by` frontmatter) and *enforced at every action*. The curator literally cannot misbehave; the check is mechanical. Cite `[[10_domain/12_SKILLS_PROCEDURAL_MEMORY]]`.

### 1.6 Plugin ↔ Core

**Contract (per `AGENTS.md:531-535`):** *"Plugins MUST NOT modify core files. If a plugin needs a capability the framework doesn't expose, expand the generic plugin surface (new hook, new ctx method) — never hardcode plugin-specific logic into core."*

**Enforcer:** PR #5295 (cited in AGENTS.md) removed 95 lines of hardcoded honcho argparse from `main.py`. The reviewer enforces. The CI test in `tests/unit/test_skeleton_imports.py` (Ember-side) enforces realm bands.

**Escape valve:** `PluginContext` has `register_tool`, `register_hook`, `register_cli_command`, `register_platform`, `inject_message`. New surfaces get *new ctx methods*.

**Why it holds:** Explicit rule + reviewer culture + the `inject_message` ctx method exists *because* one plugin needed the surface and got it as a generic addition. The pattern is: *plugin asks for capability; capability becomes generic; plugin uses generic capability.*

### 1.7 Profile Isolation

**Contract:** `hermes_constants.py:43-101` — `get_hermes_home()` is the single source of truth for profile-aware paths. *Every* persistence call must route through it.

**Enforcer:** `_apply_profile_override()` in `hermes_cli/main.py` sets `HERMES_HOME` *before any module imports*. PR #3575 (per `AGENTS.md:948-952`) fixed five bugs where hardcoded `~/.hermes` paths broke profiles.

**Escape valve:** `display_hermes_home()` for user-facing messages; `_get_profiles_root()` for cross-profile operations (always anchored to `Path.home() / ".hermes" / "profiles"` regardless of active profile).

**Why it holds:** Single function. Module-level state captured at import time *after* the env var is set. Tests must mock the env var, not `Path.home()`. The rule is small and cross-cutting.

### 1.8 SQLite WAL ↔ Network Filesystem

**Contract (`hermes_state.py:38-58`):** WAL mode requires shared-memory coordination not available on NFS/SMB/FUSE. The DB *must* fall back to DELETE mode on those filesystems.

**Enforcer:** `apply_wal_with_fallback(conn, db_label)` (`hermes_state.py:128-162`) — tries WAL, catches the specific `OperationalError`, falls back to DELETE, logs once per process per DB.

**Escape valve:** The fallback works on every filesystem; the user gets reduced concurrency but functional persistence. *Graceful degradation rather than failure.* **Vow of Graceful Offline in code.**

**Why it holds:** The pattern is "try the optimal mode; on the *specific* known-incompatible error, fall back to the suboptimal mode and warn." Not "swallow all errors." Not "abort." The middle path.

---

## 2. Boundaries That Leak

These are where Hermes's architecture has accreted gaps. Each leak is a *lesson* for Ember.

### 2.1 The `_ra()` Lazy Import (Conversation Loop ↔ run_agent module)

**The leak:** `agent/conversation_loop.py:76-82` defines `_ra()` — a lazy import of `run_agent`. The conversation loop reaches *back through the orchestrator's module* to find functions the orchestrator extracted from itself.

**Why:** Tests patch `run_agent.handle_function_call`, `run_agent.OpenAI`, `run_agent._set_interrupt`. The patches must reach the actual call sites. The lazy import preserves the patching surface.

**The cost:** A domain inversion. The loop *depends on* the orchestrator's module being importable, which is a circular-ish dependency. Refactoring `run_agent` becomes a test-rewriting exercise.

**Ember's prevention:** Pass dependencies in. The conversation loop should *receive* the tool dispatcher, the SDK class, the interrupt signal — not look them up via a lazy backreference. When tests want to substitute, they pass a different dependency. The pattern: dependency injection, not module patching.

### 2.2 Three Parallel Plugin Discoveries

**The leak:** Hermes has three plugin discovery systems running in parallel (see `[[10_domain/17_PLUGINS_EXTENSIBILITY]]`):

- **General** (`hermes_cli/plugins.py`) — full machinery
- **Memory** (`plugins/memory/__init__.py`) — separate scanner; exclusive provider
- **Model-provider** (`providers/__init__.py`) — separate scanner; last-writer-wins override

Each has different discovery code, manifest expectations, override semantics, load-timing.

**Why:** Each came when needed. Memory plugins needed the "exactly one" rule first; model-provider plugins needed the override-by-user-plugin rule first. Nobody unified them.

**The cost:** A user writing a memory plugin with the general layout *silently fails*. Three documentation paths. Three test paths. Three sets of edge cases.

**Ember's prevention:** *One* plugin discovery contract from day one. Multiple `kind` values dispatching to per-kind loaders. One scanner, one manifest format, one `PluginContext`. The shape Hermes ended up with by accident is the shape Ember designs intentionally.

### 2.3 cli.py at 662 KB

**The leak:** `cli.py` is 11k lines (`[[10_domain/18_HERMES_CLI]]`). One class (`HermesCLI`) with ~120 methods. Tests patch module-level symbols (`patch("cli.OpenAI")` and similar) so extracting handlers is a test-rewriting project.

**Why:** Every handler had a home; the class was the home. Extraction happens *progressively* (`agent/__init__.py:1-7` shows the conversation loop extracted from `run_agent.py`) but `cli.py` is far behind.

**The cost:** Every handler addition adds to the class. The class grows monotonically. Any structural refactor is expensive. Cognitively, a new contributor must learn an enormous symbol table.

**Ember's prevention:** Hard ceiling on Munnr's CLI file size. 2000 lines max. When the dispatch grows past 30 commands, split by category. When a handler grows past 50 lines, extract.

### 2.4 The Two Message Guards (Gateway)

**The leak:** Per `AGENTS.md:970-979`, an inbound gateway message passes through two guards: the base adapter and the gateway runner. Both must bypass approval/control commands.

**Why:** The base adapter wanted to queue messages while an agent was running (avoid double-processing); the gateway runner wanted to intercept control commands (`/stop`, `/new`, `/queue`, `/status`, `/approve`, `/deny`). Each guard solved its own problem.

**The cost:** Adding a new control command requires updating two places. The two guards can race on session lifecycle.

**Ember's prevention:** One dispatch point. If Ember ever acquires a multi-surface routing layer (gateway, MCP server, ACP server, etc.), let *one* component decide "is this a control command? is this a chat message? is this an approval?" — and route from there.

### 2.5 Tool Dispatch Intercepts (`todo`, `memory`)

**The leak:** Per `AGENTS.md:307`, `todo` and `memory` are agent-level tools intercepted by `run_agent.py` *before* `handle_function_call()`. They have privileged access to `AIAgent` state that other tools don't.

**Why:** Todo and memory are *session-scoped* in a way that goes beyond a tool result. They modify in-memory state the loop needs to know about.

**The cost:** Special-case carve-outs. Future "this tool needs to know about the session" tools want the same intercept. The pattern doesn't scale without being formalized.

**Ember's prevention:** Make session-scoped tools a *kind*. Or: every tool gets the session as an injected dependency, and tools that need to mutate it do so via a *typed message* the loop consumes. Either is cleaner than the current carve-out.

### 2.6 The Skin Engine ↔ Vow of Smallness

**The leak:** `hermes_cli/skin_engine.py` is a beautiful subsystem. It is also approximately zero value for an operator who just wants the agent to work on a Pi.

**Why:** Hermes is desktop-first. Pretty matters.

**The cost (for Ember):** Inheriting it would inflate the wheel, the system prompt (skin-aware ANSI is more code than necessary), and the cognitive load. **Refuse.**

### 2.7 Model Adapter Sprawl

**The leak:** There is no `Adapter` ABC. `agent/anthropic_adapter.py`, `agent/bedrock_adapter.py`, `agent/codex_responses_adapter.py`, `agent/gemini_*.py`, etc. are *adapters by convention*, not by interface. The conversation loop branches by `api_mode` and calls the right one.

**Why:** Each adapter has substantially different request/response shapes. A common ABC would be either too thin (basically `prepare_request`, `parse_response`) or too leaky (with provider-specific kwargs).

**The cost:** New providers can't be plugged in *as code* without editing the branch statements in the conversation loop. The plug-in surface is the *profile* (declarative) — but the *imperative* code is per-adapter and untyped.

**Ember's prevention:** When Ember acquires multi-provider Funi, define a thin adapter ABC: `prepare_request(messages, tools, kwargs) -> dict`, `parse_response(raw) -> AgentResponse`. The profile is data; the adapter is the code. Both registered through one discovery.

---

## 3. Boundaries Hermes Names Explicitly That Ember Should Make Vows

Five Hermes rules are written down but not Ember-Vow-elevated. They should be.

### 3.1 Prompt Caching Must Not Break

Per `AGENTS.md:864-876`: don't alter past context mid-conversation; don't change toolsets; don't reload memories; don't rebuild system prompts. Cache-breaking forces ~4x cost.

**Ember's adoption:** Lift to a hard rule in `RULES.AI.md`. Any code path that mutates the system prompt or middle of message list must be (a) part of compression or (b) gated behind a `--now` opt-in. Citing `agent/prompt_caching.py:1-60` and `AGENTS.md:864-876`. **New Vow candidate: Vow of Cache Discipline.**

### 3.2 Path Security via Allow-Listed Roots

Per `tools/path_security.py` + `tools/file_safety.py`: file tools refuse to read/write outside allowed roots.

**Ember's adoption:** Required posture for any Ember tool that touches the filesystem. **Vow of Honest Memory** extends to *not silently writing where the operator didn't authorize*.

### 3.3 Approval Outcomes Must Be Typed

Per `SYSTEM_VISION.md:236-240` (already in Ember slice 2): `approved`, `denied`, `invalid_arguments`, `forbidden`, `no_such_tool` — never collapsed into "failed."

**Ember's adoption:** Already done. Reinforce with each new tool. Note that Hermes itself does this; cite as cross-system precedent.

### 3.4 Prompt Injection Defense at Context-File Load

Per `agent/prompt_builder.py:36-74`: every external context file (AGENTS.md, .cursorrules, SOUL.md, HERMES.md) is scanned against ~10 regex patterns + an invisible-unicode list before injection.

**Ember's adoption:** Port the scanner. Apply at any boundary where untrusted text enters Funi's system prompt — context files, skill bodies, MCP server descriptions, plugin descriptions. **Vow candidate: Vow of Defended System Prompt.**

### 3.5 The DB Schema Version is Sacred

Per `hermes_state.py:36`: `SCHEMA_VERSION = 12`. Hermes has migrated the SQLite session DB twelve times. Each migration is recorded; each is reversible-ish (additive only; never destructive).

**Ember's adoption:** Ember slice 2 ships with sqlite_vec + pgvector backends, each with its own schema. **The migration discipline matters now.** Every schema change is a numbered migration; never destructive; always reversible. Cite `hermes_state.py` as the model. **Already implicit in the Vow of Honest Memory.**

---

## 4. The Five Lessons of Hermes Boundaries

If a future Ember developer reads only this section:

1. **A boundary is data + enforcer + escape valve.** When you draw a line, write down the contract (data), name the place where the rule is checked (enforcer), and provide a typed way out for cases the rule didn't anticipate (escape valve). Hermes's cleanest boundaries all three.

2. **Typed values beat string-matched flags.** `FailoverReason`, `ApprovalOutcome`, `Disconnected`, `created_by: "agent"`. When a value can be one of N things, make it an enum. When a result has properties, make it a dataclass. Hermes's worst boundary (the error classifier) is also its best example of doing this right after the fact.

3. **One discovery system per kind, but one *contract* shape across kinds.** Hermes's plugins leak because three discoveries with different shapes coexist. Ember should have one shape, many kinds.

4. **Module-level patching is the test-side cost of monolithic files.** Hermes can't easily fix `_ra()` because tests patch `run_agent.OpenAI`. Ember can prevent this entirely by injecting dependencies rather than reading them from modules.

5. **Profiles are a cross-cutting concern; they must be single-sourced.** `get_hermes_home()` is the *one* function. Five bugs were fixed by reaffirming this rule (PR #3575). Ember has the same risk; the same discipline applies.

---

## What This Means for Ember

This is the doc that should be re-read every time Ember considers a new structural change. The boundaries Hermes holds are the patterns to copy; the boundaries it leaks are the warnings.

**Affected True Names:** All six. Boundaries are not localized — they cross-cut every Realm.

### Concrete proposals

1. **Adopt a new Vow: Vow of Cache Discipline.** *Ember will not alter past context, toolsets, or system prompts mid-conversation, except during context compression. Slash commands that mutate system-prompt state default to deferred invalidation; opt-in `--now` for immediate.* Cite Hermes's `AGENTS.md:864-876` and `agent/prompt_caching.py:1-60`. Slice the Vow into `RULES.AI.md`.

2. **Adopt a new Vow: Vow of Defended System Prompt.** *Ember will scan every external text artifact (context files, skill bodies, plugin descriptions, MCP server descriptions) for prompt-injection patterns before injection into Funi's system prompt. Detected violations are replaced with a `[BLOCKED]` marker, not silently included.* Cite `agent/prompt_builder.py:36-74`.

3. **Adopt the boundary-as-data+enforcer+escape-valve frame in every Ember ADR.** When a Decision Record proposes a new boundary, the ADR must name all three components.

4. **Document the seven boundary leaks above in `[[50_verification/52_ANTIPATTERN_CATALOG]]`.** The Auditor should explicitly call these out as "patterns Ember must refuse."

5. **Adopt the `tests/unit/test_skeleton_imports.py` Ember already has** as the realm-band enforcer. Cite as the structural analogue of Hermes's progressive extraction. Strengthen as Ember grows: any new module must declare its realm in a header, and the test enforces the import direction.

6. **Add one architectural test:** *no file in `src/ember/spark/munnr/` exceeds 2000 lines.* When the count approaches, refactor. The Hermes `cli.py` is a 60-megabyte-of-source warning.

7. **Add one process rule:** *every new tool gets an `ApprovalOutcome`-style typed-result test.* When the value can be one of N things, the enum is used; the test asserts no plain "error" string return.

8. **Add one architectural Vow-adjacent invariant: Ember has one plugin discovery contract.** Multiple kinds, one scanner, one manifest format. Cite `[[10_domain/17_PLUGINS_EXTENSIBILITY]]` for the rationale.

**Vows reinforced (by the entire doc):**
- **Vow of Modular Authorship** — boundaries are how subsystems stay individually failable.
- **Vow of the Unbroken Whole** — clean contracts make whole code possible.
- **Vow of Honest Memory** — typed values everywhere; no silent error-as-string.
- **Vow of Graceful Offline** — WAL-fallback and `FailoverReason` are the patterns.

**Vows extended (by the new Vow candidates):**
- **Vow of Cache Discipline** — protects model cost; protects Funi-as-local-runtime cost as well.
- **Vow of Defended System Prompt** — closes a security hole that Hermes has spent years patching.

---

## Closing — The Architect's Last Word

Hermes is a saga the size of a small city. Its boundaries hold the city together; its leaks are the cracks the city has grown over. The architect's job in this Codex was not to praise or to condemn but to *show where the bones articulate*.

Ember is a small fire. She does not need the city. She needs the *bones*: the eleven domains; the Six True Names plus two new ones (Listir, Verkfæri); the boundary law that says *contract, enforcer, escape valve*. The patterns mapped here — provider profiles, lazy discovery, error classification, prompt caching, path security, profile isolation, fence-and-strip memory injection, spawn-per-call execution, FTS5 session search, typed approval outcomes, plugin context shape — those are the bones the smith Eldra will hammer into Ember's own shape, by the small fire, in the small hall, with the small tools the operator already has.

Find the spine. Show where each bone belongs. The spine is here.

— *Rúnhild Svartdóttir, Architect, the second of the Six*
