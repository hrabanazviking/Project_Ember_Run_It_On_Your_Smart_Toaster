# E-078 — The Comparison Harness: Identical Workloads, Three Systems

*Part V (Memory: Two Systems, One Verdict), second slice.
Roadmap line: "The comparison harness: identical workloads
through both (recall, latency, size, budget per profile)."
E-077 proved the question is three-way, so the harness runs
**three** systems — mempalace, mimir-well, and the core's
Brunnr — through one synthetic corpus, one query set, and
one measuring method. The harness is in the tree and
re-runnable: `scripts/dev/compare_memory_systems.py`.
Method and every number below are from its canonical run
(run 2) on the campaign VM, Python 3.12.3, at starting HEAD
2e5d6bb (E-078 in progress); raw reports in
`~/workspace/.verify-tmp/ember-e078/` (`report2.json` +
per-system fragments; run 1 preserved for the as-found
mimir-well numbers of §3). Load during the runs was
1-minute ~5–7 (sibling campaigns) — latency medians are
VM-contended and comparative, never device claims.*

## 1. Plain-language summary

**All three systems remember the words perfectly; they
differ in what else they can do, what they weigh, and how
fast they answer.**

- Asked for an exact phrase or for distinctive words,
  every system found every memory: **20 of 20, all three**
  (mimir-well only after this slice repaired it — §3).
- Asked a *reworded* question — the way a person actually
  asks — the two meaning-based systems answered **9 of 9**
  (mempalace) and **9 of 9 / 8 of 9** (Brunnr, pure-vector /
  hybrid), and mimir-well answered **0 of 9**, because it
  has no meaning search at all. That absence is now a
  measured number, not an impression.
- Only mimir-well could answer the living questions:
  *what matters most* (importance recall, exact), *what
  felt joyful* (mood recall, exact), and *what is true
  now* — after a fact was superseded, its current-truth
  recall returned the new fact and not the old one. Asked
  the same changed-fact question, both other systems
  returned the old and new versions together, old first:
  neither can tell current truth from stale truth at this
  layer.
- Only Brunnr holds conversation turns as turns: its
  episode recall returned exactly the last five of twelve
  stored turns, in chronological order.
- On weight, the spread is enormous. mimir-well's whole
  measured shape fits **every** profile in the budget
  book, the toaster included. Brunnr's store fits, but
  embedded-chunk growth is vector-priced (see §5's
  caveat). mempalace fits **no** profile as it stands:
  ~403 MiB of process RAM at work, and an install story
  measured in hundreds of megabytes once its required
  dependencies are counted — its own Python package is
  only ~1 MiB; the weight is ChromaDB/ONNX and the model.
- On speed, word-search is effectively instant in
  mimir-well and Brunnr (medians 0.1–0.17 ms) and three
  orders of magnitude slower in mempalace (~650–800 ms),
  whose every search pays an in-process embedding first.
  Meaning-search latency in both semantic systems is
  embedder latency (~1.0–1.25 s medians here, contended).

**And the harness found a real bug before it measured
anything fair:** mimir-well's full-text search was blind
to everything written during the running session (§3,
docket 111). It is fixed in this slice — the member's
first change since its import.

## 2. The harness and the workload

- **One corpus, synthetic only** (E-089's law applied
  early): 20 invented, canon-flavoured facts (a ferry, a
  beekeeper, a healer's fever brew…), each with a unique
  marker word, an exact phrase, three distinctive words,
  and — for 9 of them — a reworded question sharing no
  content word with the stored text. Plus one changed
  fact in two versions (the winter market's opening day)
  and 12 synthetic conversation turns for Brunnr's
  episode row.
- **Identical inputs, native faces.** The same query
  strings go to each system's own search: mempalace's
  `search_memories`, mimir-well's `fts_search` (and its
  LIKE-shaped `search_memories` for contrast), Brunnr's
  `text_search` / `vector_search` / `hybrid_search`.
  A hit = the target's marker word in a top-5 result.
  Each query runs twice; the median is kept. Each system
  runs in its own subprocess, so the peak RSS on record
  is its own.
- **The embedder is held constant, and the report says
  so.** mempalace embeds natively (ONNX all-MiniLM-L6-v2,
  384-dim). Brunnr's production embedder is an external
  Ollama service, and no Ollama is reachable on this VM
  (probed: connection refused on 127.0.0.1:11434), so the
  harness embeds Brunnr's chunks with the *same* ONNX
  model. What is compared is stores and retrieval given
  identical vectors — not two embedding services.
- **Sizes are priced as stores lie on disk after close**
  (WAL checkpointed). The harness's first run priced
  mimir-well's live WAL instead and produced a nonsense
  120 KB/item; the method was corrected and the run
  redone. Growth is (final − empty) over the 22 stored
  items, projected to the budget book's 600-item
  reference month only as a stated projection.
- **RAM judging follows E-041's law** (the model is not
  Ember's cost): mimir-well and mempalace are judged on
  their own process peaks (their machinery is in-process);
  Brunnr is judged on its store-open RSS (33.2 MiB), with
  the harness embedder's peak (438,400 KiB ≈ 428 MiB)
  reported beside it, never charged to Brunnr.
- Docket 54's discipline is honoured: TMPDIR pinned to a
  short workspace path, proxy variables stripped in the
  children (E-005's ChromaDB signature), runner and
  versions stated above.

## 3. The discovered defect — docket 111, fixed in scope

**mimir-well's `fts_search` could not see anything
written since the store was opened.** As found (harness
run 1, pre-fix): verbatim-phrase FTS **0/20**, term FTS
**0/20** — while the LIKE-shaped search on the same data
scored 20/20, isolating the fault to the FTS index.

Root cause, proven at the SQLite level: the three FTS5
tables are *external-content* (`content=memories` etc.),
whose indexes SQLite does **not** maintain automatically;
`schema.py` stated the opposite as a comment ("FTS5
auto-syncs… No triggers are needed") and no sync
triggers existed. The index was populated only by the
rebuild `RunaMemory._init_db` runs at open — so FTS knew
yesterday's memories and none of today's. The member's
own test suite knew: `test_t8_2_read_isolation.py`
carries the workaround and the note "triggers should be
added in a future migration". Part I's census missed it
because the member's tests rebuild by hand.

The fix (the member's first change since its import
commit 911eeba, 2026-05-21):

- `schema.py`: the false comment corrected and replaced
  by `FTS_TRIGGERS` — the standard external-content
  trigger set (insert / delete / update) for all three
  FTS tables, created `IF NOT EXISTS`.
- `core.py`: `_init_db` executes the triggers after the
  FTS tables, before the open-time rebuild — so existing
  stores gain sync at their next open and the rebuild
  heals their index once. No table shape changes;
  `SCHEMA_VERSION` stays 9.
- `mimir-well/tests/test_fts_sync.py`: six regression
  tests pin in-session sync (insert / update / delete,
  all three tables, trigger presence), no manual rebuild
  anywhere.
- Consequences pinned elsewhere: E-077's tracked-size
  pin for mimir-well moves under attribution in
  `test_memory_map_e077.py` (58 files / 607,675 B →
  **59 files / 614,283 B**); mempalace's pin is unmoved.
  The E-057 member budget table is re-measured under
  the same attribution in both published copies
  (`docs/BUDGET_BOOK.md` §7 and the E-057 record):
  mimir-well's row and the twelve-member total
  (131,443,689 → **131,450,297 B**); Verdandi's laptop
  miss is unchanged. Historical records (E-002 census,
  E-043, E-076 gate) keep their then-true figures.

Re-measured after the fix (canonical run): verbatim FTS
**20/20**, term FTS **20/20**. The member's full suite
re-run this slice: see §7.

## 4. Recall — the measured table (canonical run)

| Workload | mempalace | mimir-well | Brunnr |
|---|---|---|---|
| Verbatim phrase | **20/20** (`search_memories`) | **20/20** FTS (as found: 0/20); 20/20 LIKE | **20/20** text; 20/20 vector |
| Distinctive terms (FTS) | **20/20** | **20/20** FTS (as found: 0/20) | **20/20** text; 20/20 hybrid |
| Paraphrase (reworded) | **9/9** | **0/9** — no semantic search; a measured absence | **9/9** vector; **8/9** hybrid |
| Importance recall (≥9) | no such face | **exact** (5/5, none extra) | no such face |
| Mood recall (valence 0.8±0.3) | no such face | **exact** (6/6, none extra) | no such face |
| Current truth after supersession | old **and** new in top-5, **old first** | `recall_current`: **new present, old absent**; raw FTS still finds the old text (index ≠ truth view) | old **and** new in top-5, **old first** |
| Episode recall (last 5 of 12) | no such face | no such face | **exact set**, chronological order |

Notes on the rows:

- The paraphrase hybrid miss (8/9) is RRF fusion noise at
  corpus scale: the pure-vector row found all nine. One
  run-1 repetition of the same row also scored 8/9; the
  pure-vector row scored 9/9 in both runs.
- The mood row's ground truth is computed in the same
  float arithmetic the SQL uses: the item at valence
  exactly 0.5 sits at distance 0.30000000000000004 from
  the 0.8 target and is outside the ±0.3 band on both
  sides of the comparison — a boundary fact, recorded,
  not a miss.
- mempalace's knowledge graph *does* have temporal
  triples (E-077 §4.1); the current-truth row judges the
  drawer layer, which is where its searched memory
  lives. The distinction matters for E-079/E-080.

## 5. Latency, size, and budget fit (canonical run)

Medians per query (VM, contended — comparative only):

| | mempalace | mimir-well | Brunnr |
|---|---|---|---|
| Add one item | 487.5 ms (embedding incl.) | 54.0 ms (guard + audit + FULL sync) | 1.5 ms per chunk (embedding excluded — precomputed in batch) |
| Verbatim search | 799.4 ms | 0.159 ms FTS / 0.043 ms LIKE | 0.167 ms text / 1,040 ms vector |
| Term search | 645.4 ms | 0.100 ms FTS | 0.113 ms text / 1,076 ms hybrid |
| Paraphrase search | 602.4 ms | 0.054 ms (and finds nothing) | 1,162 ms vector / 1,252 ms hybrid |

The pattern is plain: wherever a search embeds first,
the embedder is the latency; wherever it does not, the
store answers in well under a millisecond at this scale.
mempalace pays the embedding on *every* search, even
exact-phrase ones — its "text" speed is its semantic
speed. mimir-well's 54 ms write is the dearest write of
the three (guard screening, audit trail, synchronous
FULL), still trivially affordable at companion scale.

Store growth (after close, 22 items stored):

| | empty store | after corpus | per item | 600-item projection |
|---|---|---|---|---|
| mimir-well | 237,568 B | 253,952 B | **745 B** | 446,836 B (0.43 MiB) |
| Brunnr | 81,920 B | 1,671,168 B | **72,239 B** | 43,343,127 B (41.3 MiB) |
| mempalace | 188,416 B | 446,628 B | **11,737 B** | 7,042,145 B (6.7 MiB) |

- **Brunnr's per-item figure prices embedded chunks** —
  a 384-float vector per chunk in the vec0 store (the
  production shape is 768 floats, ~twice the vector
  bytes). It is *not* the companion's per-turn cost:
  episodes (text only) measured **585 B/episode**
  steady-state at E-050, and that figure stands. The
  honest reading: Brunnr is cheap for turns, dear for
  embedded document ingest, at exactly the vector's
  price.
- mempalace's per-item figure is fixed-cost dominated at
  22 drawers (HNSW segments + Chroma's SQLite); it is
  the measured truth at this scale, not a projection of
  its cost at archive scale.

Budget fit (`ember.budgets`, E-041's book; install =
tracked code bytes; RAM per §2's basis; growth = the
600-item projection):

| System | Install | RAM judged | Toaster | Phone | Pi | Laptop |
|---|---|---|---|---|---|---|
| mimir-well | 614,283 B (post-fix) | 24.2 MiB peak | **fits all** | fits all | fits all | fits all |
| Brunnr | 831,124 B (`src/ember`) | 33.2 MiB store-open | install ✓, RAM ✓, growth ✗ (embedded chunks) | same | same | **fits all** |
| mempalace | 59,049,715 B member; ~1,012,495 B package **+ ~185 MB deps + ~88 MB model** (see below) | 402.8 MiB peak | ✗ install, ✗ RAM, ✗ growth | ✗ install, ✗ RAM | ✗ install, ✗ RAM | ✗ install, ✗ RAM |

mempalace's install story, itemised so E-079 argues from
evidence: the member as imported weighs 59,049,715 B
(benchmarks, results and test data included); the
importable package alone is 72 files / 1,012,495 B; the
dependencies its search cannot run without, byte-summed
in this slice's isolated extras target — chromadb
5,434,506 B, chromadb_rust_bindings 58,976,393 B,
onnxruntime 68,664,217 B, numpy 40,748,295 B,
tokenizers 11,610,824 B ≈ **185 MB** — plus the ONNX
model cache at ~88 MB on this machine. Against the
book's largest install ceiling (laptop, 16 MiB), the
package alone would fit and nothing else about it does.
Its 402.8 MiB working peak likewise exceeds every
profile's turn ceiling (toaster 64 / phone 128 / pi 192
/ laptop 384 MiB).

## 6. What this slice did NOT prove

- No device numbers: every figure is the campaign VM
  under sibling load. Tiny-hardware truth for any
  survivor is later parts' device work, not this table.
- No archive-scale behaviour: 22 items is a harness
  corpus, not a palace of years. Growth and latency at
  10⁴–10⁵ items are E-088's soak territory.
- Brunnr with its *production* embedder (Ollama,
  768-dim) is unmeasured here — unreachable from this
  VM; the harness held the embedder constant instead
  and said so. The Pi proofs (E-047/E-049) measured the
  real embedder path for turns, not for this corpus.
- mempalace's closets layer was not built by the
  harness (drawers filed directly, the shape its own
  test fixtures use); closet boost could only improve
  its recall rows, which are already perfect — its
  costs, not its recall, are its problem.

## 7. Test state

- Harness: canonical run 2, all three children `ok`,
  report + fragments in
  `~/workspace/.verify-tmp/ember-e078/` (run 1 and the
  as-found mimir fragment preserved beside it).
- mimir-well full suite, post-fix (overlay TMPDIR):
  **353 passed, 9 failed** in 839s. Six of the nine are
  docket 10's Eye family, identical to the
  E-005/E-012/E-077 baseline (350 passed / 6 failed;
  the +6 passes and +3 failures against that baseline
  are accounted for next). The other three are
  `test_recall_quality.py`'s hard wall-clock latency
  tests (<50 ms / <20 ms) — **proven environment, not
  the fix**, three ways: (1) the operations they time
  (LIKE `search_memories`, `recall_current`,
  `recall_by_importance`) never touch FTS, and their
  seeding finishes before the timers start; (2) an A/B
  on tmpfs prices the triggers' true cost at ~0.8 ms
  per add (1.0 vs 0.2 ms/add over 200 adds); (3) the
  same file with `TMPDIR=/tmp` runs **21 passed in
  3.01s**, matching E-077's calm-window shape (21
  passed, 2.44s) — the overlay's fsync cost under
  mimir-well's `synchronous=FULL` is what starved them,
  the disk sibling of E-077's contention class. The
  six `test_fts_sync.py` tests pass in every shape
  (isolated overlay run: 24 passed / the same 3 latency
  failures; tmpfs run of the recall file: all green).
- Root conformance: `tests/unit/test_memory_comparison_e078.py`
  pins this doc, the harness, the corpus, and the
  member's trigger set. Slice gate (Runs A/B/D) recorded
  in CAMPAIGN_STATE at banking.

**E-079 next** — the verdict paper, argued from these
numbers + ORIGINS provenance.
