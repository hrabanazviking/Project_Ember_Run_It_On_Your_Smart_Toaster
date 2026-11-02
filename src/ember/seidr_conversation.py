"""Seiðr in conversation: what the engine offers a chat (E-112).

Roadmap line: "Seiðr in conversation: what the engine offers
a chat (draws, interpretations as *data*) — with the honesty
rule: the engine computes; meaning is the companion's voice,
labelled."

E-107 mapped the engine and stated its truth plainly: it
composes verse by rule from a word-hoard sorted into the
Nine Worlds — it does not think, divine, or interpret, and
it models no draws, no fate, and no question-and-answer
shape. E-110 made composition a typed service to the core.
This module is the conversation layer over that ground: it
states what a chat may honestly be offered, and offers
exactly that, as data:

- **A verse offer** — a poem composed through the E-110
  service, carried with the facts the engine computed
  (form, the world actually used, seed) and, on request,
  the Old Norse forms of the verse's own words, looked up
  in the member's lexicon as data. The elder design corpus
  asked for verse as a register seed for chat — tonal
  material the companion speaks *from*, never a reply
  pasted in the companion's place (the sibling sheet's own
  rule) — and a verse offer is that seed, labelled.
- **A draw** — a seeded handful of words drawn from one
  world of the lexicon, plus that world's kenning where
  the world holds one, each item as data (word, world,
  part of speech, syllables, its Old Norse form where the
  lexicon carries one). A draw here is a *drawing of
  words*, stated as exactly that: the engine has no fate
  model (E-107 §2), so no draw from this module claims
  one. A draw requires a seed, so the same draw can
  always be re-drawn and checked; an unseeded draw is
  refused in words, never silently made irreproducible.
- **A reading, attached and labelled** — interpretation
  enters only as the companion's own text, supplied by
  the caller and carried under its own label
  (:data:`MEANING_SOURCE`), in a separate field from the
  computed facts (:data:`COMPUTED_SOURCE`). The two are
  never merged, and this module writes no reading of its
  own: there is no function here that turns a verse or a
  draw into a claim about what it means.

The context shape a chat consumes is :func:`context_text`:
one labelled block that states, in the block itself, which
part the engine computed and that meaning — present only
when the companion has supplied one — is the companion's
voice. A theme a caller names rides on an offer as a
*label* only (docket 144, ruled in this slice): it is
carried verbatim, reported back, and never passed to
composition as a hint, because the composer takes none.

Docket 144's member-side fate is ruled in this slice and
recorded in the slice doc: the member's dead
``include_old_norse`` config field and its equally dead
``format()`` parameter are removed from the member (they
promised a rendering nothing ever produced; the true road
for Old Norse in conversation is data — the forms the
lexicon itself carries, served on draws and glosses here),
and ``topic`` stands corrected in the member to what it
always was: a label carried on the stanza, never a hint.

Not built here, named plainly: no persona gate decides
whether a given persona may draw on the engine (that is
E-117, off by default there); nothing is wired into the
live prompt assembly — this module defines the offer and
its labelled context shape, and a chat that adopts them
does so deliberately; no scheduler offers verse or draws
unasked.
"""

from __future__ import annotations

import importlib
import random
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from ember import engines

#: Where computed facts come from, as every offer labels
#: them: the engine computed these; they are data.
COMPUTED_SOURCE: str = "engine"

#: Where a reading comes from, as every reading is
#: labelled: the companion spoke this in its own voice;
#: the engine claims no meaning.
MEANING_SOURCE: str = "companion"

#: The honesty rule, stated once, carried into every
#: context block this module shapes.
HONESTY_LINE: str = (
    "The engine computes; meaning is the companion's "
    "voice, labelled as its own."
)

#: How many words a draw takes when the caller does not
#: say: three — a handful a chat can hold at once. A draw
#: may ask for 1 to 9 (one per world at most, by shape).
DEFAULT_DRAW_COUNT: int = 3
MAX_DRAW_COUNT: int = 9


def _load_lexicon(member_dir: Path):
    """The member's ``Lexicon`` class, loaded from its home.

    Mirrors the engines service's discipline: the member
    is loaded from its own directory in this monorepo,
    reached through the loaded package object, never by a
    core-level import of the member's package. Returns
    ``(lexicon_class, nine_worlds, problem)``.
    """
    if not (member_dir / "seidr" / "__init__.py").is_file():
        return None, None, (
            f"seidr member not found at {member_dir} — the "
            "conversation layer binds to the in-tree member "
            "(seidr_engine/ in this monorepo)"
        )
    path_entry = str(member_dir)
    if path_entry not in sys.path:
        sys.path.insert(0, path_entry)
    try:
        package = importlib.import_module("seidr")
        lexicon_mod = importlib.import_module("seidr.lexicon")
    except ImportError as exc:
        return None, None, f"seidr member at {member_dir} did not import: {exc}"
    return lexicon_mod.Lexicon, tuple(package.NINE_WORLDS), None


# ── The verse offer ─────────────────────────────────────


@dataclass(frozen=True, slots=True)
class VerseOffer:
    """A composed verse, offered to a conversation as data.

    Every field is the E-110 service's own output, carried.
    ``theme`` is the caller's label for why the verse was
    asked for — a label only (docket 144): it was never
    passed to composition and shaped nothing. ``glosses``
    is the Old Norse data for the verse's own words when
    the caller asked for it: ``(word, old_norse)`` pairs in
    the order the words first appear, looked up in the
    member's lexicon (the verse's own world first); words
    the lexicon carries no form for — the connectors,
    above all — are absent, and ``glossed``/``words_seen``
    state the coverage as counted, never rounded up.
    """

    form: str
    world: str | None
    lines: tuple[str, ...]
    text: str
    stanzas: int
    seed: int | None
    theme: str | None
    glosses: tuple[tuple[str, str], ...]
    glossed: int
    words_seen: int
    source: str = COMPUTED_SOURCE


@dataclass(frozen=True, slots=True)
class VerseOfferResult:
    """Either a :class:`VerseOffer` or a plain refusal."""

    offer: VerseOffer | None
    reason: str | None

    @classmethod
    def served(cls, offer: VerseOffer) -> VerseOfferResult:
        return cls(offer=offer, reason=None)

    @classmethod
    def refused(cls, reason: str) -> VerseOfferResult:
        return cls(offer=None, reason=reason)


_TOKEN = re.compile(r"[^\W\d_]+(?:-[^\W\d_]+)*", re.UNICODE)


def _glosses_for(
    lines: tuple[str, ...], world: str | None, lexicon
) -> tuple[tuple[tuple[str, str], ...], int, int]:
    """Old Norse forms for a verse's words, as data.

    A pure lookup over the member's lexicon: each distinct
    word-token of the verse, in first-appearance order,
    matched case-insensitively against the lexicon's
    entries (the verse's own world first, then every
    world). Returns ``(pairs, glossed, seen)`` where
    ``seen`` counts distinct tokens and ``glossed`` those
    the lexicon carries a form for.
    """
    by_word: dict[str, str] = {}

    def _index(entries) -> None:
        for entry in entries:
            if entry.old_norse:
                by_word.setdefault(entry.word.lower(), entry.old_norse)

    if world:
        _index(lexicon.get_words(domain=world))
    _index(lexicon.get_words())
    pairs: list[tuple[str, str]] = []
    seen: set[str] = set()
    for line in lines:
        for token in _TOKEN.findall(line):
            key = token.lower()
            if key in seen:
                continue
            seen.add(key)
            if key in by_word:
                pairs.append((token, by_word[key]))
    return tuple(pairs), len(pairs), len(seen)


def offer_verse(
    *,
    form: str = "fornyrthislag",
    world: str | None = None,
    stanzas: int = 1,
    seed: int | None = None,
    theme: str | None = None,
    with_old_norse: bool = False,
    member_dir: Path | None = None,
) -> VerseOfferResult:
    """Compose a verse for a conversation, through E-110.

    The composition is the service's, untouched: a service
    refusal is returned verbatim and no offer is built.
    ``theme`` rides as a label only (docket 144). With
    ``with_old_norse`` the offer also carries the verse's
    Old Norse glosses as data, with their coverage counted.
    """
    member = engines.default_seidr_member_dir() if member_dir is None else member_dir
    result = engines.compose_verse(
        engines.VerseRequest(
            form=form, world=world, stanzas=stanzas, seed=seed),
        member_dir=member,
    )
    if result.verse is None:
        return VerseOfferResult.refused(result.reason or "seidr service refused")
    verse = result.verse
    glosses: tuple[tuple[str, str], ...] = ()
    glossed = words_seen = 0
    if with_old_norse:
        lexicon_cls, _worlds, problem = _load_lexicon(member)
        if problem is not None:
            return VerseOfferResult.refused(problem)
        glosses, glossed, words_seen = _glosses_for(
            verse.lines, verse.world, lexicon_cls())
    return VerseOfferResult.served(
        VerseOffer(
            form=verse.form,
            world=verse.world,
            lines=verse.lines,
            text=verse.text,
            stanzas=verse.stanzas,
            seed=verse.seed,
            theme=theme,
            glosses=glosses,
            glossed=glossed,
            words_seen=words_seen,
        )
    )


# ── The draw ────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class DrawnWord:
    """One drawn word, as data — the lexicon's own entry."""

    word: str
    world: str
    part_of_speech: str
    syllables: int
    old_norse: str | None


@dataclass(frozen=True, slots=True)
class DrawnKenning:
    """One drawn kenning, as data — the lexicon's own entry."""

    expression: str
    base: str
    world: str


@dataclass(frozen=True, slots=True)
class Draw:
    """A seeded drawing of words from one world, as data.

    A draw is a drawing of *words*: these entries, from
    this world, under this seed — re-drawable and checkable
    by anyone. It carries no fate, no answer, and no
    reading; what it might mean in a conversation is the
    companion's voice, attached separately or not at all.
    ``kenning`` is ``None`` where the drawn world holds no
    kenning (five of the nine hold none, E-107 §3) — the
    absence is stated, never filled from another world.
    """

    words: tuple[DrawnWord, ...]
    kenning: DrawnKenning | None
    world: str
    seed: int
    theme: str | None
    source: str = COMPUTED_SOURCE


@dataclass(frozen=True, slots=True)
class DrawResult:
    """Either a :class:`Draw` or a plain refusal ``reason``."""

    draw: Draw | None
    reason: str | None

    @classmethod
    def served(cls, draw: Draw) -> DrawResult:
        return cls(draw=draw, reason=None)

    @classmethod
    def refused(cls, reason: str) -> DrawResult:
        return cls(draw=None, reason=reason)


def draw_words(
    *,
    seed: int | None,
    world: str | None = None,
    count: int = DEFAULT_DRAW_COUNT,
    theme: str | None = None,
    member_dir: Path | None = None,
) -> DrawResult:
    """Draw words from one world of the lexicon, seeded.

    A seed is required: a conversation draw must be
    re-drawable to be checkable, so an unseeded request is
    refused in words. An unchosen world is picked by the
    seed itself (deterministically, from the nine) and the
    draw reports the world actually drawn from. Words are
    distinct within a draw; the kenning is the drawn
    world's own or honestly absent.
    """
    if seed is None:
        return DrawResult.refused(
            "seidr conversation: a draw needs a seed, so the "
            "same draw can always be drawn again and checked "
            "— an unseeded draw is not offered"
        )
    if not 1 <= count <= MAX_DRAW_COUNT:
        return DrawResult.refused(
            f"seidr conversation: a draw takes 1 to "
            f"{MAX_DRAW_COUNT} words"
        )
    member = engines.default_seidr_member_dir() if member_dir is None else member_dir
    lexicon_cls, worlds, problem = _load_lexicon(member)
    if problem is not None:
        return DrawResult.refused(problem)
    assert worlds is not None
    if world is not None and world not in worlds:
        return DrawResult.refused(
            f"seidr conversation: unknown world {world!r} — "
            "the engine's worlds are " + ", ".join(worlds)
        )
    chosen = world if world is not None else random.Random(seed).choice(list(worlds))
    lexicon = lexicon_cls(seed=seed)
    drawn: list[DrawnWord] = []
    seen: set[str] = set()
    attempts = 0
    while len(drawn) < count and attempts < count * 20:
        attempts += 1
        entry = lexicon.random_word(domain=chosen)
        if entry is None or entry.word.lower() in seen:
            continue
        seen.add(entry.word.lower())
        drawn.append(
            DrawnWord(
                word=entry.word,
                world=entry.domain,
                part_of_speech=entry.part_of_speech,
                syllables=entry.syllables,
                old_norse=entry.old_norse,
            )
        )
    if len(drawn) < count:
        return DrawResult.refused(
            f"seidr conversation: the world {chosen!r} could "
            f"not yield {count} distinct words"
        )
    kenning = lexicon.random_kenning(domain=chosen)
    return DrawResult.served(
        Draw(
            words=tuple(drawn),
            kenning=(
                DrawnKenning(
                    expression=kenning.expression,
                    base=kenning.base,
                    world=kenning.domain,
                )
                if kenning is not None
                else None
            ),
            world=chosen,
            seed=seed,
            theme=theme,
        )
    )


# ── Readings: the companion's voice, labelled ───────────


@dataclass(frozen=True, slots=True)
class Reading:
    """A computed offer plus the companion's own reading.

    The two halves never merge: ``computed`` is the
    engine's data under :data:`COMPUTED_SOURCE`;
    ``reading`` is text the companion supplied, carried
    verbatim under :data:`MEANING_SOURCE`. This module
    writes no reading; it only keeps the labels straight.
    """

    computed: VerseOffer | Draw
    reading: str
    reading_source: str = MEANING_SOURCE


def attach_reading(computed: VerseOffer | Draw, reading: str) -> Reading:
    """Attach the companion's own reading to computed data.

    The reading is carried verbatim and labelled as the
    companion's voice. An empty reading is a caller error,
    raised plainly — an empty label would dress silence up
    as speech.
    """
    if not reading or not reading.strip():
        raise ValueError(
            "a reading must be the companion's own words — "
            "an empty reading attaches nothing and labels nothing"
        )
    return Reading(computed=computed, reading=reading)


# ── The context shape a chat consumes ───────────────────


def context_text(item: VerseOffer | Draw | Reading) -> str:
    """The labelled context block a conversation consumes.

    One block, honest in its own text: a header naming the
    computed part as the engine's data, the data itself,
    and a closing section that either carries the
    companion's reading under its own label or states that
    none has been spoken — the engine offers none. Verse
    arrives as register seed (the elder corpus's shape):
    material to speak from, labelled as computed, never
    presented as the companion's reply.
    """
    reading: str | None = None
    computed: VerseOffer | Draw = item
    if isinstance(item, Reading):
        computed = item.computed
        reading = item.reading
    lines = ["Seiðr in this conversation — computed by the engine, as data:"]
    if isinstance(computed, VerseOffer):
        lines.append(
            f"Verse ({computed.form}, world: {computed.world}, "
            f"stanzas: {computed.stanzas}, seed: {computed.seed}):"
        )
        lines.extend(computed.lines)
        if computed.theme is not None:
            lines.append(f"Asked under the label: {computed.theme}")
        if computed.glosses:
            lines.append(
                "Old Norse forms of the verse's words "
                f"({computed.glossed} of {computed.words_seen} "
                "distinct words carry one):"
            )
            lines.extend(f"  {w} — {on}" for w, on in computed.glosses)
    else:
        lines.append(
            f"Draw (world: {computed.world}, seed: {computed.seed}, "
            f"{len(computed.words)} words):"
        )
        for word in computed.words:
            gloss = f" — {word.old_norse}" if word.old_norse else ""
            lines.append(f"  {word.word} ({word.part_of_speech}){gloss}")
        if computed.kenning is not None:
            lines.append(
                f"Kenning drawn: {computed.kenning.expression} "
                f"(for {computed.kenning.base})"
            )
        else:
            lines.append(
                f"No kenning drawn: the world {computed.world} "
                "holds none."
            )
        if computed.theme is not None:
            lines.append(f"Asked under the label: {computed.theme}")
    lines.append(HONESTY_LINE)
    if reading is not None:
        lines.append(f"The companion's reading, in its own voice: {reading}")
    else:
        lines.append(
            "No reading has been spoken: the engine offers "
            "none, and any meaning is the companion's to "
            "speak, in its own voice."
        )
    return "\n".join(lines)


__all__ = [
    "COMPUTED_SOURCE",
    "DEFAULT_DRAW_COUNT",
    "HONESTY_LINE",
    "MAX_DRAW_COUNT",
    "MEANING_SOURCE",
    "Draw",
    "DrawResult",
    "DrawnKenning",
    "DrawnWord",
    "Reading",
    "VerseOffer",
    "VerseOfferResult",
    "attach_reading",
    "context_text",
    "draw_words",
    "offer_verse",
]
