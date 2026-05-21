# Mímir Well v2.9.0 — Data Flow & Architecture Map

> *"Most confusion begins when people stop seeing the whole map."*
> — Védis Eikleið, Cartographer

---

## 1. File Inventory

### Source Files (`src/mimir_well/`)

| File | Lines | Purpose |
|------|-------|---------|
| `core.py` | 1481 | Central RunaMemory class — all CRUD, recall, decay, consolidation, FTS, entities, knowledge, saga, conversations, backup/restore delegates |
| `budget.py` | 485 | TokenBudget dataclass, TokenBudgeter selector, MemoryChannel/BudgetPriority enums, per-channel selection strategies |
| `wyrd_graph.py` | 618 | WyrdGraph — knowledge-graph edge layer (add/remove/traverse/neighborhood/merge) |
| `guard.py` | 525 | MemoryGuard — trust-level input validation, injection pattern detection, content sanitization |
| `audit.py` | 345 | AuditTrail — append-only write log with content hashing, query/timeline/stats |
| `schema.py` | 222 | DDL constants — all CREATE TABLE, CREATE INDEX, FTS5 virtual table SQL |
| `config.py` | 111 | MimirConfig — JSON config file loader with env var overrides |
| `decay.py` | 114 | Pure functions: compute_ebbinghaus_decay, compute_reinforcement_boost, compute_confidence_for_promotion, should_decay, should_promote |
| `repair.py` | 236 | Database integrity checking (check_integrity) and repair (repair_database) |
| `backup.py` | 329 | backup_database, backup_with_rotation, restore_from_backup, export_to_json, github_backup |
| `context_engineer.py` | 316 | ContextEngineer — assembles memory context for LLM injection using WyrdGraph + TokenBudgeter |
| `__init__.py` | 96 | Package exports, version string (v2.8.0), `__all__` |
| `migrations/__init__.py` | 260 | Migration registry — MIGRATIONS dict with versions 002–008 |
| `migrations/runner.py` | 152 | run_migrations, rollback_migration, get_schema_version |

**Total source lines: ~4,883**

### Test Files (`tests/`)

| File | Lines | Purpose |
|------|-------|---------|
| `__init__.py` | 0 | Empty package marker |
| `test_core.py` | 210 | Core CRUD, search, recall, entities, knowledge, conversations, backup/restore, health check |
| `test_decay.py` | 150 | Ebbinghaus decay math, reinforcement, should_decay/should_promote, integration decay/consolidate |
| `test_audit_trail.py` | 121 | Audit trail — store/update/delete logging, query by action/source/memory_id, timeline, stats, integrity |
| `test_guard_trust.py` | 180 | Trust-level validation — FRITH/ALLY/NEUTRAL/STRANGER length limits, pattern filtering, HTML sanitization |
| `test_repair.py` | 153 | Integrity checking — orphan detection, empty content, out-of-range values, repair |
| `test_backup.py` | 144 | Backup creation, SQLite validity, rotation, JSON export |
| `test_namespacing.py` | 210 | Per-user namespacing — user_id isolation across add/get/update/delete/FTS/recall/consolidate |
| `test_recall_quality.py` | 378 | Precision@K, latency benchmarks, superseded exclusion, temporal validity, token budget selection |
| `test_t8_1a_delete_audit.py` | 123 | delete_memory audit trail propagates user_id correctly |
| `test_t8_1b_update_delete_isolation.py` | 154 | update_memory/delete_memory respect user_id isolation |
| `test_t8_1c_supersede_isolation.py` | 117 | supersede() respects user_id — cross-user blocked |
| `test_t8_1d_store_with_validity.py` | 115 | store_with_validity propagates user_id and source |
| `test_t8_1e_get_memory_isolation.py` | 129 | get_memory() user_id filtering |
| `test_t8_2_read_isolation.py` | 219 | fts_search, recall_by_importance, recall_recent, recall_by_mood, consolidate, promote, contradictions — all user-isolated |
| `test_t8_3_wyrd_graph_isolation.py` | 165 | WyrdGraph edge/entity/type isolation by user_id |
| `test_t8_4_performance.py` | 186 | Decay JOIN (no N+1), user-isolated decay, 'hecedure' typo fix, migration 008 indexes, performance benchmark |
| `test_t8_5_architecture.py` | 229 | AuditTrail thread-local reuse, close(), multi-threaded, stats(user_id), AuditEntry.to_dict(), type hints |
| `test_t8_6_coverage.py` | 603 | Coverage for: add_entity, get_entity, get_entities_by_type, set_relationship, get_relationship_strength, add_saga_event, add_knowledge, search_knowledge, save/get_conversation, log_access, get_stats, health_check, integrity_check, repair, rebuild_fts, backup_to, restore_from, backup_with_rotation, export_to_json, WyrdGraph stats, merge_from_fact_store, github_backup |

**Total test lines: ~3,997**

---

## 2. Class Map

### `core.py` — `RunaMemory`

```
class RunaMemory:
    __init__(self, db_path: Optional[str] = None, config: Optional[MimirConfig] = None)
    _get_conn(self) -> sqlite3.Connection
    _write(self, fn: Callable) -> Any
    _commit(self) -> None
    _init_db(self) -> None

    # ── Memory CRUD ──
    add_memory(self, content: str, category: str = "general",
               importance: int = 5, emotional_valence: float = 0.0,
               tags: Optional[List[str]] = None, source: str = "mimir",
               user_id: str = "runa", memory_type: Optional[str] = None,
               entities: Optional[List[str]] = None) -> int
    get_memory(self, memory_id: int, user_id: Optional[str] = None) -> Optional[Dict]
    update_memory(self, memory_id: int, source: str = "unknown",
                  content: Optional[str] = None, importance: Optional[int] = None,
                  category: Optional[str] = None, emotional_valence: Optional[float] = None,
                  tags: Optional[List[str]] = None, user_id: Optional[str] = None) -> bool
    delete_memory(self, memory_id: int, source: str = "unknown",
                  user_id: Optional[str] = None) -> bool
    supersede(self, old_memory_id: int, new_content: str,
              importance: Optional[int] = None, category: Optional[str] = None,
              user_id: Optional[str] = None) -> int

    # ── Recall & Search ──
    search_memories(self, query: str, category: Optional[str] = None,
                    limit: int = 20, user_id: Optional[str] = None) -> List[Dict]
    fts_search(self, table: str, query: str, limit: int = 20,
               user_id: Optional[str] = None) -> List[Dict]
    recall_by_importance(self, min_importance: int = 7, limit: int = 20,
                        user_id: Optional[str] = None) -> List[Dict]
    recall_recent(self, hours: int = 24, limit: int = 5,
                  user_id: Optional[str] = None) -> List[Dict]
    recall_by_mood(self, target_valence: float = 0.0, tolerance: float = 0.3,
                   limit: int = 10, user_id: Optional[str] = None) -> List[Dict]
    recall_current(self, category: Optional[str] = None, min_importance: int = 3,
                   limit: int = 20, user_id: Optional[str] = None) -> List[Dict]
    store_with_validity(self, content: str, category: str = "general",
                       importance: int = 5, valid_from: Optional[str] = None,
                       valid_until: Optional[str] = None, source: str = "temporal",
                       user_id: str = "runa", **kwargs) -> int

    # ── Entities & Relationships ──
    add_entity(self, entity_id: str, entity_type: str,
               components: Optional[Dict] = None, state: Optional[Dict] = None) -> bool
    get_entity(self, entity_id: str) -> Optional[Dict]
    get_entities_by_type(self, entity_type: str) -> List[Dict]
    set_relationship(self, entity_a: str, entity_b: str,
                    relationship_type: str, strength: int = 5) -> Optional[Dict]
    get_relationship_strength(self, entity_a: str, entity_b: str) -> Optional[int]

    # ── Knowledge ──
    add_knowledge(self, domain: str, content: str, confidence: float = 1.0,
                  source: Optional[str] = None) -> int
    search_knowledge(self, domain: str, query: str, limit: int = 20) -> List[Dict]

    # ── Saga & Conversation ──
    add_saga_event(self, event_type: str, entity_id: Optional[str] = None,
                   data: Optional[Dict] = None, participants: Optional[List] = None) -> int
    save_conversation(self, session_id: str, participants: List[str],
                      transcript: str = "", summary: str = "") -> None
    get_conversation(self, session_id: str) -> Optional[Dict]

    # ── Decay & Consolidation ──
    _log_access(self, memory_id: int, access_type: str = "recall") -> None
    log_access(self, memory_id: int, access_type: str = "recall") -> None
    decay(self, half_life_days: float = 30.0, min_importance: int = 1,
          user_id: Optional[str] = None) -> Dict[str, int]
    consolidate(self, user_id: Optional[str] = None) -> Dict[str, int]
    promote_to_knowledge(self, min_importance: int = 8,
                        confidence_threshold: float = 0.8,
                        user_id: Optional[str] = None) -> Dict[str, int]
    detect_contradictions(self, category: Optional[str] = None,
                          user_id: Optional[str] = None) -> List[Dict]

    # ── Maintenance ──
    rebuild_fts(self) -> None
    integrity_check(self, repair: bool = False) -> Dict[str, Any]
    repair(self, aggressive: bool = False) -> Dict[str, Any]
    health_check(self) -> Dict[str, Any]
    get_stats(self) -> Dict[str, Any]

    # ── Backup ──
    backup_to(self, backup_path: str) -> str
    backup_with_rotation(self, backup_dir: Optional[str] = None,
                        max_backups: int = 7) -> str
    restore_from(self, backup_path: str) -> bool
    github_backup(self, repo_url: Optional[str] = None, branch: str = "main",
                  strip_personal: bool = True) -> Dict[str, Any]
    export_to_json(self, export_path: str) -> Dict

    # ── Lifecycle ──
    close(self) -> None
    __enter__(self) -> "RunaMemory"
    __exit__(self, exc_type, exc_val, exc_tb) -> None
    __del__(self) -> None
```

### `audit.py` — `AuditAction`, `AuditEntry`, `AuditTrail`

```
class AuditAction:
    STORE = "store"
    UPDATE = "update"
    DELETE = "delete"
    SUPERSEDE = "supersede"
    DECAY = "decay"
    PROMOTE = "promote"

class AuditEntry:
    __init__(self, id, memory_id, action, source, content_hash, timestamp, metadata, user_id)
    to_dict(self) -> Dict[str, Any]

class AuditTrail:
    __init__(self, db_path: str) -> None
    _get_conn(self) -> sqlite3.Connection
    _commit(self) -> None
    close(self) -> None
    log(self, memory_id: int, action: str, source: str,
        content_hash: str = "", metadata: Dict = None,
        user_id: str = "runa") -> int
    query(self, memory_id: Optional[int] = None,
           action: Optional[str] = None, source: Optional[str] = None,
           user_id: Optional[str] = None, limit: int = 100) -> List[AuditEntry]
    timeline(self, memory_id: int, limit: int = 50) -> List[AuditEntry]
    stats(self, user_id: Optional[str] = None) -> Dict[str, Any]
    verify_integrity(self, memory_id: int, current_hash: str) -> Dict[str, Any]
```

### `budget.py` — `BudgetPriority`, `MemoryChannel`, `TokenBudget`, `TokenBudgeter`

```
class BudgetPriority(Enum):
    REQUIRED = "required"
    PREFERRED = "preferred"
    OPTIONAL = "optional"

class MemoryChannel(Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    IMPLICIT = "implicit"
    HEURISTIC = "heuristic"

class TokenBudget:
    __init__(self, total_context: int = 128000,
              episodic_pct: float = 0.35,
              semantic_pct: float = 0.25,
              procedural_pct: float = 0.15,
              implicit_pct: float = 0.10,
              heuristic_pct: float = 0.15)
    compute(self) -> Dict[str, int]
    for_model(cls, model_name: str) -> "TokenBudget"

class TokenBudgeter:
    __init__(self, budget: TokenBudget)
    _estimate_tokens(self, text: str) -> int
    select_memories(self, candidates: List[Dict], channel: str,
                    user_id: Optional[str] = None) -> List[Dict]
    budget_all(self, candidates: List[Dict]) -> Dict[str, List[Dict]]
    format_for_injection(self, partitioned: Dict[str, List[Dict]],
                         max_tokens: Optional[int] = None) -> str
    get_budget_summary(self) -> Dict[str, Any]

def infer_channel(category: str) -> MemoryChannel
def _episodic_strategy(candidates) -> List[Dict]
def _semantic_strategy(candidates) -> List[Dict]
def _procedural_strategy(candidates) -> List[Dict]
def _implicit_strategy(candidates) -> List[Dict]
def _default_strategy(candidates) -> List[Dict]
```

### `wyrd_graph.py` — `WyrdGraph`

```
class WyrdGraph:
    __init__(self, db_path: str)
    close(self) -> None
    __enter__(self) -> "WyrdGraph"
    __exit__(self, *args) -> None
    add_edge(self, source: str, target: str, relationship_type: str,
             strength: float = 1.0, metadata: Optional[Dict] = None,
             user_id: str = "runa") -> int
    remove_edge(self, source: str, target: str, relationship_type: str,
                 user_id: Optional[str] = None) -> bool
    get_edge(self, source: str, target: str, relationship_type: str,
             user_id: Optional[str] = None) -> Optional[Dict]
    get_edges_from(self, entity: str, relationship_type: Optional[str] = None,
                   user_id: Optional[str] = None, limit: int = 100) -> List[Dict]
    get_edges_to(self, entity: str, relationship_type: Optional[str] = None,
                 user_id: Optional[str] = None, limit: int = 100) -> List[Dict]
    traverse(self, start: str, max_depth: int = 2,
             relationship_type: Optional[str] = None,
             user_id: Optional[str] = None) -> List[Dict]
    _get_incoming(self, entity: str, relationship_type: Optional[str] = None,
                  user_id: Optional[str] = None, limit: int = 100) -> List[Dict]
    get_related(self, entity: str, max_depth: int = 2,
                relationship_type: Optional[str] = None,
                user_id: Optional[str] = None) -> Dict[str, List[Dict]]
    edge_count(self, user_id: Optional[str] = None) -> int
    entity_count(self, user_id: Optional[str] = None) -> int
    relationship_types(self, user_id: Optional[str] = None) -> List[str]
    merge_from_fact_store(self, fact_store_path: str) -> Dict[str, int]
```

### `guard.py` — `TrustLevel`, `GuardSeverity`, `GuardResult`, `PatternSeverity`, `MemoryGuard`

```
class TrustLevel(IntEnum):
    FRITH = 10      # Inner circle: volmarr, runa, hermes, mimir, eir
    ALLY = 7        # Trusted tools: nse
    NEUTRAL = 5     # API calls
    STRANGER = 1    # Unknown sources

class GuardSeverity(Enum):
    TRUSTED_ALLOW = "trusted_allow"
    WARNING = "warning"
    BLOCKED = "blocked"

class GuardResult:
    __init__(self, is_valid: bool, reason: str = "",
              severity: GuardSeverity = GuardSeverity.TRUSTED_ALLOW,
              sanitized: Optional[str] = None)

class PatternSeverity(Enum):
    CRITICAL = "critical"    # null bytes, SQL injection
    HIGH = "high"            # jailbreak, roleplay override
    MEDIUM = "medium"        # "ignore instructions"
    LOW = "low"              # pretend/roleplay

class MemoryGuard:
    __init__(self, strict: bool = False)
    _resolve_trust(self, source: str, trust: Optional[int] = None) -> TrustLevel
    _should_block(self, pattern_severity, trust_level) -> bool
    compute_hash(self, content: str) -> str
    validate_content(self, content: str, source: str = "unknown",
                     trust: Optional[int] = None) -> GuardResult
    sanitize_content(self, content: str) -> str
    validate_write(self, content: str, category: str = "general",
                   importance: int = 5, source: str = "unknown",
                   trust: Optional[int] = None) -> GuardResult
```

### `context_engineer.py` — `ContextResult`, `ContextEngineer`

```
class ContextResult:
    __init__(self, memories: List[Dict], entities: List[str] = None,
              relationships: List[Dict] = None)
    to_context_block(self) -> str

class ContextEngineer:
    __init__(self, memory: RunaMemory, graph: WyrdGraph = None,
              budget: TokenBudget = None)
    _estimate_tokens(self, text: str) -> int
    _extract_entities(self, text: str) -> List[str]
    assemble_context(self, user_message: str, category: Optional[str] = None,
                     min_importance: int = 5, max_tokens: Optional[int] = None,
                     user_id: Optional[str] = None) -> ContextResult
    quick_context(self, user_message: str) -> str
```

### `config.py` — `MimirConfig`

```
class MimirConfig:
    __init__(self, config_path: Optional[str] = None)
    _default_config_path() -> Path                           # @staticmethod
    _load(self) -> None
    get(self, key: str, default: Any = None) -> Any
    set(self, key: str, value: Any) -> None
    _save(self) -> None
    db_path -> Path                                          # @property
    backup_dir -> Path                                       # @property
    to_dict(self) -> Dict[str, Any]
```

### `decay.py` — Standalone Functions

```
compute_ebbinghaus_decay(importance: float, days_since_access: float,
                         half_life_days: float = 30.0) -> float
compute_reinforcement_boost(current_importance: float, accesses_in_window: int,
                             boost: float = 0.5) -> float
compute_confidence_for_promotion(importance: float, valence: float = 0.0) -> float
should_decay(days_since_access: int, importance: int, threshold_days: int = 30) -> bool
should_promote(importance: int, access_count: int,
               access_window_days: int = 7, min_importance: int = 8) -> bool
```

### `repair.py` — Standalone Functions

```
validate_backup(backup_path: str) -> bool
check_integrity(conn: sqlite3.Connection, repair: bool = False) -> Dict[str, Any]
repair_database(conn: sqlite3.Connection, aggressive: bool = False) -> Dict[str, Any]
```

### `backup.py` — Standalone Functions

```
backup_database(conn: sqlite3.Connection, db_path: Path, backup_path: str) -> str
backup_with_rotation(conn: sqlite3.Connection, db_path: Path,
                     backup_dir: Optional[str] = None, max_backups: int = 7) -> str
restore_from_backup(db_path: Path, backup_path: str,
                    conn_ref: Optional[sqlite3.Connection] = None) -> bool
export_to_json(conn: sqlite3.Connection, export_path: str,
               include_access_log: bool = False) -> Dict
github_backup(db_path: Path, conn: sqlite3.Connection,
              repo_url: Optional[str] = None, branch: str = "main",
              commit_msg: str = ..., strip_personal: bool = True,
              config_path: Optional[Path] = None) -> Dict[str, Any]
_validate_backup_file(backup: Path) -> bool                   # private
```

### `schema.py` — Constants

```
SCHEMA_VERSION = 7
SCHEMA_META_TABLE, MEMORIES_TABLE, SAGA_EVENTS_TABLE, ENTITIES_TABLE,
RELATIONSHIPS_TABLE, CONVERSATIONS_TABLE, KNOWLEDGE_TABLE,
MEMORY_ACCESS_LOG_TABLE, WYRD_EDGES_TABLE, MEMORY_AUDIT_TABLE
INDEXES: List[str] (23 indexes)
FTS_TABLES: List[str] (memories_fts, knowledge_fts, saga_events_fts)
FTS_TRIGGERS: List[str] (empty — content= mode auto-syncs)
PRAGMAS: List[str] (5 pragmas)
ALL_TABLES: List[str] (all CREATE TABLE SQL)
MEMORY_AUDIT_INDEXES: List[str] (4 audit indexes)
```

### `migrations/__init__.py` — `register_migration()`, `MIGRATIONS`

```
MIGRATIONS = {
    2:  "T5-2: Temporal validity (valid_from, valid_until columns)",
    3:  "T5-3: Memory types (memory_type column, type_category index)",
    4:  "T6-1: Wyrd edges (wyrd_edges table, edge indexes)",
    5:  "T7-1: Memory Guard schema-ready (categories check)",
    6:  "T7-2: Memory Audit Trail (memory_audit table)",
    7:  "T7-3: Per-user namespacing (user_id columns on memories, wyrd_edges, memory_audit)",
    8:  "T8-4: Performance indexes (join optimization, temporal validity, recent access)",
}
register_migration(version, up_sql, down_sql, description)
```

### `migrations/runner.py`

```
get_schema_version(conn: sqlite3.Connection) -> int
run_migrations(conn: sqlite3.Connection, target_version: int = None) -> List[int]
rollback_migration(conn: sqlite3.Connection, version: int) -> bool
```

---

## 3. Data Flow Map

### 3a. Memory Write Path: `add_memory()` → DB → FTS → Audit

```
User/API
  │
  ▼
add_memory(content, category, importance, emotional_valence,
           tags, source, user_id, memory_type, entities)
  │
  ├─→ MemoryGuard.validate_write(content, category, importance, source, trust)
  │     ├── validate_content() → GuardSeverity check against trust level
  │     │     ├── _resolve_trust(source, trust) → TrustLevel (FRITH/ALLY/NEUTRAL/STRANGER)
  │     │     ├── Pattern matching (CRITICAL/HIGH/MEDIUM/LOW severity)
  │     │     ├── Length check (FRITH: 100K, ALLY: 50K, NEUTRAL: 10K, STRANGER: 5K)
  │     │     └── Return: GuardResult(is_valid, reason, severity, sanitized)
  │     └── If is_valid=False → return -1 (write blocked)
  │
  ├─→ sanitize_content(content) → strip HTML tags, null bytes
  │
  ├─→ infer_memory_type(category) → memory_type string
  │
  ├─→ _write(lambda conn: conn.execute(INSERT INTO memories ...))
  │     ├── self.conn.execute(INSERT)  →  memories table
  │     ├── self.conn.execute(INSERT)  →  memory_access_log (initial access)
  │     └── self._commit()
  │
  │    ┌─────────────────────────────────────────────────────┐
  │    │  memories table columns:                          │
  │    │  id, timestamp, category, content, tags (JSON),   │
  │    │  importance (1-10 CHECK), emotional_valence       │
  │    │  (-1.0 to 1.0 CHECK), valid_from, valid_until,   │
  │    │  superseded_by (FK→memories.id), is_current,      │
  │    │  memory_type, user_id (DEFAULT 'runa')            │
  │    └─────────────────────────────────────────────────────┘
  │
  ├─→ AuditTrail.log(memory_id, STORE, source, content_hash, metadata, user_id)
  │     └── INSERT INTO memory_audit (id, memory_id, action, source,
  │           content_hash, timestamp, metadata, user_id)
  │
  └─→ Return: memory_id (int) or -1 (blocked)
```

### 3b. Memory Recall Path: `recall_by_importance()` / `fts_search()` → Scoring → Results

```
User/API
  │
  ▼
recall_by_importance(min_importance=7, limit=20, user_id=None)
  │
  ├─→ SELECT * FROM memories WHERE importance >= ? AND is_current = 1
  │     [AND user_id = ?] ORDER BY importance DESC, timestamp DESC LIMIT ?
  │
  ├─→ For each result: _log_access(memory_id, "recall")
  │     └── INSERT INTO memory_access_log (memory_id, accessed_at, access_type)
  │
  └─→ Return: List[Dict] (row dicts with all columns)

─────────────────────────────────────────────────────────

fts_search(table="memories", query, limit=20, user_id=None)
  │
  ├─→ SELECT rowid FROM {table}_fts WHERE {table}_fts MATCH ?
  │     → FTS5 content= mode query (no triggers needed, auto-synced)
  │
  ├─→ SELECT * FROM memories WHERE id IN (fts_ids)
  │     [AND user_id = ?]  ← per-user filtering
  │
  ├─→ For each result: _log_access(memory_id, "recall")
  │
  └─→ Return: List[Dict]

─────────────────────────────────────────────────────────

recall_current(category=None, min_importance=3, limit=20, user_id=None)
  │
  ├─→ SELECT * FROM memories
  │     WHERE is_current = 1 AND importance >= ?
  │     [AND category = ?]
  │     AND (valid_from IS NULL OR valid_from <= now)
  │     AND (valid_until IS NULL OR valid_until >= now)
  │     [AND user_id = ?]
  │     ORDER BY importance DESC LIMIT ?
  │
  ├─→ For each: _log_access(memory_id, "recall")
  │
  └─→ Return: List[Dict] (only time-valid, non-superseded memories)

─────────────────────────────────────────────────────────

TokenBudgeter.select_memories(candidates, channel)
  │
  ├─→ Determine channel strategy (_episodic/_semantic/_procedural/_implicit/_default)
  ├─→ Sort by importance DESC (tiebreak: recent first)
  ├─→ Estimate tokens per memory (~4 chars/token)
  ├─→ Fill budget allocation (TokenBudget.compute())
  └─→ Return: List[Dict] (fits within channel token budget)
```

### 3c. Decay Cycle: How Forgetting Works End-to-End

```
cron / manual call
  │
  ▼
RunaMemory.decay(half_life_days=30.0, min_importance=1, user_id=None)
  │
  ├─→ JOIN memories LEFT JOIN memory_access_log
  │     [WHERE user_id = ?]
  │     Compute: days_since_access for each memory
  │
  ├─→ For each memory where should_decay(days, importance, threshold=30):
  │     │   └── Importance >= 9 → triple threshold (90 days)
  │     │   └── Otherwise → standard threshold (30 days)
  │     │
  │     ▼
  │     compute_ebbinghaus_decay(importance, days, half_life)
  │       └── R(t) = importance × 0.5^(days/half_life), clamped [1.0, 10.0]
  │
  │     UPDATE memories SET importance = decayed_value
  │     WHERE id = ? [AND user_id = ?]
  │
  ├─→ Reinforcement: memories with recent accesses get a boost
  │     compute_reinforcement_boost(importance, access_count, boost=0.5)
  │       └── new = importance + 0.5 × accesses, capped at 10.0
  │
  ├─→ Pruning: memories below min_importance after decay → DELETE
  │     (Counts as pruned, not decayed)
  │
  ├─→ AuditTrail.log(memory_id, "decay", source="mimir", ...)
  │     for each decayed/reinforced memory
  │
  └─→ Return: {"decayed": N, "reinforced": M, "pruned": P}

─────────────────────────────────────────────────────────
consolidate(user_id=None)
  │
  ├─→ decay() — Ebbinghaus forgetting + reinforcement
  ├─→ promote_to_knowledge() — high-importance, frequently-accessed → knowledge table
  │     should_promote(importance, access_count)
  │       ├── importance < 8 → False
  │       ├── access_count >= 3 → True
  │       └── importance >= 9 → True (auto-qualify)
  │     compute_confidence_for_promotion(importance, valence)
  │       └── min(0.95, importance/10 + valence × 0.05)
  │
  ├─→ Prune relationships with strength < 1
  │
  └─→ Return: {"decayed": N, "reinforced": M, "pruned": P, "promoted": K}
```

### 3d. Audit Trail: How Writes Are Logged

```
Every mutating operation on RunaMemory calls AuditTrail.log()

AuditTrail.log(memory_id, action, source, content_hash, metadata, user_id)
  │
  ├── Thread-local connection reuse (self._local.conn per thread)
  │     Avoids opening/closing SQLite connections per call
  │
  ├── Content hashing: MemoryGuard.compute_hash(content) → first 16 chars of SHA-256
  │     Detects tampering when content changes between writes
  │
  ├── INSERT INTO memory_audit
  │     (memory_id, action, source, content_hash, timestamp, metadata, user_id)
  │
  └── Return: audit_id (int)

Query paths:
  audit.query(memory_id=None, action=None, source=None, user_id=None, limit=100)
    → SELECT with dynamic WHERE clause, ORDER BY timestamp DESC
  audit.timeline(memory_id, limit=50)
    → Chronological view of all actions on a single memory
  audit.stats(user_id=None)
    → Aggregation: total_entries, action_counts, source_counts, unique_memories
  audit.verify_integrity(memory_id, current_hash)
    → Compare stored content_hash against current content hash
    → Detects unauthorized modifications
```

### 3e. WyrdGraph: How Relationships Flow

```
WyrdGraph (separate db_path, uses same SQLite database via shared path)
  │
  ├── add_edge(source_entity, target_entity, relationship_type, strength, metadata, user_id)
  │     INSERT INTO wyrd_edges (source_entity, target_entity, relationship_type,
  │       strength, metadata, user_id)
  │     ON CONFLICT(source_entity, target_entity, relationship_type, user_id)
  │       DO UPDATE SET strength=?, metadata=?, updated_at=?
  │
  ├── traverse(start, max_depth=2, relationship_type=None, user_id=None)
  │     BFS traversal following edges owned by user_id
  │     Returns: [{"entity": str, "depth": int, "path": [...], "strength": float}]
  │
  ├── get_related(entity, max_depth=2, user_id=None)
  │     Combine get_edges_from + get_edges_to for bidirectional neighborhood
  │     Returns: {"outgoing": [...], "incoming": [...]}
  │
  ├── merge_from_fact_store(fact_store_path)
  │     Read facts table from external DB
  │     Parse entities JSON array from each fact
  │     Create edges between co-occurring entities
  │     Returns: {"edges_created": N}
  │
  └── Per-user isolation on ALL methods via user_id parameter
      wyrd_edges has UNIQUE(source_entity, target_entity, relationship_type, user_id)
```

---

## 4. Cross-Reference Table: Test → Source Module

| Test File | Source Modules Tested |
|-----------|----------------------|
| `test_core.py` | `core.py` — CRUD, search, recall, entities, knowledge, conversations, backup/restore, health check |
| `test_decay.py` | `decay.py` — Ebbinghaus math, reinforcement, promotion; `core.py` — decay/consolidate integration |
| `test_audit_trail.py` | `audit.py` — log, query, timeline, stats, verify_integrity; `core.py` — auto-audit on store/update/delete |
| `test_guard_trust.py` | `guard.py` — validate_content, sanitize_content, trust levels, length limits, pattern filtering; `core.py` — integration via add_memory |
| `test_repair.py` | `repair.py` — validate_backup, check_integrity, repair_database; `core.py` — integrity_check method |
| `test_backup.py` | `backup.py` — backup_database, backup_with_rotation, export_to_json; `repair.py` — validate_backup |
| `test_namespacing.py` | `core.py` — user_id isolation across all CRUD/recall/consolidate methods; `audit.py` — per-user audit entries |
| `test_recall_quality.py` | `core.py` — precision, latency, superseded exclusion, temporal validity; `budget.py` — TokenBudget, TokenBudgeter, infer_channel |
| `test_t8_1a_delete_audit.py` | `core.py` — delete_memory user_id propagation; `audit.py` — per-user audit query |
| `test_t8_1b_update_delete_isolation.py` | `core.py` — update_memory/delete_memory user_id isolation |
| `test_t8_1c_supersede_isolation.py` | `core.py` — supersede() user_id isolation |
| `test_t8_1d_store_with_validity.py` | `core.py` — store_with_validity() user_id and source propagation |
| `test_t8_1e_get_memory_isolation.py` | `core.py` — get_memory() user_id filtering |
| `test_t8_2_read_isolation.py` | `core.py` — fts_search, recall_by_importance, recall_recent, recall_by_mood, consolidate, promote_to_knowledge, detect_contradictions — all user-isolated |
| `test_t8_3_wyrd_graph_isolation.py` | `wyrd_graph.py` — remove_edge, get_edge, traverse, get_related, edge_count, entity_count, relationship_types — all user-isolated |
| `test_t8_4_performance.py` | `core.py` — decay() JOIN (not N+1); `budget.py` — 'hecedure' typo fix; `migrations/` — 008 indexes |
| `test_t8_5_architecture.py` | `audit.py` — thread-local connection reuse, close(), multi-threaded; `core.py` — RunaMemory.close() propagating to audit |
| `test_t8_6_coverage.py` | `core.py` — entities, relationships, saga, knowledge, conversations, log_access, stats, health, integrity, repair, rebuild_fts, backup, restore, export; `wyrd_graph.py` — edge_count, entity_count, relationship_types, merge_from_fact_store; `backup.py` — github_backup |

---

## 5. Orphan Detection

### Methods/Functions with NO direct test coverage:

| Source | Method | Status |
|--------|--------|--------|
| `core.py` | `recall_by_mood()` | Tested in `test_core.py` (TestMemoryCRUD.test_recall_by_mood) and `test_t8_2_read_isolation.py` ✓ |
| `core.py` | `recall_current()` | Tested only in `test_recall_quality.py` (temporal validity tests) ✓ |
| `core.py` | `detect_contradictions()` | Tested in `test_t8_2_read_isolation.py` (user isolation) — **no dedicated contradiction-logic test** ⚠️ |
| `core.py` | `get_conversation()` | Tested in `test_t8_6_coverage.py` ✓ |
| `core.py` | `github_backup()` | Tested in `test_t8_6_coverage.py` (returns dict — no git env on Pi) ✓ |
| `context_engineer.py` | `ContextEngineer.assemble_context()` | **NO test coverage** ⚠️ |
| `context_engineer.py` | `ContextEngineer.quick_context()` | **NO test coverage** ⚠️ |
| `context_engineer.py` | `ContextResult.to_context_block()` | **NO test coverage** ⚠️ |
| `budget.py` | `TokenBudgeter.format_for_injection()` | **NO test coverage** ⚠️ |
| `budget.py` | `TokenBudgeter.get_budget_summary()` | **NO test coverage** ⚠️ |
| `budget.py` | `TokenBudget.for_model()` | **NO test coverage** ⚠️ |
| `budget.py` | `_implicit_strategy()` | Not explicitly tested (only budget_all calls it indirectly) ⚠️ |
| `budget.py` | `_procedural_strategy()` | Not explicitly tested ⚠️ |
| `wyrd_graph.py` | `get_edges_from()` | Not directly tested (tested indirectly via traverse) ⚠️ |
| `wyrd_graph.py` | `get_edges_to()` | Not directly tested ⚠️ |
| `wyrd_graph.py` | `_get_incoming()` | Private, tested indirectly via get_related ⚠️ |
| `guard.py` | `validate_write()` | Tested in `test_guard_trust.py` integration tests ✓ |
| `config.py` | `MimirConfig` (all methods) | **NO test coverage** ⚠️ |
| `migrations/runner.py` | `rollback_migration()` | **NO test coverage** ⚠️ |
| `migrations/__init__.py` | `register_migration()` | **NO test coverage** ⚠️ |
| `backup.py` | `github_backup()` | Only tested via `test_t8_6_coverage.py` (mock-safe, no actual push) |
| `core.py` | `infer_memory_type()` (module-level) | Not directly tested (called inside add_memory) |

### Disconnected / Potentially Orphaned Items:

| Item | Issue |
|------|-------|
| `migrations/__init__.py` migration 5 (T7-1) | "Guard schema-ready" — only adds VALID_CATEGORIES check via ALTER; no migration-5-specific test |
| `schema.py` `FTS_TRIGGERS` | Declared as empty list `[]`. Comment says content= mode auto-syncs. **Correct but dead code** — could be removed |
| `schema.py` `SCHEMA_VERSION = 7` | Stale — actual schema version is managed in `_schema_meta` table via migrations (currently at 8 via migration runner). **Misleading constant** ⚠️ |
| `__init__.py` `__version__ = "2.8.0"` | Documentation says v2.9.0 but code says 2.8.0. **Version mismatch** ⚠️ |
| `backup.py` `_validate_backup_file()` | Only called from `restore_from_backup()` (not exported, also exists as `validate_backup()` in repair.py). **Near-duplicate** of `repair.validate_backup()` ⚠️ |
| `core.py` `CATEGORY_TYPE_MAP` | Exported in `__init__.py` but also re-exported as `CORE_CATEGORY_TYPE_MAP`. **Dual export** ⚠️ |
| `core.py` `__del__` method | Destructor that calls `self.close()`. Python destructors are unreliable — potential resource leak ⚠️ |
| `context_engineer.py` | Entire module has **zero test coverage** ⚠️ |

---

*Map drawn by Védis Eikleið, Cartographer of Mímir's Well*
*v2.9.0 — All rivers traced to their source.*