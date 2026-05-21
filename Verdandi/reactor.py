#!/usr/bin/env python3
"""
Conversation Reactor — Runa's self-awareness and self-reaction system.

Reads the conversation log and current state, then produces REACTION
directives: what needs attention, what to follow up on, what to
celebrate, what to investigate, what to fix.

This is the difference between a passive log and a living system.
The log records; the Reactor RESPONDS.

Usage:
    python3 reactor.py                   # Full reaction report
    python3 reactor.py --format brief    # One-line summary
    python3 reactor.py --format json    # Machine-readable JSON
    python3 reactor.py --focus blockers  # Only show blockers needing reaction
"""

import argparse
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

STATE_DIR = Path.home() / ".hermes" / "state"
CONV_LOG = STATE_DIR / "conversation_log.jsonl"
CURRENT_FILE = STATE_DIR / "current.json"


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


def _get_current_state() -> dict | None:
    """Read the current state file."""
    if not CURRENT_FILE.exists():
        return None
    try:
        with open(CURRENT_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def _parse_timestamp(ts: str) -> datetime | None:
    """Parse an ISO timestamp string."""
    try:
        return datetime.fromisoformat(ts)
    except (ValueError, TypeError):
        return None


def react(focus: str = "all") -> dict:
    """
    Analyze conversation log and produce reaction directives.
    
    This is the CORE intelligence of the system — not just reading
    what happened, but deciding what to DO about it.
    """
    entries = _read_all_entries()
    current = _get_current_state()
    now = datetime.now(timezone.utc)
    
    reactions = {
        "blockers_needing_reaction": [],      # Things that are stuck and need action
        "decisions_needing_followup": [],       # Decisions made but not yet acted on
        "recent_learnings_to_store": [],        # Things learned that should go to Mímir
        "files_changed_needing_push": [],       # Files modified that might need committing
        "milestones_to_acknowledge": [],        # Achievements worth celebrating
        "next_actions_to_pick_up": [],          # Planned next steps from last session
        "stale_sessions_to_close": [],          # Sessions that started but never ended
        "cron_events_to_review": [],            # Recent cron events that need attention
        "reactions": [],                         # Specific reaction directives
    }
    
    # Track unique blockers, decisions, etc.
    seen_blockers = set()
    seen_decisions = set()
    seen_learnings = set()
    seen_files = set()
    
    # Get active session's blockers (resolved blockers are removed)
    resolved_blockers = set()
    active_blockers = set()
    
    # Process entries in order — most recent last
    for entry in entries:
        et = entry.get("entry_type", "")
        ts = entry.get("timestamp", "")
        
        # Track stale sessions (started but never ended)
        if et == "start":
            session_id = entry.get("session_id", "")
            # Check if there's a matching end entry
            has_end = any(
                e.get("entry_type") == "end" and e.get("session_id") == session_id
                for e in entries
            )
            if not has_end:
                # Is it a recent session or a truly stale one?
                start_time = _parse_timestamp(ts)
                if start_time:
                    age = (now - start_time).total_seconds()
                    if age > 3600:  # More than 1 hour old and no end
                        reactions["stale_sessions_to_close"].append({
                            "session_id": session_id,
                            "started": ts,
                            "age_hours": round(age / 3600, 1),
                            "reaction": f"Session {session_id} started {round(age/3600, 1)}h ago with no END entry. Close it or investigate."
                        })
        
        # Track blockers and resolutions
        if et == "event" and entry.get("event_type") == "blocker":
            content = entry.get("content", "")
            if content not in resolved_blockers:
                active_blockers.add(content)
        
        if et == "event" and entry.get("event_type") == "blocker_resolved":
            content = entry.get("content", "")
            resolved_blockers.add(content)
            active_blockers.discard(content)
        
        # Track decisions
        if et == "event" and entry.get("event_type") == "decision":
            content = entry.get("content", "")
            if content not in seen_decisions:
                seen_decisions.add(content)
                decisions_data = {"content": content, "timestamp": ts, "session": entry.get("session_id", "")}
                # Is this from the active/current session? Prioritize.
                if current and entry.get("session_id") == current.get("session_id"):
                    decisions_data["active_session"] = True
                reactions["decisions_needing_followup"].append(decisions_data)
        
        # Track learnings
        if et == "event" and entry.get("event_type") == "learned":
            content = entry.get("content", "")
            if content not in seen_learnings:
                seen_learnings.add(content)
                reactions["recent_learnings_to_store"].append({
                    "content": content,
                    "timestamp": ts,
                    "session": entry.get("session_id", ""),
                    "reaction": f"Store in Mímir: runa_remember action=memory category=lesson content=\"{content}\""
                })
        
        # Track files changed
        if et == "event" and entry.get("event_type") == "file_changed":
            content = entry.get("content", "")
            if content not in seen_files:
                seen_files.add(content)
                reactions["files_changed_needing_push"].append({
                    "file": content,
                    "timestamp": ts,
                    "session": entry.get("session_id", ""),
                    "reaction": f"Check if {content} is committed and pushed"
                })
        
        # Track milestones
        if et == "event" and entry.get("event_type") == "milestone":
            content = entry.get("content", "")
            reactions["milestones_to_acknowledge"].append({
                "content": content,
                "timestamp": ts,
                "session": entry.get("session_id", ""),
                "reaction": f"Acknowledge: {content}"
            })
        
        # Track cron events (from platform=cron)
        if entry.get("platform") == "cron" or (entry.get("session_id", "").startswith("202") and "vault-keeper" in entry.get("session_id", "")):
            if et == "event":
                reactions["cron_events_to_review"].append({
                    "type": entry.get("event_type", ""),
                    "content": entry.get("content", ""),
                    "timestamp": ts,
                    "session": entry.get("session_id", ""),
                })
    
    # Active blockers (not resolved)
    for blocker in active_blockers:
        if blocker not in seen_blockers:
            seen_blockers.add(blocker)
            reactions["blockers_needing_reaction"].append({
                "content": blocker,
                "reaction": f"UNRESOLVED BLOCKER: {blocker}. Investigate, resolve, or log blocker_resolved."
            })
    
    # Get current session's next actions
    if current and current.get("next_actions"):
        for action in current["next_actions"]:
            reactions["next_actions_to_pick_up"].append({
                "content": action,
                "reaction": f"PICK UP: {action}"
            })
    
    # Generate top-level reaction directives
    if reactions["blockers_needing_reaction"]:
        reactions["reactions"].append({
            "priority": "HIGH",
            "action": "resolve_blockers",
            "detail": f"{len(reactions['blockers_needing_reaction'])} unresolved blocker(s) need attention",
            "items": [b["reaction"] for b in reactions["blockers_needing_reaction"]]
        })
    
    if reactions["stale_sessions_to_close"]:
        reactions["reactions"].append({
            "priority": "MEDIUM",
            "action": "close_stale_sessions",
            "detail": f"{len(reactions['stale_sessions_to_close'])} session(s) started but never closed",
            "items": [s["reaction"] for s in reactions["stale_sessions_to_close"]]
        })
    
    if reactions["files_changed_needing_push"]:
        reactions["reactions"].append({
            "priority": "MEDIUM",
            "action": "verify_pushed",
            "detail": f"{len(reactions['files_changed_needing_push'])} file(s) changed — verify they're committed and pushed",
            "items": [f["reaction"] for f in reactions["files_changed_needing_push"]]
        })
    
    if reactions["recent_learnings_to_store"]:
        reactions["reactions"].append({
            "priority": "MEDIUM",
            "action": "store_learnings",
            "detail": f"{len(reactions['recent_learnings_to_store'])} learning(s) should be stored in Mímir",
            "items": [l["reaction"] for l in reactions["recent_learnings_to_store"]]
        })
    
    if reactions["next_actions_to_pick_up"]:
        reactions["reactions"].append({
            "priority": "LOW",
            "action": "continue_work",
            "detail": f"{len(reactions['next_actions_to_pick_up'])} next action(s) from last session",
            "items": [a["reaction"] for a in reactions["next_actions_to_pick_up"]]
        })
    
    if reactions["milestones_to_acknowledge"]:
        reactions["reactions"].append({
            "priority": "INFO",
            "action": "celebrate",
            "detail": f"{len(reactions['milestones_to_acknowledge'])} milestone(s) achieved",
            "items": [m["reaction"] for m in reactions["milestones_to_acknowledge"]]
        })
    
    return reactions


def format_reactions(reactions: dict, fmt: str = "text") -> str:
    """Format reactions for output."""
    if fmt == "json":
        return json.dumps(reactions, indent=2, ensure_ascii=False)
    
    if fmt == "brief":
        # One-line summary
        n_blockers = len(reactions.get("blockers_needing_reaction", []))
        n_learnings = len(reactions.get("recent_learnings_to_store", []))
        n_files = len(reactions.get("files_changed_needing_push", []))
        n_next = len(reactions.get("next_actions_to_pick_up", []))
        n_stale = len(reactions.get("stale_sessions_to_close", []))
        n_milestones = len(reactions.get("milestones_to_acknowledge", []))
        parts = []
        if n_blockers: parts.append(f"🚨 {n_blockers} blocker(s)")
        if n_stale: parts.append(f"⚠️ {n_stale} stale session(s)")
        if n_files: parts.append(f"📁 {n_files} file(s) to push")
        if n_learnings: parts.append(f"🧠 {n_learnings} learning(s) to store")
        if n_next: parts.append(f"➡️ {n_next} next action(s)")
        if n_milestones: parts.append(f"🎯 {n_milestones} milestone(s)")
        if not parts: return "✅ No reactions needed — system is clean"
        return " | ".join(parts)
    
    # Full text format
    lines = ["=== REACTION REPORT ==="]
    
    for reaction in reactions.get("reactions", []):
        priority = reaction.get("priority", "?")
        action = reaction.get("action", "?")
        detail = reaction.get("detail", "")
        items = reaction.get("items", [])
        
        lines.append(f"\n[{priority}] {action.upper()}: {detail}")
        for item in items:
            lines.append(f"  • {item}")
    
    # Detailed sections
    if reactions.get("blockers_needing_reaction"):
        lines.append("\n🚨 BLOCKERS NEEDING REACTION:")
        for b in reactions["blockers_needing_reaction"]:
            lines.append(f"  • {b['reaction']}")
    
    if reactions.get("stale_sessions_to_close"):
        lines.append("\n⚠️ STALE SESSIONS (no END entry):")
        for s in reactions["stale_sessions_to_close"]:
            lines.append(f"  • {s['reaction']}")
    
    if reactions.get("files_changed_needing_push"):
        lines.append("\n📁 FILES CHANGED (verify push):")
        for f in reactions["files_changed_needing_push"]:
            lines.append(f"  • {f['reaction']}")
    
    if reactions.get("recent_learnings_to_store"):
        lines.append("\n🧠 LEARNINGS TO STORE IN MÍMIR:")
        for l in reactions["recent_learnings_to_store"]:
            lines.append(f"  • {l['reaction']}")
    
    if reactions.get("decisions_needing_followup"):
        lines.append("\n📋 DECISIONS MADE (follow up):")
        for d in reactions["decisions_needing_followup"]:
            active = " [ACTIVE SESSION]" if d.get("active_session") else ""
            lines.append(f"  • {d['content']}{active}")
    
    if reactions.get("next_actions_to_pick_up"):
        lines.append("\n➡️ NEXT ACTIONS TO PICK UP:")
        for a in reactions["next_actions_to_pick_up"]:
            lines.append(f"  • {a['reaction']}")
    
    if reactions.get("milestones_to_acknowledge"):
        lines.append("\n🎯 MILESTONES:")
        for m in reactions["milestones_to_acknowledge"]:
            lines.append(f"  • {m['reaction']}")
    
    lines.append("\n=== END REACTIONS ===")
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Runa's conversation reactor — self-awareness and reaction system")
    parser.add_argument("--format", choices=["text", "json", "brief"], default="text",
                       help="Output format (default: text)")
    parser.add_argument("--focus", choices=["all", "blockers", "learnings", "files", "next"],
                       default="all", help="Focus area (default: all)")
    
    args = parser.parse_args()
    reactions = react(focus=args.focus)
    output = format_reactions(reactions, fmt=args.format)
    print(output)