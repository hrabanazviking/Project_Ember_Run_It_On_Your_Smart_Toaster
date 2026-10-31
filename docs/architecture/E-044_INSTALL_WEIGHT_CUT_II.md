# E-044 — Install weight cut II: the dependency diet

*Part III, slice E-044. Roadmap line: "Install weight cut II:
dependency diet per E-007 (each removal/replacement measured
before/after)." This slice diets the root package's declared
dependencies — the ones a user actually installs. Member
packages' own declarations belong to their own Parts
(E-007 dockets 18/19/21 stand as assigned).*

## The diet, in plain words

**Ember's core still installs with zero dependencies — but
its optional extras were carrying three kinds of fat, and
one of them had already turned dangerous.**

- **Every extra was an open-ended promise.** Each declared
  dependency said "this version *or anything newer, forever*."
  On the morning of this slice, a fresh `pip install
  ember-agent[mcp]` quietly installed **mcp 2.3.0** — a new
  major line of the MCP SDK whose first act was to rename
  the very class Ember's MCP server is built on. A fresh
  install of a shipped feature would simply not have
  started. That is now impossible: every requirement in the
  package carries an upper bound at the next major of the
  line the code was written and tested against.
- **The test install was paying for the lint tools.**
  Installing the `dev` extra to run the tests used to drag
  in mypy and ruff as well — 89.1 MB in all, of which the
  tests themselves need 7.6 MB. The lint tools now live in
  their own `lint` extra; a test-only install is **91%
  lighter**.
- **One real feature was not installable at all.** The
  pgvector Well's keyring secret source (ADR 0010) existed
  in code but in no installable extra — an operator had to
  guess the package name and install it by hand. It is now
  the `secrets` extra — deliberately its own, because
  keyring's Linux tree weighs 16.6 MB and folding it into
  the pgvector extra would have taxed every pgvector user
  for a source only some use. The resolver's "not installed"
  message now names the extra.

Nothing was removed that a user could feel: every extra's
feature works exactly as before — the MCP feature, indeed,
works *again* on a fresh install, and this slice ran its
tests against the real bounded SDK to prove it.

## 1. Before / after (fresh installs, VM, 2026-10-31)

Method: `pip install --target <isolated dir> --no-compile`
per extra set, on the campaign VM (Python 3.12.3); the tree
weighed file by file. Scripts and raw summaries in
`~/workspace/.verify-tmp/ember-e044/`. "Before" specs are the
pre-slice pyproject declarations; "after" specs are the
shipped ones.

| Install shape | Before | After |
|---|---|---|
| core (`dependencies`) | 0 deps | 0 deps (unchanged) |
| `[sqlite_vec]` | 162,742 B, 1 pkg (sqlite-vec 0.1.9) | identical (bound added) |
| `[config]` | 2,903,826 B, 1 pkg (PyYAML 6.0.3) | identical (bound added) |
| `[pgvector]` | 20,920,005 B, 4 pkgs | identical bytes (same resolved versions, bounds added) — and *stays* this size because keyring was not folded in (see `[secrets]`) |
| `[mcp]` | 30,379,956 B, 28 pkgs — resolved **mcp 2.3.0, broken** (below) | 29,900,245 B, 29 pkgs — mcp **1.30.0**, FastMCP imports, Ember's MCP tests pass against it |
| `[secrets]` | **did not exist** (docket 20: keyring installable only by hand) | 16,646,785 B, 10 pkgs (keyring 25.7.0; 14,922,935 B of it is `cryptography`, via SecretStorage on Linux) |
| all extras combined | 54,183,654 B, 33 pkgs | 53,703,943 B, 34 pkgs (−479,711 B) |
| `[dev]` (test install) | 89,112,145 B, 14 pkgs (tests + lint tools together) | **7,600,880 B, 7 pkgs** (−81,511,265 B, −91.5%) |
| `[lint]` (new) | — (was inside dev) | the ruff + mypy shape, measured 81,511,265 B, 7 pkgs as its own install |

### The mcp breakage, proven both ways

- Before target (mcp 2.3.0, what the unbounded floor
  installs today): `from mcp.server.fastmcp import FastMCP`
  → `ModuleNotFoundError`. The 2.x SDK's own error text says
  FastMCP was renamed and advises pinning `mcp<2` to keep
  running v1 code — which is exactly Ember's position
  (ADR 0014's stdio V1 scope is written against the 1.x API).
- After target (mcp 1.30.0 under `mcp>=1.27,<2`): the import
  succeeds, and Ember's MCP test files — server, bridge,
  runner, plus the pgvector secrets tests — run **45 passed**
  with the real SDK on the path (in the default env they
  skip, as they honestly should).

## 2. What was deliberately NOT cut, and why

- **`psycopg[binary]` is 19.9 MB of pgvector's 20.9 MB.**
  Kept whole: ADR 0010 chose the binary wheel so a normal
  operator needs no system libpq installed. The pure-Python
  driver alone would cut ~19 MB and break exactly the
  people the project is for. Named here, not smuggled.
- **The `[mcp]` tree is still 29.9 MB for a stdio-only
  feature.** The SDK ships its HTTP stack (starlette,
  uvicorn, cryptography…) as hard dependencies; a package's
  deps cannot be partially installed. The diet's honest
  answer is the one already in place: MCP is an extra, off
  by default, and the core never imports it. Rewriting MCP
  against the stdlib is a Part VIII-shaped decision, not a
  diet slice.
- **PyYAML (2.9 MB) stays.** YAML config is a shipped,
  documented feature (E-033); TOML works without it, which
  is what the extra already expresses. Removing the feature
  would be amputation, not diet.
- **Bounds are not claimed as byte savings.** Except where
  the table shows bytes (the dev split, the mcp tree's small
  delta), upper bounds buy reproducibility and breakage
  armour (docket 23) — claimed as exactly that.

## 3. Docket

- **20 CLOSED** — keyring is declared (the `secrets` extra),
  and the resolver note names the install command.
- **23 root half CLOSED** — every root requirement (build
  system included: `hatchling>=1.18,<2`) is bounded both
  ways. The member half is **new docket 92**: member
  pyprojects (Verdandi, kista, mimir-well, Hamr, bifrost)
  still declare unbounded or undeclared deps per E-007 —
  each is its own Part's to bound when that Part works the
  member (IV, VI, IX, VIII respectively), alongside dockets
  18/19/21 which already assign the undeclared halves.

## 4. Tests

`tests/unit/test_dependency_diet_e044.py` — **7 tests**:
core dependencies still empty; every requirement bounded
both ways; the mcp bound excludes the breaking major; the
`secrets` extra exists, holds keyring only, and keyring is
not in `pgvector`; `dev` is test-only and disjoint from
`lint`; an AST import scan of `src/ember` matches the
extra↔import map *exactly* (no imported-but-undeclared and
no declared-but-unimported package — the E-007 orphan class
cannot return silently); and the missing-keyring resolver
note names `ember-agent[secrets]`.

Slice gate: Run B (default env, pgvector file excluded)
**948 passed, 6 proven-environment failures, 20 skipped**
(941 E-043 baseline + 7 new). Run D in a **real venv
install** of the edited package
(`pip install ".[mcp,sqlite_vec,pgvector,config,secrets,dev]"`,
which resolved mcp 1.30.0 / keyring 25.7.0 / pgvector 0.5.1 /
psycopg 3.3.6 / PyYAML 6.0.3 / pytest 9.2.0 — the bounded
lines, not today's unbounded resolutions): **1015 passed,
0 failed, 16 skipped**, exit 0 — the MCP tests run there as
real tests, not skips. One method artifact, classified not
hidden: Run D first attempted via the campaign's usual
isolated-target PYTHONPATH shape showed the 5 MCP end-to-end
tests failing, because the MCP stdio client spawns the stub
server as a subprocess with a filtered environment that
never sees the target dir. In the real install the same
5 tests pass (43 passed across the MCP + diet files) — an
ENVIRONMENT failure of the measurement shape, proven by the
venv run, not a code failure.

*Filed by the E-044 slice, 2026-10-31. Next: E-045 — idle
discipline (measured over an hour, per profile).*
