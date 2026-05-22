# 51 — Menu Bar Presence

OpenClaw has macOS menu-bar integration. Should Ember? When?
How specifically?

---

## What menu-bar adds

A menu-bar icon (top-right on macOS; system tray on Windows;
panel on Linux) provides:

- **Always-visible Ember status**: connected/idle/working.
- **Quick access**: click → menu → start chat / open Stofa /
  voice toggle / settings.
- **Notifications**: subtle indicator for "Ember has a message
  for you."
- **Ambient presence**: Ember feels *part of the desktop*, not
  a separate app.

For some operators, this transforms how Ember feels.

---

## Cross-platform reality

Menu-bar integration is *platform-specific*:

- **macOS**: NSStatusItem; well-supported.
- **Windows**: system tray; supported.
- **Linux KDE**: system tray; supported.
- **Linux GNOME**: complicated; needs extension.
- **Linux i3/sway/tiling WMs**: depends on bar.
- **Headless (Pi)**: no menu bar.

Cross-platform menu-bar work is *real engineering*. Per-
platform native APIs or use a library that abstracts.

---

## What Python offers

- **pystray**: cross-platform system tray library. Mature.
- **rumps**: macOS menu-bar only; Python.
- **PyQt6 / PySide6**: cross-platform menu/tray; heavy.

For Ember V5+, **pystray** is the right choice. Pure Python;
mac/win/linux; small footprint.

---

## When this lands

🟡 **Defer to V5+ (Phase 4-late / Phase 5).**

Reasons to wait:
- Daemon mode (V4) is prerequisite — menu-bar needs always-on
  process.
- Web companion (V5) covers some of the "always-accessible"
  benefit differently.
- Limited operator demand pre-V5.

When it lands: useful addition for desktop operators.

---

## What ours would do

V5 minimum:

```
[Ember icon in menu bar]
  Click →
    ┌────────────────────────┐
    │ Ember                   │
    │ ──                      │
    │ ⚡ Quick chat ▶          │
    │ 🪟 Open Stofa            │
    │ 🌐 Web Companion         │
    │ 🎤 Voice (off)          │
    │ ──                      │
    │ ⚙ Settings              │
    │ 📊 Doctor                │
    │ ──                      │
    │ Quit Ember              │
    └────────────────────────┘
```

Minimal; useful; not visually busy.

---

## Implementation outline

```python
import pystray
from PIL import Image

def on_quick_chat():
    # Open quick chat input window (small Stofa-like prompt)
    ...

def on_open_stofa():
    # Spawn full Stofa
    ...

def on_quit():
    # Gracefully shut down Ember daemon
    ...

menu = pystray.Menu(
    pystray.MenuItem("Quick chat", on_quick_chat),
    pystray.MenuItem("Open Stofa", on_open_stofa),
    pystray.MenuItem("Web Companion", on_open_companion),
    pystray.MenuItem("Voice", on_toggle_voice, checked=is_voice_on),
    pystray.Menu.SEPARATOR,
    pystray.MenuItem("Settings", on_settings),
    pystray.MenuItem("Doctor", on_doctor),
    pystray.Menu.SEPARATOR,
    pystray.MenuItem("Quit", on_quit),
)

icon = pystray.Icon(
    "Ember",
    Image.open("ember-icon.png"),
    "Ember",
    menu,
)
icon.run()
```

---

## Status indicators

Icon state reflects Ember state:

- **Idle**: standard icon.
- **Thinking**: animated (subtle).
- **Has notification**: badge or color shift.
- **Error / disconnected**: red overlay.

Operators see *at a glance* what's happening.

---

## Notifications

Native system notifications via `plyer` or `notify-send`:

```python
def notify(title, body):
    # macOS: osascript display notification
    # Linux: notify-send
    # Windows: native API
    ...
```

Used for:
- "Mirror of Ginnungagap has weekly report ready."
- "Dreamstate completed."
- "Long-running ingest finished."

Operators see Ember's *background activities*.

---

## Quick chat window

Click "Quick chat" → small popover/window:

```
┌─ Quick Chat ──────────────────────┐
│                                    │
│ [Type your question...]            │
│                                    │
│                          [Send]    │
└────────────────────────────────────┘
```

Operator types brief question; Ember replies; window closes
or stays for follow-up.

Useful for *quick ask* moments — operator wants to ask Ember
something briefly without committing to full Stofa session.

---

## Privacy concerns

Menu-bar = always-visible. If others see operator's screen, the
Ember icon is visible.

Mitigations:
- **Hide-on-screensharing**: detect screen-sharing apps;
  optionally hide icon.
- **Operator can disable**: menu-bar is opt-in.
- **No sensitive info in icon state**: just connectivity, no
  content.

---

## Configuration shape

```yaml
ember:
  menu_bar:
    enabled: false                # opt-in V5+
    
    icon:
      style: dark                 # or "light" / "auto"
      animate_when_thinking: true
      badge_on_notification: true
    
    menu_items:
      quick_chat: true
      open_stofa: true
      web_companion: true
      voice: true
      settings: true
      doctor: true
    
    notifications:
      enabled: true
      sound: false                # silent by default
      hide_during_screensharing: true
```

---

## Platform-specific considerations

### macOS

- App requires bundle structure for proper menu-bar.
- Code signing for distribution.
- `pystray` works without bundle but limited.
- For polished experience: `py2app` or `briefcase` to build
  bundle.

### Windows

- System tray supported via pystray.
- Notification center for native notifications.

### Linux

- KDE / Cinnamon / Xfce: full support.
- GNOME: requires `appindicator` extension or fallback.
- Tiling WMs: depends on operator's bar config.

Document per-platform setup.

---

## What menu-bar doesn't replace

- Stofa (TUI primary surface).
- Munnr (CLI fast access).
- Web companion (mobile).

Menu-bar is *quick-access UI*; not primary chat surface.

---

## What about always-on listening

OpenClaw's macOS menu-bar exposes Voice Wake. Ember's would
too (V5+):

```
[Ember icon] →
  ├ Voice: ON  (always listening for "Hey Ember")
  ├ Voice: OFF
  └ Voice: PTT  (push-to-talk via hotkey)
```

Operator toggles via menu without going into config.

---

## Integration with daemon mode

Menu-bar requires daemon mode. The daemon runs the Ember
Gateway + menu-bar icon process.

```bash
ember daemon start --with-menu-bar
```

Daemon starts; icon appears; operator can quick-chat without
launching anything.

---

## What we don't do

🔴 **Reject**:

### 1. Dock icon

Don't add a dock icon. Menu-bar is enough; dock adds clutter.

### 2. Constant notifications

Notifications only for substantive events (weekly Mirror, long
async ops). Not for every chat turn.

### 3. Pop-up dialogs

Menu-bar leads to *operator-initiated* surfaces, not pop-ups
that interrupt.

---

## Risks + mitigations

| Risk | Mitigation |
|---|---|
| Operator confusion about state | Status indicator + tooltip |
| Cross-platform menu-bar issues | pystray + per-platform testing |
| Always-on impression | Operator-controlled enable/disable |
| Privacy on shared screens | Auto-hide on screensharing |

---

## V5+ ship plan

1. **V5a**: minimal menu-bar with chat shortcuts.
2. **V5b**: status indicators (idle/thinking/error).
3. **V5c**: notifications (limited).
4. **V5d**: quick chat window.
5. **V5e**: voice toggle.

Each ships independently. Operator opt-in throughout.

---

## Closing

Menu Bar Presence is **V5+ Klóinn adoption** — adds OpenClaw-
style ambient presence for desktop operators who want it.

Cross-platform via pystray. Modest scope. Operator-opt-in.

This is *the gentlest possible mainstream desktop integration*
— Ember-on-the-edge-of-vision without becoming intrusive.

The Klóinn lesson: ambient presence has value; build it
small; operator chooses.
