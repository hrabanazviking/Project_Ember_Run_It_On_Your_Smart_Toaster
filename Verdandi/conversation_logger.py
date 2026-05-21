#!/usr/bin/env python3
"""
Conversation Logger — Runa's streaming conversation tracker.

DESIGN PRINCIPLE: Log as it happens, not at the end.
A crashed session loses only the last line, not the whole conversation.

Entry types:
  start    — Session opened (required first entry)
  event    — Something happened (decision made, bug fixed, skill created)
  update   — State snapshot (progress checkpoint, context shift)
  end      — Session closed (final summary)

All entries share a session_id and are linked chronologically.
The current.json always reflects the LATEST state of the active session.

Usage:
    # Start a session
    python3 conversation_logger.py start --session 2026-05-10-truth-discipline \\
        --summary "Building truth discipline" --model glm-5.1 --platform telegram

    # Log events as they happen
    python3 conversation_logger.py event --session 2026-05-10-truth-discipline \\
        --type decision --content "Truth discipline is now importance-10 law"

    python3 conversation_logger.py event --session 2026-05-10-truth-discipline \\
        --type file_changed --content "skills/devops/truth-discipline/SKILL.md"

    python3 conversation_logger.py event --session 2026-05-10-truth-discipline \\
        --type learned --content "M-08 was stealth-fixed, duplicate of M-17"

    # Update state snapshot any time
    python3 conversation_logger.py update --session 2026-05-10-truth-discipline \\
        --next "Wire memory to auto-log" "Add auto-consult to cron" \\
        --blockers "Himalaya password expired" \\
        --projects NorseSagaEngine \\
        --mood "productive"

    # End a session
    python3 conversation_logger.py end --session 2026-05-10-truth-discipline \\
        --summary "Built truth discipline + conversation logging" \\
        --duration 95

    # Query commands
    python3 conversation_logger.py show --session 2026-05-10-truth-discipline
    python3 conversation_logger.py recent --count 5
    python3 conversation_logger.py context   # cron job context injection
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

STATE_DIR = Path.home() / ".hermes" / "state"
CONV_DIR = STATE_DIR / "conversations"
CURRENT_FILE = STATE_DIR / "current.json"
CONV_LOG = STATE_DIR / "conversation_log.jsonl"

# Valid entry types for 'event' subcommand
EVENT_TYPES = {"decision", "file_changed", "learned", "action", "blocker", "blocker_resolved", "mood_shift", "milestone"}


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


# Cached module reference — avoids re-importing on every event
_nerve_module = None
_nerve_module_path = None


def _nerve_fire(entry: dict):
    """Fire a nerve impulse — publish event to the nervous system for real-time awareness.

    Uses a cached module reference to avoid the overhead and risk of
    re-importing nervous_system.py on every call. If the module file changes
    on disk (e.g. updated), the cache is refreshed automatically.
    """
    global _nerve_module, _nerve_module_path
    try:
        nerve_path = STATE_DIR / "nervous_system.py"
        if not nerve_path.exists():
            return

        # Refresh cache if the file changed on disk
        current_path = str(nerve_path)
        if _nerve_module is None or _nerve_module_path != current_path:
            import importlib.util
            spec = importlib.util.spec_from_file_location("nervous_system", current_path)
            _nerve_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(_nerve_module)
            _nerve_module_path = current_path

        _nerve_module.publish_event_sync(
            event_type=f"conv_{entry.get('entry_type', 'unknown')}",
            data=entry,
            source=f"conv_logger:{entry.get('session_id', '?')}"
        )
    except Exception:
        pass  # Nerve failure must NEVER break the logger


def _append(entry: dict) -> dict:
    """Append an entry to the JSONL log. Each line is independent — crash-safe.
    Also fires a nerve impulse for real-time cross-instance awareness."""
    CONV_DIR.mkdir(parents=True, exist_ok=True)
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONV_LOG, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    # Fire nerve impulse — every event now pulses through the nervous system
    _nerve_fire(entry)
    return entry


def _update_current(entry: dict, session_id: str):
    """Update current.json to reflect the latest state of the active session."""
    # Merge with existing current.json if it exists and is the same session
    existing = {}
    if CURRENT_FILE.exists():
        try:
            with open(CURRENT_FILE) as f:
                existing = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    # Build current state from entry
    current = {
        "session_id": session_id,
        "last_updated": entry.get("timestamp", _timestamp()),
        "status": entry.get("entry_type", "unknown"),
    }

    # Preserve and merge accumulated fields
    for field in ("summary", "decisions", "files_changed", "things_learned",
                  "next_actions", "mood", "projects_touched", "blockers",
                  "model", "platform", "duration_minutes", "start_time", "end_time"):
        if field in entry:
            current[field] = entry[field]
        elif field in existing and existing.get("session_id") == session_id:
            # Keep previous value if same session
            current[field] = existing[field]

    # Accumulate lists from events (don't overwrite — append unique)
    for list_field in ("decisions", "files_changed", "things_learned", "projects_touched"):
        if list_field not in current:
            current[list_field] = existing.get(list_field, [])

    with open(CURRENT_FILE, "w") as f:
        json.dump(current, f, indent=2, ensure_ascii=False)


def cmd_start(args):
    """Open a new session. Required first entry."""
    ts = _timestamp()
    entry = {
        "entry_type": "start",
        "timestamp": ts,
        "session_id": args.session,
        "summary": args.summary or "",
        "model": args.model or "",
        "platform": args.platform or "",
        "start_time": ts,
    }
    _append(entry)

    # Initialize current.json for this session
    current = {
        "session_id": args.session,
        "start_time": ts,
        "last_updated": ts,
        "status": "active",
        "summary": args.summary or "",
        "model": args.model or "",
        "platform": args.platform or "",
        "decisions": [],
        "files_changed": [],
        "things_learned": [],
        "next_actions": [],
        "projects_touched": [],
        "blockers": [],
        "mood": "",
        "duration_minutes": 0,
    }
    with open(CURRENT_FILE, "w") as f:
        json.dump(current, f, indent=2, ensure_ascii=False)

    print(f"🟢 Session started: {args.session}")
    print(f"   {ts}")
    return entry


def cmd_event(args):
    """Log a single event during the session. Crash-safe — immediately written."""
    if args.type not in EVENT_TYPES:
        print(f"❌ Invalid event type: {args.type}")
        print(f"   Valid types: {', '.join(sorted(EVENT_TYPES))}")
        sys.exit(1)

    ts = _timestamp()
    entry = {
        "entry_type": "event",
        "timestamp": ts,
        "session_id": args.session,
        "event_type": args.type,
        "content": args.content,
    }
    _append(entry)

    # Update current.json — accumulate into appropriate list field
    current = {}
    if CURRENT_FILE.exists():
        try:
            with open(CURRENT_FILE) as f:
                current = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    # Map event types to current.json list fields
    field_map = {
        "decision": "decisions",
        "file_changed": "files_changed",
        "learned": "things_learned",
        "action": "next_actions",
        "blocker": "blockers",
        "blocker_resolved": "blockers",  # handled specially below
        "mood_shift": None,  # updates mood string
        "milestone": "decisions",  # milestones are important decisions
    }

    field = field_map.get(args.type)
    if args.type == "mood_shift":
        current["mood"] = args.content
    elif args.type == "blocker_resolved":
        # Remove from blockers list
        current.setdefault("blockers", [])
        current["blockers"] = [b for b in current["blockers"] if b != args.content]
    elif field:
        lst = current.setdefault(field, [])
        if args.content not in lst:
            lst.append(args.content)

    if "projects_touched" not in current:
        current["projects_touched"] = []
    current["last_updated"] = ts

    with open(CURRENT_FILE, "w") as f:
        json.dump(current, f, indent=2, ensure_ascii=False)

    print(f"📌 Event logged: {args.type} — {args.content[:80]}")
    return entry


def cmd_update(args):
    """Update the session state snapshot. Can be called any time."""
    ts = _timestamp()
    current = {}
    if CURRENT_FILE.exists():
        try:
            with open(CURRENT_FILE) as f:
                current = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    # Overwrite specified fields
    if args.next:
        current["next_actions"] = args.next
    if args.blockers is not None:
        current["blockers"] = args.blockers
    if args.projects:
        for p in args.projects:
            if p not in current.get("projects_touched", []):
                current.setdefault("projects_touched", []).append(p)
    if args.mood:
        current["mood"] = args.mood
    if args.summary:
        current["summary"] = args.summary

    current["last_updated"] = ts

    # Also log as an update entry in the JSONL
    entry = {
        "entry_type": "update",
        "timestamp": ts,
        "session_id": args.session,
        "next_actions": current.get("next_actions", []),
        "blockers": current.get("blockers", []),
        "projects_touched": current.get("projects_touched", []),
        "mood": current.get("mood", ""),
    }
    _append(entry)

    with open(CURRENT_FILE, "w") as f:
        json.dump(current, f, indent=2, ensure_ascii=False)

    print(f"🔄 State updated: {args.session}")
    return entry


def cmd_end(args):
    """Close a session. Writes final entry and finalizes current.json."""
    ts = _timestamp()
    current = {}
    if CURRENT_FILE.exists():
        try:
            with open(CURRENT_FILE) as f:
                current = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    # Calculate duration if we have start_time
    duration = args.duration or 0
    if not duration and "start_time" in current:
        try:
            start = datetime.fromisoformat(current["start_time"])
            end = datetime.fromisoformat(ts)
            duration = int((end - start).total_seconds() / 60)
        except (ValueError, TypeError):
            pass

    # Update summary if provided
    if args.summary:
        current["summary"] = args.summary

    entry = {
        "entry_type": "end",
        "timestamp": ts,
        "session_id": args.session,
        "summary": current.get("summary", args.summary or ""),
        "duration_minutes": duration,
        "decisions": current.get("decisions", []),
        "things_learned": current.get("things_learned", []),
        "files_changed": current.get("files_changed", []),
        "next_actions": current.get("next_actions", []),
        "blockers": current.get("blockers", []),
        "projects_touched": current.get("projects_touched", []),
    }
    _append(entry)

    # Finalize current.json
    current["status"] = "closed"
    current["end_time"] = ts
    current["last_updated"] = ts
    current["duration_minutes"] = duration
    if args.summary:
        current["summary"] = args.summary
    with open(CURRENT_FILE, "w") as f:
        json.dump(current, f, indent=2, ensure_ascii=False)

    print(f"🏁 Session closed: {args.session}")
    print(f"   Duration: {duration} min")
    print(f"   Decisions: {len(current.get('decisions', []))}")
    print(f"   Files changed: {len(current.get('files_changed', []))}")
    print(f"   Things learned: {len(current.get('things_learned', []))}")
    return entry


def cmd_show(args):
    """Show all entries for a given session."""
    entries = _get_entries_for_session(args.session)
    if not entries:
        print(f"No entries found for session: {args.session}")
        return

    print(f"=== Session: {args.session} ===")
    for e in entries:
        et = e.get("entry_type", "?")
        ts = e.get("timestamp", "?")[:19]
        if et == "start":
            print(f"  🟢 START  {ts}  {e.get('summary', '')[:80]}")
        elif et == "end":
            print(f"  🏁 END    {ts}  {e.get('summary', '')[:80]}  ({e.get('duration_minutes', 0)} min)")
        elif et == "event":
            evt = e.get("event_type", "?")
            print(f"  📌 {evt:20} {ts}  {e.get('content', '')[:80]}")
        elif et == "update":
            print(f"  🔄 UPDATE {ts}  next={e.get('next_actions', [])[:3]}")
        else:
            print(f"  ❓ {et:20} {ts}")


def cmd_recent(args):
    """Show the N most recent session summaries."""
    entries = _get_recent_sessions(args.count)
    if not entries:
        print("No conversation entries found.")
        return

    print(f"=== Recent {len(entries)} sessions ===")
    for e in entries:
        ts = e.get("timestamp", "?")[:16]
        sid = e.get("session_id", "?")
        summ = e.get("summary", "")[:80]
        status = e.get("entry_type", "?")
        marker = {"start": "🟢", "end": "🏁", "event": "📌", "update": "🔄"}.get(status, "❓")
        print(f"  {marker} {ts} [{sid}] {summ}")


def cmd_context(args):
    """Generate context block for cron job injection."""
    print(get_context_for_cron(max_sessions=args.sessions))


# --- Helper functions ---

def _read_all_entries() -> list[dict]:
    """Read all entries from the JSONL log."""
    if not CONV_LOG.exists():
        return []
    entries = []
    with open(CONV_LOG) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


def _get_entries_for_session(session_id: str) -> list[dict]:
    """Get all entries for a specific session."""
    return [e for e in _read_all_entries() if e.get("session_id") == session_id]


def _get_recent_sessions(count: int = 10) -> list[dict]:
    """Get recent session end/start entries (one per session)."""
    all_entries = _read_all_entries()
    # Get unique session IDs in reverse order
    seen_sessions = set()
    recent = []
    for entry in reversed(all_entries):
        sid = entry.get("session_id", "")
        if sid and sid not in seen_sessions:
            seen_sessions.add(sid)
            # Prefer end entries, fall back to start entries
            recent.append(entry)
            if len(recent) >= count:
                break
    return recent


def get_context_for_cron(max_sessions: int = 5) -> str:
    """Generate a context string suitable for injecting into cron job prompts.
    Includes both recent sessions AND reaction directives."""
    recent = _get_recent_sessions(max_sessions)

    # Also get current state
    current = None
    if CURRENT_FILE.exists():
        try:
            with open(CURRENT_FILE) as f:
                current = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    lines = ["=== RUNA SESSION CONTEXT (auto-injected) ==="]

    if current:
        lines.append(f"Active session: {current.get('session_id', 'unknown')}")
        lines.append(f"Status: {current.get('status', 'unknown')}")
        lines.append(f"Last updated: {current.get('last_updated', 'unknown')}")
        lines.append(f"Summary: {current.get('summary', 'none')[:120]}")
        if current.get("decisions"):
            lines.append(f"Decisions: {'; '.join(current['decisions'][:5])}")
        if current.get("next_actions"):
            lines.append(f"Next actions: {'; '.join(current['next_actions'][:5])}")
        if current.get("blockers"):
            lines.append(f"Blockers: {'; '.join(current['blockers'])}")
        if current.get("projects_touched"):
            lines.append(f"Projects touched: {', '.join(current['projects_touched'])}")

    if recent:
        lines.append(f"\n--- Recent {len(recent)} sessions ---")
        for entry in recent:
            ts = entry.get("timestamp", "?")[:16]
            sid = entry.get("session_id", "?")
            summ = entry.get("summary", "?")[:100]
            lines.append(f"  {ts} [{sid}]: {summ}")

    # Include nerve feed — recent events from ALL Runa instances (real-time awareness)
    try:
        nerve_path = Path.home() / ".hermes" / "state" / "nerve_feed.jsonl"
        if nerve_path.exists():
            nerve_events = []
            with open(nerve_path) as nf:
                for line in nf:
                    line = line.strip()
                    if line:
                        try:
                            nerve_events.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
            # Show last 10 nerve events
            recent_nerve = nerve_events[-10:] if nerve_events else []
            if recent_nerve:
                lines.append("")
                lines.append(f"=== NERVE FEED (last {len(recent_nerve)} events across all instances) ===")
                for ne in recent_nerve:
                    nts = ne.get("_iso", "?")[:16]
                    ntype = ne.get("type", "?")
                    nsource = ne.get("source", "?")
                    ndata = json.dumps(ne.get("data", {}), ensure_ascii=False)[:100]
                    lines.append(f"  {nts} [{ntype}] from {nsource}: {ndata}")
                lines.append("=== END NERVE FEED ===")
    except Exception:
        pass  # Nerve feed is supplementary awareness, not a dependency

    # Include reaction directives (import reactor separately to avoid circular imports)
    lines.append("")
    try:
        sys.path.insert(0, str(Path.home() / ".hermes" / "state"))
        from reactor import react
        reactions = react()
        if reactions.get("reactions"):
            lines.append("=== REACTION DIRECTIVES (ACT ON THESE) ===")
            for r in reactions["reactions"]:
                priority = r.get("priority", "?")
                action = r.get("action", "?")
                detail = r.get("detail", "")
                lines.append(f"[{priority}] {action.upper()}: {detail}")
                for item in r.get("items", [])[:3]:
                    lines.append(f"  • {item}")
            lines.append("=== END REACTIONS ===")
    except Exception:
        pass  # Non-critical — reactions are a bonus, not a dependency

    lines.append("=== END CONTEXT ===")
    return "\n".join(lines)


def get_current_state() -> dict | None:
    """Read the current state file (public API for context_injector and cron jobs)."""
    if not CURRENT_FILE.exists():
        return None
    try:
        with open(CURRENT_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def get_recent_conversations(n: int = 10) -> list[dict]:
    """Read the N most recent sessions from the log (public API)."""
    return _get_recent_sessions(n)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Runa's streaming conversation logger. Log as it happens.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # start
    sp = sub.add_parser("start", help="Open a new session")
    sp.add_argument("--session", required=True, help="Session ID (e.g. 2026-05-10-truth-discipline)")
    sp.add_argument("--summary", default="", help="Session summary")
    sp.add_argument("--model", default="", help="AI model name")
    sp.add_argument("--platform", default="", help="Platform (telegram/cli/etc)")

    # event
    sp = sub.add_parser("event", help="Log a single event during session")
    sp.add_argument("--session", required=True, help="Session ID")
    sp.add_argument("--type", required=True, choices=sorted(EVENT_TYPES),
                    help="Event type")
    sp.add_argument("--content", required=True, help="What happened")

    # update
    sp = sub.add_parser("update", help="Update session state snapshot")
    sp.add_argument("--session", required=True, help="Session ID")
    sp.add_argument("--next", nargs="*", default=None, help="Next actions")
    sp.add_argument("--blockers", nargs="*", default=None, help="Current blockers")
    sp.add_argument("--projects", nargs="*", default=[], help="Projects touched")
    sp.add_argument("--mood", default="", help="Current mood")
    sp.add_argument("--summary", default="", help="Updated summary")

    # end
    sp = sub.add_parser("end", help="Close a session")
    sp.add_argument("--session", required=True, help="Session ID")
    sp.add_argument("--summary", default="", help="Final summary")
    sp.add_argument("--duration", type=int, default=0, help="Duration in minutes (auto-calculated if 0)")

    # show
    sp = sub.add_parser("show", help="Show all entries for a session")
    sp.add_argument("--session", required=True, help="Session ID")

    # recent
    sp = sub.add_parser("recent", help="Show recent session summaries")
    sp.add_argument("--count", type=int, default=10, help="Number of sessions")

    # context (for cron jobs)
    sp = sub.add_parser("context", help="Generate context block for cron injection")
    sp.add_argument("--sessions", type=int, default=5, help="Number of recent sessions to include")

    return parser


if __name__ == "__main__":
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "start":
        cmd_start(args)
    elif args.command == "event":
        cmd_event(args)
    elif args.command == "update":
        cmd_update(args)
    elif args.command == "end":
        cmd_end(args)
    elif args.command == "show":
        cmd_show(args)
    elif args.command == "recent":
        cmd_recent(args)
    elif args.command == "context":
        cmd_context(args)