"""E-113 — Determinism + offline: both engines fully local.

Pins ``docs/architecture/E-113_DETERMINISM_AND_OFFLINE.md``
and, behind it, the two rulings this slice executes:

* **Docket 146 — one seed semantics.** A seeded seiðr
  composition is reproducible from its seed alone:
  across calls on one Skald, across Skalds seeded only
  through their config, across processes (the
  alliteration-group choice no longer rides on a
  hash-ordered set), and identically through the
  library, the member CLI, and the E-110 service. An
  unseeded composition is not reproducible, and the
  member's branding now says exactly that:
  *deterministic when seeded* (package docstring and
  pyproject description pinned here).
* **Docket 153 — the offline ruling.** Through the
  E-110 service both engines are fully local: seiðr
  composes under a cut network with zero attempts;
  a chart's place resolves only from explicit
  coordinates or the member's built-in table — the
  member's network geocoding tiers (Nominatim,
  GeoNames) are skipped on the service's road even
  when their packages are installed, so a city the
  table does not carry is refused, never fetched.
  The member's own cascade keeps the tiers on its
  default (CLI) road, proven here by contrast with a
  fake geocoder.
* **Date-pinned charts.** In the live shape a chart
  is a pure function of its pinned date/time/place:
  byte-equal across calls and across processes, at
  two pinned moments, and cast whole under the
  network cut with zero external attempts.
"""

from __future__ import annotations

import importlib.util
import io
import ipaddress
import json
import socket
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "docs" / "architecture" / "E-113_DETERMINISM_AND_OFFLINE.md"
SEIDR_MEMBER = REPO / "seidr_engine"
ASTRO_ENGINE = REPO / "astrology-engine" / "astrology_engine.py"

sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(SEIDR_MEMBER))

from ember import engines  # noqa: E402
from ember.engines import (  # noqa: E402
    ASTROLOGY_DEPENDENCIES,
    ChartRequest,
    VerseRequest,
    compose_verse,
    request_chart,
)

LIVE = importlib.util.find_spec("swisseph") is not None
LONDON = {"lat": 51.5074, "lon": -0.1278}


def _flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


# ── The record, on file ─────────────────────────────────


def test_doc_records_both_rulings():
    text = _flat(DOC)
    for needle in ("one seed semantics",
                   "deterministic when seeded",
                   "fully local",
                   "Docket 146",
                   "Docket 153",
                   "Next: E-114"):
        assert needle in text, needle


# ── Docket 146: the branding says the conditional truth ─


def test_branding_is_conditional_in_the_members_live_surfaces():
    init_text = (SEIDR_MEMBER / "seidr" / "__init__.py").read_text(
        encoding="utf-8")
    assert "deterministic when seeded" in init_text
    assert "A deterministic Old Norse" not in init_text
    pyproject = (SEIDR_MEMBER / "pyproject.toml").read_text(
        encoding="utf-8")
    assert "deterministic when seeded" in pyproject
    assert "Deterministic Old Norse" not in pyproject


def test_dependency_declaration_states_the_offline_ruling():
    roles = {d.package: d.role for d in ASTROLOGY_DEPENDENCIES}
    for pkg in ("kerykeion", "geopy"):
        assert "never consults" in roles[pkg], pkg
        assert "E-113" in roles[pkg], pkg


# ── Docket 146: one seed, every holder, every road ──────


def _library_poem(seed: int, stanzas: int = 1) -> str:
    from seidr.poet import PoemConfig, Skald

    return Skald(seed=seed).compose_poem(
        PoemConfig(form="fornyrthislag", seed=seed,
                   num_stanzas=stanzas)).format()


def test_seeded_poem_same_for_fresh_reused_and_config_only_skalds():
    from seidr.poet import PoemConfig, Skald

    canonical = _library_poem(42, stanzas=2)
    reused = Skald(seed=42)
    first = reused.compose_poem(
        PoemConfig(form="fornyrthislag", seed=42,
                   num_stanzas=2)).format()
    second = reused.compose_poem(
        PoemConfig(form="fornyrthislag", seed=42,
                   num_stanzas=2)).format()
    config_only = Skald().compose_poem(
        PoemConfig(form="fornyrthislag", seed=42,
                   num_stanzas=2)).format()
    assert first == canonical
    assert second == canonical
    assert config_only == canonical


def test_seeded_single_stanza_compose_is_reproducible_on_reuse():
    from seidr.poet import PoemConfig, Skald

    skald = Skald()
    one = skald.compose(PoemConfig(seed=7))
    two = skald.compose(PoemConfig(seed=7))
    assert [line.text for line in one.lines] == [
        line.text for line in two.lines]


def test_seeded_poem_is_the_same_across_processes_and_hash_seeds():
    code = (
        "import sys; sys.path.insert(0, sys.argv[1]); "
        "from seidr.poet import Skald, PoemConfig; "
        "print(Skald(seed=42).compose_poem("
        "PoemConfig(seed=42)).format())"
    )
    outputs = []
    for hash_seed in ("0", "1"):
        proc = subprocess.run(
            [sys.executable, "-c", code, str(SEIDR_MEMBER)],
            env={"PYTHONPATH": str(SEIDR_MEMBER),
                 "PYTHONHASHSEED": hash_seed,
                 "PATH": "/usr/bin:/bin"},
            capture_output=True, text=True, timeout=60)
        assert proc.returncode == 0, proc.stderr
        outputs.append(proc.stdout)
    assert outputs[0] == outputs[1]
    assert _library_poem(42).strip() in outputs[0]


def test_cli_seed_is_the_library_seed():
    outputs = []
    for hash_seed in ("0", "1"):
        proc = subprocess.run(
            [sys.executable, "-m", "seidr.cli", "--seed", "42"],
            env={"PYTHONPATH": str(SEIDR_MEMBER),
                 "PYTHONHASHSEED": hash_seed,
                 "PATH": "/usr/bin:/bin"},
            capture_output=True, text=True, timeout=60)
        assert proc.returncode == 0, proc.stderr
        outputs.append(proc.stdout)
    assert outputs[0] == outputs[1]
    assert _library_poem(42).strip() in outputs[0]


def test_service_seed_is_the_library_seed():
    result = compose_verse(VerseRequest(seed=42))
    assert result.reason is None
    assert result.verse.text.strip() == _library_poem(42).strip()
    again = compose_verse(VerseRequest(seed=42))
    assert again.verse == result.verse


def test_unseeded_poems_are_not_reproducible():
    from seidr.poet import PoemConfig, Skald

    poems = {Skald().compose_poem(PoemConfig()).format()
             for _ in range(5)}
    assert len(poems) > 1


# ── The network cut (E-029's shape, narrowed) ───────────


_LOCAL_NAMES = {"localhost", "ip6-localhost"}


def _is_local_host(host: object) -> bool:
    if host is None or host == "" or not isinstance(host, str):
        return host is None or host == ""
    if host in _LOCAL_NAMES or host == socket.gethostname():
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


class _OfflineGuard:
    def __init__(self) -> None:
        self.attempts: list[str] = []
        self._real_getaddrinfo = socket.getaddrinfo
        self._real_connect = socket.socket.connect

    def getaddrinfo(self, host, port, *args, **kwargs):
        if _is_local_host(host):
            return self._real_getaddrinfo(host, port, *args, **kwargs)
        self.attempts.append(f"dns:{host}")
        raise socket.gaierror("E-113 offline cut: DNS refused")

    def connect(self, sock, address):
        host = address[0] if isinstance(address, tuple) else None
        if host is None or _is_local_host(host):
            return self._real_connect(sock, address)
        self.attempts.append(f"connect:{host}")
        raise OSError("E-113 offline cut: connection refused")


@pytest.fixture
def offline(monkeypatch: pytest.MonkeyPatch) -> _OfflineGuard:
    guard = _OfflineGuard()

    def _connect(sock, address):
        return guard.connect(sock, address)

    monkeypatch.setattr(socket, "getaddrinfo", guard.getaddrinfo)
    monkeypatch.setattr(socket.socket, "connect", _connect)
    return guard


def test_seidr_composes_under_the_network_cut(offline):
    result = compose_verse(VerseRequest(seed=42))
    assert result.reason is None
    assert result.verse.text.strip() == _library_poem(42).strip()
    assert offline.attempts == []


# ── Docket 153 at the member: the offline road ──────────


def _load_astrology_member():
    real_stdout = sys.stdout
    sys.stdout = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
    try:
        spec = importlib.util.spec_from_file_location(
            "ember_astrology_engine_e113", ASTRO_ENGINE)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.stdout = real_stdout
    return module


class _FakeLocation:
    latitude = 41.99
    longitude = -71.99


class _FakeGeocoder:
    def __init__(self) -> None:
        self.queries: list[str] = []

    def geocode(self, query):
        self.queries.append(query)
        return _FakeLocation()


def test_member_offline_road_never_consults_the_network_tiers(
        monkeypatch: pytest.MonkeyPatch):
    module = _load_astrology_member()
    fake = _FakeGeocoder()
    monkeypatch.setattr(module, "_geo", lambda: fake)

    # A table city resolves from the table, tiers untouched.
    assert module.geocode_city("London", "UK", offline=True) == (
        51.5074, -0.1278, True)
    # A place only a network tier could find falls through
    # to the stated default, tiers still untouched.
    lat, lon, resolved = module.geocode_city(
        "Woonsocket", "US", offline=True)
    assert (lat, lon, resolved) == (0.0, 0.0, False)
    assert fake.queries == []
    # Explicit coordinates are the place, on either road.
    assert module.geocode_city(
        "", "", 10.0, 20.0, offline=True) == (10.0, 20.0, False)


def test_member_default_road_keeps_the_network_tiers(
        monkeypatch: pytest.MonkeyPatch):
    module = _load_astrology_member()
    fake = _FakeGeocoder()
    monkeypatch.setattr(module, "_geo", lambda: fake)
    lat, lon, resolved = module.geocode_city("Woonsocket", "US")
    assert resolved is True
    assert (lat, lon) == (41.99, -71.99)
    assert fake.queries  # the tier really was consulted


# ── Live shape: date-pinned charts, local and reproducible ─


@pytest.mark.skipif(not LIVE, reason="needs the isolated ephemeris dir")
def test_chart_is_byte_equal_across_calls_and_processes():
    request = ChartRequest(date="2000-01-01", time="12:00", **LONDON)
    first = request_chart(request)
    second = request_chart(request)
    assert first.reason is None
    assert first.chart == second.chart

    code = (
        "import sys, json; sys.path.insert(0, sys.argv[1]); "
        "from ember.engines import request_chart, ChartRequest; "
        "r = request_chart(ChartRequest(date='2000-01-01', "
        "time='12:00', lat=51.5074, lon=-0.1278)); "
        "c = r.chart; "
        "print(json.dumps([c.julian_day, "
        "[p.longitude for p in c.positions], list(c.cusps)]))"
    )
    proc = subprocess.run(
        [sys.executable, "-c", code, str(REPO / "src")],
        env={"PYTHONPATH": ":".join(
                 p for p in sys.path if p and "test" not in p),
             "PATH": "/usr/bin:/bin"},
        capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0, proc.stderr
    chart = first.chart
    assert json.loads(proc.stdout) == [
        chart.julian_day,
        [p.longitude for p in chart.positions],
        list(chart.cusps)]


@pytest.mark.skipif(not LIVE, reason="needs the isolated ephemeris dir")
def test_chart_second_pinned_moment(offline):
    # Cast whole under the network cut: the service's
    # road is local even with every geocoding package
    # installed.
    result = request_chart(ChartRequest(
        date="1990-06-15", time="12:00", city="London", nation="UK"))
    assert result.reason is None
    chart = result.chart
    assert (chart.lat, chart.lon) == (51.5074, -0.1278)
    by_name = {b.name: b for b in chart.positions}
    assert by_name["Sun"].longitude == pytest.approx(
        84.0898, abs=0.02)
    assert chart.ascendant == pytest.approx(164.7423, abs=0.05)
    assert offline.attempts == []


@pytest.mark.skipif(not LIVE, reason="needs the isolated ephemeris dir")
def test_chart_place_outside_the_table_is_refused_never_fetched():
    result = request_chart(ChartRequest(
        date="2000-01-01", time="12:00", city="Woonsocket",
        nation="US"))
    assert result.chart is None
    assert "could not be resolved" in result.reason
