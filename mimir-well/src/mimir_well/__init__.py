"""
Mímir's Well — AI Memory Database
===================================
Persistent, self-healing memory with Ebbinghaus decay, FTS5 search,
contradiction detection, knowledge promotion, token budgeting, and temporal validity.

ᛗ í ᛗ í ᚱ — From the Well, all wisdom flows.
"""

__version__ = "2.10.4"
__author__ = "Eldrä Járnsdóttir"
__description__ = "AI Memory Database with Ebbinghaus Decay, Self-Healing, Token Budgeting, and Temporal Validity"

from mimir_well.core import RunaMemory
from mimir_well.config import MimirConfig
from mimir_well.decay import (
    compute_ebbinghaus_decay,
    compute_reinforcement_boost,
    compute_confidence_for_promotion,
    should_decay,
    should_promote,
)
from mimir_well.repair import check_integrity, repair_database
from mimir_well.backup import (
    backup_database,
    backup_with_rotation,
    restore_from_backup,
    export_to_json,
)
from mimir_well.budget import (
    TokenBudget,
    TokenBudgeter,
    BudgetPriority,
    MemoryChannel,
    infer_channel,
)
from mimir_well.core import infer_memory_type, VALID_MEMORY_TYPES
from mimir_well.wyrd_graph import WyrdGraph
from mimir_well.context_engineer import ContextEngineer, ContextResult
from mimir_well.audit import AuditTrail, AuditAction, AuditEntry
from mimir_well.guard import (
    MemoryGuard, GuardResult, GuardSeverity,
    PatternSeverity, TrustLevel, SOURCE_TRUST, TRUSTED_SOURCES,
    VALID_CATEGORIES,
)
from mimir_well.migrations import MIGRATIONS
from mimir_well.migrations.runner import run_migrations, rollback_migration, get_schema_version

__all__ = [
    "RunaMemory",
    "MimirConfig",
    "compute_ebbinghaus_decay",
    "compute_reinforcement_boost",
    "compute_confidence_for_promotion",
    "should_decay",
    "should_promote",
    "check_integrity",
    "repair_database",
    "backup_database",
    "backup_with_rotation",
    "restore_from_backup",
    "export_to_json",
    # T5-1: Token Budgeting
    "TokenBudget",
    "TokenBudgeter",
    "BudgetPriority",
    "MemoryChannel",
    "infer_channel",
    # T5-2: Temporal Validity & Migrations
    "MIGRATIONS",
    "run_migrations",
    "rollback_migration",
    "get_schema_version",
    # T5-3: Memory Type Classification
    "infer_memory_type",
    "VALID_MEMORY_TYPES",
    # T6-1: Wyrd Graph Edge Layer
    "WyrdGraph",
    # T6-3: Context Engineering
    "ContextEngineer",
    "ContextResult",
    # T7-1: Memory Guard
    "MemoryGuard",
    "GuardResult",
    "GuardSeverity",
    "PatternSeverity",
    "TrustLevel",
    "SOURCE_TRUST",
    "TRUSTED_SOURCES",
    "VALID_CATEGORIES",
    # T7-2: Audit Trail
    "AuditTrail",
    "AuditAction",
    "AuditEntry",
]