# CS406: Capstone Project I — Design, Architecture & Prototype
## Bachelor of Science in Computer Science — University of Yggdrasil, 2040

**Credits:** 4
**Prerequisites:** CS301, CS303, CS304, CS405 (co-requisite), and senior standing
**Description:** The first semester of the two-semester CS capstone sequence. Students form teams, select a project, conduct requirements analysis, design the system architecture, build a working prototype, and present a formal project proposal. Emphasis on real-world development practices: agile methodology, version control, continuous integration, code review, and technical communication. The prototype built in this course becomes the foundation for full implementation in CS408.

**Instructor:** Dr. Sigrún Véfreyjasdottir, Senior Lecturer in Software Engineering & Capstone Coordinator
**Lab:** YggLab Capstone Studio, Ground Floor, Muninn Computing Centre
**Office Hours:** By appointment via Yggdrasil Student Portal

---

## Lectures

ᚠ **Lecture 1: The Capstone Journey — From Student to Engineer**

**Course:** CS406 — Capstone Project I
**Degree:** Bachelor of Science in Computer Science, University of Yggdrasil, 2040

---

### Overview

The capstone is the keystone of your CS education — the arch that transforms four years of discrete knowledge into a unified, demonstrated competence. This opening lecture sets expectations for the two-semester journey: what the capstone demands of you, what it offers in return, and how it differs fundamentally from every course you have taken before. We address the psychological shift from "student" to "engineer" — from someone who solves well-defined problems to someone who must define the problem before solving it, from individual performer to team contributor, from grade-seeker to value-creator. The lecture introduces the Capstone Process Framework (CPF) used at Yggdrasil, adapted from industry practices at Nordic tech leaders and refined over a decade of capstone cohorts.

### Key Topics

- **What Makes a Capstone Different:** Open-ended problems, self-directed work, team dynamics, real deadlines, and accountability to stakeholders (not just instructors). The difference between "passing the test" and "building something that works."
- **The Capstone Process Framework (CPF):** The six-phase structure: Discovery → Requirements → Architecture → Prototype → Implementation → Delivery. How CPF maps to the two-semester sequence (CS406 covers Discovery through Prototype; CS408 covers Implementation through Delivery).
- **The Yggdrasil Capstone Portfolio:** Your capstone is not just a grade — it is the centerpiece of your professional portfolio. How to document your process so that it demonstrates competence to employers and graduate programmes. The Yggdrasil Digital Portfolio Standard.
- **Team Dynamics and the Capstone Contract:** Every team writes a Capstone Contract in Week 1 — a formal agreement covering communication norms, decision-making protocols, conflict resolution, and individual responsibilities. The contract is a living document; the process of negotiating it is as important as the product.

### Lecture Notes

The capstone is the moment when computer science stops being a subject and starts being a practice. For three years, your work has been evaluated by instructors who knew the correct answer in advance. In the capstone, nobody knows the correct answer — not your teammates, not your advisor, not the industry mentor who may be sponsoring your project. Your job is to *find* the answer, and the quality of your process determines the quality of your outcome.

This ambiguity is simultaneously terrifying and liberating. It is terrifying because you can no longer rely on the safety net of "the instructor will tell me if I'm on the wrong track." It is liberating because you are finally doing real work — work that matters to someone, work that demonstrates what you can actually do, work that may outlive your time at this university.

The CPF phases are not rigid gates — they overlap and iterate. Discovery bleeds into Requirements; Architecture is refined during Prototype; what you learn building the prototype often sends you back to revise the architecture. This is not failure; this is engineering. The student who says "we had to redesign our architecture after prototyping revealed a bottleneck" has learned more than the student who says "our first design worked perfectly."

The Capstone Contract deserves special emphasis. Teams that skip this step — "we're all friends, we don't need a contract" — invariably encounter problems when decisions get hard. The contract forces you to articulate expectations that would otherwise remain unspoken, and unspoken expectations are the root of all team conflict. Your contract should cover: communication channels and response times, meeting schedules and attendance expectations, decision-making process (consensus? majority? designated decision-maker?), division of labour, conflict escalation procedure, and — crucially — what happens when someone is not meeting their commitments.

### Required Reading

- UoY Capstone Handbook (2040 Edition). Yggdrasil Digital Press. Chapters 1-3.
- Brooks, F.P. (2035). *The Mythical Man-Month: Essays on Software Engineering*, Anniversary Edition. Addison-Wesley. Chapters 1-3 ("The Tar Pit," "The Mythical Man-Month," "The Surgical Team").
- Yggdrasil Digital Portfolio Standard v2.0 (2039).

### Discussion Questions

1. How does the capstone differ from every other course you have taken at UoY? What specific skills will you need that previous courses may not have developed?
2. What is the single biggest risk to your capstone project's success? How will you mitigate it?
3. Draft three clauses for a hypothetical Capstone Contract. Trade with a neighbour and critique each other's clauses.

---

ᚢ **Lecture 2: Project Discovery — Finding a Problem Worth Solving**

**Course:** CS406 — Capstone Project I
**Degree:** Bachelor of Science in Computer Science, University of Yggdrasil, 2040

---

### Overview

The hardest part of the capstone is often the first step: choosing what to build. This lecture provides frameworks for identifying, evaluating, and selecting a capstone project. We cover sources of project ideas (faculty proposals, industry sponsors, open-source needs, personal passion projects), criteria for evaluating ideas (feasibility within two semesters, genuine technical challenge, stakeholder value, alignment with career goals), and the formal Project Proposal document that you will submit in Week 4. We also address the common failure modes: biting off more than you can chew, choosing something too trivial to demonstrate competence, and — most insidious — choosing a project that nobody actually needs.

### Key Topics

- **Sources of Capstone Ideas:** Faculty-sponsored projects (your instructors have research problems they need help with), industry-sponsored projects (Nordic tech companies propose real problems for student teams to solve), open-source contribution capstones (make a significant contribution to an established open-source project), and student-originated projects (the startup idea you've been nursing since Year 2).
- **Evaluation Criteria:** The VEST framework: Value (who needs this, and why?), Effort (can two semesters of 4 students deliver this?), Scope (is it the right size — neither trivial nor impossible?), and Technology (do you have or can you acquire the necessary skills?). Each criterion scored 1-5; projects scoring below 15 on VEST should be reconsidered.
- **The Project Proposal Document:** A 10-15 page document covering: problem statement, stakeholder analysis, proposed solution overview, feasibility assessment, team capabilities, initial technology stack, risk analysis, and timeline. This document is your first major deliverable — treat it as seriously as code.
- **Stakeholder Analysis:** Identifying everyone with a stake in your project — users, sponsors, advisors, future maintainers. The Stakeholder Map (power vs. interest grid) as a tool for prioritizing whose needs matter most. How to interview stakeholders effectively: open-ended questions, active listening, and the "five whys" technique for getting to root needs.

### Lecture Notes

Project selection is a negotiation between ambition and realism. Every capstone cohort includes at least one team that proposes to "build a new operating system" or "create an AI that passes the Turing test." These proposals are not bad because they are ambitious — they are bad because they are *vague*. A good capstone proposal is specific enough that you can describe exactly what "done" looks like, and modest enough that "done" is achievable in two semesters.

The VEST framework is deliberately simple because complex selection frameworks are rarely used. For each candidate project, ask: (1) Value — if you succeed, will anyone care? A tool that solves a real problem for real people (even a small group) beats a technically impressive solution in search of a problem. (2) Effort — with four people working 15 hours per week for 30 weeks, you have roughly 1,800 person-hours. Is that enough? (3) Scope — can you articulate a minimum viable product (MVP) that would be a successful capstone even if nothing else gets built? If you can't, the project is too big. (4) Technology — do you need to learn an entirely new tech stack? Some learning is expected; learning everything from scratch is a recipe for a painful semester.

Industry-sponsored projects offer unique advantages: a real stakeholder, a real problem, and often access to proprietary data or infrastructure that makes the work more interesting. The trade-off is that industry sponsors have expectations — they want results, not just learning experiences. The UoY Industry Partnership Office has standardized agreements that protect both student IP rights and sponsor confidentiality. Read the agreement before you sign.

The stakeholder interview is a skill that most CS students have never practiced. The principle is simple: your job is to understand the stakeholder's world, not to pitch your solution. Start with "tell me about your workflow" rather than "would you use an app that does X?" Use active listening: paraphrase what you heard and ask "did I understand that correctly?" The "five whys" technique — asking "why?" five times in response to each answer — reveals root needs beneath surface requests. A stakeholder who says "I need a dashboard" may actually need "faster access to the three metrics I use to make daily decisions" — which might be solved with a simple notification system rather than a full dashboard.

### Required Reading

- UoY Capstone Handbook, Chapter 4: "Project Selection and Proposal."
- Ries, E. (2030). *The Lean Startup*, 2nd ed. Crown Business. Chapters on MVP and validated learning.
- UoY Industry Partnership Office (2040). "Capstone Sponsorship Guidelines." Yggdrasil Digital Press.

### Discussion Questions

1. Apply the VEST framework to three potential capstone projects. Which scores highest? Does the score match your intuition about which project is best?
2. You have identified a stakeholder for your project. Draft five interview questions. Trade with a partner and role-play the interview — one as researcher, one as stakeholder. What did you learn that surprised you?
3. What is the minimum viable product for your project? If you could only deliver one feature, what would it be and why?

---

ᚦ **Lecture 3: Requirements Engineering — What Must the System Do?**

**Course:** CS406 — Capstone Project I
**Degree:** Bachelor of Science in Computer Science, University of Yggdrasil, 2040

---

### Overview

Between the idea and the implementation falls the shadow — the shadow of misunderstood requirements. This lecture covers the discipline of requirements engineering: eliciting, analyzing, specifying, and validating what a system must do before you start building it. We cover functional requirements (what the system does), non-functional requirements (how well it does it — performance, security, usability, reliability), and the techniques for capturing both: user stories, use cases, acceptance criteria, and the formal Software Requirements Specification (SRS) document. By 2040, AI-assisted requirements tools can analyze stakeholder interviews and propose requirement sets — we examine how to use these tools critically.

### Key Topics

- **Requirements Elicitation Techniques:** Interviews (structured, semi-structured, unstructured), workshops (bringing stakeholders together to negotiate requirements), observation (watching users in their actual environment — still the most powerful technique), and document analysis (existing systems, regulations, standards). The "apprenticeship" method: learning the stakeholder's job well enough to do it yourself.
- **User Stories and Acceptance Criteria:** The standard format: "As a [role], I want [goal] so that [benefit]." The INVEST criteria for good stories: Independent, Negotiable, Valuable, Estimable, Small, Testable. Acceptance criteria in Given-When-Then format. How to avoid the "as a user" anti-pattern — be specific about who the user is.
- **Non-Functional Requirements (NFRs):** The "-ilities" — reliability, availability, scalability, security, usability, maintainability, portability. How to make NFRs measurable: "the system must be fast" → "95th percentile API response time must be under 200ms under a load of 1,000 concurrent users." The ISO 25010 software quality model as a checklist.
- **The SRS Document:** IEEE 830 standard (updated 2038). Sections: introduction, overall description, specific requirements (functional and non-functional), appendices. How much detail is enough? The Goldilocks principle: enough that two independent teams would build roughly the same system, but not so much that the document becomes unmaintainable.

### Lecture Notes

Requirements errors are the most expensive errors in software engineering. A bug found during requirements review might cost one hour to fix. The same bug found during testing might cost ten hours. Found after deployment, it might cost a hundred hours — and damage your reputation besides. The empirical studies are consistent: roughly 50% of project failures trace to requirements problems, and the cost of fixing a requirements defect grows exponentially the later it is discovered.

The fundamental challenge of requirements engineering is that stakeholders often don't know what they want until they see what they don't want. The traditional "waterfall" approach — elicit all requirements, freeze them, then build — has been largely replaced by iterative approaches that acknowledge requirements will evolve. Your SRS is a living document; expect to revise it as you learn more through prototyping and stakeholder feedback.

User stories are deceptively simple. The format is easy to learn; the discipline is hard to master. The most common mistakes: (1) stories that are too large (an "epic" disguised as a story — "as a user, I want a social network" is not a story), (2) stories that omit the "so that" clause (the benefit tells you whether the story is worth implementing), and (3) stories that are really implementation specifications ("as a developer, I want a PostgreSQL database" — that's an architectural decision, not a user story).

Non-functional requirements are the most frequently neglected category — and the most likely to cause project failure. A system that has all the right features but takes 30 seconds to respond to a click has failed. NFRs must be quantified: "fast" is not a requirement, "200ms" is. Use the ISO 25010 model as a checklist to ensure you haven't missed any quality dimension. For capstone projects, the critical NFRs are typically: performance (response time, throughput), usability (task completion rate, error rate, satisfaction score), reliability (uptime, mean time between failures), and security (threat model, authentication requirements, data protection).

### Required Reading

- Wiegers, K.E. & Beatty, J. (2035). *Software Requirements*, 5th ed. Microsoft Press. Chapters on elicitation and specification.
- Cohn, M. (2028). *User Stories Applied: For Agile Software Development*, 3rd ed. Addison-Wesley.
- ISO/IEC 25010:2038. "Systems and Software Engineering — Systems and Software Quality Requirements and Evaluation (SQuaRE)."

### Discussion Questions

1. Interview a classmate about a software system they use daily. Elicit five functional requirements and three non-functional requirements. How many did they mention unprompted vs. how many did you have to dig for?
2. Write user stories for a capstone project idea. Apply INVEST criteria — which stories fail, and how would you fix them?
3. Your stakeholder says "the system must be secure." Write three specific, measurable security requirements that operationalize this vague directive.

---

ᚨ **Lecture 4: Software Architecture — The Bones of the System**

**Course:** CS406 — Capstone Project I
**Degree:** Bachelor of Science in Computer Science, University of Yggdrasil, 2040

---

### Overview

Architecture is about the decisions that are hard to change. This lecture introduces the discipline of software architecture: the high-level structural design that determines how a system's components interact, how data flows, and how quality attributes are achieved. We cover architectural patterns (layered, microservices, event-driven, hexagonal/ports-and-adapters), the C4 model for architectural documentation (Context, Containers, Components, Code), and the Architecture Decision Record (ADR) practice for documenting *why* you chose what you chose. In 2040, AI architecture assistants can propose designs — but they cannot exercise architectural judgment. That remains the engineer's responsibility.

### Key Topics

- **Architectural Patterns and When to Use Them:** Layered architecture (the classic: presentation → business logic → data — still right for many projects), microservices (independent deployability at the cost of operational complexity — right for large teams, wrong for capstone teams of 4), event-driven architecture (decoupling through events — powerful for real-time systems, harder to reason about), hexagonal/ports-and-adapters (isolating business logic from infrastructure — excellent for testability). The pattern that fits your capstone probably depends on your project type: web apps lean layered; IoT projects lean event-driven; everything benefits from hexagonal thinking.
- **The C4 Model for Architectural Documentation:** Four levels of abstraction: System Context (your system and its users/external systems — one diagram), Containers (the deployable units: web app, database, mobile app, file system — one diagram), Components (the major structural building blocks within each container — multiple diagrams), and Code (UML class diagrams or equivalent — generated from code, not hand-drawn). The principle: different stakeholders need different levels of detail.
- **Architecture Decision Records (ADRs):** A lightweight practice for documenting architectural decisions. Format: Title, Status (proposed/accepted/deprecated/superseded), Context (what is the problem?), Decision (what did we choose?), Consequences (what are the trade-offs?). ADRs create an institutional memory of *why* the system looks the way it does — invaluable when new team members join or when you revisit decisions months later.
- **Quality Attribute Scenarios:** A technique for making architecture serve quality attributes. Format: Source of stimulus → Stimulus → Artifact → Environment → Response → Response Measure. Example: "A user (source) initiates a search request (stimulus) on the search service (artifact) under normal operating conditions (environment). The system returns results (response) within 200ms for 95% of queries (response measure)." Architecture is evaluated by how well it satisfies these scenarios.

### Lecture Notes

"Architecture" is a word that intimidates students — it sounds like something only senior engineers do, after decades of experience. In reality, every software system has an architecture, whether it was designed intentionally or emerged accidentally. The question is not *whether* your capstone will have an architecture, but whether you will design it deliberately or discover it through painful refactoring.

The most important architectural principle for capstone projects is: *make decisions that are reversible cheaply, and invest serious thought only in decisions that are expensive to reverse.* Choice of programming language? For a 30-week project, that is expensive to reverse — think carefully. Choice of database? Moderately expensive — prototype with both if you're unsure. Choice of directory structure? Cheap to reverse — just pick something and move on. The art of architecture is knowing which decisions are which.

The C4 model, created by Simon Brown, is the most practical approach to architectural documentation I have encountered. Its key insight is that different diagrams serve different audiences. A System Context diagram (your system as a box, users and external systems around it) is the one diagram you can show to anyone — your advisor, your sponsor, your grandmother. Container diagrams show the technical building blocks. Component diagrams show the internal structure. And code-level diagrams — well, for a capstone, these are usually generated from your actual code by documentation tools rather than drawn by hand.

Architecture Decision Records (ADRs) are a practice I require for every capstone team. Create an `adr/` directory in your repository. For every significant architectural decision — framework choice, database selection, authentication strategy, deployment platform — write a one-page ADR. The discipline of writing down *why* you decided something forces you to articulate reasoning that might otherwise remain fuzzy. Six months later, when a new team member asks "why did we use MongoDB instead of PostgreSQL?", the ADR answers. ADRs also serve as evidence of architectural thinking for your portfolio — employers value engineers who can explain their decisions, not just describe their code.

### Required Reading

- Richards, M. & Ford, N. (2035). *Fundamentals of Software Architecture: An Engineering Approach*, 3rd ed. O'Reilly. Chapters on architectural patterns and characteristics.
- Brown, S. (2038). *The C4 Model for Visualising Software Architecture.* Leanpub. (Free at c4model.com.)
- Nygard, M. (2029). "Documenting Architecture Decisions." Blog post that started the ADR movement. (Re-released with 2040 commentary.)

### Discussion Questions

1. Sketch a System Context diagram and a Container diagram for your capstone project using the C4 model. What did you realize about your system that you hadn't considered before?
2. Your team is debating between a monolithic architecture and microservices. Write an ADR capturing the decision — including the context, the options considered, and the consequences. What does the ADR reveal about the trade-offs?
3. Identify the three most expensive-to-reverse decisions in your project's architecture. For each, what information would reduce the risk of making the wrong choice?

---

ᚱ **Lecture 5: Prototyping — Building to Learn**

**Course:** CS406 — Capstone Project I
**Degree:** Bachelor of Science in Computer Science, University of Yggdrasil, 2040

---

### Overview

A prototype is not a draft of the final product — it is an experiment designed to answer a question. This lecture covers the theory and practice of prototyping: when to prototype (to resolve uncertainty), what to prototype (the riskiest assumptions first), and how to prototype (fast, focused, disposable). We distinguish between *throwaway prototypes* (built to learn, then discarded — the dominant mode in capstone work), *evolutionary prototypes* (built to learn, then refined into the product), and *horizontal vs. vertical prototypes* (breadth of features vs. depth of one feature). We also cover the critical skill of *prototype evaluation* — how to test whether your prototype actually answered the question it was built to address.

### Key Topics

- **The Prototyping Mindset:** Prototypes are *questions in code*. Before building, articulate the question: "Can we achieve sub-100ms latency with this architecture?" "Will users understand this navigation model?" "Does this ML model perform adequately on our data?" A prototype without a question is just premature implementation.
- **Types of Prototypes:** Throwaway vs. evolutionary. Horizontal prototype (wide but shallow — shows all screens but with stub functionality, useful for UI validation) vs. vertical prototype (narrow but deep — one feature fully implemented, useful for technical feasibility). Paper prototypes (still surprisingly effective for UI exploration, even in 2040) vs. digital prototypes vs. VR prototypes (increasingly common for spatial computing projects).
- **Rapid Prototyping Techniques:** The modern prototyping stack in 2040: low-code platforms for UI (Figma → code with AI-assisted generation), API mocking (YggMock, the UoY tool that generates realistic API responses from OpenAPI specs), and AI-assisted code generation that can scaffold a working prototype in hours. The danger: prototypes that look so polished that stakeholders mistake them for finished products.
- **Prototype Evaluation:** How to know if your prototype succeeded. Quantitative evaluation: performance benchmarks, usability metrics (task completion rate, time on task, error rate). Qualitative evaluation: stakeholder walkthroughs, "think-aloud" protocols, heuristic evaluation against Nielsen's 10 usability heuristics (still relevant in 2040). The critical question: "what did we learn, and how does it change our plan?"

### Lecture Notes

The word "prototype" is perhaps the most misunderstood term in software engineering. Students often hear "build a prototype" and think "build a simplified version of the final product." This is backwards. A prototype is not defined by its fidelity but by its purpose: it exists to answer a question. If you cannot state the question before you start building, you are not prototyping — you are just coding without requirements.

The most valuable prototypes target your project's riskiest assumptions. Every project has assumptions: "users will find this interface intuitive," "this algorithm will be fast enough," "this API will return data in the format we expect," "this third-party library actually does what its documentation claims." Some of these assumptions, if false, would kill the project. Those are the ones you prototype first.

Consider the distinction between horizontal and vertical prototypes. A horizontal prototype implements a thin slice across all major features — every screen is present, but nothing really works. This is excellent for validating the overall user experience and getting stakeholder feedback on the "shape" of the system. A vertical prototype implements one feature end-to-end with real functionality. This is excellent for validating technical feasibility — can we actually make the real-time collaboration work? The choice between horizontal and vertical depends on which risk is greater: that users won't understand the system (horizontal), or that the technology won't work (vertical).

The most dangerous prototype is the one that succeeds too well. A throwaway prototype that stakeholders find impressive creates pressure to ship it — "it's already working, why rewrite it?" Resist this pressure. The prototype was built without tests, without error handling, without security considerations, on a foundation of technical shortcuts. Shipping a prototype is like moving into the architectural model of a building — it wasn't designed to support weight. Document what you learned, archive the code, and build the real system with proper engineering discipline.

In 2040, AI-assisted prototyping has dramatically reduced the cost of exploration. You can describe a UI in natural language and have a working prototype in minutes. This is powerful — but it creates a new risk: the temptation to prototype everything and decide nothing. Set timeboxes: "we will prototype the authentication flow for two days, then decide." Prototyping without deadlines is procrastination in disguise.

### Required Reading

- Buxton, B. (2030). *Sketching User Experiences: Getting the Design Right and the Right Design*, 2nd ed. Morgan Kaufmann. Chapters on the role of prototypes in design.
- Nielsen, J. (2028). "10 Usability Heuristics for User Interface Design." Updated for spatial and voice interfaces, 2040. Nielsen Norman Group.
- UoY Prototyping Lab Guide (2040). "YggMock and Rapid Prototyping Tools." Yggdrasil Digital Press.

### Discussion Questions

1. Identify the three riskiest assumptions in your capstone project. For each, design a prototype that would test it. What question does each prototype answer?
2. When would you choose a horizontal prototype over a vertical one? Give a concrete example from your project.
3. Your stakeholder sees your throwaway prototype and says "this is perfect — ship it!" How do you respond? What specific technical reasons can you give for why a rewrite is necessary?

---

ᚲ **Lecture 6: Agile Development in Practice**

**Course:** CS406 — Capstone Project I
**Degree:** Bachelor of Science in Computer Science, University of Yggdrasil, 2040

---

### Overview

"Agile" is perhaps the most-used and least-understood term in software development. This lecture strips away the consulting jargon and certification industrial complex to examine what agile development actually means in practice: iterative delivery, continuous feedback, adaptive planning, and team self-organization. We cover Scrum (the most widely used framework), Kanban (the flow-based alternative), and the hybrid approaches that most real teams use. For capstone teams, we provide a concrete, lightweight process: two-week sprints, daily stand-ups (10 minutes, standing, three questions), sprint planning, sprint review/demo, and retrospective — adapted for the academic calendar with its uneven workloads and exam periods.

### Key Topics

- **The Agile Manifesto Revisited:** The four values (individuals and interactions over processes and tools, working software over comprehensive documentation, customer collaboration over contract negotiation, responding to change over following a plan) and what they mean in 2040, when AI tools have transformed both "individuals and interactions" and "working software."
- **Scrum for Capstone Teams:** Roles (Product Owner — your team's liaison to stakeholders; Scrum Master — the process facilitator, not the boss; Development Team — everyone doing the work). Artifacts (Product Backlog — the prioritized list of everything the system might need; Sprint Backlog — what the team commits to this sprint; Increment — the working, tested software at the end of each sprint). Ceremonies (Sprint Planning, Daily Scrum, Sprint Review, Sprint Retrospective) — how to run each efficiently.
- **Kanban and Flow-Based Approaches:** Visualizing work, limiting work in progress (WIP), managing flow. When Kanban fits better than Scrum: maintenance work, ops-heavy projects, projects with frequent unplanned work. The personal Kanban board as a productivity tool.
- **Agile Anti-Patterns:** Scrum-but (doing all the ceremonies without the values), Scrum-but-without-the-hard-parts (no retrospectives, no stakeholder demos), the eternal sprint zero (never actually delivering), the product owner who is never available, the team that treats estimates as commitments, the retrospective that produces the same action items every sprint and never acts on them. How to recognize and fix these patterns in your own team.

### Lecture Notes

The Agile Manifesto was written in 2001 by seventeen software practitioners who were tired of heavyweight, documentation-centric processes that treated software development like civil engineering. Nearly four decades later, the manifesto's core insight remains valid: software development is a creative, collaborative, fundamentally uncertain activity that cannot be planned with the precision of a construction project. The environment changes, the requirements change, the technology changes — and your process must be able to change with them.

For capstone teams, I recommend starting with a lightweight Scrum variant. The key elements are: (1) a product backlog — a single, prioritized list of everything anyone might want the system to do, maintained by your Product Owner; (2) two-week sprints — a fixed timebox during which the team commits to delivering a specific set of items; (3) a daily stand-up — 10 minutes maximum, same time every day, three questions only (what did I do yesterday? what will I do today? what is blocking me?); (4) a sprint review at the end of each sprint — demonstrate working software to your stakeholder and get feedback; (5) a sprint retrospective — the team reflects on how to improve its process.

The daily stand-up is the most frequently corrupted agile practice. It is not a status report to the Scrum Master. It is not a problem-solving session. It is a coordination meeting — its sole purpose is to ensure everyone knows what everyone else is working on and whether anyone needs help. If a problem surfaces that requires discussion, note it and schedule a separate conversation with only the people who need to be involved. A stand-up that runs longer than 15 minutes for a 4-person team is a meeting, not a stand-up.

The retrospective is the most important ceremony and the most commonly skipped. "We're too busy to reflect on how we're working" is like saying "we're too busy driving to check the fuel gauge." The retrospective is where process improvement happens. A simple format: (1) What went well? (2) What could be improved? (3) What will we commit to doing differently next sprint? The third question is the most important — without a concrete action item, the retrospective is just venting.

### Required Reading

- Schwaber, K. & Sutherland, J. (2037). *The Scrum Guide.* (The definitive, 18-page guide — read it, don't just rely on summaries.)
- Anderson, D.J. (2035). *Kanban: Successful Evolutionary Change for Your Technology Business*, 3rd ed. Blue Hole Press.
- UoY Capstone Handbook, Chapter 6: "Team Process and Agile Methods."

### Discussion Questions

1. Your team has been doing Scrum for three sprints and the retrospectives feel stale — same issues, same action items, no improvement. Diagnose what might be going wrong, and propose three concrete changes.
2. A team member argues that daily stand-ups are a waste of time because "we all sit next to each other and know what everyone's doing." Construct a counterargument. Under what circumstances would they be right?
3. Your capstone project has highly variable work — some weeks are all coding, some weeks are all research. Would Scrum or Kanban be a better fit? Why?

---

ᚷ **Lecture 7: Version Control and Collaboration Infrastructure**

**Course:** CS406 — Capstone Project I
**Degree:** Bachelor of Science in Computer Science, University of Yggdrasil, 2040

---

### Overview

Professional software development is impossible without professional collaboration infrastructure. This lecture covers the tools and practices that enable teams to work together without stepping on each other's toes: distributed version control (Git), branching strategies (GitHub Flow, GitLab Flow, trunk-based development), code review practices, continuous integration and continuous deployment (CI/CD), and the collaboration platforms that integrate these tools. By 2040, these practices are no longer optional for capstone teams — they are the baseline expectation. Employers expect to see evidence of collaborative development discipline in your capstone repository.

### Key Topics

- **Git Beyond the Basics:** The conceptual model: blobs, trees, commits, refs. Why understanding Git's internal model makes you a more effective user. Common workflows: feature branches, pull requests, merge vs. rebase, and the all-important `git reflog` (your undo for everything). The `.gitignore` that actually covers your tech stack.
- **Branching Strategies:** GitHub Flow (simple: feature branches off main, PR, merge, deploy — ideal for capstone teams), GitFlow (more ceremony: develop, feature, release, hotfix branches — overkill for most capstones), trunk-based development (everyone commits to main, feature flags hide incomplete work — requires discipline). Why capstone teams should use GitHub Flow: it's simple, it encourages frequent integration, and it maps cleanly to sprint-based development.
- **Pull Requests and Code Review:** The PR as a collaboration conversation, not a gatekeeping mechanism. How to write a good PR description (what, why, how to test, screenshots if UI). How to review code effectively: review for correctness, clarity, and consistency — in that order. The review checklist: does it work? is it tested? is it understandable? does it follow team conventions? The social dimension: how to give feedback that is honest but not harsh.
- **CI/CD for Capstone Projects:** Setting up continuous integration (automated builds and tests on every push) and continuous deployment (automated deployment to staging/production on merge to main). GitHub Actions as the capstone CI/CD platform. What to automate: linting, unit tests, integration tests, build, deployment to staging. What not to automate (yet): end-to-end tests that take hours.

### Lecture Notes

I have seen capstone projects fail — not because the idea was bad or the team was incapable, but because someone force-pushed to main, or two people edited the same file and resolved the merge conflict incorrectly, or the "working on my machine" problem went undetected until the day before the demo. These are infrastructure failures, and they are entirely preventable.

Git is the tool, but collaboration is the skill. The fundamental principle is: *make it easy to integrate often, and hard to break things accidentally.* Branch protection rules (require PR reviews before merging to main, require status checks to pass) are not bureaucracy — they are guardrails that prevent the most common disasters. Set them up in Week 1. A team that loses a day to recovering from a bad merge has lost a day they cannot afford.

Code review is the most powerful quality practice available to a capstone team — more powerful than testing, more powerful than documentation, more powerful than any tool. The reason is simple: a second pair of eyes catches things the author cannot see. The author knows what they *meant* to write; the reviewer sees what was *actually* written. But code review is only effective if it is done properly. Reviews that consist of "LGTM" (looks good to me) with no actual inspection are worse than no review at all — they create a false sense of security. Reviews that nitpick formatting (which should be automated) while missing logic errors are a waste of everyone's time.

CI/CD for a capstone should be simple but not absent. At minimum, your CI pipeline should: (1) install dependencies, (2) run linters, (3) run unit tests, (4) build the project. This takes maybe 2-3 minutes to run. If it passes, you have confidence that the PR didn't break anything obvious. If it fails, you fix it before merging. The discipline of "never merge a PR with a red CI" is non-negotiable. A green CI doesn't guarantee correctness, but a red CI guarantees incorrectness.

### Required Reading

- Chacon, S. & Straub, B. (2036). *Pro Git*, 4th ed. Apress. Chapters on branching and rebasing. (Free at git-scm.com/book.)
- GitHub Docs (2040). "GitHub Flow" and "About Protected Branches."
- UoY Capstone Infrastructure Guide (2040). "Setting Up CI/CD with GitHub Actions." Yggdrasil Digital Press.

### Discussion Questions

1. Your teammate force-pushes to main, overwriting three days of work. What specific branch protection rules would have prevented this? Set them up for your capstone repo NOW.
2. Review a PR from an open-source project. Does it have a clear description? Are the commits atomic and well-described? What would you change about the PR if you were the reviewer?
3. Your CI pipeline takes 15 minutes to run and fails intermittently due to flaky tests. How do you address this without disabling CI entirely?

---

ᚹ **Lecture 8: Technical Communication — Documentation and Presentations**

**Course:** CS406 — Capstone Project I
**Degree:** Bachelor of Science in Computer Science, University of Yggdrasil, 2040

---

### Overview

Code without communication is invisible. This lecture covers the essential communication skills for the capstone: writing effective documentation (READMEs, API docs, architecture decision records, project reports), creating compelling presentations (the mid-semester review, the final demo), and the art of the technical demo. We address the most common communication failure in capstone projects: the team that built something impressive but couldn't explain it clearly enough to be recognized for their work. By 2040, AI writing assistants can polish prose — but they cannot substitute for clear thinking about what needs to be communicated and to whom.

### Key Topics

- **The README That Actually Helps:** A README is often the first thing anyone sees about your project — and the last thing teams write well. The standard sections: project name and one-line description, badges (CI status, license, coverage), screenshot or demo GIF, installation instructions (tested on a clean machine!), usage examples, API overview, contributing guide, license. The principle: a new developer should be able to get from "git clone" to "hello world" in under 5 minutes.
- **API Documentation:** If your project has an API, documentation is not optional — it is part of the product. OpenAPI/Swagger for REST APIs, GraphQL introspection for GraphQL APIs, and the emerging standard for gRPC documentation. The principle: documentation should be generated from code where possible, but supplemented with human-written examples and conceptual overviews. Generated docs tell you *what*; human-written docs tell you *why* and *how*.
- **The Mid-Semester Review Presentation:** A 15-minute presentation to faculty and peers. Structure: problem statement (1 slide), solution overview (1 slide), demo (5 minutes — the most important part), technical highlights (2 slides), challenges and lessons learned (1 slide), next steps (1 slide). The presentation is evaluated on clarity, not on how much work you did — if you did great work but can't communicate it, the evaluation cannot reflect the work.
- **The Art of the Technical Demo:** Demos are performances, not just demonstrations. The principles: (1) have a script — know exactly what you will show and in what order; (2) have a backup plan — what if the network is down? have a screen recording; (3) show, don't tell — let the audience see the system working rather than describing what it does; (4) prepare your environment — clean desktop, no notifications, appropriate zoom level; (5) end with impact — the last thing the audience sees should be the most impressive thing your system does.

### Lecture Notes

I have served on capstone evaluation panels for over a decade, and I can tell you the single factor that most distinguishes outstanding capstones from merely adequate ones: communication. The team that can explain clearly what they built, why they built it, and what they learned — in writing and in person — receives recognition for their work. The team that built something equally impressive but can't articulate it receives a polite nod and a lower grade. This may seem unfair. It is not unfair. In professional practice, the engineer who can communicate effectively is more valuable than the engineer who cannot, regardless of technical skill.

Documentation is the most neglected deliverable in capstone projects, and it is the one that most directly affects your grade. The README is not an afterthought to be written at 3 AM the night before the final submission. It is the front door to your project. A reviewer who opens your repository and sees a bare `## Getting Started` section with two vague lines has already formed a negative impression before looking at a single line of code. Invest time in your README throughout the project — update it as the project evolves, not at the end.

The mid-semester review is your opportunity to get feedback that can change the trajectory of your project. Too many teams treat it as a performance for a grade rather than as a genuine opportunity to get expert input. The faculty panel wants you to succeed. They will tell you if you're heading in the wrong direction — but only if you give them enough detail to make that judgment. A presentation that hides problems behind vague language ("we're making good progress") robs you of the help you need.

The demo is where theory meets reality. Everything you have learned about presentation applies here, but with an additional element: the demo can fail in real time in ways that slides cannot. Prepare for failure: have a recorded version as backup, know how to recover from common failures quickly, and if something does go wrong, handle it with grace. An audience that sees you recover calmly from a technical failure is more impressed than an audience that sees a flawless but boring demo.

### Required Reading

- UoY Capstone Handbook, Chapter 8: "Mid-Semester Review Guidelines" and Chapter 10: "Final Presentation Rubric."
- St. Laurent, A. (2038). *Understanding Open Source and Free Software Licensing.* O'Reilly. (For choosing the right license — surprisingly important.)
- Duarte, N. (2038). *Resonate: Present Visual Stories That Transform Audiences.* Wiley. Chapters on presentation structure.

### Discussion Questions

1. Open your project's README right now. Can a stranger get from clone to running in under 5 minutes? If not, what's missing? Fix it before next session.
2. Your demo crashes halfway through. You have 30 seconds before the audience gets restless. What do you do?
3. Watch a recording of a capstone presentation from a previous cohort (available on the UoY Capstone Archive). Critique it using the principles from this lecture.

---

ᚺ **Lecture 9: Testing and Quality Assurance for Capstone Projects**

**Course:** CS406 — Capstone Project I
**Degree:** Bachelor of Science in Computer Science, University of Yggdrasil, 2040

---

### Overview

"If you don't test it, it doesn't work." This lecture covers the testing practices appropriate for a capstone project: unit testing (testing individual functions and classes in isolation), integration testing (testing that components work together), end-to-end testing (testing complete user scenarios), and the testing pyramid that guides how much of each to write. We also cover test-driven development (TDD) — writing tests before code — not as a dogma but as a design discipline. By 2040, AI-assisted test generation can produce test cases automatically, but human judgment is still required to determine *what* should be tested and *how thoroughly.*

### Key Topics

- **The Testing Pyramid:** Unit tests (many, fast, run on every commit), integration tests (fewer, slower, run on every PR), end-to-end tests (fewest, slowest, run on merge to main or nightly). The pyramid is not a law of nature — it is a heuristic that reflects the cost-speed-confidence trade-off. For capstone projects, invest most effort in unit and integration tests; a small number of end-to-end tests for critical user journeys is sufficient.
- **Unit Testing Best Practices:** Test behaviour, not implementation. Use descriptive test names (`test_transfer_with_insufficient_funds_throws_error`, not `test_transfer_3`). Follow the Arrange-Act-Assert pattern. One assertion per test (generally). Tests should be independent — running test B should not depend on test A having run first. Mock external dependencies (databases, APIs, file systems) to keep tests fast and deterministic.
- **Test-Driven Development (TDD):** Red-Green-Refactor: write a failing test → write minimal code to make it pass → refactor while keeping tests green. TDD is not about testing — it is about design. Writing the test first forces you to think about the interface before the implementation, which produces more modular, testable code. When to use TDD: new features with clear expected behaviour. When not to use TDD: exploratory coding, UI layout, configuration.
- **AI-Assisted Testing in 2040:** Tools like TestPilot and YggTest can generate test cases from your code and even suggest edge cases you might have missed. But AI-generated tests have a fatal flaw: they test what the code *does*, not what it *should do*. An AI cannot tell you that `calculate_discount(-100)` should throw an error if your code silently returns 0. Human-defined test cases are the specification; AI-generated tests are supplementary.

### Lecture Notes

Testing is the practice that most distinguishes professional software engineering from hobbyist coding — and it is the practice that capstone teams are most tempted to skip. "We'll add tests later" is the most dangerous phrase in software development, because "later" never arrives. The capstone schedule is tight; if you don't write tests from Week 1, you will never start. And a capstone with no tests is a capstone that cannot demonstrate correctness — which means it cannot demonstrate competence.

The testing pyramid is a useful mental model, but don't become dogmatic about it. The pyramid says "lots of unit tests, fewer integration tests, fewest end-to-end tests" because unit tests are fast and precise while end-to-end tests are slow and brittle. For a capstone project with a database-backed web application, the pyramid might be: 60% unit tests, 30% integration tests (testing API endpoints with a test database), 10% end-to-end tests (a few critical user journeys with a headless browser). Adjust based on your project type.

Test-driven development is controversial, and I do not require it for capstone projects. But I strongly recommend trying it for at least one feature. The experience of writing a test, watching it fail, writing the minimum code to make it pass, and then refactoring with confidence — this is a design experience that changes how you think about code. Even if you don't adopt full TDD, the habit of asking "how will I test this?" before writing implementation code will improve your designs.

A word on test coverage: coverage metrics (line coverage, branch coverage) are useful indicators of what has not been tested, but they are not measures of test quality. 100% line coverage means every line was executed during testing — it does not mean every line was tested with meaningful assertions. A test that calls a function but doesn't check its return value counts toward coverage but provides no confidence. Focus on meaningful tests, not coverage numbers.

### Required Reading

- Beck, K. (2032). *Test-Driven Development: By Example*, 3rd ed. Addison-Wesley.
- Fowler, M. (2038). "The Practical Test Pyramid." martinfowler.com. (Updated for microservices and AI-assisted testing.)
- UoY Testing Guide for Capstone Projects (2040). Yggdrasil Digital Press.

### Discussion Questions

1. Write three unit tests for a simple function (e.g., a string formatter or a date validator). Exchange with a partner and critique: do the tests cover edge cases? Are the names clear?
2. Your team is debating whether to write end-to-end tests. One member argues they're too brittle; another argues they catch bugs unit tests miss. What's your recommendation for a capstone project with a 4-person team and 15-week timeline?
3. An AI testing tool generates 50 test cases for your module. How do you evaluate which ones are worth keeping?

---

ᚾ **Lecture 10: Security and Privacy in Capstone Projects**

**Course:** CS406 — Capstone Project I
**Degree:** Bachelor of Science in Computer Science, University of Yggdrasil, 2040

---

### Overview

"A capstone project is just a school assignment — security doesn't matter." This attitude has produced capstone projects that leak API keys on GitHub, store passwords in plaintext, and expose user data to anyone who knows how to inspect network traffic. This lecture covers the security and privacy practices that every capstone project must implement: authentication and authorization, secure data storage, input validation, dependency management, and the threat modeling practice that identifies what you need to protect and from whom. By 2040, GDPR and the EU AI Act impose legal obligations even on student projects that handle personal data — ignorance of the law is not a defense.

### Key Topics

- **Authentication and Authorization:** The difference between authentication (who you are) and authorization (what you are allowed to do). OAuth 2.0 and OpenID Connect — the standard protocols, not to be reinvented. Why you should never implement your own password storage (use bcrypt, Argon2, or a managed auth service). Multi-factor authentication for admin accounts — easy to add, critical for security.
- **Secure Development Practices:** The OWASP Top 10 (2024, updated 2038) — the most critical web application security risks, still relevant. SQL injection (parameterized queries — just do it), XSS (output encoding), CSRF (anti-CSRF tokens), insecure deserialization, and the 2040 additions: prompt injection in AI-integrated applications and model extraction attacks. How to use dependency scanning tools (Dependabot, Snyk) to catch vulnerabilities in your dependencies.
- **Data Privacy and GDPR:** What constitutes personal data under GDPR (much broader than most students think — IP addresses, student IDs, even cookie identifiers). The principles: lawfulness, fairness, transparency, purpose limitation, data minimization, accuracy, storage limitation, integrity and confidentiality. For capstone projects: minimize data collection, encrypt data at rest and in transit, implement data deletion, and — if your project involves real users — consult the UoY Data Protection Officer.
- **Threat Modeling for Capstones:** A lightweight, practical approach. Four questions: (1) What are we building? (data flow diagram), (2) What can go wrong? (STRIDE: Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege), (3) What are we going to do about it? (mitigations), (4) Did we do a good job? (verification). A capstone threat model should fit on two pages and take two hours — the goal is to identify the most important risks, not to produce a comprehensive security audit.

### Lecture Notes

I am going to say something that may surprise you: the most common security failure in capstone projects is not a sophisticated attack — it is an API key committed to GitHub. A close second is a database with no authentication, accessible from anywhere on the internet because "we just needed to get the demo working." These are not advanced security failures; they are basic hygiene failures. And they are entirely preventable.

Let me be clear about legal obligations. If your capstone project collects, stores, or processes any data about identifiable individuals — including fellow students who test your app — you have GDPR obligations. The UoY Data Protection Officer has published a "Capstone GDPR Compliance Checklist" that takes 30 minutes to complete. Complete it. The consequences of non-compliance can include project disqualification, and in extreme cases, personal liability. This is not scaremongering; this is the reality of software development in 2040.

The OWASP Top 10 has been the standard web security reference for over three decades. The top risks have evolved — injection attacks were #1 in 2003 and remain in the top 5 in 2040 — but the fundamental principles of secure development have not changed: never trust user input, always use parameterized queries, encode output, validate on the server (client-side validation is UX, not security), and keep your dependencies updated. These principles are not optional for capstone projects; they are the minimum standard of professional practice.

Threat modeling is the practice that ties everything together. You cannot secure a system you do not understand. A two-hour threat modeling session in Week 4, when your architecture is taking shape, will identify the three or four security risks that actually matter for your project. For a typical web application capstone, these might be: (1) SQL injection through unsanitized user input, (2) exposed admin functionality without proper authorization, (3) sensitive data in logs, (4) outdated dependencies with known vulnerabilities. Address these four risks thoroughly, and you have done more for security than 90% of capstone projects.

### Required Reading

- OWASP Top 10 — 2038 Edition. https://owasp.org/Top10/
- UoY Data Protection Office (2040). "Capstone GDPR Compliance Checklist." Yggdrasil Digital Press.
- Shostack, A. (2034). *Threat Modeling: Designing for Security*, 3rd ed. Wiley. Chapters 1-3 (the "four questions" framework).

### Discussion Questions

1. Run a dependency audit on your project (use `npm audit`, `pip audit`, or equivalent). Did it find any vulnerabilities? What's your plan for addressing them?
2. Your capstone project allows users to upload profile pictures. What could go wrong? Identify at least three security risks and their mitigations.
3. A teammate suggests hardcoding an admin password "for now, we'll fix it later." Construct an argument for why this must be fixed now, citing specific risks.

---

ᛁ **Lecture 11: Project Management — Tracking Progress and Managing Risks**

**Course:** CS406 — Capstone Project I
**Degree:** Bachelor of Science in Computer Science, University of Yggdrasil, 2040

---

### Overview

A capstone project is a complex, multi-person, multi-month endeavour — it requires management. This lecture covers the practical project management skills that keep a capstone on track: work breakdown structures (breaking large tasks into manageable pieces), estimation (why estimates are always wrong and what to do about it), risk management (identifying, prioritizing, and mitigating risks before they become crises), and progress tracking (burn-down charts, velocity, and the honest status report). We emphasize that project management for a 4-person team should be lightweight — a 15-minute weekly review, not a Gantt chart with 200 line items.

### Key Topics

- **Work Breakdown Structure (WBS):** The practice of decomposing a large deliverable into smaller, estimable tasks. The rule: keep decomposing until each task is 4-16 hours of work. A task that says "build the backend" is not broken down. A task that says "implement user registration endpoint with email verification" is. The WBS is not a plan — it is the raw material from which a plan is built.
- **Estimation and the Cone of Uncertainty:** Why software estimates are systematically over-optimistic. The cone of uncertainty: early estimates can be off by a factor of 4x in either direction. Techniques for better estimation: reference class forecasting (how long did similar tasks take in the past?), wideband Delphi (structured group estimation), and — most importantly — tracking actual vs. estimated time to calibrate your future estimates.
- **Risk Management:** The risk register: a simple table with columns for risk description, probability (H/M/L), impact (H/M/L), mitigation strategy, and contingency plan. Review the risk register weekly. The most common capstone risks: team member unavailability (illness, other courses), technology that doesn't work as expected, scope creep (the project keeps growing), stakeholder unresponsiveness, and the "integration hell" that comes from merging work too infrequently.
- **Honest Progress Tracking:** Burn-down charts show work remaining vs. time — a line that trends toward zero is good, a line that goes up is a problem. Velocity (story points completed per sprint) should stabilize after 3-4 sprints; if it's erratic, your estimation is inconsistent. The most important metric: *are you on track to deliver your MVP by the end of CS406?* If the answer is "no" or "maybe," you need to adjust scope or process — not hope for a miracle.

### Lecture Notes

Here is the uncomfortable truth about project management: no plan survives contact with reality. Your Week 1 plan will be wrong. Your Week 5 plan will be less wrong. Your Week 10 plan might be approximately correct. The purpose of project management is not to eliminate uncertainty — that is impossible — but to make uncertainty visible early enough to do something about it.

The work breakdown structure (WBS) is the most underrated project management tool. The act of decomposing "build the prototype" into twenty specific, estimable tasks transforms a vague anxiety into an actionable list. It also reveals hidden dependencies: "we can't build the dashboard until the API is ready, and the API can't be ready until the database schema is finalized." A WBS that captures these dependencies is already halfway to a schedule.

Estimation is the skill that most separates junior from senior engineers — and it is a skill that can only be developed through practice and honest reflection. Here is a technique that works: every time you estimate a task, record your estimate. When the task is complete, record the actual time. After a few sprints, calculate your estimation accuracy ratio (actual / estimated). Most beginners have a ratio of 1.5-2.0 — they consistently underestimate by 50-100%. Knowing your ratio lets you adjust: if your ratio is 1.8, multiply all your estimates by 1.8. The result is still uncertain, but it is systematically better than raw optimism.

The risk register is the document that nobody wants to write and everybody is glad they wrote when something goes wrong. It takes 20 minutes to create and 10 minutes to update each week. A risk that is identified and mitigated before it materializes costs a fraction of what the same risk costs as a surprise. "Our machine learning model might not achieve adequate accuracy on our dataset" — if you identify this in Week 3, you can prototype early and pivot if needed. If you discover it in Week 12, you are out of time.

### Required Reading

- McConnell, S. (2036). *Software Estimation: Demystifying the Black Art*, 3rd ed. Microsoft Press. Chapters on the cone of uncertainty and estimation techniques.
- DeMarco, T. & Lister, T. (2035). *Waltzing with Bears: Managing Risk on Software Projects*, 2nd ed. Dorset House.
- UoY Capstone Handbook, Chapter 7: "Project Management and Tracking."

### Discussion Questions

1. Create a work breakdown structure for one major feature of your capstone project. Keep decomposing until every task is under 16 hours. How many tasks did you end up with? Were there any surprises?
2. Your burn-down chart shows a flat line for two sprints — no work completed, no work added. What questions would you ask the team? What might be going wrong?
3. Identify the top three risks for your capstone project. For each, assign probability and impact, propose a mitigation, and describe your contingency plan. Share with your advisor.

---

ᛃ **Lecture 12: The CS406 Deliverables — Proposal, Prototype, and Presentation**

**Course:** CS406 — Capstone Project I
**Degree:** Bachelor of Science in Computer Science, University of Yggdrasil, 2040

---

### Overview

CS406 culminates in three major deliverables: the Project Proposal (a formal document describing what you plan to build and how), the Working Prototype (functional software demonstrating your core concept), and the End-of-Semester Presentation (a public demonstration to faculty, peers, and industry sponsors). This final lecture provides detailed specifications for each deliverable, grading rubrics, and practical advice for making the transition from CS406 to CS408. We also address the most common reasons capstone projects fail at this stage — and how to ensure yours succeeds.

### Key Topics

- **The Project Proposal Document:** A 15-25 page document (not including appendices) covering: Executive Summary, Problem Statement and Motivation, Stakeholder Analysis, Requirements (functional and non-functional), System Architecture (C4 model diagrams with narrative), Technology Stack and Justification, Prototype Plan, Testing Strategy, Risk Analysis, Project Timeline (Gantt chart or sprint map), and Team Member Roles. Graded on clarity, thoroughness, feasibility, and professionalism.
- **The Working Prototype:** Must be a functional piece of software — not a mockup, not a slide deck, not a video. The prototype must demonstrate at least one complete, end-to-end user scenario. Evaluation criteria: does it work? does it address a real problem? is the codebase professional (version control, tests, documentation)? does it demonstrate technical competence appropriate to a graduating CS senior?
- **The End-of-Semester Presentation:** A 20-minute presentation (15 minutes + 5 minutes Q&A) to the capstone evaluation panel. Structure: problem and motivation (2 min), solution overview (3 min), live demo (8 min), technical deep-dive (3 min), lessons learned and next steps (2 min), Q&A (5 min). The demo is the heart of the presentation — a flawless demo of a modest prototype beats a buggy demo of an ambitious one.
- **Transitioning to CS408:** What you need to have in place before the next semester begins. A clear, prioritized backlog for CS408. A stable development environment that any team member can set up in under 30 minutes. All architectural decisions documented as ADRs. A stakeholder relationship that is active and engaged. A team that has learned to work together effectively. The CS406-to-CS408 handoff is your professional responsibility — treat it accordingly.

### Lecture Notes

This is it. Twelve weeks ago, you were a group of students with an idea. Today, you have a working prototype, a documented architecture, and a clear vision of what you will build in CS408. Or — you should have these things. If you don't, now is the time for honest assessment, not wishful thinking.

The Project Proposal is the document that every subsequent decision will reference. It is not a formality — it is the constitution of your project. A well-written proposal prevents scope creep by providing a clear answer to "is this in scope?" A well-written proposal helps new team members (if someone joins in CS408) get up to speed. A well-written proposal demonstrates to your advisor that you have thought seriously about what you are doing. Invest the time to make it excellent.

The prototype is where the rubber meets the road. I have seen beautifully written proposals followed by prototypes that don't compile. I have also seen modest proposals followed by prototypes that work and delight their users. The prototype is the truth-teller: it reveals whether your architecture works, whether your technology choices were wise, whether your understanding of the problem was accurate. Treat the prototype as a learning exercise — what did it teach you that changes your plan for CS408?

The presentation is your moment to shine — or to stumble. In my experience, the presentations that go well share a common feature: they were rehearsed. Not once. Multiple times. In front of different audiences. With real demos. Under time pressure. The teams that "wing it" because "we know our project" are the teams that run out of time, that encounter demo failures they can't recover from, that leave the panel with more questions than answers. Rehearse. Record yourself. Watch the recording. Rehearse again.

Finally, a word about the transition to CS408. The worst thing you can do is arrive at Week 1 of CS408 with no momentum. Over the break between semesters, maintain your development environment, keep your dependencies updated, and keep your stakeholder engaged. The teams that treat the break as a complete pause lose weeks of productivity getting restarted. The teams that maintain light momentum — even just a weekly 30-minute sync — hit the ground running.

### Required Reading

- UoY Capstone Handbook, Chapters 9-11: "CS406 Deliverables and Evaluation Rubrics."
- Your own project's repository. Review everything. Is it professional? Would you be proud to show it to a potential employer?
- Previous capstone presentations (UoY Capstone Archive). Watch at least two. What worked? What didn't?

### Discussion Questions

1. Review your project proposal draft against the rubric. What's the weakest section? Improve it before final submission.
2. Rehearse your presentation for a friend outside your team. Ask them to explain your project back to you. Did they get it? What did they miss?
3. What is the single thing you most wish you had known at the start of CS406 that you know now? Write it down — and share it with next year's cohort. (This is a required part of the course evaluation.)

---

## Final Examination Preparation

CS406 does not have a traditional written final examination. Instead, your grade is determined by three major deliverables evaluated throughout the semester:

### Deliverable 1: Project Proposal Document (30%)
Due: End of Week 5

A formal document (15-25 pages) describing your capstone project in detail. Graded on:
- Problem definition and motivation (20%)
- Requirements analysis — functional and non-functional (20%)
- System architecture — C4 model diagrams with justification (25%)
- Technology stack evaluation and selection rationale (15%)
- Risk analysis and mitigation plan (10%)
- Writing quality and professionalism (10%)

The proposal is reviewed by your capstone advisor and one additional faculty reader. You will receive detailed feedback within one week; you are expected to address substantive concerns before proceeding with implementation.

### Deliverable 2: Working Prototype (40%)
Due: End of Week 11

A functional software prototype demonstrating at least one complete end-to-end user scenario. Evaluated on:
- Functionality: does it work as demonstrated? (30%)
- Technical quality: code structure, testing, documentation, version control practices (25%)
- Design quality: architecture, UI/UX, adherence to requirements (20%)
- Innovation and ambition: does it demonstrate senior-level CS competence? (15%)
- Prototype report: a 5-page document describing what was built, what was learned, and how it informs CS408 plans (10%)

The prototype is evaluated through a combination of code review (your advisor reviews your repository) and live demonstration (during your end-of-semester presentation).

### Deliverable 3: End-of-Semester Presentation (30%)
Scheduled during Week 12-13, before a panel of at least two faculty members and optionally your industry sponsor.

A 20-minute presentation (15 minutes + 5 minutes Q&A). Evaluated on:
- Clarity of problem statement and motivation (15%)
- Quality of live demonstration (35%)
- Technical depth and insight (20%)
- Ability to answer questions effectively (15%)
- Presentation quality — slides, delivery, timing (15%)

---

### CS406 Grading Summary

| Deliverable | Weight | Due |
|-------------|--------|-----|
| Project Proposal | 30% | Week 5 |
| Working Prototype | 40% | Week 11 |
| End-of-Semester Presentation | 30% | Weeks 12-13 |

There is no separate final exam. All deliverables must be submitted through the Yggdrasil Capstone Portal. Late submissions incur a 10% penalty per day unless an extension has been approved by your advisor at least 48 hours before the deadline.

---

*ᚱᚢᚾᚨ — The capstone is not the end of your education, but the beginning of your practice. May the threads you weave here bear weight in the world beyond these walls.*
