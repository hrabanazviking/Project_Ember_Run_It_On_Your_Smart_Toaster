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

    # Delete (the user's delete right, E-063 — total and provable)
    python3 conversation_logger.py delete --session 2026-05-10-truth-discipline
    python3 conversation_logger.py delete --all --yes
"""

import argparse
import gzip
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

# Context injection budget (E-062) — the literals below are the
# deployed copies of Verdandi/context_budget.py's values. They
# are literals, not imports, because this file is deployed and
# loaded standalone, file-by-file, from ~/.hermes/state (the
# E-061 pattern); the E-062 conformance tests pin the two copies
# equal so they cannot drift.
_CONTEXT_TOTAL_MAX_CHARS = 4000
_CONTEXT_CURRENT_MAX_CHARS = 1200
_CONTEXT_RECENT_MAX_CHARS = 700
_CONTEXT_NERVE_MAX_CHARS = 1000
_CONTEXT_REACTIONS_MAX_CHARS = 1100
_CONTEXT_SUMMARY_MAX_CHARS = 120
_CONTEXT_RECENT_SUMMARY_MAX_CHARS = 100
_CONTEXT_DECISIONS_MAX_ITEMS = 5
_CONTEXT_NEXT_ACTIONS_MAX_ITEMS = 5
_CONTEXT_BLOCKERS_MAX_ITEMS = 10
_CONTEXT_PROJECTS_MAX_ITEMS = 10
_CONTEXT_LIST_ITEM_MAX_CHARS = 120
_CONTEXT_PROJECT_ITEM_MAX_CHARS = 60
_CONTEXT_BLOCKERS_JOIN_MAX_CHARS = 600
_CONTEXT_DECISIONS_JOIN_MAX_CHARS = 300
_CONTEXT_NEXT_ACTIONS_JOIN_MAX_CHARS = 300
_CONTEXT_PROJECTS_JOIN_MAX_CHARS = 300
_CONTEXT_RECENT_MAX_SESSIONS = 5
_CONTEXT_NERVE_MAX_EVENTS = 10
_CONTEXT_NERVE_DATA_MAX_CHARS = 100
_CONTEXT_NERVE_SOURCE_MAX_CHARS = 60
_CONTEXT_NERVE_TYPE_MAX_CHARS = 60
_CONTEXT_REACTIONS_MAX_DIRECTIVES = 6
_CONTEXT_REACTIONS_ITEMS_PER_DIRECTIVE = 3
_CONTEXT_REACTION_ITEM_MAX_CHARS = 120
_CONTEXT_REACTION_DETAIL_MAX_CHARS = 120
_CONTEXT_TRUNCATION_MARKER = "[... truncated by context budget E-062]"


def _ctx_truncate(text, limit: int) -> str:
    """Truncate text to at most limit chars, marking the cut (E-062)."""
    text = str(text)
    if len(text) <= limit:
        return text
    marker = _CONTEXT_TRUNCATION_MARKER
    if limit <= len(marker):
        return text[:limit]
    return text[: limit - len(marker)] + marker


def _ctx_cap(items, max_items: int, max_chars: int) -> list:
    """Cap a list in both dimensions: count and per-item length (E-062)."""
    return [_ctx_truncate(item, max_chars) for item in list(items)[:max_items]]


def _ctx_fit(lines: list, cap: int, *, drop: str = "tail",
             protected_head: int = 0, protected_tail: int = 0) -> list:
    """Fit a section's lines under its char ceiling (E-062).

    Whole lines shed first — from the tail, or from the head of
    the droppable region when drop="head" (the nerve tail sheds
    its oldest events, keeping the newest) — and the truncation
    marker is left in the block so a shortened layer never
    pretends to be the whole story. Protected head/tail lines
    (section headers/footers) are never shed; if protected lines
    alone exceed the cap, they are text-truncated as a last
    resort.
    """
    lines = list(lines)
    marker = _CONTEXT_TRUNCATION_MARKER

    def _joined(extra=()):
        return len("\n".join([*lines, *extra]))

    if _joined() <= cap:
        return lines
    while len(lines) > protected_head + protected_tail and _joined((marker,)) > cap:
        if drop == "head":
            del lines[protected_head]
        else:
            del lines[len(lines) - protected_tail - 1]
    insert_at = len(lines) - protected_tail if protected_tail else len(lines)
    lines.insert(insert_at, marker)
    if _joined() > cap:  # protected lines alone are too long
        text = "\n".join(lines)
        return [_ctx_truncate(text, cap)]
    return lines


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


# Cached module reference — avoids re-importing on every event
_nerve_module = None
_nerve_module_path = None


def _nerve_candidate_paths():
    """Where the nerve hub module may live, in search order (E-067).

    The deployed copy (~/.hermes/state/nervous_system.py) wins
    wherever one exists — deployed behaviour is unchanged. The
    sibling copy beside this file is the fallback, so the
    conversation layer works from this tree with no deployment
    step (docket 94, E-067 half; the standalone half is E-073's).
    """
    return [
        STATE_DIR / "nervous_system.py",
        Path(__file__).resolve().parent / "nervous_system.py",
    ]


def _nerve_fire(entry: dict):
    """Fire a nerve impulse — publish event to the nervous system for real-time awareness.

    Uses a cached module reference to avoid the overhead and risk of
    re-importing nervous_system.py on every call. If the module file changes
    on disk (e.g. updated), the cache is refreshed automatically.
    """
    global _nerve_module, _nerve_module_path
    try:
        nerve_path = next((p for p in _nerve_candidate_paths() if p.exists()), None)
        if nerve_path is None:
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


def _load_current() -> dict:
    """Read current.json, or {} when it is missing or corrupt."""
    if CURRENT_FILE.exists():
        try:
            with open(CURRENT_FILE) as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def _current_owned_by(session_id: str) -> bool:
    """Whether current.json belongs to ``session_id`` (E-063).

    current.json is the LATEST session's snapshot: the session
    that ran ``start`` most recently owns it, and only that
    session's own event/update/end commands may change it.
    An entry logged for another session is still appended to
    the log — the log is the truth — but it never rewrites
    another session's snapshot. (This settles docket 98: the
    former _update_current helper was dead code, and the
    cmd_* commands' hand-rolled merges diverged on exactly
    this point; the merges below are now the law, uniformly.)
    A missing or ownerless current.json counts as owned, so
    the pre-E-063 behaviour for a first command stands.
    """
    owner = _load_current().get("session_id")
    return owner is None or owner == session_id


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

    # Update current.json — accumulate into appropriate list field,
    # but only when current.json belongs to this session (E-063).
    if not _current_owned_by(args.session):
        print(f"📌 Event logged: {args.type} — {args.content[:80]}")
        return entry
    current = _load_current()

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
    # Only the owning session's snapshot may be updated (E-063);
    # for any other session the update entry is built from this
    # command's own arguments and current.json is left alone.
    owned = _current_owned_by(args.session)
    current = _load_current() if owned else {
        "next_actions": [],
        "blockers": [],
        "projects_touched": [],
        "mood": "",
    }

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

    if owned:
        with open(CURRENT_FILE, "w") as f:
            json.dump(current, f, indent=2, ensure_ascii=False)

    print(f"🔄 State updated: {args.session}")
    return entry


def cmd_end(args):
    """Close a session. Writes final entry and finalizes current.json."""
    ts = _timestamp()
    # Only the owning session may finalise current.json, and its
    # end entry is built from its own snapshot (E-063); ending a
    # session that does not own current.json logs the end entry
    # from this command's arguments alone and leaves the active
    # session's snapshot untouched.
    owned = _current_owned_by(args.session)
    current = _load_current() if owned else {}

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

    if not owned:
        print(f"🏁 Session closed: {args.session}")
        print(f"   Duration: {duration} min")
        return entry

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


# --- The user's delete right (E-063): total, and provable ---


def _is_nerve_copy_of(entry, session_id: str | None) -> bool:
    """Whether a nerve-feed entry is a conv_* copy of a logged entry.

    The logger fires every appended entry to the hub as
    ``conv_<entry_type>`` with the whole entry as ``data`` and
    source ``conv_logger:<session_id>`` (E-061 contract), so a
    copy matches on type prefix plus either the source tag or
    the copied entry's own session_id. With ``session_id``
    None, every conv_* copy matches (the delete-all scope).
    """
    if not isinstance(entry, dict):
        return False
    if not str(entry.get("type", "")).startswith("conv_"):
        return False
    if session_id is None:
        return True
    if entry.get("source") == f"conv_logger:{session_id}":
        return True
    data = entry.get("data")
    return isinstance(data, dict) and data.get("session_id") == session_id


def _purge_jsonl(path: Path, matches) -> tuple[int, int]:
    """Atomically drop the lines of ``path`` whose JSON entry matches.

    Returns (removed, unattributed_kept). Lines that are not
    valid JSON objects are unattributable: they are kept
    verbatim and counted, never silently dropped — the logger
    cannot prove whose they are. Kept lines are preserved
    byte-for-byte. The rewrite goes through a temporary file
    in the same directory and os.replace, so a crash leaves
    the old file or the new one, never a torn one. A file
    with nothing to remove is left untouched.
    """
    if not path.exists():
        return 0, 0
    kept: list[str] = []
    removed = 0
    unattributed = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                kept.append(line)
                continue
            try:
                entry = json.loads(stripped)
            except json.JSONDecodeError:
                entry = None
            if not isinstance(entry, dict):
                unattributed += 1
                kept.append(line)
            elif matches(entry):
                removed += 1
            else:
                kept.append(line)
    if removed == 0:
        return 0, unattributed
    tmp = path.with_name(path.name + ".tmp-e063")
    with open(tmp, "w", encoding="utf-8") as f:
        f.writelines(kept)
    os.replace(tmp, path)
    return removed, unattributed


def _purge_jsonl_gz(path: Path, matches) -> tuple[int, int]:
    """The _purge_jsonl discipline for a gzip-compressed feed archive."""
    if not path.exists():
        return 0, 0
    kept: list[str] = []
    removed = 0
    unattributed = 0
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                kept.append(line)
                continue
            try:
                entry = json.loads(stripped)
            except json.JSONDecodeError:
                entry = None
            if not isinstance(entry, dict):
                unattributed += 1
                kept.append(line)
            elif matches(entry):
                removed += 1
            else:
                kept.append(line)
    if removed == 0:
        return 0, unattributed
    tmp = path.with_name(path.name + ".tmp-e063")
    with gzip.open(tmp, "wt", encoding="utf-8") as f:
        f.writelines(kept)
    os.replace(tmp, path)
    return removed, unattributed


def _nerve_store_paths() -> list[Path]:
    """Every state-dir file holding nerve-feed entries: the live
    feed plus its rotated archives (plain and compressed)."""
    paths = [STATE_DIR / "nerve_feed.jsonl"]
    for pattern in ("nerve_feed_*.jsonl", "nerve_feed_*.jsonl.gz"):
        paths.extend(sorted(STATE_DIR.glob(pattern)))
    return paths


def _count_nerve_copies(session_id: str | None) -> int:
    """Count conv_* copies for a session (None = all) across the
    live feed and every rotated archive — the verification read."""
    total = 0
    for path in _nerve_store_paths():
        if not path.exists():
            continue
        try:
            opener = gzip.open if path.name.endswith(".gz") else open
            with opener(path, "rt", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if _is_nerve_copy_of(entry, session_id):
                        total += 1
        except (OSError, EOFError):
            continue
    return total


def delete_session(session_id: str) -> dict:
    """Delete ONE session, totally, and prove it (E-063).

    Removes the session's entries from conversation_log.jsonl,
    current.json if (and only if) it belongs to the session,
    and the session's conv_* copies from the nerve feed and
    its rotated archives. Afterwards every affected store is
    re-read and the remaining attributable count must be
    zero for the report to claim verification.
    """
    removed_log, unattributed = _purge_jsonl(
        CONV_LOG, lambda e: e.get("session_id") == session_id)

    current_removed = False
    current = get_current_state()
    if current is not None and current.get("session_id") == session_id:
        CURRENT_FILE.unlink()
        current_removed = True

    removed_nerve = 0
    for path in _nerve_store_paths():
        purge = _purge_jsonl_gz if path.name.endswith(".gz") else _purge_jsonl
        n, u = purge(path, lambda e: _is_nerve_copy_of(e, session_id))
        removed_nerve += n
        unattributed += u

    remaining = (
        len(_get_entries_for_session(session_id))
        + _count_nerve_copies(session_id)
        + (1 if (get_current_state() or {}).get("session_id") == session_id else 0)
    )
    return {
        "scope": "session",
        "session_id": session_id,
        "log_entries_removed": removed_log,
        "current_removed": current_removed,
        "nerve_entries_removed": removed_nerve,
        "unattributed_lines_kept": unattributed,
        "remaining_attributable": remaining,
        "verified": remaining == 0,
    }


def delete_all_conversations() -> dict:
    """Delete EVERY logged conversation, totally, and prove it (E-063).

    The log and current.json are removed outright; every
    conv_* copy leaves the nerve feed and its archives (non-
    conversation feed events are not the logger's words and
    are kept). Verification re-reads every store.
    """
    removed_log = len(_read_all_entries())
    unattributed = 0
    if CONV_LOG.exists():
        with open(CONV_LOG, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    entry = None
                if not isinstance(entry, dict):
                    unattributed += 1
        CONV_LOG.unlink()

    current_removed = False
    if CURRENT_FILE.exists():
        CURRENT_FILE.unlink()
        current_removed = True

    removed_nerve = 0
    for path in _nerve_store_paths():
        purge = _purge_jsonl_gz if path.name.endswith(".gz") else _purge_jsonl
        n, u = purge(path, lambda e: _is_nerve_copy_of(e, None))
        removed_nerve += n
        unattributed += u

    remaining = (
        len(_read_all_entries())
        + _count_nerve_copies(None)
        + (1 if CURRENT_FILE.exists() else 0)
    )
    return {
        "scope": "all",
        "session_id": None,
        "log_entries_removed": removed_log,
        "current_removed": current_removed,
        "nerve_entries_removed": removed_nerve,
        "unattributed_lines_kept": unattributed,
        "remaining_attributable": remaining,
        "verified": remaining == 0,
    }


def cmd_delete(args):
    """The user's delete right (E-063): one session, or all of it.

    Deleting everything requires --yes: a session can be
    named exactly, "everything" cannot, so the extra word is
    the confirmation.
    """
    if getattr(args, "all", False):
        if not getattr(args, "yes", False):
            print("❌ Refusing to delete ALL conversations without --yes.")
            print("   Run: delete --all --yes   (this cannot be undone)")
            sys.exit(2)
        report = delete_all_conversations()
        label = "all conversations"
    else:
        report = delete_session(args.session)
        label = f"session {args.session}"

    print(f"🗑️  Deleted {label}:")
    print(f"   Log entries removed: {report['log_entries_removed']}")
    print(f"   Current snapshot removed: {'yes' if report['current_removed'] else 'no'}")
    print(f"   Nerve-feed copies removed: {report['nerve_entries_removed']}")
    if report["unattributed_lines_kept"]:
        print(f"   Unattributable lines kept (not provably anyone's): "
              f"{report['unattributed_lines_kept']}")
    if report["verified"]:
        print("   Verified: 0 attributable entries remain in any store.")
    else:
        print(f"   ⚠️  NOT VERIFIED: {report['remaining_attributable']} "
              "attributable entries remain.")
        sys.exit(1)
    return report


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
    Includes both recent sessions AND reaction directives.

    The block is built under the E-062 context injection
    discipline (Verdandi/context_budget.py): only the state
    dir's current.json, conversation_log.jsonl summaries, the
    nerve_feed.jsonl tail and reactor directives derived from
    the same log may be injected; every layer is capped in
    items, per-item length and total chars; the whole block
    never exceeds _CONTEXT_TOTAL_MAX_CHARS; and shedding —
    reactions first, then nerve, then recent, current last —
    always leaves the truncation marker in the block.
    """
    # The caller's session count is a request, clamped to the budget.
    try:
        max_sessions = int(max_sessions)
    except (TypeError, ValueError):
        max_sessions = _CONTEXT_RECENT_MAX_SESSIONS
    max_sessions = max(0, min(max_sessions, _CONTEXT_RECENT_MAX_SESSIONS))
    recent = _get_recent_sessions(max_sessions)

    # Also get current state
    current = None
    if CURRENT_FILE.exists():
        try:
            with open(CURRENT_FILE) as f:
                current = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    header = "=== RUNA SESSION CONTEXT (auto-injected) ==="
    footer = "=== END CONTEXT ==="

    # Layer 1 (sheds last): current state, fields in retention
    # order — blockers render before the other lists so line
    # shedding drops projects, then next actions, then
    # decisions, and blockers last of all.
    current_lines: list = []
    if current:
        current_lines.append(f"Active session: {_ctx_truncate(current.get('session_id', 'unknown'), _CONTEXT_LIST_ITEM_MAX_CHARS)}")
        current_lines.append(f"Status: {_ctx_truncate(current.get('status', 'unknown'), _CONTEXT_LIST_ITEM_MAX_CHARS)}")
        current_lines.append(f"Last updated: {_ctx_truncate(current.get('last_updated', 'unknown'), _CONTEXT_LIST_ITEM_MAX_CHARS)}")
        current_lines.append(f"Summary: {_ctx_truncate(current.get('summary', 'none'), _CONTEXT_SUMMARY_MAX_CHARS)}")
        if current.get("blockers"):
            blockers = _ctx_cap(current["blockers"], _CONTEXT_BLOCKERS_MAX_ITEMS, _CONTEXT_LIST_ITEM_MAX_CHARS)
            current_lines.append(f"Blockers: {_ctx_truncate('; '.join(blockers), _CONTEXT_BLOCKERS_JOIN_MAX_CHARS)}")
        if current.get("decisions"):
            decisions = _ctx_cap(current["decisions"], _CONTEXT_DECISIONS_MAX_ITEMS, _CONTEXT_LIST_ITEM_MAX_CHARS)
            current_lines.append(f"Decisions: {_ctx_truncate('; '.join(decisions), _CONTEXT_DECISIONS_JOIN_MAX_CHARS)}")
        if current.get("next_actions"):
            actions = _ctx_cap(current["next_actions"], _CONTEXT_NEXT_ACTIONS_MAX_ITEMS, _CONTEXT_LIST_ITEM_MAX_CHARS)
            current_lines.append(f"Next actions: {_ctx_truncate('; '.join(actions), _CONTEXT_NEXT_ACTIONS_JOIN_MAX_CHARS)}")
        if current.get("projects_touched"):
            projects = _ctx_cap(current["projects_touched"], _CONTEXT_PROJECTS_MAX_ITEMS, _CONTEXT_PROJECT_ITEM_MAX_CHARS)
            current_lines.append(f"Projects touched: {_ctx_truncate(', '.join(projects), _CONTEXT_PROJECTS_JOIN_MAX_CHARS)}")
    current_lines = _ctx_fit(current_lines, _CONTEXT_CURRENT_MAX_CHARS)

    # Layer 2: recent session summaries (one line per session).
    recent_lines: list = []
    if recent:
        recent_lines.append(f"--- Recent {len(recent)} sessions ---")
        for entry in recent:
            ts = str(entry.get("timestamp", "?"))[:16]
            sid = _ctx_truncate(entry.get("session_id", "?"), _CONTEXT_LIST_ITEM_MAX_CHARS)
            summ = _ctx_truncate(entry.get("summary", "?"), _CONTEXT_RECENT_SUMMARY_MAX_CHARS)
            recent_lines.append(f"  {ts} [{sid}]: {summ}")
    recent_lines = _ctx_fit(recent_lines, _CONTEXT_RECENT_MAX_CHARS, protected_head=1 if recent_lines else 0)

    # Layer 3 (supplementary, failure-silent): nerve feed tail,
    # read from the feed FILE in the logger's own state dir —
    # never a live hub query, and never a second home path.
    nerve_lines: list = []
    try:
        nerve_path = STATE_DIR / "nerve_feed.jsonl"
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
            recent_nerve = nerve_events[-_CONTEXT_NERVE_MAX_EVENTS:] if nerve_events else []
            if recent_nerve:
                nerve_lines.append(f"=== NERVE FEED (last {len(recent_nerve)} events across all instances) ===")
                for ne in recent_nerve:
                    nts = str(ne.get("_iso", "?"))[:16]
                    ntype = _ctx_truncate(ne.get("type", "?"), _CONTEXT_NERVE_TYPE_MAX_CHARS)
                    nsource = _ctx_truncate(ne.get("source", "?"), _CONTEXT_NERVE_SOURCE_MAX_CHARS)
                    ndata = _ctx_truncate(json.dumps(ne.get("data", {}), ensure_ascii=False), _CONTEXT_NERVE_DATA_MAX_CHARS)
                    nerve_lines.append(f"  {nts} [{ntype}] from {nsource}: {ndata}")
                nerve_lines.append("=== END NERVE FEED ===")
    except Exception:
        nerve_lines = []  # Nerve feed is supplementary awareness, not a dependency
    if nerve_lines:
        nerve_lines = _ctx_fit(nerve_lines, _CONTEXT_NERVE_MAX_CHARS,
                               drop="head", protected_head=1, protected_tail=1)

    # Layer 4 (supplementary, failure-silent; sheds first):
    # reaction directives derived from the same log.
    reaction_lines: list = []
    try:
        sys.path.insert(0, str(STATE_DIR))
        from reactor import react
        reactions = react()
        if reactions.get("reactions"):
            reaction_lines.append("=== REACTION DIRECTIVES (ACT ON THESE) ===")
            for r in reactions["reactions"][:_CONTEXT_REACTIONS_MAX_DIRECTIVES]:
                priority = _ctx_truncate(r.get("priority", "?"), 20)
                action = _ctx_truncate(r.get("action", "?"), 60)
                detail = _ctx_truncate(r.get("detail", ""), _CONTEXT_REACTION_DETAIL_MAX_CHARS)
                reaction_lines.append(f"[{priority}] {action.upper()}: {detail}")
                for item in _ctx_cap(r.get("items", []), _CONTEXT_REACTIONS_ITEMS_PER_DIRECTIVE, _CONTEXT_REACTION_ITEM_MAX_CHARS):
                    reaction_lines.append(f"  • {item}")
            reaction_lines.append("=== END REACTIONS ===")
    except Exception:
        reaction_lines = []  # Non-critical — reactions are a bonus, not a dependency
    if reaction_lines:
        reaction_lines = _ctx_fit(reaction_lines, _CONTEXT_REACTIONS_MAX_CHARS,
                                  protected_head=1, protected_tail=1)

    # Assemble in presentation order and enforce the total:
    # reactions shed first, then nerve, then recent; the
    # current-state layer is truncated only as a last resort
    # (its layer fit above already bounds it, so this is a
    # belt-and-braces guard, not the normal path).
    sections = [
        ("reactions", reaction_lines),
        ("nerve", nerve_lines),
        ("recent", recent_lines),
        ("current", current_lines),
    ]
    overhead = len(header) + len(footer) + 8  # newlines / spacing
    total = overhead + sum(len("\n".join(lines)) for _, lines in sections if lines)
    for name, lines in sections:
        if total <= _CONTEXT_TOTAL_MAX_CHARS:
            break
        if not lines:
            continue
        if name == "current":
            fitted = _ctx_fit(lines, max(len(_CONTEXT_TRUNCATION_MARKER),
                                         _CONTEXT_TOTAL_MAX_CHARS - (total - len("\n".join(lines)))))
            total += len("\n".join(fitted)) - len("\n".join(lines))
            sections[3] = (name, fitted)
        else:
            note = [f"[{name} layer {_CONTEXT_TRUNCATION_MARKER[4:]}"]
            total += len("\n".join(note)) - len("\n".join(lines))
            sections = [(n, note if n == name else ls) for n, ls in sections]

    out = [header]
    by_name = dict(sections)
    for name in ("current", "recent", "nerve", "reactions"):
        lines = by_name.get(name) or []
        if lines:
            if name in ("nerve", "reactions"):
                out.append("")
            out.extend(lines)
    out.append(footer)
    result = "\n".join(out)
    if len(result) > _CONTEXT_TOTAL_MAX_CHARS:  # final guard, unreachable by construction
        result = _ctx_truncate(result, _CONTEXT_TOTAL_MAX_CHARS)
    return result


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

    # delete (the user's delete right, E-063)
    sp = sub.add_parser("delete", help="Delete logged conversations — totally, with verification")
    sp.add_argument("--session", default="", help="Session ID to delete")
    sp.add_argument("--all", action="store_true", help="Delete ALL logged conversations")
    sp.add_argument("--yes", action="store_true", help="Confirm a --all deletion")

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
    elif args.command == "delete":
        if not args.all and not args.session:
            parser.error("delete needs --session <id> or --all --yes")
        cmd_delete(args)