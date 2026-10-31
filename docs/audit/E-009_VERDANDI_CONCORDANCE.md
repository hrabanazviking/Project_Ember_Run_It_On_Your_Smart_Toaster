# E-009 — The Verdandi Concordance

*Project Ember campaign, Part I (The Monorepo's True State).
Measured 2026-10-30 on branch `yrsa/ember-road-build` in the
campaign's own clone (`~/workspace/ember-build`), at campaign
commit 8cd8b75 (E-008 banked). Verdandi's own roadmap —
`Verdandi/docs/roadmap.md` (146 lines, cited as VD-RM) — was
read in full, and every claim in it was checked against the
code in `Verdandi/` (48 Python files, ~11,700 lines in the
modules named below), its config defaults, and its tests.
This slice concords only: Part IV (E-060) executes this
concordance and re-cuts Verdandi's remaining road from it.
Defects found are carried to the E-016 docket, continuing
its numbering (items 31–37). Raw inventory and the Vör
reproductions are kept under
`~/workspace/.verify-tmp/ember-e009/`.*

## Headline

**VD-RM's released version is real, and its planned version
is not.** Everything VD-RM claims for v0.3.0 "Skuld"
(RELEASED 2026-05-11) stands in the code — the predictive
check, the pre-emptive action, the emotional classifier,
maintenance windows, the 8-metric Prometheus exporter, and
the `pulse_metrics` table — and its dedicated test file
passes 35/35 in this slice. But two of the shipped features
are broken or hollow in ways VD-RM cannot show: the Vör
pre-emptive action crashes on data shapes Skuld itself
produces (docket 31, expanding E-005's item 7), and
`pulse_metrics` is a write-only table — written every
pulse, read by no code anywhere (docket 34). Everything
VD-RM plans for v0.4.0 "Valhalla" is either absent
(distributed heartbeat, REST API — no code at all) or was
already shipped in v0.3.0 and is listed as planned twice
(Prometheus, emotional architecture). And VD-RM is a
roadmap of the heartbeat only: the nerve hub, the context
injector, the conversation logger, and the Eir memory
consolidation package — the members Part IV is actually
named for — appear in it not at all (docket 36).

A dating note: the "RELEASED 2026-05-11" stamp cannot be
verified from this repo. Verdandi has exactly one commit
in the monorepo (7da4077, its 2026-05-21 import, cf.
E-002); the release predates the import. The version
itself is corroborated in-tree: `Verdandi/pyproject.toml`
and `heartbeat/__init__.py` both say 0.3.0, and an
integration test asserts it.

## The concordance table — v0.3.0 "Skuld" (claimed RELEASED)

| VD-RM claim | In code | Verdict |
|---|---|---|
| SkuldCheck — predictive health (linear regression, anomaly detection, capacity prediction, emotional classification) | `heartbeat/checks/skuld.py` (607 lines): `LinearRegression`, `AnomalyDetector`, `CapacityPredictor`, `TrendClassifier`, `SkuldCheck`; registered in `CHECK_REGISTRY` as `"prediction"` | **PRESENT** — unit-proven (see Tests); API diverges from VD-RM's sketches (docket 37); predictions run on state-derived scores, not `pulse_metrics` (docket 34) |
| Vör Action — pre-emptive healing on Skuld's predictions | `heartbeat/actions/vor_action.py` (268 lines), registered as `"preemptive_heal"`, wired by a hard-coded Reactor rule `prediction → preemptive_heal` (WARNING+) in `heartbeat/reactor.py` | **PRESENT but BROKEN** — crashes on Skuld's own `{"status": …}` capacity shape and on its no-action return path (docket 31) |
| Emotional Architecture — "7 emotional states" | `TrendClassifier` in `skuld.py`; also run per-pulse in `heartbeat/core.py` | **PRESENT, count unaccounted** — VD-RM's own v0.4 table lists 6; the `EMOTIONAL_STATES` dict holds 6; `classify()` can return 8 labels (the 6 + `moderate` + `unknown`) (docket 33) |
| Maintenance Windows — scheduled windows suppress non-critical actions | `heartbeat/core.py`: `_in_maintenance_window()` + pulse-cycle suppression of actions and named checks; defaults in `heartbeat/config.py` (`maintenance.windows: []`, `suppress_actions: true`) | **PRESENT** — 3 dedicated tests pass; the sketched Urðr integration does not exist — windows are static day/time config, no coupling to the schedule check (docket 37) |
| Prometheus Metrics — "8 metrics exposed via `/metrics`" | `heartbeat/prometheus.py` (238 lines): `MetricsRegistry` with exactly 8 metrics (`verdandi_health_score`, `health_trend`, `pulse_total`, `daemon_state`, `check_severity`, `circuit_breaker_state`, `emotional_state`, `prediction_days_to_exhaustion`); `MetricsHandler` serves `/metrics`; exporter threaded from the daemon | **PRESENT, exact count** — but off by default (`prometheus.enabled: false`, port 9101), so the endpoint exists only when a user enables it |
| `pulse_metrics` table — per-pulse health scores, trends, emotional states | `heartbeat/core.py`: created with two indexes, INSERTed every pulse in `_state_db_save()`, pruned to the last 10,000 rows | **PRESENT but WRITE-ONLY** — a tree-wide search finds no SELECT against it, ever; Skuld reads `pulse_history` instead (docket 34) |

## The concordance table — the "Original Planned Features" sketches

VD-RM reprints its original v0.3.0 plan as five numbered
sketches. Each was built — and each was built differently
from its sketch (full detail in docket 37):

1. **Predictive Health Scoring** — built, but the check is
   named `"prediction"` (sketch: class `SkuldCheck`,
   check name `"skuld"`, result `predictive:health_trend`),
   history is `hours=168` read from `pulse_history`
   (sketch: `_get_health_history(days=7)` over "the pulse
   history stored in SQLite" — the one sketch line the
   code honours in spirit), and the degrading threshold is
   slope < −0.05 (sketch: < −0.5).
2. **Anomaly Detection** — built closest to its sketch:
   rolling window 50, >2σ from the mean, exactly as drawn.
3. **Capacity Planning** — built as a generic
   `predict_exhaustion(usage_history, threshold=95%)`
   covering disk **and** memory (sketch: a disk-only
   `predict_disk_full`).
4. **Pre-emptive Healing** — built as the Vör action plus
   a hard-coded Reactor rule (sketch: a YAML reactor rule,
   trigger `predictive:health_trend`, action
   `pre_emptive_restart`, cooldown 86400 — none of those
   three names/values is the shipped one; Vör's cooldowns
   are per-action-type, 1800–86400).
5. **Scheduled Maintenance Windows** — built as static
   config windows (above); the sketch's "integrate with
   Urðr to plan maintenance during low-impact windows"
   was not built in any form.

## The concordance table — v0.4.0 "Valhalla" (claimed Planned)

| VD-RM plan | In code | Verdict |
|---|---|---|
| Distributed Heartbeat — multiple Verðandi instances sharing a nerve hub, aggregated pulse | No code: a tree-wide search finds no distributed/multi-instance/aggregation implementation. The nerve hub (`nervous_system.py`) is a single-machine Unix-socket hub (proven live locally in E-006) | **ABSENT** |
| REST API — `/api/v1/health`, `/api/v1/health/history` (authenticated) | No code: no such routes anywhere in `Verdandi/`. The only HTTP handler in the member is `/metrics`. `docs/ai-agent-integration.md` Pattern 3 prints a FastAPI *wrapper a user could write*, with different paths (`/health`, `/health/score`) — documentation of a pattern, not a shipped API | **ABSENT** (docs pattern only) |
| Prometheus Metrics Exporter | Shipped in v0.3.0 (above); the v0.4 sketch lists only 4 of the 8 shipped metric names | **ALREADY SHIPPED — listed as planned twice** (docket 35) |
| Emotional Architecture — 6-row trend→emotion table | Shipped in v0.3.0 (above); the table's 6 emotions are exactly the `EMOTIONAL_STATES` dict's 6 | **ALREADY SHIPPED — listed as planned twice** (docket 35) |

Version table (VD-RM's last section): v0.1.0 Bein /
v0.2.0 Andi / v0.3.0 Skuld are corroborated where the tree
can corroborate them — `docs/changelog-v0.2.0.md` is the
Andi changelog, and 0.3.0 is the shipped version (above).
v0.4.0 Valhöll and v1.0.0 Yggdrasil ("Production-ready")
have no code, no tag, and — for v1.0 — no stated criteria
beyond the focus word. **v1.0's "production-ready" is
undefined and NOT PROVEN in any form.**

## What VD-RM does not cover at all (docket 36)

VD-RM is a heartbeat roadmap. Named in it: nothing about
the nerve hub (`nervous_system.py`, 847 lines), the
context injector (`context_injector.py`), the conversation
logger (`conversation_logger.py`, 619 lines), the
top-level directive reactor (`reactor.py` — a different
reactor from `heartbeat/reactor.py`), the Eir memory
consolidation package (`verdandi/eir/`, 5 modules, which
carries its own `__version__ = "2.0.0"` beside the
heartbeat's 0.3.0), the `runa_*` mood/reward/negative
systems inside `heartbeat/`, or the 50-doc `research/`
corpus. Part IV (E-059) must map all of that from code;
VD-RM gives it no guidance and no completion claims to
check there — E-006's boot census (hub proven LIVE) and
E-005's baseline are the only campaign evidence so far.

## Tests as evidence

- `Verdandi/tests/test_skuld.py` — the v0.3.0 test file
  (35 tests: LinearRegression 8, AnomalyDetector 5,
  CapacityPredictor 4, TrendClassifier 8, SkuldCheck 3,
  PrometheusExporter 4, MaintenanceWindows 3) — re-run in
  this slice: **35 passed** (1 warning: `asyncio_mode`
  unknown, because `pytest-asyncio` — Verdandi's declared
  dev extra — is absent in the default env, the E-005
  environment note). Every v0.3.0 feature VD-RM claims has
  at least one dedicated passing unit test.
- The contradiction lives one layer up: the same
  features' *integration* path is broken — E-005 proved
  7 integration failures at `vor_action.py:69`, and this
  slice reproduced that crash plus two further Vör crash
  sites with synthetic contexts (docket 31). There is no
  test anywhere for Vör itself: a search of
  `Verdandi/tests/` finds the action only in one reactor
  rule-count assertion (`len(reactor.rules) == 6`).
- Suite-level Verdandi truth stands as E-005 measured it
  (539 passed / 19 failed); this slice re-ran only the
  roadmap's own test file and the Vör reproductions, and
  claims nothing wider.

## Stale sibling docs (docket 35)

VD-RM's double-listing is not the only place Verdandi's
docs disagree with its code. At least five member docs
still describe shipped v0.3.0 features as future work:
`docs/advanced-concepts.md` ("Skuld (future) is the
planned predictive module… will be implemented"),
`docs/agi-architecture-patterns.md` ("Prediction 🔜 —
(Skuld, planned)"), `docs/norse-mapping.md` (Skuld:
"Planned… Future"), `docs/integration-guide.md`
("Integration Pattern 4: Prometheus Metrics (Planned) —
Future versions will expose…"), and `docs/monitoring.md`
("Future versions will expose Prometheus-compatible
metrics"). A future reader trusting those docs would
re-plan work that shipped in May. The docs were not
edited in this slice; E-060/E-074 in Part IV own the
reconciliation.

## Carried to the E-016 docket

(31) The Vör pre-emptive action is broken in three
places, not one — expanding E-005's item 7. (a)
`should_trigger` (the E-005 line 69) and
`_get_capacity_summary` both call `.get()` on every value
in Skuld's `capacity` dict, but Skuld puts a plain string
there (`{"status": "no_resource_data"}` when no resource
data exists, `{"status": "insufficient_data", …}` below
10 history rows) — Skuld's own consumer in `_perform_check`
guards `isinstance(pred, dict)`; Vör never does.
Reproduced this slice: `AttributeError: 'str' object has
no attribute 'get'` from both sites. (b) Vör's no-action
return constructs `ActionResult(name=…, severity=
ActionSeverity.INFO, …)` — `INFO` is not a member of
`ActionSeverity` (SUCCESS/PARTIAL/FAILED/SKIPPED/DRY_RUN)
and the dataclass field is `action_name`, not `name`
(both of Vör's returns use `name=`; every sibling action
uses `action_name=`). Reproduced: the `INFO` lookup
raises `AttributeError` on the no-action path; the
`name=` error is latent behind it. (c) Vör overrides
`execute()` where every sibling action implements
`_execute()` — so it bypasses `BaseAction.execute()`'s
exception wrapper that turns action crashes into FAILED
results, and its crashes propagate into the pulse cycle
(E-005's 7 integration failures). Assigned to Part IV;
no test covers Vör today.
(32) VD-RM's v0.4.0 distributed heartbeat and REST API
are ABSENT — no code, docs pattern only for the API.
Part IV (E-060) must decide build-or-retire for both;
nothing downstream may assume they exist.
(33) The emotional architecture's state count matches
nothing: VD-RM claims 7, its own table lists 6, the
`EMOTIONAL_STATES` dict holds 6, and `classify()` can
return 8 labels (6 + `moderate` + `unknown`). Part IV
names the canonical set.
(34) `pulse_metrics` is write-only: created, indexed,
inserted every pulse, pruned at 10,000 rows — and never
read by any code in the tree. Skuld's predictions instead
derive scores from `pulse_history`'s daemon-state names
(running=100, degraded=50, critical=20…), so the per-pulse
health scores the table exists to store play no part in
prediction. Part IV decides: wire Skuld to the table, or
stop writing it.
(35) Shipped features are described as planned/future in
at least five sibling docs (named above), and VD-RM
itself lists Prometheus and the emotional architecture
as v0.4.0 plans after claiming them shipped in v0.3.0.
Part IV (E-060/E-074) owns the doc reconciliation; this
concordance is the correction of record until then.
(36) VD-RM covers the heartbeat only: the nerve hub,
context injector, conversation logger, top-level reactor,
the Eir consolidation package (own version, 2.0.0), the
`runa_*` systems, and the research corpus have no roadmap
coverage or claims. Part IV (E-059/E-060) maps them from
code alone.
(37) VD-RM's sketches diverge from the shipped API in
names, thresholds, and wiring (check name `prediction`
not `skuld`/`predictive:health_trend`; slope −0.05 not
−0.5; Reactor rule hard-coded, not the sketched YAML
rule; action `preemptive_heal`, not `pre_emptive_restart`;
maintenance windows static, not Urðr-integrated). The
code is the authority; anyone building from VD-RM's
sketches would write against the wrong contract —
E-060's re-cut must be written from the code.

## Slice gate

Root suite re-run in the E-001 shape (pgvector file
excluded, default env) as this slice's no-change gate —
see CAMPAIGN_STATE.md for the count. Doc-only slice: no
code touched, no README touched, no push. Raw inventory
and reproductions live outside the repo under
`~/workspace/.verify-tmp/ember-e009/`.

*Filed by the E-009 slice, 2026-10-30. Next: E-010 — the
Hamr verification plan.*
