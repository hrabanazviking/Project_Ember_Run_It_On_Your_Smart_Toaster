# CS407: Capstone Project II
## Bachelor of Science in Computer Science — University of Yggdrasil, 2040

**Credits:** 4  
**Prerequisites:** CS406 (Capstone Project I), CS405 (Research Methods in CS)  
**Description:** The execution semester of the year-long capstone. Students move from design documents and prototypes to full implementation, comprehensive testing, production deployment, public demonstration, and technical writeup. Emphasis on software engineering discipline, quality assurance, security hardening, observability, documentation, and the ethical responsibilities of shipping code that affects real users. The capstone culminates in a public defense before the faculty and an industry panel.

**Instructor:** Dr. Sigríðr Vébjörn, M.Eng. (MIT), Principal Engineer, Yggdrasil Systems  
**Office:** Vébjörn Lab, Room 512-C  
**Seminar:** Tuesdays and Thursdays 10:00–12:00, Mímir Hall  
**Lab:** Fridays 14:00–17:00, Open Compute Cluster  

---

## Lectures

---

ᚠ **Lecture 1: Project Implementation Architecture and Technical Debt Management**

**Course:** CS407 — Capstone Project II  
**Degree:** Bachelor of Science in Computer Science, 2040

---

### Overview

The transition from prototype to production-quality implementation is where most capstone projects falter. A working demo is not a working system. This lecture frames the implementation phase as an exercise in architectural discipline: making decisions today that will not haunt you during the final demo. We examine the concept of technical debt — introduced by Ward Cunningham in 1992, refined by Martin Fowler into the Technical Debt Quadrant, and reimagined for the 2040s as a multi-dimensional liability space that includes not just code quality but also security posture, documentation gaps, test coverage, operational runbooks, and ethical oversight.

### Key Topics

- **The Prototype Trap:** Why demos lie. A prototype optimizes for visible functionality; production code optimizes for correctness, maintainability, observability, and failure tolerance. The sunk-cost fallacy of continuing with prototype code. When to rewrite versus when to refactor. The 2040 heuristic: if your prototype's test coverage is below 40%, treat it as a specification document, not a foundation.
- **Architecture Decision Records (ADRs):** Every significant architectural choice must be documented with context, decision, consequences, and reversal criteria. We examine the Nygard format and the University of Yggdrasil's own YGG-ADR template, which adds an "Ethical Implications" section. Students must maintain an ADR log throughout the capstone; it becomes part of the final assessment.
- **Technical Debt Taxonomy:** Deliberate vs. inadvertent debt; prudent vs. reckless debt. But by 2040, we recognize additional dimensions: AI-generated debt (code produced by LLMs that passes tests but fails edge cases), quantum-hybrid debt (classical-quantum interfaces that are hard to debug), and ethical debt (design choices that embed bias or reduce user autonomy). Students learn to classify and quantify their debt using the Yggdrasil Technical Debt Calculator (YTDC), which estimates remediation effort in person-hours.
- **Modularity and Interface Contracts:** The capstone system must be decomposable. We review module boundaries, API contracts (OpenAPI, gRPC proto files, Rust traits), and the principle of information hiding. In 2040, this extends to AI agent boundaries: if your capstone includes an LLM-powered component, its prompt template is an interface contract, and version changes to the model constitute breaking changes.
- **Incremental Delivery Milestones:** Rather than a single "implementation phase," students deliver vertical slices every two weeks. Each slice must be deployable, testable, and demonstrable. The lecture presents the "Walking Skeleton" pattern (Cockburn) and the "Tracer Bullet" approach (Hunt & Thomas), adapted for 2040 hybrid architectures.

### Required Reading

- Cunningham, W. (1992). "The WyCash Portfolio Management System." *Addendum to the Proceedings of OOPSLA '92*.
- Fowler, M. (2019). "Technical Debt Quadrant." martinfowler.com/bliki/TechnicalDebtQuadrant.html.
- Nygard, M. (2011). *Documenting Architecture Decisions*. O'Reilly.
- Vébjörn, S. (2038). "AI-Generated Code Liability: A New Dimension of Technical Debt." *UoY Technical Report* TR-2038-14.
- Cockburn, A. (2004). *Crystal Clear: A Human-Powered Methodology for Small Teams*. Addison-Wesley. (Chapters 3–5)

### Discussion Questions

1. Is technical debt always bad? Under what conditions is prudent, deliberate debt the right choice for a capstone timeline?
2. How do you quantify the cost of "ethical debt" — design decisions that may cause harm if left unaddressed?
3. If an AI pair programmer generates 60% of your codebase, who owns the technical debt it introduces? How do you audit AI-generated code for hidden liabilities?

### Practice Problems

- Write an ADR for a significant architectural decision in your capstone project. Include context, decision, consequences, and an explicit ethical implications section.
- Run YTDC on your CS406 prototype. Categorize each debt item by type and estimate remediation effort. Present a debt repayment schedule for the semester.

---

ᚢ **Lecture 2: Test-Driven Development and Verification Strategies at Scale**

**Course:** CS407 — Capstone Project II  
**Degree:** Bachelor of Science in Computer Science, 2040

---

### Overview

Testing is not a phase; it is a continuous discipline woven into the fabric of implementation. This lecture moves beyond introductory unit testing into the full spectrum of verification strategies that production systems demand in 2040. We cover property-based testing, mutation testing, formal verification of critical components, differential testing for AI-powered features, and the emerging practice of "adversarial test-driven development" — writing tests that actively attempt to break your system in ways a malicious actor might.

### Key Topics

- **The Testing Pyramid, Revisited:** The classic pyramid (unit → integration → E2E) remains valid, but 2040 adds new layers. Below unit tests: "property tests" (Hypothesis, QuickCheck) that generate thousands of random inputs to catch edge cases. Above E2E tests: "chaos tests" that introduce network partitions, hardware failures, and model drift. Between integration and E2E: "contract tests" (Pact) that verify service boundaries independently.
- **Property-Based Testing:** Instead of example-based tests, define properties that must always hold (e.g., "sorting never changes the multiset of elements"). The test framework generates random inputs and shrinks failing cases to minimal counterexamples. We use Hypothesis for Python and proptest for Rust. Critical for capstones with algorithmic components: if you claim your distributed consensus implementation is safe, prove it with properties, not just examples.
- **Mutation Testing:** Are your tests actually testing anything? Mutation testing (using tools like cargo-mutants or mutmut) introduces small bugs into your code and checks if your test suite catches them. A mutation score below 80% indicates weak tests. The lecture demonstrates how mutation testing reveals "false confidence" in coverage metrics.
- **Formal Verification of Critical Paths:** For the most critical components (security checks, financial calculations, safety-critical logic), unit tests are insufficient. We introduce lightweight formal methods: Dafny for verified methods, Rust's refinement types via flux, and the practice of writing "ghost code" that proves invariants at compile time. Students identify one critical path in their capstone and apply a lightweight verification technique.
- **Differential Testing for AI Components:** If your capstone includes an LLM or neural component, traditional unit tests are impossible (the output is non-deterministic). Differential testing compares outputs across model versions, prompts, and temperature settings. "Metamorphic testing" defines relations that must hold between inputs and outputs (e.g., "rephrasing the question should not change a factual answer's truth value").
- **Coverage as Necessary but Insufficient:** The capstone requires ≥90% code coverage, but this lecture explains why coverage is a guardrail, not a goal. A 100%-covered codebase with weak assertions is less trustworthy than an 80%-covered codebase with property tests and mutation-verified assertions.

### Required Reading

- Beck, K. (2002). *Test-Driven Development: By Example*. Addison-Wesley. (Chapters 1–8)
- MacIver, D. & Hatfield-Dodds, Z. (2019). "Hypothesis: A New Approach to Property-Based Testing." *Journal of Open Source Software*, 4(43), 1891.
- Offutt, A. J. & Untch, R. H. (2001). "Mutation Testing for the New Century." *Advances in Computing*, 65, 1–26.
- Vébjörn, S. & Hrafnsson, T. (2039). "Adversarial TDD: Writing Tests That Think Like Attackers." *ACM SIGSOFT Software Engineering Notes*, 44(2), 18–25.
- Leino, K. R. M. (2010). "Dafny: An Automatic Program Verifier for Functional Correctness." *LPAR-16*, 348–370.

### Discussion Questions

1. If your test suite achieves 95% coverage but never catches a bug until production, what does that tell you about your testing philosophy?
2. How do you test a system component whose output is inherently probabilistic, such as a neural recommender or an LLM summarizer?
3. Is formal verification worth the time investment for a capstone project? Under what conditions does the cost-benefit analysis favor formal methods over extensive testing?

### Practice Problems

- Implement property-based tests for a core data structure in your capstone using Hypothesis or proptest. Define at least three invariants and run 10,000 iterations.
- Run mutation testing on your CS406 test suite. Calculate your mutation score and fix the "surviving mutants" — the bugs your tests failed to catch.

---

ᚦ **Lecture 3: Continuous Integration, Delivery, and Deployment Pipelines**

**Course:** CS407 — Capstone Project II  
**Degree:** Bachelor of Science in Computer Science, 2040

---

### Overview

A capstone project that lives only on a student's laptop is not a capstone — it is a homework assignment. This lecture treats CI/CD not as DevOps trivia but as a core software engineering competency. By 2040, CI/CD has evolved beyond Jenkins and GitHub Actions into multi-environment, AI-assisted deployment pipelines that include automated security scanning, compliance checking, rollback orchestration, and canary analysis. Students build a production-grade pipeline for their capstone that deploys to the University of Yggdrasil's staging environment and, optionally, to public cloud infrastructure.

### Key Topics

- **CI/CD as Engineering Discipline:** The distinction between continuous integration (merge often, verify always), continuous delivery (always deployable), and continuous deployment (automatic to production). For capstones, we target continuous delivery as the minimum standard: every merge to main must produce an artifact that could be deployed.
- **Pipeline Architecture (2040):** A modern pipeline has stages: (1) Lint/Format, (2) Build, (3) Unit Tests, (4) Integration Tests, (5) Security Scan (SAST, DAST, dependency vulnerability check), (6) Compliance Check (license audit, privacy policy diff), (7) Artifact Build, (8) Deploy to Staging, (9) Smoke Tests, (10) Canary Deploy (if applicable). The lecture walks through each stage with concrete tool examples: GitHub Actions, Earthly for reproducible builds, Trivy for container scanning, and Sigstore for artifact signing.
- **Reproducible Builds and Hermeticity:** A build is reproducible if running it twice produces bit-identical outputs. Hermetic builds ensure that all dependencies are pinned and the build environment is controlled. We use Nix flakes and Earthly to achieve hermeticity. For capstones, this means: no "it works on my machine" — the CI pipeline is the canonical build environment.
- **Environment Parity and Configuration Management:** The twelve-factor app methodology (still relevant in 2040) mandates that configuration lives in environment variables, not code. We review modern approaches: sealed secrets (Bitnami Sealed Secrets), external secret operators (ESO), and the University of Yggdrasil's own YGG-VAULT system for student projects. Students must manage at least three environments: local dev, staging (UoY cluster), and production (optional public cloud).
- **Rollback and Disaster Recovery:** Every deployment must be reversible within 60 seconds. We implement blue-green deployments and feature flags (using Unleash or Flagsmith). The lecture presents the "circuit breaker" pattern for graceful degradation and the "bulkhead" pattern for isolating failures. Capstone requirement: demonstrate a clean rollback during the final demo.
- **AI-Assisted Deployment Validation:** By 2040, deployment pipelines include AI agents that analyze logs, compare metrics against baselines, and make rollback recommendations. We review the VERÐANDI deployment observer — a lightweight agent that monitors capstone deployments and flags anomalies.

### Required Reading

- Humble, J. & Farley, D. (2010). *Continuous Delivery: Reliable Software Releases through Build, Test, and Deployment Automation*. Addison-Wesley. (Chapters 1–5)
- Wiggins, A. (2017). "The Twelve-Factor App." twelvefactor.net.
- Farcic, V. (2022). *Reproducible Builds with Earthly*. Manning.
- Dolstra, E. et al. (2004). "Nix: A Safe and Policy-Free System for Software Deployment." *LISA*, 79–92.
- Yggdrasil Systems Team (2039). "YGG-VAULT: Secret Management for Student Capstones." *UoY Technical Report* TR-2039-03.

### Discussion Questions

1. What is the minimum viable CI/CD pipeline for a capstone project? At what point does adding more stages create diminishing returns?
2. If a security scan flags a dependency vulnerability with no available patch, what are your options? How do you document the risk?
3. How do you maintain environment parity when one team member develops on ARM (Apple Silicon) and the deployment target is x86_64 Linux?

### Practice Problems

- Build a CI/CD pipeline for your capstone with at minimum: build, test, security scan, and staging deployment stages. Configure it to trigger on every pull request and every merge to main.
- Implement a feature flag in your capstone using an open-source feature flag service. Demonstrate toggling a feature in staging without redeploying.

---

ᚬ **Lecture 4: Performance Engineering: Profiling, Optimization, and Benchmarking**

**Course:** CS407 — Capstone Project II  
**Degree:** Bachelor of Science in Computer Science, 2040

---

### Overview

"Premature optimization is the root of all evil," Knuth warned. But late optimization is the root of all missed deadlines. This lecture teaches evidence-based performance engineering: measure first, hypothesize second, optimize third, validate always. We cover systematic profiling (CPU, memory, I/O, network), benchmarking methodology (statistical rigor, avoiding common pitfalls), and the unique challenges of optimizing hybrid classical-quantum and AI-accelerated workloads that are increasingly common in 2040 capstones.

### Key Topics

- **The Measurement Imperative:** Before touching code, establish baselines. Define performance requirements in terms of latency percentiles (p50, p95, p99), throughput (requests/second), and resource efficiency (cost per request). The lecture introduces the "USE Method" (Utilization, Saturation, Errors) for resource analysis and the "RED Method" (Rate, Errors, Duration) for service-level analysis.
- **CPU Profiling:** Flame graphs (Brendan Gregg), sampling profilers (perf, samply), and instrumentation profilers (coz for causal profiling). Understanding the difference between wall time and CPU time. Identifying "hot paths" versus "cold paths that block hot paths." For Rust capstones: cargo-flamegraph and samply. For Python: py-spy and scalene. For C++: perf and tracy.
- **Memory Profiling and Allocation Tracking:** Memory leaks, heap fragmentation, and cache inefficiency. Tools: heaptrack, valgrind (still relevant), and Rust's dhat for detailed allocation analysis. The lecture covers allocator-aware design: using arena allocators for short-lived objects, object pools for frequently allocated types, and zero-copy architectures where possible.
- **Benchmarking with Statistical Rigor:** The Criterion.rs framework for Rust and pytest-benchmark for Python. Key principles: run enough iterations to achieve statistical significance, report confidence intervals, control for environmental noise (CPU frequency scaling, thermal throttling), and always compare against a baseline. The lecture warns against common benchmarking sins: optimizing the compiler away, measuring debug builds, and reporting mean without variance.
- **Optimizing AI/ML Inference:** If your capstone includes neural inference, performance optimization spans model quantization (INT8, INT4), operator fusion, batching strategies, and hardware-specific kernels (TensorRT, ONNX Runtime, Core ML). We cover the "roofline model" for understanding whether a kernel is memory-bound or compute-bound.
- **Quantum-Classical Hybrid Optimization:** For capstones with quantum components (Qiskit, PennyLane), profiling extends to quantum circuit depth, gate fidelity, and queue wait times on quantum hardware. The lecture presents the "Variational Quantum Eigensolver" as a case study in hybrid profiling: classical optimizers call quantum circuits, and the latency is dominated by quantum execution.

### Required Reading

- Knuth, D. E. (1974). "Structured Programming with go to Statements." *ACM Computing Surveys*, 6(4), 261–301.
- Gregg, B. (2020). *Systems Performance: Enterprise and the Cloud* (2nd ed.). Addison-Wesley. (Chapters 5–7)
- Gregg, B. (2016). "The Flame Graph." *ACM Queue*, 14(2), 10–15.
- Mytkowicz, T. et al. (2009). "Producing Wrong Data Without Doing Anything Obviously Wrong!" *ASPLOS*, 265–276.
- Woo, S. C. et al. (1995). "The Memory Behavior of Cache-Conscious Programs." *ASPLOS*, 195–206.

### Discussion Questions

1. Why is the mean a poor metric for latency benchmarking? What does a high p99/p50 ratio tell you about your system's behavior under load?
2. How do you distinguish between "optimization" (making the code faster) and "performance engineering" (making the system meet its requirements)? When is the latter preferable?
3. If your profiler shows that 80% of CPU time is spent in a library you don't control, what strategies can you employ?

### Practice Problems

- Profile your capstone application under realistic load. Generate a flame graph, identify the top three hot functions, and propose optimizations. Implement at least one optimization and benchmark the before/after with statistical rigor.
- Write a microbenchmark for a critical algorithm in your capstone using Criterion.rs or pytest-benchmark. Ensure it reports confidence intervals and includes a regression test that fails if performance degrades by more than 5%.

---

ᚱ **Lecture 5: Security Hardening: Threat Modeling, Static Analysis, and Penetration Testing**

**Course:** CS407 — Capstone Project II  
**Degree:** Bachelor of Science in Computer Science, 2040

---

### Overview

Security is not a feature you add at the end; it is a property you design in from the beginning. This lecture treats security as an engineering discipline with repeatable methodologies. We cover threat modeling (STRIDE, attack trees), static and dynamic analysis, dependency scanning, secrets management, and the 2040-specific challenges of securing AI-powered systems against prompt injection, model extraction, and adversarial input attacks.

### Key Topics

- **Threat Modeling with STRIDE and Attack Trees:** Every capstone must have a documented threat model. We review the STRIDE methodology (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) and construct attack trees for sample capstone architectures. Students produce a threat model for their own project, identifying at least five realistic threats and their mitigations.
- **Static Application Security Testing (SAST):** Tools like Semgrep, CodeQL, and Rust's cargo-audit scan source code for known vulnerability patterns. The lecture covers common vulnerability classes: injection flaws (SQL, command, template), buffer overflows (less common in memory-safe languages but still relevant via unsafe blocks), insecure deserialization, and broken authentication. Capstone requirement: zero high-severity SAST findings at submission.
- **Dynamic Application Security Testing (DAST):** Running the application and probing it for vulnerabilities. Tools like OWASP ZAP and Burp Suite. The lecture demonstrates how to integrate DAST into the CI pipeline, running automated scans against the staging environment after each deployment.
- **Dependency and Supply Chain Security:** The xz utils backdoor (2024) demonstrated that supply chain attacks are not theoretical. We cover Software Bill of Materials (SBOM) generation, dependency pinning, checksum verification, and vulnerability databases (OSV, NVD). For Rust: cargo-audit. For Python: pip-audit and Safety. For JavaScript: npm audit. Capstone requirement: generate an SBOM and verify all dependencies.
- **Securing AI-Powered Components:** Capstones with LLM integrations face unique threats. Prompt injection: an attacker embeds malicious instructions in user input that override system prompts. Model extraction: an attacker crafts queries to reconstruct the model's training data or parameters. Jailbreaking: bypassing safety filters. We review defense strategies: input/output filtering, prompt hardening, rate limiting, and the "defense in depth" approach of combining multiple mitigations.
- **Secrets Management and Cryptography Hygiene:** No secrets in code. No secrets in logs. No secrets in environment variables that get dumped. We review the University of Yggdrasil's secrets management policy and demonstrate proper use of HashiCorp Vault, AWS Secrets Manager, or the University's YGG-VAULT system. The lecture covers cryptographic best practices: use established libraries (libsodium, Ring), don't roll your own crypto, prefer AEAD modes, and manage key rotation.

### Required Reading

- Shostack, A. (2014). *Threat Modeling: Designing for Security*. Wiley. (Chapters 2–4)
- OWASP Foundation (2023). *OWASP Top 10 for Large Language Model Applications*. owasp.org/www-project-top-10-for-large-language-model-applications/.
- Ladisa, P. et al. (2023). "SoK: Taxonomy of Attacks on Open-Source Software Supply Chains." *IEEE S&P*, 1509–1526.
- Arcanjo, J. (2024). "The xz Backdoor: A Wake-Up Call for Supply Chain Security." *Linux Foundation Blog*.
- Yggdrasil Security Team (2039). "Securing LLM-Integrated Applications: A Practical Guide." *UoY Security Bulletin* SB-2039-07.

### Discussion Questions

1. If your capstone uses an open-source library with a known medium-severity vulnerability that has no patch, what is your responsibility? Do you ship with the vulnerability, remove the feature, or fork and patch yourself?
2. How do you threat-model a system whose behavior is partially determined by a neural network whose decision boundaries you cannot fully enumerate?
3. What is the difference between "security through obscurity" and "defense in depth"? Can they coexist?

### Practice Problems

- Create a threat model for your capstone using STRIDE. Document at least five threats, their risk ratings, and your mitigations. Include one threat related to any AI component.
- Run SAST and DAST scans on your capstone. Fix all high-severity findings and document your reasoning for any risk-accepted medium findings.

---

ᚴ **Lecture 6: Observability: Logging, Metrics, Tracing, and Alerting in Production**

**Course:** CS407 — Capstone Project II  
**Degree:** Bachelor of Science in Computer Science, 2040

---

### Overview

You cannot operate what you cannot observe. Observability — the ability to understand a system's internal state from its external outputs — is a first-class engineering concern in 2040. This lecture moves beyond "print debugging" into structured logging, time-series metrics, distributed tracing, and intelligent alerting. We cover the OpenTelemetry standard, which has become the universal telemetry protocol, and demonstrate how to instrument a capstone system for comprehensive observability.

### Key Topics

- **The Three Pillars of Observability:** Logs (discrete events), metrics (numeric aggregates over time), and traces (request flows across services). In 2040, we add a fourth pillar: "profiles" (continuous performance snapshots). The lecture explains when to use each pillar and how they complement each other. A single user request might generate a trace, emit structured logs at each span, increment latency metrics, and trigger a CPU profile if latency exceeds a threshold.
- **Structured Logging:** Unstructured text logs are archaeological artifacts — interesting to historians, useless to operators. Modern logging uses structured formats (JSON, logfmt) with standardized fields: timestamp (RFC3339), severity (syslog levels), service name, trace ID, span ID, and contextual key-value pairs. We review the University's logging standard (YGG-LOG-2040) and demonstrate implementation in Rust (tracing crate), Python (structlog), and Go (zap/slog).
- **Metrics and Time-Series Databases:** Counter, gauge, histogram, and summary metric types. The lecture covers Prometheus-style exposition, histogram bucket selection, and the challenge of high-cardinality metrics. Students instrument their capstones with application metrics and expose them for scraping.
- **Distributed Tracing:** In a microservices or multi-agent architecture, a single user action traverses multiple services. Distributed tracing (OpenTelemetry, Jaeger, Tempo) assigns each request a trace ID and creates spans for each operation. The lecture demonstrates how to propagate trace context across HTTP/gRPC boundaries and how to use traces to identify latency bottlenecks.
- **Alerting and SLOs:** Alerts should be actionable, specific, and rare. We review the "Symptoms vs. Causes" distinction: alert on user-visible symptoms (error rate spike, latency degradation) rather than internal causes (CPU usage, memory pressure). Introduce Service Level Objectives (SLOs): target error rate < 0.1%, p99 latency < 200ms. Capstone requirement: define at least two SLOs and configure alerts for violation.
- **AI-Assisted Anomaly Detection:** By 2040, observability platforms include ML-based anomaly detection that learns baseline behavior and flags deviations. We review the VERÐANDI anomaly detector, which students can integrate into their capstone observability stack for automatic detection of unusual patterns.

### Required Reading

- Majors, C., Fong-Jones, L., & Miranda, G. (2022). *Observability Engineering: Achieving Production Excellence*. O'Reilly. (Chapters 1–4)
- OpenTelemetry Project (2023). *OpenTelemetry Concepts*. opentelemetry.io/docs/concepts/.
- Beyer, B. et al. (2016). *Site Reliability Engineering: How Google Runs Production Systems*. O'Reilly. (Chapters 2–3)
- Sridharan, C. (2018). *Distributed Systems Observability*. O'Reilly. (Chapters 1–3)
- Yggdrasil Operations Team (2038). "YGG-LOG-2040: Structured Logging Standard for Student Projects." *UoY Operations Manual*.

### Discussion Questions

1. What is the difference between "monitoring" (watching known metrics) and "observability" (exploring unknown unknowns)? When is each appropriate?
2. How do you balance observability overhead (CPU, memory, network) against the value of the telemetry it produces? What telemetry is essential and what is vanity?
3. If your system has a 0.01% error rate that only affects users in a specific geographic region using a specific browser, how does distributed tracing help you discover this?

### Practice Problems

- Instrument your capstone with OpenTelemetry. Emit structured logs, expose Prometheus metrics, and generate distributed traces for multi-service requests.
- Define two SLOs for your capstone and configure alerts (using any alerting system) that trigger when SLOs are at risk of being breached.

---

ᚺ **Lecture 7: Documentation Engineering: API Docs, Runbooks, and Knowledge Architecture**

**Course:** CS407 — Capstone Project II  
**Degree:** Bachelor of Science in Computer Science, 2040

---

### Overview

Code is written once and read a hundred times. Documentation is written once and read a thousand times. Yet documentation remains the most neglected aspect of software engineering. This lecture treats documentation as a first-class engineering artifact with its own quality standards, tooling, and maintenance discipline. We cover API documentation (OpenAPI, Rustdoc), architecture documentation (C4 model, ADRs), operational runbooks, and the 2040 practice of "living documentation" — documentation generated from and verified against code.

### Key Topics

- **Documentation as Code:** Documentation lives in version control, is reviewed in pull requests, and is built in CI. We review tools: Markdown with MkDocs or Docusaurus, Asciidoc for complex documents, and the C4 model for architecture diagrams (using Structurizr or PlantUML). The lecture emphasizes that documentation rot is real: out-of-date docs are worse than no docs. Living documentation approaches (testable code examples, diagram generation from source) combat rot.
- **API Documentation Standards:** REST APIs use OpenAPI 3.1 with auto-generated documentation (Swagger UI, Redoc). gRPC APIs use proto comments and buf-generated docs. Rust APIs use rustdoc with doc-tests. Python uses Sphinx or MkDocstrings. The lecture demonstrates how to write doc comments that serve as both developer reference and user guide, with runnable examples that are tested in CI.
- **Architecture Communication:** The C4 model (Context, Containers, Components, Code) provides a hierarchy of architecture diagrams at different zoom levels. Students create a C4 diagram set for their capstone, showing how their system fits into the broader context, what containers it comprises, and how components interact. The lecture also covers sequence diagrams for critical flows and deployment diagrams for infrastructure.
- **Operational Runbooks:** A runbook is a procedure for responding to an operational event. Good runbooks include: symptoms, impact assessment, diagnosis steps (with specific commands), remediation steps (with rollback procedures), and escalation criteria. The lecture presents the "Google SRE Runbook Template" and has students write runbooks for at least three failure scenarios in their capstone.
- **README as Product Landing:** The README is the first thing users and evaluators see. It should answer: What is this? Who is it for? How do I install it? How do I use it? How do I contribute? The lecture reviews exemplary READMEs and has students rewrite their capstone README to professional standards.
- **Knowledge Management and Handoff:** The final phase of a capstone is knowledge transfer. We review "bus factor" mitigation: no single person should hold critical knowledge. Techniques: pair programming, recorded architecture walkthroughs, decision logs, and "tours" — narrative explanations of how the codebase works.

### Required Reading

- Nygard, M. T. (2017). *Release It! Design and Deploy Production-Ready Software* (2nd ed.). Pragmatic Bookshelf. (Chapters 16–18)
- Brown, S. (2021). *Software Architecture for Developers*. Leanpub. (C4 Model chapters)
- Laloux, F. (2014). *Reinventing Organizations*. Nelson Parker. (On knowledge transparency)
- Google SRE Team (2017). *Site Reliability Engineering*. O'Reilly. (Chapters 8–9 on runbooks)
- Vébjörn, S. (2037). "Living Documentation: Keeping Docs Honest Through Compilation." *UoY Software Engineering Review*, 12(3), 45–58.

### Discussion Questions

1. Why do engineers hate writing documentation? Is the solution better tools, better incentives, or a cultural shift?
2. What is the appropriate level of detail for API documentation? When does comprehensive documentation become noise?
3. If your capstone team has a bus factor of 1 (only one person understands a critical component), what specific actions should you take in the final weeks to reduce this risk?

### Practice Problems

- Rewrite your capstone README to professional standards. Include installation, usage, architecture overview, and contribution guidelines. Have a peer review it for clarity.
- Write a runbook for three failure scenarios in your capstone. Include exact commands, expected outputs, and escalation procedures.

---

ᚾ **Lecture 8: Demo Preparation: Technical Storytelling and Presentation Design**

**Course:** CS407 — Capstone Project II  
**Degree:** Bachelor of Science in Computer Science, 2040

---

### Overview

A brilliant system that cannot be demonstrated is a brilliant system that will not be funded, adopted, or appreciated. The capstone demo is not merely a technical presentation; it is an act of storytelling. This lecture treats the demo as a performance art grounded in engineering reality. We cover narrative structure, live demonstration techniques, backup plans for demo failures, visual design, and the unique challenges of presenting AI-powered systems whose outputs are non-deterministic.

### Key Topics

- **The Narrative Arc of a Technical Demo:** Every great demo follows a story: (1) The Problem — establish stakes and empathy; (2) The Existing Pain — demonstrate why current solutions fail; (3) The Insight — the key idea that makes your solution possible; (4) The Reveal — show the system working; (5) The Deep Dive — briefly explain how it works; (6) The Future — what's next. The lecture analyzes successful tech demos (Steve Jobs' iPhone launch, early Docker demos) and extracts narrative patterns.
- **Live Demo Risk Management:** Live demos fail. Prepare for failure: (a) pre-recorded videos as backup for every live segment; (b) "demo gods" checklist (tested on clean machine, no uncommitted changes, no dependencies on external services); (c) progressive disclosure — start simple, add complexity only if time permits; (d) the "one-click reset" — a script that returns the system to demo-ready state in under 30 seconds.
- **Visual Design for Technical Presentations:** Slide design principles: one idea per slide, minimal text, high-contrast visuals, consistent typography. Tools: Figma for diagrams, Excalidraw for architecture sketches, and the University's YGG-SLIDE template. The lecture covers color theory for data visualization, animation restraint, and accessibility (colorblind-safe palettes, alt text for images).
- **Demonstrating AI Components:** If your capstone includes LLMs, neural networks, or agent systems, live demos are risky because outputs vary. Strategies: (a) seed the model for reproducibility; (b) cache representative outputs; (c) show a "success case" live but have the full range of outputs in a recorded video; (d) be honest about limitations — showing a failure mode and explaining your mitigation builds more credibility than pretending perfection.
- **Handling Q&A:** The Q&A session is where depth is tested. Strategies: repeat the question to ensure understanding; answer directly before elaborating; it's acceptable to say "I don't know, but here's how I would find out"; never bluff. The lecture includes mock Q&A sessions with common faculty and industry panel questions.
- **Accessibility and Inclusion:** Ensure your demo is accessible: live captions, readable font sizes, descriptive audio for visual demonstrations, and consideration for neurodivergent audience members who may process information differently.

### Required Reading

- Gallo, C. (2010). *The Presentation Secrets of Steve Jobs*. McGraw-Hill. (Chapters 1–3)
- Reynolds, G. (2011). *Presentation Zen: Simple Ideas on Presentation Design and Delivery* (2nd ed.). New Riders.
- Tufte, E. R. (2001). *The Visual Display of Quantitative Information* (2nd ed.). Graphics Press. (Chapters 4–5)
- Vébjörn, S. (2039). "Demo-Ready: A Checklist for Live Technical Presentations." *UoY Engineering Communication Guide*.
- Yggdrasil Accessibility Office (2038). "Accessible Technical Presentations: Guidelines for Students." *UoY Accessibility Bulletin* AB-2038-03.

### Discussion Questions

1. Is it ethical to use pre-recorded videos instead of live demos? Where is the line between "risk management" and "misrepresentation"?
2. How do you maintain audience engagement during a deeply technical explanation? What techniques translate complexity without losing accuracy?
3. If a faculty member asks a question you genuinely cannot answer, what is the most professionally credible response?

### Practice Problems

- Storyboard your capstone demo using the six-part narrative arc. Time each section. Ensure the total is under 15 minutes with 5 minutes for Q&A.
- Create a "demo failure backup kit": pre-recorded videos, screenshots, and a printed one-page cheat sheet of key commands and expected outputs.

---

ᛁ **Lecture 9: Maintenance, Refactoring, and Long-Term Code Sustainability**

**Course:** CS407 — Capstone Project II  
**Degree:** Bachelor of Science in Computer Science, 2040

---

### Overview

The final commit is not the end of a system's life; it is the beginning. This lecture addresses the reality that software must be maintained: dependencies update, security vulnerabilities are discovered, operating systems evolve, and user requirements shift. We cover refactoring techniques, dependency management strategies, deprecation policies, and the 2040 challenge of maintaining systems that include AI components whose models become obsolete or whose training data becomes socially unacceptable.

### Key Topics

- **The Four Types of Software Maintenance:** Corrective (fixing bugs), adaptive (responding to environment changes), perfective (improving performance or maintainability), and preventive (addressing technical debt before it becomes critical). The lecture presents data showing that maintenance consumes 60–80% of software lifecycle costs, even for student capstones that are nominally "complete" at graduation.
- **Refactoring Patterns:** Martin Fowler's catalog, updated for 2040. Extract function, replace conditional with polymorphism, introduce parameter object, and the newer "extract AI prompt" pattern — moving hardcoded LLM prompts into versioned template files. The lecture emphasizes that refactoring without tests is reckless; every refactoring must be protected by a comprehensive test suite.
- **Dependency Management and Renovation:** Tools like Dependabot, Renovate, and cargo-update automate dependency updates. But automated updates can introduce breaking changes. The lecture covers the "update cadence" strategy: security patches applied immediately, minor updates applied monthly, major updates planned quarterly. For capstones, students must produce a "handoff document" listing all dependencies, their versions, and known update risks.
- **Model Drift and AI System Maintenance:** For capstones with ML components, maintenance includes monitoring for model drift (data distribution changes), concept drift (the relationship between inputs and outputs changes), and cultural drift (societal norms change, making previously acceptable outputs problematic). The lecture covers monitoring strategies, retraining pipelines, and the "model sunset" process for retiring obsolete AI components.
- **Code Archaeology:** Six months after writing code, you will not remember why you made certain choices. Techniques for future-you: comprehensive commit messages (explaining why, not just what), ADRs for major decisions, inline comments for non-obvious optimizations, and "FIXME" tickets that are actually tracked. The lecture presents the "git blame → commit message → ADR" archaeology workflow.
- **Sunsetting and Deprecation:** Not all code lives forever. Graceful deprecation includes: announcing deprecation timelines, maintaining backward compatibility during transition periods, providing migration guides, and eventually removing the old code. The lecture covers semantic versioning as a communication contract and the challenge of deprecating AI features that users have come to rely on.

### Required Reading

- Fowler, M. (2018). *Refactoring: Improving the Design of Existing Code* (2nd ed.). Addison-Wesley. (Chapters 1–3)
- Glass, R. L. (2001). "Frequently Forgotten Fundamental Facts about Software Engineering." *IEEE Software*, 18(3), 110–112.
- Sculley, D. et al. (2015). "Hidden Technical Debt in Machine Learning Systems." *NeurIPS*, 2503–2511.
- Huyen, C. (2022). *Designing Machine Learning Systems*. O'Reilly. (Chapter 11: Continual Learning)
- Yggdrasil Engineering Team (2039). "Capstone Handoff Guide: Maintaining Student Projects After Graduation." *UoY Internal Document*.

### Discussion Questions

1. Is a capstone project "done" when the semester ends? What ethical obligations do you have to users (if any) who continue to use your system?
2. How do you refactor a codebase that has poor test coverage without introducing regressions? What is the "characterization test" approach?
3. If a foundation model your capstone depends on is updated and its behavior changes in ways that break your application, who is responsible for the fix?

### Practice Problems

- Perform one significant refactoring on your capstone. Ensure all tests pass before and after. Document the refactoring in your ADR log.
- Write a "handoff document" for your capstone: dependencies with versions, known technical debt, maintenance risks, and recommended next steps for a future maintainer.

---

ᛃ **Lecture 10: Ethics in Production: Bias, Safety, and Responsible Deployment**

**Course:** CS407 — Capstone Project II  
**Degree:** Bachelor of Science in Computer Science, 2040

---

### Overview

Shipping code is an act of power. When your system reaches real users, it shapes their behavior, accesses their data, makes decisions that affect their lives, and embeds your values into infrastructure. This lecture addresses the ethical responsibilities of the engineer in production. We cover algorithmic bias, safety engineering for AI systems, privacy-by-design, accessibility as an ethical imperative, and the 2040 frameworks for responsible deployment including the Yggdrasil Ethical Impact Assessment (YEIA).

### Key Topics

- **Algorithmic Bias and Fairness:** Bias can enter at any stage: data collection (sampling bias), feature engineering (proxy variables), model training (optimization for accuracy over fairness), and deployment (feedback loops that amplify existing inequities). We review fairness metrics: demographic parity, equalized odds, calibration, and the impossibility theorems (Kleinberg et al., 2016) showing that these criteria are mutually incompatible in non-trivial cases. The lecture argues that "fairness" is not a technical problem with a technical solution — it is a socio-technical negotiation.
- **AI Safety and Alignment:** For capstones with AI components, safety is not optional. We cover: specification gaming (the AI optimizes the metric but not the intent), reward hacking, distributional shift, and the "instrumental convergence" problem — the observation that most sufficiently capable agents will converge on certain subgoals (self-preservation, resource acquisition) regardless of their terminal goals. The lecture introduces the "red team" practice: deliberately attempting to make your AI system fail in dangerous ways.
- **Privacy by Design and Data Minimization:** The 2040 regulatory landscape (evolved from GDPR, CCPA, and the Global Data Compact of 2031) requires privacy to be built in, not bolted on. Techniques: data minimization (collect only what you need), purpose limitation (use data only for stated purposes), anonymization and differential privacy, and cryptographic privacy (zero-knowledge proofs, homomorphic encryption). Capstone requirement: document your data handling practices in a "Data Processing Impact Assessment."
- **Accessibility as Engineering:** Accessibility is not a feature for a minority — it is a quality indicator for everyone. We review WCAG 3.0 (2040 edition), which extends beyond web content to spatial computing, neural interfaces, and multi-modal interaction. The lecture covers: semantic HTML, keyboard navigation, screen reader compatibility, color contrast, motion sensitivity, and cognitive accessibility (clear language, predictable navigation).
- **The YEIA Framework:** The University of Yggdrasil requires every capstone to complete a Yggdrasil Ethical Impact Assessment. The assessment asks: Who could be harmed by this system? How? What mitigations are in place? Who was consulted? What monitoring ensures ongoing ethical compliance? The lecture walks through a completed YEIA for a sample capstone and provides the template.
- **Whistleblowing and Professional Responsibility:** What do you do if you discover that your capstone partner has bypassed a safety check, falsified test results, or embedded a backdoor? The lecture reviews professional codes of ethics (ACM, IEEE) and the University's Academic Integrity Policy. Ethical obligation trumps team loyalty.

### Required Reading

- Buolamwini, J. & Gebru, T. (2018). "Gender Shades: Intersectional Accuracy Disparities in Commercial Gender Classification." *FAccT*, 1–15.
- Kleinberg, J., Mullainathan, S., & Raghavan, M. (2016). "Inherent Trade-Offs in the Fair Determination of Risk Scores." *arXiv:1609.05807*.
- Amodei, D. et al. (2016). "Concrete Problems in AI Safety." *arXiv:1606.06565*.
- Dwork, C. & Roth, A. (2014). *The Algorithmic Foundations of Differential Privacy*. Now Publishers. (Chapters 1–2)
- Yggdrasil Ethics Board (2039). "Yggdrasil Ethical Impact Assessment (YEIA) Template, v3.0." *UoY Policy Document*.

### Discussion Questions

1. If your capstone achieves 95% accuracy overall but only 70% accuracy for a specific demographic group, is it ethical to deploy? What additional information would you need to make this decision?
2. Should AI safety "red teaming" be mandatory for all capstones that include AI components? Who should conduct the red team — the developers themselves, independent peers, or faculty?
3. A teammate proposes collecting user behavioral data "just in case we need it later." How do you respond?

### Practice Problems

- Complete a YEIA for your capstone. Identify at least three stakeholder groups, potential harms, and mitigations.
- Conduct a bias audit of any AI component in your capstone. Test with diverse inputs and document disparities. If disparities exist, propose and implement mitigations.

---

ᛇ **Lecture 11: Post-Mortem Analysis, Incident Response, and Organizational Learning**

**Course:** CS407 — Capstone Project II  
**Degree:** Bachelor of Science in Computer Science, 2040

---

### Overview

Systems fail. The measure of an engineering team is not whether failures occur, but how they respond to them. This lecture covers incident response: detecting, triaging, mitigating, and resolving production incidents. More importantly, it covers the post-mortem process: the structured, blameless retrospective that turns failure into organizational learning. By 2040, post-mortems are standard not just for tech companies but for student capstones, and they form part of the final assessment.

### Key Topics

- **Incident Response Lifecycle:** Detection (alerting, user reports), triage (severity assessment, impact scope), mitigation (stop the bleeding — what is the fastest way to restore service?), resolution (fix the root cause), and post-incident activity (post-mortem, action items). The lecture presents the "Incident Commander" role and the "two-pizza team" structure for incident response.
- **Blameless Post-Mortems:** The goal is not to find who is at fault but to understand how the system allowed a well-intentioned person to make a decision that led to failure. We review the Etsy/Google blameless post-mortem format: timeline (what happened, minute by minute), impact assessment (users affected, data lost, revenue impact), root cause analysis (using the Five Whys or Ishikawa diagrams), contributing factors, action items (specific, assigned, with deadlines), and lessons learned.
- **Root Cause Analysis Techniques:** The Five Whys (iterative questioning), Ishikawa/fishbone diagrams (categorizing causes by people, process, technology, environment), and the newer "Systems-Theoretic Process Analysis" (STPA) for complex socio-technical systems. The lecture warns against "root cause singularism" — most incidents have multiple contributing factors, and seeking a single root cause oversimplifies systemic failures.
- **Action Items and Follow-Through:** A post-mortem without action items is a therapy session, not engineering. Action items must be SMART (Specific, Measurable, Achievable, Relevant, Time-bound) and tracked to completion. The lecture presents the "error budget" concept from SRE: if incidents consume your error budget, feature development pauses until reliability improves.
- **Simulated Incidents for Capstones:** Students participate in a "fire drill" — a simulated incident in their staging environment. They must detect, triage, mitigate, and document the incident within 30 minutes. The drill is assessed on response time, communication clarity, and post-mortem quality.
- **Organizational Learning:** Incidents are data. Aggregated incident data reveals patterns: which services fail most often, which alerts are noisy, which deployments correlate with incidents. The lecture introduces "incident metrics" (MTTR, MTTD, change failure rate) and the DORA research program's findings on high-performing teams.

### Required Reading

- Allspaw, J. (2012). "Blameless PostMortems and a Just Culture." *Etsy Code as Craft* blog.
- Beyer, B. et al. (2016). *Site Reliability Engineering*. O'Reilly. (Chapter 15: Postmortem Culture)
- Dekker, S. W. A. (2014). *The Field Guide to Understanding 'Human Error'* (3rd ed.). Ashgate.
- Forsgren, N. et al. (2018). *Accelerate: The Science of Lean Software and DevOps*. IT Revolution Press. (Chapters 2–4)
- Leveson, N. G. (2011). *Engineering a Safer World*. MIT Press. (Chapters 1–3 on STAMP/STPA)

### Discussion Questions

1. What is the difference between "blameless" and "accountability"? Can a post-mortem be blameless while still holding individuals accountable for their actions?
2. If a junior engineer's misunderstanding of a configuration flag caused a two-hour outage, how do you address the knowledge gap without assigning blame?
3. How do you balance the need for thorough root cause analysis against the pressure to return to feature development?

### Practice Problems

- Conduct a simulated incident response drill on your capstone staging environment. Document the timeline, your mitigation steps, and a blameless post-mortem with at least three action items.
- Review your capstone's alerting configuration. Identify any "alert fatigue" risks (too many low-priority alerts) and refine your alerting rules to reduce noise while maintaining coverage.

---

ᛈ **Lecture 12: Portfolio Development, Career Launch, and the Craft of Engineering**

**Course:** CS407 — Capstone Project II  
**Degree:** Bachelor of Science in Computer Science, 2040

---

### Overview

The capstone ends, but the engineer's journey continues. This final lecture bridges the academic and professional worlds, addressing how to transform a capstone project into a career-launching portfolio. We cover portfolio presentation, interviewing techniques, the ethics of professional practice, continuous learning, and the philosophical dimensions of software engineering as a craft. The lecture closes with a meditation on what it means to be an engineer in 2040 — a time of unprecedented technological power and equally unprecedented responsibility.

### Key Topics

- **From Capstone to Portfolio:** A GitHub repository is not a portfolio; it is a code dump. A portfolio tells a story: the problem, your approach, the challenges, the solutions, and the outcomes. The lecture covers: writing a compelling README, creating a demo video, publishing a technical blog post, and presenting metrics (performance benchmarks, user counts, test coverage). Students produce a "capstone portfolio package" that can be shared with employers.
- **Technical Interviewing in 2040:** The interview landscape has evolved. Whiteboard coding is rare; system design interviews, take-home projects, and collaborative debugging sessions are standard. For AI-focused roles, candidates may be asked to review a model's output for bias or to design a safety mechanism. The lecture covers interview preparation strategies, the "think aloud" technique, and how to discuss failures honestly and constructively.
- **The Craftsman Ethic:** Software engineering is a craft — it combines scientific knowledge with practical skill, aesthetic judgment, and ethical responsibility. The lecture draws on Richard Sennett's *The Craftsman* and the Norse concept of *meistaraskapr* (mastery as a lifelong pursuit). Good code is not just correct; it is elegant, maintainable, and respectful of the people who will read it.
- **Continuous Learning and Specialization:** The half-life of technical knowledge is approximately 2.5 years in 2040. Engineers must adopt a "learn, unlearn, relearn" cycle. The lecture covers: reading research papers, contributing to open source, attending conferences (virtually or in person), finding mentors, and teaching others (the Feynman technique). Specialization vs. generalization: the T-shaped engineer has deep expertise in one area and broad competence across many.
- **Professional Ethics and the ACM Code:** The ACM Code of Ethics and Professional Conduct (2024 revision) provides guidance on: contributing to society, avoiding harm, being honest and trustworthy, respecting privacy, and honoring confidentiality. The lecture presents case studies of ethical dilemmas faced by early-career engineers and facilitates discussion on how to navigate them.
- **The Norse Engineer's Oath:** The University of Yggdrasil concludes every CS program with a voluntary oath, adapted from the old Norse concept of *heiður* (honor) and the Hippocratic tradition: "I will build systems that serve human flourishing. I will respect the privacy and autonomy of those who use my creations. I will acknowledge the limits of my knowledge and seek truth even when it is inconvenient. I will leave the code better than I found it. I will use my skills for creation, not destruction." The lecture invites students to reflect on what their own oath would be.

### Required Reading

- Sennett, R. (2008). *The Craftsman*. Yale University Press. (Chapters 1–3)
- Hunt, A. & Thomas, D. (1999). *The Pragmatic Programmer*. Addison-Wesley. (Chapter 1: The Cat Ate My Source Code)
- ACM Committee on Professional Ethics (2024). "ACM Code of Ethics and Professional Conduct." acm.org/code-of-ethics.
- Ousterhout, J. (2018). *A Philosophy of Software Design*. Yaknyam Press. (Chapters 1–4)
- Hafsteinn, E. (2040). "The Engineer as Skald: Craft, Honor, and Responsibility in the Age of AI." *Inaugural Address, University of Yggdrasil*.

### Discussion Questions

1. What is the difference between a "good" engineer and a "great" engineer? Is it technical skill, communication ability, ethical judgment, or something else?
2. If you are offered a position at a company whose products you believe cause social harm, what factors should guide your decision?
3. What will your personal "engineer's oath" be? What principles will you refuse to compromise, regardless of career pressure?

### Practice Problems

- Assemble your capstone portfolio package: polished README, architecture diagram, demo video (3–5 minutes), technical blog post (800–1200 words), and a one-page resume highlighting your capstone contributions.
- Conduct a mock system design interview with a peer. Choose a problem related to your capstone and practice thinking aloud while diagramming the solution.

---

## Assignments

### Assignment 1: Test Architecture Design Document

**Course:** CS407 — Capstone Project II  
**Type:** Design Document  
**Objective:** Produce a comprehensive testing strategy for your capstone project.

**Task:** Write a 1500–2500 word document that specifies: (a) your testing pyramid (what tests exist at each level); (b) your property-based testing strategy with at least three invariants; (c) your mutation testing plan; (d) your CI pipeline integration for tests; (e) coverage targets and how you will achieve them; (f) any formal verification or differential testing for AI components. Include a timeline for test development over the semester.

**Deliverables:**
- Test architecture document (Markdown, PDF, or LaTeX)
- Link to CI pipeline configuration
- Initial test suite with ≥50% coverage

**Grading Rubric:**
- Technical depth (30%): Appropriate selection of testing techniques for the project
- Coverage strategy (25%): Realistic targets with credible plans to achieve them
- AI-specific testing (20%): Thoughtful approach to non-deterministic components
- Documentation clarity (15%): Well-organized, readable, professional
- Timeline feasibility (10%): Achievable plan with milestones

**Due:** Week 3

---

### Assignment 2: Security Audit and Threat Model

**Course:** CS407 — Capstone Project II  
**Type:** Security Analysis  
**Objective:** Systematically evaluate your capstone's security posture.

**Task:** Produce a threat model (STRIDE-based) with at least eight identified threats. For each threat: describe the attack vector, assess risk (likelihood × impact), document your mitigation, and verify the mitigation with a test or code review. Run SAST and DAST tools; fix all high-severity findings. Generate an SBOM. Document any accepted risks with justification.

**Deliverables:**
- Threat model document with attack tree diagrams
- SAST/DAST scan reports (before and after remediation)
- SBOM in SPDX or CycloneDX format
- Security hardening commit log

**Grading Rubric:**
- Threat model completeness (30%): Comprehensive coverage of the attack surface
- Mitigation quality (25%): Effective, implemented, and verified defenses
- Tool usage (20%): Proper use of SAST, DAST, and SBOM generation
- Documentation (15%): Clear, professional security documentation
- Accepted risks (10%): Thoughtful risk acceptance with clear justification

**Due:** Week 6

---

### Assignment 3: Production Deployment and Observability

**Course:** CS407 — Capstone Project II  
**Type:** Implementation and Operations  
**Objective:** Deploy your capstone to a production-like environment with full observability.

**Task:** Deploy your capstone to the University staging cluster (or approved public cloud). Implement structured logging, metrics exposition, and distributed tracing. Define two SLOs with corresponding SLIs and error budgets. Configure alerting. Demonstrate a clean rollback. Produce operational runbooks for at least three scenarios.

**Deliverables:**
- Live deployment URL or access credentials
- Observability dashboard screenshots
- SLO/SLI definitions with error budget calculations
- Runbooks (three scenarios)
- Rollback demonstration video (2–3 minutes)

**Grading Rubric:**
- Deployment quality (25%): Stable, accessible, production-like environment
- Observability coverage (25%): Logs, metrics, traces all present and useful
- SLO design (20%): Well-chosen indicators with realistic targets
- Operational readiness (20%): Runbooks and rollback capability demonstrated
- Documentation (10%): Clear operational documentation

**Due:** Week 9

---

### Assignment 4: Capstone Defense and Portfolio

**Course:** CS407 — Capstone Project II  
**Type:** Presentation and Portfolio  
**Objective:** Defend your capstone before faculty and industry panel.

**Task:** Deliver a 15-minute technical demonstration followed by 10 minutes of Q&A. Present your system live, explain architectural decisions, discuss challenges and how you overcame them, and honestly address limitations. Submit your portfolio package: polished repository, architecture diagrams, demo video, technical blog post, and resume.

**Deliverables:**
- Live demonstration (15 minutes + Q&A)
- Portfolio package (repository, diagrams, video, blog post, resume)
- Completed YEIA ethical impact assessment
- ADR log documenting major decisions

**Grading Rubric:**
- Technical demonstration (30%): System works, features are impressive, demo is smooth
- Architectural reasoning (20%): Clear explanation of design decisions with trade-offs
- Communication (20%): Engaging, clear, professional presentation
- Portfolio quality (15%): Polished, comprehensive, career-ready materials
- Ethical consideration (10%): Thoughtful YEIA and honest discussion of limitations
- Q&A handling (5%): Direct, knowledgeable, graceful under questioning

**Due:** Finals Week

---

### Assignment 5: Post-Mortem and Handoff Document

**Course:** CS407 — Capstone Project II  
**Type:** Retrospective and Documentation  
**Objective:** Reflect on the capstone experience and prepare the project for future maintainers.

**Task:** Write a blameless post-mortem of one significant challenge or failure during your capstone (technical, interpersonal, or process-related). Include timeline, root cause analysis, contributing factors, and action items. Additionally, produce a comprehensive handoff document: architecture overview, dependency list with update risks, known technical debt, operational procedures, and recommended next steps for a future maintainer.

**Deliverables:**
- Blameless post-mortem (1500–2500 words)
- Handoff document (2000–3000 words)
- Recorded architecture walkthrough video (10–15 minutes)

**Grading Rubric:**
- Post-mortem quality (30%): Thorough, blameless, actionable
- Handoff completeness (30%): Future maintainer could take over from this document
- Architecture walkthrough (20%): Clear, comprehensive video explanation
- Reflection depth (15%): Genuine learning and growth demonstrated
- Professionalism (5%): Well-organized, well-written, suitable for external audience

**Due:** Finals Week

---

## Final Examination Preparation

The CS407 final examination is a **practical assessment** rather than a written test. Students must:

1. **Deploy and demonstrate** their capstone system live
2. **Present** their test suite, security audit, and observability setup
3. **Defend** architectural decisions using their ADR log
4. **Discuss** ethical implications using their completed YEIA
5. **Answer** technical questions from faculty and industry panelists

### Sample Assessment Questions (for preparation):

1. **Deployment Scenario:** Your capstone has been running in staging for two weeks. During the demo, a critical service fails. Walk us through your incident response: how do you detect, mitigate, and communicate? Demonstrate your rollback procedure.

2. **Architecture Defense:** You chose a microservices architecture for a system that might have been simpler as a monolith. Defend this decision. What would make you reconsider? What metrics would tell you the architecture is succeeding or failing?

3. **Security Challenge:** A penetration tester finds that your API returns verbose error messages that reveal internal file paths and stack traces. Explain how this vulnerability arose, how you will fix it, and how your testing pipeline should have caught it.

4. **Ethics Case:** Your capstone includes a recommendation engine. During testing, you discover it systematically recommends lower-paying job postings to users with certain demographic characteristics. The effect is statistically significant but small. What do you do? Do you ship? Delay? Redesign? Explain your reasoning using specific ethical frameworks.

5. **Performance Analysis:** Your system's p99 latency has doubled since the last sprint. You have profiling data, metrics, and logs. Walk us through your diagnosis process. What do you look at first? What tools do you use? How do you verify your hypothesis?

6. **Maintenance Handoff:** You graduate tomorrow. A first-year master's student will maintain your capstone. You have 30 minutes to brief them. What do you show them? What do you tell them? What documentation do you point them to?

7. **AI Safety:** Your capstone uses an LLM to generate user-facing content. During red teaming, you discover it can be prompted to generate harmful misinformation. Your mitigation reduces but does not eliminate this risk. What is your responsibility? What do you document? What do you communicate to users?

8. **Team Dynamics:** During the capstone, you and a teammate disagreed fundamentally on a technical approach. Describe the disagreement, how you resolved it (or why you didn't), and what you would do differently. This question assesses collaborative maturity, not technical correctness.

---

*The code is shipped. The tests pass. The monitors glow green. But the true measure of the engineer is not what they built — it is how they built it, why they built it, and who they built it for.* ᛟ

— Dr. Sigríðr Vébjörn, CS407 Course Notes, 2040
