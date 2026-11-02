"""E-115 — The dictionary binding: Cleasby-Vigfusson as a
lookup service for the companion.

Pins ``docs/architecture/E-115_DICTIONARY_BINDING.md``:

* the binding's contract shape — typed results that carry
  an answer or a plain reason, never both; a miss is a
  served answer with a stated note, never a fabrication;
* the member as found: its tracked tree carries no
  service layer (``src/lib`` is absent from
  ``git ls-files`` though every page imports it) and no
  dictionary data — the data lives in the member's
  pinned npm package, whose pin this battery re-reads
  from the member's own ``package.json``;
* behaviour proven on a small synthetic book in the
  dictionary's own shape (exact lookup, homographs in
  dictionary order, case-insensitive matching with no
  letter folding, the member's three search criteria,
  its 150 cap with the true total counted, malformed
  data refused by shape);
* the real book, where the campaign's isolated copy of
  the data package's no-markup JSON is present (the
  live shape): entry and definition counts as measured
  at the slice, pinned headwords answered verbatim, and
  the recorded carrying-in and memory prices as printed
  in the slice doc (measurements pinned as printed,
  judgements re-derived live against ``ember.budgets``).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "docs" / "architecture" / "E-115_DICTIONARY_BINDING.md"
MEMBER = REPO / "cleasby-vigfusson-old-norse-dict"

sys.path.insert(0, str(REPO / "src"))

import ember.budgets as budgets  # noqa: E402
from ember import dictionary  # noqa: E402

#: The campaign's isolated copy of the real data (the
#: data package's no-markup JSON, fetched at the slice —
#: the E-108 isolated-deps discipline). Absent → the
#: live-shape tests skip honestly.
LIVE_DATA = (
    Path.home()
    / "workspace" / ".verify-tmp" / "ember-e115"
    / "cleasby-vigfusson-no-markup.json"
)
live = pytest.mark.skipif(
    not LIVE_DATA.is_file(),
    reason="the isolated real dictionary data is not present",
)

# Recorded measurements at the slice (E-115 doc).
LIVE_ENTRIES = 35_207
LIVE_DEFINITIONS = 46_162
LIVE_HOMOGRAPH_KEYS = 458
LIVE_DATA_BYTES = 10_656_938
LOADED_PEAK_MIB = 59.7

_MIB = 1024 * 1024

#: A tiny book in the dictionary's own shape — synthetic
#: headwords only, no real history in any definition.
SYNTHETIC = [
    {"word": "HRAFN", "definitions": ["m. a raven.", "m. a banner name."]},
    {"word": "hrafn", "definitions": ["a later spelling, same bird."]},
    {"word": "seiðr", "definitions": ["m. a kind of fish."]},
    {"word": "SEIÐR", "definitions": ["m. magic, a spell."]},
    {"word": "askr", "definitions": ["m. an ash tree; the first man."]},
]


@pytest.fixture()
def book(tmp_path: Path) -> Path:
    path = tmp_path / "book.json"
    path.write_text(json.dumps(SYNTHETIC), encoding="utf-8")
    return path


# ── The member as found ─────────────────────────────────


def test_member_pins_the_data_package_this_binding_reads() -> None:
    package = json.loads((MEMBER / "package.json").read_text(encoding="utf-8"))
    pin = package["dependencies"][dictionary.DATA_PACKAGE]
    assert pin == f"^{dictionary.DATA_PACKAGE_VERSION}"


def test_member_service_layer_is_absent_from_the_tracked_tree() -> None:
    out = subprocess.run(
        ["git", "-C", str(REPO), "ls-files", "-z", "--",
         "cleasby-vigfusson-old-norse-dict/src"],
        capture_output=True, check=True,
    ).stdout.decode()
    tracked = [name for name in out.split("\0") if name]
    assert tracked  # the member's pages and components are tracked
    assert not any("/src/lib/" in name for name in tracked)
    # …while its own pages import that missing layer.
    word_page = (MEMBER / "src" / "pages" / "word" / "[word].tsx").read_text(
        encoding="utf-8")
    assert "lib/services/dictionary" in word_page


def test_default_data_path_is_the_members_own_install_shape() -> None:
    path = dictionary.default_dictionary_data_path()
    assert path.name == "cleasby-vigfusson-no-markup.json"
    assert path.parent.name == "json"
    assert path.parent.parent.name == dictionary.DATA_PACKAGE
    assert path.parent.parent.parent.name == "node_modules"
    assert path.parent.parent.parent.parent == dictionary.default_member_dir()


# ── Refusals: the data road fails honestly ──────────────


def test_absent_data_refuses_in_words_naming_the_path(tmp_path: Path) -> None:
    missing = tmp_path / "nope.json"
    result = dictionary.lookup_word("hrafn", data_path=missing)
    assert result.entries is None
    assert result.reason is not None
    assert str(missing) in result.reason
    assert dictionary.DATA_PACKAGE in result.reason
    assert dictionary.dictionary_available(missing) is False
    assert dictionary.entry_count(missing) is None


def test_default_shape_refuses_while_the_member_is_uninstalled() -> None:
    if dictionary.default_dictionary_data_path().is_file():
        pytest.skip("the member is installed in this tree — live shape")
    result = dictionary.lookup_word("hrafn")
    assert result.entries is None
    assert result.reason is not None


def test_malformed_data_is_refused_by_shape(tmp_path: Path) -> None:
    not_json = tmp_path / "bad.json"
    not_json.write_text("this is not json", encoding="utf-8")
    result = dictionary.lookup_word("hrafn", data_path=not_json)
    assert result.entries is None
    assert "could not be read as JSON" in (result.reason or "")

    wrong_shape = tmp_path / "wrong.json"
    wrong_shape.write_text(json.dumps({"word": "hrafn"}), encoding="utf-8")
    result = dictionary.lookup_word("hrafn", data_path=wrong_shape)
    assert result.entries is None
    assert "not the dictionary's shape" in (result.reason or "")

    wrong_entry = tmp_path / "wrong2.json"
    wrong_entry.write_text(
        json.dumps([{"word": "hrafn", "definitions": "a raven"}]),
        encoding="utf-8")
    result = dictionary.lookup_word("hrafn", data_path=wrong_entry)
    assert result.entries is None
    assert "entry 0" in (result.reason or "")


def test_blank_requests_are_refused(book: Path) -> None:
    assert dictionary.lookup_word("  ", data_path=book).reason
    assert dictionary.search_dictionary("", data_path=book).reason
    assert dictionary.search_dictionary(
        "hrafn", criteria="bogus", data_path=book).reason
    assert dictionary.search_dictionary(
        "hrafn", limit=0, data_path=book).reason


# ── Lookup: the dictionary's own words ──────────────────


def test_exact_lookup_serves_every_homograph_in_order(book: Path) -> None:
    result = dictionary.lookup_word("seiðr", data_path=book)
    assert result.reason is None
    assert result.entries is not None
    assert [e.word for e in result.entries] == ["seiðr", "SEIÐR"]
    assert result.entries[0].definitions == ("m. a kind of fish.",)
    assert result.entries[1].definitions == ("m. magic, a spell.",)
    assert all(e.source == dictionary.SOURCE for e in result.entries)


def test_lookup_is_case_insensitive_and_exact(book: Path) -> None:
    for asked in ("HRAFN", "hrafn", "Hrafn"):
        result = dictionary.lookup_word(asked, data_path=book)
        assert result.entries is not None
        assert [e.word for e in result.entries] == ["HRAFN", "hrafn"]


def test_lookup_does_not_fold_the_dictionarys_letters(book: Path) -> None:
    # 'seidr' with a plain d is a different string from
    # 'seiðr' — the binding answers the word asked about,
    # never a neighbour dressed as it.
    result = dictionary.lookup_word("seidr", data_path=book)
    assert result.entries == ()
    assert result.reason is None
    assert result.note is not None and "no headword" in result.note


def test_a_miss_is_a_served_answer_not_a_refusal(book: Path) -> None:
    result = dictionary.lookup_word("wyrd", data_path=book)
    assert result.entries == ()
    assert result.reason is None
    assert dictionary.entry_count(book) == len(SYNTHETIC)
    assert dictionary.dictionary_available(book) is True


# ── Search: the member's own criteria ───────────────────


def test_search_criteria_and_dictionary_order(book: Path) -> None:
    by_head = dictionary.search_dictionary(
        "hrafn", criteria="headword", data_path=book)
    assert [e.word for e in (by_head.entries or ())] == ["HRAFN", "hrafn"]
    by_def = dictionary.search_dictionary(
        "raven", criteria="definitions", data_path=book)
    assert [e.word for e in (by_def.entries or ())] == ["HRAFN"]
    everything = dictionary.search_dictionary(
        "raven", criteria="all", data_path=book)
    assert [e.word for e in (everything.entries or ())] == ["HRAFN"]
    # 'all' also reaches headwords the definitions road misses.
    everything = dictionary.search_dictionary(
        "askr", criteria="all", data_path=book)
    assert [e.word for e in (everything.entries or ())] == ["askr"]


def test_search_counts_the_total_and_caps_like_the_member(book: Path) -> None:
    result = dictionary.search_dictionary(
        "m.", criteria="definitions", limit=2, data_path=book)
    assert result.total == 4
    assert result.capped is True
    assert len(result.entries or ()) == 2
    assert dictionary.MAX_RESULTS == 150  # the member's own cap


# ── The conversation shape ──────────────────────────────


def test_answer_text_quotes_the_dictionary_under_its_name(book: Path) -> None:
    text = dictionary.answer_text(
        dictionary.lookup_word("seiðr", data_path=book), asked="seiðr")
    assert dictionary.SOURCE in text
    assert "m. a kind of fish." in text
    assert "m. magic, a spell." in text
    assert "the dictionary's own words, quoted" in text


def test_answer_text_states_a_miss_and_a_refusal_plainly(
    book: Path, tmp_path: Path
) -> None:
    miss = dictionary.answer_text(
        dictionary.lookup_word("wyrd", data_path=book), asked="wyrd")
    assert "no entry for 'wyrd'" in miss
    refused = dictionary.answer_text(
        dictionary.lookup_word("hrafn", data_path=tmp_path / "gone.json"),
        asked="hrafn")
    assert "cannot answer for 'hrafn'" in refused


def test_doc_carries_the_binding_shape() -> None:
    text = DOC.read_text(encoding="utf-8")
    for needle in (
        "35,207",
        "10,656,938",
        "59.7 MiB",
        "src/lib",
        "E-116",
        "docket 160",
        "docket 161",
    ):
        assert needle in text, needle


# ── The real book (live shape) ──────────────────────────


@live
def test_real_book_counts_as_measured() -> None:
    assert dictionary.entry_count(LIVE_DATA) == LIVE_ENTRIES
    book = json.loads(LIVE_DATA.read_text(encoding="utf-8"))
    assert sum(len(e["definitions"]) for e in book) == LIVE_DEFINITIONS
    from collections import Counter

    counts = Counter(e["word"].lower() for e in book)
    homographs = sum(1 for n in counts.values() if n > 1)
    assert homographs == LIVE_HOMOGRAPH_KEYS
    assert LIVE_DATA.stat().st_size == LIVE_DATA_BYTES


@live
def test_real_headwords_answered_verbatim() -> None:
    result = dictionary.lookup_word("maðr", data_path=LIVE_DATA)
    assert result.entries is not None and len(result.entries) == 1
    entry = result.entries[0]
    assert entry.word == "MAÐR"
    assert len(entry.definitions) == 10
    assert entry.definitions[0].startswith("m., qs. mann-r")

    result = dictionary.lookup_word("seiðr", data_path=LIVE_DATA)
    assert result.entries is not None
    assert [e.word for e in result.entries] == ["seiðr", "SEIÐR"]
    assert "gadus virens" in result.entries[0].definitions[0]
    assert "gen. seiðar" in result.entries[1].definitions[0]

    # Diacritic-exact: the ASCII neighbour is a miss.
    assert dictionary.lookup_word("madr", data_path=LIVE_DATA).entries == ()


@live
def test_real_searches() -> None:
    result = dictionary.search_dictionary(
        "witchcraft", criteria="definitions", data_path=LIVE_DATA)
    assert result.total == 26
    assert (result.entries or ())[0].word == "BRAGÐ"
    capped = dictionary.search_dictionary(
        "maðr", criteria="headword", data_path=LIVE_DATA)
    assert capped.total == 503
    assert capped.capped is True
    assert len(capped.entries or ()) == dictionary.MAX_RESULTS


@live
def test_prices_as_printed_against_live_ceilings() -> None:
    # Carrying-in: the data file alone fits only the
    # laptop's install ceiling (budgets re-derived live).
    fits = [
        b.profile.value for b in budgets.all_budgets()
        if LIVE_DATA_BYTES <= b.install_mib * _MIB
    ]
    assert fits == ["laptop"]
    # In use: the loaded book's measured peak sits inside
    # every profile's turn ceiling — the toaster's only
    # just (93% of it), as the doc states in those words.
    toaster = budgets.budget_for(budgets.ConversationProfile.TOASTER)
    assert LOADED_PEAK_MIB < toaster.turn_ram_mib
    assert LOADED_PEAK_MIB / toaster.turn_ram_mib > 0.9
