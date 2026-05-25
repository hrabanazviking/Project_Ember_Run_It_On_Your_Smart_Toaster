---
name: sap-codex-manifest
description: Authoritative list of all 82 documents in the SAP Codex, with slugs, scope, owner role, and target length
metadata:
  codex: sap
  type: meta
---

# MANIFEST — Super Agent Party Codex

**Total docs:** 82 (77 content + 5 meta)
**Target length:** 1,500–4,000 words each (per-IM-bot and per-livestream subdocs may run 1,200–2,500)
**Citation convention:** `path:line` from `/tmp/super-agent-party/`
**Closer:** every content doc ends with `## What This Means for Ember`

---

## meta/ (5 docs — Scribe)

| Slug | Title | Status |
|---|---|---|
| (root) | `TASK_SUPER_AGENT_PARTY_CODEX.md` | ✅ written |
| meta/SHARED_CONTEXT | Shared briefing for all agents | ✅ written |
| meta/MANIFEST | This file | ✅ written |
| meta/STYLE_GUIDE | Tone, length, citation, closer format | ✅ written |
| meta/INDEX | Final cross-link index (written last) | ⏳ pending |
| meta/READING_ORDER | Suggested traversal order | ⏳ pending |
| meta/CROSS_AGENT_NOTES | Notes between agents during authoring | ⏳ pending |

---

## 00_vision/ (5 docs — Skald)

| # | Slug | Scope |
|---|---|---|
| 00 | OVERTURE | Why mine SAP after Hermes + Peer; the embodiment-reach-affect gap |
| 01 | SAP_ESSENCE | What SAP is at the level of intent: companion-as-presence, party-as-plurality |
| 02 | THE_PARTY_METAPHOR | "Party" decoded — multi-agent + multi-device + multi-channel as the same idea |
| 03 | ANTI_SAP | What SAP refuses or fails to be; what Ember must refuse (surveillance, gacha-affect, China-default surface) |
| 04 | VISION_SYNTHESIS | Ember's identity revised post-SAP study |

---

## 10_domain/ (14 docs — Architect)

| # | Slug | Scope |
|---|---|---|
| 10 | DOMAIN_MAP | SAP's macro architecture: main.js → server.py → py/ modules; dependency graph |
| 11 | AVATAR_DOMAIN | VRM + Live2D + VTube Studio + VMC: embodiment subsystem |
| 12 | AGENT_CORE_DOMAIN | `agent.py` + `sub_agent.py` + `task_center.py` + `scheduler.py`: reasoning + delegation |
| 13 | COMPUTER_CONTROL_DOMAIN | `computer_use_tool.py` + `cdp_tool.py` + `cli_tool.py`: how SAP touches the host |
| 14 | MESSAGING_DOMAIN | The 8 IM bot managers as a class — unified-or-fragmented analysis |
| 15 | BROADCAST_DOMAIN | `blivedm/` + `ytdm.py` + `twitch_service.py` + livestream avatar pipeline |
| 16 | VOICE_DOMAIN | `moss_tts.py` + `sherpa_asr.py` + model managers: duplex voice stack |
| 17 | RETRIEVAL_DOMAIN | `know_base.py` + `minilm_router.py` + `ebd_api.py` + `ebd_model_manager.py` |
| 18 | EXTENSION_DOMAIN | `extensions.py` + `skills.py` + creators: user-extensibility surface |
| 19 | TOOL_DOMAIN | `agent_tool.py` + `utility_tools.py` + `task_tools.py` + `llm_tool.py` + `web_search.py` |
| 1A | AFFECTION_DOMAIN | `affection_api.py` + `affection_system.py` + `autoBehavior.py` + `behavior_engine.py` |
| 1B | DEPLOYMENT_DOMAIN | `node_runner.py` + `node_api.py` + `uv_api.py` + `docker_api.py` + builds |
| 1C | SCHEDULER_DOMAIN | `scheduler.py` + `sleep_guard.py` + `random_topic.py`: autonomous timing |
| 1D | ROUTING_DOMAIN | `overlay_router.py` + `live_router.py` + `mode_change.py` + `ws_manager.py`: the multiplexing fabric |

---

## 20_interface/ (12 docs — Architect: 6, Auditor: 6)

| # | Slug | Owner | Scope |
|---|---|---|---|
| 20 | MCP_INTEGRATION | Architect | `mcp_clients.py` + MCP server exposure: bidirectional MCP |
| 21 | OPENAI_COMPAT_API | Auditor | `ClaudeAsOpenAI.py` + `GeminiAsOpenAI.py` + `dify_openai.py`: simulation layer and its leaks |
| 22 | A2A_INTERFACE | Architect | `a2a_tool.py`: agent-to-agent protocol |
| 23 | SKILL_INTERFACE | Architect | `skills.py` + skill manifest format |
| 24 | EXTENSION_INTERFACE | Architect | `extensions.py` + extension manifest format |
| 25 | AVATAR_PROTOCOL | Architect | VMC bidirectional + VRM action surface + `vts_manager.py` |
| 26 | IM_BOT_INTERFACE | Auditor | Unified-or-not abstraction across the 8 IM bot managers |
| 27 | STREAMING_INTERFACE | Auditor | Livestream protocols: comments→AI→avatar→stream; OBS sink |
| 28 | BROWSER_AUTOMATION_INTERFACE | Auditor | CDP + LLM-visual-reasoning single-step approach |
| 29 | TOOL_TYPE_INTERFACE | Auditor | `code_interpreter.py` + `comfyui_tool.py` + `custom_http.py` + `computer_use_tool.py` |
| 2A | VOICE_INTERFACE | Architect | TTS + ASR protocol surface; streaming voice patterns |
| 2B | RETRIEVAL_INTERFACE | Auditor | Embedding + KB query interface; `minilm_router.py` routing logic |

---

## 30_execution/ (23 docs — Forge-A: core 12, Forge-B: per-platform 11)

### 30_execution/ — Forge-A (core 12)

| # | Slug | Scope |
|---|---|---|
| 30 | ELECTRON_BOOTSTRAP | `main.js` (70k bytes): lifecycle, IPC bridge, window management |
| 31 | PYTHON_SERVER | `server.py` (~10k LOC): single-file Python backbone — routes, state, dispatch |
| 32 | AVATAR_RENDER_PIPELINE | VRM + Live2D rendering, scene composition, transparency-to-OBS |
| 33 | COMPUTER_CONTROL_LOOP | Vision → action → verify; closing the loop without crashing the host |
| 34 | BROWSER_AUTOMATION_LOOP | CDP session lifecycle; per-step LLM visual reasoning |
| 35 | IM_BOT_DEPLOYMENT_OVERVIEW | One-click deployment mechanics — what's shared, what's per-platform |
| 36 | LIVESTREAM_INGEST_OVERVIEW | Comment → topic router → AI → avatar → stream; latency budget |
| 37 | MCP_LIFECYCLE | MCP server registration, start, health, cleanup |
| 38 | EXTENSION_LIFECYCLE | Extension install, sandbox, load, multi-instance, unload |
| 39 | DOCKER_TOPOLOGY | `docker-compose.yml` + ACR variant + gateway + auth |
| 3A | CROSS_PLATFORM_BUILDS | Electron Builder + PyInstaller + AppImage + .deb + .dmg + portable .zip |
| 3B | AFFECTION_LOOP | How `affection_system` runs: state, decay, triggers, autoBehavior coupling |

### 30_execution/ — Forge-B (per-platform 11)

| # | Slug | Scope |
|---|---|---|
| 35a | IM_QQ_BOT | `qq_bot_manager.py`: QQ deployment, message types, group-vs-private |
| 35b | IM_WECHAT_BOT | `wechat_bot_manager.py`: WeChat personal account deployment |
| 35c | IM_WECOM_BOT | `wecom_bot_manager.py`: Enterprise WeChat |
| 35d | IM_FEISHU_BOT | `feishu_bot_manager.py`: Feishu (Lark) deployment |
| 35e | IM_DINGTALK_BOT | `dingtalk_bot_manager.py`: DingTalk deployment |
| 35f | IM_TELEGRAM_BOT | `telegram_bot_manager.py` + `telegram_client.py`: Telegram bot vs client API |
| 35g | IM_DISCORD_BOT | `discord_bot_manager.py`: Discord deployment, slash commands |
| 35h | IM_SLACK_BOT | `slack_bot_manager.py`: Slack deployment |
| 36a | LIVESTREAM_BILIBILI | `blivedm/`: Bilibili live-comment ingest |
| 36b | LIVESTREAM_YOUTUBE | `ytdm.py`: YouTube live integration |
| 36c | LIVESTREAM_TWITCH | `twitch_service.py`: Twitch IRC + EventSub |

---

## 50_verification/ (10 docs — Auditor)

| # | Slug | Scope |
|---|---|---|
| 50 | SELF_HEALING_PATTERNS | What fault tolerance exists; what survives crash; what doesn't |
| 51 | CRASH_RESISTANCE | Per-subsystem failure modes — IM disconnect, livestream timeout, render fail, MCP crash |
| 52 | RESOURCE_BUDGETS | Memory + CPU + GPU usage; how SAP scales 2GB → multi-GPU |
| 53 | SECURITY_REVIEW | Computer control + smart home + 8 IM bots = attack surface; threat model |
| 54 | DEPENDENCY_HEALTH | Electron + Python + sherpa + moss + 8 IM SDKs + ComfyUI: brittleness map |
| 55 | API_SIMULATION_TRAPS | Where Claude/Gemini-as-OpenAI leak; token counting, tool calls, system prompt |
| 56 | PRIVACY_BOUNDARIES | Long-term memory + livestream + 8 IM bots: privacy minefield catalog |
| 57 | FAILURE_TAXONOMY | Categorized failure modes ranked impact × likelihood |
| 58 | OBSERVABILITY_GAPS | What SAP can't see about itself; what Ember must surface |
| 59 | CONFIG_DRIFT | `settings_template.json` analysis + long-tail config surface; mutation risks |

---

## 60_synthesis/ (13 docs — Cartographer: 6, Scribe: 7)

| # | Slug | Owner | Scope |
|---|---|---|---|
| 60 | TRUE_NAME_REASSIGNMENT | Cartographer | How SAP findings reshape Ember's True Names; proposed new names Andlit/Rödd/Hugarsýn |
| 61 | NEW_VOWS | Cartographer | Embodied Honesty, Surface Without Surveillance, Affective Restraint, Tiered Presence, Federated Self |
| 62 | PARTY_PROTOCOL | Cartographer | Ember's invented multi-device orchestration protocol — federated, leader-elected, peer-respecting |
| 63 | PERFORMANCE_TIER_ENGINE | Cartographer | Pi/laptop/workstation adaptive runtime — feature gating by host capability |
| 64 | AFFECTION_ENGINE_REIMAGINED | Cartographer | Emotional intelligence WITHOUT gacha mechanics |
| 65 | META_AWARENESS | Cartographer | Self-awareness as introspectable telemetry; Hugarsýn (mind-sight) surface |
| 66 | INVENTED_METHODS | Scribe | Novel patterns NOT in SAP — cross-host affect routing, low-power VRM stand-in, semantic IM fallback, party-leader migration |
| 67 | SLICE_PLAN_REVISIONS | Scribe | Proposed revisions to ratification-gated slice plan (PROPOSE ONLY) |
| 68 | DECISION_RECORDS | Scribe | ADRs for the most consequential adoption decisions |
| 69 | INTEGRATION_ROADMAP | Scribe | Cross-codex: SAP × Hermes × Peer × Yggdrasil × Stofa |
| 6A | MULTI_AGENT_PARTY | Scribe | Extending PARTY_PROTOCOL to multi-Ember swarming; consensus, identity, divergence |
| 6B | LOW_POWER_EMBODIMENT | Scribe | Pi/phone presence without VRM rendering — text-only / log-only tiers |
| 6C | EMBER_WAVE_3_SLICE | Scribe | Proposed Wave 3 slice plan based on SAP findings (post-ratification roadmap) |

---

## Agent Layer Assignments — final

| Agent | Role | Folders | Doc count |
|---|---|---|---|
| 1 | **Skald** — Sigrún Ljósbrá | `00_vision/` | 5 |
| 2 | **Architect** — Rúnhild Svartdóttir | `10_domain/` + 6 of `20_interface/` (Architect-owned) | 14 + 6 = 20 |
| 3 | **Cartographer** — Védis Eikleið | 6 of `60_synthesis/` (Cartographer-owned) | 6 |
| 4 | **Forge-A** — Eldra Járnsdóttir, fire-instance | `30_execution/` core 12 | 12 |
| 5 | **Forge-B** — Eldra Járnsdóttir, iron-instance | `30_execution/` per-platform 11 | 11 |
| 6 | **Auditor** — Sólrún Hvítmynd | `50_verification/` + 6 of `20_interface/` (Auditor-owned) | 10 + 6 = 16 |
| 7 | **Scribe** — Eirwyn Rúnblóm | 7 of `60_synthesis/` (Scribe-owned) + final `meta/` (INDEX, READING_ORDER, CROSS_AGENT_NOTES) | 7 + 3 = 10 |

**Total dispatch:** 7 parallel agents (six roles, Forge doubled) → 82 docs.

**Push cadence:** each agent commits + pushes once its layer is complete (per-layer push). Scribe waits for all other layers before writing final INDEX + READING_ORDER, then pushes.

---

## Reading Order (preliminary — Scribe finalizes in `meta/READING_ORDER.md`)

1. `meta/SHARED_CONTEXT` (you are here, conceptually)
2. `00_vision/00_OVERTURE` → `04_VISION_SYNTHESIS`
3. `10_domain/10_DOMAIN_MAP`
4. Domain doc of interest (`1A_AFFECTION_DOMAIN`, `11_AVATAR_DOMAIN`, `14_MESSAGING_DOMAIN`, etc.)
5. Matching interface + execution docs (e.g. AFFECTION → `3B_AFFECTION_LOOP` → `64_AFFECTION_ENGINE_REIMAGINED`)
6. `50_verification/57_FAILURE_TAXONOMY` for the threat-shaped view
7. `60_synthesis/*`
8. `60_synthesis/69_INTEGRATION_ROADMAP` last

---

## Slug Glossary (cross-codex prefix)

- `[[hermes:<slug>]]` → `docs/hermes_codex/`
- `[[peer:<slug>]]` → `docs/peer_codex/`
- `[[ember:<slug>]]` → `~/ai/ember/` root or `docs/` root
- `[[sap:<slug>]]` → this codex (also bare `[[slug]]` resolves within-codex)
