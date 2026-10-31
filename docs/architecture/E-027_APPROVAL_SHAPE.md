# E-027 — Approval shape for normal folks

*Part II, slice E-027. Builds on E-026 (permission shapes + the
approval gate, `docs/architecture/E-026_TOOLS_DISCIPLINE.md`).
The gate decided **whether** Ember asks; this slice decides
**how it asks** — in words a non-technical person can act on.*

## Before E-027

The whole approval experience was two jargon surfaces:

- Munnr's `[tool proposal] <name>` block — the tool's internal
  name, its author-facing description, and a raw argument dump;
- the prompter's own second rendering of the same, ending
  `approve this call? [y/n/always]`.

And `always` was a quiet lie in two directions:

1. **It over-promised for gated calls.** The prompter offered
   `always` for every tool. For a dangerous or unspecified access
   class, or a call carrying a guarded argument, E-026's gate in
   `resolve()` asks per call *anyway* — the person's `always`
   produced `APPROVED_FOR_SESSION`, the name entered the session
   set, and the next call prompted again regardless. The grant
   was silently worthless.
2. **It was vague for safe calls.** Even where session standing
   is honoured, nothing said what "always" spanned: this tool or
   all tools? this chat or forever? (The truth: that tool, this
   chat session only — a restart forgets it.)

## What was built

One new module, `ember.spark.funi.tools.plain` — the single
place that turns E-026's permission shapes into ordinary words:

- **`plain_action(descriptor, call)`** — one sentence saying what
  Ember wants to do, built from the detail that matters. The
  first-party tools are pinned: search_well names the search
  words ("Search the things you have saved with Ember for …"),
  read_local_file names the file, fetch_url names the address.
  Any other tool falls back to its own (human-written)
  description. A redacted argument is never used in the sentence.
- **`plain_reach(descriptor)`** — the access class in ordinary
  words, one pinned sentence per class ("It reads your own
  information, on this computer only. It cannot change or delete
  anything, and nothing is sent anywhere." / "It goes out from
  your computer to the internet. …"). The class name itself never
  appears.
- **`plain_guarded_warning(descriptor, call)`** — when a call
  widens a tool's reach, the warning is plain too; fetch_url's
  `allow_private_addresses` is named for what it is: "reach
  private addresses on your own home network, not just the
  public internet".
- **The rememberable scopes** — `offered_choices()` returns the
  answers for *this* call, each with its meaning:
  - `y` — "Yes — just this once."
  - `always` — "Yes — and don't ask me again about this tool
    while we're chatting. (Forgotten when the chat ends; it is
    never forever.)" — offered **only** when `can_remember()`
    (exactly the E-026 gate's condition: a read-only class and
    no truthy guarded argument in this call).
  - `n` — "No — don't do it."
  - Where `always` is not offered, `why_asked_every_time()` gives
    the one-sentence plain reason per class ("Because this goes
    out to the internet, Ember asks about it every time — a yes
    here means just this once."), with the guarded-argument reason
    winning when a call widens reach.
- **`render_plain_proposal(descriptor, call)`** — the full
  prompt: "Ember is asking your permission." → what it wants to
  do → what it can and cannot do (+ the guarded warning) → the
  exact details it was given (redacted shown as `<hidden — Ember
  will not show this>`) → the choices with their scopes → the
  asked-every-time reason where one applies. Tests pin the
  absence of the jargon set (`per_call`, `standing`,
  `descriptor`, `ToolAccess`, `guarded_argument`, …).

## The prompter, rewired

`StdinApprovalPrompter` now writes `render_plain_proposal` and
accepts **only the offered answers** (`Your answer (y/always/n):`
or `(y/n):` as the call allows). Behaviours kept: EOF → `n`;
unknown answer → refused with a note. One behaviour changed,
deliberately: an `always` typed when it was not offered returns
`y` **with the reinterpretation stated on screen** — "That choice
can't be remembered for this kind of request, so I'll count it
as 'y' — yes for this once only." Nothing is silently
reinterpreted, and nothing the gate cannot honour is recorded as
a session grant (so chat's `session_added` bookkeeping now only
ever names tools the gate will actually skip for).

## The chat surface

`render.render_tool_call_proposal` keeps its technical header
(other render tests and the audit-shaped record rely on it) and
gains two plain lines under the description — `in plain words:`
(the action sentence) and `what it can reach:` (the reach
sentence) — so the proposal a person reads in the chat flow is
the same plain account the prompter gives.

## User docs

The Operator Playbook's Recipe 3 transcript — which showed the
old `[y/n/always]` prompt and described `always` as "session-
level standing trust" — is replaced with the real E-027 prompt
and the true scope wording, including the not-offered cases.

## Pinned tests updated, with attribution

- `test_funi_tools_approval.py`: the prompter tests asserted the
  old prompt strings ("tool proposal:", "approve this call?",
  `<redacted>`) and used an UNSPECIFIED descriptor for the
  `always` case; they now assert the plain prompt, the
  `<hidden …>` marker, and use a PRIVATE_READ descriptor for the
  remembered case.
- No other suite section moved: `resolve()` /
  `resolve_with_answer()` semantics are unchanged (an `always`
  answer still maps to `APPROVED_FOR_SESSION` — it is the
  *prompter* that now only produces that answer where it is
  offered, plus the stated one-time-yes fallback).

## Honest limits

- The plain action sentences are hand-written for the three
  first-party tools; a future tool gets its description verbatim
  until someone writes it a sentence. The reach sentence is
  class-driven, so every tool — including MCP-bridged ones
  (EXTERNAL) — is plain about its reach from day one.
- "While we're chatting" is the widest scope a prompt answer can
  grant, by design. Remembering across restarts stays where it
  already lives: the operator's own config (`standing_trust`,
  per-tool overrides), set deliberately outside the chat — and,
  per E-026, still powerless for dangerous/guarded calls.
- Hjarta's setup flow does not prompt for tool approvals and is
  untouched; there is no graphical prompt surface in the tree to
  convert (the Stranger Test, Part XII, judges this surface).

## Tests

New `tests/unit/test_plain_approval_e027.py` — **38 passed**
(plain actions ×5, plain reach ×7 classes, guarded warnings ×3,
scope offering ×7, asked-every-time reasons ×7, rendered prompt
×3, prompter ×4, renderer ×1, schema guard ×1 — counted from the
runner). Slice gate (E-017 method; TMPDIR on the workspace
overlay): Run B (default env, pgvector file excluded) **746
passed, 6 failed, 13 skipped, 1 warning** — the 708 E-026
baseline + the 38 new; the 6 are the proven environment
failures. Run D (whole, extras) **787 passed, 0 failed, 19
skipped**, exit 0. No README touched.
