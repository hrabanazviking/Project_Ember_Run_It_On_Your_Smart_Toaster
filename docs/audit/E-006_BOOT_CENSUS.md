# E-006 — Boot Census: what actually starts today

*Project Ember campaign, Part I (The Monorepo's True State).
Measured 2026-10-30 on branch `yrsa/ember-road-build` in the
campaign's own clone (`~/workspace/ember-build`), at campaign
commit 6d81a49 (E-005 banked). E-002 listed what would start if
started; this slice starts it. Every entry point found in
E-002 was probed on the VM profile, and each is graded
**BOOTS** (starts and answers), **LIVE** (a server/entry point
started, served, and was stopped cleanly), **CRASHES**,
**CANNOT BOOT HERE** (a named thing the machine lacks), or
**NO ENTRY POINT** (library/scaffolding by design). It fixes
nothing: defects found are carried to the E-016 docket.*

## Environment and method

- VM profile, Python 3.12.3, Node v24.22.1, pytest 9.1.1 —
  the same machine as E-004/E-005. No `godot`, `blender`, or
  `flask` binary/package in the default environment.
- Probes ran non-interactively (stdin closed, 8–40s timeouts)
  with `HOME` pointed at an isolated sandbox
  (`~/workspace/.verify-tmp/ember-e006/home`) and app-specific
  state redirected into the same sandbox (`--config-root`,
  `KISTA_DIR`, `MIMIR_DB_PATH`/`FACT_DB_PATH`), so no boot
  touched the operator's real state. Raw probe outputs are
  kept with the probe scripts under
  `~/workspace/.verify-tmp/ember-e006/`.
- **One sandbox artefact, disclosed:** `cryptography` on this
  VM is a *user-site* install under the real `~/.local`, so it
  is invisible under a foreign `HOME`. The kista probe below
  was therefore re-run with the real `HOME` (vault redirected
  via `KISTA_DIR`); the foreign-`HOME` failure is itself
  evidence and is reported as such.
- Three environment shapes, as in E-004/E-005: the default
  (stdlib-only) env; the with-extras shape (the core's declared
  extras from `~/workspace/.verify-tmp/ember-extras`); and the
  per-member with-deps shape (declared deps from
  `~/workspace/.verify-tmp/ember-e005-extras`, src-layout
  members given `PYTHONPATH=src`). Nothing was installed into
  the environment; no downloads were performed (in particular
  CloakBrowser's binary was never fetched).

## The boot table

| Member / entry point | Probe | Result | Grade |
|---|---|---|---|
| ember core — `--help`, no-args, `mcp list` | `python3 -m ember …`, `PYTHONPATH=src`, sandbox config root | `--help` exit 0; no-args = argparse error exit 2 (honest); `mcp list` exit 0: "No MCP servers configured" | **BOOTS** |
| ember core — `doctor`, `well status` (default env) | as above, no extras | **Traceback**: `ModuleNotFoundError: No module named 'sqlite_vec'` out of `doctor.py:49` / `status.py:24` via the adapter's top-level import | **CRASHES** (docket 13) |
| ember core — `doctor`, `well status` (with extras) | sqlite_vec extra supplied | `well status` exit 0 (creates a 112 KB well DB under the config root — boot has state-creating side effects); `doctor` exit 1, honest report: Well ok (sqlite_vec, 0 docs), Funi UNAVAILABLE — Ollama endpoint unreachable | **BOOTS** (doctor's exit 1 is the truth, not a failure) |
| ember core — `ask` on a fresh config root | `ask hello`, stdin closed | Enters the Hjarta first-run wizard, then dies with an `EOFError` traceback (exit 1) when stdin closes mid-setup | **BOOTS, wart** (docket 15) |
| Verdandi — nerve hub CLI | `nervous_system.py` no-args / `status` / `healthcheck` | No-args prints its doc, exit 0; `status` exit 0, honestly reports not-running; `healthcheck` exit 1, honestly names the 2 issues (socket + PID file missing) | **BOOTS** |
| Verdandi — nerve hub `serve` | started, probed, terminated | **LIVE**: socket file created; `status` reports Running ✅ / Responsive ✅; `healthcheck` ALL CHECKS PASSED, exit 0; `publish boot.census e006-probe` accepted as event #2 and shown by `recent`; server terminated cleanly | **LIVE** |
| Verdandi — heartbeat CLI | `python3 -m heartbeat.cli --help` / `status` | `--help` exit 0; `status` exit 0, reports daemon STOPPED with its state dir + DB path | **BOOTS** (daemon start not probed: it is a long-run server whose pulse cycle carries E-005's docketed defect 7) |
| kista — credstore CLI | `scripts/credstore.py --help` / `status`, real `HOME`, `KISTA_DIR` sandboxed | `--help` exit 0 (44 lines); `status` exit 0, honest: vault not initialised, key file MISSING | **BOOTS** |
| kista — credstore under a foreign `HOME` | same, sandbox `HOME` | `cryptography` (user-site) invisible → the script **tries `pip install cryptography` at import time** and dies with `CalledProcessError` on this PEP 668 externally-managed system | **CRASHES, latent** (docket 14) |
| mempalace — CLI | `python3 -m mempalace --version` / `--help` | exit 0: "MemPalace 3.3.5"; help lists its 15 subcommands | **BOOTS** |
| mempalace — MCP server | `python3 -m mempalace.mcp_server [--palace …]` | Default env: dies `ModuleNotFoundError: chromadb` (its declared *core* dep — ENVIRONMENT, E-005's shape fact). With deps + a cleaned `no_proxy`: starts and stays up for the full 10s probe window, silent (stdio server shape) | **BOOTS with deps** |
| mimir-well — core library | `import mimir_well.core` (`RunaMemory`, `MimirConfig`, …), `PYTHONPATH=src` | Import clean, exit 0 | **BOOTS** (library) |
| mimir-well — the Eye (Flask dashboard) | `python3 -m mimir_well.eye --port 8421`, flask from extras, DB paths sandboxed | **LIVE**: answered `HTTP 200` with the dashboard HTML; stopped cleanly. In the default env it cannot start (flask absent — ENVIRONMENT). Its shipped launcher `start-eye.sh` hardcodes `/home/pi/…` paths and cannot run here as written | **LIVE with deps** (launcher: docket 17) |
| seidr_engine — CLI | `python3 -m seidr --help`; `python3 -m seidr fornyrthislag --seed 1` | `--help` exit 0; the real run exit 0 and **composes a stanza** — boots and computes, stdlib only | **BOOTS + COMPUTES** |
| astrology-engine — CLI | `astrology_engine.py --help`; `astrology_engine.py lunar` | `--help` exit 0 (argparse loads). `lunar` prints "pyswisseph required / WARNING: pyswisseph not installed" and **exits 0 having computed nothing** — pyswisseph/kerykeion are installed nowhere and declared nowhere (the member has no pyproject) | **CANNOT COMPUTE HERE** (docket 16) |
| bifrost — library only | `from bifrost import BifrostBridge; BifrostBridge()` with `PYTHONPATH=src` | Instantiates cleanly, exit 0. No console script / `__main__` exists (E-002) — library by design | **BOOTS** (library) |
| Hamr — CLI | `python3 -m hamr.cli --help` / `version` / `check-env`, `PYTHONPATH=src` + pydantic | `--help` exit 0; `version` exit 0: "Hamr 0.8.0 — The Shape-Skin Engine"; `check-env` exit 1, honest: "Blender: ✗ Not found" (ENVIRONMENT). Like bifrost, its config sets no `pythonpath`, so the uninstalled default shape cannot start it | **BOOTS with deps** |
| Open-VTT — Godot project | `project.godot` present: config_version 5, features "4.2", main scene `res://scenes/main_menu.tscn` **exists** in-tree; `which godot godot4` = nothing | No Godot binary on the VM, so the tabletop was never launched | **CANNOT BOOT HERE** — NOT PROVEN (needs a native Godot 4.2 install; Part X) |
| CloakBrowser (vendored) — CLI | `python3 -m cloakbrowser --help` / `info`, httpx from extras | `--help` exit 0; `info` exit 0: version 146.0.7680.177.5, platform linux-x64, **Installed: False** (binary never downloaded; `install` deliberately not run) | **BOOTS** (CLI only; browser itself NOT PROVEN) |
| dictionary — Next.js app | `npm run start` in the member dir | exit 127: `next: not found` — `node_modules/` absent (Node 24 itself is present) | **CANNOT BOOT HERE** (dependency tree not installed; E-005's unmeasured row, now boot-confirmed) |
| Scaffolding dirs (`scripts/`, `tools/`, `examples/`, `deploy/`, `vendor/`) | E-002: Markdown-only shells | Nothing exists to start | **NO ENTRY POINT** |

## Findings

1. **The companion's own diagnostics crash in the project's
   default shape.** The core is stdlib-only by design, yet its
   default Well backend is the *optional* sqlite_vec extra, and
   the adapter's top-level `import sqlite_vec` (E-004 docket
   item 2) turns that into a traceback: on a machine that
   installed nothing extra, `ember doctor` — the command a
   stuck user is told to run — cannot start. With the extra
   supplied, both commands boot and report honestly (doctor's
   Funi UNAVAILABLE is the correct truth with no Ollama up).
2. **Two members are fully alive today, proven live, not
   inferred:** Verdandi's nerve hub (serve → status →
   healthcheck → publish → recent, all green against the
   running hub) and Mímir's Eye (HTTP 200 with its declared
   dep supplied). seidr_engine goes further: it is the only
   member that boots *and computes* in the bare default env.
3. **The "boots" of most members are conditional on the
   with-deps shape** (mempalace, mimir-well's Eye, Hamr), and
   two src-layout members (bifrost, Hamr) additionally need
   their `src` on the path because their configs omit the
   `pythonpath` their sibling remembered (E-005 finding 2) —
   bifrost only *instantiates*; nothing here proves a bridge
   carrying traffic (that is Part VIII's work).
4. **Three members cannot boot on this machine at all, each
   for a named reason:** astrology-engine (its compute deps
   exist nowhere and are declared nowhere — and its failure
   path exits 0), the dictionary (dependency tree never
   installed), and Open-VTT (no Godot binary; its project and
   main scene are present and correctly referenced).
5. **Import-time self-installation is a real behaviour in
   the tree:** kista's credstore, when its crypto dep is
   missing, runs `pip install cryptography` from inside the
   import and dies noisily on PEP 668 systems. On the
   author's machine the dep was always present, so the
   fallback never fired. A credential tool must fail with a
   sentence, not a pip traceback (docket 14; custody is
   Part VI's law, E-093).
6. **First-run interactivity is not EOF-safe:** the core's
   Hjarta wizard, entered automatically by `ask`/`chat` on a
   fresh root, tracebacks on closed stdin instead of exiting
   plainly (docket 15). The wizard itself *does* start and
   greet correctly up to the first prompt.

## Carried to the E-016 docket

Continuing E-005's numbering: (13) ember `doctor` / `well
status` crash in the stdlib-only env — the boot-surface
manifestation of item 2 (sqlite_vec adapter top-level
import), compounded by the default backend requiring an
optional extra; first-run diagnostics must start bare.
(14) kista's credstore attempts an import-time
`pip install cryptography` and dies with `CalledProcessError`
where the dep is absent (PEP 668) instead of a plain message.
(15) The Hjarta setup wizard raises an `EOFError` traceback
when stdin closes mid-setup (the `ask`/`chat` first-run path).
(16) astrology-engine's real commands exit 0 while printing
"pyswisseph required" and computing nothing; its compute
dependencies (pyswisseph, kerykeion) are declared in no
packaging file. (17) mimir-well's `start-eye.sh` hardcodes
`/home/pi` paths (the machine-coupling family of E-005,
launcher edition); the `python -m mimir_well.eye` path works.

## Slice gate

Root suite re-run in the E-001 shape (pgvector file
excluded, default env) as this slice's no-change gate —
see CAMPAIGN_STATE.md for the count. Doc-only slice: no
code touched, no README touched, no push. All probe state
lives outside the repo under
`~/workspace/.verify-tmp/ember-e006/`.

*Filed by the E-006 slice, 2026-10-30. Next: E-007 —
dependency & licence audit.*
