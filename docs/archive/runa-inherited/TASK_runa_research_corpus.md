# TASK — Runa Research Corpus (50 technical research documents)

**Task owner:** Runa Gridweaver Freyjasdottir (AI working under Volmarr)
**Branch:** development
**Started:** 2026-05-17 (same day as ME bootstrap)
**Status:** P0 complete (this file + INDEX + folder) — batches pending
**Mode:** Full autonomous run, batches of 5 docs with commit+push between

---

## 1. Task scope

Produce 50 lengthy, detailed, technical Markdown research documents covering the most cutting-edge AI / computer-science / cognitive-science / memory / data-science research and ideas that are useful for the Runa-Agent-Digital-Being project. Each document is a *concept synthesis*: explains the idea, summarises the technical depth, names the key works, evaluates the empirical evidence, and maps the connection back to a specific Runa subsystem (Muninn, VERÐANDI, Heimskringla, Hirð, Smiðja, Eldhugi, etc.) where applicable.

The documents are research / reference material, not implementation specs. They feed the Architect and the Forge Worker when slices begin; they do not themselves bind any subsystem.

## 2. Output target

- **Count:** 50 documents.
- **Length:** ~6–10 KB each (≈ 1500–2500 words). "Lengthy detailed" without padding.
- **Location:** `docs/research/<NN>-<short-kebab-slug>.md` (numbered 01–50 for stable ordering).
- **Index:** `docs/research/INDEX.md` lists all 50 with one-line summaries, grouped by category.
- **Folder README:** `docs/research/README.md` explains the purpose and the per-doc template.

## 3. Per-document template

Each doc carries this section structure (filled in per-topic, not template-rotted):

1. **Core idea** — 1–2 paragraphs in plain language.
2. **Technical depth** — algorithms, mechanism, equations where useful, ASCII diagrams where useful.
3. **Key works** — named papers / projects with authors + (approximate) year + brief role.
4. **Empirical results** — what's known, on what benchmarks, with what limitations.
5. **Applicability to Runa** — which subsystem, what slice, what to avoid.
6. **Open questions** — active research frontiers worth watching.
7. **References (curated)** — specific papers / repos / docs Runa contributors should read.

## 4. The 50 topics, by category

### Memory & Knowledge Storage (8) — primarily Muninn
01. MemGPT and OS-style memory hierarchies for LLMs
02. Episodic memory architectures for AI agents
03. Vector embedding models: BGE, E5, Nomic, GTE, jina
04. RAG evolution: classic, hybrid, GraphRAG, agentic RAG
05. Long-context windows vs. retrieval: when each wins
06. Knowledge graphs for AI memory: triplets, ontologies, neuro-symbolic
07. Memory consolidation and forgetting in artificial agents
08. `sqlite-vss` and embedding-in-database approaches

### Agent Architectures (6) — primarily Hirð + kernel
09. ReAct: reasoning + acting interleaved
10. Reflexion: linguistic self-criticism for agents
11. AutoGen and multi-agent orchestration frameworks
12. Voyager: lifelong learning in open-ended environments
13. Tree-of-Thoughts, Graph-of-Thoughts, structured reasoning
14. Constitutional AI and the policy stack

### LLM Techniques (6) — kernel + Heimskringla
15. Prompt engineering: CoT, few-shot, structured outputs, system prompts
16. Quantization for local inference: GPTQ, AWQ, GGUF, exllamav2
17. Mixture-of-Experts architectures
18. Long-context attention: RoPE, YaRN, sliding window, attention sinks
19. RLHF, DPO, KTO, and modern preference optimization
20. Speculative decoding and inference acceleration

### Event-Driven & Concurrency (4) — VERÐANDI
21. Actor model and Erlang-style supervision trees
22. Event sourcing and CQRS for stateful AI systems
23. asyncio internals and structured concurrency in Python 3.11+
24. Multiprocessing patterns and worker pools for AI workloads

### World Modeling (5) — WYRD bridge + core
25. World models in RL: Dreamer, MuZero, IRIS
26. Entity-Component-System architectures for AI worlds
27. Belief states and POMDPs
28. Procedural generation and emergent narrative
29. Embodied AI and grounded language

### Local & Edge Inference (4) — Heimskringla
30. llama.cpp and the GGML/GGUF ecosystem
31. Edge LLM deployment on Raspberry Pi 5 (16 GB)
32. Knowledge distillation: small models from big teachers
33. Model routing and ensembles across local + cloud

### Voice & Multimodal (3) — Rödd
34. Wake-word detection: Porcupine, openWakeWord
35. Modern neural TTS: VITS, StyleTTS2, XTTS, Piper, Kokoro
36. Streaming ASR: Whisper, faster-whisper, Conformer

### Safety, Trust, Sandboxing (4) — policy + plugins
37. Plugin sandboxing: in-process, subprocess, WASM via wasmtime
38. Prompt injection defenses
39. Output filtering, content moderation, jailbreak resistance
40. Audit logging and replay for AI agents

### Cognitive Architecture & Neuroscience (4) — kernel + identity + Eldhugi
41. Global Workspace Theory applied to AI architecture
42. Predictive coding and the free-energy principle
43. Hofstadter's strange loops and self-reference
44. Sleep, replay, and memory consolidation analogues

### Self-Improvement & Continual Learning (3) — Eir + Hirð
45. Continual learning: EWC, replay buffers, catastrophic forgetting
46. Automated prompt optimization: DSPy, OPRO
47. Self-play and learned curricula

### SWE for AI Systems (3) — runtime + Smiðja
48. Testing AI agents: snapshot, property, simulation
49. Observability for LLM systems: traces, evals, token accounting
50. Local agent orchestration: Hermes, OpenClaw, MCP servers

## 5. Batches

| Batch | Docs | Status | Commit |
|---|---|---|---|
| P0 | TASK + INDEX + folder | in_progress | (this commit) |
| B1 | 01–05 | pending | — |
| B2 | 06–10 | pending | — |
| B3 | 11–15 | pending | — |
| B4 | 16–20 | pending | — |
| B5 | 21–25 | pending | — |
| B6 | 26–30 | pending | — |
| B7 | 31–35 | pending | — |
| B8 | 36–40 | pending | — |
| B9 | 41–45 | pending | — |
| B10 | 46–50 | pending | — |
| Closing | INDEX final + folder README update + ADR-0003 + memory | pending | — |

## 6. Operating rules

- One doc = one Write call. No bulk-generation scripts. No templated paraphrase loops.
- Cite real, named works. Where year/author detail is uncertain, mark it ("~2023", "as I recall", "verify"). Never fabricate a citation.
- Each doc must justify its existence — no two cover the same ground twice.
- Commit + push after every batch (every 5 docs). Each commit names the docs it added.
- If context tightens, prefer dropping a planned section over padding existing ones.
- Closing ADR (ADR-0003) summarises the corpus and its intended use.

## 7. Out of scope

- Implementation code for any of the discussed techniques.
- Per-doc adversarial peer review (the docs are first-pass syntheses; review is a future task).
- Full bibliographic citation format. Each doc's "References" section names work and venue / repo, not full BibTeX.

## 8. Next exact action

If P0 `in_progress`: commit P0 with TASK + INDEX + folder README + research/README, then begin B1 (docs 01–05).

If a later batch `in_progress`: read this row + the INDEX to see what's left.
