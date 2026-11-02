#!/usr/bin/env python3
"""
Verdandi Ordering & Replay — events replay deterministically
for debugging.

Filed by Project Ember slice E-069 (docs/architecture/
E-069_ORDERING_AND_REPLAY.md). Until this slice the nerve
feed had an order but no replay law: the hub stamps each
publish with a monotonic ``_seq`` (E-061), offline fallback
writes carry no ``_seq`` at all (sequence holes are by
design), legacy dialects carry their own timestamps, and a
reader who wanted to re-run a debugging session had nothing
but the feed file's append order and hope. This module IS
the replay law in code: how a feed is read, how its events
are ordered, what a replay reports about the holes and
duplicates it found, and the digest that proves two replays
of the same feed are the same replay. Stdlib only, no
imports from any other Verdandi module — deployed copies
are loaded file-by-file, so this module must stand alone
exactly like event_contract.py does.

THE ORDER (total, deterministic, stated once here)

A replay visits events in exactly this order:

1. Sequenced events first, by ``_seq`` ascending. ``_seq``
   is the hub's own monotonic stamp (E-061): it IS the
   order the hub broadcast in. Two events carrying the
   same ``_seq`` (a duplicated feed line, a merged feed)
   keep their relative file order — the file index is the
   tie-break, never the event's content.
2. Unsequenced events after them, by effective timestamp
   ascending (see below), file index breaking ties, and
   events with no timestamp at all last, in file order.
   Unsequenced events are the offline fallback writes
   (``_fallback``, no ``_seq`` — E-061) and pre-contract
   legacy lines. No sequence number is ever invented for
   them: their placement after the sequenced block is a
   stated rule of this law, not a guess about when they
   happened relative to hub events. A debugging replay
   that needs wall-clock interleaving must say so itself;
   this law never fabricates an order it was not given.

The effective timestamp of an event is, in order: its
``_ts`` when that is a number, else its ``_iso`` parsed as
ISO-8601, else its legacy ``timestamp`` field (a number, or
an ISO-8601 string — the heartbeat fallback shape), else
None. Booleans are never numbers here.

DETERMINISM

Ordering depends only on ``_seq``, the effective timestamp,
and the file index — never on dict iteration order, wall
clock, or environment. ``canonical_line`` renders an event
as JSON with sorted keys and fixed separators, and
``replay_digest`` is the SHA-256 of the canonical lines of
the ordered events, one per line. Replaying the same feed
twice yields the same order and the same digest; replaying
a shuffled copy of a feed's sequenced events yields the
same sequenced order (the shuffle test in the conformance
suite proves both). Ordering an already-ordered list is
the identity.

LOSSLESSNESS

Replay never edits an event. Legacy fields, the mood
dialect's shape, stimuli provenance inside ``data``
(E-064), and Hermes provenance — the inner lifecycle
envelope on a raw Hermes event, or the ``_hermes_*`` keys
on a translated one (E-068) — all pass through byte-for-
byte at the value level. Normalising a dialect is
event_contract.normalize_event's job, and translating a
Hermes event is hermes_nerves.normalize_hermes_event's
job; a consumer may apply those to the replayed events,
in replay order, but replay itself is not a translation.

THE REPORT

Every replay produces a report naming what it found:
the ordered events, their digest, the sequence range,
the gaps in ``_seq`` (the holes the fallback design
promises), the duplicated ``_seq`` values, how many
events were unsequenced / fallback, the dialect counts
(classified by the kind key, event_contract's rule,
restated standalone here), and — for a feed read from
lines — the corrupt lines it skipped, each named by its
1-based line number. A corrupt line is skipped and
reported, never fatal and never silently dropped: a
debugging tool that hides damage has failed at its job.
"""

import hashlib
import json
from datetime import datetime

REPLAY_VERSION = 1

# Dialect names, mirroring event_contract.DIALECTS plus the
# honest "unknown" for a dict in no recognised shape (pinned
# equal to the contract's set, plus unknown, by the E-069
# conformance tests; literals here because this module must
# stand alone).
DIALECT_HUB = "hub"
DIALECT_HEARTBEAT = "heartbeat"
DIALECT_HEARTBEAT_FALLBACK = "heartbeat_fallback"
DIALECT_MOOD = "mood"
DIALECT_UNKNOWN = "unknown"
DIALECTS = (
    DIALECT_HUB,
    DIALECT_HEARTBEAT,
    DIALECT_HEARTBEAT_FALLBACK,
    DIALECT_MOOD,
    DIALECT_UNKNOWN,
)


def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _parse_iso(value):
    """Epoch seconds for an ISO-8601 string, or None."""
    if not isinstance(value, str) or not value:
        return None
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        # Feed stamps are UTC (the hub writes timezone-aware
        # ISO strings); a naive legacy stamp is read as UTC,
        # stated here, never guessed per-event.
        from datetime import timezone

        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.timestamp()


def seq_of(event):
    """The hub's ``_seq`` stamp, or None when unsequenced.

    Only a genuine int counts (never a bool, never a numeric
    string): a stamp of the wrong shape is no stamp.
    """
    if not isinstance(event, dict):
        return None
    seq = event.get("_seq")
    if isinstance(seq, int) and not isinstance(seq, bool):
        return seq
    return None


def effective_timestamp(event):
    """The event's effective timestamp (module docstring)."""
    if not isinstance(event, dict):
        return None
    if _is_number(event.get("_ts")):
        return float(event["_ts"])
    iso = _parse_iso(event.get("_iso"))
    if iso is not None:
        return iso
    legacy = event.get("timestamp")
    if _is_number(legacy):
        return float(legacy)
    return _parse_iso(legacy)


def classify_dialect(event):
    """The dialect a raw event is written in (E-061's rule)."""
    if not isinstance(event, dict):
        return DIALECT_UNKNOWN
    if "type" in event:
        return DIALECT_HUB
    if "event" in event:
        return DIALECT_MOOD
    if "event_type" in event:
        if event.get("source") == "verdandi-heartbeat" and "timestamp" in event:
            return DIALECT_HEARTBEAT_FALLBACK
        return DIALECT_HEARTBEAT
    return DIALECT_UNKNOWN


def _order_key(indexed):
    index, event = indexed
    seq = seq_of(event)
    if seq is not None:
        return (0, seq, 0.0, index)
    ts = effective_timestamp(event)
    if ts is not None:
        return (1, 0, ts, index)
    return (2, 0, 0.0, index)


def order_events(events):
    """The events in replay order (module docstring).

    The input list is not mutated and no event is edited;
    the returned list holds the same dicts, reordered.
    """
    indexed = list(enumerate(events))
    indexed.sort(key=_order_key)
    return [event for _, event in indexed]


def canonical_line(event) -> str:
    """One event as canonical JSON: sorted keys, fixed shape."""
    return json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def replay_digest(ordered) -> str:
    """SHA-256 of the canonical lines of the ordered events."""
    digest = hashlib.sha256()
    for event in ordered:
        digest.update(canonical_line(event).encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def load_feed_lines(lines):
    """Parse JSONL feed lines into (events, issues).

    Blank lines are skipped silently (a trailing newline is
    not damage). A line that is not valid JSON, or whose
    JSON is not an object, is skipped and reported in
    ``issues`` as {"line": <1-based>, "kind": ..., "detail":
    ...}; parsing never raises.
    """
    events = []
    issues = []
    for number, raw in enumerate(lines, start=1):
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", errors="replace")
        line = raw.strip()
        if not line:
            continue
        try:
            parsed = json.loads(line)
        except (json.JSONDecodeError, ValueError) as exc:
            issues.append({"line": number, "kind": "invalid_json", "detail": str(exc)})
            continue
        if not isinstance(parsed, dict):
            issues.append(
                {"line": number, "kind": "not_object", "detail": type(parsed).__name__}
            )
            continue
        events.append(parsed)
    return events, issues


def load_feed_text(text):
    """``load_feed_lines`` over a whole feed file's text."""
    return load_feed_lines(text.splitlines())


def _report(ordered, issues):
    seqs = [seq_of(event) for event in ordered]
    present = sorted({seq for seq in seqs if seq is not None})
    gaps = []
    if present:
        have = set(present)
        gaps = [seq for seq in range(present[0], present[-1] + 1) if seq not in have]
    seen = {}
    for seq in present:
        seen[seq] = seqs.count(seq)
    duplicates = sorted(seq for seq, count in seen.items() if count > 1)
    dialect_counts = {}
    for event in ordered:
        dialect = classify_dialect(event)
        dialect_counts[dialect] = dialect_counts.get(dialect, 0) + 1
    return {
        "version": REPLAY_VERSION,
        "ordered": ordered,
        "digest": replay_digest(ordered),
        "count": len(ordered),
        "seq_min": present[0] if present else None,
        "seq_max": present[-1] if present else None,
        "gaps": gaps,
        "duplicate_seqs": duplicates,
        "unsequenced": sum(1 for seq in seqs if seq is None),
        "fallback": sum(1 for event in ordered if event.get("_fallback") is True),
        "dialects": dialect_counts,
        "issues": list(issues),
    }


def replay_events(events, issues=()):
    """Order ``events`` for replay and report what was found."""
    return _report(order_events(list(events)), issues)


def replay_feed_lines(lines):
    """Parse feed lines, then replay them (issues included)."""
    events, issues = load_feed_lines(lines)
    return replay_events(events, issues=issues)


def replay_to(events, sink):
    """Replay ``events`` into ``sink(event)``, in replay order.

    Each event is handed to the sink exactly once, in the
    order this module's law defines; the replay report is
    returned. A sink exception propagates and stops the
    replay — a debugging consumer that fails mid-replay
    must be seen to fail, never papered over.
    """
    report = replay_events(events)
    for event in report["ordered"]:
        sink(event)
    return report


def validate_replay_order(ordered) -> list:
    """Errors in a would-be replay order; [] means lawful.

    Lawful = exactly ``order_events``' output for the same
    events (compared by canonical line, so two equal-valued
    events are interchangeable and no identity is assumed).
    """
    ordered = list(ordered)
    expected = order_events(ordered)
    if [canonical_line(e) for e in expected] != [canonical_line(e) for e in ordered]:
        return ["events are not in replay order (E-069 law)"]
    return []
