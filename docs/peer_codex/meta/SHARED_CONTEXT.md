# Peer Codex (Wave 2) — Shared Context Brief

**Read this before writing a single line.** Then read [[meta/MANIFEST]] for the full doc list.

---

## 1. The Mission

Wave 2 of Ember's research arc. You are one of six Mythic Engineering specialists working in parallel to mine **three peer agent codebases** for everything they teach us beyond Hermes:

- **Letta** (formerly MemGPT) — `letta-ai/letta` — memory-architecture specialists
- **smolagents** (HuggingFace) — `huggingface/smolagents` — small + tool-using
- **Goose** (Block) — `block/goose` — local-first, MCP-native, Rust-based

You already have the **Hermes Codex** at `~/ai/ember/docs/hermes_codex/` (58 docs, 155k words). Wave 2 reveals what's **Hermes-specific** vs **universal** to capable agents, and surfaces patterns Hermes lacks.

The grand unified Ember plan will be synthesized **after all research waves complete** — your job is to leave findings durable enough for that synthesis to be possible.

---

## 2. The Three Peers in One Breath Each

### Letta (`/tmp/letta/`)
- **What:** Memory-centric agent framework descended from MemGPT (Berkeley research). Built around `LettaAgent` with structured memory blocks (`core_memory`, `archival_memory`, `recall_memory`) and explicit memory-management tools.
- **Why we mine it:** Memory architecture is core to Ember's Brunnr/Smiðja story. Letta's *explicit, agent-callable* memory tools are a radically different model from Hermes's *implicit, system-managed* curator.
- **Stats:** 875 Python files, 246,861 lines. Version `v0.16.8`. SHA: `1131535716e8a31c9a437f8695e25ac98f203a24`
- **Notable surfaces:** `letta/` (core), `letta/agent.py`, `letta/memory.py`, `letta/services/`, `alembic/` (DB migrations — schema is documented), `fern/` (API spec), `compose.yaml` (production deployment shape), `examples/`, `assets/`, server vs client split
- **Honors Vow of Pluggable Storage?** Yes — PostgreSQL + SQLite + pgvector
- **Tethered Grounding-friendly?** Yes — memory is explicitly external

### smolagents (`/tmp/smolagents/`)
- **What:** HuggingFace's deliberately-small agent library. Code-execution-centric (`CodeAgent`) and tool-calling (`ToolCallingAgent`). Minimalist on purpose. Uses HF Hub for tool sharing.
- **Why we mine it:** Smallness is Ember's first Vow. smolagents proves a capable agent *can* fit in <30k lines. Also: code-execution-as-action is a powerful pattern Hermes barely uses.
- **Stats:** 75 Python files, 30,968 lines (≈12× smaller than Hermes). Version `v1.0.0+921 commits`. SHA: `3cd5c84e7386fa8b93514cc8fd05dcda1fe44a7d`
- **Notable surfaces:** `src/smolagents/` (whole library), `src/smolagents/agents.py`, `src/smolagents/models.py`, `src/smolagents/local_python_executor.py`, `src/smolagents/e2b_executor.py`, `src/smolagents/tools.py`, `examples/`, `docs/`, `e2b.toml`
- **Honors Vow of Smallness?** Aggressively yes.
- **Has anything Hermes lacks?** Code-execution-first agent shape; E2B sandbox integration; minimalism as design discipline.

### Goose (`/tmp/goose/`)
- **What:** Block's local-first agent. **Rust** core + TypeScript desktop UI. MCP-native (Goose was an early MCP adopter). Has Recipes (declarative agent configs), Extensions (≈MCP servers), Sessions (persistent state).
- **Why we mine it:** Goose is the **closest production-grade deployment shape** to what Ember wants: local-first, cross-platform desktop, MCP-everywhere, opinionated about safety. Also the only non-Python peer — *forces* us to think about cross-language interfaces.
- **Stats:** 433 Rust files, 369,753 lines (Rust + TS + TSX). Version `v2.0-rc-04-27`. SHA: `ca26f01d3acd9871691fa8981f05d19aed9a3b82`
- **Notable surfaces:** `crates/` (Rust workspace: goose, goose-cli, goose-server, goose-mcp, goose-bench), `ui/desktop/` (Electron + React), `documentation/`, `Justfile`, `Cargo.toml`, `recipes/`, `CLAUDE.md`, `AGENTS.md`
- **Cross-platform?** First-class — they ship desktop builds for macOS / Windows / Linux.
- **Has anything Hermes lacks?** Recipes-as-code; MCP-native from day one; safety guardrails as first-class architecture; cross-language IPC; native desktop UX.

---

## 3. Ember Context Recap

Same as Hermes wave. Brief recap so you don't have to re-read the whole SYSTEM_VISION:

### Six True Names
- **Funi** (flame) — local LLM runtime
- **Strengr** (cord) — network tether to the Well
- **Brunnr** (well) — pluggable storage adapter
- **Smiðja** (forge) — ingest / chunk / embed pipeline
- **Hjarta** (heart) — first-run setup rite
- **Munnr** (mouth) — CLI / interaction surface

### Three Realms
- **The Spark** (Funi, Munnr, Hjarta) — local thinking, no-network-required
- **The Thread** (Strengr) — networking
- **The Well** (Brunnr, Smiðja) — memory + knowledge

### Ten Vows (the truth-test for any Hermes/Letta/smolagents/Goose pattern)
Smallness, Tethered Grounding, Graceful Offline, Pluggable Storage, Unbroken Whole, Flexible Roots, Public-Friendliness, Honest Memory, Modular Authorship, Open Knowledge.

### Proposed-but-NOT-ratified additions from Wave 1 (treat as candidates)
- **New True Names** (proposed): Listir, Verkfæri, Vegfarendr, Gjallarhorn, Vinátta
- **New Vows** (proposed): Cache Discipline, Defended System Prompt

When you encounter peer-agent patterns that strengthen the case for any of these candidates — *note it*. When you encounter patterns that argue against them — *also note it*.

---

## 4. Output Layout

All your docs go under `~/ai/ember/docs/peer_codex/`:

```
peer_codex/
├── 00_vision/          (Skald)
├── 10_domain/          (Architect)
├── 20_interface/       (Cartographer interface tracing + Auditor interface verification)
├── 30_execution/       (Forge)
├── 50_verification/    (Auditor)
├── 60_synthesis/       (Cartographer)
├── _cross_comparison/  (cross-peer comparison docs from any role)
└── meta/               (Scribe; also where this file lives)
```

**File naming convention** (codebase prefix where doc is peer-specific):
- `00_vision/LETTA_ESSENCE.md`
- `00_vision/SMOL_ESSENCE.md`
- `00_vision/GOOSE_ESSENCE.md`
- `00_vision/CROSS_TRIANGULATION.md` (when comparing all 3)

For cross-peer comparison docs, use the prefix `CROSS_` and place in either the relevant layer dir or `_cross_comparison/`.

---

## 5. Required Frontmatter (every doc)

```yaml
---
codex_id: <slug matching filename>
title: <human-readable>
role: <Skald|Architect|Cartographer|Forge|Auditor|Scribe>
layer: <Vision|Domain|Interface|Execution|Verification|Synthesis|Meta>
peer_targets: [Letta, smolagents, Goose]   # or subset
status: draft
peer_source_refs:
  - letta:letta/agent.py:120-300
  - smolagents:src/smolagents/agents.py:1-80
  - goose:crates/goose/src/agents/agent.rs:50-200
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
hermes_codex_refs: [10_domain/11_AGENT_CORE]   # link to Hermes Codex docs you build on
cross_refs:
  - 10_domain/CROSS_DOMAIN_TRIANGULATION
---
```

---

## 6. Voice & Quality Bar

- **1500–4000 words** per peer-specific doc; cross-comparison docs can run to 5000 if they need it.
- **Cite real source paths**: `letta/agent.py:280-320`, `src/smolagents/agents.py:412`, `crates/goose/src/agents/agent.rs:88-152` — never `/tmp/...`
- **Every doc ends with `## What This Means for Ember`** — name True Names affected, Vows touched, Hermes Codex docs that get reinforced or contradicted.
- **Compare, don't merely describe**. When you describe Letta's memory tools, contrast against Hermes's curator AND smolagents's *lack of curator* AND Goose's session model. The value of Wave 2 is the *triangulation*.
- **Reference the Hermes Codex** with `[[hermes_codex/10_domain/11_AGENT_CORE]]` syntax (it lives at `~/ai/ember/docs/hermes_codex/`).
- **Cross-link** within Wave 2 with `[[10_domain/LETTA_DOMAIN]]` syntax.
- Honor Ember's Vows.
- **NO modification of any file outside `docs/peer_codex/`.**

---

## 7. The Six Roles (Reminder)

Same six personas as Hermes wave: Skald (Sigrún), Architect (Rúnhild), Cartographer (Védis), Forge (Eldra), Auditor (Sólrún), Scribe (Eirwyn). Voice per role is documented at `~/ai/ember/docs/hermes_codex/meta/STYLE_GUIDE.md` — read that if you need a refresher.

---

## 8. The Grand-Plan Imperative

The user has stated: **the grand unified multi-step plan will be drafted only after ALL research waves complete.** Your Wave 2 docs feed that synthesis. So:

- Be **decisive** in your assessments. Don't write "this might be interesting." Write "this is a pattern Ember should adopt, this is the True Name that owns it, this is the integration cost."
- Be **specific** about *what changes for Ember* if a pattern is adopted.
- Be **honest** about what does NOT translate. Goose is Rust; smolagents skips features Ember needs; Letta's deployment model is server-first. Name the friction.
- Leave **decision-ready material** — cross-link, name names, give estimates.

The grand plan will pull from Hermes Codex + Wave 2 + Waves 3, 5, 6 + any additional waves the user adds. Make Wave 2 weightbearing.

---

*— the Six, second wave*
