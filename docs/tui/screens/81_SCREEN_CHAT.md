# 81 — Screen: Chat

The conversation surface. Where operators spend most of their time.

---

## Purpose

Carry on a chat conversation with Ember, including:
- Streaming reply with live tokens.
- Retrieval citations.
- Tool-approval modals.
- Episode persistence per turn.

---

## Layout

```
┌── Stofa ──── ᛞ ᛞ ᛞ ──── Chat ─────────────────────── 🔥 ─┐
│                                                            │
│  ┌──── Conversation ────────────────────────────────────┐  │
│  │                                                       │  │
│  │  > volmarr: hello                                    │  │
│  │                                                       │  │
│  │  ember: hi! how can I help today?                    │  │
│  │                                                       │  │
│  │  > volmarr: what do my notes say about Odin?         │  │
│  │                                                       │  │
│  │  ember: I found these in your Well:                  │  │
│  │                                                       │  │
│  │     • odin.md — "the all-father has two ravens..."   │  │
│  │     • yggdrasil.md — "the world tree, an ash..."     │  │
│  │                                                       │  │
│  │     Odin is the principal Norse god, often known as  │  │
│  │     the all-father. He has two ravens, Huginn and    │  │
│  │     Muninn, who fly across the nine worlds each day  │  │
│  │     and report back to him each night...             │  │
│  │                                                       │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                            │
│  > _                                              [↩ send] │
│                                                            │
└────────────────────────────────────────────────────────────┘
[ ● Funi llama3.2:3b · ● Well 95 docs ]   [Chat]   [↑ recall · ? · q]
```

When Hugin perches: top-right of the citations area.

When ToolApprovalScreen is up (modal):

```
┌── Stofa ──── ᛞ ᛞ ᛞ ──── Chat ─────────────────────── 🔥 ─┐
│                                                            │
│  (conversation continues underneath)                       │
│                                                            │
│       ╭──── ᛟ ── Approve tool call? ──────╮               │
│       │                                    │               │
│       │   Ember wants to use:               │               │
│       │   fetch_url                         │               │
│       │                                    │               │
│       │   Arguments:                        │               │
│       │     url: https://en.wikipedia.org   │               │
│       │           /wiki/Odin                │               │
│       │                                    │               │
│       │   y = approve once                  │               │
│       │   a = approve + remember session    │               │
│       │   n = deny                          │               │
│       │                                    │               │
│       ╰────────────────────────────────────╯               │
│                                                            │
│                       [Refur watches here]                 │
└────────────────────────────────────────────────────────────┘
```

---

## Implementation

`src/ember/stofa/screens/chat.py` — `ChatScreen(textual.screen.Screen)`.

The screen composes:
- `MessagesView` (scrollable list of message widgets).
- `InputBar` (the prompt area).

It owns:
- `episodes: list[Episode]` — in-session memory.
- `current_stream: StreamingTurn | None` — the in-flight reply.
- `tool_approval_pending: ToolCall | None` — when present, push
  ToolApprovalScreen.

---

## Per-turn flow

```
1. Operator types in InputBar, presses Enter.
2. InputBar fires SubmitMessage.
3. ChatScreen:
   a. Appends operator message to MessagesView.
   b. Calls WellService.retrieve(query) → hits.
   c. Builds prompt context (identity + recent episodes + hits + msg).
   d. Calls FuniService.stream(prompt, tools=available_tools).
4. FuniService yields tokens; ChatScreen appends to current message.
5. If tool_calls arrive:
   a. ChatScreen pushes ToolApprovalScreen with the call.
   b. Operator answers; modal pops.
   c. ChatScreen executes the tool, gets ToolReply.
   d. Appends reply context, re-asks Funi for follow-up.
6. When Funi finishes (no more tool_calls):
   a. ChatScreen persists Episode via WellService.add_episode.
   b. Returns to IDLE.
```

---

## Keybindings (chat-specific)

| Key | Action |
|---|---|
| `Enter` (when input focused) | Submit message |
| `Shift+Enter` | New line in input |
| `↑` (when input empty) | Recall last operator message |
| `Ctrl-U` | Clear current input |
| `Ctrl-C` (during stream) | Interrupt stream; tag Episode interrupted |
| `Ctrl-C` (idle) | Quit Stofa |
| `Ctrl-A` | Open audit log (V2) |
| `Enter` (on citation focus) | Expand inline |
| `Esc` | Back to Home |

---

## Streaming UX

Tokens stream into the bottom-most Ember message bubble. Visual
treatment:

- New tokens appear with no animation; just text.
- The hearth icon pulses while streaming.
- The cursor (if input bar focused) doesn't blink during streaming
  to avoid distraction.

When stream completes:
- Hearth stops pulsing.
- Input bar regains its blinking cursor.
- New empty Ember-message-area is NOT created — the operator's
  next message creates it.

If stream is interrupted (Ctrl-C):
- Partial text gets `[interrupted by operator]` appended.
- Episode persists with `finish_reason=INTERRUPTED`.
- Input bar regains cursor.

---

## Tool approval modal

`ToolApprovalScreen` (separate file but described here for context):

- Pushed as a modal Screen on top of ChatScreen.
- Operator answers y/a/n.
- Returns the answer to ChatScreen.
- Pops.

The modal shows:
- Tool name (with mcp__ prefix if it's an MCP tool).
- Each argument key + value (redacted args show `<redacted>`).
- The three options with their keybindings.

---

## Citation expansion

In an Ember reply, citations appear as compact bullets. Pressing
Enter on one expands it inline:

```
  • odin.md — "the all-father has..."          ← collapsed
         ↓ Enter to expand
  ▼ odin.md — "the all-father has..."
     Full excerpt:
       Odin (Old Norse: Óðinn) is the principal god of the
       Norse pantheon, often known as the all-father. He has
       two ravens, Huginn and Muninn...
     Press Esc to collapse.
```

Esc collapses. The operator can expand multiple citations.

---

## Pet behavior on Chat

- **Funi-spark** pulses during streaming.
- **Hugin** perches over citations when present.
- **Refur** appears at the bottom-edge during approval modals.
- **Heiðr** drops a horn after tool calls complete.
- **Sumarbýfa** doesn't appear (it's an ingest pet; not relevant
  here unless ingest runs in background).
- **Geri-cub** sleeps in the corner.
- **Ask-sapling** grows in a corner over conversation length.

---

## Empty state

When the operator opens Chat for the first time:

```
┌──── Conversation ────────────────────────────────────┐
│                                                       │
│         Hi. I'm Ember.                                │
│         Type below to say hi back.                    │
│         Press ? at any time for help.                 │
│                                                       │
└───────────────────────────────────────────────────────┘
```

Friendly. One line of identity, one line of action prompt, one line
of help discovery.

---

## What ChatScreen does NOT do

- **Edit messages.** No in-place edit; operator types a new one.
- **Branch conversations.** Linear. (V2 maybe: branched chats.)
- **Show the full system prompt.** Audit log surface, not chat.
- **Track token usage in-line.** Debug overlay only.

---

## Closing

ChatScreen is the heart of Stofa. Most operators spend > 80% of
their session here. The streaming feels alive, the citations are
proximate, the tool approval is theater not friction, the pets add
warmth without distraction. Every other screen exists to support
what happens here.
