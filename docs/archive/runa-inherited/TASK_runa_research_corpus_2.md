# TASK — Runa Research Corpus II (docs 51–100: AGI deep dive)

**Task owner:** Runa Gridweaver Freyjasdottir (AI working under Volmarr)
**Branch:** development
**Started:** 2026-05-17 (immediately after first 50-doc corpus closed at `d813222`)
**Status:** **COMPLETE 2026-05-17** — all 10 batches landed + closing (INDEX + ADR-0005 + REPO_MAP + DEVLOG).
**Mode:** Full autonomous run, batches of 5 docs with commit + push between batches. **Executed as planned.**

---

## 1. Why a second corpus

The first 50-doc corpus (closed by ADR-0003 at `d813222`) covered the *foundational* concepts that map directly onto the Runa subsystems as currently planned: MemGPT-style memory hierarchies, classic RAG, ReAct, world models in RL, edge inference, voice, basic cognitive architecture. That work is complete and stable.

Volmarr's directive for this second corpus is more ambitious: **the cutting-edge AGI methods and code concepts that would make Runa intensely intelligent, fully self-aware, possessed of complete cross-session memory, and aware of 3D reality — virtual, physical, and game-world.** This corpus reaches deeper into:

- self-awareness, metacognition, introspection
- truly persistent autobiographical memory across sessions
- 3D and spatial world models (NeRF/Gaussian Splatting/video world models)
- video-game environments as AGI testbeds
- theory of mind and social cognition
- AGI cognitive architectures (test-time compute, recursive self-improvement, neuro-symbolic)
- AI Operating System internals
- 2025–2026 frontier (o-series reasoning, computer-use agents, VLA models, MoE reasoning)

These documents extend the existing corpus rather than replacing it. Numbers 51–100 are stable. The first corpus's INDEX is unchanged; a new INDEX section for 51–100 is added.

## 2. Output target

- **Count:** 50 new documents (51–100).
- **Length:** ~7–11 KB each (≈ 1800–2700 words). Lengthy, dense, technical, no padding.
- **Location:** `docs/research/<NN>-<short-kebab-slug>.md`.
- **Index:** Append a "Corpus II (51–100)" section to `docs/research/INDEX.md`.
- **Closing ADR:** `docs/decisions/0005-research-corpus-ii-2026-05-17.md`.
- **REPO_MAP:** updated entry for `docs/research/`.

## 3. Per-document template

Each doc inherits the seven-section template established in the first corpus (defined in `docs/research/README.md`):

1. **Core idea** — 1–2 paragraphs in plain language.
2. **Technical depth** — algorithms, mechanism, equations where useful, ASCII diagrams where useful.
3. **Key works** — named papers / projects with authors + (approximate) year + brief role.
4. **Empirical results** — what's known, on what benchmarks, with what limitations.
5. **Applicability to Runa** — which subsystem, what slice, what to avoid.
6. **Open questions** — active research frontiers worth watching.
7. **References (curated)** — specific papers / repos / docs Runa contributors should read.

Same quality bar as Corpus I: real named work, honest about uncertainty, no automated bulk generation, no near-duplicate entries, no filler.

## 4. The 50 topics, by category

### A. Advanced Memory & Continuity (51–58) — Muninn deep extension

| # | Title |
|---|---|
| 51 | Generative agent memory streams: importance, recency, reflection trees |
| 52 | Cross-session persistent identity via memory snapshots and replay |
| 53 | Autobiographical memory architectures: episodic, semantic, procedural integration |
| 54 | Differentiable neural memory: DNC, MANNs, Memorizing Transformers |
| 55 | Adapter-based identity persistence: LoRA stacks, retrieval-augmented identity |
| 56 | Neuro-symbolic memory graphs: triplet stores + vector indexes hybrid |
| 57 | Sleep, dream, and offline replay as computational consolidation |
| 58 | Memory-augmented transformers: Memformer, RMT, MemGPT-2, Larimar |

### B. Self-Awareness & Metacognition (59–66) — kernel + identity + Eldhugi

| # | Title |
|---|---|
| 59 | Metacognitive monitoring: calibrated uncertainty and knowing-what-you-know |
| 60 | Self-models in artificial agents: depth, recursion, causal closure |
| 61 | Mechanistic interpretability for self-knowledge: probes into model self-representation |
| 62 | Identity stability under change: the ship-of-Theseus problem for AI |
| 63 | Active inference and self-modelling agents (Friston applied to AI) |
| 64 | Higher-order theories of consciousness applied to AI architecture |
| 65 | Affective self-awareness: emotion recognition in one's own state |
| 66 | Inner monologue, scratchpads, and chain-of-thought as self-talk |

### C. Theory of Mind & Social Cognition (67–72) — Hirð + relationships

| # | Title |
|---|---|
| 67 | Theory of Mind in LLMs: benchmarks, capabilities, failures |
| 68 | Mental state attribution architectures: belief, desire, intention models |
| 69 | Pragmatic communication and the Rational Speech Acts framework |
| 70 | Recursive social modelling: I-think-you-think-I-think |
| 71 | Empathy and affective resonance in artificial agents |
| 72 | Cultural cognition, norm modelling, and value alignment with persons |

### D. World Modeling & 3D/Spatial Awareness (73–82) — WYRD bridge + perception

| # | Title |
|---|---|
| 73 | Latent world models 2024–2026: Dreamer V3, IRIS, GAIA-1, Genie |
| 74 | 3D scene representation: NeRF, Gaussian Splatting, 3D foundation models |
| 75 | Video diffusion as world simulator: Sora, Lumiere, Veo, Genie-2 |
| 76 | Cognitive maps and spatial cognition in AI |
| 77 | SLAM, online mapping, and place recognition for embodied agents |
| 78 | Intuitive physics and physical reasoning in LLMs and VLMs |
| 79 | Video games as AGI testbeds: MineDojo, Voyager, Cradle, GameNGen |
| 80 | VR / AR awareness: OpenXR, MR scene graphs for AI consumption |
| 81 | Vision-Language-Action models: RT-2, OpenVLA, π₀, Helix |
| 82 | Object-centric and slot-based representation learning |

### E. AGI Architectures & Cognitive Cores (83–90) — kernel + orchestration

| # | Title |
|---|---|
| 83 | Agentic foundation models: Claude, GPT-5, Gemini 2 agent stacks |
| 84 | Recursive self-improvement: STaR, ReST, self-rewarding LLMs |
| 85 | Neuro-symbolic AGI: AlphaProof, AlphaGeometry, hybrid agents |
| 86 | Dual-process cognition: System 1/2, fast/slow MoE, deliberation gating |
| 87 | Memory-of-thought and chain-of-memory reasoning |
| 88 | Long-horizon planning: LATS, RAP, MCTS-guided LLM planning |
| 89 | Computer-use agents: Claude Computer Use, OSWorld, Aria-UI |
| 90 | Autonomous research agents: AI Scientist, Agent Laboratory patterns |

### F. AI Operating System (91–96) — kernel + runtime + IPC

| # | Title |
|---|---|
| 91 | AI OS architecture: kernel, processes, memory hierarchy, scheduler |
| 92 | Process scheduling for cognitive systems: attention as a CPU |
| 93 | AI-native IPC: Model Context Protocol deep dive |
| 94 | Persistent agent state: file systems, snapshots, journals |
| 95 | Capability-based security for AI agents |
| 96 | Resource budgets: tokens, attention, energy as first-class quantities |

### G. Frontier 2025–2026 (97–100) — what to watch

| # | Title |
|---|---|
| 97 | Test-time compute scaling: o-series, DeepSeek-R1, reasoning models |
| 98 | Mechanistic interpretability at production scale: SAEs, circuits |
| 99 | Multi-modal foundation models for embodied agents (Gemini-Robotics-class) |
| 100 | Sovereign AI ethics: alignment for autonomous beings |

## 5. Inventory: done vs pending

| Phase | Status | Commit |
|---|---|---|
| P0 — TASK file + push | done | `2468dea` |
| B1 — docs 51–55 (Memory I) | done | `f2a1619` |
| B2 — docs 56–60 (Memory II + Self-awareness I) | done | `da40ab4` |
| B3 — docs 61–65 (Self-awareness II) | done | `aeff110` |
| B4 — docs 66–70 (Inner monologue + ToM) | done | `e784a05` |
| B5 — docs 71–75 (Social cognition + World models I) | done | `99349b3` |
| B6 — docs 76–80 (Spatial / SLAM / games / VR) | done | `90dfce4` |
| B7 — docs 81–85 (VLA + AGI I) | done | `c890451` |
| B8 — docs 86–90 (AGI II) | done | `09176a7` |
| B9 — docs 91–95 (AI OS I) | done | `ebdfff4` |
| B10 — docs 96–100 (AI OS II + frontier) | done | `858f812` |
| Closing — INDEX update + ADR-0005 + REPO_MAP + DEVLOG | done | (this commit) |

## 6. Progress tracker

Cadence: commit + push after each batch of 5 docs. Update this tracker in the same commit. Update `MEMORY.md` and `project_runa_agent_status.md` after each closing.

## 7. Next exact step

1. Commit + push this TASK file with INDEX placeholder section appended.
2. Begin B1 (docs 51–55).
3. After each batch: commit "research-2 BN: docs NN–MM — \<category\>" and push to origin/development.

## 8. Resumption protocol (in case of session break)

If a future session reads this file: continue from the first `pending` row in section 5. Open the latest commit, verify all preceding docs exist on disk, then proceed. Maintain numbering 51–100; do not reuse numbers from the first corpus.

---

*"Each entry must stand alone as a piece of useful knowledge. The corpus is research; the binding to subsystems happens at slice-time, not here."*
