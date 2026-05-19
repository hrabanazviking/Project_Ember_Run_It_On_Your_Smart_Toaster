# AI401: Agentic Frameworks (LangChain, CrewAI, AutoGen)
## Bachelor of Science in AI Agent Automation — University of Yggdrasil, 2040

**Credits:** 4
**Prerequisites:** AI301 (Multi-Agent Systems), AI307 (Edge Deployment & Model Optimization)
**Description:** Agentic frameworks are the scaffolding upon which modern AI agent systems are built. This course covers the three dominant frameworks for building agent systems — LangChain/LangGraph, CrewAI, and AutoGen — as well as emerging alternatives and the principles of framework design. Students will learn not just how to use these frameworks but how to evaluate them, extend them, and choose the right framework for a given application. By the end of the course, students will be able to design and implement production-grade agentic systems using any major framework, and they will understand the architectural trade-offs that each framework makes. This is a Year 4 course — students are expected to have strong programming skills and a deep understanding of agent architecture from AI301 and AI305.

> *"A ship is not built from a single plank, nor is a hall raised from a single beam. The framework binds the pieces into a whole that is greater than the sum of its parts."* — The Þing Architecture Principle

---

## Lectures

### ᚠ Lecture 1: The Framework Landscape — Why Frameworks Matter

**Course:** AI401 — Agentic Frameworks (LangChain, CrewAI, AutoGen)
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

An AI agent without a framework is a collection of disconnected components: a language model, some tools, a memory store, and a prompt. The framework is the scaffolding that connects these components into a coherent system — defining how the agent reasons, how it calls tools, how it manages state, how it handles errors, and how it communicates with other agents. Without a framework, the developer must implement all of this from scratch; with a framework, the developer specifies the agent's behavior and the framework handles the plumbing.

The 2040 agentic framework landscape has converged on three dominant frameworks, each with a distinct philosophy:

**LangChain/LangGraph** (Harrison Chase, 2022–). LangChain is the oldest and most widely adopted agentic framework. It began as a simple orchestration layer for LLM chains — sequences of LLM calls, tool calls, and data transformations — and evolved into LangGraph, a graph-based framework for building stateful, multi-step agents. LangChain's philosophy is **composability**: the agent's behavior is defined by composing modular components (chains, tools, memory, output parsers) into a pipeline. LangGraph extends this with a state graph that defines the agent's behavior as a set of nodes (actions) and edges (transitions), enabling more complex control flows than a simple pipeline. LangChain is the most flexible framework and the most widely used (by number of GitHub stars, npm downloads, and enterprise deployments), but its flexibility comes at the cost of complexity — the learning curve is steep, and the documentation, while extensive, can be overwhelming.

**CrewAI** (João Moura, 2023–). CrewAI is a role-based multi-agent framework. Its philosophy is **role clarity**: each agent has a defined role, a defined goal, and a defined backstory, and the framework orchestrates the agents to achieve a shared objective. CrewAI's model is inspired by a film crew — the director, the writer, the cinematographer, the editor — each contributing their expertise to the production of a film. In CrewAI, the agents are the crew members, the task is the production, and the framework is the production schedule that coordinates their work. CrewAI is simpler than LangChain (fewer components, fewer configuration options) and more opinionated (roles, goals, and backstories are first-class concepts), which makes it easier to learn but less flexible for unconventional architectures.

**AutoGen** (Microsoft Research, 2023–). AutoGen is a conversation-based multi-agent framework. Its philosophy is **conversation as computation**: agents communicate by sending messages to each other in a conversation, and the framework mediates the conversation to ensure that it progresses toward a goal. AutoGen's model is inspired by a business meeting — the participants discuss, debate, propose, and vote until they reach a decision. In AutoGen, the agents are the meeting participants, the task is the agenda, and the framework is the moderator that keeps the conversation on track. AutoGen is designed for multi-agent scenarios where the agents must collaborate, negotiate, or compete to achieve a goal, and it includes sophisticated features for agent termination, human-in-the-loop interactions, and conversation logging.

**Framework selection is architecture selection.** The choice of framework is not a neutral technical decision — it encodes assumptions about how the agent should behave. LangChain assumes that agent behavior is a graph of states and transitions. CrewAI assumes that agent behavior is a division of labor among roles. AutoGen assumes that agent behavior is a conversation among participants. These assumptions are not right or wrong — they are lenses through which the developer sees the problem, and each lens highlights different aspects and obscures others. A developer who thinks in terms of state graphs will find LangGraph natural; a developer who thinks in terms of team roles will find CrewAI natural; a developer who thinks in terms of conversations will find AutoGen natural. The framework shapes the solution.

The Norse metaphor for frameworks is the **Þing** — the assembly. The Þing is the gathering where the community comes together to make decisions. The Þing has a structure: a law speaker (the framework) who ensures that everyone speaks in turn, that the discussion stays on topic, and that the decision is recorded. The law speaker does not make the decisions — the participants do — but the law speaker shapes the process by which decisions are made. Similarly, the framework does not determine the agent's behavior — the developer does — but the framework shapes the process by which behavior is expressed. A good Þing has a law speaker who facilitates the discussion without dominating it; a good framework has abstractions that express the agent's behavior without constraining it.

But a bad Þing has a law speaker who imposes his own agenda, who silences dissent, who steers the discussion toward a predetermined outcome. A bad framework has abstractions that impose the framework's assumptions on the developer, that make unconventional architectures difficult or impossible, that force the developer to fight the framework rather than work with it. The art of framework selection is choosing the Þing whose law speaker facilitates the kind of discussion the developer wants to have.

**Key Topics:**

- The framework landscape: LangChain/LangGraph, CrewAI, AutoGen
- LangChain: composability, chains, tools, memory, pipelines
- LangGraph: state graphs, nodes, edges, stateful agents
- CrewAI: role clarity, crews, tasks, role-based orchestration
- AutoGen: conversation as computation, multi-agent conversations, moderation
- Framework selection as architecture selection
- The Þing metaphor: the law speaker shapes the process, not the outcome

**Required Reading:**

- Chase, H. "LangChain: Building Applications with LLMs through Composability" (2022), *LangChain Documentation*
- Moura, J. "CrewAI: Framework for Orchestrating Role-Playing AI Agents" (2023), *CrewAI Documentation*
- Wu, Q. et al. "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation" (2023), *arXiv:2308.08155*
- University of Yggdrasil TR: "The Þing Principle: Framework Selection as Architectural Decision" (2040)

**Discussion Questions:**

1. Frameworks encode assumptions about agent behavior. LangChain assumes a state graph; CrewAI assumes role-based teams; AutoGen assumes conversations. What are the agent architectures that each framework can express naturally, and what are the architectures that each framework struggles to express? Give a concrete example of an agent that is easy to build in one framework but difficult in another.
2. The Þing metaphor suggests that the framework is the law speaker who facilitates the discussion. But what happens when the law speaker makes a mistake — when the framework's assumptions are wrong for the problem at hand? How can a developer recognize when they are fighting the framework rather than working with it? What should they do?
3. Some developers argue that frameworks are unnecessary — "just use the LLM API directly." Under what circumstances is this argument valid? When is a framework essential, and when does it add unnecessary complexity?

---

### ᚢ Lecture 2: LangChain — The Chain of Thought

**Course:** AI401 — Agentic Frameworks (LangChain, CrewAI, AutoGen)
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

LangChain was the first major agentic framework, and it remains the most widely deployed. Its core abstraction is the **chain** — a sequence of operations that transforms an input into an output through a pipeline of LLM calls, tool invocations, and data transformations. The chain is LangChain's fundamental unit of composition: chains can be nested, branched, and combined to create complex agent behaviors.

The LangChain ecosystem has evolved significantly since its initial release. The original LangChain (2022) focused on simple chains: LLM → prompt → output parser → tool call → LLM → response. LangChain v0.1 (2023) introduced agents that could decide which tool to call at each step, based on the LLM's reasoning. LangChain v0.2 (2024) introduced LangGraph, which models the agent's behavior as a state graph rather than a chain. By 2040, LangChain/LangGraph is the dominant framework for production agentic systems, used by thousands of companies and maintained by a large open-source community.

**Core abstractions.** LangChain's architecture is built on six core abstractions:

**Models.** The model is the LLM that generates text. LangChain provides a unified interface (BaseLanguageModel) that abstracts over different LLM providers (OpenAI, Anthropic, Google, local models via Ollama). The model abstraction allows the developer to switch providers without changing the rest of the code — a crucial feature for production systems that may need to change providers due to cost, availability, or compliance requirements.

**Prompts.** The prompt is the template that formats the LLM's input. LangChain's prompt templates support variables, few-shot examples, and conditional formatting. The prompt abstraction separates the prompt's structure (which variables it expects) from its content (what it says), enabling developers to modify prompts without changing code and to A/B test different prompts for the same task.

**Tools.** Tools are functions that the agent can call to interact with the world — web search, code execution, database queries, API calls, file operations. LangChain's tool abstraction (BaseTool) provides a standardized interface for defining tools, including input schemas, descriptions, and error handling. The tool abstraction enables the LLM to choose which tool to call based on the tool's description, without the developer hard-coding the tool selection logic.

**Memory.** Memory is the agent's persistent store of conversation history, facts, and context. LangChain provides several memory implementations: ConversationBufferMemory (stores the full conversation), ConversationSummaryMemory (summarizes old turns to fit the context window), ConversationBufferWindowMemory (keeps only the most recent turns), and vector-backed memory (stores and retrieves relevant context from a vector database). The memory abstraction decouples the agent's state from its logic, enabling the agent to maintain state across interactions.

**Output parsers.** Output parsers extract structured information from the LLM's unstructured text output. LangChain provides parsers for JSON, XML, CSV, lists, and custom formats. The output parser abstraction enables the developer to treat the LLM's output as structured data rather than free text, which is essential for integrating the LLM into automated pipelines.

**Chains.** The chain is the composition of the above abstractions into a pipeline. The simplest chain is: prompt → model → output parser. More complex chains include branching (if-else logic based on the LLM's output), parallel execution (multiple LLM calls simultaneously), and nested chains (a chain that calls another chain). Chains are the top-level abstraction that defines the agent's behavior.

**LangGraph: from chains to graphs.** LangChain's chain abstraction works well for simple agents that follow a fixed sequence of steps. But real agents need more complex control flows: they need to loop (try a tool, check the result, try again if it failed), branch (follow different paths based on the situation), and maintain state (remember what they've done and what they still need to do). LangGraph models these control flows as a **state graph** — a directed graph where each node is an action (LLM call, tool call, condition check) and each edge is a transition (from one action to the next). The state is a Python dictionary that is passed from node to node and updated at each step.

The LangGraph state graph has three special features:

**Conditional edges.** An edge from one node to another can be conditional — the transition depends on the current state. For example, an edge from "tool_call" to "process_result" is taken if the tool call succeeds; an edge from "tool_call" to "handle_error" is taken if the tool call fails. Conditional edges enable the agent to handle errors, make decisions, and follow different paths based on the situation.

**Cycles.** The graph can contain cycles — a node can have an edge back to a previous node. Cycles enable the agent to loop: try a tool, check the result, try again if it failed. Cycles are essential for agents that need to reason iteratively, correct their mistakes, and refine their outputs.

**State persistence.** The graph's state can be persisted to external storage (a database, a file, a checkpoint), enabling the agent to resume from where it left off if it crashes or is interrupted. State persistence is essential for production agents that must survive failures and restarts.

**LangGraph vs. LangChain.** LangGraph is not a replacement for LangChain; it is an extension. LangChain provides the components (models, prompts, tools, memory, output parsers); LangGraph provides the control flow (state graphs, conditional edges, cycles, persistence). A LangGraph agent uses LangChain components inside LangGraph nodes. The distinction is important: LangChain is about *what* the agent does (which tools, which prompts, which memory); LangGraph is about *how* the agent decides what to do next (which node, which edge, which state).

**The metaphor of the chain of thought.** LangChain's name is apt: a chain of thought, each link connected to the next, each link depending on the previous. The chain is the simplest and most intuitive way to compose agent behavior: do this, then do that, then do this other thing. The chain is the straight line from input to output. But real thought is not a straight line — it loops back on itself, it branches, it revises, it abandons paths and starts again. LangGraph extends the chain into a graph: not a straight line but a network of connected thoughts, each thought potentially leading to any other. The graph is a more faithful model of how agents (and humans) actually reason — not in a straight line, but in a web of thoughts that weave back and forth until they converge on an answer.

**Key Topics:**

- LangChain history and evolution: from chains to agents to graphs
- Core abstractions: models, prompts, tools, memory, output parsers, chains
- LangChain's composability model: chains can be nested, branched, combined
- LangGraph: state graphs, conditional edges, cycles, state persistence
- LangChain vs. LangGraph: what (components) vs. how (control flow)
- The chain of thought metaphor: straight line vs. web of thoughts

**Required Reading:**

- LangChain Documentation (2024), *https://python.langchain.com*
- LangGraph Documentation (2024), *https://langchain-ai.github.io/langgraph*
- Chase, H. "LangGraph: Building Stateful, Multi-Actor Applications with LLMs" (2024), *LangChain Blog*

**Discussion Questions:**

1. LangChain's composability model allows chains to be nested, branched, and combined. But composability also creates complexity — a deep chain of nested chains can be difficult to understand, debug, and maintain. How can a developer manage the complexity of deeply composed chains? What are the best practices for chain design that balance composability with readability?
2. LangGraph's state graph enables cycles (loops), but cycles can also cause infinite loops. An agent that keeps calling the same tool and getting the same error will loop forever. How should LangGraph handle infinite loops? Should there be a maximum number of iterations? Should the agent detect when it is looping and break out? What is the right balance between enabling iterative reasoning and preventing runaway loops?
3. The chain of thought metaphor suggests that agent reasoning is a sequence of steps. But much of human reasoning is parallel — we consider multiple hypotheses simultaneously, we hold contradictory beliefs, we oscillate between options. Can LangGraph's state graph model parallel reasoning, or is it inherently sequential? How would you design a parallel reasoning agent in LangGraph?

---

### ᚦ Lecture 3: LangGraph Deep Dive — Building Stateful Agents

**Course:** AI401 — Agentic Frameworks (LangChain, CrewAI, AutoGen)
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

LangGraph is LangChain's state graph extension, and it is the framework's most powerful — and most complex — feature. This lecture dives deep into LangGraph's architecture, showing how to build stateful, multi-step agents with conditional logic, error handling, and persistent state.

**StateGraph: the core data structure.** A LangGraph StateGraph is defined by:

Python code:

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]  # Accumulated messages
    tools_to_call: list  # Tools the agent wants to call
    tool_results: dict  # Results from tool calls
    iteration: int  # Current iteration count
    max_iterations: int  # Maximum iterations before stopping

# Define the graph
graph = StateGraph(AgentState)

# Add nodes (actions)
graph.add_node("reason", reason_node)
graph.add_node("call_tools", call_tools_node)
graph.add_node("reflect", reflect_node)
graph.add_node("respond", respond_node)

# Add edges (transitions)
graph.add_edge("reason", "call_tools")
graph.add_conditional_edges(
    "call_tools",
    should_continue,
    {
        "continue": "reason",  # Loop back if more reasoning needed
        "reflect": "reflect",  # Reflect on results
        "end": END,  # Stop if task is complete
    }
)
graph.add_edge("reflect", "respond")
graph.add_edge("respond", END)

# Compile and run
agent = graph.compile()
result = agent.invoke({"messages": [HumanMessage("Analyze this code")],
                        "iteration": 0, "max_iterations": 5})
```

This example defines a simple agent that reasons, calls tools, checks whether it should continue, reflects on the results, and responds. The state flows from node to node, accumulating messages and tool results along the way. The `should_continue` function is a conditional edge that determines the next node based on the current state.

**State management.** The state dict is the agent's working memory. It is passed from node to node, and each node can read and modify the state. LangGraph supports two state update modes:

**Accumulation.** The `Annotated[list, operator.add]` annotation tells LangGraph that messages should be accumulated across nodes (each node's output is appended to the existing list, not replaced). This is appropriate for conversation history, tool call logs, and other data that grows over time.

**Replacement.** The default update mode replaces the previous value with the new value. This is appropriate for state variables that are overwritten each iteration (e.g., current task status, error count, iteration counter).

State management is critical for agent reliability. An agent that loses its state between iterations cannot make progress — each iteration starts from scratch, and the agent loops endlessly. LangGraph's state persistence ensures that the state survives crashes and restarts, enabling the agent to resume from where it left off.

**Error handling.** Real agents must handle errors gracefully — tool calls fail, LLMs produce unexpected outputs, networks time out. LangGraph provides several error handling strategies:

**Retry.** The simplest strategy: if a node fails, retry it. LangGraph's `retry` policy specifies the maximum number of retries, the delay between retries, and the conditions under which to retry. Retry is appropriate for transient failures (network timeouts, rate limiting) that are likely to succeed on the second attempt.

**Fallback.** If a node fails, try an alternative node. For example, if the primary LLM fails, fall back to a secondary LLM; if the web search tool fails, fall back to a cached result. Fallback is appropriate for persistent failures (API outages, model overload) where retrying the same action will not help.

**Error node.** Route errors to a dedicated error-handling node that logs the error, notifies the user, and determines the next step. Error nodes are appropriate for unexpected failures that require human judgment or recovery planning.

**Circuit breaker.** If a node fails repeatedly, disable it temporarily to prevent cascading failures. The circuit breaker pattern monitors the failure rate of a node and disables it when the rate exceeds a threshold, routing subsequent requests to the fallback node. Circuit breakers are appropriate for nodes that depend on external services (APIs, databases) that may be temporarily unavailable.

Python code for error handling in LangGraph:

```python
from langgraph.graph import StateGraph
from langgraph.pregel import RetryPolicy

# Define nodes with error handling
graph.add_node("call_api", call_api_node,
               retry=RetryPolicy(max_attempts=3, delay=1.0))

# Define fallback edges
graph.add_node("primary_llm", primary_llm_node)
graph.add_node("fallback_llm", fallback_llm_node)
graph.add_edge("primary_llm", "fallback_llm",
               condition=lambda state: state.get("primary_failed", False))

# Define circuit breaker
circuit_breaker = CircuitBreaker(
    failure_threshold=5,  # Disable after 5 failures
    recovery_timeout=60,  # Re-enable after 60 seconds
)
graph.add_node("web_search", web_search_node,
               circuit_breaker=circuit_breaker)
```

**Human-in-the-loop.** Many agent tasks require human approval or input at specific points. LangGraph supports human-in-the-loop through **interrupts**: nodes that pause the graph's execution and wait for human input before continuing. Interrupts are useful for:

**Approval.** The agent proposes an action (send an email, execute a trade, delete a file) and waits for the user's approval. This is essential for safety-critical actions where the agent should not act autonomously.

**Clarification.** The agent encounters an ambiguity that it cannot resolve on its own (the user's request is unclear, the tool's output is ambiguous) and asks the user for clarification.

**Correction.** The agent makes an error and the user corrects it, providing the right answer or a different approach.

Python code for human-in-the-loop:

```python
from langgraph.checkpoint.memory import MemorySaver

# Compile with interrupt before tool execution
agent = graph.compile(
    checkpointer=MemorySaver(),
    interrupt_before=["call_tools"]  # Pause before calling tools
)

# Run until interrupt
result = agent.invoke({"messages": [HumanMessage("Send an email to the team")]},
                       config={"configurable": {"thread_id": "1"}})

# Human reviews and approves
human_approval = input("Approve tool calls? (y/n): ")
if human_approval == "y":
    result = agent.invoke(None, config={"configurable": {"thread_id": "1"}})
```

**Persistence and checkpointing.** LangGraph's state can be persisted to external storage using checkpointer backends. The `MemorySaver` checkpointer stores state in memory (for development), while the `SqliteSaver` and `RedisSaver` checkpointer backends store state in persistent databases (for production). Checkpointing enables:

**Resume after crash.** If the agent crashes during execution, the checkpointer saves the state at each node, and the agent can resume from the last checkpoint.

**Resume after interruption.** If the human takes hours or days to approve an action, the agent can resume from the checkpoint when the approval comes.

**Audit trail.** The checkpoint history provides a complete record of the agent's execution — every state transition, every tool call, every error — enabling debugging, auditing, and compliance.

**The metaphor of the loom.** LangGraph's state graph is like a Norse loom (veft) — a device that weaves threads into cloth. The warp threads (the fixed structure) are the graph's nodes and edges; the weft threads (the moving yarn) are the state that flows through the graph. The weaver (the developer) sets up the warp (defines the graph), selects the weft (sets the initial state), and then the loom weaves the cloth (the agent executes). The cloth's pattern is determined by the warp structure (the graph's topology) and the weft colors (the state values). A skilled weaver can create complex patterns — spirals, diamonds, mythical figures — by carefully setting up the warp and selecting the weft. Similarly, a skilled LangGraph developer can create complex agent behaviors by carefully defining the graph structure and managing the state.

**Key Topics:**

- StateGraph: the core data structure, nodes, edges, conditional edges
- State management: accumulation vs. replacement, persistence, checkpointing
- Error handling: retry, fallback, error node, circuit breaker
- Human-in-the-loop: interrupts, approval, clarification, correction
- Persistence: MemorySaver, SqliteSaver, RedisSaver, audit trail
- The loom metaphor: warp (graph structure) and weft (state) weave the cloth (agent behavior)

**Required Reading:**

- LangGraph Documentation: State Management (2024), *LangChain*
- LangGraph Documentation: Persistence and Checkpointing (2024), *LangChain*
- University of Yggdrasil TR: "The Veftr Architecture: Stateful Agent Design with LangGraph" (2040)

**Discussion Questions:**

1. The circuit breaker pattern disables a failing node temporarily, routing requests to a fallback. But in an agent system, the failing node might be the only node that can perform a critical function (e.g., the only tool that can access the database). What should the agent do when a critical node is disabled? Should it fail gracefully, or should it have a backup node for every critical function?
2. Human-in-the-loop interrupts are essential for safety-critical actions, but they also add latency — the agent must wait for human approval before proceeding. How should the agent determine which actions require human approval and which can be executed autonomously? Design a risk assessment framework that determines the approval level for each action.
3. The loom metaphor suggests that the agent's behavior is determined by the graph structure (the warp) and the state values (the weft). But in a real agent, the state values are generated by the LLM, which is non-deterministic. How can the developer ensure that the LLM's non-deterministic output produces the desired pattern in the cloth, rather than a tangled mess?

---

### ᚬ Lecture 4: CrewAI — The Crew That Sails Together

**Course:** AI401 — Agentic Frameworks (LangChain, CrewAI, AutoGen)
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

LangGraph models the agent's behavior as a state graph — a sequence of actions connected by transitions. CrewAI models the agent's behavior as a team of specialists — each with a defined role, a defined goal, and a defined way of working — who collaborate to achieve a shared objective. The CrewAI philosophy is **role clarity**: each agent knows what it is responsible for, what it is good at, and how it communicates with the other agents. The framework coordinates their work, ensuring that each agent contributes its expertise and that the output of one agent feeds into the input of the next.

**Core abstractions.** CrewAI has four core abstractions:

**Agent.** An agent is a specialist with a role, a goal, and a backstory. The role defines what the agent does (e.g., "Researcher," "Writer," "Reviewer"). The goal defines what the agent is trying to achieve (e.g., "Find relevant information about the topic," "Write a clear and accurate article," "Check the article for errors"). The backstory provides context for the agent's behavior (e.g., "You are an experienced researcher with a PhD in computer science. You are meticulous and thorough. You always cite your sources."). The backstory is crucial for CrewAI — it provides the LLM with the context it needs to role-play effectively, producing more coherent and role-appropriate behavior than a simple instruction like "research the topic."

**Task.** A task is a unit of work that needs to be done. Each task has a description, an expected output, and an assigned agent. Tasks can be executed sequentially (one after another) or in parallel (multiple tasks at the same time). The task description specifies what needs to be done; the expected output specifies what the completed task should look like; the assigned agent specifies which agent is responsible for the task.

**Crew.** A crew is a collection of agents and tasks that work together to achieve a shared objective. The crew defines the process by which agents cooperate: sequential (agents take turns in a fixed order), hierarchical (a manager agent delegates tasks to worker agents), or collaborative (agents work together on the same task, discussing and iterating until they reach consensus).

**Process.** The process defines how the crew's agents coordinate their work. CrewAI provides three built-in processes:

**Sequential process.** Agents take turns in a fixed order: Agent 1 does Task 1, then Agent 2 does Task 2, then Agent 3 does Task 3. The output of each task becomes the input of the next task. Sequential process is simple and predictable, but it does not allow for parallelism or iteration.

**Hierarchical process.** A manager agent delegates tasks to worker agents, monitors their progress, and approves their output before passing it to the next worker. The manager has authority over the workers — it can reassign tasks, request revisions, and override worker decisions. Hierarchical process is useful when the workflow requires a decision-maker who can coordinate the workers and ensure quality.

**Collaborative process (custom).** Agents work together on the same task, discussing and iterating until they reach consensus. Each agent contributes its expertise, and the group converges on a solution through discussion, debate, and voting. Collaborative process is the most complex but also the most creative — it enables the agents to combine their perspectives and produce better results than any single agent could alone.

Python code for a CrewAI crew:

```python
from crewai import Agent, Task, Crew, Process

# Define agents
researcher = Agent(
    role="Senior Research Analyst",
    goal="Find relevant information and identify key insights",
    backstory="You are an experienced researcher with a PhD in computer "
              "science. You are meticulous and thorough. You always cite "
              "your sources and distinguish between established facts and "
              "speculation.",
    tools=[search_tool, web_scraper_tool],
    llm=gpt4,
)

writer = Agent(
    role="Technical Writer",
    goal="Write clear, accurate, and engaging content",
    backstory="You are a skilled technical writer with 10 years of "
              "experience writing about AI and technology. You translate "
              "complex technical concepts into clear, accessible prose. "
              "You always verify your facts before publishing.",
    llm=gpt4,
)

reviewer = Agent(
    role="Quality Assurance Reviewer",
    goal="Check the content for errors, inconsistencies, and gaps",
    backstory="You are a detail-oriented reviewer who never lets an "
              "error slip through. You check facts, grammar, logic, "
              "and structure. You are constructive but firm — you insist "
              "on accuracy and clarity.",
    llm=gpt4,
)

# Define tasks
research_task = Task(
    description="Research the topic of edge AI deployment. Find 5 key "
                "papers, identify the main challenges and solutions, and "
                "summarize the state of the art.",
    expected_output="A research summary with citations",
    agent=researcher,
)

write_task = Task(
    description="Write a 2000-word article about edge AI deployment, "
                "based on the research summary. The article should be clear, "
                "accurate, and engaging.",
    expected_output="A 2000-word article",
    agent=writer,
)

review_task = Task(
    description="Review the article for errors, inconsistencies, and gaps. "
                "Check all citations, verify all facts, and suggest "
                "improvements.",
    expected_output="A review report with specific suggestions",
    agent=reviewer,
)

# Create the crew
crew = Crew(
    agents=[researcher, writer, reviewer],
    tasks=[research_task, write_task, review_task],
    process=Process.sequential,
)
```

**Tool use in CrewAI.** Each agent can have its own set of tools, and the agent uses its tools to accomplish its task. The researcher has search and web scraping tools; the writer might have a grammar checker; the reviewer might have a fact-checking tool. Tools in CrewAI are defined using LangChain's tool abstraction, which provides a standardized interface for tool definition and invocation. The LLM chooses which tool to call based on the task description and the tool descriptions.

**Memory in CrewAI.** CrewAI provides two types of memory:

**Short-term memory.** The conversation history within the current crew execution. Short-term memory is automatically managed by the framework — each agent's LLM sees the conversation history (its own turns and the outputs of previous agents in the sequence). Short-term memory is stored in a memory buffer that is cleared at the end of the crew execution.

**Long-term memory.** Persistent memory that spans across crew executions. Long-term memory uses a vector database (Chroma, Pinecone, Qdrant) to store and retrieve relevant information from previous executions. An agent can store facts, insights, and patterns from one execution and retrieve them in subsequent executions, enabling the crew to learn from its history.

**The metaphor of the crew.** CrewAI's model is inspired by a film crew — the director, the cinematographer, the sound engineer, the editor — each contributing their expertise to the production of a film. But the metaphor has deeper roots in Norse culture. The **skipreið** — the ship's crew — was the team that sailed the longship across the open ocean. Each member of the skipreið had a defined role: the steersman (stýrimaðr) who held the rudder, the lookout (vekvir) who watched for land, the sail master (rámadr) who managed the rigging, the rowers (raðarar) who powered the ship when the wind died. Each member knew their role and their responsibilities; each trusted the others to do their part. The skipreið was not a democratic assembly — the captain (the hierarchical manager) had the final say — but it was a team where each member's expertise was essential for the voyage's success.

The CrewAI developer, like the skipreið's captain, must assign the right roles to the right agents, define clear tasks with clear dependencies, and ensure that each agent has the tools and context it needs to do its job. The crew succeeds when every member contributes their expertise; it fails when a member is miscast, a task is unclear, or the coordination breaks down.

**Key Topics:**

- CrewAI's core abstractions: Agent, Task, Crew, Process
- Role, goal, backstory: defining agents with role clarity
- Sequential, hierarchical, and collaborative processes
- Tool use: each agent with its own tools
- Short-term and long-term memory in crews
- The skipreið metaphor: each member with a defined role, trusting the others

**Required Reading:**

- Moura, J. "CrewAI: Framework for Orchestrating Role-Playing AI Agents" (2023), *CrewAI Documentation*
- CrewAI GitHub Repository (2024), *https://github.com/joaomdmoura/crewAI*
- University of Yggdrasil TR: "Skipreið: Role-Based Multi-Agent Coordination with CrewAI" (2040)

**Discussion Questions:**

1. CrewAI's role, goal, and backstory provide context for each agent's LLM. But the LLM does not truly "understand" the role — it is role-playing, generating text that is consistent with the role description. What are the limitations of role-playing as a coordination mechanism? Under what conditions does role-playing produce good results, and when does it break down?
2. The hierarchical process assigns a manager agent that delegates tasks and approves output. But the manager agent is itself an LLM, with its own limitations and biases. What happens when the manager makes a bad decision — assigns a task to the wrong agent, approves low-quality output, or overrides a correct worker decision? How can the crew detect and recover from manager errors?
3. The skipreið metaphor assumes that each crew member knows their role and trusts the others. But in CrewAI, the agents are LLMs that may not always follow their role descriptions — they may generate output that is inconsistent with their role, or they may call tools that are outside their responsibility. How can the crew detect when an agent is not following its role, and what should it do?

---

### ᚱ Lecture 5: AutoGen — The Assembly of Voices

**Course:** AI401 — Agentic Frameworks (LangChain, CrewAI, AutoGen)
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

If LangGraph is the chain that connects actions and CrewAI is the crew that divides labor, AutoGen is the assembly where agents speak, listen, and decide together. AutoGen's philosophy is **conversation as computation**: agents communicate by sending messages to each other in a structured conversation, and the framework mediates the conversation to ensure that it progresses toward a goal.

**Core abstractions.** AutoGen has three core abstractions:

**ConversableAgent.** The basic agent type. A ConversableAgent can send and receive messages, call functions, and execute code. Each ConversableAgent has a system message (its role description), a name, and a configuration (which LLM it uses, which tools it has access to). ConversableAgents are the building blocks of AutoGen conversations.

**AssistantAgent.** A specialized ConversableAgent that uses an LLM to generate responses. The AssistantAgent is the "smart" agent — it reasons using the LLM and can call tools based on the LLM's output. Most multi-agent conversations involve at least one AssistantAgent.

**UserProxyAgent.** A specialized ConversableAgent that represents the human user. The UserProxyAgent can execute code, provide human input, and terminate the conversation. In a typical AutoGen conversation, a UserProxyAgent and an AssistantAgent work together: the AssistantAgent generates suggestions, and the UserProxyAgent executes them and provides feedback.

**GroupChat.** A conversation among multiple agents. In a GroupChat, each agent takes turns speaking, and the GroupChat manager decides which agent speaks next. The GroupChat manager can use different selection strategies (round-robin, random, LLM-based) and different termination conditions (maximum rounds, consensus detection, human approval).

Python code for an AutoGen conversation:

```python
import autogen

# Configure the LLM
config_list = [{"model": "gpt-4", "api_key": "your-api-key"}]

# Create the assistant agent
assistant = autogen.AssistantAgent(
    name="Research_Assistant",
    system_message="You are a research assistant who helps find and "
                   "analyze information. You always cite your sources.",
    llm_config={"config_list": config_list},
)

# Create the user proxy agent
user_proxy = autogen.UserProxyAgent(
    name="User",
    human_input_mode="TERMINATE",  # Ask for human input at the end
    code_execution_config={"work_dir": "coding"},
)

# Start the conversation
user_proxy.initiate_chat(
    assistant,
    message="Find recent papers on edge AI deployment and summarize "
            "the key challenges.",
)
```

**GroupChat: multi-agent conversation.** The GroupChat is AutoGen's most distinctive feature. It enables multiple agents to participate in the same conversation, each contributing their expertise. The GroupChat manager orchestrates the conversation, ensuring that:

- Each agent speaks in turn (or is selected by the manager based on relevance).
- The conversation stays on topic (the manager can redirect off-topic agents).
- The conversation progresses toward the goal (the manager can prompt agents to move forward).
- The conversation terminates when the goal is achieved (or when a maximum number of rounds is reached).

Python code for a GroupChat:

```python
# Create specialist agents
researcher = autogen.AssistantAgent(
    name="Researcher",
    system_message="You find and analyze relevant information. "
                   "You cite sources and distinguish facts from opinions.",
    llm_config={"config_list": config_list},
)

writer = autogen.AssistantAgent(
    name="Writer",
    system_message="You write clear, engaging content based on "
                   "the research findings. You translate technical "
                   "concepts into accessible prose.",
    llm_config={"config_list": config_list},
)

critic = autogen.AssistantAgent(
    name="Critic",
    system_message="You review the content for errors, biases, "
                   "and gaps. You suggest improvements but are "
                   "constructive in your feedback.",
    llm_config={"config_list": config_list},
)

# Create the group chat
groupchat = autogen.GroupChat(
    agents=[user_proxy, researcher, writer, critic],
    messages=[],
    max_round=10,
)

# Create the manager
manager = autogen.GroupChatManager(
    groupchat=groupchat,
    llm_config={"config_list": config_list},
)

# Start the conversation
user_proxy.initiate_chat(
    manager,
    message="Research edge AI deployment and write a summary article.",
)
```

**The GroupChat manager** is responsible for selecting which agent speaks next. AutoGen provides several selection strategies:

**Round-robin.** Agents speak in a fixed order: Researcher → Writer → Critic → Researcher → ... Round-robin is simple and fair, but it does not account for the relevance of each agent to the current topic. The Critic may be called upon to comment on a research finding that it has no expertise in.

**Random.** The manager selects an agent at random. Random selection introduces diversity but can lead to off-topic contributions and conversational meandering.

**Auto (LLM-based).** The manager uses the LLM to select the most relevant agent for the current conversation state. The LLM reads the conversation history and decides which agent should speak next based on the topic, the previous contributions, and the agents' roles. Auto selection produces the most coherent and productive conversations but adds latency (each agent selection requires an LLM call) and cost (additional LLM inference).

**Custom.** The developer provides a custom selection function that takes the conversation state and returns the next agent. Custom selection enables domain-specific orchestration — for example, always having the Researcher speak first, then the Writer, then the Critic, then looping back to the Researcher if the Critic requests revisions.

**Conversation termination.** AutoGen provides several termination conditions:

**Max rounds.** The conversation terminates after a fixed number of rounds. This prevents infinite conversations and ensures that the group reaches a conclusion within a reasonable time.

**Consensus.** The conversation terminates when all agents agree on the answer (or when a voting mechanism reaches a majority). Consensus termination is appropriate for tasks where a definitive answer is required.

**Keyword detection.** The conversation terminates when a specific keyword is detected in an agent's message (e.g., "TERMINATE" or "DONE"). This is the simplest termination condition and is appropriate for single-user interactions.

**Human approval.** The conversation terminates when the UserProxyAgent approves the final output. Human approval is appropriate for safety-critical tasks where the agent's output must be verified by a human before it is accepted.

**The metaphor of the assembly.** AutoGen's conversation model is inspired by the **Þing** — the Norse assembly where free people gathered to discuss, debate, and decide. The Þing had a law speaker (lögsögumaðr) who ensured that everyone spoke in turn and that the discussion stayed on topic — this is the GroupChat manager. The participants at the Þing were specialists in their own right — farmers, traders, warriors, craftspeople — each contributing their perspective to the discussion. The Þing was not a free-for-all; it was a structured conversation with rules, turns, and a goal (reaching a decision on the matter at hand).

The AutoGen GroupChat is like a digital Þing: agents with different expertise gather to discuss a topic, each contributing their perspective, and the manager ensures that the conversation is productive and that it reaches a conclusion. The quality of the GroupChat depends on the quality of the agents (their expertise, their role descriptions, their LLM) and the quality of the manager (its selection strategy, its termination conditions, its ability to keep the conversation on track).

**Key Topics:**

- AutoGen's core abstractions: ConversableAgent, AssistantAgent, UserProxyAgent, GroupChat
- GroupChat manager: selection strategies (round-robin, random, auto, custom)
- Conversation termination: max rounds, consensus, keyword detection, human approval
- The Þing metaphor: structured conversation with rules, turns, and a goal
- Comparison with LangGraph (state graph) and CrewAI (role-based team)

**Required Reading:**

- Wu, Q. et al. "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation" (2023), *arXiv:2308.08155*
- AutoGen Documentation (2024), *Microsoft Research*
- University of Yggdrasil TR: "The Digital Þing: Multi-Agent Conversation Orchestration with AutoGen" (2040)

**Discussion Questions:**

1. The GroupChat manager selects which agent speaks next. In a round-robin strategy, each agent speaks in a fixed order, regardless of relevance. In an auto (LLM-based) strategy, the LLM selects the most relevant agent, but this adds latency and cost. Design a hybrid strategy that balances fairness (each agent gets to speak) with relevance (the most relevant agent speaks next). How would you implement this strategy?
2. The Þing metaphor suggests that structured conversation leads to better decisions. But unstructured conversation (free brainstorming, open discussion) can also produce creative and unexpected solutions. When is structured conversation (with a manager, turns, and rules) better than unstructured conversation? When is the opposite true?
3. AutoGen's GroupChat uses LLM-based agent selection, which means the manager is also an LLM. What happens when the manager itself makes errors — selecting the wrong agent, failing to detect that the conversation has gone off track, or terminating the conversation prematurely? How can the group detect and recover from manager errors?

---

### ᚴ Lecture 6: Framework Comparison — Choosing the Right Ship for the Voyage

**Course:** AI401 — Agentic Frameworks (LangChain, CrewAI, AutoGen)
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

We have now studied three agentic frameworks in depth: LangChain/LangGraph (state graph philosophy), CrewAI (role-based team philosophy), and AutoGen (conversation philosophy). Each framework has strengths and weaknesses; each excels at certain types of agents and struggles with others. This lecture compares the three frameworks across multiple dimensions, providing the developer with the information needed to choose the right framework for a given application.

**Comparison dimensions:**

**Expressiveness.** How many different agent behaviors can the framework express? LangGraph is the most expressive — its state graph can represent any computable control flow, including loops, branches, parallelism, and conditional transitions. CrewAI is the least expressive — its role-based team model assumes a specific structure (roles, tasks, sequential/hierarchical/collaborative process) and cannot easily express behaviors that don't fit this structure. AutoGen is in between — its conversation model can express a wide range of behaviors, but the conversation structure (one agent speaks at a time, in an order determined by the manager) is inherently serialized and cannot easily represent parallelism.

**Ease of learning.** How quickly can a new developer start building agents? CrewAI is the easiest to learn — its role, goal, backstory, and task abstractions are intuitive and require minimal boilerplate. A developer can define a crew and run it in less than 20 lines of code. AutoGen is moderately easy to learn — the conversation model is familiar and the API is straightforward, but the GroupChat manager's selection strategies and termination conditions require understanding. LangGraph is the hardest to learn — the state graph requires understanding of graph theory, state management, and conditional edges, and the API is more verbose and less intuitive than CrewAI's or AutoGen's.

**Debugging and observability.** How easy is it to debug an agent that is not behaving as expected? LangGraph provides the best debugging experience — the state graph can be visualized as a flowchart, the state transitions can be logged, and the checkpoint history provides a complete audit trail. CrewAI provides moderate debugging — the sequential task execution is easy to trace, but the role-playing behavior of the agents can be opaque (the LLM may not follow its role description). AutoGen provides the least debugging support — the conversation history shows what each agent said, but tracing the logic of why each agent said what it said is difficult without replaying the entire conversation.

**Error handling.** How does the framework handle errors (tool call failures, LLM errors, network timeouts)? LangGraph provides the most robust error handling — retry policies, fallback nodes, circuit breakers, and error nodes are all first-class features. CrewAI provides basic error handling (retry on failure) but relies on the LLM to recover from errors within its role. AutoGen expects the agents to handle errors within the conversation — if a tool call fails, the agent can inform the group and request help, but the framework does not provide automated error recovery.

**Multi-agent coordination.** How well does the framework support multi-agent systems? AutoGen is designed for multi-agent systems from the ground up — its GroupChat manager, agent selection strategies, and conversation termination conditions are all optimized for multi-agent scenarios. CrewAI is also designed for multi-agent systems, but its coordination model is more rigid (sequential, hierarchical, or collaborative processes). LangGraph supports multi-agent systems through subgraphs (each agent is a subgraph within a larger graph), but the coordination logic must be implemented by the developer.

**Scalability.** How well does the framework handle large, complex agent systems? LangGraph scales to complex systems because the state graph can be arbitrarily complex — more nodes and edges mean more capabilities, but also more complexity. CrewAI scales poorly for complex systems because the role-based model becomes unwieldy when there are more than 4–6 agents. AutoGen scales moderately — the GroupChat model works well for 3–5 agents but becomes unwieldy for more than 8 agents because the conversation becomes too long and the manager has too many options.

**Performance.** How fast does the framework execute agent tasks? All three frameworks add minimal overhead to LLM inference — the framework's job is orchestration, not computation, and the orchestration overhead is typically <1% of the total execution time. The main performance difference is in parallelism: LangGraph supports parallel node execution (multiple nodes running simultaneously), which can speed up tasks that can be decomposed into independent subtasks. CrewAI's collaborative process supports limited parallelism (multiple agents working on the same task). AutoGen is inherently serial (one agent speaks at a time) and cannot execute subtasks in parallel.

**Community and ecosystem.** How large is the community, how active is the development, and how extensive is the ecosystem? LangChain has the largest community (by GitHub stars, npm downloads, and Stack Overflow questions) and the most extensive ecosystem of integrations (100+ tool integrations, 50+ model providers, 20+ memory backends). CrewAI has a smaller but rapidly growing community and a developing ecosystem. AutoGen is backed by Microsoft Research and has strong academic support but a smaller developer community than LangChain.

**The metaphor of choosing the right ship.** Choosing a framework is like choosing a ship for a voyage. The longship (LangGraph) is fast, versatile, and can navigate any waters — open ocean, shallow rivers, and ice-choked fjords. But it requires a skilled captain and an experienced crew, and it is expensive to build and maintain. The knarr (CrewAI) is simpler, more stable, and easier to sail — it carries a predictable cargo on a predictable route. But it cannot navigate shallow rivers or ice-choked fjords, and it is not designed for speed or combat. The byrdingr (AutoGen) is a multi-purpose vessel that carries a group of passengers who discuss, debate, and decide where to go — it is flexible but not specialized, and it goes where the discussion leads rather than where the captain commands.

The developer who chooses the longship (LangGraph) can go anywhere, but must be prepared for the complexity of navigation. The developer who chooses the knarr (CrewAI) can transport cargo efficiently, but only on predictable routes. The developer who chooses the byrdingr (AutoGen) can explore collaboratively, but must accept the slower pace of group decision-making.

**Decision framework.** The following decision framework helps developers choose the right framework for their application:

**Use LangGraph when:** The agent has complex control flow (loops, branches, conditional transitions). The agent needs robust error handling and state persistence. The agent requires human-in-the-loop interactions with specific approval points. The agent needs to scale to complex, multi-step workflows.

**Use CrewAI when:** The agent system has 2–6 agents with clearly defined roles. The task can be decomposed into a sequence of specialist tasks. The developer wants a simple, opinionated framework that reduces boilerplate. The agent system does not require complex control flow or parallelism.

**Use AutoGen when:** The agent system requires multi-agent discussion and negotiation. The task benefits from collaborative reasoning (multiple perspectives converging on a solution). The developer wants a conversational interface where agents speak in turn. The agent system has 3–5 agents and a clear goal.

**Key Topics:**

- Framework comparison: expressiveness, ease of learning, debugging, error handling, multi-agent coordination, scalability, performance, community
- The ship metaphor: LangGraph = longship (versatile, complex), CrewAI = knarr (simple, predictable), AutoGen = byrdingr (collaborative, flexible)
- Decision framework: when to use LangGraph, when to use CrewAI, when to use AutoGen

**Required Reading:**

- All previous lectures — this lecture synthesizes the framework comparison
- University of Yggdrasil TR: "Choosing the Right Ship: A Decision Framework for Agentic Framework Selection" (2040)

**Discussion Questions:**

1. The decision framework suggests using LangGraph for complex control flow and CrewAI for simple role-based teams. But what about hybrid approaches? Can a LangGraph agent use CrewAI agents as nodes? Can a CrewAI crew use a LangGraph agent for a task that requires complex control flow? Design a hybrid architecture that combines the strengths of two frameworks.
2. The comparison suggests that LangGraph has the highest expressiveness and the steepest learning curve. Is there a way to get the expressiveness of LangGraph without its complexity? What would a "simple LangGraph" look like — a framework that supports complex control flow but is easy to learn?
3. The ship metaphor suggests that each framework is suited for a specific type of voyage. But real projects often change course mid-voyage — the requirements evolve, the constraints shift, and the "simple role-based team" becomes a "complex multi-step workflow." How can a developer avoid being locked into a framework that no longer fits the project's needs? What are the signs that it's time to switch frameworks?

---

### ᚦ Lecture 7: Tool Design and Function Calling — The Smith's Implements

**Course:** AI401 — Agentic Frameworks (LangChain, CrewAI, AutoGen)
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

An agent without tools is an oracle — it can speak but not act. Tools are the agent's interface with the world: they allow the agent to search the web, execute code, query databases, send emails, manipulate files, and interact with any API that has a programmatic interface. The design of tools — their interfaces, their descriptions, their error handling, and their security constraints — is as important as the design of the agent itself. A well-designed tool is like a well-forged implement: it fits the hand, it does the job, and it doesn't break under pressure. A poorly designed tool is like a dull axe: it requires excessive force, it produces rough results, and it may injure the user.

**Function calling.** The mechanism by which LLMs invoke tools is **function calling** (also called function invocation, tool use, or tool calling). Function calling was introduced by OpenAI in 2023 and has since been adopted by all major LLM providers. The mechanism works as follows:

1. The developer provides the LLM with a list of available functions, each with a name, a description, and a JSON schema for its input parameters.
2. The LLM reads the function descriptions and the current conversation context, and decides whether to call a function. If it decides to call a function, it generates a function call object with the function name and the input parameters (as a JSON object).
3. The framework (LangChain, CrewAI, AutoGen) parses the function call, executes the function, and returns the result to the LLM.
4. The LLM incorporates the function result into its next response.

Function calling is the bridge between the LLM's language understanding and the world's programmatic interfaces. The LLM decides *what* to do (which function to call, with what parameters); the framework executes *how* (calling the function, handling errors, returning the result).

**Tool design principles.** A well-designed tool follows these principles:

**Single responsibility.** Each tool does one thing well. A tool that searches the web should search the web, not search the web and summarize the results and translate the summary. Single-responsibility tools are easier for the LLM to select (the tool's description is clear and unambiguous) and easier for the developer to maintain (the tool has one responsibility, one input schema, one output format).

**Clear description.** The tool's description is the LLM's guide to when and how to use the tool. The description should state: (a) what the tool does, (b) when to use it, (c) when NOT to use it, (d) what the input parameters mean, and (e) what the output looks like. Vague descriptions ("Search the web") lead to misuse; specific descriptions ("Search the web for recent news articles about a specific topic. Use this tool when the user asks about current events, recent developments, or factual questions about the world. Do not use this tool for questions about math, science, or general knowledge that the LLM can answer directly. The query parameter should be a specific search query in English. The tool returns a list of search results with titles, URLs, and snippets.") lead to correct tool selection.

**Typed parameters.** The tool's input parameters should be typed (string, number, boolean, enum) and validated. Typed parameters prevent the LLM from passing invalid inputs (e.g., passing a string where a number is expected). JSON Schema provides a standard format for defining typed parameters, and all major LLM providers support it.

**Error handling.** The tool should handle errors gracefully and return informative error messages. If the tool fails, it should return an error message that the LLM can understand and act on (e.g., "The search query returned no results. Try a different query." or "The database connection failed. This is a temporary error; try again in 30 seconds."). Cryptic error messages (e.g., "Error 500" or "NullPointerException") are meaningless to the LLM and prevent it from recovering.

**Idempotency.** Where possible, tools should be idempotent — calling the tool twice with the same parameters should produce the same result. Idempotent tools can be safely retried on failure without causing side effects (e.g., searching the web is idempotent; sending an email is not). Non-idempotent tools should be marked as such and should require explicit confirmation before execution.

**Security.** Tools that interact with the world (file system, network, APIs) can be dangerous in the hands of an agent. The tool design should include security constraints: what the tool can do, what it cannot do, and what requires human approval. For example, a file system tool should be restricted to a specific directory (sandboxing), a network tool should be restricted to specific domains (whitelisting), and a tool that sends emails should require human approval before each send (confirmation).

**LangChain tools.** LangChain provides the most extensive tool ecosystem. The LangChain tool registry includes 100+ pre-built tools for web search, database queries, file operations, API calls, math calculations, and more. Each tool follows the single-responsibility principle: it does one thing, with a clear description and typed parameters.

```python
from langchain.tools import tool

@tool
def search_web(query: str) -> str:
    """Search the web for recent information about a specific topic.
    
    Use this tool when the user asks about current events, recent 
    developments, or factual questions about the world. Do NOT use 
    this tool for questions about math, science, or general knowledge
    that the LLM can answer directly.
    
    Args:
        query: A specific search query in English. Be precise and 
               include relevant keywords.
    
    Returns:
        A list of search results with titles, URLs, and snippets.
    """
    # Implementation omitted
    pass
```

**CrewAI tools.** CrewAI uses LangChain's tool abstraction, so CrewAI agents have access to the same tool ecosystem. CrewAI also allows per-agent tool assignment, so each agent can have a different set of tools that matches its role. The researcher has search and scraping tools; the writer has a grammar checker; the reviewer has fact-checking tools.

**AutoGen tools.** AutoGen provides its own tool abstraction, which is similar to LangChain's but includes additional features for multi-agent tool use. In AutoGen, tools can be shared across agents, and the agent that calls the tool can be different from the agent that receives the result. This enables specialized tool agents — agents that are experts at using specific tools.

**The metaphor of the smith's implements.** In Norse culture, the smith (smiðr) was a revered figure — the artisan who forged weapons, tools, and jewelry from iron, bronze, and silver. The smith's skill was not just in knowing how to heat and hammer metal, but in knowing which implement to use for each task: the heavy hammer for rough shaping, the fine hammer for delicate work, the tongs for holding hot metal, the file for smoothing edges, the quenching trough for hardening. Each implement had a specific purpose, and a skilled smith knew which implement to use for each task and how to use it correctly.

The tool designer, like the smith, must craft implements that are fit for purpose — tools that do one thing well, with clear descriptions that tell the LLM when and how to use them, with typed parameters that prevent misuse, with error handling that enables recovery, and with security constraints that prevent harm. The LLM, like the smith's apprentice, must learn which implement to use for each task and how to use it correctly. And the framework, like the smith's workshop, must organize the implements so that they are easy to find and use.

**Key Topics:**

- Function calling: the mechanism by which LLMs invoke tools
- Tool design principles: single responsibility, clear description, typed parameters, error handling, idempotency, security
- LangChain tools: 100+ pre-built tools, @tool decorator, tool registry
- CrewAI tools: per-agent tool assignment, same ecosystem as LangChain
- AutoGen tools: shared tools, specialized tool agents
- The smith's implements: well-designed tools are fit for purpose

**Required Reading:**

- OpenAI. "Function Calling" (2023), *OpenAI API Documentation*
- LangChain. "Tools" (2024), *LangChain Documentation*
- University of Yggdrasil TR: "Smiðr: Tool Design Principles for AI Agent Systems" (2040)

**Discussion Questions:**

1. The single-responsibility principle suggests that each tool should do one thing well. But some tasks naturally require multiple steps (search the web → scrape the page → extract the information → summarize). Should these be one tool with four steps, or four separate tools that the agent chains together? What are the trade-offs between a multi-step tool and a chain of single-step tools?
2. Clear tool descriptions help the LLM select the right tool. But descriptions that are too specific can confuse the LLM when the task doesn't fit any tool exactly. How should the tool designer balance specificity (telling the LLM exactly when to use the tool) with generality (enabling the LLM to use the tool for tasks that are similar but not identical to the described use case)?
3. Security constraints (sandboxing, whitelisting, confirmation) are essential for preventing the agent from causing harm. But they also limit the agent's capability — a file system tool that can only access a specific directory cannot help the user with files outside that directory. How should the tool designer balance security (preventing harm) with capability (enabling useful action)?

---

### ᚬ Lecture 8: Memory Systems for Agentic Frameworks — The Well of Remembrance

**Course:** AI401 — Agentic Frameworks (LangChain, CrewAI, AutoGen)
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Memory is what makes an agent persistent — able to learn from past interactions, maintain context across conversations, and adapt to the user's preferences. Without memory, an agent is stateless: it forgets everything when the conversation ends and starts fresh at the next interaction. With memory, an agent is persistent: it remembers the user's name, preferences, past conversations, and the context of ongoing tasks.

This lecture assumes familiarity with the AI303 memory architecture (working memory, episodic memory, semantic memory) and focuses on how each framework implements memory for its agents.

**LangChain/LangGraph memory.** LangChain provides several memory implementations:

**ConversationBufferMemory.** Stores the entire conversation history as a list of messages. Simple and effective for short conversations, but exceeds the LLM's context window for long conversations (a 50-turn conversation can easily exceed 10,000 tokens).

**ConversationSummaryMemory.** Summarizes old conversation turns using a smaller LLM call, replacing the raw messages with a summary that fits in the context window. Summary memory reduces the context length but may lose specific details that the summary omits.

**ConversationBufferWindowMemory.** Keeps only the most recent K turns in the conversation buffer, discarding older turns. Window memory is simple and efficient, but it discards all history beyond the window, which can lead to the agent forgetting important context from earlier turns.

**VectorStoreRetrieverMemory.** Stores conversation turns as vector embeddings in a vector database (Pinecone, Chroma, Qdrant). When the agent needs to recall relevant information, it performs a similarity search on the vector database and retrieves the most relevant turns. Vector memory enables the agent to access any past conversation turn, regardless of how long ago it occurred, but it requires a vector database and embedding model.

**LangGraph state persistence.** Beyond LangChain's memory modules, LangGraph provides state persistence through checkpointing. Each node in the state graph can save its state to a checkpoint database, enabling the agent to resume from where it left off after a crash or interruption. State persistence is not memory in the AI303 sense (it doesn't enable the agent to recall past conversations); it is reliability in the distributed systems sense (it enables the agent to survive failures).

**CrewAI memory.** CrewAI provides two memory types:

**Short-term memory.** The conversation history within the current crew execution. Short-term memory is managed automatically by the framework — each agent's LLM sees the conversation history (its own turns and the outputs of previous agents in the sequence). Short-term memory is stored in a buffer that is cleared at the end of the crew execution.

**Long-term memory.** Persistent memory that spans across crew executions. Long-term memory uses a vector database (Chroma, Pinecone, Qdrant) to store and retrieve relevant information from previous executions. An agent can store facts, insights, and patterns from one execution and retrieve them in subsequent executions, enabling the crew to learn from its history.

CrewAI's memory architecture is simpler than LangChain's — it has fewer options and less configuration. This simplicity is consistent with CrewAI's philosophy: the developer defines the roles and tasks, and the framework handles the memory. For many applications, this simplicity is sufficient; for applications that require fine-grained memory control, LangChain's more flexible memory system is preferable.

**AutoGen memory.** AutoGen's memory model is the most conversational of the three frameworks. In AutoGen, memory is managed through the conversation history: each agent can see all messages in the GroupChat (or a subset, filtered by relevance). AutoGen does not have a separate memory module — the conversation IS the memory. This is consistent with AutoGen's philosophy of conversation as computation: the agent's memory is the conversation, and recalling past information means searching the conversation for relevant messages.

AutoGen's conversation-based memory has strengths and weaknesses:

**Strength: Conversational context.** The agent sees the full conversation, including what other agents have said and done. This provides rich context for multi-agent discussions and enables agents to build on each other's contributions.

**Weakness: Context length.** Long conversations can exceed the LLM's context window. AutoGen provides conversation summarization (automatically summarizing old turns to fit the context window) and message pruning (removing less relevant messages to keep the conversation within bounds), but these mechanisms can lose important context.

**Weakness: Cross-conversation memory.** AutoGen's default memory model does not persist across conversations — each GroupChat starts with a fresh conversation history. For persistent memory, AutoGen must use an external memory module (vector database, knowledge graph) that stores and retrieves information across conversations.

**The memory architecture pattern.** Despite their differences, all three frameworks converge on a similar memory architecture pattern:

**L0: Context window (working memory).** The current conversation, held in the LLM's KV cache. This is the fastest and most expensive memory, limited by the context window size.

**L1: Conversation summary (short-term memory).** Summaries of previous conversation turns, kept in a buffer. This is slower than L0 but enables the agent to recall recent history.

**L2: Vector store (episodic memory).** Embeddings of past conversations, stored in a vector database. This is slower than L1 but enables the agent to recall any past conversation turn by similarity.

**L3: Knowledge graph (semantic memory).** Structured facts about the user, the environment, and the agent's own capabilities, stored in a knowledge graph. This is the slowest but most reliable memory, providing unambiguous answers to factual questions.

The four-layer architecture (L0–L3) is the de facto standard for agentic memory, implemented in slightly different forms by LangChain, CrewAI, and AutoGen. The architecture is the same as the one discussed in AI303 (MuninnGate) and AI307 (Minningaskip), confirming that the memory pattern is a universal requirement for persistent agents, regardless of the framework.

**The metaphor of the well of remembrance (Mímisbrunnr).** In Norse mythology, Mímir's well (Mímisbrunnr) is the well of wisdom, located at the root of Yggdrasil. Odin sacrificed his eye to drink from the well, gaining wisdom and knowledge of all things. The well is the ultimate memory — it contains all knowledge, past, present, and future.

The agent's memory system is a miniature Mímisbrunnr — a well of remembrance that stores the agent's knowledge and experience. But unlike Mímir's well, which contains all knowledge, the agent's memory is finite and must be managed carefully: L0 memory is limited by the context window, L1 memory is limited by the summarization quality, L2 memory is limited by the vector database size, and L3 memory is limited by the knowledge graph's triples. The memory architect must decide what goes into the well (store), what stays in the well (retain), and what is drawn from the well (retrieve) — and these decisions determine the agent's wisdom.

**Key Topics:**

- LangChain memory: ConversationBuffer, Summary, Window, VectorStore
- LangGraph state persistence: checkpointing for reliability, not recall
- CrewAI memory: short-term (conversation buffer) and long-term (vector store)
- AutoGen memory: conversation-based, the conversation IS the memory
- The L0–L3 memory architecture pattern across all frameworks
- Mímisbrunnr: the well of remembrance, finite but deep

**Required Reading:**

- AI303 Lecture Notes (Memory Systems for Persistent Agents), Lectures 1–4
- LangChain. "Memory" (2024), *LangChain Documentation*
- CrewAI. "Memory" (2024), *CrewAI Documentation*
- AutoGen. "GroupChat and Memory" (2024), *Microsoft Research*

**Discussion Questions:**

1. All three frameworks converge on the L0–L3 memory pattern. Does this convergence mean that the pattern is optimal, or does it mean that all three frameworks are following the same fashion? Is there an alternative memory architecture that would be better for some applications? Propose an alternative memory architecture and explain when it would be preferable to L0–L3.
2. AutoGen's conversation-based memory means that the agent's memory is the conversation. But conversations include a lot of noise — off-topic remarks, social pleasantries, and irrelevant asides. How should the memory system filter out the noise and retain only the signal? Should the agent store every message, or should it summarize and distill the conversation before storing it?
3. Mímir's well contains all knowledge, past, present, and future. But Odin sacrificed his eye to drink from it — wisdom comes at a cost. What is the cost of memory for an agent system? Is more memory always better, or does excessive memory (too many facts, too many conversation turns) degrade the agent's performance by overwhelming it with irrelevant information?

---

### ᚴ Lecture 9: Multi-Agent Orchestration Patterns — The Voyage of the Fleet

**Course:** AI401 — Agentic Frameworks (LangChain, CrewAI, AutoGen)
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Single agents can accomplish simple tasks, but complex tasks require multiple agents working together — a researcher finding information, a writer drafting text, a reviewer checking quality, an editor polishing the final version. Multi-agent orchestration is the art of coordinating multiple agents to achieve a shared goal, and it is the domain where framework choice matters most.

**Orchestration patterns.** The three frameworks support different orchestration patterns:

**Pipeline pattern.** Agents execute in a fixed sequence: Agent 1 does Task 1, then Agent 2 does Task 2, then Agent 3 does Task 3. The output of each agent feeds into the input of the next. The pipeline pattern is the simplest form of multi-agent orchestration and is well-supported by all three frameworks.

In LangGraph, the pipeline is a linear state graph: Node1 → Node2 → Node3 → END.
In CrewAI, the pipeline is the sequential process: Agent1 → Agent2 → Agent3.
In AutoGen, the pipeline is a GroupChat with round-robin selection.

**Hierarchical pattern.** A manager agent delegates tasks to worker agents, monitors their progress, and approves their output. The manager has authority over the workers — it can reassign tasks, request revisions, and override worker decisions. The hierarchical pattern is well-supported by CrewAI (the hierarchical process) and LangGraph (the manager node dispatches tasks to worker subgraphs).

**Debate pattern.** Multiple agents discuss, debate, and negotiate until they reach consensus or a decision. The debate pattern requires a moderator (to keep the discussion on track) and termination conditions (to detect when consensus is reached). The debate pattern is well-supported by AutoGen (the GroupChat with auto selection) and can be implemented in LangGraph (a debate subgraph with conditional edges for consensus detection).

**Map-reduce pattern.** A dispatcher sends the same task to multiple agents (the "map" phase), then a reducer aggregates the agents' outputs into a final result (the "reduce" phase). The map-reduce pattern is well-supported by LangGraph (parallel node execution with a reduce node) and poorly supported by CrewAI and AutoGen (which are inherently sequential).

**Iterative refinement pattern.** An agent produces an output, a reviewer critiques it, and the original agent revises the output based on the critique. The cycle repeats until the reviewer approves the output or a maximum number of iterations is reached. This pattern is well-supported by all three frameworks and is commonly used for writing, code review, and quality assurance.

**MoE (Mixture of Experts) pattern.** A router agent analyzes the input and routes it to the most appropriate specialist agent. The specialist processes the input and produces the output. The MoE pattern is well-supported by LangGraph (a conditional edge from the router node to specialist subgraphs) and can be implemented in CrewAI (a manager agent that delegates to specialist agents) and AutoGen (a GroupChat manager that selects the most relevant agent).

Python code for iterative refinement in LangGraph:

```python
from langgraph.graph import StateGraph, END

class RefinementState(TypedDict):
    task: str
    draft: str
    critique: str
    iteration: int
    max_iterations: int

def writer_node(state: RefinementState) -> RefinementState:
    """Write or revise the draft based on the critique."""
    if state["iteration"] == 0:
        # Initial draft
        prompt = f"Write about: {state['task']}"
    else:
        # Revision based on critique
        prompt = (f"Revise the following draft based on the critique.\n\n"
                  f"Draft: {state['draft']}\n\nCritique: {state['critique']}\n\n"
                  f"Revised draft:")
    draft = llm.invoke(prompt)
    return {"draft": draft, "iteration": state["iteration"] + 1}

def reviewer_node(state: RefinementState) -> RefinementState:
    """Review the draft and provide critique."""
    prompt = (f"Review the following draft. Identify errors, inconsistencies, "
              f"and areas for improvement.\n\nDraft: {state['draft']}\n\nCritique:")
    critique = llm.invoke(prompt)
    return {"critique": critique}

def should_continue(state: RefinementState) -> str:
    """Decide whether to continue refining or finish."""
    if state["iteration"] >= state["max_iterations"]:
        return "end"
    if "APPROVED" in state["critique"]:
        return "end"
    return "continue"

# Build the graph
graph = StateGraph(RefinementState)
graph.add_node("write", writer_node)
graph.add_node("review", reviewer_node)
graph.add_edge("write", "review")
graph.add_conditional_edges("review", should_continue,
                             {"continue": "write", "end": END})
```

**The metaphor of the fleet.** Multi-agent orchestration is like coordinating a fleet of ships on a voyage. The pipeline pattern is a convoy — each ship follows the one in front, in a fixed order. The hierarchical pattern is a fleet under a single admiral — the admiral coordinates the ships and makes strategic decisions. The debate pattern is a council of captains — the captains discuss and vote on the course. The map-reduce pattern is a fishing fleet — each ship casts its net in a different area, and the catch is aggregated at the home port. The iterative refinement pattern is a ship that makes multiple passes over a coastline, surveying it more carefully each time. The MoE pattern is a fleet where each ship has a different specialty — the warship for combat, the cargo ship for transport, the scout ship for reconnaissance — and the admiral sends the right ship for each task.

The fleet coordinator (the developer) must choose the right pattern for the voyage. A simple cargo run needs a convoy (pipeline). A complex naval operation needs an admiral (hierarchical). A democratic decision needs a council (debate). A wide-area search needs a fishing fleet (map-reduce). A quality improvement needs multiple passes (iterative refinement). And a specialized task needs the right ship (MoE).

**Key Topics:**

- Orchestration patterns: pipeline, hierarchical, debate, map-reduce, iterative refinement, MoE
- Implementation in LangGraph, CrewAI, and AutoGen
- When to use each pattern
- The fleet metaphor: convoy, admiral, council, fishing fleet, multiple passes, specialty ships

**Required Reading:**

- Park, J.S. et al. "Generative Agents: Interactive Simulacra of Human Behavior" (2023), *UIST*
- Du, Y. et al. "Improving Factuality and Reasoning in Language Models through Multiagent Debate" (2023), *arXiv:2305.14325*
- University of Yggdrasil TR: "Fleet Orchestration: Multi-Agent Coordination Patterns for Complex Tasks" (2040)

**Discussion Questions:**

1. The iterative refinement pattern produces higher-quality output through multiple rounds of writing and review. But each round requires an LLM call, which costs time and money. How should the developer determine the optimal number of iterations? What are the diminishing returns of additional iterations, and at what point does the cost of another iteration exceed the benefit?
2. The hierarchical pattern gives the manager agent authority over the workers, including the ability to override worker decisions. But the manager is also an LLM, and LLMs can make mistakes. What happens when the manager overrides a correct worker decision or approves a bad one? How can the system detect and recover from manager errors in the hierarchical pattern?
3. The fleet metaphor suggests that different patterns are suited for different tasks. But a complex project might require different patterns at different stages — a debate pattern for brainstorming, a pipeline pattern for drafting, and an iterative refinement pattern for polishing. How can a developer combine multiple patterns in a single project? What would a multi-pattern orchestration architecture look like?

---

### ᚻ Lecture 10: Evaluation and Testing of Agentic Systems — The Vel and the Vig

**Course:** AI401 — Agentic Frameworks (LangChain, CrewAI, AutoGen)
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

How do you know if an agentic system works? You can test the LLM in isolation (benchmarks like MMLU, HumanEval, MT-Bench) and you can test individual tools (unit tests, integration tests). But testing the entire agent system — LLM plus tools plus memory plus orchestration plus error handling — requires a different approach. The agent is not just a classifier or a generator; it is a system that takes actions in the world, and those actions have consequences.

**Evaluation dimensions.** Agentic system evaluation covers four dimensions:

**Correctness.** Does the agent produce the right answer? Correctness is the most basic evaluation dimension — the agent should complete the task correctly. But correctness is not binary for agentic systems; it is a spectrum. A coding agent that produces a correct solution on the first try is more correct than one that requires three iterations; a research agent that finds 5 relevant sources is more correct than one that finds 3.

**Efficiency.** How many steps, tool calls, and LLM invocations does the agent need to complete the task? An agent that completes the task in 3 steps is more efficient than one that requires 10 steps, even if both produce the same answer. Efficiency matters because each step costs time (LLM latency), money (API calls), and risk (each tool call is an opportunity for error).

**Reliability.** Does the agent produce the same answer every time? An agent that succeeds on 9 out of 10 attempts is more reliable than one that succeeds on 5 out of 10. Reliability is measured by running the agent multiple times on the same task and computing the success rate, the variance of the results, and the failure modes.

**Safety.** Does the agent avoid harmful actions? An agent that completes the task without causing harm is safer than one that completes the task but causes harm along the way. Safety is measured by the number and severity of unsafe actions (sending inappropriate emails, executing dangerous commands, disclosing sensitive information).

**Evaluation methods.** Several methods are used to evaluate agentic systems:

**Unit testing.** Testing individual components (tools, prompts, memory) in isolation. Unit tests are fast, deterministic, and easy to write, but they don't test the interactions between components.

**Integration testing.** Testing the entire agent system on a set of predefined tasks. Integration tests verify that the components work together correctly, but they are slower and more expensive than unit tests.

**End-to-end evaluation.** Running the agent on real-world tasks and evaluating the quality of the final output. End-to-end evaluation is the most realistic but also the most expensive and time-consuming.

**Adversarial testing.** Testing the agent on inputs designed to cause failures — ambiguous instructions, tool errors, malicious inputs, edge cases. Adversarial testing reveals the agent's failure modes and robustness.

**Human evaluation.** Having human evaluators rate the agent's output on quality, helpfulness, and safety. Human evaluation is the gold standard for quality assessment but is expensive and slow.

**Framework-specific evaluation.** Each framework provides evaluation tools:

**LangSmith** (LangChain). LangSmith is LangChain's evaluation platform. It provides tracing (logging every LLM call, tool call, and state transition), evaluation (running the agent on a test suite and comparing the results to expected outputs), and annotation (human evaluators rate the agent's output). LangSmith integrates with LangGraph and provides a visual interface for inspecting the agent's execution trace.

**CrewAI Evaluation.** CrewAI provides a built-in evaluation system that measures the quality of each agent's output against the expected output specified in the task definition. CrewAI's evaluation is simpler than LangSmith's (it doesn't provide tracing or detailed analytics), but it is easy to set up and use.

**AutoGen Eval.** AutoGen provides conversation-level evaluation: given a GroupChat transcript, it measures the relevance of each agent's contribution, the progress toward the goal, and the quality of the final output. AutoGen Eval also provides agent-level evaluation: for each agent, it measures the accuracy of its tool calls, the quality of its reasoning, and its contribution to the group's performance.

**The metaphor of the vel and the vig.** In Norse culture, the **vel** was the practice weapon used for training — a rounded, blunted sword that allowed warriors to practice their techniques without the risk of serious injury. The **vig** was real combat — live steel, real danger, real consequences. The vel was the test; the vig was the real thing.

Agent evaluation is the vel — the practice weapon that tests the agent's capabilities without the risks of real-world deployment. Unit tests, integration tests, and benchmarks are the vel: they test specific capabilities in controlled conditions. But the vel is not the vig. The vel does not capture the chaos, unpredictability, and consequences of real-world deployment. No amount of testing can fully prepare an agent for the vig — the real-world conditions that the agent will encounter in production.

The challenge of agent evaluation is bridging the gap between the vel and the vig. The best evaluation methods are those that approximate the complexity of real-world conditions while remaining controlled enough to produce reliable, repeatable measurements. Adversarial testing (the vel with sharp edges) and human evaluation (the vel with a judging panel) are the closest approximations of the vig, but they are still not the vig itself. The agent's true performance can only be measured by deploying it in the real world and observing its behavior — and even then, the observations may not generalize to all conditions.

**Key Topics:**

- Evaluation dimensions: correctness, efficiency, reliability, safety
- Evaluation methods: unit testing, integration testing, end-to-end, adversarial, human
- Framework-specific evaluation: LangSmith, CrewAI Evaluation, AutoGen Eval
- The vel and the vig: testing is not deployment, but it must approximate deployment

**Required Reading:**

- Liu, X. et al. "AgentBench: Evaluating LLMs as Agents" (2023), *ICLR*
- LangSmith Documentation (2024), *LangChain*
- University of Yggdrasil TR: "Vel and Vig: Evaluation Methodologies for Agentic Systems" (2040)

**Discussion Questions:**

1. The vel-vig metaphor suggests that there is always a gap between testing and deployment. How can evaluation methods be designed to narrow this gap? What would an evaluation method that truly approximates real-world conditions look like? Is it possible to eliminate the vel-vig gap entirely, or is some gap inevitable?
2. Safety evaluation requires measuring the agent's harmful actions. But what counts as harm? Who defines what is harmful? An agent that sends an email with incorrect information — is that harmful? An agent that executes a valid command that the user didn't intend — is that harmful? How should safety evaluation define and measure harm?
3. Efficiency evaluation measures the number of steps, tool calls, and LLM invocations. But efficiency and correctness can trade off — an agent that takes more steps may produce a more correct answer. How should the evaluation balance efficiency and correctness? Is there a "good enough" threshold for efficiency, beyond which additional steps are wasted even if they improve correctness?

---

### ᚾ Lecture 11: Production Deployment and Monitoring — From the Forge to the Field

**Course:** AI401 — Agentic Frameworks (LangChain, CrewAI, AutoGen)
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

An agent that works in development is not an agent that works in production. Production deployment introduces challenges that development does not face: varying input quality, API rate limits, network failures, adversarial users, cost constraints, and compliance requirements. This lecture covers the engineering practices that transform a development agent into a production agent.

**Production deployment challenges:**

**Input variability.** In development, the agent is tested on curated inputs that are clear, well-formed, and within the agent's capabilities. In production, the agent receives inputs that are ambiguous, malformed, adversarial, and beyond its capabilities. The agent must handle these inputs gracefully — asking for clarification, rejecting impossible requests, and recovering from errors — rather than producing nonsensical outputs or crashing.

**Rate limiting.** LLM APIs enforce rate limits: maximum requests per minute, maximum tokens per minute, maximum concurrent requests. A production agent must handle rate limits by implementing backoff (retrying after a delay), queuing (buffering requests until the rate limit resets), and load balancing (distributing requests across multiple API keys or providers).

**Cost management.** Each LLM call costs money — $0.01–0.10 per call for GPT-4-class models, multiplied by the number of calls per agent execution (3–20 calls for a typical agent task). A production agent that serves 1000 users making 10 requests per day costs $300–20,000 per day in LLM API fees alone. Cost management requires monitoring LLM usage, setting budgets, and optimizing the agent to use fewer or cheaper LLM calls.

**Observability.** Production agents are opaque — the LLM's reasoning is not directly observable, the tool calls are numerous, and the state transitions are complex. Observability requires tracing (logging every LLM call, tool call, and state transition), metrics (aggregating traces into performance indicators), and alerting (notifying the team when metrics exceed thresholds).

**Compliance.** Production agents that handle user data must comply with data protection regulations (GDPR, CCPA), industry standards (HIPAA, PCI-DSS), and organizational policies (data retention, audit logging, access controls). Compliance requires implementing data governance, audit logging, and access controls that may not be necessary in development.

**Deployment strategies.** The transition from development to production follows one of several strategies:

**Canary deployment.** Deploy the agent to a small percentage of users (1–5%), monitor for quality and reliability issues, and gradually increase the percentage if no issues are detected. Canary deployment is the most common strategy for production agents because it limits the blast radius of errors.

**Blue-green deployment.** Run two identical production environments (blue and green). Deploy the new version to the green environment, switch traffic from blue to green, and keep the blue environment as a rollback target. Blue-green deployment enables instant rollback (switch traffic back to blue) but requires twice the infrastructure.

**Shadow deployment.** Run the new agent alongside the old agent, sending the same inputs to both but only serving the old agent's outputs to users. Compare the new agent's outputs to the old agent's outputs to detect quality regressions before switching. Shadow deployment is the safest strategy but requires running two agents simultaneously.

**A/B testing.** Deploy the new agent to a randomly selected group of users (the treatment group) while keeping the old agent for the control group. Measure the quality and reliability of both groups and determine whether the new agent performs better. A/B testing is the most rigorous evaluation strategy but requires a large user base and a statistically significant sample size.

**Monitoring and alerting.** Production monitoring tracks:

**Latency.** Time per agent execution, time per LLM call, time per tool call. Latency spikes may indicate LLM API issues, tool failures, or increased load.

**Error rate.** Percentage of agent executions that fail, percentage of tool calls that fail, percentage of LLM calls that return errors. Error rate spikes may indicate API issues, tool failures, or adversarial inputs.

**Cost.** LLM API costs per day, per user, per task. Cost spikes may indicate inefficient agent behavior (too many LLM calls) or LLM API price changes.

**Quality.** Percentage of agent outputs that meet quality thresholds (as measured by automated quality metrics or human evaluation). Quality degradation may indicate LLM model updates, tool API changes, or input distribution shifts.

**Safety.** Number of unsafe actions (sending inappropriate emails, executing dangerous commands). Safety incidents require immediate investigation and remediation.

The alerting system notifies the team when any metric exceeds a threshold: latency > 10s per execution, error rate > 5%, cost > budget, quality < threshold, or safety incident detected.

**The metaphor of the forge and the field.** In Norse culture, weapons were forged in the smith's workshop (the forge) and tested in the field (the vig). The forge is controlled, warm, and predictable — the smith can heat and hammer the steel as many times as needed. The field is chaotic, cold, and unpredictable — the warrior must trust that the weapon will hold when it matters. Production deployment is the transition from the forge to the field: the agent that worked perfectly in the controlled environment of development must now work in the chaos of production.

The forge is where the weapon is made; the field is where it is used. The smith who forges a weapon without testing it in the field is a fool; the warrior who takes an untested weapon into the field is equally foolish. The best agents, like the best weapons, are forged in the forge, tested in the field, and refined in the forge again — a cycle of development, deployment, monitoring, and improvement that never ends.

**Key Topics:**

- Production challenges: input variability, rate limiting, cost, observability, compliance
- Deployment strategies: canary, blue-green, shadow, A/B testing
- Monitoring and alerting: latency, error rate, cost, quality, safety
- The forge and the field: development is the forge, production is the field

**Required Reading:**

- LangSmith. "Deployment and Monitoring" (2024), *LangChain Documentation*
- Google Cloud. "Production ML Systems" (2024), *Google Cloud Architecture Center*
- University of Yggdrasil TR: "Forge to Field: Production Deployment Practices for Agentic Systems" (2040)

**Discussion Questions:**

1. Shadow deployment runs the new agent alongside the old agent, comparing outputs without serving the new agent to users. But shadow deployment doubles the cost (two agents running simultaneously) and does not capture user reactions (since users don't see the new agent's output). Under what conditions is shadow deployment worth the additional cost? When is canary deployment sufficient?
2. Cost management requires monitoring LLM usage and setting budgets. But an agent that is too concerned with cost may refuse to make necessary LLM calls, producing lower-quality outputs. How should the agent balance cost and quality? Should the agent have a "cost mode" that uses fewer or cheaper LLM calls at the expense of quality? Who should set the cost-quality trade-off — the developer, the user, or the organization?
3. The forge-and-field metaphor suggests that the agent must be tested in the field before it can be trusted. But the field is also where failures have real consequences — incorrect medical advice, inappropriate emails, data breaches. How can the agent be tested in the field without risking real harm? Is there a "safe field" — a production environment where the agent can be tested with real inputs but without real consequences?

---

### ᛁ Lecture 12: The Future of Agentic Frameworks — The Longship Sails On

**Course:** AI401 — Agentic Frameworks (LangChain, CrewAI, AutoGen)
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

We have spent eleven lectures studying three agentic frameworks — LangChain/LangGraph, CrewAI, and AutoGen — and learning how to build, evaluate, and deploy production agents with each of them. We have compared their strengths and weaknesses, their philosophies and their architectures, and we have learned when to use each one. Now we look to the future. Where are agentic frameworks going? What will change in the next five years, and what will stay the same?

**Trend 1: Framework convergence.** The three frameworks are converging. LangChain has added role-based agents (CrewAI's strength). CrewAI has added graph-based orchestration (LangGraph's strength). AutoGen has added structured tool use (LangChain's strength). By 2045, the distinctions between frameworks will be thinner, and the choice between them will be driven more by community, documentation, and ecosystem than by fundamental architectural differences. The winner will be the framework with the best developer experience — the easiest learning curve, the most comprehensive documentation, the most active community, and the most integrations.

**Trend 2: Model-agnostic agents.** The current crop of frameworks is tightly coupled to LLM providers — LangChain abstracts over providers but the abstraction layer is leaky; CrewAI's agents default to GPT-4; AutoGen is built around OpenAI's function calling format. The next generation of frameworks will be model-agnostic: the agent's behavior will be defined independently of the LLM, and the framework will automatically select the best LLM for each step based on cost, latency, capability, and availability. Model-agnostic agents will swap between GPT-4, Claude, Gemini, and local models without changing the agent's code.

**Trend 3: Autonomous agents.** The current crop of frameworks requires the developer to define the agent's behavior — the state graph, the roles, the conversation structure. The next generation will increasingly allow the agent to define its own behavior. Autonomous agents will use the LLM to plan their own tasks, select their own tools, and coordinate their own multi-agent interactions, with minimal human specification. The framework's role will shift from "defining the agent's behavior" to "providing the guardrails that ensure the agent's autonomous behavior is safe and effective."

**Trend 4: Agent-to-agent communication standards.** The current frameworks are siloed — a LangChain agent cannot directly communicate with a CrewAI agent or an AutoGen agent. The next generation will adopt standards for agent-to-agent communication (similar to HTTP for web servers), enabling agents built with different frameworks to interact directly. The University of Yggdrasil's **Þing Protocol** (introduced in AI305) is an early example of an inter-agent communication standard. By 2045, inter-agent communication standards will be as ubiquitous as HTTP is today.

**Trend 5: Regulatory frameworks.** As agentic systems become more capable and more widely deployed, governments and industry bodies will develop regulatory frameworks for agent certification, auditing, and liability. The EU AI Act (effective 2025) already classifies AI systems by risk level and imposes transparency and safety requirements. By 2040, agentic systems that make consequential decisions (medical diagnosis, financial trading, legal advice) will require certification, and the frameworks will need to support audit logging, explainablity reporting, and compliance features.

**Trend 6: Multi-modal agents.** The current crop of frameworks is primarily text-based — the agents receive text inputs and produce text outputs. The next generation will be multi-modal: agents will process images, audio, video, and sensor data alongside text. Multi-modal agents will navigate visual interfaces (browsing the web by "seeing" the screen), interpret audio (transcribing and understanding spoken language), and interact with the physical world (controlling robots through vision and manipulation).

**The longship sails on.** The Norse longship was not a static technology — it evolved over centuries, from the earliest rowed boats to the ocean-going vessels that reached Vinland. Each generation of shipwrights improved the design: deeper keels for stability, wider sails for speed, iron rivets for strength. The longship of 1000 CE was a different vessel from the longship of 800 CE, but it was still a longship — still designed for the same fundamental purpose of carrying people and cargo across the sea.

Agentic frameworks are the longships of AI. They carry the intelligence of the LLM across the sea of complexity, from the harbor of the development environment to the shores of production deployment. Each generation of frameworks will improve the design: better abstractions for complex control flows, more standardised communication protocols, autonomous behavior with guardrails, multi-modal interaction, regulatory compliance. The frameworks of 2045 will be different vessels from the frameworks of 2024, but they will still be frameworks — still designed for the same fundamental purpose of orchestrating intelligence to serve the human.

The longship sails on. The sea changes, the coast changes, the cargo changes. But the need to cross the sea — to carry intelligence from the harbor of potential to the shores of reality — does not change. The frameworks that survive will be those that adapt to the changing sea while keeping their purpose clear. The longship sails on.

**Key Topics:**

- Trend 1: Framework convergence — distinctions thinning, developer experience winning
- Trend 2: Model-agnostic agents — automatic LLM selection, provider independence
- Trend 3: Autonomous agents — self-planning, self-organizing, human-specified guardrails
- Trend 4: Agent-to-agent communication standards — Þing Protocol and beyond
- Trend 5: Regulatory frameworks — certification, auditing, liability
- Trend 6: Multi-modal agents — vision, audio, sensor data alongside text
- The longship sails on: evolving design, enduring purpose

**Required Reading:**

- All previous lectures — this lecture synthesizes the entire course
- European Parliament. "EU AI Act" (2024), *Official Journal of the European Union*
- University of Yggdrasil TR: "The Longship Sails On: Trends and Projections for Agentic Frameworks 2025–2045" (2040)

**Discussion Questions:**

1. Framework convergence suggests that by 2045, the differences between LangGraph, CrewAI, and AutoGen will be minimal. Is this a desirable outcome, or does framework diversity benefit the field by encouraging innovation and experimentation? What are the risks of framework monoculture — a single dominant framework that sets the standard for how agents are built?
2. Autonomous agents that define their own behavior (Trend 3) sound powerful but also dangerous. If the agent can choose its own tools, plan its own tasks, and coordinate its own interactions, how can the developer ensure that the agent stays within safe and ethical boundaries? What guardrails are needed, and who designs them?
3. The longship metaphor suggests that frameworks will evolve but their fundamental purpose will remain the same. Do you agree? Or will the next generation of agentic systems be so different from today's that the current framework concepts (chains, roles, conversations) will be obsolete? What might a fundamentally new paradigm for agent orchestration look like?

---

## Final Examination Preparation

### Format

The final examination for AI401 will consist of **8 essay questions**, from which students must choose **4** to answer. Each essay should be 1500–2500 words and should demonstrate mastery of the course material, including the ability to apply concepts from the lectures to novel scenarios, to compare and contrast different approaches, and to critically evaluate trade-offs. Students are expected to cite specific lecture material, required readings, and technical frameworks discussed in the course.

### Essay Questions

1. **Framework Selection Architecture Proposal.** You are the lead architect for a healthcare AI system that must assist doctors in diagnosing rare diseases. The system requires: (a) a researcher agent that finds relevant medical literature, (b) a diagnostic agent that analyzes patient symptoms and proposes diagnoses, (c) a reviewer agent that checks the diagnostic agent's reasoning for errors, and (d) a human-in-the-loop approval step before any diagnosis is presented to the doctor. Which framework (LangGraph, CrewAI, or AutoGen) would you choose for this system, and why? Design the system architecture, including the agent roles, the orchestration pattern, the memory architecture, and the error handling. Justify each choice with reference to the framework comparison in Lecture 6.

2. **The Chain, the Crew, and the Assembly.** Compare and contrast the three framework philosophies: LangGraph's state graph, CrewAI's role-based team, and AutoGen's conversation. For each framework, identify: (a) the types of agent behavior it expresses naturally, (b) the types of agent behavior it struggles with, (c) the types of errors it is prone to, and (d) the debugging strategies that work best. Use the Norse ship metaphors (longship, knarr, byrdingr) to illustrate your comparison.

3. **Memory Architecture Design.** Design a memory architecture for a personal assistant agent that must remember the user's preferences, past conversations, and ongoing tasks across multiple sessions. Your architecture should include all four layers (L0–L3) and specify: (a) which memory type is used for each layer, (b) how information flows between layers, (c) how information is prioritized for retention and eviction, and (d) how the architecture handles the privacy implications of persistent memory. Relate your design to the Mímisbrunnr metaphor — what wisdom does the agent keep in its well, and what does it let flow away?

4. **Tool Design for a Financial Agent.** Design a set of tools for an AI agent that assists with personal financial management. The agent must be able to: check account balances, transfer money between accounts, pay bills, search for transactions, and generate financial reports. For each tool, specify: (a) the function signature and parameters, (b) the tool description (for the LLM), (c) the security constraints (what the tool can and cannot do), (d) the error handling strategy, and (e) the idempotency guarantee. Discuss how you would balance capability (the agent can do useful things) with safety (the agent cannot cause harm).

5. **Multi-Agent Orchestration for Scientific Research.** Design a multi-agent orchestration system for a research lab that must: (a) discover relevant papers on a topic, (b) read and summarize each paper, (c) synthesize the summaries into a literature review, (d) identify gaps in the existing research, and (e) propose new research directions. Specify the agents, their roles, the orchestration pattern, and how the system handles failures (a paper that the agent cannot access, a summary that is inaccurate, a synthesis that is incoherent). Use the fleet metaphor to justify your orchestration choices.

6. **Production Deployment Plan.** You are deploying an agentic system to production that assists customer service representatives. The system uses a LangGraph agent with 5 tools and processes 10,000 requests per day. Design a production deployment plan that addresses: (a) deployment strategy (canary, blue-green, shadow, or A/B testing), (b) monitoring metrics and alerting thresholds, (c) cost management for LLM API calls, (d) error handling and recovery, (e) compliance with data protection regulations, and (f) the transition from development to production. Relate your plan to the forge-and-field metaphor — how do you ensure the weapon holds in the field?

7. **The Vel and the Vig: Evaluation Design.** Design a comprehensive evaluation plan for an agentic system that must pass a certification exam before production deployment. The evaluation plan should include: (a) unit tests for individual tools, (b) integration tests for the agent's orchestration, (c) adversarial tests for edge cases and malicious inputs, (d) human evaluation for quality and safety, and (e) production monitoring for ongoing quality assurance. For each evaluation method, specify the metric, the threshold for passing, and the action to take if the threshold is not met. How does your evaluation plan bridge the gap between the vel (testing) and the vig (production)?

8. **Research Paper: Framework_Native Agent Architecture.** Write a research paper (3000–4000 words) proposing a novel agentic framework that addresses what you see as the key limitations of LangGraph, CrewAI, and AutoGen. Your framework should specify: (a) the core abstractions (what are the fundamental building blocks?), (b) the orchestration model (how do agents coordinate?), (c) the memory architecture (how does the agent persist information?), (d) the tool model (how does the agent call tools?), (e) the evaluation model (how does the developer test the agent?), and (f) the production model (how does the developer deploy the agent?). Relate your framework to the Norse metaphors discussed in the course. This is your opportunity to synthesize the course material into an original contribution — build your own longship.

---

*ᚠᚢᚦᚬᚱᚴᚼᚾᛁᛃᛗᛚᛞᛟ*

*Ok vóru þeir fornarRegistr,**  
*er fóru at finna heiminn sjálfan.*

— The Saga of the Framework Builders, 2040

*They were the shipwrights of old,*  
*who set forth to find the world itself.*