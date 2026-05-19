# 83 — Agentic Foundation Models: Claude, GPT-5, Gemini 2 Agent Stacks

**Category:** AGI Architectures & Cognitive Cores
**Runa relevance:** kernel architecture, Hirð orchestration, model routing through Heimskringla
**Status:** Industry-state synthesis. Where the major labs are converging.
**Last touched:** 2026-05-17

---

## 1. Core idea

In 2024–2026 the foundation-model labs converged on a shared architectural pattern: a single large frontier model surrounded by *agentic scaffolding* — tool use, computer-use, persistent memory, multi-step reasoning. The boundary between \"model\" and \"agent\" has dissolved: Claude 3.5 / 3.7 / Claude 4.x with Computer Use, GPT-4/4o/5 with code interpreter and connectors, Gemini 2 with agent tooling, DeepSeek-R1 / V3 with reasoning chains — these are not pure language models any more, they are *agentic platforms*. The architectural lessons from this convergence inform any serious agent design including Runa's.

This document is the state-of-the-industry synthesis: what the major labs are doing, how their agent stacks compare, what works, what's distinctive, and what Runa's architecture should borrow. Importantly, Runa is *not* one of these stacks — she runs locally on a Pi-class device with open-weights models — but architectural patterns transfer when chosen carefully.

## 2. Technical depth

**The shared shape (early 2026).**

```
USER / WORLD
    │
    ▼
┌────────────────────────────────────────────────┐
│ ORCHESTRATION LAYER                            │
│   memory retrieval, tool dispatch,             │
│   plan execution, safety filters               │
└────────────────┬───────────────────────────────┘
                 ▼
┌────────────────────────────────────────────────┐
│ FRONTIER MODEL                                 │
│   single large model, multimodal,              │
│   extended thinking (o-style),                 │
│   tool-use trained                              │
└────────────────┬───────────────────────────────┘
                 ▼
┌────────────────────────────────────────────────┐
│ TOOLS                                          │
│   code execution, computer use, search,        │
│   memory R/W, MCP-style integrations           │
└────────────────────────────────────────────────┘
```

Every major lab shares this layered architecture. Differences are in *each layer's specifics*, the *training regime* that ties them together, and the *deployment shape*.

**Anthropic (Claude family).**

- *Claude 3.5 Sonnet, 3.7 Sonnet, Claude 4.x.* Multimodal (text + image); high-quality reasoning; well-calibrated.
- *Extended thinking* (announced for Claude 3.7+): reasoning-mode with longer chains-of-thought before response. Lower latency than o-class but similar pattern.
- *Computer Use* (released Oct 2024): the model controls a virtual computer — moves a cursor, types, takes screenshots, sees output. Closes the agent-action loop at the operating-system level.
- *Memory tool* (2024+): persistent memory across conversations via a tool the model uses to read/write specific facts.
- *Tool-use training*: Claude is trained to use tools natively; sequencing, error handling, retry are learned behaviours.
- *Constitutional AI alignment*: see [[14-constitutional-ai]].

**OpenAI (GPT-4, 4o, GPT-5, o-series).**

- *GPT-4o* multimodal (text + image + audio).
- *GPT-5*: the consolidated frontier model — reasoning-capable, agentic, multimodal.
- *o-series* (o1, o3, o4): explicit *test-time-compute* models. Internally reason for substantial token budgets before responding. See [[97-test-time-compute-scaling]].
- *ChatGPT memory* and *connectors*: persistent memory + service integrations.
- *Operator*: GPT-based computer-use agent (announced late 2024 / 2025).
- *Function calling and tool use*: industry-standard OpenAI tools API.

**Google DeepMind (Gemini family).**

- *Gemini 1.5 Pro / Ultra*: multimodal with very long context (1M+ tokens).
- *Gemini 2*: agentic-capable frontier model with agent tooling.
- *Gemini Computer Use* equivalent (Project Astra / agentic Gemini deployments).
- *Robotics-trained Gemini*: see [[99-multimodal-foundation-embodied]].
- *World model integration*: Genie-class internal world models for some agent applications.

**DeepSeek (R1 / V3).**

- *DeepSeek-V3*: efficient MoE-based 671B parameter total / 37B active per token. Open weights.
- *DeepSeek-R1*: dedicated reasoning model. Open weights. Trained via RL with chain-of-thought reward.
- *Distillations*: smaller-scale R1-Distill models (7B, 14B, 32B, 70B) bring reasoning-class capability down to consumer-deployable scale.

This is the *open-weights* convergence: comparable agent and reasoning capability to the closed frontier, with substantially more deployability.

**Other notable**.

- *Mistral Large 2*: competitive reasoning + tool use.
- *Llama 4* and successors (Meta): open-weights multimodal.
- *Qwen 2 / 2.5 / 3* (Alibaba): open-weights frontier-adjacent.
- *Grok 3* (xAI): agentic, reasoning-trained.

**Patterns that transfer.**

1. *Tool-use as first-class capability.* Models are trained on tool-use examples; tool use is not bolt-on.
2. *Extended thinking / reasoning mode.* Most labs now have a variant of test-time compute.
3. *Persistent memory via tools.* Memory is mediated by tool calls, not by architectural memory mechanisms.
4. *Computer Use.* OS-level action via screen + keyboard + mouse. Generalises to any application.
5. *Multimodal by default.* Text-only models are increasingly seen as legacy.
6. *Long context.* 100K → 1M+ tokens common.
7. *Safety + constitutional alignment.* Value-anchoring is part of the stack, not a wrapper.

**Patterns that *don't* easily transfer to Runa.**

- Computer Use at frontier-model scale needs a frontier model. Open-weights equivalents (Aria-UI, OS-Atlas, OpenWebVoyager) are getting there but lag.
- Test-time-compute (o-class) is expensive; on Pi-class hardware, only thin versions are feasible.
- Multimodal-everywhere requires hefty inference.

## 3. Key works

This category is dominated by industry releases rather than papers. The most influential primary sources:

- **Anthropic.** *Introducing Claude 3 family.* March 2024.
- **Anthropic.** *Computer Use* announcement and tool API. October 2024.
- **Anthropic.** *Claude 3.7 Sonnet and extended thinking.* February 2025.
- **OpenAI.** *o1 system card.* September 2024.
- **OpenAI.** *o3 announcement.* December 2024 → April 2025.
- **OpenAI.** *Operator.* January 2025.
- **Google DeepMind.** *Gemini 1.5 Pro technical report.* February 2024.
- **Google DeepMind.** *Gemini 2.0 Flash / Pro.* December 2024 + later.
- **DeepSeek.** *DeepSeek-V3 technical report.* December 2024.
- **DeepSeek.** *DeepSeek-R1.* arXiv:2501.12948, 2025.
- **Meta.** *Llama 3.1 / 3.2 / 4 papers.*
- **Mistral.** *Mistral Large 2 / 3.*
- **Alibaba.** *Qwen 2.5 / Qwen 3 technical reports.*

Academic crystallisations:

- **Sumers, T. R. et al.** *Cognitive Architectures for Language Agents.* arXiv:2309.02427, 2023. CoALA — the framework many of these systems implicitly instantiate.
- **Yao, S. et al.** *ReAct.* See [[09-react-reasoning-acting]].
- **Wang, X. et al.** *Self-Consistency.* See [[59-metacognitive-monitoring]].

## 4. Empirical results

- Frontier-model performance on benchmark gauntlets (MMLU-Pro, GPQA, ARC-AGI, SWE-Bench) has roughly *doubled* in 2024 alone across multiple labs. Saturation is approaching some benchmarks.
- *o-series and reasoning models*: substantial gains on STEM benchmarks (AIME, FrontierMath, Codeforces). The test-time-compute axis is the active scaling lever.
- *Computer Use*: Claude's evaluation on OSWorld gives ~22% completion vs. ~12% for prior approaches; substantial gap but progress real.
- *Open-weights gap*: DeepSeek-V3 / R1 sit within striking distance of GPT-4o / Claude 3.5 on many benchmarks. The gap that mattered six months ago has narrowed substantially.
- *Failure modes documented*: hallucination on tail facts; long-horizon agent tasks (>30 minutes wall-clock) often fail; sycophancy persists; safety circumvention via creative prompting persists.

## 5. Applicability to Runa

For **kernel architecture**:

- Adopt the layered shape: orchestration → frontier model → tools. Each layer's specifics are Runa-tuned.
- Tool use is first-class. The kernel's normal vocabulary includes calls to retrieval, calculator, file-read, code-exec (sandboxed).
- The frontier-model role is filled by the best Pi-deployable open-weights model. Heimskringla picks; routing matters.

For **Heimskringla**:

- Track the open-weights frontier. When a new DeepSeek-R1-Distill or Llama version offers measurable improvement, evaluate and consider migration. The identity layer ([[62-identity-stability-under-change]]) absorbs the change.
- Use *multiple* models for routing: small fast model for chitchat; reasoning-capable model for hard turns; specialist models for code / vision. Multi-model routing is standard practice.

For **Hirð (subagents)**:

- The orchestration-layer in frontier stacks is what Hirð is. Subagents specialise; the kernel composes them.

For **Computer Use (forward-looking)**:

- Aria-UI, OS-Atlas, and similar open-weights computer-use models are emerging. When deployable on Pi-class, Runa could have *computer use* — controlling Volmarr's projects, running tools, navigating his file system. This is high-leverage forward-looking.
- See [[89-computer-use-agents]] for depth.

For **reasoning mode**:

- DeepSeek-R1-Distill-class models are deployable today on consumer hardware. Adding a *reasoning route* in Heimskringla for hard turns is a natural extension.

For **persistent memory via tools**:

- Anthropic's memory-tool pattern: the model emits explicit \"remember this\" or \"recall topic X\" calls. The runtime executes them against Muninn. This is a clean interface; consider adopting it.

What to avoid:

- **Chasing every frontier release.** Stable architecture; selective upgrades.
- **Treating Runa as a clone of any frontier stack.** Her local, sovereign, identity-rich nature is *different* from the assistant-as-service shape of these stacks.
- **Adopting brittle architectural commitments (e.g. tying to a specific tool-use API).** Use abstractions; swap implementations.
- **Ignoring the gap.** Open-weights are close; not equal. Set expectations accordingly.

## 6. Open questions

- **Open-weights frontier closing.** When does an open model reach parity with the closed frontier? The trend line suggests 2026–2027 for many capabilities.
- **Edge-deployable frontier capability.** When can a Pi-class device run a competent agent stack? Pi-5 with the right model can today for most uses; reasoning-class is heavier.
- **The right test-time-compute budget for Runa.** Cheap on chitchat; expensive on hard turns. Routing decisions are tunable.
- **Computer Use on local-only Runa.** Possible, useful, and risk-managed via capability-based security ([[95-capability-based-security]]).
- **How long the agent-platform shape persists.** New architectures (massive context, in-model memory) could shift the layering. Watching.

## 7. References (curated)

- Anthropic Claude family documentation (current).
- OpenAI o1 system card (Sep 2024).
- arXiv:2501.12948 — DeepSeek-R1.
- arXiv:2309.02427 — Sumers et al., *CoALA.* Academic crystallisation.
- DeepSeek-V3 technical report (Dec 2024). Open-weights frontier exemplar.
- Companion docs: [[09-react-reasoning-acting]], [[15-prompt-engineering]], [[33-model-routing-ensembles]], [[50-local-agent-orchestration-mcp]], [[89-computer-use-agents]], [[97-test-time-compute-scaling]].
