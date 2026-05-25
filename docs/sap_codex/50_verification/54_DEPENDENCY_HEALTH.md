---
codex_id: 54_DEPENDENCY_HEALTH
title: Dependency Health — Brittleness Map Across Electron, Python, And Sixteen Vendor SDKs
role: Auditor
layer: Verification
status: draft
sap_source_refs:
  - pyproject.toml:1-87
  - uv.lock (referenced)
  - package.json (referenced)
  - py/ClaudeAsOpenAI.py:30-38
  - py/cdp_tool.py:140-155
ember_subsystem_targets: [Funi]
cross_refs:
  - 50_verification/52_RESOURCE_BUDGETS
  - 50_verification/57_FAILURE_TAXONOMY
  - 50_verification/55_API_SIMULATION_TRAPS
---

# Dependency Health — Brittleness Map Across Electron, Python, And Sixteen Vendor SDKs

> *Sólrún, voice cold and even: SAP's pyproject.toml is a tour of the open-source AI ecosystem as of late 2026. It is also a tour of the surface area an Ember maintainer would inherit if they vendored any of it wholesale. The dependency graph is the future maintenance burden in chemical form.*

This document audits SAP's dependency declarations: which are critical, which are at risk, which have version pins, which carry transitive risks. The lens is **maintenance burden over the next 24 months**: which packages will demand attention?

The data: `/tmp/super-agent-party/pyproject.toml` (87 deps), `package.json` (Electron stack), `uv.lock` (transitive resolution). I do not enumerate every transitive dep — I name the *load-bearing* ones and their risk profile.

---

## 1. The Core Trust Hinges

These dependencies are the things SAP *cannot survive without*. Their stability defines SAP's stability.

### 1.1 `litellm>=1.83.7`

`pyproject.toml:75`. LiteLLM is the multi-vendor LLM router used by `ClaudeAsOpenAI.py:32` and `GeminiAsOpenAI.py:33`. Two of three OpenAI-compat adapters depend on LiteLLM.

LiteLLM ships fast: weekly minor releases, frequent breaking changes in error types and chunk shapes. The constraint `>=1.83.7` (minimum, no upper bound) means `uv lock --upgrade` could pull a 2.x release. SAP has no test suite to detect breakage.

**Risk:** High. LiteLLM is the most-cited cause of "OpenAI-compat broke" in this codex. See [[55_API_SIMULATION_TRAPS]].

**Pin strategy SAP uses:** `>=1.83.7` — no upper bound. Permissive.

### 1.2 `openai>=1.76.0`

`pyproject.toml:23`. OpenAI's Python SDK. Used directly in eight IM bot managers (e.g. `qq_bot_manager.py:11`, `discord_bot_manager.py:15`, `slack_bot_manager.py:16`). Used indirectly through LiteLLM.

OpenAI ships breaking changes at major versions; 1.x has been stable for the Pydantic-typed surface. The dep is `>=1.76.0` — permissive minor bumps OK.

**Risk:** Low-Medium. The 1.x line has been stable.

### 1.3 `langchain-classic>=1.0.1`, `langchain-community>=0.3.22`, `langchain-core>=1.2.28`, `langchain-ollama>=0.3.2`, `langchain-openai>=0.3.14`, `langchain-google-community>=2.0.7`, `langchain-exa>=0.3.0`

Seven LangChain packages. The LangChain ecosystem has been the most-frequent breaker of dependent projects across 2024-2026 — package splits, deprecation moves, runtime API changes.

`know_base.py:7-12` imports from langchain_classic, langchain_community, langchain_text_splitters. Used for chunking and the hybrid retriever (BM25 + FAISS).

**Risk:** High. The LangChain ecosystem has had three major-version churns in the audit period; each broke downstream. Pins are minor-only.

### 1.4 `mcp>=1.6.0`

`pyproject.toml:20`. The MCP (Model Context Protocol) Python client/server library. Used by `mcp_clients.py` to spawn and talk to MCP servers.

MCP is **still pre-stable**. Spec changes between minor versions are routine. Server-side and client-side must agree on protocol version.

**Risk:** High. Active spec evolution.

### 1.5 `fastapi-mcp>=0.3.4`

`pyproject.toml:15`. FastAPI-MCP exposes SAP's own endpoints as an MCP server. The `>=0.3.4` floor — minor versions are not API-stable.

**Risk:** High. Pre-1.0.

### 1.6 `faiss-cpu>=1.10.0`

`pyproject.toml:14`. FAISS for vector search. CPU-only — confirms the GPU absence in retrieval (`[[52_RESOURCE_BUDGETS]]` §10).

FAISS is the most stable dependency in the list. The C++ core has been stable for years. The Python binding occasionally has changes.

**Risk:** Low.

### 1.7 `onnxruntime>=1.24.0`, `transformers>=4.57.3`, `sentencepiece>=0.2.1`

The local embedding stack. Used by `minilm_router.py:1-188`.

`transformers` ships breaking changes between minors regularly. `onnxruntime` is more stable. `sentencepiece` is essentially stable.

**Risk:** Medium. Transformers is the moving piece.

---

## 2. The Per-Platform IM Bot SDKs

Eight platforms, eight SDKs, eight risk profiles.

| Platform | SDK | Pin | Risk |
|---|---|---|---|
| QQ | `qq-botpy>=1.2.1` | Permissive | Medium — Chinese ecosystem moves quickly |
| WeChat | `wechatbot-sdk>=0.2.0` | Permissive | High — pre-1.0, niche, undocumented |
| WeCom | `wecom-aibot-python-sdk>=1.0.2` | Permissive | Medium |
| Feishu | `lark-oapi>=1.4.24` | Permissive | Medium — official from ByteDance, frequent updates |
| DingTalk | `dingtalk-stream>=0.24.3` | Permissive | Medium |
| Telegram | (no SDK — `telegram_client.py` is custom) | N/A | High — bespoke implementation |
| Discord | `discord-py>=2.6.4` | Permissive | Low — most mature SDK in the list |
| Slack | `slack-sdk>=3.39.0` | Permissive | Low |

The Chinese platform SDKs (`qq-botpy`, `wechatbot-sdk`, `wecom-aibot-python-sdk`, `lark-oapi`, `dingtalk-stream`) are the *most likely* to break SAP. Reasons:

- Vendor APIs in China change frequently (regulatory updates, app store requirements, anti-abuse measures)
- SDK maintainers respond to vendor changes; tests may not cover all paths
- Many of these SDKs are pre-1.0 or recently post-1.0
- Telegram has *no* SDK — `telegram_client.py` is custom code maintaining the Bot API directly. Telegram API changes go straight to SAP.

A single Chinese platform's API change can break SAP's deployment in that platform within days.

---

## 3. The Livestream Dependencies

- **Bilibili:** Vendored `py/blivedm/` (vendored, not pip-installed). Risk: vendored code does not auto-update; bug fixes upstream do not flow in.
- **YouTube:** `google-api-python-client>=2.179.0`. Stable, well-maintained.
- **Twitch:** No SDK — `twitch_service.py` uses raw socket IRC. Risk: Twitch IRC schema changes break the parser silently.

The vendored `blivedm` is the most fragile of the three because *nobody is auto-updating it*. The original repo may have moved on; SAP's copy is frozen.

---

## 4. The Audio Dependencies

- `edge-tts>=7.0.2` — Microsoft Edge TTS via reverse-engineered API. **Inherently fragile** — Microsoft can change the API at any time and the package authors must reverse-engineer the new version. Has had multiple breakages historically.
- `sherpa-onnx>=1.12.19` — well-maintained, stable.
- `tetos>=0.4.2` — multi-vendor TTS aggregator. Pre-1.0 (0.x).
- `pyttsx3>=2.99` — synthetic TTS, fairly stable.
- `elevenlabs>=2.41.0` — vendor SDK, stable.
- `soundfile>=0.13.1` — stable C-binding.
- `pydub>=0.25.1` — long-stable but unmaintained-feel.
- `imageio-ffmpeg>=0.6.0` — bundles FFmpeg binary; large, stable.

The `edge-tts` package is the surprise risk: it has broken at least twice in 2024-2025 when Microsoft changed the Edge endpoints.

---

## 5. The Code-Execution Dependencies

- `e2b-code-interpreter>=1.5.0` — E2B's official SDK. Vendor service; their uptime is the dependency.
- `zerobox>=0.1.5` — pre-1.0 sandbox library, non-Windows only. `pyproject.toml:86` shows `sys_platform != 'win32'` constraint.
- `pyautogui>=0.9.54` — long-stable but has cross-platform quirks (X11 vs Wayland on Linux; macOS permission dialogs).
- `pywin32>=310 ; sys_platform == 'win32'` — large, OS-specific.

E2B's API stability is the dominant risk; `zerobox` at 0.x is also a churn risk.

---

## 6. The Vue/Electron Dependencies

`package.json` (not yet read in full in this audit) lists the Electron stack: Electron itself, Vue, electron-builder, and various overlays. Each ships major versions ~yearly. Electron major version bumps frequently require rewriting IPC, security policy, and webview semantics.

`cdp_tool.py:140-155` already shows a coupling to Electron-specific error strings ("Illegal invocation", "GUEST_VIEW_MANAGER_CALL"). Electron upgrade is *not free*.

---

## 7. The Document Processing Dependencies

- `python-docx>=1.1.2`, `python-pptx>=1.0.2`, `pypdf2>=3.0.1`, `openpyxl>=3.1.5`, `odfpy>=1.4.1`, `xlrd>=2.0.2`, `striprtf>=0.0.29`, `lxml>=6.1.0`

Eight document parsers. Each handles one or two formats. Each has its own CVE history (`pypdf2`'s parser has had several malformed-PDF CVEs).

**Risk:** Medium-High collectively. A malformed document fed into the KB ingest can trigger any of these libraries' bugs.

`pypdf2` is the highest risk — it has been *renamed* upstream to `pypdf` (no 2), and `pypdf2` is now legacy. SAP is on the legacy line.

---

## 8. The Surprise Dependencies

A few entries in `pyproject.toml` made me pause:

- `mem0ai==1.0.0` (`pyproject.toml:38`) — **pinned exactly to 1.0.0**. The only exact pin in the whole file. Either there is a known issue with 1.0.1+, or this is a hasty pin that froze updates. mem0 has had several point releases since 1.0.0. SAP is missing all of them.
- `python-a2a[all]>=0.5.6` (`pyproject.toml:26`) — A2A (Agent-to-Agent) library, pre-1.0. Used by `a2a_tool.py` (only 39 lines).
- `nvidia-ml-py>=13.580.82` (`pyproject.toml:57`) — NVIDIA management library. Only useful on systems with NVIDIA GPU. Adds installation friction on non-NVIDIA systems (sometimes fails to install entirely).
- `nest-asyncio>=1.6.0` (`pyproject.toml:21`) — patches asyncio to allow nested `asyncio.run()`. Used because SAP's `MyOpenAICompatibleEmbeddings.embed_query` calls `asyncio.run` from inside a thread context (see `[[2B_RETRIEVAL_INTERFACE]]` §3). This is a *symptom* dependency — it covers up a design issue rather than fixing it.
- `pyinstaller>=6.17.0` (`pyproject.toml:64`) — for packaging. Heavyweight; included in runtime deps when it should be a dev-dep.
- `pip-licenses>=5.5.0` (`pyproject.toml:58`) — for compliance reporting. Also dev-only.

The exact pin on mem0 and the dev-deps mixed into prod deps are smell of a project that hasn't done a dependency hygiene pass.

---

## 9. The Transitive Risk

Even without auditing `uv.lock`, the transitive graph from these 87 direct deps is enormous. LangChain alone pulls dozens of transitive packages, including various LangChain integrations the user may never touch.

Two transitive concerns I can name without reading the lock file:

- **`requests` vs `aiohttp` vs `httpx`** — SAP uses all three. Each pulls its own TLS / DNS / certificate handling. Triple-fingerprinted by remote endpoints, three independent CA stores in memory. Slow audit footprint.
- **`pydantic v1` vs `pydantic v2`** — LangChain ecosystem oscillated between these. SAP appears to be on v2 (FastAPI is v2 native; LangChain has converged). But pre-1.0 LangChain integrations may still pull v1 transitively.

---

## 10. The License Surface

SAP is AGPLv3 (`pyproject.toml:5`). Most deps are MIT / BSD / Apache. Notable exceptions to spot-check:

- `langchain-classic` — MIT
- `discord-py` — MIT
- `slack-sdk` — MIT
- `pyttsx3` — MPL-2.0 (file-level copyleft)
- `qq-botpy` — Apache-2.0
- `wechatbot-sdk` — license must be verified per package release

Per `[[ember:RULES.AI]]` Vow of **Open Knowledge — MIT-friendly recommendations only**, several transitive packages (potentially LGPL ones from the codec stack) would need spot-check before Ember could vendor any of this. Ember's correct posture is **cite, do not vendor**.

---

## 11. Cross-References

- [[55_API_SIMULATION_TRAPS]] — LiteLLM as adapter trust hinge
- [[52_RESOURCE_BUDGETS]] — cold-start cost from these deps
- [[57_FAILURE_TAXONOMY]] — dep-driven failures ranked
- [[20_interface/2B_RETRIEVAL_INTERFACE]] — LangChain ecosystem in detail
- [[hermes:HEM-50_HERMES_RISK_REGISTER]] — Hermes's risk register for comparison

---

## What This Means for Ember

**Adopt:**
- Adopt **LiteLLM as Ember's multi-vendor router** — but pin to a tested minor (`litellm==1.83.x` style), not floor-only. Test before bumping.
- Adopt **MCP for tool transport** — but recognize MCP is pre-stable; pin tightly.
- Adopt **per-vendor SDKs for IM and livestream** — bespoke implementations (Telegram custom, Twitch raw socket) are higher long-term cost than SDK dependencies.

**Adapt:**
- Adapt SAP's broad dep list into a **modular, opt-in adapter pattern**. Ember's base install pulls only the minimum (FastAPI, Pydantic, LiteLLM, MCP). Per-feature adapters (`ember[wechat]`, `ember[discord]`, `ember[livestream]`) install platform deps. Vow of **Modular Authorship** at the dependency layer.
- Adapt the lazy-load pattern (`ClaudeAsOpenAI.py:30-38`) into Ember's adapter loader: install-time `pip install ember[X]` declares interest; runtime lazy-load defers import cost until first use.

**Avoid:**
- **Avoid floor-only pins on fast-moving dependencies** (LiteLLM, MCP, LangChain, fastapi-mcp). Pin to known-tested minor versions; promote intentionally.
- **Avoid mixing dev-deps into runtime deps** (`pyinstaller`, `pip-licenses` in `pyproject.toml:64,58`). Separate `[project.dependencies]` from `[project.optional-dependencies.dev]`.
- **Avoid vendored third-party libraries without an auto-update plan** (`py/blivedm/`). Either pin and document the freeze, or pull from upstream.
- **Avoid `pypdf2` for new code**. Use `pypdf` (the renamed successor).
- **Avoid `nest-asyncio` as a design fix** (`pyproject.toml:21`). The need for it indicates an async/sync boundary error in the consumer. Fix the consumer.
- **Avoid pulling `nvidia-ml-py` unconditionally** (`pyproject.toml:57`). Use a marker or move to optional.
- **Avoid 87 direct dependencies in the base install.** Vow of **Smallness** at the dependency surface. Ember's base should be < 20.

**Invent:**
- **Dependency Tier Map.** Every Ember dep is tagged: `CORE`, `ADAPTER`, `DEV`, `EXTRA`. Base install pulls CORE only. Adapters opt in. The tier is documented per dep. Ember publishes a `DEPENDENCY_TIERS.md` for transparency. SAP's flat 87-dep prod-list is the negative template.

- **Pin-And-Test-Forward CI.** A nightly CI job runs `uv lock --upgrade --upgrade-package X` for one package at a time; runs Ember's test suite; if green, opens a PR. Forward-test rather than forward-break.

- **License Manifest.** Every Ember release ships a `LICENSES.json` with each direct + transitive dep's license. CI fails if a non-MIT-compatible license appears. Vow of **Open Knowledge** at the build layer.

- **Cold-Start Memory Budget.** A test asserts Ember's idle process memory after import is < N MB. Each new dep declares its add-cost in MB. Bloat is visible in PRs. SAP's accumulated cold-start cost from 87 deps is the negative template.

- **Adapter Health Probe at Startup.** Each loaded adapter runs a lightweight probe against the third-party SDK at process start: import + instantiate + assertion that key APIs exist. Drift between Ember's expectations and the SDK's reality surfaces at startup, not at first user interaction.

- **Vendored Code Refresh Policy.** Any vendored third-party code (like SAP's `py/blivedm/`) gets a `VENDORED_FROM.md` with the upstream URL, commit hash, vendor date, and a "review by" date. CI warns when "review by" is past.

- **Critical-Dep Inventory.** Ember keeps a `CRITICAL_DEPS.md` naming the 5-10 deps Ember absolutely cannot survive without. Each gets: maintainer status, last release, breakage history, mitigation if abandoned. SAP's 87 deps with no inventory leaves the operator unprepared for a critical-dep collapse.
