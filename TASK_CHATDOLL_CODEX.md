# TASK: Chatdoll Codex — Mining ChatdollKit for Ember's Unity-Native Embodiment Axis

**Started:** 2026-05-25
**Owner:** Volmarr + seven Mythic Engineering agents (six roles, Forge doubled)
**Status:** Authoring (parallel) — pending agent dispatch
**Branch:** `development`
**Sibling codexes:** `docs/hermes_codex/` (58), `docs/peer_codex/` (scaffold), `docs/kloinn/` (57), `docs/sap_codex/` (84), `docs/waifu_codex/` (22)

---

## Scope

Read the ChatdollKit codebase (`uezo/ChatdollKit`, cloned to `/tmp/ChatdollKit/`) and produce a structured corpus of **63 content MD documents** under `docs/chatdoll_codex/` that distill what this mature Unity-based 3D avatar SDK teaches Ember about:

- **Unity-native local embodiment** — a third position on the embodiment axis (SAP = Electron desktop / Waifu = cloud streaming / **CDK = Unity-native local**)
- **Multi-platform reach** — Windows, macOS, Linux, iOS, Android, VR, AR, WebGL (the widest cross-platform surface of any embodiment codex source)
- **Multi-LLM choreography** — ChatGPT, Claude, Gemini, Dify, Grok, Command R via a unified `LLMService` abstraction
- **Japanese voice ecosystem** — VOICEVOX, AivisSpeech, Aivis Cloud API, VOICEROID, Style-Bert-VITS2, NijiVoice (the under-served voice stack in Western codexes)
- **Multimodal pipeline** — STT → LLM → TTS + animation (`[anim:Name]`) + face tags (`[face:Expression]`) + lip-sync (uLipSync) + VAD (Silero ML-based)
- **Sister projects ecosystem** — ChatMemory (episodic memory), AIAvatarKit (S2S streaming), AITuber Controller (VTuber streaming), OshaberiAI (iOS app)

The codex completes a **three-corpus embodiment triangulation** (SAP × Waifu × CDK) that lets Ember choose Andlit + Rödd implementation paths with full evidence.

## License posture

**Apache-2.0** — confirmed at `/tmp/ChatdollKit/LICENSE`. Permissive; commercial use allowed; adopt-list freedom restored vs Waifu's study-only posture. Citations + pattern adoption + code adaptation all acceptable with attribution.

## Method

Seven Mythic Engineering agents work in parallel — six roles, **Forge doubled** for execution-layer breadth. Each reads `meta/SHARED_CONTEXT.md`, `meta/MANIFEST.md`, `meta/STYLE_GUIDE.md` before starting.

| Agent | Role | Layer | Docs | Folder |
|---|---|---|---|---|
| 1 | Skald — Sigrún Ljósbrá | Vision | 5 | `00_vision/` |
| 2 | Architect — Rúnhild Svartdóttir | Domain + Interface (architect-owned) | 14 + 5 = 19 | `10_domain/` + 5× `20_interface/` |
| 3 | Cartographer — Védis Eikleið | Synthesis (cartographer-owned) | 6 | 6× `60_synthesis/` |
| 4 | Forge-A — Eldra Járnsdóttir (fire) | Execution (core) | 8 | `30_execution/` core |
| 5 | Forge-B — Eldra Járnsdóttir (iron) | Execution (sister + platform) | 6 | `30_execution/` sister+platform |
| 6 | Auditor — Sólrún Hvítmynd | Verification + Interface (auditor-owned) | 8 + 5 = 13 | `50_verification/` + 5× `20_interface/` |
| 7 | Scribe — Eirwyn Rúnblóm | Synthesis (scribe-owned) + meta finalization | 6 + 3 = 9 | 6× `60_synthesis/` + meta finalization |

**Push cadence:** agents write files only. Orchestrator commits + pushes per layer (six commits). Final Scribe pass for INDEX/READING_ORDER/CROSS_AGENT_NOTES = seventh commit. Pull-rebase between pushes because the repo has had concurrent activity in recent sessions.

## What Exists Now

- `/tmp/ChatdollKit/` — full clone, 18,221 C# LOC across 121 files; Apache-2.0; 1,157 commits; v0.8.16 (Feb 2026)
- `Scripts/` subsystems: `Dialog/`, `IO/`, `LLM/` (ChatGPT/Claude/Gemini/Dify/AIAvatarKit subdirs), `Model/`, `Network/`, `SpeechListener/`, `SpeechSynthesizer/`, `UI/`, plus top-level `AIAvatar.cs`
- `~/ai/ember/docs/chatdoll_codex/` — empty scaffold with subdirs ready
- This TASK file
- `meta/SHARED_CONTEXT.md`, `meta/MANIFEST.md`, `meta/STYLE_GUIDE.md` — next to write

## What Is Needed

- **63 MD docs**, each **1,500–4,000 words** (back to SAP range; source is large enough)
- Citations to real source files with line numbers
- Apache-2.0 means **Adopt freely with attribution** — distinct from Waifu's study-only
- Three-corpus triangulation in synthesis layer: SAP local / Waifu cloud / CDK Unity-native
- ADRs for adoption decisions; comparative evidence across the three embodiment sources

## Non-Goals

- Do NOT modify Ember source code
- Do NOT modify existing Ember docs outside `docs/chatdoll_codex/`
- Do NOT modify the slice plan (propose-only)
- Do NOT modify sibling codexes (Hermes, Peer, SAP, Waifu, Klóinn)
- Do NOT paraphrase the README — cite actual `.cs` files

## Vows Honored

All existing Vows in force. The newly-landed **Absolute Boundary Directive** in `RULES.AI.md` is binding: *"NEVER assume the user wants code. If the user asks for documents, plans, or research, stick strictly to generating those documents."* This codex IS that documents/plans/research work.

- **Open Knowledge** — Apache-2.0 source = adopt-friendly
- **Smallness** — every Ember proposal must remain Pi-runnable in baseline; Unity-tier features are explicitly *optional*
- **Tethered Grounding** — Hjarta integration with ChatMemory pattern must respect the external Well
- **Graceful Offline** — cloud LLM dependencies must fail gracefully
- **Pluggable Storage** — no proposal locks Ember to Unity, to VRM, or to any specific LLM
- **Modular Authorship** — every borrowed subsystem optional / individually swappable
- **Public-Friendliness** — user surface remains readable
- **Flexible Roots** — no absolute paths
- **License-Aware Study Posture** *(Waifu-proposed)* — Apache-2.0 here means adopt-list freedom restored

## Next Steps After Authoring

1. Volmarr reviews `60_synthesis/` synthesis docs, especially the three-corpus triangulation
2. Per-layer commits + push (6 commits) + final Scribe pass commit
3. DEVLOG entry
4. Memory updates ([[project-chatdoll-codex]], [[reference-chatdoll-codex-findings]])

## Continuation Notes

If an agent runs out of budget mid-doc, leave a `## Continuation Notes` block at the bottom. No silent truncation.
