# 04 — Pets Vision

## What the pets are

The pets are **small text-mode creatures** that live on the chrome of
Stofa. They animate sparingly. They serve three real functions:

1. **Ambient status signaling** — at a glance, the operator can tell
   what Ember is doing by *who* is doing what. The bee being busy
   means ingest is running. The raven landing on the citations panel
   means retrieval just returned hits.
2. **Friendliness** — a hall with a cat in it is a hall someone
   *lives* in. The pets make Stofa feel inhabited.
3. **Helpfulness** — each pet has one or two genuine tasks beyond
   being cute. The fox pokes its head out when a tool needs approval.
   Heiðrún drops a mead-horn into the audit log marker when a tool
   fires. The raven shuffles toward the document with the highest
   hit-score.

The pets are **NOT a gimmick**. They are an ambient information
display, dressed as cute. See [`pets/74_PETS_HELPFULNESS.md`](../pets/74_PETS_HELPFULNESS.md)
for the per-pet helpfulness contract.

The full bestiary lives in [`pets/71_PETS_BESTIARY.md`](../pets/71_PETS_BESTIARY.md);
this file is the *why*.

---

## Why pets, and why now

There are three reasons to have pets in Stofa, and one reason against
which we have to answer.

### Why: the cognitive-load argument

A status indicator is information. A glowing light says "the disk is
working." A spinner says "we're waiting on the server."

The *cost* of an indicator is that the operator has to learn it. A
red light next to "ERROR" works because the operator knows red+ERROR
= bad. A red light next to a circular arrow means... what? They don't
know without reading the label.

The pet is a **labeled mascot for a single status concept**. Once the
operator has learned that the bee = ingest, the bee's motion conveys
ingest status without text. The operator's eye picks up "bee active,
ingest running" in a fraction of a second, without reading.

This is the same trick that lazygit uses with its three-column
layout: positions are labels. Stofa just adds a second layer: pets
*are* labels for *operations*.

### Why: the warmth argument

Operators are people. Operators who use a tool for hours every day
build a relationship with it. The tools they end up loving are the
ones that feel inhabited.

- `lazygit` has its self-deprecating commit messages.
- `htop` has its rainbow CPU bar.
- `glow` has its little cat-eye logo.
- `cowsay` has the cow.
- `cmatrix` has the matrix.

Stofa's pets are a deeper version of the same impulse: not a logo,
not a one-off ASCII-art gag, but *little living things* in the hall.

### Why: the fun argument

Ember is, in part, a project against the corporate-AI default. Cute
text-mode creatures are *anti-corporate* in the best way. They say
"this software was made by people, for people, to be used in their
own home." They are the README's "toaster" joke in moving form.

### The argument against: distraction

A moving thing in the operator's peripheral vision is a cost. If the
pets twitch every 100ms, the operator's eye keeps getting yanked.

**This is the most important constraint on the pets.** The bestiary
addresses it head-on: every pet's animation budget is bounded to
roughly 1 frame per second of *visible* motion, and most pets are
still 95% of the time. They are *quietly alive*, not *constantly
performing*.

We back this up with hard rules:
- Per-pet motion cap of 1Hz.
- Total animation budget across all visible pets: 4Hz aggregate.
- All animation pauses while the chat input is focused (no motion
  while the operator is typing).
- Operator can disable any single pet, or all of them, in one
  keybind (`p`).
- The `--minimal-redraw` SSH-friendly mode freezes all pets.

---

## What the pets are NOT

This is as important as what they are.

- **NOT chatty.** Pets do not pop up dialog boxes. They do not say
  "Did you know you can…?" or "Hello there!" — ever. They communicate
  through *position* and *posture*, not text.
- **NOT a personality system.** Pets have one consistent behavior
  each. The fox is always the tool-approval fox. We are not building
  a Tamagotchi.
- **NOT collectible or gamified.** No achievements, no levels, no
  "feed your pet to keep it alive." The pets are *here* because Stofa
  is here. They don't track the operator.
- **NOT animated in any way that defeats the SSH-friendly cap.** A
  moving pet over high-latency SSH that produces visible jitter is
  worse than a still pet.
- **NOT random.** Every pet motion is causally linked to a real event
  (Funi token arriving, ingest progress, tool call, etc.). The pets
  are *displays*, not pure entertainment.
- **NOT generative.** Operators can't make new pets through
  conversation. The bestiary is fixed; updates ship in releases.

---

## The aesthetic register of the pets

Pets are Norse-shaped where possible, but **modern Norse, not heroic
mythological Norse**. Compare:

| Modern Norse (what we want) | Heroic Norse (what we don't) |
|---|---|
| Raven on the perch | Odin's raven Huginn the Knower-of-All |
| Goat by the wall | Heiðrún the Heavenly Mead-Goat |
| Fox at the door | Loki in Vulpine Form |
| Bee in the field | Honey-Spirit of Asgard |
| Ash sapling in a pot | The Yggdrasil-Tree-of-Worlds |

The pets *evoke* the Norse household — the kind that had goats and
ravens and bees in everyday life — without claiming mythic significance.
They get little names that nod to mythology without invoking it:

- The raven is **Hugin** (small-h, no umlaut — *hugin* = thought).
- The goat is **Heiðr** (heath, not heaven).
- The fox is **Refur** (just "the fox," with a name).
- The bee is **Sumarbýfa** (summer-bee).
- The cub is **Geri-cub** (Geri = the greedy one, but small).

Mythology fans will smile. Newcomers won't feel locked out by the
naming.

---

## Pets and the personas

How each persona reacts to the pets:

- **Volmarr (Sovereign Operator)** — neutral; turns them off if they
  annoy. Acceptable.
- **Iðunn (Newcomer)** — delighted. The pets are the moment Iðunn
  thinks "this software was made by a person who cares."
- **Sigrún (Power-User)** — has them on `--minimal` mode by default
  (still pets, no animation). Uses them as positional status
  indicators.
- **Védis (Cozy Operator)** — keeps them ALL on. May ask for more.
- **Eirwyn (Pi-Class)** — has them disabled or in minimal mode.

The pets need a **single keybind** to toggle (`p`) and a config field
to set the default. We don't want operators having to navigate three
menus.

---

## Pet roster (one-paragraph teaser; full detail in bestiary)

There are nine pets in Stofa V1:

1. **Hugin** (raven) — perches on the panel containing the most-recent
   tool reply or retrieval citation.
2. **Heiðr** (goat) — stands by the audit-log panel; drops a tiny
   mead-horn glyph when a tool call is audit-logged.
3. **Refur** (fox) — appears at the bottom of the chat panel during
   tool-approval prompts; vanishes after approval.
4. **Sumarbýfa** (bee) — ferries documents during ingest; one bee
   per active ingest task.
5. **Geri-cub** (wolf cub) — sleeps in the corner when Stofa is idle;
   yawns occasionally.
6. **Ask-sapling** (ash) — grows in a pot as the chat session
   lengthens; resets each new session.
7. **Drift** (snow-flake spirit) — appears during the Aurora theme;
   one or two drifts cross the chrome per minute.
8. **Funi-spark** (the hearth flame) — pulses softly when Funi is
   thinking; sits still otherwise.
9. **Ember-ember** (the literal hearth ember) — fixed icon, doesn't
   move; the "logo" of Stofa. Always present.

Of these, **only Funi-spark and Ember-ember are non-optional**. The
hearth and its ember are part of the chrome itself; the others can
be turned off individually or as a set.

---

## Long-tail roadmap (not V1)

After V1 ships, the pets are extensible (per the Vow of Modular
Authorship). Plugin pets are imagined for V2+:

- **Mánagarmr** (moon-hound) — appears at night based on system clock;
  paces during a long-running ingest.
- **Borgar** (the watcher-stone) — appears when MCP servers are up;
  greys out when one is down.
- **Hrímfaxi** (frost-mane horse) — appears during pgvector hybrid-search;
  gallops across the chrome.

These are sketches for after V1. No promises.

---

## Closing word

The pets are not whimsy bolted on. They are an *interface design
decision*: ambient, labeled, sparing, configurable, opt-out-able,
genuinely informative. They are also delightful — which is the point
of using cute animals instead of LED-style indicators. The smile is
the reward; the speed of comprehension is the function.

Stofa is, fundamentally, *the hall someone designed with care*. The
pets are the proof.
