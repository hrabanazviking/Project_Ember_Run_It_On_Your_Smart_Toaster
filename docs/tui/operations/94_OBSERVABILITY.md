# 94 — Observability

How operators (and developers) can see what Stofa is doing,
debug issues, and understand performance.

---

## Three observability surfaces

1. **The StatusBar.** Always visible. Realm states + recent
   activity. The operator's primary "is it alive" view.
2. **The Doctor screen.** Detailed per-realm health. The operator's
   "what's wrong" view.
3. **The debug overlay.** A V2 surface (toggled with a config flag)
   showing per-frame timing, pet ticks, message bus traffic. The
   developer's view.

---

## StatusBar content

```
[ ● Funi llama3.2:3b · ● Well 95 docs · ● MCP 2/2 · ⏱ 12s ]    [Chat]    [c/w/d/s/m · ? · q]
```

- **Realm states**: color-coded dots + label + brief detail.
- **Last activity**: small timer showing seconds-since-last-event
  (helps operator know if Stofa is responsive).
- **Current screen**: bold center.
- **Key hints**: contextual.

Updates throttled to 5 Hz max to keep SSH-friendly.

---

## The Doctor screen

Per [`../screens/83_SCREEN_DOCTOR.md`](../screens/83_SCREEN_DOCTOR.md):
all four realms, per-realm detail + raw response view.

The Doctor is what the operator uses when:
- "Why is chat slow?" → Doctor → Funi → tokens/s metric.
- "Did my ingest actually finish?" → Doctor → Brunnr → chunk count.
- "Why isn't this MCP tool firing?" → Doctor → MCP → server status
  → restart.

---

## Logging

Per [`90_PERFORMANCE_BUDGETS.md`](90_PERFORMANCE_BUDGETS.md), Stofa
honors `ember.logging.configure_from(config.logging)` (the Batch J
work).

Operators can:
- Set `logging.level: DEBUG` in `ember.yaml` for verbose output.
- Set `logging.format: structured` for JSON-per-line.
- Add `logging.destinations` with file paths + rotation.

This is the same logging Ember-the-agent uses; Stofa just emits its
own messages into that pipeline.

Typical Stofa log lines (at INFO):
```
ember.stofa.app | App ready in 421ms
ember.stofa.services.funi | FuniRequestStarted (model=llama3.2:3b)
ember.stofa.services.funi | FuniRequestFinished (tokens=247, ms=4280)
ember.stofa.pets.hugin | flew to citations panel
```

At DEBUG: per-message routing on the event bus.

---

## Audit log

The existing Ember audit log captures every tool call. Stofa
doesn't add to it; it just makes it visible (V2 screen
EpisodeBrowserScreen + AuditLogScreen).

In V1, operators read the audit log file directly:
- Path: `~/.ember/state/tool_audit/<date>.jsonl`
- Format: one JSON object per tool call.
- Inspected with `jq` or similar.

---

## Per-screen metrics (V2)

V2 adds a debug overlay (toggled with `Ctrl-Shift-D` or
`stofa.debug_overlay: true`):

```
┌─ Stofa Debug ────────────────────────────────────────╮
│                                                       │
│ Frame: 2347   FPS: 4.2 (animation budget: 4)         │
│ Last frame ms: 8.3                                    │
│ Memory RSS: 62 MB                                     │
│                                                       │
│ Active services:                                      │
│   FuniService     (idle)                              │
│   WellService     (idle)                              │
│   MCPService      (idle)                              │
│   DoctorService   (probing in 23s)                    │
│   AuditService    (idle)                              │
│                                                       │
│ Active pets (4):                                      │
│   ember-ember     (static)                            │
│   funi-spark      (idle)                              │
│   hugin           (idle)                              │
│   geri-cub        (sleeping)                          │
│                                                       │
│ Message bus traffic (last 60s):                       │
│   FuniTokenStreamed:    127                           │
│   IngestProgress:        45                           │
│   DoctorProbed:           2                           │
│                                                       │
│ Press Ctrl-Shift-D to close                           │
╰───────────────────────────────────────────────────────╯
```

The overlay is a developer/debugging surface, not for routine
operator use.

---

## Crash reporting

If Stofa crashes:

1. A crash file is written to `~/.ember/state/stofa_crashes/<timestamp>.txt`
   with the traceback + last 100 log lines.
2. On next launch, Stofa offers: "There was a crash last session.
   Would you like to view the report? (y/n)"
3. If y: shows the crash file in a modal.
4. The crash file is *not* auto-sent anywhere. Operator can include
   it in a bug report.

V2 may add a "send to maintainer" button (opt-in) that opens a
mailto link with the report pre-filled.

---

## Performance instrumentation

Beyond CI budgets, runtime instrumentation:

- Each service tracks its last N operations' duration. Exposed in
  Doctor via "last 60s avg latency."
- Pets log their tick count (debug-level).
- Render frame times tracked by Textual; exposed via debug
  overlay.

These don't surface to operators normally. They're for diagnosing
"my Stofa feels slow" complaints.

---

## What we don't observe

- **Operator behavior tracking.** No "you used the chat screen X
  times this session" telemetry.
- **External phone-home.** Stofa is sovereign; nothing leaves the
  machine without operator action.
- **Anonymized analytics.** None. Per Vow of Sovereignty.
- **Crash reports auto-sent.** Operator chooses.

---

## Closing

Observability in Stofa is **operator-facing first**, **developer-
facing optional**. StatusBar + Doctor give the operator everything
needed to understand what Stofa is doing. The debug overlay gives
the developer everything needed to fix it. Logging is structured.
Crash reports are operator-controlled.

Nothing about Stofa is hidden from the operator who wants to look,
and nothing is exposed to anyone else without their action.
