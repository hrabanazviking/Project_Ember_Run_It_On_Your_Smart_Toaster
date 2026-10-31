"""E-028 — Streaming + interruption: talked over, state stays coherent.

Before E-028, Phase 11's interrupt handling covered exactly one
waiting point: KeyboardInterrupt raised while iterating a stream.
Every other place the companion waits could be crashed by Ctrl-C,
losing the session and the turn:

* at the REPL prompt (``readline``),
* during retrieval,
* at a tool-approval prompt or during tool execution (streaming
  and non-streaming alike),
* inside a non-streaming ``complete()``.

And docket 83: the non-streaming path passed tool descriptors to
``complete()`` but silently dropped returned ``tool_calls`` (the
``wrap_complete_as_stream`` helper dropped them too).

These tests pin the E-028 shape, point by point:

1. Ctrl-C at the prompt re-prompts; the session lives.
2. Ctrl-C during retrieval abandons the turn (nothing persisted),
   the session lives, and the next turn works.
3. Ctrl-C at a tool-approval prompt (streaming): no tool executes,
   the streamed partial is persisted with the interrupt tag, the
   session lives.
4. Ctrl-C during tool execution (streaming): calls already done
   stand, later calls never run, partial persisted tagged.
5. Non-streaming ``tool_calls`` are executed and looped (docket 83).
6. Ctrl-C inside non-streaming ``complete()``: tag-only episode,
   session lives.
7. ``wrap_complete_as_stream`` carries the reply's tool calls.

No sqlite-vec, no Ollama. Pure double-driven flow, in the
Phase 11/16 test shape.
"""

from __future__ import annotations

import io
from datetime import UTC, datetime
from pathlib import Path

import pytest

from ember.schemas.chunks import BrunnrStats
from ember.schemas.config import (
    BrunnrConfig,
    EmberConfig,
    FuniConfig,
    IdentityConfig,
    SqliteVecConfig,
    StrengrConfig,
    ToolsConfig,
)
from ember.schemas.errors import Disconnected, DisconnectReason
from ember.schemas.funi import (
    FinishReason,
    FuniHealth,
    FuniReply,
)
from ember.schemas.stream import FuniStreamChunk
from ember.schemas.tool import (
    ApprovalPolicy,
    ToolCall,
    ToolDescriptor,
    ToolParameter,
    ToolParameterKind,
    ToolReply,
)
from ember.spark.funi import handle as funi_handle
from ember.spark.funi.tools import clear as registry_clear
from ember.spark.funi.tools import register
from ember.spark.hjarta import save_identity_atomic
from ember.spark.munnr import chat
from ember.spark.munnr import render

TAG = render.INTERRUPTED_TAG

# --------------------------------------------------------------------- #
# Shared helpers                                                          #
# --------------------------------------------------------------------- #


def _config(tmp_path: Path, *, streaming: bool, tools: bool = False) -> EmberConfig:
    return EmberConfig(
        funi=FuniConfig(streaming=streaming),
        strengr=StrengrConfig(retry_backoff_max_s=0.0),
        brunnr=BrunnrConfig(
            embedding_dim=4,
            sqlite_vec=SqliteVecConfig(path=tmp_path / "store.db"),
        ),
        tools=ToolsConfig(enabled=tools),
    )


def _seed_identity(tmp_path: Path) -> Path:
    save_identity_atomic(tmp_path, IdentityConfig())
    return tmp_path


def _disconnected() -> Disconnected:
    return Disconnected(
        reason=DisconnectReason.CONN_REFUSED,
        since=datetime.now(tz=UTC),
    )


class _CapturingBrunnr:
    backend_kind = "fake"
    embedding_dim = 4

    def __init__(self) -> None:
        self.episodes: list = []

    def recent_episodes(self, limit):
        return []

    def add_episode(self, episode):
        self.episodes.append(episode)
        return 1

    def hybrid_search(self, *a, **kw):
        return []

    def text_search(self, *a, **kw):
        return []

    def count(self):  # pragma: no cover
        return BrunnrStats(documents=0, chunks=0, embedded_chunks=0, size_bytes=0)

    def close(self) -> None:
        return None


class _InterruptingStdin:
    """First readline raises KeyboardInterrupt; later lines are scripted."""

    def __init__(self, lines: list[str]) -> None:
        self._lines = list(lines)
        self._raised = False

    def readline(self) -> str:
        if not self._raised:
            self._raised = True
            raise KeyboardInterrupt
        if self._lines:
            return self._lines.pop(0)
        return ""


# --------------------------------------------------------------------- #
# 1. Ctrl-C at the prompt                                                 #
# --------------------------------------------------------------------- #


class _SimpleStreamingFuni:
    runtime_kind = "fake"
    model_id = "fake:e028"

    def __init__(self) -> None:
        self.streaming_calls = 0

    def complete(self, prompt, context, tools=None):  # pragma: no cover
        raise AssertionError("streaming config must not call complete")

    def complete_streaming(self, prompt, context, tools=None):
        self.streaming_calls += 1
        yield FuniStreamChunk(text_delta="still here", done=False)
        yield FuniStreamChunk(
            text_delta="", done=True,
            finish_reason=FinishReason.STOP, model_id=self.model_id,
        )

    def health(self):
        return FuniHealth(model_id=self.model_id, last_ok=datetime.now(tz=UTC))

    def close(self):
        return None


def test_ctrl_c_at_prompt_reprompts_and_session_lives(tmp_path: Path) -> None:
    config_root = _seed_identity(tmp_path / "ember-home")
    funi = _SimpleStreamingFuni()
    stdout = io.StringIO()
    rc = chat.run(
        config=_config(tmp_path, streaming=True),
        config_root=config_root,
        stdin=_InterruptingStdin(["hello\n", "/exit\n"]),
        stdout=stdout,
        funi_opener=lambda _cfg: funi,
        strengr_opener=lambda _s, _b: _disconnected(),
    )
    assert rc == 0
    # The turn after the interrupt ran normally.
    assert funi.streaming_calls == 1
    assert "still here" in stdout.getvalue()


# --------------------------------------------------------------------- #
# 2. Ctrl-C during retrieval                                              #
# --------------------------------------------------------------------- #


class _NullEmbedder:
    """No vector for any text — retrieval falls back to text search."""

    def embed(self, texts):
        return [None for _ in texts]


class _InterruptingEmbedder:
    def embed(self, texts):
        raise KeyboardInterrupt


def test_ctrl_c_during_retrieval_abandons_turn_session_lives(
    tmp_path: Path,
) -> None:
    config_root = _seed_identity(tmp_path / "ember-home")
    funi = _SimpleStreamingFuni()
    brunnr = _CapturingBrunnr()
    stdout = io.StringIO()
    rc = chat.run(
        config=_config(tmp_path, streaming=True),
        config_root=config_root,
        stdin=io.StringIO("first\n/exit\n"),
        stdout=stdout,
        embed_client=_InterruptingEmbedder(),
        funi_opener=lambda _cfg: funi,
        strengr_opener=lambda _s, _b: brunnr,
    )
    assert rc == 0
    # No generation happened and nothing was persisted for the
    # abandoned turn — there was never a reply to tag.
    assert funi.streaming_calls == 0
    assert brunnr.episodes == []
    assert TAG in stdout.getvalue()


# --------------------------------------------------------------------- #
# Tool fixtures (Phase 16 shape)                                          #
# --------------------------------------------------------------------- #


_DESCRIPTOR = ToolDescriptor(
    name="ping",
    description="reply with 'pong'",
    parameters_schema={
        "shout": ToolParameter(
            kind=ToolParameterKind.BOOLEAN,
            description="upper-case the reply",
            required=False,
            default=False,
        ),
    },
    required_approval=ApprovalPolicy.PER_CALL,
)

_EXECUTED: list[str] = []


def _ping_executor(call: ToolCall) -> ToolReply:
    _EXECUTED.append(call.call_id)
    return ToolReply(call_id=call.call_id, output="pong", elapsed_s=0.001)


@pytest.fixture
def isolated_registry():
    _EXECUTED.clear()
    registry_clear()
    register(_DESCRIPTOR, _ping_executor)
    yield
    registry_clear()


def _call(call_id: str) -> ToolCall:
    return ToolCall(call_id=call_id, name="ping", arguments={})


def _tool_chunk(call_id: str, *, text: str = "") -> FuniStreamChunk:
    return FuniStreamChunk(
        text_delta=text,
        done=True,
        finish_reason=FinishReason.TOOL_CALL,
        model_id="fake:e028-tools",
        tool_calls=(_call(call_id),),
    )


class _ToolThenTextFuni:
    """First streaming call proposes the scripted calls; later calls answer."""

    runtime_kind = "fake"
    model_id = "fake:e028-tools"

    def __init__(self, first_chunks: list[FuniStreamChunk]) -> None:
        self._first = list(first_chunks)
        self.streaming_calls = 0

    def complete(self, prompt, context, tools=None):  # pragma: no cover
        raise AssertionError("streaming config must not call complete")

    def complete_streaming(self, prompt, context, tools=None):
        self.streaming_calls += 1
        if self.streaming_calls == 1:
            yield from self._first
        else:
            yield FuniStreamChunk(text_delta="after tools", done=False)
            yield FuniStreamChunk(
                text_delta="", done=True,
                finish_reason=FinishReason.STOP, model_id=self.model_id,
            )

    def health(self):
        return FuniHealth(model_id=self.model_id, last_ok=datetime.now(tz=UTC))

    def close(self):
        return None


class _InterruptingPrompter:
    def __init__(self) -> None:
        self.calls = 0

    def prompt(self, descriptor, call):
        self.calls += 1
        raise KeyboardInterrupt


# --------------------------------------------------------------------- #
# 3. Ctrl-C at the approval prompt (streaming)                            #
# --------------------------------------------------------------------- #


def test_ctrl_c_at_approval_prompt_no_execution_partial_tagged(
    tmp_path: Path, isolated_registry,
) -> None:
    config_root = _seed_identity(tmp_path / "ember-home")
    funi = _ToolThenTextFuni([
        FuniStreamChunk(text_delta="let me check ", done=False),
        _tool_chunk("c1"),
    ])
    brunnr = _CapturingBrunnr()
    prompter = _InterruptingPrompter()
    stdout = io.StringIO()
    rc = chat.run(
        config=_config(tmp_path, streaming=True, tools=True),
        config_root=config_root,
        stdin=io.StringIO("go\n/exit\n"),
        stdout=stdout,
        embed_client=_NullEmbedder(),
        funi_opener=lambda _cfg: funi,
        strengr_opener=lambda _s, _b: brunnr,
        approval_prompter=prompter,
    )
    assert rc == 0
    assert prompter.calls == 1
    # The interrupted approval executed nothing and generated no
    # follow-up turn.
    assert _EXECUTED == []
    assert funi.streaming_calls == 1
    # The streamed partial was persisted with the tag.
    assert len(brunnr.episodes) == 1
    assert brunnr.episodes[0].ember_reply == f"let me check {TAG}"
    assert TAG in stdout.getvalue()


# --------------------------------------------------------------------- #
# 4. Ctrl-C during tool execution: earlier calls stand, later never run   #
# --------------------------------------------------------------------- #


def _interrupting_executor(call: ToolCall) -> ToolReply:
    _EXECUTED.append(call.call_id)
    raise KeyboardInterrupt


@pytest.fixture
def interrupting_registry():
    _EXECUTED.clear()
    registry_clear()
    register(_DESCRIPTOR, _interrupting_executor)
    yield
    registry_clear()


class _ApprovePrompter:
    def prompt(self, descriptor, call):
        return "y"


def test_ctrl_c_during_execution_stops_round_partial_tagged(
    tmp_path: Path, interrupting_registry,
) -> None:
    config_root = _seed_identity(tmp_path / "ember-home")
    two_calls = FuniStreamChunk(
        text_delta="working ",
        done=True,
        finish_reason=FinishReason.TOOL_CALL,
        model_id="fake:e028-tools",
        tool_calls=(_call("c1"), _call("c2")),
    )
    funi = _ToolThenTextFuni([two_calls])
    brunnr = _CapturingBrunnr()
    stdout = io.StringIO()
    rc = chat.run(
        config=_config(tmp_path, streaming=True, tools=True),
        config_root=config_root,
        stdin=io.StringIO("go\n/exit\n"),
        stdout=stdout,
        embed_client=_NullEmbedder(),
        funi_opener=lambda _cfg: funi,
        strengr_opener=lambda _s, _b: brunnr,
        approval_prompter=_ApprovePrompter(),
    )
    assert rc == 0
    # The first call was attempted (and interrupted); the second
    # call in the same round never ran.
    assert _EXECUTED == ["c1"]
    assert funi.streaming_calls == 1
    assert len(brunnr.episodes) == 1
    assert brunnr.episodes[0].ember_reply == f"working {TAG}"


# --------------------------------------------------------------------- #
# 5 + 6. The non-streaming path                                           #
# --------------------------------------------------------------------- #


class _CompleteFuni:
    """Non-streaming double: queue of replies (or exceptions)."""

    runtime_kind = "fake"
    model_id = "fake:e028-complete"

    def __init__(self, script: list) -> None:
        self._script = list(script)
        self.complete_calls: list[dict] = []

    def complete(self, prompt, context, tools=None) -> FuniReply:
        self.complete_calls.append(
            {"prompt": prompt, "context": list(context), "tools": tools}
        )
        item = self._script.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item

    def complete_streaming(self, prompt, context, tools=None):  # pragma: no cover
        raise AssertionError("non-streaming config must not stream")

    def health(self):
        return FuniHealth(model_id=self.model_id, last_ok=datetime.now(tz=UTC))

    def close(self):
        return None


def test_nonstreaming_tool_calls_execute_and_loop_docket83(
    tmp_path: Path, isolated_registry,
) -> None:
    config_root = _seed_identity(tmp_path / "ember-home")
    funi = _CompleteFuni([
        FuniReply(
            text="",
            finish_reason=FinishReason.TOOL_CALL,
            model_id="fake:e028-complete",
            tool_calls=(_call("c1"),),
        ),
        FuniReply(
            text="the answer is pong",
            finish_reason=FinishReason.STOP,
            model_id="fake:e028-complete",
        ),
    ])
    brunnr = _CapturingBrunnr()
    stdout = io.StringIO()
    rc = chat.run(
        config=_config(tmp_path, streaming=False, tools=True),
        config_root=config_root,
        stdin=io.StringIO("go\n/exit\n"),
        stdout=stdout,
        embed_client=_NullEmbedder(),
        funi_opener=lambda _cfg: funi,
        strengr_opener=lambda _s, _b: brunnr,
        approval_prompter=_ApprovePrompter(),
    )
    assert rc == 0
    # The call executed, and the follow-up complete() saw the tool
    # reply as context with no operator input — the streaming loop's
    # shape, on the non-streaming road.
    assert _EXECUTED == ["c1"]
    assert len(funi.complete_calls) == 2
    follow_up = funi.complete_calls[1]
    assert follow_up["prompt"] == ""
    assert any("pong" in item.text for item in follow_up["context"])
    # The persisted episode is the final reply, not the tool proposal.
    assert len(brunnr.episodes) == 1
    assert brunnr.episodes[0].ember_reply == "the answer is pong"
    assert "the answer is pong" in stdout.getvalue()


def test_nonstreaming_ctrl_c_inside_complete_tags_and_lives(
    tmp_path: Path,
) -> None:
    config_root = _seed_identity(tmp_path / "ember-home")
    funi = _CompleteFuni([
        KeyboardInterrupt(),
        FuniReply(
            text="second turn answer",
            finish_reason=FinishReason.STOP,
            model_id="fake:e028-complete",
        ),
    ])
    brunnr = _CapturingBrunnr()
    stdout = io.StringIO()
    rc = chat.run(
        config=_config(tmp_path, streaming=False),
        config_root=config_root,
        stdin=io.StringIO("one\ntwo\n/exit\n"),
        stdout=stdout,
        embed_client=_NullEmbedder(),
        funi_opener=lambda _cfg: funi,
        strengr_opener=lambda _s, _b: brunnr,
    )
    assert rc == 0
    assert len(brunnr.episodes) == 2
    assert brunnr.episodes[0].ember_reply == TAG
    assert brunnr.episodes[1].ember_reply == "second turn answer"


def test_nonstreaming_no_tools_reply_unchanged(tmp_path: Path) -> None:
    config_root = _seed_identity(tmp_path / "ember-home")
    funi = _CompleteFuni([
        FuniReply(
            text="plain blob",
            finish_reason=FinishReason.STOP,
            model_id="fake:e028-complete",
        ),
    ])
    stdout = io.StringIO()
    rc = chat.run(
        config=_config(tmp_path, streaming=False),
        config_root=config_root,
        stdin=io.StringIO("hi\n/exit\n"),
        stdout=stdout,
        funi_opener=lambda _cfg: funi,
        strengr_opener=lambda _s, _b: _disconnected(),
    )
    assert rc == 0
    assert len(funi.complete_calls) == 1
    assert "plain blob" in stdout.getvalue()


# --------------------------------------------------------------------- #
# 7. wrap_complete_as_stream carries tool calls                           #
# --------------------------------------------------------------------- #


def test_wrap_complete_as_stream_carries_tool_calls() -> None:
    class _Handle:
        runtime_kind = "fake"
        model_id = "fake:wrap"

        def complete(self, prompt, context, tools=None):
            return FuniReply(
                text="",
                finish_reason=FinishReason.TOOL_CALL,
                model_id=self.model_id,
                tool_calls=(_call("c9"),),
            )

    chunks = list(
        funi_handle.wrap_complete_as_stream(_Handle(), "hi", [], tools=None)
    )
    assert len(chunks) == 1
    assert chunks[0].done is True
    assert [c.call_id for c in chunks[0].tool_calls] == ["c9"]


def test_stream_creation_interrupt_is_an_interrupted_turn(
    tmp_path: Path,
) -> None:
    """An adapter that raises Ctrl-C before returning its iterator."""

    class _RaisingFuni:
        runtime_kind = "fake"
        model_id = "fake:e028-raise"

        def complete(self, prompt, context, tools=None):  # pragma: no cover
            raise AssertionError("streaming only")

        def complete_streaming(self, prompt, context, tools=None):
            raise KeyboardInterrupt

        def health(self):
            return FuniHealth(
                model_id=self.model_id, last_ok=datetime.now(tz=UTC)
            )

        def close(self):
            return None

    config_root = _seed_identity(tmp_path / "ember-home")
    brunnr = _CapturingBrunnr()
    stdout = io.StringIO()
    rc = chat.run(
        config=_config(tmp_path, streaming=True),
        config_root=config_root,
        stdin=io.StringIO("hi\n/exit\n"),
        stdout=stdout,
        embed_client=_NullEmbedder(),
        funi_opener=lambda _cfg: _RaisingFuni(),
        strengr_opener=lambda _s, _b: brunnr,
    )
    assert rc == 0
    assert len(brunnr.episodes) == 1
    assert brunnr.episodes[0].ember_reply == TAG
    assert TAG in stdout.getvalue()
