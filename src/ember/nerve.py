"""The Ember core's nerve bridge to Verdandi (E-067).

Until E-067 the core never touched Verdandi at all (E-019,
E-059 §1): the companion's sessions and turns happened in
silence as far as the monorepo's nerve hub was concerned. This
bridge is the core's side of the cross-member wiring filed at
``docs/architecture/E-067_CROSS_MEMBER_NERVES.md`` and
registered in ``Verdandi/cross_member.py`` /
``Verdandi/event_contract.py`` (contract v1).

What crosses the nerve is FACTS, never content: a session's
start and end (persona, conversation, whether the Well — the
companion's memory store — was connected, the model, the turn
count) and one event per completed turn carrying the turn's
memory facts (Well hits that grounded it, chunks cited, where
its Episode was persisted, whether it was ungrounded, its
outcome). No operator text and no reply text ever enters an
event.

Discipline, mirroring the conversation logger's standing rule:

- **A nerve failure never breaks the chat.** Every public
  function here returns a status dict and never raises.
- **Degrade honestly.** A publish that reaches the hub returns
  its ``ack``; a publish that finds no hub is appended to the
  hub's feed file with ``_fallback`` stamped and reported as
  ``fallback`` (the hub's own offline shape, E-061 §2); any
  other failure is reported as ``error`` with the reason. The
  bridge never claims a delivery it did not make.
- **Stdlib only, no member imports.** The contract literals
  below (version, event names, field sets, vocabularies) are
  literals pinned equal to the Verdandi contract modules by
  the E-067 conformance tests — the core does not import
  Verdandi, exactly as the hub's own deployed modules carry
  their contract literals inline (E-061's pattern).

The hub's home is its own (``~/.hermes/state`` — the hub's
state dir, not Ember's config root): the socket is
``runa.sock`` there and the feed is ``nerve_feed.jsonl``.
``state_dir`` parameters exist for tests and for the hub's own
relocated deployments; chat passes none.

The reverse direction (hub → core) is offered as
:func:`read_recent` — the hub's ``recent`` control message
with the feed-file tail as its offline shape — and is proven
against a live hub by the E-067 tests. Chat's prompt assembly
does not consume nerves yet (a context-budget decision no
slice has claimed; see the E-067 doc §5).

E-071 adds the privacy law to this bridge's read path:
:func:`read_recent_for_persona` / :func:`filter_for_persona`
give a persona only its own bound events plus system events
— another persona's events, and above all their stimuli
provenance, are withheld entirely, and session-bound events
with no known owner are withheld fail-closed. The rule is
Verdandi/nerve_privacy.py's, carried inline here under this
module's no-member-imports discipline and pinned equal by
the E-071 conformance tests.
"""

from __future__ import annotations

import json
import socket as sock_mod
import time
from datetime import UTC, datetime
from pathlib import Path

#: Contract version (event_contract.CONTRACT_VERSION, E-061).
CONTRACT_VERSION = 1

#: The one source the core publishes under (registered).
SOURCE = "ember_core"

#: Registered event names (Verdandi/cross_member.py).
SESSION_EVENT = "ember_session"
TURN_EVENT = "ember_turn"

#: The exact data field sets of the two registered events.
SESSION_FIELDS = ("phase", "persona_id", "conversation_id", "well_connected", "model", "turns")
TURN_FIELDS = ("conversation_id", "persona_id", "hits", "cited", "persisted", "ungrounded", "outcome", "model")

#: Closed vocabularies of the enum-like fields.
SESSION_PHASES = ("start", "end")
PERSISTED_SHAPES = ("well", "journal", "memory_only")
TURN_OUTCOMES = ("answered", "interrupted", "error", "truncated", "ungrounded")

_SOCKET_NAME = "runa.sock"
_FEED_NAME = "nerve_feed.jsonl"


def hub_state_dir() -> Path:
    """The nerve hub's state dir (its own home, not Ember's)."""
    return Path.home() / ".hermes" / "state"


def _socket_path(state_dir: Path | None) -> Path:
    return (state_dir or hub_state_dir()) / _SOCKET_NAME


def _feed_path(state_dir: Path | None) -> Path:
    return (state_dir or hub_state_dir()) / _FEED_NAME


def build_session_event(
    phase: str,
    *,
    persona_id: str,
    conversation_id: str,
    well_connected: bool,
    model: str,
    turns: int,
) -> dict:
    """The canonical ember_session envelope (validated first)."""
    if phase not in SESSION_PHASES:
        raise ValueError(f"phase must be one of {SESSION_PHASES}, got {phase!r}")
    return {
        "v": CONTRACT_VERSION,
        "type": SESSION_EVENT,
        "data": {
            "phase": phase,
            "persona_id": persona_id,
            "conversation_id": conversation_id,
            "well_connected": bool(well_connected),
            "model": model,
            "turns": int(turns),
        },
        "source": SOURCE,
    }


def build_turn_event(
    *,
    conversation_id: str,
    persona_id: str,
    hits: int,
    cited: int,
    persisted: str,
    ungrounded: bool,
    outcome: str,
    model: str,
) -> dict:
    """The canonical ember_turn envelope (validated first)."""
    if persisted not in PERSISTED_SHAPES:
        raise ValueError(f"persisted must be one of {PERSISTED_SHAPES}, got {persisted!r}")
    if outcome not in TURN_OUTCOMES:
        raise ValueError(f"outcome must be one of {TURN_OUTCOMES}, got {outcome!r}")
    return {
        "v": CONTRACT_VERSION,
        "type": TURN_EVENT,
        "data": {
            "conversation_id": conversation_id,
            "persona_id": persona_id,
            "hits": int(hits),
            "cited": int(cited),
            "persisted": persisted,
            "ungrounded": bool(ungrounded),
            "outcome": outcome,
            "model": model,
        },
        "source": SOURCE,
    }


def publish_event(event: dict, *, state_dir: Path | None = None) -> dict:
    """Publish one canonical envelope to the hub; never raises.

    Returns the hub's ``ack`` dict when the hub answers, a
    ``{'nerve_type': 'sent', 'note': 'no_ack'}`` when it does
    not, ``{'nerve_type': 'fallback', ...}`` when no hub is
    reachable and the event was written to the feed file, or
    ``{'nerve_type': 'error', 'error': ...}`` otherwise — the
    hub's own publish result shapes (E-061 §2).
    """
    payload = json.dumps(event) + "\n"
    sock = None
    try:
        sock = sock_mod.socket(sock_mod.AF_UNIX, sock_mod.SOCK_STREAM)
        sock.settimeout(2.0)
        sock.connect(str(_socket_path(state_dir)))
        sock.sendall(payload.encode())
        try:
            response = sock.recv(4096)
            return json.loads(response.decode().strip())
        except (json.JSONDecodeError, TimeoutError, OSError):
            return {"nerve_type": "sent", "note": "no_ack"}
    except (ConnectionRefusedError, FileNotFoundError):
        try:
            stamped = dict(event)
            stamped["_ts"] = time.time()
            stamped["_iso"] = datetime.now(tz=UTC).isoformat()
            stamped["_fallback"] = True
            feed = _feed_path(state_dir)
            feed.parent.mkdir(parents=True, exist_ok=True)
            with open(feed, "a", encoding="utf-8") as handle:
                handle.write(json.dumps(stamped) + "\n")
            return {"nerve_type": "fallback", "note": "hub_offline_written_to_feed"}
        except Exception as exc:  # noqa: BLE001 — reported, never raised
            return {"nerve_type": "error", "error": str(exc)}
    except Exception as exc:  # noqa: BLE001 — reported, never raised
        return {"nerve_type": "error", "error": str(exc)}
    finally:
        if sock is not None:
            try:
                sock.close()
            except Exception:  # noqa: BLE001, S110 — close is best-effort
                pass


def publish_session(
    phase: str,
    *,
    persona_id: str,
    conversation_id: str,
    well_connected: bool,
    model: str,
    turns: int = 0,
    state_dir: Path | None = None,
) -> dict:
    """Publish an ember_session event; never raises."""
    try:
        event = build_session_event(
            phase,
            persona_id=persona_id,
            conversation_id=conversation_id,
            well_connected=well_connected,
            model=model,
            turns=turns,
        )
    except ValueError as exc:
        return {"nerve_type": "error", "error": str(exc)}
    return publish_event(event, state_dir=state_dir)


def publish_turn(
    *,
    conversation_id: str,
    persona_id: str,
    hits: int,
    cited: int,
    persisted: str,
    ungrounded: bool,
    outcome: str,
    model: str,
    state_dir: Path | None = None,
) -> dict:
    """Publish an ember_turn event; never raises."""
    try:
        event = build_turn_event(
            conversation_id=conversation_id,
            persona_id=persona_id,
            hits=hits,
            cited=cited,
            persisted=persisted,
            ungrounded=ungrounded,
            outcome=outcome,
            model=model,
        )
    except ValueError as exc:
        return {"nerve_type": "error", "error": str(exc)}
    return publish_event(event, state_dir=state_dir)


#: Conversation shapes that are session-bound for privacy
#: (Verdandi/nerve_privacy.py SESSION_BOUND_TYPES, E-071 —
#: literals pinned equal by the E-071 conformance tests).
_PRIVACY_SESSION_BOUND_TYPES = ("conv_start", "conv_event", "conv_update", "conv_end")
_PRIVACY_SESSION_BOUND_STIMULI = ("message.conversation",)


def _privacy_classify(event: object, persona_id: str, session_owners: dict | None) -> str:
    """The E-071 classification of one event for ``persona_id``.

    Mirrors Verdandi/nerve_privacy.classify_event for the
    shapes this bridge can meet: ``own`` / ``cross`` /
    ``unknown_session`` / ``system``. Bindings are explicit
    only — data.persona_id, a stimulus's payload/provenance
    persona_id, or a session binding resolved through
    ``session_owners``; everything else is system.
    """
    if not isinstance(event, dict):
        return "system"
    data = event.get("data") if isinstance(event.get("data"), dict) else {}
    typ = event.get("type")
    direct = data.get("persona_id")
    stim = data if isinstance(typ, str) and typ.startswith("stimulus:") and isinstance(data.get("payload"), dict) else None
    if stim is not None:
        payload = stim.get("payload") or {}
        prov = stim.get("provenance") if isinstance(stim.get("provenance"), dict) else {}
        if not (isinstance(direct, str) and direct):
            direct = payload.get("persona_id") or prov.get("persona_id")
    if isinstance(direct, str) and direct:
        return "own" if direct == persona_id else "cross"
    session_id = data.get("session_id")
    session_bound = typ in _PRIVACY_SESSION_BOUND_TYPES
    if stim is not None:
        payload = stim.get("payload") or {}
        if session_id is None:
            session_id = payload.get("session_id")
        if stim.get("name") in _PRIVACY_SESSION_BOUND_STIMULI:
            session_bound = True
    if session_bound:
        owners = session_owners or {}
        if isinstance(session_id, str) and session_id in owners:
            return "own" if owners[session_id] == persona_id else "cross"
        return "unknown_session"
    return "system"


def filter_for_persona(
    events: list, persona_id: str, *, session_owners: dict | None = None
) -> tuple[list, dict]:
    """The E-071 persona-scoped view of ``events``; never raises by design of its inputs.

    Visible events are returned unmodified, in order:
    events bound to ``persona_id`` and system events.
    Events bound to another persona are withheld entirely
    (their provenance never enters the view or the report),
    and session-bound events with no known owner are
    withheld fail-closed. The report is counts only.
    """
    visible = []
    withheld_cross = 0
    withheld_unknown = 0
    for event in events:
        cls = _privacy_classify(event, persona_id, session_owners)
        if cls in ("own", "system"):
            visible.append(event)
        elif cls == "cross":
            withheld_cross += 1
        else:
            withheld_unknown += 1
    report = {
        "privacy_version": 1,
        "persona_id": persona_id,
        "total": len(events),
        "visible": len(visible),
        "withheld_cross_persona": withheld_cross,
        "withheld_unknown_session": withheld_unknown,
    }
    return visible, report


def read_recent_for_persona(
    persona_id: str,
    count: int = 20,
    *,
    session_owners: dict | None = None,
    state_dir: Path | None = None,
) -> tuple[list, dict]:
    """``read_recent`` filtered by the E-071 privacy law for one persona.

    Fetches a wider tail (4x, mirroring read_recent's own
    offline over-fetch) so withholding does not silently
    shrink the view below what the persona may see, then
    returns at most ``count`` visible events + the report.
    """
    events = read_recent(max(count * 4, count), state_dir=state_dir)
    visible, report = filter_for_persona(events, persona_id, session_owners=session_owners)
    return visible[-count:] if count >= 0 else visible, report


def read_recent(count: int = 20, *, state_dir: Path | None = None) -> list:
    """The hub's most recent events; never raises.

    Live shape first: the ``recent`` control message against a
    running hub's ring buffer. Offline shape: the tail of the
    feed file, parsed line by line (unparseable lines skipped,
    as the logger's readers do). Returns [] when neither is
    available — an honest empty, not an error dressed as one.
    """
    sock = None
    try:
        sock = sock_mod.socket(sock_mod.AF_UNIX, sock_mod.SOCK_STREAM)
        sock.settimeout(2.0)
        sock.connect(str(_socket_path(state_dir)))
        sock.sendall(json.dumps({"nerve_type": "recent", "count": count}).encode() + b"\n")
        response = sock.recv(262144)
        reply = json.loads(response.decode().strip())
        if reply.get("nerve_type") == "recent_events":
            return list(reply.get("events", []))
    except Exception:  # noqa: BLE001 — fall through to the feed shape
        pass
    finally:
        if sock is not None:
            try:
                sock.close()
            except Exception:  # noqa: BLE001, S110
                pass
    try:
        lines = _feed_path(state_dir).read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    events = []
    for line in lines[-max(count * 4, count):]:
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events[-count:]
