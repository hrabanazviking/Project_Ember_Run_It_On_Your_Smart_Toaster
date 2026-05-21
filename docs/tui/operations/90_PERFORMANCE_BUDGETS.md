# 90 — Performance Budgets

Hard targets that Stofa V1 commits to. Tested in CI.

---

## Why budgets

Without numeric targets, performance regresses silently. "It feels
slow" is hard to argue; "frame budget exceeded by 12ms" is not.

Budgets also force trade-offs:
- A new pet that ticks too often → exceeds animation budget →
  redesigned.
- A new panel that renders 1000 cells → exceeds startup budget →
  rethought.

---

## The budgets

### Launch time

| From | To | Budget |
|---|---|---|
| `ember tui` shell launch | first interactive frame | < 500 ms |
| First interactive frame | Funi handle open | < 1500 ms |
| Funi open | first chat-ready frame | < 500 ms |

Total cold start to "I can type" on the Pi 5: **< 3 seconds**.

### Frame-level

| Event | Budget |
|---|---|
| Keypress → visual response | < 16 ms |
| Mouse click → visual response | < 16 ms |
| Screen push → fully rendered | < 50 ms |
| Theme swap | < 100 ms |
| Resize → reflowed | < 33 ms |
| Pet animation frame | exactly 1000 ms / tick |

### Streaming

| Event | Budget |
|---|---|
| Funi token arrives → cell painted | < 16 ms |
| Funi tokens/sec render cap | ≥ 60 tok/s (we render as fast as Funi sends, capped by Textual) |
| Interrupt (Ctrl-C) → stream stopped | < 100 ms |

### Memory

| Surface | Budget |
|---|---|
| Empty Stofa | < 50 MB RSS |
| Stofa + 50-turn conversation | < 80 MB RSS |
| Stofa + 1000-turn conversation | < 200 MB RSS |
| Stofa + active ingest | < 500 MB RSS (additional for embedder) |

### CPU

| Mode | Budget |
|---|---|
| Idle (operator not typing) | < 1% CPU on Pi 5 |
| Chat streaming | < 10% CPU on Pi 5 |
| Active ingest | < 50% CPU on Pi 5 (limited by Ollama embeddings) |

---

## How we measure

### Launch time

```python
# tests/integration/test_stofa_launch_budget.py
import time
import subprocess

def test_stofa_launches_in_under_3s():
    t0 = time.monotonic()
    p = subprocess.Popen(["ember", "tui"], ...)
    # Drive input until "ready" prompt visible
    wait_for_ready(p, timeout=3.0)
    elapsed = time.monotonic() - t0
    assert elapsed < 3.0, f"launched in {elapsed:.2f}s"
```

Run on a reference machine in CI (GitHub Actions ubuntu-latest;
roughly Pi-5-class).

### Frame budgets

Textual provides instrumentation hooks; we wrap and assert:

```python
def test_chat_keypress_responds_under_16ms():
    pilot = await ChatScreen.pilot()
    t0 = time.monotonic()
    await pilot.press("h")
    elapsed = time.monotonic() - t0
    assert elapsed < 0.016, f"{elapsed*1000:.1f}ms"
```

### Streaming throughput

```python
async def test_stream_renders_at_funi_pace():
    # Mock Funi that emits 100 tokens at 60 tok/s
    # Verify all 100 are rendered within ~1.7s
    ...
```

### Memory

```python
import resource
def test_idle_memory_under_50mb():
    app = StofaApp(...)
    app.run_in_test_mode()
    rss_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    rss_mb = rss_kb / 1024
    assert rss_mb < 50, f"{rss_mb:.1f} MB"
```

### CPU (manual; flaky in CI)

CPU budgets are *targets* not hard CI-failures. Measured manually
on the Pi 5 during pre-release testing.

---

## When budgets are exceeded

CI failure. Required to fix before merge.

If the operator legitimately needs the new feature that exceeded a
budget:
1. Discuss the budget. Some budgets are firm (launch < 3s); some
   are negotiable.
2. If the budget is negotiated: update this doc + the CI test.
3. Document the trade-off in the DEVLOG.

We don't quietly let budgets drift. Every adjustment is explicit.

---

## What blows budgets that we'll guard against

- **Loading a large model on startup.** We don't; Funi opens
  async-ish.
- **Reading the entire Well on first render.** We don't; Brunnr
  count is one query.
- **Synchronous network calls during render.** We don't; everything
  network-y is in a service with a timeout.
- **Recreating widgets per frame.** Textual's diff render avoids
  this; we don't override it.
- **Pet animation > 4 Hz aggregate.** PetLayer enforces.
- **Long-running synchronous Python in event handlers.** Caught by
  asyncio's debug warnings.

---

## Closing

Numerical budgets are the only honest way to talk about
performance. < 500ms launch. < 16ms keypress. < 100ms theme swap.
< 1Hz per pet. < 50MB idle. These numbers are tested in CI. When
something feels slow, we have a target to hit.
