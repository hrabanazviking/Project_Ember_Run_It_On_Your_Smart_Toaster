# E-061 — Event Contract v1: Shapes Versioned, Producers/Consumers Listed

*Part IV, slice E-061. Starting HEAD: 1b0c1f8's parent 037fc0a
(E-060 banked + corrected). Method: every producer and consumer
below was re-read from code this slice — the E-059 map was the
starting claim, not the authority, and one of its statements is
corrected here (§5). The contract itself lives in code at
`Verdandi/event_contract.py`; this document is its reading copy.
Conformance is pinned by `tests/unit/test_event_contract_e061.py`
(22 tests, §7), which re-derives the registry's completeness from
the producer sources, so the contract cannot silently fall
behind the code again.*

## 1. Plain-language summary

Until this slice, Verdandi's parts spoke about each other in
several unwritten dialects and nobody could say exactly who
produced an event or who was listening. Now there is one written
contract, version 1. One shape is canonical — the envelope the
nerve hub already used, now carrying an explicit version number.
Every event the tree produces is registered in one place with
its producer, its consumers, and its data fields. The heartbeat's
two events stay in their old flat shape for now, honestly
labelled legacy: they are fired at a socket nothing listens on,
their file fallback is the shape that actually lands in the
feed, and rewiring that producer onto the canonical socket is
the wiring slice's job (E-067), done under this contract. One
producer was quietly speaking a fourth dialect E-059 missed —
the mood/arousal system, firing at the *right* socket with the
wrong key — and that one is fixed in this slice: it now emits
the canonical envelope. The context injector's log-event
vocabulary is fixed too: it offered only 7 of the conversation
log's 8 event types (the missing one was `mood_shift`); it now
derives its choices from the logger's own set, so it cannot
drift again. Nothing's measured size changed: the contract
module is member-side tooling, not shipped core, and no budget
ceiling moved.

## 2. The canonical envelope (contract v1)

A publisher sends:

```json
{"v": 1, "type": "<str>", "data": {…}, "source": "<str>"}
```

- `v` is `event_contract.CONTRACT_VERSION` — **1**. An event with
  no `v` is a pre-contract event and is read through the legacy
  rules (§4), never silently trusted as canonical.
- `source` is optional on the wire (an operator publish may omit
  it) and required for any new in-tree producer.
- The hub stamps `_seq` (monotonic), `_ts`, `_iso`, removes any
  `nerve_type`, appends to `nerve_feed.jsonl`, keeps the event in
  its 256-event ring buffer, broadcasts to subscribers, and
  replies `ack`. The offline fallback in `publish_event_sync`
  writes the same envelope to the feed with `_fallback: True`
  and no `_seq` — holes are by design (E-059 §6).
- Versioning rules (in the module, binding): consumers ignore
  unknown fields; breaking a registered shape is a version bump,
  not an edit; adding a new event type is not a bump — it is
  registered in the same change that adds its producer, and the
  conformance scan (§7) fails if it is not.
- Control messages are protocol, not events: `subscribe` →
  `subscribed`, `ping` → `pong`, `recent` → `recent_events`,
  plus the hub-initiated `ack` and `shutdown`.

`publish_event_sync` now stamps `v: 1` on every publish — a
literal in `nervous_system.py`, not an import of the contract
module, because that file is deployed and loaded standalone,
file-by-file, from `~/.hermes/state`. The conformance tests pin
the literal.

## 3. The registry — every event, its producer, its consumers

Consumers, honestly stated: every hub-dialect event today has
exactly the same three consumers — the hub itself (feed, ring
buffer, broadcast), the hub CLI's `subscribe`/`recent` views,
and `conversation_logger.get_context_for_cron`, which reads the
feed *file* tail. No event has a typed in-tree subscriber beyond
those; the wiring that changes this is E-067's. The table's
consumer column says "hub set" for those rows and names the
exceptions where they exist.

| Event (`type`) | Dialect | Producer | Consumers | Data (fields beyond the envelope) | Source |
|---|---|---|---|---|---|
| `conv_start` | hub | `conversation_logger._nerve_fire` via `publish_event_sync` | hub set | the whole log entry: `timestamp, session_id, entry_type, summary, model, platform, start_time` | `conv_logger:<session_id>` |
| `conv_event` | hub | same | hub set | `timestamp, session_id, entry_type, event_type, content` — `event_type` ∈ the log vocabulary (§6) | `conv_logger:<session_id>` |
| `conv_update` | hub | same | hub set | `timestamp, session_id, entry_type, next_actions, blockers, projects_touched, mood` | `conv_logger:<session_id>` |
| `conv_end` | hub | same | hub set | `timestamp, session_id, entry_type, summary, duration_minutes, decisions, things_learned, files_changed, next_actions, blockers, projects_touched` | `conv_logger:<session_id>` |
| `push_reward` | hub | `heartbeat/push_reward.py` via `publish_event_sync` | hub set | `repo, tier, intensity, label, total_pushes, total_reward_points, streak` | `push_reward` |
| `runa_reward` | hub | `heartbeat/runa_reward_system.py` via `publish_event_sync` | hub set | `trigger, domain, tier, intensity, emoji, sensation, context` | `reward_system` |
| `runa_negative` | hub | `heartbeat/runa_negative_system.py` via `publish_event_sync` | hub set | `trigger, emotion, tier, intensity, emoji, sensation, context` | `negative_system` |
| `ping` | hub | `nervous_system.get_status` via `publish_event_sync` | hub set | *(empty)* | `status_check` |
| `*` (open) | hub | `nervous_system` CLI `publish` / any `publish_event_sync` caller | hub set | opaque — caller's own | caller's, may be absent |
| `event:*` | hub | `heartbeat/runa_mood_arousal_system.apply_event` via `_fire_nerve` | hub set | `valence, energy, tension, arousal, arousal_stage, mood, comfort` | `mood_arousal_system` |
| `stimulation:*` | hub | `…apply_stimulation` via `_fire_nerve` | hub set | `arousal, arousal_stage, mood, mood_valence` (the `stimulation:refractory` fire: `stim_type, arousal, stage, mood`) | `mood_arousal_system` |
| `orgasm` | hub | `…_trigger_orgasm` via `_fire_nerve` | hub set | `orgasm_count, mood, valence, comfort, refractory_seconds, description` | `mood_arousal_system` |
| `thought:*` | hub | `…apply_inner_thought` via `_fire_nerve` | hub set | `arousal, mood, thought` | `mood_arousal_system` |
| `location:*` | hub | `…set_location` via `_fire_nerve` | hub set | `comfort_delta, arousal_mult` | `mood_arousal_system` |
| `heartbeat_pulse` | heartbeat (legacy) | `heartbeat/core.HeartbeatDaemon._fire_nerve_pulse` | **none — no listener** | flat fields: `pulse_count, state, health_score, health_trend, emotional_state, checks` | *(none on the wire)* |
| `heartbeat_state_change` | heartbeat (legacy) | `heartbeat/core.HeartbeatDaemon._fire_nerve_state_change` | **none — no listener, no fallback** | flat fields: `old_state, new_state, pulse_count` | *(none on the wire)* |
| `heartbeat_pulse` | heartbeat_fallback (legacy) | `heartbeat/core.HeartbeatDaemon._nerve_fallback_file` | feed readers (as a non-hub shape) | the pulse fields, plus `timestamp` and `source` in the flat shape | `verdandi-heartbeat` |

Notes on three rows:

- **`ping` is a registered defect, not a feature.** `get_status`
  probes the hub by *publishing* a real `ping` event instead of
  using the `nerve_type: ping` control message, so every status
  check lands in the feed and is broadcast (docket 96). It is
  registered so the feed's `ping` events have a named, owned
  explanation; the repair is E-066's.
- **The mood families** (`event:*` etc.) are enum-driven: the
  suffix is a value of the mood system's `EventType`,
  `StimulationType`, or `InnerThought` enum, or a
  `LOCATION_MODIFIERS` key for `location:*`.
- **`heartbeat_pulse` carries the pre-transition state** — it
  fires before the reactor runs and before the state machine
  transitions (E-059 §8). The contract records this as part of
  the event's meaning; a consumer must not read it as the
  daemon's current state.

Sockets, named so they can never be confused again
(docket 93's root): the canonical hub socket is `runa.sock`
(`nervous_system.SOCKET_PATH`, under `~/.hermes/state`); the
legacy heartbeat socket is `verdandi.sock`
(`heartbeat/paths.get_socket_path()`, under the heartbeat's own
base dir). A tree-wide search this slice re-confirms E-059's
finding that no nerve producer or consumer exists outside
`Verdandi/` — the Ember core touches none of this yet (E-067).

## 4. The legacy dialects — recognised, deprecated, translatable

`event_contract.classify_dialect` recognises four shapes by
their kind key, and `normalize_event` translates any of them
into the canonical envelope with **no field dropped** (flat
heartbeat fields become `data` keys; the fallback's ISO
`timestamp` becomes `_iso`; the mood shape's epoch `timestamp`
becomes `_ts`; the origin shape is named in `_legacy_dialect`).
`validate_publish` accepts only the canonical envelope — legacy
shapes fail it by construction and are validated after
normalization.

- **heartbeat** — flat `{event_type, …}` to `verdandi.sock`.
  Deprecated as a producer shape. Its translation is defined
  here; its producer's rewiring onto the canonical socket under
  this contract is **E-067** (cross-member nerves), which is
  where transport changes belong. Until then the shape that
  actually reaches the feed is the fallback below.
- **heartbeat_fallback** — the same flat shape plus `timestamp`
  and `source: "verdandi-heartbeat"`, appended directly to the
  feed. Hub-dialect readers misread it (the hub CLI prints its
  type as `?`); `normalize_event` exists for exactly this line.
- **mood** — `{source, event, timestamp, data}` over a raw
  socket. **Retired as a producer shape by this slice** (§5);
  it stays recognised because deployed copies and old feed
  lines still carry it.

## 5. Correction to E-059, and the mood producer fixed

E-059 §1/§6 stated that `runa_mood_arousal_system.py` "publishes
nothing — it keeps its own state file". That is wrong in a way
this slice's producer census caught: the module's `_fire_nerve`
(its line 922 at E-059's HEAD) opens a raw socket to the hub's
own `runa.sock` and sends `{source, event, timestamp, data}` —
a fourth dialect, speaking to the right socket with the wrong
kind key (`event`, not `type`), so the hub stamps and feeds
these messages with no `type` at all (its log prints type `?`).
No in-tree code *calls* the mood system's entry points (E-059's
passenger finding stands), but the producer exists and fires
whenever the system is used. The E-059 doc is not edited — this
section is the correction of record, in the campaign's standing
pattern.

The fix is in this slice because the dialect is this slice's
subject: `_fire_nerve` now sends the canonical v1 envelope
(`{v: 1, type, data, source: "mood_arousal_system"}`); the hub
stamps `_ts`/`_iso` itself, so the mood shape's own `timestamp`
field is gone. Docket 93 is therefore settled in two of its
three parts by this slice — the canonical shape is declared and
versioned, and the mood dialect is retired — with the heartbeat
transport rewiring expressly owned by E-067 (§4), not silently
dropped.

## 6. The conversation-log vocabulary (docket 97 — closed)

The log's event vocabulary is part of this contract because log
events become nerve events (`conv_event` carries them). The
canonical set is `conversation_logger.EVENT_TYPES`, exactly 8:
`decision, file_changed, learned, action, blocker,
blocker_resolved, mood_shift, milestone` — mirrored in
`event_contract.LOG_EVENT_TYPES` and pinned equal by test.

`context_injector.py` previously hand-listed 7 of the 8 in its
`log-event --type` choices, missing `mood_shift` (docket 97).
It now imports `EVENT_TYPES` from the logger and uses
`choices=sorted(EVENT_TYPES)` — the same derivation the logger's
own CLI already used — so the two can never diverge again. A
conformance test runs the injector's `log-event --help` and
requires `mood_shift` among the offered choices.

## 7. Conformance — `tests/unit/test_event_contract_e061.py`

22 tests, all passing this slice (§9), pinning:

- version 1; the two socket names distinct and present in the
  code they name; `LOG_EVENT_TYPES` exactly equal to the
  logger's own set; control-message names present in the hub.
- Registry well-formedness: known dialects/statuses, no
  duplicate (name, dialect), producers named, and the legacy
  heartbeat rows' consumer list honestly empty.
- Completeness by source scan: every literal
  `publish_event_sync("…")` call site in `Verdandi/` (outside
  tests) resolves to an exact registry entry; the logger's
  dynamic `conv_*` family and all four `conv_` types registered;
  the heartbeat's two legacy fires registered as legacy; every
  `_fire_nerve` literal family in the mood system resolves to a
  non-open registry entry.
- `classify_dialect` / `normalize_event` / `validate_publish`
  behaviour across all four dialects, including field
  preservation and rejection of unrecognised shapes.
- The producers' new shapes: `publish_event_sync` stamps
  `'v': 1`; the mood `_fire_nerve` emits the canonical envelope
  and not the retired `event` key; the injector derives its
  choices from `EVENT_TYPES` (source pin + the `--help`
  behaviour test above).
- The contract module imports stdlib only and imports neither
  the hub nor the logger (it must stand alone for deployed
  copies); this doc names every registered event.

## 8. What this slice did NOT do

- No producer's *transport* was rewired: the heartbeat still
  fires at `verdandi.sock` (E-067 owns that change, under this
  contract), and the conversation layer still loads the hub only
  from its deployed home (docket 94 — E-067/E-073).
- The hub still performs no validation on publish (E-059 §6):
  contract v1 gives it — and every future consumer — the shapes
  to validate *against*; enforcing rejection at the hub is a
  behaviour change no Part IV slice has claimed yet, and none is
  smuggled in here. `validate_publish` is available to any
  consumer that wants it today.
- No event was renamed and no data field changed meaning; the
  only wire changes are additive (`v: 1` on hub publishes) and
  the mood producer's move to the envelope its events always
  needed. No README touched; no budget ceiling moved (the
  contract module is member-side, outside the shipped core).
  One bookkeeping consequence, handled in this slice: adding
  `event_contract.py` and touching three Verdandi files changed
  Verdandi's tracked weight, so the E-057 member budget table
  was re-measured and updated in both published copies, as its
  own pinning tests require — Verdandi now 180 files /
  16,837,498 B (was 179 / 16,817,105 B), the twelve-member
  total 131,231,457 B (was 131,211,064 B), Verdandi's miss of
  the laptop ceiling 60,282 B (was 39,889 B); the re-measure is
  noted in the E-057 record itself. Verdandi's profile verdict
  is unchanged (none), and no RAM floor was re-measured.

## 9. Slice gate

- New conformance suite: `tests/unit/test_event_contract_e061.py`
  — **22 passed** (runner output in
  `~/workspace/.verify-tmp/ember-e061/`).
- Verdandi focal suites, re-run this slice with the declared
  dev dependency (pytest-asyncio) supplied from the campaign's
  isolated extras dir: the conversation-layer set
  (context_injector + conversation_logger + reactor +
  nervous_system) **101 passed**, exit 0 — identical to E-059's
  banked focal count; the heartbeat set (skuld + actions +
  checks + heartbeat) **374 passed**, exit 0 — identical to
  E-060's banked focal count. The mood producer's new wire shape
  was additionally proven behaviourally by a captured-socket
  smoke (canonical envelope to `runa.sock`; script + log in the
  evidence dir).
- Root suite gate: Run B **1076 passed, 6 failed, 25 skipped,
  1 warning** (1054 E-060 baseline + 22 new; the 6 are the
  proven environment failures, identical set); Run D
  **1133 passed, 0 failed, 19 skipped, 1 warning**, exit 0
  (1111 + 22 — reconciles exactly). The first Run B attempt
  showed 8 failed: the 2 extra were the E-057 member-budget
  tests catching this slice's own Verdandi weight change —
  fixed in scope by the re-measure in §8, after which both
  gate shapes reconcile. Logs in
  `~/workspace/.verify-tmp/ember-e061/gate/`.

*Filed by the E-061 slice, 2026-10-31. Next: E-062 — context
injection discipline.*

## Addendum (E-067, 2026-10-31) — the wiring this contract ordered

E-067 executed §4/§8's assignments. The heartbeat's two legacy
producers are retired: `heartbeat_pulse` and
`heartbeat_state_change` are now ALSO registered in the hub
dialect above (canonical, producer `heartbeat/core … via
_send_nerve_event`, source `verdandi-heartbeat`), and the
legacy-dialect registrations stay as the explanation for
pre-E-067 feed lines. Two new hub-dialect events are
registered with their producers in the same change, per §2's
rule: `ember_session` and `ember_turn`, produced by the Ember
core's nerve bridge (`src/ember/nerve.py`, from
`spark/munnr/chat.run`), source `ember_core`. The full wiring
record — the three legs, the memory facts the turn event
carries, and the reverse direction's honest state — is
`docs/architecture/E-067_CROSS_MEMBER_NERVES.md`; the wiring
registry in code is `Verdandi/cross_member.py`.
