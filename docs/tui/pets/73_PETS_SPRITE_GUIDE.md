# 73 — Pet Sprite Guide

The actual ASCII / Unicode sprites for each pet. Frame by frame.
Stored in `src/ember/stofa/pets/sprites/<name>.txt`.

---

## Sprite file format

```
---FRAME:idle---
{multi-line sprite}
---FRAME:flying---
{multi-line sprite}
---FRAME:idle_ascii---
{ASCII version}
---FRAME:flying_ascii---
{ASCII version}
```

The sprite loader parses these into a dict. Trailing whitespace
preserved. Color applied at render time via the pet's `$pet-<name>`
token.

---

## Hugin the raven

### idle (perched, head down)
```
   ▄▄▄
  ▟███▙
   ▀▀▀
```

### flying (wings out)
```
  ▄  ▄
 ███▙▟███
   ▟▙▟▙
```

### perched (looking around)
```
   ▄▄▄
  ▟███▙
   ▀ ▀
    ▀
```

### looking_down (head tilted)
```
  ▟▄▄▙
  ▜███▛
   ▌▐
```

### ASCII fallbacks
```
---FRAME:idle_ascii---
   /\
  (oo)
  /  \
---FRAME:flying_ascii---
  ___
 (>oo<)
 /vv vv\
---FRAME:perched_ascii---
   /\
  (o.)
  /  \
   |
---FRAME:looking_down_ascii---
  ___
 (vv)
  ||
```

---

## Refur the fox

### idle (sitting, ears alert)
```
   ▄ ▄
  ▟███▙
  ▜███▛
   ▌ ▐
```

### watching (head turned)
```
   ▄ ▄
  ▟███▙
  ▜▀▀▟
   ▙ ▟
```

### tilt (head tilted - approval gesture)
```
   ▄  ▄
  ▟▘███▙
  ▜████▛
   ▌  ▐
```

### ASCII fallbacks
```
---FRAME:idle_ascii---
  /\_/\
 ( o.o )
  > ^ <
---FRAME:watching_ascii---
  /\_/\
 ( -.- )
  > _ <
---FRAME:tilt_ascii---
   /\__
 ( o>< )
  > _ <
```

---

## Heiðr the goat

### idle (standing)
```
   ╭∩∩╮
  ┃ oo ┃
  ┃    ┃
   ┃  ┃
   ┃  ┃
```

### drop-horn (dropping the ◊ glyph)
```
   ╭∩∩╮
  ┃ oo ┃
  ┃    ┃   ◊
   ┃  ┃
   ┃  ┃
```

(The `◊` glyph is rendered separately as a fade-out effect; appears
2 cells to the right of the goat for ~2 seconds, then fades.)

### ASCII fallbacks
```
---FRAME:idle_ascii---
   /^^\
  | oo |
  |    |
   |  |
   |  |
---FRAME:drop_horn_ascii---
   /^^\
  | oo |
  |    | <>
   |  |
   |  |
```

---

## Sumarbýfa the bee

### idle (centered, wings folded)
```
  ▟▙▟▙
 ▟▒█▒▙
  ▀▀▀▀
```

### flying_left (wings up, body leans)
```
   ▟▙▟▙
  ▟▒█▒▙
   ▀▀▀▀
  ▟    ▙
```

### flying_right (mirror)
```
   ▟▙▟▙
  ▟▒█▒▙
   ▀▀▀▀
  ▙    ▟
```

### depositing (dropping a document glyph)
```
  ▟▙▟▙
 ▟▒█▒▙
  ▀▀▀▀
   ▼
```

(Wing animation cycles flying_left → flying_right → flying_left at
~1 Hz, giving a soft ferrying motion.)

### ASCII fallbacks
```
---FRAME:idle_ascii---
  \\//
 (>I<)
  ----
---FRAME:flying_left_ascii---
   \\//
  (>I<)
   ----
  /    \
---FRAME:flying_right_ascii---
   \\//
  (>I<)
   ----
  \    /
---FRAME:depositing_ascii---
  \\//
 (>I<)
  ----
   v
```

---

## Geri-cub the wolf cub

### idle (sitting)
```
   ▟ ▙
  ▟███▙
  ▜███▛
   ╱ ╲
  ╱   ╲
```

### yawning (mouth open)
```
   ▟ ▙
  ▟███▙
  ▜▀O▀▛
   ╱ ╲
  ╱   ╲
```

### sleeping (curled up)
```
    ▟▄▄▙
   ▟████▙
   ▜████▛
    ▀▀▀▀
```

### ASCII fallbacks
```
---FRAME:idle_ascii---
   / \
  (o.o)
  /   \
  / | \
---FRAME:yawning_ascii---
   / \
  (o O)
  /   \
  / | \
---FRAME:sleeping_ascii---
   _____
  (z z z)
   \___/
```

---

## Ask-sapling the ash

### 1_leaf
```
    .
    |
    *
    |
    |
   _|_
  | * |
  |___|
```

### 2_leaves
```
   . .
    |
    *
    |
    |
   _|_
  | * |
  |___|
```

### 4_leaves
```
  . . .
   .|.
    *
    |
    |
   _|_
  | * |
  |___|
```

### 6_leaves
```
 . . . .
  ..|..
   .*.
    |
    |
   _|_
  | * |
  |___|
```

### ASCII fallbacks (already ASCII; same)

---

## Drift the snowflake

### default (just the glyph)
```
❄
```

### ASCII fallback
```
*
```

(Drift is animated by *position*, not by frame change. The single
glyph drifts horizontally across the chrome.)

---

## Funi-spark the hearth flame

### idle_dim (still, banked)
```
🔥
```

### pulse_bright (mid-pulse, glowing)
```
🔥
```

(Same glyph; the *color* shifts between `$hearth-base` and
`$hearth-glow` via the pet's state. No sprite change; only tint
animation.)

### ASCII fallback
```
^
```

(Same — color animation only.)

---

## Ember-ember the logo

### static
```
●
```

(No animation. Always this single glyph in `$hearth-glow`.)

### ASCII fallback
```
*
```

---

## How sprites get rendered

Each frame is a multi-line string. The PetWidget's `render()`
returns a Rich `Text` object with the frame string colored by the
pet's `$pet-<name>` token.

```python
def render(self) -> RichText:
    if self.state == "hidden":
        return RichText("")
    ascii_only = self.app.theme.ascii_only
    sprite_str = self.SPRITE.get(self.current_frame, ascii_only=ascii_only)
    return RichText(sprite_str, style=f"pet-{self.NAME}")
```

The PetLayer positions the rendered widget at the resolved perch
coordinates.

---

## Sprite design constraints

Every sprite must:

- **Fit in 6×6 cells or fewer.** Pets are decorative; they don't
  occupy real estate.
- **Be visible on every theme.** The pet's `$pet-<name>` token has
  WCAG 3:1 contrast with each theme's background (tested).
- **Have an ASCII fallback.** Always.
- **Use only Block Elements (U+2580-259F) and standard ASCII.**
  No emoji (except Funi-spark + Ember-ember). No combined glyphs.

These constraints make pets reliable across the terminal-emulator
matrix (per [`../operations/91_TERMINAL_COMPAT_MATRIX.md`](../operations/91_TERMINAL_COMPAT_MATRIX.md)).

---

## Closing

Nine pets. Three-to-five frames each. ASCII fallback for every
frame. All sprites < 6×6 cells. Color via theme tokens. Animation
via frame swap + position move. Tractable. Testable. Cute.
