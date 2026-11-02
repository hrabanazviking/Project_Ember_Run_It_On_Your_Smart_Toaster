# E-069 — Ordering & Replay: Events Replay Deterministically for Debugging

*Part IV, slice E-069. Starting HEAD: 7d91cf4 (E-068 banked +
its push record). Method: the ordering facts were re-read
from code this slice — the hub's stamping in
`Verdandi/nervous_system.py` (monotonic `_seq`, `_ts`,
`_iso`; ring buffer and feed reload), the contract's stamp
and fallback rules in `Verdandi/event_contract.py` (E-061),
the stimuli provenance shape (E-064), and the Hermes
provenance keys (E-068). The replay law in code is
`Verdandi/replay.py`; conformance is pinned by
`tests/unit/test_ordering_replay_e069.py` (§7).*

## 1. Plain-language summary

When something odd has happened in the companion's nerves,
the way to understand it is to play the nerve feed back —
the same events, in the same order, again. Until this slice
that playback had no rules anyone had written down: the
feed is a pile of lines, some stamped by the hub, some
written by hand when the hub was down, some in older shapes
entirely, and two people replaying it could reasonably
disagree about what order it happened in.

Now the order is a law, stated once and pinned by tests.
Events the hub stamped play back in the hub's own numbered
order. Events with no number — the offline writes, the old
shapes — play after them, ordered by their timestamps and
then by where they stood in the file, and nobody invents a
number for them. A replay also reports what it found:
which numbers are missing (the gaps the offline design
always promised), which numbers appear twice, and which
feed lines were too damaged to read — named by line
number, skipped, never hidden and never fatal. And every
replay carries a fingerprint (a SHA-256 digest of its
ordered events in canonical form), so "we replayed the
same session" is a checkable fact, not an impression:
same feed, same order, same digest — even if the copy of
the feed you were handed had its numbered events shuffled.

## 2. What ordering facts the tree already held

- **The hub stamps in broadcast order.** `NerveHub` assigns
  `_seq` from a single counter that only increases, adds
  `_ts` (epoch) and `_iso` (UTC), appends the stamped event
  to `nerve_feed.jsonl`, keeps it in the 256-event ring, and
  broadcasts it — so for hub events, `_seq` order, feed
  order, and broadcast order are the same order (E-059 §6,
  E-061 §2). On restart the hub reloads the feed and resumes
  the counter past the highest `_seq` it finds.
- **Fallback writes have no `_seq`, by design.** When the
  hub is unreachable, `publish_event_sync` and the E-067
  cross-member senders write the envelope to the feed
  themselves with `_ts`/`_iso`/`_fallback` and no `_seq` —
  "sequence holes are by design" (E-061). Any replay law
  that required a sequence would refuse exactly the events
  written while the system was in trouble — the events a
  debugging replay most needs.
- **Legacy lines carry their own time, in two shapes.** The
  retired heartbeat fallback wrote an ISO `timestamp`
  string; the retired mood dialect wrote an epoch
  `timestamp` number (both still recognised by
  `event_contract.classify_dialect`, restated in replay.py).
- **Provenance must survive.** Stimuli carry their
  provenance inside `data` (E-064); Hermes events carry an
  inner envelope with `event_id`/`occurred_at`, or, after
  E-068's translation, `_hermes_schema`,
  `_hermes_schema_version`, `_hermes_event_id`, and
  `_hermes_occurred_at` keys. E-068 §9 handed those keys to
  this slice explicitly: replay must preserve them.

## 3. The replay law (in code: `Verdandi/replay.py`)

`replay.py` is stdlib-only and standalone, like every
Verdandi contract module since E-061 (deployed copies are
loaded file-by-file). It defines:

- **Order.** (1) Sequenced events, by `_seq` ascending,
  file index breaking duplicate-`_seq` ties. (2)
  Unsequenced events, by effective timestamp ascending,
  file index breaking ties. (3) Untimestamped unsequenced
  events last, in file order. Only a genuine `int` counts
  as a `_seq` (a bool or a numeric string is no stamp).
- **Effective timestamp.** `_ts` if numeric, else `_iso`
  parsed as ISO-8601, else the legacy `timestamp` field
  (numeric, or ISO-8601). A naive ISO stamp is read as UTC
  — the hub's stamps are timezone-aware UTC, and the rule
  is stated in the code, not guessed per event.
- **Reading a feed.** `load_feed_lines` / `load_feed_text`
  parse JSONL without ever raising: blank lines are
  skipped (a trailing newline is not damage); a line that
  is not valid JSON, or whose JSON is not an object, is
  skipped and reported as an issue with its 1-based line
  number and kind (`invalid_json` / `not_object`).
- **The report.** `replay_events` / `replay_feed_lines`
  return the ordered events, the digest, the count, the
  `_seq` range, the **gaps** (missing numbers inside the
  range), the **duplicate_seqs**, the unsequenced and
  `_fallback` counts, per-dialect counts, and the load
  issues. `replay_to(events, sink)` hands each event to a
  debugging consumer exactly once, in replay order, and a
  sink exception propagates — a consumer that fails
  mid-replay is seen to fail.
- **The digest.** `canonical_line` is JSON with sorted
  keys and fixed separators; `replay_digest` is the
  SHA-256 of the ordered events' canonical lines.
  `validate_replay_order` judges a would-be order against
  the law (by canonical line, so equal-valued events are
  interchangeable).

## 4. The honest limits of this order

- **Fallback placement is a rule, not a reconstruction.**
  An unsequenced event's true position among hub events
  cannot be recovered from the feed — the hub was down;
  that is why it has no number. This law places the
  unsequenced block after the sequenced block, ordered
  internally by timestamp, and says so. It never
  interleaves by wall-clock guesswork and never invents
  a `_seq`. A future consumer that wants chronological
  interleaving must build it on top, knowing it is
  approximating.
- **Replay is not translation.** Replay edits nothing:
  legacy shapes stay legacy-shaped, a raw Hermes event
  keeps its inner envelope, a translated one keeps its
  `_hermes_*` keys, stimulus provenance stays inside
  `data`. Dialect normalisation remains
  `event_contract.normalize_event`'s job and Hermes
  translation remains `hermes_nerves.normalize_hermes_event`'s
  job; a consumer may apply them to replayed events, in
  replay order.
- **Replay is not delivery.** Nothing here re-publishes:
  replaying into the live hub would stamp new `_seq`
  values and broadcast to subscribers — a side effect no
  debugging tool may have by default. `replay_to`'s sink
  is an in-process consumer; wiring a sink to a real
  subscriber is E-073/E-076 territory, not this slice's.
- **The ring buffer is not a feed.** The hub's 256-event
  ring holds only the recent tail; a replay of a session
  longer than that must read the feed file (and its
  rotated archives, E-063), which this law's line reader
  accepts as plain line iterables.

## 5. Fixtures

The conformance suite builds its feed in code (the
E-068 pattern): hub-stamped events arriving out of order,
an offline `_fallback` write, a legacy heartbeat-fallback
line, a legacy mood line, and a timeless operator event in
one fixture; plus dedicated fixtures for duplicate `_seq`,
sequence gaps, corrupt lines (invalid JSON and a
non-object line, named by number), a shuffled sequenced
feed (same digest as the ordered original), a raw and a
translated Hermes event (provenance intact, in `_seq`
order), and a stimulus event (provenance intact).

## 6. Docket effects

- No new docket items. Dockets 100 / 101 / 102 / 103 keep
  their E-076 gate-review owner; E-070 (backpressure)
  inherits this law's report shape — a hub that sheds
  under load (E-070) will create exactly the gaps this
  slice's report names, and its shedding record can be
  checked against them.
- E-068's handoff is discharged: the `_hermes_*`
  provenance keys and the raw inner envelope are both
  replay-preserved, pinned by test (§5).

## 7. Slice gate

- New conformance suite:
  `tests/unit/test_ordering_replay_e069.py` — **19 passed**
  (module standalone/stdlib, dialect mirror of the
  contract plus `unknown`, `_seq` order, the unsequenced
  rule, duplicate tie-break, strict stamp shapes,
  idempotence + order validation, digest determinism
  incl. the shuffled-feed proof, sink order + sink-failure
  propagation, gap/duplicate/count reporting, corrupt-line
  naming, losslessness across dialects, Hermes and
  stimulus provenance survival).
- Prior Part IV conformance re-run: E-061 + E-062 +
  E-063 + E-064 + E-065 + E-066 + E-067 + E-068 + the
  E-057 pins — **149 passed** (137 prior + E-068's 12,
  reconciling exactly; the E-069 suite is counted
  separately above).
- Verdandi focal suites (declared dev deps supplied from
  the campaign's isolated extras dir, short TMPDIR): the
  conversation-layer set **101 passed** — identical to
  E-059–E-068; the heartbeat set **374 passed** —
  identical to E-060/E-065.
- Root suite gate (E-017 method; logs in
  `~/workspace/.verify-tmp/ember-e069/gate/`): Run B
  **1215 passed, 6 failed, 25 skipped, 1 warning** (1196 +
  19; the 6 are the proven environment failures, identical
  set); Run D **1272 passed, 0 failed, 19 skipped,
  1 warning**, exit 0 (1253 + 19 — reconciles exactly).
- Budget consequence handled in-slice: adding
  `Verdandi/replay.py` changed Verdandi's tracked weight,
  so the E-057 table was re-measured in both published
  copies, as its pinning tests require.

*Filed by the E-069 slice, 2026-10-31. Next: E-070 —
backpressure on tiny hardware.*
