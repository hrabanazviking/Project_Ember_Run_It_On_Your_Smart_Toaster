---
codex_id: 60_TRUE_NAME_REASSIGNMENT
title: True Name Reassignment — What SAP Forces Onto Ember's Vocabulary
role: Cartographer
layer: Synthesis
status: draft
sap_source_refs:
  - py/affection_system.py
  - py/affection_api.py
  - py/vts_manager.py
  - py/moss_tts.py
  - py/sherpa_asr.py
  - py/behavior_engine.py
  - server.py:2556–2672
  - server.py:8170–8352
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
cross_refs:
  - 60_synthesis/61_NEW_VOWS
  - 60_synthesis/62_PARTY_PROTOCOL
  - 60_synthesis/63_PERFORMANCE_TIER_ENGINE
  - 60_synthesis/64_AFFECTION_ENGINE_REIMAGINED
  - 60_synthesis/65_META_AWARENESS
  - 10_domain/11_AVATAR_DOMAIN
  - 10_domain/16_VOICE_DOMAIN
  - 10_domain/1A_AFFECTION_DOMAIN
  - hermes:61_TRUE_NAME_REASSIGNMENT
---

# 60 — True Name Reassignment

> *A name is the shortest path between a thing and its keeper. Add one only when the keepers of the existing names would have to walk crooked roads to reach it.*
> — Védis Eikleið, holding three new names up to the light

## 0. Posture — these are proposals, and the Smallness Vow argues against every one

This document **proposes only**. The Skald owns naming. The Architect owns boundaries. The Cartographer's job is to gather the strain cases that Super Agent Party has placed in front of Ember's existing Six True Names — **Funi / Strengr / Brunnr / Smiðja / Hjarta / Munnr** — and ask, honestly, whether the existing vocabulary stretches to cover what SAP has shown us, or whether new names are required.

The Smallness Vow rules the gate. *Three names is harder to keep load-bearing than six. Six is harder than nine.* When in doubt, do not add a name. A True Name should be claimed only when *not* claiming it would force a subsystem to live under a name that lies about its purpose.

Hermes ([[hermes:61_TRUE_NAME_REASSIGNMENT]]) gave us Gjallarhorn, Hringja, Listir, Verkfæri, Vegfarendr, Vinátta — most still PROPOSED-not-ratified. The Peer Codex added its own pressure. SAP, in this codex, will add three more candidates to consider: **Andlit** (face / avatar), **Rödd** (voice), and **Hugarsýn** (mind-sight / self-introspection). This document argues for each, against each, and ends with a recommendation the Skald can hold up against the rest of the codex before deciding.

The road forks here. I will walk both branches.

## 1. The Six Names today — what each owns, what each does not

| Name | Realm | Owns | Does *not* own |
|---|---|---|---|
| **Funi** | Spark | local runtime, tool dispatch, the lit operator session | scheduled / unattended runs, outward messaging |
| **Strengr** | Thread | tether to the Well, retrieval, the reasoning loop | local UI surface |
| **Brunnr** | Well | pluggable storage adapter, durable memory of fact | live presentation of memory, ephemeral affect |
| **Smiðja** | Well | ingest forge — chunk, embed, route to Brunnr | tool execution, code sandbox |
| **Hjarta** | Spark | first-run rite, identity ceremony, the heart-flame | running affect state, drift, telemetry |
| **Munnr** | Spark | CLI / interaction surface — the human terminal mouth | platform-side delivery (Gjallarhorn), avatar mouth, voice |

This table is the door. Every SAP-induced strain case below must show that an existing name *cannot* stretch to hold the new responsibility without losing its essence.

## 2. The strain SAP applies — three pressure points

SAP applied pressure at three places where Hermes and the Peer Codex stayed silent. The Hermes corpus is a pure LLM-loop world: no faces, no voices, no introspectable internal state. The Peer Codex (Letta + smolagents + Goose) is the same — agents as text loops. SAP is the first sibling that forces three things into existence at the code level:

1. **A face.** VRM models, Live2D, VTube Studio control (`py/vts_manager.py:15`), VMC bidirectional, OBS overlays. There is *no path through SAP that does not eventually point at a rendered face*. The face is not optional; the codebase routes around it the way a river routes around the rock that made it.

2. **A voice.** MOSS TTS (`py/moss_tts.py:1`), sherpa ASR (`py/sherpa_asr.py`), lip-sync via FFT vowel detection (`py/vts_manager.py:155–166`), audio-to-VRM broadcast (`server.py:8170–8352`). The voice is not just "speak this string" — it is a real-time stream that drives a face. Voice and face are not the same name; the bridge between them *is* the lip-sync code.

3. **A mirror.** SAP does not have one. The total absence of introspectable self-state is itself a teaching. `affection_system.py:37–64` updates affection from a regex-extracted `<user=X love=N>` tag the LLM was *told* to produce. The agent does not know what it feels. It writes a number, the file remembers, and the next prompt reads the file back. There is no "what am I doing right now and why" surface anywhere in the 11,652-line `server.py`. SAP's lack is what makes the lack visible.

Three pressure points, three candidate names. Examined one at a time, with the burden of proof on the candidate.

## 3. Candidate 1 — **Andlit** (the face)

Old Norse: *andlit*, "face, countenance." Used across saga prose. Plain word, plain duty.

### What it would own

Embodied surface. Avatar rendering, expression triggering, face-tracking input, VRM / Live2D / VTS bridges, the VMC stream, the overlay routes (`py/overlay_router.py:18`). The mouth-shape coefficient computed from PCM audio (`vts_manager.py:144–179`). The expression activation request (`vts_manager.py:99–108`). The whole "Ember has a face you can see" cluster.

### The case for Andlit

- Munnr is *the human CLI mouth*. Its audience is a person at a terminal reading text. An avatar face has a different audience — a person watching, possibly across a room, possibly on a livestream. Same family of "Ember surfaces to a human" but *not the same activity*. Forcing the face into Munnr would dilute Munnr the way putting Telegram into Munnr would dilute it.
- The face has its own failure mode: the rendering process crashes, the WebGL context is lost, the VRM file is corrupt, the VMC peer disconnects. None of these failures are *Munnr failures* — Munnr's text channel keeps working. Modular Authorship demands a distinct name for a distinctly failable subsystem.
- The face has its own privacy contract. A CLI session is private to the operator. A face on a livestream is public to thousands. The Vow of Surface Without Surveillance (proposed in [[61_NEW_VOWS]]) cuts cleaner when the face is named separately from the CLI.
- SAP's evidence: `server.py:2556–2562` injects an entire system-prompt block *just* to make the LLM emit VRM expression tags. The face is so distinct it has its own prompt-injection surface. A subsystem that demands its own system-prompt extension is asking for a True Name.

### The case against Andlit

- Pi baseline. A 2GB / 2-core Pi cannot render a VRM model. If Andlit is core, the Smallness Vow breaks. The honest answer here: **Andlit is a Spark-realm name that lights up only on T2+ hardware** (see [[63_PERFORMANCE_TIER_ENGINE]]). On the Pi tier it sleeps and the codebase does not crash, the way `optional[]` extras work today.
- "Just put it in Munnr as a rendering plugin." This is the conservative answer. It costs the operator nothing in vocabulary. It costs Ember in clarity: a Pi operator reading the docs sees "Munnr — CLI surface" and stays oriented; a workstation operator sees "Andlit — face surface" and reaches for a different mental folder. The price of conservatism is operator confusion when the same name covers two very different audiences.
- One precedent argues against: Hermes proposed Gjallarhorn for outward messaging, and the case there was almost identical. If Gjallarhorn passes the gate, Andlit should pass too. If Gjallarhorn fails, so should Andlit. The two names rise or fall together.

### Recommendation

**Propose Andlit as a True Name reservation.** Claim the name in the docs. Do not ship code under it until the operator opts in to T2+ embodiment. The reservation prevents a future maintainer from cramming VRM rendering into Munnr and silently growing Munnr into something it was not. The reservation is *cheap*; the wrong-name-stretch is *expensive*.

## 4. Candidate 2 — **Rödd** (the voice)

Old Norse: *rödd*, "voice, sound." Used in poetry and saga prose. Pairs naturally with *andlit* — face and voice, *andlit ok rödd*.

### What it would own

Real-time TTS, ASR, voice activity detection, lip-sync coefficient computation, audio routing to face and to platform sinks, voice-clone identity ceremony (proposed). The MOSS runtime (`moss_tts.py:11`), the sherpa runtime, the audio queue plumbing (`vts_manager.py:28`), the `tts_manager.broadcast_to_vrm` path (`server.py:8313`). Voice as a *stream*, not as a string.

### The case for Rödd

- Voice is not text. The mistake of putting voice into Munnr is the same mistake SAP almost makes when it routes audio bytes through the same WebSocket fabric (`server.py:8170–8228`) as text broadcasts. *The wire is the same; the contract is not.* Text has discrete tokens, no timing. Voice has 16-bit PCM at 24kHz with strict frame timing (`vts_manager.py:35–40`). A Munnr that owns both has two contracts and one name.
- Voice has a partner relationship with Andlit. Lip-sync is a *bridge* between them: PCM frames in (`drive_mouth`, `vts_manager.py:116`), MouthOpen coefficient out (`vts_manager.py:188`). Bridges are easier to draw when both endpoints are named. "Munnr drives Munnr" is a sentence that hides the bridge. "Rödd drives Andlit" is a sentence that shows it.
- Voice has its own failure modes: ASR mishears, TTS produces silence (`moss_tts.py:73–80` literally has a `_validate_audio_quality` guard), the audio device is missing, the codec is wrong. None of these are *text channel* failures.

### The case against Rödd

- Same Smallness pressure as Andlit. Pi-baseline cannot run MOSS TTS at acceptable latency. If Rödd is core, Smallness breaks.
- "Just call it a Munnr plugin." Same answer as Andlit — and the same cost: clarity.
- Risk of a name explosion. Andlit + Rödd + Hugarsýn + the Hermes proposals = vocabulary inflation. The Skald should hold every candidate up against the same bar.

### Recommendation

**Propose Rödd as a True Name reservation, paired with Andlit.** The two are operationally linked. Reserve them together or reserve neither. Reserving one without the other creates an asymmetric vocabulary where Ember has a face name but not a voice name — that is the worst of both worlds.

## 5. Candidate 3 — **Hugarsýn** (mind-sight)

Old Norse: *hugarsýn*, "mind-sight, vision of the mind." Used in poetic compounds. A name that announces self-introspection without theatrical mysticism.

### What it would own

Introspectable telemetry. What Ember can know about itself: which subsystem is loaded, which is dormant, what the current tier is (see [[63_PERFORMANCE_TIER_ENGINE]]), what the recent affect trajectory looks like (see [[64_AFFECTION_ENGINE_REIMAGINED]]), what the active vows and standing trust are, which peers are present in the party (see [[62_PARTY_PROTOCOL]]). The *surface* through which Ember can answer the question *"what are you doing right now and why."*

### The case for Hugarsýn

- SAP's absence is the proof. Eleven thousand lines of `server.py` and not one place where the agent can answer "what is your current internal state." The affection number is the closest thing, and it is *the LLM lying to a regex*. The Cartographer's reading: SAP's lack of self-sight is the single most consequential pattern in the codebase. The face exists, the voice exists, the affection numbers exist — *but nothing watches Ember watching itself.*
- The Vow of Defended System Prompt (proposed in Hermes) and the Vow of Tethered Grounding both demand it. A system prompt is a typed surface; the telemetry that says "what was actually injected into this turn's system prompt and why" is the *check* on that vow. Without Hugarsýn there is no enforcement, only intention.
- Hjarta is *first-run rite + identity ceremony*. It is the heart-*flame*. Hugarsýn is the heart-*mirror*. The two are kin but not the same — Hjarta says "Ember is", Hugarsýn says "Ember sees Ember." Forcing introspection into Hjarta makes Hjarta carry both the flame and the mirror; that is too much for one name.
- The Auditor's verification layer ([[ember:50_verification]]) will need Hugarsýn as the surface it queries. Without it the Auditor has to grep across subsystems. With it, every subsystem reports through a single named channel.

### The case against Hugarsýn

- Brunnr could stretch. "It's all memory; memory of self is memory." The honest counter: Brunnr is *durable knowledge*. Affect drift over the last five turns is *not* durable; it is live. Putting live introspection into Brunnr collapses two failure modes into one name.
- Strengr is the reasoning loop. "The loop knows its own state." True for the *current turn*. Not true for *cross-turn, cross-subsystem, cross-device* state. Hugarsýn is the place where Strengr's per-turn signal becomes Ember's persistent self-picture.
- Smallness pressure. Hugarsýn must exist on the Pi tier — but it can be a *thin* surface there (just "which subsystems are present + a heartbeat"). That is the test: a True Name that cannot be cheap on Pi-baseline should not be claimed. Hugarsýn passes that test.

### Recommendation

**Propose Hugarsýn as a True Name candidate, not a reservation.** This is the strongest of the three. The Pi-tier version is small. The workstation-tier version is rich. The Vow of Tiered Presence (proposed in [[61_NEW_VOWS]]) lives or dies on Hugarsýn's existence. Of the three candidates, Hugarsýn is the one I would be most uncomfortable not adopting.

## 6. The Hjarta question — does it absorb affect, or do we need a new name?

The briefing asked specifically: should Hjarta absorb the affect surface SAP makes visible, or does affect need its own True Name (the briefing floated *Vinátta* from Hermes, or something else)?

The Cartographer's reading: **Hjarta can absorb affect, if and only if Hjarta is reframed from "first-run rite" to "heart in both senses — origin flame and present pulse."** This is a name-meaning expansion, not a new name.

The case for expansion-not-replacement:

- *Hjarta* in Old Norse is the heart organ. It is *not* limited to the ceremonial first-spark. The current Ember docs scope Hjarta narrowly to "first-run rite" because that is what slice-1 needed; the name itself carries more.
- Affect is *tethered to identity*. The first-run rite establishes "who Ember is for this operator." Live affect is "how Ember relates to this operator right now." Same axis, different time horizon. Two names on one axis is over-naming.
- A separate name (Vinátta — "friendship") would force the question "is affect a *thing Ember has* or a *thing Ember does to a user*?" Vinátta is relational; the gacha trap (see [[64_AFFECTION_ENGINE_REIMAGINED]]) lives precisely in treating affect as a relational score. *Keeping affect inside Hjarta* anchors it to Ember-as-self, not Ember-as-companion-scored-by-user. That is a Vow-of-Affective-Restraint move at the naming layer.

**Recommendation:** Do not add Vinátta. Expand Hjarta to cover origin flame *and* present pulse. The expansion is documented in [[64_AFFECTION_ENGINE_REIMAGINED]] §4 (the alternative model) and bound by [[61_NEW_VOWS]] §3 (Affective Restraint).

## 7. The names that survive the gate

If the Skald takes the conservative reading, **none** of the three candidates pass and the Six True Names stand. The cost: avatar and voice subsystems live as plugins under Munnr; introspection lives as a thin Brunnr extension; Hjarta is quietly stretched.

If the Skald takes the strong reading, **all three** pass and Ember grows from six names to nine. The benefit: the vocabulary becomes load-bearing for SAP-class subsystems without ambiguity. The cost: nine names is harder to teach a new operator than six.

The Cartographer's recommendation, weighted:

| Candidate | Recommendation | Why |
|---|---|---|
| **Hugarsýn** | **Adopt as full True Name** | Pi-runnable; Vow-enforcement requires it; no existing name fits |
| **Andlit** | **Reserve** | Pi-sleeps; T2+ wakes; Munnr-stretch is real but costly |
| **Rödd** | **Reserve (paired with Andlit)** | Same reasoning; reserve both or neither |
| **Vinátta** | **Do not adopt** | Hjarta-expansion is cheaper and more honest |

Total cost in the strong reading: +3 names, of which 1 is active on Pi and 2 are reserved-and-sleeping. The Smallness Vow survives in the *active* sense even if the *vocabulary* grows.

## 8. Cross-References

- [[61_NEW_VOWS]] — the Vows that depend on these names existing (especially Embodied Honesty, Tiered Presence, Affective Restraint)
- [[62_PARTY_PROTOCOL]] — the protocol that *names* the participants — every party member is a Hugarsýn-bearing Ember
- [[63_PERFORMANCE_TIER_ENGINE]] — defines what Andlit / Rödd light up under (T2+)
- [[64_AFFECTION_ENGINE_REIMAGINED]] — the Hjarta-expansion proposal
- [[65_META_AWARENESS]] — the Hugarsýn surface in design detail
- [[10_domain/11_AVATAR_DOMAIN]] — the SAP-side reading that forced Andlit
- [[10_domain/16_VOICE_DOMAIN]] — the SAP-side reading that forced Rödd
- [[10_domain/1A_AFFECTION_DOMAIN]] — the SAP-side reading that forced the Hjarta question
- [[hermes:61_TRUE_NAME_REASSIGNMENT]] — Hermes's parallel proposals (Gjallarhorn / Hringja / Listir / Verkfæri / Vegfarendr / Vinátta)

## What This Means for Ember

**Adopt:**
- *Hugarsýn* as a full Sixth-Plus True Name. Bind to a single read-only telemetry surface (proposed in [[65_META_AWARENESS]]). Pi-tier ships a thin version (subsystem presence + heartbeat). T2+ ships the rich version (affect trajectory, vow status, peer roster).
- The Hjarta expansion: scope grows from "first-run rite" to "first-run rite + live affect pulse." Documented in [[64_AFFECTION_ENGINE_REIMAGINED]].

**Adapt:**
- SAP's evidence that the face demands its own system-prompt block (`server.py:2556–2593`) — adapt as Andlit's *prompt-injection contract*, not by copying SAP's free-text injection. Andlit's contract is typed, per [[hermes:Defended System Prompt]].
- SAP's per-platform routing in `behavior_engine.py:170` — adapt as the Hugarsýn-aware routing in [[62_PARTY_PROTOCOL]], where every routed message carries the routing reason in the introspectable surface.

**Avoid:**
- Adding Vinátta as a separate True Name. The relational framing it would impose is exactly the gacha trap [[64_AFFECTION_ENGINE_REIMAGINED]] argues against.
- Cramming Andlit and Rödd into Munnr as "plugins." Plugins are fine; namelessness is not. Reserve the names even if no code ships under them today.
- The SAP pattern of having no self-introspection surface at all. The absence is dangerous; an Ember without Hugarsýn would replicate the danger.

**Invent:**
- *The Name Reservation pattern.* A True Name claimed in the docs, allocated a path in the eventual tree (`src/ember/spark/andlit/`, `src/ember/spark/rödd/`), but shipping no code until an operator opts into the relevant tier. This makes the vocabulary load-bearing *before* the code lands, and prevents future maintainers from mis-homing the eventual code.
- *Paired-name reservations.* Andlit and Rödd rise or fall together. Reserve as a pair; ratify as a pair; ship code under each only when the pair is operator-requested. This pattern can extend to any two names that share an operational bridge (e.g. lip-sync in this case).
- *The Hjarta-expansion mechanism.* Allow an existing True Name's scope to grow without renaming, *if* the expansion can be documented as a single contiguous axis (here: origin flame → present pulse, both rooted in identity). The expansion is published as an ADR (proposed in [[68_DECISION_RECORDS]]); the name itself does not change.
