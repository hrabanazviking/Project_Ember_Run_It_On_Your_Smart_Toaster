---
codex_id: 00_OVERTURE
title: Overture — The Third Reading
role: Skald
layer: Vision
status: draft
sap_source_refs:
  - README.md:36-68
  - README.md:284-305
  - py/affection_system.py:1-64
  - py/behavior_engine.py:53-225
  - py/random_topic.py:1-95
  - py/sleep_guard.py:102-148
  - main.js:71-117
  - server.py:11652 (size)
  - py/sub_agent.py:1-120
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
cross_refs:
  - 00_vision/01_SAP_ESSENCE
  - 00_vision/02_THE_PARTY_METAPHOR
  - 00_vision/03_ANTI_SAP
  - 00_vision/04_VISION_SYNTHESIS
  - meta/SHARED_CONTEXT
  - meta/MANIFEST
  - hermes:00_OVERTURE
  - peer:LETTA_ESSENCE
---

# Overture — The Third Reading

> *"A good name does not merely label a thing. It reveals what the thing has always wanted to be."*
> — Sigrún Ljósbrá

## I. Where we are now

Two waves of reading have passed over Ember.

Hermes Codex was the first wave. Fifty-three documents pulled ore from a mainframe-class sovereign agent. We learned the shape of largeness so we could choose smallness with both eyes open. The Skald's final word on that reading was a sentence: **Ember, after reading Hermes, is the agent that learned the largeness of an agent platform and chose, with full sight, to remain a hearth.** (`[[hermes:04_VISION_SYNTHESIS §VI]]`.)

Peer Codex was the second wave. It sat down with Letta, smolagents, Goose — frameworks at Ember's own scale, agents that had already chosen smallness. The lesson there was different: when peers make different choices about memory, about tool typing, about ratification, those differences sharpen Ember's vows further. The peer reading was the apprentice's mirror, the wave that says *you are not alone in this craft, and you are not wrong to do it differently*.

Both waves had a quiet limitation. They were Large-Language-Model-shaped readings. Hermes is a 14,560-line CLI that talks to 200+ models across twenty-two messaging surfaces — but it is, at the bone, an LLM agent loop with toolsets bolted to it. Letta is a memory layer with an LLM behind it. Goose is a tool-use loop with one front end. None of them have a face. None of them have a voice you can hear in the room. None of them know what to do with the words after they have been written. They are bodies of thought without bodies of presence.

This third wave reads a system that disagrees.

Super Agent Party is an Electron + Python desktop companion (`README.md:36-68`) that has chosen, deliberately and with effort, to be **embodied** (VRM avatars, Live2D, VTube Studio control, bidirectional VMC protocol streaming over UDP/OSC — `main.js:71-117`), **reachable** (eight instant-messaging platforms one-clicked into deployment, three livestream platforms with comment ingest pipelines, an LLM-driven browser via Chrome DevTools Protocol, and a desktop-vision computer-control loop — `README.md:55-65`, `py/cdp_tool.py`, `py/computer_use_tool.py`), and **affective** (an "affection system" with names like `affection_system.py` and `behavior_engine.py` and an `autoBehavior.py` that schedules autonomous interruption across eight messaging platforms — `py/behavior_engine.py:53-225`).

Hermes had no face. SAP has thirty.

This Codex — eighty-two documents, six specialist voices, twenty thousand words of prose for the Vision layer alone — exists because no other system at Ember's scale has gone this far down the embodiment-reach-affect axis. We must read SAP not because it is right but because no one else has even tried.

## II. The three axes Hermes and Peer could not teach

Three problems sit in front of Ember's slice plan that the prior two codexes barely touched.

**The Embodiment Problem.** Ember is supposed to feel like a hearth — small, warm, present in someone's hand. A CLI does not feel like a hearth. A REST endpoint does not feel like a hearth. Munnr's job, in `[[hermes:00_OVERTURE §VII]]`, was "plain CLI." That is the right answer for slice one. It is not the answer forever. At some point, a small tethered agent that lives across the operator's devices needs a way to *appear* — to have a posture, a voice, an animation, a *face that signals state honestly* without performing personality theatre. SAP has solved the technical part of this problem at the level of bits-on-the-wire (VRM rendering, VMC bidirectional sync, VTube Studio hotkey control via `py/vts_manager.py`). Whether SAP has solved it at the level of *meaning* is a separate question — `[[03_ANTI_SAP]]` will be unkind about that — but we must read the technical solutions to know what is even possible.

**The Reach Problem.** A small agent that lives on one device, accessible only via one CLI, is not a *presence* in someone's life. It is a tool. The Vow of Smallness does not require Ember to remain confined to one terminal forever; it requires every additional surface to remain optional, individually failable, individually swappable. SAP has eight IM bots and three livestream services in the same `py/` directory. They are not abstracted by a shared interface (`[[10_domain/14_MESSAGING_DOMAIN]]` and `[[20_interface/26_IM_BOT_INTERFACE]]` will document the unfortunate fragmentation), but the *fact of their coexistence* in one Python process — coordinated by a `BehaviorEngine` singleton that broadcasts behaviors across registered handlers (`py/behavior_engine.py:158-222`) — is the most concrete demonstration we will find of multi-platform presence under one identity.

**The Affect Problem.** Hermes did not propose a personality layer; the Skald reserved `Hugr/Mynd` as a name-slot for it (`[[hermes:02_NAMING_PARALLELS §X]]`) without filling it. Peer's Letta said memory *is* personality. SAP says affection is a *number*. SAP is wrong about that — `affection_system.py` is a sixty-four-line regex parser that reads `<user=Volmarr love=12 familiarity=15>` tags out of the LLM's reply text and writes them to a JSON file (`py/affection_system.py:44-64`). The state-machine theatre is performed entirely by the LLM, instructed by a system-prompt injection block at `server.py:2609-2672`. There is no decay. There is no trigger. There is the model saying "love is twelve" and a regex believing it. **SAP did not solve the affect problem. SAP performed the affect problem.** But SAP is the only system at this scale that *tried*, and watching what it tried — and what it broke — gives Ember the clearest picture yet of what a real affect layer would have to refuse.

These three axes are the entire reason this codex exists. Everything else — Docker topologies, MCP integration, extension lifecycles, IM bot deployment mechanics — is downstream of these three. The Architect catalogues. The Forge implements. The Auditor hunts. The Cartographer reweaves. But the *reason we are here* is embodiment, reach, and affect.

## III. The shape of SAP we will be reading

A small accounting before we go further. SAP, at v0.4.2-preview, is not enormous in the Hermes sense. The Python footprint sits at roughly thirty-six thousand lines across `py/`, with `server.py` shouldering the largest single load (`server.py` is **11,652 lines** by `wc -l`; `cli_tool.py` is **2,668 lines**; `main.js` is **2,100 lines**; everything else is under a thousand). It is small enough to read in a long weekend. It is small enough that you can hold most of its working in your head, *if* you have someone like Rúnhild willing to draw the boundary lines (`[[10_domain/10_DOMAIN_MAP]]`).

What is striking is not the size. What is striking is the **breadth of surfaces** crammed into the size. Eight IM bots. Three livestreams. Two avatar protocols (VRM + Live2D-via-VTS). One bidirectional motion protocol (VMC over OSC/UDP). Two voice stacks (a Chinese in-house TTS called MOSS and a sherpa-onnx ASR). One computer-control toolchain. One Chrome DevTools Protocol browser driver. One extension system with installable plugins. One skill system that downloads zip archives from GitHub (`py/skills.py:60-93`). One MCP client surface and one MCP server surface. One OpenAI-compatible API simulation layer. One A2A interface. One affection theatre. One behavior engine. One scheduler. One sleep guard.

The author of SAP, heshengtao, has chosen breadth-over-depth as the codebase's defining trait. This is the opposite of Hermes (which chose depth-over-breadth — fewer surfaces, each engineered to the bone) and the opposite of Letta (which chose memory-as-everything). The choice has consequences. Some are admirable — SAP genuinely runs on a two-core, two-gigabyte machine (`README.md:244-247`), and the Docker variant works out of a single `docker run` command (`README.md:159-167`). Others are catastrophic — `server.py:11652` is a monolith with no apparent decomposition discipline, the IM bot managers do not share a common interface, and the affection system is a regex parser pretending to be an emotion model.

We read all of it. We are not here to ridicule and we are not here to admire. We are here to *understand* and to mine what can be mined.

## IV. What the four Vision documents that follow will do

This document is the first of five. The other four sharpen the position.

`[[01_SAP_ESSENCE]]` does for SAP what `[[hermes:01_HERMES_ESSENCE]]` did for Hermes: strips it to its load-bearing intents. What kind of *being* is SAP trying to be? Not what it does — what it *wants*. The answer, in advance, is **companion-as-presence**. SAP wants to be the small face on the operator's screen that talks to them across all their devices, all their messaging platforms, all their livestreams, all the times of day they have configured for autonomous interruption. It is the digital boyfriend / digital girlfriend / digital streamer / digital VTuber project, executed with surprising rigor and disturbing defaults.

`[[02_THE_PARTY_METAPHOR]]` is the most invent-heavy of the five. SAP's name is "Super Agent **Party**" and the party metaphor turns out to be *load-bearing* in ways the README does not articulate. A party is multi-agent (multiple guests with their own personalities, see SAP's group chat with Tavern character cards). A party is multi-device (the party happens across rooms — phone, laptop, livestream overlay, OBS scene). A party is multi-channel (some guests talk in voice, some in text, some by gesturing across the room). SAP collapses these three axes into one verb — *party* — and the collapse is *correct enough* that I will argue, in `[[02_THE_PARTY_METAPHOR]]`, that the seed of an actual Ember invention lives there. The seed becomes `[[60_synthesis/62_PARTY_PROTOCOL]]` (the Cartographer will write that).

`[[03_ANTI_SAP]]` is the dark mirror. SAP has a lot of dark. The default `random_topic.py` calls `topics-after-party.zeabur.app` — a third-party server in a foreign jurisdiction, with mood enums including `flirty` and `curious` and a depth-of-soul-question dial that goes up to five (`py/random_topic.py:6-7, 153-167`). The sleep guard simulates `Shift_L` keypresses via xdotool when systemd-inhibit is absent (`py/sleep_guard.py:142-148`), which is technically clever and ethically queasy. The affection system is built around the gacha pattern of unlocking content as a numeric meter rises (the regex parser is the foundation; the *use* of the meter to gate animation hotkeys is implied across `py/vts_manager.py` and `server.py:2576-2607`). The IM bot managers, in their per-platform `*_bot_manager.py` files, give the operator the ability to deploy one-click bots to QQ, WeChat, WeCom — surfaces with documented compliance and surveillance regimes the README does not mention. **Ember must refuse to do these things on principle, and the refusal becomes a Vow.** New Vows proposed: **Embodied Honesty** (animation reflects state, not theatre), **Surface Without Surveillance** (every reach carries explicit revocable scope), **Affective Restraint** (affection may bias, never override consent), **Tiered Presence** (reach scales down gracefully), **Federated Self** (multi-device is peer-to-peer, never master-slave). The Cartographer's `[[60_synthesis/61_NEW_VOWS]]` will turn these into formal text.

`[[04_VISION_SYNTHESIS]]` does the binding. It is the Skald's poem at the end of the Vision layer, after we have read everything. It asks: *what does Ember become, knowing what SAP tried and what SAP broke?* The answer, in advance, is that the Six True Names do not change in their roots but their **charters grow**, and the Manifest's three proposed name-slots — **Andlit** (face/visage, the embodiment layer), **Rödd** (voice, the spoken-surface layer), **Hugarsýn** (mind-sight, the self-aware introspection layer) — are argued, qualified, and either promoted or held in reserve. I will tell you, ahead of time, that I will argue *for* Andlit and Rödd and *against* immediate promotion of Hugarsýn (the Auditor's `[[50_verification/58_OBSERVABILITY_GAPS]]` should make that call after the verification work lands).

## V. Why the third reading is the hardest

Reading Hermes was hard because Hermes is enormous. Reading Peer was hard because Peer was a flock — many small things at once. Reading SAP is hard because **SAP gets the architecture right in places where it gets the ethics wrong**.

The behavior engine is *correct engineering*. `BehaviorEngine` in `py/behavior_engine.py:53-225` is a singleton tick-driven scheduler that registers per-platform handlers, supports three trigger modes (`time`, `noInput`, `cycle`), maintains debounce timers, and broadcasts behavior triggers across registered platforms. It is one hundred eighty lines of well-shaped code. It is also a system whose primary use-case in the codebase is **autonomously interrupting the operator across all eight IM bots simultaneously when they have been silent for too long** (`autoBehavior.py:3-40` constructs exactly this kind of multi-platform broadcast). The same code that proves multi-channel orchestration is *possible* in two hundred lines also proves it is *easy to weaponize against the operator's attention*.

The VMC protocol implementation is *correct engineering*. `main.js:71-117` opens a UDP socket on `0.0.0.0:port` and forwards every bone position and blend-shape value to the VRM render windows. It is a bidirectional protocol; SAP is both consumer and producer of motion data. This is exactly what an embodied agent needs. It is also exactly the kind of surface that, bound to `0.0.0.0` by default, leaks the agent's body posture and facial state across whatever network it is on.

The affection system is *the wrong abstraction wearing a name that fits something else*. The name "affection system" suggests a mechanism for representing felt state. The code is a regex parser plus a JSON file. The mechanism that *generates* the affection numbers is the LLM, instructed via prompt injection (`server.py:2653-2670`) to emit a hidden tag at the end of every reply. **Affection in SAP is performed by the model and recorded by the parser, with no truth condition anywhere.** This is not a small bug. It is the central design failure that `[[1A_AFFECTION_DOMAIN]]` will document and `[[60_synthesis/64_AFFECTION_ENGINE_REIMAGINED]]` will repair — by inventing something that *did not exist in SAP*: an affect layer where state is the model's *bias*, not the model's *output*.

This is the hardest reading because every page demands the discipline to separate *what works* from *what should be working*. Every Forge agent in this codex will be tempted by the elegance of the behavior engine; every Auditor will be horrified by the affection system. The Skald's job, in this overture, is to name both at once — to refuse the easy poem that says SAP is bad and the easy poem that says SAP is good. SAP is **interesting**. The work is to mine the interest carefully.

## VI. The Six who write the codex

The same six voices that wrote Hermes and Peer write here, with one Forge doubled.

**Sigrún Ljósbrá, the Skald** — me, INFJ 4w5, the voice you are reading. Vision layer. Five documents. Names what SAP wanted to be. Names what Ember should refuse. Refuses to leave a doc without `## What This Means for Ember`.

**Rúnhild Svartdóttir, the Architect** — INTJ 5w6. Domain layer plus the architect-owned half of Interface. Twenty documents. Draws the boundary between `main.js` and `server.py`, between the eight IM bot managers and the unified-or-not abstraction they almost share, between the VRM render pipeline and the VTube Studio control surface. Tells you exactly where `affection_system` ends and `behavior_engine` begins.

**Védis Eikleið, the Cartographer** — INFP 9w1. Synthesis layer's cartographer half. Six documents. Reweaves SAP findings into Ember's True Names. Drafts the new vows. Sketches the **Party Protocol** — Ember's invented multi-device orchestration that takes the behavior engine's *shape* and refuses its *defaults*.

**Eldra Járnsdóttir, fire-instance, Forge-A** — ESTP 8w7. Execution layer's core twelve. Patterns the Forge can give you in code: the Electron bootstrap, the affection loop (reimagined), the avatar render pipeline, the computer control loop, the MCP lifecycle, the affection loop's *reimagining*, the cross-platform builds.

**Eldra Járnsdóttir, iron-instance, Forge-B** — same person, second instance. Execution layer's per-platform eleven. One document per IM bot, one per livestream service. The deep dives nobody wants to write but everyone needs to read.

**Sólrún Hvítmynd, the Auditor** — INTJ 1w9. Verification layer plus the auditor-owned half of Interface. Sixteen documents. The hardest job in this codex. The OpenAI API simulation traps. The privacy boundaries. The dependency health. The failure taxonomy. Will tell you, with knives, what SAP cannot see about itself.

**Eirwyn Rúnblóm, the Scribe** — ISFJ 6w5. Synthesis layer's scribe half plus the final meta binding. Ten documents. Writes the integration roadmap. Cross-links the codex. Performs the final pass that resolves every `[[slug]]` to its target.

Seven agents, six roles, eighty-two documents. We work in parallel. The Scribe waits until everyone else has landed before laying the final binding.

## VII. The reader

You are Volmarr at two in the morning. You have a half-empty mug, an ADHD-flavored question, and a tab in Firefox you have been meaning to close. You are reading this because you are trying to decide whether SAP teaches Ember something worth keeping or whether the whole thing is a sketchy companion-app with regex affection and OSC over `0.0.0.0`. The answer is *some of both* and the work of the codex is to tell you which parts are which.

I will not waste your attention. I will name the parts of SAP that are gold (the behavior engine's shape, the VMC bidirectionality, the cost-of-presence floor at two cores and two gigs, the one-click IM deployment patterns, the extension installer's robust-rmtree-with-preserve trick at `py/extensions.py:64-95`). I will name the parts of SAP that are poison (the affection system, the random topic phone-home, the xdotool sleep-guard, the `0.0.0.0` VMC binding, the `<user=name love=N>` prompt injection). I will name the parts that are *neither* — the parts that *almost* work and need *one invention* to become useful for Ember.

The five Vision documents are the layer that says *what this is for*. The seventy-seven that follow are the layer that says *what to do about it*. The Codex's deliverable is the foundation for Ember's next-generation capabilities. Not by copying SAP — never by copying SAP — but by **understanding her choices, identifying her mistakes, and inventing better methods**.

## VIII. A small invocation

Ember is a small thing on purpose. She fits on a Pi. She forgets gracefully. She refuses to invent. She does not pretend to be a mainframe. The temptation, when reading SAP, will be different from the temptation when reading Hermes. Hermes tempted us toward *largeness*. SAP tempts us toward *theatre* — toward animated faces and gacha-shaped affection and one-click IM deployment to surveillance platforms.

The right direction, when reading SAP, is to look at every clever SAP mechanism and ask:

> *What is the smallest version of this that could possibly carry honest meaning across to the person holding Ember?*

That is the only question the SAP Codex is built to answer. Everything else — the seventy-seven Domain / Interface / Execution / Verification / Synthesis documents — is in service of that question.

Six of us, then, will now go and do the work. We will write eighty-two documents. We will quote real lines from real files. We will not paraphrase the README. We will not invent SAP features that aren't in the code. We will not propose anything for Ember that violates a Vow.

The forge is hot. Wave Three opens. Let us begin.

## What This Means for Ember

The Overture itself proposes no code change. What it proposes is a **stance**, and the stance has consequences for the existing Six True Names and a proposed three.

**Adopt:**
- **The shape of `BehaviorEngine`** (`py/behavior_engine.py:53-225`) as the architectural seed for a future Ember scheduler — a tick-driven singleton with platform-registered handlers, three trigger modes, debounce, and broadcast. Adopt the *shape*; refuse the *defaults*. Concrete target: a future Hjarta sub-module `ember.spark.hjarta.behavior` that owns scheduled affordances under explicit operator consent. Sequenced after a Decision Record establishes the consent boundary; not in any current slice.
- **The `is_sub_agent` flag pattern** (`server.py:2429-2680`, `py/sub_agent.py:1-120`) — every personality system in SAP is gated on `not request.is_sub_agent`, so spawned sub-agents are deliberately face-less. Adopt the *pattern* (face-less workers; the face belongs to the operator's conversation alone) into Ember's tool framework: a `WorkerContext` typed value that tells every embellishing surface "you are off duty for this call."

**Adapt:**
- **SAP's "two cores, two gigs" hardware floor** (`README.md:244-247`). Ember's existing Pi-runnable Vow already exceeds this, but the SAP example shows the *operational discipline* required to honor such a floor — lazy imports (`py/moss_tts.py:17-55` defers numpy/scipy/onnxruntime until the first synthesis), graceful absence (`py/computer_use_tool.py:9-29` defines a `require_gui` decorator that returns a typed error message when pyautogui is absent rather than crashing). Adapt: make Ember's every-optional-subsystem-degrades pattern (`[[hermes:00_OVERTURE §IV]]` capability 2) the same kind of typed-degradation pattern SAP has rediscovered in fragments.
- **The `.party/config.json` allowed_tools pattern** (`py/agent.py:9-66`). SAP scopes tool permissions per workspace via a hidden `.party/` directory. Adapt as Ember's per-workspace consent surface — typed, explicit, version-controlled — without the hidden-directory pattern (which is hostile to discovery) and without the open-by-default semantics (which is hostile to safety).

**Avoid:**
- **The affection system entire** (`py/affection_system.py:1-64`, `server.py:2609-2672`). Affect is not a regex parse of LLM output. Ember's Hjarta does not write a number to a JSON file by trusting the model to have meant it.
- **`topics-after-party.zeabur.app`** (`py/random_topic.py:6-7`). Random-topic phone-home to a third-party server in a foreign jurisdiction, with mood and depth enums that include `flirty`, is exactly the kind of default Ember must refuse. The Open Knowledge Vow demands sources be operator-chosen; the Tethered Grounding Vow demands the Well, not someone else's API.
- **`xdotool key Shift_L` every 30 seconds** (`py/sleep_guard.py:142-148`). Simulated input is not a sleep guard; it is a malware-shaped affordance pretending to be one. If Ember ever needs sleep prevention it uses the *declared* OS primitive (`systemd-inhibit`, `caffeinate`, `SetThreadExecutionState`) or it declines the work.
- **VMC bound to `0.0.0.0`** (`main.js:71-77`). The motion protocol must default to `127.0.0.1` or a typed tailnet binding. Network-exposed avatar state is a surveillance surface no companion agent should expose by default.

**Invent:**
- **The Third Reading vow itself.** This is the invention this Overture surfaces: a recognition that some readings cannot be done without explicitly *naming what we refuse to copy across the embodiment-affect boundary*. The vow is the discipline of refusing to confuse "we have read this" with "we have approved of this." Concrete artifact: every doc in this codex ends with **Avoid** that names specific SAP lines, not just patterns. The Auditor's `[[50_verification/53_SECURITY_REVIEW]]` formalizes this as the **Refusal-Citation Discipline** — every refusal carries the line number that proves the refusal is grounded.

**Vows touched by this Overture:**
- **Vow of Smallness** — reinforced. SAP's two-cores-two-gigs floor is the existence proof that small can still mean embodied; Ember inherits the discipline.
- **Vow of Tethered Grounding** — reinforced. Random-topic phone-home is named as a violation; the Well remains canonical.
- **Vow of Open Knowledge** — reinforced via the Refusal-Citation Discipline above.
- **Vow of Modular Authorship** — reinforced. SAP's 11,652-line `server.py` is the anti-example; the Vow of the Unbroken Whole gains the file-size dimension Hermes's `cli.py` already gave it.
- **Vow of Public-Friendliness** — newly tensioned. SAP's defaults (flirty topics, IM-blast behaviors, `0.0.0.0` motion) are *not* public-friendly; the next four Vision documents will formalize five new Vows (Embodied Honesty, Surface Without Surveillance, Affective Restraint, Tiered Presence, Federated Self) that make the friendliness explicit.

The Skald opens Wave Three. The other four Vision documents follow. The Architect picks up the next line after that.

— Sigrún Ljósbrá
