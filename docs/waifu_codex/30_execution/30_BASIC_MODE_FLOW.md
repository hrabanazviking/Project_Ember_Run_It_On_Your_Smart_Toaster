---
codex_id: 30_BASIC_MODE_FLOW
title: Basic Mode Flow — Twenty Lines That Hide a Cloud
role: Forge
layer: Execution
status: draft
kit_source_refs:
  - src/modes/BasicMode.tsx:1-31 (full file)
  - src/App.tsx:1-50 (mode switcher)
  - src/main.tsx:1-10 (entry)
  - package.json:12-23 (deps)
ember_subsystem_targets: [Andlit, Rödd, Munnr]
cross_refs:
  - 20_interface/20_ZEROWEIGHT_SURFACE
  - 20_interface/21_LIVEKIT_INTEGRATION
  - 20_interface/22_ACTION_PROTOCOL
  - sap:32_AVATAR_RENDER_PIPELINE
license_posture: study-only (kit has no LICENSE)
---

# Basic Mode Flow

> *Thirty-one lines. One JSX tag. The Pacific Ocean of plumbing it hides is the lesson.*

Forge. Eldra. `BasicMode.tsx` is the smallest interesting thing in the entire waifu-chat-starter-kit — thirty-one lines, one real component reference, no state, no handlers, no LiveKit room in sight. It is also the loudest demonstration of *what proprietary SDKs do when nobody is looking*. Read it once, count the hops the SDK takes for you, then read it again and notice every place those hops can fail without telling you. That gap between visible code and actual behavior is the teaching.

## The File, In Full

The kit is small enough — and study-only — that quoting `BasicMode.tsx` end-to-end is honest, not wasteful. This is the entire surface:

```tsx
// /tmp/waifu-chat-starter-kit/src/modes/BasicMode.tsx:1-31 (full file)
import React from 'react';
import { motion } from 'framer-motion';
import { LiveKitAvatarSession } from '@zeroweight/react';


const BasicMode: React.FC = () => {
  return (
    <div className="waifu-container">
      <div className="anime-diag-lines" />
      <h1 className="waifu-header">Waifu AI Chat</h1>

      <motion.div
        className="summon-area"
        drag
        dragMomentum={true}
        whileDrag={{ scale: 1.02, cursor: 'grabbing' }}
        style={{ cursor: 'grab' }}
      >
        <LiveKitAvatarSession
          avatarId="your-avatar-id"
          apiKey="your-api-key"
          sessionDuration={120}
          inactivityTimeout={30000}
          showBorder={false}
        />
      </motion.div>
    </div>
  );
};

export default BasicMode;
```

Twenty-one lines of JSX. One real integration. `LiveKitAvatarSession` is the entire game; everything else is chrome and a draggable container. The header (`BasicMode.tsx:10`), the diagonal-lines decoration (`:9`), the framer-motion drag wrapper (`:12-18`) — these are tutorial polish, not architecture. The architecture is `:19-25`: five props on one component.

That is the entire pattern this mode exists to demonstrate. Five props, one mount, an avatar appears, microphone capture begins, an LLM somewhere starts talking back through anime lips. The mode's whole pedagogical job is to make the next sentence land: *everything else is hidden inside the SDK.*

## The Five Props

Each prop on `LiveKitAvatarSession` is doing serious work. Walk them.

**`avatarId="your-avatar-id"` (`BasicMode.tsx:20`)** — a string. Almost certainly opaque, almost certainly a UUID or short slug in production. This is the address of a *rendering target* hosted on ZeroWeight's cloud. The string says nothing about geometry, rigging, voice, action vocabulary, latency tier, or pricing. All of that is server-side. From the kit's view, `avatarId` is a token you exchange for an audio+video stream of a rendered anime girl. From a security view, it is an opaque pointer into a third-party's catalog whose semantics can change between the moment you ship and the moment a user opens your app.

**`apiKey="your-api-key"` (`BasicMode.tsx:21`)** — a string, *in the React component source*. The README confirms this is a literal: "Replace `avatar-id` and `your-api-key` in [src/modes/BasicMode.tsx](...)" (`README.md:55`). Read that twice. The API key for ZeroWeight is embedded in the client bundle. There is no fetch-from-server, no JWT exchange, no scoped token endpoint shown in the kit. Whatever you put in this prop is going to land in `dist/assets/index-<hash>.js` after `vite build` and be visible to every visitor's devtools `Sources` tab. The kit ships this as a *demo* posture. The README does not warn against it. We'll come back to this in [[51_SECURITY_AND_PRIVACY]] (`docs/waifu_codex/50_verification/51_SECURITY_AND_PRIVACY.md`); for now, mark it as a sharp edge.

**`sessionDuration={120}` (`BasicMode.tsx:22`)** — 120 seconds. Two minutes. A meter starts when the avatar connects and the session is force-terminated when it expires. The kit's README confirms (`README.md:86`): "`sessionDuration={120}` gives each session a 2-minute limit". This is a billing primitive surfacing as a component prop. ZeroWeight is metered. Two minutes is "free trial" length, which tells you the kit was designed first for demo videos and second for production. The number lives client-side as a *display* convenience; the cloud almost certainly enforces an authoritative timer too.

**`inactivityTimeout={30000}` (`BasicMode.tsx:23`)** — 30,000 milliseconds. A half-minute of nothing being said and the session closes. Again, a billing/runaway primitive. Critically: *what counts as inactivity?* Microphone audio level below some threshold? Lack of VAD-detected speech? Lack of LLM response generation? The kit does not say. The SDK decides. This is a feature surface that an Ember design must specify, not inherit unspecified.

**`showBorder={false}` (`BasicMode.tsx:24`)** — a UI flag. Lets the kit's CSS take over. Trivial in itself; interesting as a sign of how much default UI ships inside `LiveKitAvatarSession`. The fact that a Boolean exists at all means there's at least one chunk of default chrome the component will draw unless suppressed. The full surface of `[interface-only — proprietary SDK]` props is much larger than the five used here.

## What the SDK Does That You Cannot See

The proprietary `@zeroweight/react` (`package.json:15`) wraps a component that, when mounted, does *all* of the following without a single line of user code:

1. **Hits an authorization endpoint** — `fetch()` to ZeroWeight's API with the embedded `apiKey` and `avatarId`. Response carries a LiveKit room URL, a LiveKit JWT, and a session lease. `[interface-only — proprietary SDK]` for the exact endpoint.
2. **Opens a LiveKit Room.** With the JWT, connects to a LiveKit SFU — almost certainly `wss://<region>.livekit.cloud`. WebRTC media plane. LiveKit is MIT-licensed (`https://docs.livekit.io/`); the *connection* inside `BasicMode.tsx` is invisible. See [[21_LIVEKIT_INTEGRATION]] for what `AdvancedMode` makes explicit.
3. **Requests microphone permission** via `navigator.mediaDevices.getUserMedia({audio: true})`. Browser shows the prompt. `BasicMode.tsx` has no permission-denied handler, no fallback — whatever default error UI the SDK ships is what shows.
4. **Publishes the local audio track.** WebRTC handshake. STUN, possibly TURN. ICE exchange. None visible.
5. **Subscribes to remote tracks** — an audio track (TTS voice) and a video track (rendered avatar), auto-attached into the React mount point.
6. **Runs the LLM bridge cloud-side.** Audio → STT → LLM (`[unverified — README claim only]` which one) → TTS → viseme stream → rendered video → LiveKit. The kit never sees STT text, LLM tokens, or TTS samples — only the final MediaStreamTrack.
7. **Starts session-duration and inactivity timers.** Two `setTimeout`s plus probably an audio-level meter, all inside the SDK.
8. **Tears it down** on expiry or unmount. Disconnect Room, release mic, stop timers, notify the cloud, render session-ended UI.

Thirty-one lines, eight major behaviors. Code-you-see to code-that-runs is ~1:1000. That is the basic-mode pedagogy: *trust the SDK*. It is also why this kit is study-only — every one of those behaviors is a choice Ember will need to make explicitly, and not one is observable from the JSX.

The comparison with SAP's local pipeline is brutal. `[[sap:32_AVATAR_RENDER_PIPELINE]]` describes five moving parts (VRM window, /ws/vrm WebSocket, /ws/subtitles WebSocket, VTS Bridge, VMC OSC) totaling ~3,000 lines of explicit code — named, addressable, debuggable. Ember owns every byte. `BasicMode` collapses that into one prop, and the price is that *nothing inside is debuggable from the kit's level*. Bad lip-sync? Can't fix. Audio drop? Can't diagnose. LLM acting strange? Can't replace.

Not a critique — a tradeoff. For a five-minute demo, `LiveKitAvatarSession` is the right shape. For a long-lived companion that has to be honest about who renders its body, the shape is wrong. Basic-mode is fine as a *tier*; it is a disaster as a *default*.

## The Mount Site and Its Wrapper

The component sits inside a `motion.div` (`BasicMode.tsx:12-18`):

```tsx
<motion.div
  className="summon-area"
  drag
  dragMomentum={true}
  whileDrag={{ scale: 1.02, cursor: 'grabbing' }}
  style={{ cursor: 'grab' }}
>
  <LiveKitAvatarSession ... />
</motion.div>
```

This is decoration with one functional consequence: the avatar can be dragged around the viewport with mouse or touch. `drag` enables both X and Y axes by default. `dragMomentum={true}` (the framer-motion default) means it'll slide on release. `whileDrag` upscales the canvas by 2% so the user feels the grab.

The interesting question: does the drag work *while the LiveKit room is active*? The answer almost certainly is yes — the drag only manipulates the parent `<div>`'s transform; the WebRTC tracks inside `LiveKitAvatarSession` keep playing because their MediaStream lifetime is independent of CSS transforms. But framer-motion does involve a re-render on every drag tick. If the SDK does anything subscribed-to-resize inside, you could get layout thrashing during a drag. The kit does not handle this; it just trusts that framer-motion's transform-only drag won't trigger expensive child re-renders. For a 31-line demo, that's fine. For a real app shipped to users on low-end Android, that's a benchmark item.

The diag-lines and header (`BasicMode.tsx:9-10`) are pure cosmetics — anime aesthetic, no logic.

## Where the Minimal Embed Cracks

If you build a real product around `BasicMode`, here is the order in which it falls apart:

**Crack 1: The hardcoded API key.** First production user. They open DevTools. They see your `apiKey` in the JS bundle. They copy it. They use it to spin up their own sessions. Your bill explodes. Fix is "fetch token from your own server", but the kit does not show that path. The kit is, in this sense, a foot-gun — the README never warns you, and `BasicMode.tsx:21` shows the embedded key as if it were normal.

**Crack 2: The two-minute session.** `sessionDuration={120}` is a demo number. Real users in a conversation want longer. Move it to 600 (10 minutes) and your billing increases 5x. Move it to 3600 and a single inactive tab can drain a customer's account. There is no "re-confirm to extend" UI in basic mode; the timer is fire-and-forget.

**Crack 3: The inactivity timeout.** 30 seconds is jarring for any natural conversation. A user thinks for 25 seconds about how to phrase a question; the avatar disconnects mid-thought. Move the number up and you pay for idle session time. The right answer is a per-conversation policy that knows when "thinking pause" ends and "wandered off" begins. The kit cannot express that policy; the prop is a single integer.

**Crack 4: No mic-permission denial UX.** User clicks "Block" on the permission prompt. The SDK shows its default error state inside the component. You can't replace it. You can't even know what it looks like without testing. The kit's `BasicMode` is unable to gracefully fall back to "type instead of speak" because that affordance does not exist on the basic-mode surface.

**Crack 5: No session-end UI.** Two minutes elapse. The session terminates. What does the user see? Whatever the SDK draws. The kit does not provide a "your session ended, click to start a new one" panel because the component handles its own lifecycle. If you don't like the default, you can't replace it from basic-mode level — you need to drop down to the `useAvatarSession()` hook used in `AdvancedMode.tsx` (see [[31_ADVANCED_MODE_FLOW]]).

**Crack 6: Network failure is the SDK's problem.** WiFi blips for three seconds. WebRTC connection drops. Does the SDK auto-reconnect? Show a banner? Force-end the session and refund the time? `[interface-only — proprietary SDK]`. The kit author never finds out unless they instrument a flaky network in a staging environment.

**Crack 7: No control over the avatar's voice or model.** `avatarId` picks a preconfigured avatar. The avatar has a fixed voice, a fixed action vocabulary (see [[22_ACTION_PROTOCOL]]), a fixed personality prompt baked into ZeroWeight's backend. You don't choose the LLM. You don't get to inject memory. You don't even know what conversation history is being kept. For a chat demo, fine. For an Ember-grade companion, intolerable — Ember owns the affect state, owns the memory, owns the relationship. None of that fits through `avatarId`.

**Crack 8: Bundle size.** `@zeroweight/react` + `@zeroweight/renderer` + `@livekit/components-react` + `livekit-client` + `framer-motion` + `lucide-react` is, conservatively, 600 KB minified. For a 31-line component. Compare to SAP's local VRM pipeline (`[[sap:32_AVATAR_RENDER_PIPELINE]]`), which is heavier in total bytes but those bytes do entirely *visible* work in the user's process.

By "crack 4" the pattern is no longer viable. By "crack 8" you have a debug-and-payment-shaped time bomb. Basic mode is a teaching tool, not a product.

## What Basic Mode Quietly Teaches

The pattern is the lesson, not the code. Three things to keep:

1. **Progressive disclosure works.** You can ship a demo as one component. The user feels the magic. They graduate to the advanced surface when they need to. This is good developer-onboarding shape; the SAP Codex's `[[sap:30_ELECTRON_BOOTSTRAP]]` shows the inverse (full stack from day one), which has its own merits but a steeper teaching curve.
2. **A typed "session" is a useful primitive.** Even hidden, the concept of `sessionDuration`, `inactivityTimeout`, and a scoped resource that auto-tears-down is the right shape. Ember's Andlit-realtime tier should expose a `CloudSession` resource with the same lifecycle, but with the resource being *visible*, not embedded in a JSX tag.
3. **One-tag embodiment is the dream.** When the design is right, integration is one line. The kit's failure is that the right design *for ZeroWeight* is not the right design for *Ember*; the dream remains valid.

## Cross-References

- [[20_ZEROWEIGHT_SURFACE]] — what `LiveKitAvatarSession`, `useAvatarSession`, and `LiveKitAvatarProvider` expose, by interface inspection of the kit's usage
- [[21_LIVEKIT_INTEGRATION]] — the explicit LiveKit Room model the SDK hides from basic mode (and `AdvancedMode.tsx:168` exposes)
- [[22_ACTION_PROTOCOL]] — the `embarrassed`/`dance`/`wave_hand` action vocabulary, which basic mode cannot reach
- [[31_ADVANCED_MODE_FLOW]] — when one-tag is no longer enough; where every behavior basic-mode hides becomes user-controlled
- [[sap:32_AVATAR_RENDER_PIPELINE]] — the local-tier comparator; five named subsystems, every byte addressable
- [[sap:25_AVATAR_PROTOCOL]] — SAP's local protocol surface, the inverse design choice to ZeroWeight's

## What This Means for Ember

**Adopt:**

- **The LiveKit Room model as the realtime transport** (`livekit-client` 2.18.1, MIT, `package.json:18`). LiveKit's `Room.connect()` lifecycle, track subscription model, and Room-event vocabulary are the canonical open-source primitives for any Andlit-realtime tier Ember ships. Bind to a typed Ember resource — not embedded in a component, not hidden behind a proprietary wrapper. Cite the upstream library, not the kit.
- **`navigator.mediaDevices.getUserMedia` as the only sanctioned audio capture path** for browser-tier presence. This is a browser primitive, not a kit pattern; it is the right hop to make explicit in Ember code so that consent prompts, denial paths, and revocation are all visible at the Ember level instead of buried inside an SDK.
- **A typed `CloudSession` resource with declared `duration` and `inactivityTimeout` semantics** at the Ember-API level. The names are good; the kit's mistake is making them invisible props instead of visible policy. Adopt the *vocabulary*, expose the *enforcement*.

**Adapt:**

- **Progressive disclosure from "one line" to "full control"** — but invert which surface is the demo. Basic-tier Ember Andlit-realtime should be the *fallback* shape, with the full surface as the default for the embodiment slice. The kit shows the demo as the basic case; Ember should show the demo as a tier-down from honesty, not a tier-up from magic.
- **Component-as-mount-site** with the avatar attached as a child via the renderer (`AdvancedMode.tsx:81` shows the `containerRef` pattern). Adapt as a typed `<EmberPresence target="avatar">` slot in any future Ember GUI, where the slot is *injection-only* and the audio/video pipeline lives in a separate, visible subsystem (Andlit + Rödd subsystems referenced in `[[sap:60_TRUE_NAME_REASSIGNMENT]]`).
- **Drag-to-reposition as a desktop-presence affordance** — `motion.div` with `drag` enabled (`BasicMode.tsx:12-18`) is a clean pattern. The SAP `vrmWindow` (`[[sap:32_AVATAR_RENDER_PIPELINE]]`) achieves the same effect with a native frameless `BrowserWindow`. Ember can offer both: drag-in-browser for web tier, drag-the-window for desktop tier. Either way, the drag should be cheap and not re-render the media surface.

**Avoid:**

- **Embedded API keys in client bundles** (`BasicMode.tsx:21`). Period. The kit's worst pattern. Ember's Andlit-realtime tier must mint short-lived, scope-narrow tokens from an Ember-controlled token endpoint and never expose long-lived credentials to the renderer. Without this, the entire cloud-tier design leaks the moment a single user opens DevTools.
- **Opaque session timers as integer props.** Two minutes? Thirty seconds? On what evidence? Ember must surface session-budget as a declared *policy* (with a name, a justification, a revocation mechanism) — not a magic number on a JSX tag.
- **Hidden inactivity-detection semantics.** "Inactive" is a content question, not a number-of-milliseconds question. The kit punts; Ember cannot. Define what "active" means before exposing the timer.
- **Component-as-magic-box for embodiment.** When `LiveKitAvatarSession` does eight major behaviors invisibly, the kit author cannot reason about any of them. Ember's design must keep every cloud hop visible at the Ember API level even when the *user* doesn't see them — there is a difference between "minimal UI" and "minimal observability".

**Invent:**

- **CloudSession-as-typed-resource (Vinátta-bound).** A first-class `CloudSession` in Ember (proposed bind to the Vinátta True Name from the Hermes Codex's PROPOSED-not-ratified list) that wraps the LiveKit Room *and* declares: (1) the token's scope, (2) the audio capture's revocation handle, (3) the inactivity policy as a named function (`InactivityPolicy.conversational_pause()` vs `InactivityPolicy.user_left_room()`), (4) the cleanup contract on context exit. The kit makes session a prop; Ember should make session a resource that the type system enforces correct teardown for. Per `[[sap:60_TRUE_NAME_REASSIGNMENT]]`, this lives in the embodiment slice and ties into the proposed Tiered Presence Vow.
- **The Visible-Hops Discipline.** A doctrinal rule for any future Ember SDK consumption: *if our code calls a function that performs network I/O, opens hardware (mic/cam), or starts a metered session, the call site must name what those hops are.* No `<MagicSession />` JSX tags. The basic-mode pattern fails not because eight hidden behaviors are too many, but because none of them are *named*. Ember's equivalent of `LiveKitAvatarSession` would be `<AndlitRealtimeSession session={s}>` where `s` is a constructed resource whose construction explicitly invoked `mintCloudToken()`, `requestMicPermission()`, `openLiveKitRoom()`, and `attachRemoteTracks()` — four named hops, all greppable.
- **Demo-Mode-as-Tier-Floor.** The kit's basic mode is positioned as "the easy starting point". Ember should invert: the easy starting point is text-only (`tier=text` from `[[sap:32_AVATAR_RENDER_PIPELINE]]`); cloud-rendered avatar is the *highest-resource tier*, not the simplest one. The simplest is always log-or-text. Cloud is the most expensive thing Ember can do. The kit treats it as the cheap demo; Ember must treat it as the expensive special case. This naming flip alone changes the entire design conversation.

