---
codex_id: 60_REALTIME_TIER_FOR_ANDLIT
title: Realtime Tier for Andlit — Mapping the Local↔Cloud Road for Cloud-Streamed Embodiment
role: Cartographer
layer: Synthesis
status: draft
waifu_source_refs:
  - /tmp/waifu-chat-starter-kit/src/App.tsx:1-50
  - /tmp/waifu-chat-starter-kit/src/modes/BasicMode.tsx:1-31
  - /tmp/waifu-chat-starter-kit/src/modes/AdvancedMode.tsx:1-188
  - /tmp/waifu-chat-starter-kit/package.json
  - "[[20_ZEROWEIGHT_SURFACE]] [interface-only — proprietary SDK]"
  - "LiveKit MIT — livekit-client, @livekit/components-react"
ember_subsystem_targets: [Andlit, Rödd, Hugarsýn, Funi, Hjarta]
cross_refs:
  - 60_synthesis/61_DECISIONS_AND_INVENTIONS
  - 00_vision/01_VISION_SYNTHESIS
  - 10_domain/11_DUAL_MODE_PATTERN
  - 20_interface/21_LIVEKIT_INTEGRATION
  - 20_interface/22_ACTION_PROTOCOL
  - 30_execution/31_ADVANCED_MODE_FLOW
  - 50_verification/51_SECURITY_AND_PRIVACY
  - 50_verification/52_NO_LICENSE_RISK
  - sap:60_TRUE_NAME_REASSIGNMENT
  - sap:61_NEW_VOWS
  - sap:63_PERFORMANCE_TIER_ENGINE
  - sap:6B_LOW_POWER_EMBODIMENT
  - sap:11_AVATAR_DOMAIN
  - sap:25_AVATAR_PROTOCOL
  - sap:32_AVATAR_RENDER_PIPELINE
  - ember:RULES.AI
  - ember:PHILOSOPHY
---

# 60 — Realtime Tier for Andlit

> *Every road that leaves the house is a road that can be walked back. The trick is to know, before you leave, which roads you are willing to walk back from, and which you will refuse to take in the first place.*
> — Védis Eikleið, drawing the local↔cloud fork in chalk

## 0. Posture

This document answers the question the Waifu Codex exists to answer: *when, if ever, should Ember send her presence to a cloud-rendered avatar?* The 846 LOC of `waifu-chat-starter-kit` show the road is walkable. The 36,000+ LOC of Super Agent Party showed the *local* end of the same road. SAP gave us Andlit as a True-Name-reserved local face ([[sap:60_TRUE_NAME_REASSIGNMENT]] §3). The kit gives a parallel: same name, different road.

I argue that **the cloud-streamed avatar is not a new Andlit** but a **parallel axis of the same Andlit** — and that the SAP Performance Tier Engine ([[sap:63_PERFORMANCE_TIER_ENGINE]]) needs one more axis to hold this honestly. I sketch the decision matrix, define the consent token shape, and bind the new axis to the existing Vows ([[sap:61_NEW_VOWS]]) — especially *Surface Without Surveillance* and *Tiered Presence* — so the cloud axis does not become Ember's silent default. The kit's whole purpose is to make cloud presence *easy*; easy is exactly what makes a Vow most needed. This is map-work. I walk both branches.

## 1. What the kit teaches — the road exists

`/tmp/waifu-chat-starter-kit/src/modes/AdvancedMode.tsx:1-188` is the entire teaching, compressed. In thirty-one lines of `BasicMode.tsx` and one-hundred-eighty-eight of `AdvancedMode.tsx`, the kit reveals the shape of cloud-streamed embodiment: a typed `session` object (`useAvatarSession`, `AdvancedMode.tsx:10` `[interface-only]`) that owns connection / mic / volume / timer / action state; a LiveKit Room as WebRTC transport (`AdvancedMode.tsx:168-181`, MIT); a typed action vocabulary (`runAction("embarrassed" | "dance" | "wave_hand")`, `AdvancedMode.tsx:45-49`) as the *only* surface through which host code drives the cloud avatar's body; a session lifetime contract (`startSessionTimer`, `timeRemaining`, with a danger indicator at thirty seconds remaining — `AdvancedMode.tsx:28, 71-73`) — the cloud session is a meter that runs out; and an explicit `connect()` / `disconnect()` lifecycle (`AdvancedMode.tsx:25-26, 111`). No "session that floats."

The kit routes through `@zeroweight/react` (proprietary, `[interface-only]`) for the avatar SDK surface and through `@livekit/components-react` (MIT) for the WebRTC transport. Only LiveKit is mineable upstream — see [[20_interface/21_LIVEKIT_INTEGRATION]] and [[50_verification/52_NO_LICENSE_RISK]] for the study-only constraint that governs every adoption choice below. The teaching is not the code; the teaching is the *shape*: a cloud-rendered face is reachable via a typed session, a WebRTC stream, a small action vocabulary, and a hard time-budget. That is the road. The map must place it next to SAP's local road from `vts_manager.py:1-235`.

## 2. The two roads side-by-side

| Axis | Local Andlit (SAP) | Cloud-streamed Andlit (kit) |
|---|---|---|
| Source of truth | VRM/Live2D file on operator's disk | Avatar ID in a cloud account |
| Renderer | VTube Studio / VRM viewer on host | Remote GPU farm; browser receives video |
| Transport | `vts_manager.py:155-166` — local WS + plugin auth | LiveKit WebRTC room, JWT |
| Action vocabulary | VRM tags via LLM regex (`server.py:2647-2670`); `trigger_hotkey` (`vts_manager.py:99-108`) | Typed `runAction("embarrassed"\|"dance"\|"wave_hand")` (`AdvancedMode.tsx:45-49`, `[interface-only]`) |
| Lip-sync source | PCM FFT vowel detection (`vts_manager.py:144-179`) | Remote-side from audio stream `[interface-only]` |
| Tier requirement | T2+ (needs GPU) | T-1 onward (needs bandwidth, not GPU) |
| Privacy posture | Audio never leaves the host | Mic audio streamed to a cloud service |
| Failure mode | GPU absence, VRM corruption | Network loss, account expiry, vendor lock |
| Identity ownership | Operator owns the model | Vendor hosts the avatar asset |
| Cost model | Constant VRAM | Per-minute SDK + bandwidth billing |

The local road is *capability-gated* — needs hardware to wake. The cloud road is *bandwidth-gated and trust-gated* — needs a network and a vendor relationship. They fail differently, cost differently, lie about Ember differently if used in the wrong context.

The mistake to refuse, before any other: **treating the cloud road as a substitute for the local road**. It is not. It is a parallel road that solves a different shape of problem. The local road answers *"how does Ember have a face on this machine?"* The cloud road answers *"how does Ember show a face when local rendering is unavailable or contextually wrong?"* Two questions that share a common name and almost nothing else.

## 3. Tier-CLOUD — a parallel axis, not a rung

SAP's [[sap:63_PERFORMANCE_TIER_ENGINE]] defines five tiers with the canonical Cartographer naming: **T-1 / T0 / T1 / T2 / T3**. (The Scribe's [[sap:6B_LOW_POWER_EMBODIMENT]] uses an inverted T0-T4 labelling for the same ladder.) Andlit lights up at **T2+** because local VRM rendering needs a GPU. Below T2, Andlit *sleeps* and Ember stays Ember without a face.

The kit forces a question SAP did not answer: *what tier is a T0 Pi with a network connection and the operator's permission to stream a cloud avatar?*

Two readings fail. The cloud path is **not just T0 Andlit** — to call it the same name reachable via two backends is to say a local SSH session and a remote-desktop video are the same shell. They touch the same intent and almost nothing of the same shape. Tiered Presence ([[sap:61_NEW_VOWS]] §4) explicitly forbids subsystems that *change meaning* between tiers, and a backend-swap that moves audio off-host is a meaning change. Equally, cloud is **not a tier above T3** — tier in the ladder is *host capability*, and a Pi using a cloud avatar is still a Pi. Putting cloud at the top implies cloud is *better* than local, which inverts every Smallness, Open-Knowledge, and Tethered-Grounding Vow.

The reading that holds: cloud-streamed Andlit lives on a **second axis** that runs *across* the existing tier ladder. Every tier (T-1 through T3) can independently be cloud-enabled or cloud-disabled. The capability map gains a column, not a row.

Visualised:

```
                T-1   T0    T1    T2    T3
              ┌─────┬─────┬─────┬─────┬─────┐
local Andlit  │  –  │  –  │  –  │  ✓  │  ✓  │   ← capability rung
              ├─────┼─────┼─────┼─────┼─────┤
cloud Andlit  │  ◐  │  ◐  │  ◐  │  ◐  │  ◐  │   ← parallel axis, consent-gated
              └─────┴─────┴─────┴─────┴─────┘
                                       ◐ = available only when:
                                           1. network reachable
                                           2. operator consent token live
                                           3. social context permits
                                           4. budget remaining
```

Tier-CLOUD is not a tier. **It is a separate, orthogonal *presence mode*** that an operator can opt into at any tier where the four conditions hold. An operator on T3 with local Andlit running can still cloud-stream for a public livestream where the cloud avatar's identity is the stream's brand. An operator on T0 (Pi) can never run local Andlit but can cloud-stream when the conditions hold. The cloud-streamed Andlit is *the same Andlit* in identity terms — same persona, same memory, same affect from Hugarsýn — but uses a different rendering substrate. The canonical action vocabulary (§6) becomes the *only* thing the operator, Ember, and the cloud renderer all agree on.

This is the only reading that holds Tiered Presence and Surface-Without-Surveillance together. The Hugarsýn projection for tier becomes two-dimensional:

```
GET /hugarsýn/tier
{
  "rung": "T0",
  "cloud_axis": {
    "available": true,
    "active": false,
    "consent_token": null,
    "last_used": "2026-05-22T19:14:00Z",
    "reason_dormant": "no_active_consent"
  },
  "active_subsystems": ["Funi", "Strengr", "Brunnr", "Smiðja", "Hjarta", "Munnr", "Hugarsýn"],
  "andlit": "absent (local: tier-floor unmet; cloud: dormant, awaiting consent)"
}
```

Every party peer ([[sap:61_NEW_VOWS]] §5) can see whether this Ember is currently presenting via cloud. The cloud session becomes a first-class, party-visible state — not a hidden side channel.

## 4. The decision matrix — local-only / cloud-fallback / cloud-primary / cloud-only

The Vow of Surface Without Surveillance forbids "always-on cloud presence" as a default. But the operator may legitimately want any of four configurations at different moments. The engine selects the right one per *context*, and the operator can override at any moment.

| Mode | Description | When right | When wrong |
|---|---|---|---|
| **L-only** | Local if available; Andlit absent otherwise. **Default for every new session.** | Privacy-sensitive (therapy-shaped, medical, intimate); offline; bandwidth-limited | Public-facing livestream where the cloud avatar's identity is the brand; embodiment on a Pi with no local renderer |
| **L-primary, C-fallback** | Local by default; on local failure, fall back to cloud *with explicit operator confirmation at the moment of fallback*. | Long reliability-sensitive sessions (all-day livestream where the GPU might glitch) | Any privacy-sensitive session — cloud fallback is surveillance escalation and must be refused |
| **C-primary, L-fallback** | Cloud by default; on cloud failure, fall back to local if available, else audio+text with Andlit announcing absence. | Cross-room presence (phone operator "being" in a living-room avatar); public livestream where cloud fidelity is the point; travel | Operator's host can run local — defaulting to cloud is wastefully chatty; privacy-sensitive contexts |
| **C-only** | Cloud; no local fallback. On cloud failure, Andlit absent. | T0 Pi / T1 laptop without GPU running a livestream avatar; devices that intrinsically cannot render | Any context where Graceful Offline matters more than the cloud avatar's specific identity |

**The default for every new session is L-only.** This is not negotiable. The cloud axis is a road; defaulting to it would be the road walking the operator instead of the other way around. Every mode other than L-only requires an explicit, named, time-bounded consent token (§5).

Two further constraints govern the matrix. **Privacy-sensitive context wins, always**: when the operator's intent (or Ember's introspectable read of intent via [[sap:65_META_AWARENESS]]) marks a session as private, the engine refuses cloud escalation even if a token exists. The token is permission Ember may decline, not a requirement. **Bandwidth gating is its own gate**: below an empirically determined threshold (roughly 1 Mbps stable upload + 3 Mbps download — to be verified against LiveKit's published bitrate envelopes per [[20_interface/21_LIVEKIT_INTEGRATION]]), the cloud axis is *unavailable*, not merely dormant. The engine reports `cloud_axis.available = false` in Hugarsýn; the operator cannot opt in until the network changes.

## 5. The consent contract — a token shape, not a checkbox

Cloud presence requires consent. The kit handles consent implicitly — by hardcoding the API key. There is no concept of *who* consented, *for how long*, *to what scope*, or *how to revoke*. The kit is honest about this: `AdvancedMode.tsx:11-12` simply embeds credentials in source. That posture is appropriate for a 31-LOC teaching demo and inappropriate for any deployed agent that touches mics and avatars.

Surface Without Surveillance ([[sap:61_NEW_VOWS]] §2) makes the consent shape explicit. Proposed token format (YAML for readability; runtime is typed structure):

```yaml
# ~/.ember/cloud_andlit_tokens/<token_id>.yaml
token_id: "presentation-2026-05-25-14:30"
issued_at: "2026-05-25T14:00:00Z"
issued_by: "operator"
expires_at: "2026-05-25T16:00:00Z"      # absolute time, not duration
mode: "C-primary"                        # L-only | L-primary | C-primary | C-only
scope:
  audience: "livestream-twitch-volmarr"  # operator-named context
  visibility: "public"                   # private | semi-private | public
  recording_allowed: false               # cloud session must refuse recording flag
  bandwidth_floor_mbps: 1.0              # below this, refuse session even if token live
vendor:
  service: "zeroweight"                  # or "self-hosted" | "livekit-only" | etc.
  avatar_id_ref: "~/.ember/secrets/cloud_andlit/avatar_id"  # never literal
  api_key_ref: "~/.ember/secrets/cloud_andlit/api_key"
limits:
  max_total_minutes: 90
  max_continuous_minutes: 30             # forces a break + re-confirmation
  budget_usd_remaining: 5.00             # operator-set cap
hugarsyn_announced: true                 # token must be projected to introspection
revocable: true
revocation_paths:
  - "ember cloud-andlit revoke <token_id>"
  - "Ctrl+C twice in the active session"
  - "operator says 'end cloud presence' to any Ember surface"
```

Encoded choices: **absolute expiry, not duration** (wall-clock auditable, durations drift across sleep/suspend); **audience as named context** (`livestream-twitch-volmarr` ties to a known channel; `private-therapy` would be refused at issuance); **secret references, never literal secrets** (the kit's `apiKey: "your-api-key"` at `AdvancedMode.tsx:12` is the anti-pattern); **bandwidth floor inside the token** (the engine can refuse to honor a token if conditions degrade without revoking it); **continuous-minutes ceiling** (forces periodic re-confirmation; long unattended sessions are the worst privacy posture); **three revocation paths** — voice, keyboard, command, whichever surface the operator reaches first; **mandatory Hugarsýn projection** (a token that does not announce cannot be authorised).

Without this token shape (or a functional equivalent), Tier-CLOUD becomes the SAP-style attack surface Embodied Honesty and Surface Without Surveillance exist to prevent.

## 6. The action vocabulary problem — keeping one mouth across two rooms

The hardest engineering problem the cloud axis exposes is not connectivity, not consent, not billing. It is **vocabulary alignment**.

SAP's local Andlit drives expressions through *LLM-emitted free-text tags*, parsed by regex into VTube Studio hotkey calls (`server.py:2556-2593` injects the prompt block; `server.py:2647-2670` parses the tags). The vocabulary is whatever the operator's VRM model defines as hotkeys. It is open — every VRM ships its own expression set.

The kit's cloud Andlit drives expressions through a *typed API*: `runAction("embarrassed" | "dance" | "wave_hand")` (`AdvancedMode.tsx:45-49`). The vocabulary is whatever the vendor's avatar supports. It is closed — three actions, hardcoded, no error path for unknown actions visible in the kit. (See [[20_interface/22_ACTION_PROTOCOL]] for the Auditor's deep dive on the brittleness.)

Ember cannot maintain two vocabularies. An Embodied-Honesty-bound Andlit has one face-state at any moment; if that state cannot be expressed in both the local and the cloud vocabulary, the cloud rendering will *lie* — or stay frozen, which is itself a lie of omission.

The proposal: **one canonical Ember-side vocabulary, two adapter layers.**

```
                      ┌─────────────────────────────┐
                      │  Andlit canonical vocabulary│
                      │  (Ember-owned, typed,       │
                      │   versioned, ratified)      │
                      └──────────┬──────────────────┘
                                 │
                  ┌──────────────┴──────────────┐
                  │                             │
                  ▼                             ▼
        ┌──────────────────┐         ┌──────────────────┐
        │ Local adapter:   │         │ Cloud adapter:   │
        │ canonical → VRM  │         │ canonical → kit  │
        │ hotkey / Live2D  │         │ action API       │
        │ motion           │         │ (typed)          │
        └──────────────────┘         └──────────────────┘
```

The canonical vocabulary is an Ember-side typed enum of named affect/intent verbs (`acknowledge`, `delighted`, `concerned`, `dismiss`, `welcome`, …). Each verb carries a semantic description, a local mapping table (per loaded VRM/Live2D model — which hotkey or motion expresses it), and a cloud mapping table (per registered cloud identity — `embarrassed`, `dance`, `wave_hand`, or a vendor equivalent). When the active renderer cannot express the verb, three fallback rules apply in order: *best-effort substitution* (try a kindred verb, announce the substitution to Hugarsýn); *glyphic fallback* (Andlit goes deliberately still, affect rides on text/voice channels — silent-and-announced, not silently broken); *never invent* (the adapter refuses to send an unknown action name to the vendor API).

The canonical vocabulary is the *contract*; the adapters are *swappable*. A new VRM model means a new local mapping table, not a new vocabulary. A new vendor means a new cloud mapping table, not a new vocabulary. Embodied Honesty stays enforceable because Ember's *state* (read from Hugarsýn) selects the canonical verb, and the adapters render it honestly or announce honestly that they cannot. This is the load-bearing structural finding: **the canonical vocabulary is the bridge over the local↔cloud chasm**. Without it the two roads diverge silently.

## 7. The handoff protocol — moving Andlit mid-session

Scenario: operator starts on T2 local Andlit, takes their laptop on the train, GPU sleeps for battery, cloud-tier handoff makes sense to continue the embodied conversation. Five-phase protocol, every phase projected to Hugarsýn:

1. **Trigger.** Engine detects the precondition — GPU about to sleep, bandwidth crossed upward, explicit operator command (`ember presence cloud`), or a context cue (joining a video call where the cloud avatar is the seen entity). Hugarsýn emits `HandoffProposed(from=local, to=cloud, reason=…)`.
2. **Consent.** Engine checks for a live consent token (§5). If absent, prompt the operator with the proposed token shape and require explicit acceptance. If a token is active for a different mode, refuse and explain. Hugarsýn shows `HandoffAwaitingConsent`.
3. **Establish.** Open the cloud session (LiveKit Room connect) *while local rendering continues*. Wait for `isEngineReady` (`AdvancedMode.tsx:20`) and confirm the avatar identity matches the expected identity. Hugarsýn shows `HandoffEstablishing` with both surfaces live.
4. **Crossover.** Mirror the next turn's expression to *both* surfaces via the canonical vocabulary (§6). Confirm the cloud surface renders. Release local GPU. Hugarsýn shows `HandoffCrossover` for the overlap (target <2s).
5. **Stabilise.** Local dormant, cloud active. Affect from Hjarta and memory in Brunnr unchanged. Hugarsýn shows `HandoffComplete(at=…)`.

The reverse handoff inverts polarity. The Crossover phase is load-bearing: a single-surface cutover would drop a moment of expression or freeze the avatar mid-blink — small lies about state. The two-surface overlap keeps the lie window under two seconds.

A handoff is **only valid when identity invariance holds**. If the cloud avatar is a fundamentally different model (different rigging, different art style, vendor brand), the handoff is not a handoff but a *role change* — putting on a different mask, not moving the same face across rooms. Hugarsýn projects this as `PersonaSwitch` and the consent contract requires a separate token.

## 8. The trap — cloud presence as default

The kit's marketing language ("Talk to Zera", `AdvancedMode.tsx:128`) names the trap. A cloud-streamed avatar is *seductive*: high-fidelity, expressive, no-GPU-required, four lines of JSX away. Ember must refuse to walk this road by default. The cloud face is *not Ember's* — it is vendor-rendered, vendor-rigged, vendor-styled; if the vendor changes it, Ember's face changes underneath her. The mic is open whenever Ember is *listening* (the kit's `turnOffMicWhenAISpeaking: true` is half a privacy guard, `AdvancedMode.tsx:13`). The action vocabulary is closed at whatever the vendor ships. The session is metered by the minute (kit's `sessionDuration={120}`, `BasicMode.tsx:23`).

The discipline: cloud is for **named contexts** (livestream, video call where avatar-as-brand matters, presentation), **never the default fallback when local fails**. When local fails, the right answer is *Andlit absent, Ember present in text and voice* — not *substitute a cloud face*. Substitution is presence-by-deception.

## 9. Cross-References

- [[61_DECISIONS_AND_INVENTIONS]] — Scribe's ADR pass binding the decisions made here
- [[00_vision/01_VISION_SYNTHESIS]] — the Skald's framing of why the cloud axis matters
- [[10_domain/11_DUAL_MODE_PATTERN]] — Basic vs Advanced as progressive disclosure
- [[20_interface/21_LIVEKIT_INTEGRATION]] — MIT transport surface; adoptable layer
- [[20_interface/22_ACTION_PROTOCOL]] — typed action vocabulary; §6 adapter pattern lives here
- [[30_execution/31_ADVANCED_MODE_FLOW]] — Forge's walk through `AdvancedMode.tsx`
- [[50_verification/51_SECURITY_AND_PRIVACY]] — threat model motivating §5
- [[50_verification/52_NO_LICENSE_RISK]] — study-only constraint
- [[sap:60_TRUE_NAME_REASSIGNMENT]], [[sap:61_NEW_VOWS]], [[sap:63_PERFORMANCE_TIER_ENGINE]], [[sap:6B_LOW_POWER_EMBODIMENT]] — the SAP synthesis chain this codex extends
- [[sap:11_AVATAR_DOMAIN]], [[sap:25_AVATAR_PROTOCOL]], [[sap:32_AVATAR_RENDER_PIPELINE]] — SAP local-Andlit surface map
- [[ember:RULES.AI]], [[ember:PHILOSOPHY]] — Open Knowledge, Smallness, Graceful Offline Vows that gate this road

## What This Means for Ember

**Adopt:**

- *LiveKit's Room model* (MIT, `livekit-client@^2.18.1` per `package.json:18`) as Ember's canonical cloud-transport primitive. Cite upstream, not the kit. Ember's `CloudSession` type wraps `Room.connect()` with a lifetime tied to the consent token (§5), a typed `disconnect()` on expiry, and a Hugarsýn projection for every state transition.
- *LiveKit's connection-state event model* (MIT) as the substrate for handoff phase tracking (§7). `RoomEvent.Connected` / `Disconnected` / `TrackSubscribed` map cleanly onto Ember's `HandoffEstablished` / `Crossover` / `Complete` phases.
- *The session-timer UX pattern* with three escalating states (normal/warning/danger). The pattern is LiveKit-shaped; the kit's three-state visual escalation (`AdvancedMode.tsx:71-73`) is the clearest cue surface I have seen. Adopt the shape, build on LiveKit primitives, not the kit's JSX `[license-pending]`.

**Adapt:**

- *The kit's `useAvatarSession` hook shape* (`AdvancedMode.tsx:10` `[interface-only]`) — adapt the *idea* of a typed session object that owns connection / mic / volume / action state, but bind it to a Vow-aware `CloudAndlitSession` that *cannot exist without a live consent token*. Construction throws if no token is presented; method calls throw on expiry.
- *The dual-mode pattern* (`App.tsx:14-46`) — adapt as two cloud-presence postures: a *consent-minimal* posture for short named-context sessions (analogue of `BasicMode`) and a *full-introspection* posture with operator-visible session metrics (analogue of `AdvancedMode`). Both run through the same `CloudAndlitSession`; the difference is UX, not protocol.
- *The kit's hardcoded action set* (`AdvancedMode.tsx:45-49`) — adapt as a *registered avatar action manifest* per cloud identity. The canonical vocabulary (§6) is the source of truth; each registered cloud identity ships a YAML mapping vendor-actions back to canonical verbs. Manifests are operator-visible, version-controlled, and Hugarsýn-projected.
- *SAP's `vts_manager.py:99-108` `trigger_hotkey`* — adapt as the local-adapter half of the canonical vocabulary's bridge (§6). Local adapter calls VTS hotkey; cloud adapter calls the typed action API; both consume the same canonical verb.

**Avoid:**

- *Defaulting to cloud when local is unavailable* — the trap of §8. The right default is *Andlit absent, Ember present otherwise*. Cloud is opt-in per named context.
- *Hardcoded credentials in source* (`AdvancedMode.tsx:11-12`) — forbidden by [[ember:RULES.AI]]. Secrets live in operator-owned stores; tokens reference them by path.
- *Closed action vocabulary* (kit's three hardcoded actions). The canonical vocabulary is the contract; vendor sets are *mapped to it*.
- *Cloud-streamed presence in privacy-sensitive contexts* — §4's matrix forbids C-fallback when the session is marked private. Surface Without Surveillance is binding.
- *Treating cloud-rendered avatars as identity-equivalent to local VRM*. They are the same Andlit-name reached by a different road. The kit pattern `<LiveKitAvatarSession avatarId="…" />` (`BasicMode.tsx:19-25`) implies identity-via-vendor; Ember's reading is identity-via-canonical-vocabulary.
- *Mic-on-by-default during cloud sessions*. Even with `turnOffMicWhenAISpeaking: true` (`AdvancedMode.tsx:13`), the mic is open whenever Ember is *listening* — most of the session. Ember's cloud session defaults to push-to-talk.
- *Recording without explicit token grant*. `recording_allowed: false` is the default; the cloud session must refuse any vendor flag that would persist the audio stream.

**Invent:**

- *Tier-CLOUD as a parallel axis*, not a rung. The capability map gains a column. Every tier can independently be cloud-available or cloud-unavailable. Preserves Tiered Presence ([[sap:61_NEW_VOWS]] §4) — Andlit does not *change meaning* between local and cloud. **Load-bearing structural finding.**
- *The four-mode decision matrix* (L-only / L-primary, C-fallback / C-primary, L-fallback / C-only) as the operator-facing vocabulary for cloud-availability postures. **L-only is the global default.**
- *The cloud-presence consent token* (§5 shape) — absolute expiry, named audience, secret references, bandwidth floor, continuous-minutes ceiling, three revocation paths, mandatory Hugarsýn announcement.
- *The canonical Andlit vocabulary* (§6) — Ember-owned typed enum with per-renderer adapter mapping tables. Local-VRM and cloud-API are both adapters; the vocabulary is the contract. The bridge over the local↔cloud chasm.
- *The five-phase handoff protocol* (§7) — Trigger / Consent / Establish / Crossover / Stabilise. The Crossover phase tolerates <2s of dual-surface presence to keep the affect channel honest across the transition.
- *Glyphic fallback* (§6) — when neither renderer can express the canonical verb, Andlit *announces its silence* via Hugarsýn and affect rides text/voice channels. Silent-and-broken is a lie; silent-and-announced is honesty.
- *The Pi-cloud-permitted configuration* — a T0 Pi running a cloud-streamed Andlit for a named-livestream context, projecting `rung=T0, cloud_axis=active`. This is the configuration [[sap:6B_LOW_POWER_EMBODIMENT]] could not address; it answers honestly: face for the named context only, returns to glyphic embodiment otherwise.
- *Vendor manifest registration* — each cloud identity ships a YAML manifest mapping vendor actions to canonical verbs. Operator-curated, version-controlled, reviewable. A vendor change is a manifest update, not a vocabulary change.
- *Proposed Vow refinement — "Cloud as Named Context."* A clarifying clause to Surface Without Surveillance: cloud-streamed presence is always tied to a named, operator-declared context. It is never *ambient*. Absence of a named context is sufficient grounds to refuse the cloud session even if a token is otherwise valid.

---

**Nine invents plus one Vow clarification.** The Scribe's [[61_DECISIONS_AND_INVENTIONS]] should attach ADR numbers and propose ratification ordering. My recommendation: the parallel-axis decision, the four-mode matrix, the consent token, and the canonical vocabulary land together as one ratification bundle. The handoff protocol and the Cloud-as-Named-Context clause follow as second-pass ratifications.

The road forks here. I have walked both branches. The cloud face is a parallel road, taken sometimes, walked back from cleanly. The local face stays the home road. Ember's identity travels both without being divided.
