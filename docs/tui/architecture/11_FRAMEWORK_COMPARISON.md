# 11 — Framework Comparison

The Python TUI ecosystem in 2026 has three serious frameworks plus
several rendering libraries. This document compares them on the axes
that matter for Stofa, then picks one with reasoning.

**Decision: Textual 2.x.** Justified below.

---

## Candidates

1. **Textual** (Will McGugan / Textualize) — async, CSS-styled,
   widget-based, devtools.
2. **Rich** (same author) — rendering library, NOT a TUI framework on
   its own (no event loop).
3. **prompt_toolkit** (Jonathan Slenders) — async, lower-level,
   battle-tested in IPython / aws-cli's interactive shells.
4. **blessed** + **urwid** — older urwid + blessed combo; widely
   deployed but pre-async-first.
5. **picotui / npyscreen** — even older; minimal, ncurses-shaped.
6. **Bubble Tea / Lipgloss** (Go) — best-in-class but wrong language.
7. **ratatui** (Rust) — same; wrong language.

For Stofa we need Python (Ember is Python). That eliminates Bubble Tea
and ratatui. picotui / npyscreen / urwid are pre-async-first and would
require their own concurrency story; skipped. The real comparison is
**Textual vs Rich-as-base vs prompt_toolkit**.

---

## Comparison matrix

| Concern | Textual | Rich-only | prompt_toolkit |
|---|---|---|---|
| Async event loop | ✅ first-class | ❌ none | ✅ first-class |
| Widget model | ✅ Widget tree | ❌ none | ⚠️ Layout/Container abstractions but not OO-widget |
| CSS-style theming | ✅ TCSS | ❌ raw style objects | ⚠️ per-component Style |
| Mouse support | ✅ everywhere | ❌ via Rich Live | ✅ |
| DevTools (live inspector) | ✅ excellent | ❌ | ❌ |
| Resize handling | ✅ automatic | ❌ DIY | ⚠️ DIY-ish |
| Animation primitives | ✅ Timer + auto_refresh | ⚠️ Live updates | ⚠️ DIY |
| Markdown rendering | ✅ via Rich | ✅ | ❌ DIY |
| Syntax highlighting | ✅ via Rich | ✅ | ⚠️ basic |
| Active maintenance (2024–) | ✅ very active | ✅ same maintainer | ✅ maintained |
| Dep count (transitive) | ~12 | ~3 | ~5 |
| Learning curve | ⚠️ moderate (new concepts) | ✅ low | ⚠️ moderate-high (low-level) |
| Production TUIs using it | Memray viewer, posting, Toolong, Frogmouth, harlequin, dolphie | many | aws-shell, IPython, ptpython, awscli v2 |
| Cross-platform (Windows) | ✅ | ✅ | ✅ |
| SSH-friendly (low repaint) | ✅ diff renderer | ⚠️ frequent full repaints | ✅ |
| Plugin / extension model | ✅ widgets as Python classes | n/a | ⚠️ DIY |

---

## Textual — the case for

**Pros:**

1. **The right level of abstraction for Stofa.** Stofa is an
   application, not a renderer. Textual has Apps, Screens, Widgets,
   Messages, CSS-styling, devtools. Rich is "a really nice print()".
   prompt_toolkit is "a lower-level toolkit for *building* TUIs."
   We want the *framework*.
2. **The CSS-style theming is exactly what Stofa needs** for
   swappable themes (Aurora / Midgard / Ginnungagap / Solstice /
   Barrow). The `$primary`, `$surface`, `$accent` token pattern slots
   in cleanly.
3. **Async-first.** All Ember backends are sync (sqlite, urllib,
   psycopg); we'll wrap with `asyncio.to_thread`. But Funi streaming
   benefits from native async, and MCP's `ClientSession` is async.
   Textual's async-first design makes the bridging trivial.
4. **The DevTools are real.** Live CSS-style inspector + live widget
   tree + log console makes Stofa-development viable without 100
   debug prints.
5. **Production track record.** Memray's viewer, Posting (a Postman
   alternative), Toolong (log viewer), harlequin (DuckDB shell) all
   ship with Textual. These are not toy apps.
6. **SSH-friendly.** Textual's diff renderer (`Compositor`) only
   repaints changed cells — important for Eirwyn the Pi-class
   operator and any operator on flaky wifi.
7. **Excellent docs + active community.** Discord, GitHub Discussions,
   weekly blog posts. Lower onboarding cost.

**Cons:**

1. **Dependency cost.** Textual brings ~12 transitive deps (Rich
   itself, markdown-it-py, mdit_py_plugins, pygments, linkify-it-py,
   uc-micro-py, platformdirs, etc.). All maintained, mostly stdlib-
   adjacent. But still: more than zero.
2. **New concepts to learn.** Widget tree, Messages, CSS, reactives.
   The learning curve is moderate, not flat.
3. **Some Textual conventions are still settling.** v2.x is stable
   but the Reactive API has been in flux. We pin to a known-good
   version range.

We accept these cons.

---

## Rich-only — why not

Rich is the rendering library. Without Textual, you write your own
event loop, your own input handler, your own widget concept (or do
without). For a one-screen tool (lazyformat, glow), Rich is great.
For a multi-screen, multi-panel, live-updating application like
Stofa: writing the framework ourselves is *exactly the work* Textual
already did. We don't gain anything by doing it again.

Rejected for Stofa's scope; we will still use Rich *through* Textual
for markdown / syntax / tables (Textual embeds Rich).

---

## prompt_toolkit — why not

prompt_toolkit is excellent and battle-tested. It powers IPython,
ptpython, the AWS shell. But:

1. **Lower-level than we need.** No `Screen` concept; we'd build it.
   No CSS theming; we'd build the token-swap ourselves.
2. **No DevTools.** Debugging is print-driven.
3. **Less idiomatic for a Stofa-shape app.** prompt_toolkit's sweet
   spot is *interactive shells* with completion / history / multiline
   input. Stofa is a *multi-screen dashboard with chat in one panel*.
   Textual's widget tree is the right shape.

prompt_toolkit would work. It would just be more code.

---

## Other rejected alternatives

- **urwid** — pre-async. Adding an asyncio bridge is possible
  (`urwid.AsyncioEventLoop`) but the widget model is OO-classic-Python
  from before `dataclass`. Aged.
- **npyscreen / picotui** — toy-grade; not production.
- **wxPython / Tkinter / PyQt** — those are GUI toolkits, not TUI.
  Auga (the future GUI) is the right surface for them.
- **Custom escape-sequence layer** — we are not writing our own
  framework. Vow of Smallness applies to code, not to ambition.

---

## Locking in the Textual version

We pin to `textual >= 2.0, < 3.0` for V1. Reasons:

- 2.x is stable.
- The Reactive API + CSS-Live-Reload work as expected.
- We don't want to surprise-upgrade through a 3.x breaking change.

Update pin in `pyproject.toml`:

```toml
tui = ["textual>=2.0,<3.0"]
```

Transitive deps come along for the ride (Rich, markdown-it-py, etc.).
All MIT or BSD licensed; all maintained; the cost is acceptable.

---

## Cross-platform reality check

Textual works on Linux, macOS, Windows (Windows Terminal preferred,
ConPTY mode), and WSL. The team explicitly tests Windows. ANSI escape
handling is mediated by Textual itself, not pushed to the operator's
terminal.

Mouse support: works in xterm, iTerm2, kitty, alacritty, Windows
Terminal, mintty. Falls back gracefully when mouse isn't available
(every Stofa action has a keyboard binding — see Persona 3 in
[`vision/03_USER_PERSONAS.md`](../vision/03_USER_PERSONAS.md)).

Terminal-emulator compatibility matrix in
[`operations/91_TERMINAL_COMPAT_MATRIX.md`](../operations/91_TERMINAL_COMPAT_MATRIX.md).

---

## Where we *don't* use Textual

Some places where we'd rather use stdlib + ourselves:

- **JSON serialization** — `json`, never Textual.
- **Config loading** — existing `ember.config.load_ember_config`.
- **Async sqlite/psycopg/urllib bridging** — `asyncio.to_thread`,
  not Textual-specific.
- **Pet sprite storage** — plain text files in `stofa/pets/sprites/`,
  not Textual assets.

Textual is the framework. It isn't the universe.

---

## What if Textual gets abandoned?

Risk worth naming.

If Textual stops being maintained tomorrow, Stofa is the only Ember
surface affected. The handles below it (Funi, Brunnr, MCP) are
framework-agnostic. The `ember chat` REPL still works for everything
Stofa does.

Worst case migration path: rewrite Stofa on prompt_toolkit. Estimated
effort: 2-3 weeks of focused work (the widget tree + CSS layer are
the parts that would need replacing; the services + pets + screen
logic translate). Recoverable.

The mitigation is **not** to avoid Textual. The mitigation is the
three-layer architecture: handles are below the framework. Whatever
framework wraps them, the data model is durable.

---

## Decision

**Textual 2.x.** Locked. The rest of this design tree assumes Textual.
