# 70 — Pets Overview

The pets system in implementation terms. The *why* lives in
[`../vision/04_PETS_VISION.md`](../vision/04_PETS_VISION.md); the
per-pet specs in [`71_PETS_BESTIARY.md`](71_PETS_BESTIARY.md); the
animation engine in [`72_PETS_BEHAVIOR_ENGINE.md`](72_PETS_BEHAVIOR_ENGINE.md);
the sprite reference in [`73_PETS_SPRITE_GUIDE.md`](73_PETS_SPRITE_GUIDE.md);
the helpfulness contract in [`74_PETS_HELPFULNESS.md`](74_PETS_HELPFULNESS.md);
personalities in [`75_PETS_PERSONALITY_PROFILES.md`](75_PETS_PERSONALITY_PROFILES.md).

This file is the **map**.

---

## What the pets system is

A `PetLayer` widget that floats on top of the main screens. Each
pet is a sub-widget inside the layer. Pets subscribe to messages
on the app event bus and animate / re-position in response.

```
┌──── Screen content ───────────────────────┐
│                                            │
│   <actual screen here>                     │
│                                            │
│                                            │
│       [pet sprites overlay here]            │  ← PetLayer (transparent)
│                                            │
│                                            │
└────────────────────────────────────────────┘
```

The pet layer is Textual's only `layers` usage — it lives in a
layer above all other widgets, so pets can appear "on top of"
panels without disturbing layout.

---

## The 9 V1 pets

| Pet | Role | Subscribes to | Default enabled? |
|---|---|---|---|
| **Hugin** (raven) | retrieval indicator | `RetrievalReturned` | ✓ |
| **Refur** (fox) | tool-approval guide | `ToolCallProposed` | ✓ |
| **Heiðr** (goat) | audit-log scribe | `ToolExecutionFinished` | ✓ |
| **Sumarbýfa** (bee) | ingest worker | `IngestProgress` | ✓ |
| **Geri-cub** (wolf cub) | idle companion | (none; ambient) | ✓ |
| **Ask-sapling** (ash) | session-length tracker | (timer-based) | ✗ (opt-in) |
| **Drift** (snowflake) | theme-specific ambient | (theme = aurora/barrow) | ✗ (opt-in) |
| **Funi-spark** (hearth flame) | Funi thinking | `FuniRequestStarted` / `Finished` | ✓ (always-on) |
| **Ember-ember** (logo) | static brand glyph | (none) | ✓ (always-on) |

Total visible at any one time: typically 3-5 (the chrome's
ember-ember + funi-spark, plus event-triggered ones).

---

## Pet lifecycle states

Every pet has three states:

1. **Hidden** — not rendered (when the operator has disabled it,
   or the underlying event hasn't happened).
2. **Idle** — rendered, at its idle position, with idle sprite.
3. **Active** — temporarily transitioning or showing an event-
   specific sprite.

A pet stays in Active for at most ~5 seconds, then returns to Idle.

---

## Per-pet implementation pattern

Each pet is a `PetWidget` subclass:

```python
class HuginRaven(PetWidget):
    NAME = "hugin"
    DEFAULT_ENABLED = True
    SUBSCRIBES_TO = (RetrievalReturned, RetrievalFailed)

    def on_retrieval_returned(self, event: RetrievalReturned) -> None:
        if not event.hits:
            return
        # Fly to perch over the citations panel
        self.set_state(active=True)
        self.fly_to(target="citations_panel", offset=(0, -1))

    async def on_idle_timeout(self) -> None:
        # After 5 seconds of no activity, return to perch
        self.fly_to(target="default_perch")
```

Each pet's class is ~50-100 lines: the SUBSCRIBES_TO declaration,
the event handlers, the position-management helpers (which the
base class provides), and the sprite reference.

---

## How pets get a position

Pets don't have free-floating positions. They have **named perches**:

```python
PERCHES = {
    "default_perch": (col=2, row=-2),         # bottom-left, idle home
    "above_chat_input": (col=-15, row=-3),    # near where input is
    "over_citations": (relative_to="citation_card", offset=(0, -1)),
    "by_audit_log": (col=-2, row=-2),         # bottom-right
    "asleep": (col=2, row=-2),                # same as default
    "ingest_active": (col="middle", row=-2),
}
```

Pets transition between named perches. The PetLayer resolves named
perches to actual cells based on current screen size and content.

This is what makes the responsive design tractable: a pet doesn't
know "I'm at (col=80, row=20)"; it knows "I'm at the default_perch,"
and the layer figures out where that is.

---

## Animation budget enforcement

Per [`../ux-science/48_ANIMATION_AND_TIMING.md`](../ux-science/48_ANIMATION_AND_TIMING.md):

- **Per-pet rate cap**: 1 Hz (each pet ticks at most once per
  second).
- **Aggregate cap**: 4 Hz (across all visible pets combined).

`PetLayer` enforces both:

```python
class PetLayer(Widget):
    async def _tick_loop(self):
        while True:
            await asyncio.sleep(0.25)  # 4 Hz check
            for pet in self.visible_pets:
                if pet.last_tick_age >= 1.0:  # at least 1s
                    if self.aggregate_ticks_this_second < 4:
                        pet.advance_frame()
                        pet.last_tick_age = 0
                        self.aggregate_ticks_this_second += 1
```

When the operator presses `p` to disable pets:

```python
def on_pets_toggled(self, event: PetsToggled) -> None:
    for pet in self.pets.values():
        pet.set_state(hidden=True)
    self.refresh()
```

Immediate, no animation, all pets vanish.

---

## When the operator opts in / out

Per-pet via `ember.yaml`:

```yaml
stofa:
  pets_enabled: true
  pets:
    hugin: true
    refur: true
    heidr: true
    sumarbyfa: true
    geri_cub: true
    ask_sapling: false       # opt-in
    drift: false             # opt-in (theme-specific anyway)
    funi_spark: true         # can't be turned off (chrome)
    ember_ember: true        # can't be turned off (logo)
```

Or via Settings → Stofa → Pets section (checkboxes).

Or via the keymap (`p` toggles ALL pets on/off; not per-pet).

---

## What pets share

All pets:

- Live in the same `PetLayer`.
- Use the same animation budget (per-pet 1 Hz, aggregate 4 Hz).
- Have a hidden / idle / active state model.
- Have ASCII fallback sprites.
- Have per-theme color tints (per [`../architecture/15_THEMING_SYSTEM.md`](../architecture/15_THEMING_SYSTEM.md)).
- Are individually toggle-able.

This common contract is what makes the pets system *a system* and
not a pile of one-offs.

---

## What pets DO NOT do

- **Talk.** No speech bubbles, no text from a pet.
- **Pop up.** They appear and disappear in their layer; never
  modal.
- **Block input.** Operator can always type / press keys; pets are
  pure UI.
- **Persist state across sessions.** A pet doesn't remember what
  it was doing yesterday; it starts fresh each Stofa launch.
- **Generate.** Operators can't customize a pet's behavior or look
  in V1.
- **Track operator activity.** No counters, no "you've used Stofa
  for 42 hours, here's a special pet."

---

## V2 ideas (placeholder)

After V1:

- **Plugin pets** (per [`../architecture/18_PLUGIN_ARCHITECTURE.md`](../architecture/18_PLUGIN_ARCHITECTURE.md)).
- **Seasonal pets** that appear in specific themes/conditions
  (Drift fades in winter scenes).
- **Operator-customizable position**: drag the default_perch.
- **Pet "moods"**: subtle sprite variants based on time of day.

V2 ideas are sketches, not commitments.

---

## Closing

The pet system is a small, disciplined, configurable, opt-out-able
ambient-info-display layer. Nine pets in V1. Each one ~80 LOC.
Subscribes to existing messages; doesn't invent data. Falls back to
ASCII. Honors animation budget. Operators get cuteness *and*
useful peripheral signaling — without any pet ever getting in their
way.
