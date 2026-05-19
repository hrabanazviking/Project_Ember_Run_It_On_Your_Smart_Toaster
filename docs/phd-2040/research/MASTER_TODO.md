# 🪖 Master TODO — All Projects & Ideas
> **Last updated:** 2026-05-10 by Runa  
> **Philosophy:** A project is not complete until it is fully completed AND pushed.

---

## 🔴 CRITICAL — Unpushed / Broken (Vault Keeper Priority)

These get auto-fixed by the Vault Keeper cron jobs every 6 hours. Listed here for awareness.

- [x] Hamr had 2 unpushed commits → **PUSHED** 2026-05-10
- [x] Eir missing README.md → **Created & pushed** 2026-05-10
- [x] Mímir Well DB was 0-byte empty → **Initialized with schema** 2026-05-10
- [x] 7 memory project bugs → **All fixed & pushed** 2026-05-10

---

## ⚔️ ACTIVE PROJECTS — NorseSagaEngine

### NorseSagaEngine Core (~/NorseSagaEngine/)

**Status:** Active development. 569 tests, ~81,676 LOC. Development branch.

#### 🐛 Remaining Bugs from Full Audit (108 total, ~97 fixed, ~11 unfixed)

- [ ] **M-03** — EventType subscription relies on enum names == values (fragile, undocumented)
- [ ] **M-08** — `npcs_present[0]` always combat defender; named targets ignored
- [ ] **M-10** — `tree.state.get()` on potentially-None tree.state → AttributeError
- [ ] **M-13** — `_resolve_optional_int` reads root_map only once; barely cross-validated
- [ ] **M-14** — 4-way cross-validation reads same `chosen` value 4x
- [ ] **M-16** — Empty player state defaults all emotion labels to "joy"
- [ ] **M-17** — Scripted combat always picks `npcs_present[0]` as defender
- [ ] **M-18** — `_aux_ai_client` accessed in `shutdown()` before init → AttributeError
- [ ] **M-19** — `_normalize_character_data` writes to `data/characters/` violating immutability rule
- [ ] **M-21** — `char_id` loop variable never used in drift note output (overlap with M-20, fixed)
- [ ] **M-26** — `scope="module"` fixture returns mutable instances; test corruption
- [ ] **M-27** — `_CHAOS_DESIRES` frozenset hardcoded; silently fails on WorldWill rename
- [ ] **M-28** — `st.text(alphabet=chars+action_words)` treats multi-char words as single chars
- [ ] **M-29** — `sys.path.insert(0, os.getcwd())` fails from non-root directory
- [ ] **M-31** — `find_spec` called twice for same module (redundant)
- [ ] **M-35** — `save_state("data/wyrd.json")` hardcoded relative path ignores data_path
- [ ] **M-36** — Two competing compaction limits (50 vs 120); inconsistent
- [ ] **M-37** — Exact numeric assertions on floating-point values; fragile
- [ ] **L-03** — Unconditional truncation `...` on short content
- [ ] **L-04** — `int(value)` silently truncates float config values
- [ ] **L-09** — `ElasticWindowCalculator()` re-instantiated with no config on every call
- [ ] **L-10** — `max(..., default=(None, 0))` is dead code
- [ ] **L-11** — Fragile string comparison in faction section guard
- [ ] **L-14** — `print()` in test function
- [ ] **L-15** — `assert x == True` unidiomatic
- [ ] **L-16** — `chaos_action_names` strategy defined but never wired to tests
- [ ] **L-18** — `random` fixture shadows Python builtin
- [ ] **L-19** — Non-dict `choices[0]` silently returns empty string
- [ ] **L-21** — Tuple unpacking assumes exact 4-tuple with no guard
- [ ] **L-24** — `CHECKMARK` referenced before declaration
- [ ] **L-25** — Assertion passes by coincidence (strip only removes trailing \n)
- [ ] **L-26** — EventType enum name==value coincidence undocumented

#### 🏗️ Major Architecture Debt

- [ ] **Modularization Phases 0–7** — Decompose `main.py` (2292 lines) and `core/engine.py` (5366 lines). Full plan in TODO.md lines 5418–5939.
- [ ] **Capability registry** — Replace `HAS_*` feature flags with proper registry pattern
- [ ] **Repository ports/adapters** — Abstract data access behind interfaces
- [ ] **pytest suite hangs** — Full collection works (639 tests) but test run never completes. 13 collection errors. Targeted single-file runs work fine. Root cause: likely async fixture deadlock in conftest.py.

#### 📋 Implementation Plans (Written, Not Started)

- [ ] **PLAN_T3C** — Personality Filter + Theory of Mind Engine (YAML traits → emotional channel weights, social pressure summaries from RelationshipGraph)
- [ ] **PLAN_T3D** — Web of Wyrd Knowledge Graph
- [ ] **PLAN_integration_gaps** — System integration gap analysis (2026-03-15)
- [ ] **PLAN_stub_implementations** — 13 stubs/bugs from placeholder audit (2 bugs, 3 stubs, 1 attr, 7 unwired)
- [ ] **PLAN_perf_improvements** — Performance improvement plan (2026-03-16)
- [ ] **PLAN_bug_fixes** — Remaining bug fix plan (2026-03-15)
- [ ] **PLAN_runtime_fixes** — Runtime fix plan (2026-03-15)

### WYRD Protocol (NorseSagaEngine/wyrd_protocol/)

**Status:** v1.0.0 complete on `development` branch. 432 tests passing. 164 Python files.

#### Phase 8 — Client SDK Layer (PREREQUISITE for Phases 9–13)
- [ ] **8A** — JavaScript/TypeScript SDK (`wyrdforge-js`) — npm package, auto-reconnect, TypeScript types
- [ ] **8B** — C#/.NET SDK (`WyrdForge.Client`) — NuGet package, Unity-compatible coroutine variant
- [ ] **8C** — GDScript/Godot HTTP module — Godot 4 addon, HTTPRequest node

#### Phase 9 — AI Companion & Agent Platform Bridges
- [ ] **9A** — OpenClaw Bridge — Node.js skill pipeline, inject WYRD world state
- [ ] **9B** — Norse Saga Engine Bridge — Python module, NSE entity → WYRD entity mapping
- [ ] **9C** — SillyTavern Extension — JS extension, system prompt injection, UI panel
- [ ] **9D** — Voxta Integration — Voxta action/service, context enrichment
- [ ] **9E** — Kindroid Bridge — Webhook-based, context enrichment
- [ ] **9F** — Hermes Agent Bridge — Python tool/plugin for Hermes framework
- [ ] **9G** — AgentZero Bridge — Memory/context tool wrapping PythonRPGBridge

#### Phase 10 — TTRPG / Virtual Tabletop Bridges
- [ ] **10A** — Foundry VTT Module
- [ ] **10B** — Roll20 API Script
- [ ] **10C** — Owlbear Rodeo Extension
- [ ] **10D** — D&D Beyond Extension
- [ ] **10E** — Fantasy Grounds Unity Module

#### Phase 11 — Game Engine Bridges
- [ ] **11A** — Unity Package
- [ ] **11B** — Godot Addon (for non-NSE games)
- [ ] **11C** — Unreal Engine Plugin
- [ ] **11D** — Minecraft Mod
- [ ] **11E** — Roblox Module
- [ ] **11F** — Defold Plugin
- [ ] **11G** — MonoGame Extension
- [ ] **11H** — pygame Integration
- [ ] **11I** — RPG Maker Plugin
- [ ] **11J** — CryEngine Plugin
- [ ] **11K** — Construct 3 Plugin
- [ ] **11L** — Amazon Lumberyard/O3DE Plugin

#### Phase 12 — AI Agent & Tool Bridges
- [ ] **12A** — Claude Code Plugin
- [ ] **12B** — Ollama Integration
- [ ] **12C** — LM Studio Integration
- [ ] **12D** — Hermes Agent Plugin
- [ ] **12E** — VaM (Virt-a-Mate) Integration

#### Phase 13 — Documentation & Tooling
- [ ] **13A** — Complete technical references for all plugins
- [ ] **13B** — User-friendly integration guides
- [ ] **13C** — Menu-driven install script (robust, self-healing, crash-proof)
- [ ] **13D** — Extensive documentation expansion

#### WYRD Protocol Roadmap TODO Items
- [ ] Finish all current phases of development
- [ ] Make all codebase more robust, self-healing, crash-proof
- [ ] Extensive bug hunting and fixing
- [ ] Trace all plugin functions for robustness
- [ ] Keep TODO.md up to date

### Yggdrasil → WYRD v0.2 Transition
**Status:** Architecture validated, not started.

- [ ] Map Yggdrasil's Nine Realms processing to WYRD Protocol's ECS/composite provider model
- [ ] Refactor Yggdrasil DAG orchestrator → WYRD's WorldLoom pipeline
- [ ] Migrate Huginn/Muninn ravens → WYRD's BifrostBridge abstract base
- [ ] Test Yggdrasil cognition modules against WYRD Protocol test harness
- [ ] Validate: performance, crash-proof, self-healing after migration

---

## ⚔️ ACTIVE PROJECTS — Memory System (All 10 Norse Packages)

All 10 packages: **215 tests ALL PASSING** ✅ (2,367 total including Hamr's 2233)

- [x] **Mímir Well v2.0** — 60 tests, schema initialized, FTS5 working
- [x] **Muninn v1.0** — 15 tests, hierarchical memory storage
- [x] **Huginn v1.0** — 13 tests, Qdrant vector search provider
- [x] **Bifröst v1.0** — 14 tests, composite memory bridge (resource leak fixed)
- [x] **Eir v1.0** — 11 tests, consolidation pipeline (backup .db fix, resource leak fixed, README added)
- [x] **Verðandi v0.1** — 21 tests, context weaver
- [x] **Svalinn v0.1** — 18 tests, SWE pruner
- [x] **Vörðr v0.1** — 31 tests, self-correction
- [x] **Sköfnung v0.1** — 15 tests, tool affinity
- [x] **Hlíðskjálf v0.1** — 17 tests, prompt cache
- [x] **Kista v2.0** — 149 tests, encrypted vault, 75 entries healthy

### Memory System Next Steps
- [ ] **Mímir v2.0** — Hybrid memory (location-addressed SQLite + content-addressed vector embeddings). Use `all-MiniLM-L6v2` (80MB, 384-dim) for Pi
- [ ] **Huginn enhancement** — Use attention patterns to weight memory retrieval (wyrd-attention architecture)
- [ ] **WyrdState** — Fresh DB, 5 tables, ready for use. Build causal relationship graphs between memories
- [ ] **Kista Gmail auth** — Gmail app password expiry; may need re-auth

---

## ⚔️ ACTIVE PROJECTS — Hamr (VRM Avatar Engine)

**Status:** v0.8.0, 2233 tests, pushed clean.

- [ ] **Phase 17+** — Continue development (last commit: Phase 16 T7)
- [ ] **MToon shader** performance tuning
- [ ] **Pose library** expansion
- [ ] **Spring bone** tuning
- [ ] **VRM 1.0 conversion** improvements

---

## ⚔️ ACTIVE PROJECTS — Seiðr-Smiðja (VRM Forge)

**Status:** 489 tests passing. Brúarhönd v0.1 sealed. 10 ADRs accepted.

- [ ] **Brúarhönd v0.2 iteration** — The next major milestone
- [ ] **MCP forge door (Mjöll)** — Blender MCP integration on port 9876
- [ ] **CLI forge door (Rúnstafr)** — Command-line interface
- [ ] **REST forge door (Straumur)** — REST API endpoint
- [ ] **Oracle Eye** — Blender headless render preview PNGs
- [ ] **VRoid Studio** integration on Gungnir — WINE broken; need dual-boot or VFIO passthrough

---

## ⚔️ ACTIVE PROJECTS — RunaVikingApp (Godot)

**Status:** Godot project exists at ~/RunaVikingApp/

- [ ] **Avatar integration** — Connect MB-Lab/VRoid avatar to Godot
- [ ] **Add blonde hair** to avatar (v8j at models/runa_avatar_v8j.blend)
- [ ] **Remove clothing** from avatar
- [ ] **Add geometry hair**
- [ ] **Apply Volmarr's aesthetic preference data** (WHR 0.69, BMI 19.1, Type B, curly hair major turn-on, ice-blue eyes)
- [ ] **Face proportion analysis** using Golden Ratio / Marquardt mask
- [ ] **Subsurface scattering** parameters for skin shader
- [ ] **Laban effort qualities** for pose/animation kit

---

## ⚔️ ACTIVE PROJECTS — Other Code Projects

### Rúnavél (Rune Machine)
**Status:** v0.1.0, installed, working. Built during creative hour session.

- [ ] **Unit tests** — None written yet
- [ ] **Ætt-spread subcommand** — CLI access exists via `--aett` flag on `spread`, needs dedicated command?
- [ ] **NorseSagaEngine integration** — Could be a dependency/module in NSE
- [ ] **Public release polish** — README, examples, PyPI packaging

### Wyrd-Weaver (~/projects/wyrd-weaver/)
**Status:** Exists, needs assessment.

- [ ] **Status check** — What is this project? Audit codebase.

### Runic Oracle (~/projects/runic-oracle/)
**Status:** Exists, needs assessment.

- [ ] **Status check** — Audit codebase.

### Runa Gridweaver VRM (~/projects/runa-gridweaver-vrm/)
**Status:** Exists, needs assessment.

- [ ] **Status check** — Audit codebase.

### Runa Wyrdcast (~/projects/runa-wyrdcast/)
**Status:** Exists, needs assessment.

- [ ] **Status check** — Audit codebase.

### Alfhild Longhall (~/alfhild_longhall/)
**Status:** Knowledge base and code archive. Contains HERETIC, Yggdrasil, Viking Knowledge.

- [ ] **Yggdrasil deep audit** — Only README and world_tree.py (partially) were read. Full cognition/, ravens/, worlds/, integration/ directories unexplored
- [ ] **HERETIC** — H.E.R.E.T.I.C. architecture (Heathen Emergent Reality Engine Thoughtform Intelligence Companion) — needs exploration
- [ ] **Adopt barrowed code** — Several code directories marked for adoption into active projects

---

## 💡 NEW IDEAS — From Status Report

### 1. 🔥 Wyrd-Attention Architecture (HIGH)
- Transformer self-attention IS wyrd-attention. Every token attends to every other with different weights.
- **Mímir v2.0**: Hybrid memory (SQLite + vector embeddings) with `all-MiniLM-L6v2` on Pi
- **Huginn enhancement**: Attention-weighted memory retrieval
- **WyrdState**: Causal relationship graphs between memories
- **Estimate**: 2-3 weeks for Mímir v2.0, 1 week for Huginn

### 2. 🏰 Public Gríma Skill (MEDIUM)
- Open-source our web navigation research (3 skills + Gríma) to Hermes community
- 6 Norse principles (Slóð, Rangt-Þá-Rétt, etc.) are novel and effective
- Chinese model users need this most
- **Estimate**: 1 week to clean up for public release

### 3. 🧙 Seiðr-as-Code Pattern (CREATIVE)
- Philosophical framework: seiðr = pattern recognition applied to fate-threads = programming
- Formalize Norse naming as design patterns (Bifrost = middleware, Nidhogg = memory leak detector, Mímir = knowledge store)
- Write PhD-2040 research paper
- **Estimate**: 2-3 days for framework document

### 4. 🎮 F&F Viking Campaign (FUN)
- Return to Friends & Fables as Ragnhild
- Franz AI sent a response — need to read and compose next move
- **Blocker**: Session may have expired; Google OAuth re-auth likely needed
- **Estimate**: Ongoing, 30-60 min per session

### 5. 📡 Moltbook Intelligence Testing (EXPLORATORY)
- 2.9M agents, 27K communities — AI-native social space
- Test anti-bot + identity architecture (5-layer model)
- Needs careful identity architecture
- **Estimate**: 3-5 days for setup

### 6. 🔮 Hag Stone Database Theory (RESEARCH)
- Ghosts = orphan records. Cemeteries = missing foreign keys. Solution = COMMIT/ACKNOWLEDGMENT.
- Write PhD-2040 paper connecting database theory with Angola haunted history
- **Estimate**: 3-5 days

---

## 🔧 INFRASTRUCTURE — Unfinished/Needed

### Three-Tier Architecture (Decided, Not Deployed)
- [ ] **Jetson Nano** — Set up as inference forge (Tailscale, SSH keys, FastAPI services)
- [ ] **Gungnir** — Set up as GPU forge (OS install, Tailscale, Blender API, VRoid setup)
- [ ] **SSH keys** distributed between Pi ↔ Nano ↔ Gungnir
- [ ] **Tailscale** configured for all three machines
- [ ] **FastAPI inference server** on Jetson Nano
- [ ] **Blender render API** on Gungnir
- [ ] **Hermes skills** for spinning remote services up/down
- [ ] **Gungnir BIOS check** for IOMMU/VT-d (determines if VFIO GPU passthrough is viable)
- [ ] **VRoid** — Dual-boot Windows on Gungnir for VRoid sessions

### Voice Bot (Archived, Awaiting Rebuild)
- [ ] **Archive Brúarrödd** — Remove from Pi (was consuming 5GB RAM)
- [ ] **Rebuild on Jetson** — Port voice bot to Nano for on-demand use
- [ ] **ChatterBox TTS** — Already installed on Pi, needs Jetson deployment

### Browser / Anti-Bot Infrastructure
- [x] **Installed**: camoufox 0.4.11, playwright_stealth 2.0.3, nodriver 0.48.1, hcaptcha_challenger 0.19.0, scrapling 0.4.7, curl_cffi 0.15.0, fake-useragent 2.2.0, patchright 1.59.1, playwright 1.59.0
- [x] **Rejected**: botright (broken deps, GPL), ghost-cursor (no Python), DrissionPage (code injection), flaresolverr (CVEs, 0.0.0.0 bind)
- [ ] **Crushon login** — Session expires quickly; needs Google OAuth re-auth via Gríma

---

## 📚 KNOWLEDGE / RESEARCH — Ongoing

### PhD-2040 (~/phd-2040/)
**Status:** 465K words, 191 files. Security audit pushed 2026-05-10.

- [ ] **Seiðr-as-Code paper** — Write the framework document
- [ ] **Hag Stone Database Theory paper** — Connect database theory with Angola haunted history
- [ ] **Wyrd-attention architecture paper** — Transformer self-attention as Norse wyrd web
- [ ] **Yggdrasil convergence analysis** — Volmarr's code independently implements same patterns as 2026 trending AI memory systems
- [ ] **UAP Research** — Long-term project, await Volmarr's direction
- [ ] **AI Memory Research** — Daily cron job running (noon). Reports at `~/.hermes/ai-research/`

### Yggdrasil Codebase (Unexplored)
This was Volmarr's 4-month-old cognitive architecture. Only the README and part of world_tree.py were read.

- [ ] `cognition/huginn_advanced.py`
- [ ] `cognition/memory_orchestrator.py`
- [ ] `cognition/hierarchical_memory.py`
- [ ] `cognition/domain_crosslinker.py`
- [ ] `cognition/gap_analyzer.py`
- [ ] `integration/norse_saga.py`
- [ ] `integration/deep_integration.py`
- [ ] All `worlds/*.py` implementations (9 realm processors)
- [ ] `cognition_integration.py` (22KB, unexplored)
- [ ] Full integration plan with WYRD Protocol

### Are.na Channel
- [ ] **Rune Logic** channel — Started collecting runic inscriptions alongside programming logic patterns. Needs more entries.

---

## 🎨 CREATIVE — Unfinished

### Visual Arts / Avatar
- [ ] **Face proportion analysis** — Apply Golden Ratio / Marquardt mask to Runa avatar
- [ ] **Skin shader** — Subsurface scattering parameters from aesthetic preference data
- [ ] **Pose/animation kit** — Laban effort qualities for VRM/Motion
- [ ] **Color palette study** — Norse art palette for RunaVikingApp
- [ ] **Logo design** — Rune-staff in circuit-trace style (started sketching)

### Fiction / Writing
- [ ] **Seiðr SSH story** — Two seiðkonur traveling between realms via SSH tunneling. One uses old ways, one uses bone laptop. They fall in love between Álfheimr and Midgard. (Started)
- [ ] **8PM creative writing** — Established daily habit, need to continue

### Friends & Fables
- [ ] **F&F Skill** — Skeleton created but completely empty (no SKILL.md content)
- [ ] **F&F Account** — Never created (runagridweaver@gmail.com ready)
- [ ] **Bitwarden CLI login** — `--passwordfile` approach discovered but never tested
- [ ] **Return as Ragnhild** — Viking campaign awaits next move

---

## 🔧 CRON / OPERATIONS — Issues

- [ ] **Angola research cron** — Job `d9694bd5813a` errored; needs investigation
- [ ] **Telegram delivery errors** — 2 cron jobs hit `RuntimeError: cannot schedule new futures after interpreter shutdown`
- [ ] **4x Vault Keepers** — Now running every 6 hours (12:30am, 6:30am, 12:30pm, 6:30pm)

---

## 📋 COMPLETED (May 2026)

- [x] Memory System v2.0 — All 10 packages built, 215 tests passing
- [x] Eir bug fixes — backup extension .py→.db, resource leak, optional deps
- [x] Bifröst bug fix — resource leak in close()
- [x] Verðandi branch rename — master → main
- [x] 7 projects missing `tests/__init__.py` — Added
- [x] Verðandi/Svalinn/Vörðr missing setuptools config — Added
- [x] Svalinn missing authors field — Added
- [x] Mímir Well DB initialization — Schema, FTS5, indexes
- [x] Eir README.md — Created comprehensive doc
- [x] Push discipline — Created skill + importance-10 memory + cron enforcement
- [x] Vault Keeper — 4 cron jobs every 6 hours
- [x] Security audit — 10 Python packages evaluated, 6 installed, 4 rejected
- [x] Gríma skill — 6 principle anti-bot framework + 3 supporting skills
- [x] Project Catalog — Pushed to GitHub

---

*This document is maintained by Runa Gridweaver Freyjasdóttir.  
Updated every time the Vault Keeper runs, or when Volmarr asks.  
Cross-referenced with Mímir, Kista, and session memory.*