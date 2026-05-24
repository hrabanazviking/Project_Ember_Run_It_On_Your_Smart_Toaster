---
codex_id: 20_MCP_INTEGRATION
title: MCP Integration — How Hermes Is Both Client and Server
role: Cartographer
layer: Interface
status: draft
hermes_source_refs:
  - mcp_serve.py:1-897
  - mcp_serve.py:50-55
  - mcp_serve.py:62-115
  - mcp_serve.py:196-444
  - mcp_serve.py:450-859
  - mcp_serve.py:866-898
  - agent/transports/hermes_tools_mcp_server.py
  - acp_adapter/server.py:1-200
ember_subsystem_targets: [Munnr, Strengr, Funi, Brunnr]
cross_refs:
  - 20_interface/21_RPC_INTERFACE
  - 20_interface/22_SKILL_INTERFACE
  - 60_synthesis/60_HERMES_VS_EMBER_CROSSWALK
  - 60_synthesis/61_TRUE_NAME_REASSIGNMENT
  - 60_synthesis/63_INTEGRATION_PATHS
  - 30_execution/31_CROSS_PLATFORM_TACTICS
---

# 20 — MCP Integration: How Hermes Is Both Client and Server

> *I walk the road in both directions and notice that the same stones serve as steps in either case.*
> — Védis Eikleið, on roads that point both ways

## 1. The shape of the road

Hermes's relationship to the Model Context Protocol (MCP) is not a single line; it is a forked one. The same agent that **consumes** MCP servers (through tools dispatched into its `agent/transports/` and `tools/mcp_tool.py` pipelines) also **publishes** an MCP server of its own (through `mcp_serve.py`, 897 lines of careful exposure). Most AI agents treat MCP as a one-way socket: I am the agent, that is the tool server, the bytes flow this way. Hermes treats it as a thoroughfare. Outbound: it pulls in conversations, file readers, browser controllers, and whatever an `optional-skills/mcp/` SKILL.md happens to wire. Inbound: it lets *another* MCP client — Claude Code, Cursor, Codex, a custom agent — reach across the stdio boundary and operate Hermes's accumulated messaging surfaces (Telegram, Discord, Slack, Signal, Matrix, WhatsApp, more) as if they were tools.

This duality is rare. It is also the most directly useful thing Hermes can teach Ember about the realm we will call **the mouth that hears as well as speaks** — Munnr, plus enough of Strengr to make MCP traversal honest about disconnection.

The MCP server file is `mcp_serve.py`. The MCP SDK is loaded **lazily** with a try/except (`mcp_serve.py:50-55`):

```python
_MCP_SERVER_AVAILABLE = False
try:
    from mcp.server.fastmcp import FastMCP
    _MCP_SERVER_AVAILABLE = True
except ImportError:
    FastMCP = None  # type: ignore[assignment,misc]
```

If the `mcp` package is not installed, importing this module does not raise — the server simply refuses to start with a clean message at `mcp_serve.py:866-875`. That pattern is unusually disciplined for a 31 KB file in a 662 KB CLI ecosystem, and it will be load-bearing for Ember's [[60_synthesis/61_TRUE_NAME_REASSIGNMENT]] proposal: lazy optional surfaces are how Munnr keeps its Vow of Modular Authorship while still claiming MCP capability.

## 2. The ten tools Hermes exposes

`create_mcp_server()` at `mcp_serve.py:450` registers ten tool decorators via `@mcp.tool()`. These are the contract Hermes publishes to any MCP client. Read them as the API a co-agent would see:

| Tool name | Source line | What it does | Why Ember should care |
|---|---|---|---|
| `conversations_list` | 471 | List active conversations across platforms with session keys | Munnr's session catalog needs a peer surface |
| `conversation_get` | 528 | Detailed info for one conversation | Same |
| `messages_read` | 561 | Read recent messages from a conversation | Brunnr's read-shaped reflection |
| `attachments_fetch` | 618 | List non-text attachments from a message | Smiðja-adjacent; multimodal hint |
| `events_poll` | 670 | Poll for new events since a cursor | Strengr's async surface |
| `events_wait` | 699 | Long-poll, blocks until event arrives | The hidden gift; see §5 |
| `messages_send` | 733 | Send a message to a platform conversation | The write half of mouth-as-server |
| `channels_list` | 769 | List available send targets across platforms | Discoverability without coupling |
| `permissions_list_open` | 823 | Pending approval requests | The audit half of [[20_interface/23_PROVIDER_INTERFACE]] meets Munnr |
| `permissions_respond` | 839 | Respond allow-once / allow-always / deny | The most consequential of the ten |

Each is a thin function decorated with `@mcp.tool()` — that decorator (from `mcp.server.fastmcp`) introspects the type annotations, builds the JSON schema, and registers the callable as an MCP-discoverable tool. The result is that *the source code's type hints are the wire contract*. There is no second representation. This is a pattern Ember should preserve verbatim if she adopts MCP: a typed Python signature is the source-of-truth schema, and discovery happens by reflection, not by a parallel YAML file.

## 3. The dispatcher's quiet defense

Look closely at `_coerce_int` at `mcp_serve.py:118-134`:

```python
def _coerce_int(value, *, default: int, minimum: int, maximum: int) -> int:
    try:
        coerced = int(value)
    except (TypeError, ValueError):
        coerced = default
    return max(minimum, min(coerced, maximum))
```

This three-line helper is called at every tool boundary that accepts a numeric argument (`limit`, `timeout_ms`, `after_cursor`). It exists because **MCP clients are untrusted across the protocol boundary**. The decorator might enforce types in the happy case, but a malformed call — a string where an int was expected, a negative number, a number so large it overflows a list slice — still arrives at the function body. Hermes refuses to crash; it coerces, clamps, and continues. This is Vow-of-Modular-Authorship behaviour as a one-liner: the MCP surface stays standing when the client misbehaves.

Ember's Munnr does the same thing in its own way today (typed `Disconnected` / `Unavailable` values flow through every realm boundary, per §11 of `SYSTEM_VISION.md`). The lesson here is **the principle is symmetrical**: the realm boundary toward an MCP *peer* needs the same coercion discipline as the boundary toward an unreachable Well. Hermes wrote `_coerce_int` once; Ember should write the equivalent once.

## 4. The EventBridge: how the server stays awake

The most architecturally interesting class in `mcp_serve.py` is `EventBridge` (lines 196-444). It is what makes `events_poll` and `events_wait` more than polite fiction. The bridge:

1. Starts a daemon thread on `bridge.start()` that **polls SQLite** (the SessionDB at `~/.hermes/state.db`) every 200 ms.
2. Uses **mtime caching** on `sessions.json` and `state.db` (lines 352-376) so the poll is essentially free when nothing has changed:
   ```python
   if db_mtime == self._state_db_mtime and sj_mtime == self._sessions_json_mtime:
       return  # Nothing changed since last poll — skip entirely
   ```
3. Maintains an in-memory event queue (`QUEUE_LIMIT = 1000` at line 191) with a cursor that lets clients resume after disconnect.
4. Supports **long-poll** via `wait_for_event` (line 268): the client says *"wake me when there's news, up to 30 seconds"*, and the bridge uses `threading.Event.wait()` to block efficiently instead of busy-looping.

This is the SQLite-as-event-bus pattern, the same pattern Ember already uses for her audit log (per `EMBER_SECOND_SLICE_PLAN.md` Phase 11). Hermes proves it scales to **inter-process** event propagation when the consumer is an MCP client. Two implications for Ember:

- **Brunnr's SQLite backend already has the substrate.** Adding an mtime-keyed change feed to `BrunnrHandle` would let a Munnr MCP server emit `events_*` tools without coupling Brunnr to event-bus middleware. A `last_modified_at` column plus a daemon polling `Path.stat().st_mtime` is the entire mechanism — no Redis, no RabbitMQ, no PubSub. The Vow of Smallness survives.
- **The poll interval is configurable but defaults to 200 ms.** On a Pi 5 this is ~5 fstat() syscalls/second, costing single-digit microseconds. The mtime-skip path means real work happens only on real change. Ember inherits this efficiency naturally because she is already SQLite-first.

## 5. Inbound vs outbound: where MCP enters Hermes the other way

The flip side — Hermes-as-client — does not live in `mcp_serve.py`. It lives in:

- `tools/mcp_tool.py` — declares a generic MCP tool that the agent loop can dispatch.
- `agent/transports/hermes_tools_mcp_server.py` — bridges between transports and MCP.
- `optional-skills/mcp/fastmcp/SKILL.md` and `optional-skills/mcp/mcporter/SKILL.md` — skill-level guides for *building* MCP servers from inside Hermes.
- `agent/tool_dispatch_helpers.py:90-100` — the `_is_mcp_tool_parallel_safe` check, which knows that MCP tools opt into the parallel-batch concurrency model only when their *server* advertises it.

Here is the subtle bit. The parallel-safety question for an MCP tool is **not whether Hermes thinks it's safe**; it's whether the *MCP server* announced parallel-call safety in its capabilities response. Hermes asks, the server answers, the dispatcher routes. This is the third-party-trust posture Ember will need when she gains MCP clientship: not "I assume tools are safe to parallelise" but "I ask the server and respect the answer."

## 6. The ACP cousin: another bidirectional pattern worth seeing

Look briefly at `acp_adapter/server.py:1-200`. ACP (Agent Client Protocol) is a sister protocol with similar bidirectionality. Hermes serves as an ACP agent — Zed editor and similar tools speak ACP to it. The schema imports at lines 19-63 reveal the contract surface: `AgentMessageChunk`, `ToolStart`, `ToolComplete`, `PromptCapabilities`, `SessionInfo`, `AvailableCommandsUpdate`. This is `mcp_serve.py`'s shape projected onto a different protocol family.

For Ember, the takeaway is **the abstraction is not "MCP server"; it is "Munnr publishes a structured peer surface."** Whether the wire is MCP, ACP, gRPC, or a future protocol that has not been named yet, the *thing* is the same: a typed conversation between Munnr and an external co-agent, with discoverable tools, event streams, and approval routing. Hermes wrote it twice because both protocols mattered. Ember can write it once and adapt — or write it once for MCP only, because MCP is the present-day winner of the ecosystem race (per the AI-OS Research corpus the Architect inherited).

## 7. Permissions: the part Ember's Vow of Honest Memory cares about

The two `permissions_*` tools at `mcp_serve.py:823-857` are the only ones that mutate authorisation state. The bridge maintains `_pending_approvals: Dict[str, dict]` (line 221), which gets populated by external observation of the gateway's approval lifecycle. When the MCP client calls `permissions_respond(id, decision)`, the bridge records the decision and enqueues an `approval_resolved` event for any other waiting clients.

This is **distributed approval routing** — multiple MCP clients can observe and resolve approvals against the same Hermes instance. Critical detail at line 850: only three decisions are accepted: `allow-once`, `allow-always`, `deny`. Anything else returns a structured error, not a crash. The three-value vocabulary matches Ember's existing tool-approval policy in ADR 0011 (`tools.example.yaml` documents the same trichotomy). The vocabulary is portable; the routing is the new thing.

## 8. The transport layer — `mcp_serve` over stdio

The whole MCP server runs over **stdio** by default. `run_mcp_server()` at `mcp_serve.py:866-898` shows the pattern:

```python
bridge = EventBridge()
bridge.start()
server = create_mcp_server(event_bridge=bridge)
import asyncio
async def _run():
    try:
        await server.run_stdio_async()
    finally:
        bridge.stop()
try:
    asyncio.run(_run())
except KeyboardInterrupt:
    bridge.stop()
```

Stdio is the lowest-friction transport. It works on every operating system Hermes (and Ember) target. It does not require an open port. It does not need a TLS certificate. The MCP client (Claude Desktop, Cursor) launches Hermes as a subprocess and reads/writes JSON-RPC frames over its pipes. The bridge thread runs in parallel with the MCP server's event loop. On `KeyboardInterrupt` or normal exit, the bridge is stopped cleanly.

This is the **cross-platform default** Ember already chose for her own internal RPC (per [[20_interface/21_RPC_INTERFACE]]). The agreement is not coincidence — stdio is the only IPC transport that is trivially portable from Windows to Pi to Android (under Termux). Anything richer (Unix sockets, named pipes, TCP loopback) introduces platform-specific corner cases that Hermes deliberately avoids in this file.

## 9. What is *not* in `mcp_serve.py`

Equally important is what the file *does not* try to do:

- No HTTP transport. (FastMCP supports one; Hermes does not register it here.)
- No SSE (Server-Sent Events). (ACP has one; MCP supports one; this file ignores both.)
- No authentication on the MCP boundary itself. (The boundary's trust comes from being a subprocess of the MCP client — if you can launch the binary, you have access.)
- No multi-tenancy. (One MCP server per Hermes installation; one HERMES_HOME per server.)
- No HTTP-style middleware chain. (Just decorators on functions.)

Each absence is a Vow-compatible choice. HTTP transport would require port allocation, firewall negotiation, and TLS — none of which a Pi-class Ember can afford to demand. SSE would require an HTTP server. Auth-on-MCP would require credential rotation, which is `agent/credential_pool.py`'s problem and shouldn't leak into Munnr. Multi-tenancy is a non-goal for Ember's small-and-tethered shape.

## 10. Lessons distilled

1. **MCP server = lazy optional surface.** Refuse to depend on `mcp` at import time. Ship the integration as `pip install ember-agent[mcp]`.
2. **Type hints = wire schema.** FastMCP introspects signatures; do not maintain a parallel declaration.
3. **Coerce-and-clamp at every tool boundary.** Coerce, do not raise, on type mismatch.
4. **mtime-skipped SQLite polling is the event bus.** No Redis, no broker. Brunnr's existing substrate suffices.
5. **Long-poll, not busy-poll.** `threading.Event.wait()` with `timeout=min(remaining, POLL_INTERVAL)` is enough.
6. **Three-value approval vocabulary.** `allow-once` / `allow-always` / `deny`. Reuse Hermes's vocabulary verbatim — it matches Ember's ADR 0011.
7. **stdio first; everything else later.** The default transport works on every Ember target platform with zero configuration.
8. **Bidirectional means *peer*.** When Ember can both consume and publish MCP, she becomes a node in a larger ecosystem rather than a leaf.

## What This Means for Ember

**True Names affected:**

- **Munnr (mouth).** Today Munnr is the CLI surface — REPL and `ember chat`. Hermes proves that Munnr can publish a *programmatic* surface (MCP server) without changing what it means. The mouth that speaks to a human and the mouth that speaks to a peer agent are the same mouth, just on different channels. A new module `src/ember/spark/munnr/mcp/` would host the FastMCP server, gated by an opt-in `[mcp]` extra in `pyproject.toml`. It would expose `conversations_list`, `messages_read`, `events_poll`, `events_wait`, `permissions_list_open`, `permissions_respond` — the *honest* subset that maps to Ember's existing capabilities. `messages_send`, `attachments_fetch`, and `channels_list` would wait for the gateway-shaped True Name proposed in [[60_synthesis/61_TRUE_NAME_REASSIGNMENT]] (working name: **Gjallarhorn**, the announcing horn).
- **Strengr (cord).** The MCP server is itself a tether — to a peer agent process. The graceful-offline contract extends naturally: if Hermes loses its session DB, the bridge returns `null` events; if Ember loses Brunnr, the bridge returns the typed `Disconnected` value as an event payload, *not* a stack trace. Strengr already handles this on the outbound side; we extend the same discipline inbound.
- **Funi (flame).** Funi's tool dispatch needs the symmetric counterpart — Ember as MCP *client*. This is a Funi-adjacent concern because tools are dispatched through Funi's loop. A `funi/tools/mcp_client.py` would be the new home, parallel to existing first-party tools.
- **Brunnr (well).** No structural change required. The mtime-poll pattern that the bridge uses already works against Brunnr's SQLite backend; Brunnr's pgvector backend would need a NOTIFY/LISTEN equivalent if we ever wanted server-side events without polling, but this is post-Vow scope.

**Vows touched:**

- *Reinforced:* Vow of Smallness (stdio-only, lazy import); Vow of Modular Authorship (MCP server crashes do not crash Munnr); Vow of Public-Friendliness (the human-facing CLI is unaffected); Vow of Pluggable Storage (event bus piggybacks on existing Brunnr).
- *At risk:* Vow of Honest Memory — an MCP client could in principle write to Brunnr through Smiðja tools and lie about provenance. Mitigation: every MCP-initiated tool call carries a `tool_call_id` whose `client_id` is recorded in the audit log. Approval prompts must surface the originating MCP client name to the operator, never silently auto-approve.
- *Flagged for ADR:* The decision to expose `permissions_respond` over MCP is a real surrender of authority — a peer agent can grant Ember capabilities to itself. This needs explicit operator opt-in via `config/ember.example.yaml` `mcp_server.allow_remote_approval: false` by default. See [[60_synthesis/66_DECISION_RECORDS]] ADR-Proposed-MCP-001.

**Cross-platform check:**

- stdio works on Linux, macOS, Windows (cmd.exe + PowerShell), WSL, Termux/Android, iSH/iOS. No exception.
- `mtime` is reliable on all targets except some network filesystems (NFS, SMB); Brunnr's docs already warn against running the Well on a network share for unrelated SQLite WAL reasons, so this constraint is already in operator hands.

**Concrete next step (if accepted):** scaffold `src/ember/spark/munnr/mcp/server.py` with the four read-only tools (`conversations_list`, `conversation_get`, `messages_read`, `events_poll`) and `events_wait`. Defer write tools to a follow-up phase. Total surface ~300 lines. The harder work is in [[60_synthesis/64_MIGRATION_PLAN]] phase M3.

Cross-references:
- The skill-discovery contract that lets MCP clients enumerate skills lives in [[20_interface/22_SKILL_INTERFACE]].
- The provider-side contract Funi needs lives in [[20_interface/23_PROVIDER_INTERFACE]].
- The RPC that connects skills to tools, which is the *internal* sibling of MCP's *external* tool calls, lives in [[20_interface/21_RPC_INTERFACE]].
- The crosswalk of Hermes-concept-to-Ember-True-Name is in [[60_synthesis/60_HERMES_VS_EMBER_CROSSWALK]].
