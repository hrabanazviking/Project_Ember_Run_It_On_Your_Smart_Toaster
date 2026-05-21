# Sprint 8 — Mímir Well Hardening Plan

> **Architect:** Rúnhild Svartdóttir | **Auditor:** Sólrún Hvítmynd
> **Goal:** Resolve all 26 audit findings from v2.8.0, reach v2.9.0
> **Philosophy:** Fix the foundation before building higher. Isolation first, performance second, polish third.

---

## Phase 1: Critical Fixes (T8-1)

**Goal:** Eliminate data corruption vectors — user_id must flow through ALL write paths.

| Task | Finding | What | Files |
|------|---------|------|-------|
| T8-1a | C1 | Fix `delete_memory` to pass `user_id` explicitly to `audit.log()` | core.py |
| T8-1b | H2 | Add `AND user_id = ?` to `update_memory` WHERE clause | core.py |
| T8-1c | C2 | Add `user_id` param to `supersede()` — pass to `add_memory()`, add `AND user_id = ?` to UPDATE | core.py |
| T8-1d | H6 | Add `user_id` + `source` params to `store_with_validity()` | core.py |
| T8-1e | M5 | Add `user_id` param + filter to `get_memory()` | core.py |

**Verify:** Run existing 96 tests + new test file `test_isolation.py` confirming:
- delete audit entries record correct user_id
- update rejects cross-user mutation
- supersede creates new memories with correct user_id
- get_memory respects user_id filter

---

## Phase 2: Query Isolation (T8-2)

**Goal:** All read/query paths respect user_id namespace. No cross-tenant data leaks.

| Task | Finding | What | Files |
|------|---------|------|-------|
| T8-2a | H1 | Add `user_id` param to `recall_by_importance()`, `recall_recent()`, `recall_by_mood()` | core.py |
| T8-2b | H3 | Add `user_id` param to `fts_search()` + fallback path | core.py |
| T8-2c | M8 | Add `user_id` param to `consolidate()` and `promote_to_knowledge()` | core.py |
| T8-2d | M9 | Add `user_id` param to `detect_contradictions()` | core.py |

**Verify:** `test_isolation.py` — every method returns only the requesting user's data.

---

## Phase 3: WyrdGraph Isolation (T8-3)

**Goal:** WyrdGraph edges and traversals are user-namespaced.

| Task | Finding | What | Files |
|------|---------|------|-------|
| T8-3a | H4 | Add `user_id` to `remove_edge()` and `get_edge()` | wyrd_graph.py |
| T8-3b | H5 | Add `user_id` to `traverse()` and `_get_incoming()` — filter edges during BFS | wyrd_graph.py |
| T8-3c | M7 | Make WyrdGraph thread-safe — use `threading.local()` for DB connections | wyrd_graph.py |

**Verify:** Test WyrdGraph isolation — user A's traversal never includes user B's edges.

---

## Phase 4: Performance & Schema Fixes (T8-4)

**Goal:** Fix the N+1 query, missing indexes, migration numbering, and typos.

| Task | Finding | What | Files |
|------|---------|------|-------|
| T8-4a | H7 | Replace N+1 `decay()` per-row query with single JOIN/subquery | core.py |
| T8-4b | M4 | Add index on `memories(timestamp)` for `recall_recent` | schema.py, migration 008 |
| T8-4c | M6 | Add `wyrd_edges` and `memory_audit` to `get_stats()` table list | core.py |
| T8-4d | C3 | Rename migration 004 to 005 (or change version=4) | migrations/__init__.py |
| T8-4e | M1 | Fix "hecedure" → "heuristic" in budget.py (6 occurrences) | budget.py |
| T8-4f | M2 | Resolve `CATEGORY_TYPE_MAP` duplication — keep budget.py's `MemoryChannel` version, remove core.py's | core.py, budget.py, __init__.py |
| T8-4f | M10 | Move `user_id` column definition into migration 004's CREATE TABLE (for fresh DBs) | migrations/__init__.py |
| T8-4g | L1 | Remove dead `CORE_CATEGORY_TYPE_MAP` import from `__init__.py` | __init__.py |

**Verify:** Full test suite passes, `get_stats()` includes all tables, LIKE queries use escaped wildcards.

---

## Phase 5: Thread Safety & Architecture (T8-5)

**Goal:** AuditTrail and WyrdGraph use thread-local connection pooling.

| Task | Finding | What | Files |
|------|---------|------|-------|
| T8-5a | M3 | Refactor AuditTrail to use `threading.local()` for DB connections | audit.py |
| T8-5b | M7 | (carried from T8-3c) WyrdGraph thread-local connection pool | wyrd_graph.py |
| T8-5c | L2 | Add return type hints to all public methods | core.py, wyrd_graph.py, audit.py |
| T8-5d | L3 | Update docstrings for user_id-filtered methods | core.py, wyrd_graph.py |

**Verify:** Thread-safety test — spawn 10 threads, concurrent reads/writes, no corruption.

---

## Phase 6: Test Coverage Expansion (T8-6)

**Goal:** Cover the 17 untested methods discovered in the audit.

| Test File | Covers |
|-----------|--------|
| `test_isolation.py` | All user_id filtering — CRUD, recall, fts, wyrd_graph |
| `test_supersede.py` | `supersede()` with user_id, cross-user rejection |
| `test_decay_performance.py` | `decay()` with bulk memories, verify single-query |
| `test_wyrd_traverse.py` | `traverse()`, `get_related()`, `remove_edge()`, `get_edge()` |
| `test_recall_methods.py` | `recall_by_importance()`, `recall_recent()`, `recall_by_mood()` |
| `test_consolidate.py` | `consolidate()`, `promote_to_knowledge()`, `detect_contradictions()` |
| `test_context_engineer.py` | `ContextEngineer` basic functionality |
| `test_budget_channels.py` | Verify "heuristic" channel key (after M1 fix) |

**Target:** 96 → 140+ tests, all passing.

---

## Phase 7: Version Bump & Release (T8-7)

| Task | What |
|------|------|
| T8-7a | Bump `pyproject.toml` and `__init__.py` to v2.9.0 |
| T8-7b | Update `CHANGELOG.md` with all Sprint 8 fixes |
| T8-7c | Update `README.md` with user_id namespacing docs |
| T8-7d | Final full test suite run (140+ tests) |
| T8-7e | Git tag `v2.9.0`, push to GitHub |

---

## Dependency Order

```
Phase 1 (Critical fixes)
  ├─ T8-1a delete_memory audit user_id
  ├─ T8-1b update_memory WHERE clause
  ├─ T8-1c supersede user_id
  ├─ T8-1d store_with_validity user_id
  └─ T8-1e get_memory user_id
     │
Phase 2 (Read isolation)
  ├─ T8-2a recall_by_* user_id
  ├─ T8-2b fts_search user_id
  ├─ T8-2c consolidate/promote user_id
  └─ T8-2d detect_contradictions user_id
     │
Phase 3 (WyrdGraph isolation)
  ├─ T8-3a remove_edge/get_edge user_id
  ├─ T8-3b traverse/_get_incoming user_id
  └─ T8-3c thread-local WyrdGraph
     │
Phase 4 (Performance & schema)
  ├─ T8-4a decay() N+1 fix
  ├─ T8-4b timestamp index
  ├─ T8-4c get_stats() tables
  ├─ T8-4d migration numbering
  ├─ T8-4e hecedure typo
  ├─ T8-4f CATEGORY_TYPE_MAP dedup
  ├─ T8-4g migration 004 user_id column
  └─ T8-4h dead import cleanup
     │
Phase 5 (Architecture)
  ├─ T8-5a AuditTrail thread-local
  ├─ T8-5b WyrdGraph thread-local
  ├─ T8-5c type hints
  └─ T8-5d docstrings
     │
Phase 6 (Tests)
  └─ All new test files
     │
Phase 7 (Release)
  └─ v2.9.0 bump, changelog, push
```

---

## Risk Notes

- **Phase 1-2 MUST complete before Phase 6 tests** — tests verify isolation that doesn't exist yet
- **T8-4e (hecedure typo)** may break external consumers if they reference the old key — check for usages first
- **T8-3c (WyrdGraph thread-local)** changes internal architecture — test thoroughly
- **T8-5a (AuditTrail thread-local)** same — connection pooling change needs concurrency testing
- **Migration 008** needed for timestamp index — requires schema v8 bump

*The threads are laid. The Norns are ready. We weave now.*