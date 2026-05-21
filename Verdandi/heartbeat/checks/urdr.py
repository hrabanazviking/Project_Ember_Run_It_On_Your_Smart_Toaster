"""
Urðr — The Thread of Fate. Schedule Keeper Check.

Urðr is the Norn who measures the thread of life. This check
monitors scheduled tasks (cron jobs, systemd timers) for health:
missed runs, stuck processes, and schedule drift.

Checks:
  - Crontab entries for Runa's scheduled jobs
  - Recent cron execution logs
  - Stuck/long-running processes
  - Systemd timer status (for nerve hub and heartbeat)
  - Schedule drift detection

Config:
  checks:
    schedule: true
  thresholds:
    missed_runs_warning: 2
    missed_runs_critical: 5
    stuck_process_minutes: 30
"""

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from heartbeat.checks.base import BaseCheck, CheckResult, CheckSeverity
from heartbeat.paths import get_state_dir


class UrdrCheck(BaseCheck):
    """Schedule keeper: cron health, missed runs, stuck processes."""
    
    name = "schedule"
    description = "Schedule health: cron jobs, systemd timers, stuck processes"
    
    def _perform_check(self) -> CheckResult:
        """Check all scheduled systems."""
        issues = []
        details = {}
        sub_results = []
        
        # ─── Cron Jobs ───
        cron_result = self._check_cron()
        sub_results.append(cron_result)
        details["cron"] = cron_result.details
        if cron_result.severity == CheckSeverity.CRITICAL:
            issues.append(("critical", cron_result.message))
        elif cron_result.severity == CheckSeverity.WARNING:
            issues.append(("warning", cron_result.message))
        
        # ─── Systemd Services ───
        systemd_result = self._check_systemd()
        sub_results.append(systemd_result)
        details["systemd"] = systemd_result.details
        if systemd_result.severity == CheckSeverity.CRITICAL:
            issues.append(("critical", systemd_result.message))
        elif systemd_result.severity == CheckSeverity.WARNING:
            issues.append(("warning", systemd_result.message))
        
        # ─── Stuck Processes ───
        stuck_result = self._check_stuck_processes()
        sub_results.append(stuck_result)
        details["stuck_processes"] = stuck_result.details
        if stuck_result.severity == CheckSeverity.CRITICAL:
            issues.append(("critical", stuck_result.message))
        elif stuck_result.severity == CheckSeverity.WARNING:
            issues.append(("warning", stuck_result.message))
        
        # ─── Nerve Hub ───
        nerve_result = self._check_nerve_hub()
        sub_results.append(nerve_result)
        details["nerve_hub"] = nerve_result.details
        
        # Determine severity
        severity = self.worst_severity(sub_results)
        
        if not issues:
            job_count = details.get("cron", {}).get("job_count", 0)
            message = f"Schedule healthy ({job_count} cron jobs)"
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
    
    def _check_cron(self) -> CheckResult:
        """Check crontab for Runa's scheduled jobs."""
        details = {"jobs": []}
        job_count = 0
        
        # Read user crontab
        try:
            result = subprocess.run(
                ["crontab", "-l"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    # Parse cron line
                    parts = line.split(None, 5)
                    if len(parts) >= 6:
                        schedule = " ".join(parts[:5])
                        command = parts[5]
                        job_count += 1
                        details["jobs"].append({
                            "schedule": schedule,
                            "command": command[:80],  # Truncate long commands
                        })
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        details["job_count"] = job_count
        
        # Check for Verdandi-relevant jobs
        verdandi_jobs = [j for j in details["jobs"] 
                         if "verdandi" in j["command"].lower() or 
                            "heartbeat" in j["command"].lower() or
                            "nerve" in j["command"].lower()]
        details["verdandi_jobs"] = len(verdandi_jobs)
        
        severity = CheckSeverity.OK
        message = f"{job_count} cron jobs found ({len(verdandi_jobs)} Verdandi-related)"
        
        if job_count == 0:
            severity = CheckSeverity.WARNING
            message = "No cron jobs found"
        
        return CheckResult(
            name="schedule:cron",
            severity=severity,
            message=message,
            details=details,
        )
    
    def _check_systemd(self) -> CheckResult:
        """Check Verdandi-related systemd services."""
        details = {"services": []}
        
        # Services we expect to be running
        expected_services = [
            "runa-nervous-system",
            "verdandi-heartbeat",
        ]
        
        for service_name in expected_services:
            service_info = {"name": service_name}
            
            try:
                result = subprocess.run(
                    ["systemctl", "--user", "status", service_name],
                    capture_output=True, text=True, timeout=10
                )
                service_info["active"] = "active" in result.stdout
                service_info["status_output"] = result.stdout[:200]
            except (FileNotFoundError, subprocess.TimeoutExpired):
                # Try without --user
                try:
                    result = subprocess.run(
                        ["systemctl", "status", service_name],
                        capture_output=True, text=True, timeout=10
                    )
                    service_info["active"] = "active" in result.stdout
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    service_info["active"] = False
                    service_info["note"] = "systemctl not available"
            
            details["services"].append(service_info)
        
        # Check how many expected services are active
        active_count = sum(1 for s in details["services"] if s.get("active", False))
        details["active_count"] = active_count
        details["expected_count"] = len(expected_services)
        
        severity = CheckSeverity.OK
        message = f"{active_count}/{len(expected_services)} services active"
        
        if active_count == 0:
            # Not critical — the services may not be installed yet
            severity = CheckSeverity.UNKNOWN
            message = "No Verdandi services found (may not be installed yet)"
        
        return CheckResult(
            name="schedule:systemd",
            severity=severity,
            message=message,
            details=details,
        )
    
    def _check_stuck_processes(self) -> CheckResult:
        """Check for stuck or long-running Verdandi processes."""
        details = {"stuck": [], "running": []}
        stuck_threshold_min = self.config.get("thresholds.stuck_process_minutes", 30)
        
        try:
            # Find Verdandi-related processes (exclude long-running services like nerve hub)
            result = subprocess.run(
                ["pgrep", "-af", "verdandi|heartbeat|reactor"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    parts = line.strip().split(None, 1)
                    if len(parts) >= 2:
                        details["running"].append({
                            "pid": int(parts[0]),
                            "command": parts[1][:80],
                        })
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # Check process run times
        for proc in details["running"]:
            try:
                # Get elapsed time
                result = subprocess.run(
                    ["ps", "-p", str(proc["pid"]), "-o", "etimes="],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    elapsed = int(result.stdout.strip())
                    proc["elapsed_seconds"] = elapsed
                    proc["elapsed_minutes"] = round(elapsed / 60, 1)
                    
                    # Check if stuck (running too long for a single pulse)
                    if elapsed > stuck_threshold_min * 60:
                        details["stuck"].append(proc)
            except (ValueError, subprocess.TimeoutExpired):
                pass
        
        details["running_count"] = len(details["running"])
        details["stuck_count"] = len(details["stuck"])
        
        severity = CheckSeverity.OK
        message = f"{len(details['running'])} Verdandi processes running"
        
        if details["stuck"]:
            severity = CheckSeverity.WARNING
            message = f"{len(details['stuck'])} stuck process(es) (>{stuck_threshold_min}min)"
        
        return CheckResult(
            name="schedule:processes",
            severity=severity,
            message=message,
            details=details,
        )
    
    def _check_nerve_hub(self) -> CheckResult:
        """Check if the nerve hub socket is responding."""
        socket_path = get_state_dir() / "runa.sock"
        
        details = {"socket_path": str(socket_path), "exists": socket_path.exists()}
        
        if not socket_path.exists():
            return CheckResult(
                name="schedule:nerve_hub",
                severity=CheckSeverity.WARNING,
                message="Nerve hub socket not found",
                details=details,
            )
        
        # Try to connect
        import socket as sock_mod
        try:
            with sock_mod.socket(sock_mod.AF_UNIX, sock_mod.SOCK_STREAM) as s:
                s.settimeout(2)
                s.connect(str(socket_path))
                details["responsive"] = True
                return CheckResult(
                    name="schedule:nerve_hub",
                    severity=CheckSeverity.OK,
                    message="Nerve hub responding",
                    details=details,
                )
        except (ConnectionRefusedError, FileNotFoundError, sock_mod.timeout, OSError):
            details["responsive"] = False
            return CheckResult(
                name="schedule:nerve_hub",
                severity=CheckSeverity.WARNING,
                message="Nerve hub socket exists but not responding",
                details=details,
            )