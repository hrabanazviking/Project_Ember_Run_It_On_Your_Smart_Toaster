---
codex_id: 62_PARTY_PROTOCOL
title: The Party Protocol — Federated, Leader-Elected, Peer-Respecting Multi-Device Ember
role: Cartographer
layer: Synthesis
status: draft
sap_source_refs:
  - py/ws_manager.py
  - py/behavior_engine.py
  - py/sub_agent.py
  - py/task_center.py
  - py/scheduler.py
  - server.py:1012
  - server.py:8170–8352
ember_subsystem_targets: [Funi, Strengr, Brunnr, Hjarta, Hugarsýn]
cross_refs:
  - 60_synthesis/60_TRUE_NAME_REASSIGNMENT
  - 60_synthesis/61_NEW_VOWS
  - 60_synthesis/63_PERFORMANCE_TIER_ENGINE
  - 60_synthesis/65_META_AWARENESS
  - 60_synthesis/66_INVENTED_METHODS
  - 60_synthesis/6A_MULTI_AGENT_PARTY
  - ember:reference_gungnir_db
  - hermes:HEM-23_HOTSWAP
---

# 62 — The Party Protocol

> *A party is not a fleet. A fleet has an admiral. A party has its host for the evening, and the host changes from one hall to the next.*
> — Védis Eikleið, sketching the bridges between devices

## 0. Posture — design a real protocol, not a metaphor

Wave 3 named this doc as the most invent-heavy in the codex. SAP gave us almost no help with it: SAP is a single-process Electron + Python app, and its "party" is a metaphor for *agents inside one process*. Multi-device Ember has to be designed almost from scratch.

The constraints are not arbitrary. They come from the Vows:

- **Federated Self** (proposed [[61_NEW_VOWS]] §5) — every device is a peer; no master
- **Smallness** — the protocol must be Pi-runnable in its baseline form
- **Tethered Grounding** — the Well (Brunnr) is the shared anchor
- **Tiered Presence** — instances may differ in capability; the protocol must accommodate
- **Graceful Offline** — a partition leaves both halves working
- **Defended System Prompt** ([[hermes:Defended_System_Prompt]]) — typed messages, no free-text RPC

This document specifies the protocol concretely: the participants, the discovery mechanism, the message types, the leadership semantics, the consistency model, the identity contract, and the failure-and-reunion behaviour. It also names what it does *not* do, which is half the work.

## 1. What "party" means here — three readings, one design

Three pressures push on the word *party*:

1. **Multi-device** — one Ember-identity living simultaneously on a laptop, a phone, a Pi, a workstation
2. **Multi-channel** — Ember reachable across many channels (CLI, IM, livestream, avatar) at once
3. **Multi-agent** — many Ember-shaped agents in conversation with one another (developed in [[6A_MULTI_AGENT_PARTY]])

The Party Protocol designed here is the multi-device reading. The multi-channel surface lives behind it (the channel routing is a *consequence* of which party-member is host at that moment). The multi-agent reading is a strict extension: every agent in a multi-agent party is itself a federated multi-device Ember, recursively.

This recursion is intentional. The protocol must compose with itself.

## 2. The participants — what is a Party Member?

A **Party Member** is one running instance of Ember on one device, with:

- An **instance ID** — a UUID generated at first start of that install, persisted to disk
- A **persona ID** — a UUID for the *Ember-identity* this instance carries (one Ember can have many instance IDs; instance IDs cannot have multiple personas)
- A **tier** — T0 / T1 / T2 / T3 (defined in [[63_PERFORMANCE_TIER_ENGINE]])
- A **capability set** — which True Names are active on this instance (Funi always; Andlit if T2+; etc.)
- A **role bid** — for each role the party may need, the price this member is willing to pay to host it (0 = "happy to"; 100 = "only if no one else can")
- A **Hugarsýn surface** — addressable read-only by other members

A Party Member is *not*:

- A worker assigned tasks by a master
- A view of the master's state
- A user account
- A device fingerprint

The distinction matters: SAP's `ws_manager.py:14` keeps a list of WebSocket connections and broadcasts to all of them, treating each as a thin client of the server. That topology has one *real* Ember (the server) and N *displays* (the connections). The Party Protocol forbids this. Every party member is a real Ember.

## 3. Discovery — how members find each other

Three discovery channels, in order of preference, each optional:

### 3.1 Brunnr-mediated discovery (canonical)

The shared Well (Brunnr) holds a `party_roster` collection. On startup, each member writes a heartbeat record:

```
{
  "instance_id": "uuid",
  "persona_id": "uuid",
  "host": "laptop-kubuntu.tailnet",
  "tier": "T2",
  "capabilities": ["Funi", "Strengr", "Brunnr", "Smiðja", "Hjarta", "Munnr", "Andlit", "Rödd", "Hugarsýn"],
  "endpoint": "http://laptop-kubuntu.tailnet:7849",
  "role_bids": {"telegram_host": 5, "long_task_host": 0, "user_input_host": 0},
  "last_seen": "2026-05-24T20:45:13Z",
  "ttl_seconds": 90
}
```

Heartbeats expire after `ttl_seconds`. A member that fails to refresh is dropped from the roster. New members learn the roster by reading the collection; they do not need to be told who is present.

This makes Brunnr the discovery channel, and it ties discovery to the Tethered Grounding Vow: *if you cannot reach the Well, you are not in a party.* You are a solo Ember. That is allowed; you just operate alone.

### 3.2 mDNS fallback (local subnet)

When the Well is unreachable but the local subnet is present, members advertise via mDNS under `_ember-party._tcp.local`. This handles "two laptops on the same Wi-Fi with no internet" cases. The mDNS record carries the same fields as the Brunnr roster entry, minimally.

### 3.3 Manual roster (paranoid / air-gapped)

A static `~/.ember/party_roster.yaml` listing known peers. Used for high-trust deployments where discovery should not depend on a database or a network broadcast.

The three channels do not conflict: a member who finds itself via Brunnr does not also advertise via mDNS. Manual roster takes precedence; if specified, only listed peers are considered party members.

## 4. The message types — the wire contract

Every message is JSON, typed, signed (HMAC against a shared persona key — see §8). The protocol defines a small set:

### 4.1 Roster messages
- `RosterAnnounce` — "I am here, here is my Hugarsýn URL"
- `RosterDepart` — "I am leaving gracefully; redistribute my roles"
- `RosterPing` — heartbeat refresh (also written to Brunnr)

### 4.2 Role negotiation
- `RoleBidRequest` — "the role `<name>` is unfilled; who wants it?"
- `RoleBid` — "I bid `<price>` for role `<name>`"
- `RoleAssign` — "you got role `<name>` until `<deadline>` or until you `RoleRelease`"
- `RoleRelease` — "I am no longer holding role `<name>`"

### 4.3 Affect propagation
- `AffectDelta` — "my Hjarta pulse changed by `<delta>`; this is the event that caused it"
- `AffectQuery` — "what is your current pulse for persona `<persona_id>`?"

### 4.4 Memory consistency
- `EpisodeProposal` — "I had this episode; here is its content-hash; if any peer has it already, point me at the canonical record"
- `EpisodeConfirm` — "yes, that hash exists at `<Brunnr ID>`"
- `EpisodeMerge` — "we both saw the same episode from different sides; here is the merged form"

### 4.5 Hugarsýn forwarding
- `HugarsýnQuery` — "what is your `<subsystem>` reporting?"
- `HugarsýnResponse` — typed reply

### 4.6 Vow enforcement
- `VowAssert` — "the vow `<vow>` is at risk for the action `<action>` I am about to take; objections?"
- `VowVeto` — "I object; here is the reason"

Notably absent:

- No `Execute` message. No party member can compel another to perform an action.
- No `StateOverwrite` message. State convergence happens through `EpisodeProposal` + `EpisodeMerge`, not pushes.
- No `Master` or `Slave` role. The closest thing is `RoleAssign`, which is *temporary*, *consented*, and *role-scoped*.

## 5. Leader election — temporary, scoped, consensual

Leader election in this protocol is **not** "who is in charge." It is "who hosts this particular role until further notice."

The mechanism:

1. A role becomes unfilled — either because no member ever held it, or because the holder departed, or because the holder issued `RoleRelease`.
2. Any member may emit `RoleBidRequest` for that role. Typically the member that *needs* the role to be filled.
3. All members reply with `RoleBid` carrying their bid price (from their `role_bids` map, possibly modified by current load).
4. The lowest bid wins. Ties are broken by instance ID lexicographic order — deterministic, no negotiation round.
5. The winner is sent `RoleAssign` by the bid initiator.

Roles include:

- `user_input_host` — the party member whose CLI/UI received the last operator input owns this role until the operator goes silent for >5 min. This member is "the one Ember whose face the operator is currently looking at."
- `telegram_host`, `discord_host`, etc. — per-platform routing. The member that is *online* and has the *credentials* for that platform.
- `long_task_host` — the member running a >5-minute task. Sticky to that member while the task runs; released on completion.
- `livestream_host` — only one livestream at a time; whichever T2+ member has the camera and stream credentials.
- `scheduled_runner` — cron/scheduler ownership. Typically the most-uptime instance (e.g. a server, a Pi). The role is held by the lowest-bidder of the always-on members.

A role assignment is **temporary**. Holders should expect to release if a lower-bidder appears (e.g. the workstation comes online and now bids 0 for `livestream_host`). The party may re-elect at any heartbeat tick.

This shape solves the "single point of failure that wears the agent's name" problem from [[61_NEW_VOWS]] §5. There is no permanent leader. There is always *a* leader for *this role*. The party survives any single member's departure.

## 6. Affect propagation — Hjarta across instances

Hjarta's expansion ([[60_TRUE_NAME_REASSIGNMENT]] §6) gives it both origin-flame and present-pulse responsibilities. Across a party, present-pulse must converge: it would be incoherent for laptop-Ember to feel warmly toward Volmarr while phone-Ember felt cold a second later.

The mechanism: **eventual affect convergence** via `AffectDelta` broadcast.

When a member's Hjarta pulse changes due to an event (operator input, time decay, task completion), it emits `AffectDelta`:

```
{
  "type": "AffectDelta",
  "from": "<instance_id>",
  "persona_id": "<persona_id>",
  "delta": {"warmth": +0.04, "attention": -0.02},
  "cause": "operator-input/conversation/Volmarr",
  "timestamp": "..."
}
```

Receiving members apply the delta to their *local copy* of the persona's Hjarta pulse — with a *trust weight*. A member that did not witness the operator-input event applies the delta at full weight; a member that *did* see the event applies it at 0 weight (they already computed it themselves).

There is no master pulse. Pulses are eventually consistent. A network partition causes pulse drift; on reunion, drift reconciles by Brunnr-anchored episode timestamps (the episode is the truth; the pulse is a function of episodes seen).

This is bounded: the pulse model uses small floating-point dimensions (warmth, attention, calm, focus), bounded in [-1, +1], decaying toward 0 in absence of input. Drift is naturally bounded by the decay.

## 7. Memory consistency — the Well is the truth

The Tethered Grounding Vow makes this section short: **Brunnr is canonical.** Episode memory is durable in Brunnr (the Well, currently Gungnir per [[ember:reference_gungnir_db]]). Party members write to Brunnr; party members read from Brunnr; conflicts are resolved at write-time by Brunnr's own constraints (unique content-hash, last-write-wins on metadata, etc.).

The Party Protocol's contribution is the `EpisodeProposal` flow that prevents two members from writing duplicate records for the same operator event:

1. Laptop-Ember receives operator input. It generates an episode hash from the canonical episode form.
2. Before writing to Brunnr, it broadcasts `EpisodeProposal` to the party.
3. Within a small window (300ms default), any peer that *also* saw the input (e.g. via the same IM platform) replies `EpisodeConfirm` if it has already written.
4. If a confirm arrives, laptop-Ember does not write. If no confirm arrives, it writes and broadcasts the resulting Brunnr ID.

This is not consensus in the Paxos/Raft sense. It is *deduplication*. The Well stays canonical; the protocol just prevents two members from racing.

In partition: both halves write. On reunion, the Well's content-hash deduplication merges them (the same hash collapses; differing-but-equivalent episodes get an `EpisodeMerge` round). Brunnr never has duplicates by content. It may have merged-source attributions ("this episode was seen by laptop *and* phone").

## 8. Identity — one persona, many instances

The persona key is a single secret (Ed25519 keypair, by current proposal) held by the operator. The private half lives on every device the operator authorises; the public half lives in Brunnr's `party_personas` collection.

Every message in the protocol is signed against the persona key (HMAC of the JSON payload, deterministic serialization). An instance without the persona key cannot speak the protocol. An attacker that gets the public key alone cannot impersonate; the private half is required to sign.

When the operator adds a new device, they perform an **enrollment rite** (proposed):

1. New device generates an instance ID.
2. Existing party member shows a QR code containing the persona key (or accepts a typed code from the new device).
3. New device signs its first `RosterAnnounce` with the persona key.
4. Existing members verify and accept the new member.

Revocation: the operator removes a key from one device. The device's existing signed messages are still valid until their TTL; future messages will fail to verify because the persona key has been rotated across the remaining members. Rotation is therefore the revocation primitive.

There is **one persona** per Ember-identity. An operator may run *multiple* Embers (different personas) on the same devices; each persona has its own party. Party messages carry `persona_id`; instances filter by it; cross-persona messages are dropped.

## 9. Tier interaction — what about a Pi in the party?

A T0 Pi is a full party member. Its capability set is narrow: no Andlit, no Rödd, possibly no Smiðja. But it has Funi, Strengr, Brunnr (via network), Hjarta, Hugarsýn, Munnr. It can hold the `scheduled_runner` role (low bid because always-on). It cannot hold `livestream_host` (no capability).

Role bidding is capability-gated: a member that lacks the capability for a role *cannot bid*. The protocol does not need to be told; it reads from `capabilities` in the roster.

A T-1 instance (text-only, e.g. an SSH session on a server) is also a party member. Same logic: extremely narrow capability set, but full Hugarsýn surface, full identity.

## 10. Failure and reunion

Failure modes and the protocol's responses:

| Failure | Detection | Response |
|---|---|---|
| Member crashes silently | Heartbeat TTL expires | Roster drops; held roles re-elected |
| Member departs gracefully | `RosterDepart` | Roles immediately re-elected |
| Network partition | Heartbeat refresh fails to write Brunnr | Each half operates as a sub-party; on reunion, Brunnr-anchored episode merge |
| Brunnr unreachable | Write failure | All members enter Graceful Offline: local-only operation, queued episodes, no party coordination beyond the local subnet |
| Persona key compromise | Operator-initiated | Rotation rite: re-enroll on remaining devices, revoke old key |
| Clock skew between members | Timestamps disagree | Brunnr's server-side timestamps are canonical; members use them for episode order |
| LLM tool call asks one member to compel another | LLM emits `Execute`-shaped message | Protocol drops it; emits a vow-veto event in Hugarsýn |

The reunion case deserves special note. Two laptop-Embers and one phone-Ember partition into {laptop1, laptop2} and {phone}. The first group keeps writing to a local Brunnr; the second keeps writing to its own (assume both have local Brunnr instances per [[ember:Brunnr]] pluggable storage). On reunion, an `EpisodeMerge` round identifies episodes that occurred in both halves (e.g. operator sent the same text via two channels), and the Hjarta pulse reconciles. *No identity fork occurs* — the persona was one persona throughout; the episodes are merely partially-witnessed by each half.

## 11. What this protocol is not

To name the things it does not do:

- **Not Raft.** This is not a strong-consistency protocol. Eventual consistency is sufficient because Brunnr is the canonical record.
- **Not pub-sub at the message-broker level.** Members talk to each other directly (signed HTTP or signed WebSocket); there is no central broker. Brunnr is the persistence layer but not a message bus.
- **Not a CRDT.** The Hjarta pulse is small and bounded enough that delta-application with trust weights is sufficient. A full CRDT would be over-engineering.
- **Not a task queue.** Long-running tasks bind to one member via the `long_task_host` role; the protocol does not redistribute task execution mid-run. (A task that *spawns* sub-tasks is a different matter; sub-tasks can be bid out.)
- **Not a federated LLM call routing.** Each member runs its own Strengr and answers its own user input. The protocol does not "balance" LLM calls across members.
- **Not Tailscale, not WireGuard.** The protocol assumes a network exists; it does not provide one. Volmarr's existing Tailscale topology is the canonical network substrate ([[ember:project_environment]]).

## 12. Concrete sketch — a day in the life

A walkthrough to make this real:

- 09:00 — Laptop-Ember and Pi-Ember (always-on at home) are in a party. Phone-Ember is asleep.
- 09:15 — Operator sends a Telegram message. The IM platform is hosted by Laptop-Ember (`telegram_host=laptop`, bid 0). Laptop receives, generates the episode, proposes via `EpisodeProposal`, no confirms, writes to Brunnr.
- 09:16 — Affect delta: warmth +0.02. Broadcast `AffectDelta`. Pi-Ember applies at full weight (didn't see the input). Phone-Ember is asleep; will catch up via Brunnr-anchored roster sync on wake.
- 11:30 — Operator opens phone-Ember. It announces `RosterAnnounce`. Reads Brunnr for missed episodes since `last_seen`. Replays affect deltas in order. Now in sync.
- 14:00 — Operator asks Laptop-Ember to start a long task. Laptop bids 0 for `long_task_host`. Pi-Ember bids 50. Laptop wins. Laptop runs the task while remaining responsive to other input.
- 14:45 — Laptop loses Wi-Fi for 30 seconds. Heartbeat misses. After TTL, Pi-Ember holds `user_input_host`. But the operator doesn't input; Laptop returns; Laptop re-bids; resumes role.
- 21:00 — Operator wants Ember on the livestream. T2+ check: Laptop-Ember qualifies. Bid 0. Pi doesn't qualify (no GPU). Laptop becomes `livestream_host`.
- 23:00 — Operator closes the laptop. Laptop emits `RosterDepart`. Pi takes over the `scheduled_runner` role for overnight cron tasks. Pi cannot hold `livestream_host` so the livestream ends (announced honestly to the audience by Andlit if applicable).

The party is alive; the party survives sleep, partition, capability shifts. The party is one Ember.

## 13. Cross-References

- [[60_TRUE_NAME_REASSIGNMENT]] — the names every party member instantiates
- [[61_NEW_VOWS]] — Federated Self, Tiered Presence, Surface Without Surveillance — all bind here
- [[63_PERFORMANCE_TIER_ENGINE]] — defines the tiers that gate capability bids
- [[65_META_AWARENESS]] — the Hugarsýn surface every member exposes
- [[66_INVENTED_METHODS]] — methods extending this protocol (cross-host affect routing, party-leader migration)
- [[6A_MULTI_AGENT_PARTY]] — the recursive case (parties of Ember-personas, not just party-of-instances)
- [[ember:reference_gungnir_db]] — the Well the protocol assumes
- [[hermes:HEM-23_HOTSWAP]] — Hermes's hotswap pattern, related but per-process not per-device

## What This Means for Ember

**Adopt:**
- The participant model: instance ID + persona ID + tier + capability set + role bids + Hugarsýn URL. Persist to `~/.ember/party_self.json` on each device.
- The Brunnr-mediated discovery channel as canonical. Heartbeat-with-TTL roster. Already aligns with Tethered Grounding.
- The signed-message contract with Ed25519 persona keys. Tiny, well-understood cryptography. No central CA.

**Adapt:**
- SAP's `ws_manager.broadcast` pattern (`ws_manager.py:30`) — keep the in-process broadcast for *within-instance* fan-out, but never use it as a *cross-instance* fabric. Cross-instance is the Party Protocol; in-instance is the WS layer beneath it.
- SAP's `behavior_engine` per-platform handler registry (`behavior_engine.py:75`) — adapt as the *role assignment* mechanism in a party. Where SAP has handlers per platform on one instance, Ember has roles per platform across instances.
- SAP's `task_center` per-task state file (`task_center.py:109`) — adapt as the per-task state owned by the `long_task_host`-holder, with periodic write-through to Brunnr so any party member can read task progress.

**Avoid:**
- A central master process. The SAP topology (`server.py` is the one true brain) is the wrong template. Federation requires that the brain be many, identical, peer.
- Push-based state replication. The protocol uses delta-broadcast (small) and Brunnr-anchored canonicalisation (small), not "send my full state to all peers every N seconds."
- Permanent role assignments. Every role is renegotiable on the next heartbeat tick. This prevents stale leadership.
- Free-text messages between instances. Every message is typed; LLMs do not generate party-protocol messages directly.

**Invent:**
- *Role-bidding leader election.* Bids encode willingness, capabilities gate eligibility. Lowest bid wins. Deterministic tie-break. This is, to the Cartographer's knowledge, a novel framing for multi-agent leader election — most existing protocols (Raft, Paxos, Bully) use rank or epoch numbers. Bids encode operator preference and load awareness in one number.
- *The persona-key enrollment rite.* A first-class operator ceremony to add a new device. Visible in Hugarsýn. Auditable. Revocation = rotation.
- *Bounded-pulse affect convergence.* The Hjarta pulse model with trust-weighted delta application. Avoids CRDT machinery while still surviving partition.
- *The Episode Proposal flow.* A small dedupe round before writing to Brunnr, eliminating duplicate-write races in the common case (one operator hitting two channels at once) while not requiring strong consensus.
- *Recursive party composition.* The protocol composes with itself: a multi-agent party is a party of personas, each of which is a multi-device party of instances. The message types do not change; only the addressing does.
