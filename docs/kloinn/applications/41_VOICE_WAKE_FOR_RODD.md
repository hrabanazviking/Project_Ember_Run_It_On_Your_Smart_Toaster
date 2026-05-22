# 41 — Voice Wake for Rödd

How specifically to build voice support in Rödd, the planned
voice sibling. Concrete Phase 5 plan.

---

## The Rödd sibling

**Rödd** = Old Norse "voice." Already planned (per Yggdrasil)
as the voice surface. Klóinn informs *how* to build it.

Phase 5 ships:
- Talk Mode (push-to-talk) — primary.
- Voice Wake (always-listening) — opt-in.
- Voice-in-text-out — hybrid.

---

## The component stack

```
                                  ┌──────────────────┐
operator voice ───────────────────►│ Microphone        │
                                  │ (sounddevice)    │
                                  └────────┬─────────┘
                                            │
              ┌─────────────────────────────┼────────────────┐
              │                              │                │
              ▼                              ▼                ▼
       ┌──────────┐                 ┌──────────────┐  ┌─────────────┐
       │ Wake-    │                 │ Voice-       │  │ Push-to-talk│
       │ word     │                 │ Activity     │  │ key listener│
       │ detector │                 │ Detector     │  │             │
       │ (opt-in) │                 │ (VAD)         │  │             │
       └────┬─────┘                 └──────┬───────┘  └──────┬──────┘
            │                              │                 │
            └──────────────────────────────┴─────────────────┘
                                            │
                                            ▼
                                  ┌──────────────────┐
                                  │ Whisper STT       │
                                  │ (whisper.cpp /    │
                                  │  faster-whisper)  │
                                  └────────┬─────────┘
                                            │
                                            ▼
                                  ┌──────────────────┐
                                  │ Ember Gateway     │
                                  └────────┬─────────┘
                                            │
                                            ▼
                                  ┌──────────────────┐
                                  │ Piper TTS         │
                                  └────────┬─────────┘
                                            │
                                            ▼
                                  ┌──────────────────┐
                                  │ Speaker          │
                                  └──────────────────┘
```

All Python; all local.

---

## Library choices

### STT: faster-whisper

`faster-whisper` is a fast CT2-based reimplementation of
OpenAI's Whisper. Runs on CPU; quality is excellent.

```python
from faster_whisper import WhisperModel

model = WhisperModel("base.en", compute_type="int8")
segments, _ = model.transcribe(audio_bytes)
text = " ".join(s.text for s in segments)
```

Model sizes: tiny (75MB), base (150MB), small (500MB), medium
(1.5GB), large (3GB). Operator picks per hardware.

### TTS: Piper

`piper-tts` is a Python wrapper for the Piper neural TTS.
Voices are ~30-100MB each; quality is good.

```python
import piper

voice = piper.PiperVoice.load("en_US-amy-medium.onnx")
audio = voice.synthesize("Hello, Volmarr.")
```

Many voices available (English, Spanish, French, German,
Norwegian, ...).

### Wake-word: openWakeWord

`openwakeword` is open-source; runs locally.

```python
from openwakeword import Model

owwModel = Model(wakeword_models=["hey_ember"])

while True:
    audio_chunk = mic.read(1280)  # 80ms
    prediction = owwModel.predict(audio_chunk)
    if prediction["hey_ember"] > 0.5:
        # Wake!
        ...
```

Custom wake words need training; "hey_ember" would be a Phase
5 deliverable (we train + ship it; or operator trains via
provided tooling).

### Microphone: sounddevice

```python
import sounddevice as sd

with sd.InputStream(samplerate=16000, channels=1) as stream:
    while True:
        audio_chunk, _ = stream.read(1280)
        # ... process ...
```

Cross-platform. Sample rate 16kHz matches Whisper expectations.

### Speaker: sounddevice (or play via pygame for cross-platform polish)

```python
sd.play(audio_array, samplerate=22050)
sd.wait()
```

---

## The three modes

### Mode 1: Talk Mode (push-to-talk)

1. Operator presses a key (configurable; e.g., F12).
2. Microphone starts recording.
3. Operator releases key.
4. Recording ends.
5. STT processes; pushes text to Gateway.
6. Gateway generates reply.
7. TTS synthesizes reply.
8. Speaker plays.

Simplest mode. No always-on listening. Operator-controlled.

### Mode 2: Voice Wake (always-listening)

1. Always-on wake-word detector runs.
2. Operator says "hey ember".
3. Wake detected → start recording (with VAD chunking).
4. Operator speaks request.
5. VAD detects end-of-speech (silence > 1.5s).
6. STT → Gateway → TTS → speaker.

More magical UX; requires always-on detector.

### Mode 3: Voice-in-text-out

Operator presses key; speaks; reply appears in Stofa.
No TTS; faster; no audio output.

Useful when operator's hands are busy but eyes are free.

---

## The Stofa integration

When Rödd is active and a chat turn happens:
- Stofa shows "🎤 Listening..." status during STT.
- Stofa shows transcribed text *as it arrives*.
- Stofa shows "💬 Ember is thinking..." during LLM processing.
- Stofa shows "🔊 Playing reply..." during TTS.
- Operator can hit Escape anytime to abort.

This *combines* surfaces: Rödd is input/output; Stofa is
state visibility.

---

## Privacy + indicators

Per Vow of Sovereignty:

- **Mic LED**: where hardware supports, mic LED on during
  recording. (Most laptops do; Pis don't have built-in LED for
  USB mic — operator must trust software.)
- **Stofa indicator**: visible UI element shows mic state.
- **No recording**: audio is processed, not stored.
- **No cloud**: all processing local.

Mute key: F11 hard-mutes mic globally. Operator can disable
voice without quitting Stofa.

---

## Latency budget on Pi 5

| Step | Pi 5 latency |
|---|---|
| Wake detect | < 100ms |
| Voice activity detect end-of-speech | ~200ms after silence start |
| STT (base.en) | ~500ms for 5s utterance |
| Gateway processing + LLM (3B model) | 3-8s |
| TTS (Piper medium voice) | ~300ms for 50-word reply |
| Audio playback start | ~100ms |
| **Total: wake → first audio** | **~4-10 seconds** |

This is *acceptable* for voice. Not snappy but workable.

For LARGE workstations: ~2-5 seconds total. Comfortable.

For TINY (Pi Zero): not recommended; voice support gracefully
degrades to "voice not available."

---

## Pip extras

```bash
pip install ember-agent[voice]         # all-in-one
pip install ember-agent[voice-stt]     # just STT
pip install ember-agent[voice-tts]     # just TTS
pip install ember-agent[voice-wake]    # just wake-word
```

Modular: operators with text-only needs don't install voice
deps.

Dependencies:
- `faster-whisper` (~50MB code + chosen model).
- `piper-tts` (~5MB code + chosen voice).
- `openwakeword` (~5MB code + chosen model).
- `sounddevice` (small).

---

## Voice setup wizard

```bash
ember setup voice

Welcome to Rödd setup.

[1/6] Detected: USB microphone (Plug-in-Mic Pro). Use it? [y/n]: y

[2/6] Speaker: built-in. Test? [y/n]: y
  (plays test tone)
  Heard it? [y/n]: y

[3/6] STT model size:
  ▶ base.en  (150MB; balanced; recommended for Pi)
    small.en (500MB; more accurate; recommended for laptops)
    medium.en (1.5GB; best accuracy; for workstations)
  > base.en

  (downloads model ~30s)

[4/6] TTS voice:
  ▶ en_US-amy-medium (warm, neutral, ~60MB)
    en_US-ryan-medium (deeper voice)
    en_GB-northern_english_male-medium (British)
    (more available)
  > en_US-amy-medium

  (downloads voice ~30s)

[5/6] Voice mode:
  ▶ push_to_talk  (press hotkey to talk)
    wake_word     (always listening for "hey ember")
    voice_in_text_out  (talk; reply in text only)
  > push_to_talk

[6/6] Push-to-talk hotkey: F12 (default)? [y/customize]: y

Configuration saved. Run `ember chat` and press F12 to talk.
```

---

## Wake-word training (optional)

For operators who don't like "hey ember" or want a custom
phrase:

```bash
ember voice train-wake-word

What phrase? > "hey claudius"

We need to record samples. Speak the phrase 20 times, with
slight variation each time.

[1/20] Press space + speak: "hey claudius"
       ✓ recorded
[2/20] ...
```

Background: train a small classifier on the samples. Takes
~5-10 minutes. Quality varies by phrase + operator voice.

This is *advanced*; not Phase 5 ship requirement.

---

## What about voice-only operators

For operators using Ember purely via voice (no screen):

- All Stofa indicators have audio equivalents.
- `/help` voiced via TTS.
- Error states announced.
- "Repeat that" / "Cancel" / "Switch persona" voice commands.

This is *accessibility* work. Important for the cohort that
*needs* voice.

---

## What we explicitly skip

🔴 **Reject for V5**:

### Full-duplex (interruptible) voice

Operator can interrupt Ember mid-TTS by speaking. Hard to do
well; defer to V6+.

### Voice cloning

Custom voices that sound like a specific person. Ethics
concerns; defer indefinitely.

### Cloud TTS as default

Stay local. Cloud TTS as operator opt-in only (and we don't
ship the integration in core).

### Always-on push notifications via voice

Ember speaking unsolicited. Defer; voice is operator-initiated.

---

## Test strategy

Voice is hard to unit-test (audio). We use:

- **Unit tests**: mock audio buffers; verify pipeline shape.
- **Integration tests**: prerecorded audio samples; verify
  STT output.
- **End-to-end smoke**: manual operator testing.

Add `pytest.mark.requires_voice` for integration.

---

## Configuration shape

```yaml
ember:
  rodd:
    enabled: false
    
    mode: push_to_talk
    
    audio:
      input_device: default
      output_device: default
      sample_rate: 16000
    
    stt:
      backend: faster_whisper
      model: base.en
      compute_type: int8
      vad_threshold: 0.5
      silence_duration_s: 1.5
    
    tts:
      backend: piper
      voice: en_US-amy-medium
      speed: 1.0
      pitch: 0
    
    wake:
      backend: openwakeword
      wake_word: "hey_ember"
      sensitivity: 0.5
      mic_led_indicator: true
    
    hotkeys:
      push_to_talk: F12
      mute: F11
      cancel: Escape
    
    privacy:
      record_audio: false
      log_transcript: true
      visual_indicator_required: true
```

---

## Closing

Voice Wake for Rödd is **Phase 5 deliverable** — local-only,
sovereign, modular. Three modes; operator picks. Local Whisper
+ Piper + openWakeWord. Honest about latency.

This is *substantial engineering* (~2000-3000 lines) but
*high operator value*. Phase 5 timeline allows it.

The Klóinn lesson translates: voice is *worth* the
investment, *sovereignly*, *opt-in*.
