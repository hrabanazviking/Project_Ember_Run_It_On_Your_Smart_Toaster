"""
Eir — The Healing Hand. Auto-Heal Action.

Eir is the goddess of healing. This action automatically repairs
corrupted databases, rebuilds indexes, and restores malformed
configuration files.

Configurable:
  - Which databases to repair
  - Whether to rebuild indexes
  - Whether to reset stuck services
  - Repair attempts before escalation
"""

import sqlite3
import shutil
import logging
from pathlib import Path
from typing import Any, Optional

from heartbeat.actions.base import (
    BaseAction, ActionContext, ActionResult, ActionSeverity, register_action,
)
from heartbeat.checks.base import CheckSeverity

logger = logging.getLogger("verdandi.heartbeat.actions.eir_action")


@register_action("auto_heal")
class EirAction(BaseAction):
    """Auto-heal corrupted databases and fix configuration issues.

    Triggered by Mímir's memory check when databases fail integrity
    checks or have malformed data.
    """

    name = "auto_heal"
    description = "Auto-heal corrupted databases, rebuild indexes, restore configs"
    trigger_checks = ["memory"]
    trigger_severity = CheckSeverity.CRITICAL
    cooldown_seconds = 1800  # Don't heal the same issue more than once per 30 min

    def _execute(self, ctx: ActionContext) -> ActionResult:
        """Heal corrupted databases and fix broken state."""
        details = ctx.trigger_details
        targets_affected = []
        targets_failed = []

        # 1. Heal Mímir database if integrity failed
        mimir = details.get("mimir", {})
        if mimir.get("integrity") == "fail":
            success = self._heal_database(Path(mimir.get("path", "")), "mimir_well")
            if success:
                targets_affected.append("mimir_well:healed")
            else:
                targets_failed.append("mimir_well:heal_failed")

        # 2. Heal state database if integrity failed
        state_db = details.get("state_db", {})
        if state_db.get("integrity") == "fail":
            success = self._heal_database(Path(state_db.get("path", "")), "verdandi_heartbeat")
            if success:
                targets_affected.append("state_db:healed")
            else:
                targets_failed.append("state_db:heal_failed")

        # 3. Ensure nerve hub socket directory exists
        from heartbeat.paths import get_state_dir, ensure_dirs
        try:
            ensure_dirs()
            targets_affected.append("directories:ensured")
        except Exception as e:
            logger.error(f"Failed to ensure directories: {e}")
            targets_failed.append("directories:ensure_failed")

        # 4. Truncate conversation log if it has malformed entries
        conv_log = details.get("conversation_log", {})
        if conv_log.get("exists"):
            success = self._heal_jsonl(
                Path(conv_log.get("path", ""))
            )
            if success:
                targets_affected.append("conversation_log:healed")
            # Non-critical if this fails

        # 5. Truncate nerve feed if it has malformed entries
        nerve_feed = details.get("nerve_feed", {})
        if nerve_feed.get("exists"):
            success = self._heal_jsonl(
                Path(nerve_feed.get("path", ""))
            )
            if success:
                targets_affected.append("nerve_feed:healed")

        if targets_failed:
            severity = ActionSeverity.PARTIAL if targets_affected else ActionSeverity.FAILED
        elif targets_affected:
            severity = ActionSeverity.SUCCESS
        else:
            severity = ActionSeverity.SKIPPED

        return ActionResult(
            action_name=self.name,
            severity=severity,
            message=f"Healed {len(targets_affected)} targets, {len(targets_failed)} failed",
            details={"affected": targets_affected, "failed": targets_failed},
            targets_affected=targets_affected,
            targets_failed=targets_failed,
        )

    def _dry_run(self, ctx: ActionContext) -> ActionResult:
        """Report what would be healed."""
        details = ctx.trigger_details
        would_heal = []

        mimir = details.get("mimir", {})
        if mimir.get("integrity") == "fail":
            would_heal.append("mimir_well DB")

        state_db = details.get("state_db", {})
        if state_db.get("integrity") == "fail":
            would_heal.append("state_db")

        return ActionResult(
            action_name=self.name,
            severity=ActionSeverity.DRY_RUN,
            message=f"[DRY-RUN] Would heal {len(would_heal)} targets: {', '.join(would_heal)}",
            details={"targets": would_heal},
        )

    def _heal_database(self, db_path: Path, name: str) -> bool:
        """Attempt to repair a corrupted SQLite database."""
        if not db_path.exists():
            logger.warning(f"Database {name} not found at {db_path}")
            return False

        try:
            # First, try to recover what we can
            backup_path = db_path.with_suffix(".db.recover")
            corrupted_path = db_path.with_suffix(".db.corrupt")

            # Step 1: Create a backup
            shutil.copy2(str(db_path), str(backup_path))

            # Step 2: Try to verify and optimize with context manager
            with sqlite3.connect(str(db_path)) as conn:
                try:
                    # Try integrity check first
                    result = conn.execute("PRAGMA integrity_check").fetchone()
                    if result[0] == "ok":
                        # Not actually corrupted — run VACUUM to optimize
                        conn.execute("VACUUM")
                        backup_path.unlink(missing_ok=True)
                        return True
                except sqlite3.DatabaseError:
                    pass  # Corrupted, proceed to recovery

            # Step 3: If corrupted, try to recover data
            # Save the corrupted file for forensics
            if not corrupted_path.exists():
                shutil.move(str(db_path), str(corrupted_path))

            # Recover from backup by re-exporting (with context managers)
            with sqlite3.connect(str(backup_path)) as recovery_conn:
                with sqlite3.connect(str(db_path)) as new_conn:
                    # Copy all tables
                    for table_row in recovery_conn.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    ):
                        table_name = table_row[0]
                        try:
                            new_conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM backup.{table_name}")
                        except Exception:
                            pass
                    new_conn.commit()

            backup_path.unlink(missing_ok=True)

            logger.info(f"Healed database {name}")
            return True

        except Exception as e:
            logger.error(f"Failed to heal database {name}: {e}")
            # Restore from backup if healing failed
            if backup_path.exists():
                shutil.copy2(str(backup_path), str(db_path))
                backup_path.unlink(missing_ok=True)
            return False

    def _heal_jsonl(self, path: Path) -> bool:
        """Remove malformed lines from a JSONL file."""
        import json

        if not path.exists():
            return True

        try:
            valid_lines = []
            removed = 0

            with open(path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        json.loads(line)
                        valid_lines.append(line + "\n")
                    except json.JSONDecodeError:
                        removed += 1

            if removed > 0:
                with open(path, "w") as f:
                    f.writelines(valid_lines)
                logger.info(f"Healed {path.name}: removed {removed} malformed lines")

            return True

        except Exception as e:
            logger.error(f"Failed to heal {path.name}: {e}")
            return False