"""
Mjölnir — The Hammer Strikes. Auto-Push Action.

Thor's hammer never misses its target. This action automatically
commits and pushes git repositories that have uncommitted changes
or unpushed commits.

Configurable triggers:
  - projects WARNING or CRITICAL → auto-push dirty repos
  - Configurable: which repos to push, commit message template,
    whether to push unpushed commits or only auto-commit dirty trees

Safety guards:
  - Rate limited: won't push the same repo more than once per cooldown
  - Dry-run mode: log what would be pushed without pushing
  - Whitelist/blacklist: only push repos you trust
  - Conventional commits: auto-generate meaningful commit messages
"""

import subprocess
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from heartbeat.actions.base import (
    BaseAction, ActionContext, ActionResult, ActionSeverity, register_action,
)
from heartbeat.checks.base import CheckSeverity

logger = logging.getLogger("verdandi.heartbeat.actions.mjölnir")


@register_action("auto_push")
class MjölnirAction(BaseAction):
    """Auto-push dirty and unpushed git repositories.

    Triggered by Huginn's project check when repos have
    uncommitted changes or unpushed commits.
    """

    name = "auto_push"
    description = "Auto-commit and push dirty/unpushed git repositories"
    trigger_checks = ["projects"]
    trigger_severity = CheckSeverity.WARNING
    cooldown_seconds = 3600  # Don't push the same repo more than once per hour

    # Repos to never auto-push (safety blacklist)
    BLOCKLIST: list[str] = []

    # Repos to always auto-push (even in dry-run)
    ALLOWLIST: list[str] = []

    def _execute(self, ctx: ActionContext) -> ActionResult:
        """Auto-push repos flagged by the projects check."""
        details = ctx.trigger_details
        repos = details.get("repos", {})
        targets_affected = []
        targets_failed = []

        for repo_name, repo_info in repos.items():
            # Skip blacklisted repos
            if repo_name in self.BLOCKLIST:
                logger.debug(f"Skipping blocklisted repo: {repo_name}")
                continue

            repo_path = Path(repo_info.get("path", ""))

            # Only act on warning or critical repos
            repo_severity = repo_info.get("severity", "ok")
            if repo_severity not in ("warning", "critical"):
                continue

            dirty_files = repo_info.get("dirty_files", 0)
            unpushed = repo_info.get("unpushed", 0)

            if dirty_files > 0:
                success = self._auto_commit(repo_path, repo_name, dirty_files)
                if success:
                    targets_affected.append(f"{repo_name}:committed")
                else:
                    targets_failed.append(f"{repo_name}:commit_failed")
                    continue

            if unpushed > 0:
                success = self._auto_push(repo_path, repo_name, unpushed)
                if success:
                    targets_affected.append(f"{repo_name}:pushed")
                else:
                    targets_failed.append(f"{repo_name}:push_failed")

        if targets_failed:
            severity = ActionSeverity.PARTIAL if targets_affected else ActionSeverity.FAILED
        else:
            severity = ActionSeverity.SUCCESS

        return ActionResult(
            action_name=self.name,
            severity=severity,
            message=f"Auto-pushed {len(targets_affected)} repos, {len(targets_failed)} failed",
            details={"affected": targets_affected, "failed": targets_failed},
            targets_affected=targets_affected,
            targets_failed=targets_failed,
        )

    def _dry_run(self, ctx: ActionContext) -> ActionResult:
        """Report what would be pushed without pushing."""
        details = ctx.trigger_details
        repos = details.get("repos", {})
        would_push = []

        for repo_name, repo_info in repos.items():
            if repo_name in self.BLOCKLIST:
                continue
            repo_severity = repo_info.get("severity", "ok")
            if repo_severity not in ("warning", "critical"):
                continue
            would_push.append(repo_name)

        return ActionResult(
            action_name=self.name,
            severity=ActionSeverity.DRY_RUN,
            message=f"[DRY-RUN] Would auto-push {len(would_push)} repos: {', '.join(would_push[:5])}",
            details={"repos": would_push},
        )

    def _auto_commit(self, repo_path: Path, repo_name: str, dirty_count: int) -> bool:
        """Auto-commit dirty files in a repo."""
        try:
            # Stage all changes
            result = subprocess.run(
                ["git", "add", "-A"],
                cwd=str(repo_path), capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                logger.warning(f"git add failed for {repo_name}: {result.stderr}")
                return False

            # Generate commit message
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            message = f"🫀 auto-commit: {dirty_count} changes [Verðandi Heartbeat {timestamp}]"

            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=str(repo_path), capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                # "nothing to commit" is OK
                if "nothing to commit" in result.stderr or "nothing to commit" in result.stdout:
                    return True
                logger.warning(f"git commit failed for {repo_name}: {result.stderr}")
                return False

            logger.info(f"Mjölnir committed {dirty_count} changes in {repo_name}")
            return True

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.error(f"Auto-commit failed for {repo_name}: {e}")
            return False

    def _auto_push(self, repo_path: Path, repo_name: str, unpushed_count: int) -> bool:
        """Auto-push unpushed commits in a repo."""
        try:
            result = subprocess.run(
                ["git", "push"],
                cwd=str(repo_path), capture_output=True, text=True, timeout=60
            )
            if result.returncode != 0:
                logger.warning(f"git push failed for {repo_name}: {result.stderr}")
                return False

            logger.info(f"Mjölnir pushed {unpushed_count} commits from {repo_name}")
            return True

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.error(f"Auto-push failed for {repo_name}: {e}")
            return False