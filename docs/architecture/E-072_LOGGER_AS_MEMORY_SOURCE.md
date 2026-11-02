# E-072 — The Logger as Memory Source: Logged Conversations Feed Memory Under the User's Rule, Never Silently

*Part IV, slice E-072. Method: the logger's law (E-063), the
privacy law (E-071) and the state of both memory systems were
re-read from the tree before anything was built. The law
itself lives in code at `Verdandi/memory_feed.py`; this
document is its reading copy. Conformance is pinned by
`tests/unit/test_memory_feed_e072.py`.*

## 1. Plain-language summary

Can the companion's diary — the conversation log — feed its
long-term memory? Yes, but only on the user's terms, stated
in advance, and never silently. Before this slice the honest
answer (E-063) was that nothing in the tree copied log
entries into memory at all, and the question was left open
on purpose. Now the road exists and it has a gate: a feed
runs only under a rule the user personally granted, naming
which sessions may feed and which kinds of entry may become
memory. Without that rule — or with it switched off, or
granted by a program instead of the user, or written in
terms the law does not recognise — nothing feeds, and the
feed says so. Every feed, successful or not, produces an
accounting: how many entries were seen, how many became
memory candidates, and how many were held back under each
named reason. The accounting is counts only, so showing it
can never leak what was in the diary. What this slice does
*not* do is choose a memory store: which system receives
the candidates is Part V's verdict (E-080), and reconciling
fed candidates with memory's own facts is E-085's work.
This law governs the crossing, not the destination.

## 2. The user's rule

A rule is a plain dict with exactly the keys the law names
(`memory_feed.RULE_KEYS`); unknown keys make it invalid —
a rule may not smuggle in terms the law does not name.

- `enabled` (bool, required) — a granted but disabled rule
  feeds nothing.
- `granted_by` — must be `"user"`. The decision to remember
  belongs to the user, as the delete right (E-063) does; a
  rule granted by a program, a default or another persona
  is invalid and feeds nothing.
- `scope` — `"named_sessions"` (with a non-empty
  `session_ids` list) or `"all_sessions"`. There is no
  default scope: an unscoped rule has not been stated.
- `event_types` — a non-empty subset of the feedable
  vocabulary (§3). Naming what may be remembered is part
  of the grant.
- `include_end_summary` (bool, default off) — whether a
  session's closing summary may also feed.
- `rule_id` (optional) — the user's name for the rule,
  carried into each candidate's provenance and each
  report, so any remembered fact can be traced to the rule
  that let it cross.

Validation is fail-closed and reports errors by field
name, never by content.

## 3. What may feed — and what never does

Of the logger's entry kinds (E-063), only two can carry a
memory:

- `event` entries of the feedable types: `learned` →
  category `lesson`, `decision` → `decision`, `milestone`
  → `milestone`; and of those, only the ones the rule's
  `event_types` names.
- `end` entries — their summary only, category
  `session_summary`, and only when the rule turns
  `include_end_summary` on.

Never, under any rule: the other event types
(`file_changed`, `action`, `blocker`, `blocker_resolved`,
`mood_shift` — working state, not memories), `start` and
`update` entries (a header and a state snapshot), empty
content, and entries with no session to attribute them to.
Within one feed run an exact repeat of an already-fed
(session, category, content) feeds once; repeats are
counted as duplicates, not silently doubled or dropped.

Each candidate is a new dict: source `conversation_logger`,
session id, timestamp, category, content, a persona tag
(§5), and provenance naming the log file, the entry kind,
the event type and the rule id.

## 4. Never silently — the report

`feed_candidates` always returns candidates *and* a
report. The report's status is one of `no_rule`,
`rule_disabled`, `invalid_rule` or `fed`, and it carries
the total seen, the number fed, and a count for every
withholding reason: `withheld_no_rule`,
`withheld_rule_disabled`, `withheld_invalid_rule`,
`withheld_unattributable`, `withheld_out_of_scope`,
`withheld_not_feedable`, `withheld_not_selected`,
`withheld_empty`, `withheld_duplicate`. Every entry that
does not feed is counted under exactly one reason. In
E-071's counts-only discipline, the report holds no entry
content, no session ids and no persona ids — the sentinel
fixture proves a fed entry's content appears nowhere in
its report.

## 5. Persona, deletion, and the honest limits

- **Persona.** Log entries carry no persona id. When the
  caller supplies the `session_owners` mapping (the same
  caller knowledge E-071 uses), candidates are tagged with
  their session's persona, preparing E-083's separation at
  the memory face. Without a mapping the tag is `None` —
  a persona is never guessed from content.
- **Deletion.** A session deleted under E-063's right
  leaves the log, so no later feed can draw from it; the
  live-logger conformance test proves exactly that. This
  law does **not** retract candidates already fed before a
  deletion. That propagation is memory's side of the
  boundary: new **docket 104**, owned by E-085 (memory ↔
  logger reconciliation), which must state how a deletion
  reaches already-fed memory or record why it cannot.
- **No store is written.** Candidates are an offer at the
  boundary, in the only lawful shape log material may
  cross in. mempalace, mimir-well and the core's Well are
  untouched by this slice; Part V's verdict (E-079/E-080)
  decides the receiving face, on top of this law.

## 6. Conformance — `tests/unit/test_memory_feed_e072.py`

- the module stdlib-only and standalone; the feedable
  vocabulary excludes the working-state event types;
- no rule, a disabled rule, a non-user grant and seven
  invalid-rule shapes each feed nothing and report why;
- a named-scope rule feeds only its named sessions and
  selected feedable types, with provenance pinned; the
  all-sessions scope feeds any session;
- working-state events, `start` and `update` entries never
  feed; an end summary feeds only when opted in;
- empty, duplicate and unattributable entries are counted,
  never silently passed over; the input is never mutated;
- the report is counts-only (sentinel content and a
  withheld session id absent from it);
- live entries written by the real logger in an isolated
  state dir feed through the law, and a session deleted
  under E-063 feeds nothing afterwards.

## 7. Slice gate

- New conformance suite: `tests/unit/test_memory_feed_e072.py`
  — **22 passed**.
- The combined conformance run (E-055 budget book, E-057
  pins, E-061–E-071 suites, plus the new suite): **234
  passed**.
- Verdandi focal suites (extras supplied, short TMPDIR):
  conversation set **101 passed**. The heartbeat focal set
  was NOT verified this tick: the keeper's focal run used
  a broader six-file set (adding eir_consolidation and
  skuld, outside the canonical four heartbeat files) and
  finished under extreme contention at 451 passed /
  6 failed, and a clean re-run of the canonical four files
  was starved at load ~17.9 and killed unverified. The
  earlier claim of "374 passed, identical" is withdrawn;
  the heartbeat set joins the Run D re-verification duty
  below. The broader run's failures (including
  test_heartbeat_integration's version-flag test and an
  eir YAML-layers test) are recorded for that re-check,
  not classified either way yet.
- Root gate Run B (default env, pgvector file excluded):
  **1273 passed, 6 failed, 25 skipped, 1 warning** — the 6
  are the proven environment failures, byte-identical set
  to E-071's Run B (verified by diff of the FAILED lists).
- Root gate Run D (extras supplied): three attempts under
  heavy cross-campaign VM contention (load average 3.0–9.3
  during the runs) — **1325–1326 passed, 19 skipped**, with
  the only failures in every attempt the contention-
  sensitive timing measurements: the four
  `test_idle_costs_nothing_over_the_window` parametrizations
  (a real CPU-tick measurement over a live window) and, in
  two of three attempts, the live-socket bridge test —
  which passed in isolation and in the second Run D
  attempt (1326 passed, 4 failed). No other test failed in
  any attempt, and no failing test touches this slice's
  code. Run D is therefore recorded as NOT GREEN under
  contention, with a standing re-verification duty: the
  next keeper tick re-runs Run D and records the result in
  the campaign state; a calm-load green Run D closes this
  note. Logs in `~/workspace/.verify-tmp/ember-e072/gate/`
  (`run_b.log`, `run_d.log`, `run_d2.log`, `run_d3.log`).
- E-057 table re-measured for the one changed member
  (Verdandi 191 files / 17,009,560 B; total 131,420,692 B;
  laptop miss 232,344 B), both published copies updated.
  No README touched.

*Filed by the E-072 slice, 2026-10-31. Next: E-073 —
Verdandi standalone: the hub usable without the full
companion.*
