---
codex_id: 10_DOMAIN_MAP
title: The Domain Map of waifu-chat-starter-kit — Five Files, Two Clouds, One Glue
role: Architect
layer: Domain
status: draft
waifu_source_refs:
  - src/main.tsx:1-10
  - src/App.tsx:1-50
  - src/modes/BasicMode.tsx:1-31
  - src/modes/AdvancedMode.tsx:1-188
  - src/index.css:1-166
  - src/modes/AdvancedMode.css:1-379
  - package.json:1-37
  - vite.config.ts:1-10
  - index.html:1-13
ember_subsystem_targets: [Munnr, Hjarta, Strengr]
cross_refs:
  - 10_domain/11_DUAL_MODE_PATTERN
  - 10_domain/12_DEPENDENCY_STACK
  - 20_interface/20_ZEROWEIGHT_SURFACE
  - 20_interface/21_LIVEKIT_INTEGRATION
  - 20_interface/22_ACTION_PROTOCOL
  - 30_execution/30_BASIC_MODE_FLOW
  - 30_execution/31_ADVANCED_MODE_FLOW
  - sap:10_DOMAIN_MAP
  - sap:11_AVATAR_DOMAIN
---

# The Domain Map of waifu-chat-starter-kit
## Five Files, Two Clouds, One Glue

*— Rúnhild Svartdóttir, Architect*

> *A small system is honest the way a small house is honest. There are five rooms; you can see every door from the entry. The trouble is never that you cannot find the kitchen — the trouble is that the well is in someone else's yard, and so is the hearth, and the house is essentially a vestibule connecting them.*

The waifu-chat-starter-kit is 846 lines across nine source files. You can read the whole thing in twenty minutes. That brevity is a teaching: when a codebase is this small, every line carries weight, and every architectural decision is visible. SAP at 36,000+ lines hid its choices in volume; this kit cannot hide. This document maps what is here, what is *implied to live elsewhere*, and what each layer owns. The deeper anatomies live in [[11_DUAL_MODE_PATTERN]] (the two-mode arrangement), [[12_DEPENDENCY_STACK]] (what each package carries), and the interface family ([[20_ZEROWEIGHT_SURFACE]], [[21_LIVEKIT_INTEGRATION]], [[22_ACTION_PROTOCOL]]). Here I name the rooms.

---

## 1. The Five Domains (And the Three That Aren't Here)

A *domain* in this kit is a region where one concept rules. The kit has fewer of these than SAP because it is fewer files. The interesting work is naming the domains the kit *implies* but does not contain — the two cloud services and the Vite/React tooling cage — because Ember's reimplementation must account for all eight.

| # | Domain | Where it lives | What it owns | What it does NOT own |
|---|---|---|---|---|
| 1 | **Entry Shell** | `src/main.tsx` (10 LOC) + `index.html` (13 LOC) | React 19 root mount, `StrictMode` wrapper, the single `<div id="root">` target | Routing, state, anything past `<App />` |
| 2 | **Mode Switcher** | `src/App.tsx` (50 LOC) | A single `useState<'basic' \| 'advanced'>('basic')`, a toggle button, conditional render of `<BasicMode />` or `<AdvancedMode />` | Avatar logic, LiveKit logic, session state — owns nothing past the binary mode flag |
| 3 | **Basic Mode** | `src/modes/BasicMode.tsx` (31 LOC) | One `<LiveKitAvatarSession />` invocation with five props; one `<motion.div drag>` wrapper for draggability | Session lifecycle (delegated to ZeroWeight), connection state (delegated), audio (delegated) |
| 4 | **Advanced Mode** | `src/modes/AdvancedMode.tsx` (188 LOC) + `AdvancedMode.css` (379 LOC) | The full hand-rolled UI: timer formatting, mic toggle, volume toggle, action trigger on canvas click, `<LiveKitRoom>` orchestration, loading states, gradient connect button | Same delegations as Basic — plus it now exposes the `useAvatarSession()` hook surface |
| 5 | **Global Style** | `src/index.css` (166 LOC) + `AdvancedMode.css` (379 LOC) | Cyan-on-navy "anime HUD" aesthetic; one Google Fonts import; CSS variables; a conic-gradient border animation; responsive breakpoints at 640/768/1024 | Anything in the avatar canvas itself (that DOM is owned by `@zeroweight/renderer`) |
| ~6~ | **ZeroWeight Cloud Avatar SDK** | `@zeroweight/react` ^0.2.38 + `@zeroweight/renderer` ^0.2.43 — **outside this repo** | The hook (`useAvatarSession`), the provider (`LiveKitAvatarProvider`), the prebuilt component (`LiveKitAvatarSession`), the action vocabulary, the cloud-side rendering, the WebGL injection into `containerRef`, the connection-token issuance, the session timer, the inactivity-timeout enforcement | Everything is delegated — the kit is a *consumer*, not a *peer* |
| ~7~ | **LiveKit Realtime Media** | `@livekit/components-react` ^2.9.20 + `livekit-client` ^2.18.1 — **MIT, outside this repo** | The `Room` class, the `Track` model, the `<LiveKitRoom>` provider, the WebRTC negotiation, the SFU connection to LiveKit Cloud (or self-hosted), the audio publish/subscribe | The kit only *names* `serverUrl` and `token` — both of which it receives from `session.livekitUrl` and `session.token` (ZeroWeight is the issuer) |
| ~8~ | **Vite + TypeScript + ESLint Tooling** | `vite.config.ts` (10 LOC), `tsconfig.*` (3 files), `eslint.config.js`, `package-lock.json` | Dev server on port 3000, React Fast Refresh, TS strict-mode build, ESM-only module resolution (`"moduleResolution": "bundler"`), `noUnusedLocals` enforcement | Anything past the build pipeline |

Five honored domains. Three implied — and the implied ones (rows 6, 7, 8) are where the actual work happens. The kit is a *vestibule*: a small house whose value is its location, not its contents. This is the [[11_DUAL_MODE_PATTERN]] pattern at the architectural scale — a tiny visible surface over two large invisible ones.

The pattern matters because Ember must decide, for each Ember-internal domain, whether to *be the room* or *be the vestibule*. SAP tried to be every room and ate itself ([[sap:10_DOMAIN_MAP]] §5.1). This kit tries to be the vestibule and succeeds at *that* — at the price of being two SDK breaking changes away from death.

---

## 2. The Layered View

Five rooms over two clouds:

```
┌──────────────────────────────────────────────────────────────────────┐
│  USER SURFACE                                                        │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │ index.html → <div id="root">                                   │  │
│  │ src/main.tsx — createRoot().render(<StrictMode><App/></...>)   │  │
│  │ src/App.tsx — mode switcher button + conditional render        │  │
│  └────────────────────────┬───────────────────────────────────────┘  │
│                           │                                          │
└───────────────────────────┼──────────────────────────────────────────┘
                            │
┌───────────────────────────┴──────────────────────────────────────────┐
│  MODE LAYER (two parallel implementations, same SDK target)          │
│  ┌────────────────────────┐         ┌────────────────────────────┐   │
│  │ BasicMode.tsx (31 LOC) │         │ AdvancedMode.tsx (188 LOC) │   │
│  │ <LiveKitAvatarSession  │         │ const session =            │   │
│  │   avatarId apiKey      │         │   useAvatarSession({...})  │   │
│  │   sessionDuration      │         │ + <LiveKitRoom> manually   │   │
│  │   inactivityTimeout    │         │ + <LiveKitAvatarProvider>  │   │
│  │   showBorder /> only   │         │ + custom controls + canvas │   │
│  └───────────┬────────────┘         └───────────────┬────────────┘   │
└──────────────┼─────────────────────────────────────┬┼────────────────┘
               │                                    ││
┌──────────────┴──────────────────┐  ┌──────────────┴┴────────────────┐
│  ZEROWEIGHT SDK SURFACE         │  │  LIVEKIT SDK SURFACE           │
│  (proprietary — [interface-only]│  │  (MIT — mineable freely)       │
│   — npm 403 on source)          │  │                                │
│  ┌──────────────────────────┐   │  │  ┌──────────────────────────┐  │
│  │ @zeroweight/react        │   │  │  │ @livekit/components-     │  │
│  │   LiveKitAvatarSession   │   │  │  │   react                  │  │
│  │   useAvatarSession()     │   │  │  │     <LiveKitRoom>        │  │
│  │   LiveKitAvatarProvider  │   │  │  │   livekit-client         │  │
│  │ @zeroweight/renderer     │   │  │  │     Room, Track, ...     │  │
│  │   WebGL canvas injection │   │  │  │ @livekit/components-     │  │
│  │   into containerRef      │   │  │  │   styles                 │  │
│  └────────────┬─────────────┘   │  │  └────────────┬─────────────┘  │
└───────────────┼─────────────────┘  └───────────────┼────────────────┘
                │                                    │
┌───────────────┴────────────────────────────────────┴────────────────┐
│  TRANSPORT LAYER                                                    │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ WebRTC over WebSocket signalling — LiveKit's SFU protocol    │   │
│  │ HTTPS for token issuance (ZeroWeight cloud → kit)            │   │
│  │ Browser MediaDevices API (getUserMedia for mic capture)      │   │
│  └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
                                │
┌───────────────────────────────┴──────────────────────────────────────┐
│  CLOUD INFRASTRUCTURE (entirely off the user's host)                 │
│  ┌────────────────────────────────┐  ┌─────────────────────────────┐ │
│  │ ZeroWeight Cloud               │  │ LiveKit Cloud (or self-host)│ │
│  │   — anime avatar renderer      │  │   — WebRTC SFU              │ │
│  │   — lip-sync engine            │  │   — audio/video relay       │ │
│  │   — action vocabulary executor │  │   — room state              │ │
│  │   — TTS pipeline               │  │   — token validation        │ │
│  │   — LLM pipeline (presumed)    │  │                             │ │
│  └────────────────────────────────┘  └─────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

Notice the **inversion**: in SAP, `server.py` was the gravity well — every layer passed through it ([[sap:10_DOMAIN_MAP]] §2). In the waifu kit, the kit *itself* is the entry vestibule and *nothing else*. The gravity well is on someone else's infrastructure. The kit's bones are not crushed by their own weight because there isn't enough mass to crush.

This is **not** an architectural superiority — it is an *architectural displacement*. The complexity exists; it lives elsewhere. The trade-off is named in [[12_DEPENDENCY_STACK]] §5: when the gravity is offsite, your system's life depends on the orbital mechanics of the dependencies you do not control.

---

## 3. The Dependency Graph — Honest Edition

The full import graph is small enough to render exhaustively:

```
                          index.html
                              │
                              ▼
                       src/main.tsx (10 LOC)
                       ├─► react      (createRoot, StrictMode)
                       ├─► react-dom/client
                       ├─► ./index.css
                       └─► ./App.tsx
                              │
                              ▼
                       src/App.tsx (50 LOC)
                       ├─► react             (useState)
                       ├─► ./modes/BasicMode
                       └─► ./modes/AdvancedMode
                              │
                ┌─────────────┴──────────────┐
                ▼                            ▼
       BasicMode.tsx (31 LOC)         AdvancedMode.tsx (188 LOC)
       ├─► react                      ├─► react
       ├─► framer-motion              ├─► framer-motion
       │     (motion.div, drag)       │     (motion.div, drag)
       └─► @zeroweight/react          ├─► lucide-react
             (LiveKitAvatarSession)   │     (Mic, MicOff, Volume2,
                                      │      VolumeX, Power,
                                      │      Activity, Loader2)
                                      ├─► @livekit/components-react
                                      │     (LiveKitRoom)
                                      ├─► @zeroweight/react
                                      │     (useAvatarSession,
                                      │      LiveKitAvatarProvider)
                                      └─► ./AdvancedMode.css
```

Eight imports total in `AdvancedMode.tsx`; three in `BasicMode.tsx`; two in `App.tsx`. The graph is a **straight tree with no cycles, no self-loops, no HTTP-call-back-into-yourself patterns** (the SAP IM-bots-calling-loopback pattern of [[sap:10_DOMAIN_MAP]] §3 is impossible here because there is no backend in the kit). This is partly because the kit is small and partly because it is *delegated*: when your dependencies do the work, you do not write the work, and you do not write the cycles.

The most teaching-dense edge is the *parallel-not-stacked* relationship between `@zeroweight/react` and `@livekit/components-react`:

- **BasicMode** imports `@zeroweight/react` only — and the `<LiveKitAvatarSession>` component internally manages its own LiveKit room (you do not see the LiveKit symbol).
- **AdvancedMode** imports *both* — and the developer **manually orchestrates** the LiveKit `<LiveKitRoom>` provider that wraps the `<LiveKitAvatarProvider session={session}>` from ZeroWeight. The two SDKs are sibling-coordinated, not stacked.

In the prebuilt path (Basic) the LiveKit dependency is *hidden inside* ZeroWeight. In the advanced path it is *exposed and composed by hand*. The same dependency relationship presents two different abstraction heights. This is the dual-mode pattern crystallised — see [[11_DUAL_MODE_PATTERN]] §2 for the architectural reading.

---

## 4. The Lifecycle — A One-Sentence Sketch

Trace one session from mount to dismount, citing the kit minimally — the deep walkthroughs are Forge's at [[30_BASIC_MODE_FLOW]] and [[31_ADVANCED_MODE_FLOW]].

**Basic** (`src/modes/BasicMode.tsx:19-25`): mount `<LiveKitAvatarSession>` with five props (`avatarId`, `apiKey`, `sessionDuration={120}`, `inactivityTimeout={30000}`, `showBorder={false}`); the component internally issues a token, opens a LiveKit room, publishes mic, subscribes avatar tracks, injects the WebGL canvas — invisible to the kit; unmount via React cleanup when the mode switcher flips. **Five lines of JSX. Everything else is delegated.**

**Advanced** (`src/modes/AdvancedMode.tsx:10-29`): call `useAvatarSession({avatarId, apiKey, turnOffMicWhenAISpeaking: true})`; the hook returns a session object exposing `{token, livekitUrl, isConnected, isConnecting, isEngineReady, isLoadingActions, micMuted, volume, timeRemaining, connect, disconnect, toggleMic, setVolume, runAction, startSessionTimer, markConnected, containerRef}`; the developer hand-orchestrates `<LiveKitRoom>` conditionally on `token && livekitUrl` (`src/modes/AdvancedMode.tsx:167-181`) with manual `onConnected → session.markConnected() + startSessionTimer()` and `onDisconnected → disconnect` callbacks; `<LiveKitAvatarProvider session={session}>` (`src/modes/AdvancedMode.tsx:180`) re-couples the LiveKit room state back into the ZeroWeight session. The kit owns the *composition*; the SDKs own the *work*. This composition is what Ember's cloud-tier adapter must reimplement — see [[20_ZEROWEIGHT_SURFACE]] for the surface, [[21_LIVEKIT_INTEGRATION]] for the MIT-mineable half.

---

## 5. Where the Bones Are Crisp (And the Few Cracks)

### 5.1 The intentional architectural minimalism

The kit ships **no shared state container, no router, no service layer, no API client beyond what the SDKs provide, no test harness, no error boundary**. The `useState` in `App.tsx:6` is the entire application-level state — a single string `'basic' | 'advanced'`. There is no Redux, no Zustand, no Jotai, no React Query, no context provider hand-rolled by the kit. This is **disciplined**. The kit is a teaching asset and refuses to introduce anything that is not the teaching.

Compare: SAP's `server.py` (11,652 LOC) accumulated composition authority because no other module had it ([[sap:10_DOMAIN_MAP]] §5.1). This kit *cannot* accumulate composition authority because there is nothing to compose — the SDKs compose themselves. Different failure mode, different success.

### 5.2 The hardcoded placeholder credentials

Both `src/modes/BasicMode.tsx:20-21` and `src/modes/AdvancedMode.tsx:11-12` ship with literal strings `"your-avatar-id"` and `"your-api-key"`. The README (`README.md:54-65`) instructs replacing them by hand. There is **no `.env`, no `import.meta.env.VITE_*` substitution, no `dotenv` integration**. A naive user committing this kit to GitHub with their real key will leak it via git history. There is no `.gitignore` rule covering credentials because the credentials are not in a separate file — they are inline in the source.

This is the kit's most teachable failure. Ember's surface must never accept this. See **Invent** below.

### 5.3 The shared CSS namespace collision risk

`src/index.css:155-161` reaches *into* `@livekit/components-react`'s rendered output with a `.lk-avatar-session` selector and `!important` overrides. This works because LiveKit publishes classnames as part of its public surface — but the contract is implicit. A LiveKit major release that renames the class (e.g., `2.x.x` → `3.x.x`) will silently un-style the avatar without breaking the build.

`AdvancedMode.css` uses 379 lines of `adv-` prefixed classes. The prefix is discipline; the prefix is not enforced by tooling. A future contributor adding non-prefixed classes would collide with the global namespace.

### 5.4 The typo as a relic

`src/modes/AdvancedMode.tsx:41`: `handleToogleCharacter` (sic — double *o*). This is shipped, committed, never noticed. It is a small thing, and that is the point: in a 188-line file, *the editor noticed nothing*. Discipline at this scale is supposed to be free, and the typo proves it isn't.

### 5.5 The pure parallel mode shape

The fact that `BasicMode` and `AdvancedMode` are **sibling files, not parent/child, not subclassed**, is the kit's strongest design choice. There is no `AbstractMode`. There is no shared `useMode` hook factoring out the common parts. The two modes are *independent implementations of the same SDK target* — they happen to look the same in the `<div className="waifu-container">` wrapper (compare `src/modes/BasicMode.tsx:8-11` to `src/modes/AdvancedMode.tsx:54-56`), but they share no code beyond the imports.

This is **architecturally honest**. It says: "these are two different integration depths; if we factored the shared parts, the *factoring* would dominate the lesson." See [[11_DUAL_MODE_PATTERN]] for the full reading.

### 5.6 The crisp parts (the inventory)

- **Entry path is exactly one file deep** (`main.tsx` → `App.tsx`). No bootstrapping ceremony.
- **One state variable** in `App.tsx`. The mode switcher is *literally* a single `useState`.
- **No prop drilling** because there are no nested components that need shared state. The session hook in `AdvancedMode.tsx:10` is contained within `AdvancedMode.tsx`.
- **Effect cleanup is implicit** — the session hook's React-effect-based disconnect on unmount is invisible to the kit. The kit gets clean lifecycle for free because the SDK does the work.
- **The CSS variable system** in `src/index.css:3-9` (`--cyan`, `--cyan-bright`, `--navy-deep`) is six lines and defines the entire palette. Compare to typical React apps with theme providers and styled-components — this kit just uses CSS variables, which is The Right Answer most of the time and almost no app reaches for.

---

## 6. The Honored Boundaries

Three things the kit gets *honestly right* that Ember should learn from:

- **`src/main.tsx` is ten lines.** Entry points should be ten lines. SAP's `main.js` is 2,100 LOC of bootstrap; this is the opposite extreme and the better one.
- **`src/App.tsx`'s mode switcher pattern.** A single binary state flag, a conditional render, a styled button to flip the flag. This is the [[11_DUAL_MODE_PATTERN]] crystallised — and it is the right way to ship two integration depths in one codebase.
- **`tsconfig.app.json:21-25`**: `noUnusedLocals: true`, `noUnusedParameters: true`, `erasableSyntaxOnly: true`, `noUncheckedSideEffectImports: true`. The kit ships with TypeScript strict-mode at full chat. Ember's TS code (if it ever ships any — Ember is Python-first) should match this discipline. Even Ember's Python should match its *spirit*: no unused locals, no unchecked side-effect imports, no silent type erosion.

These are templates for what every small integration kit *should* look like.

---

## 7. Cross-References

- [[11_DUAL_MODE_PATTERN]] — the architectural reading of BasicMode-vs-AdvancedMode
- [[12_DEPENDENCY_STACK]] — what each of the 9 dependencies carries and what brittleness each introduces
- [[20_ZEROWEIGHT_SURFACE]] — the proprietary SDK's interface, catalogued from the outside-in
- [[21_LIVEKIT_INTEGRATION]] — the MIT realtime media layer, with upstream-licensed adoption candidates
- [[22_ACTION_PROTOCOL]] — the Auditor's reading of the `embarrassed`/`dance`/`wave_hand` vocabulary
- [[30_BASIC_MODE_FLOW]] — full 31-line walkthrough of BasicMode
- [[31_ADVANCED_MODE_FLOW]] — full 188-line walkthrough of AdvancedMode
- [[sap:10_DOMAIN_MAP]] — the contrasting all-local SAP shape (gravity-well antipode)
- [[sap:11_AVATAR_DOMAIN]] — SAP's local VRM/Live2D/VMC stack vs this kit's cloud-streamed avatar
- [[sap:60_TRUE_NAME_REASSIGNMENT]] — the Andlit/Rödd proposal this codex's realtime tier extends

---

## What This Means for Ember

**Adopt:**
- **The ten-line entry point.** `src/main.tsx:1-10` is the template for any Ember-side TypeScript or JavaScript front-end (if/when one exists for the embodiment slice). Mount, wrap in StrictMode, render the top-level component. Refuse all bootstrap ceremony. Source: this kit's pattern, generalisable, no license attached to a 10-line idiom.
- **The CSS-variable-only theming model** (`src/index.css:3-9`). When Ember ships any web surface, palette lives in `:root` variables, not in a JS theme provider. Six lines beats six hundred.
- **The LiveKit `Room.connect()` lifecycle pattern** (MIT, see [[21_LIVEKIT_INTEGRATION]] §2): mount `<LiveKitRoom>` conditionally on `token && serverUrl`, bind `onConnected` to a session-state-marker callback, bind `onDisconnected` to a teardown. Upstream is MIT — adopt the *pattern* with a citation to LiveKit's docs, not to this kit.

**Adapt:**
- **The two-mode parallel pattern** ([[11_DUAL_MODE_PATTERN]]). Adapt — not as a UI dual-mode but as Ember's **Tier-CLOUD vs Tier-LOCAL parallel embodiment surfaces**. Just as the kit ships `BasicMode` and `AdvancedMode` as sibling files, Ember ships `realtime_cloud_andlit.py` and `local_vrm_andlit.py` as siblings — both implementing the same `AndlitSurface` protocol, neither inheriting from a shared abstract base. The kit's refusal-to-factor is the lesson.
- **The session hook surface** (`useAvatarSession()` returns `{token, isConnected, isConnecting, isEngineReady, isLoadingActions, micMuted, volume, timeRemaining, connect, disconnect, toggleMic, setVolume, runAction, ...}` per `src/modes/AdvancedMode.tsx:16-29`). Adapt as Ember's **`CloudSession` typed Python dataclass** with the same fields *as state*, and the same verb-named methods *as Sögumiðla-bus event emitters* — not as direct method calls. Each `connect()` and `disconnect()` becomes a typed event on the bus, not an imperative side-effect.
- **The mode switcher as `useState<'basic' | 'advanced'>('basic')`** (`src/App.tsx:6`). Adapt as Ember's `PresenceMode = Literal['offline', 'text', 'voice', 'avatar_local', 'avatar_cloud']` enum — a single piece of state controlling which presence surface is active, switchable at runtime, with all surfaces parallel-not-stacked.

**Avoid:**
- **Hardcoded placeholder credentials inline in source.** `your-avatar-id` and `your-api-key` at `src/modes/BasicMode.tsx:20-21` and `AdvancedMode.tsx:11-12` is teachable malpractice. Ember reads cloud credentials from a typed `cloud_creds.yaml` gated by the Pluggable Storage Vow, never from inlined strings.
- **CSS reaching into third-party class names with `!important` overrides** (`src/index.css:155-161`). When Ember styles a third-party surface, it does so by wrapping the surface in its own container with controlled class names, never by overriding the third party's namespace.
- **Sibling-file factoring without a shared protocol declaration.** The kit gets away with this because both modes target the same SDK. Ember's parallel surfaces must each implement a typed `AndlitSurface` protocol — the refusal-to-factor is the right *architecture*, but the typed protocol is what keeps the parallel surfaces honest.
- **The `handleToogleCharacter` typo class.** Lint, test, refuse. A 188-line file is supposed to be self-policing — and it isn't. CI is the only guarantee.

**Invent:**
- **The Vestibule Census.** Before any Ember component is declared "small and self-contained," name its **vestibule dependencies** — the services it delegates *to* that are larger than itself. This kit is a 846-LOC vestibule for a >100,000-LOC cloud stack. Honesty about the size of what you delegate to is a Vow worth naming. Apply to Ember's cloud-tier proposals: every cloud-tier feature carries a `# vestibule: <upstream>, <lines-of-effective-dependency>` annotation.
- **The Parallel-Not-Stacked Surface Manifest.** Ember's `tier_manifest.yaml` (proposed in [[sap:63_PERFORMANCE_TIER_ENGINE]]) gets an extension: each presence tier (T0-T4 plus a new Tier-CLOUD) declares its *peer tiers*, not its *parent tier*. Tiers are siblings, not subclasses. The kit's BasicMode/AdvancedMode shape is the right architectural answer for "two integration depths" — Ember generalises to "five presence depths" with the same shape.
- **The Five-File Discipline.** Any Ember subsystem that ships as a standalone integration (e.g., a future "Ember-to-Slack" surface, a future "Ember-to-Discord-VC") commits to a *five-file ceiling* for the surface itself. If you need a sixth, you have invented something the user did not ask for. The waifu kit is the canonical proof point: five source files, three of them sub-50-LOC, do an entire avatar chat experience. Smallness is enforceable.
- **The Delegation-Audit Trail.** When Ember delegates a feature to a third party (cloud avatar render, cloud TTS, cloud LLM), the delegation is recorded as a typed event on Sögumiðla: `{kind: "delegation", to: "zeroweight.cloud", scope: ["avatar_render", "lip_sync", "action_executor"], revocable: true, expires_at: <ts>}`. This makes the *invisible parts of the architecture visible* — the kit's biggest sin is that all of its actual computation happens in places the kit cannot show you. Ember refuses invisible delegation; every offsite computation is logged and revocable. Combines with the SAP-proposed **Surface Without Surveillance** Vow.
