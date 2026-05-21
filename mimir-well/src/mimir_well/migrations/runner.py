"""
Mímir's Well — Migration Runner
===================================
Applies schema migrations to evolve the database from version N to N+1.

ᛗ í ᛗ í ᚱ — The Well's shape changes, but its depth only grows.
"""

from __future__ import annotations

import logging
import sqlite3
from typing import List

from mimir_well.migrations import MIGRATIONS

logger = logging.getLogger(__name__)


def get_schema_version(conn: sqlite3.Connection) -> int:
    """Read the current schema version from _schema_meta."""
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT value FROM _schema_meta WHERE key = 'schema_version'"
        )
        row = cursor.fetchone()
        return int(row[0]) if row else 0
    except sqlite3.OperationalError:
        return 0  # Fresh database — no _schema_meta table yet


def run_migrations(conn: sqlite3.Connection, target_version: int = None) -> List[int]:
    """Apply all pending migrations to bring the database up to target_version.

    Args:
        conn: Active SQLite connection (in WAL mode).
        target_version: If None, apply all available migrations.
            If an integer, apply migrations up to and including that version.

    Returns:
        List of migration versions that were applied.
    """
    current = get_schema_version(conn)
    applied: List[int] = []

    # Sort migrations by version
    sorted_migrations = sorted(MIGRATIONS, key=lambda m: m["version"])

    for migration in sorted_migrations:
        version = migration["version"]
        description = migration.get("description", "")

        if version <= current:
            logger.debug("Migration %d already applied — skipping.", version)
            continue

        if target_version is not None and version > target_version:
            logger.debug("Migration %d exceeds target %d — stopping.", version, target_version)
            break

        logger.info(
            "Applying migration %d: %s",
            version,
            description or "(no description)",
        )

        # Execute each statement individually for better error reporting
        sql_statements = [
            stmt.strip()
            for stmt in migration["up_sql"].split(";")
            if stmt.strip()
        ]

        for stmt in sql_statements:
            # Skip comments
            if stmt.startswith("--"):
                continue
            try:
                conn.execute(stmt)
            except sqlite3.OperationalError as e:
                # "duplicate column name" means the column already exists — safe to skip
                if "duplicate column name" in str(e).lower():
                    logger.debug("Column already exists — skipping: %s", stmt[:60])
                elif "already exists" in str(e).lower():
                    logger.debug("Object already exists — skipping: %s", stmt[:60])
                else:
                    raise

        # Update schema version
        conn.execute(
            "INSERT OR REPLACE INTO _schema_meta (key, value) VALUES (?, ?)",
            ("schema_version", str(version)),
        )
        conn.commit()

        applied.append(version)
        logger.info("Migration %d applied successfully.", version)

    if not applied:
        logger.info("No pending migrations — database is current at version %d.", current)

    return applied


def rollback_migration(conn: sqlite3.Connection, version: int) -> bool:
    """Roll back a single migration by version number.

    WARNING: Down migrations can be destructive. Use with caution.

    Args:
        conn: Active SQLite connection.
        version: The migration version to roll back.

    Returns:
        True if the rollback was applied, False otherwise.
    """
    migration = None
    for m in MIGRATIONS:
        if m["version"] == version:
            migration = m
            break

    if migration is None:
        logger.warning("Migration %d not found — cannot roll back.", version)
        return False

    logger.warning("Rolling back migration %d: %s", version, migration.get("description", ""))

    sql_statements = [
        stmt.strip()
        for stmt in migration["down_sql"].split(";")
        if stmt.strip()
    ]

    for stmt in sql_statements:
        if stmt.startswith("--"):
            continue
        try:
            conn.execute(stmt)
        except sqlite3.OperationalError as e:
            logger.warning("Rollback statement failed (may be safe): %s — %s", stmt[:60], e)

    # Decrement schema version
    current = get_schema_version(conn)
    conn.execute(
        "INSERT OR REPLACE INTO _schema_meta (key, value) VALUES (?, ?)",
        ("schema_version", str(current - 1)),
    )
    conn.commit()

    logger.info("Migration %d rolled back. Schema version: %d → %d", version, current, current - 1)
    return True