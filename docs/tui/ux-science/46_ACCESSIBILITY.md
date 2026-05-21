# 46 — Accessibility

Stofa must work for operators with reduced vision, color-vision
deficiencies, motor impairments, and screen-reader use.

---

## What we commit to

1. **Every action is keyboard-accessible.** No mouse required.
2. **No color-only signals.** Every color-bearing meaning is also
   labeled / shaped / positioned.
3. **High-contrast and colorblind-safe themes shipped.** Solstice
   (high contrast) + Barrow (colorblind safe).
4. **Screen-reader-friendly output mode.** Opt-in flag that
   simplifies rendering and adds verbose alt-text.
5. **Configurable animation.** Operators with vestibular sensitivity
   can disable all animation in one keybind (`p` for pets + auto-
   disables the hearth pulse).
6. **Configurable terminal-font support.** ASCII fallback for any
   operator whose font can't render Unicode.
7. **Documented compat matrix.** We say what we tested on (see
   [`../operations/91_TERMINAL_COMPAT_MATRIX.md`](../operations/91_TERMINAL_COMPAT_MATRIX.md)).

---

## Color-vision deficiency

8% of men and 0.5% of women have some CVD. The most common types:

- **Deuteranopia** (red-green confusion, green-sensitive): ~5%
- **Protanopia** (red-green confusion, red-sensitive): ~1%
- **Tritanopia** (blue-yellow confusion): rare (~0.01%)

### Mitigation 1: never use color alone

Every meaning carried by color is ALSO carried by another signal:

| Meaning | Color | Other signal |
|---|---|---|
| Good state | $success | `●` bullet + word ("OK") |
| Warning | $warning | `●` bullet + word ("warn") |
| Error | $error | `●` bullet + "Error:" prefix + position (errors near the bottom of their panel) |
| Focused panel | $accent border | border color shift + always at the operator's cursor position |
| Operator message | $accent prefix | "> " character prefix |
| Ember message | $primary prefix | name prefix (Ember's name) |
| Citation | $text-muted | indented under the reply |

A colorblind operator sees Stofa with degraded color but **full
meaning preserved**.

### Mitigation 2: the Barrow theme

A dedicated colorblind-friendly theme:

- Replaces red ($error) with a warm brown-orange.
- Shifts green ($success) toward a teal-leaning hue.
- Boosts contrast between the two by separating their lightness
  values.

Tested with simulated deuteranopia + protanopia via:
- `colour` Python library's CVD simulators.
- Visual inspection by a CVD operator (Persona-3 stand-in).

### Mitigation 3: high-contrast mode (Solstice)

The Solstice theme has WCAG AAA contrast across every text+background
pair. Useful for:

- Low-vision operators.
- Bright-room / projector use.
- Operators who prefer maximum visibility over aesthetic preference.

---

## Reduced vision

Operators with reduced vision use:

- **Larger font sizes** in their terminal.
- **Screen magnifiers.**
- **Screen readers** (less common in TUI but possible).

### Mitigation: layout that scales

Stofa's layout (per [`../architecture/14_LAYOUT_SYSTEM.md`](../architecture/14_LAYOUT_SYSTEM.md))
is cell-based, not pixel-based. When the operator sets their
terminal font to 24pt, every cell is bigger; Stofa renders
correctly at the (now reduced cells available) terminal size.

Specifically, the responsive breakpoints kick in:

- < 80 cells wide → narrow mode (single column).
- < 60 cells wide → degraded mode (panels stack; some chrome
  hidden).
- < 40 cells wide → emergency mode (warns operator + suggests
  terminal resize).

### Mitigation: scalable fonts in the operator's terminal

We assume the operator can set their font size. We don't fight
their settings; we render what fits.

### Mitigation: screen reader mode

A `stofa.screen_reader_mode: true` setting:

- Disables all animation.
- Switches to high-contrast Solstice theme.
- Inserts `[focus changed: <panel>]` announcements when focus moves.
- Inserts `[message arrived]` for streaming tokens (rather than
  speaking each token).
- Renders pets as `[Hugin is here]` text rather than ASCII art.
- Uses simpler box-drawing (or ASCII).

This isn't a full screen-reader implementation — terminals + screen
readers are a fragmentary ecosystem — but it gives the operator a
fighting chance.

---

## Motor impairments

Some operators have difficulty with chord-keys (`Ctrl+Shift+P`),
sustained holds, or rapid sequences.

### Mitigation: no chord requirements

- Every default binding is at most one modifier + one key.
- No three-finger chords (`Ctrl+Shift+Alt+...`).
- No sustained holds (no "hold to confirm").
- No timed sequences requiring < 250ms between keys.

### Mitigation: full rebinding

Operators can rebind every action via `ember.yaml`. An operator who
finds `Ctrl-P` hard can bind the command palette to a single key
(`p` if pets are off, or a function key, or whatever).

### Mitigation: sticky keys friendly

Most OSes have "sticky keys" accessibility (one-at-a-time modifier
emulation). Stofa works correctly with this — we don't depend on
modifier timing.

---

## Vestibular / motion sensitivity

Some operators are sensitive to motion. Pulsing, bouncing, sliding
animations can cause discomfort or dizziness.

### Mitigation: motion is opt-out, granular

- **Pets** off entirely: `stofa.pets_enabled: false` or press `p`.
- **Pet animation** off but pets visible: `stofa.pets_animate: false`.
- **Hearth pulse** off: `stofa.hearth_pulse: false`.
- **Loading spinner** is the only forced motion; it's at most a
  ~1 Hz rotating glyph, NOT a fast spinner.

### Mitigation: respects OS prefers-reduced-motion (V2)

V2 will read the operator's OS-level "reduced motion" preference
(Linux GNOME setting, macOS accessibility) and default the motion
flags accordingly.

---

## Hearing impairment

Stofa is silent by default. We don't emit beeps or sound.

A V2 feature plans **optional audio cues** (chime on long ingest
complete) — these are *additions*, defaulting to off, never
replacements for visible signals.

---

## Cognitive accessibility

Operators with cognitive load constraints (dyslexia, ADHD, ASD,
fatigue) benefit from:

- **Predictable layouts.** Per [`43_VISUAL_HIERARCHY.md`](43_VISUAL_HIERARCHY.md):
  same hierarchy on every screen.
- **Clear language.** Per Vow of Public-Friendliness: no jargon
  without expansion.
- **No urgency.** No "act now or lose data!" alerts. The audit log
  is always there; the Episode is persisted; the operator can think.
- **Recovery from errors.** Esc cancels; tools are refusable; nothing
  destructive without confirm.

---

## What we test

### Automated checks

1. **Color contrast.** `tests/unit/test_stofa_palette_contrast.py`
   verifies every text/background pair meets WCAG ratio for the
   declared level.
2. **ASCII fallback completeness.** Every Unicode-using widget has
   an ASCII variant; tested under simulated `LANG=C`.
3. **Keyboard-only navigation.** `tests/integration/test_stofa_keyboard_only.py`
   drives every screen with keyboard alone; asserts every action
   is reachable.

### Manual checks (pre-release)

1. **Screen reader smoke test.** Run Stofa in screen-reader-mode
   with a screen reader (Orca on Linux); verify navigation
   announces meaningfully.
2. **CVD simulation.** Each theme rendered + CVD-simulated; check
   semantic distinctions preserved.
3. **Low-vision simulation.** Terminal at 28pt; check layout still
   works.

---

## What we don't claim

- **Full WCAG compliance.** Terminal UIs aren't web; WCAG was
  written for web. We borrow its contrast metrics; we don't claim
  the certification.
- **Universal screen reader support.** Terminal + screen reader
  combos vary wildly. We support a baseline.

---

## Operator-facing accessibility settings

Surfaced in SettingsScreen → Stofa section:

```
▾ Stofa
    Theme: [ aurora ▾ ]                  (try barrow for CVD)
    Pets: [ ✓ ]    Animate pets: [ ✓ ]    Hearth pulse: [ ✓ ]
    Screen reader mode: [ □ ]
    ASCII-only rendering: [ □ ]
    UI density: [ medium ▾ ]
```

Each is also a config field; operators can set them in `ember.yaml`
or via the CLI flag (`--theme barrow`).

---

## Closing

Accessibility is a *feature*, not a compliance checkbox. The work to
ship Solstice and Barrow themes, the keyboard-only path, the
animation opt-outs, the screen-reader mode — that work makes Stofa
*better for everyone*, including operators with no impairment. The
small extra design discipline pays off when an operator says "this
is the only TUI I can use comfortably." That's the test.
