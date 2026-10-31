"""Update weight — what an update costs to fetch and apply (E-052).

Part III, slice E-052. Roadmap line: "an update's download +
apply cost per profile (metered connections respected)."

Until this slice Ember had no update channel at all (that
is E-183's to build: signed, user-invited — "no silent
auto-anything") and nobody had ever priced one. But the
price decides the manners: a companion for normal folks on
tiny hardware will often live behind a *metered*
connection — a capped mobile plan, a shared village link —
where bytes are money, and an update that helps itself to
the wire uninvited is a theft, however small. So this
slice weighs the update first, in code, before any channel
exists to carry one:

* **The download.** An update of the core is a wheel: the
  package tree, deflated. :func:`download_bytes_for_tree`
  builds that wheel shape in memory (stdlib ``zipfile``,
  sorted entries, fixed compression) and returns its size —
  the bytes that would cross the wire. Measured on the
  campaign VM on this slice's final tree: **293,387 B**
  (~0.28 MiB), pinned in the budget book
  (``ember.budgets``, ``MEASURED_UPDATE_*``).
* **The apply.** Installing replaces the old package with
  the new one while the download still sits on disk, so the
  peak disk cost of applying is stated as a formula, not a
  hope: ``download + old installed + new installed``. At
  this slice's measurements that is ~1.76 MiB — inside even
  the toaster's room many times over, stated per profile by
  :func:`costs_per_profile`.
* **Metered connections are respected — structurally.**
  :func:`decide_update` never returns "go ahead silently".
  An update proceeds only when it is *user-invited*,
  *unmetered*, and *within the profile's download ceiling*
  (the profile's install ceiling from the budget book — an
  update may not download more than a whole install may
  weigh). On a metered connection the answer is always
  ASK FIRST, with the byte cost stated in the reason, at
  any size: smallness is not consent. Over the ceiling the
  answer is NO at any consent level short of the channel's
  own explicit override, which is E-183's to design if it
  ever does — this slice's word is the cost and the line.

The model is never part of an Ember update's weight: a
model pull is the model ladder's own act (gigabytes, its
own consent), exactly as the budget book never folds the
model into Ember's costs.

Stdlib only, like the rest of the core. This module
downloads nothing and applies nothing; it *prices* and
*judges*. The channel is E-183.
"""

from __future__ import annotations

import io
import zipfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from ember.budgets import budget_for
from ember.schemas.config import ConversationProfile

_MIB = 1024 * 1024


# --------------------------------------------------------------------- #
# Weighing an update                                                    #
# --------------------------------------------------------------------- #


def _package_files(root: Path) -> list[Path]:
    """The files an install of the package carries.

    Bytecode caches are a runtime artefact (the budget
    book's standing rule, E-041), not shipped weight.
    """
    return sorted(
        p
        for p in root.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
    )


def package_tree_bytes(root: Path) -> int:
    """The unpacked (installed) weight of a package tree."""
    return sum(p.stat().st_size for p in _package_files(root))


def download_bytes_for_tree(root: Path) -> int:
    """The download weight of an update carrying this tree.

    Builds the wheel shape — the package tree deflated
    into a zip archive, entries sorted so the shape is
    deterministic — in memory and returns its size in
    bytes: what would cross the wire.
    """
    buffer = io.BytesIO()
    with zipfile.ZipFile(
        buffer, "w", zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for path in _package_files(root):
            archive.write(path, path.relative_to(root.parent))
    return buffer.tell()


@dataclass(frozen=True, slots=True)
class UpdateCost:
    """One update's full price, stated in bytes."""

    #: What crosses the wire (the wheel shape, deflated).
    download_bytes: int
    #: What the new package weighs once installed.
    installed_bytes: int

    @property
    def apply_peak_disk_bytes(self) -> int:
        """Peak disk during apply: download + old + new.

        The installer holds the downloaded wheel, unpacks
        the new package beside the old one, and only then
        removes the old — so for a moment all three stand
        on the disk at once. Same-version updates are the
        shape priced here, so old and new weigh the same.
        """
        return self.download_bytes + 2 * self.installed_bytes


def plan_update(*, download_bytes: int, installed_bytes: int) -> UpdateCost:
    """State one update's cost from its two measured weights."""
    return UpdateCost(download_bytes=download_bytes, installed_bytes=installed_bytes)


# --------------------------------------------------------------------- #
# Per-profile judgement                                                 #
# --------------------------------------------------------------------- #


def download_ceiling_bytes(profile: ConversationProfile) -> int:
    """The most an update may download for one profile.

    Read from the budget book's install ceiling for the
    profile — an update that downloads more than a whole
    install may weigh is not an update, it is a reinstall
    wearing an update's name, and it is priced as one.
    """
    return int(budget_for(profile).install_mib * _MIB)


class UpdateDecision(Enum):
    """Whether an update may proceed, and on whose word."""

    READY = "ready"
    ASK_FIRST = "ask_first"
    INVITE_REQUIRED = "invite_required"
    EXCEEDS_BUDGET = "exceeds_budget"


@dataclass(frozen=True, slots=True)
class UpdateVerdict:
    """One judgement of one update, with its reason stated."""

    decision: UpdateDecision
    #: One plain sentence naming the deciding fact and the
    #: byte cost — on a metered connection the price is
    #: always spoken before any byte moves.
    reason: str


def decide_update(
    cost: UpdateCost,
    profile: ConversationProfile,
    *,
    metered: bool,
    user_invited: bool,
) -> UpdateVerdict:
    """Judge one update for one profile on one connection.

    The ladder, in order — the first rung that speaks
    decides:

    1. **Over the profile's download ceiling** →
       ``EXCEEDS_BUDGET``, whatever the connection or the
       invitation: the profile cannot carry it as an
       update.
    2. **Metered connection** → ``ASK_FIRST``, at *any*
       size. Metered bytes are the operator's money; the
       cost is stated in the reason and a person decides.
       An invitation given earlier, in general terms, is
       not consent to this download at this price.
    3. **Not user-invited** → ``INVITE_REQUIRED``. There
       is no silent auto-anything (E-183's law, stated
       here where the costs are): an unmetered wire does
       not invite an update by itself.
    4. Otherwise → ``READY``: invited, unmetered, and
       within the ceiling.
    """
    ceiling = download_ceiling_bytes(profile)
    if cost.download_bytes > ceiling:
        return UpdateVerdict(
            decision=UpdateDecision.EXCEEDS_BUDGET,
            reason=(
                f"the update downloads {cost.download_bytes:,} B, over the "
                f"{profile.value} ceiling of {ceiling:,} B — it does not "
                "fit this profile as an update"
            ),
        )
    if metered:
        return UpdateVerdict(
            decision=UpdateDecision.ASK_FIRST,
            reason=(
                f"the connection is metered and the update downloads "
                f"{cost.download_bytes:,} B — the price is stated and a "
                "person decides before any byte moves"
            ),
        )
    if not user_invited:
        return UpdateVerdict(
            decision=UpdateDecision.INVITE_REQUIRED,
            reason=(
                f"the update downloads {cost.download_bytes:,} B and no "
                "invitation stands — updates are user-invited, never silent"
            ),
        )
    return UpdateVerdict(
        decision=UpdateDecision.READY,
        reason=(
            f"invited, unmetered, and the {cost.download_bytes:,} B "
            f"download fits the {profile.value} ceiling of {ceiling:,} B"
        ),
    )


def costs_per_profile(
    cost: UpdateCost,
) -> tuple[tuple[ConversationProfile, int, bool], ...]:
    """The update's price against every profile, smallest first.

    Each row is ``(profile, download_ceiling_bytes, fits)``
    — the per-profile table the roadmap asks this slice
    for, derived from the book so it can never drift from
    the ceilings it judges against.
    """
    from ember.budgets import PROFILE_ORDER

    rows = []
    for profile in PROFILE_ORDER:
        ceiling = download_ceiling_bytes(profile)
        rows.append((profile, ceiling, cost.download_bytes <= ceiling))
    return tuple(rows)


__all__ = [
    "UpdateCost",
    "UpdateDecision",
    "UpdateVerdict",
    "costs_per_profile",
    "decide_update",
    "download_bytes_for_tree",
    "download_ceiling_bytes",
    "package_tree_bytes",
    "plan_update",
]
