# 10 — Sibling Matrix Overview

A canonical reference for the eleven sibling projects, their
status, their integration role in Yggdrasil, and where to find
deep details.

---

## The matrix

| # | Sibling | Cosmological realm | What it is (1-line) | Yggdrasil role | Deep-dive |
|---|---|---|---|---|---|
| 1 | **bifrost** | Bifrǫst / rainbow bridge | Composite memory provider (Mímir + Huginn + Muninn) | Memory plane gateway | [`11_SIBLING_BIFROST.md`](11_SIBLING_BIFROST.md) |
| 2 | **mimir-well** | Mímisbrunnr / well at root | Persistent self-healing memory (SQLite + FTS5 + Ebbinghaus) | Memory plane: structured + decay | [`12_SIBLING_MIMIR_WELL.md`](12_SIBLING_MIMIR_WELL.md) |
| 3 | **Verdandi** | Urðarbrunnr / present-Norn | Real-time event bus / self-awareness / Unix Domain Socket | Self-awareness plane | [`13_SIBLING_VERDANDI.md`](13_SIBLING_VERDANDI.md) |
| 4 | **seidr_engine** | Vanaheim / Vanir magic | Old Norse poetry generator (rule-based, 4 meters) | Creative / mood-channel | [`14_SIBLING_SEIDR_ENGINE.md`](14_SIBLING_SEIDR_ENGINE.md) |
| 5 | **Kista** | Niflheim / hidden chest | Encrypted vault (Fernet, 8 entry types) | Secrets plane / gatekeeper | [`15_SIBLING_KISTA.md`](15_SIBLING_KISTA.md) |
| 6 | **Hamr** | Alfheim / shape-skin | Parametric VRM avatar forge | Embodiment for Auga (GUI) | [`16_SIBLING_HAMR.md`](16_SIBLING_HAMR.md) |
| 7 | **CloakBrowser** | Útgarðr / outer-world walker | Stealth Chromium / Playwright wrapper | Web access plane | [`17_SIBLING_CLOAKBROWSER.md`](17_SIBLING_CLOAKBROWSER.md) |
| 8 | **astrology-engine** | Muspelheim / sky-fire | Swiss Ephemeris / 16 CLI subcommands | Temporal rhythm plane | [`18_SIBLING_ASTROLOGY_ENGINE.md`](18_SIBLING_ASTROLOGY_ENGINE.md) |
| 9 | **MemPalace** | Helheim / realm of stored | Local-first verbatim memory (96.6% R@5) | Alt/companion to mimir-well | [`19_SIBLING_MEMPALACE.md`](19_SIBLING_MEMPALACE.md) |
| 10 | **norse-dict** | Yggdrasil's hoard | Old Norse lexicon (Cleasby-Vigfusson) | Corpus for ingestion / Seiðr | [`20_SIBLING_NORSE_DICT.md`](20_SIBLING_NORSE_DICT.md) |
| 11 | **Open-VTT** | (not part of Yggdrasil) | Virtual tabletop (Godot) | Out of scope | [`21_SIBLING_OPEN_VTT.md`](21_SIBLING_OPEN_VTT.md) |

Plus **Ember (`src/ember/`)** itself = Asgard / the spark.

Plus **Stofa (`docs/tui/`)** = the hall surface (separate design
tree).

---

## At-a-glance integration phasing

| Sibling | Integrated in Phase | Optional? |
|---|---|---|
| bifrost | Phase 1 | Required for memory composition |
| mimir-well | Phase 1 | Required as one of bifrost's backends |
| Kista | Phase 2 | Required (secrets gatekeeper) |
| Verdandi | Phase 3 | Optional (self-awareness layer) |
| Seiðr | Phase 3 | Optional (mood-channel) |
| Astrology Engine | Phase 3 | Optional (rhythm-channel) |
| CloakBrowser | Phase 2 | Optional (as MCP tool) |
| MemPalace | Phase 2 | Optional (alt memory backend) |
| Hamr | Phase 4 | Optional (Auga-only) |
| norse-dict | Phase 1 | Optional (corpus, ingestible into Well) |
| Open-VTT | never | N/A |

"Required" = needed for the core Yggdrasil contract.
"Optional" = operator opts in via pip extras + config.

---

## License compatibility

All sibling projects: **MIT** or compatible. Yggdrasil's
integration layer in `src/ember/yggdrasil/` is also MIT
(matching Ember).

Audit:
- bifrost: MIT
- mimir-well: MIT (assumed; matches Volmarr's pattern; verify
  on integration)
- Verdandi: framework-agnostic, license verified at integration
- seidr_engine: MIT (assumed)
- Kista: MIT
- Hamr: MIT
- CloakBrowser: MIT
- astrology-engine: MIT
- MemPalace: needs verification
- norse-dict: corpus, public-domain dictionary text (Cleasby-
  Vigfusson is pre-1900); web frontend MIT
- Open-VTT: separate license; not relevant since not integrated

Yggdrasil licensing audit happens at each phase ratification.

---

## Per-sibling implementation language

| Sibling | Language | Notes |
|---|---|---|
| bifrost | Python | Imports as Python package |
| mimir-well | Python | Imports as Python package |
| Verdandi | Python | Imports as Python package + Unix socket protocol |
| Seiðr | Python | Imports as Python package |
| Kista | Python (CLI + library) | Used via library interface |
| Hamr | Python | Imports as Python package |
| CloakBrowser | Python + npm | Python: orchestrator; npm: Chromium driver |
| Astrology Engine | Python (pyswisseph) | Imports as Python package |
| MemPalace | Python | Imports as Python package |
| norse-dict | Next.js (web) | Data corpus only used |
| Open-VTT | Godot | Not integrated |

Two siblings (CloakBrowser, norse-dict) have non-Python
components. Both have Python interfaces or static data we can
use.

---

## Per-sibling resource footprint

How heavy each is at runtime:

| Sibling | Memory | Disk | CPU | Notes |
|---|---|---|---|---|
| bifrost | ~50 MB | ~2 MB | <1% idle | Pure orchestrator |
| mimir-well | ~30 MB | grows | <1% idle | SQLite is light |
| Verdandi | ~30 MB | small | <1% idle | Event bus is async |
| Seiðr | ~20 MB | <1 MB | per-call burst | Pure functional |
| Kista | ~10 MB | <100KB | per-call only | Vault opens on demand |
| Hamr | ~200 MB | ~50 MB | high during render | Avatar generation |
| CloakBrowser | ~300 MB | ~200 MB | high during fetch | Chromium |
| Astrology Engine | ~50 MB | ~30 MB ephemeris | <1% | Compute per query |
| MemPalace | varies | grows | <1% idle | Local DB |
| norse-dict | n/a (data) | ~50 MB | n/a | Static |

Pi-class operators (Eirwyn persona) will install: bifrost,
mimir-well, Verdandi, Kista, Seiðr, Astrology, norse-dict. Total
runtime: ~200 MB.

They'll skip: Hamr (no GUI), CloakBrowser (heavy + optional),
MemPalace (alt to Mímir).

Desktop operators install everything.

---

## How each sibling is currently distributed

| Sibling | Current distribution | Yggdrasil's planned distribution |
|---|---|---|
| bifrost | local-only / monorepo | PyPI as `bifrost-bridge` + pip extra `ember-agent[bifrost]` |
| mimir-well | local-only | PyPI as `mimir-well` + pip extra |
| Verdandi | local-only | PyPI as `verdandi` + pip extra |
| Seiðr | local-only | PyPI as `seidr-engine` + pip extra |
| Kista | local-only | PyPI as `kista` (already namespace) + pip extra |
| Hamr | local-only | PyPI as `hamr` + pip extra |
| CloakBrowser | published as `cloakbrowser` on PyPI + npm | already there; pip extra |
| Astrology Engine | local-only | PyPI as `agent-astrology-engine` + pip extra |
| MemPalace | already on PyPI as `mempalace` | already there; pip extra |
| norse-dict | web app | data fetched at install, ingestible |
| Open-VTT | independent | n/a |

PyPI publishing happens *per sibling*, *per maintainer's
choice*. Yggdrasil doesn't force publication; it provides the
pip-extras *if and when* the sibling is on PyPI.

For non-published siblings, operators install from source
(local monorepo or git URL).

---

## Cross-sibling dependencies

What requires what:

- **bifrost** → mimir-well (Mímir backend), Qdrant (Huginn
  backend; pip dep), Hebbian implementation (Muninn backend;
  in-bifrost or pip)
- **Verdandi** → (no sibling deps)
- **Seiðr** → (no sibling deps; pure functional)
- **Kista** → (no sibling deps)
- **Hamr** → Blender (system dep) or VRM library (pip dep)
- **CloakBrowser** → npm/playwright (subprocess)
- **Astrology Engine** → pyswisseph (pip dep) + ephemeris data
- **MemPalace** → its own deps
- **norse-dict** → Next.js (only for the web frontend)

Yggdrasil-the-integration only depends on the sibling Python
APIs. It doesn't reach into sibling internals.

---

## What's NOT in the matrix

Things that *could* become siblings someday but aren't:

- A vector store sibling (we use Qdrant via bifrost; if a
  Norse-named vector DB ever ships, it could replace).
- A speech-synthesis sibling (Rödd's eventual companion).
- A web-search sibling (CloakBrowser fetches; a search
  endpoint sibling could add structured search).

These are not committed; they're sketched in
[`05_THE_FUTURISTIC_HORIZON.md`](../vision/05_THE_FUTURISTIC_HORIZON.md).

---

## Closing

Eleven siblings. Three required for the core integration
(bifrost, mimir-well, Kista). Six optional but powerful.
One non-Python corpus. One non-integrated archival project.

The matrix is the canonical reference; the per-sibling
deep-dives ([`11_*`](11_SIBLING_BIFROST.md) through
[`21_*`](21_SIBLING_OPEN_VTT.md)) are where the actual
integration plans live.
