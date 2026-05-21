# Mímir Well v2.9.0 — Structural Report

**Architect:** Rúnhild Svartdóttir  
**Date:** 2026-05-14  
**Codebase:** `src/mimir_well/` (14 files, ~4,883 lines)  
**Test Status:** 171 passing  
**Principle:** *A strong system is not one that can do everything. It is one that knows exactly what belongs where.*

---

## 1. Priority-Ranked Fix List

### P0 — Ship-Blocking (Must fix before any release)

| # | Issue | File(s) | Complexity | Detail |
|---|-------|---------|------------|--------|
| P0-1 | **SQL Injection in `fts_search()`** | `core.py:569-603` | **M** | The `table` parameter is interpolated into SQL via f-string: `f"{table}_fts"` and `f"FROM {fts_table}"`. An attacker supplying `table="memories; DROP TABLE memories--"` gets arbitrary SQL. Fix: whitelist against `{"memories", "knowledge", "saga_events"}` before interpolation. |
| P0-2 | **Version Drift: `__init__.py` says 2.8.0, `pyproject.toml` says 2.9.0** | `__init__.py:10` | **S** | `__version__ = "2.8.0"` but the package is 2.9.0. Every `pip show` and runtime version check lies. One-liner fix. |
| P0-3 | **SCHEMA_VERSION=7 but migration 008 exists** | `schema.py:8`, `migrations/__init__.py:234-261` | **S** | `SCHEMA_VERSION = 7` in schema.py, but migration 008 registers at version=8. The runner compares against the stored version, so on a fresh DB it'll apply 008 but store `8` — yet the schema constant still says 7. Any code that reads `SCHEMA_VERSION` for business logic will be wrong. Bump SCHEMA_VERSION to 8 or remove the constant and read from `_schema_meta`. |

### P1 — Must Fix Before Production

| # | Issue | File(s) | Complexity | Detail |
|---|-------|---------|------------|--------|
| P1-1 | **`decay()` and `consolidate()` bypass `_write()` lock** | `core.py:938,1052` | **M** | Both methods use `self._get_conn()` directly and `self._commit()` instead of `self._write()`. This means concurrent writes can interleave commits without the thread lock, violating the contract that `_write()` provides. Wrap each in `self._write(lambda c: ...)` or restructure. |
| P1-2 | **WyrdGraph has no `threading.local` — shared `self._db`** | `wyrd_graph.py:43` | **L** | `WyrdGraph.__init__` creates a single `sqlite3.connect()` stored on `self._db`. If two threads call `add_edge()` or `traverse()` simultaneously, they'll share the same connection without locking. SQLite in WAL mode allows concurrent reads but only one writer at a time, and without a lock you'll get `OperationalError: database is locked`. Need `threading.local()` + `threading.Lock()` pattern mirroring `RunaMemory`. |
| P1-3 | **`context_engineer.py` has ZERO test coverage** | `context_engineer.py` | **L** | 316 lines of context assembly logic with no tests. This is the critical path for prompt injection — every recall goes through it. |
| P1-4 | **Dual `CATEGORY_TYPE_MAP` exports with different values** | `core.py:42-57`, `budget.py:74-89` | **M** | `core.CATEGORY_TYPE_MAP` maps to strings (`"episodic"`) while `budget.CATEGORY_TYPE_MAP` maps to `MemoryChannel` enums. They're both exported from `__init__.py` and users may pick the wrong one. Consolidate into a single source of truth. |

### P2 — Should Fix

| # | Issue | File(s) | Complexity | Detail |
|---|-------|---------|------------|--------|
| P2-1 | **Near-duplicate `_validate_backup_file()` vs `validate_backup()`** | `backup.py:317-330`, `repair.py:16-47` | **S** | `backup._validate_backup_file(Path)` and `repair.validate_backup(str)` do the same integrity check. One takes `Path`, the other takes `str`. Different error handling. Consolidate to one canonical function. |
| P2-2 | **`FTS_TRIGGERS = []` dead code** | `schema.py:175` | **S** | The comment says "With content=external mode, FTS5 auto-syncs" but code in `core.py:187` still iterates `for trigger_sql in FTS_TRIGGERS:` — a no-op loop. Remove the loop and the empty constant. |
| P2-3 | **`detect_contradictions()` has N+1 query pattern** | `core.py:1196-1316` | **M** | Strategy 2 loops over `positive_mems` and issues a separate query per row for the negative matching (line 1249-1253). This is O(N) queries. Should pre-fetch all negatives by category in one query. |
| P2-4 | **`promote_to_knowledge()` has N+1 check query** | `core.py:1147-1149` | **S** | For each promoted memory, a separate `SELECT id FROM knowledge WHERE content = ?` checks for duplicates. Should batch-check with a single `WHERE content IN (...)` query. |
| P2-5 | **`get_stats()` uses f-string table names** | `core.py:1441` | **S** | `f"SELECT COUNT(*) FROM {table}"` — same SQL injection pattern as `fts_search()` but with a hardcoded list, so it's safe in practice. Still, consistency says use parameterized or at minimum validate against the list. |
| P2-6 | **`export_to_json()` uses f-string table names** | `backup.py:186` | **S** | Same pattern, same list. Consolidate with `get_stats()` into a `VALID_TABLES` constant. |
| P2-7 | **Migration 004 registers at version=5** | `migrations/__init__.py:131` | **S** | `register_migration(version=5, ...)` for what's named "Migration 004". This creates a gap: versions go 2, 3, 5 (for wyrd_edges), 6, 7, 8. Not broken, but confusing. Renumber or add a comment. |

### P3 — Nice-to-Have

| # | Issue | File(s) | Complexity | Detail |
|---|-------|---------|------------|--------|
| P3-1 | **`WyrdGraph.get_edges_from/to` quadruplication** | `wyrd_graph.py:216-356` | **L** | Nearly identical code for 4 permutations of `(relationship_type, user_id)`. Extract to a `_query_edges(source_or_target, entity, relationship_type, user_id)` helper. |
| P3-2 | **Hardcoded `'runa'` default user_id** | Multiple files | **M** | `user_id TEXT DEFAULT 'runa'` in schema, migrations, WyrdGraph init, and audit trail. Should be configurable via `MimirConfig`. |
| P3-3 | **`TokenBudgeter._estimate_tokens` uses different divisor than `ContextEngineer._estimate_tokens`** | `budget.py:278`, `context_engineer.py:120` | **S** | Budgeter uses `len(text) // 3`, ContextEngineer uses `len(text) // 4`. Inconsistent estimation means budget planning doesn't match actual injection. |
| P3-4 | **`_should_block` in guard.py doesn't handle CRITICAL patterns** | `guard.py:297-315` | **S** | CRITICAL severity is checked first (correct), but the `_should_block` method has a path where `trust_level >= FRITH` returns `False` even if `pattern_severity == CRITICAL`. The early return at line 298 prevents this, but the logic is fragile — if someone reorders the checks, CRITICAL patterns could be trusted-allowed. |
| P3-5 | **`eye/app.py` opens a new DB connection per request** | `eye/app.py:42-47` | **M** | `get_db()` creates a new `sqlite3.connect()` each call, `query_db()` closes it after every query. No connection pooling. High-traffic dashboard will exhaust connections. |

---

## 2. Architecture Improvements

### A1: Consolidate `CATEGORY_TYPE_MAP` into Single Source of Truth

**What:** Currently `core.py` has `CATEGORY_TYPE_MAP: Dict[str, str]` mapping categories to string types, and `budget.py` has `CATEGORY_TYPE_MAP: Dict[str, MemoryChannel]` mapping the same categories to enum values. Multiple consumers import both. Consolidate to one canonical mapping in `budget.py` (where the enum lives) and have `core.py` import from there.

**File(s):** `core.py`, `budget.py`, `__init__.py`  
**Estimated LOC:** ~15 lines changed  
**Benefit:** Eliminates a dual-source-of-truth bug class. Any new category only needs to be added once.

### A2: Thread-Safety Wrapper for SQLite Classes

**What:** Both `RunaMemory` and `AuditTrail` duplicate the same `threading.local()` + `_get_conn()` + `_commit()` pattern. `WyrdGraph` lacks it entirely. Extract a `ThreadSafeDB` mixin or base class providing `_get_conn()`, `_write()`, `_commit()`, and `close()`.

**File(s):** New `db_base.py`, `core.py`, `audit.py`, `wyrd_graph.py`  
**Estimated LOC:** ~80 new, ~60 removed  
**Benefit:** Guarantees all DB access classes use the same thread-safety pattern. Fixes P1-2 (WyrdGraph thread safety) and prevents future regressions.

### A3: Whitelist-Based Table Validation Layer

**What:** Create a `VALID_FTS_TABLES = {"memories", "knowledge", "saga_events"}` and `VALID_TABLES = {...}` constant set. Both `fts_search()` and `get_stats()` and `export_to_json()` validate against it. This eliminates the SQL injection family of bugs (P0-1, P2-5, P2-6) with a single pattern.

**File(s):** `core.py`, `backup.py`, new `constants.py` or extend `schema.py`  
**Estimated LOC:** ~20 new, ~10 changed  
**Benefit:** Closes P0-1 SQL injection. Creates a single place to add/remove tables. Makes the table namespace auditable.

### A4: Parameterized User-ID Filtering Helper

**What:** The codebase has the same `if user_id: ... else: ...` pattern duplicated ~20 times across `core.py`, `wyrd_graph.py`, and `audit.py`. Extract a `build_where(clauses, params, user_id)` helper that appends `AND user_id = ?` when user_id is provided, reducing duplication and the risk of forgetting the user_id filter.

**File(s):** `core.py`, `wyrd_graph.py`, `audit.py`  
**Estimated LOC:** ~30 new, ~150 removed  
**Benefit:** Reduces cyclomatic complexity by ~30%. Eliminates an entire class of "forgot to filter by user_id" bugs.

### A5: Add `context_engineer.py` Test Coverage

**What:** The ContextEngineer has 316 lines of critical path logic with zero tests. Write tests covering: entity extraction, budget allocation, recall failure fallback, graph path deduplication, and the `to_context_block()` output format.

**File(s):** New `tests/test_context_engineer.py`  
**Estimated LOC:** ~200 new  
**Benefit:** Prevents regressions in the memory injection pipeline. Enables confident refactoring of budget logic.

---

## 3. Performance Opportunities

### 3.1 — Batch Decay Updates (Medium Impact)

**File:** `core.py:977-1001`  
**Issue:** `decay()` iterates over all current memories and issues an individual `UPDATE` for each one. With 10K memories, that's 10K separate SQL statements.  
**Fix:** Replace the per-row UPDATEs with a single batch UPDATE using a CTE or temp table:

```sql
UPDATE memories SET importance = CASE
  WHEN new_importance < ? THEN MAX(1, ROUND(new_importance))
  ELSE MIN(10, MAX(1, ROUND(new_importance)))
END
WHERE id IN (...);
```

Estimated improvement: ~5-10x faster for large datasets.

### 3.2 — Missing Composite Index on `wyrd_edges(source_entity, relationship_type, user_id)`

**File:** `wyrd_graph.py`, `schema.py`  
**Issue:** The `get_edges_from()` method frequently queries with `(source_entity, relationship_type, user_id)` triple, but the only indexes are on individual columns. A composite index would turn range scans into point lookups.  
**Fix:** Add `CREATE INDEX IF NOT EXISTS idx_wyrd_edges_src_type_user ON wyrd_edges(source_entity, relationship_type, user_id)` to `INDEXES` in `schema.py`. Same for target-side queries.  
**Estimated improvement:** ~3-5x faster for edge lookups on medium-sized graphs.

### 3.3 — `detect_contradictions()` N+1 Query (P2-3 Expanded)

**File:** `core.py:1196-1316`  
**Issue:** Strategy 2 (valence inversion) fires one query per positive memory row to find matching negatives. With 100 positive memories and 1000 negative, that's 100 queries.  
**Fix:** Single query:

```sql
SELECT p.id, p.content, p.category, p.emotional_valence,
       n.id, n.content, n.emotional_valence
FROM memories p, memories n
WHERE p.category = n.category
  AND p.emotional_valence > 0.3
  AND n.emotional_valence < -0.3
  AND p.user_id = ? AND n.user_id = ?
```

### 3.4 — `promote_to_knowledge()` Duplicate Check (P2-4 Expanded)

**File:** `core.py:1147-1149`  
**Issue:** Per-memory duplicate check is O(N) queries.  
**Fix:** Pre-fetch all existing knowledge content into a set, then check membership in Python. One query instead of N.

### 3.5 — `WyrdGraph.traverse()` BFS Issues N+1

**File:** `wyrd_graph.py:393-426`  
**Issue:** Each BFS hop triggers a fresh SQL query. For max_depth=3 with fan-out, this explodes.  
**Fix:** Pre-fetch all edges for the subgraph within 3 hops using a single recursive CTE, then traverse in-memory.

### 3.6 — `context_engineer.py` Estimates Tokens Inconsistently

**File:** `context_engineer.py:120` vs `budget.py:278`  
**Issue:** `ContextEngineer._estimate_tokens` uses `len(text) // 4` while `TokenBudgeter._estimate_tokens` uses `len(text) // 3`. The budgeter plans `X` tokens but the context engineer counts `0.75X`, leading to over-allocation.

### 3.7 — `export_to_json` Table Scan Without Row Limit

**File:** `backup.py:183-193`  
**Issue:** `SELECT * FROM {table}` with no LIMIT could OOM on large databases. Add a configurable row limit or streaming export.

---

## 4. API Surface Cleanup

### Inconsistent Method Signatures

The codebase has several patterns that should be unified:

| Pattern | Current | Proposed |
|---------|---------|----------|
| **User filtering** | Some methods take `Optional[str] user_id`, others default to `"runa"` hardcoded, `WyrdGraph` defaults to `"runa"` in `add_edge` but `None` elsewhere. | All methods should take `Optional[str] user_id = None`. When `None`, the caller's intent determines scope. Use `MimirConfig.default_user_id` for the "runa" default. |
| **Return types** | `decay()` → `Dict[str, int]`, `consolidate()` → `Dict[str, int]`, `promote_to_knowledge()` → `Dict[str, int]`, `add_memory()` → `int` or `GuardResult`. Methods return different shapes. | Standardize: Write operations return `int` (ID) or `GuardResult`. Batch operations return `Dict[str, int]`. Query operations return `List[Dict]`. |
| **Error handling** | `fts_search()` silently falls back to `search_memories()` on `OperationalError`. `restore_from_backup()` catches all `Exception`. `WyrdGraph.merge_from_fact_store()` catches `OperationalError` and returns a dict with "error". | Adopt a consistent exception hierarchy: `MimirError` base, `MimirSearchError`, `MimirBackupError`, `MimirIntegrityError`. Let callers decide. |
| **Connection passing** | `check_integrity(conn)` takes a connection. `RunaMemory.integrity_check()` delegates to it. Some functions take `(conn, db_path)`, some take `(db_path)`, some take `(db_path, conn)`. | All public functions that need a connection should take `conn` as the first parameter. Functions that need the path should take `db_path` as the second. Follow `(conn, db_path)` consistently. |
| **Naming** | `_validate_backup_file()` (private) vs `validate_backup()` (public) doing the same thing. `backup_with_rotation` (public in backup.py) vs `_backup_with_rotation` (imported as private in core.py). | One canonical function per responsibility. Private functions should have single-underbar prefix. Public functions should be in one module. |

### Proposed Consistent Pattern

```python
# 1. User filtering: always Optional[str] = None
def search_memories(self, query: str, *, user_id: Optional[str] = None, ...) -> List[Dict]: ...

# 2. Return type convention
# - Single resource ops → Optional[Dict] (None = not found)
# - Create ops → int (ID)
# - Batch/bulk ops → Dict[str, int] (counts)
# - Query/Search ops → List[Dict]

# 3. Error handling: typed exceptions
class MimirError(Exception): pass
class MimirSearchError(MimirError): pass
class MimirBackupError(MimirError): pass

# 4. Connection parameter order: (conn, db_path) always
def backup_database(conn: sqlite3.Connection, db_path: Path, ...) -> str: ...

# 5. Deduplicate: one `validate_backup()`, one `CATEGORY_TYPE_MAP`
```

---

## 5. Sprint 9 Proposal

### Sprint Name: **Byrgishólmr** (ᛒ ᛁ ᚱ ᚷ)

*Byrgishólmr — the fortress isle where walls are reinforced and the gate is made strong. Not a sprint of expansion, but of hardening.*

---

### Phase 1: Gate Lock (P0 Fixes) — ~25 LOC

Fix the SQL injection in `fts_search()`, sync `__version__` to 2.9.0, and bump `SCHEMA_VERSION` to 8 (or remove the constant in favor of `_schema_meta` reads).

- `core.py`: Add whitelist validation for `table` parameter
- `__init__.py`: Change `__version__`
- `schema.py`: Bump `SCHEMA_VERSION` or refactor to read from DB

---

### Phase 2: Thread Weaving (P1-1 + P1-2 + A2) — ~120 LOC

Thread-safety for all database classes. Extract `ThreadSafeDB` mixin. Wrap `decay()` and `consolidate()` in `_write()`. Add `threading.local` to `WyrdGraph`.

- New `db_base.py` with `ThreadSafeDB` mixin
- `core.py`: Refactor `decay()`/`consolidate()` to use `_write()`
- `wyrd_graph.py`: Add `threading.local` + lock pattern
- `audit.py`: Refactor to use mixin (optional, lower priority)

---

### Phase 3: Single Truth (P1-4 + A1 + A4) — ~45 LOC

Consolidate `CATEGORY_TYPE_MAP` to one source. Add parameterized user-ID helper. Remove dual export from `__init__.py`.

- `budget.py`: Keep canonical `CATEGORY_TYPE_MAP` (enum-valued)
- `core.py`: Import from `budget.py`, add `infer_memory_type()` shim for backward compat
- `core.py`, `wyrd_graph.py`: Extract `build_where()` helper
- `__init__.py`: Update exports

---

### Phase 4: Test Foundations (P1-3 + A5) — ~200 LOC

Write tests for `context_engineer.py`. Cover entity extraction, context assembly, graph path deduplication, budget allocation, and failure fallbacks.

- New `tests/test_context_engineer.py`
- Test entity extraction from various message formats
- Test `assemble_context()` with mocked mimir + graph
- Test `ContextResult.to_context_block()` output format
- Test `quick_context()` passthrough

---

### Phase 5: Cleanup Sweep (P2 Issues) — ~60 LOC

Remove dead code, deduplicate validation functions, fix minor inconsistencies.

- Remove `FTS_TRIGGERS = []` and the loop that iterates it
- Consolidate `_validate_backup_file()` and `validate_backup()`
- Fix migration 004 version comment
- Standardize `WyrdGraph.get_edges_from/to` to use a shared helper
- Fix token estimation inconsistency (P3-3)

---

### Phase 6: Performance Foundations (3.1 + 3.2) — ~50 LOC

Batch decay updates. Add composite indexes. These are the highest-impact performance wins.

- `core.py`: Batch UPDATE in `decay()` via CTE
- `schema.py` or new migration: Add composite indexes on `wyrd_edges`
- Migration 009: Performance composite indexes

---

### Phase 7: API Consistency (A3 + Section 4) — ~80 LOC

Add table whitelists. Begin the exception hierarchy. Standardize user_id pattern across all public methods.

- New `constants.py` with `VALID_FTS_TABLES`, `VALID_TABLES`
- `core.py`: Validate `table` in `fts_search()`, `get_stats()`
- `backup.py`: Validate `table` in `export_to_json()`
- Begin `exceptions.py` with `MimirError` hierarchy

---

### Summary

| Phase | Focus | Est. LOC | Priority |
|-------|-------|----------|----------|
| 1. Gate Lock | P0 fixes (SQL injection, version drift, schema version) | ~25 | Critical |
| 2. Thread Weaving | Thread safety, _write() lock consistency | ~120 | High |
| 3. Single Truth | CATEGORY_TYPE_MAP consolidation, user-ID helper | ~45 | High |
| 4. Test Foundations | context_engineer.py test coverage | ~200 | High |
| 5. Cleanup Sweep | Dead code, duplicate functions, minor inconsistencies | ~60 | Medium |
| 6. Performance Foundations | Batch decay, composite indexes | ~50 | Medium |
| 7. API Consistency | Whitelists, exception hierarchy, user_id pattern | ~80 | Medium |
| **Total** | | **~580** | |

---

*"The Well's walls must hold before its waters can deepen."* — Rúnhild Svartdóttir