---
name: chatdoll-codex-shared-context
description: Briefing every Mythic Engineering agent reads before authoring any chatdoll_codex document
metadata:
  codex: chatdoll
  type: meta
---

# SHARED_CONTEXT — Chatdoll Codex

Read this before authoring any doc.

---

## 1. What ChatdollKit Is

**Repository:** `uezo/ChatdollKit` — cloned at `/tmp/ChatdollKit/`
**Version studied:** v0.8.16 (Feb 14, 2026)
**Stars/forks:** 1.2k / 117
**Commits:** 1,157 total — mature, actively maintained
**License:** **Apache-2.0** (confirmed at `/tmp/ChatdollKit/LICENSE`) — adopt-friendly
**Author:** uezo (also maintains ChatMemory, AIAvatarKit, AITuber Controller, OshaberiAI iOS app)
**Self-description:** "3D virtual assistant SDK that enables you to make your 3D model into a voice-enabled chatbot."

**Total size:** 18,221 C# LOC across 121 files + JavaScript bridges + Unity asset metadata. The Scripts/ tree is well-organized:

```
Scripts/
├── AIAvatar.cs              ← top-level controller
├── Dialog/                  ← dialog state machine
│   └── MessageWindow/
├── IO/                      ← MicrophoneManager, devices
├── LLM/                     ← LLMService + per-provider
│   ├── ChatGPT/
│   ├── Claude/
│   ├── Gemini/
│   ├── Dify/
│   └── AIAvatarKit/
├── Model/                   ← ModelController, animation, expression
├── Network/                 ← SocketServer, JavaScriptMessageHandler
├── SpeechListener/          ← STT pipeline, multi-VAD
├── SpeechSynthesizer/       ← TTS, parallel/sequential prefetch
└── UI/
```

**13 named subsystems** (from README): AIAvatar, ModelController, DialogProcessor, SpeechListener, SpeechSynthesizer, MicrophoneManager, LLMService, Tool/ToolBase, SocketServer, JavaScriptMessageHandler, SileroVADProcessor, ModelRequestBroker, DialogPriorityManager, ChatMemoryIntegrator.

**Multi-platform:** Windows, macOS, Linux, iOS, Android, VR, AR, WebGL (the widest cross-platform reach of any embodiment-axis source we've studied).

**Multi-LLM:** ChatGPT, Claude, Gemini, Dify, Grok (via OpenAI-compat), Command R (experimental), arbitrary OpenAI-compat endpoints.

**Multi-TTS:** Google, Azure, OpenAI, Watson, **VOICEVOX, AivisSpeech, Aivis Cloud API, VOICEROID, Style-Bert-VITS2, NijiVoice** (a deep Japanese voice ecosystem — the under-served stack in Western codexes).

**Multi-STT:** Google, Azure, OpenAI, **Silero VAD** (ML-based), AIAvatarKit streaming.

## 2. What Ember Is

Same as previous codexes — small-and-tethered AI agent at `~/ai/ember`, Six True Names (Funi/Strengr/Brunnr/Smiðja/Hjarta/Munnr), doc-rich + code-empty, ratification-gated slice plan.

Wave 3 (SAP) proposed Andlit/Rödd/Hugarsýn. Wave 4 (Waifu) proposed Andlit-realtime + Rödd-realtime sub-names and Tier-CLOUD as parallel axis. **This codex (Wave 5)** proposes Andlit-unity and Rödd-unity (Unity-native local rendering tier, distinct from electron-local and cloud-streaming).

## 3. What This Codex Is For

To complete the **three-corpus embodiment triangulation**:

| Axis | Source | Codex | Runtime |
|---|---|---|---|
| Electron desktop | SAP (heshengtao/super-agent-party) | Wave 3 | Electron + Python |
| Cloud streaming | Waifu (ZeroWeight kit) | Wave 4 | Browser + WebRTC + cloud avatar |
| **Unity-native local** | **CDK (uezo/ChatdollKit)** | **Wave 5 (this)** | **Unity + VRM + local rendering** |

Each axis has different cost, latency, privacy, hardware, and platform profiles. Ember's design needs evidence for choosing which.

ChatdollKit also adds dimensions the other two skipped:
- **Mobile native** (iOS + Android via Unity)
- **XR** (VR + AR)
- **WebGL** (browser-deployed Unity)
- **Streaming-broadcast** (VTuber via sister project)
- **Japanese voice stack** (10+ providers vs Western 3-4)

## 4. How to Cite

Per STYLE_GUIDE §4. Real `path:line` from `/tmp/ChatdollKit/`. Example:

```
`/tmp/ChatdollKit/Scripts/AIAvatar.cs:142` — `OnUpdate` dispatches to current dialog state
`/tmp/ChatdollKit/Scripts/LLM/ChatGPT/ChatGPTService.cs:88` — function-call adapter
```

For Unity-specific concepts (asmdef, MonoBehaviour lifecycle, ScriptableObject), cite Unity official docs when needed.

For sister projects (ChatMemory, AIAvatarKit, AITuber Controller), clone or fetch as needed and cite with the sister-repo prefix:

```
`/tmp/ChatMemory/server/main.py:50` — episodic store FastAPI route
```

(Forge-B will clone these as needed.)

README claims marked `[unverified — README claim only]`.

## 5. Style — The "What This Means for Ember" Closer

Per STYLE_GUIDE §5. Apache-2.0 means **Adopt** entries can include kit-adapted patterns with attribution, distinct from Waifu's study-only. Format:

```
## What This Means for Ember

**Adopt:** <patterns to take wholesale — Apache-2.0 sources can be cited and adapted with attribution>
**Adapt:** <patterns to take and transform>
**Avoid:** <patterns to reject, with reason>
**Invent:** <novel patterns this analysis suggests>
```

At least one **Invent** per doc.

## 6. License Posture — APACHE-2.0 (adopt-friendly)

Distinct from Waifu Codex's study-only stance:

- **Adopt freely** with attribution (NOTICE file or commit message)
- **Vendor patterns** — yes, with proper attribution
- **Cite line by line** — yes
- **Derive new code** — yes
- **Re-license derivatives** — yes (Apache-2.0 is permissive)

When proposing adopt-list patterns, note "Apache-2.0 attribution required" once per doc.

## 7. Cross-Linking Convention

Within: `[[slug]]`. Across:
- `[[sap:slug]]` → SAP Codex
- `[[waifu:slug]]` → Waifu Codex (Wave 4 immediate predecessor on the embodiment axis)
- `[[hermes:slug]]` → Hermes Codex
- `[[peer:slug]]` → Peer Codex (scaffold-only)
- `[[kloinn:slug]]` → Klóinn Codex
- `[[ember:slug]]` → root or `docs/`
- `[[chatdoll:slug]]` → this codex (bare `[[slug]]` also resolves)

Synthesis docs especially should cross-link to SAP + Waifu for triangulation.

## 8. Three-Corpus Triangulation — Use It Heavily

The synthesis layer is where this codex earns its keep. Compare:

- **AIAvatar** (CDK) ↔ **ModelController** (SAP avatar) ↔ **LiveKitAvatarSession** (Waifu)
- **LLMService** (CDK, 6+ providers) ↔ **ClaudeAsOpenAI/GeminiAsOpenAI** (SAP, API simulation) ↔ ZeroWeight cloud LLM (Waifu, black box)
- **SpeechListener + SileroVADProcessor** (CDK, ML-based VAD) ↔ **sherpa_asr.py** (SAP, k2-sherpa) ↔ browser mic + cloud STT (Waifu)
- **SpeechSynthesizer** (CDK, 10+ TTS) ↔ **moss_tts.py** (SAP, MOSS) ↔ cloud TTS (Waifu)
- **`[anim:Name]` + `[face:Expression]` tags** (CDK) ↔ **VRM action vocabulary** (SAP) ↔ `embarrassed`/`dance`/`wave_hand` (Waifu typed API)
- **SocketServer + JavaScriptMessageHandler** (CDK, dual remote control) ↔ **MCP + A2A** (SAP) ↔ LiveKit data channel (Waifu, inferred)

Every domain doc should reference at least one SAP slug and one Waifu slug for triangulation.

## 9. Threat Awareness

Even Apache-2.0 + Unity has dangerous surfaces:
- **LLM API keys** in client builds (the Waifu pattern problem recurs)
- **SocketServer** opens local TCP port — auth posture?
- **JavaScriptMessageHandler** in WebGL — XSS / message origin
- **Mobile** — iOS permissions, Android permissions
- **VR/AR** — sensor data exfil paths
- **Multi-LLM** — provider-specific function-call format leaks

The Auditor's verification layer catalogs these.

## 10. Do Not Touch

- Ember source code, slice plan, sibling codexes (Hermes/Peer/SAP/Waifu/Klóinn)
- Anything outside `docs/chatdoll_codex/`

Propose; never enact.

## 11. Sister Projects (Forge-B + select Architect docs)

- **ChatMemory** (https://github.com/uezo/chatmemory) — episodic memory service for ChatdollKit; Hjarta-pattern reference
- **AIAvatarKit** (https://github.com/uezo/aiavatarkit) — Speech-to-Speech pipeline; streaming STT server; Rödd-streaming pattern
- **AITuber Controller** (https://github.com/uezo/chatdollkit-aituber) — VTuber streaming integration; Boðr-broadcast pattern
- **OshaberiAI** — iOS app shipping ChatdollKit + VOICEVOX in production

Forge-B gets the sister-project execution docs. Architect references them in domain-layer docs but doesn't deep-dive.
