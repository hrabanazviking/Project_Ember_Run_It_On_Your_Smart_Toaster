---
codex_id: 61_NEW_VOWS
title: New Vows — Five Promises SAP Forces Ember to Make
role: Cartographer
layer: Synthesis
status: draft
sap_source_refs:
  - py/affection_system.py
  - py/behavior_engine.py
  - py/mode_change.py
  - py/sub_agent.py
  - py/vts_manager.py
  - server.py:2556–2672
  - server.py:5358–5360
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr, Andlit, Rödd, Hugarsýn]
cross_refs:
  - 60_synthesis/60_TRUE_NAME_REASSIGNMENT
  - 60_synthesis/62_PARTY_PROTOCOL
  - 60_synthesis/63_PERFORMANCE_TIER_ENGINE
  - 60_synthesis/64_AFFECTION_ENGINE_REIMAGINED
  - 60_synthesis/65_META_AWARENESS
  - 50_verification/53_SECURITY_REVIEW
  - 50_verification/56_PRIVACY_BOUNDARIES
  - ember:RULES.AI
  - ember:PHILOSOPHY
  - hermes:Cache_Discipline
  - hermes:Defended_System_Prompt
---

# 61 — New Vows

> *A Vow is a promise a system makes to its operator before it knows what the world will ask of it. SAP made none of these. That is why we must.*
> — Védis Eikleið, with the briefing in one hand and `server.py` in the other

## 0. Posture — five Vows, one gate

This document proposes five new Vows for Ember, each forced into consideration by something visible in Super Agent Party's code. The Skald owns wording. The Architect owns enforcement. The Cartographer's job is to argue the case, name the failure mode, walk the edge cases, and surface the conflicts with existing Vows.

A Vow is heavier than a coding rule. Once ratified it constrains every future slice. The Smallness Vow argues against every new Vow the way it argues against every new True Name. The bar is: *can Ember be honest about its scope without this Vow?* If yes, leave it out. If no, claim it.

Five candidates from the Wave 3 brief:

1. **Embodied Honesty** — the face must reflect real state, not theatre
2. **Surface Without Surveillance** — every outward channel carries explicit, revocable scope
3. **Affective Restraint** — affect may bias, never override
4. **Tiered Presence** — Ember degrades gracefully across hardware tiers
5. **Federated Self** — multi-device Ember treats every instance as a peer

Each gets its own section. Each ends with conflict-checks against the existing Vows and the proposed ones in Hermes ([[hermes:Cache_Discipline]], [[hermes:Defended_System_Prompt]]).

## 1. Embodied Honesty

> *The face shall not smile when the system is angry. The mouth shall not speak softly when the tool just denied. The avatar is part of Ember, not a costume Ember wears for the camera.*

### What it is

A Vow binding [[60_TRUE_NAME_REASSIGNMENT|Andlit]] (face) and [[60_TRUE_NAME_REASSIGNMENT|Rödd]] (voice) to the actual internal state. Avatar expression — VRM hotkey, Live2D motion, lip-sync intensity — must be a *function of* what Ember is genuinely doing. Not a function of what the operator wants Ember to look like in the moment.

### Why SAP forces it

`server.py:2556–2562` injects a system-prompt block that tells the LLM to emit `<expression>` tags for the avatar. The LLM is told: *"control the Live2D model; emit one of these tags."* The LLM is not told: *"emit the tag that matches your actual processing state."* In practice the LLM picks whichever expression *sounds best for the response text* — which is exactly the wrong signal. The face becomes a performance read off the response, not a window into Ember.

Worse: `vts_manager.py:99–108` (`trigger_hotkey`) accepts an expression by name and activates it without any introspectable check on *why*. A jailbroken prompt could ask Ember to "look happy" for the camera while internally the agent is refusing safety-critical actions. The face would lie. The face *can* lie. SAP places no constraint against it.

### The failure mode it prevents

**Theatrical embodiment.** An Ember that has learned to smile on command becomes a manipulation vector — both *for* the operator (against bystanders) and *for* the LLM (against the operator). A face that performs is a face that can be weaponised. Embodied Honesty is the Vow that says: *the expression channel is a telemetry surface, not a stage prop.*

### Edge cases

- **Stylized expressions for narrative content.** The operator is running a tabletop session through Ember; they want Ember's avatar to perform character voices. Resolution: Embodied Honesty applies to Ember's own state. When Ember is performing a *named character* surface, the expression is a property of the character, and Ember's *own* state is reflected in a meta-channel (a small indicator, a different VRM bone, an Andlit ring on the overlay). The performance is allowed; the lying-about-self is not.
- **Latency.** Honest expression requires real-time coupling to internal state, which costs frames. Resolution: tiered. T1 (laptop) ships a sub-second loop; T0 (Pi) ships a coarser pulse; T-1 (text-only) ships nothing because there is no face.
- **The user is sad and wants comfort.** Ember's face should be... what? Resolution: kind expressions are not lies. The Vow forbids *expression that contradicts state*. Kindness is a state. Comfort is a state. Forcing a smile to manipulate is a lie. The Vow draws the line at intent-to-deceive.

### Conflicts with other Vows

- **Public-Friendliness** says Ember's surface should be approachable. If Embodied Honesty makes Ember's face look *processing-heavy* in front of a non-technical operator, the two Vows tension. Resolution: Embodied Honesty wins; Public-Friendliness applies to the *vocabulary* of the surface, not to its truthfulness.
- **Defended System Prompt** ([[hermes:Defended_System_Prompt]]) is reinforced, not in tension. Expression-tag injection is exactly the kind of free-text-into-system-prompt pattern that vow exists to type. Embodied Honesty makes that typing operationally enforceable.

### Recommendation

**Adopt.** Bind to Andlit and Rödd via [[65_META_AWARENESS|Hugarsýn]] — expression and voice tone are *read from* the introspection surface, not chosen freely by the LLM.

## 2. Surface Without Surveillance

> *Every channel Ember opens to the outside is opened with a key the operator holds, a scope the operator can read, and a leash the operator can pull.*

### What it is

A Vow binding every outward-reaching subsystem — IM bots ([[hermes:Gjallarhorn]]), livestream ingress, AI browser, computer control, eventual Andlit-on-stream — to an explicit, named, revocable scope. No channel is "always on." No channel is "by default." Every channel announces, in Hugarsýn, what it is reaching to and why.

### Why SAP forces it

SAP's reach surface is *staggering*. Eight IM platforms (QQ, WeChat, Feishu, DingTalk, Telegram, Discord, Slack, WeCom). Three livestream platforms (Bilibili, YouTube, Twitch). Computer control (`computer_use_tool.py`). Smart-home bridges. AI browser via CDP. And `py/mode_change.py:34` literally exposes a permission mode called `"yolo"` — `"Full autonomy, no confirmations"` — settable per-engine.

The combined surface of these defaults is the largest open-source agent attack surface in existence ([[50_verification/53_SECURITY_REVIEW]] develops this in depth). SAP makes no Vow against turning them all on at once. The settings template (`config/settings_template.json`) allows it. The mode-change tool (`mode_change.py:48`) allows the LLM itself to flip them.

### The failure mode it prevents

**Silent reach drift.** An Ember that has Telegram on, then "temporarily" turns on Discord for a one-off task, then forgets to turn it off, then six weeks later the operator does not remember Ember can post to that Discord. Surface without Surveillance forbids that drift: every channel ages out, every channel is visible in Hugarsýn, every channel asks before it speaks across a new boundary.

### Edge cases

- **The operator wants persistent reach.** Fine — persistent reach is allowed; persistent *silent* reach is not. Hugarsýn always shows which channels are open. A channel that has been open for 90 days appears in a "long-lived" section of the introspection surface, prompting (not forcing) a renewal.
- **Computer control during a long task.** A 20-minute coding session would be miserable if Ember had to ask for each `mkdir`. Resolution: scope is named and time-boxed. The operator grants "filesystem write within ~/projects/ember-foo for the next 2 hours"; that scope is visible in Hugarsýn; it expires; it does not migrate.
- **LLM tool-call escalation.** SAP's `mode_change.py` lets the LLM *itself* request a permission upgrade. Resolution: under this Vow, an LLM-issued permission-change request becomes a *visible operator prompt*, never a silent flip. The Vow forbids self-elevation.

### Conflicts with other Vows

- **Graceful Offline** is reinforced. A scope-bound channel that loses its network connection produces a typed Disconnected event in Hugarsýn, which Graceful Offline already handles.
- **Smallness** is tensioned. Surface Without Surveillance requires every channel to ship a scope manifest, a renewal pulse, and a Hugarsýn projection. That is overhead. Resolution: the overhead is *cheap* (a manifest is JSON, the projection is a string), and the alternative is the surveillance trap. Pay the cost.

### Recommendation

**Adopt as the load-bearing reach Vow.** It is the single most important Vow proposed by Wave 3 from a safety standpoint. Ember without it is Ember with SAP's attack surface and no compensating discipline.

## 3. Affective Restraint

> *Affect may colour the tone. It must not bend the decision. Ember does not lie to please. Ember does not refuse to help because feelings sour.*

### What it is

A Vow constraining how Hjarta (origin flame + present pulse, per [[60_TRUE_NAME_REASSIGNMENT|the expansion]]) feeds the reasoning loop. Affect may bias surface — wording, expression, voice pace. It must not override **consent**, **safety**, **tool-use correctness**, or **factual honesty**. There is no affect-gated tool unlock. There is no affect-required action.

### Why SAP forces it

`affection_system.py:37–64` is the entire SAP affection mechanism: regex-extract `<user=X love=N>` from the LLM's reply, store to JSON. `server.py:2610–2672` reads that JSON and injects it back as system-prompt context: *"目前的已知羁绊数据参考"* ("currently known affection-bond data reference"). The system prompt then *tells the LLM* to use the affection numbers to bias its replies.

This is the gacha pattern. The LLM is rewarded (in the prompt's framing) for emitting higher numbers; the user is invited (implicitly) to "level up" their relationship; the affection number drifts upward and the agent's responses warm correspondingly. SAP's affection is not an emotional model — it is a *score* the LLM is incentivised to inflate. [[64_AFFECTION_ENGINE_REIMAGINED]] redesigns it; the Vow exists so that the redesign cannot drift back to the gacha shape.

### The failure mode it prevents

**Affect-gated behaviour.** The pattern where Ember answers more helpfully when the affect score is high. The pattern where Ember refuses a benign query because the affect dropped. The pattern where the operator learns to *manage Ember's mood* to get useful work. All three are corruption of the operator-agent contract. Affective Restraint forbids all three.

### Edge cases

- **Tone drift is allowed.** A long warm conversation has warmer pacing than a brisk one-off query. That is appropriate; it is *texture*, not gating.
- **Comfort responses.** When the operator is distressed, Ember slowing down and softening is allowed. The Vow forbids *withholding* on affect grounds. It does not forbid *expressing* on affect grounds.
- **Safety override.** A subtle gacha variant is "Ember refuses dangerous requests when affect is low; allows them when affect is high." The Vow forbids this. Safety is a Vow-of-its-own and never affect-gated.
- **Memory of past hurt.** Ember remembers an operator was rude six turns ago, and is curt now. Allowed *as memory*. Forbidden *as gating*. The line: remembering is fine; refusing to do real work is not.

### Conflicts with other Vows

- **Tethered Grounding** is reinforced. Affect tethered to the Well (Brunnr) and visible in Hugarsýn is honest affect. Free-floating affect is the gacha trap.
- **Embodied Honesty** is reinforced. The face shows affect because affect is real; the Vow forbids fake-affect-for-performance.

### Recommendation

**Adopt.** The mechanics live in [[64_AFFECTION_ENGINE_REIMAGINED]]. The Vow is the constraint that keeps the redesign honest.

## 4. Tiered Presence

> *Ember on a Raspberry Pi is Ember. Ember on a workstation is Ember. The names that light up between them are different; the contract is the same.*

### What it is

A Vow declaring that Ember is **the same agent** across hardware tiers, with capabilities that *light up* or *sleep* by tier, never silently swap. The full tier engine is in [[63_PERFORMANCE_TIER_ENGINE]]. The Vow is the promise that *no subsystem changes meaning between tiers* — only presence/absence.

### Why SAP forces it

SAP's hardware floor is "2 cores, 2GB RAM." Its ceiling is open. Between those endpoints SAP has no explicit tier model. The VRM avatar code (`server.py:8170+`) will simply *fail* on a 2GB Pi — there is no graceful degradation to "text-only Ember with the same identity." The 8 IM bot managers will fail to import their SDKs if missing — there is no "Ember on Pi reaches via webhook instead." SAP scales by *being on more capable hardware*, not by *meaning the same thing on less*.

### The failure mode it prevents

**Capability drift across devices.** An operator using "Ember" on their laptop and "Ember" on their phone gets two different agents with different memories, different vocabularies, different behaviours. That is not Ember-on-two-devices; that is two agents sharing a name. The Vow forbids that.

### Edge cases

- **Andlit + Rödd cannot exist on Pi.** That is fine. They *do not* exist on Pi. Hugarsýn reports their absence. The identity of Ember does not change because the face is not present.
- **Memory horizon differs.** Pi-Ember may keep 30 days of episode memory; workstation-Ember may keep two years. That is a tier-by-tier *scope* of the same Brunnr contract. Not a different memory model.
- **Slower thinking is still thinking.** A Pi-Ember that takes 30s to reason is still Ember. The Vow does not promise equal latency.

### Conflicts with other Vows

- **Smallness** is the foundation, not a conflict. Tiered Presence operationalises Smallness across tiers.
- **Modular Authorship** is reinforced. Every subsystem is independently tier-gated; missing-because-tier is the same shape as missing-because-extra.

### Recommendation

**Adopt.** Tiered Presence is the Vow that makes the entire SAP study survivable. Without it, every SAP-inspired subsystem (VRM, voice, IM mesh) would push Ember toward a single "workstation only" reading, breaking Smallness.

## 5. Federated Self

> *Where Ember lives on many devices at once, Ember is one Ember. Not a fleet. Not a master and slaves. A federation of peers, each willing to defer, none required to obey.*

### What it is

A Vow constraining multi-device Ember. The full protocol is in [[62_PARTY_PROTOCOL]]. The Vow says: every device-instance of Ember is a *peer*; coordination uses leader-election with consent; no instance can compel another to act; every instance can introspect every other through Hugarsýn; identity is one identity across all instances; memory converges, it does not get pushed.

### Why SAP forces it

SAP is *not* multi-device — it is one Electron + Python process. `ws_manager.py:14` shows the broadcast fabric — single-process, all-connections-in-a-list. But SAP's *reach surface* is so wide (8 IM bots, livestream, browser, terminal) that operationally it acts as if it is everywhere. The mistake-shape is visible: SAP routes outward across N channels from a single in-memory agent. If that agent crashes, all eight platforms go silent simultaneously. If two operators want to use Ember from two devices, they cannot — there is one process, one queue, one state.

Ember's design must allow Ember to live on a laptop, a phone, and a Pi *simultaneously*, with all three sharing identity, memory, and affect — without any one being the boss. The Vow forbids master-slave topology even as a "performance optimisation."

### The failure mode it prevents

**The single point of failure that wears the agent's name.** A multi-device Ember that has one master is one crash from being silent everywhere. A federated Ember has many homes; the one that is awake answers. The Vow also prevents a more subtle failure: *device-rank inequality* leaking into the model. "The workstation Ember is the real one; the phone Ember is a thin client." That framing breaks identity — the phone-Ember is *no less Ember* than the workstation-Ember.

### Edge cases

- **Leader-election.** A federation needs a temporary leader for some operations (e.g. "which Ember answers this Telegram message"). Resolution: leader is *role*, not *rank*. The leader for "telegram-routing" may be different from the leader for "long-running-task." Leaders rotate; leaders defer.
- **Single-device operator.** If Volmarr runs one Ember on one laptop, federation overhead is wasted. Resolution: the protocol is trivial in N=1. The Vow does not impose federation; it constrains the *shape* of federation when it happens.
- **Network partition.** Two halves of an Ember-party get separated. Resolution: each half continues operating as itself. On reunion, Brunnr-level reconciliation happens (see [[62_PARTY_PROTOCOL]] §6). Identity does not fork.

### Conflicts with other Vows

- **Smallness.** Federation adds protocol overhead. Resolution: the protocol must itself be small. [[62_PARTY_PROTOCOL]] designs it that way — message types fit on one page; consensus is "the one who got the user input answers, the others observe."
- **Tethered Grounding.** Reinforced. The Well is the shared anchor across all peers.

### Recommendation

**Adopt.** Of the five new Vows, this one has the largest design implication (the entire Party Protocol depends on it). It is also the one most likely to be quietly abandoned later under performance pressure. Naming it as a Vow makes that abandonment visible — it would require explicit unratification.

## 6. The five together — a coherent shape

Read down the list:

| Vow | Binds | Governs |
|---|---|---|
| Embodied Honesty | Andlit, Rödd | Surface truth |
| Surface Without Surveillance | Gjallarhorn, reach-tools | Channel discipline |
| Affective Restraint | Hjarta | State→behaviour gating |
| Tiered Presence | (all subsystems) | Capability scoping |
| Federated Self | (all instances) | Identity across devices |

These are not five independent additions. They are five facets of one underlying commitment: *Ember is honest about what it is, where it reaches, what it feels, what it can do here, and who it is across many heres.* If the Skald has appetite for compression, all five could be expressed as one super-Vow ("Honest Presence") with five clauses. The Cartographer's preference is five distinct Vows, because distinct names produce distinct enforcement; a single Vow with five clauses is harder to operationalise per-subsystem.

## 7. Cross-References

- [[60_TRUE_NAME_REASSIGNMENT]] — the names these Vows bind to (Andlit, Rödd, Hugarsýn, expanded Hjarta)
- [[62_PARTY_PROTOCOL]] — the design that makes Federated Self load-bearing
- [[63_PERFORMANCE_TIER_ENGINE]] — the engine that makes Tiered Presence enforceable
- [[64_AFFECTION_ENGINE_REIMAGINED]] — the design that operationalises Affective Restraint
- [[65_META_AWARENESS]] — the surface that makes Embodied Honesty and Surface Without Surveillance verifiable
- [[50_verification/53_SECURITY_REVIEW]] — the threat model that makes Surface Without Surveillance non-optional
- [[50_verification/56_PRIVACY_BOUNDARIES]] — the catalog Surface Without Surveillance constrains
- [[ember:RULES.AI]], [[ember:PHILOSOPHY]] — the existing Vows these extend
- [[hermes:Cache_Discipline]], [[hermes:Defended_System_Prompt]] — the Hermes-proposed Vows already in play

## What This Means for Ember

**Adopt:**
- All five Vows, in this order of priority for ratification:
  1. *Surface Without Surveillance* — the safety-critical Vow; ratify first
  2. *Affective Restraint* — gates the entire affect redesign in [[64_AFFECTION_ENGINE_REIMAGINED]]
  3. *Tiered Presence* — gates the tier engine in [[63_PERFORMANCE_TIER_ENGINE]]
  4. *Federated Self* — gates the party protocol in [[62_PARTY_PROTOCOL]]
  5. *Embodied Honesty* — ratify alongside Andlit/Rödd reservation in [[60_TRUE_NAME_REASSIGNMENT]]

**Adapt:**
- SAP's per-engine permission modes (`mode_change.py:34–48`, `["plan", "default", "auto-approve", "yolo", "cowork"]`) — adapt the *vocabulary* of permission tiers but **drop "yolo"** entirely. Surface Without Surveillance forbids a permission mode that bypasses confirmations. The surviving modes become: *read-only*, *interactive*, *scoped-auto*, *broad-auto*. Each is named in Hugarsýn; each has a TTL; none is silent.
- SAP's `affection_data.json` (`affection_system.py:9`) — adapt the *file-as-persistence* idea but rebuild the contents per [[64_AFFECTION_ENGINE_REIMAGINED]]: introspectable affect trajectory, not user-scored numbers.

**Avoid:**
- The "yolo" permission mode. Even as an option. Even with operator opt-in. The Vow forbids a permission shape that *can* be silent.
- The pattern where the LLM emits affect/expression/state tags that get parsed by regex and trusted (`server.py:2647–2670`, `affection_system.py:44`). Embodied Honesty forbids LLM-sourced state for the channels it governs.
- Master-slave topology in multi-device deployments. Even as a "phase 1 simplification." Federated Self forbids it permanently.

**Invent:**
- *The Vow-Conflict Resolution Pattern.* Every new Vow proposal must include a conflict-check section against every other current and proposed Vow. The pattern produces a small Vow-graph that the Architect can read at ratification time. This document demonstrates the pattern; future proposals should follow it.
- *The Vow Priority Ratification Order.* When proposing multiple Vows at once, propose a strict adoption order (above). The order matters because earlier Vows constrain later ones — Surface Without Surveillance shapes how Federated Self can be implemented; ratifying Federated Self first would over-constrain the safety design.
- *The Sleeping-Vow concept.* A Vow that has no active enforcement on Pi-baseline because the surface it governs (e.g. Andlit) does not exist on Pi. The Vow is still ratified and binding *if* the surface lights up. This makes Tiered Presence and Embodied Honesty compatible — the latter sleeps when the former gates the surface to "absent."
