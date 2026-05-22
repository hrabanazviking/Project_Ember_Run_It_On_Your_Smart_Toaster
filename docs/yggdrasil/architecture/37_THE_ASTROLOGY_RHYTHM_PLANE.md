# 37 — The Astrology Rhythm Plane

How temporal awareness flows through Yggdrasil. Ephemeris-grade
time computation, ambient context for Ember's tone, and
gentle event triggers.

---

## The principle

Ember should know what time it is, in every sense — clock
time, day-segment, lunar phase, season, ecliptic events.
Not for *divination*, but for *rhythm*: a quieter evening
register, a brighter morning register, a longer pause around
the solstice.

This is `RhythmSource` — a Yggdrasil Protocol implemented by
the Astrology Engine adapter.

---

## What `RhythmState` carries

```python
@dataclass(frozen=True, slots=True)
class RhythmState:
    """A snapshot of temporal context."""
    timestamp: datetime       # the moment this was computed
    time_of_day: Literal["dawn", "morning", "afternoon", "evening", "night", "deep_night"]
    lunar_phase: float        # 0.0 = new, 0.5 = full, 1.0 = new again
    lunar_phase_name: Literal["new", "waxing_crescent", "first_quarter", ...]
    season: Literal["winter", "spring", "summer", "autumn"]
    season_progress: float    # 0.0 at solstice/equinox start, 1.0 at end
    is_solstice_period: bool  # within ±3 days of summer/winter solstice
    is_equinox_period: bool   # within ±3 days of spring/autumn equinox
    is_eclipse_period: bool   # within an eclipse window (opt-in surfacing)
    location: tuple[float, float] | None  # operator's lat/long (if configured)
```

This is **ambient context** — slow-changing, low-precision
information used for *tone* rather than *navigation*.

---

## How RhythmState flows

```
┌──────────────────┐
│ Astrology Engine │
│ (sibling)        │
└────────┬─────────┘
         │ (called once per N hours via cron-like loop)
         ▼
┌──────────────────┐
│ RhythmSource     │
│ adapter          │
│ (caches state)   │
└────────┬─────────┘
         │
         ├─────────────────────────────────────┐
         │                                     │
         ▼ (on every chat turn)                │ (on phase change)
┌──────────────────┐                ┌──────────▼────────────┐
│ EmotionalIntel.  │                │ Verdandi publishes    │
│ uses RhythmState │                │ rhythm.phase_change   │
│ to classify Mood │                │ event                  │
└──────────────────┘                └────────────────────────┘
```

The state is **cached** — we don't query Astrology Engine on
every chat turn (would be 100s of queries per hour). We
refresh every hour (configurable) and publish change-events
when the cache transitions to a new state (e.g.,
`time_of_day` changes from "afternoon" to "evening").

---

## How RhythmState shapes chat tone

The EmotionalIntelligence classifier reads `RhythmState` as
one of several inputs when picking a Mood:

| Rhythm signal | Mood bias |
|---|---|
| `time_of_day = night` or `deep_night` | toward INTROSPECTIVE or PRACTICAL (concise) |
| `time_of_day = morning` | toward BUOYANT |
| `lunar_phase_name = full` | toward SOLEMN, slightly mythic |
| `season = winter` | toward INTROSPECTIVE |
| `is_solstice_period` | toward SOLEMN, contemplative |
| `is_equinox_period` | toward CURIOUS, transitional |

This is one input among many. The operator's recent state
(via Verdandi awareness) and their input shape are the
larger signals. Rhythm is the *background* layer.

The bias is **subtle** — at most ~10% of Mood selection
weight. Operators see slightly-shifted tone without ever
needing to know why.

---

## Phase change events

When `RhythmState.time_of_day` transitions, Verdandi
publishes:

```python
{
    "type": "rhythm.time_of_day_change",
    "from": "afternoon",
    "to": "evening",
    "at": "2026-05-21T18:00:00Z"
}
```

Subscribers (the awareness layer, Stofa's StatusBar, future
plugins) can react. For example: Stofa might subtly shift
its theme accent color toward warmer tones in the evening
(opt-in).

Lunar phase + solstice/equinox transitions get similar
events, at slower cadences.

---

## Optional operator surfacing

By default, rhythm context is *invisible* — it shapes tone
but never appears as text in chat.

Operators can opt into surfacing:

```yaml
yggdrasil:
  rhythm:
    surface_phase_changes: true       # Stofa StatusBar shows current phase
    surface_eclipses: false           # rare; opt-in
    surface_seasonal_remarks: false   # Ember can say "happy equinox" etc.
```

The default is **silent ambient awareness**. The shift is
in Ember's *register*, not her *text*.

---

## Why this approach (vs full astrology)

Astrology Engine offers 16 CLI subcommands including birth
charts, transits, progressions, Arabic Lots, astrocartography,
etc. Yggdrasil uses *almost none* of these.

We use:
- `current ephemeris` (sun, moon, basic planet positions)
- `lunar phase` (current illumination + name)
- `solstice/equinox dates` (computed once per year per
  location)
- `eclipse computation` (per request, opt-in surfacing)

We deliberately don't use:
- Birth chart computation (would require birth data; we
  don't ask for it; not our place to assert "this is who
  you are").
- Personalized transit interpretation.
- Predictive divination.

The distinction: **astronomical computation is real science**
(Swiss Ephemeris is the gold standard). **Astrological
interpretation is a worldview**. Yggdrasil uses the science
for time-rhythm; we don't impose the worldview.

---

## Configuration shape (full)

```yaml
yggdrasil:
  rhythm:
    enabled: true
    location:
      latitude: 60.39           # operator-supplied; required for
      longitude: 5.32           # accurate lunar/seasonal computation
      timezone: Europe/Oslo
    refresh_interval_s: 3600    # cache state for 1 hour
    eclipse_window_days: 1      # how many days around an eclipse to flag
    surface_phase_changes: false
    surface_eclipses: false
    surface_seasonal_remarks: false
    mood_weight: 0.1            # 10% influence on Mood classifier
```

Defaults: silent, ambient, low influence. Operators tune up
or down.

---

## Performance

Astrology Engine computations are *fast* (single-digit
milliseconds on Pi 5). Caching means we typically pay zero
per-chat-turn cost.

Cold-start (boot): ~50ms for the first ephemeris query.
Subsequent queries (in cache): <1ms.

Background refresh thread: every hour, ~50ms.

Negligible footprint.

---

## What rhythm awareness enables (operator-facing)

Concrete experiences:

### "Ember talks differently at different times of day"

Operator notices: morning chats are *slightly* more
energetic; late-evening chats are *slightly* more
introspective. They can't quite pin it down — but the AI
*feels right for the time*.

### "Solstice felt special"

Operator chats on December 21. Ember's tone is a bit more
measured, slightly more contemplative. Operator might
notice: "huh, you seem thoughtful tonight." Ember (with
operator surfacing enabled) might mention: "It's the winter
solstice — a quiet evening." Without surfacing: the tone
shift is just *felt*.

### "I never knew there was an eclipse"

Operator opts into eclipse surfacing. Ember mentions a
lunar eclipse the night before, asks if the operator
noticed it. Soft anti-mainstream-news ambient awareness.

---

## Risk / known issues

- **Operator location requirement.** Lunar/seasonal/eclipse
  computation needs location. Without it, we default to
  UTC + sun-only behaviors.
- **Cultural variance.** "Morning" / "evening" semantics
  differ by latitude (sub-arctic operators have wildly
  different summer/winter day length). Defaults assume
  temperate latitudes; operators in extreme latitudes
  configure differently.
- **Edge effects.** Right at midnight, the rhythm changes;
  operators chatting through the transition might feel a
  subtle shift mid-conversation. By design.

---

## Open questions for Phase 3

1. **How granular should `time_of_day` be?** 6-bucket
   default (dawn/morning/afternoon/evening/night/deep_night)?
   Operator-tunable to 4 or 8?
2. **Should Ember mention rhythm in chat unprompted?**
   Default: never. Opt-in: rarely (1× per phase change,
   if at all).
3. **Multi-operator at different locations** (Phase 4
   multi-device). Each device has its own rhythm? Or one
   "operator's home rhythm" shared?

---

## Test strategy

Phase 3 ships:

- **Unit tests** for `RhythmSource` adapter with mocked
  Astrology Engine.
- **Integration test** with real Astrology Engine + fixed
  test dates verifying ephemeris values.
- **Cache test** verifying refresh interval is honored.
- **Mood-classifier integration test** that drives rhythm
  through 24h and verifies Mood biases shift expected
  directions.

Tests in `tests/unit/test_yggdrasil_rhythm.py` and
`tests/integration/test_yggdrasil_astrology_real.py`.

---

## Closing

The Astrology Rhythm Plane gives Ember *background hum* —
the ambient awareness of "what time it is, in every sense"
that makes her feel *of-the-world* rather than *of-the-
screen*. Subtle. Optional. Operator-controlled.

Real astronomical science. Used in service of the operator's
*felt experience* with their AI.
