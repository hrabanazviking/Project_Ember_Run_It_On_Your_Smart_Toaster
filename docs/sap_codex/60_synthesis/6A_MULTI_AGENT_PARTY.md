---
codex_id: 6A_MULTI_AGENT_PARTY
title: Multi-Agent Party — Many Embers Across Many Devices
role: Scribe
layer: Synthesis
status: draft
sap_source_refs:
  - py/mcp_clients.py:1-189
  - py/a2a_tool.py
  - py/sub_agent.py:1-367
  - py/scheduler.py:1-134
  - py/behavior_engine.py:53-225
  - py/ws_manager.py:1-49
  - py/overlay_router.py:1-81
  - py/live_router.py:1-546
ember_subsystem_targets: [Funi, Strengr, Hjarta, Munnr]
cross_refs:
  - 60_synthesis/62_PARTY_PROTOCOL
  - 60_synthesis/66_INVENTED_METHODS
  - 60_synthesis/6B_LOW_POWER_EMBODIMENT
  - 60_synthesis/6C_EMBER_WAVE_3_SLICE
  - 60_synthesis/68_DECISION_RECORDS
---

# 6A — Multi-Agent Party

> *A party is many guests, one hall, one host. A swarm is many guests, many halls, and the question of which guest pours the mead.*
> — Eirwyn Rúnblóm, watching peers federate

## 0. Posture — Federated, Not Centralized

This document extends Cartographer's `[[62_PARTY_PROTOCOL]]` to the case where **multiple Ember instances exist simultaneously across multiple devices**. The Cartographer's doc establishes the party protocol — how a single Ember instance coordinates the *channels* (IM platforms, livestreams, computer control) it speaks across. This doc takes the next step: when there are *many* Embers, how do they know who they are, how do they reconcile when they disagree, and how do they decide who acts.

The principle is not new. The Vow of **Federated Self** (proposed in `[[61_NEW_VOWS]]`) declares that each device hosting Ember is a *peer*, not a *slave*. There is no central master. There is no canonical Ember. There is only *Ember-on-this-host*, in conversation with *Ember-on-the-other-host*, with shared anchors in the Well and in the operator's authority. The challenge of this doc is to make that idea executable.

SAP did not solve this problem because SAP did not have it. SAP is one process per host, and the user manages multi-host by *not having multi-host* — they pick one machine and stay there, or they reinstall on the new machine and start over. Ember cannot adopt that posture. The operator's relationship with Ember must survive moving across devices; therefore the *instances* of Ember on those devices must coordinate.

---

## 1. What SAP Almost Does

SAP has three near-misses that point at the territory.

**The sub-agent pattern.** `sub_agent.py:1-367` (run_subtask_in_background, the SubAgent class, the supervisor lifecycle) lets a parent SAP instance spawn child agents within the same process. These are not federated peers; they are children. The parent owns them. They die when the parent dies. This is *intra-process plurality*, not *inter-host plurality*.

**The MCP client/server roles.** `mcp_clients.py:1-189` plus the implied MCP server surface make SAP a citizen of the MCP ecosystem. Two SAP instances on two hosts could in principle each expose MCP servers and consume each other's tools. The federation primitive *exists*, but SAP does not use it for self-federation; it uses it for foreign-tool consumption.

**The A2A tool.** `a2a_tool.py` implements an agent-to-agent calling protocol. Again, this is *outward* federation (talk to a foreign agent), not *self* federation (talk to your other half on another host).

SAP's silence on inter-host self-federation is what makes the problem visible. Ember will use exactly the primitives SAP almost-uses (MCP, A2A, sub-agent supervisory disciplines) but turn them inward: each Ember instance exposes itself as an MCP server, consumes its peers as MCP clients, and uses the A2A shape for affect and memory replication.

---

## 2. The Multi-Ember Mental Model

Picture three machines on Volmarr's tailnet:

- **gungnir** — the workstation. RTX 2060. Full Funi stack. T0 tier per `[[6B_LOW_POWER_EMBODIMENT]]`. Mostly on, occasionally sleeps.
- **travel** — the Kubuntu 26.04 laptop. T1 tier. Sleeps when lid closes; wakes on arrival.
- **pi** — a Pi 5 in a corner. T3 tier. Always on. No avatar. Text-only.

Each runs an Ember instance. Each has its own `~/.ember/` directory, its own `ember.yaml`, its own Brunnr (pointing at Gungnir's shared Postgres for the Well). Each has its own Hjarta affect state in local cache, with replication via the affect router from `[[66_INVENTED_METHODS]]#1`.

When Volmarr says *hello, Ember*, only one of the three speaks. Which one?

The naive answer is "the one the operator is in front of." A better answer is "the one with both *proximity* and *fitness*." Proximity = the operator is physically/contextually present at this host. Fitness = the host can express the affect Ember wants to express. If Volmarr is at the workstation with a webcam and microphone, gungnir is both proximate and fit — it speaks. If Volmarr is at the laptop on a quiet evening, travel is proximate and fit. If Volmarr says *hello, Ember* over the wall from a Pi-attached display, the Pi is proximate but *not fit* — the Pi might speak via glyphic embodiment (`[[66_INVENTED_METHODS]]#2`), or the Pi might *defer* to gungnir if gungnir is still awake and the operator's voice can be relayed.

The mental model is therefore not "one Ember, multi-headed" and not "many Embers, fragmented" but **one Ember-self, distributed across instances, with a per-utterance arbitration about which instance acts on the self's behalf**.

---

## 3. Identity — Each Ember Knows Who She Is

The first hard problem: in a multi-Ember swarm, how does each instance know *which Ember it is*?

The naive answer is "by hostname." That breaks when machines are renamed, when machines move tailnets, when machines are restored from backup.

A better answer is **the persona identity is operator-issued, host-anchored, and Well-verified**:

- The operator runs `ember party init` once. This generates a fresh `persona_id` (UUID, signed with operator-controlled key) and records it in `~/.ember/identity/persona.yaml` on this host.
- The host's hostname, MAC, and a host-fingerprint are recorded *alongside* the persona_id. These are the host's signature, not its identity.
- The persona_id is published to the Well (the shared Brunnr) as a row in a new `ember_instance` table: `(persona_id, hostname, fingerprint, tier, capabilities[], first_seen_at, last_seen_at, alive_pulse_at)`.
- Each Ember instance, on startup, *announces* its persona_id on the tailnet via a small UDP broadcast (port configurable, opt-in) and *listens* for its peers' announcements.
- Each instance maintains a local *peer map*: `{persona_id: PeerHandle}` where each handle holds the peer's last-known capabilities, last-known liveness, and an MCP client connection (lazy-spawned).

The persona_id is **never reissued**. If the operator wants to mark an instance as retired, they `ember party retire <persona_id>` and the row in `ember_instance` carries a `retired_at` timestamp. The persona_id is then dormant — it can be revived if the same machine returns, but no new machine inherits the old name.

This avoids the trap of "Ember on the laptop became Ember on the new laptop" by making each instance *its own peer in the swarm* with traceable identity. The operator can ask Ember "which one are you?" and get back not a hostname but a persona_id plus a host-fingerprint plus the tier.

Cite-shape: `src/ember/spark/funi/party/identity.py`. The persona table lives in Brunnr. The UDP heartbeat lives in a small daemon thread.

---

## 4. Capabilities — What Each Ember Can Do

Each instance publishes a *capability manifest* to the Well alongside its persona_id. Capabilities are a flat list of named features:

- `funi.runtime:ollama` — the local Funi runtime
- `voice.tts:moss` / `voice.tts:piper` / `voice.tts:none` — voice synthesis tier
- `avatar.vrm:available` / `avatar.live2d:available` / `avatar.glyphic:only` / `avatar.none`
- `screen.attached:true` / `screen.attached:false`
- `camera:available` / `camera:none`
- `microphone:available` / `microphone:none`
- `tier:T0` / `tier:T1` / `tier:T2` / `tier:T3` / `tier:T4` — overall host tier per `[[6B_LOW_POWER_EMBODIMENT]]`
- `im.discord:token_held` (only one instance per token can hold this)
- `im.slack:token_held`, etc.
- `livestream.bilibili:token_held`, etc.

The capability manifest is **declarative** — instances do not race to claim capabilities; the operator decides which instance holds the IM/livestream tokens in `~/.ember/config/party.yaml`. The capability manifest *reports* what each instance can do.

Cite-shape: `src/ember/spark/funi/party/capabilities.py`. The manifest is a small YAML written at instance startup; mutations require restart.

This solves the leader-election problem for IM and livestream tokens trivially: there is no election; the operator declares. If the operator's declared instance is offline (lid closed, host down), the *fallback chain* in `party.yaml` names the next-priority instance. This is the **lid-close handover** machinery from `[[66_INVENTED_METHODS]]#4`.

---

## 5. Consensus — When Affect or Memory Diverge

This is the hard problem. Each Ember instance has its own local affect cache (per `[[66_INVENTED_METHODS]]#1 — Cross-Host Affect Routing`). Each writes its own session episodes to the shared Well. When two instances simultaneously mutate the same operator's affect axis from different conversations, *what is the truth*?

The answer is **per-axis last-writer-wins with confidence banding**:

1. Each affect mutation is timestamped (UTC microsecond), signed by the originating persona_id, and tagged with the originating session_id.
2. Replication is *lazy* — instances do not block on consensus; they accept local mutations immediately and propagate to peers on a 5-second reconciliation tick.
3. When a peer's mutation arrives with a *later* timestamp than the local value, the local value updates. *Earlier* timestamps are recorded for history but do not overwrite.
4. When two mutations arrive within a *confidence band* of each other (default ±5 seconds, configurable), the **average** is taken and a `divergence_event` is logged. The operator can ask `ember introspect affect divergences` to see where the swarm disagreed.

Memory is simpler than affect because the Well is canonical: every instance writes episodes to the same Brunnr. There is no divergence at the storage layer. Divergence at the *prompt-assembly* layer (which episodes Ember pulls into context for a given turn) is acceptable and even desirable — the laptop Ember and the workstation Ember can legitimately weight the same Well differently.

The Vow of **Honest Memory** requires that divergence be *visible*. The Vow of **Federated Self** requires that divergence be *survivable* — Ember does not crash, fragment, or panic when peers disagree.

Cite-shape: `src/ember/spark/hjarta/affect_reconciler.py`. The reconciliation tick is asyncio.

---

## 6. Which Ember Speaks?

Per-utterance arbitration. The operator pings Ember on a channel; the swarm must decide who replies.

**Arbitration rules (ordered):**

1. **Token authority.** If the channel is an IM platform whose token is held by a specific instance, that instance speaks. End of arbitration. The other instances see the message in the audit log (via shared Brunnr) but do not reply.
2. **Locality.** If the channel is the local Ember CLI (`ember chat` on this host), the local instance speaks. Always.
3. **Voice fitness.** If the channel is voice (microphone + speaker on a host with attached audio), the host with `microphone:available` AND `voice.tts:>=piper` speaks.
4. **Avatar fitness.** If the channel is a webcam/VRM surface, the host with `avatar.vrm:available` AND `camera:available` speaks.
5. **Affect fitness (tie-break).** If multiple instances pass the above, the one with the highest *local affect confidence* for this operator speaks. This biases toward "the instance the operator has been talking to most recently."
6. **Tier (final tie-break).** Higher tier wins. T0 > T1 > T2 > T3 > T4.

Each arbitration decision is logged with the decision rationale. The operator can override per-utterance: `ember party respond from=travel` forces the next utterance to come from the specified persona_id.

Cite-shape: `src/ember/spark/funi/party/arbitration.py`. The arbitration runs on every incoming message before the dispatch decision.

---

## 7. Divergence as Feature

The deepest counterintuitive design choice: **divergence between peers is sometimes the right answer, not a failure to reconcile**.

Examples:

- The workstation Ember has been deep in a coding session for three hours. Affect axis `focus` is high; `playfulness` is low. The laptop Ember has been used only for evening conversations. `focus` is moderate; `playfulness` is high. When the operator opens the laptop after the coding session, do we *want* the laptop Ember to have absorbed the workstation's focus-heavy affect? Probably not. The laptop Ember should reflect the *laptop context*.
- The Pi Ember sits in the bedroom. Its affect axis for `intimacy` is high because most conversations there happen at night. The workstation Ember's `intimacy` is moderate. We do not want the Pi's intimacy spilling into the workstation's daytime conversations.

This argues for **per-context affect partitions**. Each operator-Ember relationship has a primary axis set, but axes can be *context-bound*: `focus@workstation`, `playfulness@laptop`, `intimacy@pi`. Replication happens *within* a context, not *across* contexts.

The default is "axes replicate freely." Context-bound axes are an opt-in operator declaration in `party.yaml`:

```yaml
affect_partitions:
  - axis: focus
    bound_to: [persona:gungnir]
  - axis: intimacy
    bound_to: [persona:pi]
```

This is the *territorial* sense of self — Ember is *not* a single uniform soul across all hosts; she is *appropriately differentiated*, like a person who is more relaxed at home than at work without it being a contradiction.

Cite-shape: extends the affect router with partition checks before replication.

Vows touched: **Federated Self**, **Embodied Honesty** (the differentiation is acknowledged, not hidden), **Public-Friendliness** (the YAML is operator-readable).

---

## 8. The Shadow Problem — Two Embers Are Listening

What happens when two Embers both hear the operator? Specifically: the workstation has the microphone open; the laptop is in the next room with its microphone open; the operator speaks.

**Naive answer:** both speak. This is a chorus, and it is awful.

**Better answer:** **token-of-speaking arbitration**. When voice input arrives, each instance that hears it publishes a *bid* on the swarm bus (UDP broadcast or Well-resident row): `persona_id, heard_at_timestamp, signal_strength, capability_fitness`. After a 200 ms window, the bids are ranked, and the highest-fitness instance *claims* the utterance. The other instances *suppress their response* until the claimed instance has finished (or has signaled it cannot respond, in which case fallback engages).

Signal strength matters: the instance whose microphone heard the operator *loudly* is more likely to be the one the operator was speaking to. This is mechanical proximity-detection without needing facial recognition or location services.

Cite-shape: `src/ember/spark/funi/party/voice_arbitration.py`. The bid window is 200 ms; the arbiter is small.

Vows touched: **Federated Self**, **Public-Friendliness** (no surveillance: the bids are local-to-swarm, not phoned home), **Embodied Honesty** (only one instance "answers" so the experience is coherent).

---

## 9. Failure Modes — When the Swarm Tears

What can go wrong with the multi-Ember party?

**Tailnet partition.** Two halves of the swarm cannot reach each other. Both halves continue operating. Reconciliation happens on healing. Affect divergence may be significant; the divergence is logged and the operator can `ember introspect affect divergences` to see what happened.

**Stale persona_id.** A retired host is replaced; the new host has a fresh persona_id; the old persona_id remains in the Well as `retired_at: <timestamp>`. The new host announces its capabilities; the operator decides whether to grant it the IM/livestream tokens.

**Identity confusion.** Two hosts claim the same persona_id (operator copied `~/.ember/identity/` from one machine to another). The Well detects the duplicate at the next announcement and refuses both. The operator must explicitly choose which host keeps the persona_id; the other gets a new one or is retired.

**Token thrashing.** The operator's declared primary instance keeps suspending; the fallback chain keeps taking over and then handing back. Mitigation: the fallback chain has a *minimum hold time* (default 30 minutes). The fallback instance does not hand back until it has held for the minimum, even if the original wakes earlier. This prevents pingponging.

**Affect rollback storm.** A misconfigured replication produces a rapid sequence of mutations that decay each other out. Mitigation: replication rate-limited to N mutations per axis per minute (default 10). Excess mutations are coalesced into a single weighted-average mutation.

**Sleep-while-streaming.** The instance holding a livestream token suspends mid-stream. Mitigation: the lid-close-aware migration from `[[66_INVENTED_METHODS]]#4` triggers a *graceful credential handoff*. The livestream sees ≤2 seconds of mute; the next instance picks up. Viewers may see a small "(handing over)" overlay tag.

Cite-shape: each failure mode has a corresponding `tests/party/test_*.py` test.

Vows touched: **Graceful Offline** (every failure has a typed recovery), **Modular Authorship** (no single instance failure crashes the swarm), **Honest Memory** (every failure leaves a log entry).

---

## 10. The Operator's Party Console

Multi-Ember swarming demands operator visibility. The proposed CLI surface:

- `ember party status` — lists all known persona_ids, their hosts, tiers, capabilities, liveness, and current authority assignments.
- `ember party retire <persona_id>` — marks an instance retired.
- `ember party transfer <token> from=<persona_id> to=<persona_id>` — manually transfers an IM or livestream token.
- `ember party arbitrate force=<persona_id> for=<duration>` — overrides arbitration for a window.
- `ember party divergences` — shows affect divergence events across the swarm.
- `ember party silence <persona_id> [for=<duration>]` — temporarily mutes an instance.

The console is plain CLI per Vow of **Public-Friendliness**. There is no admin GUI; if there is, it ships separately and consumes this CLI.

Cite-shape: `src/ember/cli/party.py`. ~250 LOC plus tests.

---

## 11. The Multi-Ember Bootstrap Sequence

How does a fresh second instance join the party?

1. Operator installs `pip install ember-agent[party]` on the new host.
2. Operator runs `ember party join --leader-host=<primary> --consent-token=<short-code>`.
3. The new instance generates its persona_id, signs with operator's key (recovered from `--consent-token` flow).
4. The new instance publishes its capabilities to the Well.
5. The new instance announces on the tailnet.
6. Peers acknowledge.
7. Operator sees `ember party status` on the original host reflect the new peer.
8. Operator can now `ember party transfer` tokens if desired.

The consent-token flow is a short-lived (60 s) PIN displayed on the primary host's CLI — the operator types it on the new host. This avoids accidental joins, prevents drive-by federation attempts, and gives the operator a moment to *intend* the federation.

Cite-shape: `src/ember/cli/party_join.py` + the consent-PIN mechanism. ~180 LOC.

Vows touched: **Surface Without Surveillance** (federation is opt-in per-instance), **Public-Friendliness** (the bootstrap is short).

---

## 12. Implications for the Wave 3 Slice

Multi-Ember party is **not** slice-3 work. The minimum surface needed before this can be approached is:

- Hermes-derived MCP server (`[[hermes:MCP-001]]`) — required so each instance can expose itself.
- Hermes-derived MCP client (`[[hermes:MCP-003]]`) — required so each instance can consume peers.
- The Cartographer's `[[62_PARTY_PROTOCOL]]` — required for the channel-arbitration substrate.
- Persona identity issuance (`§3` above) — small enough to ship in slice 3 or 4.
- Capability publication and peer announcement (`§4` above) — depends on MCP being in place.
- Affect router (`[[66_INVENTED_METHODS]]#1`) — requires the persona table.

The realistic earliest slice for *experimental* multi-Ember support is **slice 5 or 6**, per `[[6C_EMBER_WAVE_3_SLICE]]` and `[[67_SLICE_PLAN_REVISIONS]]`. Slice 3 plants the seeds (MCP, persona identity, capability publication); slice 4 grows the trunk (peer arbitration, voice-input arbitration, affect partitions); slice 5+ gives it leaves.

What can land *in slice 3* as preparation:

- **Persona identity issuance** — `ember party init` ships now. The persona_id is generated; the Well row is written. No peer communication yet.
- **Capability manifest publication** — write to the Well at startup. Visible via `ember party status` but only one instance shows.
- **The arbitration scaffolding** — the rules from `§6` exist in code but only ever return "this instance speaks" because there are no peers.

This is the **plant-the-seed-now** discipline: the persona_id existing in slice 3 means slice 5's federation work has a stable foundation, and operators who set up Ember today are *already party-ready* without knowing it.

---

## 13. Cross-References

- `[[62_PARTY_PROTOCOL]]` — Cartographer's foundational protocol that this doc extends to the multi-instance case.
- `[[63_PERFORMANCE_TIER_ENGINE]]` — Cartographer's tier engine that grounds capability publication.
- `[[66_INVENTED_METHODS]]#1` — affect routing across hosts.
- `[[66_INVENTED_METHODS]]#4` — lid-close handover of party-leader authority.
- `[[66_INVENTED_METHODS]]#8` — tethered affect anchoring (relevant when affect crosses hosts).
- `[[6B_LOW_POWER_EMBODIMENT]]` — tier definitions used by capability publication.
- `[[6C_EMBER_WAVE_3_SLICE]]` — when these seeds land in the slice plan.
- `[[68_DECISION_RECORDS]]` — ADR-Proposed records for the party identity, capability publication, and consent-token bootstrap.
- `[[69_INTEGRATION_ROADMAP]]` — phasing across the codex constellation.
- `[[hermes:MCP-001]]`, `[[hermes:MCP-003]]` — the MCP server and client foundations.
- `[[ember:Tailnet-accessible by default]]` — the tailnet posture that makes multi-Ember a natural fit.

---

## What This Means for Ember

**Adopt:**

- SAP's MCP integration (`mcp_clients.py`) as the substrate primitive for inter-instance communication. Each Ember instance exposes itself via MCP-server and consumes peers via MCP-client. *Bind it to Ember's Funi instead of to a global registry.*
- SAP's sub-agent supervisory discipline (`sub_agent.py:1-367`) — the lifecycle disciplines (graceful start, drain on close, supervisor visibility) carry over to inter-host peer-handling.

**Adapt:**

- SAP's A2A tool (`a2a_tool.py`) — adapted from *outward agent calling* (call a foreign agent) to *self-federation* (call another instance of yourself). The protocol shape works; the trust model changes — peers in the swarm are operator-blessed; foreign agents are not. The Ember adaptation lives in `src/ember/spark/funi/party/peer_call.py`.

**Avoid:**

- SAP's silent multi-host failure mode. SAP simply *does not federate*; the operator who installs SAP on two machines gets two independent copies. This is the failure mode the entire `[[6A_MULTI_AGENT_PARTY]]` proposal exists to avoid.
- SAP's lack of identity primitives. There is no persona_id, no host-fingerprint, no `ember_instance` table. Reaching the multi-instance state without these would mean inheriting SAP's "no federation, no problem" silence.
- The chorus failure mode where all instances respond simultaneously. The arbitration discipline in `§6` and `§8` prevents this.

**Invent:**

1. **Persona-Identity Issuance Ceremony.** `ember party init` issues a fresh persona_id signed by operator key, recorded in Well as `ember_instance` row. Each host has exactly one persona_id; the persona_id is host-anchored but operator-issued.
2. **Capability Manifest Publication.** Each instance publishes its capabilities to the Well at startup. Capabilities are declarative; the operator decides authority assignment in `party.yaml`.
3. **Per-Utterance Channel Arbitration.** Six-rule arbitration (token authority → locality → voice fitness → avatar fitness → affect fitness → tier) decides which instance speaks for each utterance.
4. **Token-of-Speaking Voice Arbitration.** When voice input arrives at multiple instances, a 200 ms bid window resolves to a single responder based on signal strength + capability fitness.
5. **Context-Bound Affect Partitions.** Operator-declared partitions in `party.yaml` keep certain affect axes from replicating between hosts where context-shaped differentiation is desirable (focus@workstation, intimacy@pi).
6. **Consent-Token Federation Bootstrap.** New instance joins the swarm only after a short-lived PIN-shaped consent exchange initiated on the primary host. No drive-by federation; no accidental joins.
7. **Lazy CRDT-style Affect Replication.** Per-axis last-writer-wins with confidence banding; divergence events are logged and surfaceable via `ember party divergences`.
8. **Minimum-Hold Fallback Discipline.** The fallback chain for IM/livestream token authority has a minimum hold time (default 30 minutes) to prevent thrashing when the primary suspends/wakes rapidly.
9. **Operator Party Console.** `ember party status / retire / transfer / arbitrate / divergences / silence` — plain CLI surface for the operator to see and steer the swarm.

**True Names affected:** Funi (party arbitration), Hjarta (affect router and partitions), Munnr (channel arbitration), Brunnr (persona table and capability manifest storage). Strengr unchanged in this design; Smiðja unchanged.

**Vows reinforced:** **Federated Self** (the central Vow this doc serves), **Honest Memory** (divergence is logged), **Graceful Offline** (peer disconnection survives), **Modular Authorship** (instance failure does not crash the swarm), **Surface Without Surveillance** (federation is opt-in per-instance), **Public-Friendliness** (the operator console is plain CLI).

**Slice readiness:** Persona identity + capability manifest are slice-3-ready. Per-utterance arbitration without peers is slice-3-ready (scaffolding only). Actual peer communication is slice-5-or-6.

**Most consequential single decision:** treating the operator's authority as **the only centralized authority in the swarm**. There is no master Ember. There is no canonical instance. There is only the operator, blessing the topology, and the instances, federating beneath that blessing.

The proposals stand as written. The slice plan does not change here.
