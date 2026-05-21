# 61 — Runic Typography

How we use runes as ornament. The rule: **runes are decoration, not
content**. Stofa never makes the operator read runic text to use
Stofa.

---

## What runic typography is for

Three uses, in this order of importance:

1. **Chrome separator** — a small `ᛞ ᛞ ᛞ` motif in the chrome
   header signals "this is Stofa." Like a watermark.
2. **Specific contextual ornaments** — one rune at a key moment
   (Hjarta wizard title gets `ᛟ`, the heritage rune).
3. **Pet sprite detail** — a few pet sprites incorporate a rune-like
   glyph as decorative texture (Ask-sapling's bark pattern).

It is NOT for:

- Section headers ("ᛒᛖᚷᛁᚾ" instead of "Begin"). No.
- Status labels ("ᛗᛁᛞᚷᚨᚱᛞ" instead of "Midgard"). No.
- Button labels. No.
- Operator-facing text of any kind. No.

If an operator who knows zero runic alphabets can't navigate Stofa,
we've failed. They will see one or two runes as ornament. They'll
never need to decode anything.

---

## Which runes we use

The Elder Futhark (24 runes) is the canonical Norse alphabet. We
draw from it for ornament. Specifically:

| Rune | Meaning | Used as ornament for |
|---|---|---|
| **ᛞ** (Dagaz) | day / dawn / new beginning | chrome separator |
| **ᛟ** (Othala) | heritage / ancestral home | Hjarta wizard title |
| **ᛏ** (Tiwaz) | the god Tyr / justice | pet sprite detail (Ask-sapling) |
| **ᛒ** (Berkano) | birch / nurturing | (V2 if needed) |
| **ᚹ** (Wunjo) | joy / harmony | (V2 if needed) |

We avoid runes that *could* be mistaken for letters by an operator
who doesn't know runic (the operator might read `ᛚ` and confuse it
with an "l"). The five chosen above have distinctive shapes that
look like ornament, not text.

---

## The chrome separator

Used in the chrome header to subtly visually-divide the title from
the screen-specific content:

```
┌── Stofa ─── ᛞ ᛞ ᛞ ─── Conversation ──── 🔥 ─────────┐
```

The `ᛞ ᛞ ᛞ` sits in the chrome border (top of each screen). Three
runes, separated by spaces. Single-line, never multi-line.

ASCII fallback:
```
+-- Stofa --- *** --- Conversation ---- ^ ----------+
```

The `***` replaces `ᛞ ᛞ ᛞ`. The asterisks read as ornament, not
content.

---

## The Hjarta wizard title

The first-launch identity wizard gets a single ornamental rune in
its title:

```
┌── ᛟ ── Hjarta ── First settings ────────┐
```

`ᛟ` is Othala, the rune of heritage and ancestral home. Fitting for
the moment when the operator names Ember and assigns identity.

This is the only screen-specific ornamental rune in V1.

---

## Pet sprite detail

Some pet sprites use rune-shaped glyphs as **decorative texture**, not
as readable content. Example: Ask-sapling's trunk has subtle
markings that look like runes carved into bark:

```
   .
  /|\
 / | \
   |
   ᛏ        ← decorative bark detail
   |
  / \
 /   \
```

This is a stylization. An operator who doesn't know runes sees "a
small mark on the trunk." An operator who knows runes recognizes
Tiwaz. Both are happy.

---

## What we explicitly reject

- **All-runic UI text.** "ᚺᛖᛚᛚᛟ ᚹᛟᚱᛚᛞ" as a greeting. No.
- **Runic alphabet picker.** Settings option to "render all text in
  runes." No, even as opt-in — it would tempt us to optimize for
  runic-text-readability, which dilutes the rest of the design.
- **Runic borders.** `ᛞᛞᛞᛞᛞᛞᛞ` as a horizontal rule. No — too dense.
- **Runic decorative fonts.** No font requirements beyond stdlib
  Unicode.
- **Runes in error messages.** No "ᚹᚱᛟᚾᚷ" for "wrong." Plain
  English errors.

---

## Falling back gracefully

When the operator's terminal can't render a rune (font missing the
glyph), we substitute as documented in [`../architecture/19_REPO_MAP.md`](../architecture/19_REPO_MAP.md):

| Rune | Unicode | ASCII fallback |
|---|---|---|
| ᛞ | U+16DE | `*` |
| ᛟ | U+16DF | `*` |
| ᛏ | U+16CF | `+` |
| ᛒ | U+16D2 | `B` (uppercase Latin, since Berkano = birch begins with B) |
| ᚹ | U+1B9 | `W` |

The fallback uses ASCII characters that *look* like decoration in
context. We don't try to be clever ("ᛞ → `D`") — the visual goal is
ornament, not transliteration.

---

## Pronunciation guide (for operators who want it)

If an operator asks "how do I say `Stofa`?" or wants to read aloud:

| Rune | Roman | Pronunciation |
|---|---|---|
| ᛞ | d | as in "day" |
| ᛟ | o | "oh" |
| ᛏ | t | as in "Tyr" or "tea" |
| ᛒ | b | as in "birch" |
| ᚹ | w | "voo" (like "wonder") |

The README mentions this briefly. The TUI itself doesn't surface
pronunciation guides.

---

## Where runes do NOT go

- The command palette (uses Latin commands).
- The chat input (operator types Latin text; Funi replies in Latin
  text).
- Pet names (in the pet bestiary, the names are Romanized: "Hugin"
  not "ᚺᚢᚷᛁᚾ").
- File names (Episode files, audit log, etc. — all Latin).
- Config keys (`ember.yaml` keys are all Latin).
- Error messages (always plain English / operator's locale).

---

## Closing

Runes in Stofa are like the geometric patterns on a 19th-century
Scandinavian wooden chest — visible to the visitor, beautiful in
their own right, but not asking to be read. The operator who wants
to look it up will find that `ᛟ` is the rune of heritage and feel a
small spark of meaning. The operator who doesn't will see a small
decorative mark. Both are well-served.

The discipline is: never gate functionality behind runic literacy.
Decoration only. Three motifs total. No more.
