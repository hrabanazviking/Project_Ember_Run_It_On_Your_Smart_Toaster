"""`ember chat` — the conversation REPL.

Per ``docs/architecture/DATA_FLOW.md`` §2 (the canonical turn and its
sad path). One turn:

    operator input → (optional embed) → Brunnr search → assemble prompt
                  → Funi.complete[_streaming] → render → persist Episode

When the Well is disconnected, retrieval is skipped, the system prompt
gets the "do not invent" instruction, and Munnr's render layer prepends
a banner. The Episode is written locally (Phase 6 keeps it in-memory
only; pending-journal flush is a later slice).

Phase 11 (ADR 0009 part 2) wired the streaming consumer:

* When ``config.funi.streaming`` is True (the default), the turn pulls
  :class:`FuniStreamChunk` from ``funi.complete_streaming`` and writes
  each ``text_delta`` to stdout as it arrives, so the operator watches
  tokens unfold instead of waiting for the whole reply.
* ``KeyboardInterrupt`` mid-stream is honored — the partial reply is
  tagged ``[interrupted by operator]`` and persisted to the Episode
  exactly as printed.
* When ``streaming`` is False, the legacy ``funi.complete()`` path is
  taken unchanged.
"""

from __future__ import annotations

import contextlib
import sys
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, TextIO

from ember.schemas.chunks import RetrievalHit
from ember.schemas.config import EmberConfig
from ember.schemas.episode import Episode
from ember.schemas.errors import BrunnrError, Disconnected
from ember.schemas.funi import ContextItem, FinishReason, Unavailable
from ember.schemas.stream import FuniStreamChunk
from ember.spark.funi import handle as funi_handle
from ember.spark.funi import prompt as funi_prompt
from ember.spark.hjarta.identity import has_identity, load_identity
from ember.spark.munnr import render
from ember.thread import strengr
from ember.well.smidja.embed_client import OllamaEmbedClient

if TYPE_CHECKING:
    from ember.spark.funi.handle import FuniHandle
    from ember.well.brunnr.handle import BrunnrHandle


_DEFAULT_K = 5
_DEFAULT_EPISODE_WINDOW = 5
_EXIT_COMMANDS = frozenset({"/exit", "/quit", "/q"})


@dataclass(frozen=True, slots=True)
class _StreamedTurn:
    """What chat.py's streaming hot loop returns to the persistence step."""

    text: str
    finish_reason: FinishReason | None
    model_id: str
    prompt_tokens: int | None
    completion_tokens: int | None
    interrupted: bool


def run(  # noqa: PLR0912,PLR0913,PLR0915 — orchestrator naturally takes config + test seams + one open turn loop
    *,
    config: EmberConfig,
    config_root: Path,
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
    embed_client: OllamaEmbedClient | None = None,
    funi_opener: Callable | None = None,
    strengr_opener: Callable | None = None,
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
                turn = _run_streaming_turn(
                    funi=funi,
                    prompt=text,
                    context=context,
                    hits=hits,
                    disconnect=disconnect,
                    stdout=stdout,
                )
                completed = datetime.now(tz=UTC)
                reply_text_for_episode = turn.text
                if turn.interrupted:
                    reply_text_for_episode = _tag_interrupted(turn.text)
                episode = Episode(
                    operator_input=text,
                    ember_reply=reply_text_for_episode,
                    cited_chunk_ids=tuple(h.chunk_id for h in hits),
                    funi_model=turn.model_id or funi.model_id,
                    well_disconnected=disconnect is not None,
                    started_at=started,
                    completed_at=completed,
                )
            else:
                reply = funi.complete(text, context)
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


def _run_streaming_turn(  # noqa: PLR0913 — one open turn naturally takes the whole turn shape
    *,
    funi: FuniHandle,
    prompt: str,
    context: Sequence[ContextItem],
    hits: Sequence[RetrievalHit],
    disconnect: Disconnected | None,
    stdout: TextIO,
) -> _StreamedTurn:
    """Drive one streaming turn — write deltas live, return aggregate state.

    The disconnect banner (if any) prints before the body, matching the
    non-streaming ``render_reply`` order. Citations print *after* the
    body, only when the Well is reachable. ``KeyboardInterrupt`` is
    caught here so the REPL keeps going on the next prompt rather than
    tearing down the whole session.
    """
    if disconnect is not None:
        stdout.write(render.render_well_disconnected_banner(disconnect) + "\n\n")
        stdout.flush()

    stream: Iterator[FuniStreamChunk] = funi.complete_streaming(prompt, context)
    chunks_text: list[str] = []
    finish_reason: FinishReason | None = None
    model_id = ""
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
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
