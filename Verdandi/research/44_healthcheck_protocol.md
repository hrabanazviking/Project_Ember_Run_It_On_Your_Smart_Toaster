# Healthcheck Protocol
## Verifying All Components Are Alive and Functional

---

## 1. Healthcheck Command

```bash
python3 ~/.hermes/state/nervous_system.py healthcheck
```

## 2. Checks Performed

1. **Socket exists**: Is the Unix domain socket file present?
2. **Socket responsive**: Can we connect and send a command?
3. **PID valid**: Is the hub process still running?
4. **Feed writable**: Can we append to the nerve feed file?
5. **Ring buffer**: Is the in-memory buffer functional?
6. **Recent events**: Are new events being received?

## 3. Output Format

```
🧠 VERÐANDI Health Check
========================
✅ Socket: /home/pi/.hermes/state/runa.sock (responsive)
✅ Feed: /home/pi/.hermes/state/nerve_feed.jsonl (writable, 5 events)
✅ PID: 321971 (running)
✅ Ring buffer: 5/256 events
✅ Hub: responsive to commands
========================
ALL CHECKS PASSED ✅
```

---

*Created by the Mythic Engineering Forge for VERÐANDI — The Norn of Becoming*
