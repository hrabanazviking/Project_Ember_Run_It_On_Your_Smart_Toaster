# 32 — ChatGPT-style and other AI TUIs

The closest competitors / cousins. We study: **claude-code**, **mods**,
**gpt-cli**, **llm (Simon Willison)**, **aichat**, **fabric**,
**ollama-tui**. Each one is a TUI / CLI for talking to LLMs.

Stofa learns from what they do right and what they leave on the table.

---

## The landscape (as of 2026)

| Tool | Type | Primary surface |
|---|---|---|
| **claude-code** | CLI | streaming-text chat in your terminal + tool use |
| **mods** | CLI | pipe-friendly: `cat file \| mods 'explain this'` |
| **gpt-cli** | CLI | one-shot or REPL chat |
| **llm** (Simon Willison) | CLI | multi-provider; templates; logging |
| **aichat** | CLI | shell integration; multi-provider |
| **fabric** | CLI | "patterns" (saved prompts) |
| **ollama-tui** | TUI | TUI specifically for Ollama; small audience |

Among these, **claude-code** and **ollama-tui** are the most-similar
to what Stofa is becoming.

---

## Claude-code (Anthropic's own)

The cleanest CLI-AI experience available. Streaming, tool-use
integrated, clear chrome.

### What works

- **Streaming with tokens visible as they arrive.** Not pseudo-
  paragraph dumps; real per-token streaming.
- **Clear separation of operator turns from assistant turns.**
  Different colors / prefixes.
- **Tool-call rendering in-place.** When a tool fires, the call +
  result are rendered inline as a callout, not in a separate panel.
- **Ctrl-C tagging of partial answers.** Same pattern Ember uses.

### What we steal

Stofa's ChatScreen takes the *visual conventions* from claude-code:

- Per-turn separator.
- Streaming tokens.
- Inline tool-call callouts.
- Ctrl-C tagging.

### What we add

- The hall around it (other screens, dashboard).
- The pets.
- Hjarta wizard as a real screen.
- Multi-MCP-server orchestration.

### What we avoid

- Sign-in required.
- Cloud-only execution (we're sovereign-by-default).

---

## Ollama-tui (community)

A small TUI specifically for Ollama. Single screen: chat with a model.

### What works

- Streaming.
- Model picker.

### What it leaves on the table

- No retrieval.
- No tool use.
- No MCP.
- No dashboard / multi-screen.
- No theme system.
- No pets (of course; nobody but us is doing this).

Stofa is essentially "ollama-tui plus a hall plus retrieval plus
tools plus MCP plus pets plus theming plus accessibility."

---

## Mods (Charm)

Not a TUI; a CLI. Pipe-friendly chat:

```bash
cat error.log | mods 'what's wrong here?'
```

### What works

- Stays out of the way; pure CLI composition.
- Streams to stdout.

### What it teaches us

The CLI-pipe path matters. Stofa is a *TUI*, but Ember keeps
`ember chat` and `ember ask` for pipe-friendly use. We don't compete
with mods in pipelines; we serve a different need (the persistent
hall).

---

## llm (Simon Willison)

A CLI tool with multi-provider support, template library, SQLite
logging.

### What works

- Multi-provider abstraction (OpenAI, Anthropic, Ollama, etc.)
- Templates (saved prompt snippets).
- Logging to SQLite.

### What we steal

Conceptually: the SQLite-as-log pattern matches what Ember already
does with Episodes (in Brunnr). The template system is something
Stofa could surface via a "saved prompts" screen in V2.

### What's different

llm is single-screen-CLI; Stofa is multi-screen-TUI. Different shape.

---

## Aichat / fabric / etc.

All variations of "CLI with plugin/template/multi-provider features."
None are TUIs in the persistent-application sense Stofa is.

---

## What's missing from the landscape (Stofa's opening)

Looking at all of these, there's a clear gap:

- No TUI focused on **AI as a persistent hall** (everyone else
  treats AI as a transaction).
- No TUI with **integrated tool-approval theater** (claude-code is
  close, but it's CLI-shaped, not multi-screen).
- No TUI with **first-class personal-knowledge integration** (no
  one else has the Well concept first-class).
- No TUI that's **cute, beautiful, Norse-styled, and pet-having**.

Stofa fills all four.

---

## What we explicitly do NOT do

- **Compete with claude-code for "fastest CLI AI tool."** That's
  not our game.
- **Multi-provider abstraction.** Ember picks a Funi adapter at
  startup; Stofa doesn't switch providers mid-session.
- **A template library.** V2 maybe; V1 is chat + tools + knowledge.

---

## Specific Stofa borrowings

From claude-code:
- Per-turn separators in chat.
- Token-by-token streaming.
- Inline tool-call callouts.
- Ctrl-C tagging.

From the AI-CLI landscape generally:
- Markdown rendering of replies (per [`27_GLOW.md`](27_GLOW.md)).
- Code block syntax highlighting.

What's all our own:
- The multi-screen hall.
- The pets.
- The dashboard.
- The Norse aesthetic.

---

## Closing

The AI-CLI ecosystem is rich but uniformly one-screen-transactional.
Stofa is the first AI TUI that treats the relationship as a *home*
rather than a *request*. That positioning is what makes Stofa worth
building — not "another chat tool" but a categorically different
shape.
