#!/usr/bin/env python3
"""
Verdandi Memory Feed — logged conversations may feed memory
only under the user's explicit rule, and never silently.

Filed by Project Ember slice E-072 (docs/architecture/
E-072_LOGGER_AS_MEMORY_SOURCE.md). This module IS the feed
law in code, in the same shape as logger_law.py (E-063) and
nerve_privacy.py (E-071): stdlib only, no imports from any
other Verdandi module, because deployed copies of the
conversation layer are loaded file-by-file and this law must
stand alone.

THE QUESTION IT SETTLES

E-063 wrote the conversation logger's law and left one
question open on purpose: whether logged conversations may
feed long-term memory. The answer is yes — but only under
the user's rule, stated in advance, and never silently.
Today nothing in the tree copies log entries into either
memory system (E-063 §4), and Part V (E-077–E-092) has not
yet chosen the one memory face (E-080) or reconciled the
logger's records with memory's facts (E-085). So this law
governs the FEED — the offer of memory candidates drawn
from the log — and writes nothing into any memory store
itself. The candidates it produces are the only lawful
shape in which log material may cross toward memory; which
store receives them is Part V's verdict, taken on top of
this law, never around it.

THE USER'S RULE

A feed runs under a rule: a plain dict the user (and only
the user) grants, with exactly these keys:

- ``enabled`` (bool, required) — a granted rule that is not
  enabled feeds nothing.
- ``granted_by`` (required) — must be the string ``"user"``.
  A rule granted by a program, a default, or another
  persona feeds nothing: the decision to remember is the
  user's, in the same way the delete right (E-063) is.
- ``scope`` (required) — ``"named_sessions"`` (only the
  sessions listed in ``session_ids``) or ``"all_sessions"``
  (every session in the log). There is no third scope and
  no default scope: an unscoped rule is an invalid rule.
- ``session_ids`` — required and non-empty when the scope
  is ``"named_sessions"``; meaningless (and rejected) when
  the scope is ``"all_sessions"``.
- ``event_types`` (required, non-empty) — the event kinds
  the user allows to become memory, a subset of the
  feedable vocabulary below. Naming them is part of the
  grant: a rule that does not say WHAT may be remembered
  has not been stated.
- ``include_end_summary`` (bool, optional, default False) —
  whether a session's closing summary may also feed. Off
  unless the user turns it on.
- ``rule_id`` (string, optional) — the user's name for the
  rule, carried into every candidate's provenance and every
  report, so a remembered fact can always be traced to the
  rule that let it cross.

Unknown keys make the rule invalid (fail closed): a rule
may not smuggle in terms this law does not name. Every
validation error is reported by field name, never by
content.

WHAT MAY FEED — AND WHAT NEVER DOES

From the logger's four entry kinds (E-063), only two can
carry a memory:

- ``event`` entries whose event type is feedable:
  ``learned`` (category ``lesson``), ``decision``
  (category ``decision``) and ``milestone`` (category
  ``milestone``). The other event types — file_changed,
  action, blocker, blocker_resolved, mood_shift — are
  working state, not memories; they never feed, even under
  an all-sessions rule, because the user's rule selects
  from the feedable vocabulary only.
- ``end`` entries, and only their summary, and only when
  the rule's ``include_end_summary`` is on (category
  ``session_summary``).

``start`` and ``update`` entries never feed: a start is a
header and an update is a snapshot of working state, and
neither is a fact the user said. Empty or whitespace-only
content never feeds. Within one feed run, an exact repeat
of an already-fed (session, category, content) is fed
once; the repeats are counted, not silently dropped and
not silently doubled.

NEVER SILENTLY

Every call to :func:`feed_candidates` returns the
candidates AND a report, and the report exists even when
nothing feeds — especially then. The report is counts and
status only: total entries seen, how many fed, and how
many were withheld under each named reason (no rule, rule
disabled, rule invalid, out of scope, not feedable, not
selected by the rule, empty, duplicate, unattributable).
It contains no entry content, no session ids and no
persona ids — in the counts-only discipline of E-071's
privacy report — so the accounting can be shown anywhere
without itself becoming a leak. A feed with no rule, a
disabled rule, a rule granted by anyone but the user, or
an invalid rule feeds NOTHING and says so in its status:
``no_rule``, ``rule_disabled`` or ``invalid_rule``.

PERSONA AND DELETION, HONESTLY STATED

Log entries carry no persona id (E-063). When the caller
supplies a ``session_owners`` mapping (the same caller
knowledge E-071 uses), each candidate is tagged with its
session's persona so the memory face can keep persona
separation (E-083's duty, prepared here); without a
mapping the tag is None — a persona is never guessed from
content. Deletion interplay: a session deleted under
E-063's right no longer appears in the log, so no later
feed can draw from it. This law does NOT retract
candidates already fed before a deletion — that
propagation is memory's side of the boundary and is
docket 104, owned by E-085's reconciliation; it is stated
here so no one mistakes this feed law for a retraction
mechanism.
"""

import copy

MEMORY_FEED_VERSION = 1

# The event types that may become memory, and the memory
# category each becomes. Every other logger event type is
# working state and never feeds (see the module docstring).
FEEDABLE_EVENT_TYPES = ("learned", "decision", "milestone")
CATEGORY_BY_EVENT_TYPE = {
    "learned": "lesson",
    "decision": "decision",
    "milestone": "milestone",
}
END_SUMMARY_CATEGORY = "session_summary"

# The rule's scopes. There is no default scope.
SCOPE_NAMED = "named_sessions"
SCOPE_ALL = "all_sessions"
SCOPES = (SCOPE_NAMED, SCOPE_ALL)

RULE_KEYS = frozenset({
    "enabled", "granted_by", "scope", "session_ids",
    "event_types", "include_end_summary", "rule_id",
})

# Withholding reasons, in report order. Every entry that
# does not feed is counted under exactly one of these.
WITHHELD_REASONS = (
    "withheld_no_rule",
    "withheld_rule_disabled",
    "withheld_invalid_rule",
    "withheld_unattributable",
    "withheld_out_of_scope",
    "withheld_not_feedable",
    "withheld_not_selected",
    "withheld_empty",
    "withheld_duplicate",
)


def validate_rule(rule) -> list:
    """Errors in a would-be user rule; [] means valid.

    Errors name fields, never values' content. A valid rule
    is a dict with exactly the named keys it uses, granted
    by the user, with a stated scope and a stated, feedable
    event-type selection. ``enabled`` is validated here as
    a bool; whether it is on is the feed's question, not
    validity's.
    """
    if not isinstance(rule, dict):
        return ["rule must be a dict"]
    errors = []
    unknown = sorted(set(rule) - RULE_KEYS)
    if unknown:
        errors.append(f"unknown rule keys: {unknown}")
    if not isinstance(rule.get("enabled"), bool):
        errors.append("enabled must be a bool")
    if rule.get("granted_by") != "user":
        errors.append('granted_by must be "user"')
    scope = rule.get("scope")
    if scope not in SCOPES:
        errors.append(f"scope must be one of {list(SCOPES)}")
    elif scope == SCOPE_NAMED:
        ids = rule.get("session_ids")
        if (not isinstance(ids, (list, tuple)) or not ids
                or not all(isinstance(s, str) and s for s in ids)):
            errors.append("named_sessions scope requires a non-empty "
                          "session_ids list of session id strings")
    elif "session_ids" in rule:
        errors.append("session_ids is only meaningful under "
                      "named_sessions scope")
    event_types = rule.get("event_types")
    if (not isinstance(event_types, (list, tuple)) or not event_types
            or not all(isinstance(t, str) for t in event_types)):
        errors.append("event_types must be a non-empty list drawn from "
                      f"{list(FEEDABLE_EVENT_TYPES)}")
    else:
        bad = [t for t in event_types if t not in FEEDABLE_EVENT_TYPES]
        if bad:
            errors.append(f"event_types not feedable: {sorted(set(bad))}")
    if "include_end_summary" in rule and not isinstance(
            rule["include_end_summary"], bool):
        errors.append("include_end_summary must be a bool")
    if "rule_id" in rule and not isinstance(rule["rule_id"], str):
        errors.append("rule_id must be a string")
    return errors


def _report(status, total, fed, withheld, rule_id=None, errors=()):
    report = {
        "memory_feed_version": MEMORY_FEED_VERSION,
        "status": status,
        "rule_id": rule_id,
        "total": total,
        "fed": fed,
    }
    for reason in WITHHELD_REASONS:
        report[reason] = withheld.get(reason, 0)
    if errors:
        report["errors"] = list(errors)
    return report


def feed_candidates(entries, rule, session_owners=None):
    """The lawful feed: (candidates, counts-only report).

    ``entries`` are conversation-log entries (dicts in the
    E-063 shapes). Nothing feeds without a valid, enabled,
    user-granted rule; every entry that does not feed is
    counted under exactly one withholding reason. The
    input is never mutated, and candidates are new dicts
    whose provenance names the log, the entry kind and the
    rule that let them cross.
    """
    entries = list(entries)
    total = len(entries)
    owners = session_owners or {}

    if rule is None:
        return [], _report("no_rule", total, 0,
                           {"withheld_no_rule": total})
    rule_id = rule.get("rule_id") if isinstance(rule, dict) else None
    errors = validate_rule(rule)
    if errors:
        return [], _report("invalid_rule", total, 0,
                           {"withheld_invalid_rule": total},
                           rule_id=rule_id, errors=errors)
    if not rule["enabled"]:
        return [], _report("rule_disabled", total, 0,
                           {"withheld_rule_disabled": total},
                           rule_id=rule_id)

    named = rule["scope"] == SCOPE_NAMED
    session_ids = set(rule.get("session_ids") or ())
    selected = set(rule["event_types"])
    include_end = bool(rule.get("include_end_summary", False))

    candidates = []
    withheld: dict = {}
    seen: set = set()

    def hold(reason):
        withheld[reason] = withheld.get(reason, 0) + 1

    for entry in entries:
        if not isinstance(entry, dict) or not entry.get("session_id"):
            hold("withheld_unattributable")
            continue
        session_id = entry["session_id"]
        if named and session_id not in session_ids:
            hold("withheld_out_of_scope")
            continue
        kind = entry.get("entry_type")
        if kind == "event":
            event_type = entry.get("event_type")
            if event_type not in FEEDABLE_EVENT_TYPES:
                hold("withheld_not_feedable")
                continue
            if event_type not in selected:
                hold("withheld_not_selected")
                continue
            category = CATEGORY_BY_EVENT_TYPE[event_type]
            content = entry.get("content")
        elif kind == "end":
            if not include_end:
                hold("withheld_not_selected")
                continue
            event_type = None
            category = END_SUMMARY_CATEGORY
            content = entry.get("summary")
        else:
            hold("withheld_not_feedable")
            continue
        if not isinstance(content, str) or not content.strip():
            hold("withheld_empty")
            continue
        key = (session_id, category, content)
        if key in seen:
            hold("withheld_duplicate")
            continue
        seen.add(key)
        candidates.append({
            "memory_feed_version": MEMORY_FEED_VERSION,
            "source": "conversation_logger",
            "session_id": session_id,
            "timestamp": entry.get("timestamp"),
            "category": category,
            "content": content,
            "persona_id": owners.get(session_id),
            "provenance": {
                "log_file": "conversation_log.jsonl",
                "entry_type": kind,
                "event_type": event_type,
                "rule_id": rule_id,
            },
        })
    return candidates, _report("fed", total, len(candidates), withheld,
                               rule_id=rule_id)


def feed_log_entries(entries, rule, session_owners=None):
    """A deep-copied feed run (callers that hand the result on).

    Same law as :func:`feed_candidates`; the returned
    candidates and report share no objects with the input
    entries, so a consumer cannot mutate the log's records
    through them.
    """
    candidates, report = feed_candidates(
        copy.deepcopy(list(entries)), rule, session_owners)
    return candidates, report
