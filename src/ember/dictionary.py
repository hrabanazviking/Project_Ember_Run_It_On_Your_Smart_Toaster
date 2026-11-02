"""The dictionary binding: Cleasby-Vigfusson as a lookup
service for the companion (E-115).

Roadmap line: "The dictionary binding: cleasby-vigfusson
as a lookup service for the companion (Old Norse words in
conversation, answered from the real dictionary)."

The monorepo's dictionary member
(``cleasby-vigfusson-old-norse-dict/``) is a Next.js web
frontend for the Cleasby & Vigfusson Old Norse dictionary
(1874, public domain). It was mapped by the census (E-002)
but never bound: nothing in the companion could ask it
what a word means. Worse, measured at this slice, the
member as tracked cannot answer either — every page and
API route imports a service layer (``lib/services/…``,
``lib/utils/…``) that is **not in the tracked tree at
all**, and the dictionary text itself is not tracked
either: it lives in the member's pinned npm data package
(``cleasby-vigfusson-dictionary``, ``^1.0.16`` in the
member's ``package.json``), which an install of the
member would fetch into its ``node_modules/``. Both
findings are docketed to E-116 (dictionary data hygiene),
whose road they are; this slice binds what honestly
exists — the real dictionary data, in the shape the
member's own pages consume it — and refuses in plain
words wherever it does not.

The shape, in plain words:

- **Typed requests and results, E-110's discipline.**
  :func:`lookup_word` → :class:`LookupResult` and
  :func:`search_dictionary` → :class:`SearchResult`;
  every result carries either its entries or a plain
  ``reason`` — never both — and no failure of the data
  road ever raises out of this module or is dressed up
  as an answer.
- **Answered from the real dictionary.** An entry is the
  dictionary's own record — headword and definitions
  exactly as the data package prints them, in dictionary
  order. Nothing is paraphrased, modernised, translated
  further, or invented here: where the dictionary carries
  a word, its own words are the answer; where it does
  not, the result says so in words (a miss is a served
  answer with zero entries and a ``note``, not a refusal
  and never a fabricated entry).
- **Homographs are all served.** The dictionary carries
  458 headwords (counted case-insensitively) with more
  than one entry — *seiðr* the fish and *SEIÐR* the
  magic stand side by side. A lookup returns every exact
  match, in the dictionary's own order, and never picks
  a winner the dictionary did not pick.
- **Matching is case-insensitive and character-exact.**
  Headwords compare folded to lowercase, and nothing
  else is normalised: *maðr* finds ``MAÐR``, and *madr*
  finds nothing, because the dictionary's alphabet is
  not the ASCII one — silently folding ð to d would
  answer a different word's question. Search is the
  member's own criteria shape (its search form's three
  roads: ``headword``, ``definitions``, ``all`` =
  both), substring matching, capped at the member's own
  150-result cap (its ``src/pages/api/search.ts``).
- **The data road is stated, and refuses honestly.**
  The one source this binding reads is the data
  package's no-markup JSON
  (``json/cleasby-vigfusson-no-markup.json`` — the plain
  text flavour, because a conversation is spoken, not
  rendered; the markup flavour stays the web member's).
  :func:`default_dictionary_data_path` names where an
  installed member keeps it (its ``node_modules/``);
  a caller may point the binding at the file directly.
  Absent, unreadable, or malformed data is a refusal
  naming the path — the E-110 ephemeris discipline:
  refuse before answering, never fabricate.
- **Provenance travels with the answer.** Every served
  entry and the conversation block name their source
  (:data:`SOURCE`): the 1874 dictionary, through the
  member's pinned data package. The dictionary speaks
  in its own voice; the companion's voice is its own —
  the E-112 honesty rule, applied to a book.
- **Fully local, and priced honestly.** The binding is
  standard library only, reads one file, writes nothing,
  and never touches the network. The price is real and
  is measured in the slice doc: the data file is
  10,656,938 bytes and holding the whole book in memory
  is a laptop-shaped cost, not a toaster one — the
  binding loads lazily, once per data path, and says so.

Not built here, named plainly: no correction of the
dictionary's data (OCR errors, duplicates, provenance
audit — E-116's road, with the member's missing service
layer); no letter browsing, similar-words, abbreviations
or crosslinks (the web member's shapes, whose service
layer is the missing one); no persona gate on who may
ask (E-117); nothing wired into the live prompt assembly
— a chat adopts :func:`answer_text` deliberately, as
with E-112's offers.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Final

#: The dictionary binding contract version (E-037's
#: member discipline, kin to the engines contract).
CONTRACT_VERSION: Final[str] = "1.0"

#: The data package the member pins (its package.json:
#: ``cleasby-vigfusson-dictionary: ^1.0.16``) and the
#: version this binding was measured against.
DATA_PACKAGE: Final[str] = "cleasby-vigfusson-dictionary"
DATA_PACKAGE_VERSION: Final[str] = "1.0.16"

#: Where every served entry comes from, as answers label
#: it: the dictionary's own voice, never the companion's
#: invention.
SOURCE: Final[str] = (
    "Cleasby & Vigfusson, An Icelandic-English Dictionary "
    "(1874), via the cleasby-vigfusson-dictionary data "
    "package (no-markup text)"
)

#: The search criteria the member's own search form
#: offers (its SearchForm: Everything / Headwords /
#: Definitions), as this binding serves them.
CRITERIA: Final[tuple[str, ...]] = ("headword", "definitions", "all")

#: The member's own result cap (its search API slices
#: anything longer to 150).
MAX_RESULTS: Final[int] = 150

#: The data file's name inside the data package.
_DATA_FILE: Final[str] = "cleasby-vigfusson-no-markup.json"


def _repo_root() -> Path:
    """The monorepo root of this clone (``src/ember`` → up 3)."""
    return Path(__file__).resolve().parents[2]


def default_member_dir() -> Path:
    """The in-tree dictionary member this binding serves."""
    return _repo_root() / "cleasby-vigfusson-old-norse-dict"


def default_dictionary_data_path() -> Path:
    """Where an installed member keeps the dictionary data.

    The member's ``package.json`` pins the data package;
    an install places it in the member's ``node_modules/``
    and the package keeps the book at ``json/`` under its
    root. Until the member is installed that path does not
    exist, and every request through it refuses plainly.
    """
    return (
        default_member_dir()
        / "node_modules"
        / DATA_PACKAGE
        / "json"
        / _DATA_FILE
    )


def _resolve_data_path(data_path: Path | None) -> Path:
    if data_path is not None:
        return data_path
    env = os.environ.get("EMBER_DICTIONARY_DATA")
    if env:
        return Path(env)
    return default_dictionary_data_path()


# ── Entries, as the dictionary prints them ──────────────


@dataclass(frozen=True, slots=True)
class Entry:
    """One dictionary entry, exactly as the data prints it.

    ``word`` is the headword in the dictionary's own
    casing (it prints some headwords in capitals);
    ``definitions`` are its definition texts, verbatim,
    in the dictionary's order.
    """

    word: str
    definitions: tuple[str, ...]
    source: str = SOURCE


@dataclass(frozen=True, slots=True)
class LookupResult:
    """Every exact entry for a headword, or a refusal.

    A served result with ``entries == ()`` is the
    dictionary's honest miss: ``note`` states it. A
    refusal (``reason`` set) means no answer was possible
    at all — the data road itself failed.
    """

    entries: tuple[Entry, ...] | None
    reason: str | None
    note: str | None = None

    @classmethod
    def served(cls, entries: tuple[Entry, ...], note: str | None = None) -> LookupResult:
        return cls(entries=entries, reason=None, note=note)

    @classmethod
    def refused(cls, reason: str) -> LookupResult:
        return cls(entries=None, reason=reason)


@dataclass(frozen=True, slots=True)
class SearchResult:
    """Entries matching a search, or a refusal.

    ``total`` counts every match before the cap, so a
    capped answer never pretends to be the whole field;
    ``capped`` says the cap was reached.
    """

    entries: tuple[Entry, ...] | None
    reason: str | None
    total: int = 0
    capped: bool = False

    @classmethod
    def served(
        cls, entries: tuple[Entry, ...], total: int, capped: bool
    ) -> SearchResult:
        return cls(entries=entries, reason=None, total=total, capped=capped)

    @classmethod
    def refused(cls, reason: str) -> SearchResult:
        return cls(entries=None, reason=reason)


# ── The data road ───────────────────────────────────────

_BOOKS: dict[str, tuple[Entry, ...]] = {}
_INDEXES: dict[str, dict[str, tuple[Entry, ...]]] = {}


def _index_for(
    data_path: Path, book: tuple[Entry, ...]
) -> dict[str, tuple[Entry, ...]]:
    """The headword index for a loaded book, built once.

    Keyed by lowercased headword, each value every entry
    under that headword in dictionary order — a lookup is
    then one dict read, not a scan of the whole book.
    """
    cached = _INDEXES.get(str(data_path))
    if cached is not None:
        return cached
    index: dict[str, list[Entry]] = {}
    for entry in book:
        index.setdefault(entry.word.lower(), []).append(entry)
    built = {key: tuple(value) for key, value in index.items()}
    _INDEXES[str(data_path)] = built
    return built


def _load_book(data_path: Path) -> tuple[tuple[Entry, ...] | None, str | None]:
    """Load and shape-check the dictionary data, once per path.

    The shape is the member's own (its pages consume
    ``{word, definitions}`` records): a JSON list of
    objects with a string headword and a list of string
    definitions. Anything else is refused as malformed —
    a differently-shaped file is not this dictionary,
    and guessing at it would fabricate entries.
    """
    cached = _BOOKS.get(str(data_path))
    if cached is not None:
        return cached, None
    if not data_path.is_file():
        return None, (
            f"dictionary data not found at {data_path} — the "
            "binding reads the real Cleasby-Vigfusson data "
            f"from the member's pinned data package "
            f"({DATA_PACKAGE} {DATA_PACKAGE_VERSION}, the "
            "no-markup JSON); install the member or point "
            "the binding at that file"
        )
    try:
        raw = json.loads(data_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, (
            f"dictionary data at {data_path} could not be "
            f"read as JSON: {type(exc).__name__}: {exc}"
        )
    if not isinstance(raw, list):
        return None, (
            f"dictionary data at {data_path} is not the "
            "dictionary's shape (a list of entries) — no "
            "lookup is served from a differently-shaped file"
        )
    entries: list[Entry] = []
    for i, item in enumerate(raw):
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("word"), str)
            or not isinstance(item.get("definitions"), list)
            or not all(isinstance(d, str) for d in item["definitions"])
        ):
            return None, (
                f"dictionary data at {data_path} is not the "
                f"dictionary's shape (entry {i} is not a "
                "headword with definition texts) — no lookup "
                "is served from a differently-shaped file"
            )
        entries.append(
            Entry(word=item["word"], definitions=tuple(item["definitions"])))
    book = tuple(entries)
    _BOOKS[str(data_path)] = book
    return book, None


def dictionary_available(data_path: Path | None = None) -> bool:
    """True when the real dictionary data can be read."""
    book, problem = _load_book(_resolve_data_path(data_path))
    return problem is None and book is not None


def entry_count(data_path: Path | None = None) -> int | None:
    """How many entries the loaded book carries, or None."""
    book, problem = _load_book(_resolve_data_path(data_path))
    if problem is not None:
        return None
    assert book is not None
    return len(book)


# ── Lookup: one word, answered from the book ────────────


def lookup_word(
    word: str, *, data_path: Path | None = None
) -> LookupResult:
    """Every dictionary entry for one headword, exactly.

    Case-insensitive, character-exact (see the module
    docstring): all homographs are served in dictionary
    order. A word the dictionary does not carry is a
    served miss with a stated note — never a refusal,
    never a near-miss dressed as the answer.
    """
    if not word or not word.strip():
        return LookupResult.refused(
            "dictionary lookup: a lookup needs a word"
        )
    path = _resolve_data_path(data_path)
    book, problem = _load_book(path)
    if problem is not None:
        return LookupResult.refused(problem)
    assert book is not None
    wanted = word.strip().lower()
    hits = _index_for(path, book).get(wanted, ())
    if not hits:
        return LookupResult.served(
            (),
            note=(
                f"the dictionary carries no headword "
                f"{word.strip()!r} — matching is exact, and "
                "the dictionary's own letters (ð, þ, ö and "
                "the long vowels) are not folded to plain ones"
            ),
        )
    return LookupResult.served(hits)


def search_dictionary(
    query: str,
    *,
    criteria: str = "all",
    limit: int = MAX_RESULTS,
    data_path: Path | None = None,
) -> SearchResult:
    """Search the dictionary by the member's own criteria.

    ``headword`` matches the query inside headwords,
    ``definitions`` inside definition texts, ``all``
    either — substring, case-insensitive, in dictionary
    order, capped at ``limit`` (the member's own cap is
    :data:`MAX_RESULTS`) with the true total counted.
    """
    if criteria not in CRITERIA:
        return SearchResult.refused(
            f"dictionary search: unknown criteria "
            f"{criteria!r} — the dictionary's roads are "
            + ", ".join(CRITERIA)
        )
    if not query or not query.strip():
        return SearchResult.refused(
            "dictionary search: a search needs a word or phrase"
        )
    if limit < 1:
        return SearchResult.refused(
            "dictionary search: a search returns at least one entry"
        )
    book, problem = _load_book(_resolve_data_path(data_path))
    if problem is not None:
        return SearchResult.refused(problem)
    assert book is not None
    needle = query.strip().lower()

    def matches(entry: Entry) -> bool:
        if criteria in ("headword", "all") and needle in entry.word.lower():
            return True
        if criteria in ("definitions", "all"):
            return any(needle in d.lower() for d in entry.definitions)
        return False

    hits = [e for e in book if matches(e)]
    total = len(hits)
    return SearchResult.served(
        tuple(hits[:limit]), total=total, capped=total > limit)


# ── The conversation shape ──────────────────────────────


def answer_text(result: LookupResult, *, asked: str) -> str:
    """The labelled block a conversation consumes.

    One block, honest in its own text: the word asked
    for, the dictionary's entries under the dictionary's
    name, and a closing line stating the source — the
    dictionary's words are quoted, never spoken as the
    companion's own knowledge. A refusal or a miss is
    stated in the same block, in plain words.
    """
    if result.reason is not None:
        return (
            f"The dictionary cannot answer for {asked!r}: "
            f"{result.reason}"
        )
    assert result.entries is not None
    if not result.entries:
        return (
            f"The dictionary has no entry for {asked!r}: "
            f"{result.note}"
        )
    lines = [f"From the dictionary — {SOURCE}:"]
    for entry in result.entries:
        lines.append(entry.word)
        for i, definition in enumerate(entry.definitions, 1):
            if len(entry.definitions) > 1:
                lines.append(f"  {i}. {definition}")
            else:
                lines.append(f"  {definition}")
    lines.append(
        "These are the dictionary's own words, quoted — "
        "what they mean for this conversation is the "
        "companion's to say, in its own voice."
    )
    return "\n".join(lines)


__all__ = [
    "CONTRACT_VERSION",
    "CRITERIA",
    "DATA_PACKAGE",
    "DATA_PACKAGE_VERSION",
    "MAX_RESULTS",
    "SOURCE",
    "Entry",
    "LookupResult",
    "SearchResult",
    "answer_text",
    "default_dictionary_data_path",
    "default_member_dir",
    "dictionary_available",
    "entry_count",
    "lookup_word",
    "search_dictionary",
]
