"""
Mímir's Well — Core Memory Database
=======================================
The main RunaMemory class: persistent, self-healing memory with
Ebbinghaus decay, FTS5 search, contradiction detection, and
knowledge promotion.

ᛗ í ᛗ í ᚱ — From the Well, all wisdom flows.
"""

import json
import hashlib
import logging
import re
import sqlite3
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from mimir_well.schema import (
    ALL_TABLES, FTS_TABLES, INDEXES, PRAGMAS, SCHEMA_VERSION
)
from mimir_well.config import MimirConfig
from mimir_well.guard import MemoryGuard, GuardResult, GuardSeverity
from mimir_well.audit import AuditTrail, AuditAction
from mimir_well.decay import (
    compute_ebbinghaus_decay, compute_reinforcement_boost,
    compute_confidence_for_promotion
)
from mimir_well.repair import check_integrity, repair_database
from mimir_well.backup import (
    backup_database, backup_with_rotation as _backup_with_rotation,
    restore_from_backup, export_to_json, github_backup
)

logger = logging.getLogger("mimir_well")

# ── T5-3: Memory Type Classification ──────────────────────────────────────

CATEGORY_TYPE_MAP = {
    "nse_character": "episodic",
    "nse_location": "episodic",
    "nse_relationship": "episodic",
    "saga_moment": "episodic",
    "preference": "semantic",
    "lesson": "procedural",
    "knowledge": "semantic",
    "relationship": "semantic",
    "science_discovery": "semantic",
    "spiritual": "semantic",
    "sexual": "episodic",
    "dream": "episodic",
    "brilliant": "episodic",
    "general": "episodic",
}

VALID_MEMORY_TYPES = {"episodic", "semantic", "procedural", "implicit"}


def infer_memory_type(category: str) -> str:
    """Auto-classify a memory type from its category.

    Returns one of: 'episodic', 'semantic', 'procedural', 'implicit'.
    Falls back to 'episodic' for unknown categories.
    """
    return CATEGORY_TYPE_MAP.get(category, "episodic")


class RunaMemory:
    """Persistent AI memory database with Ebbinghaus decay and self-healing.

    Mímir's Well stores memories, knowledge, entities, and relationships
    in a SQLite database with WAL mode, FTS5 full-text search, and
    Ebbinghaus-inspired forgetting curves. Memories that are used get
    stronger; memories that are forgotten decay.

    Thread-safe: uses per-thread connections with WAL mode.

    Example::

        from mimir_well import RunaMemory

        db = RunaMemory()
        db.add_memory("I prefer dark themes", category="preference", importance=7)
        results = db.search_memories("dark theme")
        db.close()
    """

    def __init__(self, db_path: Optional[str] = None, config: Optional[MimirConfig] = None):
        """Initialize the memory database.

        Args:
            db_path: Path to the SQLite database file. If None, uses
                ~/.mimir_well/mimir_well.db
            config: Optional MimirConfig instance. If None, loads from
                ~/.mimir_well/mimir-well-config.json
        """
        self._config = config or MimirConfig()
        if db_path:
            self.db_path = Path(db_path).expanduser()
        else:
            self.db_path = self._config.db_path

        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Thread-local storage for connections
        self._local = threading.local()
        self._lock = threading.RLock()

        # T7-1: Memory Guard for injection protection
        self.guard = MemoryGuard()

        # T7-2: Audit Trail for traceability
        from mimir_well.audit import AuditTrail
        self.audit = AuditTrail(str(self.db_path))

        # Initialize schema
        self._init_db()

        logger.info("Mímir's Well initialized at %s", self.db_path)

    # ─── Connection Management ────────────────────────────────────────────

    def _get_conn(self) -> sqlite3.Connection:
        """Get a thread-local database connection with row factory."""
        conn = getattr(self._local, 'conn', None)
        if conn is None:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            for pragma in PRAGMAS:
                cursor.execute(pragma)
            self._local.conn = conn
        return conn

    def _write(self, fn):
        """Execute a write operation with thread-safe commit.

        Args:
            fn: Callable that takes a connection and performs the write

        Returns:
            The return value of fn
        """
        with self._lock:
            conn = self._get_conn()
            result = fn(conn)
            conn.commit()
            return result

    def _commit(self):
        """Explicitly commit the current transaction (thread-safe)."""
        with self._lock:
            conn = self._get_conn()
            conn.commit()

    # ─── Schema Initialization ───────────────────────────────────────────

    def _init_db(self):
        """Initialize all tables, indexes, FTS, and triggers."""
        conn = self._get_conn()
        cursor = conn.cursor()

        for table_sql in ALL_TABLES:
            cursor.execute(table_sql)

        for index_sql in INDEXES:
            cursor.execute(index_sql)

        for fts_sql in FTS_TABLES:
            try:
                cursor.execute(fts_sql)
            except sqlite3.OperationalError:
                pass  # FTS table already exists

        # With content= mode, rebuild FTS indexes from existing data
        for fts_name in ["memories_fts", "knowledge_fts", "saga_events_fts"]:
            try:
                cursor.execute(f"INSERT INTO {fts_name}({fts_name}) VALUES('rebuild')")
            except sqlite3.OperationalError:
                pass  # Table doesn't exist yet or no data

        # ── Run pending migrations before stamping the version ──────────
        # P0 fix: The migration runner existed but was never called from
        # _init_db(), so databases created at earlier schema versions (e.g. v2)
        # had their version stamp bumped to SCHEMA_VERSION without actually
        # receiving the ALTER TABLE additions. This caused silent column
        # absence (valid_from, memory_type, user_id, etc.) and the 93% orphan
        # rate in Eir consolidation reports.
        from mimir_well.migrations.runner import run_migrations

        current_version = cursor.execute(
            "SELECT value FROM _schema_meta WHERE key = 'schema_version'"
        ).fetchone()
        if current_version is None:
            # Fresh database — stamp the current version
            cursor.execute(
                "INSERT OR REPLACE INTO _schema_meta (key, value) VALUES (?, ?)",
                ("schema_version", str(SCHEMA_VERSION)),
            )
        elif int(current_version[0]) < SCHEMA_VERSION:
            # Existing database behind current schema — run all pending migrations
            logger.info(
                "Database schema v%d behind current v%d — running migrations",
                int(current_version[0]),
                SCHEMA_VERSION,
            )
            applied = run_migrations(conn, target_version=SCHEMA_VERSION)
            if applied:
                logger.info("Applied migrations: %s", applied)

        conn.commit()

    # ─── CRUD: Memories ──────────────────────────────────────────────────

    def add_memory(self, content: str, category: str = "general",
                   tags: Optional[Any] = None, importance: int = 5,
                   emotional_valence: float = 0.0,
                   memory_type: Optional[str] = None,
                   source: str = "mimir",
                   user_id: str = "runa") -> Optional[int]:
        """Store a new memory.

        Args:
            content: The memory content to store
            category: Category label (e.g., 'preference', 'lesson')
            tags: Tags as string or list
            importance: Importance 1-10 (default 5)
            emotional_valence: Emotion -1.0 to 1.0 (default 0.0)
            memory_type: 'episodic', 'semantic', 'procedural', or 'implicit'.
                If None, auto-classified from category via infer_memory_type().
            source: Origin of the write ('mimir', 'hermes', 'runa_remember', 'eir', 'nse')
            user_id: User namespace for multi-tenant isolation (default 'runa')

        Returns:
            The ID of the new memory, or -1 if blocked
        """
        if isinstance(tags, list):
            tags = json.dumps(tags)
        emotional_valence = max(-1.0, min(1.0, emotional_valence))
        importance = max(1, min(10, importance))

        # T7-1: Validate content through MemoryGuard
        guard_result = self.guard.validate_write(
            content=content,
            source=source,
            category=category,
            importance=importance,
            tags=json.loads(tags) if isinstance(tags, str) else tags,
        )
        if not guard_result.is_valid:
            logger.warning(
                "Memory write BLOCKED by Guard: %s (content: %.50s...)",
                guard_result.reason, content[:50],
            )
            return None
        # Use sanitized content if available
        if guard_result.sanitized_content:
            content = guard_result.sanitized_content

        # T5-3: Auto-classify memory type from category if not provided
        if memory_type is None:
            memory_type = infer_memory_type(category)

        def _insert(conn):
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO memories (content, category, tags, importance, emotional_valence, memory_type, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (content, category, tags, importance, emotional_valence, memory_type, user_id))
            return cursor.lastrowid
        memory_id = self._write(_insert)

        # T7-2: Audit trail — log the store action
        if memory_id > 0:
            self.audit.log(
                memory_id=memory_id,
                action=AuditAction.STORE,
                source=source,
                content_hash=guard_result.content_hash or hashlib.sha256(content.encode()).hexdigest()[:16],
                user_id=user_id,
                metadata={
                    "category": category,
                    "importance": importance,
                    "trust_level": guard_result.trust_level.name if guard_result.trust_level else "UNKNOWN",
                    "guard_severity": guard_result.severity.value,
                },
            )
        return memory_id

    def get_memory(self, memory_id: int, user_id: Optional[str] = None) -> Optional[Dict]:
        """Retrieve a specific memory by ID.

        Args:
            memory_id: The memory ID to look up.
            user_id: If provided, only return the memory if it belongs to this user.
                None (default) returns the memory regardless of ownership.

        Returns:
            Dict of memory fields, or None if not found (or not owned by user_id).
        """
        conn = self._get_conn()
        if user_id:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM memories WHERE id = ? AND user_id = ?",
                (memory_id, user_id),
            )
        else:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM memories WHERE id = ?", (memory_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def search_memories(self, query: str, category: Optional[str] = None,
                        limit: int = 20, user_id: Optional[str] = None) -> List[Dict]:
        """Search memories by content using LIKE.

        For full-text search, use fts_search() instead.

        Args:
            query: Search string.
            category: Filter by category.
            limit: Max results.
            user_id: Filter by user namespace (None = all users).
        """
        cursor = self._get_conn().cursor()
        if category and user_id:
            cursor.execute("""
                SELECT * FROM memories
                WHERE content LIKE ? AND category = ? AND user_id = ?
                ORDER BY importance DESC, timestamp DESC
                LIMIT ?
            """, (f"%{query}%", category, user_id, limit))
        elif category:
            cursor.execute("""
                SELECT * FROM memories
                WHERE content LIKE ? AND category = ?
                ORDER BY importance DESC, timestamp DESC
                LIMIT ?
            """, (f"%{query}%", category, limit))
        elif user_id:
            cursor.execute("""
                SELECT * FROM memories
                WHERE content LIKE ? AND user_id = ?
                ORDER BY importance DESC, timestamp DESC
                LIMIT ?
            """, (f"%{query}%", user_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM memories
                WHERE content LIKE ?
                ORDER BY importance DESC, timestamp DESC
                LIMIT ?
            """, (f"%{query}%", limit))
        return [dict(row) for row in cursor.fetchall()]

    def update_memory(self, memory_id: int, source: str = "unknown",
                     user_id: str = "runa", **kwargs) -> bool:
        """Update specific fields of a memory.

        Args:
            memory_id: ID of the memory to update.
            source: Origin of the action (audit trail).
            user_id: User namespace for the audit entry.
            **kwargs: Fields to update (content, category, tags, importance, emotional_valence).
        """
        allowed_fields = {'content', 'category', 'tags', 'importance', 'emotional_valence'}
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return False

        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [memory_id]

        # Compute content hash for audit before the update
        content_hash = hashlib.sha256(
            (updates.get("content") or str(memory_id)).encode()
        ).hexdigest()[:16]

        def _update(conn):
            cursor = conn.execute(
                f"UPDATE memories SET {set_clause} WHERE id = ? AND user_id = ?",
                values + [user_id],
            )
            return cursor.rowcount > 0
        result = self._write(_update)

        # T7-2: Audit trail — log the update action
        if result:
            self.audit.log(
                memory_id=memory_id,
                action=AuditAction.UPDATE,
                source=source,
                content_hash=content_hash,
                user_id=user_id,
                metadata={"updated_fields": list(updates.keys())},
            )
        return result

    def delete_memory(self, memory_id: int, source: str = "unknown",
                     user_id: str = "runa") -> bool:
        """Delete a memory by ID (also removes access log entries).

        Args:
            memory_id: ID of the memory to delete.
            source: Origin of the action (audit trail).
            user_id: User namespace for the audit entry.
        """

        # T7-2: Audit trail — log the delete action (hash of the ID since content is gone)
        content_hash = hashlib.sha256(str(memory_id).encode()).hexdigest()[:16]

        def _delete(conn):
            conn.execute(
                "DELETE FROM memory_access_log WHERE memory_id = ?", (memory_id,)
            )
            cursor = conn.execute(
                "DELETE FROM memories WHERE id = ? AND user_id = ?",
                (memory_id, user_id),
            )
            return cursor.rowcount > 0
        result = self._write(_delete)

        # Log delete after successful removal
        if result:
            self.audit.log(
                memory_id=memory_id,
                action=AuditAction.DELETE,
                source=source,
                content_hash=content_hash,
                user_id=user_id,
                metadata={"action": "delete"},
            )
        return result

    # ─── CRUD: Saga Events ───────────────────────────────────────────────

    def add_saga_event(self, event_type: str, entity_id: Optional[str] = None,
                       data: Optional[Dict] = None,
                       participants: Optional[List[str]] = None) -> int:
        """Record a saga (life event) in the memory system."""
        participants_json = json.dumps(participants) if participants else None
        data_json = json.dumps(data) if data else None

        def _insert(conn):
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO saga_events (event_type, entity_id, data, participants)
                VALUES (?, ?, ?, ?)
            """, (event_type, entity_id, data_json, participants_json))
            return cursor.lastrowid
        return self._write(_insert)

    # ─── CRUD: Entities ──────────────────────────────────────────────────

    def add_entity(self, entity_id: str, entity_type: str,
                   components: Optional[Dict] = None,
                   state: Optional[Dict] = None) -> bool:
        """Add or update an entity in the knowledge graph."""
        comps_json = json.dumps(components) if components else "{}"
        state_json = json.dumps(state) if state else "{}"

        def _upsert(conn):
            conn.execute("""
                INSERT OR REPLACE INTO entities (entity_id, entity_type, components, state, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (entity_id, entity_type, comps_json, state_json))
            return True
        return self._write(_upsert)

    def get_entity(self, entity_id: str) -> Optional[Dict]:
        """Retrieve an entity by ID."""
        cursor = self._get_conn().cursor()
        cursor.execute("SELECT * FROM entities WHERE entity_id = ?", (entity_id,))
        row = cursor.fetchone()
        if row:
            data = dict(row)
            data['components'] = json.loads(data.get('components', '{}'))
            data['state'] = json.loads(data.get('state', '{}'))
            return data
        return None

    def get_entities_by_type(self, entity_type: str) -> List[Dict]:
        """Get all entities of a specific type."""
        cursor = self._get_conn().cursor()
        cursor.execute("SELECT * FROM entities WHERE entity_type = ?", (entity_type,))
        results = []
        for row in cursor.fetchall():
            data = dict(row)
            data['components'] = json.loads(data.get('components', '{}'))
            data['state'] = json.loads(data.get('state', '{}'))
            results.append(data)
        return results

    # ─── CRUD: Relationships ──────────────────────────────────────────────

    def set_relationship(self, entity_a: str, entity_b: str,
                         relationship_type: str = "related",
                         strength: int = 5,
                         metadata: Optional[Dict] = None) -> bool:
        """Create or update a relationship between two entities."""
        meta_json = json.dumps(metadata) if metadata else None

        def _upsert(conn):
            conn.execute("""
                INSERT OR REPLACE INTO relationships (entity_a, entity_b, relationship_type, strength, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (entity_a, entity_b, relationship_type, strength, meta_json))
            return True
        return self._write(_upsert)

    def get_relationship_strength(self, entity_a: str, entity_b: str) -> Optional[int]:
        """Get the strength of a relationship."""
        cursor = self._get_conn().cursor()
        cursor.execute("""
            SELECT strength FROM relationships
            WHERE (entity_a = ? AND entity_b = ?) OR (entity_a = ? AND entity_b = ?)
        """, (entity_a, entity_b, entity_b, entity_a))
        row = cursor.fetchone()
        return row['strength'] if row else None

    # ─── CRUD: Conversations ─────────────────────────────────────────────

    def save_conversation(self, session_id: str, participants: List[str],
                          transcript: Optional[str] = None,
                          summary: Optional[str] = None):
        """Save a conversation session."""
        def _upsert(conn):
            conn.execute("""
                INSERT OR REPLACE INTO conversations
                (session_id, participants, transcript, summary, timestamp)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (session_id, json.dumps(participants), transcript, summary))
        self._write(_upsert)

    def get_conversation(self, session_id: str) -> Optional[Dict]:
        """Retrieve a conversation by session ID."""
        cursor = self._get_conn().cursor()
        cursor.execute("SELECT * FROM conversations WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    # ─── CRUD: Knowledge ──────────────────────────────────────────────────

    def add_knowledge(self, domain: str, content: str,
                      source: Optional[str] = None,
                      confidence: float = 1.0) -> int:
        """Store a piece of knowledge.

        Args:
            domain: Knowledge domain (e.g., 'norse_mythology', 'python')
            content: The knowledge content
            source: Where this knowledge came from
            confidence: 0.0-1.0 confidence level
        """
        confidence = max(0.0, min(1.0, confidence))

        def _insert(conn):
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO knowledge (domain, content, source, confidence)
                VALUES (?, ?, ?, ?)
            """, (domain, content, source, confidence))
            return cursor.lastrowid
        return self._write(_insert)

    def search_knowledge(self, domain: str, query: str,
                          limit: int = 20,
                          user_id: Optional[str] = None) -> List[Dict]:
        """Search knowledge within a domain.

        Args:
            domain: Knowledge domain to search in.
            query: Search string (LIKE pattern).
            limit: Maximum results to return.
            user_id: Filter by user namespace (None = all users).
        """
        conn = self._get_conn()
        if user_id:
            rows = conn.execute("""
                SELECT * FROM knowledge
                WHERE domain = ? AND content LIKE ? AND user_id = ?
                ORDER BY confidence DESC, created_at DESC
                LIMIT ?
            """, (domain, f"%{query}%", user_id, limit)).fetchall()
        else:
            rows = conn.execute("""
                SELECT * FROM knowledge
                WHERE domain = ? AND content LIKE ?
                ORDER BY confidence DESC, created_at DESC
                LIMIT ?
            """, (domain, f"%{query}%", limit)).fetchall()
        return [dict(row) for row in rows]

    # ─── FTS5 Search ──────────────────────────────────────────────────────

    VALID_FTS_TABLES = {"memories", "knowledge", "saga_events"}

    def fts_search(self, table: str, query: str, limit: int = 20,
                    user_id: Optional[str] = None) -> List[Dict]:
        """Full-text search using FTS5 on a source table.

        Args:
            table: One of 'memories', 'knowledge', 'saga_events'
            query: FTS5 query string
            limit: Max results
            user_id: Filter by user namespace (None = all users).
        """
        if table not in self.VALID_FTS_TABLES:
            raise ValueError(f"Invalid FTS table '{table}'. Must be one of {self.VALID_FTS_TABLES}")
        fts_table = f"{table}_fts"
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            if user_id and table == "memories":
                cursor.execute(f"""
                    SELECT src.*, fts.rank
                    FROM {fts_table} fts
                    JOIN {table} src ON src.id = fts.rowid
                    WHERE {fts_table} MATCH ? AND src.user_id = ?
                    ORDER BY fts.rank
                    LIMIT ?
                """, (query, user_id, limit))
            else:
                cursor.execute(f"""
                    SELECT src.*, fts.rank
                    FROM {fts_table} fts
                    JOIN {table} src ON src.id = fts.rowid
                    WHERE {fts_table} MATCH ?
                    ORDER BY fts.rank
                    LIMIT ?
                """, (query, limit))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            return self.search_memories(query, limit=limit, user_id=user_id)

    # ─── Recall Methods ───────────────────────────────────────────────────

    def recall_by_importance(self, min_importance: int = 7,
                              category: Optional[str] = None,
                              limit: int = 10,
                              user_id: Optional[str] = None) -> List[Dict]:
        """Retrieve high-importance memories.

        Args:
            min_importance: Minimum importance threshold (default 7).
            category: Filter by category.
            limit: Max results.
            user_id: Filter by user namespace (None = all users).
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        if category and user_id:
            cursor.execute("""
                SELECT * FROM memories
                WHERE importance >= ? AND category = ? AND user_id = ?
                ORDER BY importance DESC, timestamp DESC LIMIT ?
            """, (min_importance, category, user_id, limit))
        elif category:
            cursor.execute("""
                SELECT * FROM memories
                WHERE importance >= ? AND category = ?
                ORDER BY importance DESC, timestamp DESC LIMIT ?
            """, (min_importance, category, limit))
        elif user_id:
            cursor.execute("""
                SELECT * FROM memories
                WHERE importance >= ? AND user_id = ?
                ORDER BY importance DESC, timestamp DESC LIMIT ?
            """, (min_importance, user_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM memories
                WHERE importance >= ?
                ORDER BY importance DESC, timestamp DESC LIMIT ?
            """, (min_importance, limit))
        results = [dict(row) for row in cursor.fetchall()]
        for m in results:
            self._log_access(m["id"], "recall_core")
        return results

    def recall_recent(self, hours: int = 24, limit: int = 5,
                      user_id: Optional[str] = None) -> List[Dict]:
        """Retrieve memories from the last N hours.

        Args:
            hours: How far back to look (default 24).
            limit: Max results.
            user_id: Filter by user namespace (None = all users).
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        if user_id:
            cursor.execute("""
                SELECT * FROM memories
                WHERE timestamp >= datetime('now', ?) AND user_id = ?
                ORDER BY importance DESC, timestamp DESC LIMIT ?
            """, (f'-{hours} hours', user_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM memories
                WHERE timestamp >= datetime('now', ?)
                ORDER BY importance DESC, timestamp DESC LIMIT ?
            """, (f'-{hours} hours', limit))
        results = [dict(row) for row in cursor.fetchall()]
        for m in results:
            self._log_access(m["id"], "recall_recent")
        return results

    def recall_by_mood(self, target_valence: float = 0.0,
                        tolerance: float = 0.3,
                        limit: int = 5,
                        category: Optional[str] = None,
                        user_id: Optional[str] = None) -> List[Dict]:
        """Recall memories matching an emotional context.

        Args:
            target_valence: Target emotional valence (-1.0 to 1.0).
            tolerance: How close the valence must be (default 0.3).
            limit: Max results.
            category: Filter by category.
            user_id: Filter by user namespace (None = all users).
        """
        cursor = self._get_conn().cursor()
        query = """
            SELECT *, ABS(emotional_valence - ?) AS valence_distance
            FROM memories WHERE ABS(emotional_valence - ?) <= ?
        """
        params = [target_valence, target_valence, tolerance]
        if category:
            query += " AND category = ?"
            params.append(category)
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        query += " ORDER BY valence_distance ASC, importance DESC LIMIT ?"
        params.append(limit)
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    # ── T5-2: Temporal Validity ────────────────────────────────────────────

    def store_with_validity(
        self,
        content: str,
        category: str = "general",
        tags: Optional[Any] = None,
        importance: int = 5,
        emotional_valence: float = 0.0,
        valid_from: Optional[str] = None,
        valid_until: Optional[str] = None,
        user_id: str = "runa",
        source: str = "temporal",
    ) -> int:
        """Store a memory with a temporal validity window.

        Facts that are only true within a time range (e.g. \"staying at
        Hotel X until Friday\") get valid_from/valid_until. Facts without
        an expiry are NULL in both columns (always valid).

        Args:
            content: The memory content to store.
            category: Category label.
            tags: Tags as string or list.
            importance: 1-10 (default 5).
            emotional_valence: -1.0 to 1.0.
            valid_from: ISO datetime string — fact becomes true at this time.
            valid_until: ISO datetime string — fact expires after this time.
            user_id: User namespace (default 'runa').
            source: Source label for audit trail.

        Returns:
            The ID of the new memory.
        """
        memory_id = self.add_memory(
            content=content,
            category=category,
            tags=tags,
            importance=importance,
            emotional_valence=emotional_valence,
            user_id=user_id,
            source=source,
        )
        if memory_id < 0:
            return memory_id  # Blocked by filter

        def _update_validity(conn):
            conn.execute(
                "UPDATE memories SET valid_from=?, valid_until=? WHERE id=? AND user_id=?",
                (valid_from, valid_until, memory_id, user_id),
            )
        self._write(_update_validity)
        return memory_id

    def supersede(
        self,
        old_memory_id: int,
        new_content: str,
        category: Optional[str] = None,
        importance: Optional[int] = None,
        tags: Optional[Any] = None,
        emotional_valence: Optional[float] = None,
        user_id: str = "runa",
        source: str = "supersede",
    ) -> Optional[int]:
        """Mark an old memory as superseded by a new one.

        Use this when a preference or fact changes (e.g. "I'm vegetarian"
        → "I eat fish now"). The old memory gets is_current=0 and a
        superseded_by reference to the new memory. The new memory
        inherits the old memory's category and importance if not provided.

        Args:
            old_memory_id: The memory to supersede.
            new_content: The updated content.
            category: Category for the new memory (inherits from old if None).
            importance: Importance for the new memory (inherits from old if None).
            tags: Tags (inherits from old if None).
            emotional_valence: (inherits from old if None).
            user_id: User namespace (default 'runa'). New memory is attributed
                to this user. Old memory must belong to this user to supersede.
            source: Source label for audit trail.

        Returns:
            The ID of the new (superseding) memory.
        """
        old = self.get_memory(old_memory_id, user_id=user_id)
        if old is None:
            logger.warning(
                "Cannot supersede memory %d — not found or not owned by user '%s'.",
                old_memory_id, user_id,
            )
            return None

        # Inherit from old memory if not explicitly provided
        _category = category or old.get("category", "general")
        _importance = importance if importance is not None else old.get("importance", 5)
        _tags = tags if tags is not None else old.get("tags")
        _valence = emotional_valence if emotional_valence is not None else old.get("emotional_valence", 0.0)

        new_id = self.add_memory(
            content=new_content,
            category=_category,
            tags=_tags,
            importance=_importance,
            emotional_valence=_valence,
            user_id=user_id,
            source=source,
        )

        if new_id < 0:
            return new_id  # Store blocked

        # Mark old memory as superseded (only if owned by this user)
        def _mark_superseded(conn):
            cursor = conn.execute(
                "UPDATE memories SET is_current=0, superseded_by=? WHERE id=? AND user_id=?",
                (new_id, old_memory_id, user_id),
            )
            return cursor.rowcount > 0
        result = self._write(_mark_superseded)

        logger.info(
            "Memory %d superseded by %d: '%s' → '%s'",
            old_memory_id, new_id,
            old.get("content", "")[:40], new_content[:40],
        )
        return new_id

    def recall_current(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 10,
        min_importance: int = 5,
        now: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> List[Dict]:
        """Recall only currently-valid memories.

        Filters out:
        - Memories with is_current=0 (superseded)
        - Memories whose valid_from is in the future
        - Memories whose valid_until is in the past

        Args:
            query: Optional FTS5 search string.
            category: Filter by category.
            limit: Max results.
            min_importance: Minimum importance threshold.
            now: Override current time (ISO string). Defaults to UTC now.
            user_id: Filter by user namespace (None = all users, 'runa' = Runa only).

        Returns:
            List of currently-valid memory dicts.
        """
        from datetime import datetime as _dt

        if now is None:
            now = _dt.utcnow().isoformat()

        base_sql = """
            SELECT * FROM memories
            WHERE is_current = 1
            AND (valid_from IS NULL OR valid_from <= ?)
            AND (valid_until IS NULL OR valid_until >= ?)
        """
        params: list = [now, now]

        if user_id is not None:
            base_sql += " AND user_id = ?"
            params.append(user_id)

        if category:
            base_sql += " AND category = ?"
            params.append(category)

        if min_importance > 1:
            base_sql += " AND importance >= ?"
            params.append(min_importance)

        base_sql += " ORDER BY importance DESC, timestamp DESC LIMIT ?"
        params.append(limit)

        cursor = self._get_conn().cursor()
        cursor.execute(base_sql, params)
        results = [dict(row) for row in cursor.fetchall()]

        for m in results:
            self._log_access(m["id"], "recall_current")

        return results

    # ─── Access Logging ──────────────────────────────────────────────────

    def _log_access(self, memory_id: int, access_type: str = "recall") -> None:
        """Log that a memory was accessed (for Ebbinghaus tracking)."""
        try:
            self._write(
                lambda conn: conn.execute(
                    "INSERT INTO memory_access_log (memory_id, access_type) VALUES (?, ?)",
                    (memory_id, access_type),
                )
            )
        except Exception:
            pass  # Non-critical

    def log_access(self, memory_id: int, access_type: str = "recall") -> None:
        """Public interface for access logging."""
        self._log_access(memory_id, access_type)

    # ─── Ebbinghaus Decay ─────────────────────────────────────────────────

    def decay(self, half_life_days: float = 30.0, min_importance: int = 1,
             user_id: Optional[str] = None) -> Dict[str, int]:
        """Apply Ebbinghaus forgetting curve to memory importance.

        Memories decay over time unless reinforced. The half-life determines
        how quickly importance fades. Accessing a memory resets its decay.

        Args:
            half_life_days: Days for importance to halve (default 30)
            min_importance: Below this threshold, memories are prunable
            user_id: Filter by user namespace (None = all users).

        Returns:
            Dict with 'decayed', 'pruned', 'reinforced' counts
        """
        with self._lock:
            return self._decay_inner(half_life_days, min_importance, user_id)

    def _decay_inner(self, half_life_days: float, min_importance: int,
                     user_id: Optional[str]) -> Dict[str, int]:
        """Inner decay implementation — called with lock held."""
        decay_factor = 0.5 ** (1.0 / half_life_days)
        conn = self._get_conn()
        now = datetime.now()
        decayed = 0
        pruned = 0
        reinforced = 0

        # N+1 fix: JOIN memories with access log in a single query
        # instead of per-row SELECT MAX(accessed_at)
        if user_id:
            cursor = conn.execute(
                """
                SELECT m.id, m.importance, m.timestamp,
                       COALESCE(a.last_access, m.timestamp) AS last_accessed
                FROM memories m
                LEFT JOIN (
                    SELECT memory_id, MAX(accessed_at) AS last_access
                    FROM memory_access_log
                    GROUP BY memory_id
                ) a ON m.id = a.memory_id
                WHERE m.is_current = 1 AND m.user_id = ?
                """,
                (user_id,),
            )
        else:
            cursor = conn.execute(
                """
                SELECT m.id, m.importance, m.timestamp,
                       COALESCE(a.last_access, m.timestamp) AS last_accessed
                FROM memories m
                LEFT JOIN (
                    SELECT memory_id, MAX(accessed_at) AS last_access
                    FROM memory_access_log
                    GROUP BY memory_id
                ) a ON m.id = a.memory_id
                WHERE m.is_current = 1
                """,
            )
        rows = cursor.fetchall()

        for row in rows:
            mem_id, importance, timestamp_str = row["id"], row["importance"], row["timestamp"]
            try:
                timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else now
            except (ValueError, TypeError):
                timestamp = now

            # Use pre-joined last_accessed instead of N+1 query
            last_accessed_str = row["last_accessed"]
            try:
                last_accessed = datetime.fromisoformat(last_accessed_str) if last_accessed_str else timestamp
            except (ValueError, TypeError):
                last_accessed = timestamp

            days_since = (now - last_accessed).total_seconds() / 86400.0
            new_importance = importance * (decay_factor ** days_since)

            if new_importance < min_importance:
                conn.execute("UPDATE memories SET importance = ? WHERE id = ?",
                            (max(1, round(new_importance)), mem_id))
                pruned += 1
            else:
                conn.execute("UPDATE memories SET importance = ? WHERE id = ?",
                            (max(1, min(10, round(new_importance))), mem_id))
                decayed += 1

        # Reinforce recently accessed memories (single UPDATE, no N+1)
        yesterday = (now - timedelta(hours=24)).isoformat()
        if user_id:
            reinforced = conn.execute(
                """
                UPDATE memories SET importance = MIN(importance + 0.5, 10)
                WHERE id IN (
                    SELECT DISTINCT mal.memory_id
                    FROM memory_access_log mal
                    JOIN memories m ON m.id = mal.memory_id
                    WHERE mal.accessed_at > ? AND m.importance < 10 AND m.user_id = ?
                )
                """,
                (yesterday, user_id),
            ).rowcount
        else:
            reinforced = conn.execute(
                """
                UPDATE memories SET importance = MIN(importance + 0.5, 10)
                WHERE id IN (
                    SELECT DISTINCT mal.memory_id
                    FROM memory_access_log mal
                    JOIN memories m ON m.id = mal.memory_id
                    WHERE mal.accessed_at > ? AND m.importance < 10
                )
                """,
                (yesterday,),
            ).rowcount

        self._commit()
        return {"decayed": decayed, "pruned": pruned, "reinforced": reinforced}

    # ─── Consolidation ────────────────────────────────────────────────────

    def consolidate(self, user_id: Optional[str] = None) -> Dict[str, int]:
        """Session-end consolidation: Ebbinghaus decay + promotion + pruning.

        Three operations:
        1. DECAY: Memories not accessed in 30+ days lose 1 importance point
        2. PROMOTE: Memories accessed 3+ times in 7 days gain 1 importance
        3. PRUNE: Relationships below strength 1 are deleted

        Args:
            user_id: User namespace to consolidate (None = all users).

        Returns:
            Dict with counts: {"decayed": N, "promoted": N, "pruned": N}
        """
        with self._lock:
            return self._consolidate_inner(user_id)

    def _consolidate_inner(self, user_id: Optional[str] = None) -> Dict[str, int]:
        """Inner consolidate implementation — called with lock held."""
        report = {"decayed": 0, "promoted": 0, "pruned": 0}
        conn = self._get_conn()
        cursor = conn.cursor()

        user_filter = " AND user_id = ?" if user_id else ""
        user_params = [user_id] if user_id else []

        # 1. Decay old, unaccessed memories
        cursor.execute(f"""
            UPDATE memories
            SET importance = MAX(1, importance - 1)
            WHERE importance > 5
            AND timestamp < datetime('now', '-30 days'){user_filter}
            AND id NOT IN (
                SELECT memory_id FROM memory_access_log
                WHERE accessed_at > datetime('now', '-7 days')
            )
        """, user_params)
        report["decayed"] = cursor.rowcount

        # 2. Promote frequently-accessed memories
        cursor.execute(f"""
            UPDATE memories
            SET importance = MIN(10, importance + 1)
            WHERE id IN (
                SELECT memory_id FROM memory_access_log
                WHERE accessed_at > datetime('now', '-7 days')
                GROUP BY memory_id
                HAVING COUNT(*) >= 3
            )
            AND importance < 9{user_filter}
        """, user_params)
        report["promoted"] = cursor.rowcount

        # 3. Prune weak relationships
        # NOTE: relationships table doesn't have user_id yet;
        # filter only when the column exists (added in future migration)
        if user_id:
            try:
                cursor.execute(
                    "DELETE FROM relationships WHERE strength < 1.0 AND user_id = ?",
                    (user_id,),
                )
            except Exception:
                cursor.execute("DELETE FROM relationships WHERE strength < 1.0")
        else:
            cursor.execute("DELETE FROM relationships WHERE strength < 1.0")
        report["pruned"] = cursor.rowcount

        # 4. Clean up old access logs (keep 90 days)
        cursor.execute("""
            DELETE FROM memory_access_log
            WHERE accessed_at < datetime('now', '-90 days')
        """)

        self._commit()
        logger.info("Mímir consolidation: decayed=%d, promoted=%d, pruned=%d",
                     report["decayed"], report["promoted"], report["pruned"])
        return report

    # ─── Knowledge Promotion ──────────────────────────────────────────────

    def promote_to_knowledge(self, min_importance: int = 8,
                            user_id: Optional[str] = None) -> Dict[str, int]:
        """Promote high-importance memories to knowledge entries.

        Memories above the threshold are converted into knowledge entries
        with higher confidence — crystallizing experience into wisdom.

        Args:
            min_importance: Minimum importance to promote (default 8)
            user_id: Filter by user namespace (None = all users).

        Returns:
            Dict with 'promoted' and 'skipped' counts
        """
        conn = self._get_conn()
        promoted = 0
        skipped = 0

        if user_id:
            cursor = conn.execute(
                "SELECT id, content, category, emotional_valence, timestamp FROM memories "
                "WHERE importance >= ? AND user_id = ?", (min_importance, user_id)
            )
        else:
            cursor = conn.execute(
                "SELECT id, content, category, emotional_valence, timestamp FROM memories "
                "WHERE importance >= ?", (min_importance,)
            )

        # Batch check: get all content already in knowledge to avoid N+1
        rows = cursor.fetchall()
        if not rows:
            return {"promoted": 0, "skipped": 0}

        contents = [row["content"] for row in rows]
        placeholders = ",".join("?" * len(contents))
        existing_set = {
            row["content"] for row in conn.execute(
                f"SELECT content FROM knowledge WHERE content IN ({placeholders})",
                contents
            ).fetchall()
        }

        for row in rows:
            mem_id, content, category, valence, timestamp_str = (
                row["id"], row["content"], row["category"],
                row["emotional_valence"], row["timestamp"]
            )
            if content in existing_set:
                skipped += 1
                continue

            confidence = compute_confidence_for_promotion(min_importance, valence or 0.0)
            conn.execute(
                "INSERT INTO knowledge (domain, content, confidence, source, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (category or "general", content, round(confidence, 2),
                 f"promoted_from_memory_{mem_id}", timestamp_str or datetime.now().isoformat())
            )
            existing_set.add(content)  # Track newly inserted to avoid duplicates within batch
            promoted += 1

        self._commit()
        return {"promoted": promoted, "skipped": skipped}

    # ─── Contradiction Detection ──────────────────────────────────────────

    def detect_contradictions(self, category: Optional[str] = None,
                               limit: int = 20,
                               user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Detect contradictory memories — conflicting beliefs or facts.

        Scans for:
        1. Opposing preferences (love/hate, like/dislike, etc.)
        2. Valence inversions (same topic, opposite emotions)
        3. Conflicting knowledge entries (same domain, divergent confidence)

        Args:
            category: Filter by category.
            limit: Max contradictions to return.
            user_id: Filter by user namespace (None = all users).
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        contradictions = []
        search_limit = limit * 3

        user_filter = " AND user_id = ?" if user_id else ""
        user_params = [user_id] if user_id else []

        # Strategy 1: Opposing preference pairs
        preference_pairs = [
            ("love", "hate"), ("like", "dislike"), ("prefer", "avoid"),
            ("always", "never"), ("best", "worst"), ("favorite", "least"),
        ]

        for positive, negative in preference_pairs:
            cursor.execute(f"""
                SELECT id, content, category, emotional_valence
                FROM memories WHERE emotional_valence > 0.2
                AND content LIKE ?{user_filter} ORDER BY importance DESC LIMIT ?
            """, [f"%{positive}%"] + user_params + [search_limit])
            pos = cursor.fetchall()

            cursor.execute(f"""
                SELECT id, content, category, emotional_valence
                FROM memories WHERE emotional_valence < -0.2
                AND content LIKE ?{user_filter} ORDER BY importance DESC LIMIT ?
            """, [f"%{negative}%"] + user_params + [search_limit])
            neg = cursor.fetchall()

            for p in pos:
                p_words = set(w.lower() for w in (p["content"] or "").split() if len(w) > 4)
                if not p_words:
                    continue
                for n in neg:
                    n_words = set(w.lower() for w in (n["content"] or "").split() if len(w) > 4)
                    shared = p_words & n_words
                    if len(shared) >= 2:
                        contradictions.append({
                            "type": "opposing_preference",
                            "memory_a": {"id": p["id"], "content": (p["content"] or "")[:80], "valence": p["emotional_valence"]},
                            "memory_b": {"id": n["id"], "content": (n["content"] or "")[:80], "valence": n["emotional_valence"]},
                            "shared_terms": list(shared)[:5],
                            "confidence": min(1.0, len(shared) * 0.3),
                            "positive_keyword": positive,
                            "negative_keyword": negative,
                        })

            if len(contradictions) >= limit * 2:
                break

        # Strategy 2: Category valence inversions
        category_clause = "AND category = ?" if category else ""
        cat_params = [category] if category else []
        cursor.execute(f"""
            SELECT id, content, category, emotional_valence FROM memories
            WHERE emotional_valence > 0.3 {category_clause}{user_filter}
            ORDER BY ABS(emotional_valence) DESC LIMIT ?
        """, cat_params + user_params + [search_limit])
        positive_mems = cursor.fetchall()

        for row in positive_mems:
            mem_cat = row["category"]
            neg_base_params = [mem_cat]
            if user_id:
                neg_base_params.append(user_id)
            user_neg_filter = " AND user_id = ?" if user_id else ""
            cursor.execute(f"""
                SELECT id, content, category, emotional_valence FROM memories
                WHERE category = ? AND emotional_valence < -0.3{user_neg_filter}
                ORDER BY emotional_valence ASC LIMIT 5
            """, neg_base_params)
            negative_mems = cursor.fetchall()

            for neg_row in negative_mems:
                a_words = set(w.lower() for w in (row["content"] or "").split() if len(w) > 4)
                b_words = set(w.lower() for w in (neg_row["content"] or "").split() if len(w) > 4)
                shared = a_words & b_words
                if shared:
                    contradictions.append({
                        "type": "valence_inversion",
                        "memory_a": {"id": row["id"], "content": (row["content"] or "")[:80], "valence": row["emotional_valence"]},
                        "memory_b": {"id": neg_row["id"], "content": (neg_row["content"] or "")[:80], "valence": neg_row["emotional_valence"]},
                        "shared_terms": list(shared)[:5],
                        "confidence": min(1.0, len(shared) * 0.25 + 0.3),
                        "category": mem_cat,
                    })

            if len(contradictions) >= limit * 2:
                break

        # Strategy 3: Conflicting knowledge entries
        cursor.execute("""
            SELECT domain, COUNT(*) as cnt, MIN(confidence) as min_conf,
                    MAX(confidence) as max_conf FROM knowledge
            GROUP BY domain HAVING cnt > 1 AND (max_conf - min_conf) > 0.1
            ORDER BY cnt DESC LIMIT 20
        """)

        for domain_row in cursor.fetchall():
            domain = domain_row["domain"]
            max_conf = domain_row["max_conf"]
            min_conf = domain_row["min_conf"]

            cursor.execute("""
                SELECT id, content, domain, confidence FROM knowledge
                WHERE domain = ? AND confidence = ? ORDER BY RANDOM() LIMIT 3
            """, (domain, max_conf))
            high_rows = cursor.fetchall()

            cursor.execute("""
                SELECT id, content, domain, confidence FROM knowledge
                WHERE domain = ? AND confidence = ? ORDER BY RANDOM() LIMIT 3
            """, (domain, min_conf))
            low_rows = cursor.fetchall()

            for h in high_rows:
                for l in low_rows:
                    if h["id"] == l["id"]:
                        continue
                    h_words = set(w.lower() for w in (h["content"] or "").split() if len(w) > 4)
                    l_words = set(w.lower() for w in (l["content"] or "").split() if len(w) > 4)
                    shared = h_words & l_words
                    if len(shared) >= 2:
                        contradictions.append({
                            "type": "knowledge_conflict",
                            "entry_a": {"id": h["id"], "content": (h["content"] or "")[:80], "confidence": h["confidence"]},
                            "entry_b": {"id": l["id"], "content": (l["content"] or "")[:80], "confidence": l["confidence"]},
                            "domain": domain,
                            "confidence": abs(h["confidence"] - l["confidence"]),
                            "shared_terms": list(shared)[:5],
                        })

            if len(contradictions) >= limit * 2:
                break

        # Deduplicate and rank
        seen_keys = set()
        unique = []
        for c in contradictions:
            key = frozenset(c.get("shared_terms", []) + [c["type"]])
            if key not in seen_keys:
                seen_keys.add(key)
                unique.append(c)

        return sorted(unique, key=lambda x: x.get("confidence", 0), reverse=True)[:limit]

    # ─── Integrity Check & Repair ──────────────────────────────────────────

    def integrity_check(self, repair: bool = False) -> Dict[str, Any]:
        """Check database integrity and optionally repair issues.

        Args:
            repair: If True, fix detected issues automatically

        Returns:
            Dict with check results and repairs made
        """
        return check_integrity(self._get_conn(), repair=repair)

    def repair(self, aggressive: bool = False) -> Dict[str, Any]:
        """Repair the database — fix orphans, inconsistencies, and corruption.

        Args:
            aggressive: If True, also vacuum and deep clean

        Returns:
            Dict with repair statistics
        """
        return repair_database(self._get_conn(), aggressive=aggressive)

    # ─── Backup & Export ──────────────────────────────────────────────────

    def backup_to(self, backup_path: str):
        """Create a backup of the database."""
        return backup_database(self._get_conn(), self.db_path, backup_path)

    def backup_with_rotation(self, backup_dir: Optional[str] = None,
                              max_backups: int = 7) -> str:
        """Create a timestamped backup with rotation."""
        return _backup_with_rotation(self._get_conn(), self.db_path, backup_dir, max_backups)

    def restore_from(self, backup_path: str) -> bool:
        """Restore the database from a backup file.

        After restoration, the thread-local connection is reset so that
        _get_conn() creates a fresh connection to the restored database.
        """
        result = restore_from_backup(self.db_path, backup_path)
        # Reset thread-local connection to avoid stale references
        conn = getattr(self._local, 'conn', None)
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass
            self._local.conn = None
        return result

    def github_backup(self, repo_url: Optional[str] = None, branch: str = "main",
                       commit_msg: str = "auto: Mímir's Well backup",
                       strip_personal: bool = True) -> Dict[str, Any]:
        """Push a sanitized backup to GitHub."""
        return github_backup(
            self.db_path, self._get_conn(),
            repo_url=repo_url, branch=branch,
            commit_msg=commit_msg, strip_personal=strip_personal,
        )

    def export_to_json(self, export_path: str) -> Dict:
        """Export all data to JSON."""
        return export_to_json(self._get_conn(), export_path)

    # ─── FTS Rebuild ─────────────────────────────────────────────────────

    def rebuild_fts(self):
        """Rebuild all FTS5 indexes from source tables.

        With content= (external content) mode, FTS5 automatically
        syncs with the content tables. This method triggers a full rebuild
        to ensure consistency.
        """
        def _rebuild(conn):
            cursor = conn.cursor()
            # For content= mode FTS5, use the rebuild command
            for fts in ["memories_fts", "knowledge_fts", "saga_events_fts"]:
                try:
                    cursor.execute(f"INSERT INTO {fts}({fts}) VALUES('rebuild')")
                except sqlite3.OperationalError:
                    pass  # Table may not exist yet
        self._write(_rebuild)
        logger.info("Mímir: FTS5 indexes rebuilt")

    # ─── Health Check ────────────────────────────────────────────────────

    def health_check(self) -> Dict[str, Any]:
        """Verify database health and connection integrity."""
        result = {"healthy": True, "issues": []}
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM memories")
            result["memory_count"] = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM knowledge")
            result["knowledge_count"] = cursor.fetchone()[0]
        except Exception as e:
            result["healthy"] = False
            result["issues"].append(f"Query failed: {e}")

        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("PRAGMA quick_check")
            integrity = cursor.fetchone()[0]
            if integrity != "ok":
                result["healthy"] = False
                result["issues"].append(f"Integrity: {integrity}")
            result["integrity"] = integrity
        except Exception as e:
            result["issues"].append(f"Integrity check skipped: {e}")

        return result

    # ─── Statistics ──────────────────────────────────────────────────────

    def get_stats(self) -> Dict[str, Any]:
        """Get memory health statistics."""
        import os
        cursor = self._get_conn().cursor()
        stats = {}

        VALID_STAT_TABLES = frozenset({
            "memories", "entities", "relationships", "knowledge",
            "saga_events", "conversations", "memory_access_log",
        })
        for table in VALID_STAT_TABLES:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[table] = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                stats[table] = 0

        # Importance distribution
        cursor.execute("SELECT importance, COUNT(*) FROM memories GROUP BY importance ORDER BY importance")
        stats["importance_distribution"] = {str(row[0]): row[1] for row in cursor.fetchall()}

        # DB size
        try:
            db_size = os.path.getsize(self.db_path)
            stats["db_size_mb"] = round(db_size / (1024 * 1024), 2)
        except OSError:
            stats["db_size_mb"] = 0

        return stats

    # ─── Context Manager ─────────────────────────────────────────────────

    def close(self):
        """Close the database connections (RunaMemory and AuditTrail).

        Note: Only closes the calling thread's connection. Other threads'
        connections will be closed when they next call _get_conn() after
        the object is garbage-collected, or when the process exits.
        """
        # Close audit trail connection
        if hasattr(self, 'audit') and self.audit is not None:
            self.audit.close()
        # Close main memory connection
        conn = getattr(self._local, 'conn', None)
        if conn:
            try:
                conn.close()
            except Exception:
                pass
            self._local.conn = None

    def __repr__(self) -> str:
        """String representation showing DB path and memory count."""
        try:
            conn = self._get_conn()
            count = conn.execute("SELECT COUNT(*) FROM memories WHERE is_current = 1").fetchone()[0]
        except Exception:
            count = '?'
        return f"RunaMemory(db_path='{self.db_path}', memories={count})"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()