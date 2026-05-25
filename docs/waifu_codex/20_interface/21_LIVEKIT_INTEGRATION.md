---
codex_id: 21_LIVEKIT_INTEGRATION
title: The LiveKit Integration — Room, Tracks, and the MIT Foundation
role: Architect
layer: Interface
status: draft
waifu_source_refs:
  - src/modes/AdvancedMode.tsx:2
  - src/modes/AdvancedMode.tsx:167-181
  - src/index.css:155-161
  - package.json:13-19
livekit_refs:
  - https://docs.livekit.io/home/
  - https://docs.livekit.io/reference/components/react/
  - https://docs.livekit.io/client-sdk-js/
  - https://github.com/livekit/components-js
  - https://github.com/livekit/client-sdk-js
ember_subsystem_targets: [Munnr, Rödd]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/12_DEPENDENCY_STACK
  - 20_interface/20_ZEROWEIGHT_SURFACE
  - 20_interface/22_ACTION_PROTOCOL
  - 30_execution/31_ADVANCED_MODE_FLOW
  - 51_SECURITY_AND_PRIVACY
  - 60_synthesis/60_REALTIME_TIER_FOR_ANDLIT
  - sap:11_AVATAR_DOMAIN
  - sap:25_AVATAR_PROTOCOL
---

# The LiveKit Integration
## Room, Tracks, and the MIT Foundation

*— Rúnhild Svartdóttir, Architect*

> *Of the nine packages the waifu kit pulls in, only one is built for the long road. LiveKit has been at version 2 for the better part of two years, ships its source on GitHub, ships its types in-package, and licenses everything Apache 2.0 (server) and MIT (client). Everything else in the dependency tree is either pre-1.0 or freshly-major. The kit underuses LiveKit; that is the most teachable fact in this entire study.*

LiveKit is the **only MIT-licensed dependency on the kit's critical path** that Ember can adopt without copyright hesitation. The kit imports `<LiveKitRoom>` from `@livekit/components-react` at `src/modes/AdvancedMode.tsx:2`, mounts it at `src/modes/AdvancedMode.tsx:168-181`, and uses three props (`serverUrl`, `token`, `connect`) plus two boolean media flags (`video={false}`, `audio={true}`) plus two callbacks (`onConnected`, `onDisconnected`). That is the *entire* LiveKit surface the kit consumes. The library exposes vastly more — see §3 — and the gap between *what the kit uses* and *what LiveKit offers* is where Ember finds its richest adoption candidates. This document catalogues both halves of that gap.

LiveKit citations cite the upstream MIT-licensed repos (`livekit/client-sdk-js`, `livekit/components-js`) and the official documentation at `docs.livekit.io`. Source claims that go beyond what the kit demonstrates are attributed to the upstream — those are *patterns Ember should adopt from LiveKit*, not from this kit.

---

## 1. What LiveKit Is

LiveKit is an open-source realtime media platform built around three layers, all MIT/Apache:

| Layer | Repo | License | What it provides |
|---|---|---|---|
| **Server** (LiveKit SFU) | `livekit/livekit` | Apache 2.0 | The selective forwarding unit — receives audio/video from publishers, forwards to subscribers; handles room state |
| **JS client** | `livekit/client-sdk-js` | MIT | The `Room` class, `Track` model, `Participant` events; pure JS, framework-agnostic |
| **React adapter** | `livekit/components-js` | MIT | `<LiveKitRoom>`, hooks (`useTracks`, `useLocalParticipant`, `useRoomContext`), pre-styled components |

The kit consumes the React adapter directly (`@livekit/components-react`), the JS client transitively (`livekit-client` is a dep), and the SFU implicitly — the kit's `serverUrl` (`src/modes/AdvancedMode.tsx:169`) points at a LiveKit server somewhere, either LiveKit Cloud (the commercial offering) or a self-hosted SFU. ZeroWeight cloud presumably hosts its own LiveKit fleet or uses LiveKit Cloud; from the kit's perspective both are URL-and-JWT-shaped.

**Why MIT matters here:** LiveKit's client and React adapter are MIT-licensed (verified at `github.com/livekit/client-sdk-js/blob/main/LICENSE` and `github.com/livekit/components-js/blob/main/LICENSE`). Ember can mine the protocol, the abstractions, even the source code — with attribution — and ship it inside Ember's repository as derived work. Compare to the waifu kit itself (no LICENSE; study-only per [[52_NO_LICENSE_RISK]]). The kit is study-only; LiveKit is **adopt-with-attribution**. This is the single most important license distinction in the codex.

---

## 2. What the Kit Actually Uses

### 2.1 The full LiveKit surface consumed by AdvancedMode

```typescript
// /tmp/waifu-chat-starter-kit/src/modes/AdvancedMode.tsx:2
import { LiveKitRoom } from "@livekit/components-react";

// /tmp/waifu-chat-starter-kit/src/modes/AdvancedMode.tsx:167-181
{token && session.livekitUrl && (
  <LiveKitRoom
    serverUrl={session.livekitUrl}
    token={token}
    connect={true}
    video={false}
    audio={true}
    onConnected={() => {
      session.markConnected();
      startSessionTimer();
    }}
    onDisconnected={disconnect}
  >
    <LiveKitAvatarProvider session={session} />
  </LiveKitRoom>
)}
```

That is it. One imported symbol. Seven props. Two callback handlers. One child (the ZeroWeight bridge component from [[20_ZEROWEIGHT_SURFACE]] §4).

### 2.2 The seven props, annotated

| Prop | Value | Inferred behaviour (from LiveKit docs) |
|---|---|---|
| `serverUrl` | `session.livekitUrl` (cloud-issued) | The WebSocket URL of the LiveKit SFU — `wss://...livekit.cloud` typically |
| `token` | `session.token` (cloud-issued JWT) | Signed JWT containing room name, participant identity, and grants |
| `connect` | `true` (constant) | Auto-connect on mount; `false` would mean "mount but await `room.connect()` manually" |
| `video` | `false` | Do **not** publish local video — mic only from the user |
| `audio` | `true` | Publish local mic track to the room |
| `onConnected` | inline arrow function | Fires once when the room transitions to `Connected` state |
| `onDisconnected` | `disconnect` (session method) | Fires when the room is torn down by either side |

The `onConnected` handler is where the kit closes its dual-SDK handshake: it calls `session.markConnected()` and `startSessionTimer()` (`src/modes/AdvancedMode.tsx:174-177`). This is the moment LiveKit's "I am connected" event is *translated* into ZeroWeight's "I am connected" state.

### 2.3 The conditional mount

`<LiveKitRoom>` is conditional on `token && session.livekitUrl` (`src/modes/AdvancedMode.tsx:167`). If either is null/empty, the room does not mount. This is the **correct** way to mount LiveKit's React adapter — `<LiveKitRoom>` requires both props to be truthy at mount-time; passing `null` or `undefined` would cause the room to fail its initial connect attempt.

The conditional also keeps the room *out of the DOM* until the session has issued credentials. This avoids a flash of error or a phantom connection attempt. The kit gets this right by virtue of treating `<LiveKitRoom>` as a *resource gate* — mount it only when the resources to drive it exist.

### 2.4 The CSS reach-into

`src/index.css:155-161` reaches into LiveKit's published class names:

```css
.lk-avatar-session {
  border: 1px solid rgba(0, 242, 255, 0.2) !important;
  border-radius: 0.5rem !important;
  box-shadow: 0 0 30px rgba(0, 242, 255, 0.1) !important;
  background: rgba(5, 10, 31, 0.8) !important;
  backdrop-filter: blur(10px) !important;
}
```

`.lk-avatar-session` is *not a class from `@livekit/components-react`* (LiveKit's React classes are prefixed `lk-*` but `lk-avatar-session` specifically appears to be from `@zeroweight/react`, which has likely *re-used the LiveKit naming convention*). The naming is ambiguous — the override could be targeting a LiveKit-styled wrapper or a ZeroWeight-styled wrapper. Either way, the kit reaches into the third-party namespace with `!important`. See [[10_DOMAIN_MAP]] §5.3 for why this is brittle.

`@livekit/components-styles` (the third LiveKit package, `^1.2.0` at `package.json:14`) is the canonical default-styles bundle. The kit does not appear to import it explicitly in TypeScript — meaning the styles arrive via `@livekit/components-react`'s side-effect imports (likely an `import './styles.css'` deep inside that package's barrel). If a future LiveKit version drops the side-effect import (a real possibility — modern best practice is to require explicit style imports), the kit's avatar will render unstyled until the user adds `import '@livekit/components-styles'` explicitly.

---

## 3. What LiveKit Actually Offers (And the Kit Underuses)

LiveKit's surface is **much larger than the kit demonstrates**. The kit uses one component (`<LiveKitRoom>`) with seven props. The MIT React library exposes (per `docs.livekit.io/reference/components/react/`):

**Components the kit could use but doesn't:**
- `<RoomContext>` — explicit context provider for manual room management
- `<ConnectionState>` — render-prop component for the room's connection state
- `<ParticipantTile>`, `<TrackRefContext>`, `<TrackToggle>` — track-level primitives
- `<ControlBar>` — pre-built mic/camera/leave controls
- `<MediaDeviceMenu>` — device selection UI
- `<GridLayout>`, `<FocusLayout>` — multi-participant layout primitives
- `<RoomAudioRenderer>` — explicit audio output mounting
- `<StartAudio>` — auto-play workaround for browser audio policies

**Hooks the kit could use but doesn't:**
- `useRoomContext()` — access the Room object directly
- `useLocalParticipant()` — local participant state + mute methods
- `useRemoteParticipants()` — remote participant list (the avatar in this case)
- `useTracks()` — all tracks across all participants, filtered
- `useConnectionState()` — room connection state as a reactive value
- `useConnectionQualityIndicator()` — link quality monitoring
- `usePinnedTracks()` — UI focus management
- `useChat()` — text chat over the LiveKit data channel
- `useDataChannel()` — arbitrary message-passing over the LiveKit data channel
- `useMediaDeviceSelect()` — device-switching state machine

**Lower-level (`livekit-client`) primitives the kit doesn't touch:**
- `Room` events: `Connected`, `Disconnected`, `Reconnecting`, `Reconnected`, `TrackPublished`, `TrackUnpublished`, `TrackSubscribed`, `TrackUnsubscribed`, `DataReceived`, `LocalTrackPublished`, `LocalTrackUnpublished`, `ActiveSpeakersChanged`, `RoomMetadataChanged`, `ParticipantConnected`, `ParticipantDisconnected`, and more
- `Track.Source` enum: `Camera`, `Microphone`, `ScreenShare`, `ScreenShareAudio`, `Unknown` — useful for distinguishing track kinds
- `RoomOptions`: `adaptiveStream`, `dynacast`, `videoCaptureDefaults`, `audioCaptureDefaults`, `publishDefaults`, `reconnectPolicy`
- `room.localParticipant.publishData(data: Uint8Array, options)` — out-of-band messages on the data channel
- `room.disconnect()`, `room.reconnect()` — explicit lifecycle control

**The kit uses ~5% of LiveKit's surface.** This is appropriate — the kit is a *demo*. But for Ember, the unused 95% is the goldmine. The kit teaches *what LiveKit could be used for in a thin glue*; Ember should learn what LiveKit *enables in a deep integration*.

The single most important under-used primitive: **the LiveKit data channel** (`room.localParticipant.publishData()` + the `DataReceived` event). This is an arbitrary-bytes pipe between participants in a room. ZeroWeight's `runAction("dance")` likely sends *something* over this channel (the action is presumably executed by an avatar process on the ZeroWeight side that receives a data-channel message). If Ember wanted to *send Munnr-internal state* (Hjarta affect vector, current focus, recent retrieval) to the cloud-rendered avatar without going through the audio channel, the data channel is the right path. See **Invent** below.

---

## 4. The Connection Lifecycle — As LiveKit Sees It

From the upstream LiveKit docs (cited freely; MIT/Apache):

```
                       ┌──────────────────┐
                       │  Disconnected    │ ← initial
                       └────────┬─────────┘
                                │ room.connect(url, token)
                                │ OR <LiveKitRoom connect={true}>
                                ▼
                       ┌──────────────────┐
                       │  Connecting      │
                       │  (signalling     │
                       │   WS handshake)  │
                       └────────┬─────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  Connected       │ ← onConnected fires
                       │  (RTC peer       │   tracks subscribe
                       │   connection up) │
                       └────┬─────────────┘
                            │
                ┌───────────┼───────────┐
                │           │           │
                │ network   │ explicit  │ server
                │ blip      │ disconnect│ kick
                ▼           ▼           ▼
        ┌────────────┐  ┌────────────┐  ┌────────────┐
        │Reconnecting│  │Disconnected│  │Disconnected│
        └─────┬──────┘  └────────────┘  └────────────┘
              │ recovery succeeds      onDisconnected fires
              ▼
        ┌────────────┐
        │ Connected  │ ← onReconnected fires
        │ (no remount│
        │  required) │
        └────────────┘
```

The kit handles `onConnected` and `onDisconnected` (`src/modes/AdvancedMode.tsx:174-178`). It does **not** handle `onReconnecting` or `onReconnected`. This means: if the user's wifi blinks for two seconds and LiveKit recovers the connection silently (which it can do, via the SDK's automatic reconnect), the kit's session state will show `isConnected: true` throughout — *correctly*, because the room is connected — but the kit has no way to indicate to the user "we just had a hiccup."

This is fine for a 2-minute demo session. For Ember's cloud-tier embodiment Vow ("Graceful Offline"), this is **insufficient** — Ember must surface reconnect transitions to the user (or to the audit trail) explicitly. Add `onReconnecting={...}` and `onReconnected={...}` to Ember's `<LiveKitRoom>` adoption. See **Adopt** below.

---

## 5. Tokens — What the JWT Contains

From the LiveKit docs (`docs.livekit.io/home/get-started/authentication/`), a LiveKit JWT carries:

- `iss` — API key identifier (the LiveKit project's API key)
- `sub` — participant identity (a string the SFU uses to identify the participant)
- `nbf`, `exp` — not-before / expiry (typically 1-6 hours; the kit's session timer is 120 seconds, much shorter than typical token lifetime)
- `name` — display name
- `video.room` — the room name the token grants access to
- `video.roomJoin` — boolean, the join grant
- `video.canPublish`, `video.canSubscribe`, `video.canPublishData` — granular grants
- `metadata` — opaque participant metadata

The kit's `session.token` (`src/modes/AdvancedMode.tsx:168`) is issued by ZeroWeight cloud — the kit never sees the JWT's payload. ZeroWeight signs it with their LiveKit API key; the kit just relays. **This is the right architecture**: the client never holds the LiveKit API secret; the secret stays server-side; the client gets a scoped JWT.

What Ember would need: **a Funi-side LiveKit token issuer**. Ember's cloud-tier embodiment adapter holds the LiveKit API secret on the Ember host (or, ideally, never on the Ember host — see [[51_SECURITY_AND_PRIVACY]]) and issues short-lived JWTs to the client. This is the *server-of-record* pattern; the kit demonstrates the *consumer* side; the server side is Ember's responsibility to implement.

LiveKit publishes a Python helper (`livekit-api`, MIT) that does exactly this. Ember can `pip install livekit-api` and have a `mint_token()` function in ~20 lines of Python. Cite `livekit/python-sdks` for the source.

---

## 6. Where the Kit's LiveKit Use Breaks (and What That Teaches)

### 6.1 The audio-only commitment

`video={false}, audio={true}` (`src/modes/AdvancedMode.tsx:171-172`). The user publishes mic, no camera. The avatar's video comes back from the remote. This is correct for the anime-avatar-chat use case — the user does not want their own face on camera; the avatar's face is what is rendered.

**What this teaches**: LiveKit can be configured for the asymmetric case (one-way video, two-way audio) trivially. Ember's text-chat embodiment can be even more asymmetric — `audio={false}, video={false}` and use *only the data channel* for messaging. The kit demonstrates audio-only; Ember can extend to data-channel-only for a low-bandwidth presence tier.

### 6.2 The missing track-level controls

The kit does not expose **device selection** — the user cannot choose which mic to use. On a laptop with three input devices (built-in mic, USB headset, virtual cable), LiveKit will pick the browser default; the user has no in-app way to switch. The library offers `<MediaDeviceMenu>` and `useMediaDeviceSelect()` for exactly this; the kit ignores them.

For Ember's production-grade embodiment: **always expose device selection**. The user must be able to choose which mic Ember listens to. This is a privacy as much as a UX issue.

### 6.3 The missing data-channel surface

Already noted in §3 — the kit does not touch `publishData()` or `useDataChannel()`. The action protocol ([[22_ACTION_PROTOCOL]]) presumably traverses *something*, and that something is most likely the LiveKit data channel (or a separate HTTPS API from the SDK to ZeroWeight cloud). Ember's investigation should determine which; if it is the data channel, Ember can ride the same channel for its own Munnr-side payloads.

### 6.4 The missing connection-quality surface

`useConnectionQualityIndicator()` (MIT, upstream) returns a per-participant quality enum (`Excellent`, `Good`, `Poor`, `Lost`, `Unknown`). The kit does not consume this — the user has no idea whether their connection is fine. For a 2-minute session, this is acceptable; for Ember's longer-lived cloud-tier presence, a quality indicator is mandatory. The user must know when to expect glitches.

### 6.5 The crisp parts of the kit's LiveKit usage

- **The conditional mount on `token && session.livekitUrl`** — correct resource-gating.
- **The `onConnected` handshake closure** — correctly translates LiveKit's lifecycle into ZeroWeight's state machine.
- **The `audio={true}, video={false}` asymmetry** — correct for the use case.
- **The `<LiveKitAvatarProvider session={session} />` as the sole child** — minimal coupling, correctly placed inside the room context.

---

## 7. Cross-References

- [[10_DOMAIN_MAP]] §1 row 7 for where LiveKit fits in the macro shape
- [[12_DEPENDENCY_STACK]] §2.4 for the three LiveKit packages and their version posture
- [[20_ZEROWEIGHT_SURFACE]] for the proprietary SDK that consumes LiveKit
- [[22_ACTION_PROTOCOL]] (Auditor) for the action-vocabulary that likely traverses LiveKit's data channel
- [[31_ADVANCED_MODE_FLOW]] (Forge) for the runtime walkthrough
- [[51_SECURITY_AND_PRIVACY]] (Auditor) for the JWT/credential threat model
- [[60_REALTIME_TIER_FOR_ANDLIT]] (Cartographer) for the Andlit-realtime tier proposal
- [[sap:11_AVATAR_DOMAIN]] §2.3 for SAP's VMC-over-UDP protocol — the local counterpart to LiveKit's WebRTC
- [[sap:25_AVATAR_PROTOCOL]] for SAP's avatar protocol comparison
- LiveKit docs: `https://docs.livekit.io/home/`
- LiveKit React components reference: `https://docs.livekit.io/reference/components/react/`
- LiveKit client SDK reference: `https://docs.livekit.io/client-sdk-js/`

---

## What This Means for Ember

**Adopt:**
- **`<LiveKitRoom>` (MIT, `@livekit/components-react`) as the canonical React mount** if/when Ember ships a React surface. Cite LiveKit's MIT license; adopt freely. The pattern: conditional mount on `token && serverUrl`; explicit `onConnected` / `onDisconnected` / `onReconnecting` / `onReconnected` handlers; `audio` / `video` booleans for the asymmetry.
- **`livekit-api` (Python, MIT) for Ember's token issuance.** A Funi-side `mint_livekit_token(participant_identity, room_name, ttl_seconds, grants: List[Grant]) -> str` function in ~20 lines, calling LiveKit's published helper. Cite LiveKit's Python SDK; adopt directly. The function is the *server of record* for token minting; Ember never embeds the API secret in client code.
- **`livekit` (Python, MIT) for Ember's server-side room operations** — `pip install livekit`. If Ember needs to dispatch a Munnr-driven event into a LiveKit room (a server-issued data-channel message, a forced disconnect, a metadata update), do it from Python via the MIT SDK. The kit demonstrates only the browser side; Ember's value is in the server side.
- **The LiveKit connection state machine** (Disconnected → Connecting → Connected → Reconnecting → Connected, per `client-sdk-js/src/room/Room.ts` and the upstream docs). This is the canonical realtime-media state machine. Ember's `CloudSession` state machine ([[20_ZEROWEIGHT_SURFACE]] §5) inherits this shape — *adopt* the state names and transitions directly. The diagram in §4 of this doc is the contract.
- **The `audio` + `video` boolean asymmetry pattern** for cross-modality presence. Ember's embodiment tiers explicitly declare which media tracks they publish vs subscribe; the LiveKit boolean shape generalises to a typed `MediaProfile` config.

**Adapt:**
- **The seven-prop `<LiveKitRoom>` config** — adapt as Ember's `LiveKitRoomConfig` Pydantic model with typed fields, default values, and validation. The kit's `connect={true}` constant becomes a configurable `auto_connect: bool = True`; the silent `onReconnecting` becomes a required callback.
- **The conditional-on-truthy mount pattern** — adapt as Ember's `mount_on_credentials_ready(creds: Optional[Credentials]) -> AsyncContextManager[Room]` idiom. The kit conditions on a JSX render; Ember conditions on a Python async context.
- **The `.lk-avatar-session` CSS reach-in** — adapt by *refusing* to override third-party class names. Ember wraps the LiveKit-rendered surface in its own container with controlled classes; never `!important` overrides into LiveKit's namespace.
- **The implicit-style-import behaviour** of `@livekit/components-styles` — adapt by *requiring* explicit style imports. If Ember ever ships a JS surface that consumes LiveKit, it does so with `import '@livekit/components-styles/components/styles.css'` written explicitly, not relying on side-effect imports.

**Avoid:**
- **The under-used MIT surface.** Already named in §3 — 95% of LiveKit's offering is on the table; the kit ignores it. Ember should not. Specifically: data channel, connection-quality indicator, reconnect callbacks, device selection menu. These are MIT, mineable, free for Ember to consume.
- **The audio-tracks-via-side-effect-imports pattern** for CSS dependencies. Make every dep import explicit.
- **The silent reconnect transitions.** Ember always surfaces reconnect to the user (status indicator) and to the audit trail (Sögumiðla event).
- **The single-mic-no-selection failure mode.** Always expose device selection in any Ember surface that captures audio.

**Invent:**
- **The LiveKit Data Channel as Munnr's Externalised Inner-Voice Track.** When Ember is in cloud-tier embodiment, the data channel (MIT) carries typed Munnr-internal events alongside the audio: `{kind: "affect_update", valence: -0.2, arousal: 0.5}` from Hjarta, `{kind: "memory_resurfaced", anchor: "thread-2026-04-12-walking-the-dog"}` from Brunnr, `{kind: "action_intent", action: "wave_hand", reason: "user said hello"}` from Munnr. The cloud-rendered avatar receives these as typed events and can *visualise the internal state alongside the spoken audio*. This is what SAP's VMC achieves in the local tier ([[sap:25_AVATAR_PROTOCOL]] §2.3) and what the data channel enables in the cloud tier — *parallel-not-substitute*. Defining the typed event schema is **load-bearing for the Embodied Honesty Vow** ([[sap:11_AVATAR_DOMAIN]] §invent).
- **The Connection-Quality-As-Vow-Trigger.** When LiveKit reports `Poor` or `Lost` connection quality (`useConnectionQualityIndicator()`, MIT), Ember automatically downgrades presence — turns off cloud avatar rendering, falls back to text mode, emits a Sögumiðla audit event. The user does not have to notice the connection is bad; Ember notices and adapts. Graceful Offline operationalised at the realtime layer.
- **The Token-Issuer-Of-Record Vow.** Ember's cloud-tier credentials always come from a Funi-side issuer that holds the API secret. The browser/UI side never sees the secret. This is the kit's actual architecture (ZeroWeight cloud is the issuer-of-record for the kit) generalised: *whatever Ember tier needs a third-party cloud credential, the credential is minted server-side and scoped narrowly*. The pattern is named, documented, and required for any cloud-tier feature.
- **The Reconnect-Audit-Trail.** Every LiveKit `onReconnecting` and `onReconnected` event becomes a Sögumiðla audit entry. The user can review their session and see exactly when network blips occurred — useful for debugging quality complaints and for *evidence that Ember was operating during a contentious window*. This is provenance-aware embodiment.
- **The MIT-First Dependency Audit.** Before adding any cloud-tier dependency to Ember, check: is there a comparable MIT or Apache-2.0 library? LiveKit is the canonical *yes*. Ember refuses to depend on a proprietary cloud surface for a feature that has an MIT alternative. If `@zeroweight/react` had to be the only path to anime avatars (it isn't — there are MIT alternatives like SadTalker or local VRM via [[sap:11_AVATAR_DOMAIN]]), Ember's calculus would shift. The audit is mandatory.
- **The Underuse Inventory.** When Ember adopts a third-party library, an *Underuse Inventory* is produced: a list of the library's features *Ember does not yet use but should consider*. This doc's §3 is the canonical example for LiveKit. Stored at `docs/external_surfaces/<lib>_underuse.yaml`. Reviewed quarterly. The kit's lesson is that great libraries are systematically underused; Ember refuses that lesson.
