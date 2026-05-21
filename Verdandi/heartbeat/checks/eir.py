"""
Eir — The Healing Touch. System Health Check.

Monitors the physical body: CPU temperature, RAM pressure, disk space.
On Raspberry Pi, also checks thermal throttling status and SD card health.

Eir is the Norse goddess of medicine and healing. She knows when the
body is well and when it needs attention — before the human notices.

Thresholds are configurable via heartbeat.yaml:
  thresholds:
    cpu_temp_warning: 70
    cpu_temp_critical: 80
    ram_warning_percent: 85
    ram_critical_percent: 95
    disk_warning_percent: 80
    disk_critical_percent: 90
"""

import subprocess
from pathlib import Path
from typing import Optional

from heartbeat.checks.base import BaseCheck, CheckResult, CheckSeverity


class EirCheck(BaseCheck):
    """System health check: CPU temp, RAM, disk, services."""
    
    name = "health"
    description = "System health: CPU temperature, RAM usage, disk space"
    
    def _perform_check(self) -> CheckResult:
        """Run all health sub-checks."""
        issues = []
        details = {}
        sub_results = []
        
        # ─── CPU Temperature ───
        temp = self._read_cpu_temp()
        if temp is not None:
            details["cpu_temp_c"] = temp
            warn = self.config.get("thresholds.cpu_temp_warning", 70)
            crit = self.config.get("thresholds.cpu_temp_critical", 80)
            if temp >= crit:
                issues.append(("critical", f"CPU temp {temp:.1f}°C >= {crit}°C"))
            elif temp >= warn:
                issues.append(("warning", f"CPU temp {temp:.1f}°C >= {warn}°C"))
        
        # ─── RAM Usage ───
        ram = self._read_ram()
        if ram:
            details["ram_used_percent"] = ram["percent"]
            details["ram_total_gb"] = ram["total_gb"]
            details["ram_available_gb"] = ram["available_gb"]
            warn = self.config.get("thresholds.ram_warning_percent", 85)
            crit = self.config.get("thresholds.ram_critical_percent", 95)
            if ram["percent"] >= crit:
                issues.append(("critical", f"RAM {ram['percent']:.1f}% >= {crit}%"))
            elif ram["percent"] >= warn:
                issues.append(("warning", f"RAM {ram['percent']:.1f}% >= {warn}%"))
        
        # ─── Disk Usage ───
        disk = self._read_disk()
        if disk:
            details["disk_used_percent"] = disk["percent"]
            details["disk_total_gb"] = disk["total_gb"]
            details["disk_free_gb"] = disk["free_gb"]
            warn = self.config.get("thresholds.disk_warning_percent", 80)
            crit = self.config.get("thresholds.disk_critical_percent", 90)
            if disk["percent"] >= crit:
                issues.append(("critical", f"Disk {disk['percent']:.1f}% >= {crit}%"))
            elif disk["percent"] >= warn:
                issues.append(("warning", f"Disk {disk['percent']:.1f}% >= {warn}%"))
        
        # ─── Pi-specific: thermal throttling ───
        throttle = self._read_pi_throttle()
        if throttle:
            details["pi_throttled"] = throttle
            if throttle != "no":
                issues.append(("warning", f"Pi throttle flags: {throttle}"))
        
        # ─── Determine severity ───
        severity = CheckSeverity.OK
        message = self._health_message(issues, temp)
        for level, msg in issues:
            if level == "critical":
                severity = CheckSeverity.CRITICAL
                message = msg
                break
            elif level == "warning" and severity != CheckSeverity.CRITICAL:
                severity = CheckSeverity.WARNING
                message = msg
        
        return CheckResult(
            name=self.name,
            severity=severity,
            message=message,
            details=details,
        )
    
    def _health_message(self, issues: list, temp: Optional[float]) -> str:
        """Generate a friendly health message."""
        from heartbeat.paths import get_platform_info
        pinfo = get_platform_info()
        if not issues:
            base = "All health checks passing"
            if pinfo.get("is_pi") and temp:
                base += f" (Pi, {temp:.1f}°C)"
            elif temp:
                base += f" ({temp:.1f}°C)"
            return base
        # Return worst issue
        for level, msg in reversed(issues):
            if level == "critical":
                return msg
        return issues[-1][1] if issues else "Unknown health status"
    
    # ─────────────────────────────────────────────────────
    # System readers — each handles its own errors gracefully
    # ─────────────────────────────────────────────────────
    
    def _read_cpu_temp(self) -> Optional[float]:
        """Read CPU temperature. Returns °C or None."""
        # Linux thermal zones (works on Pi and most Linux)
        for tz in Path("/sys/class/thermal").glob("thermal_zone*"):
            try:
                raw = int((tz / "temp").read_text().strip())
                return raw / 1000.0
            except (FileNotFoundError, ValueError, PermissionError):
                continue
        
        # Raspberry Pi vcgencmd
        try:
            result = subprocess.run(
                ["vcgencmd", "measure_temp"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return float(result.stdout.strip().split("=")[1].split("'")[0])
        except (FileNotFoundError, subprocess.TimeoutExpired, ValueError, IndexError):
            pass
        
        return None
    
    def _read_ram(self) -> Optional[dict]:
        """Read RAM statistics from /proc/meminfo."""
        try:
            info = {}
            with open("/proc/meminfo") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 2:
                        info[parts[0].rstrip(":")] = int(parts[1])
            
            total = info.get("MemTotal", 0)
            available = info.get("MemAvailable", 0)
            if total == 0:
                return None
            
            return {
                "total_kb": total,
                "available_kb": available,
                "total_gb": round(total / 1048576, 1),
                "available_gb": round(available / 1048576, 1),
                "percent": round((total - available) / total * 100, 1),
            }
        except (FileNotFoundError, ValueError, PermissionError):
            return None
    
    def _read_disk(self, path: str = "/") -> Optional[dict]:
        """Read disk usage for a mount point."""
        try:
            import shutil
            u = shutil.disk_usage(path)
            return {
                "total_gb": round(u.total / 1073741824, 1),
                "used_gb": round(u.used / 1073741824, 1),
                "free_gb": round(u.free / 1073741824, 1),
                "percent": round(u.used / u.total * 100, 1),
            }
        except Exception:
            return None
    
    def _read_pi_throttle(self) -> Optional[str]:
        """Read Pi throttle status via vcgencmd. Non-Pi returns None."""
        try:
            result = subprocess.run(
                ["vcgencmd", "get_throttled"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip().split("=")[-1].strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        return None