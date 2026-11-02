# E-068 — Hermes-Shaped Nerves: Verdandi's Event Shapes Matched Against the Hermes Hack's volmarr-core Session / Turn / Tool Events

*Part IV, slice E-068. Starting HEAD: 6f7b43c (E-067 banked +
its push record) plus this slice's IN PROGRESS marker 7448d2d.
Method: the Hermes side was re-read from code this slice —
the post-refresh surfaces in the Hermes hack's own tree
(`~/workspace/hermes-hack-build`, HEAD
7b821b270423149072a596503b60e0d7f8dd549d, 2026-10-31) —
never from memory: `plugins/volmarr-core/plugin.yaml`
(v0.26.0, the hook list), `plugins/volmarr-core/verdandi.py`
(the publisher), `plugins/volmarr-core/lifecycle.py` (the
session/turn/tool bridge), and
`plugins/volmarr-core/verdandi_stimuli.py` (the reverse
intake). The Hermes tree was NOT modified by this slice. The
translation registry in code is `Verdandi/hermes_nerves.py`;
the eight types are also registered in
`Verdandi/event_contract.py` in this same change, per the
contract's own rule. Conformance is pinned by
`tests/unit/test_hermes_nerves_e068.py` (§10).*

## 1. Plain-language summary

Ember's nerve hub and the Hermes agent's lifecycle events
already meet in the same place: Hermes's volmarr-core plugin
sends its session, turn, and tool events down the same
socket, in the same outer wrapping, that Ember's own parts
use. A Hermes event therefore lands in Ember's nerve feed
today, stamped and acknowledged by the hub like any other —
this slice proved that against the real hub.

But the two sides do not speak quite the same dialect
inside the wrapping. Ember events carry their facts flat,
in one envelope with a version number on it. Hermes events
carry a second, smaller envelope inside — its own named
and versioned schema — with the facts tucked one level
deeper. Forcing either side to abandon its envelope would
break a versioned contract that other work already stands
on, so the verdict of this slice is: **not one dialect —
a documented translation**. The translation now lives in
code: any Ember-side reader can turn a Hermes event into
Ember's canonical shape without losing a single field, the
eight Hermes lifecycle events are registered by name in
Ember's contract, and the one real gap the match exposed —
Hermes reports tool calls and Ember has no tool event at
all — is named plainly and docketed (docket 103), not
papered over.

## 2. What was read on the Hermes side

- **The hook list** (`plugin.yaml`, volmarr-core v0.26.0):
  the plugin registers `on_session_start`, `on_session_end`,
  `on_session_finalize`, `pre_tool_call`, `post_tool_call`,
  `pre_llm_call`, `post_llm_call`. The lifecycle bridge
  (`lifecycle.py`, `LifecycleBridge.hooks`) binds five of
  them — the two `*_llm_call` hooks have no lifecycle
  binding and publish nothing today.
- **The publisher** (`verdandi.py`, `VerdandiPublisher`):
  one JSON line per event over a Unix socket; the socket
  path comes from plugin config (`socket_path`, default
  `state/runa.sock` relative to the active Hermes profile
  home, resolved inside that home — a path escaping the
  home falls back to the default); `source` from config,
  default `hermes-agent`; timeout from config, default
  100 ms, clamped to 1–1000 ms.
- **The bridge** (`lifecycle.py`): an observer-only adapter
  whose docstring states its content rule — "raw content
  never enters the event envelope" — and which truncates
  its text fields (session/model ids 256, platform 64, tool
  names 128, exit reasons 128, status 64).
- **The reverse intake** (`verdandi_stimuli.py`): Hermes
  also READS the hub — §8.

## 3. The transport is already one

| Fact | Verdandi (this tree) | Hermes volmarr-core | Match |
|---|---|---|---|
| Socket | `runa.sock` in the hub state dir `~/.hermes/state` | `state/runa.sock` under the Hermes profile home — the same dir for the default profile | SAME (see the profile note below) |
| Wire framing | one JSON object per line | one JSON object per line | SAME |
| Outer keys | `type`, `source`, `data` | `type`, `source`, `data` | SAME |
| Hub behaviour | stamps `_seq`/`_ts`/`_iso`, feeds, rings, broadcasts, replies `ack` | (the hub's behaviour, received) | — |

Profile note, stated honestly: the in-tree hub's state dir
is the process HOME's `~/.hermes/state`, while Hermes
resolves its socket per profile home. For the default
profile those are the same directory; a Hermes running
under a different profile home would aim at that profile's
own `state/runa.sock` — reachable to this hub only via the
plugin's absolute `socket_path` config. Binding non-default
profiles is bridge work (Part VIII, E-126), not this
slice's; nothing here claims it.

## 4. The payload match, field by field

### 4.1 The envelopes

| Layer | Verdandi contract v1 | Hermes lifecycle |
|---|---|---|
| Version mark | outer `v: 1` | none outer; inner `schema` + `schema_version: 1` |
| Event kind | outer `type` | outer `type`, duplicated as inner `event` |
| The facts | outer `data` IS the field dict | inner `context` is the field dict; outer `data` is the inner envelope |
| Identity / time | hub stamps `_seq`, `_ts`, `_iso` on arrival | inner `event_id` (UUID) and `occurred_at` (ISO) minted by the publisher before sending |
| Inner envelope fields | — | exactly `schema, schema_version, event_id, occurred_at, event, context`; schema `runeforge.hermes.lifecycle` |

So a hub-stamped Hermes feed line and a hub-stamped Ember
feed line differ by exactly the inner envelope: strip it
(losslessly — §6) and the Hermes line IS a canonical event
whose `data` is its context. Without stripping it, a
Verdandi consumer reading `data` as flat fields reads the
envelope instead of the facts — the precise confusion this
slice exists to prevent.

### 4.2 The eight lifecycle events × their Verdandi kin

| Hermes type (hook) | Context fields (exact) | Verdandi kin | The difference that matters |
|---|---|---|---|
| `hermes.session.started` (`on_session_start`) | `session_id, model, platform` | `ember_session` phase=start; `conv_start` | No persona, no conversation_id, no Well-connected fact, no turn count — Hermes sessions are agent sessions, not companion conversations |
| `hermes.session.ended` (`on_session_finalize`) | `session_id` | `ember_session` phase=end; `conv_end` | Carries nothing else — no turn count, no duration. (Naming note: the `on_session_end` HOOK publishes the turn events below; `ended` comes from `on_session_finalize` — Hermes's own naming, recorded as-is.) |
| `hermes.turn.completed` (`on_session_end`) | `session_id, task_id, turn_id, completed, exit_reason, model, platform` | `ember_turn` outcome=answered | Outcome is encoded in the TYPE (three turn types from one hook); Ember carries one type + an `outcome` field |
| `hermes.turn.failed` (`on_session_end`) | same set | `ember_turn` outcome=error | Hermes's `completed` bool stays in context (False here) beside the type-encoded outcome |
| `hermes.turn.interrupted` (`on_session_end`) | same set | `ember_turn` outcome=interrupted | The bridge chooses interrupted > failed > completed, in that order |
| `hermes.tool.started` (`pre_tool_call`) | `tool_name, session_id, task_id, turn_id, tool_call_id, api_request_id` | **none** | No event in the E-061 registry reports tool calls — docket 103 |
| `hermes.tool.completed` (`post_tool_call`, status `ok`) | started set + `duration_ms, status, error_type` | **none** | docket 103 |
| `hermes.tool.failed` (`post_tool_call`, status ≠ `ok`) | same set as completed | **none** | docket 103 |

Field-level asymmetries worth naming once:

- **Identity vocabularies differ.** Hermes keys its world
  by `session_id` (+ `task_id`/`turn_id` inside it); Ember
  keys by `conversation_id` + `persona_id`. Neither is a
  renaming of the other — a Hermes session is not an Ember
  conversation — so the translation keeps both vocabularies
  exactly as they arrive.
- **Memory facts exist on one side only.** `ember_turn`
  carries hits / cited / persisted / ungrounded; no Hermes
  lifecycle event carries any memory fact. A translated
  Hermes turn is therefore never a substitute `ember_turn`.
- **Content rule: both sides agree.** Hermes's bridge is
  observer-only and content-free by its own docstring;
  Ember's nerve bridge is facts-only by E-067's law. The
  match needed no privacy negotiation — the same instinct
  stands on both sides, and E-071 will govern both shapes.

## 5. The delivery asymmetry

The one place the match is NOT symmetric, recorded plainly:

- **Verdandi publishers** (the hub's `publish_event_sync`,
  the heartbeat's sender, the core bridge) wait for the
  hub, and on failure either receive the hub's `ack` or
  write the feed file themselves with `_fallback` — an
  event survives the hub being down.
- **Hermes's publisher** writes its line with a ≤1 s
  timeout, reads NO reply (the hub's `ack` is sent and
  unread), and drops the event on any failure, returning
  False to a caller that (in the lifecycle bridge) ignores
  the result. A Hermes lifecycle event published while the
  hub is down is GONE — no feed line, no fallback.

This is Hermes-side design (fail-open so a transport
failure can never enter the agent turn), not a defect this
Ember slice may repair: the fix, if Volmarr wants one,
belongs to the Hermes tree (a feed fallback in
`VerdandiPublisher.publish`, shaped like the one this tree
already proves). Nothing in this slice changes Hermes.

## 6. The verdict and the translation

**Verdict: one transport, two payload dialects, a
documented translation between them.** Not one dialect,
because unifying would mean breaking a versioned contract
on one side: on the Verdandi side, changing a registered
shape is a contract version bump by E-061's own rules; on
the Hermes side, the inner envelope is the shared shape of
EVERY volmarr-core publisher family — lifecycle
(`runeforge.hermes.lifecycle`), cognition telemetry
(`runeforge.cognition.telemetry`), WYRD changes
(`runeforge.wyrd.change`), entity heartbeat / routine /
consolidation (`runeforge.entity.*`), and the §14
self-aware events (`runeforge.hermes.self_aware_events`),
all built by the same `build_envelope`, all v1. An Ember
slice does not get to re-shape another project's spine —
it documents the translation and proves it lossless.

**The translation in code** — `Verdandi/hermes_nerves.py`
(stdlib only, standalone like the other contract modules):

- `HERMES_SPECS`: the eight lifecycle types with their
  hook, exact context fields, and kin (the table in §4.2).
- `is_hermes_event`: shape detection — a `runeforge.*`
  schema, inner `event` equal to outer `type`, dict
  `context`. It never keys on `source`, which is
  operator-configurable on the Hermes side.
- `validate_hermes_event`: the lifecycle registry's full
  judgement (envelope field set, schema name + version,
  exact context fields per type). Other `runeforge.*`
  families are recognised by shape and refused HERE —
  their registries live on the Hermes side.
- `normalize_hermes_event`: the lossless canonical form —
  context becomes `data`; `schema`, `schema_version`,
  `event_id`, `occurred_at` move to `_hermes_schema`,
  `_hermes_schema_version`, `_hermes_event_id`,
  `_hermes_occurred_at` provenance keys (the underscore
  convention of the hub's stamps and E-061's
  `_legacy_dialect`); type, source, and hub stamps pass
  through. The result passes `validate_publish`. No
  Hermes type is renamed: a translated `hermes.turn.*`
  stays `hermes.turn.*`, because §4.2's differences are
  real and a rename would lie about them.

**Registration** — the eight types stand in
`event_contract.EVENT_SPECS` (hub dialect, status
canonical) with the ENVELOPE's fields as their registered
`data_fields` — the honest description of what is on the
wire — and the E-061 doc gains a dated addendum naming
them, keeping its doc-names-every-event pin true.

## 7. What this slice did NOT do

- No Hermes file was touched, and no producer in this
  tree emits the Hermes shape (pinned by test): the
  translation is for reading, per E-061's rule that
  in-tree producers emit the canonical envelope.
- No `ember_tool` event was invented to answer docket
  103. Whether the core should publish tool facts (it HAS
  a tool loop, E-026 — its approvals and executions are
  audited locally, never nerved) is a Part IV gate
  question, not a matching exercise.
- The other volmarr-core families (cognition, WYRD,
  entity, §14) are matched at the envelope level only:
  same publisher, same translation shape (proven on a
  cognition-shaped event by test); their per-type field
  registries stay Hermes-side, and any Ember consumer
  that grows to need one registers it the way this slice
  registered the lifecycle eight.
- No README touched. Budget consequence handled in-slice
  (§10): adding `hermes_nerves.py` and touching
  `event_contract.py` changed Verdandi's tracked weight,
  so the E-057 table was re-measured in both published
  copies, as its pinning tests require.

## 8. The reverse direction was already matched

Hermes's `verdandi_stimuli.py` reads the hub's `recent`
control message and maps feed events into its affective
layer: `runa_reward` (source `reward_system`),
`runa_negative` (source `negative_system`), `push_reward`
(source `push_reward`), and `conv_event` (source
`conv_logger:*`, on blocker / blocker_resolved /
milestone). Every one of those types and sources is a
canonical Verdandi event of the E-061 registry, read in
its flat canonical shape — the reverse direction needed
no translation and gets none. Its cursor discipline
(advance only after the stimuli commit) is Hermes-side
behaviour this slice records, not changes.

## 9. Docket effects

- **Docket 103 — NEW**: no Verdandi tool event exists to
  match `hermes.tool.started` / `.completed` / `.failed`
  (§4.2). Owner: the E-076 Part IV gate review, which must
  either road a core tool-facts event (the core's tool
  loop, E-026, is the would-be producer) or record the
  publish-side absence as Part IV's verdict.
- Dockets 100 / 101 / 102 keep their E-076 owner; E-069
  (ordering & replay) now has the Hermes provenance keys
  to preserve in replay, noted for its slice.

## 10. Slice gate

- New conformance suite:
  `tests/unit/test_hermes_nerves_e068.py` — **12 passed**
  (registry coherence across hermes_nerves / event_contract
  / this doc, shape detection keyed on the envelope not the
  source, validation refusing schema / version / field
  drift, lossless normalization of all eight types, the
  other-`runeforge.*`-schema shape rule, the
  no-in-tree-producer pin, and a Hermes-shaped publish
  landing on the REAL hub — subprocess `serve` under a
  redirected HOME — stamped, acked, fed, and translated
  back with its context intact).
- Prior Part IV conformance re-run: E-061 (as addended)
  + E-062 + E-063 + E-064 + E-065 + E-066 + E-067 + the
  E-057 pins — **137 passed** (116 prior + E-067's 21,
  reconciling exactly).
- Verdandi focal suites (declared dev deps supplied from
  the campaign's isolated extras dir, short TMPDIR): the
  conversation-layer set (context_injector +
  conversation_logger + reactor + nervous_system) **101
  passed** — identical to E-059–E-067; the heartbeat set
  (skuld + actions + checks + heartbeat) **374 passed** —
  identical to E-060/E-065.
- Root suite gate (E-017 method; logs in
  `~/workspace/.verify-tmp/ember-e068/gate/`): Run B
  **1196 passed, 6 failed, 25 skipped, 1 warning** (1184 +
  12; the 6 are the proven environment failures, identical
  set); Run D **1253 passed, 0 failed, 19 skipped,
  1 warning**, exit 0 (1241 + 12 — reconciles exactly).

*Filed by the E-068 slice, 2026-10-31. Next: E-069 —
ordering & replay.*
