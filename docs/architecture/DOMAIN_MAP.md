# DOMAIN_MAP — Subsystem Ownership for the Three Realms

**Voice:** Architect (Rúnhild Svartdóttir)
**Status:** Ratified 2026-05-21 by Volmarr. Canonical. The Runa-shaped predecessor is preserved at `docs/archive/runa-inherited/architecture/DOMAIN_MAP.md` for lineage reference.
**Last touched:** 2026-05-21 (promoted from `EMBER_DOMAIN_MAP.md` at ratification)
**Reads with:** `ARCHITECTURE.md` (shape), `docs/SYSTEM_VISION.md` (intent), `DATA_FLOW.md` (motion).

---

## 0. How to read this document

For every planned subpackage of `src/ember/`, this document gives:

- **Purpose** — one sentence. If a subpackage cannot be described in one sentence, its boundary has already failed.
- **True Name** — the named subsystem from `docs/SYSTEM_VISION.md` that lives here (when applicable).
- **Owns** — the data, behaviours, and invariants that are this subpackage's responsibility.
- **Does not own** — explicit negative space.
- **May import from** — the only subpackages whose code may appear in `import` statements here.
- **May be imported by** — the only subpackages permitted to import from here.
- **Failure semantics** — what happens to the rest of Ember when this subpackage fails.

Two iron rules sit on top of every row:

1. **Dependency direction is strict.** No late imports, no `importlib`, no string-built module paths to evade the boundary. The boundary is mechanical.
2. **Every subpackage has exactly one INTERFACE.md.** Anything not on the surface declared in that INTERFACE.md is private to the subpackage.

The top-level shape is:

```
src/ember/
├── schemas/        ← types only
├── well/           ← Brunnr (storage) + Smiðja (ingest)
│   ├── brunnr/
│   │   ├── sqlite_vec/
│   │   ├── pgvector/
│   │   ├── qdrant/
│   │   ├── chroma/
│   │   └── lancedb/
│   └── smidja/
│       ├── local_files/
│       ├── url_fetch/
│       ├── nomad/
│       └── shared_well/
├── thread/         ← Strengr
│   └── strengr/
├── spark/          ← Funi (LLM) + Hjarta (wizard) + Munnr (CLI)
│   ├── funi/
│   │   ├── ollama/
│   │   ├── llamacpp/
│   │   ├── lmstudio/
│   │   ├── phi_silica/      (Windows Copilot+ only)
│   │   └── apple_foundation/(Apple silicon only)
│   ├── hjarta/
│   └── munnr/
└── cli/            ← entry point
```

---

## 1. `src/ember/schemas/`

- **Purpose:** Pydantic models, dataclasses, and shared type definitions used in two or more other subpackages.
- **True Name:** *(none — structural)*
- **Owns:** Type definitions (`Chunk`, `Document`, `Episode`, `RetrievalHit`, `FuniReply`, `WellHandle`, `Disconnected`, error classes, config types, on-disk version markers).
- **Does not own:** Behaviour. A schema may define a type; it may not define a method that does work.
- **May import from:** Standard library only. Optional `pydantic`, `typing_extensions`, `enum`.
- **May be imported by:** Everything in `src/ember/`.
- **Failure semantics:** A failure here means the package will not load — there is no graceful degradation. Tests guarantee `ember.schemas` imports cleanly under all supported Python versions.

## 2. `src/ember/well/brunnr/`

- **Purpose:** Pluggable storage adapter layer. Reads embeddings out, writes chunks and embeddings in. One concrete adapter per supported backend.
- **True Name:** **Brunnr** (the well)
- **Owns:** The Brunnr `INTERFACE.md`, the concrete backend adapters (`sqlite_vec/`, `pgvector/`, `qdrant/`, `chroma/`, `lancedb/`), the backend selection registry, the on-disk schema versioning per backend.
- **Does not own:** Embedding generation (that's Smiðja). Network transport selection (that's Strengr). What questions Ember asks of the Well (that's Spark/Funi).
- **May import from:** `ember.schemas` and the specific backend library for each adapter (e.g. `sqlite3` + `sqlite_vec` only inside `brunnr/sqlite_vec/`; `psycopg` only inside `brunnr/pgvector/`).
- **May be imported by:** `ember.well.smidja`, `ember.thread.strengr` (to obtain a typed handle), tests.
- **Failure semantics:** **Critical.** Per the Vow of Modular Authorship: a backend failure must not take Ember down. The Brunnr interface returns a typed `Disconnected` value rather than raising, and Strengr surfaces this honestly to Spark.

### 2.1 Brunnr's INTERFACE.md — the minimum surface

(Drafted here; will be split into `src/ember/well/brunnr/INTERFACE.md` when code lands.)

| Operation | Inputs | Returns | Notes |
|---|---|---|---|
| `open(config)` | `BrunnrConfig` | `BrunnrHandle` or `Disconnected` | One handle per process; thread-safe within the adapter. |
| `add_document(doc)` | `Document` | `document_id: int` | Idempotent on content hash; existing hash returns the existing id. |
| `add_chunks(chunks)` | `list[Chunk]` (with `document_id`, `chunk_index`, `text`, `embedding`) | `list[chunk_id: int]` | Bulk insert; commit at end. |
| `vector_search(qvec, k, filter=None)` | `list[float]`, `int`, optional filter | `list[RetrievalHit]` | Cosine by default; HNSW or backend-equivalent. |
| `text_search(query, k, filter=None)` | `str`, `int`, optional filter | `list[RetrievalHit]` | FTS (sqlite FTS5, Postgres tsvector, etc.). |
| `hybrid_search(qvec, query, k)` | both | `list[RetrievalHit]` | Reciprocal rank fusion. |
| `get_document(document_id)` | `int` | `Document` | |
| `get_chunk(chunk_id)` | `int` | `Chunk` | |
| `count()` | — | `BrunnrStats` (documents, chunks, embedded_chunks, size_bytes) | For `ember well status`. |

Any backend that cannot satisfy `hybrid_search` natively must implement it via `vector_search` + `text_search` + RRF in the adapter — never above the interface.

## 3. `src/ember/well/smidja/`

- **Purpose:** Ingest forge. Take a content source, chunk it, embed it, deposit chunks in Brunnr.
- **True Name:** **Smiðja** (the forge)
- **Owns:** Source adapters (`local_files/`, `url_fetch/`, `nomad/`, `shared_well/`), the chunker, the embedding client (calls Ollama / configured endpoint), the ingest progress journal.
- **Does not own:** The Brunnr backend (writes through the Brunnr interface). The embedding model itself (that's an external service called via HTTP or local subprocess).
- **May import from:** `ember.schemas`, `ember.well.brunnr` (through the public interface), HTTP client of choice.
- **May be imported by:** `ember.spark.munnr` (for `ember well ingest`), `ember.spark.hjarta` (for the first-run "ingest these files" step), tests.
- **Failure semantics:** A failed ingest is recoverable. Smiðja journals progress; partial ingests can be resumed. A failed embedding for one chunk does not fail the whole job — the chunk is marked failed and reported in the summary.

## 4. `src/ember/thread/strengr/`

- **Purpose:** The tether. Make the Well usable from Spark without leaking network surface into Spark code.
- **True Name:** **Strengr** (the string)
- **Owns:** Connection lifecycle, health checks, auth (keyring, file, env), retry-with-backoff, transport selection (local-in-process, Unix socket, HTTP, Tailscale endpoint), the `Disconnected` graceful-offline contract.
- **Does not own:** Backend-specific protocols (those live inside the Brunnr adapter). Conversation memory (that's the operator's Well content).
- **May import from:** `ember.schemas`, `ember.well.brunnr` (to obtain handles by config — Strengr's job is to wrap that call with the failure handling).
- **May be imported by:** `ember.spark.*` only. Strengr is *the* boundary Spark crosses to reach the Well.
- **Failure semantics:** **Critical** — and a critical design success when it works. Strengr's whole reason to exist is to make Well failures legible to Spark instead of catastrophic. Strengr never raises a connection error upward; it returns a typed `Disconnected(reason)` value. Spark code is required to handle that value.

## 5. `src/ember/spark/funi/`

- **Purpose:** Local model runtime. One adapter per supported runtime.
- **True Name:** **Funi** (the flame)
- **Owns:** One subpackage per runtime (`ollama/`, `llamacpp/`, `lmstudio/`, `phi_silica/`, `apple_foundation/`), the Funi `INTERFACE.md`, the prompt assembler, the tool-call slot wiring.
- **Does not own:** Retrieval (Spark assembles context from Strengr/Brunnr before calling Funi). Identity (that's `~/.ember/identity/`). Conversation persistence (that's the Well via Smiðja-style ingest of episodes).
- **May import from:** `ember.schemas`, the runtime-specific client library (only inside the matching subpackage).
- **May be imported by:** `ember.spark.munnr`, `ember.spark.hjarta`, tests.
- **Failure semantics:** A Funi failure aborts the current turn with a clear error. Ember reports the error to the operator and continues to be usable for non-LLM commands (`ember well status`, `ember doctor`).

### 5.1 Funi's INTERFACE.md — the minimum surface

| Operation | Inputs | Returns | Notes |
|---|---|---|---|
| `open(config)` | `FuniConfig` | `FuniHandle` or `Unavailable` | Loads the model or connects to its endpoint. |
| `complete(prompt, context, tools=None)` | `str`, `list[ContextItem]`, optional list | `FuniReply` (text + optional structured tool calls + finish reason) | One turn. No streaming yet in the first slice. |
| `embed(texts)` *(optional)* | `list[str]` | `list[list[float]]` | Only some runtimes; if absent, Smiðja uses its own embedding endpoint. |
| `health()` | — | `FuniHealth` (model_id, ram_use, last_ok) | For `ember doctor`. |

## 6. `src/ember/spark/hjarta/`

- **Purpose:** First-run setup ritual. The conversation that wires Funi to Strengr to Brunnr the first time someone meets Ember.
- **True Name:** **Hjarta** (the heart)
- **Owns:** A *finite, named* state machine: `Greet → ChooseFuni → DiscoverFuni → ChooseWell → ConfigureWell → TestRetrieval → NameEmber → WriteIdentity → Done`. Each state has a single typed transition. No generative wizardry.
- **Does not own:** Ongoing conversation (that's `ember chat`). Reconfiguration after first run (that's `ember config edit` or re-running Hjarta with `ember setup --reset`).
- **May import from:** `ember.schemas`, `ember.spark.funi`, `ember.thread.strengr`, `ember.well.brunnr`.
- **May be imported by:** `ember.spark.munnr` (the CLI invokes Hjarta when `~/.ember/identity/` is absent).
- **Failure semantics:** A Hjarta failure leaves the operator with a clear "what went wrong, here is how to fix it" message and exits non-zero. No half-configured state on disk; Hjarta writes identity atomically at the end.

## 7. `src/ember/spark/munnr/`

- **Purpose:** The command-line surface — argument parsing, subcommand dispatch, output formatting.
- **True Name:** **Munnr** (the mouth)
- **Owns:** Argument parsers, subcommand table, terminal output rendering, REPL loop for `ember chat`.
- **Does not own:** Any actual work. The CLI is a router; behaviour lives below.
- **May import from:** `ember.schemas`, `ember.spark.funi`, `ember.spark.hjarta`, `ember.thread.strengr`, `ember.well.brunnr` (read-only handle), `ember.well.smidja` (for `ember well ingest`).
- **May be imported by:** `ember.cli` only.
- **Failure semantics:** A CLI parse failure prints help and exits non-zero. Subcommand failures bubble exit codes upward with a one-line human-readable cause.

## 8. `src/ember/cli/`

- **Purpose:** The `ember` console-script entry point.
- **True Name:** *(part of Munnr; lives separately only because `pyproject.toml` points its `[project.scripts]` here.)*
- **Owns:** The `main()` function and any top-level argparse plumbing too thin to live inside Munnr.
- **Does not own:** Anything. CLI is a leaf.
- **May import from:** `ember.spark.munnr`.
- **May be imported by:** Nothing — it is the entry point.
- **Failure semantics:** Same as Munnr.

---

## 9. Cross-cutting concerns

These concerns are spread across many subpackages — their ownership is declared once here to prevent drift.

| Concern | Owned by | How |
|---|---|---|
| Logging | `ember.spark.munnr.logging` (planned; thin) | Single `get_logger(__name__)` accessor; never `print`, never raw `logging.getLogger`. |
| Configuration | `ember.schemas.config` (types) + `ember.spark.munnr.config_loader` (loader) | All subpackages receive config objects from above; nothing reads files directly except the loader. |
| Errors | `ember.schemas.errors` | All exception classes raised across subpackage boundaries are defined here. |
| Time | `ember.schemas.clock` (planned, injected) | No `datetime.now()` direct in business logic — tests are deterministic. |
| Identity | `~/.ember/identity/` (on disk) | Read by Hjarta on first run; read by Munnr each launch for the operator-facing greeting. |
| Secrets | `~/.ember/secrets/` (on disk, mode 600) or OS keyring | Strengr is the only consumer. Never logged. |

---

## 10. What this map does *not* yet decide

Each will earn an ADR under `docs/decisions/` before the corresponding code lands:

- The exact `BrunnrHandle` Python protocol (Protocol vs ABC vs plain duck typing).
- Whether the FTS layer is mandatory or per-backend optional (sqlite-vec without FTS5 vs with).
- The chunk-size and overlap defaults for `Smiðja` — the Gungnir corpus uses ~1684-char chunks; the Ember default should likely match unless measured otherwise.
- Whether `funi/phi_silica` and `funi/apple_foundation` are first-party or live in a separate optional package (the Vow of Smallness says: not in core).

---

## 11. Boundary checklist (for any future PR)

Before merging code that touches more than one of the rows above, the author confirms:

- [ ] The new code respects the dependency law in `ARCHITECTURE.md` §2.
- [ ] No new file imports across a band gap (Well → Spark, Spark → CLI in reverse, etc.).
- [ ] The relevant `INTERFACE.md` is updated in the same commit as the code change.
- [ ] If a boundary moved, this document was updated *and* an ADR added under `docs/decisions/`.
- [ ] The change preserves the Vow of Modular Authorship: any single backend / runtime / adapter can fail without taking Ember down.

— Rúnhild Svartdóttir
