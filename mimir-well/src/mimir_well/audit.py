"""Mímir Well — Audit Trail for memory traceability.

Records every write/update/delete/supersede action on memories,
providing a tamper-detection chain via content hashes and timestamps.

T8-5: Refactored to use thread-local connection reuse (matches RunaMemory pattern).
"""

import json
import logging
import sqlite3
import threading
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AuditAction:
    """Constants for audit action types."""
    STORE = "store"
    UPDATE = "update"
    DELETE = "delete"
    SUPERSEDE = "supersede"
    COMPRESS = "compress"


@dataclass
class AuditEntry:
    """A single audit trail entry."""
    id: int
    memory_id: int
    action: str
    source: str
    content_hash: str
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    user_id: str = "runa"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "memory_id": self.memory_id,
            "action": self.action,
            "source": self.source,
            "content_hash": self.content_hash,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
            "user_id": self.user_id,
        }


class AuditTrail:
    """Memory audit trail — records every write/update/delete for traceability.

    Uses thread-local connections for safe concurrent access, matching
    the RunaMemory pattern. No more open/close per call.

    Usage:
        # Log a memory write
        audit.log(memory_id=42, action="store", source="hermes",
                  content_hash="abc123", metadata={"category": "knowledge"})

        # Query audit history
        entries = audit.query(memory_id=42)
        entries = audit.query(source="hermes", action="store")
        entries = audit.query(since="2026-05-01")

        # Get full timeline for a memory
        timeline = audit.timeline(memory_id=42)
    """

    def __init__(self, db_path: str) -> None:
        """Initialize the audit trail.

        Args:
            db_path: Path to the SQLite database (shared with RunaMemory).
        """
        self.db_path = db_path
        self._local = threading.local()
        self._lock = threading.Lock()

    def _get_conn(self) -> sqlite3.Connection:
        """Get a thread-local database connection with row factory.

        Reuses the connection per thread instead of opening/closing
        on every call. Matches RunaMemory's pattern.
        """
        conn = getattr(self._local, 'conn', None)
        if conn is None:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA foreign_keys = ON")
            self._local.conn = conn
            logger.debug("AuditTrail: created new thread-local connection")
        return conn

    def _commit(self) -> None:
        """Commit the current transaction on the thread-local connection."""
        conn = self._get_conn()
        conn.commit()

    def close(self) -> None:
        """Close the thread-local database connection."""
        conn = getattr(self._local, 'conn', None)
        if conn is not None:
            conn.close()
            self._local.conn = None
            logger.debug("AuditTrail: closed thread-local connection")

    def __repr__(self) -> str:
        """String representation showing entry count."""
        try:
            conn = self._get_conn()
            count = conn.execute("SELECT COUNT(*) FROM memory_audit").fetchone()[0]
        except Exception:
            count = '?'
        return f"AuditTrail(entries={count})"

    def log(
        self,
        memory_id: int,
        action: str,
        source: str,
        content_hash: str,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: str = "runa",
    ) -> int:
        """Record an audit entry for a memory action.

        Args:
            memory_id: The ID of the affected memory.
            action: What happened ('store', 'update', 'delete', 'supersede', 'compress').
            source: Who made the change ('hermes', 'runa_remember', 'eir', 'nse', 'wyrd').
            content_hash: SHA-256 hash (first 16 chars) of the content at time of action.
            metadata: Optional JSON metadata (importance, category, trust_level, etc.).
            user_id: User namespace for multi-tenant isolation (default 'runa').

        Returns:
            The audit entry ID.
        """
        valid_actions = {
            AuditAction.STORE, AuditAction.UPDATE, AuditAction.DELETE,
            AuditAction.SUPERSEDE, AuditAction.COMPRESS,
        }
        if action not in valid_actions:
            logger.warning(f"Unknown audit action: {action} (logging anyway)")

        metadata_json = json.dumps(metadata or {})

        conn = self._get_conn()
        cursor = conn.execute(
            """INSERT INTO memory_audit (memory_id, action, source, content_hash, metadata, user_id)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (memory_id, action, source, content_hash, metadata_json, user_id),
        )
        self._commit()
        audit_id = cursor.lastrowid
        logger.debug(
            f"Audit: {action} memory_id={memory_id} source={source} "
            f"hash={content_hash[:8]}... (audit_id={audit_id})"
        )
        return audit_id

    def query(
        self,
        memory_id: Optional[int] = None,
        source: Optional[str] = None,
        action: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[AuditEntry]:
        """Query audit trail entries with optional filters.

        Args:
            memory_id: Filter by memory ID.
            source: Filter by source ('hermes', 'runa_remember', etc.).
            action: Filter by action type ('store', 'update', etc.).
            since: ISO timestamp — entries after this time.
            until: ISO timestamp — entries before this time.
            user_id: Filter by user namespace (None = all users).
            limit: Maximum entries to return (default 100).

        Returns:
            List of AuditEntry objects, most recent first.
        """
        clauses: List[str] = []
        params: List[Any] = []

        if memory_id is not None:
            clauses.append("memory_id = ?")
            params.append(memory_id)
        if source is not None:
            clauses.append("source = ?")
            params.append(source)
        if action is not None:
            clauses.append("action = ?")
            params.append(action)
        if since is not None:
            clauses.append("timestamp >= ?")
            params.append(since)
        if until is not None:
            clauses.append("timestamp <= ?")
            params.append(until)
        if user_id is not None:
            clauses.append("user_id = ?")
            params.append(user_id)

        where = " AND ".join(clauses) if clauses else "1=1"
        sql = f"""SELECT * FROM memory_audit
                   WHERE {where}
                   ORDER BY timestamp DESC
                   LIMIT ?"""
        params.append(limit)

        conn = self._get_conn()
        rows = conn.execute(sql, params).fetchall()
        return [
            AuditEntry(
                id=row["id"],
                memory_id=row["memory_id"],
                action=row["action"],
                source=row["source"],
                content_hash=row["content_hash"],
                timestamp=row["timestamp"],
                metadata=json.loads(row["metadata"] or "{}"),
                user_id=row["user_id"] if "user_id" in row.keys() else "runa",
            )
            for row in rows
        ]

    def timeline(self, memory_id: int, limit: int = 50) -> List[AuditEntry]:
        """Get the full audit timeline for a specific memory.

        Args:
            memory_id: The memory ID to trace.
            limit: Maximum entries to return.

        Returns:
            List of AuditEntry objects for this memory, most recent first.
        """
        return self.query(memory_id=memory_id, limit=limit)

    def stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get audit trail statistics.

        Args:
            user_id: Optional user namespace filter (None = all users).

        Returns:
            Dictionary with total entries, action counts, source counts,
            and time range.
        """
        conn = self._get_conn()

        if user_id:
            total = conn.execute(
                "SELECT COUNT(*) FROM memory_audit WHERE user_id = ?",
                (user_id,),
            ).fetchone()[0]
            action_counts = dict(
                conn.execute(
                    "SELECT action, COUNT(*) FROM memory_audit WHERE user_id = ? GROUP BY action",
                    (user_id,),
                ).fetchall()
            )
            source_counts = dict(
                conn.execute(
                    "SELECT source, COUNT(*) FROM memory_audit WHERE user_id = ? GROUP BY source",
                    (user_id,),
                ).fetchall()
            )
            time_range = conn.execute(
                "SELECT MIN(timestamp), MAX(timestamp) FROM memory_audit WHERE user_id = ?",
                (user_id,),
            ).fetchone()
        else:
            total = conn.execute("SELECT COUNT(*) FROM memory_audit").fetchone()[0]
            action_counts = dict(
                conn.execute(
                    "SELECT action, COUNT(*) FROM memory_audit GROUP BY action"
                ).fetchall()
            )
            source_counts = dict(
                conn.execute(
                    "SELECT source, COUNT(*) FROM memory_audit GROUP BY source"
                ).fetchall()
            )
            time_range = conn.execute(
                "SELECT MIN(timestamp), MAX(timestamp) FROM memory_audit"
            ).fetchone()

        return {
            "total_entries": total,
            "action_counts": action_counts,
            "source_counts": source_counts,
            "earliest": time_range[0],
            "latest": time_range[1],
        }

    def verify_integrity(self, memory_id: int, current_hash: str) -> Dict[str, Any]:
        """Verify a memory's content hash against the audit trail.

        Compares the current content hash with the most recent 'store' or
        'update' audit entry for the same memory. Detects tampering.

        Args:
            memory_id: The memory ID to verify.
            current_hash: The current content hash to check against.

        Returns:
            Dictionary with 'verified' (bool), 'last_audit_hash', 'last_audit_time',
            and 'matches' (bool).
        """
        entries = self.query(
            memory_id=memory_id,
            action=AuditAction.STORE,
            limit=1,
        )

        # Also check updates
        update_entries = self.query(
            memory_id=memory_id,
            action=AuditAction.UPDATE,
            limit=1,
        )

        # Use the most recent of store or update
        all_writes = entries + update_entries
        if not all_writes:
            return {
                "verified": False,
                "reason": "No audit entries found for this memory",
                "memory_id": memory_id,
            }

        all_writes.sort(key=lambda e: e.timestamp, reverse=True)
        latest = all_writes[0]

        matches = latest.content_hash == current_hash

        return {
            "verified": True,
            "memory_id": memory_id,
            "current_hash": current_hash,
            "last_audit_hash": latest.content_hash,
            "last_audit_time": latest.timestamp,
            "last_audit_source": latest.source,
            "matches": matches,
            "tampered": not matches,
        }