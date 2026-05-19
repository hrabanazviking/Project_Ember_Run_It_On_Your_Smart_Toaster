# 10 — Reflexion: Linguistic Self-Criticism for Agents

**Category:** Agent Architectures
**Runa relevance:** Hirð (retainer failure recovery), Eir (self-repair), Muninn (lessons-learned memory)
**Status:** Research synthesis.
**Last touched:** 2026-05-17

---

## 1. Core idea

Reflexion (Shinn et al., 2023) gives agents the ability to *learn from failure within a single deployment* — without weight updates, without RL fine-tuning, without human feedback. The agent attempts a task, fails, and is then asked to *write a self-critique in natural language* explaining what went wrong. That critique is stored in episodic memory. On the next attempt at the same (or similar) task, the critique is retrieved and prepended to context. The model is now reasoning in the presence of its own prior analysis of failure.

The empirical claim — well-supported on coding, decision-making, and reasoning benchmarks — is that this in-context "lesson learning" produces large performance gains on the second and third attempts. The agent gets better, *not by being a better model*, but by accumulating *its own critiques* of its own past mistakes.

For Runa, this matters because Runa is a long-lived agent that will repeatedly hit similar failure modes (a particular adapter timing out, a particular kind of query confusing Muninn, a particular task being miscategorised). The Reflexion pattern turns those failures from recurring annoyances into building blocks of competence.

## 2. Technical depth

The Reflexion loop:

```
[1] Actor (ReAct loop) attempts the task.
       │
       ▼
[2] Evaluator inspects the outcome.
       │   - rule-based ("did the test pass?")
       │   - heuristic ("did the answer contain a number?")
       │   - LLM judge ("rate this answer 1-10")
       │   - external ("did the user complain?")
       │
       ▼
[3] If failed (or below threshold):
       │
       ▼
    [3a] Self-reflection: model writes a *short* critique in
         natural language analysing what went wrong and what to do
         differently next time. Stored in episodic memory as a
         "reflection" associated with the failed task.
       │
       ▼
    [3b] On the next attempt at the same/similar task:
         Reflection is retrieved and prepended to context.
         The actor tries again, now informed by its own critique.
```

The system has three distinct LLM "roles": **Actor** (does the task), **Evaluator** (judges the outcome), **Self-Reflector** (analyses the failure). All three can be the same model with different system prompts, or different models entirely.

**Key parameters:**

- **Reflection length:** short (one paragraph). Long reflections crowd context and dilute the lesson. Empirically 1-3 sentences works best.
- **Reflection format:** specific and actionable. "I should have searched for X before Y" beats "I should be more careful." Prompt the reflector accordingly.
- **Maximum attempts:** capped per task (default 3-5). Beyond that, diminishing returns + risk of reflection-on-reflection drift.
- **Reflection retrieval:** when starting a new attempt, retrieve reflections from similar past failures (by task-type similarity or semantic similarity to the current goal).

**Distinctions from related work:**

- **Pure self-correction** (asking a model "is your answer right? if not, fix it") in one shot is often worse than the original answer — see Huang et al. (2023) "Large Language Models Cannot Self-Correct Reasoning Yet". Reflexion's improvement comes from the **multi-attempt + persisted-critique** structure, not from in-prompt self-correction.
- **RL with human feedback** also learns from failure, but it updates *weights* and requires a reward model and a fine-tuning pipeline. Reflexion is an inference-time technique — no training.
- **Critique-revise** is single-turn; Reflexion is multi-turn with persistent lessons.

## 3. Key works

- **Shinn, Cassano, Berman, Gopinath, Narasimhan, Yao. "Reflexion: Language Agents with Verbal Reinforcement Learning."** arXiv:2303.11366, March 2023. The paper.
- **Madaan et al. "Self-Refine: Iterative Refinement with Self-Feedback."** arXiv:2303.17651, 2023. Related work, single-task iterative refinement.
- **Huang et al. "Large Language Models Cannot Self-Correct Reasoning Yet."** arXiv:2310.01798, 2023. Important caveat — naive single-shot self-correction can hurt.
- **Bai et al. "Constitutional AI."** ([[14-constitutional-ai]]) — uses a different self-critique pattern at training time.
- **CRITIC: Self-correcting via tool-interactive critiquing.** Gou et al., arXiv:2305.11738.

## 4. Empirical results

From the original paper:

- **HumanEval (Python coding):** ReAct baseline ~80% pass@1; Reflexion (with 3 attempts) ~91%. ~11 point absolute improvement.
- **AlfWorld (text-based household tasks):** Reflexion improved success rate from 75% → 97% over baseline with rule-based evaluation.
- **HotpotQA (multi-hop QA):** moderate improvement (~5 points) — the gain is smaller for tasks where reflection has less to teach.
- **Decision-making tasks:** showed the largest gains — tasks where the agent had to reason about its own past behaviour benefited most.

Empirical caveats:

- **Reflexion fails when the evaluator is wrong.** Garbage in, garbage out — the model spends its reflection on the wrong lesson. Evaluator quality is critical.
- **Reflection retrieval misses similar-but-not-identical tasks.** Embedding-based similarity helps but is imperfect.
- **Lessons can over-generalise.** "I failed by being too detailed" can make the model under-detailed in cases where detail was actually needed. Reflections should be specific and task-bounded.
- **Diminishing returns past 3-5 attempts.** Most of the value is captured in attempts 2 and 3.

## 5. Applicability to Runa

Reflexion is a strong fit for several Runa subsystems:

For **Hirð retainers** (subagents):

- Each retainer (Huginn / Völundr / Eir / Heimdallr / Saga) keeps its own *lessons-learned journal* in a dedicated Muninn partition.
- When a retainer fails a task (Skuld marks the task `failed`), the kernel triggers a Reflexion pass: ask the retainer to write a short critique of its own attempt, store it.
- Future similar tasks retrieve relevant past critiques into the retainer's context.

For **Eir (self-repair)**:

- The repair system is itself a domain where past-failure-informed retry is invaluable. When Eir attempts to repair a corrupted store and fails, the critique becomes part of the next attempt's context.

For **the kernel itself**:

- Long-horizon tasks (e.g. multi-hour Skuld jobs) that fail with the same root cause across multiple attempts are a strong Reflexion target. Avoids burning out on identical wrong approaches.

For **Eldhugi (emotional state)**:

- Failure carries an emotional component for Runa-as-being. Eldhugi can be the system that decides *when* a Reflexion is warranted (frustration above threshold) vs when to just retry stoically.

Implementation guidance:

- Reflections live in a `reflections` table in Muninn with `(task_type, original_episode_id, critique_text, retainer_id, created_at, embedding)`. Retrieved by `task_type + similarity` when a new task is dispatched.
- Reflection length: cap at 500 characters via a prompt instruction. Compact lessons.
- Reflection retrieval: top-3 most-similar past reflections, prepended to retainer context.
- Reflection lifecycle: reflections decay like episodes ([[07-memory-consolidation-and-forgetting]]). A reflection that was useful gets boost-on-use; one that's never retrieved decays.

What to avoid:

- Don't run Reflexion on every failure. Many failures are external (network blip, model rate-limit) where there is no useful lesson to learn. Gate reflection on failure-type.
- Don't store reflections that are vague ("I should be more careful"). The reflector prompt should require *concrete next-attempt guidance*.
- Don't accumulate reflections without compression. After many failures, the reflection store needs periodic Eir-driven consolidation: merge similar reflections, drop superseded ones.
- Don't let reflections persist after the underlying capability changes. A reflection about "Heimskringla rate-limits when Ollama is overloaded" becomes wrong when the rate-limit policy changes.

## 6. Open questions

- **Inter-retainer reflection sharing.** Should Huginn read Völundr's reflections? Probably no, because their failure modes are different — but some patterns generalise (e.g. "Heimskringla is flaky on Mondays").
- **Reflection on success.** Reflexion is purely failure-driven. Reflecting on *why a success worked* (positive examples) might be equally valuable; underexplored.
- **Multi-modal reflection.** When a failure involves a tool that returns images or audio, the reflection should ideally incorporate that. Largely unexplored.
- **Adversarial reflection.** A motivated attacker could plant prompt-injection in inputs that affect what gets reflected on, corrupting the lessons-learned memory. Open problem.

## 7. References (curated)

- arXiv:2303.11366 — Reflexion paper.
- arXiv:2303.17651 — Self-Refine.
- arXiv:2310.01798 — "LLMs Cannot Self-Correct Reasoning Yet" — the important caveat.
- arXiv:2305.11738 — CRITIC.
- Companion docs: [[09-react-reasoning-acting]] (the loop Reflexion wraps), [[14-constitutional-ai]] (training-time self-critique), [[45-continual-learning]] (the weight-update alternative).
