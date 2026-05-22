# 31 — The Protocol Layer

Detailed specification of the new Protocols Yggdrasil adds, and
how existing Ember Protocols are reused.

---

## Existing Protocols (unchanged)

- **`BrunnrHandle`** — memory storage + retrieval (ADR-0010)
- **`FuniHandle`** — LLM runtime
- **`StrengrConfig` retry wrapper** — connection resilience
- **`ToolExecutor`** + **`ToolDescriptor`** — tool framework (ADR-0011)
- **`MCPClientPool`** + **`MCPServerSpec`** — MCP integration (ADR-0014)

Yggdrasil **uses these as-is**. New realms either implement
existing Protocols (Bifrǫst → BrunnrHandle) or new Protocols
documented below.

---

## New Protocol: `SecretResolver`

Used by all realms that need credentials. Replaces (or
generalizes) the current pgvector-only secret-resolution
chain.

```python
class SecretResolver(Protocol):
    """Resolves a named secret to its plaintext value.

    Implementations:
      - EnvVarResolver (existing pattern, generalized)
      - KistaResolver (new, primary)
      - KeyringResolver (existing pattern, fallback)
      - FileResolver (existing pattern, last resort)
      - ChainResolver (composes the above)
    """
    def resolve(self, key: str) -> str | None:
        """Return the plaintext value or None if not found."""
        ...
```

A `ChainResolver` composes them in priority order, matching
the pgvector pattern but extended:

```python
chain = ChainResolver([
    EnvVarResolver(),
    KistaResolver(config.kista),         # Phase 2 addition
    KeyringResolver(),
    FileResolver(config.secret_dir),
])
```

Each realm requests secrets via this chain. Operators control
which resolvers are active via `ember.yaml`.

---

## New Protocol: `EventBus`

Used to publish + subscribe to events.

```python
class EventBus(Protocol):
    """Publish + subscribe to typed events."""
    def publish(self, event_type: str, payload: dict[str, Any]) -> None: ...
    def subscribe(
        self,
        event_pattern: str,
        handler: Callable[[Event], None],
    ) -> SubscriptionHandle: ...
    def unsubscribe(self, handle: SubscriptionHandle) -> None: ...
```

Implementation: `VerdandiEventBus` wraps the Verdandi Unix
socket. A `NullEventBus` no-ops everything for operators who
don't run Verdandi.

Pattern matching uses dot-separated wildcards:
- `ember.chat.*` — all chat events
- `ember.**` — all Ember events (recursive)
- `mimir.decay` — exact match

---

## New Protocol: `AwarenessSource`

Used by Ember to introspect her own recent state.

```python
class AwarenessSource(Protocol):
    """Read-only access to recent state events."""
    def recent_events(
        self,
        event_pattern: str = "**",
        within_seconds: int = 3600,
    ) -> list[Event]: ...

    def summary(self, within_seconds: int = 3600) -> AwarenessSummary: ...
```

`AwarenessSummary` is a dataclass capturing:
- Number of chat turns in the window
- Most-frequent topics (via simple keyword extraction)
- Tool-call counts by type
- Recent errors (if any)
- Rhythm context (if Astrology enabled)

Implementation: `VerdandiAwarenessSource` queries the
Verdandi bus's recent-event ring buffer.

---

## New Protocol: `MoodChannel`

Used for register-shaping in chat responses.

```python
class MoodChannel(Protocol):
    """Detects a register/mood from input + awareness state,
    and optionally seeds verse-context to shape Funi's tone."""

    def detect(
        self,
        operator_input: str,
        awareness_summary: AwarenessSummary | None,
        rhythm: RhythmState | None,
    ) -> Mood:
        """Classify the desired register."""
        ...

    def seed_register(self, mood: Mood) -> str | None:
        """Optional: produce a tone-context fragment for the
        Funi system prompt (e.g., a Seiðr verse used as
        register inspiration, NOT as literal output)."""
        ...
```

`Mood` is an enum:
- `NEUTRAL` (default)
- `INTROSPECTIVE` (evening, slow, reflective)
- `BUOYANT` (morning, energetic)
- `SOLEMN` (cosmic / mythic / memorial)
- `PRACTICAL` (problem-solving)
- `CURIOUS` (operator-asking-questions register)

Implementation: `EmotionalIntelligenceMoodChannel` is a small
classifier (rule-based; could grow to use a small LLM) that
maps inputs to moods.

---

## New Protocol: `RhythmSource`

Used for temporal awareness.

```python
class RhythmSource(Protocol):
    """Current temporal context."""

    def current(self) -> RhythmState: ...

    def subscribe(
        self,
        events: Iterable[RhythmEvent],
        handler: Callable[[RhythmChange], None],
    ) -> SubscriptionHandle: ...
```

`RhythmState` is:
- `time_of_day: Literal["morning", "afternoon", "evening", "night"]`
- `lunar_phase: float` (0-1 cycle)
- `season: Literal["winter", "spring", "summer", "autumn"]`
- `is_solstice_or_equinox: bool`
- `is_eclipse_period: bool`

Implementation: `AstrologyRhythmSource` calls into the
Astrology Engine sibling.

---

## New Protocol: `AvatarSource` (Phase 4)

For Auga's visual embodiment.

```python
class AvatarSource(Protocol):
    """Source of VRM avatars for visual embodiment surfaces."""

    def get_current(self) -> Path:
        """Return path to the current avatar VRM file."""
        ...

    def generate(self, params: AvatarParams) -> Path:
        """Generate a new avatar with the given parameters."""
        ...
```

Implementation: `HamrAvatarSource` calls into Hamr.

Phase 4 only; no V1 implementation.

---

## New Protocol: `IngestSource`

Generalizes Smiðja's `local_files` pattern for corpus
ingestion. Allows new ingest types beyond filesystem walks.

```python
class IngestSource(Protocol):
    """A source of ingestable documents."""

    def walk(self) -> Iterator[ParsedFile]:
        """Yield documents one at a time."""
        ...

    def name(self) -> str:
        """Operator-facing name for the source."""
        ...
```

Implementations:
- `LocalFilesIngestSource` (existing, refactored to this
  Protocol shape).
- `NorseDictIngestSource` (Phase 1 — the Cleasby-Vigfusson
  ingest helper).
- Future: `URLIngestSource`, `MemPalaceIngestSource`, etc.

---

## How Protocols compose

```python
@dataclass(frozen=True, slots=True)
class YggdrasilContext:
    """The cross-realm runtime context."""
    secrets: SecretResolver
    event_bus: EventBus
    awareness: AwarenessSource | None
    mood: MoodChannel | None
    rhythm: RhythmSource | None
    avatar: AvatarSource | None
```

`YggdrasilContext` is constructed at Ember startup from
`config.yggdrasil`. Each field is None if the operator
hasn't opted into that realm.

Chat-loop code uses the context via `getattr-with-fallback`:

```python
if ctx.rhythm:
    rhythm = ctx.rhythm.current()
else:
    rhythm = None  # tone shaping skipped
```

Pattern: **everything is optional, nothing is required**.

---

## Protocol versioning

Protocols can evolve. We use a `protocol_version` constant:

```python
class EventBus(Protocol):
    PROTOCOL_VERSION: ClassVar[int] = 1
    # ...
```

When a Protocol's contract changes, version bumps. Realm
adapters check compatibility:

```python
def get_event_bus(config) -> EventBus:
    bus = VerdandiEventBus(config)
    if bus.PROTOCOL_VERSION < EXPECTED_VERSION:
        raise ConfigError("Verdandi too old; upgrade to vN+")
    return bus
```

This is the same pattern Stofa uses for plugin compatibility.

---

## Where Protocols live in code

```
src/ember/schemas/
├── yggdrasil_protocols.py    # NEW — all new Protocols defined here
├── yggdrasil_dataclasses.py  # NEW — RhythmState, Mood, etc.
└── config.py                 # YggdrasilConfig added
```

Protocols + their dataclass companions live in `schemas/` so
implementing them doesn't require depending on
`src/ember/yggdrasil/`.

---

## Closing

The Protocol layer is **small and composable**. Six new
Protocols. All optional. Each implementable by any party
(including community plugins). Yggdrasil's adapters are the
first implementations; not the only ones.

This is the architectural foundation that lets the system
evolve over years without breaking the core. The Vows hold;
the Protocols multiply.
