# E-074 — The nerve model for member-builders

*Roadmap slice E-074 (Part IV — Verdandi: the Nerve Hub).
This is the builder's reading of the whole part: it adds no
new law. Every rule below was made by an earlier Part IV
slice (E-059–E-073) and is stated in code in the module
named beside it; this document is the one place a
member-builder can learn the whole model without reading
fourteen slice records. Pinned by
`tests/unit/test_nerve_model_docs_e074.py`, which checks
that every file and entry point named here exists, that
every earlier slice's law is represented, and that the
worked examples below run as written.*

## 1. The model in one paragraph

Verdandi is a **nerve hub**, not a message queue and not a
database. Members publish small, typed **events** to one
hub; the hub stamps, archives, and broadcasts them; other
members feel what happened by reading the hub's recent
tail or the feed file. Everything travels in one
canonical envelope (contract v1, E-061), external touches
enter as provenanced **stimuli** (E-064), fast safe
reactions happen in a **reflex layer** that never speaks
for the companion (E-065), and every read a persona makes
is filtered so one persona's nerves never leak into
another's view (E-071). The hub runs **standalone** — one
stdlib-only file, no companion required (E-073) — and it
degrades honestly when it is sick (E-066) or flooded
(E-070).

## 2. The shape of the system

```
  producers                    the hub                  consumers
  ─────────                    ───────                  ─────────
  conversation logger ─┐
  heartbeat rewards ───┤   Verdandi/nervous_system.py
  mood/arousal system ─┤   · stamps _seq / _ts / _iso   hub CLI (recent /
  Ember core bridge ───┼─▶ · appends nerve_feed.jsonl ─▶  subscribe)
  Hermes publishers ───┤   · 256-event ring (E-070      context injector
  operator CLI ────────┘     shedding by tier)          (budgeted, E-062)
                               · broadcasts to            persona-filtered
                                 subscribers              readers (E-071)
                                                          replay tooling (E-069)
```

- The hub module is `Verdandi/nervous_system.py`. Its
  state dir is `VERDANDI_HOME` when set, else
  `~/.hermes/state` (E-073); the socket is `runa.sock`
  and the archive is `nerve_feed.jsonl` in that dir.
- The hub's eight commands are the whole operator
  surface: `serve`, `publish`, `stimulus`, `recent`,
  `subscribe`, `status`, `healthcheck`, `stop`
  (`Verdandi/standalone.py`: `COMMANDS`,
  `standalone_manifest`, `resolve_state_dir`).

## 3. The builder's entry points

Each row names the file a builder loads, the entry points
to call, and the slice whose law the file states. Member
modules are stdlib-only and are loaded file-by-file —
that is why several laws are *carried inline* by their
consumers instead of imported (see §9).

| File | Entry points | Law |
|---|---|---|
| `Verdandi/event_contract.py` | `validate_publish`, `normalize_event`, `spec_for`, `classify_dialect`, `CONTRACT_VERSION` | E-061 |
| `Verdandi/nervous_system.py` | `publish_event_sync` | E-061, E-073 |
| `Verdandi/context_budget.py` | `TOTAL_MAX_CHARS`, `LAYER_SHED_ORDER` | E-062 |
| `Verdandi/logger_law.py` | `ENTRY_TYPES`, `EVENT_TYPES`, `DELETE_SCOPE_FILES` | E-063 |
| `Verdandi/stimuli.py` | `make_stimulus`, `to_event`, `from_event`, `validate_stimulus` | E-064 |
| `Verdandi/reflexes.py` | `reflexes_for_trigger`, `validate_reflex_result`, `validate_registry` | E-065 |
| `Verdandi/nerve_health.py` | `classify_nerve_health`, `NerveObservations`, `validate_classification` | E-066 |
| `Verdandi/cross_member.py` | `build_event`, `validate_cross_event`, `spec_for_cross` | E-067 |
| `src/ember/nerve.py` | `publish_session`, `publish_turn`, `read_recent`, `read_recent_for_persona`, `filter_for_persona`, `hub_state_dir` | E-067, E-071, E-073 |
| `Verdandi/hermes_nerves.py` | `normalize_hermes_event`, `validate_hermes_event`, `is_hermes_event`, `spec_for_hermes` | E-068 |
| `Verdandi/replay.py` | `order_events`, `replay_feed_lines`, `replay_digest`, `validate_replay_order` | E-069 |
| `Verdandi/backpressure.py` | `tier_of`, `apply_backpressure`, `BackpressureQueue`, `pressure_level` | E-070 |
| `Verdandi/nerve_privacy.py` | `filter_events_for_persona`, `redact_provenance`, `event_persona` | E-071 |
| `Verdandi/memory_feed.py` | `feed_candidates`, `feed_log_entries`, `validate_rule` | E-072 |
| `Verdandi/standalone.py` | `resolve_state_dir`, `standalone_manifest` | E-073 |

The per-slice reading copies live beside this file:
`docs/architecture/E-059_VERDANDI_MAPPED.md`,
`docs/architecture/E-060_VDRM_CONCORDANCE_EXECUTED.md`,
`docs/architecture/E-061_EVENT_CONTRACT_V1.md`,
`docs/architecture/E-062_CONTEXT_INJECTION_DISCIPLINE.md`,
`docs/architecture/E-063_CONVERSATION_LOGGER_LAW.md`,
`docs/architecture/E-064_STIMULI.md`,
`docs/architecture/E-065_REFLEX_LAYER.md`,
`docs/architecture/E-066_NERVE_HEALTH.md`,
`docs/architecture/E-067_CROSS_MEMBER_NERVES.md`,
`docs/architecture/E-068_HERMES_SHAPED_NERVES.md`,
`docs/architecture/E-069_ORDERING_AND_REPLAY.md`,
`docs/architecture/E-070_BACKPRESSURE.md`,
`docs/architecture/E-071_NERVE_PRIVACY.md`,
`docs/architecture/E-072_LOGGER_AS_MEMORY_SOURCE.md`,
`docs/architecture/E-073_VERDANDI_STANDALONE.md`.

## 4. Rule 1 — publish only the canonical envelope (E-061)

An event on the wire is:

```json
{"v": 1, "type": "<str>", "data": {…}, "source": "<str>"}
```

- `v` is `CONTRACT_VERSION` — **1**. Check a would-be
  publish with `validate_publish` before sending; a
  legacy-dialect shape (heartbeat, mood) is first
  translated with `normalize_event`, never published raw.
- `source` is required for any new in-tree producer.
- The hub stamps `_seq`, `_ts`, `_iso`; builders never
  set stamp fields themselves.
- Register before you publish: adding an event type is
  not a version bump, but the new type is registered in
  `EVENT_SPECS` in the same change that adds its
  producer, and the E-061 conformance scan fails if it
  is not. Breaking a registered shape *is* a version
  bump.
- The easy path is the hub's own publisher:
  `publish_event_sync(event_type, data, source)` stamps
  `v: 1` for you and falls back to appending the same
  envelope to the feed file when the socket is down
  (the fallback carries `_fallback: True` and no `_seq`).
- Cross-member events (heartbeat ⇄ hub, core ⇄ hub) are
  stricter: build them with `build_event` in
  `Verdandi/cross_member.py`, which refuses unregistered
  names and any data field set that is not exactly the
  registered one.

## 5. Rule 2 — the outside world enters as stimuli (E-064)

Time passing, a sensor-shaped check result, and an
incoming message are not events a member invents ad hoc:
they are **stimuli** — typed (`time.tick`,
`time.schedule`, `sensor.check:*`, `sensor.signal`,
`message.operator`, `message.conversation`,
`message.mood_input`), with mandatory provenance
(`origin` + `channel`, optionally `at`). Build one with
`make_stimulus`, render it onto the wire with
`to_event`, and read one back with `from_event`. An
unprovenanced or unregistered stimulus never becomes a
nerve event — `to_event` raises instead.

### Worked example A — a stimulus becomes a valid event

Run from the repo root:

```python
import importlib.util
from pathlib import Path

def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, Path(rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

stimuli = load("stimuli", "Verdandi/stimuli.py")
contract = load("event_contract", "Verdandi/event_contract.py")

s = stimuli.make_stimulus(
    "message.operator", {"text": "hello nerves"},
    origin="my_member", channel="cli")
event = stimuli.to_event(s)
assert contract.validate_publish(event) == []
print("example A:", event["type"], "from", event["source"])
```

## 6. Rule 3 — respect the budgets (E-062, E-070)

Two budgets protect tiny hardware:

- **Context budget (what may be felt).** The context
  injector may spend at most `TOTAL_MAX_CHARS` (4000)
  characters across its layers, nerve events capped at
  10 events with truncated data; when over budget it
  sheds layers in `LAYER_SHED_ORDER`, never silently
  truncating mid-thought. A builder whose member
  injects context obeys `Verdandi/context_budget.py`,
  not its own numbers.
- **Hub backpressure (what may be queued).** The hub's
  ring holds 256 events. When full, admission is by
  tier (`tier_of`): protected heartbeat events shed
  last, low mood-family traffic sheds first, and every
  shed is counted — never the old blind FIFO eviction.
  `pressure_level` words (calm / pressured / full) are
  report vocabulary only. A flooding producer is not
  throttled; its low-tier events are what shed, and the
  shed report from `apply_backpressure` is the honest
  record of the loss.

## 7. Rule 4 — logging, privacy, and memory are laws, not habits

- **Logger law (E-063).** Conversations are logged as
  `start` / `event` / `update` / `end` entries
  (`ENTRY_TYPES`) with the closed `EVENT_TYPES`
  vocabulary, in the files `Verdandi/logger_law.py`
  names. The user may delete — totally and provably:
  `DELETE_SCOPE_FILES` is the exact scope a delete must
  cover, archives included.
- **Privacy (E-071).** An event bound to a persona
  (a `persona_id` in its data, or a conversation session
  resolved through a caller-supplied `session_owners`
  map) is visible whole to that persona and withheld
  *entirely* from every other persona — not redacted.
  System events (heartbeat, time, sensor stimuli) are
  visible to all. Persona-scoped reads go through
  `filter_events_for_persona` (member side) or the core
  bridge's `read_recent_for_persona`; aggregate views
  that cross personae use `redact_provenance`. Never
  read the raw feed tail for a persona.

### Worked example B — one persona never feels another's nerves

```python
import importlib.util
from pathlib import Path

def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, Path(rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

privacy = load("nerve_privacy", "Verdandi/nerve_privacy.py")

events = [
    {"v": 1, "type": "heartbeat_pulse", "data": {}, "source": "verdandi-heartbeat"},
    {"v": 1, "type": "ember_turn", "data": {"persona_id": "ada"}, "source": "ember_core"},
    {"v": 1, "type": "ember_turn", "data": {"persona_id": "bob"}, "source": "ember_core"},
]
visible, report = privacy.filter_events_for_persona(events, "ada")
assert [e["type"] for e in visible] == ["heartbeat_pulse", "ember_turn"]
assert report["withheld_cross_persona"] == 1
print("example B: ada sees", len(visible), "of", report["total"])
```

- **Memory feed (E-072).** Logged conversations may feed
  memory only under the user's explicit rule — granted
  by the user, enabled, scoped, naming the feedable
  event types (`learned`, `decision`, `milestone`, plus
  an end summary only on opt-in) — via `feed_candidates`
  / `feed_log_entries` in `Verdandi/memory_feed.py`.
  Every run returns a counts-only report; a feed is
  never silent. Working-state entries never feed.

## 8. Rule 5 — react fast below cognition, degrade honestly

- **Reflexes (E-065).** A reflex is a fast, dumb, safe
  reaction to a health check at `warning` severity or
  worse (`reflexes_for_trigger`); its result must pass
  `validate_reflex_result`, and a reflex **never speaks
  for the companion** — no reply, utterance, or dialogue
  field may appear in a reflex result. If a reaction
  needs words, it is not a reflex; route it through
  cognition instead.
- **Nerve health (E-066).** A hub that is stuck, dead, or
  absent is a *state to report*, not an error to hide:
  `classify_nerve_health` (fed a `NerveObservations`)
  returns healthy / degraded / stuck / dead / absent,
  and consumers degrade by the stated behaviour for each
  state — the companion keeps working without nerves and
  says so, rather than pretending to feel.
- **Hermes dialect (E-068).** Hermes lifecycle events
  arrive in their own envelope; `normalize_hermes_event`
  is the one translation into the contract, and
  `is_hermes_event` / `validate_hermes_event` are the
  gate. Builders do not hand-translate Hermes shapes.
- **Replay (E-069).** A recorded feed replays
  deterministically: `order_events` gives the one true
  order, `replay_feed_lines` replays a feed, and
  `replay_digest` is the fingerprint two replays must
  share. Debug from a replay, not from a live hub.

### Worked example C — replay order is deterministic

```python
import importlib.util
from pathlib import Path

def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, Path(rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

replay = load("replay", "Verdandi/replay.py")

feed = [
    {"v": 1, "type": "b", "data": {}, "_seq": 2, "_ts": 2.0},
    {"v": 1, "type": "a", "data": {}, "_seq": 1, "_ts": 1.0},
]
first = replay.replay_digest(replay.order_events(feed))
second = replay.replay_digest(replay.order_events(list(reversed(feed))))
assert first == second
print("example C: one digest for both orders")
```

## 9. The disciplines that hold the model together

1. **File-by-file loading.** The hub and its law modules
   are loaded by path by their consumers (the hub's
   deployed form is a lone file in its state dir). A law
   a consumer needs is therefore *carried inline* by that
   consumer and pinned equal by tests — the hub's
   `VERDANDI_HOME` resolution and the core bridge's
   `hub_state_dir` are the standing examples (E-073).
   Never add an import of a sibling member module to a
   file that is deployed alone.
2. **Stdlib only.** Every module in §3's table is
   stdlib-only. A nerve feature that needs a third-party
   package is a design smell on tiny hardware — bring it
   to the part gate instead.
3. **Fail closed.** Unknown stimulus, unregistered event,
   unknown session owner, invalid memory-feed rule: each
   refuses, counts, and reports — none guesses.
4. **Counts-only reports.** Privacy filtering, memory
   feeding, and backpressure all report counts and
   reasons, never the withheld content. A builder's new
   report surface obeys the same shape.
5. **Never leave a discovered bug unfixed.** A wart a
   builder finds in the nerve model is fixed in scope or
   docketed to its owning slice — the open dockets at
   this filing are 100–103 (E-076 gate review), 104
   (E-085), 105 and 106 (E-076).

## 10. A new member, end to end (checklist)

1. Decide the member's role: producer, consumer, or both.
2. For each event it produces: register the type in
   `Verdandi/event_contract.py` (`EVENT_SPECS`) in the
   same change; publish via `publish_event_sync` or, for
   a cross-member leg, `build_event`.
3. For each external touch it receives: name it as a
   stimulus in `Verdandi/stimuli.py` with provenance, or
   reuse a registered one.
4. For each event it consumes: read through the hub
   (socket `recent` / `subscribe`, or the bridge's
   `read_recent`), and if the read is for a persona, use
   the persona-filtered reader.
5. If it injects context: spend from
   `Verdandi/context_budget.py`'s budget.
6. If it reacts below cognition: register the reflex,
   keep it speechless, validate its results.
7. If it logs conversations: obey
   `Verdandi/logger_law.py`, including the delete scope.
8. Prove it: conformance tests beside the existing
   Part IV suites, the hub's `healthcheck` green, and a
   replay of the member's own events reproducing by
   digest.

## 11. Honest limits

- There is **no typed subscriber SDK**: consumers today
  are the hub's feed/ring/broadcast, the CLI views, the
  context injector's feed-tail read, and the core bridge.
  The companion's chat does not yet consume nerves
  (docket 102, owned by the E-076 gate review).
- The hub's open `publish` CLI path may still omit
  `source` (docket 101, E-076) — in-tree producers may
  not use that freedom.
- Session-aware log pruning (docket 100), a Verdandi
  tool-event family matching the Hermes tool events
  (docket 103), the machine-hard-coded systemd units
  (docket 105), and the hub stop command's zombie-blind
  liveness probe (docket 106) are all open at this
  filing, each with its owner named above.
- Load truth is **not** in this document: hub throughput
  per profile is measured by E-075, the next slice; any
  throughput number quoted before then is invented.
- Install-from-package for the Verdandi member is not
  proven (E-073): the model above is proven at the file
  level, which is how every in-tree consumer loads it.

## 12. Slice gate

Recorded in `CAMPAIGN_STATE.md` (the E-070 pattern):
the new conformance suite
(`tests/unit/test_nerve_model_docs_e074.py`), the
combined Part IV conformance run, the Verdandi focal
sets, and the root Run B / Run D gates, all by the
E-017 method. This slice changes no member code, so the
E-057 member budget table is unchanged — its pinning
tests in the combined run prove that from the tree.

*Filed by the E-074 slice, 2026-10-31. Next: E-075 —
Load truth: hub throughput per profile, measured.*
