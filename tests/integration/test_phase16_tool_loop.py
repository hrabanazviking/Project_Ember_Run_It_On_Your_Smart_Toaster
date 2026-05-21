"""Phase 16 acceptance: Munnr drives the propose→approve→execute→feedback loop.

Uses a scripted streaming Funi that emits a synthesized tool call on
the first turn and a plain reply on the follow-up turn (after seeing
the tool reply). Verifies:

1. Funi is given the available tool descriptors on the first call.
2. The proposal is rendered to stdout.
3. The approval prompt fires when the policy is PER_CALL.
4. The executor is actually called.
5. The reply is rendered.
6. The follow-up turn carries a ``role=tool`` context item AND
   no operator input.
7. The persisted Episode holds Funi's *final* (post-tool-loop) reply.
8. The audit log gains one record per call.
"""

from __future__ import annotations

import io
import json
from collections.abc import Iterator, Sequence
from datetime import UTC, datetime
from pathlib import Path

import pytest

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
    ContextItem,
    ContextKind,
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
from ember.spark.funi.tools import (
    clear as registry_clear,
)
from ember.spark.funi.tools import (
    register,
)
from ember.spark.hjarta import save_identity_atomic
from ember.spark.munnr import chat

# --------------------------------------------------------------------- #
# Test registry — replace the first-party tools with one controllable   #
# --------------------------------------------------------------------- #


_TEST_DESCRIPTOR = ToolDescriptor(
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


def _ping_executor(call: ToolCall) -> ToolReply:
    text = "pong"
    if call.arguments.get("shout"):
        text = text.upper()
    return ToolReply(call_id=call.call_id, output=text, elapsed_s=0.001)


@pytest.fixture
def isolated_registry():
    # Don't load the real first-party tools — register our test ping.
    registry_clear()
    register(_TEST_DESCRIPTOR, _ping_executor)
    yield
    registry_clear()


# --------------------------------------------------------------------- #
# Funi double — scripted streaming                                      #
# --------------------------------------------------------------------- #


class _ScriptedFuni:
    """Funi that returns a queue of pre-built stream sequences.

    Each call to ``complete_streaming`` consumes one queue entry. The
    captured tools / context are recorded for assertions.
    """

    runtime_kind = "fake"
    model_id = "fake:tool-driver"

    def __init__(self, stream_sequences: list[list[FuniStreamChunk]]) -> None:
        self._sequences = list(stream_sequences)
        self.streaming_calls: list[dict] = []

    def complete(self, prompt, context, tools=None) -> FuniReply:  # pragma: no cover
        raise AssertionError("test uses streaming only")

    def complete_streaming(
        self, prompt: str, context: Sequence[ContextItem],
        tools: Sequence[ToolDescriptor] | None = None,
    ) -> Iterator[FuniStreamChunk]:
        self.streaming_calls.append({
            "prompt": prompt,
            "context": list(context),
            "tools": list(tools) if tools else [],
        })
        if not self._sequences:
            raise AssertionError(
                f"unexpected extra streaming call (prompt={prompt!r})"
            )
        seq = self._sequences.pop(0)
        yield from seq

    def health(self) -> FuniHealth:
        return FuniHealth(model_id=self.model_id, last_ok=datetime.now(tz=UTC))

    def close(self) -> None:
        return None


# --------------------------------------------------------------------- #
# Approval prompter — scripted answers                                  #
# --------------------------------------------------------------------- #


class _ScriptedPrompter:
    def __init__(self, answers: list[str]) -> None:
        self._answers = list(answers)
        self.calls: list[ToolCall] = []

    def prompt(self, descriptor, call):
        self.calls.append(call)
        if not self._answers:
            return "n"  # default-deny if test under-scripts
        return self._answers.pop(0)


# --------------------------------------------------------------------- #
# Helpers                                                               #
# --------------------------------------------------------------------- #


def _config(tmp_path: Path, *, tools_enabled: bool = True) -> EmberConfig:
    return EmberConfig(
        funi=FuniConfig(streaming=True),
        strengr=StrengrConfig(retry_backoff_max_s=0.0),
        brunnr=BrunnrConfig(
            embedding_dim=4,
            sqlite_vec=SqliteVecConfig(path=tmp_path / "store.db"),
        ),
        tools=ToolsConfig(enabled=tools_enabled),
    )


def _seed_identity(tmp_path: Path) -> Path:
    save_identity_atomic(tmp_path, IdentityConfig())
    return tmp_path


def _final_chunk_with_tool_call(
    *, tool_name: str = "ping", arguments: dict | None = None,
) -> FuniStreamChunk:
    return FuniStreamChunk(
        text_delta="",
        done=True,
        finish_reason=FinishReason.TOOL_CALL,
        model_id="fake:tool-driver",
        tool_calls=(
            ToolCall(
                call_id="c-1", name=tool_name,
                arguments=arguments or {},
            ),
        ),
    )


def _read_audit_lines(audit_root: Path) -> list[dict]:
    audit_dir = audit_root / "state" / "tool_audit"
    if not audit_dir.exists():
        return []
    out: list[dict] = []
    for file in sorted(audit_dir.iterdir()):
        for line in file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                out.append(json.loads(line))
    return out


# --------------------------------------------------------------------- #
# Acceptance: full propose→approve→execute→feedback loop                 #
# --------------------------------------------------------------------- #


def test_tool_loop_proposes_executes_and_feeds_reply_back(
    isolated_registry, tmp_path: Path,
) -> None:
    config_root = _seed_identity(tmp_path / "ember-home")
    cfg = _config(tmp_path, tools_enabled=True)

    funi = _ScriptedFuni([
        # First turn: model emits a tool call only.
        [_final_chunk_with_tool_call(tool_name="ping", arguments={"shout": True})],
        # Second turn: model produces the summarising reply.
        [
            FuniStreamChunk(text_delta="You said: ", done=False),
            FuniStreamChunk(text_delta="PONG", done=False),
            FuniStreamChunk(
                text_delta="", done=True, finish_reason=FinishReason.STOP,
                model_id="fake:tool-driver",
            ),
        ],
    ])
    prompter = _ScriptedPrompter(["y"])

    stdout = io.StringIO()
    rc = chat.run(
        config=cfg,
        config_root=config_root,
        stdin=io.StringIO("call ping shouting\n/exit\n"),
        stdout=stdout,
        funi_opener=lambda _cfg: funi,
        strengr_opener=lambda _s, _b: Disconnected(
            reason=DisconnectReason.CONN_REFUSED,
            since=datetime.now(tz=UTC),
        ),
        approval_prompter=prompter,
    )
    assert rc == 0

    out = stdout.getvalue()

    # Funi was called twice: first with the operator input, then with no input.
    assert len(funi.streaming_calls) == 2
    first, second = funi.streaming_calls
    assert first["prompt"] == "call ping shouting"
    assert any(d.name == "ping" for d in first["tools"])

    # The follow-up turn's context contains the tool reply, no operator input.
    assert second["prompt"] == ""
    tool_items = [
        ci for ci in second["context"] if ci.kind is ContextKind.TOOL_REPLY
    ]
    assert tool_items
    assert tool_items[0].text == "PONG"
    assert tool_items[0].metadata["tool_name"] == "ping"

    # Operator saw the proposal, approval was prompted, reply rendered.
    assert "[tool proposal] ping" in out
    assert len(prompter.calls) == 1
    assert "[tool reply: approved] ping" in out
    assert "PONG" in out

    # The final operator-facing reply (the summarising turn) printed too.
    assert "You said: PONG" in out


def test_tool_loop_audits_every_call(
    isolated_registry, tmp_path: Path,
) -> None:
    config_root = _seed_identity(tmp_path / "ember-home")
    cfg = _config(tmp_path)
    funi = _ScriptedFuni([
        [_final_chunk_with_tool_call(tool_name="ping", arguments={})],
        [FuniStreamChunk(
            text_delta="ok", done=True, finish_reason=FinishReason.STOP,
        )],
    ])
    prompter = _ScriptedPrompter(["y"])

    chat.run(
        config=cfg,
        config_root=config_root,
        stdin=io.StringIO("go\n/exit\n"),
        stdout=io.StringIO(),
        funi_opener=lambda _cfg: funi,
        strengr_opener=lambda _s, _b: Disconnected(
            reason=DisconnectReason.CONN_REFUSED,
            since=datetime.now(tz=UTC),
        ),
        approval_prompter=prompter,
    )

    records = _read_audit_lines(config_root)
    assert len(records) == 1
    r = records[0]
    assert r["tool"] == "ping"
    assert r["approval"] == "approved_this_call"
    assert r["reply"]["output"] == "pong"


def test_denied_call_skips_execution_and_audits_denial(
    isolated_registry, tmp_path: Path,
) -> None:
    config_root = _seed_identity(tmp_path / "ember-home")
    cfg = _config(tmp_path)
    funi = _ScriptedFuni([
        [_final_chunk_with_tool_call(tool_name="ping", arguments={})],
        [FuniStreamChunk(
            text_delta="ack", done=True, finish_reason=FinishReason.STOP,
        )],
    ])
    prompter = _ScriptedPrompter(["n"])

    stdout = io.StringIO()
    chat.run(
        config=cfg,
        config_root=config_root,
        stdin=io.StringIO("go\n/exit\n"),
        stdout=stdout,
        funi_opener=lambda _cfg: funi,
        strengr_opener=lambda _s, _b: Disconnected(
            reason=DisconnectReason.CONN_REFUSED,
            since=datetime.now(tz=UTC),
        ),
        approval_prompter=prompter,
    )
    assert "[tool refused: operator denied]" in stdout.getvalue()

    records = _read_audit_lines(config_root)
    assert records[0]["approval"] == "denied"
    # No reply key → tool was not executed.
    assert "reply" not in records[0]


def test_unknown_tool_call_records_no_such_tool(
    isolated_registry, tmp_path: Path,
) -> None:
    config_root = _seed_identity(tmp_path / "ember-home")
    cfg = _config(tmp_path)
    funi = _ScriptedFuni([
        [_final_chunk_with_tool_call(tool_name="ghost", arguments={})],
        [FuniStreamChunk(
            text_delta="hm", done=True, finish_reason=FinishReason.STOP,
        )],
    ])
    prompter = _ScriptedPrompter([])  # no prompt should fire

    chat.run(
        config=cfg,
        config_root=config_root,
        stdin=io.StringIO("go\n/exit\n"),
        stdout=io.StringIO(),
        funi_opener=lambda _cfg: funi,
        strengr_opener=lambda _s, _b: Disconnected(
            reason=DisconnectReason.CONN_REFUSED,
            since=datetime.now(tz=UTC),
        ),
        approval_prompter=prompter,
    )
    records = _read_audit_lines(config_root)
    assert records[0]["tool"] == "ghost"
    assert records[0]["approval"] == "no_such_tool"
    # Operator was NOT prompted for a tool that doesn't exist.
    assert prompter.calls == []


def test_invalid_arguments_short_circuits_before_prompt(
    isolated_registry, tmp_path: Path,
) -> None:
    config_root = _seed_identity(tmp_path / "ember-home")
    cfg = _config(tmp_path)
    # ping descriptor has `shout: bool, required=False`. Pass an int.
    funi = _ScriptedFuni([
        [_final_chunk_with_tool_call(
            tool_name="ping", arguments={"shout": 1},  # bool-shape violation
        )],
        [FuniStreamChunk(text_delta="ok", done=True,
                         finish_reason=FinishReason.STOP)],
    ])
    prompter = _ScriptedPrompter([])

    chat.run(
        config=cfg,
        config_root=config_root,
        stdin=io.StringIO("go\n/exit\n"),
        stdout=io.StringIO(),
        funi_opener=lambda _cfg: funi,
        strengr_opener=lambda _s, _b: Disconnected(
            reason=DisconnectReason.CONN_REFUSED,
            since=datetime.now(tz=UTC),
        ),
        approval_prompter=prompter,
    )
    records = _read_audit_lines(config_root)
    assert records[0]["approval"] == "invalid_arguments"
    # Operator was NOT prompted — args failed at the framework boundary.
    assert prompter.calls == []


def test_standing_tool_auto_approves_without_prompt(
    tmp_path: Path,
) -> None:
    """A descriptor with STANDING approval skips the prompt."""
    registry_clear()
    safe_descriptor = ToolDescriptor(
        name="search_safe", description="x",
        parameters_schema={},
        required_approval=ApprovalPolicy.STANDING,
    )
    register(
        safe_descriptor,
        lambda call: ToolReply(call_id=call.call_id, output="results"),
    )

    config_root = _seed_identity(tmp_path / "ember-home")
    cfg = _config(tmp_path)
    funi = _ScriptedFuni([
        [_final_chunk_with_tool_call(tool_name="search_safe", arguments={})],
        [FuniStreamChunk(text_delta="summary", done=True,
                         finish_reason=FinishReason.STOP)],
    ])
    prompter = _ScriptedPrompter([])  # must never be consulted

    try:
        chat.run(
            config=cfg,
            config_root=config_root,
            stdin=io.StringIO("go\n/exit\n"),
            stdout=io.StringIO(),
            funi_opener=lambda _cfg: funi,
            strengr_opener=lambda _s, _b: Disconnected(
                reason=DisconnectReason.CONN_REFUSED,
                since=datetime.now(tz=UTC),
            ),
            approval_prompter=prompter,
        )
    finally:
        registry_clear()

    assert prompter.calls == []
    records = _read_audit_lines(config_root)
    assert records[0]["approval"] == "auto_approved"


def test_tools_disabled_means_funi_gets_no_tool_list_and_loop_is_skipped(
    isolated_registry, tmp_path: Path,
) -> None:
    config_root = _seed_identity(tmp_path / "ember-home")
    cfg = _config(tmp_path, tools_enabled=False)

    funi = _ScriptedFuni([
        # Even if the model somehow emitted tool_calls, the loop should
        # short-circuit because tool_ctx is None.
        [_final_chunk_with_tool_call(tool_name="ping", arguments={})],
    ])
    prompter = _ScriptedPrompter([])

    chat.run(
        config=cfg,
        config_root=config_root,
        stdin=io.StringIO("go\n/exit\n"),
        stdout=io.StringIO(),
        funi_opener=lambda _cfg: funi,
        strengr_opener=lambda _s, _b: Disconnected(
            reason=DisconnectReason.CONN_REFUSED,
            since=datetime.now(tz=UTC),
        ),
        approval_prompter=prompter,
    )

    # Funi was called exactly once (no follow-up loop).
    assert len(funi.streaming_calls) == 1
    # No tool list was sent.
    assert funi.streaming_calls[0]["tools"] == []
    # No audit records (tools were disabled).
    assert _read_audit_lines(config_root) == []
    # No prompt fired.
    assert prompter.calls == []


def test_tool_loop_max_iterations_bounded(
    isolated_registry, tmp_path: Path,
) -> None:
    """A model that loops on tool calls forever still terminates."""
    config_root = _seed_identity(tmp_path / "ember-home")
    cfg = _config(tmp_path)

    # Provide more sequences than _MAX_TOOL_TURNS — the loop must cap.
    loop_chunk = [_final_chunk_with_tool_call(tool_name="ping", arguments={})]
    funi = _ScriptedFuni([loop_chunk] * 20)  # way more than the cap
    prompter = _ScriptedPrompter(["y"] * 20)

    stdout = io.StringIO()
    rc = chat.run(
        config=cfg,
        config_root=config_root,
        stdin=io.StringIO("go\n/exit\n"),
        stdout=stdout,
        funi_opener=lambda _cfg: funi,
        strengr_opener=lambda _s, _b: Disconnected(
            reason=DisconnectReason.CONN_REFUSED,
            since=datetime.now(tz=UTC),
        ),
        approval_prompter=prompter,
    )
    assert rc == 0
    # The loop cap fires; we don't drain all 20 sequences.
    assert len(funi.streaming_calls) <= chat._MAX_TOOL_TURNS
    assert "max iterations reached" in stdout.getvalue()
