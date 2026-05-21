"""``search_well`` tool — happy path + each failure mode."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pytest

from ember.schemas.chunks import RetrievalHit
from ember.schemas.errors import BrunnrError
from ember.schemas.tool import ApprovalPolicy, ToolCall
from ember.spark.funi.tools.registry import clear, lookup
from ember.tools import search_well

# --------------------------------------------------------------------- #
# Fixtures + fakes                                                      #
# --------------------------------------------------------------------- #


@pytest.fixture(autouse=True)
def _isolate_registry_and_binding():
    """Each test starts with a clean registry + clean bound state, then
    re-imports search_well to re-register."""
    clear()
    search_well.unbind()
    # Re-execute the side-effect registration.
    import importlib  # noqa: PLC0415
    importlib.reload(search_well)
    yield
    search_well.unbind()
    clear()


class _FakeBrunnr:
    backend_kind = "fake"
    embedding_dim = 8

    def __init__(self, *, hits: Sequence[RetrievalHit] = ()) -> None:
        self._hits = list(hits)
        self.calls: list[tuple[str, ...]] = []

    def hybrid_search(self, qvec, query, k):
        self.calls.append(("hybrid", query, k))
        return self._hits[:k]

    def text_search(self, query, k, filter=None):
        self.calls.append(("text", query, k))
        return self._hits[:k]


class _FakeEmbedder:
    def __init__(self, *, vectors: list[Any] | None = None) -> None:
        self._vectors = vectors or [tuple([0.1] * 8)]

    def embed(self, texts):
        return self._vectors[: len(texts)]


def _call(arguments: dict) -> ToolCall:
    return ToolCall(call_id="c-1", name="search_well", arguments=arguments)


def _hit(chunk_id: int, *, score: float = 0.9, text: str = "x") -> RetrievalHit:
    return RetrievalHit(
        chunk_id=chunk_id, document_id=1,
        document_title="Odin notes", text=text, score=score,
    )


# --------------------------------------------------------------------- #
# Registration                                                          #
# --------------------------------------------------------------------- #


def test_tool_registers_with_standing_approval() -> None:
    entry = lookup("search_well")
    assert entry is not None
    descriptor, _executor = entry
    assert descriptor.required_approval is ApprovalPolicy.STANDING
    assert "query" in descriptor.parameters_schema
    assert "k" in descriptor.parameters_schema


# --------------------------------------------------------------------- #
# Refusals                                                              #
# --------------------------------------------------------------------- #


def test_refuses_when_no_brunnr_bound() -> None:
    _descriptor, execute = lookup("search_well")  # type: ignore[misc]
    reply = execute(_call({"query": "Odin", "k": 3}))
    assert reply.output == ""
    assert "no Brunnr handle bound" in (reply.error or "")


def test_refuses_empty_query() -> None:
    search_well.bind_brunnr(_FakeBrunnr(hits=[_hit(1)]))
    _descriptor, execute = lookup("search_well")  # type: ignore[misc]
    reply = execute(_call({"query": "   ", "k": 3}))
    assert reply.output == ""
    assert "empty query" in (reply.error or "")


# --------------------------------------------------------------------- #
# Happy paths                                                           #
# --------------------------------------------------------------------- #


def test_text_search_path_when_no_embedder() -> None:
    """No embedder bound → falls straight to text_search."""
    fake = _FakeBrunnr(hits=[_hit(7, score=0.42, text="Odin sacrificed an eye.")])
    search_well.bind_brunnr(fake)
    _descriptor, execute = lookup("search_well")  # type: ignore[misc]

    reply = execute(_call({"query": "Odin", "k": 1}))

    assert reply.error is None
    assert "chunk 7" in reply.output
    assert "Odin sacrificed" in reply.output
    assert fake.calls == [("text", "Odin", 1)]


def test_hybrid_path_when_embedder_returns_vector() -> None:
    fake = _FakeBrunnr(hits=[_hit(9, score=0.81, text="Allfather hung on Yggdrasil.")])
    search_well.bind_brunnr(fake, embedder=_FakeEmbedder())
    _descriptor, execute = lookup("search_well")  # type: ignore[misc]

    reply = execute(_call({"query": "Allfather", "k": 1}))

    assert reply.error is None
    assert "chunk 9" in reply.output
    assert fake.calls == [("hybrid", "Allfather", 1)]


def test_falls_back_to_text_when_embedder_returns_none() -> None:
    fake = _FakeBrunnr(hits=[_hit(3)])
    bad_embedder = _FakeEmbedder(vectors=[None])
    search_well.bind_brunnr(fake, embedder=bad_embedder)
    _descriptor, execute = lookup("search_well")  # type: ignore[misc]

    reply = execute(_call({"query": "Freyja", "k": 2}))

    assert reply.error is None
    assert fake.calls[0][0] == "text"


def test_falls_back_to_text_when_hybrid_raises_brunnr_error() -> None:
    class _BadHybrid(_FakeBrunnr):
        def hybrid_search(self, qvec, query, k):
            self.calls.append(("hybrid-failed", query, k))
            raise BrunnrError("dim mismatch")

    fake = _BadHybrid(hits=[_hit(5)])
    search_well.bind_brunnr(fake, embedder=_FakeEmbedder())
    _descriptor, execute = lookup("search_well")  # type: ignore[misc]

    reply = execute(_call({"query": "Tyr", "k": 1}))

    assert reply.error is None
    # First call attempted hybrid; then text_search.
    kinds = [call[0] for call in fake.calls]
    assert kinds == ["hybrid-failed", "text"]


def test_no_hits_renders_helpful_no_results_line() -> None:
    search_well.bind_brunnr(_FakeBrunnr(hits=[]))
    _descriptor, execute = lookup("search_well")  # type: ignore[misc]
    reply = execute(_call({"query": "nonsense words xyz", "k": 5}))
    assert reply.error is None
    assert "no results" in reply.output


def test_k_is_clamped_to_max() -> None:
    fake = _FakeBrunnr(hits=[_hit(i) for i in range(50)])
    search_well.bind_brunnr(fake)
    _descriptor, execute = lookup("search_well")  # type: ignore[misc]

    execute(_call({"query": "x", "k": 999}))
    # Tool clamps to _MAX_K = 25 before calling Brunnr.
    assert fake.calls[0][2] == 25


def test_k_below_one_is_clamped_to_one() -> None:
    fake = _FakeBrunnr(hits=[_hit(1)])
    search_well.bind_brunnr(fake)
    _descriptor, execute = lookup("search_well")  # type: ignore[misc]
    execute(_call({"query": "x", "k": 0}))
    assert fake.calls[0][2] == 1


def test_text_preview_is_bounded_for_long_chunks() -> None:
    long_text = "Lorem ipsum " * 200  # well over 240 chars
    fake = _FakeBrunnr(hits=[_hit(1, text=long_text)])
    search_well.bind_brunnr(fake)
    _descriptor, execute = lookup("search_well")  # type: ignore[misc]
    reply = execute(_call({"query": "lorem", "k": 1}))
    assert reply.error is None
    # The output contains the truncation marker.
    assert "..." in reply.output
