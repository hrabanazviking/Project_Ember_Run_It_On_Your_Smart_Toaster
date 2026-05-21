# 48 — Animation and Timing

When to move things; how fast; and how often. The discipline behind
"Stofa feels alive without being distracting."

---

## The principle: animation is information

Animation is justified when it conveys something the operator needs
to know. Animation is unjustified when it's decorative-only AND
costly to the operator's attention.

Stofa's animations fall into three categories:

1. **Status animations** — the hearth pulses to say "Funi is
   thinking."
2. **Pet animations** — Hugin flying to a new perch says "retrieval
   came back."
3. **Transition animations** — fade in / slide on screen push.
   (Used very sparingly.)

There are no purely decorative animations.

---

## The frame budget

We cap aggregate visible animation at **4 Hz**.

That means: across all visible moving things, no more than 4 frames
of motion per second total.

Why 4 Hz:

- Below 1 Hz: feels jerky, like the app is sluggish.
- 1-4 Hz: clearly intentional, comfortable to look at.
- 4-15 Hz: noticeable motion; can be distracting peripherally.
- > 15 Hz: looks "smooth" but is bandwidth-heavy and SSH-hostile.

Stofa stays in 1-4 Hz. Pets tick at 1 Hz max each. The hearth pulses
at 1 Hz when active. The chat token stream is "as fast as Funi
sends" but the *rendering* of streamed tokens uses Textual's
batched updates (max 30 Hz internally, but each frame is small).

Aggregate cap enforced by `PetLayer` throttling all subscribed pets
collectively.

---

## Specific animations

### The hearth pulse

When Funi is thinking, the hearth icon pulses through three states
at ~1 Hz:

```
frame 0: 🔥 (default tint)
frame 1: 🔥 (brighter tint)
frame 0: 🔥 (default tint)
frame -1: 🔥 (dimmer tint)
```

Visually, it's a soft brightness wave. Operator's eye sees "Funi
is working" without reading any text.

When Funi is idle: no animation. The hearth is still and dim.

### Pet idle motion

Most pets are still 95% of the time. Their "idle" state is a fixed
sprite.

When an event triggers a pet, it transitions over 2-3 frames
(at 1 Hz):

```
frame 0: pet at idle position
frame 1: pet in mid-transition (e.g., one cell over)
frame 2: pet at new position
```

After arriving, the pet stays at the new position until another
event.

This is the **"perch" model** — pets don't wander continuously; they
*perch* at meaningful positions and *move* on cue.

### Streaming chat tokens

Funi tokens arrive at maybe 20-40 tok/s. We render them as they
arrive but batched via Textual's internal frame timing (max 30 Hz).
Operator perceives smooth streaming. No special animation
beyond "the text appears."

### Screen transitions

When a screen pushes on top of Home:

- V1: instant swap (no transition).
- V2 considered: ~150ms fade-in. Decision: V1 stays instant for
  responsiveness; V2 may add subtle transitions if operators feel
  abrupt.

Esc back to Home is also instant.

### Modal appearance

ToolApprovalScreen, CommandPalette, HelpOverlay: instant appearance,
no slide-in. Their visibility IS the cue; transition would just
delay it.

### Resize

When the terminal resizes, Textual handles redraw. Stofa doesn't
animate the transition; it snaps to the new layout in one frame.

---

## What we never animate

- **Borders.** Borders don't pulse, don't fade.
- **Background colors.** No background-color transitions.
- **Text color.** Once rendered, text doesn't change color (unless
  the entire theme changes via `:theme`).
- **Pets continuously.** Each pet ticks once per second at most;
  no pet has a constant-motion animation.
- **Spinners except during loading.** Spinners are operator-visible
  only when there's an actual long operation; never as decoration.
- **Notifications.** No slide-in toast notifications. StatusBar
  highlights briefly (1 frame) for events.

---

## SSH-friendly rate

Eirwyn (Persona 5) is on SSH. Animation budget:

| Mode | Aggregate animation | Pet motion |
|---|---|---|
| `stofa.minimal_redraw: false` (default) | 4 Hz | per-pet 1 Hz, aggregate 4 Hz |
| `stofa.minimal_redraw: true` (SSH-friendly) | 0 Hz | 0 (pets visible but still) |

`minimal_redraw: true` auto-engages when:

- `SSH_CONNECTION` env var is set on first launch.
- Operator explicitly sets in config.

Operator can override either way.

---

## Vestibular-sensitive operators

For operators sensitive to motion (per
[`46_ACCESSIBILITY.md`](46_ACCESSIBILITY.md)):

- `p` key disables pet animation entirely (pets stay visible but
  still).
- A separate config: `stofa.hearth_pulse: false` stops the hearth
  pulsing.
- V2 will respect OS `prefers-reduced-motion`.

---

## Timing budgets

Per [`../operations/90_PERFORMANCE_BUDGETS.md`](../operations/90_PERFORMANCE_BUDGETS.md):

| Event | Budget |
|---|---|
| Keypress to visual response | < 16ms |
| Screen push to fully rendered | < 50ms |
| Theme swap | < 100ms |
| Startup to first interactive frame | < 500ms |
| Resize to reflowed | < 33ms |
| Pet animation frame | 1 frame / second / pet (1000ms) |
| Hearth pulse frame | 250ms / state-transition |

These are *budgets*, not guarantees. CI snapshot tests verify the
boot time and screen-push time on a reference machine.

---

## What "feels alive" means

The pets + hearth + status bar together create the *illusion of
ongoing activity*, even when nothing is actually happening. This
matters because:

- A still screen feels frozen, even when it's just idle.
- A subtly animate screen feels responsive, even when it's idle.
- The "responsive idle" makes the operator trust that when they
  press a key, something happens.

This is the same trick Spotify uses with the playback bar — the
bar shows seconds ticking, which is *information* (current position)
but also *reassurance* (the app is alive).

Stofa's reassurance comes from:

- The hearth (still, dim when idle; pulsing when working).
- The pets (mostly still; occasional ambient motion).
- The status bar (clock ticks; realm states refresh quietly).

Together, ~1-2 Hz of total visible motion at any time. Calm,
inhabited, alive.

---

## Animation in error states

When something goes wrong:

- **No animation.** Errors are *still*. They demand attention through
  position + color + prefix, not through motion.
- **The hearth stops pulsing** when Funi is unreachable. (Replaces
  the "thinking" signal with "no spark.")
- **The bee disappears** when ingest stops with an error (rather
  than visually contorting).

Stillness in errors is the right response. The operator's eye should
land on the error text, not be drawn to motion that's now meaningless.

---

## Closing

Animation in Stofa is **earned** (every motion has a reason),
**bounded** (4 Hz aggregate), **opt-out-able** (vestibular-sensitive
operators can freeze everything), and **respectful of SSH**
(minimal-redraw mode kills it). The pets are alive because they
sometimes move; the hearth is alive because it sometimes pulses;
the rest of the screen is calmly still. That equilibrium is what
makes Stofa feel like a hall someone lives in rather than a
slideshow.
