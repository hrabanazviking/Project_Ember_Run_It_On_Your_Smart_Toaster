"""Unit tests for MCPRunner — the async-event-loop-in-a-thread bridge.

Per ADR-0014. The runner is the foundation of the MCP client; if its
sync→async submit semantics are wrong, every MCP call breaks.
"""

from __future__ import annotations

import asyncio
import time

import pytest

from ember.mcp.runner import MCPRunner


def test_runner_submit_returns_coroutine_result() -> None:
    runner = MCPRunner()
    try:
        async def _value() -> int:
            return 42
        assert runner.submit(_value()) == 42
    finally:
        runner.close()


def test_runner_submit_propagates_exception() -> None:
    runner = MCPRunner()
    try:
        async def _raises() -> None:
            raise ValueError("crafted")
        with pytest.raises(ValueError, match="crafted"):
            runner.submit(_raises())
    finally:
        runner.close()


def test_runner_submit_honours_timeout() -> None:
    runner = MCPRunner()
    try:
        async def _slow() -> None:
            await asyncio.sleep(2.0)
        t0 = time.monotonic()
        with pytest.raises(TimeoutError):
            runner.submit(_slow(), timeout=0.1)
        elapsed = time.monotonic() - t0
        # We should have given up well before the 2-second sleep finishes.
        assert elapsed < 0.5, f"timeout took {elapsed}s"
    finally:
        runner.close()


def test_runner_close_is_idempotent() -> None:
    runner = MCPRunner()
    runner.close()
    runner.close()  # second call must not raise


def test_runner_submit_after_close_raises() -> None:
    runner = MCPRunner()
    runner.close()
    async def _noop() -> None: ...
    with pytest.raises(RuntimeError, match="closed"):
        runner.submit(_noop())


def test_runner_many_submits_share_one_loop() -> None:
    """Verify multiple submits share the same loop (we don't spin up
    a new thread per submit)."""
    runner = MCPRunner()
    try:
        loops_seen: set[int] = set()

        async def _get_loop_id() -> int:
            return id(asyncio.get_running_loop())

        for _ in range(5):
            loops_seen.add(runner.submit(_get_loop_id()))
        assert len(loops_seen) == 1
    finally:
        runner.close()
