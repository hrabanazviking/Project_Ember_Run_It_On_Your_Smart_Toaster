# E-037 — Core API freeze v1 (library shape)

*Part II, slice E-037. Roadmap line: "Core API freeze v1
(library shape) — members and bindings (Parts IV–X) bind
here." Docket 56 CLOSED (its member half lands here; the core
half closed at E-033).*

## Why a freeze, and why now

Part II built the companion piece by piece: the backend
contract (E-022), the Aesir binding (E-023), the cognition
candidate (E-024), personae (E-025), tools discipline
(E-026/E-027), persistence (E-031), one config surface
(E-033), conversations (E-035), determinism (E-036). Each
slice froze its own shape in its own tests. What no slice had
done was say, in one place, **which of those shapes a member
may rely on** — the surface was real but scattered across
curated `__all__` lists, two empty `__init__` files
(`ember.well.brunnr`, `ember.schemas`), and prose.

Parts IV–X bind members to this core — Verdandi's nerves
(E-067), the memory face (E-080), the Kista binding (E-100),
the engines as services "under the member contract (E-037's
kin)" (E-110), the bridges (Part VIII). Those parts need a
contract that cannot drift silently underneath them. E-037
is that contract.

## The freeze

**`ember.api`** is the freeze registry (stdlib-only at import;
the surface check imports lazily, so asking for the version
never pulls an optional extra or an adapter into the
process):

- `API_VERSION = "1.0.0"`, `API_MAJOR = 1`, re-exported as
  `ember.API_VERSION`. The API version is **separate from the
  package version**: `ember.__version__` stays `0.2.0`, an
  operator-facing release label. The package may gain
  features without moving the library contract.
- `API_V1` lists every individually frozen name as an
  `ApiEntry` (module, attribute, kind). `api_manifest()`
  returns the full surface as data — the API_V1 entries plus
  one entry per name in each frozen schema module — sorted by
  dotted path: **155 entries** at the freeze (63 individual +
  92 schema names).
- `is_api_compatible(want)` is the member's gate: same major,
  and this build's minor/patch at least the wanted one.
  `"1"`, `"1.0"`, `"1.0.0"` all name the freeze; `"1.1"` does
  not bind to a 1.0 build; an unparseable want never binds
  and never raises.
- `verify_api_surface()` resolves every frozen name against
  the live code and returns the problems (empty at the
  freeze, in the bare stdlib-only environment). The E-037
  tests pin it to empty, so a rename of a frozen name fails
  in this repo before it fails in a member.

**The rules of v1** (semver, stated once here): within major
version 1, a frozen name is never removed, renamed, or given
an incompatible signature; a signature may only widen with
defaults. Additions are a minor bump, fixes a patch bump,
and only a major bump may break a frozen name — a major bump
is a campaign-level act with its own slice, never a side
effect of another slice.

## What is frozen

| Surface | Frozen shape |
|---|---|
| Version | `ember.__version__`, `ember.API_VERSION`, `ember.api` (version, manifest, compatibility, verification) |
| Config | `ember.config`: `load_ember_config`, `ember_config_path`, `ember_config_exists`, `write_ember_config`, `ConfigError` |
| Schemas | `ember.schemas.*` as module surfaces — every name in each of the 12 modules' `__all__`, at its module path (`SCHEMA_MODULES`) |
| Funi | `FuniHandle` + `open` (`ember.spark.funi`), the registry (`backend_registry`, `capabilities_for`, `BackendRegistration`, `wrap_complete_as_stream`) |
| Determinism | `ember.spark.funi.determinism`: `effective_options`, `determinism_error`, `is_deterministic`, `DETERMINISTIC_TEMPERATURE` |
| Windowing | `ember.spark.funi.windowing`: `Summariser`, `ExtractiveSummariser`, `window_history`, `WindowedHistory`, `estimate_tokens`, `episode_cost` |
| Tools | `ember.spark.funi.tools` as a module surface — its curated `__all__` (registry, approval, audit, permissions, plain shapes) |
| Cognition | `CognitionHandle` + `open_cognition` + `cognition_registry` / `CognitionRegistration` |
| Personae | `ember.spark.persona`'s whole `__all__` (loading, resolution, the separation wall) |
| Conversations | `ember.spark.conversation`'s whole `__all__` |
| Brunnr | `BrunnrHandle` + `open` — now also re-exported from `ember.well.brunnr` itself, mirroring Funi's shape (its `__init__` was empty; the handle module's paths were already the de-facto bind point and stay frozen too) |
| Strengr | `ember.thread.strengr`: `open`, `health`, `Opener` |
| Records | `ember.well.pending_journal` (journal, drain shapes, payload codec) and `ember.diary` (`Diary`, `diary_root`) |

Two disciplines the tests enforce beyond the list itself:
every frozen subpackage's curated `__all__` must be a subset
of the manifest (a new public name in a frozen package fails
the gate until it is frozen or unpublished), and the frozen
imports must resolve in the **default environment** — a
member on a toaster-profile install binds without the
`sqlite_vec` / `pgvector` / `mcp` extras present.

## What is NOT frozen

Named plainly, so nobody binds to it by accident: the CLI
(`ember.cli`, its flags and its printed text), the MCP
surfaces (`ember.mcp`, `ember.cli.mcp`), the session internals
(`ember.spark.munnr`, `ember.spark.hjarta`), the ingest
internals (`ember.well.smidja`), and the **concrete adapters**
— `OllamaFuni`, `AesirFuni`, `SqliteVecBrunnr`,
`PgVectorBrunnr`. Members reach backends through the frozen
`open()` registries and hold them as the frozen protocols;
an adapter class is an implementation, and implementations
may change in any release. The schemas package `__init__`
keeps its pre-freeze shape (it re-exports nothing): schemas
are frozen at their module paths, not at the package path.

## Docket 56, member half — CLOSED

E-013 found at least seven config shapes across the monorepo
and no method learned from one member transfers to another.
E-033 closed the core half (one operator config surface,
fossil keys refused). The member half closes here with the
binding rule the freeze makes possible:

- A member is configured by **its own** config shape, in its
  own home — the freeze does not impose `ember.yaml` on
  Verdandi, Kista, or any other member, and no member's
  config file becomes part of API v1.
- Where a member needs the companion, it binds through the
  API: check `is_api_compatible`, load an `EmberConfig`
  through the frozen loader (never parse `ember.yaml`
  itself), and open handles from its sub-configs through the
  frozen registries. The core's config *values* a member
  receives arrive as the frozen schema types.
- The E-013 census stands as the inventory of member shapes;
  unifying them was never the goal — a stated boundary was.

The fake-member test in `test_core_api_freeze_e037.py` binds
exactly this way (version gate → default `EmberConfig` →
typed `Unavailable` / `CognitionUnavailable` refusals from
the frozen opens → persona/conversation tagging) with no
extra installed and no config file read.

## Honest limits

- **The freeze is a contract plus tests, not machinery.**
  Nothing stops an internal caller from importing an
  unfrozen module; the manifest and its gate tests are what
  make a breach visible in this repo's own suite.
- **No member has been migrated onto the freeze yet.**
  Verdandi, the memory systems, and the rest still sit
  unwired beside the core (E-019's finding); their parts
  (IV–X) do the binding, against this contract. Claiming a
  bound member here would be inventing one.
- **Signatures are frozen by the rules above, not by
  introspection.** `verify_api_surface` proves names exist;
  the per-surface conformance suites (E-022's backend tests,
  E-024's cognition tests, and kin) are what pin behaviour.
  A signature change that keeps the name would be caught by
  those suites and by review, not by the manifest alone.
- Package version and API version will drift apart on
  purpose; the changelog discipline for telling them apart
  is Part XII's release shaping (E-198), not this slice's.

## Tests and gate

`tests/unit/test_core_api_freeze_e037.py` — **33 passed** in
the default env: version separation, the compatibility
matrix (16 cases), surface verification clean, manifest
sorted/unique/complete at 155, schema `__all__` coverage,
the seven frozen subpackages' subset gate, the tools module
surface, the not-frozen exclusions, the stdlib-only import
scan, the fresh-process laziness check, and the fake-member
binding. Slice gate Run B (default env, pgvector file
excluded): **903 passed, 6 failed, 17 skipped, 1 warning** —
870 E-036 baseline + 33 new; the 6 are the proven environment
failures. Run D (whole suite, extras supplied): **951
passed, 0 failed, 19 skipped, 1 warning**, exit 0 (918
baseline + 33 new). No README touched.
