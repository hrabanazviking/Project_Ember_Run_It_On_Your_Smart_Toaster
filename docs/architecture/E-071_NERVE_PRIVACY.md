# E-071 — Privacy of nerves: stimuli provenance never leaks across personae

*Part IV, slice E-071. Roadmap line: "Privacy of nerves:
stimuli provenance never leaks across personae (fixtures)."*

## In plain words

**One persona must never learn, from the nerves, where
another persona's touches from the world came from.** E-064
made every outside touch (a *stimulus*) carry *provenance*
— who or what produced it, and through which channel it
entered — so the system can always answer "where did this
come from?". E-025 made personae separate companions whose
memories never mix. This slice joins those two laws: a
persona looking at the nerves sees its own events (with
their provenance, whole) and the machine's system events —
and nothing that belongs to another persona. Another
persona's stimulus is not shown with its provenance blanked
out; it is *not shown at all*, because even the fact that
another persona was touched, at a certain time by a certain
kind of entrance, is that persona's private business.

## 1. How an event is bound to a persona

A binding is explicit, never guessed from content:

- `data.persona_id` — the core's own events (`ember_session`,
  `ember_turn`, E-067) carry it directly.
- A stimulus event (`stimulus:<name>`, E-064): 
  `data.payload.persona_id` first, then
  `data.provenance.persona_id` — a producer acting on behalf
  of one persona says so in one of those two places.
- A session binding: `data.session_id` (the conversation
  logger's `conv_*` events) or a stimulus's
  `data.payload.session_id` (`message.conversation`),
  resolved through a caller-supplied `session_owners`
  mapping of session_id → persona_id. The mapping is the
  caller's knowledge; the law invents none of its own.

Everything else is **system**: heartbeat pulses, health
checks, Hermes lifecycle events (which carry no persona at
all, E-068), and time/sensor stimuli with no persona or
session binding. A timer's origin is the schedule and a
check's origin is the machine — no persona's provenance —
so system events are visible to every persona, provenance
intact.

## 2. The law (in `Verdandi/nerve_privacy.py`)

For a persona-scoped view:

1. Bound to the asking persona → visible, whole, provenance
   intact.
2. Bound to a different persona → withheld entirely. Not
   redacted, not summarised, and its provenance values
   appear nowhere in the view or in the filter's report.
3. Session-bound (a `conv_*` shape, or a
   `message.conversation` stimulus) with **no known owner**
   → withheld, fail closed. An unowned session is not proven
   to be the asker's, and those shapes carry a person's
   words' session.
4. System → visible, provenance intact.

`filter_events_for_persona(events, persona_id,
session_owners=None)` returns the visible events unmodified
and in their original order, plus a **counts-only report**
(total / visible / withheld_cross_persona /
withheld_unknown_session, and the asker's own id) — no
withheld content, provenance, persona or session value can
appear in it, so withholding is auditable without becoming
a leak itself. The input is never mutated.

For unscoped aggregate views, `redact_provenance(event)`
returns a copy whose stimulus provenance origin — and the
event's top-level `source`, which E-064 sets to the origin —
are replaced by `"redacted"`, keeping only the channel (a
closed vocabulary; counts by channel are a system fact). A
persona binding inside provenance does not survive
redaction. Redaction is for operators counting across the
hub; persona-scoped views withhold instead.

## 3. The live enforcement: the core's read path

The law is filed standalone in `Verdandi/nerve_privacy.py`
(stdlib only, no member imports — the deployed-copy pattern
of E-061–E-070), and it is enforced on the one live
persona-facing read path the tree has: the Ember core's
nerve bridge. `src/ember/nerve.py` gains
`filter_for_persona` (the same classifications, carried
inline under that module's no-member-imports discipline,
pinned equal to `nerve_privacy` by the conformance tests
on every core/stimulus/conversation shape) and
`read_recent_for_persona(persona_id, …)`, which over-fetches
the hub tail (4×, mirroring `read_recent`'s own offline
over-fetch) so withholding does not silently shrink a
persona's view, then returns at most the requested count
of visible events plus the counts-only report. Chat does
not consume nerves yet (docket 102, E-076's review) — this
slice gives that future consumer its separation rule in
advance, already wired into the bridge it will read
through.

## 4. Fixtures

`tests/unit/test_nerve_privacy_e071.py` proves, with
synthetic personae (`persona-a` / `persona-b`) and sentinel
provenance strings that must never appear in another
persona's view or report:

- a persona's own `ember_session` / `ember_turn` events and
  its own bound stimuli are visible, provenance intact;
- another persona's events and stimuli are withheld
  entirely, sentinel provenance absent from both the
  serialised view and the report;
- system events (heartbeat pulse, a Hermes lifecycle event,
  a time stimulus) are visible to both personae;
- `conv_*` events follow their session owner; an unowned
  session is withheld fail-closed, while a `session_id` on a
  non-conversation shape is a correlation id, not a binding;
- stimulus bindings via payload and via provenance both
  hold; a `message.conversation` stimulus with an unknown
  session is withheld;
- redaction removes the origin/source/persona binding and
  keeps the channel, without mutating the input;
- the core bridge's inline copy classifies every fixture
  identically to `nerve_privacy`, and
  `read_recent_for_persona` over a feed file returns only
  the asking persona's view.

## 5. Honest limits

- The hub's feed itself is **not** encrypted, deleted or
  rewritten: the operator who owns the machine owns the
  record (the tether, E-020). This law governs
  persona-scoped *views*, which is where one persona could
  otherwise learn about another.
- Pre-E-071 stimuli with no persona/session binding are
  system-shaped by this rule: a binding cannot be invented
  retroactively for them. Producers that act for a persona
  must say so (payload or provenance `persona_id`, or a
  known session) for the law to bind their stimuli.
- Dockets 100–103 keep their E-076 owner unchanged; this
  slice creates no new docket items.
