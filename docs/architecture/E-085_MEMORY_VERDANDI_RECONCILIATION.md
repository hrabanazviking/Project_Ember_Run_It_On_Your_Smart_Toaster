# E-085 — Memory ↔ Verdandi: the logger's records and memory's facts reconciled

*Part V, slice E-085. Roadmap line: "Memory ↔ Verdandi:
conversation_logger's records and memory's facts reconciled
(one truth, two views or a stated boundary)." The
reconciliation lives on the one memory face,
`src/ember/well/memory_face.py` (E-080); the conformance
battery is
`tests/unit/test_memory_logger_reconciliation_e085.py`.*

## In plain words

**The companion keeps a diary and it keeps a memory, and
those are two different things.** The diary — Verdandi's
conversation logger — is the truth about *what was logged*
in a session: the entries exactly as they were written,
kept under the logger's own law (E-063), with the owner's
own delete right. Memory — this face — is the truth about
*what the companion currently remembers*: living facts it
believes now, and conversation turns it kept. Neither one
is a copy of the other, and this slice does not merge
them. It builds the one lawful road between them, and
states the boundary plainly: **two views** of a
companionship, joined by a crossing the user controls —
not one store pretending to be both.

## 1. The stated boundary (two views)

| Question | Whose truth |
|---|---|
| What was said and decided in session X, as logged? | The logger's log (E-063) |
| What does the companion believe and remember now? | The memory face (E-080) |
| What may move from the diary into memory? | Only E-072 feed candidates, under the user's rule |
| When a logged session is deleted, what happens in memory? | §3 — retraction, run explicitly (docket 104) |

The logger's other copies (its current-session snapshot
and its nerve-feed copies) remain the logger's business,
governed by E-063/E-071; the face neither reads nor
re-points them. The face's conversation *turns* (Brunnr
episodes) are a separate record from the logger's
*entries*: a turn is what the companion said and heard in
chat, an entry is what a session's keeper wrote down.
They are not reconciled row-for-row because they were
never the same record — the battery pins the feed road
below as the only place log material becomes memory.

## 2. The crossing, completed: ingest with provenance

E-072 built the feed's law and stopped at the boundary:
candidates were *offered*, and no store was written. This
slice builds the receiving side,
`MemoryFace.ingest_log_candidates`:

- **Lawful shape only.** A candidate must claim source
  `conversation_logger`, carry one of the four feedable
  categories (`lesson`, `decision`, `milestone`,
  `session_summary` — exactly E-072's vocabulary), hold
  non-empty words, name its session, and carry its
  provenance dict. Anything else is counted
  `withheld_invalid`.
- **A persona is never guessed.** The candidate's persona
  tag comes from the caller's session-owners mapping
  (E-072 §5). A candidate with no tag, or a tag that is
  not a valid persona slug, is counted
  `withheld_unattributable` and remembers nothing. When
  the caller names a persona, a candidate tagged for
  anyone else is `withheld_persona_mismatch` — withheld,
  never re-homed.
- **Provenance is recorded.** Each ingested candidate is
  remembered through the face's own guarded
  `remember_fact` (so the member's guard, the profile's
  index rule, and the persona wall all apply unchanged),
  and the sidecar records its origin: fact id, session,
  persona, category, rule id — keyed by a hash of
  (session, category, words), so the sidecar holds no
  second copy of the words. `logger_provenance()` lists
  those rows, per persona, words never included.
- **A repeat feed is a duplicate, not a second fact.**
  Re-feeding the same (session, category, words) is
  counted `withheld_duplicate` for as long as the fed
  fact lives — across a close and reopen of the face
  (battery-pinned). If the fed fact was forgotten, its
  provenance is dropped with it (the face's delete paths
  clean it; a fact deleted behind the face's back is
  detected as stale at the next feed), so a later feed is
  a fresh crossing, not a resurrection of bookkeeping.
- **The report is counts only** — totals, per-reason
  withholdings, and the new fact ids. No candidate words
  and no session ids appear in it (sentinel-pinned), in
  E-072's counts-only discipline.

## 3. Deletion reaches fed memory — docket 104, settled

E-072 left this exact question as **docket 104**: a
session deleted under the logger's right (E-063) leaves
the log, so no *later* feed can draw from it — but what
of candidates *already fed*? The answer, built here:

- **`retract_deleted_session(session_id)` is the
  propagation.** It forgets exactly the living facts the
  named session fed — each through the face's own
  `delete_fact`, so its meaning-search entry and its
  provenance go with it — and nothing else. Facts the
  persona remembered directly (never fed) are untouched,
  other sessions' fed facts are untouched, and another
  persona's fed facts from a same-named session are
  untouched unless no persona fence is named (battery
  pins each). A fed fact the user already forgot is
  counted `already_gone`, and its stale provenance is
  dropped either way.
- **`audit_logger_reconciliation(live_session_ids)` is
  the finder.** Given the caller's authoritative list of
  sessions still in the log, it reports the tracked fed
  facts whose session is gone — counts and the orphaned
  fact ids — and deletes nothing, so a person decides
  before anything is forgotten.
- **Propagation is not automatic — and that is stated,
  not hidden.** The logger is a standalone Verdandi
  member, loaded file-by-file, with no hook into this
  core (the E-067 no-member-imports discipline runs both
  ways). Nothing in the logger's delete path can call
  this face. So deletion reaches already-fed memory when
  the caller who deleted the session runs the
  retraction — or audits for orphans and then does. The
  end-to-end battery proves the whole road with the real
  logger: feed → ingest → logger deletion (memory
  unchanged on its own, exactly as this boundary says) →
  audit finds the orphan → retraction forgets it.
- **One misuse is refused by naming it:** the audit's
  live list must come from a deletion the user made,
  never from a size-pruned log. Bifröst's line pruning
  (docket 100) is machine hygiene, not a deletion; every
  audit report carries that warning, because auditing
  against a pruned log would mistake hygiene for intent
  and orphan facts whose sessions were never deleted.

## 4. What did not change

No Verdandi code was touched: the logger, its delete
right, and the feed law stand exactly as E-063/E-072 left
them — this slice is entirely the memory side of the
boundary, as E-072 assigned it. Chat is still not rewired
to feed or retract on its own (no cadence was claimed by
this slice; the operations are live on the face for the
wiring slices that follow). Mempalace is untouched, its
retirement question exactly where E-079 left it.
Docket 104 is **closed** by this slice; dockets 100
(pruning shape, E-076's verdict stands), 112 and 119
(handle-level deletes) are unchanged.

## 5. Gate

Conformance:
`tests/unit/test_memory_logger_reconciliation_e085.py`
(see CAMPAIGN_STATE for the runner counts of this slice's
gate). Combined Part V conformance and the whole-suite
gate runs are recorded in CAMPAIGN_STATE.md with this
slice's banking entry.
