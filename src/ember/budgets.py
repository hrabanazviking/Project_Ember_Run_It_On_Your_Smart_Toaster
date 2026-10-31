"""The budget book — per-profile ceilings for the Ember core (E-041).

Part III opens here. Tiny hardware is this project's soul, and
until this slice the core's size had never been weighed by the
campaign: the front door claimed "~50 MB" of RAM and "~50 MB"
installed (E-015, docket 67) and nobody had measured either.
E-041 measured the core on the VM profile (method and full
numbers in ``docs/architecture/E-041_BUDGET_BOOK.md``) and this
module is the book those measurements bought, in code:

* **Four profiles**, the ones E-021 already names —
  :class:`~ember.schemas.config.ConversationProfile`'s
  ``toaster`` (the smallest, the project's namesake floor),
  ``phone``, ``pi`` and ``laptop``. Each profile's ceiling set
  covers the four costs the roadmap names: install size, idle
  RAM, turn RAM, and storage growth per month.
* **Ceilings price the Ember core only** — the Python package,
  its default local Well, its diary and journal. The language
  model is *not* Ember's cost and is never folded in: the model
  ladder (which model fits which host) is the FUNI docs' table,
  and the book states each profile's reference host so a reader
  can add the two honestly. A ceiling that silently included a
  model would be a claim Ember cannot keep on its own.
* **Measured anchors, not wishes.** The constants below record
  what the core actually cost on measurement day; every ceiling
  is a stated multiple of the anchor it governs, so a future
  slice (E-042) can turn the book into tests that fail loudly
  when the core outgrows its profile instead of drifting.
* **Storage growth is workload-shaped.** A turn costs a fixed
  number of bytes (one Well episode + its diary lines); a
  month's growth is that cost times the turns, so the book
  projects growth at a stated reference workload (20 turns a
  day) instead of pretending growth is a property of the code
  alone. Documents an operator ingests into the Well are their
  own act, not growth — they are bounded by the ingest caps
  (E-015 §4), not by this book.

Stdlib only, like the rest of the core. This module measures
nothing at runtime; it *states* the book. The measuring lives
in the E-041 slice record and in E-042's tests.
"""

from __future__ import annotations

from dataclasses import dataclass

from ember.schemas.config import ConversationConfig, ConversationProfile

_MIB = 1024 * 1024

# --------------------------------------------------------------------- #
# Measured anchors (VM profile, 2026-10-31 — E-041 slice record)        #
# --------------------------------------------------------------------- #

#: Bytes of one persisted turn in the default (sqlite_vec) Well:
#: a typical turn (operator ~40 words, reply ~40 words) measured
#: over 100 episodes — (143,360 − 81,920) / 100 = 614.4, recorded
#: as the whole-byte floor the projection uses.
WELL_BYTES_PER_EPISODE = 614

#: Bytes of diary per turn (E-034): two short fact lines
#: ("answered", "saved") at ~40 bytes each, measured from a real
#: session file (660 bytes held a session's start/stop lines plus
#: five turns of two lines each).
DIARY_BYTES_PER_TURN = 80

#: The reference workload the monthly projection is stated at:
#: twenty turns a day, every day — a companion in daily use,
#: not a benchmark burst.
REFERENCE_TURNS_PER_DAY = 20

#: What the installed core weighed on measurement day: the
#: package itself (729,802 B, byte-identical installed and in
#: source), its dist-info (83,102 B) and the one default extra a
#: working install carries, ``sqlite-vec`` (165,939 B with its
#: dist-info) — 978,843 bytes in all, bytecode caches excluded
#: (they are a runtime artefact, counted in the book's prose).
MEASURED_INSTALL_BYTES = 978_843

#: The heaviest idle shape measured: the CLI surface imported
#: and the default Well open — 40.7 MiB RSS on the VM. (Idle
#: without the Well measured 25.3 MiB; the Well is part of a
#: running companion, so the book anchors on the heavier shape.)
MEASURED_IDLE_RAM_MIB = 40.7

#: The heaviest turn shape measured: five real chat turns
#: against the real Well (labelled fake model), the largest
#: per-profile peak — 40.1 MiB RSS, flat across all four
#: profiles at fixture scale.
MEASURED_TURN_RAM_MIB = 40.1

#: Cold start to first word, E-046: the median of seven fresh
#: ``ember ask`` processes on the toaster profile (real CLI,
#: real sqlite_vec Well, loopback wire-shape model answering
#: instantly — so this prices Ember's own startup, not a
#: model's thinking time), 2.87 s. The VM was heavily
#: contended during the measurement (sibling campaigns
#: running; 5-minute load average ~8), so the anchor is a
#: contended median: on a quiet machine E-032's whole
#: second-run ask took 0.93 s end to end. Method and every
#: run's numbers live in
#: ``docs/architecture/E-046_COLD_START.md``. Docket 90
#: stands — a VM anchor, re-anchored per device at
#: E-047–E-049.
MEASURED_COLD_START_FIRST_WORD_S = 2.87

# --------------------------------------------------------------------- #
# Measured anchors (Raspberry Pi 5 — E-047, the Pi proof)               #
# --------------------------------------------------------------------- #

#: The device: Mimir (``purpleviking1``), a Raspberry Pi 5
#: Model B Rev 1.1 (aarch64, 16 GiB RAM, Python 3.11.2) — a
#: real Pi, named, not a simulation. Ember was installed from
#: a clean clone of the campaign branch at fae0e0b into a
#: fresh venv and run on the ``pi`` conversation profile
#: against the house Ollama (0.20.5) with the book's default
#: models: phi3:mini for chat, nomic-embed-text for embedding.
#: Method and every run live in
#: ``docs/architecture/E-047_PI_PROOF.md``.
#:
#: Ember's own startup on the Pi — process spawn to the
#: "is ready." line (interpreter, imports, config, Funi probe
#: of the real Ollama, Well open, history load) — the median
#: of three judged fresh ``ember ask`` processes (0.17–0.19 s).
#: This is the Ember-side re-anchor docket 90 asked E-047
#: for: against the flat 5.0 s cold-start cap it leaves ~28x
#: headroom, so the cap stands unrelaxed.
MEASURED_PI_READY_S = 0.18

#: First word of the reply on the Pi, median of the same
#: three runs (5.17–6.37 s): a REAL-model number — it prices
#: phi3:mini's prompt processing on the Pi's CPU, which is
#: the model's cost, never Ember's, and is therefore recorded
#: as an anchor but NOT judged against the cold-start cap
#: (the cap prices Ember's own startup with an instantly
#: answering wire-shape model, E-046). Stated so no reader
#: mistakes the two numbers for one another.
MEASURED_PI_FIRST_WORD_REAL_MODEL_S = 5.69

#: The Ember process's peak RSS across every Pi run, first
#: ever and judged alike: 27.1 MiB — inside even the
#: toaster's 64 MiB turn ceiling, let alone the pi
#: profile's 192 MiB. (Ollama's own runner held ~3.7 GiB
#: with phi3:mini loaded; that is the model's house, not
#: Ember's, and no Ember ceiling prices it.)
MEASURED_PI_PEAK_RSS_MIB = 27.1

#: What the installed core weighed on the Pi: the package
#: (1,684,679 B, device-generated bytecode caches included —
#: the VM anchor excludes them), its dist-info (91,535 B)
#: and sqlite-vec with its dist-info (175,294 B) —
#: 1,951,508 B in all, inside the pi profile's 8 MiB
#: install ceiling and the toaster's 2 MiB alike.
MEASURED_PI_INSTALLED_BYTES = 1_951_508

# --------------------------------------------------------------------- #
# Measured anchors (phone-class SIMULATION — E-048)                     #
# --------------------------------------------------------------------- #

#: **Proof grade: SIMULATED — no real phone is claimed.**
#: The house's real phone (a Galaxy S26 Ultra, paired) was
#: offline when checked, and the tree holds no Android
#: runtime or install path for the core, so E-048 ran the
#: phone conversation profile on the campaign VM under a
#: simulation envelope: each fresh ``ember ask`` process
#: pinned to 2 CPUs, a 512 MiB harness watchdog on its RSS
#: (the slice of a 2,048 MiB phone host left for the
#: companion's process after the OS and the smallest model
#: rung, E-041 §3 — an envelope, not a measurement of a
#: phone), and a loopback wire-shape model answering
#: instantly (the E-046 shape, so these numbers price
#: Ember's own startup and turn, never a model's thinking).
#: VM x86 cores are faster per core than phone silicon;
#: method and every run live in
#: ``docs/architecture/E-048_PHONE_PROOF.md``.
#:
#: Ember-side ready (spawn → "is ready.") at the median of
#: three judged fresh processes (1.47–2.99 s, heavily
#: contended VM, 1-minute load 6.0–7.6): 1.77 s.
MEASURED_PHONE_SIM_READY_S = 1.77

#: First word at the median of the same three runs
#: (1.49–3.01 s): 1.79 s — an Ember-side number against an
#: instantly answering wire-shape model, so unlike the Pi's
#: real-model first word it IS judged against the flat
#: 5.0 s cold-start cap, and fits. The first-ever run (Well
#: created) also fit: first word 3.92 s.
MEASURED_PHONE_SIM_FIRST_WORD_S = 1.79

#: The Ember process's peak RSS across every simulated run,
#: first ever and judged alike: 43.0 MiB — inside the phone
#: profile's 96 MiB idle and 128 MiB turn ceilings, and
#: 8.4% of the 512 MiB simulation envelope, which the
#: watchdog never had to enforce. Cross-process memory was
#: proven at the wire: each later process's request carried
#: the earlier exchanges (the recall run's prompt held the
#: first run's stated fact verbatim).
MEASURED_PHONE_SIM_PEAK_RSS_MIB = 43.0

# --------------------------------------------------------------------- #
# Measured anchors (Raspberry Pi 5, TOASTER profile — E-049)            #
# --------------------------------------------------------------------- #

#: **The Toaster Test (E-049).** The smallest honest target
#: the house can muster is the same named device as E-047 —
#: Mimir (``purpleviking1``), a Raspberry Pi 5 Model B
#: Rev 1.1 — because the house holds no smaller computer:
#: no Pi Zero-class board, and the paired phone/tablet were
#: offline (E-048). On that device Ember ran the
#: ``toaster`` conversation profile (history 512 tokens /
#: 3 episodes) end to end through the day-one flow — fresh
#: clean-venv install at c4c7cdc, fresh Well, real
#: embeddings — against the smallest real model rung the
#: house can serve: **qwen2.5:0.5b** (397 MB on disk),
#: pulled for this test, with nomic-embed-text for
#: embedding. Method and every run live in
#: ``docs/architecture/E-049_TOASTER_TEST.md``.
#:
#: Ember's own startup on the toaster profile — process
#: spawn to the "is ready." line — the median of three
#: judged fresh ``ember ask`` processes (0.20–0.28 s):
#: 0.21 s. This is the toaster-device re-anchor docket 90
#: asked E-049 for: against the flat 5.0 s cap it leaves
#: ~24x headroom, so the cap stands unrelaxed.
MEASURED_TOASTER_PI_READY_S = 0.21

#: First word of the reply on the toaster test, median of
#: the same three runs (1.15–2.55 s): a REAL-model number —
#: it prices qwen2.5:0.5b's prompt processing on the Pi's
#: CPU, the model's cost, never Ember's. It happens to sit
#: inside the 5.0 s cap (the 0.5B rung is fast); it is
#: still recorded as an anchor, NOT judged against the cap
#: — the cap prices Ember's own startup (the ready anchor
#: above), exactly as in E-047.
MEASURED_TOASTER_PI_FIRST_WORD_REAL_MODEL_S = 2.18

#: The Ember process's peak RSS across every toaster-test
#: run, first ever and judged alike: 27.2 MiB — inside the
#: toaster profile's own 64 MiB idle and turn ceilings
#: with more than 2x headroom.
MEASURED_TOASTER_PI_PEAK_RSS_MIB = 27.2

#: What the installed core weighed on the Pi at c4c7cdc:
#: the package (1,689,599 B, device-generated bytecode
#: caches included), its dist-info (91,535 B) and
#: sqlite-vec with its dist-info (175,294 B) — 1,956,428 B
#: in all, inside the toaster profile's 2 MiB install
#: ceiling.
MEASURED_TOASTER_PI_INSTALLED_BYTES = 1_956_428


def storage_bytes_per_turn() -> int:
    """The on-disk cost of one ordinary turn, in bytes.

    One Well episode plus its diary lines. The pending journal's
    per-episode file (741 B measured) is *transient* — it drains
    into the Well at the next connected session (E-031) — so it
    is not growth and is not counted here.
    """
    return WELL_BYTES_PER_EPISODE + DIARY_BYTES_PER_TURN


def projected_monthly_growth_mib(turns_per_day: int = REFERENCE_TURNS_PER_DAY) -> float:
    """Projected storage growth for a 30-day month of companionship."""
    return storage_bytes_per_turn() * turns_per_day * 30 / _MIB


# --------------------------------------------------------------------- #
# The book                                                              #
# --------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class ProfileBudget:
    """One profile's ceilings — the most the core may cost there.

    ``reference_host_ram_mib`` is the smallest host the profile
    is named for *in this book* (the toaster's 512 MiB is the
    Tiny Device Profile's Pi Zero 2 W target, E-015 §5; the
    others are this book's definitions, stated so the model
    ladder can be added honestly). It is context, not a ceiling
    on Ember: Ember's ceilings are the four cost fields.

    ``history_token_budget`` is not a second copy of E-021's
    numbers — it is read from the conversation config the
    profile actually runs with, so the book can never drift
    from the code it describes.
    """

    profile: ConversationProfile
    reference_host_ram_mib: int
    install_mib: float
    idle_ram_mib: float
    turn_ram_mib: float
    storage_growth_mib_per_month: float
    #: E-046: seconds from launching a fresh process to the
    #: first word of the companion's reply on the operator's
    #: screen. Flat across profiles on purpose: cold start is
    #: process startup (interpreter, imports, config, model
    #: probe, Well open), which E-046 measured as the same
    #: shape on the smallest profile — the profiles differ in
    #: what a turn may carry, not in what starting costs.
    cold_start_first_word_s: float = 5.0

    @property
    def history_token_budget(self) -> int:
        return ConversationConfig(profile=self.profile).resolved_token_budget

    @property
    def history_max_episodes(self) -> int:
        return ConversationConfig(profile=self.profile).resolved_max_episodes


_BUDGETS: dict[ConversationProfile, ProfileBudget] = {
    ConversationProfile.TOASTER: ProfileBudget(
        profile=ConversationProfile.TOASTER,
        reference_host_ram_mib=512,
        install_mib=2.0,
        idle_ram_mib=64.0,
        turn_ram_mib=64.0,
        storage_growth_mib_per_month=2.0,
    ),
    ConversationProfile.PHONE: ProfileBudget(
        profile=ConversationProfile.PHONE,
        reference_host_ram_mib=2048,
        install_mib=4.0,
        idle_ram_mib=96.0,
        turn_ram_mib=128.0,
        storage_growth_mib_per_month=10.0,
    ),
    ConversationProfile.PI: ProfileBudget(
        profile=ConversationProfile.PI,
        reference_host_ram_mib=4096,
        install_mib=8.0,
        idle_ram_mib=128.0,
        turn_ram_mib=192.0,
        storage_growth_mib_per_month=25.0,
    ),
    ConversationProfile.LAPTOP: ProfileBudget(
        profile=ConversationProfile.LAPTOP,
        reference_host_ram_mib=8192,
        install_mib=16.0,
        idle_ram_mib=256.0,
        turn_ram_mib=384.0,
        storage_growth_mib_per_month=100.0,
    ),
}

#: The profiles in smallest-first order — the book's spine.
PROFILE_ORDER: tuple[ConversationProfile, ...] = (
    ConversationProfile.TOASTER,
    ConversationProfile.PHONE,
    ConversationProfile.PI,
    ConversationProfile.LAPTOP,
)


def budget_for(profile: ConversationProfile) -> ProfileBudget:
    """The budget book's entry for one profile."""
    return _BUDGETS[profile]


def all_budgets() -> tuple[ProfileBudget, ...]:
    """Every profile's budget, smallest first."""
    return tuple(_BUDGETS[profile] for profile in PROFILE_ORDER)


def check_against(
    profile: ConversationProfile,
    *,
    install_mib: float,
    idle_ram_mib: float,
    turn_ram_mib: float,
    storage_growth_mib_per_month: float,
    cold_start_first_word_s: float | None = None,
) -> tuple[str, ...]:
    """Judge one measured shape against a profile's ceilings.

    Returns one plain sentence per ceiling the shape exceeds,
    empty when the shape fits. This is the judgement E-042's
    budget tests will call; keeping it beside the book means a
    test failure speaks in the book's own words.
    """
    budget = _BUDGETS[profile]
    problems: list[str] = []
    if install_mib > budget.install_mib:
        problems.append(
            f"install {install_mib:.2f} MiB exceeds the {profile.value} "
            f"ceiling of {budget.install_mib:.2f} MiB"
        )
    if idle_ram_mib > budget.idle_ram_mib:
        problems.append(
            f"idle RAM {idle_ram_mib:.1f} MiB exceeds the {profile.value} "
            f"ceiling of {budget.idle_ram_mib:.1f} MiB"
        )
    if turn_ram_mib > budget.turn_ram_mib:
        problems.append(
            f"turn RAM {turn_ram_mib:.1f} MiB exceeds the {profile.value} "
            f"ceiling of {budget.turn_ram_mib:.1f} MiB"
        )
    if storage_growth_mib_per_month > budget.storage_growth_mib_per_month:
        problems.append(
            f"storage growth {storage_growth_mib_per_month:.2f} MiB/month exceeds "
            f"the {profile.value} ceiling of "
            f"{budget.storage_growth_mib_per_month:.2f} MiB/month"
        )
    if (
        cold_start_first_word_s is not None
        and cold_start_first_word_s > budget.cold_start_first_word_s
    ):
        problems.append(
            f"cold start to first word {cold_start_first_word_s:.2f} s exceeds "
            f"the {profile.value} ceiling of "
            f"{budget.cold_start_first_word_s:.2f} s"
        )
    return tuple(problems)


def measured_shape_fits(profile: ConversationProfile) -> tuple[str, ...]:
    """Judge the E-041 measured anchors against one profile.

    Empty when the core as measured fits the profile — the
    book's founding fact, pinned by the E-041 tests.
    """
    return check_against(
        profile,
        install_mib=MEASURED_INSTALL_BYTES / _MIB,
        idle_ram_mib=MEASURED_IDLE_RAM_MIB,
        turn_ram_mib=MEASURED_TURN_RAM_MIB,
        storage_growth_mib_per_month=projected_monthly_growth_mib(),
        cold_start_first_word_s=MEASURED_COLD_START_FIRST_WORD_S,
    )


__all__ = [
    "DIARY_BYTES_PER_TURN",
    "MEASURED_COLD_START_FIRST_WORD_S",
    "MEASURED_IDLE_RAM_MIB",
    "MEASURED_INSTALL_BYTES",
    "MEASURED_TURN_RAM_MIB",
    "PROFILE_ORDER",
    "REFERENCE_TURNS_PER_DAY",
    "WELL_BYTES_PER_EPISODE",
    "ProfileBudget",
    "all_budgets",
    "budget_for",
    "check_against",
    "measured_shape_fits",
    "projected_monthly_growth_mib",
    "storage_bytes_per_turn",
]
