# 90 — Phase Overview

The five phases of Yggdrasil integration, what they
deliver, what they defer.

---

## The principle

Yggdrasil is *too large to ship at once*. We phase it.

Each phase:
- Ships *operator-visible value*.
- Doesn't break the previous phase.
- Sets up the next.

Five phases. Each is a *real release* of Ember with
expanded capabilities.

---

## The phases

| Phase | Name | What ships | What's deferred |
|---|---|---|---|
| 1 | Roots | Bifrǫst + Mímir + Huginn integration; Kista mediation; Verdandi observability | Federation, Mirror, Skein/Skry live |
| 2 | Branches | Seiðr mood-channel; Astrology rhythm; Hamr (basic); Audit (light) | Deep audit; model-based mood; Hamr animation |
| 3 | Crown | Self-awareness layer; emotional-intelligence; meta-learning; intuition; dreamstate | Curiosity; Mirror; Trinity fusion |
| 4 | Network | Federation across operator's tailnet; distributed coordination | Skein live; Skry live |
| 5 | Constellation | Mirror of Ginnungagap; Skein knowledge graph; Skry projection; multi-modal | (the next horizon) |

Each phase delivers something *the operator can use today*
while laying groundwork for the next.

---

## Why this order

### Phase 1: Roots first

The memory layer is foundational. Everything else
depends on Bifrǫst + Mímir + Huginn working. So we ship
those first — the *roots* of the tree.

Also: Kista (secret plane) + Verdandi (event bus) are
needed for *every* later phase. They go in early.

### Phase 2: Branches next

With memory working, we add the *outward* layers — tone
(Seiðr), time-awareness (Astrology), embodiment (Hamr).
These are *additive* to Phase 1; don't break it.

Audit goes in light-mode here. Deep mode comes later
when devices warrant.

### Phase 3: Crown — the canopy of AI capabilities

Self-awareness, emotional intelligence, meta-learning,
intuition, dreamstate. These are the *AI capability
crown* — what makes Ember feel intelligent rather than
mechanical.

They need Phase 1 (memory) + Phase 2 (rhythm/mood) to
work, so they come third.

### Phase 4: Network — federation

Once one device's Ember is great, expand to many.
Federation needs everything from Phases 1-3 to be stable.

Adds the *cross-device* dimension.

### Phase 5: Constellation — the advanced frontier

The Mirror; Skein knowledge graph; Skry projection;
multi-modal (vision-language). These are the *most novel*
capabilities; they need everything stable first.

The "horizon" — but not the end. Yggdrasil grows.

---

## What's in scope vs out of scope

In scope through Phase 5:
- All eleven sibling projects fully integrated.
- The methods of [`../methods/`](../methods/) (Borg
  Protocol, Heimdall, Well of Replay, Rhythmic
  Computation, Trinity Fusion, Mirror).
- Cross-platform support (TINY through WORKSTATION).
- Offline-first guarantees.
- Federation.

Out of scope (V6+ or never):
- Cloud Yggdrasil. (Operators can self-host on VPS, but
  no Anthropic-hosted offering.)
- "Agentic" autonomous-action features. (Curiosity-driven
  ingest is the closest; even it is operator-approved.)
- Public marketplace of sibling-projects. (Each operator
  curates their own; no central app store.)
- AGI / superintelligence claims. (We build a *small,
  tethered* AI. We don't chase scale-up.)

---

## Phase boundaries

Each phase ends with a *release*. Before release:
- All planned tests pass on all profile classes.
- Documentation complete for the phase's features.
- Operator can install fresh and have working Ember.
- Existing operators can upgrade without data loss.

Releases are versioned: `ember-agent==1.0.0` (Phase 1),
`2.0.0` (Phase 2), etc. Semantic versioning within a
phase.

---

## Timeline (rough)

Not commitments; rough sequencing:

- **Phase 1 (Roots):** 3-6 months from now.
- **Phase 2 (Branches):** 6-12 months.
- **Phase 3 (Crown):** 12-18 months.
- **Phase 4 (Network):** 18-24 months.
- **Phase 5 (Constellation):** 24+ months.

Throughout: small operator-visible releases (point versions
within a phase) every 2-4 weeks.

---

## What operators see at each phase

### Phase 1 ships

Operator installs Ember. Bifrǫst + memory composition
works. Stofa shows memory in the Well panel. Chat feels
*remembered* across sessions.

Visible message: "Yggdrasil V1 — composed memory across
Mímir + Huginn + Muninn."

### Phase 2 ships

Operator notices: Ember's tone fits the moment. Verses
seed her responses subtly. Astrology layer surfaces
"full moon tonight" if asked. Audit catches obvious
errors. Optional avatar appears in CLI/TUI.

Visible message: "Yggdrasil V2 — mood, rhythm, audit,
and embodiment."

### Phase 3 ships

Operator notices: Ember says "I notice you've been
asking about X" naturally. Replies fit register
intuitively. Long-term memory consolidates overnight.
Intuition surfaces related notes unprompted.

Visible message: "Yggdrasil V3 — self-awareness,
emotional intelligence, meta-learning."

### Phase 4 ships

Operator can now run Ember on multiple devices that
share memory + identity. Laptop offloads inference to
homelab. Pi-stofa-only-mode works.

Visible message: "Yggdrasil V4 — federation across
your tailnet."

### Phase 5 ships

The Mirror reports weekly. Skein knowledge graph
surfaces in Stofa. Vision-language model (if hardware
allows) understands operator's images.

Visible message: "Yggdrasil V5 — the constellation
complete."

---

## What if a phase takes longer

We don't ship early to hit dates. If Phase 1 needs an
extra 2 months for stability, it gets the extra 2 months.

Slipping doesn't help the next phase; broken Phase 1 means
broken Phase 2.

This is the Iron Law of *deliver quality, not promises*.

---

## Per-phase ratification

Each phase has a *ratification gate*:
- Plan documented.
- Operator-personas (Iðunn, Volmarr, Sigrún) walked through
  the design.
- Edge cases considered.
- Test plan written.

Only then does code begin.

This mirrors the ratification-gate currently in place for
Project Ember's first slice (per the project memory).

---

## How operators contribute per phase

Yggdrasil is open. Operators (especially Sigrún
power-users) contribute:

- **Phase 1:** Brunnr backend extensions for unusual
  storage; ingest pipelines.
- **Phase 2:** Mood-channel verses; avatar models; rhythm
  rules for their cultural traditions.
- **Phase 3:** Pattern-detection heuristics; classifier
  refinements.
- **Phase 4:** Federation discovery for non-tailnet
  networks; per-OS coordination.
- **Phase 5:** Skein extensions; multi-modal models.

Each phase opens a new contribution surface.

---

## What this roadmap is NOT

- **Not a marketing roadmap.** No "features by Q4"
  promises.
- **Not a feature list.** It's a *sequencing* of work.
- **Not exhaustive.** Each phase has details that emerge
  during implementation.
- **Not immutable.** If learning shifts the order, we
  adjust.

---

## Closing

The Phase Overview is **the path from where we are to where
we're going**. Five phases; each shipping value; each
setting up the next.

We don't sprint. We build. Each phase becomes a stable
plateau before we climb to the next.

Operators get a *real Ember* at every phase — not a
half-built one waiting for completion. The Vows hold
throughout. The system grows; it never breaks.
