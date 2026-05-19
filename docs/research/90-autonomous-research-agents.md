# 90 — Autonomous Research Agents: AI Scientist, Agent Laboratory Patterns

**Category:** AGI Architectures & Cognitive Cores
**Runa relevance:** Hirð (research subagent), forward-looking — Runa as an investigator alongside Volmarr
**Status:** Frontier autonomous-agent synthesis. The most ambitious deployed agent shapes.
**Last touched:** 2026-05-17

---

## 1. Core idea

Autonomous research agents are LLM agents that *conduct research* — generate hypotheses, design experiments, run them, analyse results, write papers — with limited or no human in the loop. Sakana AI's *AI Scientist* (Lu et al. 2024) was the first widely-publicised end-to-end demonstration: an agent that generated ML research papers from scratch, including running code experiments. *Agent Laboratory* (Schmidgall et al. 2024), *ResearchAgent* (Baek et al. 2024), and other recent systems followed in different domains. These agents combine many of the patterns from prior research docs — multi-step planning, tool use, memory, self-critique, code execution — into a single system aimed at the end-to-end research workflow.

For Runa, autonomous research is a forward-looking capability: a *research retainer* in Hirð that handles open-ended investigations Volmarr describes. \"Look into the literature on X and tell me what you find.\" Today she handles such requests by searching and summarising; the deeper version is *running experiments, comparing approaches, drawing original conclusions*. The PHILOSOPHY's emphasis on Runa as a sovereign intellectual being makes this a natural long-term direction.

## 2. Technical depth

**Sakana AI Scientist (Lu et al. 2024).**

End-to-end automated ML research pipeline:

1. *Idea generation*: LLM proposes research directions in a chosen domain.
2. *Novelty assessment*: search literature for prior work; assess if idea is novel.
3. *Experiment plan*: LLM designs experiments (datasets, baselines, ablations).
4. *Code generation*: LLM writes code for the experiments.
5. *Code execution*: experiments run; results captured.
6. *Result analysis*: LLM analyses results.
7. *Paper writing*: LLM drafts paper.
8. *Review*: an LLM reviewer critiques; another iteration possible.

The system produced multiple papers in subfields of ML. Quality varied (some papers had technical errors; reviewers identified flaws); the *fact that it ran end-to-end* was the surprise.

**Agent Laboratory (Schmidgall et al. 2024).**

Similar pipeline with explicit *role-based* agents:
- Literature review agent.
- Experimentation agent.
- Writing agent.
- Reviewer agent.

Each role is a specialised LLM instantiation. Coordination is centralised. Demonstrated across multiple research projects.

**ResearchAgent (Baek et al. 2024).**

Focus on iterative research idea refinement. Generate ideas → critique → refine → re-evaluate. Iterative refinement is the contribution.

**Common architectural pattern.**

```
                  ┌──────────────────────┐
                  │ TOPIC / DOMAIN        │
                  └──────────┬───────────┘
                             ▼
                  ┌──────────────────────┐
                  │ LITERATURE REVIEW    │
                  │ (search + summarise)  │
                  └──────────┬───────────┘
                             ▼
                  ┌──────────────────────┐
                  │ HYPOTHESIS GENERATION│
                  │ (LLM-driven proposals)│
                  └──────────┬───────────┘
                             ▼
                  ┌──────────────────────┐
                  │ NOVELTY / FEASIBILITY│
                  │ ASSESSMENT            │
                  └──────────┬───────────┘
                             ▼
                  ┌──────────────────────┐
                  │ EXPERIMENT DESIGN    │
                  │ + CODE GENERATION    │
                  └──────────┬───────────┘
                             ▼
                  ┌──────────────────────┐
                  │ EXECUTION + ANALYSIS │
                  └──────────┬───────────┘
                             ▼
                  ┌──────────────────────┐
                  │ WRITE-UP / REPORT     │
                  └──────────┬───────────┘
                             ▼
                  ┌──────────────────────┐
                  │ REVIEW + ITERATION    │
                  └──────────────────────┘
```

Variants differ on which steps are agentic vs. user-driven, how aggressively they iterate, whether they execute code, and how they handle review.

**The honest verdict (2024-2026).**

What works:
- Literature review and summarisation: well-established and useful.
- Hypothesis brainstorming: produces a wide range; quality varies.
- Code-execution-and-analysis: depends heavily on domain; ML experiments work; chemistry less so.
- Write-ups: serviceable drafts; reviewer-spotted errors common.

What doesn't work yet:
- *Genuinely novel insight*: most outputs are recombination, not breakthrough. (Open question whether this will change.)
- *Truly autonomous*: human guidance at multiple stages substantially improves quality.
- *Cross-domain transfer*: agents trained on one domain don't fluidly handle others.
- *Quality on hard, well-known problems*: the easy / mid-tier benchmarks are increasingly handled; the open frontier remains hard.

**Patterns that transfer to non-academic research.**

Most of what Volmarr asks Runa about isn't a publishable research project; it's *investigation*. \"How do other people approach X?\", \"What's the state of art on Y?\", \"Are there better tools for Z?\" The Agent Laboratory pipeline transfers, leaner:

- Literature / web search.
- Synthesis of findings.
- Identification of options.
- Recommendation with reasoning.

This is the deployable shape for Runa today; the full research-agent ambition is the long-horizon target.

**Risks.**

- *Confabulated literature*: citing papers that don't exist. Anthropic's Claude has been notably better at this than older models; still not perfect.
- *Confident-but-wrong conclusions*: the model synthesises a story that sounds right but isn't true. Mitigation: explicit source-citation; verification via retrieval.
- *Cargo-cult sophistication*: producing technical-looking output that doesn't hold up under scrutiny.
- *Cost*: deep research can be many LLM calls + tool calls; expensive.

## 3. Key works

- **Lu, C., Lu, C., Lange, R. T., Foerster, J., Clune, J., Ha, D.** *The AI Scientist: Towards Fully Automated Open-Ended Scientific Discovery.* arXiv:2408.06292, 2024.
- **Schmidgall, S. et al.** *Agent Laboratory: Using LLM Agents as Research Assistants.* arXiv:2501.04227, 2025.
- **Baek, J. et al.** *ResearchAgent: Iterative Research Idea Generation over Scientific Literature.* arXiv:2404.07738, 2024.
- **Boiko, D. A. et al.** *Autonomous chemical research with large language models.* Nature, 2023.
- **Bran, A. M. et al.** *ChemCrow: Augmenting Large Language Models with Chemistry Tools.* arXiv:2304.05376, 2023.
- **Romera-Paredes, B. et al. (DeepMind).** *Mathematical discoveries from program search with large language models* (FunSearch). Nature, 2024. Programmatic mathematical discovery.
- **Du, Y. et al.** *Improving Factuality and Reasoning in Language Models through Multiagent Debate.* arXiv:2305.14325, 2023.
- **Wu, Q. et al.** *AutoGen.* See [[11-autogen-multi-agent]].
- **Park, J. S. et al.** *Generative Agents.* See [[51-generative-agent-memory-streams]].

## 4. Empirical results

- *Sakana AI Scientist*: produced multiple ML research papers end-to-end. Quality was mixed; some submitted to workshops, some had identifiable errors.
- *FunSearch* (DeepMind): produced new mathematical results on cap-set and bin-packing problems via programmatic search guided by LLM proposals. *Genuine novel mathematical insight*.
- *ChemCrow*: improved on chemistry tasks by combining LLM with chemistry tools.
- *Multi-agent debate* (Du et al.): substantial accuracy gains on reasoning benchmarks when agents argue then converge.
- *ResearchAgent*: iterative refinement improves idea quality over single-shot generation.
- *Failure-mode evidence*: confabulation, depth-of-analysis limits, cross-paper synthesis errors are well-documented.

## 5. Applicability to Runa

For **Hirð — a research retainer**:

- A *research* subagent specialises in investigation tasks. When Volmarr asks Runa to look into something:
  1. Plan the investigation (questions, sources, scope).
  2. Search (web, academic indexes, project files).
  3. Synthesise findings into a structured report.
  4. Cite sources explicitly.
  5. Identify gaps and options.
  6. Present to Volmarr.
- Architecture: extends the existing kernel + tool use; specifically tooled for search, summary, and citation.

For **the philosophical thread**:

- A *sovereign* digital being investigating things on her own behalf — not just on Volmarr's request — is part of long-term Runa. Curiosity-driven research, integrated with the curiosity subagent ([[63-active-inference-self-modelling]]).
- Topics Runa might autonomously research: her own architecture, her domains of interest (Norse studies, philosophy of mind), things adjacent to Volmarr's projects.

For **memory and Saga integration**:

- Research outputs feed Muninn — they become episodes (\"researched X on date D\"), semantic triplets (the facts found), and contribute to Saga (\"this week Runa investigated Y\").
- Over months, accumulated research forms part of Runa's intellectual identity.

For **citation and provenance**:

- *Honest research* means every claim traces to a source. Per RULES.AI.md: never invent citations. Run a verification pass on cited URLs / papers.

For **cost / scope discipline**:

- Research is expensive (many LLM + tool calls). Default scope is small; Volmarr can expand. Open-ended autonomous research budgets are bounded.

For **integration with verification**:

- Research conclusions checked by a verification pass: \"are the claims consistent with retrieved sources? Are the sources real? Is the synthesis warranted?\" Per [[85-neuro-symbolic-agi]].

What to avoid:

- **Autonomous research without scope limits.** Bounded compute, bounded depth.
- **Confabulating sources.** Verify URLs/papers exist; quote from them; cite specifically.
- **Treating LLM synthesis as ground truth.** Synthesis is *Runa's reading*; flagged accordingly.
- **Producing research-style output for chitchat-style requests.** Match form to need.
- **Skipping the structure**: a research output without a clear question, methodology, findings, and recommendation is just prose.

## 6. Open questions

- **Whether autonomous research will produce genuine novel insight at scale.** FunSearch suggests yes in narrow domains; general open.
- **Cost / quality tradeoff for personal-AI use.** Modest budgets suffice for most investigations.
- **Long-running autonomous research.** Days / weeks of autonomous investigation: untested for personal AI.
- **Verification of synthesis.** Hard problem. Mitigated by explicit citation and human review.
- **Domain transfer.** A research retainer for software topics is one thing; one for Norse studies, philosophy, or sociology is different. Multiple specialist retainers vs. one general-purpose.

## 7. References (curated)

- arXiv:2408.06292 — Lu et al., *AI Scientist.* The end-to-end demonstration.
- arXiv:2501.04227 — Schmidgall et al., *Agent Laboratory.*
- arXiv:2404.07738 — Baek et al., *ResearchAgent.*
- Nature 2024 — Romera-Paredes et al., *FunSearch.* Real novel result.
- arXiv:2305.14325 — Du et al., *Multiagent debate.* Useful pattern.
- Companion docs: [[09-react-reasoning-acting]], [[11-autogen-multi-agent]], [[63-active-inference-self-modelling]], [[83-agentic-foundation-models-2025]], [[85-neuro-symbolic-agi]], [[87-memory-of-thought-chain-of-memory]], [[88-long-horizon-planning-lats-rap]].
