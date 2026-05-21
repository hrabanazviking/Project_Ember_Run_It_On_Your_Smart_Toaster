"""Phase 16: Hjarta's ADVANCED_TOOLS branch writes tools.enabled into ember.yaml."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

from ember.config import load_ember_config
from ember.schemas.chunks import BrunnrStats, RetrievalHit
from ember.schemas.funi import FuniHealth
from ember.spark.hjarta import HjartaIO
from ember.spark.hjarta import run as hjarta_run


class _FakeFuni:
    runtime_kind = "fake"
    model_id = "fake:tiny"
    embedding_dim = 4

    def complete(self, *a, **kw):  # pragma: no cover — not exercised
        raise AssertionError("not used here")

    def complete_streaming(self, *a, **kw):  # pragma: no cover
        raise AssertionError("not used here")
        yield

    def health(self) -> FuniHealth:
        return FuniHealth(model_id=self.model_id, last_ok=datetime.now(tz=UTC))

    def close(self) -> None:
        return None


class _FakeBrunnr:
    backend_kind = "fake"
    embedding_dim = 4

    def __init__(self) -> None:
        self._docs: dict[str, int] = {}
        self._chunks: list[tuple[int, str]] = []

    def add_document(self, doc):
        self._docs.setdefault(doc.hash, len(self._docs) + 1)
        return self._docs[doc.hash]

    def add_chunks(self, chunks):
        out = []
        for c in chunks:
            cid = len(self._chunks) + 1
            self._chunks.append((cid, c.text))
            out.append(cid)
        return out

    def add_episode(self, ep):  # pragma: no cover
        return 1

    def vector_search(self, *a, **kw):  # pragma: no cover
        return []

    def text_search(self, query: str, k: int, filter=None):
        return [
            RetrievalHit(
                chunk_id=cid, document_id=1, document_title="probe",
                text=text, score=1.0,
            )
            for cid, text in self._chunks if "probe" in text.lower()
        ][:k]

    def hybrid_search(self, *a, **kw):  # pragma: no cover
        return []

    def has_document(self, content_hash):
        return self._docs.get(content_hash)

    def count(self) -> BrunnrStats:
        return BrunnrStats(
            documents=len(self._docs),
            chunks=len(self._chunks),
            embedded_chunks=len(self._chunks),
            size_bytes=0,
        )

    def close(self) -> None:
        return None


def _scripted_io(answers: Sequence[str]) -> tuple[HjartaIO, list[str]]:
    out: list[str] = []
    it = iter(answers)
    return (
        HjartaIO(
            prompt=lambda _t: next(it, ""),
            info=out.append,
            error=lambda s: out.append("ERROR: " + s),
        ),
        out,
    )


def test_answering_yes_writes_tools_enabled_true(tmp_path: Path) -> None:
    cfg = load_ember_config(tmp_path, skip_env=True)
    # Answers in wizard order: greet, choose_funi, choose_well,
    # name_ember, advanced_tools. (DISCOVER_FUNI / CONFIGURE_WELL /
    # TEST_RETRIEVAL have no operator prompts.)
    io_obj, _ = _scripted_io(["", "", "", "", "y"])
    outcome = hjarta_run(
        config=cfg,
        config_root=tmp_path,
        io=io_obj,
        funi_opener=lambda _: _FakeFuni(),
        strengr_opener=lambda _s, _b: _FakeBrunnr(),
    )
    assert outcome.success, outcome.detail

    cfg_after = load_ember_config(tmp_path, skip_env=True)
    assert cfg_after.tools.enabled is True


def test_answering_no_leaves_tools_disabled(tmp_path: Path) -> None:
    cfg = load_ember_config(tmp_path, skip_env=True)
    io_obj, _ = _scripted_io(["", "", "", "", "n"])
    outcome = hjarta_run(
        config=cfg,
        config_root=tmp_path,
        io=io_obj,
        funi_opener=lambda _: _FakeFuni(),
        strengr_opener=lambda _s, _b: _FakeBrunnr(),
    )
    assert outcome.success

    cfg_after = load_ember_config(tmp_path, skip_env=True)
    assert cfg_after.tools.enabled is False


def test_empty_answer_keeps_tools_disabled(tmp_path: Path) -> None:
    """Default is off — the Vow of Sovereignty in the wizard form."""
    cfg = load_ember_config(tmp_path, skip_env=True)
    io_obj, _ = _scripted_io(["", "", "", "", ""])
    outcome = hjarta_run(
        config=cfg,
        config_root=tmp_path,
        io=io_obj,
        funi_opener=lambda _: _FakeFuni(),
        strengr_opener=lambda _s, _b: _FakeBrunnr(),
    )
    assert outcome.success
    cfg_after = load_ember_config(tmp_path, skip_env=True)
    assert cfg_after.tools.enabled is False
