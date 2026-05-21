"""Hjarta FSM — happy path + every documented abort point.

Uses scripted IO + injected Funi/Strengr openers; no real Ollama, no
sqlite_vec dependency. The integration test against the real backends
lives in ``tests/integration/test_phase6_acceptance.py``.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from ember.schemas.chunks import BrunnrStats, Document, RetrievalHit
from ember.schemas.config import EmberConfig
from ember.schemas.errors import Disconnected, DisconnectReason
from ember.schemas.funi import FuniHealth, Unavailable, UnavailableReason
from ember.spark.hjarta import HjartaIO, HjartaState, has_identity
from ember.spark.hjarta import run as hjarta_run
from ember.spark.hjarta.identity import load_identity

# --------------------------------------------------------------------- #
# Test doubles                                                          #
# --------------------------------------------------------------------- #


class _FakeFuni:
    runtime_kind = "fake"
    model_id = "fake:tiny"
    embedding_dim = 4

    def complete(self, *args, **kwargs):  # pragma: no cover — not exercised in Hjarta
        raise AssertionError("Hjarta does not call Funi.complete")

    def complete_streaming(self, *args, **kwargs):  # pragma: no cover — not exercised in Hjarta
        raise AssertionError("Hjarta does not call Funi.complete_streaming")
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
        self._next_id = 1

    def add_document(self, doc: Document) -> int:
        if doc.hash in self._docs:
            return self._docs[doc.hash]
        new_id = self._next_id
        self._next_id += 1
        self._docs[doc.hash] = new_id
        return new_id

    def add_chunks(self, chunks):
        ids = []
        for chunk in chunks:
            new_id = self._next_id
            self._next_id += 1
            self._chunks.append((new_id, chunk.text))
            ids.append(new_id)
        return ids

    def add_episode(self, episode):  # pragma: no cover — not used in Hjarta
        return 1

    def vector_search(self, qvec, k, filter=None):  # pragma: no cover
        return []

    def text_search(self, query: str, k: int, filter=None) -> list[RetrievalHit]:
        matches: list[RetrievalHit] = []
        needle = query.lower()
        for cid, text in self._chunks:
            if any(word in text.lower() for word in needle.split()):
                matches.append(
                    RetrievalHit(
                        chunk_id=cid,
                        document_id=1,
                        document_title="probe",
                        text=text,
                        score=1.0,
                    )
                )
        return matches[:k]

    def hybrid_search(self, qvec, query, k):  # pragma: no cover
        return self.text_search(query, k)

    def get_document(self, document_id):  # pragma: no cover
        raise NotImplementedError

    def get_chunk(self, chunk_id):  # pragma: no cover
        raise NotImplementedError

    def has_document(self, content_hash):
        return self._docs.get(content_hash)

    def count(self) -> BrunnrStats:  # pragma: no cover
        return BrunnrStats(
            documents=len(self._docs),
            chunks=len(self._chunks),
            embedded_chunks=len(self._chunks),
            size_bytes=0,
        )

    def close(self) -> None:
        return None


def _scripted_io(answers: list[str]) -> tuple[HjartaIO, list[str]]:
    output: list[str] = []
    answer_iter = iter(answers)

    def prompt(_text: str) -> str:
        return next(answer_iter, "")

    def info(text: str) -> None:
        output.append(text)

    def error(text: str) -> None:
        output.append("ERROR: " + text)

    return HjartaIO(prompt=prompt, info=info, error=error), output


def _opener_returning(value):
    def opener(*args, **kwargs):
        return value

    return opener


def _config() -> EmberConfig:
    return EmberConfig()


# --------------------------------------------------------------------- #
# Happy path                                                            #
# --------------------------------------------------------------------- #


def test_happy_path_writes_identity_and_returns_done(tmp_path: Path) -> None:
    io, output = _scripted_io(["", "", "", "Sigrún"])
    outcome = hjarta_run(
        config=_config(),
        config_root=tmp_path,
        io=io,
        funi_opener=_opener_returning(_FakeFuni()),
        strengr_opener=_opener_returning(_FakeBrunnr()),
    )
    assert outcome.success is True
    assert outcome.final_state is HjartaState.DONE
    assert outcome.identity_path is not None
    assert outcome.identity_path.is_file()
    assert has_identity(tmp_path)

    # And the operator-chosen name made it into the saved identity.
    loaded = load_identity(tmp_path)
    assert loaded.name == "Sigrún"

    # Render output mentions the chosen name in the Done banner.
    assert any("Sigrún" in line for line in output)


def test_blank_name_keeps_default(tmp_path: Path) -> None:
    io, _ = _scripted_io(["", "", "", ""])
    outcome = hjarta_run(
        config=_config(),
        config_root=tmp_path,
        io=io,
        funi_opener=_opener_returning(_FakeFuni()),
        strengr_opener=_opener_returning(_FakeBrunnr()),
    )
    assert outcome.success is True

    loaded = load_identity(tmp_path)
    assert loaded.name == "Ember"


# --------------------------------------------------------------------- #
# Abort paths                                                            #
# --------------------------------------------------------------------- #


def test_aborts_at_greet_when_operator_cancels(tmp_path: Path) -> None:
    io, _ = _scripted_io(["cancel"])
    outcome = hjarta_run(
        config=_config(),
        config_root=tmp_path,
        io=io,
        funi_opener=_opener_returning(_FakeFuni()),
        strengr_opener=_opener_returning(_FakeBrunnr()),
    )
    assert outcome.success is False
    assert outcome.final_state is HjartaState.GREET
    assert outcome.identity_path is None
    assert not has_identity(tmp_path)


def test_aborts_when_funi_is_unavailable(tmp_path: Path) -> None:
    io, output = _scripted_io(["", ""])
    outcome = hjarta_run(
        config=_config(),
        config_root=tmp_path,
        io=io,
        funi_opener=_opener_returning(
            Unavailable(
                reason=UnavailableReason.ENDPOINT_UNREACHABLE,
                detail="connection refused",
            )
        ),
        strengr_opener=_opener_returning(_FakeBrunnr()),
    )
    assert outcome.success is False
    assert outcome.final_state is HjartaState.DISCOVER_FUNI
    assert not has_identity(tmp_path)
    # And the error was surfaced via the IO error channel.
    assert any("ERROR" in line and "unavailable" in line.lower() for line in output)


def test_aborts_when_well_is_disconnected(tmp_path: Path) -> None:
    io, _ = _scripted_io(["", "", ""])
    outcome = hjarta_run(
        config=_config(),
        config_root=tmp_path,
        io=io,
        funi_opener=_opener_returning(_FakeFuni()),
        strengr_opener=_opener_returning(
            Disconnected(
                reason=DisconnectReason.BACKEND_REPORTED_UNAVAILABLE,
                since=datetime.now(tz=UTC),
                detail="sqlite vec load failed",
            )
        ),
    )
    assert outcome.success is False
    assert outcome.final_state is HjartaState.CONFIGURE_WELL
    assert not has_identity(tmp_path)


def test_does_not_write_identity_when_probe_fails(tmp_path: Path) -> None:
    """A Brunnr that loses chunks should abort before WriteIdentity."""
    class _BrokenBrunnr(_FakeBrunnr):
        def text_search(self, query, k, filter=None):
            return []  # probe never finds itself

    io, _ = _scripted_io(["", "", ""])
    outcome = hjarta_run(
        config=_config(),
        config_root=tmp_path,
        io=io,
        funi_opener=_opener_returning(_FakeFuni()),
        strengr_opener=_opener_returning(_BrokenBrunnr()),
    )
    assert outcome.success is False
    assert outcome.final_state is HjartaState.TEST_RETRIEVAL
    assert not has_identity(tmp_path)


def test_keyboard_interrupt_during_prompt_is_a_clean_abort(tmp_path: Path) -> None:
    def prompt_then_interrupt(_text: str) -> str:
        raise KeyboardInterrupt

    io = HjartaIO(prompt=prompt_then_interrupt, info=lambda _s: None, error=lambda _s: None)
    outcome = hjarta_run(
        config=_config(),
        config_root=tmp_path,
        io=io,
        funi_opener=_opener_returning(_FakeFuni()),
        strengr_opener=_opener_returning(_FakeBrunnr()),
    )
    assert outcome.success is False
    assert not has_identity(tmp_path)
