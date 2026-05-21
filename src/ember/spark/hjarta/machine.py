"""Hjarta — the first-run state machine.

Per ``docs/architecture/EMBER_ARCHITECTURE.md`` §3.1 and
``docs/architecture/DATA_FLOW.md`` §4. A finite, named FSM — not a
generative wizard. Each state has a fixed transition function and a
prompt loaded from :file:`prompts/wizard.toml` (per RULES.AI.md "no
hardcoded data").

States:

    Greet → ChooseFuni → DiscoverFuni → ChooseWell → ConfigureWell
          → TestRetrieval → NameEmber → WriteIdentity → Done

Atomic guarantee: nothing is written to ``~/.ember/`` until the
``WriteIdentity`` step at the very end. Any earlier failure leaves
the filesystem unchanged so the operator can re-run cleanly.
"""

from __future__ import annotations

import logging
import tomllib
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from importlib import resources
from pathlib import Path
from typing import TYPE_CHECKING

from ember.schemas.chunks import Chunk, Document
from ember.schemas.config import (
    BrunnrConfig,
    EmberConfig,
    FuniConfig,
    IdentityConfig,
    StrengrConfig,
)
from ember.schemas.errors import Disconnected
from ember.schemas.funi import Unavailable
from ember.spark.funi import handle as funi_handle
from ember.spark.hjarta.identity import save_identity_atomic
from ember.thread import strengr

if TYPE_CHECKING:
    from ember.spark.funi.handle import FuniHandle
    from ember.well.brunnr.handle import BrunnrHandle


logger = logging.getLogger(__name__)


_PROBE_HASH = "ember-hjarta-probe-v1"
_PROBE_TEXT = (
    "This is an Ember Hjarta first time setup probe. "
    "It can be safely deleted."
)


# --------------------------------------------------------------------- #
# States + outcome                                                      #
# --------------------------------------------------------------------- #


class HjartaState(StrEnum):
    GREET = "greet"
    CHOOSE_FUNI = "choose_funi"
    DISCOVER_FUNI = "discover_funi"
    CHOOSE_WELL = "choose_well"
    CONFIGURE_WELL = "configure_well"
    TEST_RETRIEVAL = "test_retrieval"
    NAME_EMBER = "name_ember"
    WRITE_IDENTITY = "write_identity"
    DONE = "done"


@dataclass(frozen=True, slots=True)
class HjartaOutcome:
    success: bool
    final_state: HjartaState
    identity_path: Path | None = None
    detail: str | None = None


# --------------------------------------------------------------------- #
# IO abstraction                                                        #
# --------------------------------------------------------------------- #


@dataclass(slots=True)
class HjartaIO:
    """How Hjarta talks to the operator.

    Defaults wrap stdin/stdout for production. Tests supply scripted
    callables; nothing in the FSM touches stdio directly.
    """

    prompt: Callable[[str], str] = field(default=input)
    info: Callable[[str], None] = field(default=print)
    error: Callable[[str], None] = field(default=print)


# --------------------------------------------------------------------- #
# Prompt loader                                                         #
# --------------------------------------------------------------------- #


def _load_prompts() -> dict[str, dict[str, str]]:
    raw = (
        resources.files("ember.spark.hjarta.prompts")
        .joinpath("wizard.toml")
        .read_text(encoding="utf-8")
    )
    return tomllib.loads(raw)


# --------------------------------------------------------------------- #
# The FSM                                                               #
# --------------------------------------------------------------------- #


def run(  # noqa: PLR0911,PLR0915 — explicit FSM with one return per abort state and one per success state
    *,
    config: EmberConfig,
    config_root: Path,
    io: HjartaIO | None = None,
    funi_opener: Callable[[FuniConfig], FuniHandle | Unavailable] | None = None,
    strengr_opener: Callable[
        [StrengrConfig, BrunnrConfig], BrunnrHandle | Disconnected
    ]
    | None = None,
) -> HjartaOutcome:
    """Drive the first-run state machine to completion or to a clean stop.

    ``funi_opener`` and ``strengr_opener`` are test seams; production
    uses the registry defaults.
    """
    io = io or HjartaIO()
    open_funi = funi_opener or funi_handle.open
    open_well = strengr_opener or strengr.open
    prompts = _load_prompts()

    current_state = HjartaState.GREET
    funi: FuniHandle | None = None
    brunnr: BrunnrHandle | None = None
    chosen_name = config.identity.name

    try:
        # ---------------------------------------------------------- GREET
        _emit(io, prompts[HjartaState.GREET])
        if not _confirm(io, prompts[HjartaState.GREET].get("prompt", "")):
            return _abort(HjartaState.GREET, "operator cancelled at greet")

        # ----------------------------------------------------- CHOOSE_FUNI
        current_state = HjartaState.CHOOSE_FUNI
        _emit(io, prompts[HjartaState.CHOOSE_FUNI])
        answer = io.prompt(prompts[HjartaState.CHOOSE_FUNI].get("prompt", "")).strip()
        if answer.lower() == "cancel":
            return _abort(current_state, "operator cancelled at choose_funi")

        # --------------------------------------------------- DISCOVER_FUNI
        current_state = HjartaState.DISCOVER_FUNI
        _emit(io, prompts[HjartaState.DISCOVER_FUNI])
        funi_result = open_funi(config.funi)
        if isinstance(funi_result, Unavailable):
            io.error(
                f"Funi ({config.funi.runtime.value}) is unavailable: "
                f"{funi_result.reason.value} — {funi_result.detail or ''}"
            )
            return _abort(current_state, f"funi unavailable: {funi_result.reason.value}")
        funi = funi_result
        io.info(f"  → connected to {funi.runtime_kind}, model {funi.model_id}")

        # ----------------------------------------------------- CHOOSE_WELL
        current_state = HjartaState.CHOOSE_WELL
        sqlite_path = config.brunnr.sqlite_vec.path if config.brunnr.sqlite_vec else "(unset)"
        _emit(io, prompts[HjartaState.CHOOSE_WELL], sqlite_path=str(sqlite_path))
        well_answer = io.prompt(
            prompts[HjartaState.CHOOSE_WELL].get("prompt", "")
        ).strip()
        # For Phase 6 we only support the default sqlite_vec; a typed
        # path is accepted but the backend stays sqlite_vec.
        chosen_brunnr = config.brunnr
        if well_answer:
            from dataclasses import replace  # noqa: PLC0415

            new_sqlite = (
                None
                if chosen_brunnr.sqlite_vec is None
                else replace(chosen_brunnr.sqlite_vec, path=Path(well_answer))
            )
            chosen_brunnr = replace(chosen_brunnr, sqlite_vec=new_sqlite)

        # -------------------------------------------------- CONFIGURE_WELL
        current_state = HjartaState.CONFIGURE_WELL
        well_path_for_render = (
            str(chosen_brunnr.sqlite_vec.path)
            if chosen_brunnr.sqlite_vec
            else "(unset)"
        )
        _emit(
            io,
            prompts[HjartaState.CONFIGURE_WELL],
            sqlite_path=well_path_for_render,
        )
        brunnr_result = open_well(config.strengr, chosen_brunnr)
        if isinstance(brunnr_result, Disconnected):
            io.error(
                f"Could not open the Well: {brunnr_result.reason.value} — "
                f"{brunnr_result.detail or ''}"
            )
            return _abort(current_state, f"well disconnected: {brunnr_result.reason.value}")
        brunnr = brunnr_result
        io.info(f"  → opened {brunnr.backend_kind} Well")

        # -------------------------------------------------- TEST_RETRIEVAL
        current_state = HjartaState.TEST_RETRIEVAL
        _emit(io, prompts[HjartaState.TEST_RETRIEVAL])
        probe_ok, probe_detail = _probe_round_trip(brunnr)
        if not probe_ok:
            io.error(f"Probe failed: {probe_detail}")
            return _abort(current_state, probe_detail or "probe failed")
        io.info(f"  → {probe_detail}")

        # ------------------------------------------------------ NAME_EMBER
        current_state = HjartaState.NAME_EMBER
        _emit(io, prompts[HjartaState.NAME_EMBER])
        name_answer = io.prompt(prompts[HjartaState.NAME_EMBER].get("prompt", "")).strip()
        if name_answer:
            chosen_name = name_answer

        # -------------------------------------------------- WRITE_IDENTITY
        current_state = HjartaState.WRITE_IDENTITY
        identity = IdentityConfig(name=chosen_name, role=config.identity.role)
        from ember.spark.hjarta.identity import identity_path as _identity_path  # noqa: PLC0415

        target = _identity_path(config_root)
        _emit(io, prompts[HjartaState.WRITE_IDENTITY], identity_path=str(target))
        written_path = save_identity_atomic(config_root, identity)

        # ----------------------------------------------------------- DONE
        current_state = HjartaState.DONE
        _emit(io, prompts[HjartaState.DONE], name=identity.name)
        return HjartaOutcome(
            success=True,
            final_state=HjartaState.DONE,
            identity_path=written_path,
        )

    except KeyboardInterrupt:
        io.info("")
        return _abort(current_state, "operator interrupted")
    finally:
        if funi is not None:
            funi.close()
        if brunnr is not None:
            brunnr.close()


# --------------------------------------------------------------------- #
# Helpers                                                                #
# --------------------------------------------------------------------- #


def _emit(io: HjartaIO, block: dict[str, str], **subs: str) -> None:
    body = block.get("body", "")
    if subs:
        body = body.format(**subs)
    io.info(body.rstrip())


def _confirm(io: HjartaIO, prompt: str) -> bool:
    answer = io.prompt(prompt).strip().lower()
    return answer not in {"cancel", "quit", "q", "no", "n"}


def _abort(state: HjartaState, detail: str) -> HjartaOutcome:
    logger.debug("hjarta: abort at %s: %s", state.value, detail)
    return HjartaOutcome(
        success=False,
        final_state=state,
        identity_path=None,
        detail=detail,
    )


def _probe_round_trip(brunnr: BrunnrHandle) -> tuple[bool, str]:
    """Write a probe chunk, retrieve it, report success or failure.

    The probe doc uses a fixed hash so re-running Hjarta is idempotent
    (the probe chunk is not multiplied across runs). The probe text and
    search query avoid FTS5-reserved characters (no colons; no bare
    ``run`` followed by punctuation that FTS5 reads as a column ref).
    """
    try:
        doc_id = brunnr.add_document(
            Document(
                source="hjarta://probe",
                title="ember-hjarta-probe",
                content_type="probe",
                hash=_PROBE_HASH,
            )
        )
        zero_vec = tuple(0.0 for _ in range(brunnr.embedding_dim))
        probe_text = f"{_PROBE_TEXT} probe_id_{uuid.uuid4().hex[:8]}"
        brunnr.add_chunks(
            [
                Chunk(
                    document_id=doc_id,
                    chunk_index=0,
                    text=probe_text,
                    embedding=zero_vec,
                )
            ]
        )
        # The Brunnr adapter sanitises FTS5 input for us, so plain text
        # is safe here. (Hjarta originally hit a `no such column: run`
        # error from a bare `run:` token; the fix now lives in
        # SqliteVecBrunnr.text_search via _escape_fts5_query.)
        hits = brunnr.text_search("Ember Hjarta first time setup", k=3)
    except Exception as exc:
        return (False, f"probe error: {exc}")

    if not any("probe" in h.text.lower() for h in hits):
        return (False, "probe chunk written but not found via text_search")
    return (True, "probe round trip OK")


__all__ = ["HjartaIO", "HjartaOutcome", "HjartaState", "run"]
