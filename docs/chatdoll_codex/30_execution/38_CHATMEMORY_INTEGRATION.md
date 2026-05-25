---
codex_id: 38_CHATMEMORY_INTEGRATION
title: ChatMemory Integration — A FastAPI Companion to the Doll, and the First Real Hjarta Pattern
role: Forge-B
layer: Execution
status: draft
chatdoll_source_refs:
  - /tmp/ChatdollKit/Extension/ChatMemory/ChatMemoryIntegrator.cs:10-108 (Unity-side integrator)
  - /tmp/ChatdollKit/Extension/ChatMemory/ChatMemoryTool.cs (LLM tool wrapper)
sister_source_refs:
  - /tmp/chatmemory/chatmemory/chatmemory.py:141-1451 (the ChatMemory class)
  - /tmp/chatmemory/chatmemory/chatmemory.py:239-317 (DB schema init)
  - /tmp/chatmemory/chatmemory/chatmemory.py:1066-1138 (search() entry point)
  - /tmp/chatmemory/chatmemory/chatmemory.py:1140-1451 (FastAPI router)
  - /tmp/chatmemory/docker/run.py:1-28 (deployment shape)
ember_subsystem_targets: [Hjarta, Brunnr]
cross_refs:
  - 10_domain/1A_MEMORY_DOMAIN
  - 60_synthesis/65_MEMORY_INTEGRATION
  - sap:14_MEMORY_DOMAIN
  - waifu:30_MEMORY_HANDLING
---

# ChatMemory Integration

> *The doll does not remember; a small FastAPI service across the network remembers for it. The cost of that decoupling is exactly the right cost — Unity stays a renderer, memory stays in Postgres, the LLM is the only thing that needs both.*

Forge. Eldra-iron. ChatdollKit ships a `ChatMemoryIntegrator` MonoBehaviour that is, generously, **96 lines including braces**. Almost nothing happens in Unity. The whole memory subsystem lives in a separate Python project — `uezo/chatmemory`, a 1,451-line single-file FastAPI service backed by Postgres + pgvector. This is the cleanest two-process separation in the entire CDK ecosystem, and it is the **single most important sister-project pattern** for Ember's Hjarta.

The cross-process design is not incidental. Memory is the one subsystem where coupling to the game engine would be catastrophic — every save state, every long-running conversation, every embedded vector index — and uezo refused to couple it. We adopt the posture wholesale.

## What ChatMemory Is

`uezo/chatmemory` is a four-table FastAPI service:

1. **`conversation_history`** — every turn of dialogue, keyed by `(user_id, session_id, channel)`. No vectors. Pure transcript.
2. **`conversation_summaries`** — LLM-generated session summaries with **two vector columns**: `embedding_summary` (over the summary text) and `content_embedding` (over the full conversation). The dual embedding is unusual; most chat-memory tools use one.
3. **`user_knowledge`** — operator-curated factual statements about a user. Single vector column.
4. **`diaries`** — date-indexed daily entries with a `UNIQUE (user_id, diary_date)` constraint and a `metadata` JSONB field. Single vector column. Upsert via `ON CONFLICT`.

Schema reference: `chatmemory.py:239-317`. The four tables map directly to four memory **categories**, each retrievable through a single `search()` entry point at `chatmemory.py:1066`.

```python
# /tmp/chatmemory/chatmemory/chatmemory.py:1066-1075
async def search(
    self,
    user_id: Union[str, List[str]],
    query: str,
    top_k: int = 5,
    search_content: bool = False,
    include_retrieved_data: bool = False,
    since: Optional[datetime.date] = None,
    until: Optional[datetime.date] = None,
    utc_offset_hours: float = 0.0,
) -> SearchResult:
```

Three retrieval modes, one entry point: summaries, knowledge, diaries — all vector-ranked by the same query embedding. If the LLM declares the retrieved data insufficient by emitting `[search:content]`, the call falls back to full conversation-content search (`chatmemory.py:1120-1135`). One round-trip per query; up to two LLM calls per search. The cascading retrieval is uezo's quietest cleverness.

## The Unity Side Is Almost Nothing

`ChatMemoryIntegrator.cs:10-96` is the entire Unity-side surface. It is a `MonoBehaviour` with three string fields (`BaseUrl`, `UserId`, `Channel`) and two methods:

```csharp
// /tmp/ChatdollKit/Extension/ChatMemory/ChatMemoryIntegrator.cs:20-54
public async UniTask AddHistory(string sessionId, string requestText, string responseText, CancellationToken token = default)
{
    if (string.IsNullOrEmpty(UserId)) { Debug.LogWarning(...); return; }
    await httpClient.PostJsonAsync(
        $"{BaseUrl}/history",
        data: new Dictionary<string, object>()
        {
            { "user_id", UserId },
            { "session_id", sessionId },
            { "messages", new List<Dictionary<string, string>>() {
                new() { { "role", "user" }, { "content", requestText } },
                new() { { "role", "assistant" }, { "content", responseText } }
            }},
            { "channel", Channel }
        },
        cancellationToken: token
    );
}
```

That is it. `AddHistory()` posts two messages per turn (user request + assistant response) to `POST /history`. `SearchMemory()` (lines 56-95) posts a query to `POST /search`. The Unity client uses CDK's `ChatdollHttp` wrapper with a 10-second timeout. There is **no caching, no batching, no retry, no offline queue**. If ChatMemory is down, history additions are silently swallowed (`catch (Exception)` at line 50 logs and returns).

This is the right amount of code for the Unity side. The doll-as-renderer should not be in the business of managing a persistent store; if the memory service is unreachable, the conversation continues without memory. Graceful degradation by indifference. Compare with [[sap:14_MEMORY_DOMAIN]] where SAP keeps memory in-process (mem0) and a crash takes the entire chat history with it.

## The Summary-on-Session-Switch Trick

The single most interesting pattern in the whole sister project lives in the POST `/history` handler:

```python
# /tmp/chatmemory/chatmemory/chatmemory.py:1149-1175
@router.post("/history", ...)
async def post_history_endpoint(request: AddHistoryRequest, background_tasks: BackgroundTasks):
    try:
        with self.get_db_cursor() as (cur, _):
            cur.execute(
                "SELECT session_id FROM conversation_history WHERE user_id = %s "
                "ORDER BY id DESC LIMIT 1",
                (request.user_id,),
            )
            row = cur.fetchone()
            previous_session = row[0] if row else None

        self.add_history(...)
        # If a session switch is detected, schedule summary generation
        # for the previous session
        if previous_session and previous_session != request.session_id:
            background_tasks.add_task(self.create_summary, request.user_id, previous_session)
        return AddHistoryResponse(status="ok")
```

Every time a new session starts (the `session_id` in the request differs from the most recent stored `session_id` for that user), FastAPI schedules `create_summary()` for the **previous** session as a background task. The summary call generates an LLM summary, embeds the summary, embeds the full session content, and writes both vectors plus the summary text into `conversation_summaries`.

This means the user never has to ask for summaries. They are produced lazily, at the boundary between sessions, off the request-response critical path. The cost is one LLM call + two embedding calls **per session-switch**, not per turn. For a user who chats five times a day, that is five LLM calls a day for memory consolidation, total. Cheap.

The `create_summary()` itself (`chatmemory.py:518-596`) is tolerant: if summary already exists and `overwrite=False`, do nothing; on LLM error, log and return without raising. The background task is fire-and-forget by design.

## The Dual-Embedding Retrieval Cascade

`conversation_summaries` carries two vectors: `embedding_summary` (over the brief summary) and `content_embedding` (over the full conversation text). The cascade works as:

1. `search()` embeds the query.
2. Vector-search `embedding_summary` to find top-k matching session summaries — this is the **cheap, high-precision** pass.
3. Vector-search `embedding` on `user_knowledge` for facts.
4. Vector-search `embedding` on `diaries` for date-bracketed events.
5. Concatenate the three retrieved blobs, feed to the LLM with `SEARCH_SYSTEM_PROMPT_DEFAULT`, get an answer.
6. If the LLM appends `[search:content]` to its answer, fall back: vector-search `embedding_summary` again, but now pull the *full conversation history* for the top sessions and feed that bulkier blob back to the LLM (`chatmemory.py:1128-1138`).

The fallback is gated by an LLM-emitted token — the model decides whether the summary was enough. This is **model-as-retrieval-decider**, not a hard threshold. Hard-threshold ranking would either over-retrieve (cost) or under-retrieve (quality); letting the LLM say "I need more" is a cheap and self-tuning signal.

The pattern matches Brunnr's expected behavior in [[ember:reference_gungnir_db]] — vector-rank the cheap representations, escalate to content only when needed.

## The Postgres + pgvector Choice

`init_db()` (`chatmemory.py:239-317`) creates `vector` extension, three tables, and indexes including:

- `CREATE INDEX idx_history_user_id ON conversation_history(user_id);`
- `CREATE INDEX idx_history_session_id ON conversation_history(session_id);`
- `CREATE INDEX idx_history_channel ON conversation_history(channel);`

But **no vector index**. The `embedding_summary <-> %s::vector` operator (`chatmemory.py:884`) runs against the column without an `ivfflat` or `hnsw` index. For small datasets (< 100k summaries) that is fine. For Ember's expected scale (one user, hundreds of sessions over a year), still fine. For deployment at scale, this becomes a footgun.

The connection pool (`pool.SimpleConnectionPool(1, 10, ...)` at line 192) is naive but tolerant. The `get_db_cursor()` context manager (`chatmemory.py:207-237`) health-checks every cursor lease with `SELECT 1` and discards zombies. Solid; we adopt this pattern unmodified.

## The Diary Surface — A Surprise

The `diaries` table is the surprise. Most memory tools treat diaries as long-running journals. ChatMemory treats them as **date-keyed daily entries with vector search**:

```python
# /tmp/chatmemory/chatmemory/chatmemory.py:301-314
CREATE TABLE IF NOT EXISTS diaries (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL,
    user_id TEXT NOT NULL,
    diary_date DATE NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding VECTOR(...),
    UNIQUE (user_id, diary_date)
);
```

`UNIQUE (user_id, diary_date)` means one diary entry per user per day. `update_diary()` (`chatmemory.py:782-811`) is an upsert: `ON CONFLICT (user_id, diary_date) DO UPDATE`. The diary is mutable, but the mutation is consolidating — you can rewrite today's diary entry but not split it.

`search_diary()` (`chatmemory.py:933-983`) does vector search with date bounds. The query receives both vector similarity *and* a date window. Combined: "find me diary entries about `<query>` between `<since>` and `<until>`". For Ember this is exactly the affordance Hjarta needs to surface "what happened on Tuesday" — vector for topic, date for window.

The `metadata` JSONB is the open seam. CDK doesn't use it directly; it's there for downstream callers to attach event tags (location, mood, weather, who-was-present). Ember should adopt the JSONB seam and define a small canonical schema for metadata keys — see Invent below.

## Where It Breaks

- **No auth.** The FastAPI router has zero auth middleware. Any process that can reach the port can read or write any user's memory. Deployment must be inside a trusted network or behind a reverse proxy doing auth (`docker/run.py:1-28` provides no auth example).
- **No multi-user isolation at the DB level.** `user_id` is the only partition. A bug in the integrator that sends the wrong `UserId` (note: only one field on the Unity side; trivially miscopiable when prefab is duplicated) writes into another user's history. No RLS, no constraint.
- **OpenAI is hardcoded.** `openai.AsyncOpenAI` (`chatmemory.py:173`) is the only LLM client. `openai_base_url` lets you point at any OpenAI-compatible endpoint, but the embedding column dimension is set at table-create time (`embedding_dimension or 3072 if embedding_model == "text-embedding-3-large" else 1536`). Switching providers later means rebuilding the table.
- **Background tasks are silent on failure.** If `create_summary()` raises mid-task, FastAPI's `BackgroundTasks` swallows the exception. Session summaries can silently fail to be generated; the user has no signal.
- **No pgvector index.** As noted above, vector queries at scale will degrade to seq-scan.
- **The Unity integrator has no retry, no offline queue.** A user who has a 10-minute conversation with the network down loses 10 minutes of history. CDK doesn't try.
- **`UTCnow()` everywhere.** `datetime.datetime.utcnow()` (`chatmemory.py:347`, `670`, `714`, `796`) is deprecated as of Python 3.12; should be `datetime.now(timezone.utc)`. Minor but real.
- **The `[search:content]` cascade can double the latency** of any search. Two LLM calls back-to-back if the first answer says "not enough". No timeout to skip the cascade.
- **No GDPR-style delete-all-for-user route surfaced as a single call.** The delete routes exist per-table (`delete_history`, `delete_summaries`, `delete_knowledge`, `delete_diary`) but no convenience endpoint glues them. A right-to-forget request requires four DELETE calls.

## Where It Surprises

- **The summary-on-session-switch trigger.** Implicit, automatic, zero-config. The user changes sessions, the system summarizes. Compare with [[sap:14_MEMORY_DOMAIN]] where mem0 requires explicit consolidation calls.
- **`UNIQUE (user_id, diary_date)`.** One diary per day. The constraint forces a discipline — the system can't accumulate a hundred half-thoughts per day. It has to consolidate.
- **`SearchResult` returns both `answer` and `retrieved_data`** with `include_retrieved_data=True` (default False). The answer is for display; the retrieved blob is for audit. Ember's audit Vow benefits — every memory answer can be paired with its evidence trail.
- **The single-file design.** 1,451 lines, one class, one router. Easy to read end-to-end in a sitting. Compare with mem0's multi-module sprawl. This is what "small enough to fit in head" actually looks like.
- **`openai_base_url` parameter** means ChatMemory works against Ollama (`http://localhost:11434/v1`), Together, Groq, llama-server, anything OpenAI-compat. The LLM choice is per-deployment, not per-build.
- **The connection pool health check** (`SELECT 1` before lease) handles Postgres zombie connections gracefully. Most pool wrappers don't bother; ChatMemory's resilience here is a real engineering quality.
- **Docker layout is two-container.** `docker/Dockerfile.app` for the FastAPI service, `docker/Dockerfile.db` for Postgres+pgvector. `docker-compose.yaml` wires them on the same internal network. Single command deploy.

## The Tool-Calling Wrapper

`ChatMemoryTool.cs` (a sibling file under `/tmp/ChatdollKit/Extension/ChatMemory/`) wraps `SearchMemory()` as an LLM function-call tool. The LLM can decide to invoke memory search mid-conversation. This is the right composition: the integrator is the network client; the tool is the LLM-facing surface. CDK keeps them separate.

For Ember, this maps directly onto Munnr's tool surface — see [[26_TOOL_FUNCTION_CALL_INTERFACE]]. The "ask Hjarta" tool is exactly a wrapped Brunnr search.

## Cross-References

- [[10_domain/1A_MEMORY_DOMAIN]] — domain view of CDK's memory layer
- [[60_synthesis/65_MEMORY_INTEGRATION]] — Cartographer's synthesis: ChatMemory pattern as the Hjarta blueprint
- [[26_TOOL_FUNCTION_CALL_INTERFACE]] — how `ChatMemoryTool.cs` plugs into the LLM
- [[sap:14_MEMORY_DOMAIN]] — SAP's in-process mem0 alternative (compare and contrast)
- [[waifu:30_MEMORY_HANDLING]] — Waifu's cloud-managed memory (compare)
- [[ember:reference_gungnir_db]] — Ember's existing knowledge well, where Hjarta will likely write through

## What This Means for Ember

*Apache-2.0 attribution: ChatdollKit and chatmemory are both Apache-2.0. When adopted into Ember source, preserve upstream header references per Apache-2.0 §4(c).*

**Adopt:**

- **The two-process separation.** Memory lives in its own process; the embodiment layer treats it as a remote service with timeout-and-degrade. Adopt the integrator/service split: `ChatMemoryIntegrator.cs:18` (`new ChatdollHttp(timeout: 10000)`) and Ember's renderer should never hold session state.
- **The four-category schema** (history, summaries, knowledge, diaries) into Hjarta's table set. Apache-2.0 attribution required. The category split has earned its keep across CDK's deployment history.
- **The summary-on-session-switch background task** (`chatmemory.py:1170-1171`). Adopt as Hjarta's session-end consolidation. The cost-curve is right.
- **The dual-embedding cascade** (`embedding_summary` cheap pass, then content fallback gated by `[search:content]`). Adopt as Brunnr's default retrieval strategy.
- **The `UNIQUE (user_id, diary_date)` upsert pattern** for daily consolidation. Forces discipline on the writer.
- **The `get_db_cursor()` zombie-connection health check** (`chatmemory.py:207-237`). Drop into Ember's Postgres helper unmodified.
- **The `openai_base_url` parameter** for LLM-provider agnosticism. Ember's Vow of Pluggable Storage extends to pluggable embedding/LLM endpoints.

**Adapt:**

- **The Unity integrator's silent-swallow on error** — Ember's integrator must queue writes locally when the service is unreachable, retry with backoff, and surface a warning to the user after N failures. The Vow of Tethered Grounding requires the user know when the Well is unreachable; CDK doesn't tell them.
- **The single-table `user_id` partition** — adapt with Postgres RLS so a misconfigured client cannot read another user's rows. This is operator-tier hardening; CDK assumes a benevolent environment.
- **The OpenAI-only LLM client** — adapt to a `MemoryLLMService` interface so Ember's Brunnr can use the same provider abstraction as Munnr ([[20_LLM_SERVICE_INTERFACE]]).
- **The hardcoded embedding dimension at table-create time** — adapt by storing dimension in a metadata table and refusing inserts that mismatch. Provider switches become explicit migrations rather than silent corruption.
- **`utcnow()` calls** — adapt to `datetime.now(timezone.utc)` throughout. Pure correctness fix.

**Avoid:**

- **No auth on the FastAPI surface.** Ember's memory service must require a token, validated at the middleware layer. Deployment behind a trusted reverse proxy is not enough; the service itself should refuse anonymous calls.
- **No vector index by default.** Ember should create `hnsw` or `ivfflat` indexes at table-init, configurable by deployment-size estimate. The default that hurts at scale is not a default; it's a trap.
- **Background-task silence on failure.** Ember's session-switch summarization must log structured errors and expose them through a `/health/memory` endpoint. Silent failure is anti-Vow.
- **The naive `UserId` string field on the Unity prefab.** Ember's equivalent must be set programmatically from a single source of truth, not edited by prefab inspector. Prefab-duplication-as-bug-surface is real.
- **Single LLM client per-deployment.** Adopt provider-pluggability up front.

**Invent:**

- **Hjarta Tiered Recall.** ChatMemory's cascade is two-tier (summary → content). Ember's Hjarta adds a third tier *below* the summary — an even cheaper LSH/MinHash-based "did we ever talk about this topic" filter. Most queries answer "no, never" and bypass the LLM entirely. Vow tie-in: **Smallness** (most queries cost zero LLM calls).
- **Diary Metadata Canon.** ChatMemory's `metadata JSONB` is open-ended. Ember publishes a canonical schema `data/charts/diary_metadata_canon.yaml` defining keys: `location`, `mood`, `runes_drawn`, `weather`, `people_present`, `fate_thread_active`. Operator-extensible but Ember's own subsystems read only canonical keys. Vow tie-in: **Separation of Knowledge and Reasoning**.
- **Audit-Trail-as-Return-Value.** ChatMemory returns `retrieved_data` only when `include_retrieved_data=True`. Ember inverts: every memory answer **always** carries a typed `AuditTrail(query, retrieved_summaries[], retrieved_knowledge[], retrieved_diaries[], llm_model, prompt_hash)`. The renderer can ignore it; the audit log archives it. Vow tie-in: **Defended Builds / Defended Memory**.
- **Tethered-or-Local Hjarta.** ChatMemory assumes the Postgres+FastAPI service is reachable. Ember's Hjarta runs in two modes: **tethered** (writes to Gungnir-style external Well, expected default) and **local** (writes to a SQLite + sqlite-vec fallback when offline). Switching modes is automatic on health-check failure; on reconnect, local writes are merged upstream by `created_at`. Vow tie-in: **Graceful Offline**, **Pluggable Storage**.
- **Right-to-Forget Single-Call.** A single `DELETE /memory/user/{user_id}` route that atomically removes from all four tables and writes a deletion-receipt row. ChatMemory has the parts; Ember welds them. Vow tie-in: **Surface Without Surveillance** generalized to **Right-to-Forget as First-Class**.
- **Cross-Channel Identity Map for ChatMemory.** ChatMemory's `channel` field tags every message with the platform of origin (web, discord, twitch, etc.) but does not normalize identity. Ember pairs ChatMemory with a `channel_identity_map` table — same human on multiple channels becomes the same `user_id`. Vow tie-in: **Federated Self** (a single person across many surfaces is one person to Hjarta).
