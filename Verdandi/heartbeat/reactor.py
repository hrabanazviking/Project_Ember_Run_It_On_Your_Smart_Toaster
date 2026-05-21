"""
Verðandi Reactor — The Bridge Between Senses and Actions.

The reactor evaluates check results and decides which actions to trigger.
It's the pattern-recognition engine of the heartbeat: not every warning
needs Mjölnir to strike, and not every error needs Eir's healing.

Reactor rules (configurable via heartbeat.yaml):
  1. Only trigger actions for checks at or above the action's trigger_severity
  2. Respect cooldown periods — don't hammer the same action
  3. Log every action attempt (success, failure, or dry-run)
  4. In dry-run mode, report what WOULD happen without doing it
  5. Actions are ordered by priority; a CRITICAL check triggers more actions

The reactor is called by the pulse cycle after checks are complete.
It can also be invoked manually via CLI for one-off actions.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from heartbeat.checks.base import CheckResult, CheckSeverity
from heartbeat.actions.base import (
    BaseAction, ActionContext, ActionResult, ActionSeverity, ACTION_REGISTRY,
)

logger = logging.getLogger("verdandi.heartbeat.reactor")


# ─────────────────────────────────────────────────────
# Severity → Action priority mapping
# ─────────────────────────────────────────────────────

# Higher severity = more aggressive response
SEVERITY_RESPONSE_LEVELS = {
    CheckSeverity.OK: 0,        # No action needed
    CheckSeverity.UNKNOWN: 1,   # Log and monitor
    CheckSeverity.WARNING: 2,   # Trigger mild actions (cleanup, notify)
    CheckSeverity.CRITICAL: 3,  # Trigger aggressive actions (restart, heal)
}

# ─────────────────────────────────────────────────────
# Reaction Rule — When and how to act
# ─────────────────────────────────────────────────────

class ReactionRule:
    """A rule defining when a check result triggers an action.

    Rules are matched by:
      - check_name: which check triggers this rule
      - min_severity: minimum severity to trigger
      - action_name: which action to invoke
      - conditions: optional dict of additional conditions on check details
    """

    def __init__(
        self,
        check_name: str,
        action_name: str,
        min_severity: CheckSeverity = CheckSeverity.WARNING,
        conditions: Optional[dict] = None,
        enabled: bool = True,
    ):
        self.check_name = check_name
        self.action_name = action_name
        self.min_severity = min_severity
        self.conditions = conditions or {}
        self.enabled = enabled

    def matches(self, result: CheckResult) -> bool:
        """Check if this rule matches the given check result."""
        if not self.enabled:
            return False

        # Check name match
        if self.check_name != result.name and self.check_name != "*":
            return False

        # Severity threshold
        result_level = SEVERITY_RESPONSE_LEVELS.get(result.severity, 0)
        threshold_level = SEVERITY_RESPONSE_LEVELS.get(self.min_severity, 0)
        if result_level < threshold_level:
            return False

        # Additional conditions on details
        for key, expected in self.conditions.items():
            actual = result.details.get(key) if result.details else None
            if isinstance(expected, list):
                if actual not in expected:
                    return False
            elif actual != expected:
                return False

        return True

    def __repr__(self) -> str:
        return f"ReactionRule({self.check_name} → {self.action_name}, min={self.min_severity.value})"


# ─────────────────────────────────────────────────────
# Reactor — The Bridge
# ─────────────────────────────────────────────────────

class Reactor:
    """Evaluates check results and triggers appropriate actions.

    The reactor is the central nervous system of the heartbeat's
    response mechanism. It:
      1. Receives all check results from a pulse
      2. Evaluates them against configured rules
      3. Creates ActionContexts for matching rules
      4. Executes actions (or dry-runs) and collects results
      5. Logs all action outcomes for audit
    """

    def __init__(self, config: Optional[Any] = None, dry_run: bool = False):
        self.config = config
        self.dry_run = dry_run
        self.rules: list[ReactionRule] = []
        self.actions: dict[str, BaseAction] = {}
        self.action_history: list[dict] = []

        # Initialize default rules
        self._init_default_rules()
        self._init_actions()

    def _init_default_rules(self) -> None:
        """Set up default reaction rules."""
        self.rules = [
            # Projects check → auto-push
            ReactionRule(
                check_name="projects",
                action_name="auto_push",
                min_severity=CheckSeverity.WARNING,
            ),
            # Schedule check → auto-restart
            ReactionRule(
                check_name="schedule",
                action_name="auto_restart",
                min_severity=CheckSeverity.WARNING,
            ),
            # Memory check → auto-cleanup on warning
            ReactionRule(
                check_name="memory",
                action_name="auto_cleanup",
                min_severity=CheckSeverity.WARNING,
            ),
            # Health check → auto-cleanup on critical (disk full)
            ReactionRule(
                check_name="health",
                action_name="auto_cleanup",
                min_severity=CheckSeverity.CRITICAL,
                conditions={"disk_used_percent": True},  # Any critical disk usage
            ),
            # Memory check → auto-heal on critical (DB corruption)
            ReactionRule(
                check_name="memory",
                action_name="auto_heal",
                min_severity=CheckSeverity.CRITICAL,
            ),
            # v0.3.0: Skuld prediction → pre-emptive healing
            ReactionRule(
                check_name="prediction",
                action_name="preemptive_heal",
                min_severity=CheckSeverity.WARNING,
            ),
        ]

        # Load custom rules from config
        if self.config:
            custom_rules = self.config.get("reactor.rules", [])
            for rule_config in custom_rules:
                try:
                    rule = ReactionRule(
                        check_name=rule_config.get("check", "*"),
                        action_name=rule_config.get("action", ""),
                        min_severity=CheckSeverity(rule_config.get("min_severity", "warning")),
                        conditions=rule_config.get("conditions", {}),
                        enabled=rule_config.get("enabled", True),
                    )
                    self.rules.append(rule)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Skipping invalid reaction rule: {e}")

    def _init_actions(self) -> None:
        """Initialize action instances from registry."""
        for name, action_class in ACTION_REGISTRY.items():
            try:
                self.actions[name] = action_class(self.config)
            except Exception as e:
                logger.error(f"Failed to initialize action {name}: {e}")

    def react(self, results: dict[str, CheckResult]) -> list[ActionResult]:
        """Evaluate all check results and trigger matching actions.

        This is the main entry point called by the pulse cycle.
        Returns a list of all action results (including dry-runs).
        """
        action_results = []

        for check_name, result in results.items():
            if result.severity == CheckSeverity.OK:
                continue  # No action needed for healthy checks

            # Find matching rules
            for rule in self.rules:
                if not rule.matches(result):
                    continue

                # Get the action
                action = self.actions.get(rule.action_name)
                if not action:
                    logger.warning(f"Action {rule.action_name} not found in registry")
                    continue

                # Check if action should trigger (cooldown, etc.)
                ctx = ActionContext(
                    trigger_check=check_name,
                    trigger_result=result,
                    all_results=results,
                    dry_run=self.dry_run,
                    config=self.config,
                )

                if not action.should_trigger(ctx):
                    logger.debug(f"Action {action.name} not triggered (cooldown or conditions not met)")
                    continue

                # Execute the action
                action_result = action.execute(ctx)
                action_results.append(action_result)

                # Record in history
                self.action_history.append({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "check": check_name,
                    "action": action.name,
                    "severity": action_result.severity.value,
                    "message": action_result.message,
                })

                logger.info(
                    f"Reactor: {check_name} ({result.severity.value}) → "
                    f"{action.name} → {action_result.severity.value}: {action_result.message}"
                )

        return action_results

    def get_status(self) -> dict:
        """Get reactor status for diagnostics."""
        return {
            "rules_count": len(self.rules),
            "rules": [str(r) for r in self.rules],
            "actions_registered": list(self.actions.keys()),
            "action_history_count": len(self.action_history),
            "dry_run": self.dry_run,
        }

    def add_rule(self, rule: ReactionRule) -> None:
        """Add a custom reaction rule."""
        self.rules.append(rule)
        logger.info(f"Added reaction rule: {rule}")

    def remove_rule(self, check_name: str, action_name: str) -> None:
        """Remove reaction rules matching the given check and action."""
        self.rules = [
            r for r in self.rules
            if not (r.check_name == check_name and r.action_name == action_name)
        ]
        logger.info(f"Removed reaction rules: {check_name} → {action_name}")