---
codex_id: 2A_VOICE_INTERFACE
title: Voice Interface — TTS Bytes, ASR Text, and the Half-Built Duplex
role: Architect
layer: Interface
status: draft
sap_source_refs:
  - py/moss_tts.py:1-267
  - py/sherpa_asr.py:1-93
  - server.py:7900-8260
  - py/moss_model_manager.py:1-124
  - py/sherpa_model_manager.py:1-100
ember_subsystem_targets: [Munnr]
cross_refs:
  - 10_domain/16_VOICE_DOMAIN
  - 10_domain/11_AVATAR_DOMAIN
  - 10_domain/1D_ROUTING_DOMAIN
  - 20_interface/25_AVATAR_PROTOCOL
  - 30_execution/3B_AFFECTION_LOOP
  - 60_synthesis/6B_LOW_POWER_EMBODIMENT
---

# Voice Interface
## TTS Bytes, ASR Text, and the Half-Built Duplex

*— Rúnhild Svartdóttir, Architect*

> *Voice is the bandwidth that goes through the ear. The contract for that bandwidth is not "send the audio" — it is "send the audio in the form, at the latency, and within the budget the listener can carry." SAP signs half of that contract.*

This doc names the voice interface — what bytes cross which wire when, what the ASR/TTS surfaces expose, and where the protocol is incomplete. The [[16_VOICE_DOMAIN]] domain doc covered the substance; this doc covers the contract.

---

## 1. The Subject

**What the interface offers:**
- **TTS:** synthesize speech audio from text + voice + speed parameters; return WAV bytes.
- **ASR:** recognize speech from audio bytes; return text.
- **Routing:** distribute synthesized audio to VRM windows + subtitle overlays via WebSocket fanout.

**Where the wire lives:**

| Surface | Transport | Wire format | Direction |
|---|---|---|---|
| `/v1/audio/speech` (OpenAI-compat TTS) | HTTP POST | `{model, voice, input, speed}` → `audio/wav` bytes | One-shot |
| `/v1/audio/transcriptions` (OpenAI-compat ASR) | HTTP POST multipart | `file` (audio) → `{text}` JSON | One-shot |
| `ws://.../tts` (VRM fanout) | WebSocket | `bytes` (audio) + `str` (control) | Server → client |
| `ws://.../funasr` (duplex hint) | WebSocket | `bytes` (audio in) + recognized text out | Bidirectional (incomplete) |

The two OpenAI-compatible HTTP routes are the *external* contract — anything that speaks the OpenAI Audio API can call SAP for TTS or ASR. The WebSocket fanout is the *internal* contract — the synthesized bytes also reach VRM clients without an explicit HTTP fetch.

---

## 2. How It Works

### 2.1 TTS — input contract

`/v1/audio/speech` (the OpenAI-compatible TTS route, implemented in `server.py` somewhere in 7900-8200) accepts:

- `model: str` — the configured backend (`moss-tts` for local MOSS, or another configured remote)
- `voice: str` — voice name (e.g. `Junhao` per `py/moss_tts.py:240`)
- `input: str` — text to synthesize
- `speed: float` — speed multiplier (1.0 default, 0.1-3.0 range per `py/moss_tts.py:246`)

Returns `audio/wav` bytes.

The MOSS pipeline (`py/moss_tts.py:240-267`):

```python
# /tmp/super-agent-party/py/moss_tts.py:240-267 (excerpts)
async def moss_generate_audio(text, voice="Junhao", speed=1.0, prompt_audio_path=""):
    if not text or not text.strip():
        raise ValueError("文本内容不能为空")
    if speed <= 0 or speed > 3.0:
        raise ValueError(f"语速参数不合法: {speed}, 应在 0.1-3.0 之间")
    try:
        wav_bytes = await asyncio.to_thread(_process_tts_sync, text, voice, speed, prompt_audio_path)
        if not wav_bytes:
            raise RuntimeError("生成的音频为空")
        return wav_bytes
    except asyncio.CancelledError:
        if _moss_runtime and hasattr(_moss_runtime, 'codec_streaming_session'):
            _moss_runtime.codec_streaming_session.reset()
        raise
    except Exception as e:
        logging.error(f"moss_generate_audio failed: {e}")
        raise
```

**Contract enforced:**
- Text must be non-empty.
- Speed must be in (0, 3.0].
- Cancellation resets the codec session state (avoiding pollution across calls).

**Contract leaked:**
- No length cap on input. A 100 KB text input synthesizes a long audio with no warning.
- No format selection — always WAV bytes, never MP3, never Opus, never raw PCM.
- The optional `prompt_audio_path` for voice-cloning is undocumented in the OpenAI-compat surface; only the internal call surface exposes it.

### 2.2 ASR — input contract

`/v1/audio/transcriptions` accepts:

- `file` — multipart upload of audio (any format `soundfile.read` understands — WAV, OGG, FLAC).
- (Other OpenAI-compat fields like `model`, `language` — present in the SAP shape but the implementation forces `model_name="sherpa-onnx-sense-voice-zh-en-ja-ko-yue"` per `py/sherpa_asr.py:82`).

Returns `{text: str}`.

The sherpa pipeline (`py/sherpa_asr.py:82-93`):

```python
# /tmp/super-agent-party/py/sherpa_asr.py:82-93
async def sherpa_recognize(audio_bytes, model_name="sherpa-onnx-sense-voice-zh-en-ja-ko-yue"):
    try:
        recognizer = _get_recognizer(model_name)
        if recognizer is None:
            raise RuntimeError("ASR 模型未就绪（可能未下载或加载失败）")
        text = await asyncio.to_thread(_process_audio_sync, recognizer, audio_bytes)
        return text
    except Exception as e:
        raise RuntimeError(f"Sherpa ASR 处理失败: {e}")
```

**Contract enforced:**
- Model file must exist (returns RuntimeError otherwise).
- Audio format must be readable by `soundfile`.
- Inference is forced to CPU (per `_detect_device` at `py/sherpa_asr.py:14-17`).

**Contract leaked:**
- The model is implicit — caller cannot specify which sherpa model to use (only the default).
- No language hint — sense-voice is multilingual but the caller cannot bias it.
- No confidence score — returned only `text`, never `{text, confidence, language}` even though sherpa exposes more.
- ASR is on CPU regardless of GPU availability.

### 2.3 Routing — `TTSConnectionManager`

The internal wire from TTS to the avatar is `TTSConnectionManager` (`server.py:8167-8246`). Three connection lists:
- `main_connections` — the main chat UI's audio receiver.
- `vrm_connections` — VRM window clients (drive lip-sync).
- `overlay_connections` — subtitle overlay clients.

`broadcast_to_vrm(message)`:
- If `bytes` → send only to VRM (audio).
- If `str` → send to VRM (control) + overlay (subtitles).

This is the *internal* dispatch contract for the voice surface. Detailed crack analysis in [[1D_ROUTING_DOMAIN]] §3.

### 2.4 The half-built duplex

`server.py:8160-8163` has a `FunASR connection closed` log message implying a duplex (real-time) ASR path. The full path would be:

1. Client opens WS to `/ws/funasr` (or similar).
2. Client sends audio bytes as they arrive (e.g. from microphone capture).
3. Server feeds bytes to FunASR (an alternative ASR engine, separate from sherpa-onnx).
4. Server emits partial-recognition events.
5. On "user stopped speaking" detection (VAD), server emits final-recognition.
6. Final recognition fed into `/v1/chat/completions`.
7. Response streams back; TTS streams to VRM; lip-sync runs.

Steps 1-3 are present in code; the rest is partial. The duplex is *intended* but *incomplete*. The voice interface today is *half-duplex* (push-to-talk style).

---

## 3. The Contract — Inputs, Outputs, Side Effects, Invariants

### 3.1 TTS inputs / outputs

- **Inputs:** `{text, voice, speed, [prompt_audio_path]}` via HTTP or via internal call.
- **Outputs:** `audio/wav` bytes (PCM 16-bit, sample rate from model, possibly resampled).
- **Side effects:**
  - Audio quality validation runs and *logs warnings* but does not gate output.
  - Frame validation runs and *logs warnings*.
  - Codec streaming session may be reset on cancellation.
  - The audio is also broadcast through `TTSConnectionManager.broadcast_to_vrm` if the call came via the streaming chat path.
- **Invariants:** non-empty input; speed in valid range; codec session reset on cancel.

### 3.2 ASR inputs / outputs

- **Inputs:** `audio_bytes` (any soundfile-readable format) + optional `model_name`.
- **Outputs:** plain text string.
- **Side effects:** ONNX inference on CPU.
- **Invariants:** model exists; audio is readable; mono conversion happens (`audio[:, 0]` at `py/sherpa_asr.py:73`).

### 3.3 Routing invariants

- TTS bytes go to VRM clients exclusively.
- TTS control strings go to VRM + overlay clients.
- Dead clients are disconnected silently.

### 3.4 The leaks

Three leaks worth naming:

1. **No streaming TTS.** The TTS path returns full WAV after synthesis. Lip-sync waits for the full utterance.
2. **No language detection.** ASR runs the multilingual model with no hint; output language is whatever the model decided.
3. **The duplex is half-built.** FunASR integration is hinted but the VAD + final-recognition + close-the-loop path is partial.

---

## 4. Where It Breaks and Where It Surprises

### 4.1 TTS is one-shot

`moss_generate_audio` returns full WAV bytes. Synthesizing a 30-second utterance means 30 seconds of latency before the mouth opens. For desk-companion use this is acceptable; for live broadcast it is not.

### 4.2 ASR is one-shot

`sherpa_recognize` returns final text after processing the whole input. There is no partial-recognition path in the wrapper (the underlying sherpa SDK *could* stream, but the wrapper does not).

### 4.3 Voice catalog is by string

`voice="Junhao"` is a string. The MOSS model has a fixed set of voices baked in; the OpenAI-compat surface accepts any string and the model handles it (or errors). No catalog endpoint.

### 4.4 The CPU-only choice is hardcoded

`_detect_device() -> 'cpu'` always (`py/sherpa_asr.py:14-17`). A user with a GPU and the GPU sherpa wheel installed cannot opt in without editing the code.

### 4.5 The model-name lookup mismatch

ASR's default is `sherpa-onnx-sense-voice-zh-en-ja-ko-yue`. The OpenAI-compat surface accepts a `model` field but the implementation ignores it (per the wrapper). A caller passing `model="whisper-1"` gets sense-voice anyway. Silent.

### 4.6 The crisp parts

- The **explicit text + speed validation** at `moss_generate_audio` entry.
- The **codec session reset on cancellation** — a real correctness fix.
- The **typed RuntimeError for missing models** at both TTS and ASR entries.
- The **OpenAI-compat surface** — anything speaking the standard can call.
- The **mono-conversion** at ASR — saves a sharp-edged user error.

---

## 5. Cross-References

- [[16_VOICE_DOMAIN]] — the domain this interface serves
- [[11_AVATAR_DOMAIN]] — the avatar that consumes TTS audio
- [[25_AVATAR_PROTOCOL]] — the avatar wire, which TTS bytes share
- [[1D_ROUTING_DOMAIN]] — the WS fanout substrate
- [[30_execution/3B_AFFECTION_LOOP]] (Forge) — the affect → voice mapping that's missing
- [[60_synthesis/6B_LOW_POWER_EMBODIMENT]] (Scribe) — the Pi voice tier
- [[hermes:HEM-16_TUI_GATEWAY_BACKENDS]] — Hermes's voice surface (TUI-side, very different)

---

## What This Means for Ember

**Adopt:**
- The **OpenAI-compatible audio surface** for both TTS and ASR. Interoperable with any client speaking the standard. Vow of Open Knowledge.
- The **explicit input validation** at the boundary (`moss_generate_audio` text + speed check).
- The **codec session reset on cancellation** discipline.
- The **typed `RuntimeError("...未就绪")`** for missing models.
- The **mono conversion** at ASR ingest.

**Adapt:**
- The **one-shot WAV return** — adapt to **chunked streaming**. Munnr's TTS interface returns an async generator yielding ~200ms PCM chunks; the VRM lip-sync starts on the first chunk. SAP synthesizes then ships; Ember ships as it synthesizes.
- The **string voice catalog** — adapt to a **typed voice manifest**: TTS adapters declare `available_voices: List[VoiceDescriptor(name, language, gender, affect_capable)]`. The OpenAI-compat surface validates the request against the manifest.
- The **CPU-forced ASR** — adapt to **tier-driven device selection**: Pi → CPU; laptop → CPU with optional GPU; workstation → GPU. Config is the tier manifest, not a hardcoded function.
- The **model-name field ignored** — adapt to **honor the field with explicit error**: unknown model → 400 Bad Request with a list of supported names.

**Avoid:**
- **TTS that is full-utterance-only.** Streamed TTS is mandatory for embodied presence.
- **A half-built duplex.** Either ship full duplex (VAD + barge-in + chunked turn) or be honest about being push-to-talk.
- **A silent model-substitution.** If the caller asks for whisper-1 and we have sense-voice, fail explicitly.
- **No language detection** when the engine supports it.

**Invent:**
- **The Affect-Conditioned TTS Surface.** TTS calls in Ember include an optional `affect_vector: AffectVector(valence, arousal, intimacy)`. The adapter consumes the vector to choose prosody parameters (pitch, pace, timbre). MOSS-TTS doesn't natively support; the adapter approximates via speed + SSML-ish markup. Coqui XTTS does; the adapter passes through. Munnr's voice is honest about how it feels. See [[16_VOICE_DOMAIN]] Invent.
- **The Voice Continuity Contract.** A user heard Ember speak via MOSS-TTS on the laptop yesterday; tomorrow they hear Ember via a different TTS engine on the workstation. The two should be *recognizable as the same voice*. Implemented via either pinned engine + voice across tiers, or via voice-fingerprint matching across engines. The Embodied Honesty Vow requires it.
- **The Per-Chunk Validation Stream.** The chunked TTS interface validates each chunk (`_validate_audio_quality` at chunk granularity) and *drops or interpolates* bad chunks rather than emitting silence. The avatar's mouth never goes dead mid-utterance. SAP validates the full utterance and ships even when bad; Ember filters at the seam.
- **The Duplex Vow.** Ember commits to full duplex *or* an explicit half-duplex mode. The wire format declares which is active. `/ws/voice/duplex` requires VAD + barge-in support; `/ws/voice/half-duplex` accepts complete utterances only. Capability-honest.
- **The Voice Tier Manifest.** `voice_tier.yaml` per host declares: which TTS engine, which voice, which ASR engine, which device. Pi: text-only or eSpeak; laptop: MOSS-TTS-Nano + sherpa; workstation: XTTS + whisper.cpp + GPU. The Cross-Voice Bridge ([[16_VOICE_DOMAIN]] Invent) reads the tier manifest.
- **The ASR Confidence Field.** Every recognized utterance returns `{text, confidence, language, partials: List[Partial]}`. Strengr uses confidence to decide whether to ask for clarification; SAP cannot — it sees only the final text.
