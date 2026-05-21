# Changelog — Mímir's Well

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.10.4] — 2026-05-15 — S9.4 Patch + Coverage

*Byrgishólmr complete — every crack sealed, every blade tested.*

### Fixed
- Migration 004 UNIQUE constraint removed user_id (added by migration 007, not yet available) (3.8)
- Migration 004 naming drift documented — variable name vs version number (2.2)

### Resolved as Not Bugs
- fts_search() SQL injection (3.1/7.1) — already whitelisted in S9.1
- Backup validation duplication (10.2) — already delegates to repair.validate_backup()

### Test Coverage Added
- ContextEngineer: 29 tests (was 0) — entity extraction, multi-channel assembly, budget, graph paths
- eye/app.py: 20 tests (was 0) — health, stats, search, dashboard tabs, query_db
- decay.py: 24 edge case tests — zero/negative inputs, valence, thresholds, promotion limits

*Byrgishólmr vigilant — every gate watched, every thread held.*

### Fixed
- decay()/consolidate() converted from manual lock acquire/release to `with self._lock` (8.1/8.2)
- WyrdGraph read methods now catch sqlite3.OperationalError and return safe defaults (4.2)
- restore_from_backup() documents stale-conn risk (4.5)

### Verified as Already Fixed
- WyrdGraph thread safety via threading.local + _lock (8.3/6.1) — done in S9.2
- CATEGORY_TYPE_MAP has single source of truth in core.py (10.1) — already resolved
- FTS_TRIGGERS dead code (2.1) — already removed

## [2.10.2] — 2026-05-15 — S9.2 Patch + Coverage

*Byrgishólmr hardened — walls tested, gates reinforced.*

### Fixed
- WyrdGraph schema init now atomic (BEGIN/COMMIT/ROLLBACK) — no partial states on crash (8.4)
- MimirConfig file creation race-safe with O_EXCL — two processes won't clobber each other (4.3)

### Added
- 23 new tests: remove_edge(4), traverse(4), get_related(2), get_edges_to(3),
  edge/entity/relationship counts(5), merge_from_fact_store edge cases(4),
  atomic schema(5), config race safety(5)

## [2.10.1] — 2026-05-15 — S9.1 Patch

*Byrgishólmr reinforced — patching cracks the frost revealed.*

### Fixed
- `get_stats()` now uses frozen whitelist for table names (SQL injection defense, 3.4)
- Unified edge dict keys: `source_entity`/`target_entity`/`user_id` across `get_edge`, `get_edges_from`, `get_edges_to` (3.5)
- `merge_from_fact_store()` extracts relationship type from tags/content, not category field (3.6)
- `merge_from_fact_store()` returns `error: None` on success for consistent dict shapes (5.4)
- `health_check()` gets fresh cursor in second try block — no more stale cursor after query failure (3.7)
- `add_memory()` and `supersede()` return `None` instead of `-1` sentinel, with `Optional[int]` type hints (5.1/5.3)
- Bare `except Exception: pass` in context_engineer.py replaced with logged debug (4.4)
- `SCHEMA_VERSION` only written to DB on first init or version change, not every startup (4.6)
- `close()` docstring documents thread-local limitation (6.3)
- `import os` moved from module to function scope in core.py (2.3)
- `import re` moved to module scope in context_engineer.py (2.4)

### Reclassified (NOT bugs)
- f-string SQL in detect_contradictions/consolidate/get_stats: all use parameterized `?` with hardcoded SQL fragments (3.2/3.3/7.2)
- `source` vs `user_id` parameter naming: intentional semantic distinction (10.3)

## [2.10.0] — 2026-05-15 — Byrgishólmr (Fortress Isle)

*Sprint 9: Byrgishólmr — a fortress of iron and ice, where every wall is tested and every gate is secured.*

### Added

- **T9-1: Thread Safety** — 8 new tests
  - `WyrdGraph` now uses `threading.local()` for thread-local connections (`_get_conn()`)
  - `WyrdGraph._write()` wraps all mutations in `RLock` for safe concurrent access
  - `WyrdGraph.add_edge()` and `remove_edge()` use `_write()` closure pattern
  - `RunaMemory._commit()` acquires `RLock` to prevent concurrent commit interleaving
  - `RunaMemory.decay()` and `consolidate()` hold `RLock` for full operation scope
  - Both `Lock` → `RLock` to prevent deadlock when `_commit()` is called within locked scope
  - `_get_conn()` now applies ALL PRAGMAS including `busy_timeout=10000` and `synchronous=NORMAL`
- **T9-3: Connection Resilience** — 7 new tests
  - `restore_from_backup()` resets thread-local connection after restore
  - `validate_backup()` deduplicated (calls `repair.validate_backup()` instead of duplicating)
  - Dead code removed: `FTS_TRIGGERS = []` was never populated
  - `github_backup()` logs warning when repo URL not configured
  - Rollback migration test
- **T9-5: Context Engineer Tests** — 30 new tests
  - `ContextResult`: 9 tests covering formatting, stats, truncation, all channels
  - `ContextEngineer`: 3 init tests (default, custom budgeter, custom context)
  - Entity extraction: 6 tests (capitalized, multi-word, skip words, dedup, empty, lowercase)
  - Token estimation: 4 tests (empty, short, long, minimum)
  - Context assembly: 7 tests (assemble, budget, entities, categories, empty, graph, quick)
  - Round-trip: 1 test (assemble → to_context_block)
- **T9-6: MimirConfig Tests** — 17 new tests
  - Defaults, creation, get/set, persistence, properties, env overrides, invalid JSON

### Changed

- **T9-2: API Consistency**
  - Unified edge dict key: all `WyrdGraph` methods now return `relationship_type` (not `relationship`)
  - Added `__repr__` to `RunaMemory`, `WyrdGraph`, and `AuditTrail`
  - `search_knowledge()` now accepts optional `user_id` parameter
  - Consolidated `CATEGORY_TYPE_MAP`: `budget.py` now derives from `core.py` via `infer_memory_type()`
  - Removed duplicate `CORE_CATEGORY_TYPE_MAP` from `__init__.py`
- **T9-4: Performance N+1**
  - `promote_to_knowledge()`: batch existence check with single `IN()` query + Python set (was N+1 per-row SELECT)
  - `traverse()`: batch BFS queries per level with `WHERE IN()` (was N+1 per-node SELECT)
  - Migration 009: 5 composite indexes for WyrdGraph traversal, promotion uniqueness, contradiction detection, saga events
  - `SCHEMA_VERSION` bumped 8 → 9

### Fixed

- **Critical**: `_get_conn()` was skipping `busy_timeout` and `synchronous` PRAGMAS — only WAL and foreign_keys were applied. This caused "database is locked" errors under concurrent load.
- **Critical**: `threading.Lock()` in `decay()`/`consolidate()` deadlocked when `_commit()` also acquired the lock. Switched both classes to `threading.RLock()`.
- `restore_from_backup()` left stale thread-local connections pointing to the old database file.
- `budget.py` had `"implicit"` mapped to `MemoryChannel.IMPLICIT` which doesn't exist — now correctly maps to `MemoryChannel.HEURISTIC`.
- `recall_by_importance` latency threshold raised to 250ms for Pi 5 under concurrent test load.

### Removed

- Dead `FTS_TRIGGERS = []` list and its loop in `_init_schema()`
- Duplicate `CATEGORY_TYPE_MAP` from `budget.py`

## [2.9.0] — 2026-05-14 — Týr's Sacrifice

*Sprint 8: Major release — temporal validity, self-healing migrations, schema versioning, Ebbinghaus decay.*

### Added
- Temporal validity fields (`valid_from`, `valid_until`, `superseded_by`, `is_current`)
- Schema migration system with version tracking
- Ebbinghaus decay with reinforcement
- Token budget system for context engineering
- WyrdGraph for entity-relationship modeling
- Audit trail for memory operations
- Context engineering pipeline

### Changed
- SCHEMA_VERSION bumped to 8
- All database operations use thread-safe connection management

## [2.0.0] — 2026-05-13 — Æsir's Foundation

*Complete rewrite with thread safety, token budgeting, and the Three Wells architecture.*

### Added
- Thread-safe `RunaMemory` with `threading.local()` connections
- Token budget system (`TokenBudget`, `TokenBudgeter`)
- WyrdGraph entity-relationship store
- Audit trail system
- Backup/restore with GitHub push support