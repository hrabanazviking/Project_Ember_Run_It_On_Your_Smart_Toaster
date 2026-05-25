---
codex_id: 16_VOICE_DOMAIN
title: Voice Domain — TTS, ASR, and the Two Lazy Runtimes
role: Architect
layer: Domain
status: draft
sap_source_refs:
  - py/moss_tts.py:1-267
  - py/moss_model_manager.py:1-124
  - py/sherpa_asr.py:1-93
  - py/sherpa_model_manager.py:1-100
  - server.py:7900-8250
ember_subsystem_targets: [Munnr]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/11_AVATAR_DOMAIN
  - 20_interface/2A_VOICE_INTERFACE
  - 30_execution/3B_AFFECTION_LOOP
  - 60_synthesis/6B_LOW_POWER_EMBODIMENT
---

# Voice Domain
## TTS, ASR, and the Two Lazy Runtimes

*— Rúnhild Svartdóttir, Architect*

> *The voice is the second body. A voice that lags, hisses, or clips speaks louder than the words it carries. SAP knows this. The voice domain is one of the few places where SAP is paranoid in the right direction.*

The voice domain houses two heavyweight runtimes: MOSS-TTS for synthesis and Sherpa-ONNX (sense-voice) for recognition. Both load lazily, both validate their output, both gate themselves on file presence. This is the *quietly disciplined* part of SAP — a model for how Ember should handle every model-bearing capability.

---

## 1. The Subject Itself

**What the domain owns:** text-to-audio synthesis (TTS), audio-to-text recognition (ASR), the lifecycle of the underlying ONNX runtimes, audio-quality validation.

**What the domain does *not* own:**
- Routing of audio to surfaces (that's `TTSConnectionManager` in `server.py`)
- Lip-sync (that's `vts_manager.vts_worker` — see [[11_AVATAR_DOMAIN]])
- VAD/turn detection (the duplex story is incomplete; see §3.5)
- Translation (not a goal; both engines are multilingual but neither bridges languages)

**Where it lives:**

| File | LOC | Owns |
|---|---|---|
| `py/moss_tts.py` | 267 | MOSS-TTS-Nano-100M-ONNX inference, audio-quality validation, WAV bytes output |
| `py/moss_model_manager.py` | 124 | TTS model download / discovery / version pinning |
| `py/sherpa_asr.py` | 93 | sherpa-onnx sense-voice inference, model lazy-load |
| `py/sherpa_model_manager.py` | 249 | ASR model download / hash-check / availability |
| `py/moss/` (sub-tree) | (vendored) | MOSS-TTS runtime helpers (`tts_runtime`, `tts_robust_normalizer_single_script`, `ort_cpu_runtime`) |

Roughly 700 LOC of model orchestration plus vendored runtime helpers. The two models are decoupled — replacing TTS doesn't touch ASR.

---

## 2. How It Works

### 2.1 Lazy loading with double-checked locking

`py/moss_tts.py:11-13` declares module-level singletons:

```python
_moss_runtime = None
_runtime_lock = threading.Lock()
```

`_get_moss_runtime()` (line 17) is the only entry point. It checks `_moss_runtime is not None` *before* acquiring the lock (line 20), then *after* (line 24). The pattern is:

```python
# /tmp/super-agent-party/py/moss_tts.py:17-26
def _get_moss_runtime():
    global _moss_runtime
    if _moss_runtime is not None:
        return _moss_runtime
    with _runtime_lock:
        if _moss_runtime is not None:
            return _moss_runtime
        ...
```

This is **double-checked locking** done correctly. The first check is a fast-path; the lock is only entered if the runtime might need loading; the second check protects against the race where two threads both pass the first check before either has loaded.

The heavy imports (`numpy`, `scipy.signal`, `TTSRuntime`, `onnxruntime`, `sentencepiece`, `soundfile`) are inside the lock (line 29-33). If any fails, `print(f"MOSS TTS 依赖缺失...")` and `return None`. Graceful Offline at the import level.

Model files are checked at line 38: `if not (model_dir / "MOSS-TTS-Nano-100M-ONNX").exists(): print("提示: MOSS TTS 模型未找到，请先通过 SDK 接口下载。"); return None`. So the runtime *can be absent*, and the downstream code (`moss_generate_audio`, line 240) raises a typed `RuntimeError("MOSS TTS 模型未就绪")` rather than crashing.

### 2.2 Per-inference quality validation

`_validate_audio_quality` (`py/moss_tts.py:58-98`) is the kind of code Hermes Codex would call "Vow of Cache Discipline applied at the output boundary." It checks:

- `waveform is None` → fail.
- `waveform.size == 0` → fail.
- `np.any(np.isnan)` or `np.any(np.isinf)` → fail.
- Mean energy `< min_energy=0.0001` → fail (audio too quiet).
- Peak `> max_peak=1.0` → fail (clipping).
- Near-zero ratio `> 0.5` → fail (silence padding too dominant).

Each failure is a specific named reason. The function returns `(bool, str)` — pass/fail + reason. This is not paranoia; it is integrity.

`_validate_generated_frames` (line 101-124) similarly validates the model's audio-token output frame-by-frame: every token must be in `[0, audio_codebook_size)`, no empty frames. The codebook size is read from `runtime.tts_meta["model_config"]["audio_codebook_sizes"][0]` (line 181) — a metadata read, not a hardcoded value.

### 2.3 The synthesis path

`_process_tts_sync(text, voice, speed, prompt_audio_path)` (`py/moss_tts.py:127-237`) is the synchronous inference. Async callers wrap it via `asyncio.to_thread` (line 250 in `moss_generate_audio`). The flow:

1. Reset codec streaming session state (line 138-140) — prevents state pollution across calls.
2. Generate via `runtime.synthesize(...)` (line 154-161).
3. **Normalize peak to 0.95** if `max_val > 1.0` (lines 167-171) — explicit anti-clipping margin.
4. Validate audio quality (line 174); log warnings but don't fail (the comment at 177 explicitly hands the decision to the caller).
5. Validate frame quality (line 180-187).
6. Apply speed via `scipy.signal.resample` if `abs(speed - 1.0) >= 0.01` (lines 190-205) — only resample when meaningfully different.
7. Convert to 16-bit PCM, write to in-memory WAV (lines 207-222), return `bytes`.

A temp WAV file (line 150) is written by the runtime and immediately deleted in `finally:` (line 233-237) — the runtime's API requires a path, but SAP achieves an in-memory illusion by writing and instantly cleaning up. Pragmatic.

### 2.4 The recognition path

`py/sherpa_asr.py` is half the size and half the discipline. `_get_recognizer(model_name)` (line 20) is the lazy loader; `_detect_device()` (line 14) explicitly *forces CPU* with a comment "强制使用 CPU，避免 GPU 版本未安装的警告" (forcing CPU to avoid the GPU-not-installed warning).

The recognizer construction (line 49-56) calls `sherpa_onnx.OfflineRecognizer.from_sense_voice(model=str(model_path), tokens=str(tokens_path), num_threads=4, provider=device, use_itn=True, debug=False)`. `use_itn=True` enables inverse text normalization (numbers/dates rendered as digits in output). Sensible default.

`_process_audio_sync(recognizer, audio_bytes)` (line 65-79) is simple: `soundfile.read` → mono → `create_stream` → `accept_waveform` → `decode_stream` → return `stream.result.text`. Eleven lines, one purpose. The async wrapper `sherpa_recognize` (line 82) is six lines, throws `RuntimeError("ASR 模型未就绪")` if the model is absent.

The whole file is 93 LOC. The whole capability is honest.

### 2.5 The route surface

`server.py:7900-8250` (approximately — the boundary fades) registers `/v1/audio/transcriptions` and `/v1/audio/speech` (OpenAI-compatible audio endpoints). It also defines `TTSConnectionManager` (lines 8167-8249), the routing fabric for TTS output (covered in [[11_AVATAR_DOMAIN]] §2.4).

Notable: the OpenAI-compatible audio endpoints can serve `omniVoice` (the configurable voice name from `settings.json`) or `moss_tts` directly. The two backends are exposed under the same API surface.

---

## 3. Where It Breaks and Where It Surprises

### 3.1 Force-CPU is honest but limiting

`py/sherpa_asr.py:14-17` forces CPU even on machines with GPUs because the GPU build of sherpa-onnx is a separate wheel. This is correct for safety but leaves performance on the table on the user's RTX-2060-bearing laptop. There is no opt-in for "I know what I'm doing; use GPU."

### 3.2 Speed adjustment via resampling, not pitch-preserving

`scipy.signal.resample` (`py/moss_tts.py:194-199`) changes both speed *and* pitch. A user setting speed=1.5 will get audio that is 1.5x faster *and* about 5 semitones higher. This is a known TTS user-experience footgun; pitch-preserving algorithms (PSOLA, WSOLA) exist but are not used. The comment at line 200-203 mentions the trade-off implicitly by adjusting `sample_rate` rather than the data.

### 3.3 Quality validation doesn't gate

`_validate_audio_quality` (`py/moss_tts.py:174-178`) logs warnings but does *not* refuse to return the audio. The comment is explicit: "不直接抛出异常，让客户端自己决定是否接受" (don't throw; let the client decide). The client is the caller, which is the streaming response handler, which is server.py, which... does not decide. The validation is collected but not acted on.

### 3.4 No streaming TTS

`moss_generate_audio` returns *bytes* — a full WAV after the model completes. A long response means a long wait. There is no chunked output. The mouth on the VRM avatar cannot start moving until the entire utterance has synthesized. Compare to commercial TTS APIs that stream in 200ms chunks.

### 3.5 The duplex story is half-built

ASR exists. TTS exists. Voice activity detection (VAD) — needed to know *when the user stopped speaking* — is not in this domain. There is a FunASR integration hint at `server.py:8160-8163` (`FunASR connection closed`), suggesting a duplex pipeline being prototyped, but the path from "user spoke" → "user stopped" → "ASR run" → "LLM responds" → "TTS streams back" → "VRM lip-syncs" is not fully closed in the code I have surveyed. The pieces exist; the integration is partial.

### 3.6 The crisp parts

- The **double-checked lazy load** of `py/moss_tts.py:17-26` is correct, rare, and worth lifting verbatim.
- The **per-inference quality validation** is the right kind of paranoia, even if its result is not acted on.
- The **peak normalization to 0.95** is a small but real anti-clipping discipline.
- The **typed `RuntimeError("...未就绪")`** when models are absent is exactly the Graceful Offline contract.
- The **`use_itn=True` default** in sense-voice is a sensible UX choice that many ASR integrations miss.

---

## 4. Cross-References

- [[10_DOMAIN_MAP]] §1 row 5
- [[11_AVATAR_DOMAIN]] §2.4 for the audio fanout to VRM
- [[20_interface/2A_VOICE_INTERFACE]] for the full protocol
- [[30_execution/3B_AFFECTION_LOOP]] (Forge) — affect → voice intonation is a gap
- [[60_synthesis/6B_LOW_POWER_EMBODIMENT]] for the Pi-tier voice strategy
- [[hermes:HEM-16_TUI_GATEWAY_BACKENDS]] — Hermes has voice surface in TUI gateway; very different shape

---

## What This Means for Ember

**Adopt:**
- **Double-checked lazy-load** (`py/moss_tts.py:17-26`) verbatim for every Ember capability bearing a heavyweight model — TTS, ASR, embeddings, VLM, anything that costs >100ms to import.
- **Per-inference output validation** with named-reason fails (`_validate_audio_quality`). Apply to every Brunnr query, every Smiðja tool output, every Munnr surface emission. The validation may not gate, but it must record.
- **Typed RuntimeError for absent models** — `RuntimeError("ASR 模型未就绪")` style. Ember refuses cryptic `AttributeError`s; the failure mode is *named*.
- **Peak normalization at boundaries** — a 0.95 anti-clipping margin (or its analog for whatever output type) at every Munnr surface.
- The **forced-CPU honest default** for any GPU-optional dependency, with opt-in elevation via tier manifest (see [[60_synthesis/63_PERFORMANCE_TIER_ENGINE]]).

**Adapt:**
- The **bytes-only TTS return** of `moss_generate_audio` — adapt to **streamed-chunks-with-validation**. Ember's TTS returns an async generator yielding ~200ms chunks; per-chunk validation feeds the avatar lip-sync without latency.
- The **speed-via-resample** of `_process_tts_sync:190-205` — adapt to pitch-preserving (use a library like `pyrubberband` or roll a WSOLA implementation). The pitch-shift footgun is too sharp.
- The **quality validation logs but doesn't gate** — adapt to *configurable gate severity*: in `tier_manifest` set per-tier rules (Pi: warn-only; workstation: refuse-and-resynthesize).

**Avoid:**
- **No streaming TTS as the default.** Ember's avatar must start lipsyncing as soon as the first audio chunk is ready, not after the whole utterance synthesizes.
- **A force-CPU default with no opt-in** for users who explicitly have GPUs.
- **A duplex pipeline that's half-built.** Either ship full duplex (VAD + barge-in + chunked turn) or don't claim duplex.

**Invent:**
- **Affect-Coupled Intonation.** SAP's TTS is *expressionless* — the same waveform regardless of Hjarta state. Ember invents: the TTS request includes an `affect_vector` (valence, arousal, intimacy), and the synthesis uses it to choose pitch/pace/timbre parameters. On models that don't support affect-conditioned TTS, Ember substitutes prosody via SSML-like markup. On models that do (e.g. Coqui XTTS with style transfer), Ember passes the vector. Either way, Ember's voice is *honest about how it feels*.
- **Voice-Identity Continuity.** A user who has spoken with Pi-Ember (text-only with a placeholder voice) and then with laptop-Ember (full MOSS-TTS) hears a *recognizably continuous voice*. This requires either a single TTS pinned across tiers, or a voice-fingerprint match across TTS engines. The Embodied Honesty Vow requires it.
- **The Quiet Voice Tier.** A Pi-Ember might have no TTS — the True Name Munnr still owns voice, but the surface is *typed prosody markup* logged for debugging. The mouth is absent; the *meant intonation* still lives. This becomes the [[60_synthesis/6B_LOW_POWER_EMBODIMENT]] voice surface.
- **The Validation Ledger.** Every voice synthesis records its `_validate_audio_quality` result to the Sögumiðla bus. Over weeks, a histogram emerges — what fraction of utterances clipped, what fraction were too quiet, what fraction had silence-padding. This becomes the basis for automated re-tuning of the TTS-prompt or model choice. SAP collects this implicitly (in print statements) and uses it not at all.
- **The Cross-Voice Bridge.** Munnr exposes a `speak(text, surface=..., voice=..., affect=...)` API where `surface` can be `terminal`, `vrm`, `slack`, `phone`, `livestream-overlay`. The same utterance can travel to multiple surfaces with surface-appropriate transformations (TTS for vrm; text-with-emoji for slack; raw text for terminal). SAP routes audio bytes to one surface at a time; Ember treats voice as a polyform.
