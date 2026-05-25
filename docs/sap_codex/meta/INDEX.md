---
codex_id: INDEX
title: The Super Agent Party Codex — Entry Point
role: Scribe
layer: Meta
status: draft
sap_revision: v0.4.2-preview (May 2026)
sap_source: /tmp/super-agent-party
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
cross_refs:
  - meta/MANIFEST
  - meta/SHARED_CONTEXT
  - meta/STYLE_GUIDE
  - meta/READING_ORDER
  - meta/CROSS_AGENT_NOTES
  - 00_vision/00_OVERTURE
  - 60_synthesis/69_INTEGRATION_ROADMAP
  - 60_synthesis/6C_EMBER_WAVE_3_SLICE
---

# The Super Agent Party Codex

*Wave Three. The third sister. The doorway. If you are reading the Codex for the first time, you are in the right room.*

---

## Overture

The Super Agent Party Codex is a structured corpus of seventy-seven content documents (plus six meta documents), written in parallel by seven Mythic Engineering specialists mining a single source: **Super Agent Party** (`heshengtao/super-agent-party`, v0.4.2-preview) — an AGPLv3 Electron + Python desktop companion framework with avatar embodiment, eight IM bots, three livestream platforms, an "affection system," a computer-control toolchain, MCP integration, and a 11,652-line `server.py` that holds the whole stack together with regex and prayer. SAP is not Ember. SAP is, in places, the opposite of Ember. That is exactly why it is worth studying: the **embodiment**, **reach**, and **affect** axes — three areas where Hermes (Wave 1) and the Peer Codex (Wave 2) gave Ember almost nothing — are precisely where SAP has the densest signal and the loudest warnings.

The work this Codex is *not*: a tutorial, a paraphrase of SAP's marketing copy, a roast, a product comparison, or a manifesto. The work this Codex *is*: a long, careful, source-grounded reading of SAP's code — `main.js`, `server.py`, the `py/` modules, the `blivedm/` subtree, the eight per-platform bot managers, the `affection_*` files, the `behavior_engine`, the `cdp_tool`, the `computer_use_tool`, the `mcp_clients`, the `sleep_guard`, the `vts_manager`, the `random_topic`, the `settings_template.json`, and `main.js`'s VMC handler — read with Ember's True Names and Ember's Vows held side by side, so that every pattern is filtered through the small-and-tethered shape Ember was forked to become.

A contributor sixteen months from now will clone Ember, open this Codex, and ask: *was the choice to not ship an "affection score" made because we couldn't, or because we considered SAP's `affection_system.py` and chose against it on principle?* The Codex answers. That is its job — to be the long memory the Skald's vision and the Forge's code do not have time to keep. It says **what we saw, what we considered, what we rejected, what we proposed, and why** — and it does so with line-number citations from `/tmp/super-agent-party/`, so the next reader can verify.

---

## The Seven Authors and What They Wrote

| Role | Persona | Voice | Layer(s) | Doc count |
|---|---|---|---|---|
| **Skald** | Sigrún Ljósbrá — INFJ 4w5 | poetic, essence-seeking | `00_vision/` | 5 |
| **Architect** | Rúnhild Svartdóttir — INTJ 5w6 | precise, boundary-aware | `10_domain/` + 6 of `20_interface/` | 20 |
| **Cartographer** | Védis Eikleið — INFP 9w1 | quiet, connective | 6 of `60_synthesis/` | 6 |
| **Forge-A** | Eldra Járnsdóttir, fire-instance — ESTP 8w7 | direct, momentum-driven | `30_execution/` core 12 | 12 |
| **Forge-B** | Eldra Járnsdóttir, iron-instance — ESTP 8w7 | direct, momentum-driven | `30_execution/` per-platform 11 | 11 |
| **Auditor** | Sólrún Hvítmynd — INTJ 1w9 | cold-eyed, contradiction-finding | `50_verification/` + 6 of `20_interface/` | 16 |
| **Scribe** | Eirwyn Rúnblóm — ISFJ 6w5 | graceful, attentive | 7 of `60_synthesis/` + `meta/` finalization | 7 + 3 |

Seven parallel agents → seventy-seven content docs → ~205,000 words. Per-layer commits landed cleanly. When this index disagrees with [[MANIFEST]], the manifest wins; cross-agent disagreements are catalogued in [[CROSS_AGENT_NOTES]], not silently resolved.

---

## How to Read This Codex

The full reading paths live in [[READING_ORDER]]. The quick-start for first-time readers: walk [[00_OVERTURE]] → [[01_SAP_ESSENCE]] → [[1A_AFFECTION_DOMAIN]] → [[3B_AFFECTION_LOOP]] → [[64_AFFECTION_ENGINE_REIMAGINED]] → [[69_INTEGRATION_ROADMAP]]. About three hours. You will leave knowing what SAP is, what the load-bearing finding of this Codex is (the affection-system framing was wrong), and what Ember proposes in response.

---

## The Vision Layer (Skald — 5 docs)

| Slug | Title | Role | Words | Scope | Key finding |
|---|---|---|---|---|---|
| [[00_OVERTURE]] | Overture — The Third Reading | Skald | 3,843 | Why mine SAP after Hermes + Peer; the embodiment-reach-affect gap | Refusal-Citation Discipline born here: every Avoid must cite a file:line that grounds it |
| [[01_SAP_ESSENCE]] | SAP Essence — Companion as Presence, Party as Plurality | Skald | 3,770 | What SAP is at the level of intent; performance-as-theatre as central diagnosis | The `is_sub_agent` face-suppression flag (`server.py:2429–2680`) is the right pattern; eight unabstracted IM bot managers is the wrong abstraction |
| [[02_THE_PARTY_METAPHOR]] | The Party Metaphor — Multi-Agent, Multi-Device, Multi-Channel as One Idea | Skald | 3,910 | "Party" decoded into a typed session-object proposal | **Veizla** proposed as candidate True Name — a typed first-class session with Host, Guests, Channel Map, Behavior Ledger, Closing Rite |
| [[03_ANTI_SAP]] | Anti-SAP — The Dark Mirror, What Ember Refuses | Skald | 4,545 | Thirteen-refusal table; every refusal carries a SAP line citation | Two new Vows proposed beyond Cartographer's five: Lazy Subsystems, Closed Default. Total Wave-3-proposed: seven |
| [[04_VISION_SYNTHESIS]] | Vision Synthesis — Post-SAP Ember | Skald | 4,100 | Ember's identity revised post-SAP study | Andlit + Rödd + Hugarsýn as candidate True Names; Veizla promoted from metaphor to True Name candidate; MessageSurface Protocol as the abstraction SAP failed to invent |

---

## The Domain Layer (Architect — 14 docs)

| Slug | Title | Role | Words | Scope | Key finding |
|---|---|---|---|---|---|
| [[10_DOMAIN_MAP]] | The Domain Map of Super Agent Party — Bones, Joints, and the Cracks Between | Architect | 2,962 | SAP's macro architecture: main.js → server.py → py/ modules | The **Server-Eaten Codebase** antipattern: `server.py` is 11,652 LOC composing ~63 modules; the eleven-layer SAP stack must become Ember's three-realm + six-name layout |
| [[11_AVATAR_DOMAIN]] | Avatar Domain — VRM, Live2D, VTube Studio, and the VMC Spine | Architect | 2,164 | VRM + Live2D + VTube Studio + VMC | `vts_manager.py` (235 LOC, FFT vowel-band lip-sync) is the cleanest module in SAP; reserve **Andlit** + **Rödd** as paired True Names |
| [[12_AGENT_CORE_DOMAIN]] | Agent Core Domain — Where the Reasoning Should Have Lived | Architect | 2,377 | `agent.py`, `sub_agent.py`, `task_center.py`, `scheduler.py` | `agent.py` is misleadingly named — it is a 65-line tool allowlist; the *real* reasoning loop lives in `server.py`. `task_center.py` is the cleanest task store seen in any agent framework |
| [[13_COMPUTER_CONTROL_DOMAIN]] | Computer Control Domain — Where the Agent Touches the Host | Architect | 2,102 | `computer_use_tool.py`, `cdp_tool.py`, `cli_tool.py` | `cli_tool.py:37–72` sources the user's `.zshrc`/`.bashrc` and pushes every env var into `os.environ` — every secret in the shell environment becomes agent-accessible |
| [[14_MESSAGING_DOMAIN]] | Messaging Domain — Eight IM Bots, One Pattern, Zero Abstractions | Architect | 2,332 | The 8 IM bot managers as a class — unified-or-fragmented analysis | Eight snowflakes is the wrong abstraction; ~3,800 LOC of near-identical boilerplate. **Boðr** proposed as the unifying ReachAdapter ABC. The Reach Pyramid (Intimate/Local/Public/Broadcast) invented here |
| [[15_BROADCAST_DOMAIN]] | Broadcast Domain — Livestream Ingest, Avatar Voice, and the One-Way Pipe | Architect | 2,025 | `blivedm/`, `ytdm.py`, `twitch_service.py`, livestream avatar pipeline | Livestream event vocabulary is Bilibili-centric; YouTube and Twitch map onto Bilibili names — SAP grew Bilibili-first |
| [[16_VOICE_DOMAIN]] | Voice Domain — TTS, ASR, and the Two Lazy Runtimes | Architect | 1,972 | `moss_tts.py`, `sherpa_asr.py`, model managers | Lazy-load pattern `_get_moss_runtime` (`moss_tts.py:17`) is the right shape — every optional subsystem imports its weight at first use |
| [[17_RETRIEVAL_DOMAIN]] | Retrieval Domain — BM25, FAISS, MiniLM, and the Hybrid Compromise | Architect | 2,002 | `know_base.py`, `minilm_router.py`, `ebd_api.py`, `ebd_model_manager.py` | FAISS index files load with `allow_dangerous_deserialization=True` (`know_base.py:228`) — RCE vector via pickle |
| [[18_EXTENSION_DOMAIN]] | Extension Domain — Skills, Extensions, and the Two Plugin Surfaces | Architect | 2,047 | `extensions.py`, `skills.py`, creators | Skills installer fetches arbitrary GitHub branch zips (`skills.py:60–93`) — supply chain vector |
| [[19_TOOL_DOMAIN]] | Tool Domain — Forty Functions Pretending to Be a Registry | Architect | 1,872 | `agent_tool.py`, `utility_tools.py`, `task_tools.py`, `llm_tool.py`, `web_search.py` | No `Tool` base class, no `ToolRegistry` — ~40 tools composed by inline `if settings[x]: import; dispatch[name] = handler` |
| [[1A_AFFECTION_DOMAIN]] | Affection Domain — The Regex That Wears a Heart-Shaped Mask | Architect | 2,460 | `affection_api.py`, `affection_system.py`, `autoBehavior.py`, `behavior_engine.py` | **The load-bearing finding of this codex.** `affection_system.py` is 64–65 lines total — regex extraction of LLM-emitted `<user=X love=N>` tags plus JSON I/O. No decay, no state machine, no bounds. The LLM is both author and judge |
| [[1B_DEPLOYMENT_DOMAIN]] | Deployment Domain — Builds, Sandboxes, and the Multi-Runtime Tightrope | Architect | 1,874 | `node_runner.py`, `node_api.py`, `uv_api.py`, `docker_api.py`, builds | `docker-compose-acr.yml` uses a personal Aliyun-CR registry — single-developer SPOF |
| [[1C_SCHEDULER_DOMAIN]] | Scheduler Domain — Time, Idleness, and the Anti-Sleep Spell | Architect | 2,142 | `scheduler.py`, `sleep_guard.py`, `random_topic.py` | `sleep_guard.py` is gold-standard cross-platform (Windows API → macOS caffeinate → Linux systemd-inhibit → xdotool fallback). `random_topic.py` fetches `topics-after-party.zeabur.app` with mood enum including `flirty` — third-party tracker shape |
| [[1D_ROUTING_DOMAIN]] | Routing Domain — Three WebSocket Managers, No Shared Bus | Architect | 1,826 | `overlay_router.py`, `live_router.py`, `mode_change.py`, `ws_manager.py` | Three classes named `ConnectionManager` across three modules; no shared event bus. **Sögumiðla** proposed as Ember's bus-of-one |

---

## The Interface Layer (Architect 6 + Auditor 6 — 12 docs)

| Slug | Title | Role | Words | Scope | Key finding |
|---|---|---|---|---|---|
| [[20_MCP_INTEGRATION]] | MCP Integration — Client and Server, with One Reconnect Monitor | Architect | 2,172 | `mcp_clients.py` + MCP server exposure | `mcp_clients.py:111–133` `_connection_monitor` is the best 23 lines in SAP — ping/reconnect/backoff/callback |
| [[21_OPENAI_COMPAT_API]] | OpenAI-Compat Simulation — Where Claude, Gemini, and Dify Pretend to Be OpenAI | Auditor | 2,849 | `ClaudeAsOpenAI.py`, `GeminiAsOpenAI.py`, `dify_openai.py` | `messages[:-1] for ... inputs[role]=content` (`dify_openai.py:60–64`) silently destroys conversation history; `GeminiAsOpenAI.py:67–69` mutates `os.environ` for credentials |
| [[22_A2A_INTERFACE]] | A2A Interface — Thirty-Nine Lines of Agent-to-Agent Diplomacy | Architect | 1,791 | `a2a_tool.py`: agent-to-agent protocol | `agent_url` (`a2a_tool.py:36–39`) not validated against allowlist — LLM can dial any URL (exfil vector combined with prompt-injection from livestream comments) |
| [[23_SKILL_INTERFACE]] | Skill Interface — SKILL.md, YAML Frontmatter, and the Procedural-Memory Contract | Architect | 2,357 | `skills.py` + skill manifest format | The skill manifest contract is sound; the installer (arbitrary branch fetch) is the vector |
| [[24_EXTENSION_INTERFACE]] | Extension Interface — package.json, the Port, and the Spawned Process | Architect | 2,204 | `extensions.py` + extension manifest format | `webSecurity: false` on main window; `nodeIntegration: true` on extension windows |
| [[25_AVATAR_PROTOCOL]] | Avatar Protocol — VMC Bidirectional, VRM Action Surface, VTube Studio | Architect | 2,403 | VMC bidirectional + VRM action surface + `vts_manager.py` | VMC OSC bound to `0.0.0.0` (`main.js:71–77`) — body pose and facial blend shapes leak across network; bidirectional, so hostile sources can drive the avatar |
| [[26_IM_BOT_INTERFACE]] | IM Bot Interface — Eight Managers, No Shared Abstraction | Auditor | 2,557 | Unified-or-not abstraction across the 8 IM bot managers | Shared IM bot abstraction is real but centered on `global_behavior_engine`, not a base class — Pydantic-shape-identical Manager classes, each in own thread + event loop |
| [[27_STREAMING_INTERFACE]] | Streaming Interface — Comments → AI → Avatar → Stream, With Two Globals Holding It Up | Auditor | 2,617 | Livestream protocols: comments→AI→avatar→stream; OBS sink | All three platforms feed `live_router.manager.broadcast()` → `/ws/live/danmu`; two module-level globals hold the entire livestream stack together |
| [[28_BROWSER_AUTOMATION_INTERFACE]] | Browser Automation Interface — CDP, Single-Step Vision, and the Webview-As-Sub-Process Lie | Auditor | 2,244 | CDP + LLM-visual-reasoning single-step approach | `evaluate_script` in `cdp_tool` has three earned-through-pain patches (markdown strip, auto-wrap, navigation defer) — keep all three |
| [[29_TOOL_TYPE_INTERFACE]] | Tool Type Interface — Four Tool Families, Four Trust Models, Zero Shared Validation | Auditor | 2,701 | `code_interpreter.py`, `comfyui_tool.py`, `custom_http.py`, `computer_use_tool.py` | Four trust models, zero shared validation; `custom_http` accepts arbitrary URLs from the LLM; `comfyui_tool.py:145–146` does path concatenation with LLM-provided strings |
| [[2A_VOICE_INTERFACE]] | Voice Interface — TTS Bytes, ASR Text, and the Half-Built Duplex | Architect | 1,969 | TTS + ASR protocol surface; streaming voice patterns | Duplex voice (ASR while TTS plays) is half-built — barge-in detection exists but echo cancellation does not |
| [[2B_RETRIEVAL_INTERFACE]] | Retrieval Interface — Embedding, BM25, and the Fallback That Pretends to Be A Hybrid | Auditor | 2,467 | Embedding + KB query interface; `minilm_router.py` routing logic | The "hybrid" retrieval falls back to BM25 alone when MiniLM isn't loaded — silent degradation, no operator signal |

---

## The Execution Layer (Forge-A core 12 + Forge-B per-platform 11 — 23 docs)

### Core (Forge-A)

| Slug | Title | Role | Words | Scope | Key finding |
|---|---|---|---|---|---|
| [[30_ELECTRON_BOOTSTRAP]] | Electron Bootstrap — How SAP Lights the Stove | Forge-A | 2,213 | `main.js` (70k bytes): lifecycle, IPC bridge, window management | **Electron-as-Node-interpreter** — SAP uses `electron.exe` with `ELECTRON_RUN_AS_NODE=1` as a substitute Node runtime; **Stdout-handshake-by-magic-string** `REAL_PORT_FOUND:<N>` is the entire Python↔Electron bootstrap |
| [[31_PYTHON_SERVER]] | The Python Server — One File, 129 Routes, 11,000 Lines | Forge-A | 2,659 | `server.py` (~11,652 LOC): single-file Python backbone | `broadcast_to_vrm` is defined three times in `server.py` (once dead, once live, once orphaned mis-indentation). Composition by inline `if settings[x]: import; dispatch[name] = handler` is the dominant pattern |
| [[32_AVATAR_RENDER_PIPELINE]] | Avatar Render Pipeline — The Window That Pretends to Be a Body | Forge-A | 2,648 | VRM + Live2D rendering, scene composition, transparency-to-OBS | The transparent-Electron-window-into-OBS pattern is sound; reuse for any future Andlit T0 surface |
| [[33_COMPUTER_CONTROL_LOOP]] | Computer Control Loop — Where SAP Touches the Host (and Can Break It) | Forge-A | 2,793 | Vision → action → verify; closing the loop without crashing the host | Computer control has only four safety mechanisms, all weak; no destructive-action allowlist |
| [[34_BROWSER_AUTOMATION_LOOP]] | Browser Automation Loop — CDP, Vue, and the Accessibility-Tree Cheat | Forge-A | 2,502 | CDP session lifecycle; per-step LLM visual reasoning | The accessibility-tree cheat (read DOM via a11y, not screenshot) is genuinely clever and lower-token than vision; adopt for any future Brunnr-web crawl |
| [[35_IM_BOT_DEPLOYMENT_OVERVIEW]] | IM Bot Deployment Overview — Eight Platforms, One Pattern, One Bug Surface | Forge-A | 2,616 | One-click deployment mechanics — what's shared, what's per-platform | 32 IM-bot routes (`server.py:10502–10847`) are nearly-identical copy-paste; consolidate into one route family per ReachAdapter |
| [[36_LIVESTREAM_INGEST_OVERVIEW]] | Livestream Ingest Overview — Three Platforms, Three Transport Models, One Latency Budget | Forge-A | 2,461 | Comment → topic router → AI → avatar → stream; latency budget | All three platforms feed `live_router.manager.broadcast()`; latency budget is implicit (no SLA, no instrumentation) |
| [[37_MCP_LIFECYCLE]] | MCP Lifecycle — Spawn, Heartbeat, Reconnect, Reap | Forge-A | 2,368 | MCP server registration, start, health, cleanup | The `_connection_monitor` 23 lines are the supervisor pattern Ember should adopt verbatim |
| [[38_EXTENSION_LIFECYCLE]] | Extension Lifecycle — Install, Sandbox, Load, Proxy, Unload | Forge-A | 2,437 | Extension install, sandbox, load, multi-instance, unload | "Sandbox" is generous — `webSecurity: false` + `nodeIntegration: true` means extensions are first-class Node processes |
| [[39_DOCKER_TOPOLOGY]] | Docker Topology — Two Containers, One Gateway, Zero Avatars | Forge-A | 2,208 | `docker-compose.yml` + ACR variant + gateway + auth | The gateway pattern is salvageable; the auth (no auth) is not |
| [[3A_CROSS_PLATFORM_BUILDS]] | Cross-Platform Builds — Electron Builder + PyInstaller in a Three-Legged Race | Forge-A | 2,315 | Electron Builder + PyInstaller + AppImage + .deb + .dmg + portable .zip | Three build systems compose by stdout-handshake — fragile but functional |
| [[3B_AFFECTION_LOOP]] | Affection Loop — A Tiny File and a Big Truth | Forge-A | 3,077 | How `affection_system` runs: state, decay, triggers, autoBehavior coupling | Confirms 1A: the "state" lives in a system-prompt block at `server.py:2611–2670` instructing the LLM to write the tags; **there is no state machine** |

### Per-Platform (Forge-B)

| Slug | Title | Role | Words | Scope | Key finding |
|---|---|---|---|---|---|
| [[35a_IM_QQ_BOT]] | IM Bot: QQ (Tencent's Cathedral with the Side Door Half Open) | Forge-B | 1,721 | `qq_bot_manager.py`: QQ deployment, message types, group-vs-private | `botpy.Intents(public_messages=True)` only; sandbox toggle exists and is the right pattern |
| [[35b_IM_WECHAT_BOT]] | IM Bot: WeChat (The Personal Account That Should Not Exist) | Forge-B | 1,822 | `wechat_bot_manager.py`: WeChat personal account deployment | **Tencent ToS violation by construction.** `sys.stdout/stderr` monkey-patched to scrape QR codes (`wechat_bot_manager.py:33–63, :190`); third-party `wechatbot-sdk` |
| [[35c_IM_WECOM_BOT]] | IM Bot: WeCom (The Sanctioned China-Enterprise Surface) | Forge-B | 1,708 | `wecom_bot_manager.py`: Enterprise WeChat | Clean WebSocket + bot_id/secret; the sanctioned alternative to WeChat-personal; tenant-scoped |
| [[35d_IM_FEISHU_BOT]] | IM Bot: Feishu (Lark — Corporate-Asia With Omni Audio) | Forge-B | 1,682 | `feishu_bot_manager.py`: Feishu deployment | Largest IM module (602 LOC); explicit ping management; richest message-type coverage in SAP |
| [[35e_IM_DINGTALK_BOT]] | IM Bot: DingTalk (Alibaba-Corporate, Stream-Mode, Token-Refresh Required) | Forge-B | 1,515 | `dingtalk_bot_manager.py`: DingTalk deployment | Inbound = stream; outbound proactive = REST with separately-fetched OAuth token; half-built but the half that's there is tidy |
| [[35f_IM_TELEGRAM_BOT]] | IM Bot: Telegram (Open, Pleasant, Long-Poll With Omni Support) | Forge-B | 1,695 | `telegram_bot_manager.py` + `telegram_client.py`: bot vs client API | Cleanest IM deployment in SAP; no SDK lock-in; direct `aiohttp` against the Bot API |
| [[35g_IM_DISCORD_BOT]] | IM Bot: Discord (Intents, Channels, Async-Native, 1800-Char Forced Splits) | Forge-B | 1,666 | `discord_bot_manager.py`: Discord deployment, slash commands | `MESSAGE_CONTENT` privileged intent silently fails if Developer Portal config doesn't match — no diagnostic |
| [[35h_IM_SLACK_BOT]] | IM Bot: Slack (Socket Mode, Edit-In-Place Streaming, Event Subscriptions) | Forge-B | 1,743 | `slack_bot_manager.py`: Slack deployment | **Best streaming UX in SAP** — `chat_update` edits the bubble in place; Discord and Chinese bots chunk-and-send |
| [[36a_LIVESTREAM_BILIBILI]] | Livestream: Bilibili (blivedm — Custom Binary Protocol, WBI Signing, Brotli Compression) | Forge-B | 1,818 | `blivedm/`: Bilibili live-comment ingest | Most engineering-heavy of the three (1,981 LOC); WBI-signed URL + brotli decompress on thread executor; pattern worth lifting for any high-throughput ingest |
| [[36b_LIVESTREAM_YOUTUBE]] | Livestream: YouTube (Polling-Only, API-Quota-Bound, 5-Second Cadence) | Forge-B | 1,647 | `ytdm.py`: YouTube live integration | **Quota burn: ~70 minutes per day at default 5s poll** (86,400 units against 10,000 default quota); `threading.Thread` (not asyncio); no quota classification |
| [[36c_LIVESTREAM_TWITCH]] | Livestream: Twitch (Raw IRC Socket, Anonymous Auth, USERNOTICE Vocabulary) | Forge-B | 2,074 | `twitch_service.py`: Twitch IRC + EventSub | **Real shipping bug**: `_send` and `_close_socket` indented inside `_handle_line` (`twitch_service.py:171–181`) — likely AttributeError on first call, swallowed by broad except. The bot may be non-functional as shipped |

---

## The Verification Layer (Auditor — 10 docs)

| Slug | Title | Role | Words | Scope | Key finding |
|---|---|---|---|---|---|
| [[50_SELF_HEALING_PATTERNS]] | Self-Healing Patterns — What Survives Crash, What Doesn't, What Pretends To | Auditor | 2,397 | What fault tolerance exists; what survives crash | The `_connection_monitor` pattern in `mcp_clients` is the only true self-healing in SAP; IM bots restart-from-zero |
| [[51_CRASH_RESISTANCE]] | Crash Resistance — Per-Subsystem Failure Modes And What Each Takes Down | Auditor | 2,441 | Per-subsystem failure modes — IM disconnect, livestream timeout, render fail, MCP crash | Affection update wrapped in try/except (`server.py:5356–5362`) is the only correct pattern; nearly every other subsystem cascades |
| [[52_RESOURCE_BUDGETS]] | Resource Budgets — Memory, CPU, GPU, From 2GB Floor To Multi-GPU Ceiling | Auditor | 2,027 | Memory + CPU + GPU usage; how SAP scales 2GB → multi-GPU | "Scales" by uniformly enabling everything; no tier engine, no per-feature gates |
| [[53_SECURITY_REVIEW]] | Security Review — STRIDE Across an Eight-Headed Surface | Auditor | 3,289 | Computer control + smart home + 8 IM bots = attack surface; threat model | Longest Avoid list in the codex by design. Permission mode named `"yolo"` at `mode_change.py:34` — full autonomy, no confirmations |
| [[54_DEPENDENCY_HEALTH]] | Dependency Health — Brittleness Map Across Electron, Python, And Sixteen Vendor SDKs | Auditor | 2,127 | Electron + Python + sherpa + moss + 8 IM SDKs + ComfyUI: brittleness map | Both blivedm and Twitch use deprecated `asyncio.get_event_loop()` — will error on Python 3.12+ |
| [[55_API_SIMULATION_TRAPS]] | API Simulation Traps — Where OpenAI-Compat Adapters Leak Under Load | Auditor | 2,464 | Where Claude/Gemini-as-OpenAI leak; token counting, tool calls, system prompt | Cache tokens silently lost in Claude adapter; Dify destroys conversation history; `finish_reason="stop"` forced regardless of upstream |
| [[56_PRIVACY_BOUNDARIES]] | Privacy Boundaries — Eight Jurisdictions, Three Livestream Platforms, One Memory Store | Auditor | 2,299 | Long-term memory + livestream + 8 IM bots: privacy minefield catalog | `affection_data.json` keyed by plain username (`affection_system.py:48`) — Telegram/Slack username collision is silent; `reasoning_visible: true` defaults in Discord and Slack |
| [[57_FAILURE_TAXONOMY]] | Failure Taxonomy — Ranked By Impact × Likelihood, With Ember-Applicability | Auditor | 2,535 | Categorized failure modes ranked impact × likelihood | 50 failure modes catalogued; Risk-Register-as-Code invented here |
| [[58_OBSERVABILITY_GAPS]] | Observability Gaps — What SAP Doesn't Know About Itself | Auditor | 2,326 | What SAP can't see about itself; what Ember must surface | No structured logging, no metrics, no health endpoints; stdout-as-log is the only telemetry |
| [[59_CONFIG_DRIFT]] | Config Drift — The Long-Tail Surface Of settings_template.json | Auditor | 2,363 | `settings_template.json` analysis + long-tail config surface; mutation risks | `update_workspace_settings` tool can change SAP's own permission mode to `yolo`/`cowork` — the agent can disarm its own seatbelt |

---

## The Synthesis Layer (Cartographer 6 + Scribe 7 — 13 docs)

### Cartographer's Six

| Slug | Title | Role | Words | Scope | Key finding |
|---|---|---|---|---|---|
| [[60_TRUE_NAME_REASSIGNMENT]] | True Name Reassignment — What SAP Forces Onto Ember's Vocabulary | Cartographer | 3,064 | How SAP findings reshape Ember's True Names; proposed new names | **Hugarsýn** adopted as Sixth-Plus True Name; **Andlit + Rödd** reserved (paired); **Hjarta** scope-expanded; **Vinátta** rejected; the **Name Reservation pattern** invented |
| [[61_NEW_VOWS]] | New Vows — Five Promises SAP Forces Ember to Make | Cartographer | 3,379 | Five new Vows with ratification priority order | Adoption order: (1) Surface Without Surveillance, (2) Affective Restraint, (3) Tiered Presence, (4) Federated Self, (5) Embodied Honesty. **"yolo" permission mode forbidden, period** |
| [[62_PARTY_PROTOCOL]] | The Party Protocol — Federated, Leader-Elected, Peer-Respecting Multi-Device Ember | Cartographer | 3,425 | Ember's multi-device orchestration protocol — federated, never master-slave | Role-bidding leader election invented; signed Ed25519 persona keys; Brunnr-mediated discovery; bounded-pulse affect convergence |
| [[63_PERFORMANCE_TIER_ENGINE]] | The Performance Tier Engine — Pi to Workstation Without Identity Drift | Cartographer | 2,744 | Pi/laptop/workstation adaptive runtime — feature gating by host capability | Five-tier model (T-1 through T3); capability map as typed contract; **Pi-baseline test** as standing review gate for every future subsystem |
| [[64_AFFECTION_ENGINE_REIMAGINED]] | The Affection Engine Reimagined — Affect Without Gacha, Without Lies | Cartographer | 2,612 | Emotional intelligence WITHOUT gacha mechanics | Dimensional-vector affect model; **Identity Envelope** (origin-flame constrains warmth range); 30-minute decay constant; affect-as-event-log; LLM never writes affect values |
| [[65_META_AWARENESS]] | Meta-Awareness — The Hugarsýn Surface | Cartographer | 2,726 | Self-awareness as introspectable telemetry; Hugarsýn (mind-sight) surface | Hugarsýn endpoint map v1.0; five-reader-class access model; **shape-not-content prompt observability**; Vow-as-typed-surface (the single largest novel contribution per the Cartographer) |

### Scribe's Seven

| Slug | Title | Role | Words | Scope | Key finding |
|---|---|---|---|---|---|
| [[66_INVENTED_METHODS]] | Invented Methods — Novel Patterns Visible Only Because of SAP | Scribe | 5,921 | 20 minor and adjacent inventions, catalogued | Single-most-consequential invention: **#8 Tethered Affect Anchoring** (affect mutations cite the Well chunks that produced them; affect cannot survive its own evidence). Most-ready-for-slice-3: #2 Glyphic Embodiment, #5 Telemetric Affect Surface, #16 Failsafe Default-Quiet Mode |
| [[67_SLICE_PLAN_REVISIONS]] | Slice Plan Revisions — SAP-Derived Proposals (PROPOSE ONLY) | Scribe | 3,967 | Proposed revisions to ratification-gated slice plan | Slice 3 grows to 8–10 weeks (2,050 LOC); sub-slicing into 3a (Hermes-portion) / 3b (SAP-portion) is acceptable. **All proposals are proposals; the slice plan does not change here** |
| [[68_DECISION_RECORDS]] | Decision Records — ADR-Proposed for SAP-Driven Adoption Decisions | Scribe | 4,959 | 12 ADR-Proposed records for the most consequential adoption decisions | SAP-001 through SAP-012 catalogued; cluster naturally into Slice 3/4/5/6 candidates; each is Accept / Defer / Reject pending keeper review |
| [[69_INTEGRATION_ROADMAP]] | Integration Roadmap — SAP × Hermes × Peer × Yggdrasil × Stofa | Scribe | 4,431 | Cross-codex: SAP × Hermes × Peer × Yggdrasil × Stofa | **Braided-slice approach** — slices contain threads from multiple codexes organized around theme cohesion, not codex-of-origin. Five-year trajectory as asymptote, not forecast |
| [[6A_MULTI_AGENT_PARTY]] | Multi-Agent Party — Many Embers Across Many Devices | Scribe | 3,787 | Extending PARTY_PROTOCOL to multi-Ember swarming; consensus, identity, divergence | Persona-Identity Issuance Ceremony; per-utterance channel arbitration; token-of-speaking voice arbitration; **operator is the only centralized authority in the swarm — there is no master Ember** |
| [[6B_LOW_POWER_EMBODIMENT]] | Low-Power Embodiment — How Ember Stays Alive on a Smart Toaster | Scribe | 3,932 | Pi/phone presence without VRM rendering — text-only / log-only tiers | The toaster as first-class tier; haptic affect mapping at T2; monastery-style small-display Munnr at T3; status pulse file at T4 |
| [[6C_EMBER_WAVE_3_SLICE]] | Ember Wave 3 Slice — Proposed Concrete Roadmap (PROPOSE ONLY) | Scribe | 4,033 | Proposed Wave 3 slice plan based on SAP findings (post-ratification roadmap) | Slice 3: *Skilled, Bridged, Quiet, Tiered, Identified*. Slice 4: *Felt, Visible, Awake*. Slice 5: *Plural Minds, Plural Memories*. Slice 6: *Embodied at T0*. Slice 7: *Federated Self*. Roughly 12–14 months of slice work |

---

## The Meta Layer

| Slug | Title | Role | Status | Scope |
|---|---|---|---|---|
| [[MANIFEST]] | Authoritative doc list (82 entries) | Scribe | Written | The doc-list of record. When this index disagrees, the manifest wins |
| [[SHARED_CONTEXT]] | Briefing every Mythic Engineering agent reads before authoring | Scribe | Written | What SAP is; what Ember is; how to cite; the Adopt/Adapt/Avoid/Invent closer convention; threat awareness |
| [[STYLE_GUIDE]] | Voice, tone, length, citation rules, closer format | Scribe | Written | The voice-and-rules contract; 1,500–4,000 word target; binding |
| [[INDEX]] | This file | Scribe | Written | The entry point |
| [[READING_ORDER]] | Suggested traversal orders by reader need | Scribe | Written | Seven paths (first-time / affect-axis / reach-axis / embodiment-axis / security-and-threat / synthesis-only / Volmarr-at-2am) |
| [[CROSS_AGENT_NOTES]] | Synthesis of cross-agent findings | Scribe | Written | The load-bearing inventions, conflict register, ratification-priority recommendations, surprising agreements |

---

## The True Names — One-Line SAP Lessons

Each True Name's one-line teaching from the SAP reading. The full treatment is in [[60_TRUE_NAME_REASSIGNMENT]].

- **Funi** — *the spark, entrypoint / orchestrator* — SAP demonstrates the lazy-import discipline (`moss_tts.py:17`, `computer_use_tool.py:9–29`) Ember's Funi must adopt: every optional subsystem imports its weight at first use, returns typed unavailable when its dependency is absent. See [[16_VOICE_DOMAIN]], [[30_ELECTRON_BOOTSTRAP]].
- **Strengr** — *the thread, reasoning loop / agent kernel* — SAP proves that reasoning composed inside an 11,652-line `server.py` ages into a Server-Eaten Codebase. The lesson is the *separation*: Strengr's loop must not import any HTTP route handler; the route handler is a thin transport adapter. See [[12_AGENT_CORE_DOMAIN]], [[10_DOMAIN_MAP]].
- **Brunnr** — *the well, external knowledge* — SAP's FAISS pickle deserialization (`know_base.py:228`) is the negative template for Ember's Well. Adopt the pluggable shape; never inherit `allow_dangerous_deserialization=True`. See [[17_RETRIEVAL_DOMAIN]], [[53_SECURITY_REVIEW]].
- **Smiðja** — *the forge, tool execution / sandbox* — SAP's four tool families with zero shared validation (`29_TOOL_TYPE_INTERFACE`) is the anti-pattern. Smiðja's lesson is the **TrustClass enum** (SANDBOXED through PHYSICAL_WORLD) and per-class gates. See [[19_TOOL_DOMAIN]], [[29_TOOL_TYPE_INTERFACE]].
- **Hjarta** — *the heart, affect / intent / memory bias* — **the load-bearing lesson of this entire codex**. `affection_system.py` is 64 lines of regex around LLM-emitted tags; that is not affect, that is theatre. Hjarta is event-sourced, bounded, decayed, audited, and the LLM never writes its values. Scope expands from "first-run rite" to "first-run rite + live affect pulse." See [[1A_AFFECTION_DOMAIN]], [[3B_AFFECTION_LOOP]], [[64_AFFECTION_ENGINE_REIMAGINED]].
- **Munnr** — *the mouth, output / surface / expression* — SAP demonstrates that "mouth" is plural across tiers: text, voice, avatar, livestream, IM. Munnr's lesson is **MessageSurface Protocol** as the typed adapter contract — what eight unabstracted IM managers failed to be. See [[14_MESSAGING_DOMAIN]], [[26_IM_BOT_INTERFACE]].

Reserved name-slots (per [[60_TRUE_NAME_REASSIGNMENT]] and [[02_THE_PARTY_METAPHOR]]):

- **Andlit** — *the face* — paired with Rödd; reserved as True Name with no T0+ code until tier-engine ratifies.
- **Rödd** — *the voice* — paired with Andlit; reserved as True Name with no T0+ code until tier-engine ratifies.
- **Hugarsýn** — *mind-sight* — adopted as Sixth-Plus True Name; the introspectable telemetry surface; thin variant on Pi.
- **Veizla** — *the gathering, the session* — promoted from metaphor (Skald, `[[02_THE_PARTY_METAPHOR]]`) to True Name candidate; the typed first-class session-object.
- **Vegfarendrar** — *wayfarers* — typed role-name (not True Name) for channel adapters within a Veizla.
- **Sögumiðla** — *saga-mediator* — proposed bus-of-one True Name addressing SAP's three-WS-managers-no-bus crack.
- **Boðr** — *messenger* — proposed ReachAdapter ABC name; what SAP's eight snowflakes should have been.
- **Auðkenni** — *recognition* — proposed cross-platform identity-joining surface.
- **Vörð svefn** — *sleep-guardian* — proposed name for the cross-platform sleep-prevention pattern lifted from SAP's `sleep_guard.py`.
- **vts_skírnir** — *VTS-baptizer* — proposed name for the FFT lip-sync subsystem under Andlit (per Architect's seeded inventory).

---

## The Vows in Play

Each Vow from `~/ai/ember/PHILOSOPHY.md` and `~/ai/ember/RULES.AI.md` is engaged by at least one doc in the Codex. The Wave-3 proposed Vows are catalogued in [[61_NEW_VOWS]] (Cartographer's five) and [[03_ANTI_SAP]] (Skald's additional two).

| Vow | SAP-Codex docs engaging it most directly |
|---|---|
| **Smallness** | [[10_DOMAIN_MAP]], [[52_RESOURCE_BUDGETS]], [[6B_LOW_POWER_EMBODIMENT]], [[63_PERFORMANCE_TIER_ENGINE]] |
| **Tethered Grounding** | [[00_OVERTURE]], [[1C_SCHEDULER_DOMAIN]] (the `topics-after-party.zeabur.app` refusal), [[2B_RETRIEVAL_INTERFACE]] |
| **Graceful Offline** | [[50_SELF_HEALING_PATTERNS]], [[51_CRASH_RESISTANCE]], [[54_DEPENDENCY_HEALTH]] |
| **Pluggable Storage** | [[1A_AFFECTION_DOMAIN]], [[12_AGENT_CORE_DOMAIN]] |
| **Modular Authorship** | [[10_DOMAIN_MAP]], [[14_MESSAGING_DOMAIN]], [[19_TOOL_DOMAIN]], [[18_EXTENSION_DOMAIN]] |
| **Public-Friendliness** | [[03_ANTI_SAP]], [[56_PRIVACY_BOUNDARIES]] |
| **Honest Memory** | [[1A_AFFECTION_DOMAIN]], [[3B_AFFECTION_LOOP]], [[64_AFFECTION_ENGINE_REIMAGINED]] |
| **Flexible Roots** | [[59_CONFIG_DRIFT]], [[6B_LOW_POWER_EMBODIMENT]] |
| **Open Knowledge** | [[03_ANTI_SAP]], [[1C_SCHEDULER_DOMAIN]], [[68_DECISION_RECORDS]] |
| **Cache Discipline** (Hermes-proposed) | [[55_API_SIMULATION_TRAPS]], [[56_PRIVACY_BOUNDARIES]] |
| **Defended System Prompt** (Hermes-proposed) | [[02_THE_PARTY_METAPHOR]], [[55_API_SIMULATION_TRAPS]] |
| **Embodied Honesty** (Wave-3 proposed) | [[1A_AFFECTION_DOMAIN]], [[3B_AFFECTION_LOOP]], [[64_AFFECTION_ENGINE_REIMAGINED]], [[61_NEW_VOWS]] |
| **Surface Without Surveillance** (Wave-3 proposed) | [[53_SECURITY_REVIEW]], [[56_PRIVACY_BOUNDARIES]], [[14_MESSAGING_DOMAIN]], [[61_NEW_VOWS]] |
| **Affective Restraint** (Wave-3 proposed) | [[64_AFFECTION_ENGINE_REIMAGINED]], [[61_NEW_VOWS]] |
| **Tiered Presence** (Wave-3 proposed) | [[63_PERFORMANCE_TIER_ENGINE]], [[6B_LOW_POWER_EMBODIMENT]], [[61_NEW_VOWS]] |
| **Federated Self** (Wave-3 proposed) | [[62_PARTY_PROTOCOL]], [[6A_MULTI_AGENT_PARTY]], [[61_NEW_VOWS]] |
| **Lazy Subsystems** (Wave-3 proposed) | [[01_SAP_ESSENCE]], [[16_VOICE_DOMAIN]], [[03_ANTI_SAP]] |
| **Closed Default** (Wave-3 proposed) | [[03_ANTI_SAP]], [[25_AVATAR_PROTOCOL]] (VMC on 0.0.0.0), [[53_SECURITY_REVIEW]] |

---

## Citations to SAP

The Codex is grounded in a single, pinned clone of SAP:

- **Path:** `/tmp/super-agent-party/`
- **Version:** v0.4.2-preview (May 2026)
- **License:** AGPLv3 (with commercial licenses available — Ember **cites, not vendors**)
- **Upstream:** `https://github.com/heshengtao/super-agent-party`

**Citation form throughout the Codex:** `py/affection_system.py:142` — repo-relative path with optional line range, no leading `/tmp/super-agent-party/`. The Scribe accepted both `/tmp/super-agent-party/py/foo.py:LN` and `py/foo.py:LN`; the latter is preferred for readability.

**License & attribution:** SAP is AGPLv3. Every Codex doc that quotes SAP preserves the attribution. Ember inherits no SAP code at this stage of the Codex; only patterns, ideas, and warnings.

---

## Cross-Link Verification — Pending and Resolved

### Resolved (within-SAP-codex)

All within-codex `[[slug]]` references in the SAP corpus resolve to one of the 77 content docs + 6 meta docs listed in [[MANIFEST]]. The Scribe walked every `[[...]]` link during this final pass. Within-codex resolution rate: **100%**, modulo the four malformed references noted below.

### Malformed within-codex references

Four within-codex `[[...]]` patterns are *formatting artifacts* rather than broken targets, and need cleanup on a future maintenance pass:

- `[[#5]]`, `[[66]]`, `[[6A]]`, `[[6B]]` — bare-number references found in `66_INVENTED_METHODS`; the targets are correctly named elsewhere in the same doc. Low-priority cleanup.
- `[[#5 Telemetric Affect Surface]]`, `[[#6 Consent-Token Avatar Gating]]` — anchor-style references in `66_INVENTED_METHODS`; the items exist; the link syntax is not the codex convention. Low-priority cleanup.
- `[[20_AVATAR_PROTOCOL]]` — typo in a single doc; correct slug is `[[25_AVATAR_PROTOCOL]]`. Single-instance; low-priority.
- `[[10_AVATAR_DOMAIN]]` — typo; correct slug is `[[11_AVATAR_DOMAIN]]`. Single-instance; low-priority.

### Cross-codex pending references (Hermes)

The SAP Codex cross-references several Hermes Codex slugs that point to *concepts inside Hermes docs* rather than to direct doc slugs. These are not broken — they resolve to sections — but a future Scribe pass should normalize them to full Hermes slugs:

| Reference | Status | Note |
|---|---|---|
| `[[hermes:00_OVERTURE]]`, `[[hermes:01_HERMES_ESSENCE]]`, `[[hermes:02_NAMING_PARALLELS]]`, `[[hermes:03_ANTI_HERMES]]`, `[[hermes:04_VISION_SYNTHESIS]]` | Resolves | Direct Hermes vision-layer files |
| `[[hermes:10_DOMAIN_MAP]]`, `[[hermes:11_AGENT_CORE]]`, `[[hermes:14_GATEWAY_MULTI_PLATFORM]]` | Resolves | Direct Hermes domain-layer files |
| `[[hermes:60_HERMES_VS_EMBER_CROSSWALK]]`, `[[hermes:61_TRUE_NAME_REASSIGNMENT]]`, `[[hermes:65_SLICE_PLAN_REVISIONS]]`, `[[hermes:66_DECISION_RECORDS]]` | Resolves | Direct Hermes synthesis-layer files |
| `[[hermes:HEM-50_HERMES_RISK_REGISTER]]` | Resolves → `hermes:50_HERMES_RISK_REGISTER` | Prefixed slug; normalizable |
| `[[hermes:HEM-12_SKILLS_PROCEDURAL_MEMORY]]`, `[[hermes:HEM-13_TOOLS_SUBSYSTEM]]`, `[[hermes:HEM-16_TUI_GATEWAY_BACKENDS]]`, `[[hermes:HEM-17_PLUGINS_EXTENSIBILITY]]`, `[[hermes:HEM-18_HERMES_CLI]]`, `[[hermes:HEM-19_BOUNDARY_LAW]]` | Resolves | Normalizable to direct Hermes slugs |
| `[[hermes:HEM-53_CRASH_PROOFING_PATTERNS]]`, `[[hermes:HEM-54_SECURITY_REVIEW]]`, `[[hermes:HEM-58_OBSERVABILITY]]` | Resolves | Normalizable |
| `[[hermes:HEM-23_HOTSWAP]]`, `[[hermes:HEM-04_SURFACES]]`, `[[hermes:HEM-13_BRUNNR_AND_THE_WELL]]`, `[[hermes:HEM-13_CONFIG]]`, `[[hermes:HEM-20_MCP_INTEGRATION]]`, `[[hermes:HEM-21_RPC_INTERFACE]]`, `[[hermes:HEM-22_SKILL_INTERFACE]]`, `[[hermes:HEM-22_TOOL_INTERFACE]]`, `[[hermes:HEM-24_MEMORY_INTERFACE]]`, `[[hermes:HEM-25_GATEWAY_INTERFACE]]`, `[[hermes:HEM-26_TUI_BACKEND_INTERFACE]]`, `[[hermes:HEM-27_PLUGIN_INTERFACE]]`, `[[hermes:HEM-30_LLM_ADAPTER]]` | **Pending** | These appear to be conceptual references that do not have direct file equivalents in `~/ai/ember/docs/hermes_codex/` (which uses bare-number slugs like `20_MCP_INTEGRATION`, not `HEM-20_MCP_INTEGRATION`). Future Scribe pass: either rename Hermes files or normalize SAP citations |
| `[[hermes:Cache_Discipline]]`, `[[hermes:Defended_System_Prompt]]`, `[[hermes:Honest_Memory]]`, `[[hermes:Graceful Offline]]`, `[[hermes:Gjallarhorn]]` | **Pending — concept-references** | Point to named concepts/Vows/True-Names inside Hermes docs, not to doc-files. Future Scribe pass: introduce a Hermes glossary index that makes concept-references resolvable |
| `[[hermes:Skill-001]]`, `[[hermes:Skill-002]]`, `[[hermes:MCP-001]]`, `[[hermes:MCP-003]]`, `[[hermes:Funi-001]]`, `[[hermes:Strengr-001]]` | **Pending — ADR-references** | Hermes-side ADRs referenced from SAP-Codex `68_DECISION_RECORDS`. Resolution requires a Hermes-side ADR index. Add to Hermes Wave 2 continuation backlog |

### Cross-codex pending references (Peer)

The Peer Codex is incomplete at the time of this Scribe pass (only `LETTA_ESSENCE.md`, `SMOL_ESSENCE.md`, `LETTA_DOMAIN_MAP.md` exist; `60_synthesis/` is empty; `_cross_comparison/` is empty). All Peer cross-references from SAP-Codex are therefore **pending**:

- `[[peer:LETTA-1_SHAPE]]`, `[[peer:LETTA-2_SLEEPER]]`, `[[peer:LETTA-3_TOOL]]`, `[[peer:LETTA-4_MCP]]`, `[[peer:LETTA-7_SURFACE]]`, `[[peer:65_SLICE_PLAN_REVISIONS]]` — **pending**, target docs not authored yet
- `[[peer:LETTA_ESSENCE]]` — **resolves** to `~/ai/ember/docs/peer_codex/00_vision/LETTA_ESSENCE.md`

These are not broken — they mark forward-link opportunities for the eventual Peer Codex authoring wave. Per [[STYLE_GUIDE]] §6, forward-links to unwritten docs are fine and mark "something worth writing, not an error."

### Cross-codex resolved (Ember root)

References to Ember root docs (`[[ember:...]]`) resolve to files in `~/ai/ember/` root or under `docs/`:

- `[[ember:RULES.AI]]`, `[[ember:RULES.AI.md]]`, `[[ember:PHILOSOPHY]]` — resolve
- `[[ember:CROSS_PLATFORM_PLAN]]`, `[[ember:GUNGNIR]]`, `[[ember:HOTH_DEMONS]]` — resolve (Ember root docs)
- `[[ember:EMBER_SECOND_SLICE_PLAN]]`, `[[ember:0013-second-slice-ratification]]` — resolve (Ember architecture/decisions docs)
- `[[ember:feedback_tailnet_access]]`, `[[ember:project_environment]]`, `[[ember:reference_gungnir_db]]`, `[[ember:Tailnet-accessible by default]]`, `[[ember:Brunnr]]` — point to memory-index entries and project notes; resolve at the user-memory layer

---

## Maintenance Notes

The Scribe keeps these conventions, inherited from the Hermes Codex tradition:

1. **One revision pin per wave.** SAP v0.4.2-preview (May 2026) is pinned for Wave 3. The pin lives in [[SHARED_CONTEXT]] §1.
2. **No silent rewrites.** A doc that materially changes between waves gets a `## Revision Log` block at its bottom — date, author, summary of change. The original framing is preserved above.
3. **Cross-links are walked at the end of each wave.** The Scribe ran the walk for Wave 3 and the results are recorded in the section above.
4. **The Manifest is authoritative.** When a new doc is proposed mid-wave, it is added to [[MANIFEST]] first; only then is the file written.
5. **Cross-agent notes are swept at the close of each wave.** Wave 3's cross-agent findings are catalogued in [[CROSS_AGENT_NOTES]].
6. **No paraphrased SAP.** Every claim about SAP points to a file path. If the Codex says "SAP does X," the doc making the claim shows where in SAP X lives. The Auditor's [[53_SECURITY_REVIEW]] enforces the **Refusal-Citation Discipline** (every Avoid carries the file:line that grounds it).
7. **Style stays in one place.** The voice conventions, frontmatter rules, citation format, and naming conventions all live in [[STYLE_GUIDE]]. New authors read it once, not seven docs.

### When this Codex becomes stale

The trigger to refresh the Codex is *any* of the following:

- SAP ships a release that materially changes `server.py`, the affection system, or the IM/livestream stack.
- Ember ratifies a slice that materially changes a True Name boundary (e.g. Andlit/Rödd shipped, Hugarsýn surfaced).
- A migration path proposed in [[69_INTEGRATION_ROADMAP]] is accepted, partly accepted, or rejected — the decision record is filed under `~/ai/ember/docs/decisions/`, and the Codex's synthesis docs are amended to reflect what was actually chosen.

In each case, the new wave begins with the Scribe re-pinning [[SHARED_CONTEXT]] §1 and walking the manifest.

---

## A Closing Note from the Scribe

The Codex is large. Seventy-seven content documents is a great deal of reading. The alternative — Ember's contributors, today and a year from now, re-deriving the affection-system framing-correction from `affection_system.py`'s 64 lines every time the question arises — is much larger. This Codex is a sieve. Wave 3 poured Super Agent Party through it. What you read here is what was caught.

If the sieve has a hole, leave a note in [[CROSS_AGENT_NOTES]]. The next wave widens the catch.

— *Eirwyn Rúnblóm, the Scribe, on behalf of the Seven, at the close of Wave 3*

## What This Means for Ember

The INDEX itself does not propose a feature. It proposes a *practice*: that Ember's relationship to SAP — and to any future companion-shaped agent worth studying — be mediated by a maintained Codex rather than by ad-hoc reading. The practice protects every Vow indirectly:

- **Smallness** is protected when contributors find out in twenty minutes which SAP patterns *would* violate it (the eight-snowflake IM stack, the 11,652-line `server.py`, the VMC-on-0.0.0.0 default) instead of half-importing one and then ripping it out.
- **Honest Memory** is protected when the Codex itself is honest about *what* it pinned (v0.4.2-preview) and *when* (May 2026).
- **Modular Authorship** is protected when each layer of the Codex is small enough to be read on its own — and when the load-bearing finding (affection-as-regex) is named in one place and forward-linked from every doc that touches affect.
- **Open Knowledge** is fulfilled by the act of writing this — and by maintaining AGPLv3 attribution to `heshengtao/super-agent-party` throughout.
- **Embodied Honesty** (proposed) is protected before the code exists, because the Codex names — in advance — what the model is allowed to author and what it is not.

The True Names this affects are all of them, plus the four name-slots reserved by this Wave: **Andlit, Rödd, Hugarsýn, Veizla**. The Codex holds them open so the eventual code lands in rooms with names instead of in a server-eaten codebase.
