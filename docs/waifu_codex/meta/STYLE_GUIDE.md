---
name: waifu-codex-style-guide
description: Voice, tone, length, citation rules, and closer format for every Waifu Codex document
metadata:
  codex: waifu
  type: meta
---

# STYLE_GUIDE — Waifu Codex

Read before authoring. Binding.

---

## 1. Length

**Target:** 1,500–3,000 words per content doc.
**Floor:** 1,500 words. Below this you are summarizing, not teaching.
**Ceiling:** 3,000 words. Above this, split (`<slug>_A.md` / `<slug>_B.md`) and update MANIFEST.

Tighter than SAP's 1,500–4,000 range. Source is 846 LOC — there isn't padding-worth material to fill 4,000-word docs honestly.

## 2. Voice

Same family as SAP Codex (which is the same family as Hermes Codex). Technical + entertaining + insight-rich. The reader is Volmarr at 2am.

Avoid: corporate dead language, marketing tone, filler, generic warnings.
Prefer: concrete subject + verb + object; one idea per paragraph; named modules; specific failure modes.

## 3. Structure

Every content doc follows the skeleton from SAP STYLE_GUIDE §3 (adapted):

```markdown
# <Title>

> *<Optional epigraph>*

<2–4 sentence opening: what this doc is about, what the reader gains>

## <Section 1: The Subject>
<What it is, where it lives, cite files>

## <Section 2: How It Works>
<Mechanism, cite lines>

## <Section 3: Where It Breaks / Where It Surprises>
<Brittle, leaky, clever-in-the-wrong-way>

## <Section 4: Cross-References>
<[[slug]] within; [[sap:slug]] for SAP comparison>

## What This Means for Ember

**Adopt:** <patterns to take wholesale — bias toward LiveKit (MIT) or invented patterns; never kit code without license clarification>
**Adapt:** <patterns to take and transform, transformation specified>
**Avoid:** <patterns to reject, with reason>
**Invent:** <novel patterns this analysis suggests but the kit did not implement>
```

The closer is **mandatory**. Each list must have at least one entry — if you can't fill one, write "(none from this lens)" and explain in one line.

## 4. Citation

**Kit citations** (study-only, no license):
```
`/tmp/waifu-chat-starter-kit/src/modes/AdvancedMode.tsx:142` — `onAction` handler dispatches typed action
```

**LiveKit citations** (MIT, cite freely):
- For protocol/spec claims: official docs URLs acceptable
- For source claims: `livekit/livekit:livekit-server/<path>:line` or similar if cloned

**ZeroWeight SDK citations** (proprietary, mostly inaccessible):
- Cite kit's *usage* + mark `[interface-only — proprietary SDK]`
- TypeScript types from `node_modules/@zeroweight/react/` are fair game if accessible
- README claims marked `[unverified — README claim only]`

## 5. The "What This Means for Ember" Closer

Critical for this codex due to license posture:

- **Adopt** entries must **prefer LiveKit (MIT)** as the upstream, OR Ember-invented patterns. Kit-derived adoption requires `[license-pending]` annotation
- **Adapt** entries can adapt *patterns* (architecture, vocab shape, dual-mode arrangement) freely — adapting code is restricted
- **Avoid** entries name the failure mode the kit's pattern embodies
- **Invent** entries name patterns not in the kit but visible because of it

Be specific. "Adopt LiveKit Room model" is useless. "Adopt LiveKit's `Room.connect()` lifecycle with `disconnect` handler pattern (livekit-client docs), but bind it to Ember's Andlit-realtime as a typed `CloudSession` resource that auto-revokes on context exit" is the bar.

## 6. Cross-Linking

Within: `[[slug]]`. Across: `[[sap:slug]]`, `[[hermes:slug]]`, `[[peer:slug]]`, `[[kloinn:slug]]`, `[[ember:slug]]`.

Forward-link liberally — Scribe verifies all links resolve on final pass.

## 7. Code Excerpts

The kit is 846 LOC total. Excerpts are fine but use restraint:

```typescript
// /tmp/waifu-chat-starter-kit/src/modes/BasicMode.tsx:1-31 (full file)
import { LiveKitAvatarSession } from '@zeroweight/react'
...
```

Quoting the full 31-line `BasicMode.tsx` once (in `30_BASIC_MODE_FLOW.md`) is acceptable since it's load-bearing for the analysis.

## 8. License-Aware Phrasing

When discussing adoption candidates:

**Good:**
> "LiveKit's `Room.connect()` pattern (MIT) maps cleanly to Ember's proposed `CloudSession` resource. The kit's `AdvancedMode.tsx:88` shows one usage, but the upstream is what Ember should reference."

**Bad:**
> "We should copy the kit's `AdvancedMode.tsx:88` connection code."

The first cites the kit for context; the second proposes code adoption without license confirmation.

## 9. SAP Cross-Reference

This codex's whole purpose is the local↔cloud axis. Cross-link to SAP Codex liberally:

- `[[sap:11_AVATAR_DOMAIN]]` — SAP's local domain
- `[[sap:25_AVATAR_PROTOCOL]]` — SAP's protocol
- `[[sap:32_AVATAR_RENDER_PIPELINE]]` — SAP's render
- `[[sap:60_TRUE_NAME_REASSIGNMENT]]` — Andlit/Rödd
- `[[sap:63_PERFORMANCE_TIER_ENGINE]]` — the T0-T4 ladder

Every doc that touches embodiment should reference at least one SAP slug for comparison.

## 10. Continuation Notes

Same as SAP STYLE_GUIDE §10. If you run out of budget mid-doc, leave a `## Continuation Notes` block. No silent truncation.

## 11. Voice References

Calibrate against:
- SAP Codex `00_vision/` (Skald voice)
- SAP Codex `10_domain/` (Architect voice)
- SAP Codex `50_verification/` (Auditor voice)
- SAP Codex `30_execution/` (Forge voice)
- SAP Codex `60_synthesis/` (synthesis voice)

This codex is a sibling of SAP — same voice family, complementary subject.

## 12. The Reader

Volmarr at 2am with ADHD, half-empty mug, asking *"is the cloud-tier worth it for Ember, and if so, how do we do it safely?"*

Earn the attention. Answer the question.
