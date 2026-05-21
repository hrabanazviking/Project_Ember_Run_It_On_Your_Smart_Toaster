"""Async-event-loop-in-a-thread bridge (ADR-0014).

The ``mcp`` client SDK is asyncio-based. Ember is synchronous everywhere
else. ``MCPRunner`` owns a single asyncio event loop running on a
daemon thread; sync code submits coroutines via ``submit()`` and gets a
result (or raises the awaited exception) without leaving the calling
thread's sync world.

One runner can host many ``ClientSession`` objects (one per MCP
server). The single-event-loop model means all session lifetimes are
serialized through one loop — simpler than per-session loops, and
sufficient for the single-process REPL Ember runs.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import threading
from collections.abc import Awaitable
from typing import TypeVar

logger = logging.getLogger(__name__)

_T = TypeVar("_T")


class MCPRunner:
    """Owns one asyncio event loop on a daemon thread.

    Methods are thread-safe (the loop is single-threaded; submission is
    via ``asyncio.run_coroutine_threadsafe``).

    Lifecycle:

    - Construct: starts the thread + loop, returns when loop is ready.
    - ``submit(coro, timeout=...)``: schedule + block on a coroutine.
    - ``close()``: stop the loop, join the thread. Idempotent.
    """

    def __init__(self) -> None:
        self._loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        self._ready = threading.Event()
        self._closed = False
        self._thread = threading.Thread(
            target=self._run_loop,
            name="ember-mcp-runner",
            daemon=True,
        )
        self._thread.start()
        # Wait until the loop is actually running before letting callers
        # submit coros — otherwise the first submit() can race the loop
        # startup and silently hang.
        if not self._ready.wait(timeout=5.0):
            raise RuntimeError("MCPRunner event loop failed to start in 5s")

    def _run_loop(self) -> None:
        asyncio.set_event_loop(self._loop)
        self._loop.call_soon(self._ready.set)
        try:
            self._loop.run_forever()
        finally:
            # Drain any pending tasks so close() leaves no orphan futures.
            try:
                pending = asyncio.all_tasks(self._loop)
                for task in pending:
                    task.cancel()
                self._loop.run_until_complete(
                    asyncio.gather(*pending, return_exceptions=True)
                )
            except Exception as exc:
                logger.warning("MCPRunner loop drain failed: %s", exc)
            finally:
                self._loop.close()

    def submit(self, coro: Awaitable[_T], *, timeout: float | None = None) -> _T:
        """Schedule a coroutine on the runner's loop, block on the result.

        Raises whatever the coroutine raises. Raises ``TimeoutError`` if
        ``timeout`` elapses (default: no timeout). Raises ``RuntimeError``
        if the runner is already closed.
        """
        if self._closed:
            raise RuntimeError("MCPRunner is closed")
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)  # type: ignore[arg-type]
        try:
            return future.result(timeout=timeout)
        except TimeoutError:
            # Try to cancel the underlying task so it doesn't keep
            # running after the caller has given up on the result.
            future.cancel()
            raise

    def close(self) -> None:
        """Stop the loop + join the thread. Idempotent.

        After close() any submit() raises RuntimeError.
        """
        if self._closed:
            return
        self._closed = True
        # call_soon_threadsafe is the safe way to schedule from outside
        # the loop's thread. RuntimeError means the loop already stopped —
        # which is exactly the post-close state we want, so suppress.
        with contextlib.suppress(RuntimeError):
            self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join(timeout=5.0)
        if self._thread.is_alive():  # pragma: no cover — fallback
            logger.warning("MCPRunner thread did not exit within 5s")


__all__ = ["MCPRunner"]
