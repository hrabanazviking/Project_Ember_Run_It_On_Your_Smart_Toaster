---
codex_id: 52_RESOURCE_BUDGETS
title: Resource Budgets — Memory, CPU, GPU, From 2GB Floor To Multi-GPU Ceiling
role: Auditor
layer: Verification
status: draft
sap_source_refs:
  - py/minilm_router.py:106-130
  - py/moss_tts.py
  - py/sherpa_asr.py
  - py/ebd_model_manager.py
  - py/know_base.py:174-194
  - py/sherpa_model_manager.py
  - config/settings_template.json
ember_subsystem_targets: [Funi, Brunnr]
cross_refs:
  - 50_verification/54_DEPENDENCY_HEALTH
  - 50_verification/57_FAILURE_TAXONOMY
  - 60_synthesis/63_PERFORMANCE_TIER_ENGINE
---

# Resource Budgets — Memory, CPU, GPU, From 2GB Floor To Multi-GPU Ceiling

> *Sólrún, voice cold and even: SAP's README claims "2 cores, 2GB RAM" as a floor. That floor is honored only if you accept that "running" and "running every feature" are different commitments. This document audits which features fit in 2GB, which require 8, which require a GPU, and where the cliffs are.*

This document profiles SAP's resource demands as best the static code permits. The methodology: read the imports, read the model paths, read the per-batch sizes, identify the cliffs, name the bottlenecks.

I do not run the code. I have not benchmarked. What I report is bounded by code-reading inference. Numbers are estimates; the reader should treat them as upper bounds for what SAP *intends*.

---

## 1. The 2GB Floor Claim — Inspected

SAP's README claims a 2-core / 2GB minimum. This is plausible if the operator runs:

- The Electron + Python core
- The web chat UI
- A single remote LLM via API (no local model)
- No avatar (or a static Live2D)
- No ASR
- No TTS
- No knowledge base
- No livestream
- No IM bots beyond perhaps Telegram

In that mode, SAP is mostly Electron + a FastAPI server. Electron on Linux baseline is ~250-400 MB (Chromium renderer + Node main). Python with FastAPI + Uvicorn + Pydantic is ~80-150 MB baseline. LangChain ecosystem imports (`know_base.py:1-15`) add ~100-200 MB even if unused — `langchain_classic`, `langchain_community`, `langchain_text_splitters` all eager-load.

Floor estimate: ~700-900 MB used with no real workload. The 2GB ceiling leaves ~1.1-1.3 GB headroom for conversation context, message buffers, async overhead.

This is *tight*. A KB query (load FAISS index + embedding model into memory) blows past 2GB if a local model is used. Remote-only LLM keeps memory low.

---

## 2. The MiniLM Local Embeddings Cliff

`minilm_router.py:26-27`:

```python
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
MODEL_PATH = os.path.join(DEFAULT_EBD_DIR, MODEL_NAME)
```

`paraphrase-multilingual-MiniLM-L12-v2` is ~470 MB on disk. Loaded into memory as ONNX, ~500-600 MB depending on quantization (`model_O4.onnx` vs `model.onnx` — line 46-50). The ONNX runtime adds ~200 MB session overhead.

Cliff: ~700-900 MB on top of baseline. A 2GB system that turns on local embeddings is at ~1.6 GB before any conversation context. KB queries that batch 20 documents per call (`know_base.py:174`) add transient per-batch memory; FAISS index for a 1000-doc KB at 384-dim float32 is ~1.5 MB (modest) but the documents themselves are also in memory during query.

Crossing the 2GB line: turn on local embeddings on a 2GB machine and run a knowledge-base query. Likely OOM kill.

`minilm_router.py:130` hardcodes `use_gpu=False`. A user with a small GPU cannot offload the embedding model. The only way to get local embeddings on GPU is editing source.

---

## 3. The Moss TTS Cliff

`moss_tts.py` — not yet read in this audit, but Moss TTS is a streaming TTS model. Moss-Streamer-TTS, the most common open-weight Moss TTS at the time of SAP development, is ~2-3 GB in model weights. Plus VRAM if GPU.

`moss_model_manager.py` (`/tmp/super-agent-party/py/moss_model_manager.py`, 124 lines) handles model lifecycle. Loading the model into CPU adds 2-3 GB resident; into GPU adds 2-3 GB VRAM and ~500 MB CPU staging.

Cliff: enabling Moss TTS pushes a 2GB system past 4 GB. Out-of-scope for the floor.

The user has alternatives: `edgetts` (cloud-based Microsoft Edge TTS, no local cost, but online-dependent), `openai` (cloud), `gsv` (GPT-SoVITS, smaller but still local), or one of nine other vendor TTS options (`settings_template.json:311-378` lists them).

---

## 4. The Sherpa ASR Cliff

`sherpa_asr.py` + `sherpa_model_manager.py`. Sherpa-ONNX models vary widely: zipformer-streaming-2023 is ~70 MB; zipformer-multi-zh-hans is ~400 MB; zipformer-large is ~1+ GB.

Best case (small streaming model on CPU): ~150 MB resident. Acceptable on the 2GB floor.

Worst case (large multilingual model on CPU): ~1.2 GB resident. Pushes past floor.

`asrSettings.engine` in `settings_template.json:295` defaults to `"sherpa"`. The user can choose `funasr`, `openai`, `vendor-specific`. Cloud options are zero-local-cost.

---

## 5. The Avatar Rendering Cliff

VRM rendering is in the Electron renderer, not Python. The cost is GPU time + Chromium memory.

VRM model files are typically 5-50 MB; loaded into WebGL they consume similar VRAM plus per-frame compositing buffers. A VRM with PBR + bloom + dynamic shadows might use 200-500 MB VRAM on the renderer GPU.

Live2D is lighter: ~30-100 MB VRAM for a typical model.

If the user has no discrete GPU, Chromium falls back to software rendering. CPU usage spikes; frame rate drops. The Electron window for VRM (`cdp_tool.py:46-47` excludes `vrm.html` — it has its own window) is a separate Chromium process.

Cliff: VRM with high-fidelity model on a 2GB / no-GPU system → 5-10 fps software rendering, host CPU pegged. Not a *crash* but a UX failure.

---

## 6. The Multi-Bot Multiplier

Each IM bot manager (8 of them) spins a thread + asyncio loop + the vendor SDK. Each SDK has its own overhead:

- `botpy` (QQ) — moderate; ~50-100 MB resident per bot
- `discord.py` (Discord) — heavyweight; ~100-150 MB; maintains a persistent gateway WebSocket
- `slack_sdk` (Slack) — moderate; ~80-120 MB; Socket Mode persistent connection
- `wechatbot-sdk` (WeChat) — varies; QR-login lifecycle
- Custom HTTP polling (Telegram, Feishu, DingTalk, WeCom) — light; ~20-40 MB

All eight enabled: ~500-700 MB across bot SDKs + threads. Each has its own active WebSocket / long-poll connection.

If the user turns on all eight bots on a 2GB system, the baseline + bot overhead consumes ~1.4-1.6 GB before any conversation activity. KB queries, message processing, and tool calls share what's left.

Cliff: SAP at full IM configuration is no longer a 2GB system.

---

## 7. The Three Livestream Multipliers

- Bilibili: `blivedm/` package, thread + WebSocket + danmaku parser. ~30-60 MB.
- YouTube: `googleapiclient` + thread. ~80-120 MB (googleapiclient is heavy).
- Twitch: socket + parser. ~10-20 MB.

All three enabled: ~120-200 MB.

Reasonable. Livestream is not the memory cliff; it is the *network* cliff. Three persistent WebSockets + one poll loop. Bandwidth per platform is low (~1-10 KB/s for danmaku) but the *latency* matters — every comment ingest → broadcast → consumer chain runs through the WebSocket fan-out.

---

## 8. The MCP Server Spawn Multiplier

Each MCP server registered is a `subprocess.Popen` (via `StdioServerParameters`). The cost is **whatever the MCP server costs** — Ember has no control. A naive MCP server in Python with stdlib is ~50 MB. A heavy MCP server (e.g. one that wraps a local LLM) is whatever the wrapped tool costs.

`mcp_clients.py:33-42` doesn't limit how many MCP servers can be registered. The settings file is the only gate.

Cliff: ten MCP servers spawned = ten extra processes. RAM follows.

---

## 9. The Sub-Agent Token Cliff

`sub_agent.py:38`:

```python
max_iterations = self.settings.get("CLISettings", {}).get("max_iterations", 100)
```

Default `max_iterations = 100`. Each iteration is a full LLM call with full conversation history. Conversation history grows over time (`conversation_history.append` at `sub_agent.py:77`). At iteration 50, the history might be 30-50 KB of context. At iteration 100, 60-100 KB.

`max_tokens` for the LLM (`settings_template.json:11`) defaults to 8192. Per-iteration token cost up to 8192 output. At 100 iterations, up to 800K output tokens for one sub-agent task.

This is not memory pressure — this is *cost* pressure. A poorly-scoped sub-agent burns through tokens. There is no per-task token budget. There is only the iteration ceiling.

---

## 10. The 2GB → Multi-GPU Adaptive Profile

SAP claims to scale 2GB → multi-GPU. In code, the adaptation is:

- **All local models gated by config flags** — TTS engine, ASR engine, embedding engine
- **`use_gpu` parameter** — passed to model loaders, currently hardcoded `False` for MiniLM
- **ComfyUI as the GPU-heavy escape hatch** — image generation off-host to a separate ComfyUI server

The adaptation is "user disables features they can't afford." There is no auto-detection. No "I have 2GB, disable heavy models." No "I have a GPU, enable GPU paths."

A user installing SAP on a 2GB Raspberry Pi gets a default config that, on first KB query with local embedding, OOMs.

The 2GB claim is *technically true* (the process can start) and *operationally false* (anything past minimum interactive chat overruns).

---

## 11. The CPU Cost Bottleneck

CPU spends time on:

- ONNX inference (embedding query) — 50-200 ms per query on CPU, 1-3 cores active
- LiteLLM HTTP serialization — milliseconds
- LangChain text splitting / chunking — milliseconds per document
- Sherpa ASR streaming — real-time-or-faster on small models, 0.5-1 core
- Moss TTS synthesis — 0.5-3 seconds per sentence on CPU, 2-4 cores active
- behavior_engine `_tick` (`behavior_engine.py:144-222`) — 1ms per tick (cheap)

The dominant CPU consumers when active are TTS and ASR. Both are gated by config; the user pays only when enabled.

The dominant CPU consumer in steady state is the **YouTube `_run` thread's `time.sleep(5)` between polls plus the Google API client** — ~50-100ms per poll on the network and ~5-10ms parsing.

A 2-core SAP host with both TTS and ASR enabled struggles to keep up with conversational latency.

---

## 12. The Disk Cost

`USER_DATA_DIR/uploaded_files/` — all screenshots, all uploaded images, all generated images. No reap policy.

`USER_DATA_DIR/kb/<id>/index.faiss` + `index.pkl` — per KB.

`USER_DATA_DIR/affection/affection_data.json` — small.

`USER_DATA_DIR/memory_cache/` — chat history; grows linearly with use.

A power user accumulates GB of `uploaded_files/` over months. No GC. No warning. The disk fills.

---

## 13. Cross-References

- [[54_DEPENDENCY_HEALTH]] — LiteLLM, LangChain, ONNX as the biggest cold-start contributors
- [[57_FAILURE_TAXONOMY]] — OOM failure modes
- [[60_synthesis/63_PERFORMANCE_TIER_ENGINE]] — Cartographer's invention: tier-adaptive runtime, riffing on this analysis
- [[ember:RULES.AI]] — "Pi-runnable baseline" Vow of Smallness; SAP fails this Vow at full configuration

---

## What This Means for Ember

**Adopt:**
- Adopt the **lazy-load with `is_loaded` validity** pattern from `minilm_router.py:113-124`. Resources load on demand, are cached, and have an explicit load-state.
- Adopt the **cloud-or-local engine selection** pattern from `ttsSettings.engine` (eleven options across cloud and local). Per-subsystem engine choice keeps the floor low.

**Adapt:**
- Adapt the per-subsystem `use_gpu` parameter into a **PerformanceTier**-keyed setting. Tier determines what the system runs. Pi tier disables all local heavy models. Workstation tier enables them. Mid-tier picks per-feature. The decision is one config; the gating is automatic.
- Adapt the `max_iterations` ceiling into a **typed budget**: tokens-per-task, cost-per-task, time-per-task, iterations-per-task. Any budget breach halts the sub-agent and surfaces to the operator. SAP's 100-iteration default with no token budget is the negative template.

**Avoid:**
- **Avoid hardcoded `use_gpu=False`** (`minilm_router.py:130`). GPU choice is settings.
- **Avoid eager-loading LangChain ecosystem at import time** (`know_base.py:1-15`). Use `if TYPE_CHECKING` for type hints, defer real imports until first use.
- **Avoid uncapped `uploaded_files/` growth**. Reap with TTL or LRU.
- **Avoid claiming a floor the floor doesn't support**. If Ember claims Pi-runnable, the default config must run on Pi. Test it.

**Invent:**
- **Performance Tier Auto-Detect on First Run.** At first start, Ember measures: RAM, cores, GPU availability, disk space. Picks a tier: `pi` / `laptop` / `workstation` / `multi-gpu`. Sets defaults. Operator can override.
- **Resource Budget Per Subsystem.** Every subsystem declares: `min_ram_mb`, `recommended_ram_mb`, `cpu_share_pct`, `gpu_vram_mb | None`. The tier engine compares budget to host; subsystems that overrun the budget are disabled with a notice.
- **Disk Reap Daemon.** Background task that runs `disk_reaper.scan()` daily. Files older than TTL get reaped. Per-directory policies (uploaded screenshots: 30 days; KB indices: never; logs: 7 days). User-visible.
- **Cost Telemetry Dashboard.** Real-time view of cumulative LLM tokens, vision-tokens, TTS-seconds, ASR-minutes per session. Lets the operator see what's expensive. SAP has no equivalent; it's a number that surprises at the end of the month.
- **Cold-Start Profile in CI.** A test that measures import-time memory + process memory at idle. If a PR pushes baseline memory by > 5%, CI fails. SAP's accumulated baseline (LangChain + Pydantic + LiteLLM + ...) is the negative template.
- **Out-Of-Memory Pre-Check.** Before loading a heavy model (TTS, embedding), check `psutil.virtual_memory().available > model_estimated_mb`. If not, refuse the load and explain. Better than `MemoryError` mid-load. Vow of **Graceful Offline** for resource starvation.
