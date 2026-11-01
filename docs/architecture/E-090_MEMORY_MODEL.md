# E-090 — The Memory Model: for Users (Plain) and for Builders

*Part V (Memory: Two Systems, One Verdict), slice E-090.
Roadmap line: "Docs: the memory model for users (plain) +
builders." The model this document describes lives at
`src/ember/well/memory_face.py` (`MemoryFace`, E-080) and
was built slice by slice across E-080–E-089; the
conformance battery for this filing is
`tests/unit/test_memory_model_docs_e090.py`, which pins
this document against the code — every public operation
named below is checked to exist on the face, and every
price and constant is checked against the module that
owns it. Where this document and the code ever disagree,
the code and its batteries are the truth and this
document is the defect.*

---

# Part A — For users, in plain words

## A1. What your companion remembers

Your companion remembers three kinds of things, and
only three:

| Kind | What it is | An example |
|---|---|---|
| **Living facts** | Things that are true about your world, which can change — and when they change, the new version replaces the old as "what is true now", while the old version is kept as history you can look at. | "The beekeeper trades honey at the winter market." |
| **Conversation turns** | The chats themselves: what you said, and what the companion replied, in order. | Yesterday's conversation, there to be picked up again. |
| **Documents** | Longer writings you or the companion added as documents, kept whole and searchable. Documents are *shared grounding*: they belong to the companion's library, not to one person's private memory (see A5). | A letter, a set of notes, a reference text. |

That is the whole list. There is no fourth, hidden kind
of memory, and nothing is remembered anywhere else
behind your back: §A8 states the two neighbouring
records that are *not* this memory (the session diary
and the wider WYRD shapes) and exactly how they touch
it.

## A2. How the companion finds a memory again

Two ways, and the companion always says which one it
used:

- **By words.** It looks for the actual words you asked
  about. Fast, tiny, and available on every machine,
  including the smallest.
- **By meaning.** It can also find a fact when you ask
  in *different words* — "when does the boat carry post
  between the isles?" finds the fact about the harbour
  ferry. This costs much more room (a found-by-meaning
  fact costs 72,239 bytes of index, against 745 bytes
  for the fact itself), so it is **on by default only on
  phone, pi, and laptop machines. On the smallest
  profile — the toaster — it is off, and a meaning
  question is answered by word search, with the answer
  honestly labelled `"word"`.** Nothing is silently
  upgraded, and nothing pretends a word match was a
  meaning match.

When a fact has changed, meaning search can never serve
you the old words as if they were still true: every
meaning hit is checked against what is true *now*
before it is shown.

## A3. When a fact changes

There are two different acts, and they are not the
same:

- **Correcting** fixes a fact that was *wrong*: the
  same fact keeps its number, and your words replace
  the wrong ones. Nothing new hides the mistake.
- **Superseding** records that the world *changed*: the
  old fact stops being "true now" and is kept as
  history; the new fact becomes the current one. Ask
  what is true and you hear the new one; ask to inspect
  your memory and you can see both, marked which is
  which.

## A4. Your memory is yours — the four rights

Everything in this section is a working operation, not
a promise:

- **See it all.** You can look at everything remembered
  for you: the facts still believed true, the old
  versions kept as history (shown separately), and the
  remembered conversation turns — with plain counts
  first. You can also look at any single fact exactly as
  stored.
- **Fix it.** Any fact that is wrong can be corrected
  in place (§A3).
- **Take it away with you.** Your whole memory exports
  as one plain bundle you can carry as a file: facts
  (marked still-true or old version), turns, and
  counts. Nothing belonging to anyone else is ever in
  your bundle.
- **Have it forgotten.** One fact can be forgotten for
  real — its record is removed. *Everything* can be
  forgotten at once, but only when you say the exact
  confirmation words `"delete everything"` — a slip, a
  typo, or a near-miss deletes nothing. Forgetting is
  per person: your total deletion provably leaves every
  other person's memory untouched.

Two honest limits, stated rather than hidden:

- **A forgotten conversation turn's stored bytes are
  not yet physically reclaimed** (docket 119). The turn
  is sealed off the moment you forget it — it can never
  be shown, searched, inspected, or exported again —
  but the storage program has no "delete a turn"
  operation yet, so its bytes wait for one. Forgotten
  means *unreachable forever*, and the deletion report
  itself says the bytes-reclaimed figure is 0.
- **The memory engine keeps an audit trail of hashes**
  (docket 120): after a deletion, a short scrambled
  fingerprint of the fact's *number* — never its words —
  remains in the engine's own accountability log. No
  words of yours remain anywhere after a deletion.

## A5. Different people, different memories

A companion can serve more than one persona (a named
identity it speaks as and remembers for). The rule is
absolute: **one persona's facts and turns are invisible
to every other persona** — not searchable, not
inspectable, not correctable, not deletable, not
exportable. A name that is not a valid persona name is
refused outright; it never quietly falls back to
someone else's memory. The one shared thing is
documents (§A1): a document added as a document is
library grounding for the whole companion, which is
why documents are never part of one person's export or
deletion.

## A6. How memory ages

Memory is not pruned in a panic, because it does not
need to be: a measured month of daily companionship
costs 0.39 MiB of growth, inside even the toaster's
2 MiB monthly allowance. A simulated *year* of memory
— 7,300 turns, 377 facts, 365 diary files — weighed
5,717,556 bytes in total, about a quarter of the
toaster's twelve-month allowance.

What does happen, when a lifecycle pass is run:

- **Facts fade, they are not thrown away.** A fact not
  revisited loses importance over time (a 30-day
  half-life by default), down to a floor — it is never
  deleted by ageing. Only you delete facts (§A4).
- **Stale signposts are collected.** When a fact has
  been replaced or forgotten, the signpost that let
  meaning search find it is dropped, so it can never be
  served again. (Its stored index bytes, like a
  forgotten turn's, await a delete operation the store
  does not yet have — docket 112; the report says so.)

One open wrinkle is recorded, not concealed
(docket 125): running the fading pass monthly makes facts fade
somewhat faster than the stated half-life, because each
pass applies the full age again. Whether the pass
should remember when it last ran is a decision the
Part V gate (E-092) owns; no number in this document
depends on it.

## A7. What memory costs, per machine

Measured prices (campaign VM measurements, E-078;
device truth is named per device where it exists):

| Thing | Cost |
|---|---|
| One living fact | 745 B |
| One conversation turn | 585 B |
| One meaning-indexed fact | 72,239 B (hence §A2's toaster rule) |
| Monthly growth allowance: toaster / phone / pi / laptop | 2 MiB / 10 MiB / 25 MiB / 100 MiB |

## A8. The two neighbours that are not this memory

- **The session diary** (Verdandi's conversation
  logger) is the truth about *what was logged* in a
  session; this memory is the truth about *what the
  companion currently remembers*. They are two views,
  never merged. Log entries become facts only through
  one guarded crossing, under rules you control, and
  every fact that crossed carries its provenance (which
  session fed it). If you delete a logged session, the
  facts it fed are *not* silently deleted from memory:
  whoever deletes the session can run the retraction
  that forgets exactly those facts, or audit for them
  first. Facts you told the companion directly are
  never touched by either.
- **The WYRD shapes.** Your memory can also be exported
  in the record shapes the house's world-model work
  (the WYRD Protocol) consumes — the same facts and
  turns, dressed in its envelopes. That export is
  one-way data in WYRD's shapes: Ember builds no world
  model, writes nothing into WYRD, and invents nothing
  to fill a field it does not hold.

## A9. The third system you may hear about

Three memory systems stood in this house when Part V
began. Two of them are this memory (living facts and
documents/turns, §B1). The third, mempalace, is **not**
part of your companion's memory: it fits no tiny-hardware
budget in the book (roughly 403 MiB of working memory
against ceilings of 64–384 MiB), nothing in the
companion uses it, and its honourable retirement from
Ember has been *proposed* — the decision is Volmarr's
word, it has not been given, and until it is, the member
stays exactly where it is, untouched, under the
fallback restraints (never bundled, never a default).
If retirement is ever ruled, existing palace stores get
the one-way migration E-081 proved on fixtures — never
a silent deletion.

---

# Part B — For builders

## B1. Architecture: one face, two bounded engines

```
            callers (companion code, tools, tests)
                            │
                     MemoryFace            ← the only contract
              ┌─────────────┼──────────────────┐
              │             │                  │
     living facts     documents, chunks,   sidecar (JSON,
     via RunaMemory   episodes via         atomic replace):
     (library only,   BrunnrHandle         episode persona tags,
     never raw SQL)                        fact→chunk index map,
                                           tombstones, log-feed
                                           provenance
              │             │
         mimir-well     Brunnr store
         store          (sqlite_vec /
         (~/.mimir_well/ pgvector shapes)
          mimir_well.db)
```

- **mimir-well owns living facts**: importance, mood
  (emotional valence), validity windows, supersession,
  current truth, the write guard, the audit trail, and
  the Ebbinghaus decay the lifecycle delegates to. The
  face speaks to it **only through `RunaMemory`** — it
  is the companion's one sanctioned library-path
  consumer (docket 109's reckoning, E-080 §6); the four
  elder raw-SQL consumers keep their stated paths, and
  Part VIII owns bifrost's side.
- **Brunnr owns documents, chunks, and episodes**, as
  it did before the face existed; survivor stores stay
  native behind the face, proven byte-identical in
  schema and content rows by E-081.
- **The sidecar is bookkeeping, not a third store**:
  one JSON file beside the mimir store by default
  (`memory_face_sidecar.json`), replaced atomically on
  every change, holding only tags and pointers —
  `episode_persona`, `fact_chunk`, `fact_persona`,
  `deleted_episodes` (docket 119 tombstones),
  `log_facts` (E-085 provenance), `index_document_id`.
  A corrupt sidecar degrades to empty and fails closed
  both ways (E-083): untagged episodes fall back to the
  default persona only, and facts fall back to
  unindexed.
- **One canonical path** (docket 51):
  `CANONICAL_MIMIR_DB_PATH` is
  `~/.mimir_well/mimir_well.db` — the mimir-well
  library's own default, named once in the face. Any
  other path arrives only as explicit configuration.
- **Chat is not rewired yet — stated plainly.** As of
  this slice no code in `src/ember/` outside
  `well/memory_face.py` references the face; the chat
  loop still opens Brunnr directly, as E-080 §7
  recorded. The contract exists, proven, so the wiring
  slices bind to one face instead of two stores; do not
  write docs or code that assume the wiring has landed.

## B2. Opening a face

```python
from ember.schemas.config import ConversationProfile
from ember.well.memory_face import MemoryFace

face = MemoryFace.open(
    profile=ConversationProfile.LAPTOP,
    embedder=my_embedder,          # caller-supplied; the core grows none
)
print(face.state())                # both halves, profile, index mode
face.close()
```

- `MemoryFace.open(...)` accepts `brunnr_config` (opens
  Brunnr through its own registry), an injected
  `brunnr` handle, `mimir_db_path`, `mimir_src`,
  `profile`, `embedder`, `index_facts` (override the
  profile default), `sidecar_path`, and
  `default_persona_id`. Tests inject both handles and a
  `tmp_path` sidecar (the E-080 battery's `_face` shape).
- **Graceful offline**: a `Disconnected` Brunnr or an
  unloadable mimir-well never raises at open. The
  affected half reports its state (`state()` /
  `mimir_state`) and its operations return typed empty
  or refusal results — `FactResult(None, False, note)`,
  `[]`, or a stated `note` — never a fabricated success.
- mimir-well is loaded lazily at open, never at module
  import (the E-067 discipline): an importable
  `mimir_well` wins, then the in-tree member's `src`.

## B3. The contract surface (complete)

Every public operation on `MemoryFace`, grouped as the
module groups them. The E-090 battery derives this list
from the class itself, so an operation added without a
row here fails the gate.

**State and lifecycle of the face itself**

| Operation | Returns | Notes |
|---|---|---|
| `open(...)` (classmethod) | `MemoryFace` | §B2 |
| `state()` | `dict` | both halves, canonical path, profile, index mode + price, indexed count, monthly ceiling |
| `close()` | `None` | closes both handles that are present |

**Living facts (mimir-well's territory)**

| Operation | Returns | Notes |
|---|---|---|
| `remember_fact(content, *, category, importance, emotional_valence, persona_id)` | `FactResult` | guarded write; a guard block is reported, never hidden; `indexed` + note say whether/why not indexed |
| `recall_facts_word(query, *, limit, persona_id)` | `list[dict]` | FTS5 word search, current facts only, asker's only |
| `recall_current(*, limit, min_importance, persona_id)` | `list[dict]` | the current-truth view |
| `recall_by_importance(*, min_importance, limit, persona_id)` | `list[dict]` | current only |
| `recall_by_mood(target_valence, *, tolerance, limit, persona_id)` | `list[dict]` | current only |
| `supersede_fact(old_fact_id, new_content, *, persona_id)` | `FactResult` | old fact stops being current; new fact indexed under the usual rule |
| `search_facts_meaning(query, *, k, persona_id)` | `MeaningHits` | `mode` is `"meaning"` or `"word"`, always stated (§B4) |

**The user's rights (E-084)**

| Operation | Returns | Notes |
|---|---|---|
| `inspect_fact(fact_id, *, persona_id)` | `dict \| None` | owner's eyes only; anyone else is shown nothing |
| `inspect_memory(*, persona_id)` | `dict` | plain counts first, then current facts, old facts, turns |
| `correct_fact(fact_id, new_content, *, persona_id)` | `FactResult` | in place, same id, audited; an indexed fact is re-indexed with the corrected words |
| `export_memory(*, persona_id, path)` | `dict` | the plain bundle (§A4); with `path`, also written atomically as JSON |
| `export_wyrd(*, persona_id, path)` | `dict` | the WYRD-shaped bundle (§B6) |
| `delete_fact(fact_id, *, persona_id)` | `dict` | real row deletion; a fact's own old versions (its lineage) are forgotten first, oldest first |
| `delete_all_memory(*, persona_id, confirmation)` | `dict` | total per persona; `confirmation` must equal `DELETE_ALL_CONFIRMATION` = `"delete everything"` exactly |

**Logger reconciliation (E-085)**

| Operation | Returns | Notes |
|---|---|---|
| `ingest_log_candidates(candidates, *, persona_id)` | `dict` | counts-only report; lawful shape = source `conversation_logger`, category in `LOG_FEED_CATEGORIES`, named session + persona + provenance |
| `logger_provenance(*, persona_id)` | `list[dict]` | fact id, session, category, rule — never the words |
| `audit_logger_reconciliation(live_session_ids, *, persona_id)` | `dict` | finds orphaned fed facts; deletes nothing; never audit against a size-pruned log (docket 100) |
| `retract_deleted_session(session_id, *, persona_id)` | `dict` | forgets exactly the facts that session fed, through `delete_fact` |

**Lifecycle (E-082)**

| Operation | Returns | Notes |
|---|---|---|
| `lifecycle_report()` | `LifecycleReport` | priced from the measured anchors only (§B5) |
| `prune_stale_index()` | `dict` | drops stale sidecar pointers; `physical_bytes_reclaimed` is honestly 0 (docket 112) |
| `run_decay(*, persona_id, half_life_days)` | `dict` | delegates to the member's decay verbatim; its `pruned` count means *floored at importance 1*, never deleted (docket 113) |
| `run_lifecycle(*, persona_id, half_life_days)` | `dict` | decay → prune → report, in that order |

**Documents and episodes (Brunnr's territory)**

| Operation | Returns | Notes |
|---|---|---|
| `add_document(doc)` | `int \| None` | pass-through to the handle |
| `add_chunks(chunks)` | `list[int]` | pass-through |
| `search_documents_word(query, *, k)` | `list[RetrievalHit]` | the fact index is never a document result (docket 114) |
| `search_documents_meaning(qvec, *, k)` | `list[RetrievalHit]` | likewise; both widen past filtered index hits |
| `add_turn(episode)` | `int \| None` | records the episode's persona tag in the sidecar; an invalid tag is refused, nothing stored |
| `recent_turns(*, limit, persona_id)` | `list[Episode]` | the persona's *newest* `limit`, oldest-first; tombstoned turns never served |

Result shapes: `FactResult(fact_id, indexed, note)`,
`MeaningHits(mode, facts, note)`, and
`LifecycleReport(...)` are frozen dataclasses defined
in the module; everything else returns the plain
`dict` / `list` shapes tabled above.

## B4. Index, don't merge — the meaning-search flow

1. `remember_fact` writes the fact to mimir-well. Only
   then, if indexing is on for the profile *and* an
   embedder was supplied *and* Brunnr is live, the face
   adds the fact's text as one chunk of its single
   synthetic index document (source
   `FACT_INDEX_SOURCE` = `"ember-memory-face/fact-index"`)
   and records chunk → fact + persona in the sidecar.
   Every other case returns `indexed == False` with the
   reason in the note (profile, no embedder, no Brunnr,
   or — docket 122 — the index record could not be
   saved: the fact is durable, word search still finds
   it, and the face never claims an index it did not
   record).
2. `search_facts_meaning` embeds the query, scans the
   index widening until the *asker's* facts are found or
   the index is exhausted (dockets 115/116), and
   **resolves every candidate through mimir-well**: a
   fact is served only if it still exists, belongs to
   the asker, and is current. A superseded fact's chunk
   may still sit in Brunnr; resolution, not the index,
   decides truth.
3. With the index off, no embedder, or no Brunnr, the
   same call answers by word search with
   `mode == "word"` and the reason stated — the
   toaster's shipping shape, not an error state.

Persona discipline (E-083) binds every operation:
`persona_id=None` means the face's *configured* default
persona; any explicit id must satisfy the E-025 slug
rules, and an invalid id (the empty string included)
fails closed everywhere — reads return nothing, writes
are refused with the reason. There is no silent
substitution of one persona for another at this layer,
ever.

## B5. Constants a builder can rely on

All defined in `ember.well.memory_face` and pinned by
the E-090 battery against this document:

| Constant | Value | Source |
|---|---|---|
| `CANONICAL_MIMIR_DB_PATH` | `~/.mimir_well/mimir_well.db` | the library's own default (docket 51) |
| `FACT_BYTES_PER_FACT` | 745 | E-078 harness |
| `EPISODE_BYTES_PER_TURN` | 585 | E-050 / E-078 |
| `INDEX_BYTES_PER_FACT` | 72,239 | E-078 embedded-chunk growth |
| `DELETE_ALL_CONFIRMATION` | `"delete everything"` | E-084 |
| `FACT_INDEX_SOURCE` | `"ember-memory-face/fact-index"` | E-080 |
| `LOG_FEED_SOURCE` | `"conversation_logger"` | E-072 / E-085 |
| Index default profiles | phone, pi, laptop (not toaster) | verdict §5.4 |

## B6. The WYRD-shaped export (E-086)

`export_wyrd` re-shapes `inspect_memory`'s lawful view
into the WYRD Protocol's published shapes: facts as its
`CanonicalFactRecord` (store `mimir_canonical_store`),
turns as its `ObservationRecord` (store
`hugin_observation_store`), plus its `FactSummary`
grouping. The boundary is ThoughtForge TF-145's: this
side owns cognition and memory; WYRD owns the
world-model. Fields Ember does not hold are never
invented — a fact's key is its mimir-well category, its
confidence is the member's importance rescaled, its
support names a logger session only where E-085's
provenance recorded one, and a turn with no recorded
time is stamped at export and counted as such.

## B7. Open dockets a builder must not trip over

- **docket 108** — mimir-well's flask dependency hygiene;
  owed at or before the E-092 gate.
- **docket 112** — Brunnr has no chunk delete: stale
  index chunks become unreachable and uncounted, their
  bytes unreclaimed (§A6).
- **docket 113** — the member's decay vocabulary:
  `pruned` means floored, not deleted (§B3).
- **docket 119 / docket 120** — turn tombstones and
  audit hashes (§A4).
- **docket 125** — decay passes compound (§A6); the
  E-092 gate owns the semantics choice.
- **The mempalace question** (§A9) and **docket 51/109's
  other consumers** (§B1) stand exactly where E-079 /
  E-080 left them: E-091 owns the residue marking after
  Volmarr's word, E-092 is Part V's gate, and Part VIII
  owns bifrost's side.

## One guard extended, consciously

This slice's own battery carries the governance needle
"Volmarr's word" (§A9's status pin), which E-089's
canon guard correctly refused: the name may appear in
test files only where its 11-file allowlist records a
reason. The battery was added to that allowlist as its
twelfth file, with its reason, in
`tests/unit/test_canon_test_data_e089.py` — the
conscious act that guard exists to force, recorded
here rather than routed around.

## Slice gate

Conformance: `tests/unit/test_memory_model_docs_e090.py`
— this document's plain part precedes its builder part;
every public `MemoryFace` operation is documented;
the constants, prices, profiles, and honest limits
above match the module; the mempalace status is stated
as proposed-not-decided; and the chat-not-rewired truth
(§B1) is stated, not hidden. Root-suite gate runs are
recorded in CAMPAIGN_STATE at banking. No README
touched; no code touched — this slice documents the
model E-080–E-089 built and proves the document against
it.

*Filed by the E-090 slice, 2026-11-01. Next: E-091 —
the verdict's residue: the retired-or-bounded system's
docs marked truthfully (superseded, with the successor
named), after Volmarr's word or under the fallback.*
