# 30 — gh-dash

> https://github.com/dlvhdr/gh-dash

A GitHub dashboard TUI. The CLI extension `gh dash` opens a multi-panel
view of PRs, issues, repos. Teaches Stofa about **views as composable
queries**, **multi-section dashboards**, and **integrating with a
larger ecosystem (the `gh` CLI)**.

---

## What it is

A Go TUI built as a `gh` extension. Operator runs `gh dash` and gets:

```
┌── Pull requests ─────────────────────────────────────────────────┐
│  My open PRs                                                      │
│   • #4519  feat: stofa first cut                                  │
│   • #4517  doc: hardening batch I                                 │
│                                                                   │
│  Needs review                                                     │
│   • #4510  fix: tool timeout                                      │
│   • #4502  test: improve mcp coverage                             │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
┌── Issues ─────────────────────────────────────────────────────────┐
│  Assigned to me                                                    │
│   • #321  Stofa: pet `Refur` doesn't appear during approval       │
│                                                                    │
└───────────────────────────────────────────────────────────────────┘
```

Each section is a configurable *view* (a saved query). Operators
define their own sections in `~/.config/gh-dash/config.yml`.

---

## The clever idea: configurable saved views

The operator doesn't have to navigate through GitHub's UI to find
"my open PRs in the ember repo." They define that as a view once,
and gh-dash shows it every time.

This shifts the operator's work *from navigation to definition*.
Define your reality once; review it many times.

### What we steal

Stofa V1 doesn't have configurable dashboard sections — the 2×2
HomeScreen is fixed. But V2 is planned to add **dashboard sections
as plugins** (per [`../architecture/18_PLUGIN_ARCHITECTURE.md`](../architecture/18_PLUGIN_ARCHITECTURE.md)),
which is the same idea: operators add their own widgets to Home.

---

## The multi-section dashboard

gh-dash stacks multiple horizontal sections. Each scrolls
independently. Tab switches focus.

### What we steal

Stofa's HomeScreen has 4 panels in a 2×2 grid. Tab cycles focus.
Different shape but same principle: multiple semantic sections in
one view.

### What we avoid

The "infinitely scrollable" dashboard. gh-dash can have many sections
that don't all fit; the operator scrolls past them. Stofa's HomeScreen
has exactly 4 panels, all visible (or, on narrow terminals, 4 stacked).
We don't grow Home arbitrarily.

---

## The ecosystem-integration lesson

gh-dash is `gh dash` — a subcommand of the official `gh` CLI. It
integrates naturally with the rest of the `gh` workflow.

### What we steal

Stofa is `ember tui` — a subcommand of `ember`. Integrates with the
rest of the `ember` workflow:

- `ember setup` runs Hjarta CLI; Stofa's Hjarta wizard runs the same FSM.
- `ember chat` runs the synchronous REPL; Stofa's ChatScreen runs the
  same logic.
- `ember well ingest` runs the CLI ingest; Stofa's WellScreen runs
  the same ingest.

The operator never has to choose between CLI and TUI; they use
either, and the data is shared.

---

## Specific Stofa choices

- **`ember tui` subcommand** (not a separate binary).
- **Same handles + same Episodes** between CLI and TUI.
- **HomeScreen as fixed-section dashboard** (V1) — extensible via
  plugins (V2).

---

## Closing

gh-dash teaches that *the dashboard is a query*. Stofa's HomeScreen
is currently a fixed view of Ember's state; V2 will make it
operator-customizable. The deeper lesson: integrate with the
ecosystem you're in (CLI ↔ TUI sharing data, sharing handles, sharing
identity).
