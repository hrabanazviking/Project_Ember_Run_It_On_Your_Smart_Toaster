# 00 — Vision

> *Got a toaster? Good. You can have a hall, too.*

## What Stofa is

**Stofa** is Project Ember's terminal-user-interface surface. It turns the
existing `ember chat` REPL (one prompt, one reply, one buffer) into a full
interactive home for everything the operator does with Ember: chat, browse
the Well, watch ingest, run the doctor, manage MCP servers, tune settings,
approve tool calls — all in one persistent screen.

Stofa is not a chat client wearing fancy borders. It is the *primary home*
for the operator's relationship with Ember, in the place most operators of
small-and-tethered AI actually live: the terminal.

## What Stofa is *not*

- **Not a re-skin of `ember chat`.** Chat stays the way it is for
  scripted / piped use. Stofa is a separate subcommand (`ember tui` or
  just `ember`) that hosts chat as one of several screens.
- **Not a webview-in-a-terminal.** No HTML rendering, no embedded browser,
  no JavaScript runtime. Stofa is text + ANSI + maybe one or two
  terminal-graphics extensions for opt-in operators.
- **Not a GUI port.** The GUI surface (Auga, slice-3 placeholder) is
  separate and will share data via the existing handle Protocols.
- **Not a feature factory.** Stofa is for surfaces the operator already
  has good reasons to touch. New capabilities still land as core slices;
  Stofa surfaces them when they're real.

## Why Stofa exists

Three reasons.

### 1. The CLI is a great power but a poor *home*

`ember chat` is correct for what it does: a streaming REPL with tool
approval. But operators have to:

- Quit chat to run `ember well ingest`
- Quit chat to run `ember doctor`
- Quit chat to edit `ember.yaml` and reload
- Re-launch chat to see the changes
- Track separately what `ember mcp ping` returned and what the chat said
  about it

A TUI lets all of this happen in one persistent context. The chat is
running while ingest runs in a panel. The doctor health is visible in the
status bar. The Well's document count ticks up as documents land. The
operator doesn't lose their conversation buffer to look at *anything*.

### 2. Operators learn faster when they can *see*

Stofa makes Ember's state legible. Right now the operator has to know that
`config.tools.enabled: true` plus `--allow-tools` overrides config, plus
that some tools need MCP servers spawned, plus that the audit log is at
`~/.ember/state/tool_audit/`. In Stofa, that's a panel labelled "Tools"
with the tools listed, a green/grey indicator for each, and a `View audit`
shortcut. Discovery is built in. The first-run wizard (Hjarta) becomes a
warm hall scene, not a sequence of stdin prompts.

### 3. Coziness is a Vow-aligned feature

The Vow of Public-Friendliness ("operator-facing errors readable by
non-developers"; the README's "Got a toaster? Good!" tone) is already
mechanically enforced for errors. Stofa extends it to the *whole
operator experience*. Warmth + clarity + a small cute pet on the floor +
a quiet Norse aesthetic — these are not decoration. They are how an
operator's first hour with Ember decides whether Ember stays installed.

## What "best ever" means here

When the brief says "best, most advanced, most user-friendly, most
beautiful, most modern Viking, most fun, most cute, most stable, most
robust ever TUI," that is a *direction*, not a benchmark. The plan is:

- **Best** = better than the operator's current chat experience by a
  large margin AND defensibly best-in-class on at least one axis (we pick
  the *cozy AI hall* axis where no one is competing).
- **Most advanced** = stable async streaming + live updating panels +
  optional terminal-graphics + plugin architecture + theming + pets.
- **Most user-friendly** = first-touch usable inside 60 seconds; every
  screen has a `?` overlay; nothing required is hidden behind a menu.
- **Most beautiful** = serious considered visual design, not the
  default-blue-on-black of every other tool.
- **Most modern Viking** = restrained Norse motif (runes as ornament,
  not as gatekeeping), modern type, considered color, *not* a fantasy
  LARP aesthetic.
- **Most fun + cute** = the pets. See [`04_PETS_VISION.md`](04_PETS_VISION.md).
- **Most stable + robust** = Vow of the Unbroken Whole binds Stofa
  too; tested across terminals, resize-safe, graceful when colors /
  Unicode / mouse aren't available.

We will not achieve every superlative. We will achieve a *coherent
design* that lets us call Stofa "the cozy Viking AI hall of the terminal"
without any operator hearing that and rolling their eyes.

## What success looks like

A new operator runs `pip install ember-agent[tui]`, then `ember`, and:

1. The hall opens. There's a fire icon in the corner. A small raven is
   perched on the Well panel. The status bar says "no identity yet —
   press `n` to set up."
2. They press `n`. The Hjarta wizard appears as a warm vignette in the
   center of the hall, not a stdin Q&A. Three questions, all visible at
   once. They name Ember, pick a Funi model, pick a Well backend.
3. They land in Chat. The cursor blinks in the input area. The model is
   loading; the fire crackles softly (a faint pulse on the fire icon).
4. They type "hello". Stream tokens flow in. The raven flutters once.
5. After 30 seconds, they press `?`. Every key is shown, grouped by panel.
6. They press `w` and the Well panel takes focus. They run an ingest of
   `~/notes`. A bee appears, ferrying documents. Chunk count ticks up.
7. They press `c` and they're back in the conversation. The chat has
   stayed alive the whole time. They ask "what do my notes say about X".
   Hits cite the documents they just ingested. The raven hops to perch
   over the citation panel.

At no point does the operator have to read a man page, edit a YAML file,
or guess at the right CLI flag. The whole thing feels alive.

## What Stofa is *for*

Concrete primary use-cases, in priority order:

1. **The cozy AI chat** — long sessions with Ember on the operator's own
   knowledge base.
2. **Operator-grade observability** — at-a-glance health (Funi reachable?
   Well populated? MCP servers up?).
3. **Ingest workflow** — point Ember at a directory, watch documents land,
   see when it's done.
4. **Tool approval theater** — the moment Funi proposes a tool call,
   the operator sees the call in a clean approval modal, not a stdin
   prompt buried in a chat scrollback.
5. **First-run wizardry** — Hjarta as a hall scene.
6. **Plugin / MCP management** — add an MCP server, see its tools, see
   what was approved.

Secondary (deferred to later phases):

- Markdown viewer for Well documents
- Episode browser
- Audit log browser with filters
- Theme switcher with live preview
- Pet customization

## What Stofa is *not for*

- Heavy data exploration (use the Bifröst HTTP gateway when it ships
  and hit Ember's Well with a real analytics tool).
- Code editing (that's neovim's job; Ember doesn't compete).
- A general-purpose terminal multiplexer.
- A replacement for `ember chat` in scripts (chat keeps its piped /
  one-shot semantics).

## How Stofa relates to existing surfaces

| Surface | Status | Stofa's relation |
|---|---|---|
| `ember chat` | shipped, slice 2 | Stofa hosts the same logic in a panel; CLI chat keeps working unchanged for scripts |
| `ember ask` | shipped, slice 2 | Unchanged. Pipe-friendly one-shot stays one-shot. |
| `ember setup` | shipped, slice 2 | Becomes the *Hjarta wizard* screen inside Stofa; also still runs as a CLI subcommand |
| `ember well ingest` | shipped, slice 2 | Becomes the Well screen's "ingest a directory" action; also still runs as a CLI |
| `ember doctor` | shipped, slice 2 | Becomes the always-visible status bar + the dedicated Doctor screen |
| `ember mcp serve/list/tools/ping` | shipped, batch I | Becomes the MCP screen |
| `ember` (no args) | currently shows help | After Stofa ships: opens Stofa |
| Auga (GUI) | placeholder (ADR-0012) | Shares handles, shares prompts, can render the same conversations |
| Rödd (voice) | placeholder (ADR-0012) | Same |

## Closing word

If `ember chat` is a phone call with a friend, **Stofa is the hall you
both sit in.** Same conversation, but now there's also a fire, a window
to the Well, a couple of pets at your feet, a sense that this is a real
place you can return to. That is what the brief means by "most advanced,
most beautiful, most cute" — not maxed-out chrome, but a *room someone
designed*.
