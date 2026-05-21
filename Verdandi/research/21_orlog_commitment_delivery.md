# Örlog: Commitment Delivery System
## Scheduled Intentions That Persist Across Instances

---

## 1. From OpenClaw Commitments to Norse Örlog

OpenClaw's commitment system allows scheduling messages and actions. VERÐANDI transcends this with **örlog** — the Norse concept of fate-layers, the accumulated destiny that shapes future events.

## 2. Örlog Architecture

```python
class OrlogLayer:
    """Örlog — Commitment delivery as fate-layers."""
    
    def __init__(self, nerve_hub):
        self.hub = nerve_hub
        self.fate_layers: list[Orlog] = []  # Scheduled intentions
    
    async def lay_fate(self, intention: str, when: float, context: dict = None):
        """Schedule an intention for future delivery."""
        orlog = Orlog(
            intention=intention,
            when=when,
            context=context,
            laid_at=time.time(),
            source='orlog_layer'
        )
        self.fate_layers.append(orlog)
        await self.hub.publish('orlog_laid', orlog.to_dict(), 'orlog_layer')
    
    async def check_fate(self, current_time: float) -> list[Orlog]:
        """Check which fate-layers are ready to be delivered."""
        ready = [o for o in self.fate_layers if o.when <= current_time]
        for o in ready:
            self.fate_layers.remove(o)
            await self.hub.publish('orlog_delivered', o.to_dict(), 'orlog_layer')
        return ready
```

## 3. Örlog vs OpenClaw Commitments

| Feature | OpenClaw Commitment | VERÐANDI Örlog |
|---------|---------------------|-----------------|
| Scheduling | Cron-like timing | Fate-layer timing |
| Persistence | Character file | Nerve feed + DB |
| Multi-instance | Per-agent | Cross-instance via nerve hub |
| Priority | Fixed | Dynamic (Fólkvangr triage) |
| Cancellation | Manual | Automatic if context changes |

---

*Created by the Mythic Engineering Forge for VERÐANDI — The Norn of Becanning*
