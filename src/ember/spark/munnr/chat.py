"""`ember chat` — the conversation REPL.

Per ``docs/architecture/DATA_FLOW.md`` §2 (the canonical turn and its
sad path). One turn:

    operator input → (optional embed) → Brunnr search → assemble prompt
                  → Funi.complete → render → persist Episode

When the Well is disconnected, retrieval is skipped, the system prompt
gets the "do not invent" instruction, and Munnr's render layer prepends
a banner. The Episode is written locally (Phase 6 keeps it in-memory
only; pending-journal flush is a later slice).
"""

from __future__ import annotations

import contextlib
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, TextIO

from ember.schemas.chunks import RetrievalHit
from ember.schemas.config import EmberConfig
from ember.schemas.episode import Episode
from ember.schemas.errors import BrunnrError, Disconnected
from ember.schemas.funi import Unavailable
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


def run(  # noqa: PLR0913,PLR0915 — orchestrator naturally takes config + test seams + has one open turn loop
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
