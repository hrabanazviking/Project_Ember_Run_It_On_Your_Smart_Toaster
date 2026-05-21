"""
Verðandi Health Checks — The Senses.

Each check is a pluggable module with a clear interface.
If one check fails, others continue. Graceful degradation is law.

Naming convention:
  - Eir: Health (CPU, RAM, disk, services)
  - Huginn: Projects (git repos, unpushed changes, stale branches)
  - Mímir: Memory (DB integrity, conversation log growth, fact store)
  - Urðr: Schedule (cron jobs, missed runs, stuck processes)
  - Skuld: Prediction (health trends, anomaly detection, capacity planning)
"""

from heartbeat.checks.base import BaseCheck, CheckResult, CheckSeverity
from heartbeat.checks.eir import EirCheck
from heartbeat.checks.huginn import HuginnCheck
from heartbeat.checks.mimir import MimirCheck
from heartbeat.checks.urdr import UrdrCheck
from heartbeat.checks.skuld import SkuldCheck

# Registry: name → class mapping
CHECK_REGISTRY: dict[str, type[BaseCheck]] = {
    "health": EirCheck,
    "projects": HuginnCheck,
    "memory": MimirCheck,
    "schedule": UrdrCheck,
    "prediction": SkuldCheck,
}

__all__ = [
    "BaseCheck", "CheckResult", "CheckSeverity",
    "EirCheck", "HuginnCheck", "MimirCheck", "UrdrCheck", "SkuldCheck",
    "CHECK_REGISTRY",
]