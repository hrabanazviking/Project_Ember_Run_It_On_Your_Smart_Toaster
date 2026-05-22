# 14 — Voice Wake and Talk Mode

OpenClaw's voice patterns. What they enable. How they integrate.
What it means for Ember's planned Rödd surface.

---

## The two modes

### Voice Wake

Always-listening wake-word detection. Operator says "Hey Molty"
(or whatever wake word configured); the system activates; listens
for the actual request; responds.

Available on macOS/iOS.

### Talk Mode

Push-to-talk. Operator presses a button (menu bar, keyboard
shortcut, mobile button); speaks; releases; system processes.

Available across more platforms.

### Continuous Voice (Android)

On Android: continuous listening + transcription, with chunked
processing. Variant of voice wake for the mobile context.

---

## What's required

For *voice wake*:
- Wake-word detection model (small, always-on).
- Microphone access permission.
- Background process (the always-listening loop).
- Low-latency hand-off to STT (speech-to-text).
- Speech-to-text engine.
- Agent processing.
- Text-to-speech engine.
- Audio output.

For *talk mode*:
- Same minus wake-word detection.
- UI element to start/stop recording.

For *continuous voice*:
- Higher-quality STT (since wake-word filter is absent).
- Voice-activity detection (chunking by silence).
- Streaming STT (don't wait for full utterance).

---

## OpenClaw's choices

- **TTS backend**: ElevenLabs (premium quality), with system TTS
  fallback.
- **STT backend**: not explicitly stated; likely OpenAI Whisper
  or similar.
- **Wake-word**: not explicitly stated; possibly Porcupine,
  openWakeWord, or custom.
- **Platform**: voice-wake limited to macOS/iOS where always-on
  microphone access works.

---

## Why voice matters

Voice is a *fundamentally different interaction mode* than
text:

- **Hands-free**: driving, cooking, walking, exercising.
- **Ambient**: "while doing other things."
- **Inclusive**: accessible to operators who don't type well.
- **Faster for some tasks**: short questions / commands.
- **Slower for others**: long-form requests / context.

Voice is *additive*. Few operators want voice-only; many want
voice-as-an-option alongside text.

---

## Ember's current state

**Zero voice support**. Munnr is text-only. Stofa (planned) is
text-only. Auga (planned, V5) might add voice.

The Rödd sibling (planned, see Yggdrasil) is the voice surface.
Currently *unimplemented*; design only.

---

## What Ember can adopt

🟢 **Adapt to Ember Vows** in Phase 5+.

When Rödd is implemented:

### 1. Talk Mode (easier; ship first)

- Operator presses a key in Stofa (or button in Auga).
- Microphone records until key released.
- Audio → STT (local Whisper or VOSK).
- STT text → standard chat-turn pipeline.
- Response → TTS (system TTS or local Coqui).
- Audio playback.

This is *additive*; Stofa keeps working as text. Talk Mode is a
hotkey away.

### 2. Voice Wake (harder; ship later)

- Always-on wake-word detector (Porcupine via PicoVoice, or
  openWakeWord).
- Wake word: "Hey Ember" or operator-customizable.
- On wake: same flow as Talk Mode.

Voice Wake requires *daemon mode* (per
[`10_LOCAL_FIRST_GATEWAY.md`](10_LOCAL_FIRST_GATEWAY.md)) because
the wake-detector must run continuously.

### 3. Local-first voice components

🔵 **Borrow as-is** but with sovereign substitutions:

- **STT**: local Whisper (whisper.cpp or faster-whisper) — runs
  on CPU; quality is excellent.
- **TTS**: local Coqui TTS or Piper — runs on CPU; quality is
  good.
- **Wake-word**: openWakeWord (open-source) — runs on CPU.

Ember **does not** ship ElevenLabs (cloud TTS). Sovereign-only.

Operators *could* configure a cloud TTS as opt-in, but we don't
make it the default.

---

## Cross-platform considerations

### Linux

Microphone access via PulseAudio/PipeWire. Sounddevice, PyAudio
libraries. Standard.

### macOS

Microphone permission per app (system dialog). Once granted,
sounddevice works.

### Windows

Microphone permission via Windows settings. PyAudio works.

### iOS/Android (Phase 5+)

Mobile companion apps. Native microphone access. Streaming to
Ember daemon via WebSocket (per
[`17_COMPANION_APP_PAIRING.md`](17_COMPANION_APP_PAIRING.md)).

### Pi (headless)

Microphone via USB sound card or HAT. Speaker via 3.5mm jack
or USB.

Voice on Pi works; latency depends on model size. Tiny Whisper
+ Piper TTS = 2-3 seconds round-trip on Pi 5.

---

## Latency budget

For *good* voice interaction:

| Step | Target latency |
|---|---|
| Wake-word detect to STT start | < 100ms |
| STT (post-utterance) | < 500ms |
| Agent processing | < 2s (depends on LLM) |
| TTS first audio frame | < 500ms |
| Audio playback start | < 200ms |
| **Total: wake to audio response** | **< 3s** |

Pi 5 with 3B LLM: ~5-8s total (LLM is bottleneck).
Laptop with 8B LLM: ~3-5s.
Workstation with 70B LLM (offloaded via federation): ~2-4s.

Voice is *latency-sensitive*; we set realistic expectations.

---

## Configuration shape

```yaml
ember:
  rodd:
    enabled: false                 # opt-in
    
    mode: talk                     # or "wake" (requires daemon)
    
    wake:
      backend: openwakeword
      wake_word: "hey ember"
      sensitivity: 0.5
    
    stt:
      backend: whisper_cpp
      model: small.en              # or "base.en" for less RAM
      language: en
    
    tts:
      backend: piper
      voice: en_US-amy-medium
      speed: 1.0
    
    audio:
      input_device: default
      output_device: default
      sample_rate: 16000
    
    behavior:
      auto_send_after_silence_ms: 1500
      max_recording_seconds: 60
      tts_interrupt_on_key: true
```

---

## What Voice means for Stofa

Stofa is a TUI — it doesn't *render* voice. But it can:

- Show a "🎤 Listening" indicator when voice wake fires.
- Show transcribed text as it arrives.
- Show TTS playback indicator.
- Toggle voice via hotkey (e.g., `Ctrl+T` for talk mode).

So Stofa + Rödd combine: the TUI shows the conversation; voice
is the input/output mode.

---

## Privacy considerations

🟢 **Critical for Ember's Vow of Sovereignty.**

### What stays local

- STT processing (local Whisper).
- TTS processing (local Piper).
- Wake-word detection (local model).
- All audio (never sent off-device).

### What never happens

- No "send audio to cloud for STT" (Ember-default).
- No "cloud TTS providers" (operator opt-in only).
- No "voice training to improve the model" (Ember-default).

Voice on Ember is *operator-owned audio that never leaves the
device*. This is a *significant* sovereignty win over OpenClaw's
ElevenLabs default.

---

## What this gives operators

After Phase 5 ships voice:

- **Hands-free Ember**: ask questions while cooking, driving,
  exercising.
- **Accessibility**: operators with mobility/typing
  difficulties.
- **Ambient companion**: Ember running on a kitchen Pi with a
  USB mic; operator interacts as they pass by.
- **Multimodal sessions**: voice in, text out (or vice versa);
  operator picks per moment.

The *companion-AI experience* deepens when voice is an option.

---

## What we should NOT do (yet)

🔴 **Reject for Phase 5**:

### 1. Real-time voice conversation

Continuous-back-and-forth voice (no push-to-talk; full duplex).
This is *very hard* — voice activity detection, interruption
handling, latency budgets. Skip for V5; consider V6+.

### 2. Voice cloning / custom voices

Use stock TTS voices. Custom voice cloning has ethics
implications + much bigger model footprint.

### 3. Multilingual auto-detection

Stay English-first for V5. Operator-configurable other
languages can come V6.

---

## Closing

Voice Wake and Talk Mode are **OpenClaw's expansion of where the
operator can be**. Hands-free, ambient, accessible.

Ember can adopt this in Phase 5+ (Rödd) using fully-local
components — keeping voice as *yet another sovereign capability*,
not a cloud-dependent feature.

The lesson from OpenClaw: voice is *not optional* for operators
who want a companion AI present in their daily life. Even if
text is primary, voice is *near-essential* for the highest tier
of companion experience.

Plan it; build it well; ship it sovereign.
