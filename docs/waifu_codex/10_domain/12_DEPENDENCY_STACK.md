---
codex_id: 12_DEPENDENCY_STACK
title: The Dependency Stack — Nine Packages, Three Brittleness Classes
role: Architect
layer: Domain
status: draft
waifu_source_refs:
  - package.json:1-37
  - vite.config.ts:1-10
  - tsconfig.app.json:1-28
  - eslint.config.js:1-23
  - src/modes/AdvancedMode.tsx:3
  - src/modes/BasicMode.tsx:2-3
ember_subsystem_targets: [Munnr, Strengr]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/11_DUAL_MODE_PATTERN
  - 20_interface/20_ZEROWEIGHT_SURFACE
  - 20_interface/21_LIVEKIT_INTEGRATION
  - 50_verification/50_DEPENDENCY_HEALTH
  - 50_verification/52_NO_LICENSE_RISK
  - sap:10_DOMAIN_MAP
---

# The Dependency Stack
## Nine Packages, Three Brittleness Classes

*— Rúnhild Svartdóttir, Architect*

> *A house knows itself; a house knows nothing of the forest its timbers came from. The waifu kit knows its nine packages by name. It does not know that two of them are on the wrong side of a major-version cliff, that three of them depend on an SDK whose source no public network will return, and that one of them was incremented past 8.0 last month. The kit is small; its rooting is not.*

The waifu-chat-starter-kit has **nine runtime dependencies** and twelve dev-dependencies (`package.json:12-36`). The runtime nine are what ships to the user's browser; they are the kit's actual surface. This document inventories each one, names what it carries, classifies its brittleness, and proposes what an Ember reimplementation would need to provide *from each*. The Auditor's [[50_DEPENDENCY_HEALTH]] doc covers the *threat profile*; this doc covers the *architectural shape* — what each dependency is *for*, not what it could break.

---

## 1. The Inventory — Runtime Dependencies

```
@livekit/components-react        ^2.9.20    MIT, mineable
@livekit/components-styles       ^1.2.0     MIT, mineable
livekit-client                   ^2.18.1    MIT, mineable
@zeroweight/react                ^0.2.38    proprietary, [interface-only]
@zeroweight/renderer             ^0.2.43    proprietary, [interface-only]
framer-motion                    ^12.38.0   MIT, mineable
livekit-client                   (already counted above)
lucide-react                     ^1.7.0     ISC, mineable
react                            ^19.2.4    MIT, mineable
react-dom                        ^19.2.4    MIT, mineable
```

Nine packages. Three brittleness classes, defined in §3 below: **structurally young** (versioned 0.x, breaking changes expected), **recently major-bumped** (1.x to a much-higher 1.x, or freshly past 1.0), and **stable mature** (long-lived, multi-major-version-old SDKs).

Where each lives:

| Package | Imported by | Class | Provides |
|---|---|---|---|
| `react` 19.2.4 | `main.tsx`, all components | Recently major-bumped | The runtime — `createRoot`, `useState`, `StrictMode`, hooks rules |
| `react-dom` 19.2.4 | `main.tsx` via `react-dom/client` | Recently major-bumped | The renderer for the browser |
| `@zeroweight/react` 0.2.38 | `BasicMode.tsx`, `AdvancedMode.tsx` | **Structurally young (0.x)** | `<LiveKitAvatarSession>`, `useAvatarSession()`, `<LiveKitAvatarProvider>` — the dual-mode surface itself |
| `@zeroweight/renderer` 0.2.43 | (transitively via `@zeroweight/react`) | **Structurally young (0.x)** | WebGL canvas injection into `containerRef`; the actual avatar rendering pipeline |
| `@livekit/components-react` 2.9.20 | `AdvancedMode.tsx` | Stable mature | `<LiveKitRoom>` and the React-adapter primitives for LiveKit |
| `@livekit/components-styles` 1.2.0 | (CSS import — not visible in source files but pulled by `@livekit/components-react`) | Stable mature | Default styling for LiveKit components |
| `livekit-client` 2.18.1 | (transitively via `@livekit/components-react`) | Stable mature | The low-level WebRTC client — `Room`, `Track`, `Participant` |
| `framer-motion` 12.38.0 | `BasicMode.tsx`, `AdvancedMode.tsx` | Recently major-bumped | `motion.div`, `drag`, `dragMomentum`, `whileDrag` — the draggable wrapper |
| `lucide-react` 1.7.0 | `AdvancedMode.tsx` | **Recently past 1.0 (~6 months)** | Icon components: `Mic`, `MicOff`, `Volume2`, `VolumeX`, `Power`, `Activity`, `Loader2` |

The dev-dependency list (`package.json:23-36`) adds: `vite` 8.0.1 (recently major-bumped from 7), `typescript` 5.9.3, `@vitejs/plugin-react` 6.0.1, `eslint` 9.39.4, `typescript-eslint` 8.57.0, `globals` 17.4.0, three `@types/*` packages, two `eslint-plugin-*` packages. These do not ship to the browser but they determine *whether the kit builds at all* — a Vite 8 incompatibility with a future React plugin would be a fatal-at-build-time bug.

---

## 2. What Each Carries — The Anatomy

### 2.1 React 19 + react-dom 19

React 19 (~1 year old) brought the compiler (memoization automation), Actions, and a tightened ref API. The kit's usage is **minimal-modern**: `createRoot()` (`src/main.tsx:2,6`), `StrictMode` (`src/main.tsx:7-9`), `useState` (`src/App.tsx:6`), `React.FC` typing. No `use()`, no Actions, no `useActionState`. The kit could downgrade to React 18 and lose almost nothing — but pins 19, marking itself for the new compiler era.

Ember decision: *whether to have a React front-end at all*. Ember is Python-first; the cloud-tier UI may well be a static page calling Munnr-side endpoints, not a React SPA.

### 2.2 framer-motion 12

The kit's usage is **single-prop**: `<motion.div drag dragMomentum={true} whileDrag={{ scale: 1.02, cursor: 'grabbing' }}>` (`src/modes/BasicMode.tsx:13-18`, mirrored at `src/modes/AdvancedMode.tsx:57-63`). A 300+ KB minified dependency for *one* feature: a draggable wrapper. **Wildly overprovisioned** — the same behaviour is 30 lines of pointer-event handling. `framer-motion` is here because it is idiomatic in modern React UI, not because the kit needs variants, layout animations, scroll-linking, or springs.

### 2.3 lucide-react 1

Shipped **1.0 in early 2025**; the kit pins 1.7.0, six minor versions in. Lucide is a fork of Feather Icons with ~1,000 tree-shakeable React components. The kit's usage is **seven icons**: `Mic`, `MicOff`, `Volume2`, `VolumeX`, `Power`, `Activity`, `Loader2` (`src/modes/AdvancedMode.tsx:3`). Runtime cost ~7 KB after tree-shaking; ~50 MB in `node_modules` before. Standard React pattern; wrong pattern for Ember's TUI-or-static-first surface.

### 2.4 LiveKit — `@livekit/components-react` 2.9 + `livekit-client` 2.18 + `@livekit/components-styles` 1.2

LiveKit is **the load-bearing MIT dependency**. The three packages cleave the SDK into:

- **`livekit-client`** — the WebRTC engine. `Room`, `LocalParticipant`, `RemoteParticipant`, `Track`, `LocalTrackPublication`. This is the protocol layer. Pure JS, framework-agnostic.
- **`@livekit/components-react`** — React adapter primitives. `<LiveKitRoom>`, `<RoomContext>`, hooks like `useTracks`, `useRoomContext`, `useLocalParticipant`. The kit uses `<LiveKitRoom>` directly (`src/modes/AdvancedMode.tsx:168`).
- **`@livekit/components-styles`** — default CSS. Imported indirectly. The kit's `src/index.css:155-161` overrides one class (`.lk-avatar-session`) with `!important`.

Version notes: LiveKit's components-react has been at 2.x since mid-2024; the kit's 2.9.20 is current-stable. `livekit-client` 2.18 is recent. `components-styles` 1.2 is the long-stable companion.

What Ember would need: at minimum the protocol layer (`livekit-client`-equivalent). LiveKit Cloud has Python and Go SDKs as well — if Ember's cloud-tier code is Python (Funi-side), it can consume the `livekit` Python package for room state without ever touching the JS client. The React adapter is consumed only by a React UI; if Ember's UI is Python-rendered HTML or a TUI, the React adapter is not needed. This is the most important architectural point in this whole document: **LiveKit's MIT-licensed core can be consumed from Python**, decoupling Ember's cloud-tier from React entirely. See [[21_LIVEKIT_INTEGRATION]] §4 for the protocol detail.

### 2.5 ZeroWeight — `@zeroweight/react` 0.2.38 + `@zeroweight/renderer` 0.2.43

`@zeroweight/react` is the **proprietary SDK** at the heart of the kit. Version `0.2.x` is the critical fact: this is **pre-1.0 software**. By semantic versioning convention, 0.x packages can introduce breaking changes in any minor release. The kit's `^0.2.38` caret-pin allows upgrades up to `0.3.0` (exclusive) — but 0.3.0 might rename `useAvatarSession` to `useAvatar`, or change the action-runner signature, with no obligation to maintain compatibility.

`@zeroweight/renderer` is the lower-level WebGL renderer. The version (`0.2.43`) is even higher in patch number than its React sibling, suggesting active development. `[interface-only — proprietary SDK]`: the npm registry returns 403 on source inspection. We know its surface only through the kit's *usage*: `containerRef` is a mount point ([[20_ZEROWEIGHT_SURFACE]] §2), and the renderer injects WebGL there.

What Ember would need from these: *to not need them*. Ember's cloud-tier proposal in [[60_REALTIME_TIER_FOR_ANDLIT]] should treat ZeroWeight as a *pluggable provider*, not a hard dependency. The Pluggable Storage Vow generalises here as a **Pluggable Cloud Avatar Provider** Vow — see **Invent** below.

### 2.6 Vite 8 + TypeScript 5.9 + ESLint 9 (dev deps)

`vite` **8.0.1** is recent — Vite 8 shipped in early 2025, raising the minimum Node version to 20.19. `vite.config.ts:5-9` uses only the React plugin and a custom port. No SSR, no SSG, no environment-variable wiring, no proxy config. The Vite usage is *vanilla*.

`typescript` 5.9.3 is stable. `tsconfig.app.json:21-25` enables every paranoid flag: `noUnusedLocals`, `noUnusedParameters`, `erasableSyntaxOnly`, `noUncheckedSideEffectImports`. **The kit ships with TS strict-mode at full chat.** This is discipline worth adopting.

`eslint` 9.39.4 is the new flat-config era. `eslint.config.js:1-23` uses the flat config format. `tseslint.configs.recommended` is enabled. The kit lints — but no `lint-staged`, no `husky`, no CI config in the repo. Lint is *available*, not *enforced*.

What Ember would need: nothing for the build pipeline directly. The *discipline* — strict TS, recommended ESLint, paranoid compiler flags — is worth lifting into any Ember-side TS code, and the *spirit* (no unused locals, no silent type erosion) is worth lifting into Ember's Python via mypy strict-mode + ruff + ban-on-unused-imports.

---

## 3. The Brittleness Map

### 3.1 Class A — Structurally Young (0.x packages)

**Members:** `@zeroweight/react` 0.2.38, `@zeroweight/renderer` 0.2.43.

By semver, 0.x packages can introduce **breaking changes in any minor release**. The kit's caret-pin (`^0.2.38`) allows upgrades up to (but not including) 0.3.0 — within that range, the SDK *should* be compatible, but ZeroWeight has not made the 1.0 commitment. A jump to 0.3.0 in three months could rename `useAvatarSession` (`src/modes/AdvancedMode.tsx:10`) to `useAvatar`, remove `runAction` in favour of an event-bus API, or change `LiveKitAvatarSession`'s prop list. Each of those would break the kit's existing user base.

The version asymmetry between the two ZeroWeight packages (0.2.38 vs 0.2.43) is also notable. Patch numbers in the high 30s/40s for a `0.x` package implies *active development*, which is good (the SDK is being maintained) and *frequent surface change*, which is bad (today's working integration is tomorrow's broken integration).

**Brittleness verdict:** **high**. Any production user of this kit must pin exact versions, audit each patch release, and budget time for breakage at each upgrade. Ember's Pluggable Cloud Avatar Provider abstraction (see **Invent**) must be layered such that a ZeroWeight 0.3 surface change requires editing *the adapter*, not Ember's core code.

### 3.2 Class B — Recently Major-Bumped (post-1.0, fresh majors)

**Members:** `react` 19.2.4 (React 19 is ~1 year old as of 2026-05), `framer-motion` 12.38.0 (12 is ~6 months old), `vite` 8.0.1 (~3 months old), `lucide-react` 1.7.0 (1.0 was ~6 months ago).

These are *post-1.0 stable* in the sense that semver protects against breaking changes within the major — but the major itself is recent. Adjacent tooling may not yet be compatible. React 19's compiler is still being adopted; some popular libraries (`@react-three/fiber`, certain MobX patterns) had compatibility lag. Vite 8's Node 20.19+ requirement quietly excluded Node 18 users. `framer-motion` 12 dropped IE / older-browser support.

**Brittleness verdict:** **medium**. The packages themselves are stable inside their major versions. The *ecosystem* around them may not be. A new contributor to the kit who runs `npm install` on Node 18 will get an error before they reach the first `npm run dev`. The kit does not document its Node version requirement (the README says "Node.js 20+ recommended" at `README.md:39` — recommended, not required, despite Vite 8 making it a hard requirement).

### 3.3 Class C — Stable Mature

**Members:** `livekit-client` 2.18.1, `@livekit/components-react` 2.9.20, `@livekit/components-styles` 1.2.0.

LiveKit's 2.x line has been stable for a year-plus, MIT-licensed, with an active maintainer (LiveKit Inc.) and a documented compatibility policy. The library's API has been incrementally extended within 2.x rather than re-architected. Source is on GitHub at `livekit/livekit-client` and `livekit/components-js`.

**Brittleness verdict:** **low**. These are the closest the kit comes to "things you can build on for years." If Ember has *any* hard dependency in the cloud-tier, LiveKit is the right one — and even then, only the protocol layer, with a typed adapter to insulate Ember from LiveKit's JS surface.

### 3.4 The combined brittleness profile

Two packages are high-brittleness *and* on the load-bearing path (the entire kit collapses without `@zeroweight/react`). Four packages are medium-brittleness, two of which (`react`, `vite`) are critical to the build. Three packages are low-brittleness and form the *only* part of the dependency stack a long-term maintainer can rely on.

This is the kit's fundamental architectural risk: **the part most likely to break is the part you cannot replace** (ZeroWeight is proprietary; no fork is possible; no MIT equivalent is named). The part *least* likely to break (LiveKit) is *also* the part that is *trivially replaceable* — you could swap LiveKit Cloud for self-hosted LiveKit or for Daily.co or Twilio Video with adapter work.

The brittleness inversion is the lesson. See [[50_DEPENDENCY_HEALTH]] for the threat-shaped reading; this doc's job is to make sure Ember inverts the inversion — its hardest dependencies must be its most-replaceable, not its least.

---

## 4. The ESM-Only Future

`package.json:5`: `"type": "module"`. The kit is ESM-only. `tsconfig.app.json:11`: `"moduleResolution": "bundler"`. The kit assumes its dependencies are also ESM-compatible.

This is the current state of the JS ecosystem: most modern packages are ESM-first or dual-published (CJS+ESM). The kit's dependencies are all ESM-compatible. But the trend is one-directional — *new* major releases of popular libraries are dropping CJS exports. A future user of this kit on a CJS-heavy host (some legacy Node tools, some bundlers) will be unable to consume the kit's compiled output without an additional transpilation step.

What Ember would need: if Ember ever ships a JS/TS module, it should be **ESM-first**, dual-published if budget allows, with explicit Node-version requirements in `package.json:engines`. The kit's silent assumption (`type: module` with no `engines` declaration) is teachable malpractice — the kit *assumes* a modern Node and fails opaquely on older ones.

---

## 5. Where the Stack Surprises (and What That Teaches)

### 5.1 The hidden transitive surface

The kit imports 9 packages. `npm install` produces ~800–1,500 packages in `node_modules/`. The transitive surface is *the actual* attack/breakage surface — and the kit cannot enumerate it. No SBOM, no `npm audit` automation. Normal for the JS ecosystem; *the* vector for supply-chain attacks. Ember needs **dependency boundary auditing** as a hard prerequisite for any cloud-tier feature.

### 5.2 The dev-vs-runtime asymmetry

The kit's *dev* dependencies (6) are **smaller** than its *runtime* dependencies (9). Unusual — typical SDKs have larger dev surfaces (test frameworks, codegen, linters). No `jest`, no `vitest`, no `playwright`. The kit is **shipped untested**. Teachable malpractice for a production-grade kit; understandable for a 7-commit teaching demo.

### 5.3 The crisp parts

- **Caret-pinning** is consistent and correct semver discipline.
- **Lock-file committed** — right for an application, wrong for a library; the kit is an application.
- **No optional or peer dependencies declared** — fully self-contained at install.
- **No build-time env-var substitution** — credentials live as code-edits (`README.md:54-65`). Wrong for production, *honest* for teaching (no false sense of security).

---

## 6. Cross-References

- [[10_DOMAIN_MAP]] §3 for the dependency graph as it intersects the file structure
- [[11_DUAL_MODE_PATTERN]] §2 for how the dual-SDK shape enables the dual-mode pattern
- [[20_ZEROWEIGHT_SURFACE]] for the proprietary surface this stack delivers
- [[21_LIVEKIT_INTEGRATION]] for the MIT realtime media foundation
- [[50_DEPENDENCY_HEALTH]] (Auditor) for the threat-shaped reading of these dependencies
- [[52_NO_LICENSE_RISK]] (Auditor) for the no-LICENSE-file kit posture
- [[sap:10_DOMAIN_MAP]] §3 for SAP's much larger Python+JS dependency graph

---

## What This Means for Ember

**Adopt:**
- **The strict TypeScript profile** (`tsconfig.app.json:21-25`: `noUnusedLocals`, `noUnusedParameters`, `erasableSyntaxOnly`, `noUncheckedSideEffectImports`). If Ember ever ships TS, this is the floor. Source: standard TS compiler flags, no kit code attached.
- **The flat-config ESLint shape** with `tseslint.configs.recommended`. The pattern (config-as-module-export, `defineConfig([...])`) is the current ESLint norm and worth using directly.
- **The Vite + React plugin minimal config** (`vite.config.ts:1-10`). Ten lines for a fully working dev server is the bar. Ember's documentation site (if any) should not exceed this footprint.
- **LiveKit Python SDK** for any Ember cloud-tier work. `pip install livekit` + `pip install livekit-api` gives Ember a Funi/Munnr-side WebRTC client without React. Cite LiveKit's MIT license; adopt freely.

**Adapt:**
- **The dev-vs-runtime asymmetry** — adapt by *reversing* it. Ember's dev surface (mypy, ruff, pytest, hypothesis, pre-commit) must be *larger* than its runtime surface. The kit's shipped-untested posture is wrong for Ember. Each cloud-tier feature requires test coverage as a hard gate, not an aspiration.
- **The `package.json:engines` discipline** — adapt to Ember's `pyproject.toml` requiring an explicit Python version range. The kit's silent Node-20-required assumption is the *exact* failure mode `pyproject.toml`'s `python` field exists to prevent. Ember declares; the kit does not.
- **The caret-pin convention** — adapt to Python: prefer `~=` (compatible release) over `^` semantics. For high-brittleness deps (any 0.x equivalent), use exact pins. The kit's `^0.2.38` for ZeroWeight is *under-pinned* for production; Ember adopts the convention but ratchets stricter for any 0.x equivalent.
- **The seven-icons-from-a-thousand pattern** — adapt by *refusing*. Ember inlines icons as SVG strings in a `static/icons/` directory, no icon-library dependency. The kit's `lucide-react` is overprovisioning; Ember rejects.

**Avoid:**
- **0.x packages on the load-bearing path** without a typed adapter and a budgeted-upgrade plan. The kit's `@zeroweight/react` 0.2.38 is on the critical path with no insulation. Ember's cloud-tier features that depend on a 0.x SDK *must* be insulated behind a typed `CloudAvatarProvider` adapter ([[60_REALTIME_TIER_FOR_ANDLIT]]).
- **The 300-KB-for-one-feature dependency pattern** (`framer-motion` for drag). Inline 30 lines instead. Every browser dependency carries weight; Ember's web surface (if any) refuses dependencies whose used-surface is <5% of their shipped surface.
- **The implicit-Node-version assumption.** Document the runtime version explicitly; fail loudly on mismatch. The kit's `Node.js 20+ recommended` (`README.md:39`) is the wrong word — `required`.
- **Shipped untested.** Even a 846-LOC kit deserves a smoke test. Ember refuses untested code in any tier.

**Invent:**
- **The Pluggable Cloud Avatar Provider Vow.** Generalises the Pluggable Storage Vow. Any Ember cloud-tier feature that depends on a third-party cloud SDK declares a typed `CloudAvatarProvider` protocol; the ZeroWeight integration is *one implementation*, alongside hypothetical Heygen, Synthesia, D-ID, or self-hosted-SadTalker implementations. The kit's hard-coupling to `@zeroweight/react` is the failure mode; Ember refuses it. Specifically: the `runAction(name: str)`, `connect()`, `disconnect()`, `toggle_mic()`, `set_volume(v: float)` methods become the protocol; the ZeroWeight adapter wraps `useAvatarSession`'s return shape into the protocol; another provider's adapter would do the same to its own SDK.
- **The Dependency Brittleness Ledger.** Every Ember dependency (Python or JS) carries a one-line brittleness annotation in `pyproject.toml` or equivalent: `# brittleness: high | medium | low`, `# upgrade-cadence: months | quarters | never`. The waifu kit's `package.json` carries no such annotation; Ember refuses opacity about the long-term cost of each dep.
- **The Transitive Risk Surface Audit.** For each Ember top-level dependency, the team produces (at adoption time) a *one-page summary* of: who maintains it, how many transitive deps it pulls, what its primary attack surface is, what the rollback plan is. Stored at `docs/dependencies/<package>.md`. The kit ships no such audit; Ember requires it before any cloud-tier dep lands.
- **The Brittleness Inversion Vow.** Ember refuses to depend hardest on its least-replaceable dependency. If a feature needs a 0.x cloud SDK, the feature is *optional* and *isolated*; if a feature needs a 2.x stable open-source library (like LiveKit), the feature can be load-bearing. The waifu kit gets this exactly backwards: ZeroWeight is load-bearing-and-fragile; LiveKit is non-load-bearing-and-stable. Ember inverts.
- **The ESM-First Manifest.** When Ember ships JS, it ships ESM-only with explicit Node engine declarations. The transition cost is the user's, paid once, in exchange for not perpetuating CJS. The kit gets this right by accident; Ember gets it right on purpose.
