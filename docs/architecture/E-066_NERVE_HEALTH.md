# E-066 — Nerve Health: a Stuck/Dead Nerve Is Detected and Reported; the Hub Degrades Honestly

*Part IV, slice E-066. Method: the hub's existing health
surface (nervous_system's healthcheck, get_status, the
subscriber pruner, the feed fallback) and Skuld's data
sources were re-read from code this slice; the Hermes
baseline's Verdandi-socket failures (E-059 §8) are this
slice's cautionary fixture. The discipline itself lives
in code at `Verdandi/nerve_health.py`; this document is
its reading copy. Conformance is pinned by
`tests/unit/test_nerve_health_e066.py`.*

## 1. Plain-language summary

A nerve that stops working must say so, plainly, and the
rest of the system must not pretend otherwise. Before
this slice the hub had pieces of health — a healthcheck
command, a status command, a pruner for silent
subscribers — but no single verdict, and the status
command itself was part of the problem: every time
anyone asked "is the hub alive?" it published a real
`ping` event into the feed, so checking the nerve
changed the nerve. And elsewhere in Verdandi, the
prophet Skuld was ignoring the health diary the daemon
writes every pulse and guessing scores from state names
instead.

Now the hub's state has five names — healthy, degraded,
stuck, dead, absent — each decided from stated facts
(is the process alive? does the socket answer the
control ping? how full is the feed?), each carrying the
reasons that decided it and a plain sentence for what
that state means for publishers, subscribers and
readers. The status probe is a control message and
leaves no trace in the feed. When the hub is not there,
publishing degrades to the feed fallback — and the
fallback is *marked* as a fallback, never reported as a
delivered event. And Skuld now reads the real per-pulse
health scores from `pulse_metrics`.

## 2. The cautionary fixture

E-059 §8 mapped how the heartbeat's nerve impulses
failed in the Hermes baseline shape: one producer fired
at a socket nothing listened on (`verdandi.sock`), one
shape's failure was silent (the state-change fire has
no fallback), and one "health" probe polluted the very
feed it measured. The lesson this slice builds on is
not "sockets are fragile" — it is that *unnoticed*
failure is the defect. Every failure mode named there
now has a detector, a name, or an owner: the legacy
transport's rewiring is E-067's; the hub side is this
slice; the state-change fire's silence is part of the
legacy shape E-067 replaces.

## 3. The five states

`Verdandi/nerve_health.py` (`classify_nerve_health`)
decides from a stated observation set — state dir,
socket presence, PID file, process aliveness (tri-state:
an unobserved fact is None, never invented), control-
ping response (likewise), feed presence/size, log
writability:

| State | Decided when | What it honestly means |
|---|---|---|
| `healthy` | process alive, socket answers ping→pong, no warning condition | live pub/sub: publishes acked, subscribers receive, recent reads from the hub |
| `degraded` | the hub answers, but a warning holds (feed ≥80% of its 10 MB rotation threshold, feed missing, log not writable, or responsiveness never probed) | live pub/sub still works — and the warnings are shown, not hidden behind "healthy" |
| `stuck` | process alive (or socket file stands) but the socket does not answer the control ping; or a live process with no socket file | publishes time out or return no-ack — never a success; subscribers receive nothing new; recent reads fall back to the feed file |
| `dead` | a PID file stands but its process is not running | publishes degrade to the marked feed fallback; subscribers cannot connect; the stale PID is reported, not silently cleaned by a probe |
| `absent` | no socket, no live process, no PID file | the hub is simply not running: publishes degrade to the marked feed fallback, subscribers are told the hub is not running, recent reads come from the feed file |

The order is load-bearing and test-pinned: dead and
stuck are judged before degraded/healthy, so a warning
condition (a fat feed, an unwritable log) can never
mask a silent hub. An unprobed hub is never called
healthy — the verdict is degraded, with "responsiveness
was not probed" among its warnings.

## 4. Detection, in the tree

- **The classifier** (`nerve_health.py`): pure,
  stdlib-only, standalone like its sibling disciplines.
  `validate_classification` refuses a record whose
  stated behaviour does not match its status — a dead
  hub reported with the healthy behaviour sentence is a
  validation error.
- **The live probe** (`nervous_system.ping_hub`): sends
  the `nerve_type: ping` control message and returns
  True only on `pong`. Control messages are protocol,
  not events (E-061): nothing is stamped, fed or
  broadcast.
- **get_status** now reports `nerve_health` beside its
  existing fields, computed by an inline copy of the
  classification (the deployed-standalone pattern of
  E-061/E-064 — nervous_system.py is loaded alone from
  `~/.hermes/state`; the conformance tests pin the two
  classifiers equal on a nine-case matrix). The `status`
  CLI prints it.
- **healthcheck** uses `ping_hub` for its socket check,
  and its stuck wording now says so ("no pong to control
  ping (hub stuck?)").
- **Already in the tree, now named as part of this
  discipline:** the subscriber pruner (a subscriber
  silent >120 s is pruned; `handle_client`'s read
  timeout is the same line from the other side), feed
  rotation at 10 MB, stale-PID refusal at hub startup,
  and the feed fallback's `_fallback` mark.

## 5. Docket 96 CLOSED — the probe is not traffic

`get_status()` probed the hub by calling
`publish_event_sync` with type `ping` — a real publish:
stamped, appended to the feed, broadcast to every
subscriber, on *every* status check. The probe now uses
`ping_hub` (control message). The conformance suite
proves the degrade-honesty consequence directly:
`get_status` on an absent hub leaves a seeded feed
byte-identical — where the old code would have appended
a fallback `ping` line — and reports `nerve_health:
absent`. The E-061 contract's `ping` spec is re-registered
from `defect` to `legacy`: no current producer emits it;
the spec remains so pre-E-066 feed lines keep their
named explanation.

## 6. Degrade honestly — the shapes, pinned

Degradation was already the hub's shape; this slice
names it and pins that no path upgrades it:

- Hub unreachable → `publish_event_sync` appends the
  event to the feed under lock, marked `_fallback: True`
  with no `_seq`, and returns `nerve_type: fallback` —
  never `ack`. A caller can always tell a delivered
  event from a filed one.
- A stuck hub (connects, never answers) → the publish
  read times out and returns `sent / no_ack` — again,
  not an ack.
- `get_recent_events` tries the hub's ring buffer and
  falls back to reading the feed file — the degraded
  read is the same data, honestly sourced from disk.
- `subscribe` on a non-running hub refuses plainly
  ("Nerve Hub is not running…"), it does not hang or
  fake a connection.
- Detection never restarts anything: reporting is this
  slice; acting on a report belongs to operators and to
  E-065's reflex layer, whose own daemon-side senses are
  the heartbeat checks. This separation is deliberate —
  a detector that silently restarts its subject can
  mask exactly the failures it exists to name.

## 7. Docket 34 CLOSED — Skuld reads pulse_metrics

The daemon's `_state_db_save` has written a
`pulse_metrics` row every pulse since v0.3.0 — the real
per-pulse `health_score`, trend, daemon state, check
severities and emotional state, pruned to the newest
10,000 — and nothing ever read it (E-009). Skuld, the
prediction check, instead approximated health from
`pulse_history`'s daemon-state *names* (running=100,
degraded=50, critical=20…), so two very different
machines in the same state scored identically and a
machine declining *within* "running" was invisible.

Skuld now reads `pulse_metrics.health_score` as its
health-history source (`_get_pulse_metrics` +
`_health_score_series` in `heartbeat/checks/skuld.py`):
the trend prediction, anomaly detection and emotional
classification all consume that series, and their
results carry `score_source` naming which source
answered — `pulse_metrics` or `pulse_history_state`.
The fallback is real and kept: stores that predate the
table, lack it, or hold no usable score still answer
through the state-name approximation, exactly as
before (test-pinned: a metrics-less store's trend is
byte-for-byte the old behaviour). Capacity prediction
deliberately still reads `pulse_history`: the disk /
memory percentages it regresses live in `checks_json`,
which `pulse_metrics` does not carry — stated here so
nobody "completes" the wiring by breaking it. This
executes E-060's WIRE decision; E-076's gate verifies
the closure stands.

## 8. What this slice did NOT do

- No transport was rewired: the heartbeat's legacy
  dialect moving onto the canonical socket is E-067
  (cross-member nerves), as E-061/E-064 assigned it.
- No backpressure: a flooded hub shedding by rule,
  reflexes first-protected, is E-070 — this slice's
  states are the verdicts that work reports against.
- No auto-restart, no hub supervision loop, no new
  daemon: detection and reporting only (§6).
- The open-publish provenance question (docket 101)
  and the session-aware pruning question (docket 100)
  keep their E-076 gate-review owner; nerve privacy is
  E-071.
- No README touched; no budget-book ceiling moved. One
  bookkeeping consequence, handled in this slice:
  adding `nerve_health.py` and the Skuld/hub changes
  moved Verdandi's tracked weight, so the E-057 member
  budget table is re-measured and updated in both
  published copies, as its pinning tests require
  (figures in §10).

## 9. Conformance — `tests/unit/test_nerve_health_e066.py`

Tests pinning:

- the classification: version 1, the five states and
  their behaviour sentences; healthy requires a pong;
  degraded shows its warnings; dead is papers without a
  process and cannot be masked by a warning; stuck is
  alive-but-silent in both its shapes; absent is
  not-running, stated as fallback behaviour; an unprobed
  hub is never healthy; `validate_classification`
  refuses mismatched behaviour;
- the inline classifier in nervous_system.py agreeing
  with nerve_health.py on the nine-case matrix;
- docket 96: no published-ping probe remains in the hub
  source; `ping_hub` against a live one-shot socket
  server sends exactly the control message and accepts
  only pong; `ping_hub` is False when nothing listens;
  `get_status` on an absent hub reports `absent` and
  leaves the feed byte-identical; on a stale-PID hub it
  reports `dead`; the contract's ping spec is legacy
  with its closure named;
- docket 34: Skuld's trend reads the metrics series
  (a store whose history says "running" throughout but
  whose scores fall 90→45 is predicted degrading, from
  `pulse_metrics`); the metrics-less fallback reproduces
  the old state-score behaviour exactly; anomalies and
  emotion consume the metrics series (a low, declining
  real series classifies urgency where state names
  alone could not); a DB without the table falls back
  cleanly;
- this document naming the five states, both dockets,
  and the slices it hands forward to (E-067, E-070,
  E-076).

## 10. Slice gate

- New conformance suite: `tests/unit/test_nerve_health_e066.py`
  — **19 passed**.
- Verdandi focal suites, re-run this slice with the declared
  dev dependency (pytest-asyncio) supplied from the isolated
  e005-extras dir and a short TMPDIR: the conversation-layer
  set (context_injector + conversation_logger + reactor +
  nervous_system) **101 passed** — identical to
  E-059/E-061/E-062/E-063/E-064/E-065; the heartbeat set
  (skuld + heartbeat actions + heartbeat checks + heartbeat)
  **374 passed** — identical to E-060/E-065, with Skuld now
  reading pulse_metrics underneath it.
- Root suite gate: Run B **1163 passed, 6 failed, 25
  skipped, 1 warning** (1144 E-065 baseline + 19 new; the
  6 are the proven environment failures, identical set);
  Run D **1220 passed, 0 failed, 19 skipped, 1 warning**,
  exit 0 (1201 + 19). Logs in
  `~/workspace/.verify-tmp/ember-e066/gate/`.
- Bookkeeping: adding `Verdandi/nerve_health.py` and the
  hub/Skuld changes moved Verdandi's tracked weight —
  re-measured and updated in both published copies of
  the E-057 table: Verdandi now 185 files / 16,919,924 B
  (was 184 / 16,903,436 B), the twelve-member total
  131,313,883 B (was 131,297,395 B), Verdandi's miss of
  the laptop ceiling 142,708 B (was 126,220 B); profile
  verdict unchanged (none), no RAM floor re-measured, no
  ceiling moved. No README touched.

*Filed by the E-066 slice, 2026-10-31. Next: E-067 —
cross-member nerves.*
