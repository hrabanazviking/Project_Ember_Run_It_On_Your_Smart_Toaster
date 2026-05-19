# IT307: Quantum-Safe Cryptography Migration
## Bachelor of Science in Information Technology — University of Yggdrasil, 2040

**Credits:** 4
**Description:** A comprehensive guide to the most consequential infrastructure migration in IT history — transitioning from classical public-key cryptography (RSA, ECC) to post-quantum cryptographic algorithms before quantum computers render current encryption obsolete. Covers the quantum threat timeline, NIST PQC standards, migration strategies, hybrid cryptography, crypto-agility, and the organizational challenge of updating every certificate, key, and protocol in the enterprise.

**Prerequisites:** IT303 (Zero-Trust Security Architecture), IT305 (Disaster Recovery & Business Continuity)
**Instructor:** Dr. Brynhildr Véfreyjasdóttir, Department of Information Technology

**Course Philosophy:** The cryptographic foundations of digital civilization are about to break. Every TLS connection, every digital signature, every VPN tunnel, every blockchain — all secured by mathematical problems that quantum computers will solve in hours or minutes. This is not science fiction; NIST began standardizing replacement algorithms in 2024, and the "harvest now, decrypt later" threat means data intercepted today may be decrypted retroactively. The migration to post-quantum cryptography is the largest, most complex infrastructure project the IT industry has ever undertaken. This course prepares you to lead it. In the Norse tradition, Ragnarök is prophesied — but the wise prepare, and the prepared survive. The quantum Ragnarök is coming. We will be ready.

---

## Lectures

ᚠ **Lecture 1: The Quantum Threat — Why Cryptography Must Change**

**Course:** IT307 — Quantum-Safe Cryptography Migration
**Degree:** Bachelor of Science in Information Technology, 2040

---

### Overview

The cryptographic systems that secure the internet — RSA, Diffie-Hellman, Elliptic Curve Cryptography (ECC) — are based on mathematical problems (integer factorization, discrete logarithm) that are computationally infeasible for classical computers. Quantum computers running Shor's algorithm change this calculus entirely. This lecture explains the quantum threat: how quantum computing works at a conceptual level, why it breaks current public-key cryptography, and the timeline for when cryptographically relevant quantum computers (CRQCs) are expected to arrive. The key message: the migration must begin now, not when the threat materializes, because migration takes years and the "harvest now, decrypt later" threat means yesterday's encrypted data is already at risk.

### Lecture Notes

Classical public-key cryptography rests on a single pillar: certain mathematical operations are easy to perform in one direction but prohibitively difficult to reverse. Multiply two large prime numbers together? Easy — even for 2048-bit numbers, a modern computer can do it in milliseconds. Factor the product back into its constituent primes? For a 2048-bit RSA key, this would take a classical computer billions of years. The asymmetry between the forward operation (encryption, signature verification) and the reverse operation (decryption, signature forgery without the key) is what makes public-key cryptography possible.

Quantum computing breaks this asymmetry. Peter Shor's 1994 algorithm demonstrated that a sufficiently powerful quantum computer could factor integers and compute discrete logarithms in polynomial time — transforming problems that are exponentially hard for classical computers into problems that are merely polynomial. A 2048-bit RSA key that would take a classical computer longer than the age of the universe to factor could be broken by a quantum computer with approximately 4,000 logical qubits in a matter of hours.

The timeline for cryptographically relevant quantum computers (CRQCs) has been the subject of intense debate and constant revision. In 2015, the consensus was "20+ years away." In 2020, "10–15 years." By 2030, prototype quantum computers with 100+ noisy qubits existed but were far from the millions of physical qubits needed for error-corrected logical qubits to run Shor's algorithm at cryptographic scale. By 2040, the timeline has firmed: most experts predict CRQCs capable of breaking 2048-bit RSA within 5–10 years. The National Security Agency (NSA) mandated post-quantum migration for national security systems by 2035. The financial sector has targeted 2038 for completion. Organizations that have not started their migration by 2040 are already behind.

The "**harvest now, decrypt later**" (HNDL) threat makes the timeline more urgent than it appears. An adversary — a nation-state or well-resourced criminal organization — can intercept and store encrypted traffic today, even though they cannot decrypt it. When a CRQC becomes available in 5–10 years, they will use it to retroactively decrypt everything they harvested. Any data with a sensitivity lifetime longer than the time until a CRQC arrives is already at risk. Medical records (lifetime sensitivity), financial data (decades), classified information (25–50 years), intellectual property (varies) — all must be protected against HNDL now, not when the CRQC arrives.

The specific algorithms at risk: **RSA** (all key sizes, for both encryption and signatures), **Diffie-Hellman** (both finite-field and elliptic-curve variants), **ECDSA** and **EdDSA** (elliptic curve signature schemes), and any protocol built on these primitives — which is essentially all of them. TLS, SSH, IPsec, S/MIME, PGP, DNSSEC, blockchain consensus, code signing, software update verification — all use algorithms that Shor's algorithm breaks. Symmetric cryptography (AES, ChaCha20) and hash functions (SHA-256, SHA-3) are affected differently: Grover's algorithm provides a quadratic speedup for brute-force attacks, meaning AES-128 becomes effectively 64-bit security (inadequate), but AES-256 remains secure (128-bit effective security). The migration burden falls primarily on public-key systems.

The quantum threat is not theoretical. It is the most predictable, most consequential, and most time-sensitive infrastructure challenge in the history of IT. The organizations that survive it will be those that started preparing earliest. This course ensures you are among them.

### Required Reading

- Shor, P. W. (1994). "Algorithms for Quantum Computation: Discrete Logarithms and Factoring." *Proceedings of the 35th Annual Symposium on Foundations of Computer Science*.
- NIST. (2024). "Post-Quantum Cryptography Standards." NIST Special Publication 800-208.
- NSA. (2022). "Announcing the Commercial National Security Algorithm Suite 2.0." CNSA 2.0 Timeline.
- Mosca, M. (2018). "Cybersecurity in an Era with Quantum Computers: Will We Be Ready?" *IEEE Security & Privacy*, 16(5), 38–41.

### Discussion Questions

1. If the CRQC timeline is uncertain (anywhere from 5 to 15 years), how should an organization decide how urgently to invest in PQC migration?
2. "Harvest now, decrypt later" means data intercepted today is at risk. What categories of your own personal data would be most concerning if decrypted in 10 years?
3. Symmetric cryptography (AES) is not broken by Shor's algorithm, only weakened by Grover's. Should symmetric key sizes be increased as part of PQC migration, or is AES-256 already sufficient?

---

ᚢ **Lecture 2: The NIST PQC Standards — Meet the Replacement Algorithms**

**Course:** IT307 — Quantum-Safe Cryptography Migration
**Degree:** Bachelor of Science in Information Technology, 2040

---

### Overview

In 2016, NIST launched a public competition to select quantum-resistant cryptographic algorithms — the cryptographic community's equivalent of the Advanced Encryption Standard (AES) competition of the late 1990s. After three rounds of evaluation, NIST announced its first selections in 2024. This lecture introduces the NIST PQC standards: CRYSTALS-Kyber (key encapsulation), CRYSTALS-Dilithium and FALCON (digital signatures), and SPHINCS+ (stateless hash-based signatures). Students learn the mathematical foundations — lattice-based cryptography, hash-based signatures — and the practical characteristics (key sizes, signature sizes, performance) that determine where each algorithm fits in enterprise architecture.

### Lecture Notes

The NIST PQC standardization process was unprecedented in its transparency and rigor. Eighty-two candidate algorithms were submitted in 2017. After three rounds of public cryptanalysis — with researchers worldwide attempting to break every candidate — NIST selected four algorithms for standardization in 2024, with additional candidates under consideration for future rounds.

**CRYSTALS-Kyber (ML-KEM)**: The selected Key Encapsulation Mechanism (KEM) — the post-quantum replacement for RSA encryption and Diffie-Hellman key exchange. Kyber is based on the Module Learning With Errors (MLWE) problem, a lattice-based hardness assumption that has resisted quantum and classical cryptanalysis since its introduction by Regev in 2005. Kyber offers small ciphertexts (768–1568 bytes), fast operations, and three security levels (Kyber-512, Kyber-768, Kyber-1024). Its primary disadvantage is larger public keys and ciphertexts than ECC — a TLS handshake using Kyber will be noticeably larger than one using ECDH. NIST standardized Kyber as ML-KEM (Module-Lattice Key Encapsulation Mechanism).

**CRYSTALS-Dilithium (ML-DSA)**: The primary selected digital signature algorithm — the post-quantum replacement for RSA signatures, ECDSA, and EdDSA. Dilithium is also lattice-based (MLWE and MSIS problems). It offers reasonable signature sizes (2420–4595 bytes) and public key sizes (1312–2592 bytes), with fast signing and verification. Its main disadvantage is signature size — Dilithium signatures are approximately 10x larger than Ed25519 signatures, which has significant implications for protocols where signatures are transmitted frequently (TLS, certificate chains, blockchain transactions). NIST standardized Dilithium as ML-DSA.

**FALCON (FN-DSA)**: An alternative signature algorithm, also lattice-based but using the NTRU lattice problem and a different mathematical approach (fast Fourier sampling). FALCON offers smaller signatures than Dilithium (666–1280 bytes) but requires floating-point arithmetic for signing, making it harder to implement securely against side-channel attacks. NIST selected FALCON as an alternative standard (FN-DSA) for applications where signature size is critical and side-channel resistance can be managed.

**SPHINCS+ (SLH-DSA)**: A stateless hash-based signature scheme — fundamentally different from lattice-based approaches. SPHINCS+ security relies only on the security of the underlying hash function (SHA-256 or SHAKE256), making it the most conservative choice — if hash functions remain secure, SPHINCS+ remains secure, regardless of advances in lattice cryptanalysis. The cost: massive signatures (7856–49856 bytes) and public keys. SPHINCS+ is recommended for long-term, high-assurance applications (root CAs, firmware signing) where signature size is secondary to cryptographic conservatism.

The **key size comparison** tells the migration story:

| Algorithm | Public Key | Ciphertext/Signature |
|-----------|-----------|---------------------|
| RSA-2048 | 256 bytes | 256 bytes |
| ECDH P-256 | 64 bytes | — |
| Ed25519 | 32 bytes | 64 bytes |
| Kyber-768 | 1184 bytes | 1088 bytes |
| Dilithium-3 | 1952 bytes | 3293 bytes |
| FALCON-512 | 897 bytes | 666 bytes |
| SPHINCS+-128s | 32 bytes | 7856 bytes |

The size increase is dramatic. A TLS 1.3 handshake with ECDH key exchange and Ed25519 signatures requires a few hundred bytes of cryptographic material. The same handshake with Kyber + Dilithium requires several kilobytes. This has cascading effects: larger packets, more fragmentation, higher latency, increased bandwidth consumption, and compatibility challenges with protocols that have fixed-size fields. The migration is not a drop-in replacement — it requires protocol engineering to accommodate larger cryptographic objects.

By 2040, **hybrid cryptography** — combining classical and post-quantum algorithms — has become standard practice during the migration period. A hybrid key exchange performs both an ECDH exchange AND a Kyber exchange, combining the two shared secrets. If either algorithm is secure, the resulting key is secure. This provides defense-in-depth: protection against quantum attacks (from Kyber) while retaining protection against any undiscovered weakness in the relatively young lattice-based schemes (from ECDH). Hybrid mode is recommended by NIST and required by many regulators during the transition period, expected to last through the 2040s.

### Required Reading

- NIST SP 800-208: "Post-Quantum Cryptography Standards" (2024). Full specifications for ML-KEM, ML-DSA, and SLH-DSA.
- Alagic, G., et al. (2022). "Status Report on the Third Round of the NIST Post-Quantum Cryptography Standardization Process." NISTIR 8413.
- Bernstein, D. J., & Lange, T. (2017). "Post-Quantum Cryptography." *Nature*, 549, 188–194.

### Discussion Questions

1. Kyber + Dilithium increase TLS handshake sizes by ~10x. For IoT devices with limited bandwidth, is PQC migration even feasible, or do we need fundamentally different approaches?
2. SPHINCS+ is the most conservative choice (hash-based, not lattice-based) but has enormous signatures. For what applications is "most conservative" worth the cost?
3. Hybrid cryptography provides defense-in-depth but doubles the cryptographic overhead. When should organizations transition from hybrid to PQC-only?

---

ᚦ **Lecture 3: Crypto-Agility — Designing for Algorithm Replacement**

**Course:** IT307 — Quantum-Safe Cryptography Migration
**Degree:** Bachelor of Science in Information Technology, 2040

---

### Overview

The PQC migration is not the last cryptographic migration. New mathematical attacks, algorithmic innovations, and computing paradigms will continue to emerge. Crypto-agility is the architectural principle that cryptographic algorithms should be swappable without rewriting applications, re-architecting protocols, or disrupting operations. This lecture teaches the design patterns of crypto-agile systems: algorithm negotiation, pluggable cryptographic providers, protocol versioning, and the organizational practices (cryptographic inventories, algorithm lifecycle management) that enable rapid migration when the next cryptographic crisis arrives.

### Lecture Notes

Most enterprise systems were not designed for cryptographic agility. They were designed in an era when RSA and AES were assumed to be eternal — hardcoded into application logic, baked into protocol implementations, embedded in hardware. When a TLS library hardcodes "RSA_WITH_AES_256_GCM" as the cipher suite, migrating to Kyber requires changing the library, recompiling the application, retesting everything, and redeploying — a process measured in months or years for large codebases. When the cryptographic algorithm is baked into a hardware security module (HSM) or a smart card, migration requires physical hardware replacement.

Crypto-agility is the antidote. A crypto-agile system has three properties:

**Algorithm Independence**: The application does not depend on a specific algorithm. It depends on an abstract interface — "encrypt this data" or "sign this message" — and the actual algorithm is selected at runtime based on configuration or negotiation. This is the software engineering principle of dependency inversion applied to cryptography.

**Negotiated Selection**: When two systems communicate, they negotiate which algorithms to use, similar to TLS cipher suite negotiation. The client offers a list of supported algorithms; the server selects the strongest mutually supported option. This enables gradual migration — old clients using RSA can coexist with new clients using Kyber, as long as the server supports both.

**Pluggable Implementation**: New algorithms can be added to the system without modifying application code. The cryptographic provider — OpenSSL, BoringSSL, AWS KMS, hardware HSM — is abstracted behind a standard interface (PKCS#11, JCA/JCE, CNG), and new algorithms can be added by updating the provider, not the application.

The **protocol engineering** challenges of crypto-agility are substantial. TLS 1.3 already supports algorithm negotiation, but post-quantum algorithms require extensions: larger handshake messages, new named groups for Kyber, new signature algorithms for Dilithium. The IETF has been standardizing these extensions through the TLS Working Group since the early 2020s, and TLS 1.3 with PQC extensions (sometimes called "TLS 1.3 PQC" or simply implemented as extensions to TLS 1.3) is the standard by 2040. But legacy protocols — SSH, IPsec/IKEv2, S/MIME, PGP — each require their own PQC extensions, and progress varies.

**Cryptographic Inventory** is the organizational prerequisite for crypto-agility. You cannot migrate what you cannot see. A cryptographic inventory catalogs: every system that uses cryptography, which algorithms it uses, which key sizes, which protocols, which libraries, which certificates, and when each certificate expires. For a large enterprise, this inventory can contain thousands of entries. The 2040 practice of **automated cryptographic discovery** — using network scanning, code analysis, and certificate transparency logs to build and maintain the inventory — has made this feasible, but it remains a significant undertaking.

**Algorithm Lifecycle Management** extends the inventory into action. Each algorithm in the inventory has a lifecycle state: **Standard** (approved for use), **Legacy** (still supported but deprecated — migration should be planned), **Emergency** (known to be broken — must be replaced immediately), and **Retired** (must not be used). When a new vulnerability is discovered — whether quantum (Shor's algorithm) or classical (a new attack on a specific implementation) — the lifecycle management system identifies every system using the affected algorithm and triggers migration workflows. The transition from Legacy to Emergency can happen overnight (as it did for SHA-1 in 2017), and organizations without crypto-agility find themselves unable to respond.

The ultimate goal of crypto-agility is to make the PQC migration the LAST painful cryptographic migration. By building systems that can swap algorithms through configuration changes rather than code changes, we ensure that when the next mathematical breakthrough arrives — whether a quantum algorithm for lattice problems or an entirely new computing paradigm — the migration is measured in days, not decades.

### Required Reading

- Sullivan, N. (2022). "A Primer on Crypto-Agility." Cloudflare Blog.
- IETF TLS Working Group. (2025). "Post-Quantum TLS 1.3." RFC Series (PQC extensions).
- NIST. (2024). "Crypto-Agility: Considerations for Migrating to Post-Quantum Cryptographic Algorithms." NIST Whitepaper.
- Véfreyjasdóttir, B. (2039). "Automated Cryptographic Discovery: Building and Maintaining Enterprise Cryptographic Inventories." *ACM Conference on Computer and Communications Security*.

### Discussion Questions

1. Crypto-agility adds abstraction layers that have performance costs. For high-frequency trading systems where microseconds matter, is crypto-agility compatible with performance requirements?
2. Hardware-based cryptography (HSMs, smart cards) is inherently less agile than software-based cryptography. How should organizations balance the security benefits of hardware with the agility benefits of software?
3. An organization discovers that a critical legacy application hardcodes RSA-1024 and cannot be modified (the vendor is out of business). What options exist for protecting this application in a post-quantum world?

---

ᚨ **Lecture 4: Certificate Migration — The Longest Pole in the Tent**

**Course:** IT307 — Quantum-Safe Cryptography Migration
**Degree:** Bachelor of Science in Information Technology, 2040

---

### Overview

Public Key Infrastructure (PKI) is the backbone of digital trust — and it is built entirely on algorithms that quantum computers will break. Every X.509 certificate, every certificate authority, every certificate revocation list, every OCSP responder — all must be migrated to post-quantum algorithms. This lecture covers the PKI migration challenge: hybrid certificates, cross-signed transitions, root CA migration, and the operational complexity of replacing every certificate in the enterprise before the CRQC arrives.

### Lecture Notes

The scale of the PKI migration is staggering. The global PKI encompasses billions of certificates: web server certificates (TLS), client certificates, code signing certificates, email certificates (S/MIME), document signing certificates, IoT device certificates, VPN certificates, and internal enterprise certificates for service-to-service authentication. Every single one uses RSA or ECC. Every single one must be replaced.

The challenge is not just the number of certificates but the dependency chains. A web server's TLS certificate is signed by an intermediate CA, which is signed by a root CA. The root CA's certificate is embedded in every browser and operating system trust store. Migrating the web server's certificate to Dilithium is useless if the intermediate and root CAs still use RSA — the entire chain must be migrated.

The **hybrid certificate** approach — standardized in the ITU X.509 PQC extensions — addresses this transition. A hybrid certificate contains both a classical signature (RSA or ECDSA) and a post-quantum signature (Dilithium or FALCON), both over the same certificate data. A PQC-aware client validates both signatures; a legacy client validates only the classical signature and ignores the PQC signature. This enables gradual migration: servers can deploy hybrid certificates before all clients are PQC-capable, and clients can be upgraded incrementally.

The **root CA migration** is the most complex element. Root CAs have lifetimes of 20–30 years. A root CA created in 2020 with an RSA-4096 key, expiring in 2040, cannot simply have its algorithm changed — the root key is the root of trust. The migration strategy involves creating new PQC root CAs, having them cross-signed by the existing classical roots (so that old clients trust the new roots), and then transitioning the existing roots to Legacy status. This process takes years and must be coordinated across the entire PKI ecosystem — every browser vendor, every OS vendor, every CA.

The **certificate size** problem is severe. A Dilithium-3 signature is 3293 bytes. A hybrid certificate with both RSA-2048 and Dilithium-3 signatures adds ~3.5KB to every certificate. In a typical TLS handshake, the server sends its certificate chain (typically 2–4 certificates). With hybrid certificates, the certificate chain alone can exceed 15KB — larger than many entire TLS handshakes in the classical era. This increases handshake latency, consumes more bandwidth, and causes fragmentation at the TCP and IP layers. Protocol optimizations — certificate compression (RFC 8879), cached certificate chains, and the "TLS Cached Info" extension — become essential.

By 2040, the migration is well underway but far from complete. Major CAs (DigiCert, Let's Encrypt, GlobalSign) offer PQC certificates. Major browsers (Chrome, Firefox, Safari) support PQC certificate validation. But the "long tail" of PKI — internal enterprise CAs, IoT device certificates, legacy system certificates — remains the hardest part. Many organizations discover that they have CAs they didn't know existed, certificates that auto-renew without oversight, and embedded certificates in devices that cannot be updated.

### Required Reading

- ITU-T X.509: "Information Technology — Open Systems Interconnection — The Directory: Public-Key and Attribute Certificate Frameworks." (PQC extensions, 2028 update.)
- Barnes, R., et al. (2020). "Automatic Certificate Management Environment (ACME)." RFC 8555. (PQC extensions in progress.)
- CA/Browser Forum. (2030). "Baseline Requirements for Post-Quantum TLS Certificates."
- Véfreyjasdóttir, B. (2039). "The Long Tail of PKI: Discovering and Migrating Forgotten Certificates." *IEEE Security & Privacy*, 17(3), 45–58.

### Discussion Questions

1. Some IoT devices have certificates burned into firmware at manufacture and can never be updated. What is the secure retirement strategy for these devices in a post-quantum world?
2. Hybrid certificates double the validation work for every TLS handshake. For high-traffic web servers, how do you balance the security of hybrid validation with the performance impact?
3. The CA/Browser Forum governs PKI standards globally. Is this governance model sufficient for a migration of this scale, or does PQC migration require government mandates?

---

ᚱ **Lecture 5: Protocol Migration — TLS, SSH, IPsec, and Beyond**

**Course:** IT307 — Quantum-Safe Cryptography Migration
**Degree:** Bachelor of Science in Information Technology, 2040

---

### Overview

Cryptographic algorithms are embedded in protocols, and protocols embed assumptions about algorithm characteristics — key sizes, signature sizes, message formats — that post-quantum algorithms violate. This lecture surveys the protocol migration landscape: TLS 1.3 PQC extensions, SSH PQC key exchange, IPsec/IKEv2 PQC, DNSSEC PQC, and the application-layer protocols (S/MIME, PGP, Signal) that each require their own migration path. The emphasis is on the practical engineering challenges of deploying PQC-enabled protocols in production environments.

### Lecture Notes

Every secure protocol must be updated for PQC. The IETF has been working on this since the early 2020s, but progress varies by protocol:

**TLS 1.3** is the most advanced. The TLS Working Group defined PQC extensions that add new named groups for Kyber key exchange (e.g., "MLKEM768") and new signature algorithms for Dilithium and FALCON (e.g., "MLDSA65"). TLS 1.3's handshake already supports algorithm negotiation, so adding PQC is "mostly" a matter of defining the new identifiers and ensuring the larger messages don't break implementations. The primary challenge is the increased handshake size: a PQC TLS handshake with hybrid key exchange and hybrid certificates can exceed 20KB, compared to ~5KB for a classical handshake. This impacts performance, especially on high-latency connections. The 2040 optimizations include: QUIC (which integrates TLS and reduces round trips), ECH (Encrypted Client Hello, for privacy), and certificate compression.

**SSH** (Secure Shell) uses its own key exchange and authentication protocols. The SSH protocol (RFC 4251–4254) was designed for extensibility, and PQC key exchange methods (e.g., "sntrup761x25519-sha512@openssh.com") have been deployed by OpenSSH since 2022 as hybrid schemes combining Streamlined NTRU Prime with X25519. Full PQC migration for SSH requires not just PQC key exchange but PQC host keys and user authentication keys — a more complex migration because SSH keys are often manually managed and distributed.

**IPsec/IKEv2** (Internet Key Exchange version 2) is the VPN workhorse. IKEv2 negotiates cryptographic algorithms for IPsec tunnels. Adding PQC to IKEv2 requires defining new transform types for PQC key exchange and authentication, and ensuring that the larger IKE messages (which can exceed the UDP MTU and require fragmentation) are handled correctly. IPsec PQC migration is critical for site-to-site VPNs that protect traffic between data centers and cloud environments.

**DNSSEC** (DNS Security Extensions) signs DNS records with RSA or ECDSA. Migrating DNSSEC to PQC requires: new DNSKEY algorithm numbers, updated resolver logic to validate PQC signatures, and — the hardest part — handling the increased response sizes. A DNSSEC-signed response with Dilithium signatures can exceed the 512-byte UDP DNS message size limit, forcing fallback to TCP, which is slower and sometimes blocked by firewalls. This is the "DNSSEC size problem" and it has been a significant barrier to PQC adoption in the DNS.

**Email Security** (S/MIME, PGP) faces its own challenges. S/MIME certificates are X.509 certificates that must be migrated (covered in Lecture 4). PGP keys are self-managed and not part of a PKI; migrating PGP to PQC requires new key formats, new algorithm identifiers, and coordination across the entire PGP ecosystem. The decentralized nature of PGP makes coordinated migration particularly difficult.

**Messaging Protocols** (Signal, WhatsApp, Matrix) use the Double Ratchet Algorithm and other forward-secrecy mechanisms. These protocols typically use ECDH for key agreement, and migrating to PQC requires integrating Kyber or other PQC KEMs into the ratchet — which increases message sizes and may impact the real-time performance that messaging requires. The Signal Protocol added PQC support (PQXDH — Post-Quantum Extended Diffie-Hellman) in 2023, making it one of the earliest adopters at the application layer.

### Required Reading

- IETF TLS Working Group. (2025). "Post-Quantum TLS 1.3." RFC Series.
- OpenSSH. (2022). "Post-Quantum SSH Key Exchange." OpenSSH 9.0 Release Notes.
- Signal Foundation. (2023). "The PQXDH Key Agreement Protocol." Signal Technical Documentation.
- Véfreyjasdóttir, B., & Chen, L. (2040). "Post-Quantum DNSSEC: Overcoming the Size Barrier." *Proceedings of the 2040 ACM SIGCOMM Conference*.

### Discussion Questions

1. QUIC integrates TLS and reduces handshake round-trips, which helps offset PQC size increases. Is QUIC the natural transport for PQC-secured communications, or are there use cases where TCP+TLS remains preferable?
2. PGP's decentralized trust model makes coordinated migration difficult. Is this a flaw in PGP's design, or a feature that forces us to think differently about migration?
3. Some legacy protocols (FTP, Telnet, SNMPv1) will likely never be migrated to PQC. What is the secure retirement strategy for these protocols?

---

ᚲ **Lecture 6: Hardware and Embedded Systems — When You Can't Just Update Software**

**Course:** IT307 — Quantum-Safe Cryptography Migration
**Degree:** Bachelor of Science in Information Technology, 2040

---

### Overview

Not all cryptographic migration can be accomplished through software updates. Hardware Security Modules (HSMs), smart cards, IoT devices, automotive systems, and industrial controllers often have cryptographic algorithms burned into silicon — and that silicon has a 10–20 year operational lifetime. This lecture addresses the hardest cases of PQC migration: systems where cryptographic algorithms are physically immutable, where a software update is impossible, and where the only option may be physical replacement — on a timeline that precedes the CRQC.

### Lecture Notes

Hardware-based cryptography presents a fundamental tension: hardware offers superior security (tamper-resistant key storage, side-channel resistance, physical isolation) but inferior agility (algorithms are embedded in ASICs or firmware that cannot be updated). The PQC migration exposes this tension at scale.

**Hardware Security Modules (HSMs)** are the most critical hardware cryptography devices. HSMs protect root CA keys, payment processing keys, and other high-value cryptographic material. An HSM deployed in 2025, with a 15-year operational lifetime, will still be in service in 2040 — potentially within the CRQC window. But HSMs certified to FIPS 140-2 or 140-3 cannot simply have their algorithms changed — the certification is for a specific hardware/firmware combination. PQC-capable HSMs require new hardware designs, new firmware, and new FIPS certifications. The HSM industry (Thales, Gemalto, Entrust, Utimaco) has been shipping PQC-capable HSMs since the early 2030s, but the installed base of legacy HSMs remains substantial.

**Smart Cards and Secure Elements** — including EMV payment cards, national ID cards, and mobile SIMs — have even longer replacement cycles. A national ID card issued in 2030 might be valid until 2045. If that card uses RSA-2048 for authentication, and a CRQC arrives in 2040, every card must be physically replaced — a logistical operation involving millions of citizens. Governments and payment networks (EMVCo) have been planning for this migration since the 2020s, but execution is inherently slow.

**IoT and Embedded Devices** represent the largest volume and the hardest migration challenge. A smart meter deployed in 2020, with a 20-year lifetime, uses TLS for communication with the utility's backend. The meter's TLS implementation is in firmware; there is no update mechanism (or the update mechanism itself relies on the cryptography being replaced). When a CRQC arrives, these meters become vulnerable — an attacker could impersonate the utility's backend and send malicious commands to millions of meters. The only solutions are physical replacement (prohibitively expensive) or wrapping the meter in a PQC-capable gateway that terminates the insecure connection and forwards traffic securely — a "cryptographic proxy" pattern that centralizes the migration burden.

**Automotive and Industrial Systems** have operational lifetimes of 10–30 years. A car manufactured in 2030, with V2X (vehicle-to-everything) communication secured by ECDSA, will still be on the road in 2045. The automotive industry has addressed this through: (1) designing update capabilities into vehicle platforms, (2) planning for PQC migration in the 2035–2040 model years, and (3) accepting that pre-2035 vehicles may need aftermarket cryptographic upgrades or operating restrictions in a post-quantum world.

The **cryptographic proxy** pattern deserves emphasis. When an embedded device cannot be updated, a PQC-capable gateway can be placed in front of it. The gateway terminates the insecure connection using PQC algorithms, and communicates with the legacy device over a physically secured, isolated network segment where the classical cryptography is acceptable. This pattern does not eliminate the vulnerability — an attacker with physical access to the isolated segment could still exploit it — but it dramatically reduces the attack surface. For many IoT and embedded use cases, the cryptographic proxy is the only practical migration strategy.

### Required Reading

- NIST SP 800-210: "General Access Control Guidance for Cloud Systems" — Section on Cryptographic Boundaries.
- FIPS 140-3: "Security Requirements for Cryptographic Modules." (PQC revision in progress.)
- EMVCo. (2030). "Post-Quantum Cryptography Migration for Payment Systems." Technical Framework.
- Véfreyjasdóttir, B., & Olafsdóttir, S. (2040). "The Cryptographic Proxy Pattern: Securing Legacy Embedded Systems in the Post-Quantum Era." *IEEE Internet of Things Journal*, 7(2), 1234–1248.

### Discussion Questions

1. A smart meter with a 20-year lifetime and no update mechanism was deployed in 2020. In 2040, it is cryptographically obsolete but physically functional. Who should bear the cost of replacement — the manufacturer, the utility, or the ratepayer?
2. The cryptographic proxy pattern reduces but does not eliminate risk. Under what circumstances is the residual risk acceptable, and under what circumstances is physical replacement the only option?
3. Automotive safety systems (brake-by-wire, steering-by-wire) rely on cryptography for authenticity. If these systems cannot be updated to PQC, should vehicles be taken off the road when a CRQC arrives?

---

ᚷ **Lecture 7: The Organizational Migration — People, Process, and Governance**

**Course:** IT307 — Quantum-Safe Cryptography Migration
**Degree:** Bachelor of Science in Information Technology, 2040

---

### Overview**

The PQC migration is not primarily a technical problem — it is an organizational one. The technology exists. The algorithms are standardized. The protocols are updated. What remains is the human challenge of coordinating a migration that spans every system, every team, every vendor, and every business unit in the enterprise — on a deadline that approaches relentlessly. This lecture covers the organizational dimensions: executive sponsorship, cross-functional governance, vendor management, migration prioritization, and the communication strategies that keep a multi-year migration program on track.

### Lecture Notes

The PQC migration program has several characteristics that make it uniquely challenging to manage:

**Universal Scope**: Every system that uses cryptography is in scope. This includes not just the obvious (web servers, VPNs, databases) but also the obscure: building access control systems, digital signage, laboratory instruments, HVAC controllers, elevator management systems. The cryptographic inventory (Lecture 3) reveals the full scope, and it is always larger than anyone expected.

**No Immediate Benefit**: Unlike most IT projects, PQC migration delivers no visible improvement to users. Applications don't get faster. Interfaces don't get better. Features aren't added. The benefit is purely negative — preventing a future catastrophe. Convincing business stakeholders to invest significant resources in a project with no positive ROI — only avoided negative ROI — requires exceptional communication skills.

**Hard Deadline with Uncertainty**: The CRQC timeline is uncertain (5–15 years), but the deadline is real and immovable. Unlike a software project where a deadline can slip without existential consequences, slipping the PQC migration deadline means the organization's cryptography is broken. Everything encrypted is exposed. Every signature is forgeable. Every authenticated connection is interceptable. The consequences are total.

The **migration governance structure** recommended by NIST and adopted by leading organizations includes:

**Executive Sponsor**: A C-suite leader (CTO, CISO, or Chief Risk Officer) who has the authority to allocate resources across business units and the credibility to communicate the urgency to the board. Without executive sponsorship, PQC migration becomes a "security team project" that other teams deprioritize.

**Migration Program Office**: A dedicated team responsible for planning, tracking, and reporting migration progress. This is not a part-time assignment. For a large enterprise, the PMO may have 5–15 full-time staff.

**System Owner Accountability**: Every system owner is responsible for migrating their systems. The PMO provides tools, guidance, and tracking; the system owners do the work. This distributed model is the only way to scale migration across thousands of systems.

**Vendor Engagement Program**: Most organizations depend on vendors for cryptographic software and hardware. The vendor engagement program tracks each vendor's PQC roadmap, sets contractual expectations for PQC support, and identifies vendors that are not on track — enabling contingency planning before it's too late.

The **migration prioritization framework** answers "where do we start?" The recommended ordering:

1. **Highest-value keys**: Root CAs, code signing keys, and other long-lived, high-impact keys — these have the longest sensitivity lifetime and the most catastrophic compromise consequences.
2. **Long-lived secrets**: Data with sensitivity lifetimes extending beyond the CRQC window — medical records, financial data, classified information. Encryption must be upgraded before the data is harvested.
3. **Externally facing systems**: Systems accessible from the internet — these face the highest HNDL risk (traffic can be passively intercepted) and must be migrated before internally-facing systems.
4. **Internally facing systems**: Internal applications, databases, and service-to-service communication — lower HNDL risk but still must be migrated.
5. **Non-critical and short-lived systems**: Systems where data sensitivity expires before the CRQC window — these can be migrated last or, in some cases, retired instead of migrated.

The **communication strategy** must address multiple audiences:

- **Board of Directors**: "This is an existential risk. The cost of migration is X. The cost of not migrating is total cryptographic compromise. We must start now."
- **Business Unit Leaders**: "Your systems are in scope. The migration will require resources from your teams. Here is the timeline. Here is the support we provide."
- **IT Staff**: "This is the most important infrastructure project of your careers. Here is the training. Here are the tools. Here is why it matters."
- **End Users**: "Over the next two years, you may experience brief service interruptions during migration windows. Here is what's happening and why it's necessary."

The organizations that succeed in PQC migration will be those that treat it not as a technical project but as an organizational transformation — led from the top, resourced adequately, tracked rigorously, and communicated relentlessly.

### Required Reading

- NIST. (2024). "Migration to Post-Quantum Cryptography: Project Management and Governance." NIST Special Publication 1800-37.
- NSA. (2022). "CNSA 2.0 Algorithm Suite: Frequently Asked Questions." National Security Agency.
- FS-ISAC. (2030). "Post-Quantum Cryptography Migration: A Guide for Financial Institutions."
- Véfreyjasdóttir, B. (2040). "Leading the Unseen Migration: Organizational Strategies for PQC Transformation." *Harvard Business Review* (2040 Technology Special Issue).

### Discussion Questions

1. How do you convince a CFO to allocate $10 million to a project whose only benefit is "preventing something bad that might happen in 5–15 years"?
2. System owners are accountable for migration, but they have other priorities. What incentives and consequences should the governance structure include to ensure compliance?
3. A critical vendor has no PQC roadmap and shows no signs of developing one. What are your options, and in what order should you pursue them?

---

ᚹ **Lecture 8: PQC in the Cloud — Shared Responsibility for Quantum Safety**

**Course:** IT307 — Quantum-Safe Cryptography Migration
**Degree:** Bachelor of Science in Information Technology, 2040

---

### Overview

Cloud computing does not exempt organizations from PQC migration — it changes who does the work. This lecture examines the shared responsibility model for PQC: what cloud providers handle (their own infrastructure, their TLS endpoints, their KMS services), what customers must handle (their applications, their data encryption, their certificate management), and what falls into the gray area of "it depends" (managed services that use cryptography internally). Students learn how to assess cloud providers' PQC readiness, how to configure cloud services for PQC, and how to plan a hybrid cloud/on-premises PQC migration.

### Lecture Notes

The cloud providers (AWS, Azure, GCP) have been preparing for PQC since the early 2020s. Their scale — millions of servers, billions of TLS connections per day — means they have both the most to lose from cryptographic compromise and the most resources to invest in migration. But their migration does not automatically make their customers quantum-safe.

The **cloud shared responsibility model for PQC** extends the familiar security model:

**Provider Responsibility**: The cloud provider is responsible for the cryptography in the infrastructure they control — the TLS endpoints for their APIs, the encryption of data at rest in their managed storage services (S3, Azure Blob, GCS), the key management in their KMS services, the certificate management for their managed services, and the internal service-to-service communication within their data centers. By 2040, all major cloud providers have completed or are nearing completion of their infrastructure PQC migration.

**Customer Responsibility**: The customer is responsible for the cryptography in everything they deploy in the cloud — their applications' TLS configuration, their application-level encryption (if they encrypt data before sending it to cloud storage), their own certificates, their own key management if they use external KMS or bring-your-own-key (BYOK), and their network-level encryption (VPNs, IPsec tunnels to the cloud). The customer is also responsible for migrating their on-premises systems that communicate with cloud services.

**Gray Areas**: Managed services (AWS RDS, Azure SQL Database, GCP Cloud SQL) use cryptography internally for replication, backups, and management operations. The provider handles most of this, but the customer may need to configure PQC options. Database connection encryption (TLS from the application to the managed database) is typically the customer's responsibility to configure with PQC cipher suites. The precise boundary varies by service and provider.

**Cloud KMS and PQC**: Cloud Key Management Services (AWS KMS, Azure Key Vault, Google Cloud KMS) are the most critical services for PQC because they protect the keys that protect everything else. By 2040, cloud KMS services support: creation of PQC keys (Kyber, Dilithium), hybrid key operations (wrapping data keys with both classical and PQC key encryption keys), and integration with external PQC HSMs for customers who require hardware-based key protection. The customer's responsibility is to: create PQC keys, migrate existing keys (re-wrap data keys with PQC key encryption keys), and update applications to request PQC key types.

**Certificate Management in the Cloud**: AWS Certificate Manager (ACM), Azure Key Vault certificates, and similar services handle certificate provisioning and renewal. By 2040, these services support PQC certificates (hybrid and PQC-only), but the customer must request PQC certificate types — the default may still be classical for backward compatibility. Customers must explicitly configure their load balancers, API gateways, and CDN endpoints to use PQC certificates.

The **multi-cloud PQC challenge**: Organizations that use multiple cloud providers must manage PQC migration across providers with different timelines, different API semantics, and different maturity levels. The abstraction layer — Infrastructure as Code (Terraform, Pulumi), policy-as-code (OPA), and cloud management platforms — becomes essential for maintaining consistency.

### Required Reading

- AWS. (2035). "Post-Quantum Cryptography in AWS: Customer Migration Guide." AWS Whitepaper.
- Azure. (2035). "Quantum-Safe Cryptography for Azure Services." Microsoft Documentation.
- Cloud Security Alliance. (2030). "Post-Quantum Cryptography in the Cloud: Guidance for Customers."
- Véfreyjasdóttir, B. (2040). "Multi-Cloud PQC: Managing Cryptographic Migration Across Heterogeneous Cloud Environments." *IEEE Cloud Computing*, 8(4), 78–92.

### Discussion Questions

1. Cloud providers claim their infrastructure is PQC-migrated, but customers have no way to verify this independently. What level of assurance (audit report, technical demonstration, contractual warranty) should customers require?
2. BYOK (Bring Your Own Key) gives customers control over their key material but also makes them responsible for PQC migration of those keys. For which use cases is BYOK worth this additional responsibility?
3. A cloud provider offers PQC as a premium feature with higher cost. Is it ethical to charge extra for quantum safety, or should PQC be included in baseline security?

---

ᚺ **Lecture 9: The Long Tail of Cryptography — Finding Every Last Algorithm**

**Course:** IT307 — Quantum-Safe Cryptography Migration
**Degree:** Bachelor of Science in Information Technology, 2040

---

### Overview

The hardest part of PQC migration is finding everything that needs to be migrated. Cryptography is embedded in places that no one thinks about: build systems, backup software, license managers, database replication, log shipping, monitoring agents, and configuration management tools. This lecture is a practical field guide to discovering the "long tail" of cryptography — the obscure, embedded, and forgotten uses of cryptography that can derail an otherwise successful migration.

### Lecture Notes

Every organization that has conducted a cryptographic inventory has discovered uses of cryptography they didn't know existed. The pattern is so consistent that it has a name: **cryptographic surprise**. Common sources of cryptographic surprise include:

- **Build and CI/CD Systems**: Package signing, artifact verification, and deployment authentication all use cryptography. Jenkins, GitHub Actions, GitLab CI — each has its own certificate store, its own SSH keys, its own TLS configuration. A build pipeline that signs artifacts with RSA-2048 will produce forgeable artifacts after a CRQC arrives.

- **Backup and DR Systems**: Backup software encrypts data in transit (TLS) and at rest (AES with RSA-wrapped keys). The backup catalog database uses TLS. The replication channel to the DR site uses TLS or IPsec. All must be migrated — and because backups have long retention periods, HNDL is a real threat. A backup from 2040, encrypted with RSA, may be decryptable in 2045.

- **Database Replication**: Database replication channels (PostgreSQL streaming replication, MySQL Group Replication, SQL Server Always On) use TLS for inter-node communication. If the TLS is not upgraded to PQC, an attacker who can intercept replication traffic (which contains all data changes) can harvest it for future decryption.

- **License Managers**: Enterprise software license servers (FlexNet, Reprise, custom solutions) often use RSA for license file signing. If the license signing key is compromised, anyone can generate valid licenses for expensive software.

- **Monitoring and Observability**: Prometheus, Grafana, Elasticsearch, Datadog — all use TLS for agent-to-server and server-to-server communication. Monitoring data (metrics, logs, traces) may contain sensitive information harvestable for HNDL.

- **Configuration Management**: Ansible, Puppet, Chef, Salt — these tools push configuration to servers over SSH or TLS. If an attacker can intercept configuration pushes, they can inject malicious configuration.

Discovery techniques for the long tail:

**Network Traffic Analysis**: Monitor traffic and identify connections that use TLS but haven't been identified in the cryptographic inventory. Tools like Zeek (formerly Bro) and cloud flow logs can identify TLS connections and their cipher suites, revealing unknown cryptographic usage.

**Code Analysis**: Static analysis tools can scan source code for cryptographic API calls (Java JCA, Python cryptography library, OpenSSL calls in C/C++). This catches embedded cryptography that doesn't produce network traffic — file encryption, local key generation, certificate validation.

**Certificate Transparency Log Monitoring**: Monitor Certificate Transparency (CT) logs for certificates issued to your organization's domains. This catches certificates provisioned by teams outside the central IT organization — "shadow IT" certificates.

**Configuration Scanning**: Scan server configurations for TLS settings, SSH configurations, and application configurations that reference cryptographic material. Tools like OpenSCAP, Chef InSpec, and cloud security posture management (CSPM) platforms can automate this.

The **cryptographic surprise response process**: When a previously unknown cryptographic usage is discovered, the response is: (1) Document it in the inventory (don't skip — if it was unknown once, it could become unknown again). (2) Assess the risk — what is protected, what is the sensitivity lifetime, what is the exposure? (3) Prioritize — where does this system fall in the migration prioritization framework? (4) Migrate or retire — can the system be migrated, or should it be retired? (5) Update discovery processes to catch similar systems in the future.

### Required Reading

- NIST. (2024). "Cryptographic Inventory Guidance." Included in SP 1800-37.
- Cloud Security Alliance. (2030). "Cryptographic Inventory for Cloud-Native Enterprises."
- Véfreyjasdóttir, B. (2039). "Cryptographic Surprise: Findings from 50 Enterprise Cryptographic Inventories." *Proceedings of the 2039 RSA Conference*.

### Discussion Questions

1. Cryptographic surprise is inevitable. Should organizations budget contingency resources for "unknown cryptography," and if so, what percentage of the total migration budget?
2. Some long-tail cryptography is so obscure that no one knows how to update it (abandoned internal tools, legacy vendor products). What is the risk acceptance process for systems that genuinely cannot be migrated?
3. The discovery techniques described (network analysis, code scanning, CT log monitoring) require significant tooling and expertise. For a mid-sized enterprise without a dedicated crypto team, what is the minimum viable discovery program?

---

ᚾ **Lecture 10: Performance and Optimization — Making PQC Practical**

**Course:** IT307 — Quantum-Safe Cryptography Migration
**Degree:** Bachelor of Science in Information Technology, 2040

---

### Overview**

Post-quantum algorithms are larger and slower than their classical counterparts. Kyber key exchange adds kilobytes to every TLS handshake. Dilithium signatures are 10x larger than Ed25519. For high-throughput systems, these overheads are not negligible — they affect latency, throughput, bandwidth costs, and user experience. This lecture examines the performance characteristics of PQC algorithms, optimization techniques (hardware acceleration, batching, caching), and the architectural patterns that mitigate PQC overhead in production environments.

### Lecture Notes

PQC performance must be evaluated holistically — not just algorithm speed but the system-level impact of larger keys, larger signatures, and larger handshake messages:

**Latency Impact**: A PQC TLS handshake with Kyber-768 + Dilithium-3 hybrid certificates adds approximately 10–15KB of additional data compared to a classical ECDH + Ed25519 handshake. On a 100Mbps connection, this adds roughly 1ms of transmission time — negligible. But on a high-latency satellite link (600ms RTT) or a constrained mobile connection, the additional round-trips caused by larger messages (TCP congestion window effects, IP fragmentation) can add hundreds of milliseconds. For latency-sensitive applications (online gaming, video conferencing, financial trading), PQC overhead must be carefully managed.

**Throughput Impact**: PQC algorithms are computationally more expensive than classical algorithms. Kyber key generation, encapsulation, and decapsulation are actually quite fast — comparable to or faster than ECDH in many implementations. But Dilithium signing is 2–5x slower than Ed25519 signing. For a TLS terminating proxy (load balancer, API gateway) that performs thousands of handshakes per second, the additional CPU cost of PQC can be significant. Hardware acceleration — using CPU vector instructions (AVX2, AVX-512, NEON) — can reduce but not eliminate the overhead.

**Bandwidth Costs**: Cloud providers charge for data transfer. A PQC TLS handshake that is 15KB larger, performed millions of times per day, adds up to real money. For a large web property serving billions of requests per day, the bandwidth cost of PQC can be substantial. Optimization techniques — TLS session resumption (which avoids full handshakes), certificate compression, and QUIC 0-RTT — become essential.

**Optimization Techniques**:

**TLS Session Resumption**: After the initial full PQC handshake, subsequent connections can use abbreviated handshakes (session tickets or session IDs) that avoid repeating the expensive asymmetric operations. This is a critical optimization — the first connection to a server is expensive, but subsequent connections are cheap.

**Certificate Compression**: RFC 8879 defines TLS certificate compression, which can reduce certificate chain sizes by 50–70%. For PQC certificates, which are several times larger than classical certificates, compression is essential.

**Key Caching**: Servers can cache the results of key generation operations, avoiding the cost of generating new ephemeral keys for every handshake (with appropriate rotation to maintain forward secrecy).

**Connection Pooling and Multiplexing**: HTTP/2, HTTP/3 (QUIC), and gRPC allow multiple requests to share a single TLS connection, amortizing the PQC handshake cost across many requests. Architectures that use connection pooling heavily reduce the per-request PQC overhead.

**Edge Computing**: Performing PQC termination at edge locations (CDN nodes, cloud edge zones) reduces latency for end users and centralizes the PQC processing burden. The edge node handles the PQC handshake; the connection from edge to origin can use classical cryptography (if on a trusted network) or PQC (if not).

By 2040, the performance gap has narrowed significantly. Hardware vendors (Intel, AMD, ARM) have added PQC acceleration instructions. Cloud providers have optimized their TLS termination infrastructure for PQC at scale. And the protocol optimizations (TLS 1.3 PQC with session resumption, QUIC, certificate compression) have reduced the practical overhead to manageable levels for most use cases. The remaining challenges are in constrained environments: IoT, embedded systems, and satellite communications.

### Required Reading

- Paquin, C., Stebila, D., & Tamvada, G. (2020). "Benchmarking Post-Quantum Cryptography in TLS." *Proceedings of the 2020 ACM SIGSAC Conference*.
- AWS. (2035). "Optimizing TLS for Post-Quantum Cryptography: Performance Best Practices." AWS Whitepaper.
- Cloudflare. (2035). "PQC at the Edge: Performance Data from Global Deployment." Cloudflare Blog.
- Véfreyjasdóttir, B. (2040). "Hardware Acceleration of Post-Quantum Cryptography: A Survey of CPU, GPU, and FPGA Implementations." *ACM Computing Surveys*, 53(2), 1–34.

### Discussion Questions

1. TLS session resumption dramatically reduces PQC overhead but weakens forward secrecy (if session ticket keys are compromised, past sessions can be decrypted). How should organizations balance performance and security in their TLS configuration?
2. IoT devices with 32KB of RAM may not be able to perform PQC operations at all. Is "PQC proxy" (a gateway that handles PQC on behalf of the device) the only viable architecture?
3. Hardware acceleration of PQC is becoming standard. What is the fallback for systems that don't have PQC-accelerated hardware — is software-only PQC acceptable performance-wise?

---

ᛁ **Lecture 11: The Regulatory and Standards Landscape — Compliance and the Quantum Mandate**

**Course:** IT307 — Quantum-Safe Cryptography Migration
**Degree:** Bachelor of Science in Information Technology, 2040

---

### Overview

Governments and regulators are not waiting for organizations to voluntarily migrate to PQC. National security agencies, financial regulators, and data protection authorities have issued mandates, timelines, and compliance requirements. This lecture surveys the global regulatory landscape for PQC migration: the U.S. NSM-10 and CNSA 2.0, the EU's PQC transition framework, sector-specific requirements (financial services, healthcare, defense), and the compliance frameworks that translate regulatory requirements into auditable controls.

### Lecture Notes

The regulatory driver for PQC migration began with national security. In 2022, the U.S. National Security Agency (NSA) released the Commercial National Security Algorithm Suite 2.0 (CNSA 2.0), which set a timeline: all National Security Systems (NSS) must use PQC algorithms by 2035. While CNSA 2.0 directly applies only to government systems, its influence extends across the entire technology industry — vendors who want to sell to the government must support PQC, and the algorithms NSA selects effectively become the global standard.

The 2022 **National Security Memorandum 10 (NSM-10)** , signed by the U.S. President, directed all federal agencies to inventory their cryptographic systems, plan for PQC migration, and complete migration by 2035. This was followed by the **Quantum Computing Cybersecurity Preparedness Act** (2023), which codified the migration requirement into law. By 2040, the federal migration is largely complete for major systems, with the long tail of legacy systems still in progress.

The **European Union** has taken a parallel approach. The EU Agency for Cybersecurity (ENISA) published PQC migration guidance in 2023, and the updated NIS2 Directive (2023) requires operators of essential services to "address the risks posed by quantum computing to cryptographic systems." The EU's approach emphasizes a coordinated, pan-European migration with shared timelines and mutual recognition of PQC certifications.

**Sector-specific regulations** have driven adoption in critical industries:

- **Financial Services**: The U.S. Federal Financial Institutions Examination Council (FFIEC) and the European Banking Authority (EBA) require financial institutions to have PQC migration plans, conduct cryptographic inventories, and report progress. The Basel Committee on Banking Supervision added PQC readiness to its operational risk framework. By 2040, all major banks have active PQC migration programs, and regulators are auditing progress.

- **Healthcare**: HIPAA (U.S.) and GDPR (EU) require protection of personal health information. While neither explicitly mentions quantum computing, the general requirement for "appropriate technical and organizational measures" is interpreted by regulators to include PQC for data with long sensitivity lifetimes. Medical records have lifetime sensitivity — a patient's genome, once harvested and decrypted, cannot be re-protected.

- **Defense and Critical Infrastructure**: PQC migration is mandatory for defense contractors and critical infrastructure operators under national security directives. Compliance is enforced through procurement requirements — you cannot bid on government contracts without a PQC migration plan.

**Compliance Frameworks** have emerged to operationalize regulatory requirements. The NIST Cybersecurity Framework (CSF) 2.0 added a "Quantum-Safe Cryptography" subcategory. SOC 2 and ISO 27001 audits increasingly include PQC readiness as an evaluation criterion. By 2040, a SOC 2 report that does not address PQC migration is considered incomplete.

The **regulatory trend** is clear: PQC migration is transitioning from "forward-thinking best practice" to "regulatory requirement." Organizations that began their migration early are well-positioned. Organizations that are just starting now face compressed timelines, vendor capacity constraints, and regulatory scrutiny. The window for voluntary migration is closing.

### Required Reading

- NSM-10: "Promoting United States Leadership in Quantum Computing While Mitigating Risks to Vulnerable Cryptographic Systems" (2022).
- NSA. (2022). "Announcing the Commercial National Security Algorithm Suite 2.0."
- ENISA. (2023). "Post-Quantum Cryptography: Integration Study." European Union Agency for Cybersecurity.
- FFIEC. (2035). "Post-Quantum Cryptography Migration: Regulatory Expectations for Financial Institutions."

### Discussion Questions

1. Government mandates require PQC migration by 2035. But small businesses have fewer resources and less cryptographic expertise. Should small businesses be exempt, given a longer timeline, or subject to the same requirements?
2. Regulatory compliance can drive migration — but it can also drive checkbox compliance that doesn't actually improve security. How should regulations be designed to incentivize genuine quantum safety?
3. Different jurisdictions (U.S., EU, China) may standardize different PQC algorithms. How should a global organization handle algorithm selection in a fragmented regulatory environment?

---

ᛃ **Lecture 12: Beyond PQC — The Cryptographic Horizon**

**Course:** IT307 — Quantum-Safe Cryptography Migration
**Degree:** Bachelor of Science in Information Technology, 2040

---

### Overview

Post-quantum cryptography solves the immediate threat of cryptographically relevant quantum computers. But the arc of cryptographic history bends toward constant renewal. This final lecture looks beyond PQC to the cryptographic challenges of the next 30 years: quantum key distribution (QKD) as a complement to PQC, the possibility of new mathematical attacks on lattice-based cryptography, the implications of AI for cryptanalysis, and the ultimate vision of cryptography that is secure against any physically feasible adversary — including adversaries with technologies we haven't imagined yet.

### Lecture Notes

PQC is a response to a specific threat (Shor's algorithm on CRQCs) using specific mathematical foundations (lattice problems, hash functions, multivariate equations). But the history of cryptography teaches humility. Every generation's "unbreakable" cipher has eventually been broken — not always through advances in computing, but through advances in mathematics. The lattice problems that underlie Kyber and Dilithium (Learning With Errors, Short Integer Solution) have resisted cryptanalysis for two decades, but there is no proof that they are hard. A mathematical breakthrough — a classical algorithm for lattice problems — would break PQC without requiring a quantum computer at all.

**Quantum Key Distribution (QKD)** offers a fundamentally different approach: security based on the laws of physics rather than mathematical hardness assumptions. QKD uses quantum mechanical properties (the no-cloning theorem, the observer effect) to distribute encryption keys with a provable guarantee that any eavesdropping will be detected. QKD has been demonstrated over hundreds of kilometers of fiber and via satellite, and commercial QKD networks exist. But QKD has significant practical limitations: it requires specialized hardware (single-photon sources and detectors), it cannot authenticate endpoints without classical cryptography, and it is point-to-point (not suitable for the internet's packet-switched architecture). By 2040, the consensus view is that QKD complements PQC rather than replacing it — QKD for niche high-assurance links (inter-data center, government communications), PQC for the broad internet.

**AI and Cryptanalysis**: Machine learning has transformed many fields. Could it transform cryptanalysis? By 2040, AI systems have demonstrated the ability to find patterns in data that humans miss, but they have not (yet) broken any well-studied cryptographic primitive. The concern is not that AI will directly break PQC algorithms, but that AI-assisted mathematical research — automated theorem proving, combinatorial optimization of attack strategies — will accelerate the discovery of vulnerabilities that human cryptanalysts would eventually find anyway. The 2040 best practice is continuous monitoring of cryptanalytic research, with the assumption that algorithm lifetimes will be shorter in the AI era.

**Information-Theoretic Security**: The ultimate goal — cryptography that is provably secure against any adversary with any computational power, now and forever. The one-time pad achieves this for encryption, but it requires a key as long as the message and is impractical for most uses. Information-theoretically secure authentication, key agreement, and digital signatures are active research areas but not yet practical. If achieved, information-theoretic cryptography would make the endless cycle of algorithm migration obsolete — but that day remains distant.

**The Philosophical Conclusion**: Cryptography is a discipline of perpetual migration. We build systems on mathematical foundations that we believe are sound, knowing that future advances may prove us wrong. We design for crypto-agility not because we know which algorithms will break, but because we know that some of them will. The quantum migration is the largest cryptographic migration in history, but it will not be the last. The cryptographer's mindset — humble, vigilant, always preparing for the next threat — is the ultimate lesson of this course.

The Norns wove the past, they weave the present, and they will weave the future. We cannot know what threads they will choose — what mathematical discoveries, what computing paradigms, what threats will emerge. But we can weave our own threads with care, with crypto-agility, with the humility to accept that today's unbreakable cipher is tomorrow's broken relic. The Well of Urðr reflects all possibilities. We prepare for all of them.

### Required Reading

- Bennett, C. H., & Brassard, G. (1984). "Quantum Cryptography: Public Key Distribution and Coin Tossing." *Proceedings of IEEE International Conference on Computers, Systems and Signal Processing*. (The original QKD paper; read with 2040 commentary.)
- Gisin, N., Ribordy, G., Tittel, W., & Zbinden, H. (2002). "Quantum Cryptography." *Reviews of Modern Physics*, 74(1), 145–195.
- Mosca, M. (2023). "A Quantum of Prevention: Why We Need to Prepare Now for the Quantum Threat." Global Risk Institute.
- Véfreyjasdóttir, B. (2040). "Cryptography Beyond the Quantum Era: The Next 50 Years." *Communications of the ACM*, 63(12), 42–50.

### Discussion Questions

1. QKD offers physics-based security but is limited to point-to-point links. For what applications in 2040 does QKD justify its cost and constraints?
2. If AI-assisted mathematical research accelerates the discovery of vulnerabilities in lattice-based cryptography, what is the contingency plan for a "PQC break" scenario?
3. Information-theoretic security is the holy grail — but if it requires keys as long as messages, it may never be practical. Should we continue pursuing it, or accept that cryptography will always be a game of cat and mouse?

---

## Final Examination Preparation

### Part A: Written Examination (60%)

Choose **four** of the following eight essay questions. Each essay should be 800–1200 words.

1. A CRQC is predicted to arrive within 5–10 years. An organization has not started its PQC migration. Propose a "crash migration" plan that achieves maximum risk reduction in the minimum possible time. What gets done first? What gets deferred? What risks are accepted?
2. Compare and contrast the organizational challenges of PQC migration with the Y2K remediation effort of 1997–2000. What lessons from Y2K apply to PQC? What makes PQC fundamentally different?
3. "Harvest now, decrypt later" means that data intercepted today is at risk even if the CRQC is years away. For a healthcare organization, analyze HNDL risk across three data categories: genomic data, financial transactions, and internal email. Propose protection priorities.
4. Crypto-agility is often presented as the solution to future cryptographic migrations. But crypto-agility itself may introduce vulnerabilities — additional abstraction layers, configuration complexity, algorithm negotiation that could be exploited. Is crypto-agility a net security positive or negative? Argue both sides and reach a conclusion.
5. Hardware Security Modules (HSMs) with 15-year operational lifetimes cannot be easily migrated. For a financial institution that relies on HSMs for payment processing, propose a transition strategy that maintains security, compliance, and operational continuity.
6. The cryptographic proxy pattern places a PQC-capable gateway in front of legacy devices that cannot be updated. Analyze the security properties of this pattern: what threats does it mitigate, what threats remain, and under what circumstances is the residual risk acceptable?
7. Government mandates require PQC migration for critical infrastructure. But small organizations with limited resources struggle to comply. Should migration timelines be tiered by organization size and criticality? Design a tiered regulatory framework and defend it against the criticism that it creates a "two-tier" security model.
8. Beyond PQC, what is the next cryptographic crisis? Identify one emerging threat (your choice: AI-assisted cryptanalysis, a specific mathematical breakthrough, a new computing paradigm) and describe how an organization practicing crypto-agility would respond differently from one that is not.

### Part B: Migration Architecture Design (40%)

**Scenario:** Mímir National Bank (MNB) is a mid-sized financial institution with 5,000 employees, operating a hybrid IT environment: on-premises data centers (2 locations), AWS (primary cloud), and Azure (secondary for specific workloads). MNB processes 2 million transactions daily, maintains customer financial records with 30-year retention requirements, and is regulated by the FFIEC and EBA.

MNB's CEO has just read a quantum computing whitepaper and is alarmed. She has mandated: "I want every system quantum-safe within 3 years. Budget is whatever it takes — within reason."

**Deliverables:**
1. **Cryptographic Inventory Strategy** (500–750 words): Design the approach for creating a comprehensive cryptographic inventory at MNB. What discovery techniques would you employ? What systems are likely to be the hardest to discover? How do you ensure the inventory stays current during the 3-year migration?
2. **Prioritized Migration Roadmap** (750–1000 words): Apply the prioritization framework to MNB's environment. Which systems get migrated first? Which can wait? Justify your ordering with reference to MNB's specific risks (financial transactions, customer data with 30-year retention, regulatory obligations).
3. **Technical Architecture** (750–1000 words): Specify the PQC algorithms, protocols, and configuration for MNB's key systems: customer-facing web applications, internal service-to-service communication, database encryption, and backups/DR. Address hybrid vs. PQC-only decisions.
4. **Risk Acceptance and Contingency** (500–750 words): Despite the 3-year mandate, some systems will not be fully migrated. Identify which systems are most likely to be incomplete, articulate the residual risk, propose compensating controls, and outline the communication to the CEO and regulators when the deadline passes with incomplete migration.

---

*This course was woven at the University of Yggdrasil, 2040, by the Department of Information Technology. The quantum dawn approaches. The wise have already begun to prepare. May your keys be quantum-safe, your certificates be PQC-signed, and your migrations be complete before the CRQC arrives. The Norns weave — but we choose the threads. Skál!*
