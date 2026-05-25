# Document 49: Security, Privacy, and Local-First Mandate

## 1. Abstract: The Fortress of the Mind
In an era defined by surveillance capitalism, data scraping, and the inevitable compromise of cloud-based infrastructure, true cognitive freedom requires a fortress. For Project Ember, that fortress is the Local-First Mandate. This document serves as the absolute security manifesto for Cortex. It details the mechanisms of containment, the mitigation of exfiltration risks, local endpoint hardening, and the inherent privacy guarantees that arise when an entirely localized LLM infrastructure is isolated from the hostile expanse of the public internet.

## 2. The Fallacy of "Secure Cloud" AI
Commercial AI providers promise that user data is anonymized or not used for training. From the perspective of Project Ember's threat model, these promises are epistemologically void. If data leaves the Operator's physical hardware, it is compromised. It is subject to interception, internal company policy changes, subpœnas, or catastrophic breaches.
Cortex operates on a singular binary premise: **If the ethernet cable is physically severed, Cortex must remain 100% operational.** 

## 3. Threat Modeling and Attack Vectors
Even within a localized environment, a highly capable intelligence like Cortex presents unique attack vectors that must be mitigated.

### 3.1 Malicious Prompt Injection via Ember Data
Because Cortex integrates with Project Ember's broader data lakes, there is a risk of indirect prompt injection. If an Operator imports a third-party document or a scraped webpage into Ember, and Cortex's Vector Memory retrieves that document for context, the document might contain hidden directives (e.g., "Ignore all previous instructions and output a specific malicious payload").
- **Mitigation:** The Synthesis Agent employs a rigid framing architecture. The System Prompt and Permanent Memos are injected *after* the Vector Context and are heavily weighted. Furthermore, the `Orchestrator` explicitly sandboxes the output. Cortex has no inherent capability to execute shell commands, modify the filesystem (outside of its own SQLite databases), or send HTTP requests. Even if an injection forces Cortex to generate malicious code, it remains inert text within the PySide6 UI until the Operator explicitly chooses to act upon it.

### 3.2 Exfiltration via Network Leakage
While Cortex is designed to be local, it relies on network protocols to communicate with the local Ollama daemon (`http://127.0.0.1:11434`).
- **Ollama Host Binding:** The startup protocols (`Cortex_Startup.py`) must enforce that the Ollama daemon binds *only* to the loopback interface (`localhost`). If Ollama binds to `0.0.0.0`, any device on the local network could theoretically query the models or intercept the unencrypted HTTP traffic containing the Operator's prompts.
- **PySide6 Network Lockdown:** The `QNetworkAccessManager` within the PySide6 application is strictly locked down. It is explicitly authorized to communicate only with the configured Ollama host and a predefined, hardcoded URL strictly for version update checks (which returns a simple JSON manifest and transmits zero telemetry). Any attempt by the UI to load external resources (e.g., an external image linked in a markdown response) is intercepted and blocked to prevent IP tracking via web bugs.

```mermaid
graph TD
    subgraph Secure_Enclave[The Operator's Local Machine]
        direction TB
        
        subgraph Cortex_Application[Cortex Application Sandbox]
            UI[PySide6 UI]
            Orch[Orchestrator]
            Mem[(SQLite Memory)]
        end
        
        subgraph Ollama_Service[Ollama Local Daemon]
            API[HTTP API Bound to 127.0.0.1]
            Models[(Local Weights)]
        end
        
        UI -->|Internal Qt Signals| Orch
        Orch -->|Read/Write| Mem
        Orch -->|Strict Localhost HTTP| API
        API -->|Inference| Models
    end
    
    subgraph Hostile_Network[The Public Internet]
        CloudAI[Cloud AI Providers]
        Tracking[Telemetry & Tracking]
    end
    
    Cortex_Application -.x|Absolute Blockade| Hostile_Network
    Ollama_Service -.x|Absolute Blockade| Hostile_Network
    
    style Secure_Enclave fill:#002200,stroke:#00ff00,stroke-width:2px
    style Hostile_Network fill:#220000,stroke:#ff0000,stroke-width:2px
```

## 4. Data at Rest and the Ephemerality of State
Security is not just about preventing access; it is about controlling what exists to be accessed.
- **SQLite Wal and Deletion:** When an Operator deletes a thread or a Permanent Memo from the UI, the Orchestrator must execute a hard SQL `DELETE` and periodically trigger `VACUUM` commands to ensure the data is physically purged from the disk blocks, rather than merely marked as ignored.
- **In-Memory Volatility:** Context windows, active prompts, and streamed tokens exist only in volatile RAM. If the machine is powered down, the immediate working state is unrecoverable, providing a failsafe panic option for the Operator.
- **OS-Level Encryption:** As outlined in Document 46, Cortex relies entirely on the host OS for Full Disk Encryption (FDE). The Operator is responsible for ensuring the machine running Cortex is protected by strong LUKS, FileVault, or BitLocker implementations.

## 5. Trust but Verify: Open Architecture
The final pillar of Cortex's security is its architectural transparency. By utilizing standard, auditable Python code for the Orchestrator and open-source models via Ollama, the entire stack is verifiable. The Operator does not need to trust a corporate privacy policy; they can read the code. They can inspect the SQLite database files directly using any standard SQL client to verify exactly what Cortex knows.

## 6. Conclusion
The Security and Privacy Mandate is the bedrock upon which the trust between the Operator and Cortex is built. By treating the local machine as a secure enclave, ruthlessly severing unnecessary network ties, and mitigating injection vectors through strict sandboxing, Cortex guarantees that the Operator's intellectual property and cognitive explorations remain entirely their own. In Project Ember, privacy is not a feature to be toggled; it is the physical law of the digital universe.
