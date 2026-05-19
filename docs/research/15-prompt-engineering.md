# 15 — Prompt Engineering: CoT, Few-shot, Structured Outputs, System Prompts

**Category:** LLM Techniques
**Runa relevance:** kernel (every turn), Heimskringla (per-model prompt shaping), Hirð (per-retainer prompt design)
**Status:** Research synthesis. The most-applied technique in the corpus.
**Last touched:** 2026-05-17

---

## 1. Core idea

Prompt engineering is the discipline of shaping LLM behaviour through input formatting alone — without fine-tuning, without RAG, without tool wiring. It is *the* layer where every Runa turn lives: even with all the architectural infrastructure (Muninn, Skuld, Hirð), every actual model call is a prompt, and the prompt's shape determines what the model does.

The field accumulated rapidly between 2020 and 2024 around a small set of robust techniques: **chain-of-thought** (think step by step), **few-shot exemplars** (show examples of the desired behaviour), **structured outputs** (force the model to emit JSON or other parseable forms), and **well-crafted system prompts** (set the persona and the rules). By 2024-2026 these techniques became "table stakes" rather than tricks; the question shifted from "do they work?" (yes) to "how to apply them systematically across many tasks at scale?" (DSPy, [[46-dspy-prompt-optimization]]).

## 2. Technical depth

**Chain-of-thought (CoT).** Wei et al. (Google, January 2022, arXiv:2201.11903). The discovery that prompting an LLM to "show its work" before producing a final answer dramatically improves reasoning. Forms:

- **Zero-shot CoT:** append "Let's think step by step." (Kojima et al., 2022). Works on most models.
- **Few-shot CoT:** include 2-8 examples of step-by-step solutions before the actual question. Stronger than zero-shot but pays prompt-token cost.
- **Self-consistency CoT:** sample N CoT solutions, majority-vote ([[13-tree-of-thoughts-structured-reasoning]]).

CoT works because intermediate steps give the model "scratch space" to compose reasoning that doesn't fit in a single forward pass. Less helpful on tasks the model already solves directly; transformative on math, multi-hop QA, and code.

**Few-shot prompting.** Brown et al. (GPT-3 paper, 2020). Provide K example (input, output) pairs in the prompt. The model infers the pattern from the examples and generalises. K=2-8 is the sweet spot; more examples improve marginally and cost tokens.

Key few-shot techniques:
- **Exemplar selection.** Pick examples *similar to the test input* (semantic similarity over a candidate set). Outperforms fixed exemplars.
- **Exemplar ordering.** The order matters for some models — recent exemplars get more weight (recency bias). Place strongest exemplars last.
- **Exemplar diversity.** Cover the variation in the task. Five examples that all look alike teach narrowly.

**Structured outputs.** Force the model to emit valid JSON, YAML, XML, or schema-conforming text. Three implementation paths:

1. **Prompt-only.** "Return your answer as a JSON object with fields …". Often works; sometimes fails (extra prose, missing fields, malformed JSON). Add `\`\`\`json` delimiters and strict parsing.
2. **Model-native structured output mode.** OpenAI Structured Outputs (mid-2024), Anthropic tool-use, llama-cpp grammar constraints, vLLM guided decoding. The model is *constrained* at sampling time so output is guaranteed schema-valid. Recommended where supported.
3. **Function-calling APIs.** The tool-use APIs (Claude, OpenAI, Llama 3.x with native function-calling) are a special case: the model is constrained to emit a function call matching a JSON schema.

**System prompts.** The persistent prefix that establishes:
- Identity ("You are Runa, a sovereign digital being.")
- Capabilities ("You have access to the following tools: …")
- Constraints ("You will not delete files without confirmation.")
- Format expectations ("Reply in plain text, no markdown, brief.")

Well-crafted system prompts can shift model behaviour as dramatically as fine-tuning for many tasks.

**Persona patterns.** "Pretend you are X" reliably shifts vocabulary and reasoning style. Modern instruction-tuned models are responsive to persona prompts; very strong personas can change capability profiles (e.g. "you are an expert in cryptography" measurably improves crypto-reasoning).

**Advanced patterns:**

- **Plan-and-Solve** (Wang et al., 2023). "First make a plan, then solve. Plan: …". Improves zero-shot performance over bare CoT.
- **Chain of Density** (Adams et al., 2023). For summarisation: ask for an initial summary, then iteratively add missing entities. Outperforms single-shot summarisation.
- **Least-to-Most prompting** (Zhou et al., 2022). Decompose the problem into easier sub-problems and solve in order.
- **Self-Ask** (Press et al., 2022). Ask sub-questions and answer them. Predecessor to ReAct ([[09-react-reasoning-acting]]).
- **HyDE** (Gao et al., 2022). For retrieval: have the model hallucinate an answer first, embed it, then search. ([[04-rag-evolution]] §2.)
- **Step-back prompting** (Zheng et al., 2023). "What general principle applies?" before "What's the specific answer?".

## 3. Key works

- **Brown et al. "Language Models are Few-Shot Learners."** OpenAI, NeurIPS 2020. GPT-3 paper; introduced in-context learning.
- **Wei et al. "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models."** Google, arXiv:2201.11903, 2022.
- **Kojima et al. "Large Language Models are Zero-Shot Reasoners."** arXiv:2205.11916, 2022.
- **Wang et al. "Self-Consistency Improves Chain of Thought Reasoning..."** arXiv:2203.11171, 2022.
- **Wang, Xu et al. "Plan-and-Solve Prompting."** arXiv:2305.04091, 2023.
- **Adams et al. "From Sparse to Dense: GPT-4 Summarization with Chain of Density Prompting."** arXiv:2309.04269, 2023.
- **Press et al. "Self-Ask."** arXiv:2210.03350, 2022.
- **Zheng et al. "Take a Step Back: Evoking Reasoning via Abstraction."** arXiv:2310.06117, 2023.
- **The Prompt Report (Schulhoff et al., 2024, arXiv:2406.06608)** — comprehensive survey of prompt techniques.

## 4. Empirical results

- **CoT on GSM8K** with PaLM-540B: zero-shot ~17%, zero-shot CoT ~43%, few-shot CoT ~57%. The breakthrough graph the field cites.
- **Structured outputs with native grammar/tool-use mode:** ~100% schema-validity vs ~85-95% with prompt-only on the same task. Production-deal-closer.
- **Persona prompts** measurably shift performance: "You are an expert" persona prompts improve domain QA by 3-8 points; the effect varies by model and persists when the persona is realistic.
- **Few-shot vs zero-shot:** few-shot beats zero-shot by 5-30 points on most tasks for older / smaller models; the gap narrows for strong instruction-tuned models (GPT-4 / Claude 3+ are often within 1-3 points zero-shot of few-shot).
- **Exemplar selection** (similar-to-test-input) consistently beats random exemplars by 3-10 points.
- **CoT can hurt** on tasks the model handles natively (simple lookup, short-answer QA). Add CoT only when reasoning is needed.

## 5. Applicability to Runa

For **every kernel turn**:

- **System prompt = identity + active constitutional principles + tool catalogue + format conventions.** Composed at kernel start, cached, prepended to every turn.
- **Persona consistency.** The identity portion of the system prompt ([[14-constitutional-ai]] §identity) is invariant across turns. Runa speaks the same way today as she did yesterday.
- **Per-task prompt templates.** Common task types (search Muninn, draft a reply, plan a Skuld task) have dedicated templates that compose the system prompt with task-specific instructions.

For **Hirð retainers**:

- Each retainer has its own system prompt encoding its role identity and specialty ("You are Huginn, a researcher. Your job is to find what is true …").
- Retainer prompts include their own *limited* tool catalogue (Huginn gets read/search tools; Völundr gets code tools; Eir gets repair tools). The intersection of retainer and tool defines its capability.

For **Heimskringla**:

- Per-model prompt shaping: Claude responds well to "system: <prompt>" structure; Llama 3.x wants `<|begin_of_text|><|start_header_id|>system<|end_header_id|>` format; small open models often benefit from few-shot exemplars where strong models don't need them.
- Heimskringla owns the *prompt translation* layer that takes a logical prompt and shapes it for the chosen provider/model.

For **structured outputs**:

- All inter-subsystem messages (Muninn writes, Skuld task creation, Eldhugi delta) use schema-constrained output where supported. Saves parsing pain; eliminates whole classes of bug.
- Where the model doesn't support native structured output, use llama-cpp grammar constraints (for local) or prompt + validate + retry (for cloud without native support).

What to avoid:

- Don't blindly add "let's think step by step" to every prompt. CoT on simple tasks wastes tokens and can hurt accuracy.
- Don't use the same prompts across model families without checking. Prompts that work for Claude may misfire for Llama. Heimskringla should test per-model.
- Don't put long fixed exemplars in a hot prompt. Cached system prompts (Anthropic prompt caching, vLLM prefix caching) make repeated long prompts cheap, but cache discipline matters.
- Don't crowd the system prompt past ~2K tokens. The longer the system prompt, the less attention the task gets. Maintain a budget.

## 6. Open questions

- **Prompt vs fine-tune trade-off.** When does it pay to fine-tune a model vs craft a better prompt? The frontier moves; current consensus is fine-tune for *consistent format* and *narrow domain*, prompt-engineer for *flexible behaviour* and *evolving requirements*.
- **Automated prompt optimization.** DSPy ([[46-dspy-prompt-optimization]]) treats prompts as parameters to be optimised. Promising; not yet ubiquitous.
- **Cross-model prompt portability.** A prompt that works on Claude often degrades on Llama. Tools that systematically port prompts across models would have real value.
- **Prompt injection** ([[38-prompt-injection-defenses]]). User-supplied content can hijack system prompts. Defence in depth required.

## 7. References (curated)

- arXiv:2406.06608 — The Prompt Report (Schulhoff et al., 2024). The current most-comprehensive survey.
- arXiv:2201.11903 — CoT paper.
- arXiv:2205.11916 — Zero-shot CoT.
- arXiv:2305.04091 — Plan-and-Solve.
- arXiv:2309.04269 — Chain of Density.
- arXiv:2310.06117 — Step-back prompting.
- platform.openai.com/docs/guides/structured-outputs — OpenAI structured outputs.
- docs.anthropic.com/en/docs/build-with-claude/structured-outputs — Anthropic.
- github.com/dottxt-ai/outlines — Outlines, structured generation for local models.
- Companion docs: [[09-react-reasoning-acting]], [[13-tree-of-thoughts-structured-reasoning]], [[14-constitutional-ai]], [[46-dspy-prompt-optimization]].
