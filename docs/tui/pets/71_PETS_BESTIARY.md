# 71 — The Pets Bestiary

The nine pets in V1. Each has a name, a role, an appearance, a
behavior summary, and an "in their words" voice (used in operator-
facing copy about the pet, not by the pet itself — pets don't talk).

---

## 1. Hugin — the Raven

**Role:** retrieval-citation indicator.

**Subscribes to:** `RetrievalReturned`, `RetrievalFailed`.

**Default perch:** bottom-left, by the chrome footer.

**Active behavior:** when a chat turn returns retrieval hits, Hugin
flies to perch over the citations panel. He stays there until the
operator scrolls past those citations, then returns to the default
perch.

**Appearance:** small slate-grey raven, head-and-body silhouette,
about 4×3 cells. (Sprite in [`73_PETS_SPRITE_GUIDE.md`](73_PETS_SPRITE_GUIDE.md).)

**Voice (operator-facing copy):** *"Hugin is the messenger raven who
fetches knowledge from your Well and lets you see what was found.
He perches on the freshest information."*

**Why his name:** Hugin (*hugr* = "thought" in Old Norse) is one of
Odin's two ravens (along with Munin) who fly the world each day
gathering news. The retrieval-indicator role fits perfectly. We use
lowercase "hugin" (not "Huginn") because the pet is a *small h*
version, not the mythic one.

---

## 2. Refur — the Fox

**Role:** tool-approval companion.

**Subscribes to:** `ToolCallProposed`, `ToolApprovalDecided`.

**Default perch:** hidden; only appears during tool approval.

**Active behavior:** when Funi proposes a tool call, Refur appears
at the bottom of the chat panel, sitting alert (his "I'm watching"
sprite). When the operator answers (approve / deny), Refur tilts
his head once and vanishes back to hidden.

**Appearance:** small warm-tan fox, sitting upright, ears alert,
about 4×4 cells.

**Voice:** *"Refur the fox shows up when Ember asks for permission.
He's not a guard — he's a witness, here so you can decide with
company."*

**Why his name:** *Refur* is just "the fox" in Icelandic / Old Norse.
Plain naming, like a household nickname.

---

## 3. Heiðr — the Goat

**Role:** audit-log scribe; drops a tiny mead-horn glyph when a
tool call is logged.

**Subscribes to:** `ToolExecutionFinished`.

**Default perch:** bottom-right, by where the StatusBar tags audit
activity.

**Active behavior:** after a tool call completes and the audit log
records it, Heiðr drops a small horn glyph (`◊` or `᠀`) that fades
out over 2 seconds. Heiðr herself doesn't move much; the dropped
horn is the visual signal.

**Appearance:** small cream-colored goat, four legs visible, simple
horn shape on her head, about 5×4 cells.

**Voice:** *"Heiðr is the household goat. Every time Ember uses a
tool, Heiðr offers a horn of mead to the audit log — a small ritual
of record-keeping."*

**Why her name:** *Heiðr* (Heath / Bright / Honor) was a name used
for several Norse mythological figures (including a seeress in the
Völuspá). Domestic register: this is a goat, not a goddess. We
chose Heiðr over the more obvious "Heiðrún" (the mythic mead-goat)
to keep the register household.

---

## 4. Sumarbýfa — the Bee

**Role:** ingest worker. One bee per active ingest task.

**Subscribes to:** `IngestStarted`, `IngestProgress`, `IngestFinished`.

**Default perch:** hidden; only appears during ingest.

**Active behavior:** when ingest starts, a Sumarbýfa appears at the
top of the WellScreen (or chrome header if operator is elsewhere).
She animates a small left-right ferry motion as documents are
processed. When ingest finishes, she returns to a "delivering"
position for a moment, then disappears.

**Appearance:** tiny honey-gold bee with two faint wing strokes,
about 3×2 cells.

**Voice:** *"Sumarbýfa (summer-bee) ferries documents into your
Well. When she's active, ingest is running. When she's gone, you
have what she brought."*

**Why her name:** *Sumarbýfa* = "summer-bee" (compound; *sumar* +
*býfa*, the latter being a poetic word for bee). Distinctive
enough to be ornamental; long enough to be obviously special.

---

## 5. Geri-cub — the Wolf Cub

**Role:** idle companion. Just there.

**Subscribes to:** (none — ambient).

**Default perch:** bottom-left or wherever there's empty space.

**Active behavior:** mostly still. Every few minutes (random
interval), yawns once (one-frame sprite swap). When Stofa has been
idle (no operator input) for > 5 minutes, Geri-cub curls up
("sleeping" sprite).

**Appearance:** small warm-brown wolf pup, curled or sitting, about
5×4 cells.

**Voice:** *"Geri-cub keeps you company. She doesn't do anything in
particular — she's a wolf cub, and they don't have to. She'll yawn
sometimes. She'll sleep when you do."*

**Why her name:** Geri is one of Odin's two wolves (with Freki).
"Geri-cub" makes it clear this is a *small Geri*, not the mythic
warrior wolf. Domestic register.

---

## 6. Ask-sapling — the Ash

**Role:** session-length indicator. Grows as the chat goes longer.

**Subscribes to:** (timer-based; ticks once per ~10 conversation
turns).

**Default perch:** in a pot, bottom corner.

**Active behavior:** starts as a 1-leaf sprite. Every ~10 conversation
turns, gains another sprite frame (more leaves). Caps at ~6 leaves
(roughly 60+ turns). When the chat session resets, Ask-sapling
resets to 1 leaf.

**Appearance:** small ash sapling in a pot. Sprite progression:
1 → 2 → 4 → 6 leaves, with the trunk getting slightly taller.

**Voice:** *"Ask-sapling is a young Yggdrasil — a small ash tree
growing in a pot beside the hearth. The longer you and Ember talk
together, the more it grows. New conversation, new sapling."*

**Why its name:** *askr* = "ash tree" in Old Norse, the wood from
which the first man was made (per Norse cosmology — Askr and
Embla). "Ask-sapling" reads as "young ash."

---

## 7. Drift — the Snowflake Spirit

**Role:** theme-specific ambient (Aurora and Barrow themes only;
hides in Midgard, Ginnungagap, Solstice).

**Subscribes to:** (theme change events; otherwise timer-based).

**Default perch:** drifts across the chrome at ~1 per minute.

**Active behavior:** A small `*` or `❄` character appears at one
side of the screen and drifts horizontally across, taking ~10
seconds to cross. Disappears when off-screen. Maximum one Drift
visible at a time.

**Appearance:** A single `❄` or `*` glyph.

**Voice:** *"Drift is winter weather. In the cool themes (Aurora,
Barrow), tiny snowflakes drift across the hall. Quiet, slow, no
sound. They don't land — they just pass."*

**Why its name:** *Drift* = the simple English word, no Norse
counterpart. (Old Norse for snow is *snjór*; "Drift" reads better as
a pet name.) Default opt-in; some operators find ambient motion
distracting.

---

## 8. Funi-spark — the Hearth Flame

**Role:** Funi thinking indicator. Pulses while Funi is processing.

**Subscribes to:** `FuniRequestStarted`, `FuniRequestFinished`,
`FuniRequestFailed`.

**Default perch:** fixed in the chrome header (top-right), right of
the Stofa title.

**Active behavior:** Idle: still, dim. When Funi starts thinking:
pulses softly (brightness wave at ~1 Hz). When Funi finishes:
returns to still + dim with a brief moment of full brightness
(like a flame settling).

**Appearance:** Small flame glyph (`🔥` with fallback `^`). Color
shifts between `$hearth-base` (dim) and `$hearth-glow` (bright).

**Voice:** *"Funi-spark is the fire in the hearth. When Ember is
thinking, it brightens. When she's resting, it's banked. You'll
learn to feel her pace by watching it."*

**Always on** — operator can't disable Funi-spark; it's part of the
chrome.

---

## 9. Ember-ember — the Logo

**Role:** static brand glyph. Doesn't move. Doesn't react. Always
there.

**Subscribes to:** nothing.

**Default perch:** top-left of chrome, before the "Stofa" word.

**Active behavior:** none.

**Appearance:** small ember dot/glyph (`●` or `◉`) tinted with the
hearth color.

**Voice:** *"Ember-ember is the ember of the project name — the
small mark that says 'this is Ember.' It's the logo. It doesn't
do anything else."*

**Always on** — part of the chrome identity.

---

## How they fit together — a visual

A typical HomeScreen with default pets:

```
● Stofa ─── ᛞ ᛞ ᛞ ─── Home ─────────────────────── 🔥 ─────╮
↑                                                            ↑
ember-ember                                            funi-spark
                                                       (pulses on)

  ┌──── Conversation ──┐ ┌──── Well ────────────────┐
  │                     │ │                            │
  │  ...                │ │  ...                       │
  │                     │ │            🐝              │     ← Sumarbýfa during ingest
  │                     │ │      (bee ferries)        │
  └─────────────────────┘ └────────────────────────────┘

  ┌──── Realms ────────┐ ┌──── Tools ────────────────┐
  │  ● Funi ok          │ │  ...                       │
  │  ● Well ok          │ │                            │
  │  ● MCP ok           │ │  🦊                        │     ← Refur during tool approval
  │  ● Strengr ok       │ │  (fox watches)            │
  └─────────────────────┘ └────────────────────────────┘

  [Geri-cub sleeps here]      [Hugin perches here]
     🐺                            🐦
```

Six pets visible. None are loud. Each tells the operator something
about the hall's current state.

---

## Closing

Nine pets. Each with a job, a name, a perch, a voice. Some always-on
(funi-spark, ember-ember), some event-triggered (hugin, refur, heidr,
sumarbýfa), some ambient (geri-cub, drift, ask-sapling). Together
they make Stofa feel like *a place someone lives in*, not just a
program.
