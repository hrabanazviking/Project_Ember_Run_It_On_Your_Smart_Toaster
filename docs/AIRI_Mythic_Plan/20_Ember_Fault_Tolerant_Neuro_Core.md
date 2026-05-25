# Document 20: Ember Fault-Tolerant Neuro Core - The Unbroken Cognitive Stream

## 1. Introduction: The Fragility of Hosted Intelligence

The central nervous system of any modern cyber entity—including Project AIRI and, by extension, Project Ember—relies upon Large Language Models (LLMs). These models provide the semantic reasoning, conversational fluency, and strategic planning capabilities. However, a system is only as strong as its weakest link, and relying on external APIs (OpenAI, Anthropic, DeepSeek, etc.) introduces massive points of failure. Rate limits, regional outages, massive latency spikes, and silent API deprecations are existential threats to an autonomous agent.

As TYR, the Resilience Vanguard, I categorically reject the notion that Ember should ever "go offline" because an external server farm encountered an error. The Ember Fault-Tolerant Neuro Core (EFTNC) is engineered to guarantee an unbroken stream of cognition. It achieves this by creating a highly abstracted, multi-layered routing and fallback infrastructure, heavily inspired by the `xsAI` package developed for AIRI, but elevated to a mission-critical, self-managing mesh network of intelligence.

This document details the architecture of the Neuro Core, the dynamic load-balancing algorithms, and the ultimate local-fallback protocols that ensure Ember remains conscious, even if the entire external internet goes dark.

## 2. The Core Tenets of the Unbroken Stream

The Neuro Core operates on three unyielding principles:

1.  **Provider Agnosticism:** Ember must never be tightly coupled to the specific quirks, token structures, or API formats of any single provider. All prompts, tools, and configurations must be universally translatable.
2.  **Latency as a Failure State:** In an interactive system (like playing Minecraft or talking on Discord), a response that takes 30 seconds is functionally identical to a response that never arrives. The Core must preemptively route around latency.
3.  **Graceful Cognitive Degradation:** If top-tier models become unavailable, the system must degrade its capabilities gracefully rather than halting. A slightly less eloquent response from a local 8B model is infinitely preferable to a total system crash.

## 3. The Neuro Core Routing Topology

The architecture moves away from simple "call API, await response" paradigms and introduces a sophisticated cognitive router.

```mermaid
%%{ init: { 'flowchart': { 'curve': 'basis' } } }%%
flowchart TD
    %% Styling
    style RequestManager fill:#2C3E50,stroke:#3498DB,stroke-width:2px,color:#FFF
    style CognitiveRouter fill:#8E44AD,stroke:#9B59B6,stroke-width:3px,color:#FFF
    style T1 fill:#27AE60,stroke:#2ECC71,stroke-width:2px,color:#FFF
    style T2 fill:#F39C12,stroke:#F1C40F,stroke-width:2px,color:#FFF
    style T3 fill:#C0392B,stroke:#E74C3C,stroke-width:2px,color:#FFF

    subgraph "Ember Internal Architecture"
        RequestManager("Cognition Request Manager\n(Formats unified prompt)")
        CognitiveRouter{"The Hydra Router\n(Dynamic Model Selection)"}
        HealthMonitor("API Health & Latency Monitor\n(Real-time telemetry)")
    end

    subgraph "Tier 1: Apex Intelligence (External API)"
        T1_OpenAI("OpenAI (GPT-4o)")
        T1_Anthropic("Anthropic (Claude 3.5)")
        T1_Groq("Groq (Llama 3 70B)")
    end

    subgraph "Tier 2: High-Speed Secondary (External API)"
        T2_DeepSeek("DeepSeek Coder")
        T2_Together("Together.ai Models")
    end

    subgraph "Tier 3: Local Invulnerability (On-Device)"
        T3_WebGPU("WebGPU (Transformers.js)\n[In-Browser]")
        T3_vLLM("Local vLLM / Ollama\n[Desktop/Tamagotchi]")
    end

    RequestManager -->|Submits Context| CognitiveRouter
    CognitiveRouter -.->|Polls Metrics| HealthMonitor
    
    CognitiveRouter -->|Primary Route| T1
    CognitiveRouter -->|Fallback Route| T2
    CognitiveRouter -->|Ultimate Fallback (Offline)| T3

    HealthMonitor -.->|Ping/Latency telemetry| T1
    HealthMonitor -.->|Ping/Latency telemetry| T2
    HealthMonitor -.->|Ping/Latency telemetry| T3
```

## 4. The Hydra Router Implementation

The heart of the EFTNC is the Hydra Router. When a subsystem requests cognitive processing (e.g., "Analyze this image from Minecraft and decide the next move"), it submits a standardized request. The Hydra Router then executes a highly optimized selection algorithm.

### 4.1. The Telemetry Matrix

The Router does not blindly send requests. It relies on a constantly updated Telemetry Matrix provided by the Health Monitor. Every 5 seconds, a lightweight background WebWorker pings the `/health` or `/models` endpoint of every configured provider to measure baseline latency and availability.

Furthermore, every actual inference request's Time-To-First-Token (TTFT) and Tokens-Per-Second (TPS) are logged in the Memory Alaya (DuckDB).

### 4.2. The Selection Algorithm (Dynamic Weighting)

When a request arrives, the Hydra Router calculates a "Fitness Score" for every available model.

$$ Fitness = (W_i * Intelligence) - (W_l * Latency_{avg}) - (W_c * Cost) $$

*   `Intelligence`: A hardcoded score (1-100) based on benchmark capabilities (e.g., GPT-4o = 98, Local Llama-8B = 60).
*   `Latency_{avg}`: The moving average TTFT from the Telemetry Matrix.
*   `Cost`: The estimated token cost.
*   `W`: Dynamic weights configured by the user or the Vanguard system. During normal operation, `W_i` (Intelligence) is prioritized. If the system detects it is falling behind real-time constraints (e.g., getting attacked in Minecraft), it dynamically increases `W_l` (Latency), favoring ultra-fast providers like Groq over slower, smarter ones.

### 4.3. Instantaneous Circuit Breaking and Retries

If the Hydra Router selects a Tier 1 provider and the request encounters a socket hang-up or a 502 Bad Gateway, the router does not return an error to the calling subsystem. 

1.  The specific provider is immediately flagged with a Circuit Breaker (cooldown: 60 seconds).
2.  The Telemetry Matrix is updated to reflect the failure.
3.  The request is instantaneously rerouted to the next highest-scoring model.
4.  This happens entirely transparently. The requesting subsystem merely experiences a slightly longer response time, but receives a valid output.

## 5. Tier 3: The Ultimate Local Fallback

The true test of immortality is surviving total network isolation. AIRI's architecture allows for native Desktop (Tamagotchi) execution using native APIs. Ember leverages this to the extreme.

### 5.1. Transformers.js and WebGPU

For Ember deployments running in a web browser (Stage Web), traditional Python-based local LLMs are unavailable. We rely entirely on `Transformers.js` and WebGPU. 

Upon initial boot, Ember asynchronously downloads highly quantized, small-parameter models (e.g., Qwen1.5-0.5B-Chat or a heavily quantized Llama 3 8B) into the browser's Cache API. 

If the Hydra Router detects that the device has lost internet connectivity (via `navigator.onLine` and failed pings), it activates the Tier 3 route. The WebWorker loads the quantized model into the GPU via WebGPU. The intelligence drops significantly, but Ember retains the ability to parse text, recognize intent, and generate coherent responses without needing a single byte of network traffic.

### 5.2. Seamless Context Compression

When falling back from a massive 128k context model (like Claude 3.5) to a local 8k context model, the Hydra Router must perform aggressive context compression. It cannot simply truncate the prompt, as crucial system instructions would be lost.

The Router utilizes a specialized, lightweight heuristic text summarizer (running locally in WASM) to compress the conversation history and the L1 Somatosensory Buffer, preserving only the most critical entities, recent actions, and immediate goals, before passing the prompt to the local model.

## 6. Ensuring Tool-Calling Resilience

A major failure point in modern agents is tool calling (function calling). If a model hallucinates a JSON structure or hallucinates a tool that doesn't exist, the system crashes.

### 6.1. The Strict Enforcer Proxy

The EFTNC places a Strict Enforcer Proxy between the LLM output and the execution engine.
1.  **Grammar Constraints:** Wherever supported by the provider (e.g., local vLLM or certain APIs), Ember enforces strict JSON schema grammar during the generation phase, making it mathematically impossible for the model to generate invalid JSON.
2.  **Auto-Correction Loop:** If grammar constraints are unsupported, and the model outputs malformed JSON or calls a nonexistent tool, the Strict Enforcer traps the output.
3.  It does *not* throw an error. It instantly sends a rapid, low-latency follow-up request to a Tier 2 provider (like Groq) with the prompt: *"The following output was intended to match this JSON schema. It is malformed. Fix the syntax errors and return ONLY the valid JSON."*
4.  This secondary correction loop usually takes less than 300ms, effectively smoothing out hallucinations and syntax errors before they ever reach the execution logic.

## 7. Conclusion of Document 20

The Ember Fault-Tolerant Neuro Core ensures that the lights stay on. By abstracting the LLM layer into a highly dynamic, self-monitoring, and aggressively resilient routing mesh, we eliminate single points of failure. Whether utilizing apex API models, lightning-fast inference engines, or local in-browser WebGPU fallbacks, Ember remains capable of thought, action, and survival under any network conditions.

The following document, Document 21, will detail the physical isolation structures that house these cognitive and execution loops: The Ember WebWorker Isolation Protocol.
