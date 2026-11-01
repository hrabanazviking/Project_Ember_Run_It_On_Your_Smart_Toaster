# E-076 — Part IV Gate: VD-RM's road accounted, contract v1 frozen

*Project Ember campaign, Part IV (Verdandi: the Nerve Hub)
— GATE. Filed 2026-11-01 on branch `yrsa/ember-road-build`
in the campaign's own clone (`~/workspace/ember-build`), at
campaign commit f27683e (E-075 banked + its push record +
this slice's IN PROGRESS marker). This gate closes Part IV
on the roadmap's own criteria for E-076: "VD-RM's remaining
road closed or re-roaded with owners; event contract
frozen; summary filed." Unlike the earlier part gates,
this slice also lands three small repairs the gate review
itself owned (docket 106, docket 92's Verdandi half, and
the docket 6 CLI-test family) — a gate that owns a bug
does not get to merely describe it. No README was
touched. Gate re-measurements were run this slice; raw
logs live in `~/workspace/.verify-tmp/ember-e076/gate/`,
and the E-075 re-verification duty's logs in
`~/workspace/.verify-tmp/ember-e076/reverify/`.*

## The gate, in plain words — read this first

**Part IV is done. The companion's nervous system — the
event hub everything in the constellation feels through —
is mapped, contracted, disciplined, and measured, and
Verdandi's own old roadmap (VD-RM) is fully accounted
for: nothing it promised is left hanging without a
verdict.** Every event now travels in one versioned
envelope (contract v1, frozen at this gate — §3). What
may be injected into a conversation, what gets logged,
who may see whose stimuli, how a flooded hub sheds load,
how events replay for debugging — each is a written law
with tests, built slice by slice in E-061–E-075. The hub
runs standalone, in one file, out of a home you can move
with a single environment variable (E-073), and its
speed is measured, not claimed: about 2,700 events a
second in its best shape on the campaign machine,
against a real demand of a few events per conversation
turn (E-075).

The three repairs this gate landed: the hub's `stop`
command no longer reports "could not be killed" for a
hub it had in fact just killed (its aliveness probe was
blind to zombie processes — docket 106, fixed and
test-proven); Verdandi's own dependency declarations are
now bounded above as well as below, like the root
package's (docket 92's Verdandi half, closed); and
Verdandi's CLI integration tests no longer assume they
run on the Pi deployment's home directory, nor judge the
host machine's health instead of the code (the docket 6
family, fixed — all five pass in seconds against an
isolated home).

Honesty, kept plain: the hub's speed on a **real**
tiny-hardware device is **NOT PROVEN** — E-075 measured
a contended VM simulation, and the real-device run is
re-roaded to the Pi endurance soak with its criteria
stated (§4, docket 107). One road VD-RM sketched —
"v1.0.0 Yggdrasil, production-ready" — was never
defined by its author; this gate defines the criteria
(§2) and gives the judgement to the campaign's final
gate, rather than declaring victory over an undefined
claim. The slice opened under the heaviest
sibling-campaign contention of the whole part (1-minute
load above 25); §5 records exactly which runs are green
and on what evidence, including the E-075 duty's
discharge.

## 1. Gate criteria — each one checked, not assumed

| # | Criterion (roadmap E-076) | Evidence | Result |
|---|---|---|---|
| G1 | Every Part IV slice E-059–E-075 banked | CAMPAIGN_STATE slice ledger, E-059–E-075 all DONE; all 18 per-slice documents E-059–E-076 present under `docs/architecture/` (pinned by this slice's conformance test) | PASS |
| G2 | VD-RM's remaining road closed or re-roaded with owners | §2: every row of E-060's re-cut table carries its final disposition; the two retirements stand, the two double-counts stand, `pulse_metrics` and Vör verified closed at their slices, v1.0.0 re-roaded with criteria | PASS |
| G3 | Event contract frozen | §3: contract v1 declared FROZEN at this gate; the freeze terms are the contract's own versioning rules (E-061 §2) | PASS |
| G4 | Part IV's docket accounted for — nothing found, nothing lost | §4: items 93–107 and the inherited items (6, 31, 33–35, 37, 65 wording, 92) each closed, fixed here, or carried with a named owner | PASS — as an accounting; the carried items remain open at their named homes |
| G5 | Full suite green before banking | §5: Run D **1362 passed, 0 failed** exit 0; Run B identical in shape to E-075's banked gate plus this slice's 7 tests; combined Part IV conformance **266 passed**; Verdandi sets **423 + 101 passed** | PASS |
| G6 | The E-075 re-verification duty discharged | §5: the duty's runs re-done at this slice's opening; the first attempt's two failures each proven a method artifact (deep-TMPDIR socket cap; cold-start at load 25+) by isolated re-runs, and the gate's own Run D — short TMPDIR, calmer load — is green with both tests inside it | PASS — on the evidence stated in §5 |
| G7 | Summary filed; the road below checked | The section above ("The gate, in plain words"), §6, and §7: no re-cut demanded; Part V inherits its named items | PASS |

## 2. VD-RM's remaining road — final dispositions

E-060 re-cut VD-RM's remainder into Part IV's order. This
gate verifies each executing slice landed and closes the
account:

| VD-RM item | E-060 verdict | Final disposition at this gate |
|---|---|---|
| Distributed Heartbeat (v0.4.0) | RETIRED (contradicts the tethering spec) | Stands retired. The local form — cross-member nerves on one machine — was built at E-067 |
| REST API `/api/v1/health…` (v0.4.0) | RETIRED as a VD-RM item | Stands retired. Its honest local form landed: contract (E-061), nerve health (E-066), standalone hub (E-073) |
| Prometheus exporter (v0.4.0 listing) | Already shipped in v0.3.0 — double-counted | Stands struck from the remaining road; its standing verification rode E-066/E-075 (the Skuld focal set is green at this gate, §5) |
| Emotional Architecture (v0.4.0 listing) | Already shipped in v0.3.0 — double-counted | Stands struck; the canonical eight labels named at E-060 §5 and carried into the member docs at E-074 |
| v0.4.0 "Valhalla" as a version | CLOSED (two shipped, two retired) | Stands closed — nothing remains under this label |
| `pulse_metrics` write-only (docket 34) | WIRE at E-066; gate verifies | **VERIFIED CLOSED.** E-066 wired Skuld to read `pulse_metrics`; at this gate a live `heartbeat.cli pulse` on the VM reported its prediction and anomaly results with `score_source: 'pulse_metrics'` (probe log in the slice evidence dir) |
| Sketch 5 remainder: Urðr-integrated maintenance windows (docket 37) | RETIRED as a sketch; static windows stand | Stands retired; static windows remain the shipped, test-proven shape |
| VD-RM sketches diverging from shipped API (docket 37) | Code is the authority | Stands; builders' reading is E-059 + E-060, reconciled for member-builders at E-074 |
| v1.0.0 "Yggdrasil — Production-ready" | NOT PROVEN, undefined; gate must close or re-road with criteria and an owner | **RE-ROADED with criteria, owner E-204** (the campaign's final gate), judged there — see below |

**The v1.0.0 criteria, defined here so E-204 judges a
stated claim, not a mood.** "Production-ready" for the
nerve hub means, all at once: (a) every Part IV slice
banked and this gate passed; (b) contract v1 frozen with
no unregistered in-tree producer (the E-061 conformance
scan green); (c) the hub's load truth measured on at
least one real tiny-hardware device (docket 107's
re-anchor, owned by E-191) — a VM simulation does not
satisfy this row; (d) no Part IV docket item open
without an owner (this gate's §4 state, maintained);
(e) the standalone hub exercised end-to-end on the
smallest proven machine in the E-199 showcase's
narrated session. Rows (a), (b) and (d) are true today;
(c) and (e) are future evidence. E-204 records the
verdict against these five rows exactly.

## 3. The event contract, frozen

**Event contract v1 is FROZEN at this gate.** Frozen
means, in the contract's own terms (E-061 §2, in
`Verdandi/event_contract.py`, `CONTRACT_VERSION = 1`):

- The canonical envelope `{v, type, data, source}`, the
  hub's stamps (`_seq`, `_ts`, `_iso`), the feed and
  256-event ring, the offline fallback shape, and the
  control protocol (`subscribe` / `ping` / `recent` /
  `ack` / `shutdown`) do not change under v1. Any
  breaking change to a registered shape is a
  **version bump** to v2, made as its own slice with
  its own conformance — never an edit under the v1 name.
- The registry as it stands at this gate includes the
  E-067 addendum (canonical `heartbeat_pulse`,
  `heartbeat_state_change`, `ember_session`,
  `ember_turn`, with the legacy heartbeat specs kept as
  the pre-E-067 feed lines' explanation) and the E-068
  addendum (the eight Hermes lifecycle/tool shapes and
  their translation, `_hermes_*` provenance preserved).
  Adding a new event type is not a bump: it is
  registered in the same change that adds its producer,
  and the conformance scan fails if it is not — that
  rule is part of the freeze.
- `source` stays optional on the wire for an operator
  publish and required for any new in-tree producer
  (E-061's rule). Making the hub stimulus-only would
  break that term; it is a v2 question, owned by the
  E-187 security audit (§4, docket 101) — the freeze is
  precisely the promise that Part IV does not smuggle
  it in.
- The docket 103 verdict is part of the frozen picture:
  contract v1 carries **no** tool-facts event. The
  `hermes.tool.*` family stays in the Hermes dialect,
  matched but never renamed (E-068); a core tool-facts
  event is a v2 candidate for E-204's presentation, not
  a v1 addition looking for a producer.

The combined conformance run at this gate (§5) re-pins
the whole registry: every Part IV conformance suite
E-061–E-076 in one run, green.

## 4. Part IV's docket — closed, fixed here, carried

Closed during Part IV (each at its slice, verified from
the state ledger): docket 93 (three dialects / two
sockets → one canonical envelope, E-061, completed
E-067), docket 94 (logger→hub coupling — in-tree half
E-067, standalone half E-073), docket 95 (reflex actions
unregistered → the reflex registry, E-065), docket 96
(the contract's `ping` a defect → the hub's real ping,
E-066), docket 97 (injector vocabulary → E-061/E-062),
docket 98 (logger's dead helper + current.json ownership
→ E-063), docket 31 (Vör broken → E-065), docket 33
(emotional set named, E-060), docket 34 (`pulse_metrics`
→ E-066, verified live at this gate, §2), docket 35
(double-listed v0.4 items struck, E-060), docket 65's
wording half (hub vs heartbeat figures settled, E-060),
docket 99 (withdrawn at E-060 as unattributable — the
number is never reused).

Fixed at this gate, in scope — the gate review owned
all three:

- **Docket 106 — CLOSED.** `Verdandi/nervous_system.py`'s
  `cmd_stop` probed aliveness with `os.kill(pid, 0)`,
  which answers True for a zombie; a hub killed by its
  SIGTERM but not yet reaped was therefore reported
  "could not be killed" (found live at E-073). The new
  `_pid_alive` probe reads the /proc state and reads a
  zombie as dead (falling back to the kill probe where
  /proc is absent). Proven by conformance tests (a real
  forked zombie; `cmd_stop` against a zombie pid file
  reports a graceful stop and clears the file) and by a
  live probe of both shapes (zombie and live sleeper) in
  this slice's evidence.
- **Docket 92, Verdandi half — CLOSED.** Verdandi's
  `pyproject.toml` declared `pytest-asyncio>=0.23` and
  `setuptools>=68.0` with no upper bound — the exact
  shape E-044 proved broken at the root (an unbounded
  floor resolves a future breaking major silently).
  Both are now bounded both ways (`<2`, `<82`), pinned
  by this slice's conformance test, which fails if any
  Verdandi requirement loses either bound. The other
  members' halves of docket 92 keep their Part VI /
  VIII / IX homes, as E-058 recorded.
- **Docket 6 family (Verdandi CLI tests) — CLOSED for
  this file.** `Verdandi/tests/test_heartbeat_integration.py`'s
  five CLI tests ran their subprocesses in
  `Path.home() / "Verdandi"` — a directory that exists
  only on the Pi deployment, so they failed on every
  other machine (the 5 failures the E-072 correction
  recorded). They now run in the member's own directory,
  derived from the test file. That exposed the family's
  second layer: `pulse` and `react` judge the host (the
  projects check scans the home directory's git repos —
  175 of them on this VM, 1m52s wall — and `pulse` exits
  1 when the pulse state is critical), so both now run
  against an isolated HOME + VERDANDI_HOME. All five
  pass in ~5 s. The rest of docket 6's family (other
  members' machine-coupled tests) keeps the homes E-005
  assigned it; this closure is for the file Part IV owns.

Carried forward, open, with a named owner each — this
gate closes Part IV on its stated criteria; it does
**not** claim these are fixed:

- **Docket 100** (Bifröst's size pruning of the
  conversation log is not session-aware) — the gate's
  stated verdict: pruning is storage hygiene, never a
  privacy mechanism; the privacy instrument is E-063's
  delete right (total and provable). Session-aware
  pruning as an enhancement is owned by **E-136**
  (Part VIII gate — Bifröst is Part VIII's member).
- **Docket 101** (the hub's open `publish` accepts
  operator events with `source` omitted) — frozen as
  contract v1 stands (§3); the stimulus-only question
  is a v2 decision owned by **E-187** (security audit).
- **Docket 102** (no typed subscriber; the core's
  bridge offers `read_recent` but chat does not consume
  nerves) — no slice in Parts V–XI builds one; first
  review at **E-085** (memory ↔ Verdandi, the next
  real consumer), backstop owner **E-204**, which must
  present it to Volmarr as a named gap if still unbuilt.
- **Docket 103** — verdict recorded at §3 (absence is
  Part IV's answer for v1); the v2 candidacy is owned
  by **E-204**'s presentation.
- **Docket 104** (already-fed memory candidates are not
  retracted when their session is deleted) — owned by
  **E-085**, as E-072 assigned; untouched by this gate.
- **Docket 105** (shipped systemd units hard-code
  `/home/pi` + `~/.hermes/state`) — deployment shape,
  owned by **E-182** (native deploy recipes,
  systemd-shaped), which rewrites the units against
  `VERDANDI_HOME` / `%h` as part of the native recipe.
- **Docket 107** (hub load truth on real tiny hardware
  NOT PROVEN; E-075's figures are a contended VM
  simulation) — owned by **E-191** (endurance soak, pi
  profile): run `Verdandi/load_truth.py`'s four
  profiles on the device and file the figures beside
  E-075's. Until then, no document may quote E-075's
  numbers as device numbers.

## 5. Gate re-measurement (E-017 method, part-gate shapes)

Measured this slice at HEAD f27683e plus this slice's
changes (unbanked at measurement time, banked by this
slice's commit), VM profile (Python 3.12.3, pytest
9.1.1), short TMPDIR (`/tmp/e076tmp` — the AF_UNIX
~108-char socket cap is why short, per E-067's lesson);
raw logs in `~/workspace/.verify-tmp/ember-e076/gate/`
(final runs: `combined2.log`, `run_b2.log`,
`run_d2.log`, `run_a.log`, `heartbeat_glob_final.log`,
`focal_conversation.log`).

| Run | Shape | Gate result |
|---|---|---|
| A | Whole suite, default env | Interrupted at collection — **1 error, 11 skipped**, exit 2 (docket 1, unchanged since the E-017 freeze) |
| B | Default env, pgvector file excluded (the slice gate) | **1305 passed, 6 failed, 25 skipped, 1 warning** — E-075's 1298 + this slice's 7; the 6 are the proven environment failures, FAILED list identical |
| D | Whole suite, extras supplied from the isolated dir | **1362 passed, 0 failed, 19 skipped, 1 warning**, exit 0 — E-075's would-be 1355 + 7 |

Part IV's own sets, same slice:

- **Combined Part IV conformance** (E-055 + E-057 pins
  + E-061–E-076 suites, 18 files): **266 passed**,
  exit 0 (E-075's combined 259 + this slice's 7).
- **Verdandi heartbeat + Skuld + integration set**
  (five files, pytest-asyncio from the e005-extras
  dir): **423 passed**, exit 0 — the canonical 374
  (heartbeat + actions + checks + Skuld) and the
  integration file's 49, in one run, on the final tree.
  An earlier run of the same set against this slice's
  intermediate tree scored 421 passed / 2 failed, the
  2 being exactly the pulse/react pair before the
  isolation half of the docket 6 fix landed; the final
  run supersedes it.
- **Verdandi conversation focal set** (context
  injector, conversation logger, reactor, nervous
  system): **101 passed**, exit 0 — identical to
  E-059–E-075.

**The E-075 re-verification duty, discharged.** E-075
banked Run D NOT GREEN under extreme contention and
left a standing duty: re-run Run D (canonical shape)
and the cold-start test before E-076. Both were re-run
at this slice's opening (`reverify/` logs). The first
Run D attempt scored **1354 passed, 1 failed** — the
one failure the E-075 load-truth live mini-run, with
"hub exited early rc=1": proven a method artifact of
this keeper's first attempt, not a regression — the
attempt ran with a deep workspace TMPDIR whose socket
paths exceed the AF_UNIX cap, so the mini-run's hub
could not bind; the identical test re-run isolated
with a short TMPDIR passed (8 passed, with the whole
load-truth file). The isolated cold-start run at
1-minute load 25.4–27.2 failed honestly (median
8.66 s vs the 5.00 s cap — the E-075 contention shape
exactly), and the same test passed inside this gate's
Run D and in the short-TMPDIR isolated re-run
(4 passed). The gate's Run D above — canonical shape,
short TMPDIR — is the duty's closing run: **green,
exit 0, both duty tests inside it**. No standing
re-verification duty carries past this gate.

The E-057 member budget table was re-measured for this
slice's Verdandi changes (hub stop probe, pyproject
bounds, CLI test file): Verdandi **193 files /
17,032,082 B**; core unchanged 130 files / 831,912 B;
total **131,443,689 B**; laptop miss **254,866 B** —
both published copies updated, as their pinning tests
require (they are inside the combined run above).

## 6. Plain-language summary (for the campaign record)

Part IV asked: *can the whole constellation feel
through one nerve system, under one contract, on tiny
hardware?* Eighteen slices answered it. Verdandi was
mapped as it actually is (E-059) and its own roadmap
was concorded and closed out (E-060). The event
contract gave every nerve one envelope (E-061);
context injection got budgets (E-062); the conversation
logger got its law and the user's delete right (E-063);
the outside world learned to knock as typed stimuli
with provenance (E-064); reflexes were registered,
bounded, and forbidden to speak (E-065); nerve health
became a real ping and an honest degradation (E-066);
the core, the heartbeat, and the logger were wired
together under the contract (E-067); the Hermes dialect
was matched and translated without renaming (E-068);
replay became deterministic (E-069); a flooded hub
learned to shed by rule (E-070); provenance stopped
leaking across personae (E-071); the logger became a
memory source only under the user's rule (E-072); the
hub stood alone (E-073); the whole model was written
for the next builder (E-074); its speed was measured
(E-075); and this gate froze the contract, closed the
roadmap's account, and fixed the three defects the
review itself owned. What Part IV did not do is prove
the hub on a real small device, give the nerves a typed
subscriber, or judge "production-ready" — each is
named, owned, and carried in §4 and §2, not buried.

## 7. The road below — checked

Part V (E-077–E-092, Memory: two systems, one verdict)
follows in roadmap order; nothing in Part IV's evidence
demands a re-cut. Part V inherits, by name: docket 104
at E-085 (logger-fed candidates vs the delete right),
docket 102's first review at E-085, and the nerve
contract as frozen law its memory crossing must obey.
Later owners named at this gate: E-136 (docket 100),
E-182 (docket 105), E-187 (docket 101), E-191
(docket 107), E-204 (docket 102's backstop, docket
103's v2 candidacy, and the v1.0.0 judgement under
§2's five criteria). The roadmap file was not edited
by this gate.

## Carried forward

- Part IV is CLOSED by this gate. Next: E-077
  (Part V) — both memory systems mapped.
- Open and carried, not lost: docket 100 (→ E-136),
  101 (→ E-187), 102 (→ E-085 review, E-204 backstop),
  103's v2 candidacy (→ E-204), 104 (→ E-085),
  105 (→ E-182), 107 (→ E-191), VD-RM v1.0.0
  "Yggdrasil" (→ E-204, criteria at §2).
- NOT PROVEN at this gate: hub throughput on real
  tiny hardware; a typed nerve subscriber; the
  v1.0.0 "production-ready" claim — each with its
  owning slice named above.

*Filed by the E-076 slice, 2026-11-01. Part IV gate:
PASS. Next: E-077 — both memory systems mapped
(Part V opens).*
