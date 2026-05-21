"""
Mímir's Well — Database Schema Definitions
============================================
SQL CREATE statements, indexes, and FTS5 triggers for the memory database.
"""

# Schema version for migration tracking
SCHEMA_VERSION = 9

SCHEMA_META_TABLE = """
CREATE TABLE IF NOT EXISTS _schema_meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
)
"""

# ─── Table creation statements ─────────────────────────────────────────────

MEMORIES_TABLE = """
CREATE TABLE IF NOT EXISTS memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    category TEXT NOT NULL,
    content TEXT NOT NULL,
    tags JSON,
    importance INTEGER DEFAULT 5 CHECK(importance >= 1 AND importance <= 10),
    emotional_valence REAL DEFAULT 0.0 CHECK(emotional_valence >= -1.0 AND emotional_valence <= 1.0),
    valid_from TEXT DEFAULT NULL,
    valid_until TEXT DEFAULT NULL,
    superseded_by INTEGER DEFAULT NULL REFERENCES memories(id),
    is_current INTEGER DEFAULT 1,
    memory_type TEXT DEFAULT 'episodic',
    user_id TEXT DEFAULT 'runa'
)
"""

SAGA_EVENTS_TABLE = """
CREATE TABLE IF NOT EXISTS saga_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    event_type TEXT NOT NULL,
    entity_id TEXT,
    data JSON,
    participants JSON
)
"""

ENTITIES_TABLE = """
CREATE TABLE IF NOT EXISTS entities (
    entity_id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL,
    components JSON,
    state JSON,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
"""

RELATIONSHIPS_TABLE = """
CREATE TABLE IF NOT EXISTS relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_a TEXT NOT NULL,
    entity_b TEXT NOT NULL,
    relationship_type TEXT NOT NULL,
    strength INTEGER DEFAULT 5 CHECK(strength >= 1 AND strength <= 10),
    metadata JSON,
    UNIQUE(entity_a, entity_b, relationship_type)
)
"""

CONVERSATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS conversations (
    session_id TEXT PRIMARY KEY,
    participants JSON,
    transcript TEXT,
    summary TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
"""

KNOWLEDGE_TABLE = """
CREATE TABLE IF NOT EXISTS knowledge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain TEXT NOT NULL,
    content TEXT NOT NULL,
    source TEXT,
    confidence REAL DEFAULT 1.0 CHECK(confidence >= 0.0 AND confidence <= 1.0),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
"""

MEMORY_ACCESS_LOG_TABLE = """
CREATE TABLE IF NOT EXISTS memory_access_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_id INTEGER NOT NULL,
    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_type TEXT DEFAULT 'recall',
    FOREIGN KEY (memory_id) REFERENCES memories(id)
)
"""

# ── T6-1: Wyrd Graph Edge Table ────────────────────────────────────────────

WYRD_EDGES_TABLE = """
CREATE TABLE IF NOT EXISTS wyrd_edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_entity TEXT NOT NULL,
    target_entity TEXT NOT NULL,
    relationship_type TEXT NOT NULL,
    strength REAL DEFAULT 1.0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    metadata TEXT DEFAULT '{}',
    user_id TEXT DEFAULT 'runa',
    UNIQUE(source_entity, target_entity, relationship_type, user_id)
)
"""

# ─── Index creation statements ─────────────────────────────────────────────

INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_memories_category ON memories(category)",
    "CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance)",
    "CREATE INDEX IF NOT EXISTS idx_memories_valence ON memories(emotional_valence)",
    # T5-2: Temporal validity indexes
    "CREATE INDEX IF NOT EXISTS idx_memories_current ON memories(is_current, category, importance DESC)",
    "CREATE INDEX IF NOT EXISTS idx_memories_validity ON memories(valid_from, valid_until)",
    "CREATE INDEX IF NOT EXISTS idx_memories_superseded ON memories(superseded_by)",
    # T5-3: Memory type + category index
    "CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(memory_type, category)",
    "CREATE INDEX IF NOT EXISTS idx_saga_events_type ON saga_events(event_type)",
    "CREATE INDEX IF NOT EXISTS idx_saga_events_entity ON saga_events(entity_id)",
    "CREATE INDEX IF NOT EXISTS idx_knowledge_domain ON knowledge(domain)",
    "CREATE INDEX IF NOT EXISTS idx_access_log_memory ON memory_access_log(memory_id)",
    "CREATE INDEX IF NOT EXISTS idx_access_log_time ON memory_access_log(accessed_at)",
    # T6-1: Wyrd Graph edge indexes
    "CREATE INDEX IF NOT EXISTS idx_wyrd_edges_source ON wyrd_edges(source_entity)",
    "CREATE INDEX IF NOT EXISTS idx_wyrd_edges_target ON wyrd_edges(target_entity)",
    "CREATE INDEX IF NOT EXISTS idx_wyrd_edges_type ON wyrd_edges(relationship_type)",
    "CREATE INDEX IF NOT EXISTS idx_wyrd_edges_strength ON wyrd_edges(strength)",
    # T7-2: Audit trail indexes
    "CREATE INDEX IF NOT EXISTS idx_audit_memory ON memory_audit(memory_id)",
    "CREATE INDEX IF NOT EXISTS idx_audit_source ON memory_audit(source)",
    "CREATE INDEX IF NOT EXISTS idx_audit_action ON memory_audit(action)",
    "CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON memory_audit(timestamp)",
    # T7-3: Per-user namespacing indexes
    "CREATE INDEX IF NOT EXISTS idx_memories_user ON memories(user_id, category)",
    "CREATE INDEX IF NOT EXISTS idx_wyrd_edges_user ON wyrd_edges(user_id)",
    "CREATE INDEX IF NOT EXISTS idx_audit_user ON memory_audit(user_id)",
    # T8-4: Performance indexes for decay JOIN and temporal validity
    "CREATE INDEX IF NOT EXISTS idx_access_log_memory_time ON memory_access_log(memory_id, accessed_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_access_log_recent ON memory_access_log(accessed_at DESC, memory_id)",
    "CREATE INDEX IF NOT EXISTS idx_memories_temporal ON memories(valid_from, valid_until, is_current)",
]

# ─── FTS5 virtual tables ──────────────────────────────────────────────────

FTS_TABLES = [
    """
    CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts
    USING fts5(content, category, tags, content=memories, content_rowid=id)
    """,
    """
    CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts
    USING fts5(content, domain, source, content=knowledge, content_rowid=id)
    """,
    """
    CREATE VIRTUAL TABLE IF NOT EXISTS saga_events_fts
    USING fts5(event_type, entity_id, content=saga_events, content_rowid=id)
    """,
]

# ─── FTS sync ──────────────────────────────────────────────────────────────
# With content=external mode, FTS5 auto-syncs on INSERT, UPDATE, and DELETE.
# No triggers are needed — SQLite handles it all internally.
# ─── SQLite PRAGMAs ────────────────────────────────────────────────────────

PRAGMAS = [
    "PRAGMA foreign_keys = ON",
    "PRAGMA journal_mode = WAL",
    "PRAGMA busy_timeout = 10000",
    "PRAGMA synchronous = FULL",
    "PRAGMA wal_autocheckpoint = 1000",
    "PRAGMA mmap_size = 0",
]

# ─── All table SQL aggregated for convenience ──────────────────────────────

# ── Memory Audit Trail (T7-2) ────────────────────────────────────────────

MEMORY_AUDIT_TABLE = """
CREATE TABLE IF NOT EXISTS memory_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    source TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    timestamp TEXT DEFAULT (datetime('now')),
    metadata TEXT DEFAULT '{}',
    user_id TEXT DEFAULT 'runa'
);
"""

MEMORY_AUDIT_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_audit_memory ON memory_audit(memory_id)",
    "CREATE INDEX IF NOT EXISTS idx_audit_source ON memory_audit(source)",
    "CREATE INDEX IF NOT EXISTS idx_audit_action ON memory_audit(action)",
    "CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON memory_audit(timestamp)",
]

ALL_TABLES = [
    SCHEMA_META_TABLE,
    MEMORIES_TABLE,
    SAGA_EVENTS_TABLE,
    ENTITIES_TABLE,
    RELATIONSHIPS_TABLE,
    CONVERSATIONS_TABLE,
    KNOWLEDGE_TABLE,
    MEMORY_ACCESS_LOG_TABLE,
    WYRD_EDGES_TABLE,
    MEMORY_AUDIT_TABLE,
]