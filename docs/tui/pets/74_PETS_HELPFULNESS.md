# 74 — Pets Helpfulness Contract

What each pet **does for the operator** besides being cute. The
"earn their keep" specification.

---

## Why this matters

The pets are not optional cuteness. They are *labeled ambient
status indicators*. The bee is the most direct example: when the
bee is visible, ingest is running. When it's gone, ingest is done.
The operator doesn't have to read a status string; they read the
*presence* of the bee.

This document specifies the *information* each pet conveys, what
operator question it answers, and how reliable the signaling is.

---

## Pet-by-pet helpfulness

### Hugin (raven)

**Operator question it answers:** *"Did the last chat turn use my
Well's knowledge?"*

**Signal:** Hugin perches over the citations panel when
`RetrievalReturned` returned hits. Hugin returns to default perch
when there are no hits (or when no chat turn is in flight).

**Why this is helpful:** Operators can scan the screen and *see*
whether Ember's answer was grounded in retrieval, before reading
the citations themselves. Reduces cognitive load.

**Failure mode:** if RetrievalFailed fires, Hugin returns to
default perch (NOT a special "error" position). The error itself is
visible in the panel; Hugin doesn't double-signal it.

**Reliability:** depends on the WellService firing the message.
WellService is well-tested; reliability is high.

---

### Refur (fox)

**Operator question it answers:** *"Is there a tool-approval
prompt I need to attend to?"*

**Signal:** Refur appears at the bottom of the chat panel during
tool-approval prompts. He disappears when the operator responds.

**Why this is helpful:** When the operator is reading the chat,
the tool-approval modal appears centered. Refur's presence at the
bottom *also* signals "approval needed" through peripheral vision —
the operator who looked away briefly sees Refur and knows to
attend.

**Failure mode:** if the ToolApprovalScreen is dismissed without
input (e.g., operator presses Esc), Refur dismisses too. No
"linger to remind" — that would be naggy.

**Reliability:** the ToolCallProposed event drives Refur; same
reliability as the approval flow itself.

---

### Heiðr (goat) and the dropped horn

**Operator question it answers:** *"Was that tool call audit-logged?"*

**Signal:** When ToolExecutionFinished fires, Heiðr drops a small
horn glyph (`◊`) that fades over 2 seconds.

**Why this is helpful:** The audit log is invisible by default
(it's a JSONL file). Heiðr's horn confirms "yes, that just got
written." Operator sees the horn → trust restored that the audit
trail exists.

**Failure mode:** if audit-log write fails (disk full,
permissions), the AuditService logs a warning; Heiðr still drops a
horn (because we don't have a clean per-call "audit-write-succeeded"
event). V2 may add a more accurate signal.

**Reliability:** moderate (close, not exact). Worth improving.

---

### Sumarbýfa (bee)

**Operator question it answers:** *"Is ingest running, and how
far along is it?"*

**Signal:** The bee is *visible* when ingest is active. The bee
**moves more frequently** when ingest is making fast progress, and
slows when it stalls. When ingest completes, the bee deposits
(briefly shows `depositing` frame) and disappears.

**Why this is helpful:** Operators can leave Stofa on the Chat
screen and *peripherally* know "ingest is going." Returning to
WellScreen shows the actual progress bar; the bee is the
cross-screen ambient signal.

**Failure mode:** if ingest stalls for > 30 seconds (no progress),
the bee freezes at its last frame. Operator can check WellScreen
to see what's wrong.

**Reliability:** high — the IngestProgress message fires reliably
during active ingest.

---

### Geri-cub (wolf cub)

**Operator question it answers:** *"Is Stofa alive?"*

**Signal:** Geri-cub is always present (if enabled). She yawns
occasionally (random 1-5 min interval). She curls up
("sleeping" sprite) when Stofa has been idle for > 5 minutes.

**Why this is helpful:** The "is the app frozen?" question.
Operators looking at a still screen sometimes wonder if their TUI
hung. Geri-cub's slow ambient yawning is a *non-noisy* "I'm here,
nothing is wrong, everyone is just being quiet."

**Failure mode:** none in the usual sense; Geri-cub is ambient and
unreliable signaling is not a fail (it's the design).

**Reliability:** n/a — ambient.

---

### Ask-sapling (ash)

**Operator question it answers:** *"How long has this conversation
been going?"*

**Signal:** Sapling grows leaves (1 → 2 → 4 → 6) over conversation
length (every ~10 turns).

**Why this is helpful:** Operators in long sessions can see at a
glance "I've been talking with Ember for a while." It's a small
sense-of-place — the sapling has grown, like a real plant on a desk
during a long task.

**Failure mode:** if the session resets (new Stofa launch), sapling
returns to 1 leaf. No persistence of sapling state. Operators
who want a "growing tree across sessions" are out of luck in V1.

**Reliability:** entirely local; high.

---

### Drift (snowflake)

**Operator question it answers:** *"What theme am I in?"*

**Signal:** Drift appears (occasional snowflake drifts across
chrome) in Aurora and Barrow themes. Disappears in Midgard
(daylight summer), Ginnungagap (void; no precipitation), Solstice
(too saturated for snow).

**Why this is helpful:** Subtle reinforcement of the theme's mood.
Aurora is twilight + snow; Drift completes the picture.

**Failure mode:** if the theme switch happens mid-session, Drift
fades in or out within a frame. No glitches.

**Reliability:** n/a — ambient decoration.

---

### Funi-spark (hearth flame)

**Operator question it answers:** *"Is Funi thinking right now?"*

**Signal:** Funi-spark pulses (color cycles between `$hearth-base`
and `$hearth-glow` at ~1 Hz) while Funi is processing. Stops
pulsing when Funi finishes.

**Why this is helpful:** The most important pet for live signaling.
Operators learn within minutes: "pulsing hearth = Ember is thinking,
wait." The signal is right where the operator's eye expects to find
"ready/busy" status.

**Failure mode:** if FuniRequestStarted fires but
FuniRequestFinished doesn't (e.g., a hang), the hearth keeps
pulsing indefinitely. Operator can Ctrl-C to interrupt. The pulse
itself is the cue that *something* is still going.

**Reliability:** very high — driven by the FuniService event flow.

---

### Ember-ember (logo)

**Operator question it answers:** *"Is this Stofa?"*

**Signal:** Always present in the top-left of chrome.

**Why this is helpful:** Brand recognition. In a tmux pane next to
other tools, the operator's eye immediately picks out "that's
Stofa" from the logo.

**Failure mode:** none.

**Reliability:** static; perfect.

---

## What pets DON'T signal

To be clear about scope:

- **Not connection latency.** Pets don't speed up or slow down
  based on network conditions. (Maybe V2.)
- **Not specific error types.** Errors are surfaced in the panel
  text, not via pet color/posture. The pets de-escalate, they
  don't alarm.
- **Not operator activity.** Pets react to *system* events, not to
  operator typing. (Geri-cub's "idle when operator is idle" is the
  closest exception.)
- **Not future events.** No pet "warns" the operator about a
  prediction. Pets react to the present.

These limits keep pets understandable. An operator who learns "bee
= ingest active" and "fox = approval needed" has a complete model;
nothing surprises them.

---

## Per-pet reliability summary

| Pet | What it signals | Reliability |
|---|---|---|
| Hugin | retrieval used | high |
| Refur | tool approval pending | high |
| Heiðr | tool was audit-logged | moderate (event-coupling could improve) |
| Sumarbýfa | ingest running | high |
| Geri-cub | Stofa is alive | ambient (n/a) |
| Ask-sapling | conversation length | high |
| Drift | theme is twilight/cool | n/a (decorative) |
| Funi-spark | Funi is thinking | very high |
| Ember-ember | this is Stofa | perfect (static) |

---

## How operators learn pet semantics

We do NOT ship a "pet meanings legend." Discovery is via:

1. **Doing things.** Operator runs ingest, sees the bee, learns.
2. **The Help overlay.** `?` mentions in the legend section: "Pets:
   Hugin signals retrieval; Refur signals approval; bee signals
   ingest; ...".
3. **Hover tooltips (V2).** Hovering over a pet briefly tooltips
   its name + role.

The pets *should* be intuitive enough that operators figure out
most of them without reading. The bee is *obviously* working when
ingest is happening; the fox is *obviously* watching during
approval.

---

## Closing

Each pet has a job. Each job answers a real operator question.
Each signal is reliable (or honestly labeled as ambient). The
pets are pretty AND useful — exactly the load-bearing
combination described in the pets-vision doc.
