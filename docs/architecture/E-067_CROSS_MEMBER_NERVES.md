# E-067 — Cross-Member Nerves: Ember Core ⇄ Verdandi ⇄ Memory, Wired Under the E-061 Contract

*Part IV, slice E-067. Starting HEAD: 93f0913 (E-066 banked +
its push record). Method: every producer and consumer below
was re-read from code this slice — the E-059 map and the
E-061 contract were the starting claims; the wiring registry
in code is `Verdandi/cross_member.py`, the core's bridge is
`src/ember/nerve.py`, and conformance is pinned by
`tests/unit/test_cross_member_nerves_e067.py` (21 tests, §8).*

## 1. Plain-language summary

Until today the parts of Ember could not feel each other. The
heartbeat daemon — the part that watches the machine's health —
shouted its pulse into a socket nobody listens on, in an old
dialect nobody else speaks, and its state changes vanished
silently whenever that shout failed. The conversation logger
could only reach the nerve hub if somebody had first copied
the hub's files into a special folder by hand. And the Ember
companion itself — the chat a person actually talks to — never
touched the nerve system at all: its sessions and turns left
no trace the rest of the house could feel.

Now all three are wired, in the one dialect the E-061 contract
declared. The heartbeat's pulse and state changes travel as
proper contract envelopes to the real hub socket, and if the
hub is asleep they land in its feed file in the same proper
shape — state changes included, so they are no longer lost.
The logger finds the hub on its own: the hand-copied deployment
still wins where it exists, and the copy beside the logger in
this tree is the fallback, so the layer works with no copying
step. And a chat session now announces itself to the hub when
it starts and ends, and reports every finished turn — not what
was said, never that, but the turn's memory facts: how much of
the companion's memory grounded it, how many sources it cited,
where the turn was saved, and how it ended. Memory crosses the
nerve as facts a friend could read, never as the conversation
itself.

## 2. Leg 1 — heartbeat → hub (the E-061 §4 rewiring, executed)

`heartbeat/core.py` gains `_send_nerve_event(event_type,
data)`, the daemon's one nerve sender. It builds the canonical
v1 envelope — `{v: 1, type, data, source: "verdandi-heartbeat"}`
(literals inline, the deployed-standalone pattern, pinned equal
to `event_contract`/`cross_member` by the conformance tests) —
and sends it to the operator's `nerve.socket_path` override
when one is set, else the canonical hub socket (`runa.sock` in
the hub's state dir, `~/.hermes/state`).

- `_fire_nerve_pulse` and `_fire_nerve_state_change` now send
  through it; their data fields are unchanged from the legacy
  shapes (the pulse still carries the PRE-transition state —
  it fires before the reactor and the state transition, as
  E-059 §8 recorded — and its `checks` still include the
  Mimir memory check, so the memory member's state crosses
  the nerve inside the pulse, as it always did in intent).
- `_nerve_fallback_file` now appends the canonical envelope
  plus the hub's own fallback stamps (`_ts`/`_iso`/`_fallback`,
  the shape `publish_event_sync` writes) instead of the
  retired flat `heartbeat_fallback` dialect. **Both** events
  fall back: the state change's legacy shape had no fallback
  at all and a failed connect was silent (E-059 §8) — that
  loss is closed.
- The legacy socket path (`verdandi.sock`, `heartbeat/paths`)
  is untouched as a *paths* fact — the daemon's own IPC and
  pid/run layout still live there — but no nerve impulse is
  sent to it any more. Docket 93 is therefore COMPLETE: its
  three parts were the canonical shape (E-061), the mood
  dialect's retirement (E-061), and this transport rewiring.
- The heartbeat config's `nerve.socket_path` comment now
  names the true default (the canonical hub socket).

## 3. Leg 2 — conversation layer → hub, in-tree (docket 94, E-067 half)

`conversation_logger._nerve_fire` resolved the hub module
from exactly one place — `~/.hermes/state/nervous_system.py` —
so from this tree, on any machine without that deployment,
the logger worked fully and fired nothing, silently (E-059
§3). The search is now a named function,
`_nerve_candidate_paths()`: the deployed copy first (deployed
behaviour is byte-for-byte unchanged where a deployment
exists — pinned by test), the sibling `nervous_system.py`
beside the logger second. The logger's never-break-the-logger
rule is unchanged: any failure in either copy is still
swallowed by `_nerve_fire`'s guard. The remaining half of
docket 94 — Verdandi usable *standalone*, as its own program,
without the companion (its CLI and deployment story) — stays
E-073's, as E-060 assigned it.

## 4. Leg 3 — ember core → hub (the core's first nerves)

New module `src/ember/nerve.py` (stdlib only; contract
literals inline and pinned equal to the Verdandi registry by
test, the E-061 deployed-standalone pattern applied to the
core). Its discipline mirrors the logger's law and E-066's
degrade honesty:

- `publish_event` returns the hub's `ack` when the hub
  answers, `sent/no_ack` when it does not, `fallback` when no
  hub is reachable and the envelope was appended to the feed
  file with `_fallback`, and `error` with the reason
  otherwise. It never raises, and never claims a delivery it
  did not make.
- `publish_session` / `publish_turn` build the two registered
  events (field sets and vocabularies validated before the
  wire; a bad vocabulary is an `error` result, not a bad
  event).
- `read_recent` is the reverse direction's offered shape:
  the hub's `recent` control message against a live hub,
  the feed-file tail when there is none, `[]` when neither
  exists.

`chat.run` is wired at three points, all facts-only:

- **Session start** — after the Well opens (or honestly
  fails to): `ember_session{phase: start, persona_id,
  conversation_id, well_connected, model, turns: 0}`.
- **Each completed turn** — after the persistence outcome is
  known: `ember_turn{conversation_id, persona_id, hits,
  cited, persisted, ungrounded, outcome, model}`, where
  `hits`/`cited` are the turn's Well retrieval counts,
  `persisted` is `well` / `journal` / `memory_only` (exactly
  where the Episode landed, E-031's three shapes), and
  `outcome` is read off the same reply tags the diary reads
  (E-034): `interrupted` / `error` / `truncated`, else
  `ungrounded` when the turn ran without memory grounding,
  else `answered`.
- **Session end** — from the loop's `finally` block, so
  every exit path reports it: `ember_session{phase: end,
  …, turns: <completed turns>}`.

No operator text and no reply text ever enters an event —
the chat conformance test drives a full session with marked
sentinel strings in both directions and asserts neither
string appears anywhere in the feed. The bridge is **not**
part of the frozen core API (E-037): it is core-internal
wiring; a member binds to the hub's contract, not to this
module. Because chat now has a real side effect outside the
config root, the root suite's `conftest.py` gains an autouse
fixture redirecting the bridge's hub home to a short per-test
/tmp dir — tests must never write to the operator's live
feed (and AF_UNIX's ~108-char path cap is why the dir is
short: deep pytest tmp paths exceed it, a trap this slice's
first run proved and the fixture + the suite's socket tests
now respect).

## 5. The reverse direction, honestly stated

Hub → core consumption is **not** built in this slice, and
nothing here pretends otherwise. What exists today: the hub
set of E-061 §3 (feed, ring, broadcast, CLI views), the
context injector's budget-disciplined nerve block for cron
context (E-062), and now the bridge's tested `read_recent`.
What does not exist: any *typed* in-tree subscriber, and any
consumption of nerves by chat's prompt assembly. Injecting
live nerve state into a conversation is a context-budget
decision — E-062's discipline applied to chat — that no
slice has claimed. New docket **102**: the nerve-consumption
gap (no typed subscriber; chat does not consume nerves),
owned by the E-076 Part IV gate review, which must either
road a consumption slice or record the publish-only shape as
Part IV's verdict. E-068 (Hermes-shaped nerves) and E-072
(logger as memory source) proceed on the publish side this
slice proved.

## 6. Registration (the contract's own rule, kept)

`event_contract.EVENT_SPECS` gains, in this same change, the
hub-dialect registrations for `heartbeat_pulse`,
`heartbeat_state_change`, `ember_session`, and `ember_turn`
(producers and field sets identical to `cross_member.py`'s
registry — pinned equal by test). The legacy heartbeat
registrations stay, their notes now recording the producer's
retirement, as pre-E-067 feed lines' explanation (the E-066
`ping` pattern). The E-061 doc gains a dated addendum naming
the new registrations, keeping its doc-names-every-event pin
true. One E-061 conformance test was updated in this slice —
`test_heartbeat_legacy_fires_are_registered` now pins the
post-rewiring truth (no flat fires in `core.py`; both legacy
specs retained; both canonical specs registered) — because
E-067 is the slice E-061 assigned the change to; the test's
purpose (the registry cannot drift from the producers) is
unchanged and now covers both dialects.

## 7. What this slice did NOT do

- No hub-side validation was added (still E-059 §6's open
  fact; `validate_publish`/`validate_cross_event` are
  available to consumers, the hub does not yet enforce).
- No event was renamed and no existing data field changed
  meaning; the wire changes are the heartbeat's dialect move
  and the two new core events, both registered above.
- The heartbeat's non-nerve uses of its own paths (DB, PID,
  state dump) are untouched; `get_socket_path()` still
  resolves `verdandi.sock` for the surfaces that name it
  (the contract's socket-name pin stands).
- No README touched. Budget consequence handled in-slice:
  adding `cross_member.py` + `nerve.py` and touching five
  member files changed two members' tracked weight, so the
  E-057 table was re-measured in both published copies —
  Verdandi 186 files / 16,935,635 B (was 185 / 16,919,924),
  the core 130 files / 826,913 B (was 129 / 814,264), the
  twelve-member total 131,342,243 B, Verdandi's laptop miss
  158,419 B. No profile verdict changed; no ceiling moved;
  no RAM floor was re-measured.

## 8. Slice gate

- New conformance suite:
  `tests/unit/test_cross_member_nerves_e067.py` — **21
  passed** (registry coherence across all three modules,
  envelope builders/validators, heartbeat canonical wire +
  fallback behaviour against a captured socket, logger
  search-order behaviour against fake hubs, bridge ack /
  fallback / read-back against a live socket server, and a
  full chat session crossing start/turn/end facts with
  content proven absent).
- Prior Part IV conformance suites re-run: E-061 (as
  updated, §6) + E-062 + E-063 + E-064 + E-065 + E-066 +
  E-057 pins — **116 passed**.
- Verdandi focal suites (declared dev deps supplied from
  the campaign's isolated extras dir, short TMPDIR): the
  conversation-layer set (context_injector +
  conversation_logger + reactor + nervous_system) **101
  passed** — identical to E-059–E-066; the heartbeat set
  (skuld + actions + checks + heartbeat) **374 passed** —
  identical to E-060/E-065. A wider run that also included
  `test_heartbeat_integration.py` scored 418 passed / 5
  failed; the 5 are that file's CLI tests, which subprocess
  with `cwd=~/Verdandi` — a directory that does not exist on
  this VM — the machine-coupling family E-005 proved and
  docketed (its item 8 kin), not this slice's change: the
  failure is at subprocess spawn, before any heartbeat code
  runs.
- Root suite gate (E-017 method; logs in
  `~/workspace/.verify-tmp/ember-e067/gate/`): Run B
  **1184 passed, 6 failed, 25 skipped, 1 warning** (1163 +
  21; the 6 are the proven environment failures, identical
  set); Run D **1241 passed, 0 failed, 19 skipped,
  1 warning**, exit 0 (1220 + 21 — reconciles exactly).

## 9. Docket effects

- **Docket 93 — COMPLETE** (canonical shape E-061, mood
  dialect retired E-061, heartbeat transport rewired here).
- **Docket 94 — E-067 half CLOSED** (logger reaches the
  in-tree hub; the standalone-Verdandi half stays E-073's).
- **Docket 102 — NEW** (nerve-consumption gap, §5; owner:
  E-076 gate review). Dockets 100/101 keep their E-076
  owner; ordering/replay (E-069), backpressure (E-070),
  nerve privacy enforcement (E-071) and logger→memory
  (E-072) keep theirs.

*Filed by the E-067 slice, 2026-10-31. Next: E-068 —
Hermes-shaped nerves.*
