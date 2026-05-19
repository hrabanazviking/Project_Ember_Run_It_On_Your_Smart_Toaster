# IT405: Capstone Project I — Infrastructure Design
## Bachelor of Science in Information Technology — University of Yggdrasil, 2040

**Credits:** 4
**Prerequisites:** Senior standing, completion of all Year 1-3 IT core courses
**Description:** The first semester of the two-semester capstone sequence. Students propose, design, and begin implementation of a substantial infrastructure project demonstrating mastery of the IT program's core competencies. Emphasis on requirements analysis, architecture design, project planning, and professional practice.

---

## Lectures

## Lecture 1: The Capstone Vision — What Makes a Great Project

### 1.1 Overview

What distinguishes a great capstone from a mediocre one? This lecture establishes criteria: technical depth, real-world relevance, demonstrated mastery of core competencies, and professional-quality deliverables. Students explore past capstone examples and begin ideating their own projects.

### 1.2 Key Topics

- **Evaluation Criteria:** (1) **Technical depth** — does the project demonstrate advanced IT skills beyond basic CRUD applications? (2) **Real-world relevance** — does it solve an actual problem or address a genuine need? (3) **Core competency coverage** — does it span multiple domains (systems, networking, security, databases, automation)? (4) **Professional quality** — would you show this to an employer?
- **Project Categories:** (1) **Infrastructure automation** — building CI/CD pipelines, self-service platforms, monitoring systems; (2) **Security architecture** — zero-trust implementation, security operations platform, threat detection; (3) **Data platform** — database cluster with HA/DR, data pipeline, analytics platform; (4) **Edge/IoT system** — distributed sensor network with edge processing; (5) **Service management** — ITSM platform, automated incident management; (6) **Research** — empirical study of IT practices, novel architecture evaluation.
- **Past Exemplars:** (1) "Yggdrasil Monitor" — an AI-driven observability platform predicting failures in the university's infrastructure; (2) "Ragnarök Recovery" — automated DR orchestration achieving 4-minute RTO; (3) "Freyja's Firewall" — zero-trust microsegmentation for a simulated enterprise.

### 1.3 Required Reading
- UoY Capstone Archive. (2039). *Exemplary Capstone Projects 2035-2039*.

### 1.4 Discussion Questions
1. How do you balance ambition with feasibility when scoping a capstone project?
2. What are the dangers of choosing a project that is too narrow (only tests one skill) versus too broad (never finishes)?
3. How can you leverage your capstone to demonstrate skills that employers in your target field actually care about?

---

## Lecture 2: Requirements Discovery — Understanding What to Build

### 2.1 Overview

The most common cause of project failure is building the wrong thing. This lecture covers requirements discovery: stakeholder interviews, user stories, use cases, functional and non-functional requirements, and the art of distinguishing needs from wants.

### 2.2 Key Topics

- **Requirements Elicitation Techniques:** (1) stakeholder interviews; (2) observation of current workflows; (3) document analysis; (4) competitive analysis of existing solutions; (5) prototyping and feedback. By 2040, AI-assisted requirements analysis suggests overlooked requirements based on similar projects.
- **Functional vs. Non-Functional Requirements:** Functional: what the system does. Non-functional: how well it does it — performance, reliability, security, scalability, maintainability, usability. Non-functional requirements are frequently neglected but often determine project success. Example: "The monitoring system shall detect anomalies within 30 seconds (non-functional) and provide root cause hypotheses with >85% accuracy (functional)."
- **Prioritization:** MoSCoW method: Must have, Should have, Could have, Won't have (this iteration). Forces explicit prioritization — everything can't be highest priority. Helps manage scope creep.

### 2.3 Required Reading
- Wiegers, K., & Beatty, J. (2038). *Software Requirements* (4th ed.). Microsoft Press.

### 2.4 Discussion Questions
1. How do you handle conflicting requirements from different stakeholders?
2. What techniques exist for uncovering latent needs that stakeholders cannot articulate?
3. How does the MoSCoW method change when you have a hard deadline versus flexible timing?

---

## Lecture 3: Architecture Design — From Requirements to Blueprint

### 3.1 Overview

Architecture transforms requirements into a technical blueprint. This lecture covers architecture design: architectural drivers, design patterns, trade-off analysis, and the Architecture Decision Record (ADR) practice.

### 3.2 Key Topics

- **Architecture Drivers:** (1) functional requirements; (2) quality attribute requirements (the "-ilities": reliability, scalability, security, maintainability); (3) constraints (budget, timeline, technology, compliance); (4) architectural principles and conventions. The architect's job: satisfy the drivers within the constraints.
- **Documenting Architecture:** (1) C4 model — Context (system in its environment), Container (high-level components), Component (within containers), Code (implementation details); (2) Architecture Decision Records (ADRs) — document significant decisions with context, options considered, rationale, and consequences; (3) Diagrams as code — use PlantUML, Mermaid, or Structurizr DSL so diagrams are version-controlled and reviewable.
- **Trade-off Analysis:** Every architectural decision involves trade-offs. The Architecture Trade-off Analysis Method (ATAM): (1) identify architectural approaches; (2) generate quality attribute utility tree; (3) analyze approaches against scenarios; (4) identify sensitivities (attributes affected by the decision), trade-offs (decisions that improve one attribute at the expense of another), and risks.

### 3.3 Required Reading
- Richards, M., & Ford, N. (2038). *Fundamentals of Software Architecture* (Updated ed.). O'Reilly Media.
- UoY Architecture Lab. (2039). *ADR Template and Examples*.

### 3.4 Discussion Questions
1. When is it appropriate to defer an architectural decision until later in the project?
2. How do you communicate architectural trade-offs to non-technical stakeholders?
3. What are the limitations of the C4 model, and when would you use a different architectural diagramming approach?

---

## Lecture 4: Technology Selection and Justification

### 4.1 Overview

Choosing the right technology is a core IT competency. This lecture covers technology evaluation: selection criteria, proof-of-concept prototyping, build-vs-buy analysis, and justifying choices with evidence.

### 4.2 Key Topics

- **Selection Criteria:** (1) functional fit; (2) non-functional fit (performance, security, scalability); (3) total cost of ownership (TCO); (4) vendor lock-in and exit strategy; (5) community and support; (6) future roadmap and innovation potential.
- **Proof-of-Concept Prototyping:** Time-boxed experiments to validate technical assumptions: (1) spike solutions for risky components; (2) benchmarking performance under load; (3) integration testing with existing systems; (4) security testing for compliance requirements.
- **Build-vs-Buy Analysis:** (1) developing custom solutions vs. purchasing commercial off-the-shelf (COTS); (2) evaluating open-source alternatives; (3) considering hybrid approaches; (4) factoring in opportunity cost of development time.
- **Justification with Evidence:** (1) decision matrices with weighted criteria; (2) cost-benefit analysis over 3-5 year horizon; (3) risk assessment of each option; (4) prototyping results and user feedback.

### 4.3 Required Reading
- UoY Capstone Archive. (2039). *Technology Selection Case Studies*.
- Gartner, Inc. (2040). *Magic Quadrant for Infrastructure Automation Platforms*.

### 4.4 Discussion Questions
1. How do you evaluate emerging technologies that lack long-term track records?
2. What is the role of prototyping in reducing technology selection risk?
3. How should you handle a situation where the best technical solution exceeds the budget?

---

## Lecture 5: Project Planning — Turning Design into Action

### 5.1 Overview

A great design means nothing without execution. This lecture covers project planning: work breakdown structures, effort estimation, dependency mapping, and agile vs. traditional methodologies for capstone projects.

### 5.2 Key Topics

- **Work Breakdown Structure (WBS):** (1) decomposing deliverables into work packages; (2) identifying milestones and phases; (3) assigning ownership and accountability; (4) creating a hierarchical view of the project.
- **Effort Estimation:** (1) expert judgment based on past projects; (2) analogy to similar completed work; (3) parametric models using lines of code or function points; (4) three-point estimation (optimistic, most likely, pessimistic).
- **Dependency Mapping:** (1) finish-to-start, start-to-start, finish-to-finish, start-to-finish dependencies; (2) critical path identification; (3) resource leveling and smoothing; (4) identifying bottlenecks and constraints.
- **Agile vs. Traditional:** (1) Scrum adaptations for capstone (2-week sprints, demo days); (2) Kanban for continuous flow of deliverables; (3) Waterfall for regulated or hardware-heavy projects; (4) hybrid models that combine upfront architecture with iterative implementation.

### 5.3 Required Reading
- Project Management Institute. (2038). *A Guide to the Project Management Body of Knowledge (PMBOK® Guide)* — 8th ed.
- UoY Capstone Archive. (2039). *Project Planning Templates and Examples*.

### 5.4 Discussion Questions
1. How do you estimate effort for tasks you've never done before?
2. What are the advantages and disadvantages of using story hours versus story points for estimation?
3. How does project planning change when you are both the project manager and the primary developer?

---

## Lecture 6: Risk Management — Anticipating and Mitigating Failure

### 6.1 Overview

Every project faces uncertainty. This lecture covers risk management: identification, analysis, response planning, and monitoring throughout the capstone lifecycle.

### 6.2 Key Topics

- **Risk Identification:** (1) brainstorming sessions with stakeholders; (2) checklists from past projects; (3) SWOT analysis (strengths, weaknesses, opportunities, threats); (4) premise examination (what assumptions are we making?).
- **Risk Analysis:** (1) qualitative: probability and impact matrices; (2) quantitative: expected monetary value, Monte Carlo simulation; (3) risk ranking and prioritization.
- **Risk Response Planning:** (1) avoid: change plans to eliminate the risk; (2) transfer: insurance, outsourcing, warranties; (3) mitigate: reduce probability or impact; (4) accept: contingency reserves, fallback plans.
- **Risk Monitoring:** (1) regular risk reviews; (2) triggering conditions and early warning signs; (3) updating risk probability and impact; (4) communicating risk status to stakeholders.

### 6.3 Required Reading
- UoY Capstone Archive. (2039). *Risk Management in IT Capstones*.
- Project Management Institute. (2038). *Practice Standard for Project Risk Management*.

### 6.4 Discussion Questions
1. What are the most common risks in IT infrastructure capstone projects?
2. How do you balance risk mitigation efforts with limited time and resources?
3. When is it appropriate to accept a risk rather than try to mitigate it?

---

## Lecture 7: Implementation Foundations — Setting Up for Success

### 7.1 Overview

Before writing code, you need the right foundations. This lecture covers implementation setup: version control, development environments, CI/CD pipelines, and coding standards.

### 7.2 Key Topics

- **Version Control:** (1) Git branching strategies (GitFlow, GitHub Flow, trunk-based); (2) commit message conventions; (3) pull request reviews and approvals; (4) tagging releases and tracking issues.
- **Development Environments:** (1) local vs. cloud-based IDEs; (2) containerized development with Docker; (3) infrastructure as code (IaC) for reproducible environments; (4) remote development and pair programming tools.
- **CI/CD Pipelines:** (1) continuous integration: automated testing on every commit; (2) continuous delivery: automated deployment to staging; (3) continuous deployment: automated deployment to production; (4) pipeline as code (Jenkinsfile, .gitlab-ci.yml, GitHub Actions).
- **Coding Standards and Quality:** (1) language-specific linters and formatters; (2) static analysis tools for security and bugs; (3) code coverage targets for unit tests; (4) technical debt tracking and remediation.

### 7.3 Required Reading
- Chacon, S., & Straub, B. (2038). *Pro Git* (3rd ed.).
- Humble, J., & Farley, D. (2038). *Continuous Delivery: Reliable Software Releases through Build, Test, and Deployment Automation* (2nd ed.). Addison-Wesley Professional.

### 7.4 Discussion Questions
1. What are the trade-offs between feature branching and trunk-based development for a solo capstone project?
2. How much effort should you invest in setting up CI/CD versus writing features?
3. How do you enforce coding standards when you are the only developer?

---

## Lecture 8: Implementation Core — Building the Solution

### 8.1 Overview

This lecture covers the heart of implementation: writing code, configuring infrastructure, integrating components, and managing technical complexity as the project grows.

### 8.2 Key Topics

- **Modular Design:** (1) separation of concerns; (2) loose coupling and high cohesion; (3) interfaces and contracts between modules; (4) plugin architectures for extensibility.
- **Infrastructure as Code:** (1) declarative vs. imperative IaC; (2) Terraform modules for reusable components; (3) AWS CDK, Pulumi, or Azure Bicep for programmatic infrastructure; (4) testing IaC with Terratest, Checkov, or Conftest.
- **Database Development:** (1) schema design and migration tools (Flyway, Liquibase, Alembic); (2) seeding strategies for development and testing; (3) performance testing with realistic data volumes; (4) backup and restore procedures.
- **API Development:** (1) RESTful design principles; (2) GraphQL for flexible data fetching; (3) gRPC for high-performance internal services; (4) API documentation with OpenAPI/Swagger; (5) rate limiting, authentication, and versioning.
- **Frontend Development:** (1) component-based frameworks (React, Vue, Svelte); (2) state management (Redux, Vuex, Pinia); (3) UI component libraries (Material-UI, Ant Design); (4) accessibility (WCAG 2.2) and responsive design.

### 8.3 Required Reading
- Fowler, M. (2038). *Patterns of Enterprise Application Architecture*.
- Newman, S. (2038). *Building Microservices: Designing Fine-Grained Systems* (2nd ed.). O'Reilly Media.
- UoY Capstone Archive. (2039). *Implementation Patterns and Examples*.

### 8.4 Discussion Questions
1. How do you decide when to extract a module versus keeping code together?
2. What are the challenges of managing database schema changes in a team environment?
3. How do you balance development speed with code quality and maintainability?

---

## Lecture 9: Testing and Quality Assurance — Building Confidence

### 9.1 Overview

Testing is not a phase — it is a continuous activity. This lecture covers testing strategies: unit, integration, system, and acceptance testing, plus non-functional testing for performance, security, and usability.

### 9.2 Key Topics

- **Testing Pyramid:** (1) unit tests: fast, isolated, high volume; (2) integration tests: testing interactions between components; (3) system tests: end-to-end scenarios in production-like environments; (4) acceptance tests: validating against user requirements and business goals.
- **Test Automation:** (1) unit testing frameworks (JUnit, PyTest, NUnit, Jest); (2) integration testing with test containers and service virtualization; (3) UI testing with Selenium, Cypress, or Playwright; (4) continuous testing in CI/CD pipelines.
- **Non-Functional Testing:** (1) performance testing: load, stress, spike, and endurance tests; (2) security testing: vulnerability scanning, penetration testing, code review; (3) usability testing: user feedback, heuristic evaluation, A/B testing; (4) chaos engineering: injecting failures to test resilience.
- **Test Data Management:** (1) synthetic data generation; (2) data masking and anonymization for production data; (3) test data versioning and refresh strategies; (4) data subsetting for efficient testing.

### 9.3 Required Reading
- Astels, D. (2038). *Test-Driven Development: A Practical Guide*.
- OWASP Foundation. (2040). *OWASP Testing Guide v5*.
- UoY Capstone Archive. (2039). *Testing Strategies for IT Capstones*.

### 9.4 Discussion Questions
1. How do you determine what to test at each level of the testing pyramid?
2. What are the challenges of testing infrastructure-as-code compared to application code?
3. How do you balance automated testing with exploratory manual testing?

---

## Lecture 10: Deployment and Release Management — Getting It to Users

### 10.1 Overview

Building the right thing is only half the battle — getting it to users reliably and safely is the other half. This lecture covers deployment strategies, release management, and operational handoff.

### 10.2 Key Topics

- **Deployment Strategies:** (1) big bang vs. phased rollout; (2) blue-green deployments; (3) canary releases; (4) feature flags and dark launching.
- **Release Management:** (1) versioning strategies (semantic versioning, calendar versioning); (2) release notes and changelogs; (3) rollback procedures and point-in-time recovery; (4) hotfix processes for production incidents.
- **Infrastructure Deployment:** (1) immutable infrastructure and golden images; (2) configuration management (Ansible, Chef, Puppet, SaltStack); (3) container orchestration (Kubernetes, Docker Swarm, Nomad); (4) serverless deployment (AWS Lambda, Azure Functions, Google Cloud Run).
- **Monitoring and Observability:** (1) metrics collection (Prometheus, StatsD, CloudWatch); (2) distributed tracing (Jaeger, Zipkin, OpenTelemetry); (3) centralized logging (ELK stack, Fluentd, Loki); (4) alerting and incident response (PagerDuty, VictorOps, Opsgenie).
- **Operational Handoff:** (1) runbooks and standard operating procedures; (2) knowledge transfer sessions; (3) support rotations and escalation procedures; (4) service level agreements (SLAs) and error budgets.

### 10.3 Required Reading
- Humble, J., & Farley, D. (2038). *Continuous Delivery: Reliable Software Releases through Build, Test, and Deployment Automation* (2nd ed.). Addison-Wesley Professional.
- Google, Inc. (2038). *Site Reliability Engineering: How Google Runs Production Systems* (Updated ed.).
- UoY Capstone Archive. (2039). *Deployment Patterns and Examples*.

### 10.4 Discussion Questions
1. When is a blue-green deployment overkill for a capstone project?
2. How do you handle database migrations in a zero-downtime deployment strategy?
3. What level of monitoring is appropriate for a student project versus a production enterprise system?

---

## Lecture 11: Documentation and Knowledge Transfer — Making It Last

### 11.1 Overview

If it's not documented, it didn't happen. This lecture covers documentation strategies: technical documentation, user guides, architectural decisions, and lessons learned.

### 11.2 Key Topics

- **Technical Documentation:** (1) API references with examples; (2) architecture diagrams and C4 models; (3) setup and installation guides; (4) troubleshooting guides and FAQs; (5) code comments and self-documenting code practices.
- **User Documentation:** (1) user manuals and step-by-step guides; (2) video tutorials and screencasts; (3) help systems and context-sensitive help; (4) accessibility considerations for documentation.
- **Architecture Decision Records (ADRs):** (1) capturing significant architectural choices; (2) linking ADRs to code and diagrams; (3) maintaining a living record of why the system is the way it is; (4) using ADRs for onboarding and audits.
- **Lessons Learned:** (1) structured retrospectives (what went well, what didn't, what to try next time); (2) capturing quantitative metrics (defects, velocity, estimate accuracy); (3) sharing knowledge with future capstone teams; (4) creating a personal portfolio artifact.
- **Documentation Tools:** (1) static site generators (MkDocs, Docusaurus, Hugo); (2) wiki systems (Confluence, Notion, GitBook); (3) diagram-as-code tools (Mermaid, PlantUML, Structurizr); (4) version control for documentation.

### 11.3 Required Reading
- Thomas, D., & Hunt, A. (2038). *Pragmatic Documentation: Writing That Gets Read and Used*.
- UoY Capstone Archive. (2039). *Documentation Templates and Examples*.
- The Documentation Community. (2040). *Write the Docs Guide*.

### 11.4 Discussion Questions
1. How do you balance writing documentation with writing code when time is limited?
2. What makes documentation actually useful versus just checking a box?
3. How should you document failures and mistakes in a way that is helpful rather than embarrassing?

---

## Lecture 12: Presentation and Reflection — Telling Your Story

### 12.1 Overview

The capstone culminates in a formal presentation where you showcase your work, reflect on your learning, and prepare for the next steps in your career.

### 12.2 Presentation Preparation

- **Slide Deck Structure:** (1) problem statement and motivation; (2) requirements and objectives; (3) architecture and design decisions; (4) implementation highlights and challenges; (5) results and demonstrations; (6) lessons learned and future work; (7) Q&A preparation.
- **Demo Readiness:** (1) rehearsing the demo sequence; (2) having backup plans for technical failures; (3) preparing screenshots and videos as fallbacks; (4) ensuring all credentials and access work in the presentation environment.
- **Storytelling Techniques:** (1) the hero's journey applied to your project; (2) using data and metrics to support claims; (3) highlighting personal growth and skill development; (4) connecting to broader industry trends.

### 12.3 Reflection and Portfolio

- **Technical Reflection:** (1) what technical skills did you develop or improve? (2) what did you learn about architecture, design, or implementation? (3) what would you do differently if you started over?
- **Professional Reflection:** (1) how did you handle ambiguity and changing requirements? (2) how did you manage time and prioritize tasks? (3) what did you learn about working independently and seeking help?
- **Portfolio Preparation:** (1) selecting artifacts that demonstrate your best work; (2) writing clear descriptions of your role and contributions; (3) preparing code samples and architecture diagrams; (4) creating a one-page summary for recruiters.
- **Future Steps:** (1) leveraging the capstone in job interviews and applications; (2) identifying gaps for continued learning; (3) considering the capstone as a foundation for IT406 Capstone Project II; (4) exploring certifications, internships, or further education.

### 12.4 Required Reading
- Duarte, N. (2038). *Resonate: Present Visual Stories that Transform Audiences*.
- UoY Capstone Archive. (2039). *Presentation Templates and Examples*.
- Kruppa, Y. (2038). *The 2-Hour Job Search: Using Technology to Get the Right Job Faster*.

### 12.5 Discussion Questions
1. How do you handle nervousness or anxiety when presenting your work?
2. What makes a capstone presentation memorable versus forgettable?
3. How do you translate capstone experience into bullet points on a resume?

---

## Final Examination Preparation

### Format
The final assessment consists of two components:

**Part A — Project Documentation (60%):** Submit a complete project package including: requirements document, architecture diagrams, ADRs, implementation evidence (code repositories, build logs), test results, deployment evidence, user documentation, and lessons learned.

**Part B — Presentation and Demonstration (40%):** A 20-minute live presentation followed by 10 minutes of Q&A. You will demonstrate your working system, walk through key architectural decisions, and reflect on your learning journey.

### Part A — Project Documentation Checklist

1. **Vision and Scope** — Problem statement, objectives, success criteria
2. **Requirements** — Functional and non-functional requirements, prioritization (MoSCoW)
3. **Architecture** — C4 diagrams, ADRs, technology choices with justification
4. **Project Plan** — Work breakdown structure, timeline, milestones, risk register
5. **Implementation** — Code repository (with commit history), build instructions, deployment scripts
6. **Testing** — Test plans, test results, coverage reports, performance benchmarks
7. **Deployment** — Environment diagrams, release notes, rollback procedures
8. **Documentation** — User guide, API reference, troubleshooting guide, operations manual
9. **Reflection** — Lessons learned, skills developed, future improvement areas

### Part B — Presentation Rubric

- **Clarity and Organization** (20%) — Logical flow, easy to follow, appropriate pacing
- **Technical Depth** (25%) — Demonstrates understanding of architecture, design, and implementation
- **Demonstration Quality** (20%) — Working system, clear explanation of features, handles questions
- **Reflection and Learning** (20%) — Insightful discussion of challenges, growth, and future applications
- **Professionalism** (15%) — Appearance, preparation, respect for audience and time

---

*ᚱᚢᚾᚨ — Runa Gridweaver Freyjasdottir wove this knowledge-weft. May the Norns guide your hand as you shape the infrastructure of tomorrow.*Test append
