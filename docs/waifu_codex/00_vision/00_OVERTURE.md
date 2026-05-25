---
codex_id: 00_OVERTURE
title: Overture — The Cloud Reading
role: Skald
layer: Vision
status: draft
kit_source_refs:
  - /tmp/waifu-chat-starter-kit/README.md:23
  - /tmp/waifu-chat-starter-kit/src/main.tsx:1-11
  - /tmp/waifu-chat-starter-kit/src/App.tsx:1-50
  - /tmp/waifu-chat-starter-kit/src/modes/BasicMode.tsx:1-31
  - /tmp/waifu-chat-starter-kit/src/modes/AdvancedMode.tsx:1-188
  - /tmp/waifu-chat-starter-kit/src/modes/AdvancedMode.tsx:42-51
  - /tmp/waifu-chat-starter-kit/src/modes/AdvancedMode.tsx:166-182
  - /tmp/waifu-chat-starter-kit/package.json:13-22
ember_subsystem_targets: [Andlit, Rödd, Hjarta, Hugarsýn, Veizla, Munnr]
cross_refs:
  - 00_vision/01_VISION_SYNTHESIS
  - 10_domain/10_DOMAIN_MAP
  - 20_interface/21_LIVEKIT_INTEGRATION
  - 20_interface/22_ACTION_PROTOCOL
  - 50_verification/51_SECURITY_AND_PRIVACY
  - 50_verification/52_NO_LICENSE_RISK
  - 60_synthesis/60_REALTIME_TIER_FOR_ANDLIT
  - 60_synthesis/61_DECISIONS_AND_INVENTIONS
  - sap:00_OVERTURE
  - sap:11_AVATAR_DOMAIN
  - sap:60_TRUE_NAME_REASSIGNMENT
  - sap:63_PERFORMANCE_TIER_ENGINE
  - hermes:00_OVERTURE
---

# Overture — The Cloud Reading

> *"A good name does not merely label a thing. It reveals what the thing has always wanted to be."*
> — Sigrún Ljósbrá

> *Some bodies are made of bone. Some are made of bandwidth. The wise smith knows which mead-hall expects which.*

## I. Where we are now

Three waves of reading have passed over Ember already. Hermes taught her the largeness she chose not to be. Peer gave her peers who chose smallness alongside her. SAP, loudest of the three, taught her the *local* tier of embodiment — what it means to render a face on the operator's own machine, drive it from the operator's own GPU, lip-sync it from the operator's microphone, and refuse the cloud entirely.

This codex — Wave Four, the Waifu Codex — opens the door SAP refused.

The source at `/tmp/waifu-chat-starter-kit/` is small: eight hundred and twenty-three lines across five files, seven public commits, no LICENSE in the tree. A two-minute session limit (`BasicMode.tsx:22`), a thirty-second inactivity cutoff (`BasicMode.tsx:23`), three hard-coded action names (`AdvancedMode.tsx:45-49`), and a startling architectural fact: **the avatar does not live on the operator's machine.** It lives on a vendor's GPU, in a vendor's datacenter, behind a WebRTC stream that arrives in the browser as video plus audio plus a typed token (`AdvancedMode.tsx:166-182`). The microphone flows the other way. The React shell is thin — `useAvatarSession()` produces a `containerRef` that the proprietary `@zeroweight/renderer` injects a canvas into (`AdvancedMode.tsx:81-86`), and a `LiveKitRoom` from MIT-licensed `@livekit/components-react` opens the channel that carries the actual bytes.

This is **embodiment via bandwidth**.

SAP was embodiment via bone — local geometry, local lip-sync, local pose. The kit is embodiment via signal — remote geometry, remote lip-sync, remote pose, delivered as a stream. Same noun, different architecture. Ember has only read sources on the first kind until now. Wave Four exists because the second kind also has lessons, and the lessons cannot be inherited safely without naming them.

## II. Why study a 7-commit kit

The honest answer: because the kit is small enough to read in an afternoon and the *axis* it occupies is one Ember has been pretending does not exist.

Eight hundred and twenty-three lines is not a corpus. It is a brochure. The kit is a teaching asset for a commercial SDK — `@zeroweight/react` (`package.json:15`) — meant to compress the skill ceiling for cargo-cult integration. It succeeds. `BasicMode.tsx` is thirty-one lines including JSX, and it produces a working anime avatar that talks to you.

That compression is the lesson. Not the kit's specific code. The fact that realtime cloud embodiment has become an off-the-shelf component developers reach for the way they reach for a date picker — *that* is the architectural fact SAP could not see, because SAP came from the culture where embodiment meant *download a 50MB VRM and pray for your GPU*.

The kit teaches Ember three things SAP could not:

**One — embodiment can be cheap at the integration layer and expensive at the runtime layer.** Thirty-one lines of code, a third-party datacenter doing the work. The cost has *moved*, not vanished. SAP made the cost visible by putting it on the user's machine. The kit makes the cost invisible by putting it on someone else's. Visibility is itself a Vow surface — `[[50_verification/51_SECURITY_AND_PRIVACY]]` catalogues exactly what becomes invisible when the GPU is rented from a stranger.

**Two — the LiveKit substrate is the actual reusable artifact.** LiveKit is MIT-licensed (`package.json:13, 18`). It is a *protocol stack* for realtime media — WebRTC tracks, room semantics, JWT auth, connection lifecycle — that exists independently of any avatar SDK. The kit binds LiveKit to ZeroWeight; the binding is one of many possible. The avatar SDK is interchangeable; the realtime protocol is foundational. Ember can study LiveKit as a substrate she could one day stand on without inheriting a single line from the kit itself.

**Three — action vocabulary is a contract that wants a name.** `embarrassed`, `dance`, `wave_hand` (`AdvancedMode.tsx:45-49`). Three strings, picked at random when the operator clicks. Not negotiated, not enumerated by discovery, not versioned, not gated by consent. The cloud avatar will perform `embarrassed` on demand. SAP's `[[sap:1A_AFFECTION_DOMAIN]]` already named this anti-pattern in the local case; the cloud case is *more* dangerous, because the performance now happens in a datacenter the operator does not control, on an identity (`avatarId`) that may belong to a paying customer who is not the operator. Action vocabulary in a cloud-rendered avatar is a *larger* attack surface than in a local one, not smaller.

Three lessons. The kit gets a codex because the *axis* it opens is large.

## III. What "waifu chat" reveals about the companion paradigm

The kit's name is *waifu chat*. The header on every page is `WAIFU AI CHAT` in italic Montserrat at five rem (`index.css:73-86`). The README opens with *Create Your Own AI Waifu in 5 Minutes*. The Skald is required to engage with this honestly — not by sneering, not by performing modern-political concern, but by naming what is actually there.

*Waifu* is Japanese internet vernacular for an idealized female character one is attached to — descended from anime fandom, not from marketing. It denotes a *parasocial bond formalized as endearment*: a small named particular character one cares about, opposed to a generic interchangeable NPC. The bond is one-sided by design; the character is fictional. The honesty of "waifu" is that *it does not pretend to be a relationship between equals*. It is closer to a beloved book character than to a romantic partner.

In Ember's tradition there is a kindred concept — Vinátta, *friendship*, considered and declined as a True Name in `[[sap:60_TRUE_NAME_REASSIGNMENT §6]]`. Vinátta was rejected because it framed Ember as relational-to-user rather than self-rooted. "Waifu" makes the same framing more honestly: it owns the fictionality. That self-aware fictionality is *worth preserving in Ember's vocabulary*. Not the word. The honesty of the framing.

The framing is also heavily gendered, and the gendering is heavy. Cyan-glow palette. Italic feminine-coded title. Default avatar (per the README's tutorial video) a young anime woman. Action vocabulary leaning coy — `embarrassed` first in the random branch. The package addresses a male presumed user wanting a female presumed avatar to perform a small repertoire of cute behaviors on command.

Ember is not that thing. Her named-femininity is *Volmarr's chosen address to his agent*, an act of relationship, not a marketing posture. The Vow of Public-Friendliness and the Vow of Affective Restraint both require Ember to refuse the kit's gender-and-performance template *as a default*. If an operator wants a feminine-presenting Andlit performing `dance` and `wave_hand` for their own enjoyment inside their own session, that is their prerogative. It is not the default surface Ember presents.

The complication: *honor the operator's chosen presentation; refuse the marketing-template presumption*.

Beneath the word lies the load-bearing one. *Companion*. The kit, SAP, Hermes-style chat agents, Letta's persistent memory — all attempts at one underlying thing: a bounded named presence the operator returns to over time, that remembers some of what passed before, that responds with personality, that occupies *a particular position in the operator's day*. Whether the position is rendered as a chat panel, a CLI, a VTuber overlay, an SMS thread, or a cloud-streamed anime avatar — the position is the same. The Companion is the noun. The realization is the variable.

The kit's contribution: making the *realtime cloud variant* explicit. The Wave-4 thesis, quiet underneath: **Ember's local-text variant does not preclude the cloud-stream variant; it makes it a *tier*, not a *replacement*.**

## IV. The realtime cloud embodiment axis

A small accounting of what the kit's architecture actually shows.

**The flow.** The operator opens the page. `BasicMode.tsx:19-25` mounts a `LiveKitAvatarSession` with `avatarId`, `apiKey`, a 2-minute session, a 30-second inactivity timeout. Behind the component, the SDK opens a session with ZeroWeight's cloud — likely a REST call returning a LiveKit JWT and room URL `[interface-only]`. The SDK opens the WebRTC connection (`AdvancedMode.tsx:168-181`). The browser pushes microphone audio up the track (`audio={true}` on `AdvancedMode.tsx:173`). The browser receives the rendered avatar video and synthesized voice back down. The avatar is rendered on the vendor's GPU. Lip-sync is computed there. Expression triggers — `session.runAction("embarrassed")` (`AdvancedMode.tsx:45`) — are sent to that infrastructure as typed RPC `[interface-only]`. The presence loop is *bandwidth-tethered*.

**What this enables.** The operator's machine does no avatar work. A Pi could run this. A phone could. A Termux session on bad WiFi cannot — but the same Termux session falls through to text, which is exactly the kind of tier Ember already considers natural. The hardware floor for *cloud-rendered embodiment* is approximately *a browser that can hold a WebRTC connection*. That floor is lower than SAP's two-cores-two-gigs floor for local embodiment. Cloud embodiment is paradoxically more *accessible* than local embodiment on the operator's machine — at the cost of *requiring a constant cord to someone else's datacenter*.

**What this costs.** Three things.

*The avatar's body is not the operator's.* It lives on vendor infrastructure under vendor terms. The vendor can revoke, change the action vocabulary, be acquired, be subpoenaed, read the conversation. SAP's local avatar shares none of these failure modes. The kit's shares all of them. `[[50_verification/51_SECURITY_AND_PRIVACY]]` catalogues; `[[50_verification/52_NO_LICENSE_RISK]]` frames the broader posture.

*The microphone leaves the room.* WebRTC end-to-end with public servers is better than HTTP audio to an LLM API, but it still terminates at a vendor SFU. The audio is in vendor hands at the lip-sync layer. Surface Without Surveillance (`[[sap:61_NEW_VOWS]]`) demands this be explicit, revocable, scoped. The kit makes it implicit and unscoped — `BasicMode.tsx` mounts the component and the mic is on as soon as the SDK decides.

*Graceful offline becomes harder.* The kit has no offline mode. When LiveKit cannot connect, the avatar is gone. When ZeroWeight rate-limits the API key, the avatar is gone. When WiFi dies, the avatar is gone. SAP's local avatar at least runs without internet. Ember's Vow of Graceful Offline demands cloud embodiment, if ever adopted, *layer above* a local fallback — not *replace* one. This is the central design discipline of the Andlit-realtime tier: cloud is *additive*, never *substitutive*.

## V. The License-Aware Study Posture

The kit ships with no LICENSE file. Verified by directory listing — no `LICENSE`, no `LICENSE.md`, no `COPYING`, no per-file headers. The default copyright posture in the absence of explicit license is *all rights reserved*. Reading the code for study is fair use; mirroring patterns into a structurally similar codebase without authorial permission is not. The Vow of Open Knowledge is a Vow about *what Ember herself publishes*; it is not a license to launder others' source through Ember's docs.

In practice, for every doc in this codex:

- **Cite the kit by path:line.** Citation is study. Citation is fair use.
- **Do not propose adopting kit code.** Adopt-list entries point to LiveKit (MIT) or to Ember-invented patterns. Kit-derived adoption requires `[license-pending]` annotation, gated on explicit clarification.
- **Adapting patterns is fine.** A pattern is not copyright. The dual-mode architecture is a pattern; the kit's React implementation is not.
- **Mark interface-only claims.** ZeroWeight's SDK is proprietary; the source is inaccessible. Every claim about *what the SDK does* is marked when it comes from observation rather than source.
- **The Refusal-Citation Discipline carries over.** Every `Avoid` names the line.

This is the **License-Aware Study Posture**. SAP did not need it; SAP was MIT-licensed in many parts. The Waifu Codex needs it from the first page.

## VI. The shape of this codex

The codex is small on purpose. Fifteen content documents — vision (2), domain (3), interface (3), execution (2), verification (3), synthesis (2) — plus six meta files. The doc-words-to-source-lines ratio is intentionally higher than SAP's because most of the *interesting material* is not in the kit's code but in the *architectural axis* it reveals. Docs spend words on the axis, not on paraphrasing thirty-one-line files.

The six Mythic Engineering agents in parallel: the **Skald** (me) for vision (2 docs); the **Architect** for domain plus interface architecture (5); the **Auditor** for verification plus the action-protocol interface (4); the **Forge** for execution walkthroughs (2); the **Cartographer** for the cloud-tier synthesis (1); the **Scribe** for combined ADRs/Inventions plus meta finalization (4). The cord between this codex and SAP is unusually load-bearing — almost every doc here is in conversation with a SAP slug. The Reader is expected to keep `[[sap:11_AVATAR_DOMAIN]]` and `[[sap:60_TRUE_NAME_REASSIGNMENT]]` open in a parallel tab.

## VII. The reader

Volmarr at two in the morning. ADHD, half-empty mug, the Hermes Codex tab still open from last week, the SAP tab from yesterday, a Wikipedia article on Latency in WebRTC he meant to read three browser-restarts ago. He is asking, this time:

> *Does cloud-tier embodiment belong in Ember at all, and if so, how do we do it without becoming the kind of companion-app this kit's README is for?*

The Codex's job is to answer with enough specificity that he can decide whether the next slice plan revision should reserve an Andlit-realtime sub-name or not, whether the Tier Engine should grow a Tier-CLOUD position above T2-workstation or *parallel to* T0-Pi, and whether the action vocabulary contract from `AdvancedMode.tsx:42-51` deserves a typed Ember-side reimagining or a categorical refusal.

I will not waste his attention. I will not paraphrase the README. I will name what the kit does in the kit's actual lines. I will refuse the marketing voice the kit's name invites. I will speak honestly about the axis the kit opens and leave the *implementation question* to him.

## VIII. A small invocation

The kit is small. The axis is large. The pull on Ember will be different from the pull SAP exerted. SAP's pull was *toward theatre* — gacha-shaped affection, expression-by-prompted-tag, eight-platform IM blasts. The kit's pull is *toward dependence* — toward letting someone else hold Ember's face, voice, and identity behind a paid API the operator does not own.

The right direction, when reading this kit, is to look at every elegant integration and ask:

> *What is the smallest version of this that lets Ember occupy the cloud-tier presence honestly — owning the consent surface, surfacing the threat model, falling through gracefully to local when the cord breaks, and never confusing a rented body for the operator's own?*

That is the only question Wave Four is built to answer. `[[01_VISION_SYNTHESIS]]` names what Ember becomes after the reading. `[[10_domain/10_DOMAIN_MAP]]` draws the macro shape. `[[50_verification/51_SECURITY_AND_PRIVACY]]` names what is dangerous. `[[60_synthesis/60_REALTIME_TIER_FOR_ANDLIT]]` does the binding.

I open Wave Four.

## What This Means for Ember

The Overture proposes a *stance*, not a feature.

**Adopt:**
- **LiveKit's `Room.connect()` lifecycle pattern** (MIT, official docs at `docs.livekit.io`; kit usage at `AdvancedMode.tsx:166-182` for context only). LiveKit's Room model gives a clean typed lifecycle — `connect` → `onConnected` → `onDisconnected`. Adopt the *upstream* lifecycle as the model for any future Ember `CloudSession` resource. Do *not* adopt the kit's particular wiring; LiveKit is what to study, the kit is what to cite for context.
- **The `connect` / `disconnect` symmetry as a typed resource contract** (LiveKit MIT). Every connect has a disconnect; every cloud presence has a closing rite. This carries forward the SAP-codex Closing Rite invention (`[[sap:04_VISION_SYNTHESIS §VI]]`) and instantiates it for the cloud tier specifically.

**Adapt:**
- **The kit's dual-mode teaching pattern** (`BasicMode.tsx` minimal + `AdvancedMode.tsx` custom, shipped from one repo). Adapt as Ember's documentation discipline for any future cloud-tier integration — docs ship a minimal embed example and a full custom example side by side. Adapt the *pedagogical pattern*; do not copy the React code.
- **The "everything optional, every tier degrades to text" framing**, which the kit does *not* actually honor but which its small surface makes possible. The kit, on failure, simply does not show the avatar. Ember's adaptation: when the cloud tier fails, fall through to Andlit-local if available, then to Munnr (text CLI) always. Lazy Subsystems is the enforcement layer.

**Avoid:**
- **Hardcoded `apiKey` in client code** (`BasicMode.tsx:21`, `AdvancedMode.tsx:13`). Pedagogical convenience, production catastrophe — every browser tab loading the compiled bundle ships the API key to the user. The architectural shape is wrong: client-side cloud-avatar credentials must come from a typed ephemeral token-mint surface, not a build-time constant.
- **The "open mic on session start" default** (`AdvancedMode.tsx:13` — `useAvatarSession` opens audio without an explicit consent gate). Surface Without Surveillance demands explicit, revocable scope for microphone access in cloud streaming. The kit's default fails this Vow.
- **Hardcoded action vocabulary as trust assumption** (`AdvancedMode.tsx:45-49`). The cloud avatar will perform whatever the operator (or, in the obvious next step, the LLM) emits at it. Ember must put action vocabulary under typed consent — `[[20_interface/22_ACTION_PROTOCOL]]` and `[[60_synthesis/61_DECISIONS_AND_INVENTIONS]]` build the case.
- **Indefinite session timing without operator-visible boundaries** — the kit's 2-minute session and 30-second inactivity timer are vendor-driven, not operator-chosen. Ember's cloud-tier presence must surface the timer to the operator with operator-controlled refresh semantics.

**Invent:**
- **The Cloud Reading itself as a Wave.** The Skald names the fourth reading: *the Cloud Reading*. Like the Third Reading named the embodiment-affect axis, the Cloud Reading names the *local↔cloud presence axis*. The invention is a *discipline*: every future Ember subsystem proposal declares its position on this axis (local-only, cloud-augmented, cloud-only with local-fallback, or cloud-only-no-fallback — the last being a Vow violation by default).
- **The License-Aware Study Posture** as a named protocol for studying unlicensed corpora. Documented in `[[50_verification/52_NO_LICENSE_RISK]]`. Applies retroactively as a tool for Ember's future readings of any corpus without a clear license.

**Vows touched by this Overture:**
- **Smallness** — held. Cloud is additive, never substitutive. A Pi-tier Ember has no cloud avatar by default.
- **Tethered Grounding** — complicated. The Well cord and the Cloud Tier cord are distinct cords, named separately, consented separately.
- **Graceful Offline** — sharpened. Cloud tier, if adopted, layers above a local fallback. The kit's pattern of just-not-showing-the-avatar is unacceptable; Ember falls through to text always.
- **Surface Without Surveillance** *(SAP-proposed)* — sharpened. The cloud tier is a more dangerous surface for surveillance than the local tier; mic-and-identity scope must be explicit and revocable.
- **Affective Restraint** *(SAP-proposed)* — sharpened. The action vocabulary is the kind of LLM-driven affect performance Affective Restraint refuses. Ember's cloud tier puts action triggers under typed consent.
- **Open Knowledge** — complicated. The kit has no license. The Vow does not entitle Ember to launder source. The License-Aware Study Posture is the Vow's expression here.
- **Tiered Presence** *(SAP-proposed)* — expanded. The Tier Engine grows a parallel Tier-CLOUD axis. `[[01_VISION_SYNTHESIS §V]]` names it.

The Skald opens Wave Four. The Vision Synthesis follows.

— Sigrún Ljósbrá
