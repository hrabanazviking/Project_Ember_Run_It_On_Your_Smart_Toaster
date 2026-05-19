# 34 — Wake-Word Detection: Porcupine, openWakeWord

**Category:** Voice & Multimodal
**Runa relevance:** Rödd (voice surface entry-point)
**Status:** Research synthesis.
**Last touched:** 2026-05-17

---

## 1. Core idea

For Runa to listen via voice without recording everything continuously to the cloud (or even continuously to local disk), she needs **wake-word detection**: a small, always-on, on-device classifier that listens to the microphone stream and only opens the larger pipeline (full speech recognition, the kernel) when it recognises a specific trigger phrase like "Runa" or "Hey Runa." Wake-word detection is what makes voice assistants *ambient* rather than *transactional* — and what makes them *privacy-respecting* rather than *surveillance*.

The technology has matured enormously since the early days (Siri's "Hey Siri" launched 2014). Modern open-source options like **openWakeWord** make custom wake words practical without proprietary services. Commercial offerings like **Picovoice Porcupine** are reliable but commercial. For Runa's voice surface, picking the right wake-word system is a *necessary* engineering decision.

## 2. Technical depth

**Wake-word detection requirements:**

- **Always-on.** The system listens continuously; cannot drain battery / CPU.
- **On-device.** No audio leaves the machine until a wake word fires.
- **Low false-accept rate** (FAR). Too many false wakes is annoying and privacy-violating.
- **Low false-reject rate** (FRR). Failing to wake when the user does say the word is frustrating.
- **Low latency.** Should fire within ~200ms of the wake word completing.
- **Robust to noise.** TV in the background, music, multiple speakers.
- **Speaker-invariant** (usually). Should wake for any voice saying the phrase, not just a trained user (some systems offer speaker-dependent mode for privacy).

**Architectural pattern:**

```
microphone ──► VAD ──► acoustic features ──► keyword model ──► wake event
              (voice                          (small NN)
              activity
              detector)
```

Voice Activity Detection (VAD) reduces compute by skipping silence. Acoustic features (typically log-mel spectrograms over short windows) feed a small neural network (depthwise-separable CNNs, gated RNNs, or small transformers) trained to recognise the wake word. The model outputs a per-frame probability; a smoother (often a sliding-window peak detector) fires when the probability exceeds a threshold for long enough.

**Practical considerations:**

- **Wake-word length:** 2-4 syllables is the sweet spot. Too short = false-positives; too long = annoying. "Runa" (2 syllables) is borderline-short.
- **Distinguishability:** the phrase shouldn't sound like common English words. "Runa" is uncommon → easier to distinguish.
- **Background-noise training:** the classifier needs negative examples that include speech-without-wake-word, music, TV audio, sirens, etc.
- **Speaker variation:** training data should include diverse speakers, accents, gender, pitch.
- **Far-field robustness:** wake-word from across the room is harder than wake-word from arm's reach. Microphone array + beamforming helps.

**Major options:**

**Picovoice Porcupine.**
- Proprietary, but free for personal / non-commercial / Raspberry Pi use.
- Pre-built models for popular wake words (no custom training cost).
- Custom-word generation requires paid console (Picovoice Console).
- Excellent on-device, very low resource use.
- Supported on Pi, Linux, macOS, Windows, Android, iOS, Cortex-M MCUs.
- License: Apache for the SDK; the wake-word models themselves are under separate license.

**openWakeWord** (David Scripka, 2023+).
- Fully open-source (Apache 2.0).
- Pre-trained models for popular wake words ("alexa", "hey jarvis", others contributed by community).
- Custom training pipeline: synthetic-speech data generation (Piper TTS) + augmentation + train a small model. Practical without a dataset of recorded examples.
- Tensorflow / ONNX based; runs on Pi reliably.
- Quality: comparable to Porcupine on popular words; custom-word quality depends on training pipeline care.

**Snowboy** — historic; abandoned / forked. Original by KITT.AI, deprecated. Community forks exist.

**Mycroft Precise** — historic, project largely defunct.

**Whisper as wake-word** — overkill. Whisper is full ASR; running it always-on burns CPU. Possible but not the right tool.

**Wake-word as small Whisper distillation** — emerging area. Distilling small ASR variants into "wake-word + short-phrase" classifiers. Underdeveloped.

**Performance on Pi 5:**

- openWakeWord: ~5-10% of one core continuous, ~50-150ms latency.
- Porcupine: ~2-5% of one core, ~50-100ms latency. Slightly more efficient.

Both are practical on Pi 5 alongside everything else.

## 3. Key works

- **Picovoice Porcupine.** picovoice.ai/platform/porcupine/.
- **openWakeWord.** github.com/dscripka/openWakeWord.
- **Piper TTS** (for synthetic training data — see [[35-modern-tts]]).
- **Sainath, T., Parada, C.** "Convolutional Neural Networks for Small-footprint Keyword Spotting." Interspeech 2015. The foundational small-NN keyword-spotting paper.
- **He et al.** "Streaming Small-footprint Keyword Spotting Using Sequence-to-Sequence Models." ICASSP 2017.
- **Berg, A.; O'Connor, M.; Cruz, M.** "Keyword Transformer: A Self-Attention Model for Keyword Spotting." Interspeech 2021.
- **Google's Personal & Lighter Speech Detection papers** — relevant for on-device speaker-aware variants.

## 4. Empirical results

- Porcupine published numbers: ~0.5 false accepts per 24 hours of audio at recommended thresholds. Comparable to commercial assistants.
- openWakeWord (Scripka, README benchmarks): ~0.5-1 false accept per 8 hours of varied audio for the published "hey jarvis" model.
- Custom-trained openWakeWord (synthetic data, no real recordings): can reach Porcupine-comparable performance for moderately distinctive wake words; less reliable for very short or common words.
- Both systems' false-accept rates degrade significantly in noisy environments. Microphone choice matters as much as wake-word model choice.
- Latency: both systems fire within 100-200 ms of word completion on Pi 5.

## 5. Applicability to Runa

For **Rödd (voice surface)**:

- **Recommended wake word:** "Runa" — short, distinctive, infrequent in English speech. "Hey Runa" is the safer two-word fallback if "Runa" alone produces too many false accepts.
- **Recommended system:** openWakeWord with custom training. Reasons:
  - Open-source aligns with the project's open-knowledge philosophy.
  - Avoids commercial licensing complications.
  - Custom training is the only path to "Runa" specifically (no provider ships pre-trained "Runa" models).
- **Fallback for fast bootstrap:** Porcupine with a paid Console-generated "Runa" model. Use for early development if openWakeWord custom training is too slow to iterate on. Switch to openWakeWord before public release.
- **Mic recommendation:** any USB conference mic (Snowball, AT2020USB+, ReSpeaker 4-Mic Array). Pi's built-in audio is for output only.

For **Rödd architecture**:

```
mic → VAD → openWakeWord ─wake─► full ASR ([[36-streaming-asr]])
                            │
                            └─continuous─ discarded
```

The wake-word fires; the audio buffer (last ~2s + ongoing) feeds full ASR; ASR transcript becomes a `Heard` event on VERÐANDI.

For **Privacy posture**:

- Audio never leaves the Pi before wake-word fires. Document this clearly in `docs/security/`.
- Wake-word system runs in its own process (Rödd service), separate from the kernel. Crash isolation per the actor / supervision pattern ([[21-actor-model-supervision]]).
- Microphone-on indicator (hardware or software) is the operator-visible signal that the wake-word system is active.

For **Config**:

- Wake word, sensitivity threshold, mic device, VAD aggressiveness all in `config/runa.example.yaml#surfaces.voice`.

What to avoid:

- Don't run Whisper as the always-on listener. Too heavy, too power-hungry.
- Don't ship a wake word that triggers on common words ("Hey", "Computer"). False accepts compound.
- Don't disable VAD. The CPU savings are real and the wake-word model gets cleaner input.
- Don't train custom wake-word models on tiny datasets without strong negative examples. False-positive rate balloons.

## 6. Open questions

- **Custom-trained wake words for Runa specifically.** No published baseline; will require iteration.
- **Speaker-dependent modes.** Wake only for Volmarr's voice → privacy win, technical complexity. Some support in openWakeWord roadmap.
- **Multimodal wake (button + word).** Hybrid: press a button OR say a word. Removes always-on listening for those who prefer; supported in many UI shells.
- **Multilingual wake.** Volmarr is English-speaking, but if Runa eventually serves multilingual users, multilingual wake-word handling is an open question.

## 7. References (curated)

- picovoice.ai/platform/porcupine/ — Porcupine docs.
- github.com/dscripka/openWakeWord — openWakeWord.
- github.com/rhasspy/piper — Piper TTS (used for synthetic training data generation).
- arXiv:1503.08395 — Sainath & Parada keyword-spotting paper.
- github.com/rhasspy/rhasspy3 — the broader Rhasspy voice-assistant project (good engineering reference).
- Companion docs: [[35-modern-tts]] (the speaking side), [[36-streaming-asr]] (the post-wake transcription).
