# 33 — Decorative / Cute TUIs

We study **nap** (Charm's snippet manager), **pipes.sh** (animated
screensaver), and **oneko-tui** (a cat that follows your cursor).
These are mostly-aesthetic tools. They teach Stofa about **cute as
load-bearing**, **motion done right**, and **the case for personality
in operator tools**.

---

## nap (Charm)

> https://github.com/maaslalani/nap

A snippet manager in the terminal. The use-case is "I have a bunch
of code snippets I want to find quickly." Plenty of tools do this;
nap stands out because it's **gorgeous**.

```
                          ╭─ My Snippets ─────────────────────────╮
   ╭─ Folders ──────╮     │                                        │
   │ ★ favorites    │     │  # Quick git stash                      │
   │ ◇ rust         │     │                                         │
   │ ◇ python       │     │  ```bash                                │
   │ ◇ shell        │     │  git stash push -m "wip"                │
   │                │     │  git stash pop                          │
   ╰────────────────╯     │  ```                                    │
                          │                                         │
                          ╰─────────────────────────────────────────╯
                          / search  n new  d delete  ? help
```

### What works

- **Padding everywhere.** Generous interior whitespace.
- **Rounded borders.** Modern.
- **Two-tone color scheme.** Restrained.
- **Star + diamond glyphs for categories.** Decorative without
  being noisy.

### What we steal

These four. They're not exclusive to nap, but nap is a great
distilled example.

---

## pipes.sh

> https://github.com/pipeseroni/pipes.sh

A shell screensaver. Draws random animated pipes across your
terminal. Pure decoration.

```
                    ╭─╮     ╭───────────╮
                    │ ╰─────╯           │
                    │       ╭───────╮   │
                    │       │       │   │
                    ╰───────┤       │   │
                            ╰───────╯   │
                                        │
```

### What it teaches us

**Pure decoration has a place.** Pipes does nothing useful, but it's
beloved. The fact that we *can* put a soft animation in a terminal
is itself a feature. The terminal isn't a calculator; it's a
canvas the operator looks at.

### What we apply

The Stofa pets are not pure decoration — each does something — but
the *willingness to put motion in a terminal* comes from this
tradition. Without pipes, the cultural permission for animated
terminal UIs would be smaller.

---

## oneko-tui

> A terminal version of the classic X11 "oneko" cat that follows
> your mouse cursor.

A small cat ASCII-art creature wanders around your screen. Mostly
idle; chases mouse when the cursor moves.

```
          (\_/)
          (^.^)
```

### What it teaches us

**A character can be a companion.** Operators who run oneko leave
it on all day. The cat doesn't *do* anything; it's just there. The
"there"-ness is the point.

### What we apply

Stofa pets are designed to *be there* in the same spirit. They are
inhabitants of the hall. The fact that they *also* do helpful
signaling is bonus.

The specific lesson: animation **rate** matters. Oneko-tui's cat
moves slowly, deliberately. Stofa's pets are similarly paced
(see [`../pets/72_PETS_BEHAVIOR_ENGINE.md`](../pets/72_PETS_BEHAVIOR_ENGINE.md)).

---

## Anti-examples (what NOT to do)

For balance, here's what cuteness goes wrong:

- **Clippy.** The Microsoft Office assistant. Pop-up, intrusive,
  text-heavy, demanding. Cute-but-annoying. Stofa pets are silent
  and ambient.
- **Excessive ASCII-art logos.** Some CLI tools have a giant logo
  every time they launch. After the first three launches, it's
  noise. Stofa's logo (the hearth icon) is small and *useful*
  (animates when Funi works).
- **Bouncing notifications.** Some tools have alerts that bounce
  to grab attention. Distracting. Stofa pets don't bounce; they
  drift, perch, fly briefly.

---

## The pattern: cute as load-bearing

Tools that are *only* useful eventually feel like a chore. Tools
that are *also* delightful become things operators keep using even
when they have alternatives.

This is not "fluff to attract." It's a real cognitive-load argument:

- Operators look at Stofa for hours.
- Visual interest reduces eye fatigue.
- Personality creates loyalty.
- The pets earn the operator's affection, which earns Ember the
  benefit of the doubt when something goes wrong.

This is the same principle that makes Glow's cat logo > a corporate
"GitHub-style" logo.

---

## Specific Stofa borrowings

From nap:
- Generous padding.
- Rounded borders.
- Decorative glyphs (★ ◇) used as ornament.

From pipes.sh:
- Cultural permission for terminal animation.

From oneko-tui:
- Pets-as-inhabitants (vs pets-as-utility).
- Slow, deliberate animation pace.

From the anti-examples:
- Never pop up.
- Never demand attention.
- Never bounce.
- Never be giant.

---

## Closing

Decorative TUIs prove that "useful" and "beautiful" are not in
tension. The pets in Stofa stand on this tradition — present
because they bring something the operator values, even when that
something is *just* "the hall feels lived in."
