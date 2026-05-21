"""
Verðandi Check Base — The Interface Every Sense Implements.

Every health check inherits from BaseCheck and implements check().
Results are CheckResult objects with severity, message, and details.
Checks are pluggable: add a new one to CHECK_REGISTRY and it
appears in the pulse automatically.

Design principles:
  - Graceful degradation: if a check fails, it returns UNKNOWN, not an exception
  - No I/O in __init__: all file/socket/network access happens in check()
  - Timeout-safe: checks should complete within config thresholds
  - Pi-friendly: minimize SD card writes, check thermal status first
"""

import time
import logging
from datetime import datetime, timezone
from enum import Enum, auto
from dataclasses import dataclass, field, asdict
from typing import Any, Optional

logger = logging.getLogger("verdandi.checks")


class CheckSeverity(Enum):
    """Severity levels for check results.
    
    Ordered by severity: OK < WARNING < CRITICAL < UNKNOWN
    
    UNKNOWN is used when a check cannot determine status (e.g., file not found,
    permission denied). It does NOT contribute to state machine transitions
    unless it's the only result available.
    """
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"
    
    def __lt__(self, other):
        """Compare severity levels. Higher = worse."""
        order = {CheckSeverity.OK: 0, CheckSeverity.WARNING: 1, 
                 CheckSeverity.CRITICAL: 2, CheckSeverity.UNKNOWN: -1}
        return order[self] < order[other]
    
    def __le__(self, other):
        return self < other or self == other
    
    def __gt__(self, other):
        return not self <= other
    
    def __ge__(self, other):
        return not self < other


@dataclass
class CheckResult:
    """Result of a single health check pulse.
    
    Attributes:
        name: Identifier for the check (e.g., 'health', 'projects', 'memory')
        severity: Overall severity of the check
        message: Human-readable summary
        details: Machine-readable details (metrics, paths, etc.)
        timestamp: ISO 8601 timestamp of when the check was performed
        duration_ms: How long the check took in milliseconds
        sub_results: Individual results from sub-checks (e.g., per-repo, per-DB)
    """
    name: str
    severity: CheckSeverity = CheckSeverity.OK
    message: str = ""
    details: dict = field(default_factory=dict)
    timestamp: str = ""
    duration_ms: float = 0.0
    sub_results: list = field(default_factory=list)
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> dict:
        """Serialize to dict for JSON/nerve impulses."""
        return {
            "name": self.name,
            "severity": self.severity.value if isinstance(self.severity, CheckSeverity) else self.severity,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp,
            "duration_ms": self.duration_ms,
            "sub_results": [
                r.to_dict() if isinstance(r, CheckResult) else r
                for r in self.sub_results
            ],
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CheckResult":
        """Deserialize from dict."""
        severity = data.get("severity", "unknown")
        if isinstance(severity, str):
            severity = CheckSeverity(severity)
        sub_results = [
            cls.from_dict(r) if isinstance(r, dict) else r
            for r in data.get("sub_results", [])
        ]
        return cls(
            name=data["name"],
            severity=severity,
            message=data.get("message", ""),
            details=data.get("details", {}),
            timestamp=data.get("timestamp", ""),
            duration_ms=data.get("duration_ms", 0.0),
            sub_results=sub_results,
        )


class BaseCheck:
    """Base class for all health checks.
    
    Subclasses must implement check() and return a CheckResult.
    The check() method should:
      1. Be idempotent (safe to call multiple times)
      2. Handle all exceptions internally (never raise)
      3. Return UNKNOWN if it cannot determine status
      4. Complete within max_duration_ms
      5. Minimize I/O on Pi (SD card longevity)
    
    Example:
        class MyCheck(BaseCheck):
            def check(self) -> CheckResult:
                try:
                    # ... check something ...
                    return CheckResult(
                        name="my_check",
                        severity=CheckSeverity.OK,
                        message="All good",
                        details={"score": 42},
                    )
                except Exception as e:
                    return CheckResult(
                        name="my_check",
                        severity=CheckSeverity.UNKNOWN,
                        message=f"Check failed: {e}",
                    )
    """
    
    # Subclasses can override these
    name: str = "base"
    description: str = "Base check — override in subclasses"
    
    def __init__(self, config):
        """Initialize check with configuration. No I/O here.
        
        Args:
            config: HeartbeatConfig instance for threshold lookups
        """
        self.config = config
        self._last_result: Optional[CheckResult] = None
    
    @property
    def last_result(self) -> Optional[CheckResult]:
        """Most recent check result, or None if never run."""
        return self._last_result
    
    def check(self) -> CheckResult:
        """Run the health check. Must be overridden by subclasses.
        
        Returns:
            CheckResult with severity, message, and details.
            Never raises — all exceptions are caught and returned as UNKNOWN.
        """
        start = time.monotonic()
        try:
            result = self._perform_check()
            result.duration_ms = (time.monotonic() - start) * 1000
            self._last_result = result
            return result
        except Exception as e:
            logger.error(f"Check {self.name} failed with exception: {e}")
            result = CheckResult(
                name=self.name,
                severity=CheckSeverity.UNKNOWN,
                message=f"Check error: {e}",
                duration_ms=(time.monotonic() - start) * 1000,
            )
            self._last_result = result
            return result
    
    def _perform_check(self) -> CheckResult:
        """Override this in subclasses. May raise exceptions — 
        they'll be caught by check()."""
        raise NotImplementedError("Subclasses must implement _perform_check()")
    
    @staticmethod
    def worst_severity(results: list[CheckResult]) -> CheckSeverity:
        """Return the worst severity from a list of results, ignoring UNKNOWNs
        unless that's all there is."""
        non_unknown = [r for r in results if r.severity != CheckSeverity.UNKNOWN]
        if not non_unknown:
            return CheckSeverity.UNKNOWN if results else CheckSeverity.OK
        return max(r.severity for r in non_unknown)
    
    @staticmethod
    def detail_message(issues: list[tuple[str, str]], all_ok: str = "All checks passing") -> str:
        """Build a human-readable message from a list of (severity, description) issues."""
        if not issues:
            return all_ok
        level_icons = {"critical": "🚨", "warning": "⚠️", "ok": "✅", "unknown": "❓"}
        worst = "critical" if any(l == "critical" for l, _ in issues) else "warning"
        worst_msg = next(m for l, m in issues if l == worst)
        return worst_msg