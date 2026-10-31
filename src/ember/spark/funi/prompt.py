"""Runtime-neutral prompt assembler.

Per ``docs/architecture/DATA_FLOW.md`` §2.1 step 6: Munnr (or another
Spark caller) assembles the per-turn context, then hands it to Funi as
a list of :class:`ContextItem` plus the raw operator input string.
Funi's runtime-specific adapter translates the items into whatever
shape the runtime accepts (Ollama uses role-tagged messages; llamacpp
will use a chat template; etc.).

This module is *runtime-neutral* — it produces only the typed
:class:`ContextItem` list, never a runtime-specific payload.

Per ``docs/architecture/EMBER_ARCHITECTURE.md`` §6: the system prompt
explicitly tells Funi when grounding is unavailable, so the Vow of
Honest Memory is mechanically enforced at the prompt level.
"""

from __future__ import annotations

from collections.abc import Sequence

from ember.schemas.chunks import RetrievalHit
from ember.schemas.config import IdentityConfig
from ember.schemas.episode import Episode
from ember.schemas.funi import ContextItem, ContextKind
from ember.schemas.persona import Persona

_HONESTY_INSTRUCTION = (
    "Answer honestly and concisely. When you do not know something, "
    "say so plainly rather than inventing an answer."
)

_DISCONNECTED_INSTRUCTION = (
    "Your well of knowledge is currently unreachable. Do not invent "
    "specific facts. If the operator asks something requiring grounded "
    "knowledge, say plainly that your well is disconnected and answer "
    "only what you can say without sources."
)

_GROUNDED_INSTRUCTION = (
    "Use the grounding excerpts below to answer. When you cite a fact, "
    "name the document title it came from. When the excerpts do not "
    "cover the question, say so plainly rather than guessing."
)


def assemble(
    *,
    identity: IdentityConfig,
    episodes: Sequence[Episode] = (),
    hits: Sequence[RetrievalHit] = (),
    well_disconnected: bool = False,
    summary: str | None = None,
    persona: Persona | None = None,
) -> list[ContextItem]:
    """Return the per-turn context items in canonical order.

    Order: system → history summary (E-021, when the window dropped
    older episodes) → episodes (oldest first) → chunk hits (best
    first). The operator's current line is **not** included; the
    caller passes it separately to :meth:`FuniHandle.complete` as
    ``prompt``.

    E-025: when ``persona`` is given it, not ``identity``, names
    who is speaking — the persona's name/role open the system
    text and its instructions ride after the honesty instruction,
    attributed to the persona so prompt text never poses as
    anything else. Persona is also the prompt boundary's memory
    wall: **only episodes tagged with this persona's id are
    assembled**, whatever the caller passed in, so one persona's
    conversation can never ride into another's turn through this
    door. Without a persona there is no wall (the pre-E-025
    single-companion shape, unchanged for its existing callers).
    """
    items: list[ContextItem] = []

    if persona is not None:
        episodes = [ep for ep in episodes if ep.persona_id == persona.id]

    system_text = _system_text(
        identity=persona.identity if persona is not None else identity,
        has_hits=bool(hits),
        well_disconnected=well_disconnected,
        persona=persona,
    )
    items.append(ContextItem(kind=ContextKind.SYSTEM, text=system_text))

    if summary:
        items.append(ContextItem(kind=ContextKind.SUMMARY, text=summary))

    for episode in episodes:
        items.append(
            ContextItem(
                kind=ContextKind.EPISODE,
                text=_episode_text(episode),
                metadata=(
                    {"episode_id": episode.id, "persona_id": episode.persona_id}
                    if episode.id is not None
                    else {"persona_id": episode.persona_id}
                ),
            )
        )

    for hit in hits:
        items.append(
            ContextItem(
                kind=ContextKind.CHUNK,
                text=_hit_text(hit),
                metadata={
                    "chunk_id": hit.chunk_id,
                    "document_id": hit.document_id,
                    "score": hit.score,
                },
            )
        )

    return items


# --------------------------------------------------------------------- #
# Helpers                                                                #
# --------------------------------------------------------------------- #


def _system_text(
    *,
    identity: IdentityConfig,
    has_hits: bool,
    well_disconnected: bool,
    persona: Persona | None = None,
) -> str:
    lines = [f"You are {identity.name}, {identity.role}.", _HONESTY_INSTRUCTION]
    if persona is not None and persona.instructions:
        # Persona instructions are operator-authored persona data,
        # labelled as such in the prompt itself — they extend who
        # the companion is; they do not outrank the honesty
        # instruction above them, and the label keeps that order
        # visible to the model reading it.
        lines.append(f"{persona.name}'s own notes on how to be:\n{persona.instructions}")
    if well_disconnected:
        lines.append(_DISCONNECTED_INSTRUCTION)
    elif has_hits:
        lines.append(_GROUNDED_INSTRUCTION)
    else:
        lines.append(
            "No grounding excerpts are available for this turn. Answer "
            "only what you can say from general knowledge, and name any "
            "limit honestly."
        )
    return "\n\n".join(lines)


def _episode_text(episode: Episode) -> str:
    return (
        "Past turn:\n"
        f"Operator: {episode.operator_input}\n"
        f"Ember: {episode.ember_reply}"
    )


def _hit_text(hit: RetrievalHit) -> str:
    title = hit.document_title or "(untitled)"
    return f"From {title}:\n{hit.text}"


__all__ = ["assemble"]
