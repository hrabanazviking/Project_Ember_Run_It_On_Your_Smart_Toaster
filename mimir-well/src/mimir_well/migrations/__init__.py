"""
Mímir's Well — Schema Migrations
==================================
Each migration is an independent module with UP and DOWN SQL.
Run sequentially to evolve the database schema from version N to N+1.

ᛗ í ᛗ í ᚱ — The Well remembers what was, even as it becomes.
"""

MIGRATIONS = []  # Populated by individual migration modules


def register_migration(version: int, up_sql: str, down_sql: str, description: str = ""):
    """Register a migration in the ordered sequence."""
    MIGRATIONS.append({
        "version": version,
        "up_sql": up_sql,
        "down_sql": down_sql,
        "description": description,
    })


# ── Migration 002: Temporal Validity ─────────────────────────────────

MIGRATION_002_UP = """
-- Add temporal validity fields to memories table
-- Enables time-bounded facts and automatic supersession tracking

ALTER TABLE memories ADD COLUMN valid_from TEXT DEFAULT NULL;
ALTER TABLE memories ADD COLUMN valid_until TEXT DEFAULT NULL;
ALTER TABLE memories ADD COLUMN superseded_by INTEGER DEFAULT NULL
    REFERENCES memories(id);
ALTER TABLE memories ADD COLUMN is_current INTEGER DEFAULT 1;

-- Fast filter for currently-valid memories
CREATE INDEX IF NOT EXISTS idx_memories_current
    ON memories(is_current, category, importance DESC);

-- Temporal range queries (valid_from/valid_until)
CREATE INDEX IF NOT EXISTS idx_memories_validity
    ON memories(valid_from, valid_until);

-- Supersession chain lookups
CREATE INDEX IF NOT EXISTS idx_memories_superseded
    ON memories(superseded_by);
"""

MIGRATION_002_DOWN = """
-- Remove temporal validity fields (rarely needed — this is destructive)

DROP INDEX IF EXISTS idx_memories_superseded;
DROP INDEX IF EXISTS idx_memories_validity;
DROP INDEX IF EXISTS idx_memories_current;

ALTER TABLE memories DROP COLUMN valid_from;
ALTER TABLE memories DROP COLUMN valid_until;
ALTER TABLE memories DROP COLUMN superseded_by;
ALTER TABLE memories DROP COLUMN is_current;
"""

register_migration(
    version=2,
    up_sql=MIGRATION_002_UP,
    down_sql=MIGRATION_002_DOWN,
    description="Add temporal validity (valid_from, valid_until, superseded_by, is_current) to memories",
)


# ── Migration 003: Memory Types ────────────────────────────────────────

MIGRATION_003_UP = """
-- Add memory type classification column
-- Values: 'episodic' (specific events), 'semantic' (general facts),
--          'procedural' (learned patterns/skills), 'implicit' (behavioral patterns)
ALTER TABLE memories ADD COLUMN memory_type TEXT DEFAULT 'episodic';

-- Index for type-filtered queries (used by TokenBudgeter per-type strategies)
CREATE INDEX IF NOT EXISTS idx_memories_type
    ON memories(memory_type, category);
"""

MIGRATION_003_DOWN = """
-- Remove memory type classification

DROP INDEX IF EXISTS idx_memories_type;
ALTER TABLE memories DROP COLUMN memory_type;
"""

register_migration(
    version=3,
    up_sql=MIGRATION_003_UP,
    down_sql=MIGRATION_003_DOWN,
    description="Add memory_type column (episodic, semantic, procedural, implicit) with type+category index",
)


# ── Migration 004: Wyrd Graph Edge Layer ──────────────────────────────

MIGRATION_004_UP = """
-- Wyrd Graph: Directed edges between entities
-- Enables multi-hop relationship traversal (BFS from any entity)
-- Note: user_id column is added by migration 007, so we exclude it
-- from the UNIQUE constraint here for upgrade compatibility.
CREATE TABLE IF NOT EXISTS wyrd_edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_entity TEXT NOT NULL,
    target_entity TEXT NOT NULL,
    relationship_type TEXT NOT NULL,
    strength REAL DEFAULT 1.0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    metadata TEXT DEFAULT '{}',
    UNIQUE(source_entity, target_entity, relationship_type)
);

-- Fast neighbor lookups
CREATE INDEX IF NOT EXISTS idx_wyrd_edges_source ON wyrd_edges(source_entity);
CREATE INDEX IF NOT EXISTS idx_wyrd_edges_target ON wyrd_edges(target_entity);
CREATE INDEX IF NOT EXISTS idx_wyrd_edges_type ON wyrd_edges(relationship_type);
CREATE INDEX IF NOT EXISTS idx_wyrd_edges_strength ON wyrd_edges(strength);
"""

MIGRATION_004_DOWN = """
-- Remove Wyrd Graph edge table and indexes
DROP INDEX IF EXISTS idx_wyrd_edges_strength;
DROP INDEX IF EXISTS idx_wyrd_edges_type;
DROP INDEX IF EXISTS idx_wyrd_edges_target;
DROP INDEX IF EXISTS idx_wyrd_edges_source;
DROP TABLE IF EXISTS wyrd_edges;
"""

# Note: Variable name MIGRATION_004 but version=5 because migration 004
# corresponds to schema version 5 (migrations advance the schema version
# by the version number they register). This is intentional but confusing.
register_migration(
    version=5,
    up_sql=MIGRATION_004_UP,
    down_sql=MIGRATION_004_DOWN,
    description="Add wyrd_edges table for multi-hop relationship graph traversal",
)


# ── Migration 006: Memory Audit Trail ─────────────────────────────────

MIGRATION_006_UP = """
-- Memory Audit Trail: Log every memory write/update/delete for traceability
-- Every action against the Well is witnessed and recorded.
CREATE TABLE IF NOT EXISTS memory_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_id INTEGER NOT NULL,
    action TEXT NOT NULL,           -- 'store', 'update', 'delete', 'supersede', 'compress'
    source TEXT NOT NULL,           -- 'hermes', 'runa_remember', 'eir', 'nse', 'wyrd'
    content_hash TEXT NOT NULL,     -- SHA-256 (first 16 chars) of content at time of action
    timestamp TEXT DEFAULT (datetime('now')),
    metadata TEXT DEFAULT '{}'      -- JSON: importance, category, trust_level, guard_result, etc.
);

-- Fast lookups: by memory, by source, by action type, by time range
CREATE INDEX IF NOT EXISTS idx_audit_memory ON memory_audit(memory_id);
CREATE INDEX IF NOT EXISTS idx_audit_source ON memory_audit(source);
CREATE INDEX IF NOT EXISTS idx_audit_action ON memory_audit(action);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON memory_audit(timestamp);
"""

MIGRATION_006_DOWN = """
-- Remove Memory Audit Trail
DROP INDEX IF EXISTS idx_audit_timestamp;
DROP INDEX IF EXISTS idx_audit_action;
DROP INDEX IF EXISTS idx_audit_source;
DROP INDEX IF EXISTS idx_audit_memory;
DROP TABLE IF EXISTS memory_audit;
"""

register_migration(
    version=6,
    up_sql=MIGRATION_006_UP,
    down_sql=MIGRATION_006_DOWN,
    description="Add memory_audit table for write/update/delete traceability",
)


# ── Migration 007: Per-User Memory Namespacing ────────────────────────────

MIGRATION_007_UP = """
-- Per-User Memory Namespacing: Add user_id to all memory tables
-- Enables future multi-tenant isolation (runa, volmarr, shared)
-- All existing memories default to user_id='runa'

ALTER TABLE memories ADD COLUMN user_id TEXT DEFAULT 'runa';
ALTER TABLE memory_audit ADD COLUMN user_id TEXT DEFAULT 'runa';

-- wyrd_edges needs table recreation to update UNIQUE constraint
-- Step 1: Add user_id column
ALTER TABLE wyrd_edges ADD COLUMN user_id TEXT DEFAULT 'runa';

-- Step 2: Recreate wyrd_edges with updated UNIQUE constraint (includes user_id)
CREATE TABLE wyrd_edges_new (
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
);
INSERT INTO wyrd_edges_new (id, source_entity, target_entity, relationship_type, strength, created_at, updated_at, metadata, user_id)
    SELECT id, source_entity, target_entity, relationship_type, strength, created_at, updated_at, metadata, user_id FROM wyrd_edges;
DROP TABLE wyrd_edges;
ALTER TABLE wyrd_edges_new RENAME TO wyrd_edges;

-- Fast filter by user
CREATE INDEX IF NOT EXISTS idx_memories_user ON memories(user_id, category);
CREATE INDEX IF NOT EXISTS idx_wyrd_edges_user ON wyrd_edges(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_user ON memory_audit(user_id);
"""

MIGRATION_007_DOWN = """
-- Remove per-user namespacing

DROP INDEX IF EXISTS idx_audit_user;
DROP INDEX IF EXISTS idx_wyrd_edges_user;
DROP INDEX IF EXISTS idx_memories_user;

ALTER TABLE memory_audit DROP COLUMN user_id;
ALTER TABLE wyrd_edges DROP COLUMN user_id;
ALTER TABLE memories DROP COLUMN user_id;
"""

register_migration(
    version=7,
    up_sql=MIGRATION_007_UP,
    down_sql=MIGRATION_007_DOWN,
    description="Add user_id column to memories, wyrd_edges, and memory_audit for multi-tenant namespacing",
)

# ── Migration 008: Performance Indexes ────────────────────────────────────

MIGRATION_008_UP = """
-- Composite index for decay() N+1 fix: JOIN on memory_id + MAX(accessed_at)
CREATE INDEX IF NOT EXISTS idx_access_log_memory_time
    ON memory_access_log(memory_id, accessed_at DESC);

-- Covering index for decay reinforcement: recent access by time
CREATE INDEX IF NOT EXISTS idx_access_log_recent
    ON memory_access_log(accessed_at DESC, memory_id);

-- Index for temporal validity queries
CREATE INDEX IF NOT EXISTS idx_memories_temporal
    ON memories(valid_from, valid_until, is_current);
"""

MIGRATION_008_DOWN = """
DROP INDEX IF EXISTS idx_memories_temporal;
DROP INDEX IF NOT EXISTS idx_access_log_recent;
DROP INDEX IF NOT EXISTS idx_access_log_memory_time;
"""

register_migration(
    version=8,
    up_sql=MIGRATION_008_UP,
    down_sql=MIGRATION_008_DOWN,
    description="Performance indexes for decay JOIN, recent access, and temporal validity queries",
)

# ── Migration 009: T9-4 Composite Indexes ──────────────────────────────

MIGRATION_009_UP = """
-- WyrdGraph traversal: batch BFS queries filter by source_entity + relationship_type
CREATE INDEX IF NOT EXISTS idx_wyrd_edges_source_type
    ON wyrd_edges(source_entity, relationship_type, strength DESC);

-- WyrdGraph reverse traversal: incoming edges by target
CREATE INDEX IF NOT EXISTS idx_wyrd_edges_target
    ON wyrd_edges(target_entity, strength DESC);

-- promote_to_knowledge: batch check content uniqueness by category
CREATE INDEX IF NOT EXISTS idx_knowledge_domain_content
    ON knowledge(domain, content);

-- detect_contradictions: LIKE queries with emotional valence filter
CREATE INDEX IF NOT EXISTS idx_memories_valence
    ON memories(emotional_valence, category, importance DESC);

-- FTS content sync: fast joins on memory_id
CREATE INDEX IF NOT EXISTS idx_saga_events_character
    ON saga_events(character_id, timestamp DESC);
"""

MIGRATION_009_DOWN = """
DROP INDEX IF EXISTS idx_saga_events_character;
DROP INDEX IF EXISTS idx_memories_valence;
DROP INDEX IF EXISTS idx_knowledge_domain_content;
DROP INDEX IF EXISTS idx_wyrd_edges_target;
DROP INDEX IF EXISTS idx_wyrd_edges_source_type;
"""

register_migration(
    version=9,
    up_sql=MIGRATION_009_UP,
    down_sql=MIGRATION_009_DOWN,
    description="T9-4: Composite indexes for WyrdGraph traversal, promotion, contradictions, and saga events",
)