# 33 — Model Routing and Ensembles Across Local + Cloud

**Category:** Local & Edge Inference
**Runa relevance:** Heimskringla (the entire subsystem), Hirð (per-retainer model choice)
**Status:** Research synthesis. Centrally relevant to Heimskringla design.
**Last touched:** 2026-05-17

---

## 1. Core idea

In 2026, a sovereign agent like Runa has access to a *zoo* of language models: small fast local models (TinyLlama, Phi-3-mini), capable local models (Llama-3.1-8B, Mistral Nemo), big local models (Mixtral 8x22B if you have the RAM), and cloud-hosted frontier models (Claude family, GPT family, Gemini, OpenRouter as aggregator). Each has its own cost curve, latency profile, capability profile, and trust profile.

**Model routing** is the discipline of picking the right model for each request. **Model ensembles / mixture-of-agents** is the related idea of running *multiple models in parallel or sequence* and combining their outputs for quality. Both have been active research areas as the model zoo grew, and both directly inform Heimskringla's design.

The simplest router — "use the cheapest model that won't embarrass the agent" — captures most of the value. The more sophisticated patterns — learned routers that classify query difficulty, ensembles that vote, cascades that escalate on uncertainty — earn the rest.

## 2. Technical depth

**The decision factors a router juggles:**

| Factor | Why it matters |
|---|---|
| **Capability fit** | Math problem → strong reasoning model. Casual chat → small model is fine. |
| **Latency budget** | Voice turn requires <500 ms TTFT. Background task can take seconds. |
| **Cost budget** | Per-call dollar cost for cloud; per-second power cost for local. |
| **Privacy / trust** | Some content shouldn't leave the local machine. |
| **Context length** | Long context goes to long-context-capable providers. |
| **Tool use needs** | Native function-calling requires capable providers. |
| **Caching state** | Cloud providers' context caching changes economics for repeated prompts. |
| **Reliability** | Availability history per provider. |

**Routing strategies (in order of sophistication):**

**1. Static rules.** Simple `if/else` based on task type, prompt length, etc. Trivial; the right starting point.

```
def route(request):
    if request.surface == "voice":
        return "phi3-mini-local"
    if request.expected_tokens > 50000:
        return "claude-sonnet"
    if request.task_type == "code":
        return "llama-3.1-8b-local"
    return "llama-3.1-8b-local"
```

**2. Heuristic difficulty estimators.** Use the prompt's length, presence of certain keywords ("prove that", "write code", "summarise"), or a cheap classifier model to predict whether a strong model is warranted.

**3. Learned classifier router.** Train a small model on (prompt, model_used, quality_score) triples to predict which model gives the best quality/cost trade-off for a given prompt. RouteLLM (Ong et al., 2024) is a published example.

**4. Cascade with verifier.** Route to cheapest model first; if the verifier (rule-based, learned, or LLM-as-judge) doesn't accept the answer, escalate to a stronger model. Pays the cheap cost most of the time.

**5. Mixture-of-Agents** (Wang et al., 2024, arXiv:2406.04692). Run multiple models in parallel, then combine their answers with a third model. Quality often exceeds the best single model. High cost.

**6. Speculative cross-model.** A fast model drafts; a strong model verifies in batched parallel ([[20-speculative-decoding]]). Pays strong-model cost only on rejections.

**Architectural patterns:**

```
                ┌─────────────────────────────────┐
                │           Heimskringla           │
                │                                  │
                │   ┌──────────┐  ┌──────────┐    │
                │   │ Router   │  │ Cache    │    │
                │   │ (per-req)│  │ (per-prv)│    │
                │   └──────────┘  └──────────┘    │
                │                                  │
                │   ┌──────────────────────────┐   │
                │   │ Provider adapters         │   │
                │   ├──────────────────────────┤   │
                │   │ • ollama (local)          │   │
                │   │ • lmstudio (local)        │   │
                │   │ • llama-cpp (local)       │   │
                │   │ • openrouter (cloud)      │   │
                │   │ • anthropic (cloud)       │   │
                │   │ • nous (cloud)            │   │
                │   │ • home-server (Tailnet)   │   │
                │   └──────────────────────────┘   │
                │                                  │
                │   ┌──────────────────────────┐   │
                │   │ Budget tracker            │   │
                │   │ Failure-history tracker   │   │
                │   │ Per-provider rate limiter │   │
                │   └──────────────────────────┘   │
                └─────────────────────────────────┘
```

**Cost models per provider:**

- Local: power-draw cost (~$0.0001 per 1K tokens at home electricity prices), latency cost, memory occupancy cost. Effectively free; the constraint is throughput.
- Cloud: per-token dollar cost, varies wildly. Modern frontier ranges $0.50-$15 per million input tokens, $1.50-$75 per million output tokens. Major variation across providers and tiers.
- OpenRouter: aggregator markup (~5-10%) for flexible routing. Useful for trying many models without separate accounts.

**Ensembles and mixture-of-agents:**

- **Mixture-of-Agents** (Wang et al., 2024): proposers + aggregator. Multiple LLMs propose answers in layer 1; an aggregator synthesises in layer 2 (or further layers iterate).
- **Self-consistency** (Wang et al., 2022, see [[13-tree-of-thoughts-structured-reasoning]]): N samples from one model, majority vote.
- **Cascade verification**: cheap model first, expensive model verifies, only-correct outputs proceed.

## 3. Key works

- **Ong et al. "RouteLLM: Learning to Route LLMs with Preference Data."** arXiv:2406.18665, 2024.
- **Wang et al. "Mixture-of-Agents Enhances Large Language Model Capabilities."** arXiv:2406.04692, 2024.
- **Chen et al. "FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance."** arXiv:2305.05176, 2023.
- **Lu et al. "LLM-Blender: Ensembling Large Language Models with Pairwise Ranking and Generative Fusion."** arXiv:2306.02561, 2023.
- **Hari et al. "TryAge: Adaptive Routing in Multi-Model Systems."** arXiv:2305.05176-related, 2023.
- **LiteLLM** — github.com/BerriAI/litellm. Production-grade multi-provider router library.
- **LangChain's model abstraction layer** — varying quality, but widely used.
- **portkey-ai** — gateway service for multi-LLM routing.

## 4. Empirical results

- **FrugalGPT** demonstrated cost reductions of up to 98% (vs always using GPT-4) with cascade routing while *improving* accuracy on selected tasks. Headline number; depends on workload mix.
- **RouteLLM:** learned router improved cost-quality Pareto frontier by 30-80% over single-model baselines on standard benchmarks.
- **Mixture-of-Agents:** 6.5 percentage points over best single model on AlpacaEval 2.0 with 3-4 models in the ensemble. Strong but expensive.
- **Cascading with strong verifier:** when verifier is well-calibrated, near-frontier quality at fraction-of-frontier cost. Verifier quality bounds outcome.
- **Latency variance:** within a single provider, latency varies 10-100× by hour-of-day. Real-world routing should consider current observed latency, not advertised.

## 5. Applicability to Runa

This research maps directly to Heimskringla's design.

For **Heimskringla v0**:

- **Static rule router.** Suffices for the first slice. Examples:
  - voice surface → local Phi-3-mini.
  - long context (>30K tokens) → cloud (Claude).
  - codegen → CodeLlama-7B-Instruct local OR Claude Sonnet cloud per task complexity.
  - default chat → local Llama-3.1-8B Q4_K_M.
- **Per-provider cache.** Per ADR-0002 §D-2.4.
- **Semantic-dedup cache** sitting over all providers. Per ADR-0002 §D-2.4.
- **Budget tracker.** Daily cloud-token budget, hard cap with operator-visible warnings.
- **Failure-history tracker.** A provider that's failed thrice in five minutes gets quarantined; Heimskringla routes around.

For **Heimskringla v1.x**:

- **Heuristic difficulty estimator** as a cheap classifier (Phi-3-mini run locally) deciding "this needs the big model" vs "this is fine with the small one".
- **Cascade pattern** for tasks with verifiable outputs (codegen, math, structured answers): cheap-first, verify, escalate.

For **Hirð per-retainer routing**:

- Each retainer has a *preferred* model and an *escalation* model. Huginn (research) prefers a fast small local for first-pass synthesis, escalates to cloud for hard syntheses. Eir (diagnosis) is fine with a smaller model — diagnostic patterns are narrow.

For **Mixture-of-Agents (selectively)**:

- Reserve for "council" tasks (multi-retainer debate on hard questions, see [[11-autogen-multi-agent]]). Not the default; budget-aware.

What to avoid:

- Don't route blindly without a budget cap. Cloud cost is unbounded by default; one runaway loop can rack up serious money.
- Don't route based on advertised provider capability without empirical verification. Some providers' actual quality drifts from their marketing.
- Don't add ensemble / mixture-of-agents to every turn. The cost multiplier is real.
- Don't ignore local. Many turns genuinely don't need cloud, and the privacy + latency wins compound.
- Don't bypass the router. Code that hardcodes a specific provider undermines the whole abstraction.

## 6. Open questions

- **Cost-aware quality estimation.** When the router considers escalating, it's making a "value" decision. The right utility function for "this query is worth $0.05 of cloud cost" is unclear.
- **Adaptive routing under drift.** Providers change behaviour over time (model updates, training data, capability gains). Routers calibrated on old data drift.
- **Multi-objective routing.** Cost, latency, quality, privacy, reliability — these don't reduce to a scalar. Pareto-optimal routing under multiple constraints is open.
- **Routing for tool use.** Models vary widely in tool-use ability and format. Routing decisions should account for this; few systems do.

## 7. References (curated)

- arXiv:2406.18665 — RouteLLM.
- arXiv:2406.04692 — Mixture-of-Agents.
- arXiv:2305.05176 — FrugalGPT.
- arXiv:2306.02561 — LLM-Blender.
- github.com/BerriAI/litellm — LiteLLM router.
- portkey.ai — Portkey gateway.
- openrouter.ai — OpenRouter (the cloud aggregator most flexible for routing).
- Companion docs: [[16-quantization-local-inference]], [[20-speculative-decoding]], [[30-llama-cpp-gguf-ecosystem]], [[31-edge-llm-pi5]].
- Anchored decision: ADR-0002 §D-2.4 (cache strategy that interacts with routing).
