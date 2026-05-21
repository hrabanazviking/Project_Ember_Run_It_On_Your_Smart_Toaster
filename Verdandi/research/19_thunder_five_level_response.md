# Thunder: Five-Level Threat Response
## From Rumble to Mjölnir Strike

---

## 1. Threat Levels

| Level | Name | Response | Example |
|-------|------|----------|---------|
| 1 | Rumble | Log and monitor | Unusual nerve impulse frequency |
| 2 | Clap | Throttle and warn | Resource usage spike |
| 3 | Crack | Suspend and isolate | Potential infinite loop detected |
| 4 | Bolt | Terminate and quarantine | Memory leak or security breach |
| 5 | Mjölnir | Full reset | System compromise or data corruption |

## 2. Escalation Protocol

```python
class Thunder:
    async def strike(self, threat: Threat) -> ThunderResult:
        level = self._assess_level(threat)
        match level:
            case 1:  # Rumble — just log
                await self._log_threat(threat)
            case 2:  # Clap — throttle
                await self._throttle(threat.source)
            case 3:  # Crack — suspend
                await self._suspend(threat.source)
            case 4:  # Bolt — terminate
                await self._terminate(threat.source)
                await self._quarantine(threat.source)
            case 5:  # Mjölnir — full reset
                await self._full_reset()
        return ThunderResult(level=level, action=TAKEN)
```

## 3. De-escalation

After a threat is neutralized, Thor doesn't stay angry. The system returns to normal:
- **Rumble → Normal**: Immediate
- **Clap → Rumble**: After 5 minutes of calm
- **Crack → Clap**: After 15 minutes of calm
- **Bolt → Crack**: After 30 minutes of calm
- **Mjölnir → Bolt**: Never — a Mjölnir strike means something fundamental changed

---

*Created by the Mythic Engineering Forge for VERÐANDI — The Norn of Becoming*
