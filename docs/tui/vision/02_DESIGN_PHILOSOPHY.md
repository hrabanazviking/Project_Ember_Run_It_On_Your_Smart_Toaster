# 02 — Design Philosophy

The Stofa design philosophy is **five principles**, each one a
non-negotiable lens that every later decision in this design tree has
to pass through. If a feature, layout, palette, or pet violates one,
that thing changes.

---

## 1. Coziness over capability

Stofa is a **mead-hall**, not a cockpit.

A cockpit has every dial visible at once. Stofa shows what you're
working on, with the rest one keystroke away. Coziness means:

- **Reading is the default state**, not configuring. The chat is the
  largest panel. Everything else is in service to the conversation.
- **No screen looks busy.** If the operator can count more than ~10
  visible distinct elements (excluding text content), the screen is
  too dense — reduce.
- **Warmth in the color choices.** Aurora palette leans warm-dark, not
  cyberpunk. See [`design/64_PALETTE_AURORA.md`](../design/64_PALETTE_AURORA.md).
- **A fire is always lit somewhere.** Literally: there is a hearth
  icon in a fixed location on the chrome. It animates softly when
  Funi is working. Coziness is reinforced by environmental detail.
- **Sound is opt-in, not default.** No beeps. No bells. Operators
  who want a soft chime when a long ingest finishes can opt in.

**Anti-pattern:** the all-panels-visible-all-the-time dashboard. We are
not building a Bloomberg terminal.

---

## 2. The operator is at home; Ember serves them

Stofa belongs to the operator. Every screen reflects:

- **Their** identity (the name they chose for Ember).
- **Their** Well (their documents, their chunks, their counts).
- **Their** approvals (their tool-trust list).
- **Their** pets (selected, theme-able, can be turned off).

Ember speaks. Ember does not own. The TUI never:

- Pushes notifications about new features.
- Phones home for "improvement telemetry."
- Hides operator data behind a "premium" tier.
- Asks the operator to log in to anything.
- Suggests upgrades that aren't strictly necessary.

When Ember needs to ask the operator something (tool approval, missing
config, "shall I create this directory?"), the ask is **clear, scoped,
typed, and refusable**. The operator can always say no. The operator
can always Ctrl-C without losing anything that wasn't already lost.

This principle is the Vow of Sovereignty in interface form.

---

## 3. Modern Viking, not fantasy Viking

The aesthetic register is **domestic Old Norse**, not heroic mythic
Norse.

- **Runes as ornament, never as content.** A status separator can
  be `ᛞᛞᛞ` decoratively, but no actual UI text is in runes the operator
  has to decode. (Reading "ᛒᚱᚢᚾᚾᚱ" instead of "Brunnr" is a barrier
  to entry, not a feature.)
- **Compound nouns and naming over titles.** "Mead-hall" — yes.
  "House of the Æsir" — no. The aesthetic is *household*, not
  *heroic-mythological*.
- **Modern type for body text.** No blackletter, no Futhark-as-headers,
  no decorative ligatures. The body of every panel is in the
  operator's terminal font, monospace, plain. Only the chrome
  (panel headers, status bar, separators) gets ornament.
- **Considered color over loud color.** The Aurora palette is muted
  twilight; even Midgard (the brightest theme) avoids saturated reds
  and yellows. No #FF0000 anywhere.
- **Animals + plants over weapons + armor.** Pets are ravens, foxes,
  goats, bees. Not warriors, not war-banners. The hall is for living
  in, not fighting from.

A specific test: **does this design choice look out of place in a
modern operator's terminal next to neovim and lazygit?** If yes, soften
it. Stofa should feel like a cousin to those tools, not an alien.

---

## 4. Beauty is correctness

A beautiful TUI is a *correct* TUI. The two are not in tension:

- **Aligned column edges** are not just nice — they make scanning fast.
- **Consistent box-drawing characters** prevent the visual jitter that
  exhausts the operator.
- **Restrained color** lets meaningful color (errors, citations,
  approvals) actually stand out.
- **Predictable layout** means the operator's eyes go to the right
  place without thought — Fitts's Law applied to gaze.
- **Whitespace** is information. Cramped is unreadable.

This means we will:

- Use exactly one box-drawing vocabulary (Unicode rounded corners +
  light-weight verticals; see [`design/62_BOX_DRAWING_VOCABULARY.md`](../design/62_BOX_DRAWING_VOCABULARY.md)).
- Use exactly five semantic colors (see [`design/64_PALETTE_AURORA.md`](../design/64_PALETTE_AURORA.md)
  and siblings).
- Use exactly two type weights (regular + bold; no italic unless the
  operator's terminal supports italic well).
- Use exactly one accent rule (saturated only on actionable things;
  desaturated everywhere else).

The discipline of *fewer choices, more consistently applied* is the
discipline that produces a beautiful TUI. Lazygit's success is not
that it has the prettiest single screen — it's that every screen
follows the same five rules.

---

## 5. Robust because failure is part of the design

Stofa runs in an unpredictable environment:

- Terminal could be 30×80 or 200×60 or 5×400 (tmux split).
- It might support truecolor; it might support 16 colors.
- It might be a real TTY; it might be `script` redirecting to a file.
- The operator might Ctrl-C at any millisecond.
- The Funi server might disconnect mid-stream.
- The Well might be a network mount that just lost packets.
- The terminal might be alt-screen-broken (some over-eager `tput`
  invocation left state behind).

Stofa survives all of this. Specifically:

- **Resize is correct.** Every panel reflows. Test matrix in
  [`operations/92_RESIZE_HANDLING.md`](../operations/92_RESIZE_HANDLING.md).
- **No-color fallback is correct.** Pure ASCII variants exist for
  every box-drawing character. The pets degrade to one-line
  text descriptions ("(raven hops onto the well panel)").
- **No-mouse fallback is correct.** Every action has a keyboard
  binding. Discoverable via `?`.
- **No-Unicode fallback exists.** ASCII-art-only mode for terminals
  that report `LANG=C` or refuse U+E000-range glyphs.
- **Crash is bounded.** Per-panel error boundaries. A panel that
  raises shows "(panel error: <one-line reason>)" instead of
  killing the whole TUI.
- **Quit always works.** `Ctrl-C` and `q` both leave. Stofa restores
  the cursor, exits the alt-screen, and prints one line so the
  operator knows the session ended cleanly.

Per the Vow of the Unbroken Whole: one panel failing doesn't take down
the hall. The fire keeps lit. The other panels keep their state.

---

## How these principles interact

When two principles seem in conflict, the precedence is:

1. **Robust** (P5) wins over everything — a beautiful screen that
   crashes is worse than an ugly one that doesn't.
2. **Operator-at-home** (P2) wins over **modern Viking** (P3) — if
   the aesthetic gets in the operator's way, soften it.
3. **Beauty = correctness** (P4) wins over **coziness** (P1) — coziness
   that produces misalignment loses to discipline.
4. **Coziness** (P1) is the default tiebreaker — when nothing else
   forces the answer, choose the option that feels warmer.

These are not arbitrary. They are the order in which an operator
experiences the TUI: does it work at all (P5), do I feel respected
(P2), is it well-made (P4), is it beautiful (P3), is it pleasant (P1).
Higher levels of Maslow once the basics are met.

---

## Specific anti-patterns we refuse

Listed here so any future PR can be checked against the list:

- **Splash screens longer than 200ms.** No "Loading Stofa…" with a
  spinner that lingers. The hall opens; the panels populate over the
  next few hundred ms as their data arrives.
- **Modal dialogs that block input.** The only modals are: tool
  approval, Hjarta wizard, the help overlay. All three have explicit
  reasons. No "Are you sure?" modals for non-destructive actions.
- **Pop-up tutorials.** Discovery is via `?`, not via "Hey! Want a
  tour?" interruptions.
- **Emoji in chrome.** UI labels are words. (Operator-typed messages
  and Funi replies can contain emoji; the chrome itself doesn't.)
- **Tickers for tickers' sake.** The chat panel scrolls when there's
  new content. The status bar updates on real events. Nothing animates
  just to look alive *except* the pets, which are explicitly opt-in.
- **Confusing iconography.** Every icon has a one-word tooltip on
  hover (or in the `?` overlay).
- **Hidden settings.** Every operator-tunable lives in
  `ember.yaml` + a Settings screen. Nothing is "in code only."
- **Surprise destruction.** Nothing in Stofa ever deletes operator
  data without explicit confirmation. Even `q` doesn't clear the
  chat history (it's persisted as an Episode regardless).

---

## Closing

Five principles. Twenty pages of consequence. The rest of this design
tree is just the work of applying these five to every concrete
question. When in doubt later: re-read this file.
