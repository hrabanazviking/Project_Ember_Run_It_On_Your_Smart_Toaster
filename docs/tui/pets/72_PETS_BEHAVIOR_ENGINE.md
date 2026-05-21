# 72 — Pets Behavior Engine

The technical model: how each pet's behavior is encoded, how
animation budgets are enforced, how events flow.

---

## The PetWidget base class

```python
class PetWidget(Widget):
    """Base for all pet widgets in Stofa.

    Each pet is a Textual Widget that lives in the PetLayer.
    Subclasses declare:
      - NAME: str
      - DEFAULT_ENABLED: bool
      - SUBSCRIBES_TO: tuple[type[Message], ...]
      - DEFAULT_PERCH: str  (named perch key)
      - SPRITE: PetSprite

    The base provides:
      - hidden / idle / active state machine
      - perch transitions
      - sprite frame management
      - animation budget compliance
    """
    NAME: ClassVar[str]
    DEFAULT_ENABLED: ClassVar[bool] = True
    SUBSCRIBES_TO: ClassVar[tuple[type[Message], ...]] = ()
    DEFAULT_PERCH: ClassVar[str] = "default_perch"
    SPRITE: ClassVar[PetSprite]

    state: reactive[Literal["hidden", "idle", "active"]] = reactive("idle")
    current_perch: reactive[str] = reactive("default_perch")
    current_frame: reactive[str] = reactive("idle")
    last_tick_time: reactive[float] = reactive(0.0)

    def set_state(
        self, *, hidden=False, active=False, perch=None, frame=None,
    ) -> None:
        """One method to update state; reactive properties trigger re-render."""
        if hidden:
            self.state = "hidden"
        elif active:
            self.state = "active"
        else:
            self.state = "idle"
        if perch is not None:
            self.current_perch = perch
        if frame is not None:
            self.current_frame = frame
```

Each concrete pet (HuginRaven, RefurFox, etc.) subclasses this and
overrides:

1. The `NAME` / `DEFAULT_ENABLED` / `SUBSCRIBES_TO` / `DEFAULT_PERCH`
   / `SPRITE` class attributes.
2. The message handlers (`on_retrieval_returned`, etc.).
3. Any pet-specific helper methods.

---

## Event flow

```
Service raises Message            App posts to bus            PetLayer receives        Individual pet handles
   │                                  │                            │                          │
   ▼                                  ▼                            ▼                          ▼
FuniService.complete()            Textual App                  PetLayer subscribed       HuginRaven.on_retrieval_returned()
  posts                           propagates                   to RetrievalReturned       changes state + perch
  FuniRequestFinished              messages                     forwards to               PetLayer schedules redraw
                                                               relevant pets               at next budget slot
```

The pets system **subscribes to** the bus; it doesn't poll. Each
pet receives every message it declares interest in.

---

## The PetLayer container

```python
class PetLayer(Widget):
    """The transparent overlay where pets live.

    Manages:
      - Pet registration / deregistration (per operator config).
      - Per-pet positioning via named perches.
      - Animation budget (per-pet + aggregate).
      - The ticker that advances animation frames.
    """

    pets: dict[str, PetWidget]
    perch_resolver: PerchResolver
    aggregate_ticks_this_second: int = 0

    def compose(self):
        # Mount each enabled pet
        for pet in self.pets.values():
            yield pet

    async def _tick_loop(self):
        """Run forever, enforce the animation budget."""
        last_aggregate_reset = time.monotonic()
        while True:
            await asyncio.sleep(0.25)  # check 4 times/sec
            now = time.monotonic()
            if now - last_aggregate_reset >= 1.0:
                self.aggregate_ticks_this_second = 0
                last_aggregate_reset = now

            for pet in self.pets.values():
                if pet.state == "hidden":
                    continue
                if (now - pet.last_tick_time) < 1.0:
                    continue  # per-pet 1Hz cap
                if self.aggregate_ticks_this_second >= 4:
                    continue  # aggregate 4Hz cap

                pet.advance_frame()
                pet.last_tick_time = now
                self.aggregate_ticks_this_second += 1
```

`advance_frame()` is what makes the pet's `current_frame` cycle
through its animation states (idle → active sprite → returning →
idle, or pulse-bright → pulse-dim).

---

## Perch resolution

A pet says "I want to perch at `over_citations`." The PetLayer's
`PerchResolver` translates that to a cell position based on the
current screen geometry.

```python
class PerchResolver:
    def resolve(self, perch_name: str, *, screen: Screen) -> tuple[int, int]:
        """Return (col, row) for the named perch on the current screen."""
        if perch_name == "default_perch":
            return (2, screen.size.height - 2)  # bottom-left
        if perch_name == "above_chat_input":
            return (screen.size.width - 15, screen.size.height - 3)
        if perch_name == "over_citations":
            # Look up the citation panel widget; perch above it
            citation = screen.query_one("#citations_panel", expect_type=Widget)
            if citation:
                return (citation.region.x + 2, citation.region.y - 1)
            return (2, screen.size.height - 2)  # fallback
        # ... etc
```

This indirection means **pets don't need to know about screen
layout**. They name a perch; the resolver figures out where.

When the screen is resized or the underlying panel moves, the
resolver re-resolves and each pet's position updates.

---

## State machine per pet

```
                ┌─────────────┐
                │   HIDDEN     │
                │ (operator    │
                │  disabled,   │
                │ or precondi- │
                │  tion gone)  │
                └──────┬───────┘
                       │
              operator enables /
              precondition met
                       │
                       ▼
                ┌─────────────┐
                │     IDLE     │  ◀── default state for enabled pets
                │ (still at   │
                │  default    │
                │  perch)     │
                └──────┬───────┘
                       │
               event triggers
               this pet
                       │
                       ▼
                ┌─────────────┐
                │   ACTIVE     │
                │ (animated   │
                │  or moved   │
                │  to event   │
                │  perch)     │
                └──────┬───────┘
                       │
              after ~5s OR
              next event
                       │
                       ▼
              back to IDLE
```

Pets never stay in ACTIVE forever. There's always a timeout (default
5 seconds) that returns them to IDLE. If a new event fires during
ACTIVE, the active timer resets and the pet adapts.

---

## Animation frame cycling

Each pet has a few named frames:

```python
class HuginRaven(PetWidget):
    SPRITE = PetSprite({
        "idle": "...",           # standing, head still
        "flying": "...",          # mid-flight, wings out
        "perched": "...",         # perched, watching
        "looking_down": "...",    # head tilted as if reading
    })
```

When ACTIVE, the pet cycles through its event-specific frames at
1 Hz:

```
RetrievalReturned →
  frame "flying" (0s, just received)
  frame "perched" (1s, arrived)
  frame "looking_down" (2s, reading)
  frame "perched" (3s, done reading)
  → back to IDLE at default perch, frame "idle"
```

Some pets have just 1-2 frames; some have 4-5. Always small.

---

## Sprite definition

A `PetSprite` is a small dataclass:

```python
@dataclass(frozen=True, slots=True)
class PetSprite:
    """A pet's set of frames.

    Each frame is a multiline string of Unicode characters. Lines are
    rendered top-to-bottom; characters left-to-right. Single-color
    rendering via the pet's `$pet-<name>` token.

    ASCII variants: each Unicode frame has an ASCII counterpart at
    the same key with "_ascii" suffix.
    """
    frames: Mapping[str, str]

    def get(self, frame: str, ascii_only: bool = False) -> str:
        if ascii_only:
            return self.frames.get(f"{frame}_ascii", self.frames[frame])
        return self.frames[frame]
```

Sprites are stored in `src/ember/stofa/pets/sprites/` as plain text
files, one per pet, with frames separated by `---FRAME:name---`
markers.

---

## Throttling under load

When many events arrive in quick succession (e.g., during a fast
ingest, IngestProgress messages might fire at 50 Hz), the system
prevents pet over-animation:

- Each pet has a *coalesce* method: receiving multiple events of
  the same type within a tick window only triggers one animation.
- Sumarbýfa's `on_ingest_progress` coalesces to "I'm active";
  updates the sprite once per second regardless of how many
  documents progressed.

---

## Disabling a pet

When the operator toggles a pet off (via Settings or `p` key):

```python
def disable_pet(self, name: str) -> None:
    pet = self.pets.get(name)
    if pet:
        pet.set_state(hidden=True)
        # leave it mounted; just don't render
        self.refresh()
```

Disabled pets stay in the widget tree (cheap; not rendering). When
re-enabled, they pop back to idle at the default perch.

---

## Error handling

If a pet's event handler raises (defensively):

- The exception is logged via `logger.warning`.
- The pet returns to IDLE.
- The PetLayer continues; other pets are unaffected.

A buggy pet doesn't crash the hall. Vow of the Unbroken Whole.

---

## Performance characteristics

- **Per pet**: < 50 cells changed per second worst-case (frame swap
  + position move).
- **Aggregate**: < 200 cells changed per second across all pets.
- **CPU per tick**: < 0.1ms in the tight loop.
- **Memory per pet**: < 10 KB (sprite + state).

These are all well under any meaningful budget. Pets are the cheapest
visual elements in Stofa.

---

## Closing

The pet behavior engine is **a tiny state machine wrapped in event
subscription, with strict animation budgets, and named perches for
responsive layout**. ~200 LOC for the base + ~50-100 LOC per pet.
Tractable. Testable. Operator-controllable. The cute is engineered.
