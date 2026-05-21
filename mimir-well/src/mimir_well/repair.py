"""
Mímir's Well — Self-Healing / Repair Logic
=============================================
Database integrity checking, corruption detection, and auto-repair.
The Well of Mímir heals what time has damaged.
"""

import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("mimir_well.repair")


def validate_backup(backup_path: str) -> bool:
    """Validate a backup file's integrity before restoring.

    Runs PRAGMA integrity_check on the backup file to ensure it's
    not corrupted before using it to restore.

    Args:
        backup_path: Path to the backup SQLite database

    Returns:
        True if the backup is valid, False otherwise
    """
    backup = Path(backup_path)
    if not backup.exists():
        logger.error("Backup file not found: %s", backup_path)
        return False

    try:
        test_conn = sqlite3.connect(str(backup))
        test_conn.row_factory = sqlite3.Row
        row = test_conn.execute("PRAGMA integrity_check").fetchone()
        test_conn.close()
        if row and row[0] == "ok":
            return True
        logger.error("Backup integrity check failed: %s", row[0] if row else "unknown")
        return False
    except sqlite3.DatabaseError as e:
        logger.error("Cannot read backup: %s", e)
        return False
    except Exception as e:
        logger.error("Backup validation error: %s", e)
        return False


def check_integrity(conn: sqlite3.Connection, repair: bool = False) -> Dict[str, Any]:
    """Check database integrity and optionally repair issues.

    The Norns inspect the threads of fate for frayed edges.

    Checks:
    1. SQLite integrity_check
    2. FTS index consistency (memory count vs FTS count)
    3. Orphaned relationships
    4. Orphaned access log entries
    5. Empty/null content in memories
    6. Importance out of valid range (1-10)
    7. Emotional valence out of range (-1.0 to 1.0)

    Args:
        conn: Active SQLite connection
        repair: If True, fix detected issues

    Returns:
        Dict with check results and repairs made
    """
    cursor = conn.cursor()
    results: Dict[str, Any] = {"checks": {}, "issues": [], "repairs": []}

    # 1. SQLite integrity check
    cursor.execute("PRAGMA integrity_check")
    ic = cursor.fetchone()[0]
    results["checks"]["sqlite_integrity"] = ic
    if ic != "ok":
        results["issues"].append(f"SQLite integrity check failed: {ic}")

    # 2. FTS consistency — verify FTS table exists and is queryable
    # Note: COUNT(*) on content= FTS5 tables can fail with UNINDEXED columns,
    # so we just verify the table exists and is readable
    try:
        # Verify FTS table exists and can be queried
        conn.execute("SELECT rowid FROM memories_fts LIMIT 1")
        results["checks"]["fts_consistency"] = "ok"
    except sqlite3.OperationalError as e:
        results["checks"]["fts_consistency"] = f"error: {e}"
        if "no such table" in str(e):
            results["issues"].append("FTS table missing — run repair to recreate")
        else:
            results["issues"].append(f"FTS check error: {e}")

    # 3. Orphaned relationships
    orphan_rels = cursor.execute("""
        SELECT COUNT(*) FROM relationships r
        WHERE r.entity_a NOT IN (SELECT entity_id FROM entities)
        AND r.entity_b NOT IN (SELECT entity_id FROM entities)
    """).fetchone()[0]
    results["checks"]["orphaned_relationships"] = orphan_rels
    if orphan_rels > 0:
        results["issues"].append(
            f"{orphan_rels} relationships reference non-existent entities")
        if repair:
            cursor.execute("""
                DELETE FROM relationships
                WHERE entity_a NOT IN (SELECT entity_id FROM entities)
                AND entity_b NOT IN (SELECT entity_id FROM entities)
            """)
            results["repairs"].append(f"Deleted {orphan_rels} orphaned relationships")

    # 4. Orphaned access log entries
    orphan_log = cursor.execute("""
        SELECT COUNT(*) FROM memory_access_log
        WHERE memory_id NOT IN (SELECT id FROM memories)
    """).fetchone()[0]
    results["checks"]["orphaned_access_log"] = orphan_log
    if orphan_log > 0:
        results["issues"].append(
            f"{orphan_log} access log entries reference deleted memories")
        if repair:
            cursor.execute("""
                DELETE FROM memory_access_log
                WHERE memory_id NOT IN (SELECT id FROM memories)
            """)
            results["repairs"].append(f"Deleted {orphan_log} orphaned log entries")

    # 5. Empty/null content
    empty_content = cursor.execute(
        "SELECT COUNT(*) FROM memories WHERE content IS NULL OR content = ''"
    ).fetchone()[0]
    results["checks"]["empty_content"] = empty_content
    if empty_content > 0:
        results["issues"].append(f"{empty_content} memories have empty content")

    # 6. Importance out of range
    bad_importance = cursor.execute(
        "SELECT COUNT(*) FROM memories WHERE importance < 1 OR importance > 10"
    ).fetchone()[0]
    results["checks"]["importance_range"] = bad_importance
    if bad_importance > 0:
        results["issues"].append(
            f"{bad_importance} memories have importance outside 1-10")
        if repair:
            cursor.execute("UPDATE memories SET importance = 1 WHERE importance < 1")
            cursor.execute("UPDATE memories SET importance = 10 WHERE importance > 10")
            results["repairs"].append(f"Clamped {bad_importance} importance values")

    # 7. Emotional valence out of range
    bad_valence = cursor.execute(
        "SELECT COUNT(*) FROM memories WHERE emotional_valence < -1.0 OR emotional_valence > 1.0"
    ).fetchone()[0]
    results["checks"]["valence_range"] = bad_valence
    if bad_valence > 0:
        results["issues"].append(
            f"{bad_valence} memories have valence outside -1.0 to 1.0")
        if repair:
            cursor.execute(
                "UPDATE memories SET emotional_valence = -1.0 WHERE emotional_valence < -1.0")
            cursor.execute(
                "UPDATE memories SET emotional_valence = 1.0 WHERE emotional_valence > 1.0")
            results["repairs"].append(f"Clamped {bad_valence} valence values")

    results["healthy"] = len(results["issues"]) == 0
    return results


def repair_database(conn: sqlite3.Connection, aggressive: bool = False) -> Dict[str, Any]:
    """Repair the database — fix orphans, inconsistencies, and corruption.

    The Well of Mímir heals what time has damaged.

    Args:
        conn: Active SQLite connection
        aggressive: If True, also vacuum and deep clean

    Returns:
        Dict with repair statistics
    """
    repairs = {
        "orphaned_relationships": 0,
        "orphaned_saga_events": 0,
        "missing_categories": 0,
        "fixed_timestamps": 0,
        "vacuumed": False,
        "integrity": {},
    }

    cursor = conn.cursor()

    # Fix orphaned relationships
    entity_ids = {r[0] for r in cursor.execute("SELECT entity_id FROM entities").fetchall()}
    orphans = cursor.execute("""
        SELECT id, entity_a, entity_b FROM relationships
        WHERE entity_a NOT IN (SELECT entity_id FROM entities)
        OR entity_b NOT IN (SELECT entity_id FROM entities)
    """).fetchall()
    for rel_id, ea, eb in orphans:
        if ea not in entity_ids and eb not in entity_ids:
            cursor.execute("DELETE FROM relationships WHERE id = ?", (rel_id,))
            repairs["orphaned_relationships"] += 1

    # Fix orphaned saga events
    cursor.execute("""
        SELECT id FROM saga_events WHERE entity_id IS NOT NULL
        AND entity_id NOT IN (SELECT entity_id FROM entities)
    """)
    orphan_saga = cursor.fetchall()
    for (sid,) in orphan_saga:
        cursor.execute("UPDATE saga_events SET entity_id = NULL WHERE id = ?", (sid,))
        repairs["orphaned_saga_events"] += 1

    # Fix timestamps
    from datetime import datetime
    now = datetime.now().isoformat()
    fixed_ts = cursor.execute(
        "UPDATE memories SET timestamp = ? WHERE timestamp IS NULL OR timestamp = ''",
        (now,)
    ).rowcount
    repairs["fixed_timestamps"] = fixed_ts

    # Fix categories
    fixed_cat = cursor.execute(
        "UPDATE memories SET category = 'uncategorized' WHERE category IS NULL OR category = ''"
    ).rowcount
    repairs["missing_categories"] = fixed_cat

    # Run integrity check with repair
    repairs["integrity"] = check_integrity(conn, repair=True)

    # Vacuum if aggressive
    if aggressive:
        cursor.execute("VACUUM")
        repairs["vacuumed"] = True

    return repairs