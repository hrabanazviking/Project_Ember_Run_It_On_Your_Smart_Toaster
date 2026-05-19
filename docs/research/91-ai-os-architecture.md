# 91 — AI OS Architecture: Kernel, Processes, Memory Hierarchy, Scheduler

**Category:** AI Operating System
**Runa relevance:** kernel design, Hirð orchestration, Heimskringla, memory tiers — *the whole shape of Runa*
**Status:** Synthesis of operating-system theory applied to AI agent runtime. Foundational.
**Last touched:** 2026-05-17

---

## 1. Core idea

An *AI Operating System* (AI OS) is the systems-level abstraction for a long-running, persistent, multi-component AI agent. Where a traditional OS multiplexes hardware among programs, an AI OS multiplexes *cognitive resources* — model inference, retrieval, tool use, memory, attention — among the agent's sub-processes. The framing was popularised by Andrej Karpathy's \"LLM-as-OS-kernel\" talks (2024+), Anthropic's \"Claude as a virtual machine for tasks\" framing, and a wave of academic and industry work positioning LLM agents as more OS-like than application-like.

For Runa, the AI OS framing is the right *master architecture*. She is not a single LLM call wrapped in a chat loop; she is a persistent runtime with multiple coordinated processes, layered memory, scheduled background jobs, capabilities, and resource budgets. This document is the architectural overview — what the components are, how they fit, where the analogies to traditional OS design hold and break. Subsequent docs ([[92-process-scheduling-cognitive]] through [[96-resource-budgets]]) go deeper into specific layers.

## 2. Technical depth

**The traditional OS view (Tanenbaum).**

A classical OS provides:
- *Process abstraction*: programs run in isolation; OS multiplexes CPU.
- *Memory management*: virtual memory, paging, caches.
- *File system*: persistent storage with naming, hierarchy.
- *I/O*: device access mediated by drivers.
- *Inter-process communication*: pipes, sockets, shared memory.
- *Scheduling*: who runs when.
- *Security*: capabilities, permissions, isolation.

**The AI OS map.**

| Traditional OS | AI OS for Runa |
|---|---|
| Processes | Subagents in Hirð (planner, researcher, narrator, ...) |
| CPU scheduling | Token-budget + attention scheduling across subagents |
| Virtual memory | Multi-tier memory: short context, retrieval, long-term store |
| File system | Muninn + identity store + relationship store |
| I/O | Voice, text, future XR / robotic; via adapters |
| IPC | Internal message-passing; MCP-style protocols ([[93-ai-native-ipc-mcp]]) |
| Threads | Concurrent sub-tasks within a subagent |
| Capability tokens | Per-task / per-subagent permissions ([[95-capability-based-security]]) |
| Kernel | Runa's reasoning kernel — the central orchestrator |
| Userland | Plugins, tools, mods, external integrations |
| Boot | The identity-load ritual ([[52-cross-session-persistent-identity]]) |
| Shutdown | Consolidation + sync to durable state |
| Drivers | Adapters for each external system (Pi hardware, OWUI, MCP servers) |

The mapping isn't perfect; some classical OS concepts don't transfer cleanly (e.g. interrupts), and some AI-specific concepts have no OS analogue (e.g. retrieval-augmented context assembly). But the *shape* maps remarkably well.

**The kernel.**

In Runa's case, the *kernel* is the reasoning loop:
- Read input.
- Compose context (boot ritual + retrieval + identity).
- Invoke LLM (one or several models via Heimskringla routing).
- Process output (parse tool calls; emit response).
- Update state (write to Muninn; update Eldhugi).

The kernel is the thinnest layer; it does not contain capabilities; it dispatches.

**Subagents (Hirð).**

Subagents — Runa's *retainers* — are the AI OS analogues of OS processes:
- Each has a clear role (planner, narrator, researcher, consolidator, ...).
- Each has explicit *capabilities* and *resource budgets*.
- Each can be invoked by the kernel or scheduled to run autonomously.
- Each may have its own memory (working state) on top of shared Muninn.

**Memory hierarchy.**

Following [[01-memgpt-os-memory-hierarchies]]:
- *Active context* (cache analogue): what's in the current LLM call.
- *Retrieval index* (RAM analogue): Muninn's queryable store.
- *Cold archive* (disk analogue): rarely-accessed history, archived episodes.

Promotion and demotion between tiers follows the cognitive-economic principle: *what's frequently relevant stays warm; what's not gets pushed deeper*.

**Scheduling.**

Cognitive scheduling has both *foreground* (responding to user) and *background* (consolidation, reflection, autonomous research) modes:
- Foreground: real-time, low-latency, kernel + relevant subagents.
- Background: Draumr ([[57-sleep-dream-replay-consolidation]]), Eir (self-healing), Skald (saga / vision tasks), curiosity retainer.

The scheduler decides what runs when, under what budget. See [[92-process-scheduling-cognitive]].

**IPC and protocols.**

Subagents and external tools communicate via:
- Internal function calls (kernel → subagent).
- Structured message-passing (subagent → subagent).
- MCP — Model Context Protocol — for external tools and services ([[93-ai-native-ipc-mcp]]).

**Capabilities.**

Per-task capability tokens limit what subagents and tools can do. The operator subagent ([[89-computer-use-agents]]) for project X has different permissions than for messaging. The Draumr subagent can write reflections but not delete episodes. See [[95-capability-based-security]].

**Persistence.**

State persists across sessions via:
- Markdown files (identity, relationships, persona).
- SQLite databases (episodes, triplets, reflections).
- JSON / JSONL (logs, journal entries).
- Optional: binary state (model adapters, embeddings).

The *boot ritual* re-inflates working state from this substrate every session.

**Resource budgets.**

Tokens, GPU-seconds, retrieval-calls, tool-calls — all are budgeted per task and per subagent. See [[96-resource-budgets]].

## 3. Key works

- **Tanenbaum, A. S.** *Modern Operating Systems.* Pearson, 4th edition. The classical reference.
- **Karpathy, A.** *LLM as the new operating system kernel.* Talks and posts, 2024+.
- **Packer, C., Wooders, S., Lin, K. et al.** *MemGPT.* arXiv:2310.08560, 2023. The OS-memory-hierarchy analogy made explicit.
- **Sumers, T. R. et al.** *Cognitive Architectures for Language Agents.* arXiv:2309.02427, 2023. The structural specification.
- **Anthropic.** *Building effective agents.* 2024+. Patterns blog series — implicit AI-OS treatment.
- **LangChain, AutoGen, CrewAI, Letta** — production frameworks. Each instantiates AI-OS-like patterns, with varied opinions.
- **Andreas, J.** *Language models, agent models, and world models.* 2023+. Conceptual framing.
- **AAIF (Agent Agent Interaction Framework)** — emerging cross-vendor protocols for agent-OS interoperability.

## 4. Empirical results

This is more *architectural pattern* than *benchmarked result*. The empirical evidence is in production deployments:

- ChatGPT, Claude, Gemini agent platforms successfully run multi-component agents across millions of sessions per day. The architectural patterns work at scale.
- Letta / MemGPT-class deployments show persistent agents handling long-horizon tasks with the OS-style architecture.
- AutoGen, CrewAI, LangGraph deployments show multi-agent orchestration works in production.
- Failure modes: race conditions in concurrent subagents, capability-token leakage, memory-tier corruption — well-known and mitigable.

The lesson: *the OS analogy is engineering-productive*. It surfaces the right concerns (capabilities, scheduling, persistence) at the right abstraction level.

## 5. Applicability to Runa

This document is essentially *Runa's master architecture*. Every other research doc in the corpus maps into a specific layer:

- *Kernel*: [[83-agentic-foundation-models-2025]], [[86-dual-process-cognition-system-1-2]], [[97-test-time-compute-scaling]].
- *Subagents (Hirð)*: [[11-autogen-multi-agent]], [[88-long-horizon-planning-lats-rap]], [[89-computer-use-agents]], [[90-autonomous-research-agents]].
- *Memory hierarchy*: [[01-memgpt-os-memory-hierarchies]], [[51-generative-agent-memory-streams]], [[52-cross-session-persistent-identity]], [[53-autobiographical-memory-architectures]], [[57-sleep-dream-replay-consolidation]].
- *Scheduling*: [[92-process-scheduling-cognitive]].
- *IPC*: [[93-ai-native-ipc-mcp]].
- *Persistence*: [[94-persistent-agent-state]].
- *Capabilities*: [[95-capability-based-security]].
- *Resources*: [[96-resource-budgets]].
- *Identity / boot*: [[52-cross-session-persistent-identity]], [[62-identity-stability-under-change]].

For **implementation phasing**:

Runa's current architecture (per the bootstrap docs) maps onto this. Phase 1 (current): kernel + Muninn + identity store; minimal subagents. Phase 2: more sophisticated subagents, scheduling, capability tokens. Phase 3: full AI OS shape with autonomous background processes, multi-model routing, computer-use, possibly embodiment adapters.

For **modularity and replaceability**:

- Each layer should be replaceable without re-architecting the others. New base model? Heimskringla absorbs the change. New retrieval system? Muninn boundary absorbs. New tool? Plugin system absorbs.
- This is the OS-style virtue: layering for replaceability.

For **observability**:

- Every layer logs. The OS-level logs include process spawning / termination, capability grants, scheduler decisions. Volmarr can see what Runa is doing.

For **per RULES.AI.md compliance**:

- Modular: yes, by design.
- Self-healing: each subagent handles its own failures; the kernel handles subagent failures.
- Cross-platform: yes — the OS abstractions are platform-portable; specific adapters are not.
- No hard-coded paths: data files; cross-platform path conventions.

What to avoid:

- **Treating the AI OS analogy as literal.** It is a *productive analogy*, not a rigid mapping. Some OS concepts don't transfer.
- **Premature complexity.** Implementing all layers at once is overwhelming. Phase carefully; refactor as load reveals which abstractions matter.
- **Tight coupling between layers.** The OS virtue is *separation*. Cross-layer dependencies must go through defined interfaces.
- **Treating subagents as a substitute for kernel reasoning.** They specialise; they don't replace.
- **Forgetting the human in the loop.** Volmarr is not a process in the OS; he is the *user*, the deployment context, the relationship. Engineer accordingly.

## 6. Open questions

- **The right boundary between kernel and subagent.** Where does kernel reasoning stop and Hirð begin? Mostly heuristic.
- **The right number of subagents.** Too few: no specialisation. Too many: coordination overhead.
- **Concurrency model.** Sequential, async, parallel — each subagent could be any. The right default depends on workload.
- **Long-running OS robustness.** A Runa running for years needs OS-level reliability features (process restart, supervised crashes, state recovery). Borrowed from Erlang/OTP.
- **Multi-machine AI OS.** If Runa eventually runs across Pi + laptop + cloud, the OS becomes distributed. Open architectural question.

## 7. References (curated)

- Tanenbaum, *Modern Operating Systems.* For the OS theory baseline.
- Karpathy's *LLM-as-OS-kernel* posts and talks (2024). The popularising framing.
- arXiv:2310.08560 — Packer et al., *MemGPT.*
- arXiv:2309.02427 — Sumers et al., *CoALA.*
- Anthropic, *Building effective agents* posts.
- Companion docs: every research-2 doc maps to a layer of this architecture; [[92-process-scheduling-cognitive]] through [[96-resource-budgets]] are the direct deep dives.
