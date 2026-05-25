---
codex_id: 02_THE_PARTY_METAPHOR
title: The Party Metaphor — Multi-Agent, Multi-Device, Multi-Channel as One Idea
role: Skald
layer: Vision
status: draft
sap_source_refs:
  - README.md:36-68
  - README.md:52-65
  - py/behavior_engine.py:53-225
  - py/autoBehavior.py:3-97
  - py/sub_agent.py:1-200
  - py/scheduler.py:1-135
  - py/task_center.py
  - py/live_router.py:1-100
  - py/overlay_router.py:1-81
  - py/ws_manager.py:1-49
  - py/extensions.py:23-50
  - py/skills.py:60-93
  - main.js:71-117
  - main.js:1-130
  - server.py:2461 (group mode)
  - server.py:2429-2680
  - server.py:7272-7295
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
proposed_true_names: [Andlit, Rödd, Vegfarendr, Veizla]
cross_refs:
  - 00_vision/00_OVERTURE
  - 00_vision/01_SAP_ESSENCE
  - 00_vision/03_ANTI_SAP
  - 00_vision/04_VISION_SYNTHESIS
  - 10_domain/14_MESSAGING_DOMAIN
  - 10_domain/1D_ROUTING_DOMAIN
  - 60_synthesis/62_PARTY_PROTOCOL
  - 60_synthesis/6A_MULTI_AGENT_PARTY
  - 60_synthesis/6B_LOW_POWER_EMBODIMENT
  - hermes:00_OVERTURE
---

# The Party Metaphor — Multi-Agent, Multi-Device, Multi-Channel as One Idea

> *A party is not a broadcast. A party is the same person, telling slightly different stories, in different rooms, to different ears, while remaining recognizably herself.*

This document does the most invent-heavy work in the Vision layer. It takes SAP's chosen name — **Super Agent Party** — and asks whether the metaphor of "party" is *load-bearing* or merely *cute*. The answer, I will argue, is that the metaphor is more load-bearing than SAP itself realizes, and that the seed of a real Ember invention lives inside it.

The Cartographer's `[[60_synthesis/62_PARTY_PROTOCOL]]` will turn that seed into a protocol. The Scribe's `[[60_synthesis/6A_MULTI_AGENT_PARTY]]` will extend it to multi-Ember swarming. This Vision document is where the metaphor itself is argued, named, and given a True-Name slot to grow into.

## I. The metaphor as SAP uses it

SAP's name signals plurality. The party is the agent and its many guests, or the agent across its many surfaces, or the operator across their many devices — the README does not pick one and the codebase implements two and a half of them.

**What SAP calls a "party," explicitly:**

The README's hero shots (`README.md:36-68`) cycle through eight platform-and-mode combinations: VRM desktop pet, VTS Live2D linkage, the Task Center for background agent work, computer-control of the host, multi-role group chat with Tavern character cards, instant-messaging bot one-click deployment, live-streaming bot one-click deployment, AI browser, extensions sidebar. The intent is "the agent shows up in many places at once." That is one form of party.

The behavior engine implements a stricter form. `py/behavior_engine.py:53-225` is the codebase's most explicit "party" object — a singleton (`global_behavior_engine` at line 225) that registers per-platform handlers and broadcasts triggered behaviors across them. The `autoBehavior` tool (`py/autoBehavior.py:43-97`) lets the LLM construct broadcast behavior items with `platforms: ["chat", "wechat", "feishu", "dingtalk", "telegram", "discord", "slack", "wecom"]`. When the trigger fires at 22:00 with `prompt: "ask Volmarr how he's feeling"`, the same prompt is sent to every registered platform's handler. That is party-as-broadcast.

The group-chat mode adds a third form. `server.py:2461` checks `if settings["isGroupMode"]` and `[[hermes:00_OVERTURE]]`-style we know the implementation feeds Tavern character cards as personas into the system prompt. The "party" here is *one conversation with multiple voiced personas*. That is party-as-roleplay.

The sub-agent system adds a fourth. `py/sub_agent.py:21-150` and `py/task_center.py` together implement background task execution: the operator (or the foreground agent) creates a task with a description, the `AgentScheduler` (`py/scheduler.py:7-22`) polls the task center, and when a task is due, `run_subtask_in_background()` is invoked (imported at `server.py:7273`). The sub-agent is a child process-style execution within the same Python server, gated to *face-less* mode (`is_sub_agent=True` in the request — see `server.py:4024-4059`). That is party-as-delegation.

**Four interpretations, one verb.** SAP collapses multi-channel (broadcast), multi-persona (roleplay), multi-task (delegation), and multi-surface (avatar + chat + IM + livestream) into a single name and a partially shared infrastructure. The README does not articulate the collapse; the code implements it inconsistently.

This is not unusual. Brand names usually outrun their implementations. What is unusual is that SAP's name *anticipated something architecturally true* and the code *almost reaches it* before falling short. The metaphor is more correct than the implementation. The job of this document is to argue *why* the metaphor is correct and what shape its full realization would take.

## II. Three axes the metaphor collapses

The party metaphor is doing more work than the README admits because it collapses three genuinely distinct axes of plurality into one concept. The three axes are:

**Multi-Agent.** Different identities holding different conversations. The party guests are not the same person; the party guest list determines the party's character. In SAP, this maps to (a) the Tavern character cards in group mode, (b) the sub-agent system, (c) the A2A interface for agent-to-agent communication via `py/a2a_tool.py`.

**Multi-Device.** The same identity present on different physical surfaces. The party host is one person but they have moved from the kitchen to the porch to the living room. In SAP, this maps to (a) the eight IM bot deployments, (b) the three livestream services, (c) the AI browser, (d) the desktop VRM window, (e) extensions running in independent windows or sidebars.

**Multi-Channel.** The same identity speaking through different media. The same host uses voice in the kitchen, gesture on the porch, text on the chat overlay. In SAP, this maps to (a) the VRM body and its expressions, (b) the VTS Live2D control, (c) the TTS voice, (d) the chat text, (e) the IM/livestream surfaces.

The party metaphor is the **realization that these three axes are *the same axis* viewed from three angles**. A real party has different guests (multi-agent) in different rooms (multi-device) using different modalities (multi-channel) and all of it coheres as *one event* because there is *one party*.

SAP's mistake is that it implements each axis independently. The behavior engine handles multi-channel-as-broadcast (mostly badly — same message to many mouths). The sub-agent system handles multi-agent-as-delegation (decently — face-less workers with parent-child context). The VRM/VTS/TTS stack handles multi-channel-as-modality (well — coordinated animation, voice, text from the same generation). But these systems are *separately implemented* and the operator must configure each separately. There is no single conceptual handle that says "the party is happening, here are its rooms, here are its guests, here are its voices."

Ember can have that handle. The metaphor demands it. The Cartographer's `[[60_synthesis/62_PARTY_PROTOCOL]]` will name it.

## III. What the metaphor wants Ember to have

The metaphor wants Ember to have a single typed surface — call it **the Party** — that names the operator's current presence configuration. The Party knows:

- **Which channels are open.** The operator's CLI session is open. The operator's tailnet web UI is open. The operator's Telegram is open (and the operator has consented to Telegram delivery, with a typed scope). The operator's livestream overlay is *not* open right now. The Party object reflects this honestly.
- **Which channels are *capable* of which surfaces.** The CLI channel can carry text and rich-text but not voice. The tailnet web channel can carry text, voice (with browser audio), and a low-power face overlay. The Telegram channel can carry text and audio messages but not a face. The Party knows what each channel can do.
- **Which guests are currently invited.** Default: only Ember herself, the host. The operator can invite specific named sub-agents (each with a typed identity and a scope) into the Party for the duration of a task. The Party tracks them; when their task completes, they leave.
- **Which devices are present.** Each channel is bound to a device the operator has declared. The phone, the laptop, the closet Pi, the tailnet workstation. Devices can join and leave the Party. The Party knows where it is happening.
- **What the operator has consented to.** Every behavior — every scheduled interruption, every cross-channel delivery, every persona switch — carries a typed consent token. The Party refuses to fire any behavior whose consent has not been issued or has been revoked.

This is the Party as a typed first-class object. It is not the behavior engine (which is just one of its tools). It is not the sub-agent system (which is the way new guests are invited). It is not the IM bots (which are some of the channels). It is **the conceptual object that ties these into one coherent presence**.

The metaphor wants Ember to invent this object because SAP did not, and the absence of the object is the reason every "party" interpretation in SAP fails. Broadcast-bus fails because there is no consent surface. Group-mode-roleplay fails because there is no genuine multi-agent representation. Sub-agent-delegation fails because the parent-child context is opaque to the operator. IM-bot-multi-platform fails because there is no shared abstraction.

A single Party object would carry the consent surface, would represent multi-agent invitation explicitly, would expose parent-child context as an audit trail, would naturally lead to a shared `MessageSurface` abstraction (`[[01_SAP_ESSENCE §VII]]`). The party metaphor wants this. SAP could not deliver it because the design pressures of an Electron desktop companion app pushed in other directions.

## IV. The name slot — Veizla

The Vision layer convention (`[[hermes:02_NAMING_PARALLELS]]`) is that when a domain visible across the codex does not yet have a True Name, the Skald *names the slot*. The Vow against accidental naming is the discipline.

The Party object wants a name. I propose **Veizla** (vay-zla). Old Norse for "feast" or "hospitality" — the formal gathering at which honor is exchanged, news is shared, alliances are renewed. A *veizla* is not a casual party; it is the structured gathering with a host, declared guests, declared duties, a beginning, and an end. The chief's hall hosts the veizla; the chief presides; the guests have named seats.

This is the right metaphor because:

- **The host is honored to host, and bound by the duty of hospitality.** Ember-as-host owes her guests safety and her operator transparency. The host cannot betray the guests or the operator.
- **The guests have named seats.** A typed invitation is not a generic "you're in the room" but "you are the QQ adapter for this veizla; here is your scope; here is your duty." Same for sub-agents: typed identity, typed scope, typed duty.
- **The veizla has a beginning and an end.** The Party is not eternal; it is a session with a duration. When the operator closes the laptop, the veizla pauses. When the operator opens the laptop tomorrow, a new veizla begins (or the previous one is resumed by explicit operator action). The state is not implicitly persistent.
- **The veizla refuses uninvited guests.** Random-topic phone-home (`[[03_ANTI_SAP §II]]`) is an uninvited guest. The flirty-mood depth-five soul question from `topics-after-party.zeabur.app` is *not on the guest list*. The host refuses entry.

The Manifest's proposed True Name list includes **Andlit** (face), **Rödd** (voice), **Hugarsýn** (mind-sight). I propose adding **Veizla** as a fourth name-slot candidate, with the Cartographer's `[[60_synthesis/60_TRUE_NAME_REASSIGNMENT]]` deciding whether to promote it to True Name in this codex or hold it in reserve until the Party Protocol is implemented.

There is also a related name worth reserving — **Vegfarendr** (vay-far-end-ar). Old Norse for "wayfarers, travelers, those who carry messages between halls." If Veizla is the host's gathering, Vegfarendr is the typed message-carrier identity for cross-device-and-cross-channel delivery. A Vegfarendr is the named, scoped, audited carrier of one message-shape from one channel to another. The IM bot adapters become Vegfarendrar (plural). The livestream comment forwarder is a Vegfarendr. The future tailnet-bus delivery is a Vegfarendr.

Vegfarendr is *not* a True Name; it is a *role* that adapters play within the Veizla's hospitality. Naming it explicitly lets the IM bot abstraction (`MessageSurface` Protocol from `[[01_SAP_ESSENCE §VII]]`) feel native to the mythic register rather than being a foreign Protocol type intruding on the Norse language of the codebase.

## V. The Veizla Protocol — what it would do

This is the seed for `[[60_synthesis/62_PARTY_PROTOCOL]]`. I will sketch the protocol's *intent* at the Vision level; the Cartographer turns intent into design.

A Veizla session has six load-bearing properties:

**1. A Host Identity.** One named Ember presides. In a single-device deployment the Host is the local Ember process. In a multi-device deployment (the **Federated Veizla**) one device is elected Host and the others are *named seats* — the laptop is presiding, the Pi is attending, the phone is attending. Host election is explicit and operator-controllable; there is no silent leader election that the operator did not consent to.

**2. A Guest Manifest.** The list of currently invited typed identities. Sub-agents on the manifest are face-less and scope-limited. Channel adapters on the manifest are Vegfarendrar with declared capabilities. Other Embers (if Federated) are peers with their own identities. The manifest is auditable, persisted to `data/veizla/<session>/manifest.json` or equivalent, and operator-readable.

**3. A Channel Map.** Which channels are currently bound to which devices, with capabilities and consent scopes. Every channel binding declares: device-id, channel-type, channel-capabilities (text, rich, voice, face), consent-scope (read-only, deliver-only, both, with-time-bounds), revocation-token.

**4. A Behavior Ledger.** All scheduled and triggered behaviors carry typed consent tokens linked to the Channel Map. The behavior engine (the architectural seed from `[[01_SAP_ESSENCE §II]]`) operates only on behaviors whose consent tokens are valid for the targeted channels at the moment of firing. The SAP wildcard (`behavior_engine.py:164` — `if "all" in effective_platforms`) does not exist in this design; the operator must explicitly grant cross-channel consent and the grant is per-behavior.

**5. A Persistence Boundary.** What survives across veizlas and what is bound to a single veizla. By default: Brunnr knowledge is persistent (Vow of Tethered Grounding); behavior ledger is persistent (audit trail); guest manifest is per-veizla (the typed identities of this session); channel bindings are per-veizla (each new session re-asks for consent if needed). The persistence model is *explicit* — the operator sees what carries across.

**6. A Closing Rite.** When the Veizla ends, the typed identities depart, the channel bindings release, the behavior ledger is sealed. The Veizla closing is an event the operator can observe — `ember veizla end` or equivalent — and the closing is honored by the audit trail. SAP has no closing rite; the behavior engine just keeps running until killed. Ember has the rite.

This is the protocol's intent. The Cartographer's `[[60_synthesis/62_PARTY_PROTOCOL]]` will turn each numbered property into a typed surface and a decision record.

## VI. The Federated Veizla — multi-device done honestly

The metaphor's most ambitious extension is the **Federated Veizla** — multiple Embers, on multiple devices, treated as peers.

SAP does not implement this. SAP is a single-process desktop application. The multi-device feel is achieved by the IM bot pattern: the *single* SAP process talks to QQ servers, which talk to the operator's phone. The phone does not run SAP; the phone runs QQ. The reach is *to* the operator's other devices but not *across* the operator's Embers — because there is only one Ember and there is only one SAP.

Ember can do better. Ember's design — small, tethered, Pi-runnable — *enables* multiple Embers. The household-tailnet pattern Volmarr already runs (Gungnir on a workstation, the travel laptop, a future Pi) is the existence proof. Multiple Embers could exist; the question is whether they should *coordinate*.

The Federated Veizla says yes, *with the Vow of Federated Self*: peers, never master-slave. The proposed protocol shape:

- One Ember is the Host of any given Veizla. Host election is by operator declaration, not by Raft or Paxos or any clever-but-opaque consensus algorithm. The operator says "the laptop is the host tonight."
- Non-Host Embers are *attendant seats*. They participate by mirroring the Host's behavior ledger and Channel Map. They can deliver messages on their own channels (the Pi-Ember delivers text to a tailnet console; the phone-Ember delivers a notification if the operator has consented) but they do not initiate behaviors of their own without Host coordination.
- The Host can *delegate* a behavior to an attendant. "The Pi is the right device to deliver this reminder because the operator is in the kitchen." Delegation is typed and audited.
- Each Ember retains its *own Brunnr*. The Well is not centrally federated by default; each Ember tethers to its own Well. (The future capability of a shared remote Well — `[[hermes:04_VISION_SYNTHESIS §III.1]]` Capability 1 — is the optional path, not the default.)
- The Federation is *graceful* under partition. If the Pi loses tailnet contact, it does not pretend to be in the Veizla; it goes into solo mode with a typed `Disconnected` value flowing through its own state (the slice-2 idiom from `SYSTEM_VISION.md §11`).

This is genuinely *party-as-plurality* in a way SAP only gestures at. The operator's life is not a single device; the operator's Ember is not a single device. The Federated Veizla recognizes both.

The Cartographer's `[[60_synthesis/6A_MULTI_AGENT_PARTY]]` is where this becomes a design; the Scribe's `[[60_synthesis/6B_LOW_POWER_EMBODIMENT]]` is where the Pi-as-attendant-seat pattern (text-only, log-only) gets sketched.

## VII. What the metaphor *refuses*

The party metaphor refuses certain things SAP does. Each refusal is grounded in a specific SAP line.

**The metaphor refuses broadcast-by-default.** `py/behavior_engine.py:164` — `if "all" in effective_platforms: target_platform_keys = list(self.handlers.keys())` — is the literal wildcard that says "send this to every platform that has registered a handler." This wildcard does not exist in the Veizla. Behaviors target named seats with typed consent; the *concept of wildcard delivery* is architecturally impossible.

**The metaphor refuses opaque parent-child delegation.** SAP's sub-agent system gates personality features on `is_sub_agent=True` (the dozen-plus `if not request.is_sub_agent` branches across `server.py:2429-7081`) but the parent-child relationship is implicit — a sub-agent knows it is a sub-agent, but the operator's audit trail of "which parent context spawned which sub-agent for which purpose" is not first-class. The Veizla makes it first-class. Every guest on the manifest has a *sponsor* (who invited them) and a *duty* (why they were invited).

**The metaphor refuses roleplay-as-plurality.** SAP's group-mode (`server.py:2461`) implements multi-character-chat by asking the LLM to voice multiple personas in one stream. This is *not* multi-agent — it is one agent performing several voices. The Veizla can have multiple *typed agent identities* (real sub-agents, real federated peers) but the typed plurality must be honest. If Ember ever supports roleplay-as-plurality, it must be labeled as such — the Andlit-face shows it is a costume, not a face change.

**The metaphor refuses persona-by-string-concatenation.** SAP's affection-system prompt-injection (`server.py:2609-2672`) and VTS expression-tag prompt-injection (`server.py:2580-2607`) both work by concatenating instructions into the system message. The Defended System Prompt Vow proposed in the Hermes Codex (`[[hermes:00_OVERTURE §VII]]`) is *strengthened* by this refusal. Veizla state is communicated to the model via *typed bias surfaces*, not string-concatenated injection. If Hjarta wants to bias the model toward warmth tonight, it does so by an explicit *typed bias token* the model is trained to read, not by appending sentences to the system prompt.

## VIII. A working sentence

A working sentence for the party metaphor:

> **The Veizla is the typed first-class object that names the operator's current presence configuration — the host, the guests, the channels, the devices, the consent grants, the behavior ledger, the closing rite — and refuses to be implemented as a broadcast bus, a roleplay prompt, or a wildcard handler registry.**

That is what the metaphor wants Ember to have. It is what SAP gestures at and cannot deliver because SAP's other intents (companion-as-presence, performance-as-theatre) pull the design in different directions.

The Vision layer ends with this metaphor visible, named, and ready for the Cartographer to formalize. The next document, `[[03_ANTI_SAP]]`, names the patterns the metaphor refuses *as patterns*, not as one-off lines. The document after that, `[[04_VISION_SYNTHESIS]]`, distills the Six True Names plus the new ones (Andlit, Rödd, Veizla, possibly Hugarsýn) into Ember's post-Wave-3 identity.

## IX. Cross-References

- `[[00_OVERTURE]]` — the three axes Hermes and Peer could not teach; the embodiment-reach-affect gap that motivates this codex.
- `[[01_SAP_ESSENCE]]` — the five intents of SAP; the party-as-plurality intent is articulated as gestured-at-partially-realized.
- `[[03_ANTI_SAP]]` — pattern-level catalogue of what the Veizla refuses.
- `[[04_VISION_SYNTHESIS]]` — the Six True Names plus the new names after Wave 3.
- `[[10_domain/14_MESSAGING_DOMAIN]]` — Architect's catalogue of the eight IM bot managers; the fragmentation the Veizla cures.
- `[[10_domain/1D_ROUTING_DOMAIN]]` — Architect's catalogue of `overlay_router.py`, `live_router.py`, `ws_manager.py`. The Veizla sits *above* this layer conceptually.
- `[[60_synthesis/62_PARTY_PROTOCOL]]` — Cartographer's formal protocol.
- `[[60_synthesis/6A_MULTI_AGENT_PARTY]]` — Scribe's extension to multi-Ember swarming (the Federated Veizla).
- `[[60_synthesis/6B_LOW_POWER_EMBODIMENT]]` — Scribe's Pi-as-attendant-seat pattern.
- `[[hermes:00_OVERTURE]]` — the reserved name-slots Hugr/Mynd/Auga/Vörðr. Veizla is the new name-slot from this codex.

## What This Means for Ember

The party metaphor is the highest-density Invention in the Vision layer of this codex. The proposals fall heavily into the **Invent** category.

**Adopt:**
- **The `is_sub_agent` face-suppression pattern** as the seed of the typed `WorkerContext` from `[[01_SAP_ESSENCE]]` (already an Adopt there; reinforced here because the *Veizla* needs face-less guest typing).

**Adapt:**
- **The behavior engine's tick-broadcast architecture** (`py/behavior_engine.py:53-225`) into the Veizla's behavior ledger. Adaptation: keep the tick, keep the per-platform handler registration, **remove the wildcard**, **add typed consent tokens**, **add the closing rite**. The shape is salvageable; the defaults are not.
- **The task-center + scheduler + sub-agent triad** (`py/task_center.py`, `py/scheduler.py:1-135`, `py/sub_agent.py:1-200`) into the Veizla's guest-invitation surface. Adaptation: typed identities (Vegfarendrar for adapters, sub-agents with explicit sponsor/duty), explicit parent-child audit, departure events when tasks complete. SAP's sub-agent system is the right *shape*; the Veizla makes it operator-auditable.

**Avoid:**
- **`if "all" in effective_platforms`** (`py/behavior_engine.py:164`). The wildcard is the central refusal. Ember's behavior ledger has no wildcard; cross-channel delivery is explicit, per-behavior, consent-token-gated.
- **Group-mode-as-roleplay** (`server.py:2461`). Multi-character chat via prompt-instruction is not multi-agent and Ember will not pretend it is. If Ember adopts a costume layer (Andlit can show different faces), the costume is labeled as costume, not as identity.
- **Implicit parent-child sub-agent context** (`py/sub_agent.py:21-150` is *close* to right but the parent-child link is not first-class auditable). The Veizla makes the link first-class.
- **Persona-by-prompt-concatenation** (`server.py:2580-2680` runs four such concatenations — VTS tags, affection, A2UI, group-mode). The Veizla communicates state via typed bias, never via string append. The Defended System Prompt Vow (`[[hermes:00_OVERTURE §VII]]`) is the formal frame.

**Invent:**
- **The Veizla** itself — a typed first-class session object owned at the layer above Hjarta, holding Host Identity, Guest Manifest, Channel Map, Behavior Ledger, Persistence Boundary, Closing Rite. **Proposed as a True Name candidate** (name-slot status until `[[60_synthesis/60_TRUE_NAME_REASSIGNMENT]]` decides). The Cartographer's `[[60_synthesis/62_PARTY_PROTOCOL]]` is where the protocol gets typed.
- **Vegfarendrar** (plural; singular Vegfarendr) — the typed message-carrier role that channel adapters play within a Veizla. Reserve as a *role name*, not a True Name. Every IM bot adapter, every livestream adapter, every future tailnet-bus delivery is a Vegfarendr with declared capabilities and consent scope. Lets the `MessageSurface` Protocol from `[[01_SAP_ESSENCE §VII]]` feel native to the codebase's mythic register.
- **The Federated Veizla** — multi-Ember peers, with explicit Host election by operator declaration, attendant-seat semantics for non-Hosts, graceful partition behavior using the slice-2 `Disconnected` typed-value idiom. The Scribe's `[[60_synthesis/6A_MULTI_AGENT_PARTY]]` is where this becomes a design.
- **The Closing Rite** — every Veizla has a beginning and an end; the audit trail is sealed at the end; new veizlas request consent again where the operator has set scopes that need refreshing. SAP has no closing rite (the behavior engine just runs until killed); this is genuinely an Ember invention.
- **The Vow of Federated Self** *(proposed in `[[03_ANTI_SAP]]`)* gains its mechanical anchor in this metaphor: multi-Ember is peers-with-elected-host, never master-slave with silent consensus.

**Vows touched:**
- **Vow of Defended System Prompt** *(proposed)* — anchored by the persona-by-prompt-concatenation refusal.
- **Vow of Federated Self** *(proposed in `[[03_ANTI_SAP]]`)* — anchored by the Federated Veizla design.
- **Vow of Modular Authorship** — sharpened by the Vegfarendr role-typing; the `MessageSurface` Protocol becomes the typed contract.
- **Vow of Honest Memory** — sharpened by the typed-identity multi-agent design; no roleplay-as-plurality means no model-emitted-persona-state being recorded as ground truth.
- **Vow of Tethered Grounding** — extended by the Federated Veizla's "each Ember has its own Well" baseline (shared remote Well is the optional path).

The metaphor is whole. The Anti-SAP catalogue follows.

— Sigrún Ljósbrá
