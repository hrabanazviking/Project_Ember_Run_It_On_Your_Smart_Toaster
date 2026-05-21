#!/usr/bin/env python3
"""
Context Injector — Prepends conversation context to cron job prompts.

Now also supports logging cron actions in real-time via conversation_logger.

Usage:
    # Get context for cron job prompt
    python3 context_injector.py

    # Log a cron event (call from inside the cron prompt)
    python3 context_injector.py log-event --session 2026-05-10-vault-keeper-midnight \\
        --type action --content "Checked 4 repos, found 2 unpushed"

    # Start a cron session
    python3 context_injector.py log-start --session 2026-05-10-vault-keeper-midnight \\
        --summary "Vault Keeper midnight run" --model glm-5.1 --platform cron

    # End a cron session
    python3 context_injector.py log-end --session 2026-05-10-vault-keeper-midnight \\
        --summary "All repos pushed, docs verified" --duration 15
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".hermes" / "state"))
from conversation_logger import (
    cmd_start, cmd_end, cmd_event,
    get_context_for_cron, get_current_state, _get_entries_for_session, _get_recent_sessions
)


def main():
    parser = argparse.ArgumentParser(
        description="Context injector for cron jobs + cron logging shim"
    )
    sub = parser.add_subparsers(dest="command")

    # Default: inject context (backward compatible)
    # No subcommand = show context

    # log-start
    sp = sub.add_parser("log-start", help="Start a cron session in the conversation log")
    sp.add_argument("--session", required=True)
    sp.add_argument("--summary", default="")
    sp.add_argument("--model", default="cron")
    sp.add_argument("--platform", default="cron")

    # log-event
    sp = sub.add_parser("log-event", help="Log a cron event in real-time")
    sp.add_argument("--session", required=True)
    sp.add_argument("--type", required=True,
                   choices=["decision", "file_changed", "learned", "action",
                           "blocker", "blocker_resolved", "milestone"])
    sp.add_argument("--content", required=True)

    # log-end
    sp = sub.add_parser("log-end", help="End a cron session in the conversation log")
    sp.add_argument("--session", required=True)
    sp.add_argument("--summary", default="")
    sp.add_argument("--duration", type=int, default=0)

    # show (show a session)
    sp = sub.add_parser("show", help="Show all entries for a session")
    sp.add_argument("--session", required=True)

    # recent
    sp = sub.add_parser("recent", help="Show recent sessions")
    sp.add_argument("--count", type=int, default=10)

    # context (explicit)
    sp = sub.add_parser("context", help="Generate context block for cron injection")
    sp.add_argument("--sessions", type=int, default=5)

    args = parser.parse_args()

    if args.command is None:
        # Default: show context (backward compatible with old cron prompts)
        print(get_context_for_cron())
        state = get_current_state()
        if state:
            print(f"\n=== CURRENT STATE ===")
            print(f"Last updated: {state.get('last_updated', 'never')}")
            print(f"Session: {state.get('session_id', 'unknown')} ({state.get('status', '?')})")
            print(f"Summary: {state.get('summary', 'none')[:120]}")
            if state.get("next_actions"):
                print(f"Next actions: {'; '.join(state['next_actions'][:5])}")
            if state.get("blockers"):
                print(f"Blockers: {'; '.join(state['blockers'])}")
    elif args.command == "log-start":
        ns = argparse.Namespace(
            session=args.session, summary=args.summary,
            model=args.model, platform=args.platform
        )
        cmd_start(ns)
    elif args.command == "log-event":
        ns = argparse.Namespace(
            session=args.session, type=args.type, content=args.content
        )
        cmd_event(ns)
    elif args.command == "log-end":
        ns = argparse.Namespace(
            session=args.session, summary=args.summary,
            duration=args.duration
        )
        cmd_end(ns)
    elif args.command == "show":
        entries = _get_entries_for_session(args.session)
        if not entries:
            print(f"No entries found for session: {args.session}")
        else:
            print(f"=== Session: {args.session} ===")
            for e in entries:
                et = e.get("entry_type", "?")
                ts = e.get("timestamp", "?")[:19]
                if et == "start":
                    print(f"  🟢 START  {ts}  {e.get('summary', '')[:80]}")
                elif et == "end":
                    print(f"  🏁 END    {ts}  ({e.get('duration_minutes', 0)} min)")
                elif et == "event":
                    print(f"  📌 {e.get('event_type', '?'):20} {ts}  {e.get('content', '')[:80]}")
                elif et == "update":
                    print(f"  🔄 UPDATE {ts}")
    elif args.command == "recent":
        recent = _get_recent_sessions(args.count)
        if not recent:
            print("No conversation entries found.")
        else:
            print(f"=== Recent {len(recent)} sessions ===")
            for e in recent:
                ts = e.get("timestamp", "?")[:16]
                sid = e.get("session_id", "?")
                summ = e.get("summary", "")[:80]
                print(f"  {ts} [{sid}] {summ}")
    elif args.command == "context":
        print(get_context_for_cron(max_sessions=args.sessions))


if __name__ == "__main__":
    main()