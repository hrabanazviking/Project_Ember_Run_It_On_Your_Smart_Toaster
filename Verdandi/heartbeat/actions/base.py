"""
Verðandi Action Base — The Interface Every Voice Implements.

Every recovery action inherits from BaseAction and implements execute().
Actions receive an ActionContext with the triggering check results,
config, and history. They return an ActionResult with outcome details.

Safety guards:
  - Rate limiting: each action tracks its last execution time
  - Cooldown: minimum time between identical actions
  - Dry-run: log what would happen without doing it
  - Audit: every action logged to state DB and nerve hub
"""

import time
import logging
from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Optional
from pathlib import Path

from heartbeat.checks.base import CheckResult, CheckSeverity

logger = logging.getLogger("verdandi.heartbeat.actions")


# ─────────────────────────────────────────────────────
# Action Severity — mirrors CheckSeverity but for outcomes
# ─────────────────────────────────────────────────────

class ActionSeverity(Enum):
    """Action outcome severity."""
    SUCCESS = "success"
    PARTIAL = "partial"      # Some targets succeeded, some failed
    FAILED = "failed"
    SKIPPED = "skipped"      # Action not taken (cooldown, dry-run, etc.)
    DRY_RUN = "dry_run"      # Would-have-been action in dry-run mode


# ─────────────────────────────────────────────────────
# Action Context — What triggers an action
# ─────────────────────────────────────────────────────

@dataclass
class ActionContext:
    """Context provided to an action when it's triggered.

    Contains the triggering check results, config, and history
    so the action can make informed decisions.
    """
    trigger_check: str                    # Name of the check that triggered
    trigger_result: CheckResult           # The check result that triggered
    all_results: dict[str, CheckResult]   # All check results from this pulse
    dry_run: bool = False                # If True, don't execute, just report
    config: Optional[Any] = None         # HeartbeatConfig reference

    @property
    def trigger_severity(self) -> CheckSeverity:
        """Convenience: severity of the triggering check."""
        return self.trigger_result.severity

    @property
    def trigger_details(self) -> dict:
        """Convenience: details of the triggering check."""
        return self.trigger_result.details or {}


# ─────────────────────────────────────────────────────
# Action Result — What an action reports back
# ─────────────────────────────────────────────────────

@dataclass
class ActionResult:
    """Result of an action execution."""
    action_name: str
    severity: ActionSeverity
    message: str
    details: dict = field(default_factory=dict)
    timestamp: str = ""
    targets_affected: list[str] = field(default_factory=list)
    targets_failed: list[str] = field(default_factory=list)
    duration_ms: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            from datetime import datetime, timezone
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "action_name": self.action_name,
            "severity": self.severity.value,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp,
            "targets_affected": self.targets_affected,
            "targets_failed": self.targets_failed,
            "duration_ms": self.duration_ms,
        }

    @property
    def is_success(self) -> bool:
        """True if the action fully succeeded."""
        return self.severity == ActionSeverity.SUCCESS

    @property
    def is_partial(self) -> bool:
        """True if the action partially succeeded."""
        return self.severity == ActionSeverity.PARTIAL


# ─────────────────────────────────────────────────────
# Base Action — The Voice Pattern
# ─────────────────────────────────────────────────────

class BaseAction:
    """Base class for all recovery actions.

    Subclasses must implement:
      - name: str — unique action identifier
      - description: str — human-readable description
      - trigger_checks: list[str] — which check names can trigger this action
      - trigger_severity: CheckSeverity — minimum severity to trigger
      - _execute(ctx) -> ActionResult — the actual action logic

    Safety features inherited:
      - Rate limiting via cooldown_seconds
      - Dry-run mode support
      - Duration tracking
      - Audit logging
    """

    name: str = "base"
    description: str = "Base action — override in subclass"
    trigger_checks: list[str] = []       # Which checks can trigger this
    trigger_severity: CheckSeverity = CheckSeverity.WARNING  # Minimum severity
    cooldown_seconds: float = 300.0      # 5 minutes between identical actions

    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self._last_execution: dict[str, float] = {}  # target -> timestamp
        self._last_result: Optional[ActionResult] = None

    def should_trigger(self, ctx: ActionContext) -> bool:
        """Determine if this action should trigger for the given context.

        Checks:
          1. The triggering check is in our trigger_checks list
          2. The triggering severity meets our threshold
          3. We're not in cooldown for this specific target
        """
        # Check name match
        if self.trigger_checks and ctx.trigger_check not in self.trigger_checks:
            return False

        # Severity threshold
        severity_order = [
            CheckSeverity.OK, CheckSeverity.UNKNOWN,
            CheckSeverity.WARNING, CheckSeverity.CRITICAL
        ]
        trigger_idx = severity_order.index(ctx.trigger_severity)
        threshold_idx = severity_order.index(self.trigger_severity)
        if trigger_idx < threshold_idx:
            return False

        # Cooldown check
        cooldown_key = f"{ctx.trigger_check}:{ctx.trigger_result.message[:50]}"
        last_run = self._last_execution.get(cooldown_key, 0)
        if time.time() - last_run < self.cooldown_seconds:
            logger.debug(
                f"Action {self.name} cooling down for {cooldown_key} "
                f"({time.time() - last_run:.0f}s ago, need {self.cooldown_seconds}s)"
            )
            return False

        return True

    def execute(self, ctx: ActionContext) -> ActionResult:
        """Execute the action with safety guards.

        Wraps _execute() with:
          - Dry-run support
          - Duration tracking
          - Cooldown registration
          - Error catching
          - Audit logging
        """
        cooldown_key = f"{ctx.trigger_check}:{ctx.trigger_result.message[:50]}"
        start = time.monotonic()

        try:
            # Dry-run mode
            if ctx.dry_run:
                result = self._dry_run(ctx)
                result.duration_ms = (time.monotonic() - start) * 1000
                self._last_result = result
                logger.info(f"[DRY-RUN] {self.name}: {result.message}")
                return result

            # Execute
            result = self._execute(ctx)
            result.duration_ms = (time.monotonic() - start) * 1000

            # Register cooldown
            self._last_execution[cooldown_key] = time.time()
            self._last_result = result

            # Audit log
            if result.is_success:
                logger.info(f"✅ {self.name}: {result.message}")
            elif result.is_partial:
                logger.warning(f"⚠️ {self.name}: {result.message}")
            else:
                logger.error(f"❌ {self.name}: {result.message}")

            return result

        except Exception as e:
            duration = (time.monotonic() - start) * 1000
            logger.error(f"💥 {self.name} exception: {e}")
            return ActionResult(
                action_name=self.name,
                severity=ActionSeverity.FAILED,
                message=f"Action failed: {e}",
                details={"error": str(e)},
                duration_ms=duration,
            )

    def _execute(self, ctx: ActionContext) -> ActionResult:
        """Override in subclass. The actual action logic."""
        raise NotImplementedError("Subclasses must implement _execute()")

    def _dry_run(self, ctx: ActionContext) -> ActionResult:
        """Override in subclass for dry-run behavior. Default: report what would happen."""
        return ActionResult(
            action_name=self.name,
            severity=ActionSeverity.DRY_RUN,
            message=f"[DRY-RUN] Would execute {self.name}",
            details={"trigger": ctx.trigger_result.message},
        )


# ─────────────────────────────────────────────────────
# Action Registry — Discover Available Actions
# ─────────────────────────────────────────────────────

ACTION_REGISTRY: dict[str, type[BaseAction]] = {}

def register_action(name: str):
    """Decorator to register an action class."""
    def decorator(cls):
        ACTION_REGISTRY[name] = cls
        return cls
    return decorator

# Register built-in actions
# (Imported at bottom of __init__.py to avoid circular imports)