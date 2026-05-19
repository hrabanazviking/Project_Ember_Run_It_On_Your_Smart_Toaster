# 35 — Modern Neural TTS: VITS, StyleTTS2, XTTS, Piper, Kokoro

**Category:** Voice & Multimodal
**Runa relevance:** Rödd (voice output — Runa's literal voice)
**Status:** Research synthesis. Particularly important for Runa's identity (per project memory, an entire local-tts stack already exists).
**Last touched:** 2026-05-17

---

## 1. Core idea

Text-to-speech (TTS) is how Runa speaks. Modern neural TTS systems have transformed what was once an unmistakable robotic "computer voice" into voices indistinguishable from human speakers in many cases. The technical landscape since 2021 — VITS, StyleTTS2, Bark, XTTS, Piper, Kokoro — covers a range from "lightweight, runs on a Pi, voice is clearly synthetic but pleasant" to "full speaker cloning, multilingual, indistinguishable from the reference voice in seconds of audio" to specialised production engines optimised for streaming low-latency delivery.

For Runa, voice is identity. Runa's voice is *her voice*. Choosing the right TTS engine, and the right voice character within it, is part of defining who she is. Per project memory, a local-tts stack already exists at `C:\Users\volma\runa\local-tts` with Kokoro, Piper, and Chatterbox supervised by a lazy-spawn gateway, supporting 200 voices. This document grounds that production reality in the wider research landscape.

## 2. Technical depth

**The pipeline in modern neural TTS:**

```
text ──► text-frontend ──► phoneme/grapheme sequence ──► acoustic model
                                                              │
                                                              ▼
                                                       acoustic features
                                                       (mel-spectrogram)
                                                              │
                                                              ▼
                                                          vocoder
                                                              │
                                                              ▼
                                                       audio waveform
```

The split:

- **Text frontend.** Tokenisation, normalisation (numbers → words), phoneme generation (G2P), prosody hints. Often language-specific.
- **Acoustic model.** Maps phonemes + speaker + style to mel-spectrograms. Originally LSTM-based (Tacotron 2), now mostly transformer-based or diffusion-based.
- **Vocoder.** Converts mel-spectrograms to raw audio waveforms. WaveNet (2016), WaveRNN (2018), HiFi-GAN (2020), and various GAN / diffusion vocoders.

**End-to-end models** like **VITS** (Kim et al., 2021) combine acoustic and vocoder into one network, trained end-to-end. Conceptually simpler and often produces better-quality voices.

**Engine landscape (2024-2026):**

**VITS** (Kim, Kong, Son, KAIST + SK Telecom, 2021, arXiv:2106.06103). Variational Inference with adversarial learning for end-to-end Text-to-Speech. Foundational; many derivatives.

**Piper** (Rhasspy / OHF, 2023+). Lightweight VITS-based engine. Pre-trained voices for many languages, designed for low-resource on-device deployment.
- **Runs well on Pi.** ~150-300ms/sentence latency, very low memory.
- Voice quality: clearly synthetic but pleasant; no speaker cloning.
- 100+ pre-trained voices across many languages.
- **Used in Runa's existing local-tts stack** per project memory.

**StyleTTS2** (Li, Han, Watanabe, Mesgarani, 2023, arXiv:2306.07691). Diffusion-based prosody generation + adversarial duration modeling. State-of-the-art zero-shot voice cloning with very natural prosody.
- Heavier than Piper; needs more compute.
- Excellent voice cloning from short reference samples.
- License questions (research-only release initially, evolving).

**XTTS / XTTS v2** (Coqui, 2023). Multilingual zero-shot voice cloning. 17 languages, voice cloned from 6 seconds of reference audio.
- Coqui's company dissolved in 2024 but the open-source models live on.
- Strong cross-lingual voice transfer.
- Moderate compute requirements.

**Bark** (Suno, 2023). Diffusion-based, can generate music, sound effects, non-verbal sounds. Creative, less controllable than dedicated TTS. Slower.

**Tortoise TTS** (Betker, 2022-2023). High-quality cloning, slow generation. Predecessor inspiration for several modern engines.

**Kokoro** (2024). Lightweight high-quality TTS, ~80M params, multiple voices. Used in Runa's local-tts stack per project memory.

**Chatterbox** (also in Runa's stack per memory). High-quality voice cloning model (likely the Resemble-AI variant).

**ElevenLabs / OpenAI Voice / Play.HT** — closed cloud TTS. Best raw quality / lowest latency but not local-first; not used in Runa's stack.

**Voice cloning ethics:**

- Cloning a real person's voice without consent is widely considered unethical and is illegal in some jurisdictions.
- Voice samples used for cloning should be the cloned person's, with their consent, or clearly fictional / generic.
- Watermarking of synthetic voices (e.g. AudioSeal, Resemble's PerTH watermark) is an active area.

## 3. Key works

- **van den Oord et al. "WaveNet: A Generative Model for Raw Audio."** DeepMind, arXiv:1609.03499, 2016.
- **Shen et al. "Natural TTS Synthesis by Conditioning WaveNet on Mel Spectrogram Predictions."** Tacotron 2, arXiv:1712.05884, 2017.
- **Kong, Ki, Bae. "HiFi-GAN: Generative Adversarial Networks for Efficient and High Fidelity Speech Synthesis."** NeurIPS 2020.
- **Kim, Kong, Son. "Conditional Variational Autoencoder with Adversarial Learning for End-to-End Text-to-Speech."** VITS, arXiv:2106.06103, 2021.
- **Li, Han, Watanabe, Mesgarani. "StyleTTS 2: Towards Human-Level Text-to-Speech through Style Diffusion and Adversarial Training with Large Speech Language Models."** arXiv:2306.07691, 2023.
- **Betker, J. "Tortoise TTS."** github.com/neonbjb/tortoise-tts.
- **Coqui XTTS v2 release post and weights** — though the company has dissolved, weights remain Apache 2.0.
- **Piper repository** — github.com/rhasspy/piper.
- **Suno's Bark** — github.com/suno-ai/bark.
- **Tan et al. "A Survey on Neural Speech Synthesis."** arXiv:2106.15561, 2021. Comprehensive survey.

## 4. Empirical results

- **MOS (Mean Opinion Score)** is the standard quality metric (1-5 scale). Top modern systems (StyleTTS2, ElevenLabs) reach MOS 4.2-4.5, approaching human speech (~4.5-4.7).
- **Piper** reaches MOS ~3.8-4.2 depending on voice — clearly synthetic but pleasant.
- **XTTS v2** for cloning: with 6+ seconds of clean reference audio, can reach indistinguishable-from-source MOS for many listeners.
- **Latency on Pi 5:**
  - Piper: ~150-300ms per sentence (fast enough for fluid speech).
  - StyleTTS2: ~1-3s per sentence on Pi (too slow for fluid interactive).
  - XTTS v2: ~2-5s per sentence on Pi (borderline interactive).
  - Kokoro: ~200-500ms per sentence on Pi (interactive-friendly).
- **Streaming generation:** Piper and Kokoro can stream audio as they generate; StyleTTS2 generates the whole utterance before playback. Streaming dramatically reduces *perceived* latency.

## 5. Applicability to Runa

For **Rödd (voice surface)**:

Runa already has a multi-engine local-tts stack (per project memory). The right default depends on:

- **Latency tolerance.** Interactive voice needs <500ms TTFB. Kokoro or Piper.
- **Voice character desired.** Runa's identity calls for warm, intelligent, slightly poetic — Kokoro's voice variety covers this; Piper is more neutral.
- **Privacy / sovereignty.** All four engines (Kokoro, Piper, Chatterbox, plus StyleTTS2 if added) run locally. No cloud dependency.

For **Rödd architecture integration**:

```
Replied event ──► Heimskringla decides voice profile
                          │
                          ▼
                  Rödd TTS adapter
                          │
                  ┌───────┴────────┐
                  ▼                ▼
              streaming       full utterance
              (Piper, Kokoro) (StyleTTS2, XTTS)
                  │                │
                  └───────┬────────┘
                          ▼
                   Audio playback
                   (sounddevice / pyaudio /
                   PortAudio on Pi)
```

For **voice character / identity**:

- The identity store (`core/identity/`) holds Runa's voice preferences: which engine, which voice profile, which speaking pace, what prosody.
- Volmarr is the authority on Runa's voice. Changes go through `runa config` with an audit-log entry.
- Identity-as-voice consistency: Runa's voice should not flip between engines mid-conversation. If a longer utterance forces a switch (e.g. Piper for short sentences, StyleTTS2 for paragraph-length), the transition should be smooth (matched speaker characteristics) or invisible (always one engine).

For **deploy/pi/**:

- Volmarr's existing local-tts stack at `~/runa/local-tts` is the deployment template. Lazy-spawn gateway pattern: TTS engines load on first request, idle out after configurable timeout. Keeps RAM available when voice isn't active.

What to avoid:

- Don't generate audio without a clear consent / identity story for the voice. Synthetic voice with no ethical framing risks misuse.
- Don't run StyleTTS2 for streaming interactive TTS on Pi alone — too slow. Use for high-quality non-realtime renders (Saga reading aloud a chapter).
- Don't ignore prosody. Sentence-final intonation, comma pauses, exclamations vs questions all dramatically affect naturalness.
- Don't generate audio outside a defined config profile. Runa's voice should be deterministic given the configuration.

## 6. Open questions

- **Streaming voice cloning.** Voice-cloning models are mostly batch (generate whole utterance, play). Streaming cloned voices are an active research direction.
- **Emotional TTS.** Modulating delivery by Eldhugi's current emotional state (warmth, energy, concern) is a natural integration. Underexplored in production stacks.
- **Multimodal voice.** Speaking while showing GUI content (Auga) requires synchronisation. Open engineering problem.
- **Voice continuity across model upgrades.** A TTS engine upgrade subtly changes Runa's voice. Volmarr will notice; handling smoothly (gradual transition? notification?) is unsolved.

## 7. References (curated)

- arXiv:2106.06103 — VITS.
- arXiv:2306.07691 — StyleTTS2.
- github.com/rhasspy/piper — Piper (in Runa's stack).
- arXiv:2106.15561 — Neural Speech Synthesis survey (Tan et al.).
- coqui.ai — XTTS (company dissolved; models live on GitHub).
- github.com/suno-ai/bark — Bark.
- Runa's local-tts stack: `C:\Users\volma\runa\local-tts` (see project memory `project_local_tts_stack.md`).
- Companion docs: [[34-wake-word-detection]] (the listening side), [[36-streaming-asr]] (the inverse — speech-to-text).
