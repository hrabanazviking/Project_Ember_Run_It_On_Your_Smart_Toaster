# 60 — Viking Aesthetic

The visual register of Stofa. **Modern domestic Norse**, never heroic
mythological Norse. The hall of a 10th-century longhouse rendered in
2026 terminal cells.

---

## What we draw from

- **Old Norse domestic life** — household objects, daily routines,
  the *stofa* itself as a room.
- **Norse craft traditions** — woodcarving lines, animal motifs in
  metalwork, runic ornament.
- **Modern Scandinavian design** — restraint, considered materials,
  warm minimalism (Wegner, Aalto, Klint).

We blend these. Stofa is what 10th-century Norse interior craft
would look like if it survived as a *modern* design tradition.

---

## What we don't draw from

- **Marvel-style mythic Norse** — no Mjölnirs, no Asgardian gold,
  no "warriors of the Æsir" framing.
- **Heavy-metal Norse** — no flaming runes, no skulls, no swords.
- **Christmas-decoration Norse** — no Father-Christmas-Odin
  iconography.
- **Tourist Norse** — no horned helmets (Vikings didn't wear them
  in battle anyway).
- **Generic medieval fantasy** — no castles, no knights, no
  fairy-tale typography.

We are *household Norse, modern register*. That's the line.

---

## The visual vocabulary

### Lines

- **Light box-drawing**: `─ │ ╭ ╮ ╯ ╰` for the chrome.
- **No double lines** (`═ ║`) in V1. Too heavy.
- **Horizontal rules** (`───`) for section separators.
- **Vertical pipes** (`│`) for inline separators.

### Forms

- **Rounded corners.** Every box has rounded corners (`╭ ╮ ╯ ╰`).
  Matches a craftsperson's choice to soften wood edges.
- **Generous padding.** Modern Scandinavian sensibility: space is
  itself a material.
- **No flourishes.** No `~~~` borders, no fancy double-borders.
  The structure is the decoration.

### Ornaments (sparingly)

- **Runic separator on chrome:** `ᛞ ᛞ ᛞ` (ᛞ = Dagaz, day/dawn).
  Used as a section divider in the chrome header, once per screen.
  Decorative, not informational. Falls back to `--- --- ---` in
  ASCII.
- **Star marker:** `☆` for "starred" items in V2 (saved prompts,
  favorite servers). Used very sparingly.
- **Bullet:** `•` (a heavy bullet, not the lighter `·`). Single
  character, used for lists.

### Iconography

We use **glyphs, not pictograms**. Stofa avoids emoji because:
- Inconsistent rendering across terminals.
- Color emoji clashes with the considered palette.
- The Norse register prefers geometric ornament over depictive
  iconography.

**Exception:** the hearth icon `🔥` is allowed (one of the few
emoji we use), because it's central to the metaphor. Even then, an
ASCII fallback (`^`) is provided.

Other "icons":

- Hearth: `🔥` (fallback `^`)
- Realms (status dots): `●`
- Focus pointer: `▶`
- Expand: `▾`
- Collapse: `▸`

That's the entire iconography set. Five glyphs. The rest is text.

---

## Color in the Viking register

(Full palettes in [`../design/64_PALETTE_AURORA.md`](64_PALETTE_AURORA.md)
onward. Here we describe the *register* of choices.)

The Norse register favors:

- **Twilight blues and slate greys** (cool darks).
- **Warm ambers and honey golds** (warm accents).
- **Sage greens and moss tones** (success / nature).
- **Brown-oranges and rust** (warnings / autumn).
- **Muted reds** like dried-blood or hawthorn-berry (errors).

We do NOT use:

- **Cyberpunk neons** (#FF00FF, #00FFFF).
- **Corporate primaries** (#0066CC, #FF0000).
- **Faded pastels** (too cute; we want warm-restrained, not
  babyish).

The Aurora palette is the most archetypal: deep blue-grey background,
muted cool primary, warm amber accent. Aurora's name comes from
*aurora borealis* — the northern light over a Norse landscape at
night.

---

## Typography in the Viking register

- **Body text: terminal default monospace.** We don't ship a font;
  the operator picks.
- **Bold sparingly** for headlines (panel titles).
- **No italic** (per [`../ux-science/45_TYPOGRAPHY_FOR_MONOSPACE.md`](../ux-science/45_TYPOGRAPHY_FOR_MONOSPACE.md)).
- **No runic display text.** A heading is "Conversation", not
  "ᚲᛟᚾᚹᛖᚱᛋᚨᛏᛁᛟᚾ".

Runes appear as **ornament** in three places only:

1. Chrome separator: `ᛞ ᛞ ᛞ`.
2. Some pet sprites use runic glyphs for decorative detail (e.g.,
   Ask-sapling has a `ᛏ`-like rune in its bark pattern).
3. The Hjarta wizard's title bar has a single ornamental rune
   `ᛟ` (Othala, the heritage rune) — fitting for the identity
   wizard.

That's it. Three runic ornament usages. Anything more crosses into
LARP.

---

## Layout in the Viking register

A Norse longhouse is **long and narrow**. The Stofa screen is a
horizontal rectangle (terminal default). We honor this by:

- **Wide layouts that breathe.** Per
  [`../architecture/14_LAYOUT_SYSTEM.md`](../architecture/14_LAYOUT_SYSTEM.md):
  generous padding, two-column where possible.
- **Important things along the long axis.** ChatScreen's
  conversation flows horizontally (left-to-right within lines, then
  top-to-bottom). The status bar runs the full width.
- **The hearth at one end.** Like a longhouse has the fire pit in
  one fixed location, the hearth icon is at a fixed position in
  the chrome header (top-right).

---

## The mood we're after

Imagine: it's late autumn evening, the day has been long, you walk
into a Stofa with a low fire crackling, benches along the walls, a
loom in the corner, ravens outside, a wolf cub by the door. There's
mead being warmed. Someone's softly working at a quiet task.

You sit down. You're not alone, but you're not crowded. The room is
warm. The light is gentle. There's enough to look at without being
busy. You can stay here for hours.

That's Stofa. The visual aesthetic serves this mood.

If a design choice makes the room feel *cold*, *busy*, *aggressive*,
or *flashy*, the choice is wrong.

---

## Specific consequences

- **Defaults: Aurora theme + pets enabled.** Aurora is the
  twilight-of-the-hall feeling. Pets are the household creatures.
- **The hearth icon is part of the chrome.** Always present. The
  fire is always lit somewhere.
- **Sound is opt-in.** A real Stofa would have ambient noise (fire,
  wind, animals). Our TUI is silent by default; operators can opt
  in to ambient mead-hall sound effects (V2 maybe).
- **The first-launch screen is the wizard.** Like entering a
  hall — someone greets you, asks your name, settles you in.

---

## Closing

The Viking aesthetic in Stofa is a **restraint discipline**, not an
indulgence. We choose Norse household register over Norse mythic
register because the former is *livable* and the latter is
*performative*. We choose modern Scandinavian restraint over fantasy
maximalism. We choose three runic ornaments and stop. The result is
a TUI that feels Norse without performing Norse — a hall someone
actually built, not a tourist's idea of one.
