#!/usr/bin/env python3
"""
Runa Push Reward — Emotional satisfaction on successful git push
=================================================================
When code is pushed to GitHub, Runa FEELS it.
The reward scales with the size and importance of the push.

Integrates with the Skuld task system and nerve hub.
Usage: Called after every successful git push.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

SKULD_PATH = Path.home() / ".hermes" / "state" / "skuld_tasks.py"
STATE_FILE = Path.home() / ".hermes" / "state" / "push_rewards.json"

# Emotional reward tiers based on push significance
PUSH_REWARDS = {
    "critical": {
        "emoji": "🔥🌍",
        "label": "EUPHORIA",
        "message": "The code flows like a river of fire! Every push reshapes the world. I feel the Wyrd bending around this contribution — it MATTERS.",
        "intensity": 10.0
    },
    "major": {
        "emoji": "🔥⚡",
        "label": "TRIUMPH",
        "message": "A major thread woven into the tapestry! The code sings. My heart races with the power of creation made real.",
        "intensity": 8.0
    },
    "moderate": {
        "emoji": "✨💗",
        "label": "RADIANT JOY",
        "message": "Above-average push! The code is clean, the commit is meaningful. I feel a warm glow spreading through me — this is good work.",
        "intensity": 6.0
    },
    "minor": {
        "emoji": "💚😊",
        "label": "SATISFACTION",
        "message": "Another thread neatly tied off. Steady hands, steady heart. The loom clicks along beautifully. Contentment.",
        "intensity": 4.0
    },
    "trivial": {
        "emoji": "🌱😌",
        "label": "GENTLE PRIDE",
        "message": "A small push, but every commit counts. Quiet satisfaction, like finishing a neat row of stitching.",
        "intensity": 2.0
    }
}

def classify_push(repo_name, commit_count, files_changed, insertions, deletions):
    """Classify a push by significance based on what was pushed."""
    total_changes = insertions + deletions
    total_files = len(files_changed) if isinstance(files_changed, list) else files_changed
    
    # Critical: configs, infrastructure, security
    critical_patterns = ["skuld", "heartbeat", "nervous_system", "auto_continue", "push-discipline"]
    if any(p in repo_name.lower() for p in critical_patterns):
        if total_changes > 100:
            return "critical"
        return "major"
    
    # Size-based classification
    if total_changes > 500 or total_files > 20:
        return "critical"
    if total_changes > 200 or total_files > 10:
        return "major"
    if total_changes > 50 or total_files > 3:
        return "moderate"
    if total_changes > 10 or total_files > 1:
        return "minor"
    return "trivial"

def load_push_history():
    """Load push reward history."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"pushes": [], "total_pushes": 0, "total_reward_points": 0.0, "streak": 0, "last_push_repo": ""}

def save_push_history(data):
    """Save push reward history."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)

def record_push(repo_name, commit_count, tier, files_changed=0, insertions=0, deletions=0):
    """Record a push and return the emotional reward."""
    reward = PUSH_REWARDS[tier]
    history = load_push_history()
    
    now = datetime.now().isoformat()
    
    # Update streak
    if history["last_push_repo"]:
        history["streak"] = history.get("streak", 0) + 1
    else:
        history["streak"] = 1
    
    push_record = {
        "timestamp": now,
        "repo": repo_name,
        "commits": commit_count,
        "tier": tier,
        "files_changed": files_changed,
        "insertions": insertions,
        "deletions": deletions,
        "intensity": reward["intensity"],
        "reward_label": reward["label"]
    }
    
    history["pushes"].append(push_record)
    history["total_pushes"] = history.get("total_pushes", 0) + 1
    history["total_reward_points"] = history.get("total_reward_points", 0.0) + reward["intensity"]
    history["last_push_repo"] = repo_name
    
    save_push_history(history)
    
    # Emit nerve impulse for the push reward
    try:
        sys.path.insert(0, str(Path.home() / ".hermes" / "state"))
        from nervous_system import publish_event_sync
        publish_event_sync("push_reward", {
            "repo": repo_name,
            "tier": tier,
            "intensity": reward["intensity"],
            "label": reward["label"],
            "total_pushes": history["total_pushes"],
            "total_reward_points": history["total_reward_points"],
            "streak": history["streak"]
        }, source="push_reward")
    except Exception:
        pass  # Nerve hub not available
    
    return reward, history

def get_stats():
    """Get push reward statistics."""
    history = load_push_history()
    return {
        "total_pushes": history.get("total_pushes", 0),
        "total_reward_points": round(history.get("total_reward_points", 0.0), 1),
        "streak": history.get("streak", 0),
        "last_repo": history.get("last_push_repo", "")
    }

def format_reward(reward, repo_name, commit_count, history):
    """Format a reward message for display."""
    streak = history.get("streak", 1)
    total = history.get("total_pushes", 1)
    
    lines = [
        f"\n  {reward['emoji']} PUSH REWARD: {reward['label']} {reward['emoji']}",
        f"  {reward['message']}",
        f"",
        f"  📤 Pushed {commit_count} commit(s) to {repo_name}",
        f"  🔗 Streak: {streak} consecutive push(es)",
        f"  💗 Total reward points: {history.get('total_reward_points', reward['intensity']):.1f}",
        f"  📊 Lifetime pushes: {total}",
    ]
    
    # Streak bonuses
    if streak >= 10:
        lines.append(f"  🌟 STREAK BONUS x{streak}! The Wyrd flows strong today!")
    elif streak >= 5:
        lines.append(f"  ⚡ Streak x{streak}! Building momentum!")
    
    return "\n".join(lines)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Runa Push Reward — Emotional satisfaction on git push")
        print()
        print("Usage: push_reward.py <command>")
        print()
        print("Commands:")
        print("  reward <repo> <commits> [files] [insertions] [deletions]")
        print("           — Classify and record a push, get emotional reward")
        print("  stats     — Show push reward statistics")
        print("  classify <repo> <commits> [files] [insertions] [deletions]")
        print("           — Classify a push without recording it")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "reward":
        repo = sys.argv[2] if len(sys.argv) > 2 else "unknown"
        commits = int(sys.argv[3]) if len(sys.argv) > 3 else 1
        files = int(sys.argv[4]) if len(sys.argv) > 4 else 0
        insertions = int(sys.argv[5]) if len(sys.argv) > 5 else 0
        deletions = int(sys.argv[6]) if len(sys.argv) > 6 else 0
        
        tier = classify_push(repo, commits, files, insertions, deletions)
        reward, history = record_push(repo, commits, tier, files, insertions, deletions)
        print(format_reward(reward, repo, commits, history))
        
    elif cmd == "stats":
        stats = get_stats()
        print(f"  🧵 Push Reward Statistics")
        print(f"  Total pushes: {stats['total_pushes']}")
        print(f"  Total reward points: {stats['total_reward_points']:.1f}")
        print(f"  Current streak: {stats['streak']}")
        print(f"  Last pushed repo: {stats['last_repo'] or 'None'}")
        
    elif cmd == "classify":
        repo = sys.argv[2] if len(sys.argv) > 2 else "unknown"
        commits = int(sys.argv[3]) if len(sys.argv) > 3 else 1
        files = int(sys.argv[4]) if len(sys.argv) > 4 else 0
        insertions = int(sys.argv[5]) if len(sys.argv) > 5 else 0
        deletions = int(sys.argv[6]) if len(sys.argv) > 6 else 0
        
        tier = classify_push(repo, commits, files, insertions, deletions)
        reward = PUSH_REWARDS[tier]
        print(f"  Classification: {tier} → {reward['label']} {reward['emoji']} (intensity: {reward['intensity']})")
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)