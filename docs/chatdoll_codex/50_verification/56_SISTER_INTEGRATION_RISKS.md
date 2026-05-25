---
codex_id: 56_SISTER_INTEGRATION_RISKS
title: Sister Integration Risks — ChatMemory, AIAvatarKit, AITuber Controller, And The Single-Maintainer Coupling They Share
role: Auditor
layer: Verification
status: draft
chatdoll_source_refs:
  - /tmp/ChatdollKit/Extension/ChatMemory/ChatMemoryIntegrator.cs:10-108
  - /tmp/ChatdollKit/Extension/ChatMemory/ChatMemoryTool.cs
  - /tmp/ChatdollKit/Scripts/SpeechSynthesizer/AIAvatarKitSpeechSynthesizer.cs:15-131
  - /tmp/ChatdollKit/Scripts/SpeechListener/AIAvatarKitSpeechListener.cs:11-73
  - /tmp/ChatdollKit/Scripts/SpeechListener/AIAvatarKitStreamSpeechListener.cs:11-375
  - /tmp/ChatdollKit/Scripts/LLM/AIAvatarKit/AIAvatarKitService.cs
sister_source_refs:
  - /tmp/chatmemory/setup.py:5 (version 0.2.8)
  - /tmp/chatmemory/chatmemory/chatmemory.py
  - /tmp/aiavatarkit/setup.py:5 (version 0.8.17)
  - /tmp/aiavatarkit/aiavatar/sts/pipeline.py
  - /tmp/chatdollkit-aituber/setup.py:5 (version 0.2.4)
  - /tmp/chatdollkit-aituber/chatdollkit_aituber/client.py
  - /tmp/chatdollkit-aituber/chatdollkit_aituber/api.py
ember_subsystem_targets: [Funi, Hjarta, Munnr, Rödd, Strengr]
cross_refs:
  - 30_execution/38_CHATMEMORY_INTEGRATION
  - 30_execution/39_AIAVATARKIT_STREAMING
  - 30_execution/3A_AITUBER_CONTROLLER
  - 20_interface/27_SOCKET_PROTOCOL
  - 50_verification/50_DEPENDENCY_HEALTH
  - 50_verification/51_SECURITY_REVIEW
  - 50_verification/57_FAILURE_TAXONOMY
---

# Sister Integration Risks — ChatMemory, AIAvatarKit, AITuber Controller, And The Single-Maintainer Coupling They Share

> *Sólrún, voice cold and even: ChatdollKit does not stand alone. Memory is delegated to `uezo/chatmemory`. Streaming STT, the Speech-to-Speech pipeline, and the optional alternative dialog backend live in `uezo/aiavatarkit`. VTuber broadcast orchestration is `uezo/chatdollkit-aituber`. iOS production is `OshaberiAI`. Five repos. Five `setup.py` files. Four GitHub release histories that drift independently. One maintainer — `uezo@uezo.net` — listed as author on every one. The audit posture is: the kit-of-kits is held together by a single human's release discipline, and the human's release discipline is generous but not protocol-versioned. When uezo changes ChatMemory's `/search` response shape, three downstream consumers must update in step. There is no contract. There is `setup.py` `version =` and the GitHub commit history. That is the integration risk surface.*
>
> *This document maps the coupling: who depends on whom, where the contracts are, where the version drift will bite, and what Ember inherits if Ember adopts the kit-of-kits posture wholesale. The conclusion is that Ember must adopt the* `pattern` *but not the* `coupling` *— take the architecture (two-process separation, FastAPI services, sister-project plug-ins) without taking the implicit shared-maintainer trust chain.*

This document audits ChatdollKit's sister-project ecosystem as a coupling graph. Each sister is named, version-pinned at the time of writing, its dependency on CDK or CDK on it is traced, the breaking-change history is reviewed where available, and the failure mode at version drift is recorded. The execution-side reads are in `[[38_CHATMEMORY_INTEGRATION]]` (Forge-B), `[[39_AIAVATARKIT_STREAMING]]` (Forge-B), and `[[3A_AITUBER_CONTROLLER]]` (Forge-B). Here I focus on the *integration risk* — what breaks when versions drift, what the operator must verify, what Ember should refuse to inherit.

---

## 1. The Five Repos, Versions Verified

Versions checked at HEAD as of the corpus cut, 2026-Q1:

| Repo | Version | Most-recent commit | LOC | License |
|---|---|---|---|---|
| `uezo/ChatdollKit` | v0.8.16 (per Scribe meta) | Feb 14 2026 | 18,221 C# | Apache-2.0 |
| `uezo/chatmemory` | 0.2.8 | `89c35d3 Update for v0.2.8` | 1,451 Python (single file) | Apache-2.0 |
| `uezo/aiavatarkit` | 0.8.17 | `96b051f Merge pull request #369 from uezo/develop` | ~10k Python | Apache-2.0 |
| `uezo/chatdollkit-aituber` | 0.2.4 | `769e428 Merge pull request #6 from buchizo/support-azure-openai-from-aituber-controller` | 346 Python | Apache-2.0 |
| `uezo/OshaberiAI` | (iOS production app; not cloned) | (closed-source/proprietary) | unknown Swift | unknown |

`setup.py` references for the verifiable versions:

- `/tmp/chatmemory/setup.py:5` — `version="0.2.8"`.
- `/tmp/aiavatarkit/setup.py:5` — `version="0.8.17"`.
- `/tmp/chatdollkit-aituber/setup.py:5` — `version="0.2.4"`.

CDK itself uses Unity's UPM/asmdef tracking rather than a Python `setup.py`; the v0.8.16 figure comes from the SHARED_CONTEXT meta document and the README's mention of release history. **There is no shared compatibility matrix** — no document anywhere in any of the repos says "ChatdollKit 0.8.x is compatible with ChatMemory 0.2.x and AIAvatarKit 0.8.x." Operators infer compatibility from publication-date proximity and README mentions.

The numerical coincidence — ChatdollKit 0.8.16 and AIAvatarKit 0.8.17 share a major/minor — *is meaningful*. uezo has historically aligned the minor versions across CDK and AIAvatarKit. ChatMemory tracks its own 0.x line. AITuber Controller tracks its own 0.x line. Three independent versioning streams that must compose.

---

## 2. The ChatMemory Coupling — Narrow And Stable

`/tmp/ChatdollKit/Extension/ChatMemory/ChatMemoryIntegrator.cs:10-108` is the entire CDK-side interface to ChatMemory. The execution-side read (`[[38_CHATMEMORY_INTEGRATION]]`) covers the architecture; here the question is *coupling*.

### 2.1 The Wire Surface

CDK posts to two endpoints on the ChatMemory FastAPI server:

- `POST /history` with `{user_id, session_id, messages: [{role, content}, ...], channel}`. (`ChatMemoryIntegrator.cs:20-54`.)
- `POST /search` with `{user_id, query, top_k}` and reads `{answer, retrieved_data}`. (`ChatMemoryIntegrator.cs:56-95`.)

Two endpoints. Two payload shapes. The wire surface is narrow.

ChatMemory v0.2.8's FastAPI router defines both endpoints at `chatmemory.py:1140-1451`. The shapes match. The coupling is stable as long as ChatMemory keeps the endpoint paths and payload field names.

### 2.2 The Breaking-Change Risks

ChatMemory is a single-file 1,451-line Python service. Breaking changes are localized to one file but unconstrained by contract.

Concrete risks observable in the code:

- **The `/search` response shape carries `answer` (string) and `retrieved_data` (dict) at root.** If ChatMemory 0.3.0 nests these under a `data` envelope (a common API maturation step), the C# `SearchResult` typed deserialization (`ChatMemoryIntegrator.cs:79-83`) breaks. The C# class is hardcoded to the flat shape.
- **The embedding dimension is set at table-create time** (per `[[38_CHATMEMORY_INTEGRATION]]` analysis). If ChatMemory 0.3.0 changes the default embedding model (from `text-embedding-3-small` → `text-embedding-4` when OpenAI ships it), and the operator does not re-run `init_db()` with the new dimension, every search returns `vector dimension mismatch` errors. The C# integrator does not see the dimension; the failure is server-side and surfaces as an HTTP 500.
- **The `metadata JSONB` field on `diaries`** is currently open-ended. If ChatMemory 0.3.0 introduces required keys, existing CDK clients that don't supply them get 422 validation errors. The C# integrator does not send `metadata` — it relies on default empty.
- **The `[search:content]` cascade token** is hardcoded into ChatMemory's system prompt. If 0.3.0 changes the token (to e.g. `[content_search]`), the cascade silently never triggers and search quality degrades for callers who rely on it.

None of these breaks are catastrophic — the operator notices the error in logs and pins the ChatMemory version. The risk is **drift** rather than **failure**: the operator updates one side, forgets the other, and silently loses functionality.

### 2.3 The DB Schema Coupling

ChatMemory owns its Postgres schema. CDK does not read the schema directly — it only calls the HTTP API. **CDK is decoupled from the schema by the FastAPI layer.** This is the right architectural shape. A schema migration in ChatMemory does not require a CDK rebuild as long as the HTTP API stays stable.

The risk is that ChatMemory's schema migration *also* changes the API (because the new schema requires a new field in the request). In that case both must update in step.

### 2.4 The Verdict on ChatMemory Coupling

**Narrowest sister-project coupling in the ecosystem.** Two endpoints, well-defined payloads, FastAPI's automatic schema documentation at `/docs`. The risk is real but bounded. Operators can pin ChatMemory at a known-good version, run the FastAPI service forever, and only update when they decide.

Ember adoption posture: **adopt the architecture, version-pin the dependency.** Hjarta's `MemoryService` interface should target a specific ChatMemory minor version, and Ember's `requirements.txt` for the ChatMemory deployment should freeze.

---

## 3. The AIAvatarKit Coupling — Wide And Sliding

AIAvatarKit is the most architecturally entangled sister. CDK has *four* separate integration paths into it:

| File | What it does | Sister surface |
|---|---|---|
| `AIAvatarKitSpeechSynthesizer.cs:15-131` | Calls AIAvatarKit's TTS endpoint as a backend-proxy | `POST <EndpointUrl>` with `{text, language}` |
| `AIAvatarKitSpeechListener.cs:11-73` | Calls AIAvatarKit's batch STT endpoint | `POST <EndpointUrl>` multipart with `audio` |
| `AIAvatarKitStreamSpeechListener.cs:11-375` | WebSocket streaming STT | `ws://<server>/ws/stt` with custom JSON protocol |
| `Scripts/LLM/AIAvatarKit/AIAvatarKitService.cs` | Alternative dialog LLM service (proxies LLM calls through AIAvatarKit) | streaming via JSLIB or HTTP |

Four touchpoints. Each is a separate contract. Each depends on AIAvatarKit's STS pipeline (`/tmp/aiavatarkit/aiavatar/sts/pipeline.py`) being configured with the matching components.

### 3.1 The Pipeline Surface

`/tmp/aiavatarkit/aiavatar/sts/pipeline.py:33-75` constructs `STSPipeline` with a vad/stt/llm/tts quartet plus extensive config (`vad_volume_db_threshold`, `vad_silence_duration_threshold`, `merge_request_threshold`, ~30 named kwargs). The operator wires up:

- A VAD (Silero by default).
- An STT (`/tmp/aiavatarkit/aiavatar/sts/stt/google.py`, `azure.py`, `openai.py`, `amivoice.py`).
- An LLM (`/tmp/aiavatarkit/aiavatar/sts/llm/`).
- A TTS (`/tmp/aiavatarkit/aiavatar/sts/tts/voicevox.py`, `azure.py`, `google.py`, `openai.py`, `speech_gateway.py`).
- A storage backend (SQLite default, Postgres optional via `db_connection_str`).

The operator's `STSPipeline(...)` call has thirty-plus keyword arguments. The kit's CDK side is *agnostic* to most of these — CDK calls `/tts` and `/stt` and `/dialog` endpoints; the AIAvatarKit server's pipeline shape is internal.

### 3.2 The Contract Surfaces

For each of CDK's four AIAvatarKit integration points:

**TTS at `AIAvatarKitSpeechSynthesizer.cs:55-86`**: Posts `{text, language}` to a URL, expects audio bytes back. The contract is the operator's chosen `EndpointUrl` — AIAvatarKit's FastAPI server exposes a `/tts/synthesize` endpoint (or similar; the exact path depends on the operator's server setup; AIAvatarKit's server scaffolding is in `/tmp/aiavatarkit/aiavatar/sts/`). **The kit does not include the path in the URL; the operator must.**

Operator confusion vector: `EndpointUrl = "http://localhost:8000"` is wrong; it must be `"http://localhost:8000/tts/synthesize"` or whatever the server's path is. The C# code performs no path validation. The error surfaces as HTTP 404.

**Batch STT at `AIAvatarKitSpeechListener.cs:11-73`**: Posts multipart `audio` to the URL, expects `{text, preprocess_metadata, postprocess_metadata, speakers}` JSON.

The `speakers` field requires the AIAvatarKit server to have its `SpeakerGate` configured (`/tmp/aiavatarkit/aiavatar/sts/stt/speaker_gate.py`). If the operator has not configured it, the field is `null` and CDK's `PostProcess` callback (if wired) receives a null. Edge case if the operator forgets the null check.

**Streaming STT at `AIAvatarKitStreamSpeechListener.cs:11-375`**: WebSocket protocol with `start`, `data`, `stop`, `connected`, `partial`, `final`, `voiced`, `error` message types (`AIAvatarKitStreamSpeechListener.cs:286-353`). This is the most fragile of the four — the protocol is **custom JSON over WebSocket**, defined by the CDK code and consumed by the AIAvatarKit server.

The protocol exists in two places:
- CDK's C# `WebSocketMessage` class at `:360-373`.
- AIAvatarKit's Python WebSocket handler (in `/tmp/aiavatarkit/aiavatar/sts/` somewhere — the exact server file varies by operator's setup).

**There is no shared schema file.** No `.proto`, no JSON Schema, no OpenAPI spec. The two implementations must agree by convention. If AIAvatarKit 0.9.0 adds a new message type (e.g. `metadata_update`) or renames `voiced` → `voice_activity_detected`, CDK's `default:` case (`:344-346`) logs "Unknown message type" and the new feature is invisible to the client.

**LLM service at `AIAvatarKitService.cs`** (not exhaustively read here; the file targets the LLM-as-dialog backend). The CDK service is an `LLMServiceBase` subclass that POSTs to the AIAvatarKit server's `/chat` endpoint. The streaming response shape and tool-call format must match what `/tmp/aiavatarkit/aiavatar/sts/pipeline.py:invoke()` emits.

### 3.3 The Breaking-Change Risks — Many

AIAvatarKit had 369 pull requests at HEAD (`96b051f Merge pull request #369`). The project moves fast. Breaking changes are likely to be frequent.

Concrete observable risks:

- **The STSPipeline kwarg surface** (`pipeline.py:33-75`) has changed historically — `db_pool_provider` is recent, `voice_recorder_dir` is recent, `insert_channel_tag` looks recent. Each addition is backward-compatible (kwarg with default); a removal would not be.
- **The WebSocket message protocol** has no version field. Adding a `protocol_version` field at the `start` message is a backward-compatible improvement; renaming an existing field is not.
- **The `merge_request_prefix` / `timestamp_prefix`** defaults look operator-tunable. If AIAvatarKit changes the default phrasing for merge requests, the LLM's behavior at barge-in changes silently.
- **The `db_connection_str` default `"aiavatar.db"`** is SQLite; if AIAvatarKit moves the default to PostgreSQL, existing operator setups with no explicit `db_connection_str` break on the next server start.
- **The Silero VAD dependency at `silero-vad>=6.0.0`** in `setup.py:15`. Silero ships breaking changes occasionally. AIAvatarKit's loose `>=6.0.0` accepts any future Silero major-version; if Silero 7.0 changes the inference call signature, AIAvatarKit's `vad.py` breaks on the next user's `pip install`.

### 3.4 The Verdict on AIAvatarKit Coupling

**Widest and most fragile.** Four touchpoints, custom JSON-over-WebSocket protocol with no schema file, fast-moving 369-PR project with no public compatibility matrix.

Ember adoption posture: **adopt the architecture (two-process STS), reject the protocol borrowing.** Ember should define its own WebSocket protocol with versioned envelope (`{version, type, session_id, payload}`) and implement its own STS pipeline service. Operators who want to use AIAvatarKit's server for prototyping can do so via an adapter; Ember's canonical streaming STT speaks Ember's protocol.

---

## 4. The AITuber Controller Coupling — Narrow But Privileged

`/tmp/chatdollkit-aituber/` is 346 Python LOC across five files. The package wraps the SocketServer protocol (`[[27_SOCKET_PROTOCOL]]`) in a FastAPI server with REST endpoints. The CDK side does not call into chatdollkit-aituber; chatdollkit-aituber calls into CDK via the socket. **The dependency direction is unidirectional**: AITuber Controller depends on CDK's protocol; CDK does not depend on AITuber Controller.

### 4.1 The Contract Surface

The contract is the SocketServer protocol — `ExternalInboundMessage` with five fields, sixteen demo operations (per `[[27_SOCKET_PROTOCOL §4]]`). chatdollkit-aituber's `client.py:43-67` is the canonical client.

If CDK changes the `ExternalInboundMessage` field names (PascalCase → camelCase, say), `client.py:47-54` breaks immediately. **The Python client hardcodes the PascalCase shape** — `"Endpoint"`, `"Operation"`, `"Text"`, `"Priority"`, `"Payloads"`. Newtonsoft's case-insensitive deserialization on the CDK side means CDK could accept either case, but `client.py` is pinned to PascalCase.

If CDK changes the operation set (adds operations, removes operations), chatdollkit-aituber's `api.py:1-173` quietly fails for removed operations and silently does nothing for new ones. The REST surface is hardcoded to the sixteen demo operations.

### 4.2 The Breaking-Change Risks

The AITuber Controller has only six PRs at HEAD (`769e428 Merge pull request #6`). The project is small and stable.

Risks:

- **CDK adds an operation** (e.g. `dialog/inject_persona`). AITuber Controller's API doesn't expose it. Operators can't drive the new feature via REST; they have to use the raw socket client. Workable but inconsistent.
- **CDK removes an operation** (e.g. `llm/debug` because the security-conscious operator pushes back). AITuber Controller still exposes `POST /llm/debug`; calls to it succeed at the HTTP layer, fail at the socket layer (`Error while parsing message` since the operation no longer dispatches), but the FastAPI returns 200 because the socket call was sync-success.
- **CDK changes the priority semantics** (e.g. larger number = higher priority, swap from current). AITuber Controller's `Priority` is a free integer; operator calls produce silently-different behavior.

### 4.3 The Single-Repo PR Pattern

The most recent PR (`#6 buchizo:support-azure-openai-from-aituber-controller`) is an *external contributor* extending the controller, not uezo. This is the only sister project with merged external contributions visible at HEAD (chatmemory had `Update for v0.2.8` from uezo; aiavatarkit had `Merge pull request #369 from uezo/develop` from uezo). The chatdollkit-aituber project is the most externally-contributed — small enough for community PRs, narrow enough for them to land.

### 4.4 The Verdict on AITuber Controller Coupling

**Narrow but propagates CDK's protocol weaknesses.** The Controller inherits the no-auth surface of the SocketServer and the no-version-handshake. Operators who run the Controller publicly inherit the threat model of the underlying protocol *plus* whatever exposures the FastAPI server adds.

Ember adoption posture: **do not adopt directly.** The Controller's pattern (wrap a control protocol in a FastAPI server) is sound, but Ember's control protocol (per `[[27_SOCKET_PROTOCOL]]` Invent) requires bearer tokens. An Ember-equivalent Controller would inherit the bearer requirement and add HTTP-layer auth (bearer or mTLS). Build it new; don't fork the existing.

---

## 5. The OshaberiAI Coupling — Closed-Source Production

`OshaberiAI` is uezo's iOS app shipping CDK + VOICEVOX in production. It is named in the CDK SHARED_CONTEXT (`§11`) but is closed-source. We cannot audit it.

What we know:
- It runs on iOS (App Store).
- It uses VOICEVOX as the TTS.
- It uses ChatdollKit as the embodiment engine.
- It is uezo's "this works in production" credential.

What we don't know:
- Which version of CDK it ships.
- Whether it ships a Strengr-equivalent backend or holds API keys in the build.
- Whether it uses the SocketServer or only the in-process embodiment.

**OshaberiAI's existence is evidence the CDK+VOICEVOX stack works in production iOS. It is not evidence that the production deployment fixed any of the security findings in `[[51_SECURITY_REVIEW]]`.** The most likely deployment shape is "operator-side proxy server" (a Strengr-like backend), but we cannot confirm.

Ember adoption posture: **treat OshaberiAI as a proof-of-life that the architecture ships**, not as a reference deployment. Ember's iOS path will likely look architecturally similar — Unity + CDK + VOICEVOX + Strengr proxy — without OshaberiAI's specific implementation.

---

## 6. The Maintainer Risk

Every sister repo's `setup.py` lists `uezo` as author and `uezo@uezo.net` as maintainer. The license is uniformly Apache-2.0 (good — re-licensing is possible without consent).

**uezo is a single maintainer.** The PR review, release cutting, version bumping, and security response for five repos is one human's responsibility. Maintained well at HEAD; that condition is contingent.

The bus-factor concern:
- ChatdollKit: 1,157 commits, 1.2k stars, 117 forks. A community fork is possible if uezo stops.
- ChatMemory: small, single-file, easy to fork and continue.
- AIAvatarKit: 369 PRs, complex. Community fork would face a learning curve.
- AITuber Controller: small, six PRs. Community fork is trivial but the value comes from CDK compatibility.

**The integration cost** for an operator depending on the kit-of-kits is proportional to *how many repos they depend on*. An operator using only CDK + ChatMemory has two repos to track. An operator using CDK + ChatMemory + AIAvatarKit + AITuber Controller has four, each on its own release cycle, with no compatibility matrix between them.

For Ember, this is a real cost. Ember currently has six True Names plus Bifröst plus Skein plus Skry. Adopting the kit-of-kits posture means Ember-Embodiment-Tier-Unity inherits *another* four-repo coupling. The accumulated maintenance cost is non-trivial.

---

## 7. The Coupling Graph

```
ChatdollKit (Unity / C#)
    │
    ├──→ [HTTP] ChatMemory v0.2.8
    │           └─→ Postgres + pgvector
    │
    ├──→ [HTTP / WS] AIAvatarKit v0.8.17
    │           └─→ STSPipeline { VAD, STT, LLM, TTS }
    │               └─→ Silero VAD (silero-vad>=6.0.0)
    │               └─→ OpenAI / Google / Azure (operator's keys)
    │
    ├──→ [TCP Socket] ← AITuber Controller v0.2.4 (REST wrapper)
    │
    ├──→ [LLM API] ChatGPT / Claude / Gemini / Dify (operator's keys)
    │
    ├──→ [TTS API] Google / Azure / OpenAI / VOICEVOX / Aivis / NijiVoice / etc.
    │
    └──→ [STT API] Google / Azure / OpenAI / AIAvatarKit
```

Eight outbound directions. Four of them go through sister projects, four go direct to commercial providers. The sister projects further fan out to their own dependencies.

The *failure modes* compose. ChatMemory down → search degrades. AIAvatarKit down → streaming STT and the LLM proxy both fail. AITuber Controller down → external control plane unavailable but CDK keeps working. ChatGPT down → fall back to Claude or Gemini if the operator wired them; otherwise dialog fails.

The kit's resilience to sister failure is *graceful where it exists and brittle where it does not*. ChatMemory's silent-on-error pattern (`ChatMemoryIntegrator.cs:50`) is the right shape — the doll keeps talking without memory. AIAvatarKit streaming has no fallback to batch STT; if the WebSocket dies, the listener stops. CDK does not auto-failover to the batch listener.

---

## 8. Cross-References

- `[[27_SOCKET_PROTOCOL]]` — the AITuber Controller's transport.
- `[[38_CHATMEMORY_INTEGRATION]]` — Forge-B's ChatMemory architecture read.
- `[[39_AIAVATARKIT_STREAMING]]` — Forge-B's AIAvatarKit STS architecture read.
- `[[3A_AITUBER_CONTROLLER]]` — Forge-B's AITuber Controller architecture read.
- `[[50_DEPENDENCY_HEALTH]]` — CDK's direct Unity-side dependencies (UniTask, UniVRM, etc.).
- `[[51_SECURITY_REVIEW]]` — the security findings the sisters propagate.
- `[[57_FAILURE_TAXONOMY]]` — the ranked failure rollup.

---

## What This Means for Ember

*Apache-2.0 attribution: when adopting CDK-derived patterns into Ember source, preserve the ChatdollKit and sister-project header references per Apache-2.0 §4(c).*

**Adopt:**

- **The two-process separation pattern.** Memory in its own process. Streaming STS in its own process. Broadcast control in its own process. The architectural shape is right; the embodiment client should be the renderer, not the data plane. Ember's Hjarta-as-FastAPI-Postgres mirrors ChatMemory; Ember's Munnr-streaming-as-WebSocket-service mirrors AIAvatarKit. Apache-2.0 attribution required.
- **The graceful-degradation-by-silence pattern from ChatMemory** (`ChatMemoryIntegrator.cs:50`). When the sister service is unreachable, the doll keeps talking. Memory absence is a degraded state, not a crash. The kit makes the right choice. **But improve the user signal**: a status indicator (Funi UI badge) when a sister is offline. CDK ships no such badge.
- **The narrow-wire surface of ChatMemory** (two endpoints). Resist the temptation to add fifteen RPC methods. A minimal API is a stable API.

**Adapt:**

- **The wide AIAvatarKit coupling (four touchpoints).** Adapt by defining Ember's own protocol on the WebSocket and HTTP surfaces and treating AIAvatarKit as one possible *backend* behind an Ember-defined facade. The facade is a stable Ember contract; AIAvatarKit can be swapped for any STS server speaking the facade.
- **The AITuber Controller pattern** (REST wrapper around a control protocol). Adapt to require bearer auth at both the REST layer and the underlying socket layer. The Controller's value (operator-friendly REST surface for streaming) is real; the no-auth surface is not.

**Avoid:**

- **The implicit shared-maintainer trust chain.** Ember should not assume uezo's release discipline will continue. Pin every sister project to a known-good version in a `data/charts/sister_versions.yaml`; do not auto-track HEAD. New sister versions require explicit operator promotion, not implicit `pip install --upgrade`.
- **The no-version-handshake protocols.** Every Ember-to-sister wire protocol carries a version field. Mismatches produce explicit errors, not silent drift.
- **The four-repo dependency surface** for any tier of Ember's deployment. Ember-Unity-Embodiment-Tier-Default should depend on at most one sister service (a single Strengr backend that fans out to the per-vendor APIs). Operators wanting the AITuber/ChatMemory/AIAvatarKit stack can opt in, but Ember's defaults must work with the single Strengr.
- **The no-compatibility-matrix posture.** Ember publishes a `data/charts/sister_compat.yaml` mapping Ember versions to compatible sister-project version ranges. Operators read this before deploying.

**Invent:**

- A **Sister Service Health Manifest** for Ember's Funi. At boot, Funi reads `data/charts/sister_versions.yaml` and pings each declared sister via a `/health` endpoint. Health includes `{version, schema_hash, last_migration_id}`. Funi refuses to enter the user-facing state if any sister returns a version outside the declared compatibility range. Operators see explicit "Sister AIAvatarKit 0.9.0 is incompatible with Ember 1.2.x; pin to 0.8.x" errors at boot rather than runtime mysteries. CDK has nothing equivalent. Vow tie-in: **Tethered Grounding** (don't pretend to be ready when dependencies are misaligned), **Defended System Prompt** (fail loud at boot).
- A **Single-Strengr Default** for Ember tiers. Strengr is the operator's local backend; it speaks to all upstream sisters (memory, STS, LLM proxies, broadcast control) and presents one stable contract to the embodiment tier. The embodiment client talks to Strengr only. Sister rotations are an operator concern handled inside Strengr, not in Funi or Andlit-unity. CDK's embodiment client knows about ChatMemory, AIAvatarKit, AITuber Controller, and four LLM providers directly; Ember's knows about Strengr. Vow tie-in: **Smallness**, **Pluggable Storage**.
- A **Sister Contract Registry** that defines, in machine-readable form, every wire contract between Ember and a sister. The registry is a versioned set of OpenAPI / AsyncAPI / WebSocket-protocol files. CDK has no `.openapi.yaml` for any sister; the contracts are implicit. Ember's are explicit. New sister versions must publish a new contract; old contracts stay supported through declared deprecation windows. Vow tie-in: **Forge-Ready**, **Defended Memory** generalized to **Defended Sister Contracts**.
- A **Cross-Sister Audit Trail.** Every cross-sister hop (Funi → Strengr → ChatMemory → Postgres; Funi → Strengr → AIAvatarKit → OpenAI) is tagged with a request ID. Each hop logs to Hjarta's audit table with `(request_id, hop_id, parent_hop_id, sister, latency_ms, result)`. Operators debugging "why was the response 8 seconds late" can trace the chain. CDK has no cross-sister tracing; it is a series of black boxes. Vow tie-in: **Audit-Trail-as-Return-Value**, **Tethered Grounding**.
- A **Sister Lifecycle Steward.** A new Mythic Engineering role (or a recurring Auditor task) responsible for monitoring sister-project release cadence, reading their CHANGELOGs, identifying breaking changes, and proposing Ember-side adapter updates. The cost of the kit-of-kits posture is *active stewardship*; CDK assumes the operator does this informally. Ember formalizes the work. Vow tie-in: **Defended Builds**.
- A **Sister Forkability Vow.** For every external sister Ember depends on, Ember maintains a documented fork plan: which repo, which version range, what to do if upstream stops. The plan lives in `docs/peer_codex/_cross_comparison/sister_forkability.md` (or analog). If uezo's bus factor breaks, Ember's operators have a procedural plan to take over a fork. CDK ships none. Vow tie-in: **Tethered Grounding** generalized to **Forkable Grounding**.

A final invent: a **Single-Source Compatibility Truth.** One YAML file (`data/charts/ember_sister_compat.yaml`) is the *only* source of truth for "Ember 1.2.x works with ChatMemory 0.2.x and AIAvatarKit 0.8.x and AITuber Controller 0.2.x." The Funi boot health check reads it. The release pipeline validates it. The docs cite it. The operator deploying Ember reads one file and knows the stack. CDK's compatibility is folkloric; Ember's is single-source.

---

*Apache-2.0 attribution: when adopting CDK-derived patterns into Ember source, preserve the ChatdollKit and sister-project header references per Apache-2.0 §4(c). All sisters are Apache-2.0; re-licensing as part of Ember derivatives is permitted under the §3 grant.*
