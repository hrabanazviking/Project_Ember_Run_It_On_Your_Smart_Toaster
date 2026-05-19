# 46 — Automated Prompt Optimization: DSPy, OPRO

**Category:** Self-Improvement & Continual Learning
**Runa relevance:** Heimskringla prompt-translation layer, Hirð retainer prompt design, evals
**Status:** Research synthesis.
**Last touched:** 2026-05-17

---

## 1. Core idea

Hand-engineered prompts are how every LLM application starts. Hand-engineered prompts are also, in practice, the source of most quality drift, regression, and "this worked yesterday" pain. The realisation around 2022-2023 was that prompts can be treated as **parameters to be optimised** rather than artefacts to be hand-edited — given a training set of (input, ideal_output) examples and a quality metric, you can search the space of prompts for the one that maximises the metric.

**DSPy** (Khattab et al., Stanford, 2022+) reframes the whole programming model: you write programs in terms of *signatures* (typed input/output specifications) and *modules* (LLM-using components), and a *compiler* automatically generates and optimises prompts to make the modules satisfy the signatures. **OPRO** (Yang et al., DeepMind, 2023) treats the LLM itself as the optimiser: it iteratively proposes new prompts based on observing which past prompts scored well. **APE** (Zhou et al., 2022) was an earlier related technique.

For Runa, the relevance is forward-looking: as the kernel and retainers accumulate many prompts (one per skill, per task type, per retainer specialty), maintaining them by hand becomes a quality risk. The automated-optimisation paradigm offers a way to keep prompts continuously calibrated against real evaluation data.

## 2. Technical depth

**DSPy's programming model:**

```python
# Signature: declarative spec of input/output
class SummariseEpisode(dspy.Signature):
    """Summarise a Muninn episode in 2 sentences."""
    episode_text: str = dspy.InputField()
    summary: str = dspy.OutputField(desc="Concise 2-sentence summary")

# Module: an LLM-using component implementing the signature
class EpisodeSummariser(dspy.Module):
    def __init__(self):
        self.summarise = dspy.ChainOfThought(SummariseEpisode)
    
    def forward(self, episode_text):
        return self.summarise(episode_text=episode_text)

# Compile: optimise the prompt with training data
trainset = [(episode_a, summary_a), (episode_b, summary_b), ...]
metric = rouge_l_score   # or custom: includes_key_facts, length_ok, etc.
optimised = MIPROv2(metric=metric).compile(EpisodeSummariser(), trainset=trainset)
```

The DSPy compiler:
- Analyses the module structure.
- Generates candidate prompts (with chain-of-thought formats, few-shot exemplars, instruction phrasings).
- Evaluates candidates against the training set.
- Picks the best; can also pick examples to include as few-shot demonstrations.

Optimisers shipped with DSPy:
- **BootstrapFewShot** — generates few-shot demonstrations from the trainset.
- **MIPROv2** (Multi-prompt Instruction PRoposal Optimizer v2) — coordinated optimisation of instructions and demonstrations.
- **BootstrapFinetune** — generates training data for fine-tuning smaller models.

**OPRO (Optimization by PROmpting)** (Yang et al., DeepMind, arXiv:2309.03409, 2023):

The optimiser is *also an LLM*. Given a problem (e.g. "find prompt that maximises math accuracy"), feed the LLM the history of past prompts and their scores; ask it to propose a new, better prompt. Iterate.

```
Iter 1: random prompt "let's solve this" → score 0.6
Iter 2: prompt "let's think carefully" → score 0.62
Iter 3: optimiser proposes "Take a deep breath and work step by step" → 0.71  
Iter N: converges
```

(The "take a deep breath" finding from OPRO was widely-shared as a kind of accidentally-evocative example.)

**APE (Automatic Prompt Engineer)** (Zhou et al., 2022). Predecessor to OPRO; LLM proposes, scores, refines.

**TextGrad** (Yuksekgonul et al., 2024). Gradient-like optimisation through natural-language feedback. Generalises further.

**The compile-once / run-many pattern:**

Optimised prompts are computed offline against a development set, then deployed. Re-compile when:
- New data arrives that the dev set didn't cover.
- The model changes (Heimskringla swaps providers / quants).
- The metric definition changes.

## 3. Key works

- **Khattab et al. "DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines."** Stanford, arXiv:2310.03714, 2023.
- **Yang et al. "Large Language Models as Optimizers."** Google DeepMind, arXiv:2309.03409, 2023. OPRO.
- **Zhou et al. "Large Language Models Are Human-Level Prompt Engineers."** arXiv:2211.01910, 2022. APE.
- **Yuksekgonul, Bianchi, Yang, Banerjee, Cao, Tahmasebi, Maerten, Polo, Buch, Heimann, Anandkumar, Liang, Zou. "TextGrad: Automatic 'Differentiation' via Text."** arXiv:2406.07496, 2024.
- **Schulhoff et al.** "The Prompt Report." arXiv:2406.06608, 2024. Comprehensive survey including automation.
- **DSPy documentation** — dspy.ai.

## 4. Empirical results

- DSPy-compiled pipelines consistently outperform hand-prompted baselines on standardised tasks (HotpotQA, math benchmarks, summarisation). Often by 5-15 absolute points.
- DSPy's compile process can reduce prompt token count substantially while improving quality — because the compiler can find a more efficient instruction that the human prompt engineer wouldn't think of.
- OPRO produced the "take a deep breath" finding — an example of LLM-as-optimiser discovering counterintuitive prompts that beat human-engineered ones on certain benchmarks. The result is real but task-specific; the technique doesn't always find better prompts.
- TextGrad scales the optimisation idea but adds complexity.
- **Caveats:**
  - Quality depends critically on the metric. A bad metric optimised perfectly is worse than a good metric optimised mediocrely.
  - Optimised prompts often *don't transfer* across models. Re-compile when changing providers.
  - The development-set size matters; too small and the optimiser overfits.

## 5. Applicability to Runa

For **v0**:

- Hand-write all prompts. Document them clearly. The discipline of writing prompts manually first teaches what the kernel actually needs.
- Track each prompt's performance via the audit log (see [[49-observability-llm-systems]]). Notice what works and what doesn't.

For **v1+ — once Runa has substantial usage data**:

For **Heimskringla per-model prompt translation**:

- Heimskringla has a "logical prompt" abstraction; the per-model adapter translates to the model-specific shape ([[15-prompt-engineering]]). The translations are good candidates for DSPy-style compilation: given a (logical_prompt, model, ideal_response) tuple, compile a translation that maximises quality.

For **Hirð retainer prompts**:

- Each retainer has its own system prompt. After enough data accrues (hundreds of (retainer_task, retainer_response, Volmarr_satisfaction) tuples), retainer prompts become DSPy-compilable.

For **Saga's prose generation**:

- Saga generates narrative chapters from event logs. The "ideal" output is what Volmarr would write if he were Runa's saga-poet. Hard metric to define; possible.

For **eval suites**:

- The dev set is the bottleneck. Building it means: collect prompt-result pairs over time, label which were good; over months accrue a labelled set DSPy can compile against.
- Eir might run scheduled re-compilation when the dev set grows past a threshold.

What to avoid:

- Don't try to compile prompts before you have meaningful data. Compilation is a tool for *improving* working systems, not for *bootstrapping* them.
- Don't share compiled prompts across providers without re-compilation. They're often model-specific.
- Don't trust LLM-as-judge metrics blindly. Validate that the judge agrees with Volmarr on representative samples before using it as the optimisation target.
- Don't compile against tiny dev sets (<50 examples). Overfitting is severe.

## 6. Open questions

- **Continual prompt optimisation.** Re-compile periodically? On data threshold? On performance regression? No clear rule.
- **Multi-objective prompt optimisation.** Cost, latency, quality, style — finding Pareto-optimal prompts requires multi-objective optimisers. Active work.
- **Prompt composition.** If skill A's prompt is optimised and skill B's prompt is optimised, are they jointly optimal when composed? Often no. Compositional optimisation is hard.
- **Optimisation under safety constraints.** A prompt that maximises some quality metric may also produce policy violations. The optimiser needs to respect constraints. Active area.

## 7. References (curated)

- dspy.ai — DSPy site and docs.
- arXiv:2310.03714 — DSPy paper.
- arXiv:2309.03409 — OPRO.
- arXiv:2211.01910 — APE.
- arXiv:2406.07496 — TextGrad.
- arXiv:2406.06608 — The Prompt Report.
- github.com/stanfordnlp/dspy — DSPy source.
- Companion docs: [[15-prompt-engineering]] (the hand-written predecessor), [[49-observability-llm-systems]] (the eval infra DSPy needs).
