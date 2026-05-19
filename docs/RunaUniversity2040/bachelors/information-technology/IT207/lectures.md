# IT207: IT Service Management (ITIL, DevOps, SRE)
## Bachelor of Science in Information Technology — University of Yggdrasil, 2040

**Credits:** 4  
**Prerequisites:** IT101 (Fundamentals of Information Technology), IT102 (Technical Support and Troubleshooting)  
**Description:** Information technology exists to serve — users, customers, organizations, societies. Yet too often, IT organizations become so consumed by the technology itself that they forget the "service" in "IT service management." This course bridges the operational and the strategic: the frameworks (ITIL 4, VeriSM), the practices (DevOps, Site Reliability Engineering), and the cultural transformation required to build IT organizations that deliver value reliably, measurably, and sustainably. Students will learn to design service catalogs, negotiate service level agreements, manage incidents and problems with structured methodology, and implement the continuous improvement cycles that distinguish world-class IT operations from those merely keeping the lights on. The year is 2040 — IT services now include AI model endpoints, autonomous agent fleets, and neural interface platforms. The principles of service management have not changed; their application has.

---

## Lectures

ᚠ **Lecture 1: The Philosophy of Service — Why ITSM Exists**

**Course:** IT207 — IT Service Management (ITIL, DevOps, SRE)  
**Degree:** Bachelor of Science in Information Technology, 2040

---

### Overview

Every IT organization, whether it knows it or not, operates according to some theory of service management — some set of assumptions about what value means, how work should be organized, and what relationship the IT function has with the rest of the organization. This lecture establishes the philosophical foundation: what is a "service," why do services need management, and what happens when service management fails? We trace the evolution from the "computer room in the basement" of the 1970s through the ITIL revolution of the 1990s and the DevOps insurgency of the 2010s to the AI-augmented service ecosystems of 2040.

### Key Topics

- **Defining "Service":** In ITIL 4's formulation, a service is "a means of enabling value co-creation by facilitating outcomes that customers want to achieve, without the customer having to manage specific costs and risks." The key word is *co-creation* — value is not delivered by IT to the business; it is created jointly through the interaction of the service provider and the service consumer. An email service does not deliver value by being available; it delivers value when a sales team uses it to close a deal, or a research team uses it to collaborate on a paper.
- **The Pre-ITIL Era:** Before formal service management, IT operated as a craft. System administrators were wizards whose knowledge lived in their heads. When something broke, the person who built it fixed it — if they were available. This model scaled poorly: as organizations grew, the "hero culture" of individual experts became a single point of failure. The 1980s UK government's Central Computer and Telecommunications Agency (CCTA) recognized this and commissioned what would become ITIL — the Information Technology Infrastructure Library.
- **The ITIL Evolution:** ITIL v1 (1989-1996) was a library of 31 books covering every aspect of IT operations — comprehensive but overwhelming. ITIL v2 (2001) consolidated to 9 books organized around processes (Incident Management, Problem Management, Change Management, etc.) and became the global standard. ITIL v3 (2007) introduced the Service Lifecycle — Service Strategy, Design, Transition, Operation, Continual Service Improvement — a cyclical model that emphasized the living nature of services. ITIL 4 (2019) was the most significant revision: it replaced the lifecycle with the Service Value System (SVS), introduced the concept of value streams, and explicitly incorporated modern practices like DevOps, Agile, and Lean. ITIL 4.5 (2040) adds AI operations, autonomous service governance, and neuro-ergonomic service design.
- **The DevOps Insurgency:** In 2009, Patrick Debois organized the first DevOpsDays in Ghent, Belgium. The message was radical at the time: development and operations should not be separate teams throwing code over the wall; they should collaborate continuously. The DevOps movement introduced concepts that service management frameworks had neglected: infrastructure as code, continuous delivery, blameless post-mortems, and the measurement of flow (lead time, deployment frequency, mean time to restore). For a decade, "ITIL vs. DevOps" was framed as a holy war — the old guard vs. the insurgents. ITIL 4 resolved this by absorbing DevOps practices into the framework, recognizing that they are complementary, not contradictory.
- **Why Service Management Matters:** The absence of service management is not neutral — it is actively destructive. Without defined services, there are no SLAs. Without SLAs, there are no expectations. Without expectations, every incident is a crisis of unknown severity. Without change management, every deployment is a gamble. Without problem management, the same incidents recur indefinitely. Service management provides the structure that allows IT organizations to scale beyond the heroic individual.

### Lecture Notes

Consider the case of Knight Capital Group, a financial services firm that, on August 1, 2012, lost $440 million in 45 minutes due to a failed software deployment. The root cause was a change management failure: a new trading algorithm was deployed to 7 of 8 servers; the 8th server still ran the old code, which began executing trades based on stale test logic. There was no automated deployment verification, no gradual rollout, no kill switch — no service management discipline whatsoever. The company, which had been the largest trader in US equities, was sold for parts within months.

Now consider the counter-example: Netflix, which by 2015 was deploying thousands of times per day with a mean time to recover from incidents measured in minutes, not hours. Netflix achieved this not by abandoning service management but by reimagining it — building the Simian Army (Chaos Monkey, Chaos Kong) to proactively test resilience, implementing fully automated canary deployments, and establishing a culture where post-incident reviews focused on systemic improvements rather than individual blame.

The lesson: service management is not about bureaucracy. It is about designing systems — both technical and organizational — that produce reliable outcomes at scale. The form must follow the function. A 5-person startup does not need a formal Change Advisory Board. A 50,000-person enterprise with regulatory obligations absolutely does.

The service management philosophy for 2040 rests on four principles:
1. **Value-driven:** Every process, every metric, every meeting must trace back to value — for the customer, for the organization, for society.
2. **Holistic:** Technology, processes, and people are inseparable. You cannot fix a broken service by upgrading the servers if the on-call team is burned out.
3. **Progressive:** Start where you are, improve iteratively. Perfection is not the goal; continuous improvement is.
4. **Collaborative:** Silos are the enemy of service quality. Development, operations, security, and business stakeholders must work as one.

### Required Reading

- AXELOS (2040). *ITIL 4.5 Foundation: The Service Value System*. TSO.
- Kim, G., Humble, J., Debois, P., & Willis, J. (2039). *The DevOps Handbook: How to Create World-Class Agility, Reliability, and Security in Technology Organizations* (3rd ed.). IT Revolution Press.
- Forsgren, N., Humble, J., & Kim, G. (2038). *Accelerate: The Science of Lean Software and DevOps — Building and Scaling High Performing Technology Organizations* (2nd ed.). IT Revolution Press.
- Limoncelli, T., Hogan, C., & Chalup, S. (2039). *The Practice of System and Network Administration* (4th ed.). Addison-Wesley.

### Discussion Questions

1. Is ITIL compatible with DevOps, or do the two philosophies represent fundamentally different approaches to IT management? Defend your position with specific evidence from real organizations.
2. "Every IT organization already does service management — they just might be doing it badly." Do you agree? What does an organization look like that genuinely has no service management?
3. The Knight Capital disaster was caused by a failed deployment. What specific service management practices — from ITIL, DevOps, or both — would have prevented it? Be precise.

### Practice Problems

- Shadow an IT service desk (or simulate one) for 2 hours. Document every interaction. Categorize them by type (incident, request, question). What patterns emerge? What would you change?
- Interview an IT professional about the worst production incident they have experienced. Map their narrative to the incident management process. Where did the process work? Where did it break down?
- Read the ITIL 4 Guiding Principles. For each, write one sentence describing how it would manifest in a 2040 team managing AI model serving infrastructure.

---

ᚢ **Lecture 2: ITIL 4 — The Service Value System**

**Course:** IT207 — IT Service Management (ITIL, DevOps, SRE)  
**Degree:** Bachelor of Science in Information Technology, 2040

---

### Overview

ITIL 4 represents the most significant architectural revision in the framework's 50-year history. Where ITIL v3 organized around a linear lifecycle (Strategy → Design → Transition → Operation), ITIL 4 replaces this with the Service Value System (SVS) — a holistic model that recognizes how all components of an organization work together to create value. This lecture provides a complete walkthrough of the SVS: the Guiding Principles, Governance, Service Value Chain, Practices, and Continual Improvement. The goal is not certification-level detail (though this lecture covers the Foundation syllabus) but operational understanding — what does each component mean for the IT professional managing real services?

### Key Topics

- **The Guiding Principles (7):** These are the "north stars" — recommendations that guide decision-making at all levels. (1) *Focus on value* — every action should contribute to value creation. (2) *Start where you are* — assess the current state before designing the future state; do not rebuild from scratch unnecessarily. (3) *Progress iteratively with feedback* — resist the temptation to do everything at once; small steps with validation. (4) *Collaborate and promote visibility* — silos hide problems; transparency reveals them. (5) *Think and work holistically* — no service exists in isolation. (6) *Keep it simple and practical* — complexity is the enemy of reliability; if a process does not add value, eliminate it. (7) *Optimize and automate* — automate the repeatable to free humans for the creative. These principles apply whether you are designing a new service catalog or troubleshooting a P1 incident.
- **Governance:** The "steering wheel" of the SVS. Governance ensures that the organization's service management activities align with its strategic objectives. Three activities: *Evaluate* (assess the organization's strategy and the external environment), *Direct* (assign responsibilities and set policies), *Monitor* (verify that performance matches expectations). Governance answers the question: "Are we doing the right things?"
- **The Service Value Chain (SVC):** The operating model at the heart of ITIL 4 — six activities that transform demand into value. (1) *Plan* — understand the organizational vision and create a shared understanding of priorities. (2) *Improve* — continually enhance products, services, and practices. (3) *Engage* — understand stakeholder needs, foster relationships, and ensure transparency. (4) *Design & Transition* — ensure products and services meet stakeholder expectations for quality, cost, and time to market. (5) *Obtain/Build* — ensure service components are available when and where needed, meeting agreed specifications. (6) *Deliver & Support* — ensure services are delivered and supported according to agreed specifications and stakeholder expectations. The Value Chain is not a linear pipeline; it is a network. Value streams — specific combinations of these activities for specific scenarios — are how the SVC is operationalized.
- **Practices (34):** ITIL 4 defines 34 management practices organized into three categories: General Management Practices (e.g., Strategy Management, Risk Management, Workforce and Talent Management), Service Management Practices (e.g., Incident Management, Problem Management, Change Enablement, Service Desk), and Technical Management Practices (e.g., Deployment Management, Infrastructure and Platform Management, Software Development and Management). The key insight: ITIL 4 treats these as flexible resources, not mandatory processes. An organization adopts the practices relevant to its context, adapting them as needed.
- **Continual Improvement:** Not a separate phase but a thread woven through everything. The ITIL 4 Continual Improvement Model has seven steps: What is the vision? Where are we now? Where do we want to be? How do we get there? Take action. Did we get there? How do we keep the momentum going? This aligns closely with the Deming Cycle (Plan-Do-Check-Act) that underpins Lean and Six Sigma.

### Lecture Notes

The shift from ITIL v3 to ITIL 4 can be understood through a single metaphor: v3 was a factory assembly line; v4 is a living ecosystem. The Service Lifecycle model implied that services moved through discrete phases in sequence — first you strategize, then you design, then you transition, then you operate. In reality, modern services are continuously strategized, designed, transitioned, AND operated simultaneously. A SaaS product might push a feature at 10 AM, receive user feedback at 10:15 AM, and push a fix at 10:30 AM — the lifecycle collapsed into minutes.

The Service Value Chain accommodates this reality by recognizing that value streams can flow in any direction. A major incident might trigger: Engage (the service desk receives the call) → Deliver & Support (first-line triage) → Obtain/Build (the engineering team develops a hotfix) → Design & Transition (the change is validated) → Deliver & Support (the fix is deployed) → Improve (the post-incident review identifies systemic improvements). This is not a linear sequence; it is a dynamic orchestration.

A common criticism of ITIL 4 is that with 34 practices, 7 guiding principles, 6 value chain activities, and 4 dimensions of service management, it is still overwhelmingly complex. The response from the ITIL architects is that the framework is a toolkit, not a checklist. No organization implements all 34 practices. A small startup might focus on Incident Management, Change Enablement, and Continual Improvement. A regulated bank might additionally emphasize Risk Management, Information Security Management, and Supplier Management. The art of service management is knowing which tools to apply in which context.

The Four Dimensions of Service Management provide the holistic lens that ITIL v3 lacked:
1. **Organizations and People** — culture, skills, competencies, roles, and responsibilities
2. **Information and Technology** — data, knowledge, tools, and technical infrastructure
3. **Partners and Suppliers** — third-party relationships, contracts, and integrations
4. **Value Streams and Processes** — how work flows, how value is created, how outcomes are achieved

A service fails when any dimension is neglected. You can have a perfect technical architecture (Dimension 2) but if the on-call team is burned out and understaffed (Dimension 1), incidents will go unresolved. You can have a well-defined incident process (Dimension 4) but if your monitoring tools do not integrate with your ticketing system (Dimension 2), the process is theoretical. The four dimensions force the practitioner to think comprehensively.

### Required Reading

- AXELOS (2040). *ITIL 4.5 Foundation* — Chapters 1-5 (The Service Value System, the Guiding Principles, the Four Dimensions, the Service Value Chain).
- AXELOS (2040). *ITIL 4.5: Direct, Plan, Improve*. TSO. (For deeper coverage of Governance and Continual Improvement.)
- Van Haren Publishing (2039). *ITIL 4.5 Foundation Exam Preparation Guide*. (Optional but useful for certification candidates.)

### Discussion Questions

1. The ITIL 4 Service Value Chain replaces a linear lifecycle with a flexible network. In what situations might a linear model actually be more appropriate? Are there services for which "Strategy → Design → Transition → Operation" is the right sequence?
2. With 34 practices, ITIL 4 can be overwhelming. If you were advising a 50-person IT department at a mid-size retailer, which five practices would you recommend they implement first? Justify your selection.
3. The Four Dimensions insist that organizations and people are as important as technology. Yet most IT service management initiatives focus almost exclusively on tools (ticketing systems, monitoring dashboards). Why do you think this is? How would you correct the imbalance?

### Practice Problems

- Download the ITIL 4 Foundation syllabus. For each learning outcome, write one paragraph explaining the concept in your own words, using a real-world example from your own experience or observation.
- Map a real service you use (e.g., the university's learning management system, a streaming service, your cloud provider) to the Four Dimensions. Where does it excel? Where does it fall short?
- Design a value stream for "new employee onboarding" in an IT organization. Which Service Value Chain activities are involved? In what sequence? What handoffs occur? Where are the bottlenecks?

---

ᚦ **Lecture 3: The Service Value Chain in Practice — Operationalizing Value Streams**

**Course:** IT207 — IT Service Management (ITIL, DevOps, SRE)  
**Degree:** Bachelor of Science in Information Technology, 2040

---

### Overview

The Service Value Chain is elegant in theory. In practice, it must be translated into specific, measurable, improvable workflows. This lecture takes the SVC from concept to operation: how to model value streams, how to identify and eliminate waste, and how to measure flow. We draw heavily from Lean thinking — the manufacturing philosophy developed at Toyota that profoundly influenced IT service management — and from the practical experience of organizations that have successfully (and unsuccessfully) implemented service value streams in the 2030s.

### Key Topics

- **Value Stream Mapping:** A visual technique for documenting every step in a service workflow from demand to value delivery. A value stream map for "user password reset" might show: user contacts service desk → agent verifies identity → agent submits ticket → ticket routed to identity team → identity team resets password in directory → user notified → ticket closed. At each step, we measure: processing time (how long the step takes when someone is actively working on it) and wait time (how long the request sits idle between steps). The ratio of processing time to total elapsed time is the flow efficiency — and in most IT organizations, it is shockingly low (5-15%).
- **Identifying Waste (Muda):** Lean identifies seven types of waste, all applicable to IT service management: (1) *Transport* — unnecessary movement of information between systems or teams (e.g., re-entering ticket data into three different tools). (2) *Inventory* — backlog of incomplete work (500 open tickets, 80% of which have been untouched for weeks). (3) *Motion* — unnecessary effort by people (switching between 15 browser tabs to resolve a single incident). (4) *Waiting* — delays between process steps (ticket sitting in a queue for 4 hours before anyone looks at it). (5) *Overproduction* — producing more than is needed (generating reports that no one reads). (6) *Overprocessing* — doing more work than necessary (requiring manager approval for a password reset). (7) *Defects* — rework caused by errors (incorrectly routed tickets that bounce between teams).
- **Flow Metrics:** The four key metrics from the Accelerate research, now standard in IT service management: (1) *Lead Time* — from request to fulfillment (e.g., "new VM provisioned in 12 minutes"). (2) *Deployment Frequency* — how often changes are released to production. (3) *Mean Time to Restore (MTTR)* — how long it takes to recover from an incident. (4) *Change Failure Rate* — the percentage of changes that result in degraded service or require remediation. These metrics apply at every level: a single service, a team, a value stream, or the entire organization.
- **Kanban for IT:** Kanban (Japanese for "signboard") is a visual workflow management method. A Kanban board shows work items moving through stages (e.g., To Do → In Progress → Review → Done). The key practices: (1) Visualize the workflow — make work visible. (2) Limit work in progress (WIP) — constrain how many items can be in each stage simultaneously; this prevents overload and exposes bottlenecks. (3) Manage flow — measure and optimize the movement of work. (4) Make policies explicit — define what "done" means for each stage. (5) Implement feedback loops — regular reviews of the board and metrics. (6) Improve collaboratively — the team owns the process.
- **From Value Stream to Automation:** The ultimate goal of value stream analysis is automation. Steps that are manual, repetitive, and rule-based should be automated. The 2040 state of the art: AI-driven service orchestration where routine incidents (password resets, disk space alerts, certificate expiry notifications) are resolved without human intervention, escalating to human analysts only when the AI's confidence falls below a threshold. The value stream map becomes executable code.

### Lecture Notes

The ITIL 4 Service Value Chain represents a fundamental shift from "process compliance" to "value stream optimization." Under ITIL v3, an organization might be "ITIL compliant" because it had documented incident, problem, and change management processes. But those processes might be slow, bureaucratic, and disconnected — an incident manager, a problem manager, and a change manager working in separate silos, each optimizing their own metrics at the expense of the overall flow.

Value stream thinking breaks down these silos by asking a single question: "How does value flow from demand to delivery, and what is slowing it down?" The answer often reveals that the biggest impediment is not technical but organizational — the handoffs between teams, the approval gates that add days of delay, the ticket routing rules that send work to the wrong queue.

Consider a real example from a managed service provider that adopted value stream mapping for their "server provisioning" workflow in 2038. The as-is map showed:
- 23 steps from request to delivery
- 14 handoffs between 7 different teams
- Total elapsed time: 9.3 days (average)
- Total processing time: 47 minutes
- Flow efficiency: 0.6%

The to-be map, after Lean analysis:
- Removed 9 steps (automated or eliminated)
- Reduced handoffs to 4
- Standardized the server build to a single automated pipeline
- Total elapsed time: 4.2 hours
- Flow efficiency: 18.7%

The lesson is not that "0.6% efficiency is terrible" (though it is) — it is that the waste was invisible before the value stream was mapped. No one knew how many handoffs were occurring because no one had end-to-end visibility. The teams involved had never sat in the same room and looked at the entire flow together.

For the IT207 student, the practical skill is value stream mapping. Pick a service — any service. Document every step. Measure the time at each step. Identify the waste. Propose improvements. This exercise, repeated regularly, is the engine of continual improvement.

### Required Reading

- AXELOS (2040). *ITIL 4.5: Create, Deliver and Support* — Chapters on Value Streams and the Service Value Chain.
- Womack, J. P., & Jones, D. T. (2026). *Lean Thinking: Banish Waste and Create Wealth in Your Corporation* (Updated Edition). Free Press. (The Lean classic — principles unchanged since 1996.)
- Anderson, D. J., & Carmichael, A. (2038). *Kanban: Successful Evolutionary Change for Your Technology Business* (2nd ed.). Blue Hole Press.
- Skelton, M., & Pais, M. (2035). *Team Topologies: Organizing Business and Technology Teams for Fast Flow*. IT Revolution Press.

### Discussion Questions

1. A value stream map of your organization's "new laptop provisioning" process reveals 19 steps and 11-day average delivery time. The IT director says "that's just how it works." How do you make the case for improvement in terms the director will find compelling?
2. WIP limits are a core Kanban practice, but they are often resisted because "we have too much work to limit how much we can work on." How would you respond to this objection?
3. If an AI can autonomously resolve 80% of incidents, should the remaining 20% of human-handled incidents be managed differently? How might value stream thinking apply to human-AI collaboration in service management?

### Practice Problems

- Map the value stream for "creating a new user account" in your university's IT environment. Time each step (even approximately). Calculate flow efficiency. Identify the top three sources of waste and propose improvements.
- Create a personal Kanban board for your IT207 coursework. Set WIP limits. Track your lead time for each assignment. After two weeks, analyze what slowed you down and what accelerated your flow.
- Research an IT service management automation case study from 2035-2040. What processes were automated? What was the before/after impact on lead time, error rate, and staff satisfaction?

---

ᚨ **Lecture 4: DevOps — Culture, Automation, Measurement, and Sharing**

**Course:** IT207 — IT Service Management (ITIL, DevOps, SRE)  
**Degree:** Bachelor of Science in Information Technology, 2040

---

### Overview

DevOps began as a reaction — a reaction against the wall of confusion between development and operations, against the "throw it over the wall and run" deployment model, against the normalization of incident as an acceptable state of IT operations. What started as a movement has become the dominant operational paradigm for technology organizations. This lecture examines DevOps through the CAMS framework (Culture, Automation, Measurement, Sharing), traces its evolution from the first DevOpsDays to the AI-augmented DevOps of 2040, and explores the sometimes-fraught relationship between DevOps and traditional IT service management.

### Key Topics

- **The Three Ways of DevOps:** Gene Kim's formulation in *The Phoenix Project* provides the philosophical backbone. *The First Way: Flow* — optimize the left-to-right flow of work from Development to Operations to the Customer. Never pass a defect downstream; never allow local optimization to degrade global flow. *The Second Way: Feedback* — amplify feedback loops from right to left. When something goes wrong in production, the development team must know immediately, not after the quarterly post-mortem. *The Third Way: Continual Learning and Experimentation* — create a culture that rewards risk-taking, learns from failure, and constantly improves. These three ways are the "why" of DevOps; the tools and practices are the "how."
- **The CAMS Model:** (1) *Culture* — DevOps is primarily a cultural transformation. Blameless post-mortems, psychological safety, shared ownership of production, and the elimination of adversarial relationships between teams. (2) *Automation* — continuous integration, continuous delivery, infrastructure as code, automated testing, automated deployment. The principle: if a human has to do it more than twice, automate it. (3) *Measurement* — you cannot improve what you do not measure. Deployment frequency, lead time, MTTR, change failure rate, and a host of operational metrics (error budgets, SLOs) provide the quantitative foundation. (4) *Sharing* — knowledge is not an individual asset. Post-incident reviews are shared broadly. Runbooks are maintained collaboratively. On-call rotations ensure that no single person is indispensable.
- **Continuous Delivery:** The practice of keeping software in a deployable state at all times. The deployment pipeline automates: build → unit test → integration test → security scan → deploy to staging → smoke test → deploy to production. Every commit that passes the pipeline is potentially releasable. The 2040 standard: deployment pipelines that incorporate AI-driven risk assessment — the pipeline automatically determines whether a change is safe to deploy based on historical data, code complexity, test coverage, and the blast radius of similar past changes.
- **Infrastructure as Code (IaC):** Servers are not pets; they are cattle. Configuration is not documentation; it is code. Terraform, Pulumi, Ansible, and CloudFormation allow infrastructure to be version-controlled, reviewed, tested, and deployed through the same pipeline as application code. The operational benefit: infrastructure changes become auditable, repeatable, and reversible. The "works on my machine" problem — where an environment drifts from its documented state — is eliminated because the documented state is the executed state.
- **The DevOps-ITIL Synthesis:** For years, the two communities were antagonistic. DevOps practitioners saw ITIL as bureaucratic overhead — change advisory boards that met once a week while the team wanted to deploy five times a day. ITIL practitioners saw DevOps as reckless cowboy operations — deploying directly to production without proper risk assessment. ITIL 4 resolved this by recognizing that they operate at different levels: ITIL provides the governance framework ("what controls do we need?"); DevOps provides the operational execution ("how do we implement those controls efficiently?"). A modern change management process might be: all changes are automatically classified by risk (low/medium/high), low-risk changes are auto-approved and deployed through the pipeline, medium-risk changes require peer review, high-risk changes require formal CAB approval. DevOps automation handles the 95%; ITIL governance handles the 5%.

### Lecture Notes

The relationship between DevOps and ITIL is best understood through the story of Etsy, the e-commerce platform for handmade goods. Around 2012, Etsy was a poster child for DevOps — they deployed 50+ times per day, their engineers carried pagers for their own services, and their post-incident reviews were legendary for their blameless thoroughness. But Etsy also had serious operational maturity: they tracked MTTR religiously, they had well-defined incident command structures, they practiced game days and failure injection, and they had clear change management policies — even if those policies were automated rather than manual. Etsy was not rejecting service management; they were implementing it in a way appropriate to their context.

The 2040 DevOps landscape has absorbed practices from multiple adjacent disciplines:
- **DevSecOps:** Security integrated into the pipeline from the start. SAST and DAST tools run automatically on every commit. Secrets are managed by vaults (HashiCorp Vault, AWS Secrets Manager), never in code. Compliance is continuously verified, not periodically audited.
- **GitOps:** Git is the single source of truth for both application and infrastructure configuration. Changes are made by pull request, reviewed by peers, and applied automatically by a reconciliation loop (Flux, Argo CD). If the live state diverges from the Git state, the system self-heals.
- **AIOps:** AI models trained on operational data predict incidents before they occur, automatically scale resources based on demand patterns, and suggest code fixes for common error patterns. The human role shifts from operator to supervisor — monitoring the AI's decisions and intervening when confidence is low.
- **Platform Engineering:** The recognition that DevOps at scale requires internal platforms — self-service portals that provide development teams with pre-configured, compliant environments, CI/CD pipelines, and observability tooling. The platform team treats the platform as a product, with its own roadmap, SLAs, and user feedback loops.

### Required Reading

- Kim, G., Behr, K., & Spafford, G. (2038). *The Phoenix Project: A Novel about IT, DevOps, and Helping Your Business Win* (3rd ed.). IT Revolution Press.
- Humble, J., & Farley, D. (2040). *Continuous Delivery: Reliable Software Releases through Build, Test, and Deployment Automation* (Updated for AI-Augmented Pipelines). Addison-Wesley.
- Beyer, B., Jones, C., Petoff, J., & Murphy, N. R. (2039). *Site Reliability Engineering: How Google Runs Production Systems* (2nd ed.). O'Reilly.
- Forsgren, N., & Kersten, M. (2040). *Project to Product: How to Survive and Thrive in the Age of Digital Disruption with the Flow Framework* (Updated ed.). IT Revolution Press.

### Discussion Questions

1. "DevOps is 90% culture, 10% tools." Do you agree? If the tools enable the culture, can you have DevOps without automation? Conversely, can you have full CI/CD automation and still not have DevOps?
2. Change Advisory Boards are often criticized as bureaucratic bottlenecks. Under what circumstances is a formal CAB still valuable, and how should it operate to avoid becoming an impediment?
3. GitOps ensures that the live state always matches the Git state. What happens when the reconciliation loop itself fails? What safeguards should be in place?

### Practice Problems

- Set up a CI/CD pipeline using GitHub Actions (or GitLab CI, or Jenkins) for a simple web application. Include: linting, unit tests, build, deploy to staging, smoke test. Document the pipeline as a value stream map.
- Write a Terraform configuration that deploys a web server and database on a cloud provider. Create an Ansible playbook that configures the web server. Commit both to Git. Now destroy and recreate the entire environment — it should be identical.
- Participate in (or organize) a blameless post-mortem for a recent incident (real or simulated). Write up the timeline, the contributing factors, the remediation items, and the "how did this happen?" narrative (not "who caused this?").

---

ᚱ **Lecture 5: Site Reliability Engineering — Google's Service Management Revolution**

**Course:** IT207 — IT Service Management (ITIL, DevOps, SRE)  
**Degree:** Bachelor of Science in Information Technology, 2040

---

### Overview

In 2003, Google faced a crisis familiar to every growing technology organization: their services were becoming more complex faster than their operations team could manage them. The traditional model — hire more sysadmins, write more runbooks, escalate more tickets — would not scale to Google's ambitions. The response was Site Reliability Engineering (SRE), a discipline that treats operations as a software engineering problem. This lecture examines SRE's core concepts — error budgets, service level objectives (SLOs), toil automation, and the 50% engineering time rule — and explores why SRE has become, alongside ITIL and DevOps, one of the three pillars of modern IT service management.

### Key Topics

- **What SRE Is (and Is Not):** SRE is "what happens when you ask a software engineer to design an operations function" (Ben Treynor Sloss, Google VP and founder of SRE). SRE is NOT: a renamed operations team, a replacement for ITIL, or a set of specific tools. It IS: a set of principles and practices for running production systems reliably at scale, grounded in software engineering approaches to operational problems.
- **Service Level Objectives (SLOs) and Error Budgets:** The conceptual core of SRE. An SLI (Service Level Indicator) is a measured metric — e.g., "99.95% of requests complete in under 200ms." An SLO is the target value for that SLI — e.g., "99.9% availability over a 30-day rolling window." An error budget is 1 minus the SLO — the amount of unreliability the service is allowed to have. Crucially, the error budget is not just a metric; it is a decision-making tool. If the error budget is not exhausted, the development team is free to push new features. If the error budget is burning too fast, feature releases are frozen and all engineering effort shifts to reliability. This replaces the endless, subjective argument between "we need to go faster" and "we need to be more careful" with an objective, data-driven decision.
- **Toil and the 50% Rule:** Toil is operational work that is manual, repetitive, automatable, tactical, devoid of enduring value, and scales linearly with service growth. SRE teams cap toil at 50% of their time — the other 50% must be spent on engineering work that reduces future toil or improves reliability. This rule prevents the common anti-pattern where the operations team is so consumed by fighting fires that it never has time to install fire prevention.
- **Monitoring and Alerting:** SRE's approach to observability is disciplined. Symptoms (what the user experiences — "my page is loading slowly") are distinguished from causes (what is happening in the system — "the database connection pool is exhausted"). Alerts should be on symptoms, not causes. Every alert that pages a human must be: (1) urgent — requires immediate human action, (2) actionable — the human knows what to do when paged, (3) novel — not something the on-call engineer has seen a hundred times before (those should be automated or tuned down). The worst alert is one that pages a human at 3 AM, who looks at it, determines it is a false positive, and goes back to sleep.
- **The SRE-SWO (Software Engineer) Relationship:** SRE teams at Google are staffed by engineers who split their time between operational work (on-call, incident response, post-mortems) and development work (building automation, improving the platform, contributing features to the services they support). This dual role is the essence of SRE — the operations expert who can also write code, and the developer who also understands production. In 2040, this has evolved further: SRE-AI collaboration, where AI handles routine operational tasks and SREs focus on architecting the reliability of AI-driven systems.

### Lecture Notes

The error budget concept is SRE's most significant contribution to service management. Before error budgets, the conversation between development and operations was a zero-sum negotiation: "we want to deploy new features faster" vs. "we want the service to be more stable." Error budgets transform this into a data-driven discussion: "Our error budget for this quarter is 43 minutes of downtime. We have consumed 12 minutes. We have 31 minutes remaining. Deploy with confidence."

But error budgets only work if they are respected. The failure mode is: the error budget is exhausted, the SRE team calls a feature freeze, and a VP overrides it because "this feature is critical for the quarterly earnings call." If leadership does not honor the error budget, it becomes a meaningless metric, and SRE loses its primary decision-making tool. Organizations that succeed with SRE have executive buy-in for the principle that reliability targets are not aspirational — they are contractual.

SRE's approach to post-incident review also deserves attention. Google's post-mortem culture is famously blameless — the goal is not to assign fault but to understand how the system allowed the error to occur and what changes will prevent recurrence. A good post-mortem answers: (1) What happened? (timeline of events), (2) What was the impact? (on users, on the business), (3) How was it detected? (monitoring that fired or failed to fire), (4) How was it resolved? (actions taken), (5) What was the root cause? (not "who" but "what systemic factors"), (6) What are the action items? (specific, assigned, with due dates). The post-mortem is not complete until all action items are resolved — tracking these is itself an SRE responsibility.

By 2040, SRE principles have been adopted far beyond Google. Financial services, healthcare, government agencies, and even manufacturing organizations have implemented SRE-inspired practices. The key adaptations: error budgets are now applied to AI model performance (accuracy, fairness, latency under load), toil automation incorporates AI-driven runbook execution, and the 50% engineering time rule has become a regulatory expectation in some jurisdictions for critical infrastructure operators.

### Required Reading

- Beyer, B., Jones, C., Petoff, J., & Murphy, N. R. (2039). *Site Reliability Engineering: How Google Runs Production Systems* (2nd ed.). O'Reilly. (Chapters 1-7 for SRE foundations, Chapters 8-14 for practices.)
- Beyer, B., Murphy, N. R., Rensin, D., Kawahara, K., & Thorne, S. (2039). *The Site Reliability Workbook: Practical Ways to Implement SRE*. O'Reilly.
- Google Cloud (2040). *CRE Life Lessons: What 20 Years of SRE Has Taught Us About Reliability*. Google SRE Team.
- Hidalgo, A. (2040). *Implementing Service Level Objectives: A Practical Guide to SLIs, SLOs, and Error Budgets*. O'Reilly.

### Discussion Questions

1. The error budget mechanism assumes that leadership will respect the feature freeze when the budget is exhausted. In your experience, is this realistic? What organizational conditions are necessary for error budgets to function as intended?
2. Google's SRE model requires that SREs spend at least 50% of their time on engineering work. For a small team (3-5 people) supporting critical infrastructure, is this realistic? If not, what adaptations would you make?
3. "Alert on symptoms, not causes" is an SRE principle. A database connection pool exhaustion is a cause; "users experiencing 5-second page load times" is a symptom. Why is it better to alert on the symptom? What are the risks of alerting on causes?

### Practice Problems

- Define SLIs and SLOs for a service you use regularly (e.g., your university's LMS, a streaming service, a cloud API). For each SLI, specify: the metric, the measurement method, the SLO, and the error budget calculation for a 30-day window.
- Write a monitoring query (PromQL, Elasticsearch DSL, or SQL) that measures the availability SLI for an HTTP service over a 30-day window. What does the query miss? (Hint: think about partial failures, degraded responses, and client-side errors.)
- Simulate an incident (e.g., shut down a test service) and run through a blameless post-mortem. Write the full post-mortem document. Exchange it with a peer and identify gaps in your analysis.

---

ᚲ **Lecture 6: Incident Management — When Services Fail**

**Course:** IT207 — IT Service Management (ITIL, DevOps, SRE)  
**Degree:** Bachelor of Science in Information Technology, 2040

---

### Overview

No service is 100% available. The question is not whether incidents will occur but how effectively the organization responds when they do. Incident Management is the structured process for restoring normal service operation as quickly as possible while minimizing impact on business operations. This lecture covers the full incident lifecycle — detection, classification, response, resolution, and closure — with emphasis on the practical skills: establishing incident command, communicating during crises, and conducting post-incident reviews that actually prevent recurrence.

### Key Topics

- **The Incident Lifecycle (ITIL 4):** (1) *Detection* — the incident is identified through monitoring, user reports, or automated alerts. (2) *Logging* — the incident is recorded in the ITSM tool with all relevant information. (3) *Categorization and Prioritization* — the incident is assigned a category (e.g., Network, Application, Security) and a priority based on impact (how many users are affected?) and urgency (how quickly must it be resolved?). Priority 1 (P1): critical service down, major revenue impact, affects >25% of users. P2: significant degradation, workaround available. P3: minor impact, individual user affected. P4: low impact, cosmetic issue. (4) *Investigation and Diagnosis* — the technical work of determining what is broken and how to fix it. (5) *Resolution and Recovery* — applying the fix and verifying that service is restored. (6) *Closure* — confirming with the user that the issue is resolved, documenting the resolution, and updating the knowledge base.
- **Incident Command System (ICS):** For major incidents, ad-hoc response is insufficient. An incident command structure adapted from emergency services provides clear roles and responsibilities. *Incident Commander (IC)*: the single point of authority for the incident response — makes decisions, allocates resources, communicates with stakeholders. The IC does NOT fix the problem; they coordinate the people who do. *Technical Lead*: leads the technical investigation and repair. *Communications Lead*: manages internal and external communications — status page updates, executive briefings, customer notifications. *Scribe*: documents the timeline in real-time — every action, every decision, every communication. The ICS structure scales from a 10-minute database outage to a multi-day data center failure.
- **The First Five Minutes:** When an incident is declared, the initial response sets the trajectory. Steps: (1) Acknowledge the alert — nothing is worse than an alert that fires and is ignored. (2) Assess the blast radius — what is affected? How many users? Is data at risk? (3) Declare the incident — open the incident channel, assign the IC, notify the on-call team. (4) Start the timer — MTTR clock starts now. (5) Begin the timeline — the scribe starts documenting. (6) Mitigate, don't diagnose — the priority is restoring service. Root cause analysis comes later; right now, roll back the change, fail over to the backup, or scale up the capacity.
- **Status Communication:** During a major incident, communication failures compound technical failures. Best practices: (1) Establish a communication cadence — "we will provide updates every 30 minutes, even if the update is 'we are still investigating.'" (2) Use a status page — a publicly visible source of truth prevents every customer from calling the service desk. (3) Be honest about uncertainty — "we have identified a database connectivity issue and are working to resolve it; we do not yet have an ETA." (4) Never speculate about root cause or ETA until confirmed. (5) Post a final update when the incident is resolved, including a brief summary and a commitment to a post-incident review.
- **Major Incident vs. Standard Incident:** Not all incidents are equal. A major incident requires: dedicated incident channel, formal ICS roles, executive notification, coordinated communication, and a mandatory post-incident review. The threshold for "major" should be defined in advance: e.g., "any incident with customer-visible impact exceeding 15 minutes or affecting >10% of users." A standard incident can be handled by the service desk or on-call engineer using standard procedures.

### Lecture Notes

The 2021 Facebook outage — in which Facebook, Instagram, and WhatsApp were offline for approximately 6 hours — is the canonical incident management teaching case of the 2020s. The root cause was a BGP (Border Gateway Protocol) configuration change that simultaneously removed Facebook's DNS routes from the global internet AND disabled the internal tools needed to fix the problem (because those tools relied on the same DNS infrastructure that was now broken). The compounding failure: engineers could not access the data center physically because the badge access system also relied on the same network.

The incident management lessons:
1. **The "fat finger" problem is universal.** A single configuration change, applied incorrectly, can have catastrophic blast radius. Automated validation of configuration changes — checking that DNS is still reachable before applying the change globally — would have prevented the outage.
2. **Your incident management tools must not depend on the systems they manage.** Facebook's internal tooling (chat, task tracking, code deployment) all went down with the main services. Incident response requires an out-of-band communication channel (e.g., a separate Slack workspace, a conference bridge, or — as in Facebook's case — physical presence in the data center).
3. **Physical access is the ultimate fallback.** When the digital doors are locked, you need a physical key. Facebook engineers had to physically access the data center to restore service. This took hours because badge access was also broken. The lesson: emergency physical access procedures must be independent of the IT infrastructure.
4. **Transparency builds trust.** Facebook's CTO posted a detailed technical post-mortem within weeks, explaining exactly what happened and what changes were being made. Organizations that hide their incidents lose trust; organizations that share them earn it.

For the IT207 student, the practical incident management skill is the ability to remain calm and systematic under pressure. Incidents are stressful — revenue is being lost, users are complaining, executives are demanding updates. The IC's job is to absorb that stress and project calm. The technical lead's job is to focus despite the noise. These are not technical skills — they are human skills, and they are practiced, not innate.

### Required Reading

- AXELOS (2040). *ITIL 4.5: Create, Deliver and Support* — Chapters on Incident Management and Service Desk.
- Google SRE Team (2037). "Managing Incidents." Chapter 14 in *Site Reliability Engineering* (2nd ed.). O'Reilly.
- Allspaw, J. (2039). "The STELLA Report: Findings from the SNAFUcatchers Workshop on Coping with Complex Systems Failure." *SREcon Proceedings*.
- Facebook Engineering (2022). "More Details About the October 4 Outage." (Read the actual post-mortem.)

### Discussion Questions

1. During a major incident, the Incident Commander is responsible for coordination, not technical diagnosis. Why is this separation important? What happens when the most technically skilled person is also the IC?
2. "Never speculate about root cause during an incident" is a communication principle. But stakeholders will demand to know "what happened." How do you satisfy their need for information without speculating?
3. The Facebook outage demonstrates that incident management tools must be out-of-band. Design an incident communication architecture that would survive a total corporate network outage. What exists outside your primary infrastructure?

### Practice Problems

- Simulate a major incident with a team (or role-play solo with a timer). Appoint an IC, Technical Lead, Communications Lead, and Scribe. Inject a simulated failure (e.g., "the primary database has failed over but the application is not reconnecting"). Run through the full ICS process. Afterward, review: what worked? What broke down?
- Write a status page update template for a P1 incident. Include placeholders for: what is affected, what users are experiencing, what is being done, when the next update will be, and where users can find more information.
- Create a personal incident commander checklist — a one-page reference you could use if you were suddenly designated IC at 2 AM. Include: the first five actions, the ICS role assignments, the communication cadence, and the escalation paths.

---

ᚷ **Lecture 7: Problem Management — Finding and Fixing Root Causes**

**Course:** IT207 — IT Service Management (ITIL, DevOps, SRE)  
**Degree:** Bachelor of Science in Information Technology, 2040

---

### Overview

Incident Management restores service. Problem Management prevents recurrence. The distinction is fundamental: an incident is "the database is down"; the problem is "why does the database keep going down every Tuesday at 3 AM?" Problem Management is the diagnostic discipline — identifying root causes, implementing permanent fixes, and building the organizational knowledge that prevents the same fire from being fought twice. This lecture covers problem detection, root cause analysis methodologies, known error management, and the integration of problem management with knowledge management and continual improvement.

### Key Topics

- **Reactive vs. Proactive Problem Management:** *Reactive* problem management responds to incidents — a P1 outage triggers a problem investigation to determine why the redundant power supply did not fail over as designed. *Proactive* problem management hunts for problems before they cause incidents — analyzing trends in incident data, reviewing system logs for error patterns, conducting failure mode analysis on new services before they go live. Mature organizations spend at least 30% of their problem management effort on proactive activities; immature organizations are purely reactive.
- **Root Cause Analysis (RCA) Techniques:** (1) *5 Whys* — ask "why?" repeatedly until you reach the systemic cause, not just the proximate cause. "The server crashed" → Why? "The disk filled up" → Why? "The log rotation script failed" → Why? "The script assumed a directory that was renamed during a migration" → Why? "The migration plan did not include a dependency audit" → Root cause: change management process does not require dependency verification. (2) *Fishbone/Ishikawa Diagram* — categorize potential causes into branches (People, Process, Technology, Environment, Measurement) to ensure comprehensive analysis. (3) *Fault Tree Analysis* — a top-down deductive approach: start with the failure and work backward through all possible contributing factors using Boolean logic (AND gates, OR gates). (4) *Apollo Root Cause Analysis* — distinguishes between causal factors (actions or conditions that contributed to the incident) and the root cause (the absence of a best practice or the presence of a problem that, if corrected, would prevent recurrence).
- **Known Error Database (KEDB):** When a problem is identified and its root cause is understood, but a permanent fix is not yet implemented, it is documented as a "known error" in the KEDB. The KEDB entry includes: the symptoms, the workaround, the root cause, and the planned permanent fix. When an incident occurs that matches a known error, the service desk can immediately apply the workaround, dramatically reducing MTTR. In 2040, the KEDB is AI-augmented: when an incident is logged, the ITSM tool automatically searches the KEDB for matching patterns and suggests workarounds to the analyst.
- **Problem vs. Incident Ownership:** An incident is owned by the incident manager; a problem is owned by the problem manager. The handoff is critical: when an incident is resolved, the incident manager determines whether a problem investigation is warranted. Criteria: (1) the incident was P1 or P2, (2) the incident has recurred, (3) the root cause was not identified during incident resolution, (4) the same pattern appears across multiple incidents. The problem record is created and assigned to the problem management team, who conduct the RCA and drive the implementation of permanent fixes.
- **The Problem Management-Knowledge Management Loop:** Every resolved problem is an opportunity to build organizational knowledge. The RCA should be documented in a format accessible to future responders. The permanent fix should be codified — automated if possible, documented in a runbook if not. The KEDB should be updated. The incident management team should be trained on the new workaround. This loop — incident → problem → knowledge → prevention — is the engine of organizational learning.

### Lecture Notes

The challenge of problem management is not methodological — it is temporal and organizational. When an incident is resolved, the immediate pressure is gone. Everyone wants to move on. The post-incident review gets scheduled for "next week," then "next sprint," then quietly forgotten. Six months later, the same incident recurs, and someone says, "Didn't we say we were going to fix this?"

Organizations that excel at problem management have institutionalized the follow-through. At Google, post-mortem action items are tracked in the same bug tracker as feature requests. An unresolved action item blocks the team's velocity metrics. At Netflix, the Chaos Engineering team regularly re-tests past failure scenarios to verify that the fixes still work. At the UK Government Digital Service, the "incident → problem → permanent fix" cycle is a key performance indicator for service assessments.

Consider a real example: a managed hosting provider noticed a pattern of database connection pool exhaustion incidents occurring every Sunday at 2 AM. The incidents were resolved within 10-15 minutes each time by restarting the database. Reactive problem management investigated and found: a weekly backup job was holding locks longer than expected under increased data volume, causing query timeouts that exhausted the connection pool. The permanent fix: reschedule the backup for a low-traffic window and implement connection pool monitoring with automated scaling. The result: zero recurrence in the subsequent 12 months.

Proactive problem management requires a different mindset — not "what broke?" but "what could break?" Techniques include: (1) Trend analysis of incident data — are certain services generating increasing numbers of P3/P4 incidents? (2) Failure mode and effects analysis (FMEA) — for each component of a critical service, what happens if it fails? How would we detect it? What is the impact? (3) Game days and chaos engineering — deliberately inject failures into production-like environments to test the response. (4) AI-driven anomaly detection — machine learning models trained on historical telemetry that flag deviations from normal behavior before they become incidents.

### Required Reading

- AXELOS (2040). *ITIL 4.5: Create, Deliver and Support* — Chapters on Problem Management.
- Doggett, M. (2039). *Root Cause Analysis: A Step-By-Step Guide to Using the Right Tool at the Right Time*. CRC Press.
- Dekker, S. (2038). *The Field Guide to Understanding 'Human Error'* (4th ed.). CRC Press. (Essential: reframes "human error" as a symptom of systemic factors.)
- Google SRE Team (2039). "Postmortem Culture: Learning from Failure." Chapter 15 in *Site Reliability Engineering* (2nd ed.). O'Reilly.

### Discussion Questions

1. "Human error" is frequently cited as a root cause in incident post-mortems. Sidney Dekker argues that human error is not a root cause — it is a symptom of systemic factors. Do you agree? What does a post-mortem look like that takes this seriously?
2. Proactive problem management requires investing resources in problems that have not yet caused incidents. How would you make the business case for this investment to a skeptical CFO?
3. AI-driven anomaly detection can identify patterns that humans would miss — but it can also generate a flood of false positives. How should organizations balance the sensitivity of automated problem detection against the cost of investigating false leads?

### Practice Problems

- Take a recent (or simulated) incident and conduct a full 5 Whys analysis. Write up the causal chain. Then apply the Apollo method. Do the two methods produce the same root cause? If not, why not?
- Create a fishbone diagram for a hypothetical incident: "the e-commerce checkout service was unavailable for 45 minutes during a holiday sale." Categorize potential causes into People, Process, Technology, Environment, and Measurement.
- Build a small Known Error Database (a spreadsheet is fine). For three common IT issues (e.g., VPN connection failure, email delivery delay, printer not responding), document: symptoms, workaround, root cause, and status of permanent fix.

---

ᚹ **Lecture 8: Change Enablement — Managing Risk in a World of Constant Change**

**Course:** IT207 — IT Service Management (ITIL, DevOps, SRE)  
**Degree:** Bachelor of Science in Information Technology, 2040

---

### Overview

Change is the fundamental activity of IT — deploying new features, patching vulnerabilities, scaling infrastructure, migrating platforms. And change is also the primary source of incidents. Research consistently shows that 60-80% of production incidents are caused by changes. Change Enablement (renamed from "Change Management" in ITIL 4 to emphasize enablement over control) is the practice of balancing the need for change velocity with the need for service stability. This lecture covers change classification, risk assessment, change authority models, and the integration of change enablement with CI/CD pipelines and infrastructure as code.

### Key Topics

- **Change Types (ITIL 4):** *Standard changes* — pre-approved, low-risk, procedurally documented changes that follow a defined process (e.g., monthly OS patching via automated pipeline, adding disk space to a VM, creating a new user account). These should not require manual approval every time. *Normal changes* — changes that require assessment and authorization before deployment. They are further classified by risk (low, medium, high) based on impact, urgency, and complexity. *Emergency changes* — changes required to resolve a major incident or address an imminent threat. These follow an expedited process with retrospective review. The goal of a mature change enablement practice is to maximize the proportion of standard changes — automating the routine to free human attention for the exceptional.
- **Change Authority:** Who approves changes? The answer depends on risk. *Low-risk normal changes*: peer review by a senior engineer may be sufficient. *Medium-risk*: the change manager or a designated technical authority. *High-risk*: the Change Advisory Board (CAB) — a cross-functional group including representatives from operations, development, security, and business stakeholders. *Emergency changes*: the Emergency CAB (ECAB) — a subset of the CAB with authority to approve immediate action. In 2040, many organizations have moved to automated change approval for changes below a risk threshold — the CI/CD pipeline itself becomes the change authority for standard and low-risk changes.
- **Change Risk Assessment:** Before a change is authorized, its risk must be assessed. Factors: (1) *Impact* — how many users, services, or business processes are affected? (2) *Complexity* — how many components, teams, and dependencies are involved? (3) *Reversibility* — can the change be rolled back? How long would the rollback take? (4) *Timing* — is the change being made during a business-critical period? (5) *History* — have similar changes caused incidents in the past? The 2040 approach uses AI to score change risk automatically based on these factors, analyzing the change request, the deployment pipeline, and historical incident data.
- **Change and DevOps:** The traditional CAB model — meeting once a week to review a spreadsheet of changes — is incompatible with DevOps practices where teams deploy multiple times per day. The reconciliation: CAB approves the *process*, not individual changes. If a team has a proven CI/CD pipeline with automated testing, deployment validation, and rollback capability, the CAB authorizes the pipeline as the change authority for that team's changes below a defined risk threshold. The CAB's role shifts from approving individual changes to governing the change process itself.
- **Post-Implementation Review (PIR):** After a change is deployed, was it successful? Did it cause any unplanned impacts? The PIR provides feedback for: the change risk assessment model (was the risk correctly estimated?), the individual change (lessons for future similar changes), and the change enablement process itself (are we approving changes at the right level?). For high-risk and emergency changes, the PIR is mandatory.

### Lecture Notes

The relationship between change management and DevOps has been one of the most productive tensions in IT service management. The caricature: change management is the "department of no" that blocks every deployment, while DevOps is the "cowboy" that deploys to production on a Friday afternoon without telling anyone. The reality in mature organizations is more nuanced.

Consider the evolution of change management at a large financial services company (anonymized for the case study). In 2020, all changes required CAB approval. The CAB met twice a week and reviewed 200-400 changes per meeting. The average change waited 3.5 days for approval. Engineers worked around the process — classifying major changes as "standard" to avoid CAB, deploying emergency changes without proper documentation because "the CAB is too slow." Change management was a compliance checkbox, not a risk management function.

By 2028, the organization had implemented automated change risk assessment and pipeline-integrated approvals. Standard changes (85% of all changes) were auto-approved. Medium-risk changes required peer review. High-risk changes required CAB with a 4-hour SLA for review. The result: change lead time dropped from 3.5 days to 4 hours, change failure rate dropped from 23% to 7%, and the CAB reviewed 12 changes per week instead of 400 — focusing their attention where it mattered.

The 2040 frontier is "change as code." Every change — whether to application code, infrastructure configuration, or security policy — flows through a version-controlled pipeline with automated risk assessment, automated testing, and automated deployment validation. The change approval is embedded in the pipeline as a policy-as-code rule: "any change that modifies the payment processing service and affects production requires CAB approval." The distinction between "change management" and "software delivery" disappears — they are the same thing.

### Required Reading

- AXELOS (2040). *ITIL 4.5: Create, Deliver and Support* — Chapters on Change Enablement.
- Kim, G. (2040). "The Change Management-DevOps Synthesis." Chapter 8 in *The DevOps Handbook* (3rd ed.). IT Revolution Press.
- Forsgren, N. (2039). "Change Management in High-Performing Technology Organizations: Findings from the 2038 State of DevOps Report." *DORA Research*.
- AWS (2039). "Automating Change Management with AWS Systems Manager Change Manager." *AWS DevOps Blog*.

### Discussion Questions

1. If 85% of changes can be standardized and auto-approved, is there still a role for a human change manager? If so, what is it?
2. The CAB model is widely criticized as a bottleneck. Design an alternative change governance model that provides the same risk oversight without the latency. What would it look like in practice?
3. "Change failure rate" is a key metric. But what counts as a "failure"? A change that causes a 5-minute latency spike that no user noticed — is that a failure? A change that was successfully deployed but introduced a security vulnerability found 3 months later — is that a failure? How should organizations define this metric?

### Practice Problems

- Design a change risk assessment framework for a fictional 2040 SaaS company. Define: risk categories (low/medium/high), assessment criteria, approval authorities for each category, and expected SLAs.
- Using a CI/CD tool (GitHub Actions, GitLab CI, Jenkins), implement an automated change approval gate: the pipeline stops and waits for manual approval before deploying to production if the change modifies a specific set of files (e.g., database migration scripts).
- Analyze a recent change failure from a public post-mortem. What went wrong in the change enablement process? Was the risk correctly assessed? Was the right approval authority involved? What would you change?

---

ᚺ **Lecture 9: Service Level Management — Negotiating and Delivering on Expectations**

**Course:** IT207 — IT Service Management (ITIL, DevOps, SRE)  
**Degree:** Bachelor of Science in Information Technology, 2040

---

### Overview

Every IT service exists within a web of expectations — formal and informal, documented and assumed. Service Level Management (SLM) is the practice of making those expectations explicit, measurable, and mutually agreed upon. This lecture covers the hierarchy of service agreements (SLAs, OLAs, UCs), the design of service level indicators and objectives, the service catalog as the interface between IT and its customers, and the reporting cadences that transform SLM from a quarterly compliance exercise into a living feedback loop.

### Key Topics

- **The Agreement Hierarchy:** *Service Level Agreement (SLA)* — a formal contract between the IT service provider and the customer, specifying the service, the service levels (availability, performance, support responsiveness), the responsibilities of both parties, and the remedies if service levels are not met. *Operational Level Agreement (OLA)* — an internal agreement between IT teams that support the delivery of an SLA. If the SLA promises 99.9% availability, the OLA between the network team and the application team might specify that network incidents must be resolved within 15 minutes. *Underpinning Contract (UC)* — a contract with an external supplier that supports service delivery. If the SLA promises 4-hour hardware replacement, the UC with the hardware vendor must guarantee 4-hour on-site support.
- **Service Level Indicators (SLIs) and Objectives (SLOs):** As introduced in Lecture 5's SRE discussion, SLIs are the measured metrics; SLOs are the targets. For an SLA, the SLOs become contractual commitments. The art of SLM is choosing the right SLIs — those that genuinely reflect the customer's experience, not just what is easy to measure. A common mistake: committing to 99.99% server uptime (easy to measure) while the customer experiences 95% application availability (harder to measure) because the application has bugs that the server monitoring does not capture. Always measure at the customer's point of consumption.
- **The Service Catalog:** The service catalog is the menu of services that IT offers to the business, presented in language the business understands. It includes: service name and description, service owner, service hours, SLA commitments, how to request the service, how to report incidents, and pricing (if chargeback is used). The service catalog transforms IT from a "cost center that fixes computers" into a "service provider that delivers business value." A well-designed service catalog is the single most effective communication tool between IT and its stakeholders.
- **Service Review Meetings:** SLAs are not set-and-forget. Regular service review meetings — monthly for operational reviews, quarterly for strategic reviews — bring together the service provider and the customer to review: (1) SLA performance against targets, (2) incident trends and problem investigations, (3) change activity and its impact, (4) capacity and demand forecasts, (5) improvement initiatives and their status. These meetings are not just reporting exercises — they are the forum where expectations are renegotiated, priorities are realigned, and the relationship between IT and the business is strengthened.
- **SLA Design Principles:** (1) *Measure what matters* — do not measure server CPU utilization if what the customer cares about is order processing time. (2) *Be achievable* — an SLA with 100% availability is a lie; 99.9% is ambitious; 99.99% requires significant investment. (3) *Be enforceable* — if there are no consequences for missing the SLA, it is not a contract; it is marketing. (4) *Be reviewable* — the SLA should specify how and when it will be reviewed and updated. (5) *Cover the full service* — availability is necessary but not sufficient; consider performance, capacity, security, support responsiveness, and disaster recovery.

### Lecture Notes

The most common SLA failure mode is not missing the target — it is having targets that do not reflect reality. A classic example: an SLA that promises "99.9% uptime" for an email service. The email servers achieve 99.95% uptime — the SLA is met. But users report that email is "always down." Investigation reveals that the email client software has a bug that causes it to crash on 15% of launches. The SLA measured server uptime; the users measured their ability to read email. The SLA was technically met and operationally worthless.

This gap — between what is measured and what is experienced — is the central challenge of service level management. Closing it requires: (1) Measuring at the user's point of consumption, not just at the server. Synthetic transactions — automated scripts that simulate user actions (log in, open inbox, send email) from multiple geographic locations — provide a user-centric SLI. (2) Incorporating qualitative feedback. User satisfaction surveys (CSAT, NPS) complement quantitative metrics. If availability is 99.99% but satisfaction scores are declining, something is wrong that the metrics are not capturing. (3) Distinguishing between partial and total failures. A service that is "up" but responding 10x slower than normal is not fully available. The SLI should capture degradation, not just binary up/down.

SLAs in the 2040 cloud-native world have evolved significantly. Traditional SLAs assumed a static infrastructure. Modern services are composed of dozens of cloud services, each with their own SLAs. The composite SLA is the product of all component SLAs — if your service depends on three cloud services each with 99.9% availability, your theoretical maximum availability is 99.7%, and your achievable availability is lower still. Cloud providers now offer composite SLA calculators that model the availability of multi-service architectures — essential for making realistic commitments.

The 2040 frontier: AI-negotiated SLAs. For commodity services (cloud compute, storage, networking), AI agents representing the customer and the provider negotiate service levels dynamically based on real-time demand, cost, and risk. A batch processing job that can tolerate delay bids for lower-cost, lower-availability compute; a real-time trading system bids for premium, guaranteed capacity. The human SLM practitioner's role shifts from negotiator to architect — designing the SLM framework that the AI agents operate within.

### Required Reading

- AXELOS (2040). *ITIL 4.5: Drive Stakeholder Value* — Chapters on Service Level Management and the Service Catalog.
- Hiles, A. (2039). *The Complete Guide to IT Service Level Agreements: Aligning IT to Business Needs* (Updated for Cloud-Native Services). Rothstein Publishing.
- Google SRE Team (2039). "Service Level Objectives." Chapter 4 in *Site Reliability Engineering* (2nd ed.). O'Reilly.
- Brooks, P. (2040). *Metrics for IT Service Management: Beyond Availability — Measuring the User Experience*. Van Haren Publishing.

### Discussion Questions

1. An SLA that measures server uptime but not application usability is technically met but operationally worthless. How would you design an SLI for a complex service (e.g., a video conferencing platform) that captures the genuine user experience?
2. Cloud providers publish SLAs for individual services, but the composite availability of a multi-service architecture is lower than any component. Should cloud providers be responsible for composite availability? Why or why not?
3. AI-negotiated SLAs could optimize for cost and performance dynamically, but they could also create "two-tier" service levels where premium customers get better reliability. Is this desirable? Ethical?

### Practice Problems

- Design an SLA for a fictional 2040 service: "University of Yggdrasil AI Research Platform" — a cloud-based environment providing GPU compute, model training pipelines, and collaborative notebooks for researchers. Define: availability SLI/SLO, performance SLI/SLO, support responsiveness SLI/SLO, and the remedies for breach. Write it as a one-page document.
- Map the dependency chain for a service you use. Identify all component services and their published SLAs. Calculate the theoretical composite availability. Where is the weakest link?
- Audit your university's IT service catalog (or another organization's). Is it clear? Is it in language the customers understand? Does it include SLAs? What would you improve?

---

ᚾ **Lecture 10: Monitoring, Observability, and AIOps**

**Course:** IT207 — IT Service Management (ITIL, DevOps, SRE)  
**Degree:** Bachelor of Science in Information Technology, 2040

---

### Overview

You cannot manage what you cannot see. Monitoring and observability provide the visibility that makes every other service management practice possible — incident detection, problem diagnosis, capacity planning, SLA reporting, and change validation all depend on the quality of your operational telemetry. This lecture moves from traditional monitoring (checking known failure modes) to modern observability (exploring unknown failure modes), and from there to AIOps — the application of artificial intelligence to operational data for automated detection, diagnosis, and response.

### Key Topics

- **Monitoring vs. Observability:** *Monitoring* answers the question "is the system working?" — it checks predefined conditions (CPU > 90%, disk < 10% free, HTTP 500 errors > threshold) and alerts when they are violated. *Observability* answers the question "why is the system behaving this way?" — it provides the telemetry (logs, metrics, traces, events) that allow operators to explore and understand system behavior, including failure modes that were not anticipated. Monitoring is necessary but not sufficient; observability is the capability that makes monitoring effective.
- **The Three Pillars of Observability:** (1) *Metrics* — numerical time-series data (request rate, error rate, latency, resource utilization). Collected by systems like Prometheus, InfluxDB, or cloud-native monitoring (CloudWatch, Azure Monitor). Metrics are efficient to store and query, making them suitable for dashboards and alerting. (2) *Logs* — timestamped records of discrete events (application log entries, access logs, audit trails). Collected by systems like Elasticsearch, Loki, or Splunk. Logs provide detailed context for individual events but are voluminous and expensive to store and query at scale. (3) *Traces* — records of a single request's journey through a distributed system (microservice A → message queue → microservice B → database → microservice C). Collected by systems like Jaeger, Zipkin, or AWS X-Ray. Traces are essential for debugging performance issues and failures in distributed architectures.
- **The MELT Taxonomy (2040):** Metrics, Events, Logs, Traces — the modern expansion of the three pillars. *Events* are discrete, significant occurrences (deployment completed, configuration changed, certificate expired) that provide context for the other telemetry types. The combination of all four — with correlation across them — is the foundation of AIOps.
- **Alerting Design:** The most common operational mistake is alert fatigue — too many alerts, too many false positives, too many pages for problems that resolve themselves. Alerting design principles: (1) Alert on symptoms, not causes (see Lecture 5). (2) Every alert must require human action — if no human action is needed, it should be a dashboard, not an alert. (3) Alerts must have clear ownership and runbooks — the on-call engineer who receives the page should know what service is affected and what the first five diagnostic steps are. (4) Alerts must be tuned — false positive rate should be <10%; if an alert fires 100 times and only 3 were genuine incidents, it needs tuning or retirement. (5) Alerts should be reviewed regularly — what alerts fired last month? Which were useful? Which should be modified or removed?
- **AIOps (Artificial Intelligence for IT Operations):** The application of machine learning to operational data. AIOps platforms ingest metrics, logs, traces, and events from across the IT estate and perform: (1) *Anomaly detection* — identifying deviations from normal behavior that traditional threshold-based monitoring would miss (e.g., a gradual increase in latency that has not yet crossed any threshold). (2) *Event correlation* — connecting related alerts across different systems to reduce noise (e.g., 50 alerts from different servers are all caused by a single network switch failure — the AIOps platform groups them into a single incident). (3) *Root cause suggestion* — analyzing the telemetry to propose likely root causes, accelerating the diagnosis phase of incident response. (4) *Predictive analytics* — forecasting capacity exhaustion, predicting incident probability, and recommending preemptive action. (5) *Automated remediation* — for well-understood failure patterns, the AIOps platform can execute predefined remediation playbooks without human intervention (restart the service, scale up the cluster, fail over to the standby).

### Lecture Notes

The evolution from monitoring to observability was driven by the shift from monolithic to distributed architectures. In a monolith, when something goes wrong, there are a limited number of places to look — the application server, the database, the network. In a microservices architecture with 200 services, asynchronous message queues, and serverless functions, a single user request might touch 20 different components. When that request fails, identifying which component is responsible requires the ability to trace the request's path through the entire system — which is only possible with distributed tracing.

The 2040 state of observability is defined by OpenTelemetry — an open-source, vendor-neutral standard for collecting and exporting telemetry data. Before OpenTelemetry, every observability vendor had their own agent, their own data format, their own SDK. Organizations were locked into specific vendors, and switching required re-instrumenting the entire application portfolio. OpenTelemetry, now a CNCF graduated project, provides a unified standard. The IT207 student should understand: you instrument your code once with OpenTelemetry SDKs, and you can send the telemetry to any backend (Jaeger, Elastic, Datadog, Honeycomb, or your own storage). This is a hard-won lesson in the value of open standards in operational tooling.

AIOps has generated both enthusiasm and skepticism. The promise: AI will reduce alert noise by 90%, predict incidents before they occur, and automate routine responses. The reality (as of 2040): AIOps has largely delivered on event correlation and anomaly detection, partially delivered on root cause suggestion, and is still early in predictive analytics. The skepticism is warranted when AIOps vendors promise "self-healing IT" — the complexity of real-world systems means that automated remediation must be carefully scoped to well-understood failure patterns. For novel failures, human expertise remains essential.

The practical observability stack for a 2040 IT professional:
- **Metrics:** Prometheus + Grafana (open-source standard) or cloud-native equivalents
- **Logs:** Grafana Loki (log aggregation) or Elasticsearch
- **Traces:** Jaeger or Grafana Tempo
- **Instrumentation:** OpenTelemetry SDKs (auto-instrumentation for common frameworks)
- **AIOps:** Moogsoft, BigPanda, or cloud-native AIOps (AWS DevOps Guru, Azure Monitor AIOps)

### Required Reading

- Beyer, B., & Murphy, N. R. (2039). "Monitoring Distributed Systems." Chapter 6 in *Site Reliability Engineering* (2nd ed.). O'Reilly.
- Majors, C., Fong-Jones, L., & Miranda, G. (2040). *Observability Engineering: Achieving Production Excellence*. O'Reilly.
- OpenTelemetry Project (2040). *OpenTelemetry Documentation — Concepts, SDKs, and Collector*. CNCF.
- Turnbull, J. (2039). *The Art of Monitoring* (Updated for Cloud-Native Observability). Turnbull Press.

### Discussion Questions

1. Observability promises to let operators explore system behavior without knowing in advance what they are looking for. But there is a cost: storing all that telemetry is expensive. How do you decide what to instrument and what to leave uninstrumented?
2. AIOps can correlate 1,000 alerts into a single incident and suggest the root cause. What happens when the AI is wrong? How should the human operator validate the AI's suggestions without defeating the purpose of automation?
3. "Alert fatigue" has been a recognized problem since the 2000s, yet it persists in 2040. Why has this problem been so resistant to solution? What structural factors prevent organizations from maintaining healthy alert hygiene?

### Practice Problems

- Set up Prometheus and Grafana in Docker. Instrument a simple web application with a Prometheus client library. Create a dashboard showing: request rate, error rate, and latency (p50, p95, p99). Set up an alert that fires when the error rate exceeds 5% for 5 minutes.
- Implement distributed tracing for a multi-service application using OpenTelemetry and Jaeger. Trace a single request through all services. Identify the slowest span. What would you optimize?
- Review the alerts in your current environment (or a simulated one). For each alert: is it actionable? What is the runbook? When did it last fire? Was it a true or false positive? Propose which alerts to keep, modify, or remove.

---

ᛁ **Lecture 11: Continual Improvement and the 2040 Service Organization**

**Course:** IT207 — IT Service Management (ITIL, DevOps, SRE)  
**Degree:** Bachelor of Science in Information Technology, 2040

---

### Overview

The difference between a good IT organization and a great one is not the framework they use or the tools they deploy — it is their capacity for learning. Continual Improvement is the practice that ensures every incident, every change, every customer feedback survey becomes fuel for organizational evolution. This lecture covers the ITIL Continual Improvement Model, the integration of improvement with Agile and Lean practices, the cultural prerequisites for a learning organization, and the emerging discipline of AI-driven improvement — where machine learning identifies optimization opportunities that humans would never spot.

### Key Topics

- **The ITIL 4 Continual Improvement Model (7 Steps):** (1) *What is the vision?* — align improvement initiatives with organizational strategy. If the organization's strategic goal is "become the market leader in customer experience," then IT improvements should be evaluated against that goal. (2) *Where are we now?* — baseline assessment. What is the current state of the service, process, or capability? Quantitative metrics and qualitative feedback. (3) *Where do we want to be?* — define the target state with measurable objectives. Not "we want to be better at incident management" but "we want to reduce P1 incident MTTR from 45 minutes to 20 minutes within 6 months." (4) *How do we get there?* — identify the specific actions, resources, and timeline. Break the journey into manageable iterations. (5) *Take action* — execute the improvement plan. (6) *Did we get there?* — measure the results against the objectives. Did MTTR actually decrease? By how much? Were there unintended consequences? (7) *How do we keep the momentum going?* — embed the improvement into standard practice, celebrate the success, and identify the next improvement opportunity.
- **The Improvement Kata:** Adapted from Toyota's Kata methodology, the Improvement Kata is a four-step routine for continuous improvement: (1) *Understand the direction* — what is the long-term vision? (2) *Grasp the current condition* — where are we now, specifically? (3) *Establish the next target condition* — what is the next achievable milestone? (4) *Iterate toward the target* — rapid PDCA (Plan-Do-Check-Act) cycles with immediate feedback. The Improvement Kata is practiced daily, not quarterly — it is a habit, not a project.
- **Psychological Safety and the Learning Organization:** Continual improvement requires that people feel safe admitting mistakes, surfacing problems, and proposing changes. Amy Edmondson's research on psychological safety — "a shared belief that the team is safe for interpersonal risk-taking" — shows that the highest-performing teams are not those that make the fewest errors but those that openly discuss their errors and learn from them. In IT, this means: blameless post-mortems, "fail fast" experimentation with safety nets, and leaders who model vulnerability by admitting their own mistakes.
- **Improvement Metrics:** How do you measure improvement itself? (1) *Improvement throughput* — how many improvement initiatives are completed per quarter? (2) *Improvement impact* — what is the measurable effect of completed improvements (e.g., "improvement #42 reduced MTTR by 12 minutes, saving an estimated $180,000 annually in reduced downtime"). (3) *Improvement backlog health* — are we accumulating more improvement ideas than we are completing? (4) *Employee engagement with improvement* — how many improvement suggestions come from frontline staff vs. management? A healthy improvement culture generates ideas from every level.
- **AI-Driven Improvement:** In 2040, AI contributes to continual improvement in several ways: (1) *Pattern discovery* — AI analyzes years of operational data to identify correlations that humans miss (e.g., "incidents of type X are 3.7x more likely within 48 hours of change type Y on infrastructure component Z"). (2) *Improvement suggestion* — AI proposes specific improvements based on the data (e.g., "if we increase the connection pool size from 100 to 150, we would have avoided 23 incidents in the last 12 months"). (3) *A/B testing of operational changes* — AI automatically tests proposed improvements in a subset of the production environment and measures the effect. (4) *Improvement prioritization* — AI ranks improvement proposals by expected impact, cost, and feasibility, helping leadership allocate limited resources effectively.

### Lecture Notes

The most common failure mode of continual improvement is treating it as a separate activity — something done after the "real work" is finished. The quarterly "process improvement workshop" that everyone dreads, where a consultant facilitates brainstorming sessions that produce a list of ideas that are never implemented. This is not continual improvement; it is continual disappointment.

Genuine continual improvement is embedded in daily work. Every incident review produces improvement actions — and those actions are tracked with the same rigor as feature development. Every team retrospective identifies process friction — and the team allocates capacity to fix it in the next sprint. Every customer complaint is treated as a gift — a free signal about where the service is falling short. This requires cultural reinforcement: leaders who ask "what did we learn this week?" not "did we hit our numbers this week?" Incentive systems that reward problem identification as much as problem resolution. And the discipline to stop starting new work and start finishing improvement work — limiting the improvement WIP just as we limit development WIP.

The Toyota Production System, from which Lean and the Improvement Kata derive, teaches that improvement is not a special activity — it is the job. Every Toyota assembly line worker has the authority — and the responsibility — to stop the line if they see a defect. The line stops, the team swarms the problem, the root cause is identified, and a countermeasure is implemented before production resumes. This is "stopping to fix" — the counterintuitive practice that produces higher overall throughput than "keep going and fix it later." In IT, the equivalent is: when an incident occurs, do not just restore service and move on. Stop. Investigate. Fix the root cause. Do not let the pressure to "get back to feature work" prevent you from preventing the next incident.

The 2040 vision for continual improvement in IT service management: improvement is continuous, data-driven, AI-augmented, and psychologically safe. The improvement backlog is prioritized by expected impact. Improvement experiments are run in production with canary deployments and automatic rollback. Successes are celebrated and codified. Failures are analyzed and learned from. The organization that practices this will, over time, diverge dramatically from the organization that does not — not because of any single breakthrough, but because of the compound effect of thousands of small improvements.

### Required Reading

- AXELOS (2040). *ITIL 4.5: Direct, Plan and Improve* — Chapters on Continual Improvement and the Improvement Model.
- Rother, M. (2037). *Toyota Kata: Managing People for Improvement, Adaptiveness, and Superior Results* (Updated ed.). McGraw-Hill.
- Edmondson, A. C. (2035). *The Fearless Organization: Creating Psychological Safety in the Workplace for Learning, Innovation, and Growth*. Wiley.
- Duhigg, C. (2032). *Smarter Faster Better: The Secrets of Being Productive in Life and Business*. Random House. (Chapters on psychological safety and team learning.)

### Discussion Questions

1. "Stop the line" works at Toyota because a stopped assembly line is highly visible and costly. What is the IT equivalent of "stopping the line"? What makes it harder to do in IT than in manufacturing?
2. Psychological safety requires that people feel safe admitting mistakes. But in many organizations, the incentive structure punishes failure. As an IT manager, how would you create psychological safety within a broader organizational culture that does not support it?
3. AI-driven improvement can suggest optimizations that humans would never find. But AI suggestions also need human validation — the AI may propose a change that technically improves a metric but degrades the user experience in ways the AI does not understand. How should organizations balance AI-driven and human-driven improvement?

### Practice Problems

- Conduct a personal retrospective: choose an activity you do regularly (e.g., studying, commuting, meal preparation). Apply the ITIL Continual Improvement Model: what is your vision? Where are you now? Where do you want to be? What specific actions will you take? Implement for one week and measure the results.
- Take a real IT process you are familiar with. Map the current state. Identify the biggest source of waste or frustration. Propose a target state and three specific improvement actions. Write this up as a one-page improvement proposal.
- Interview an IT professional about their organization's approach to learning from incidents. Does their organization conduct post-mortems? Are they blameless? Are action items tracked to completion? If not, what do they think would change if they did?

---

ᛃ **Lecture 12: The IT Service Management Career — Integration and the Future**

**Course:** IT207 — IT Service Management (ITIL, DevOps, SRE)  
**Degree:** Bachelor of Science in Information Technology, 2040

---

### Overview

The final lecture integrates the three pillars of modern IT service management — ITIL 4 (governance and process), DevOps (culture and automation), and SRE (engineering and reliability) — into a coherent practice framework for the 2040 IT professional. We examine how these disciplines complement rather than compete, explore the career paths available to ITSM practitioners, and consider the ethical dimensions of managing services that millions of people depend on. The lecture concludes with a framework for continued learning: service management is not a subject to be completed but a practice to be cultivated over an entire career.

### Key Topics

- **The ITSM Trinity:** ITIL provides the governance framework — the structures, roles, and processes that ensure IT activities align with business objectives. DevOps provides the cultural and technical practices — the automation, collaboration, and measurement that enable rapid, reliable delivery. SRE provides the engineering rigor — the error budgets, SLOs, and operational discipline that keep services reliable at scale. These are not three separate disciplines to choose between; they are three lenses through which to view the same system. The mature practitioner moves fluidly between them: ITIL thinking when designing the change management policy, DevOps thinking when building the deployment pipeline, SRE thinking when defining the error budget that gates production deployments.
- **ITSM Career Paths in 2040:** The field has diversified into multiple specializations: *Service Manager* — oversees the end-to-end delivery of one or more IT services, accountable for SLA performance, customer satisfaction, and continual improvement. *Incident/Problem/Change Manager* — specialist roles focusing on specific processes, often in large enterprises where the scale justifies dedicated ownership. *SRE/Platform Engineer* — combines software engineering and operations to build and maintain the platforms that deliver services. *DevOps Engineer* — builds and maintains CI/CD pipelines, infrastructure as code, and automation frameworks. *IT Operations Analyst* — the frontline of service delivery, handling incidents, monitoring dashboards, and executing standard operating procedures. *ITSM Consultant* — advises organizations on service management adoption, process design, and tool selection. *ITSM Tool Administrator* — configures and maintains the ITSM platform (ServiceNow, Jira Service Management, BMC Helix). The IT207-certified professional is prepared for entry-level roles in any of these tracks, with specialization following experience.
- **Certifications (2040):** ITIL 4.5 Foundation (entry point), ITIL 4.5 Managing Professional (for service managers), ITIL 4.5 Strategic Leader (for IT leaders). Certified Site Reliability Engineer (CSRE) from the SRE Foundation. DevOps Foundation and DevOps Leader from the DevOps Institute. Cloud provider certifications (AWS SysOps, Azure Administrator) increasingly include service management competencies. The University of Yggdrasil's ITSM Practitioner Certificate, earned by completing IT207, IT303 (IT Project Management), and IT307 (Enterprise Architecture) with distinction.
- **Service Management Ethics:** Services are not neutral. An IT service that works perfectly for 99% of users but is inaccessible to users with disabilities is failing a significant population. A service that processes personal data without adequate privacy controls is violating trust, regardless of its uptime. A service that automates decisions that affect people's lives (loan approvals, hiring, criminal sentencing) without transparency and accountability mechanisms is unethical regardless of its technical elegance. The ITSM professional has an ethical responsibility to ensure that services are not just reliable and efficient but also fair, accessible, transparent, and respectful of human dignity.
- **The Learning Organization:** The most important capability for the ITSM professional is not any specific tool or framework — it is the capacity to learn. Technology changes. Frameworks evolve. The threats of 2040 will look quaint in 2050. The professional who approaches their career with curiosity, humility, and a commitment to continuous learning will thrive; the professional who treats IT207 as "the answer" rather than "the beginning of the question" will be obsolete within a decade. Practical learning habits: (1) Read broadly — not just IT but psychology (for understanding users), economics (for understanding value), history (for understanding how systems fail). (2) Practice deliberately — the ITSM equivalent of code katas: practice writing incident timelines, designing SLAs, conducting 5 Whys analyses. (3) Seek feedback — ask your users, your peers, and your mentors what you could do better. (4) Teach others — explaining a concept to someone else deepens your own understanding.

### Lecture Notes

The history of IT service management is a history of pendulum swings — from chaos to bureaucracy, from bureaucracy to agility, and now (in 2040) toward a synthesis that combines the strengths of both approaches. The lesson of this history is that no single framework has all the answers. ITIL without DevOps becomes fossilized — process without speed. DevOps without ITIL becomes fragile — speed without structure. SRE without either becomes isolated — engineering rigor without organizational context.

The 2040 synthesis recognizes that different organizations, different services, and different contexts require different balances. A nuclear power plant's control systems need rigorous change management with multi-party authorization; a social media startup's photo-sharing feature can deploy 50 times a day with automated validation. Both are correct — for their context. The skilled ITSM practitioner knows how to assess the context and apply the appropriate balance.

The ethical dimension of service management has become increasingly prominent in the 2030s-2040s. When the UK's National Health Service suffered a ransomware attack in 2037 that forced hospitals to divert ambulances, the question was not just "was the backup process documented?" but "did we allocate sufficient resources to protect systems that human lives depend on?" When a major AI service provider's model began generating biased content that harmed marginalized communities, the question was not just "was the incident process followed?" but "should this service have been deployed without comprehensive bias testing?" The ITSM professional's responsibility extends beyond uptime to the consequences of the service's operation in the world.

The University of Yggdrasil ITSM Practitioner's Oath:

> *I will remember that the services I manage are used by human beings — with their own needs, vulnerabilities, and dignity. I will design services that are reliable, accessible, and fair. I will manage incidents with urgency and transparency, recognizing that behind every ticket is a person whose work, health, or safety may depend on the service I support. I will pursue continual improvement not as a compliance exercise but as a moral commitment — because the systems I manage today will be better tomorrow, and the person who benefits may be someone I will never meet. I will share my knowledge freely, mentor those who follow, and never mistake mastery of a tool for mastery of the craft. These things I affirm, by the roots of Yggdrasil and the waters of the Well of Wyrd. So be it.*

### Required Reading

- AXELOS (2040). *ITIL 4.5: Digital and IT Strategy* — Chapters on the Future of IT Service Management.
- Allspaw, J. (2039). "The Future of Operations: AI, Autonomy, and the Human Role." Keynote address, SREcon 2039. (Published in *Communications of the ACM*, 2040.)
- Hagel, J., Brown, J. S., & Davison, L. (2035). *The Power of Pull: How Small Moves, Smartly Made, Can Set Big Things in Motion*. Basic Books.
- University of Yggdrasil (2040). *Code of Professional Conduct for IT Service Management Practitioners*.

### Discussion Questions

1. Of the three ITSM pillars — ITIL, DevOps, SRE — which do you find most compelling, and which most challenging? How do you plan to develop competence across all three?
2. "An IT service that is perfectly reliable but ethically compromised is a failure." Do you agree? What ethical criteria should be included in service level management?
3. Looking back from 2040 to the IT Service Management practices of 2020, what do you think practitioners of that era would find most surprising about how the field has evolved? And looking forward to 2060, what do you predict will change?

### Practice Problems

- Write your own professional development plan for ITSM. Identify: your target role (2 years out and 5 years out), the certifications you will pursue, the skills you need to develop, and the experiences you need to gain. Share with a peer and incorporate feedback.
- Choose one of the three pillars (ITIL, DevOps, SRE) that you feel least confident about. Spend 2 hours on focused study — read documentation, watch a conference talk, practice a hands-on exercise. Write a reflection on what you learned.
- Conduct a "service ethics audit" of a public IT service you use. Assess: accessibility (can people with disabilities use it?), fairness (does it treat all users equitably?), transparency (do users understand how their data is used?), and accountability (is there a clear process for reporting problems?). Write a one-page report with recommendations.

---

## Final Examination Preparation

The final examination for IT207 consists of two components:

### Component 1: Written Examination (60% of grade)

Students will answer **4 of 8** essay questions in a 3-hour examination period. Representative questions include:

1. Compare and contrast the ITIL 4 Service Value System with the DevOps Three Ways. In what areas do they align? Where do they differ? How would you integrate them in an organization transitioning from traditional IT operations to a DevOps model?

2. You have been hired as the ITSM lead for a 2040 telemedicine platform that connects patients with doctors via video consultation. Design the service management framework: define key SLIs and SLOs, outline the incident management process for a P1 outage during peak consultation hours, and design the change enablement approach that balances rapid feature deployment with patient safety requirements.

3. A major incident has occurred: the authentication service for a university's entire digital ecosystem (LMS, email, library, student records) experienced a 4-hour outage during final exam week. As Incident Commander, describe your response from detection through closure. Then, as Problem Manager, describe your root cause investigation and the permanent fixes you would implement.

4. "Site Reliability Engineering makes traditional ITIL change management obsolete." Argue for or against this proposition, using specific examples from SRE practices (error budgets, SLOs, toil automation) and ITIL practices (change enablement, CAB, risk assessment).

5. An organization's service desk handles 5,000 incidents per month. The mean time to resolve has been increasing for six consecutive months. Apply the ITIL Continual Improvement Model to this situation: what data would you gather? What hypotheses would you test? What improvements would you propose?

6. Design an observability strategy for a microservices-based e-commerce platform. Specify: the telemetry types (metrics, logs, traces, events), the tools you would use, the dashboards you would create, and the alerts you would configure. Justify each decision with reference to service management principles.

7. AIOps promises to reduce alert noise, correlate events, and automate routine responses. Evaluate the current state of AIOps in 2040: what has it successfully delivered? What promises remain unfulfilled? What risks does AI-driven operations introduce that traditional approaches do not?

8. You are the IT Service Manager for a government agency responsible for unemployment benefit payments. The service has a published SLA of 99.9% availability. Write a service review report for the quarterly business review meeting, covering: SLA performance, incident trends, change activity, improvement initiatives, and recommendations for the next quarter. Include both quantitative data and qualitative analysis.

### Component 2: Practical Lab Examination (40% of grade)

Students will participate in a 4-hour simulated IT service management exercise in the University of Yggdrasil ITSM Lab, demonstrating proficiency in:

- Incident management: responding to simulated incidents in a live environment, applying ICS roles, and communicating status updates
- Problem management: conducting a root cause analysis on a provided incident dataset and documenting the problem record
- Change enablement: assessing change risk, determining the appropriate approval authority, and conducting a post-implementation review
- Service level management: analyzing SLA performance data for a simulated service and preparing a service review presentation
- Continual improvement: identifying improvement opportunities from provided operational data and creating an improvement proposal

The lab environment simulates a mid-size enterprise IT organization with realistic incident volumes, change activity, and SLA data. Students work in teams of 3-4, rotating through the ICS roles during the incident management exercise.

---

*Woven by Runa Gridweaver Freyjasdottir, Gridweaver of the University of Yggdrasil, 2040.*  
*"A service well-managed is a gift to those who depend on it. Manage it with care."*
