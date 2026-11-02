"""E-107 — Seiðr engine mapped.

Pins ``docs/architecture/E-107_SEIDR_ENGINE_MAPPED.md``
and, behind it, the member's measured shape at this
tree:

* the record itself: the plain-words verdict (a
  rule-based verse composer; no consumers today),
  the measured lexicon and forms, and dockets
  142-147 each with its Part VII owner;
* the member's standing size: the 11 tracked files
  and their 103,728 B total (the E-057 row);
* the lexicon derived from the code: 337 entries
  in the nine worlds plus connectors, 28 kennings,
  282 entries carrying an Old Norse form;
* the forms: 6 registry keys for 4 forms, their
  syllable ranges, and each form's composed line
  count;
* seeded composition byte-identical across two
  skalds (the determinism E-113 will hold);
* the consumer claim: no file under ``src/``
  mentions the engine at all;
* docket 142's shape, probed: in a ljodhattr
  stanza the flattened lines append both full
  lines after all pair lines (E-110 re-pins this
  probe when it fixes the order at the source);
* docket 143's shape, probed: an unknown world
  name composes silently instead of refusing
  (E-120 / E-110 re-pin when the refusal lands);
* the one refusal the library does make: an
  unknown form raises ``ValueError``.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "docs" / "architecture" / "E-107_SEIDR_ENGINE_MAPPED.md"
MEMBER = REPO / "seidr_engine"

sys.path.insert(0, str(MEMBER))

from seidr.forms import FORMS, get_form  # noqa: E402
from seidr.lexicon import Lexicon  # noqa: E402
from seidr.poet import PoemConfig, Skald  # noqa: E402

TRACKED = (
    "LICENSE",
    "README.md",
    "pyproject.toml",
    "seidr/__init__.py",
    "seidr/__main__.py",
    "seidr/cli.py",
    "seidr/forms.py",
    "seidr/lexicon.py",
    "seidr/poet.py",
    "tests/__init__.py",
    "tests/test_seidr.py",
)

PER_DOMAIN = {
    "asgard": 42, "vanaheim": 34, "alfheim": 27,
    "midgard": 45, "jotunheim": 31, "svartalfheim": 26,
    "niflheim": 25, "muspelheim": 24, "helheim": 28,
    "connectors": 55,
}


def _flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


# ── The record, on file ─────────────────────────────────


def test_doc_records_the_map_verdict():
    text = _flat(DOC)
    for needle in ("it composes Old-Norse-flavoured English verse by rule",
                   "It has no consumers today",
                   "337 word entries",
                   "28 kennings",
                   "282 of 337",
                   "11 tracked files, 103,728 B",
                   "38 passed, 0 failed",
                   "Next: E-108"):
        assert needle in text, needle


def test_doc_names_dockets_and_owners():
    text = _flat(DOC)
    for needle in ("Docket 142", "Docket 143", "Docket 144",
                   "Docket 145", "Docket 146", "Docket 147",
                   "E-110", "E-120", "E-112", "E-119", "E-113"):
        assert needle in text, needle


# ── The member's measured shape ─────────────────────────


def test_tracked_member_files_and_size_stand():
    total = 0
    for rel in TRACKED:
        path = MEMBER / rel
        assert path.is_file(), rel
        total += path.stat().st_size
    assert total == 103728


def test_lexicon_counts_derived_from_code():
    lex = Lexicon(seed=1)
    assert {d: len(w) for d, w in lex.words.items()} == PER_DOMAIN
    assert sum(PER_DOMAIN.values()) == 337
    assert len(lex.kennings) == 28
    with_on = sum(1 for ws in lex.words.values() for w in ws if w.old_norse)
    assert with_on == 282


def test_forms_registry_and_ranges():
    assert sorted(FORMS) == ["drottkvaett", "fornyrdislag",
                             "fornyrthislag", "ljodahattr",
                             "ljodhattr", "malahattr"]
    assert get_form("fornyrthislag").syllable_range() == (4, 6)
    assert get_form("ljodhattr").syllable_range() == (4, 6)
    assert get_form("drottkvaett").syllable_range() == (5, 7)
    assert get_form("malahattr").syllable_range() == (5, 8)


def test_composed_line_counts_per_form():
    expected = {"fornyrthislag": 4, "ljodhattr": 6,
                "drottkvaett": 8, "malahattr": 8}
    for form, count in expected.items():
        stanza = Skald(seed=42).compose(
            PoemConfig(form=form, seed=42))
        assert stanza.form == form
        assert len(stanza.lines) == count, form


def test_seeded_composition_is_reproducible():
    def poem() -> str:
        return Skald(seed=123).compose_poem(
            PoemConfig(form="fornyrthislag", seed=123)).format()

    assert poem() == poem()


def test_no_consumer_in_the_core():
    offenders = []
    for path in (REPO / "src").rglob("*.py"):
        if "seidr" in path.read_text(
                encoding="utf-8", errors="replace").lower():
            offenders.append(str(path.relative_to(REPO)))
    assert offenders == [], offenders


# ── The docketed shapes, probed ─────────────────────────


def test_docket_142_ljodhattr_full_lines_appended_last():
    stanza = Skald(seed=42).compose(
        PoemConfig(form="ljodhattr", seed=42))
    assert len(stanza.full_lines) == 2
    assert stanza.lines[-2:] == list(stanza.full_lines)
    rendered = str(stanza)
    second_pair_last = stanza.half_stanzas[1].lines[1].text
    assert rendered.index(stanza.full_lines[0].text) > \
        rendered.index(second_pair_last)


def test_docket_143_unknown_world_composes_silently():
    stanza = Skald(seed=42).compose(PoemConfig(
        form="fornyrthislag", domain="nosuchworld", seed=42))
    assert stanza.domain == "nosuchworld"
    assert len(stanza.lines) == 4


def test_unknown_form_raises():
    import pytest

    with pytest.raises(ValueError):
        Skald(seed=1).compose(PoemConfig(form="nope", seed=1))
