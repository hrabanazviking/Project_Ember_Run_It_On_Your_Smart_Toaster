---
codex_id: LETTA_ESSENCE
title: Letta Essence — Memory as the Operating System
role: Skald
layer: Vision
peer_targets: [Letta]
status: draft
peer_source_refs:
  - letta:README.md:1-110
  - letta:CITATION.cff:1-26
  - letta:AI_POLICY.md:1-64
  - letta:PRIVACY.md:1-127
  - letta:letta/agent.py:79-235
  - letta/agents/letta_agent.py:82-200
  - letta:letta/schemas/memory.py:68-200
  - letta:letta/functions/function_sets/base.py:87-450
  - letta:compose.yaml:1-66
  - letta:letta/services/agent_manager.py
  - letta:letta/services/block_manager.py
  - letta:letta/services/passage_manager.py
ember_subsystem_targets: [Brunnr, Smiðja, Funi, Hjarta, Munnr]
hermes_codex_refs:
  - 00_vision/01_HERMES_ESSENCE
  - 00_vision/03_ANTI_HERMES
ember_subsystem_targets: [Brunnr, Smiðja, Funi, Hjarta]
cross_refs:
  - 00_vision/CROSS_TRIANGULATION
  - 00_vision/CROSS_ANTI_PEERS
  - 00_vision/CROSS_VISION_REFINED
  - 10_domain/LETTA_MEMORY_ARCHITECTURE
  - 20_interface/LETTA_MEMORY_TOOL_INTERFACE
  - 60_synthesis/CROSSWALK_LETTA_TO_EMBER
---

# Letta Essence — Memory as the Operating System

> *Some systems are organised around what they do. Some are organised around what they think. Letta is organised around what it remembers. To read its bones is to learn what an agent looks like when the Well comes first and the loop comes second.*

## I. The seven sentences

If I had to give you the whole essence of Letta in seven sentences, this is what I would write. Everything else justifies them.

1. **Letta is the descendant of a research paper that proposed the LLM as an operating system, and it has never stopped believing that memory, not reasoning, is the kernel.** The CITATION still names the paper — *MemGPT: Towards LLMs as Operating Systems* (Packer et al., arXiv:2310.08560) — and the lineage shows everywhere in the code (`letta/CITATION.cff:1-26`).
2. **Letta makes memory a first-class, named, agent-callable surface.** The agent does not have memory; it *has tools for editing memory*, which it must use, which it is taught to use, which the system prompt forces it to use (`letta/functions/function_sets/base.py:246-450`).
3. **Letta separates the bounded "core" (always in context) from the unbounded "archival" and "recall" (retrieved on demand)**, and the boundary between them is a literal pgvector lookup over a Postgres table (`letta/services/passage_manager.py`, `letta/services/archive_manager.py`, `compose.yaml:1-22`).
4. **Letta is a server, not a script.** The deployment shape is `docker compose up` with PostgreSQL+pgvector, an HTTP API, an nginx fronting, a TypeScript SDK, a Python SDK, and the CLI is a separate npm package (`@letta-ai/letta-code`, README.md:11-17, compose.yaml:23-66).
5. **Letta sees the agent as a long-lived entity that outlives any conversation** — agents have IDs, agents persist between sessions, agents can be exported and imported, agents carry their memory blocks with them. The conversation is an event in the agent's life, not its substance.
6. **Letta is model-agnostic at the dispatch layer but opinionated at the surface** — `LettaAgent` works against an abstract `LLMClient` (`letta/agents/letta_agent.py:29-30`), but the recommendations in the README are Opus 4.5 and GPT-5.2; the system is built assuming a strong tool-using frontier model is at the wheel.
7. **Letta is corporate-shaped open source** — Apache-licensed (in spirit) but with telemetry-by-default opt-out (`PRIVACY.md`), a hosted endpoint that collects training data unless you self-host, a strict AI-disclosure contributor policy (`AI_POLICY.md`), and a clear delineation between the OSS server and the Letta Cloud service.

That is the self Letta is reaching for. Everything else — the four agent classes (`Agent`, `LettaAgent`, `LettaAgentBatch`, `LettaAgentV2/V3`), the 875 Python files, the 35 service managers, the alembic migrations — is in service of those seven sentences.

## II. The secret Letta does not state

The README leads with *advanced memory*. The CITATION leads with *MemGPT*. The API docs lead with *stateful agents*. None of them states the *secret of the project*, which becomes visible only after reading `letta/services/agent_manager.py` (3,599 lines) and noticing that the codebase calls itself an OS without ever quite saying so.

> **Letta is an operating system kernel that happens to wear the costume of an agent framework.**

It is shipped as a Python library, supplied with SDKs in two languages, used through HTTP — and architected, top to bottom, as if the agent were a process and the memory blocks were the address space. The core abstractions tell on it:

- **`AgentState`** is a process control block. It carries the agent's ID, its tools, its memory layout, its model config, its tool rules. It is *durable* — stored in the database — and *reloaded* between every step (`letta/agents/letta_agent.py:186-190`: `agent_state = await self.agent_manager.get_agent_by_id_async(...)`). A LettaAgent step *does not trust* its in-memory state across the loop; it goes back to the table.
- **`Memory`** is the address space. It has labelled blocks. Blocks have a `chars_limit`. Going over the limit raises a typed error, exactly the way an out-of-memory condition surfaces in a kernel (`letta/schemas/memory.py:155-173`).
- **`memory_replace` / `memory_insert` / `core_memory_append`** are page-table operations. They take a label (the page), an old string and a new string (the diff), and they validate carefully — uniqueness checks, line-number checks, expansion checks (`letta/functions/function_sets/base.py:311-450`).
- **`archival_memory_search` / `conversation_search`** are syscalls into the long-term store. They go *out* of the address space to find a passage, and they bring it back, but they do not put it permanently in core memory unless the agent explicitly chooses to.
- **`Summarizer`** is the swapper. When the context window fills, it evicts old messages into a summary block (`letta/agents/letta_agent.py:141-153`, `letta/services/summarizer/`). The discipline of where the summary goes, what it carries, what gets evicted, is genuinely OS-shaped.
- **The `step()` loop** (`letta/agents/letta_agent.py:174-200`) reads its agent state, executes a step, persists messages, persists step metrics, persists any tool execution result — each step is a transaction.

This is not metaphor; this is design. The paper is titled "LLMs as Operating Systems" and the code lives the title.

Why does this matter for Ember? Because **Ember has already chosen, in the Vow of Pluggable Storage and the architecture of Brunnr, to make memory a real subsystem with a real Protocol** ([[hermes_codex/00_vision/01_HERMES_ESSENCE]] §V, ANTI_HERMES Antipattern 1). Hermes refused to centralise memory; Letta *centralises memory and builds the whole agent around it*. The two systems are arguing different sides of the same question, and Ember's answer — the Well — sits between them.

This is the secret. Now to the bones.

## III. The five essences (and their evidence)

Letta has five essences I will name explicitly. Each comes with citations.

### Essence 1 — Memory is agent-callable, not system-managed

Hermes's curator (`agent/curator.py`) runs in the background, reviewing and archiving skills *without the agent's awareness*. The Hermes Vow that this serves is the Closed Learning Loop ([[hermes_codex/00_vision/01_HERMES_ESSENCE]] §III, Essence 1). Letta refuses this exact pattern. In Letta, *the agent is the curator*:

```python
def core_memory_append(agent_state: "AgentState", label: str, content: str) -> str:
    """Append to the contents of core memory."""
    current_value = str(agent_state.memory.get_block(label).value)
    new_value = current_value + "\n" + str(content)
    agent_state.memory.update_block_value(label=label, value=new_value)
    return new_value
```
(`letta/functions/function_sets/base.py:246-260`)

The agent calls this. The agent sees its results. The agent is responsible for choosing *when* and *what* to write. The system prompt shows the blocks every turn (`letta/schemas/memory.py:142-173`, the `_render_memory_blocks_standard` method renders `<memory_blocks>` with current/limit metadata, so the model knows how full each block is). The model writes the block via a tool call. There is no curator daemon.

Crucially, the operations are *surgical*: `memory_replace(label, old_string, new_string)` (`letta/functions/function_sets/base.py:311-388`) refuses to run if `old_string` is not unique, refuses if it contains a line-number prefix, refuses if it contains the line-number warning text. The agent must specify *what it is replacing*, not just *what the new state should be*. This is the same discipline as a `sed` script with safety rails — and it is encoded in the schema, not in the prompt.

The most important consequence: **agent-authored memory is verifiable**. Every memory edit is a `Message` of role `tool` with a function name and arguments persisted in `message_manager`. You can replay the agent's memory history. You can audit every edit. The Vow of Honest Memory — which Ember holds, which Hermes nudges, which Letta operationalises — finds its sharpest expression here.

### Essence 2 — The three-tier memory hierarchy

Letta names three distinct memory regions:

- **Core memory** (`letta/schemas/memory.py:68-130`): the in-context blocks. Always rendered. Bounded (`chars_limit`). Edited via `core_memory_append`, `core_memory_replace`, `memory_replace`, `memory_insert`, `rethink_memory`. This is the agent's "RAM."
- **Archival memory** (`letta/services/passage_manager.py`, `letta/services/archive_manager.py`): pgvector-backed long-term store. Tool surface: `archival_memory_insert(content, tags)`, `archival_memory_search(query, ...)`. This is the agent's "disk."
- **Recall memory** / **conversation history**: the durable record of past messages. Tool surface: `conversation_search(query, roles, start_date, end_date, limit)` (`letta/functions/function_sets/base.py:87-160`). This is the agent's "log."

The boundary discipline is explicit. The agent does not *automatically* pull from archival into core. The agent must *decide* to search archival, must *decide* to copy a finding into core if it wants the finding to persist in-context. The boundary is the system's load-bearing teaching:

> The model is taught — by the system prompt, by the tool docstrings, by the metadata it sees — that there is a wall between what is always present and what must be summoned. Crossing the wall is a tool call. The tool call is a decision the agent makes and the operator can read.

Smolagents has nothing like this. Goose has session history (and compaction) but not the named tiers. Hermes has cross-session memory via pluggable providers but no agent-callable surface — the provider decides when to inject. Letta is the *only one of the four* whose architecture says, in code: *"memory is the kernel, the agent is the program, retrieval is a syscall."*

### Essence 3 — The agent outlives the conversation

Hermes's `Agent` is bound to a session. Smolagents's `MultiStepAgent` is bound to `agent.run(task)`. Goose's `Agent` lives within a `Session`. In all three peers and in Hermes, the agent is *bounded by* the conversation.

Letta's `Agent` (`letta/agent.py:96-175`) and `LettaAgent` (`letta/agents/letta_agent.py:82-153`) are different. They take an `agent_id` and a `User`. They load `AgentState` from `agent_manager` at every step (`letta/agents/letta_agent.py:186-190`):

```python
agent_state = await self.agent_manager.get_agent_by_id_async(
    agent_id=self.agent_id,
    include_relationships=["tools", "memory", "tool_exec_environment_variables", "sources"],
    actor=self.actor,
)
```

The agent is *not* a long-lived Python object. The agent is a *row in a database* with relations to other tables: tools, blocks, sources. A Python `LettaAgent` instance is a short-lived dispatcher — it reads the agent row, runs a step, writes results back. Between requests, the agent *is* the database state.

This has profound consequences:

- **Horizontal scalability.** Two `letta_server` containers can serve the same agent (`compose.yaml:23-58`) — Postgres is the source of truth.
- **Multi-tenancy as a property.** Every method takes `actor: User`. Authorisation lives at the ORM layer.
- **Resumability is free.** A crash mid-step doesn't lose the agent — only the in-flight `Job`/`Run` is lost.
- **Migration is real.** `alembic/versions/` exists. The agent schema has versioned migrations. You can move an agent from one Letta install to another by exporting/importing rows.

Ember has chosen, in slice 2, the Episode model with FTS5 and pgvector for retrieval. Ember has chosen pluggable storage. Ember has *not* chosen multi-tenancy — and that refusal is correct for a personal hearth — but the Letta pattern of "agent state in the database, agent instance is ephemeral" is one Ember should study carefully when she grows toward sleeptime agents, scheduled work, or any process that runs detached from a single CLI session.

### Essence 4 — The server-client split is the deployment shape

Letta is not a library that an application embeds. Letta is a service the application calls (`README.md:19-45`).

The shape:

- `letta_db` (Postgres + pgvector) — `compose.yaml:2-22`
- `letta_server` (`letta/server/server.py`) — Python ASGI, exposes REST API on 8083, agent ports on 8283 — `compose.yaml:23-58`
- `letta_nginx` (optional) — `compose.yaml:59-66`
- `letta-client` (Python pip package) — `README.md:31-34`, `@letta-ai/letta-client` (TypeScript) — `README.md:26-29`
- `@letta-ai/letta-code` (CLI, separate npm package) — `README.md:8-17`

The fact that the CLI is *not in this repo* is telling. Letta the project has decided that the agent server is the canonical product; user-facing surfaces are clients. This is a Postgres-shaped or Kubernetes-shaped architecture, not a tool-shaped one.

The cost: deployment friction. To run Letta, you need Docker, you need Postgres, you need pgvector, you need a server, you need either local Ollama or a cloud key. The Hello World in the README assumes a Letta API key from `app.letta.com`, i.e. their hosted endpoint. The OSS path exists but is not the default flow.

The benefit: rigor. Once you accept the server, everything composes. The agent state is in a single database. Multiple agents share the database. Multiple users share the server. The frontend is decoupled. The API is OpenAPI-generated (the `fern/` directory).

Ember will not adopt this shape — see Anti-Letta below. But the *idea* that there is a Well, and the agent has a network address to find the Well, and the agent is small at the edge while the Well is large at the centre — that *is* exactly Ember's Strengr+Brunnr split. Letta has built it server-shaped; Ember will build it tether-shaped. The same insight, translated for a smaller hypothesis.

### Essence 5 — Tool-rule discipline as agent control

Letta has a system the others lack: **tool rules** (`letta/helpers/tool_rules_solver.py`, used at `letta/agent.py:116, 320-326`). A tool rule constrains which tools the agent may call at which times. Variants include:

- `InitToolRule` — must be called as the first tool.
- `TerminalToolRule` — calling this ends the loop (e.g. `send_message`).
- `ConditionalToolRule` — based on prior call history.
- `ToolRuleSolver` — computes the *currently allowed* tool set at every step (`letta/agent.py:320-322`).

The solver narrows the allowed-tool set to a subset of available tools each turn:
```python
allowed_tool_names = self.tool_rules_solver.get_allowed_tool_names(
    available_tools=available_tools, last_function_response=self.last_function_response
) or list(available_tools)
```

This is a deeper version of what smolagents calls "final answer checks" and what Goose calls "tool confirmation." Letta's discipline says: *the schema of what the agent may do next is computed by the framework, not by the prompt*. If a model doesn't support structured output well enough to be trusted with this constraint, Letta warns at agent-construction time (`letta/agent.py:122-127`).

This is the answer Letta gives to a question Hermes does not formally pose: *how do you bound the action space of an agent without re-inventing it in prose?* The answer is: name the rule kinds, write a solver, and let the framework filter the tool catalog every turn.

Ember should adopt this insight — but in a small form. The Forge's `[[30_execution/LETTA_AGENT_LOOP]]` and the Architect's `[[10_domain/LETTA_MEMORY_ARCHITECTURE]]` will draw it out. The relevant Ember Vow is the Vow of Modular Authorship: tool-rules are a *structural* constraint, not a prompt-level one, and that is the right place for them.

## IV. The triangulation — what these five essences mean together

Take all five at once and the secret-shape of Letta appears:

- **Memory as kernel** + **three-tier hierarchy** = memory is not stored, it is *managed*, with operations the agent must explicitly invoke.
- **Agent outlives conversation** + **server/client split** = the agent is a database row, the server is the kernel, the SDKs are syscalls.
- **Tool-rule discipline** = the framework, not the prompt, owns the agent's available action space.

This triangulation is *exactly* what a research lab built on the MemGPT paper would produce when commercialising. It is a clean engineering of the original paper's claim. It is *not* what Ember is. Ember is one hearth, one user, one device, one tether — Letta is *one server, many agents, many users, many sessions, network everywhere*.

But what Letta gets *right at the kernel level*, Ember would do well to study. The agent-callable memory tools. The three-tier hierarchy. The discipline of "memory edits are tool calls, persisted, replayable, auditable." These are correct insights that Hermes never quite codified.

## V. What Ember should inherit (preview)

A quick preview — each is justified at length in [[10_domain/LETTA_MEMORY_ARCHITECTURE]], [[20_interface/LETTA_MEMORY_TOOL_INTERFACE]], and [[60_synthesis/CROSSWALK_LETTA_TO_EMBER]].

- **The agent-callable memory edit model** — Brunnr already exposes a write surface; the *operator* writes via Smiðja, but the *agent* should have a smaller, more disciplined edit surface for a future "core memory" concept (the "operator persona / human persona" Letta-style blocks). This is a candidate Vow strengthening for Honest Memory: edits are tool calls, not silent context mutations.
- **The three-tier conceptual model** — Ember has Episodes (recall) and chunked Brunnr (archival). She does *not* yet have a named "core memory" tier that always renders. The Architect's domain map will propose this; the Skald's CROSS_VISION_REFINED will ratify or refuse.
- **Tool-rule solver** — a small version, with `InitToolRule` and `TerminalToolRule` only, fits Funi's loop. The Architect will trace.
- **The `chars_limit` discipline** — bounded blocks with visible current/limit metadata in the system prompt is a small thing that does a lot of work. Cheap to lift.
- **The `last_function_response` reload** — if the agent crashes mid-step, the next step can read its last function response from the message history rather than rebuilding state. The pattern is small (`letta/agent.py:176-189`) and instructive.

## VI. What Ember should refuse (preview)

Detailed in [[00_vision/CROSS_ANTI_PEERS]]. Summary:

- **The server-first deployment shape.** Ember runs on a Pi, not in Docker. The Vow of Public-Friendliness refuses "compose up Postgres" as a first step. Brunnr's pluggable adapter pattern is a *softer* version of Letta's pgvector-by-default.
- **The "agent is a database row" model.** Multi-tenancy, multiple agents per server, etc. — none of this is Ember's shape. Ember is one hearth.
- **The `summarize_messages_inplace` mid-conversation context mutation** (`letta/agent.py:432-436`) — same antipattern Hermes has ([[hermes_codex/00_vision/03_ANTI_HERMES]] Antipattern 7), with the same Vow violation (Honest Memory).
- **The `EphemeralSummaryAgent` / `Summarizer` sub-agents that re-author core memory** (`letta/agents/letta_agent.py:130-153`) — auto-summarised conversation blocks re-enter the agent's context as if they were ground truth. Ember's truncation is honest about being truncation.
- **The `tool_execution_sandbox` external-Docker dance** (`letta/services/tool_executor/tool_execution_sandbox.py`) — too heavy for a Pi.
- **The four agent classes** (`Agent`, `LettaAgent`, `LettaAgentBatch`, `LettaAgentV2`, `LettaAgentV3`, plus `EphemeralAgent`, `VoiceAgent`, `VoiceSleeptimeAgent`) — the class proliferation that comes from a project trying to satisfy many product surfaces at once. Ember will have one `Funi` loop.

## VII. A meditation on memory-first

There is a kind of agent architect who looks at the field and sees only *reasoning*. There is another who looks at the field and sees only *tools*. There is a third — and the MemGPT authors are it — who sees only *memory*. That third school is right about something specific, and Letta is its monument.

The thing the memory-first school is right about: **the failures of small agents are usually failures of context, and the failures of context are usually failures of memory.** When a small model loses the thread, it has rarely failed at reasoning — it has failed at recalling. The fix is not a better model; the fix is a better Well, better retrieval, better promotion of what matters into the limited core that the model sees.

Ember inherits this lesson directly. Funi is small. Funi's context is small. Funi *will lose the thread*. Brunnr is the Well that Funi forgets *into*, and the Well that Funi summons *from* when she needs to remember. Smiðja is what curates the Well's content. The Vow of Tethered Grounding *is* this lesson: knowledge lives outside the model, and the model summons what it needs.

Where Ember departs from Letta: Letta puts agent-callable memory tools at the agent's prompt and lets the agent decide when to write to core memory mid-conversation. Ember, in v1, will not. The reason is the Vow of Honest Memory and the small-model fragility: a `phi3:mini` calling `core_memory_append` with the wrong content writes garbage into the Well's most-loaded surface. Letta mitigates with strong frontier models (Opus 4.5, GPT-5.2). Ember does not have that luxury.

The right Ember inheritance is therefore: *Smiðja owns writes; Funi reads*. The operator authors core knowledge; the agent retrieves and reasons; the agent does *not* author memory edits in v1. This is more conservative than Letta, less conservative than Hermes (which has zero memory-authoring discipline). It is the right shape for a small, honest, tethered hearth.

## What This Means for Ember

The Letta reading produces concrete proposals.

- **Funi**: study Letta's `LettaAgent.step()` loop (`letta/agents/letta_agent.py:174-300`) and the `ToolRulesSolver` discipline (`letta/agent.py:116, 320-322`). Lift the *idea* of computing the allowed-tool set per-step, but in a small form (Init + Terminal only at v1). Refuse the `EphemeralSummaryAgent` mid-conversation pattern.

- **Strengr**: the Letta server/client split is *exactly* the Strengr↔Brunnr-as-remote-Well story translated to server architecture. Strengr should be able to talk to a Brunnr at network distance the way `letta-client` talks to `letta-server`. The retry/auth/idempotency discipline of the Letta SDK is worth lifting; the deployment overhead is not.

- **Brunnr**: study the three-tier model (core/archival/recall). Brunnr already implements something like *archival* (chunks + vector search) and *recall* (Episodes + FTS5). The missing tier is *core memory* — bounded, always-rendered blocks with `chars_limit`. Propose this as a Brunnr sub-surface, owned by Smiðja for writes (operator authors), surfaced by Funi for reads (always rendered). The Architect's [[10_domain/LETTA_MEMORY_ARCHITECTURE]] will trace; the Skald's [[CROSS_VISION_REFINED]] will ratify.

- **Smiðja**: Letta's `archival_memory_insert` is *agent-authored*. Smiðja, by contrast, is *operator-authored*. This difference is load-bearing for the Vow of Honest Memory. Smiðja should *not* lift the agent-callable insert pattern at v1. A future "agent-suggested ingest" surface where the agent *proposes* and the operator *approves* could exist; not in v1.

- **Hjarta**: Letta's first-run is `docker compose up`. Ember's is `ember setup`. The Letta path teaches us *what we don't want*: a multi-service stack as the price of entry. Hjarta's setup conversation is the right shape; Letta's compose file is a teacher by counter-example.

- **Munnr**: the `letta-code` CLI is a separate npm package, not in the main repo. Ember will *not* split Munnr out of the monorepo (the Vow of Modular Authorship and the existing monorepo structure are clear on this), but the *idea* that the CLI is decoupled from the server is good. Munnr should talk to Brunnr via Strengr-compatible interfaces, not by importing Brunnr directly. Slice 2 already honours this.

**Vows touched:**

- **Vow of Honest Memory** — *strengthened*. Letta's agent-callable, surgical, replayable memory edits are the strongest evidence I've seen that this Vow is correct. The discipline of `memory_replace(label, old_string, new_string)` refusing to run on duplicates or line-number warnings is a Vow-honoring schema. Ember should adopt the *idea* even where she refuses the *implementation*.
- **Vow of Tethered Grounding** — *strengthened*. The three-tier hierarchy is what tethered grounding looks like in code. Core memory = the part the agent always sees; archival = the part the agent summons; recall = the part the system keeps. Brunnr is poorer than Letta at the moment because she lacks an explicit "core" tier; the Architect will propose closing this gap.
- **Vow of Pluggable Storage** — *neutral*. Letta uses pgvector. Letta does not offer an adapter Protocol the way Brunnr does. This is a place Ember is *ahead*: she has the Protocol, she has multiple adapters (sqlite_vec + pgvector). Confirm this position.
- **Vow of Smallness** — *strained*. Letta is large. `agent_manager.py` is 3,599 lines. The `services/` directory has 30+ managers. The temptation to copy this shape into Ember must be resisted. The CROSS_ANTI_PEERS doc names this strain explicitly.
- **Vow of Public-Friendliness** — *strained*. Letta's first-run is multi-container Docker. Hjarta must not look like this. Letta is a teacher by what it does *not* do.
- **Vow of Graceful Offline** — *neutral*. Letta is online-by-default; the OSS server can run with local Ollama but the project's centre of gravity is online. Ember's offline-first commitment is a real differentiator.

**The Architect's [[10_domain/LETTA_MEMORY_ARCHITECTURE]] picks up the bones. The Cartographer's [[20_interface/LETTA_MEMORY_TOOL_INTERFACE]] traces the surfaces. The Forge's [[30_execution/LETTA_AGENT_LOOP]] follows the loop. The Auditor's [[50_verification/LETTA_RISK_REGISTER]] names the risks. The Cartographer's [[60_synthesis/CROSSWALK_LETTA_TO_EMBER]] maps the inheritance.**

The memory-first school has been read. Two more peers remain.

— Sigrún Ljósbrá
