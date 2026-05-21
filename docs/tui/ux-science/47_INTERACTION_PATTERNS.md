# 47 — Interaction Patterns

A catalogue of the *patterns* Stofa uses for operator-app
interaction. Each pattern is documented so screen designers can pick
the right one rather than invent.

---

## Modal vs modeless

**Modal:** input is captured by one thing until that thing is
dismissed.

**Modeless:** input flows normally; multiple things accept input
based on focus.

Stofa is **mostly modeless**. Modals are reserved for:

1. **ToolApprovalScreen** — the operator MUST answer before chat
   continues.
2. **HjartaWizardScreen** — first-launch identity setup, can't be
   skipped.
3. **HelpOverlay** — informational; modal because it's an overlay.
4. **CommandPalette** — modal during search; dismissible with Esc.

Everything else is modeless. The operator can press Tab to cycle
between panels; pressing `c` jumps to chat from any screen.

---

## Confirmation patterns

### When to confirm

Confirm on **destructive** actions only:

- Delete a document from the Well.
- Reset operator identity (Hjarta-from-scratch).
- Force-quit a running ingest.
- Cancel changes in Settings (only if unsaved).

### When to NOT confirm

- Switching screens.
- Theme changes.
- Pet toggles.
- Opening / closing panels.
- Refreshing data.

### The confirmation pattern

A small inline modal asks:

```
┌─ Confirm ─────────────────────────────────────────┐
│  Delete document 'notes/odin.md'?                  │
│  This will remove all 23 chunks. Cannot be undone. │
│                                                    │
│  [ Yes (y) ]   [ No (n) ]   default: No            │
└────────────────────────────────────────────────────┘
```

Defaults to the **safe** option (No). Enter selects default. Y/N
keys execute. Esc = No.

---

## Loading patterns

### Long operation in foreground

Operator pressed Enter; we're waiting on a slow operation. Show
*something* immediately:

- Replace the input cursor area with an indicator: a spinner +
  one line of status text.
- The hearth icon pulses softly.
- Pets relevant to the operation may animate (bee for ingest).

The spinner is at most one rotating glyph at ~1.5 Hz:

```
... 
asking Funi ⠋
```

(Braille spinner. Falls back to `|/-\` in ASCII mode.)

### Long operation in background

Operator triggered an ingest, then went back to Chat. The ingest
runs in the background:

- StatusBar shows abbreviated progress: "Ingest: 12/95 docs"
- The bee pet appears (visible on whatever screen the operator is
  on; pet layer is global)
- The WellScreen, if visible, shows the live progress

Operator can keep doing other things. When ingest completes:

- StatusBar updates: "Ingest: 95/95 done"
- The bee returns to its idle position
- WellScreen's count refreshes

---

## Notification patterns

Stofa **does not pop up notifications** as modal dialogs. Instead:

- **Status changes** are reflected in the StatusBar.
- **Background events** (ingest done) flash briefly in the StatusBar
  (1-second highlight) and then settle.
- **Errors** show as red text in the relevant context (chat reply,
  panel content) AND tag the StatusBar.

This is per the "no Clippy" anti-pattern (see
[`../research/33_DECORATIVE_TUIS_NAP_PIPES_NEKOTUI.md`](../research/33_DECORATIVE_TUIS_NAP_PIPES_NEKOTUI.md)).

---

## Editing patterns

### Input bars

The chat input bar:

- One line tall by default; expands to multi-line when content
  needs it.
- Cursor is always visible when the bar is focused.
- `Enter` submits; `Shift+Enter` inserts newline.
- `Ctrl+U` clears the input.
- `↑` (when input is empty) recalls the last operator message.
- `Tab` autocompletes from MCP server tool names (V2 feature).

### Settings fields

Text fields in Settings:

- Click or Tab to focus.
- Type to edit.
- Esc reverts the field to its current saved value.
- Enter or Tab commits the field's edit (not the whole form).
- `s` or `Ctrl+S` saves the form.

Dropdown fields:

- Space or Enter opens the dropdown.
- Arrow keys navigate options.
- Enter selects; Esc closes without changing.

Toggle (checkbox) fields:

- Space or Enter flips.
- Visual: `[ ✓ ]` for on, `[ □ ]` for off (with `[x]`/`[ ]` ASCII
  fallback).

---

## Selection patterns

### Single selection

Used in lists where the operator picks one thing at a time:

- WellScreen sources panel.
- MCPScreen server list.
- CommandPalette results.

Visual: focused row has $accent border AND a focus glyph (▶) at the
leftmost cell.

### Multi-selection (V2)

Not in V1. If V2 introduces (e.g., "delete multiple documents"):

- Space toggles selection.
- Visual: selected rows get a checkbox glyph (`[✓]`).
- Action keys apply to all selected rows.

---

## Drill-down patterns

Some screens have detail views — press Enter to drill in, Esc to
back out.

### Two-pane drill-down (WellScreen)

Sources panel left, details panel right. Selecting a document on the
left updates the details on the right. **No drilling required** —
the detail is always visible.

This is the most operator-friendly pattern; it removes a click.

### List-then-detail (V2 EpisodeBrowserScreen)

Episodes listed; Enter on one opens it full-screen; Esc returns to
the list. This is needed when the detail is too big for a panel.

### Inline expand (chat citations)

In chat, citations appear as compact one-line items:

```
ember: I found these in your notes:
   • odin.md (line 14): "the all-father has two ravens..."
   • yggdrasil.md (line 89): "the world tree..."
```

Pressing Enter on a citation expands it inline:

```
ember: I found these in your notes:
   ▼ odin.md (line 14): "the all-father has two ravens..."
      Full excerpt:
        Odin, the all-father of the Æsir, sends his two
        ravens Huginn and Muninn forth each morning to
        gather news from across the nine worlds. They
        return each evening to whisper what they have...
   • yggdrasil.md (line 89): "the world tree..."
```

Esc collapses back. This is the most context-preserving drill-down.

---

## Cancel / undo patterns

### Cancel

- **Esc** in any modal closes it.
- **Esc** in a screen pops to Home (or previous screen).
- **Esc** with focus on an input field defocuses the field (without
  losing the field's text).
- **Ctrl+C** in chat during a streaming response interrupts the
  stream (and tags the Episode).

### Undo

V1 does not have global undo. Specific cases:

- **Settings:** Esc reverts unsaved changes.
- **Chat:** can't undo a sent message (just like in real chat).
- **Ingest:** can't undo (you'd re-ingest if you wanted; or delete
  documents from WellScreen).

V2 may add **Episode rollback** (delete the last Episode) but it's
a low-priority feature.

---

## Search patterns

### Filter in a list (`/`)

In WellScreen, MCPScreen, CommandPalette: `/` starts a filter.

- Filter input appears at the bottom of the pane.
- Typing narrows the list in real-time.
- `Esc` cancels the filter (restores full list).
- `Enter` confirms and selects the first matching item.

Fuzzy matching: characters in order, not necessarily contiguous.
"odn" matches "odin.md" (subsequence).

### Full-text search across data

Not in V1. V2 plans a global `/` from any screen → searches across
Episodes, documents, chunks.

---

## Empty-state patterns

When a panel has no content, instead of blank space:

```
┌── Well ──── 0 documents ────────────┐
│                                      │
│  Your Well is empty.                 │
│                                      │
│  Press i to ingest a directory.      │
│                                      │
│  Or run: ember well ingest <path>    │
│                                      │
└──────────────────────────────────────┘
```

- A friendly one-line message about the state.
- A clear next-action key + hint.
- Optional CLI alternative.

Same for empty conversation, empty MCP server list, etc.

---

## Error-state patterns

When something goes wrong, the operator sees:

```
┌── Funi ──── ✗ Unavailable ──────────┐
│                                      │
│   Ollama is not reachable at         │
│   http://100.67.240.22:11434         │
│                                      │
│   Last attempted: 14:32:18            │
│                                      │
│   Press r to retry · s to edit       │
│                                      │
└──────────────────────────────────────┘
```

- A clear one-line summary.
- Specific detail (where, when).
- Recovery actions (retry, edit config).

Never a stack trace. Never a "An error occurred" without specifics.

---

## Closing

Sixteen named patterns. Modal sparingly. Confirm destructively only.
Loading shown immediately. Notifications never pop. Editing is
keyboard-first with sensible defaults. Selection is single by V1.
Drill-down preserves context where possible. Cancel via Esc; undo
not yet. Search via `/`. Empty states friendly. Error states
recovery-oriented. The interactions feel consistent because they
ARE consistent — picked from this catalogue, not invented per screen.
