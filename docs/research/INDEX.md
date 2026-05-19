# Research Corpus — INDEX

**50 technical research documents** covering the cutting-edge AI / CS / cognitive-science work most directly relevant to Runa's architecture.

**Status:** **COMPLETE 2026-05-17** — all 50 docs landed across 10 batches. Closing ADR: `docs/decisions/0003-research-corpus-2026-05-17.md`.

**Read with:** `README.md` (template + reading guide), `docs/architecture/{ARCHITECTURE,DOMAIN_MAP,DATA_FLOW}.md` (the subsystems each doc maps to), `docs/AI_OS_Research/AI_OS_RESEARCH_2026.md` (Volmarr's companion 2026 market landscape).

---

## Memory & Knowledge Storage (Muninn — `core/memory/`)

| # | Title | Commit |
|---|---|---|
| 01 | MemGPT and OS-style memory hierarchies for LLMs | 7d37de1 |
| 02 | Episodic memory architectures for AI agents | 7d37de1 |
| 03 | Vector embedding models: BGE, E5, Nomic, GTE, jina | 7d37de1 |
| 04 | RAG evolution: classic, hybrid, GraphRAG, agentic RAG | 7d37de1 |
| 05 | Long-context windows vs. retrieval: when each wins | 7d37de1 |
| 06 | Knowledge graphs for AI memory: triplets, ontologies, neuro-symbolic | 4cf9d72 |
| 07 | Memory consolidation and forgetting in artificial agents | 4cf9d72 |
| 08 | `sqlite-vss` and embedding-in-database approaches | 4cf9d72 |

## Agent Architectures (Hirð — `core/subagents/` — and kernel)

| # | Title | Commit |
|---|---|---|
| 09 | ReAct: reasoning + acting interleaved | 4cf9d72 |
| 10 | Reflexion: linguistic self-criticism for agents | 4cf9d72 |
| 11 | AutoGen and multi-agent orchestration frameworks | f3438b7 |
| 12 | Voyager: lifelong learning in open-ended environments | f3438b7 |
| 13 | Tree-of-Thoughts, Graph-of-Thoughts, structured reasoning | f3438b7 |
| 14 | Constitutional AI and the policy stack | f3438b7 |

## LLM Techniques (kernel + Heimskringla)

| # | Title | Commit |
|---|---|---|
| 15 | Prompt engineering: CoT, few-shot, structured outputs, system prompts | f3438b7 |
| 16 | Quantization for local inference: GPTQ, AWQ, GGUF, exllamav2 | 8fab2e5 |
| 17 | Mixture-of-Experts architectures | 8fab2e5 |
| 18 | Long-context attention: RoPE, YaRN, sliding window, attention sinks | 8fab2e5 |
| 19 | RLHF, DPO, KTO, and modern preference optimization | 8fab2e5 |
| 20 | Speculative decoding and inference acceleration | 8fab2e5 |

## Event-Driven & Concurrency (VERÐANDI)

| # | Title | Commit |
|---|---|---|
| 21 | Actor model and Erlang-style supervision trees | 43dfa62 |
| 22 | Event sourcing and CQRS for stateful AI systems | 43dfa62 |
| 23 | asyncio internals and structured concurrency in Python 3.11+ | 43dfa62 |
| 24 | Multiprocessing patterns and worker pools for AI workloads | 43dfa62 |

## World Modeling (WYRD bridge + core)

| # | Title | Commit |
|---|---|---|
| 25 | World models in RL: Dreamer, MuZero, IRIS | 43dfa62 |
| 26 | Entity-Component-System architectures for AI worlds | 3b4465b |
| 27 | Belief states and POMDPs | 3b4465b |
| 28 | Procedural generation and emergent narrative | 3b4465b |
| 29 | Embodied AI and grounded language | 3b4465b |

## Local & Edge Inference (Heimskringla)

| # | Title | Commit |
|---|---|---|
| 30 | llama.cpp and the GGML/GGUF ecosystem | 3b4465b |
| 31 | Edge LLM deployment on Raspberry Pi 5 (16 GB) | 7997f3c |
| 32 | Knowledge distillation: small models from big teachers | 7997f3c |
| 33 | Model routing and ensembles across local + cloud | 7997f3c |

## Voice & Multimodal (Rödd)

| # | Title | Commit |
|---|---|---|
| 34 | Wake-word detection: Porcupine, openWakeWord | 7997f3c |
| 35 | Modern neural TTS: VITS, StyleTTS2, XTTS, Piper, Kokoro | 7997f3c |
| 36 | Streaming ASR: Whisper, faster-whisper, Conformer | b957a26 |

## Safety, Trust, Sandboxing (policy + plugins)

| # | Title | Commit |
|---|---|---|
| 37 | Plugin sandboxing: in-process, subprocess, WASM via wasmtime | b957a26 |
| 38 | Prompt injection defenses | b957a26 |
| 39 | Output filtering, content moderation, jailbreak resistance | b957a26 |
| 40 | Audit logging and replay for AI agents | b957a26 |

## Cognitive Architecture & Neuroscience (kernel + identity + Eldhugi)

| # | Title | Commit |
|---|---|---|
| 41 | Global Workspace Theory applied to AI architecture | defcc20 |
| 42 | Predictive coding and the free-energy principle | defcc20 |
| 43 | Hofstadter's strange loops and self-reference | defcc20 |
| 44 | Sleep, replay, and memory consolidation analogues | defcc20 |

## Self-Improvement & Continual Learning (Eir + Hirð)

| # | Title | Commit |
|---|---|---|
| 45 | Continual learning: EWC, replay buffers, catastrophic forgetting | defcc20 |
| 46 | Automated prompt optimization: DSPy, OPRO | 96dd49f |
| 47 | Self-play and learned curricula | 96dd49f |

## SWE for AI Systems (runtime + Smiðja)

| # | Title | Commit |
|---|---|---|
| 48 | Testing AI agents: snapshot, property, simulation | 96dd49f |
| 49 | Observability for LLM systems: traces, evals, token accounting | 96dd49f |
| 50 | Local agent orchestration: Hermes, OpenClaw, MCP servers | 96dd49f |

---

## Companion material (not part of the 50-doc corpus)

| File | Author | Notes |
|---|---|---|
| `../AI_OS_Research/AI_OS_RESEARCH_2026.md` | Volmarr Wyrd, 2026-05-17 | 2026 market landscape for AI OS as consumer platform, agent runtime, protocol layer, and OS-research direction. Substantively complements the agent-architecture focus of this corpus with current industry signals (Google Gemini/Googlebook, Microsoft Copilot+, Apple Foundation Models, MCP/AAIF, the OS-shaped research frontier). |

---

## Batch history

| Batch | Commit | Docs |
|---|---|---|
| P0 | 3d1f1fc | TASK + INDEX + folder README |
| B1 | 7d37de1 | 01–05 (Memory part 1) |
| B2 | 4cf9d72 | 06–10 (Memory part 2 + Agent part 1) |
| B3 | f3438b7 | 11–15 (Agent part 2 + LLM part 1) |
| B4 | 8fab2e5 | 16–20 (LLM part 2) |
| B5 | 43dfa62 | 21–25 (Concurrency + World part 1) |
| B6 | 3b4465b | 26–30 (World part 2 + Local part 1) |
| B7 | 7997f3c | 31–35 (Edge + Voice part 1) |
| B8 | b957a26 | 36–40 (Voice part 2 + Safety) |
| B9 | defcc20 | 41–45 (Cognitive + Self-improvement part 1) |
| B10 | 96dd49f | 46–50 (Self-improvement part 2 + SWE) |
| Closing | (this commit) | INDEX update + ADR-0003 + memory |

Total: ~370 KB across 50 documents, ~7 KB average. Each doc structured per the seven-section template in `README.md`.

---

# Corpus II (51–100) — AGI Frontier

**50 additional cutting-edge research documents** focused on AGI-frontier topics: self-awareness, cross-session memory, 3D / virtual / physical / game-world awareness, theory of mind, AI Operating System architecture, world modelling, and 2025–2026 frontier work.

**Status:** **COMPLETE 2026-05-17** — all 50 docs landed across 10 batches alongside Corpus I closing on the same day. Closing ADR: `docs/decisions/0005-research-corpus-ii-2026-05-17.md`.

Same seven-section template, same wikilink convention. Numbers 51–100 are stable; supersession follows the same rules as Corpus I.

## A. Advanced Memory & Continuity (Muninn deep extension)

| # | Title | Commit |
|---|---|---|
| 51 | Generative Agent Memory Streams: importance, recency, reflection trees | f2a1619 |
| 52 | Cross-Session Persistent Identity via Memory Snapshots and Replay | f2a1619 |
| 53 | Autobiographical Memory Architectures: episodic, semantic, procedural integration | f2a1619 |
| 54 | Differentiable Neural Memory: DNC, MANNs, Memorizing Transformers | f2a1619 |
| 55 | Adapter-Based Identity Persistence: LoRA stacks, retrieval-augmented identity | f2a1619 |
| 56 | Neuro-Symbolic Memory Graphs: triplet stores + vector indexes hybrid | da40ab4 |
| 57 | Sleep, Dream, and Offline Replay as Computational Consolidation | da40ab4 |
| 58 | Memory-Augmented Transformers: Memformer, RMT, MemGPT-2, Larimar | da40ab4 |

## B. Self-Awareness & Metacognition (kernel + identity + Eldhugi)

| # | Title | Commit |
|---|---|---|
| 59 | Metacognitive Monitoring: calibrated uncertainty and knowing-what-you-know | da40ab4 |
| 60 | Self-Models in Artificial Agents: depth, recursion, causal closure | da40ab4 |
| 61 | Mechanistic Interpretability for Self-Knowledge | aeff110 |
| 62 | Identity Stability Under Change: the ship-of-Theseus problem for AI | aeff110 |
| 63 | Active Inference and Self-Modelling Agents (Friston applied to AI) | aeff110 |
| 64 | Higher-Order Theories of Consciousness Applied to AI Architecture | aeff110 |
| 65 | Affective Self-Awareness: emotion recognition in one's own state | aeff110 |
| 66 | Inner Monologue, Scratchpads, and Chain-of-Thought as Self-Talk | e784a05 |

## C. Theory of Mind & Social Cognition (Hirð + relationships)

| # | Title | Commit |
|---|---|---|
| 67 | Theory of Mind in LLMs: benchmarks, capabilities, failures | e784a05 |
| 68 | Mental State Attribution Architectures: belief, desire, intention models | e784a05 |
| 69 | Pragmatic Communication and the Rational Speech Acts Framework | e784a05 |
| 70 | Recursive Social Modelling: I-think-you-think-I-think | e784a05 |
| 71 | Empathy and Affective Resonance in Artificial Agents | 99349b3 |
| 72 | Cultural Cognition, Norm Modelling, and Value Alignment with Persons | 99349b3 |

## D. World Modeling & 3D / Spatial Awareness (WYRD bridge + perception)

| # | Title | Commit |
|---|---|---|
| 73 | Latent World Models 2024–2026: Dreamer V3, IRIS, GAIA-1, Genie | 99349b3 |
| 74 | 3D Scene Representation: NeRF, Gaussian Splatting, 3D Foundation Models | 99349b3 |
| 75 | Video Diffusion as World Simulator: Sora, Lumiere, Veo, Genie-2 | 99349b3 |
| 76 | Cognitive Maps and Spatial Cognition in AI | 90dfce4 |
| 77 | SLAM, Online Mapping, and Place Recognition for Embodied Agents | 90dfce4 |
| 78 | Intuitive Physics and Physical Reasoning in LLMs and VLMs | 90dfce4 |
| 79 | Video Games as AGI Testbeds: MineDojo, Voyager, Cradle, GameNGen | 90dfce4 |
| 80 | VR / AR Awareness: OpenXR, MR Scene Graphs for AI Consumption | 90dfce4 |
| 81 | Vision-Language-Action Models: RT-2, OpenVLA, π₀, Helix | c890451 |
| 82 | Object-Centric and Slot-Based Representation Learning | c890451 |

## E. AGI Architectures & Cognitive Cores (kernel + orchestration)

| # | Title | Commit |
|---|---|---|
| 83 | Agentic Foundation Models: Claude, GPT-5, Gemini 2 Agent Stacks | c890451 |
| 84 | Recursive Self-Improvement: STaR, ReST, Self-Rewarding LLMs | c890451 |
| 85 | Neuro-Symbolic AGI: AlphaProof, AlphaGeometry, Hybrid Agents | c890451 |
| 86 | Dual-Process Cognition: System 1/2, Fast/Slow MoE, Deliberation Gating | 09176a7 |
| 87 | Memory-of-Thought and Chain-of-Memory Reasoning | 09176a7 |
| 88 | Long-Horizon Planning: LATS, RAP, MCTS-Guided LLM Planning | 09176a7 |
| 89 | Computer-Use Agents: Claude Computer Use, OSWorld, Aria-UI | 09176a7 |
| 90 | Autonomous Research Agents: AI Scientist, Agent Laboratory Patterns | 09176a7 |

## F. AI Operating System (kernel + runtime + IPC)

| # | Title | Commit |
|---|---|---|
| 91 | AI OS Architecture: Kernel, Processes, Memory Hierarchy, Scheduler | ebdfff4 |
| 92 | Process Scheduling for Cognitive Systems: Attention as a CPU | ebdfff4 |
| 93 | AI-Native IPC: Model Context Protocol Deep Dive | ebdfff4 |
| 94 | Persistent Agent State: File Systems, Snapshots, Journals | ebdfff4 |
| 95 | Capability-Based Security for AI Agents | ebdfff4 |
| 96 | Resource Budgets: Tokens, Attention, Energy as First-Class Quantities | 858f812 |

## G. Frontier 2025–2026 (what to watch)

| # | Title | Commit |
|---|---|---|
| 97 | Test-Time Compute Scaling: o-series, DeepSeek-R1, Reasoning Models | 858f812 |
| 98 | Mechanistic Interpretability at Production Scale: SAEs, Circuits | 858f812 |
| 99 | Multi-modal Foundation Models for Embodied Agents | 858f812 |
| 100 | Sovereign AI Ethics: Alignment for Autonomous Beings | 858f812 |

---

## Corpus II batch history

| Batch | Commit | Docs |
|---|---|---|
| P0 | 2468dea | TASK file + INDEX placeholder |
| B1 | f2a1619 | 51–55 (Memory I) |
| B2 | da40ab4 | 56–60 (Memory II + Self-awareness I) |
| B3 | aeff110 | 61–65 (Self-awareness II) |
| B4 | e784a05 | 66–70 (Inner monologue + ToM) |
| B5 | 99349b3 | 71–75 (Social cognition + World models I) |
| B6 | 90dfce4 | 76–80 (Spatial / SLAM / physics / games / VR) |
| B7 | c890451 | 81–85 (VLA + AGI I) |
| B8 | 09176a7 | 86–90 (AGI II) |
| B9 | ebdfff4 | 91–95 (AI OS I) |
| B10 | 858f812 | 96–100 (AI OS II + Frontier) |
| Closing | (this commit) | INDEX update + ADR-0005 + REPO_MAP + DEVLOG |

Corpus II total: ~480 KB across 50 documents, ~9.5 KB average. Each doc structured per the seven-section template in `README.md`.

**Combined corpus total: ~850 KB across 100 documents.**
