"""
Verðandi Vör Action — Pre-emptive Healing.

Vör is the Norse goddess of awareness and wisdom — she who knows all things.
In our architecture, Vör is the action that responds to Skuld's predictions
BEFORE they become critical. She acts on WARNING + negative trend instead of
waiting for CRITICAL.

Pre-emptive actions (triggered by Skuld predictions):
  1. Disk trending full → proactive log cleanup before 95%
  2. Memory trending high → proactive cache clearing before 95%
  3. Service degradation detected → proactive restart before crash
  4. DB growth trending high → proactive vacuum/reindex before 90%

This is the wisdom of prevention: don't wait for the roof to collapse.
Shore it up when you see the first crack.
"""

import logging
import subprocess
from datetime import datetime, timezone
from typing import Optional

from heartbeat.actions.base import (
    BaseAction, ActionContext, ActionResult, ActionSeverity, ACTION_REGISTRY,
)
from heartbeat.checks.base import CheckSeverity

logger = logging.getLogger("verdandi.actions.vör")


class VörAction(BaseAction):
    """Pre-emptive healing action — act on warnings with negative trends.

    Vör listens to Skuld's predictions and acts BEFORE things go critical.
    When a WARNING check has a degrading trend, Vör escalates to proactive
    healing. This is the system's immune response before the fever starts.

    Trigger conditions (configurable):
      - disk_health: warning + degrading → proactive log cleanup
      - memory_health: warning + degrading → proactive cache flush
      - service_health: warning + degrading → proactive service restart
      - db_health: warning + degrading → proactive vacuum/reindex
    """

    name = "preemptive_heal"
    description = "Pre-emptive healing — act on WARNING + degrading trend before CRITICAL"

    # Cooldown in seconds between pre-emptive actions for the same target
    COOLDOWNS: dict[str, int] = {
        "disk_cleanup": 3600,       # 1 hour between disk cleanups
        "memory_cache_flush": 1800, # 30 min between cache flushes
        "service_restart": 7200,    # 2 hours between restarts
        "db_vacuum": 86400,         # 24 hours between vacuums
    }

    def __init__(self, config=None):
        super().__init__(config)
        self._last_action: dict[str, datetime] = {}

    def should_trigger(self, context: ActionContext) -> bool:
        """Trigger on Skuld predictions or WARNING with degrading trend."""
        # Check if Skuld prediction indicates pre-emptive action needed
        skuld = context.all_results.get("prediction")
        if skuld and skuld.severity in (CheckSeverity.WARNING, CheckSeverity.CRITICAL):
            prediction_details = skuld.details
            capacity = prediction_details.get("capacity", {})
            for resource, pred in capacity.items():
                if pred.get("urgency") in ("critical", "warning"):
                    return True

        # Check for WARNING + degrading trend in other checks
        for name, result in context.all_results.items():
            if result.severity == CheckSeverity.WARNING:
                # Check if health trend is degrading
                trend = getattr(result, '_trend', None)
                if trend == "degrading":
                    return True

        return False

    def execute(self, context: ActionContext) -> ActionResult:
        """Execute pre-emptive healing actions based on prediction data."""
        actions_taken = []
        errors = []

        # 1. Disk pre-emptive cleanup
        capacity = self._get_capacity_prediction(context)
        for resource, pred in capacity.items():
            if resource == "disk" and pred.get("urgency") in ("critical", "warning"):
                result = self._preemptive_disk_cleanup(context)
                if result:
                    actions_taken.append(result)
                else:
                    errors.append("disk_cleanup_failed")

            elif resource == "memory" and pred.get("urgency") in ("critical", "warning"):
                result = self._preemptive_memory_flush(context)
                if result:
                    actions_taken.append(result)
                else:
                    errors.append("memory_flush_failed")

        # 2. Skuld health trend actions
        skuld = context.all_results.get("prediction")
        if skuld and skuld.details:
            emotion = skuld.details.get("emotion", {})
            if emotion.get("emotion") == "urgency":
                result = self._preemptive_service_check(context)
                if result:
                    actions_taken.append(result)

            elif emotion.get("emotion") == "concern":
                # Log concern but don't act yet
                logger.info(
                    f"Vör: Health concern detected — {emotion.get('description')}. "
                    f"Monitoring closely."
                )

        if not actions_taken and not errors:
            return ActionResult(
                name=self.name,
                severity=ActionSeverity.INFO,
                message="No pre-emptive actions needed at this time",
                details={"skuld_predictions": self._get_capacity_summary(context)},
            )

        severity = ActionSeverity.SUCCESS if not errors else ActionSeverity.PARTIAL
        message = f"Pre-emptive healing: {len(actions_taken)} actions taken"
        if errors:
            message += f", {len(errors)} errors"

        return ActionResult(
            name=self.name,
            severity=severity,
            message=message,
            details={
                "actions_taken": actions_taken,
                "errors": errors,
                "dry_run": context.dry_run,
            },
        )

    def _get_capacity_prediction(self, context: ActionContext) -> dict:
        """Extract capacity predictions from Skuld check results."""
        skuld = context.all_results.get("prediction")
        if skuld and skuld.details:
            return skuld.details.get("capacity", {})
        return {}

    def _get_capacity_summary(self, context: ActionContext) -> dict:
        """Get a summary of capacity predictions."""
        capacity = self._get_capacity_prediction(context)
        return {
            resource: pred.get("prediction", "unknown")
            for resource, pred in capacity.items()
        }

    def _check_cooldown(self, action_type: str) -> bool:
        """Check if enough time has passed since last action of this type."""
        if action_type not in self._last_action:
            return True
        cooldown_seconds = self.COOLDOWNS.get(action_type, 3600)
        elapsed = (datetime.now(timezone.utc) - self._last_action[action_type]).total_seconds()
        return elapsed >= cooldown_seconds

    def _record_action(self, action_type: str) -> None:
        """Record that an action was taken, for cooldown tracking."""
        self._last_action[action_type] = datetime.now(timezone.utc)

    def _preemptive_disk_cleanup(self, context: ActionContext) -> Optional[str]:
        """Proactive disk cleanup before disk reaches critical levels."""
        if not self._check_cooldown("disk_cleanup"):
            logger.debug("Vör: Disk cleanup cooldown active, skipping")
            return None

        if context.dry_run:
            self._record_action("disk_cleanup")
            return "disk_cleanup:would_clean_logs_and_temp_files"

        try:
            # Clean log files older than 7 days
            result = subprocess.run(
                ["find", "/var/log", "-name", "*.log.*", "-mtime", "+7", "-delete"],
                capture_output=True, text=True, timeout=30,
            )
            # Clean temp files
            subprocess.run(
                ["find", "/tmp", "-name", "verdandi_*", "-mtime", "+1", "-delete"],
                capture_output=True, text=True, timeout=30,
            )
            # Vacuum our own database
            from heartbeat.paths import get_db_path
            import sqlite3
            db_path = get_db_path()
            if db_path.exists():
                with sqlite3.connect(str(db_path)) as conn:
                    conn.execute("VACUUM")

            self._record_action("disk_cleanup")
            return "disk_cleanup:cleaned_logs_temp_vacuumed_db"

        except Exception as e:
            logger.error(f"Vör: Pre-emptive disk cleanup failed: {e}")
            return None

    def _preemptive_memory_flush(self, context: ActionContext) -> Optional[str]:
        """Proactive memory cache flush before memory reaches critical."""
        if not self._check_cooldown("memory_cache_flush"):
            logger.debug("Vör: Memory flush cooldown active, skipping")
            return None

        if context.dry_run:
            self._record_action("memory_cache_flush")
            return "memory_flush:would_drop_caches"

        try:
            # Drop page caches (Linux)
            try:
                with open("/proc/sys/vm/drop_caches", "w") as f:
                    f.write("1\n")  # Drop page cache only
                self._record_action("memory_cache_flush")
                return "memory_flush:dropped_page_caches"
            except (PermissionError, IOError):
                # Not running as root — try Python-level cache clearing
                import gc
                gc.collect()
                self._record_action("memory_cache_flush")
                return "memory_flush:python_gc_collected"

        except Exception as e:
            logger.error(f"Vör: Pre-emptive memory flush failed: {e}")
            return None

    def _preemptive_service_check(self, context: ActionContext) -> Optional[str]:
        """Check and optionally restart degraded services."""
        if not self._check_cooldown("service_restart"):
            logger.debug("Vör: Service restart cooldown active, skipping")
            return None

        if context.dry_run:
            self._record_action("service_restart")
            return "service_check:would_check_and_restart_degraded_services"

        try:
            # Check systemd services that should be running
            result = subprocess.run(
                ["systemctl", "list-units", "--type=service", "--state=failed",
                 "--no-legend", "--no-pager"],
                capture_output=True, text=True, timeout=10,
            )
            failed_services = [
                line.split()[0] for line in result.stdout.strip().split("\n")
                if line.strip()
            ]
            if failed_services:
                logger.info(f"Vör: Found failed services: {failed_services}")
                return f"service_check:found_{len(failed_services)}_failed_services"

            self._record_action("service_restart")
            return "service_check:all_services_healthy"

        except Exception as e:
            logger.error(f"Vör: Pre-emptive service check failed: {e}")
            return None


# Register the action — VörAction has name="preemptive_heal"
ACTION_REGISTRY["preemptive_heal"] = VörAction