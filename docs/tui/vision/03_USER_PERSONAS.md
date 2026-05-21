# 03 — User Personas

Stofa is designed for **five concrete personas**. Every screen, every
keybinding, every default has to make sense for at least three of them.
This document describes who they are, what they want, and how Stofa
serves each.

These are not market segments. They are real archetypes from the
operator community the README is aimed at, distilled down to make
trade-off decisions easier.

---

## Persona 1 — Volmarr the Sovereign-AI Operator

> *"I run my own everything. I want a real AI that lives on my
> hardware and respects my data. Nothing leaves the machine."*

**Background:** mid-career engineer / philosopher / craftsperson. Runs
Linux at home. Has a Pi cluster, a tailnet, a Postgres they care about.
Knows what `ssh -L` does. Suspicious of cloud-AI offerings.

**What they want from Stofa:**
- A *home* for Ember, not a tool they invoke and quit.
- Full visibility into what's happening (Well counts, MCP server
  states, audit log).
- Confidence that nothing leaks (no telemetry, no auto-update
  pings).
- Beautiful + considered, because they care about craft.

**What they will *not* tolerate:**
- Sign-in screens.
- Telemetry opt-outs that default to "on."
- Pushed notifications.
- Sluggish redraw.
- Anything that breaks under Wayland / tmux / SSH.

**How Stofa serves them:**
- The status bar is the truth — Funi up, Well at N docs, MCP servers
  healthy, last audit-log entry N seconds ago.
- The Doctor screen is one keypress (`d`); they can verify health
  without quitting chat.
- The Settings screen edits `ember.yaml` with operator-friendly
  validation; never edits anything else.
- The pets can be turned off in one keypress (`p`) and stay off.

---

## Persona 2 — Iðunn the Curious Newcomer

> *"I just read the README. The 'toaster' joke made me smile. I have no
> idea what an LLM is, but the author seems like a person I could
> trust."*

**Background:** student, writer, hobbyist, retiree, librarian — could
be anyone who reads a friendly README and decides to give a thing a
chance. May not have used a terminal much. Might be on macOS with
Homebrew, might be on a Pi they got for Christmas.

**What they want from Stofa:**
- To *understand what they're looking at* within 30 seconds.
- To be told what to do next.
- To not feel stupid.
- Cute pets are a plus.

**What they will *not* tolerate:**
- Acronyms without expansion.
- Errors that look like stack traces.
- Anything that requires them to read a man page first.
- A wizard that asks them about embedding dimensions before they've
  even had a conversation.

**How Stofa serves them:**
- First launch goes straight into Hjarta in cozy-wizard mode. Three
  questions, with helpful defaults pre-filled. They can press `?` on
  any field to see what it means.
- After Hjarta, the chat screen has a placeholder text in the input
  box: "Say hi to {Ember's name}. Press `?` any time for help."
- A small fox pokes its head out of the citations panel on the first
  conversation, with a one-line tip: "I'll show you where Ember found
  her answers."
- Errors are sentences. Never "Traceback (most recent call last)".

---

## Persona 3 — Sigrún the Ruthless Power-User

> *"I have keybindings for everything. I haven't reached for a mouse in
> seven years. If I have to click anything, I will write a script that
> does it for me."*

**Background:** career engineer or sysadmin. Lives in neovim and tmux.
Knows lazygit by heart. Has strong opinions about modal editing.

**What they want from Stofa:**
- Every action keyboard-bindable.
- A help overlay that shows the *current screen's* bindings, organized
  by section.
- Configurable bindings (vim-style HJKL, or arrow keys, both work).
- A command palette (Ctrl-P) that fuzzy-searches everything.
- No mouse required, ever.

**What they will *not* tolerate:**
- Mouse-only actions.
- Two-step actions when one would do (no "click then confirm").
- Confirmations on non-destructive operations.
- Modal dialogs that grab focus without an explicit action.

**How Stofa serves them:**
- Default keymap is vim-shaped (`hjkl` navigates panels;
  `gg`/`G` jumps to top/bottom of scrollable; `:` opens command
  palette).
- `?` shows the current-screen bindings, grouped.
- `Ctrl-P` opens the universal command palette.
- Every keymap key is rebindable via `stofa.keymap` in `ember.yaml`.
- Mouse is supported but never required.

---

## Persona 4 — Védis the Cozy Operator

> *"I work from home. My desk faces a window. I want the tools I use
> all day to feel like part of the room, not visiting card-table
> hardware."*

**Background:** any age, any field. Cares about how their workspace
*feels*. Uses a nice mechanical keyboard, decorates their dotfiles
folder with comments, has at least one houseplant within arm's reach.

**What they want from Stofa:**
- Visual warmth. Not corporate, not nerd-cave, just *nice*.
- Smooth animations (the spinning hearth, the streaming-text shimmer).
- The pets, on.
- A theme they can pick to match their wall colors.

**What they will *not* tolerate:**
- Default-Microsoft-blue.
- Loud red error states.
- Anything Brutalist.
- Pets that move so often they become a distraction.

**How Stofa serves them:**
- Five built-in palettes: Aurora (twilight default), Midgard (warm
  earth), Ginnungagap (true-black void), Solstice (high contrast),
  Barrow (colorblind-safe).
- Pets opt-in (configurable), and even when on they animate sparingly
  and predictably.
- The hearth icon pulses to a slow ~1Hz when Funi is thinking; the
  rest of the time it's still.

---

## Persona 5 — Eirwyn the Pi-Class Operator

> *"My computer for Ember is a Raspberry Pi 5 in a 3D-printed case
> behind my monitor. I SSH into it from my laptop. Everything needs to
> run smoothly over the network."*

**Background:** anyone running Ember on small / remote / shared
hardware. SSH-only operator. Sometimes on flaky wifi. Cares about
bandwidth.

**What they want from Stofa:**
- Low-bandwidth-friendly redraw (no full-screen repaints every frame).
- Smooth over high-latency SSH (no animations that look bad jittered).
- Graceful degradation when the SSH connection blips.

**What they will *not* tolerate:**
- 60fps animation that saturates the SSH pipe.
- Full-screen redraws (paints the operator's connection slow).
- Behavior that depends on `mouse_tracking_xterm` extensions their
  server doesn't speak.

**How Stofa serves them:**
- Render uses the Textual framework's diff-based updates; only changed
  cells get repainted.
- Animations cap at ~15fps; pet motion ticks at ~1Hz when active.
- A `--minimal-redraw` flag tells Stofa to use ASCII box-drawing and
  freeze pet animations entirely.
- Auto-detects SSH (presence of `SSH_CONNECTION` env var) and asks at
  first launch: "I notice you're on SSH. Use the SSH-friendly defaults?"

---

## Cross-persona invariants

These are the things that have to hold for every persona, regardless
of preferences:

1. **First-launch usability under 60 seconds.** Every persona can
   land on a usable chat screen, having made one decision (or zero),
   within a minute.
2. **`?` always tells you what you can do.** All five personas
   benefit from a contextual help overlay.
3. **`q` always quits cleanly.** No persona ever gets stuck.
4. **Operator data is never silently transmitted.** Sovereign by
   default; opt-in for anything otherwise.
5. **Everything is configurable in `ember.yaml`.** Power-users can
   rebind; cozy-users can pick themes; newcomers can stay on defaults.

---

## What we are NOT designing for

To be honest, here are personas Stofa is **not** trying to serve. We
won't build features that only matter to these groups, and we won't
let their feedback warp the design.

- **Enterprise admins managing 100 Ember installs.** That's Bifröst's
  job when it ships. Stofa is a single-operator surface.
- **Teams collaborating in real-time.** No multiplayer cursor; no
  collaborative editing. Different software.
- **Pure-mouse users.** Stofa supports mouse, but doesn't optimize
  for the mouse-only operator (they're better served by Auga, the
  future GUI).
- **Read-only kiosk users.** No "demo mode" or "anonymous browsing
  mode." Stofa is operator software.

---

## How personas inform decisions

When a design choice comes up, the question is:

> Which personas does this serve? Which does it harm?

- A choice that serves 4+ personas wins.
- A choice that serves 2-3 but harms none is OK.
- A choice that serves 1 and harms others is rejected.
- A choice that's good for power-users but invisible to newcomers is
  OK (configurability).
- A choice that's good for newcomers but annoying to power-users is
  OK *only if* power-users can turn it off.

Example: **animated pets on by default**.
- Iðunn ✓ (cute, makes them smile).
- Védis ✓ (cozy warmth).
- Volmarr — neutral (one keypress to turn off).
- Sigrún — neutral (one keypress to turn off).
- Eirwyn ✓ if the animation cost is bounded; we cap at 1Hz so it is.
- **Verdict: ship.**

Example: **default keybinding `hjkl` over arrow keys**.
- Sigrún ✓ (matches vim).
- Volmarr ✓ (likely also vim-user).
- Iðunn ✗ (doesn't know hjkl).
- **Resolution: both work simultaneously.** Arrow keys + hjkl are
  bound to the same actions. Iðunn uses arrows; Sigrún uses hjkl.

Example: **command palette opens with `:` (vim-style)**.
- Sigrún ✓.
- Iðunn ✗ (doesn't know what `:` means).
- **Resolution: also bind to `Ctrl-P` (familiar from VS Code).** Both
  work.

---

## Closing

If a future PR is hard to decide on, run it through these five
personas. The answer usually becomes obvious.
