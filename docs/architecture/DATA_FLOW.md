# DATA_FLOW — How Ember Lives in Motion

**Voice:** Cartographer (Védis Eikleið)
**Status:** Ratified 2026-05-21 by Volmarr. Canonical. The Runa-shaped predecessor is preserved at `docs/archive/runa-inherited/architecture/DATA_FLOW.md` for lineage reference.
**Last touched:** 2026-05-21 (promoted from `EMBER_DATA_FLOW.md` at ratification)
**Reads with:** `ARCHITECTURE.md` (shape), `DOMAIN_MAP.md` (ownership), `docs/SYSTEM_VISION.md` (intent).

---

## 1. The grammar

Every flow in Ember is built from a small set of primitives:

| Primitive | Type | Meaning |
|---|---|---|
| **Operator input** | external | A line typed at `ember chat`, an argument to `ember ask "…"`, an answer to a Hjarta prompt. |
| **Munnr call** | function | `Munnr` parses input into a typed command. |
| **Strengr access** | function | `Strengr` hands back a `BrunnrHandle` (live) or a `Disconnected` value (honest failure). |
| **Brunnr query** | function | A typed retrieval against the Well — vector, text, or hybrid. |
| **Funi turn** | function | One LLM call with assembled context and optional tool slot. |
| **Smiðja job** | function | A unit of ingest: chunk + embed + deposit. May be batched. |
| **Episode** | a row written to Brunnr's `episodes` table | A remembered turn (operator input, Ember reply, retrieval hits, timestamps). |

Every flow below is a sequence of these primitives. There are exactly **three** canonical flows in Ember:

1. The **conversation turn** — operator asks, Ember answers.
2. The **ingest job** — operator (or scheduler) adds new content to the Well.
3. The **first-run rite** — Hjarta wires the realms together.

There are no other flows that ship in the first slice. New flows require an ADR.

---

## 2. Flow A — the conversation turn

### 2.1 Happy path

```
[1] Operator types a line at `ember chat`
    │
    ▼
[2] Munnr parses the line into a typed `AskTurn(text, time)`
    │
    ▼
[3] Munnr asks Strengr for a Well handle.
    │   ┌─────────────────────────────────────────────────────────────┐
    │   │  Strengr.open(well_config) → BrunnrHandle | Disconnected     │
    │   └─────────────────────────────────────────────────────────────┘
    │
    ▼
[4] Munnr calls Funi.embed(text)  →  qvec  (or, if Funi cannot embed,
    │                                       Strengr asks Smiðja's embed
    │                                       client at the configured
    │                                       endpoint.)
    │
    ▼
[5] Munnr calls BrunnrHandle.hybrid_search(qvec, text, k=8)
    │       returns list[RetrievalHit] (chunk + document title + score)
    │
    ▼
[6] Munnr assembles a Funi prompt:
    │       · system prompt (from ~/.ember/identity/)
    │       · last N episodes (read from Well)
    │       · retrieved chunks, with attribution
    │       · the operator's line
    │
    ▼
[7] Munnr calls Funi.complete(prompt, context, tools=None)
    │       returns FuniReply(text, tool_calls=None, finish_reason)
    │
    ▼
[8] Munnr renders the reply, with citations to retrieved chunks.
    │
    ▼
[9] Munnr writes the Episode back to the Well (Brunnr.add_episode).
    │
    ▼
[10] Loop back to [1] (REPL) or exit (one-shot ask).
```

The flow is **synchronous**. There is no event bus, no kernel, no concurrent retrieval+inference path. The Vow of Smallness allows this; if first-slice profiling on a Pi shows retrieval latency dominating, we add an *internal* parallelism in Munnr — not an event bus.

### 2.2 Sad path — the Well is unreachable

```
[3'] Strengr.open(well_config) → Disconnected(reason="conn_refused", since=…)
    │
    ▼
[4'] Munnr notes the disconnect, sets a turn-local flag.
    │
    ▼
[5'] Munnr skips retrieval. No hits.
    │
    ▼
[6'] Funi prompt is assembled WITHOUT retrieval, WITH an explicit
    │   system-side note: "Your well is unreachable. Do not invent
    │   facts. If asked about specific content, name your limit
    │   honestly."
    │
    ▼
[7'] Funi.complete(prompt_without_retrieval, …)
    │
    ▼
[8'] Munnr renders the reply AND a one-line banner:
        "well: disconnected (conn_refused, since 03:42) — reply is
         ungrounded; run `ember doctor` for diagnosis."
    │
    ▼
[9'] Munnr writes the Episode locally to ~/.ember/state/pending_episodes/
    │   (a tiny SQLite file). When the Well comes back, Hjarta or a
    │   `ember well drain` flushes these in.
```

This is the Vow of Graceful Offline in flow form. Ember **never** hides being disconnected. She **never** invents facts to fill the silence. The sad path is a first-class flow, not an afterthought.

### 2.3 Sad path — Funi is unavailable

If Funi cannot complete (model not loaded, OOM, runtime crashed), Munnr exits the turn with a clean error and continues to be usable for non-Funi commands. The operator can run `ember doctor` to see what is wrong.

---

## 3. Flow B — the ingest job

### 3.1 Single-source ingest (a directory of `.md` files)

```
[1] Operator: `ember well ingest ~/notes/`
    │
    ▼
[2] Munnr parses into IngestJob(source=Path, options).
    │
    ▼
[3] Munnr asks Strengr for the Well handle.
    │   (Same Disconnected handling as Flow A: ingest cannot proceed
    │    if the Well is unreachable; Munnr says so and exits.)
    │
    ▼
[4] Munnr hands the job to Smiðja.local_files.run(handle, job).
    │
    ▼
[5] Smiðja walks the source, producing a stream of (path, bytes,
    │   content_type) tuples. Each goes through:
    │       a. hash → check duplicate via Brunnr.has_document(hash)
    │       b. parse to text per content_type
    │       c. chunk to ~1684 chars (Gungnir-aligned default)
    │       d. batch-embed via the configured embedding endpoint
    │       e. write Document + Chunks via Brunnr.
    │
    ▼
[6] Smiðja journals progress to ~/.ember/state/smidja_progress/<job>.json
    │   (resumable: if killed at chunk 4000 of 12000, re-running the
    │    same job continues from 4000).
    │
    ▼
[7] On completion, Smiðja returns IngestSummary(n_docs, n_chunks,
    │   n_failed, elapsed_s).
    │
    ▼
[8] Munnr renders the summary to the operator.
```

### 3.2 Why this matters for the toaster story

Smiðja is the most expensive flow in Ember. Embedding generation on a Pi is slow. The journal is what makes ingest *bearable*: the operator can leave a `ember well ingest ~/library/` running overnight, kill it, resume next day, and not lose work. Without the journal, the Vow of Smallness is broken — you cannot ingest a real library on a Pi without it.

---

## 4. Flow C — the first-run rite (Hjarta)

```
[1] Operator runs `ember chat` for the first time.
    │
    ▼
[2] Munnr detects ~/.ember/identity/ is absent → launches Hjarta.
    │
    ▼
[3] Hjarta state machine:
    │   Greet
    │     │
    │     ▼
    │   ChooseFuni  (Ollama? llama.cpp? LM Studio? auto-detect)
    │     │
    │     ▼
    │   DiscoverFuni  (probe the chosen runtime, list available models,
    │     │           recommend by host RAM)
    │     │
    │     ▼
    │   ChooseWell  (local SQLite default? PG on the network? Gungnir?)
    │     │
    │     ▼
    │   ConfigureWell  (file path for SQLite; URL + secret for remote)
    │     │
    │     ▼
    │   TestRetrieval  (write a probe chunk, retrieve it, delete it)
    │     │
    │     ▼
    │   NameEmber  ("What would you like to call me?" — defaults: Ember)
    │     │
    │     ▼
    │   WriteIdentity  (atomic write to ~/.ember/identity/)
    │     │
    │     ▼
    │   Done  → hands control back to `ember chat`
```

Each transition is a single typed function. Each state's prompt is in a data file under `config/hjarta_prompts/`, never hardcoded in source (Vow of Modular Authorship; RULES.AI.md §"no hardcoded data").

If any state fails, Hjarta exits with a one-line cause and the operator's filesystem is unchanged. There is no half-configured state.

---

## 5. Where each datum lives at each moment

Tracking *who owns the bytes at each step* is the Cartographer's job. Here is the table for the conversation turn:

| Step | Datum | Lives in | Lifetime |
|---|---|---|---|
| 1 | Operator's raw input | stdin / arg | This turn only. |
| 2 | `AskTurn` | RAM (Munnr) | This turn only. |
| 3 | `BrunnrHandle` | RAM (Strengr → Munnr) | Process lifetime. |
| 4 | `qvec` (embedding) | RAM (Munnr) | This turn only. |
| 5 | `RetrievalHit` list | RAM (Munnr) | This turn only. |
| 6 | Assembled prompt | RAM (Munnr) | This turn only. |
| 7 | `FuniReply` | RAM (Munnr) | This turn only. |
| 8 | Rendered terminal output | stdout | This turn only. |
| 9 | `Episode` row | Well (Brunnr) | Until operator deletes; persists across reboots and devices. |

The discipline this enforces: **nothing of consequence lives in RAM**. Ember's RAM footprint is dominated by Funi (the model itself). Everything else is small and transient. This is what lets Ember run on a toaster.

---

## 6. Where each datum lives during ingest

| Step | Datum | Lives in | Lifetime |
|---|---|---|---|
| 1-2 | `IngestJob` | RAM (Munnr) | This job only. |
| 3 | `BrunnrHandle` | RAM (Strengr → Smiðja) | This job only. |
| 5a | Source bytes | RAM (one file at a time) | Released after chunking. |
| 5b | Parsed text | RAM | Released after chunking. |
| 5c | Chunk batch (≤ 64) | RAM | Released after embedding. |
| 5d | Embedding batch | RAM | Released after Brunnr write. |
| 5e | Document + Chunks | Well (Brunnr) | Persistent. |
| 6 | Progress journal | `~/.ember/state/smidja_progress/<job>.json` | Until job completes successfully, then deleted. |

The discipline this enforces: **Smiðja's RAM working set is one batch**. A 50 000-chunk ingest does not require 50 000 chunks in RAM at any moment.

---

## 7. What is *not* in these flows

Listed so the negative space is explicit.

- **No background reflection.** Ember does not silently re-read her own memory while idle. If the operator wants summarisation, they ask for it.
- **No autonomous tool use.** Funi may produce a structured tool call only when the operator's turn explicitly invited one (e.g. `ember ask --allow-tools "…"`). No tools in the default first-slice path.
- **No cross-operator flows.** Ember is single-operator. A shared Well between two operators is supported, but each operator runs their own Ember instance.
- **No streaming in the first slice.** Funi returns whole replies. Streaming is a later slice.

---

## 8. How a flow becomes new code

When a future flow is proposed:

1. The Skald names it.
2. The Architect places it in the right realm and confirms boundaries.
3. The Cartographer adds a section to *this* document with the grammar primitives.
4. The Forge Worker implements it as a single function in the appropriate subpackage.
5. The Auditor writes one happy-path test and one sad-path test.
6. The Scribe writes the DEVLOG entry and the ADR.

No flow ships without all six steps. Per `MYTHIC_ENGINEERING.md`'s core loop.

— Védis Eikleið
