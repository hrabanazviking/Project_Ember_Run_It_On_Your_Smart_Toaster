"""Phase 9 acceptance: operator edits ember.yaml → next launch picks it up.

Drives the full Hjarta-writes-then-operator-edits-then-cli-reloads
loop, with mocked Funi/Brunnr so it runs without Ollama or sqlite_vec
on the host.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

from ember.config import load_ember_config
from ember.schemas.chunks import BrunnrStats, RetrievalHit
from ember.schemas.funi import FuniHealth
from ember.spark.hjarta import HjartaIO, has_identity
from ember.spark.hjarta import run as hjarta_run

# --------------------------------------------------------------------- #
# Fakes                                                                  #
# --------------------------------------------------------------------- #


class _FakeFuni:
    runtime_kind = "fake"
    model_id = "fake:tiny"
    embedding_dim = 4

    def complete(self, *a, **kw):  # pragma: no cover — not exercised in Hjarta
        raise AssertionError("not used here")

    def complete_streaming(self, *a, **kw):  # pragma: no cover — not exercised in Hjarta
        raise AssertionError("not used here")
        yield  # make this a generator function

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
        if doc.hash in self._docs:
            return self._docs[doc.hash]
        new_id = len(self._docs) + 1
        self._docs[doc.hash] = new_id
        return new_id

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
        # Match on any token to keep Hjarta's probe happy.
        return [
            RetrievalHit(
                chunk_id=cid, document_id=1, document_title="probe",
                text=text, score=1.0,
            )
            for cid, text in self._chunks if "probe" in text.lower()
        ][:k]

    def hybrid_search(self, *a, **kw):  # pragma: no cover
        return []

    def get_document(self, document_id):  # pragma: no cover
        raise NotImplementedError

    def get_chunk(self, chunk_id):  # pragma: no cover
        raise NotImplementedError

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


# --------------------------------------------------------------------- #
# Acceptance                                                            #
# --------------------------------------------------------------------- #


def test_first_launch_writes_both_identity_and_config(tmp_path: Path) -> None:
    """Hjarta lays down both identity.json and ember.yaml atomically."""
    io_obj, _output = _scripted_io(["", "", "", "Spark"])
    cfg = load_ember_config(tmp_path, skip_env=True)
    outcome = hjarta_run(
        config=cfg,
        config_root=tmp_path,
        io=io_obj,
        funi_opener=lambda _: _FakeFuni(),
        strengr_opener=lambda _s, _b: _FakeBrunnr(),
    )
    assert outcome.success, outcome.detail
    assert has_identity(tmp_path)
    assert (tmp_path / "config" / "ember.yaml").is_file()

    # The follow-up load picks the chosen name out of the file.
    cfg2 = load_ember_config(tmp_path, skip_env=True)
    assert cfg2.identity.name == "Spark"


def test_operator_edit_takes_effect_on_next_load(tmp_path: Path) -> None:
    """The Phase 9 acceptance criterion — edit yaml, see effect."""
    io_obj, _ = _scripted_io(["", "", "", ""])
    cfg = load_ember_config(tmp_path, skip_env=True)
    outcome = hjarta_run(
        config=cfg,
        config_root=tmp_path,
        io=io_obj,
        funi_opener=lambda _: _FakeFuni(),
        strengr_opener=lambda _s, _b: _FakeBrunnr(),
    )
    assert outcome.success

    # Operator hand-edits the yaml between launches.
    yaml_path = tmp_path / "config" / "ember.yaml"
    original = yaml_path.read_text(encoding="utf-8")
    yaml_path.write_text(
        original
        + "\nfuni:\n  ollama:\n    model: qwen2.5:7b-instruct\n",
        encoding="utf-8",
    )

    cfg_after = load_ember_config(tmp_path, skip_env=True)
    assert cfg_after.funi.ollama.model == "qwen2.5:7b-instruct"
    # Identity from Hjarta is preserved through the edit.
    assert cfg_after.identity.name == "Ember"


def test_yaml_failing_to_write_does_not_block_identity(tmp_path: Path) -> None:
    """Hjarta still succeeds when the yaml write fails — identity is load-bearing."""
    # Make the config dir unwritable AFTER identity dir is created.
    # Easiest: pre-create a *file* where the config dir should be.
    (tmp_path / "config").write_text("not a dir", encoding="utf-8")

    io_obj, output = _scripted_io(["", "", "", ""])
    cfg = load_ember_config(tmp_path, skip_env=True)
    outcome = hjarta_run(
        config=cfg,
        config_root=tmp_path,
        io=io_obj,
        funi_opener=lambda _: _FakeFuni(),
        strengr_opener=lambda _s, _b: _FakeBrunnr(),
    )
    assert outcome.success  # identity write succeeded
    assert has_identity(tmp_path)
    # And the operator was warned in IO output.
    assert any("could not write operator config" in line for line in output)


# --------------------------------------------------------------------- #
# Helpers                                                                #
# --------------------------------------------------------------------- #


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
