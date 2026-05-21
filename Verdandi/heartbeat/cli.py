"""
Verðandi Heartbeat CLI — Command the Pulse.

Usage:
    verdandi-heartbeat start          Start the daemon
    verdandi-heartbeat stop           Stop the daemon
    verdandi-heartbeat status         Show daemon status
    verdandi-heartbeat pulse          Run a single pulse (no daemon)
    verdandi-heartbeat config         Show current configuration
    verdandi-heartbeat config --validate  Validate config file
    verdandi-heartbeat paths          Show resolved paths

Each command is also available as a Python module:
    python3 -m heartbeat.cli start
"""

import argparse
import json
import os
import sys
import signal
import subprocess
from pathlib import Path
from datetime import datetime, timezone

from heartbeat import __version__, __norse_name__
from heartbeat.config import HeartbeatConfig
from heartbeat.paths import (
    get_state_dir, get_config_dir, get_log_dir, get_pid_dir,
    get_socket_path, get_config_path, get_db_path, get_pid_path,
    get_log_path, get_platform_info, ensure_dirs, resolve_paths,
)
from heartbeat.core import HeartbeatDaemon, DaemonState
from heartbeat.reactor import Reactor


def cmd_start(args):
    """Start the heartbeat daemon."""
    config = HeartbeatConfig(
        config_path=Path(args.config) if args.config else None
    )
    
    # Check if already running
    pid_path = get_pid_path()
    if pid_path.exists():
        try:
            old_pid = int(pid_path.read_text().strip())
            os.kill(old_pid, 0)  # Check if process exists
            print(f"❌ Verðandi Heartbeat is already running (PID {old_pid})")
            return 1
        except ProcessLookupError:
            print(f"🧹 Stale PID file found, cleaning up")
            pid_path.unlink(missing_ok=True)
        except PermissionError:
            print(f"❌ Another instance appears to be running (PID {old_pid})")
            return 1
    
    ensure_dirs()
    
    if args.foreground:
        # Run in foreground (for debugging / systemd)
        daemon = HeartbeatDaemon(config=config, daemon=False)
        print(f"🫀 Starting Verðandi Heartbeat in foreground (v{__version__})")
        print(f"   Platform: {get_platform_info()['platform_name']}")
        print(f"   State dir: {get_state_dir()}")
        print(f"   Pulse interval: {config.get('heartbeat.interval_seconds')}s")
        print(f"   Press Ctrl+C to stop")
        print()
        try:
            # For foreground mode, we run the pulse loop directly without daemon context
            import heartbeat.core as core_mod
            handler = core_mod.SignalHandler(
                config_reload_callback=config.reload,
                state_dump_callback=lambda: daemon.state.to_dict(),
            )
            handler.install()
            daemon._signal_handler = handler
            daemon._setup_logging()
            daemon.state.state = DaemonState.RUNNING
            daemon._running = True
            daemon._state_db_init()
            
            # Startup delay
            startup_delay = config.get("heartbeat.startup_delay_seconds", 10)
            print(f"   Startup delay: {startup_delay}s...")
            import time
            time.sleep(startup_delay)
            
            while daemon._running and not handler.should_shutdown:
                # Handle signals
                if handler.should_reload:
                    handler.clear_reload()
                    config.reload()
                    print("   🔄 Config reloaded")
                if handler.should_dump_state:
                    handler.clear_dump_state()
                    handler.dump_state(daemon.state.to_dict(), get_state_dir() / "verdandi_state_dump.json")
                if handler.should_pulse:
                    handler.clear_pulse()
                
                daemon.pulse()
                daemon._update_daemon_state()
                
                interval = config.get("heartbeat.interval_seconds", 60)
                jitter = config.get("heartbeat.jitter_seconds", 5)
                sleep_time = interval + __import__("random").uniform(-jitter, jitter)
                
                for _ in range(max(1, int(sleep_time))):
                    if handler.should_shutdown:
                        break
                    if handler.should_pulse:
                        handler.clear_pulse()
                        break
                    if handler.should_reload:
                        handler.clear_reload()
                        config.reload()
                    time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n🫀 Verðandi Heartbeat stopping...")
        finally:
            daemon.state.state = DaemonState.SHUTTING_DOWN
            daemon._state_db_save()
            handler.restore()
            daemon._running = False
            print("🫀 Verðandi Heartbeat stopped. The pulse is silent for now.")
    else:
        # Daemonize (double-fork)
        print(f"🫀 Starting Verðandi Heartbeat as daemon (v{__version__})")
        print(f"   PID file: {pid_path}")
        print(f"   Log file: {get_log_path()}")
        
        # Use subprocess to start in background
        # The actual daemonization is handled by systemd or nohup
        cmd = [sys.executable, "-m", "heartbeat.cli", "start", "--foreground"]
        if args.config:
            cmd.extend(["--config", args.config])
        
        # Start as background process
        log_path = get_log_path()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_path, "a") as log_f:
            proc = subprocess.Popen(
                cmd,
                stdout=log_f,
                stderr=log_f,
                start_new_session=True,
            )
        
        print(f"   Started with PID {proc.pid}")
        print(f"   Use 'verdandi-heartbeat status' to check status")
        return 0


def cmd_stop(args):
    """Stop the heartbeat daemon."""
    pid_path = get_pid_path()
    
    if not pid_path.exists():
        # Try to find by process name
        try:
            result = subprocess.run(
                ["pgrep", "-f", "verdandi-heartbeat"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                pids = result.stdout.strip().split("\n")
                for pid_str in pids:
                    try:
                        pid = int(pid_str)
                        os.kill(pid, signal.SIGTERM)
                        print(f"🛑 Sent SIGTERM to process {pid}")
                    except (ValueError, ProcessLookupError):
                        pass
                return 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        print("❌ No PID file found and no matching process")
        return 1
    
    try:
        pid = int(pid_path.read_text().strip())
        print(f"🛑 Sending SIGTERM to PID {pid}...")
        os.kill(pid, signal.SIGTERM)
        
        # Wait for process to exit
        import time
        for _ in range(30):  # 30 second timeout
            try:
                os.kill(pid, 0)  # Check if still running
                time.sleep(1)
            except ProcessLookupError:
                print(f"✅ Process {pid} stopped")
                return 0
        
        # Force kill
        print(f"⚠️ Process {pid} didn't stop gracefully, sending SIGKILL")
        os.kill(pid, signal.SIGKILL)
        return 0
    
    except ProcessLookupError:
        print("❌ Process not found (may have already stopped)")
        pid_path.unlink(missing_ok=True)
        return 1
    except PermissionError:
        print("❌ Permission denied (try with sudo)")
        return 1


def cmd_status(args):
    """Show daemon status."""
    pinfo = get_platform_info()
    pid_path = get_pid_path()
    
    print(f"🫀 Verðandi Heartbeat v{__version__} — {__norse_name__}")
    print(f"")
    print(f"   Platform: {pinfo['platform_name']} ({pinfo['system']}/{pinfo['machine']})")
    print(f"   State dir: {get_state_dir()} (source: {resolve_paths()['source']})")
    print(f"   Config: {get_config_path()}")
    print(f"   PID file: {pid_path}")
    print(f"   Socket: {get_socket_path()}")
    print(f"   Log: {get_log_path()}")
    print(f"   DB: {get_db_path()}")
    print(f"")
    
    # Check if running
    if pid_path.exists():
        try:
            pid = int(pid_path.read_text().strip())
            os.kill(pid, 0)  # Check if alive
            print(f"   Status: 🟢 RUNNING (PID {pid})")
            
            # Try to read state DB
            db_path = get_db_path()
            if db_path.exists():
                import sqlite3
                try:
                    conn = sqlite3.connect(str(db_path))
                    # Last pulse
                    row = conn.execute("SELECT value FROM heartbeat_state WHERE key = 'last_pulse'").fetchone()
                    last_pulse = row[0] if row else "never"
                    # State
                    row = conn.execute("SELECT value FROM heartbeat_state WHERE key = 'state'").fetchone()
                    state = row[0] if row else "unknown"
                    # Pulse count
                    row = conn.execute("SELECT value FROM heartbeat_state WHERE key = 'pulse_count'").fetchone()
                    pulse_count = row[0] if row else "0"
                    
                    print(f"   State: {state}")
                    print(f"   Last pulse: {last_pulse}")
                    print(f"   Pulse count: {pulse_count}")
                    conn.close()
                except Exception as e:
                    print(f"   (State DB: {e})")
        except ProcessLookupError:
            print(f"   Status: 🔴 STOPPED (stale PID file)")
        except PermissionError:
            print(f"   Status: 🟡 RUNNING (PID {pid}, can't verify)")
    else:
        print(f"   Status: 🔴 STOPPED")
    
    return 0


def cmd_pulse(args):
    """Run a single pulse without starting the daemon."""
    config = HeartbeatConfig(
        config_path=Path(args.config) if args.config else None
    )
    
    print(f"🫀 Running single pulse...")
    daemon = HeartbeatDaemon(config=config, daemon=False)
    daemon._state_db_init()  # Ensure DB tables exist for single-pulse mode
    state = daemon.pulse()
    daemon._update_daemon_state()  # Transition from INITIALIZING after first pulse
    
    print(f"")
    print(f"   State: {state.state.value}")
    print(f"   Pulse: #{state.pulse_count}")
    for name, result in state.checks.items():
        icon = {"ok": "✅", "warning": "⚠️", "critical": "🚨", "unknown": "❓"}.get(result.severity.value, "❓")
        print(f"   {icon} {name}: {result.severity.value} — {result.message}")
        if result.details:
            for key, value in result.details.items():
                print(f"      {key}: {value}")
    
    return 0 if state.state in (DaemonState.RUNNING, DaemonState.DEGRADED) else 1


def cmd_config(args):
    """Show or validate current configuration."""
    config = HeartbeatConfig(
        config_path=Path(args.config) if args.config else None
    )
    
    if args.validate:
        # Validate: load and check all values
        try:
            all_config = config.all
            # Check required sections exist
            required = ["heartbeat", "thresholds", "checks", "recovery", "nerve"]
            missing = [s for s in required if s not in all_config]
            if missing:
                print(f"❌ Missing config sections: {', '.join(missing)}")
                return 1
            
            # Check critical values
            interval = config.get("heartbeat.interval_seconds")
            if not isinstance(interval, (int, float)) or interval <= 0:
                print(f"❌ Invalid heartbeat.interval_seconds: {interval}")
                return 1
            
            print(f"✅ Configuration is valid")
            print(f"   Config path: {config.config_path}")
            print(f"   Config source: {config}")
            return 0
        except Exception as e:
            print(f"❌ Config validation error: {e}")
            return 1
    
    # Show config
    print(f"📄 Verðandi Heartbeat Configuration")
    print(f"   Config file: {config.config_path}")
    print(f"   Config source: {config}")
    print(f"")
    
    import yaml
    try:
        print(yaml.dump(config.all, default_flow_style=False, sort_keys=True))
    except NameError:
        # No PyYAML — use JSON fallback
        print(json.dumps(config.all, indent=2))
    
    return 0


def cmd_paths(args):
    """Show resolved path configuration."""
    paths = resolve_paths()
    print(f"📁 Verðandi Path Resolution (platform: {paths['platform_name']})")
    print(f"   Source: {paths['source']}")
    print(f"")
    path_names = [
        "state_dir", "config_dir", "log_dir", "pid_dir",
        "socket_path", "config_path", "db_path", "pid_path", "log_path"
    ]
    for name in path_names:
        value = paths.get(name, "N/A")
        exists = Path(value).exists() if isinstance(value, (str, Path)) else False
        icon = "✅" if exists else "📁" if name.endswith("_dir") else "📄"
        print(f"   {icon} {name}: {value}")
    return 0


def cmd_react(args):
    """Run checks and show what actions would be triggered."""
    config = HeartbeatConfig(
        config_path=Path(args.config) if args.config else None
    )
    dry_run = not args.execute  # Default is dry-run; --execute makes it real
    
    daemon = HeartbeatDaemon(config=config, daemon=False)
    daemon._state_db_init()
    
    print(f"🎯 Verðandi Reactor — mode: {'DRY-RUN' if dry_run else 'EXECUTE'}")
    print(f"")
    
    # Run a single pulse to get check results
    state = daemon.pulse()
    
    # Show check results
    print(f"📋 Check Results:")
    for name, result in state.checks.items():
        icons = {"ok": "✅", "warning": "⚠️", "critical": "🚨", "unknown": "❓"}
        icon = icons.get(result.severity.value, "❓")
        print(f"   {icon} {name}: {result.severity.value} — {result.message}")
    
    # Run reactor
    reactor = Reactor(config=config, dry_run=dry_run)
    action_results = reactor.react(state.checks)
    
    print(f"")
    print(f"🎯 Action Results ({len(action_results)} triggered):")
    if not action_results:
        print(f"   No actions triggered — all checks OK or in cooldown")
    else:
        for ar in action_results:
            icons = {"success": "✅", "partial": "⚠️", "failed": "❌", "skipped": "⏭️", "dry_run": "🔮"}
            icon = icons.get(ar.severity.value, "❓")
            print(f"   {icon} {ar.action_name}: {ar.severity.value}")
            print(f"      {ar.message}")
            if ar.targets_affected:
                print(f"      Affected: {', '.join(ar.targets_affected[:5])}")
            if ar.targets_failed:
                print(f"      Failed: {', '.join(ar.targets_failed[:5])}")
    
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="verdandi-heartbeat",
        description=f"Verðandi Heartbeat v{__version__} — {__norse_name__}",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--config", "-c", help="Path to config file")
    
    sub = parser.add_subparsers(dest="command", help="Available commands")
    
    # start
    sp = sub.add_parser("start", help="Start the heartbeat daemon")
    sp.add_argument("--foreground", "-f", action="store_true", help="Run in foreground (don't daemonize)")
    
    # stop
    sub.add_parser("stop", help="Stop the heartbeat daemon")
    
    # status
    sub.add_parser("status", help="Show daemon status")
    
    # pulse
    sub.add_parser("pulse", help="Run a single pulse (no daemon)")
    
    # config
    sp = sub.add_parser("config", help="Show or validate configuration")
    sp.add_argument("--validate", action="store_true", help="Validate config")
    
    # paths
    sub.add_parser("paths", help="Show resolved path configuration")
    
    # react
    sp = sub.add_parser("react", help="Run checks and show what actions would be triggered")
    sp.add_argument("--dry-run", action="store_true", default=True, help="Dry-run mode (default: True)")
    sp.add_argument("--execute", action="store_true", help="Actually execute actions (not dry-run)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    commands = {
        "start": cmd_start,
        "stop": cmd_stop,
        "status": cmd_status,
        "pulse": cmd_pulse,
        "config": cmd_config,
        "paths": cmd_paths,
        "react": cmd_react,
    }
    
    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main() or 0)