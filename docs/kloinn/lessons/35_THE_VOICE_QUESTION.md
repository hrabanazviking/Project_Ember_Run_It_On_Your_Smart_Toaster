# 35 — The Voice Question

OpenClaw ships voice. Ember doesn't (yet). The deeper question:
how does voice change the operator-AI relationship?

---

## The technical question (easy)

Per [`../patterns/14_VOICE_WAKE_AND_TALK_MODE.md`](../patterns/14_VOICE_WAKE_AND_TALK_MODE.md):

Voice components are now mature + local:
- STT: Whisper.cpp, faster-whisper, VOSK.
- TTS: Piper, Coqui, Mimic3.
- Wake-word: openWakeWord, Porcupine.

All run locally. All work offline. All fit in modest hardware.

We *can* ship voice. The question is *when* and *how*.

---

## The deeper question (hard)

Voice changes the *relationship*:

### 1. Voice is more intimate

Talking to an AI feels different from typing. Voice activates
language areas of the brain more strongly. Operators report
voice interactions feeling more *present*, more like talking
to a person.

This can be:
- **Good**: deeper engagement; companion feels real.
- **Bad**: confusion about what's-real; emotional dependency
  risk.

### 2. Voice is faster for short exchanges

"Hey Ember, what's the time?" — voice wins.
"Hey Ember, summarize this 50-page document" — typing wins (you
can paste the document).

Voice is *interaction-shape-dependent*.

### 3. Voice is exclusionary in shared spaces

Talking to AI in a co-working space / library / public transit
is awkward. Voice limits *where* an operator can interact.

Typing is universal.

### 4. Voice surfaces accessibility

Operators with vision or mobility impairments may prefer voice.
For some, it's *essential* not optional.

This is a *case for shipping voice*, not against.

### 5. Voice changes timing expectations

In voice, silence is *meaningful*. A 5-second pause feels
weird. With typing, a 5-second pause is normal.

Voice puts pressure on response latency. Pi-class with 3B
model may be too slow for natural voice interaction.

---

## Ember's voice strategy

🟢 **Adapt to Ember Vows in Phase 5+**.

### Principles

1. **Voice is opt-in.** Default off. Operator enables.
2. **Voice is local-only.** No cloud STT/TTS. Sovereignty.
3. **Voice augments, doesn't replace.** Text remains primary
   surface. Voice is an *additional* surface.
4. **Voice respects context.** Operator can mute / pause
   anytime. No "always listening" without explicit consent.
5. **Voice acknowledges limits.** Latency, language support,
   accent variation are honest constraints.

### Components (Phase 5 build)

- **Rödd** (sibling) — voice surface implementation.
- **Local Whisper** — STT.
- **Local Piper** — TTS.
- **OpenWakeWord** — wake-word detector.
- **Voice activity detection** — for talk-mode chunking.

All local. All open-source. All sovereign.

---

## The wake-word question

A wake-word implies **always-listening**. Mic always on. Audio
buffer always running.

For some operators: this is *creepy*.

For others: it's *necessary* (driving, cooking, exercise).

Ember's solution: wake-word is *opt-in within voice*. Default
voice mode is push-to-talk (no always-on). Operators can
enable wake-word in config.

If wake-word is on:
- Audio processed locally (no cloud).
- Audio NOT recorded (only wake-word detector runs).
- Mic LED on (where hardware supports) so operator sees the
  state.
- Operator can toggle anytime.

This is *sovereignty-aligned voice*. We don't betray privacy
for convenience.

---

## The emotional-dependency question

Voice + a *warm* register can create emotional bonds with the
AI. Some operators find this comforting; some find it concerning.

OpenClaw doesn't seem to address this explicitly. Their lobster
mascot keeps things light; voice is a tool, not a relationship.

Ember's stance (informed by the emotional-intelligence
framework per Yggdrasil):

- Voice register **matches the moment** but **never claims
  feeling**.
- "I notice you sound tired" is OK. "I feel for you" is NOT
  ok. The first is observation; the second is false claim.
- The Vow of Honest Memory applies: don't fake what you don't
  have.
- Operators with attachment concerns can configure neutral-only
  register (no WARM, no REASSURING, no SOLEMN moods).

---

## What about TTS naturalness

Modern local TTS (Piper, Coqui) is **good but not great**. Not
ElevenLabs-quality. Voices are intelligible but recognizably
synthetic.

Two paths:

### Path A: accept current local TTS

Pros: sovereign, simple, free.
Cons: voice sounds "AI-ish."

### Path B: hybrid (operator opt-in cloud TTS)

Operator can configure ElevenLabs or similar for higher
quality. Cloud TTS handles only voice synthesis (text → audio);
no other data leaves device.

Pros: high quality.
Cons: cloud dependency for voice; potentially $$$.

For Ember: ship Path A as default; document Path B as opt-in
for operators who want it.

This is *informed opt-in*: the operator chooses; we don't
hide the trade-off.

---

## Voice-only contexts

Some operators want voice as *primary* surface. E.g.:
- Operator with chronic vision impairment.
- Operator running Ember on a kitchen Pi as ambient companion.
- Operator driving long distances.

For these contexts, voice must work *reliably*. Latency,
clarity, error-recovery all matter.

Phase 5 voice should be *first-class* — not a thrown-in
afterthought. Time to build well.

---

## What about voice-input + visual-output?

A hybrid: voice in, Stofa text out. Operator speaks; Ember
replies in text on screen.

Use case: operator is hands-busy but eyes-free. Cooking + reading
recipe. Working out + watching screen for next instruction.

This is *cheaper* than full voice (no TTS needed) and works
for many use cases.

We should support this hybrid in Phase 5.

---

## Voice + multilingual

OpenClaw's voice (presumably) supports multiple languages via
ElevenLabs / Whisper.

Ember's default: English. Other languages possible via Whisper
language flag + Piper voices in that language.

This is *not free* — each language needs:
- Whisper model size for that language.
- Piper voice model in that language.
- LLM understanding of that language.

For V5: ship English; document path to other languages; let
community contribute.

---

## Cross-cultural voice

Different cultures have different voice norms:
- Some prefer brief, direct.
- Some prefer formal, ornate.
- Some prefer warm, relational.

Ember's emotional-intelligence framework handles register (per
Yggdrasil). Adding voice doesn't change this — operator's
register preferences inform TTS prosody (where Piper supports
it).

---

## The reality of voice quality

Even with good components:

- **Background noise** affects STT.
- **Accents** affect STT (Whisper varies by accent).
- **Soft voices** can be missed by wake-word.
- **TTS pronunciation** of unusual names (proper nouns) is shaky.

This is *honest engineering*: voice works but has *real
constraints*. Operators should know.

Configuration includes:
- Mic gain / noise gate.
- Wake-word sensitivity.
- TTS speed / pitch.
- Whisper model size (larger = more accurate but slower).

---

## Configuration shape (full)

```yaml
ember:
  rodd:
    enabled: false
    
    mode: push_to_talk     # or "wake_word" / "voice_in_text_out"
    
    wake:
      backend: openwakeword
      wake_phrase: "hey ember"
      sensitivity: 0.5
      mic_led_indicator: true
    
    stt:
      backend: whisper_cpp
      model: base.en        # or "small.en" / "medium.en"
      language: en
      vad_enabled: true
    
    tts:
      backend: piper
      voice: en_US-amy-medium
      speed: 1.0
      
      # Operator opt-in cloud TTS
      cloud:
        enabled: false       # opt-in
        provider: elevenlabs
        api_key_ref: kista://elevenlabs/api_key
    
    register:
      respect_emotional_intelligence: true
      neutral_only: false    # operator can force
    
    privacy:
      record_audio: false    # NEVER record
      log_transcript: true   # operator can disable
      mute_hotkey: F12
```

---

## What about voice in Stofa

Stofa is a TUI. Voice doesn't render visually. But Stofa can:
- Show "🎤 Listening..." when voice active.
- Show transcribed text as it arrives.
- Show TTS playback indicator.
- Voice controls in command palette.

Stofa + Rödd is a powerful combo. Each surface plays to its
strength.

---

## Closing

The Voice Question is **both technical and relational**. The
tech is solvable; the relationship implications matter more.

Ember's voice strategy:
- 🟢 Phase 5 ships voice (Rödd).
- 🟢 Local-only by default.
- 🟢 Operator opt-in cloud TTS for quality lovers.
- 🟢 Honest about quality + limits.
- 🟢 Mute / pause anytime.
- 🟢 Don't fake emotions.
- 🔴 Reject always-on by default.

OpenClaw's voice is mature; Ember's will arrive later but
*sovereign-by-design*.

The Klóinn lesson: voice is *worth the investment* — once
done right. Plan now; build in V5.
