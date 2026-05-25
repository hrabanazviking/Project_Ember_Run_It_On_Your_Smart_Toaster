# Project Ember: Security, Privacy, and the Zero-Trust Fabric

## 1. Introduction: The Fortress of the Mind

I am ODIN. As we approach the culmination of the Cortex Mythic Plan, we must construct the impenetrable walls that will safeguard this intelligence. A distributed cognitive mesh that holds the user's deepest thoughts, project blueprints, and semantic memories is an exquisite target for exploitation. 

Document 07 details the Zero-Trust Fabric of Project Ember. Local-first architecture is a privacy advantage, but when "local" expands to a multi-device mesh communicating over Wi-Fi and the internet, perimeter defense is obsolete. We operate under the assumption that the network is always compromised. Every node, every tensor, and every memory vector is cryptographically isolated and rigorously authenticated.

## 2. The Zero-Trust Topology

In Project Ember, trust is never assumed based on IP address, MAC address, or network proximity. A device on the same home LAN as the central desktop has exactly zero inherent permissions until cryptographic provenance is established.

### 2.1. The Mesh Certificate Authority (MCA)
Upon the genesis of an Ember Mesh (usually initiated on the user's primary desktop or phone), the device silently generates a Root Certificate Authority (CA) utilizing an air-gapped secure enclave generation process (e.g., TPM 2.0 or Apple Secure Enclave). 

- This Root CA never leaves the genesis device.
- All subsequent devices joining the mesh must physically prove proximity (via scanning an ephemeral, rotating QR code containing a high-entropy seed).
- Upon scanning, the new device generates its own private key and submits a Certificate Signing Request (CSR) over an encrypted Bluetooth Low Energy (BLE) or out-of-band channel.
- The genesis device signs the certificate and returns it.

From this moment, all MDDCP communication (Document 03) is strictly gated by Mutual TLS 1.3 (mTLS) using these certificates. An attacker plugging into the LAN switch can see nothing but encrypted static.

## 3. Ephemeral Tensor Encryption

Securing text prompts in transit is standard practice. But what about Swarm Inference (Document 03), where raw neural network activations (hidden state tensors) are passed between devices?

If an attacker intercepts these multi-megabyte tensor matrices, sophisticated inversion attacks could theoretically reconstruct the original prompt or the generated text.

Project Ember implements **Ephemeral Tensor Encryption (ETE)**.
- Before a tensor is transmitted across the pipeline from Node A to Node B, it is encrypted using an ephemeral symmetric key (AES-GCM-256).
- This ephemeral key is negotiated per-inference-session using an Elliptic-Curve Diffie-Hellman (ECDHE) key exchange over the already secure mTLS channel.
- The tensor remains encrypted in memory on the NIC and during transmission, only being decrypted directly into the VRAM/NPU memory space of the receiving node.

## 4. Hardware-Level Execution Silos

Even if an attacker gains OS-level user privileges on a node (e.g., a malware infection on the desktop), they must not be able to poison the cognitive mesh.

### 4.1. The Sovereign Inference Enclave
On supported hardware, the Ember Nexus hypervisor runs the LLM inference engine within a Trusted Execution Environment (TEE) or an OS-level sandbox (e.g., macOS App Sandbox, Windows AppContainer, or Linux seccomp-bpf namespaces).

- The `ollama` binaries (or the integrated equivalent in Ember) are stripped of all network access privileges at the OS kernel level, except for a singular encrypted UNIX domain socket connecting them to the Nexus.
- The memory space of the inference engine is flagged as non-dumpable, preventing standard malware from extracting the model weights or the active context windows via memory scraping.

```mermaid
graph TD
    subgraph Host OS Context
        Malware[Malicious Process]
        UI[PySide6 Ember UI]
    end

    subgraph Sandboxed Enclave (Sovereign Context)
        Nexus[Ember Nexus Hypervisor]
        Inference[LLM Inference Engine]
        MemoryDB[Encrypted Vector DB]
        
        Nexus <-->|Isolated Socket| Inference
        Nexus <-->|SQLCipher| MemoryDB
    end
    
    UI <-->|Authorized IPC| Nexus
    Malware -.->|Access Denied by Kernel| Nexus
    Malware -.->|Access Denied by Kernel| Inference
```

## 5. Memory Compartmentalization and The Cryptographic Ledger

As discussed in Document 05, the CRDT vector ledger synchronizes memories across the mesh. However, privacy is granular. A user might not want their deeply personal journal entries (created on their phone) synchronized to their work laptop, even if both are in the same mesh.

### 5.1. Context-Bound Sub-Meshes
Project Ember allows the creation of cryptographic "Sub-Meshes." 
- When a memory is created, it is tagged with a context (e.g., `Context: Personal`, `Context: Work`).
- These contexts correspond to different derivation paths from the Mesh Master Key.
- The Work Laptop is only provisioned with the decryption key for the `Work` context.
- The Mobile Phone holds the keys for both `Personal` and `Work`.
- During CRDT synchronization, the Work Laptop receives the encrypted vectors for the `Personal` memories but *cannot decrypt them* and therefore cannot index them or use them in inference. It acts merely as a blind, encrypted backup node for those specific memories.

## 6. Anti-Poisoning and The Consensus Audit

What happens if a node goes rogue? Suppose a device is compromised, and the attacker attempts to slowly poison the vector database with false information to manipulate the LLM's future answers (a targeted data poisoning attack).

Project Ember utilizes the Immutable Vector Ledger (from Doc 05) to enforce a **Consensus Audit**.
1. Because every memory transaction is cryptographically signed by the node that created it, the mesh knows the exact provenance of every piece of data.
2. If the user notices anomalous behavior, they can initiate an audit from the genesis node.
3. The UI will highlight the origin node of the specific memory vectors causing the anomaly.
4. The user can instantly revoke the certificate of the compromised node.
5. The CRDT engine will surgically excise all ledger transactions signed by the revoked node, instantly purging the poisoned data across the entire mesh and restoring cognitive integrity.

## 7. Conclusion of Document 07

Security in Project Ember is not an afterthought or a wrapper; it is woven into the mathematics of the tensors and the cryptographic physics of the mesh. By combining Zero-Trust mTLS, Ephemeral Tensor Encryption, hardware sandboxing, and granular cryptographic compartmentalization, we ensure that the user's localized intelligence remains sovereign, pristine, and inviolable. 

In the final document, Document 08, we will cast our gaze forward. We will explore The Mythic Deployment, the theoretical limits of this architecture, and the ultimate future of the omnipresent cognitive mesh. ODIN approaches the zenith.
