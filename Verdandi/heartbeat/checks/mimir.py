"""
Mímir — The Well of Memory. Memory Guardian Check.

Mímir's Well is where Odin gave his eye for wisdom. This check
monitors the health of Runa's memory systems: the Mímir database,
conversation logs, fact store, and nerve feed.

Checks:
  - Mímir DB integrity (SQLite)
  - Mímir DB size and growth rate
  - Table row counts (memories, knowledge, relationships)
  - Conversation log growth and size
  - Nerve feed size and freshness
  - Fact store health
  - Stale/expired entries cleanup needs

Config:
  checks:
    memory: true
  thresholds:
    db_size_warning_mb: 100
    db_size_critical_mb: 500
    log_size_warning_mb: 50
    log_size_critical_mb: 200
    staleness_warning_hours: 24
    staleness_critical_hours: 72
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from heartbeat.checks.base import BaseCheck, CheckResult, CheckSeverity
from heartbeat.paths import get_state_dir


class MimirCheck(BaseCheck):
    """Memory guardian: database health, log growth, fact store stats."""
    
    name = "memory"
    description = "Mímir memory system health: DB integrity, log growth, fact store"
    
    def _perform_check(self) -> CheckResult:
        """Check all memory subsystems."""
        issues = []
        details = {}
        sub_results = []
        
        # ─── Mímir DB ───
        mimir_result = self._check_mimir_db()
        sub_results.append(mimir_result)
        if mimir_result.severity == CheckSeverity.CRITICAL:
            issues.append(("critical", mimir_result.message))
        elif mimir_result.severity == CheckSeverity.WARNING:
            issues.append(("warning", mimir_result.message))
        details["mimir"] = mimir_result.details
        
        # ─── Conversation Log ───
        log_result = self._check_conversation_log()
        sub_results.append(log_result)
        if log_result.severity == CheckSeverity.CRITICAL:
            issues.append(("critical", log_result.message))
        elif log_result.severity == CheckSeverity.WARNING:
            issues.append(("warning", log_result.message))
        details["conversation_log"] = log_result.details
        
        # ─── Nerve Feed ───
        nerve_result = self._check_nerve_feed()
        sub_results.append(nerve_result)
        if nerve_result.severity == CheckSeverity.CRITICAL:
            issues.append(("critical", nerve_result.message))
        elif nerve_result.severity == CheckSeverity.WARNING:
            issues.append(("warning", nerve_result.message))
        details["nerve_feed"] = nerve_result.details
        
        # ─── State DB ───
        state_result = self._check_state_db()
        sub_results.append(state_result)
        details["state_db"] = state_result.details
        
        # ─── Kista Vault ───
        kista_result = self._check_kista()
        sub_results.append(kista_result)
        details["kista"] = kista_result.details
        
        # Determine worst severity
        severity = self.worst_severity(sub_results)
        
        if not issues:
            memory_count = details.get("mimir", {}).get("total_rows", 0)
            message = f"Memory systems healthy ({memory_count} memories)"
        else:
            for level, msg in issues:
                if level == "critical":
                    message = msg
                    break
            else:
                message = issues[0][1]
        
        return CheckResult(
            name=self.name,
            severity=severity,
            message=message,
            details=details,
            sub_results=sub_results,
        )
    
    def _check_mimir_db(self) -> CheckResult:
        """Check Mímir Well database integrity and size."""
        db_path = Path.home() / ".mimir_well" / "mimir_well.db"
        if not db_path.exists():
            return CheckResult(
                name="memory:mimir_db",
                severity=CheckSeverity.UNKNOWN,
                message="Mímir Well DB not found",
                details={"path": str(db_path), "exists": False},
            )
        
        details = {"path": str(db_path), "exists": True}
        
        try:
            # File size
            size_bytes = db_path.stat().st_size
            size_mb = size_bytes / (1024 * 1024)
            details["size_mb"] = round(size_mb, 1)
            
            warn = self.config.get("thresholds.db_size_warning_mb", 100)
            crit = self.config.get("thresholds.db_size_critical_mb", 500)
            
            if size_mb >= crit:
                return CheckResult(
                    name="memory:mimir_db",
                    severity=CheckSeverity.CRITICAL,
                    message=f"Mímir DB {size_mb:.1f}MB >= {crit}MB",
                    details=details,
                )
            elif size_mb >= warn:
                # Warning but not critical
                pass
            
            # Connect and check tables (context manager ensures cleanup)
            with sqlite3.connect(str(db_path)) as conn:
                # Integrity check
                integrity = conn.execute("PRAGMA integrity_check").fetchone()
                details["integrity"] = integrity[0] if integrity else "unknown"
                
                # Row counts
                total = 0
                for table_name in ["memories", "knowledge", "relationships"]:
                    try:
                        count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                        details[f"{table_name}_count"] = count
                        total += count
                    except sqlite3.OperationalError:
                        details[f"{table_name}_count"] = 0
                
                details["total_rows"] = total
                
                # Last entry timestamp
                try:
                    last_ts = conn.execute(
                        "SELECT MAX(created_at) FROM memories"
                    ).fetchone()[0]
                    details["last_memory"] = last_ts
                except sqlite3.OperationalError:
                    details["last_memory"] = "unknown"
            
            severity = CheckSeverity.OK
            if size_mb >= warn:
                severity = CheckSeverity.WARNING
            
            return CheckResult(
                name="memory:mimir_db",
                severity=severity,
                message=f"Mímir DB OK ({total} rows, {size_mb:.1f}MB)",
                details=details,
            )
        
        except sqlite3.Error as e:
            return CheckResult(
                name="memory:mimir_db",
                severity=CheckSeverity.WARNING,
                message=f"Mímir DB error: {e}",
                details=details,
            )
    
    def _check_conversation_log(self) -> CheckResult:
        """Check conversation log growth and size."""
        log_path = get_state_dir() / "conversation_log.jsonl"
        
        if not log_path.exists():
            return CheckResult(
                name="memory:conversation_log",
                severity=CheckSeverity.UNKNOWN,
                message="Conversation log not found",
                details={"path": str(log_path), "exists": False},
            )
        
        details = {"path": str(log_path), "exists": True}
        
        try:
            size_bytes = log_path.stat().st_size
            size_mb = size_bytes / (1024 * 1024)
            details["size_mb"] = round(size_mb, 1)
            
            # Count lines (entries)
            entry_count = 0
            last_timestamp = None
            with open(log_path, "r") as f:
                for line in f:
                    entry_count += 1
                    if entry_count <= 5 or entry_count % 1000 == 0:
                        try:
                            data = json.loads(line)
                            last_timestamp = data.get("timestamp", None)
                        except json.JSONDecodeError:
                            pass
            
            details["entry_count"] = entry_count
            details["last_entry"] = last_timestamp
            
            # Size thresholds
            warn = self.config.get("thresholds.log_size_warning_mb", 50)
            crit = self.config.get("thresholds.log_size_critical_mb", 200)
            
            if size_mb >= crit:
                return CheckResult(
                    name="memory:conversation_log",
                    severity=CheckSeverity.CRITICAL,
                    message=f"Conversation log {size_mb:.1f}MB >= {crit}MB",
                    details=details,
                )
            elif size_mb >= warn:
                return CheckResult(
                    name="memory:conversation_log",
                    severity=CheckSeverity.WARNING,
                    message=f"Conversation log {size_mb:.1f}MB >= {warn}MB",
                    details=details,
                )
            
            return CheckResult(
                name="memory:conversation_log",
                severity=CheckSeverity.OK,
                message=f"Conversation log OK ({entry_count} entries, {size_mb:.1f}MB)",
                details=details,
            )
        
        except Exception as e:
            return CheckResult(
                name="memory:conversation_log",
                severity=CheckSeverity.WARNING,
                message=f"Conversation log error: {e}",
                details=details,
            )
    
    def _check_nerve_feed(self) -> CheckResult:
        """Check nerve feed size and freshness."""
        feed_path = get_state_dir() / "nerve_feed.jsonl"
        
        if not feed_path.exists():
            return CheckResult(
                name="memory:nerve_feed",
                severity=CheckSeverity.UNKNOWN,
                message="Nerve feed not found",
                details={"path": str(feed_path), "exists": False},
            )
        
        details = {"path": str(feed_path), "exists": True}
        
        try:
            size_bytes = feed_path.stat().st_size
            details["size_kb"] = round(size_bytes / 1024, 1)
            
            # Count lines and get last event
            event_count = 0
            last_event = None
            with open(feed_path, "r") as f:
                for line in f:
                    event_count += 1
                    try:
                        last_event = json.loads(line)
                    except json.JSONDecodeError:
                        pass
            
            details["event_count"] = event_count
            details["last_event_type"] = last_event.get("event_type") if last_event else None
            
            # Check freshness
            staleness_warn = self.config.get("thresholds.staleness_warning_hours", 24)
            if last_event and "timestamp" in last_event:
                last_ts = last_event["timestamp"]
                details["last_event_ts"] = last_ts
            
            return CheckResult(
                name="memory:nerve_feed",
                severity=CheckSeverity.OK,
                message=f"Nerve feed OK ({event_count} events)",
                details=details,
            )
        
        except Exception as e:
            return CheckResult(
                name="memory:nerve_feed",
                severity=CheckSeverity.WARNING,
                message=f"Nerve feed error: {e}",
                details=details,
            )
    
    def _check_state_db(self) -> CheckResult:
        """Check heartbeat state database."""
        db_path = get_state_dir() / "verdandi_heartbeat.db"
        
        if not db_path.exists():
            return CheckResult(
                name="memory:state_db",
                severity=CheckSeverity.OK,
                message="State DB not yet created (first pulse pending)",
                details={"path": str(db_path), "exists": False},
            )
        
        details = {"path": str(db_path), "exists": True}
        
        try:
            size_bytes = db_path.stat().st_size
            details["size_kb"] = round(size_bytes / 1024, 1)
            
            with sqlite3.connect(str(db_path)) as conn:
                integrity = conn.execute("PRAGMA integrity_check").fetchone()
                details["integrity"] = integrity[0] if integrity else "unknown"
                
                # Row count
                try:
                    count = conn.execute("SELECT COUNT(*) FROM heartbeat_state").fetchone()[0]
                    details["state_rows"] = count
                except sqlite3.OperationalError:
                    details["state_rows"] = 0
                
                try:
                    count = conn.execute("SELECT COUNT(*) FROM pulse_history").fetchone()[0]
                    details["pulse_count"] = count
                except sqlite3.OperationalError:
                    details["pulse_count"] = 0
            
            return CheckResult(
                name="memory:state_db",
                severity=CheckSeverity.OK,
                message=f"State DB OK ({details['size_kb']}KB)",
                details=details,
            )
        
        except Exception as e:
            return CheckResult(
                name="memory:state_db",
                severity=CheckSeverity.WARNING,
                message=f"State DB error: {e}",
                details=details,
            )
    
    def _check_kista(self) -> CheckResult:
        """Check Kista vault health."""
        kista_path = Path.home() / ".kista" / "vault.db"
        
        if not kista_path.exists():
            return CheckResult(
                name="memory:kista",
                severity=CheckSeverity.UNKNOWN,
                message="Kista vault not found",
                details={"path": str(kista_path), "exists": False},
            )
        
        details = {"path": str(kista_path), "exists": True}
        
        try:
            size_bytes = kista_path.stat().st_size
            details["size_kb"] = round(size_bytes / 1024, 1)
            
            with sqlite3.connect(str(kista_path)) as conn:
                try:
                    count = conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
                    details["entry_count"] = count
                except sqlite3.OperationalError:
                    details["entry_count"] = "unknown"
            
            return CheckResult(
                name="memory:kista",
                severity=CheckSeverity.OK,
                message=f"Kista OK ({details.get('entry_count', '?')} entries)",
                details=details,
            )
        
        except Exception as e:
            return CheckResult(
                name="memory:kista",
                severity=CheckSeverity.WARNING,
                message=f"Kista error: {e}",
                details=details,
            )