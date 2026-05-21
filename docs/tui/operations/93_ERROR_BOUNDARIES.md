# 93 — Error Boundaries

How errors are contained per-panel so one failing widget doesn't
crash the hall.

---

## The principle

Per the Vow of the Unbroken Whole: one panel failing doesn't take
down the hall. Each widget / service / pet has an error boundary;
exceptions caught at the boundary, logged, panel shows a graceful
error message, app continues.

---

## Per-widget boundaries

Each widget's `render()` is wrapped:

```python
class SafePanel(Widget):
    def render(self):
        try:
            return self._render_real()
        except Exception as exc:
            logger.warning("panel %s render failed: %s", self.name, exc)
            return RichText(
                f"(panel error: {type(exc).__name__})",
                style="error",
            )
```

A widget that raises during render shows "(panel error: TypeError)"
instead of crashing. Adjacent widgets continue to render normally.

---

## Per-service boundaries

Each service's message-handler is wrapped:

```python
class WellService:
    def handle_message(self, msg):
        try:
            self._handle_real(msg)
        except Exception as exc:
            logger.warning("WellService dropped message: %s", exc)
            # Re-emit a typed failure message so subscribers know
            self.app.post_message(WellServiceFailed(reason=str(exc)))
```

A service that fails to handle one message:
- Logs the failure.
- Posts a typed failure message so widgets can show the operator.
- Continues to handle subsequent messages.

---

## Per-pet boundaries

Pets are passive subscribers; their event handlers are wrapped too:

```python
class PetWidget(Widget):
    async def on_message(self, message):
        try:
            await self._handle_real(message)
        except Exception as exc:
            logger.warning("pet %s handler failed: %s", self.NAME, exc)
            self.set_state(hidden=True)
            # Re-enable on next operator p-toggle
```

A buggy pet hides itself rather than crashing. Operator notices it's
gone, presses `p` to toggle; it re-enables (the bug may recur, but
the hall continues).

---

## Handle-level boundaries

The existing handle layer already wraps backend errors:
- `BrunnrHandle` methods raise `BrunnrError` (typed).
- `FuniHandle` methods return `Unavailable` or `FuniReply`.
- `MCPClientPool` methods return typed results.

Stofa services consume these typed results; we don't add a second
error boundary at the handle layer.

---

## App-level boundary (last resort)

The `StofaApp` has a top-level exception handler:

```python
class StofaApp(App):
    def _on_uncaught_exception(self, exc):
        logger.error("UNCAUGHT in StofaApp: %s", exc, exc_info=True)
        self.notify(
            f"Stofa encountered an error: {type(exc).__name__}: {exc}\n"
            "The hall is still standing. Press q to quit if needed.",
            severity="error",
            timeout=30,
        )
```

Operator sees a notification; app keeps running.

---

## What happens on really catastrophic errors

If the asyncio event loop itself crashes (rare):
- Stofa exits with a Python traceback to stderr.
- The CLI catches and prints a friendly error.
- Operator's audit log + identity are unaffected.

This is the deepest fallback. We don't try to recover from event-loop
death because it's not recoverable.

---

## Crash-safe surfaces

These specific surfaces are guaranteed to render even in error
states:

| Surface | Why |
|---|---|
| ChromeHeader | Doesn't depend on any service |
| StatusBar (basic state) | Reads from cached service.last_known_state |
| HomeScreen panels (empty state) | If a service is down, shows "(unavailable)" |
| Hearth icon | Pure visual; no dependencies |
| Quit (`q`) | Works from any state including catastrophic |

These are the "last-rendered things." Even if the entire chat
state is wrecked, the operator can see the chrome and quit.

---

## Audit log of crashes

If Stofa crashes, the next launch:
1. Reads any leftover crash file in `~/.ember/state/stofa_crashes/`.
2. Offers to send the operator a summary at first launch.
3. Logs the recovery to the audit log.

V2 adds an "automated bug report" surface that bundles the crash
file + system info + Stofa config (sanitized) for the operator to
optionally send.

---

## What we don't do

- **Restart crashed components.** Once a service errors, it's
  marked unhealthy; operator manually restarts via Doctor screen.
- **Hide errors silently.** Every error surfaces somewhere: the
  panel says "(error)" or a notification fires.
- **Continue with stale data.** A service that errored on its last
  refresh marks its data stale; UI shows "(last refresh failed)".

---

## Testing error paths

`tests/integration/test_stofa_error_boundaries.py`:

```python
async def test_widget_crash_doesnt_crash_app():
    app = StofaApp()
    pilot = await app.pilot()
    # Force a render error in HomePanel
    home = pilot.app.query_one(HomeScreen)
    home.realms_panel._raise_on_render = True
    await pilot.pause()
    # App should still be alive
    assert pilot.app.is_running
    # Other panels should still render
    assert home.well_panel.is_rendered
```

Same for service failures, pet failures, etc.

---

## Closing

Error boundaries make Stofa **robust by structure**, not by hope.
Each widget renders or shows "(error)"; each service handles or
re-emits a failure; each pet self-hides; the app top-level catches
everything else. The hall keeps standing. Operators trust that
clicking something experimental won't lose their chat.
