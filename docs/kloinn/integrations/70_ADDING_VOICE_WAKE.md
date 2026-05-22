# 70 — Adding Voice Wake

Concrete implementation guidance for adding Voice Wake to
Ember. Phase 5 work.

---

## Prerequisites

Before Voice Wake:
- Daemon mode landed (Phase 4).
- Rödd sibling project exists (currently planned).
- `ember-agent[voice]` pip extras available.

---

## Step 1: dependency add

```bash
pip install ember-agent[voice-wake]
# Brings in: openwakeword, sounddevice
```

Add to `pyproject.toml`:
```toml
[project.optional-dependencies]
voice-wake = [
    "openwakeword>=0.6",
    "sounddevice>=0.4",
]
```

---

## Step 2: implement wake detector

Create `src/ember/rodd/wake_word.py`:

```python
import asyncio
from openwakeword.model import Model
import sounddevice as sd
import numpy as np

class WakeWordDetector:
    def __init__(self, wake_model: str, sensitivity: float):
        self.model = Model(wakeword_models=[wake_model])
        self.sensitivity = sensitivity
        self.running = False
        self.audio_q = asyncio.Queue()
    
    async def listen(self) -> AsyncGenerator[WakeEvent]:
        """Yield wake events as detected."""
        self.running = True
        
        # Sounddevice runs in thread; queue chunks
        def callback(indata, frames, time, status):
            asyncio.run_coroutine_threadsafe(
                self.audio_q.put(indata.copy()),
                asyncio.get_event_loop()
            )
        
        with sd.InputStream(
            samplerate=16000,
            channels=1,
            callback=callback,
            blocksize=1280,
        ):
            while self.running:
                chunk = await self.audio_q.get()
                prediction = self.model.predict(
                    chunk.flatten() * 32768
                )
                for word, score in prediction.items():
                    if score > self.sensitivity:
                        yield WakeEvent(word=word, score=score)
    
    async def stop(self):
        self.running = False
```

---

## Step 3: integrate into Humarr Gateway

In `src/ember/spark/humarr/__init__.py`:

```python
class HumarrGateway:
    async def start_voice_wake(self):
        if not self.config.voice.wake.enabled:
            return
        
        detector = WakeWordDetector(
            wake_model=self.config.voice.wake.wake_phrase,
            sensitivity=self.config.voice.wake.sensitivity,
        )
        
        async for event in detector.listen():
            await self._handle_wake(event)
    
    async def _handle_wake(self, event: WakeEvent):
        """Wake fired; start STT session."""
        await self.publish_event("voice.wake", event.dict())
        await self.start_voice_session()
```

---

## Step 4: wake → STT bridge

After wake fires:
- Stop wake detection (avoid double-trigger).
- Start full STT recording.
- VAD detects end of utterance.
- Transcribe; push to chat as input.
- Resume wake detection.

---

## Step 5: privacy + indicators

```python
def trigger_mic_led(state: bool):
    """OS-specific mic LED control where available."""
    if sys.platform == "darwin":
        # macOS: use mic indicator API
        pass
    elif sys.platform == "linux":
        # Linux: may need uledmon or similar
        pass
    # Windows: no standard
```

Always show visual indicator in Stofa regardless of hardware
LED.

---

## Step 6: tests

```python
# tests/integration/test_rodd_wake.py

async def test_wake_word_fires_on_phrase():
    detector = WakeWordDetector("hey_ember", 0.5)
    
    # Inject prerecorded audio of someone saying "hey ember"
    detector._inject_audio(load_test_audio("hey_ember.wav"))
    
    events = []
    async for event in detector.listen():
        events.append(event)
        break
    
    assert events[0].word == "hey_ember"
    assert events[0].score > 0.5

async def test_wake_word_does_not_fire_on_silence():
    # Inject silent audio
    # Assert no events
    ...
```

---

## Step 7: configuration + setup

Add to setup wizard:

```
[N/M] Voice Wake — always-listening?

  Voice Wake lets you say "Hey Ember" to start a chat.
  
  Requires:
    - Microphone access (browser/OS permission).
    - Always-on daemon mode (--install-daemon).
    - ~10MB wake-word model.
  
  Enable Voice Wake? [y/n]: y
  
  Wake phrase: ▶ hey_ember (default) / custom
  > hey_ember
  
  Sensitivity (0.0-1.0; default 0.5):
  > 0.5
```

---

## Step 8: documentation

Add to `docs/voice/`:
- `wake-word.md` — operator guide.
- `troubleshooting.md` — common issues.
- `privacy.md` — what's stored, what's not.

---

## Step 9: rollout

V5 release notes:

```
V5 ships Voice Wake (opt-in).

To enable:
  pip install ember-agent[voice-wake]
  ember setup voice
  ember daemon start --voice
  
Say "Hey Ember" to begin a chat.
```

---

## Hardware considerations

### Linux

- USB microphones work well.
- ALSA/PulseAudio handle the audio stack.
- Some Pi cases obstruct microphones; external mic recommended.

### macOS

- Built-in mic excellent.
- macOS asks for mic permission per app.
- Bundle app for proper permission flow.

### Windows

- Permission flow simpler than macOS.
- Quality varies by laptop.

### Pi

- Need USB mic (3.5mm jack input doesn't work well).
- Recommend: Samson Q2U or similar USB mic.

---

## Closing

Adding Voice Wake is **Phase 5 work**. Integrates openWakeWord
+ sounddevice into Humarr Gateway. Operator opt-in. Sovereign.

Implementation ~500 lines including tests. Documentation ~5
pages. Total scope: ~2 weeks for one engineer.

Critical: ship with Talk Mode first (simpler); Voice Wake
second when stability is proven. Operators can use Talk Mode
indefinitely if they prefer.
