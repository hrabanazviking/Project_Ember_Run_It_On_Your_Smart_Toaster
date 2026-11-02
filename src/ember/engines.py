"""The engines as services to the core (E-110).

Roadmap line: "The engines as services to the core: typed
requests/responses under the member contract (E-037's kin)."

Part VII's two soul-organs — the seiðr verse engine
(``seidr_engine/``) and the astrology engine
(``astrology-engine/``) — were mapped at E-107/E-108 with no
consumers in the companion at all: each could be reached only
through its own command line, one printing verse, the other
printing a box-drawn chart, neither returning data a program
could hold. This module is the first real consumer, and the
contract it binds under is E-037's member discipline: bind
through a stated surface, check shapes before computing,
refuse in plain words with a typed reason, and never let a
member's failure shape leak into the companion as a fabricated
answer.

The shape, in plain words:

- **Typed requests and responses.** :class:`VerseRequest` →
  :class:`Verse`; :class:`ChartRequest` → :class:`Chart`.
  Every result is a :class:`VerseResult` / :class:`ChartResult`
  carrying either the answer or a ``reason`` — never both, and
  a member-side failure never raises out of this module.
- **The members stay where they live.** Nothing is copied into
  the core. The verse engine is imported from its own member
  directory; the astrology engine is loaded from its own single
  file — the same in-tree members their command lines serve,
  reached the way the Kista binding (E-100) reaches its member:
  by the path this monorepo gives them. An installed core
  without the members beside it gets a plain refusal naming the
  missing path, not an ImportError.
- **Validation happens before composition** (docket 143's
  contract note): the verse service checks the requested world
  against the engine's nine worlds itself, so a bad name is
  refused here and never reaches the composer's silent
  fallback. Docket 143 itself — the library answering a bad
  world with borrowed words — remains E-120's to fix at the
  member; the contract simply never lets it be served.
- **No dead fields are carried** (docket 144's contract note):
  the verse request has no ``include_old_norse`` and no
  ``topic``. Both exist in the member's own config, where the
  first is never consulted by composition and the second is a
  stored label misdescribed as a hint; a contract that carried
  them would promise what the engine does not do. E-112
  decides those fields' fate in the member; until then the
  service surface is exactly what composition honours —
  form, world, stanza count, kennings, alliteration
  strictness, seed.
- **The astrology service refuses before computing when the
  ephemeris is absent** (docket 148's contract note): without
  ``pyswisseph`` the member's own functions return an empty
  position table and fabricated equal cusps, and its command
  line prints them as a chart. The service checks the
  ephemeris first and answers with a reason instead. The
  CLI-wide honesty fix remains E-120's; no chart served here
  is ever the fabricated shape.
- **The dependencies are declared here, as part of the
  contract** (docket 153): :data:`ASTROLOGY_DEPENDENCIES`
  names every package the astrology member imports, which one
  is a hard requirement, and what each optional one costs when
  absent — the member itself declares them nowhere (it has no
  packaging of any kind), so the contract carries the
  declaration. The verse engine needs nothing beyond the
  standard library (:data:`SEIDR_DEPENDENCIES` is empty, and
  that emptiness is itself pinned).
- **The chart contract is tropical only** (docket 154): the
  member's sidereal branch exists in its code but no caller
  has ever reached it and no accuracy fixture has ever run
  against it (E-109 proved the tropical path only). A dead
  option is not served as a live one: the request carries no
  sidereal field, the service always computes tropical, and
  the response says so. Wiring sidereal honestly is a future
  slice's work, gated on fixtures this campaign has not run.
- **The response names its ephemeris model** (E-109 §3):
  :attr:`Chart.ephemeris_model` states that positions come
  from the library's built-in analytical model — the tree
  carries no Swiss Ephemeris data files and the engine sets
  no ephemeris path — so a consumer never has to guess which
  sky produced a chart, and the one-arcminute standard E-109
  proved is the claim that travels with the answer.

Not served, named plainly: the astrology member's other
analyses (synastry, progressions, searches, astrocartography,
its printed Norse overlay) stay command-line only at this
slice — the service serves the natal chart core the later
Part VII slices consume (E-111's day's-astrology stimulus,
E-112's seiðr in conversation). The verse service serves
composition only; interpretation is the companion's voice
(E-112), never this module's.
"""

from __future__ import annotations

import importlib.util
import io
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Final

#: The engines service contract version. A consumer states the
#: version it was written against; the shape may only widen
#: with defaults within a major version (E-037's rules, kin).
CONTRACT_VERSION: Final[str] = "1.0"


@dataclass(frozen=True, slots=True)
class Dependency:
    """One third-party package a member's service shape needs.

    ``package`` is the distribution name, ``imports`` the module
    name it is imported as, ``role`` what the member uses it
    for, and ``required`` whether the service can answer at all
    without it. An optional package's absence is never silent:
    its cost is stated in ``role`` and shows up in the typed
    response (the chart's timezone label, below).
    """

    package: str
    imports: str
    role: str
    required: bool


#: The seiðr engine's dependency declaration: standard library
#: only (E-107 §1, measured from its imports). Empty on purpose.
SEIDR_DEPENDENCIES: Final[tuple[Dependency, ...]] = ()

#: The astrology engine's dependency declaration (docket 153,
#: carried here because the member declares them nowhere —
#: E-108 §1). Five packages, one hard requirement:
ASTROLOGY_DEPENDENCIES: Final[tuple[Dependency, ...]] = (
    Dependency(
        "pyswisseph", "swisseph",
        "the ephemeris itself — every position, house, and "
        "search the engine computes; without it there is no sky "
        "and the service refuses before computing (docket 148)",
        True,
    ),
    Dependency(
        "timezonefinder", "timezonefinder",
        "the IANA timezone name for a place's coordinates; "
        "without it no local-time conversion is possible and "
        "the chart reads its input time as UTC, stated in the "
        "response's timezone label",
        False,
    ),
    Dependency(
        "pytz", "pytz",
        "the local-to-UTC conversion itself, with historical "
        "DST rules; without it (or a timezone name) the input "
        "time is read as UTC, stated in the response",
        False,
    ),
    Dependency(
        "kerykeion", "kerykeion",
        "a network geocoding tier (GeoNames) for places the "
        "built-in table does not carry; without it that tier "
        "drops out and the built-in table is the offline road",
        False,
    ),
    Dependency(
        "geopy", "geopy",
        "a network geocoding tier (Nominatim) for places the "
        "built-in table does not carry; without it that tier "
        "drops out and the built-in table is the offline road",
        False,
    ),
)

#: The ephemeris model every served chart is computed with, as
#: the response states it (E-109 §3): the tree carries no .se1
#: ephemeris data files and the engine never sets an ephemeris
#: path, so the library's built-in analytical model is the sky.
EPHEMERIS_MODEL: Final[str] = (
    "pyswisseph built-in analytical model "
    "(no ephemeris data files configured)"
)

#: The frame every served chart is computed in (docket 154).
CHART_FRAME: Final[str] = "tropical"


def _repo_root() -> Path:
    """The monorepo root of this clone (``src/ember`` → up 3)."""
    return Path(__file__).resolve().parents[2]


def default_seidr_member_dir() -> Path:
    """The in-tree seiðr member this service binds to."""
    return _repo_root() / "seidr_engine"


def default_astrology_engine_path() -> Path:
    """The in-tree astrology member file this service binds to."""
    return _repo_root() / "astrology-engine" / "astrology_engine.py"


# ── The verse service ─────────────────────────────────────


@dataclass(frozen=True, slots=True)
class VerseRequest:
    """One request to the seiðr engine.

    Exactly the fields composition honours (docket 144's
    contract note — see the module docstring). ``world`` is
    one of the engine's nine worlds or ``None`` (the composer
    chooses per composition, and the response reports the
    world actually used). ``seed`` is the determinism switch:
    a seeded request is byte-reproducible, an unseeded one is
    not claimed to be (E-107 §6; E-113 owns the ruling).
    """

    form: str = "fornyrthislag"
    world: str | None = None
    stanzas: int = 1
    use_kennings: bool = True
    alliteration_strictness: float = 0.7
    seed: int | None = None


@dataclass(frozen=True, slots=True)
class Verse:
    """A composed poem, as data.

    ``lines`` is every line of every stanza **in reading
    order** — for ljóðaháttr, pair, full line, pair, full line
    (docket 142, fixed at the source in this slice). ``text``
    is the member's own rendering of the same poem. ``world``
    is the world the words were actually drawn from.
    """

    form: str
    world: str | None
    lines: tuple[str, ...]
    text: str
    stanzas: int
    seed: int | None


@dataclass(frozen=True, slots=True)
class VerseResult:
    """Either a :class:`Verse` or a plain refusal ``reason``."""

    verse: Verse | None
    reason: str | None

    @classmethod
    def served(cls, verse: Verse) -> VerseResult:
        return cls(verse=verse, reason=None)

    @classmethod
    def refused(cls, reason: str) -> VerseResult:
        return cls(verse=None, reason=reason)


_SEIDR_MODULES: dict[str, object] = {}


def _load_seidr(member_dir: Path) -> tuple[object | None, str | None]:
    """Import the member's ``seidr`` package, or say why not."""
    cached = _SEIDR_MODULES.get(str(member_dir))
    if cached is not None:
        return cached, None
    if not (member_dir / "seidr" / "__init__.py").is_file():
        return None, (
            f"seidr member not found at {member_dir} — the "
            "engines service binds to the in-tree member "
            "(seidr_engine/ in this monorepo)"
        )
    path_entry = str(member_dir)
    if path_entry not in sys.path:
        sys.path.insert(0, path_entry)
    try:
        import importlib

        seidr = importlib.import_module("seidr")
    except ImportError as exc:
        return None, f"seidr member at {member_dir} did not import: {exc}"
    _SEIDR_MODULES[str(member_dir)] = seidr
    return seidr, None


def compose_verse(
    request: VerseRequest,
    *,
    member_dir: Path | None = None,
) -> VerseResult:
    """Compose verse through the seiðr engine, as a service.

    Validates the form and world before composing (an unknown
    form is the member's own refusal, re-stated; an unknown
    world is refused here, before the composer can answer it
    with borrowed words — docket 143's contract note). Never
    raises for a member-side failure.
    """
    member = default_seidr_member_dir() if member_dir is None else member_dir
    seidr, problem = _load_seidr(member)
    if problem is not None:
        return VerseResult.refused(problem)
    assert seidr is not None

    # The member's submodules are reached through the loaded
    # package, never by a core-level import statement: the
    # core's import map (E-044) is exact, and a member's
    # package is not a core dependency — it is loaded from
    # its own home, above, or not at all.
    import importlib

    forms = importlib.import_module("seidr.forms")
    poet = importlib.import_module("seidr.poet")

    try:
        forms.get_form(request.form)
    except ValueError as exc:
        return VerseResult.refused(f"seidr service: {exc}")
    if request.world is not None and request.world not in seidr.NINE_WORLDS:
        return VerseResult.refused(
            f"seidr service: unknown world {request.world!r} — "
            "the engine's worlds are "
            + ", ".join(seidr.NINE_WORLDS)
        )
    if request.stanzas < 1:
        return VerseResult.refused(
            "seidr service: a poem needs at least one stanza"
        )
    if not 0.0 <= request.alliteration_strictness <= 1.0:
        return VerseResult.refused(
            "seidr service: alliteration_strictness is a "
            "probability, between 0 and 1"
        )

    config = poet.PoemConfig(
        form=request.form,
        domain=request.world,
        num_stanzas=request.stanzas,
        use_kennings=request.use_kennings,
        alliteration_strictness=request.alliteration_strictness,
        seed=request.seed,
    )
    try:
        poem = poet.Skald(seed=request.seed).compose_poem(config)
    except Exception as exc:  # the member's failure, stated
        return VerseResult.refused(
            f"seidr service: composition failed: "
            f"{type(exc).__name__}: {exc}"
        )
    lines = tuple(line.text for stanza in poem.stanzas for line in stanza.lines)
    world = poem.stanzas[0].domain if poem.stanzas else request.world
    return VerseResult.served(
        Verse(
            form=request.form,
            world=world,
            lines=lines,
            text=poem.format(),
            stanzas=len(poem.stanzas),
            seed=request.seed,
        )
    )


# ── The astrology service ─────────────────────────────────


@dataclass(frozen=True, slots=True)
class ChartRequest:
    """One natal-chart request to the astrology engine.

    ``date`` is ``YYYY-MM-DD``; ``time`` is ``HH:MM`` local to
    the place, or ``None`` (the engine's noon default, flagged
    in the response as unknown time). The place is explicit
    coordinates (``lat`` and ``lon`` together) or a ``city``
    (with optional ``nation``) resolved through the engine's
    own cascade — explicit coordinates first, its built-in
    table the offline tier. There is deliberately no sidereal
    field (docket 154) and no house-system field: Placidus is
    the only system the member computes (E-108 §2).
    """

    date: str
    time: str | None = None
    city: str = ""
    nation: str = ""
    lat: float | None = None
    lon: float | None = None


@dataclass(frozen=True, slots=True)
class BodyPosition:
    """One body's served position."""

    name: str
    longitude: float
    sign: str
    degree: int
    minutes: int
    retrograde: bool
    house: int


@dataclass(frozen=True, slots=True)
class Aspect:
    """One aspect between two bodies."""

    body_a: str
    body_b: str
    name: str
    orb: float
    applying: bool


@dataclass(frozen=True, slots=True)
class Chart:
    """A natal chart, as data — the member's maths, typed.

    Positions, Placidus cusps, aspects, and the seven Arabic
    lots are the engine's own outputs (E-109's accuracy gate
    covers the maths); ``day_chart`` is the chart's sect as
    the engine rules it after E-109's fix. ``tz_label`` is the
    engine's own statement of how the input time was read —
    including, when no timezone could be resolved, that the
    time was treated as UTC. ``ephemeris_model`` and
    ``frame`` travel with every chart (E-109 §3, docket 154).
    """

    julian_day: float
    positions: tuple[BodyPosition, ...]
    cusps: tuple[float, ...]
    ascendant: float
    mc: float
    aspects: tuple[Aspect, ...]
    lots: tuple[tuple[str, float], ...]
    day_chart: bool
    lat: float
    lon: float
    tz_name: str
    tz_label: str
    time_known: bool
    ephemeris_model: str
    frame: str


@dataclass(frozen=True, slots=True)
class ChartResult:
    """Either a :class:`Chart` or a plain refusal ``reason``."""

    chart: Chart | None
    reason: str | None

    @classmethod
    def served(cls, chart: Chart) -> ChartResult:
        return cls(chart=chart, reason=None)

    @classmethod
    def refused(cls, reason: str) -> ChartResult:
        return cls(chart=None, reason=reason)


_ASTRO_MODULES: dict[str, object] = {}


def _load_astrology(engine_path: Path) -> tuple[object | None, str | None]:
    """Load the member's single engine file, or say why not.

    The engine rebinds ``sys.stdout`` at import; the load runs
    with a throwaway buffered stdout and the real one is
    restored after (the E-108 battery's proven shape).
    """
    cached = _ASTRO_MODULES.get(str(engine_path))
    if cached is not None:
        return cached, None
    if not engine_path.is_file():
        return None, (
            f"astrology member not found at {engine_path} — "
            "the engines service binds to the in-tree member "
            "(astrology-engine/astrology_engine.py in this "
            "monorepo)"
        )
    real_stdout = sys.stdout
    sys.stdout = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
    try:
        spec = importlib.util.spec_from_file_location(
            "ember_astrology_engine_service", engine_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as exc:
        return None, (
            f"astrology member at {engine_path} did not load: "
            f"{type(exc).__name__}: {exc}"
        )
    finally:
        sys.stdout = real_stdout
    _ASTRO_MODULES[str(engine_path)] = module
    return module, None


def ephemeris_available(engine_path: Path | None = None) -> bool:
    """True when the astrology member has its ephemeris.

    The one hard requirement of :data:`ASTROLOGY_DEPENDENCIES`:
    the member imports ``pyswisseph`` guarded, so absence is a
    state to check, not an import error to catch.
    """
    path = default_astrology_engine_path() if engine_path is None else engine_path
    module, problem = _load_astrology(path)
    if problem is not None:
        return False
    return bool(module.SWE)


def request_chart(
    request: ChartRequest,
    *,
    engine_path: Path | None = None,
) -> ChartResult:
    """Cast a natal chart through the astrology engine.

    Refuses **before computing** when the ephemeris is absent
    (docket 148's contract note), when the request's own
    shapes are invalid, and when the place cannot be resolved
    (the engine's 0°N 0°E default is never served as a chart).
    Never raises for a member-side failure.
    """
    path = default_astrology_engine_path() if engine_path is None else engine_path
    engine, problem = _load_astrology(path)
    if problem is not None:
        return ChartResult.refused(problem)
    assert engine is not None

    if not engine.SWE:
        return ChartResult.refused(
            "astrology service: the ephemeris is not available "
            "— pyswisseph (the one hard requirement declared in "
            "ASTROLOGY_DEPENDENCIES) is not installed, so no "
            "chart can be computed; the service refuses rather "
            "than serve the member's empty-positions shape "
            "(docket 148)"
        )
    if (request.lat is None) != (request.lon is None):
        return ChartResult.refused(
            "astrology service: lat and lon are given together "
            "or not at all"
        )
    if request.lat is not None and not -90.0 <= request.lat <= 90.0:
        return ChartResult.refused(
            "astrology service: lat is outside -90 to 90"
        )
    if request.lon is not None and not -180.0 <= request.lon <= 180.0:
        return ChartResult.refused(
            "astrology service: lon is outside -180 to 180"
        )
    if request.lat is None and not request.city.strip():
        return ChartResult.refused(
            "astrology service: a chart needs a place — "
            "explicit lat/lon or a city name"
        )
    # The member's own date parsing is permissive to a fault:
    # its Julian-day conversion silently normalises a
    # thirteenth month into the next year. The contract
    # validates the calendar shapes itself, before computing.
    import datetime as _datetime

    try:
        _datetime.date.fromisoformat(request.date)
    except ValueError:
        return ChartResult.refused(
            f"astrology service: {request.date!r} is not a "
            "calendar date (YYYY-MM-DD)"
        )
    if request.time is not None:
        parts = request.time.split(":")
        try:
            hour, minute = int(parts[0]), int(parts[1])
            if len(parts) != 2 or not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError
        except (ValueError, IndexError):
            return ChartResult.refused(
                f"astrology service: {request.time!r} is not a "
                "time of day (HH:MM)"
            )

    try:
        (year, month, day, utc_hour, lat, lon, tz_name, tz_label,
         time_known, place_defaulted) = engine.resolve_birth(
            request.date, request.time, request.city,
            request.nation, request.lat, request.lon)
    except Exception as exc:  # unparsable date/time, stated
        return ChartResult.refused(
            f"astrology service: the birth data could not be "
            f"read: {type(exc).__name__}: {exc}"
        )
    # The member's flag means "the city *name* did not resolve"
    # — its geocoder returns resolved=False for the explicit-
    # coordinate road too, where the coordinates themselves
    # are the place (its CLI reads the flag the same way, as a
    # label switch). It therefore proves a fall-through to the
    # 0°N 0°E default only on the name road, and only there is
    # it a refusal.
    if place_defaulted and request.lat is None:
        return ChartResult.refused(
            f"astrology service: the place {request.city!r} "
            "could not be resolved by the engine's cascade or "
            "its built-in table — no chart is cast at the "
            "default 0°N 0°E"
        )

    jd = engine.julian_day(year, month, day, utc_hour)
    positions = engine.calc_planet_positions(jd, tropical=True)
    if not positions:
        return ChartResult.refused(
            "astrology service: the ephemeris returned no "
            "positions for that moment — no chart is served "
            "from an empty sky"
        )
    cusps, asc, mc = engine.calc_houses(jd, lat, lon)
    bodies = tuple(
        BodyPosition(
            name=name,
            longitude=data["longitude"],
            sign=data["sign"],
            degree=data["degree"],
            minutes=data["minutes"],
            retrograde=bool(data["retrograde"]),
            house=engine.planet_house(data["longitude"], cusps),
        )
        for name, data in positions.items()
    )
    aspects = tuple(
        Aspect(body_a=a, body_b=b, name=name, orb=orb, applying=applying)
        for a, b, name, orb, _quality, _glyph, applying
        in engine.calc_aspects(positions)
    )
    day_chart = engine.is_day_chart(
        positions["Sun"]["longitude"], asc)
    lots = tuple(engine.calc_lots(positions, asc, day_chart).items())
    return ChartResult.served(
        Chart(
            julian_day=jd,
            positions=bodies,
            cusps=tuple(cusps),
            ascendant=asc,
            mc=mc,
            aspects=aspects,
            lots=lots,
            day_chart=day_chart,
            lat=lat,
            lon=lon,
            tz_name=tz_name,
            tz_label=tz_label,
            time_known=time_known,
            ephemeris_model=EPHEMERIS_MODEL,
            frame=CHART_FRAME,
        )
    )


__all__ = [
    "ASTROLOGY_DEPENDENCIES",
    "CHART_FRAME",
    "CONTRACT_VERSION",
    "EPHEMERIS_MODEL",
    "SEIDR_DEPENDENCIES",
    "Aspect",
    "BodyPosition",
    "Chart",
    "ChartRequest",
    "ChartResult",
    "Dependency",
    "Verse",
    "VerseRequest",
    "VerseResult",
    "compose_verse",
    "default_astrology_engine_path",
    "default_seidr_member_dir",
    "ephemeris_available",
    "request_chart",
]
