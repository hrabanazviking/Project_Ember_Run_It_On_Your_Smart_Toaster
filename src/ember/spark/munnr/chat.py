"""`ember chat` — the conversation REPL.

Per ``docs/architecture/DATA_FLOW.md`` §2 (the canonical turn and its
sad path). One turn:

    operator input → (optional embed) → Brunnr search → assemble prompt
                  → Funi.complete[_streaming] → (optional tool loop) → render
                  → persist Episode

When the Well is disconnected, retrieval is skipped, the system prompt
gets the "do not invent" instruction, and Munnr's render layer prepends
a banner. The Episode is written locally.

* **Phase 11 (ADR 0009 part 2)** wired the streaming consumer — see the
  ``_run_streaming_turn`` helper. Ctrl-C tags partial replies.
* **Phase 16 (ADR 0011 part 3)** wires the tool-use loop. When
  ``config.tools.enabled`` is True and Funi produces ``tool_calls`` in
  the final stream chunk, this module: validates arguments → resolves
  approval → optionally prompts → executes → audits → folds each
  :class:`ToolReply` back into the next turn's context. The loop is
  bounded by ``_MAX_TOOL_TURNS`` per operator input.
"""

from __future__ import annotations

import contextlib
import sys
from collections.abc import Callable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, TextIO

from ember.schemas.chunks import RetrievalHit
from ember.schemas.config import EmberConfig
from ember.schemas.episode import Episode
from ember.schemas.errors import BrunnrError, Disconnected
from ember.schemas.funi import (
    ContextItem,
    ContextKind,
    FinishReason,
    Unavailable,
)
from ember.schemas.stream import FuniStreamChunk
from ember.schemas.tool import (
    ApprovalOutcome,
    ApprovalPolicy,
    ToolCall,
    ToolDescriptor,
    ToolReply,
)
from ember.spark.funi import handle as funi_handle
from ember.spark.funi import prompt as funi_prompt
from ember.spark.funi.tools import (
    AuditLog,
    StdinApprovalPrompter,
    list_tools,
    lookup,
    resolve_approval,
    resolve_with_answer,
    validate_arguments,
)
from ember.spark.hjarta.identity import has_identity, load_identity
from ember.spark.munnr import render
from ember.thread import strengr
from ember.well.smidja.embed_client import OllamaEmbedClient

if TYPE_CHECKING:
    from ember.spark.funi.handle import FuniHandle
    from ember.spark.funi.tools.approval import ApprovalPrompter
    from ember.well.brunnr.handle import BrunnrHandle


_DEFAULT_K = 5
_DEFAULT_EPISODE_WINDOW = 5
_EXIT_COMMANDS = frozenset({"/exit", "/quit", "/q"})
# Bound the propose→execute→follow-up cycle so a model that loops on
# tool calls can't lock up the REPL. Eight is plenty for any real
# multi-step answer; the operator can Ctrl-C anyway.
_MAX_TOOL_TURNS = 8


@dataclass(frozen=True, slots=True)
class _StreamedTurn:
    """What chat.py's streaming hot loop returns to the persistence step."""

    text: str
    finish_reason: FinishReason | None
    model_id: str
    prompt_tokens: int | None
    completion_tokens: int | None
    interrupted: bool
    tool_calls: tuple[ToolCall, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class _ToolRoundOutcome:
    """One round of tool execution after a single Funi reply."""

    replies: tuple[ToolReply, ...]
    context_extension: tuple[ContextItem, ...]
    session_added: tuple[str, ...]   # tool names the operator just promoted to standing


def run(  # noqa: PLR0912,PLR0913,PLR0915 — orchestrator naturally takes config + test seams + tool loop
    *,
    config: EmberConfig,
    config_root: Path,
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
    embed_client: OllamaEmbedClient | None = None,
    funi_opener: Callable | None = None,
    strengr_opener: Callable | None = None,
    approval_prompter: ApprovalPrompter | None = None,
) -> int:
    """Run the chat REPL until EOF or an exit command. Returns exit code."""
    stdin = stdin if stdin is not None else sys.stdin
    stdout = stdout if stdout is not None else sys.stdout
    open_funi = funi_opener or funi_handle.open
    open_well = strengr_opener or strengr.open
    embedder = embed_client or OllamaEmbedClient(config=config.smidja.embedding)

    identity = (
        load_identity(config_root) if has_identity(config_root) else config.identity
    )

    # Open Funi first — without a reasoner, the REPL has nothing to do.
    funi_result = open_funi(config.funi)
    if isinstance(funi_result, Unavailable):
        stdout.write(
            f"Funi is unavailable ({funi_result.reason.value}): "
            f"{funi_result.detail or 'no detail'}\n"
        )
        return 1
    funi: FuniHandle = funi_result

    # Open the Well. Disconnected is honest, not fatal — we continue ungrounded.
    well_result = open_well(config.strengr, config.brunnr)
    brunnr: BrunnrHandle | None
    disconnect: Disconnected | None
    if isinstance(well_result, Disconnected):
        brunnr, disconnect = None, well_result
        stdout.write(render.render_well_disconnected_banner(disconnect) + "\n")
    else:
        brunnr, disconnect = well_result, None

    tool_ctx = _maybe_init_tools(
        config=config,
        config_root=config_root,
        brunnr=brunnr,
        embedder=embedder,
        stdin=stdin,
        stdout=stdout,
        prompter_override=approval_prompter,
    )
    if tool_ctx is not None:
        stdout.write(
            f"{identity.name} is ready (tools enabled: "
            f"{', '.join(d.name for d in tool_ctx.descriptors) or 'none'}). "
            "Type a message; /exit to leave.\n"
        )
    else:
        stdout.write(
            f"{identity.name} is ready. Type a message; /exit to leave.\n"
        )
    stdout.flush()

    episodes: list[Episode] = []
    streaming = config.funi.streaming

    try:
        while True:
            stdout.write("> ")
            stdout.flush()
            line = stdin.readline()
            if not line:
                break  # EOF
            text = line.rstrip("\n").strip()
            if not text:
                continue
            if text.lower() in _EXIT_COMMANDS:
                break

            started = datetime.now(tz=UTC)
            hits = _retrieve(text, brunnr, embedder)
            context = funi_prompt.assemble(
                identity=identity,
                episodes=episodes[-_DEFAULT_EPISODE_WINDOW:],
                hits=hits,
                well_disconnected=disconnect is not None,
            )

            if streaming:
                final_text, model_id_seen = _drive_turn_with_tools(
                    funi=funi,
                    operator_input=text,
                    initial_context=context,
                    hits=hits,
                    disconnect=disconnect,
                    stdout=stdout,
                    tool_ctx=tool_ctx,
                )
                completed = datetime.now(tz=UTC)
                episode = Episode(
                    operator_input=text,
                    ember_reply=final_text,
                    cited_chunk_ids=tuple(h.chunk_id for h in hits),
                    funi_model=model_id_seen or funi.model_id,
                    well_disconnected=disconnect is not None,
                    started_at=started,
                    completed_at=completed,
                )
            else:
                # Non-streaming opt-out path. Tool use here is intentionally
                # one-shot: we honour tool_calls but do not loop, since the
                # legacy path is meant to be the "give me a single blob"
                # mode for piped callers.
                reply = funi.complete(
                    text,
                    context,
                    tools=tuple(tool_ctx.descriptors) if tool_ctx else None,
                )
                completed = datetime.now(tz=UTC)
                rendered = render.render_reply(
                    reply,
                    hits=hits,
                    well_disconnected=disconnect is not None,
                )
                stdout.write(rendered + "\n")
                stdout.flush()
                episode = Episode(
                    operator_input=text,
                    ember_reply=reply.text,
                    cited_chunk_ids=tuple(h.chunk_id for h in hits),
                    funi_model=reply.model_id,
                    well_disconnected=disconnect is not None,
                    started_at=started,
                    completed_at=completed,
                )

            episodes.append(episode)
            if brunnr is not None:
                # Persistence failure is recoverable — we keep serving
                # the operator with the in-memory episode window.
                with contextlib.suppress(BrunnrError):
                    brunnr.add_episode(episode)
    finally:
        funi.close()
        if brunnr is not None:
            brunnr.close()

    return 0


# --------------------------------------------------------------------- #
# Tool plumbing                                                         #
# --------------------------------------------------------------------- #


@dataclass(slots=True)
class _ToolContext:
    """Live state for tool execution within one ``run()`` invocation.

    Mutable because the operator can promote a tool to session-standing
    via the ``always`` prompter answer; ``session_standing`` is the
    accumulating set of those approvals.
    """

    descriptors: tuple[ToolDescriptor, ...]
    config_overrides: Mapping[str, ApprovalPolicy]
    standing_trust_all: bool
    session_standing: set[str]
    audit: AuditLog
    prompter: ApprovalPrompter


def _maybe_init_tools(  # noqa: PLR0913 — wires together the optional Phase-16 surface
    *,
    config: EmberConfig,
    config_root: Path,
    brunnr: BrunnrHandle | None,
    embedder: OllamaEmbedClient | None,
    stdin: TextIO,
    stdout: TextIO,
    prompter_override: ApprovalPrompter | None,
) -> _ToolContext | None:
    """Return a populated tool context, or None when tools are disabled.

    Side-effects: when enabled, imports ``ember.tools`` (which
    self-registers the first-party tools at module-load time) and binds
    the live ``BrunnrHandle`` into ``search_well``.
    """
    if not config.tools.enabled:
        return None

    # Side-effect import: every first-party tool calls register() at
    # import time. Repeated imports are no-ops thanks to Python's
    # module cache; tests use ``registry.clear()`` between cases.
    import ember.tools  # noqa: PLC0415 — side-effect import for tool registration
    from ember.tools import search_well as _search_well  # noqa: PLC0415

    if brunnr is not None:
        _search_well.bind_brunnr(brunnr, embedder=embedder)

    descriptors = tuple(list_tools())
    overrides = _coerce_overrides(config.tools.approval_overrides)

    audit_root = config.tools.audit_root or config_root
    audit = AuditLog(audit_root, ember_version=getattr(ember, "__version__", ""))
    prompter = prompter_override or StdinApprovalPrompter(
        stdin=stdin, stdout=stdout,
    )

    return _ToolContext(
        descriptors=descriptors,
        config_overrides=overrides,
        standing_trust_all=config.tools.standing_trust,
        session_standing=set(),
        audit=audit,
        prompter=prompter,
    )


def _coerce_overrides(
    raw: Mapping[str, str],
) -> dict[str, ApprovalPolicy]:
    """Coerce string-valued config overrides into ``ApprovalPolicy``.

    Unknown values are dropped silently — config validation in Phase 8
    catches typos at load time; this is the runtime-safety belt.
    """
    out: dict[str, ApprovalPolicy] = {}
    for name, value in raw.items():
        try:
            out[name] = ApprovalPolicy(value)
        except ValueError:
            continue
    return out


def _drive_turn_with_tools(  # noqa: PLR0913 — one whole turn naturally fans in this many handles
    *,
    funi: FuniHandle,
    operator_input: str,
    initial_context: Sequence[ContextItem],
    hits: Sequence[RetrievalHit],
    disconnect: Disconnected | None,
    stdout: TextIO,
    tool_ctx: _ToolContext | None,
) -> tuple[str, str]:
    """Drive the streaming turn, then loop on tool_calls until none arrive.

    Returns ``(final_reply_text, model_id_seen)``. ``final_reply_text``
    is what gets persisted as the Episode's ``ember_reply`` — for a
    multi-turn tool-loop this is *the last* Funi reply (which is what
    Funi produced after seeing every tool's output). Tool outputs are
    not concatenated into the reply text — they're audit-log material,
    surfaced live on stdout, and fed back as context for the model's
    eventual summarising reply.
    """
    context: list[ContextItem] = list(initial_context)
    current_input = operator_input
    model_id_seen = ""
    final_text = ""

    for iteration in range(_MAX_TOOL_TURNS):
        tools_arg = tuple(tool_ctx.descriptors) if tool_ctx is not None else None
        turn = _run_streaming_turn(
            funi=funi,
            prompt=current_input,
            context=context,
            hits=hits if iteration == 0 else (),  # citations only after the first turn
            disconnect=disconnect if iteration == 0 else None,
            stdout=stdout,
            tools=tools_arg,
        )
        if turn.model_id:
            model_id_seen = turn.model_id

        # Track the final text — operator-interrupt overrides any
        # subsequent loop iteration.
        if turn.interrupted:
            final_text = _tag_interrupted(turn.text)
            break
        final_text = turn.text

        if not turn.tool_calls or tool_ctx is None:
            break

        round_outcome = _run_tool_round(
            calls=turn.tool_calls,
            tool_ctx=tool_ctx,
            stdout=stdout,
        )
        context.extend(round_outcome.context_extension)
        for promoted in round_outcome.session_added:
            tool_ctx.session_standing.add(promoted)
        # Subsequent turns carry no operator input — Funi's job is to
        # produce a summarising reply now that it has the tool output.
        current_input = ""
    else:
        # Loop bound hit — note it so the operator knows we capped.
        stdout.write("\n[tool-loop max iterations reached]\n")
        stdout.flush()

    return final_text, model_id_seen


def _run_tool_round(
    *,
    calls: Sequence[ToolCall],
    tool_ctx: _ToolContext,
    stdout: TextIO,
) -> _ToolRoundOutcome:
    """Execute every tool call from one Funi reply. Each call:

    1. is rendered as a proposal,
    2. has its arguments validated,
    3. has approval resolved (config + descriptor + session + maybe prompt),
    4. is executed (or refused with a typed error),
    5. is audited,
    6. has its reply rendered on stdout and queued for the next turn.
    """
    replies: list[ToolReply] = []
    context_extension: list[ContextItem] = []
    session_added: list[str] = []

    for call in calls:
        looked_up = lookup(call.name)
        if looked_up is None:
            reply = ToolReply(
                call_id=call.call_id,
                error=f"no such tool: {call.name!r}",
            )
            _emit_proposal(stdout, descriptor=None, call=call)
            _emit_reply(stdout, reply=reply, descriptor=None,
                        outcome=ApprovalOutcome.NO_SUCH_TOOL)
            tool_ctx.audit.record(
                call=call, descriptor=None,
                approval=ApprovalOutcome.NO_SUCH_TOOL, reply=reply,
            )
            replies.append(reply)
            context_extension.append(_tool_reply_to_context(reply, call.name))
            continue

        descriptor, executor = looked_up
        _emit_proposal(stdout, descriptor=descriptor, call=call)

        arg_error = validate_arguments(descriptor, call.arguments)
        if arg_error is not None:
            reply = ToolReply(call_id=call.call_id, error=arg_error)
            _emit_reply(stdout, reply=reply, descriptor=descriptor,
                        outcome=ApprovalOutcome.INVALID_ARGUMENTS)
            tool_ctx.audit.record(
                call=call, descriptor=descriptor,
                approval=ApprovalOutcome.INVALID_ARGUMENTS, reply=reply,
            )
            replies.append(reply)
            context_extension.append(_tool_reply_to_context(reply, descriptor.name))
            continue

        decision = resolve_approval(
            descriptor,
            config_overrides=tool_ctx.config_overrides,
            session_standing=frozenset(tool_ctx.session_standing),
            standing_trust_all=tool_ctx.standing_trust_all,
        )
        if decision.needs_prompt:
            answer = tool_ctx.prompter.prompt(descriptor, call)
            outcome = resolve_with_answer(answer)
            if outcome is ApprovalOutcome.APPROVED_FOR_SESSION:
                session_added.append(descriptor.name)
        else:
            outcome = decision.outcome

        if outcome not in _APPROVE_OUTCOMES:
            reply = ToolReply(
                call_id=call.call_id,
                error=f"refused: {outcome.value}",
            )
            _emit_reply(stdout, reply=reply, descriptor=descriptor, outcome=outcome)
            # Audit reply=None on refusal paths — the tool was not called,
            # so there is no tool-side reply to record. The synthesized
            # error string is still fed back into Funi's next-turn context
            # so the model knows the call was refused.
            tool_ctx.audit.record(
                call=call, descriptor=descriptor,
                approval=outcome, reply=None,
            )
            replies.append(reply)
            context_extension.append(_tool_reply_to_context(reply, descriptor.name))
            continue

        # Execute. The framework boundary turns any exception into a
        # typed-error ToolReply per ADR 0011 §2.8.
        try:
            reply = executor(call)
        except Exception as exc:
            reply = ToolReply(
                call_id=call.call_id,
                error=f"{type(exc).__name__}: {exc}",
            )

        _emit_reply(stdout, reply=reply, descriptor=descriptor, outcome=outcome)
        tool_ctx.audit.record(
            call=call, descriptor=descriptor,
            approval=outcome, reply=reply,
        )
        replies.append(reply)
        context_extension.append(_tool_reply_to_context(reply, descriptor.name))

    return _ToolRoundOutcome(
        replies=tuple(replies),
        context_extension=tuple(context_extension),
        session_added=tuple(session_added),
    )


_APPROVE_OUTCOMES = frozenset({
    ApprovalOutcome.AUTO_APPROVED,
    ApprovalOutcome.APPROVED_THIS_CALL,
    ApprovalOutcome.APPROVED_FOR_SESSION,
})


def _emit_proposal(
    stdout: TextIO,
    *,
    descriptor: ToolDescriptor | None,
    call: ToolCall,
) -> None:
    stdout.write("\n" + render.render_tool_call_proposal(descriptor, call) + "\n")
    stdout.flush()


def _emit_reply(
    stdout: TextIO,
    *,
    reply: ToolReply,
    descriptor: ToolDescriptor | None,
    outcome: ApprovalOutcome | None,
) -> None:
    stdout.write(
        render.render_tool_reply(reply, descriptor, outcome=outcome) + "\n",
    )
    stdout.flush()


def _tool_reply_to_context(reply: ToolReply, tool_name: str) -> ContextItem:
    """Encode a ``ToolReply`` as the next turn's tool-context item.

    The Ollama adapter (Phase 16) emits ``ContextKind.TOOL_REPLY`` as
    ``role="tool"`` messages with the tool name supplied in
    ``metadata["tool_name"]``.
    """
    body = reply.error if (reply.error and not reply.output) else reply.output
    return ContextItem(
        kind=ContextKind.TOOL_REPLY,
        text=body,
        metadata={"tool_name": tool_name, "call_id": reply.call_id},
    )


# --------------------------------------------------------------------- #
# Streaming turn (extended Phase 16 — now surfaces tool_calls)          #
# --------------------------------------------------------------------- #


def _run_streaming_turn(  # noqa: PLR0913 — one open turn naturally takes the whole turn shape
    *,
    funi: FuniHandle,
    prompt: str,
    context: Sequence[ContextItem],
    hits: Sequence[RetrievalHit],
    disconnect: Disconnected | None,
    stdout: TextIO,
    tools: Sequence[ToolDescriptor] | None = None,
) -> _StreamedTurn:
    """Drive one streaming turn — write deltas live, return aggregate state.

    The disconnect banner (if any) prints before the body, matching the
    non-streaming ``render_reply`` order. Citations print *after* the
    body, only when the Well is reachable. ``KeyboardInterrupt`` is
    caught here so the REPL keeps going on the next prompt rather than
    tearing down the whole session. Tool calls from the final chunk are
    returned for the caller's tool loop.
    """
    if disconnect is not None:
        stdout.write(render.render_well_disconnected_banner(disconnect) + "\n\n")
        stdout.flush()

    stream: Iterator[FuniStreamChunk] = funi.complete_streaming(
        prompt, context, tools=tools,
    )
    chunks_text: list[str] = []
    finish_reason: FinishReason | None = None
    model_id = ""
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    tool_calls: tuple[ToolCall, ...] = ()
    interrupted = False
    last_delta_was_empty = True  # so we don't double-newline an empty body

    try:
        for chunk in stream:
            delta = render.render_stream_chunk(chunk)
            if delta:
                stdout.write(delta)
                stdout.flush()
                chunks_text.append(delta)
                last_delta_was_empty = False
            if chunk.done:
                finish_reason = chunk.finish_reason
                if chunk.model_id:
                    model_id = chunk.model_id
                prompt_tokens = chunk.prompt_tokens
                completion_tokens = chunk.completion_tokens
                tool_calls = chunk.tool_calls
    except KeyboardInterrupt:
        interrupted = True
    finally:
        # Generators may hold an HTTP response open; close cleanly.
        close = getattr(stream, "close", None)
        if callable(close):
            with contextlib.suppress(Exception):
                close()

    # End the body line — skip the trailing newline if nothing was streamed,
    # to keep "(no reply text)" / empty-body cases visually tidy.
    if not last_delta_was_empty:
        stdout.write("\n")

    tag = render.stream_finish_tag(finish_reason, interrupted=interrupted)
    if tag:
        stdout.write("\n" + tag + "\n")

    if hits and disconnect is None:
        stdout.write("\n" + render.render_citations(hits) + "\n")

    stdout.flush()

    return _StreamedTurn(
        text="".join(chunks_text),
        finish_reason=finish_reason,
        model_id=model_id,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        interrupted=interrupted,
        tool_calls=tool_calls,
    )


def _tag_interrupted(partial_text: str) -> str:
    """Append the operator-interrupt tag to a partial reply.

    Empty partials still get tagged so the Episode preserves the fact
    that the operator chose to stop the stream.
    """
    body = partial_text.rstrip()
    if not body:
        return render.INTERRUPTED_TAG
    return f"{body} {render.INTERRUPTED_TAG}"


def _retrieve(
    text: str,
    brunnr: BrunnrHandle | None,
    embedder: OllamaEmbedClient,
) -> list[RetrievalHit]:
    if brunnr is None:
        return []
    try:
        vectors = embedder.embed([text])
    except Exception:
        vectors = [None]

    qvec = vectors[0] if vectors else None
    try:
        if qvec is not None and len(qvec) == brunnr.embedding_dim:
            return brunnr.hybrid_search(list(qvec), text, k=_DEFAULT_K)
        return brunnr.text_search(text, k=_DEFAULT_K)
    except BrunnrError:
        return []


__all__ = ["run"]
