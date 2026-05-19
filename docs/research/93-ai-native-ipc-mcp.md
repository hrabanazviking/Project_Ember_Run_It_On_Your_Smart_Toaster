# 93 — AI-Native IPC: Model Context Protocol Deep Dive

**Category:** AI Operating System
**Runa relevance:** integrations with Volmarr's tools, OWUI / Hermes connection, external plugin architecture
**Status:** Standards + architecture synthesis. Anthropic's MCP is the de-facto standard.
**Last touched:** 2026-05-17

---

## 1. Core idea

Inter-process communication (IPC) in a traditional OS connects processes via well-defined channels — pipes, sockets, shared memory. In an AI OS, IPC connects *agents to tools and services*: the LLM kernel makes structured calls to retrieval, code execution, file access, external APIs. Each integration historically required custom adapter code; the explosion of agent platforms in 2023–2024 created an interoperability problem analogous to early-internet protocol fragmentation. Anthropic's *Model Context Protocol* (MCP, released Nov 2024) is the most consequential standardisation attempt and has rapidly become the *de-facto* standard adopted across the industry.

For Runa, MCP is the *interoperability protocol* for everything outside her kernel. Tools that Volmarr or third parties build can expose themselves via MCP; Runa consumes them uniformly. Conversely, Runa herself can expose capabilities via MCP for other agents (Hermes, OpenClaw, Cursor, Claude Code) to consume. This is the OS-level *IPC + driver model* of the AI OS, and getting it right early avoids a generation of brittle one-off integrations.

## 2. Technical depth

**Model Context Protocol (MCP, Anthropic Nov 2024).**

The architecture has three pieces:

- *MCP servers*: processes that expose *resources* (read-only data) and *tools* (executable operations) and optionally *prompts* (template prompts the agent can use).
- *MCP clients*: processes that connect to MCP servers — typically the LLM application (Claude desktop, Cursor, agent runtimes).
- *Protocol*: JSON-RPC over stdio or HTTP+SSE. Messages typed; capabilities discoverable.

Server example: a filesystem MCP server exposes:
- Resources: `file://...` URIs the agent can read.
- Tools: `read_file(path)`, `write_file(path, content)`, `list_directory(path)`.
- Prompts: optional template prompts for filesystem tasks.

Client connects, discovers capabilities, the LLM can then call them.

**Why MCP took off.**

- *Standard*: industry consensus on the message format, capability discovery, capability/tool naming. Avoids the M×N integration explosion.
- *Local-first*: servers can run on the user's machine, exposing local resources without cloud dependency.
- *Composable*: a single client can connect to many servers; capabilities aggregate.
- *Anthropic-shepherded*: the protocol has clear stewardship and a versioning policy.
- *Open*: spec and reference implementations are public.

**MCP ecosystem (early 2026).**

- Anthropic Claude Desktop natively supports MCP.
- Cursor (IDE) supports MCP for code-context.
- Custom builds (Cline, Continue, OpenClaw, others) adopt MCP.
- A growing library of community MCP servers: GitHub, Google Drive, Slack, Postgres, Notion, file system, terminal, browser, more.

**Protocol primitives.**

```
        ┌──────────────────┐
        │ MCP CLIENT       │  initiates
        │  (LLM runtime)   │
        └────────┬─────────┘
                 │
                 ▼  initialize, list_resources, list_tools
        ┌──────────────────┐
        │ MCP SERVER       │
        │   resources      │
        │   tools          │
        │   prompts        │
        └────────┬─────────┘
                 │
                 ▼  read_resource, call_tool
        ┌──────────────────┐
        │ EXTERNAL SYSTEM  │
        │  (filesystem,    │
        │   API, database) │
        └──────────────────┘
```

Each tool call is a JSON-RPC request with typed parameters; the response is structured (success/error, content, mime-types).

**Transport options.**

- *stdio*: server runs as a child process; messages via stdin/stdout. Best for local tools.
- *HTTP+SSE*: server is a network service; messages via HTTP with Server-Sent Events for streaming. Best for remote services.

**Security model.**

MCP servers have full access to whatever the user grants them; the client mediates. Capability-based-security ([[95-capability-based-security]]) still applies: a server that *can* delete files needs explicit user / kernel approval to do so. The client is responsible for gating.

**Non-MCP IPC alternatives.**

- *OpenAI function calling*: a tool format coupled to OpenAI's API; less portable.
- *LangChain tool format*: framework-specific.
- *Direct HTTP / REST*: ad-hoc; works but no standard discovery.
- *Custom RPC*: bespoke; the M×N problem.

MCP is increasingly the lingua franca; others are legacy or framework-bound.

**Beyond MCP — AAIF.**

Some industry actors are exploring *Agent-Agent Interaction Framework* (AAIF) and similar protocols specifically for *agent-to-agent* communication (vs. agent-to-tool). This is a frontier; MCP handles agent-to-tool; agent-to-agent is less standardised. For Runa, agent-to-agent matters when she interacts with Hermes, OpenClaw, etc.

## 3. Key works

- **Anthropic.** *Model Context Protocol Specification.* 2024. Open at `modelcontextprotocol.io`.
- **Anthropic.** *Introducing the Model Context Protocol.* Nov 2024 announcement.
- **MCP Reference servers** — open-source library of common servers (filesystem, git, GitHub, etc.).
- Companion to Volmarr's projects:
  - **Hermes Agent** (Nous Research): exposes itself via OpenAI-compatible API; can be wrapped as MCP server.
  - **OpenClaw**: maintains its own skill protocol; MCP bridging possible.
- **Tanenbaum, A. S.** *Distributed Systems.* For the IPC theory baseline.

## 4. Empirical results

This is largely a *standards adoption* story rather than empirical performance:

- MCP server / client implementations are correct and stable; the protocol works.
- Adoption across major IDEs and agent platforms within a year of release — fastest standardisation in recent AI tooling history.
- Latency: stdio MCP calls add ~1-5ms; HTTP+SSE adds ~10-100ms depending on network.
- Failure modes documented: server crashes (need restart policy in client), capability spoofing if servers untrusted, version mismatches.

## 5. Applicability to Runa

For **Runa's external integrations**:

- All Runa's external tool integrations should be MCP-mediated by default.
  - Filesystem access → official filesystem MCP server.
  - Git operations → git MCP server.
  - Web search / fetch → web MCP server (Brave Search, Firecrawl, etc.).
  - Volmarr's project files → bespoke MCP server exposing his repo structures.

For **Runa as MCP server** (forward-looking):

- Expose Runa-capabilities for other agents to consume:
  - `recall(query)` → retrieve from Muninn.
  - `consult_runa(question)` → ask Runa as an oracle.
  - `narrative_excerpt(timeframe)` → quote from Saga.
- Other Volmarr agents (Hermes, OpenClaw, Sigrid) connect as MCP clients and consume.
- This is the *interoperability* layer of Volmarr's broader AI ecosystem.

For **OWUI integration**:

- OWUI (Open WebUI) is Volmarr's chat frontend, configured to talk to Hermes and to TTS. Adding Runa as a backend involves either:
  - OWUI's standard OpenAI-compatible API protocol (works today).
  - Custom MCP-based integration (richer, future).

For **Hermes / OpenClaw bridges**:

- A bridge layer translates between Runa's MCP exposure and Hermes / OpenClaw native protocols. Bridge code is small and well-localised.

For **Mythic Vibe CLI** (Volmarr's other plugin/CLI project):

- Already supports MCP; Runa-as-MCP-server would directly integrate.

For **capability discovery**:

- MCP's `list_tools` and `list_resources` are introspectable. Volmarr can `mcp list runa` and see what Runa exposes.
- Heimskringla maintains a registry of connected MCP servers and their capabilities.

For **versioning and stability**:

- MCP is versioned. Runa pins to specific MCP server versions; upgrades are deliberate.
- Per RULES.AI.md: cross-platform. MCP transports (stdio, HTTP) are platform-portable.

For **security**:

- Per-server capability scoping. Some MCP servers may be high-trust (filesystem, git); others lower-trust (web search). The kernel mediates which servers can be called for which tasks.
- Audit log: every MCP call logged with parameters and result-summary.

What to avoid:

- **Bespoke IPC where MCP would work.** The cost of standardisation is small; the long-term integration tax of bespoke is huge.
- **Trusting untrusted MCP servers.** They run with user-level permissions; treat with appropriate caution.
- **Coupling Runa's kernel to specific MCP servers.** The kernel uses abstract tool-call interfaces; specific servers are configuration.
- **Skipping discovery.** Don't hardcode tool names; use `list_tools` and adapt.

## 6. Open questions

- **Agent-to-agent extension of MCP.** Whether MCP grows to handle agent-to-agent or stays tool-shaped. AAIF and adjacent work targets the gap.
- **Performance at scale.** Many concurrent MCP servers may saturate; production observations are early.
- **Authentication and authorisation.** MCP's current model is local-trust; remote/multi-user scenarios need more.
- **Server discovery beyond config.** A registry / marketplace of MCP servers exists in nascent form.
- **Streaming and long-running calls.** SSE handles streaming responses; long-running tool calls need lifecycle support.

## 7. References (curated)

- Anthropic MCP specification (current). At `modelcontextprotocol.io`.
- Anthropic's introductory post (Nov 2024).
- MCP reference servers repo on GitHub.
- Tanenbaum & van Steen, *Distributed Systems.* For the IPC theory baseline.
- Companion docs: [[37-plugin-sandboxing]], [[50-local-agent-orchestration-mcp]], [[83-agentic-foundation-models-2025]], [[91-ai-os-architecture]], [[95-capability-based-security]].
