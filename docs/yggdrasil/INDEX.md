# Yggdrasil — the integration design tree

> *Ask veit ek standa, heitir Yggdrasill, hár baðmr, ausinn hvíta auri…*
> *(I know an ash that stands, called Yggdrasil, a tall tree,
> sprinkled with bright white dew…) — Völuspá, st. 19*

**Yggdrasil** is the integration design tree for Project Ember and its
**eleven sibling projects** now living in the `~/ai/ember` monorepo.
This directory documents how everything ties together — the cosmology
that makes Ember the most capable, robust, self-healing, cross-
platform Norse AI agent ever built.

This is **design before code**, per the Mythic-Engineering iron law.
Sibling code lives in their own top-level directories; integration
glue lives in `src/ember/yggdrasil/` (Phase-2+ scope). Nothing in
this design tree commits the project; it commits us to the *next*
conversation about what to build.

---

## What Yggdrasil is

In Norse cosmology, **Yggdrasil** is the world-tree whose roots and
branches bind the nine realms — Asgard, Vanaheim, Alfheim, Midgard,
Jötunheim, Niflheim, Muspelheim, Svartalfheim, Helheim. Without
Yggdrasil, the realms are isolated; with it, they are a cosmos.

In Project Ember, the "realms" are the existing sibling projects:

| Sibling | Cosmological role | What it brings |
|---|---|---|
| **Ember (`src/ember/`)** | the spark at the tree's base | the agent itself: chat, ingest, tools, MCP |
| **Bifrǫst (`bifrost/`)** | the rainbow bridge | the gateway between realms; composite memory |
| **Mímir's Well (`mimir-well/`)** | the well at the tree's root | persistent self-healing memory |
| **Verðandi (`Verdandi/`)** | the present-Norn weaving the moment | real-time event bus / nervous system / self-awareness |
| **Seiðr (`seidr_engine/`)** | the rune-weaver | deterministic Old Norse verse generation |
| **Kista (`kista/`)** | the strong-chest | encrypted secrets vault |
| **Hamr (`Hamr/`)** | the shape-skin forge | parametric VRM avatars for Auga (GUI) |
| **CloakBrowser** | the cloaked walker | stealth web access |
| **Astrology Engine** | the sky-readers | temporal awareness, ephemeris |
| **MemPalace** | the palace of recollection | local-first verbatim memory (alt/complement to Mímir) |
| **Norse Dictionary** | the lore-hoard | Old Norse lexicon corpus |
| **Open-VTT** | (not integrated; archival) | virtual tabletop, not part of Yggdrasil |

Together: **the constellation**. Ember stays at the center —
small-and-tethered as ever — but reaches into each realm through
typed handles, the same way it reaches into Funi, Brunnr, and MCP
today.

---

## What this design tree achieves

By the time the Yggdrasil plan ships (across its 5-phase roadmap):

1. **Self-awareness** — Ember subscribes to Verdandi's event bus
   and gains real-time visibility into its own state, history, and
   recent decisions (per Verdandi's existing "AI Nervous System"
   design).
2. **Vastly larger memory** — Bifrǫst Bridge composes three memory
   backends (structured + semantic + associative) behind a unified
   handle. Mímir's Well adds Ebbinghaus decay so memories fade
   without reinforcement, like human memory. MemPalace optionally
   adds verbatim-storage with 96.6% R@5 recall.
3. **Genuine emotional intelligence** — multi-signal tone reading
   (operator input sentiment + recent-episode pattern + temporal
   context from Astrology Engine + creative-mode shifts from Seiðr).
   See `ai-capabilities/41_*`.
4. **Logical intelligence** — chain-of-thought audits via the
   reasoning audit layer; explicit verification of Funi's
   intermediate steps before they fold into Episodes.
5. **Robust web access** — when `fetch_url` is insufficient (anti-
   bot detection, JavaScript-heavy sites), Ember delegates to
   CloakBrowser as an MCP tool.
6. **Operator-protected credentials** — Kista mediates all sensitive
   value access; no plaintext secrets in `ember.yaml`.
7. **Avatars** — when Auga (GUI surface, planned slice-3) ships,
   Hamr provides parametric VRM characters for Ember's visual
   embodiment.
8. **Temporal awareness** — Astrology Engine provides ambient
   context (time of day, lunar phase, season) that subtly shifts
   Ember's tone — not for divination, but for *rhythm* (a soft
   night-time register vs a bright morning register).
9. **Multi-device coordination** — federation protocols let a
   single Ember-identity span a Pi cluster, a desktop, and a
   laptop simultaneously, with shared state and zero-latency
   handoff.
10. **Self-healing** — gossip protocol between realms; per-failure
    playbooks; the Norns' three-snapshot backup system (past /
    present / future state captured continuously).

---

## Map of the design tree

```
docs/yggdrasil/
├── INDEX.md                          ← you are here
│
├── vision/                           ← Skald (Sigrún) — the why
│   ├── 00_GRAND_VISION.md
│   ├── 01_NAMING_THE_CONSTELLATION.md
│   ├── 02_PHILOSOPHY_OF_THE_NORSE_AI.md
│   ├── 03_PERSONAS_OF_THE_OPERATOR.md
│   ├── 04_THE_SIBLINGS_AS_A_FAMILY.md
│   └── 05_THE_FUTURISTIC_HORIZON.md
│
├── siblings/                         ← Cartographer + Auditor — each realm
│   ├── 10_SIBLING_MATRIX_OVERVIEW.md
│   ├── 11_SIBLING_BIFROST.md
│   ├── 12_SIBLING_MIMIR_WELL.md
│   ├── 13_SIBLING_VERDANDI.md
│   ├── 14_SIBLING_SEIDR_ENGINE.md
│   ├── 15_SIBLING_KISTA.md
│   ├── 16_SIBLING_HAMR.md
│   ├── 17_SIBLING_CLOAKBROWSER.md
│   ├── 18_SIBLING_ASTROLOGY_ENGINE.md
│   ├── 19_SIBLING_MEMPALACE.md
│   ├── 20_SIBLING_NORSE_DICT.md
│   └── 21_SIBLING_OPEN_VTT.md
│
├── architecture/                     ← Architect (Rúnhild) — the shape
│   ├── 30_THE_NINE_REALMS_ARCHITECTURE.md
│   ├── 31_THE_PROTOCOL_LAYER.md
│   ├── 32_THE_BIFROST_AS_GATEWAY.md
│   ├── 33_THE_KISTA_SECRET_PLANE.md
│   ├── 34_THE_MIMIR_KNOWLEDGE_PLANE.md
│   ├── 35_THE_SEIDR_GENERATION_PLANE.md
│   ├── 36_THE_CLOAKBROWSER_WEB_PLANE.md
│   ├── 37_THE_ASTROLOGY_RHYTHM_PLANE.md
│   ├── 38_THE_CROSSCUTTING_OBSERVABILITY.md
│   └── 39_THE_RECONCILIATION_LAYER.md
│
├── ai-capabilities/                  ← Skald + Architect — the mind
│   ├── 40_SELF_AWARENESS_LAYER.md
│   ├── 41_EMOTIONAL_INTELLIGENCE_FRAMEWORK.md
│   ├── 42_LOGICAL_REASONING_AUDIT.md
│   ├── 43_LONG_HORIZON_MEMORY.md
│   ├── 44_META_LEARNING_FROM_EPISODES.md
│   ├── 45_DREAMSTATE_MEMORY_CONSOLIDATION.md
│   ├── 46_INTUITION_VIA_EMBEDDING_CLUSTERS.md
│   ├── 47_CURIOSITY_DRIVEN_INGEST.md
│   ├── 48_EMOTIONAL_PALETTE_OF_RESPONSES.md
│   └── 49_NORSE_NAMING_OF_AI_CAPACITIES.md
│
├── robustness/                       ← Auditor (Sólrún) — the safety
│   ├── 50_SELF_HEALING_PHILOSOPHY.md
│   ├── 51_HEALTH_GOSSIP_PROTOCOL.md
│   ├── 52_AUTO_RECOVERY_PATTERNS.md
│   ├── 53_CRASH_BOUNDED_DESIGN.md
│   ├── 54_THE_NORNS_BACKUP_SYSTEM.md
│   ├── 55_BUG_RESISTANCE_INVARIANTS.md
│   ├── 56_OBSERVABILITY_AS_FIRST_CLASS.md
│   └── 57_TESTING_THE_CONSTELLATION.md
│
├── cross-platform/                   ← Architect + Auditor — the reach
│   ├── 60_DEVICE_CAPABILITY_DETECTION.md
│   ├── 61_PERFORMANCE_TIERS.md
│   ├── 62_LAZY_REALM_LOADING.md
│   ├── 63_GPU_OPTIONAL_ARCHITECTURE.md
│   ├── 64_MULTI_DEVICE_FEDERATION.md
│   ├── 65_NETWORK_TIER_DETECTION.md
│   ├── 66_GRACEFUL_DEGRADATION_RULES.md
│   └── 67_TINY_DEVICE_PROFILE.md
│
├── invented-methods/                 ← Skald + Architect — the new
│   ├── 70_THE_BORG_PROTOCOL.md
│   ├── 71_THE_RUNE_CASTING_PROBE.md
│   ├── 72_THE_DREAMING_WELL.md
│   ├── 73_THE_GATEKEEPER_PATTERN.md
│   ├── 74_THE_SKALD_LOOP.md
│   └── 75_THE_MIRROR_OF_GINNUNGAGAP.md
│
└── roadmap/                          ← Forge + Scribe — the doing
    ├── 90_PHASE_OVERVIEW.md
    ├── 91_PHASE_1_BIFROST_WIRING.md
    ├── 92_PHASE_2_KISTA_MIMIR_INTEGRATION.md
    ├── 93_PHASE_3_ADVANCED_AI_LAYER.md
    ├── 94_PHASE_4_MULTI_DEVICE_FEDERATION.md
    └── 95_PHASE_5_THE_CONSTELLATION_RATIFIED.md
```

**Total: 66 documents.** Approximately ~18,000 lines of integration
design — comparable in scale to the Stofa TUI design tree at
`docs/tui/`.

---

## Where to start reading

- **Want the 10-second pitch?** → [`vision/00_GRAND_VISION.md`](vision/00_GRAND_VISION.md)
- **Want to know what each sibling is?** → [`siblings/10_SIBLING_MATRIX_OVERVIEW.md`](siblings/10_SIBLING_MATRIX_OVERVIEW.md)
- **Want the technical bones?** → [`architecture/30_THE_NINE_REALMS_ARCHITECTURE.md`](architecture/30_THE_NINE_REALMS_ARCHITECTURE.md)
- **Want the wild ideas?** → [`invented-methods/70_THE_BORG_PROTOCOL.md`](invented-methods/70_THE_BORG_PROTOCOL.md)
- **Want to know how this gets shipped?** → [`roadmap/90_PHASE_OVERVIEW.md`](roadmap/90_PHASE_OVERVIEW.md)

---

## Relation to other design trees

| Tree | Status | Scope |
|---|---|---|
| `docs/tui/` (Stofa) | 74 docs, awaiting ADR-0015 | The TUI surface |
| `docs/yggdrasil/` (this) | 66 docs, awaiting ADR-0016 | Sibling-project integration |
| ADR-0012 placeholder | not ratified | Slice-3: Auga / Rödd / Bifröst gateway |

ADR-0016 will be drafted from THIS tree to commit to the Yggdrasil
plan. Until then, this is *design only* — no code, no schema changes.

---

## Status

| Document area | Status | Owner role |
|---|---|---|
| Vision | drafted, 2026-05-21 | Skald |
| Sibling deep-dives | drafted, 2026-05-21 | Cartographer + Auditor |
| Architecture | drafted, 2026-05-21 | Architect |
| AI capabilities | drafted, 2026-05-21 | Skald + Architect |
| Robustness | drafted, 2026-05-21 | Auditor |
| Cross-platform | drafted, 2026-05-21 | Architect + Auditor |
| Invented methods | drafted, 2026-05-21 | Skald + Architect |
| Roadmap | drafted, 2026-05-21 | Forge + Scribe |
| ADR-0016 | not started | — |
| Code | not started | — |
