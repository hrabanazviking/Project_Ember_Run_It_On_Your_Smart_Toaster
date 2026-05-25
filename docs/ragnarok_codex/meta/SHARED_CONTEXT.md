---
name: ragnarok-codex-shared-context
description: Briefing every Mythic Engineering agent reads before authoring any ragnarok_codex document
metadata:
  codex: ragnarok
  type: meta
---

# SHARED_CONTEXT — Ragnarok Codex

Read this before authoring any doc.

---

## 1. What NorseWorld-Ragnarok Is

**Repository:** `Serg-Norseman/NorseWorld-Ragnarok` — cloned at `/tmp/NorseWorld-Ragnarok/`
**Version studied:** v0.11.0 (April 12, 2015) — final release
**Status:** **Archived March 13, 2025** (read-only on GitHub)
**Stars/forks:** 49 / 9 (niche but historically significant)
**Commits:** 27 (small git history; ~23-year development cycle 2002-2015 mostly pre-git)
**License:** **GPL-3.0** (confirmed at `/tmp/NorseWorld-Ragnarok/LICENSE`)
**Author:** Sergey Zhdanovskih (aliases Alchemist, Norseman), with team (Bu, Quiet, Brigadir, Aerton)
**Origin:** Remake of classical roguelike Ragnarok (Valhalla) by Thomas Boyd and Robert Vawter (1992-1995)

**Self-description:** "Remake of classical roguelike game Ragnarok (Valhalla). Game story is based on scandinavian mythology and sagas."

**Total size:** 50,517 C# LOC across 266 files + XML dialog scripts + localization files (English + Russian). 45 MB clone.

**Architecture (well-organized, single-developer-mature):**
```
project/
├── AssemblyInfo.cs
├── Universe/                    ← world model
│   ├── UniverseBuilder.cs       ← top-level world construction
│   ├── NWField.cs / NWLayer.cs / NWTile.cs  ← cell-based world
│   ├── Region.cs / Village.cs / Building.cs ← composite places
│   ├── DungeonRoom.cs / Door.cs / BaseRoom.cs ← procedural rooms
│   └── Gate.cs / MapObject.cs / MapEffect.cs  ← world objects
├── Items/                       ← 200+ item types
├── Effects/                     ← 230+ magical effects
│   └── Rays/                    ← ranged magic
├── Creatures/                   ← 150+ creature races
│   ├── Brain/                   ← AI behavior trees
│   └── Specials/                ← unique creatures
├── Database/                    ← game-data editor + scripting
├── Game/                        ← top-level game logic
│   ├── Types/                   ← enums, constants
│   ├── Story/                   ← narrative branching
│   ├── Quests/                  ← quest system
│   ├── Scores/                  ← high-score tracking
│   └── Ghosts/                  ← death-replay system
├── GUI/                         ← rendering subsystem
│   └── Controls/                ← UI widgets
└── libs/                        ← native binaries (win-x86, win-x64)

languages/
├── en_db.xml / ru_db.xml        ← game database localization
├── en_texts.xml / ru_texts.xml  ← UI strings
├── ru_dlg_*.xml                 ← per-character dialog scripts
│   (jarl, merchant, oldman, guardsman, ...)
└── ru_help.htm
```

**6 player character classes:** Viking, Woodsman, Blacksmith, Sage, Conjurer, Alchemist — each with distinct stats and progression.

**Worlds:** Midgard, Jotenheim, Nidavellir, Niflheim, Asgard, plus dwarven caves and lands by gods/wizards. 15+ worlds, 110 levels total.

**Features:** 150+ creature races, 200+ items, 230+ magical effects, procedural generation, modding via Database editor, FOV (field-of-view) visibility algorithm, scripting (originally Java; C# replacement pending — never shipped before archive), flat-tile + isometric views, EN/RU localization with dialog scripts.

## 2. What Ember Is

Same as previous codexes — small-and-tethered AI agent at `~/ai/ember`, Six True Names (Funi/Strengr/Brunnr/Smiðja/Hjarta/Munnr), doc-rich + code-empty, ratification-gated slice plan.

**The cultural alignment is unique here.** Ember already names its parts in Old Norse. NorseWorld-Ragnarok already systematizes Norse mythology. This codex teaches Ember about *itself* — how to render Old Norse weight in software without becoming pastiche or LARP.

## 3. What This Codex Is For

To answer questions previous codexes have not touched:

> *"How do you systematize a mythology into a working software model? What does it mean to give an agent character-class archetypes? How does action-space taxonomy scale (200+ items × 230+ effects × 150+ creatures)? How does Ember stay culturally honest as it grows?"*

Previous codexes (SAP/Waifu/CDK) taught Ember about **embodiment**. Ragnarok teaches Ember about **world model + identity + content taxonomy**.

Specific axes:
- **Character classes** (6 classes) ↔ Ember's six True Names; what does it mean to give Ember "play styles"?
- **Procedural worlds** (15 worlds, 110 levels) ↔ Ember's situational reasoning; world-as-data
- **Creature Brain** (`Creatures/Brain/`) ↔ Ember's Strengr (reasoning kernel); behavior-tree-style decision making
- **Items + Effects taxonomy** (200 × 230) ↔ Ember's Smiðja (tools) + Munnr (output); how does action space stay coherent at scale?
- **XML dialog scripts** (per-archetype: jarl, merchant, oldman, guardsman) ↔ Ember's persona system; persona-as-content
- **Database editor** (modding) ↔ Ember's extensibility; data-driven content
- **GPL-3 license posture** ↔ License-Aware Study Posture (Waifu-proposed); copyleft constraints

## 4. How to Cite

Real `path:line` from `/tmp/NorseWorld-Ragnarok/`:

```
`/tmp/NorseWorld-Ragnarok/project/Creatures/Brain/SeerBrain.cs:42` — flight-from-danger heuristic
`/tmp/NorseWorld-Ragnarok/project/Universe/UniverseBuilder.cs:128` — Asgard generation logic
`/tmp/NorseWorld-Ragnarok/languages/ru_dlg_jarl.xml:14` — jarl dialog tree root
```

For Russian XML files (which carry the most idiomatic Norse content), cite even if translating; note `[translation: ...]` if quoting.

README claims marked `[unverified — README claim only]`.

## 5. Style — The "What This Means for Ember" Closer

Per STYLE_GUIDE. Every doc ends with:

```
## What This Means for Ember

**Adopt:** <patterns — for GPL-3 source, prefer reimplementation from concept; cite Ragnarok with attribution as inspiration>
**Adapt:** <patterns to take and transform>
**Avoid:** <patterns to reject>
**Invent:** <novel patterns this analysis suggests>
```

At least one **Invent** per doc. Synthesis docs naturally have many.

## 6. License Posture — GPL-3.0 (study + cite + reimplement; do not vendor)

Distinct from Apache-2.0 (CDK) and from no-LICENSE (Waifu study-only):

- **Citation:** unlimited
- **Pattern description:** unlimited
- **Concept adoption:** OK with attribution ("inspired by Ragnarok's X pattern")
- **Code vendoring:** **forbidden** unless Ember accepts GPL — currently not aligned
- **Reimplementation from concept:** OK (functional ideas are not copyrightable)

When proposing Adopt patterns, prefer "reimplement from concept (attribution: Ragnarok, GPL-3, line N)" wording.

## 7. Cross-Linking Convention

Within: `[[slug]]`. Across:
- `[[hermes:slug]]`, `[[peer:slug]]`, `[[kloinn:slug]]`, `[[sap:slug]]`, `[[waifu:slug]]`, `[[chatdoll:slug]]`
- `[[ember:slug]]` → root or `docs/`
- `[[ragnarok:slug]]` → this codex (bare `[[slug]]` also resolves)

Synthesis docs should cite multiple prior codexes for cross-codex coherence.

## 8. Threat Awareness

Ragnarok is a **complete, archived game** — much smaller threat surface than active frameworks:
- No network surface (single-player)
- No LLM API keys
- No mic/avatar/cloud
- **Threat is conceptual, not operational:** stagnant code = no security updates; vendor lock-in for any code copied wholesale (GPL); cultural appropriation if Norse content adopted naively

The Auditor's verification layer focuses on:
- License implications (GPL-3 copyleft)
- Archive-status risks (no upstream fixes)
- Cultural-respect implications (how to adopt Norse content without LARP)
- Code-quality archaeology (50k LOC by mostly one developer)

## 9. Do Not Touch

- Ember source code, slice plan, sibling codexes (Hermes/Peer/Klóinn/SAP/Waifu/Chatdoll)
- Anything outside `docs/ragnarok_codex/`

Propose; never enact.

## 10. The Cultural Question — Read This Carefully

Ember already names its parts in Old Norse. NorseWorld-Ragnarok also names its parts in Old Norse. **This is convergent, not borrowed.** Both projects independently chose Norse weight.

This codex's job is *not* to make Ember more Norse — Ember is already Norse. The job is to learn what *systematizing* Norse mythology in code teaches us:
- When to use Old Norse names (Funi, Strengr) vs English (Heart, Voice)
- When to gloss (Funi = "spark, fire") vs leave bare
- When the Norse weight earns its keep vs becomes performance
- How to scale (Ember has 6 True Names; Ragnarok has 6 classes, 5 worlds, hundreds of creatures — what's the right resolution?)

Be honest. Be culturally careful. Don't romanticize. Don't apologize. Match the source's directness.
