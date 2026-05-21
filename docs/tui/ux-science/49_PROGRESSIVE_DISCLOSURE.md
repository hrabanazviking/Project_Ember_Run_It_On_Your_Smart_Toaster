# 49 — Progressive Disclosure

Show only what the operator needs *right now*. Reveal more on
request. The mental model: a hall has rooms; rooms have shelves;
shelves have books. You don't see every book at once.

---

## Why progressive disclosure

The alternative is **everything visible all the time**, which is:

- Overwhelming on first contact (Iðunn bounces).
- Exhausting in long sessions (Védis's eyes hurt).
- Slow to scan (Sigrún waits too long).
- Hostile to focus (the chat is what the operator's *doing*; not the
  audit log).

Progressive disclosure is the discipline of layering complexity. The
first layer is friendly; the second is helpful; the third is
operator-specific.

---

## Three disclosure layers in Stofa

### Layer 1: the immediate surface (chrome + first content)

What every operator sees on every screen, always:

- Chrome header (current screen name, hearth icon).
- Main content area (chat, document list, etc.).
- StatusBar (realm states + key hints).

This is *all* an operator needs to do the primary task on that
screen. No menus, no panels-within-panels.

### Layer 2: helpful context (one keypress away)

Pressed `?`: help overlay shows what's possible here.
Pressed Tab: focus cycles through visible panels.
Pressed `Enter` on a citation: expand inline.
Pressed `]`: cycle to next detail tab.

These are *visible* in the help overlay and *suggested* in the
StatusBar's key hints. The operator can do their primary task
without ever knowing about them; they're available the moment the
operator wants more.

### Layer 3: power-user surface (rare, palette-or-config)

Pressed `:`: command palette opens any named action.
Edited `ember.yaml`: any setting can be tuned.
Installed a plugin (V2): new screens / pets / themes.

Some operators never visit layer 3. That's fine — Stofa works
fully without them.

---

## Per-screen disclosure rules

### HomeScreen

- **Always visible:** 4 panels, each with a 1-line current state +
  1-line hint.
- **One keypress away:** any other screen.
- **In the palette:** all admin commands (theme switch, audit
  export, plugin manage).

The HomeScreen does NOT show:
- The full Episode history (that's in V2's EpisodeBrowserScreen).
- The audit log (that's in V2's AuditLogScreen).
- The per-tool approval-override list (that's in Settings).

### ChatScreen

- **Always visible:** the conversation, the input bar.
- **One keypress away:** citation expansion (Enter), help (?), tool
  approval (only when triggered).
- **In the palette:** export conversation, clear chat, change model
  for next turn.

Does NOT show:
- The full system prompt (it's in the audit log).
- The model's token throughput (debug overlay only).
- The MCP server states (those are in StatusBar + MCPScreen).

### WellScreen

- **Always visible:** sources list, selected document details.
- **One keypress away:** ingest a path (i), re-ingest (r), search
  (/).
- **In the palette:** export Well metadata, vacuum the sqlite, etc.

Does NOT show:
- The chunk-level detail of the selected document (Enter → tab to
  Chunks).
- The embedding vector itself (way too dense; debug overlay only).

### DoctorScreen

- **Always visible:** 4 realms with status + 2-3 detail fields each.
- **One keypress away:** re-probe (r), view raw response (v).
- **In the palette:** export doctor report.

### SettingsScreen

- **Always visible:** section list (collapsed) + the focused section
  expanded.
- **One keypress away:** save (s), cancel (Esc), field help (?).
- **In the palette:** reset section, reset all settings, import/export
  config.

### MCPScreen

- **Always visible:** server list with status + tool count.
- **One keypress away:** add (a), ping (p), restart (r), view logs (l).
- **In the palette:** install MCP server from registry (V2),
  audit-log of all MCP calls.

---

## The help overlay as disclosure surface

`?` opens the help overlay. It shows:

```
┌─ Help (Chat screen) ─────────────────────────────────────────┐
│                                                               │
│  Global:                                                      │
│    ? F1       this help                                       │
│    : Ctrl-P   command palette                                 │
│    q Ctrl-C   quit                                            │
│    h          Home                                            │
│    Esc        cancel / pop                                    │
│                                                               │
│  Navigation:                                                  │
│    c          Chat (you are here)                             │
│    w          Well                                            │
│    d          Doctor                                          │
│    s          Settings                                        │
│    m          MCP                                             │
│                                                               │
│  Chat:                                                        │
│    Enter      send message                                    │
│    Shift+Ent  newline                                         │
│    ↑          recall last message                             │
│    Ctrl-C     interrupt streaming                             │
│    Ctrl-U     clear input                                     │
│    Ctrl-A     open audit log                                  │
│                                                               │
│  Approval modal (when shown):                                 │
│    y          approve once                                    │
│    a          approve + remember session                      │
│    n          deny                                            │
│                                                               │
│  Press ? or Esc to close.                                     │
└───────────────────────────────────────────────────────────────┘
```

Three sections: global (everywhere), navigation (universal), and
screen-specific (changes per screen). The operator gets the layer-2
surface in one keypress, plus a reminder of layer-1 actions.

---

## The command palette as disclosure surface

`:` opens the fuzzy command palette. It contains *every* named
action — layer 1, layer 2, AND layer 3. Operators who don't want to
memorize anything can find anything by typing what it does.

```
> the
  :theme aurora
  :theme midgard
  :theme ginnungagap
  :theme solstice
  :theme barrow
```

Typing `the` immediately suggests theme commands. Operator picks one.
No menu, no nested submenus, no "where in Settings is that."

---

## What is NEVER hidden

A few things must be *always* visible:

- The hearth icon (proves Stofa is alive).
- The chrome header with current screen name.
- The StatusBar with realm states.
- The cursor (operators must see where they are).
- Error states (red bullet next to the affected realm).

Hiding any of these would damage trust.

---

## The "what does this do?" question

When an operator sees something they don't understand:

1. **Hover with focus** — if a widget shows a tooltip, it's displayed.
2. **Press `?`** — help overlay explains what's bindable.
3. **Press `:`** — command palette lets them type to find related
   actions.
4. **Read the StatusBar** — current screen + key hints visible.

Four routes to disclosure. The operator who's confused has
*somewhere* to land.

---

## Anti-disclosure: things we don't hide

Some things we deliberately keep visible even when "less is more"
might tempt us:

- **Per-screen key hints.** Always in StatusBar. Don't make the
  operator memorize.
- **Realm states.** Always in StatusBar. Operators need ground truth.
- **The current screen name.** Always in chrome. Orientation matters.

The opposite of progressive disclosure is **persistent disclosure** —
things important enough to never hide.

---

## How disclosure changes between V1 and V2

V1 is a **fixed** set of screens + features. V2 adds:

- Plugin-installed screens → command palette + (optionally) hotkey.
- Plugin-installed pets → Settings → Pets list.
- Operator-defined dashboard sections → Home customization.

V2 disclosure rule: **anything plugins add appears in layer 2 or 3
by default**. A plugin can't put itself in layer 1 (the always-visible
chrome) without operator opt-in. Default-opt-in plugins would
violate the disclosure model.

---

## Closing

Progressive disclosure is *trust in the operator*. The first surface
is friendly because newcomers deserve a soft landing. The second
surface is helpful because curious operators want more. The third
surface is powerful because power-users will *seek* it. We don't
have to put everything on one screen; we just have to make every
layer reachable from the one above.

The hall has rooms. The rooms have shelves. The shelves have books.
The operator who wants the chat finds the chat. The operator who
wants to audit every tool call finds *that*. Nothing is hidden;
nothing is in the way.
