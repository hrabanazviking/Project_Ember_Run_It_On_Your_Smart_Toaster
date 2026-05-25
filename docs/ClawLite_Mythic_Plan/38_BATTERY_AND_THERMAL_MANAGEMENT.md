# Document 38: BATTERY AND THERMAL MANAGEMENT – The Jötunheimr Controller

## 1. Introduction: Surviving the Frost Giants

The **Jötunheimr Thermal Controller** is an energy-aware compute governor that dynamically monitors hardware telemetry to throttle inference, defer background tasks, and optimize for longevity.

---

## 2. The Three-Tiered State Machine

Jötunheimr operates Ember based on physical reality:

- **Green Zone (Wall power, < 65°C):** Max thread count, background tasks run freely.
- **Yellow Zone (Battery < 50%, 65-80°C):** Thread usage drops 50%. Background tasks suspended.
- **Red Zone (Battery < 15%, > 80°C):** 
  - Surtr engages Q2 Cascade.
  - LLM limited to 1 thread.
  - **Inter-token Sleep:** Ember injects a 50ms `sleep` between generating every token, allowing CPU C-states to cool the chip.

---

## 3. The "Cold-Start" Heuristic

When the CPU is cold, immediately slamming all 4 cores to 100% causes a thermal spike, triggering OS throttling. 
Jötunheimr starts inference on 1 thread and scales to 4 threads over the first 10 tokens, spreading the thermal load and avoiding panic-throttling.

---

## 4. Deferrable Background Queues

Every background task has an `energy_cost`. If the device is on battery, HIGH energy tasks (like vectorizing PDFs) are moved to the `Deferral Queue`. They remain dormant until wall power is connected, at which point the queue flushes.

---

## 5. Invented Method: "Thermal-Aware Prompt Compression"

Processing a large prompt generates the most heat ($O(N^2)$). If the device is in the Red Zone, Jötunheimr uses **Thermal-Aware Prompt Compression**.
1. Jötunheimr passes the massive prompt through a Tier 1 Spark model (1 thread).
2. The Spark model executes extractive summarization, compressing it down 70%.
3. The compressed "skeleton" is passed to `phi3:mini` for the query.

Ember sacrifices minor nuance to prevent a hard system crash, ensuring the user gets an answer without melting their hardware.

*(End of Document 38)*
