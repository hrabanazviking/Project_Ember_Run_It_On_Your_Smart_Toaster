# E-062 — Context Injection Discipline: What May Be Injected, When, With What Budget

*Part IV, slice E-062. Starting HEAD: 801bf77's parent 8c946b5
(E-061 banked + push-recorded). Method: the injector and the
context builder were re-read from code this slice — E-059 §5
was the starting claim, and its central finding (each layer
item-capped, nothing measuring the total) was re-proven line
by line before anything was changed. The discipline itself
lives in code at `Verdandi/context_budget.py`; this document
is its reading copy. Conformance is pinned by
`tests/unit/test_context_injection_e062.py` (18 tests, §7).*

## 1. Plain-language summary

Before this slice, the block of old context that gets handed
to a new job had good manners piecemeal — summaries shortened,
lists trimmed — but no overall size limit, and a few of its
lists had no limit at all: every blocker ever recorded, each
as long as it liked, went in whole. On a tiny machine, and in
a small model's attention, that is how a helpful brief becomes
a flood. Now the injection has a written discipline. Only four
named sources may feed it, all from the companion's own state
folder. The whole block can never exceed 4000 characters.
Every list is capped in count *and* in length, every layer has
its own ceiling, and when something must be shed the least
important layer goes first — reaction suggestions, then the
nerve tail, then older sessions — while the current state's
blockers are the last thing ever dropped. Nothing is shortened
in secret: wherever the budget cut something, the block itself
carries the marker `[... truncated by context budget E-062]`.
Two quiet defects were found and fixed on the way: the nerve
tail and the reaction layer were read from a second hardcoded
home path instead of the logger's own state folder (so they
could silently read a different machine-state than the log
they accompany), and the injector's own echo of the current
state repeated blockers and actions with no caps at all,
defeating the budget of the block printed just above it.

## 2. What may be injected — the only sources

The block built by `conversation_logger.get_context_for_cron`
(and printed by `context_injector`'s default / `context`
commands) may draw on exactly four sources, all inside the one
state dir (`STATE_DIR`, default `~/.hermes/state`):

1. **Current state** — `current.json`: session id, status,
   last updated, summary, blockers, decisions, next actions,
   projects touched.
2. **Recent session summaries** — `conversation_log.jsonl`:
   one line per session (timestamp, session id, summary).
   Full log entries and event contents beyond the summary
   line are not injected.
3. **Nerve feed tail** — `nerve_feed.jsonl`, read from the
   *file* (never a live hub query, so injection works with
   the hub down and can never block on it): the last events,
   one short line each, under the E-061 event contract.
4. **Reaction directives** — `reactor.react()` output derived
   from the same log: priority, action, detail, capped items.

Nothing else: no environment variables, no config files, no
file contents from outside the state dir, and no
credential-shaped material — E-093's custody law starts here:
a secret that is never in the log can never be injected, and
log writers must never log one. The allowed file names are
pinned in `context_budget.ALLOWED_SOURCE_FILES` and by test
against the builder's actual reads.

**When:** once, at the start of a cron/companion job, as a
starting brief. This discipline authorises no mid-session
re-injection and no injection into a human's ordinary chat.

## 3. The budget (characters, verified without a tokenizer)

| Scope | Ceiling |
|---|---|
| Whole block (header + footer included) | **4000** chars |
| Current-state layer | 1200 chars |
| Recent-sessions layer | 700 chars |
| Nerve-feed layer | 1000 chars |
| Reactions layer | 1100 chars |

The layer ceilings sum to the total (4000), so no layer can
starve the others by construction. Per-item caps inside the
layers:

- summary ≤120 chars; recent summaries ≤100 chars;
- decisions ≤5 items, next actions ≤5 items, blockers ≤10
  items, projects ≤10 items; list items ≤120 chars each,
  project items ≤60;
- each rendered list line is *also* capped as a whole
  (blockers 600, decisions 300, next actions 300, projects
  300 chars) — so blockers at full per-item allowance plus
  the scalar lines always fit the current layer alone, and
  line-shedding can never be forced to drop blockers just
  because every item used its full allowance;
- recent sessions: the caller's `max_sessions` is a request,
  clamped to ≤5;
- nerve tail: ≤10 events, data ≤100 chars, source ≤60,
  type ≤60 per event;
- reactions: ≤6 directives, ≤3 items per directive, items
  and details ≤120 chars.

**Shedding order** (whole lines first, never mid-word except
as a last resort for a single over-long line): reactions
shed first, then nerve (its oldest events first, keeping the
newest), then recent sessions (oldest first); the current
layer sheds last, and inside it the field order — identity /
summary, blockers, decisions, next actions, projects — means
projects shed first and blockers last. Every shed or
truncation leaves the marker in the block.

**Failure discipline, unchanged in spirit and now stated:**
the nerve and reaction layers are supplementary and stay
failure-silent — a missing or broken source yields no layer,
never an error and never a fabricated one. The primary layers
(current, recent) come from the log's own state.

## 4. What changed in code

- **New: `Verdandi/context_budget.py`** — the discipline in
  code, stdlib-only and self-contained like
  `event_contract.py` (the deployed conversation layer loads
  modules file-by-file, so the budget must stand alone):
  the ceilings, the shed order, the allowed sources, and the
  `truncate_text` / `cap_items` helpers.
- **`Verdandi/conversation_logger.py`** — `get_context_for_cron`
  rebuilt in layers under the budget: the budget literals live
  here as plain literals (not imports, for the same deployed-
  standalone reason E-061's version literal lives in
  `nervous_system.py`), pinned equal to `context_budget.py` by
  the conformance tests. Three fixes ride with it:
  (a) the nerve tail is read from `STATE_DIR / nerve_feed.jsonl`
  and the reactor is loaded from `STATE_DIR` — previously both
  used a second hardcoded `Path.home() / .hermes / state`,
  identical only while `STATE_DIR` kept its default, and
  silently divergent (a different state than the log's) for
  any redirected state dir, which is exactly the shape the
  test suites and sandboxed runs use;
  (b) blockers and projects, previously uncapped in count and
  length, are capped like every other list;
  (c) the caller's `max_sessions` is clamped to the budget.
- **`Verdandi/context_injector.py`** — its default command's
  extra `=== CURRENT STATE ===` echo now applies the same
  caps (it previously printed blockers and next actions
  unbounded, directly under the budgeted block).

## 5. What this slice did NOT do

- No source was added or removed: the four layers are the
  four E-059 mapped. Persona separation of injected content
  is E-071's (privacy of nerves), not smuggled in here.
- The reactor's own analysis is untouched — its ignored
  `focus` parameter is docket 95, owned by E-065; this slice
  caps what injection *takes* from it.
- The logger's write path (E-063's law) and the hub are
  untouched. No README touched; no budget-book ceiling moved.
- One bookkeeping consequence, handled in this slice: adding
  `context_budget.py` and reworking two Verdandi files changed
  Verdandi's tracked weight, so the E-057 member budget table
  was re-measured and updated in both published copies, as its
  pinning tests require — Verdandi now 181 files /
  16,852,579 B (was 180 / 16,837,498 B), the twelve-member
  total 131,246,538 B (was 131,231,457 B), Verdandi's miss of
  the laptop ceiling 75,363 B (was 60,282 B); the re-measure
  is noted in the E-057 record itself. Verdandi's profile
  verdict is unchanged (none), and no RAM floor was
  re-measured.

## 6. Docket

No new docket items. The two defects fixed in §4 were found
and fixed inside this slice's own subject (the injector's
rules), per the never-leave-a-bug rule; neither predates
E-059's map, which recorded the hardcoded home path as the
deployment shape (§3 there) without judging the divergence —
the judgement and the fix are this slice's.

## 7. Conformance — `tests/unit/test_context_injection_e062.py`

18 tests, all passing this slice (§8), pinning:

- the budget's shape: layer ceilings sum to the 4000 total,
  shed order reactions > nerve > recent > current, the
  allowed-source list is exactly the three state files, the
  module is stdlib-only and imports neither the logger nor
  the reactor;
- the logger's deployed literals equal the module's values,
  field by field (23 pairings);
- the builder reads the nerve feed from its own `STATE_DIR`
  (source pin: no `Path.home()` remains in the function) and
  the injector's echo block uses the caps;
- behaviour under adversarial fixtures in an isolated state
  dir: blockers/decisions/next-actions/projects capped in
  count, per-item length and joined length; a `max_sessions`
  request of 50 clamped to 5 recent lines; a 25-event nerve
  flood trimmed to the newest 10; a flooding reactor (9
  directives × 9 huge items — proven live against a reactor
  placed in the state dir, the deployed shape) capped with
  the total intact; the full adversarial load together —
  5000-char summary, 40 huge blockers, 20 huge decisions and
  actions, 30 huge projects, 12 sessions, 25 huge nerve
  events — yields a block of at most 4000 chars that still
  carries its blockers, and the truncation marker appears
  wherever the budget cut.

## 8. Slice gate

- New conformance suite: `tests/unit/test_context_injection_e062.py`
  — **18 passed** (runner output in
  `~/workspace/.verify-tmp/ember-e062/`).
- Verdandi focal suites, re-run this slice with the declared
  dev dependency (pytest-asyncio) supplied from the campaign's
  isolated e005-extras dir and a short TMPDIR (the nerve hub's
  Unix-socket paths cannot live under the deep overlay TMPDIR
  — socket paths cap at ~108 chars; with the overlay TMPDIR
  the hub tests fail identically on the unmodified tree,
  proven this slice by a stash-and-rerun): the
  conversation-layer set (context_injector + conversation_logger
  + reactor + nervous_system) **101 passed**, exit 0 —
  identical to E-059's and E-061's banked focal count for the
  same set.
- Root suite gate: Run B **1094 passed, 6 failed, 25 skipped,
  1 warning** (1076 E-061 baseline + 18 new; the 6 are the
  proven environment failures, identical set); Run D
  **1151 passed, 0 failed, 19 skipped, 1 warning**, exit 0
  (1133 + 18 — reconciles exactly). The first Run B attempt in
  this slice's working session caught the E-057 member-budget
  tests failing on this slice's own Verdandi weight change —
  fixed in scope by the re-measure in §5, after which both
  gate shapes reconcile. Logs in
  `~/workspace/.verify-tmp/ember-e062/gate/`.

*Filed by the E-062 slice, 2026-10-31. Next: E-063 — the
conversation logger's law.*
