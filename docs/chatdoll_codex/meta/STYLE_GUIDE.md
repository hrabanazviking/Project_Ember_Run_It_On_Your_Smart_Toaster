---
name: chatdoll-codex-style-guide
description: Voice, tone, length, citation rules, and closer format for every Chatdoll Codex document
metadata:
  codex: chatdoll
  type: meta
---

# STYLE_GUIDE — Chatdoll Codex

Read before authoring. Binding.

---

## 1. Length

**Target:** 1,500–4,000 words per content doc (back to SAP range; source is 18k LOC).
**Floor:** 1,500.
**Ceiling:** 4,000. Above this, split (`<slug>_A.md` / `<slug>_B.md`) and update MANIFEST.

Some docs (like `66_JAPANESE_VOICE_INTEGRATION.md` or `60_TRIANGULATION.md`) may justify the upper bound. Most should land at 2,000–3,000.

## 2. Voice

Same family as the SAP / Waifu codexes. Technical + entertaining + insight-rich. The reader is Volmarr at 2am.

Avoid: corporate dead language, marketing tone, filler, generic warnings.
Prefer: concrete subject + verb + object; one idea per paragraph; named modules; specific failure modes.

## 3. Structure

Standard skeleton:

```markdown
# <Title>

> *<Optional epigraph>*

<2–4 sentence opening>

## <Section 1: The Subject>
## <Section 2: How It Works>
## <Section 3: Where It Breaks / Where It Surprises>
## <Section 4: Cross-References>

## What This Means for Ember

**Adopt:** <Apache-2.0 sources — cite + adapt with attribution>
**Adapt:** <patterns to take and transform>
**Avoid:** <patterns to reject, with reason>
**Invent:** <novel patterns this analysis suggests>
```

Mandatory closer. Each list at least one entry — if you can't fill one, write "(none from this lens)" with one-line reason.

## 4. Citation

Real `path:line` from `/tmp/ChatdollKit/`:

```
`/tmp/ChatdollKit/Scripts/AIAvatar.cs:142` — main update dispatch
`/tmp/ChatdollKit/Scripts/LLM/ChatGPT/ChatGPTService.cs:88` — function-call adapter
```

For sister projects:
```
`/tmp/chatmemory/server/main.py:50` — episodic store route
```

For Unity-specific concepts (asmdef, MonoBehaviour lifecycle, prefab), cite Unity official docs by URL when needed.

For C# specifically: cite class + method, e.g. `ChatGPTService.GenerateAsync at ChatGPTService.cs:88-105`.

README claims marked `[unverified — README claim only]`.

## 5. The "What This Means for Ember" Closer

Apache-2.0 license posture means Adopt is generous (with attribution). Examples:

**Good:**
> "Adopt CDK's tag-extraction pattern `Regex.Matches(text, @"\[anim:(\w+)\]")` (ChatdollKit `Scripts/Model/ModelController.cs:240`, Apache-2.0 attribution required) into Ember's Munnr as `extract_animation_tags()`."

**Bad:**
> "Adopt CDK's tag-extraction pattern" (no location, no attribution)

At least one **Invent** per doc.

## 6. Cross-Linking

Within: `[[slug]]`. Across: `[[sap:slug]]`, `[[waifu:slug]]`, `[[hermes:slug]]`, `[[peer:slug]]`, `[[kloinn:slug]]`, `[[ember:slug]]`.

Synthesis docs especially should cross-link to SAP and Waifu for triangulation. Aim for at least one cross-codex link per doc.

## 7. Code Excerpts

Quote real code where instructive. C# excerpts ≤25 lines per block:

```csharp
// /tmp/ChatdollKit/Scripts/Model/ModelController.cs:240-260
public void RegisterGesture(string name, AnimationClip clip) {
    ...
}
```

## 8. Apache-2.0 Attribution Standard

Per doc, when proposing Adopt-list entries derived from CDK:

- Add a footer note: *"Apache-2.0 attribution: when adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c)."*
- This is a once-per-doc note, not per-line.

## 9. Three-Corpus Cross-Reference

Every domain doc should reference at least one SAP slug and one Waifu slug for triangulation. Synthesis docs should cite all three corpora liberally.

Examples:
- `12_MODEL_CONTROLLER_DOMAIN.md` should cross-ref `[[sap:11_AVATAR_DOMAIN]]` + `[[waifu:20_ZEROWEIGHT_SURFACE]]`
- `16_LLM_SERVICE_DOMAIN.md` should cross-ref `[[sap:21_OPENAI_COMPAT_API]]` + `[[waifu:21_LIVEKIT_INTEGRATION]]`

## 10. Continuation Notes

If you run out of budget mid-doc, leave a `## Continuation Notes` block at the bottom. No silent truncation.

## 11. Voice References

Calibrate against:
- SAP Codex `00_vision/`, `10_domain/`, `30_execution/`, `60_synthesis/` — same voice family
- Waifu Codex any layer — same family, smaller scale

## 12. The Reader

Volmarr at 2am with ADHD, half-empty mug, asking *"is Unity worth committing to as Ember's third embodiment runtime — and what do I learn from the Japanese voice ecosystem that the SAP and Waifu corpora missed?"*

Answer that question.
