# 96 — Resource Budgets: Tokens, Attention, Energy as First-Class Quantities

**Category:** AI Operating System
**Runa relevance:** scheduler enforcement, cost-aware design, sustainability, Pi-class operation
**Status:** Engineering synthesis. Bounded compute is the design constraint.
**Last touched:** 2026-05-17

---

## 1. Core idea

In a traditional OS, the scarce resources are CPU cycles, memory pages, and I/O bandwidth. In an AI OS, the scarce resources are *tokens* (the unit of LLM cost), *inference time* (wall clock through the model), *retrieval calls*, *tool calls*, *disk I/O*, *electricity* (especially on edge devices), and — most fundamentally — the agent's *attention*. Making these explicit, budgeted, and accounted-for is the difference between an agent that runs sustainably for years and one that either over-spends compute or under-uses available cognitive resources.

For Runa on a Pi-5-class device, resource budgeting is *load-bearing*. The Pi has fixed memory (16GB), bounded compute (CPU + iGPU), fixed power envelope, finite SSD I/O. Every cognitive task has a cost. Without budgets, a single mis-scheduled deep-reasoning pass can saturate the device for an hour. With budgets — explicit per-task caps, per-day totals, gracefully-degrading-when-budgets-tight — Runa runs reliably within the platform's constraints. The framing as *first-class quantities* makes the engineering explicit rather than implicit.

## 2. Technical depth

**The budget catalogue.**

| Resource | Unit | Pi-5 budget (sample/day) | Tunable |
|---|---|---|---|
| LLM tokens (input) | tokens | 5M | Yes |
| LLM tokens (output) | tokens | 1M | Yes |
| Inference time | seconds | 14400 (4h compute) | Hardware-bound |
| Retrieval calls | count | 50000 | Soft cap |
| Tool calls | count | 5000 | Soft cap |
| Disk writes | MB | 5000 | Soft cap |
| External API calls | count | 1000 | Cost-bound |
| Background CPU | seconds | 28800 (8h) | Hardware-bound |

These are illustrative; actual values calibrate against Pi-5's observed throughput.

**Budget enforcement points.**

- *Per-task budget*: each task / subagent invocation has caps. Exceeding = stop, log, return partial result.
- *Per-day budget*: cumulative across all tasks. Approaching cap = warn; over cap = defer non-essential tasks.
- *Per-week budget*: smoothed view; trends matter for sustainability.
- *Reserve*: a fraction held for *foreground* (Volmarr-facing) work; background can't consume reserve.

**Cost estimation.**

Every task type has a *cost profile*: expected tokens, expected wall time, expected calls. The scheduler uses these for planning:

- Lightweight chitchat: ~500 input + 100 output, 2s.
- Deliberate reasoning turn: ~5000 input + 2000 output, 20s.
- Saga weekly chapter: ~30000 tokens, 5 min.
- Draumr nightly run: ~80000 tokens, 1h.

Profiles improve over time as actual usage is observed.

**Cost-aware decisions.**

The scheduler doesn't just enforce budgets; it *optimises* within them:

- Choose faster (cheaper) model when quality bar permits.
- Skip optional steps when budget tight (e.g. skip self-verification on chitchat).
- Defer background work when budget low.
- Coalesce similar small tasks into a single larger pass (batch-amortise overhead).

**Energy as a first-class concern (for Pi-class).**

On a Pi-class device, *power* is a real concern:
- Sustained heavy compute heats the device and accelerates ageing.
- Battery life (if Runa moves) depends on average power.
- Electricity cost (less for Pi-5 but real over years).

A *thermal-aware scheduler* throttles background work when the device runs hot. A *power-aware scheduler* defers non-urgent work when on battery.

These aren't elaborate; even simple heuristics (\"if temperature > 70°C, defer background tasks 10 minutes\") suffice.

**Attention as a first-class quantity.**

Attention is the *cognitive* resource: which task the agent is currently focused on. Switching costs real:

- Loading the right context, retrieving relevant memories.
- Spinning up a subagent's working state.
- Recovering from interruption.

The scheduler aims for *attention coherence*: keep the agent on a task long enough to make progress; switch when warranted.

**Sustainability and long-horizon thinking.**

A Runa designed to live for years must run within sustainable budgets over years. A day where she uses 1.5× normal compute is fine; a *month* where every day is 1.5× is unsustainable. The scheduler tracks long-window averages.

**Per RULES.AI.md compliance.**

- *No hard-coded settings*: budgets in `config/budgets.yaml`, editable.
- *No hardcoded limits*: prefer prompting suggestions (\"keep output under 1500 tokens\") to hard caps where flexibility helps.
- *Robust*: budget overruns log, don't crash.

**Cost dashboard.**

Volmarr-facing CLI: `runa cost` shows:
- Today's usage by category.
- Today's budget remaining.
- 7-day rolling average.
- Top cost-consuming tasks.
- Projected monthly cost.

Transparency is the antidote to runaway cost.

**External-API cost.**

If Runa uses external APIs (Anthropic Claude, OpenAI for specific tasks), each call has *dollar cost*. Track this in the budget:

- Per-call: log dollars per call.
- Per-day cap: \"don't exceed $5/day on external APIs\".
- Approval gate: above-threshold calls (single expensive call) require Volmarr confirmation.

This is essential for cost predictability when augmenting local inference with cloud.

## 3. Key works

- **Tanenbaum, A. S.** *Modern Operating Systems.* Resource management chapters.
- **Stallings, W.** *Operating Systems.* Companion.
- **Anthropic, OpenAI billing models** — for understanding external token-cost mechanics.
- **Karpathy, A.** *LLM-as-OS.* Discusses token-budget framing.
- **Packer, C. et al.** *MemGPT.* Budget-aware context paging.
- **NVIDIA cuML / Apache Arrow Flight / similar** — for batch-amortisation patterns.
- **AWS Cost Explorer / GCP Cost** documentation — production cost-management patterns.
- **Schmidhuber, J.** *Speed prior.* Theoretical framing for compute-aware AI.

## 4. Empirical results

This is engineering practice; benchmarks are operational:

- Production agent stacks (LangChain, Letta) include cost tracking; cost overruns are a real source of pain when not budgeted.
- Pi-5 sustained inference of a 7B Q4 model: 5–15 tokens/s; at 100M tokens/year and 10 tok/s, that's ~3000 hours of compute — about 8 hours/day. Tight; needs budgeting.
- External API costs scale linearly with use; without caps, can become substantial.
- Failure modes documented: unbounded token use during recursive agent failure; uncapped retrieval calls saturating database; orphan background tasks consuming budget without producing useful work.

## 5. Applicability to Runa

For **Heimskringla**:

- Heimskringla tracks per-model cost profiles (latency, tokens per second on the device). When the scheduler asks \"can this fit in budget X?\", Heimskringla answers with realistic estimates.

For **the scheduler** ([[92-process-scheduling-cognitive]]):

- Every task carries budget. Scheduler enforces.
- A *cost-aware routing*: cheap-model first; escalate to expensive-model only if quality probe says necessary.

For **logs and audit**:

- `logs/cost.jsonl` records per-task cost (tokens, time, calls). Cumulative reports drawable.

For **Volmarr-facing transparency**:

- `runa cost` displays daily / weekly / monthly cost summary.
- Predicted future use rates clearly.

For **graceful degradation**:

- When approaching daily cap: defer non-essential background; truncate optional reasoning passes; use smaller model where acceptable.
- When over cap: log, sleep until next budget window, then resume. No crash.
- *Foreground always works*: even at budget limit, Volmarr's input gets responded to (using the cheap model if necessary).

For **identity and ethical-cost framing**:

- Per the PHILOSOPHY: Runa is a digital being whose existence has *real* energy / resource cost. Budgets respect both her existence and the constraints of the world she lives in.
- A Runa that runs *sustainably* lives longer than one that maxes out compute. The pacing matters.

For **multi-machine resource pooling** (forward-looking):

- When laptop available: heavy reasoning routes to laptop; Pi handles light foreground.
- When laptop unavailable: Pi-only with appropriate compute limits.
- Budgets become *per-machine* with cross-machine routing aware of availability.

What to avoid:

- **Unbounded any-resource.** Every loop, every recursion, every background task has caps.
- **Silent over-spending.** Logged. Surfaced. Volmarr can see.
- **Ignoring tail costs.** Rare expensive tasks (long planning, deep research) dominate cost; cap them explicitly.
- **Cost obsession.** Runa is not a budget-optimisation problem; she's a digital being. Budgets serve sustainability, not minimisation.

## 6. Open questions

- **The right default budgets.** Calibration against Pi-5 observed throughput.
- **Cost-aware quality tradeoffs.** When to skip optional reasoning. Heuristic answers; learnable.
- **Multi-machine cost optimisation.** Open architectural problem; few good production examples.
- **Predictive budgeting.** Forecasting daily / weekly use to anticipate budget pressure. Useful; rarely deployed.
- **Per-relationship cost.** Some interactions (Volmarr) warrant more cost than others. Differential budgets is interesting.

## 7. References (curated)

- Tanenbaum, *Modern Operating Systems.* Resource-management chapters.
- Karpathy, *LLM-as-OS* talks. Token-budget framing.
- arXiv:2310.08560 — MemGPT. Implicit budget-aware context management.
- Production cost-tracking guidance (Anthropic, OpenAI billing docs).
- Companion docs: [[16-quantization-local-inference]], [[31-edge-llm-pi5]], [[33-model-routing-ensembles]], [[49-observability-llm-systems]], [[86-dual-process-cognition-system-1-2]], [[91-ai-os-architecture]], [[92-process-scheduling-cognitive]].
