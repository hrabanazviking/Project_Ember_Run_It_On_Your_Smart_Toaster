"""E-030 — Error honesty: failures are spoken, never fabricated.

Before E-030 three failures in the chat session were silent, and
one stored record lied by omission:

* docket 85 — ``add_episode`` exceptions were suppressed with no
  warning, so a session could believe it was remembering when the
  store was not;
* docket 86 — a mid-session ``BrunnrError`` in retrieval yielded
  no hits and no signal, indistinguishable from an honestly empty
  Well (the prompt even assembled as if a search had happened and
  found nothing);
* the startup history load (E-021) suppressed its reader failure
  the same way;
* a reply that ended in an ERROR, or was cut off at LENGTH, was
  persisted as bare text — a later session reading its history
  back met the error text, or the partial answer, as if Ember had
  completed the turn.

These tests pin the E-030 shape, point by point:

1. A save failure warns at that moment, in plain words, and the
   session keeps serving (the turn lives in memory only).
2. A search failure warns for that turn, the prompt carries the
   do-not-invent instruction, and the Episode is flagged
   ``well_disconnected`` — the turn is ungrounded in fact.
3. A non-``BrunnrError`` backend exception from search is spoken
   too (the catch is broad, like persistence's).
4. An embedding failure alone is NOT a retrieval failure: text
   search still runs and its real hits ground the turn.
5. A history-load failure warns at startup; the session starts
   empty and keeps serving.
6. Streaming and non-streaming ERROR finishes persist with the
   ``[ember reported an error]`` tag.
7. Streaming and non-streaming LENGTH finishes persist with the
   truncation tag.
8. A normal STOP reply persists untagged (control).

No sqlite-vec, no Ollama. Pure double-driven flow, in the
Phase 11/16 test shape.
"""

from __future__ import annotations

import io
from datetime import UTC, datetime
from pathlib import Path

from ember.schemas.chunks import BrunnrStats, RetrievalHit
from ember.schemas.config import (
    BrunnrConfig,
    EmberConfig,
    FuniConfig,
    IdentityConfig,
    SqliteVecConfig,
    StrengrConfig,
)
from ember.schemas.errors import BrunnrError, Disconnected, DisconnectReason
from ember.schemas.funi import FinishReason, FuniHealth, FuniReply
from ember.schemas.stream import FuniStreamChunk
from ember.spark.hjarta import save_identity_atomic
from ember.spark.munnr import chat, render

ERROR_TAG = render.ERROR_TAG
TRUNCATED_TAG = render.TRUNCATED_TAG

# --------------------------------------------------------------------- #
# Shared helpers                                                          #
# --------------------------------------------------------------------- #


def _config(tmp_path: Path, *, streaming: bool) -> EmberConfig:
    return EmberConfig(
        funi=FuniConfig(streaming=streaming),
        strengr=StrengrConfig(retry_backoff_max_s=0.0),
        brunnr=BrunnrConfig(
            embedding_dim=4,
            sqlite_vec=SqliteVecConfig(path=tmp_path / "store.db"),
        ),
    )


def _seed_identity(tmp_path: Path) -> Path:
    save_identity_atomic(tmp_path, IdentityConfig())
    return tmp_path


def _disconnected() -> Disconnected:
    return Disconnected(
        reason=DisconnectReason.CONN_REFUSED,
        since=datetime.now(tz=UTC),
    )


class _NullEmbedder:
    """No vector for any text — retrieval falls back to text search."""

    def embed(self, texts):
        return [None for _ in texts]


class _VectorEmbedder:
    def embed(self, texts):
        return [(0.1, 0.2, 0.3, 0.4) for _ in texts]


class _FailingEmbedder:
    def embed(self, texts):
        raise RuntimeError("embedder down")


class _Brunnr:
    """Capturing Well double with scriptable failure points."""

    backend_kind = "fake"
    embedding_dim = 4

    def __init__(
        self,
        *,
        save_error: Exception | None = None,
        search_error: Exception | None = None,
        history_error: Exception | None = None,
        hits: list[RetrievalHit] | None = None,
    ) -> None:
        self.episodes: list = []
        self._save_error = save_error
        self._search_error = search_error
        self._history_error = history_error
        self._hits = hits or []

    def recent_episodes(self, limit):
        if self._history_error is not None:
            raise self._history_error
        return []

    def add_episode(self, episode):
        if self._save_error is not None:
            raise self._save_error
        self.episodes.append(episode)
        return 1

    def hybrid_search(self, *a, **kw):
        if self._search_error is not None:
            raise self._search_error
        return list(self._hits)

    def text_search(self, *a, **kw):
        if self._search_error is not None:
            raise self._search_error
        return list(self._hits)

    def count(self):  # pragma: no cover
        return BrunnrStats(documents=0, chunks=0, embedded_chunks=0, size_bytes=0)

    def close(self) -> None:
        return None


class _StreamingFuni:
    """Streaming double: scripted chunks, contexts captured."""

    runtime_kind = "fake"
    model_id = "fake:e030"

    def __init__(self, chunks: list[FuniStreamChunk]) -> None:
        self._chunks = list(chunks)
        self.contexts: list[list] = []
        self.streaming_calls = 0

    def complete(self, prompt, context, tools=None):  # pragma: no cover
        raise AssertionError("streaming config must not call complete")

    def complete_streaming(self, prompt, context, tools=None):
        self.streaming_calls += 1
        self.contexts.append(list(context))
        yield from self._chunks

    def health(self):
        return FuniHealth(model_id=self.model_id, last_ok=datetime.now(tz=UTC))

    def close(self):
        return None


def _chunks(text: str, finish: FinishReason) -> list[FuniStreamChunk]:
    return [
        FuniStreamChunk(text_delta=text, done=False),
        FuniStreamChunk(
            text_delta="", done=True, finish_reason=finish, model_id="fake:e030",
        ),
    ]


class _CompleteFuni:
    runtime_kind = "fake"
    model_id = "fake:e030-complete"

    def __init__(self, reply: FuniReply) -> None:
        self._reply = reply
        self.contexts: list[list] = []

    def complete(self, prompt, context, tools=None) -> FuniReply:
        self.contexts.append(list(context))
        return self._reply

    def complete_streaming(self, prompt, context, tools=None):  # pragma: no cover
        raise AssertionError("non-streaming config must not stream")

    def health(self):
        return FuniHealth(model_id=self.model_id, last_ok=datetime.now(tz=UTC))

    def close(self):
        return None


def _run(tmp_path, *, streaming, funi, brunnr, embedder=None, lines="hello\n/exit\n"):
    config_root = _seed_identity(tmp_path / "ember-home")
    stdout = io.StringIO()
    rc = chat.run(
        config=_config(tmp_path, streaming=streaming),
        config_root=config_root,
        stdin=io.StringIO(lines),
        stdout=stdout,
        embed_client=embedder or _NullEmbedder(),
        funi_opener=lambda _cfg: funi,
        strengr_opener=lambda _s, _b: brunnr,
    )
    return rc, stdout.getvalue()


def _system_text(context) -> str:
    return next(item.text for item in context if item.kind.value == "system")


# --------------------------------------------------------------------- #
# 1. Docket 85 — a save failure is spoken                                 #
# --------------------------------------------------------------------- #


def test_save_failure_warns_and_session_keeps_serving(tmp_path: Path) -> None:
    funi = _StreamingFuni(_chunks("an answer", FinishReason.STOP))
    brunnr = _Brunnr(save_error=RuntimeError("disk full"))
    rc, out = _run(
        tmp_path, streaming=True, funi=funi, brunnr=brunnr,
        lines="one\ntwo\n/exit\n",
    )
    assert rc == 0
    # Both turns were generated; each failed save was spoken at the
    # moment it happened, with the consequence named plainly.
    assert funi.streaming_calls == 2
    assert out.count("this turn could not be saved to the Well") == 2
    assert "RuntimeError: disk full" in out
    assert "remembered only until this session ends" in out
    # Nothing reached the store — and now the operator knows that.
    assert brunnr.episodes == []


# --------------------------------------------------------------------- #
# 2 + 3. Docket 86 — a search failure is spoken, the turn ungrounded      #
# --------------------------------------------------------------------- #


def test_search_failure_warns_ungrounds_and_flags_episode(
    tmp_path: Path,
) -> None:
    funi = _StreamingFuni(_chunks("unguarded answer", FinishReason.STOP))
    brunnr = _Brunnr(search_error=BrunnrError("well hurt"))
    rc, out = _run(tmp_path, streaming=True, funi=funi, brunnr=brunnr)
    assert rc == 0
    assert "search failed for this message" in out
    assert "BrunnrError: well hurt" in out
    assert "will not be grounded in your documents" in out
    # The prompt told the model the truth for this turn: the
    # do-not-invent instruction, not the no-excerpts shrug.
    assert "well of knowledge is currently unreachable" in _system_text(
        funi.contexts[0]
    )
    # The stored Episode is flagged ungrounded, as a disconnect
    # turn's is.
    assert len(brunnr.episodes) == 1
    assert brunnr.episodes[0].well_disconnected is True


def test_search_failure_from_low_level_backend_error_is_spoken(
    tmp_path: Path,
) -> None:
    # Adapters can let lower-level exceptions through on a stale
    # connection; the broad catch speaks those too.
    hits, failure = chat._retrieve(
        "anything", _Brunnr(search_error=RuntimeError("db gone")),
        _VectorEmbedder(),
    )
    assert hits == []
    assert failure == "RuntimeError: db gone"


# --------------------------------------------------------------------- #
# 4. Embedding failure alone is not a retrieval failure                   #
# --------------------------------------------------------------------- #


def test_embedding_failure_degrades_to_real_text_search(tmp_path: Path) -> None:
    hit = RetrievalHit(
        chunk_id=7, document_id=3, document_title="Saga",
        text="a real excerpt", score=0.5,
    )
    hits, failure = chat._retrieve(
        "anything", _Brunnr(hits=[hit]), _FailingEmbedder(),
    )
    assert failure is None
    assert hits == [hit]


def test_successful_search_does_not_warn_and_grounds(tmp_path: Path) -> None:
    funi = _StreamingFuni(_chunks("grounded answer", FinishReason.STOP))
    brunnr = _Brunnr()
    rc, out = _run(tmp_path, streaming=True, funi=funi, brunnr=brunnr)
    assert rc == 0
    assert "search failed" not in out
    assert len(brunnr.episodes) == 1
    assert brunnr.episodes[0].well_disconnected is False


# --------------------------------------------------------------------- #
# 5. A history-load failure is spoken at startup                          #
# --------------------------------------------------------------------- #


def test_history_load_failure_warns_and_session_starts_empty(
    tmp_path: Path,
) -> None:
    funi = _StreamingFuni(_chunks("fresh answer", FinishReason.STOP))
    brunnr = _Brunnr(history_error=BrunnrError("store unreadable"))
    rc, out = _run(tmp_path, streaming=True, funi=funi, brunnr=brunnr)
    assert rc == 0
    assert "your saved conversations could not be loaded" in out
    assert "they have not been deleted" in out
    # The session still served the turn, starting from no history.
    assert funi.streaming_calls == 1
    assert len(brunnr.episodes) == 1


# --------------------------------------------------------------------- #
# 6 + 7. Failed / partial finishes persist tagged                         #
# --------------------------------------------------------------------- #


def test_streaming_error_finish_persists_tagged(tmp_path: Path) -> None:
    funi = _StreamingFuni(
        _chunks("[ollama unreachable: boom]", FinishReason.ERROR)
    )
    brunnr = _Brunnr()
    rc, out = _run(tmp_path, streaming=True, funi=funi, brunnr=brunnr)
    assert rc == 0
    assert ERROR_TAG in out  # the screen tag, as before E-030
    assert len(brunnr.episodes) == 1
    assert brunnr.episodes[0].ember_reply == (
        f"{ERROR_TAG} [ollama unreachable: boom]"
    )


def test_nonstreaming_error_finish_persists_tagged(tmp_path: Path) -> None:
    funi = _CompleteFuni(FuniReply(
        text="[ollama unreachable: boom]",
        finish_reason=FinishReason.ERROR,
        model_id="fake:e030-complete",
    ))
    brunnr = _Brunnr()
    rc, out = _run(tmp_path, streaming=False, funi=funi, brunnr=brunnr)
    assert rc == 0
    assert ERROR_TAG in out
    assert len(brunnr.episodes) == 1
    assert brunnr.episodes[0].ember_reply == (
        f"{ERROR_TAG} [ollama unreachable: boom]"
    )


def test_streaming_length_finish_persists_tagged(tmp_path: Path) -> None:
    funi = _StreamingFuni(_chunks("a partial ans", FinishReason.LENGTH))
    brunnr = _Brunnr()
    rc, out = _run(tmp_path, streaming=True, funi=funi, brunnr=brunnr)
    assert rc == 0
    assert TRUNCATED_TAG in out
    assert len(brunnr.episodes) == 1
    assert brunnr.episodes[0].ember_reply == f"a partial ans {TRUNCATED_TAG}"


def test_nonstreaming_length_finish_persists_tagged(tmp_path: Path) -> None:
    funi = _CompleteFuni(FuniReply(
        text="a partial ans",
        finish_reason=FinishReason.LENGTH,
        model_id="fake:e030-complete",
    ))
    brunnr = _Brunnr()
    rc, out = _run(tmp_path, streaming=False, funi=funi, brunnr=brunnr)
    assert rc == 0
    assert TRUNCATED_TAG in out
    assert len(brunnr.episodes) == 1
    assert brunnr.episodes[0].ember_reply == f"a partial ans {TRUNCATED_TAG}"


# --------------------------------------------------------------------- #
# 8. Control — a normal reply persists untagged                           #
# --------------------------------------------------------------------- #


def test_stop_finish_persists_untagged(tmp_path: Path) -> None:
    funi = _StreamingFuni(_chunks("a full answer", FinishReason.STOP))
    brunnr = _Brunnr()
    rc, _out = _run(tmp_path, streaming=True, funi=funi, brunnr=brunnr)
    assert rc == 0
    assert len(brunnr.episodes) == 1
    assert brunnr.episodes[0].ember_reply == "a full answer"


def test_tag_failed_finish_leaves_other_finishes_alone() -> None:
    assert chat._tag_failed_finish("plain", FinishReason.STOP) == "plain"
    assert chat._tag_failed_finish("no", FinishReason.REFUSED) == "no"
    assert chat._tag_failed_finish("calls", FinishReason.TOOL_CALL) == "calls"
    assert chat._tag_failed_finish("plain", None) == "plain"
    assert chat._tag_failed_finish("", FinishReason.ERROR) == ERROR_TAG
    assert chat._tag_failed_finish("", FinishReason.LENGTH) == TRUNCATED_TAG
