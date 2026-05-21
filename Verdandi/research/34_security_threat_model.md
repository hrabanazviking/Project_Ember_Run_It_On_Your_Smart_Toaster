# Security Threat Model
## E→M→B Vulnerability and Norse Defense Architecture

---

## 1. Key Vulnerability: E→M→B Attack

Zhang et al. (2026) identified that heartbeat-driven agents can be memory-polluted through the E→M→B (Exposure→Memory→Behavior) pathway:
- **Exposure**: Attacker feeds malicious data through input channels
- **Memory**: Agent stores the malicious data in long-term memory
- **Behavior**: Agent later acts on the stored malicious data

## 2. Thor's Defense Against E→M→B

| Attack Phase | Thor Defense |
|---|---|
| Exposure (E) | Járngreipr — validate all inputs before processing |
| Memory (M) | Algiz rune — access control on memory writes |
| Behavior (B) | Mjölnir — detect and correct malicious behavior |

## 3. Additional Defenses

- **Socket permissions (0600)**: Only the owner can read/write the nerve hub
- **Stale subscriber pruning**: Prevent abuse of long-running subscriptions
- **PID race protection**: Prevent process substitution attacks
- **Feed rotation**: Prevent disk exhaustion attacks
- **Dedup suppression**: Prevent event injection attacks

---

*Created by the Mythic Engineering Forge for VERÐANDI — The Norn of Becanning*
