# E-080 — The Chosen Shape Implemented: One Memory Contract

*Part V (Memory: Two Systems, One Verdict), fourth slice.
Roadmap line: "The chosen shape implemented: one memory
contract for the companion (whichever system(s) survive,
behind one face)." The shape is E-079's verdict — **bound**:
Brunnr bounded to documents/chunks/episodes, mimir-well
bounded to living facts, mempalace neither (its retirement
is proposed, not decided — Volmarr's word, E-079 §6; this
slice neither waits on it nor touches the member).*

*The contract lives at `src/ember/well/memory_face.py`
(`MemoryFace`), proven by
`tests/unit/test_memory_face_e080.py`. No store was
merged, moved, or migrated by this slice.*

## 1. Plain-language summary

The companion now has **one memory contract** — one face it
speaks to for everything it remembers:

- **Living facts** ("the beekeeper trades honey at the
  winter market", what matters, how it felt, what is true
  *now*) go to **mimir-well**, through its own library,
  under the asking persona's name.
- **Documents and conversation turns** go to **Brunnr**,
  the incumbent store the companion already uses.
- **Meaning search over living facts** works by
  *index, don't merge* (§4): facts are indexed into Brunnr for
  finding, but every answer is resolved back through
  mimir-well's current truth — so a fact that changed is
  never served in its old shape.
- **On the toaster, meaning search over facts is off** —
  priced, stated, and answered by word search that says
  it is word search (§5). The budget is the project's
  soul; the face does not break it in silence.

## 2. The contract surface

`MemoryFace` (all operations name their bounded engine;
unavailable engines degrade to typed empty results, never
raise — the core's graceful-offline rule):

| Operation | Engine | Notes |
|---|---|---|
| `remember_fact` | mimir-well | guarded write; returns id + whether indexed + a plain note |
| `recall_facts_word` | mimir-well | FTS5, persona-filtered, current only |
| `recall_current` | mimir-well | the current-truth view |
| `recall_by_importance` / `recall_by_mood` | mimir-well | its exact living faces, persona-scoped |
| `supersede_fact` | mimir-well | old fact stops being current; new fact indexed under the same rule |
| `search_facts_meaning` | face (§4) | mode stated: `"meaning"` or `"word"` |
| `add_document` / `add_chunks` | Brunnr | pass-through to the handle |
| `search_documents_word` / `search_documents_meaning` | Brunnr | text / vector search over documents |
| `add_turn` / `recent_turns` | Brunnr + face tags | persona separation at the face (§3.3) |
| `state` | face | both halves, canonical path, profile, index mode, price |

## 3. The verdict's five binding conditions, reckoned

### 3.1 One canonical mimir-well path — docket 51 settled for the companion

The face's one default is the mimir-well library's own
default, named once in the contract as
`CANONICAL_MIMIR_DB_PATH` = `~/.mimir_well/mimir_well.db`.
Any other path reaches the face only as explicit
configuration. The companion — the consumer this part
judges — now has exactly one mimir default, and it is
the library's, not a fourth invention.

### 3.2 Stores are not merged

Facts live only in mimir-well's store; documents and
episodes only in Brunnr's. The E-080 tests pin this: after
remembering an indexed fact, Brunnr holds exactly **one**
document — the face's synthetic index document — and the
fact itself is nowhere in Brunnr's record shape, only an
index chunk pointing back to mimir-well.

### 3.3 Persona separation is a face property — docket 110

Facts are written and read under the persona's own
mimir-well `user_id` namespace (the member's own
isolation, proven at E-077/E-078), so one persona's facts
are invisible to another on every fact path. Brunnr's
adapters persist no persona tag on episodes (docket 110),
so the face tags **above the adapter**: `add_turn` records
the episode's persona in the face's tag sidecar (one small
JSON file beside the mimir store, atomically replaced —
face bookkeeping, not a third store), and `recent_turns`
serves an episode only to its tagged persona. An
**untagged** episode (written before the face, or outside
it) belongs to the default persona only — fail-closed for
everyone else, proven by test. E-083 owns this layer's
full fixture battery; the guarantee is built here.

### 3.4 Budgets bind the face — priced in §5

### 3.5 mimir-well hygiene — docket 108

Not this slice: the flask bound rides to the E-092 gate,
as the verdict assigned ("at or before E-092"). Recorded
here so it is not lost between slices.

## 4. Index, don't merge — implemented and proven

When a fact is remembered on an indexing profile with an
embedder supplied, the face adds the fact's text as one
chunk of its single synthetic Brunnr document (source
`ember-memory-face/fact-index`) and records chunk → fact
in the sidecar. The chunk is an **index entry, not a copy
of record**. `search_facts_meaning` runs Brunnr vector
search, maps hits back to fact ids, drops other personae's
facts, and resolves each candidate through mimir-well's
`get_memory`: a fact is served only if it still exists,
belongs to the asker, and **is current**.

Proven by test with a deterministic stand-in embedder
(synonym-folding bag of words — reworded text lands near
the original without sharing its words):

- a paraphrase question ("When does the boat carry post
  between the isles?") finds the ferry fact — mode
  `"meaning"`, exact content;
- after `supersede_fact`, the same question returns the
  **new** text and never the old — the stale index chunk
  still sits in Brunnr and resolves away at the face.
  Supersession truth lives in mimir-well, exactly as
  E-079 charged.

No embedder supplied → no index, and the remember result
says so plainly. The core grows no embedder of its own in
this slice; production embedding remains the caller's
(Brunnr's existing Ollama-shaped path, E-078's caveat).

## 5. The price, per profile (verdict §5.4)

One indexed fact costs one embedded Brunnr chunk:
**72,239 B** measured growth per embedded chunk (E-078).
Against the budget book's monthly storage-growth ceilings
(E-041), that price buys, per month, roughly:

| Profile | Growth ceiling | Indexed facts it prices | Face default |
|---|---|---|---|
| toaster | 2 MiB | ~29 | **index OFF — word search, stated** |
| phone | 10 MiB | ~145 | index on (embedder permitting) |
| pi | 25 MiB | ~363 | index on |
| laptop | 100 MiB | ~1,452 | index on |

The toaster's ~29 facts a month is not a memory; that is
why the verdict's fallback is the toaster's shipping
shape, not an error state: `remember_fact` still works
(word-priced, 745 B/item in mimir-well, E-078), and
`search_facts_meaning` answers by word search with
`mode == "word"` and the profile named in the note.
Pruning the index under growth pressure is lifecycle
work — E-082 owns it, with this price table as its input.
Combined store-open weight is the two bounded engines'
own (mimir-well 24.2 MiB peak, Brunnr 33.2 MiB store-open,
E-078, VM-measured) — no third engine is opened.

## 6. Docket 109 — the four raw-SQL readers/writers, reckoned with

E-077 found docket 109's four in-tree consumers touching mimir-well's
shape without its library: bifrost's bridge
(`memory_bridge.py`), bifrost's core (`core.py:_ensure_mimir`),
the member's own Eye, and Verdandi's heartbeat check
(which alone follows the library default). The verdict
ordered them "reckoned with, Part VIII consulted — none
broken, none silently re-pointed." The reckoning:

- **The face is not a fifth raw-SQL consumer.** It speaks
  to mimir-well **only through RunaMemory** — the
  companion's one sanctioned library-path consumer.
- **None of the four is re-pointed by this slice.** Their
  paths are theirs (two follow `~/.hermes/memory/runa_memory.db`,
  a deployment shape older than this campaign); changing
  bifrost's storage is Part VIII's call, and the Eye is
  the member's own program. What changed is only this:
  the *companion* now has one canonical default (§3.1),
  so no future core code needs to invent a path — it
  opens the face.
- Their divergence is therefore now **bounded and named**,
  not ambient: E-085 (Verdandi ↔ memory reconciliation)
  and Part VIII (bifrost) inherit a stated map, and
  E-092's gate re-checks it.

## 7. What this slice does NOT claim

- **Chat is not rewired yet.** `MemoryFace` is live,
  proven, and openable (`MemoryFace.open`), but the chat
  loop still opens Brunnr directly, as before. Wiring the
  companion's turns through the face is follow-on work for
  the slices that touch those paths (E-085 first among
  them) — the contract exists so they wire to one face,
  not two stores.
- **No device truth.** All numbers are E-078's VM
  measurements; the bounded shape on real tiny hardware
  is later parts' device work.
- **Persona separation at the face is built, not yet
  fixture-batteried** — E-083 owns the full E-025 fixture
  set at this layer.
- **Lifecycle is not here.** Decay/pruning of facts and
  of the index is E-082, on mimir-well's own machinery.
- **mempalace is untouched**, and the retirement question
  stands exactly where E-079 left it: proposed, awaiting
  **Volmarr's word**, fallback restraints in force.

## Slice gate

Conformance: `tests/unit/test_memory_face_e080.py` —
canonical path, index defaults per profile, fact
word/importance/mood recall + persona isolation,
paraphrase meaning search, supersession resolution,
toaster word-mode honesty, document pass-through, turn
separation + untagged fail-closed, honest degradation,
and this filing's pins. Root-suite gate runs recorded in
CAMPAIGN_STATE at banking. No README touched; no member
code touched (mimir-well is consumed, not modified).

*Filed by the E-080 slice, 2026-11-01. Next: E-081 —
migration: survivors' stores stay native behind the face
(E-079 §3.2); the mempalace-store answer (migrate vs
read-compat forever) argued from fixtures, executed only
under Volmarr's ruling.*
