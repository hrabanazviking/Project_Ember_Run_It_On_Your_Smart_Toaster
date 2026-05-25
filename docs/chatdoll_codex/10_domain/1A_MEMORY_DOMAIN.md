---
codex_id: 1A_MEMORY_DOMAIN
title: Memory Domain — Two Stores Outside, One Integrator Inside, One Tool to Reach Them
role: Architect
layer: Domain
status: draft
chatdoll_source_refs:
  - Extension/ChatMemory/ChatMemoryIntegrator.cs:1-108
  - Extension/ChatMemory/ChatMemoryTool.cs:1-37
  - Scripts/LLM/LLMServiceBase.cs:38-86
  - Scripts/Dialog/DialogProcessor.cs
ember_subsystem_targets: [Hjarta, Brunnr]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/16_LLM_SERVICE_DOMAIN
  - 10_domain/19_TOOL_DOMAIN
  - 30_execution/38_CHATMEMORY_INTEGRATION
  - 60_synthesis/65_MEMORY_INTEGRATION
  - sap:1A_MEMORY_DOMAIN
  - waifu:25_PERSONA_MEMORY
---

# Memory Domain
## Two Stores Outside, One Integrator Inside, One Tool to Reach Them

*— Rúnhild Svartdóttir, Architect*

> *Memory is the dimension of a companion that survives the conversation ending. ChatdollKit's choice is the boldest of the three corpora — push the memory out of the avatar entirely, into a sister service that knows about it the way the avatar does not. The integrator is a hundred lines. The discipline is profound.*

`Extension/ChatMemory/ChatMemoryIntegrator.cs` (108 LOC) and `Extension/ChatMemory/ChatMemoryTool.cs` (37 LOC) together comprise the *entire* CDK-side memory subsystem. One hundred forty-five lines of code. They do nothing but talk HTTP to an external FastAPI service — `github.com/uezo/chatmemory` — running in a separate process, usually on the same host but conceivably elsewhere. The integrator posts conversation history. The tool searches the service from inside a function call.

**This is the architectural decision Ember most needs to study from CDK.** Other codexes baked memory into the avatar: SAP's `super_party_db.py` is part of `server.py`'s monolith ([[sap:1A_MEMORY_DOMAIN]]); Waifu has no persistent memory at all ([[waifu:25_PERSONA_MEMORY]]). CDK chose **memory as an external service**, communicated over HTTP, owned by a separate repository on a separate release cadence. The cost: a deployment surface to manage. The benefit: memory is a *separate concern with separate testing, separate versioning, separate scaling, separate failure modes*. Ember's `Hjarta` (heart) and `Brunnr` (Well) True Names map onto this pattern directly — Hjarta as the integrator, Brunnr-Well-of-Memory as the external store.

Below, the LLM service's *transient* per-session context (`LLMServiceBase.context` with 10-minute timeout, [[16_LLM_SERVICE_DOMAIN]] §2.2) is the *other* part of CDK's memory model. Two tiers: *conversation-window context* (in-process, transient, per-LLM-service) and *persistent memory* (external service, durable, cross-session). The split matches the cognitive science distinction between working memory and long-term memory; CDK names neither but implements both.

---

## 1. The Subject Itself

**What the domain is:** the substrate of cross-turn and cross-session continuity. *Inside* the LLM service: a 10-minute-idle-expiring list of `ILLMMessage`s — the avatar's working memory. *Outside* the avatar process: a ChatMemory FastAPI service with two stores — *history* (recent conversations) and *memory* (vector-indexed long-term facts and episodes extracted from history).

**What it owns:**

| Concern | Files | LOC | Owns |
|---|---|---|---|
| **Transient context** | `Scripts/LLM/LLMServiceBase.cs:38-86` | ~50 | The in-memory `context: List<ILLMMessage>`, `contextId: string`, `historyTurns` config, `contextTimeout: int = 600` (10 min), `ClearContext`, time-based idle eviction |
| **External integration** | `Extension/ChatMemory/ChatMemoryIntegrator.cs` | 108 | HTTP client to ChatMemory server: `AddHistory(sessionId, request, response)` posts user+assistant exchanges, `SearchMemory(query, top_k)` returns hits |
| **Tool wrapper** | `Extension/ChatMemory/ChatMemoryTool.cs` | 37 | `ITool` adapter so the LLM can search memory via function-calling: `search_memory(query: string)` |
| **Server-side (external repo)** | `uezo/chatmemory` FastAPI | (separate) | Episodic store + factual store + the "extract memory from history" LLM call, batch-processed offline; vector index + retrieval |

**What it does NOT own:**
- The vector store, the embedding model, the memory-extraction pipeline — those live in the `uezo/chatmemory` repository, deployed as a separate process. Forge-B's [[38_CHATMEMORY_INTEGRATION]] goes deep on the sister-project.
- Memory *consolidation* — the integrator does not decide "what is worth remembering"; the server-side `consolidate_memories` cron decides. CDK is the *client*; ChatMemory is the *knowledge owner*.
- Cross-user memory isolation — handled by `UserId` field on the integrator; the server enforces.

---

## 2. How It Works

### 2.1 The two-tier memory model

CDK's working memory is the LLM service's per-session context. Long-term memory is ChatMemory.

```
┌────────────────────────────────────────────────────────────────────────┐
│  TRANSIENT (in-process)                                                │
│  LLMServiceBase.context : List<ILLMMessage>                            │
│    │  capped to `historyTurns * 2` messages                            │
│    │  cleared after `contextTimeout` seconds idle (default 600 = 10m)  │
│    │  per-provider message subtypes (ChatGPTMessage / ClaudeMessage…)  │
└────────────────────────────────────────────────────────────────────────┘
                              │ each turn:
                              │   - read for prompt
                              │   - written with user+assistant exchange
                              ▼
                      ┌─────────────────┐
                      │ ChatMemory      │  AddHistory(sessionId, req, resp)
                      │ Integrator      │ ───────────────────────────► HTTP
                      │ (HTTP client)   │
                      └─────────────────┘
                              │
                              │ (also) SearchMemory(query) when tool fires
                              ▼
              ┌─────────────────────────────────┐
              │  EXTERNAL — uezo/chatmemory     │
              │   FastAPI service               │
              │   ─ History store               │
              │   ─ Memory (vector) store       │
              │   ─ Consolidation cron          │
              │   ─ Per-user_id isolation       │
              └─────────────────────────────────┘
```

Two writes per turn (request + response → ChatMemory); zero reads in the default path (the LLM works from its in-process context); reads triggered when the LLM emits a tool call to `search_memory`. **The default cost of using long-term memory is zero LLM latency** — the LLM only reaches for it when the working-memory context is insufficient.

### 2.2 The transient-context tier

`LLMServiceBase` (`Scripts/LLM/LLMServiceBase.cs:38-86`):

```csharp
[SerializeField] protected int historyTurns = 100;        // turns × 2 = messages
[SerializeField] protected int contextTimeout = 600;       // 10 minutes idle
protected float contextUpdatedAt;
protected List<ILLMMessage> context = new List<ILLMMessage>();
protected string contextId = string.Empty;

public virtual List<ILLMMessage> GetContext(int count) {
    if (Time.time - contextUpdatedAt > contextTimeout) ClearContext();
    if (string.IsNullOrEmpty(contextId)) contextId = Guid.NewGuid().ToString();
    return context.Skip(context.Count - count).ToList();
}
```

100 turns × 2 = 200 messages. 10-minute idle reset. Each provider's `UpdateContext` appends user + assistant after each turn (e.g., `ChatGPTService.cs:42-79`). A new `contextId: Guid` is minted on session start; passed through `ILLMSession.ContextId`; usable as a foreign key to the ChatMemory side.

The 10-minute cliff is **deliberate forgetting**. CDK assumes a conversation that idles for 10 minutes is over; the next utterance starts fresh. For voice-first companions this is reasonable — humans context-switch on similar timescales. For text-first assistants (Slack-bot style), it is too short. Ember should expose the timeout per-realm; default for voice-first 10 minutes, default for text 4 hours.

The context is *per-provider*. Switching from ChatGPT to Claude mid-session means the new provider starts empty (the cache is not portable; the message subclasses are not interchangeable). This is a real cost of the multi-provider model. Ember's `Cross-Provider Context Migration` invented in [[16_LLM_SERVICE_DOMAIN]] solves this; CDK does not.

### 2.3 The persistent-memory tier — `ChatMemoryIntegrator`

The integrator is **two HTTP calls** plus configuration. The full file is 108 lines; the substance is below.

`AddHistory` (`Extension/ChatMemory/ChatMemoryIntegrator.cs:20-54`):

```csharp
public async UniTask AddHistory(string sessionId, string requestText, string responseText, CancellationToken token = default) {
    if (string.IsNullOrEmpty(UserId)) { Debug.LogWarning(...); return; }
    await httpClient.PostJsonAsync(
        $"{BaseUrl}/history",
        data: new Dictionary<string, object>() {
            { "user_id", UserId },
            { "session_id", sessionId },
            { "messages", new List<Dictionary<string, string>>() {
                new() { { "role", "user" }, { "content", requestText } },
                new() { { "role", "assistant" }, { "content", responseText } }
            }},
            { "channel", Channel }
        },
        cancellationToken: token);
}
```

POST a two-message exchange to `/history`. The server stores it. *Eventually* (the consolidation cron, server-side), the LLM running inside ChatMemory extracts "what is worth remembering" and writes vector-indexed memory entries. This is asynchronous and out-of-band; the avatar does not wait for it.

`SearchMemory` (`Extension/ChatMemory/ChatMemoryIntegrator.cs:56-95`):

```csharp
public async UniTask<SearchResponse> SearchMemory(string query, int top_k = 5, ...) {
    var response = await httpClient.PostJsonAsync<SearchResponse>(
        $"{BaseUrl}/search",
        data: new Dictionary<string, object>() {
            { "user_id", UserId }, { "query", query }, { "top_k", top_k },
            { "search_content", search_content }, { "include_retrieved_data", include_retrieved_data }
        }, cancellationToken: token);
    return response;
}
```

POST to `/search` with the LLM-supplied query. Receive a `SearchResponse` with `result.answer` (a synthesised string) and `result.retrieved_data` (the raw memory entries that produced it). The tool wraps this and returns to the LLM.

**The configuration** (`Extension/ChatMemory/ChatMemoryIntegrator.cs:12-18`):

```csharp
[SerializeField] private string BaseUrl;
public string UserId;
public string Channel;
[SerializeField] private bool isDebug;
private ChatdollHttp httpClient = new ChatdollHttp(timeout: 10000);
```

Five fields. `BaseUrl` is the ChatMemory FastAPI endpoint (`http://localhost:8123` typical). `UserId` is the cross-session key — same user across sessions retrieves shared memory; different users are isolated. `Channel` is a coarse namespace (e.g., `voice`, `text`, `mobile`) for cross-channel separation. The simplicity is deliberate: the *server* owns the heavy lifting; the *integrator* is a five-field, two-method wrapper.

### 2.4 The tool wrapper — `ChatMemoryTool`

`Extension/ChatMemory/ChatMemoryTool.cs:22-35`:

```csharp
public override ILLMTool GetToolSpec() {
    var func = new LLMTool(FunctionName, FunctionDescription);
    func.AddProperty("query", new Dictionary<string, object>() { { "type", "string" } });
    return func;
}

protected override async UniTask<ToolResponse> ExecuteFunction(string argumentsJsonString, CancellationToken token) {
    var arguments = JsonConvert.DeserializeObject<Dictionary<string, string>>(argumentsJsonString);
    var searchResponse = await chatMemoryIntegrator.SearchMemory(arguments["query"], include_retrieved_data: IncludeRetrivedData);
    return new ToolResponse(JsonConvert.SerializeObject(searchResponse.result));
}
```

The whole tool is *thirteen lines of substance*. Declare one parameter (`query: string`). Parse the LLM's call. Forward to the integrator. Return the JSON.

The result lands in the LLM's next context message (`ChatGPTFunctionMessage` or equivalent per provider). The LLM reads its own search result and answers the user based on what it now knows. **The avatar does not "use" memory; the LLM does, through the tool.** This is the architectural inversion: memory is not a property of the avatar that the LLM consults; memory is a *resource the LLM reaches for* when it needs it. The avatar is a polite middleware between the user and the LLM's tool-augmented reasoning.

For Ember: this is the *correct* split. `Hjarta` is not the keeper of memories; `Hjarta` is the *integrator that lets the LLM reach for memories*. The Well (Brunnr) holds them. The split lets Ember swap LLMs without losing memory continuity, and swap memory backends (ChatMemory ↔ a homegrown PostgreSQL ↔ Skein KG, [[ember:project_skein_skry]]) without changing the avatar.

### 2.5 The session lifecycle and `AddHistory` timing

`ChatMemoryIntegrator.AddHistory` is *not* called automatically by CDK. The user wires it. Typical wiring (deduced from sister-project docs):

```csharp
// In application setup
dialogProcessor.OnEndAsync = async (request, response, payloads, token) => {
    await chatMemoryIntegrator.AddHistory(dialogProcessor.ContextId, request, response, token);
};
```

`DialogProcessor.OnEndAsync` fires after a successful turn. The user-side handler bridges to the integrator. The wiring is *not* in the integrator; the integrator is a *passive* HTTP client. This is intentional: the user might want to NOT-persist certain sessions (private mode), or post to multiple memory stores, or transform before posting. CDK leaves the policy to the application.

For Ember: the wiring should be the default (`Hjarta` automatically appends to Brunnr on turn end), with an *explicit opt-out* per realm. Default-on persistence is the right discoverable behaviour; default-off makes "where did my conversation go?" a question users have to debug.

---

## 3. Where It Breaks and Where It Surprises

### 3.1 The integrator silently fails on missing `UserId`

Lines 22-26: `if (string.IsNullOrEmpty(UserId)) { Debug.LogWarning(...); return; }`. No throw; no event; the conversation is silently un-persisted. Ember should fail loud — startup verification that `UserId` is set, or refuse to register the integrator without one.

### 3.2 The 10-minute context cliff cannot be observed mid-conversation

If the user idles for 9:59 and then says something, the context is intact. At 10:01, fresh. There is no graceful warm-down — no "I'm starting to forget" signal at minute 9. Ember could fire a `ContextFading` Sögumiðla event at 80% of the timeout; the application can decide to surface this to the user.

### 3.3 No memory-write batching

Every turn → one `AddHistory` HTTP call. On a long conversation, that is one call per turn. For a phone deployment over cellular, this is real latency *and* battery cost. Ember should batch (configurable: per-turn, every N turns, on-idle-only) with a flush at session end.

### 3.4 The tool can return arbitrarily-large data

`SearchResponse.result.retrieved_data` is a server-supplied string. If it is 50KB, the LLM's next context message is 50KB. No bound. Ember should cap (8KB default; configurable) and re-summarise server-side if over.

### 3.5 No memory-write confirmation

`AddHistory` is fire-and-forget. If the HTTP call fails, the conversation is lost. CDK logs the error; nothing else happens. Ember should retry with exponential backoff and, on persistent failure, queue locally for later flush (the Pi-tier can lose connectivity at any moment).

### 3.6 The `Channel` field is undocumented

No mention in CDK's docs of how `Channel` should be used. The integrator passes it; the server presumably indexes by it. Ember's equivalent should *name* the channels (`voice`, `text`, `image`, `vr-session`) and document semantics.

### 3.7 The tool name `search_memory` is hardcoded by default

`FunctionName = "search_memory"` (line 14) is a public field — overridable per deployment — but the default is a generic name. If multiple memory backends are active simultaneously, name collisions are silent (last-registered wins in the linear scan). Ember's tools have namespaced names by default (`memory.search`, `memory.write`, `web.search`).

### 3.8 The crisp parts

- **External service for long-term memory.** The bold architectural choice. The single most adoptable pattern in this domain.
- **Two-method integrator** (`AddHistory` + `SearchMemory`). Smallest viable HTTP-client wrapper.
- **Tool-mediated memory access.** The LLM uses memory through function-calling, not through prompt-stuffing.
- **`UserId` + `Channel` as the cross-session keys.** Simple, two-dimensional namespacing.
- **`contextId: Guid` as the join key.** Per-session identifier links transient context to persistent history.
- **Default 10-minute idle context cliff** — explicit forgetting, named in code.

---

## 4. Cross-References

- [[10_DOMAIN_MAP]] §1 + §7 — Memory as an Extension; sister-project ecosystem
- [[16_LLM_SERVICE_DOMAIN]] §2.2 — the transient-context tier in detail
- [[19_TOOL_DOMAIN]] §2.6 — `ChatMemoryTool` as the example tool
- [[38_CHATMEMORY_INTEGRATION]] — Forge-B's deep dive on the sister-project
- [[65_MEMORY_INTEGRATION]] — Scribe's synthesis: how this pattern maps to Hjarta
- [[sap:1A_MEMORY_DOMAIN]] — SAP's monolith-internal memory
- [[waifu:25_PERSONA_MEMORY]] — Waifu's persona-only-no-history model
- [[hermes:1A_MNEMOSYNE_DOMAIN]] — Hermes's memory True Name (placeholder)

---

## What This Means for Ember

**Adopt:**
- The **memory-as-external-service** architectural decision. Ember's `Hjarta` is the integrator; `Brunnr` is the Well of Memory (already running PostgreSQL+pgvector on `gungnir:5432` — [[ember:reference_gungnir_db]]). The CDK pattern translates directly; the Well already exists.
- The **two-method integrator interface** (`AddHistory` + `SearchMemory`). Ember's `HjartaIntegrator` Protocol: `async add_history(session_id, user_text, assistant_text)`, `async search_memory(query, top_k) -> SearchResult`. Apache-2.0 attribution required.
- The **tool-mediated memory access** pattern. Ember's `memory.search` tool follows `ChatMemoryTool.cs:22-35` shape exactly: thirteen lines, four-line spec, five-line execute.
- The **`UserId` + `Channel` two-dimensional namespacing**. Ember's Brunnr schema indexes by `(user_id, channel)` for natural isolation.
- The **two-tier model** (transient context + persistent memory). Ember's working memory is `Smiðja`-internal (LLM context list); long-term is `Hjarta` → `Brunnr`. Two memories, two timescales, two access patterns.

*Apache-2.0 attribution: when patterns from `ChatdollKit/Extension/ChatMemory/` are adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).*

**Adapt:**
- The **10-minute transient-context cliff**. Adapt as per-realm config: voice realm 10m, text realm 4h, code-pair realm 2h. The CDK default is reasonable for voice; not universal.
- The **fire-and-forget `AddHistory`**. Adapt with retry + local-queue-on-failure semantics. Pi-tier connectivity loss must not lose memory writes.
- The **silent-fail-on-missing-UserId**. Adapt as startup-verification; the Hjarta integrator refuses to register without `user_id` configured; emits `HjartaUnconfigured` event and the orchestrator surfaces a setup prompt.
- The **single-tool memory access**. Adapt as a *small family* of tools: `memory.search(query)`, `memory.recent(n)` (last N turns), `memory.summarise(timeframe)` — each with explicit semantics. CDK has one; Ember has three.
- The **server-side memory consolidation**. Ember's Brunnr already has the Skein KG (`~/ai/skein-kg` — [[ember:project_skein_skry]]) for cheap entity extraction. Consolidation runs as a Skein job; the integrator queries the resulting embeddings.

**Avoid:**
- **Unbounded memory-search results** flowing into the LLM context.
- **No write confirmation** — Ember acks `AddHistory` writes; sessions track in-flight unconfirmed writes.
- **Hardcoded generic tool names** like `search_memory`. Ember namespaces: `memory.search`, `memory.write`, `web.search`. Collisions are visible.
- **Default-off persistence**. The CDK pattern leaves persistence to user wiring; Ember persists by default, opts out per-realm explicitly.

**Invent:**
- **The Two-Memory Vow.** Every Ember conversational realm has two memories named in config: `working` (transient, capped, time-bounded) and `persistent` (durable, vector-indexed, cross-session). Mixing them is forbidden by design; access patterns differ; eviction policies differ. The two-memory split is *explicit* in Ember's vocabulary.
- **The Memory-Write Receipt.** Every `AddHistory` returns a `receipt: MemoryReceipt(session_id, turn_id, server_ack: bool, written_at: datetime)`. Failed writes are queued locally with `pending_receipt` semantics; flushed on next connectivity. The session post-mortem can list "writes that never got receipts."
- **The Context-Decay Sögumiðla Event.** At 80% of `context_timeout`, emit `ContextDecaying(session_id, remaining_seconds)`. At 100%, emit `ContextExpired`. The UI can surface "I'm about to forget what we were talking about" with a refresh button. CDK has no warm-down; Ember has two events.
- **The Channel-as-Tier Vow.** Ember's memory channels are not arbitrary strings; they map to typed realms (`voice`, `text`, `code`, `vr`). Each realm has its own Brunnr schema branch and its own retention policy (voice: 30 days; code: forever; vr: 7 days). CDK's `Channel` field is freeform; Ember's is a typed enum.
- **The Memory-Read Provenance.** When the LLM's `memory.search` tool returns results, each result carries `(session_id, turn_id, written_at, channel)` provenance. The LLM can cite ("on Tuesday you mentioned...") and the user can verify. CDK returns `retrieved_data` without provenance; Ember makes it first-class.
- **The Cross-Backend Memory Adapter.** Ember's `HjartaIntegrator` Protocol has at least two implementations: `ChatMemoryHjarta` (the CDK pattern, via HTTP), `BrunnrHjarta` (the local PostgreSQL+pgvector). Configurable per-realm. Same tools (`memory.search`) hit either backend; the LLM never knows the difference.
- **The Memory Forgetting Rite.** Beyond automatic eviction, Ember supports *explicit* user-driven forgetting: `forget_about(topic)` is a tool the user can invoke through dialogue. The Hjarta integrator marks matching memories `deleted: true`; the search tool skips them. Right-to-be-forgotten as a first-class affordance. CDK has no such mechanism; Ember owes one.
