"""
Verðandi Heartbeat Actions — The Voice.

Where checks sense, actions speak. This module provides automated
recovery behaviors that respond to health check results.

The reactor pattern:
  1. Checks run and produce CheckResults with severity levels
  2. The reactor evaluates results against configured rules
  3. Matching rules trigger corresponding actions
  4. Actions execute (or dry-run) and produce ActionResults
  5. All outcomes are logged for audit

Available actions:
  - Mjölnir (auto_push): Auto-commit and push dirty/unpushed repos
  - Gungnir (auto_restart): Restart crashed or inactive systemd services
  - Bifrǫst (auto_cleanup): Prune logs, temp files, vacuum databases
  - Eir (auto_heal): Repair corrupted databases, rebuild indexes, fix configs
"""

from heartbeat.actions.base import (
    BaseAction,
    ActionSeverity,
    ActionResult,
    ActionContext,
    ACTION_REGISTRY,
    register_action,
)
from heartbeat.actions.mjölnir import MjölnirAction
from heartbeat.actions.gungnir import GungnirAction
from heartbeat.actions.bifrǫst import BifrǫstAction
from heartbeat.actions.eir_action import EirAction
from heartbeat.actions.vor_action import VörAction

__all__ = [
    "BaseAction",
    "ActionSeverity",
    "ActionResult",
    "ActionContext",
    "ACTION_REGISTRY",
    "register_action",
    "MjölnirAction",
    "GungnirAction",
    "BifrǫstAction",
    "EirAction",
    "VörAction",
]