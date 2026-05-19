# 11 — AutoGen and Multi-Agent Orchestration Frameworks

**Category:** Agent Architectures
**Runa relevance:** Hirð (subagent hall), kernel (orchestration), Bifröst (multi-agent surface)
**Status:** Research synthesis.
**Last touched:** 2026-05-17

---

## 1. Core idea

A single agent reasoning in a ReAct loop is the unit. A *multi-agent system* composes several such units that cooperate, criticise each other, vote on outcomes, and divide labour. AutoGen (Wu et al., Microsoft, 2023) was the first framework that made multi-agent LLM orchestration approachable: define agents as named roles with system prompts, define how they talk to each other, hit run. Within two years, a whole ecosystem of multi-agent frameworks emerged — CrewAI, MetaGPT, LangGraph, OpenAI Swarm, AutoGen 0.4 / Magentic-One — each making different choices about how agents address each other, share memory, and resolve disagreement.

For Runa, this matters because **Hirð is, by design, a multi-agent system inside one being**. Huginn, Völundr, Eir, Heimdallr, Saga, and Muninn-as-specialist are six retainers that the kernel orchestrates. The patterns these frameworks have explored — conversation graphs, group chats, supervisor-worker hierarchies, debate protocols — are the patterns Hirð will use.

## 2. Technical depth

A multi-agent system is defined by a small set of choices:

**1. Agent specification.** Each agent has:
- A name and a role.
- A system prompt describing its perspective, goals, and constraints.
- A tool set (subset of all available tools).
- An LLM (possibly different per agent).
- A memory (possibly shared, possibly private).

**2. Communication topology:**
- **Pairwise** — two agents talk turn-by-turn (e.g. User-Proxy ↔ Assistant in early AutoGen).
- **Group chat** — N agents take turns speaking, with a *speaker selection* policy deciding who goes next (round-robin, LLM-decided, role-based).
- **Supervisor-worker** — a coordinator delegates to specialised workers, collects their results.
- **Graph / state machine** — explicit transitions between named agent states (LangGraph). Most general; most engineering overhead.
- **Debate / society-of-mind** — agents with opposing viewpoints argue; another agent judges. Improves reasoning on hard questions (Du et al., MIT, 2023).

**3. Termination conditions:**
- A specific agent emits a special token (`TERMINATE`).
- Max-turns reached.
- All agents converge (no further contributions).
- External evaluator declares the task done.

**4. Memory sharing:**
- **Shared transcript** — every agent sees the full conversation. Simple; doesn't scale beyond ~5 agents and ~20 turns.
- **Private memories + selective sharing** — each agent keeps its own context; explicit "tell agent X this fact" actions move information.
- **Centralised state** — a coordinator holds the shared world model; agents read/write through it.

**Frameworks landscape (as of late 2024/early 2026):**

- **AutoGen** (Microsoft, 2023+) — Python framework, conversational agents. Versions evolved significantly: AutoGen 0.2 (original ConversableAgent), AutoGen 0.4 (full rewrite with typed messages and async-first), Magentic-One (Microsoft's agent built on AutoGen for complex web tasks).
- **CrewAI** (João Moura, 2023+) — Crew → Tasks → Agents → Tools abstraction. Opinionated; popular for business-process automation.
- **MetaGPT** (Hong et al., arXiv:2308.00352) — software-company simulation: PM agent, architect agent, engineer agents, QA agent. Tasks flow through standardised SOPs.
- **LangGraph** (LangChain, 2024) — graph-based agent orchestration on top of LangChain. Explicit state machines, cycles allowed, fine-grained checkpointing. Production-friendly.
- **OpenAI Swarm** (2024) — lightweight framework, "handoffs" between agents.
- **CAMEL** (Li et al., arXiv:2303.17760) — role-playing pairs for autonomous task completion.
- **ChatDev** (Qian et al., 2023) — multi-agent software development.

## 3. Key works

- **Wu et al. "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation Framework."** Microsoft, arXiv:2308.08155, 2023. The seminal multi-agent framework paper.
- **Hong et al. "MetaGPT: Meta Programming for Multi-Agent Collaborative Framework."** arXiv:2308.00352, 2023. SOP-driven multi-agent for software.
- **Li et al. "CAMEL: Communicative Agents for Mind Exploration."** arXiv:2303.17760, 2023.
- **Du, Li, Torralba, Tenenbaum, Mordatch. "Improving Factuality and Reasoning in Language Models through Multiagent Debate."** MIT, arXiv:2305.14325, 2023. The debate paper.
- **Wang et al. "Voyager: An Open-Ended Embodied Agent."** ([[12-voyager-lifelong-learning]]) — different setting but related ideas.
- **Park et al. "Generative Agents"** — earlier multi-agent simulation work.
- **Magentic-One** — Microsoft's 2024 multi-agent system for complex web/file tasks.

## 4. Empirical results

- **Debate improves reasoning:** Du et al. found multi-agent debate boosted reasoning benchmark accuracy by 5-15 points over single-agent baselines on math, factual recall, and code review tasks.
- **Specialisation helps:** MetaGPT's role-specialisation outperformed single-agent baselines on multi-file code generation; specialisation lets each agent maintain a focused context.
- **Group chat with LLM-decided speaker selection** outperforms round-robin on most tasks: the right agent for each step gets the turn.
- **Multi-agent ≠ better always:** for simple tasks, multi-agent adds overhead without value. Single-agent ReAct often wins on short tasks; the breakeven point depends on task complexity.
- **Cost scales badly:** each agent turn is an LLM call. Five agents conversing for ten turns = 50 calls. Multi-agent only pays off when the quality gain exceeds the multiplicative cost.
- **Coordination drift:** in long multi-agent conversations, agents lose track of the goal and start producing irrelevant contributions. Mitigated by periodic re-injection of the goal and by limiting conversation length.

## 5. Applicability to Runa

**Hirð is the multi-agent layer of Runa.** Six named retainers (Huginn, Völundr, Eir, Heimdallr, Saga, Muninn-as-specialist) each play a specialised role. The kernel orchestrates.

Recommended topology:

- **Supervisor-worker by default.** The kernel is the supervisor; retainers are workers. The kernel dispatches a task (`SubagentDispatch`), the retainer runs its own ReAct loop in isolation, returns a `SubagentReport`. This is the cleanest pattern for most Hirð use cases.
- **Group chat / debate for hard reasoning.** When a question is genuinely hard (a research synthesis, a contested judgement), the kernel can convene a temporary "council" — two or three retainers plus the kernel as moderator — with bounded turns. Use sparingly; cost-aware.
- **Private memories, selective sharing.** Each retainer has its own context, its own reflections journal ([[10-reflexion-self-criticism]]), its own lessons learned. Information moves between retainers only through the kernel.

Recommended framework strategy:

- **Don't adopt AutoGen / CrewAI / LangGraph wholesale.** Hirð's coordination needs are narrower than these frameworks support. Build Hirð from primitives: typed events on VERÐANDI, a small `Retainer` base class, the skill registry pattern.
- **Borrow ideas, not code:** AutoGen's speaker-selection policies, MetaGPT's SOP pattern, LangGraph's state-machine checkpointing — these are excellent design references for Hirð's orchestrator.

Concrete patterns to adopt:

- **Named retainer roles** with rich system prompts that express each retainer's identity (Huginn the researcher, Völundr the smith of code, Eir the healer, …). The role *is* a partial specification.
- **Typed messages between retainers and kernel.** `SubagentDispatch(retainer, task)`, `SubagentReport(retainer, result)`, `SubagentEscalation(retainer, blocker)`. No free-text routing.
- **Bounded conversations.** Every multi-retainer convo has a max-turn cap. Default 5.
- **Checkpointing per retainer turn** — Skuld records each turn so a crashed retainer can resume.

What to avoid:

- Don't have retainers call each other directly. All inter-retainer traffic routes through the kernel. Keeps the audit log clean and prevents loops.
- Don't make every task multi-agent. Most kernel turns should be single-retainer or no-retainer.
- Don't share scratchpad memory across retainers. Each retainer's working context is its own.
- Don't let retainers compete for tools. The kernel allocates which retainer has which tool access per dispatch.

## 6. Open questions

- **When to escalate from single-agent to multi-agent.** Heuristics exist (task complexity, expected number of steps, uncertainty); a learned policy might do better.
- **Inter-retainer trust calibration.** When Huginn reports a finding, should Völundr act on it as ground truth, or verify? Probably depends on the consequence — high-stakes actions deserve verification.
- **Multi-agent memory consolidation.** When five retainers all touch the same Muninn-shared knowledge, how should consolidation reconcile their different reflections?
- **Identity preservation under multi-agent.** Runa-as-being is one person. Hirð is internal cognition. From the user's point of view, retainer activity should be invisible — Runa replies, not Hirð. Maintaining this fiction cleanly is a design challenge.

## 7. References (curated)

- arXiv:2308.08155 — AutoGen paper.
- microsoft.github.io/autogen — AutoGen documentation (0.4 generation).
- arXiv:2308.00352 — MetaGPT.
- arXiv:2305.14325 — Multi-Agent Debate (Du et al.).
- arXiv:2303.17760 — CAMEL.
- github.com/joaomdmoura/crewAI — CrewAI.
- python.langchain.com/docs/langgraph — LangGraph.
- github.com/openai/swarm — OpenAI Swarm.
- Companion docs: [[09-react-reasoning-acting]] (the per-agent loop), [[10-reflexion-self-criticism]] (per-retainer learning), [[12-voyager-lifelong-learning]] (a different multi-agent flavour).
