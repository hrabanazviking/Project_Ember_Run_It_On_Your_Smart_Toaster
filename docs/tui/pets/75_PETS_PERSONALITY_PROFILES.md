# 75 — Pets Personality Profiles

The "in their words" voice for each pet — used in operator-facing
copy *about* each pet (in docs, settings, help overlay). The pets
themselves never speak (no text from a pet to an operator).

This document is for the Scribe role: when writing about a pet,
this is its voice.

---

## Hugin — the messenger

**Voice:** quiet, watchful, slightly formal. Speaks rarely; when
mentioned, brief and observational.

**Sample copy:**

> Hugin perches over the citations panel when a chat turn brought
> back retrieval hits. He doesn't speak — ravens don't — but you'll
> know what he's reading.

> If Hugin has flown back to his default perch, the last reply was
> ungrounded (no citations).

---

## Refur — the witness

**Voice:** alert, neutral, a bit shy. Doesn't push; just watches.

**Sample copy:**

> Refur appears at the chat's edge when Ember asks for permission
> to use a tool. He's not enforcing anything — he's keeping you
> company while you decide.

> The fox vanishes the moment you answer. He doesn't linger to
> nag.

---

## Heiðr — the keeper

**Voice:** steady, domestic, practical. The household goat.

**Sample copy:**

> Heiðr stands by the audit panel. Every time Ember finishes using
> a tool, Heiðr drops a small horn into the audit log — a tiny
> ritual that confirms the record was made.

> She doesn't move much. The horn is the gesture.

---

## Sumarbýfa — the ferry

**Voice:** busy, summer-warm, never anxious. Just always working
when work is to be done.

**Sample copy:**

> Sumarbýfa (summer-bee) ferries documents into your Well. When
> you see her, ingest is running. When she's gone, what she
> brought is yours.

> Multiple ingests = multiple bees. Each carries her own load.

---

## Geri-cub — the companion

**Voice:** plain, undemanding, present.

**Sample copy:**

> Geri-cub keeps you company. She doesn't do anything in particular
> — she's a wolf cub, and they don't have to. She'll yawn
> sometimes. When you go quiet, she sleeps.

> She's named after Odin's wolf Geri (the greedy one), but this
> Geri is small and harmless.

---

## Ask-sapling — the grower

**Voice:** patient, slow, alive in its quiet way.

**Sample copy:**

> Ask-sapling is a young Yggdrasil — a small ash tree growing in a
> pot beside the hearth. The longer you and Ember talk together,
> the more it grows. New conversation, new sapling.

> Don't try to water it. It's a TUI.

---

## Drift — the weather

**Voice:** distant, ambient, doesn't really have a voice. Like
weather.

**Sample copy:**

> Drift is winter weather. In the cool themes (Aurora, Barrow),
> tiny snowflakes drift across the hall. Quiet, slow, no sound.
> They don't land — they just pass.

> Drift isn't really a pet. Drift is *the day*.

---

## Funi-spark — the fire

**Voice:** primal, warm, doesn't need words. The fire IS the voice.

**Sample copy:**

> Funi-spark is the fire in the hearth. When Ember is thinking, it
> brightens. When she's resting, it's banked. You'll learn to feel
> her pace by watching it.

> A still hearth is fine — Ember is just listening.

---

## Ember-ember — the mark

**Voice:** simply present. The logo. Doesn't need a voice.

**Sample copy:**

> Ember-ember is the ember of the project name — the small mark
> that says "this is Ember." It's the logo. It doesn't do anything
> else.

> If you ever wonder which terminal pane Stofa is in: look for
> the ember-ember at the top-left.

---

## How these voices are used

In the help overlay:

```
┌─ Help: pets ──────────────────────────────────────────┐
│                                                        │
│  🔥  Funi-spark (the fire)                             │
│      Pulses when Ember is thinking.                    │
│                                                        │
│  Hugin (raven)                                         │
│      Perches over citations after retrieval.           │
│                                                        │
│  Refur (fox)                                           │
│      Watches during tool-approval prompts.             │
│                                                        │
│  Heiðr (goat)                                          │
│      Drops a horn when a tool call is audit-logged.    │
│                                                        │
│  Sumarbýfa (bee)                                       │
│      Ferries documents during ingest.                  │
│                                                        │
│  Geri-cub (wolf cub)                                   │
│      Keeps you company. Sleeps when idle.              │
│                                                        │
│  Press p to toggle pets · Esc to close                │
└────────────────────────────────────────────────────────┘
```

One line per pet. Friendly, brief, useful.

In the README/INSTALL docs, longer paragraphs (the "sample copy"
above) are used to introduce the cast.

---

## The discipline

These voices are *aboutness*, not literal speech. We never put
words in a pet's mouth (a pet saying "Hello!" to the operator
would be Clippy, which we reject).

What we do put in the world:

- Names (Hugin, Refur, etc. — fixed).
- Roles (one-liner per pet).
- Manner of acting (perches, drops, flies — the verbs that describe
  their behavior).
- The narration in docs.

What we don't:

- Dialogue from pets.
- "Personality systems" that surface stats or moods.
- Petnames in chat replies ("Hugin says: ...").

---

## Naming individual pets vs the species

We name the *species token* (Hugin, Refur). We don't name *individual*
instances:

- One bee in the chrome: still Sumarbýfa.
- Three bees during three concurrent ingests: still three Sumarbýfa.
  (No "Bee #1, Bee #2, Bee #3.")

This keeps the vocabulary small and predictable.

---

## What if an operator wants to rename a pet?

V1: no. The names are part of the design vocabulary.

V2 maybe: an operator could supply `stofa.pets.hugin.display_name`
in their config to rename their copy of Hugin. Internal references
still use `hugin`; only the operator-facing display string changes.
This is a small operator-friendliness; not committed.

---

## Closing

Each pet has a voice in the docs but not in the app. The voices are
the Scribe's tool for writing about Stofa with consistency. Same
register across every document. The pets stay silent in the hall;
their behavior is their speech.
