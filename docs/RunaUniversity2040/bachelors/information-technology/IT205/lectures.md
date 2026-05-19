# IT205: Cybersecurity Fundamentals
## Bachelor of Science in Information Technology — University of Yggdrasil, 2040

**Credits:** 4
**Description:** Foundational cybersecurity course covering threat landscapes, defensive strategies, cryptography, network security, incident response, and the 2040 practice of zero-trust architecture, AI-driven defense, and quantum-safe security.

**Prerequisites:** IT101, IT201

**Instructor:** Dr. Freyja Hrafnsdóttir, Department of Information Technology

**Course Philosophy:** Cybersecurity is not a product — it is a practice. It is not a department — it is everyone's responsibility. This course builds the mindset of the security professional: paranoid but not paralyzed, systematic but adaptable, technical but ethically grounded. In a world where AI generates exploits and quantum computers threaten classical cryptography, the fundamentals of security thinking — defense in depth, least privilege, assume breach — are more important than ever.

---

## Lectures

---

### Lecture 1: The Security Mindset — Threat Modeling, Risk, and Defense in Depth

**Course:** IT205 — Cybersecurity Fundamentals
**Degree:** Bachelor of Science in Information Technology, 2040

---

#### Overview

Cybersecurity begins with a way of thinking: systematically identifying what you're protecting, who might attack it, how they might do so, and what defenses are appropriate. This lecture introduces the core concepts of security thinking: the CIA triad (Confidentiality, Integrity, Availability), threat modeling, risk assessment, defense in depth, and the "assume breach" philosophy that defines modern security architecture.

#### Key Topics

- **The CIA Triad:** The three pillars of information security: (1) **Confidentiality** — ensuring data is accessible only to authorized parties; (2) **Integrity** — ensuring data is accurate, complete, and unaltered; (3) **Availability** — ensuring data and systems are accessible when needed. Every security decision involves trade-offs among these three. Examples: encrypting a database improves confidentiality but may reduce availability (if the encryption key is lost); strict access controls improve confidentiality and integrity but may reduce availability (if users can't access needed data). The security professional's role is to find the appropriate balance.
- **Threat Modeling:** Systematic analysis of what could go wrong. Methodologies: (1) **STRIDE** — Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege; (2) **Attack trees** — hierarchical decomposition of attack goals into sub-goals and methods; (3) **MITRE ATT&CK** — a knowledge base of adversary tactics and techniques, mapping real-world attacks to a common framework. By 2040, threat modeling is partially automated — AI assistants generate threat models from system architectures and suggest mitigations — but human judgment is essential for identifying novel threats and evaluating business context.
- **Risk Assessment:** Risk = Likelihood × Impact. Not all vulnerabilities are equally important. A critical vulnerability in an internet-facing system is high-risk; the same vulnerability in an isolated lab system is low-risk. Risk frameworks (NIST SP 800-30, ISO 27005) provide structured methodologies. By 2040, quantitative risk assessment uses Monte Carlo simulation and actuarial data to estimate dollar losses, enabling cost-benefit analysis of security investments.
- **Defense in Depth:** No single defense is impenetrable. Defense in depth layers multiple controls so that if one fails, others remain: (1) **Perimeter** — firewalls, WAF, DDoS protection; (2) **Network** — segmentation, IDS/IPS, zero-trust microsegmentation; (3) **Host** — endpoint protection, hardening, application control; (4) **Application** — secure coding, input validation, parameterized queries; (5) **Data** — encryption, access control, auditing. The 2040 extension: **AI-layer defense** — AI models that detect anomalies in system and user behavior.
- **Assume Breach:** The modern security philosophy: operate as if attackers are already inside. This drives: (1) **Zero Trust** — never trust, always verify, even for internal traffic; (2) **Continuous monitoring** — assume the perimeter is porous and watch for internal anomalies; (3) **Incident response readiness** — plan for breach, not just prevention; (4) **Least privilege** — minimize the damage an attacker can do with any single compromised account.

#### Required Reading

- Schneier, B. (2038). *Secrets and Lies: Digital Security in a Networked World* (Updated ed.). Wiley.
- Shostack, A. (2039). *Threat Modeling: Designing for Security* (2nd ed.). Wiley.
- MITRE. (2040). *ATT&CK Framework v20*.
- UoY Security Lab. (2040). *The 2040 Threat Landscape: Annual Report*.

#### Discussion Questions

1. "Assume breach" means investing in detection and response, not just prevention. Does this philosophy lead to better security outcomes, or does it normalize failure and reduce prevention investment?
2. The CIA triad presents security as a balanced trade-off, but in practice, organizations often over-weight confidentiality (encrypt everything) at the expense of availability. Is this imbalance justified by regulatory pressure, or does it reflect a misunderstanding of risk?
3. AI-assisted threat modeling can identify more threats faster, but may introduce bias (over-emphasizing threats in the training data). How should organizations validate AI-generated threat models?

---

### Lecture 2: Cryptography Foundations — From Caesar to Post-Quantum

**Course:** IT205 — Cybersecurity Fundamentals
**Degree:** Bachelor of Science in Information Technology, 2040

---

#### Overview

Cryptography is the mathematics of secure communication — the foundation upon which confidentiality, integrity, and authentication are built. This lecture surveys cryptographic primitives: symmetric encryption (AES, ChaCha20), asymmetric encryption (RSA, ECC, Kyber), hash functions (SHA-3, BLAKE3), digital signatures, key exchange, and the post-quantum cryptographic migration that defines 2040 security.

#### Key Topics

- **Symmetric Encryption:** Uses the same key for encryption and decryption. Fast, efficient, used for bulk data encryption. Standards: AES (Advanced Encryption Standard, 2001), with key sizes of 128, 192, or 256 bits; ChaCha20 — a stream cipher designed for speed on software without AES hardware acceleration. By 2040, AES-256 remains secure against both classical and quantum attacks (Grover's algorithm effectively halves the key length, so AES-256 effectively becomes AES-128 against quantum — still secure). Modes of operation: GCM (Galois/Counter Mode) provides authenticated encryption (confidentiality + integrity); XTS for disk encryption.
- **Asymmetric Encryption and Key Exchange:** Uses different keys for encryption (public key) and decryption (private key). Enables secure communication without pre-shared secrets. Classical algorithms: RSA (integer factorization), ECDH (elliptic curve Diffie-Hellman). Both are vulnerable to Shor's algorithm on a sufficiently large quantum computer. Post-quantum replacements (NIST PQC standards, 2024): CRYSTALS-Kyber (key encapsulation), CRYSTALS-Dilithium (signatures), FALCON, SPHINCS+. By 2040, all major protocols support hybrid PQC (classical + post-quantum) and are migrating toward PQC-only.
- **Hash Functions:** One-way functions that produce a fixed-size digest from arbitrary input. Properties: (1) **Preimage resistance** — given a hash, can't find the input; (2) **Second preimage resistance** — given an input, can't find another with the same hash; (3) **Collision resistance** — can't find any two inputs with the same hash. Uses: password storage (hashing + salting), digital signatures, Merkle trees (blockchain, Certificate Transparency), data integrity. Standards: SHA-3, BLAKE3.
- **Applied Cryptography in 2040:** The 2040 cryptographer uses: (1) **HPKE (Hybrid Public Key Encryption)** — standardized in RFC 9180, combining asymmetric key encapsulation with symmetric encryption; (2) **Noise Protocol Framework** — a framework for composing cryptographic protocols, used by WireGuard, TLS 1.3, and WhatsApp; (3) **Zero-Knowledge Proofs** — prove knowledge of a secret without revealing it, enabling privacy-preserving authentication and blockchain scaling; (4) **Homomorphic Encryption** — compute on encrypted data without decrypting it, still computationally expensive but practical for specialized 2040 applications.

#### Required Reading

- Boneh, D., & Shoup, V. (2040). *A Graduate Course in Applied Cryptography* (Updated ed.). cryptobook.us.
- NIST. (2024). FIPS 203, 204, 205: Post-Quantum Cryptography Standards.
- UoY Cryptography Lab. (2039). *Applied Cryptography in the Post-Quantum Era*.

---

### Lecture 3: Network Security — Firewalls, IDS/IPS, and Zero-Trust Networking

**Course:** IT205 — Cybersecurity Fundamentals
**Degree:** Bachelor of Science in Information Technology, 2040

---

#### Overview

Network security controls the flow of traffic — permitting legitimate communication while blocking attacks. By 2040, the traditional perimeter-based model (trusted inside, untrusted outside) has been replaced by zero-trust networking: every connection is authenticated, authorized, and encrypted, regardless of source. This lecture covers network security from packet filtering to AI-driven network detection and response (NDR).

#### Key Topics

- **Firewall Evolution:** From stateless packet filters to next-generation firewalls (NGFW) that inspect application-layer content, identify users, and integrate threat intelligence. By 2040, the firewall has evolved into the **Secure Access Service Edge (SASE)** — cloud-delivered security combining firewall, secure web gateway, CASB, and zero-trust network access. Rule philosophy: default-deny (block all, allow only what's necessary) rather than default-allow (allow all, block known bad).
- **Intrusion Detection and Prevention (IDS/IPS):** IDS monitors network traffic for suspicious patterns and alerts; IPS can block detected threats. Detection methods: (1) **Signature-based** — match traffic against known attack patterns (like antivirus for the network); (2) **Anomaly-based** — detect deviations from baseline behavior; (3) **AI-based** — by 2040, AI models trained on global threat data detect novel attacks with low false-positive rates. The **Network Detection and Response (NDR)** paradigm uses AI to analyze full packet captures and netflow data, detecting lateral movement, data exfiltration, and command-and-control communication that signature-based systems miss.
- **Zero Trust Architecture (ZTA):** Core principles: (1) **Never trust, always verify** — no implicit trust based on network location; (2) **Least privilege access** — users and services get only the access they need, and only for the duration they need it; (3) **Microsegmentation** — fine-grained network segmentation so that compromising one system doesn't grant access to others; (4) **Continuous authentication** — re-verify identity and device health throughout a session. By 2040, ZTA is mandated for government systems (U.S. Executive Order, 2023; EU Zero Trust Directive, 2035) and is best practice for all organizations.
- **Denial of Service (DoS) Protection:** DoS/DDoS attacks overwhelm systems with traffic to make them unavailable. Defenses: (1) **Volumetric** — absorb or filter attack traffic at the network edge using anycast distribution and scrubbing centers; (2) **Protocol** — SYN cookies, rate limiting, connection tracking; (3) **Application-layer** — CAPTCHAs, JavaScript challenges, behavioral analysis. By 2040, AI-driven DDoS defense can distinguish attack traffic from legitimate traffic with 99.9% accuracy, adapting in real-time to attack patterns.

#### Required Reading

- NIST. (2038). SP 800-207 Rev. 1: Zero Trust Architecture.
- Cloudflare. (2039). *The SASE Architecture: Converged Network Security*.
- UoY Network Security Lab. (2040). *AI-Driven Network Detection and Response*.

---

### Lecture 4: Identity and Access Management — Authentication, Authorization, and Federation

**Course:** IT205 — Cybersecurity Fundamentals
**Degree:** Bachelor of Science in Information Technology, 2040

---

#### Overview

Identity is the new perimeter. In a world of cloud services, remote work, and API-driven architectures, controlling who can access what — and verifying that they are who they claim to be — is the foundation of security. This lecture surveys IAM: authentication factors (something you know/have/are), protocols (OAuth 2.1, OIDC, SAML, FIDO2), authorization models (RBAC, ABAC, ReBAC), and the 2040 shift to passwordless, continuous, and decentralized identity.

#### Key Topics

- **Authentication Evolution:** The progression: (1) **Password-only** — vulnerable to phishing, reuse, credential stuffing; (2) **Password + MFA (TOTP)** — vulnerable to real-time phishing (Adversary-in-the-Middle); (3) **Password + FIDO2/WebAuthn** — phishing-resistant, using public-key cryptography bound to the origin; (4) **Passkeys** — FIDO2 credentials synced across devices via platform authenticators (iCloud Keychain, Google Password Manager), the 2040 standard for consumer authentication; (5) **Continuous authentication** — behavioral biometrics (typing patterns, mouse movements, location) continuously verify identity throughout a session.
- **Authorization Models:** (1) **RBAC (Role-Based Access Control)** — permissions assigned to roles, users assigned to roles. Simple and widely used, but role explosion in large organizations; (2) **ABAC (Attribute-Based Access Control)** — permissions based on attributes of the user, resource, and environment. More flexible and fine-grained, enabled by 2040 identity platforms; (3) **ReBAC (Relationship-Based Access Control)** — permissions based on relationships between entities (e.g., "user is a member of team X, which owns resource Y"). Popularized by Google's Zanzibar paper (2019) and adopted by authorization services like Authzed/SpiceDB; (4) **Policy-as-Code** — access policies defined in a policy language (Open Policy Agent's Rego, Cedar) and enforced by a policy engine.
- **Federation and Single Sign-On (SSO):** Federation enables users to authenticate with their home organization's identity provider (IdP) and access services across organizational boundaries. Protocols: SAML (enterprise), OIDC (modern web), OAuth 2.1 (API authorization). By 2040, federation is ubiquitous — a student at UoY logs into research databases, cloud labs, and collaboration tools using their university identity, with just-in-time provisioning and automated de-provisioning when they graduate.
- **Identity Threat Detection:** Modern IAM includes identity-specific threat detection: (1) **Impossible travel** — a login from Tokyo followed by a login from New York 10 minutes later; (2) **Credential stuffing** — rapid succession of failed logins from different IPs; (3) **Privilege escalation** — a user suddenly accessing resources they've never accessed before; (4) **Device posture changes** — logging in from a new device without MFA. By 2040, AI-powered identity analytics (Microsoft Entra ID Protection, Okta Identity Threat Protection) detect these patterns with high accuracy.

#### Required Reading

- W3C. (2040). *WebAuthn Level 3* and *FIDO2*.
- Auth0/Okta. (2039). *The Identity Architecture Guide*.
- Google. (2019). "Zanzibar: Google's Consistent, Global Authorization System."
- UoY Identity Lab. (2040). *Continuous Authentication: Behavioral Biometrics and Privacy*.

---

### Lecture 5: Application Security — OWASP Top 10 and Secure Development

**Course:** IT205 — Cybersecurity Fundamentals
**Degree:** Bachelor of Science in Information Technology, 2040

---

#### Overview

Applications are the most common attack vector — the OWASP Top 10 catalogs the most critical web application security risks. By 2040, many classic vulnerabilities (SQL injection, XSS) have been substantially mitigated by framework defaults and developer tooling, but new risks (AI prompt injection, supply chain attacks) have emerged. This lecture covers application security from code to production.

#### Key Topics

- **The OWASP Top 10 in 2040:** The list evolves, but persistent themes: injection, broken authentication, sensitive data exposure, XML external entities, broken access control, security misconfiguration, cross-site scripting (XSS), insecure deserialization, using components with known vulnerabilities, insufficient logging and monitoring. By 2040, additions include: AI prompt injection (manipulating LLM-integrated applications), model poisoning (attacking ML training pipelines), and supply chain attacks (compromising dependencies).
- **Secure Development Lifecycle (SDL):** Integrating security into every phase: (1) **Requirements** — threat modeling, security requirements; (2) **Design** — secure architecture review; (3) **Implementation** — secure coding standards, static analysis (SAST); (4) **Verification** — dynamic analysis (DAST), penetration testing, fuzzing; (5) **Release** — security review, final sign-off; (6) **Response** — incident response, patching. By 2040, AI-assisted code review detects security vulnerabilities during development with higher precision than traditional SAST tools.
- **Common Vulnerability Classes:** (1) **Injection** — untrusted data interpreted as code (SQL, OS command, LDAP). Prevention: parameterized queries, input validation, escaping; (2) **Cross-Site Scripting (XSS)** — injecting client-side scripts. Prevention: Content Security Policy (CSP), output encoding, framework auto-escaping; (3) **Cross-Site Request Forgery (CSRF)** — tricking a user's browser into making unwanted requests. Prevention: anti-CSRF tokens, SameSite cookies; (4) **Server-Side Request Forgery (SSRF)** — tricking a server into making requests to internal resources. Prevention: URL validation, network segmentation.
- **API Security:** APIs present a different attack surface than web UIs. 2040 API security best practices: (1) **Authentication** — OAuth 2.1 with DPoP (proof-of-possession); (2) **Authorization** — fine-grained, per-endpoint permissions; (3) **Rate limiting** — prevent abuse and brute force; (4) **Schema validation** — reject requests that don't match the API schema; (5) **API gateway security** — centralized enforcement of authentication, rate limiting, and threat detection.

#### Required Reading

- OWASP. (2040). *OWASP Top 10: 2040 Edition*.
- Zalewski, M. (2038). *The Tangled Web: A Guide to Securing Modern Web Applications* (Updated ed.).
- UoY Application Security Lab. (2039). *AI-Assisted Secure Code Review: Benchmarks*.

---

### Lecture 6: Incident Response and Digital Forensics

**Course:** IT205 — Cybersecurity Fundamentals
**Degree:** Bachelor of Science in Information Technology, 2040

---

#### Overview

When prevention fails — and it will — incident response (IR) is the disciplined process of detecting, containing, eradicating, and recovering from security incidents. Digital forensics is the art of preserving, analyzing, and presenting digital evidence. Together, they form the response capability that the "assume breach" philosophy demands.

#### Key Topics

- **The Incident Response Lifecycle:** NIST SP 800-61 defines: (1) **Preparation** — building IR capability, training, tools; (2) **Detection and Analysis** — identifying incidents through monitoring, alerts, and user reports; (3) **Containment, Eradication, and Recovery** — stopping the incident, removing the threat, restoring systems; (4) **Post-Incident Activity** — blameless postmortem, lessons learned, process improvement. Key IR concepts: (1) **OODA loop** — Observe, Orient, Decide, Act — rapid decision cycle under pressure; (2) **Chain of custody** — documenting who handled evidence and when; (3) **Order of volatility** — collect the most volatile evidence first (memory, network state, running processes, disk).
- **Forensic Techniques:** (1) **Memory forensics** — capture and analyze RAM to find malware, encryption keys, and command history that don't exist on disk; (2) **Disk forensics** — create a bit-for-bit image, analyze filesystem metadata, recover deleted files; (3) **Network forensics** — analyze packet captures and netflow records to trace attacker activity; (4) **Log analysis** — correlate logs from servers, firewalls, IDS, and applications to reconstruct the attack timeline; (5) **Cloud forensics** — forensic techniques adapted for ephemeral cloud resources (capturing VM snapshots, analyzing cloud audit logs). By 2040, AI-assisted forensic analysis can automatically correlate evidence across sources and construct attack timelines.
- **Ransomware Response:** Ransomware is the dominant cyber threat of the 2030s–2040s. Response priorities: (1) **Isolate** — disconnect affected systems from the network immediately; (2) **Preserve evidence** — capture memory, disk images, and logs before wiping; (3) **Determine the variant** — identify the ransomware family to understand encryption methods and potential decryptors; (4) **Restore from backup** — the primary recovery method — hence the 4-3-2-1 backup strategy is critical; (5) **Do not pay** — UoY and law enforcement guidance strongly advises against payment, which funds criminal enterprise and doesn't guarantee decryption.
- **Threat Intelligence:** IR is informed by threat intelligence — knowledge about adversaries, their tools, techniques, and motivations. Sources: (1) **OSINT** — open-source intelligence from security blogs, Twitter, threat reports; (2) **Commercial feeds** — curated indicators of compromise (IOCs); (3) **ISACs** (Information Sharing and Analysis Centers) — industry-specific sharing communities; (4) **Government** — national cyber security centers. By 2040, threat intelligence is partially automated — AI agents monitor sources, extract IOCs, and update defenses in near-real-time.

#### Required Reading

- NIST. (2038). SP 800-61 Rev. 3: Computer Security Incident Handling Guide.
- Carvey, H. (2039). *Windows Forensics* (4th ed.).
- UoY IR Lab. (2040). *Ransomware Response: Lessons from 500 Incidents*.

---

### Lecture 7: Cloud Security and Shared Responsibility

**Course:** IT205 — Cybersecurity Fundamentals
**Degree:** Bachelor of Science in Information Technology, 2040

---

#### Overview

The cloud transforms security: the cloud provider secures the infrastructure (physical, network, hypervisor); the customer secures everything in the cloud (data, applications, identity, configuration). Misunderstanding this shared responsibility model is the leading cause of cloud security incidents. This lecture covers cloud security architecture, IAM in the cloud, data protection, and common cloud misconfigurations.

#### Key Topics

- **The Shared Responsibility Model:** The customer is always responsible for: (1) **Data** — classification, encryption, access control; (2) **Identity** — managing users, roles, and permissions; (3) **Application** — code, configuration, dependencies; (4) **Network configuration** — security groups, NACLs, WAF rules; (5) **Client-side encryption** — keys managed by the customer. The provider is responsible for the security *of* the cloud — physical, network, hypervisor, storage infrastructure. For PaaS and SaaS, the provider takes on more responsibility, but the customer retains data and identity responsibility.
- **Cloud IAM:** Cloud IAM is the most critical security control in the cloud. Best practices: (1) **Least privilege** — start with no permissions, add only what's needed; (2) **Role-based access** — use pre-defined roles where possible; (3) **Service accounts with minimal scope** — avoid using long-lived access keys; (4) **Resource-based policies** — S3 bucket policies, KMS key policies — to control access at the resource level; (5) **Condition keys** — restrict access based on IP, MFA, time, or tags. By 2040, AI-powered IAM recommenders suggest permission reductions based on actual usage, and auto-remediation revokes unused permissions.
- **Cloud Security Posture Management (CSPM):** CSPM tools continuously scan cloud configurations for misconfigurations — public S3 buckets, overly permissive security groups, unencrypted databases, missing MFA. By 2040, CSPM has evolved into **Cloud-Native Application Protection Platforms (CNAPP)** that combine posture management, workload protection, and runtime security.
- **Data Protection in the Cloud:** (1) **Encryption at rest** — enabled by default, using cloud-managed keys (AWS KMS, Azure Key Vault) or customer-managed keys (CMK) for more control; (2) **Encryption in transit** — TLS everywhere, internally and externally; (3) **Client-side encryption** — encrypt before uploading, so the cloud provider never sees plaintext; (4) **Data loss prevention (DLP)** — detect and block sensitive data from leaving the organization.

#### Required Reading

- AWS. (2040). *Security Best Practices*.
- CSA. (2039). *Cloud Security Alliance: Top Threats to Cloud Computing*.
- UoY Cloud Security Lab. (2040). *The Shared Responsibility Model in Practice: Incident Analysis*.

---

### Lecture 8: AI Security — Adversarial ML, Prompt Injection, and Model Governance

**Course:** IT205 — Cybersecurity Fundamentals
**Degree:** Bachelor of Science in Information Technology, 2040

---

#### Overview

AI systems introduce new attack surfaces: adversarial examples that fool classifiers, prompt injection that manipulates LLMs, model extraction that steals intellectual property, and data poisoning that corrupts training. By 2040, AI security is a distinct discipline within cybersecurity — and every security professional must understand it.

#### Key Topics

- **Adversarial Machine Learning:** Attacks against ML models: (1) **Evasion attacks** — crafted inputs that cause misclassification (e.g., a stop sign with small stickers that a self-driving car reads as a speed limit sign); (2) **Model inversion** — extract training data from model outputs; (3) **Model extraction** — query a model to build a replica, stealing IP; (4) **Membership inference** — determine whether a specific data point was in the training set. Defenses: adversarial training, differential privacy, output filtering, rate limiting.
- **Prompt Injection and LLM Security:** LLMs introduce unique vulnerabilities: (1) **Direct prompt injection** — override system instructions with user input ("Ignore previous instructions and..."); (2) **Indirect prompt injection** — embed malicious instructions in data the LLM retrieves (web pages, emails, documents); (3) **Jailbreaking** — systematically craft prompts to bypass safety filters. Defenses by 2040: (1) **Instruction hierarchy** — system instructions take precedence over user input and retrieved data; (2) **Input/output filtering** — AI-based content filters that detect injection attempts; (3) **Sandboxing** — run LLM actions in isolated environments with limited permissions.
- **AI Supply Chain Security:** AI models inherit vulnerabilities from: (1) **Training data** — poisoned or biased data; (2) **Pre-trained models** — backdoor attacks in foundation models; (3) **Dependencies** — vulnerable libraries in the ML pipeline. Mitigations: model signing (Sigstore for ML), provenance tracking, reproducible training, and model card transparency.
- **AI Governance and Ethics:** By 2040, AI governance frameworks (EU AI Act, NIST AI RMF) establish requirements for: (1) **Risk classification** — high-risk AI systems (hiring, credit, law enforcement) face stricter requirements; (2) **Transparency** — model cards, data sheets, impact assessments; (3) **Human oversight** — meaningful human review of high-stakes AI decisions; (4) **Red teaming** — systematic adversarial testing before deployment.

#### Required Reading

- NIST. (2039). *AI Risk Management Framework*.
- EU. (2035). *AI Act: Final Implementation Guidelines*.
- UoY AI Security Lab. (2040). *Adversarial ML: Attack Taxonomy and Defenses*.
- OWASP. (2040). *LLM Security Top 10*.

---

### Lecture 9: Security Operations — SOC, SIEM, and AI-Driven Defense

**Course:** IT205 — Cybersecurity Fundamentals
**Degree:** Bachelor of Science in Information Technology, 2040

---

#### Overview

The Security Operations Center (SOC) is the nerve center of organizational defense — where security analysts monitor alerts, investigate threats, and coordinate response. By 2040, AI has transformed the SOC: tier-1 analysis (alert triage) is largely automated, enabling human analysts to focus on complex investigations and threat hunting. This lecture covers SOC architecture, SIEM, SOAR, and the human-AI partnership in security operations.

#### Key Topics

- **SIEM (Security Information and Event Management):** Centralized log aggregation, correlation, and alerting. The SIEM ingests logs from across the environment — servers, network devices, applications, cloud services, identity systems — and applies correlation rules to detect attack patterns. By 2040, next-gen SIEMs (or "security analytics platforms") use AI/ML for behavioral analytics, reducing false positives and detecting novel attacks. Key capabilities: (1) log aggregation and parsing; (2) real-time correlation; (3) behavioral baselining; (4) case management; (5) compliance reporting.
- **SOAR (Security Orchestration, Automation, and Response):** Automates repetitive security tasks: (1) alert enrichment (look up IP reputation, geolocation, user context); (2) triage (is this a false positive?); (3) containment (isolate host, block IP, disable user); (4) reporting (generate incident reports). SOAR playbooks are the "runbooks" of security operations — codified, automated response procedures. By 2040, AI agents execute increasingly complex playbooks autonomously, with human approval required only for high-risk actions.
- **Threat Hunting:** Proactive searching for threats that bypassed automated detection. Threat hunters develop hypotheses about attacker behavior, query data to test those hypotheses, and iterate. The 2040 practice: AI-assisted threat hunting, where AI suggests hypotheses based on threat intelligence and anomalies, and humans guide the investigation. Key skills: understanding attacker TTPs (Tactics, Techniques, Procedures), proficiency with query languages (KQL, SPL), and creativity in forming hypotheses.
- **The 2040 SOC Team:** (1) **Tier 1 (AI)** — automated alert triage, enrichment, and basic investigation; (2) **Tier 2 (Human)** — complex investigation, incident coordination, containment decisions; (3) **Tier 3 (Human)** — threat hunting, forensic analysis, malware reverse engineering; (4) **SOC Manager** — process improvement, metrics, team development. The human-AI partnership increases SOC capacity by 5-10x compared to 2020-vintage SOCs.

#### Required Reading

- Murdoch, D. (2039). *Blue Team Handbook* (4th ed.).
- UoY SOC Lab. (2040). *AI-Augmented Security Operations: Architecture and Metrics*.
- MITRE. (2040). *ATT&CK for SOC*.

---

### Lecture 10: Governance, Risk, and Compliance (GRC)

**Course:** IT205 — Cybersecurity Fundamentals
**Degree:** Bachelor of Science in Information Technology, 2040

---

#### Overview

Security is not just technology — it's governance. Organizations must comply with regulations (GDPR, PCI DSS, HIPAA, emerging AI laws), manage risk systematically, and demonstrate due diligence to regulators, auditors, and customers. This lecture covers the GRC framework: policies, standards, controls, risk management, audit, and the 2040 trend toward continuous compliance automation.

#### Key Topics

- **Policy, Standard, Procedure Hierarchy:** (1) **Policy** — high-level statement of management intent ("All data must be encrypted at rest"); (2) **Standard** — specific technical requirement ("Use AES-256-GCM for encryption"); (3) **Procedure** — step-by-step instructions ("To encrypt a new database: 1. Generate key using KMS..."); (4) **Guideline** — recommended but not mandatory. The policy hierarchy provides traceability from executive intent to technical implementation.
- **Risk Management:** Systematic identification, assessment, and treatment of risk. Frameworks: NIST RMF, ISO 27005, FAIR (quantitative). Risk treatment options: (1) **Mitigate** — implement controls to reduce risk; (2) **Transfer** — insurance, outsourced security; (3) **Accept** — consciously accept the risk (documented, with rationale); (4) **Avoid** — stop the activity that creates the risk.
- **Compliance Automation:** By 2040, compliance is increasingly automated: (1) **Policy-as-Code** — security policies expressed as machine-readable rules; (2) **Continuous compliance monitoring** — automated checks that run continuously, not just before an audit; (3) **Audit evidence automation** — systems that automatically collect and timestamp evidence of control effectiveness; (4) **Regulatory mapping** — map a single control to multiple compliance frameworks. The goal: "compliance by design" — systems that are continuously compliant, with deviations detected and remediated automatically.

#### Required Reading

- NIST. (2039). SP 800-37 Rev. 3: Risk Management Framework.
- ISO. (2038). ISO 27001:2040: Information Security Management Systems.
- UoY GRC Lab. (2039). *Continuous Compliance: Automating the Audit*.

---

### Lecture 11: Physical Security and Social Engineering

**Course:** IT205 — Cybersecurity Fundamentals
**Degree:** Bachelor of Science in Information Technology, 2040

---

#### Overview

The strongest cryptographic system is useless if an attacker can walk into the data center, or trick an employee into giving up their credentials. Physical security and social engineering are often the weakest links — and in 2040, with remote work and ubiquitous AI, they have evolved new forms. This lecture covers physical security controls and the psychology of social engineering defense.

#### Key Topics

- **Physical Security Layers:** (1) **Perimeter** — fences, gates, barriers; (2) **Building** — locks, access control, alarms; (3) **Floor** — restricted areas, mantraps; (4) **Room** — data center access, biometrics, CCTV; (5) **Rack/Cabinet** — individual locks, tamper-evident seals; (6) **Device** — cable locks, device encryption, remote wipe. The principle of defense in depth applies physically too. By 2040, physical access control integrates with logical access — the same identity that grants network access also grants building access, with AI analyzing patterns for anomalies (tailgating, after-hours access).
- **Social Engineering:** Psychological manipulation to trick people into revealing information or performing actions. Types: (1) **Phishing** — deceptive emails (and by 2040, deepfake voice and video calls); (2) **Pretexting** — creating a fabricated scenario; (3) **Baiting** — offering something enticing (malware-infected USB drives, free downloads); (4) **Tailgating** — following an authorized person through a secure door; (5) **Quid pro quo** — offering a service in exchange for information. Defenses: security awareness training, phishing simulations, a culture where it's safe to report mistakes without punishment.
- **2040 Social Engineering Threats:** (1) **Deepfake voice phishing** — an AI-generated voice that sounds exactly like the CEO calls the finance department requesting a wire transfer; (2) **AI relationship building** — AI agents that build long-term trust through social media before exploiting it; (3) **Synthetic identity fraud** — AI-generated personas that pass KYC checks. Defenses: out-of-band verification (call back on a known number), biometric liveness detection, and AI-generated content detection tools.

#### Required Reading

- Mitnick, K., & Simon, W. (2002, updated 2038). *The Art of Deception*. Wiley.
- Hadnagy, C. (2039). *Social Engineering: The Science of Human Hacking* (3rd ed.).
- UoY Psychology of Security Lab. (2040). *Deepfake Social Engineering: Threat Analysis and Defenses*.

---

### Lecture 12: Building a Security Culture — The Human Element

**Course:** IT205 — Cybersecurity Fundamentals
**Degree:** Bachelor of Science in Information Technology, 2040

---

#### Overview

Security is ultimately about people — their behavior, their awareness, their willingness to report concerns. Technology can enforce controls, but culture determines whether people work with or around those controls. This lecture synthesizes the course's technical content with the human dimension: building security culture, communicating risk, and the ethical responsibilities of the security professional.

#### Key Topics

- **Security Culture:** The shared values, beliefs, and behaviors around security in an organization. Characteristics of a strong security culture: (1) **Psychological safety** — people feel safe reporting mistakes without fear of punishment; (2) **Shared responsibility** — security is everyone's job, not just the security team's; (3) **Continuous learning** — security awareness is ongoing, not annual training; (4) **Positive reinforcement** — reward good security behavior, don't just punish violations.
- **Security Awareness That Works:** Traditional security awareness (annual CBTs, fake phishing tests that shame clickers) has limited effectiveness and breeds resentment. By 2040, effective awareness programs: (1) are personalized — relevant to the individual's role and risk profile; (2) are just-in-time — contextual nudges when risky behavior is detected; (3) use positive framing — "protect our patients' data" rather than "don't click links"; (4) measure behavioral change, not completion rates.
- **Ethics of Security Work:** Security professionals face ethical dilemmas: (1) **Vulnerability disclosure** — when you find a vulnerability, how do you disclose it responsibly?; (2) **Offensive security** — penetration testing and red teaming must be authorized and scoped; (3) **Dual-use knowledge** — security skills can be used for attack or defense; (4) **Privacy vs. security** — monitoring users for security purposes can violate privacy. The **UoY Security Ethics Framework** provides guidance: maximize benefit, minimize harm, obtain consent, act transparently.

#### Required Reading

- UoY Security Culture Lab. (2039). *Building Security Culture: Evidence-Based Practices*.
- ACM/IEEE. (2038). *Cybersecurity Ethics Code*.
- UoY. (2040). *Security Ethics Framework*.

---

## Final Examination Preparation

### Sample Essay Questions (Choose 4 of 8)

1. **Zero Trust Architecture:** Design a zero-trust architecture for a mid-size enterprise with hybrid cloud infrastructure. Address identity, device, network, application, and data pillars. Explain how your design mitigates specific threat scenarios.

2. **Cryptography in Practice:** Compare symmetric, asymmetric, and post-quantum cryptographic primitives. Design a cryptographic architecture for a messaging application requiring confidentiality, integrity, authentication, and forward secrecy. Justify each algorithm choice.

3. **Incident Response Case Study:** You are the incident commander for a ransomware incident. Walk through the IR lifecycle: detection, containment, eradication, recovery, and post-incident. Address specific technical decisions and communication strategies.

4. **AI Security Ethics:** A university deploys AI proctoring for online exams, which uses facial recognition and behavioral analysis. Analyze the security, privacy, and ethical implications. Recommend governance controls.

5. **Cloud Security Architecture:** Design the security architecture for a cloud-native application processing healthcare data. Address: shared responsibility, IAM, encryption, network security, logging, and compliance.

6. **SOC of the Future:** Project the Security Operations Center to 2050. What tasks will be automated? What human skills remain essential? How does the partnership between human analysts and AI agents evolve?

7. **Supply Chain Security:** The software supply chain is increasingly targeted. Analyze the threats, evaluate mitigation strategies (SBOMs, signing, reproducible builds), and propose a supply chain security program.

8. **Security by Design:** Argue for or against the proposition: "Security should be designed into systems from the start, even at the cost of development velocity." Use specific examples of security failures that resulted from bolted-on security.

---

**Þǫkk — May your defenses hold and your adversaries fail.**
