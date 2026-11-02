# E-081 — Migration: Survivors Stay Native; the Palace Answer

*Part V (Memory: Two Systems, One Verdict), fifth slice.
Roadmap line: "Migration: existing stores of the losing
shape migrate losslessly (fixtures on synthetic stores) —
or are read-compat forever, per the verdict."
E-079's verdict (§5.2, §8) narrowed the question before
this slice opened: **no shape migration between the
survivors is ordered** — Brunnr's and mimir-well's stores
stay native behind the E-080 face. The only "losing
shape" is mempalace's, and its answer (migrate vs
read-compat) is argued here from fixtures and, where it
involves retirement, **executed only under Volmarr's
word — which has not been given. This slice therefore
proves the survivors' half outright and files the palace
argument; the migration itself is not executed, no real
palace was opened, and the mempalace member is
untouched.**

## 1. Plain-language summary — the answer

- **The survivors need no migration at all, and this
  slice proves it.** Stores written the old way — by
  mimir-well's and Brunnr's own APIs, before the face
  existed — are served whole by the one face, and
  serving them changes neither store's shape nor a
  single content row (§2). The stores stay native
  behind the face, forever, by design: there is nothing
  to move because the face speaks both native shapes.
- **For a palace, the answer is migrate — one-way, once,
  when (and only if) Volmarr rules retirement.** The
  fixture proof (§4) shows every drawer carries
  losslessly into the bounded shape: its text as a
  Brunnr chunk, every scrap of its filing metadata in
  the Brunnr document's own metadata, the original
  drawer reconstructable exactly from what landed.
  Knowledge-graph triples carry into living-fact records
  with their validity and confidence intact. Closets
  and embeddings are derived indexes, not records —
  they are rebuilt at the destination, never carried.
- **Read-compat forever is refused** (§5): it would tax
  every future version of the companion with a second
  memory shape to read a store nothing writes any more,
  and actually *searching* a palace read-compatibly
  needs the very ~185 MB dependency stack the verdict
  disqualified. The one honest use of read-compat — a
  stdlib-only reader — is exactly what the migration
  itself uses, once.
- **Nothing here executes.** If Volmarr declines
  retirement, the fallback stands (§6): palaces stay
  with the member, untouched, and this same mapping is
  available as a user's own one-way export. Silence is
  never read as a retirement word.

## 2. Survivors — stay native, proven

Fixture (conformance test
`test_survivor_stores_stay_native_behind_the_face`):
both stores are written **the pre-face way** — facts
(including a supersession) through `RunaMemory`
directly, a document + chunk + an episode through the
Brunnr handle directly — then snapshotted (full
`sqlite_master` schema + per-table row counts), then
opened through `MemoryFace` over the same files
(toaster profile) and served: word recall, the
current-truth view, document search, recent turns.

Result: **everything written is served whole** — the
current fact and the preference fact, never the
superseded text; the document's chunk by word search;
the episode to the default persona — and afterwards:

- both stores' **schemas are byte-identical** to the
  snapshot;
- **every content table's row count is identical**
  (facts, knowledge, documents, chunks, episodes, all);
- Brunnr's store shows **zero count deltas of any
  kind**.

The only deltas anywhere are mimir-well's own native
behaviour, named so no one mistakes them for migration:
its **read audit log** (`memory_access_log`, +2 — the
member's audit trail recording this test's two recalls;
the audit doing its job is E-077 §4.2's territory
working as designed), and the **FTS5 shadow tables**
(`memories_fts_data` / `memories_fts_idx`), whose
internal segment rows compact when the member reopens
its store — the FTS content table itself is unchanged,
and no fact row moved. A face that migrated would have
changed content rows or schema. This one changed
neither. **Stay native is not a hope; it is measured.**

## 3. The palace's anatomy — what a migration must answer

From the member's own code (E-077 §4.1 in depth; paths
checked again this slice):

- **One ChromaDB palace directory** (default
  `~/.mempalace/palace`): `chroma.sqlite3` holding an
  `embeddings` + `embedding_metadata` pair of tables,
  plus HNSW segment files. Two collections live in it:
  `mempalace_drawers` (the records) and
  `mempalace_closets` (the index layer).
- **A drawer** is one verbatim chunk of text (≤800
  chars, mined; one-per-day for diaries) with metadata:
  `wing`, `room`, `source_file`, `chunk_index`,
  `added_by`, `filed_at`, `normalize_version`, `hall`,
  optional `source_mtime` / `entities` / `source_session`.
  Its id is its provenance: `drawer_{wing}_{room}_{sha}`.
- **A closet** is packed pointer lines,
  `topic|entities|→drawer_ids`, built *from drawer
  content* by `palace.py`'s `build_closet_lines`
  (proper-noun extraction over the text) — a precomputed
  index, ≤1500 chars per closet.
- **A knowledge graph** sits beside the palace as plain
  SQLite (`knowledge_graph.sqlite3`): `entities` and
  `triples` (subject, predicate, object, `valid_from`,
  `valid_to`, `confidence`, `source_closet`,
  `source_file`, `source_drawer_id`, `adapter_name`,
  `extracted_at`). An entity-registry JSON stands
  beside that.

So a palace is **three content classes** (drawers,
triples, entities) and **two derived layers** (closets,
embeddings). The mapping answers each class separately.

## 4. The mapping — argued from fixtures, lossless where it must be

The fixture palace is synthetic (E-089: canon-flavoured
harbour letters only) and built in the exact shape the
member's own reader reads — because the reader *is* the
contract: `mempalace/mempalace/migrate.py`'s
**`extract_drawers_from_sqlite`** reads any palace's
`chroma.sqlite3` with **sqlite3 alone** (its imports are
stdlib only), returning every record's id, document,
and typed metadata. The conformance tests extract the
fixture palace with that very function — loaded from
the member file, ChromaDB never installed — and then:

| Palace class | Destination | Lossless? |
|---|---|---|
| Drawer (text) | Brunnr chunk under its own document, text byte-identical | **Yes — round-trip exact** |
| Drawer (all metadata + id) | The document's `metadata` mapping (the sqlite_vec adapter persists it as JSON) + `source` ← `source_file`, `hash` ← drawer id | **Yes — the original drawer record reconstructs exactly from the stored document** |
| Diary drawer | The same drawer mapping (it is a drawer whose wing is `diary`) — a day *document*, honestly **not** an episode: a diary page is not a conversation turn, and the mapping does not pretend otherwise | Yes, as a document |
| Knowledge-graph triple | One living-fact record: content rendered `subject predicate object`; `valid_from` / `valid_to` / `confidence` / provenance carried as record fields | **Yes — field-for-field round-trip** |
| Entity registry | Carried as records beside the triples (names/types are KG `entities` rows' content) | Yes, as records |
| Closets | **Not carried** — rebuilt at the destination by Brunnr's own word/meaning search over the migrated chunks | Derived: the fixture proves every closet pointer resolves to an extracted drawer, and a closet's payload is only topics/entities extracted from drawer text + those pointers — no user-authored content lives only in a closet |
| Stored embeddings | **Not carried** — re-embedded at the destination under the face's embedder rule, or word-only where the profile says so (E-080) | Derived from text by definition |

The round-trips are not paper claims: the fixture's
mapped drawers are written into a **real Brunnr store
through the face** and read back from the store, and
the original drawer records reconstruct exactly from
what the store returns (provenance survived the real
destination, not just the mapper's dictionaries).

**Priced** (E-078/E-080 numbers, per profile): one
migrated drawer = one Brunnr chunk — **585 B** priced
as episode-shaped growth, or **72,239 B** if embedded
for meaning search (the E-078 embedded-chunk price);
one migrated triple = one mimir-well fact at
**745 B/item**. A palace of 10,000 drawers migrates to
≈5.9 MB word-only, ≈722 MB embedded — which is why the
executing migration follows the face's own per-profile
index rule (the toaster migrates word-only and says so,
exactly as E-080 already does for living facts).

**One honest gap, named:** the face's `remember_fact`
today carries no `confidence` or validity-window
fields, so the triple half of an executing migration
writes through `RunaMemory` directly (the member's own
API, which holds those fields) or the face grows them
first — the executing slice chooses, with E-083's
persona work in view. The fixture proves the *record*
mapping is lossless; it does not pretend the current
face signature already carries every field.

## 5. Two fixture findings the executing slice inherits

1. **The member's extractor is collection-blind.**
   `extract_drawers_from_sqlite` joins `embeddings` ⋈
   `embedding_metadata` with no collection filter, so it
   returns **closets among the drawers** (proven: the
   fixture's closet comes back in the same list). Any
   executing reader must classify by id —
   `drawer_` / `closet_` — as this slice's reference
   mapper does, or it will migrate its own index as if
   it were memory. (Upstream's own `migrate()` has the
   same blindness and re-imports drawers only; closets
   and the knowledge graph are outside it entirely —
   another reason the executing migration is Ember's
   own tool, not an upstream command.)
2. **A palace can be read with the standard library
   alone.** No ChromaDB, no model, no ~185 MB stack is
   needed to *read* a palace — only to search it the
   palace's own way. This is what makes a one-time
   migration cheap and what makes read-compat-forever
   indefensible as the *search* story: read-compat
   search would drag the disqualified stack behind it
   forever to serve a store nothing writes.

## 6. Why not read-compat forever — and the fallback

Read-compat forever means: every future companion
carries palace-shape reading code, a second set of
search semantics, and (for meaning search) the
ChromaDB stack, permanently, for archives that stop
growing the day the verdict lands. On the project's
own budget law that is a forever tax on the smallest
machines to avoid a one-time, stdlib-priced, provably
lossless move. **Refused as the standing answer.**

The fallback if Volmarr declines retirement is
unchanged from E-079 §6 and fully compatible with this
answer: mempalace stays in the tree as an optional,
non-default, never-bundled laptop-class adapter; users'
palaces stay where they are; and this mapping remains
available as a **user-chosen, one-way export** into the
bounded shape whenever a user asks for it — nothing
automatic, nothing silent. If he rules retirement, the
executing slice (charged at E-091/E-092's line) runs:
stdlib extract → classify → map → write through the
face / `RunaMemory` → verify counts and round-trips
against the palace → the palace directory itself left
untouched on the user's disk until the user removes
it. Migration copies; it never deletes.

## 7. What this slice does NOT claim

- **Not executed.** No migration ran on any real
  store; no real palace was opened; the core gained no
  mempalace reader (pinned by conformance — the mapping
  lives in this slice's tests as the argument's
  reference implementation, to be promoted to a tool
  only by the executing slice under Volmarr's word).
- **The fixture's chroma shape is the reader's shape.**
  Real palaces also carry HNSW segment files and
  version-specific extras the migration ignores *by
  design* (they are derived indexes). A palace whose
  `chroma.sqlite3` the member's own reader cannot read
  is outside this answer until a fixture proves
  otherwise.
- **No archive-scale truth.** The fixture palace holds
  3 drawers, 1 closet, 2 triples. Behaviour at 10⁴–10⁵
  drawers is the executing slice's verification duty,
  with E-088's soak as its neighbour.
- **No device truth.** All runs are the campaign VM.

## 8. Assignments this answer makes

- **The executing migration slice** (only under
  Volmarr's retirement ruling; recorded at E-092):
  promote §4's mapping to a tool, classify-by-id per
  §5.1, verify at archive scale, leave source palaces
  untouched.
- **E-082** — lifecycle, unaffected: the survivors'
  stores it governs are the native ones §2 proved.
- **E-091** — the residue: whichever way the ruling
  lands, mark the palace's docs with this answer's
  outcome (migrated-by-tool, or bounded with export).
- **E-092** — the gate: this answer + Volmarr's word
  (or its recorded absence, fallback in force) on
  record; migration *proven on fixtures* is this
  slice's delivery toward the gate's "migration
  proven" line, with execution expressly ruling-gated.

## Slice gate

Conformance: `tests/unit/test_memory_migration_e081.py`
— survivors-native proof, palace extraction by the
member's own stdlib reader, collection-blindness
finding, lossless drawer round-trip (mapper-level and
through a real Brunnr store via the face), closet
derivation audit, triple mapping, and the filing pins
(member untouched; no mempalace reader shipped in the
core). Root-suite gate runs recorded in
CAMPAIGN_STATE at banking. No README touched; no
member code touched.

*Filed by the E-081 slice, 2026-11-01. Next: E-082 —
memory lifecycle: growth, decay, pruning under Part
III's storage budget, on the native stores this slice
proved stay native.*
