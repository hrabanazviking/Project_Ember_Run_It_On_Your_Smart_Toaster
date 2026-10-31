"""Tool framework — schemas + registry + approval + audit (ADR 0011).

Phase 14 ships the framework only. Phase 15 adds the first three
first-party tools at :mod:`ember.tools`; Phase 16 wires Munnr to
consume :class:`FuniReply.tool_calls` through this framework and bumps
to 0.2.0-rc1.

Public surface::

    from ember.spark.funi.tools import (
        ApprovalPrompter,
        AuditLog,
        StdinApprovalPrompter,
        list_tools,
        lookup,
        register,
        resolve_approval,
        resolve_with_answer,
        validate_arguments,
    )

See :file:`INTERFACE.md` for the operator-facing surface contract.
"""

from __future__ import annotations

from ember.spark.funi.tools.approval import (
    ApprovalDecision,
    ApprovalPrompter,
    PromptAnswer,
    StdinApprovalPrompter,
    resolve_with_answer,
)
from ember.spark.funi.tools.approval import resolve as resolve_approval
from ember.spark.funi.tools.audit import AuditLog
from ember.spark.funi.tools.permissions import (
    ToolPermissionShape,
    may_auto_approve,
    permission_shape,
    tool_inventory,
)
from ember.spark.funi.tools.registry import (
    ToolExecutor,
    clear,
    is_registered,
    list_tools,
    lookup,
    register,
    validate_arguments,
)

__all__ = [
    "ApprovalDecision",
    "ApprovalPrompter",
    "AuditLog",
    "PromptAnswer",
    "StdinApprovalPrompter",
    "ToolExecutor",
    "ToolPermissionShape",
    "clear",
    "is_registered",
    "list_tools",
    "lookup",
    "may_auto_approve",
    "permission_shape",
    "register",
    "resolve_approval",
    "resolve_with_answer",
    "tool_inventory",
    "validate_arguments",
]
