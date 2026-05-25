---
codex_id: 65_MEMORY_INTEGRATION
title: Memory Integration — ChatMemory as the Hjarta-and-Brunnr Boundary Lesson
role: Cartographer
layer: Synthesis
status: draft
cdk_source_refs:
  - /tmp/ChatdollKit/Extension/ChatMemory/ChatMemoryIntegrator.cs:10-108
  - /tmp/ChatdollKit/Extension/ChatMemory/ChatMemoryTool.cs
sister_source_refs:
  - /tmp/chatmemory/chatmemory/chatmemory.py:141-1451
  - /tmp/chatmemory/chatmemory/chatmemory.py:239-317
  - /tmp/chatmemory/chatmemory/chatmemory.py:518-596
  - /tmp/chatmemory/chatmemory/chatmemory.py:1066-1138
  - /tmp/chatmemory/chatmemory/chatmemory.py:1140-1451
  - /tmp/chatmemory/chatmemory/chatmemory.py:1149-1175
  - /tmp/chatmemory/docker/run.py:1-28
ember_subsystem_targets: [Hjarta, Brunnr, Strengr, Munnr, Hugarsýn]
cross_refs:
  - 60_TRIANGULATION
  - 63_MULTIMODAL_PIPELINE
  - 64_FUNCTION_CALLING_FOR_EMBODIED
  - chatdoll:1A_MEMORY_DOMAIN
  - chatdoll:38_CHATMEMORY_INTEGRATION
  - sap:14_MEMORY_DOMAIN
  - waifu:30_MEMORY_HANDLING
  - ember:reference_gungnir_db
  - ember:reference_ember_true_names
  - ember:RULES.AI
  - ember:PHILOSOPHY
---

# 65 — Memory Integration

> *Memory is the one subsystem whose boundary you cannot fake. Either the agent owns it in-process and crashes with it, or it lives across a network seam and the agent learns to live without it when it disappears. The seam is the lesson.*
> — Védis Eikleið, reading 1,451 lines of FastAPI and 96 lines of Unity

## 0. Posture — the boundary is the design

ChatMemory is not interesting because of its features. It is interesting because of *where uezo drew the seam*. The Unity-side `ChatMemoryIntegrator.cs` is 96 lines including braces (`/tmp/ChatdollKit/Extension/ChatMemory/ChatMemoryIntegrator.cs:10-108`). The Python-side `chatmemory.py` is 1,451 lines including the FastAPI router (`/tmp/chatmemory/chatmemory/chatmemory.py:141-1451`). The ratio — **15:1 in favour of the service** — is the design statement. Memory is not *inside* the agent. Memory is *across a network boundary*, accessed by the agent through a thin client.

CDK demonstrates the boundary. SAP refuses it (`[[sap:14_MEMORY_DOMAIN]]` keeps mem0 in-process). Waifu hides it (`[[waifu:30_MEMORY_HANDLING]]` lets the vendor own it). The three corpora hold three different bets on memory locality, and Ember has to choose.

I propose that Ember adopts CDK's boundary wholesale, and uses it to *finally* draw the line between Hjarta and Brunnr that the Six True Names doc has gestured at but never settled. The line, stated plain: **Hjarta is in-process and fast; Brunnr is across a seam and durable; the seam is typed messages over HTTP; the Forge-B doc at `[[chatdoll:38_CHATMEMORY_INTEGRATION]]` shows what the implementation looks like.** This synthesis sits above that execution doc and develops the structural argument.

I walk the boundary. I name what Hjarta owns and what Brunnr owns. I identify three classes of memory (working / episodic / factual) and assign each to a True Name. I propose the Hjarta-Brunnr Transit Protocol — the four typed messages that cross the seam. I propose `Tethered-or-Local Hjarta` (Forge-B sketched this; I formalise the state machine). I close with the question SAP got wrong: *whose process does memory crash with?*

## 1. The three corpora bet on memory locality

| Corpus | Memory location | Failure shape | Identity ownership | Coupling |
|---|---|---|---|---|
| **SAP** (mem0 in-process) | Inside `server.py`'s Python process | Agent crash takes memory with it | Operator's filesystem | Tight — schema changes require agent restart |
| **Waifu** (cloud-managed) | Inside vendor's GPU-farm-side state | Vendor crash takes memory; vendor pivots take memory | Vendor's database | Total — operator owns nothing |
| **CDK** (ChatMemory service) | Across HTTP seam to FastAPI + Postgres | Service crash leaves agent functional, memory dark | Operator's Postgres instance | Loose — schema changes go through API version |

Three bets. Three failure shapes. The bet that *survives the agent-crash failure mode* is CDK's. The bet that *survives the vendor-pivot failure mode* is also CDK's (the operator can self-host or migrate; the Apache-2.0 license posture extends to the sister project, which is also Apache-2.0). The bet that *survives any future schema evolution gracefully* is also CDK's — versioning the API is easier than versioning a co-located library.

Ember's True Name structure already prefigures this choice. Brunnr is *the Well*: a named place separate from the agent, with its own contract. Hjarta is *the Heart*: in-process state, fast, sovereign. The Six True Names doc (`[[ember:reference_ember_true_names]]`) describes the split conceptually; ChatMemory shows what the implementation looks like.

## 2. Three classes of memory — and the True Name each belongs to

ChatMemory's four tables (history, summaries, knowledge, diaries — see `[[chatdoll:38_CHATMEMORY_INTEGRATION]]`) collapse, for the purposes of this synthesis, into **three structural classes**:

| Class | Examples in ChatMemory | Lifetime | Latency requirement | Locality |
|---|---|---|---|---|
| **Working** | the current dialog turn, mid-stream tokens, active `LLMSession` state | seconds-to-minutes | sub-millisecond | in-process |
| **Episodic** | `conversation_history` (raw transcripts), `conversation_summaries` (per-session LLM summaries with dual embeddings) | days-to-months | tens-of-milliseconds | across-seam |
| **Factual** | `user_knowledge` (curated facts), `diaries` (date-keyed entries) | months-to-years | tens-of-milliseconds | across-seam |

The three classes have categorically different requirements. Working memory cannot afford a network hop; the LLM is generating tokens at ~30/s and waiting on a Postgres query for each token would be ruinous. Episodic and factual memory *cannot afford to live in-process*; the agent crash must not destroy the operator's diary.

The True Name assignment that follows:

- **Hjarta** owns **working** memory. The current session's state, the active dialog tree, the streaming buffer, the mid-utterance affect — all of it lives in-process inside Hjarta. Hjarta crashes; the current turn is lost. The operator restarts; the next turn starts fresh.
- **Brunnr** owns **episodic** and **factual** memory. Conversations past, summaries, knowledge, diaries — all of it lives across the seam in Gungnir (PG18 + pgvector, per `[[ember:reference_gungnir_db]]`). Brunnr crashes; the agent goes memory-blind but keeps responding. The operator restores Brunnr; full memory comes back online.

The Forge-B doc at `[[chatdoll:38_CHATMEMORY_INTEGRATION]]` argues this from the ChatMemory side: the 96-line Unity client is *Hjarta's* shape; the 1,451-line FastAPI service is *Brunnr's* shape. The Cartographer's contribution is naming the structural rule:

**The Hjarta-Brunnr Rule:** *in-process fast / across-seam durable, with typed messages at the seam, and the agent stays alive when the seam goes dark.*

## 3. What lives in Hjarta, exactly

Hjarta's working set, derived from CDK's `AIAvatar` + `DialogProcessor` state and Ember's Six True Names:

1. **The active dialog state** — current mode (`Idle`/`Conversation`/`Sleep`), wake-word detection state, conversation timeout countdown.
2. **The active LLM session** — provider, model, accumulated context (the `Contexts` list), streaming buffer, parsed thinking-tag state.
3. **The active turn's affect colouring** — the read-only-for-tone affect signal that `[[63_MULTIMODAL_PIPELINE §3.2]]` describes.
4. **The active pipeline stage** — which of the seven stages is currently running (per `[[63_MULTIMODAL_PIPELINE §1]]`).
5. **The active tool call** — when a `[[64_FUNCTION_CALLING_FOR_EMBODIED]]` invocation is in flight, the `ToolCall` + `ToolManifest` + consent state lives here until the `Receipt` is written.
6. **Recent receipt cache** — the last N (default 16) tool receipts, for Hugarsýn projection and operator inspection without a Brunnr round-trip.
7. **The active session ID** — generated at session-start, the key under which episodic memory writes will eventually flush to Brunnr.
8. **The pending writes queue** — receipts and history rows queued for Brunnr write; flushed asynchronously or on session end.

Hjarta is *Python in-process state*. No DB, no disk except for crash-recovery checkpoint. Its restart cost is *one session of context*. If Hjarta crashes mid-utterance, the doll forgets the current utterance and re-establishes from the operator's next input. This is acceptable; an agent that *cannot survive its own crashes* by restarting is structurally broken.

The Smallness Vow argues here: Hjarta's state must fit in the operator's mental model. Eight items. Each operator-visible (Hugarsýn projects every one of them). No hidden state in Hjarta.

## 4. What lives in Brunnr, exactly

Brunnr's durable set, derived from ChatMemory's four tables plus Ember's existing Gungnir schema:

1. **`conversation_history`** — every turn of every session, keyed by `(user_id, session_id, channel)`. ChatMemory's table; Ember adopts wholesale.
2. **`conversation_summaries`** — LLM-generated session summaries with the dual-embedding cascade (`embedding_summary` cheap pass, `content_embedding` content fallback). ChatMemory's table; Ember adopts.
3. **`user_knowledge`** — operator-curated factual statements. Single vector. Operator-writable, not LLM-writable by default (LLM writes go through a `gated_action` tool — see `[[64_FUNCTION_CALLING_FOR_EMBODIED §5]]`).
4. **`diaries`** — date-keyed daily entries with `UNIQUE (user_id, diary_date)` upsert. Vector + date-range query. Operator-writable, LLM-writable through a `announced_write_local` tool.
5. **`tool_receipts`** — the audit log proposed in `[[64_FUNCTION_CALLING_FOR_EMBODIED §6.4]]`. Every Smiðja invocation produces a receipt; the receipt lives in Brunnr. Ember adds this table; ChatMemory doesn't have it.
6. **`hugarsyn_snapshots`** — periodic snapshots of Hugarsýn's projection state, for replay and audit. Ember adds; ChatMemory doesn't have.
7. **`session_metadata`** — per-session context (`session.context = "private-journal" | "livestream" | "commute"`), provider mix, latency-budget P50/P95. Ember adds.
8. **`channel_identity_map`** — the multi-channel-identity table proposed in `[[chatdoll:38_CHATMEMORY_INTEGRATION §What This Means / Invent]]`. Same human across web/Discord/Twitch becomes one `user_id`.

Brunnr is **the existing Gungnir database** (PG18 + pgvector, `[[ember:reference_gungnir_db]]`) extended with the ChatMemory-derived tables. The existing Gungnir tables (95 docs, 35k chunks) coexist with the new tables; the ingest pathway is already in place.

The Apache-2.0 license posture of ChatMemory means Ember can vendor the schema SQL and the search-cascade Python directly, with attribution. The Forge-B doc at `[[chatdoll:38_CHATMEMORY_INTEGRATION §What This Means]]` enumerates the adopt list per-line; this synthesis affirms the choice at the boundary level.

## 5. The Hjarta-Brunnr Transit Protocol — four typed messages

The seam between Hjarta and Brunnr carries exactly four message types. Anything that needs to cross is one of these four. The protocol is intentionally narrow; anything wider is a leak.

### 5.1 `WriteHistory(session_id, user_message, assistant_message, channel)`

Sent at the end of every turn. Hjarta accumulates the user/assistant pair; on turn-complete, sends one POST to Brunnr (`POST /history` on the ChatMemory-derived router). Brunnr inserts into `conversation_history`. Brunnr's side-effect: if the `session_id` differs from the previous most-recent session for this user, Brunnr schedules a background `create_summary()` for the previous session (the ChatMemory pattern at `chatmemory.py:1149-1175`).

Failure handling: Hjarta queues the write locally (in-memory ring buffer, default 64 entries) when Brunnr is unreachable. Reconnect triggers drain. Buffer overflow logs a structured warning and oldest entries are kept (the most recent dialogue is more recoverable from operator memory than the oldest).

### 5.2 `WriteReceipt(receipt)`

Sent at the end of every Smiðja invocation. Hjarta accumulates the receipt; flushes immediately for `announced_write_external` and `gated_action` (high audit value), batches for `silent_read` (low audit value, batched every 30s or 16 receipts).

Failure handling: receipts are *never* dropped. On Brunnr unreachable, receipts spill to `~/.ember/spill/receipts/` and are replayed on reconnect.

### 5.3 `Query(query_text, user_id, session_context, top_k, since, until)`

The retrieval call. Sent whenever Strengr needs context for the LLM prompt. Brunnr runs the dual-embedding cascade (cheap summary pass, content fallback gated by `[search:content]` from a Brunnr-internal LLM call). Returns a `SearchResult(answer, retrieved_summaries[], retrieved_knowledge[], retrieved_diaries[], retrieved_receipts[], audit_trail)`.

Failure handling: on Brunnr unreachable, the query returns an empty `SearchResult` with `error: "brunnr_unreachable"`. Strengr proceeds without retrieval context; the doll's reply notes the absence ("I can't reach my memory right now, so I'm answering from this conversation only"). Embodied Honesty Vow at work.

### 5.4 `ProjectHugarsyn(snapshot)`

Periodic Hugarsýn snapshot push from Hjarta to Brunnr. Lower-priority; once per minute or on significant state change. Brunnr writes to `hugarsyn_snapshots`. Used for after-the-fact replay, debugging, audit.

Failure handling: drops silently on Brunnr unreachable (snapshots are *eventually-consistent* by design; missing some is acceptable). Logs a structured event on N consecutive failures.

---

Four message types. Four failure-handling postures. No fifth type without an ADR.

The narrowness is the point. The 96-line `ChatMemoryIntegrator.cs` carries exactly two of these (Write + Query); Ember carries four because Ember's audit and projection layers are heavier. But the *shape* — narrow, typed, network-aware-but-graceful — is CDK's.

## 6. Tethered-or-Local Hjarta — the two-mode state machine

Forge-B sketched this in `[[chatdoll:38_CHATMEMORY_INTEGRATION §What This Means / Invent]]`. I formalise the state machine.

Hjarta runs in one of two modes:

- **`Tethered`** — Brunnr is reachable; writes go through; queries return real data. Default mode. Hugarsýn projects `hjarta.mode = "tethered"`.
- **`Local`** — Brunnr is unreachable; writes spool to `~/.ember/spill/`; queries return empty + warning. The doll continues operating, narrowing its memory horizon to the active session only. Hugarsýn projects `hjarta.mode = "local"`.

The transitions:

```
                  ┌─────────────────────┐
                  │     Tethered        │
                  │  (Brunnr reachable) │
                  └─────────┬───────────┘
                            │
                  health-check fails
                  (3 consecutive failures
                   or explicit network error)
                            │
                            ▼
                  ┌─────────────────────┐
                  │       Local         │
                  │  (Brunnr dark)      │
                  │  spill-to-disk      │
                  │  warn-on-query      │
                  └─────────┬───────────┘
                            │
                  health-check passes
                  (1 successful ping)
                            │
                            ▼
                  ┌─────────────────────┐
                  │   Reconnecting      │
                  │   (drain spill,     │
                  │    no new writes    │
                  │    cross seam)      │
                  └─────────┬───────────┘
                            │
                  drain complete
                            │
                            ▼
                       Tethered
```

The reconnection drain is ordered: receipts first (audit priority), history second, snapshots last. Each spill file is timestamped; conflicts resolve by `created_at`.

The Vow tie-in is multiple:

- **Embodied Honesty**: when Hjarta is `Local`, the doll *says so* on the next memory-dependent question. "I can't reach my memory right now" is honest; pretending the memory is intact would not be.
- **Surface Without Surveillance**: spilled receipts on disk are encrypted at rest with the operator's key (or `~/.ember/keys/spill.key` if the operator hasn't set up one). Spill files are not world-readable.
- **Smallness**: the state machine has two modes plus one transient. No hidden states. Operator-readable.
- **Tiered Presence**: at lower tiers (T-1, T0), Hjarta may run in *permanently-Local* mode if Brunnr is too heavy for the deployment. The Tiered-Presence Vow allows this; the Embodied Honesty Vow requires the doll to know.

## 7. The summary-on-session-switch lesson

ChatMemory's quietest cleverness is the background summary trigger (`chatmemory.py:1149-1175`): on every `POST /history`, the service checks whether `session_id` changed since the last write; if so, it schedules `create_summary()` for the *previous* session as a `BackgroundTask`. The user never asks. Summaries appear lazily, between sessions, off the critical path.

The cost-curve is right:

- One LLM call (summary generation) + two embedding calls (summary vector + content vector) per session-switch.
- A user with 5 sessions per day: 5 summary cycles per day. Cheap.
- The cost grows with the number of session-switches, not the number of turns. Long conversations within a session pay no consolidation cost during the session.

The pattern generalises. *Lazy consolidation at boundaries* is the right shape for many memory operations:

- **Diary consolidation**: at end-of-day (operator-defined, or midnight in operator's TZ), Brunnr consolidates the day's history into a `diaries` upsert.
- **Knowledge promotion**: when a fact recurs across N sessions, Brunnr promotes it from `conversation_summaries` to `user_knowledge`. The threshold is operator-tunable.
- **Identity merging**: when `channel_identity_map` accumulates evidence that two channel-specific `user_id` values belong to one human, Brunnr consolidates on a configurable confidence threshold.

Ember adopts the *lazy-at-boundary* pattern as a general principle, not just for summaries. Brunnr's background-task layer is the engine; the boundary events (session-switch, day-end, threshold-crossing) are the triggers.

The cost is the silent-failure mode that the Forge-B doc flags: FastAPI's `BackgroundTasks` swallows exceptions. Ember must wrap each task in a `try/except` that writes a typed `BackgroundTaskFailureEvent` to a `/health/memory` surface. Operator can read the surface and know when consolidation has been failing.

## 8. The dual-embedding cascade as the retrieval default

ChatMemory's `search()` cascade (`chatmemory.py:1066-1138`):

1. Embed the query.
2. Vector-search `embedding_summary` (cheap, high-precision) for top-k summaries.
3. Vector-search `embedding` on `user_knowledge` for facts.
4. Vector-search `embedding` on `diaries` for date-bracketed events.
5. Concatenate; feed to LLM with retrieval system prompt; get an answer.
6. *If the LLM emits `[search:content]`*, fall back to full-content search on `embedding_summary` and re-query.

The cascade has three structural properties Ember should adopt verbatim:

- **Cheap-first**: the summary embedding is a much smaller representation than the full content embedding; the cheap pass returns N candidates at low cost.
- **LLM-as-retrieval-decider**: rather than a hard relevance threshold, the LLM itself decides whether the retrieved data is sufficient. The decision is a typed token (`[search:content]`); the cascade is self-tuning.
- **At-most-two-LLM-calls per query**: the cascade has a depth bound. Worst case: cheap pass → LLM says insufficient → content pass → LLM responds. Two LLM calls. Bounded latency.

Brunnr's default retrieval is this cascade. The Hjarta-Brunnr `Query` message of §5.3 maps directly. The Audit-Trail-as-Return-Value invention from the Forge-B doc means the returned `SearchResult` *always* carries `retrieved_data`; Munnr can render the evidence trail on operator request.

The thesis from `[[chatdoll:38_CHATMEMORY_INTEGRATION §What This Means / Invent]]`'s **Hjarta Tiered Recall**: add a *third tier* below the cheap embedding pass — an LSH/MinHash filter that answers "did we ever talk about this topic" in microseconds. Most queries answer "no, never" and bypass the LLM entirely. The cost-curve goes from O(N summaries) per query to O(1) for the "no" case.

I affirm the proposal. The three-tier cascade — LSH cheap-no → embedding-summary cheap-pass → content-fallback expensive — gives Brunnr a budget-aware retrieval surface that the Smallness Vow can actually defend.

## 9. The audit-trail-as-return-value pattern

Forge-B proposed and I affirm: every Brunnr query returns *both* an answer and the evidence trail.

```python
@dataclass(frozen=True)
class SearchResult:
    answer: str                                # LLM-composed reply
    retrieved_summaries: list[SummaryRecord]   # what fed the answer
    retrieved_knowledge: list[KnowledgeRecord]
    retrieved_diaries: list[DiaryRecord]
    retrieved_receipts: list[ReceiptRecord]    # Ember addition
    llm_model: str                             # which model composed
    prompt_hash: str                           # for reproducibility
    audit_trail: AuditTrail                    # full chain
    elapsed_ms: int
```

Three users of this return value:

- **Strengr** reads `answer` and feeds it to the LLM prompt as retrieved context.
- **Hjarta** archives the full `SearchResult` to the receipt log (per §4 #5: `tool_receipts`, but extended for retrieval calls too).
- **Munnr** can render the trail on operator request: "where did you get that answer from?" → the doll lists the summaries, knowledge, diaries, receipts that fed the reply.

The trail makes Brunnr's behaviour legible. Operator can audit the retrieval pathway, not just the answer. Vow tie-in: **Defended Memory** — the operator can always see how the doll's memory composed its answer.

CDK's `include_retrieved_data: bool = False` (default off) is inverted. Ember's audit posture says the trail is *always* present; the renderer can choose to hide it. The cost is the wire-format size; a network response carries the trail data even when the operator doesn't ask. This is acceptable; Brunnr is across-seam and the operator's network is the operator's network.

## 10. The OpenAI-base-URL pluggability — extended

ChatMemory's `openai_base_url` parameter (`chatmemory.py:173`) means the service works against Ollama, Together, Groq, llama-server — any OpenAI-compatible endpoint. The provider choice is per-deployment, not per-build.

Ember extends this pluggability across both axes of LLM use:

- **Brunnr's internal LLM** (for cascade decisions and summary generation) uses an OpenAI-compatible endpoint configured per-deployment in `~/.ember/brunnr.yaml`.
- **Brunnr's embedding model** is configured similarly, with the dimension-mismatch fix from Forge-B's adapt list (the dimension is stored in a metadata table; inserts that mismatch are refused).
- **Strengr's external LLM** (for user-facing dialog) is separately configured; the two LLMs can be different. The Brunnr-internal LLM might run on local Ollama (cheap, private, fast); the user-facing LLM might run on Anthropic (high quality, low latency).

The two-LLM split is meaningful. Most memory operations don't need a SOTA model; the summary task is closer to compression than to reasoning. Running Brunnr's LLM on a 7B local model and Strengr's LLM on Claude is a *valid and economical* deployment shape. The Pluggable Storage Vow generalises to Pluggable Reasoning at the memory layer.

This is the deployment-shape conversation that SAP's in-process mem0 cannot have. mem0 is bound to whatever LLM SAP's `server.py` is configured to use; you can't split. CDK's separate FastAPI service makes the split natural.

## 11. The right-to-forget contract

ChatMemory has per-table delete routes (`delete_history`, `delete_summaries`, `delete_knowledge`, `delete_diary`) but no convenience endpoint. A right-to-forget for a `user_id` requires four DELETE calls.

Forge-B's invented `Right-to-Forget Single-Call` is the right shape. I affirm and extend:

```
DELETE /brunnr/user/{user_id}/forget?confirm={token}

Effect:
  - DELETE FROM conversation_history WHERE user_id = $1
  - DELETE FROM conversation_summaries WHERE user_id = $1
  - DELETE FROM user_knowledge WHERE user_id = $1
  - DELETE FROM diaries WHERE user_id = $1
  - DELETE FROM tool_receipts WHERE user_id = $1
  - DELETE FROM hugarsyn_snapshots WHERE user_id = $1
  - DELETE FROM session_metadata WHERE user_id = $1
  - INSERT INTO deletion_receipts (user_id, deleted_at, requested_by, table_counts) VALUES (...)

Returns:
  {
    "deleted_at": "...",
    "table_counts": {"conversation_history": 1234, ...},
    "deletion_receipt_id": "uuid",
  }
```

Atomic. Idempotent. Records the *fact* of deletion in `deletion_receipts` (the deletion-itself is not deleted; that would be dishonest). The `confirm` token is operator-side, fetched from a separate endpoint, ensuring the call is intentional.

The Vow tie-in: **Surface Without Surveillance** generalised. The operator can withdraw consent for memory wholesale; the system honours it; the system records that it honoured it. The right-to-forget is *first-class*, not bolted on.

## 12. Where the boundary leaks — and the patches

CDK's boundary has known leaks. The Forge-B doc catalogs them; the patches Ember must apply:

| Leak | Patch |
|---|---|
| No auth on FastAPI surface | Bearer-token middleware required; token rotation; per-token scope (read-only / read-write / admin) |
| `user_id` as only partition | Postgres RLS policies per-table; misconfigured client cannot cross-read |
| OpenAI hardcoded LLM | `openai_base_url` is good but dimension lock-in must be addressed; dimension stored in metadata table, mismatched inserts refused |
| Background tasks silent on failure | `BackgroundTaskFailureEvent` written to `/health/memory` surface; operator-readable |
| No vector index | HNSW or IVFFlat at table-init, deployment-size-configurable |
| Unity integrator silent-swallow | Spill-to-disk + replay + operator warning after N consecutive failures (Tethered-or-Local mode of §6) |
| Plaintext `UserId` Inspector field | Single source of truth at `~/.ember/identity.yaml`; clients read from one place |
| `[search:content]` cascade can double latency | Per-query timeout caps total cascade time; partial result returned on cascade-timeout with explicit `cascade_timed_out: true` |
| No GDPR convenience route | Single-call right-to-forget per §11 |
| `utcnow()` deprecation | `datetime.now(timezone.utc)` throughout |

Each patch is small, named, and Ember-original. The Apache-2.0 license posture means we can fork or patch upstream; we don't need to wait on uezo. The Forge-B doc enumerates per-line patches; this synthesis flags them at the boundary level.

## 13. Cross-References

- `[[60_TRIANGULATION]]` — three-corpus matrix; ChatMemory is the corpus that named the boundary
- `[[63_MULTIMODAL_PIPELINE]]` — Strengr's retrieval call sits inside the pipeline; the Query message of §5.3 is the seam
- `[[64_FUNCTION_CALLING_FOR_EMBODIED]]` — Smiðja's tool receipts cross the same seam as the memory writes
- `[[chatdoll:1A_MEMORY_DOMAIN]]` — Architect's domain-level view of CDK's memory layer
- `[[chatdoll:38_CHATMEMORY_INTEGRATION]]` — Forge-B's per-line implementation analysis; this synthesis sits above it
- `[[sap:14_MEMORY_DOMAIN]]` — SAP's in-process mem0; the counter-example
- `[[waifu:30_MEMORY_HANDLING]]` — Waifu's vendor-owned memory; the cautionary counter-example
- `[[ember:reference_gungnir_db]]` — Brunnr's existing substrate (PG18 + pgvector at gungnir:5432)
- `[[ember:reference_ember_true_names]]` — the Six True Names; this doc settles the Hjarta-Brunnr boundary
- `[[ember:RULES.AI]]`, `[[ember:PHILOSOPHY]]` — Smallness, Embodied Honesty, Tethered Grounding

## What This Means for Ember

**Adopt:**

- **The Hjarta-Brunnr boundary** as drawn here. In-process working memory in Hjarta; across-seam episodic and factual memory in Brunnr. The boundary is *the* lesson from ChatMemory; everything else hangs on it.
- **ChatMemory's four-table schema** (`conversation_history`, `conversation_summaries`, `user_knowledge`, `diaries`) directly into Brunnr's extension. Apache-2.0 attribution required. Schema SQL vendored from `chatmemory.py:239-317` with header reference preserved.
- **The summary-on-session-switch background trigger** (`chatmemory.py:1149-1175`). The lazy-at-boundary pattern; Brunnr's session-end consolidation. The cost-curve is right.
- **The dual-embedding cascade** (`embedding_summary` cheap pass; content fallback gated by `[search:content]`). Brunnr's default retrieval strategy. `chatmemory.py:1066-1138`.
- **The `get_db_cursor()` zombie-connection health check** (`chatmemory.py:207-237`) unmodified into Brunnr's Postgres helper. Operator-grade resilience earned through CDK's deployment history.
- **The `openai_base_url` pluggability** as Brunnr's LLM client config. Operator chooses per-deployment; Brunnr-internal LLM and Strengr's user-facing LLM can be different.
- **The 15:1 line-count ratio** as a design statement. The Unity client is 96 lines; the FastAPI service is 1,451. Hjarta's thin-client and Brunnr's thick-service is the right shape.

*Apache-2.0 attribution: ChatdollKit and chatmemory are both Apache-2.0. When adopted into Ember source, preserve upstream header references per Apache-2.0 §4(c).*

**Adapt:**

- **The Unity integrator's silent-swallow on error** — adapt to the **Tethered-or-Local Hjarta** state machine of §6. Spill to `~/.ember/spill/` on Brunnr unreachable; replay on reconnect; warn the operator. Embodied Honesty Vow requires the operator know when memory is dark.
- **The `user_id` partition** — adapt with Postgres Row Level Security policies per-table. A misconfigured client cannot read another user's rows even if it sends the wrong `user_id`. ChatMemory assumes benevolent environment; Ember must not.
- **The OpenAI-only LLM client** — adapt to a `BrunnrLLMService` interface mirroring Strengr's `LLMService` shape. Same provider abstraction as `[[64_FUNCTION_CALLING_FOR_EMBODIED §2]]`. Brunnr's LLM and Strengr's LLM share the abstraction layer but are independently configured.
- **The hardcoded embedding dimension at table-create time** — adapt by storing dimension in a `brunnr_metadata` table; inserts that mismatch are refused. Provider switches become explicit migrations, not silent corruption.
- **The two-table CDK memory surface** (`AddHistory`, `SearchMemory`) — adapt to the **four-message Hjarta-Brunnr Transit Protocol** of §5: `WriteHistory`, `WriteReceipt`, `Query`, `ProjectHugarsyn`. Narrow seam; explicit message types; nothing wider without an ADR.
- **`utcnow()` deprecation** — adapt to `datetime.now(timezone.utc)` throughout. Pure correctness fix; carry through the vendored SQL helpers too.

**Avoid:**

- **In-process memory store (SAP's mem0 pattern).** The agent crash takes the operator's history. The schema-evolution coupling is tight. The deployment-shape conversation is closed. Refused.
- **Vendor-owned memory (Waifu's pattern).** Identity ownership lies with the vendor. Vendor pivot is data loss. Refused.
- **No-auth FastAPI surface.** Brunnr requires bearer-token middleware; tokens rotate; per-token scope. Trust-the-network is not a posture Ember can afford.
- **No vector index by default.** HNSW or IVFFlat at table-init; deployment-size-configurable. The default that hurts at scale is a trap.
- **Background-task silence on failure.** Each background task wraps in `try/except`; failures write structured events to `/health/memory`. Operator can read.
- **Single LLM client per-deployment.** Two-LLM split is meaningful; pluggability up front.
- **Per-table DELETE for right-to-forget.** Single atomic endpoint per §11. Right-to-forget is first-class.
- **Logging of full conversation content in plaintext at the Brunnr server.** ChatMemory does this in `Debug.Log`-equivalents on the Python side. Ember's audit logging is structured, redacted by manifest, and separately scoped from operational logs.

**Invent:**

- **The Hjarta-Brunnr Rule** as a named design law: *in-process fast / across-seam durable, with typed messages at the seam, and the agent stays alive when the seam goes dark.* The rule is the load-bearing structural finding of this doc. Every future memory-adjacent design decision tests against it.
- **The four-message Hjarta-Brunnr Transit Protocol** (`WriteHistory`, `WriteReceipt`, `Query`, `ProjectHugarsyn`). Narrow seam; ADR-gated additions; failure-handling-explicit-per-message. The protocol is the contract; the schema is implementation.
- **The Tethered-or-Local Hjarta state machine** of §6, with spill-to-disk encrypted at rest, ordered drain on reconnect (receipts first), and operator-visible mode in Hugarsýn. Graceful Offline as Vow tie-in.
- **The three-class memory taxonomy** (working / episodic / factual) with explicit True-Name assignment. Working in Hjarta. Episodic and factual in Brunnr. The taxonomy is the membership rule; future tables get placed by class.
- **Hjarta Tiered Recall** (Forge-B's invention, affirmed and developed): three-tier cascade — LSH cheap-no → embedding-summary cheap-pass → content-fallback expensive. Most queries answer "no, never" in microseconds and bypass the LLM entirely. Smallness Vow defended at the retrieval level.
- **The Audit-Trail-as-Return-Value pattern**: every Brunnr query returns both answer and trail; Hjarta archives both; Munnr can render the trail on request. Defended Memory Vow at the query level.
- **The Right-to-Forget Single-Call** of §11. Atomic across all Brunnr tables; deletion-receipt written; idempotent. Right-to-forget is first-class, not bolted on.
- **The two-LLM deployment shape**: Brunnr-internal LLM (cheap, local, for summary/cascade decisions) and Strengr's user-facing LLM (high-quality, for dialog). The split is structurally available because the boundary is across-seam. Pluggable Reasoning Vow at the memory layer.
- **The Diary Metadata Canon** (Forge-B's invention, affirmed): canonical schema for `diaries.metadata` JSONB keys (`location`, `mood`, `weather`, `people_present`, etc.). Operator-extensible but Ember's own subsystems read only canonical keys. Separation of Knowledge and Reasoning Vow.
- **The deletion-receipt ledger.** Every right-to-forget writes a row to `deletion_receipts` that itself cannot be forgotten. The fact of deletion is durable; the deleted data is not. The operator can audit *that* memory was forgotten without seeing *what*. Embodied Honesty at the meta-memory level.
- **The Hugarsýn projection of Brunnr health.** `/hugarsýn/brunnr` returns `{reachable: bool, last_successful_query_at, recent_failure_count, mode_history: [...]}`. Every party peer can see whether this Ember's memory is dark. Federation-aware Tethered Grounding.

---

*Apache-2.0 attribution: ChatdollKit and chatmemory are both Apache-2.0. When adopted into Ember source, preserve upstream header references per Apache-2.0 §4(c).*

96 lines on the doll side; 1,451 lines on the service side. The ratio is the design statement. Hjarta is what crashes with the agent and restarts in seconds; Brunnr is what survives and waits across the seam. The four messages carry the seam. The state machine survives the dark. The cascade is cheap-first. The audit is always returned. The right-to-forget is one call. The Hjarta-Brunnr Rule is what makes Ember's memory a thing the operator can trust — because it can fail honestly, and the doll keeps talking when it does.
