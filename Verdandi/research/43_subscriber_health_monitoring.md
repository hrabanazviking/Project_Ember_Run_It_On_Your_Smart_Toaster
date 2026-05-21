# Subscriber Health Monitoring
## Stale Detection and Pruning for Real-Time Connections

---

## 1. Problem

Subscribers connect to the nerve hub to receive real-time impulses. But subscribers can disconnect without notifying the hub (crash, network issue). Stale subscribers consume resources.

## 2. Solution

Every subscriber sends a heartbeat every 30 seconds. If no heartbeat is received within 120 seconds, the subscriber is considered stale and is pruned.

## 3. Configurable Parameters

- `SUBSCRIBER_TIMEOUT`: 120 seconds (how long before considered stale)
- `SUBSCRIBER_PRUNE_INTERVAL`: 30 seconds (how often to check for stale subscribers)
- `SUBSCRIBER_HEARTBEAT_INTERVAL`: 30 seconds (how often subscribers should heartbeat)

---

*Created by the Mythic Engineering Forge for VERÐANDI — The Norn of Becoming*
