"""
Gungnir — The Spear That Always Finds Its Target. Auto-Restart Action.

Odin's spear Gungnir never misses. This action automatically restarts
crashed or failed systemd services and processes.

Configurable:
  - Which services to manage
  - Max restart attempts before escalation
  - Restart cooldown periods
  - Escalation to nerve hub on repeated failures
"""

import subprocess
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from heartbeat.actions.base import (
    BaseAction, ActionContext, ActionResult, ActionSeverity, register_action,
)
from heartbeat.checks.base import CheckSeverity

logger = logging.getLogger("verdandi.heartbeat.actions.gungnir")


@register_action("auto_restart")
class GungnirAction(BaseAction):
    """Auto-restart crashed Verdandi services.

    Triggered by Urðr's schedule check when systemd services
    are found inactive or processes are stuck.
    """

    name = "auto_restart"
    description = "Auto-restart crashed systemd services and stuck processes"
    trigger_checks = ["schedule"]
    trigger_severity = CheckSeverity.WARNING
    cooldown_seconds = 600  # Don't restart the same service more than once per 10 min

    # Services we're allowed to restart
    MANAGED_SERVICES = [
        "runa-nervous-system",
        "verdandi-heartbeat",
    ]

    # Maximum restart attempts per service before escalating
    MAX_RESTART_ATTEMPTS = 3

    def __init__(self, config: Optional[Any] = None):
        super().__init__(config)
        self._restart_counts: dict[str, int] = {}

    def _execute(self, ctx: ActionContext) -> ActionResult:
        """Restart inactive services found by the schedule check."""
        details = ctx.trigger_details
        targets_affected = []
        targets_failed = []

        # Check systemd services
        systemd = details.get("systemd", {})
        services = systemd.get("services", [])

        for svc in services:
            svc_name = svc.get("name", "")
            is_active = svc.get("active", False)

            if not svc_name or is_active:
                continue

            # Only restart services we manage
            managed = any(m in svc_name for m in self.MANAGED_SERVICES)
            if not managed:
                logger.debug(f"Skipping unmanaged service: {svc_name}")
                continue

            # Check restart count
            restart_count = self._restart_counts.get(svc_name, 0)
            if restart_count >= self.MAX_RESTART_ATTEMPTS:
                logger.warning(
                    f"Service {svc_name} has exceeded max restart attempts "
                    f"({restart_count}/{self.MAX_RESTART_ATTEMPTS}). Escalating."
                )
                targets_failed.append(f"{svc_name}:max_restarts")
                continue

            # Attempt restart
            success = self._restart_service(svc_name)
            if success:
                self._restart_counts[svc_name] = restart_count + 1
                targets_affected.append(f"{svc_name}:restarted")
            else:
                targets_failed.append(f"{svc_name}:restart_failed")

        if targets_failed:
            severity = ActionSeverity.PARTIAL if targets_affected else ActionSeverity.FAILED
        elif targets_affected:
            severity = ActionSeverity.SUCCESS
        else:
            severity = ActionSeverity.SKIPPED

        return ActionResult(
            action_name=self.name,
            severity=severity,
            message=f"Restarted {len(targets_affected)} services, {len(targets_failed)} failed",
            details={
                "affected": targets_affected,
                "failed": targets_failed,
                "restart_counts": self._restart_counts,
            },
            targets_affected=targets_affected,
            targets_failed=targets_failed,
        )

    def _dry_run(self, ctx: ActionContext) -> ActionResult:
        """Report what would be restarted."""
        details = ctx.trigger_details
        systemd = details.get("systemd", {})
        services = systemd.get("services", [])
        would_restart = [
            svc.get("name", "") for svc in services
            if not svc.get("active", False) and any(m in svc.get("name", "") for m in self.MANAGED_SERVICES)
        ]

        return ActionResult(
            action_name=self.name,
            severity=ActionSeverity.DRY_RUN,
            message=f"[DRY-RUN] Would restart {len(would_restart)} services: {', '.join(would_restart)}",
            details={"services": would_restart},
        )

    def _restart_service(self, service_name: str) -> bool:
        """Restart a systemd user service."""
        try:
            # Use systemctl --user to restart
            result = subprocess.run(
                ["systemctl", "--user", "restart", service_name],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                logger.warning(f"systemctl restart {service_name} failed: {result.stderr}")
                return False

            logger.info(f"Gungnir restarted {service_name}")

            # Verify the service came back up
            result = subprocess.run(
                ["systemctl", "--user", "is-active", service_name],
                capture_output=True, text=True, timeout=10
            )
            return result.stdout.strip() == "active"

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.error(f"Service restart failed for {service_name}: {e}")
            return False