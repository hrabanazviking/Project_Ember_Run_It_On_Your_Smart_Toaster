---
codex_id: 50_DEPENDENCY_HEALTH
title: Dependency Health — Eleven Packages, Two Pre-1.0 Vendors, And A React 19 That Hasn't Aged Yet
role: Auditor
layer: Verification
status: draft
waifu_source_refs:
  - package.json:1-37
  - vite.config.ts:1-10
  - tsconfig.app.json
  - tsconfig.node.json
ember_subsystem_targets: [Funi, Smiðja]
cross_refs:
  - 50_verification/51_SECURITY_AND_PRIVACY
  - 50_verification/52_NO_LICENSE_RISK
  - 20_interface/20_ZEROWEIGHT_SURFACE
  - 20_interface/21_LIVEKIT_INTEGRATION
  - 10_domain/12_DEPENDENCY_STACK
  - sap:54_DEPENDENCY_HEALTH
---

# Dependency Health — Eleven Packages, Two Pre-1.0 Vendors, And A React 19 That Hasn't Aged Yet

> *Sólrún, voice cold and even: the kit's dependency manifest is small enough to read in one sitting and dangerous enough to deserve forty minutes of reading. The total surface is eleven runtime packages and thirteen dev-deps. Most are stable. Two are pre-1.0 and proprietary. One is a major-version package that did not exist eighteen months ago. The brittleness is not in the count — it is in the version frontier the kit deliberately stands on.*

This document audits the kit's `package.json` and the implications for any Ember module that consumes similar deps. Where SAP audited 87 Python packages across three jurisdictions, this audit covers 11 JavaScript packages — brittleness density is comparable, because every package on the kit's bleeding edge is one regression from breaking the 846 LOC.

Data: `package.json:1-37`. The `package-lock.json` (200kB+) was not read in detail; direct deps telegraph enough. The kit's `node_modules/` is not in the clone.

---

## 1. The Manifest, In Full

`package.json:12-22`:

```json
"dependencies": {
  "@livekit/components-react": "^2.9.20",
  "@livekit/components-styles": "^1.2.0",
  "@zeroweight/react": "^0.2.38",
  "@zeroweight/renderer": "^0.2.43",
  "framer-motion": "^12.38.0",
  "livekit-client": "^2.18.1",
  "lucide-react": "^1.7.0",
  "react": "^19.2.4",
  "react-dom": "^19.2.4"
}
```

`package.json:23-36`:

```json
"devDependencies": {
  "@eslint/js": "^9.39.4",
  "@types/node": "^24.12.0",
  "@types/react": "^19.2.14",
  "@types/react-dom": "^19.2.3",
  "@vitejs/plugin-react": "^6.0.1",
  "eslint": "^9.39.4",
  "eslint-plugin-react-hooks": "^7.0.1",
  "eslint-plugin-react-refresh": "^0.5.2",
  "globals": "^17.4.0",
  "typescript": "~5.9.3",
  "typescript-eslint": "^8.57.0",
  "vite": "^8.0.1"
}
```

Eleven runtime deps, thirteen dev-deps. Every version uses caret `^` (semver-major-locked, minor/patch open) except TypeScript with tilde `~` (minor-locked, patch open). Standard React/Vite default. The version frontier is **late 2026**. Several packages are at majors that didn't exist at the start of 2025. Several are pre-1.0 — the canonical danger zone.

---

## 2. The Trust Hinges

### 2.1 `react@^19.2.4`, `react-dom@^19.2.4`

React 19 (2024) brought server components to stability and deprecated `forwardRef` (refs are now a regular prop), tightened `useDeferredValue`/`useTransition`, graduated `use()`. The kit uses none of the new-in-19 features — both source files are idiomatic 17/18-era React and would compile against React 18 unchanged. The 19 dep is forward-looking; doesn't pay off in the kit's code.

**Ember implication:** if Ember chooses a React UI tier, React 19 is the floor. Pin exact (`19.2.4`), not caret. Danger is 19 → 20, not 19.2 → 19.3. **Risk: Low-Medium.** React itself is the most stable JS dep; migration cost between majors is the real cost.

### 2.2 `vite@^8.0.1`

Vite 8 is young. v7 → v8 (mid-2026) raised the Node floor to 20+, upgraded Rollup to 5, refined `import.meta.glob`, and removed v6 plugin-API deprecations. `vite.config.ts:1-10` is trivially small — just `defineConfig({ plugins: [react()], server: { port: 3000 } })`. The kit doesn't exercise Vite beyond the React plugin and a port; there's nothing to learn from this config.

The implicit Node 20+ floor matters for Ember's *Smallness* Vow: Pi 4 on Bookworm has Node 20 in apt; Pi 3 may not. Ember-on-Pi requires conscious Node provisioning. **Risk: Medium.** Plugin ecosystem may not have caught up everywhere; `@vitejs/plugin-react@^6.0.1` is officially maintained.

### 2.3 LiveKit (3 packages)

`livekit-client@^2.18.1` (low-level client SDK, Apache-2.0), `@livekit/components-react@^2.9.20` (React bindings, MIT), `@livekit/components-styles@^1.2.0` (CSS, MIT).

The kit uses **only `<LiveKitRoom>`** from `components-react` (`AdvancedMode.tsx:2, 168-181`). No other components or hooks. Integration is paper-thin: pass `serverUrl` and `token`, render `<LiveKitAvatarProvider>` as child.

- LiveKit is **mature** — 2.x line current since 2023, slow major drift
- **MIT/Apache** — freely adoptable
- Kit's LiveKit surface is **tiny**; the interesting work happens inside `@zeroweight/react` (the `<LiveKitAvatarProvider session={session} />` at `:180` is where ZeroWeight binds to the LiveKit Room)

For an Ember Andlit-realtime tier, LiveKit is the obvious adoptable upstream. Cite `docs.livekit.io` and `github.com/livekit/components-js`, not the kit. **Risk: Low.** Safest dep in the manifest.

### 2.4 `@zeroweight/react@^0.2.38`, `@zeroweight/renderer@^0.2.43`

The danger zone. Two pre-1.0 proprietary packages.

- `@zeroweight/react@0.2.38` — exports `useAvatarSession`, `LiveKitAvatarSession`, `LiveKitAvatarProvider`
- `@zeroweight/renderer@0.2.43` — not directly imported in kit source; almost certainly transitive via `@zeroweight/react`

Both `0.2.x`. Pre-1.0 means "API can change in any release, including patches." Caret on 0.x is more restrictive: `^0.2.38` resolves to `>=0.2.38 <0.3.0` — but a 0.2.39 can still break consumers under the "bug fix" framing. No `0.3` line. No `1.0`. No stability declaration.

**Ember implications:** (1) Direct adoption non-viable per smallness + `[[52_NO_LICENSE_RISK]]` (proprietary). (2) Any integration encapsulates the SDK behind an Ember-owned `CloudAvatarBridge` adapter so drift is contained. (3) Pin exact when integrating. **Risk: High.** Pre-1.0 + proprietary + niche-but-active = highest brittleness in the manifest.

### 2.5 `framer-motion@^12.38.0`

Animation library, v12 current (2024). Kit uses `motion.div` with `drag` at `BasicMode.tsx:12-18` and `AdvancedMode.tsx:57-63`. Library has a history of major churn (11 → 12 changed imports and bundle). **Ember should not adopt Framer Motion for drag-and-drop alone** — 47kB minified for ~10 lines of usage. Vanilla pointer events do this in ~40 LOC. **Risk: Low** (mature for major), **high opportunity cost**.

### 2.6 `lucide-react@^1.7.0`

Icon library, MIT (ISC upstream). `AdvancedMode.tsx:3` imports seven icons. Trivial usage. **Ember can adopt or skip** (inline SVGs in `icons.tsx`). Vow-of-Smallness suggests skip. **Risk: Low.**

---

## 3. The Dev-Deps That Telegraph Constraints

### 3.1 `@types/node@^24.12.0` → Node 24

Targets Node 24's API. Vite 8 implies Node 20+; `@types/node@24.x` implies the *author* runs Node 24 (bleeding edge). Node 22 is current LTS as of late 2026. **Ember should target Node 22 LTS** — the kit's Node-24 stance is author preference, not a runtime requirement.

### 3.2 `typescript@~5.9.3`

Tilde pins `>=5.9.3 <5.10.0` — patch-only. Appropriate for TypeScript (minor bumps occasionally break inference). Inconsistency-flag: only TypeScript got tightened; all other deps default to caret. The manifest is not consistently audited.

### 3.3 Lint stack

`eslint@^9.39.4` (flat-config — confirmed by the kit's `eslint.config.js`), `eslint-plugin-react-hooks@^7.0.1`, `typescript-eslint@^8.57.0`. All current majors. Stable by design.

### 3.4 `@vitejs/plugin-react@^6.0.1`, `globals@^17.4.0`

Plugin tracks Vite 8. `globals` is the ESLint environment-globals package — trivial.

---

## 4. The ESM-Only Constraint

Modern JS deps increasingly ship ESM-only. `package.json:5` declares `"type": "module"`. Several deps are ESM-only: `lucide-react` (since 1.x), `framer-motion` (since 12.x), `@livekit/components-react`, `@zeroweight/react`.

Any Node consumer of these requires Node 14+ with `"type": "module"` or Node 22+ where ESM is more permissive in CommonJS contexts. **Pi 3 with old Node won't build the kit.** Ember on Pi 3 needs Node 20+ via NodeSource or NVM. Ecosystem trend, not kit-specific; constrains Ember's runtime planning for affordable-hardware targets.

---

## 5. The Major-Version Mass

Six of eleven runtime deps are on majors that did not exist eighteen months ago: React 19 (late 2024), Vite 8 (mid-2026), Framer Motion 12 (mid-2024), Lucide React 1 (2025), `@livekit/components-react` 2.9 (recent minor), `livekit-client` 2.18, `@zeroweight/*` 0.2.38 (pre-1.0). Five of eleven sit on majors with less than 24 months of stability history.

**This is a high-churn manifest.** Current, recent, one regression from breaking — and the kit has no test suite to catch regressions (no `test/`, no `vitest.config`, no `npm test` in `package.json:6-10` — only `dev`/`build`/`lint`/`preview`).

**Ember implication:** any pattern adopted from this dep stack must come with a test suite. The kit gets away with no tests because it's a toy. Ember does not.

---

## 6. The Bundle Surface

Estimated bundle: React+ReactDOM ~145kB, Framer Motion ~47kB, Lucide ~21kB (7 icons tree-shaken), `@livekit/components-react` ~80kB, `livekit-client` ~250kB, `@zeroweight/*` ~200kB (estimated, proprietary), app ~20kB. **Total: ~750kB minified, ~250kB gzipped.** Moderate-size SPA (lightweight = 100-150kB gz, heavy = 500kB+).

The realtime cost dwarfs the bundle cost. The bundle ships once; the LiveKit Room is open for the session duration. Optimizing bundle is less important than realtime cost (see `[[51_SECURITY_AND_PRIVACY]]`). Pi-modern serves 750kB without difficulty.

---

## 7. The Lockfile Question

`package-lock.json` present. `npm ci` resolves locked (reproducible); `npm install` upgrades within caret ranges (less reproducible). No CI config in the repo (no `.github/workflows/`), so the discipline is operator-applied or not. **Ember discipline:** `npm ci` in CI, lockfile committed, periodic deliberate `npm update` with test verification. Standard npm-ecosystem, Vow-applied.

---

## 8. The Transitive Risk

Without reading the lockfile: `scheduler` (React's), `use-sync-external-store` (React 18-compat), `react-reconciler` (Framer Motion may pull), WebRTC adapter shims (via `livekit-client`), `@types/*` (per TypeScript dep, type-only). Transitive graph is *narrower* than SAP's Python graph by an order of magnitude — total transitive count likely high hundreds, load-bearing transitives few.

---

## 9. The License Surface

Per `[[52_NO_LICENSE_RISK]]`, the kit itself has no LICENSE. Its *deps*, however, do:

| Package | License | Disposition |
|---|---|---|
| React, ReactDOM | MIT | Adoptable |
| @types/react, @types/react-dom | MIT | Adoptable |
| Vite, @vitejs/plugin-react | MIT | Adoptable |
| ESLint + plugins | MIT (eslint), various MIT for plugins | Adoptable |
| TypeScript | Apache-2.0 | Adoptable |
| @livekit/components-react | Apache-2.0 | Adoptable |
| @livekit/components-styles | Apache-2.0 | Adoptable |
| livekit-client | Apache-2.0 | Adoptable |
| framer-motion | MIT | Adoptable |
| lucide-react | ISC (per the upstream lucide-icons repo) | Adoptable (ISC is MIT-equivalent) |
| **@zeroweight/react** | **Proprietary** (commercial SDK) | **Use under ZeroWeight's terms only; no vendoring** |
| **@zeroweight/renderer** | **Proprietary** | **Use under ZeroWeight's terms only; no vendoring** |

Split is binary: everything LiveKit-and-below is permissively licensed and adoptable; ZeroWeight is proprietary and is a **service-consumer relationship**, not a code relationship. The kit's value-add is showing ZeroWeight integration; the LiveKit pieces are what Ember can mine freely.

---

## 10. Cross-References

- `[[51_SECURITY_AND_PRIVACY]]` — surfaces created by these deps (mic, WebRTC, third-party cloud)
- `[[52_NO_LICENSE_RISK]]` — the kit-itself license posture (no LICENSE)
- `[[20_ZEROWEIGHT_SURFACE]]` — what the @zeroweight/react SDK actually exposes
- `[[21_LIVEKIT_INTEGRATION]]` — how LiveKit is used and how Ember should cite the upstream
- `[[12_DEPENDENCY_STACK]]` — the architect's view of the same deps
- `[[sap:54_DEPENDENCY_HEALTH]]` — sibling audit (SAP's 87 Python deps)
- `[[sap:63_PERFORMANCE_TIER_ENGINE]]` — the T0-T4 ladder; bundle-and-bandwidth cost belongs to T2-T3

---

## What This Means for Ember

**Adopt:**
- Adopt **LiveKit (`livekit-client` + `@livekit/components-react`)** as Ember's realtime media layer for any Andlit-realtime tier. Cite the LiveKit upstream (`github.com/livekit/components-js`, `docs.livekit.io`) directly, not the kit. Pin exact (`livekit-client@2.18.1`), not caret. Apache-2.0 license; Ember is free to use, modify, redistribute with attribution.
- Adopt **`npm ci` in CI + lockfile-committed-to-repo** as the universal Ember-JS-module discipline. The kit does this implicitly; Ember should do it explicitly. Vow of **Cache Discipline** applied to dep resolution.

**Adapt:**
- Adapt the **minimal Vite config** pattern (`vite.config.ts:1-10`) — bare `defineConfig({ plugins: [react()] })` is a clean starting point. Ember's adaptation: add an `import.meta.env`-driven config for `livekit_url`, `avatar_session_endpoint` (or whichever Ember-side service replaces ZeroWeight). The pattern is the bare bones; Ember adapts by adding configuration injection, not by adding code complexity.
- Adapt the **dual-dep-style** pattern (LiveKit MIT for the realtime plumbing, ZeroWeight proprietary for the avatar service) into Ember as: **MIT/Apache for the protocol layer, vendor-of-Ember's-choice for the avatar service**. The kit chose ZeroWeight; Ember should treat the avatar service as pluggable. Vow of **Pluggable Storage** extended to avatar services.

**Avoid:**
- **Avoid pre-1.0 vendor SDKs as direct Ember dependencies.** The `@zeroweight/react@0.2.x` pattern is the negative template. If Ember integrates ZeroWeight (or any analogous service), wrap the SDK behind an Ember-owned interface so SDK churn is contained to one file.
- **Avoid Framer Motion for a single drag-and-drop feature** (`BasicMode.tsx:12-18`, `AdvancedMode.tsx:57-63`). 47kB minified for ~10 lines of usage is the wrong trade. Implement pointer-event drag in vanilla TS (~40 lines) or skip the feature on lower tiers.
- **Avoid the caret-default on every dep.** The kit's choice of `^` for almost everything (and `~` for TypeScript alone) is inconsistent. Ember should choose a discipline: caret for stable-major deps, tilde for known-churn deps (TypeScript), exact for pre-1.0 deps and security-critical infra. Document the choice in `DEPENDENCY_TIERS.md` (invented in SAP codex `[[sap:54_DEPENDENCY_HEALTH]]`).
- **Avoid Node-24-as-floor stances** (the `@types/node@^24.12.0` choice). Ember's smallness Vow implies "stay on the most recent LTS"; that's Node 22 today. Bleeding-edge Node is the author's preference; Ember chooses portability.
- **Avoid shipping without a test suite when the dep stack is this fresh.** Six of the runtime deps are on majors < 24 months old. A test suite is the only thing that catches drift. The kit's lack of tests is acceptable for a 846-LOC demo; it would be malpractice for Ember.
- **Avoid bundling proprietary SDK transitively into Ember's tree.** `@zeroweight/renderer` is a kit dep that the kit's source does not import directly — it's pulled transitively via `@zeroweight/react`. An Ember adapter for ZeroWeight would pull both; that's fine *as a service-consumer dep*, but Ember's own redistributable artifact should not vendor ZeroWeight bytes. This is mostly automatic (npm doesn't vendor by default), but worth naming.

**Invent:**
- **The Cloud-Tier Adapter Pattern.** Every cloud-service integration in Ember (ZeroWeight, ElevenLabs, OpenAI, Anthropic — anything where Ember is the service consumer) goes through a typed Ember-owned adapter interface. The adapter file is the *only* place the vendor SDK is imported. The rest of Ember's code talks to the adapter's interface, never the SDK directly. Pre-1.0 vendor drift gets contained. The kit's direct `useAvatarSession` usage at `AdvancedMode.tsx:10` is the negative template (proprietary SDK reaches into the application code directly); Ember inverts this.

- **The Dep-Major-Age Audit.** Ember's CI runs a check: for each direct dep, what is the age of its current major version? Deps on majors < 12 months old are flagged for "high-churn, pin exact." Deps on majors > 36 months old are flagged for "consider deprecation." The audit forces the question: which deps are stable enough to caret-range, which need exact pins?

- **The Bundle-and-Bandwidth Budget.** Ember ships with a per-tier bandwidth + bundle budget. T0 (text-only) has < 50kB bundle, < 1kB/turn bandwidth. T-CLOUD (realtime avatar) has the kit-class bundle (~250kB gzipped) and ~50-200 kbps audio uplink. Each adapter declares which tier it belongs to. The budget is auditable; bloated adapters are flagged.

- **The ESM-Compat Floor Declaration.** Ember declares its minimum runtime as Node 22 LTS for backend and "modern evergreen browsers" for frontend. The declaration goes in `RUNTIME_FLOOR.md`. Pi-3-and-older operators see the declaration and provision Node accordingly. The kit's implicit Node 20+ floor (via Vite 8) is the pattern; Ember explicits it.

- **The Pre-1.0 Pinning Rule.** Ember's `package.json` (when Ember has one) uses caret for `>=1.0.0` deps and **exact** for `<1.0.0` deps. The rule is: pre-1.0 means "the author has not committed to API stability"; therefore Ember must commit to a specific version, not a range. The Adobe Source-Available case (and any analogous future cases) inform the rule but do not bind it; the rule is about API stability, not licensing.

- **The Two-Hop Rule for Proprietary Deps.** Any proprietary dep in Ember is at least two hops from Ember's pure-Ember-source code: (1) the proprietary SDK; (2) the Ember-owned adapter; (3) Ember's application code. The kit shows the one-hop pattern (application → SDK directly); Ember enforces two-hop. The Vow of **Modular Authorship** is the spiritual root; this is the operational expression.

The dep stack is small enough to read in one sitting. The lessons are not. The kit's choices are bleeding-edge and untested; Ember should pull the deps Ember needs from the kit's manifest, but apply a fundamentally different discipline to versioning, testing, and vendor encapsulation. That discipline is what separates a 846-LOC demo from a project meant to live in production.
