"""``search_well`` — first-party tool that queries the Well.

The safest tool in the first three, so the descriptor declares
:class:`ApprovalPolicy.STANDING` — the operator doesn't have to
approve every query.

Calls :meth:`BrunnrHandle.hybrid_search` when an embedder is bound and
the query embedding succeeds, otherwise falls back to
:meth:`BrunnrHandle.text_search`. The bound :class:`BrunnrHandle` is
set once at chat-loop startup via :func:`bind_brunnr` — see
``README.md`` §4 for the host-state pattern.
"""

from __future__ import annotations

import time
from collections.abc import Sequence

from ember.schemas.chunks import RetrievalHit
from ember.schemas.errors import BrunnrError
from ember.schemas.tool import (
    ApprovalPolicy,
    ToolCall,
    ToolDescriptor,
    ToolParameter,
    ToolParameterKind,
    ToolReply,
)
from ember.spark.funi.tools.registry import register

# Module-level binding (the "host state" pattern from README §4). The
# host (Munnr) calls bind_brunnr(handle) once at chat-loop setup; the
# executor reads this. Tests inject via the same setter and call
# unbind() in teardown.
_BOUND_BRUNNR: object | None = None  # typed loosely so we don't pull BrunnrHandle into Spark
_BOUND_EMBEDDER: object | None = None

_NAME = "search_well"
_DEFAULT_K = 5
_MAX_K = 25
_MAX_OUTPUT_HITS_PREVIEW_CHARS = 240  # per hit


_DESCRIPTOR = ToolDescriptor(
    name=_NAME,
    description=(
        "Search the operator's Well (knowledge base) for chunks relevant "
        "to a query. Returns up to k cited results. Safe — read-only."
    ),
    parameters_schema={
        "query": ToolParameter(
            kind=ToolParameterKind.STRING,
            description="Natural-language search query.",
        ),
        "k": ToolParameter(
            kind=ToolParameterKind.INTEGER,
            description=f"Number of results to return (1-{_MAX_K}).",
            required=False,
            default=_DEFAULT_K,
        ),
    },
    required_approval=ApprovalPolicy.STANDING,
    timeout_s=15.0,
)


def bind_brunnr(brunnr: object, embedder: object | None = None) -> None:
    """Wire the live :class:`BrunnrHandle` (and optional embedder) into the tool.

    Called once by Munnr at chat-loop startup (Phase 16). ``embedder``
    is the same callable Smiðja uses (``OllamaEmbedClient``-shaped);
    when missing or when embedding fails, the tool falls back to
    :meth:`text_search`.
    """
    global _BOUND_BRUNNR, _BOUND_EMBEDDER  # noqa: PLW0603 — module-level binding by design
    _BOUND_BRUNNR = brunnr
    _BOUND_EMBEDDER = embedder


def unbind() -> None:
    """Clear the bound state. Production callers don't use this; tests do."""
    global _BOUND_BRUNNR, _BOUND_EMBEDDER  # noqa: PLW0603 — module-level binding by design
    _BOUND_BRUNNR = None
    _BOUND_EMBEDDER = None


def _execute(call: ToolCall) -> ToolReply:
    started = time.monotonic()

    if _BOUND_BRUNNR is None:
        return ToolReply(
            call_id=call.call_id,
            error=(
                "search_well: no Brunnr handle bound; "
                "the host must call ember.tools.search_well.bind_brunnr(...) "
                "at startup"
            ),
            elapsed_s=time.monotonic() - started,
        )

    query = str(call.arguments.get("query", "")).strip()
    if not query:
        return ToolReply(
            call_id=call.call_id,
            error="search_well: empty query",
            elapsed_s=time.monotonic() - started,
        )

    k = _clamp_k(call.arguments.get("k", _DEFAULT_K))

    hits = _try_hybrid_then_text(query, k)
    output = _render_hits(hits, query, k)
    return ToolReply(
        call_id=call.call_id,
        output=output,
        elapsed_s=time.monotonic() - started,
    )


def _clamp_k(raw: object) -> int:
    try:
        k = int(raw)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return _DEFAULT_K
    if k < 1:
        return 1
    if k > _MAX_K:
        return _MAX_K
    return k


def _try_hybrid_then_text(query: str, k: int) -> Sequence[RetrievalHit]:
    """Try hybrid_search if an embedder + matching dim is available;
    otherwise fall back to text_search."""
    if _BOUND_EMBEDDER is not None:
        try:
            qvec = _embed_one(query)
        except Exception:
            qvec = None
        if qvec is not None:
            try:
                return _BOUND_BRUNNR.hybrid_search(  # type: ignore[attr-defined]
                    list(qvec), query, k=k,
                )
            except BrunnrError:
                pass  # fall through to text_search
    try:
        return _BOUND_BRUNNR.text_search(query, k=k)  # type: ignore[attr-defined]
    except BrunnrError as exc:
        # Bubble up as a typed-error ToolReply via the executor's catch
        # in the framework — but the framework only catches generic
        # exceptions, so we re-raise as one.
        raise RuntimeError(f"search_well: Brunnr text_search failed: {exc}") from exc


def _embed_one(query: str) -> tuple[float, ...] | None:
    """Embed a single query string via the bound embedder.

    The embedder shape matches :class:`OllamaEmbedClient` — ``.embed(texts)``
    returns ``list[tuple[float, ...] | None]``. Missing / mismatched
    dim → None, which the caller treats as "fall back to text_search".
    """
    embedder = _BOUND_EMBEDDER
    if embedder is None:
        return None
    vectors = embedder.embed([query])  # type: ignore[attr-defined]
    if not vectors:
        return None
    first = vectors[0]
    if first is None:
        return None
    # Dim check is done implicitly by the Brunnr handle's hybrid_search,
    # which raises BrunnrError on mismatch — we catch that above.
    return tuple(float(x) for x in first)


def _render_hits(
    hits: Sequence[RetrievalHit], query: str, k: int,
) -> str:
    """Format hits for the operator + the next Funi turn's context.

    Concise: one block per hit, with title / chunk id / score / a
    bounded text preview. Funi can cite by chunk id; Munnr will render
    the citations footer when the reply lands.
    """
    if not hits:
        return f"search_well({query!r}, k={k}): no results"

    lines = [f"search_well({query!r}, k={k}) → {len(hits)} result(s):"]
    for hit in hits:
        title = hit.document_title or "(untitled)"
        preview = hit.text.strip().replace("\n", " ")
        if len(preview) > _MAX_OUTPUT_HITS_PREVIEW_CHARS:
            preview = preview[:_MAX_OUTPUT_HITS_PREVIEW_CHARS].rstrip() + "..."
        lines.append(
            f"- chunk {hit.chunk_id} | {title} | score={hit.score:.3f}\n"
            f"  {preview}"
        )
    return "\n".join(lines)


# Side-effect registration — see ember.tools README §1.
register(_DESCRIPTOR, _execute)


__all__ = ["bind_brunnr", "unbind"]
