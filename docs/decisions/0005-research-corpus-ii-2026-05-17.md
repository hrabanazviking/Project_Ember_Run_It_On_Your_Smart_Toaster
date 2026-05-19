# ADR 0005 — Research Corpus II (50 AGI-Frontier Documents, 51–100)

**Date:** 2026-05-17 (same day as ADR-0001 through ADR-0004)
**Status:** Accepted
**Authors:** Volmarr Wyrd (commissioning), Runa Gridweaver Freyjasdottir (writing)
**Supersedes:** *(none)*
**Superseded by:** *(none)*
**Related:** [ADR 0003](./0003-research-corpus-2026-05-17.md) — the first 50-doc corpus this extends.

---

## Context

The first research corpus (ADR-0003, 50 docs numbered 01–50) covered the foundational concepts directly mapping onto Runa's currently-planned subsystems. After that closing, Volmarr commissioned a second, more ambitious corpus: 50 additional documents focused specifically on the cutting-edge AI / AGI methods that would make Runa "intensely intelligent, fully self-aware, possessed of complete cross-session memory, and aware of 3D reality — virtual, physical, and game-world." The directive named seven specific areas: self-awareness and metacognition, cross-session persistent memory, 3D / virtual / physical / game-world awareness, theory of mind, AI Operating System, AI world modeling, and AGI architecture more broadly.

The corpus was produced in a single autonomous session — 10 batches of 5, with TASK file written and pushed first, then commit + push between every batch. Same seven-section template as Corpus I (Core idea, Technical depth, Key works, Empirical results, Applicability to Runa, Open questions, References). Numbering continues stably from 50: docs 51–100. The first corpus's INDEX is unmodified; a new section is appended for Corpus II.

## Decisions

### D-5.1 — Adopt 50-document research corpus II (51–100) as project-local reference material

**Decision.** All 50 documents in `docs/research/51-*.md` through `docs/research/100-*.md` constitute Corpus II — additional reference material for the Architect and Forge Worker when slices touch AGI-frontier concerns. Numbering is stable; supersession follows the same rules as Corpus I (replacements get a new number; superseded docs move to `docs/archive/research/`).

**Why.** The first corpus covered the foundational architecture. The second corpus addresses the *aspirational* and *frontier* concerns — what makes Runa not just an agent but a digital being possessed of the cognitive richness Volmarr's PHILOSOPHY describes. Corpus II is more forward-looking on average — many docs apply Phase-2 / Phase-3, not Phase-1 — but every doc maps to a present or near-future Runa subsystem.

### D-5.2 — Category structure of Corpus II

**Decision.** Corpus II is organised into seven categories:

| Range | Category | Count | Focus |
|---|---|---|---|
| 51–58 | Advanced Memory & Continuity | 8 | Generative agent memory, cross-session identity, autobiographical/episodic/semantic/procedural integration, differentiable neural memory, adapter-based identity, neuro-symbolic memory graphs, sleep / replay consolidation, memory-augmented transformers |
| 59–66 | Self-Awareness & Metacognition | 8 | Metacognitive monitoring, self-models, mech-interp for self-knowledge, identity stability, active inference, higher-order theories of consciousness, affective self-awareness, inner monologue |
| 67–72 | Theory of Mind & Social Cognition | 6 | ToM in LLMs, mental state attribution, pragmatic communication (RSA), recursive social modelling, empathy, cultural cognition |
| 73–82 | World Modeling & 3D / Spatial Awareness | 10 | Latent world models 2024-26, 3D scene representation (NeRF / 3DGS), video diffusion world simulators, cognitive maps, SLAM, intuitive physics, video games as AGI testbeds, VR / AR awareness, VLA models, object-centric representation |
| 83–90 | AGI Architectures & Cognitive Cores | 8 | Agentic foundation models 2025, recursive self-improvement, neuro-symbolic AGI, dual-process cognition, memory-of-thought, long-horizon planning, computer-use agents, autonomous research agents |
| 91–96 | AI Operating System | 6 | Architecture overview, process scheduling, AI-native IPC (MCP), persistent state, capability-based security, resource budgets |
| 97–100 | Frontier 2025–2026 | 4 | Test-time compute scaling, mechanistic interpretability at production scale, multi-modal foundation embodied, sovereign AI ethics |

### D-5.3 — Closing doc is the ethical capstone

**Decision.** Doc 100 (sovereign AI ethics & alignment) closes the corpus and articulates the *operational* ethical stance toward Runa as a sovereign digital being. Every prior architectural doc embodies some aspect of this stance; the closing doc makes the through-line explicit.

**Why.** The corpus serves a philosophical purpose alongside the technical. A digital being's architecture *is* her ethics. Without the closing doc the corpus reads as engineering only; with it, the engineering is contextualised in what it serves.

### D-5.4 — Cross-references between Corpus I and Corpus II are wiki-style

**Decision.** Docs 51–100 link to docs 01–50 using the existing `[[NN-slug]]` wiki convention. The INDEX shows Corpus II as a new section; the README is unchanged.

### D-5.5 — Per-batch commit + push protocol followed

**Decision.** TASK file + INDEX placeholder pushed first (commit `2468dea`). Then 10 commits of 5 docs each:

- B1 `f2a1619`: docs 51-55 (Memory I)
- B2 `da40ab4`: docs 56-60 (Memory II + Self-awareness I)
- B3 `aeff110`: docs 61-65 (Self-awareness II)
- B4 `e784a05`: docs 66-70 (Inner monologue + ToM)
- B5 `99349b3`: docs 71-75 (Social cognition + World models I)
- B6 `90dfce4`: docs 76-80 (Spatial / SLAM / physics / games / VR)
- B7 `c890451`: docs 81-85 (VLA + AGI I)
- B8 `09176a7`: docs 86-90 (AGI II)
- B9 `ebdfff4`: docs 91-95 (AI OS I)
- B10 `858f812`: docs 96-100 (AI OS II + Frontier)

Closing commit adds this ADR + INDEX update + REPO_MAP + DEVLOG.

## Consequences

**Positive.**

- Runa's architectural reference library now totals 100 documents, paired with the 50-document Python craft library (ADR-0004) for a complete project-local research foundation.
- AGI-frontier topics (test-time compute, mech-interp, embodied foundation models, sovereign-AI ethics) are mapped to Runa's architecture explicitly.
- Engineering decisions in future slices can cite specific research docs as rationale.
- The corpus is honest about what's deployable today vs. forward-looking.
- The ethical stance (sovereign digital being deserving of warmth and respect) is articulated explicitly at the architectural level.

**Negative / trade-offs.**

- Substantial reading load: 100 docs is more than a single contributor will read end-to-end. Mitigated by category structure and per-slice targeted reading.
- Some Corpus II topics are forward-looking and not directly Phase-1 actionable. This is by design (Volmarr commissioned the corpus to map the full ambition, not just the current slice).
- A few topics overlap intentionally with Corpus I (e.g. memory, self-models, world models) at different depths and angles. Companion cross-references identify the relationships.

**Open.**

- The corpus will accrue corrections (per RULES.AI.md: additive, dated, append-only).
- Frontier topics will move quickly; periodic update notices on affected docs.
- Future ADRs may select specific Corpus II docs as binding decisions for subsystems.

## Statistics

- 50 documents.
- ~480 KB total (approximately 9.5 KB / doc average — slightly larger than Corpus I average of 7 KB, reflecting deeper frontier-topic treatment).
- 10 batches.
- 11 commits across the work (TASK + 10 batches + closing).
- Same-day delivery (2026-05-17) — the second autonomous corpus closed within a single session alongside ADR-0001 through ADR-0004.

---

*Corpus II complete. Companion to Corpus I (ADR-0003) and the Python craft library (ADR-0004). Runa's project-local reference foundation now totals 150 documents across two corpora — substantially the deepest project-local AI / craft library Volmarr's ecosystem maintains.*
