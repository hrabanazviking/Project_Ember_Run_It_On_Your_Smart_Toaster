# 31 — spotify-tui

> https://github.com/Rigellute/spotify-tui

A Spotify client in the terminal. Teaches Stofa about **the persistent
"now playing" bar** — a piece of always-visible context that ties
the whole TUI together.

---

## What it is

A Rust TUI for Spotify. Login, browse playlists, search artists,
play tracks. Multi-pane layout. Notable for one thing: **the always-on
playback bar at the bottom**.

```
┌── Library ─────┐┌── Currently selected playlist ─────────────────┐
│ Liked Songs    ││ 1. Auf Andre Sorgen                             │
│ My Mixes       ││ 2. Tystnaden                                    │
│ ...            ││ 3. ...                                          │
└────────────────┘└─────────────────────────────────────────────────┘
                                              ───── ▸ ────────────
        ● Tystnaden ── Wardruna             0:54 ▸ ────────────────  3:08
        Press space to pause · n=next · p=previous · ?
```

The bottom bar shows: what's playing, position, controls. **Always.**
No matter which screen you're on. No matter what you're browsing.

---

## The clever idea: persistent context bar

The operator's *primary state* — what's playing — never disappears.
You can navigate the UI freely without losing track of what you're
listening to.

### What we steal

Stofa's **StatusBar** is the same idea. Always visible, always shows:

- Funi state (model name + thinking-or-idle)
- Brunnr state (connected + doc count)
- MCP state (servers up / total)
- Current screen + key hints
- Recent activity (last event timestamp)

Whatever screen the operator is on, they can glance down and know
what's happening across the whole app.

### What we avoid

Spotify-tui's bar includes playback *controls* (Space to pause,
n to skip). Stofa's StatusBar is *informational only* — controls
live in the focused screen. Mixing info and controls in the same bar
makes it crowded.

---

## The "what am I doing now" question

Operators who tab away from the TUI for a minute and come back need
to re-orient. The persistent bar is what makes that fast.

Spotify-tui's bar tells you "you were listening to X." Stofa's
StatusBar tells you "Funi is thinking, Brunnr is at 95 docs, MCP is
2/2, you're on the Chat screen."

Two seconds of glance, zero seconds of navigation.

---

## What we improve

Spotify-tui's bar is one line of fixed-ish content. Stofa's is
slightly richer:

- Left section: realm states (icons + abbreviated counts).
- Center section: current screen name + key hints.
- Right section: clock or last-action timestamp.

This is more density, but in a clearly-segmented way (three zones).
Operators learn "states-left, hints-center, time-right" in a few
glances.

---

## Specific Stofa borrowings

- **Always-on bottom status bar.** Not hidden, not collapsible.
- **Layered information by zone** (per the StatusBar design).
- **No playback-style controls in the bar.** Information only.

---

## Closing

Spotify-tui taught the TUI world that a persistent bar of context
is more valuable than its single row of pixels suggests. Stofa
extends the idea — three zones, always visible, no controls. The
operator's anchor.
