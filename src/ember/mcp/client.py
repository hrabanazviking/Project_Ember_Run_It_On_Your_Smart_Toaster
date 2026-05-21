"""MCP client pool — spawn external MCP servers, hold sessions, call tools.

Per ADR-0014. The pool owns one ``MCPRunner`` (single asyncio loop on a
daemon thread) and one ``ClientSession`` per configured
``MCPServerSpec``. Sessions are initialized + tools/resources discovered
during ``open()``; tools are surfaced via ``get_descriptors()`` for the
bridge module to register into Ember's tool registry.

Failure semantics:

- Missing ``mcp`` package → typed ``BrunnrError`` at open() (operator
  needs ``pip install ember-agent[mcp]``).
- Server spawn failure → that server's tools are absent; other servers
  continue. Logged warning, no crash.
- Per-call failure → typed ``ToolReply`` with ``error`` set. The chat
  loop is the caller and handles it like any other tool failure.
"""

from __future__ import annotations

import logging
from contextlib import AsyncExitStack
from typing import Any

from ember.mcp.runner import MCPRunner
from ember.schemas.config import MCPConfig, MCPServerSpec

logger = logging.getLogger(__name__)


class MCPClientPool:
    """Holds open sessions for each configured MCP server.

    Lifecycle:

    - ``MCPClientPool(config)`` constructs but does not connect.
    - ``open()`` spawns subprocesses + initializes sessions. Returns
      a list of ``(server_name, tools)`` pairs the bridge module will
      register.
    - ``call_tool(server, tool, args)`` forwards a call synchronously.
    - ``close()`` tears down all sessions + the runner.
    """

    def __init__(self, config: MCPConfig) -> None:
        self._config = config
        self._runner: MCPRunner | None = None
        # Map server_name → (ClientSession, AsyncExitStack). The stack
        # owns both the stdio_client + ClientSession context managers
        # so we can unwind them in one place on close().
        self._sessions: dict[str, tuple[Any, AsyncExitStack]] = {}
        # server_name → list of mcp.types.Tool (cached at open() time so
        # repeated get_descriptors() calls don't re-roundtrip).
        self._tools: dict[str, list[Any]] = {}

    # ------------------------------------------------------------- open

    def open(self) -> dict[str, list[Any]]:
        """Spawn every configured server + initialize sessions.

        Returns ``{server_name: [Tool, ...]}`` for the bridge to
        register. Servers that fail to start are skipped with a
        ``logger.warning``; their entry is absent from the returned
        dict. ``open()`` itself never raises for per-server failures —
        the operator gets a degraded subset rather than a crashed chat.

        Raises ``ImportError`` if the ``mcp`` extra is not installed
        (caller turns this into a ``ConfigError`` at startup).
        """
        # Lazy imports — only paid when the extra is installed and the
        # operator turned MCP on.
        try:
            from mcp.client.session import ClientSession  # noqa: PLC0415
            from mcp.client.stdio import (  # noqa: PLC0415
                StdioServerParameters,
                stdio_client,
            )
        except ImportError as exc:
            raise ImportError(
                f"MCP client requested but the `mcp` package is not installed: "
                f"{exc}. Install with `pip install ember-agent[mcp]`."
            ) from exc

        if self._runner is None:
            self._runner = MCPRunner()

        for spec in self._config.servers:
            try:
                self._open_one(spec, ClientSession, StdioServerParameters, stdio_client)
            except Exception as exc:
                logger.warning(
                    "MCP server %r failed to start: %s. "
                    "Its tools will be unavailable this session.",
                    spec.name, exc,
                )
        return dict(self._tools)

    def _open_one(
        self,
        spec: MCPServerSpec,
        ClientSession: Any,
        StdioServerParameters: Any,
        stdio_client: Any,
    ) -> None:
        """Open one session under a managed AsyncExitStack.

        We hold the stack so ``close()`` can unwind everything for this
        server in one call.
        """
        params = StdioServerParameters(
            command=spec.command,
            args=list(spec.args),
            env=dict(spec.env) if spec.env else None,
            cwd=spec.cwd,
        )

        async def _start() -> tuple[Any, AsyncExitStack, list[Any]]:
            stack = AsyncExitStack()
            try:
                # stdio_client yields (read_stream, write_stream)
                streams = await stack.enter_async_context(stdio_client(params))
                session = await stack.enter_async_context(
                    ClientSession(streams[0], streams[1])
                )
                await session.initialize()
                tools_result = await session.list_tools()
                return session, stack, list(tools_result.tools)
            except Exception:
                await stack.aclose()
                raise

        assert self._runner is not None
        session, stack, tools = self._runner.submit(
            _start(), timeout=self._config.startup_timeout_s
        )
        self._sessions[spec.name] = (session, stack)
        self._tools[spec.name] = tools
        logger.info(
            "MCP server %r ready; discovered %d tool(s)", spec.name, len(tools),
        )

    # ------------------------------------------------------------- call

    def call_tool(
        self,
        server: str,
        tool: str,
        arguments: dict[str, Any],
    ) -> Any:  # mcp.types.CallToolResult
        """Forward a tool call to the named server. Synchronous wrapper.

        Raises ``KeyError`` if the server is not registered (caller
        should turn this into ``ApprovalOutcome.NO_SUCH_TOOL``). Raises
        ``TimeoutError`` if the call exceeds ``config.call_timeout_s``.
        Propagates other exceptions from the MCP server.
        """
        if server not in self._sessions:
            raise KeyError(
                f"MCP server {server!r} not in pool "
                f"(known: {sorted(self._sessions)!r})"
            )
        session, _ = self._sessions[server]

        async def _call() -> Any:
            return await session.call_tool(tool, arguments=arguments)

        assert self._runner is not None
        return self._runner.submit(_call(), timeout=self._config.call_timeout_s)

    # ------------------------------------------------------------- ping

    def ping(self, server: str) -> bool:
        """Send an MCP ping to the named server. Returns True on success."""
        if server not in self._sessions:
            return False
        session, _ = self._sessions[server]

        async def _ping() -> Any:
            return await session.send_ping()

        try:
            assert self._runner is not None
            self._runner.submit(_ping(), timeout=self._config.call_timeout_s)
            return True
        except Exception as exc:
            logger.warning("MCP server %r ping failed: %s", server, exc)
            return False

    def server_names(self) -> list[str]:
        return sorted(self._sessions)

    def tools_for(self, server: str) -> list[Any]:
        return list(self._tools.get(server, ()))

    # ------------------------------------------------------------- close

    def close(self) -> None:
        """Tear down every session + the runner. Idempotent."""
        if self._runner is None:
            return
        # Unwind every server's AsyncExitStack in the loop.
        for name, (_, stack) in list(self._sessions.items()):
            async def _aclose(s: AsyncExitStack = stack) -> None:
                await s.aclose()
            try:
                self._runner.submit(_aclose(), timeout=5.0)
            except Exception as exc:
                logger.warning("MCP server %r close failed: %s", name, exc)
        self._sessions.clear()
        self._tools.clear()
        try:
            self._runner.close()
        finally:
            self._runner = None


__all__ = ["MCPClientPool"]
