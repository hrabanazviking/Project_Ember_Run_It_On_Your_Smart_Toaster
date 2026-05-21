# Circadian Rhythm & Active Hours
## Respecting the User's Biological Patterns

---

## 1. From OpenClaw to VERÐANDI

OpenClaw has a sophisticated active-hours system that respects user sleep schedules. VERÐANDI must adopt this AND transcend it — not just respecting when the user is active, but understanding their biological rhythms.

## 2. The Circadian Rhythm Layer

```python
class CircadianRhythm:
    """Track and respect the user's biological patterns."""
    
    PHASES = {
        'dawn':    {'hours': (6, 9),   'energy': 'rising',  'pulse_mode': 'SEED'},
        'morning': {'hours': (9, 12),   'energy': 'peak',    'pulse_mode': 'BLOOM'},
        'midday':  {'hours': (12, 14),  'energy': 'sustained','pulse_mode': 'SPROUT'},
        'afternoon':{'hours': (14, 18), 'energy': 'moderate','pulse_mode': 'SPROUT'},
        'evening': {'hours': (18, 22),  'energy': 'declining','pulse_mode': 'SEED'},
        'night':   {'hours': (22, 6),   'energy': 'rest',    'pulse_mode': 'SEED'},
    }
    
    def get_pulse_mode(self, hour: int) -> str:
        phase = self._get_phase(hour)
        return self.PHASES[phase]['pulse_mode']
```

## 3. Integration with VERÐANDI

- Morning (peak energy): More creative pulses, BLOOM mode, Freyja's fertility
- Afternoon (moderate): Standard SPROUT pulses, balanced monitoring
- Evening (declining): Conservative SEED pulses, minimal creative exploration
- Night (rest): Minimal heartbeat, watch-only mode

---

*Created by the Mythic Engineering Forge for VERÐANDI — The Norn of Becoming*
