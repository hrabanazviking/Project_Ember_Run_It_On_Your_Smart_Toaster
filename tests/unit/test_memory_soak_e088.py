"""E-088 — Long-life soak: a simulated year of memory.

Proves docs/architecture/E-088_LONG_LIFE_SOAK.md:

* the year anchors in ``ember.budgets`` are the measured
  record of the soak script's run (365 days x 20 turns =
  7,300 turns, 365 daily facts + 12 supersessions, the
  real face on the toaster profile, monthly restarts,
  stores weighed closed) — pinned exactly;
* the year fits every profile's twelve-month storage
  allowance, and every month's growth fits the toaster's
  monthly ceiling (the monthly curve is pinned too);
* the diary judgement: 365 files / 685,105 B — the
  one-file-per-day shape stands (E-082's open question);
* a live mini-soak (30 days through the face, a
  supersession, a restart) re-proves the counts the
  year's inspect showed;
* year-aged decay: a fact backdated ~a year is floored
  to importance 1 by one pass and is STILL current and
  still served — decay fades, it never deletes
  (docket 113's honesty at year scale);
* the cadence probe, live: two decay passes over a
  fact aged 60 days in all end LOWER than one pass at
  the same total age — passes compound (docket 125).

The year's acceleration was timestamp placement only:
episodes carried simulated dates, and fact timestamps
were set to their simulated days. The small fixtures
here backdate through the member handle's own
connection — the same fixture technique, stated here
so no reader mistakes it for a product path.

Synthetic canon-shaped data only (E-089's law, early).
Skips honestly without the sqlite_vec extra (Run D
supplies it), like the E-080..E-087 files it joins.
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "docs" / "architecture" / "E-088_LONG_LIFE_SOAK.md"

pytest.importorskip("sqlite_vec")

sys.path.insert(0, str(REPO / "mimir-well" / "src"))

from ember.budgets import (  # noqa: E402
    MEASURED_YEAR_BRUNNR_BYTES,
    MEASURED_YEAR_DIARY_BYTES,
    MEASURED_YEAR_DIARY_FILES,
    MEASURED_YEAR_FACTS_STORED,
    MEASURED_YEAR_MIMIR_BYTES,
    MEASURED_YEAR_SIDECAR_BYTES,
    MEASURED_YEAR_TOTAL_BYTES,
    MEASURED_YEAR_TURNS,
    PROFILE_ORDER,
    budget_for,
)
from ember.schemas.config import (  # noqa: E402
    BrunnrConfig,
    ConversationProfile,
    SqliteVecConfig,
)
from ember.schemas.episode import Episode  # noqa: E402
from ember.well.brunnr.sqlite_vec import open as sv_open  # noqa: E402
from ember.well.memory_face import MemoryFace  # noqa: E402
from mimir_well.core import RunaMemory  # noqa: E402

_MIB = 1024 * 1024
_TOASTER = ConversationProfile.TOASTER
PERSONA = "mabel"

_VOCAB = [
    "ferry", "letters", "islands", "dawn", "harbour",
    "beekeeper", "honey", "hives", "orchard", "winter",
    "market", "teaches", "song", "children", "river",
]


def embed(text: str) -> tuple[float, ...]:
    words = [w.strip(".,?!").lower() for w in text.split()]
    return tuple(float(words.count(v)) for v in _VOCAB)


DIM = len(_VOCAB)

#: The soak's monthly curve: every store weighed with
#: the face closed, month totals (Brunnr + mimir-well +
#: sidecar + diary), from the run's results.json.
MONTH_TOTALS = (
    814_849, 1_213_538, 1_664_433, 2_096_687, 2_543_486,
    3_000_316, 3_455_307, 3_910_298, 4_350_744, 4_805_735,
    5_270_757, 5_725_748,
)

FERRY = ("The harbour ferry leaves at dawn carrying letters "
         "between the islands.")


def _open_face(tmp_path: Path) -> MemoryFace:
    handle = sv_open(BrunnrConfig(
        embedding_dim=DIM,
        sqlite_vec=SqliteVecConfig(path=tmp_path / "brunnr.db")))
    mimir = RunaMemory(db_path=str(tmp_path / "mimir_well.db"))
    return MemoryFace(
        brunnr=handle, mimir=mimir, mimir_state="live",
        profile=_TOASTER, embedder=embed,
        sidecar_path=tmp_path / "sidecar.json")


def _backdate(face: MemoryFace, fact_id: int, days: float) -> None:
    """Fixture acceleration: set one fact's timestamp
    ``days`` into the past, through the member handle's
    own connection (the soak script did the same at
    month boundaries on the closed fixture file)."""
    stamp = (datetime.now() - timedelta(days=days)).isoformat()
    conn = face._mimir._get_conn()
    conn.execute("UPDATE memories SET timestamp = ? WHERE id = ?",
                 (stamp, fact_id))
    face._mimir._commit()


# --------------------------------------------------------------------- #
# The year anchors — the measured record, pinned                        #
# --------------------------------------------------------------------- #


def test_year_anchors_are_the_measured_record():
    assert MEASURED_YEAR_TURNS == 7_300
    assert MEASURED_YEAR_FACTS_STORED == 377  # 365 current + 12 old
    assert MEASURED_YEAR_BRUNNR_BYTES == 4_366_336
    assert MEASURED_YEAR_MIMIR_BYTES == 528_384
    assert MEASURED_YEAR_SIDECAR_BYTES == 137_731
    assert MEASURED_YEAR_DIARY_BYTES == 685_105
    assert MEASURED_YEAR_DIARY_FILES == 365
    assert MEASURED_YEAR_TOTAL_BYTES == 5_717_556
    assert MEASURED_YEAR_TOTAL_BYTES == (
        MEASURED_YEAR_BRUNNR_BYTES + MEASURED_YEAR_MIMIR_BYTES
        + MEASURED_YEAR_SIDECAR_BYTES + MEASURED_YEAR_DIARY_BYTES)


def test_year_fits_every_profiles_twelve_month_allowance():
    year_mib = MEASURED_YEAR_TOTAL_BYTES / _MIB
    assert year_mib < 5.5  # the whole year is under 5.5 MiB
    for profile in PROFILE_ORDER:
        allowance = (budget_for(profile).storage_growth_mib_per_month
                     * 12)
        assert year_mib < allowance, profile
    # On the toaster the headroom is better than 4x.
    toaster_year = budget_for(_TOASTER).storage_growth_mib_per_month * 12
    assert year_mib < toaster_year / 4


def test_every_months_growth_fits_the_toaster_ceiling():
    ceiling = int(
        budget_for(_TOASTER).storage_growth_mib_per_month * _MIB)
    increments = [MONTH_TOTALS[0]] + [
        b - a for a, b in zip(MONTH_TOTALS, MONTH_TOTALS[1:])]
    assert len(increments) == 12
    assert all(0 < inc < ceiling for inc in increments)
    # Steady months (2..12) averaged ~446 KB — the doc's
    # 446,445 B figure, recomputed from the pinned curve.
    steady = (MONTH_TOTALS[-1] - MONTH_TOTALS[0]) / 11
    assert abs(steady - 446_445) < 1.0


def test_diary_year_shape_stands_judged():
    # E-082's open question, answered by measurement:
    # one file per day for a year is 365 files and
    # under 0.7 MiB — a non-issue on the smallest
    # profile, so no diary lifecycle is built.
    assert MEASURED_YEAR_DIARY_FILES == 365
    assert MEASURED_YEAR_DIARY_BYTES < _MIB
    per_day = MEASURED_YEAR_DIARY_BYTES / MEASURED_YEAR_DIARY_FILES
    assert 1_800 < per_day < 1_950


def test_sidecar_growth_is_priced_per_turn():
    per_turn = MEASURED_YEAR_SIDECAR_BYTES / MEASURED_YEAR_TURNS
    assert 15 < per_turn < 22  # ~19 B per turn tag, linear


# --------------------------------------------------------------------- #
# Live mini-soak — a month through the face, then a restart             #
# --------------------------------------------------------------------- #


def test_mini_soak_a_month_through_the_face(tmp_path):
    face = _open_face(tmp_path)
    first_fact = None
    turn = 0
    for day in range(30):
        for _ in range(20):
            ep_id = face.add_turn(Episode(
                operator_input=f"turn {turn} " + "word " * 40,
                ember_reply="reply " * 40,
                funi_model="fake:tiny", persona_id=PERSONA))
            assert ep_id is not None
            turn += 1
        res = face.remember_fact(
            f"Day {day + 1} note: {FERRY}", importance=6,
            persona_id=PERSONA)
        assert res.fact_id and res.fact_id > 0
        if first_fact is None:
            first_fact = res.fact_id
    sup = face.supersede_fact(first_fact, FERRY + " (corrected)",
                              persona_id=PERSONA)
    assert sup.fact_id and sup.fact_id > 0

    seen = face.inspect_memory(persona_id=PERSONA)
    assert len(seen["turns"]) == 600
    assert len(seen["facts"]) == 30
    assert len(seen["old_facts"]) == 1
    assert face.lifecycle_report().facts_stored == 31
    recent = face.recent_turns(limit=5, persona_id=PERSONA)
    assert recent[-1].operator_input.startswith("turn 599 ")
    face.close()

    # A restart later, the month is still all there.
    face = _open_face(tmp_path)
    seen = face.inspect_memory(persona_id=PERSONA)
    assert len(seen["turns"]) == 600
    assert len(seen["facts"]) == 30
    assert len(seen["old_facts"]) == 1
    face.close()


# --------------------------------------------------------------------- #
# Year-aged decay — faded, never deleted                                #
# --------------------------------------------------------------------- #


def test_year_aged_fact_floors_but_survives(tmp_path):
    face = _open_face(tmp_path)
    old = face.remember_fact(FERRY, importance=6, persona_id=PERSONA)
    fresh = face.remember_fact(
        "The beekeeper keeps nine hives behind the orchard.",
        importance=6, persona_id=PERSONA)
    _backdate(face, old.fact_id, 360)
    _backdate(face, fresh.fact_id, 10)

    result = face.run_decay(persona_id=PERSONA)
    assert result["pruned"] >= 1  # the member's word: floored

    aged = face.inspect_fact(old.fact_id, persona_id=PERSONA)
    assert aged is not None and aged["is_current"]
    assert aged["importance"] == 1  # floored, not deleted
    recent = face.inspect_fact(fresh.fact_id, persona_id=PERSONA)
    # 6 x 0.5^(10/30) = 4.76 -> 5: a ten-day-old fact
    # has barely faded — the curve at the other end.
    assert recent["importance"] == 5
    # Both still served by word search after the pass.
    hits = face.recall_facts_word("ferry", persona_id=PERSONA)
    assert [h["content"] for h in hits] == [FERRY]
    assert len(face.inspect_memory(persona_id=PERSONA)["facts"]) == 2
    face.close()


# --------------------------------------------------------------------- #
# The cadence probe — passes compound (docket 125)                      #
# --------------------------------------------------------------------- #


def test_decay_passes_compound_docket_125(tmp_path):
    mem = RunaMemory(db_path=str(tmp_path / "cadence.db"))

    def age(fact_id: int, days: float) -> None:
        stamp = (datetime.now() - timedelta(days=days)).isoformat()
        conn = mem._get_conn()
        conn.execute(
            "UPDATE memories SET timestamp = ? WHERE id = ?",
            (stamp, fact_id))
        mem._commit()

    two = mem.add_memory("Cadence probe fact, two passes.",
                         importance=10, user_id=PERSONA)
    age(two, 30)
    mem.decay(half_life_days=30.0, user_id=PERSONA)
    assert mem.get_memory(two, user_id=PERSONA)["importance"] == 5
    age(two, 60)
    mem.decay(half_life_days=30.0, user_id=PERSONA)
    two_final = mem.get_memory(two, user_id=PERSONA)["importance"]

    one = mem.add_memory("Cadence probe fact, one pass.",
                         importance=10, user_id=PERSONA)
    age(one, 60)
    mem.decay(half_life_days=30.0, user_id=PERSONA)
    one_final = mem.get_memory(one, user_id=PERSONA)["importance"]
    mem.close()

    # The measured divergence, pinned as measured:
    # one pass at 60 days is the curve as stated (2);
    # two passes over the same total age end lower (1).
    assert one_final == 2
    assert two_final == 1
    assert two_final < one_final


# --------------------------------------------------------------------- #
# The doc                                                                 #
# --------------------------------------------------------------------- #


def test_doc_delivers_the_soak_and_its_finding():
    text = DOC.read_text(encoding="utf-8")
    for needle in ("5,717,556", "7,300", "365", "446,445",
                   "docket 125", "docket 113", "NOT MEASURED",
                   "1519 passed"):
        assert needle in text, needle


def test_soak_battery_is_wired_into_the_gate():
    assert Path(__file__).parent.name == "unit"
