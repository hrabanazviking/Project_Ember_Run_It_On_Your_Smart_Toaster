# E-031 — Session persistence: conversations survive restarts

Roadmap slice E-031 (Part II): *"Session persistence:
conversations survive restarts, atomic writes (the Samtal
lesson), corruption fixtures."*

## 1. What was missing

Cross-restart history for *connected* sessions landed at E-021
(docket 81). What remained — **docket 82** — was the sad path:
`ember.schemas.episode` and DATA_FLOW §2.2 step 9' promised that
when the Well is unreachable the Episode "is written to a local
pending-episodes journal under `~/.ember/state/pending_episodes/`
and flushed in on Well recovery". No such journal existed in
code. A disconnected session's turns, and a turn whose Well save
failed mid-session (spoken since E-030, docket 85), lived only
in RAM and were lost at exit.

## 2. The pending-episodes journal

New module `ember.well.pending_journal`:

- **Location** — `<config_root>/state/pending_episodes/`, inside
  the E-020 person tether (custody of the folder is custody of
  the waiting turns; two config roots never share a journal).
  This honours the promised *place*; the promised shape ("a tiny
  SQLite file", DATA_FLOW §2.2) is deliberately not followed —
  per-episode JSON files give O(1) appends on a toaster, isolate
  corruption to the one damaged turn, and need stdlib only. The
  divergence is recorded here, not hidden.
- **Atomic writes (the Samtal lesson)** — each episode is one
  file, written to a `.tmp` sibling, fsynced, `os.replace`d into
  its final name, and the directory is fsynced. A kill mid-write
  leaves at most a `.tmp` fragment, which is ignored — never an
  episode, never "corrupt". File names are UTC-timestamp
  prefixed, so name order is turn order.
- **Contents** — every Episode field, including `persona_id`
  (the journal persists the E-025 tag even though the Brunnr
  adapters do not yet; a waiting turn keeps its persona).
- **Drain** — on a connected session's startup, before history
  loads: each file is passed to `add_episode` in order and
  deleted only *after* the Well accepts it. The first refusal
  stops the drain, keeps the remaining files in order, and is
  reported. A later session resumes where it stopped.
- **Corruption** — a file that cannot be parsed, or whose
  payload fails validation (missing/non-string text fields,
  non-integer cited ids), is **quarantined**: moved to
  `pending_episodes/corrupt/` — never deleted — and reported in
  the drain result. Healthy episodes flush past it.

## 3. Chat wiring (`spark/munnr/chat.py`)

- **Disconnected session**: every turn is journaled instead of
  dropped. The disconnect banner already states the Well is
  unreachable; if the journal write itself fails, that failure
  is spoken with the E-030 consequence ("remembered only until
  this session ends").
- **Save failure on a connected session** (docket 85's site):
  the turn falls back to the journal, and the warning now says
  so — "it has been saved locally and will be added to the Well
  when it can be reached again". Only when the journal *also*
  fails does the operator hear the old session-only wording.
  E-030's pinned test was updated with attribution.
- **Recovery**: a connected startup with a non-empty journal
  drains it (see §2) *before* the E-021 history load, so drained
  turns join that session's prompt history. Outcomes are spoken
  in plain words: how many turns were added, how many files
  were damaged and moved aside (with the folder named), and —
  on a refused drain — how many turns remain saved locally.

## 4. The Well side: atomicity and corruption

- **Durability** — the sqlite_vec adapter now sets
  `PRAGMA synchronous = FULL` beside its WAL mode (the Samtal
  lesson: WAL + FULL is what makes a committed turn survive a
  power cut, not just a clean close).
- **Typed writes** — sqlite_vec `add_episode` is wrapped like
  its sibling writes: a backend error rolls back and raises
  `BrunnrError` (before E-031 it propagated raw).
- **Corrupt rows** — both adapters' `recent_episodes` now skip a
  single damaged episode row (bad cited-ids JSON, a non-integer
  id in the list) with a logged warning naming the row id, and
  return the healthy history. Before E-031 one such row failed
  the whole load and the session started empty. A whole-store
  failure (unreadable file, closed handle) still raises the
  typed error and still gets E-030's spoken startup warning —
  skipping is per-row, never a blanket swallow.

## 5. Honest limits

- Drain happens at chat startup (and `ember ask`, which rides
  chat). A Well that recovers *mid*-session does not drain until
  the next session — there is no background retry loop, by the
  same smallness discipline as the rest of the core.
- If the Well accepts a drained episode and the process is
  killed before the journal file is unlinked, that turn can be
  drained twice at the next startup (the adapters have no
  episode dedup key). The window is one unlink wide; the failure
  mode is a duplicated history turn, never a lost one.
- Drained episodes enter the Well without their `persona_id`
  (the adapters do not store the tag — E-025's limit, owned by
  Part V / E-080). The journal kept the tag while waiting; the
  Well-side separation gap is unchanged, not widened.
- Corrupt-row skipping is spoken in the log, not on screen: the
  operator-facing startup message stays the E-030 one for whole
  load failures. Surfacing a per-row count in the chat banner is
  possible future polish, not claimed here.

## 6. Tests and gate

- New `tests/unit/test_session_persistence_e031.py` — **8
  passed** (default env): journal round-trip in order with the
  persona tag; no `.tmp` after append and a leftover `.tmp`
  ignored; corrupt JSON + invalid payload quarantined while
  healthy turns flush; drain stops at first refusal, keeps
  order, resumes later; disconnected chat turns journaled and
  drained into the next session's Well *and* its prompt, with
  the announcement; save-failure fallback spoken; journal-only
  failure keeping the old honest wording (connected and
  disconnected shapes).
- New `tests/unit/test_episode_corruption_e031.py` — **4
  passed** (extras shape; skips honestly without sqlite_vec):
  WAL + `synchronous=FULL`; two corrupt-row shapes skipped with
  healthy history intact, across a restart; `add_episode` on a
  closed handle raising typed `BrunnrError`.
- Updated with attribution: `test_error_honesty_e030.py`'s
  save-failure test (the spoken consequence is now the journal
  fallback; its E-030 core is unchanged).
- Playbook: the tethering section's "not yet journalled (E-031)"
  limit is replaced with the shipped behaviour.
- Slice gate (E-017 method; logs in
  `~/workspace/.verify-tmp/ember-e031/`): Run B and Run D counts
  are recorded in `CAMPAIGN_STATE.md` for this slice.
- No README touched. **Docket 82 CLOSED.**
