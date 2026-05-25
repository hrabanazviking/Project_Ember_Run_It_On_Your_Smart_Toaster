---
name: waifu-codex-manifest
description: Authoritative list of all 21 files in the Waifu Codex (15 content + 6 meta), with slugs, scope, owner role, and target length
metadata:
  codex: waifu
  type: meta
---

# MANIFEST — Waifu Codex

**Total files:** 21 (15 content + 6 meta)
**Target length:** 1,500–3,000 words per content doc (tighter than SAP because source is 846 LOC)
**Citation convention:** `/tmp/waifu-chat-starter-kit/<path>:line` for kit; LiveKit official docs/repo for MIT upstream; `[interface-only]` for proprietary ZeroWeight surface
**Closer:** every content doc ends with `## What This Means for Ember`
**License posture:** study-only (no LICENSE in kit) — see SHARED_CONTEXT §6

---

## meta/ (6 docs — orchestrator + Scribe)

| Slug | Status |
|---|---|
| (root) `TASK_WAIFU_CODEX.md` | ✅ written |
| meta/SHARED_CONTEXT | ✅ written |
| meta/MANIFEST | ✅ written |
| meta/STYLE_GUIDE | ⏳ next |
| meta/INDEX | Scribe final pass |
| meta/READING_ORDER | Scribe final pass |
| meta/CROSS_AGENT_NOTES | Scribe final pass |

---

## 00_vision/ (2 docs — Skald)

| # | Slug | Scope |
|---|---|---|
| 00 | `00_OVERTURE.md` | Why study a 7-commit, 846-LOC kit; the realtime cloud embodiment axis Ember has not yet addressed; what "waifu chat" reveals about the companion paradigm; license-aware study |
| 01 | `01_VISION_SYNTHESIS.md` | What this teaches Ember about cloud-tier presence; how Andlit-realtime + Rödd-realtime fit the Tiered Presence Vow; the local↔cloud axis as a design choice, not a default |

---

## 10_domain/ (3 docs — Architect)

| # | Slug | Scope |
|---|---|---|
| 10 | `10_DOMAIN_MAP.md` | The kit's macro shape: `main.tsx` → `App.tsx` → mode switcher → `BasicMode` / `AdvancedMode` → `@zeroweight/react` + LiveKit. Dependency graph. What each layer owns |
| 11 | `11_DUAL_MODE_PATTERN.md` | `BasicMode` (31 LOC, minimal) vs `AdvancedMode` (188 LOC, custom UI) — the architectural pattern of shipping two integration depths from one codebase. What this teaches about progressive disclosure |
| 12 | `12_DEPENDENCY_STACK.md` | React 19, Vite 8, `@livekit/components-react` 2.9, `@zeroweight/react` 0.2, framer-motion 12, lucide-react 1: what each dep carries, what brittleness it introduces, what an Ember reimplementation would need from each |

---

## 20_interface/ (3 docs — Architect: 2, Auditor: 1)

| # | Slug | Owner | Scope |
|---|---|---|---|
| 20 | `20_ZEROWEIGHT_SURFACE.md` | Architect | What hooks/components `@zeroweight/react` exposes (`LiveKitAvatarSession`, `useAvatarSession`, action APIs) as visible through the kit's usage and TypeScript types. Proprietary surface — `[interface-only]` annotations throughout |
| 21 | `21_LIVEKIT_INTEGRATION.md` | Architect | How the kit uses `@livekit/components-react` + `livekit-client`: Room model, Track model, connection lifecycle, token surface. LiveKit is MIT — cite freely |
| 22 | `22_ACTION_PROTOCOL.md` | Auditor | `embarrassed`, `dance`, `wave_hand`: action vocabulary as a contract. What this teaches about typed avatar action surfaces. Where it's brittle (hardcoded action names; no negotiation; no error on unknown action) |

---

## 30_execution/ (2 docs — Forge)

| # | Slug | Scope |
|---|---|---|
| 30 | `30_BASIC_MODE_FLOW.md` | `BasicMode.tsx` walked end-to-end (it's 31 lines — full coverage feasible). Session lifecycle, what the SDK does invisibly, where the minimal embed pattern starts to crack |
| 31 | `31_ADVANCED_MODE_FLOW.md` | `AdvancedMode.tsx` walked end-to-end (188 LOC). Custom UI elements (timer, mic toggle, volume toggle, action triggers); event handlers; LiveKit Room hooks; how the advanced mode shapes a real production surface |

---

## 50_verification/ (3 docs — Auditor)

| # | Slug | Scope |
|---|---|---|
| 50 | `50_DEPENDENCY_HEALTH.md` | React 19, Vite 8, LiveKit 2.18, ZeroWeight 0.2.38, framer-motion 12, lucide-react 1.7: brittleness map. Major-version risks. ZeroWeight 0.x = breaking-change territory. ESM-only deps |
| 51 | `51_SECURITY_AND_PRIVACY.md` | Mic capture posture; what audio leaves the browser; what tokens are needed (ZeroWeight API key + avatar ID + LiveKit JWT); the cross-origin attack surface; what a malicious cloud avatar could exfiltrate; mitigation paths |
| 52 | `52_NO_LICENSE_RISK.md` | What study-only means in practice. What Ember can and cannot do with the kit's patterns. Why this matters for the Open Knowledge Vow. How to honor citation without inheriting copyright debt |

---

## 60_synthesis/ (2 docs — Cartographer: 1, Scribe: 1)

| # | Slug | Owner | Scope |
|---|---|---|---|
| 60 | `60_REALTIME_TIER_FOR_ANDLIT.md` | Cartographer | The Andlit-realtime tier: when cloud streaming embodiment is appropriate; the local↔cloud decision matrix; integration with the SAP-Codex Tier Engine (T0-T4); proposed Tier-CLOUD as parallel-not-substitute to T0; consent, scope, revocability for cloud presence |
| 61 | `61_DECISIONS_AND_INVENTIONS.md` | Scribe | Combined ADRs (3-5) + invented methods (5-10) — small source justifies combined doc. Hybrid local+cloud avatar handoff; action vocab as Vow-gated tool; cloud-session-as-typed-resource (auto-close); fallback ladder; bandwidth-tier-aware action surface; revocable cloud-session scope token |

---

## Agent Layer Assignments — final

| Agent | Role | Folder(s) | Doc count |
|---|---|---|---|
| 1 | **Skald** — Sigrún Ljósbrá | `00_vision/` | 2 |
| 2 | **Architect** — Rúnhild Svartdóttir | `10_domain/` (3) + Architect-owned `20_interface/` (2) | 5 |
| 3 | **Cartographer** — Védis Eikleið | Cartographer-owned `60_synthesis/` (1) | 1 |
| 4 | **Forge** — Eldra Járnsdóttir | `30_execution/` (2) | 2 |
| 5 | **Auditor** — Sólrún Hvítmynd | `50_verification/` (3) + Auditor-owned `20_interface/` (1) | 4 |
| 6 | **Scribe** — Eirwyn Rúnblóm | Scribe-owned `60_synthesis/` (1) + meta finalization (3) | 1 + 3 = 4 |

**Total content authored by agents:** 15 docs across 6 roles. Single Forge instance (no A/B split — only 2 execution docs).

**Push cadence:** orchestrator commits + pushes per layer after all agents return. Scribe's final-pass meta docs (INDEX/READING_ORDER/CROSS_AGENT_NOTES) get one more commit.

---

## Reading Order (preliminary — Scribe finalizes in `meta/READING_ORDER.md`)

1. `meta/SHARED_CONTEXT`
2. `00_vision/00_OVERTURE` → `01_VISION_SYNTHESIS`
3. `10_domain/10_DOMAIN_MAP` → `11_DUAL_MODE_PATTERN` → `12_DEPENDENCY_STACK`
4. `20_interface/20-22`
5. `30_execution/30-31`
6. `50_verification/50-52` for the threat-shaped view
7. `60_synthesis/60` → `61` (the synthesis is the prize)

---

## Slug Glossary (cross-codex prefix)

- `[[hermes:<slug>]]` → `docs/hermes_codex/`
- `[[peer:<slug>]]` → `docs/peer_codex/`
- `[[sap:<slug>]]` → `docs/sap_codex/`
- `[[kloinn:<slug>]]` → `docs/kloinn/`
- `[[ember:<slug>]]` → `~/ai/ember/` root or `docs/` root
- `[[waifu:<slug>]]` → this codex (bare `[[slug]]` also resolves within-codex)
