#!/usr/bin/env python3
"""
Verdandi Nerve Privacy — stimuli provenance never leaks
across personae.

Filed by Project Ember slice E-071 (docs/architecture/
E-071_NERVE_PRIVACY.md). This module IS the privacy law in
code, in the same shape as event_contract.py (E-061),
stimuli.py (E-064) and replay.py (E-069): stdlib only, no
imports from any other Verdandi module, so the discipline
stands alone wherever a copy is loaded file-by-file. The
Ember core's nerve bridge (src/ember/nerve.py) carries the
same rule inline for its own read path — the core does not
import Verdandi (E-067) — and the E-071 conformance tests
pin the two copies' verdicts equal on the core's shapes.

THE PROBLEM IT SOLVES

E-064 made provenance mandatory for stimuli: every outside
touch names its origin and channel, and that provenance
survives the feed, the ring and every reader — deliberately,
so the question "where did this come from?" can always be
answered. E-025 made personae separate companions: one
persona's episodes never ride in another's prompts. Between
those two laws sat a leak. A persona-scoped reader of the
nerves (a context builder, a future chat consumer per
docket 102, an operator tool filtered for one persona)
could receive EVERY event on the hub, including stimuli
bound to a different persona — and a stimulus's provenance
(origin, channel, timing) is itself private: it can name
the session, job or channel through which another persona
was touched by the world. Recording provenance so it can be
governed (E-064) must never become recording it so it can
leak (this slice).

HOW AN EVENT IS BOUND TO A PERSONA

A binding is explicit, never guessed from content:

- ``data.persona_id`` — the core's own events (ember_session,
  ember_turn, E-067) carry it directly.
- A stimulus event (``stimulus:<name>``, E-064 shape, in
  ``data``): ``data.payload.persona_id`` first, then
  ``data.provenance.persona_id`` — a producer that touches
  the world on behalf of one persona says so in one of
  those two places.
- A session binding: ``data.session_id`` (the conversation
  logger's conv_* events) or a stimulus's
  ``data.payload.session_id`` (message.conversation),
  resolved through a caller-supplied ``session_owners``
  mapping of session_id -> persona_id. The mapping is the
  caller's knowledge (the logger's own records); this
  module invents no mapping of its own.

Everything else is SYSTEM: heartbeat pulses, checks, Hermes
lifecycle events (which carry no persona at all, E-068),
time/sensor stimuli with no persona or session binding.
System events carry no persona's provenance — a timer's
origin is the schedule, a check's origin is the machine —
so they are visible to every persona, provenance intact.

THE LAW

For a persona-scoped view (one persona asking "what may I
see?"):

1. An event bound to that persona is visible, whole —
   its provenance intact. A persona may always see where
   its own touches came from.
2. An event bound to a DIFFERENT persona is withheld
   ENTIRELY — not redacted, not summarised. A redacted
   copy would still leak that the other persona was
   touched, when, and by what kind of stimulus; the
   provenance values must not appear anywhere in the
   view or in this module's report.
3. A session-bound event whose session has NO known
   owner is withheld from persona-scoped views (fail
   closed): a conv_* event or a message.conversation
   stimulus carries a person's words' session, and an
   unowned session is not proven to be the asker's.
   System stimuli are never session-bound in this sense —
   only the conversation shapes named in
   SESSION_BOUND_TYPES / SESSION_BOUND_STIMULI are.
4. A system event is visible, provenance intact.

THE REPORT

``filter_events_for_persona`` returns the visible events
in their original order plus a report: counts only —
total, visible, withheld_cross_persona,
withheld_unknown_session. The report contains no event
content, no provenance values, no persona ids other than
the asker's, and no session ids. Withholding is therefore
auditable without itself becoming a leak.

REDACTION (for unscoped aggregate views)

``redact_provenance`` returns a copy of an event with any
stimulus provenance replaced by
``{"origin": "redacted", "channel": <original channel>}``
and a top-level stimulus ``source`` replaced by
``"redacted"`` — the channel (how a thing entered, a
closed vocabulary) survives because aggregate counts by
channel are a system fact; the origin (who or what
specifically produced it) does not. Persona-bound events
should be withheld, not redacted, for persona-scoped
views; redaction exists for operators counting across
the whole hub without carrying anyone's provenance into
a report.

WHAT THIS DOES NOT DO

It does not encrypt, delete or rewrite the feed: the hub's
record stays whole for the operator who owns the machine
(the tether, E-020 — custody of the folder is custody of
the companion). Privacy here governs persona-scoped VIEWS
of the nerves, which is where one persona could otherwise
learn about another. It does not retroactively bind old
feed lines: a pre-E-071 stimulus with no persona/session
binding is system-shaped by the rule above, stated as the
honest limit in the E-071 doc. And it does not decide
docket 102 (whether chat consumes nerves at all) — it
gives any such consumer its separation rule in advance.
"""

import copy

PRIVACY_VERSION = 1

# The conversation shapes that carry a session's words and
# are therefore session-bound (fail closed when unowned).
SESSION_BOUND_TYPES = ("conv_start", "conv_event", "conv_update", "conv_end")
SESSION_BOUND_STIMULI = ("message.conversation",)

REDACTED = "redacted"


def _data(event):
    if isinstance(event, dict) and isinstance(event.get("data"), dict):
        return event["data"]
    return {}


def _event_type(event):
    if not isinstance(event, dict):
        return None
    typ = event.get("type") or event.get("event_type") or event.get("event")
    return typ if isinstance(typ, str) else None


def is_stimulus_event(event) -> bool:
    """True for an E-064 stimulus event (``stimulus:<name>``)."""
    typ = _event_type(event)
    return bool(typ and typ.startswith("stimulus:"))


def stimulus_of(event):
    """The stimulus dict inside a stimulus event, or None."""
    if not is_stimulus_event(event):
        return None
    data = _data(event)
    if not isinstance(data.get("payload"), dict):
        return None
    return data


def event_persona(event, session_owners=None):
    """The persona an event is bound to, or None if system.

    Bindings are explicit only (see the module docstring):
    data.persona_id, then a stimulus's payload/provenance
    persona_id, then a session binding resolved through
    ``session_owners``. An unresolvable session binding
    returns None here — callers that need the fail-closed
    distinction use :func:`classify_event`, which reports
    it as ``unknown_session`` rather than ``system``.
    """
    cls, persona, _reason = classify_event(event, session_owners)
    if cls in ("own", "cross"):
        return persona
    return None


def classify_event(event, session_owners=None, persona_id=None):
    """Classify an event for a persona-scoped view.

    Returns ``(classification, bound_persona, reason)`` where
    classification is one of:

    - ``"own"``     — bound to ``persona_id`` (or bound at
                      all, when ``persona_id`` is None)
    - ``"cross"``   — bound to a different persona
    - ``"unknown_session"`` — session-bound, owner unknown
    - ``"system"``  — no persona/session binding

    ``bound_persona`` is the bound persona id or None; the
    reason is a short stable string for tests and reports.
    """
    owners = session_owners or {}
    data = _data(event)
    typ = _event_type(event)

    # 1. A direct persona binding.
    direct = data.get("persona_id")
    stim = stimulus_of(event)
    if stim is not None:
        payload = stim.get("payload") or {}
        prov_raw = stim.get("provenance")
        prov = prov_raw if isinstance(prov_raw, dict) else {}
        if not isinstance(direct, str) or not direct:
            direct = payload.get("persona_id") or prov.get("persona_id")
    if isinstance(direct, str) and direct:
        if persona_id is None or direct == persona_id:
            return ("own", direct, "persona_id")
        return ("cross", direct, "persona_id")

    # 2. A session binding.
    session_id = data.get("session_id")
    session_bound = typ in SESSION_BOUND_TYPES
    if stim is not None:
        payload = stim.get("payload") or {}
        if session_id is None:
            session_id = payload.get("session_id")
        if stim.get("name") in SESSION_BOUND_STIMULI:
            session_bound = True
    if session_bound:
        if isinstance(session_id, str) and session_id in owners:
            owner = owners[session_id]
            if persona_id is None or owner == persona_id:
                return ("own", owner, "session_owner")
            return ("cross", owner, "session_owner")
        return ("unknown_session", None, "session_unowned")
    # A session_id on a non-conversation shape is a
    # correlation id, not a binding (e.g. a check that
    # names the session it checked) — not bound.

    # 3. No binding: system.
    return ("system", None, "unbound")


def visible_to_persona(event, persona_id, session_owners=None) -> bool:
    """True when ``persona_id``'s scoped view may see ``event``."""
    cls, _persona, _reason = classify_event(event, session_owners, persona_id)
    return cls in ("own", "system")


def filter_events_for_persona(events, persona_id, session_owners=None):
    """The persona-scoped view of ``events`` + a counts-only report.

    Visible events are returned unmodified, in their
    original order; the input is never mutated. The report
    carries counts and the asker's id only — no withheld
    event's content, provenance, persona or session values
    appear in it.
    """
    visible = []
    withheld_cross = 0
    withheld_unknown = 0
    for event in events:
        cls, _persona, _reason = classify_event(event, session_owners, persona_id)
        if cls in ("own", "system"):
            visible.append(event)
        elif cls == "cross":
            withheld_cross += 1
        else:
            withheld_unknown += 1
    report = {
        "privacy_version": PRIVACY_VERSION,
        "persona_id": persona_id,
        "total": len(events),
        "visible": len(visible),
        "withheld_cross_persona": withheld_cross,
        "withheld_unknown_session": withheld_unknown,
    }
    return visible, report


def redact_provenance(event):
    """A copy of ``event`` with stimulus provenance redacted.

    The provenance origin (and a stimulus event's top-level
    source, which E-064 sets to the origin) become
    ``"redacted"``; the channel survives. Non-stimulus
    events are returned as an unchanged copy. The input is
    never mutated.
    """
    result = copy.deepcopy(event)
    if not is_stimulus_event(result):
        return result
    data = _data(result)
    prov = data.get("provenance")
    if isinstance(prov, dict):
        channel = prov.get("channel")
        new_prov = {"origin": REDACTED}
        if isinstance(channel, str) and channel:
            new_prov["channel"] = channel
        # A persona binding inside provenance is provenance
        # too: it does not survive redaction.
        data["provenance"] = new_prov
    if isinstance(result.get("source"), str):
        result["source"] = REDACTED
    return result
