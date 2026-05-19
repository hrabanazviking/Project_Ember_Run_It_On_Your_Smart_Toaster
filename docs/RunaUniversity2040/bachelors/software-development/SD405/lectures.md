# SD405: Capstone Project II — Build, Test, Deploy
## Bachelor of Science in Software Development — University of Yggdrasil, 2040

**Credits:** 4
**Semester:** Year 4, Semester 2
**Prerequisites:** SD401 (AI Agent Integration & Orchestration), SD403 (Legal, Ethics & Compliance in Software)
**Instructor:** Brynhildr Vérdóttir, Faculty of Software Engineering, University of Yggdrasil

> *"A ship is safe in harbor, but that's not what ships are built for. A project is safe in planning, but that's not what projects are built for. Deployment is the moment of truth — when your work meets the world."* — Brynhildr Vérdóttir, *The Builder's Codex* (2039)

---

## Course Description

Capstone Project II is the culminating experience of the Bachelor of Science in Software Development program — the course where students transition from learners to builders. In Capstone I (SD307), students designed and prototyped a significant software project. In Capstone II, students build, test, and deploy that project to production.

This is not a lecture course in the traditional sense. The "lectures" are structured as working sessions, each focused on a phase of the build-test-deploy lifecycle. Students work in teams of 2-4 on a single project throughout the semester, with weekly milestones, code reviews, and progressive deployment to the University's RúnarOS cloud platform. The instructor serves as a technical advisor, code reviewer, and deployment gatekeeper.

By the end of this course, each team will have: (a) built a production-quality software system, (b) implemented comprehensive automated testing (unit, integration, end-to-end, performance, security), (c) deployed to production using CI/CD pipelines, (d) monitored the deployed system for quality and reliability, and (e) documented the entire system for future maintainers. The project serves as the centerpiece of the student's professional portfolio.

The Norse metaphor for this course is the *langskip* (longship) — the vessel that carried Vikings across the seas. Building a longship required mastery of multiple crafts: woodworking, metalworking, sail-making, rope-making. Testing a longship meant putting it in the water and sailing it. Deploying a longship meant filling it with crew and provisions and setting out for distant shores. So too with software: build with craft, test with rigor, deploy with courage.

---

## Working Sessions (Lectures)

### ᚠ Session 1: The Keel is Laid — Project Architecture and Planning

**Date:** Week 1

#### Overview

The keel is the backbone of a longship — the first piece laid, the foundation upon which everything else is built. This session establishes the technical foundation for the semester's project: reviewing and finalizing the architecture designed in Capstone I, establishing the development environment, setting up version control and CI/CD pipelines, and creating the project roadmap.

#### Working Notes

**From Capstone I to Capstone II: What Changes?** In Capstone I (SD307), you designed your system on paper — architecture diagrams, data models, API specifications, user stories. You built a prototype — functional but not production-ready. In Capstone II, you build the real thing. The transition from prototype to production introduces concerns that prototyping deliberately excludes:

- **Reliability** — The system must handle real users, real data volumes, and real failure modes. Prototypes assume the happy path; production systems must handle the unhappy paths.
- **Security** — The system must resist attacks, protect user data, and comply with regulations (as studied in SD403). Prototypes often use hardcoded credentials and open ports; production systems need proper authentication, authorization, and encryption.
- **Performance** — The system must respond quickly under load. Prototypes are tested with one user; production systems must handle hundreds or thousands of concurrent users.
- **Maintainability** — The system must be understandable, modifiable, and testable by developers who didn't build it. Prototypes prioritize speed of development; production systems prioritize clarity of design.
- **Observability** — The system must expose its internal state for debugging, monitoring, and alerting. Prototypes are debugged with print statements; production systems need structured logging, metrics, and tracing.

**The Project Architecture Document.** Your first deliverable (due end of Week 1) is a Project Architecture Document (PAD) that formalizes the design from Capstone I with production concerns. The PAD must include:

1. **System Context Diagram** — A high-level diagram showing your system in its environment: users, external services, data stores, and the boundaries between them. Use C4 model (Context, Container, Component, Code) or similar structured approach.
2. **Technology Stack** — Justify every technology choice. Why this language? Why this framework? Why this database? The justification must address: (a) fitness for purpose, (b) team expertise, (c) ecosystem maturity, and (d) operational concerns (hosting, monitoring, cost).
3. **Data Model** — Entity-relationship diagram or equivalent, with explanations of key design decisions (normalization vs. denormalization, partitioning strategy, indexing strategy).
4. **API Specification** — For each endpoint: HTTP method, path, request schema, response schema, authentication requirements, rate limits, error responses. Use OpenAPI 3.1 or equivalent.
5. **Component Architecture** — How the system is decomposed into components (services, modules, packages), their responsibilities, and their interactions. Include component diagrams.
6. **Security Architecture** — Authentication flow, authorization model, data encryption (at rest and in transit), threat model, and security controls.
7. **Deployment Architecture** — How the system will be deployed: containerization (Docker/OCI), orchestration (Kubernetes or RúnarOS), CI/CD pipeline (GitHub Actions, GitLab CI, or the University's Gungnir CI), monitoring stack (Prometheus, Grafana, or the University's Mímir stack).
8. **Testing Strategy** — What types of tests will you write (unit, integration, E2E, performance, security), what tools will you use, what coverage targets will you set, and how will tests be integrated into CI/CD?

**Development Environment Setup.** By the end of Week 1, every team member must have a working development environment. This means:

- **Local environment** — The project builds and runs on each developer's machine. Use Docker Compose or equivalent to ensure consistent environments.
- **Version control** — The project is in a Git repository (GitHub or the University's Gungnir GitLab) with branch protection, code review requirements, and CI/CD integration.
- **CI/CD pipeline** — Every commit triggers: (a) linting and formatting checks, (b) unit tests, (c) integration tests, (d) security scanning (dependency vulnerabilities, static analysis), and (e) deployment to a staging environment. A successful CI/CD run is a prerequisite for merging any pull request.

**The Project Roadmap.** Break the semester into 2-week sprints, each with specific, measurable deliverables:

- **Sprints 1-2 (Weeks 1-4):** Core infrastructure and MVP (minimum viable product). The system does one thing end-to-end.
- **Sprints 3-4 (Weeks 5-8):** Feature expansion. The system does everything it's supposed to do.
- **Sprints 5-6 (Weeks 9-12):** Hardening. Testing, performance optimization, security hardening, documentation.
- **Sprint 7 (Weeks 13-14):** Deployment and presentation. Production deployment, monitoring setup, final presentation.

#### Milestones (Week 1)
- Project Architecture Document submitted and approved by instructor
- Development environment working for all team members
- CI/CD pipeline operational (at least lint + unit tests passing)
- Project roadmap with sprint breakdown submitted

#### Required Reading
- Vérdóttir, B. (2039). *The Builder's Codex: From Prototype to Production*. Reykjavík: University Press. Chapters 1-3.
- Kleppmann, M. (2017). *Designing Data-Intensive Applications*. O'Reilly. Chapters 1-2. [Still the best introduction to production system architecture.]
- C4 Model (Brown, S.). https://c4model.com. [The standard for software architecture diagrams.]
- University of Yggdrasil (2040). *Gungnir CI/CD Platform: Documentation and Best Practices*. Technical Guide UoY-ENG-2040-01.

#### Discussion Questions
1. Your team has two strong opinions about the technology stack: one member wants to use Rust for its safety and performance, another wants Python for its ecosystem and team familiarity. How do you resolve this? What criteria should drive the decision?
2. In Capstone I, you designed a monolithic architecture. Now you're considering microservices. What questions should you ask to decide whether to stay monolithic or decompose into services? What are the costs of distributed systems that prototypes don't reveal?
3. Your architecture document must justify every technology choice. But some choices are based on taste, not evidence — "I like React better than Vue." How do you distinguish between justified choices and taste-based choices in an architecture document?

---

### ᚢ Session 2: The Shipwright's Craft — Building with Discipline

**Date:** Week 2

#### Overview

A longship was built by skilled shipwrights who followed time-tested techniques: selecting the right wood, shaping the planks, fastening them with iron rivets, and caulking the seams with tarred wool. Building software with discipline requires similar craft: coding standards, design patterns, code review, pair programming, and the daily practices that produce quality code.

#### Working Notes

**The Discipline of Daily Development.** Professional software development is not about heroic bursts of inspiration — it's about consistent, disciplined practice day after day. The builders of longships didn't wait for inspiration; they went to the shipyard every morning and worked. This session establishes the daily practices and standards that will produce quality code over the semester.

**Coding Standards and Style Guides.** Every project must have a written coding standard. In 2040, this means:

- **Language-specific style guide** — PEP 8 for Python, Google Java Style Guide, Airbnb JavaScript Style Guide, etc. The style guide should be enforced by automated linters (flake8, ESLint, Checkstyle) integrated into CI/CD. Code that doesn't pass the linter doesn't merge.
- **Naming conventions** — Files, classes, functions, variables, constants. Names should be descriptive, consistent, and follow language conventions. A reader should be able to understand what a name refers to without reading the implementation.
- **Code organization** — How files and directories are structured. Use the standard project layout for your language and framework. Don't invent novel directory structures — consistency with community conventions is more valuable than cleverness.
- **Commenting and documentation** — When to comment (explaining *why*, not *what*), how to write docstrings (following language conventions: Javadoc, JSDoc, Sphinx/Google-style), and what must be documented (public APIs, complex algorithms, non-obvious design decisions).
- **Error handling** — How errors are represented, propagated, and handled. Use exceptions (Python, Java), Result types (Rust, Go), or Either types (functional languages) — but be consistent. Every error must be either handled or explicitly propagated; silently swallowing errors is forbidden.

**Design Patterns and When to Use Them.** Design patterns are reusable solutions to common problems. The original "Gang of Four" patterns (Gamma et al., 1994) remain relevant, but modern software development uses patterns that the Gang of Four didn't anticipate:

- **Dependency Injection** — Instead of creating dependencies inside a class, pass them in from outside. This makes testing easier (you can inject mocks) and coupling looser (the class doesn't know how its dependencies are created).
- **Repository Pattern** — Abstract data access behind an interface, so the business logic doesn't know whether data comes from PostgreSQL, MongoDB, or an in-memory cache. This makes testing easier and allows swapping data stores without changing business logic.
- **Command Pattern / CQRS** — Separate commands (which change state) from queries (which read state). This enables different optimization strategies for reads and writes and aligns with event-driven architectures.
- **Observer / Pub-Sub** — Decouple producers of events from consumers of events. This is the foundation of event-driven architectures, which are central to multi-agent AI systems (as studied in SD401).
- **Saga Pattern** — For distributed transactions: break a transaction into steps, each with a compensating action. If a step fails, execute the compensating actions for previous steps. This is essential for microservice architectures.

**Code Review: The Quality Gate.** Every line of code must be reviewed by at least one other team member before merging. Code review is not an adversarial process — it's a collaborative one. The reviewer's role is to catch bugs, suggest improvements, and ensure consistency. The author's role is to receive feedback graciously and improve the code.

Effective code reviews follow the University's *Rún Review Protocol*:

1. **Size** — Pull requests should be small (under 400 lines changed). Large PRs are hard to review thoroughly and tend to receive superficial feedback. Break large changes into multiple small PRs.
2. **Description** — Every PR must include: what changed, why, how it was tested, and any risks or concerns. The reviewer should be able to understand the change without reading the code.
3. **Automation** — Automated checks (lint, tests, security scan) must pass before human review begins. Don't waste reviewer time on problems that automation can catch.
4. **Review** — The reviewer checks: (a) correctness (does it work?), (b) design (is it well-structured?), (c) style (does it follow conventions?), (d) tests (are there adequate tests?), (e) documentation (is it documented?), and (f) security (are there vulnerabilities?).
5. **Response** — The author responds to every comment: "Fixed," "Will fix in follow-up," or "Disagree, because..." with reasoning. Unresolved comments block merge.
6. **Approval** — At least one reviewer must approve the PR. The author merges after approval.

**Version Control Discipline.** Your Git repository tells the story of your project. A clean Git history makes it easy to understand what changed, when, and why. Practices:

- **Meaningful commit messages** — Not "fixed bug" but "Fix null pointer in UserService when email is missing (fixes #42)." The conventional commits format is recommended: `type(scope): description` (e.g., `feat(auth): add OAuth2 login`, `fix(db): resolve connection pool exhaustion`).
- **Atomic commits** — Each commit should be a single, coherent change. Don't mix unrelated changes in one commit (e.g., "add login feature and fix typo in README").
- **Branch discipline** — Main branch is always deployable. Feature branches are short-lived (merge within a few days). Use feature flags for long-running changes that can't be merged incrementally.

#### Milestones (Week 2)
- Coding standards document written and agreed upon by the team
- First pull request opened, reviewed, and merged following the Rún Review Protocol
- CI/CD pipeline enforcing lint and unit tests on every push

#### Required Reading
- Vérdóttir, B. (2039). *The Builder's Codex*. Chapters 4-6.
- Martin, R.C. (2008). *Clean Code: A Handbook of Agile Software Craftsmanship*. Prentice Hall. [Still the classic on code quality, though some examples are dated.]
- Gamma, E., et al. (1994). *Design Patterns: Elements of Reusable Object-Oriented Software*. Addison-Wesley. [The Gang of Four — foundational, though the patterns have evolved.]
- University of Yggdrasil (2040). *Rún Review Protocol: Code Review Standards*. Technical Guide UoY-ENG-2040-02.

#### Discussion Questions
1. Your teammate submits a PR that works correctly but violates several coding standards (naming conventions, code organization). The PR is 800 lines. How do you handle this in code review? Do you approve and file follow-up issues, or block until standards are met?
2. "Design patterns are a sign of weakness in a programming language" — some developers argue that patterns exist because languages lack features to express the pattern directly. Do you agree? How does this affect your use of patterns in modern languages like Rust or TypeScript?
3. Conventional commits require a specific format for every commit message. Is this discipline worth the overhead? When would you relax it (e.g., for personal projects, prototypes, or emergency fixes)?

---

### ᚦ Session 3: Testing the Planks — Automated Testing Strategy

**Date:** Week 3

#### Overview

Before a longship was launched, every plank was tested — for strength, for fit, for watertightness. In software, automated testing is the equivalent: the systematic verification that every component works, individually and together. This session establishes the testing strategy for the project: the test pyramid, test-driven development, mocking and stubbing, and testing AI components.

#### Working Notes

**The Test Pyramid in 2040.** The test pyramid (Cohn, 2009) remains the dominant mental model for organizing tests, but it has evolved to reflect modern software architecture:

- **Unit Tests (Base of the Pyramid, Most Tests).** Test individual functions, methods, or classes in isolation. Fast (milliseconds), reliable (no external dependencies), and numerous (hundreds or thousands per project). Unit tests verify *correctness*: does this function return the right output for this input?
- **Integration Tests (Middle of the Pyramid).** Test the interaction between components: does the UserService correctly save and retrieve users from the database? Does the API endpoint correctly call the AuthService and return the appropriate response? Integration tests are slower than unit tests (seconds) and require real or containerized dependencies (databases, message queues). They verify *composition*: do these components work together?
- **End-to-End (E2E) Tests (Top of the Pyramid, Fewest Tests).** Test the system from the user's perspective: a simulated user interacts with the UI (or API) and the test verifies the correct outcome. E2E tests are slow (minutes), flaky (sensitive to timing and environment), and expensive to maintain. They verify *system behavior*: does the system do what the user expects?
- **Performance Tests (Side of the Pyramid).** Test that the system meets performance requirements: response time (P50, P95, P99), throughput (requests per second), and resource utilization (CPU, memory, network). Performance tests are run less frequently than correctness tests but are critical for production readiness.
- **Security Tests (Side of the Pyramid).** Automated vulnerability scanning: dependency vulnerabilities (npm audit, Snyk), static analysis (Semgrep, CodeQL), and dynamic analysis (OWASP ZAP). Security tests should run on every commit alongside unit tests.
- **Accessibility Tests (Side of the Pyramid in 2040).** Automated accessibility checks (axe-core, Lighthouse) verify that UIs are accessible to users with disabilities. Required for compliance with the European Accessibility Act (2025) and University policy.

**Test-Driven Development (TDD) and Its Variants.** TDD (Beck, 2003) is the practice of writing tests before writing the code that makes them pass. The cycle: Red (write a failing test) → Green (write the minimum code to make it pass) → Refactor (improve the code without changing behavior). TDD is widely practiced at the University and is the default expectation for capstone projects.

Variants of TDD include:

- **Behavior-Driven Development (BDD).** Write tests in a human-readable format that describes behavior: "Given a user with a valid account, when they enter their credentials, then they are logged in." BDD aligns tests with business requirements and makes them readable by non-developers.
- **Acceptance Test-Driven Development (ATDD).** Write acceptance tests (E2E tests that verify user-visible behavior) before implementation. ATDD ensures that the entire team (developers, designers, product owners) agrees on what "done" means.
- **Property-Based Testing.** Instead of writing specific test cases, define properties that should hold for all inputs, and let the test framework generate random inputs. Example: "For any list, reversing it twice returns the original list." Property-based testing finds edge cases that example-based testing misses.

**Testing AI Components.** Many capstone projects in 2040 include AI components (LLM-based agents, recommendation systems, classification models). Testing AI is fundamentally different from testing deterministic code because AI outputs are non-deterministic — the same input can produce different outputs. Strategies for testing AI:

- **Golden Dataset Testing.** Maintain a curated dataset of inputs and expected outputs. Run the AI component on the golden dataset and measure accuracy, precision, recall, F1, or other relevant metrics. The test "passes" if the metrics meet the threshold.
- **Invariant Testing.** Define properties that should hold regardless of the specific output: "The response should be grammatically correct English," "The response should not contain personally identifiable information," "The response should be relevant to the query." These invariants can be checked deterministically.
- **A/B Testing.** Run two versions of the AI component side-by-side and compare them on key metrics. A/B testing is not a CI/CD test — it's a production evaluation technique — but it's essential for AI systems that learn and evolve.
- **Human Evaluation.** For subjective qualities (tone, helpfulness, creativity), human evaluation is still the gold standard in 2040. Automated metrics (BLEU, ROUGE, BERTScore) correlate imperfectly with human judgment.

**Mocking, Stubbing, and Test Doubles.** Unit tests require isolating the component under test from its dependencies. Test doubles are objects that stand in for real dependencies:

- **Mocks** — Verify that the dependency was called correctly (with what arguments, how many times).
- **Stubs** — Return pre-configured responses to calls, without verifying how they were called.
- **Fakes** — Lightweight implementations of the dependency (an in-memory database instead of PostgreSQL, a fake email service that records sent emails).
- **Spies** — Record calls to the dependency for later verification, while also delegating to the real implementation.

The University's guidance: prefer fakes over mocks for external services (databases, APIs) because fakes behave more like the real thing and catch more integration bugs. Use mocks sparingly and only for dependencies that are impractical to fake.

#### Milestones (Week 3)
- Test pyramid documented: what types of tests, what tools, what coverage targets
- Unit test suite established with at least 50% code coverage
- At least one integration test passing for each major system component
- CI/CD pipeline running all tests on every push

#### Required Reading
- Vérdóttir, B. (2039). *The Builder's Codex*. Chapters 7-9.
- Beck, K. (2003). *Test-Driven Development: By Example*. Addison-Wesley. [The classic TDD text.]
- Freeman, S., & Pryce, N. (2009). *Growing Object-Oriented Software, Guided by Tests*. Addison-Wesley. [Practical guide to TDD in larger systems.]
- Megler, V., et al. (2037). "Testing AI Systems: A Practitioner's Guide." *IEEE Software* 54(3). [Contemporary guide to testing non-deterministic AI components.]

#### Discussion Questions
1. TDD requires writing tests before code. But for AI components where the output isn't predictable, you can't write a precise expected output. How would you adapt TDD for AI components? What would the "Red" step look like?
2. Your project has a microservice architecture. E2E tests that span multiple services are slow (5 minutes) and flaky (they fail 10% of the time due to timing issues). How do you balance the value of E2E tests (catching integration bugs) with their cost (slow, flaky)? Would you run them on every commit?
3. Code coverage is a metric, not a goal. 100% code coverage means every line is executed by at least one test — but it doesn't mean the tests are good. A test that executes a line without asserting anything about its behavior increases coverage without increasing quality. How should teams use coverage metrics responsibly?

---

### ᚨ Session 4: The Rivets Hold — Integration and API Testing

**Date:** Week 4

#### Overview

A longship's planks were fastened with iron rivets — each one individually forged and hammered into place. The strength of the ship depended on every rivet holding. In software, the rivets are the interfaces between components: APIs, database queries, message queues, and service calls. This session focuses on integration testing: verifying that the interfaces between components are correct, reliable, and resilient.

#### Working Notes

**Why Integration Testing Matters More Than Ever.** In 2040, software systems are more integrated than ever. A typical capstone project involves: one or more APIs (REST, GraphQL, gRPC), a database (PostgreSQL, MongoDB, or both), at least one external service (auth provider, payment processor, AI API), and possibly a message queue (for async processing). Each integration point is a potential failure point.

Integration tests verify that these integration points work correctly. Unlike unit tests (which isolate components) and E2E tests (which test the entire system), integration tests focus specifically on the boundaries between components. They answer questions like: "Does the UserService correctly serialize and deserialize user objects to and from the database?" "Does the API return the correct HTTP status codes for error conditions?" "Does the message consumer correctly process messages from the queue, even when messages arrive out of order?"

**API Testing Patterns.** Testing APIs (REST, GraphQL, gRPC) requires specific patterns:

*Contract Testing.* Verify that the API adheres to its specification (OpenAPI, GraphQL schema, Protobuf). The test checks: endpoints exist, request/response formats match the spec, status codes match expectations, and error responses follow the documented format. Tools: Dredd, Schemathesis, or the University's *Mjǫllnir Contract Validator*.

*Scenario Testing.* Test specific user scenarios: "A new user registers, verifies their email, logs in, creates a resource, updates it, and deletes it." Scenario tests verify that the API supports complete workflows, not just individual endpoints.

*Error Testing.* Test that the API handles errors gracefully: invalid input (400), unauthorized access (401), forbidden access (403), not found (404), conflict (409), server error (500). Good error handling is the difference between a professional API and an amateur one.

*Rate Limiting and Throttling Tests.* Verify that the API enforces rate limits and returns appropriate responses (429 Too Many Requests) with Retry-After headers. This is essential for production resilience.

*Authentication and Authorization Tests.* Verify that protected endpoints require valid credentials, that different roles have appropriate access, and that expired or invalid tokens are rejected.

**Database Testing.** Testing database interactions requires a realistic database — not mocks. The University provides the *Viðarr Test DB* service, a containerized PostgreSQL instance that resets to a known state before each test suite.

Key database testing patterns:

- **Repository Tests** — Test that data access objects correctly create, read, update, and delete records. Verify that constraints (unique, foreign key, check) are enforced. Verify that indices are used (EXPLAIN ANALYZE).
- **Migration Tests** — Test that database migrations apply cleanly and can be rolled back. Test that migrations work on realistic data volumes.
- **Transaction Tests** — Test that operations within a transaction are atomic (all or nothing), consistent (constraints satisfied), isolated (concurrent transactions don't interfere), and durable (committed data survives restarts).

**Message Queue Testing.** For systems that use message queues (for async processing, event-driven architectures, or agent communication), integration testing includes:

- **Message Production Tests** — Verify that messages are correctly serialized and published to the queue with the right routing keys, headers, and payloads.
- **Message Consumption Tests** — Verify that consumers correctly deserialize messages, process them, and acknowledge or reject them as appropriate.
- **Idempotency Tests** — Verify that processing the same message twice doesn't cause duplicate effects. This is critical for at-least-once delivery semantics.
- **Dead Letter Queue Tests** — Verify that messages that cannot be processed (malformed, unexpected) are routed to a dead letter queue for inspection, rather than silently dropped.

**Test Data Management.** Integration tests need test data. Managing test data is a non-trivial problem:

- **Fixtures** — Pre-defined data sets that are loaded before tests. Simple but brittle: if the schema changes, fixtures break.
- **Factories** — Generate test data programmatically. More flexible than fixtures: factories adapt to schema changes. Tools: factory_boy (Python), FactoryBot (Ruby), or the University's *Dvergr Data Factory*.
- **Property-Based Data Generation** — Define properties of valid data (e.g., "email must contain @") and let the test framework generate random valid data. This is the most thorough approach but requires defining properties for every data type.

#### Milestones (Week 4)
- Integration test suite covering all API endpoints, database operations, and message flows
- Contract tests passing against API specification
- Error handling tested for all endpoints (at minimum: 400, 401, 403, 404, 500)
- Test data management strategy implemented

#### Required Reading
- Vérdóttir, B. (2039). *The Builder's Codex*. Chapters 10-12.
- Newman, S. (2021). *Building Microservices*. 2nd ed. O'Reilly. Chapters on testing. [Essential for testing distributed systems.]
- Marick, B. (1995). *The Craft of Software Testing*. Prentice Hall. [Still relevant for its treatment of testing philosophy.]
- University of Yggdrasil (2040). *Viðarr Test DB Service and Mjǫllnir Contract Validator*. Technical Guide UoY-ENG-2040-03.

#### Discussion Questions
1. Contract testing verifies that the API matches its specification. But the specification might be wrong — the spec says status 200 on success, but the business requirement says status 201 Created. How do you ensure that the specification is correct? What role does BDD play here?
2. Your integration tests are slow (30 seconds per test suite) because they use a real database. Your teammate suggests replacing the database with an in-memory mock to speed up tests. What do you argue? When is it acceptable to mock the database, and when must you use the real thing?
3. Test data management becomes harder as the system grows. A test that creates a user, an organization, a project, and a task needs all four entities to exist in the right state. How do you manage test data complexity? Would you use shared fixtures, per-test setup, or something else?

---

### ᚱ Session 5: Into the Fjord — Staging Deployment and CI/CD Pipelines

**Date:** Week 5

#### Overview

Before a longship ventured into the open sea, it was tested in the fjord — sheltered waters where the crew could practice sailing, identify problems, and make repairs before facing the ocean. The fjord is the staging environment: a production-like environment where the system is deployed, tested, and validated before release to users.

#### Working Notes

**The Staging Environment.** The staging environment (also called "pre-production" or "UAT") is the last stop before production. It should be as similar to production as possible: same infrastructure (containerized on RúnarOS), same database engine, same external service configurations, same security controls. The only difference should be scale (staging runs on fewer resources) and data (staging uses synthetic or anonymized data, never real user data).

The staging environment serves several purposes:

- **Integration validation** — Do all the components work together in a deployed environment? Problems that don't appear on a developer's machine (network latency, service discovery, configuration differences) become visible in staging.
- **Performance baseline** — How does the system perform under moderate load? You can't extrapolate production performance from a developer's laptop, but staging gives a rough baseline.
- **Deployment rehearsal** — Does the deployment process work? Every step of the deployment (database migration, service restart, health check, smoke test) is practiced in staging before production.
- **Stakeholder review** — Product owners, designers, and other stakeholders can interact with the deployed system and provide feedback before it reaches users.

**CI/CD Pipeline Design.** A CI/CD pipeline automates the path from code commit to deployed system. The pipeline for this course must include at minimum:

1. **Build** — Compile code, install dependencies, build containers. The build step produces a deployable artifact (Docker image, compiled binary, static assets).
2. **Test** — Run linting, unit tests, integration tests, security scans. Every test must pass before the pipeline proceeds.
3. **Deploy to Staging** — Push the artifact to the staging environment. Run database migrations, restart services, run health checks.
4. **Smoke Tests** — Run a small set of critical E2E tests against the staging deployment. If these pass, the deployment is considered healthy.
5. **Approval Gate** — For production deployments, require manual approval. The team lead (or instructor) reviews the staging deployment and approves the promotion to production.
6. **Deploy to Production** — Push the artifact to production, with the same process practiced in staging.
7. **Post-Deployment Monitoring** — After deployment, monitor production for errors, latency spikes, or other anomalies for a configurable period (minimum 30 minutes). If anomalies are detected, automatically roll back.

The University's Gungnir CI platform provides pre-configured pipeline templates that implement this flow. Teams customize the template for their specific technology stack.

**Deployment Strategies.** How you deploy affects risk:

*Rolling Deployment.* Gradually replace old instances with new ones. At any point, some instances are old and some are new. This eliminates downtime but means users may hit different versions during the deployment window. Suitable for stateless services where version differences don't cause problems.

*Blue-Green Deployment.* Maintain two identical environments (blue and green). Deploy to the inactive environment (e.g., green), test it, then switch traffic from blue to green. If problems arise, switch back. This provides instant rollback but requires twice the infrastructure.

*Canary Deployment.* Deploy to a small percentage of users first, monitor for problems, then gradually increase. This limits the blast radius of a bad deployment but requires traffic splitting and careful monitoring.

For capstone projects, blue-green deployment on RúnarOS is the recommended strategy. It provides the best balance of safety and simplicity for small teams.

**Infrastructure as Code.** The deployment infrastructure should be defined as code, not configured manually. This means: Dockerfiles for container images, Kubernetes manifests (or RúnarOS descriptors) for service definitions, Terraform (or RúnarOS IaC) for cloud resources, and configuration files (with secrets externalized) for application configuration.

Infrastructure as Code (IaC) ensures that: (a) deployments are reproducible (the same configuration produces the same environment), (b) environments are versioned (changes are tracked in Git alongside code), and (c) environments can be recreated from scratch (disaster recovery).

#### Milestones (Week 5)
- Staging environment operational and accessible
- CI/CD pipeline deploying to staging automatically on merge to main
- Smoke tests passing against staging
- Infrastructure defined as code and committed to the repository

#### Required Reading
- Vérdóttir, B. (2039). *The Builder's Codex*. Chapters 13-15.
- Humble, J., & Farley, D. (2010). *Continuous Delivery*. Addison-Wesley. [The foundational text on CI/CD — still relevant in 2040.]
- Kim, G., et al. (2016). *The DevOps Handbook*. IT Revolution. [Practical guide to DevOps practices.]
- University of Yggdrasil (2040). *Gungnir CI Platform: Pipeline Templates*. Technical Guide UoY-ENG-2040-04.

#### Discussion Questions
1. Your team wants to use feature flags to control which users see new features. Feature flags are code, so they break the principle of "the main branch is always deployable" — a feature flag might be off in production but on in staging. How do you manage feature flags in a CI/CD pipeline?
2. Blue-green deployment requires twice the infrastructure. For a small team with a limited budget, is the cost justified? What deployment strategy would you use if you couldn't afford blue-green?
3. Infrastructure as Code means your database schema is defined in migration files committed to Git. A teammate wants to make a quick change to the staging database directly (not through a migration) to unblock a demo. What do you do? What are the risks of manual database changes?

---

### ᚲ Session 6: The Captain's Eye — Code Review and Technical Debt Management

**Date:** Week 6

#### Overview

The captain of a longship didn't just steer — they inspected every part of the vessel, looking for wear, damage, and weakness before it became critical. In software, the captain's eye is code review and technical debt management: the ongoing discipline of reviewing code, identifying problems, and paying down debt before it sinks the project.

#### Working Notes

**Technical Debt: The Interest You Pay on Hasty Decisions.** Ward Cunningham coined the metaphor of "technical debt" in 1992: when you take shortcuts to deliver faster, you accumulate debt that must be paid back later, with interest. Like financial debt, technical debt is not inherently bad — taking on debt to deliver value faster can be rational. But uncontrolled debt compounds until the interest payments consume all your development capacity.

Types of technical debt:

- **Deliberate debt** — You consciously chose a shortcut, knowing you'd pay it back later. Example: hardcoding a value instead of building a configuration system, with a plan to build the configuration system next sprint. This is the most manageable type because it's intentional and documented.
- **Inadvertent debt** — You didn't realize you were taking a shortcut until later. Example: a design that seemed clean at the time but became convoluted as requirements evolved. This is the most common type and the hardest to manage because it accumulates silently.
- **Bit rot** — The codebase degrades over time due to inconsistent practices, outdated dependencies, and accumulated cruft. Even without deliberate shortcuts, a codebase that isn't actively maintained accumulates debt.
- **Environmental debt** — The world changes around your code. Dependencies become unmaintained, security vulnerabilities are discovered, platforms evolve, and your code that was state-of-the-art becomes legacy.

**Managing Technical Debt.** The capstone project is only one semester — there's a natural temptation to ignore technical debt because "we won't have to maintain this after the course." This is a trap. The purpose of the capstone is to practice professional practices, and managing technical debt is one of the most important professional practices.

The University's *Gjaldkeri Protocol* (named after the Old Norse term for a steward who managed accounts) provides a framework for technical debt management:

1. **Measure** — You can't manage what you don't measure. Track: (a) code complexity (cyclomatic complexity per function), (b) duplication (copy-pasted code), (c) test coverage (percentage of code exercised by tests), (d) dependency freshness (how many dependencies are outdated), (e) known issues (bugs and TODOs in the issue tracker). Tools: SonarQube, CodeClimate, or the University's *Einherjar Code Analyzer*.
2. **Prioritize** — Not all debt is equal. Prioritize based on: (a) impact (how much does this debt slow you down?), (b) risk (how likely is this debt to cause a production incident?), (c) contagion (how much does this debt spread to other parts of the system?).
3. **Allocate** — Reserve a portion of each sprint for debt reduction. The industry standard is 15-20% of capacity. For the capstone, allocate at least one day per sprint to refactoring, dependency updates, and documentation improvements.
4. **Document** — Every deliberate shortcut should be documented as a "debt item" in the issue tracker: what was the shortcut, why was it taken, what's the proper solution, and when will it be addressed? This prevents "we'll fix it later" from becoming "we forgot about it."
5. **Review** — At the end of each sprint, review the debt backlog: what was paid down, what new debt was incurred, and what's the plan for next sprint.

**Code Review as Debt Prevention.** The best way to manage technical debt is to prevent it from being incurred in the first place. Code review is the primary prevention mechanism. Beyond the Rún Review Protocol (Session 2), effective code review for debt prevention means:

- **Ask "Why?" not just "What?"** — Understanding the reasoning behind a change reveals whether it's a careful design decision or a hasty shortcut.
- **Check for consistency** — Does the new code follow the patterns established in the rest of the codebase? Inconsistency is a form of debt — it makes the codebase harder to understand and maintain.
- **Consider future readers** — Will someone reading this code six months from now understand it? If not, it needs better naming, comments, or restructuring.
- **Be pragmatic** — Not every code review comment needs to be addressed. "This works, ship it" is sometimes the right response. The key is distinguishing between "this could be slightly better" (nice to have) and "this will cause problems later" (must fix).

#### Milestones (Week 6)
- Code complexity and duplication metrics established
- Technical debt items documented in the issue tracker with priorities
- At least one "debt reduction" session completed (refactoring, dependency updates, documentation)
- Mid-semester code review with instructor

#### Required Reading
- Vérdóttir, B. (2039). *The Builder's Codex*. Chapters 16-17.
- Fowler, M. (2018). *Refactoring: Improving the Design of Existing Code*. 2nd ed. Addison-Wesley. [The definitive text on refactoring.]
- Allman, E. (2012). "Managing Technical Debt." *Communications of the ACM* 55(5). [Accessible introduction to technical debt.]
- University of Yggdrasil (2040). *Gjaldkeri Protocol: Technical Debt Management*. Technical Guide UoY-ENG-2040-05.

#### Discussion Questions
1. Your team has a critical feature to deliver this sprint, and you've taken on significant technical debt to deliver it on time. The product owner wants to start the next feature immediately. How do you advocate for debt reduction time? What would convince a non-technical stakeholder that "cleaning up code" is worth the investment?
2. Some technical debt is invisible to tools — it's in the design, not the code. A microservice boundary cuts through a transaction, creating distributed consistency issues. No linter or complexity analyzer will catch this. How do you identify and manage design-level debt?
3. "If it ain't broke, don't fix it" vs. "continuous improvement." When is refactoring working code justified? When is it vanity — making changes that feel productive but don't deliver value?

---

### ᚷ Session 7: The Sea Trials — Performance and Load Testing

**Date:** Week 7

#### Overview

A longship's sea trials tested it against wind, waves, and weather — proving that it could survive the conditions it would face. Performance and load testing serve the same purpose: proving that the system can handle the load it will face in production, and understanding what happens when it can't.

#### Working Notes

**Why Performance Testing Matters for Capstone Projects.** "It works on my machine" is the most dangerous phrase in software development. A system that performs well on a developer's laptop with one user and a fresh database may collapse under 100 concurrent users with a database containing a million records. Performance testing reveals these problems before users do.

For capstone projects, the goals of performance testing are:

1. **Establish a performance baseline** — What is the system's throughput (requests per second) and latency (response time) under normal load? This baseline serves as a reference for future optimization and regression detection.
2. **Identify bottlenecks** — Where does the system spend its time? Database queries? External API calls? CPU-bound computation? Understanding bottlenecks tells you where to focus optimization efforts.
3. **Determine the system's limits** — At what point does the system degrade or fail? What is the maximum throughput before latency becomes unacceptable? What is the maximum concurrent user count before errors appear?
4. **Verify that the system degrades gracefully** — When overloaded, does the system return errors quickly (fail fast) or hang indefinitely (fail slow)? Graceful degradation means users get responses, even if those responses indicate the system is overloaded.

**Performance Testing Methodology.** The University's *Ægir Load Testing Protocol* (named after the Norse sea giant) provides a structured approach:

*Step 1: Define Performance Requirements.* What are the acceptable performance characteristics? Example: "P95 latency for the /api/search endpoint must be under 200ms at 100 requests per second." Without defined requirements, you can't determine whether the system passes or fails.

*Step 2: Design Load Profiles.* What patterns of load will the system face? Common profiles:
- **Constant load** — A steady rate of requests. Tests whether the system can sustain the expected baseline.
- **Ramp load** — Gradually increasing load. Identifies the point at which the system degrades.
- **Spike load** — Sudden increase in load. Tests whether the system can handle traffic spikes (e.g., a product launch or viral post).
- **Stress load** — Load beyond the expected maximum. Tests the system's breaking point and recovery behavior.

*Step 3: Instrument the System.* Before testing, ensure the system is instrumented with metrics: CPU, memory, network, database query times, cache hit rates, queue depths. Testing without instrumentation is like sailing without a compass — you can tell something is wrong, but not what.

*Step 4: Execute Tests.* Run load tests against the staging environment (never production for initial testing). Tools: Locust, k6, JMeter, or the University's *Jǫrmungandr Load Generator*. Record: throughput, latency (P50, P95, P99), error rate, and resource utilization.

*Step 5: Analyze Results.* Compare results to requirements. If the system doesn't meet requirements, identify bottlenecks using profiling tools (flame graphs, query analyzers, distributed tracing).

*Step 6: Optimize and Retest.* Address the most impactful bottleneck, retest, and iterate. This is the performance optimization loop.

**Common Performance Bottlenecks.** In 2040, most performance problems fall into a few categories:

- **N+1 queries** — Fetching a list of items, then making a separate database query for each item. Solution: eager loading, batch queries, or GraphQL DataLoader.
- **Missing indices** — Database queries that scan entire tables because the appropriate index is missing. Solution: analyze query patterns and add indices.
- **Uncached repeated computations** — Expensive operations performed repeatedly with the same inputs. Solution: caching (in-memory, Redis, CDN).
- **Chatty service communication** — Microservices that make many small calls to each other instead of batching. Solution: aggregate APIs, batch requests, or consolidate services.
- **Blocking I/O** — Synchronous I/O operations that block the thread pool, preventing other requests from being processed. Solution: async I/O, non-blocking frameworks, or reactive programming.

#### Milestones (Week 7)
- Performance requirements defined and documented
- Load tests executed against staging for all critical endpoints
- Performance baseline established
- Bottlenecks identified and optimization plan created

#### Required Reading
- Vérdóttir, B. (2039). *The Builder's Codex*. Chapters 18-19.
- Gregg, B. (2021). *Systems Performance: Enterprise and the Cloud*. 2nd ed. Pearson. [The definitive text on performance analysis.]
- Newman, S. (2021). *Building Microservices*. 2nd ed. O'Reilly. Chapters on performance and observability.
- University of Yggdrasil (2040). *Ægir Load Testing Protocol*. Technical Guide UoY-ENG-2040-06.

#### Discussion Questions
1. You discover that your system's P95 latency doubles when the database reaches 10,000 records. The cause is a missing index. Adding the index reduces P95 latency by 60%, but increases insert time by 25%. Is this a good trade-off? How do you decide?
2. Load testing in staging doesn't perfectly replicate production — production has more data, more concurrent users, and different usage patterns. How do you account for the differences between staging and production in your performance testing? Would you ever load test in production?
3. Your teammate optimizes a function and reduces its runtime from 100ms to 10ms — a 10x improvement. But profiling shows the function is only called once per request, and the real bottleneck is a 500ms database query. How do you handle the teammate's optimization effort? Do you celebrate the improvement or redirect attention to the real bottleneck?

---

### ᚹ Session 8: The Shield of the Ship — Security Hardening

**Date:** Week 8

#### Overview

Viking longships carried shields along their sides — not just for battle, but as a visible declaration that the ship was defended. Security hardening is the process of fortifying your system against attack, reducing the attack surface, and ensuring that security is not an afterthought but a fundamental property of the system.

#### Working Notes

**Security Hardening: Beyond the Basics.** By Week 8, your system should have basic security controls: authentication (users must log in), authorization (users can only access their own data), and encryption (data in transit and at rest). Security hardening goes beyond these basics to make the system robust against determined attackers.

**The OWASP Top 10 in 2040.** The Open Web Application Security Project (OWASP) maintains a list of the top 10 web application security risks, updated every few years. In 2040, the list includes both classic vulnerabilities and AI-specific risks:

1. **Broken Access Control** — Users can access data or functions they shouldn't. Example: changing a user ID in a URL to access another user's data. Solution: enforce authorization on every request, not just at the UI level.
2. **Injection Attacks** — Untrusted data is interpreted as code. SQL injection, command injection, and the newer prompt injection (crafting inputs that cause AI models to behave maliciously). Solution: parameterized queries, input validation, and output encoding.
3. **Cryptographic Failures** — Sensitive data exposed due to weak encryption, missing encryption, or improper key management. Solution: use industry-standard algorithms (AES-256-GCM, TLS 1.4), manage keys securely (HSM or KMS), never roll your own crypto.
4. **Insecure Design** — Security flaws built into the architecture. Example: a design that assumes the client can be trusted (it can't). Solution: threat modeling, secure design reviews, and the "never trust the client" principle.
5. **Security Misconfiguration** — Default credentials, unnecessary features enabled, verbose error messages exposing system details. Solution: hardened configuration by default, automated configuration scanning, and regular configuration reviews.
6. **Vulnerable and Outdated Components** — Using libraries with known vulnerabilities. Solution: automated dependency scanning (Dependabot, Snyk), regular updates, and a policy for responding to critical vulnerabilities (patch within 24 hours).
7. **Identification and Authentication Failures** — Weak password policies, missing MFA, session management flaws. Solution: require MFA, use secure session tokens (httpOnly, secure, SameSite), implement account lockout and rate limiting on login attempts.
8. **Software and Data Integrity Failures** — CI/CD pipeline compromises, dependency confusion attacks, deserialization of untrusted data. Solution: verify pipeline integrity (signed commits, reproducible builds), pin dependencies with checksums, validate deserialized data.
9. **Security Logging and Monitoring Failures** — Attacks go undetected because logging is insufficient or not monitored. Solution: log security-relevant events (authentication, authorization, data access), monitor logs for anomalies, set up alerts for suspicious activity.
10. **AI-Specific Risks** (added in 2038) — Prompt injection, model extraction, training data poisoning, adversarial inputs that cause misclassification. Solution: input filtering for AI endpoints, output verification (as covered in SD401's Valkyrie Protocol), rate limiting on AI endpoints, and human review for high-stakes AI outputs.

**Hardening Exercise.** For the capstone project, conduct a security hardening exercise using the OWASP checklist as a guide. For each item:

1. Is your system vulnerable?
2. If yes, what is the specific vulnerability?
3. What is the fix?
4. Implement the fix and verify with a security test.

**Dependency Security.** Modern applications depend on hundreds or thousands of third-party libraries. Each dependency is a potential vulnerability. Practice:

- **Dependency auditing** — Run `npm audit`, `pip audit`, or equivalent on every CI/CD run. Fail the build for critical vulnerabilities.
- **Dependency pinning** — Pin exact versions of all dependencies (including transitive dependencies) using lockfiles (package-lock.json, Pipfile.lock, Cargo.lock).
- **Dependency freshness** — Regularly update dependencies, but not blindly. Review changelogs, run tests, and deploy to staging before updating production.
- **Supply chain security** — Verify that dependencies come from the expected source (prevent dependency confusion attacks). Use signed packages where available.

#### Milestones (Week 8)
- OWASP Top 10 security review completed
- Automated security scanning integrated into CI/CD (dependency audit, static analysis, dynamic analysis)
- All critical and high vulnerabilities addressed
- Security documentation updated

#### Required Reading
- Vérdóttir, B. (2039). *The Builder's Codex*. Chapter 20.
- OWASP (2040). *OWASP Top 10 Web Application Security Risks — 2040 Edition*. [The definitive list, updated for AI-era threats.]
- Shostack, A. (2014). *Threat Modeling: Designing for Security*. Wiley. [Practical guide to threat modeling.]
- University of Yggdrasil (2040). *Security Hardening Checklist for Capstone Projects*. Technical Guide UoY-ENG-2040-07.

#### Discussion Questions
1. Your dependency audit reveals a critical vulnerability in a library you use extensively. The fix requires upgrading to a new major version that breaks your API. The alternative is to stay on the old version and mitigate the vulnerability with a workaround. Which do you choose, and why?
2. "Never trust the client" is a security principle — any validation done on the client must be repeated on the server. But double validation creates code duplication and potential inconsistency. How do you architect validation to be secure without being redundant?
3. Prompt injection is the #1 AI security risk in 2040. You're building a system that accepts user input and passes it to an LLM agent. What defenses can you implement? Hint: consider the layered defenses discussed in SD401.

---

### ᚻ Session 9: The Runes of Documentation — Writing for Future Maintainers

**Date:** Week 9

#### Overview

Runes were carved in stone and wood, meant to last for generations. Documentation is the runes of software — the permanent record that enables future developers (including your future self) to understand, use, and modify the system. This session covers the documentation that every capstone project must produce.

#### Working Notes

**Why Documentation Matters for Capstone Projects.** In industry, code is read far more often than it is written. The developers who maintain a system are rarely the ones who built it. Without documentation, they must reverse-engineer the system's design and intent from its code — a slow, error-prone process.

For capstone projects, documentation serves multiple purposes:

- **Portfolio** — Your capstone is the centerpiece of your professional portfolio. Good documentation demonstrates professionalism to potential employers.
- **Assessment** — The instructor assesses not just whether your system works, but whether it's maintainable. Good documentation is evidence of maintainability.
- **Handoff** — Some capstone projects are adopted by the University, open-sourced, or continued by other students. Documentation enables this handoff.
- **Your future self** — In six months, you won't remember why you made that design decision. Documentation is a gift to your future self.

**The Documentation Portfolio.** Every capstone project must produce:

*README.md.* The front door of the project. The README should enable a new developer to: (a) understand what the project does in 30 seconds, (b) get the project running locally in 5 minutes, and (c) find the documentation they need. Required sections: project name and description, badges (build status, coverage, license), quick start guide, links to full documentation, and team information.

*Architecture Decision Records (ADRs).* For every significant architectural decision, write an ADR. An ADR captures: the context (what was the situation?), the decision (what did we choose?), the consequences (what are the implications?), and the alternatives considered (what else did we think about?). ADRs prevent future developers from "fixing" decisions that were made for good reasons.

*API Documentation.* For every public API endpoint: description, method, path, request parameters, request body schema, response schema, authentication requirements, error codes, and example request/response. Use OpenAPI/Swagger for REST APIs, GraphQL introspection for GraphQL APIs, or Protobuf comments for gRPC.

*Database Schema Documentation.* For every table: name, description, columns (name, type, constraints, description), indices, and relationships. Tools like SchemaSpy or the University's *Yggdrasil Schema Doc* can generate this automatically, but you must review and supplement the generated output.

*Deployment Guide.* Step-by-step instructions for deploying the system to a new environment. Include: prerequisites, infrastructure requirements, configuration, database setup, and verification steps. The deployment guide should enable a DevOps engineer who has never seen the system to deploy it.

*Operations Guide.* How to operate the system in production: monitoring dashboards, alert configurations, common operational tasks (restarting services, scaling, backup/restore), and incident response procedures.

*Contributor Guide.* How to contribute to the project: development environment setup, coding standards, testing requirements, code review process, and issue tracking conventions. This is essential if the project will be open-sourced or continued by other students.

**Writing Good Documentation.** Documentation is a form of technical writing, and it benefits from the same principles as good code: clarity, concision, and structure.

- **Write for the reader, not for yourself.** You understand the system deeply; the reader doesn't. Assume the reader is a competent developer who knows nothing about your specific project.
- **Use examples generously.** A concrete example is worth a thousand abstract descriptions. Every API endpoint should have a curl example. Every configuration option should have a commented example.
- **Keep documentation close to code.** Documentation that lives far from the code it describes tends to go stale. Use tools that generate documentation from code (Javadoc, Sphinx, JSDoc, rustdoc) and embed documentation in the repository.
- **Treat documentation as a product.** Documentation has users (other developers) and must meet their needs. Solicit feedback on documentation, track documentation issues, and improve documentation iteratively.

#### Milestones (Week 9)
- README, ADRs, API docs, and database docs complete
- Deployment guide and operations guide drafted
- Documentation review with instructor

#### Required Reading
- Vérdóttir, B. (2039). *The Builder's Codex*. Chapter 21.
- Nygard, M. (2011). "Documenting Architecture Decisions." *Cognitect Blog*. [The original ADR proposal — widely adopted since.]
- Riona MacNamara, J. (2019). *Documentation in the Age of Agile*. Write the Docs Press. [Practical guide to documentation in fast-moving teams.]
- University of Yggdrasil (2040). *Capstone Documentation Standards*. Technical Guide UoY-ENG-2040-08.

#### Discussion Questions
1. "Good code is self-documenting" — some developers argue that if your code is clean enough, you don't need documentation. Where do you draw the line? What can't code express that documentation can?
2. Your team has 2 weeks left and several features to finish. Your documentation is incomplete. The product owner says "ship the features, we'll document later." How do you respond? What documentation is absolutely essential before shipping, and what can wait?
3. ADRs capture decisions made, but they don't capture decisions *not* made — the options that were never seriously considered. This creates a survivorship bias in the documentation: only the chosen option is documented, making it seem inevitable. How would you address this?

---

### ᚾ Session 10: The Launch — Production Deployment

**Date:** Week 10

#### Overview

The longship is built, tested, and provisioned. The crew is trained. The weather is favorable. It's time to launch — to push the ship into the water and set sail. In software, this is production deployment: the moment when your system goes live to real users.

#### Working Notes

**The Deployment Checklist.** Production deployment should never be ad-hoc. Follow a deployment checklist that covers every step:

*Pre-Deployment (in Staging).*
- [ ] All tests pass (unit, integration, E2E, performance, security)
- [ ] Code review complete and approved
- [ ] Documentation updated (README, API docs, deployment guide)
- [ ] Database migrations tested on a copy of production data
- [ ] Load tests pass at expected production volume
- [ ] Security scan shows no critical or high vulnerabilities
- [ ] Dependencies are up to date (or known vulnerabilities are accepted and documented)
- [ ] Monitoring and alerting configured
- [ ] Backup and restore tested

*Deployment.*
- [ ] Deployment approved (by team lead and instructor)
- [ ] Maintenance window communicated to users (if applicable)
- [ ] Database migrations applied (with rollback plan if migrations fail)
- [ ] Services deployed (blue-green or rolling)
- [ ] Health checks pass
- [ ] Smoke tests pass

*Post-Deployment (in Production).*
- [ ] Monitor for 30 minutes: error rate, latency, throughput, resource utilization
- [ ] Verify critical user flows end-to-end
- [ ] Verify monitoring dashboards and alerts
- [ ] Communicate deployment status to stakeholders
- [ ] If issues detected, execute rollback plan

**The Rollback Plan.** Every deployment must have a rollback plan. If the deployment causes problems, you must be able to revert to the previous working state quickly and safely.

Rollback strategies:
- **Blue-Green Rollback** — Switch traffic back to the old (blue) environment. Fastest and safest: typically under 1 minute.
- **Rolling Rollback** — Redeploy the previous version. Slower but doesn't require duplicate infrastructure.
- **Database Migration Rollback** — The hardest part to roll back. Database migrations should be: (a) reversible (every migration has a down migration), (b) backward-compatible (the old code works with the new schema), and (c) tested (rollback is practiced in staging).

**What to Do When Deployment Goes Wrong.** Deployments will go wrong. The sign of a professional team is not that deployments always succeed — it's that the team handles failures calmly and effectively.

If the deployment fails:
1. **Don't panic.** Deployment failures are normal. The rollback plan exists for this reason.
2. **Assess the impact.** Is the system down, degraded, or functioning with minor issues? Different impacts warrant different responses.
3. **Decide: roll back or fix forward?** If the issue can be fixed quickly (minutes), fix forward. If the fix will take longer, roll back. The priority is restoring service to users.
4. **Execute the rollback** (if chosen). Follow the rollback plan. Verify that the system is healthy after rollback.
5. **Investigate the root cause.** What went wrong? Was it a code bug, a configuration error, an infrastructure issue, or a process failure?
6. **Prevent recurrence.** Update the deployment checklist, add a test, improve monitoring — whatever prevents this failure from happening again.

**Going Live: The Psychological Moment.** For many students, production deployment is the first time their code serves real users. This is a significant psychological moment — it's natural to feel anxious, excited, and vulnerable. Your code, which you've been carefully crafting and testing for weeks, is now exposed to the world.

Remember: deployment is not the end. It's the beginning of the operational phase of your project. The system will have bugs you didn't find in testing. Users will use it in ways you didn't anticipate. There will be incidents. This is normal. The measure of a good developer is not avoiding all problems — it's handling problems when they occur, learning from them, and improving.

#### Milestones (Week 10)
- Production deployment completed
- Deployment checklist executed and signed off
- System healthy in production (verified by 30-minute monitoring window)
- Rollback plan documented and tested
- Post-deployment retrospective conducted

#### Required Reading
- Vérdóttir, B. (2039). *The Builder's Codex*. Chapter 22.
- Allspaw, J., & Hammond, P. (2012). "10+ Deploys Per Day: Dev and Ops Cooperation at Flickr." *Velocity 2009*. [The talk that launched the DevOps movement.]
- Limoncelli, T., et al. (2015). *The Practice of Cloud System Administration*. Addison-Wesley. Chapters on deployment and incident response.
- University of Yggdrasil (2040). *Production Deployment Checklist and Standards*. Technical Guide UoY-ENG-2040-09.

#### Discussion Questions
1. You're deploying on Friday at 4 PM. A teammate warns "never deploy on Friday" — if something goes wrong, you'll be debugging all weekend. The product owner wants the feature live for a Monday demo. What do you do?
2. Database migrations are the hardest thing to roll back. You need to add a NOT NULL column to a table with 10 million rows. What strategies can you use to make this migration safe and reversible?
3. Your smoke tests pass in production, but 10 minutes after deployment, users start reporting errors. The monitoring dashboard shows error rate spiking. Your teammate says "roll back immediately." You say "let me investigate for 5 minutes first." Who is right? When should you investigate vs. roll back?

---

### ᛁ Session 11: The Watch on the Mast — Monitoring and Incident Response

**Date:** Week 11

#### Overview

On a longship, a crew member was always on watch — scanning the horizon for danger, weather, or land. In production software, monitoring is the watch: the continuous observation of the system's behavior, looking for anomalies that indicate problems. This session covers production monitoring, alerting, and incident response — the operational disciplines that keep a deployed system healthy.

#### Working Notes

**Observability in Production.** Observability (as discussed in SD401, Lecture 8) is the ability to understand the internal state of a system from its external outputs. In production, observability is not optional — it's the difference between knowing about a problem before users report it, and learning about it from angry users.

The three pillars of observability, applied to production:

- **Logs** — Structured JSON logs for every significant event: requests, responses, errors, authentication events, data access. The University's Mímir log format provides a standard schema. Logs must be centralized (shipped to a log aggregator), searchable, and retained for at least 30 days.
- **Metrics** — Numerical measurements of system behavior: request latency (P50, P95, P99), error rate, throughput, CPU/memory/disk utilization, database query times, cache hit rates, queue depths. Metrics enable dashboards (visual overview of system health) and alerts (notifications when metrics cross thresholds).
- **Traces** — End-to-end request flows through the system. A trace shows every service and database call that a single request made, with timing for each. Traces enable root cause analysis: when a request is slow, you can see exactly which step caused the delay.

**Alerting.** Alerts notify the team when something needs attention. Good alerting is the difference between proactive operations (you fix problems before users notice) and reactive operations (users tell you about problems).

Good alerting principles:
- **Alert on symptoms, not causes.** "Error rate > 1%" is a symptom — it tells you something is wrong. "CPU > 90%" is a cause — it might be a problem, or it might be normal. Alert on the symptom, use the cause for investigation.
- **Every alert must require human action.** If an alert fires and the correct response is "ignore it," the alert is noise. Noise breeds alert fatigue, which causes real alerts to be ignored.
- **Every alert must have a runbook.** A runbook is a documented procedure for responding to the alert: what does this alert mean, what should you check first, what are common causes, what are the escalation paths. Without a runbook, the on-call engineer is left guessing at 3 AM.
- **Alerts have severity levels.** Critical (page the on-call engineer immediately), Warning (notify during business hours), Info (log for later analysis). Not everything that's interesting is actionable.

**Incident Response.** When something goes wrong in production — an outage, a data loss, a security breach — the team must respond effectively. Incident response is a skill that must be practiced, not improvised.

The University's *Heimdallr Incident Response Protocol*:

1. **Detect** — The incident is detected by monitoring, a user report, or a team member. Acknowledge the incident immediately (even if you don't know the cause). "I see the alert. I'm investigating."
2. **Triage** — Assess severity. Is this a minor issue (affects few users, workaround exists) or a major incident (system down, data loss, security breach)? Severity determines the response priority and escalation.
3. **Coordinate** — Assign roles: Incident Commander (coordinates the response), Communications Lead (keeps stakeholders informed), and Investigators (diagnose the problem). The Incident Commander's job is not to fix the problem — it's to keep the team organized and making progress.
4. **Mitigate** — Stop the bleeding. This might mean: rolling back a deployment, failing over to a backup, blocking an attacker's IP, or turning off a broken feature. Mitigation comes before root cause analysis — restore service first, understand why it broke later.
5. **Resolve** — Fix the root cause. This might take minutes (a misconfiguration) or days (a subtle race condition). The incident is not resolved until the root cause is fixed and verified.
6. **Learn** — After every incident, conduct a blameless postmortem: what happened, why, how did we detect it (or why didn't we), how did we respond, and what will we do to prevent recurrence. The postmortem's purpose is learning and improvement, not assigning blame.

**Blameless Postmortems.** The "blameless" in blameless postmortem is essential. If people fear punishment for incidents, they will hide incidents, delay reporting, and shift blame. A blameless culture treats incidents as learning opportunities: "We made a mistake. What can we learn from it so it doesn't happen again?"

A good postmortem answers:
- What was the impact (users affected, duration, data lost)?
- What was the timeline (detection, response, mitigation, resolution)?
- What was the root cause?
- What went well in our response?
- What went poorly?
- What action items will prevent recurrence?
- Where did we get lucky (things that could have been worse)?

#### Milestones (Week 11)
- Monitoring dashboards configured and operational
- Alerts configured for critical metrics with runbooks
- Incident response roles assigned and documented
- At least one incident simulation (tabletop exercise) conducted

#### Required Reading
- Vérdóttir, B. (2039). *The Builder's Codex*. Chapter 23.
- Beyer, B., et al. (2016). *Site Reliability Engineering*. O'Reilly. Chapters on monitoring, alerting, and incident response. [The SRE bible.]
- Allspaw, J. (2012). "Blameless PostMortems and a Just Culture." *Etsy Code as Craft*. [The foundational text on blameless incident response.]
- University of Yggdrasil (2040). *Heimdallr Incident Response Protocol*. Technical Guide UoY-ENG-2040-10.

#### Discussion Questions
1. Your system has been in production for a week with no incidents. You're getting false confidence — "our system is rock solid." Then a user reports a bug that's been silently corrupting data for the entire week. Your monitoring didn't detect it because you only monitored system metrics, not data quality. How would you expand your monitoring to catch data corruption?
2. A critical alert fires at 3 AM Saturday. The on-call engineer is asleep and doesn't respond for 45 minutes. During that time, the system is down. In the postmortem, how do you address the response delay without blaming the engineer? What systemic changes would prevent this?
3. "Every alert must have a runbook." But for a capstone project that's only been in production for 2 weeks, you don't have enough operational experience to write runbooks for every alert. How do you bootstrap runbooks? What's the minimum viable runbook?

---

### ᛏ Session 12: The Saga is Told — Final Presentation and Portfolio

**Date:** Week 12

#### Overview

The Vikings told sagas — long-form narratives that preserved the history, values, and achievements of their people. A capstone project is a saga: the story of what you built, how you built it, what you learned, and why it matters. This final session covers the capstone presentation, the portfolio defense, and the transition from student to professional.

#### Working Notes

**The Capstone Presentation.** The capstone presentation is a 20-minute presentation to a panel of faculty and industry reviewers. It is the public defense of your project and your learning. The presentation should tell the story of your project:

1. **The Problem (2 minutes).** What problem does your system solve? Why does it matter? Who are the users? Establish the context and the stakes.
2. **The Solution (5 minutes).** Demonstrate the system live. Show the key features, the user experience, and the technical highlights. A live demo is worth a thousand slides — but have a backup video in case of demo failure.
3. **The Architecture (5 minutes).** How is the system built? Show the key architectural decisions: technology stack, data model, component architecture, deployment architecture. Explain the trade-offs you made and why.
4. **The Process (3 minutes).** How did you build it? Show the development process: sprints, CI/CD pipeline, testing strategy, code review practices. Demonstrate that you can operate as a professional team.
5. **The Learnings (3 minutes).** What did you learn? What would you do differently? What are you proud of? This is the most important part of the presentation — it shows self-awareness and growth.
6. **Q&A (2 minutes).** Answer questions from the panel. Be honest about what you don't know and what you'd improve.

**The Portfolio Defense.** In addition to the presentation, each student must submit a portfolio that demonstrates their individual contribution to the project. The portfolio includes:

- **Project summary** — What was the project, what was your role, what did you personally build?
- **Code samples** — 3-5 representative code samples that you wrote, with annotations explaining your design decisions.
- **Design artifacts** — Architecture diagrams, ADRs, API specifications that you contributed to.
- **Testing evidence** — Test suites you wrote, performance tests you conducted, security reviews you performed.
- **Reflection** — A 500-word reflection on your growth over the course of the project and the program.

The portfolio defense is a 15-minute individual meeting with the instructor, where you present your portfolio and answer questions about your contributions and your learning.

**From Student to Professional.** The capstone is the bridge between student and professional life. The skills you've demonstrated — building production-quality software, working in a team, testing rigorously, deploying safely, monitoring proactively — are the skills that employers seek.

As you prepare to graduate, reflect on the journey:
- What skills did you have when you started the program?
- What skills do you have now?
- What kind of developer do you want to be?
- What kind of problems do you want to solve?
- What kind of team do you want to work with?

These questions are more important than any technical skill. Your career will span decades. The technologies you've learned will change. The principles — building with craft, testing with rigor, deploying with courage, and maintaining with discipline — will endure.

**Course Conclusion.** This course has been a journey from the keel (architecture and planning) to the saga (presentation and reflection). You've built a production-quality software system, tested it comprehensively, deployed it to production, and monitored it in operation. You've practiced the professional disciplines that distinguish a software developer from a code writer.

The longship metaphor has carried us through the course because it captures something essential about software development: it is a craft, practiced by skilled individuals working together, to create something that serves a purpose in the world. A longship wasn't built for its own sake — it was built to carry people and goods across the sea. Software isn't built for its own sake — it's built to solve problems for people.

As you launch your careers, remember the builder's codex: build with craft, test with rigor, deploy with courage, maintain with discipline, and always — always — serve the users who depend on your work.

#### Milestones (Week 12)
- Capstone presentation delivered to faculty and industry panel
- Portfolio submitted and defended
- Project repository archived (or handed off to maintainers)
- Production system handed off or decommissioned

#### Required Reading
- Vérdóttir, B. (2039). *The Builder's Codex*. Chapter 24 and Afterword.
- Re-read your own project documentation, code, and reflection. The final examination is a synthesis of everything you've learned and built.

#### Discussion Questions
1. Looking back at your project, what's the one thing you're most proud of? What's the one thing you'd do differently if you could start over?
2. The capstone presentation is your last chance to impress the faculty panel. What's your strategy? Do you focus on the technical brilliance of your architecture, the business value of your solution, or the elegance of your process? What story do you want to tell?
3. In 5 years, when you look back at this project, what do you hope you'll think? What standard are you setting for your future self?

---

## Final Examination Preparation

The final examination for SD405 is a **Capstone Defense Portfolio**, consisting of three components:

### Component 1: Project Summary (30%)

Write a 1,000-1,500 word executive summary of your capstone project, addressed to a technical manager who is considering you for a job. Cover: the problem you solved, the architecture you built, the key technical decisions you made (and why), the challenges you encountered, and what you learned. This is a portfolio document — it should be polished, professional, and persuasive.

### Component 2: Code Walkthrough (40%)

Select three significant pieces of code you personally wrote. For each:
1. Present the code (with context — what does this code do, and where does it fit in the system?)
2. Explain your design decisions (why did you write it this way?)
3. Reflect on the code (what would you do differently now? What are you proud of?)

The code walkthrough is assessed on: the quality of the code, the depth of your design reasoning, and the honesty of your reflection.

### Component 3: Capstone Reflection (30%)

Write a 1,500-2,000 word personal reflection on your capstone experience. Address:
- Your growth as a software developer over the course of the project
- Your contribution to the team and the project
- The most challenging moment of the project and how you handled it
- The most rewarding moment of the project
- How this project has prepared you for your career
- What kind of developer you want to be, and how you plan to get there

The reflection is assessed on: depth of self-awareness, honesty about challenges and failures, and evidence of learning and growth.

---

*Course content developed by Brynhildr Vérdóttir, Faculty of Software Engineering, University of Yggdrasil. Last updated: 2040.*