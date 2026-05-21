# 86 — Screen: Tool Approval

The modal where the operator approves or denies a tool call.

---

## Purpose

When Funi proposes a tool call, the operator decides whether to
allow it — clearly, with full information, refusable. Vow of
Sovereignty in interface form.

---

## Layout

Modal centered on top of ChatScreen. Other screen content is dimmed
but visible (per the design philosophy: modal-but-visible).

```
                    ╭──── ᛟ ── Approve tool call? ──────╮
                    │                                     │
                    │   Ember wants to use:                │
                    │   fetch_url                          │
                    │                                     │
                    │   Arguments:                         │
                    │     url:                             │
                    │       https://en.wikipedia.org       │
                    │       /wiki/Odin                     │
                    │                                     │
                    │   This tool will:                    │
                    │   - GET the URL                      │
                    │   - Return up to 1 MiB of response   │
                    │   - Refuse private IPs               │
                    │   - Honor robots.txt                 │
                    │                                     │
                    │   y = approve once                   │
                    │   a = approve + remember session     │
                    │   n = deny                           │
                    │                                     │
                    │   (Refur watches from the corner)    │
                    ╰─────────────────────────────────────╯
```

---

## Implementation

`src/ember/stofa/screens/tool_approval.py` —
`ToolApprovalScreen(textual.screen.ModalScreen)`.

Pushed by ChatScreen when `ToolCallProposed` fires. Returns the
operator's answer (y/a/n) when popped.

```python
class ToolApprovalScreen(ModalScreen):
    BINDINGS = [
        Binding("y", "approve_once", "approve once"),
        Binding("a", "approve_session", "approve + session"),
        Binding("n", "deny", "deny"),
        Binding("escape", "deny", "(esc = deny)"),
    ]

    def __init__(self, call: ToolCall, descriptor: ToolDescriptor):
        super().__init__()
        self.call = call
        self.descriptor = descriptor

    def action_approve_once(self) -> None:
        self.dismiss("y")

    def action_approve_session(self) -> None:
        self.dismiss("a")

    def action_deny(self) -> None:
        self.dismiss("n")
```

---

## What gets displayed

For each tool call:

- **Tool name** — bold, $accent.
- **Arguments** — each key + value. Long values wrapped + indented.
- **Redacted args** show as `<redacted>` per `descriptor.redacted_arg_names`.
- **Tool description** — from the descriptor (V2 may include a
  "what this tool can do" preview based on a fuller schema).
- **Three options** — y / a / n, with bindings shown clearly.

For MCP-bridged tools, the display includes the MCP server's name:

```
Tool: mcp__filesystem__read_file
Arguments:
  path: /home/volmarr/notes/odin.md
```

Operator sees "this came from the filesystem MCP server" + the
actual call.

---

## Why three options (not just yes/no)

Vow-of-Sovereignty-aware. Three states reflect three operator
intentions:

- **y** (approve once) — "yes this time, ask me again next."
- **a** (approve + remember) — "yes this time + for the rest of
  this session for this tool."
- **n** (deny) — "no."

The middle option `a` (session-approve) builds operator-level
trust over the session without committing to permanent trust (no
"always approve" config setting from the modal — that requires
Settings).

---

## Esc semantics

`Esc` is bound to `deny`. The reasoning:

- The modal is asking permission. The safe default is "no."
- Operators conditioned to "Esc = cancel" find the right behavior.
- An operator who Esc-out-of-thinking effectively says "I don't
  want to engage with this approval right now" — which is best
  served by denying (Funi gets a refusal back; chat continues
  ungrounded).

---

## Visual emphasis

- **The modal border is $accent**, drawing the eye.
- **The tool name is bold + $accent.**
- **The three options are each on their own line**, key in
  $accent.
- **The dimmed-content under** is at 30% opacity (Textual `dim`
  rendering) — visible enough to remind the operator they were
  in a chat, faded enough not to compete.

---

## Pet behavior during approval

- **Refur** appears at the bottom of the chat panel (visible
  underneath the modal).
- **Funi-spark** stops pulsing — Funi is waiting on the operator
  now, not thinking.
- Other pets: no change.

---

## Approval timeout (V2)

V1: no timeout. The modal stays until the operator answers.

V2 considered: a "this approval expires in 30s, defaulting to deny"
countdown. Trade-off: timeouts can pressure the operator. Decision:
ship V1 without timeouts; revisit if real operators ask for it.

---

## What ToolApprovalScreen does NOT do

- **Show the full tool execution preview.** Just shows the call
  proposal; the execution happens after approval, in the chat.
- **Bypass-able from config.** The closest is `tools.standing_trust:
  true` which sets every PER_CALL tool to AUTO_APPROVED — but that
  affects every tool, and is configured in Settings/CLI, not from
  the modal.
- **Edit the proposed call.** Operator either accepts what Funi
  proposed or declines.

---

## Closing

ToolApprovalScreen is the **sovereignty moment** of Stofa. Tools
don't fire without the operator's explicit consent (or their
standing-trust setting). The modal makes the consent clear,
informed, and refusable. Refur watches from the corner — present
but not pushing. Three options, escapable, audit-logged.
