# E-086 — Memory ↔ WYRD-shaped export: memory in the world-model's shapes

*Part V, slice E-086. Roadmap line: "Memory ↔ WYRD-shaped
export: the companion's memory exportable in the shapes
the constellation's world-model work consumes
(ThoughtForge TF-145's boundary, honoured)." The export
lives on the one memory face,
`src/ember/well/memory_face.py` (E-080), as
`MemoryFace.export_wyrd()`; the conformance battery is
`tests/unit/test_memory_wyrd_export_e086.py`.*

## In plain words

**The companion can now hand its memory over in the
shape the family world-model understands.** Ember already
lets a person take their memory out as one plain bundle
(E-084). This slice adds the second door: the same memory
— your facts, their old versions, your conversation
turns — re-shaped into the record shapes the WYRD
Protocol itself publishes, so WYRD's world-model work can
consume it without an interpreter in between. Nothing new
is remembered, nothing is merged, and nothing leaves the
machine unless the caller writes the bundle to a file,
exactly like the plain export.

## 1. The boundary, honoured (TF-145)

ThoughtForge's TF-145 draws the line this slice is built
on: **ThoughtForge owns cognition; the WYRD Protocol
owns the world-model** — what each owns, and the
interface between them. This face sits on the cognition
side of that line. So the export is deliberately only an
*offering*:

- Ember **shapes data** in WYRD's published record
  shapes. That is Ember's side of the interface.
- Ember **builds no world model**: no entities are
  inferred, no relations are derived, no world state is
  asserted. The persona and the companion appear as
  entities because WYRD's shapes need a subject to hang
  facts on — they are labels for the offering, not a
  modelled world.
- Ember **writes nothing into WYRD** and claims no
  WYRD-side ingestion. Whether WYRD takes the offering,
  and what it models from it, is WYRD's own road (its
  Passive Oracle and bridges), not this slice's claim.
- ThoughtForge is not imported or consulted: the
  boundary is honoured by *shape and restraint*, the
  same way E-024 bound TF's frozen contract without a
  live turn.

The bundle states this boundary in its own `boundary`
block, so the truth travels with the data.

## 2. The shapes (WYRD's own, pinned)

Every field table below is WYRD's published model
(`wyrdforge.models.memory`, `wyrdforge.oracle.models` in
the WYRD Protocol tree), whose models forbid extra
fields — so the battery pins the export's key sets
*exactly*, and a live-model validation runs wherever a
real `wyrdforge` is importable (it skips honestly in
environments that do not carry WYRD; Ember's core gains
no pydantic and no WYRD dependency).

| Ember memory | WYRD shape |
|---|---|
| The persona | `EntitySummary` — `entity_id` `ember-persona:<id>`, name, tags `["ember-persona"]` |
| The companion | `EntitySummary` — `entity_id` `ember-companion` |
| A fact still believed true | `CanonicalFactRecord` (store `mimir_canonical_store`): the `MemoryRecord` envelope over a `CanonicalFactPayload` |
| Current facts, grouped | `FactSummary` list under the subject id — the grouping WYRD's `WorldContextPacket.canonical_facts` uses |
| An old (superseded) version | The same `CanonicalFactRecord` shape, `write_policy: ephemeral`, facet `current: ["false"]`; the current fact's payload names it in `supersedes_record_id` |
| A remembered turn | `ObservationRecord` (store `hugin_observation_store`): an `utterance` observation, participants = persona + companion |

*Proof beyond the pinned tables:* at this slice's
building, a bundle produced by the real face (a
supersede chain, a logger-fed fact, a turn) was validated
against WYRD's **live** pydantic models in the WYRD
tree's own environment — 8 of 8 objects
(`CanonicalFactRecord` ×3, `ObservationRecord` ×1,
`EntitySummary` ×2, `FactSummary` ×2) validated with no
errors. The battery's live-model test re-proves this
wherever `wyrdforge` is importable and skips honestly
where it is not.

The envelope is complete on every record: `entity_scope`
(subject first, companion second, the feeding session
where one is recorded), `truth`, `provenance`,
`lifecycle`, `retrieval`, `governance` (training always
refused; promotion always review-gated — the offering
never pre-approves itself into a world model), and
`audit`.

## 3. Nothing invented to fill the shapes

WYRD's shapes ask for fields Ember's memory does not
natively keep. Each is filled from something real, or
left honestly empty:

- **`fact_key`** is the fact's mimir-well *category* —
  the only key the member keeps. Ember does not parse a
  key out of the fact's words.
- **`confidence`** is the member's importance (kept
  1–10) rescaled to WYRD's 0–1. It is the member's own
  number in WYRD's units, not a new judgement.
- **`support_record_ids`** names a logger session
  (`ember-log-session:<id>`) only for facts E-085's
  provenance actually recorded as logger-fed; a directly
  remembered fact's support list is empty, and its
  `entity_scope.session_id` is null.
- **`supersedes_record_id`** comes from the member's own
  `superseded_by` link, inverted: the new fact names the
  old record it replaced.
- **A turn's `observed_at`** is the turn's own recorded
  time; a turn that carries none is stamped with the
  export time and counted under
  `counts.turns_time_stamped_at_export` — the
  substitution is counted, never silent.
- **`source_hash`** is the member-audit convention: the
  first 16 hex digits of the content's SHA-256.
- Provenance `extracted_by` is `ember-memory-face/e-086`
  — the crossing names the slice that built it.

## 4. The persona law holds

The export is built from `inspect_memory`'s lawful view:
one persona's facts and turns only, invalid persona ids
refused with an empty bundle and the refusal note,
documents (shared grounding, E-025/E-035) never included
— the same law as E-084's plain export, which is
untouched and unchanged. The two exports are two shapes
of one truth, both read-only: exporting changes no
memory, feeds nothing back, and crosses nothing.

## 5. What is NOT claimed

- **No WYRD-side ingestion is proven.** The shapes are
  WYRD's published ones, pinned field-for-field and
  validated against the live models where WYRD is
  importable; that WYRD's running systems accept this
  bundle end-to-end is WYRD's own road to prove.
- **No world model.** No graph, no state, no relations
  beyond the subject/companion labels above.
- **No ThoughtForge involvement.** TF-145 is honoured as
  a boundary, not consumed as a service; TF-145's own
  document is ThoughtForge's slice to write.

## 6. The bug this slice's first duty found — and fixed

This slice's first duty was E-085's owed Run D
re-verification. Run under load, it caught a real defect
in E-084's rights, invisible to every same-second
fixture: **`delete_all_memory` could die half-done on
the member's `superseded_by` foreign key.** The face
deleted facts in the member's search order (importance,
then timestamp); when a superseding fact sorted before
the old version that points at it — which happens
whenever the supersede crosses a timestamp second, and
load made that likely — mimir-well's delete was refused
by the key and the exception escaped, leaving a partial
total-delete: the worst failure shape a "forget
everything" right can have. The same trap waited in
`delete_fact` for any fact an old version points at.

Fixed on the face (no member code touched):

- `delete_all_memory` deletes oldest-first (ascending
  id): a `superseded_by` reference always points at a
  later-created fact, so referrers are always removed
  before referents, in any chain.
- `delete_fact` forgets the fact's lineage with it: the
  old versions of that very fact (the ones pointing at
  it) are removed first, oldest first, and the result
  counts them as `old_versions_deleted` — forgetting a
  fact means forgetting what it replaced, not stranding
  a dangling chain.

Regression-pinned in this slice's battery with a
deterministically staggered fixture (the new fact made
to sort first — the exact killing order), plus the
lineage and no-lineage delete cases. E-084's and E-085's
batteries re-run green with the fix in place.
