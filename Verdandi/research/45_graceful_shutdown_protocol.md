# Graceful Shutdown Protocol
## Draining Subscribers Before Closing

---

## 1. Shutdown Sequence

1. **Stop accepting new subscribers**
2. **Drain existing subscriber queues** (up to 5 seconds)
3. **Write final shutdown event to feed**
4. **Close the Unix domain socket**
5. **Remove the PID file**
6. **Exit cleanly**

## 2. Signal Handling

- **SIGTERM**: Initiate graceful shutdown
- **SIGINT**: Same as SIGTERM
- **SIGHUP**: Not handled (systemd restarts on failure)

## 3. Emergency Shutdown

If graceful shutdown takes more than 10 seconds, force close all connections and exit immediately.

---

*Created by the Mythic Engineering Forge for VERÐANDI — The Norn of Becoming*
