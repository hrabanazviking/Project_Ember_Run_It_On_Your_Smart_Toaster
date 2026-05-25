---
codex_id: 20_MCP_INTEGRATION
title: MCP Integration — Client and Server, with One Reconnect Monitor
role: Architect
layer: Interface
status: draft
sap_source_refs:
  - py/mcp_clients.py:1-189
  - server.py:371
  - server.py:11626
ember_subsystem_targets: [Munnr, Smiðja]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/19_TOOL_DOMAIN
  - 10_domain/12_AGENT_CORE_DOMAIN
  - 20_interface/22_A2A_INTERFACE
  - 60_synthesis/69_INTEGRATION_ROADMAP
---

# MCP Integration
## Client and Server, with One Reconnect Monitor

*— Rúnhild Svartdóttir, Architect*

> *A protocol that points both ways is a road. A protocol that points only one way is a downhill slide. SAP built a road but only paved one direction of it.*

SAP integrates with the Model Context Protocol (MCP) in two directions: as a *client* of external MCP servers (consuming their tools), and as a *server* publishing its own surface to external MCP clients. The two halves are unevenly developed — the client side is small, disciplined, and reconnect-aware; the server side is a single `mcp.mount()` line at `server.py:11626` whose underlying FastApiMCP integration we will dissect. This doc names the contract on both sides.

---

## 1. The Subject

**What MCP is to SAP:** the protocol by which SAP's agent can call tools served by *other* processes — Anthropic's reference servers, third-party MCP servers, custom MCP servers users register. Inversely, the protocol by which *other* AI agents can call SAP's tools as if SAP were itself a tool server.

**The contract surface:**

| Direction | Where it lives | Transport | Tool listing | Tool dispatch |
|---|---|---|---|---|
| **Outbound (client)** | `py/mcp_clients.py` (189 LOC) | stdio / websocket / SSE / streamable HTTP | `McpClient.get_openai_functions()` (line 136) | `McpClient.call_tool(name, params)` (line 159) |
| **Inbound (server)** | `mcp.mount()` at `server.py:11626` + FastApiMCP integration | Auto-derived from FastAPI routes | Auto-introspected from `@app.get/post(...)` route signatures | Direct route call |

The asymmetry is the load-bearing point of this interface: SAP wrote a real MCP *client*; SAP mounted a derivative MCP *server* on the existing FastAPI app without writing any new code.

---

## 2. How It Works

### 2.1 The outbound client — `py/mcp_clients.py`

The file is 189 lines and contains two classes: `ConnectionManager` (the per-MCP-server transport handler) and `McpClient` (the lifecycle wrapper with reconnect).

**Transport selection** at `ConnectionManager.connect` (line 29-78):

```python
# /tmp/super-agent-party/py/mcp_clients.py:32-53
if "command" in config:
    from mcp.client.stdio import StdioServerParameters
    server_params = StdioServerParameters(
        command=get_command_path(config["command"]),
        args=config.get("args", []),
        env=config.get("env"),
    )
    read, write = await stack.enter_async_context(stdio_client(server_params))
else:
    mcptype = config.get("type", "ws")
    if "streamable" in mcptype: mcptype = "streamablehttp"
    client_map = {
        "ws": websocket_client,
        "sse": sse_client,
        "streamablehttp": streamablehttp_client,
    }
    headers = config.get("headers", {})
    client = client_map[mcptype](
        config["url"], headers=headers
    ) if headers else client_map[mcptype](config["url"])
    transport = await stack.enter_async_context(client)
```

Four transports — stdio (for child-process MCP servers), WebSocket, Server-Sent Events, and the modern "streamable HTTP" — selected by config shape. The `get_command_path` helper (line 17-22) uses `shutil.which` with a fallback to `uv`, so `command: "ember"` resolves to either `/usr/local/bin/ember` or `/usr/local/bin/uv` if the literal command is absent. Defensive.

**SSE handshake validation** at lines 64-73:

```python
if mcptype == "sse":
    try:
        with anyio.move_on_after(3):
            await read.receive()
    except anyio.EndOfStream:
        raise RuntimeError("SSE stream closed immediately")
    except Exception as e:
        raise RuntimeError(f"SSE initial handshake failed: {e}") from e
```

SAP refuses to silently accept an SSE connection that closes immediately. Three-second timeout; explicit failure mode. This is the kind of paranoia [[hermes:HEM-20_MCP_INTEGRATION]] also exercises — both codexes converge on "validate the handshake."

**The reconnect monitor** at `McpClient._connection_monitor` (lines 111-133):

```python
async def _connection_monitor(self) -> None:
    while not self._shutdown:
        try:
            async with ConnectionManager().connect(self._config) as conn:
                async with self._lock:
                    self._conn = conn
                # 心跳检测
                while not self._shutdown:
                    try:
                        await asyncio.wait_for(self._conn.session.send_ping(), timeout=3)
                    except Exception:
                        break  # 断线，跳出 inner loop
                    await asyncio.sleep(30)
        except Exception as e:
            logging.exception("Connection failed, will retry: %s", e)
            if self._on_failure_callback:
                await self._on_failure_callback(str(e))
        finally:
            async with self._lock:
                self._conn = None
        if not self._shutdown:
            await asyncio.sleep(5)
```

This is **the single best small piece of code in the SAP codebase**. It is:
- A daemon task that owns the connection lifecycle.
- A 30-second ping heartbeat with 3-second timeout.
- A 5-second backoff between reconnect attempts.
- A `_on_failure_callback` hook for the registration site to be notified of degradation.
- An `_AsyncExitStack`-managed transport that cleans up correctly on cancellation.

It is also the *only* part of SAP that handles cross-process disconnection with this discipline. Compare to `py/live_router.py:170-205` (livestream `stop_live`) which is reactive — wait-for-stop-then-cancel — rather than proactive-reconnect.

**The tool wire format** at `get_openai_functions` (lines 136-157):

```python
return [
    {
        "type": "function",
        "function": {
            "name": t.name,
            "description": t.description,
            "parameters": t.inputSchema,
        },
    }
    for t in tools if t.name not in disable_tools
]
```

The MCP SDK's `Tool` objects (with `.name`, `.description`, `.inputSchema`) translate to OpenAI function-call shape. The translation is one-to-one. The optional `disable_tools` list lets the registration site veto specific tools (e.g. don't expose `mcp__shell` to a sub-agent that shouldn't have it).

### 2.2 The inbound server — `mcp.mount()` at `server.py:11626`

The mount is one line of Python. It assumes `mcp` is a `FastApiMCP` (or equivalent) wrapper imported earlier. The full chain:

1. SAP's FastAPI app exposes dozens of `@app.get`/`@app.post` routes for its various features (`/api/affection/*`, `/api/extensions/*`, `/api/live/*`, `/v1/chat/completions`, etc.).
2. The MCP server adapter walks the app, derives a tool *for each route*, and exposes them via the MCP protocol on the same FastAPI mount.
3. An external MCP client connecting to SAP gets a *very long tool list* — every API route becomes a callable tool.

The implication is that **SAP's inbound MCP surface is its full HTTP API**. There is no curation. A connecting MCP client can call `POST /api/extensions/install` (which downloads and executes Node code) as easily as `GET /api/uv/probe`. The same lack of authentication that applies to the localhost HTTP API applies to the MCP surface — connecting MCP clients are trusted by default.

### 2.3 The registration flow

`McpClient.initialize(server_name, server_config, on_failure_callback)` (line 95-100) is non-blocking — it spawns the monitor task and returns. The caller does *not* await connection; they call `get_openai_functions()` later and either get the tools (connected) or an empty list (not connected yet or disconnected).

`get_openai_functions` returns `[]` if `self._conn is None` (line 138-139) — the silent-empty pattern. This is consistent with Vow of Modular Authorship: a missing MCP server does not break tool composition, it just contributes nothing.

The list of configured MCP servers comes from `settings.mcpServers` (a dict; see `config/settings_template.json`); `server.py` reads the dict at startup, instantiates an `McpClient` per entry, calls `initialize`, and includes the resulting tools in the LLM-facing function list.

---

## 3. The Contract — Inputs, Outputs, Side Effects, Invariants

### 3.1 Outbound MCP — what SAP promises

**Inputs to an MCP server:**
- Tool name (string, must be in the server's `list_tools()` output)
- Tool params (dict, must match the tool's `inputSchema`)

**Outputs:**
- The MCP server's response, returned as-is from `call_tool` (line 164).
- On failure: a stringified error (`"Failed to call tool %s: %s" % (tool_name, e)`, line 167). **Not a structured error.**

**Side effects:**
- The MCP server is presumed to do whatever it wants on its side.
- SAP's connection monitor may log reconnect attempts (line 126).
- The optional `on_failure_callback` (line 127-128) may be invoked.

**Invariants:**
- One `_lock` per `McpClient` serializes connection state mutations (line 88).
- `_shutdown` is sticky — once set, the monitor exits and does not reconnect (line 113).
- The connection's `session` is the only valid call surface; `_conn.session` accessed without the lock is undefined (lines 137-138 guard with the lock).

### 3.2 Inbound MCP — what SAP exposes

**Inputs:**
- Whatever the FastApiMCP adapter derives from each route signature — typically Pydantic models as input schemas.

**Outputs:**
- The route's normal HTTP response, wrapped in MCP's `CallToolResult`.

**Side effects:**
- **Every side effect of every route is exposed.** Installing extensions, mutating settings, starting livestream listeners, dispatching to IM bots — all are reachable.

**Invariants:**
- **None enforced at the MCP boundary.** Whatever invariants the routes enforce are the only invariants on the MCP surface.

### 3.3 The leak

The **interface leak** is this: SAP's outbound MCP path validates handshakes, manages reconnects, and stringifies errors. SAP's inbound MCP path does *none* of those things — it inherits whatever the underlying FastAPI route does. The two halves of the same protocol are at very different discipline levels. An MCP client of SAP gets less rigor than SAP exhibits as a client of others.

---

## 4. Where It Breaks and Where It Surprises

### 4.1 No tool-call rate limit

`McpClient.call_tool` (line 159-167) has no rate limiting and no concurrency cap. A misbehaved LLM that calls `mcp__shell` 100 times in 5 seconds hits the upstream MCP server with 100 concurrent invocations. The MCP SDK's `ClientSession.call_tool` may serialize internally (depending on the transport); SAP does not enforce.

### 4.2 The single-string error envelope

The `"Failed to call tool %s: %s"` return on failure (line 167) loses the structured exception. A `TimeoutError` and a `PermissionError` look identical to the LLM, which cannot reason about either.

### 4.3 The auto-mount has no allowlist

`mcp.mount()` exposes every FastAPI route. There is no `mcp.mount(allowed_routes=[...])` config. Exposing only `/v1/chat/completions` and the read-only `/api/*` probes would be the right shape; SAP does not curate.

### 4.4 Authentication is inherited

The HTTP routes have no auth (localhost trust). The MCP routes inherit. A connection to SAP's MCP server from a non-localhost peer (which is possible if SAP is exposed via Tailscale or docker-compose with port forwarding) gets full access.

### 4.5 The reconnect monitor is per-client

Each `McpClient` has its own monitor task. For 10 configured MCP servers, that's 10 monitor coroutines, 10 ping loops, 10 reconnect schedulers. Lightweight, but uncoordinated — if all 10 servers reconnect-storm at the same time, no global backoff.

### 4.6 The crisp parts

- `_connection_monitor` — the best 23 lines in SAP.
- The four-transport selection.
- The SSE handshake validation.
- The lazy-empty `get_openai_functions` return.
- The `on_failure_callback` hook.
- The `disable_tools` veto.

---

## 5. Cross-References

- [[10_DOMAIN_MAP]] §1 row 13
- [[19_TOOL_DOMAIN]] for the tool registry that should consume MCP tools
- [[22_A2A_INTERFACE]] for the adjacent agent-to-agent protocol
- [[hermes:HEM-20_MCP_INTEGRATION]] for the Hermes MCP duality (which both publishes *and* consumes well)
- [[peer:LETTA-4_MCP]] for Letta's MCP surface
- [[60_synthesis/69_INTEGRATION_ROADMAP]] — MCP as the cross-codex bridge

---

## What This Means for Ember

**Adopt:**
- **`py/mcp_clients.py:111-133` (`_connection_monitor`) whole.** Lift verbatim; rename `McpClient` to `mcp_brunnr_link` or similar. This is the gold-standard reconnect daemon.
- The **four-transport selection** (stdio / WS / SSE / streamable HTTP). Ember's outbound MCP surface supports all four.
- The **SSE handshake validation** with named-timeout failure.
- The **`disable_tools` veto** at the consumer side — Smiðja's MCP integration can selectively whitelist or blacklist tools per Realm.
- The **`on_failure_callback` hook** for surfacing degradation to subscribers (becomes a Sögumiðla event in Ember).
- The **lazy-empty return** (`get_openai_functions` returns `[]` when disconnected) — Modular Authorship at the tool boundary.

**Adapt:**
- The **`mcp.mount()` auto-exposure of every route** — adapt to **curated MCP surface**: Munnr explicitly declares which capabilities are exposed via MCP. The list is in a manifest, reviewed at startup, audit-logged. No accidental exposure.
- The **stringly-typed error envelope** of `call_tool` — adapt to `ToolResult` (the typed shape proposed in [[19_TOOL_DOMAIN]] Invent). Errors include `error_type`, `error_message`, `retry_advisable`.
- The **per-client monitor** — adapt to a **federated monitor**: one supervisor task watches all MCP clients; coordinates reconnect schedules; enforces global backoff under widespread failure.

**Avoid:**
- **Auto-exposing every HTTP route as an MCP tool.** This is the worst pattern of the inbound side.
- **Authentication-inherited-from-localhost-trust** on a protocol that travels between processes (and possibly hosts).
- **No rate limit on `call_tool`.**
- **Stringified errors** that lose the exception class.

**Invent:**
- **The MCP Surface Manifest.** `munnr/mcp_surface.yaml` declares: which Ember capabilities are exposed via inbound MCP, with what input schemas, with what authentication requirements, with what rate limits, with what audit level. Funi reads the manifest at startup; refuses to mount routes not declared. SAP's `mcp.mount()` becomes a *typed, curated, signed* surface.
- **The MCP Channel Identity.** Every connecting MCP client identifies itself via a typed handshake (`client_name`, `client_purpose`, `client_capabilities`). Ember's MCP surface logs every connection; refuses connections that don't identify; revokes connections that misbehave. SAP trusts; Ember verifies.
- **Bidirectional MCP as the Realm Bus.** Two Ember Realms (e.g. main Ember + a sub-Realm extension) communicate via *paired* MCP sessions — Realm A is a server to Realm B and vice versa. This is the [[60_synthesis/62_PARTY_PROTOCOL]] foundation: federation by MCP rather than by HTTP or by raw sockets. The same protocol Ember uses to talk to external MCP servers it uses to talk to its own sub-Realms.
- **The MCP Reconnect Storm Brake.** If >50% of configured MCP servers are in reconnect-failure state, the federated monitor (see Adapt) raises a Sögumiðla alarm and *throttles* reconnect attempts to once per 30 seconds. This is the failure mode SAP cannot detect.
- **The Probe-on-Connect Capability Discovery.** When Ember connects to an external MCP server, it probes (a) the tool list, (b) the input schemas of each tool, (c) any version metadata. Logs the probe result. Diff-watches across reconnects — a tool that disappeared or changed schema raises a Sögumiðla alarm. SAP lists tools and trusts them stable; Ember tracks drift.
