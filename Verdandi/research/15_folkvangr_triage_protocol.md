# The Fólkvangr Triage Protocol
## Valkyrie-Like Selection Intelligence for System Events

---

## 1. The Myth

Freyja receives half of those who die in battle — the other half goes to Odin's Valhöll. She chooses who enters Fólkvangr (her field of the slain). This is not random selection — it is **intelligent triage** based on qualities that matter for the system's ongoing health.

## 2. The Triage Protocol

```python
class FolkvangrTriage:
    """Fólkvangr triage — choosing which events live and which are deferred."""
    
    REALMS = {
        'folkvangr': {  # Process now — live in the field
            'priority': 'high',
            'processing': 'immediate',
            'description': 'Events that directly serve the user or system health'
        },
        'valholl': {  # Send to background — live in the hall
            'priority': 'medium',
            'processing': 'deferred',
            'description': 'Events that are important but not time-critical'
        },
        'battlefield': {  # Leave on the battlefield — died in action
            'priority': 'low',
            'processing': 'discarded',
            'description': 'Events that are noise, redundant, or irrelevant'
        }
    }
    
    def triage(self, event: dict) -> str:
        """Decide which realm an event belongs to."""
        score = self._score_event(event)
        if score >= 0.7:
            return 'folkvangr'  # Process now
        elif score >= 0.3:
            return 'valholl'    # Defer to background
        else:
            return 'battlefield'  # Discard
```

## 3. Scoring Criteria

Events are scored on five dimensions:

1. **Urgency** — Does this need immediate attention? (Muspelheim check)
2. **Relevance** — Is this connected to active goals? (Asgard check)
3. **Novelty** — Have we seen this before? (Seiðr check)
4. **Impact** — How much does this affect system health? (Thor check)
5. **Fertility** — Can this lead to new connections or insights? (Freyja check)

---

*Created by the Mythic Engineering Forge for VERÐANDI — The Norn of Becoming*
