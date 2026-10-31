# E-030 — Error honesty: failures are spoken, never fabricated

Roadmap slice E-030 (Part II): *"Error honesty: failures surface
as truthful plain messages; never a fabricated completion."*

## 1. The rule this slice enforces

A failure the operator cannot see is a lie of omission, and a
record that stores a failed or partial reply as if it were a
completed answer is a fabrication that later sessions will read
back as truth. E-030 audited every failure surface of a chat
session (`ember chat`, and `ember ask`, which rides it), fixed
the ones that were silent or mis-recorded, and pinned each fix
with tests (`tests/unit/test_error_honesty_e030.py`, **12
passed** in the default env).

## 2. What was silent, and what it says now

| Failure | Before E-030 | Now |
|---|---|---|
| An Episode cannot be saved (`add_episode` raises) | Exception suppressed in silence (`contextlib.suppress`); the session believed it was remembering when the store was not — **docket 85** | A plain warning at that moment — `[warning: this turn could not be saved to the Well (Type: message); it will be remembered only until this session ends.]` — and the session keeps serving with the turn in its in-memory window only. **Docket 85 CLOSED.** |
| The Well search fails mid-session (`hybrid_search` / `text_search` raises) | No hits, no signal; the prompt assembled exactly as for an honestly empty Well — **docket 86** | The operator is told for that turn (`[well: search failed for this message (…); the reply will not be grounded in your documents]`), the turn's prompt carries the do-not-invent instruction, and its Episode is flagged `well_disconnected` — the turn is ungrounded in fact, on screen, and in the record. The catch is broadened beyond `BrunnrError` to any exception, for the same stale-connection reason persistence already catches broadly. **Docket 86 CLOSED.** |
| Saved conversations cannot be loaded at startup (`recent_episodes` raises, E-021) | Reader failure suppressed in silence; the session started with an empty history and no word | A plain warning at startup — `[warning: your saved conversations could not be loaded (…); this session starts without them — they have not been deleted.]` — and the session serves from an empty in-session history. Found in this slice's audit and fixed in scope (it was the startup twin of docket 85/86). |

One distinction is kept deliberately, because collapsing it would
itself be a falsehood: **an embedding failure alone is not a
retrieval failure.** With no vector, retrieval degrades to text
search, whose hits are real search results; the turn is grounded
by them and no warning is owed. Only the search failing makes the
turn ungrounded. This is pinned by test.

## 3. Never a fabricated completion — the stored record

The screen already tagged a failed finish (`[ember reported an
error]`) and a cut-off one (`[reply truncated — context limit
reached]`). But the **Episode stored the bare text**, so a later
session reading its history back (E-021) met the error text — or
the partial answer — as `Ember: <text>`, indistinguishable from a
completed reply.

Now the persisted text carries the same tag the operator saw:
`chat._tag_failed_finish` prefixes `render.ERROR_TAG` to an
ERROR finish's text and appends `render.TRUNCATED_TAG` to a
LENGTH finish's text, on both the streaming and non-streaming
roads. (The two tags became named constants in `render.py`; the
rendered strings are byte-identical to before.) STOP, TOOL_CALL
and None finishes store unchanged, and REFUSED stores unchanged —
a refusal is a completed act whose text already says what it is.
An interrupted reply keeps its E-028 interrupt tag, which already
wins over finish tags.

## 4. Examined and already honest (no change)

- Funi unavailable at open → the session refuses with the reason
  named and exit 1 (E-020). A configured persona that cannot load
  → exit 1 with the reason, never a silent swap (E-025).
- The Well disconnected at open → banner, do-not-invent prompt
  instruction, `well_disconnected` Episodes (E-020/E-021).
- Backend failures inside a turn → typed ERROR replies/chunks
  with explanatory text from the Ollama and Aesir adapters, never
  raised, never invented prose (E-022/E-023).
- Tool failures → typed error `ToolReply`s rendered and audited;
  an audit-write failure warns on screen (`_safe_audit`); an
  approval-prompter failure warns and counts as "n" (E-026/27).
- Tool-loop cap → a printed note; approval-override typos → a
  startup warning naming the unknown tools.
- Ingest → failures return `Ingest failed: …` with exit 1, and
  the summary prints its `failed:` count beside the word
  "complete" — the count is the honesty.
- Session-close handle suppressions examined and kept: closing
  claims nothing to anyone, so there is nothing for it to lie
  about.

## 5. Honest limits

- The warnings name the exception type and message as the
  adapters produce them (`RuntimeError: disk full`, …) — truthful
  and specific, but still technician-shaped text inside plain
  framing sentences. Fully plain-worded error *causes* would need
  a cause taxonomy the adapters do not have; not invented here.
- A Funi adapter that *raises* instead of folding its failure
  into an ERROR reply (the contract every in-tree adapter
  follows) would still crash the turn — a loud failure, never a
  fabricated one, and the session record simply has no Episode
  for it. Making third-party adapters obey the contract is
  E-022's conformance surface, unchanged here.
- Docket 82 (the pending-episodes journal for disconnected
  sessions) is untouched and remains E-031's: a disconnected
  turn is honestly flagged, but it is still lost at exit, and
  E-030 does not pretend otherwise.

## 6. Tests and gate

- New: `tests/unit/test_error_honesty_e030.py` — **12 passed**
  (default env): save-failure warning ×2 turns + session lives;
  search-failure warning + do-not-invent prompt + Episode flag;
  low-level backend exception spoken via `_retrieve`; embedding
  failure degrading to real text hits; clean-search control (no
  warning, grounded Episode); history-load warning + session
  lives; ERROR and LENGTH finishes persisted tagged on both
  roads; STOP control untagged; `_tag_failed_finish` unit pins.
- Slice gate (E-017 method; logs in
  `~/workspace/.verify-tmp/ember-e030/`): Run B (default, pgvector
  file excluded) **773 passed, 6 failed, 14 skipped, 1 warning** —
  the E-029 baseline (761) + the 12 new; the 6 failures are the
  proven environment failures, identical to the freeze. Run D
  (whole, extras) **815 passed, 0 failed, 19 skipped, 1
  warning**, exit 0.
- No README touched. No production behaviour changed outside
  `spark/munnr/chat.py` and the tag constants in
  `spark/munnr/render.py`.
