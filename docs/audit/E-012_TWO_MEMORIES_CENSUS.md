# E-012 — The Two-Memories Census

*Project Ember campaign, Part I (The Monorepo's True State).
Measured 2026-10-31 on branch `yrsa/ember-road-build` in the
campaign's own clone (`~/workspace/ember-build`), at campaign
commit 22facc6 (E-011 banked). Both members were measured
from this tree — code, packaging, tests, git, and fresh
runner passes this slice (deps supplied from the isolated
target dir of the E-004/E-005 method, proxy env cleaned per
E-005's proven httpx finding; nothing installed into the
system env). Raw run tails are summarised in §6; no store
belonging to either system was opened, migrated, or
modified — every test ran against its own fixtures.*

## Headline — read this first, in plain words

**There are two full memory systems in this house, they
overlap on the everyday work of remembering, and neither
one is connected to the companion.** Both can store a
memory, search it, keep a knowledge graph, hold
conversations, and repair themselves. Each also does
things the other does not do at all:

- **mempalace** (`mempalace/`, v3.3.5) is the *verbatim
  archive*: it mines whole projects and whole
  conversations into a "palace" of wings, rooms, closets
  and drawers, and finds things again by meaning
  (embeddings) as well as by words. It is an upstream
  open-source project (MemPalace, by milla-jovovich)
  imported whole — big, benchmarked, MCP-served, and
  heavy: its search brain is ChromaDB plus an ONNX
  embedding model.
- **mimir-well** (`mimir-well/`, v2.10.4) is the
  *living memory*: a single SQLite file of memories
  that carry importance and feeling, fade by the
  Ebbinghaus forgetting curve unless reinforced, can be
  superseded when the world changes, and are guarded,
  audited, and budgeted for context. It is the house's
  own line (Runa/Hermes heritage, author Eldrä
  Járnsdóttir) — small, stdlib-only at its core, and
  shaped exactly for a companion.

**The Ember core uses neither.** `src/ember/` contains
zero imports of either system (proven §5): the
companion's live memory today is a *third* system, its
own `src/ember/well/` (Brunnr: sqlite_vec / pgvector).
So Part V's question is not "which of the two is wired
in" — it is "which face, if any, the companion should
have, given that it currently has a different one."
That verdict is Part V's (E-077–E-079); this census is
its evidence. No system is retired, merged, or judged
here.

## 1. The two at a glance

| Fact | mempalace | mimir-well |
|---|---|---|
| Version / licence | 3.3.5, MIT (E-007 verified) | 2.10.4, MIT (E-007 verified) |
| Provenance | Upstream OSS: pyproject homepage/repository = `github.com/MemPalace/mempalace`, author milla-jovovich | House line: homepage = `github.com/runafreyjasdottir/mimir-well`, author Eldrä Járnsdóttir |
| History here | ONE import commit f7ef473, 2026-05-21 (E-002) | ONE import commit 911eeba, 2026-05-21 (E-002) |
| Tree weight | 59,194,391 B / 262 files (this slice, excl. `__pycache__`); ~43 MB of it is `benchmarks/` (incl. ~38.5 MB result `.jsonl`, E-002) + website/landing | 638,182 B / 63 files (this slice, excl. `__pycache__`) |
| Code mass | Package alone 25,318 lines (`mempalace/mempalace/*.py` + subpackages, this slice) | Whole `src/` 6,496 lines |
| Core deps | `chromadb>=1.5.4,<2`, `pyyaml`, (+ ONNX runtime via chromadb's embedding function; GPU/DML/CoreML extras) | **None for the core** (stdlib `sqlite3` etc.); the single declared dep `flask>=3.0` serves only the Eye dashboard |
| Store | A palace *directory* (default `~/.mempalace/palace`): ChromaDB collections (drawers + closets) over `chroma.sqlite3` + HNSW segments, a separate SQLite knowledge graph, `~/.mempalace/identity.txt` | One SQLite *file* (default `~/.mimir_well/mimir_well.db`): 11 tables + 3 FTS5 virtual tables (schema.py) |
| Entry points | CLIs `mempalace` + `mempalace-mcp`; `python -m mempalace` | Library only (`from mimir_well import RunaMemory`); Eye via `eye/__main__.py` / `start-eye.sh` |
| Test files | 67 `tests/test_*.py` (+ benchmarks/conftest; E-002's strict count 76 incl. all test-shaped files) | 28 `tests/test_*.py` |
| Suite this slice | **1669 passed, 90 failed, 39 errors, 1 skipped, 106 deselected** (§6) | **356 passed, 0 failed** (§6) |

## 2. What each one is, from its code

### mempalace — the palace

- **Shape of memory:** verbatim text filed as *drawers*
  under *rooms* under *wings*; *closets* hold AAAK
  compressed index lines that point at drawers
  (`palace.py`, `dialect.py` — AAAK is a dense shorthand
  an LLM can scan, per MISSION.md). Nothing is
  summarised away at write time; the drawer keeps the
  original words.
- **Getting things in:** miners, not single writes —
  `miner.py` (projects), `convo_miner.py`
  (conversations), `convo_scanner.py`, `diary_ingest.py`,
  `project_scanner.py`, `sync.py`, plus shell hooks
  that mine transcripts around Claude Code compaction
  (`hooks/mempal_save_hook.sh`,
  `mempal_precompact_hook.sh`).
- **Getting things out:** `searcher.py` — hybrid
  retrieval (Chroma vector search + BM25 re-rank, with
  a BM25-only SQLite path), closet-guided expansion to
  neighbouring drawers; `layers.py` — the 4-layer
  wake-up stack (L0 identity ~100 tokens, L1 essential
  story ~500–800, L2 on-demand, L3 deep search;
  `MemoryStack`); a temporal **knowledge graph**
  (`knowledge_graph.py`: entities, triples,
  `invalidate()`, `as_of` queries, timeline) in its own
  SQLite file.
- **Faces:** a large CLI (init / mine / sweep / sync /
  search / compress / wake-up / split / hook /
  instructions / repair / migrate / status) and an MCP
  server (`mcp_server.py`, 2,333 lines, **30 `tool_*`
  functions**: search, drawers CRUD, taxonomy, tunnels
  between wings, KG query/add/invalidate/timeline,
  diary read/write, …).
- **Also in the member:** a benchmark suite with
  published-style result files (LongMemEval / LoCoMo /
  ConvoMem shapes under `benchmarks/`), a website, an
  OpenClaw integration skill, i18n in 12 languages, an
  entity detector/registry, a fact checker, a sweeper
  and a repair tool (its `repair.py` alone is 1,441
  lines, much of it Chroma/HNSW segment forensics —
  see `backends/chroma.py`).

### mimir-well — the well

- **Shape of memory:** one row per memory in `memories`
  (content, category, tags, importance 1–10,
  emotional valence, `memory_type`
  episodic/semantic/procedural/implicit, `user_id`
  namespacing defaulting to `'runa'`, temporal
  validity `valid_from`/`valid_until`, `is_current`,
  `superseded_by`), beside `knowledge`, `saga_events`,
  `entities`/`relationships`, `conversations`, an
  access log and an audit table (schema.py).
- **The class:** `RunaMemory` (`core.py`, 1,571 lines)
  — `add_memory`, `get_memory`, `search_memories`
  (FTS5), `update_memory`, `delete_memory`,
  conversations, knowledge add/search,
  `recall_by_importance` / `recall_recent` /
  `recall_by_mood`, `store_with_validity`,
  `supersede`, `recall_current`, `decay`,
  `consolidate`, `promote_to_knowledge`,
  `detect_contradictions`, integrity/repair, backups
  with rotation, JSON export, `health_check`,
  `get_stats`.
- **The living parts no archive has:** `decay.py`
  (Ebbinghaus decay + reinforcement boost + promotion
  confidence), `guard.py` (MemoryGuard: trust levels
  per source, pattern severity — writes are screened),
  `audit.py` (every mutation trailed), `budget.py`
  (TokenBudgeter: per-channel token budgets for
  context assembly), `context_engineer.py`
  (ContextEngineer builds the context block),
  `wyrd_graph.py` (WyrdGraph: strength-weighted edges
  over the *same* db file, traversal, relatedness),
  `migrations/` (versioned schema runner), and
  `eye/app.py` (the Mímir's Eye Flask dashboard,
  948 lines).
- **Retrieval is words, not vectors:** FTS5 full-text
  (`memories_fts`, `knowledge_fts`, `saga_events_fts`)
  plus structured recall (importance / recency /
  mood / validity). A tree-wide grep finds **no
  embedding or vector code anywhere in mimir-well**.

## 3. Overlap — where they genuinely do the same job

| Capability | mempalace | mimir-well |
|---|---|---|
| Store a memory, get it back by id | drawers + `tool_get_drawer` | `memories` + `get_memory` |
| Full-text search | BM25 leg of hybrid search; BM25-only fallback | FTS5 (`fts_search`, `search_memories`) |
| Knowledge graph | `KnowledgeGraph`: temporal triples, invalidate, as-of | `entities`/`relationships` + `WyrdGraph` edges on the same db |
| Conversations held | convo mining + diary read/write | `conversations` table, `save_conversation` |
| Layered context for wake-up | Layers 0–3 / `MemoryStack` (~600–900 token wake-up) | `ContextEngineer` + `TokenBudgeter` (channel budgets) |
| Self-repair | `repair.py`, `sweeper.py`, palace locks | `integrity_check` / `repair`, self-healing migrations |
| Backup / export | exporter, sync, migrate | `backup_to` / rotation / GitHub backup, `export_to_json` |
| Multi-user / separation | wings as separation (a wing per project/agent) | `user_id` column + isolation-tested namespacing (the T8 test family) |
| MCP face | Yes — its own MCP server | No |

Overlap is real but it is *shape* overlap, not code
overlap: the two share **zero code and zero storage
format** — a grep of each member for the other's name
returns nothing, and neither can read the other's
store. Any unification in Part V is a contract-and-
migration job (E-080/E-081), never a merge of files.

## 4. Uniqueness — what only one of them does

**Only mempalace:**
- Verbatim-first storage with mining pipelines for
  whole projects and whole conversation archives;
  nothing else in the tree ingests at that scale.
- Semantic (embedding) retrieval — the only vector
  memory among the two; hybrid vector+BM25 ranking.
- AAAK closets: a compressed index layer built for
  LLM scanning, with tunnels between wings and a
  palace graph (`palace_graph.py`).
- An MCP server as a first-class face (30 tools) and
  Claude Code hook integration — its consumers are
  *external agent harnesses*, not this repo.
- A benchmark estate (LongMemEval/LoCoMo/ConvoMem
  runners + result files) — evidence culture mimir
  does not have.
- The cost: ChromaDB + ONNX embedding model at
  runtime, a 59 MB tree, and a repair burden spent
  largely on vector-store segment health. On the
  roadmap's tiny-hardware profiles this is the heavy
  candidate by an order of magnitude (Part III will
  price it exactly; E-015/E-041 inherit this row).

**Only mimir-well:**
- Forgetting as a feature: Ebbinghaus decay,
  reinforcement, consolidation, promotion of memories
  into knowledge — a lifecycle, not just storage
  (Part V's E-082 consumes exactly this).
- Truth over time: temporal validity, supersession
  chains, contradiction detection, `recall_current`.
- Feeling as data: importance + emotional valence as
  first-class, queryable fields (`recall_by_mood`).
- Custody machinery: source-trust guard on writes,
  a full audit trail, per-user isolation *proven by a
  dedicated test family* (T8/T9 files are ~half its
  suite).
- Zero-dependency core: the whole engine is stdlib
  SQLite in one file — the toaster-shaped candidate.
- The cost: no semantic search at all (a paraphrase
  that shares no words with the memory is invisible
  to FTS5), no MCP face, no mining pipelines, no
  benchmarks.

**A third memory stands in the room:** the core's own
`src/ember/well/` — Brunnr (sqlite_vec + pgvector
adapters behind the `BrunnrHandle` protocol:
`add_document` / `add_chunks` / `add_episode` /
vector+text+hybrid search) fed by Smíðja (chunker,
embed client, journal). It is smaller than both,
already the companion's, and it is the incumbent
Part V must judge the two members against — E-077
maps it in the same depth.

## 5. Consumers — who actually uses either, in code

Proven by grep over `*.py` in `src/`, `tests/`, and
every other member (this slice):

- **Ember core (`src/ember/`, root `tests/`): NEITHER.**
  Zero imports, zero references (the only "Mimir"
  hits in root tests are Old Norse prose fixtures —
  "Mimir's well" the myth, not the member). Both
  members stand exactly as `docs/UNWIRED_INVENTORY.md`
  records: wired = no.
- **mempalace consumers in-tree: none.** Its real
  consumers are outside this repo by design — the
  Claude Code hooks and MCP clients its member ships
  for. Inside the tree it is referenced only in docs
  (the Yggdrasil design corpus designs a
  `MemPalaceBrunnr` adapter and a Bifröst routing
  weight of 1.5 for verbatim questions — design
  intent, no code; `docs/yggdrasil/siblings/
  19_SIBLING_MEMPALACE.md`).
- **mimir-well consumers in-tree: two, both
  shape-consumers, neither path-agreeing:**
  - *Verdandi's heartbeat* (`heartbeat/checks/
    mimir.py`): opens `~/.mimir_well/mimir_well.db`
    — **mimir-well's own default path** — checks
    integrity, counts `memories`/`knowledge`/
    `relationships`, watches size (warn 100 MB /
    critical 500 MB); Eir's heal action consumes its
    verdict. This consumer agrees with the member.
  - *bifrost's memory bridge* (`bifrost/src/bifrost/
    bridges/memory_bridge.py`): reads and writes the
    `memories` + `memories_fts` tables directly by
    SQL (its own category mapping, INSERT of 5
    columns) — but at **its own default path,
    `~/.hermes/memory/runa_memory.db`**, which is
    *not* mimir-well's default. A store written by
    `RunaMemory` at its default is invisible to
    bifrost, and bifrost's store is invisible to
    `RunaMemory` at its default; they meet only if an
    operator points both at the same file.
  - A third path claimant: mimir-well's own Eye
    (`eye/app.py`) defaults its `DB_PATH` to that
    same `~/.hermes/memory/runa_memory.db` (env
    `MIMIR_DB_PATH` overrides) — the member's
    dashboard and the member's library disagree
    about where the well is, out of the box.
    (→ docket 51.)
- **Design-corpus consumers (intent, not code):** the
  Yggdrasil corpus seats both — Mímir as "the well at
  the tree's root" and MemPalace as "alt/complement"
  for verbatim recall (`docs/yggdrasil/INDEX.md`;
  sibling docs 12 + 19) — and the code-harvest doc
  names mimir-well "the durable long-term memory
  layer… one of the most important repos in the
  account". None of it is wired; all of it is Part V
  evidence, none of it is a verdict.
- **Stale inventory line:** `docs/UNWIRED_INVENTORY.md`
  calls mempalace "(README is scam-warning only —
  content unclear)… Likely abandoned or archival."
  Measured reality (§1–§2, §6: v3.3.5, 25k lines,
  1,669 passing tests this slice) contradicts
  "abandoned" outright. The inventory predates the
  import's measurement; its *wired = no* fact stands,
  its characterisation does not. (→ docket 52.)

## 6. Test state — fresh this slice

Method: each member's own suite in its own shape
(E-005 method), declared deps from the isolated
target dir, proxy env cleaned (E-005's proven
environment signature), VM profile.

- **mimir-well: 356 passed, 0 failed** (38.7s) — the
  member's whole suite green with flask supplied.
  Delta vs E-005 (350 passed / 6 failed): the 6 were
  docket item 10, the Eye-fixture family (fixture
  sets `DB_PATH`; the app binds `MIMIR_DB_PATH` /
  its `~/.hermes` default at import). **No code has
  changed since E-005** — the pass here is
  environment-shaped (this VM carries a real
  `~/.hermes` tree and `~/.mimir_well` state for the
  defaults to land on), not a fix. Item 10 stays open
  exactly as classified: machine-coupled. (→ docket
  53.)
- **mempalace: 1669 passed, 90 failed, 1 skipped,
  39 errors, 106 deselected** (293.0s; benchmark /
  slow / stress markers deselected by its own
  config). Failure and error totals are **identical
  to E-005** (90 / 39 — the proven environment bulk
  plus the STALE `.claude-plugin/` family, item 12,
  plus E-005's small unresolved residue); passed is
  **+72 vs E-005's 1597** with the same 106
  deselected — a collection delta this slice records
  as UNRESOLVED rather than explaining away (runner
  version and proxy-clean env from the start are the
  candidate causes; E-077 re-measures in depth).
  (→ docket 54.)
- Default-env shape unchanged from E-005: mempalace
  cannot even collect without chromadb (its conftest
  imports it unguarded — a *declared core* dep, so a
  shape fact, not a guard defect; E-005's wording
  stands). mimir-well's core needs nothing; only its
  Eye tests need flask.

## 7. What the later slices inherit

- **E-013** (config & secrets census): the two
  config shapes — mempalace `~/.mempalace/config.json`
  + env (`MEMPALACE_*`, palace path) vs mimir-well
  `~/.mimir_well/mimir-well-config.json` + env
  (`MIMIR_DB_PATH`, `MIMIR_BACKUP_REPO`) — and the
  three-path disagreement (docket 51) as a known
  shape collision.
- **E-014** (dead/duplicate census): §3's shape
  overlap (graph, conversations, repair, export in
  both) is duplication *of capability across
  members*, with zero shared code — classify it as
  such, not as dead code.
- **E-015** (budget archaeology): mempalace's
  published-style recall claims live in its benchmark
  docs/results (the 96.6% R@5 figure the Yggdrasil
  corpus repeats); mimir-well's size claims live in
  Verdandi's thresholds (100/500 MB). Both are
  claims to test or strike there.
- **E-016** (docket): items 51–54 below.
- **E-077/E-078** (Part V opening): §2 + §4 are the
  map both systems are judged from; the comparison
  harness must include the Brunnr incumbent (§4) or
  it answers the wrong question; workloads must
  cover what each is *unique* at (verbatim mining +
  paraphrase recall vs decay/validity/mood recall),
  not only the overlap.
- **E-085** (memory ↔ Verdandi): the one live
  in-tree consumer relationship is Verdandi ↔
  mimir-well's file (§5) — reconcile there first.

## Carried to the E-016 docket

(51) "The Mímir DB" has three default paths and the
claimants disagree: mimir-well's library defaults to
`~/.mimir_well/mimir_well.db` (`config.py`), its own
Eye defaults to `~/.hermes/memory/runa_memory.db`
(`eye/app.py`, env `MIMIR_DB_PATH`), and bifrost's
bridge defaults to that same Hermes path while
speaking the library's table shape. Verdandi's check
alone follows the library. Stores at different
defaults are mutually invisible. One canonical
default (or an explicit, documented divergence) is
undecided and unbuilt; assigned to Part V
(E-077/E-080), with Parts IV/VIII consulted.
(52) `docs/UNWIRED_INVENTORY.md`'s mempalace line
("content unclear… likely abandoned or archival") is
proven stale by this census (v3.3.5, actively
testable, 1,669 passing). The wired = no fact is
correct and stays; the characterisation must be
corrected where the inventory is next truthfully
updated (E-018 gate / E-091 residue), never silently.
(53) Docket item 10 (mimir-well Eye fixture sets
`DB_PATH` while the app binds `MIMIR_DB_PATH` at
import over `~/.hermes` defaults) re-observed: the
6 tests pass on this VM with no code change, because
the machine now carries the Hermes-shaped state the
fixture accidentally relies on. Machine-coupling
stands as the classification; a pass on a coupled
machine is not a repair. Stays assigned as item 10
was (Part V / member hygiene at E-077's mapping).
(54) mempalace collection delta: +72 passed vs
E-005 at identical failure/error/deselection totals
(90 / 39 / 106). Cause unresolved in this slice
(runner version vs from-the-start cleaned proxy env
are candidates). E-077 re-measures both suites in
depth and either explains the delta or carries it
as a standing uncertainty in Part V's evidence.

## Slice gate

Root suite re-run in the E-001 shape (pgvector file
excluded, default env) as this slice's no-change
gate — see CAMPAIGN_STATE.md for the count. Both
members' own suites re-run this slice as census
evidence (§6). Doc-only slice: no code touched, no
README touched, no push.

*Filed by the E-012 slice, 2026-10-31. Next: E-013 —
config & secrets census.*
