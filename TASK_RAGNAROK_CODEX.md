# TASK: Ragnarok Codex — Mining NorseWorld-Ragnarok for Ember's Norse Systematization

**Started:** 2026-05-25
**Owner:** Volmarr + six Mythic Engineering agents
**Status:** Authoring (parallel) — pending agent dispatch
**Branch:** `development`
**Sibling codexes:** Hermes (58), Peer (scaffold), Klóinn (57), SAP (84), Waifu (22), Chatdoll (70)

---

## Scope

Read the NorseWorld-Ragnarok codebase (`Serg-Norseman/NorseWorld-Ragnarok`, cloned to `/tmp/NorseWorld-Ragnarok/`) and produce a structured corpus of **46 content MD documents** under `docs/ragnarok_codex/` that distill what this **complete, archived, Norse-mythology-systematized roguelike** teaches Ember about:

- **Norse identity rendered in software** — 23-year project where every name, system, and structure carries Old Norse weight. Direct teaching for Ember, whose own True Names (Funi/Strengr/Brunnr/Smiðja/Hjarta/Munnr) and Vows are Norse-rooted
- **Persona archetypes** — 6 character classes (Viking, Woodsman, Blacksmith, Sage, Conjurer, Alchemist) parallel ME's six roles; what does it mean to systematize human archetypes into code?
- **Action and effect spaces** — 200+ items, 230+ magical effects, 150+ creature races, 110 levels: how does a complete game model action-space taxonomy?
- **Procedural world generation** — 15+ dynamically-generated worlds (Midgard / Jotenheim / Nidavellir / Niflheim / Asgard); world-as-data architecture
- **AI brain modeling** — `Creatures/Brain/` subdir holds creature AI; teaching for Ember's reasoning kernel (Strengr)
- **Dialog systems** — XML dialog scripts per character archetype (jarl, merchant, oldman, guardsman); persona-as-content
- **GPL-3.0 license posture** — strong copyleft. Study + cite freely; vendoring would force GPL on Ember. Adopt-list cautious; pattern adoption + reimplementation OK
- **Completeness as teaching** — unlike previous codexes (active frameworks), this is a *finished artifact*, archived 2025. Archaeological study mode

This is the **first non-embodiment codex** (after Hermes/Peer/Klóinn/SAP/Waifu/CDK all centered on agent frameworks or avatar embodiment). The teaching axis shifts from "how to build agent infrastructure" to "how to systematize a mythology into a working software model."

## License posture

**GPL-3.0** — confirmed at `/tmp/NorseWorld-Ragnarok/LICENSE`. Copyleft. Implications:
- **Citation:** unlimited (study, line-references, pattern descriptions)
- **Pattern adoption:** OK with attribution
- **Code vendoring:** forces GPL on Ember source — **avoid**
- **Reimplementation from scratch:** OK (functional ideas are not copyrightable)
- **Adapt-list:** can adapt *concepts* freely; cannot copy *code* without GPL'ing Ember

## Method

Six Mythic Engineering agents work in parallel (no Forge split — execution layer is light at 8 docs). Each reads `meta/SHARED_CONTEXT.md`, `meta/MANIFEST.md`, `meta/STYLE_GUIDE.md` before starting.

| Agent | Role | Layer | Docs | Folder |
|---|---|---|---|---|
| 1 | Skald — Sigrún Ljósbrá | Vision | 5 | `00_vision/` |
| 2 | Architect — Rúnhild Svartdóttir | Domain + Interface | 10 + 3 = 13 | `10_domain/` + 3× `20_interface/` |
| 3 | Cartographer — Védis Eikleið | Synthesis | 6 | 6× `60_synthesis/` |
| 4 | Forge — Eldra Járnsdóttir | Execution | 8 | `30_execution/` |
| 5 | Auditor — Sólrún Hvítmynd | Verification + Interface | 6 + 3 = 9 | `50_verification/` + 3× `20_interface/` |
| 6 | Scribe — Eirwyn Rúnblóm | Synthesis + meta finalization | 5 + 3 = 8 | 5× `60_synthesis/` + meta finalization |

**Push cadence:** agents write files only. Orchestrator commits + pushes per layer. Final Scribe pass for INDEX/READING_ORDER/CROSS_AGENT_NOTES. Pull-rebase between pushes due to ongoing concurrent activity in the repo.

## What Exists Now

- `/tmp/NorseWorld-Ragnarok/` — full clone, 50,517 C# LOC across 266 files, GPL-3.0, archived
- `project/Universe/` — world model
- `project/Items/`, `project/Game/`, `project/GUI/`, `project/Effects/`, `project/Database/`, `project/Creatures/` (with `Brain/` and `Specials/` subdirs)
- `languages/en_db.xml`, `languages/ru_db.xml`, `languages/ru_dlg_*.xml` — localization + dialog scripts
- `~/ai/ember/docs/ragnarok_codex/` — empty scaffold with subdirs
- This TASK file
- `meta/SHARED_CONTEXT.md`, `meta/MANIFEST.md`, `meta/STYLE_GUIDE.md` — to be written

## What Is Needed

- **46 MD docs**, each 1,500–4,000 words, technical, entertaining, insight-rich, ending with `## What This Means for Ember`
- Citations to real `.cs` and `.xml` files
- **Synthesis layer is unusually heavy** (11 docs of 46) because Norse-mythology-systematization is the actual teaching prize
- Dedicated GPL-3 license-implications doc in verification
- Cross-references to all six prior codexes where relevant; Ember root docs liberally

## Non-Goals

- Do NOT modify Ember source code, slice plan, sibling codexes
- Do NOT propose vendoring Ragnarok GPL-3 code (only reimplementation from concepts)
- Do NOT paraphrase the README — cite actual `.cs`/`.xml` files
- Do NOT mistake the game's Norse styling for permission to overstate Ember's Norse identity

## Vows Honored

- **Open Knowledge** — GPL-3 means citation + concept-adoption OK; vendoring avoided
- **Smallness** — every Ember proposal must remain Pi-runnable
- **Tethered Grounding** — world-model lessons must integrate with Brunnr/Well
- **Pluggable Storage** — proposals stay backend-neutral
- **Modular Authorship** — every borrowed concept stays optional
- **Public-Friendliness** — Norse names with English glosses on first use
- **Flexible Roots** — no absolute paths
- **License-Aware Study Posture** *(Waifu-proposed)* — GPL-3 here means citation OK + vendoring restricted (distinct from Apache-2.0 CDK)
- **Server-Held-Keys-Only** *(CDK-proposed, three-corpus convergent)* — not directly relevant to this codex but worth noting in interface docs
- **Absolute Boundary Directive** (in `RULES.AI.md`) — document only; no code generation

## Next Steps After Authoring

1. Volmarr reviews `60_synthesis/` synthesis docs (the Norse-systematization is the prize)
2. Per-layer commits + push + final Scribe pass commit
3. DEVLOG entry
4. Memory updates ([[project-ragnarok-codex]], [[reference-ragnarok-codex-findings]])

## Continuation Notes

If an agent runs out of budget mid-doc, leave a `## Continuation Notes` block. No silent truncation.
