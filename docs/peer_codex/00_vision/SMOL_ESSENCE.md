---
codex_id: SMOL_ESSENCE
title: smolagents Essence — Smallness as Discipline
role: Skald
layer: Vision
peer_targets: [smolagents]
status: draft
peer_source_refs:
  - smolagents:README.md:34-256
  - smolagents:AGENTS.md:1-5
  - smolagents:docs/source/en/conceptual_guides/intro_agents.md:1-110
  - smolagents:src/smolagents/__init__.py:17-32
  - smolagents:src/smolagents/agents.py:268-450
  - smolagents:src/smolagents/agents.py:1215-1810
  - smolagents:src/smolagents/local_python_executor.py:1-100
  - smolagents:src/smolagents/local_python_executor.py:1500-1768
  - smolagents:src/smolagents/memory.py:1-316
  - smolagents:src/smolagents/tools.py
ember_subsystem_targets: [Funi, Munnr, Brunnr]
hermes_codex_refs:
  - 00_vision/01_HERMES_ESSENCE
  - 00_vision/03_ANTI_HERMES
cross_refs:
  - 00_vision/CROSS_TRIANGULATION
  - 00_vision/CROSS_ANTI_PEERS
  - 00_vision/CROSS_VISION_REFINED
  - 10_domain/SMOL_DOMAIN_MAP
  - 30_execution/SMOL_MINIMALISM_LESSONS
  - 30_execution/SMOL_CODE_AS_ACTION
  - 60_synthesis/CROSSWALK_SMOL_TO_EMBER
---

# smolagents Essence — Smallness as Discipline

> *Not every smallness is a smallness of the same kind. There is a smallness that is poverty, and there is a smallness that is discipline. smolagents is the second kind, and the line counts are not the proof — the refusals are.*

## I. The seven sentences

If I had to give you the whole essence of smolagents in seven sentences, this is what I would write.

1. **smolagents is a deliberately small library whose stated thesis is that the agent loop fits in <1,000 lines and abstractions above that line are usually wrong** (`README.md:36`, `agents.py` is 1,814 lines including two full agent variants and all the streaming/serialization plumbing — the *core* loop is genuinely ~1,000 lines).
2. **smolagents believes actions should be written in code, not JSON**, and the CodeAgent is the headline product; the ToolCallingAgent is provided for completeness but is the secondary citizen (`README.md:38, 248`, `agents.py:1505 vs agents.py:1215`).
3. **smolagents is model-agnostic but not provider-loyal** — it ships seven model backends (`InferenceClientModel`, `LiteLLMModel`, `OpenAIModel`, `TransformersModel`, `AzureOpenAIModel`, `AmazonBedrockModel`, `MLXModel`) but treats them all as conformant to a thin `Model` interface (`models.py`, used at `agents.py:62-72`).
4. **smolagents is tool-agnostic by integration**, not by core abstraction — `Tool` is a class; tools can be loaded from MCP servers (`mcp_client.py`), from LangChain (`tools.py::Tool.from_langchain`), from HF Spaces (`tools.py::Tool.from_space`), from the HF Hub (`tools.py::Tool.from_hub`), or written from scratch as Python functions.
5. **smolagents treats the Hugging Face Hub as the agent's package manager** — agents can be pushed and pulled (`agent.push_to_hub`, `agent.from_hub`), tools can be shared, the Hub is the equivalent of npm for the agent ecosystem.
6. **smolagents takes the security problem seriously and is honest about its own limits** — the `LocalPythonExecutor` is explicitly *not* a security sandbox (`README.md:246, 273`), and the library ships five other executors (E2B, Blaxel, Modal, Docker, Wasm/Pyodide-Deno) for actual isolation (`remote_executors.py`).
7. **smolagents is a library, not a server** — the CLI (`smolagent`, `webagent`) exists but is thin (`cli.py:294 lines`, `vision_web_browser.py:247 lines`), and the project's centre of gravity is `from smolagents import CodeAgent; agent.run(task)`.

That is the self smolagents is reaching for. Everything else — the 30,968-line repository, the documentation, the benchmarks — is in service of those seven sentences.

## II. The secret smolagents does not state

The README leads with simplicity. The `AGENTS.md` is *five lines long* — "Follow OOP principles, be Pythonic, write unit tests for new functionality" (`smolagents/AGENTS.md:1-5`). The intro guide leads with the agency spectrum. None of them states the *secret of the project*, which becomes visible only after reading the agent loop and noticing what is *missing*:

> **smolagents is a deliberate refusal of the agent framework as a category.**

The largest agent frameworks of the era — LangChain, AutoGen, CrewAI, even Hermes and Letta — define an "agent" as a system that owns: a memory model, a tool registry, a model abstraction, a planning subsystem, a session model, possibly a UI, possibly a deployment shape. smolagents refuses *most of that*. It owns:

- An agent loop (`MultiStepAgent.run` / `_run_stream` at `agents.py:436-780`, ~340 lines)
- A memory class that is *literally a list of steps* (`memory.py:1-316`, named `AgentMemory`, but it has no archival, no retrieval, no scoring — it is a Python list with a few render helpers)
- A model interface (~2,100 lines but most of that is adapter code for the seven backends; the interface itself is trivial)
- A tool class with a docstring-driven schema
- A code executor (the load-bearing one) and an action parser

It does *not* own: cross-session persistence, multi-user auth, deployment infrastructure, a server, a database, a curator, an evolutionary skill system, prompt caching, a routine system, a gateway. It does not even own *durable memory* — when the Python process exits, the agent is gone unless the developer wrote their own persistence on top.

This is not minimalism by accident; it is minimalism by hypothesis. The thesis of smolagents is *the agent does not need most of what frameworks have accumulated. Give the LLM tools and a code interpreter and a small ReAct loop, and the rest is a distraction.*

Why does this matter for Ember? Because **Ember has stated the Vow of Smallness as her first Vow**, and smolagents is the closest peer in the field that has lived that Vow at architecture-scale. The temptation, after reading Hermes, is to think "smallness is a constraint that prevents capability." smolagents disproves this. The library is *capable* — it ships benchmarks where it beats much larger systems — and it is *small*, in the same breath.

The harder question — which the smolagents authors do *not* state explicitly — is: **what did smolagents have to refuse to stay small?** That is what makes this document load-bearing for Ember.

## III. The five essences (and their evidence)

smolagents has five essences I will name explicitly. Each comes with citations.

### Essence 1 — Code as the action surface

smolagents's central architectural bet is that the agent's *actions* should be Python code, not JSON tool calls. The CodeAgent (`agents.py:1505-1810`) is the default. Its system prompt (`prompts/code_agent.yaml`) teaches the model to write Python blocks. The model produces something like:

```python
results = web_search("smolagents architecture")
for r in results[:3]:
    print(r.title, r.url)
```

The agent parses this with `parse_code_blobs` (`utils.py`), executes it through a `PythonExecutor` (`local_python_executor.py:1768 lines`, the load-bearing module), captures `print` output as the "observation," and feeds it back into the next turn.

Why this matters:

- **Composability**: one code block can call three tools, loop, conditionally branch, store intermediate state. A JSON tool call cannot.
- **Density**: one code action does what three JSON actions would. The paper smolagents cites (Wang et al., 2024, "Executable Code Actions Elicit Better LLM Agents") shows ~30% fewer steps.
- **Naturalness**: code is the modality the LLM has the most pretraining data in.
- **Honesty about complexity**: when a task gets hairy, the agent *writes a program*, which is how a human would solve it.

The cost: **arbitrary code execution as the foundational primitive**. This is acknowledged head-on (`README.md:241-246`, `local_python_executor.py:46-71`). The `LocalPythonExecutor` parses the AST, filters dunder access, applies operation budgets and timeout limits — but the docstring (`README.md:273`) is unambiguous: *"`LocalPythonExecutor` provides best-effort mitigations only and is not a security boundary. Do not use it to run untrusted code."*

The honest solution is to use one of the remote executors — E2B (`e2b_executor.py`), Blaxel, Modal, Docker, or the WASM/Pyodide-Deno executor — which provide actual isolation. The library makes this a one-line change: `CodeAgent(executor_type="e2b", ...)`.

Ember will *partially* inherit this insight. Funi will not be a CodeAgent — the security cost is too high for a personal hearth running a local model with no sandboxed compute. But the *idea* that a tool call can be more expressive than `{"name": "foo", "args": {...}}` is correct, and Munnr's tool-protocol surface should not foreclose code-shaped tools (one tool that takes a Python expression and evaluates it inside a tightly-bounded sandbox is plausible for slice-N).

### Essence 2 — Memory as a list

smolagents's `AgentMemory` is small enough to read in one sitting (`memory.py:1-316`). Its shape:

```python
class AgentMemory:
    system_prompt: SystemPromptStep
    steps: list[MemoryStep]  # TaskStep, ActionStep, PlanningStep, FinalAnswerStep
```

That is the memory. A list of typed step records. Each step carries timing, token usage, model output, observations, tool calls, errors. The agent re-renders the memory as messages on every step via `write_memory_to_messages()` (used at `agents.py:782+`).

There is *no* archival memory. There is *no* retrieval. There is *no* curator. There is *no* recall search. When you ask the agent something, it sees its full step history rendered as ChatML; when the step count grows, the context grows; when the context exceeds the model's window, you have a problem the library does not solve for you.

This is a *radically* different choice from Letta and Hermes. It says: *the agent's working memory and its persistent memory are the same thing; if you want persistence, persist the memory yourself between runs; if you want retrieval, build it on top.*

The defensible position: tasks that fit in one `agent.run()` invocation don't need durable memory. The agent does its work and exits. If you want a Q&A bot with long-term memory, smolagents is the wrong library — go use Letta. smolagents is for *tasks*, not *companions*.

This is the cleanest separation of concerns I have seen in the four-way comparison. It is also a refusal Ember cannot fully copy: Ember *is* a companion, by hypothesis, and the Well is core to her identity. But the *step list as the working-memory primitive* is good design. Funi's per-turn state in slice 2 already approximates this — a Conversation object accumulates messages and tool calls. The smolagents discipline says: *make this the only working memory; promote nothing implicitly; persist nothing implicitly; if it needs to live, somebody must explicitly send it to Brunnr*. That is precisely Ember's Vow-of-Honest-Memory shape, and smolagents validates it.

### Essence 3 — The Hub as package manager

smolagents treats the Hugging Face Hub the way Node treats npm: it is the canonical place for sharing tools, models, and agents (`README.md:40, 70-77`). The API:

- `Tool.from_hub("user/tool-repo")` — load a tool from a HF Space
- `Tool.from_space("user/space")` — wrap an HF Space as a tool
- `Tool.from_langchain(...)`, `Tool.from_mcp(...)` — adapters to other ecosystems
- `agent.push_to_hub("user/my-agent")` — share the agent
- `agent.from_hub("user/my-agent")` — load it back

This is a federated extension model — agents and tools are normal Hub repos, public or private. The HF Hub auth flow is the agent's auth flow. The Hub's versioning is the agent's versioning. The Hub's safety/abuse policies are the agent's.

Compare to:
- **Hermes**: in-tree plugins + the operator's `~/.hermes/skills/` — no federated registry. Agent-authored skills live on the operator's disk only.
- **Letta**: tools live in the database; no federated marketplace; the official "tools" are documented at docs.letta.com but there is no `letta.tools.from_hub()`.
- **Goose**: MCP servers in the wild are the federation, but the MCP protocol is the standard, not a specific registry; Goose has Block-curated "extensions" but the Hub-as-package-manager pattern is not the model.

For Ember, this is *information* more than a pattern to lift. The Vow of Open Knowledge and the Vow of Public-Friendliness both have *opinions* about how Ember's content (operator-authored knowledge, Smiðja content sources, future skills) should be shareable. smolagents shows that "tools and agents are first-class repository citizens" is a viable model. Ember will probably not build a registry, but if the Open Knowledge Vow ever requires "operator can share a Brunnr corpus with a friend," the smolagents Hub pattern is the easiest precedent to lift.

### Essence 4 — Multi-step ReAct as the only loop

There is *one* agent loop in smolagents. It is `MultiStepAgent._run_stream` (`agents.py:436-780`). It is ReAct, in the original Yao et al. form, with three optional enhancements:

- A *planning step* every N steps if `planning_interval` is set (`agents.py:330-340`).
- *Step callbacks* that fire after each step, dispatched by step-type or globally (`agents.py:351`).
- *Final answer checks* — validation functions that can refuse a `final_answer` and force the loop to continue (`agents.py:309-310, 335`).

That's it. No internal sub-agent invocation (managed agents exist but are external — `agents.py:369-388`). No streaming-only or batch-only paths (streaming is opt-in via `stream_outputs=True`). No alternate-loop modes for thinking vs acting.

This is *radical restraint*. Hermes has multiple loop modes (interactive, batch, no-agent cron, sub-agent). Letta has four agent classes plus an EphemeralSummaryAgent. Goose has streamed reply, recipe-driven non-interactive runs, sub-agents. smolagents has one loop, one shape, one mental model.

Ember should adopt this discipline. Funi has *one* loop. There is *one* shape. If Ember ever needs a non-interactive mode, it is the same loop with an input source change. If Ember ever needs a sub-agent, it is the same loop, recursively invoked. The Vow of Smallness and the Vow of Modular Authorship together argue for this; smolagents lives it.

### Essence 5 — Honesty about security

smolagents is the first peer I have read whose README contains the sentence *"Do not use it to run untrusted code"* about its own primary executor (`README.md:273`). The library names its own security boundary as best-effort, points the user at *five* alternative sandboxes (E2B, Blaxel, Modal, Docker, Wasm), and refuses to pretend the local executor is more than it is.

The local executor itself (`local_python_executor.py:1768 lines`) is sophisticated:

- AST-walked interpreter (does not use Python's `exec`)
- Configurable authorized imports list (`BASE_BUILTIN_MODULES` + `additional_authorized_imports`)
- Dunder access denied (`local_python_executor.py:68-71`)
- Operation budget (`MAX_OPERATIONS = 10_000_000`)
- While-loop budget (`MAX_WHILE_ITERATIONS = 1_000_000`)
- Execution timeout (`MAX_EXECUTION_TIME_SECONDS = 30`)
- Output truncation (`DEFAULT_MAX_LEN_OUTPUT = 50_000`)

This is real engineering. And yet the README still says: *not a security boundary*. The honesty is striking.

The lesson for Ember is double-edged. First: when Ember builds a tool sandbox (slice-N, when she has Munnr-tool concerns), she should be this honest about its limits. Second: there is a *huge* engineering cost to AST-walked interpretation, and Ember should not pay that cost unless the tool surface justifies it. Ember's tool surface in v1 is small (Funi's bounded action set); the AST-walker is overkill. If Ember ever does code execution, she should use Wasm/Pyodide (the smolagents WasmExecutor pattern) or Docker (the Modal/E2B pattern, simplified to local Docker), never roll her own AST interpreter.

## IV. The triangulation — what these five essences mean together

Take all five at once and the secret-shape of smolagents appears:

- **Code as action** + **memory as list** = the agent is a programmer with a notebook. No long-term memory, no curator, no provenance — just an iterative programmer-loop with a small workbook of past steps.
- **Hub as package manager** + **one loop** = sharing is structural, not architectural. You don't extend smolagents by writing a plugin; you write a tool, push it to the Hub, and `Tool.from_hub()` it.
- **Honesty about security** = the library doesn't pretend to solve hard problems it hasn't actually solved.

This triangulation is *exactly* what an opinionated, paper-driven open-source library wants to be. It is *not* what Ember is. Ember is a personal hearth with durable memory, with operator-authored knowledge, with a specific commitment to *not* being a programmer-loop. But the *discipline* of smolagents — the things it refused to grow — is what Ember should study most carefully.

## V. What Ember should inherit (preview)

A quick preview — each is justified at length in [[10_domain/SMOL_DOMAIN_MAP]], [[30_execution/SMOL_CODE_AS_ACTION]], and [[60_synthesis/CROSSWALK_SMOL_TO_EMBER]].

- **The single-loop discipline**. One loop, one shape. Funi's loop is the *only* loop. If Ember ever needs batch processing, scheduled work, or sub-agents, those are wrappers around the same loop, not parallel loops.
- **The step-list working memory**. Smolagents's `AgentMemory` as a list of typed steps is exactly the shape Ember's Conversation/Episode should adopt: typed step records, no implicit promotion, no implicit retrieval. Persistence (to Brunnr) is *explicit* and *operator/system-triggered*, never *agent-triggered* in v1.
- **Honesty about security limits**. When Ember builds a tool sandbox or a code-execution surface, she names its limits in the README the way smolagents does.
- **The `add_base_tools` flag pattern** (`agents.py:301, 394-402`). A boolean that adds the default toolkit. Cleaner than Hermes's eager-discovery. Adopt the pattern for Funi's default tool surface.
- **The `final_answer_checks` discipline**. Validation functions that can refuse a terminal action and force another step. Ember has nothing like this; it is a small, clean structural constraint. The Auditor will propose.
- **The `Tool` class with docstring-driven schema**. Tools are normal Python classes/functions with docstrings; the schema is generated from the type hints (`_function_type_hints_utils.py:431 lines`). No separate JSON schema file, no decorator soup. Ember should adopt.

## VI. What Ember should refuse (preview)

Detailed in [[00_vision/CROSS_ANTI_PEERS]]. Summary:

- **CodeAgent as the primary shape**. Funi is not a CodeAgent in v1. The arbitrary-code-execution security cost is unacceptable for a hearth running a small model on a personal device with no sandboxed compute substrate. The smolagents authors are honest about this; Ember is honest in turn by refusing.
- **Memory as a list with no archival**. Ember has a Well. The Vow of Tethered Grounding demands it. The smolagents discipline of "step list as working memory" is good; the *refusal of archival* is wrong for Ember.
- **The HF Hub as package manager**. Ember does not have a centralised marketplace, and the Vow of Open Knowledge does not require one. Federation, if any, will be operator-shaped (Smiðja ingesting from a remote source), not platform-shaped.
- **Multiple remote executor adapters**. Smolagents ships five (E2B, Blaxel, Modal, Docker, Wasm). Ember's surface, when she has one, will be one. The Vow of Smallness and the Vow of Modular Authorship together argue for *one* sandbox if/when sandbox is needed.
- **The `gradio_ui.py` web-UI module**. Ember has Munnr as the CLI; a Gradio UI is a v0-or-never product. Refuse.
- **Multiple planning modes**. The structured-outputs-internally path (`agents.py:1545-1554`) loads two different prompt YAMLs depending on flag. Funi has one prompt. One mode. One shape.

## VII. A meditation on smallness as discipline

There is a kind of project that is small because it has not yet grown. There is another that is small because it has refused to grow. The first is a sapling; the second is a bonsai. They look alike in a photograph and are not the same kind of thing.

smolagents is bonsai. The 13,090 source lines under `src/smolagents/` are *carefully cropped*. The library could have grown an archival memory module — it didn't. Could have grown a server — didn't. Could have grown a deployment story — didn't. Could have grown a plugin system — didn't. Could have grown its own marketplace — didn't (it leans on the HF Hub instead, refusing to invent a new registry).

The refusals are what makes it small. The *capability* is the same as a much larger system — benchmarks confirm — but the *architectural footprint* is a fraction. The lesson for Ember is not "be like smolagents." The lesson is: *every system makes refusals; the question is whether the refusals are conscious or accidental.* Ember's Vow of Smallness will only hold if her refusals are named, documented, and defensible. The Anti-Hermes doc was the first instance of this discipline. The Anti-Peers doc will be the second. The discipline must continue every time Ember faces a temptation to grow.

smolagents teaches: **the framework that is small enough to read is the framework that can be trusted**. A reader who can hold `agents.py` and `local_python_executor.py` and `tools.py` in mind simultaneously can audit them, can extend them, can refuse them. A reader who cannot hold Hermes's 14,560-line `cli.py` cannot. Ember will be small enough to read. That is what the Vow of Smallness pays for.

## What This Means for Ember

The smolagents reading produces concrete proposals.

- **Funi**: study smolagents's `MultiStepAgent._run_stream` (`agents.py:436-780`) as the cleanest reference implementation of a single-shape ReAct loop. Lift the *one-loop discipline*. Lift the `step_number` / `max_steps` / `step_callbacks` shape. Lift `final_answer_checks` as the v1 mechanism for "agent must satisfy a structural check before terminating." Refuse the CodeAgent shape; Funi's actions are tool calls, not code blocks, at v1.

- **Strengr**: study smolagents's `Model` interface (`models.py`). The interface is thin: `generate(messages, stop_sequences, **kwargs) -> ChatMessage` plus a streaming variant. Strengr's interface to the remote provider should be this thin. Confirm: the slice-2 `LLMProvider` Protocol already matches this shape.

- **Brunnr**: smolagents has no Brunnr-equivalent. This is *information* — it tells Ember that her commitment to durable, retrievable memory is a real architectural commitment that distinguishes her from libraries-shaped agents. Confirm the position. Refuse the "memory is a list" stripping.

- **Smiðja**: smolagents has no Smiðja-equivalent either. Same lesson: Ember's commitment to operator-curated knowledge ingestion is a real position. Confirm.

- **Hjarta**: smolagents's `cli.py` (294 lines) has an interactive-mode wizard for first-time users (`README.md:189-195`). Read it. It is a clean reference for "small wizard that asks just enough to get going." Hjarta's setup conversation can borrow the *brevity* discipline.

- **Munnr**: smolagents's two CLI surfaces (`smolagent` and `webagent`) are minimal — one for general agents, one for web-browsing. Each is a thin wrapper around the library. Munnr should follow this pattern: the CLI is *thin*, the loop is *in Funi*, the tool/memory work is *in Brunnr/Smiðja*. CLI logic in Munnr stays under (call it) 800 lines per module. The smolagents-style `cli.py:294 lines` is a North Star.

**Vows touched:**

- **Vow of Smallness** — *strongly reinforced*. smolagents is proof of concept that smallness is a design discipline, not a stage of immaturity. Ember's commitment is correct.
- **Vow of Modular Authorship** — *reinforced*. smolagents's tools are normal Python objects with normal interfaces. No plugin registry. No discovery dance. The library is a *kit*, and the user assembles. Ember's Brunnr/Smiðja Protocols are this shape; confirm.
- **Vow of Tethered Grounding** — *strained*. smolagents *does not honor this Vow*. Its memory is a Python list. Ember explicitly does. Reading smolagents reveals the cost of *not* having tethered grounding: every `agent.run()` starts from scratch, no learning persists, no operator-curated context. Ember is right to refuse this.
- **Vow of Honest Memory** — *reinforced indirectly*. smolagents's refusal to have a curator means there is no entity that can edit memory dishonestly. Ember can borrow this discipline: in v1, Smiðja writes, Funi reads, no entity edits memory mid-conversation.
- **Vow of Pluggable Storage** — *neutral*. smolagents has no storage to plug. This is information about scope: Ember commits to something smolagents declines to attempt.
- **Vow of Public-Friendliness** — *reinforced*. smolagents's quickstart is `pip install smolagents[toolkit]` + 6 lines of Python. That is the friendliness bar. Hjarta should aim at the same shape: one install command, one short conversation, one running agent.
- **Vow of Open Knowledge** — *reinforced*. smolagents demonstrates that open knowledge can live as Hub repos with no proprietary marketplace. Ember's Open Knowledge commitment is satisfied by the existence of git/the operator's filesystem; she does not need a marketplace.

**The Architect's [[10_domain/SMOL_DOMAIN_MAP]] picks up the bones. The Forge's [[30_execution/SMOL_MINIMALISM_LESSONS]] traces the cuts. The Forge's [[30_execution/SMOL_CODE_AS_ACTION]] traces the bet. The Cartographer's [[60_synthesis/CROSSWALK_SMOL_TO_EMBER]] maps the inheritance.**

The bonsai has been read. One peer remains.

— Sigrún Ljósbrá
