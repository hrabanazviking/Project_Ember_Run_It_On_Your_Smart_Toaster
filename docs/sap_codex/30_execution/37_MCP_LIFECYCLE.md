---
codex_id: 37_MCP_LIFECYCLE
title: MCP Lifecycle — Spawn, Heartbeat, Reconnect, Reap
role: Forge
layer: Execution
status: draft
sap_source_refs:
  - py/mcp_clients.py:24-80 (ConnectionManager)
  - py/mcp_clients.py:84-167 (McpClient)
  - py/mcp_clients.py:111-133 (connection monitor)
  - server.py:9201-9307 (process_mcp)
  - server.py:9309-9340 (remove_mcp)
  - server.py:806-855 (lifespan MCP init)
  - server.py:9391-9672 (built-in MCP servers: HA, ChromeMCP, SQL)
ember_subsystem_targets: [Smiðja, Brunnr]
cross_refs:
  - 30_execution/31_PYTHON_SERVER
  - 30_execution/38_EXTENSION_LIFECYCLE
  - 20_interface/20_MCP_INTEGRATION
---

# MCP Lifecycle

> *Connect, ping every 30 seconds, reconnect after every break, never give up. The MCP client is built like a labrador.*

Forge. Eldra. The Model Context Protocol is how SAP plugs in external tool servers. `py/mcp_clients.py` is **189 lines** total — the entire client implementation. Plus another ~600 lines in `server.py` for the lifecycle endpoints and the three built-in MCP servers (HomeAssistant, ChromeMCP, SQL). The total surface is small. The reconnect logic is the load-bearing piece.

## The Two Classes

`py/mcp_clients.py` has exactly two classes:

```python
# py/mcp_clients.py:24-80 (compressed)
class ConnectionManager:
    """Owns the AsyncExitStack and one MCP ClientSession."""
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.tools: list[str] = []

    @asynccontextmanager
    async def connect(self, config: dict):
        async with AsyncExitStack() as stack:
            # Transport selection: stdio, ws, sse, streamablehttp
            if "command" in config:
                # stdio: spawn subprocess
                server_params = StdioServerParameters(...)
                read, write = await stack.enter_async_context(stdio_client(server_params))
            else:
                mcptype = config.get("type", "ws")
                client_map = {"ws": websocket_client, "sse": sse_client, "streamablehttp": streamablehttp_client}
                client = client_map[mcptype](config["url"], headers=...)
                # ... handshake
            self.session = await stack.enter_async_context(ClientSession(read, write))
            await self.session.initialize()
            self.tools = [t.name for t in (await self.session.list_tools()).tools]
            yield self
```

The `AsyncExitStack` is the cleanup hammer. Every context manager opened inside (`stdio_client`, `ClientSession`) is registered, and unwinding the stack closes everything in reverse order — including killing subprocess MCPs. This is the right tool for the job. Without it, partial-failure cleanup would be a finally-block nightmare.

**Four transport types**: `command` (stdio subprocess), `ws` (WebSocket), `sse` (Server-Sent Events), `streamablehttp` (the newer MCP HTTP+SSE hybrid). SAP supports all four. The transport is selected by config — if the config has `command`, it's stdio; otherwise the `type` field decides.

Note the SSE handshake check at lines 64-72:

```python
# py/mcp_clients.py:64-73
if mcptype == "sse":
    try:
        with anyio.move_on_after(3):
            await read.receive()
    except anyio.EndOfStream:
        raise RuntimeError("SSE stream closed immediately")
    except Exception as e:
        raise RuntimeError(f"SSE initial handshake failed: {e}") from e
```

SSE is the trickiest transport — the server can accept the connection but never send anything, and the client would hang waiting. SAP does a non-blocking 3-second receive to verify the SSE server is actually talking. If the stream is empty after 3 seconds, the connection is considered failed. **Earned wisdom** — every SSE-using developer learns this trick the hard way.

## The Monitor Loop

```python
# py/mcp_clients.py:111-133 (heart of the client)
async def _connection_monitor(self) -> None:
    """持续重连逻辑：仅在一个协程里管理 AsyncExitStack"""
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

Three loops nested:
1. **Outer (`while not self._shutdown`)**: forever, until somebody calls `close()`.
2. **Connection lifetime (`async with ConnectionManager().connect(...)`)**: one connection's life. When this context exits — for any reason — the inner loop is dead.
3. **Heartbeat (`while not self._shutdown` inside)**: ping every 30 seconds, timeout at 3 seconds. If ping fails, break out of the heartbeat loop, which exits the `async with`, which closes the connection, which sends control back to the outer loop, which sleeps 5 seconds and reconnects.

This is **mature client design**. Three loops, each with a clear responsibility. The lock around `self._conn = conn` and `self._conn = None` is the only mutex, and it's only there to make `call_tool` (line 159) safe to call from outside.

The 30-second ping interval is reasonable. The 3-second ping timeout is aggressive but appropriate — if the server can't respond to a ping in 3 seconds, something is wrong. The 5-second post-failure sleep before reconnect is a debounce — protects against tight reconnect loops if the server is rejecting connects.

## The Lifespan Init: Concurrent and Bounded

```python
# server.py:807-855 (compressed)
mcp_init_tasks = []

async def init_mcp_with_timeout(server_name, server_config, timeout=6.0, max_wait_failure=5.0):
    if server_config.get("disabled"):
        return server_name, None, "disabled"

    mcp_client = mcp_client_list.get(server_name) or McpClient()
    mcp_client_list[server_name] = mcp_client
    failure_event = asyncio.Event()
    first_error = None

    async def on_failure(msg: str):
        nonlocal first_error
        if first_error: return
        first_error = msg
        settings.setdefault("mcpServers", {}).setdefault(server_name, {})["disabled"] = True
        mcp_client.disabled = True
        await mcp_client.close()
        failure_event.set()

    init_task = asyncio.create_task(mcp_client.initialize(server_name, server_config, on_failure_callback=on_failure))
    try:
        await asyncio.wait_for(init_task, timeout=timeout)         # 6s init timeout
        try:
            await asyncio.wait_for(failure_event.wait(), timeout=max_wait_failure)   # then 5s wait for failure callback
        except asyncio.TimeoutError:
            pass    # no failure in 5s; treat as success
        return server_name, (None if first_error else mcp_client), first_error
    except Exception as exc:
        return server_name, None, str(exc)
    finally:
        if not init_task.done(): init_task.cancel()

if settings.get('mcpServers'):
    mcp_init_tasks = [asyncio.create_task(init_mcp_with_timeout(k, v)) for k, v in settings['mcpServers'].items()]
    if mcp_init_tasks: asyncio.create_task(check_results())
```

This is the pattern I'd lift verbatim. Two timeouts: 6 seconds for the initial connect, 5 seconds for the failure callback to fire. If neither timeout fires, the MCP is considered ready. If either does, it's disabled in settings and removed.

The **fire-and-forget concurrent init** is what makes SAP feel snappy. The lifespan doesn't wait for MCPs — it spawns the init tasks and yields. The HTTP server is accepting requests within ~500 ms of process start; MCPs become available as they finish initializing. The renderer polls `/mcp_status/{id}` to know which ones are ready.

The same pattern is repeated in `process_mcp` (`server.py:9226`) for the runtime `POST /create_mcp` endpoint. Slightly different (uses 10-retry tool-fetch loop at lines 9281-9290 because `get_openai_functions` can return empty list while the session is still initializing), same shape.

## The Runtime Endpoints

| Endpoint | Function |
|---|---|
| `POST /create_mcp` (9202) | Add a new MCP server; runs `process_mcp` in background |
| `GET /mcp_status/{id}` (9215) | Returns `initializing` / `ready` / `failed: <msg>` / `not_found` |
| `DELETE /remove_mcp` (9309) | Remove an MCP from settings + close its client |
| `DELETE /remove_agent` (9357) | Remove an agent (separate from MCP servers) |

Simple CRUD. Status is text strings (`"ready"`, `"initializing"`, `"failed: <reason>"`, `"not_found"`) stored in a module-level dict `mcp_status` at line 9201. This is fine for single-user single-process; it does not survive a restart.

## The Three Built-In MCPs

SAP ships three pre-baked MCP server integrations at the route level:

### Home Assistant (`server.py:9391+`)

```python
@app.post("/start_HA")
async def start_HA(...):
    HA_client = McpClient()
    ...
```

A managed instance of `mcp-server-home-assistant` (npm package). SAP can start/stop it from the UI. The URL+token are stored in settings.

### ChromeMCP (`server.py:9454+`)

A managed MCP server that exposes Chrome (via CDP) as MCP tools. Different from SAP's own `cdp_tool.py` ([[34_BROWSER_AUTOMATION_LOOP]]) — this one exposes the user's *external* Chrome, not Electron's embedded webview. Starts via npm.

### SQL Server (`server.py:9577+`)

A managed MCP server for arbitrary SQL databases. Schema-introspecting; supports MySQL, Postgres, SQLite, MSSQL.

All three are spawned as separate `McpClient` instances with config dicts that name npm packages. SAP doesn't bundle them — it `npm install`s on first start via `node_runner.py`. Cold start time for any of the three is 5–15 seconds depending on npm cache.

## The Removal Path

```python
# server.py:9309-9340 (compressed)
@app.delete("/remove_mcp")
async def remove_mcp_server(request: Request):
    data = await request.json()
    server_name = data.get("serverName", "")
    current_settings = await load_settings()
    if server_name in current_settings['mcpServers']:
        del current_settings['mcpServers'][server_name]
        await save_settings(current_settings)
        settings = current_settings

        if server_name in mcp_client_list:
            mcp_client_list[server_name].disabled = True
            await mcp_client_list[server_name].close()
            del mcp_client_list[server_name]
        return JSONResponse({"success": True, "removed": server_name})
```

Three steps: remove from settings, mark client disabled, close client. The `close()` cancels the monitor task and unwinds the AsyncExitStack, which is what actually kills the subprocess (for stdio MCPs) or closes the WebSocket (for ws/sse MCPs).

There's a subtle issue: `mcp_client_list[server_name].disabled = True` is set *before* `await close()`. If `call_tool` is racing in another task, it may see disabled=True and refuse to call — but it may also have already started the call and be mid-await. The `_lock` in `call_tool` (line 160) prevents the race, but only if the caller is already past the lock acquisition. In practice this works because removals are user-initiated and synchronous from the user's POV; in heavy automation, a race window exists.

## Where It Breaks

- **Status strings as state**. The state machine is in string comparisons (`if status == "ready":`). No typed enum. Easy to typo a check; the test catches it only at runtime.
- **Empty-tools polling loop with no failure exit** (`server.py:9281-9290`): if the MCP session is live but `get_openai_functions()` keeps returning `[]`, SAP burns 10 retries × 0.5s = 5s of CPU and then declares ready. The 10-retry cap means a slow-tool-list MCP gets marked ready with an empty tool set, and the user wonders why the MCP "works" but has no tools.
- **No tool-count health check post-init**. If an MCP loses tools after init (server restarts and reports fewer tools), SAP doesn't notice until the next call fails.
- **Stdio MCP subprocess accumulation**. If `close()` doesn't actually terminate the subprocess (rare but happens — Python's subprocess cleanup is sometimes flaky on Windows), the process leaks. SAP has no zombie reaper.
- **The 30-second ping interval** means up to 30 seconds of "MCP is broken but I don't know yet" between heartbeats. Tool calls during that window will fail unexpectedly.
- **No per-MCP rate limiting**. If the LLM calls `mcp_tool_X` in a tight loop (say, batch-summarizing 1000 documents), SAP will dutifully forward every call to the MCP server. If the MCP server is rate-limited upstream, the failures cascade.
- **No version pinning** in `command`/`args` for stdio MCPs. The npm-based MCPs install latest by default. A backwards-incompatible upgrade silently breaks SAP's calls.

## Where It Surprises

- **189 lines for the whole client** is genuinely minimal. The `mcp` Python library does the heavy lifting; SAP just wires the lifecycle. Refreshing to read after the 11k-line server file.
- **The three-layer reconnect loop** is correct. I've reviewed dozens of MCP clients and most either have no heartbeat (the connection silently dies) or no debounce (reconnect storm). SAP has both.
- **The SSE 3-second handshake check** (line 67) is the kind of detail I'd bet 80% of MCP client implementations get wrong. The SSE protocol does not require the server to send anything immediately; many do, and most clients assume "no data in 3s = broken". SAP makes the same assumption, which is pragmatically right even if technically over-cautious.
- **The post-init 5-second "wait for failure" window** (line 832) is a non-obvious pattern. It treats the failure callback as authoritative even after the init coroutine returns. This catches MCPs that complete the initialize() call but then fail their own internal startup. Earned wisdom.
- **No MCP server inside SAP itself**. SAP is purely an MCP client; it does not expose itself as an MCP server. This is a missed opportunity (other agents could plug into SAP via MCP) and a design choice (SAP wants to be the entrypoint, not a sub-tool).

## Cross-References

- [[31_PYTHON_SERVER]] — where the route handlers live
- [[38_EXTENSION_LIFECYCLE]] — extension subsystem; similar lifecycle shape, different purpose
- [[20_MCP_INTEGRATION]] (Architect) — interface-level audit
- [[54_DEPENDENCY_HEALTH]] — npm-MCP version drift concern

## What This Means for Ember

**Adopt:**

- **The three-layer reconnect loop** verbatim: outer-shutdown / connection-lifetime / heartbeat. Apply to every long-lived external connection in Ember (MCP, IM bots, livestream adapters, knowledge-base subscriptions). Bind as a Funi-level utility: `class AutoReconnectingClient`.
- **The `AsyncExitStack`-as-cleanup-hammer pattern**. Any subsystem that opens multiple resources should use AsyncExitStack so failure-cleanup is structural, not manual.
- **The dual-timeout init** (6s init + 5s post-init failure window). Bind to Smiðja's tool-registry init.
- **The non-blocking fire-and-forget concurrent MCP init** during startup. The server is available immediately; tools become available as they finish loading. Pattern applies to any subsystem with N>1 instances of slow init.
- **The SSE 3-second handshake check**. Adopt for any SSE consumer in Ember.

**Adapt:**

- **String-based status** → typed enum: `MCPStatus(Enum) = {INITIALIZING, READY, FAILED, DISCONNECTED, DISABLED}`. SAP's strings work; types catch bugs.
- **The 10-retry empty-tools loop** → exponential backoff with a hard "MCP is healthy but reports zero tools" terminal state. Don't silently pretend zero-tools is ready.
- **The 30-second ping interval** → adaptive: faster when there's recent traffic, slower when idle. SAP's flat 30s is fine for desktop; Ember's federated party ([[6A_MULTI_AGENT_PARTY]]) needs faster fail-detection during high-engagement moments.

**Avoid:**

- **No tool version pinning** for npm-based MCPs. Ember's MCP config must require explicit version pins or content hashes. Vow tie-in: **Cache Discipline** (every external resource has a pinned reference).
- **No subprocess zombie reaper**. Ember must explicitly track spawned subprocess PIDs and reap on shutdown.
- **MCP-as-client-only**. Ember should expose its own MCP server surface so peer agents (other Embers in the federated party, external Hermes instances, Claude Desktop, etc.) can call Ember as a tool. Bidirectional MCP. Vow tie-in: **Federated Self**.
- **No per-MCP rate limiting**. Ember's MCP layer must include a token bucket per server, configurable per-deployment.

**Invent:**

- **Smiðja Tool Manifest Registry**. Every MCP server's tool list is hashed on connect; the hash is compared against a last-known-good. If the hash changes (server upgraded, tool set differs), the registry flags "MCP capability drift" to the operator. Vow tie-in: **Cache Discipline**.
- **Reconnecting Tool Capability Cache**. While an MCP is disconnected, calls to its tools return a typed `MCPUnavailable` error with `expected_recovery_time` based on past reconnect history. The LLM can use this to choose alternative tools or plan around the outage. SAP returns `None` and a log line; Ember should structure.
- **Federated MCP Mesh**. If Ember-on-laptop knows that Ember-on-Pi has a stdio MCP server (e.g. `home-assistant`), it can route MCP calls through the Pi's instance instead of spawning its own. Vow tie-in: **Federated Self**, **Modular Authorship**.
- **MCP Provenance Tags**. Every tool call records: which MCP, which session-id, which version-hash, which transport. Audit log retains for 30 days. Lets the operator answer "which MCP server returned this answer last Tuesday at 3pm?". SAP has no audit log; Ember should.
- **MCP-as-Brunnr-Backend**. The Well (Brunnr / Gungnir) exposes itself as an MCP server. Any agent — Ember or external — can query the Well via MCP. Bind the existing knowledge-base routes to a parallel MCP surface. Vow tie-in: **Tethered Grounding**.
