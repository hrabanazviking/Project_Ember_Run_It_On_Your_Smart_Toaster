"""ThoughtForgeCognition — Ember's ThoughtForge cognition binding (E-024).

Binds MindSpark ThoughtForge as Ember's candidate cognition layer,
against the contract ThoughtForge itself froze at its TF-034:
cognition API **v1.0.0** — ``ThoughtForgeCore(config, model_path,
memory_dir, db_path, backend)``, ``think(user_text, retrieval_path,
num_drafts, history, interrupt)`` returning a FinalResponseRecord,
and the package's ``API_VERSION`` / ``api_manifest()`` /
``verify_api_surface()`` freeze machinery. TF-159 consumes this
same contract from ThoughtForge's side; this module is Ember's
side, written from the freeze doc + the live frozen tables, and
proven here with a fake core shaped from them (TF-161's pattern:
consumers needn't be present to prove the shape).

How the binding works:

- **Optional, lazy, never a core dependency.** ThoughtForge is
  imported inside :meth:`ThoughtForgeCognition.open` only. An
  Ember built without it still imports, still runs its Funi turn,
  and gets a typed ``RUNTIME_NOT_INSTALLED`` refusal if the layer
  is switched on. Nothing is added to Ember's (zero) core
  dependency list.
- **Version refusal, never silent corruption.** ``open()`` reads
  the live package's ``API_VERSION`` and refuses with
  ``VERSION_MISMATCH`` when its major differs from the configured
  ``expected_api_major`` (default 1) — the Ember-side half of the
  rule ThoughtForge's TF-162 owns at its service shape. When the
  package offers ``verify_api_surface()``, open() also runs it:
  any drift it reports is a refusal naming the drift count, never
  a shrug.
- **One core = one conversation.** ThoughtForge's standing shape
  (TF-032/TF-035): each core instance holds one conversation's
  will ledger, persona expectation and serialised turn lock. The
  handle therefore owns exactly one core, constructed at open;
  Ember conversations that want parallel cognition open one
  handle each.
- **Custody.** The core is constructed with Ember's configured
  ``memory_dir`` / ``db_path`` (defaulting inside ``~/.ember/``,
  the E-020 tether) and ``tf_config`` passed through unchanged —
  Ember does not shadow ThoughtForge's own config surface
  (TF-032). ``model_path`` goes through only when the operator
  set one; unset, ThoughtForge runs its documented knowledge-only
  shape. No credential is involved in this binding at all, so
  none is carried (TF-160's custody rule is satisfied by absence).
- **History.** Ember ``Episode`` turns become a ThoughtForge
  ``ChatHistory`` built with ThoughtForge's *own* classes
  (``add_user`` / ``add_assistant`` per episode, in order) and
  handed to ``think(history=…)`` — the frozen parameter exists
  for exactly this, and the core renders it via
  ``history.to_prompt_context()``. No history object of Ember's
  own invention is passed.
- **The reply.** FinalResponseRecord fields map straight:
  ``text``, ``turn_id``, ``mode``, ``enforcement_passed``,
  ``citations``, ``token_count``. A record with empty text is
  returned as-is — an honestly empty answer, never dressed up.
  Exceptions from the core fold into an ERROR-shaped reply whose
  text names the failure (ThoughtForge's ``think`` is documented
  to never raise on content failure, so an exception is a binding
  or environment failure, and is labelled as such).
- **Profile gate + draft cap.** ``open()`` is normally reached
  through :func:`ember.spark.cognition.handle.open_cognition`,
  which refuses disabled / unaffordable-profile configs first;
  the adapter re-checks the cap: a resolved ``num_drafts`` below 1
  is refused as ``CONFIG_INVALID`` here instead of surfacing as
  ThoughtForge's ``ValueError`` mid-turn.
"""

from __future__ import annotations

import importlib
import logging
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType
from typing import Any

from ember.schemas.cognition import (
    CognitionHealth,
    CognitionReply,
    CognitionUnavailable,
    CognitionUnavailableReason,
)
from ember.schemas.config import CognitionConfig
from ember.schemas.episode import Episode

logger = logging.getLogger(__name__)

PROVIDER = "thoughtforge"


def _now_utc() -> datetime:
    return datetime.now(tz=UTC)


def _import_thoughtforge() -> ModuleType:
    """Import ThoughtForge's cognition package (isolated for tests)."""
    return importlib.import_module("thoughtforge.cognition")


class ThoughtForgeCognition:
    """ThoughtForge-backed cognition handle. Implements CognitionHandle."""

    provider: str = PROVIDER

    def __init__(
        self,
        *,
        core: Any,
        module: ModuleType,
        api_version: str,
        num_drafts: int | None,
    ) -> None:
        self._core = core
        self._module = module
        self.api_version = api_version
        self._num_drafts = num_drafts
        self._last_ok: datetime | None = None

    # ------------------------------------------------------------- open

    @classmethod
    def open(
        cls,
        config: CognitionConfig,
        *,
        module: ModuleType | None = None,
    ) -> ThoughtForgeCognition | CognitionUnavailable:
        """Construct the ThoughtForge core, or refuse truthfully.

        ``module`` is the already-imported ``thoughtforge.cognition``
        package; tests inject a fake shaped from the TF-034 freeze.
        Production callers leave it None and the real package is
        imported lazily here.
        """
        num_drafts = config.resolved_num_drafts
        if num_drafts is not None and num_drafts < 1:
            return CognitionUnavailable(
                reason=CognitionUnavailableReason.CONFIG_INVALID,
                detail=(
                    f"cognition num_drafts is {num_drafts}; a turn "
                    "asked for zero drafts is a caller error, not a "
                    "knowledge-only turn (ThoughtForge TF-034)"
                ),
            )
        if module is None:
            try:
                module = _import_thoughtforge()
            except ImportError as exc:
                return CognitionUnavailable(
                    reason=CognitionUnavailableReason.RUNTIME_NOT_INSTALLED,
                    detail=(
                        "ThoughtForge is not installed in this "
                        f"environment ({exc}); the cognition layer "
                        "is an optional neighbour, never a core "
                        "dependency — Ember's Funi turn still runs"
                    ),
                )
        api_version = str(getattr(module, "API_VERSION", ""))
        major = _major_of(api_version)
        if major is None or major != config.expected_api_major:
            return CognitionUnavailable(
                reason=CognitionUnavailableReason.VERSION_MISMATCH,
                detail=(
                    f"ThoughtForge cognition API is "
                    f"{api_version or 'unversioned'}, this binding "
                    f"expects major {config.expected_api_major} "
                    "(TF-034 froze v1.0.0); refusing rather than "
                    "adapting silently (TF-162's rule)"
                ),
            )
        verify = getattr(module, "verify_api_surface", None)
        if callable(verify):
            try:
                problems = verify()
            except Exception as exc:  # drift check itself failed
                return CognitionUnavailable(
                    reason=CognitionUnavailableReason.VERSION_MISMATCH,
                    detail=(
                        "ThoughtForge's verify_api_surface() could "
                        f"not run ({exc}); refusing a surface that "
                        "cannot prove itself against its freeze"
                    ),
                )
            if problems:
                return CognitionUnavailable(
                    reason=CognitionUnavailableReason.VERSION_MISMATCH,
                    detail=(
                        f"ThoughtForge's live cognition surface "
                        f"drifts from its TF-034 freeze in "
                        f"{len(problems)} place(s); first: "
                        f"{problems[0]}"
                    ),
                )
        core_cls = getattr(module, "ThoughtForgeCore", None)
        if core_cls is None:
            return CognitionUnavailable(
                reason=CognitionUnavailableReason.RUNTIME_NOT_INSTALLED,
                detail=(
                    "the installed thoughtforge.cognition package "
                    "has no ThoughtForgeCore — not the package this "
                    "binding was written against (TF-034)"
                ),
            )
        try:
            core = core_cls(
                config=dict(config.tf_config),
                model_path=(
                    Path(config.model_path).expanduser()
                    if config.model_path is not None
                    else None
                ),
                memory_dir=Path(config.memory_dir).expanduser(),
                db_path=Path(config.db_path).expanduser(),
                backend=None,
            )
        except Exception as exc:
            return CognitionUnavailable(
                reason=CognitionUnavailableReason.CONFIG_INVALID,
                detail=(
                    f"ThoughtForgeCore refused its construction "
                    f"arguments ({exc}); ThoughtForge's config "
                    "surface raises on an invalid selection rather "
                    "than defaulting silently (TF-032)"
                ),
            )
        handle = cls(
            core=core,
            module=module,
            api_version=api_version,
            num_drafts=num_drafts,
        )
        handle._last_ok = _now_utc()
        return handle

    # ------------------------------------------------------------- think

    def think(
        self,
        user_text: str,
        episodes: Sequence[Episode] = (),
    ) -> CognitionReply:
        """Run one ThoughtForge turn and map its final record.

        Never raises: a core exception folds into an ERROR-shaped
        reply naming the failure as a binding/environment failure
        (ThoughtForge's think() itself never raises on content).
        """
        history = self._build_history(episodes)
        try:
            record = self._core.think(
                user_text,
                num_drafts=self._num_drafts,
                history=history,
            )
        except Exception as exc:
            logger.debug("thoughtforge think: core raised %s", exc)
            return CognitionReply(
                text=(
                    "[thoughtforge cognition failed: "
                    f"{type(exc).__name__}: {exc}]"
                ),
                provider=self.provider,
                api_version=self.api_version,
                mode="error",
            )
        self._last_ok = _now_utc()
        return CognitionReply(
            text=str(getattr(record, "text", "") or ""),
            provider=self.provider,
            api_version=self.api_version,
            turn_id=str(getattr(record, "turn_id", "") or ""),
            mode=str(getattr(record, "mode", "") or ""),
            enforcement_passed=bool(
                getattr(record, "enforcement_passed", False)
            ),
            citations=tuple(
                str(c) for c in (getattr(record, "citations", ()) or ())
            ),
            token_count=_safe_int(getattr(record, "token_count", None)),
        )

    def _build_history(self, episodes: Sequence[Episode]) -> Any | None:
        """Ember episodes → a ThoughtForge ChatHistory, or None.

        Built with ThoughtForge's own classes (frozen package
        exports at TF-034): one user + one assistant message per
        episode, oldest first. None when there are no episodes —
        the frozen default — or when the installed package carries
        no ChatHistory (a drifted surface; the turn then proceeds
        without history rather than fabricating a look-alike).
        """
        if not episodes:
            return None
        history_cls = getattr(self._module, "ChatHistory", None)
        if history_cls is None:
            return None
        history = history_cls()
        for episode in episodes:
            history.add_user(episode.operator_input)
            history.add_assistant(episode.ember_reply)
        return history

    # ------------------------------------------------------------- health

    def health(self) -> CognitionHealth:
        return CognitionHealth(
            provider=self.provider,
            api_version=self.api_version,
            last_ok=self._last_ok,
        )

    def close(self) -> None:
        unload = getattr(self._core, "unload_model", None)
        if callable(unload):
            try:
                unload()
            except Exception as exc:  # close must not raise
                logger.debug("thoughtforge close: unload failed %s", exc)
        return None


# --------------------------------------------------------------------- #
# Module-level open() for the registry                                  #
# --------------------------------------------------------------------- #


def open(config: CognitionConfig) -> ThoughtForgeCognition | CognitionUnavailable:
    return ThoughtForgeCognition.open(config)


# --------------------------------------------------------------------- #
# Helpers                                                                #
# --------------------------------------------------------------------- #


def _major_of(api_version: str) -> int | None:
    """The major of a semver string, or None when unparseable."""
    head = api_version.split(".", 1)[0].strip()
    try:
        return int(head)
    except ValueError:
        return None


def _safe_int(value: object) -> int | None:
    if value is None:
        return None
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


__all__ = ["PROVIDER", "ThoughtForgeCognition", "open"]
