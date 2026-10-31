# E-054 — Graceful smallness: shedding features at budget's edge, announcing each shed

*Part III, slice E-054. Roadmap line: "at budget's edge the
companion sheds features by the stated ladder, announcing
each shed." The ladder lives in `ember.smallness`; the
wiring is the chat turn (`ember.spark.munnr.chat`); the
gate tests are `tests/unit/test_smallness_e054.py`.*

## In plain words

**When Ember starts running out of room on a small
machine, it now gives things up in a set order — and it
tells you each time.** Until now the budget book (E-041)
said what a turn may cost, but nothing in the companion
*reacted* when a live process crept toward that limit: it
would keep paying for every comfort it owns until the
machine itself decided what died — on a tiny host, that
decision belongs to the operating system's out-of-memory
killer, and it does not explain itself.

Now the companion watches its own memory use against its
profile's turn budget. At **three quarters** of the
budget it stops composing summaries of the earlier
conversation. At **nine tenths** it also drops to
plain-word memory search (and skips the embedding work
entirely). At the **ceiling itself** it also narrows what
it keeps in mind to the smallest profile's allowance —
the most recent few exchanges. Everything is still
*answered* and still *saved*; only comforts are shed.
Each shed is announced in plain words, on screen and in
the diary, at the moment it happens — and when room
returns, each restore is announced too, so nobody is left
believing a feature is gone that has quietly come back.

One honesty line up front: the ladder judges the
*process's* resident memory, which is the right measure
for the shipped shape — `ember chat` is its own process,
and E-041's anchors were measured on exactly such
processes. A host that embeds Ember as a library inside a
larger process shares that process's memory with the
ladder; §4 records the seam the chat loop grew for
exactly this reason, and the defect it fixed.

## 1. What existed before (audited this slice)

- The budget book (`ember.budgets`, E-041) states
  per-profile turn-RAM ceilings and `check_against`
  judges *measured shapes after the fact* — nothing read
  a live process's memory or changed a live turn.
- A search of `src/ember` for shedding / degradation
  ladders found only per-failure degrades (a failed embed
  falls back to text search, E-029/E-030; a failed search
  marks the turn ungrounded). No budget-driven shedding
  existed.
- The three things the ladder sheds all had real,
  separately-tested shapes already: history summarisation
  is a conversation-config flag (E-021); text-only search
  is the existing no-vector retrieval path (E-029); the
  history window is built from the conversation config's
  resolved caps (E-021). The slice wires a judge in front
  of those shapes; it invents no new degradation shapes.

## 2. The ladder, as stated in `ember.smallness`

Reading: the process's own `VmRSS` from
`/proc/self/status` (stdlib only). An unreadable gauge
reads `None` and **never votes** — nothing sheds on a
memory figure that could not be taken (the E-051/E-053
unknown-signal rule).

Judging (pure `assess`): the reading over the profile's
turn-RAM ceiling from the budget book — toaster 64 MiB,
phone 128, pi 192, laptop 384:

| Level | Fraction of ceiling | Sheds (cumulative) |
|---|---|---|
| COMFORTABLE | < 0.75 | — |
| EDGE | ≥ 0.75 | history summaries |
| STRAINED | ≥ 0.90 | + semantic retrieval |
| OVER | ≥ 1.00 | + wide history window |

The ladder, cheapest to lose first, each rung with its
one plain announcement sentence (pinned verbatim in the
module and the tests):

1. **History summaries** — the extractive summary of
   dropped history is extra composition work per turn.
   The window still *reports* what it dropped; only the
   summary is not composed. *"I'm getting close to my
   memory limit on this machine, so I've stopped writing
   summaries of our earlier conversation — nothing is
   lost, and everything is still saved."*
2. **Semantic memory search** — the turn's question is
   no longer embedded; memory search runs on plain words
   (the existing text shape), which also saves the embed
   call itself. *"To stay within my memory limit, my
   memory search is using plain words only for now —
   some subtler matches may be missed."*
3. **The wide history window** — the history riding in
   the turn narrows to the book's smallest allowance
   (toaster: 512 tokens / 3 episodes), or stays at the
   operator's own caps when those are already smaller —
   narrowing never widens an operator override.
   *"To stay within my memory limit, I'm keeping only
   our most recent few exchanges in mind for now —
   everything is still saved."*

**Never shed, at any level:** answering the turn, saving
the turn to memory, the announcements themselves, and
tool approval / safety discipline. A shed is not sticky:
the guard is consulted per turn, restores arrive as room
returns, and each restore carries its own sentence
("I have room again, so …"). Announcements fire only on
change — a long session at the edge does not repeat
itself every turn.

## 3. The wiring (the chat turn)

`chat.run` builds a `SmallnessGuard` for the session's
conversation profile; its announcer writes
`[room: <sentence>]` to the person's screen and records
the same sentence in the diary (E-034). Once per turn,
before any priced work runs, the turn consults the guard:

- rung 2 → `_retrieve(..., text_only=True)`: the embed
  call is skipped entirely and `text_search` runs — not
  a failed embed dressed up, a deliberate plain-words
  search through the same honest path E-029 proved;
- rungs 1 + 3 → `window_history` is built under
  `plan.conversation_config(config.conversation)`: with
  no sheds that returns the config object unchanged, so
  a comfortable turn is byte-for-byte the pre-E-054
  shape.

**Deliberately not wired:** bulk background ingest.
An embed batch shed mid-job would return `None` vectors
whose chunks the ingest journal counts as failed while
still marking their document *done* — the chunks would
be lost, not deferred (read in
`well/smidja/local_files/source.py` this slice). Background
work keeps its own manners (E-051 patience, E-053 duty
cycling); this ladder governs the live companion's
features, and the record says so rather than wiring a
shed that silently eats data.

## 4. The defect the gate found, and its fix

The first full gate run failed one test beyond the six
proven environment failures:
`test_conversation_e021.py::test_chat_windows_loaded_history_under_tiny_budget`.
That test runs chat under the **toaster** profile inside
the pytest process, whose resident memory (the harness's,
~100 MiB-class under the suite) is over the toaster's
64 MiB ceiling — so the ladder, doing exactly what it
states, shed the history summary the E-021 test asserts.
The coupling is a real defect, not a test nuisance: any
host process embedding the chat loop (the E-037 library
shape) would inherit sheds driven by the *host's* memory,
and any suite's assertions about summaries would go
non-deterministic with harness size.

Fix, in scope: `chat.run` gains a `smallness_guard` test
seam beside its existing seams (`funi_opener`,
`strengr_opener`, `embed_client`). Injected, the guard
judges by its own assessor; absent, the shipped process
builds the real one. The E-021 chat helper pins a
comfortable guard with a comment naming this slice (its
subject is windowing; E-054's own tests pin the ladder,
including two full chat runs — at the ceiling and
comfortable — through this same seam's construction
path). No assertion in the E-021 test was changed.

## 5. The ladder, driven live on the VM

Method: a fresh process imports the full chat surface
(the E-041 idle shape, 24.3 MiB RSS — beside E-041's
25.3 MiB CLI-surface anchor), then holds memory in steps
while a `SmallnessGuard` for the **toaster** profile
(64 MiB ceiling) is consulted after each step. Scripts
and raw JSON in `~/workspace/.verify-tmp/ember-e054/`
(`probe.py`/`probe.json` at 8 MiB steps, `probe2.py`/
`probe2.json` at 4 MiB steps); VM heavily contended by
sibling campaigns — RSS here is the probe's own, which
contention does not inflate.

4 MiB-step run (the finer pass):

| Held | RSS (MiB) | Fraction | Level | Announcements so far |
|---|---|---|---|---|
| base | 24.29 | 0.380 | comfortable | 0 |
| +20 MiB | 44.30 | 0.692 | comfortable | 0 |
| +24 MiB | 48.31 | 0.755 | **edge** | 1 (summaries) |
| +32 MiB | 56.32 | 0.880 | edge | 1 |
| +36 MiB | 60.32 | 0.943 | **strained** | 2 (+ semantic) |
| +40 MiB | 64.33 | 1.005 | **over** | 3 (+ wide history) |

Every line crossed in ladder order, exactly one
announcement per rung, no repeats at steady levels. The
8 MiB-step run crossed the strained band inside a single
allocation step and announced rungs 2 and 3 together at
the first consultation that saw them — the guard speaks
for what changed since the last consult, in ladder
order; it does not invent intermediate states it never
observed.

## 6. Gate

- New tests: `tests/unit/test_smallness_e054.py` —
  **15 tests**: policy lines pinned; plans shed a ladder
  prefix; RSS reading (parse / missing / garbage);
  unknown never votes; levels cross in order at the
  exact lines; ceilings read from the book (the same
  63 MiB is strained on toaster, comfortable on laptop);
  config narrowing (identity when unshed, summaries-only
  at edge, smallest allowance at over, operator override
  never widened); guard announcement sequence (shed,
  steady-silence, restore in ladder order); a real-process
  guard consult; and two full chat runs (at the ceiling:
  all three announcements in order on screen *and* in the
  diary, embed never called, text search ran, the turn
  still answered and saved; comfortable: no announcement,
  hybrid search, turn saved).
- Slice gate Run B (default env, pgvector file excluded):
  **1032 passed, 6 failed, 25 skipped, 1 warning** —
  1017 E-053 baseline + 15 new; the 6 are the proven
  environment failures, identical set.
- Slice gate Run D (whole, extras): **1089 passed,
  0 failed, 19 skipped, 1 warning**, exit 0 — 1074 + 15,
  reconciles exactly. (Logs in
  `~/workspace/.verify-tmp/ember-e054/gate/`.)
- No defect left unfixed: the §4 coupling was found by
  this slice's gate and fixed inside it. No new docket
  items. No README touched.
- E-055 next — the budget book published in-repo with
  its measurements.
