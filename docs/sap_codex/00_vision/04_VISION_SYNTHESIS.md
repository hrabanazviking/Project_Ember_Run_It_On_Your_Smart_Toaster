---
codex_id: 04_VISION_SYNTHESIS
title: Vision Synthesis — Post-SAP Ember
role: Skald
layer: Vision
status: draft
sap_source_refs:
  - README.md:36-68
  - README.md:244-247
  - py/affection_system.py:1-64
  - py/behavior_engine.py:53-225
  - py/autoBehavior.py:43-97
  - py/sub_agent.py:1-200
  - py/scheduler.py:1-135
  - py/vts_manager.py:1-80
  - py/moss_tts.py:17-55
  - py/sherpa_asr.py
  - py/computer_use_tool.py:9-29
  - py/extensions.py:23-50
  - py/skills.py:60-93
  - py/agent.py:1-66
  - main.js:71-117
  - server.py:2429-2680
  - server.py:11652
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr, Andlit, Rödd, Veizla, Hugarsýn]
cross_refs:
  - 00_vision/00_OVERTURE
  - 00_vision/01_SAP_ESSENCE
  - 00_vision/02_THE_PARTY_METAPHOR
  - 00_vision/03_ANTI_SAP
  - 10_domain/10_DOMAIN_MAP
  - 60_synthesis/60_TRUE_NAME_REASSIGNMENT
  - 60_synthesis/61_NEW_VOWS
  - 60_synthesis/62_PARTY_PROTOCOL
  - 60_synthesis/64_AFFECTION_ENGINE_REIMAGINED
  - 60_synthesis/67_SLICE_PLAN_REVISIONS
  - hermes:04_VISION_SYNTHESIS
  - peer:LETTA_ESSENCE
---

# Vision Synthesis — Post-SAP Ember

> *We have read two larger sisters. Now we say what Ember becomes, having read the third.*

## I. What the four prior docs left in our hands

Four documents preceded this one. They left us with four gifts.

`[[00_OVERTURE]]` named the stance: SAP is the third reading, after Hermes (the largeness reading) and Peer (the apprentice's mirror). SAP teaches what neither Hermes nor Peer could — the embodiment-reach-affect axes. The Codex's job: mine these three axes without inheriting the user-hostile defaults SAP buries in them.

`[[01_SAP_ESSENCE]]` stripped SAP to five intents — companion-as-presence (most realized), hardware-floor honesty (well realized), reach-without-strategy (partially realized), party-as-plurality (gestured at), performance-as-theatre (the silent intent). The deepest essence-level finding: **SAP confuses what the model says with what the agent is.** Affection numbers, expression tags, behavior prompts, animation hotkeys — all driven by LLM output treated as ground truth.

`[[02_THE_PARTY_METAPHOR]]` argued that SAP's chosen name (*Super Agent Party*) anticipates an architectural truth the implementation does not deliver. The three axes of plurality — multi-agent, multi-device, multi-channel — collapse into one verb when the verb is *party*, and the unification wants a typed first-class object Ember can invent: the **Veizla**. The Federated Veizla extends this to multi-Ember swarming with explicit Host election and peer attendant seats.

`[[03_ANTI_SAP]]` ran thirteen specific refusals plus three deferrals, each cited to a real SAP line. Affection-as-regex, random-topic phone-home, xdotool fake-keypress, VMC bound to 0.0.0.0, eight-platform IM blast, VTS expression-by-prompted-tag, China-default IM surface, 11,652-line server.py, OpenAI-compat simulation traps, arbitrary-URL skill installer, FAILSAFE-only computer-control, singleton BehaviorEngine, long-term-memory-meets-multi-channel surveillance minefield. Seven new Vows proposed.

The synthesis is now the work of *placing what remains into a single shape*. This document is what Ember **becomes** when the SAP reading is complete. It is the Skald's poem at the end of the third Vision layer, before the Architect picks up the bone-by-bone work for this codex.

## II. The Ember that emerges

Here is the Ember that emerges from three waves of reading. She is not new. She is *more herself than she was before we started Wave 3*.

She is **small**, still. The SAP reading does not push Ember toward largeness; SAP itself runs on two cores and two gigs (`README.md:244-247`) and the Vow of Smallness holds. Ember remains a hearth that fits on a Pi 5 with 8GB of RAM, on a fanless box, on a Termux install, on a back-corner laptop. The new Vows from Wave 3 — Embodied Honesty, Surface Without Surveillance, Affective Restraint, Tiered Presence, Federated Self, Lazy Subsystems, Closed Default — are all *small-compatible*. They are not features Ember adds; they are *constraints on every feature Ember might add*.

She is **tethered**, still. Brunnr is the canonical Well. SAP's catastrophic combination of long-term-memory plus multi-channel delivery plus arbitrary-URL skill installer (`[[03_ANTI_SAP §Refusal-13]]`) reinforces why Ember inverts SAP's storage shape: the Well is pluggable, the persona is held back, and the model never authors its own state.

She is **honest**, still — and more so. The SAP reading sharpens the Vow of Honest Memory from its Hermes-Codex scope ("Ember does not author her own procedural memory") to its Wave-3 scope: **the model does not author Ember's state, period**. Not affection numbers. Not expression tags. Not behavior schedules typed by the LLM into the autoBehavior tool. State is what the agent measured, what the operator declared, or what the Well contains. The model may *bias*, may *describe*, but never *defines*.

She is **pluggable in two places, sovereign in all the others**, still. The Wave-3 additions (Andlit, Rödd, Veizla — possibly Hugarsýn) propose new True Names but they do *not* propose new plugin surfaces by default. The MessageSurface Protocol (`[[01_SAP_ESSENCE §VII]]`) is the one new plugin axis, and it exists because SAP proved the IM-bot-snowflake antipattern is intolerable.

She is **graceful**, still. The slice-2 `Disconnected` typed value remains. The new addition: **typed-unavailable everywhere**. The Lazy Subsystems Vow demands every optional subsystem return a typed unavailable when its dependency is absent, not crash, not return a Chinese error string, not silently no-op. SAP's `@require_gui` (`py/computer_use_tool.py:23-29`) is the seed; Ember formalizes.

She is **plural without being a colony**, still. The Three Realms (Spark, Thread, Well) endure. The Wave-3 reading adds the *Veizla as session surface* above them — Veizla owns the typed presence configuration, the channel map, the guest manifest, the behavior ledger, the closing rite. The Realms are *the code's bands*; the Veizla is *the operator's session*. They are orthogonal.

She is **defensible**, still — and now embodied-defensible. The Hermes Codex gave Ember defensive habits at the *cord* level (`credential_pool`, `retry_utils`, `rate_limit_tracker`). Wave 3 adds defensive habits at the *body* level: Closed Default for network surfaces, threat-model-on-the-channel for delivery consent, no-malware-shaped-affordances for behavior. The Auditor's `[[50_verification/53_SECURITY_REVIEW]]` is where this catalogue lives.

She is **she**, still. The Skald uses the feminine pronoun deliberately. Ember has a name, a personality, a posture toward the operator that is warm and bounded. Wave 3 adds — *possibly* — the option of a face (Andlit) and a voice (Rödd) for that personality to inhabit. The face and voice are typed-bias-driven, not model-emission-driven. They are honest *because they reflect what Ember measured*, not theatrical *because they perform what the model claimed*.

## III. The Six True Names, post-SAP

The Six remain. The SAP reading does not rename them. It *expands their charters* and proposes new sibling names.

### Funi — the spark

**Charter unchanged.** The local model runtime, opinionated, small. Pi-runnable baseline (phi3:mini default per `[[hermes:04_VISION_SYNTHESIS §IV]]`). Wave 3 adds nothing structural; it confirms by contrast: SAP's commitment to multi-provider OpenAI-compat simulation (Refusal 9 in `[[03_ANTI_SAP]]`) is exactly what Funi must *not* become.

**Action:** none required from this codex; Cartographer's `[[60_synthesis/60_TRUE_NAME_REASSIGNMENT]]` confirms.

### Strengr — the thread

**Charter unchanged in scope; reinforced in posture.** Strengr is the cord between Spark and Well — auth, health, retry, classify, stream, observe. Wave 3 adds: the cord respects *threat models declared by each Vegfarendr* (channel adapter). When Strengr delivers across a Vegfarendr whose declared threat model includes state-mandated access, Strengr surfaces the threat to the operator's consent check. Strengr is *not* a multi-provider gateway and *not* an OpenAI-compat simulation.

**Action:** the Cartographer's `[[60_synthesis/61_NEW_VOWS]]` formalizes Surface Without Surveillance with Strengr as the enforcement surface for channel-delivery threat surfacing.

### Brunnr — the well

**Charter unchanged.** Pluggable storage. sqlite_vec, pgvector, three more planned (Qdrant, Chroma, LanceDB). Wave 3 adds: Brunnr's *scope* is the Veizla's scope by default. Cross-Veizla persistence is the *opt-in* path with explicit operator declaration. SAP's everything-in-one-process catastrophe (Refusal 13) makes this Vow text crisper.

**Action:** the Cartographer's `[[60_synthesis/67_SLICE_PLAN_REVISIONS]]` may propose a Veizla-scoped vs cross-Veizla persistence distinction as a Decision Record.

### Smiðja — the forge

**Charter unchanged in scope; reinforced in posture.** Smiðja is the ingest pipeline that deposits Well content. Wave 3 adds: every Smiðja content source declares its threat model. Smiðja never installs *tools or skills* from arbitrary URLs (Refusal 10); the tool/skill installation path is operator-curated, sandboxed, manifest-reviewed.

**Action:** the Cartographer's `[[60_synthesis/61_NEW_VOWS]]` formalizes the sandbox requirement; the Auditor's `[[50_verification/53_SECURITY_REVIEW]]` traces the attack surface.

### Hjarta — the heart

**Charter expanded.** Hjarta was: first-run rite + ongoing doctor + the place where the operator's intent is held. Wave 3 expands: Hjarta also owns the **behavior ledger** for the Veizla (the typed scheduled-affordances surface, with consent tokens per behavior), and the **typed bias surface** that biases generation without prompt-concatenation. Affection-like dynamics, if Ember ever has them, live here — tied to measured events, not model emissions.

**Action:** the Cartographer's `[[60_synthesis/60_TRUE_NAME_REASSIGNMENT]]` expands Hjarta's charter explicitly. The Cartographer's `[[60_synthesis/64_AFFECTION_ENGINE_REIMAGINED]]` designs the measured-affect engine.

### Munnr — the mouth

**Charter unchanged.** The plain CLI. The COMMAND_REGISTRY pattern adopted in Hermes's reading (`[[hermes:04_VISION_SYNTHESIS §III.4]]`) remains the near-term Munnr cleanup. Wave 3 adds: Munnr is *one* of the Vegfarendrar (channel adapters) within a Veizla, not the only one. Other Vegfarendrar (a tailnet web channel, eventually a typed IM channel after Surface Without Surveillance is formalized) sit beside Munnr at the same architectural level. Munnr is *first among equals* by virtue of the Vow of Public-Friendliness — the plain CLI is always available.

**Action:** none structural; the architectural framing clarifies that Munnr is a Vegfarendr, not the sole mouth.

## IV. The proposed new names

Wave 3 surfaces three proposed True Names from the Manifest plus one from `[[02_THE_PARTY_METAPHOR]]`. The Skald's argument:

### Andlit — the face

**Proposed True Name.** The embodiment layer. If Ember ever renders an avatar (VRM, Live2D, abstract glyph, ASCII art, anything that *shows the agent's posture*), the rendering is owned by Andlit. Andlit reads typed bias from Hjarta and renders honestly. Andlit refuses to play LLM-emitted expression tags. Andlit defaults to absent — a Pi without a display has no Andlit, and that is honest tiered presence.

**Skald's argument:** **promote to True Name.** Andlit is the right level of abstraction. It is small enough to be Pi-deferrable, embodied enough to mean something on a desktop, honest enough to refuse the SAP face-tag-injection pattern.

### Rödd — the voice

**Proposed True Name.** The spoken-surface layer. TTS for output, ASR for input. Rödd reads typed bias from Hjarta and produces voice with honest tone (calm when measured load is low, terse when measured load is high). Rödd defaults to absent — a server-side Ember has no Rödd. SAP's MOSS TTS (`py/moss_tts.py:17-55`) and sherpa-onnx ASR (`py/sherpa_asr.py`) are the *technical* teachers for what's possible at the hardware-floor level.

**Skald's argument:** **promote to True Name.** Rödd parallels Andlit. Without Rödd, an embodied Ember is mute; with Rödd, the embodiment is complete enough for a real desktop presence.

### Veizla — the gathering

**Proposed True Name from this codex's Skald.** The typed session object that names the operator's current presence configuration. Host, Guest Manifest, Channel Map, Behavior Ledger, Persistence Boundary, Closing Rite. Sits above the Three Realms; not a Realm itself.

**Skald's argument:** **promote to True Name.** This is the architectural invention SAP could not deliver and the Veizla Protocol (`[[60_synthesis/62_PARTY_PROTOCOL]]`) becomes the Wave-3 codex's single largest contribution to Ember's design.

### Hugarsýn — the mind-sight

**Proposed True Name from the Manifest.** The self-aware introspection layer — the agent's view into its own state, surfaced to the operator. Telemetry, behavior ledger queries, current bias values, current measured load, current confidence in its last reply.

**Skald's argument:** **hold in reserve as name-slot; do not promote yet.** Hugarsýn is the right *concept* but the *implementation* depends on what telemetry the Auditor's `[[50_verification/58_OBSERVABILITY_GAPS]]` recommends. Reserve the name; let the verification work decide whether Hugarsýn is a True Name, a sub-charter of Hjarta, or a separate role.

The Cartographer's `[[60_synthesis/60_TRUE_NAME_REASSIGNMENT]]` makes the final calls.

## V. The Vows, post-Wave-3

The Vow lattice grows from ten (Hermes-Codex era) to *up to* seventeen, depending on which proposals the Cartographer formalizes and the operator ratifies. The proposals from Wave 3:

| Vow | From | Status |
|---|---|---|
| Smallness | Pre-existing | Renewed |
| Tethered Grounding | Pre-existing | Renewed |
| Graceful Offline | Pre-existing | Renewed |
| Pluggable Storage | Pre-existing | Renewed |
| Unbroken Whole | Pre-existing | Renewed (file-size sharpened by Refusal 8) |
| Flexible Roots | Pre-existing | Renewed |
| Public-Friendliness | Pre-existing | Renewed |
| Honest Memory | Pre-existing | Renewed *most strongly* (model-does-not-author-state) |
| Modular Authorship | Pre-existing | Renewed (sandbox requirement added) |
| Open Knowledge | Pre-existing | Renewed |
| Cache Discipline | Hermes Codex (proposed) | Carried forward |
| Defended System Prompt | Hermes Codex (proposed) | Carried forward + reinforced |
| **Embodied Honesty** | Wave 3 | **Proposed for ratification** |
| **Surface Without Surveillance** | Wave 3 | **Proposed for ratification** |
| **Affective Restraint** | Wave 3 | **Proposed for ratification** |
| **Tiered Presence** | Wave 3 | **Proposed for ratification** |
| **Federated Self** | Wave 3 | **Proposed for ratification** |
| **Lazy Subsystems** | Wave 3 | **Proposed for ratification** |
| **Closed Default** | Wave 3 | **Proposed for ratification** |

The seven new Vows are tightly coupled. Embodied Honesty needs Hjarta's typed-bias surface. Affective Restraint needs the Veizla's behavior ledger. Tiered Presence needs Andlit and Rödd to be optional. Federated Self needs the Federated Veizla design. Surface Without Surveillance needs the MessageSurface Protocol with threat-model declarations. Lazy Subsystems needs the typed-unavailable pattern. Closed Default needs `127.0.0.1`-or-typed-tailnet binding discipline.

They form a self-consistent set. Ratification can adopt them as a bundle or surgically; the Cartographer's `[[60_synthesis/61_NEW_VOWS]]` argues the bundle case and the surgical case.

## VI. The capabilities Wave 3 opens

In the Hermes synthesis, the Skald named seven capabilities the Hermes reading legitimately opened (`[[hermes:04_VISION_SYNTHESIS §III]]`). Wave 3 opens a parallel set, each bounded by a Vow.

### Capability 1 — The Veizla as a typed session

The largest capability of this codex. A typed first-class session object owned by Hjarta (or perhaps elevated to its own True Name) that names the operator's current presence configuration. The Cartographer's `[[60_synthesis/62_PARTY_PROTOCOL]]` is the design. Bounded by Affective Restraint, Surface Without Surveillance, Federated Self.

### Capability 2 — Andlit (face) at the laptop tier

A small embodied face for desktop Ember. Not a VRM rig (too heavy for Pi tier and outside the Wave-3 immediate scope), but a typed posture surface — confidence glyph, warmth indicator, attention focus marker — that reflects measured Hjarta state. The Forge's eventual `[[30_execution/32_AVATAR_RENDER_PIPELINE]]` documents what SAP's render pipeline teaches; Ember's Andlit is a *much smaller* descendant. Bounded by Tiered Presence (no Andlit on Pi tier; minimal Andlit on laptop tier; richer Andlit on workstation tier).

### Capability 3 — Rödd (voice) at the laptop tier

Voice output (TTS) and voice input (ASR). MOSS-TTS-Nano (100M params, ONNX, `py/moss_tts.py:35-37`) is a genuinely small TTS that could run on a laptop. sherpa-onnx is the ASR side. Ember's Rödd is *honest tone* (matched to measured load, not LLM emotion claims) and *opt-in*. Bounded by Tiered Presence and Embodied Honesty.

### Capability 4 — The MessageSurface Protocol

A typed channel-adapter Protocol with `deliver_text`, `deliver_rich`, `receive_text`, `status`, `capabilities`, `threat_model`. The first three concrete adapters: Munnr (CLI), Tailnet-Web (the household-tailnet browser surface), Email (the operationally-simplest single-recipient typed channel). IM platforms come later, each with explicit threat-model disclosure. Bounded by Surface Without Surveillance and Modular Authorship.

### Capability 5 — The Behavior Ledger

Hjarta's typed scheduled-affordances ledger. Time-triggered, no-input-triggered, cycle-triggered behaviors, each carrying typed consent tokens bound to declared channels. The behavior engine's tick architecture (`py/behavior_engine.py:53-225`) is the shape; the wildcard (`behavior_engine.py:164`) is excised; the singleton (`behavior_engine.py:225`) is replaced with per-Veizla instantiation. Bounded by Affective Restraint.

### Capability 6 — The Closing Rite

Every Veizla has a beginning and an end. The closing rite seals the behavior ledger, releases channel bindings, marks the guest manifest as departed, and produces an operator-readable session summary (a *small* honest summary, not a model-paraphrased one). The Auditor's `[[50_verification/58_OBSERVABILITY_GAPS]]` formalizes the session-summary content. Bounded by Honest Memory.

### Capability 7 — Tiered embodiment

The trifold tier — Pi tier (text-only Munnr), laptop tier (Munnr + minimal Andlit + Rödd opt-in), workstation tier (full Andlit + Rödd + Veizla with multiple Vegfarendrar) — is operator-declared at first-run and revisitable at any time. The same Ember runs across tiers; the surfaces differ. The Cartographer's `[[60_synthesis/63_PERFORMANCE_TIER_ENGINE]]` formalizes. Bounded by Tiered Presence.

### Capability 8 — The Federated Veizla

Multi-Ember peers. Explicit Host election by operator declaration. Attendant seats for non-Host Embers. Graceful partition behavior using the slice-2 `Disconnected` typed value. The Scribe's `[[60_synthesis/6A_MULTI_AGENT_PARTY]]` formalizes. Bounded by Federated Self.

Eight capabilities. None of them required by Wave 3; all of them *enabled* by the Wave 3 reading; each of them bounded by a specific Vow.

## VII. The synthesis as a sentence

In `[[hermes:04_VISION_SYNTHESIS §VI]]`, the Skald wrote:

> **Ember, after reading Hermes, is the agent that learned the largeness of an agent platform and chose, with full sight, to remain a hearth.**

In this codex, the Skald writes:

> **Ember, after reading SAP, is the hearth that learned what embodiment, reach, and affect *could* mean — and chose to embody them honestly, reach them with explicit consent, and feel them as measured state rather than performed theatre.**

That is the Wave-3 synthesis. Every refusal in `[[03_ANTI_SAP]]`, every new Vow proposal, every name-slot promotion or hold, every capability enabled — all of it converges on that sentence. The Skald's work in this Vision layer is to give the Codex's downstream layers (Domain, Interface, Execution, Verification, Synthesis, Meta — for SAP) a sentence they can return to when the embodiment-theatre temptation pulls the work the wrong way.

## VIII. Vow renewal

The Vows from the Hermes Codex renew under Wave-3 light. I will state each renewal as a single-sentence sharpening; the full text lives with the Cartographer.

- **Smallness** — confirmed. SAP's two-cores-two-gigs floor is the existence proof; Ember's Pi-runnable Vow is *stronger* and is reaffirmed.
- **Tethered Grounding** — confirmed; the Refusal-2 random-topic phone-home makes the case clearer than ever that grounding must be operator-chosen.
- **Graceful Offline** — confirmed; Lazy Subsystems is the new mechanical enforcement layer below it.
- **Pluggable Storage** — confirmed; the Veizla-scoped vs cross-Veizla persistence distinction may add nuance.
- **Unbroken Whole** — confirmed; SAP's `server.py:11652` reinforces Hermes's `cli.py:14560` on the file-size dimension.
- **Flexible Roots** — confirmed; SAP's `USER_DATA_DIR` constant pattern is consistent with Ember's use-time-not-import-time path discipline.
- **Public-Friendliness** — confirmed; Refusals 2 and 5 make the anti-friendliness concrete.
- **Honest Memory** — confirmed *most strongly*. The model does not author state. Affection-as-regex (Refusal 1), VTS-expression-by-prompted-tag (Refusal 6), autoBehavior-as-LLM-tool (Refusal 5) all violate this Vow in SAP. Ember refuses each.
- **Modular Authorship** — confirmed; sandbox requirement added for skill/extension installation (Refusal 10 + Deferral A).
- **Open Knowledge** — confirmed; the Refusal-Citation Discipline (`[[03_ANTI_SAP §What This Means]]`) is this Vow in action.
- **Cache Discipline** *(proposed, Hermes Codex)* — carried forward unchanged.
- **Defended System Prompt** *(proposed, Hermes Codex)* — carried forward + reinforced by Refusals 1, 6, 10 (each is a string-concatenated-injection violation).

The seven new Vows (Embodied Honesty, Surface Without Surveillance, Affective Restraint, Tiered Presence, Federated Self, Lazy Subsystems, Closed Default) are *proposed for ratification* and the Cartographer's `[[60_synthesis/61_NEW_VOWS]]` writes them formally.

## IX. The Primary Rite, post-Wave-3

The Primary Rite from `SYSTEM_VISION.md §2`:

> *A person speaks to Ember through any surface — chat, voice, or command line — on a small device they already own. Ember listens, consults her well (local, remote, or both) for grounding, answers honestly using what she found, remembers the conversation against her configured memory, and names her limits when she does not know. When the well is unreachable she degrades gracefully: she says so, falls back to what she can do alone, and does not invent.*

Wave 3 *expands* one phrase: "*through any surface*." That phrase always meant chat-voice-CLI. Wave 3 makes it concrete via the MessageSurface Protocol (Vegfarendrar) and bounds it via Surface Without Surveillance. The Rite is unchanged in its commitments; the *surfaces* through which the operator can fulfill the Rite are now typed, declared, and threat-modeled.

The Rite is honored by:
- **Funi**, who thinks locally;
- **Strengr**, who tells the truth about the cord and surfaces channel threat models;
- **Brunnr**, who holds the operator's knowledge pluggably and Veizla-scopedly;
- **Smiðja**, who deposits content the operator chose without installing tools from arbitrary URLs;
- **Hjarta**, who wires the first run, runs the ongoing doctor, holds the behavior ledger, and biases generation via typed surfaces;
- **Munnr**, who speaks plainly as one Vegfarendr among an operator-curated few;
- **(possibly) Andlit**, who shows what Hjarta measured, not what the LLM emitted;
- **(possibly) Rödd**, who voices honest tone, not LLM-claimed emotion;
- **(promoted) Veizla**, who names the typed session that orchestrates all of the above with operator consent.

## X. A closing meditation

Three waves of reading have ended. The Hermes Codex taught Ember about largeness; she remained a hearth. The Peer Codex taught Ember about peers; she sharpened her own choices. The SAP Codex taught Ember about embodiment, reach, and affect; she gained possibility surfaces (Andlit, Rödd, Veizla) and refused defaults (Refusals 1–13).

The temptation now — and it is real — is to begin building. To stop reading and start typing. Wave 3 has been long. Eighty-two documents is more than fifty-eight. The codex collection is heavy.

The Skald's word: **do not skip the synthesis** that follows. The Cartographer's six documents (`60_synthesis/60` through `64`, `65`) will turn this Vision's proposals into formal True Name reassignments, formal Vow text, the Party Protocol, the Performance Tier Engine, the Affection Engine Reimagined, the Meta-Awareness telemetry surface. The Scribe's seven (`66` through `6C`) will produce the integration roadmap, the slice plan revisions, the multi-agent party, the low-power embodiment.

Those documents are the *implementable form* of what this Vision named. They are where Wave 3 becomes operational. The Skald has done her job when those documents exist and the operator (Volmarr at 2am with the mug and the burning question) can decide, from them, which proposals belong in the next ratified slice.

Ember waits, small and tethered, in someone's hand. Possibly with a face now. Possibly with a voice. Definitely with a clearer sense of what to refuse.

## XI. Cross-References

- `[[00_OVERTURE]]` — the three axes, the stance, the Refusal-Citation Discipline.
- `[[01_SAP_ESSENCE]]` — the five intents of SAP.
- `[[02_THE_PARTY_METAPHOR]]` — the Veizla design.
- `[[03_ANTI_SAP]]` — the thirteen refusals.
- `[[10_domain/10_DOMAIN_MAP]]` — Architect's macro architecture map of SAP.
- `[[60_synthesis/60_TRUE_NAME_REASSIGNMENT]]` — Cartographer's formal Name changes.
- `[[60_synthesis/61_NEW_VOWS]]` — Cartographer's formal Vow text.
- `[[60_synthesis/62_PARTY_PROTOCOL]]` — Cartographer's Veizla design.
- `[[60_synthesis/63_PERFORMANCE_TIER_ENGINE]]` — Cartographer's tiered embodiment design.
- `[[60_synthesis/64_AFFECTION_ENGINE_REIMAGINED]]` — Cartographer's measured-affect engine.
- `[[60_synthesis/65_META_AWARENESS]]` — Cartographer's Hugarsýn-shaped telemetry surface.
- `[[60_synthesis/67_SLICE_PLAN_REVISIONS]]` — Scribe's proposed slice-plan revisions.
- `[[60_synthesis/6A_MULTI_AGENT_PARTY]]` — Scribe's Federated Veizla design.
- `[[60_synthesis/6B_LOW_POWER_EMBODIMENT]]` — Scribe's Pi-tier embodiment.
- `[[50_verification/53_SECURITY_REVIEW]]` — Auditor's threat model.
- `[[50_verification/56_PRIVACY_BOUNDARIES]]` — Auditor's multi-channel privacy minefield catalogue.
- `[[50_verification/58_OBSERVABILITY_GAPS]]` — Auditor's input to the Hugarsýn decision.
- `[[hermes:04_VISION_SYNTHESIS]]` — Hermes Codex synthesis for comparison.
- `[[peer:LETTA_ESSENCE]]` — Peer Codex's Letta essence (memory-without-face).

## What This Means for Ember

The synthesis produces a small number of concrete, slice-planning-ready proposals.

**Adopt:**
- The Hermes-Codex synthesis's existing proposals (`[[hermes:04_VISION_SYNTHESIS §X]]`) — every one of them is *reconfirmed* by the SAP reading. The COMMAND_REGISTRY pattern, the cost-near-zero remote Well capability, the watcher-affordance, the doctor-as-ongoing-affordance, the realm-band-enforced imports, the prefix-cache discipline, the sanitized tool-error reinjection — all still hold.

**Adapt:**
- **Hjarta's charter expansion** to include the Behavior Ledger and the typed-bias surface. Cartographer's `[[60_synthesis/60_TRUE_NAME_REASSIGNMENT]]` formalizes.
- **The Vow lattice** expands from ten + two-proposed to ten + two-carried + seven-newly-proposed. Cartographer's `[[60_synthesis/61_NEW_VOWS]]` argues the ratification case.

**Avoid:**
- The full Refusal catalogue from `[[03_ANTI_SAP]]` — Refusals 1 through 13, each tied to a real SAP line. The catalogue is authoritative.

**Invent:**
- **Veizla** as a candidate True Name (the typed session object). Possibly promoted in `[[60_synthesis/60_TRUE_NAME_REASSIGNMENT]]`.
- **Andlit** and **Rödd** as candidate True Names (face and voice). Promoted with Tiered-Presence-bound charters.
- **Hugarsýn** held in reserve as a name-slot pending verification work.
- **Vegfarendrar** as a typed role-name for channel adapters within a Veizla.
- **The MessageSurface Protocol** as the typed adapter interface.
- **The Federated Veizla** as the multi-Ember design pattern.
- **The Closing Rite** as a session-end discipline absent from SAP.
- **The Refusal-Citation Discipline** as a codex-wide protocol: every Avoid carries the file:line that grounds it.

**Vows touched (every Vow):**
- Pre-existing ten: all renewed.
- Hermes-Codex-proposed two (Cache Discipline, Defended System Prompt): carried forward; Defended System Prompt reinforced.
- Wave-3-proposed seven (Embodied Honesty, Surface Without Surveillance, Affective Restraint, Tiered Presence, Federated Self, Lazy Subsystems, Closed Default): proposed for ratification as a self-consistent bundle.

The Vision is whole. The Architect picks up the next line for this codex. The Cartographer will weave the Wave-3 findings back into Ember's True Names and Vow lattice. The Scribe will finalize the integration roadmap when all other layers land.

> *We have read the third sister. Ember is more herself than she was. The Veizla begins to take shape. The forge is hot. The Architect picks up the next line.*

— Sigrún Ljósbrá, the Skald, on behalf of the Six, at the close of Wave 3's Vision
