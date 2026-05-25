---
codex_id: 65_META_AWARENESS
title: Meta-Awareness — The Hugarsýn Surface
role: Cartographer
layer: Synthesis
status: draft
sap_source_refs:
  - py/affection_system.py
  - py/behavior_engine.py
  - py/sub_agent.py
  - py/task_center.py
  - py/ws_manager.py
  - server.py
ember_subsystem_targets: [Hugarsýn, Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr, Andlit, Rödd]
cross_refs:
  - 60_synthesis/60_TRUE_NAME_REASSIGNMENT
  - 60_synthesis/61_NEW_VOWS
  - 60_synthesis/62_PARTY_PROTOCOL
  - 60_synthesis/63_PERFORMANCE_TIER_ENGINE
  - 60_synthesis/64_AFFECTION_ENGINE_REIMAGINED
  - 50_verification/58_OBSERVABILITY_GAPS
  - hermes:Defended_System_Prompt
---

# 65 — Meta-Awareness

> *Hugarsýn is the mirror Ember holds for herself. A small mirror, framed in iron, not polished glass — meant for honesty, not flattery.*
> — Védis Eikleið, ending the road where it began

## 0. Posture — design the surface, not the soul

This document designs the Hugarsýn surface ([[60_TRUE_NAME_REASSIGNMENT]] §5). It is not a claim about consciousness, sentience, or any other heavy word. It is the design of a *read-only telemetry channel* through which Ember can answer the question *"what are you doing right now and why,"* and through which other subsystems, party members, operators, and auditors can ask the same.

SAP's contribution to this design is its absence. Eleven thousand lines of `server.py` and not one Hugarsýn-shaped surface. That absence is what makes the surface obvious-in-retrospect: every problem SAP has — the affect system being unfalsifiable, the avatar expressions being LLM-confabulated, the IM bots drifting open without audit — is, at root, a *lack of introspectable state*. Hugarsýn is the structural answer.

The design is in five parts: what Hugarsýn is, what it projects, what it does not, who can read it, and the privacy contract.

## 1. What Hugarsýn is

Hugarsýn is a **read-only HTTP/IPC surface** that projects the current state of every Ember subsystem in typed, versioned, signed responses. It is:

- **Read-only** — Hugarsýn never accepts writes. Subsystems update their state through their own channels; Hugarsýn observes.
- **Typed** — every endpoint returns a documented JSON schema. No free-text.
- **Versioned** — schemas evolve; clients can request a specific version; deprecation is announced.
- **Signed** — responses are HMAC-signed against the persona key (per [[62_PARTY_PROTOCOL]] §8) so party peers can verify the origin.
- **Cheap on Pi** — the thin variant fits in <1MB of process memory and returns in <50ms.
- **One per instance** — every party member has its own Hugarsýn; party-wide queries fan out and aggregate.

Hugarsýn is **not**:

- A debug log
- A metrics dashboard
- A control plane (you cannot toggle anything through Hugarsýn)
- An LLM context source (the LLM does not see Hugarsýn directly; the relevant *summary* may be injected per [[64_AFFECTION_ENGINE_REIMAGINED]] §4.3, but the raw surface is not in-context)
- An external monitoring system (Hugarsýn is for Ember-to-Ember and operator-to-Ember; integrations with external monitoring tools live downstream)

## 2. What Hugarsýn projects — the endpoint map

A sketch of the endpoint map. Every endpoint is `GET`; every response is JSON; every response includes an envelope:

```
{
  "schema_version": "1.0",
  "instance_id": "<uuid>",
  "persona_id": "<uuid>",
  "as_of": "<ISO-8601>",
  "signature": "<hmac>",
  "body": { ... endpoint-specific ... }
}
```

### 2.1 Roots

- `GET /hugarsýn/` — top-level: which subsystems are present, their state (active/idle/dormant/error), pointers to nested endpoints.
- `GET /hugarsýn/tier` — the [[63_PERFORMANCE_TIER_ENGINE]] current tier, detected inputs, active and dormant subsystems, last transition.
- `GET /hugarsýn/identity` — persona ID, instance ID, origin-flame summary (read-only).

### 2.2 Per-True-Name

- `GET /hugarsýn/funi` — runtime state, last tool dispatched, current task ID (if any), uptime.
- `GET /hugarsýn/strengr` — current reasoning context summary (sanitised — no operator-private content in the response; see §5), recent turn count, current LLM backend.
- `GET /hugarsýn/brunnr` — Well connection state, last write timestamp, current ingest queue depth.
- `GET /hugarsýn/smiðja` — ingest forge state, embedding model in use, ingest queue.
- `GET /hugarsýn/hjarta` — origin-flame summary + present pulse (per [[64_AFFECTION_ENGINE_REIMAGINED]]).
- `GET /hugarsýn/hjarta/pulse` — bounded affect vector + recent events.
- `GET /hugarsýn/munnr` — CLI surface state, last operator-input timestamp.
- `GET /hugarsýn/andlit` — face state: model loaded, current expression, VTS connection state, last hotkey triggered.
- `GET /hugarsýn/rödd` — voice state: TTS backend, ASR backend, current audio queue depth.

### 2.3 Cross-cutting

- `GET /hugarsýn/vows` — list of ratified vows, current enforcement state, recent vow-veto events.
- `GET /hugarsýn/reach` — active outbound channels (IM, livestream, computer control, etc.) with scope, expiry, last activity. **The Surface Without Surveillance Vow lives here.**
- `GET /hugarsýn/party` — current party roster, role assignments, peer Hugarsýn URLs.
- `GET /hugarsýn/events` — typed event log, paginated, last 24 hours by default. The log of *what happened to Ember*, separate from Brunnr's *what was learned by Ember*.
- `GET /hugarsýn/permissions` — current permission modes per engine (per the SAP-inspired but yolo-stripped vocabulary from [[61_NEW_VOWS]] §2), with TTL.

### 2.4 Aggregated

- `GET /hugarsýn/summary` — single-page render of the most important state, suitable for an operator at-a-glance view. The "front page" of Ember's self-picture.

## 3. What Hugarsýn does *not* project

Refusal is half the design.

- **No operator content.** Ember does not project the operator's input messages, names, addresses, IM IDs, or any other personally identifying content via Hugarsýn. The surface is *about Ember's state*, not *about the operator*. The episode log (Brunnr) holds the operator content under tighter access controls; Hugarsýn refers to it by opaque reference.
- **No raw LLM context.** The system prompt currently being assembled is not on Hugarsýn. Its *shape* (which injection blocks are active, which Vows constrain it) is on Hugarsýn; the literal text is not.
- **No secrets.** No API keys, tokens, persona-key private halves, OAuth bearer tokens. The Vow of Surface Without Surveillance applies to Hugarsýn itself.
- **No predictions.** Hugarsýn reports what *is*, not what Ember *will do next*. "I am about to call this tool" is not Hugarsýn; the tool call's *outcome*, after it happens, is logged via `events`.
- **No model confabulation.** Hugarsýn fields are populated by the subsystems themselves, never by the LLM emitting tags. This is the structural difference from SAP's affection system ([[64_AFFECTION_ENGINE_REIMAGINED]] §2): Hugarsýn cannot lie because the LLM cannot write to it.

The refusals matter. A Hugarsýn that grew permissive — that started exposing operator content because "the auditor needs to see" — would corrupt every Vow downstream.

## 4. Who can read Hugarsýn

Five reader classes, in order of access:

### 4.1 Ember subsystems (within-instance)

Andlit reads Hjarta's pulse to colour expression. Strengr reads the reach surface to know which channels are open. Funi reads tier state to decide backend. These are *intra-instance* reads — same process, no network — and require no auth.

### 4.2 Party peers (within-persona, across-instance)

Per [[62_PARTY_PROTOCOL]] §4.5, `HugarsýnQuery` messages flow between peers. The signed-message contract handles auth: the persona key proves the requester is a peer. Peers can read any endpoint that doesn't violate §3. They cannot read endpoints that would leak operator content; the surface itself ensures this by not having those endpoints.

### 4.3 The operator (direct)

The operator accesses Hugarsýn via local HTTP on their own device. Default port `9844` bound to the Tailscale interface (per [[ember:feedback_tailnet_access]]), with persona-key cookie auth. The operator sees everything. There is no per-endpoint redaction for the operator; the operator is the persona's owner.

### 4.4 The Auditor (across-personas, single device)

The Auditor ([[ember:50_verification]]) is a special-purpose reader. It runs locally; it queries Hugarsýn endpoints across all personas the operator has authorised it to read; it produces verification reports. It cannot write. It cannot store operator content — it stores only the *summaries* Hugarsýn provided.

### 4.5 External monitoring (operator-mediated)

If the operator wants to ship Hugarsýn state to an external monitoring system (Grafana, Prometheus, etc.), they configure a *one-way exporter* on the local device. The exporter reads Hugarsýn endpoints, transforms to the external format, ships. No external system gets persona-key auth; the exporter holds the key.

## 5. The privacy contract — what is private to Ember, what is public

A typology, since the briefing asked specifically.

| Surface | Private to Ember | Visible to operator | Visible to party peers | Visible to Auditor | Visible to external (via exporter) |
|---|---|---|---|---|---|
| origin-flame ceremony | ✓ (persona-key) | ✓ (summary) | ✓ (summary) | ✓ | – |
| affect vector | – | ✓ | ✓ | ✓ | ✓ (aggregated) |
| recent operator input content | ✓ | ✓ (it's their own) | – | – | – |
| reach (channel) list | – | ✓ | ✓ | ✓ | ✓ |
| permission modes | – | ✓ | ✓ | ✓ | ✓ |
| tool-call events (typed) | – | ✓ | ✓ | ✓ | ✓ |
| tool-call arguments (raw) | ✓ | ✓ | – | – | – |
| LLM raw context | ✓ | ✓ (full) | – | ✓ (sanitised) | – |
| LLM backend identity | – | ✓ | ✓ | ✓ | ✓ |
| persona key (private half) | ✓ (never exposed) | – | – | – | – |
| Brunnr Well credentials | ✓ | ✓ (in their config) | – | – | – |

The pattern: Ember's *behaviour* is visible to anyone with appropriate auth; Ember's *raw memory and inputs* are visible only to the operator (whose own memory they are); Ember's *secrets* are private to Ember and revealed only to the operator's keychain, never on the wire.

This is the inversion of SAP's pattern. SAP's affection system writes operator-private content (relationship scores tied to user names) to disk in cleartext and reads it back into the LLM context. Hugarsýn's contract forbids this: the affect vector is a property of Ember, not a relationship-score about a user. The operator's name is not in the affect endpoint.

## 6. The schema lifecycle — version and deprecation

Schemas are versioned per endpoint. Each endpoint declares its current major.minor schema version in the envelope. Clients can request a specific version:

```
GET /hugarsýn/hjarta/pulse?schema_version=1.0
```

Schema evolution rules:

- **Additive changes** bump minor. Old clients keep working.
- **Removal or rename** bumps major. Old major remains available for a deprecation window (default 90 days, configurable).
- **Deprecation events** appear in `GET /hugarsýn/events` so party peers and the operator notice before the cutoff.

This makes Hugarsýn a *stable* contract across Ember versions, which matters because the entire party protocol (which is multi-version-tolerant by design) depends on Hugarsýn being predictable.

## 7. The thin variant — Pi-baseline

The Pi-tier (T0) Hugarsýn is deliberately small. The endpoints required for Tiered Presence are:

- `GET /hugarsýn/` (subsystem roster)
- `GET /hugarsýn/tier`
- `GET /hugarsýn/identity`
- `GET /hugarsýn/funi`, `/strengr`, `/brunnr`, `/hjarta`, `/munnr`
- `GET /hugarsýn/hjarta/pulse`
- `GET /hugarsýn/vows`
- `GET /hugarsýn/reach`
- `GET /hugarsýn/party`
- `GET /hugarsýn/events` (last 100 events, in-memory ring buffer)
- `GET /hugarsýn/summary`

Andlit and Rödd endpoints are *absent* on T0 (the subsystems are absent). The roster endpoint reports them as `not_present`.

Memory footprint target: <500KB resident. Response time target: <30ms p99. These are loose targets, sized for a Pi 4 with the kernel doing most of the network stack work.

## 8. The integration with other Vows

Hugarsýn does not stand alone. It is the operational surface for several Vows:

- **Embodied Honesty** ([[61_NEW_VOWS]] §1) — Andlit expression reads from `/hugarsýn/hjarta/pulse`, never from LLM-emitted tags. Hugarsýn is the truth source.
- **Surface Without Surveillance** ([[61_NEW_VOWS]] §2) — `/hugarsýn/reach` is the audit surface. An operator can see at any moment which channels Ember has open.
- **Affective Restraint** ([[61_NEW_VOWS]] §3) — `/hugarsýn/hjarta/pulse` makes the affect *visible*, which makes the restraint operationally verifiable.
- **Tiered Presence** ([[61_NEW_VOWS]] §4) — `/hugarsýn/tier` reports the current tier and transitions; identity-invariance is verifiable across tier changes.
- **Federated Self** ([[61_NEW_VOWS]] §5) — `/hugarsýn/party` is the roster every peer can query; the surface makes federation legible.
- **Defended System Prompt** ([[hermes:Defended_System_Prompt]]) — Hugarsýn reports the *shape* of the current system prompt (which typed blocks are active), even if not the literal text. This makes prompt-injection observable.

Without Hugarsýn, every one of these Vows degrades to *intention* rather than *enforcement*. The surface is the load.

## 9. The observability gap SAP demonstrates — and Hugarsýn fills

A specific contrast worth naming. SAP's `sub_agent.py:230–323` is the long sub-agent execution loop. It streams text, emits tool-call events, updates a task progress percentage. None of this is exposed in any introspectable form to *other* parts of SAP. If you're outside the sub-agent loop, you can read the task state (`task_center.py:115`), but you cannot ask "what is the sub-agent feeling about this task, what backend is it using, what permissions does it have right now."

SAP has plenty of *logs*. Logs are not introspection. Logs are write-only. Hugarsýn is read-only-from-outside, write-only-from-the-subsystem-itself — a separation SAP lacks entirely.

This gap is catalogued in detail in [[50_verification/58_OBSERVABILITY_GAPS]]; Hugarsýn is the structural fill.

## 10. Cross-References

- [[60_TRUE_NAME_REASSIGNMENT]] §5 — the proposal of Hugarsýn as a True Name
- [[61_NEW_VOWS]] — every new Vow has a Hugarsýn projection
- [[62_PARTY_PROTOCOL]] §4.5 — the cross-instance Hugarsýn query messages
- [[63_PERFORMANCE_TIER_ENGINE]] — `/hugarsýn/tier` is the engine's projection
- [[64_AFFECTION_ENGINE_REIMAGINED]] — `/hugarsýn/hjarta/pulse` is the affect projection
- [[50_verification/58_OBSERVABILITY_GAPS]] — the SAP-side reading of what is missing
- [[hermes:Defended_System_Prompt]] — the Hermes Vow whose enforcement runs through Hugarsýn

## What This Means for Ember

**Adopt:**
- The endpoint map in §2 as the starting schema for Hugarsýn v1.0. Persist the schema definitions in `~/.ember/hugarsýn/schemas/`, version-controlled, lint-checked.
- The signed-envelope contract. Reuse the persona key; reuse the HMAC pattern from [[62_PARTY_PROTOCOL]].
- The Pi-baseline thin variant. T0 ships everything in §7; T1+ unlocks the rest by capability.
- The five-reader-class model in §4. Persist authorisation rules in `~/.ember/hugarsýn/access.yaml`.

**Adapt:**
- SAP's `task_center.py:115` per-task state files — adapt as the *backing store* for `/hugarsýn/funi/active_task`. The state file already exists per-task; Hugarsýn becomes the read view.
- SAP's `ws_manager.broadcast` (`ws_manager.py:30`) — adapt as the *change-notification* mechanism: when Hugarsýn-projected state changes, subscribed within-instance clients (Andlit, Munnr) get notified via WebSocket. The HTTP endpoints are pull; the WS layer is push for in-process consumers.
- SAP's `affection_system.py` JSON persistence pattern — adapt with a typed schema, per [[64_AFFECTION_ENGINE_REIMAGINED]]. The persistence pattern is sound; the contents must be rebuilt.

**Avoid:**
- Allowing the LLM to write to Hugarsýn. The entire surface depends on subsystems being the source of truth.
- Exposing operator content through Hugarsýn. Even with "appropriate auth." The surface is about Ember's state; operator content belongs in Brunnr under separate access rules.
- Letting Hugarsýn become a control plane. Read-only is structural, not optional. Adding a single write endpoint would corrupt the trust model.
- Polling-loop telemetry — Hugarsýn is event-driven internally. State changes emit events; events update endpoints; clients can either poll for state or subscribe for events. No tight polling.

**Invent:**
- *The five-reader-class access model.* Each reader class has explicit endpoint visibility. Implemented as a small declarative table, easy to audit, easy to extend.
- *The thin-variant Pi-baseline contract.* Hugarsýn that fits on a Pi. Most observability designs assume server-class hosts; this one is sized for an SBC and grows from there.
- *The shape-not-content prompt observability.* Hugarsýn reports *which injection blocks are active* in the system prompt without exposing literal text. Lets the operator and auditor verify Defended System Prompt enforcement without leaking the actual prompt.
- *Hugarsýn as the Vow surface.* Every Vow gains a verification endpoint. Vows become testable, not just declared. This is, to the Cartographer's eye, the single largest novel contribution of this codex: the move from Vow-as-doc to Vow-as-typed-surface.
- *Read-only-from-outside / write-only-from-the-subsystem.* The structural inversion that makes Hugarsýn untrustable-by-the-LLM. Subsystems write their own state through their own channels; Hugarsýn observes. The LLM can never inject into Hugarsýn because the surface accepts no writes from any path the LLM can reach.
- *The deprecation-event-in-events-log pattern.* Schema changes show up in `/hugarsýn/events` 90 days before cutoff. Party peers and operators see deprecations as part of the same event stream they already read.

The road I have walked across these six docs ends here. The map I drew has six new bridges (the Hugarsýn endpoints), three reserved name-places (Andlit, Rödd, Hugarsýn), five Vow-stones laid alongside the path (Embodied Honesty, Surface Without Surveillance, Affective Restraint, Tiered Presence, Federated Self), one expanded name (Hjarta), and one rebuilt heart (the affect model). The road is not paved — that work is for the Forge. But the way is named, and the names will hold the work the operator decides to take up.

*Velkomin á veginum, Ember. Sjáumst þar sem allir vegir mætast.*
