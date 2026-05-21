# 12 — State Machine

Stofa is a state machine at heart. This document names the states,
the transitions, and the invariants each state must preserve.

---

## Top-level app states

```
                            ┌──────────────────┐
                            │   CONSTRUCTING   │
                            │ (config loading, │
                            │  identity probe) │
                            └─────────┬────────┘
                                      │
                          ┌───────────┴──────────────┐
                          │                          │
                          ▼                          ▼
            ┌──────────────────────────┐  ┌───────────────────┐
            │  HJARTA (first-run)      │  │  READY            │
            │  identity not set yet    │  │  identity loaded  │
            └────────────┬─────────────┘  └────────┬──────────┘
                         │                         │
                         └────────────┬────────────┘
                                      ▼
                            ┌──────────────────┐
                            │      OPEN        │  ◀──── normal operation
                            │  (screens live)  │
                            └─────────┬────────┘
                                      │
                                  q / Ctrl-C
                                      ▼
                            ┌──────────────────┐
                            │    CLOSING       │
                            │  (close handles, │
                            │   restore TTY)   │
                            └─────────┬────────┘
                                      ▼
                                   exited
```

Five states. Transitions are explicit, observable, audit-able. No
"limbo" states.

### CONSTRUCTING

- Loads `ember.yaml` via `load_ember_config`.
- Configures logging via `ember.logging.configure_from`.
- Opens Funi (best-effort — `Unavailable` is allowed).
- Opens Brunnr (best-effort — `Disconnected` is allowed).
- Opens MCP pool if configured (best-effort).
- Probes for `has_identity(config_root)`.

**Invariants:** zero visible UI yet; no event loop running for input;
errors caught and recorded for the splash-error screen if they're
fatal.

**Exits to:** HJARTA (if no identity) or READY (if identity loaded).

### HJARTA

- Visible UI is the wizard screen only.
- Operator answers three questions.
- On completion, writes `ember.yaml` and identity file.
- Returns to CONSTRUCTING to re-load with new config.

**Invariants:** no other screens visible; navigation locked; only `q`
(quit before completing) and the wizard's own keys work.

**Exits to:** CONSTRUCTING (with new config).

### READY

A momentary state between CONSTRUCTING and OPEN. Used for:
- Splash render (the hall opens; the hearth lights).
- Service-startup messages animate in (panels populate as their data
  arrives).
- Pet layer initializes.

Lasts at most ~500ms. The operator may see it as a brief vignette
("Stofa opening…") if their handle-opens were slow, otherwise it's
invisible.

**Invariants:** input is suppressed for the splash's duration;
splash can't last more than a hard cap (1500ms).

**Exits to:** OPEN.

### OPEN

The normal operating state. Multiple screens are stack-able (Home is
always at the bottom; a screen like Settings push-pops on top of
it). The chat keeps its state regardless of which screen is focused.

**Invariants:**
- The status bar reflects current truth.
- All five services (Funi/Well/MCP/Doctor/Audit) are running.
- The pet layer is subscribed.
- Resize events propagate immediately.

**Exits to:** CLOSING (on `q`, Ctrl-C, EOF, fatal error).

### CLOSING

- Closes Funi handle.
- Closes Brunnr handle.
- Closes MCP pool.
- Flushes audit log.
- Restores terminal (cursor visibility, alt-screen exit).
- Prints one farewell line to stdout: `Stofa closed. {N} episodes
  persisted.`

**Invariants:** no UI repaints; close failures are logged but never
prevent exit (`contextlib.suppress(Exception)` on each close —
matching the pattern from `chat.py`'s REPL cleanup).

**Exits to:** process exit (0 normally; 1 on fatal-startup-error path).

---

## Per-screen state machines

Each screen has its own sub-state-machine. Documented briefly here;
detail in [`screens/`](../screens/).

### Chat screen states

```
   IDLE  ──(operator types + Enter)──▶  AWAITING_FUNI
     ▲                                       │
     │                                       │  (stream begins)
     │                                       ▼
     │                                   STREAMING
     │                                       │
     │   (Funi returns; no tool calls)       │
     ├───────────────────────────────────────┤
     │                                       │
     │                                       │  (tool_calls in chunk)
     │                                       ▼
     │                                  AWAITING_APPROVAL
     │                                       │
     │                              (operator approves)
     │                                       │
     │                                       ▼
     │                                  EXECUTING_TOOL
     │                                       │
     │                            (tool reply ready)
     │                                       │
     │                                       ▼
     │                              AWAITING_FUNI (follow-up)
```

States: IDLE, AWAITING_FUNI, STREAMING, AWAITING_APPROVAL,
EXECUTING_TOOL.

### Well screen states

```
   VIEWING ──(operator presses "i" to ingest)──▶  CHOOSING_PATH
     ▲                                                  │
     │                                                  │
     │                                                  ▼
     │                                              INGESTING
     │                                                  │
     └──────────────────────────────────────────────────┘
                  (ingest completes / cancels)
```

### Hjarta screen states

```
   NAME_EMBER  ──▶  PICK_FUNI  ──▶  PICK_WELL  ──▶  ADVANCED_TOOLS  ──▶  WRITE_IDENTITY
```

(Mirrors the existing Hjarta FSM; Stofa is a visual reskin, same
states.)

---

## State sources of truth

For each piece of state, exactly one component owns it. Other
components read via `app.query_one()` or via reactive subscriptions.

| State | Owner |
|---|---|
| Current app state (CONSTRUCTING / OPEN / ...) | `StofaApp` |
| Active screen | `app.screen_stack` (Textual) |
| Chat scroll position | `ChatScreen` |
| Conversation history | `ChatScreen` (in-memory `episodes` list) |
| Well counts | `WellService.stats` (reactive) |
| Funi health | `FuniService.health` (reactive) |
| MCP server states | `MCPService.servers` (reactive) |
| Audit log offsets | `AuditService.tail_position` |
| Pet positions | `PetLayer` per-pet widget |
| Theme | `StofaApp.theme` (reactive) |
| Pets enabled | `StofaApp.pets_enabled` (reactive) |

When a value changes, the reactive system fires a Message, every
subscriber updates. No polling.

---

## Reactive vs imperative — when which

**Reactive** (Textual `reactive[]` attributes):
- State that multiple widgets need to see (Funi health, theme,
  pets-enabled).
- State that the operator changes via UI (theme switch, pet toggle).
- State that animations depend on (the hearth pulse).

**Imperative** (direct method calls):
- One-shot actions ("submit this prompt to Funi").
- Tool approval responses (the modal returns the answer directly).
- Service startup / shutdown.

Reactives are cheap but not free. We use them where they earn their
keep (cross-widget state). Local state stays local.

---

## Invariants enforced regardless of state

These hold in every state, every transition:

1. **The status bar can render.** If a service is down, the bar
   shows "(down)"; it never crashes.
2. **The hearth icon renders.** It is part of the chrome. Even
   during CONSTRUCTING errors, the hearth is drawn unlit.
3. **`Ctrl-C` exits cleanly.** From any state. CONSTRUCTING aborts;
   READY/OPEN go to CLOSING; CLOSING continues to exit.
4. **Operator data is never lost.** The chat conversation is
   persisted as Episodes on every turn. Quitting mid-stream tags
   the partial Episode `interrupted=True` but persists it.

---

## State transitions worth detailing

### Funi disconnect during chat

```
STREAMING --(URLError mid-stream)--> EXPECTED:
  - Episode persisted with finish_reason=ERROR
  - Banner appears: "Funi disconnected. Reply incomplete."
  - Returns to IDLE
  - Status bar reflects funi_disconnected=True
  - Funi-spark pet pulses to "thinking" briefly, then dims
```

### Brunnr disconnect mid-session

```
At any time --(BrunnrError on retrieve)--> EXPECTED:
  - Banner appears: "Well disconnected. Continuing ungrounded."
  - Subsequent chat turns skip retrieval (well_disconnected=True
    flag in prompt assembly)
  - Status bar reflects brunnr_disconnected=True
  - Hugin (raven) flies to its idle perch (off the citations panel)
```

### Resize while in chat

```
Any size --(SIGWINCH)--> EXPECTED:
  - Textual handles the resize internally (compositor.refresh)
  - Chat panel reflows the in-progress streaming text
  - The pets re-position relative to the new sizes
  - The hearth icon stays in its anchored position
  - No data loss, no flicker beyond one frame
```

### Theme switch mid-session

```
OPEN --(operator: ":theme midgard")--> EXPECTED:
  - StofaApp.theme = "midgard" (reactive)
  - All widgets re-render with the new CSS variables
  - Pet sprites reload their per-theme color choices
  - Conversation buffer keeps content; only colors change
  - No flicker (Textual's diff render handles this)
```

---

## Closing

Five top-level app states. Per-screen sub-states documented in their
respective screen docs. Reactive where multiple widgets need to see;
imperative where they don't. Every transition has a Message; every
Message has at most one owner; every owner has invariants documented.

This is what robustness looks like at the architecture level — not
"don't crash" but "every state is named and every transition has a
contract."
