"""Phase 11 acceptance: streaming Munnr REPL.

Drives ``chat.run`` against a fake Funi that emits a small sequence of
:class:`FuniStreamChunk` instances and verifies:

1. The default config takes the streaming branch (``complete_streaming``
   is called, ``complete`` is not).
2. Each chunk's ``text_delta`` lands in stdout in order, so an operator
   would see tokens unfold.
3. The persisted Episode reconstructs the full joined reply.
4. ``KeyboardInterrupt`` mid-stream tags the partial reply with
   ``[interrupted by operator]`` and the REPL still exits cleanly.
5. ``config.funi.streaming = False`` falls back to the legacy
   ``complete`` path unchanged.
6. The disconnect banner renders before tokens start streaming when the
   Well is unreachable.

No sqlite-vec, no Ollama. Pure double-driven flow.
"""

from __future__ import annotations

import io
from collections.abc import Iterator, Sequence
from datetime import UTC, datetime
from pathlib import Path

from ember.schemas.chunks import BrunnrStats
from ember.schemas.config import (
    BrunnrConfig,
    EmberConfig,
    FuniConfig,
    IdentityConfig,
    SqliteVecConfig,
    StrengrConfig,
)
from ember.schemas.errors import Disconnected, DisconnectReason
from ember.schemas.funi import (
    ContextItem,
    FinishReason,
    FuniHealth,
    FuniReply,
)
from ember.schemas.stream import FuniStreamChunk
from ember.spark.hjarta import save_identity_atomic
from ember.spark.munnr import chat

# --------------------------------------------------------------------- #
# Doubles                                                               #
# --------------------------------------------------------------------- #


class _ScriptedStreamingFuni:
    """A fake Funi that streams a pre-scripted sequence of chunks."""

    runtime_kind = "fake"
    model_id = "fake:stream"

    def __init__(self, chunks: Sequence[FuniStreamChunk]) -> None:
        self._chunks = tuple(chunks)
        self.complete_calls = 0
        self.streaming_calls = 0
        self.last_prompt: str | None = None

    def complete(self, prompt: str, context: Sequence[ContextItem], tools=None) -> FuniReply:
        # If we land here in a streaming-enabled test, the assertion in
        # the test will catch the mistake.
        self.complete_calls += 1
        self.last_prompt = prompt
        return FuniReply(
            text="(non-streaming reply)",
            finish_reason=FinishReason.STOP,
            model_id=self.model_id,
        )

    def complete_streaming(
        self, prompt: str, context: Sequence[ContextItem], tools=None,
    ) -> Iterator[FuniStreamChunk]:
        self.streaming_calls += 1
        self.last_prompt = prompt
        yield from self._chunks

    def health(self) -> FuniHealth:
        return FuniHealth(model_id=self.model_id, last_ok=datetime.now(tz=UTC))

    def close(self) -> None:
        return None


class _InterruptingFuni:
    """Yields a few chunks, then raises KeyboardInterrupt to simulate Ctrl-C."""

    runtime_kind = "fake"
    model_id = "fake:interrupt"

    def __init__(self, prefix_chunks: Sequence[FuniStreamChunk]) -> None:
        self._prefix = tuple(prefix_chunks)

    def complete(self, prompt, context, tools=None) -> FuniReply:  # pragma: no cover
        raise AssertionError("non-streaming path not used here")

    def complete_streaming(self, prompt, context, tools=None):
        yield from self._prefix
        raise KeyboardInterrupt

    def health(self) -> FuniHealth:
        return FuniHealth(model_id=self.model_id, last_ok=datetime.now(tz=UTC))

    def close(self) -> None:
        return None


# --------------------------------------------------------------------- #
# Config + setup                                                        #
# --------------------------------------------------------------------- #


def _config(tmp_path: Path, *, streaming: bool = True) -> EmberConfig:
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


# --------------------------------------------------------------------- #
# Acceptance                                                            #
# --------------------------------------------------------------------- #


def test_streaming_default_writes_tokens_in_order_and_takes_stream_path(
    tmp_path: Path,
) -> None:
    config_root = _seed_identity(tmp_path / "ember-home")
    cfg = _config(tmp_path, streaming=True)

    funi = _ScriptedStreamingFuni([
        FuniStreamChunk(text_delta="Hello ", done=False),
        FuniStreamChunk(text_delta="there, ", done=False),
        FuniStreamChunk(text_delta="operator.", done=False),
        FuniStreamChunk(
            text_delta="",
            done=True,
            finish_reason=FinishReason.STOP,
            model_id="fake:stream",
            prompt_tokens=10,
            completion_tokens=3,
        ),
    ])

    stdout = io.StringIO()
    rc = chat.run(
        config=cfg,
        config_root=config_root,
        stdin=io.StringIO("hi\n/exit\n"),
        stdout=stdout,
        funi_opener=lambda _cfg: funi,
        strengr_opener=lambda _s, _b: Disconnected(
            reason=DisconnectReason.CONN_REFUSED,
            since=datetime.now(tz=UTC),
        ),
    )

    assert rc == 0
    assert funi.streaming_calls == 1
    assert funi.complete_calls == 0

    out = stdout.getvalue()
    # The full joined text appears in stdout in order.
    assert "Hello there, operator." in out
    # And the order is left-to-right (delta-by-delta).
    assert out.index("Hello ") < out.index("there, ") < out.index("operator.")


def test_streaming_persists_full_joined_reply_to_episode(tmp_path: Path) -> None:
    """The Episode keeps the reconstructed full reply (Vow of Memory)."""
    config_root = _seed_identity(tmp_path / "ember-home")
    cfg = _config(tmp_path, streaming=True)

    captured: list[dict[str, object]] = []

    funi = _ScriptedStreamingFuni([
        FuniStreamChunk(text_delta="Odin ", done=False),
        FuniStreamChunk(text_delta="hung ", done=False),
        FuniStreamChunk(text_delta="from the World Tree.", done=False),
        FuniStreamChunk(
            text_delta="", done=True, finish_reason=FinishReason.STOP,
            model_id="fake:stream",
        ),
    ])

    class _CapturingBrunnr:
        backend_kind = "fake"
        embedding_dim = 4

        def add_episode(self, episode):
            captured.append({"text": episode.ember_reply, "model": episode.funi_model})
            return 1

        def hybrid_search(self, *a, **kw):
            return []

        def text_search(self, *a, **kw):
            return []

        def count(self):  # pragma: no cover
            return BrunnrStats(documents=0, chunks=0, embedded_chunks=0, size_bytes=0)

        def close(self) -> None:
            return None

    rc = chat.run(
        config=cfg,
        config_root=config_root,
        stdin=io.StringIO("Who hung on the World Tree?\n/exit\n"),
        stdout=io.StringIO(),
        funi_opener=lambda _cfg: funi,
        strengr_opener=lambda _s, _b: _CapturingBrunnr(),
    )
    assert rc == 0
    assert len(captured) == 1
    assert captured[0]["text"] == "Odin hung from the World Tree."
    assert captured[0]["model"] == "fake:stream"


def test_keyboard_interrupt_mid_stream_tags_partial_and_exits_cleanly(
    tmp_path: Path,
) -> None:
    config_root = _seed_identity(tmp_path / "ember-home")
    cfg = _config(tmp_path, streaming=True)

    captured: list[str] = []

    funi = _InterruptingFuni([
        FuniStreamChunk(text_delta="Once upon ", done=False),
        FuniStreamChunk(text_delta="a time ", done=False),
        FuniStreamChunk(text_delta="there was", done=False),
    ])

    class _MemBrunnr:
        backend_kind = "fake"
        embedding_dim = 4

        def add_episode(self, episode):
            captured.append(episode.ember_reply)
            return 1

        def hybrid_search(self, *a, **kw):
            return []

        def text_search(self, *a, **kw):
            return []

        def count(self):  # pragma: no cover
            return BrunnrStats(documents=0, chunks=0, embedded_chunks=0, size_bytes=0)

        def close(self) -> None:
            return None

    stdout = io.StringIO()
    rc = chat.run(
        config=cfg,
        config_root=config_root,
        # One operator turn, then /exit — even though Ctrl-C fired inside
        # the streaming turn, the REPL must come back for the next prompt.
        stdin=io.StringIO("tell me a story\n/exit\n"),
        stdout=stdout,
        funi_opener=lambda _cfg: funi,
        strengr_opener=lambda _s, _b: _MemBrunnr(),
    )
    assert rc == 0

    out = stdout.getvalue()
    assert "Once upon a time there was" in out
    assert "[interrupted by operator]" in out

    # The Episode preserves the partial reply *with* the tag, so the
    # memory layer knows the operator interrupted.
    assert len(captured) == 1
    assert "Once upon a time there was" in captured[0]
    assert "[interrupted by operator]" in captured[0]


def test_streaming_false_takes_complete_path_unchanged(tmp_path: Path) -> None:
    """Opt-out preserves the slice-1 non-streaming behaviour exactly."""
    config_root = _seed_identity(tmp_path / "ember-home")
    cfg = _config(tmp_path, streaming=False)

    funi = _ScriptedStreamingFuni([
        FuniStreamChunk(text_delta="should not be used", done=True,
                        finish_reason=FinishReason.STOP),
    ])

    stdout = io.StringIO()
    rc = chat.run(
        config=cfg,
        config_root=config_root,
        stdin=io.StringIO("hello\n/exit\n"),
        stdout=stdout,
        funi_opener=lambda _cfg: funi,
        strengr_opener=lambda _s, _b: Disconnected(
            reason=DisconnectReason.CONN_REFUSED,
            since=datetime.now(tz=UTC),
        ),
    )
    assert rc == 0
    assert funi.streaming_calls == 0
    assert funi.complete_calls == 1
    assert "(non-streaming reply)" in stdout.getvalue()


def test_streaming_disconnect_banner_prints_before_tokens(tmp_path: Path) -> None:
    """The Vow of Graceful Offline in streaming form."""
    config_root = _seed_identity(tmp_path / "ember-home")
    cfg = _config(tmp_path, streaming=True)

    funi = _ScriptedStreamingFuni([
        FuniStreamChunk(text_delta="I cannot reach the Well.", done=False),
        FuniStreamChunk(text_delta="", done=True, finish_reason=FinishReason.STOP),
    ])

    stdout = io.StringIO()
    rc = chat.run(
        config=cfg,
        config_root=config_root,
        stdin=io.StringIO("hi\n/exit\n"),
        stdout=stdout,
        funi_opener=lambda _cfg: funi,
        strengr_opener=lambda _s, _b: Disconnected(
            reason=DisconnectReason.CONN_REFUSED,
            since=datetime(2026, 5, 21, 12, 0, 0, tzinfo=UTC),
        ),
    )
    assert rc == 0
    out = stdout.getvalue()
    assert "[well: disconnected" in out
    # Banner appears before the streamed body.
    assert out.index("[well: disconnected") < out.index("I cannot reach the Well.")


def test_streaming_finish_reason_length_appends_truncation_tag(
    tmp_path: Path,
) -> None:
    config_root = _seed_identity(tmp_path / "ember-home")
    cfg = _config(tmp_path, streaming=True)

    funi = _ScriptedStreamingFuni([
        FuniStreamChunk(text_delta="A very long reply that...", done=False),
        FuniStreamChunk(text_delta="", done=True, finish_reason=FinishReason.LENGTH),
    ])

    stdout = io.StringIO()
    rc = chat.run(
        config=cfg,
        config_root=config_root,
        stdin=io.StringIO("hi\n/exit\n"),
        stdout=stdout,
        funi_opener=lambda _cfg: funi,
        strengr_opener=lambda _s, _b: Disconnected(
            reason=DisconnectReason.CONN_REFUSED,
            since=datetime.now(tz=UTC),
        ),
    )
    assert rc == 0
    out = stdout.getvalue()
    assert "A very long reply that..." in out
    assert "[reply truncated" in out
