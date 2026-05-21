# EMBER_FIRST_SLICE_PLAN — The Smallest End-to-End Vertical

**Voice:** Forge Worker (Eldra Járnsdóttir), with Architect (Rúnhild Svartdóttir)
**Status:** Proposed — for ratification. Bootstrap-stage. The plan is a *file-by-file* listing; the code is not in this commit.
**Last touched:** 2026-05-21
**Reads with:** `ARCHITECTURE.md` (the shape), `DOMAIN_MAP.md` (the ownership), `DATA_FLOW.md` (the motion), `EMBER_FORK_DELTA.md` (the migration).

---

## 0. What "first slice" means here

Per `MYTHIC_ENGINEERING.md` §"The first slice", a slice is the **smallest end-to-end vertical** that proves the Three Realms work together. It does *not* have to be impressive; it has to be *whole*.

Acceptance criterion for this slice:

> A fresh operator on a Raspberry Pi 5 with Ollama already running locally can:
> 1. `pip install ember-agent`
> 2. `ember chat` — sees the Hjarta first-run wizard
> 3. Walks the wizard: confirms Ollama with `phi3:mini`, chooses local SQLite Brunnr, names Ember
> 4. `ember well ingest ~/notes/` — sees a progress summary
> 5. `ember chat` — asks a question, gets a reply that cites a chunk from `~/notes/`
> 6. Stops the network, asks again — gets a clean ungrounded reply with a "well: disconnected" banner

If that loop works, the slice is done. Everything else is later slices.

---

## 1. Dependencies the slice assumes

| Dependency | Why | First-slice version pin |
|---|---|---|
| Python 3.11+ | Already in `pyproject.toml` | `>=3.11` |
| `sqlite-vec` | The default Brunnr backend | `>=0.1.6` |
| `httpx` | Ollama / embedding HTTP client | `>=0.27` |
| `pydantic` | Config + schemas | `>=2.7` |
| `typer` *or* `argparse` | Munnr CLI | Recommend `argparse` (stdlib) for the Vow of Smallness; revisit only if it hurts. |

**Explicit non-dependencies** (Vow of Smallness):
- No web framework. The first slice has no HTTP face.
- No async runtime. Synchronous calls only (Pi single-thread reality).
- No structured-output libraries (instructor, etc.) — Funi reply parsing is a hand-rolled regex/dict reader in the first slice.

---

## 2. The slice as a file list

Files marked **NEW** are created in the first slice's PR. Files marked *(scaffolded)* exist as empty `__init__.py` from the `src/runa/` → `src/ember/` rename.

```
src/ember/
├── __init__.py                              (scaffolded)
├── __main__.py                              NEW
├── cli/
│   ├── __init__.py                          (scaffolded)
│   └── main.py                              NEW — entry point, dispatches to Munnr
├── schemas/
│   ├── __init__.py                          (scaffolded)
│   ├── INTERFACE.md                         NEW
│   ├── errors.py                            NEW — typed exceptions
│   ├── config.py                            NEW — EmberConfig, BrunnrConfig, FuniConfig
│   ├── chunks.py                            NEW — Document, Chunk, RetrievalHit
│   ├── episode.py                           NEW — Episode (operator turn record)
│   └── funi.py                              NEW — FuniReply, FuniHealth
├── well/
│   ├── __init__.py                          (scaffolded)
│   ├── brunnr/
│   │   ├── __init__.py                      (scaffolded)
│   │   ├── INTERFACE.md                     NEW
│   │   ├── handle.py                        NEW — BrunnrHandle protocol + registry
│   │   └── sqlite_vec/
│   │       ├── __init__.py                  NEW
│   │       ├── adapter.py                   NEW — the only backend in the first slice
│   │       └── schema.sql                   NEW — tables + indexes
│   └── smidja/
│       ├── __init__.py                      (scaffolded)
│       ├── INTERFACE.md                     NEW
│       ├── chunker.py                       NEW — ~1684-char chunks, paragraph-aware
│       ├── embed_client.py                  NEW — calls Ollama /api/embed
│       ├── journal.py                       NEW — resumable progress file
│       └── local_files/
│           ├── __init__.py                  NEW
│           └── source.py                    NEW — walks a path, yields parsed text
├── thread/
│   ├── __init__.py                          (scaffolded)
│   └── strengr/
│       ├── __init__.py                      NEW
│       ├── INTERFACE.md                     NEW
│       └── tether.py                        NEW — open(config) → BrunnrHandle | Disconnected
└── spark/
    ├── __init__.py                          (scaffolded)
    ├── funi/
    │   ├── __init__.py                      (scaffolded)
    │   ├── INTERFACE.md                     NEW
    │   ├── handle.py                        NEW — FuniHandle protocol + registry
    │   └── ollama/
    │       ├── __init__.py                  NEW
    │       └── adapter.py                   NEW — the only Funi adapter in the first slice
    ├── hjarta/
    │   ├── __init__.py                      (scaffolded)
    │   ├── INTERFACE.md                     NEW
    │   ├── machine.py                       NEW — finite state machine
    │   └── prompts/
    │       └── *.yaml                       NEW — state prompts as data (RULES.AI.md)
    └── munnr/
        ├── __init__.py                      (scaffolded)
        ├── INTERFACE.md                     NEW
        ├── chat.py                          NEW — REPL loop, the conversation turn
        ├── ask.py                           NEW — one-shot ask
        ├── ingest.py                        NEW — `ember well ingest <path>`
        ├── doctor.py                        NEW — `ember doctor`
        ├── status.py                        NEW — `ember well status`
        └── render.py                        NEW — terminal output formatting

config/
├── ember.example.yaml                       NEW (renamed from runa.example.yaml)
├── storage.example.yaml                     NEW
├── sources.example.yaml                     NEW
└── profiles/
    └── pi5.yaml                             NEW — first profile

tests/
├── unit/
│   ├── test_chunker.py                      NEW
│   ├── test_journal.py                      NEW
│   ├── test_sqlite_vec_adapter.py           NEW
│   ├── test_strengr_disconnect.py           NEW
│   └── test_hjarta_state_machine.py         NEW
├── integration/
│   ├── test_ingest_to_query.py              NEW — write 10 chunks, query, get hits
│   └── test_offline_path.py                 NEW — kill Brunnr mid-turn, observe banner
└── fixtures/
    └── tiny_corpus/                         NEW — three small .md files
```

Total **new** files: ~38. Total **lines of Python** at first-slice acceptance: targeting under **2 500 LOC** (excluding tests, configs, and docs). If the slice grows past 4 000 LOC, the Architect re-cuts before merge.

---

## 3. Slice phases (ordered, each is a separable commit)

The seven phases below each ship as their own commit. Each phase ends with a green test suite and a DEVLOG entry.

### Phase 1 — Rename and pyproject

- `src/runa/` → archived to `docs/archive/runa-inherited/src-skeleton/`
- `src/ember/` created with empty subpackages per the file tree above
- `pyproject.toml`: name `ember-agent`, entry point `ember`
- `__main__.py` raises `NotImplementedError` cleanly with a "first slice not yet landed" message
- Tests: import-only

### Phase 2 — Schemas (the gravitational floor)

- `ember.schemas.errors` (typed `EmberError` family — `BrunnrError`, `FuniError`, `IngestError`, etc.)
- `ember.schemas.config` (`EmberConfig`, `BrunnrConfig`, `FuniConfig`, `StrengrConfig`)
- `ember.schemas.chunks` (`Document`, `Chunk`, `RetrievalHit`)
- `ember.schemas.episode` (`Episode`)
- `ember.schemas.funi` (`FuniReply`, `FuniHealth`, `Unavailable`)
- Tests: shape contracts only

### Phase 3 — Brunnr (sqlite_vec) and Smiðja

- `ember.well.brunnr.handle` (the `BrunnrHandle` protocol + registry)
- `ember.well.brunnr.sqlite_vec.adapter` + `schema.sql`
- `ember.well.smidja.chunker` (paragraph-aware, ~1684 chars per chunk, Gungnir-aligned)
- `ember.well.smidja.embed_client` (calls Ollama `POST /api/embed`)
- `ember.well.smidja.journal` (resumable JSON state under `~/.ember/state/smidja_progress/`)
- `ember.well.smidja.local_files.source` (walks directories, parses `.md` and `.txt`)
- Tests: write-then-query round trip, journal resume, chunk size invariants
- Acceptance: `python -c "from ember.well.brunnr.sqlite_vec import SqliteVecBrunnr; …"` end-to-end ingest + query in a notebook

### Phase 4 — Strengr

- `ember.thread.strengr.tether` (`open(config) → BrunnrHandle | Disconnected`)
- Initially supports only the local `sqlite_vec` backend
- The `Disconnected` value carries a typed reason (enum) and a `since` timestamp
- Tests: `Disconnected` returned when the configured DB file is missing; returned when permissions deny; returned when the path is on a remote mount that times out
- Acceptance: `strengr.open(config)` returns a working handle for a fresh SQLite, returns `Disconnected` for an invalid config

### Phase 5 — Funi (Ollama)

- `ember.spark.funi.handle` (the `FuniHandle` protocol + registry)
- `ember.spark.funi.ollama.adapter` (calls Ollama `POST /api/generate` with `phi3:mini` by default)
- Prompt assembler: system prompt + last 5 episodes + retrieval hits + operator line
- Tests: mocked Ollama responses, prompt assembly invariants, OOM behaviour
- Acceptance: `funi.complete(prompt, context)` returns a `FuniReply` for a real local Ollama; returns `Unavailable` when Ollama is down

### Phase 6 — Hjarta and Munnr

- `ember.spark.hjarta.machine` (the FSM)
- `ember.spark.hjarta.prompts/*.yaml` (state prompts as data — RULES.AI.md "no hardcoded data")
- `ember.spark.munnr.chat` (the REPL turn)
- `ember.spark.munnr.ask`, `ember.spark.munnr.ingest`, `ember.spark.munnr.doctor`, `ember.spark.munnr.status`
- `ember.spark.munnr.render` (terminal formatting + the `well: disconnected` banner)
- Tests: Hjarta full happy-path with mocks, Hjarta failure-rollback, `ember chat` one-turn with mocked Funi
- Acceptance: full Hjarta wizard runs from a clean `~/.ember/`; `ember chat` works against a mock Funi and a real SQLite Brunnr

### Phase 7 — Acceptance and shipping

- Integration tests `tests/integration/test_ingest_to_query.py` and `tests/integration/test_offline_path.py`
- `deploy/pi/INSTALL.md` — single-page operator install for Raspberry Pi 5
- DEVLOG entry: first slice ratified
- ADR: any decisions made during the slice that bind future code
- `pyproject.toml`: bump to 0.1.0

---

## 4. What the slice deliberately does NOT include

Each of these is a *later* slice. None block first-slice ratification.

- **Other Brunnr backends** (pgvector, qdrant, chroma, lancedb). Gungnir integration is *deferred* to the second slice — see `docs/adapters/GUNGNIR_WELL_REFERENCE.md` for the planned shape.
- **Other Funi runtimes** (llamacpp, lmstudio, phi_silica, apple_foundation).
- **Other Smiðja sources** (url_fetch, nomad, shared_well).
- **Streaming Funi replies.**
- **Tool use.** `funi.complete(..., tools=None)` is the only mode.
- **Auga (GUI), Rödd (voice), Bifröst (HTTP face).**
- **Multi-operator wells.** First slice is single-operator only.
- **Plugins.** First slice has no plugin loader.

---

## 5. Forge Worker's quality bar

For each phase:

- **Type-checked under mypy strict.** No `Any` escape hatches in interfaces.
- **One responsibility per function**, methods under 50 lines (RULES.AI.md Python Style Laws).
- **No hardcoded settings**, **no hardcoded paths**, **no `print`** — loggers only.
- **Every public function has a one-line docstring** (no multi-paragraph essays).
- **Every subpackage has its INTERFACE.md** written *before* the code in that subpackage is merged.
- **Whole files only** — no fragments, no partials in any commit.

When a phase ships, the closing rite of `MYTHIC_ENGINEERING.md` applies: Auditor pass, DEVLOG entry, push.

---

## 6. Risks the Forge Worker flags now

| Risk | Mitigation |
|---|---|
| Ollama embedding throughput on a Pi is slow (~minutes per hundred chunks of `nomic-embed-text`) | Smiðja's journal makes long ingests resumable; document expected duration in `deploy/pi/INSTALL.md`. |
| `sqlite-vec` HNSW index does not yet support all distance metrics in stable releases | Pin a known-good version; ship a `tests/integration/test_sqlite_vec_smoke.py` that fails fast if upstream regresses. |
| Phi-3-mini at Q4 still uses ~2 GB resident on a Pi 5 (8 GB OK; 4 GB Pi marginal) | Default to `phi3:mini`; recommend `qwen2.5:0.5b` for 4-GB-class Pis in `FUNI_LOCAL_MODEL_OPTIONS.md`. |
| Hjarta's auto-detect for Ollama assumes `localhost:11434` | Hjarta asks the operator before assuming; auto-detect is *a suggestion*, not a default. |

---

## 7. The Forge Worker's closing word

> *Potential means nothing until it survives effort. The first slice will be ugly in places and beautiful in others — that is how a real thing is forged. The shape stays clean; the surface gets honest scars.*

— Eldra Járnsdóttir
