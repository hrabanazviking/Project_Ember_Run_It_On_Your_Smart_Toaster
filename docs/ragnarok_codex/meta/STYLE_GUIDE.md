---
name: ragnarok-codex-style-guide
description: Voice, tone, length, citation, closer format for every Ragnarok Codex document
metadata:
  codex: ragnarok
  type: meta
---

# STYLE_GUIDE — Ragnarok Codex

Read before authoring. Binding.

---

## 1. Length

1,500–4,000 words per content doc. Synthesis docs may run upper end.

## 2. Voice

Same family as prior codexes — technical + entertaining + insight-rich. The reader is Volmarr at 2am.

**Ragnarok-specific addition:** the voice carries Norse weight without becoming pastiche. Cite Old Norse terms with English gloss on first use (e.g., "*Jotenheim* — the giants' realm"). Then drop the gloss for repeated references. Match the Skald's voice in Hermes/SAP/Waifu/Chatdoll for the kinship; lean into Norse content where the source justifies it.

Avoid: LARP-tone ("By Odin's beard...!"), unnecessary romanticism, pastiche; corporate dead language; marketing tone.

## 3. Structure

Standard skeleton with one addition — Norse terms get glossed on first use.

```markdown
# <Title>

> *<Optional epigraph — Old Norse phrase + English translation acceptable here>*

<2–4 sentence opening>

## <Section 1: The Subject>
## <Section 2: How It Works>
## <Section 3: Where It Breaks / Where It Surprises>
## <Section 4: Cross-References>

## What This Means for Ember

**Adopt:** <patterns — for GPL-3 prefer "reimplement from concept; attribution: Ragnarok line N">
**Adapt:** <patterns to take and transform>
**Avoid:** <patterns to reject — including LARP, pastiche, cultural narrowing>
**Invent:** <novel patterns this analysis suggests>
```

Mandatory closer; at least one Invent.

## 4. Citation

```
`/tmp/NorseWorld-Ragnarok/project/Creatures/Brain/SeerBrain.cs:42` — flight heuristic
`/tmp/NorseWorld-Ragnarok/languages/ru_dlg_jarl.xml:14` — jarl dialog root
`/tmp/NorseWorld-Ragnarok/project/Universe/UniverseBuilder.cs:128` — Asgard build
```

For Russian XML, cite even if translating; mark `[translation: ...]`.

README claims marked `[unverified — README claim only]`.

## 5. The "What This Means for Ember" Closer — GPL-3 wording

Because the source is GPL-3 copyleft, Adopt entries must use careful wording:

**Good:**
> "Adopt the cell-based world representation pattern from Ragnarok's `NWField.cs` (GPL-3, attribution required; reimplement from concept rather than vendor) into Ember's Brunnr as a typed `WorldCell` resource."

**Bad:**
> "Copy the NWField class into Ember."

Always: **reimplement from concept**, **attribution required**, **do not vendor**.

## 6. Cross-Linking

Within: `[[slug]]`. Across: `[[hermes:slug]]`, `[[peer:slug]]`, `[[kloinn:slug]]`, `[[sap:slug]]`, `[[waifu:slug]]`, `[[chatdoll:slug]]`, `[[ember:slug]]`.

Synthesis docs should braid prior codexes. Wave 6 closes the first codex collection — cross-references heavy.

## 7. Code Excerpts

C# excerpts ≤25 lines per block. Cite the path on the first line as a comment.

```csharp
// /tmp/NorseWorld-Ragnarok/project/Creatures/Brain/BeastBrain.cs:42-58
public override void Think()
{
    // ...
}
```

## 8. Norse Term Discipline

- **First use:** Old Norse term + brief English gloss in parens or em-dash
  - "*Asgard* — the gods' world, final-battle location"
  - "*Niflheim* (realm of the dead)"
- **Subsequent uses:** bare Norse term OK
- **When Old Norse is essential:** use it (it carries meaning the English doesn't)
- **When English suffices:** use English (don't perform)
- **When in doubt:** gloss

This discipline is what the **Cartographer's `6A_EMBER_CULTURAL_CHARTER.md`** distills as standing rule for Ember.

## 9. Cultural Honesty

This codex sits closer to Ember's own cultural identity than any prior codex. Honesty matters:

- Don't romanticize ("the noble Viking spirit")
- Don't apologize (Norse weight is real; carry it)
- Don't LARP ("Hark! The mead of poetry...")
- Don't narrow (Norse mythology has tragic, weird, queer, dark sides — name them when source does)
- Don't appropriate (Sergey Zhdanovskih is the source author; cite him)

When in doubt, ask: "Would a Norse studies professor wince at this paragraph?"

## 10. Continuation Notes

If you run out of budget mid-doc, leave a `## Continuation Notes` block. No silent truncation.

## 11. Voice References

- Hermes Codex `00_vision/` — original Skald voice
- SAP Codex `60_synthesis/` — synthesis tradition
- Waifu Codex `meta/STYLE_GUIDE.md` — license-aware closer pattern (different license here — GPL-3 not no-LICENSE)
- Chatdoll Codex `60_synthesis/60_TRIANGULATION.md` — multi-corpus braid

## 12. The Reader

Volmarr at 2am with ADHD, half-empty mug, asking *"What does Norse mythology systematized in software teach Ember about being itself? And what should I refuse from the LARP-adjacent territory?"*

Answer that question.
