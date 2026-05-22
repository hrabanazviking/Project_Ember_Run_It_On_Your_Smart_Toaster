# 18 — Sibling: Astrology Engine

> *"Full-spectrum astrological computation. Swiss Ephemeris on
> bare metal. Norse sky, Hellenistic roots."*

Pi-deployable astronomy + astrology engine. 16 CLI subcommands.
pyswisseph-backed.

---

## What it is

A complete astrological computation library + CLI. From its
README:

- **Swiss Ephemeris** (`pyswisseph`) for precise planetary
  positions.
- **16 CLI subcommands** covering Arabic Lots, astrocartography,
  ephemeris queries, etc.
- **No cloud, no API keys, no lookup tables.** Real
  computations on bare metal.
- **Runs on a Raspberry Pi 5** as part of the "Hermes Agent"
  skill system.

---

## Why this sibling matters for Yggdrasil

It's the **temporal rhythm plane**.

Yggdrasil's emotional-intelligence layer (per
[`../ai-capabilities/41_EMOTIONAL_INTELLIGENCE_FRAMEWORK.md`](../ai-capabilities/41_EMOTIONAL_INTELLIGENCE_FRAMEWORK.md))
includes a *temporal awareness* component:

- Time of day (morning / afternoon / evening / night) shifts
  Ember's register.
- Lunar phase (waxing / full / waning / new) provides ambient
  context.
- Season (solstice / equinox-aware) gives long-cycle awareness.
- Specific astronomical events (eclipses, conjunctions) can
  trigger operator-facing notifications IF the operator
  opted in.

Astrology Engine provides all of this with *ephemeris-grade
precision*, not "what's roughly the time."

---

## How Yggdrasil integrates Astrology Engine

### Integration role

Two integration modes:

1. **Ambient signal source** — Yggdrasil's rhythm layer
   queries Astrology Engine at startup and at slow intervals
   (e.g., once per hour) for current temporal context.
2. **On-demand MCP tool** — when Funi explicitly asks "what
   time is it in cosmic terms?", a tool wraps Astrology
   Engine queries.

### Adapter shape

A `src/ember/yggdrasil/rhythm/` package:

- `client.py` — `AstrologyClient` calling Astrology Engine.
- `rhythm.py` — high-level "current rhythm" state object
  (time-of-day, lunar phase, season).
- `bridge.py` — bridges rhythm state changes into Verdandi
  events.

### Configuration shape

```yaml
yggdrasil:
  rhythm:
    enabled: true                # use Astrology Engine
    location:                    # for accurate ephemeris
      latitude: 60.39
      longitude: 5.32
      timezone: Europe/Oslo
    refresh_interval_s: 3600     # check rhythm every hour
    events:                      # optional notifications
      lunar_phase_change: true
      solstice_equinox: true
      eclipses: false            # only if operator opted in
```

### Why this enables emotional intelligence

A chat reply benefits from temporal context the operator
doesn't have to provide:

- 3am chat: "I notice you're up late — should I lean
  concise?"
- Full moon: tone slightly more imaginative.
- Autumn equinox: ambient register toward introspection.
- Operator's birthday (if Astrology Engine knows it): warmth.

These are *subtle modulations*, not gimmicks. The operator
can disable any of them; they happen because Astrology
Engine surfaced *precise* time-and-cycle data.

### What Astrology Engine does NOT do

We use the *temporal computation* parts — not the
*divination* parts. Yggdrasil does not:

- Make predictions about the operator's life.
- Cast birth charts as "this is who you are."
- Tell the operator "Mars is in retrograde; be careful."

It uses ephemeris data for ambient context only. If the
operator wants the divination features, they can use
Astrology Engine's CLI directly outside Yggdrasil.

---

## Risk / known issues

- **Cultural concerns.** Some operators distrust astrology
  as pseudo-science. Yggdrasil uses it as *time-rhythm
  computation* (which is real astronomy via Swiss Ephemeris,
  not astrology *per se*). The presentation matters:
  "lunar phase" is astronomy; "Mars in retrograde affects
  your love life" is what we don't do.
- **Ephemeris data is large** (~30MB). Pi-class operators
  install the data once.
- **Operator location requirement.** For accurate lunar
  phase + season, we need a rough location. Optional;
  defaults to UTC if not provided.

---

## Open questions for Phase 3 ratification

1. **What level of detail surfaces to chat?** Default: very
   light (a sentence per day, maybe). Tunable.
2. **What rhythm events trigger Verdandi notifications?**
   Default: lunar phase changes + solstice/equinox. Tunable.
3. **Hermes Agent vs Yggdrasil naming.** Astrology Engine
   mentions "Hermes Agent" as its integration target.
   Hermes is Hellenistic — different pantheon. Conflict? Or
   Ember + Hermes can coexist?

---

## Test strategy

Phase 3 ships:

- **Unit tests** for `AstrologyClient` with mocked Astrology
  Engine.
- **Integration test** with real Astrology Engine + a fixed
  date — verify queries return expected ephemeris values.
- **Rhythm-state test** — drive the system clock through 24
  hours; verify time-of-day transitions are detected
  correctly.

Tests in `tests/unit/test_yggdrasil_rhythm.py` and
`tests/integration/test_yggdrasil_astrology_real.py`.

---

## Operator-facing example

Phase 3 in action:

```
[3:14 AM, lunar phase: waning crescent, season: autumn]

> volmarr: what should I work on tomorrow?

ember: It's late — I'll keep this brief. From recent
documents, you've been thinking about Norse cosmology and
your AI architecture. The waning crescent moon traditionally
marked a time of completion in Norse rhythm; perhaps you're
near the end of a research arc and ready to write something
down?

(if rhythm-events visible in Stofa: tiny "🌙 waning crescent"
indicator in chrome)
```

The reply is *informed by* the temporal context (concise
because late, gentle introspection because the season + moon
suggest it) without ever lecturing about astrology.

---

## Closing

Astrology Engine is *time, with weight*. Ephemeris-grade
data feeding subtle tonal cues. The operator doesn't read
horoscopes; they get an AI that *knows what hour of what
season it is, and modulates accordingly*.

Optional, opt-in, gentle. Old Norse rhythm in modern code.
