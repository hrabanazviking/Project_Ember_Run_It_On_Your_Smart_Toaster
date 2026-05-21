# 92 — Resize Handling

How Stofa handles terminal resize events. The rules that prevent
visual breakage when operators drag-resize their window or split
tmux panes.

---

## The principle

A resize is **never a glitch**. Every screen reflows correctly.
Content survives (the operator's chat scrollback doesn't get lost).
No layout artifacts (border characters in wrong places).

Tested at every meaningful size.

---

## What Textual does for us

Textual handles SIGWINCH automatically:
1. SIGWINCH arrives.
2. Textual recalculates the terminal size.
3. Triggers `on_resize` on the active screen.
4. The compositor re-renders only the cells that changed.

We don't have to write the resize-detection loop. We write the
**reflow logic** for each screen.

---

## Per-screen reflow rules

### HomeScreen

The 2×2 grid collapses to 1×4 stack when width drops below 80
cells:

```css
HomeScreen {
    grid-size: 2 2;
}

HomeScreen.narrow {
    grid-size: 1 4;
}
```

```python
def on_resize(self, event: Resize) -> None:
    self.set_class(event.size.width < 80, "narrow")
```

### ChatScreen

Vertical layout reflows automatically. The MessagesView resizes; the
input bar stays at 3 rows. No special code needed beyond Textual's
default flex layout.

### WellScreen

Two-pane reflows to single-pane when width < 80:

```python
def on_resize(self, event: Resize) -> None:
    if event.size.width < 80:
        self.set_class(True, "narrow")
    else:
        self.set_class(False, "narrow")
```

CSS:

```css
WellScreen.narrow {
    layout: vertical;
}
WellScreen.narrow > SourcesPanel {
    height: 15;
    width: 1fr;
}
WellScreen.narrow > DetailsPanel {
    height: 1fr;
    width: 1fr;
}
```

### DoctorScreen, SettingsScreen, MCPScreen

Tables and forms reflow column widths automatically. No special code.

### HjartaWizardScreen

Centered vignette. Stays centered at any size. The wizard's content
box has a max-width of 60 cells; smaller terminals shrink to fit.

### HelpOverlay

Centered modal. Width: `min(60 cells, 80% of terminal width)`. Long
descriptions truncate with `…` at very narrow sizes.

### ToolApprovalScreen

Centered modal. Same scaling as HelpOverlay.

---

## Pet layer reflow

Pets are positioned at named perches; the perch resolver re-evaluates
on resize:

```python
def on_resize(self, event: Resize) -> None:
    for pet in self.pets.values():
        if pet.state != "hidden":
            new_pos = self.perch_resolver.resolve(
                pet.current_perch, screen=event.size,
            )
            pet.set_position(new_pos)
```

Pets don't animate during the resize itself; they snap to the new
position in one frame.

---

## What we test

`tests/integration/test_stofa_resize.py`:

```python
@pytest.mark.parametrize("size", [
    (80, 24), (100, 30), (120, 40), (200, 60), (400, 80),
    (80, 80), (40, 30),
])
async def test_home_reflows_at_size(size):
    pilot = await StofaApp().pilot(size=size)
    await pilot.press("h")  # navigate to home
    await pilot.pause()
    # Snapshot: visually correct
    assert_snapshot_matches(pilot.app.screen, f"home_{size[0]}x{size[1]}.svg")
```

The snapshot tests use Textual's `pytest-textual-snapshot` plugin to
render SVG of the current state and diff against committed
golden files.

When a CI change causes a snapshot diff, the developer reviews; if
intended, regenerates; if unintended, fixes the regression.

---

## Edge cases handled

### Sudden very-narrow

If the terminal drops below 40 cells:

```
┌──────────────────────────────────────┐
│                                      │
│  Terminal too narrow.                │
│  Stofa needs at least 40 cells       │
│  of width to render correctly.       │
│                                      │
│  Current: 32×24                       │
│                                      │
└──────────────────────────────────────┘
```

Stofa pauses normal rendering and shows this message. When the
terminal widens past 40, normal rendering resumes.

### Sudden very-short

If height drops below 10:
- StatusBar may overlap chrome header.
- Pets get hidden (no room).
- Single-line "Terminal too short" message can appear.

We do NOT crash; we render something legible.

### Mid-stream resize

If Funi is streaming when a resize happens:
- Tokens already received re-flow into the new width.
- Subsequent tokens append to the new width.
- The Episode persists correctly (text content is wrap-agnostic).

### Modal up during resize

If a modal (ToolApprovalScreen, HelpOverlay) is up during resize:
- The modal re-centers and re-sizes.
- The underlying screen also reflows.
- Operator's pending answer is not lost.

---

## What we don't handle (deferred)

- **Splitscreen reflow during ingest.** Currently the ingest progress
  bar reflows on resize but might look weird mid-bar. Acceptable.
- **Pet animation interrupted by resize.** Pets snap to new positions;
  in-progress animation frames are dropped.

These are real but minor; V2 may polish.

---

## Closing

Resize handling is **automatic for layout, manual for breakpoints,
snapshot-tested in CI**. The operator can drag-resize their window
freely. The chat doesn't lose state. The panels reflow. The pets
re-perch. No glitches, no lost data.
