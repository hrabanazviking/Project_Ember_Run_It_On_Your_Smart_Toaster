# E-007 — Dependency & Licence Audit

*Project Ember campaign, Part I (The Monorepo's True State).
Measured 2026-10-30 on branch `yrsa/ember-road-build` in the
campaign's own clone (`~/workspace/ember-build`), at campaign
commit 42be1c7 (E-006 banked). Every licence file in the tree
was read and hash-checked; every packaging file was parsed;
and the actual third-party imports of each member's Python
code were scanned (AST walk) and compared against what that
member declares. It fixes nothing: defects found are carried
to the E-016 docket, continuing its numbering (items 18–25).*

## Headline

**The licence estate is permissive and intact — with one
proprietary trap, and it is exactly where the roadmap said to
look: the vendored browser's binary.** Every member licence
file present is complete standard text (MIT grant + warranty
clause verified in all 11 MIT files; astrology-engine carries
full Apache-2.0). No copyleft licence file exists anywhere in
the tree. But CloakBrowser is *two* licences, not one: the
wrapper is MIT, while its compiled Chromium binary — not in
this tree — is proprietary under `BINARY-LICENSE.md`, which
forbids redistributing or bundling the binary into a product
distributed to third parties without a separate OEM licence.

**The dependency estate is the weaker half:** declarations
and reality disagree in four places (astrology-engine declares
nothing at all; Verdandi's Eir layers import `yaml` hard and
undeclared; the core's `keyring` is optional-by-design but
declared in no extra; Hamr lazily imports undeclared
`psutil`), and only one member (mempalace) carries a Python
lockfile.

## Method

- Licence inventory: filename scan for `*license*`,
  `*licence*`, `*copying*`, `*copyright*`, `*notice*` across
  the whole tree (excluding `.git`) — 19 hits, including the
  two image files named `MIT_license_Rune_Forge_AI.jpeg`
  (pictures of a licence, in `assets/` and `Verdandi/`).
- Each licence file's text was checked for its licence's
  load-bearing phrases (MIT: "Permission is hereby granted"
  + "THE SOFTWARE IS PROVIDED"; Apache: full 2.0 terms) and
  sha256-recorded (prefixes in the table).
- Dependency inventory: every `pyproject.toml`,
  `package.json`, `setup.py`, lockfile (`uv.lock`,
  `package-lock.json`, `yarn.lock`, `bun.lock`, `flake.lock`)
  parsed or counted. Raw inventories are kept under
  `~/workspace/.verify-tmp/ember-e007/`.
- Import scan: AST walk of each member's Python (source +
  tests), stdlib and local modules removed; what remains is
  what the code actually asks the environment for.

## The licence table

| Holder of the file | Licence | Bytes | sha256 (prefix) | Verdict |
|---|---|---|---|---|
| root `LICENSE` — © 2026 Volmarr Wyrd | MIT | 1,069 | c006b7010fa0 | intact, complete |
| `Verdandi/LICENSE` — © Volmarr Wyrd & Runa Gridweaver Freyjasdottir | MIT | 1,103 | 2b549b401afc | intact |
| `kista/LICENSE` — © Runa Gridweaver | MIT | 1,071 | eff52e4122e2 | intact |
| `mempalace/LICENSE` — © MemPalace Contributors | MIT | 1,079 | 81dc6cc278d8 | intact |
| `mimir-well/LICENSE` — © 2024 Eldrä Járnsdóttir | MIT | 1,076 | cef774bbcd0d | intact |
| `seidr_engine/LICENSE` — © Runa Gridweaver Freyjasdóttir | MIT | 1,086 | 80bc0ad81c4b | intact |
| `bifrost/LICENSE` — © 2025 Runa Gridweaver & Volmarr Viking | MIT | 1,088 | 35b8fe910f42 | intact |
| `Hamr/LICENSE` — © Runa Gridweaver Freyjasdottir & Volmarr | MIT + a 7-line poetic coda after the warranty clause | 1,276 | 063972d5e6f1 | intact (coda adds words, removes nothing — diffed against root) |
| `CloakBrowser/LICENSE` — © 2026 CloakHQ | MIT (wrapper) | 1,064 | 93a9c5b5542f | intact — vendored licence verified, untouched |
| `CloakBrowser/BINARY-LICENSE.md` — © 2026 CloakHQ | **Proprietary** (the compiled binary only) | 7,825 | 98e5039b37b8 | intact — see below |
| `Open-VTT/LICENSE` — © 2023 Khazlor | MIT | 1,064 | eb74f6b325ba | intact — upstream-copyright member, not marked vendored in ORIGINS (E-003) |
| `cleasby-vigfusson…/LICENSE` — © 2020 Sampo Silvennoinen | MIT | 1,075 | 5dfd5a522545 | intact — upstream-copyright member; the underlying 1874 dictionary text is public domain per the member's own footer |
| `astrology-engine/LICENSE` | **Apache-2.0** (full text) | 11,358 | cfc7749b96f6 | intact — the tree's only non-MIT member licence; permissive, MIT-compatible for Ember's use |
| root `NOTICE` / `THIRD_PARTY_NOTICES.md`; astrology `NOTICE` / `LEGAL-NOTICE.md`; root `LEGAL-NOTICE.md` | notices, not licences | 367 / 743 / 267 / 3,269 / 3,250 | — | astrology's pair is current; the root pair is **stale** (docket 24) |

No other licence, copying, or copyright files exist in the
tree. No source file anywhere carries an SPDX header (0 files
in the scanned Python) — licences live only in these files.
GPL/AGPL appear only as *discussion* in the elder codices
(TASK_RAGNAROK_CODEX: external GPL-3.0 project, "vendoring
would force GPL on Ember — avoid"; TASK_SUPER_AGENT_PARTY:
AGPLv3 "cite, do not vendor") and in the waifu codex's
study-only verification doc — the contamination the codices
warn about is **not present in the tree**; their posture is
already the campaign's.

### The CloakBrowser binary licence (the one real trap)

Read in full (`CloakBrowser/BINARY-LICENSE.md`, v1.0, Feb
2026). It applies only to the compiled Chromium binary
distributed via CloakHQ's own channels — *not* to the wrapper
source in this repo (MIT, above). Its load-bearing terms:

- Use, personal or commercial, is free; **listing
  CloakBrowser as a dependency is expressly not
  redistribution** (end users download the binary from
  CloakHQ themselves) and needs no commercial licence.
- **Redistribution, resale, repackaging, or including the
  binary in any product or service distributed to third
  parties is prohibited**; bundling/embedding/pre-installing
  it into a distributed product — or running it on your own
  infrastructure to serve third-party customers — **requires
  a separate OEM/SaaS licence** (contact in the file).
- No modification, no reverse engineering, no trademark
  grant; acceptable-use bans (credential stuffing, unauthed
  access, fraud) bind any future Ember browser use (Part XI,
  E-178's ladder inherits them).

Current state is lawful and clean: the binary is **not in
the tree** (E-006 proved `Installed: False`; the campaign has
never downloaded it). This is not a violation — it is a
release-shape constraint, carried as docket 25 for Part XI
(E-175–E-179, E-185): Ember may *depend on* CloakBrowser, it
may never *ship* the binary without CloakHQ's OEM word.

## The dependency table

| Member | Declared core deps | Optional / dev | Lockfile | Pinning shape |
|---|---|---|---|---|
| ember core (root) | **none** (stdlib only — verified by import scan: every third-party import sits under an extra or the lazy keyring path) | extras: sqlite-vec; pyyaml (`config`); psycopg[binary] + pgvector (`pgvector`); mcp (`mcp`); dev: pytest, pytest-cov, ruff, mypy | none | all `>=`, no upper bounds |
| Verdandi | **none declared** | dev: pytest-asyncio only | none | — (but see docket 19: reality differs) |
| kista | cryptography (unpinned, no floor) | — | none | bare name |
| mempalace | chromadb `>=1.5.4,<2`, pyyaml `>=6,<7`, tomli (py<3.11) | spellcheck: autocorrect; gpu/dml/coreml: onnxruntime variants; dev set | **uv.lock — 122 packages, hashed** (821 KB) + website `bun.lock` | the tree's only bounded + locked Python member |
| mimir-well | flask `>=3.0` | — | none | `>=` only |
| seidr_engine | none | — | none | genuinely stdlib-only (scan-clean) |
| astrology-engine | **no packaging file exists at all** | — | none | see docket 18 |
| bifrost | none | huginn, muninn extras (both unpinned bare names — neither is a PyPI-resolvable public package name in-tree; they are constellation-internal); dev: pytest, pytest-cov | none | imports of both are lazy + guarded in `core.py` (the E-005 test-guard defect is the tests', not the library's) |
| Hamr | numpy, Pillow, pyyaml, click, pydantic, rich (all `>=`) | blender extra: empty (Blender is external by design); dev: pytest, pytest-cov, mypy, ruff | none | `>=` only |
| CloakBrowser (vendored) | playwright, httpx | geoip: geoip2 + socksio; patchright; serve: aiohttp + websockets; dev | JS: `package-lock.json` (215 packages); `flake.lock` | JS lock licences, from the lock metadata: 178 MIT, 13 ISC, 10 Apache-2.0, 6 BSD-2, 4 BSD-3, 4 BlueOak-1.0.0, 1 0BSD — **all permissive, no copyleft** |
| dictionary | package.json: 19 runtime deps (next 16.1.6 and react 18.3.1 pinned exactly; the rest `^`) | 27 dev deps | `yarn.lock` (1,063 resolved entries; yarn v1 format records no licence fields — per-package licences **not verifiable from the lock**) | mixed |
| Open-VTT | no packaging (Godot project; engine is an external native tool) | — | none | n/a |

Also noted: `src/ember/spark/munnr/setup.py` matches the
`setup.py` filename but is the Hjarta setup *command*
module, not packaging — a naming collision for future
auditors, not a defect. Dockerfiles exist only inside the
vendored member (`CloakBrowser/Dockerfile` + one example) —
never used, per campaign law; `deploy/` is Markdown shells
(E-002), audited properly at E-181.

## Declarations vs reality (import scan)

1. **astrology-engine imports five third-party packages and
   declares none:** `swisseph` (pyswisseph), `kerykeion`,
   `geopy`, `timezonefinder`, `pytz` — all lazily imported
   and guarded in code (the engine degrades instead of
   crashing, which is why E-006 saw warnings, not tracebacks),
   but no `pyproject.toml`, `requirements`, or any other
   declaration exists to install them from. This is docket
   16's declaration half, now fully itemised (docket 18).
2. **Verdandi's Eir layers import `yaml` at module top
   level, unguarded** (`verdandi/eir/layers.py:16`), and
   Verdandi declares no `pyyaml` anywhere — on a machine
   without PyYAML (which the core itself makes merely an
   optional extra), importing the Eir layers dies outright.
   The same member shows it knows the disciplined pattern:
   `heartbeat/config.py` guards its yaml import with a
   fallback parser, and `heartbeat/cli.py` imports yaml
   lazily (though its `except NameError` fallback can never
   catch the `ImportError` a missing yaml would raise at
   that line — wart, noted for the docket). Verdandi's tests
   also import yaml unguarded. Eir's `muninn`/`huginn`
   imports are lazy and try-guarded — clean (docket 19).
3. **The core's `keyring` is a declaration orphan:**
   `well/brunnr/pgvector/secrets.py` lazily imports it, by
   design (ADR 0010: "keyring is *optional*"), and degrades
   with an honest note when absent — good code, but **no
   extra in the root pyproject installs it**, so an operator
   who wants the keyring secret source must discover and
   install the package by hand, undocumented by the
   packaging (docket 20).
4. **Hamr imports `psutil` in two core modules**
   (`core/gpu_profiles.py`, `core/benchmark.py`) — lazily,
   `ImportError`-guarded, with /proc fallbacks: graceful,
   but undeclared; and its `tests/test_packaging.py` falls
   back to `tomli` on Python < 3.11, also undeclared in its
   dev extra, on a member that claims `>=3.10` support
   (docket 21).
5. **Licence metadata disagrees with licence files:**
   `kista/pyproject.toml` declares **no license field** (its
   LICENSE is MIT); the dictionary's and mempalace-website's
   `package.json` files declare **no license field** (the
   dictionary's LICENSE is MIT); astrology-engine has no
   packaging metadata at all. Tooling that reads metadata —
   registries, licence scanners, the E-185 estate table —
   will report these members as unlicensed until the fields
   agree with the files (docket 22).
6. **Clean members, said plainly:** seidr_engine (stdlib
   only, declared and real), mimir-well (flask declared and
   its only third-party import), mempalace (every scanned
   import maps to a declared core/optional dep), CloakBrowser
   wrapper (scanned imports map to its declared deps/extras),
   and the ember core's *declared* shape (zero core deps is
   true of the code as scanned).

## Reproducibility & weight (feeds Part III)

Outside mempalace, **no Python member is locked and almost
nothing is upper-bounded** — a fresh install of the core's
extras, kista, mimir-well, Hamr, or CloakBrowser resolves to
whatever is newest that day. For a project whose soul is
tiny, predictable installs on small machines, the diet work
is already scoped: E-044 (dependency diet per this audit)
inherits the unbounded list above, and the dictionary's
1,063-entry yarn tree is the monorepo's largest single
install weight (its licences, per above, are verifiable
only package-by-package, not from its lock).

## Carried to the E-016 docket

(18) astrology-engine declares no dependencies anywhere and
has no packaging file: pyswisseph, kerykeion, geopy,
timezonefinder, pytz are all code-guarded but
install-invisible (the declaration half of item 16; Part VII
owns the fix shape). (19) Verdandi: `verdandi/eir/layers.py`
imports yaml top-level unguarded while pyyaml is declared
nowhere in the member (its tests import it unguarded too);
`heartbeat/cli.py`'s yaml fallback catches NameError where
ImportError is the real failure. (20) The ember core's
optional `keyring` secret source (ADR 0010) is declared in
no extra — lazy and graceful in code, undiscoverable from
the packaging. (21) Hamr: undeclared lazy `psutil` in two
core modules (guarded, /proc fallback) and undeclared
`tomli` in its packaging test's <3.11 fallback. (22)
Licence-metadata gaps: kista pyproject, dictionary
package.json, and mempalace-website package.json declare no
license field despite MIT LICENSE files standing beside two
of them. (23) No Python lockfile outside mempalace and
near-universal unbounded `>=` ranges — fresh installs are
unreproducible by construction (Part III / E-044 inherits).
(24) The root licence estate is stale for release:
`THIRD_PARTY_NOTICES.md` still names "Runa Agent"/"HERETIC"
(E-003) and, despite its own promise to record *every*
third-party dependency, contains **zero entries**; root
`NOTICE` likewise still names Runa Agent and its old repo —
the estate table E-185 must ship cannot be built from these
files as they stand. (25) CloakBrowser's **binary** licence
(proprietary, CloakHQ): Ember may depend on the wrapper and
let users fetch the binary from CloakHQ, but may never
redistribute or bundle the binary into a distributed
product without an OEM/SaaS licence — a release-shape
constraint for Part XI, not a present violation (the binary
is absent from the tree and has never been downloaded by
this campaign).

## Slice gate

Root suite re-run in the E-001 shape (pgvector file
excluded, default env) as this slice's no-change gate —
see CAMPAIGN_STATE.md for the count. Doc-only slice: no
code touched, no README touched, no push. Raw inventories
and scan scripts live outside the repo under
`~/workspace/.verify-tmp/ember-e007/`.

*Filed by the E-007 slice, 2026-10-30. Next: E-008 — the
codex census.*
