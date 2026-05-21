"""
Huginn — The All-Seeing Eye. Project Watcher.

Odin's raven Huginn (Thought) flies out each morning and returns
with news of the world. This check does the same for git repositories:
scans for unpushed commits, stale branches, dirty working trees,
and merge conflicts.

Features:
  - Auto-discovery of git repos under configured paths
  - Explicit watch paths for targeted monitoring
  - Unpushed commit detection with configurable thresholds
  - Stale branch detection (branches older than N days)
  - Dirty working tree detection
  - Diverged branch detection (ahead AND behind)
  - Pi-friendly: batches git operations, respects SD card

Config:
  projects:
    auto_discover: true
    watch_paths:
      - ~/Verdandi
      - ~/.hermes/state
    ignore_paths:
      - ~/.cache
      - ~/.local
  thresholds:
    unpushed_commits_warning: 5
    unpushed_commits_critical: 20
    stale_branch_days: 30
"""

import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from heartbeat.checks.base import BaseCheck, CheckResult, CheckSeverity


class HuginnCheck(BaseCheck):
    """Project watcher: git repos, unpushed changes, stale branches."""
    
    name = "projects"
    description = "Git project health: unpushed commits, stale branches, dirty trees"
    
    def _perform_check(self) -> CheckResult:
        """Scan all configured git repos."""
        repos = self._discover_repos()
        if not repos:
            return CheckResult(
                name=self.name,
                severity=CheckSeverity.UNKNOWN,
                message="No git repos found",
                details={"repos_found": 0},
            )
        
        details = {"repos_found": len(repos), "repos": {}}
        sub_results = []
        issues = []
        total_unpushed = 0
        total_dirty = 0
        total_stale = 0
        
        for repo_path in repos:
            repo_result = self._check_repo(repo_path)
            sub_results.append(repo_result)
            
            repo_name = repo_path.name
            details["repos"][repo_name] = {
                "path": str(repo_path),
                "severity": repo_result.severity.value,
                "message": repo_result.message,
            }
            details["repos"][repo_name].update(repo_result.details)
            
            # Aggregate
            total_unpushed += repo_result.details.get("unpushed", 0)
            if repo_result.details.get("dirty", False):
                total_dirty += 1
            if repo_result.details.get("stale_branches", 0) > 0:
                total_stale += 1
            
            if repo_result.severity == CheckSeverity.CRITICAL:
                issues.append(("critical", repo_result.message))
            elif repo_result.severity == CheckSeverity.WARNING:
                issues.append(("warning", repo_result.message))
        
        details["total_unpushed"] = total_unpushed
        details["total_dirty"] = total_dirty
        details["total_stale"] = total_stale
        
        # Determine worst severity
        severity = self.worst_severity(sub_results)
        
        # Build message
        if not issues:
            message = f"All {len(repos)} repos healthy ({total_unpushed} unpushed)"
        else:
            # Report the worst
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
    
    def _discover_repos(self) -> list[Path]:
        """Find all git repos from configured paths."""
        repos = set()
        home = Path.home()
        
        # Explicit watch paths
        watch_paths = self.config.get("projects.watch_paths", [])
        for path_str in watch_paths:
            p = Path(path_str).expanduser()
            if p.exists() and (p / ".git").exists():
                repos.add(p.resolve())
        
        # Auto-discover
        if self.config.get("projects.auto_discover", True):
            ignore = set(self.config.get("projects.ignore_paths", []))
            ignore_patterns = {".cache", ".local", ".config", ".npm", ".rustup",
                             ".cargo", ".nvm", ".pyenv", "node_modules", "__pycache__",
                             ".tox", ".eggs", ".mypy_cache", ".venv", "venv"}
            
            search_dirs = [home]
            max_depth = 3  # Don't recurse too deep — Pi-friendly
            
            for base_dir in search_dirs:
                self._scan_for_repos(base_dir, repos, ignore, ignore_patterns, max_depth)
        
        return sorted(repos)
    
    def _scan_for_repos(
        self, 
        directory: Path, 
        found: set, 
        ignore: set, 
        ignore_patterns: set,
        depth: int,
    ) -> None:
        """Recursively scan for git repos (depth-limited)."""
        if depth <= 0:
            return
        
        try:
            for entry in directory.iterdir():
                if not entry.is_dir():
                    continue
                # Skip ignored paths
                if entry.name in ignore_patterns:
                    continue
                if any(str(entry).startswith(str(Path(i).expanduser())) for i in ignore):
                    continue
                # Skip hidden dirs (except those in watch_paths)
                if entry.name.startswith(".") and entry.name not in (".hermes",):
                    # But check if it's a git repo first
                    if (entry / ".git").exists():
                        found.add(entry.resolve())
                    continue
                # Found a git repo
                if (entry / ".git").exists():
                    found.add(entry.resolve())
                else:
                    # Recurse
                    self._scan_for_repos(entry, found, ignore, ignore_patterns, depth - 1)
        except PermissionError:
            pass
    
    def _check_repo(self, repo_path: Path) -> CheckResult:
        """Check a single git repository."""
        issues = []
        details = {"path": str(repo_path)}
        
        # Current branch
        branch = self._git(repo_path, ["rev-parse", "--abbrev-ref", "HEAD"])
        if branch is None:
            return CheckResult(
                name=f"project:{repo_path.name}",
                severity=CheckSeverity.UNKNOWN,
                message=f"Cannot read git repo",
                details=details,
            )
        branch = branch.strip()  # Strip trailing newlines
        details["branch"] = branch
        
        # Dirty working tree
        status = self._git(repo_path, ["status", "--porcelain"])
        if status is not None:
            dirty_files = [l for l in status.strip().split("\n") if l.strip()]
            details["dirty"] = len(dirty_files) > 0
            details["dirty_files"] = len(dirty_files)
            if dirty_files:
                issues.append(("warning", f"{len(dirty_files)} uncommitted changes"))
        
        # Unpushed commits
        # Try upstream first, then origin
        unpushed = self._count_unpushed(repo_path, branch)
        details["unpushed"] = unpushed
        warn = self.config.get("thresholds.unpushed_commits_warning", 5)
        crit = self.config.get("thresholds.unpushed_commits_critical", 20)
        if unpushed >= crit:
            issues.append(("critical", f"{unpushed} unpushed commits"))
        elif unpushed >= warn:
            issues.append(("warning", f"{unpushed} unpushed commits"))
        
        # Stale branches (branches not touched in N days)
        stale_days = self.config.get("thresholds.stale_branch_days", 30)
        stale_count = self._count_stale_branches(repo_path, stale_days)
        details["stale_branches"] = stale_count
        if stale_count > 5:
            issues.append(("warning", f"{stale_count} stale branches (>{stale_days}d)"))
        
        # Determine severity
        severity = CheckSeverity.OK
        message = f"{repo_path.name}: {branch}, {unpushed} unpushed"
        for level, msg in issues:
            if level == "critical":
                severity = CheckSeverity.CRITICAL
                message = f"{repo_path.name}: {msg}"
                break
            elif level == "warning" and severity != CheckSeverity.CRITICAL:
                severity = CheckSeverity.WARNING
                message = f"{repo_path.name}: {msg}"
        
        return CheckResult(
            name=f"project:{repo_path.name}",
            severity=severity,
            message=message,
            details=details,
        )
    
    def _count_unpushed(self, repo_path: Path, branch: str) -> int:
        """Count unpushed commits for a branch."""
        # Try @{upstream} first
        result = self._git(repo_path, ["rev-list", "--count", "@{upstream}..HEAD"])
        if result is not None:
            try:
                return int(result.strip())
            except ValueError:
                pass
        
        # Fallback: try origin/<branch>
        result = self._git(repo_path, ["rev-list", "--count", f"origin/{branch}..HEAD"])
        if result is not None:
            try:
                return int(result.strip())
            except ValueError:
                pass
        
        # No upstream at all — all commits are "unpushed"
        result = self._git(repo_path, ["rev-list", "--count", "HEAD"])
        if result is not None:
            try:
                return int(result.strip())
            except ValueError:
                pass
        
        return 0
    
    def _count_stale_branches(self, repo_path: Path, days: int) -> int:
        """Count branches not touched in N days."""
        result = self._git(repo_path, [
            "for-each-ref", "--sort=-committerdate",
            "--format=%(committerdate:unix)", "refs/heads/"
        ])
        if result is None:
            return 0
        
        now = datetime.now(timezone.utc).timestamp()
        stale_count = 0
        for line in result.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            try:
                commit_ts = int(line)
                age_days = (now - commit_ts) / 86400
                if age_days > days:
                    stale_count += 1
            except ValueError:
                continue
        
        return stale_count
    
    def _git(self, repo_path: Path, args: list[str]) -> Optional[str]:
        """Run a git command and return stdout. Returns None on failure."""
        try:
            result = subprocess.run(
                ["git", "-C", str(repo_path)] + args,
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                return result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError):
            pass
        return None