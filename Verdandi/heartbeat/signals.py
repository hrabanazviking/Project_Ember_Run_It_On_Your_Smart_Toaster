"""
Verðandi Signal Handling — The Daemon's Reflexes.

Graceful handling of Unix signals for the heartbeat daemon:
  - SIGTERM/SIGINT: Graceful shutdown
  - SIGHUP: Reload configuration
  - SIGUSR1: Dump state to file
  - SIGUSR2: Force immediate pulse

All signal handlers are designed to be safe: they set flags
that the main loop checks, rather than performing actions directly.
This avoids the re-entrancy issues that plague naïve signal handling.
"""

import os
import signal
import json
import logging
from pathlib import Path
from typing import Callable, Optional
from types import FrameType

logger = logging.getLogger("verdandi.signals")


class SignalHandler:
    """Thread-safe signal handler for the heartbeat daemon.
    
    Sets flags that the main loop polls. Never performs I/O in handlers.
    
    Usage:
        handler = SignalHandler()
        handler.install()
        # ... in main loop ...
        if handler.should_shutdown:
            break
        if handler.should_reload:
            handler.clear_reload()
            config.reload()
    """
    
    def __init__(
        self,
        config_reload_callback: Optional[Callable] = None,
        state_dump_callback: Optional[Callable[[], dict]] = None,
    ):
        self.should_shutdown: bool = False
        self.should_reload: bool = False
        self.should_dump_state: bool = False
        self.should_pulse: bool = False
        
        self._config_reload = config_reload_callback
        self._state_dump = state_dump_callback
        self._original_handlers: dict[int, Any] = {}
        self._installed = False
    
    def install(self) -> None:
        """Install signal handlers. Safe to call multiple times."""
        if self._installed:
            return
        
        self._original_handlers[signal.SIGTERM] = signal.signal(signal.SIGTERM, self._handle_shutdown)
        self._original_handlers[signal.SIGINT] = signal.signal(signal.SIGINT, self._handle_shutdown)
        self._original_handlers[signal.SIGHUP] = signal.signal(signal.SIGHUP, self._handle_reload)
        
        # SIGUSR1/SIGUSR2 may not exist on all platforms (e.g., Windows)
        if hasattr(signal, "SIGUSR1"):
            self._original_handlers[signal.SIGUSR1] = signal.signal(signal.SIGUSR1, self._handle_dump_state)
        if hasattr(signal, "SIGUSR2"):
            self._original_handlers[signal.SIGUSR2] = signal.signal(signal.SIGUSR2, self._handle_pulse)
        
        self._installed = True
        logger.info("Signal handlers installed (SIGTERM, SIGINT, SIGHUP, SIGUSR1, SIGUSR2)")
    
    def restore(self) -> None:
        """Restore original signal handlers."""
        for sig, handler in self._original_handlers.items():
            if handler is not None:
                signal.signal(sig, handler)
            else:
                signal.signal(sig, signal.SIG_DFL)
        self._installed = False
        logger.info("Signal handlers restored to defaults")
    
    def clear_reload(self) -> None:
        """Clear the reload flag after processing."""
        self.should_reload = False
    
    def clear_dump_state(self) -> None:
        """Clear the dump-state flag after processing."""
        self.should_dump_state = False
    
    def clear_pulse(self) -> None:
        """Clear the force-pulse flag after processing."""
        self.should_pulse = False
    
    # ─────────────────────────────────────────────────────
    # Signal Handlers — Set flags only, no I/O
    # ─────────────────────────────────────────────────────
    
    def _handle_shutdown(self, sig: int, frame: Optional[FrameType]) -> None:
        """Handle SIGTERM/SIGINT by setting shutdown flag."""
        sig_name = signal.Signals(sig).name if hasattr(signal, "Signals") else f"Signal {sig}"
        self.should_shutdown = True
        logger.info(f"Received {sig_name}, initiating graceful shutdown")
    
    def _handle_reload(self, sig: int, frame: Optional[FrameType]) -> None:
        """Handle SIGHUP by setting reload flag."""
        self.should_reload = True
        logger.info("Received SIGHUP, scheduling config reload")
    
    def _handle_dump_state(self, sig: int, frame: Optional[FrameType]) -> None:
        """Handle SIGUSR1 by setting dump-state flag."""
        self.should_dump_state = True
        logger.info("Received SIGUSR1, scheduling state dump")
    
    def _handle_pulse(self, sig: int, frame: Optional[FrameType]) -> None:
        """Handle SIGUSR2 by scheduling an immediate pulse."""
        self.should_pulse = True
        logger.info("Received SIGUSR2, scheduling immediate pulse")
    
    # ─────────────────────────────────────────────────────
    # State Dump — for diagnostics
    # ─────────────────────────────────────────────────────
    
    def dump_state(self, state: dict, path: Path) -> None:
        """Write daemon state to a file for diagnostics.
        
        Called from main loop, NOT from signal handler.
        """
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w") as f:
                json.dump(state, f, indent=2, default=str)
            logger.info(f"State dumped to {path}")
        except Exception as e:
            logger.error(f"Failed to dump state: {e}")


class DaemonContext:
    """PID file management for daemon mode.
    
    Creates a PID file on start, removes on exit.
    Detects stale PID files from crashed instances.
    """
    
    def __init__(self, pid_path: Path):
        self.pid_path = pid_path
        self._stale_pid = False
    
    def acquire(self) -> bool:
        """Try to acquire the PID file. Returns True if this is the only instance.
        
        If a stale PID file is found (process not running), it's cleaned up.
        If another instance is running, returns False.
        """
        if self.pid_path.exists():
            try:
                old_pid = int(self.pid_path.read_text().strip())
                # Check if process is still running
                try:
                    os.kill(old_pid, 0)  # Signal 0 = existence check
                    # Process is running — we are NOT the only instance
                    return False
                except ProcessLookupError:
                    # Stale PID file — process is dead
                    self._stale_pid = True
                    logger.warning(f"Stale PID file found (PID {old_pid}), cleaning up")
                    self.pid_path.unlink(missing_ok=True)
                except PermissionError:
                    # Process exists but we can't signal it — assume it's running
                    return False
            except (ValueError, OSError) as e:
                logger.warning(f"Corrupt PID file: {e}, removing")
                self.pid_path.unlink(missing_ok=True)
        
        # Write our PID
        try:
            self.pid_path.parent.mkdir(parents=True, exist_ok=True)
            self.pid_path.write_text(str(os.getpid()))
            logger.info(f"Acquired PID file: {self.pid_path} (PID {os.getpid()})")
            return True
        except OSError as e:
            logger.error(f"Cannot write PID file: {e}")
            return False
    
    def release(self) -> None:
        """Release the PID file on shutdown."""
        try:
            self.pid_path.unlink(missing_ok=True)
            logger.info(f"Released PID file: {self.pid_path}")
        except OSError as e:
            logger.warning(f"Error removing PID file: {e}")