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
* **E-021** loads persisted history from the Well at startup and
  windows it per turn under the profile-aware token budget
  (``ember.spark.funi.windowing``), with dropped turns summarised
  through the summarisation hook rather than silently forgotten.
* **E-025** resolves the session's persona (``ember.spark.persona``),
  starts from that persona's own remembered turns only, assembles
  each turn under that persona, and tags every new Episode with
  its id — one persona's conversation never rides in another's.
* **Phase 16 (ADR 0011 part 3)** wires the tool-use loop. When
  ``config.tools.enabled`` is True and Funi produces ``tool_calls`` in
  the final stream chunk, this module: validates arguments → resolves
  approval → optionally prompts → executes → audits → folds each
  :class:`ToolReply` back into the next turn's context. The loop is
  bounded by ``_MAX_TOOL_TURNS`` per operator input.
* **E-028** completes the interruption shape: the companion can be
  talked over at *every* waiting point — at the prompt, during
  retrieval, mid-stream, at a tool-approval prompt, during tool
  execution, and inside a non-streaming ``complete()`` — and the
  session stays coherent (see
  ``docs/architecture/E-028_STREAMING_INTERRUPTION.md``). E-028 also
  closes docket 83: the non-streaming path now executes returned
  ``tool_calls`` through the same bounded loop instead of dropping
  them.
* **E-054** consults graceful smallness once per turn
  (``ember.smallness``): as this process's memory approaches
  the conversation profile's turn budget, the companion sheds
  features by the stated ladder — history summaries, then
  semantic retrieval (this turn's search runs text-only and
  the embed call is skipped), then the wide history window —
  announcing each shed (and each restore) in plain words on
  screen and in the diary. Answering, saving, and tool safety
  are never shed.
* **E-030** completes the error-honesty shape: a failure the
  operator cannot see is a lie of omission, so the three silent
  degradations are now spoken — a history load that fails says so
  at startup, a Well search that fails mid-session says so for
  that turn *and* marks the turn ungrounded in the prompt and the
  Episode (docket 86), and an Episode that cannot be saved says
  so at that moment (docket 85). Replies that ended in an error
  or were cut off for length are persisted *with* their tag, so
  a failed or partial reply never poses as a completed answer
  in the remembered history (see
  ``docs/architecture/E-030_ERROR_HONESTY.md``).
* **E-031** completes session persistence (docket 82): turns a
  disconnected session makes, and turns whose Well save fails,
  are written atomically to the pending-episodes journal under
  ``<config_root>/state/pending_episodes/`` instead of being lost
  at exit; the next connected session drains the journal into
  the Well (in order, before history loads) and says so, with
  damaged journal files quarantined and reported, never fatal
  (see ``docs/architecture/E-031_SESSION_PERSISTENCE.md``).
* **E-034** keeps the diary beside the technical trace: the
  session's plain-words facts (started, Well reached or not,
  turns answered and how they were saved, ended) are written
  to ``<config_root>/diary/`` via :mod:`ember.diary` — never
  the operator's words, never the reply's words. A diary
  failure warns once, in plain words, and never stops a chat
  (see ``docs/architecture/E-034_DIARY_LOG.md``).
* **E-035** runs the session in one named conversation
  (``ember.spark.conversation``): history loads only that
  conversation's turns, each turn is assembled under it and
  tagged with it, so one talk never bleeds into another. The
  choice is the ``conversation_id`` argument / ``--conversation``
  flag, then ``conversation.active`` in the config file, then
  the ``default`` conversation (see
  ``docs/architecture/E-035_MULTI_CONVERSATION_ISOLATION.md``).
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
from ember.schemas.errors import Disconnected
from ember.schemas.funi import (
    ContextItem,
    ContextKind,
    FinishReason,
    FuniReply,
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
from ember.spark.funi.windowing import window_history
from ember.spark.funi.tools import (
    AuditLog,
    StdinApprovalPrompter,
    list_tools,
    lookup,
    resolve_approval,
    resolve_with_answer,
    validate_arguments,
)
from ember import nerve
from ember.diary import Diary, diary_root
from ember.smallness import SmallnessGuard
from ember.schemas.conversation import DEFAULT_CONVERSATION_ID
from ember.spark.conversation import (
    episodes_for_conversation,
    resolve_conversation_id,
)
from ember.spark.conversation.core import ConversationError
from ember.spark.hjarta.identity import has_identity, load_identity
from ember.spark.munnr import render
from ember.spark.persona import episodes_for_persona, resolve_persona
from ember.spark.persona.core import PersonaError
from ember.thread import strengr
from ember.well.pending_journal import PendingJournal, pending_root
from ember.well.smidja.embed_client import OllamaEmbedClient

if TYPE_CHECKING:
    from ember.spark.funi.handle import FuniHandle
    from ember.spark.funi.tools.approval import ApprovalPrompter
    from ember.well.brunnr.handle import BrunnrHandle


_DEFAULT_K = 5
# How much stored history to load at startup. The window (profile
# token budget + episode cap, E-021) trims what actually rides in the
# prompt; loading a generous multiple of the largest profile cap
# keeps the summarisation hook fed without unbounded memory growth.
_HISTORY_LOAD_LIMIT = 64
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
    smallness_guard: SmallnessGuard | None = None,
    approval_prompter: ApprovalPrompter | None = None,
    conversation_id: str | None = None,
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

    # Diary (E-034): the plain-words record beside the technical
    # trace. Only facts are recorded — never what the operator
    # wrote, never what Ember replied. A failed diary write warns
    # ONCE on stdout, in plain words, and never stops the session.
    diary = Diary(diary_root(config_root), enabled=config.logging.diary)
    diary_warned = False

    def diary_note(sentence: str) -> None:
        nonlocal diary_warned
        if not diary.enabled or diary.record(sentence):
            return
        if not diary_warned:
            diary_warned = True
            stdout.write(
                "[note: Ember's diary could not be written, so this "
                "session's plain-words record may be missing entries. "
                "The chat itself is unaffected.]\n"
            )
            stdout.flush()

    # Graceful smallness (E-054): the shed ladder, consulted
    # once per turn against this process's own memory and the
    # conversation profile's turn budget from the book. A shed
    # (or a restore) is announced in plain words — on the
    # person's screen and in the diary — at the moment it
    # happens, never silently. The plan shapes the turn below:
    # semantic retrieval goes text-only, and the history window
    # is built under the plan's (possibly narrowed) config.
    # ``smallness_guard`` is a test seam: an injected guard
    # judges by its own assessor (a test process's resident
    # memory is the harness's, not a companion's, so a suite
    # that means to pin windowing must not inherit whatever
    # pressure the harness happens to be under).
    def announce_smallness(sentence: str) -> None:
        stdout.write(f"[room: {sentence}]\n")
        stdout.flush()
        diary_note(sentence)

    smallness = smallness_guard or SmallnessGuard(
        config.conversation.profile, announce=announce_smallness
    )

    # Persona (E-025): who the companion is this session. An
    # explicitly configured persona that cannot load stops the
    # session with the reason named — never a silent swap to a
    # different companion. With no persona configured and no
    # persona files, this is the identity above, projected onto
    # the default persona unchanged.
    try:
        persona = resolve_persona(config_root, config.personas.active or None)
    except PersonaError as exc:
        diary_note(
            "A chat session could not start because the chosen "
            "companion profile could not be loaded."
        )
        stdout.write(f"Persona could not be loaded: {exc}\n")
        return 1
    identity = persona.identity

    # Conversation (E-035): which talk this session is in. An
    # invalid chosen id stops the session with the reason named —
    # never a silent fall-back to a different conversation, which
    # would mix the talks the operator asked to keep apart.
    try:
        session_conversation = resolve_conversation_id(
            conversation_id, config.conversation.active
        )
    except ConversationError as exc:
        diary_note(
            "A chat session could not start because the chosen "
            "conversation name was not usable."
        )
        stdout.write(f"Conversation could not be opened: {exc}\n")
        return 1
    if session_conversation != DEFAULT_CONVERSATION_ID:
        diary_note(
            f"This session is in the '{session_conversation}' "
            "conversation, kept apart from Ember's other talks."
        )

    # Open Funi first — without a reasoner, the REPL has nothing to do.
    funi_result = open_funi(config.funi)
    if isinstance(funi_result, Unavailable):
        diary_note(
            "A chat session could not start because the model "
            "program was not available."
        )
        stdout.write(
            f"Funi is unavailable ({funi_result.reason.value}): "
            f"{funi_result.detail or 'no detail'}\n"
        )
        return 1
    funi: FuniHandle = funi_result
    _model = getattr(funi, "model_id", "") or "an unknown model"
    diary_note(f"A chat session started with {identity.name} (model {_model}).")

    # Open the Well. Disconnected is honest, not fatal — we continue ungrounded.
    well_result = open_well(config.strengr, config.brunnr)
    brunnr: BrunnrHandle | None
    disconnect: Disconnected | None
    if isinstance(well_result, Disconnected):
        brunnr, disconnect = None, well_result
        diary_note(
            "The memory store could not be reached, so this session "
            "began without memory grounding."
        )
        stdout.write(render.render_well_disconnected_banner(disconnect) + "\n")
    else:
        brunnr, disconnect = well_result, None
        diary_note("The memory store was connected.")

    # Cross-member nerves (E-067): the session announces itself
    # to the Verdandi hub — facts only (persona, conversation,
    # memory connected or not, model), never content. The
    # bridge never raises and a missing hub degrades to the
    # feed file inside the bridge; the chat is never affected.
    nerve.publish_session(
        "start",
        persona_id=persona.id,
        conversation_id=session_conversation,
        well_connected=brunnr is not None,
        model=_model,
        turns=0,
    )
    nerve_turns = 0

    # Session persistence (E-031, docket 82): the pending-episodes
    # journal for this config root. A connected session drains it
    # into the Well *before* history loads, so turns saved locally
    # by an earlier disconnected (or save-failed) session join the
    # remembered history in order. Drain outcomes are spoken:
    # flushed turns are announced, a refused drain keeps its files
    # and says why, and damaged files are quarantined + reported.
    pending = PendingJournal(pending_root(config_root))
    if brunnr is not None and pending.count():
        drain = pending.drain(brunnr)
        if drain.flushed:
            stdout.write(
                f"[well: added {drain.flushed} saved turn(s) from the "
                "local pending journal to the Well.]\\n"
            )
        if drain.corrupt:
            stdout.write(
                f"[warning: {len(drain.corrupt)} saved turn file(s) in "
                "the pending journal were damaged and have been moved "
                "aside (not deleted) under "
                f"{pending.root / 'corrupt'}; they could not be added "
                "to the Well.]\\n"
            )
        if drain.failure is not None:
            stdout.write(
                "[warning: saved turns could not be added to the Well "
                f"({drain.failure}); {drain.kept} turn(s) are still "
                "saved locally and will be tried again next session.]\\n"
            )
        if drain.flushed:
            diary_note(
                f"{drain.flushed} saved turn(s) from an earlier session "
                "were added to the memory store."
            )
        if drain.corrupt:
            diary_note(
                f"{len(drain.corrupt)} saved turn file(s) were damaged "
                "and were moved aside, not deleted."
            )
        if drain.failure is not None:
            diary_note(
                "Some saved turns could not be added to the memory "
                "store and are still saved locally for next time."
            )
        stdout.flush()

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

    # History (E-021): episodes persisted in the Well are loaded back
    # so the conversation survives a restart (docket 81). A failing
    # reader degrades to an in-session-only history, never a crash —
    # and since E-030 it degrades *loudly*: before E-030 the failure
    # was suppressed in silence and the operator was left believing
    # the companion remembered when it could not load its memory.
    episodes: list[Episode] = []
    if brunnr is not None:
        try:
            # Per-persona separation (E-025): this persona's
            # session starts from its own remembered turns only.
            # Per-conversation separation (E-035): of those, only
            # this conversation's turns — the other talks this
            # persona remembers stay in their own conversations.
            # Filtering happens BEFORE windowing, so a foreign
            # talk's turns can neither ride verbatim nor leak in
            # through the window's summary of dropped episodes.
            episodes = episodes_for_conversation(
                episodes_for_persona(
                    brunnr.recent_episodes(_HISTORY_LOAD_LIMIT), persona.id
                ),
                session_conversation,
            )
            diary_note(
                f"{len(episodes)} earlier exchange(s) were loaded "
                "from memory."
                if episodes
                else "No earlier exchanges were loaded from memory."
            )
        except Exception as exc:
            diary_note(
                "Saved conversations could not be loaded, so this "
                "session started without them (they were not deleted)."
            )
            stdout.write(
                "[warning: your saved conversations could not be loaded "
                f"({type(exc).__name__}: {exc}); this session starts "
                "without them — they have not been deleted.]\n"
            )
            stdout.flush()
            episodes = []
    streaming = config.funi.streaming

    try:
        while True:
            stdout.write("> ")
            stdout.flush()
            try:
                line = stdin.readline()
            except KeyboardInterrupt:
                # E-028: Ctrl-C at the prompt talks over an empty
                # line, not over the session — re-prompt. Leaving is
                # /exit or EOF, never an accidental interrupt.
                stdout.write("\n")
                stdout.flush()
                continue
            if not line:
                break  # EOF
            text = line.rstrip("\n").strip()
            if not text:
                continue
            if text.lower() in _EXIT_COMMANDS:
                break

            started = datetime.now(tz=UTC)
            # E-054: judge this turn's room before any of the
            # turn's priced work runs — the plan decides whether
            # retrieval embeds (semantic) or reads plain words,
            # and under what history window the prompt is built.
            smallness_plan = smallness.consult().plan
            try:
                hits, retrieval_failure = _retrieve(
                    text,
                    brunnr,
                    embedder,
                    text_only=not smallness_plan.semantic_retrieval,
                )
            except KeyboardInterrupt:
                # E-028: talked over during retrieval — before any
                # reply existed. The turn is abandoned (nothing is
                # persisted; there is no partial reply to tag) and
                # the session continues at the next prompt.
                diary_note(
                    "A turn was stopped while looking things up, "
                    "before any reply was written."
                )
                stdout.write("\n" + render.INTERRUPTED_TAG + "\n")
                stdout.flush()
                continue
            # E-030 (docket 86): a search that failed mid-session is
            # not an honestly empty Well. The operator is told for
            # this turn, and the turn is ungrounded in fact: the
            # prompt carries the do-not-invent instruction and the
            # Episode is flagged well_disconnected, exactly as an
            # open-time disconnect turn is.
            turn_ungrounded = disconnect is not None or retrieval_failure is not None
            if retrieval_failure is not None:
                stdout.write(
                    "[well: search failed for this message "
                    f"({retrieval_failure}); the reply will not be "
                    "grounded in your documents]\n"
                )
                stdout.flush()
            windowed = window_history(
                episodes, smallness_plan.conversation_config(config.conversation)
            )
            context = funi_prompt.assemble(
                identity=identity,
                episodes=windowed.episodes,
                hits=hits,
                well_disconnected=turn_ungrounded,
                summary=windowed.summary,
                persona=persona,
                conversation_id=session_conversation,
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
                    well_disconnected=turn_ungrounded,
                    started_at=started,
                    completed_at=completed,
                    persona_id=persona.id,
                    conversation_id=session_conversation,
                )
            else:
                # Non-streaming opt-out path ("give me a single blob"
                # mode for piped callers). E-028 (docket 83): returned
                # tool_calls are executed through the same bounded
                # loop as the streaming path — before E-028 they were
                # silently dropped while the old comment claimed they
                # were honoured. Interruption inside complete() or a
                # tool round yields the tagged partial, never a crash.
                reply, was_interrupted = _drive_complete_turn_with_tools(
                    funi=funi,
                    operator_input=text,
                    initial_context=context,
                    disconnect=disconnect,
                    stdout=stdout,
                    tool_ctx=tool_ctx,
                )
                completed = datetime.now(tz=UTC)
                if was_interrupted:
                    final_text = _tag_interrupted(reply.text if reply else "")
                    stdout.write(final_text + "\n")
                    stdout.flush()
                    episode_text = final_text
                    episode_model = reply.model_id if reply else funi.model_id
                else:
                    assert reply is not None  # noqa: S101 — driver invariant
                    rendered = render.render_reply(
                        reply,
                        hits=hits,
                        well_disconnected=disconnect is not None,
                    )
                    stdout.write(rendered + "\n")
                    stdout.flush()
                    # E-030: the rendered reply already carries its
                    # error / truncation tag on screen; the persisted
                    # Episode carries it too, so the failed or partial
                    # reply never poses as a completed answer when a
                    # later session reads the history back.
                    episode_text = _tag_failed_finish(reply.text, reply.finish_reason)
                    episode_model = reply.model_id
                episode = Episode(
                    operator_input=text,
                    ember_reply=episode_text,
                    cited_chunk_ids=tuple(h.chunk_id for h in hits),
                    funi_model=episode_model,
                    well_disconnected=turn_ungrounded,
                    started_at=started,
                    completed_at=completed,
                    persona_id=persona.id,
                    conversation_id=session_conversation,
                )

            episodes.append(episode)
            nerve_turns += 1
            # Diary (E-034): the turn's outcome in plain words,
            # read off the same tags the operator saw and the
            # Episode carries — never the turn's content.
            if render.INTERRUPTED_TAG in episode.ember_reply:
                diary_note("A turn was stopped before its reply finished.")
            elif render.ERROR_TAG in episode.ember_reply:
                diary_note("A turn ended with an error instead of a finished answer.")
            elif render.TRUNCATED_TAG in episode.ember_reply:
                diary_note("A turn's reply was cut off because it ran too long.")
            elif turn_ungrounded:
                diary_note("A turn was answered without memory grounding.")
            else:
                diary_note("A turn was answered.")
            persisted_shape = "memory_only"
            if brunnr is not None:
                # Persistence failure is recoverable — we keep serving
                # the operator with the in-memory episode window.
                # Broaden beyond BrunnrError to also catch lower-
                # level backend exceptions (sqlite3.Error, psycopg.Error)
                # that the adapter might let through on a stale
                # connection; the cost of losing one Episode is less
                # than crashing the REPL. E-030 (docket 85): the
                # failure is caught, never hidden — before E-030 it
                # was suppressed in silence and a session could
                # believe it was remembering when the store was not.
                # E-031 (docket 82): a failed save now falls back to
                # the pending journal, so the turn survives exit and
                # drains into the Well on a later connected session;
                # only when the journal *also* fails is the turn
                # remembered only until this session ends.
                try:
                    brunnr.add_episode(episode)
                    persisted_shape = "well"
                    diary_note("The turn was saved to the memory store.")
                except Exception as exc:
                    try:
                        pending.append(episode)
                        persisted_shape = "journal"
                    except Exception as journal_exc:
                        diary_note(
                            "The turn could not be saved anywhere, so "
                            "it will only be remembered until this "
                            "session ends."
                        )
                        stdout.write(
                            "[warning: this turn could not be saved to the "
                            f"Well ({type(exc).__name__}: {exc}) or to the "
                            "local pending journal "
                            f"({type(journal_exc).__name__}: {journal_exc}); "
                            "it will be remembered only until this "
                            "session ends.]\n"
                        )
                    else:
                        diary_note(
                            "The turn could not be saved to the memory "
                            "store, so it was saved locally for a later "
                            "session."
                        )
                        stdout.write(
                            "[warning: this turn could not be saved to the "
                            f"Well ({type(exc).__name__}: {exc}); it has "
                            "been saved locally and will be added to the "
                            "Well when it can be reached again.]\n"
                        )
                    stdout.flush()
            else:
                # Disconnected session (E-031, docket 82): the turn
                # goes to the pending journal — DATA_FLOW §2.2 step
                # 9', promised since the Episode schema was written.
                # The disconnect banner already told the operator the
                # Well is unreachable; a journal failure is the new
                # fact, and it is spoken like any save failure.
                try:
                    pending.append(episode)
                    persisted_shape = "journal"
                    diary_note(
                        "The turn was saved locally, to be added to "
                        "the memory store when it can be reached again."
                    )
                except Exception as journal_exc:
                    diary_note(
                        "The turn could not be saved anywhere, so it "
                        "will only be remembered until this session ends."
                    )
                    stdout.write(
                        "[warning: this turn could not be saved locally "
                        f"({type(journal_exc).__name__}: {journal_exc}); "
                        "it will be remembered only until this session "
                        "ends.]\n"
                    )
                    stdout.flush()
            # Cross-member nerves (E-067): the completed turn
            # crosses to the Verdandi hub as memory FACTS — hits
            # that grounded it, chunks cited, where the Episode
            # was persisted, its outcome — never its content.
            # The outcome words are read off the same tags the
            # diary reads above. The bridge never raises.
            if render.INTERRUPTED_TAG in episode.ember_reply:
                nerve_outcome = "interrupted"
            elif render.ERROR_TAG in episode.ember_reply:
                nerve_outcome = "error"
            elif render.TRUNCATED_TAG in episode.ember_reply:
                nerve_outcome = "truncated"
            elif turn_ungrounded:
                nerve_outcome = "ungrounded"
            else:
                nerve_outcome = "answered"
            nerve.publish_turn(
                conversation_id=session_conversation,
                persona_id=persona.id,
                hits=len(hits),
                cited=len(episode.cited_chunk_ids),
                persisted=persisted_shape,
                ungrounded=turn_ungrounded,
                outcome=nerve_outcome,
                model=episode.funi_model,
            )
    finally:
        # Cross-member nerves (E-067): the session's end crosses
        # too, from the finally block so every exit path reports
        # it, with the count of completed turns.
        nerve.publish_session(
            "end",
            persona_id=persona.id,
            conversation_id=session_conversation,
            well_connected=brunnr is not None,
            model=_model,
            turns=nerve_turns,
        )
        # Close each handle independently so a raise from one doesn't
        # leak the other. Neither adapter's close() is documented to
        # raise, but we defend in depth.
        with contextlib.suppress(Exception):
            funi.close()
        if brunnr is not None:
            with contextlib.suppress(Exception):
                brunnr.close()

    diary_note("The chat session ended.")
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

    # Wire operator-config `allow_private_addresses` default into the
    # fetch_url tool (Batch J — previously declared on ToolsConfig but
    # never read; the per-call arg always overrides).
    from ember.tools import fetch_url as _fetch_url  # noqa: PLC0415
    _fetch_url.bind_allow_private_default(config.tools.allow_private_addresses)

    descriptors = tuple(list_tools())
    overrides = _coerce_overrides(config.tools.approval_overrides)
    _warn_unknown_override_tools(overrides, descriptors, stdout=stdout)

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


def _warn_unknown_override_tools(
    overrides: Mapping[str, ApprovalPolicy],
    descriptors: Sequence[ToolDescriptor],
    *,
    stdout: TextIO,
) -> None:
    """Warn the operator if ``tools.approval_overrides`` names a tool
    that isn't actually registered.

    Without this, a config like ``approval_overrides: {fech_url: per_call}``
    (note the typo) would silently apply nothing — the operator would
    believe they had tightened approval on ``fetch_url`` while the
    actual descriptor's policy is in force. Surfacing the typo at
    startup is the only point where the operator is looking for it.
    """
    if not overrides:
        return
    known = {d.name for d in descriptors}
    unknown = sorted(name for name in overrides if name not in known)
    if not unknown:
        return
    stdout.write(
        f"warning: tools.approval_overrides names {len(unknown)} unknown "
        f"tool(s) (typo? plugin not loaded?): {unknown!r}; the override "
        f"will NOT take effect.\n"
    )


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
        # E-030: an error or length finish is tagged in the text
        # that gets persisted, not only on screen, so the stored
        # Episode never reads back as a completed answer. A later
        # tool-loop iteration overwrites this with its own text.
        final_text = _tag_failed_finish(turn.text, turn.finish_reason)

        if not turn.tool_calls or tool_ctx is None:
            break

        try:
            round_outcome = _run_tool_round(
                calls=turn.tool_calls,
                tool_ctx=tool_ctx,
                stdout=stdout,
            )
        except KeyboardInterrupt:
            # E-028: talked over while approving or executing a tool
            # call. Calls already executed in this round stand (they
            # were emitted + audited as they completed); no further
            # call runs, no follow-up generation happens, and the
            # streamed text is persisted with the interrupt tag —
            # the same shape as a mid-stream interrupt.
            stdout.write("\n" + render.INTERRUPTED_TAG + "\n")
            stdout.flush()
            final_text = _tag_interrupted(turn.text)
            break
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


def _drive_complete_turn_with_tools(  # noqa: PLR0913 — mirrors the streaming driver's shape
    *,
    funi: FuniHandle,
    operator_input: str,
    initial_context: Sequence[ContextItem],
    disconnect: Disconnected | None,
    stdout: TextIO,
    tool_ctx: _ToolContext | None,
) -> tuple[FuniReply | None, bool]:
    """Drive one non-streaming turn, looping on tool_calls (E-028).

    Returns ``(reply, interrupted)``. ``reply`` is the last Funi
    reply produced (None only when the *first* ``complete()`` was
    interrupted before returning anything). ``interrupted`` is True
    when the operator talked over the turn — inside ``complete()``,
    at a tool-approval prompt, or during tool execution — in which
    case the caller persists ``reply.text`` with the interrupt tag
    and no further generation or tool call happens.

    Before E-028 (docket 83) this path passed descriptors to
    ``complete()`` and silently dropped any returned ``tool_calls``.
    Now a reply carrying calls runs the same propose → approve →
    execute → feedback round as streaming, bounded by
    ``_MAX_TOOL_TURNS``. A non-final reply that carries both text
    and tool calls is rendered before its round runs, mirroring
    what the streaming operator already saw live.
    """
    context: list[ContextItem] = list(initial_context)
    current_input = operator_input
    last_reply: FuniReply | None = None

    for iteration in range(_MAX_TOOL_TURNS):
        tools_arg = tuple(tool_ctx.descriptors) if tool_ctx is not None else None
        try:
            reply = funi.complete(current_input, context, tools=tools_arg)
        except KeyboardInterrupt:
            return last_reply, True
        last_reply = reply

        if not reply.tool_calls or tool_ctx is None:
            return reply, False

        if reply.text:
            rendered = render.render_reply(
                reply,
                hits=(),
                well_disconnected=disconnect is not None and iteration == 0,
            )
            stdout.write(rendered + "\n")
            stdout.flush()

        try:
            round_outcome = _run_tool_round(
                calls=reply.tool_calls,
                tool_ctx=tool_ctx,
                stdout=stdout,
            )
        except KeyboardInterrupt:
            return reply, True
        context.extend(round_outcome.context_extension)
        for promoted in round_outcome.session_added:
            tool_ctx.session_standing.add(promoted)
        current_input = ""
    else:
        stdout.write("\n[tool-loop max iterations reached]\n")
        stdout.flush()

    return last_reply, False


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
            _safe_audit(
                tool_ctx.audit, stdout,
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
            _safe_audit(
                tool_ctx.audit, stdout,
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
            # E-026: the call's own arguments feed the guarded-
            # argument gate (a model-supplied escape hatch such as
            # fetch_url's allow_private_addresses always prompts).
            arguments=call.arguments,
        )
        if decision.needs_prompt:
            answer = _safe_prompt(tool_ctx.prompter, stdout, descriptor, call)
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
            _safe_audit(
                tool_ctx.audit, stdout,
                call=call, descriptor=descriptor,
                approval=outcome, reply=None,
            )
            replies.append(reply)
            context_extension.append(_tool_reply_to_context(reply, descriptor.name))
            continue

        # Execute. The framework boundary turns any exception into a
        # typed-error ToolReply per ADR 0011 §2.8. The descriptor's
        # ``timeout_s`` is enforced via a ThreadPoolExecutor (Batch J —
        # previously declared on the descriptor but not honoured at
        # call time; tools could hang the REPL indefinitely).
        reply = _execute_with_timeout(executor, call, descriptor.timeout_s)

        _emit_reply(stdout, reply=reply, descriptor=descriptor, outcome=outcome)
        _safe_audit(
            tool_ctx.audit, stdout,
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


def _execute_with_timeout(
    executor, call: ToolCall, timeout_s: float,
) -> ToolReply:
    """Run a tool executor under a per-descriptor timeout.

    Cross-platform: uses ``concurrent.futures.ThreadPoolExecutor`` so
    the timeout works on POSIX + macOS + Windows (``signal.alarm`` is
    POSIX-only). Python threads can't actually be killed, so a runaway
    tool keeps consuming CPU until it returns — but the REPL is
    unblocked and the operator gets a typed timeout reply.

    Any exception inside the executor is caught and turned into a
    typed :class:`ToolReply` per ADR-0011 §2.8 — the framework boundary
    never raises across into the chat loop.
    """
    from concurrent.futures import ThreadPoolExecutor  # noqa: PLC0415
    from concurrent.futures import TimeoutError as _FutTimeout  # noqa: PLC0415

    # NB: deliberately NOT using `with ThreadPoolExecutor(...) as pool`
    # here — the context manager's __exit__ calls shutdown(wait=True),
    # which would block the REPL until the runaway worker finishes,
    # defeating the timeout. We shutdown manually with wait=False so
    # the REPL is unblocked the moment the timeout fires. The worker
    # thread keeps running until the executor returns (Python threads
    # can't be killed cooperatively); that's documented in the
    # operator-facing error string.
    pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="ember-tool")
    try:
        future = pool.submit(executor, call)
        try:
            return future.result(timeout=timeout_s)
        except _FutTimeout:
            future.cancel()
            return ToolReply(
                call_id=call.call_id,
                error=(
                    f"tool exceeded its declared timeout of {timeout_s}s; "
                    f"the work may still be running in the background"
                ),
            )
        except Exception as exc:
            return ToolReply(
                call_id=call.call_id,
                error=f"{type(exc).__name__}: {exc}",
            )
    finally:
        pool.shutdown(wait=False, cancel_futures=True)


def _safe_audit(
    audit: AuditLog,
    stdout: TextIO,
    **record_kwargs: object,
) -> None:
    """Record an audit entry; degrade-loud if the audit log can't be written.

    Audit failures (disk full, permission flip, etc.) historically raised
    ``ToolError`` per ADR 0011 §2.7's "audit miss is bad" stance, which
    would crash the chat loop mid-tool. We keep audit miss visible by
    writing a one-line warning to stdout, but never let it terminate
    the REPL.
    """
    try:
        audit.record(**record_kwargs)  # type: ignore[arg-type]
    except Exception as exc:
        stdout.write(
            f"[warning: audit log write failed: {type(exc).__name__}: {exc}]\n"
        )
        stdout.flush()


def _safe_prompt(
    prompter: ApprovalPrompter,
    stdout: TextIO,
    descriptor: ToolDescriptor,
    call: ToolCall,
) -> str:
    """Ask the prompter for an approval answer; degrade to "n" on any IO error.

    A closed-stdin / disconnected-terminal IOError mid-prompt should
    refuse the call rather than crash the loop. The Vow of Sovereignty
    says ambiguity defaults to refusal.

    ``KeyboardInterrupt`` is deliberately NOT caught here (E-028):
    Ctrl-C at an approval prompt is the operator talking over the
    whole turn, not answering "n" to one call — it propagates to the
    turn driver, which ends the turn with the interrupt tag.
    """
    try:
        return prompter.prompt(descriptor, call)
    except (OSError, EOFError, ValueError) as exc:
        stdout.write(
            f"[warning: approval prompter failed ({type(exc).__name__}); "
            f"treating as 'n']\n"
        )
        stdout.flush()
        return "n"


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

    chunks_text: list[str] = []
    finish_reason: FinishReason | None = None
    model_id = ""
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    tool_calls: tuple[ToolCall, ...] = ()
    interrupted = False
    last_delta_was_empty = True  # so we don't double-newline an empty body
    stream: Iterator[FuniStreamChunk] | None = None

    try:
        # E-028: creating the stream is inside the interrupt guard
        # too — an adapter may do real work (or block) before it
        # returns its iterator, and Ctrl-C there is still just the
        # operator talking over this turn.
        stream = funi.complete_streaming(prompt, context, tools=tools)
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


def _tag_failed_finish(text: str, finish_reason: FinishReason | None) -> str:
    """Carry a failed or partial finish into the persisted Episode text.

    E-030: the screen already tags an ERROR finish with
    ``[ember reported an error]`` and a LENGTH finish with the
    truncation tag (``render.stream_finish_tag`` / ``render_reply``),
    but before E-030 the Episode stored the bare text — so a later
    session reading its history back met the error text, or the
    cut-off answer, as if Ember had completed the turn. The stored
    text now carries the same tag the operator saw. Other finishes
    (STOP, REFUSED — a refusal is a completed act whose text says
    what it is — TOOL_CALL, None) are stored unchanged.
    """
    if finish_reason is FinishReason.ERROR:
        body = text.strip()
        if not body:
            return render.ERROR_TAG
        return f"{render.ERROR_TAG} {body}"
    if finish_reason is FinishReason.LENGTH:
        body = text.rstrip()
        if not body:
            return render.TRUNCATED_TAG
        return f"{body} {render.TRUNCATED_TAG}"
    return text


def _retrieve(
    text: str,
    brunnr: BrunnrHandle | None,
    embedder: OllamaEmbedClient,
    *,
    text_only: bool = False,
) -> tuple[list[RetrievalHit], str | None]:
    """Search the Well for one turn; return ``(hits, failure)``.

    E-030 (docket 86): ``failure`` is a plain ``Type: message``
    description when the search itself failed, and the caller turns
    the turn ungrounded *and says so* — before E-030 a
    :class:`BrunnrError` here yielded no hits and no signal, so a
    broken search was indistinguishable from an honestly empty
    Well. The catch is broadened beyond ``BrunnrError`` for the
    same reason persistence catches broadly: an adapter can let a
    lower-level backend exception (sqlite3 / psycopg) through on a
    stale connection, and that failure must be spoken too.

    An embedding failure alone is *not* a retrieval failure: the
    no-vector degrade falls back to text search, whose hits are
    real search results. ``KeyboardInterrupt`` is never caught
    here (it is not an ``Exception``) — E-028's talk-over shape.
    """
    if brunnr is None:
        return [], None
    # E-054: graceful smallness may shed semantic retrieval —
    # the turn then skips the embed call entirely (saving the
    # work, not just its use) and searches on plain words,
    # the same honest text shape the no-vector degrade uses.
    if text_only:
        try:
            return brunnr.text_search(text, k=_DEFAULT_K), None
        except Exception as exc:
            return [], f"{type(exc).__name__}: {exc}"
    try:
        vectors = embedder.embed([text])
    except Exception:
        vectors = [None]

    qvec = vectors[0] if vectors else None
    try:
        if qvec is not None and len(qvec) == brunnr.embedding_dim:
            return brunnr.hybrid_search(list(qvec), text, k=_DEFAULT_K), None
        return brunnr.text_search(text, k=_DEFAULT_K), None
    except Exception as exc:
        return [], f"{type(exc).__name__}: {exc}"


__all__ = ["run"]
