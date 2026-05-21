# 27 — Glow

> https://github.com/charmbracelet/glow

A markdown renderer for the terminal. Single-purpose, beautiful,
written in Go by the Charm team. Teaches Stofa about **rendering
prose**, **type-as-design**, and **the small-and-focused tool
philosophy**.

---

## What it is

`glow README.md` opens the markdown in a TUI with beautiful
formatting: real heading hierarchy, syntax-highlighted code blocks,
proper list formatting, link annotations, table rendering.

```
                                                              ━━━━━━━━

  ╭── README ─────────────────────────────────────────────╮
  │                                                        │
  │  # Project Ember                                       │
  │                                                        │
  │  Got a toaster? Good. You can run Ember on it.         │
  │                                                        │
  │  ## Features                                           │
  │                                                        │
  │  • Funi — local LLM via Ollama                         │
  │  • Brunnr — vector store (sqlite-vec or pgvector)      │
  │  • Strengr — health checks                             │
  │                                                        │
  ╰────────────────────────────────────────────────────────╯
```

Pure rendering. No editing. No navigation between files (well, a
small list view exists, but the focus is rendering).

---

## The clever idea: prose deserves design

Most TUIs render markdown as either:

- Raw text (you see `# Heading` literally)
- A faked rendering (one bold weight; no real type hierarchy)

Glow does *real* typography:

- Headings get scale (not just bold) via spacing + horizontal rules.
- Code blocks have syntax highlighting + visible borders.
- Tables align properly.
- Links are styled (color + underline where the terminal supports
  it).
- The whole thing has **padding around the content** that gives it
  room to breathe.

The result is that reading prose in glow feels like reading prose in
a typeset book. Not a perfect comparison — terminal cells aren't
type — but the *care* matches.

---

## What we steal

1. **Markdown rendering for Funi replies.** When Funi returns
   markdown (which it often does for code-shaped questions), Stofa
   renders it with real headings, code blocks, lists. Rich (the
   library underneath Textual) provides this.
2. **Generous padding inside content panels.** Glow's content has
   ~3-4 cells of padding inside its border. Stofa's chat messages
   panel has `padding: 1 2` (1 row top/bottom, 2 cells left/right)
   — same spirit.
3. **Code blocks with real syntax highlighting.** When Funi replies
   with a code block, we syntax-highlight it via Rich. The language
   is sniffed from the code fence; we fall back to plain on
   unknown languages.
4. **Horizontal rules as section separators.** Glow uses ─── lines
   between sections. Stofa's settings screen uses the same to
   separate sections without requiring a heavy border.

### What we avoid

1. **Glow's pager mode.** Glow scrolls one page at a time by
   default. Stofa scrolls continuously (more familiar from web
   browsers).
2. **The "rendering is the whole point" focus.** Glow does only
   rendering. Stofa renders AND chats AND ingests AND probes.

---

## The Charm philosophy

The Charm team (charmbracelet) has built a small constellation of
beautiful TUIs: glow, gum, bubbletea, soft-serve, etc. Their
philosophy (from blog posts + talks):

- **Beauty in the terminal is allowed.** Reject the "terminal must
  be Spartan" prejudice.
- **Small and focused.** Each tool does one thing.
- **Cute is OK.** Their logos all have cute animal mascots.
- **Quality of life everywhere.** Defaults that just work.

Stofa shares all four. Stofa is *less small and focused* than any
single Charm tool, because we have a multi-screen application.
But the principles apply.

---

## Specific renderings we want to match

### Code blocks in chat

When Funi says:
````
Here's how to install Ember:

```bash
pip install ember-agent[sqlite_vec]
```
````

Stofa renders:

```
                                                              ━━━━━━━━

  Here's how to install Ember:

  ╭── bash ──────────────────────────────────────────────╮
  │ pip install ember-agent[sqlite_vec]                   │
  ╰───────────────────────────────────────────────────────╯
```

Syntax highlighting on the `pip install` line; rounded border;
language label in the top-left of the border.

### Lists in chat

When Funi says:

> Here are three things to try:
> - Run `ember setup` to configure
> - Run `ember well ingest` to load documents  
> - Run `ember chat` to start chatting

Stofa renders:

```
  Here are three things to try:

   • Run `ember setup` to configure
   • Run `ember well ingest` to load documents
   • Run `ember chat` to start chatting
```

Bullet character (`•`) instead of `-`; consistent indent; backticks
get rendered as monospace (which in a terminal means they get a
subtle background tint).

---

## What glow does that we don't

- **Render whole files.** Glow's job is "render this whole .md."
  Stofa's job in chat is "render this one message" — which is
  shorter and arrives over time as it streams.
- **Pager navigation.** Glow has Page Down / Page Up styled
  scrolling. Stofa's chat scrolls continuously.

---

## Closing

Glow proves that *reading is a design problem*, not just a
rendering one. Stofa borrows the typographic care for in-chat
markdown, code blocks, and lists — making Funi's replies *pleasant
to read*, not just legible. Reading is what an operator does in
Stofa for hours; the typography earns its keep many times over.
