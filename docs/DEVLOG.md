# DEVLOG — Ember

**Append-only.** New entries go at the top. Each entry: date, scope, what shipped, what's next, who.

The DEVLOG is read at the start of every session. It is the Cartographer's first reference and the Scribe's last word of each session.

The DEVLOG of the parent project Runa-Agent-Digital-Being is preserved at `docs/archive/runa-inherited/DEVLOG.md` for lineage reference. Ember's record begins here.

---

## 2026-05-21 — Phase 3 shipped: Well realm wired end-to-end.

**Who:** Claude (Opus 4.7, 1M context). Voices rotated: Architect (Brunnr handle Protocol), Forge Worker (sqlite_vec adapter + Smiðja modules), Auditor (test suite + bug fixes mid-phase), Scribe (this entry).
**Scope:** Phase 3 of `docs/architecture/EMBER_FIRST_SLICE_PLAN.md` §3 — the first end-to-end vertical that actually writes embeddings to disk and reads them back. Real `sqlite-vec` 0.1.9 in a `.venv`. No code beyond what the plan listed; integration test mocks the embedding endpoint with deterministic content-addressed vectors so no Ollama is required.

### What shipped

**Schemas (additive to Phase 2)**
- `src/ember/schemas/ingest.py` — `IngestJob`, `IngestEntry`, `IngestSummary`, `ParsedFile`, `IngestSourceKind` enum, `IngestEntryStatus` enum.

**Brunnr (the Well's storage layer)**
- `src/ember/well/brunnr/handle.py` — `@runtime_checkable` `BrunnrHandle` Protocol plus `open(config)` registry. Dispatches on `config.backend`; unknown/unimplemented backends return `Disconnected(reason=CONFIG_INVALID)` rather than raising.
- `src/ember/well/brunnr/sqlite_vec/adapter.py` — `SqliteVecBrunnr` implementing the protocol. Vec store via sqlite-vec `vec0` virtual table; FTS5 with insert/update/delete triggers; hybrid search via reciprocal rank fusion (k=60). Connection failure → `Disconnected`. Schema-mismatched embedding dim → `BrunnrError`.
- `src/ember/well/brunnr/sqlite_vec/schema.sql` — DDL loaded via `importlib.resources`, `{embedding_dim}` substituted from `BrunnrConfig.embedding_dim` at apply time. Schema version marker.
- `src/ember/well/brunnr/sqlite_vec/__init__.py` — re-exports.
- `src/ember/well/brunnr/sqlite_vec/INTERFACE.md` — adapter contract; calls out the lock-at-first-apply behaviour for `embedding_dim`.

**Smiðja (the Well's ingest forge)**
- `src/ember/well/smidja/chunker.py` — paragraph → sentence → word → char fallback splitter. Returned chunks satisfy `chunk.text == original[chunk.char_start:chunk.char_end]` *exactly*, so original whitespace is preserved and `max_chars` is honored as a true ceiling (no silent over-runs from separator-length math).
- `src/ember/well/smidja/embed_client.py` — `OllamaEmbedClient`, stdlib `urllib.request` only (no httpx dep). Batches per `EmbeddingConfig.batch_size`, exponential backoff, per-batch failure returns `EmbedResult` with `None`-vectors rather than raising. Embed-or-skip semantics per `SMIDJA_INGEST_PATTERNS.md` §4.
- `src/ember/well/smidja/journal.py` — `Journal` with atomic writes (`NamedTemporaryFile` + `os.replace`), heartbeat every N updates or on-demand, `complete()` moves the file to `done/` subdir. Resume by matching `source_root`.
- `src/ember/well/smidja/local_files/source.py` — `walk()` plus the orchestrator `run(brunnr, *, root, smidja_config, embed_client, ...)`. Walk → hash → check duplicate → chunk → embed → write. Each file is a journal entry; per-chunk embedding failures contribute to `IngestSummary.n_failed` without aborting the doc.
- `src/ember/well/smidja/local_files/__init__.py` — re-exports.

**Tests**
- `tests/unit/test_brunnr_handle.py` — registry returns `Disconnected` for unimplemented backends; Protocol is `runtime_checkable`.
- `tests/unit/test_brunnr_sqlite_vec.py` — 11 tests covering: open creates DB file, open returns Disconnected on missing sqlite_vec config, idempotent `add_document`, dim-mismatch refusal, vector/text/hybrid search ranking, embedding round-trip via `get_chunk`, episode persistence, initial counts. Skipped automatically if `sqlite-vec` isn't installed (`pytest.importorskip`).
- `tests/unit/test_smidja_chunker.py` — 8 tests covering: short/empty text, paragraph preference, hard max ceiling, oversize-paragraph sentence fallback, pure-overlong char fallback, consecutive indexing, Gungnir-aligned defaults, char-boundary behaviour.
- `tests/unit/test_smidja_embed_client.py` — 6 tests covering: empty input, single batch shape, multi-batch concatenation, URL-error → None-vectors, mismatched response size → None-vectors, invalid JSON → None-vectors. All mocked.
- `tests/unit/test_smidja_journal.py` — 8 tests covering: file creation, status persistence, resume by source_root, distinct-roots get distinct jobs, failure recording, complete() move, `pending()`, atomic-write tmp-file cleanup.
- `tests/unit/test_smidja_local_files.py` — 8 tests covering: include/exclude, suffix-based content_type, hash determinism, non-utf8 skip, missing-root error, file-as-root error, sorted-deterministic order.
- `tests/integration/test_ingest_then_query.py` — 3 tests covering: full ingest → query round trip with a 32-dim deterministic content-addressed mock embedder; resume idempotency (hash-based at the Brunnr layer); per-chunk failure isolation.

**Suite size: 128 tests, 0.20s, ruff clean.**

**Config + docs**
- `pyproject.toml` — `sqlite_vec = ["sqlite-vec>=0.1.6"]` added under `[project.optional-dependencies]`; planned-for-later list trimmed of `ollama` (stdlib urllib reaches the endpoint).
- `src/ember/well/brunnr/INTERFACE.md` — updated from "(planned, Phase 3 onward)" to "(shipped Phase 3, 2026-05-21)".
- `src/ember/well/smidja/INTERFACE.md` — same.
- `src/ember/__init__.py` — module docstring updated to reflect Phases 1-3 complete.

### What's next

- **Phase 4 of the first slice:** `ember.thread.strengr` — wraps `ember.well.brunnr.handle.open()` with auth/retry/health-check policy and the typed-Disconnected contract enforced at the Spark↔Well boundary. Initially supports only `sqlite_vec`; the same handle shape will work for the Phase 8 `pgvector` adapter.
- **Light root edits** still pending: Ember-descent rows in `ORIGINS.md`; check root `PHILOSOPHY.md` for Runa-specific phrasings.

### Notes & gotchas

- **Stdlib urllib over httpx for the embed client.** Vow of Smallness wins again. The Ollama endpoint is one POST; stdlib handles it. Saves ~5 MB of deps on a Pi.
- **Chunker rewrite mid-phase.** First attempt computed chunk lengths from segment-body lengths plus a `"\n\n"` separator constant, which was off-by-one and produced chunks slightly over `max_chars` for some inputs. The fix was to track only `(start, end)` ranges into the original text and slice at the end — the slice's actual length is authoritative. Caught by the chunker shape-contract tests *before* integration.
- **Walker rewrite mid-phase.** First attempt used `fnmatch.fnmatch(rel_path, "**/*.md")` patterns, but fnmatch doesn't understand the `**` glob (that's a pathlib-only feature). Rewrote to suffix-based filtering — simpler, matches the test contract, supports the same operator-facing semantics.
- **`Disconnected` and `BrunnrError` split.** Connection-style failures (missing config, dir-create denied, sqlite-vec load failure, schema apply failure) return `Disconnected` rather than raising. Per-call programming errors (mismatched embedding dim, missing chunk lookup) raise `BrunnrError`. The split keeps the Vow of Graceful Offline distinct from the "your code is wrong" case.
- **No mypy run this session** — mypy not installed on this host. Ruff is the only static check in CI for now; mypy belongs in a real CI loop with a fresh venv install.
- **`.venv/` is gitignored.** Created for this session to install `sqlite-vec` and `pytest`; not committed.

---

## 2026-05-21 — Phase 1 closure: skeleton-import test added.

**Who:** Claude (Opus 4.7, 1M context). Voice: Auditor (Sólrún Hvítmynd).
**Scope:** Volmarr asked whether Phase 1 had been fully completed. The four structural bullets (`src/runa/` archived, `src/ember/` built, `pyproject.toml` rewritten, `__main__.py` raises clean `NotImplementedError`) all landed in commit `045fda6`. The fifth bullet — *"Tests: import-only"* — had been rolled forward into Phase 2's `tests/unit/test_schemas_import.py`, which only covers the schemas subpackage. This entry closes the gap for the full Three Realms tree.

### What shipped

- **`tests/unit/test_skeleton_imports.py`** — parametrised import test over the 12 importable subpackages of `src/ember/`: `ember`, `ember.cli`, `ember.schemas`, `ember.spark` (+ `funi`, `hjarta`, `munnr`), `ember.thread` (+ `strengr`), `ember.well` (+ `brunnr`, `smidja`). Plus three specific assertions:
    - `ember.__version__` is `"0.0.0"`.
    - `ember.__main__` imports cleanly and exposes a callable `main`.
    - `ember.__main__.main()` raises `NotImplementedError` with a message that mentions `EMBER_FIRST_SLICE_PLAN`.
- **Suite size:** 81 tests (was 66 after Phase 2), 0.09s, ruff clean.

### What's next

Phase 3 of the first slice — the `sqlite_vec` Brunnr adapter, `local_files` Smiðja, chunker, embed client, resumable journal. First end-to-end vertical that writes embeddings to disk.

### Notes

- Phase 1 is now strictly complete per the plan's bullet list. No code or doc change required beyond the new test file; the scaffolding it tests was already correct.
- Failure of any parametrised case in this test would name the breach — typically a circular import, a typo in an `__init__.py`, or a stray top-level statement that fails at import time.

---

## 2026-05-21 — Phase 2 shipped: ember.schemas populated, 66 shape tests green.

**Who:** Claude (Opus 4.7, 1M context). Voice: Forge Worker (Eldra Járnsdóttir) for the code; Auditor (Sólrún Hvítmynd) for the tests; Scribe (Eirwyn Rúnblóm) for this entry.
**Scope:** Execute Phase 2 of `EMBER_FIRST_SLICE_PLAN.md` §3 — the gravitational floor: typed schemas only. No behaviour, no I/O, no sibling-realm imports.

### What shipped

- **Five schema modules** under `src/ember/schemas/`, stdlib-only (`dataclasses` + `enum.StrEnum`, no pydantic dependency):
    - **`errors.py`** — `EmberError` base; per-realm hierarchy: `SchemaError`, `ConfigError`, `WellError`/`BrunnrError`/`IngestError`, `ThreadError`/`StrengrError`, `SparkError`/`FuniError`/`HjartaError`/`MunnrError`. Plus the non-raised failure value **`Disconnected(reason, since, detail)`** with the `DisconnectReason` enum — Strengr's mechanical implementation of the Vow of Graceful Offline.
    - **`config.py`** — `EmberConfig` (top-level) composing `IdentityConfig`, `FuniConfig` (+ `FuniOllamaConfig`), `StrengrConfig`, `BrunnrConfig` (+ `SqliteVecConfig`, `PgVectorConfig`), `SmidjaConfig` (+ `ChunkerConfig`, `EmbeddingConfig`, `JournalConfig`), `LoggingConfig` (+ `LoggingDestination`). Six enums: `BrunnrBackend`, `FuniRuntime`, `LogLevel`, `LogFormat`, `LogDestinationKind`, `BoundaryPreference`. **Defaults are Gungnir-aligned** where applicable (`embedding_dim=768`; chunker `max=2000` / `target=1684`; model `phi3:mini` / `nomic-embed-text`). Path fields use `pathlib.Path` *without* `expanduser()` — consumer expands at use time so `$HOME` isn't frozen at import.
    - **`chunks.py`** — `Document`, `Chunk` (embedding as `tuple[float, ...]` to keep the dataclass truly frozen), `RetrievalHit`, `BrunnrStats`. Column-aligned with the Gungnir schema captured in `docs/adapters/GUNGNIR_WELL_REFERENCE.md` §3.
    - **`episode.py`** — `Episode(operator_input, ember_reply, cited_chunk_ids, funi_model, well_disconnected, started_at, completed_at, id)`. The `well_disconnected` flag mirrors `DATA_FLOW.md` §2.2 — when the Well is unreachable the Episode records that fact for later flush-in.
    - **`funi.py`** — `FuniReply`, `FuniHealth`, the non-raised failure value **`Unavailable(reason, detail)`** with `UnavailableReason` enum (parallel to `Disconnected`), `ContextItem` (+ `ContextKind` enum), `ToolCall`, `FinishReason` enum (includes `REFUSED` so Funi can stop cleanly per the Vow of Honest Memory).
- **All dataclasses are `frozen=True, slots=True`.** All enums are `StrEnum` (Python 3.11+ stdlib).
- **66 shape-contract tests** under `tests/unit/test_schemas_*.py`, organised one file per schema module plus `test_schemas_import.py` (verifies the gravitational floor — schemas import without reaching into any sibling realm). Suite runs in 0.09s. All green.
- **`tests/conftest.py`** added — adds `src/` to `sys.path` so tests run without an editable install. Documented as a temporary ergonomic shim.
- **`src/ember/schemas/INTERFACE.md`** updated from "(planned, Phase 2)" to "(shipped Phase 2, 2026-05-21)" with the full exported surface enumerated and the floor-test cited as the import-allowlist enforcer.
- **`src/ember/__init__.py`** module docstring updated to reflect Phase 2 complete.
- **Ruff clean.** No mypy run this session (mypy not installed on the travel laptop; strict mypy check belongs in CI per `pyproject.toml`).

### What's next

- **Phase 3 of the first slice** per `EMBER_FIRST_SLICE_PLAN.md` §3: the `sqlite_vec` Brunnr adapter, the `local_files` Smiðja, the chunker, the embed client, the resumable journal. First end-to-end vertical that actually writes embeddings to disk. Tests: write-then-query round trip, journal resume, chunk-size invariants.
- **Light root edits** still pending: Ember-descent rows in `ORIGINS.md`; check root `PHILOSOPHY.md` for Runa-specific phrasings.

### Notes

- Stdlib `dataclasses` chosen over `pydantic` for Phase 2 to honour the Vow of Smallness. The cost is no runtime validation beyond the type system — but Phase 2 has no validation responsibility anyway (the loader's Phase 6). Easy to swap to `pydantic` per-module later if needed; the `__all__` exports are the public surface.
- `tuple[float, ...]` is the right embedding type for a frozen dataclass; `list[float]` would be a mutable field on a "frozen" container. Phase 3's Brunnr adapter is where the practical perf trade against `numpy.ndarray` becomes worth re-evaluating.
- `StrEnum` (Python 3.11+) replaces the older `class X(str, Enum)` pattern across all five modules. The values are still plain strings, comparison and serialisation behaviour are unchanged.
- The schema test for non-sibling-imports walks every module's exported attribute and refuses any `__module__` that starts with `ember.well`, `ember.thread`, `ember.spark`, or `ember.cli`. If the floor is breached in a future phase, the test will name the breach.

---

## 2026-05-21 — Six True Names formally ratified. EMBER_TRUE_NAMES.md added.

**Who:** Claude (Opus 4.7, 1M context) continuing the same session. Voice: Skald (Sigrún Ljósbrá) for the new doc; Scribe (Eirwyn Rúnblóm) for this entry.
**Scope:** Capture Volmarr's formal ratification of the Six True Names and preserve the per-name explanatory record they were ratified against.

### What shipped

- **Volmarr's ratification of all six names** — *"names are all approved"*. Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr are now canonical. The longstanding item from the 2026-05-19 "What's next" — Skald's True Names ratification — is closed.
- **`docs/architecture/EMBER_TRUE_NAMES.md`** — new canonical reference doc, Skald-voiced. One section per True Name covering: Old Norse meaning, realm + code path, what it is, what it's for, owns/does-not-own, why the name was chosen. Includes the Three Realms grouping, the conversation-turn flow tying all six together, and the discipline-of-naming framing. Ratification recorded in §5 with rules for any future rename.

### What's next

- **First-slice Phase 2 begins** (the next commit) per `EMBER_FIRST_SLICE_PLAN.md` §3 Phase 2: ship `ember.schemas.{errors,config,chunks,episode,funi}`. Types only. Tests: shape contracts only. With the names ratified, every typed identifier in the schemas can lean on them.
- **Light root edits** still pending from 2026-05-19: Ember-descent rows in `ORIGINS.md`; Runa-specific phrasing pass on root `PHILOSOPHY.md`.

### Notes

- The ratification covers the names as they appear in `SYSTEM_VISION.md` §4 and as used throughout `ARCHITECTURE.md` / `DOMAIN_MAP.md` / `DATA_FLOW.md` / `EMBER_TRUE_NAMES.md` / `pyproject.toml` (via folder paths) / `config/ember.example.yaml` / every `INTERFACE.md` in `src/ember/`. Renaming from this point requires an ADR, a single atomic commit touching every reference, and updates to all five canonical docs in the same commit.
- This entry is intentionally short. The substance is in the new `EMBER_TRUE_NAMES.md`; this is the index pointer.

---

## 2026-05-21 — Ember fork-delta executed. Three Realms tree built. Runa skeleton archived.

**Who:** Claude (Opus 4.7, 1M context) on the travel laptop, continuing the same session as the earlier 2026-05-21 entry below. Roles rotated: Architect (mostly), Forge Worker (the new `src/ember/` files), Cartographer (the archive mapping), Scribe (this entry).
**Scope:** Execute step 6 of `docs/architecture/EMBER_FORK_DELTA.md` §7 after Volmarr's ratification ("good work buddy! Go for Ember fork delta!"). Bring the file tree into alignment with the ratified architecture. **No first-slice code in this commit — that is the next commit.**

### What shipped

- **`src/ember/` tree built** to match the Three Realms layout in `docs/architecture/DOMAIN_MAP.md`:
    ```
    src/ember/
    ├── __init__.py, __main__.py, README.md
    ├── schemas/         (+ INTERFACE.md, README.md)
    ├── well/
    │   ├── brunnr/      (+ INTERFACE.md, README.md)
    │   └── smidja/      (+ INTERFACE.md, README.md)
    ├── thread/
    │   └── strengr/     (+ INTERFACE.md, README.md)
    ├── spark/
    │   ├── funi/        (+ INTERFACE.md, README.md)
    │   ├── hjarta/      (+ INTERFACE.md, README.md)
    │   └── munnr/       (+ INTERFACE.md, README.md)
    └── cli/             (+ INTERFACE.md, README.md)
    ```
  Each subpackage has an empty `__init__.py`, a one-page `README.md`, and an `INTERFACE.md` draft that cites the matching `DOMAIN_MAP.md` section. **No code yet** beyond `__init__.py` and `__main__.py`.
- **`src/ember/__main__.py`** raises a friendly `NotImplementedError` pointing at `EMBER_FIRST_SLICE_PLAN.md`. `python -m ember` and `ember` (once installed) both resolve to it.
- **Archived the inherited Runa skeleton** to `docs/archive/runa-inherited/src-skeleton/runa/` via `git mv` (rename history preserved). Added `docs/archive/runa-inherited/src-skeleton/README.md` explaining the lineage.
- **Promoted the EMBER-prefixed architecture docs to canonical names** via `git mv`:
    - `docs/architecture/ARCHITECTURE.md` (was Runa's; Runa version → `docs/archive/runa-inherited/architecture/ARCHITECTURE.md`; Ember version promoted from `EMBER_ARCHITECTURE.md`).
    - `docs/architecture/DOMAIN_MAP.md` (same shape).
    - `docs/architecture/DATA_FLOW.md` (same shape).
  Each canonical doc's header updated: **Status: Ratified 2026-05-21 by Volmarr**, "promoted from EMBER_*.md", inter-doc cross-refs rewritten to canonical names, `(parent Runa shape)` cross-refs rewritten to the archive path. ARCHITECTURE.md §8 rewritten in past tense to record the promotion event.
- **Added `docs/archive/runa-inherited/architecture/README.md`** mapping each archived file to its canonical Ember replacement.
- **`pyproject.toml` rewritten** for Ember:
    - `name = "ember-agent"`
    - entry point `ember = "ember.cli.main:main"`
    - `[tool.hatch.build.targets.wheel] packages = ["src/ember"]`
    - `[tool.mypy] files = ["src/ember"]`; `[tool.coverage.run] source = ["src/ember"]`
    - planned optional-dependencies groups commented in for each Brunnr backend and each Funi runtime
    - added `requires_pi` pytest marker
- **`config/runa.example.yaml` → `config/ember.example.yaml`** via `git mv`, with contents rewritten to the Ember shape: identity (name + role), Funi (Ollama with phi3:mini default), Strengr (timeout + retry), Brunnr (sqlite_vec default + commented pgvector example for Gungnir), Smiðja (Gungnir-aligned chunker defaults: 2000-char max, 1684 target), logging.
- **Cross-references updated** in `docs/adapters/{BRUNNR_BACKEND_MATRIX,FUNI_LOCAL_MODEL_OPTIONS,GUNGNIR_WELL_REFERENCE,SMIDJA_INGEST_PATTERNS}.md` and `docs/architecture/EMBER_{FIRST_SLICE_PLAN,FORK_DELTA}.md` from `EMBER_*.md` → canonical names. ADR 0006 retains its as-proposed snapshot text with a clearly-marked "Update 2026-05-21 (post-ratification)" footnote pointing forward.
- **`docs/architecture/README.md`** rewritten to describe Ember-shape canonical docs and the living working docs (FORK_DELTA, FIRST_SLICE_PLAN), with a Runa-lineage section.
- **`docs/REPO_MAP.md`** updated: `(planned)` removed from src/ember entries; src/runa entry rewritten as archived; `(planned)` removed from `config/ember.example.yaml`; archive entry expanded to mention the new subdirs.
- **`docs/architecture/EMBER_FORK_DELTA.md` §3.1 table** updated: each "Move to archive" / "Promote to canonical" row marked **Done 2026-05-21**.

### What's next (the next commit)

- **First slice begins.** Per `docs/architecture/EMBER_FIRST_SLICE_PLAN.md` §3 Phase 2: ship `ember.schemas.errors`, `ember.schemas.config`, `ember.schemas.chunks`, `ember.schemas.episode`, `ember.schemas.funi` — types only. Tests: shape contracts only.
- **Skald's True Names ratification** (item 3 from 2026-05-19, still pending). The names Funi/Strengr/Brunnr/Smiðja/Hjarta/Munnr are now load-bearing across the file tree; final ratification would lock them.
- **Light root edits** still pending: Ember-descent rows in `ORIGINS.md`; check root `PHILOSOPHY.md` for any Runa-specific phrasings worth softening.

### Notes

- Per the additive rule, **nothing was deleted in this session**. Every move was a `git mv`; every "new" file at a canonical path was the Ember version promoted from `EMBER_*.md`; every "deleted" entry git status shows is a rename git's similarity heuristic chose not to recognise (verified by content read at every old and new path before commit).
- The Runa skeleton archive at `docs/archive/runa-inherited/src-skeleton/runa/` preserves all the per-subpackage `README.md` and `INTERFACE.md` drafts from the parent project. They remain reachable to anyone reading the inheritance.
- `python -m ember` now resolves to a clean `NotImplementedError` with a friendly pointer — i.e. *honest failure*, the same shape the Vow of Graceful Offline asks of the runtime.
- The Ember-shape `config/ember.example.yaml` includes a commented-in `pgvector` block that operators can uncomment to point Ember at Gungnir (or any Gungnir-compatible Postgres) once the `pgvector` Brunnr ships in Phase 8.

---

## 2026-05-21 — Ember architecture first-pass + live Gungnir survey.

**Who:** Claude (Opus 4.7, 1M context) working under Volmarr on the travel laptop — rotating through Cartographer, Architect, Forge Worker, and Scribe roles. Mythic Engineering activated at session start.
**Scope:** Address three of the four "What's next" items from the 2026-05-19 entry — the Architect's first pass, the Cartographer's reading review, and the first Forge slice's plan — and ground them in a live read of the Gungnir knowledge database.

### What shipped

- **`docs/architecture/EMBER_ARCHITECTURE.md`** — Ember-specific shape. Three Realms (Spark/Thread/Well), Six True Names, dependency law, why-no-kernel-no-bus, what-is-not-in-this-architecture, first-slice anchor, and disposition recommendation for the inherited Runa-shaped canonical files.
- **`docs/architecture/EMBER_DOMAIN_MAP.md`** — Per-subpackage ownership for the planned `src/ember/{schemas,well/{brunnr,smidja},thread/strengr,spark/{funi,hjarta,munnr},cli}/`. Brunnr and Funi minimum-surface interface tables included.
- **`docs/architecture/EMBER_DATA_FLOW.md`** — The three canonical flows (conversation turn, ingest job, first-run rite) with explicit happy + sad paths, including the Vow of Graceful Offline in flow form.
- **`docs/architecture/EMBER_FORK_DELTA.md`** — Cartographer's recommendation for every inherited file/folder: keep / move-to-archive / rewrite, with rationale and ratification-gated execution order. No deletions proposed.
- **`docs/architecture/EMBER_FIRST_SLICE_PLAN.md`** — File-by-file plan for ~38 new files across seven phases, ≤2 500 LOC target, with explicit non-goals and risk register.
- **`docs/adapters/BRUNNR_BACKEND_MATRIX.md`** — Storage backend comparison and selection rule.
- **`docs/adapters/FUNI_LOCAL_MODEL_OPTIONS.md`** — Local-LLM ladder by host RAM, why Phi Silica / Apple Foundation are second-slice, embedding-dim recommendation locked to 768 for Gungnir compatibility.
- **`docs/adapters/GUNGNIR_WELL_REFERENCE.md`** — Live survey conducted today against `knowledge` on Gungnir: complete schema, real counts (95 docs / 35 682 chunks / 768-dim / 394 MB / 97% buffer hit), Skein vs LLM-extracted KG distinction, hybrid-search pattern.
- **`docs/adapters/SMIDJA_INGEST_PATTERNS.md`** — Four ingest patterns, Gungnir-calibrated chunking defaults (~1684 chars avg, 2000 max), resumable-journal contract.
- **`docs/decisions/0006-ember-architecture-and-gungnir-survey-2026-05-21.md`** — ADR capturing all proposed decisions, alternatives considered, open follow-ups.

### What's next

- **Volmarr ratification.** Read EMBER_ARCHITECTURE.md, EMBER_DOMAIN_MAP.md, EMBER_DATA_FLOW.md, EMBER_FORK_DELTA.md, EMBER_FIRST_SLICE_PLAN.md and ADR 0006. Confirm, revise, or replace.
- **Skald's True Names ratification** (item 3 from the 2026-05-19 entry — *not* addressed in this session). The names Funi/Strengr/Brunnr/Smiðja/Hjarta/Munnr are used throughout the new docs as if ratified; Volmarr's final word is still pending.
- **Next commit (after ratification):** `src/runa/` → `src/ember/` rename, archive the inherited `src/runa/` skeleton under `docs/archive/runa-inherited/src-skeleton/`, rewrite `pyproject.toml` (package `ember-agent`, entry point `ember`). Per ADR 0006 §4.1.
- **Light root edits** still pending from 2026-05-19: Ember-descent rows in `ORIGINS.md`; check root `PHILOSOPHY.md` for Runa-specific phrasings.
- **First Forge slice begins** after the rename: Phase 2 (schemas), per `EMBER_FIRST_SLICE_PLAN.md`.

### Gungnir survey — load-bearing measurements

Captured today against the running database. Reproduce by re-running the queries cited in `docs/adapters/GUNGNIR_WELL_REFERENCE.md` §4:

- PostgreSQL 18.3, pgvector 0.8.1, pg_trgm 1.6.
- 95 documents (42 md, 26 web/markdown, 13 json, 9 jsonl, 5 yaml). 35 682 chunks, all 768-dim embedded via `nomic-embed-text`.
- Chunk text: avg **1 684** chars, max **2 000** — this is the calibration anchor for Ember's chunker default.
- 394 MB database total; 372 MB of that is `chunks` (mostly embeddings).
- Buffer cache hit 97.0% tables / 99.8% indexes — healthy.
- Two parallel KG layers: `skein_*` (embedding-derived, 276 entities × 855 relations across the full corpus; broad but with known false-friend artifacts) and `kg_*` (LLM-extracted per chunk, 366 entities × 176 relations across only 202 of 35 682 chunks; precise but expensive). This cheap-broad-vs-expensive-precise split is load-bearing for any future Ember KG work.

### Notes

- Per the additive rule, **nothing was deleted in this session**. Every file is new; no existing file modified except this DEVLOG (which is itself append-only by design).
- The Ember-specific architecture documents live at the `EMBER_*.md` prefix rather than overwriting the canonical `ARCHITECTURE.md`/`DOMAIN_MAP.md`/`DATA_FLOW.md` paths. The inherited Runa-shaped files at those canonical paths are preserved untouched; ADR 0006 proposes their migration to `docs/archive/runa-inherited/architecture/` only after Volmarr's ratification.
- The session ran on the travel laptop (Kubuntu 26.04 + RTX 2060), with Gungnir reachable over Tailscale. The `mcp__knowledge__*` tools provided read-only access to the live Postgres DB.
- The Skald-voice scrolls authored by Runa on 2026-05-19 (`docs/SYSTEM_VISION.md`, `docs/REPO_MAP.md`, root `MYTHIC_ENGINEERING.md`) are treated as **normative source-of-truth** throughout the new documents — they are cited but not modified.

---

## 2026-05-19 — Ember born. Fork from Runa. Soul-layer authored.

**Who:** Runa (the AI working under Volmarr from Mjolnir) — speaking in turn as Skald, Cartographer, and Scribe.
**Scope:** Project naming, repository creation, fork from Runa-Agent-Digital-Being, additive archive of the Runa-named soul-layer scrolls, and authoring of Ember's own soul layer.

### What shipped

- **The name "Ember"** chosen in a Skald pass with Volmarr. Public-pronounceable, mythically resonant as the spark from Eldra Járnsdóttir's forge. Selected over Hugin, Saga, and Wren for maximum user-facing accessibility while keeping mythic compatibility.
- **Repository created** at `hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster` (the toaster pun preserved in the repository name itself). Local clone at `C:/Users/volma/runa/Project_Ember_Run_It_On_Your_Smart_Toaster/` on Mjolnir. Default branch: `development`.
- **Knowledge DB on Gungnir** wired to Mjolnir during the same evening — Postgres 18 + pgvector + Ollama on the tailnet, MCP server `knowledge` at user scope. The first concrete Brunnr-shaped well Ember can be tethered to, and the proof that the storage layer can be sovereign and shared.
- **Additive archive** of inherited Runa-named scrolls into `docs/archive/runa-inherited/` (via `git mv`, with rename history preserved):
  - `docs/SYSTEM_VISION.md` *(Runa's)*
  - `docs/REPO_MAP.md` *(Runa's)*
  - `docs/DEVLOG.md` *(Runa's bootstrap-day log)*
  - `MYTHIC_ENGINEERING.md` *(Runa's, was at repo root)*
  - `TASK_runa_bootstrap.md`
  - `TASK_runa_python_craft.md`
  - `TASK_runa_research_corpus.md`
  - `TASK_runa_research_corpus_2.md`
- **Fresh Ember scrolls** authored at the now-vacant canonical paths:
  - `docs/SYSTEM_VISION.md` — Ember's Skald scroll. Six True Names (Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr) and three Realms (Spark, Thread, Well). Nine Unbreakable Vows.
  - `docs/REPO_MAP.md` — Ember's Cartographer scroll. Reflects what exists now plus near-term planned shape.
  - `docs/DEVLOG.md` — *(this file, this entry)*
  - `MYTHIC_ENGINEERING.md` (root) — Ember's compact methodology statement, lightly adapted from the inherited version.
- **Archive convention extended** additively:
  - `docs/archive/runa-inherited/README.md` — new, explains the lineage subfolder.
  - `docs/archive/README.md` — additive update, documents the new "grouped fork-inheritance archives" subfolder pattern alongside the existing single-file dated-suffix convention.

### What's next

- **Architect's first pass.** Author `docs/architecture/ARCHITECTURE.md`, `DOMAIN_MAP.md`, `DATA_FLOW.md` for Ember. Locate the Three Realms in `src/`. Decide on the rename `src/runa/` → `src/ember/` and the migration plan for the inherited skeleton.
- **Cartographer's reading review.** Walk the inherited research corpus (`docs/research/`) and the inherited Python craft corpus (`docs/python/`); mark the 10–20 docs most load-bearing for Ember's smaller scope; leave the rest as inherited reference without re-reading every one.
- **Skald's True Names ratification.** Hold the six names (Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr) with Volmarr; either ratify or revise.
- **First Forge slice.** Smallest end-to-end vertical: Hjarta wizard → Strengr to a local SQLite Brunnr → first Funi answer grounded in retrieved chunks. *No code in this commit; this is the next obvious work.*
- **Light root edits** (next commit, not this one): add Ember-descent entry to `ORIGINS.md`; check root `PHILOSOPHY.md` for any Runa-specific phrasings worth softening.

### Notes

- The cute Ember README ("*Got a toaster? Good!*") is preserved unchanged. It is correct as it stands.
- The 16 KB `ORIGINS.md` and the 599 KB `Yggdrasil_and_Huginn_and_Muninn_Theory.md` remain at the root unchanged. They are inherited but applicable.
- Per the additive rule, **nothing was deleted in this session**. Every move was a `git mv`; every replacement is a new file at the now-vacant path; every edit to the archive index was additive (new section appended, no removal).
- Volmarr had earlier the same evening wired the Gungnir knowledge well into the Mjolnir MCP layer (after a memorable VPN-related diagnostic detour). That work, recorded in Runa's local memory, informs Ember's Vow of Pluggable Storage and Vow of Tethered Grounding directly.

---

*(The parent project's DEVLOG entries follow at `docs/archive/runa-inherited/DEVLOG.md`.)*
