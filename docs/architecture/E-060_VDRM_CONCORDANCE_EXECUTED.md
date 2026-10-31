# E-060 — The VD-RM Concordance Executed

*Part IV, slice E-060. This slice executes the E-009 concordance:
Verdandi's own roadmap (`Verdandi/docs/roadmap.md`, VD-RM) is
checked item by item against reality one final time, its completed
claims are verified by tests run this slice, and everything it
left remaining is re-cut into Part IV's order (E-061–E-076) with
an owner for every item. VD-RM itself was not edited — this
document is the correction of record until E-074 reconciles the
member docs. No code and no README was touched in this slice.
Starting HEAD: eb3d440's parent 669655d (E-059 banked + corrected).
Evidence kept under `~/workspace/.verify-tmp/ember-e060/`.*

## 1. Plain-language summary

Verdandi's own roadmap promised one finished version and one
planned version. The finished one (v0.3.0 "Skuld") is real: its
test file passes 35 out of 35 again today, and the wider
heartbeat test set passes 374 out of 374. One part of it is still
broken — the Vör pre-emptive healing action crashes on the very
data the prediction check produces — and that repair now has a
named home (E-065). The planned version (v0.4.0 "Valhalla") is
closed out in this slice: two of its four items were already
shipped inside v0.3.0 (Prometheus metrics, the emotional
architecture), and the other two (a distributed heartbeat, a
REST API) are **retired** — not built, not silently dropped, but
struck with reasons (§4). A companion tethered to one person on
one small machine (E-020) does not need its heartbeat spread
across several machines, and Part IV's local event contract
(E-061) plus nerve health (E-066) do the honest local part of
what the REST API sketch wanted. The emotional states are named
canonically (§5: eight labels the code can actually return, not
the "7" VD-RM claimed), the budget-wording tangle is settled
(§6: the hub and the heartbeat are different programs with
different measured sizes — 21.9 MiB live and 18.4 MiB
import-level on the VM, E-041 — and every future document must
say which one a number prices), and the write-only
`pulse_metrics` table gets a decision (§4: it will be wired as
the prediction check's real history source at E-066, not left
written-and-never-read).

## 2. Completed claims — verified by tests this slice

Every v0.3.0 claim from E-009's concordance table was re-verified
against the code (present, at the E-009 paths) and by the runner:

- `Verdandi/tests/test_skuld.py` — the roadmap's own test file
  (LinearRegression, AnomalyDetector, CapacityPredictor,
  TrendClassifier, SkuldCheck, PrometheusExporter,
  MaintenanceWindows): **35 passed**, 1 warning (the known
  `asyncio_mode` environment note), identical to E-009.
- The wider focal set — `test_skuld.py` +
  `test_heartbeat_actions.py` + `test_heartbeat_checks.py` +
  `test_heartbeat.py`: **374 passed, 0 failed** in three
  consecutive serial runs. One earlier combined run, taken while
  other commands ran in parallel on this VM, scored 371 passed /
  3 failed; its log captured only the tail, the three failures
  were never identified, and they did not reproduce in any of the
  three serial re-runs. That is recorded as an unreproduced
  flake, not hidden — docket 99, with its re-open rule.
- Claim-by-claim: SkuldCheck (registered `"prediction"`),
  maintenance windows (3 dedicated tests in the 35), the
  exactly-8-metric Prometheus exporter (4 dedicated tests; the
  8 names as E-009 listed them), and the emotional classifier
  (8 dedicated tests) all stand as E-009 found them.
  `pulse_metrics` stands too — as a table that is created,
  indexed, inserted every pulse, and pruned at 10,000 rows
  (`heartbeat/core.py:684–765`); a tree-wide search this slice
  re-confirms **no code SELECTs from it** outside its own prune
  subquery. Write-only, as docketed (34) — decision in §4.
- Absence claims re-verified this slice: a search of
  `Verdandi/**/*.py` finds **no** distributed/multi-instance
  heartbeat code and **no** `/api/v1` route anywhere. The two
  v0.4.0 items were absent in E-009 and are absent still.

## 3. Vör — the one broken shipped feature, re-proven

Docket 31 stands exactly as written. Reproduced this slice with
synthetic contexts (script in the evidence dir):

- `should_trigger` on Skuld's own string capacity shape
  (`{"status": "no_resource_data"}`) crashes:
  `AttributeError: 'str' object has no attribute 'get'`.
- The no-action path of `execute()` crashes:
  `AttributeError: type object 'ActionSeverity' has no attribute
  'INFO'` — and behind it, both returns construct
  `ActionResult(name=…)` where the dataclass field is
  `action_name`.
- Structurally, `VörAction` defines its own `execute()` and no
  `_execute()` — so it bypasses `BaseAction.execute()`'s
  crash-to-FAILED wrapper every sibling action runs under.

No test covers Vör (E-009's finding stands). The repair contract
is fixed here and owned by **E-065** (the reflex layer — the
actions that fire below cognition are exactly the ones that must
never crash the pulse): guard non-dict capacity values the way
Skuld's own consumer does; return `ActionResult` with
`action_name=` and a real severity member; implement
`_execute()` instead of overriding `execute()`; and land the
first Vör tests (trigger on the string shape, no-action return,
one real pre-emptive path) in that slice.

## 4. The remaining road, re-cut into Part IV's order

VD-RM's remaining items × their verdicts and owners. "Retired"
means struck from the road by this concordance, with the reason
stated — reopening any of them is a new commission, not a
continuation of VD-RM.

| VD-RM item | Verdict | Owner / home |
|---|---|---|
| Distributed Heartbeat (v0.4.0) | **RETIRED.** Absent (re-verified §2). It contradicts the tethering spec (E-020: one person, one machine, local sockets); the in-scope form of "instances feeling each other" is cross-*member* nerves on one machine | The local form is E-067's work; multi-machine is nobody's slice |
| REST API `/api/v1/health…` (v0.4.0) | **RETIRED as a VD-RM item.** Absent (docs wrapper pattern only, E-009). What it wanted — health visible, history readable — is served locally by the event contract and nerve health; a remote HTTP surface on tiny hardware is a security and budget decision VD-RM never made | Local form: E-061 (contract) + E-066 (nerve health) + E-073 (standalone hub) |
| Prometheus exporter (v0.4.0 listing) | **ALREADY SHIPPED in v0.3.0** — struck from the remaining road as double-counted (docket 35) | Standing verification rides E-066 / E-075 |
| Emotional Architecture (v0.4.0 listing) | **ALREADY SHIPPED in v0.3.0** — struck as double-counted; canonical set named in §5 (docket 33 closed as a naming) | Doc wording fixed at E-074 |
| v0.4.0 "Valhalla" as a version | **CLOSED.** Two items shipped under v0.3.0, two retired above; nothing remains under this label | — |
| v1.0.0 "Yggdrasil — Production-ready" | **NOT PROVEN, undefined.** VD-RM states no criteria beyond the focus word; no slice in Part IV can close an undefined claim | E-076 gate must close it or re-road it with criteria and an owner (its natural home is Part XII's final gate) |
| Sketch 5 remainder: Urðr-integrated maintenance windows (docket 37) | **RETIRED as a sketch.** Windows as shipped are static day/time config and test-proven (§2); no consumer needs schedule-check coupling, and the code is the authority over the sketch | Static windows stand as the shipped shape |
| `pulse_metrics` write-only (docket 34) | **WIRE, don't stop.** The table stores exactly the per-pulse health score / trend / emotion the prediction check needs; Skuld today derives scores from `pulse_history`'s daemon-state names instead | **E-066** wires Skuld to read `pulse_metrics` as its health-history source, with tests; E-076 gate verifies the closure |
| VD-RM sketches diverging from shipped API (docket 37) | **Code is the authority** — check name `prediction`, slope −0.05, hard-coded Reactor rule, action `preemptive_heal`, static windows. The sketches are struck as a building source | Builders use E-059 + this doc; doc reconciliation at E-074 |

And the concordance's other open items, confirmed in Part IV's
existing order (E-059 §8 and the E-016 docket agree):

- Docket 93 (three event dialects / two sockets) + 97 (injector
  vocabulary) → **E-061** event contract v1.
- Docket 36's uncovered members take their road from E-059's
  map: injector discipline **E-062**, logger law 98 → **E-063**,
  reflex layer 31 + 95 → **E-065**, nerve health 96 + 34 →
  **E-066**, deployment coupling 94 → **E-067 / E-073**,
  Hermes dialect **E-068**, replay **E-069**, backpressure
  **E-070**, privacy **E-071**, logger-as-memory **E-072**,
  member-builder docs **E-074**, load truth **E-075**, gate
  **E-076**.

## 5. The canonical emotional set (docket 33 — named)

The code is the authority, and the code can return **eight**
labels from `TrendClassifier.classify()`:

- the six of the `EMOTIONAL_STATES` dict — `contentment`,
  `concern`, `acceptance`, `urgency`, `anxiety`, `hope` (these
  are VD-RM's v0.4 table's six, and the shipped architecture);
- `moderate` — the default when data exists but no named state
  matches;
- `unknown` — when there is no data at all.

VD-RM's headline "7 emotional states" matches nothing and is
struck. Any document, exporter label, or test written from here
uses the eight above; E-074 corrects the member docs.

## 6. Budget-wording settlement (docket 65, wording half)

E-041 measured the two programs separately, and this slice
settles the wording every later document must use:

- **The nerve hub** (`nervous_system.py`) is one program; its
  measured figure is **21.9 MiB live** (VM, E-041).
- **The heartbeat** (`heartbeat/`) is a different program; its
  measured figure is **18.4 MiB import-level** (VM, E-041) — a
  floor, not a running cost.
- The elder documents' figures (~1 MB hub in the README
  comparison table, ~13 MB / ~15 MB heartbeat, ~15–25 MB Pi
  guide, <50 MB research target, ~30 MB proposal matrix) are
  **unmeasured claims, superseded by the two measured figures
  above** wherever they overlap; no document may quote a
  Verdandi size without naming which program it prices. The
  editing itself is E-074's; this section is the verdict it
  executes. The README is never edited by this campaign — its
  ~1 MB comparison line stands recorded as contradicted by
  measurement, correction of record here.

One further wording verdict E-059 passed to this slice:
`heartbeat/checks/base.py`'s docstring orders severity
"OK < WARNING < CRITICAL < UNKNOWN", but its own comparator
ranks UNKNOWN at −1 — below OK — and `worst_severity` ignores
UNKNOWN unless it is alone. **The comparator is the
behaviour**; the docstring is wrong wording, corrected at
E-074, verdict recorded here.

## 7. Stale sibling docs (docket 35 — re-verified)

Still stale this slice, each describing shipped v0.3.0 work as
future: `docs/advanced-concepts.md` ("Skuld (future) is the
planned predictive module"), `docs/agi-architecture-patterns.md`
("Prediction 🔜 — (Skuld, planned)"),
`docs/norse-mapping.md` (Skuld: "Planned… Future"),
`docs/integration-guide.md` ("Integration Pattern 4:
Prometheus Metrics (Planned) — Future versions will expose…"),
`docs/monitoring.md` ("Future versions will expose
Prometheus-compatible metrics"). VD-RM's own double-listing is
settled in §4. All five files are E-074's reconciliation list;
until then, E-009 + this document are the correction of record.

## 8. New docket item

(99) The Verdandi focal set (skuld + heartbeat actions /
checks / heartbeat, 374 tests) scored 371 passed / 3 failed in
one run taken under parallel command load on the VM, then
374 passed in three consecutive serial runs; the failing
tests were not captured (tail-only log) and are unidentified.
Class: UNRESOLVED flake. Re-open rule: any future focal or
gate run that fails in this set must capture the full log and
name the tests before the count is banked; if the same tests
recur, the flake becomes a defect with a Part IV owner.

## 9. Slice gate

- Focal Verdandi proof (§2/§3): `test_skuld.py` **35 passed**;
  the four-file focal set **374 passed, 0 failed** in three
  consecutive serial runs (one earlier parallel-load run scored
  371/3, unreproduced — docket 99). Vör reproductions in §3 from
  the evidence dir's script.
- Root suite gate (doc-only slice): Run B **1054 passed,
  6 failed, 25 skipped, 1 warning** — the 6 are the proven
  environment failures, identical to E-058/E-059; Run D
  **1111 passed, 0 failed, 19 skipped, 1 warning**, exit 0 —
  identical to E-058's Run D. Logs in
  `~/workspace/.verify-tmp/ember-e060/gate/`.
- Doc-only slice: no code touched, no README touched. New
  docket item 99 (§8); docket 31, 33, 34, 35, 37 and 65's
  wording half are settled or given executing owners above —
  none is closed by a doc edit in this slice, and E-076's gate
  must verify each executing slice landed.

*Filed by the E-060 slice, 2026-10-31. Next: E-061 — event
contract v1.*
