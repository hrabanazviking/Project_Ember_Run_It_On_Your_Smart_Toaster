"""
Bifrǫst — The Burning Bridge. Auto-Cleanup Action.

The rainbow bridge Bifrǫst burns hot enough to cleanse. This action
automatically prunes old logs, temp files, stale data, and oversized
databases that accumulate over time.

Configurable:
  - Which paths to prune
  - Age thresholds for different file types
  - Size limits that trigger cleanup
  - Whether to vacuum SQLite databases
"""

import os
import shutil
import subprocess
import logging
from pathlib import Path
from typing import Any, Optional

from heartbeat.actions.base import (
    BaseAction, ActionContext, ActionResult, ActionSeverity, register_action,
)
from heartbeat.checks.base import CheckSeverity

logger = logging.getLogger("verdandi.heartbeat.actions.bifrǫst")


@register_action("auto_cleanup")
class BifrǫstAction(BaseAction):
    """Auto-cleanup old logs, temp files, and oversized data.

    Triggered by Mímir's memory check when databases or logs
    exceed size thresholds, or by Eir's health check when disk
    usage is high.
    """

    name = "auto_cleanup"
    description = "Auto-cleanup old logs, temp files, and vacuum databases"
    trigger_checks = ["memory", "health"]
    trigger_severity = CheckSeverity.WARNING
    cooldown_seconds = 7200  # Don't cleanup more than once every 2 hours

    # Default cleanup targets
    DEFAULT_TARGETS = {
        "conversation_log_max_mb": 50,
        "nerve_feed_max_mb": 20,
        "state_db_max_mb": 10,
        "pulse_history_max_rows": 1000,
        "log_files_max_mb": 50,
        "vacuum_dbs": True,
    }

    def _execute(self, ctx: ActionContext) -> ActionResult:
        """Clean up oversized files and databases."""
        targets_affected = []
        targets_failed = []
        bytes_freed = 0

        # Get state directory
        from heartbeat.paths import get_state_dir, get_log_dir
        state_dir = get_state_dir()
        log_dir = get_log_dir()

        # Merge config defaults with user config
        targets = dict(self.DEFAULT_TARGETS)
        if self.config:
            config_targets = self.config.get("actions.auto_cleanup.targets", {})
            targets.update(config_targets)

        # 1. Prune conversation log
        freed, ok = self._prune_jsonl(
            state_dir / "conversation_log.jsonl",
            max_mb=targets["conversation_log_max_mb"],
        )
        if freed > 0:
            bytes_freed += freed
            targets_affected.append("conversation_log:pruned")
        elif not ok:
            targets_failed.append("conversation_log:prune_failed")

        # 2. Prune nerve feed
        freed, ok = self._prune_jsonl(
            state_dir / "nerve_feed.jsonl",
            max_mb=targets["nerve_feed_max_mb"],
        )
        if freed > 0:
            bytes_freed += freed
            targets_affected.append("nerve_feed:pruned")
        elif not ok:
            targets_failed.append("nerve_feed:prune_failed")

        # 3. Vacuum databases
        if targets["vacuum_dbs"]:
            db_freed, ok = self._vacuum_databases(state_dir)
            if db_freed > 0:
                bytes_freed += db_freed
                targets_affected.append("dbs:vacuumed")
            elif not ok:
                targets_failed.append("dbs:vacuum_failed")

        # 4. Prune pulse history
        pruned, ok = self._prune_pulse_history(
            state_dir / "verdandi_heartbeat.db",
            max_rows=targets["pulse_history_max_rows"],
        )
        if pruned > 0:
            targets_affected.append(f"pulse_history:pruned_{pruned}_rows")
        elif not ok:
            targets_failed.append("pulse_history:prune_failed")

        # 5. Rotate log files
        freed, ok = self._rotate_logs(log_dir, max_mb=targets["log_files_max_mb"])
        if freed > 0:
            bytes_freed += freed
            targets_affected.append("logs:rotated")
        elif not ok:
            targets_failed.append("logs:rotate_failed")

        mb_freed = bytes_freed / (1024 * 1024)

        if targets_failed:
            severity = ActionSeverity.PARTIAL if targets_affected else ActionSeverity.FAILED
        elif targets_affected:
            severity = ActionSeverity.SUCCESS
        else:
            severity = ActionSeverity.SKIPPED

        return ActionResult(
            action_name=self.name,
            severity=severity,
            message=f"Cleaned up {len(targets_affected)} targets, freed {mb_freed:.1f}MB",
            details={
                "bytes_freed": bytes_freed,
                "mb_freed": round(mb_freed, 2),
                "affected": targets_affected,
                "failed": targets_failed,
            },
            targets_affected=targets_affected,
            targets_failed=targets_failed,
        )

    def _dry_run(self, ctx: ActionContext) -> ActionResult:
        """Report what would be cleaned up."""
        from heartbeat.paths import get_state_dir
        state_dir = get_state_dir()
        would_clean = []

        conv_log = state_dir / "conversation_log.jsonl"
        if conv_log.exists():
            size_mb = conv_log.stat().st_size / (1024 * 1024)
            if size_mb > self.DEFAULT_TARGETS["conversation_log_max_mb"]:
                would_clean.append(f"conversation_log ({size_mb:.1f}MB)")

        nerve_feed = state_dir / "nerve_feed.jsonl"
        if nerve_feed.exists():
            size_mb = nerve_feed.stat().st_size / (1024 * 1024)
            if size_mb > self.DEFAULT_TARGETS["nerve_feed_max_mb"]:
                would_clean.append(f"nerve_feed ({size_mb:.1f}MB)")

        return ActionResult(
            action_name=self.name,
            severity=ActionSeverity.DRY_RUN,
            message=f"[DRY-RUN] Would clean {len(would_clean)} targets: {', '.join(would_clean)}",
            details={"targets": would_clean},
        )

    def _prune_jsonl(self, path: Path, max_mb: float) -> tuple[int, bool]:
        """Prune a JSONL file to stay under max_mb. Returns (bytes_freed, success)."""
        if not path.exists():
            return 0, True

        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb <= max_mb:
            return 0, True

        try:
            # Read all lines
            with open(path, "r") as f:
                lines = f.readlines()

            # Keep only the last max_mb worth of lines (estimate)
            # Each line is roughly the same size, so keep proportionally
            keep_ratio = max_mb / size_mb
            keep_count = max(100, int(len(lines) * keep_ratio))  # Keep at least 100 lines
            kept_lines = lines[-keep_count:]

            # Write back
            with open(path, "w") as f:
                f.writelines(kept_lines)

            freed = len(lines) - keep_count  # Approximate bytes freed per line
            avg_line_size = path.stat().st_size / keep_count if keep_count > 0 else 100
            bytes_freed = int(avg_line_size * (len(lines) - keep_count))

            logger.info(f"Pruned {path.name}: {len(lines)} → {keep_count} lines")
            return bytes_freed, True

        except Exception as e:
            logger.error(f"Failed to prune {path}: {e}")
            return 0, False

    def _vacuum_databases(self, state_dir: Path) -> tuple[int, bool]:
        """Vacuum SQLite databases to reclaim space."""
        import sqlite3

        total_freed = 0
        db_files = list(state_dir.glob("*.db"))

        for db_path in db_files:
            try:
                old_size = db_path.stat().st_size

                conn = sqlite3.connect(str(db_path))
                conn.execute("PRAGMA incremental_vacuum")
                conn.execute("VACUUM")
                conn.commit()
                conn.close()

                new_size = db_path.stat().st_size
                freed = old_size - new_size
                if freed > 0:
                    total_freed += freed
                    logger.info(f"Vacuumed {db_path.name}: freed {freed / 1024:.1f}KB")

            except Exception as e:
                logger.warning(f"Failed to vacuum {db_path}: {e}")

        return total_freed, True

    def _prune_pulse_history(self, db_path: Path, max_rows: int) -> tuple[int, bool]:
        """Prune old rows from pulse history table."""
        if not db_path.exists():
            return 0, True

        import sqlite3

        try:
            conn = sqlite3.connect(str(db_path))
            count = conn.execute("SELECT COUNT(*) FROM pulse_history").fetchone()[0]

            if count <= max_rows:
                conn.close()
                return 0, True

            pruned = count - max_rows
            conn.execute(
                "DELETE FROM pulse_history WHERE id < "
                "(SELECT id FROM pulse_history ORDER BY id DESC LIMIT 1 OFFSET ?)",
                (max_rows,)
            )
            conn.commit()
            conn.close()

            logger.info(f"Pruned {pruned} old pulse history rows")
            return pruned, True

        except Exception as e:
            logger.warning(f"Failed to prune pulse history: {e}")
            return 0, False

    def _rotate_logs(self, log_dir: Path, max_mb: float) -> tuple[int, bool]:
        """Remove old rotated log files."""
        if not log_dir.exists():
            return 0, True

        total_freed = 0
        try:
            for log_file in log_dir.glob("*.log.*"):
                try:
                    size = log_file.stat().st_size
                    log_file.unlink()
                    total_freed += size
                except Exception:
                    pass

            # Check current log size
            current_log = log_dir / "verdandi_heartbeat.log"
            if current_log.exists():
                size_mb = current_log.stat().st_size / (1024 * 1024)
                # Truncate if too large but keep last section
                if size_mb > max_mb:
                    # Let Python's RotatingFileHandler handle this
                    pass

        except Exception as e:
            logger.warning(f"Failed to rotate logs: {e}")

        return total_freed, True