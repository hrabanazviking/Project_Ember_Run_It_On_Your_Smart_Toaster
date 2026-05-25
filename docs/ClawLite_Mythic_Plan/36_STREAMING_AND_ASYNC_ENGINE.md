# Document 36: STREAMING AND ASYNC ENGINE – The Gjallarhorn Stream Engine

## 1. Introduction: The Sound of Gjallarhorn

The **Gjallarhorn Stream Engine** is the high-performance asynchronous networking and streaming architecture that ensures information flows instantly, concurrently, and without bottlenecks across all subagents and user interfaces. 

Gjallarhorn guarantees **Zero-Latency User Feedback** through multiplexed channels, backpressure handling, priority queues, and a deeply integrated asyncio core built on top of `uvloop`.

---

## 2. The Asynchronous Core: `uvloop`

Ember abandons standard Python `asyncio` loops for `uvloop` (built on `libuv`), providing a 2-4x performance boost. Everything is scheduled on the main event loop. Blocking I/O is strictly banished to a `ThreadPoolExecutor` (the "Exile Pool").

---

## 3. Multiplexed Streaming Channels

Gjallarhorn implements a multiplexed streaming protocol over WebSockets.
- **Voice Channel (`ch:out`):** User-facing text output.
- **Thought Channel (`ch:tht`):** Internal monologue (`<think>` tags).
- **Action Channel (`ch:act`):** Structured tool calls.
- **Telemetry Channel (`ch:sys`):** Real-time hardware metrics.

```python
async def multiplex_stream(raw_token_generator, websocket):
    current_channel = "ch:out"
    buffer = ""
    async for token in raw_token_generator:
        buffer += token
        if "<think>" in buffer:
            current_channel = "ch:tht"
        # Dispatch token to the correct WebSocket channel...
```

---

## 4. Backpressure Handling: The Floodgates

If the LLM generates tokens faster than the network can send them, RAM fills up. Gjallarhorn implements strict **Backpressure Management**.
- If the WebSocket buffer exceeds the high-water mark, a signal is sent.
- This signal *pauses the Surtr Inference Engine*.
- Matrix multiplication stops until the network buffer drains, ensuring perfectly flat memory footprints.

---

## 5. Priority Job Queues and Preemption

All tasks go to the **Yggdrasil Queue**:
- **Pri 0:** User input processing, UI streaming.
- **Pri 1:** Active agent reasoning.
- **Pri 2:** Background vector indexing.

### 5.1 Async Preemption

If `phi3:mini` is generating a Pri 2 background summary and the user types a new message (Pri 0), Gjallarhorn uses **Async Preemption**. Because Surtr yields after every single token, Gjallarhorn intercepts execution, parks the Pri 2 state in RAM, processes the user request, and then restores the background task.

---

## 6. Invented Method: "Temporal Token Batching"

For high-latency links (e.g., SSH over satellite), sending 1 WebSocket frame per token chokes the connection. Gjallarhorn uses **Temporal Token Batching**.
- If RTT < 50ms, stream token-by-token.
- If RTT > 300ms, buffer tokens and send chunks every 250ms.
This reduces TCP overhead by 90%, preventing stutter and connection timeouts on poor networks.

*(End of Document 36)*
