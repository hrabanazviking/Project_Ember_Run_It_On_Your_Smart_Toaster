# 42 — Information Density

How much to show, where to show it, when to show it.

## The density spectrum

```
   sparse                  balanced                     dense
   ──────                  ────────                     ─────
   one number             a dashboard                  a spreadsheet
   on a screen            with 4 panels                with 1000 rows
   (cute, slow)           (Stofa target)              (powerful, fatiguing)
```

Stofa sits in the *balanced* middle. Sparse is wasteful; dense is
exhausting. The target: every cell on screen earns its place AND
the whole screen is scan-able in 2-3 seconds.

## The 2-second rule

A trained operator looking at a familiar Stofa screen should be able
to answer "what's going on?" in 2 seconds. Concretely:

- **HomeScreen:** what realms are up, what's in the Well, what's
  the latest activity — 2 seconds.
- **ChatScreen:** what's the operator's last message, what's Ember's
  in-progress reply, where are the citations — 2 seconds.
- **DoctorScreen:** which realm is OK, which isn't, what's the
  detail — 2 seconds.

If a screen takes longer than 2 seconds to scan, it's either too
dense or insufficiently organized.

## How to scan-optimize

### Hierarchy via visual weight

The eye is drawn to:
- High contrast (color vs neutral).
- High weight (bold vs regular).
- Bigger areas (a full panel vs a one-line label).
- Top-left position (most languages read top-to-bottom, left-to-right).

Stofa uses this:
- **The operator's input cursor** in chat is high-contrast — it's
  where the operator's about to type.
- **Errors** are red ($error token) — the *only* high-contrast red
  on screen, so they jump out.
- **The current screen name** is in the chrome header — top, bold,
  primary color.
- **Realm status** in the StatusBar is left of center — where the
  operator's eye lands first.

### Hierarchy via whitespace

Whitespace IS information. It says "these things are grouped" and
"these things aren't."

- Each panel has 1 row/column of padding inside its border.
- Panels are separated by 1 cell of gutter (grid).
- Conversation turns in chat have a blank line between them.
- Major sections in Settings have a blank line between them.

We do not save the cell. The cell saved is the operator's eye time
spent.

### Hierarchy via position

Same information, different position, different meaning:

- Top of chat panel: oldest message (scrolled-into-history).
- Bottom of chat panel: newest message (just-arrived).
- Bottom of any screen: input bar (where to type).
- Bottom of the app: StatusBar (chrome).

Position is a label. Per [`../research/21_LAZYGIT.md`](../research/21_LAZYGIT.md):
operators stop reading the label after the first session.

## What we don't show (deliberate omission)

A common density failure: showing things the operator doesn't need.
Stofa is aggressive about omission.

### Not shown by default

- **Funi's full token-by-token timing.** We show "thinking" via the
  hearth pulse, not "first token in 247ms; 12.3 tok/s." Token-rate
  is a debug overlay only.
- **The full system prompt.** It's in the audit log if the operator
  cares; not in the chat panel.
- **Embedding dimensions.** Visible only in Settings → Brunnr.
- **The full retrieval-hit text.** We show the title + a 1-line
  excerpt; full text in the citation card on Enter.
- **Audit log entries.** Not on HomeScreen; in the dedicated
  AuditLogScreen (V2).
- **Pet hit-point counters or whatever else gamification might
  tempt us with.** Pets just are; no stats to track.

### Shown only on demand

- **Detailed help.** `?` opens the help overlay.
- **Document chunks.** Open via WellScreen → Enter on document → tab
  to "Chunks".
- **Raw MCP responses.** MCPScreen → `v` on a server (view raw).
- **Operator config diff (between in-memory and ember.yaml).**
  SettingsScreen → `Ctrl-D` for diff (V2).

## Specific density targets

### HomeScreen
- 4 panels.
- Each panel: ~4 lines of content + title.
- Total visible: ~20 information units (counts, names, status dots).
- Scan time: target 2 seconds.

### ChatScreen
- Last ~3-5 conversation turns visible by default.
- Input bar: 1 prompt + cursor.
- Status bar: realm states (4 dots + 4 abbreviated metrics).
- Scan time: target 1 second for current state, longer to read
  the conversation itself (which is the operator's *task*, not the
  *chrome*).

### WellScreen
- ~30 documents visible in the sources column at terminal height 40.
- Details panel: ~10 fields.
- Header stats: 3 numbers (docs, chunks, size).
- Scan time: target 2 seconds for an overview.

### DoctorScreen
- 4 realm rows.
- Each row: realm name + status + 2-3 detail fields.
- Total: 4 rows × 4 fields = ~16 information units.
- Scan time: target 1.5 seconds.

## When density is the operator's choice

Operators differ:

- **Védis** (cozy) wants air. Generous padding, no walls of text.
- **Sigrún** (power) wants every cell carrying weight.

Stofa's defaults are **mid-density**. Power-users can opt into
denser variants via Settings:

```yaml
stofa:
  ui_density: medium   # default; alternative: "compact"
```

`compact` mode:
- Reduces padding from 1 to 0 inside panels.
- Removes the blank line between conversation turns.
- Reduces grid gutter from 1 to 0.

This is a one-flag opt-in for operators who want it. Defaults
remain mid-density.

## What we measure

In CI snapshot tests:

- **Visible characters per cell.** Each panel's content area
  averages ≥ 40% non-whitespace characters. (Below that = wasteful;
  above 70% = too dense.)
- **Distinct visible elements per panel.** Average 5-10. Above 15
  triggers a design review.
- **Maximum text density of any single line.** No line > 80% of its
  cell width filled with characters (leaves room for variability).

## Closing

Density is not "fit more in." Density is "give every cell a job."
Stofa's screens are mid-density on purpose: every visible cell is
information, plus enough whitespace to scan, plus enough chrome to
orient. Operators who want denser have it via one flag. Operators
who want sparser have it via choosing not to fill their screen with
Stofa (`Esc` always works).
