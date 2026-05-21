# 01 — Naming

## Chosen name: **Stofa**

**Stofa** /ˈstoː.va/ — Old Norse. Literally *the hall* or *the
heated common-room* of a longhouse: where the household ate, talked,
played tafl, slept on benches along the walls. The center of domestic
life.

Pronounced: **STOH-va** (the *o* like in *snow*, *a* like in *idea*).

### Why this name fits

- **It names what the thing IS.** A TUI is a *room* the operator enters
  and stays inside. Not a command, not a request, not a transaction —
  a sitting-room. "I'm in Stofa" reads the same as "I'm in the kitchen."
- **It's small and warm.** Two syllables, soft consonants. The operator
  saying it to a friend doesn't feel embarrassed.
- **It carries the Norse register without LARP.** Compare to *Mjölnir*
  or *Valhalla* (over-claimed) or *RuneShell* (cringe). Stofa is
  domestic Norse — the language of households, not of myth.
- **It sits in the existing taxonomy.** Ember already has six True
  Names (Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr) and three
  slice-3 placeholders (Auga, Rödd, Bifröst). Adding Stofa fits the
  pattern: short, lowercase-and-honest, semantically loaded.

### Why not alternatives

Names workshopped and set aside:

| Candidate | Meaning | Why rejected |
|---|---|---|
| **Auga** | the eye | Already claimed by the slice-3 GUI. |
| **Sjón** | sight | Same conflict, plus it's an Icelandic singer's name. |
| **Augasal** | eye-hall | Sounds invented (it is — compound form). |
| **Sjónarhorn** | viewpoint | Mouthful (4 syllables); operators won't say it. |
| **Speglur** | mirror | Promises a reflection; that's not quite Stofa's role. |
| **Þing** | assembly, court | Suggests deliberation; Stofa is more cozy. |
| **Hringborð** | round table | Implies multi-user; Stofa is single-operator. |
| **Vísir** | pointer, index | True but cold; doesn't capture the *room* feeling. |
| **Vé** | sanctuary | Too sacred — Stofa is a place for relaxing. |
| **Lios** | light | Too thin; doesn't say "you live here." |

The decision rule: **does the name describe a place the operator can
*be in* for an hour at a time?** Stofa passes. Most candidates failed
this. *Augasal* came close, but inventing compound words for a project
that values short clear names felt off.

## How operators talk about it

Idiomatic in the docs and prompts:

- "Open Stofa" → run `ember tui` (or `ember`, once Stofa is the default
  subcommand).
- "In Stofa" → using the TUI, as opposed to `ember chat` (the bare REPL).
- "Stofa is ready" → the loading splash is done; the hearth icon is lit.
- "Press `q` to leave Stofa" → quit the TUI.

Not idiomatic (avoid in docs):

- "The Stofa app" — Stofa *is* Ember; it's a surface, not a separate app.
- "Stofa TUI" — redundant; Stofa is a TUI by definition.
- "STOFA" all-caps — Stofa is a noun, not an acronym.

The README + INSTALL docs use **Stofa** in body text; the command-line
references use lowercase `stofa` where it appears as a CLI string
(though it never will — the CLI subcommand is `tui`).

## Where the name lives in the codebase

- Python package: `src/ember/stofa/` (Phase 1+).
- ADR: `docs/decisions/0015-stofa-tui.md` (to be drafted).
- Config block: `EmberConfig.stofa: StofaConfig` (theme, pets-enabled,
  layout preferences).
- CLI entry: `ember tui` (subcommand) and `ember` (alias when stdin is
  a TTY and no other subcommand was given).
- Docs root: `docs/tui/` (this directory).
- Memory file: `~/.claude/projects/.../memory/project_stofa.md` (to be
  written once the surface ships).

## Where the name does NOT belong

- **Tool names.** MCP-bridged tools keep the `mcp__<server>__<tool>`
  convention. First-party tools keep `search_well`, `read_local_file`,
  `fetch_url`. Stofa is not a namespace for tools.
- **Schema dataclasses for the agent itself.** `EmberConfig.funi`,
  `EmberConfig.brunnr` — Stofa is a *surface*, sibling to these, not
  one of them.
- **Episode metadata.** Episodes are universal; they don't carry "this
  was a Stofa conversation" markers. (An operator switching between
  Stofa and `ember chat` should see the same history.)

## Sibling-surface names (placeholder, for context)

The slice-3 plan groups Stofa with three other planned surfaces. None
of these are built yet; the names are reserved:

- **Auga** (the eye) — desktop GUI.
- **Rödd** (the voice) — speech-in / speech-out surface.
- **Bifröst** (the rainbow bridge) — HTTP gateway that other agents
  and tools can call.

Stofa is the first to be designed because:
1. It runs everywhere Ember already runs (terminal).
2. It's the lowest-dep option (Textual; no GUI toolkit, no audio).
3. The operator gains the most per line of code shipped.

## Closing

A good name does not merely label a thing. It reveals what the thing
has always wanted to be. *Stofa* reveals that Ember's interface — at
its best — is a hall you go to, not a command you type. The rest of
this design tree builds the hall around that name.
