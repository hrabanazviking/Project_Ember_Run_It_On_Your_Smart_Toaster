# 09 — ReAct: Reasoning and Acting Interleaved

**Category:** Agent Architectures
**Runa relevance:** kernel (turn shape), Hirð (subagent loops), Smiðja (tool invocation pattern)
**Status:** Research synthesis. This is the *canonical* foundation pattern for modern agent loops.
**Last touched:** 2026-05-17

---

## 1. Core idea

ReAct (Yao et al., Princeton + Google, 2022) is the foundational pattern for agentic LLM use. The insight is simple: interleave **R**easoning steps (the LLM thinks out loud about what to do) with **Act**ing steps (the LLM emits tool calls), and feed the **Obs**ervations from each action back into the next reasoning step. The model sees its own thoughts, its own actions, and the world's responses as a unified trajectory.

This is the pattern almost every subsequent agent architecture — AutoGen, LangChain agents, OpenAI tool-use, Claude's native tool-use, Voyager, SWE-Agent, computer-use agents — extends or specialises. Understanding ReAct is understanding the spine of modern agentic LLM systems.

## 2. Technical depth

A ReAct trace looks like:

```
Question: When did Volmarr last back up Muninn?

Thought 1: I need to find recent Muninn backup events. I'll search Muninn
           for events tagged "memory backup".
Action 1:  muninn.search(query="memory backup", surface=null, k=5)
Observation 1: [
  {date: "2026-05-14", text: "runa memory backup nightly"},
  {date: "2026-05-09", text: "runa memory backup manual"},
  ...
]

Thought 2: The most recent automated backup was 2026-05-14. I should
           confirm the backup succeeded by checking the audit log.
Action 2:  audit.search(query="memory backup", date="2026-05-14")
Observation 2: [{status: "ok", duration_s: 12, size_mb: 84}]

Thought 3: I have what I need to answer.
Action 3:  reply("Muninn was last backed up on 2026-05-14, automated,
                 12 seconds, 84 MB. The backup succeeded.")
```

The format is *prompt engineering*: the system prompt teaches the model the Thought / Action / Observation cycle, the available tools, and the format conventions. The kernel parses each model response for an Action, dispatches the tool, formats the result as an Observation, and re-prompts.

The ReAct paper's framing: pure chain-of-thought reasoning (Thought-only) is good at logic but cannot get fresh information; pure action-taking (Action-only) is good at fetching information but cannot integrate it well; *interleaving* gives the model the ability to plan, fetch, re-plan, refine. The interleaving is the value.

**Variants and extensions:**

- **Tool-augmented ReAct** — the OpenAI / Anthropic native tool-use APIs are a structured form of ReAct where Actions are typed function calls with JSON schemas, and Observations are returned in standardised slots. Easier than parsing free-text actions; loses some flexibility in unusual flows.
- **Plan-and-Execute** — split the work: a *planner* model produces a multi-step plan, an *executor* model runs each step ReAct-style. Useful for long tasks where naive ReAct loses track.
- **Self-Ask** (Press et al., 2022) — predecessor that decomposes questions into sub-questions before searching.
- **ReWOO** (Xu et al., 2023) — Reasoning WithOut Observation: pre-plan all actions in parallel before observing any results. More efficient on tasks where the plan doesn't depend on intermediate observations.
- **Reflexion** ([[10-reflexion-self-criticism]]) — adds an explicit self-critique step after failure.
- **Tree-of-Thoughts** ([[13-tree-of-thoughts-structured-reasoning]]) — branches at Thought steps to explore alternative reasoning paths.

**Critical implementation details:**

- The system prompt must enumerate available tools with their argument shapes and example calls.
- The system prompt must specify the format conventions exactly (often Thought:/Action:/Observation: prefixes). Format breakage is a top failure mode.
- Loop bounds: cap the number of Action turns per question. Without a cap, models can loop indefinitely.
- Action validation: malformed Actions should return an Observation explaining the error, not crash the agent.
- Observation summarisation: long tool outputs (e.g. a 50-row search result) should be summarised before being shoved into the next prompt. Otherwise context fills.

## 3. Key works

- **Yao, Zhao, Yu, Du, Shafran, Narasimhan, Cao. "ReAct: Synergizing Reasoning and Acting in Language Models."** Princeton + Google, arXiv:2210.03629, October 2022. The paper.
- **Press, Zhang, Min, Schmidt, Smith, Lewis. "Measuring and Narrowing the Compositionality Gap in Language Models."** arXiv:2210.03350. Self-Ask, contemporaneous predecessor.
- **Xu, Peng, Wu, Cheng, Lin, Yu, Wang. "ReWOO: Decoupling Reasoning from Observations for Efficient Augmented Language Models."** arXiv:2305.18323, 2023.
- **Wei et al. "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models."** arXiv:2201.11903. The pure-CoT predecessor that ReAct extends.
- **Schick et al. "Toolformer."** arXiv:2302.04761. Contemporary work on training models to use tools.
- The **OpenAI function-calling API** (mid-2023) and the **Anthropic tool-use API** (2024) are productionisations of the ReAct pattern with stricter typing.

## 4. Empirical results

- **HotpotQA / FEVER:** ReAct outperformed both pure-CoT and pure-Action baselines on multi-hop question answering by 4-8 EM points. The gap was larger on harder questions.
- **ALFWorld:** ReAct + an environment of household tasks outperformed pure-RL agents and pure-LLM agents by wide margins (often doubled success rate).
- **WebShop:** ReAct agents purchasing items in a simulated e-commerce site outperformed imitation-learning baselines.
- **Failure modes empirically observed:**
  - **Hallucinated actions:** the model emits a tool call that looks plausible but doesn't exist. Mitigated by listing tools exhaustively in the system prompt and validating syntactically.
  - **Looping:** the model repeats the same action with the same arguments. Mitigated by hard turn caps and by including the model's own previous turns in subsequent prompts.
  - **Premature termination:** the model declares success before checking. Mitigated by training the model on critic-feedback or by adding a verification step.
  - **Drift in long traces:** the model loses track of the original goal after 10-20 turns. Mitigated by re-injecting the goal in the prompt and by checkpointing intermediate results.

## 5. Applicability to Runa

ReAct is *the default* shape of a Runa kernel turn:

- The kernel implements a ReAct loop. A `Heard` event triggers a Thought-Action-Observation cycle that proceeds until the model emits a `Replied` action (or a turn-cap is hit).
- **Actions** are skill invocations from the skill registry — Muninn reads, Smiðja tool calls, Hirð subagent dispatches, model calls through Heimskringla. The skill registry is the canonical tool catalogue the kernel exposes to the model in its system prompt.
- **Observations** come back as skill results, formatted into the model's context for the next prompt.
- **Hirð subagents** themselves run ReAct loops, parented by the kernel. Their final `SubagentReport` is an Observation to the kernel.

Implementation guidance:

- Use the model provider's native tool-use API when available (Claude, GPT-4, Llama 3.x with function-calling) rather than parsing free-text Actions. Stricter typing, fewer format-breakage failures.
- Cap kernel turns at a config-pinned limit (default: 10 Actions per `Heard`). Exceeding emits a `Stopping` and a deferred follow-up.
- Validate every Action against the skill registry's schema before dispatch. Invalid Actions get an Observation explaining the error rather than executing.
- Summarise long Observations before re-prompting. Muninn search results: top-5 with one-line previews, not all 12 full episodes.
- Log every Thought-Action-Observation triplet to the audit log with the correlation_id of the originating `Heard`. This is the basis for reproducible debugging.

What to avoid:

- Don't let the model invent tools. Strict schema validation.
- Don't expose every internal capability as a tool. Curated tool surface — start with ~10-20 well-chosen tools, expand as needed.
- Don't include the entire conversation history in every Action turn. Use Muninn's working-set scratchpad (the MemGPT pattern, [[01-memgpt-os-memory-hierarchies]]) to keep the prompt focused.
- Don't trust the model's self-declared completion. The kernel decides when a turn is done, by inspecting the emitted Action (Reply vs anything else).

## 6. Open questions

- **When to switch from ReAct to Plan-and-Execute.** For tasks with >5-7 steps, planning ahead is often better. The boundary is empirical and task-specific.
- **Parallel actions.** Modern models can emit multiple tool calls in one Action turn (parallel function calling). ReAct's original linear trace is a special case. Worth using when actions are independent.
- **Failure recovery without Reflexion.** Reflexion adds verbal self-critique on failure ([[10-reflexion-self-criticism]]). Simpler recovery — retry with different arguments, ask for clarification — is often enough.
- **ReAct in multi-agent settings.** When Hirð has multiple retainers all ReAct'ing, do they share scratchpad? Compete for tools? AutoGen ([[11-autogen-multi-agent]]) explores some of this.

## 7. References (curated)

- arXiv:2210.03629 — ReAct paper (Yao et al.).
- arXiv:2201.11903 — Chain-of-Thought (Wei et al.).
- arXiv:2210.03350 — Self-Ask (Press et al.).
- arXiv:2305.18323 — ReWOO.
- arXiv:2302.04761 — Toolformer.
- platform.openai.com/docs/guides/function-calling — OpenAI function-calling.
- docs.anthropic.com/en/docs/build-with-claude/tool-use — Claude tool-use.
- Companion docs: [[10-reflexion-self-criticism]], [[11-autogen-multi-agent]], [[13-tree-of-thoughts-structured-reasoning]].
