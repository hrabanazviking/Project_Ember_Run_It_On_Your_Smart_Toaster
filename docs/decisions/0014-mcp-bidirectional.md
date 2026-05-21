# ADR-0014 — Bidirectional MCP Integration

**Status:** Accepted, 2026-05-21 — Phase 18 of slice-2-extended (post-ratification feature).
**Date:** 2026-05-21
**Deciders:** Volmarr Wyrd; Mythic-Engineering session.

## Context

Ember has a working first-party tool framework (ADR-0011) with three
tools (`search_well`, `read_local_file`, `fetch_url`). The Model Context
Protocol (MCP) — Anthropic's standard for AI-to-tool-server
communication — has reached 1.0 and a working Python SDK exists at
`mcp 1.27.1`.

Two distinct integrations are possible:

1. **Ember as MCP *client*** — Ember spawns external MCP servers and
   surfaces their tools to Funi alongside the first-party ones.
   Operators get an open ecosystem of tools (filesystem, GitHub,
   Postgres, fetch, custom plugins) without Ember bloating.
2. **Ember as MCP *server*** — Ember exposes its own capabilities
   (Well search, ingest, doctor, status) to other MCP clients. Claude
   Desktop, Claude Code, and other agents can query the operator's
   Well and use Ember's tooling.

Both fit the Vows:

- **Smallness** — MCP is an *optional extra*, not a core dep. Operators
  who don't want MCP install `pip install ember-agent[sqlite_vec]` and
  never touch it. Operators who do: `pip install ember-agent[mcp]`.
- **Sovereignty** — MCP tools follow the same approval policy as
  first-party tools. Default PER_CALL. Operator opts in to STANDING
  per-tool via `auto_approve` in config. Server-side exposure is
  opt-in via `mcp.expose_self`.
- **Pluggable Storage** / **Modular Authorship** — MCP slots into the
  existing tool registry the same way `search_well` does. No special
  case in the chat loop.
- **Tetheredness** — when an MCP server crashes or is unreachable, its
  tools become typed `NO_SUCH_TOOL` outcomes; the chat loop continues.
  Same contract as Brunnr disconnect.

## Decision

Ship both client and server as `src/ember/mcp/` package, gated behind
`config.mcp.enabled = true` for client and `mcp.expose_self = true`
for server. Both gated additionally behind `[mcp]` pip extra
(missing-extra → typed config error at startup, not crash).

### Architecture

```
src/ember/mcp/
├── __init__.py
├── README_AI.md
├── INTERFACE.md
├── runner.py            # async-event-loop-in-a-thread bridge
├── client.py            # MCPClientPool — manages multiple stdio servers
├── bridge.py            # bridges MCP tools into ember.spark.funi.tools
└── server.py            # FastMCP wrapper exposing Ember's capabilities
```

### Naming

MCP tools registered into Ember's tool registry use the convention:
```
mcp__<server_name>__<tool_name>
```
This matches Claude Code's MCP naming convention and prevents collisions
between MCP servers and first-party tools.

### Approval

Per ADR-0011 §2.4. Default for any MCP tool is `PER_CALL` (operator
approves each invocation). Operators can list specific tool names
under `MCPServerSpec.auto_approve` to lift them to `STANDING`. Operators
can use `tools.approval_overrides` (existing) to set per-tool policy.

The `FORBIDDEN` policy can be applied to a specific MCP tool to refuse
it entirely (registry refuses to register, ADR-0011 §2.4).

### Audit

Audit log records get an additional `mcp_server` field when the tool
came from an MCP server. The existing audit log fd/path/format are
unchanged.

### Transports — V1 scope

**V1 (this ADR):** stdio only, both sides. JSON-RPC over the spawned
subprocess's stdin/stdout — the canonical MCP transport. No network
auth needed; trust is process-level.

**Deferred to V2:**
- `streamable-http` transport (network-served MCP)
- `sse` transport (legacy)
- WebSocket transport
- HTTP auth (bearer tokens, OAuth2)

The `mcp` SDK supports all transports; V1 just doesn't surface them in
Ember's config schema. Adding them in V2 is a config-only extension.

### Async-to-sync bridge

The MCP client SDK is `asyncio`-based. Ember is synchronous everywhere
else. We bridge with a dedicated event-loop thread:

- `MCPRunner` owns one `asyncio` event loop running in a daemon thread
- All `ClientSession` objects live in that loop
- Sync code submits coroutines via `asyncio.run_coroutine_threadsafe(...)` and `.result()`
- One runner, many sessions. Single-thread Python's GIL makes this safe.

The FastMCP server side handles its own event loop via `mcp.run()`;
the `ember mcp serve` subcommand simply calls that and blocks until
SIGINT.

### Server-side: what Ember exposes

Tools (V1):
- `search_well(query: str, k: int = 5)` — RRF hybrid search over the Well
- `well_status()` — `BrunnrStats` as JSON
- `doctor()` — health report (Funi/Strengr/Brunnr probes)
- `recent_episodes(limit: int = 10)` — last N chat episodes

Resources (V1):
- `ember://well/status` — Well stats as a resource
- `ember://well/recent-episodes` — recent episodes feed

Deferred:
- `ingest_path(path: str)` — needs careful approval-model design; ingest is high-cost
- `chat_once(message: str)` — would need full Funi flow; nontrivial async
- Resource subscription / change notifications

### CLI

```
ember mcp list           # list configured MCP servers + their state
ember mcp tools          # list all tools (Ember's first-party + MCP)
ember mcp ping [<server>] # health-probe configured MCP servers
ember mcp serve [--transport stdio]  # run Ember as MCP server
```

### Config shape (additive to `EmberConfig`)

```yaml
mcp:
  enabled: true                   # turn on MCP client
  expose_self: false              # turn on Ember-as-MCP-server (default off)
  startup_timeout_s: 10.0
  call_timeout_s: 30.0
  servers:
    - name: filesystem
      command: npx
      args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/me/notes"]
      auto_approve: []            # default: every tool requires PER_CALL
    - name: github
      command: docker
      args: ["run", "-i", "--rm", "-e", "GITHUB_TOKEN", "ghcr.io/github/github-mcp-server"]
      env:
        GITHUB_TOKEN: "${GITHUB_TOKEN}"
      auto_approve: ["search_repositories"]
```

## Consequences

### Positive

- **Open tool ecosystem** — operators add capabilities without Ember
  changes. Plugin model.
- **Ember becomes addressable** — Claude Desktop / Claude Code / any
  MCP client can query the operator's Well.
- **Vow alignment** — opt-in, gated by extras, approval-defaulted-safe.
- **Audit symmetry** — MCP calls audit-logged the same as first-party
  tools.
- **No core bloat** — `[mcp]` is opt-in; default `pip install
  ember-agent[sqlite_vec]` doesn't pull `anyio`, `pydantic`, `starlette`,
  `uvicorn`, etc.

### Negative

- **Dependency surface grows** under `[mcp]` extra: `anyio`, `httpx`,
  `httpx-sse`, `jsonschema`, `pydantic`, `pydantic-settings`, `pyjwt`,
  `python-multipart`, `sse-starlette`, `starlette`, `typing-inspection`,
  `uvicorn`. ~12 deps. All well-maintained.
- **Async-in-thread complexity** — the sync/async bridge is one more
  thing to test. Mitigated by `MCPRunner` being a small focused class.
- **Subprocess lifecycle** — spawned MCP servers can crash, hang, leak
  fds. Mitigated by per-call timeouts and explicit shutdown on chat exit.
- **MCP server crashes during chat** — V1 treats this as "tools from
  that server become NO_SUCH_TOOL"; no auto-reconnect. V2 should add
  backoff-retry.

### Risks

- **Operator types `auto_approve: ["*"]`** thinking it's a wildcard.
  V1: literal name match only. Future: explicit wildcard syntax.
- **MCP server attempts to read the entire Well via a resource list.**
  Ember's exposed resources are deliberately small (status + recent
  episodes). The Well itself is queryable via `search_well` (with `k`
  cap) but not enumerable.
- **`ember mcp serve` over stdio could be confused with `ember chat`**
  if operator's MCP client expects different transport. The subcommand
  prints a one-line "Ember MCP server starting on stdio" to stderr
  (not stdout — stdout is the JSON-RPC channel).

## Alternatives considered

- **`langchain.tools` / OpenAI function calling format only** — would
  lock Ember to one ecosystem. MCP is the cross-vendor standard.
- **Build a custom JSON-RPC layer** — re-implementing MCP would violate
  Smallness and Modular Authorship; the `mcp` SDK is the right
  level of abstraction.
- **Skip server-side; only client** — was option B in the scoping
  question. User chose client + server; bidirectional integration
  is materially more useful.

## Migration notes

None — this is an additive feature. Operators who don't set
`mcp.enabled: true` see no change. Configs without an `mcp:` section
get the default (all-off) MCPConfig.

## References

- MCP specification: https://modelcontextprotocol.io/specification
- MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk
- Anthropic MCP announcement: https://www.anthropic.com/news/model-context-protocol
- ADR-0011 (tool-use framework) — MCP tools register through this registry
- ADR-0007 §2.2 (typed-value-over-exception) — MCP failures are typed
- ADR-0013 §6 (slice-2 open questions) — superseded for this question
