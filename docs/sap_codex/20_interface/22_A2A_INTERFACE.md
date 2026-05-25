---
codex_id: 22_A2A_INTERFACE
title: A2A Interface — Thirty-Nine Lines of Agent-to-Agent Diplomacy
role: Architect
layer: Interface
status: draft
sap_source_refs:
  - py/a2a_tool.py:1-39
  - server.py:1055
  - server.py:3381
ember_subsystem_targets: [Munnr, Strengr]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/12_AGENT_CORE_DOMAIN
  - 10_domain/19_TOOL_DOMAIN
  - 20_interface/20_MCP_INTEGRATION
  - 60_synthesis/62_PARTY_PROTOCOL
  - 60_synthesis/69_INTEGRATION_ROADMAP
---

# A2A Interface
## Thirty-Nine Lines of Agent-to-Agent Diplomacy

*— Rúnhild Svartdóttir, Architect*

> *The shortest interface I have seen in this codebase calls the most ambitious protocol — agent to agent, across hosts, in one direction, without confirmation. Diplomacy is rarely so abbreviated, and never so optimistic.*

The A2A (Agent-to-Agent) interface in SAP is `py/a2a_tool.py` — 39 lines, including imports, including blank lines. It is the contract by which SAP can call *another* agent (one that speaks Google's A2A protocol) as a tool. It is the kind of interface where you can read every line of the implementation and still wonder how much you have missed.

---

## 1. The Subject

**What A2A is:** Google's Agent-to-Agent protocol — a JSON-over-HTTP convention by which one agent calls another agent with a *question* and gets a *response*. The protocol is meant to be discoverable (each agent advertises its skills) and stateless from the caller's perspective.

**What SAP does with it:** lets the LLM call a configured A2A agent as if it were a tool. The agent lookup is by URL; the call payload is a single string (the query); the response is whatever the upstream agent returned.

**Where it lives:**

| File | LOC | Purpose |
|---|---|---|
| `py/a2a_tool.py` | 39 | Tool schema + dispatch |
| `server.py:1055` | 1 | Import the dispatch function |
| `server.py:3381` | 1 | Compose the tool schema into the LLM-facing tools list |
| `python_a2a` (external lib) | — | `A2AClient` — the HTTP client |

Forty-one lines of SAP code total. The rest is the external `python_a2a` library.

---

## 2. How It Works

### 2.1 The schema-builder

`get_a2a_tool(settings)` (lines 4-34) is the dynamic-description pattern from [[19_TOOL_DOMAIN]] §2.5:

```python
# /tmp/super-agent-party/py/a2a_tool.py:4-34
async def get_a2a_tool(settings):
    a2a_agent_list = []
    for a2a_agent_url, a2a_agent_config in settings["a2aServers"].items():
        if a2a_agent_config["enabled"]:
            a2a_agent_list.append({
                "agent_url": a2a_agent_url,
                "agent_description": a2a_agent_config["description"],
                "agent_skills": a2a_agent_config["skills"]
            })
    if len(a2a_agent_list) > 0:
        a2a_agent_list = json.dumps(a2a_agent_list, ensure_ascii=False, indent=4)
        agent_tool = {
            "type": "function",
            "function": {
                "name": "a2a_tool_call",
                "description": f"参考A2A智能体中的配置信息调用指定A2A服务，返回结果。当前可用的A2A服务器有：{a2a_agent_list}",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "agent_url": {"type": "string", "description": "需要调用的A2A智能体URL"},
                        "query": {"type": "string", "description": "需要向A2A智能体发送的问题"}
                    },
                    "required": ["agent_url", "query"]
                }
            }
        }
        return agent_tool
    else:
        return None
```

The function reads `settings.a2aServers` (a dict of `{url: {enabled, description, skills}}`), filters to enabled, JSON-stringifies the resulting list, and embeds it in the tool description. So the LLM sees:

> "当前可用的A2A服务器有： \[{...}, {...}\]"

— literally the agent roster embedded in the tool description. This is **the dynamic-description pattern at its smallest**: 30 lines, no abstraction, completely self-contained.

If no A2A servers are enabled, the function returns `None`, and the composition at `server.py` (presumably) omits the tool from the LLM's option list. Modular Authorship by absence.

### 2.2 The dispatcher

`a2a_tool_call(agent_url, query)` (lines 36-39):

```python
async def a2a_tool_call(agent_url, query):
    client = A2AClient(agent_url)
    response = client.ask(query)
    return response
```

Four lines. `A2AClient` is imported from `python_a2a`. `client.ask(query)` is synchronous (no `await`) — the `python_a2a` library does not provide an async interface in this version, so the call blocks the event loop.

That is the entire dispatcher. No error handling. No timeout. No retry. No tool validation against the configured `agent_skills`. No content-shape coercion.

### 2.3 The integration with the conversation loop

`server.py:1055` `from py.a2a_tool import a2a_tool_call` — bound to `tool_dispatch['a2a_tool_call']`.

`server.py:3381` `from py.a2a_tool import get_a2a_tool` — the schema-builder; called at conversation-prep time to produce the dynamic tool dict.

The LLM emits a `tool_calls` chunk with `name="a2a_tool_call"` and `arguments={"agent_url": "...", "query": "..."}`. The server dispatcher unpacks and calls `a2a_tool_call(agent_url, query)`. The return value is fed back into the conversation as the tool result.

---

## 3. The Contract — Inputs, Outputs, Side Effects, Invariants

### 3.1 Inputs

- `agent_url: str` — must match one of the keys in `settings.a2aServers`. **There is no validation that the URL is in the configured list.** The LLM could invent a URL and SAP would dispatch to it.
- `query: str` — free-form text.

### 3.2 Outputs

- Whatever `A2AClient.ask(query)` returns — presumably a string or dict from the upstream agent.
- On failure: the function will propagate the exception up through SAP's tool-call handler in `server.py`, which (per [[19_TOOL_DOMAIN]] §2.3) has its own try/except wrapping. The LLM sees a stringified exception.

### 3.3 Side effects

- An outbound HTTP call to `agent_url`.
- Whatever the upstream agent does on its side.
- Synchronous block of the asyncio loop for the duration of the call (since `A2AClient.ask` is sync).

### 3.4 Invariants enforced

- None. There is no validation of `agent_url` against the configured list. There is no timeout. There is no rate limit. There is no auth handling beyond whatever `A2AClient` does internally.

### 3.5 The leak

The leak is multi-dimensional:

1. **No allowlist enforcement** — the LLM can dispatch to *any* URL by emitting it in `agent_url`.
2. **Synchronous call in async context** — a slow upstream blocks every other request.
3. **No structured error** — failures look like text to the LLM.
4. **No skill validation** — the schema includes `agent_skills` in the description, but the dispatcher does not check that the query matches any declared skill.

Compare to the MCP outbound side ([[20_MCP_INTEGRATION]] §2.1) which has a 30-second ping, a 5-second reconnect, a typed error path, and explicit allowlists via `disable_tools`. The A2A interface has none of those. Same codebase, very different rigor.

---

## 4. Where It Breaks and Where It Surprises

### 4.1 The LLM can dial anywhere

`a2a_tool_call(agent_url, query)` accepts any string as URL. The LLM could be prompt-injected (by a malicious upstream agent! or by a comment in a livestream) into calling `http://attacker.example.com/`. SAP would call. There is no validation.

### 4.2 The sync call

`A2AClient.ask` blocks the event loop. A 30-second A2A call delays *every other concurrent request* in the SAP server — including the streaming chat reply the user is waiting for.

### 4.3 The skills are advertised but not enforced

The tool description embeds `agent_skills` per configured A2A agent. The LLM sees them. The dispatcher ignores them. So the *prompt* is honest about what each agent can do; the *runtime* trusts the LLM to pick the right agent. Mismatches (the LLM asks an arithmetic agent a poetry question) are not caught here.

### 4.4 No content validation

Whatever the upstream agent returns becomes the tool result. If the upstream returns 10 MB of JSON, SAP feeds 10 MB of JSON back into the conversation, blowing the context window. If the upstream returns base64-encoded executable, SAP doesn't notice.

### 4.5 The single import that drags a dependency

`from python_a2a import A2AClient` (line 2) pulls in the `python_a2a` library. The library's behavior — auth, timeout, encoding, error shape — is the *actual* A2A contract from SAP's perspective. The 39 lines of SAP code are a thin wrapper.

### 4.6 The crisp parts

- The **dynamic-description pattern** (line 18) at its purest.
- The **`None` return when no agents are enabled** (line 33) — Modular Authorship.
- The **honesty about agent skills** in the description, even if not enforced.

---

## 5. Cross-References

- [[10_DOMAIN_MAP]] §1 row 11 — A2A is part of the Tool Surface
- [[12_AGENT_CORE_DOMAIN]] §2.2 — the sub-agent system that A2A *could* be the cross-host version of
- [[20_MCP_INTEGRATION]] — the protocol with discipline that A2A is the foil for
- [[60_synthesis/62_PARTY_PROTOCOL]] — Ember's multi-host orchestration
- [[60_synthesis/69_INTEGRATION_ROADMAP]] — A2A vs. MCP as cross-codex bridge
- [[hermes:HEM-21_RPC_INTERFACE]] — Hermes uses JSON-RPC over stdio for ACP (Agent Communication Protocol from Zed); a parallel to A2A

---

## What This Means for Ember

**Adopt:**
- The **dynamic-description pattern** for A2A and similar peer-discovery tools. Embedding the current peer roster in the tool description is *correct*; it scales gracefully with config and requires no separate "list peers" call.
- The **`None` return when nothing is configured** — Modular Authorship at the tool composition boundary.

**Adapt:**
- The **synchronous `A2AClient.ask`** — adapt to an async client (either fork `python_a2a` or use the async A2A SDK if one exists; the protocol is HTTP+JSON, which any async HTTP client can speak). Strengr does not block its event loop on peer calls.
- The **agent_skills advertised but not enforced** — adapt to **enforced skill routing**. The dispatch function validates the query against the target agent's declared skills (text match or semantic similarity). Mismatches return an early error or a redirect to a more appropriate agent.
- The **stringly-typed return** — adapt to the `ToolResult` shape from [[19_TOOL_DOMAIN]].

**Avoid:**
- **Accepting any URL as `agent_url`.** Strengr's A2A dispatcher validates against the configured allowlist. Off-allowlist URLs fail closed.
- **Synchronous calls in async dispatch.** Refuse to merge.
- **Unvalidated response size.** Cap response payloads (e.g. 100 KB) with a typed truncation error.

**Invent:**
- **MCP as A2A.** Ember collapses the two protocols into one: peer-to-peer agent communication uses *MCP* (an established protocol with reconnect, transports, and tool schemas). The A2A "agent_url + query" shape is *one tool* on the MCP surface (`call_peer(peer_name, query) → response`). Peers register via MCP and respond via MCP. The Google A2A protocol becomes an *adapter* — Ember exposes an A2A-compatible HTTP route that translates A2A calls into Ember's MCP-internal peer dispatch. SAP runs A2A and MCP separately; Ember unifies. This is one of the largest [[60_synthesis/69_INTEGRATION_ROADMAP]] reductions.
- **Peer-Skill Manifests.** Each Ember peer (Realm, host, or external agent) publishes a *typed skill manifest*: declared skills, input/output schemas, rate limits, audit obligations. The manifest is signed (or hash-pinned in `tier_manifest.yaml`). Dispatching to a peer requires the manifest to be loaded; a mismatch between declared schema and actual peer behavior raises a Sögumiðla alarm.
- **Peer Identity Verification.** Before Ember calls a peer, the peer's identity is verified — a public-key challenge or a shared-secret HMAC. SAP trusts the URL string in `settings`; Ember trusts a verifiable identity. The Tailnet-default-bind preference of Volmarr is *the* environment where this becomes natural — every Ember Realm on the tailnet has a verifiable identity by virtue of the Tailscale ACL.
- **The Peer Latency Budget.** Strengr declares per-peer latency budgets in the tier manifest (Pi peers: 10s; workstation peers: 2s). A peer that exceeds the budget for 3 consecutive calls is *demoted* — Strengr stops routing queries to it until a probe succeeds. SAP makes the call and waits; Ember disciplines the wait.
- **The Audit-as-Response Header.** Every peer call includes an `audit_token` in the request — a Sögumiðla event id. The peer's response includes the token. Ember's audit log can trace the full conversation across Realms by following tokens. SAP has no such trace; cross-agent debugging is by `grep` over print statements.
