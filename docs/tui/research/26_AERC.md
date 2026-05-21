# 26 — Aerc

> https://aerc-mail.org/

An email TUI in Go. Vim-flavored, multi-tab, scriptable. Teaches
Stofa about **tabs**, **the email-message-list pattern**, and
**multi-account / multi-context UX**.

---

## What it is

Open-source IMAP/SMTP email client running in the terminal. Built by
Drew DeVault and the SourceHut community. Designed for power-users
who live in mutt but want something better.

```
┌── ⌘ ── [1] INBOX (123) ─ [2] sent ─ [3] drafts ─────────────────┐
│   ● 14:32  Volmarr Wyrd            Re: stofa design tree         │
│     12:01  Sigrún H.                Helix vs vim showdown        │
│   ○ 10:45  Iðunn the Curious       I tried it!                   │
│     09:22  Eirwyn R.                SSH tip                      │
│ ─────────────────────────────────────────────────────────────── │
│                                                                  │
│  From: Volmarr Wyrd <volmarr@example>                            │
│  To: stofa-design@example                                        │
│  Subject: Re: stofa design tree                                  │
│  Date: 2026-05-21 14:32                                          │
│                                                                  │
│  > what name did you settle on?                                  │
│                                                                  │
│  Stofa. "The hall" in Old Norse. Soft consonants, two-syllable.  │
│  …                                                                │
└──────────────────────────────────────────────────────────────────┘
```

---

## The clever idea: tabs as a context layer

Aerc puts multiple accounts/folders/searches in tabs across the top.
`Alt-1` / `Alt-2` / etc. jump between. Tab order is fixed by the
operator's config.

This means an operator can have:

- INBOX of work account
- INBOX of personal account
- A search ("from:client subject:invoice")
- A draft they're composing

…all "open" simultaneously, switching between them in one keystroke.

### What we steal

For V1, **we don't.** Stofa V1 doesn't have multi-tab. The screen
stack model (one screen at a time, pop-and-push) is enough.

For V2+, we keep this in mind. If operators end up wanting multiple
chat conversations open, tabs are the right pattern. (See [`../architecture/13_SCREEN_HIERARCHY.md`](../architecture/13_SCREEN_HIERARCHY.md)
under V2+ for the tab discussion.)

---

## The 3-pane email pattern

Email TUIs converge on:

- Top: tab/folder selector
- Middle: message list
- Bottom: focused message body

This is the same pattern as ranger's miller columns, just rotated.

### What we steal

Not the pattern itself for chat (chat is conversational, not
listed). But we borrow it for V2's planned **EpisodeBrowserScreen**
(see [`../architecture/13_SCREEN_HIERARCHY.md`](../architecture/13_SCREEN_HIERARCHY.md)):

- Top: filter / search input
- Middle: episode list
- Bottom: selected episode's full text + retrieval cited

Episodes are list-shaped; the email pattern fits.

---

## What aerc teaches about vim-likeness

Aerc is heavily vim-keymapped. Operators coming from mutt feel at
home. New operators feel lost.

Aerc handles this with:

- A `:help` command that opens documentation in a buffer.
- A startup tutorial that runs the first time.
- A configurable keymap for non-vim operators.

Stofa's response:

- `?` always shows current bindings (better than `:help` for
  discoverability).
- No startup tutorial. (Hjarta is the first-launch surface; it's
  about identity, not key training.)
- Configurable keymap via `ember.yaml`.

---

## The scriptability lesson

Aerc has a `:` command line where the operator can type any aerc
command. Commands can be chained, scripted, bound to keys.

This is essentially a command palette, just slightly different in
implementation.

### What we steal

The `:` opens our command palette. Operators type, fuzzy-search,
hit Enter. Every named action is here. Per
[`../architecture/16_KEYBINDING_PHILOSOPHY.md`](../architecture/16_KEYBINDING_PHILOSOPHY.md).

What we DO NOT steal: command chaining (`:foo && bar`). Stofa keeps
commands single. Power-users who want chained behavior can write a
plugin (V2).

---

## What aerc does that we don't need

- **IMAP / SMTP / IDLE protocol stuff.** Stofa is a chat TUI, not a
  mail TUI.
- **PGP integration.** Not relevant.
- **HTML email rendering.** Not relevant.

---

## What aerc gets wrong that we improve

- **The vim curve.** Aerc is hard for novices. Stofa is easy by
  default + power-user-tunable.
- **The configuration burden.** Aerc requires a fair amount of
  config to fit your workflow. Stofa works out of the box.

---

## Closing

Aerc shows what a vim-flavored TUI looks like when applied to a
list-and-detail data model. Stofa borrows the command-palette
pattern, the `?` discoverability, and the responsive defaults
across keybinding traditions. We don't borrow the multi-tab
model — for V1. V2 may revisit.
