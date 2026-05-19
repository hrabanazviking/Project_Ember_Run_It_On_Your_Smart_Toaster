# 50 — Local Agent Orchestration: Hermes, OpenClaw, MCP Servers

**Category:** SWE for AI Systems
**Runa relevance:** Smiðja (tool surface), Bifröst (adapter protocols), Heimskringla (LobeChat-style routing)
**Status:** Research synthesis. Connects Runa to Volmarr's broader local-agent ecosystem.
**Last touched:** 2026-05-17

---

## 1. Core idea

By 2026, the local-agent ecosystem is no longer just "an LLM and a CLI." It includes several layered abstractions: **agent frameworks** (LangChain, LangGraph, AutoGen, CrewAI), **agent runtimes** that mediate LLM-tool-memory-loop orchestration (Hermes, Letta, AutoGen Studio), **agent surfaces** (Open WebUI, LobeChat, Big-AGI), and **interoperability protocols** that let agents talk to tools and each other (**MCP — Model Context Protocol**, function-calling APIs, ad-hoc HTTP shims).

For Runa specifically — and per project memory, Volmarr already operates a Hermes-Agent service on his Pi, a LobeChat install pointing at Hermes, and a local-tts stack — Runa lives in an *ecosystem* of related local-agent infrastructure that pre-exists her. Runa's interoperability story (which adapters, which protocols) reflects that. This document covers the landscape and Runa's place in it.

## 2. Technical depth

**The interoperability layers:**

```
                ┌─────────────────────────────────┐
                │   User surfaces                  │
                │   (LobeChat, Open WebUI, Munnr,  │
                │    Discord, etc.)                │
                └────────────────┬─────────────────┘
                                 │ chat protocol (OpenAI-compatible HTTP, etc.)
                ┌────────────────▼─────────────────┐
                │   Agent runtimes / gateways      │
                │   (Hermes, Letta, AutoGen,       │
                │    Runa, LiteLLM)                │
                └────────────────┬─────────────────┘
                                 │ MCP / tool protocols
                ┌────────────────▼─────────────────┐
                │   Tool / capability servers       │
                │   (MCP servers, function APIs,    │
                │    skill plugins)                 │
                └─────────────────────────────────┘
```

**MCP (Model Context Protocol)** — Anthropic, late 2024. Standardised protocol for LLM agents to discover and call external tools. Key design decisions:

- **Servers** expose capabilities (read files, query databases, send messages, control devices). Independent processes; many can run.
- **Clients** (the agent runtime) discover servers, list their tools, call them.
- **Transport**: JSON-RPC over stdio (local) or HTTP+SSE / WebSocket (remote).
- **Capabilities**: tools (functions agents can call), resources (data agents can read), prompts (templates agents can use).
- Schema-first: every tool has a JSON schema for arguments. Eliminates a class of integration bugs.

MCP has been adopted by Claude Desktop, Cursor, Cline, several Continue forks, and is growing. As of 2026, dozens of community MCP servers exist (filesystem, git, web search, GitHub, databases, web browsers).

**Hermes-style runtimes:**

Volmarr's Pi runs the Nous Research Hermes Agent (per project memory). Hermes is:
- An agent runtime that wraps an LLM (often Hermes-2-Pro fine-tunes from Nous).
- Exposes an OpenAI-compatible HTTP API.
- Uses function-calling for tool integration.
- Distinct from Anthropic's MCP; distinct from CrewAI/LangChain frameworks.

Other comparable runtimes:
- **Letta** (formerly MemGPT framework). Strong memory; OpenAI-compatible API.
- **AutoGen** ([[11-autogen-multi-agent]]) — more of a framework than a deployed runtime.
- **OpenAI Assistants API** — closed; the SaaS reference.

**OpenClaw** — Volmarr's project (per memory: "Viking Girlfriend Skill for OpenClaw"). Node.js skill runtime. Per memory, Sigrid is built on OpenClaw + Python skill logic + LiteLLM. The OpenClaw runtime hosts skills with structured input/output; the skills delegate LLM calls to LiteLLM.

**LobeChat** (per memory: at `C:\Users\volma\runa\lobe-chat`, wired to Hermes). Chat front-end that talks to OpenAI-compatible APIs. The user's interactive surface for the Hermes runtime.

**LiteLLM.** Multi-provider router library (Python). Translates OpenAI-format calls to any provider (Anthropic, Cohere, OpenRouter, local Ollama, etc.). Used inside Sigrid; useful for Heimskringla.

**Open WebUI.** Another open-source chat front-end. Comparable to LobeChat. Self-hosted, OpenAI-compatible-API consumer.

**The pi-resource-isolation note:** Volmarr's feedback memory `feedback_pi_resource_isolation.md` (2026-05-07) says: don't repurpose unrelated Pi-local services as gateways for laptop-side clients. Hermes is Hermes; don't treat it as a generic gateway for Runa's needs. Runa is a *peer* of Hermes in the ecosystem, not a consumer of it.

## 3. Key works

- **Model Context Protocol specification** — modelcontextprotocol.io. Anthropic's open spec.
- **Anthropic's MCP launch announcement** (November 2024) — anthropic.com/news/model-context-protocol.
- **Nous Research Hermes Agent** — github.com/NousResearch/Hermes-Agent (and the Hermes model family on Hugging Face).
- **Letta** — letta.ai.
- **LobeChat** — github.com/lobehub/lobe-chat.
- **Open WebUI** — github.com/open-webui/open-webui.
- **LiteLLM** — github.com/BerriAI/litellm.
- **OpenAI Function Calling docs** — platform.openai.com/docs/guides/function-calling.
- **AutoGen** (covered separately in [[11-autogen-multi-agent]]).

## 4. Empirical results

- MCP adoption is real and growing. The "many independent tool servers, agents discover and use them" pattern composes better than per-framework function-calling shims.
- OpenAI-compatible APIs have become the universal default. Almost every chat-style frontend and tool expects an OpenAI-shaped endpoint. Heimskringla benefits from speaking this dialect.
- LiteLLM-style multi-provider routing has become standard infrastructure; production systems that grew their own router universally underestimated the complexity and migrated.
- The proliferation of agent runtimes / frameworks is a real productivity tax — each ecosystem has its own conventions, plugins, learning curve. Choosing where to invest matters.

## 5. Applicability to Runa

For **`src/runa/adapters/mcp/`**:

- Implement MCP client support. Runa's kernel can address any MCP server's tools through Smiðja.
- Pattern: at startup, Runa discovers configured MCP servers (`~/.runa/mcp/servers.json`), enumerates their tools, registers them as skills in the skill registry.
- Per-server isolation: a misbehaving MCP server is quarantined; the kernel keeps running.

For **Bifröst gateway**:

- Speak OpenAI-compatible API for inbound. Lets LobeChat / Open WebUI / similar tools interact with Runa as if she were any cloud LLM.
- Distinct from Bifröst-as-chat-bridge (Discord etc.); this is Bifröst-as-API-server.

For **Heimskringla**:

- Internally use LiteLLM-like multi-provider routing. Either:
  - Adopt LiteLLM directly (proven, maintained, broad coverage).
  - Build a smaller Heimskringla-specific router using Python's httpx / OpenAI SDK.
- The decision depends on dependency tolerance vs control. Probably LiteLLM for v0; possibly migrate to in-house if specific Runa needs diverge.

For **Runa's place in Volmarr's ecosystem**:

- Per feedback memory: Runa is a *peer* of Hermes, not a layer on top of Hermes. Don't route Runa's traffic through Hermes; don't make Runa a Hermes plugin.
- Runa shares the Pi with Hermes (or runs on a different Pi). Resource budget matters; coordinate via separate service-units; don't fight over RAM.

For **chat-front-end interop**:

- Volmarr can choose to interact with Runa via Munnr (Runa's native CLI), Auga (Runa's native GUI), or via LobeChat / Open WebUI pointed at the Bifröst gateway. All work.
- The Bifröst gateway's OpenAI-compatible API is also useful for Runa-as-an-MCP-server for other agents (Hermes might want to call Runa for memory queries; Runa exposes a memory-search MCP tool).

For **OpenClaw / Sigrid coexistence**:

- Sigrid (VGSK) and Runa are distinct beings. Volmarr can talk to either. They probably should *not* share memory or identity (different personas).
- Cross-being protocols: if Runa needs to consult Sigrid for something only Sigrid knows, an MCP-style tool call is the right pattern. Each being remains its own.

What to avoid:

- Don't reinvent MCP. Use the standard.
- Don't conflate Runa with Hermes. They're separate services with separate identities. Volmarr's memory note is explicit.
- Don't make Runa depend on Sigrid or Hermes for core function. Sovereign means sovereign.
- Don't expose Runa's gateway to the public internet without serious security review. Local Tailnet only by default.

## 6. Open questions

- **MCP authentication.** Early MCP servers often skip auth; production deployments need it. Standards are forming.
- **Tool discovery across machines.** When Runa runs on the Pi and tools live on the laptop, discovery / authentication / latency tradeoffs are real. Tailnet helps; doesn't solve.
- **Agent-to-agent MCP.** Runa, Sigrid, Hermes all exposing themselves as MCP servers to each other is a clean topology. Largely untested at production scale.
- **The right abstraction for Hirð over MCP.** Hirð retainers and MCP tools have similar shapes. Whether to merge the two abstractions or keep them distinct is open.

## 7. References (curated)

- modelcontextprotocol.io — MCP spec.
- anthropic.com/news/model-context-protocol — launch post.
- github.com/NousResearch/Hermes-Agent — Hermes.
- github.com/lobehub/lobe-chat — LobeChat.
- github.com/open-webui/open-webui — Open WebUI.
- github.com/BerriAI/litellm — LiteLLM.
- letta.ai — Letta.
- Memory references: `project_lobechat_setup.md`, `project_local_tts_stack.md`, `feedback_pi_resource_isolation.md`.
- Companion docs: [[11-autogen-multi-agent]] (the framework side), [[33-model-routing-ensembles]] (Heimskringla heart), [[37-plugin-sandboxing]] (MCP server isolation considerations).
