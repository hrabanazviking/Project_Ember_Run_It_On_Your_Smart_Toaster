---
name: waifu-codex-shared-context
description: Briefing every Mythic Engineering agent reads before authoring any waifu_codex document
metadata:
  codex: waifu
  type: meta
---

# SHARED_CONTEXT — Waifu Codex

Read this before authoring any doc. This is the common ground.

---

## 1. What the Waifu Chat Starter Kit Is

**Repository:** `ZeroWeight-Engineering/waifu-chat-starter-kit` — cloned at `/tmp/waifu-chat-starter-kit/`
**Stars/forks:** 74 / 21 at time of study
**Commits:** 7 total (very young)
**License:** **NONE — no LICENSE file in repo.** This is critical (see §6 below)
**Self-description:** "A React + Vite starter for building an anime-style AI avatar chat experience with the ZeroWeight avatar SDK and LiveKit."

**Total size:** 846 LOC across all source + CSS files. TypeScript LOC alone: ~269. Five source files:
- `src/main.tsx` — Vite entrypoint
- `src/App.tsx` (50 LOC) — mode switcher + top-level wrapper
- `src/index.css` — global styling
- `src/modes/BasicMode.tsx` (31 LOC) — minimal embedded avatar session
- `src/modes/AdvancedMode.tsx` (188 LOC) — custom UI with controls (timer, mic toggle, volume toggle, action triggers)
- `src/modes/AdvancedMode.css` (379 LOC) — heavy styling

**What it actually is:** a thin glue layer between two cloud services:
- **`@zeroweight/react` + `@zeroweight/renderer`** (proprietary) — cloud-rendered anime avatar SDK
- **`@livekit/components-react` + `livekit-client`** (MIT-licensed) — WebRTC realtime media for audio in / audio+video out

The kit is *intentionally small*. It's a teaching/demo asset for ZeroWeight's commercial SDK. The interesting content for Ember is **not in the kit's 846 LOC** — it's in the *architectural choice* the kit demonstrates (realtime cloud avatar streaming) and the *upstream surfaces* it integrates (LiveKit, ZeroWeight).

## 2. What Ember Is

Same as the SAP Codex's SHARED_CONTEXT §2 — small-and-tethered AI agent at `~/ai/ember`, Six True Names (Funi/Strengr/Brunnr/Smiðja/Hjarta/Munnr), doc-rich + code-empty, ratification-gated slice plan since 2026-05-21.

Wave 3 (SAP Codex) recently proposed three additional True Names: **Andlit** (face/avatar), **Rödd** (voice), **Hugarsýn** (mind-sight). The Cartographer recommended adopting **Hugarsýn** fully and **reserving** Andlit + Rödd pending the embodiment slice. **This codex is the embodiment slice's source material for the realtime/cloud tier.**

## 3. What This Codex Is For

To answer one specific question Ember has not yet honestly addressed:

> *"When is local avatar rendering not enough? What does it look like to stream Ember's embodiment to a cloud-rendered avatar — and when should we?"*

The SAP Codex covered **local** avatar embodiment (VRM, Live2D, VTube Studio — Ember owns the assets, Ember renders, the avatar lives on the host). This codex covers **realtime cloud** embodiment (Ember sends audio/intent to a cloud service, a cloud avatar is rendered, the user's browser receives a media stream).

Both are legitimate. Both have failure modes. Both have privacy implications. Ember's design needs to know when to use which — and how they relate to **Tiered Presence** (the SAP-proposed Vow).

## 4. How to Cite

Per STYLE_GUIDE §4. Every claim about the kit cites real source files:

```
`/tmp/waifu-chat-starter-kit/src/modes/AdvancedMode.tsx:142` — action trigger handler
```

For LiveKit references (MIT, mineable freely), cite either:
- LiveKit's open-source repos (link or path if cloned)
- LiveKit official documentation (URL acceptable for protocol/spec claims)

For ZeroWeight SDK references (proprietary, npm 403'd, cannot read source directly), cite either:
- The kit's *usage* of the SDK (`AdvancedMode.tsx:88` calls `useAvatarSession()`)
- The TypeScript types as visible in `node_modules/@zeroweight/react/` if available
- Mark as `[interface-only — proprietary SDK]` if no source citation possible

README claims are marked `[unverified — README claim only]`.

## 5. Style — The "What This Means for Ember" Closer

Per STYLE_GUIDE §5. Every doc ends with:

```
## What This Means for Ember

**Adopt:** <patterns to take wholesale — strongly biased toward LiveKit (MIT), not kit code>
**Adapt:** <patterns to take and transform, with the transformation specified>
**Avoid:** <patterns to reject, with the reason>
**Invent:** <novel patterns this analysis suggests, named>
```

**Critical license-aware constraint:** "Adopt" recommendations must prefer LiveKit (MIT) or self-invented Ember patterns. Adopting *kit code* requires explicit license clarification — flag with `[license-pending]` if proposed.

## 6. License Posture — STUDY-ONLY

The waifu-chat-starter-kit ships with **no LICENSE file**. Per Ember's Open Knowledge Vow, this means:

- **Study freely** — read the code, learn from the patterns, cite the lines
- **Do not vendor** — no code from the kit lives in Ember
- **Adopt-list cautious** — Adopt-list entries must prefer the upstream LiveKit (MIT) or invented-by-Ember patterns
- **Adapt-list acceptable** — adapting a *pattern* (the dual-mode architecture, the action protocol shape) is fine; adapting *code* is not
- **Cite carefully** — citations are for understanding, not for borrowing

If a clear MIT/Apache license appears for the kit during the study, this posture relaxes. Until then: study-only.

## 7. Cross-Linking Convention

Within the codex use `[[slug]]`. Example: `[[60_REALTIME_TIER_FOR_ANDLIT]]`.

Cross-codex (heavily used for the SAP comparison):
- `[[sap:11_AVATAR_DOMAIN]]` — SAP's local avatar domain
- `[[sap:25_AVATAR_PROTOCOL]]` — SAP's avatar protocol surface
- `[[sap:32_AVATAR_RENDER_PIPELINE]]` — SAP's local render pipeline
- `[[sap:60_TRUE_NAME_REASSIGNMENT]]` — Andlit/Rödd proposal
- `[[sap:63_PERFORMANCE_TIER_ENGINE]]` — the T0-T4 ladder
- `[[hermes:...]]`, `[[peer:...]]`, `[[ember:...]]` per usual

The Scribe verifies all links resolve on the final pass.

## 8. Threat Awareness

Even at 846 LOC, the kit touches dangerous surfaces:
- **Microphone capture** in the browser
- **Audio streaming to a cloud service**
- **Avatar identity rendered by a third party**
- **Cloud auth tokens** for ZeroWeight + LiveKit
- **Browser permissions** for media access
- **Action vocabulary** as an attack surface (what does the LLM trigger?)

The Auditor's verification docs catalog these. Every doc should at least notice when it's touching dangerous territory.

## 9. Do Not Touch

- Ember source code (`~/ai/ember/src/`, sibling project folders)
- Ember's existing slice plan
- Sibling codexes (Hermes, Peer, SAP, Klóinn)
- Anything outside `docs/waifu_codex/`

Propose changes — never enact them.

## 10. Comparison with SAP — Use It

The SAP Codex (83 docs at `docs/sap_codex/`) is the immediate sibling. Cross-link liberally:
- SAP's local VRM/Live2D ↔ this codex's cloud streaming
- SAP's `vts_manager.py` lip-sync ↔ ZeroWeight's cloud-rendered lip-sync
- SAP's `affection_system.py` (regex on LLM tags) ↔ the kit's *absence* of an affect surface
- SAP's local action triggers via VRM tags ↔ the kit's typed `embarrassed`/`dance`/`wave_hand` action API

The teaching is in the comparison.
