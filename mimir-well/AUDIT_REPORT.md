# Mímir Well v2.9.0 — Forensic Audit Report

**Auditor:** Sólrún Hvítmynd  
**Date:** 2026-05-14  
**Scope:** `src/mimir_well/` (14 files, ~4883 lines), `tests/` (18 files, ~3997 lines)  
**Maxim:** *"If it cannot survive scrutiny, it was never stable."*

---

## 1. Version Drift — CRITICAL

### 1.1 `__init__.py` version stuck at 2.8.0

- **File:** `src/mimir_well/__init__.py`, line 10
- **Code:** `__version__ = "2.8.0"`
- **Expected:** `"2.9.0"` (matches `pyproject.toml` line 7 and `CHANGELOG.md` line 5)
- **Impact:** Any code or packaging tool reading `mimir_well.__version__` reports the wrong version. This is the canonical version string for the package.
- **Severity:** **CRITICAL**

### 1.2 SCHEMA_VERSION stale at 7

- **File:** `src/mimir_well/schema.py`, line 8
- **Code:** `SCHEMA_VERSION = 7`
- **Expected:** `8` — Migration 008 (performance indexes) was added in this sprint but `SCHEMA_VERSION` was not bumped.
- **Impact:** Fresh installs write `schema_version=7` into `_schema_meta` even though migration 008 should set it to 8. The migration runner *does* update it to 8 when run, but `_init_db()` at line 196 of `core.py` hard-writes `str(SCHEMA_VERSION)` which is 7, overwriting whatever the migrations set. This means:
  1. On first init, version is set to 7.
  2. Migration 008 runs and sets it to 8.
  3. But if `_init_db()` runs again (e.g., on restart), it overwrites back to 7 via `INSERT OR REPLACE`.
  **The migrations become re-runnable on every restart, and the schema version ping-pongs between 7 and 8.**
- **Severity:** **CRITICAL**

### 1.3 Version consistency summary

| Source | Value | Status |
|---|---|---|
| `pyproject.toml` line 7 | `2.9.0` | ✅ Correct |
| `CHANGELOG.md` line 5 | `[2.9.0]` | ✅ Correct |
| `__init__.py` line 10 | `2.8.0` | ❌ STALE |
| `schema.py` line 8 | `7` | ❌ STALE (should be 8) |

---

## 2. Dead Code — MEDIUM

### 2.1 `FTS_TRIGGERS = []` — empty list, never populated

- **File:** `src/mimir_well/schema.py`, line 175
- **Code:** `FTS_TRIGGERS = []`
- **Comment:** "With content=external mode, FTS5 auto-syncs on INSERT, UPDATE, and DELETE. No triggers are needed"
- **Also consumed:** `core.py` line 187 iterates over it: `for trigger_sql in FTS_TRIGGERS:`
- **Impact:** Zero runtime impact — the for-loop simply never executes. But the import, export, and iteration of an empty constant is misleading.
- **Severity:** **LOW**

### 2.2 Migration 004 registered as version 5

- **File:** `src/mimir_well/migrations/__init__.py`, lines 131-135
- **Code:**
  ```python
  register_migration(
      version=5,
      up_sql=MIGRATION_004_UP,
      down_sql=MIGRATION_004_DOWN,
      ...
  )
  ```
- **Impact:** The constant is named `MIGRATION_004_UP` but registers as version 5. This is confusing but functionally harmless since the migration system uses the `version` key, not the variable name. However, it indicates a numbering drift between naming and semantics.
- **Severity:** **LOW**

### 2.3 `import os` at module level in core.py

- **File:** `src/mimir_well/core.py`, line 14 (import os) and line 1434 (`import os` again inside `get_stats`)
- **Impact:** `os` is imported at module level (line 14) and again locally inside `get_stats()` (line 1434). The local import is redundant.
- **Severity:** **LOW**

### 2.4 `import re` inside method body in context_engineer.py

- **File:** `src/mimir_well/context_engineer.py`, line 130
- **Code:** `import re` inside `_extract_entities()`
- **Impact:** Minor performance penalty from re-importing on every call. Should be at module level.
- **Severity:** **LOW**

---

## 3. Bug Candidates — HIGH

### 3.1 fts_search() — SQL injection via `table` parameter

- **File:** `src/mimir_well/core.py`, lines 569-603
- **Code:**
  ```python
  def fts_search(self, table: str, query: str, limit: int = 20,
                   user_id: Optional[str] = None) -> List[Dict]:
      fts_table = f"{table}_fts"
      # ...
      cursor.execute(f"""
          SELECT src.*, fts.rank
          FROM {fts_table} fts
          JOIN {table} src ON src.id = fts.rowid
          WHERE {fts_table} MATCH ? AND src.user_id = ?
          ORDER BY fts.rank
          LIMIT ?
      """, (query, user_id, limit))
  ```
- **Impact:** The `table` parameter is interpolated directly into SQL using f-strings. If a caller passes a malicious `table` value like `memories; DROP TABLE memories;--`, it creates an SQL injection vector. While the docstring says "One of 'memories', 'knowledge', 'saga_events'", there is **no validation** enforcing this.
- **Severity:** **CRITICAL**

### 3.2 detect_contradictions() — f-string SQL with user-controlled `user_filter`

- **File:** `src/mimir_well/core.py`, lines 1055, 1059, 1063, 1198, 1205, 1236, 1249
- **Code:**
  ```python
  user_filter = " AND user_id = ?" if user_id else ""
  cursor.execute(f"""
      UPDATE memories SET importance = MAX(1, importance - 1)
      WHERE importance > 5
      AND timestamp < datetime('now', '-30 days'){user_filter}
  """, user_params)
  ```
- **Impact:** `user_filter` is controlled by the code (not user input), so this specific instance is safe. However, this pattern of f-string SQL construction is fragile — if future modifications introduce user-controlled strings into `user_filter`, it becomes an injection vector. The safer pattern is parameterized SQL throughout.
- **Severity:** **MEDIUM** (pattern risk, not active exploit)

### 3.3 consolidate() uses f-string SQL with `user_filter` — no `db_path` parameter

- **File:** `src/mimir_well/core.py`, lines 1037-1109
- **Impact:** Same pattern as 3.2. The consolidate method builds SQL via f-strings with `user_filter`. Safe now but fragile.
- **Severity:** **MEDIUM** (pattern risk)

### 3.4 get_stats() uses f-string for table names

- **File:** `src/mimir_well/core.py`, line 1441
- **Code:** `cursor.execute(f"SELECT COUNT(*) FROM {table}")`
- **Impact:** Hardcoded table list, so not injectable from outside. But if the table list ever included user input, it would be an injection vector. Low risk.
- **Severity:** **LOW**

### 3.5 WyrdGraph.get_edge() — inconsistent return shape vs get_edges_from()

- **File:** `src/mimir_well/wyrd_graph.py`
  - `get_edge()` (line 166): Returns dict with key `"relationship_type"`
  - `get_edges_from()` (line 216): Returns dict with key `"relationship"`
  - `get_edges_to()` (line 287): Returns dict with key `"relationship"`
- **Impact:** Callers expecting consistent key names across edge result shapes will be confused. `get_edge()` uses `relationship_type` while `get_edges_from/to` use `relationship`.
- **Severity:** **HIGH**

### 3.6 WyrdGraph.merge_from_fact_store() — metadata uses wrong key for category

- **File:** `src/mimir_well/wyrd_graph.py`, line 591
- **Code:**
  ```python
  self.add_edge(
      source=entities[0],
      target=entities[1],
      relationship_type=row["category"],  # Always "relationship" since that's the filter
      ...
  )
  ```
- **Impact:** The query filters `WHERE category = 'relationship'`, so `row["category"]` is always `"relationship"`. This means every migrated edge has `relationship_type="relationship"`, which is meaningless. The actual relationship content is in the `content` field, not `category`.
- **Severity:** **MEDIUM**

### 3.7 health_check() — cursor used after potential exception without reset

- **File:** `src/mimir_well/core.py`, lines 1404-1428
- **Code:**
  ```python
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
      cursor.execute("PRAGMA quick_check")  # cursor may be in bad state
  ```
- **Impact:** If the first `try` block fails, the `cursor` variable may be in an undefined state, but the second `try` block reuses it. Also, `cursor` is defined inside the first `try` block — if the exception occurs *before* `cursor` is assigned (e.g., if `_get_conn()` fails), then `cursor` is an `UnboundLocalError`.
- **Severity:** **HIGH**

### 3.8 Migration 004 UNIQUE constraint mismatch with schema.py

- **File:** `src/mimir_well/migrations/__init__.py`, line 112
- **Code (migration 004):** `UNIQUE(source_entity, target_entity, relationship_type, user_id)`
- **Code (schema.py):** `UNIQUE(source_entity, target_entity, relationship_type, user_id)` — same.
- **BUT:** Migration 004 (line 112) includes `user_id` in the UNIQUE constraint, but the migration creates the table *without* the `user_id` column first. The column is only added by migration 007. This means migration 004's CREATE TABLE will fail because `user_id` doesn't exist yet.
  - However, examining more carefully: Migration 004 is registered as version 5. It runs *after* the base schema. The `user_id` column is added by migration 007 (version 7). So on a fresh DB, `_init_db()` creates the base tables with the full schema including `user_id` in `WYRD_EDGES_TABLE`. The migrations only run on upgrades from older versions.
  - **For upgrade path:** If upgrading from schema version 4 to 5, migration 004 will try to create `wyrd_edges` with `user_id` in the UNIQUE constraint, but `user_id` column doesn't exist yet. **This is a real migration path bug.**
- **Severity:** **HIGH**

### 3.9 context_engineer.py — indentation error in section 3

- **File:** `src/mimir_well/context_engineer.py`, line 239
- **Code:** `# ── 3. Procedural: Skills and Patterns ────────────────────────────────────`
  This comment and the subsequent `try:` block (lines 240-262) are at module-level indentation (no indentation), not inside the `assemble_context` method. The same applies to lines 264-278 and 279-285.
- **Impact:** This is actually correct Python — these lines are at the same indentation level as the previous sections inside `assemble_context`. The comments are just at column 0. The code works fine.
- **Severity:** NOT A BUG (misleading formatting only)

---

## 4. Missing Error Handling — HIGH

### 4.1 WyrdGraph — no `close()` on thread-local connection patterns

- **File:** `src/mimir_well/wyrd_graph.py`, lines 37-47
- **Code:**
  ```python
  def __init__(self, db_path: str):
      self._db = sqlite3.connect(db_path)
      ...
      self._db.close()
  ```
- **Impact:** `WyrdGraph.__init__` creates a direct (not thread-local) SQLite connection. If the WyrdGraph is used from multiple threads, this is a race condition. Unlike `RunaMemory` which uses `threading.local()`, WyrdGraph shares one connection. The `close()` method exists but no thread-safety mechanism.
- **Severity:** **HIGH**

### 4.2 WyrdGraph — no try/except on database operations

- **File:** `src/mimir_well/wyrd_graph.py` (multiple methods)
- **Impact:** `add_edge()`, `remove_edge()`, `get_edge()`, `get_edges_from()`, `get_edges_to()`, `traverse()`, `_get_incoming()`, `edge_count()`, `entity_count()`, `relationship_types()` — none of these methods have any error handling. A database error (locked, corrupt, etc.) will propagate as an unhandled `sqlite3.OperationalError`.
- **Severity:** **MEDIUM**

### 4.3 MimirConfig._load() — race condition on file creation

- **File:** `src/mimir_well/config.py`, lines 49-74
- **Impact:** Between `self._config_path.parent.mkdir()` and `open()`, another process could create or modify the file. More critically, there's no error handling for the case where the config file exists but contains invalid JSON after a partial write. The JSON decode error is caught, but the `OSError` path logs a warning and continues with defaults — which may silently mask configuration loss.
- **Severity:** **LOW**

### 4.4 context_engineer.py — bare `except Exception: pass` on graph lookups

- **File:** `src/mimir_well/context_engineer.py`, lines 225-226
- **Code:**
  ```python
  except Exception:
      pass  # Graph lookups are best-effort
  ```
- **Impact:** Swallows *all* exceptions including `KeyboardInterrupt` subclasses (though not `KeyboardInterrupt` itself). More importantly, SQLite connection failures, schema errors, and other serious problems are silently ignored.
- **Severity:** **MEDIUM**

### 4.5 restore_from_backup() closes conn_ref but doesn't reopen

- **File:** `src/mimir_well/backup.py`, lines 136-141
- **Code:**
  ```python
  if conn_ref:
      try:
          conn_ref.close()
      except Exception:
          pass
  ```
- **Impact:** After closing the connection passed in, the `RunaMemory` instance still holds a reference to the closed connection in its thread-local storage. Subsequent operations will fail with "closed database" errors. There is no mechanism to reopen or reconnect.
- **Severity:** **HIGH**

### 4.6 _init_db() writes SCHEMA_VERSION unconditionally on every startup

- **File:** `src/mimir_well/core.py`, lines 194-197
- **Code:**
  ```python
  cursor.execute(
      "INSERT OR REPLACE INTO _schema_meta (key, value) VALUES (?, ?)",
      ("schema_version", str(SCHEMA_VERSION)),
  )
  ```
- **Impact:** This overwrites the schema version with the (stale) constant `7` every time `RunaMemory` is initialized. If migrations have been applied to bring the version to 8, the next restart will reset it to 7, causing migrations to re-run unnecessarily or incorrectly.
- **Severity:** **CRITICAL** (drifts into version mismatch with 1.2)

---

## 5. Type Inconsistencies — MEDIUM

### 5.1 add_memory() returns -1 on guard block, int otherwise

- **File:** `src/mimir_well/core.py`, line 208
- **Signature:** `-> int`
- **Actual:** Returns `cursor.lastrowid` (positive int) on success, `-1` on guard block
- **Impact:** Callers checking truthiness (`if result`) will treat `-1` as truthy (success), not falsy (failure). Should return `None` or raise an exception on block.
- **Severity:** **MEDIUM**

### 5.2 store_with_validity() also returns -1 on guard block

- **File:** `src/mimir_well/core.py`, line 722
- **Same issue as 5.1.**
- **Severity:** **MEDIUM**

### 5.3 supersede() returns -1 on failure

- **File:** `src/mimir_well/core.py`, line 773
- **Same pattern.**
- **Severity:** **MEDIUM**

### 5.4 merge_from_fact_store() returns inconsistent dict shapes

- **File:** `src/mimir_well/wyrd_graph.py`, line 560
- **Code:** On success returns `{"edges_created": N, "edges_skipped": N, "total_facts": N}`. On failure, returns `{"edges_created": 0, "edges_skipped": 0, "total_facts": 0, "error": str}`.
- **Impact:** The error path adds an `"error"` key not present in success. Callers checking for `"error"` will work, but the shape inconsistency could cause issues with typed consumers.
- **Severity:** **LOW**

---

## 6. Memory Leaks / Connection Management — HIGH

### 6.1 WyrdGraph — no thread-local connections, single shared connection

- **File:** `src/mimir_well/wyrd_graph.py`, line 43
- **Code:** `self._db = sqlite3.connect(db_path)`
- **Impact:** Unlike `RunaMemory` which uses `threading.local()` for per-thread connections, `WyrdGraph` creates a single shared connection. In multi-threaded use (as in ContextEngineer), `self._db` will be shared across threads without synchronization, leading to `sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that thread`.
- **Severity:** **HIGH**

### 6.2 WyrdGraph — no WAL mode configuration in schema.py version

- **File:** `src/mimir_well/wyrd_graph.py`, line 44
- **The `__init__` method sets WAL mode, but this is separate from the main database.** If the WyrdGraph is pointed at the same DB as RunaMemory, WAL mode is already set. If pointed at a different DB, it sets its own WAL. No leak — just inconsistency in configuration patterns.
- **Severity:** **LOW**

### 6.3 RunaMemory.close() only closes self._local.conn

- **File:** `src/mimir_well/core.py`, lines 1461-1473
- **Code:**
  ```python
  def close(self):
      if hasattr(self, 'audit') and self.audit is not None:
          self.audit.close()
      conn = getattr(self._local, 'conn', None)
      if conn:
          try:
              conn.close()
          except Exception:
              pass
          self._local.conn = None
  ```
- **Impact:** Only closes the connection for the *calling* thread. If other threads have opened connections via `_get_conn()`, those connections remain open. This is a known limitation of thread-local storage — `close()` only cleans up the current thread.
- **Severity:** **MEDIUM**

---

## 7. SQL Injection Risk — CRITICAL

### 7.1 fts_search() table name interpolation — CONFIRMED INJECTION VECTOR

- **File:** `src/mimir_well/core.py`, lines 569-603
- **Code:**
  ```python
  def fts_search(self, table: str, query: str, ...):
      fts_table = f"{table}_fts"
      cursor.execute(f"""
          SELECT src.*, fts.rank
          FROM {fts_table} fts
          JOIN {table} src ON src.id = fts.rowid
          WHERE {fts_table} MATCH ? ...
      """, ...)
  ```
- **Impact:** The `table` parameter is directly interpolated into SQL. No whitelist validation. Any caller passing a crafted table name can inject arbitrary SQL. The method is public and exported.
- **Severity:** **CRITICAL**

### 7.2 consolidate() f-string SQL patterns

- **File:** `src/mimir_well/core.py`, lines 1055-1097
- **Impact:** Pattern uses `user_filter` f-string concatenation. While `user_filter` is computed internally, the pattern is fragile and should use parameterized queries for consistency.
- **Severity:** **MEDIUM** (current code is safe; pattern is risky)

---

## 8. Race Conditions — HIGH

### 8.1 RunaMemory._write() uses threading.Lock but decay() bypasses it

- **File:** `src/mimir_well/core.py`, lines 141-154 (`_write`) vs lines 922-1033 (`decay`)
- **Impact:** `decay()` reads from and writes to the database using `self._get_conn()` directly (line 938: `conn = self._get_conn()`), then performs individual row updates (lines 995-1000) without using `self._write()`. While `_write()` uses `self._lock`, the `decay()` method performs bulk write operations without acquiring the lock. In concurrent scenarios, `decay()` could interleave with `_write()` calls from other threads.
- **Severity:** **HIGH**

### 8.2 consolidate() also bypasses _write()

- **File:** `src/mimir_well/core.py`, lines 1037-1109
- **Impact:** Same pattern as 8.1. Direct `cursor.execute()` calls without acquiring `self._lock`.
- **Severity:** **HIGH**

### 8.3 WyrdGraph — no thread safety at all

- **File:** `src/mimir_well/wyrd_graph.py`
- **Impact:** As noted in 6.1, WyrdGraph shares a single connection across all threads with no locking mechanism.
- **Severity:** **HIGH**

### 8.4 WyrdGraph.create table + ALTER TABLE — not atomic

- **File:** `src/mimir_well/wyrd_graph.py`, lines 50-78
- **Impact:** The `__init__` method runs `CREATE TABLE IF NOT EXISTS` followed by `ALTER TABLE ADD COLUMN`. If two threads hit init simultaneously, both may try to create the table and add the column, resulting in race condition errors (though `IF NOT EXISTS` and `try/except OperationalError` mitigate this somewhat).
- **Severity:** **LOW** (mitigated by idempotent patterns)

---

## 9. Test Coverage Gaps — HIGH

### 9.1 context_engineer.py — ZERO test coverage

- **File:** `src/mimir_well/context_engineer.py` (316 lines)
- **No test file exists for `ContextEngineer`, `ContextResult`, or `assemble_context()`.**
- **Impact:** The entire context assembly pipeline — which determines what memories get injected into a Hermes turn — is untested. This includes entity extraction, budget allocation, and multi-channel recall.
- **Severity:** **HIGH**

### 9.2 config.py (MimirConfig) — ZERO test coverage

- **File:** `src/mimir_well/config.py` (111 lines)
- **No test file exists for `MimirConfig`.**
- **Impact:** Configuration loading, environment variable overrides, default creation, and `set()` persistence are all untested.
- **Severity:** **MEDIUM**

### 9.3 eye/app.py — ZERO test coverage

- **File:** `src/mimir_well/eye/app.py` (948 lines)
- **No test file exists for the Flask dashboard.**
- **Impact:** The HTTP endpoint that directly queries SQLite has zero security or integration testing. SQL injection via the Flask `query_db()` function is a live concern (see eye/app.py line 40-47 which uses `get_db()` with raw SQL).
- **Severity:** **MEDIUM** (dashboard is likely dev-only, but still)

### 9.4 WyrdGraph — minimal test coverage

- **Tests exist for:** `edge_count`, `entity_count`, `relationship_types`, `merge_from_fact_store`, plus thread-isolation tests.
- **Missing tests for:** `get_edge()`, `get_edges_from()` with all parameter combinations, `get_edges_to()` with parameters, `traverse()` at depth > 1, `get_related()` with depth > 2, `remove_edge()` return value.
- **Severity:** **MEDIUM**

### 9.5 decay.py — partial coverage

- **File:** `tests/test_decay.py` exists but onlytests `compute_ebbinghaus_decay`, `compute_reinforcement_boost`, and timing-based decay via `RunaMemory.decay()`.
- **Missing:** Direct unit tests for `should_decay()`, `should_promote()`, `compute_confidence_for_promotion()` edge cases.
- **Severity:** **LOW**

---

## 10. API Surface Inconsistencies — MEDIUM

### 10.1 Dual CATEGORY_TYPE_MAP export

- **File:** `src/mimir_well/__init__.py`, lines 36-38
- **Code:**
  ```python
  from mimir_well.budget import (
      ...
      CATEGORY_TYPE_MAP,
  )
  from mimir_well.core import infer_memory_type, CATEGORY_TYPE_MAP as CORE_CATEGORY_TYPE_MAP, VALID_MEMORY_TYPES
  ```
- **Impact:** Two different `CATEGORY_TYPE_MAP` constants are exported under different names:
  - `budget.CATEGORY_TYPE_MAP` maps categories to `MemoryChannel` enum values
  - `core.CATEGORY_TYPE_MAP` maps categories to plain strings (`"episodic"`, etc.)
  
  They have **identical key sets** but different value types. Importing both under different names (`CATEGORY_TYPE_MAP` and `CORE_CATEGORY_TYPE_MAP`) is confusing. Any consumer using the budget version expecting string values (or vice versa) will get enum objects instead.
- **Severity:** **HIGH**

### 10.2 Near-duplicate backup validation functions

- **File:** `src/mimir_well/backup.py`, lines 317-330 (`_validate_backup_file`)
- **File:** `src/mimir_well/repair.py`, lines 16-47 (`validate_backup`)
- **Impact:** Two nearly identical functions:
  - `repair.validate_backup(backup_path: str)` → takes `str`, checks existence, runs integrity_check, returns bool
  - `backup._validate_backup_file(backup: Path)` → takes `Path`, runs integrity_check (not quick_check), returns bool
  
  Key difference: `_validate_backup_file` uses `PRAGMA integrity_check` (full check, slow) while `validate_backup` uses `PRAGMA integrity_check` (same, but they're documented differently). Actually, both use `integrity_check` — so the difference is just parameter type and error handling.
- **Severity:** **LOW** (code smell, not a bug)

### 10.3 Inconsistent parameter naming: `source` vs `user_id` precedence

- **File:** `src/mimir_well/core.py`
  - `add_memory(source="mimir", user_id="runa")` — two identity params
  - `update_memory(source="unknown", user_id="runa")` — same pattern
  - `delete_memory(source="unknown", user_id="runa")` — same pattern
  - `store_with_validity(user_id="runa", source="temporal")` — parameter order differs from `add_memory`
- **Impact:** The alternating order of `source` and `user_id` in method signatures is confusing for API consumers.
- **Severity:** **LOW**

### 10.4 WyrdGraph.get_edge() returns different key names than get_edges_from()

- See finding 3.5 above. `get_edge()` uses `"relationship_type"` while `get_edges_from()` and `get_edges_to()` use `"relationship"`.
- **Severity:** **HIGH**

### 10.5 add_memory() return type: int with sentinel -1

- See finding 5.1. Using -1 as a sentinel for "blocked by guard" is non-Pythonic and inconsistent with the `-> int` type hint (which doesn't document the -1 case).
- **Severity:** **MEDIUM**

---

## Summary by Severity

| Severity | Count | Key Items |
|---|---|---|
| **CRITICAL** | 3 | Version drift (1.1, 1.2), SQL injection in fts_search (7.1), _init_db overwrites schema version (4.6) |
| **HIGH** | 8 | Inconsistent edge dict keys (3.5, 10.4), health_check UnboundLocalError (3.7), migration 004 UNIQUE constraint (3.8), WyrdGraph thread-unsafety (6.1/8.3), decay/consolidate bypass lock (8.1/8.2), NO test coverage for context_engineer (9.1), dual CATEGORY_TYPE_MAP (10.1), restore_from_backup closes conn (4.5) |
| **MEDIUM** | 10 | f-string SQL pattern risk (3.2/3.3), merge_from_fact_store wrong key (3.6), -1 sentinel return (5.1-5.3/10.5), config race (4.3), bare except (4.4), WyrdGraph no error handling (4.2), close() thread-local (6.3), config testing (9.2), eye/app testing (9.3) |
| **LOW** | 7 | FTS_TRIGGERS dead code (2.1), migration naming (2.2), re-import (2.3/2.4), merge_from_fact_store return shape (5.4), backup duplication (10.2), parameter order (10.3), minor risks (3.4/6.2/8.4/9.5) |

---

## Top 5 Priority Fixes

1. **CRITICAL:** Fix `__version__ = "2.9.0"` in `__init__.py` and `SCHEMA_VERSION = 8` in `schema.py`. Change `_init_db()` to not overwrite schema version if migrations have already set it.

2. **CRITICAL:** Add input validation to `fts_search()` — whitelist allowed tables to `{"memories", "knowledge", "saga_events"}` before interpolating into SQL.

3. **HIGH:** Fix WyrdGraph thread safety — add `threading.local()` connection pattern matching RunaMemory, or document that it's single-threaded only.

4. **HIGH:** Fix inconsistent edge dict keys in WyrdGraph — use `"relationship"` consistently (or `"relationship_type"`, but pick one).

5. **HIGH:** Add test coverage for `context_engineer.py` — the entire memory injection pipeline is untested.

---

*This audit was conducted with forensic rigor. Findings are cited to file, line, and exact code. The Well remembers what was, even as it becomes.*