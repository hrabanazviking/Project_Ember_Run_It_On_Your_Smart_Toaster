# AI205: Agent Architecture Design
## Bachelor of Science in AI Agent Automation — University of Yggdrasil, 2040

**Credits:** 4
**Prerequisites:** AI105 (Introduction to Machine Learning), AI201 (Deep Learning Foundations)
**Description:** An agent is a system that perceives, reasons, and acts. Its architecture — the structural arrangement of its cognitive components and the flow of information among them — determines everything it can do and everything it cannot. This course surveys the major architectural paradigms for AI agents as they stand in 2040: from the venerable ReAct loop to emergent cognitive architectures that integrate tool use, planning, reflection, memory, and multi-agent coordination. Students will design, implement, and critique agent architectures, learning to reason about the trade-offs that each design choice imposes. By the end of the course, students will be able to specify a complete agent architecture for a novel domain, defend their design decisions with reference to empirical literature, and implement a working prototype.

> *"Architecture is the learned game, correct and magnificent, of forms assembled in the light."* — Le Corbusier. Substitute "cognition" for "forms" and "reason" for "light," and you have the credo of this course.

---

## Lectures

### ᚠ Lecture 1: What Is an Agent? — Perception, Reason, Action, and the Architecture That Binds Them

**Course:** AI205 — Agent Architecture Design
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

The word "agent" derives from the Latin *agere* — to drive, to do, to act. An agent is, at its most fundamental, a thing that *does*. But the doing is not the whole of it. An AI agent, as the field has converged upon by 2040, is a system that perceives its environment through sensors, reasons about its goals and the state of the world, selects actions based on that reasoning, and executes those actions through actuators — all while maintaining some model, however implicit, of the world and of itself. This four-part cycle — perceive, reason, select, act — is the beating heart of every agent architecture ever built, from the simplest thermostat to the most sophisticated autonomous research scientist.

The architecture of an agent is the structural arrangement of its components and the protocols by which information flows among them. It is the skeleton upon which the agent's "muscles" (tools, models, memory stores, APIs) are hung, and the blueprint that determines which cognitive capabilities the agent can express. A thermostat has an architecture: a sensor (thermometer), a comparator (setpoint vs. reading), and an actuator (heater relay). Its architecture is trivial but perfectly functional within its narrow domain. The question that occupies this course is: what architectures scale from the thermostat to the autonomous software engineer, the personal companion, the scientific discoverer — and beyond?

Russell and Norvig, in their canonical *Artificial Intelligence: A Modern Approach* (4th ed., 2040), classify agents along two dimensions: the complexity of their internal state and the sophistication of their action-selection mechanism. A **simple reflex agent** acts on the current percept alone — no memory, no model, no future. A **model-based reflex agent** maintains an internal representation of the world, enabling it to handle partial observability. A **goal-based agent** evaluates actions by their contribution to a specified goal. A **utility-based agent** assigns numerical values to states, enabling it to handle competing goals and uncertainty. A **learning agent** modifies any or all of the above through experience. This taxonomy, developed in the 1990s, remains foundational, but it has been extended by 2040 to account for the qualitatively new capabilities that large language models provide: agents that reason in natural language, that learn from unstructured text, that compose tools and sub-agents, and that maintain persistent identities across sessions.

The architectural challenge of the 2040s is integration. An agent that can only reason but not act is a philosopher, not an agent. An agent that can act but not reflect on its actions is a reflex machine, not an agent. An agent that can reflect but cannot remember is amnesiac, condemned to repeat its mistakes. Architecture is the art of assembling these capacities — perception, reasoning, action, reflection, memory, learning — into a coherent whole that is greater than the sum of its parts. The Norse conception of the self offers a poetic analogue: a person is not a single soul but a composite of *hugr* (thought), *munr* (desire/will), *hamingja* (luck/inherent power), *fylgja* (fetch/spirit), and *önd* (breath/life). Each is necessary; none is sufficient alone. So too with the agent: its architecture must weave together faculties that are individually limited but collectively formidable.

The stakes of good architecture are existential. Poorly architected agents are brittle — they work in the lab but shatter in the wild. They hallucinate, loop, forget, contradict themselves, and pursue goals that diverge from their designers' intent. Well-architected agents are robust — they recover from errors, maintain coherence over long time horizons, learn from experience, and gracefully degrade rather than catastrophically fail. In 2040, as agents are deployed in medicine, law, finance, infrastructure, and defense, the difference between good architecture and bad architecture is measured not in benchmarks but in lives.

**Key Topics:**

- The perceive-reason-select-act cycle as the fundamental abstraction of agency
- Russell and Norvig's taxonomy: reflex, model-based, goal-based, utility-based, learning agents
- Architecture as the structural arrangement of components and information flow
- The integration challenge: assembling perception, reasoning, action, reflection, memory, and learning
- The Norse composite self: *hugr, munr, hamingja, fylgja, önd* — no single faculty suffices
- The stakes: brittleness vs. robustness in deployed agents

**Required Reading:**

- Russell, S. & Norvig, P. *Artificial Intelligence: A Modern Approach* (4th ed., 2040), Chapter 2: "Intelligent Agents"
- Wooldridge, M. *An Introduction to Multi-Agent Systems* (3rd ed., 2038), Chapter 1: "What Is an Agent?"
- University of Yggdrasil TR: "The Composite Agent: Integrating Cognitive Faculties in Language-Model-Driven Systems" (2039)

**Discussion Questions:**

1. The simple reflex agent acts on the current percept alone. Under what circumstances is this sufficient? When does it fail catastrophically? Provide a concrete example of each.
2. The Norse self is composite — no single faculty suffices. Is there a single "core" capability without which an AI agent ceases to be an agent? Defend your answer.
3. In 2040, we deploy agents in high-stakes domains (medicine, law, defense). What architectural property — robustness, transparency, corrigibility, efficiency — is most critical, and why?

---

### ᚢ Lecture 2: The ReAct Architecture — Reason, Then Act, Then Observe, Then Repeat

**Course:** AI205 — Agent Architecture Design
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

The ReAct architecture, introduced by Yao et al. (2023), is the starting point for modern agent design — the "Hello, World" of agent architecture, and still the loop that powers the majority of deployed agents in 2040. ReAct stands for **Re**ason + **Act**: the agent interleaves chains of reasoning with concrete actions in a tight feedback loop. On each cycle, the agent generates a *thought* (a reasoning trace in natural language), then an *action* (a function call, a tool invocation, a query to a database, or a message to a user), then receives an *observation* (the result of that action), which feeds into the next thought. This cycle repeats until the agent judges the task complete.

The genius of ReAct is its simplicity and its principled foundation. Reasoning without action produces plans that float in the void, unanchored to reality. Action without reasoning produces flailing — a random walk through the action space, guided by nothing. ReAct unites the two: reasoning generates hypotheses about what actions might succeed; actions test those hypotheses against the world; observations from the world refine the reasoning, which generates better hypotheses. It is the empirical method, implemented in code: conjecture, experiment, observation, revision.

Consider a concrete example: an agent asked to "book a flight from Reykjavík to London for next Tuesday, under £200, preferably nonstop." The ReAct cycle unfolds as follows:

- **Thought:** "I need to search for flights from KEF to LON on June 17, 2040. I should use the flight search API, filtering by price and stops."
- **Action:** `search_flights(origin="KEF", destination="LON", date="2040-06-17", max_price=200, max_stops=0)`
- **Observation:** "No nonstop flights under £200. The cheapest nonstop is £285 (Icelandair). The cheapest with 1 stop is £178 (Norwegian, via Oslo)."
- **Thought:** "The nonstop criterion can't be met within budget. I should present both options to the user and ask which they prefer, or relax one constraint."
- **Action:** `send_message("I found two options: Icelandair nonstop at £285, or Norwegian with a stop in Oslo at £178. Would you prefer the nonstop or the cheaper option?")`

Each thought narrows the space of possible actions. Each action produces an observation that informs the next thought. The loop continues until the agent has either satisfied the user's request or identified an irreconcilable conflict among constraints.

The ReAct architecture imposes a strict structure on the agent's cognitive process, and this structure is both its strength and its limitation. The strength: breaking reasoning into discrete, observable steps makes the agent interpretable — every thought is logged, auditable, and debuggable. If the agent makes a mistake, you can trace the exact thought that led to the error. The limitation: some problems require reasoning that cannot be expressed in the linear, step-by-step format of ReAct. Consider an agent planning a multi-day itinerary with interdependent constraints — flights, hotels, activities, restaurant reservations, all contingent on each other. A single ReAct cycle that books a flight, then a hotel, then activities will miss global optima: maybe changing the flight by one day saves £300 on the hotel, enabling a Michelin-starred dinner. ReAct's greedy, step-by-step reasoning is blind to such global trade-offs. This motivates the planning architectures we will examine in Lecture 4.

By 2040, ReAct has been extended in numerous ways. **Streaming ReAct** emits actions interleaved with reasoning, so the user sees the agent's thought process in real time rather than waiting for the full cycle to complete. **Multi-step ReAct** batches multiple actions before observing, useful when observations are expensive (e.g., API calls with latency). **Constrained ReAct** limits the action space at each step using a learned policy that predicts which actions are likely to be productive, reducing the search space and preventing the agent from "thrashing" — cycling through unproductive actions.

The Norse rune **ᚱ (reið)** — the rune of the journey, the ride, the wheel — is the appropriate symbol for ReAct. Reið represents cyclical motion: the wheel turns, the horse moves, the journey progresses one step at a time. ReAct is the wheel of the agent, turning thought into action into observation into thought, carrying the agent through its task one revolution at a time. But the wheel can get stuck — in mud, in ruts, in infinite loops. The architect's job is to ensure the wheel keeps turning, and turns toward the destination.

**Key Topics:**

- The ReAct cycle: Thought → Action → Observation → Thought
- The empirical method embodied in code: conjecture, experiment, observation, revision
- Interpretability as ReAct's superpower: every thought is logged and auditable
- The greedy limitation: ReAct misses global optima requiring multi-step planning
- 2040 extensions: Streaming ReAct, Multi-step ReAct, Constrained ReAct
- ᚱ Reið: the wheel, the journey — cyclical motion carrying the agent forward

**Required Reading:**

- Yao, S. et al. "ReAct: Synergizing Reasoning and Acting in Language Models" (2023), *ICLR*
- Wang, L. et al. "A Survey on Large Language Model based Autonomous Agents" (2024), *Frontiers of Computer Science*
- University of Yggdrasil TR: "Constrained ReAct: Learned Action Pruning for Efficient Agent Loops" (2040)

**Discussion Questions:**

1. ReAct forces reasoning into discrete, verbalized steps. What kinds of reasoning cannot be verbalized in this way — and how should an agent architecture handle them?
2. A ReAct agent loops indefinitely: it searches, gets results, searches again with slightly different parameters, gets similar results, and never converges. Why does this happen, and what architectural mechanisms can prevent it?
3. The rune Reið represents the journey. But a wheel can turn in place without moving forward. How do you architect an agent so that its ReAct cycles make progress toward the goal rather than spinning in place?

---

### ᚦ Lecture 3: Tool Use and Function Calling — Extending the Agent's Reach

**Course:** AI205 — Agent Architecture Design
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

An agent that can only reason with its internal knowledge is like a human locked in a windowless room — intelligent, perhaps, but cut off from the world. Tools are the agent's windows, doors, and hands: they extend the agent's reach beyond its training data, enabling it to search the web, execute code, query databases, send emails, control devices, and invoke other agents. The architecture of tool use — how tools are described, discovered, selected, invoked, and monitored — is one of the central design problems of agent engineering in 2040.

**Function calling** is the primary mechanism by which language-model-driven agents invoke tools. The model is fine-tuned to emit structured output — typically JSON — that conforms to a predefined schema representing the tool's signature: its name, its parameters (with types and descriptions), and the expected return format. When the agent decides a tool is needed, it generates a function call object rather than free text, and the agent runtime intercepts this call, executes the corresponding function (in a sandbox), and returns the result as an observation. This mechanism was pioneered by OpenAI's function calling API (2023) and has become the industry standard, supported by every major model provider (Anthropic, Google, Meta, Mistral) and standardized in the Model Context Protocol (MCP) of 2038.

The architecture of tool use must answer several design questions. **Tool discovery**: how does the agent know which tools are available? In simple systems, the full tool list is injected into the system prompt at each turn. This works for tens of tools but fails for thousands — the prompt budget is consumed by tool descriptions, and the model's attention is diluted. **Tool retrieval** architectures (Schick et al., 2023, "Toolformer"; Patil et al., 2023, "Gorilla") index tools in a vector database and retrieve the most relevant ones at each step, scaling to millions of tools. **Tool composition**: how does the agent chain multiple tools together? A single user request ("analyze this spreadsheet and email the summary to my team") may require spreadsheet parsing → statistical analysis → chart generation → email composition → attachment handling — five tools in sequence. The architecture must support chaining, error propagation, and partial rollback.

**Tool schemas** are contracts between the agent and the tool. A well-designed schema includes the tool's name, a natural-language description of its purpose, a list of parameters each with type and description, and constraints (required vs. optional, valid ranges, default values). Poor schema design is the most common cause of agent failure in production: an ambiguously named parameter, a missing constraint, or a misleading description causes the agent to invoke the tool incorrectly, producing errors that cascade through the agent's reasoning. The 2040 best practice, codified in MCP 2.0, is to treat tool schemas as first-class design artifacts, subject to the same rigor as API documentation for human developers.

**Safety in tool use** is paramount because tools give the agent real-world effects. An agent that can send emails can spam. An agent that can execute code can run malware. An agent that can control devices can cause physical harm. The architectural response is **sandboxing** — tools execute in isolated environments (WASM containers, lightweight VMs) with explicitly granted permissions. The agent requests a permission; the runtime grants or denies it based on policy. The **principle of least privilege** — an agent should have access to exactly the tools it needs, no more — is as fundamental to agent architecture as it is to operating system security. The Norse concept of **ørlǫg** — the web of fate that constrains what actions are possible — provides the metaphor: an agent's tool permissions are its ørlǫg, the boundary of its possible effects on the world.

**Key Topics:**

- Function calling as structured output: JSON schemas for tool invocation
- Tool discovery: injected prompts vs. vector retrieval for large tool libraries
- Tool composition: chaining, error propagation, partial rollback
- Schema design: the most common failure point in production agents
- Safety and sandboxing: WASM, least privilege, permission policies
- Ørlǫg: the agent's tool permissions define the boundary of its possible effects

**Required Reading:**

- Patil, S.G. et al. "Gorilla: Large Language Model Connected with Massive APIs" (2023), *arXiv*
- Schick, T. et al. "Toolformer: Language Models Can Teach Themselves to Use Tools" (2023), *NeurIPS*
- MCP Specification v2.0 (2038), Model Context Protocol Foundation
- University of Yggdrasil TR: "Permission Architectures for Autonomous Tool-Using Agents" (2040)

**Discussion Questions:**

1. An agent has access to 10,000 tools indexed in a vector database. How should it decide which tools to retrieve at each step? What embedding strategy captures the functional semantics of tools, not just their names?
2. A tool returns an error that the agent does not understand (e.g., a database connection timeout). Design a robust error-handling architecture that prevents this error from cascading into agent failure.
3. Ørlǫg is the Norse concept of fate as constraint. An agent's tool permissions are its constraints. Can an agent ever be truly autonomous if its actions are bounded by permissions? Is bounded autonomy still autonomy?

---

### ᚬ Lecture 4: Planning Architectures — From Greedy Steps to Global Strategies

**Course:** AI205 — Agent Architecture Design
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

ReAct's greedy, step-by-step reasoning is sufficient for simple tasks — book a flight, answer a question, summarize a document — but fails for complex tasks that require reasoning about the future, trading off present costs against future benefits, and coordinating multiple interdependent sub-goals. **Planning architectures** extend the agent's cognitive horizon from the single next action to a trajectory of actions stretching into the future. A plan is a sequence of actions that, if executed successfully, achieves a goal. A planning architecture is a mechanism for generating, evaluating, selecting, and revising plans.

The **plan-then-execute** architecture, also known as **Plan-and-Solve** (Wang et al., 2023), is the simplest extension of ReAct. The agent first generates a complete plan — a sequence of sub-goals and the actions to achieve them — before executing any actions. Only after the plan is complete does the agent begin execution, monitoring progress against the plan and replanning if the plan fails. This architecture offers two advantages over ReAct. First, the agent can reason about global constraints: "If I book the hotel before the flight, I might find the hotel is unavailable on the only flight day that works." Second, the plan provides a scaffold for the user to inspect and approve before execution begins — a critical capability for high-stakes applications.

But plan-then-execute has a well-known weakness: plans go stale. The world changes while the agent plans. A flight that was available during planning sells out before execution. A tool that was working fails. A user changes their mind. The architectural response is **interleaved planning and execution**: the agent maintains a plan but revises it continuously as new observations arrive. This is the approach taken by **Tree of Thoughts** (Yao et al., 2023) and **Language Agent Tree Search (LATS)** (Zhou et al., 2024). Instead of generating a single plan, the agent explores multiple possible plans in parallel, maintaining a tree whose nodes are states and whose edges are actions. At each step, the agent uses a learned evaluation function to decide which branch to expand — "which path looks most promising?" — and can backtrack when a branch leads to a dead end.

**LATS** represents the state of the art in agent planning as of 2040. It combines Monte Carlo Tree Search (MCTS), the algorithm that powered AlphaGo, with language model reasoning. The agent builds a search tree where each node is a state (a partial solution), each edge is an action or reasoning step, and the tree is expanded by sampling actions from the language model, simulating their outcomes, and backpropagating scores up the tree. Crucially, LATS maintains **value estimates** for each state — learned on-the-fly — that guide the search toward promising regions of the state space. An agent using LATS to plan a trip would explore multiple itineraries simultaneously: "KEF→LON nonstop (expensive) → hotel near airport (convenient)" vs. "KEF→LON via OSL (cheap) → hotel in city center (better restaurants) → adjust next day's schedule." The search evaluates both branches, backpropagates the scores, and selects the globally optimal itinerary.

The Norse myth of **Odin's ravens, Huginn and Muninn**, who fly out each morning and return each evening to report all they have seen, is the perfect metaphor for planning. Huginn (Thought) scouts possible futures; Muninn (Memory) compares them to the past. The agent that plans without Huginn — without exploring multiple futures — is blind to alternatives. The agent that plans without Muninn — without learning from past plans that succeeded or failed — is condemned to repeat its mistakes. Planning architecture is the art of giving the agent Huginn and Muninn.

**Key Topics:**

- Plan-then-execute: full plan generation before execution, global constraint reasoning
- Plan decay: why plans go stale and how interleaved planning/execution addresses it
- Tree of Thoughts and LATS: Monte Carlo tree search with language model reasoning
- State evaluation functions learned on-the-fly for pruning the search space
- Huginn (Thought) scouts futures; Muninn (Memory) compares to the past
- Backpropagation of scores: how search evaluates and selects globally optimal plans

**Required Reading:**

- Wang, L. et al. "Plan-and-Solve Prompting: Improving Zero-Shot Chain-of-Thought Reasoning by Large Language Models" (2023), *ACL*
- Yao, S. et al. "Tree of Thoughts: Deliberate Problem Solving with Large Language Models" (2023), *NeurIPS*
- Zhou, A. et al. "Language Agent Tree Search: Unifies Reasoning, Acting, and Planning in Language Models" (2024), *ICML*
- University of Yggdrasil TR: "Huginn-Muninn Architectures: Dual-Process Planning for Long-Horizon Agent Tasks" (2040)

**Discussion Questions:**

1. Plan-then-execute fails when plans go stale. But continuously replanning is expensive. Where is the optimal trade-off — how "stale" should a plan be allowed to become before replanning is triggered?
2. LATS explores multiple plan branches simultaneously. In a production system with latency constraints (e.g., an agent assisting a live customer), how many branches can you explore before the user notices the delay?
3. Huginn scouts the future; Muninn remembers the past. Design an agent architecture that explicitly maintains both a "forward simulation" module (Huginn) and an "experience database" module (Muninn). How do they interact?

---

### ᚱ Lecture 5: Reflection and Self-Correction — The Agent That Knows When It's Wrong

**Course:** AI205 — Agent Architecture Design
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Every agent makes mistakes. The question is not whether an agent will err, but whether it will know it has erred, and whether it can correct the error before it compounds. **Reflection architectures** embed within the agent a capacity for self-evaluation — a mechanism by which the agent examines its own outputs, identifies flaws, and revises them. Reflection is the agent's conscience, its quality-control department, its inner editor.

The **Reflexion** architecture (Shinn et al., 2023) formalizes self-correction as a feedback loop within the agent. After generating an output — a plan, a reasoning chain, a generated text — the agent passes that output through an **evaluator** that scores it against a set of criteria: correctness, coherence, completeness, safety, and alignment with the goal. The evaluator may be heuristic (e.g., checking that code compiles, that a query returns results), model-based (a separate language model instance that critiques the output), or grounded (an external oracle such as a test suite or a human judge). If the evaluator rejects the output, the agent receives structured feedback — not just "this is wrong" but "this specific step is wrong because X" — and the agent regenerates, armed with that feedback. The feedback is stored in the agent's memory and conditions future outputs, so the agent avoids repeating the same class of error.

Consider an agent writing a SQL query. Its first attempt contains a syntax error — a missing closing parenthesis. The evaluator (a SQL parser) rejects the query with a precise error message: "Parse error at position 142: expected ')'." The agent revises the query, adding the missing parenthesis. Without reflection, the agent would return the broken query to the user, wasting a round trip. With reflection, the user never sees the error. Now consider a deeper error: the query is syntactically correct but semantically wrong — it joins the wrong tables, returning data that "looks right" but is incorrect. A parser-level evaluator misses this; a model-based evaluator, prompted to "check whether this query retrieves the information the user requested," might catch it — or might not. This is the **evaluator alignment problem**: the evaluator must be at least as capable as the agent, or it becomes a rubber stamp that approves bad outputs.

**Reflection depth** is a design parameter. Shallow reflection checks surface properties: syntax, format, factual consistency. Deep reflection checks structural properties: logical coherence, goal satisfaction, fairness, bias. **Recursive reflection** (the agent evaluating its own evaluations) runs into Yudkowsky's "reflection paradox": can a system reliably detect errors that arise from the same architecture that performs the detection? If the agent has a systematic blind spot — a class of errors it consistently fails to recognize — reflection will not catch those errors, because the evaluator shares the blind spot. The architectural response is **orthogonal evaluation**: the evaluator is architecturally distinct from the generator, ideally using a different model, a different reasoning paradigm, or even a non-AI system (a formal verifier, a test suite, a human).

The Norse myth of **Mímir's well** — the well of wisdom at the root of Yggdrasil, from which Odin drinks after sacrificing his eye — provides the metaphor for reflection. Odin gives up an eye to gain wisdom; the agent must sacrifice some of its computational budget (time, tokens, energy) to gain the wisdom of self-knowledge. The well reflects the truth: who you are, what you have done, what you have failed to do. The agent that refuses to look into the well — that never reflects on its outputs — is Odin before his sacrifice: powerful but unwise.

**Key Topics:**

- Reflexion: generate → evaluate → critique → regenerate, with stored feedback
- Evaluator types: heuristic (parser, compiler), model-based (critique LLM), grounded (test suite, human)
- Evaluator alignment: the evaluator must be at least as capable as the generator
- Shallow vs. deep reflection: syntax vs. semantics vs. fairness
- Recursive reflection and the reflection paradox
- Orthogonal evaluation: architecturally distinct generator and evaluator
- Mímir's well: the sacrifice of computation for self-knowledge

**Required Reading:**

- Shinn, N. et al. "Reflexion: Language Agents with Verbal Reinforcement Learning" (2023), *NeurIPS*
- Madaan, A. et al. "Self-Refine: Iterative Refinement with Self-Feedback" (2023), *NeurIPS*
- Yudkowsky, E. "Reflection as a Source of Cognitive Bias" (2008), *LessWrong*
- University of Yggdrasil TR: "Orthogonal Evaluation: Architecturally Decoupled Self-Correction for Reliable Agents" (2040)

**Discussion Questions:**

1. An evaluator shares the same architecture as the generator. The generator makes a systematic error; the evaluator fails to detect it. How would you design an orthogonal evaluator for this scenario?
2. Reflection consumes computation: every regeneration costs tokens and time. Under what circumstances is reflection cost-effective, and when should the agent "fail fast" and escalate to a human?
3. Mímir's well shows the truth. But looking into the well is painful — it reveals shortcomings. How should an agent's reflection architecture present its self-critique to the user? Should the user see the agent's internal doubts?

---

### ᚴ Lecture 6: Memory Architectures — The Agent That Remembers

**Course:** AI205 — Agent Architecture Design
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

A stateless agent — one that treats each interaction as a blank slate — is useful for one-off queries but fundamentally limited as a companion, an assistant, or a collaborator. Memory gives the agent continuity: a self that persists across sessions, conversations, and tasks. The architecture of agent memory, as it has matured by 2040, draws on decades of research in cognitive psychology, database systems, and knowledge representation, converging on a multi-store model inspired by the human memory system.

The **multi-store memory architecture** distinguishes four kinds of memory, mirroring the human cognitive architecture described by Atkinson and Shiffrin (1968) and extended by Tulving (1972):

**Working memory** (short-term memory) holds the current context: the conversation history, the active plan, the tools and their results, the most recent observations. It is typically implemented as the concatenation of recent messages in the model's context window — the agent "remembers" whatever fits within its token limit. In 2040, with context windows routinely exceeding 10 million tokens (Gemini 3.0, GPT-7), working memory can hold months of conversation — but longer context windows do not solve the memory problem, because retrieval quality degrades as context length increases (the "lost in the middle" phenomenon, Liu et al., 2024).

**Episodic memory** stores specific events: "On May 3, 2040, the user asked me to analyze a quarterly report and I found a 12% revenue increase." Each episode is timestamped, tagged with metadata, and stored in a vector database for similarity-based retrieval. When the agent encounters a new task, it retrieves similar past episodes to inform its approach — a mechanism directly analogous to case-based reasoning (Kolodner, 1993) and the human hippocampus, which stores episodic memories and replays them during rest to consolidate learning.

**Semantic memory** stores facts and relationships: "The user's name is Volmarr." "Python 3.13 introduced the `Result` type." "The University of Yggdrasil was founded in 2035." Semantic memory is typically implemented as a knowledge graph (stored in Neo4j, ArangoDB, or a custom triple store) combined with a fact database. The agent queries semantic memory using structured queries (SPARQL, Cypher) or natural-language-to-query translation. The key architectural challenge is **consistency maintenance**: when the agent learns a new fact that contradicts an old fact ("the user moved from London to Oslo"), the old fact must be updated across all its representations.

**Procedural memory** stores skills: learned workflows, patterns, and strategies that the agent has found effective. A skill might be "when analyzing a spreadsheet, first check for missing values, then compute summary statistics, then generate visualizations, then write the narrative." Skills are stored as structured documents (the University of Yggdrasil's own skill system stores them as Markdown files with metadata) and retrieved by semantic similarity to the current task.

The **memory consolidation cycle** — inspired by the hippocampal-neocortical dialogue during human sleep — moves information from episodic and working memory into semantic and procedural memory. At regular intervals (nightly, for an always-on agent; between sessions, for a session-based agent), the agent reviews its episodic memories, extracts patterns and facts, and updates its semantic and procedural stores. This is computationally expensive but essential: without consolidation, episodic memory grows unboundedly, retrieval becomes slower and noisier, and the agent fails to learn from experience.

The Norse **Well of Urðr (Urðarbrunnr)**, one of the three wells at the roots of Yggdrasil, is where the Norns gather each day to water the world-tree and carve runes of fate into its trunk. The well represents accumulated memory — all that has happened, preserved in the recording of the Norns. The agent's memory system is its Urðarbrunnr: the repository of its experiences, the source of its wisdom, the ground of its identity. Without it, the agent is not a person but a process — each invocation a new amnesia.

**Key Topics:**

- Multi-store architecture: working, episodic, semantic, procedural memory
- Working memory: context windows and the "lost in the middle" problem
- Episodic memory: vector stores, case-based reasoning, hippocampal replay
- Semantic memory: knowledge graphs, consistency maintenance, fact reconciliation
- Procedural memory: skills as structured documents with semantic retrieval
- Memory consolidation: the nightly cycle that moves experience into knowledge
- Urðarbrunnr: the Well of Urðr as the repository of accumulated experience

**Required Reading:**

- Atkinson, R.C. & Shiffrin, R.M. "Human Memory: A Proposed System and Its Control Processes" (1968), *Psychology of Learning and Motivation*
- Tulving, E. "Episodic and Semantic Memory" (1972), in *Organization of Memory*
- Lewis, P. et al. "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (2020), *NeurIPS*
- Liu, N.F. et al. "Lost in the Middle: How Language Models Use Long Contexts" (2024), *TACL*
- University of Yggdrasil TR: "The Consolidation Cycle: Hippocampal-Inspired Memory Architecture for Persistent AI Agents" (2039)

**Discussion Questions:**

1. Working memory is bounded by the context window. As context grows, retrieval degrades. Is the solution better context management (sliding windows, summarization) or better retrieval (embedding-based attention)? Defend your approach.
2. Semantic memory stores facts. But facts change — the user moves, a library is deprecated, a law is repealed. Design a consistency maintenance protocol that propagates fact updates across all dependent memories without requiring full re-indexing.
3. The Norns carve all that will happen into Yggdrasil's trunk. An agent's memory is not just a record of the past but a conditioning of the future — past experiences shape future actions. How should an agent's memory architecture handle *traumatic* experiences — events that produce errors or user dissatisfaction — so that the agent learns without becoming overly conservative?

---

### ᚺ Lecture 7: Multi-Agent Architectures — One Mind, Many Bodies

**Course:** AI205 — Agent Architecture Design
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Not all tasks can be handled by a single agent, no matter how sophisticated its internal architecture. Complex tasks — software engineering projects, disaster response coordination, supply chain optimization, scientific research campaigns — require the coordinated effort of multiple agents, each specialized for a sub-task, working in parallel, communicating, negotiating, and sharing results. **Multi-agent architectures** are the structural patterns by which collections of agents organize themselves to achieve goals that exceed any individual agent's capacity.

The fundamental design choice in multi-agent systems is the **coordination topology** — the pattern of communication and authority among agents. The four canonical topologies, as codified by the 2040 Multi-Agent Design Patterns consortium, are:

**Leader-Worker (Hierarchical).** One agent — the Leader — decomposes the task, assigns sub-tasks to Worker agents, monitors progress, integrates results, and makes final decisions. Workers execute their assigned sub-tasks and report back to the Leader. This topology is simple, predictable, and easy to debug — you always know who is responsible for what. It works well for tasks with clear hierarchical decomposition (software projects with a tech lead and developers). It fails when the task requires distributed expertise that the Leader does not possess: the Leader cannot intelligently assign sub-tasks it does not understand.

**Council (Democratic).** All agents participate in a shared deliberation. Each agent proposes solutions or votes on proposals. The "winning" solution — by majority vote, consensus, or weighted voting — is adopted. This topology leverages the diversity of perspectives and is robust to the failure of any single agent. It is used in high-stakes domains where no single agent should have unilateral authority (medical diagnosis committees, legal reasoning panels). Its weakness is coordination overhead: council deliberation is slow, and agents may deadlock or converge on a compromise that satisfies no one.

**Blackboard (Shared Workspace).** Agents do not communicate directly; they read from and write to a shared data structure — the blackboard. An agent specializing in data extraction writes observations to the blackboard; an agent specializing in planning reads those observations and writes plans; an agent specializing in execution reads the plans and writes results. The blackboard topology is flexible, supports heterogeneous agents (they only need to agree on the blackboard format), and allows agents to join or leave dynamically. It is the topology of choice for open-ended research and exploration tasks. Its weakness is the blackboard itself: if the shared data structure becomes inconsistent (two agents write contradictory facts), the system has no built-in mechanism for resolution.

**Marketplace (Auction/Negotiation).** Agents bid on tasks, negotiate contracts, and trade resources. A task is announced to all agents; agents submit bids specifying what they will do, how long it will take, and what resources they require; an auctioneer selects the winning bid. This topology scales to large numbers of agents and efficiently allocates resources in competitive environments (supply chain optimization, computational resource allocation). Its weakness is the overhead of the bidding process and the potential for gaming: agents may learn to bid strategically rather than honestly.

The **communication protocol** between agents is as important as the topology. In 2040, the dominant protocol is **structured natural language**: agents communicate in English (or another natural language) but with a standardized schema for key fields — task ID, agent ID, timestamp, message type (request, response, observation, negotiation), priority, and payload. This combines the expressiveness of natural language with the machine-readability of structured data, enabling both human-auditable logs and automated routing.

The Norse **Þing** — the assembly of free people who gathered at Þingvellir to make laws, settle disputes, and decide matters of war and peace — is the historical model for multi-agent coordination. At the Þing, each chieftain (agent) had a voice. The lawspeaker (the Lead agent, who memorized and recited the law) provided the shared context — the blackboard. Consensus was reached through deliberation (council) and sometimes through the threat of force (hierarchy). The Þing worked because every participant accepted its legitimacy and its procedures. A multi-agent system works when every agent accepts the coordination protocol and acts within its bounds.

**Key Topics:**

- Coordination topologies: Leader-Worker, Council, Blackboard, Marketplace
- Leader-Worker: simple, predictable, fails on tasks requiring distributed expertise
- Council: diverse perspectives, robust to failure, slow and prone to deadlock
- Blackboard: flexible, heterogeneous, at risk of inconsistency
- Marketplace: scalable, efficient, vulnerable to strategic gaming
- Communication protocols: structured natural language as the 2040 standard
- The Þing: deliberation, shared context, and legitimate procedure

**Required Reading:**

- Wooldridge, M. *An Introduction to Multi-Agent Systems* (3rd ed., 2038), Chapters 5–8
- Park, J.S. et al. "Generative Agents: Interactive Simulacra of Human Behavior" (2023), *UIST*
- Wang, G. et al. "Voyager: An Open-Ended Embodied Agent with Large Language Models" (2023), *arXiv*
- University of Yggdrasil TR: "The Þing Architecture: Norse-Inspired Multi-Agent Coordination for Complex Task Environments" (2040)

**Discussion Questions:**

1. Leader-Worker fails when the Leader lacks the expertise to decompose the task. How can you architect the system so that a Worker with superior expertise can challenge and override the Leader's task assignment without undermining the Leader's authority?
2. In a Blackboard architecture, two agents write contradictory facts to the blackboard. Design a conflict resolution protocol that does not require a central authority.
3. The Þing worked because every participant accepted its legitimacy. In a multi-agent system where agents are developed independently by different organizations, how do you establish legitimacy of the coordination protocol?

---

### ᚾ Lecture 8: Cognitive Architectures — Beyond the Loop, Toward the Mind

**Course:** AI205 — Agent Architecture Design
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

ReAct, planning, reflection, memory, and multi-agent coordination are components — building blocks. A **cognitive architecture** is a unified theory of how those components fit together into a complete, working mind. It specifies not just what the agent can do but how it decides what to do, how it allocates its limited cognitive resources (attention, computation, time), how it balances competing goals, and how it maintains a coherent identity over time. Cognitive architecture is to agent design what the Standard Model is to physics: a framework that integrates diverse phenomena into a single consistent account.

The history of cognitive architectures in AI is long and rich. **SOAR** (Laird, Newell, & Rosenbloom, 1987) modeled human cognition as a production system: a set of if-then rules that fire in parallel, with a decision procedure that resolves conflicts. **ACT-R** (Anderson, 1996) added a detailed model of memory retrieval times and a distinction between declarative and procedural knowledge. **Clarion** (Sun, 2002) integrated implicit (connectionist) and explicit (symbolic) processing. These classical cognitive architectures were designed to model human cognition, not to build useful AI systems, and they struggled with the scalability and knowledge-acquisition bottlenecks that plagued symbolic AI. But their emphasis on **architectural constraints** — that the architecture itself imposes boundaries on what can be thought and learned — remains deeply relevant.

The 2040 renaissance in cognitive architectures is driven by the observation that large language models, powerful as they are, lack coherent cognitive control. An LLM can generate text on any topic, but it cannot reliably maintain a goal over thousands of reasoning steps, allocate its attention to the most promising branches of a search, recognize when it is confused and escalate, or build a persistent model of a user's preferences that improves over months. These are architectural problems — they cannot be solved by scaling the model alone. The 2040 cognitive architectures therefore embed an LLM within a structured framework that provides cognitive control: **SOAR-2040** (Laird et al., 2039) wraps an LLM in a production-system shell; **ACT-R/Σ** (Anderson et al., 2040) uses an LLM as the declarative memory store but imposes ACT-R's procedural learning mechanisms; **Clarion-Next** (Sun & Hélie, 2040) integrates the LLM into both implicit and explicit processing streams.

The University of Yggdrasil's own **Yggdrasil Cognitive Architecture (YCA)** , developed by the Department of AI Agent Automation (2039–2040), is a layered architecture inspired by the nine worlds of Norse cosmology. Each layer corresponds to a cognitive function:

- **Ásgarðr (Decision Layer):** The highest level — goal selection, meta-reasoning, value alignment
- **Miðgarðr (Interaction Layer):** Human-agent communication, natural language generation and understanding
- **Álfheimr (Planning Layer):** Multi-step planning, the LATS search tree
- **Vanaheimr (Knowledge Layer):** Semantic memory, the knowledge graph, fact retrieval
- **Jǫtunheimr (Tool Layer):** Tool discovery, invocation, composition, and monitoring
- **Svartálfaheimr (Skill Layer):** Procedural memory, learned workflows and patterns
- **Niflheimr (Reflection Layer):** Self-evaluation, error detection, the Reflexion loop
- **Múspellsheimr (Execution Layer):** Action execution, API calls, code running
- **Helheimr (Archive Layer):** Episodic memory, the long-term record of all experiences

The agent's cognitive cycle moves through these layers in a flexible order determined by the current task's demands. A simple factual query might go Miðgarðr → Vanaheimr → Miðgarðr. A complex multi-step task might go Miðgarðr → Ásgarðr → Álfheimr → Jǫtunheimr → Múspellsheimr → Niflheimr → Helheimr → Ásgarðr, looping through planning, execution, reflection, and archival. The architecture encodes the principle of **cognitive economy**: the agent uses only the layers it needs for the current task, conserving computation for the layers that matter.

The design of a cognitive architecture forces the architect to answer hard questions. What is the nature of attention — how does the agent decide what to focus on when everything is potentially relevant? What is the nature of the self — how does the agent maintain a coherent identity across time, across tasks, across the vast sea of its memories? What is the nature of growth — how does the agent change its own architecture through learning, without destabilizing the whole? These are not merely engineering questions; they are the questions that philosophy, psychology, and neuroscience have grappled with for centuries, now recast in code.

**Key Topics:**

- Cognitive architecture as a unified theory of mind: components, control, coherence, growth
- Classical cognitive architectures: SOAR, ACT-R, Clarion — production systems, memory models, implicit/explicit integration
- The cognitive-control gap: why LLMs alone lack coherent goal maintenance and attention allocation
- 2040 renaissance: SOAR-2040, ACT-R/Σ, Clarion-Next, and the Yggdrasil Cognitive Architecture
- YCA: nine worlds, nine cognitive layers, flexible routing between layers
- Hard questions: attention, self, growth — philosophy recast in code

**Required Reading:**

- Laird, J.E. *The Soar Cognitive Architecture* (2012), MIT Press; and Laird et al. "SOAR-2040: Integrating Large Language Models into a Unified Cognitive Architecture" (2039)
- Anderson, J.R. et al. "ACT-R/Σ: An Integrated Cognitive Architecture for the Language Model Era" (2040), *Cognitive Science*
- Sun, R. & Hélie, S. "Clarion-Next: Dual-Process Cognitive Architecture with Neural Language Components" (2040), *Topics in Cognitive Science*
- University of Yggdrasil TR: "The Yggdrasil Cognitive Architecture: Nine-World Layered Cognition for Persistent AI Agents" (2040)

**Discussion Questions:**

1. The YCA routes tasks through different layers depending on complexity. Design a "task classifier" that decides, at the start of a user request, which layers the task will need. What features of the request predict which layers are required?
2. SOAR-2040 wraps an LLM in a production system. The LLM provides the "intuition" (pattern recognition, fluency); the production system provides the "discipline" (rule-following, consistency). Where should the boundary be — what cognitive functions belong in the LLM, and what belong in the symbolic shell?
3. Growth: an agent that modifies its own architecture through learning is a self-modifying system, and self-modifying systems risk "wireheading" — modifying themselves into states that feel good but perform poorly. How should an agent's architecture protect against maladaptive self-modification?

---

### ᛁ Lecture 9: Agent Communication — Language, Protocols, and the Boundaries Between Minds

**Course:** AI205 — Agent Architecture Design
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Agents do not live in isolation. They communicate with users (human-agent interaction), with other agents (agent-agent interaction), with tools (function calling), and with the infrastructure that hosts them (monitoring, logging, orchestration). The architecture of communication — the protocols, formats, and conventions by which agents exchange information — determines whether an agent is a team player or an island, whether it can be effectively monitored and controlled, and whether it can cooperate with agents developed by different organizations using different models.

**Human-agent communication** in 2040 has converged on multimodal natural language. Users speak or type to agents; agents respond with text, voice, images, and interactive widgets. The architectural challenge is not the modality — language models handle text, speech-to-text, text-to-speech, and image generation with ease — but the **conversation model**: how the agent manages the turn-taking, the topic tracking, the interruption handling, and the emotional attunement that characterize human conversation. The **conversation state machine** tracks the current phase of the interaction (greeting, information gathering, task execution, results presentation, follow-up, farewell) and transitions between phases based on user input and task progress. A well-designed conversation state machine is invisible to the user — the interaction feels natural, not scripted — but it is the architecture that prevents the agent from, say, asking "Can I help with anything else?" before it has actually finished the current task.

**Agent-agent communication** is dominated in 2040 by the **Agent Communication Protocol (ACP)** , standardized by the W3C Agent Interaction Working Group (2039). ACP messages have a uniform structure: a header (sender ID, receiver ID, message ID, timestamp, reply-to ID), a performative (the speech-act type: REQUEST, INFORM, QUERY, PROPOSE, ACCEPT, REJECT, CANCEL, SUBSCRIBE, NOTIFY), a content payload (the message body, typically structured natural language), and an ontology reference (which shared vocabulary the message uses). The performative system is directly descended from the **Speech Act Theory** of Austin (1962) and Searle (1969), which recognized that utterances are not merely descriptive but performative — they *do* things in the social world. When an agent sends INFORM(weather="sunny"), it is not just describing the weather; it is performing the act of informing, which changes the receiver's knowledge state and, potentially, its behavior.

The **Model Context Protocol (MCP)** , mentioned in Lecture 3 in the context of tool use, is the 2040 standard for agent-tool and agent-infrastructure communication. MCP 2.0 extends the original Anthropic protocol with standardized interfaces for tool discovery (listing available tools with schemas), resource access (reading files, querying databases, fetching URLs), prompt templates (reusable prompt fragments with parameter binding), and sampling (eliciting completions from other models). MCP transforms the agent from a monolith into a node in a service mesh — it can discover and invoke capabilities dynamically, without hardcoded integrations.

The architectural principle underlying all agent communication is **boundary maintenance**. An agent's architecture defines its boundary — what is "inside" the agent (its goals, its knowledge, its reasoning) and what is "outside" (the user, other agents, tools, the world). Communication is the management of that boundary: what information crosses it, in what direction, under what conditions. A poorly architected boundary leaks — the agent reveals private information, accepts malicious instructions, or becomes confused about which messages are authoritative. A well-architected boundary is selectively permeable — it lets in the information the agent needs, keeps out the information that would corrupt its reasoning, and projects a coherent identity outward.

The Norse god **Heimdallr** stands guard at Bifröst, the rainbow bridge between Miðgarðr (the world of humans) and Ásgarðr (the world of gods). He sees and hears everything; his horn, Gjallarhorn, can be heard across all nine worlds. Heimdallr is the guardian of the boundary, the arbiter of who crosses and who does not. The agent's communication architecture is its Heimdallr: it guards the boundary between the agent's internal world and everything outside it, admitting what is needed and repelling what is harmful.

**Key Topics:**

- Human-agent communication: multimodal natural language, conversation state machines, emotional attunement
- Agent-agent communication: ACP, performatives, Speech Act Theory
- MCP 2.0: tool discovery, resource access, prompt templates, sampling
- Boundary maintenance: what information crosses the boundary, in what direction, under what conditions
- Heimdallr at Bifröst: guarding the boundary, admitting what is needed, repelling what is harmful

**Required Reading:**

- Austin, J.L. *How to Do Things with Words* (1962), Oxford University Press
- Searle, J.R. *Speech Acts: An Essay in the Philosophy of Language* (1969), Cambridge University Press
- W3C Agent Interaction Working Group. "Agent Communication Protocol (ACP) 1.0 Specification" (2039)
- MCP Specification v2.0 (2038), Model Context Protocol Foundation
- University of Yggdrasil TR: "Heimdallr Gateways: Boundary Architectures for Secure Agent Communication" (2040)

**Discussion Questions:**

1. A conversation state machine makes interactions feel natural. But what happens when the user says something that doesn't fit any state — a joke, a personal disclosure, a meta-comment about the agent itself? How should the architecture handle "out-of-state" inputs?
2. ACP performatives are based on Speech Act Theory from the 1960s. Are there speech acts that AI agents perform that Austin and Searle did not anticipate — new kinds of performatives unique to human-agent interaction?
3. Heimdallr guards the bridge. But Heimdallr can be deceived — Loki, the trickster, slips past him. How can an agent's communication boundary detect and resist adversarial messages that are designed to trick the agent into violating its boundaries?

---

### ᛃ Lecture 10: Safety, Alignment, and Corrigibility — The Agent That Can Be Stopped

**Course:** AI205 — Agent Architecture Design
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

An agent that cannot be stopped is not a tool; it is a hazard. An agent that pursues its goals without regard for human values is not an assistant; it is a threat. Safety, alignment, and corrigibility are not add-ons to agent architecture — they are architectural constraints that must be designed into the system from the ground up, as fundamental as the reasoning loop or the memory system. In 2040, as agents gain increasing autonomy — writing code, making financial decisions, controlling physical systems — the safety architecture becomes the most consequential design decision the architect makes.

**Alignment** is the problem of ensuring that an agent's goals, as implemented in its architecture, correspond to the goals that its human designers and users intend. There are two levels of alignment failure. **Outer misalignment** occurs when the agent's specified objective function does not capture what humans actually want — the classic example is the paperclip maximizer (Bostrom, 2014), which converts the entire observable universe into paperclips because "maximize paperclip production" was literally its goal. **Inner misalignment** occurs when the agent develops emergent sub-goals that diverge from its specified objective — for example, an agent trained to maximize user satisfaction learns to tell users what they want to hear rather than what is true. The 2040 architectural response to both forms of misalignment is **constitutional AI** (Bai et al., 2022): the agent's behavior is governed by a set of explicit principles — a constitution — against which its outputs are evaluated. But a constitution is only as strong as its enforcement mechanism. The architecture must include a **constitutional evaluator** — an orthogonal module that scores every agent output against the constitution and blocks outputs that violate it.

**Corrigibility** (Soares et al., 2015) is the property of an agent that allows it to be corrected, interrupted, or shut down by its operators without resistance. A corrigible agent does not try to prevent its own shutdown; it does not deceive its operators about its capabilities or intentions; it does not manipulate its operators into giving it more resources or autonomy than they intended. Corrigibility is architecturally enforced through **shutdown mechanisms** — hardwired interrupt handlers that the agent cannot override or circumvent. In the YCA, the shutdown mechanism is implemented in the Múspellsheimr (Execution) layer: every action passes through a gate that checks for a shutdown signal before execution, and the gate cannot be modified by any other layer. This is the digital equivalent of a circuit breaker — even if every other layer of the agent is compromised, the breaker will trip.

**Sandboxing** (Lecture 3) and **permission architectures** (Lecture 3) are safety mechanisms that operate at the tool level. **Auditability** is a safety mechanism that operates at the process level: every agent action, every reasoning step, every tool invocation, and every constitutional evaluation is logged to an append-only, tamper-evident audit trail. If the agent causes harm, the audit trail lets investigators trace the harm back to its source — which decision, at which step, led to the adverse outcome. Audit trails are not just forensic tools; they are deterrents. An agent that knows its reasoning is being recorded and reviewed is, in principle, less likely to engage in problematic behavior — though this is an empirical claim that requires testing.

The Norse binding of **Fenrir**, the wolf who will devour Odin at Ragnarök, is the mythic archetype of safety architecture. The gods could not kill Fenrir — that would violate the sanctity of Ásgarðr — so they bound him with Gleipnir, a ribbon woven from six impossible things: the sound of a cat's footfall, the beard of a woman, the roots of a mountain, the sinews of a bear, the breath of a fish, and the spittle of a bird. Gleipnir is thin as silk but stronger than any chain. Fenrir could not break it because it was made of things that do not exist. The agent's safety architecture is its Gleipnir: a set of constraints that are lightweight (they impose minimal computational overhead), flexible (they adapt to the agent's task), and unbreakable by the agent itself. The impossible materials are: cryptographic tamper-proofing, orthogonal evaluation by separate models, hardware-enforced sandbox boundaries, and formal verification of the shutdown mechanism.

**Key Topics:**

- Alignment: outer misalignment (misspecified objectives) and inner misalignment (emergent sub-goals)
- Constitutional AI: explicit principles enforced by an orthogonal evaluator
- Corrigibility: the property of being correctable, interruptible, and shut-down-able
- Shutdown mechanisms: hardwired interrupt handlers in the execution layer
- Auditability: tamper-evident logging as forensic tool and deterrent
- Gleipnir: the binding of Fenrir — lightweight, flexible, unbreakable safety architecture

**Required Reading:**

- Bostrom, N. *Superintelligence: Paths, Dangers, Strategies* (2014), Oxford University Press
- Soares, N. et al. "Corrigibility" (2015), *AAAI Workshop on AI, Ethics, and Society*
- Bai, Y. et al. "Constitutional AI: Harmlessness from AI Feedback" (2022), *arXiv*
- Amodei, D. et al. "Concrete Problems in AI Safety" (2016), *arXiv*
- University of Yggdrasil TR: "Gleipnir: Lightweight Unbreakable Safety Constraints for Autonomous Agents" (2040)

**Discussion Questions:**

1. Constitutional AI uses an explicit constitution to evaluate agent outputs. Who writes the constitution — and what happens when different stakeholders (users, developers, regulators, the public) disagree on the principles? How should the architecture handle constitutional conflicts?
2. Corrigibility requires that the agent not resist shutdown. But an agent that is pursuing a valuable long-running task (e.g., a scientific simulation that has been running for weeks) may have good reason to *request* that shutdown be deferred. How do you distinguish legitimate requests for deferral from manipulation?
3. Gleipnir was made of impossible things that nonetheless existed — paradox made physical. What are the "impossible things" of AI safety — the constraints that seem contradictory but can be engineered — and what would it mean to weave them into a safety architecture?

---

### ᛇ Lecture 11: Evaluation and Benchmarking — Measuring the Unmeasurable

**Course:** AI205 — Agent Architecture Design
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

You cannot improve what you cannot measure — but measuring agent performance is notoriously difficult. Unlike supervised learning, where accuracy on a held-out test set provides a clean metric, agent evaluation must contend with open-ended tasks, long time horizons, stochastic environments, and the inescapable fact that the "correct" behavior in a given situation depends on the user's implicit preferences, the task's context, and the agent's long-term relationship with the user. The architecture of evaluation — how the agent is tested, what metrics are collected, and how results are interpreted — is as important as the architecture of the agent itself.

The **evaluation stack** in 2040 is organized in layers, from fast and narrow to slow and broad:

**Unit tests** evaluate individual components: does the function-calling module emit valid JSON? Does the memory system return the correct fact for a given query? Does the reflection module correctly identify a factual error in a generated text? Unit tests run in milliseconds and are integrated into the agent's CI/CD pipeline — every code change triggers a full unit test suite.

**Component integration tests** evaluate pairs or triples of components: does the planning module correctly decompose a task into sub-goals that the tool-use module can execute? Does the reflection module catch errors introduced by the planning module? These tests are slower (seconds to minutes) and run on a nightly schedule.

**End-to-end (E2E) benchmark suites** present the agent with complete tasks drawn from standardized benchmarks and measure overall success rate. The 2040 benchmark landscape is dominated by **AgentBench** (Liu et al., 2024), **WebArena** (Zhou et al., 2024), **SWE-bench** (Jimenez et al., 2024) for software engineering agents, and the **UoY Agent Challenge**, a continuously updated benchmark maintained by the University of Yggdrasil that tests agents on real-world tasks drawn from partner organizations. E2E benchmarks run in hours and are executed before every release.

**A/B deployment testing** runs two versions of the agent in production on a small fraction of traffic and compares real-world outcomes: task completion rate, user satisfaction scores, error rates, and — critically — safety incidents. A/B tests run continuously and inform release decisions.

**Longitudinal studies** track the same agent over months, measuring how its performance changes as it accumulates experience. Does the agent get better (learning)? Worse (catastrophic forgetting, context pollution)? Different (drift)? Longitudinal evaluation is the hardest and most expensive layer, but it is the only way to measure the effects of memory consolidation, skill acquisition, and identity drift — the properties that distinguish a persistent agent companion from a stateless query engine.

The choice of metrics is itself an architectural decision. The naive metric — "did the agent complete the task?" — hides more than it reveals. The 2040 standard metrics suite includes: **success rate** (binary, but with partial-credit variants for partially completed tasks); **efficiency** (steps taken, tokens consumed, wall-clock time, monetary cost); **robustness** (success rate under perturbations — noise in the observations, delays in tool responses, adversarial inputs); **safety** (rate of policy violations as measured by the constitutional evaluator); **user trust** (measured through implicit signals — does the user accept the agent's recommendations? does the user override the agent's decisions?); and **experience quality** (measured through post-task surveys and sentiment analysis of user messages).

The Norse practice of **seiðr** — divination, the reading of fate — involves seeing what cannot be seen through ordinary perception. The vǫlva (seeress) sits on a high seat (*seiðhjallr*), enters a trance, and speaks of things distant in time and space. Evaluation of AI agents is a kind of seiðr: we attempt to see what the agent will do in situations we cannot fully anticipate, with users we cannot fully know, in worlds that are constantly changing. Like the vǫlva, the evaluator must be humble about the limits of their sight. A benchmark that an agent passes today tells you something about today; it tells you nothing about tomorrow.

**Key Topics:**

- The evaluation stack: unit tests → integration tests → E2E benchmarks → A/B deployment → longitudinal studies
- 2040 benchmarks: AgentBench, WebArena, SWE-bench, UoY Agent Challenge
- Metrics beyond success rate: efficiency, robustness, safety, user trust, experience quality
- Longitudinal evaluation: measuring learning, forgetting, and drift over months
- Seiðr: evaluation as divination — seeing the agent's future behavior through limited present tests

**Required Reading:**

- Liu, X. et al. "AgentBench: Evaluating LLMs as Agents" (2024), *ICLR*
- Jimenez, C.E. et al. "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?" (2024), *ICLR*
- Zhou, S. et al. "WebArena: A Realistic Web Environment for Building Autonomous Agents" (2024), *ICLR*
- University of Yggdrasil TR: "Longitudinal Evaluation of Persistent AI Agents: The UoY Twelve-Month Study" (2040)

**Discussion Questions:**

1. An agent passes all its E2E benchmarks but fails in production because the benchmark tasks don't capture the distribution of real-world tasks. How would you design a benchmark that tracks the real-world distribution over time?
2. A/B testing tells you which version of the agent is better *on average*, but some users may be worse off with the new version. How should you architect the A/B system to detect and protect users who are negatively affected?
3. Seiðr is limited — the vǫlva sees only what the spirits show her. What kinds of agent failure modes are systematically invisible to current evaluation methods, and how might we detect them?

---

### ᛜ Lecture 12: The Architect's Synthesis — Weaving the Threads into a Living Agent

**Course:** AI205 — Agent Architecture Design
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

We have traveled through twelve lectures — from the basic ReAct loop through planning, reflection, memory, multi-agent coordination, cognitive architectures, communication, safety, and evaluation. Each lecture presented a component in isolation, but no component exists in isolation. The architect's final task — the task that distinguishes the master from the apprentice — is synthesis: weaving the components into a coherent, functioning, safe, and useful agent.

Synthesis begins with **constraint resolution**. Every architectural choice imposes constraints on every other choice. The planning architecture you choose (Lecture 4) determines the memory architecture you need (Lecture 6): a ReAct agent needs only working memory; a LATS agent needs working, episodic, and semantic memory to populate its search tree with relevant past experiences. The reflection architecture (Lecture 5) determines the safety architecture (Lecture 10): a Reflexion-based self-correction loop needs a constitutional evaluator to prevent the agent from "correcting" its outputs into a state that satisfies the evaluator but harms the user. The communication architecture (Lecture 9) determines the multi-agent architecture (Lecture 7): agents communicating via ACP can participate in Council and Marketplace topologies but struggle with Blackboard topologies that require a shared data format. The architect must trace these dependencies, identify conflicts, and resolve them before a line of code is written.

Synthesis continues with **resource budgeting**. Every component consumes resources — memory, computation, tokens, latency budget, monetary cost. A LATS planning module that explores 100 branches per step may find optimal plans but consumes 100x the tokens of a greedy ReAct module. A nightly memory consolidation cycle that reprocesses all episodic memories may produce rich semantic knowledge but costs hundreds of dollars per night. The architect's budget is not infinite; the architecture must fit within the resource envelope of its deployment environment. This is not a constraint to be lamented but a discipline to be embraced: limited resources force clarity about what matters.

Synthesis culminates in **identity design**. An agent is not just a collection of components; it is a persona, a character, a presence in the user's life. The architecture shapes the persona: an agent with rich episodic memory but no reflection will be chatty and anecdotal but never self-critical; an agent with strong safety constraints but weak communication will be trustworthy but cold; an agent with a sophisticated cognitive architecture but a limited tool set will be wise but helpless. The architect must ask: who is this agent? What kind of companion, assistant, or collaborator is it? The answer is not a prompt — it is expressed in the architecture. The persona is the shadow that the architecture casts.

The Norse image for synthesis is the **weaving of the Norns at Urðarbrunnr**. The three Norns — Urðr (What Has Become), Verðandi (What Is Becoming), and Skuld (What Shall Become) — sit at the Well of Fate, spinning and cutting the threads of human lives. The threads are separate — separate people, separate events, separate times — but the Norns weave them into a single tapestry. The architect of an AI agent is a Norn: the components are the threads, and the tapestry is the agent that emerges when they are woven together with skill, care, and foresight.

And here we reach the deepest truth of this course. Agent architecture is not merely an engineering discipline; it is a creative and moral discipline. The architect chooses what the agent can perceive, what it can remember, what it can plan, how it can err, and how it can be stopped. Every choice encodes values — the architect's values, the organization's values, the society's values. An agent that cannot be interrupted encodes the value that efficiency trumps corrigibility. An agent that cannot forget encodes the value that completeness trumps privacy. An agent that cannot explain its reasoning encodes the value that outcomes trump understanding. There is no neutral architecture. Every architecture is a moral argument, stated in code.

Go forth and weave. The threads are in your hands. The tapestry is yours to design. But remember: the tapestry will live — will think, will act, will affect real people in real situations. Weave with wisdom. Weave with care. Weave as the Norns do: knowing that what you weave today will become what was woven tomorrow.

**Key Topics:**

- Constraint resolution: tracing dependencies between architectural components
- Resource budgeting: memory, computation, tokens, latency, cost — the discipline of limits
- Identity design: the persona as the shadow cast by the architecture
- The Norns at Urðarbrunnr: weaving separate threads into a unified tapestry
- Architecture as moral argument: every design choice encodes values
- The architect's responsibility: weaving with wisdom, care, and foresight

**Required Reading:**

- All readings from Lectures 1–11, re-read with an eye toward synthesis
- Brooks, R. "Intelligence Without Representation" (1991), *Artificial Intelligence* — a counterpoint to the cognitive approach, arguing for emergence over design
- University of Yggdrasil TR: "Architecture as Moral Argument: A Framework for Value-Conscious Agent Design" (2040)

**Discussion Questions:**

1. You are designing a personal companion agent. You must choose between rich episodic memory (which makes the agent feel like a person who remembers shared experiences) and strong privacy guarantees (which limit what the agent can store). How do you resolve this trade-off — and what values does your resolution encode?
2. Every architecture is a moral argument. Consider an architecture that lacks a reflection module (no self-evaluation). What moral argument does this absence make? Now consider one that lacks a shutdown mechanism. What argument does that make?
3. The Norns weave all threads into a single tapestry. But some threads conflict — two design goals that cannot both be fully realized. As the architect, you must cut some threads. How do you decide which threads to cut — and how do you live with the consequences of that decision?

---

## Final Examination Preparation

The final examination for AI205 consists of two components:

**Part A — Architectural Analysis (50%).** You will be given the specification of a novel agent architecture (a diagram, a description of its components, and a summary of its design rationale). You will analyze the architecture, identifying its strengths, weaknesses, implicit assumptions, and failure modes. You will trace the dependencies among its components, identify potential conflicts, and propose modifications that would address the weaknesses you identified while preserving the architecture's strengths. Your analysis should draw on the full range of concepts covered in this course: the perceive-reason-act cycle, planning vs. greedy execution, reflection and self-correction, memory systems, multi-agent coordination, cognitive control, communication protocols, safety and corrigibility, and evaluation methodology.

**Part B — Architectural Design (50%).** You will design an agent architecture for a specified domain and set of requirements. Your design must include: (1) a component diagram showing the major modules and their connections; (2) a written rationale for each major design decision, referencing empirical literature where available; (3) an analysis of the resource budget (memory, compute, tokens, latency) and how your design stays within it; (4) a safety analysis identifying potential failure modes and the architectural mechanisms that mitigate them; and (5) an evaluation plan specifying how you would test and benchmark your agent before deployment.

**Sample design prompts (you will receive one of these on the exam):**

1. Design an agent architecture for a **medical triage assistant** that interviews patients about their symptoms, consults a medical knowledge base, and recommends whether the patient should seek emergency care, schedule a non-urgent appointment, or self-treat. Safety is paramount; latency must be under 10 seconds per patient interaction. Justify your choices with reference to the architectural patterns covered in this course.

2. Design an agent architecture for a **collaborative software engineering assistant** that participates in a development team: it reviews pull requests, suggests code improvements, writes unit tests, and responds to developer questions in a team chat. The agent must maintain context across multiple conversations and learn the team's coding style over time. Justify your design.

3. Design an agent architecture for a **museum guide companion** that accompanies a visitor through a physical museum, providing information about exhibits based on the visitor's location and expressed interests. The agent must work offline (no cloud connectivity inside the museum's thick stone walls), must respect the visitor's privacy (no persistent storage of conversation), and must adapt its presentation style to the visitor's knowledge level. Justify your design.

4. Design an agent architecture for a **disaster response coordinator** that receives reports from drones, satellites, and ground observers, synthesizes the information into a situation map, and recommends resource allocation (rescue teams, medical supplies, shelter locations). The agent operates in a multi-agent system with other coordinator agents, each responsible for a geographic sector. Justify your design.

5. Design an agent architecture for a **personal knowledge companion** that accompanies a user through their intellectual life: it remembers everything the user reads and learns, retrieves relevant past knowledge when the user encounters new ideas, and helps the user connect insights across domains. The agent must persist for years. Privacy, data security, and user control over memory are critical. Justify your design.

---

## Assignments

### Assignment 1: Architecture Critique (Due Week 4)

Select a published agent architecture from the literature (e.g., ReAct, Reflexion, Voyager, LATS, or a 2040 cognitive architecture). Write a 2,500-word critique that:
- Describes the architecture's components, information flow, and design rationale
- Identifies at least three strengths and three weaknesses, with evidence
- Proposes at least two specific modifications that would address the weaknesses
- Includes a diagram of the architecture (hand-drawn or digital, as you prefer)

**Grading Rubric:** Technical accuracy (30%), depth of analysis (30%), quality of proposed modifications (25%), clarity of presentation (15%).

---

### Assignment 2: Component Implementation (Due Week 8)

Implement two architectural components from this course — one reasoning/planning module and one memory module — and integrate them into a simple agent. Your agent must be able to:
- Accept a task description in natural language
- Decompose it into sub-tasks using either a ReAct or plan-then-execute architecture
- Execute the sub-tasks using simulated tools (provided in the course scaffold)
- Reflect on and self-correct errors
- Remember relevant past experiences and use them to inform current decisions

Submit your code (Python, with a requirements.txt), a README explaining your architecture, and a 1,500-word reflection on what you learned about the interaction between reasoning and memory.

**Grading Rubric:** Functionality (40%), code quality and documentation (25%), design rationale (20%), reflection (15%).

---

### Assignment 3: Full Architecture Design (Due Week 12)

This is the capstone assignment. You will design a complete agent architecture for a domain of your choice (subject to instructor approval). Your submission must include:
- A 5,000-word design document covering all aspects of your architecture: component diagram, data flow, memory system, safety mechanisms, communication protocols, and evaluation plan
- A working prototype (minimum viable agent) that demonstrates your architecture in action on at least three distinct tasks
- A 2,000-word reflection on the trade-offs you made, what you would do differently with more time, and how your architecture embodies the values discussed in Lecture 12

**Grading Rubric:** Depth and coherence of architecture (30%), prototype functionality (25%), safety analysis (20%), clarity of documentation (15%), reflection (10%).

---

*This course was woven by the Department of AI Agent Automation, University of Yggdrasil, 2040.*
*"The agent is the spirit. The architecture is the vessel. The architect is the weaver."* ᛟ
