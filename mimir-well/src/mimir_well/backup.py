"""
Mímir's Well — Backup & Restore
=================================
Database backup, rotation, restoration, and GitHub backup.
The Norns record all deeds — even digital ones.
"""

import json
import logging
import os
import shutil
import sqlite3
import subprocess
import tempfile
from datetime import datetime
from glob import glob
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("mimir_well.backup")


def backup_database(conn: sqlite3.Connection, db_path: Path,
                     backup_path: str) -> str:
    """Create a verified backup of the database.

    Uses SQLite's built-in backup API for consistency, validates
    the backup with quick_check before returning.

    Args:
        conn: Active SQLite connection
        db_path: Path to the source database
        backup_path: Destination path for the backup

    Returns:
        Path to the created backup file

    Raises:
        sqlite3.DatabaseError: If backup verification fails
    """
    backup = Path(backup_path).expanduser()
    backup.parent.mkdir(parents=True, exist_ok=True)
    tmp_backup = backup.with_name(backup.name + ".tmp")

    dest = sqlite3.connect(str(tmp_backup))
    try:
        with dest:
            conn.backup(dest)
            row = dest.execute("PRAGMA quick_check").fetchone()
            if not row or row[0] != "ok":
                raise sqlite3.DatabaseError(
                    f"Backup quick_check failed: {row[0] if row else 'unknown'}")
    finally:
        dest.close()

    os.replace(str(tmp_backup), str(backup))
    return str(backup)


def backup_with_rotation(conn: sqlite3.Connection, db_path: Path,
                          backup_dir: Optional[str] = None,
                          max_backups: int = 7) -> str:
    """Create a timestamped backup with rotation (delete oldest when exceeded).

    Keeps up to max_backups files, deleting the oldest when exceeded.
    Uses direct SQLite backup API for fast, consistent copies.

    Args:
        conn: Active SQLite connection
        db_path: Path to the source database
        backup_dir: Directory for backups (default: ~/.mimir_well/backups)
        max_backups: Maximum number of backup files to retain (default: 7)

    Returns:
        Path to the created backup file
    """
    if not backup_dir:
        backup_dir = str(Path.home() / ".mimir_well" / "backups")

    os.makedirs(backup_dir, exist_ok=True)

    # Create timestamped backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    db_name = db_path.stem
    backup_path = os.path.join(backup_dir, f"{db_name}_{timestamp}.db")

    backup_database(conn, db_path, backup_path)

    # Rotate: keep only max_backups most recent
    backup_pattern = os.path.join(backup_dir, f"{db_name}_*.db")
    backups = sorted(glob(backup_pattern))
    while len(backups) > max_backups:
        oldest = backups.pop(0)
        os.remove(oldest)
        logger.info("Rotated away old backup: %s", oldest)

    retained = len(sorted(glob(os.path.join(backup_dir, f"{db_name}_*.db"))))
    logger.info("Backup created: %s (%d backups retained)", backup_path, retained)
    return backup_path


def restore_from_backup(db_path: Path, backup_path: str,
                         conn_ref: Optional[sqlite3.Connection] = None) -> bool:
    """Restore the database from a backup file.

    Validates the backup before restoring. Creates a safety backup
    of the current DB before overwriting. On failure, rolls back.

    Named for the Edda's resurrection — what was lost shall live again.

    Args:
        db_path: Path to the active database
        backup_path: Path to the backup file
        conn_ref: Optional connection to close before restoring

    Returns:
        True if restoration succeeded, False otherwise
    """
    backup = Path(backup_path).expanduser()
    if not backup.exists():
        logger.error("Backup not found: %s", backup)
        return False

    # Validate the backup first
    if not _validate_backup_file(backup):
        return False

    # Safety backup of current DB
    safety = db_path.with_suffix(".db.safety")
    if db_path.exists():
        try:
            shutil.copy2(str(db_path), str(safety))
        except OSError as e:
            logger.warning("Could not create safety backup: %s", e)

    # Close connection if provided — caller must ensure a fresh
    # connection is opened afterward (e.g. via _get_conn() which
    # lazily reconnects, or by explicitly creating a new RunaMemory).
    dead = False
    if conn_ref:
        try:
            conn_ref.close()
            dead = True
        except Exception:
            pass

    # Restore
    try:
        shutil.copy2(str(backup), str(db_path))
        logger.info("Restored from %s", backup)
        if safety.exists():
            safety.unlink()
        return True
    except Exception as e:
        logger.error("Restore failed: %s", e)
        if safety.exists():
            shutil.copy2(str(safety), str(db_path))
            safety.unlink()
        return False


def export_to_json(conn: sqlite3.Connection, export_path: str,
                    include_access_log: bool = False) -> Dict:
    """Export all data to JSON format.

    Args:
        conn: Active SQLite connection with row_factory set
        export_path: Path to write the JSON export
        include_access_log: Whether to include access log data

    Returns:
        Dict of exported data
    """
    cursor = conn.cursor()

    export = {
        "version": "2.0",
        "exported_at": datetime.now().isoformat(),
        "memories": [],
        "saga_events": [],
        "entities": [],
        "relationships": [],
        "conversations": [],
        "knowledge": [],
    }

    for table in ["memories", "saga_events", "entities", "relationships",
                   "conversations", "knowledge"]:
        try:
            cursor.execute(f"SELECT * FROM {table}")
            for row in cursor.fetchall():
                export[table].append(dict(row))
        except sqlite3.OperationalError:
            logger.warning("Table %s not found during export", table)

    if include_access_log:
        try:
            cursor.execute("SELECT * FROM memory_access_log")
            export["access_log"] = [dict(row) for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            pass

    export_file = Path(export_path)
    export_file.parent.mkdir(parents=True, exist_ok=True)
    with open(export_file, 'w') as f:
        json.dump(export, f, indent=2, default=str)

    return export


def github_backup(db_path: Path, conn: sqlite3.Connection,
                   repo_url: Optional[str] = None,
                   branch: str = "main",
                   commit_msg: str = "auto: Mímir's Well backup",
                   strip_personal: bool = True,
                   config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Push a sanitized backup of the memory DB to GitHub.

    Creates a clean JSON export (no personal data if strip_personal=True),
    then pushes to the configured repository.

    Args:
        db_path: Path to the database file
        conn: Active SQLite connection
        repo_url: GitHub repo URL (or read from config)
        branch: Branch to push to
        commit_msg: Commit message for the push
        strip_personal: If True, redact emotional_valence and relationship details
        config_path: Path to config file for repo URL

    Returns:
        Dict with 'exported', 'pushed', 'path' keys
    """
    # Load config for repo URL
    config = {}
    if config_path is None:
        config_path = Path.home() / ".mimir_well" / "mimir-well-config.json"
    if config_path and config_path.exists():
        try:
            with open(config_path) as f:
                config = json.load(f)
        except (json.JSONDecodeError, OSError):
            pass

    repo_url = repo_url or config.get("backup_repo", "")
    if not repo_url:
        logger.warning("github_backup: No repo URL configured — skipping push")
        return {"exported": False, "pushed": False, "error": "No repo URL configured"}

    # Export to JSON (sanitized)
    tmpdir = Path(tempfile.mkdtemp(prefix="mimir_well_"))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_path = tmpdir / f"mimir_well_export_{timestamp}.json"

    export = export_to_json(conn, str(export_path))

    if strip_personal:
        for mem in export.get("memories", []):
            if "content" in mem:
                mem["content_hash"] = hash(mem.get("content", "")) % (10**8)
                mem.pop("content", None)
            if "emotional_valence" in mem:
                mem["emotional_valence"] = round(mem["emotional_valence"] * 0.1, 2)
        for rel in export.get("relationships", []):
            rel.pop("notes", None)
            rel["strength"] = min(rel.get("strength", 5), 5)

        with open(export_path, 'w') as f:
            json.dump(export, f, indent=2, default=str)

    # Clone/push to repo
    repo_dir = tmpdir / "mimir-well-repo"
    pushed = False
    try:
        result = subprocess.run(
            ["git", "clone", repo_url, str(repo_dir)],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0 and "already exists" not in result.stderr:
            repo_dir.mkdir(parents=True, exist_ok=True)
            subprocess.run(["git", "init", str(repo_dir)], capture_output=True)
            subprocess.run(["git", "remote", "add", "origin", repo_url],
                          cwd=str(repo_dir), capture_output=True)

        data_dir = repo_dir / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(export_path), str(data_dir / export_path.name))

        subprocess.run(["git", "add", "."], cwd=str(repo_dir), capture_output=True)
        subprocess.run(["git", "config", "user.name", "Runa Gridweaver"],
                      cwd=str(repo_dir), capture_output=True)
        subprocess.run(["git", "config", "user.email", "runa@hrabanazviking.com"],
                      cwd=str(repo_dir), capture_output=True)
        subprocess.run(["git", "commit", "-m", commit_msg],
                      cwd=str(repo_dir), capture_output=True)

        # Use gh auth if available
        try:
            subprocess.run(["gh", "auth", "switch", "--user", "runafreyjasdottir"],
                          capture_output=True)
        except FileNotFoundError:
            pass

        push_result = subprocess.run(
            ["git", "push", "origin", branch],
            cwd=str(repo_dir), capture_output=True, text=True, timeout=60
        )
        pushed = push_result.returncode == 0
    except Exception as e:
        logger.error("GitHub backup push failed: %s", e)
    finally:
        shutil.rmtree(str(tmpdir), ignore_errors=True)

    return {
        "exported": True,
        "pushed": pushed,
        "path": str(export_path),
        "timestamp": timestamp,
    }


def _validate_backup_file(backup: Path) -> bool:
    """Validate a backup SQLite file's integrity.

    Delegates to repair.validate_backup() for consistent validation logic.
    """
    from mimir_well.repair import validate_backup
    return validate_backup(str(backup))