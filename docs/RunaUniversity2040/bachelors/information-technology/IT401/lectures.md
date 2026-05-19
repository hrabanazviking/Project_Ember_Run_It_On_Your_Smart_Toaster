# IT401: IT Governance & Compliance — The Law-Speaker's Role in the Digital Thing

**Program:** Bachelor of Information Technology, Year 4  
**Credits:** 4 ECTS  
**Prerequisites:** IT301, IT307  
**Instructor:** Prof. Ragna Þórisdottir, CISA, CGEIT, CRISC, ISO 27001 Lead Auditor  
**Office:** Heorot Hall, Room 401  
**Semester:** Fall 2041  

> *"At the Thing, the law-speaker did not create the law — he remembered it, recited it, and ensured it was followed. The compliance officer and the CISO share this function: they are the memory of regulatory obligation, the voice of due diligence, and the conscience of the organisation when expediency tempts it to forget."* — Ragna Þórisdottir, *The Digital Thing: Governance in the Age of Algorithmic Accountability*, 2039

---

## Course Description

IT Governance and Compliance form the legal, regulatory, and ethical framework within which all other IT disciplines operate. This course prepares the senior IT professional to design governance structures, implement compliance programmes, prepare for regulatory audits, and advise executive leadership on technology risk. Students will navigate the complex 2040 regulatory landscape — GDPR, HIPAA, DORA, CIRCIA, the EU AI Act, and emerging quantum-readiness mandates — while learning to write policies that are both compliant and operationally practical. The course culminates in a simulated regulatory audit where students defend a fictional enterprise's compliance posture before a panel of auditors.

---

## Lecture 1: IT Governance — The Constitution of Technology Decision-Making

### What Governance Is, and Why It Fails

IT Governance is the system by which an organisation's technology decisions are made, monitored, and held accountable. The internationally recognised standard — ISO/IEC 38500:2040, *Governance of IT for the Organisation* — defines six principles: **Responsibility** (individuals and groups understand and accept their responsibilities), **Strategy** (IT strategy aligns with business strategy), **Acquisition** (IT investments are made for valid reasons, with appropriate analysis), **Performance** (IT delivers the promised benefits), **Conformance** (IT complies with laws, regulations, and policies), and **Human Behaviour** (IT policies and decisions respect human factors).

Governance fails — and it fails often — when it devolves into one of three pathologies:

1. **Governance Theatre**: The structures exist on paper — steering committees meet, policies are published, RACI matrices are distributed — but decisions continue to be made informally by whoever shouts loudest. The governance framework is a Potemkin village, maintained to satisfy auditors but disconnected from actual decision-making.
2. **Governance Overreach**: The governance function inserts itself into every operational decision, creating bottlenecks. Every software purchase requires three committee approvals; every architecture decision goes through a six-week review cycle. The organisation slows to a governance crawl, and shadow IT flourishes in the gaps.
3. **Governance by Fear**: Governance is driven exclusively by compliance audit findings. Activities are motivated by "what will the auditors flag?" rather than "what is the right decision for the organisation?" The tail wags the dog.

Effective 2040 governance is **proportionate, principles-based, and integrated** into operational workflows rather than layered on top as a separate process.

### Governance Frameworks

| Framework | Focus | Best For |
|-----------|-------|----------|
| **ISO/IEC 38500** | Board-level governance principles | Enterprise governance; board reporting |
| **COBIT 2040** | 40 governance and management objectives with maturity models | Aligning IT with business goals; audit preparation |
| **ITIL 4 Governance** | Governance component of the Service Value System | Service-oriented organisations |
| **NIST CSF 2.0 Govern Function** | Cybersecurity-specific governance | Risk-based governance for security |

For Yggdrasil Health, a COBIT 2040-aligned governance framework would define: who makes architecture decisions (the Architecture Board), who approves IT investments above €250K (the IT Steering Committee), who owns data (the Data Governance Council), and how these bodies report to the Board of Directors (quarterly IT performance and risk reports).

### Required Reading

- ISO/IEC 38500:2040, *Governance of IT for the Organisation*, all sections.
- ISACA, *COBIT 2040: Governance and Management Objectives*, Introduction and Governance Objectives EDM01-EDM05.
- Weill, P. & Ross, J. (2037), *IT Governance*, 2nd ed., HBR Press, Chs. 1-3.

### Discussion Questions

1. Distinguish between "governance theatre" and genuine governance. How would you detect the former in an organisation?
2. COBIT 2040 distinguishes between "governance objectives" (board-level, evaluate-direct-monitor) and "management objectives" (executive-level, plan-build-run-operate). Why does this distinction matter?
3. If an IT steering committee approves every project proposal put before it, is it fulfilling its governance function?

---

## Lecture 2: The Regulatory Landscape of 2040

### The Expanding Map of Obligation

The 2040 IT professional operates under a regulatory framework vastly more complex than that of 2020. Regulations now cover not only data privacy and financial reporting but also AI system behaviour, operational resilience, supply chain security, and quantum-era cryptography. The key regulatory instruments affecting IT operations include:

| Regulation | Jurisdiction | Scope | Key IT Impact |
|------------|-------------|-------|---------------|
| **GDPR** (Regulation 2016/679, updated 2038) | EU/EEA | Personal data protection | Data mapping, consent management, DPIAs, breach notification (72 hours), DPO appointment |
| **HIPAA** (updated 2040) | USA | Protected Health Information (PHI) | Security Rule (administrative, physical, technical safeguards), Breach Notification Rule |
| **DORA** (Digital Operational Resilience Act, 2025, Rev. 2038) | EU | Financial sector ICT risk | ICT risk management, incident reporting, digital operational resilience testing, third-party risk |
| **CIRCIA** (Cyber Incident Reporting for Critical Infrastructure Act, 2022, updated 2039) | USA | Critical infrastructure | 24-hour ransomware payment reporting, 72-hour incident reporting |
| **EU AI Act** (2036) | EU | AI systems | Risk-based classification (unacceptable, high, limited, minimal); conformity assessments; transparency obligations |
| **CSRD** (Corporate Sustainability Reporting Directive, 2024, Rev. 2039) | EU | Sustainability reporting | IT energy consumption disclosure, e-waste reporting, supply chain due diligence |
| **NIS3 Directive** (2037) | EU | Essential and important entities | Cybersecurity risk management, supply chain security, incident reporting, board accountability |
| **CCPA/CPRA** (California, updated 2038) | California, USA | Consumer privacy | Data subject access requests, opt-out of sale/sharing, data minimisation |

### Regulatory Overlap and Harmonisation

A multinational 2040 enterprise like Yggdrasil Health (operating in Norway, serving EU patients, using US-based cloud providers) faces overlapping regulatory regimes. GDPR and HIPAA both govern health data but have different definitions, breach notification timelines, and individual rights. The compliance function's challenge is to identify the **most stringent applicable requirement** and build controls to that standard — a "highest common denominator" approach — rather than maintaining separate compliance programmes for each regulation. The ISO 27701:2039 Privacy Information Management System provides a unified framework that maps to both GDPR and HIPAA requirements.

### Required Reading

- EU, *General Data Protection Regulation (GDPR)*, updated consolidated text 2038.
- EU, *Digital Operational Resilience Act (DORA)*, Regulatory Technical Standards, 2038.
- EU, *Regulation Laying Down Harmonised Rules on Artificial Intelligence (AI Act)*, 2036.
- US Department of Health and Human Services, *HIPAA Security Rule*, 2040 update.

### Discussion Questions

1. DORA requires financial entities to report major ICT incidents within 4 hours of classification. How would you design an incident management process to meet this requirement?
2. The EU AI Act classifies AI systems by risk. Where would Yggdrasil Health's AI diagnostic module fall, and what obligations does this classification trigger?
3. GDPR and HIPAA have different definitions of a "breach." How does this affect a cloud-hosted EHR system serving both EU and US patients?

---

## Lecture 3: Policy Writing — The Craft of Enforceable Governance

### From Principle to Procedure

IT policies translate governance principles and regulatory requirements into actionable rules that guide behaviour. A policy hierarchy organises documentation from broad to specific:

| Level | Document Type | Purpose | Example |
|-------|--------------|---------|---------|
| **Policy** | Mandatory high-level statement of management intent | Sets expectations; approved by senior leadership | "All PHI must be encrypted at rest and in transit." |
| **Standard** | Mandatory specific technical or procedural requirements | Defines how policy is implemented | "PHI at rest must use AES-256-GCM encryption. TLS 1.3 required for PHI in transit." |
| **Guideline** | Recommended but not mandatory | Provides best-practice guidance | "Consider using customer-managed KMS keys rather than AWS-managed keys for additional control." |
| **Procedure** | Step-by-step instructions | Operationalises the standard | Step 1: Identify the S3 bucket containing PHI. Step 2: Enable default encryption with KMS key arn:aws:kms:... |

### Anatomy of an Effective Policy

A well-written IT policy has eight essential components:

1. **Purpose**: Why this policy exists; which risk it mitigates; which regulation it satisfies
2. **Scope**: Who and what the policy applies to (employees, contractors, all systems, specific systems)
3. **Policy Statement**: The actual requirement, in clear, testable language
4. **Roles and Responsibilities**: Who is accountable for compliance, who is responsible for implementation, who monitors
5. **Compliance Measurement**: How compliance will be verified (automated scanning, manual audit, attestation)
6. **Exceptions Process**: How to request and obtain an exception; who approves; maximum exception duration
7. **Consequences**: What happens if the policy is violated (disciplinary, contractual, regulatory reporting)
8. **Review Cycle**: Annual review date; policy owner

The 2040 policy is a machine-readable artifact as well as a human-readable document. Policy-as-code tools (OPA/Rego, Cedar, AWS SCPs, Azure Policy) encode policies into rules that are automatically enforced. A policy stating "no S3 bucket may be publicly accessible" is expressed as an AWS SCP that blocks `s3:PutBucketPublicAccessBlock` with `PublicAccessBlockConfiguration.RestrictPublicBuckets = false`. The human-readable policy and the machine-enforceable policy must be kept in synchronisation — a gap between them is a compliance finding waiting to happen.

### Required Reading

- ISACA, *COBIT 2040: APO01 Managed I&T Management Framework*, §Policy Development.
- Fitzgerald, T. (2039), *Information Security Policy: A Practical Guide*, 3rd ed., CRC Press.
- AWS, *Service Control Policies: Policy Evaluation Logic*, Documentation, 2040.

### Discussion Questions

1. What distinguishes a policy from a standard from a guideline? Why does conflating these cause compliance failures?
2. Write the encryption policy for Yggdrasil Health's PHI, covering all eight components of an effective policy.
3. How does policy-as-code change the role of the compliance auditor compared to manual policy enforcement?

---

## Lecture 4: Risk Governance and the CISO's Mandate

### Governing Technology Risk

Risk governance is the board-level component of risk management — the structures, processes, and culture that determine how the organisation identifies, evaluates, and responds to risk. ISO 31000:2040, *Risk Management — Guidelines*, defines the framework: the board sets risk appetite (how much risk the organisation is willing to accept in pursuit of its objectives), executive management implements risk management processes, and independent assurance (internal audit, external audit) verifies effectiveness.

The **Three Lines Model** (Institute of Internal Auditors, 2040) clarifies roles:

- **First Line**: Operational management — owns and manages risk. The IT department that configures firewalls and patches servers.
- **Second Line**: Risk and compliance functions — oversee risk. The CISO's office that defines security policies and monitors compliance.
- **Third Line**: Internal audit — provides independent assurance. Audits that the first and second lines are functioning effectively.

The 2040 CISO (Chief Information Security Officer) has evolved from a technical security manager into a C-suite executive. Their mandate includes: presenting cyber risk to the board in business terms (financial exposure, regulatory penalty risk, reputational damage), maintaining the risk register with quantified risk scenarios, overseeing the security programme budget, ensuring regulatory compliance, managing security incident disclosure obligations (materiality assessments under SEC and EU rules), and serving as the public face of the organisation's security posture to customers, regulators, and the press.

### Board-Level Risk Reporting

The board does not need to know the CVSS score of a specific vulnerability. It needs to know: "What is our top cyber risk? What is the potential financial impact? What are we doing about it? Is it getting better or worse?" The CISO's quarterly board report uses a standardised risk dashboard:

| Top Cyber Risks | Inherent Risk | Residual Risk | Trend | Key Mitigations | Investment Required |
|----------------|---------------|---------------|-------|-----------------|---------------------|
| Ransomware attack on EHR systems | Critical (€45M) | High (€12M) | → Stable | Air-gapped backups, EDR, incident response retainer | €1.2M annual |
| Third-party cloud provider outage | High (€18M) | Medium (€5M) | ↑ Increasing | Multi-cloud architecture, provider SLAs | €800K (migration) |
| AI diagnostic model data poisoning | Medium (€8M) | Medium (€4M) | ↑ New | Model validation pipeline, adversarial testing | €500K |

### Required Reading

- ISO 31000:2040, *Risk Management — Guidelines*.
- Institute of Internal Auditors, *Three Lines Model*, 2040 Update.
- NIST SP 800-221A (2040), *Cybersecurity Risk Governance for Boards of Directors*.

### Discussion Questions

1. The Three Lines Model places security operations in the first line and the CISO in the second line. What tensions arise from this separation, and how should they be managed?
2. A board member asks, "Are we secure?" How should the CISO answer?
3. How does quantified risk reporting (EUR amounts, probabilities) change board decision-making compared to red/yellow/green risk heatmaps?

---

## Lecture 5: The Audit Process — Preparation, Participation, Remediation

### The Audit as a Constructive Event

IT audits — whether internal, external (ISO 27001 certification, SOC 2 Type II, HITRUST), or regulatory (GDPR, HIPAA, DORA) — are often perceived as adversarial: auditors versus auditees. The mature 2040 organisation treats audits as constructive verification: an independent assessment that confirms controls are working as designed, identifies gaps before threat actors exploit them, and provides evidence for regulatory compliance that protects the organisation from enforcement actions.

The audit lifecycle:

1. **Audit Notification**: The auditor provides the scope, objectives, criteria (e.g., ISO 27001:2039 Annex A controls), and timeline.
2. **Preparation**: The auditee gathers evidence (policies, procedures, screen captures, system configurations, logs), identifies a point of contact for each audit area, and conducts a pre-audit self-assessment.
3. **Fieldwork**: The auditor interviews personnel, reviews evidence, tests controls (e.g., attempts to access a system without proper authorisation to verify access controls), and documents findings.
4. **Reporting**: The auditor presents findings — non-conformities (major, minor), observations (opportunities for improvement), and positive findings.
5. **Remediation**: The auditee develops a corrective action plan (CAP) for each finding, with root cause analysis, corrective actions, responsible parties, and target dates.
6. **Follow-up**: The auditor verifies corrective actions have been implemented and are effective.

### Audit Evidence Management

The 2040 approach to audit evidence is continuous, not point-in-time. Instead of scrambling to gather evidence in the four weeks before an audit, the organisation maintains an **evidence repository** (a GRC platform — ServiceNow GRC, Archer, OneTrust) where evidence is collected continuously: automated control tests run daily (e.g., "are all production databases encrypted? — Test: query AWS RDS encryption status via API"), their results are stored, and the auditor accesses the evidence repository rather than requesting ad-hoc evidence from the auditee. This "audit-ready at all times" posture reduces audit fatigue and increases the reliability of evidence.

### Required Reading

- ISO 19011:2040, *Guidelines for Auditing Management Systems*.
- ISACA, *CISA Review Manual*, 30th Edition (2040), Chs. 1-2.
- ISACA, *IT Audit Framework (ITAF)*, 4th Edition, 2040.

### Discussion Questions

1. What is the difference between a "finding," an "observation," and a "non-conformity" in audit terminology, and how should each be responded to?
2. How does continuous evidence collection change the relationship between auditor and auditee compared to point-in-time audits?
3. An auditor identifies a major non-conformity: Yggdrasil Health has no documented incident response testing programme. Write the corrective action plan.

---

## Lecture 6: Data Privacy and Protection — Beyond GDPR Compliance

### Privacy by Design and Default

The GDPR introduced the principles of **Data Protection by Design and by Default** (Article 25): data protection measures must be integrated into the processing activities from the design stage, and default settings must minimise data collection. In 2040, these principles have been operationalised into specific architectural patterns:

- **Data Minimisation at Ingestion**: API gateways and ETL pipelines enforce schemas that reject fields not explicitly required for the processing purpose. A patient registration form that collects "religious affiliation" without a documented processing purpose is blocked at the API level.
- **Purpose Limitation via Data Tagging**: Every data element is tagged with its processing purpose(s). Downstream consumers (analytics, ML training, reporting) can only access data tagged with purposes they are authorised for.
- **Storage Limitation via Automated Retention**: Data is assigned a retention period at creation. Automated jobs archive or delete data when its retention period expires. "Delete" means cryptographic erasure where technically feasible.
- **Privacy Engineering**: The emerging discipline of privacy engineering (ISO 31700:2040, *Privacy by Design for Consumer Goods and Services*) specifies technical privacy controls: differential privacy for aggregate analytics, homomorphic encryption for computation on encrypted data, and secure multi-party computation for collaborative analysis without raw data sharing.

### Data Subject Rights Management

GDPR grants data subjects eight rights: access, rectification, erasure ("right to be forgotten"), restriction of processing, data portability, objection, and rights related to automated decision-making and profiling. The 2040 organisation must operationalise these rights into automated workflows. A Data Subject Access Request (DSAR) — "provide all personal data you hold about me" — must be fulfilled within 30 days. For Yggdrasil Health, a DSAR might span data in the EHR, the billing system, the patient portal, call centre recordings, and email archives. The privacy engineering team builds **DSAR automation pipelines** that discover, retrieve, and compile personal data across systems, with manual review gates for data that might infringe third-party rights.

### Required Reading

- EU, *GDPR*, Articles 5 (principles), 12-23 (data subject rights), 25 (data protection by design), 32 (security), 33-34 (breach notification).
- Cavoukian, A. (2038), *Privacy by Design: The 7 Foundational Principles*, 3rd ed., Information and Privacy Commissioner of Ontario.
- ISO 31700:2040, *Privacy by Design for Consumer Goods and Services*.

### Discussion Questions

1. Yggdrasil Health receives a DSAR from a patient who participated in a clinical trial 15 years ago. The trial data is archived on tape. How do you respond?
2. What is the difference between anonymisation and pseudonymisation, and why does this distinction matter under GDPR?
3. How does privacy engineering intersect with data architecture? Give a specific example of an architectural decision driven by privacy requirements.

---

## Lecture 7: Third-Party Risk Management and Supply Chain Security

### The Extended Enterprise

In 2040, the typical enterprise's IT supply chain encompasses cloud providers, SaaS vendors, open-source dependencies, professional services firms, hardware manufacturers, and API-consuming partners. Each link in this chain is a potential vector for compromise. The 2038 SolarWinds-scale attack on the ML framework supply chain — where a compromised Python package in the PyPI repository was used to inject backdoors into AI training pipelines — demonstrated that third-party risk is not theoretical.

Third-Party Risk Management (TPRM) follows a lifecycle:

1. **Inherent Risk Assessment**: Before engagement, assess the vendor's inherent risk (based on the data they will access, the systems they will integrate with, and the criticality of their service). A vendor processing PHI is inherently high-risk.
2. **Due Diligence**: For high-risk vendors: review their SOC 2 Type II report, ISO 27001 certificate, penetration test results, business continuity plan, and financial stability. Send a security questionnaire (SIG, CAIQ, or a custom questionnaire).
3. **Contractual Controls**: Include security requirements in the contract: right to audit, security incident notification (within 24 hours), data processing addendum (DPA), data residency commitments, subcontractor disclosure, and termination assistance (data export).
4. **Ongoing Monitoring**: Continuously monitor the vendor's security posture: certificate expiration, domain reputation, dark web mentions, CVEs in their products, and financial health indicators.
5. **Offboarding**: When the relationship ends: revoke access, verify data deletion (with certificate of destruction), and conduct a final risk assessment.

### Software Bill of Materials (SBOM)

The SBOM is a formal, machine-readable inventory of all components, libraries, and dependencies in a software product. Following the 2037 Log4Shell-scale event in the ML supply chain, the US Executive Order on Improving the Nation's Cybersecurity (2021) was expanded to mandate SBOMs for all software sold to the federal government, and the practice became industry standard. The 2040 SBOM is in SPDX 3.0 or CycloneDX format, generated automatically by CI/CD pipelines, and ingested into the CMDB so that when a CVE is published for a library, affected services are identified in minutes.

### Required Reading

- NIST SP 800-161 Rev. 2 (2040), *Cybersecurity Supply Chain Risk Management*.
- ISO/IEC 27036:2040, *Information Security for Supplier Relationships*.
- Linux Foundation, *SPDX 3.0 Specification*.

### Discussion Questions

1. A critical SaaS vendor refuses to share their SOC 2 report, citing "competitive confidentiality." How do you proceed?
2. An SBOM reveals that a production application depends on a library with a known critical vulnerability but no available patch. Walk through your risk response.
3. How should TPRM differ for an open-source dependency (no contract) compared to a commercial SaaS vendor?

---

## Lecture 8: Business Continuity and Disaster Recovery Governance

### Beyond the BCP Binder

Business Continuity Management (BCM) ensures that critical business functions can continue during and after a disruption. Disaster Recovery (DR) is the subset focused on restoring IT services. The 2040 standard — ISO 22301:2040, *Business Continuity Management Systems* — requires: Business Impact Analysis (BIA) to identify critical functions and their Recovery Time Objectives (RTOs) and Recovery Point Objectives (RPOs), risk assessment to identify threats to those functions, business continuity strategies and plans, testing and exercising of plans, and continual improvement.

For Yggdrasil Health, a BIA would identify:

| Business Function | RTO | RPO | Maximum Tolerable Downtime |
|-------------------|-----|-----|---------------------------|
| Emergency Department EHR Access | < 5 minutes | 0 (zero data loss) | 15 minutes |
| Inpatient Clinical Documentation | < 1 hour | < 5 minutes | 4 hours |
| Outpatient Scheduling | < 4 hours | < 1 hour | 24 hours |
| Billing and Claims | < 24 hours | < 4 hours | 72 hours |

The RTO drives architectural decisions: the Emergency Department's <5-minute RTO requires active-active multi-region deployment with synchronous data replication; the Billing system's 24-hour RTO can be satisfied by backup restoration from cold storage.

### Testing — The Missing Half of BCM

A business continuity plan that has never been tested is not a plan; it is a hope. The 2040 testing regimen includes:

- **Tabletop Exercises** (quarterly): Facilitated discussion of a scenario (ransomware attack, data centre flood). Participants walk through their response verbally. Low cost, high insight into plan gaps.
- **Functional Exercises** (biannual): Selected components are tested in a simulated environment. The IT team restores EHR from backup to a sandbox environment. Measures: restoration time, data integrity.
- **Full-Scale Exercises** (annual): The entire organisation participates. All systems are failed over to the DR site; critical functions are exercised. The most realistic test, but also the most disruptive and expensive.
- **Chaos Engineering** (continuous): Netflix's Chaos Monkey concept — deliberately inject failures into production to verify resilience. In 2040, chaos engineering is standard practice for cloud-native workloads: randomly terminate EC2 instances, introduce network latency, exhaust disk space — and verify that the system self-heals without human intervention.

### Required Reading

- ISO 22301:2040, *Business Continuity Management Systems — Requirements*.
- NIST SP 800-34 Rev. 2 (2040), *Contingency Planning Guide for Information Technology Systems*.
- Rosenthal, C. & Jones, N. (2039), *Chaos Engineering: System Resiliency in Practice*, 2nd ed., O'Reilly.

### Discussion Questions

1. A BIA identifies an RTO of 5 minutes for the EHR. What does this RTO require architecturally, and what is the cost implication?
2. A tabletop exercise reveals that the incident response team lead is unreachable because their phone number in the plan is three years out of date. How should the plan maintenance process prevent this?
3. Chaos engineering in a healthcare production environment raises ethical concerns. Where should the line be drawn?

---

## Lecture 9: Ethics and Professional Responsibility in IT Governance

### The Expanding Ethical Frontier

IT governance in 2040 confronts ethical questions that the profession barely recognised in 2020. The decisions made by governance bodies — what data to collect, what AI models to deploy, what surveillance technologies to implement, what environmental impact to accept — have consequences that extend far beyond the organisation's balance sheet. Key ethical domains:

- **AI Ethics and Algorithmic Fairness**: If Yggdrasil Health's AI diagnostic model was trained on a dataset that underrepresents certain demographic groups, its accuracy for those groups may be lower — a governance failure with medical consequences. The EU AI Act requires conformity assessments for high-risk AI systems, including bias testing and human oversight mechanisms.
- **Surveillance and Employee Monitoring**: Remote work technologies enable granular employee monitoring — keystroke logging, webcam snapshots, location tracking. Governance must decide: what monitoring is proportionate to legitimate business needs, and what crosses into privacy violation?
- **Environmental Sustainability**: IT infrastructure accounts for 3-4% of global greenhouse gas emissions (2040 estimate). Governance must consider: are we selecting cloud regions based on grid carbon intensity? Are we rightsizing workloads or leaving idle resources consuming energy? Are we extending hardware refresh cycles to reduce e-waste?
- **Digital Colonialism**: When a global technology platform deploys in a developing nation without adapting to local legal frameworks, cultural norms, or data sovereignty requirements, it engages in a form of digital colonialism. The 2040 IT governance professional considers these impacts.

### Ethics as Governance, Not Afterthought

Organisations that treat ethics as a public relations function — a "statement of values" on the website, disconnected from operational decisions — are exposed to ethics failures. The 2040 governance approach integrates ethics structurally: an **Ethics Committee** (or subcommittee of the Board) that reviews high-risk AI deployments, surveillance technology procurement, and data-sharing agreements; an **Ethics Impact Assessment** process modelled on the Data Protection Impact Assessment (DPIA) that must be completed before deploying systems with significant ethical implications; and a **Whistleblower Protection Programme** that ensures employees who raise ethical concerns are protected from retaliation.

### Required Reading

- IEEE, *Ethically Aligned Design: A Vision for Prioritising Human Well-being with Autonomous and Intelligent Systems*, 3rd Ed. (2040).
- EU High-Level Expert Group on AI, *Ethics Guidelines for Trustworthy AI*, updated 2040.
- Floridi, L. (2039), *The Ethics of Artificial Intelligence: Principles, Challenges, and Opportunities*, Oxford.

### Discussion Questions

1. Yggdrasil Health's AI diagnostic model performs 4% worse for patients over 75. Is this an IT governance issue, a medical ethics issue, or both? Who should decide whether to deploy the model?
2. An employee monitoring system flags a remote worker as "idle" for 30% of their shift. The system recommends disciplinary action. What governance controls should have been in place before this system was deployed?
3. What is the difference between "ethics washing" (a PR statement) and genuine ethics governance? How would you detect the former?

---

## Lecture 10: Quantum Readiness and Emerging Technology Governance

### Governing What Has Not Yet Arrived

Quantum computing presents a unique governance challenge: the threat (the ability to break current public-key cryptography) is not yet realised, but the preparation (migrating to post-quantum cryptography) must begin years before the threat materialises. The "harvest now, decrypt later" scenario — adversaries capturing encrypted data today for decryption when CRQCs arrive — means that data with long-term sensitivity must be protected with PQC now. The governance question: which data qualifies, and who decides?

Emerging technology governance more broadly requires the organisation to: **scan** the technology horizon for developments that could disrupt or enhance the business, **assess** each technology's implications (opportunity, risk, compliance, ethical), **decide** whether to monitor, experiment, or adopt, and **govern** the adoption with appropriate controls. The 2040 horizon includes: neuromorphic computing, DNA data storage, ambient computing (invisible interfaces), brain-computer interfaces in workplace settings, and autonomous AI agents with delegated authority.

### The Governance Precautionary Principle

Applied to emerging technology: the absence of evidence of harm is not evidence of absence of harm. When deploying a technology whose long-term effects are unknown — a novel AI architecture, an experimental biometric identification system — the governance body should require: a limited-scale trial with defined success and safety criteria, continuous monitoring for unexpected effects, a predefined kill switch (ability to roll back), and an independent ethical review before full-scale deployment.

### Required Reading

- NIST, *Post-Quantum Cryptography: Governance and Migration Planning*, SP 1800-38 (2040).
- World Economic Forum, *Governance of Emerging Technologies*, 2040 Annual Report.
- Greenberg, A. (2039), *Sandworm: A New Era of Cyberwar and the Hunt for the Kremlin's Most Dangerous Hackers*, 2nd ed., Doubleday.

### Discussion Questions

1. Yggdrasil Health holds genomic data with multi-generational sensitivity. Should it migrate to PQC now, or wait until NIST standards are more mature?
2. A vendor proposes deploying an autonomous AI agent that can approve IT change requests without human review. Design the governance conditions under which this would be acceptable.
3. What is the governance precautionary principle, and when should it be overridden by the innovation imperative?

---

## Lecture 11: Building a Compliance Programme — The CISO's Operating Model

### The Compliance Operating Model

A compliance programme is the operational machinery that ensures the organisation meets its regulatory obligations. The 2040 programme consists of eight components, aligned with the US Department of Justice's *Evaluation of Corporate Compliance Programs* (updated 2040) and the ISO 37301:2040 Compliance Management Systems standard:

1. **Leadership and Culture**: Tone from the top. The CEO and Board publicly and consistently communicate that compliance is non-negotiable.
2. **Risk Assessment**: An annual compliance risk assessment identifying the regulations applicable to the organisation, the risks of non-compliance, and the controls in place.
3. **Policies and Procedures**: The hierarchy of policy, standard, guideline, and procedure, translated into machine-enforceable rules where possible.
4. **Training and Awareness**: Role-based compliance training. Developers receive secure coding training. Managers receive ethics and reporting training. All staff receive annual data privacy refreshers.
5. **Monitoring and Testing**: Continuous automated compliance monitoring (cloud configuration scanning, access recertification, policy-as-code enforcement) plus periodic manual testing (penetration tests, social engineering tests, tabletop exercises).
6. **Reporting and Investigation**: A confidential reporting mechanism (whistleblower hotline). Clear procedures for investigating reported concerns, with protections against retaliation.
7. **Enforcement and Discipline**: Consistent consequences for policy violations, regardless of the violator's seniority. Inconsistent enforcement undermines the entire programme.
8. **Continuous Improvement**: The compliance programme is not static. Audit findings, incident root causes, regulatory changes, and industry benchmarks feed a continuous improvement cycle.

### The Compliance Calendar

The 2040 compliance team maintains a **compliance calendar** — a 12-month rolling schedule of all compliance activities:

| Month | Activity | Owner |
|-------|----------|-------|
| January | Annual compliance risk assessment | CISO |
| February | HIPAA Security Rule controls self-assessment | Compliance Officer |
| March | Penetration test (external) | Security Engineering |
| April | SOC 2 Type II audit fieldwork | External Auditor |
| May | GDPR DPIA review and update | DPO |
| June | Tabletop exercise: ransomware scenario | CISO |
| July | Access recertification campaign (all systems) | IAM Team |
| August | Policy annual review (all policies) | Policy Owners |
| September | ISO 27001 surveillance audit | External Auditor |
| October | Security awareness training (all staff) | Security Training |
| November | Vendor risk reassessment (high-risk vendors) | TPRM Team |
| December | Board cyber risk report | CISO |

### Required Reading

- ISO 37301:2040, *Compliance Management Systems — Requirements with Guidance for Use*.
- US Department of Justice, Criminal Division, *Evaluation of Corporate Compliance Programs*, updated 2040.
- ISACA, *CGEIT Review Manual*, 15th Edition (2040), Domain 3: Benefits Realisation.

### Discussion Questions

1. The DOJ evaluates compliance programmes partly on whether the organisation "has a culture of compliance." How would you demonstrate this to a regulator?
2. Yggdrasil Health's access recertification campaign reveals 340 accounts that should have been disabled (former employees, expired contractors). What does this finding indicate about the compliance programme's maturity?
3. Design the compliance calendar for Yggdrasil Health, considering its obligations under GDPR, HIPAA, DORA, and the EU AI Act.

---

## Lecture 12: The Governance Professional — Synthesis and the Long View

### The Rounding of the Circle

This final lecture integrates the threads of the course: governance as the constitution of IT decision-making, compliance as the operationalisation of regulatory obligation, risk governance as the board's lens on technology uncertainty, audit as independent verification, privacy as a fundamental design constraint, supply chain security as the defence of the extended enterprise, business continuity as the commitment to resilience, ethics as the conscience of technology deployment, and emerging technology governance as preparation for what comes next.

The 2040 IT governance professional occupies a unique position in the organisation: neither purely technical nor purely legal, fluent in both Risk = Likelihood × Impact and "the board's fiduciary duty under §172 of the Companies Act requires due consideration of cybersecurity risk," capable of translating between the engineer who says "we need to upgrade the TLS cipher suite" and the board member who needs to hear "this protects us from a €15M regulatory fine and preserves patient trust."

### The Heathen Reflection — The Law-Speaker's Burden

In the Old Norse Thing (assembly), the *lǫgsǫgumaðr* (law-speaker) stood at the Law Rock and recited the laws from memory. He did not create the laws; he preserved them, interpreted them, and ensured the community operated within their bounds. When a dispute arose, the community looked to the law-speaker not because he wielded executive power but because he represented the accumulated legal wisdom of the community — the institutional memory of right process and due restraint.

The 2040 IT governance professional occupies the law-speaker's position. They do not command the servers or write the code. They do not set business strategy or allocate budget. But when questions arise — "Can we use this patient data for AI training?" "Should we pay the ransomware demand?" "Must we report this incident to the regulator?" "Is this vendor's security posture acceptable?" — the organisation turns to them. Their authority derives not from hierarchical position but from the demonstrated integrity of their judgement, the depth of their regulatory knowledge, and their willingness to speak uncomfortable truths to power.

The Norns' final gift to the governance professional is the understanding that governance is not a destination but a practice — Urðr (the compliance history that has been woven), Verðandi (the regulatory obligations becoming due right now), and Skuld (the emerging risks and regulations that shall come). The professional who embraces this rhythmic, iterative, never-finished quality of governance will find satisfaction not in completion but in the craft itself: the well-written policy, the clean audit report, the board presentation that actually changes minds, the compliance programme that bends but does not break under regulatory scrutiny.

### Required Reading

- ISACA, *State of IT Governance 2040*, Global Survey Report.
- Allen, J. (2039), *The CISO Evolution: Business Knowledge for Cybersecurity Executives*, Wiley.
- Þórisdottir, R. (2039), *The Digital Thing: Governance in the Age of Algorithmic Accountability*, University of Yggdrasil Press, Ch. 12, "The Law-Speaker's Rock."

### Discussion Questions

1. What distinguishes a great IT governance professional from a competent one? Identify at least three specific capabilities that are difficult to certify but essential in practice.
2. The law-speaker metaphor suggests that governance authority derives from knowledge and integrity, not hierarchical power. Is this realistic in a corporate environment?
3. If you were building an IT governance function from scratch at a 500-person healthtech startup, what would you prioritise — and what would you defer?

---

## Final Examination Preparation

The final examination for IT401 consists of two components:

### Component A: Written Examination (60%)

Choose **four** of the following eight essay questions.

1. Critically evaluate COBIT 2040 as a governance framework for a healthcare organisation. Which governance objectives are most relevant, which are least, and what adaptations would you make for the healthcare context?

2. Yggdrasil Health experiences a data breach: an unencrypted laptop containing PHI of 15,000 patients is stolen from a physician's car. Analyse the regulatory obligations under both GDPR and HIPAA. What notifications are required, to whom, and within what timeframes? What governance failures does this incident reveal?

3. Design the board-level cyber risk reporting framework for Yggdrasil Health. Include: the reporting cadence, the dashboard structure (at least five metrics), the method for quantifying cyber risk in financial terms, and how the board should evaluate the CISO's performance.

4. The EU AI Act classifies Yggdrasil Health's AI diagnostic module as "high-risk." Produce the conformity assessment documentation required, including: risk management system description, data governance measures, technical documentation requirements, transparency provisions, and human oversight mechanisms.

5. The Yggdrasil Health Board has directed the CISO to implement an employee monitoring system (keystroke logging, application usage tracking, webcam snapshots every 10 minutes) for all remote employees. Write the governance analysis: identify the ethical concerns, regulatory implications (GDPR Article 88, employee monitoring), proportionality assessment, and alternative approaches.

6. Yggdrasil Health is acquiring a telemedicine startup. Design the IT due diligence scope covering: cybersecurity posture assessment, regulatory compliance verification (HIPAA, GDPR), technology architecture evaluation, third-party risk inheritance, and integration risk analysis.

7. Write a complete IT policy for Yggdrasil Health's use of generative AI tools by employees. Address: acceptable use, data classification restrictions (no PHI in prompts), model approval process, output review requirements, and consequences for policy violations. The policy must be enforceable through technical controls (policy-as-code).

8. Compare the roles of internal audit, external audit, and regulatory inspection in IT governance. How do they differ in objectives, scope, authority, and reporting lines? How should the CISO engage with each?

### Component B: Simulated Regulatory Audit (40%)

Students participate in a simulated regulatory audit where they represent Yggdrasil Health responding to an information request from the Norwegian Data Protection Authority (Datatilsynet) following a patient complaint about AI-driven diagnostic decisions. Students must:

1. Present the governance framework for AI systems at Yggdrasil Health
2. Provide evidence of conformity assessment for the AI diagnostic module
3. Demonstrate the human oversight mechanism for AI decisions
4. Explain the data protection impact assessment (DPIA) for the AI system
5. Respond to follow-up questions from a panel of auditors (faculty)

### Grading Rubric

| Criterion | Weight | Excellent (A) | Good (B) | Adequate (C) | Insufficient (D/F) |
|-----------|--------|---------------|----------|--------------|-------------------|
| Regulatory knowledge | 25% | Precise and comprehensive; correct citations and interpretations | Minor errors; mostly accurate | Significant gaps | Fundamental misunderstandings |
| Governance design | 25% | Structures are specific, proportionate, and evidence-based | Good design; some abstraction | Generic; lacks operational detail | Governance components missing or ineffective |
| Risk and ethics integration | 25% | Quantitative risk where appropriate; ethics considered as first-order concern | Risk considered; ethics acknowledged | Superficial treatment of risk/ethics | Risk and ethics ignored |
| Communication to leadership | 25% | Persuasive, clear, appropriate for board/regulator audience | Clear but some presentation issues | Disorganised; too technical or too vague | Inappropriate for intended audience |

---

## Course Resources

### Primary Textbooks
- ISACA (2040), *COBIT 2040: Governance and Management Objectives*.
- Þórisdottir, R. (2039), *The Digital Thing: Governance in the Age of Algorithmic Accountability*, University of Yggdrasil Press.
- ISO/IEC 38500:2040, *Governance of IT for the Organisation*.

### Key Regulations (current 2040 editions)
- EU General Data Protection Regulation (GDPR)
- EU Digital Operational Resilience Act (DORA)
- EU AI Act (2036)
- US HIPAA Security Rule, 2040 Update
- US CIRCIA, 2039 Update
- EU NIS3 Directive (2037)
- EU CSRD (2039)

### Supplemental Texts
- Allen, J. (2039), *The CISO Evolution*, Wiley.
- Fitzgerald, T. (2039), *Information Security Policy: A Practical Guide*, 3rd ed., CRC Press.
- ISO 31000:2040, *Risk Management — Guidelines*.
- ISO 37301:2040, *Compliance Management Systems*.
- ISO 22301:2040, *Business Continuity Management Systems*.
- NIST Cybersecurity Framework (CSF) 2.0.

### Tools
- **GRC Platforms**: ServiceNow GRC, Archer, OneTrust, LogicGate
- **Policy-as-Code**: OPA/Rego, AWS SCPs, Azure Policy, Sentinel
- **Audit Management**: AuditBoard, TeamMate, HighBond
- **Vendor Risk**: SecurityScorecard, BitSight, UpGuard, OneTrust Vendorpedia
- **Compliance Automation**: Drata, Vanta, Secureframe

---

*ᚦ — Þurs er kvenna kvöl.* The thorn that protects through discipline.

*Course designed and maintained by the Faculty of Information Technology, University of Yggdrasil, 2040.*
