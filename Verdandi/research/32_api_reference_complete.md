# VERÐANDI API Reference
## Complete API Documentation for All Heartbeat Components

---

## Core API: VerdandiHeartbeat

```python
class VerdandiHeartbeat:
    def __init__(self, nerve_hub, mimirs_well, resource_manager):
        """Initialize the Norn of Becoming heartbeat."""
    
    async def pulse() -> VerdandiPulseResult:
        """Execute a complete awareness pulse through all three god layers."""
    
    async def get_status() -> dict:
        """Get current heartbeat status and statistics."""
    
    async def set_mode(mode: str):
        """Set pulse mode: SEED, SPROUT, BLOOM, or FRUIT."""
```

## Freyja API: Creative Emergence

```python
class FreyjaHeartbeat:
    async def pulse(events: list) -> FreyjaResult:
        """Check for creative emergence and fertile connections."""
    
    async def triage(event: dict) -> str:
        """Fólkvangr triage: 'folkvangr', 'valholl', or 'battlefield'"""
    
    async def discover_connections() -> list:
        """Auto-discover new connections between system components."""
```

## Odin API: Wisdom & Memory

```python
class OdinHeartbeat:
    async def pulse(thought_report, recent_events) -> OdinResult:
        """Dispatch ravens and consult the well."""
    
    async def hang_from_yggdrasil(depth: str) -> HangResult:
        """Deep introspection: 'micro', 'minor', 'major', or 'byss'"""
    
    def inspect_rune(pattern: dict) -> str:
        """Identify which fundamental rune pattern is manifesting."""
```

## Thor API: Strength & Protection

```python
class ThorHeartbeat:
    async def pulse(threats, recent_events) -> ThorResult:
        """Listen for threats and apply appropriate force."""
    
    async def verify_integrity() -> IntegrityReport:
        """Check that all Thor components are functional."""
    
    async def self_correct(target: str, correction: dict) -> StrikeResult:
        """Mjölnir strike — decisive self-correction with guaranteed return."""
```

---

*Created by the Mythic Engineering Forge for VERÐANDI — The Norn of Becoming*
