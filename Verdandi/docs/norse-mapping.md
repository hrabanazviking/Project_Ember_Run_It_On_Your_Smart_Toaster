# 🏛️ Norse Mythology Mapping

## Why Norse Names?

Verðandi uses Norse mythological names because they're **meaningful abstractions**, not arbitrary labels. Each name was chosen because the deity or concept maps directly to the function of that code module. This isn't decoration — it's a mnemonic system that makes the architecture memorable and self-documenting.

## The Norns

| Name | Norse Role | Code Role | Module |
|------|-----------|-----------|--------|
| **Urðr** (Urd) | Norn of the Past — "what was" | Schedule — checking what has been planned | `heartbeat/checks/urdr.py` |
| **Verðandi** | Norn of the Present — "what is becoming" | The entire daemon — continuously becoming | `heartbeat/core.py` |
| **Skuld** | Norn of the Future — "what shall be" | Planned: predictive analysis module | Future |

## The Four Senses

| Name | Norse Role | Code Role | Module |
|------|-----------|-----------|--------|
| **Eir** | Goddess of Healing and Medicine | Health checks — diagnosing what ails the system | `heartbeat/checks/eir.py` |
| **Huginn** | Odin's Thought Raven — "the one who flies out each day to gather information" | Project checks — surveying the state of code | `heartbeat/checks/huginn.py` |
| **Mímir** | The Wise — keeper of the well of wisdom that Odin sacrificed an eye to drink from | Memory checks — verifying the store of knowledge | `heartbeat/checks/mimir.py` |
| **Urðr** | As above — also represents the schedule (past commitments coming due) | Schedule checks — reviewing what's been promised | `heartbeat/checks/urdr.py` |

## The Four Acts

| Name | Norse Role | Code Role | Module |
|------|-----------|-----------|--------|
| **Mjölnir** | Thor's Hammer — the divine instrument that smashes threats and protects the realm | Restart/cleanup actions — smashing problems | `heartbeat/actions/mjolnir_action.py` |
| **Gungnir** | Odin's Spear — always hits its target, never misses | Escalation actions — precisely targeted notifications | `heartbeat/actions/gungnir_action.py` |
| **Bifrǫst** | The Rainbow Bridge — connects Midgard to Asgard | Bridge actions — forwarding to external systems | `heartbeat/actions/bifrost_action.py` |
| **Eir** | As above — also the goddess who heals | Auto-heal actions — repairing corrupted state | `heartbeat/actions/eir_action.py` |

## The Watchman

| Name | Norse Role | Code Role |
|------|-----------|-----------|
| **Heimdall** | The Watchman — sees everything, hears everything, guards the Bifröst | Circuit breaker pattern + health score trending |

## Supporting Concepts

| Name | Norse Role | Code Role |
|------|-----------|-----------|
| **Hjartsláttur** | "Heartbeat" in Old Norse | The daemon's name in the system |
| **Yggdrasil** | The World Tree connecting all nine realms | The interconnected system architecture |
| **Bifröst** | Rainbow Bridge between realms | Unix domain socket nerve hub |
| **Urðarbrunnr** | The Well of Fate at the base of Yggdrasil | The state database (heartbeat.db) |
| **Mímisbrunnr** | The Well of Wisdom | The Mímir knowledge database |

## The Deeper Metaphor

In Norse cosmology, the three Norns draw water from Urðarbrunnr (the Well of Fate) and pour it over Yggdrasil's roots, keeping the World Tree alive. In our system:

- **Verðandi draws from the well of state** (heartbeat.db) each pulse
- **She pours the results over the roots** (nerve hub) to nourish the system's awareness
- **What was (Urðr)** feeds **what is becoming (Verðandi)**, which shapes **what shall be (Skuld)**

The circuit breaker is Heimdall standing at the bridge, deciding when to close the gate. The health score is the thread the Norns weave — measuring the fabric of the system's wellbeing over time.

The daemon loop is the pulse of the World Tree itself: regular, rhythmic, essential. When the pulse stops, the Tree sickens. When the pulse is strong, the Tree flourishes.

This isn't just naming — it's a **semantic architecture**. The myth tells you how the code works.