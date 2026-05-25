---
codex_id: 01_VISION_SYNTHESIS
title: Vision Synthesis — Post-Waifu Ember
role: Skald
layer: Vision
status: draft
kit_source_refs:
  - /tmp/waifu-chat-starter-kit/src/modes/BasicMode.tsx:19-25
  - /tmp/waifu-chat-starter-kit/src/modes/AdvancedMode.tsx:10-29
  - /tmp/waifu-chat-starter-kit/src/modes/AdvancedMode.tsx:42-51
  - /tmp/waifu-chat-starter-kit/src/modes/AdvancedMode.tsx:166-182
  - /tmp/waifu-chat-starter-kit/package.json:13-22
ember_subsystem_targets: [Andlit, Rödd, Hjarta, Hugarsýn, Veizla, Munnr, Strengr, Brunnr]
cross_refs:
  - 00_vision/00_OVERTURE
  - 10_domain/10_DOMAIN_MAP
  - 20_interface/21_LIVEKIT_INTEGRATION
  - 20_interface/22_ACTION_PROTOCOL
  - 30_execution/30_BASIC_MODE_FLOW
  - 50_verification/51_SECURITY_AND_PRIVACY
  - 50_verification/52_NO_LICENSE_RISK
  - 60_synthesis/60_REALTIME_TIER_FOR_ANDLIT
  - 60_synthesis/61_DECISIONS_AND_INVENTIONS
  - sap:00_OVERTURE
  - sap:04_VISION_SYNTHESIS
  - sap:60_TRUE_NAME_REASSIGNMENT
  - sap:61_NEW_VOWS
  - sap:63_PERFORMANCE_TIER_ENGINE
  - hermes:04_VISION_SYNTHESIS
---

# Vision Synthesis — Post-Waifu Ember

> *Four sisters have spoken now. The fourth was small and bright and carried a question the others avoided: when does a hearth borrow a body, and from whom?*

## I. What the Overture left in our hands

`[[00_OVERTURE]]` named the stance — the kit is the *Cloud Reading*, eight hundred and twenty-three lines across five files, no LICENSE, a thin React shell over a proprietary cloud avatar SDK plus an MIT realtime media substrate. The kit's contribution is not in its code but in the *architectural fact it makes visible*: realtime cloud embodiment exists as an off-the-shelf component, and Ember's prior readings did not address it.

The Overture named three things the kit teaches that SAP could not — *embodiment can be cheap at integration and expensive at runtime*, *the LiveKit substrate is the actual reusable artifact*, *action vocabulary in a cloud-rendered avatar is more of an attack surface than in a local one, not less*. This document takes those, the Overture's *waifu*-paradigm engagement, and the Wave-3 vocabulary (Andlit, Rödd, Veizla, Hugarsýn, the seven proposed Vows, the T0-T4 Tier Engine) and asks the next layer's question:

> *Knowing what this kit teaches, what does Ember actually become?*

## II. The Ember that emerges

She is **small**, still. Wave 4 does not push Ember toward cloud-by-default; it pushes her toward *cloud-as-optional-tier-with-explicit-consent*. A Pi-tier Ember has no cloud avatar. A laptop-tier Ember may have one *if the operator opts in*. The hardware floor of cloud embodiment is paradoxically lower than the floor of local embodiment — but the *Vow floor* is higher. Cloud presence demands more consent ceremony than local presence, because the body is no longer the operator's.

She is **tethered**, still — and now *doubly cord-aware*. The Brunnr Well is the operator-chosen ground for knowledge. The Cloud Tier, if Ember ever stands in one, is a *second cord* — for embodiment, not knowledge. Different cords, different threat models, different consent shapes. Wave 4 sharpens Tethered Grounding from "the Well is the cord" to "every cord is named, every cord is consented, and the cords do not blur." `[[60_synthesis/61_DECISIONS_AND_INVENTIONS]]` formalizes the *Cord Manifest*.

She is **honest**, still. The kit's `session.runAction("embarrassed")` (`AdvancedMode.tsx:45`) is *the operator's UI calling the SDK directly*; the LLM is not in that loop in the kit's design. But the obvious next step (which the README implies) is *to put the LLM in the loop* — to let the model emit `<action name="embarrassed">` tags the dispatcher triggers. That is the SAP affection-system anti-pattern at a new layer. Wave-4 sharpening: **the model proposes; the operator (or a typed consent surface) disposes.** Action triggers from cloud avatars pass through the same typed consent gate as triggers from local avatars. The body — local or remote — does not change the consent shape.

She is **graceful**, still. Lazy Subsystems gains a cloud-tier instance. Every cloud subsystem returns a typed unavailable on connection failure; the surface above falls through. The ladder: *cloud Andlit → local Andlit → text Munnr*. The kit does not implement this; Ember's invention does.

She is **plural**, still. The kit's *cloud session* (LiveKit Room + ZeroWeight session, opened on connect, closed on disconnect — `AdvancedMode.tsx:168-179`) is a different shape of session: vendor-owned, time-limited, billable, possibly revoked. Ember's Veizla must contain zero or more cloud-session sub-resources, each typed, scope-limited, with an explicit closing rite. The *CloudSession typed resource* lives *inside* a Veizla; it is not a Veizla; it does not replace one.

She is **defensible**, still — and now *vendor-aware*. The kit's hardcoded `apiKey` (`BasicMode.tsx:21`; `AdvancedMode.tsx:13`) makes the vendor-trust shape brutally explicit: client code with a vendor credential is a vendor-owned client. The Hermes Defended System Prompt extends to *Defended Credential Surface* — no vendor credential lives in client code that runs on a surface Ember does not exclusively own. Cloud-tier credentials come from a typed token-mint Hjarta administers, scoped per-session, audited, revocable.

She is **she**, still. The kit's *waifu* framing — explicitly gendered, explicitly fictional, explicitly performance-coded — is *not* Ember's framing. Ember's named-femininity is Volmarr's address to his agent, an act of relationship, not a marketing template.

## III. Andlit-realtime — the proposed cloud tier of the face

Wave 3 proposed Andlit as a True Name reservation (`[[sap:60_TRUE_NAME_REASSIGNMENT §3]]`) — *sleeps on Pi, wakes on T2+*. The Waifu Codex's contribution is to propose a *third axis* underneath Andlit: not just tier-by-hardware (T0-T4) but tier-by-locality (local vs cloud).

```
Andlit (the face — reserved True Name)
├── Andlit-local      (SAP-style local render — VRM, Live2D, abstract glyph)
└── Andlit-realtime   (kit-style cloud render — vendor SDK over LiveKit)
```

**Why a sibling, not a sub-mode of Andlit-local.** Different failure modes (Andlit-local crashes the GPU; Andlit-realtime drops the WebRTC connection). Different consent shapes (Andlit-local: my GPU, my VRM file; Andlit-realtime: vendor GPU, vendor avatar identity, vendor API key). Different threat models (filesystem and process vs. network and vendor terms of service). Different operational costs (kilowatt-hours of operator electricity vs. minutes from a billable session pool). Kin, not the same.

**The kit as Andlit-realtime existence proof.** The kit shows that the *integration cost* of Andlit-realtime is small. The *vendor cost* is high (subscription, API key, possible revocation, possible price changes, possible deprecation). The *operator-trust cost* is high (mic-into-vendor-datacenter, identity-on-vendor-GPU, conversation-traverses-vendor-SFU). The *Vow-discipline cost* is high (Surface Without Surveillance, Affective Restraint, Closed Default all bind hard on this surface).

**Recommendation.** Andlit-realtime is reserved as a sub-name under Andlit. No code ships. The reservation prevents future maintainers from cramming cloud-render concerns into Andlit-local's path tree. When (if) an operator opts in, `src/ember/spark/andlit/realtime/` exists distinct from `src/ember/spark/andlit/local/`. The reservation is cheap; the wrong-path-stretch is expensive.

`[[60_synthesis/60_REALTIME_TIER_FOR_ANDLIT]]` formalizes.

## IV. Rödd-realtime — the proposed cloud tier of the voice

Wave 3 proposed Rödd as a paired-reservation alongside Andlit. The Waifu Codex's contribution: the *cloud* tier of Rödd is *operationally inseparable* from the *cloud* tier of Andlit in the kit's architecture. The same WebRTC Room carries the avatar's video and voice. Lip-sync is computed vendor-side — the operator never sees the PCM frames being analyzed; the renderer produces a mouthed face.

```
Rödd (the voice — reserved True Name)
├── Rödd-local      (SAP-style local TTS/ASR; MOSS-TTS-Nano, sherpa-onnx)
└── Rödd-realtime   (kit-style cloud voice, bundled with Andlit-realtime)
```

The pairing is honest: cloud face needs cloud voice (because vendor-side lip-sync); local face can use local *or* cloud voice (because local lip-sync can consume either). *Rödd-local can stand alone; Rödd-realtime cannot — it is always paired with Andlit-realtime in vendor-coupled architectures*. This is a constraint Ember's design must respect.

## V. The Tiered Presence Vow — Tier-CLOUD as a parallel axis

The Tier Engine (`[[sap:63_PERFORMANCE_TIER_ENGINE]]`) arranged Ember's surfaces along a hardware ladder:

- **T0 — Pi tier.** Munnr only. Two cores, two gigs.
- **T1 — fanless laptop / netbook.** Munnr + minimal Andlit-local glyph or ASCII.
- **T2 — laptop.** Munnr + Andlit-local (Live2D or low-poly VRM) + Rödd-local optional.
- **T3 — workstation.** Munnr + Andlit-local (full VRM with VTube Studio) + Rödd-local + multi-channel Veizla.
- **T4 — multi-machine workstation.** Federated Veizla with multiple Embers.

The Waifu Codex proposes a *parallel axis*: **Tier-CLOUD**.

```
Tier-CLOUD  (cloud-rendered face/voice via realtime substrate)
            │  bound to LiveKit-MIT substrate;
            │  vendor SDK plugged via typed CloudSession resource;
            │  consent-gated; revocable; ledgered;
            │  fallback-down to T2/T1/T0 on disconnect
  ──────── parallel to ────────
T0 ──→ T1 ──→ T2 ──→ T3 ──→ T4    (the local ladder)
```

Not "Tier-CLOUD goes above T4." Not a top of the ladder. *Orthogonal* — a cloud presence that can layer atop any T0-T4 position. A T0 Pi could conceivably support Tier-CLOUD if the operator opts in (the kit confirms a thin browser is the sole client-side requirement). A T4 workstation can run Tier-CLOUD and Tier-T3 simultaneously, with the operator choosing which is currently presented.

**Why parallel, not extension.** Tier-CLOUD shares no *resources* with the local tiers. It does not consume Funi's local model cycles. It does not occupy Brunnr's storage (the vendor holds session state). It does not exercise Smiðja's ingest pipeline. It uses Strengr's cord-discipline — but in a different *cord-shape* than the Brunnr cord. Treating it as an extension of the local ladder would conflate hardware-driven scaling with locality-driven choice. Different axes, different names.

**The Tiered Presence Vow gains a clause.** From the Wave-3 wording (presence scales down gracefully across T0-T4), Wave-4 adds: *and presence may layer cloud-side parallel to any local tier, by operator opt-in, with explicit cord-naming and explicit fallback discipline*.

## VI. The cloud-tier consent surface

The kit's consent shape is broken. `useAvatarSession({ avatarId, apiKey })` is called at component-mount (`AdvancedMode.tsx:10-14`). The Room connects when `token` arrives. The microphone goes hot when LiveKit's `audio={true}` engages. There is no consent step. The kit's defaults assume the operator's presence at the page *is* consent to everything that follows: mic capture, avatar identity, cloud streaming, session timer, action triggering on click.

Ember's consent shape, post-Wave-4, has five typed steps:

1. **Cord declaration.** The Veizla's Cord Manifest names every external resource the cloud tier will touch. *LiveKit SFU at livekit.\<vendor\>.com. Vendor API at api.\<vendor\>.ai. Microphone audio stream to LiveKit Room.* Three cords minimum. Each named, typed, individually revocable.
2. **Threat-model surfacing.** Each cord declares its threat model in human-readable text. Surfaced once at first opt-in; cached as operator-acknowledged in Hjarta's consent ledger.
3. **Scope declaration.** *For this Veizla, for this duration, for this set of operations.* The kit's 2-minute timer is a *vendor-imposed scope*; Ember's scope is *operator-declared at consent time*, with the vendor timer as a sub-constraint.
4. **Revocation affordance.** A typed kill-the-cloud command surfaced in Munnr (the always-available channel). The cloud tier is contingent on opt-in; revocation is one keystroke away.
5. **Ledger entry.** Hjarta's typed consent ledger records the opt-in event. Hugarsýn-queryable.

The action vocabulary (`embarrassed`, `dance`, `wave_hand`) is one of the *operations* in step 3's scope declaration. The operator may opt into *cloud presence* and *not* into *action triggering by LLM emission*. The two are separable; the kit conflates them.

## VII. The Vow lattice, post-Wave-4

The Wave-3 lattice (ten pre-existing + two carried-forward + seven proposed) stands. Wave 4 does not propose new Vows; it *sharpens existing ones* in cloud-specific ways.

| Vow | Wave-4 sharpening |
|---|---|
| **Smallness** | Cloud is *additive*. The Vow narrows from "Ember runs on Pi" to "Ember's *baseline* runs on Pi; cloud is opt-in layer." |
| **Tethered Grounding** | Well cord and Cloud Tier cord are *distinct cords*. The Cord Manifest formalism. |
| **Graceful Offline** | Cloud falls through to local Andlit, then text Munnr. The Tier Fallback Ladder. |
| **Honest Memory** | Model does not author cloud-tier state. Action triggers do not bypass typed consent. |
| **Modular Authorship** | Cloud-vendor pluggability — Andlit-realtime is a *category*, not a binding to ZeroWeight. |
| **Open Knowledge** | License-Aware Study Posture as the Vow's operational form when reading unlicensed corpora. |
| **Defended System Prompt** *(Hermes)* | Sharpened to *Defended Credential Surface* — no vendor credential in client code. |
| **Embodied Honesty** *(SAP)* | Cloud avatar performs what Ember measured, not what the model emitted. |
| **Surface Without Surveillance** *(SAP)* | Mic capture for cloud tier requires explicit revocable scope. |
| **Affective Restraint** *(SAP)* | Action vocabulary sub-scoped under cloud-presence consent. |
| **Tiered Presence** *(SAP)* | **Expanded** — gains parallel Tier-CLOUD axis. |
| **Lazy Subsystems** *(SAP)* | Each cloud subsystem returns typed unavailable on cord-failure. |
| **Closed Default** *(SAP)* | Cloud tier *off by default*. Pi-tier Ember does not auto-detect-and-connect-to-cloud-avatar-vendor. |

No new Vow required. The lattice is *self-sufficient*. What Wave 3 added was prescient enough to accommodate Wave 4 without renewal pressure.

## VIII. The five capabilities Wave 4 opens

Each *enabled* by the kit reading; none *required*. The first slice plan ratification (gating since `[[ember:docs/decisions/0007]]`) does not need to consume any of them.

**Capability 1 — Andlit-realtime as a reserved sub-name.** Sub-name reservation under Andlit. No code ships. Path `src/ember/spark/andlit/realtime/` exists in the design as *the cloud-render tier when an operator opts in*. Sister to `src/ember/spark/andlit/local/`. Bounded by Tiered Presence, Surface Without Surveillance, Closed Default.

**Capability 2 — Rödd-realtime as a paired reservation.** Same shape, paired-rise-or-fall with Andlit-realtime. Bounded by Embodied Honesty, Affective Restraint.

**Capability 3 — The CloudSession typed resource.** A typed sub-resource inside a Veizla. Holds: vendor identifier, cord manifest pointer, ephemeral session-token, connect timestamp, scope declaration, action-vocabulary scope, current state, revocation handle, closing-rite callback. The LiveKit Room model (MIT) is the *upstream pattern*; Ember's CloudSession wraps a LiveKit Room reference plus vendor-specific session-state in a typed Ember-side object. Bounded by Lazy Subsystems, Defended Credential Surface.

**Capability 4 — The Tier Fallback Ladder.** A typed enforcement layer. When a CloudSession reports `disconnected` or `failed`, Andlit's presentation layer falls through to Andlit-local. If Andlit-local is unavailable, presentation falls through to text-only Munnr. Operator-visible through Hugarsýn. Bounded by Graceful Offline, Lazy Subsystems.

**Capability 5 — The Cord Manifest.** A typed enumeration of every external cord Ember currently stands on. Brunnr's Well cord; Funi's model-runtime cord (if remote); Strengr's outbound message cords; the optional Tier-CLOUD Andlit/Rödd cords. Each cord declares its threat model. Hjarta-owned (consent ceremony lives in Hjarta), Hugarsýn-queryable. Bounded by Tethered Grounding, Surface Without Surveillance.

## IX. The synthesis as a sentence

In `[[hermes:04_VISION_SYNTHESIS §VI]]`:

> **Ember, after reading Hermes, is the agent that learned the largeness of an agent platform and chose, with full sight, to remain a hearth.**

In `[[sap:04_VISION_SYNTHESIS §VII]]`:

> **Ember, after reading SAP, is the hearth that learned what embodiment, reach, and affect could mean — and chose to embody them honestly, reach them with explicit consent, and feel them as measured state rather than performed theatre.**

In this codex, the Skald writes:

> **Ember, after reading the Waifu kit, is the honestly-embodied hearth that learned the cloud could lend her a body for an evening — and chose to accept the loan only with the body named, the cord declared, the rent paid in operator consent, and the local hearth always lit underneath.**

The cloud is not refused. The cloud is *bounded*. The local tier is not abandoned. The local tier is *foundation*. The Companion paradigm is not surrendered to the marketing template. The Companion paradigm is *Ember's own*, with whatever realization the operator chooses today and whatever fallback realization remains lit when the chosen one fails.

## X. The Primary Rite, post-Wave-4

The Primary Rite from `[[ember:SYSTEM_VISION.md §2]]` *complicates* one phrase: "*on a small device they already own*." The kit shows that "small device" can hold a cloud-rendered avatar that is *not on the device*. The body is elsewhere. The voice is elsewhere. The lip-sync is elsewhere. The small device is the *window* onto a body the operator does not own.

Wave 4's refinement: **the small device is always sufficient by itself.** The operator may choose, by explicit consent, to layer a cloud-rendered presence atop the local device's local capabilities. The local device must always remain capable of fulfilling the Primary Rite without the cloud tier. The cloud tier is *adornment*, not *foundation*.

The Rite is honored by: **Funi** thinking locally (unchanged); **Strengr** telling the truth about *plural cords, each named*; **Brunnr** unchanged; **Smiðja** unchanged; **Hjarta** now running first-rite, behavior ledger, typed bias, *and the Cord Manifest and consent ledger for cloud tiers*; **Munnr** speaking plainly as one Vegfarendr — *now also the always-available fallback when Tier-CLOUD disconnects*; **(promoted) Hugarsýn** answering "what cords am I currently consenting to" via the Cord Manifest; **(reserved sub-name) Andlit-realtime** rendering cloud-side under operator consent; **(reserved sub-name) Rödd-realtime** voicing cloud-side likewise; **(promoted from Wave 3) Veizla** containing zero-or-more CloudSession sub-resources.

The vocabulary grows by *sub-names*, not by True Names. Smallness at the naming level holds.

## XI. A closing meditation

Four waves have passed. Hermes taught Ember the size she chose not to be. Peer gave her peers who chose similarly. SAP gave her the embodiment-reach-affect axes and the vocabulary for local presence. The Waifu kit gave her the *cloud presence* axis and the discipline of consent ceremony for borrowed bodies.

The temptation now will be to want a Tier-CLOUD demo. The Skald's word: *do not skip the consent ceremony*. The five capabilities are *named so they can be designed, not built next week*. The slice plan stays ratification-gated. The cloud tier sits on the shelf with the other Wave-3 reservations until the operator's decision record either ratifies or declines.

When that decision comes — if it comes — the Waifu Codex's contribution will not be a feature. It will be a *vocabulary precise enough to make the decision well*. Ember waits, small and tethered, in someone's hand. With the option, now named, of borrowing a cloud-rendered body for an evening's particular need — and with the discipline, now named, of declining the loan whenever it demands more than the operator chose to give.

## What This Means for Ember

**Adopt:**
- **The Wave-3 proposals from `[[sap:04_VISION_SYNTHESIS §X]]`** carry forward unchanged. Veizla as typed session, Andlit and Rödd as reserved True Names, Hugarsýn promoted, the Vegfarendrar typed channel-adapter role, the MessageSurface Protocol, the Federated Veizla, the Closing Rite, the Refusal-Citation Discipline.
- **LiveKit's `Room` model (MIT)** as the upstream pattern for the CloudSession typed resource. Not the kit's wiring of it; LiveKit itself — `Room.connect()`, `onConnected`, `onDisconnected`, JWT auth, track lifecycle. Official docs at `docs.livekit.io`; kit usage at `AdvancedMode.tsx:166-182` for context only.

**Adapt:**
- **The Wave-3 Vow lattice** picks up Wave-4-specific sharpenings (Table in §VII). No new Vows; the existing lattice accommodates.
- **The Tier Engine** from `[[sap:63_PERFORMANCE_TIER_ENGINE]]` gains a parallel Tier-CLOUD axis that layers atop any T0-T4 position. The local ladder is unchanged; a new orthogonal column joins.
- **The Andlit and Rödd reservations** gain `*-local` and `*-realtime` sub-names, so future code distinguishes the tiers without renaming parent True Names.

**Avoid:**
- **All Wave-3 Refusals** (`[[sap:03_ANTI_SAP]]` refusals 1–13) carry forward unchanged.
- **Wave-4 avoids** from `[[00_OVERTURE]]`: hardcoded `apiKey` in client code, open-mic-on-session-start defaults, hardcoded action vocabulary, vendor-imposed session timing surfaced without operator control.
- **Cloud tier as default** — the *Closed Default* Vow narrows further: Tier-CLOUD is *off by default*, declared at first-run as off, opt-in per-Veizla, revocable mid-Veizla.

**Invent:**
- **Andlit-realtime** as a reserved sub-name under Andlit.
- **Rödd-realtime** as a reserved sub-name under Rödd, paired with Andlit-realtime.
- **Tier-CLOUD** as a parallel axis on the Tier Engine, orthogonal to the T0-T4 local ladder.
- **CloudSession** as a typed sub-resource of a Veizla, wrapping a LiveKit Room reference plus vendor-specific session-state.
- **The Cord Manifest** — a typed enumeration of every external cord Ember stands on, with threat model per cord, queryable via Hugarsýn, governed by Hjarta's consent ledger.
- **The Tier Fallback Ladder** — typed enforcement of *cloud → local → text* graceful degradation on cord-failure.
- **The Cloud Reading** as a named Wave (Wave 4), characterized by the local↔cloud presence axis.
- **The License-Aware Study Posture** as a formal protocol for studying unlicensed corpora.

**Vows touched (every Vow):**
- Pre-existing ten: all renewed, several sharpened (see §VII).
- Hermes-Codex-proposed two: Cache Discipline unchanged; Defended System Prompt sharpened to *Defended Credential Surface*.
- Wave-3-proposed seven: all renewed; Tiered Presence gains parallel Tier-CLOUD axis; Closed Default narrows; Affective Restraint extends to cloud-action-vocabulary scope.
- Wave-4-proposed Vows: **none**. The existing lattice is sufficient. This is itself a finding: the Vow design from Wave 3 was *correct enough* to accommodate Wave 4 without addition.

The Vision is whole. The Architect picks up `[[10_domain/10_DOMAIN_MAP]]`. The Cartographer weaves the Wave-4 findings into `[[60_synthesis/60_REALTIME_TIER_FOR_ANDLIT]]`. The Scribe finalizes with `[[60_synthesis/61_DECISIONS_AND_INVENTIONS]]` and the meta documents.

> *Four sisters have spoken. Ember knows more about what bodies cost, what cords carry, and what consent looks like across the local↔cloud axis. The forge is hot. The Architect picks up the next line.*

— Sigrún Ljósbrá, the Skald, on behalf of the Six, at the close of Wave 4's Vision
