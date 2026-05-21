# 13 — Screen Hierarchy

Stofa is composed of nine screens in V1. Each is a self-contained
`textual.Screen` subclass. This document is the *map* of what exists
and how they nest.

---

## The nine V1 screens

| Screen | Always-present? | Purpose | Doc |
|---|---|---|---|
| **HomeScreen** | yes (base) | Landing + dashboard | [`screens/80_SCREEN_HOME.md`](../screens/80_SCREEN_HOME.md) |
| **ChatScreen** | no (modal-ish push) | Conversation | [`screens/81_SCREEN_CHAT.md`](../screens/81_SCREEN_CHAT.md) |
| **WellScreen** | no | Browse + ingest | [`screens/82_SCREEN_WELL.md`](../screens/82_SCREEN_WELL.md) |
| **DoctorScreen** | no | Health snapshot | [`screens/83_SCREEN_DOCTOR.md`](../screens/83_SCREEN_DOCTOR.md) |
| **SettingsScreen** | no | Edit ember.yaml | [`screens/84_SCREEN_SETTINGS.md`](../screens/84_SCREEN_SETTINGS.md) |
| **MCPScreen** | no | Manage MCP servers | [`screens/85_SCREEN_MCP.md`](../screens/85_SCREEN_MCP.md) |
| **ToolApprovalScreen** | no (modal) | Approve / deny tools | [`screens/86_SCREEN_TOOL_APPROVAL.md`](../screens/86_SCREEN_TOOL_APPROVAL.md) |
| **HjartaWizardScreen** | only first-run | First-run setup | [`screens/87_SCREEN_HJARTA_WIZARD.md`](../screens/87_SCREEN_HJARTA_WIZARD.md) |
| **HelpOverlay** | available everywhere | Per-screen help | [`screens/88_HELP_OVERLAY.md`](../screens/88_HELP_OVERLAY.md) |

---

## Stack semantics

Textual gives us a screen stack. Stofa's rules:

- **HomeScreen is the bottom of the stack** in OPEN state. It is
  pushed by `StofaApp.on_mount` and never popped (except on close).
- **ChatScreen, WellScreen, DoctorScreen, SettingsScreen, MCPScreen**
  push on top of Home. Operator presses keybind (e.g., `c`, `w`,
  `d`, `s`, `m`) to push; `Esc` to pop back to Home.
- **ToolApprovalScreen is modal-on-top-of-chat.** Pushes when Funi
  emits a tool_call; pops when the operator answers. Only the chat
  screen pushes it.
- **HjartaWizardScreen is exclusive.** Pushed before HomeScreen on
  first launch; replaces (not stacks on) Home. Popped only on wizard
  completion.
- **HelpOverlay is a true overlay.** Doesn't replace the underlying
  screen; renders translucently on top. Operator can dismiss with
  `?` or `Esc`. Tied to whatever screen is on top of the stack.

Visually:

```
            ┌─────────────────────────┐
            │       HelpOverlay        │  ← rendered on top, opt-in (?)
            └─────────────────────────┘
                       │
            ┌─────────────────────────┐
            │   ToolApprovalScreen     │  ← modal during tool approval
            └─────────────────────────┘
                       │
            ┌─────────────────────────┐
            │  ChatScreen / WellScreen │  ← whatever the operator is on
            │  / DoctorScreen / etc.   │
            └─────────────────────────┘
                       │
            ┌─────────────────────────┐
            │       HomeScreen         │  ← always present
            └─────────────────────────┘
```

---

## HomeScreen: the persistent dashboard

HomeScreen is **not just "main menu"**. It is a real dashboard with
panels that the operator can read at a glance:

```
┌────── Stofa ─────────────────────────── 🔥 ─────┐
│                                                  │
│  ┌──── Conversation ────┐ ┌──── Well ────────┐  │
│  │ {model-id}            │ │ {N} documents    │  │
│  │ {episodes-this-sess.} │ │ {M} chunks       │  │
│  │ Press c to chat       │ │ Press w to open  │  │
│  └───────────────────────┘ └──────────────────┘  │
│                                                  │
│  ┌──── Realms ──────────┐ ┌──── Tools ───────┐  │
│  │ Funi    ✓ {model}    │ │ {N} enabled      │  │
│  │ Strengr ✓             │ │ {M} MCP servers  │  │
│  │ Brunnr  ✓ {backend}   │ │ Press m / t      │  │
│  │ Press d for details   │ │                  │  │
│  └───────────────────────┘ └──────────────────┘  │
│                                                  │
│ [Hugin perches here] [Geri-cub sleeps here]      │
└──────────────────────────────────────────────────┘
[ status bar ]
```

Pressing `c` pushes ChatScreen; `w` pushes WellScreen; etc.
Pressing `Esc` from any pushed screen returns to Home.

---

## Why a Home screen at all (vs going straight to chat)

This was debated. Arguments for going straight to chat:

- Faster path to conversation (Iðunn).
- Operator who wants chat shouldn't have to press `c`.

Arguments for Home as the bottom of the stack:

- The **dashboard view of Ember's state** is itself valuable
  (Volmarr's sovereign-operator perspective).
- Operators who *aren't* sure what they want to do today land
  somewhere they can survey.
- The `Esc` semantics — pressing `Esc` should *take you home*, not
  drop you out of the app — only work if Home exists.

**Compromise:** the operator can configure `stofa.start_screen`. The
default is `"home"`; setting it to `"chat"` skips Home on launch
(though `Esc` still goes there, and `:home` always navigates there).

---

## Why a Help overlay (vs a Help screen)

Overlay so that the operator never *loses* their context. Help that
covers the screen and requires backing out is friction. Help that
floats above is friction-free.

The overlay shows:
- Current screen's keybindings.
- Global keybindings (always there).
- Two-line "what is this screen for" reminder.
- A link/keybind to the relevant doc URL if internet is reachable
  (graceful degradation otherwise).

---

## Navigation summary

| Action | From any screen | From Home specifically |
|---|---|---|
| Go to Home | `Esc` (one level) or `h` (always) | (already there) |
| Go to Chat | `c` | `c` |
| Go to Well | `w` | `w` |
| Go to Doctor | `d` | `d` |
| Go to Settings | `s` | `s` |
| Go to MCP | `m` | `m` |
| Show help | `?` or `F1` | `?` |
| Command palette | `:` or `Ctrl-P` | `:` |
| Toggle pets | `p` | `p` |
| Theme menu | `:theme` | `:theme` |
| Quit | `q` or `Ctrl-C` | `q` |

All keybindings are rebindable in `ember.yaml` (per
[`16_KEYBINDING_PHILOSOPHY.md`](16_KEYBINDING_PHILOSOPHY.md)).

---

## Screen ownership of state

Each screen owns its own local state. Cross-screen state lives in
the App or in a Service.

| State | Lives where |
|---|---|
| Active conversation | ChatScreen (in-memory `episodes` list) |
| Persisted Episodes | Brunnr (via `add_episode`) |
| Current ingest job | WellService |
| MCP server list | MCPService |
| Last-doctor result | DoctorService |
| Theme | StofaApp |
| Pets visible | StofaApp |
| Tool approval pending | ChatScreen (transient — pushed to ToolApprovalScreen) |

When a screen unmounts (pop), its local state is preserved if the
screen is push-pop-restored. Textual handles this.

---

## What we are NOT doing in V1

- **Multi-tab / multi-window.** Stofa is one focused context at a
  time. Power-users who want multiple conversations open run multiple
  `ember tui` instances.
- **Floating non-modal panels.** Everything either fills the screen
  (push) or is a true modal/overlay.
- **Customizable Home dashboard.** The 4-panel layout is fixed in V1.
  V2 may add layout flexibility.
- **Multiple home pages.** Just one Home screen.

---

## V2+ screens (named but not designed)

When the V2 plugin system lands, third-party screens become possible.
Named candidates:

- **EpisodeBrowserScreen** — search + view persisted Episodes.
- **AuditLogScreen** — paginated audit log viewer.
- **ThemeStudioScreen** — interactive theme editor with live preview.
- **PetCustomizationScreen** — toggle individual pets, configure
  pet personalities.
- **MCPMarketplaceScreen** — browse community MCP servers by tag.

V2 is a future conversation. V1 ships the 9 above.
