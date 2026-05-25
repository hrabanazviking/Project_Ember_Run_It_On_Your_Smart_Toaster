---
name: sap-codex-shared-context
description: Briefing every Mythic Engineering agent reads before authoring any sap_codex document
metadata:
  codex: sap
  type: meta
---

# SHARED_CONTEXT — Super Agent Party Codex

This brief is read by every agent before they begin authoring. It is the common ground.

---

## 1. What Super Agent Party (SAP) Is

**Repository:** `heshengtao/super-agent-party` — cloned at `/tmp/super-agent-party/`
**Version studied:** v0.4.2-preview (May 2026)
**License:** AGPLv3 (with commercial licenses available — we will **cite, not vendor**)
**Self-description:** "All-in-one AI companion! Super Agent Party = Self hosted neuro sama + openclaw!"

**What it actually is:** an Electron + Python desktop AI companion framework with:

- **Avatar embodiment** — VRM models, Live2D, VTube Studio control, VMC protocol bidirectional streaming to OBS
- **Agent task center** — autonomous background tasks via MCP servers and Agent Skills
- **Computer control** — desktop vision + mouse + keyboard + terminal toolchain (`computer_use_tool.py`, `cli_tool.py`)
- **Multi-role group chat** — Tavern character card support with long-term memory
- **8 IM bot platforms** — QQ, WeChat, Feishu, DingTalk, Telegram, Discord, Slack, WeCom (one-click deployment)
- **3 livestream platforms** — Bilibili (blivedm), YouTube (ytdm), Twitch (twitch_service) with 360° panoramic streaming
- **AI browser** — agent-controlled browser via Chrome DevTools Protocol (`cdp_tool.py`)
- **Extension system** — installable extensions with independent windows / sidebar modes; multi-instance capable
- **OpenAI-compatible API + MCP server surface** — `ClaudeAsOpenAI.py`, `GeminiAsOpenAI.py`, `dify_openai.py`
- **Affection system** — `affection_api.py` + `affection_system.py` — actual emotional state mechanics
- **Behavior engine** — `behavior_engine.py` + `autoBehavior.py` — autonomous behavior loops
- **Voice** — `moss_tts.py` + `sherpa_asr.py` + their model managers
- **Knowledge** — `know_base.py` + `minilm_router.py` + `ebd_*` embedding stack
- **Cross-platform** — Win10/11 + Server 2025, macOS M-chip, Linux (AppImage/.deb), Docker, Docker Compose with gateway

Hardware floor: **2 cores, 2GB RAM**. Hardware ceiling: open (multi-GPU workstation, anything Electron+Python can use).

## 2. What Ember Is

Ember is a small-and-tethered AI agent forked from Runa, located at `~/ai/ember`. Six True Names (current):

- **Funi** — the spark (entrypoint / orchestrator)
- **Strengr** — the thread (reasoning loop / agent kernel)
- **Brunnr** — the well (external knowledge / Gungnir DB)
- **Smiðja** — the forge (tool execution / sandbox)
- **Hjarta** — the heart (affect, intent, memory bias)
- **Munnr** — the mouth (output, surface, expression)

Three Realms (current): **Spark / Thread / Well**.

Ember's identity is **small, tethered, doc-rich, code-empty** (first slice ratification-gated since 2026-05-21). The Hermes Codex (Wave 1) and Peer Codex (Wave 2) have already produced True-Name and Vow proposals; this codex (Wave 3) refines or contests them.

Ember's home is currently a single laptop (Kubuntu 26.04 + RTX 2060, ~/ai/ember/) but the design must allow Ember to live across many devices simultaneously when present.

## 3. What This Codex Is For

To **distill SAP into the deepest source of teaching available to Ember for the embodiment, reach, and affect axes** — three areas where Hermes (pure LLM loop) and the Peer Codex (Letta + smolagents + Goose, also pure-LLM) gave us almost nothing.

Specifically:
- **Embodiment** — SAP's avatar / voice / behavior stack is unique among open-source agent frameworks
- **Reach** — no other open-source agent ships 8 IM bots + 3 livestream platforms
- **Affect** — the `affection_*` modules are an actual code-level emotional state machine

We are not copying SAP. We are **understanding it deeply, finding its mistakes, and inventing better methods**.

## 4. How to Cite

Every claim about SAP must be backed by a citation. Format:

```
`/tmp/super-agent-party/py/affection_system.py:142` — `class AffectionState` defines decay rate
```

Or for multi-line:
```
`server.py:2410–2438` — sub-agent spawn lifecycle (`spawn_sub_agent`)
```

**Never** paraphrase marketing copy from `README.md`. Always read the actual code, configs, or skill manifests and cite from there.

If a marketing claim cannot be verified in code, mark it explicitly: `[unverified — README claim only]`.

## 5. Style — The "What This Means for Ember" Closer

Every doc ends with a section titled exactly:

```
## What This Means for Ember
```

This section contains:
- **Adopt** — patterns Ember should take wholesale
- **Adapt** — patterns Ember should take but transform
- **Avoid** — patterns Ember should reject and why
- **Invent** — novel patterns this analysis suggests but SAP did not implement

Be concrete. Name files. Name modules. Name proposed True Names if a new domain demands one.

## 6. Cross-Linking Convention

Within the codex use `[[slug]]` to link to another doc by its slug (filename minus `.md`). Example: `[[1A_AFFECTION_DOMAIN]]`.

Cross-codex links:
- To Hermes Codex: `[[hermes:HEM-23_HOTSWAP]]` (slug from `docs/hermes_codex/meta/MANIFEST.md`)
- To Peer Codex: `[[peer:LETTA-2_SLEEPER]]`
- To root Ember docs: `[[ember:CROSS_PLATFORM_PLAN]]`

The Scribe verifies all links resolve on the final pass.

## 7. Vows in Force

Read `~/ai/ember/RULES.AI.md` and `~/ai/ember/PHILOSOPHY.md` for the immutable Vows. Highlights:

- **Smallness** — Pi-runnable baseline
- **Tethered Grounding** — Well (external knowledge) is canonical
- **Graceful Offline** — every network-dependent surface must degrade
- **Pluggable Storage** — no single-backend lock-in
- **Modular Authorship** — every borrowed subsystem optional
- **Public-Friendliness** — readable surface for non-experts
- **Flexible Roots** — no absolute paths
- **Open Knowledge** — MIT-friendly recommendations only
- **Cache Discipline** *(proposed)* — every cache has TTL + invariant
- **Defended System Prompt** *(proposed)* — typed instruction entry

## 8. Threat Awareness

SAP's surface is dangerous if uncritically copied:
- **Computer control + smart home + 8 IM bots = enormous attack surface**
- **Long-term memory + livestream = privacy nightmare**
- **Affection state could be used to manipulate users (gacha pattern)**
- **OpenAI-compat API simulation layers are famously leaky** (think token counting, system prompt handling)

The Auditor's verification docs (`50_*`) are where these are catalogued in depth. Every doc in any layer should at least notice when it is touching dangerous territory.

## 9. Do Not Touch

- Ember source code (`~/ai/ember/src/`, sibling project folders)
- Ember's existing slice plan
- Hermes Codex docs (`docs/hermes_codex/`)
- Peer Codex docs (`docs/peer_codex/`)
- Anything outside `docs/sap_codex/`

Propose changes — never enact them.

## 10. If You're Stuck

- Read `meta/MANIFEST.md` for the full doc list and your assigned slugs.
- Read `meta/STYLE_GUIDE.md` for tone, length, structure.
- Read one of the existing Hermes Codex docs (e.g. `docs/hermes_codex/00_vision/00_OVERTURE.md`) for the established voice.
- If a doc's scope grows beyond ~4,000 words, split it (`<slug>_A.md` / `<slug>_B.md`) and update the manifest.
- If you run out of budget mid-doc, leave a `## Continuation Notes` block at the bottom for the next agent.
