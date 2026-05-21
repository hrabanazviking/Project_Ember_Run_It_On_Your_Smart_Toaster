# 87 — Screen: Hjarta Wizard

The first-launch identity setup. The TUI counterpart to the CLI
`ember setup` flow.

---

## Purpose

When an operator first runs `ember tui` and has no identity
configured, the wizard walks them through:
1. Naming Ember.
2. Picking a Funi model.
3. Picking a Brunnr backend.
4. (Optional) enabling tools.
5. Writing the identity + config.

After the wizard, Stofa proceeds normally with the operator's
choices.

---

## Layout

```
┌── Stofa ──── ᛟ ──── Hjarta ── First settings ── 🔥 ─┐
│                                                       │
│                                                       │
│        Welcome.                                       │
│                                                       │
│        I'm a small AI companion meant to run          │
│        on your own hardware. Let's set me up.         │
│                                                       │
│                                                       │
│        What would you like to call me?                │
│                                                       │
│        Name: [ Mimir                              ]   │
│                                                       │
│                                                       │
│                                                       │
│        Tab to advance · Esc to cancel · ? for help    │
│                                                       │
└───────────────────────────────────────────────────────┘
```

This is **state 1 of 4 (or 5)**. Each subsequent state shows the
operator's prior answers (small recap) plus the next question.

State 2: "Which language model should I use?" (with helpful
defaults pre-filled based on Ollama auto-detection if possible).

State 3: "Where should I keep my knowledge?" (sqlite_vec or
pgvector).

State 4: "Should I use tools? (default: no — opt-in)"

State 5: "Ready! Press Enter to begin."

---

## Implementation

`src/ember/stofa/screens/hjarta_wizard.py` —
`HjartaWizardScreen(textual.screen.Screen)`.

Composes:
- A title bar with the Othala rune (`ᛟ`).
- A centered question area.
- An input widget (Input / Select / Checkbox depending on state).
- Footer with Tab/Esc/?/Help hints.

The wizard wraps the existing Hjarta FSM
(`src/ember/spark/hjarta/machine.py`). Same states, same transitions,
visual presentation.

---

## State transitions

```
NAME_EMBER → PICK_FUNI → PICK_WELL → ADVANCED_TOOLS → WRITE_IDENTITY → done
```

Each state has a Question, an InputType, and a Validate function.
Tab/Enter advances if validation passes; Shift+Tab goes back; Esc
prompts confirm-and-cancel.

---

## Visual treatment

- **Centered vignette.** The wizard content occupies the middle of
  the screen, with empty space above and below. Like sitting down
  at a table.
- **One question at a time.** Not a form with 5 fields visible at
  once. Per Hick's Law: one decision at a time is fastest.
- **Prior answers visible.** Operator can see what they chose so
  far without scrolling.

After step 1 (NAME_EMBER):

```
┌── Stofa ──── ᛟ ──── Hjarta ── 2 of 4 ── 🔥 ─┐
│                                                │
│        You named me: Mimir                     │
│                                                │
│                                                │
│        Which language model should I use?      │
│                                                │
│        I'll talk through Ollama. Recommended   │
│        for Pi-class hardware: llama3.2:3b      │
│                                                │
│        Model: [ llama3.2:3b              ]     │
│                                                │
│        Tab to advance · Shift-Tab to go back   │
│                                                │
└────────────────────────────────────────────────┘
```

---

## Field help (`?`)

Same as the SettingsScreen pattern — pressing `?` on a focused
field opens an overlay with explanation.

---

## Pet behavior during the wizard

- **Funi-spark** still pulses if Stofa is loading something in
  background (e.g., detecting Ollama).
- **Ember-ember** in chrome.
- **Other pets** disabled during the wizard. The wizard is meant
  to be a focused single-task; no distractions.

---

## Esc handling

Operator presses Esc:

```
╭── Cancel setup? ───────────────────────╮
│                                          │
│  You haven't finished setting up Stofa.  │
│  Without an identity, chat can't start.  │
│                                          │
│  Cancel anyway? (y/n)                    │
│                                          │
╰──────────────────────────────────────────╯
```

If y: Stofa exits with code 1 and message "Setup canceled. Run
`ember setup` to try again."

If n: returns to wizard.

---

## Completion (WRITE_IDENTITY)

Final step:

```
┌── Stofa ──── ᛟ ──── Hjarta ── 5 of 5 ── 🔥 ─┐
│                                                │
│        Almost done.                            │
│                                                │
│        I'll write your choices to:             │
│          ~/.ember/config/ember.yaml            │
│          ~/.ember/identity.json                │
│                                                │
│        Press Enter to begin.                    │
│                                                │
└────────────────────────────────────────────────┘
```

Operator presses Enter. The wizard:
1. Writes identity.json via `save_identity_atomic`.
2. Writes ember.yaml via `ember.config.writer.write_ember_yaml`.
3. Pops the wizard.
4. Pushes HomeScreen (the operator's first real Stofa view).
5. HomeScreen shows a welcome message: "Hi, I'm {Mimir}. Press
   c to chat."

---

## What HjartaWizardScreen does NOT do

- **Auto-detect Ollama models.** V1: operator types model name.
  V2: try `GET http://localhost:11434/api/tags` and offer a
  picker.
- **Test the chosen model.** That happens at first chat turn.
- **Skip steps.** Each step is required to produce valid config.
- **Modify config after first run.** That's Settings' job.

---

## Closing

The Hjarta wizard is the *threshold ritual* of Stofa. Operator
crosses it once, exits with an identity, becomes a Stofa user.
Friendly. Centered. One question at a time. Othala rune in the
title (heritage, ancestral home). The pets are quiet — this is a
serious moment.
