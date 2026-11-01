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

# --------------------------------------------------------------------- #
# Measured anchors (a simulated month of companionship — E-050)         #
# --------------------------------------------------------------------- #

#: **Storage growth, measured at month scale (E-050).** A
#: simulated month of companionship — 30 days × 20 turns at
#: the book's reference workload, E-041's typical-turn
#: fixture (~40 words a side) — was run against the real
#: stores on the VM: the real sqlite_vec Well at the
#: production embedding dimension (768; episode rows carry
#: text only, so the dimension does not price episodes) and
#: the real diary in chat's connected shape (one session a
#: day; start + memory-connected + end lines, two lines per
#: turn). The Well was closed and weighed after every day;
#: growth was linear in 4 KiB page steps with no superlinear
#: component, and retrieval still worked at day 30. The
#: same Well then grew to 3,000 episodes for the steady
#: marginal. Method and the full curve live in
#: ``docs/architecture/E-050_STORAGE_GROWTH.md``.
#:
#: The Well's growth over the 600-episode month: 352,256 B
#: (587.1 B/episode averaged over the month; the file stood
#: at 434,176 B from an 81,920 B empty schema).
MEASURED_MONTH_WELL_GROWTH_BYTES = 352_256

#: The diary's growth over the same month: 56,310 B across
#: 30 daily files — 93.85 B/turn all-in (85 B/turn marginal:
#: the two per-turn lines; the rest is one header + three
#: session lines per day).
MEASURED_MONTH_DIARY_BYTES = 56_310

#: The whole month's growth, both stores: 408,566 B
#: (0.39 MiB) over 600 turns — 680.9 B/turn all-in, inside
#: the book's 694 B/turn statement, which therefore stands
#: unrevised (docket 91, closed at E-050: E-042's 808 B/turn
#: was 30-episode page rounding plus a different diary
#: session shape, not the month's truth).
MEASURED_MONTH_TOTAL_BYTES = 408_566

#: Turns in the simulated month (30 days × the reference
#: 20 turns/day).
MEASURED_MONTH_TURNS = 600

#: The Well's steady-state marginal cost per episode,
#: measured over episodes 600–3,000 of the same store:
#: 585.4 B — flat, so a heavier month costs the same per
#: turn as the reference month.
MEASURED_WELL_STEADY_BYTES_PER_EPISODE = 585.4

#: The long-turn cost: 60 essay turns (~500 words a side)
#: in a fresh Well cost 6,144 B/episode at that scale. A
#: month of essay-length turns at the reference rate
#: (3.51 MiB) exceeds the toaster's storage ceiling and
#: fits the phone's — the book's ceilings price typical
#: turns, as E-041 §4 already stated; E-082's lifecycle
#: rules own the long-turn store.
MEASURED_ESSAY_BYTES_PER_EPISODE = 6_144


# --------------------------------------------------------------------- #
# Measured anchors (a simulated year of memory — E-088)                 #
# --------------------------------------------------------------------- #

#: **The long-life soak, measured (E-088).** A simulated
#: year of companionship — 365 days x 20 turns (7,300
#: turns, the book's reference workload, E-041's typical
#: fixture) plus one living fact a day (365, with 12
#: monthly supersessions) — was run through the real
#: memory face (E-080) on the TOASTER profile against the
#: real stores, with monthly restarts, monthly growth
#: accounting, the real diary in chat's connected shape,
#: and one full lifecycle pass at year end. Acceleration
#: was timestamp placement only (episodes carry simulated
#: dates; fact timestamps were set to their simulated
#: days), never skipped writes. Method and the monthly
#: curve live in
#: ``docs/architecture/E-088_LONG_LIFE_SOAK.md``.
#:
#: The whole year's growth, every store weighed closed:
#: Brunnr 4,366,336 B + mimir-well 528,384 B + the face's
#: sidecar 137,731 B + the diary 685,105 B = 5,717,556 B
#: (5.45 MiB) — inside every profile's twelve-month
#: allowance, the toaster's 24 MiB included, with ~4.4x
#: headroom. Steady monthly growth (months 2-12) averaged
#: 446,445 B (~0.43 MiB), under the toaster's 2 MiB
#: monthly ceiling in every single month.
MEASURED_YEAR_TOTAL_BYTES = 5_717_556

#: Turns in the simulated year (365 days x 20/day).
MEASURED_YEAR_TURNS = 7_300

#: Living-fact rows after the year: 365 still current
#: plus the 12 superseded versions kept as history.
MEASURED_YEAR_FACTS_STORED = 377

#: The Brunnr store's closed size after the year: 7,300
#: episodes at a measured 591 B/episode all-in (the
#: E-050 steady marginal was 585.4 B — the soak's figure
#: carries the same store at year scale).
MEASURED_YEAR_BRUNNR_BYTES = 4_366_336

#: The mimir-well store's closed size after the year:
#: 377 fact rows plus its audit trail. The member's fixed
#: schema (~266 KB on day one) dominates; growth over the
#: year was ~718 B per fact row, beside E-078's 745 B
#: anchor.
MEASURED_YEAR_MIMIR_BYTES = 528_384

#: The memory face's sidecar after the year: one persona
#: tag per turn plus the fact bookkeeping — 137,731 B,
#: ~19 B per turn. A real growth the E-050 month (which
#: predates the face) did not price; now priced.
MEASURED_YEAR_SIDECAR_BYTES = 137_731

#: The diary after the year: 365 daily files, 685,105 B
#: in all (~1,877 B a day). E-082 left the
#: one-file-per-day shape to this soak to judge: at year
#: scale the file count is a non-issue and the bytes are
#: trivial — the shape stands, no lifecycle action.
MEASURED_YEAR_DIARY_BYTES = 685_105
MEASURED_YEAR_DIARY_FILES = 365


# --------------------------------------------------------------------- #
# Measured anchors (update weight — E-052)                              #
# --------------------------------------------------------------------- #

#: **Update weight, measured (E-052).** An update of the
#: core is a wheel: the package tree deflated. Weighed on
#: the VM with ``ember.updates``' own functions on the
#: final tree of the E-052 slice (this module's anchors
#: included): the download — the wheel shape built in
#: memory, entries sorted, deflate level 9 — is 293,387 B
#: (~0.28 MiB), and the package it unpacks to weighs
#: 775,675 B installed (bytecode caches excluded, the
#: book's standing rule). Method and the per-profile
#: table live in
#: ``docs/architecture/E-052_UPDATE_WEIGHT.md``.
MEASURED_UPDATE_DOWNLOAD_BYTES = 293_387

#: The installed weight of the package tree the update
#: carries, measured the same way at the same moment.
MEASURED_UPDATE_INSTALLED_BYTES = 775_675

#: Peak disk while applying: the wheel still on disk, the
#: new package unpacked beside the old, the old not yet
#: removed — download + 2 × installed, the formula
#: ``ember.updates.UpdateCost`` states. 1,844,737 B
#: (~1.76 MiB): inside every profile's room many times
#: over, and the download itself fits every profile's
#: download ceiling (its install ceiling, read from this
#: book) — the toaster's 2 MiB ceiling with ~7x headroom.
MEASURED_UPDATE_APPLY_PEAK_BYTES = 1_844_737


# --------------------------------------------------------------------- #
# Measured anchors (battery drain shape — E-053)                        #
# --------------------------------------------------------------------- #

#: **Battery-shaped behaviour, measured as its cause (E-053).**
#: No battery device in the house can run Ember today (the
#: paired phone was offline at E-048 and the tree holds no
#: phone runtime), so a real battery's drain — percent per
#: hour — is NOT PROVEN and is claimed nowhere. What this
#: slice measured on the campaign VM is the drain's *cause*:
#: the CPU duty of bulk background work, shaped and
#: unshaped, run back to back under the same (heavy,
#: sibling-campaign) contention. The probe's unit of work
#: is 0.25 s of process CPU; the job shape is the embedding
#: client's (the duty hook consulted between batches only);
#: rests are the real ``time.sleep``. Method and both runs
#: live in ``docs/architecture/E-053_BATTERY_BEHAVIOUR.md``.
#:
#: Process CPU spent across one single blocking 5 s rest
#: (the CONSERVE rest): **0.000 s** (second run: 0.0001 s) —
#: the no-busy-wait fact, measured: a rest is one blocking
#: sleep, and the CPU is not woken to poll the clock.
MEASURED_BATTERY_REST_CPU_S = 0.0

#: CPU-over-wall fraction of an unshaped (FULL) background
#: job, 16 work units: 4.001 s of CPU over 9.719 s of wall
#: — **0.4117**. Below 1.0 because the contended VM
#: deschedules the process, neighbours included; the
#: fraction's use is comparative, against the CONSERVE run
#: beside it, not as a claim about any quiet machine.
MEASURED_DUTY_FULL_CPU_FRACTION = 0.4117

#: CPU-over-wall fraction of the same job duty-cycled at
#: CONSERVE (40% charge shape: bursts of 4 batches, one
#: 5 s rest between), 12 work units: 3.001 s of CPU over
#: 15.921 s of wall — **0.1885**, less than half the FULL
#: run's fraction under the same contention, with exactly
#: 2 rests totalling 10.0 s. Counted over work + rest only
#: (contention excluded), CONSERVE's imposed duty is
#: 3.001 / 13.001 ≈ 23% against FULL's 100%.
MEASURED_DUTY_CONSERVE_CPU_FRACTION = 0.1885


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
    "MEASURED_BATTERY_REST_CPU_S",
    "MEASURED_COLD_START_FIRST_WORD_S",
    "MEASURED_DUTY_CONSERVE_CPU_FRACTION",
    "MEASURED_DUTY_FULL_CPU_FRACTION",
    "MEASURED_ESSAY_BYTES_PER_EPISODE",
    "MEASURED_IDLE_RAM_MIB",
    "MEASURED_INSTALL_BYTES",
    "MEASURED_MONTH_DIARY_BYTES",
    "MEASURED_MONTH_TOTAL_BYTES",
    "MEASURED_MONTH_TURNS",
    "MEASURED_MONTH_WELL_GROWTH_BYTES",
    "MEASURED_TURN_RAM_MIB",
    "MEASURED_UPDATE_APPLY_PEAK_BYTES",
    "MEASURED_UPDATE_DOWNLOAD_BYTES",
    "MEASURED_UPDATE_INSTALLED_BYTES",
    "MEASURED_WELL_STEADY_BYTES_PER_EPISODE",
    "MEASURED_YEAR_BRUNNR_BYTES",
    "MEASURED_YEAR_DIARY_BYTES",
    "MEASURED_YEAR_DIARY_FILES",
    "MEASURED_YEAR_FACTS_STORED",
    "MEASURED_YEAR_MIMIR_BYTES",
    "MEASURED_YEAR_SIDECAR_BYTES",
    "MEASURED_YEAR_TOTAL_BYTES",
    "MEASURED_YEAR_TURNS",
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
