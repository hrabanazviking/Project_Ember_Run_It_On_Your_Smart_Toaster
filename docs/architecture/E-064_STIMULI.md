# E-064 — Stimuli: External Events Enter as Typed Stimuli with Provenance

*Part IV, slice E-064. Method: every entrance named below was
re-read from code this slice (the heartbeat daemon and its
checks and signal handler, the conversation logger and cron
shim, the nerve hub, the mood system). The discipline itself
lives in code at `Verdandi/stimuli.py`; this document is its
reading copy. Conformance is pinned by
`tests/unit/test_stimuli_e064.py`.*

## 1. Plain-language summary

Things from outside — the clock, the machine's senses, and
messages — used to wander into Verdandi in whatever shape
their producer happened to speak, and an event itself could
not say where it came from: the hub's source field was
optional, a timer's pulse spoke a legacy dialect, and a
scheduled job's words looked like a person's. Now the
outside has a front door with a register on it. Every
external entrance is a named, typed **stimulus** in one of
three kinds — time, sensor, message — and no stimulus
enters without **provenance**: who or what produced it
(its origin) and how it entered (its channel). A stimulus
travels on the nerves as an ordinary canonical event
(E-061) whose data carries the full provenance, so every
later reader can answer "where did this come from?" from
the event itself — and E-071 can later govern that
provenance's privacy from the same record. One live
entrance is built in this slice: the nerve hub accepts
stimuli through `publish_stimulus_sync` and its `stimulus`
CLI command, and a stimulus that fails validation is
rejected with nothing published at all — no hub write, no
feed fallback.

## 2. What a stimulus is

A stimulus is an event that comes from OUTSIDE the
companion — the world touching the nerves — as opposed to
an internal nerve event (E-061), which one part of the
system publishes for another. Its shape:

```json
{"stimulus_version": 1, "kind": "<kind>", "name": "<name>",
 "payload": {…},
 "provenance": {"origin": "<str>", "channel": "<channel>",
                "at": "<ISO string, optional>"}}
```

- **Kind** is one of `time`, `sensor`, `message`
  (`stimuli.KINDS`) — the roadmap's own three: time,
  sensors-shaped inputs, messages.
- **Name** must be registered in `stimuli.STIMULUS_SPECS`
  (§3). There is deliberately no open fallback: an
  unregistered name is not a stimulus, and registering a
  new entrance is part of adding it.
- **Payload** is a dict of the stimulus's own fields.
- **Provenance** is mandatory: `origin` is a non-empty
  string naming the producer; `channel` is one of
  `timer`, `cron`, `check`, `signal`, `cli`, `log`,
  `direct` — and it must be the channel the name's spec
  registers, so one entrance cannot borrow another's
  channel. `at`, when present, is the origin's own
  timestamp string.

## 3. The register — every external entrance in the tree

| Stimulus (`name`) | Kind | Producer | Channel | Payload fields |
|---|---|---|---|---|
| `time.tick` | time | `heartbeat/core.HeartbeatDaemon.run` (interval timer loop) | timer | `pulse_count`, `interval_s` |
| `time.schedule` | time | `context_injector` / `conversation_logger` cron sessions (`log-start`) | cron | `session`, `summary` |
| `sensor.check:*` | sensor | `heartbeat/checks` (Eir health, Huginn projects, Mimir memory, Urdr schedule, Skuld prediction) | check | `severity`, `message`, `details` |
| `sensor.signal` | sensor | `heartbeat/signals.SignalHandler` (SIGTERM, SIGINT, SIGHUP, SIGUSR1, SIGUSR2) | signal | `signal` |
| `message.operator` | message | `nervous_system` CLI `stimulus` / `publish_stimulus_sync` callers | cli | *(the operator's own dict)* |
| `message.conversation` | message | `conversation_logger` entries (start / event / update / end) | log | `session_id`, `entry_type` |
| `message.mood_input` | message | `heartbeat/runa_mood_arousal_system` (`apply_event`, `apply_stimulation`, `apply_inner_thought`, `set_location`) | direct | *(the caller's own dict)* |

Notes on the register's honesty:

- `time.tick` and `sensor.check:*` describe entrances that
  today surface inside the legacy `heartbeat_pulse`
  (E-061): the timer fires the pulse and the five check
  results are folded into it. This slice registers the
  typed shape they enter AS; rewiring that transport onto
  the canonical socket is E-067's work, as E-061 already
  assigned it — not silently done here.
- `sensor.signal`: the signal handler's own law is flags
  only, no I/O in handlers; a stimulus record names which
  signal arrived when a consumer chooses to record one.
  No handler was changed in this slice.
- `message.conversation`: the origin is what separates a
  scheduled job's words from a person's — a cron session's
  origin is its job, a person's is their session.
  E-071 (privacy of nerves) owns the separation rule;
  this slice gives it the provenance to enforce on.
- `message.mood_input` registers the mood system's INPUT
  side; its output families (`event:*` and kin) are
  already registered as nerve events in E-061.

## 4. On the nerves

`stimuli.to_event` renders a validated stimulus as a
canonical E-061 event — `{"v": 1, "type":
"stimulus:<name>", "data": {"kind", "name", "payload",
"provenance"}, "source": <provenance origin>}` — and
`from_event` is its exact reverse, returning None for any
event that is not a valid stimulus event. Provenance is
inside the event's data, so it survives the feed file,
the ring buffer, the offline fallback and every reader;
it is not a side channel that a copy can lose (the
E-063 logger law's nerve copies are the cautionary shape).

The hub entrance stamps the entry time itself
(`provenance.at` = the hub-side UTC instant) when it
publishes through `publish_stimulus_sync`, because the
hub is the one witness every entrance shares.

## 5. The live entrance

`nervous_system.publish_stimulus_sync(name, payload,
origin, channel)` and the CLI form —

```
python3 nervous_system.py stimulus message.operator '{"text": "hello"}' operator_jane cli
```

— are the one live entrance built here. They follow the
deployed-standalone pattern of E-061/E-062/E-063: the
registry literals live in `nervous_system.py` as plain
literals (kinds, channels, the spec table), pinned equal
to `stimuli.py` by the conformance tests. Validation
failure — unregistered name, missing or empty origin,
unknown channel, a channel that is not the entrance's
own, or a non-dict payload — returns an error and
publishes **nothing**: unlike `publish_event_sync`, there
is no feed fallback for a rejected stimulus, because a
fallback line would be exactly an unprovenanced entry.

## 6. Docket

- **Docket 101 (new, → E-076 gate review):** the hub's
  open `publish` path (E-061's open vocabulary) still
  accepts operator events with the source optional, so an
  operator *can* still enter unprovenanced through the
  old door. The typed stimulus door now exists beside it;
  making the old door stimulus-only is a breaking change
  to every deployed caller and is not claimed by any
  Part IV slice — the E-076 gate reviews it with the
  part's whole record.
- No other new docket items. Nothing found in this
  slice's subject was left unfixed: the entrance,
  validation and registry are the slice, and the two
  legacy-shaped entrances (tick, checks) were already
  owned by E-067 before this slice began.

## 7. What this slice did NOT do

- The heartbeat's timer, checks and signal handler were
  not rewired (E-067 owns cross-member transport; the
  signal handler's flags-only law is untouched).
- The conversation logger was not changed: its entries
  are registered as the `message.conversation` entrance
  shape, and E-072 still owns whether they feed memory.
- No stimulus is yet *consumed* by a typed subscriber —
  the hub set (feed, ring, broadcast, CLI views, context
  builder) reads stimulus events as ordinary canonical
  events today; typed reaction to stimuli is the reflex
  layer's subject (E-065) and the wiring's (E-067).
- No README touched; no budget-book ceiling moved. One
  bookkeeping consequence, handled in this slice: adding
  `stimuli.py` and the hub entrance changed Verdandi's
  tracked weight, so the E-057 member budget table is
  re-measured and updated in both published copies, as
  its pinning tests require (figures in §9).

## 8. Conformance — `tests/unit/test_stimuli_e064.py`

Tests pinning:

- the discipline's shape: version 1, kinds exactly
  (time, sensor, message), the seven channels, the module
  stdlib-only and importing neither the hub nor the
  contract; registry well-formedness (unique names, kinds
  and channels valid, producers named, names rooted in
  their kind);
- registry coverage re-derived from the tree: the daemon
  timer and cron producers, all five `sensor.check:*`
  names, the five handled signals in `signals.py`, the
  logger entrance, and the mood system's four input
  functions in its source;
- provenance mandatory: empty/missing/non-string origins
  rejected, unknown channels rejected, `at` validated,
  and the channel bound to the entrance (a tick cannot
  enter by the operator's channel);
- the nerve rendering: `to_event` passes the E-061
  contract's own `validate_publish`, carries payload and
  provenance in data with source = origin, round-trips
  through `from_event`, rejects an unprovenanced
  stimulus, and `from_event` ignores non-stimulus events;
- the hub entrance: its literals equal the registry
  (exact names and the check pattern), a valid stimulus
  is published as `stimulus:<name>` with provenance
  stamped and readable back through `stimuli.from_event`,
  and six invalid calls each return an error while
  publishing nothing at all.

## 9. Slice gate

- New conformance suite: `tests/unit/test_stimuli_e064.py`
  — **16 passed**.
- Verdandi focal suites, re-run this slice with the declared
  dev dependency (pytest-asyncio) supplied from the isolated
  e005-extras dir and a short TMPDIR: the conversation-layer
  set (context_injector + conversation_logger + reactor +
  nervous_system) **101 passed**, exit 0 — identical to
  E-059/E-061/E-062/E-063.
- Root suite gate: Run B **1126 passed, 6 failed, 25
  skipped, 1 warning** (1110 E-063 baseline + 16 new; the 6
  are the proven environment failures, identical set);
  Run D **1183 passed, 0 failed, 19 skipped, 1 warning**,
  exit 0 (1167 + 16 — reconciles exactly). The first Run D
  attempt in this slice was killed mid-run (SIGTERM to the
  harness at ~36%, no summary line); it was re-run clean
  and the figures above are the re-run's own log. Logs in
  `~/workspace/.verify-tmp/ember-e064/gate/`.
- Bookkeeping: adding `Verdandi/stimuli.py` and the hub
  entrance changed Verdandi's tracked weight — re-measured
  and updated in both published copies of the E-057 table:
  Verdandi now 183 files / 16,889,384 B (was 182 /
  16,871,542 B), the twelve-member total 131,283,343 B
  (was 131,265,501 B), Verdandi's miss of the laptop
  ceiling 112,168 B (was 94,326 B); profile verdict
  unchanged (none), no RAM floor re-measured, no ceiling
  moved. No README touched.

*Filed by the E-064 slice, 2026-10-31. Next: E-065 — the
reflex layer.*
