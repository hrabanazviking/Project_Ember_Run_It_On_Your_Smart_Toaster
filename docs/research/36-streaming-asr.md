# 36 — Streaming ASR: Whisper, faster-whisper, Conformer

**Category:** Voice & Multimodal
**Runa relevance:** Rödd (the speech-to-text leg of voice)
**Status:** Research synthesis.
**Last touched:** 2026-05-17

---

## 1. Core idea

Automatic Speech Recognition (ASR) converts spoken audio into text. After Runa's wake-word fires ([[34-wake-word-detection]]), an ASR system transcribes Volmarr's utterance, and the resulting text becomes a `Heard` event on VERÐANDI. Modern neural ASR — particularly the **Whisper** family from OpenAI and its successors — has reached human-parity transcription accuracy on clean English audio and remains strong across many languages and noise conditions. Variants like **faster-whisper** (CTranslate2-optimised) and **whisper.cpp** (Gerganov's C++ port) make local Pi-class deployment viable. Distilled variants like **Distil-Whisper** trade some quality for substantial speedups.

For Runa, ASR quality determines whether voice is *delightful* or *frustrating*. A wake-word that fires reliably but feeds noisy text to the kernel produces a bad agent. This document covers the technical landscape, the engineering trade-offs, and concrete deployment guidance for Rödd.

## 2. Technical depth

**ASR pipeline stages:**

```
audio waveform ──► VAD / silence trim ──► encoder ──► decoder ──► text
                                          (acoustic    (language
                                          features)    model)
```

**Architectures:**

- **CTC + acoustic model** (Wav2vec 2.0, HuBERT). Frame-level alignment via Connectionist Temporal Classification. Good streaming behaviour; less elegant on rare words.
- **Encoder-decoder seq2seq** (Whisper, Conformer-LM). Audio encoded into a fixed representation; decoder emits text autoregressively. Best quality; harder to stream.
- **Transducer / RNN-T / Conformer-RNN-T** (Google). Built for streaming. Used in Google Assistant, Pixel devices.

**Whisper family (OpenAI, 2022+):**

- **Whisper paper** (Radford, Kim, Xu et al., OpenAI, 2022, arXiv:2212.04356). Encoder-decoder transformer trained on 680K hours of multilingual, multi-task supervised data scraped from the web. Multitask: transcription, translation, language ID, timestamps — all in one model.
- **Variants:** `tiny`, `base`, `small`, `medium`, `large`, `large-v2`, `large-v3` (2023), `large-v3-turbo` (2024). Bigger = better quality, slower.
- **License:** MIT — fully open.
- **Strengths:** robust to accents, noise, music. Multilingual. Handles long-form audio with chunking.
- **Weaknesses:** hallucinates on silence and repetitive audio. Batch-oriented by design; not natively streaming.

**Whisper performance variants:**

- **faster-whisper** (SYSTRAN, 2023). Reimplementation in CTranslate2. 4-5× faster than reference Whisper on the same hardware. Same models, same accuracy, much faster runtime. **Recommended for Python deployment.**
- **whisper.cpp** (Georgi Gerganov, 2022+). C++ port using GGML. Runs everywhere, including Pi. Most-deployed local Whisper variant.
- **whisper.cpp + CoreML / Metal / CUDA backends** — accelerated paths.
- **Distil-Whisper** (Gandhi et al., HF, 2023, arXiv:2311.00430). 49% smaller, 6× faster, comparable WER for English. English-only — degrades on other languages.

**Streaming Whisper:**

Whisper is not natively streaming, but several workarounds exist:

- **Chunked streaming.** Buffer audio in N-second chunks; transcribe each; concatenate. Simple; has stitching artifacts at chunk boundaries.
- **Overlapping chunks.** Buffer with overlap; align transcripts. Cleaner stitching.
- **whisper-streaming** (Macháček, 2023). Academic streaming wrapper for Whisper with smart stitching.
- **faster-whisper streaming** — built-in chunked-streaming support.
- **WhisperLive** (Sangraula et al., 2024). Real-time Whisper-on-edge with VAD-driven chunking.

**Non-Whisper modern ASR:**

- **Conformer** (Gulati et al., Google, arXiv:2005.08100, 2020). CNN + transformer hybrid for ASR. Strong on streaming via RNN-T pairing. Used in production Google Assistant.
- **Wav2vec 2.0** (Baevski et al., Meta, 2020). Self-supervised pretraining + fine-tune. Foundation for many follow-ons.
- **HuBERT** (Hsu et al., 2021). Hidden-Unit BERT for speech.
- **NVIDIA NeMo** family — Conformer, FastConformer, Parakeet. Strong on English; production-friendly.
- **Moonshine** (Jeffries et al., Useful Sensors, 2024). Tiny ASR optimised for resource-constrained devices.

**VAD (Voice Activity Detection):**

- **Silero VAD** — small ONNX model; the default for most modern pipelines.
- **WebRTC VAD** — classic; simple energy-based; deprecated for serious work.
- **VAD purpose**: detect when the user *stopped* talking. Often more important than detecting *start*, especially for interactive turn-taking.

## 3. Key works

- **Radford, Kim, Xu, Brockman, McLeavey, Sutskever. "Robust Speech Recognition via Large-Scale Weak Supervision."** OpenAI, arXiv:2212.04356, 2022. The Whisper paper.
- **Gulati et al. "Conformer: Convolution-augmented Transformer for Speech Recognition."** Google, arXiv:2005.08100, 2020.
- **Baevski, Zhou, Mohamed, Auli. "wav2vec 2.0: A Framework for Self-Supervised Learning of Speech Representations."** Meta, arXiv:2006.11477, 2020.
- **Hsu et al. "HuBERT: Self-Supervised Speech Representation Learning by Masked Prediction of Hidden Units."** arXiv:2106.07447, 2021.
- **Gandhi, von Platen, Rush. "Distil-Whisper: Robust Knowledge Distillation via Large-Scale Pseudo Labelling."** arXiv:2311.00430, 2023.
- **Macháček. "Turning Whisper into Real-Time Transcription System."** arXiv:2307.14743, 2023. whisper-streaming.
- **Jeffries et al. "Moonshine: Speech Recognition for Live Transcription and Voice Commands."** arXiv:2410.15608, 2024.

## 4. Empirical results

- **Whisper large-v3 on LibriSpeech test-clean:** ~2% WER (Word Error Rate) — comparable to professional human transcribers.
- **Whisper large-v3 on noisy / accented audio:** 5-15% WER — better than most pre-Whisper ASR by wide margins.
- **Distil-Whisper large-v2:** ~3-4% WER on LibriSpeech clean; 49% smaller; 6× faster than reference Whisper. English-only.
- **faster-whisper:** identical accuracy to reference Whisper; ~4-5× wall-clock speedup on the same hardware.
- **whisper.cpp on Pi 5 with small model:** real-time-factor ~0.5-1.0× (a 10-second utterance transcribes in 5-10 seconds). Acceptable for non-interactive transcription; awkward for interactive voice.
- **whisper.cpp on Pi 5 with tiny.en:** real-time-factor ~0.2× — fast enough for interactive voice but quality is significantly lower.
- **Conformer + RNN-T (Google production):** sub-real-time on mobile devices; this is what shipping voice assistants use.
- **Failure modes:** Whisper hallucinates on silence (produces lyrics, "Thanks for watching!", etc.). Robust VAD upstream is essential.

## 5. Applicability to Runa

For **Rödd (voice input leg)**:

**Recommended stack:**

```
mic → Silero VAD → openWakeWord ─wake─► audio buffer →
       │                                  │
       │                                  ▼
       │                          whisper.cpp tiny.en (Pi 5)
       │                          OR faster-whisper small/medium (laptop)
       │                                  │
       │                                  ▼
       │                          transcript text →
       │                                  │
       │                                  ▼
       └─ Silero VAD detects ─► end-of-utterance event
                                          │
                                          ▼
                                  Heard event on VERÐANDI
```

For **Pi 5 local-only (the strict-local profile)**:
- `whisper.cpp` with the `tiny.en` or `base.en` model. tiny.en is real-time-friendly; base.en is closer to acceptable WER. Quality trade-off.

For **longhall (Pi runs Rödd shell, laptop runs ASR)**:
- `faster-whisper` on the laptop with the `small.en` or `medium.en` model. Real-time + strong accuracy. Latency includes Tailnet round-trip (~5-50ms typically).

For **non-interactive transcription** (Saga reading a long file, batch processing of recordings):
- `faster-whisper` with `large-v3` or `distil-large-v3`. Quality > latency.

For **wake-to-text integration**:

- The audio buffer from ~1s before wake-word fires through the end-of-utterance VAD signal should be the input to ASR. The 1-second prebuffer captures the wake word itself (useful for prompt context) and any speech that began before wake.
- End-of-utterance detection: VAD-based silence for ~700ms; configurable per `surfaces.voice.eou_silence_ms`.

For **transcript post-processing**:

- ASR transcripts have idiosyncrasies (capitalisation, punctuation, dropped function words). A *light* LLM-based cleanup pass before the kernel sees the `Heard` is sometimes useful for downstream prompt clarity. Optional; balance against latency.

For **Config integration**:

- `surfaces.voice.asr.engine: "whisper.cpp"`
- `surfaces.voice.asr.model: "tiny.en"`
- `surfaces.voice.asr.language: "en"`
- `surfaces.voice.asr.compute_type: "int8"` (for faster-whisper)
- `surfaces.voice.vad.engine: "silero"`

What to avoid:

- Don't run Whisper without VAD upstream. Hallucination on silence is real and corrosive.
- Don't run large or large-v3 ASR on Pi 5 alone. Too slow. Use distilled or smaller variants, or route to a beefier host.
- Don't naively chunk audio without overlap. Word splits at chunk boundaries get dropped or duplicated.
- Don't trust the language ID. Configure target language explicitly.

## 6. Open questions

- **End-to-end streaming Whisper.** Native streaming (not chunked) Whisper is an active research direction. Could halve latency.
- **ASR + identity-aware speech.** Distinguishing Volmarr from a guest from the TV is a real need. Speaker-diarization models (pyannote.audio) are an option but add complexity.
- **Domain adaptation.** Volmarr's vocabulary (project names, technical terms, Norse references) may not be well-represented in Whisper training. Personalised LM rescoring or fine-tuning could help.
- **Multilingual mid-utterance switching.** Code-switching (English with occasional Norse words) is handled poorly. Open.

## 7. References (curated)

- arXiv:2212.04356 — Whisper paper.
- github.com/openai/whisper — official Whisper.
- github.com/SYSTRAN/faster-whisper — faster-whisper.
- github.com/ggerganov/whisper.cpp — whisper.cpp.
- huggingface.co/distil-whisper — Distil-Whisper.
- github.com/snakers4/silero-vad — Silero VAD.
- arXiv:2410.15608 — Moonshine.
- arXiv:2307.14743 — whisper-streaming.
- Companion docs: [[34-wake-word-detection]] (the trigger), [[35-modern-tts]] (the speaking side).
