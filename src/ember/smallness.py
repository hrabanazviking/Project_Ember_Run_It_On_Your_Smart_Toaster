"""Graceful smallness — shedding features at budget's edge (E-054).

Part III, slice E-054. Roadmap line: "at budget's edge the
companion sheds features by the stated ladder, announcing
each shed."

The budget book (E-041, ``ember.budgets``) states what a
turn may cost on each profile. Until this slice nothing in
the core *reacted* when a live companion actually approached
that ceiling: a process whose memory crept toward its
profile's turn-RAM ceiling would keep paying for every
feature it owns — summarising the history it drops, embedding
every question for semantic memory search, carrying the
profile's full history window — until the machine, not
Ember, decided what died. On a 512 MiB toaster-class host
that decision is the OOM killer's, and it does not announce
itself.

This module is the stated ladder, in three parts:

* **Reading the room (stdlib only).** The process's own
  resident memory from ``/proc/self/status`` (``VmRSS``,
  the Linux shape every Ember host exposes). A reading
  that cannot be taken is *unknown* (``None``), never a
  guessed number — and unknown never votes (below).
* **Judging the room (pure).** :func:`assess` folds one
  reading against the profile's turn-RAM ceiling from the
  budget book into a level: ``COMFORTABLE`` (under 75% of
  the ceiling), ``EDGE`` (at/over 75%), ``STRAINED``
  (at/over 90%), ``OVER`` (at/over the ceiling itself).
  An unknown reading is COMFORTABLE with its reason
  stated plainly — a gauge that cannot be read never
  invents a crisis, exactly as E-051's unknown thermal
  and E-053's unknown charge never vote.
* **The ladder, and its announcements.** Each level past
  COMFORTABLE sheds one more feature, cheapest to lose
  first, and **every shed carries one plain sentence**
  the companion says out loud (the chat wiring writes it
  to the person's screen and to the diary, E-034):

  1. **History summaries** (EDGE) — the extractive
     summary of dropped history (E-021) is extra work
     per turn; the dropped episodes are still reported
     as dropped, only the summary is not composed.
  2. **Semantic memory search** (STRAINED) — the turn's
     question is no longer embedded for hybrid search;
     memory search runs on plain words only (the
     existing no-vector shape, E-029/E-030), which also
     saves the embed call itself. Some subtler matches
     may be missed, and the announcement says so.
  3. **The wide history window** (OVER) — the history
     the turn carries narrows to the book's smallest
     allowance (the toaster's 512 tokens / 3 episodes,
     or the profile's own allowance when that is already
     smaller). Everything is still *saved*; only what
     rides in this turn's prompt narrows.

  **Never shed, at any level:** answering the person's
  turn, saving the turn to memory, the announcements
  themselves, and tool approval / safety discipline.
  Smallness is about comforts, never about the companion
  ceasing to be present, honest, or safe. A shed is not
  sticky: the guard is consulted per turn, and when room
  returns a shed feature is restored — and the restore
  is announced too, in the same plain words, so the
  person is never left believing a feature is gone that
  has quietly come back (or the reverse).

The one wiring in this slice is the chat turn
(``ember.spark.munnr.chat``), the place all three rungs
have real consumers: the window the turn builds
(``window_history`` takes the plan's narrowed conversation
config) and the retrieval the turn runs (``_retrieve``
takes the plan's text-only flag). Bulk background work is
not on this ladder — it already has its own manners
(E-051's patience, E-053's duty cycling), and an embed
batch shed mid-job would mark its chunks failed while the
ingest journal marks their document done (the chunks
would be *lost*, not deferred) — so background shedding
by this ladder is deliberately not wired there, and the
record says why.

Policy constants, not measurements: the three fraction
lines below are stated manners, pinned by the E-054 tests
so they can only change deliberately. What the ladder did
on the campaign VM when driven across its lines lives in
``docs/architecture/E-054_GRACEFUL_SMALLNESS.md``.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from ember.budgets import budget_for
from ember.schemas.config import ConversationConfig, ConversationProfile

# --------------------------------------------------------------------- #
# Policy — the stated ladder (E-054)                                    #
# --------------------------------------------------------------------- #

#: Fraction of the profile's turn-RAM ceiling at/over
#: which the companion is at budget's edge: rung 1 sheds.
EDGE_FRACTION = 0.75

#: Fraction at/over which the room is strained: rung 2
#: sheds as well.
STRAINED_FRACTION = 0.90

#: Fraction at/over which the process is at (or past)
#: the ceiling itself: rung 3 sheds as well. Stated as
#: a fraction so the three lines read as one ladder.
OVER_FRACTION = 1.00

#: Where Linux exposes this process's own memory
#: (the shape every Ember host in the book exposes).
PROC_STATUS = Path("/proc/self/status")


class ShedFeature(Enum):
    """One feature the ladder can shed, in ladder order."""

    HISTORY_SUMMARIES = "history_summaries"
    SEMANTIC_RETRIEVAL = "semantic_retrieval"
    WIDE_HISTORY = "wide_history"


#: The ladder, cheapest to lose first. The plan sheds a
#: prefix of this tuple — never a later rung while an
#: earlier one is kept.
SHED_LADDER: tuple[ShedFeature, ...] = (
    ShedFeature.HISTORY_SUMMARIES,
    ShedFeature.SEMANTIC_RETRIEVAL,
    ShedFeature.WIDE_HISTORY,
)

#: One plain sentence per shed, said out loud when the
#: shed happens. Written for the person, not the log:
#: what is happening, why, and what it costs them.
SHED_ANNOUNCEMENTS: dict[ShedFeature, str] = {
    ShedFeature.HISTORY_SUMMARIES: (
        "I'm getting close to my memory limit on this machine, so "
        "I've stopped writing summaries of our earlier conversation "
        "— nothing is lost, and everything is still saved."
    ),
    ShedFeature.SEMANTIC_RETRIEVAL: (
        "To stay within my memory limit, my memory search is using "
        "plain words only for now — some subtler matches may be missed."
    ),
    ShedFeature.WIDE_HISTORY: (
        "To stay within my memory limit, I'm keeping only our most "
        "recent few exchanges in mind for now — everything is still saved."
    ),
}

#: One plain sentence per restore, said when room returns
#: and a shed feature comes back.
RESTORE_ANNOUNCEMENTS: dict[ShedFeature, str] = {
    ShedFeature.HISTORY_SUMMARIES: (
        "I have room again, so I'm writing summaries of our earlier "
        "conversation once more."
    ),
    ShedFeature.SEMANTIC_RETRIEVAL: (
        "I have room again, so my memory search is back to its "
        "full strength."
    ),
    ShedFeature.WIDE_HISTORY: (
        "I have room again, so I'm keeping our fuller conversation "
        "in mind once more."
    ),
}


class SmallnessLevel(Enum):
    """How close the process stands to its budget's edge."""

    COMFORTABLE = "comfortable"
    EDGE = "edge"
    STRAINED = "strained"
    OVER = "over"




@dataclass(frozen=True, slots=True)
class SmallnessPlan:
    """What one level sheds, and what the sheds change."""

    level: SmallnessLevel
    #: The features shed at this level — a prefix of
    #: :data:`SHED_LADDER`, in ladder order.
    sheds: tuple[ShedFeature, ...]

    @property
    def announcements(self) -> tuple[str, ...]:
        """One plain sentence per shed, in ladder order."""
        return tuple(SHED_ANNOUNCEMENTS[feature] for feature in self.sheds)

    @property
    def semantic_retrieval(self) -> bool:
        """True while memory search keeps its full (hybrid) shape."""
        return ShedFeature.SEMANTIC_RETRIEVAL not in self.sheds

    def conversation_config(self, config: ConversationConfig) -> ConversationConfig:
        """The conversation config this plan runs a turn under.

        Rung 1 turns history summarisation off (the window
        still reports what it dropped — E-021's honesty is
        not the shed, only the summary's composition is).
        Rung 3 narrows the window to the book's smallest
        allowance: the toaster profile's resolved caps, or
        the config's own resolved caps when those are
        already smaller (an operator's explicit smaller
        override is never widened by shedding). With no
        sheds the config is returned unchanged — the very
        same object, so an unshed turn is byte-for-byte
        the pre-E-054 shape.
        """
        if not self.sheds:
            return config
        narrowed = config
        if ShedFeature.HISTORY_SUMMARIES in self.sheds:
            narrowed = dataclasses.replace(narrowed, summarise_dropped=False)
        if ShedFeature.WIDE_HISTORY in self.sheds:
            smallest = ConversationConfig(profile=ConversationProfile.TOASTER)
            narrowed = dataclasses.replace(
                narrowed,
                token_budget=min(
                    narrowed.resolved_token_budget,
                    smallest.resolved_token_budget,
                ),
                max_episodes=min(
                    narrowed.resolved_max_episodes,
                    smallest.resolved_max_episodes,
                ),
            )
        return narrowed


_PLANS: dict[SmallnessLevel, SmallnessPlan] = {
    level: SmallnessPlan(level=level, sheds=SHED_LADDER[:rungs])
    for level, rungs in (
        (SmallnessLevel.COMFORTABLE, 0),
        (SmallnessLevel.EDGE, 1),
        (SmallnessLevel.STRAINED, 2),
        (SmallnessLevel.OVER, 3),
    )
}


def plan_for(level: SmallnessLevel) -> SmallnessPlan:
    """The shed plan for one level."""
    return _PLANS[level]


@dataclass(frozen=True, slots=True)
class SmallnessAssessment:
    """One reading judged against one profile's ceiling."""

    profile: ConversationProfile
    #: This process's resident memory (MiB), or ``None``
    #: when it could not be read — never guessed.
    rss_mib: float | None
    #: The profile's turn-RAM ceiling from the budget book.
    ceiling_mib: float
    #: rss / ceiling, or ``None`` when the reading is unknown.
    fraction: float | None
    plan: SmallnessPlan
    #: One plain sentence naming the deciding fact.
    reason: str


# --------------------------------------------------------------------- #
# Reading the room                                                      #
# --------------------------------------------------------------------- #


def read_rss_mib(status_path: Path = PROC_STATUS) -> float | None:
    """This process's resident memory in MiB, or ``None``.

    Reads ``VmRSS`` from ``/proc/self/status`` (kibibytes).
    Any failure — no such file, no such line, an
    unparseable value — reads ``None``: unknown, never a
    guessed number.
    """
    try:
        text = status_path.read_text(encoding="ascii", errors="replace")
    except OSError:
        return None
    for line in text.splitlines():
        if line.startswith("VmRSS:"):
            parts = line.split()
            try:
                return float(parts[1]) / 1024.0
            except (IndexError, ValueError):
                return None
    return None


# --------------------------------------------------------------------- #
# Judging the room (pure)                                               #
# --------------------------------------------------------------------- #


def assess(profile: ConversationProfile, rss_mib: float | None) -> SmallnessAssessment:
    """Judge one memory reading against the profile's ceiling.

    The ceiling is the budget book's turn-RAM ceiling for
    the profile — the cost a turn may reach, which is the
    budget a running companion actually lives against.
    Lines are strictest-first; an unknown reading never
    votes, so nothing sheds on a gauge that cannot be read.
    """
    ceiling = budget_for(profile).turn_ram_mib
    if rss_mib is None:
        return SmallnessAssessment(
            profile=profile,
            rss_mib=None,
            ceiling_mib=ceiling,
            fraction=None,
            plan=_PLANS[SmallnessLevel.COMFORTABLE],
            reason="this process's memory use cannot be read — unknown "
            "never votes, so nothing is shed",
        )
    fraction = rss_mib / ceiling if ceiling > 0 else 1.0
    if fraction >= OVER_FRACTION:
        level = SmallnessLevel.OVER
        reason = (
            f"the companion is using {rss_mib:.0f} MiB of the "
            f"{profile.value} profile's {ceiling:.0f} MiB turn budget "
            "— at the ceiling, the full ladder is shed"
        )
    elif fraction >= STRAINED_FRACTION:
        level = SmallnessLevel.STRAINED
        reason = (
            f"the companion is using {rss_mib:.0f} MiB of the "
            f"{profile.value} profile's {ceiling:.0f} MiB turn budget "
            "— strained, so summaries and semantic search are shed"
        )
    elif fraction >= EDGE_FRACTION:
        level = SmallnessLevel.EDGE
        reason = (
            f"the companion is using {rss_mib:.0f} MiB of the "
            f"{profile.value} profile's {ceiling:.0f} MiB turn budget "
            "— at budget's edge, so history summaries are shed"
        )
    else:
        level = SmallnessLevel.COMFORTABLE
        reason = (
            f"the companion is using {rss_mib:.0f} MiB of the "
            f"{profile.value} profile's {ceiling:.0f} MiB turn budget "
            "— comfortable, nothing is shed"
        )
    return SmallnessAssessment(
        profile=profile,
        rss_mib=rss_mib,
        ceiling_mib=ceiling,
        fraction=fraction,
        plan=_PLANS[level],
        reason=reason,
    )


def assess_system(profile: ConversationProfile) -> SmallnessAssessment:
    """Read this process's memory right now and judge it."""
    return assess(profile, read_rss_mib())


# --------------------------------------------------------------------- #
# The guard — per-turn consults, announcements on change                #
# --------------------------------------------------------------------- #


class SmallnessGuard:
    """Consults the ladder per turn and announces changes.

    Each :meth:`consult` re-reads the process's memory, so
    a companion that grows into its ceiling sheds rung by
    rung as it crosses the lines, and a companion whose
    room returns (a smaller history, a quieter moment)
    restores them the same way. Announcements fire **only
    on change**: a feature newly shed speaks its shed
    sentence; a feature newly restored speaks its restore
    sentence; a steady state says nothing, so a long
    session at the edge does not repeat itself every turn.
    The announcer is any one-sentence callable (the chat
    wiring passes one that writes to the person's screen
    and the diary); the guard also keeps the sentences it
    has spoken in ``announcements`` for the record.
    """

    def __init__(
        self,
        profile: ConversationProfile,
        *,
        assess_fn: Callable[[], SmallnessAssessment] | None = None,
        announce: Callable[[str], None] | None = None,
    ) -> None:
        self._profile = profile
        self._assess_fn = assess_fn or (lambda: assess_system(profile))
        self._announce = announce
        self._active: tuple[ShedFeature, ...] = ()
        self.announcements: list[str] = []
        self.last_assessment: SmallnessAssessment | None = None

    @property
    def profile(self) -> ConversationProfile:
        return self._profile

    @property
    def active_sheds(self) -> tuple[ShedFeature, ...]:
        """The features shed as of the last consultation."""
        return self._active

    def consult(self) -> SmallnessAssessment:
        """One consultation: judge the room, announce any change."""
        assessment = self._assess_fn()
        self.last_assessment = assessment
        new = assessment.plan.sheds
        if new != self._active:
            for feature in SHED_LADDER:
                if feature in new and feature not in self._active:
                    self._speak(SHED_ANNOUNCEMENTS[feature])
                elif feature in self._active and feature not in new:
                    self._speak(RESTORE_ANNOUNCEMENTS[feature])
            self._active = new
        return assessment

    def _speak(self, sentence: str) -> None:
        self.announcements.append(sentence)
        if self._announce is not None:
            self._announce(sentence)


__all__ = [
    "EDGE_FRACTION",
    "OVER_FRACTION",
    "PROC_STATUS",
    "RESTORE_ANNOUNCEMENTS",
    "SHED_ANNOUNCEMENTS",
    "SHED_LADDER",
    "STRAINED_FRACTION",
    "ShedFeature",
    "SmallnessAssessment",
    "SmallnessGuard",
    "SmallnessLevel",
    "SmallnessPlan",
    "assess",
    "assess_system",
    "plan_for",
    "read_rss_mib",
]
