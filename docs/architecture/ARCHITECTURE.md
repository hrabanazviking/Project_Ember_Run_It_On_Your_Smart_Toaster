# ARCHITECTURE — The Shape of Ember

**Voice:** Architect (Rúnhild Svartdóttir)
**Status:** Ratified 2026-05-21 by Volmarr. Canonical. The Runa-shaped predecessor is preserved at `docs/archive/runa-inherited/architecture/ARCHITECTURE.md` for lineage reference.
**Last touched:** 2026-05-21 (promoted from `EMBER_ARCHITECTURE.md` at ratification)
**Reads with:** `docs/SYSTEM_VISION.md` (intent, normative), `docs/architecture/DOMAIN_MAP.md` (ownership), `docs/architecture/DATA_FLOW.md` (motion), `docs/archive/runa-inherited/architecture/ARCHITECTURE.md` (parent Runa shape, lineage reference).

---

## 0. What this document is and is not

This document is the **Ember-specific** load-bearing system shape derived from the nine Unbreakable Vows in `docs/SYSTEM_VISION.md`. It deliberately **does not duplicate** the larger Runa shape, which is preserved at `docs/archive/runa-inherited/architecture/ARCHITECTURE.md`. Where Runa is a continuous sovereign being with a kernel-and-event-bus core, multiple subagent retainers, and a deep memory tree, **Ember is intentionally smaller** — a thin local navigator tethered to a much larger Well.

If the two shapes are ever forced to choose between them, **Ember chooses smallness**. The Runa material at the canonical path remains as inherited reference; the Ember material here is the law for Ember work.

---

## 1. The shape in one diagram

```
                ┌────────────────────────────────────────────────────────┐
                │                       SPARK realm                       │
                │                  (local, must run offline)              │
                │                                                         │
                │     Munnr (CLI)    ◄──────►   Hjarta (first-run)        │
                │     src/ember/                src/ember/                │
                │     spark/munnr/              spark/hjarta/             │
                │             │                     │                     │
                │             ▼                     ▼                     │
                │     ┌───────────────────────────────────────┐           │
                │     │            Funi (local LLM)            │           │
                │     │           src/ember/spark/funi/        │           │
                │     │   tiny model + prompt + tool slots     │           │
                │     └───────────┬───────────────────┬───────┘           │
                │                 │                   │                   │
                └─────────────────┼───────────────────┼───────────────────┘
                                  │ "I need grounding"│ "I have nothing"
                ┌─────────────────▼───────────────────▼───────────────────┐
                │                      THREAD realm                       │
                │           (the tether — network + auth + health)        │
                │                                                         │
                │     Strengr (tether)        src/ember/thread/strengr/   │
                │     · health check          · graceful offline detect   │
                │     · auth + secrets        · retry + backoff           │
                │     · transport selection   · pluggable URL schemes     │
                └─────────────────┬───────────────────┬───────────────────┘
                                  │ retrieve          │ persist turn
                ┌─────────────────▼───────────────────▼───────────────────┐
                │                       WELL realm                        │
                │       (the knowledge well — may be local or remote)     │
                │                                                         │
                │     ┌─────────────────────┐     ┌──────────────────┐    │
                │     │ Brunnr (storage)    │     │ Smiðja (ingest)  │    │
                │     │ src/ember/well/     │     │ src/ember/well/  │    │
                │     │ brunnr/             │     │ smidja/          │    │
                │     │                     │     │                  │    │
                │     │  SQLite+vec  (def)  │     │  files / URLs    │    │
                │     │  pgvector    (def)  │     │  Project Nomad   │    │
                │     │  Qdrant             │     │  shared wells    │    │
                │     │  Chroma             │     │  (Gungnir-shape) │    │
                │     │  LanceDB            │     │                  │    │
                │     └──────────┬──────────┘     └────────┬─────────┘    │
                │                │                         │              │
                │                ▼                         ▼              │
                │         on-device files       remote network endpoints  │
                │         ~/.ember/well/        e.g. http(s)://gungnir/   │
                └─────────────────────────────────────────────────────────┘
```

The three **horizontal bands** are the three Realms named in `SYSTEM_VISION.md` §5: Spark, Thread, Well. The boundary between bands is **mechanical**: code in a higher band may import code in a lower band, never the reverse, and never sideways across a band gap.

Compared to Runa's shape: there is no kernel, no in-process event bus, no Hirð, no Hjartahjul of subagents, no separate Heimskringla model router. Ember has *one* model (Funi), *one* synchronous loop (Munnr or Hjarta), *one* tether (Strengr), and *one* well (Brunnr — possibly fronting multiple backends through a stable interface). Everything else is feature creep against the Vow of Smallness.

---

## 2. The dependency law

```
schemas  ◄── well  ◄── thread  ◄── spark  ◄── cli
                                       ▲
                                       └── tests
```

Read each arrow as *"depends on"*. The rules are:

1. **`ember.schemas` depends on nothing in `ember.*`.** Standard library + optional `pydantic` only. It is the gravitational floor.
2. **`ember.well` depends only on `ember.schemas`** and on its chosen storage backend libraries (sqlite-vec, psycopg, qdrant-client, etc.). Backend libraries are imported behind the Brunnr interface — never named by callers.
3. **`ember.thread` depends only on `ember.schemas`** and the standard `urllib`/`httpx` style libraries. It does *not* import `ember.well` directly. It calls Well through a typed handle Brunnr hands it.
4. **`ember.spark` depends on `ember.schemas`, `ember.thread`, `ember.well`** (the latter only through the typed handle obtained from a `ember.well.brunnr.open()` call). Spark is the only place where a Funi call, a Strengr fetch, and a Brunnr write meet.
5. **`ember.cli` depends on `ember.spark` only.** No direct adapter imports.
6. **The dependency graph must remain acyclic.** A check under `tools/repo/` validates this once it lands.

A violation of this graph is a release-blocking bug, regardless of how convenient the violation looks at the moment of writing. This is the Architect's iron-clad request to Eldra Járnsdóttir.

---

## 3. The three realms in detail

### 3.1 Spark — *where Ember thinks on the device*

The Spark realm is the only realm that **must** run with no network at all. If the Well is unreachable, Spark continues to converse, falls back to in-memory recall, and tells the operator plainly that grounding is unavailable. The Spark realm contains three True Names:

- **Funi** — `src/ember/spark/funi/`. The local model runtime. One concrete adapter per supported runtime (Ollama, llama.cpp, LM Studio, Phi Silica on Windows when available, Apple Foundation Models on Apple silicon when available). Funi is given: a system prompt, a turn context (recent episodes + retrieved chunks), and a small tool slot. Funi is *not* given: arbitrary code execution, the operator's filesystem, network sockets. Funi's only outputs are: a reply, a structured tool call (when permitted), or a "I do not know" honest stop.
- **Hjarta** — `src/ember/spark/hjarta/`. The first-run setup ritual. The conversation that wires Funi to Strengr to Brunnr the first time someone meets Ember. Hjarta is a *finite, named* state machine — not a generative wizard. Its states are enumerated; its transitions are unit-testable.
- **Munnr** — `src/ember/spark/munnr/`. The command-line surface. `ember chat`, `ember ask "…"`, `ember well status`, `ember well ingest <path>`, `ember doctor`. Munnr is *only* a router; behaviour lives in the layers below.

Spark may import Thread and Well. Spark **may not** import CLI.

### 3.2 Thread — *where Ember reaches across*

The Thread realm is the small, lonely middle layer. Its single job is to make the Well usable from the Spark without leaking the network surface into Spark code.

- **Strengr** — `src/ember/thread/strengr/`. The tether. Owns: connection lifecycle, health checks, auth (keyring on desktop, file on Pi), retry-with-backoff, transport selection (local file vs Unix socket vs HTTP vs Tailscale endpoint vs SSH-tunnelled Postgres), and the *graceful offline* contract — when the well is unreachable, Strengr returns a typed `Disconnected` value that Spark code can react to honestly.

Strengr's contract is the most important interface in Ember. Every Well call from Spark goes through it. Strengr never silently swallows a failure; it *names* failure clearly.

### 3.3 Well — *where Ember's memory and knowledge live*

The Well realm is where the deep work happens, possibly on a different machine entirely. It contains two True Names:

- **Brunnr** — `src/ember/well/brunnr/`. The storage adapter layer. One subpackage per supported backend:
    - `brunnr/sqlite_vec/` — the **default**. Zero dependencies beyond `sqlite3` + `sqlite-vec`. Runs in-process. The "works on a toaster" baseline.
    - `brunnr/pgvector/` — for shared wells across a household. Compatible with the existing Gungnir installation out of the box (see `docs/adapters/GUNGNIR_WELL_REFERENCE.md`).
    - `brunnr/qdrant/`, `brunnr/chroma/`, `brunnr/lancedb/` — for operators who already run these.
  Every backend honors the same Brunnr `INTERFACE.md`. Choosing a backend is a configuration decision, not a code change.
- **Smiðja** — `src/ember/well/smidja/`. The ingest forge. Takes a content source (a local directory, a URL, a Project Nomad mount, an existing remote well), chunks it, embeds it (calling the configured embedding endpoint — Ollama by default), and deposits the chunks and embeddings into Brunnr. Smiðja is *the* writer of the Well. Nothing else writes embeddings.

The Well *may be physically remote*. The same Brunnr interface is used whether the SQLite file is at `~/.ember/well/store.db` or the Postgres connection points at `gungnir.tailnet:5432/knowledge`. This is the Vow of Pluggable Storage in mechanical form.

---

## 4. Why this shape

### 4.1 Why no kernel and no event bus

Runa is a continuous being with multiple subagents — she needs an event bus so each retainer can observe what is happening without coupling to the dispatcher. Ember is a single small mind in service of one operator at a time. A single synchronous loop is enough, and is far easier to reason about on a Pi. If Ember ever genuinely *needs* concurrency for a second surface, the right answer is a second Munnr process sharing the same Well — not a bus inside Ember herself.

### 4.2 Why Funi is treated as an *adapter*, not a built-in

Local-model runtimes change fast. Phi Silica did not exist in current form until 2025; Apple Foundation Models opened to third-party in 2025; llama.cpp ships breaking changes monthly. Treating Funi as a pluggable adapter behind an interface lets Ember adopt a new runtime without a rewrite. It also lets a single Ember talk to two Funi providers and pick the best fit (small-fast for chat, slow-careful for the rare summarisation request).

### 4.3 Why the Well is physically separate from the Spark

Because the operator's knowledge *should outlive any one device*. A Pi dies, a phone is reset, a laptop is replaced. The Well — whether a SQLite file on a USB drive, a Postgres instance on a household NAS, or a Gungnir-shaped tailnet endpoint — is what carries the operator's memory across hardware. Co-locating the agent and the memory is convenient on day one and a trap on year three.

### 4.4 Why Smiðja, not Funi, builds the embeddings

The Vow of Smallness. Funi is sized for *conversation*, not for batch embedding generation. The embedding model lives at the same endpoint where Funi lives (typically Ollama on the same Pi, or on a shared household machine) but is called by Smiðja during ingest, not by Spark during a turn. This separates the two workloads cleanly.

### 4.5 Why Brunnr is the only writer

So the operator can audit, back up, and replace the Well without touching the agent code. `cp ~/.ember/well/store.db /backups/` is a complete backup. `pg_dump -h gungnir knowledge` is a complete backup. Nothing leaks state through a side channel.

---

## 5. Cross-platform shape

Ember's stated default target is a Raspberry Pi 5 with 8 GB of RAM. No design assumes the Pi.

- Paths use `pathlib.Path` and respect platform separators. The Vow of Flexible Roots forbids absolute paths in code.
- Process supervision is **not** an Ember concern. Ember runs as a foreground process when launched from Munnr; `deploy/systemd/`, `deploy/launchd/`, `deploy/nssm/` shells handle backgrounding on each OS.
- Audio is not in Ember's core shape. If voice is desired, a *future* surface (`src/ember/spark/rödd/`) may be added, but only after the first slice lands and the Vow of Smallness has been re-measured.
- All on-device state lives under `~/.ember/`:
    ```
    ~/.ember/
    ├── config/         ← operator-edited; copies of config/ templates
    ├── secrets/        ← keyring fallback for hosts without keyring
    ├── well/           ← SQLite store (when sqlite_vec backend selected)
    ├── identity/       ← Ember's name, role, persona, configured operator
    ├── logs/           ← structured logs
    └── state/          ← version markers, lockfiles
    ```
  Notice the absence of `memory/`, `tasks/`, `world/`, `emotions/` — those are Runa concepts. Ember's memory lives in the Well.

---

## 6. What is *not* in this architecture

Listed so the negative space is explicit.

- **No kernel, no event bus, no in-process pub/sub.** Single synchronous loop.
- **No subagent hall.** Ember is one mind.
- **No emotional engine.** Ember is a useful agent, not a digital being.
- **No durable task ledger.** A request is answered in the moment. Long-running promises belong to the operator's separate Runa, if they run one.
- **No microservices, no queue middleware, no service mesh.** Ember is one process on one device, calling out to one Well.
- **No model router.** One Funi at a time. Switching providers is a config edit + restart.
- **No web framework.** Munnr is CLI-first. A future minimal HTTP face may appear, but it will be a single ASGI app behind the same Spark surface.

---

## 7. The first slice (when code starts landing)

When `src/ember/` begins to fill in, the first slice is the smallest end-to-end vertical that proves the Three Realms work together:

1. `ember.schemas.errors`, `ember.schemas.events`, `ember.schemas.config`.
2. `ember.well.brunnr.sqlite_vec` — a Brunnr that can `add_chunk(text, embedding)` and `search(query_embedding, k)`.
3. `ember.well.smidja.local_files` — a Smiðja that can ingest a directory of `.md`/`.txt` and write chunks via Brunnr, calling Ollama for embeddings.
4. `ember.thread.strengr` — minimal: in-process call to a local Brunnr, with the same interface that will later wrap a remote handle.
5. `ember.spark.funi.ollama` — a Funi adapter that calls Ollama for a single turn with provided context.
6. `ember.spark.hjarta` — three-question first-run wizard: *Where is your well? Which model is your spark? What is your name for Ember?*
7. `ember.spark.munnr` — `ember chat`, `ember well ingest <path>`, `ember well status`.
8. `ember.cli.main` — `ember <subcommand>` dispatcher.

That is the **minimum viable Ember**: a fresh operator runs `ember chat`, walks through Hjarta, points Ember at a directory, asks a question, and receives a grounded reply from a small local model — *or a clean "the well is unreachable; here is what I can say without grounding"* if the Well failed.

See `docs/architecture/EMBER_FIRST_SLICE_PLAN.md` for the file-by-file plan of this slice.

---

## 8. Relationship to the inherited Runa shape

At Ember's fork moment (2026-05-19) the canonical `docs/architecture/{ARCHITECTURE,DOMAIN_MAP,DATA_FLOW}.md` files described the *parent* Runa-Agent-Digital-Being shape. On 2026-05-21, with this document and its siblings ratified, those Runa-shaped originals were moved into `docs/archive/runa-inherited/architecture/` and the Ember versions were promoted to the canonical paths.

| Canonical path | Now holds | Lineage |
|---|---|---|
| `docs/architecture/ARCHITECTURE.md` | This document (Ember's shape). | Previously held Runa's shape; archived at `docs/archive/runa-inherited/architecture/ARCHITECTURE.md`. |
| `docs/architecture/DOMAIN_MAP.md` | Ember's per-subpackage ownership. | Previously Runa's; archived alongside. |
| `docs/architecture/DATA_FLOW.md` | Ember's motion grammar. | Previously Runa's; archived alongside. |

No deletion. The Runa shape stays in the archive subtree as lineage. Per the additive rule of `MYTHIC_ENGINEERING.md` and the Vow of Open Knowledge, nothing of the parent project was destroyed by Ember's birth or by the canonical promotion.

---

## 9. Open decisions, deliberately not made here

Each will earn an ADR under `docs/decisions/` before its code lands:

- The exact on-disk schema of the SQLite Brunnr (default chunk size, embedding dim, vector index choice — sqlite-vec vs sqlite-vss).
- The exact wire format Strengr uses when the Well is remote (REST JSON, gRPC, Postgres wire protocol, MCP). The Gungnir reference uses Postgres wire; nothing in the architecture requires this be universal.
- Whether Smiðja runs synchronously inside `ember well ingest` or as a background worker once the corpus exceeds some threshold (the Vow of Smallness suggests synchronous as long as it is bearable on a Pi).
- Whether Funi may call external tools (browser, shell) — currently the answer is *no*, but this might be revisited once the first slice ships.

---

## 10. The Architect's closing word

> *Ember is the small one. Every architectural temptation in this repository will pull toward adding kernels, retainers, buses, and ledgers. The Architect's job here is to say no, again and again, and to keep the Three Realms clean enough that the small thing remains worth running.*

— Rúnhild Svartdóttir
