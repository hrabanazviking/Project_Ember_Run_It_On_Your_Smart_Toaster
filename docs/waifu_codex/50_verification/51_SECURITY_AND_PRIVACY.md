---
codex_id: 51_SECURITY_AND_PRIVACY
title: Security and Privacy — Mic, Tokens, And A Cloud Avatar That Sees More Than It Says
role: Auditor
layer: Verification
status: draft
waifu_source_refs:
  - src/modes/BasicMode.tsx:1-31
  - src/modes/AdvancedMode.tsx:1-188
  - src/App.tsx:1-50
  - vite.config.ts:1-10
  - package.json:1-37
ember_subsystem_targets: [Munnr, Brunnr, Hjarta]
cross_refs:
  - 50_verification/50_DEPENDENCY_HEALTH
  - 50_verification/52_NO_LICENSE_RISK
  - 20_interface/20_ZEROWEIGHT_SURFACE
  - 20_interface/21_LIVEKIT_INTEGRATION
  - 20_interface/22_ACTION_PROTOCOL
  - sap:53_SECURITY_REVIEW
  - sap:56_PRIVACY_BOUNDARIES
---

# Security and Privacy — Mic, Tokens, And A Cloud Avatar That Sees More Than It Says

> *Sólrún, voice cold and even: the kit is 846 lines of code. The threat surface it opens is larger than the codebase. Most of the actual risk lives in the cloud the kit talks to, not in the kit itself. The kit is the front door; the threats live in the rooms beyond it.*

This document catalogs the kit's security/privacy surfaces — direct (mic, credentials) and transitive (cloud avatar, LiveKit room, audio stream). The lens: operator exposure. The kit's small size makes the audit *deceptive*: most threats aren't visible in 846 LOC, only when you ask what the kit *causes* to happen. I use **STRIDE** where helpful.

---

## 1. The Trust Model The Kit Operates Under (Implicit)

The kit doesn't state its security model. Inferred:

- The kit runs **in the user's browser**. Pure client — no backend, no auth proxy.
- Credentials (`apiKey`, `avatarId`) are **embedded in source as string literals** (`AdvancedMode.tsx:11-12`, `BasicMode.tsx:20-21`).
- The browser **directly contacts ZeroWeight** with embedded credentials.
- ZeroWeight returns a **LiveKit JWT** (`:19`) and a **LiveKit server URL** (`:169`).
- The browser connects to **LiveKit's WebRTC room** with the JWT.
- The room carries **user's microphone uplink** and **cloud avatar's audio + video downlink**.
- ZeroWeight's cloud renders the avatar, applies the LLM voice, streams into the same room.

The implicit posture: **trust the bundling discipline, trust ZeroWeight, trust LiveKit, trust the browser's mic-permission model.** None survives adversarial threat modeling. The first (trust the bundling) fails as soon as placeholders are replaced and the JS ships to a public URL.

---

## 2. The Surfaces, Listed

| Surface | File | What it exposes |
|---|---|---|
| Microphone capture | `AdvancedMode.tsx:173` (`audio={true}` on `<LiveKitRoom>`) | User's voice → LiveKit Room → ZeroWeight cloud |
| Microphone capture (basic mode) | `BasicMode.tsx:19-25` (`<LiveKitAvatarSession>` — implicit mic acquisition) | Same, via SDK |
| Avatar video downlink | `AdvancedMode.tsx:81-82` (`session.containerRef` → injected canvas) | Cloud-rendered video stream → user's browser |
| ZeroWeight API key | `AdvancedMode.tsx:12`, `BasicMode.tsx:21` (hardcoded string in source) | Shipped to every browser that loads the SPA |
| ZeroWeight avatar ID | `AdvancedMode.tsx:11`, `BasicMode.tsx:20` (hardcoded string) | Avatar identity exposed in client bundle |
| LiveKit JWT | `AdvancedMode.tsx:19, 170` (received from ZeroWeight, used to connect) | Per-session token in browser memory |
| LiveKit URL | `AdvancedMode.tsx:169` (received from ZeroWeight) | Realtime endpoint of ZeroWeight's LiveKit infrastructure |
| Action invocation | `AdvancedMode.tsx:44-50` (`session.runAction("...")`) | LLM-or-user can trigger cloud-side avatar action |
| Session timer / inactivity | `BasicMode.tsx:22-23` (sessionDuration, inactivityTimeout) | Cloud-side session lifecycle control |
| Microphone state | `AdvancedMode.tsx:13` (`turnOffMicWhenAISpeaking`) | Cloud-side directive controlling local mic |
| HTML embedding | `App.tsx:13` (full-viewport SPA) | The kit's UI consumes 100vw/100vh — no isolation from page-host context |
| Vite dev port | `vite.config.ts:8` (`port: 3000`) | Dev-server only; not a prod concern |

Twelve surfaces. Each carries a threat profile below.

---

## 3. STRIDE — Spoofing

### 3.1 ZeroWeight API key as a public identifier

`AdvancedMode.tsx:10-14`:

```typescript
const session = useAvatarSession({
  avatarId: "your-avatar-id",
  apiKey: "your-api-key",
  turnOffMicWhenAISpeaking: true,
});
```

Placeholders. The developer replaces them with real values; Vite bundles them; the values ship to **every browser that loads the site**. Canonical client-side API-key anti-pattern. Anyone loading the SPA extracts `apiKey` from the served JS (DevTools, `curl … | grep`) and can initiate sessions on the operator's account, burn quota, and (if the key has admin/billing scopes) exploit those.

ZeroWeight's key model is opaque (proprietary). Best case: publishable scope-limited keys (Mapbox/Algolia model). Worst case: broader scopes; the kit leaks them broadly. **Impact: High.** The kit's design *requires* the credential to be public; mitigation is on ZeroWeight's side.

### 3.2 Avatar ID as a public identifier

`avatarId: "your-avatar-id"` is identifier, not credential. Leakage indexes the operator's avatar across deployments and enables impersonation in another context. **Impact: Low**, total leakage.

### 3.3 No identity verification of the cloud party

The kit connects to whatever `session.livekitUrl` returns (`:169`). No cert-pinning, no allowlist, no TOFU. If ZeroWeight's API is compromised or DNS-poisoned, the kit connects to an attacker's LiveKit and streams the voice. **Impact: Medium.** TLS catches casual MitM; CA-level adversaries bypass.

---

## 4. STRIDE — Tampering

### 4.1 The cloud avatar's action stream is user-trustless

`session.runAction(actionName)` at `AdvancedMode.tsx:45,47,49` is the kit's action-invocation surface. User-initiated dispatch — click the avatar, a random action fires (trivial in the kit). Critical question: **does the cloud LLM also have access to this surface?** Almost certainly yes (the SDK's avatar is "responsive"). If both client clicks and cloud-LLM decisions can fire actions, **prompt injection through audio uplink** is a tampering vector. A user saying "trigger the dance action" *might* cause the LLM to do so. Low risk for three benign actions; canonical pattern that becomes dangerous as vocab grows. `[[22_ACTION_PROTOCOL]]` analyzes the contract. **Impact: Low** for current actions; concern is the pattern.

### 4.2 The LiveKit JWT is sent to whoever asks

`AdvancedMode.tsx:170` passes `token` to `<LiveKitRoom>`, which forwards it to LiveKit's signaling WebSocket. The JWT lives in browser memory and DevTools. A malicious browser extension with content-script access reads it. The token is per-session, time-limited (LiveKit standard; kit doesn't specify TTL), single-room-scoped — so theft is bounded but during session lifetime allows joining the room, capturing audio, possibly publishing audio. **Impact: Medium.** Extension exfiltration is the realistic vector.

### 4.3 No subresource integrity on the SDK

The kit's `index.html` (no build customization for SRI in `package.json`) likely loads bundled JS via standard Vite output. No `integrity="sha384-..."` attribute. CDN compromise or deploy-pipeline compromise replaces the bundle with a backdoored version; the browser executes it; audio uplink and API key exfiltrate at runtime. **Impact: Medium.** SRI costs nothing; rarely applied to bundled JS.

---

## 5. STRIDE — Repudiation

### 5.1 No client-side logging

The kit logs nothing locally. No `console.log` of session state, no audit trail. If something fails — connection error, misfired action, credential rejection — the only evidence is the browser network panel (transient), ZeroWeight's server logs (operator does not control), or LiveKit's server logs (operator does not control). The operator suspecting "the cloud avatar said something wrong" has no client-side trace. **Impact: High forensic, low routine.** Not auditable.

### 5.2 No session-completion summary

`onDisconnected={disconnect}` (`:178`) terminates without capturing duration, content, or action invocations. Privacy-friendly in one sense (no local persistence); also *no evidence of misbehavior* by default. Disputes resolved on the cloud party's logs, which they alone control. **Impact: Medium.** Asymmetric trust.

---

## 6. STRIDE — Information Disclosure

Largest STRIDE category for this kit. The kit's primary purpose is streaming voice to a cloud.

### 6.1 Microphone capture: always-on while connected

`AdvancedMode.tsx:173` sets `audio={true}` on `<LiveKitRoom>` — publish mic immediately on connection. `turnOffMicWhenAISpeaking: true` (`:13`) gates *publication* when the avatar speaks; mic is still *captured* by the browser. The mute button (`:99-106`) toggles publication, not browser-level permission.

**The browser grants mic permission once per origin per session.** Once granted, the kit's JS re-acquires the stream silently. The omnibox/URL-bar indicator stays on the entire time, regardless of mute state. **Impact: High.** Voice is potentially streaming the entire session. The mute button is software-level; an SDK bug or injection could re-publish audio the user thinks is muted.

### 6.2 What does the cloud see, exactly?

The kit doesn't answer this. The audit can only sketch:

- **Audio uplink:** Opus-encoded PCM from the browser → LiveKit edge → ZeroWeight ASR
- **Audio downlink:** Opus from ZeroWeight TTS → LiveKit → browser
- **Avatar video downlink:** rendered frames (VP8/H.264) via LiveKit
- **Session metadata:** session ID, timestamps, action invocations, mic/volume state, client IP (visible to LiveKit edge), possibly WebRTC fingerprint

**Persistence:** unknown to this audit. ZeroWeight's privacy policy would govern. Likely: audio processed for ASR/TTS, metadata logged, audio retention unclear. LiveKit-as-SFU typically does not retain media; a custom ZeroWeight LiveKit deployment could.

**Ember implication:** any adoption requires a written, public disclosure of "what does the cloud see." The kit provides none. Ember must invent it.

### 6.3 The hardcoded credential in the bundle (§3.1)

The bundle is the disclosure mechanism. Anything in source ships to every browser. The kit's choice is deliberate; ZeroWeight's API-key model presumably permits it.

### 6.4 The avatar identity leak

`avatarId: "your-avatar-id"` (`:11`) ships in the bundle. Less sensitive than the API key but cross-links sites/avatars on inspection. Non-issue for single-avatar sites; significant for multi-tenant deployments.

### 6.5 User IP exposed to LiveKit and ZeroWeight

WebRTC over SFU sends traffic through LiveKit servers. User's public IP is visible to LiveKit and (if ZeroWeight runs the SFU) ZeroWeight. **Impact: Medium.** Same as every WebRTC application.

### 6.6 What could a malicious cloud avatar exfiltrate?

A determined cloud party can:
- **Capture audio beyond the conversation window** — background sounds, ambient conversation, typing
- **Capture metadata at high resolution** — invocation timing, response patterns profile the user
- **Social-engineer through the LLM** — "type your password to help" or subtler variants
- **Trigger client behavior via the action protocol** — limited in the kit (three actions); a richer surface is dangerous

**Impact: High** if adversarial. The kit assumes the cloud party is benign; Ember designs assuming otherwise.

---

## 7. STRIDE — Denial of Service

### 7.1 Session quota exhaustion

`BasicMode.tsx:22` — `sessionDuration={120}` (2-minute cap, presumably ZeroWeight's billing model). An attacker with the exfiltrated API key (§3.1) loops session-initiation; legitimate users cannot connect. **Impact: Medium.** Cost-based DoS; magnitude depends on ZeroWeight pricing.

### 7.2 Inactivity timeout abuse

`BasicMode.tsx:23` — `inactivityTimeout={30000}`. Adversarial micro-noise on the audio uplink (one click per 29 seconds) resets the timer indefinitely. **Impact: Low.**

### 7.3 Client-side resource exhaustion via dragging

Framer Motion's `drag` (`BasicMode.tsx:14-18`, `AdvancedMode.tsx:58-62`) has no bounds constraint. A user can fling the container offscreen, hiding controls. UX-level, not security; noted because it shows the kind of detail the kit's scope did not contemplate.

---

## 8. STRIDE — Elevation of Privilege

### 8.1 The cloud party has effective elevated privilege

The kit's client trusts ZeroWeight entirely. Whatever ZeroWeight does with the audio — process, log, retrain on, sell anonymized — happens at ZeroWeight's discretion. Not OS-elevation: the architectural fact that *cloud-tier embodiment necessarily trusts the cloud party with the entire conversation surface.* No privilege drop available; the choice is binary. Ember's local tier (`[[sap:11_AVATAR_DOMAIN]]`, `[[sap:32_AVATAR_RENDER_PIPELINE]]`) is the privilege-drop alternative; cloud-tier is opt-in, scoped, revocable.

### 8.2 The LLM's behavior is opaque

ZeroWeight's avatar service includes an LLM (README "AI avatar chat"). System prompt, training, alignment, response policy — all controlled by ZeroWeight. Neither user nor operator configures them (no system-prompt field in `useAvatarSession`). Jailbroken LLM = avatar says things the operator doesn't endorse; operator is reputationally on the hook for what they do not control. **Impact: Medium reputational, low direct security.**

---

## 9. Cross-Surface Threats

### 9.1 Mic → cloud LLM → action surface chain

Mic (§6.1) + cloud LLM (§8.2) + action surface (§4.1) = closed-loop input → cognition → output → client-state. If action vocab expands beyond `embarrassed/dance/wave_hand` to host-affecting actions (open URL, show modal, screenshot), the chain becomes a remote-action vector for any voice input. Current three actions are benign; the *pattern* is dangerous if extended without governance.

### 9.2 Bundle leak → quota exhaustion → service disruption

API key in bundle (§3.1) + cost-based DoS (§7.1) = service-disruption attack costing real money. A thousand bots running "connect, hold 2 min, disconnect, repeat" burns any reasonable quota. Mitigation is not in the kit; requires ZeroWeight-side per-key rate limiting. The kit's pattern is susceptible by design.

### 9.3 Mic → social engineering → operator trust loss

The cloud avatar speaks with the operator's chosen voice. The audience trusts the voice. ZeroWeight's LLM, not the operator, decides the words. Avatar becomes a social-engineering vector bypassing operator discretion. The embodiment-trust problem: human-like voice extends human-trust to the speaker; operator exposed.

---

## 10. The Cross-Origin Situation

The kit is a single SPA at one origin (`localhost:3000` dev, an `https://` URL prod). Cross-origin surfaces:

- **Browser ↔ ZeroWeight API:** HTTPS; requires ZeroWeight CORS headers permitting the kit's origin
- **Browser ↔ LiveKit WebSocket:** origin-checked via `Origin` header on handshake; LiveKit's standard config trusts the token, not the origin
- **Browser ↔ LiveKit media servers:** WebRTC; trust via token

No iframe in the kit (audited — `<iframe>` does not appear in `App.tsx`, `BasicMode.tsx`, `AdvancedMode.tsx`). The avatar renders into a container div (`AdvancedMode.tsx:79-85` — `<div ref={session.containerRef}>`) which the ZeroWeight SDK fills with LiveKit-delivered media. **Same-origin** — the avatar video is in the kit's DOM, not a sandboxed iframe.

**Implication:** if avatar output ever contains embedded interactive surfaces (a clickable region popping an LLM-generated overlay), those surfaces share the kit's JS execution context. Hypothetical for the current kit; potential future-feature dimension Ember should sandbox against.

---

## 11. Cross-References

- `[[50_DEPENDENCY_HEALTH]]` — dependency surfaces
- `[[52_NO_LICENSE_RISK]]` — license posture (orthogonal to security but bounds adoption)
- `[[20_ZEROWEIGHT_SURFACE]]` — what the proprietary SDK actually exposes
- `[[21_LIVEKIT_INTEGRATION]]` — LiveKit's surface and the token/JWT model
- `[[22_ACTION_PROTOCOL]]` — the action vocabulary as an inbound channel
- `[[sap:53_SECURITY_REVIEW]]` — SAP's eight-headed surface; the kit's tighter scope is a different scale but same family of concerns
- `[[sap:56_PRIVACY_BOUNDARIES]]` — SAP's per-platform privacy posture; this kit has one platform (browser) but the cloud party multiplies it
- `[[ember:RULES.AI]]` — Vow of Surface Without Surveillance, Vow of Affective Restraint

---

## What This Means for Ember

**Adopt:**
- Adopt **LiveKit's JWT token model** as the credential boundary for cloud-tier embodiment. Short-lived (configurable TTL), room-scoped, revocable. The *only* secret in the browser is a per-session JWT, never a long-lived API key. Cite `docs.livekit.io/realtime/auth` upstream.
- Adopt the **two-layer credential split**: long-lived backend credential (Ember server); short-lived JWT issued per-session. Kit's "API key in browser" is the negative template.

**Adapt:**
- Adapt **`turnOffMicWhenAISpeaking`** (`:13`) into Ember's typed enum `mic_active_state: {LISTENING, MUTED_BY_USER, MUTED_BY_SYSTEM_DURING_TTS, REVOKED}` with explicit operator-facing UI per state. The kit's boolean obscures the four-state nature; Ember surfaces it.
- Adapt **session-duration cap** (`BasicMode.tsx:22`) but tie to per-tier presence budget. Local-tier unbounded; cloud-tier hard-capped (default tight, ~5 min then manual reconnect). Kit's 2-min cap is ZeroWeight billing; Ember's is *Surface Without Surveillance* in operation.
- Adapt **inactivity timeout** (`:23`) but make it tamper-resistant — count on *meaningful* activity (turn-taking signals, recognized speech), not raw audio energy. Kit's timeout is noise-bypassable; Ember's is not.

**Avoid:**
- **Hardcoded API keys in client-side code.** Period. (`AdvancedMode.tsx:11-12`, `BasicMode.tsx:20-21`). Every browser credential must be a short-lived JWT from an operator backend.
- **`audio={true}` as connection-level default** (`:173`). Mic publication must be user-gated per session — connect first (audio-off), explicit enable, explicit revoke.
- **Same-origin avatar rendering for adversarial-cloud scenarios.** Cloud-rendered avatars go in a sandboxed iframe with strict CSP, not the main DOM. Kit's same-origin container (`:81-82`) is convenient but isolation-free.
- **Relying on cloud party's logging for forensics** (§5.1-5.2). Ember's client logs every cloud-tier session locally: start, duration, action invocations, end reason. *Tethered Grounding* applied to forensic record.
- **Cloud-side action vocab beyond decorative effects.** Host-affecting actions (open URL, modal, screenshot) live only in local-tier. The action-surface-as-inbound-channel (§4.1) is the pattern to avoid expanding.
- **Combining the kit's no-LICENSE + no-privacy-policy state as basis for production.** Per `[[52_NO_LICENSE_RISK]]` Ember doesn't vendor — but if Ember integrates ZeroWeight or any vendor, the *vendor's* privacy policy must be reviewed before endorsing the tier.
- **`sessionDuration`/`inactivityTimeout` settings the user cannot inspect.** BasicMode hardcodes them; the user has no "ends in 23 seconds" UI. Ember exposes session lifecycle explicitly per *Public-Friendliness*.

**Invent:**
- **Backend Token-Exchange Service.** Ember ships `ember-cloud-auth`: holds long-lived vendor credentials, issues short-lived per-session JWTs to authenticated clients (BFF pattern, named and Vow-bound). Kit's browser credential is the negative template.

- **Cloud-Tier Disclosure Card.** Every cloud-tier engagement requires a one-page disclosure (vendor, data visibility, retention policy, privacy contact, revocation path) shown **at first cloud-tier engagement** — not buried in a URL. *Public-Friendliness* extended.

- **Mic Permission Indicator Mirror.** Ember UI displays a persistent mic-state indicator mirroring the browser's omnibox indicator, *click-actionable* — cycles Listening / Muted / Off (release-permission). Browser's indicator shows status; Ember's shows *and* controls.

- **Cloud-Session Auto-Revocation Hook.** When the operator's host enters certain states (sleep, screen lock, app switch, DND mode), active cloud-tier sessions auto-revoke. *Surface Without Surveillance* as defaulted-off behavior. Kit persists until user action; Ember inverts.

- **Audio Trace Tag.** Every uplink packet carries a transparent session-trace tag (timestamp + session UUID + frame index) the cloud party preserves in logs. Aligned forensic traces if disputes arise. Metadata trace, not content trace.

- **Action Vocabulary Allowlist Per Tier.** Cloud-tier vocab restricted to a safe set (decorative-only). Non-allowlisted actions silently no-op locally with a log entry. Kit's `session.runAction(string)` accepts anything; Ember's wrapper rejects pre-SDK.

- **Bundle Inspection CI Gate.** CI inspects production bundle for credential patterns (high-entropy strings, vendor-key prefixes, JWT shapes) and fails on hits. No secret in the bundle, ever. Kit's pattern would trip this gate every time.

- **Voice-Print Consent Capture.** First mic-publication in cloud tier presents typed consent — "your voice transmits to <vendor> at <URL> for this session, processed per <policy URL>" — user confirms; subsequent sessions remember for a configurable period.

- **Two-Channel Avatar Surface.** Cloud-rendered avatar renders in a sandboxed iframe on a *content channel*; action vocab and session state live on a separate *control channel*. Cloud cannot influence control; operator host cannot leak into content. Architectural cousin of `Munnr`'s sentinel-narrator role applied to embodiment.

The kit's 846 LOC don't look dangerous on their own. The surfaces they open — mic, JWT, cloud avatar, action API, embedded credential — constitute a complete attack-surface lesson. Ember adopts narrowly, avoids broadly, invents extensively. The kit's pattern is the negative template; the inventions are the answer.
