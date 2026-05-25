---
name: ragnarok-codex-manifest
description: Authoritative list of all 52 files in the Ragnarok Codex (46 content + 6 meta)
metadata:
  codex: ragnarok
  type: meta
---

# MANIFEST — Ragnarok Codex

**Total files:** 52 (46 content + 6 meta)
**Target length:** 1,500–4,000 words per content doc
**Citation convention:** `/tmp/NorseWorld-Ragnarok/<path>:line`
**Closer:** every content doc ends with `## What This Means for Ember`
**License:** GPL-3.0 — study + cite + reimplement; do not vendor

---

## meta/ (6 docs — orchestrator + Scribe)

| Slug | Status |
|---|---|
| (root) `TASK_RAGNAROK_CODEX.md` | ✅ written |
| meta/SHARED_CONTEXT | ✅ written |
| meta/MANIFEST | ✅ written |
| meta/STYLE_GUIDE | ⏳ next |
| meta/INDEX | Scribe final pass |
| meta/READING_ORDER | Scribe final pass |
| meta/CROSS_AGENT_NOTES | Scribe final pass |

---

## 00_vision/ (5 docs — Skald)

| # | Slug | Scope |
|---|---|---|
| 00 | `00_OVERTURE.md` | Why mine a 50k-LOC archived single-player roguelike? Because Ember is already Norse, and Ragnarok is a 23-year proof that Norse mythology can be systematized into software without losing its weight |
| 01 | `01_RAGNAROK_ESSENCE.md` | What NorseWorld-Ragnarok is at the level of intent: Norse mythology as living systematized world, not pastiche; the Alchemist's 23-year saga |
| 02 | `02_THE_NORSE_QUESTION.md` | When does Old Norse naming earn its keep vs become performance? Ember's True Names vs Ragnarok's six classes; the cultural alignment honest examination |
| 03 | `03_ANTI_RAGNAROK.md` | What Ragnarok fails to be: archived without C# scripting replacement; Linux temporarily broken; cultural narrowing risks; what Ember must refuse |
| 04 | `04_VISION_SYNTHESIS.md` | Ember's identity refined post-Ragnarok study; the cultural alignment validated; world-model + persona-archetype as design axes complementing the embodiment axis |

---

## 10_domain/ (10 docs — Architect)

| # | Slug | Scope |
|---|---|---|
| 10 | `10_DOMAIN_MAP.md` | Macro architecture: `project/` subsystems — Universe, Items, Effects, Creatures, Database, Game, GUI |
| 11 | `11_UNIVERSE_DOMAIN.md` | `Universe/` — UniverseBuilder, NWField/Layer/Tile, Region/Village/Building, DungeonRoom/Door, Gate/MapObject/MapEffect. World-as-cellular-data architecture |
| 12 | `12_CREATURE_DOMAIN.md` | `Creatures/` — 150+ races + `Brain/` AI + `Specials/` unique creatures. Action-space ontology for living beings |
| 13 | `13_ITEMS_DOMAIN.md` | `Items/` — 200+ item types. ItemsList + Item; tool-and-artifact ontology |
| 14 | `14_EFFECTS_DOMAIN.md` | `Effects/` — 230+ magical effects + `Rays/`. Action-space ontology for changes |
| 15 | `15_BRAIN_DOMAIN.md` | `Creatures/Brain/` deep dive — creature AI as behavior-tree pattern; teaching for Strengr |
| 16 | `16_GAME_DOMAIN.md` | `Game/` — Types, Story, Quests, Scores, Ghosts; top-level orchestration |
| 17 | `17_DATABASE_DOMAIN.md` | `Database/` — game-data editor + (originally) scripting; the modding surface; teaching for Ember's data-driven extensibility |
| 18 | `18_LOCALIZATION_DOMAIN.md` | `languages/` — en + ru db, texts, dialog scripts; XML-as-content architecture |
| 19 | `19_DIALOG_DOMAIN.md` | `ru_dlg_*.xml` per-character dialog scripts (jarl, merchant, oldman, guardsman); persona-as-content teaching |

---

## 20_interface/ (6 docs — Architect: 3, Auditor: 3)

| # | Slug | Owner | Scope |
|---|---|---|---|
| 20 | `20_WORLD_CELL_INTERFACE.md` | Architect | NWField/Layer/Tile API; how the world is queried and mutated |
| 21 | `21_BRAIN_BEHAVIOR_INTERFACE.md` | Architect | Creature Brain decision interface; sense → think → act |
| 22 | `22_EFFECT_APPLICATION_INTERFACE.md` | Architect | How effects target and modify world/creatures |
| 23 | `23_DATABASE_SCRIPT_INTERFACE.md` | Auditor | Database editor + scripting interface (originally Java); what was promised, what shipped, what's missing |
| 24 | `24_DIALOG_XML_INTERFACE.md` | Auditor | XML schema for character dialog scripts; the conversation-as-tree pattern |
| 25 | `25_GUI_RENDER_INTERFACE.md` | Auditor | Tile + isometric rendering; FOV visibility integration |

---

## 30_execution/ (8 docs — Forge)

| # | Slug | Scope |
|---|---|---|
| 30 | `30_GAME_LOOP.md` | Turn-based main loop; player input → world update → render |
| 31 | `31_UNIVERSE_BUILD.md` | `UniverseBuilder.cs` walk; how 15+ worlds + 110 levels are generated |
| 32 | `32_DUNGEON_GENERATION.md` | `DungeonRoom.cs` + procedural generation algorithm (credited to Brigadir) |
| 33 | `33_FOV_ALGORITHM.md` | Field-of-view visibility (credited to Bu); shadowcasting or symmetric variants |
| 34 | `34_BRAIN_EXECUTION.md` | `Creatures/Brain/*.cs` runtime; per-creature thinking loop |
| 35 | `35_EFFECT_PIPELINE.md` | Effect activation → ray-tracing → target resolution → application |
| 36 | `36_QUEST_PROGRESSION.md` | `Game/Quests/` — quest state machine; narrative progression |
| 37 | `37_PERSISTENCE.md` | Save/load; how a complete game state serializes |

---

## 50_verification/ (6 docs — Auditor)

| # | Slug | Scope |
|---|---|---|
| 50 | `50_GPL3_LICENSE_IMPLICATIONS.md` | Copyleft consequences; the citation/vendoring boundary; what Ember can and cannot do |
| 51 | `51_ARCHIVE_RISK.md` | Project archived 2025; no upstream maintenance; security fix delivery impossible; what depends on archived code |
| 52 | `52_CODE_QUALITY_ARCHAEOLOGY.md` | 23-year codebase, mostly one developer; idioms; patterns; smells; what survives, what shows age |
| 53 | `53_CULTURAL_RESPECT.md` | Norse mythology as content vs costume; when adoption is honest vs pastiche; the LARP boundary |
| 54 | `54_LINUX_BROKENNESS.md` | README states "Linux temporarily not worked out for C# post-migration"; cross-platform claim vs reality |
| 55 | `55_SCRIPTING_GAP.md` | Java scripting removed; C# replacement never shipped before archive; the unfinished promise |

---

## 60_synthesis/ (11 docs — Cartographer: 6, Scribe: 5)

| # | Slug | Owner | Scope |
|---|---|---|---|
| 60 | `60_NORSE_SYSTEMATIZATION.md` | Cartographer | How a mythology becomes a software model; the principles distilled from 23 years of Ragnarok's design choices. **LOAD-BEARING DOC** |
| 61 | `61_CHARACTER_CLASSES_FOR_EMBER.md` | Cartographer | The 6 Ragnarok classes mapped onto Ember's 6 True Names + 6 ME roles; archetypes in software |
| 62 | `62_WORLD_AS_DATA.md` | Cartographer | UniverseBuilder + NWField patterns for Ember's situational reasoning; world-as-cellular-data |
| 63 | `63_BRAIN_FOR_STRENGR.md` | Cartographer | Creature Brain behavior-tree patterns for Ember's Strengr reasoning kernel |
| 64 | `64_PERSONA_AS_XML.md` | Cartographer | Dialog XML scripts as persona-content pattern; comparison with SAP's character cards |
| 65 | `65_ACTION_TAXONOMY.md` | Cartographer | Items × Effects × Creatures: scaling action space; how Ember stays coherent at scale |
| 66 | `66_INVENTED_METHODS.md` | Scribe | Novel patterns NOT in Ragnarok — Norse-name-with-gloss discipline, mythology-as-typed-resource, cultural-honesty checks |
| 67 | `67_DECISION_RECORDS.md` | Scribe | ADRs RAG-001..RAG-010 covering Norse naming discipline, GPL-3 study posture, character-class adoption, etc. |
| 68 | `68_SLICE_PLAN_NOTES.md` | Scribe | Notes on how Ragnarok findings touch the slice plan (propose-only) |
| 69 | `69_SEVEN_CODEX_BRAID.md` | Scribe | All seven codexes synthesized: Hermes + Peer + Klóinn + SAP + Waifu + CDK + Ragnarok. The first codex collection map after the embodiment triangulation closed |
| 6A | `6A_EMBER_CULTURAL_CHARTER.md` | Scribe | Proposed cultural charter: when/how Ember invokes Norse weight; gloss discipline; LARP avoidance; the public-friendliness of Old Norse |

---

## Agent Layer Assignments — final

| Agent | Role | Folder(s) | Doc count |
|---|---|---|---|
| 1 | **Skald** | `00_vision/` | 5 |
| 2 | **Architect** | `10_domain/` (10) + Architect-owned `20_interface/` (3) | 13 |
| 3 | **Cartographer** | Cartographer-owned `60_synthesis/` (6) | 6 |
| 4 | **Forge** | `30_execution/` (8) | 8 |
| 5 | **Auditor** | `50_verification/` (6) + Auditor-owned `20_interface/` (3) | 9 |
| 6 | **Scribe** | Scribe-owned `60_synthesis/` (5) + meta finalization (3) | 8 |

**Total dispatch:** 6 parallel agents → 46 content + 3 meta finalization.

---

## Reading Order (preliminary — Scribe finalizes)

1. `meta/SHARED_CONTEXT`
2. `00_vision/00_OVERTURE` → `04_VISION_SYNTHESIS`
3. `60_synthesis/60_NORSE_SYSTEMATIZATION` — the load-bearing prize
4. `60_synthesis/61_CHARACTER_CLASSES_FOR_EMBER`
5. Domain doc of interest (e.g. `15_BRAIN_DOMAIN`, `19_DIALOG_DOMAIN`, `11_UNIVERSE_DOMAIN`)
6. Matching interface + execution docs
7. `50_verification/50_GPL3_LICENSE_IMPLICATIONS` + `53_CULTURAL_RESPECT`
8. `60_synthesis/69_SEVEN_CODEX_BRAID` + `6A_EMBER_CULTURAL_CHARTER` — closes the wave

---

## Slug Glossary (cross-codex prefix)

- `[[hermes:<slug>]]` → `docs/hermes_codex/`
- `[[peer:<slug>]]` → `docs/peer_codex/`
- `[[kloinn:<slug>]]` → `docs/kloinn/`
- `[[sap:<slug>]]` → `docs/sap_codex/`
- `[[waifu:<slug>]]` → `docs/waifu_codex/`
- `[[chatdoll:<slug>]]` → `docs/chatdoll_codex/`
- `[[ragnarok:<slug>]]` → this codex
- `[[ember:<slug>]]` → root or `docs/`
