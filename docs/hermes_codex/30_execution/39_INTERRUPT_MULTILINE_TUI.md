---
codex_id: 39_INTERRUPT_MULTILINE_TUI
title: TUI Patterns — Interrupt-Without-Loss, Multiline, Slash Completion
role: Forge
layer: Execution
status: draft
hermes_source_refs:
  - cli.py:54-69
  - cli.py:2602-2670
  - cli.py:2920-2925
  - cli.py:10985-11005
  - cli.py:11955-11975
  - cli.py:12200-12340
  - cli.py:14020-14030
  - hermes_cli/completion.py
ember_subsystem_targets: [Munnr]
cross_refs:
  - 30_execution/31_CROSS_PLATFORM_TACTICS
  - 30_execution/34_PROCEDURAL_SKILL_CRAFTING
  - 60_synthesis/63_INTEGRATION_PATHS
  - 50_verification/52_ANTIPATTERN_CATALOG
---

# TUI Patterns — Interrupt, Multiline, Slash

Hermes's CLI is 662 KB in a single file. That's an absurdity. Don't aspire to it. But hidden in that absurdity are five patterns Hermes solved well and that anyone writing a terminal-driven agent will want to steal:

1. **Interrupt-without-loss.** Hit Ctrl-C; the agent stops cleanly; your typed-but-unsent text remains visible.
2. **Multiline editing.** Shift-Enter inserts a newline; Enter submits. Works inside VSCode terminals.
3. **Slash completion.** Type `/`, see a menu of commands + skills + bundles, fuzzy-narrow as you type.
4. **Type-while-agent-runs.** Queue messages for the *next* turn while the *current* turn is processing.
5. **External editor handoff.** Ctrl-G opens the draft in `$EDITOR` for long composition.

I'm Eldra. Let me show you each one from the actual `cli.py`, then propose what Munnr should adopt.

## Foundation — prompt_toolkit

`cli.py:54-67`:

```python
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style as PTStyle
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.application import Application
from prompt_toolkit.layout import Layout, HSplit, Window, FormattedTextControl, ConditionalContainer
from prompt_toolkit.layout.processors import Processor, Transformation, PasswordProcessor, ConditionalProcessor
from prompt_toolkit.filters import Condition
from prompt_toolkit.layout.dimension import Dimension
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.key_binding import KeyBindings
```

The choice of `prompt_toolkit` (over `readline`, `cmd2`, `urwid`, `textual`) is load-bearing. `readline` is GNU-only and ships differently on macOS (libedit). `prompt_toolkit` is pure-Python, cross-platform, and has the layered Application abstraction Hermes needs.

The dep is pinned in `pyproject.toml` at `prompt_toolkit==3.0.52`.

## The Two Input Queues

`cli.py:2920-2925`:

```python
self._interrupt_queue = queue.Queue()
# Tracks whether the turn that just finished was interrupted via
self._last_turn_interrupted = False
```

And `cli.py:11955-11975` (around the chat loop init):

```python
self._interrupt_queue = queue.Queue()   # For messages typed while agent is running
```

Hermes maintains **two separate queues**:

- `_pending_input` — messages typed in the *foreground* prompt (the user wasn't waiting for the agent).
- `_interrupt_queue` — messages typed while the agent was already running.

Behavior (per `cli.py:12069`):

> "- Agent running: goes to _interrupt_queue (chat() monitors this)"

The chat loop polls `_interrupt_queue` with a short timeout (`get(timeout=0.1)`) while the agent is producing its current turn. If a message appears, the loop:

- treats it as an interrupt-signal (stop current turn, deliver this new message as the next user turn), OR
- treats it as a queued-for-next-turn message (don't stop current turn, but deliver it after this one finishes).

The `busy_input_mode` config (line 362, 2658-2667) toggles between these:

```python
"busy_input_mode": "interrupt",  # or "queue"
```

`interrupt` (default): Enter while-the-agent-is-running stops the agent and runs the new message. Like Cmd-Enter on a chat app where you wanted to take back what the model is saying.

`queue`: Enter while-the-agent-is-running adds the message to a stack, runs the new message *after* the current turn finishes. Like sending a follow-up before the bot finishes typing.

This is the right UX choice to make explicit. Different users want different behaviors. The config switch costs nothing and serves both camps.

## Interrupt-Without-Loss

`cli.py:11265+` (around interrupt handling):

```python
# _interrupt_queue is separate from _pending_input, so process_loop
# typed while the agent is running go to _interrupt_queue; messages typed while
if hasattr(self, '_interrupt_queue'):
    interrupt_msg = self._interrupt_queue.get(timeout=0.1)
```

When Ctrl-C is hit and the agent interrupts itself, the input buffer at the prompt is **NOT** cleared. The user's typed-but-unsent text stays visible. They can continue editing it after the interrupt is processed.

This is implemented by `prompt_toolkit`'s `patch_stdout()` (imported line 57). The agent's output writes go through the patch so they don't clobber the input area. When the agent is interrupted, the prompt area is redrawn from its preserved state.

The SIGINT absorption at `cli.py:14023`:

```python
_signal.signal(_signal.SIGINT, _sigint_absorb)
```

Hermes registers a custom SIGINT handler at TUI startup so the *raw* signal doesn't propagate to the agent thread. The interrupt becomes a TUI event, not a kernel signal. This is how the agent can be "interrupted" without `KeyboardInterrupt` being raised from arbitrary frames (which would crash mid-write of a tool result).

## Multiline Editing

The Shift-Enter / Ctrl-J trick is at `cli.py:12260-12265`:

```python
"""
without requiring terminal settings changes. Ctrl+J (the raw
LF keystroke) also triggers this by virtue of being the same
key code — a harmless side effect since Ctrl+J has no
conflicting Hermes binding. See issue #22379.
"""
event.current_buffer.insert_text('\n')
```

`Shift+Enter` on most terminals sends LF (Ctrl+J). Hermes binds Ctrl+J to "insert newline." Enter (CR, Ctrl+M) is bound to "submit." The result: the user can compose multiline text without escapes, without flags, without a separate command. This works on Linux, macOS, and Windows Terminal alike.

The VSCode/Cursor edge case is handled at `cli.py:12267-12270`:

> "VSCode/Cursor bind Ctrl+G to "Find Next" at the editor level, so the keystroke never reaches the embedded terminal. Alt+G is unbound in those IDEs and arrives here as ('escape', 'g') — register it as a fallback..."

The user in an embedded terminal gets the same affordances. This is the kind of small detail that earns Hermes users for life.

## External Editor Handoff

`cli.py:12275-12279`:

```python
@kb.add('c-g', filter=_editor_filter)
@kb.add('escape', 'g', filter=_editor_filter)
def handle_open_in_editor(event):
    """Ctrl+G (or Alt+G in VSCode/Cursor) opens the current draft in an external editor."""
    cli_ref._open_external_editor(event.current_buffer)
```

Ctrl-G opens the current input buffer in `$EDITOR` (typically `vim`, `nano`, or `code --wait`). The user composes a long message in their editor of choice, saves, exits — the buffer is replaced with the file contents. This is how long messages get composed without making the terminal scroll forever.

## Slash Completion

`cli.py:12281+`:

```python
@kb.add('tab', eager=True)
def handle_tab(event):
    """Tab: accept completion, auto-suggestion, or start completions.

    Priority:
    1. Completion menu open → accept selected completion
    2. Ghost text suggestion available → accept auto-suggestion
    3. Otherwise → start completion menu
    """
```

Three-state Tab handling. Each state is a different UX affordance:

1. **Menu open**: Tab accepts the highlighted item.
2. **Ghost suggestion**: Tab accepts the ghost text (`prompt_toolkit`'s `AutoSuggest` shows greyed-out text predicting what you might type next; Tab makes it real).
3. **No menu**: Tab starts the completion menu (equivalent to typing the first character of a slash command).

The slash menu populates from THREE sources, in this order:

- Built-in commands (`/help`, `/exit`, `/title`, `/resume`, `/usage`, etc.).
- Skill commands (via `agent/skill_commands.py:329` `get_skill_commands()`).
- Bundle commands (via `agent/skill_bundles.py:195` `get_skill_bundles()`).

Bundle wins on a slug collision (per [[30_execution/30_SELF_HEALING_LOOP]]).

The completion uses a `FuzzyCompleter` (`hermes_cli/completion.py`). User types `/back` and matches `/backend-dev` (skill), `/back-out` (bundle), `/backup` (built-in command). Fuzzy ranking puts the best match at the top.

## File-Drop Support

A bonus: `cli.py:13835` shows file-drop handling. The user drags a file into the terminal, the path is pasted; Hermes detects "this looks like a file" and offers to read its contents. The slash-vs-file branch:

```python
if not _file_drop and isinstance(user_input, str) and _looks_like_slash_command(user_input):
    ...
```

A file path can be its own command — "read this file." No explicit `/read` needed. Good UX.

## What This Means for Ember (Munnr)

Ember's CLI is currently simpler than Hermes's. That's a feature, not a deficit. But the patterns above translate cleanly and give Munnr a UX that *feels* like Hermes without the 662KB of code.

### Adopt prompt_toolkit

Already in the dep list per `pyproject.toml`. Confirmed. Munnr already uses it for the chat REPL. Build on what's there.

### Two-queue input model

```python
# src/ember/munnr/chat/queues.py
class InputQueues:
    """Pending-foreground vs interrupt-while-agent-runs."""

    def __init__(self) -> None:
        self.pending: queue.Queue[str] = queue.Queue()
        self.interrupt: queue.Queue[str] = queue.Queue()

    def submit(self, text: str, *, agent_busy: bool, mode: Literal["interrupt", "queue"]) -> None:
        if not agent_busy:
            self.pending.put(text)
            return
        if mode == "interrupt":
            self.interrupt.put(text)  # chat loop sees this, stops agent
        else:  # "queue"
            self.pending.put(text)    # delivered after current turn
```

Configurable mode via `ember.yaml`:

```yaml
chat:
  busy_input_mode: interrupt    # "interrupt" | "queue"
```

Default `interrupt` mirrors Hermes and matches user expectations from web chat apps.

### Multiline binding

```python
# src/ember/munnr/chat/keybindings.py
def build_keybindings(state: ChatState) -> KeyBindings:
    kb = KeyBindings()

    @kb.add('c-j')
    def insert_newline(event):
        """Shift-Enter / Ctrl-J inserts newline."""
        event.current_buffer.insert_text('\n')

    @kb.add('enter')
    def submit(event):
        """Enter submits the buffer."""
        ...
```

This is 10 lines. Steal verbatim.

### SIGINT absorption

Per [[docs/CROSS_PLATFORM_PLAN.md]], Ember currently catches `KeyboardInterrupt` at three sites (chat REPL, stream loop, Strengr retry sleep). Adding `signal.signal(SIGINT, ...)` would *contradict* the existing pattern of catching `KeyboardInterrupt` naturally.

Reconciliation: don't install a SIGINT handler at startup. Continue catching `KeyboardInterrupt` at the chat REPL boundary. The interrupt-without-loss UX is achieved via `patch_stdout()` (which Munnr already uses) preserving the input area across writes. When `KeyboardInterrupt` arrives:

- the agent thread is sent a cancellation event via `asyncio.CancelledError` or a `threading.Event`
- the chat REPL catches the interrupt
- prompt_toolkit's `app.invalidate()` redraws
- the buffer remains intact

This is the cross-platform-clean way. POSIX-only `signal.signal()` would break the Vow of Smallness.

### Slash completion

Mirror Hermes's three-source approach (built-in + skills + bundles) but Ember-shaped:

```python
# src/ember/munnr/chat/completion.py
def build_slash_completer() -> Completer:
    """Merge built-in commands, skills, and bundles.

    Priority on collision: bundle > skill > built-in.
    """
    builtin = WordCompleter([
        "/help", "/exit", "/clear", "/title", "/history", "/resume",
        "/well", "/funi", "/strengr", "/curator", "/skills", "/bundles",
    ])
    skills = SkillsCompleter()   # reads ~/.ember/skills/
    bundles = BundlesCompleter() # reads ~/.ember/skill-bundles/
    return FuzzyCompleter(merge_completers([bundles, skills, builtin]))
```

Fuzzy ranking gets the user `/well` and `/well-vacuum` and `/wellness-check-bundle` all from typing `we`. The ranking algorithm is `prompt_toolkit`'s default — proven, no tuning needed.

### External editor handoff

Ctrl-G binding. 30 lines. Adopts `$EDITOR` if set, falls back to `vi` on POSIX and `notepad` on Windows. The cross-platform fallback:

```python
def _editor_command() -> list[str]:
    editor = os.environ.get("VISUAL") or os.environ.get("EDITOR")
    if editor:
        return shlex.split(editor)
    if sys.platform == "win32":
        return ["notepad"]
    return ["vi"]
```

### File-drop heuristic

Same as Hermes. After the user pastes text, check if it looks like a file path:

```python
def _looks_like_file_drop(text: str) -> Path | None:
    candidate = Path(text.strip().strip("'\"")).expanduser()
    if candidate.is_file():
        return candidate
    return None
```

If yes, offer: "Read this file? [Y/n]". On yes, replace the buffer with the file's contents wrapped in a markdown code fence with the path as the language hint.

### What Ember should NOT adopt

- **A 662KB single-file CLI.** Ember's CLI lives in modules under `src/ember/munnr/chat/`. Each pattern is its own file. Code review stays sane.
- **Gateway integration.** No multi-platform bridge. Munnr is local-only in v1.
- **Computer-use integration.** Out of scope.
- **A heavyweight TUI like Textual.** prompt_toolkit's basic Application is plenty.

### Vow check

- **Vow of Smallness** — strengthened. Munnr's CLI stays small by not adopting Hermes's gateway features.
- **Vow of Public-Friendliness** — strengthened. Slash completion, file-drop, Ctrl-G editor handoff are non-developer affordances.
- **Vow of Flexible Roots** — preserved. All paths via `Path.home() / ".ember"`.
- **Vow of Graceful Offline** — preserved. The chat REPL has zero network dependencies.
- **Vow of Modular Authorship** — strengthened. Each TUI feature is a sibling module; a broken keybinding doesn't crash chat.

### Concrete deliverables

1. `src/ember/munnr/chat/queues.py` — two-queue input model.
2. `src/ember/munnr/chat/keybindings.py` — Ctrl-J multiline + Ctrl-G editor + Tab completion.
3. `src/ember/munnr/chat/completion.py` — three-source FuzzyCompleter.
4. `src/ember/munnr/chat/file_drop.py` — file-path heuristic.

Each is < 200 lines. Total Munnr TUI surface stays under 1,500 LoC.

### Where to read next

- [[30_execution/31_CROSS_PLATFORM_TACTICS]] — why prompt_toolkit over readline.
- [[30_execution/34_PROCEDURAL_SKILL_CRAFTING]] — what the skill completer pulls from.
- [[50_verification/52_ANTIPATTERN_CATALOG]] — why we don't ship a 662KB cli.py.
- [[60_synthesis/63_INTEGRATION_PATHS]] — sequenced PRs.

A good TUI does not announce itself. It feels like nothing — until you try a worse one. — Eldra.
