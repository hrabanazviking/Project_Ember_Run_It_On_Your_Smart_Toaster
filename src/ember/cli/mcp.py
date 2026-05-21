"""CLI handlers for ``ember mcp …`` subcommands (ADR-0014).

Each function returns an exit code (0 = success, non-zero = failure)
and never raises — operator-facing CLI errors are written to stdout.

The MCP package import is lazy so operators who haven't installed the
``[mcp]`` extra get a friendly message rather than an ImportError
traceback.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TextIO

from ember.schemas.config import EmberConfig

# --------------------------------------------------------------------- #
# `ember mcp list`                                                      #
# --------------------------------------------------------------------- #


def list_servers(*, config: EmberConfig, stdout: TextIO) -> int:
    """Show the operator's configured MCP servers and their state.

    Doesn't actually spawn them — just lists the config + indicates
    whether each is currently configured to start (mcp.enabled gate).
    """
    if not config.mcp.servers:
        stdout.write("No MCP servers configured.\n")
        stdout.write(
            "Add servers under `mcp.servers:` in ember.yaml. See "
            "docs/decisions/0014-mcp-bidirectional.md.\n"
        )
        return 0
    state = "ENABLED" if config.mcp.enabled else "DISABLED (set mcp.enabled: true)"
    stdout.write(f"MCP client: {state}\n")
    stdout.write(
        f"MCP server (ember-as-server): "
        f"{'EXPOSED' if config.mcp.expose_self else 'NOT EXPOSED'}\n"
    )
    stdout.write(f"\nConfigured servers ({len(config.mcp.servers)}):\n")
    for spec in config.mcp.servers:
        auto = sorted(spec.auto_approve)
        auto_str = f" auto_approve={auto!r}" if auto else ""
        stdout.write(
            f"  - {spec.name}: {spec.command} {' '.join(spec.args)}{auto_str}\n"
        )
    return 0


# --------------------------------------------------------------------- #
# `ember mcp tools`                                                     #
# --------------------------------------------------------------------- #


def list_tools(*, config: EmberConfig, stdout: TextIO) -> int:
    """Show all registered tools — first-party + MCP-bridged.

    Requires spawning MCP servers to discover their tools (the registry
    is empty until they're loaded). If ``mcp.enabled`` is false or the
    extra isn't installed, lists only first-party tools.
    """
    # Side-effect imports register the first-party tools.
    import ember.tools  # noqa: F401, PLC0415
    from ember.spark.funi.tools import list_tools as registry_list  # noqa: PLC0415

    pool = None
    if config.mcp.enabled and config.mcp.servers:
        try:
            from ember.mcp.bridge import register_pool_tools  # noqa: PLC0415
            from ember.mcp.client import MCPClientPool  # noqa: PLC0415
        except ImportError as exc:
            stdout.write(
                f"MCP enabled in config but `mcp` package not installed: {exc}\n"
                f"Install with `pip install ember-agent[mcp]` to discover "
                f"MCP-server tools.\n"
            )
        else:
            pool = MCPClientPool(config.mcp)
            try:
                pool.open()
                register_pool_tools(pool, config.mcp.servers)
            except Exception as exc:
                stdout.write(f"warning: MCP pool open failed: {exc}\n")

    try:
        descriptors = registry_list()
        if not descriptors:
            stdout.write("No tools registered.\n")
            return 0
        stdout.write(f"Registered tools ({len(descriptors)}):\n")
        for d in descriptors:
            policy = d.required_approval.value
            stdout.write(f"  - {d.name} [{policy}] — {d.description}\n")
    finally:
        if pool is not None:
            pool.close()
    return 0


# --------------------------------------------------------------------- #
# `ember mcp ping`                                                      #
# --------------------------------------------------------------------- #


def ping(
    *, config: EmberConfig, server: str | None, stdout: TextIO,
) -> int:
    """Health-probe one (or all) configured MCP server(s)."""
    if not config.mcp.servers:
        stdout.write("No MCP servers configured.\n")
        return 1
    try:
        from ember.mcp.client import MCPClientPool  # noqa: PLC0415
    except ImportError as exc:
        stdout.write(
            f"MCP ping requires the `mcp` package: {exc}\n"
            f"Install with `pip install ember-agent[mcp]`.\n"
        )
        return 1

    targets = (
        [s for s in config.mcp.servers if s.name == server]
        if server
        else list(config.mcp.servers)
    )
    if server and not targets:
        stdout.write(f"No MCP server named {server!r} in config.\n")
        return 1

    # Build a scoped MCPConfig containing only the targets so we don't
    # spin up servers the operator didn't ask about.
    from dataclasses import replace  # noqa: PLC0415
    scoped = replace(config.mcp, servers=tuple(targets))

    pool = MCPClientPool(scoped)
    failures = 0
    try:
        pool.open()
        for spec in targets:
            ok = pool.ping(spec.name)
            mark = "OK" if ok else "FAIL"
            stdout.write(f"  {spec.name}: {mark}\n")
            if not ok:
                failures += 1
    finally:
        pool.close()
    return 0 if failures == 0 else 1


# --------------------------------------------------------------------- #
# `ember mcp serve`                                                     #
# --------------------------------------------------------------------- #


def serve(
    *,
    config: EmberConfig,
    config_root: Path,
    transport: str,
    stdout: TextIO,
) -> int:
    """Run Ember as an MCP server (expose self over stdio).

    The MCP protocol owns stdin + stdout once the loop starts; any
    operator-facing output during startup goes to stderr.
    """
    try:
        from ember.mcp.server import run_stdio  # noqa: PLC0415
    except ImportError as exc:
        stdout.write(
            f"`ember mcp serve` requires the `mcp` package: {exc}\n"
            f"Install with `pip install ember-agent[mcp]`.\n"
        )
        return 1

    if transport != "stdio":
        # argparse already restricts choices, but defensive
        stdout.write(f"Unsupported transport {transport!r}; V1 is stdio only.\n")
        return 1

    # Best-effort open the Brunnr handle so the server can answer
    # Well-touching tools. If it fails, we still serve — the tools just
    # return typed errors per Vow of Graceful Offline.
    brunnr = None
    try:
        from ember.thread.strengr import open as strengr_open  # noqa: PLC0415
        outcome = strengr_open(config.strengr, config.brunnr)
        # strengr.open returns the handle on success or a Disconnected.
        # Duck-type it: BrunnrHandle has add_document, Disconnected has reason.
        if hasattr(outcome, "add_document"):
            brunnr = outcome
        else:
            print(
                f"Ember MCP server: Brunnr unavailable "
                f"({getattr(outcome, 'detail', outcome)!r}); "
                f"Well tools will return typed errors.",
                file=sys.stderr,
            )
    except Exception as exc:
        print(
            f"Ember MCP server: Brunnr open raised {type(exc).__name__}: {exc}; "
            f"Well tools will return typed errors.",
            file=sys.stderr,
        )

    try:
        run_stdio(config=config, brunnr=brunnr)
    except KeyboardInterrupt:
        print("\nEmber MCP server stopped.", file=sys.stderr)
    finally:
        if brunnr is not None:
            import contextlib  # noqa: PLC0415
            with contextlib.suppress(Exception):
                brunnr.close()
    return 0


__all__ = ["list_servers", "list_tools", "ping", "serve"]
