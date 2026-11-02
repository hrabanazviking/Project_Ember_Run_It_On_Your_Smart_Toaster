# E-065 — The Reflex Layer: Fast, Dumb, Safe Reactions Below Cognition

*Part IV, slice E-065. Method: every reflex named below was
re-read from code this slice (the heartbeat Reactor and its
six rules, the five actions in `heartbeat/actions/`, the
BaseAction wrapper, Skuld's capacity shapes, and the
top-level conversation reactor). The discipline itself
lives in code at `Verdandi/reflexes.py`; this document is
its reading copy. Conformance is pinned by
`tests/unit/test_reflex_layer_e065.py`.*

## 1. Plain-language summary

Below the companion's thinking there is a layer that does
not think at all. When the heartbeat's senses report
something wrong — a disk filling, a database corrupt, a
service down, a prediction turning bad — a small set of
fixed rules fires small pre-written reactions: clean up,
restart, heal, push the project's own work to safety. That
layer is now registered, bounded and repaired. Every
reflex in the tree is named in one register with its
trigger, its floor and its cooldown; every reflex fires
only at WARNING or above, only through the one safety
wrapper, and only ever leaves a technician's record of
what it did. A reflex never speaks for the companion — it
has no voice, produces no dialogue, and addresses no one;
it acts on the machine and writes a record, and that is
all. The one reflex that was broken — Vör, the
pre-emptive healer, which crashed on the very prediction
data it exists to answer — is repaired and has its first
tests. And the conversation reactor's `--focus` switch,
which for its whole life accepted a focus and silently
ignored it, now actually filters.

## 2. What a reflex is — the three words made testable

A reflex is a reaction below cognition: a sensor result
(a heartbeat check result, in E-064's terms a
`sensor.check:*` stimulus) crosses a fixed severity
threshold, a fixed rule matches, and one pre-written
action runs.

- **Fast.** The decision is a deterministic rule match
  (check name + severity + optional detail conditions)
  inside the pulse cycle. No model is consulted, no
  retrieval is performed, nothing from the companion
  core (`src/ember`) is imported. The same check results
  always match the same reflexes — `reflexes_for_trigger`
  in `reflexes.py` is that match, stated purely.
- **Dumb.** The rule is fixed at build/config time. A
  reflex does not choose its trigger, widen its reach,
  learn a new action, or invent one. An action that is
  not in the register is not a reflex; adding one means
  registering it, with its floor and cooldown stated.
- **Safe.** Four bounds, all pinned by tests: the floor
  is WARNING (OK and UNKNOWN fire nothing); the action
  runs through `BaseAction.execute` — the wrapper that
  honours dry-run, measures duration, registers the
  cooldown and folds any exception into a FAILED result
  instead of crashing the pulse; a positive cooldown
  bounds how often it may fire; and its output is one
  `ActionResult` record (see §4).

## 3. The register — every reflex in the tree

The heartbeat Reactor carries exactly six rules, mapping
five checks onto five actions. The register in
`Verdandi/reflexes.py` (`REFLEX_SPECS`) states each one;
the conformance tests re-derive the action registry, each
class's declared trigger/severity/cooldown, and the
Reactor's rule set from the code and pin them equal to
the register, so the register cannot drift from the tree.

| Reflex (`name`) | Trigger check(s) | Floor | Effect | Cooldown |
|---|---|---|---|---|
| `auto_push` | projects | warning | commit and push the project's own dirty/unpushed repos | 3600 s |
| `auto_restart` | schedule | warning | restart crashed or inactive systemd services | 600 s |
| `auto_cleanup` | memory, health | warning | prune logs and temp files, vacuum databases | 7200 s |
| `auto_heal` | memory | critical | repair corrupted databases, rebuild indexes, restore configs | 1800 s |
| `preemptive_heal` | prediction | warning | pre-emptive cleanup, cache flush or service check on a degrading prediction | 300 s (BaseAction floor; per-sub-action cooldowns 1800–86400 s in the action) |

Notes:

- `auto_cleanup` has two Reactor rules: memory at
  WARNING, and health at CRITICAL with a disk-usage
  condition. The registered floor is the lower one; the
  stricter rule narrows, it does not widen.
- `auto_heal` is the only reflex whose floor is
  CRITICAL — healing a database is the heaviest hand
  the layer has, and it is kept for the worst reports.
- The daemon's own default is dry-run for the reactor
  (`heartbeat/core.py`: `reactor.dry_run` defaults
  True) — a fresh install reports what its reflexes
  *would* do before it lets them do it.

## 4. Never speaks for the companion

This is the Heimdall doc-05 instinct, applied to nerves:
the part of the system that acts fastest is the part that
must never be mistaken for the companion's own voice.

A reflex's only output is the `ActionResult` record —
`action_name`, `severity` (one of success / partial /
failed / skipped / dry_run), `message` (a technician's
summary line), `details`, `timestamp`, `targets_affected`,
`targets_failed`, `duration_ms`. `reflexes.validate_reflex_result`
accepts exactly that shape and refuses any record
carrying a speech field (`reply`, `utterance`, `speech`,
`dialogue`, `message_to_user`, `companion_says`, `voice`)
or an unregistered action name. A reflex may act on the
machine and may leave a record for operators and logs;
it produces no dialogue, no first-person utterance, no
nerve event in the companion's voice, and no message
addressed to a person as if from the companion.

The neighbouring directive layer keeps the same line.
The top-level conversation reactor (`Verdandi/reactor.py`)
executes nothing: it reads the conversation log and emits
reaction *directives* — proposals a reader or cognition
considers (and which E-062's context discipline injects,
capped, as a starting brief). Directives propose;
reflexes act; cognition speaks. This slice does not
collapse any two of those.

## 5. Docket 31 — Vör repaired

Vör (`preemptive_heal`) was the one broken shipped
reflex, re-proven at E-060 §3. All three breaks are
fixed in `heartbeat/actions/vor_action.py`:

1. **Crash on Skuld's own shape.** Skuld's capacity dict
   can carry string status values —
   `{"status": "no_resource_data"}` or
   `{"status": "insufficient_data"}` — and Vör called
   `.get("urgency")` / `.get("prediction")` on those
   strings. `should_trigger`, `_get_capacity_prediction`
   and `_get_capacity_summary` now guard with the same
   `isinstance(pred, dict)` check Skuld's own consumer
   uses; string shapes are not predictions and are
   dropped, never crashed on. A non-dict emotion value
   is guarded the same way.
2. **Broken result construction.** Both returns built
   `ActionResult(name=…)` (the dataclass field is
   `action_name`) and the no-action return used
   `ActionSeverity.INFO` (no such member). Both now use
   `action_name=self.name`, and the no-action return is
   `ActionSeverity.SKIPPED` — the severity sibling
   actions use when nothing was done.
3. **Wrapper bypass.** Vör defined `execute()` and no
   `_execute()`, so it ran around BaseAction's wrapper
   (no dry-run honour, no duration, no crash fold). It
   now implements `_execute()` only, declares
   `trigger_checks = ["prediction"]`,
   `trigger_severity = WARNING` and its BaseAction
   cooldown like its siblings, and the conformance tests
   pin that *no* registered action overrides `execute()`.

Vör's first tests land in this slice's conformance suite:
trigger on the string shapes (no crash, no trigger),
trigger on a real urgency prediction, the capacity
helpers dropping string shapes, the no-action SKIPPED
record, the wrapper's dry-run answer, and one real
pre-emptive path (disk cleanup in dry-run). Docket 31
is **CLOSED**.

## 6. Docket 95 — the conversation reactor's focus honoured

`reactor.py`'s `react(focus=…)` accepted a focus
(`all`, `blockers`, `learnings`, `files`, `next` — the
CLI's own `--focus` choices) and never used it: a
"blockers only" report silently carried everything.
The function now applies a focus filter (`FOCUS_MAP`)
after computing the full reactions: the focused value
keeps exactly its one category and its one top-level
directive, every other category is returned empty, and
the result shape is unchanged, so formatting and the
context injector's `react()` call (no argument = `all`)
are untouched. An unknown focus raises `ValueError` —
refused, never silently treated as `all`. Docket 95 is
**CLOSED**.

## 7. What this slice did NOT do

- No new reflex was added, and no reflex's trigger,
  floor, cooldown or effect was changed — Vör's declared
  trigger fields state what its Reactor rule already
  did; they widen nothing.
- Transport is untouched: which stimuli reach the
  reactor over the canonical socket is E-067's work
  (cross-member nerves), as E-061/E-064 assigned it.
- Detecting a stuck or dead reflex/hub is nerve health,
  E-066 — including docket 96 (the hub's `get_status`
  publishing a real ping) and docket 34's `pulse_metrics`
  wiring, both already owned there.
- Flooding behaviour is E-070 (backpressure on tiny
  hardware: a flooded hub sheds by rule, reflexes
  first-protected) — the register's floors and cooldowns
  are the facts that slice builds on.
- No README touched; no budget-book ceiling moved. One
  bookkeeping consequence, handled in this slice: adding
  `reflexes.py` and repairing Vör and the conversation
  reactor changed Verdandi's tracked weight, so the
  E-057 member budget table is re-measured and updated
  in both published copies, as its pinning tests require
  (figures in §9).

## 8. Conformance — `tests/unit/test_reflex_layer_e065.py`

Tests pinning:

- the register: version 1, `validate_registry` clean,
  the module stdlib-only and self-contained; the
  register covering *exactly* the live `ACTION_REGISTRY`
  (five actions, no more, no fewer), each spec equal to
  its class's declared trigger checks, floor severity
  and cooldown, and each spec's `speaks_for_companion`
  False;
- the Reactor's six rules re-derived from a live
  `Reactor()` and matched against the register;
- every registered action implementing `_execute` and
  none overriding `execute` (the wrapper is universal);
- the rule match: WARNING/CRITICAL fire by check,
  OK/UNKNOWN fire nothing, unknown checks/severities
  fire nothing, `auto_heal` waits for CRITICAL;
- the result shape: a valid ActionResult record passes,
  speech fields / unregistered names / the old `info`
  severity / missing fields are refused;
- Vör (docket 31): §5's six behaviours;
- focus (docket 95): `all` is the unchanged default,
  each focus keeps only its category + directive, an
  unknown focus is refused;
- this document naming every reflex and the bounds
  (E-066 / E-067 / E-070) it hands forward to.

## 9. Slice gate

- New conformance suite: `tests/unit/test_reflex_layer_e065.py`
  — **18 passed**.
- Verdandi focal suites, re-run this slice with the declared
  dev dependency (pytest-asyncio) supplied from the isolated
  e005-extras dir and a short TMPDIR: the conversation-layer
  set (context_injector + conversation_logger + reactor +
  nervous_system) **101 passed** — identical to
  E-059/E-061/E-062/E-063/E-064, so the focus change broke
  no existing reactor behaviour; the heartbeat set (skuld +
  heartbeat actions + heartbeat checks + heartbeat)
  **374 passed** — identical to E-060, with Vör repaired
  underneath it.
- Root suite gate: Run B **1144 passed, 6 failed, 25
  skipped, 1 warning** (1126 E-064 baseline + 18 new; the
  6 are the proven environment failures, identical set,
  verified in three runs this slice); Run D **1201
  passed, 0 failed, 19 skipped, 1 warning**, exit 0
  (1183 + 18). Logs in `~/workspace/.verify-tmp/ember-e065/gate/`.
- Bookkeeping: adding `Verdandi/reflexes.py` and repairing
  Vör and the conversation reactor changed Verdandi's
  tracked weight — re-measured and updated in both
  published copies of the E-057 table: Verdandi now
  184 files / 16,903,436 B (was 183 / 16,889,384 B), the
  twelve-member total 131,297,395 B (was 131,283,343 B),
  Verdandi's miss of the laptop ceiling 126,220 B (was
  112,168 B); profile verdict unchanged (none), no RAM
  floor re-measured, no ceiling moved. No README touched.

*Filed by the E-065 slice, 2026-10-31. Next: E-066 —
nerve health.*
