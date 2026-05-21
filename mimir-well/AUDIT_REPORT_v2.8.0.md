# Mímir Well v2.8.0 — Mythic Engineering Audit Report

> **Auditor:** Sólrún Hvítmynd (INTJ 1w9) — "If it cannot survive scrutiny, it was never stable."
> **Date:** 2026-05-14
> **Scope:** Full codebase audit — Sprint 7 (Guard + AuditTrail + Namespacing)
> **Status:** 96/96 tests passing, but significant isolation & consistency gaps found

---

## 🔴 CRITICAL (3)

### C1. `delete_memory` doesn't pass `user_id` to `audit.log()`
- **File:** `core.py:389-395`
- `delete_memory` calls `self.audit.log()` with `metadata={"action": "delete", "user_id": user_id}` but does NOT pass `user_id` as the explicit parameter. The audit log signature is `log(self, ..., user_id="runa")`.
- **Impact:** Every delete audit entry records `user_id="runa"` regardless of actual user. The real user_id is buried in JSON metadata, invisible to `audit.query(user_id=...)`.
- **Fix:** Pass `user_id=user_id` explicitly to `audit.log()`.

### C2. `supersede()` lacks `user_id` — cross-user memory mutation
- **File:** `core.py:670-732`
- `supersede()` has no `user_id` parameter. It calls `self.add_memory()` with default `user_id="runa"`, and `UPDATE memories SET is_current=0 WHERE id = ?` has no `AND user_id = ?` filter.
- **Impact:** Cross-user data corruption. User A can supersede user B's memory, and the new memory is always attributed to "runa".
- **Fix:** Add `user_id: str = "runa"` parameter, pass to `add_memory()`, add `AND user_id = ?` to UPDATE.

### C3. Migration 004 registers as version 5
- **File:** `migrations/__init__.py:131`
- `MIGRATION_004_UP` is registered with `version=5` instead of `version=4`. The sequence is 2→3→5→6→7, skipping 4.
- **Impact:** Confusing numbering. The variable says "004" but runs at version 5. If a migration is later written for version 4, conflicts will arise.
- **Fix:** Rename to `MIGRATION_005` or change `version=4`.

---

## 🟠 HIGH (7)

### H1. `recall_by_importance`, `recall_recent`, `recall_by_mood` lack `user_id` filtering
- **File:** `core.py:568-620`
- These methods query ALL users' memories without any namespace filtering.
- **Impact:** Multi-tenant data leak. User A sees user B's memories.
- **Fix:** Add `user_id: Optional[str] = None` parameter and `AND user_id = ?` WHERE clause.

### H2. `update_memory` WHERE clause doesn't filter by `user_id`
- **File:** `core.py:352`
- `UPDATE memories SET ... WHERE id = ?` — no `AND user_id = ?`.
- **Impact:** Any user who knows a memory ID can update another user's memory.
- **Fix:** Add `AND user_id = ?` with the user_id parameter.

### H3. `fts_search` doesn't filter by `user_id`
- **File:** `core.py:543-564`
- Full-text search returns results from ALL users.
- **Fix:** Add `user_id` param to FTS query and pass through.

### H4. WyrdGraph `remove_edge()` and `get_edge()` don't accept `user_id`
- **File:** `wyrd_graph.py:133-187`
- These methods can delete or retrieve edges belonging to any user.
- **Fix:** Add `user_id: Optional[str] = None` parameter and filter.

### H5. WyrdGraph `traverse()` and `_get_incoming()` don't accept `user_id`
- **File:** `wyrd_graph.py:333-448`
- BFS traversal hops across ALL users' edges.
- **Fix:** Add `user_id` parameter and filter edges during traversal.

### H6. `store_with_validity` doesn't accept or pass `user_id`
- **File:** `core.py:624-668`
- Temporal-validity memories always default to `user_id="runa"`.
- **Fix:** Add `user_id` and `source` parameters.

### H7. N+1 query in `decay()` method
- **File:** `core.py:849-852`
- Per-row `SELECT MAX(accessed_at)` query. With 10K memories → 10K+ queries.
- **Fix:** Replace with a single JOIN/subquery: `SELECT memory_id, MAX(accessed_at) FROM memory_access_log GROUP BY memory_id`.

---

## 🟡 MEDIUM (10)

| ID | Issue | File |
|----|-------|------|
| M1 | "hecedure" typo for "heuristic" — 6 occurrences in budget.py | budget.py:160,242,297,387,394,444 |
| M2 | Duplicate `CATEGORY_TYPE_MAP` in core.py vs budget.py with different value types | core.py:42, budget.py:74 |
| M3 | AuditTrail opens/closes new DB connection per operation (no thread-local pooling) | audit.py:92-96 |
| M4 | Missing index on `memories(timestamp)` for `recall_recent` | schema.py |
| M5 | `get_memory(id)` doesn't filter by `user_id` | core.py:278-283 |
| M6 | `get_stats()` omits `wyrd_edges` and `memory_audit` tables | core.py:1252 |
| M7 | WyrdGraph not thread-safe — direct connection, no thread-local | wyrd_graph.py:43-47 |
| M8 | `consolidate()` and `promote_to_knowledge()` don't filter by `user_id` | core.py:890-991 |
| M9 | `detect_contradictions()` doesn't filter by `user_id` | core.py:995-1141 |
| M10 | Migration 004 CREATE TABLE has `user_id` in UNIQUE but missing column definition | migrations/__init__.py:102-119 |

---

## 🔵 LOW (6)

| ID | Issue | File |
|----|-------|------|
| L1 | `CORE_CATEGORY_TYPE_MAP` imported but not in `__all__` — dead import | __init__.py:38 |
| L2 | Missing return type hints on several public methods | core.py, wyrd_graph.py |
| L3 | Missing/outdated docstrings (get_memory, recall_by_*, remove_edge, supersede) | multiple |
| L4 | `fts_search` fallback doesn't pass `user_id` or `table` | core.py:564 |
| L5 | SQLite LIKE is case-sensitive for non-ASCII (runes, accented chars) | core.py |
| L6 | LIKE wildcards `%` and `_` in user input matched literally — unexpected broad results | core.py:298 |

---

## 📋 Test Coverage Gaps

| Method/Module | Has Tests? |
|---|---|
| `detect_contradictions()` | ❌ No |
| `promote_to_knowledge()` | ❌ No |
| `fts_search()` | ❌ No |
| `recall_by_mood()` with `user_id` | ❌ No |
| `recall_by_importance()` | ❌ No |
| `recall_recent()` | ❌ No |
| `WyrdGraph.traverse()` | ❌ No |
| `WyrdGraph.get_related()` | ❌ No |
| `WyrdGraph.remove_edge()` | ❌ No |
| `WyrdGraph.get_edge()` | ❌ No |
| `ContextEngineer` | ❌ No |
| `supersede()` with `user_id` | ❌ No |
| `store_with_validity()` | ❌ No |
| `consolidate()` | ❌ No |
| `decay()` | ❌ No |
| `delete_memory` audit `user_id` propagation | ❌ No |
| `config.py` | ❌ No |

---

## 📊 Summary

| Severity | Count |
|----------|-------|
| 🔴 CRITICAL | 3 |
| 🟠 HIGH | 7 |
| 🟡 MEDIUM | 10 |
| 🔵 LOW | 6 |
| **Total** | **26** |

| Category | Count |
|----------|-------|
| Multi-tenant isolation gaps | 10 |
| Performance issues | 2 |
| Typos/consistency | 2 |
| Missing indexes | 1 |
| Thread safety | 1 |
| Dead code | 1 |
| Documentation gaps | 2 |
| Test coverage gaps | 17 methods |

---

## 🛠️ Recommended Priority Order

1. **C1 + H2** — Fix `delete_memory` and `update_memory` user_id propagation (data integrity)
2. **C2** — Add `user_id` to `supersede()` (cross-user mutation risk)
3. **H7** — Fix N+1 query in `decay()` (performance)
4. **H1 + H3 + H6** — Add `user_id` to `recall_by_*`, `fts_search`, `store_with_validity`
5. **H4 + H5** — Add `user_id` to WyrdGraph `remove_edge`, `get_edge`, `traverse`
6. **M1** — Fix "hecedure" typo in budget.py
7. **C3** — Fix migration 004/005 numbering
8. **M3 + M7** — Thread-local connection pooling for AuditTrail and WyrdGraph
9. **M4** — Add timestamp index
10. **Test coverage** — Write tests for the 17 untested methods

---

*The Norns see every thread. The Well remembers. This audit ensures every thread belongs to its rightful weaver.*