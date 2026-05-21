"""Ember as an MCP server — expose Well + diagnostics over MCP.

Per ADR-0014. Builds a FastMCP server with four tools (search_well,
well_status, doctor, recent_episodes) and two resources
(ember://well/status, ember://well/recent-episodes).

The transport is stdio. The ``ember mcp serve`` subcommand wires this
up by:

1. Loading config + opening Brunnr + Funi (best-effort; doctor still
   works with degraded state).
2. Calling ``build_server(...)``.
3. Calling ``mcp.run(transport="stdio")`` — which takes over the
   process's stdio and blocks until SIGINT.

Per ADR-0014 §Transports: stdio is V1 scope. HTTP/SSE transports are
deferred — they would need authn/authz design.

Stdio note: anything the server prints to stdout becomes JSON-RPC
bytes. All operator-visible logging must go to stderr (FastMCP handles
this via its built-in logger).
"""

from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING, Any

from ember.schemas.config import EmberConfig

if TYPE_CHECKING:
    from ember.well.brunnr.handle import BrunnrHandle

logger = logging.getLogger(__name__)


def build_server(
    *,
    config: EmberConfig,
    brunnr: BrunnrHandle | None,
) -> Any:  # mcp.server.fastmcp.FastMCP
    """Construct a FastMCP server exposing Ember's capabilities.

    ``brunnr`` may be None — in that case the well-touching tools
    return a typed error rather than crashing. This keeps
    ``ember mcp serve`` runnable even when the Well is unreachable
    (Vow of Graceful Offline).

    Returns the FastMCP instance; caller invokes ``.run(transport="stdio")``.
    """
    try:
        from mcp.server.fastmcp import FastMCP  # noqa: PLC0415
    except ImportError as exc:
        raise ImportError(
            f"`ember mcp serve` requested but the `mcp` package is not "
            f"installed: {exc}. Install with `pip install ember-agent[mcp]`."
        ) from exc

    mcp = FastMCP(
        name="ember",
        instructions=(
            "Ember exposes its knowledge Well + diagnostics over MCP. "
            "Use `search_well` to query the operator's ingested documents. "
            "Use `well_status` and `doctor` for health information. "
            "Use `recent_episodes` to see the last N chat exchanges."
        ),
    )

    _register_tools(mcp, config=config, brunnr=brunnr)
    _register_resources(mcp, config=config, brunnr=brunnr)

    return mcp


def _register_tools(
    mcp: Any, *, config: EmberConfig, brunnr: BrunnrHandle | None,
) -> None:
    """Decorate the four V1 tools onto the FastMCP instance."""

    @mcp.tool(
        name="search_well",
        description=(
            "Hybrid (vector + full-text) search over the operator's "
            "ingested knowledge Well. Returns the top `k` chunks with "
            "their source document titles and text excerpts."
        ),
    )
    def search_well(query: str, k: int = 5) -> list[dict[str, Any]]:
        if brunnr is None:
            return [{"error": "Well unavailable (Brunnr disconnected)"}]
        from ember.well.smidja.embed_client import (  # noqa: PLC0415
            OllamaEmbedClient,
        )
        # Embed the query via the same Ollama endpoint Ember uses.
        # The MCP server is single-threaded synchronous; we just call
        # the embedder directly.
        embedder = OllamaEmbedClient(config=config.smidja.embedding)
        vecs = embedder.embed([query])
        qvec = vecs[0] if vecs and vecs[0] is not None else None
        if qvec is None:
            return [{"error": "embedding failed (Ollama unreachable?)"}]
        try:
            hits = brunnr.hybrid_search(qvec, query, max(1, int(k)))
        except Exception as exc:
            return [{"error": f"hybrid_search failed: {exc}"}]
        return [
            {
                "chunk_id": h.chunk_id,
                "document_id": h.document_id,
                "document_title": h.document_title,
                "text": h.text,
                "score": h.score,
                "char_start": h.char_start,
                "char_end": h.char_end,
            }
            for h in hits
        ]

    @mcp.tool(
        name="well_status",
        description="Return the Well's BrunnrStats (document + chunk counts, size).",
    )
    def well_status() -> dict[str, Any]:
        if brunnr is None:
            return {"error": "Well unavailable (Brunnr disconnected)"}
        try:
            stats = brunnr.count()
        except Exception as exc:
            return {"error": f"count() failed: {exc}"}
        return {
            "documents": stats.documents,
            "chunks": stats.chunks,
            "embedded_chunks": stats.embedded_chunks,
            "size_bytes": stats.size_bytes,
        }

    @mcp.tool(
        name="doctor",
        description=(
            "Cross-realm health snapshot: Funi (LLM), Strengr (tether), "
            "Brunnr (Well). Each realm reports OK or a reason."
        ),
    )
    def doctor() -> dict[str, Any]:
        # Lightweight: only probe what we already hold.
        result: dict[str, Any] = {"realms": {}}
        if brunnr is None:
            result["realms"]["brunnr"] = {"ok": False, "detail": "disconnected"}
        else:
            try:
                stats = brunnr.count()
                result["realms"]["brunnr"] = {
                    "ok": True,
                    "documents": stats.documents,
                    "chunks": stats.chunks,
                }
            except Exception as exc:
                result["realms"]["brunnr"] = {"ok": False, "detail": str(exc)}
        # Funi probe deferred — would need to open a Funi handle here.
        # For V1, we report it as "unprobed" rather than block startup.
        result["realms"]["funi"] = {"ok": None, "detail": "not probed in MCP doctor"}
        return result

    # Note: `recent_episodes` was scoped for V1 but BrunnrHandle currently
    # has only `add_episode` (write-only). The reader API is deferred to
    # V2 along with the matching MCP tool + resource exposure.


def _register_resources(
    mcp: Any, *, config: EmberConfig, brunnr: BrunnrHandle | None,
) -> None:
    """Register MCP resources — read-only views of Ember state.

    Tools are for *actions* (search, ingest); resources are for *state*
    (current counts, recent activity). Resources don't go through the
    operator-approval flow on the client side — they're more like
    files than commands.
    """

    @mcp.resource(
        "ember://well/status",
        name="well_status",
        description="The Well's current BrunnrStats as a JSON document.",
        mime_type="application/json",
    )
    def status_resource() -> str:
        import json  # noqa: PLC0415
        if brunnr is None:
            return json.dumps({"error": "Well unavailable"})
        try:
            stats = brunnr.count()
            return json.dumps({
                "documents": stats.documents,
                "chunks": stats.chunks,
                "embedded_chunks": stats.embedded_chunks,
                "size_bytes": stats.size_bytes,
            }, indent=2)
        except Exception as exc:
            return json.dumps({"error": str(exc)})

    # Episode resource deferred to V2 (see note on recent_episodes tool).


def run_stdio(*, config: EmberConfig, brunnr: BrunnrHandle | None) -> None:
    """Build + run the server over stdio. Blocks until SIGINT.

    Logs startup to stderr (NOT stdout — stdout is the JSON-RPC channel
    once the loop is running).
    """
    print("Ember MCP server starting on stdio…", file=sys.stderr, flush=True)
    server = build_server(config=config, brunnr=brunnr)
    server.run(transport="stdio")


__all__ = ["build_server", "run_stdio"]
