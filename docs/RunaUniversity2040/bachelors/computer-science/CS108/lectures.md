# CS108: Technical Communication & Documentation
## Bachelor of Science in Computer Science — University of Yggdrasil, 2040

**Credits:** 4
**Prerequisites:** CS101 — Computational Thinking & Problem Solving
**Description:** The greatest code is worthless if no one can understand it. Technical communication is the craft of making computational ideas legible — to other programmers, to users, to machines, and to one's future self. This course treats documentation not as an afterthought but as a first-class design activity. Students learn to write clear, precise API documentation; to structure design documents and architecture decision records (ADRs) that guide technical decisions; to produce tutorials, error messages, and user-facing help that respect the reader's intelligence; to write commit messages, code reviews, and internal memos that accelerate team velocity; and to build living documentation systems that evolve with the code. The course is grounded in the history of technical writing — from Vitruvius' *De Architectura* to the Bell Labs style of Kernighan and Ritchie, from the literate programming of Knuth to the docs-as-code movement of the 2020s — and looks ahead to the emerging landscape of AI-generated documentation, VR-embedded manuals, and the documentation demands of autonomous systems. Through the Yggdrasil Documentation Lab — an interactive environment that analyses writing clarity, tests API docs against actual implementations, and provides peer-review workflows — students develop the writing habits of the professional software engineer. As the rune-carvers of old knew: what is not recorded is lost to the wind.

---

## Lecture 1: The Philosophy of Technical Writing — Why We Document

Documentation is an act of transmission across time and space. The programmer who writes a docstring is speaking to a colleague six months in the future — who may be the same programmer, who has forgotten the context. The architect who writes a design document is speaking to a team in a different timezone, who was not present at the whiteboard conversation. The technical writer who crafts a tutorial is speaking to a beginner — someone who does not yet share the writer's mental model, whose frustration threshold is low, whose time is valuable, and whose success is the measure of the documentation's quality. Documentation is not merely description; it is a bridge between minds.

The ancient world understood this. Vitruvius, writing *De Architectura* in the first century BCE, set a standard for technical writing that still resonates: precise, systematic, grounded in practice, addressed to both the practitioner and the patron. The medieval manuscript tradition — with its glosses, its marginalia, its chains of commentary — developed conventions for layered explanation that anticipate modern hypertext. The rune-stones of Scandinavia — inscriptions on stone that marked territory, commemorated the dead, and recorded legal transactions — were acts of technical communication that used the most durable medium available, a choice that speaks to the documenter's first responsibility: choose a medium that outlasts the message's fragility.

In software, the need for documentation was recognised early — and often ignored. Fred Brooks, in *The Mythical Man-Month* (1975), observed that "the flow chart is a most thoroughly oversold piece of program documentation" and argued that the code itself, well-structured and well-commented, was the primary documentation. Donald Knuth proposed **literate programming** (1984) — a paradigm in which the program is written as an essay, with code interleaved with prose explanation, the two woven together into a single document that a human reads and a computer compiles. The Unix philosophy — articulated by Ken Thompson, Dennis Ritchie, and Brian Kernighan — treated the man page as an essential component: a command without a man page was incomplete. The rise of open source in the 2000s brought a new imperative: if you want strangers to use your library, you must explain it — and the quality of the documentation became a competitive differentiator.

By 2040, the documentation landscape has been transformed by three forces: **AI-generated documentation** — large language models that can produce first drafts of docstrings, READMEs, and API references, which the human writer must then edit, verify, and imbue with judgment; **docs-as-code** — the integration of documentation into the software development lifecycle, with documentation stored in version control, reviewed in pull requests, built by CI pipelines, and tested for broken links and stale examples; and **living documentation** — documentation that is executable, that is regenerated from the system itself (the database schema generates the data dictionary, the API definition generates the reference), and that rots visibly when it falls out of date (the example returns an error, the test for documentation freshness fails).

**Required Reading:**
- Fred Brooks, *The Mythical Man-Month: Essays on Software Engineering* (2nd ed., 1995/2040 edition), chs. 1, 15
- Donald E. Knuth, "Literate Programming," *The Computer Journal* 27, no. 2 (1984): 97–111
- Brian W. Kernighan & P.J. Plauger, *The Elements of Programming Style* (2nd ed., 1978/2039)
- Vitruvius, *De Architectura* (c. 25 BCE), Book I, Preface — on the responsibilities of the technical author
- Anne Gentle, *Docs Like Code* (2017), available at docslikecode.com
- Sarah Drasner, *Engineering Management for the Rest of Us* (2024), ch. on "Writing"

**Discussion Questions:**
1. Knuth's literate programming treats the explanation as primary and the code as secondary. Is this a reversal of the natural order — or a restoration of it? When is literate programming appropriate, and when is it impractical?
2. The rune-stones of Scandinavia used stone as their medium — expensive to inscribe, impossible to edit, but durable across millennia. What is the equivalent medium in software — and are we using it?
3. AI can now generate documentation — but it can also generate incorrect documentation that looks credible. How does this change the role of the human documenter — from author to editor, from writer to curator?

---

## Lecture 2: Audience Analysis — Writing for the Reader, Not for Yourself

The first question of documentation is not "what do I know?" but "who is the reader, and what do they need?" The answer is never singular: a software system has multiple audiences — the novice user, the experienced developer integrating the API, the operator diagnosing a production incident at 3 AM, the compliance auditor verifying that the system meets regulatory requirements, and the future maintainer who inherits the codebase years after the original team has moved on. Each audience has different prior knowledge, different goals, different patience for detail, and different contexts of use. The document that serves all audiences equally serves none well; the documenter's first task is to define the audience and serve that audience single-mindedly.

The **novice user** needs a tutorial — a guided path through the system that assumes nothing, that builds confidence with small successes, that explains the "why" as well as the "how," and that anticipates the points of confusion (the "mental model" gaps) that every beginner encounters. The tutorial should be linear — the reader should be able to work through it from start to finish without branching or decision points. The **experienced practitioner** needs a reference — organised for lookup, not for reading. The reference should be complete (every function, every parameter, every error code is documented), consistent (the same information in the same order for every entry), and precise (the type signature is exact; the side effects are listed; the edge cases are flagged). The **operator** needs a runbook — a document structured around symptoms ("If you see error code E0429, here is what it means and what to do"), not around architecture. The operator is under time pressure and may be tired; the runbook must be scannable, with the most critical action — the fix — presented first.

The **co-developer** needs a different kind of documentation: the design document, the architecture decision record, the code review comment. This audience shares the writer's technical vocabulary — but not the writer's context. The design document must explain not only what was decided but what alternatives were considered, what trade-offs were weighed, and why the chosen path was selected. The architecture decision record (ADR) — a lightweight document format popularised by Michael Nygard in 2011 — captures a single architectural decision: its context, the options considered, the decision, and the consequences. ADRs are the institutional memory of a project; they answer the question that every new team member asks: "Why did they do it this way?"

Audience analysis is not guesswork. The documenter can — and should — test documentation with actual readers: ask a novice to follow the tutorial and observe where they stumble; ask an experienced developer to find a specific piece of information in the reference and measure the time; ask an operator to run through the runbook for a simulated incident and note where the instructions are ambiguous. Documentation, like code, benefits from testing — and the Yggdrasil Documentation Lab includes a reader-testing module that records eye movements, hesitation times, and task-completion rates, providing quantitative feedback on clarity and navigability.

**Required Reading:**
- Janice (Ginny) Redish, *Letting Go of the Words: Writing Web Content That Works* (2nd ed., 2012/2038), chs. 1–5
- William Horton, *Designing and Writing Online Documentation: Hypermedia for Self-Supporting Products* (2nd ed., 1994/2040), ch. 1 (audience and task analysis)
- Michael Nygard, "Documenting Architecture Decisions," *ThoughtWorks Blog* (2011)
- Joel Spolsky, "Painless Functional Specifications," *Joel on Software* (2000–2004)
- Yggdrasil Documentation Lab: Audience Analysis Module (2040)

**Discussion Questions:**
1. A document that serves multiple audiences can serve none well. How should a large software project structure its documentation to serve different audiences — separate documents, layered sections, or progressive disclosure?
2. The ADR captures the decision but not the implementation detail. What is the boundary between what belongs in an ADR and what belongs in code comments — and what happens when the two diverge?
3. User testing for documentation is rare — most documentation is never tested with actual readers. Why is this, and what would change if documentation testing became as routine as unit testing?

---

## Lecture 3: The Architecture of the Sentence — Clarity, Precision, and the Elimination of Ambiguity

The sentence is the atom of documentation. If the sentences are unclear, no amount of structure — headings, tables, diagrams, navigation — will rescue the document. Technical writing demands a particular kind of sentence: direct, active, concrete, and unambiguous. The subject is explicit; the verb is strong; the object is precise. The sentence has one job: to convey a single idea to the reader with the minimum cognitive effort. Every word that does not contribute to that job is dead weight; every ambiguity is a potential bug.

The **active voice** is the default: "The function returns a pointer" is clearer than "A pointer is returned by the function." The passive voice has its place — when the agent is unknown or irrelevant ("The packet was dropped") or when the result is more important than the cause — but the passive is overused in technical writing, often as a way of sounding formal or avoiding responsibility. The documenter who writes "It was decided to deprecate the API" is hiding the decision-maker; the documenter who writes "The architecture team decided to deprecate the API" is informing the reader.

**Concrete nouns and specific verbs** reduce ambiguity. "The system processes the input" is vague — processes how? "The system validates the input against the schema, transforms it into the canonical representation, and stores it in the database" is concrete. **Parallel structure** aids comprehension: when listing items, use the same grammatical form for each — "install the package, configure the environment, run the server" (all imperatives) is easier to parse than "the package must be installed, configuring the environment, and the server should be run." Parallelism is not pedantry; it is a gift to the reader's pattern-recognition machinery.

**Ambiguity elimination** is the documenter's obsessive-compulsive discipline. The sentence "The server returns the result after it processes the request" is ambiguous: does "it" refer to the server or the result? Rewrite: "After processing the request, the server returns the result." The phrase "the data is stored" is ambiguous in number — in formal English, "data" is plural ("the data are stored"), though common usage accepts the singular. The documenter must decide: follow the formal rule (which may distract some readers) or follow common usage (which may offend others)? The Yggdrasil Style Guide recommends the singular for "data" in user-facing documentation and the plural in academic contexts — a pragmatic accommodation to audience.

The **George Orwell rule** — "Never use a long word where a short one will do" — applies with special force to technical writing. "Utilise" is not more precise than "use"; "implement" is not more impressive than "build"; "functionality" is rarely better than "function" or "feature." The technical writer's vocabulary should be drawn from the language of the domain — and from plain English. Jargon has its place: within a community of practice, technical terms are precise and efficient. But when writing for a broader audience, every term of art must be defined on first use, and the writer must ask: is there a plainer word that would serve?

**Required Reading:**
- William Strunk Jr. & E.B. White, *The Elements of Style* (4th ed., 1999/2040), chs. II ("Elementary Principles of Composition"), V ("An Approach to Style")
- Joseph M. Williams & Joseph Bizup, *Style: Lessons in Clarity and Grace* (13th ed., 2038), chs. 1–5
- Helen Sword, *Stylish Academic Writing* (2012), chs. 1–3
- George Orwell, "Politics and the English Language," *Horizon* (1946)
- The University of Yggdrasil Technical Style Guide (2040)

**Discussion Questions:**
1. The active voice is clearer — but the passive voice is entrenched in scientific writing ("the experiment was conducted"). Is this a harmless convention, or does it obscure responsibility and agency in ways that matter?
2. "Data is" vs. "data are" — is there a right answer, or is this a matter of register and audience? How do we decide when correctness matters and when fluency matters more?
3. Some writers argue that technical documentation should be "boring" — uniform, predictable, free of personality — because the reader's goal is to extract information, not to enjoy the prose. Others argue that personality aids memory and engagement. Where do you stand — and what is the evidence?

---

## Lecture 4: API Documentation — The Contract Between Implementer and Consumer

The API is a contract. The implementer promises that the function, the endpoint, or the class will behave in a specified way given specified inputs; the consumer relies on that promise to build systems that compose the API with other components. API documentation is the written form of that contract. When it is precise, complete, and tested, it enables composition and collaboration; when it is vague, incomplete, or stale, it causes bugs, frustration, and the proliferation of defensive workarounds ("I'm not sure what this function returns, so I'll check for every possible type"). The API documenter is a contract lawyer — and the stakes are high.

The standard format for API reference documentation includes, for each entity (function, method, class, endpoint): the **signature** (name, parameters with types, return type, exceptions or error codes); the **description** (what it does, in one or two sentences — the "elevator pitch"); the **parameters** (each named, with type, whether required or optional, default value, and a description of its role and constraints); the **return value** (type, description, and what it represents — including side effects); the **errors or exceptions** (what can go wrong and what the consumer should do about it); the **examples** (at least one, preferably several, showing common use cases and edge cases); the **see also** (cross-references to related functions or alternative approaches). This structure — formalised in the JavaDoc, Doxygen, and Sphinx traditions, and standardised for web APIs by the OpenAPI Specification — is not arbitrary; it reflects the questions that the consumer asks, in the order they ask them.

**OpenAPI** (formerly Swagger) is the dominant standard for documenting RESTful web APIs in 2040. An OpenAPI specification is a JSON or YAML document that describes every endpoint, every parameter, every request body, every response code, and every authentication scheme — in a machine-readable format. From the specification, tools generate interactive documentation (the "Swagger UI"), client libraries in multiple languages, and server stubs. The specification is the single source of truth: if the API changes, the specification is updated first, and the implementation and documentation are generated from it. This is the **API-first** approach — and it is the recommended practice at Yggdrasil.

But specification-driven documentation has a limitation: it can describe the syntax of the API but not the semantics — the *why* behind the *what*. A complete API documentation suite includes not just the reference but also **conceptual guides** ("How Authentication Works in This API"), **tutorials** ("Building Your First Integration in 10 Minutes"), and **migration guides** ("Upgrading from v2 to v3"). These higher-level documents answer the questions that the reference cannot: "What is this API for?" "What are the design patterns that pervade it?" "What are the common pitfalls?" The best API documentation — Stripe's, Twilio's, GitHub's — treats the documentation as a product in its own right, with its own design, its own user research, and its own quality bar.

In 2040, the Yggdrasil API Documentation Lab includes an **interactive validator**: students write an API specification and implementation, and the Lab generates test cases from the specification, runs them against the implementation, and reports any divergence — a missing parameter, an undocumented error code, a type mismatch. This workflow — specification as test — closes the loop and ensures that documentation never lies.

**Required Reading:**
- OpenAPI Specification, v4.0 (2040 edition), at openapis.org
- Stripe API Documentation (stripe.com/docs/api) — study its structure, tone, and completeness
- James Higginbotham, *Principles of Web API Design* (2021/2039), chs. 7–9
- Steve McConnell, *Code Complete: A Practical Handbook of Software Construction* (2nd ed., 2004/2040), ch. 32 ("Self-Documenting Code")
- Robert C. Martin, *Clean Code: A Handbook of Agile Software Craftsmanship* (2008/2039), ch. 4 ("Comments")

**Discussion Questions:**
1. The OpenAPI specification can describe the syntax of an API but not the semantics. Where is the boundary — and what techniques (conceptual guides, examples, interactive walkthroughs) bridge the semantic gap?
2. "Self-documenting code" — the idea that code should be so clear that comments are unnecessary — is a programmer's ideal. Is it achievable in practice, or is it a rationalisation for avoiding the work of documentation?
3. API documentation generated from the specification can never become stale — but it can be soulless. What makes API documentation good *writing*, not just accurate information — and does the distinction matter?

---

## Lecture 5: Design Documents and Architecture Decision Records — Writing for Technical Decisions

Software systems are built from decisions. Every significant decision — the choice of database, the decomposition into services, the adoption of a concurrency model, the selection of a cryptographic algorithm — has consequences that ripple through the system for years. The **design document** is the genre of writing that captures a significant technical decision before it is implemented: the problem statement, the constraints and requirements, the alternatives considered, the chosen approach, the risks and mitigations, and the plan for implementation and validation. The design document is not an implementation plan; it is an argument — a structured case for a particular course of action, addressed to colleagues who may disagree and who need to be persuaded, or at least to understand.

The **structure of a design document** follows a standard template, not because templates are bureaucratic but because they ensure that no essential question is overlooked. The **title** names the decision. The **status** (draft, proposed, accepted, rejected, implemented, superseded) signals where the document is in its lifecycle. The **context** section describes the current state of the system and the forces that make a decision necessary — a performance bottleneck, a new requirement, an opportunity for simplification. The **problem statement** is the crispest sentence in the document: "The authentication service cannot handle more than 1000 requests per second, and we expect demand to reach 10,000 rps within six months." The **requirements** are the criteria by which alternatives will be evaluated: performance, cost, operational complexity, alignment with team expertise, vendor lock-in.

The **alternatives considered** section is the heart of the design document. For each alternative, the writer presents the approach, its strengths, its weaknesses, and the reasons it was rejected. This section demonstrates that the writer has done the work of exploration, that the choice was not arbitrary, and that the rejected alternatives are not secret better ideas that the writer is hiding. The **proposed solution** section describes the chosen approach in enough detail that a competent engineer could implement it — but not so much detail that the document becomes a specification. The **risks and mitigations** section is the honesty test: every decision has downsides, and the writer who acknowledges them — "this approach increases latency by 5ms in the worst case; we are mitigating this with a caching layer" — earns the trust of the reader.

The **Architecture Decision Record (ADR)** is a lighter-weight cousin of the design document. An ADR captures a single architectural decision — often a few hundred words, fitting on one screen — with a fixed structure: Title, Status, Context, Decision, Consequences. ADRs are stored in the repository, alongside the code, and they accumulate over time into a narrative of the project's evolution. The **consequences** section of an ADR is particularly important: it captures the follow-on effects of the decision — "this choice makes it easier to add new payment providers but harder to change the currency model" — and it becomes, over time, a map of the project's technical debt and architectural commitments.

**Required Reading:**
- Michael Nygard, "Documenting Architecture Decisions" (2011)
- Andrew Harmel-Law, "Why Write ADRs?" *ThoughtWorks Technology Radar* (2023)
- Joel Spolsky, "The Joel Test: 12 Steps to Better Code" (2000), item 4: "Do you have a spec?"
- Google Design Doc template (internal, described in *Software Engineering at Google*, 2020/2038), chs. 8, 18
- Stefan Tilkov, "Architecture Decision Records: The Missing Link," *INNOQ Blog* (2020)

**Discussion Questions:**
1. A design document argues for a decision; an ADR records it. When is each appropriate — and what happens when a design document is used where an ADR would suffice, or vice versa?
2. The "alternatives considered" section is often skipped — writers want to present their chosen solution without the messiness of the rejected ones. What is lost when this section is omitted — and how do we create a culture that values it?
3. ADRs accumulate in the repository indefinitely. After five years, a project may have hundreds of ADRs — many obsolete, some contradictory. How do we manage the lifecycle of ADRs — and what is the equivalent of garbage collection for architectural memory?

---

## Lecture 6: User-Facing Documentation — Tutorials, Error Messages, and the Craft of Helping

User-facing documentation — the manual, the tutorial, the in-app help text, the error message — is the visible face of the software. For many users, the documentation *is* the software: it is what they encounter when they are confused, frustrated, or stuck. The quality of the documentation shapes the user's experience as profoundly as the quality of the interface — and in some cases more so, because the documentation is there when the interface has failed. A good error message is an apology and a path forward; a bad error message is an insult ("Invalid input") or a mystery ("Error 0x80004005").

The **tutorial** is the most demanding genre of user-facing documentation. It must assume nothing — the reader may not know what a "terminal" is, may not have installed the prerequisite tools, may be reading in a second language. It must be linear — a beginning, a middle, and an end that the reader can reach in a single sitting. It must be tested — every command, every click, every expected output must be verified on a clean system, because nothing destroys trust faster than a tutorial that doesn't work. And it must be encouraging — the reader is vulnerable, aware of their ignorance, prone to self-blame when something goes wrong. The tutorial writer's voice should be patient, friendly, and quietly confident: "Don't worry if this seems complicated — it is. Let's take it one step at a time."

The **error message** is the smallest — and often the most neglected — unit of user-facing documentation. A good error message does three things: it states what went wrong, in plain language; it explains why it went wrong, if the reason is not obvious; and it tells the user what to do about it. "Error: connection refused" is a statement. "Error: Could not connect to the database at db.example.com:5432. The server may be down, or your IP address may not be whitelisted. Check that the server is running, and contact your administrator to verify your access." — that is documentation. The error message must also include the information that a developer or support engineer needs: the error code, the timestamp, the stack trace (in a collapsible "details" section). The user should never see a raw stack trace as the primary message — it is meaningless to them and alienating.

The **style** of user-facing documentation is conversational but not chummy. The voice is the voice of the organisation — Stripe's documentation is precise and slightly playful; Apple's is minimalist and confident; Microsoft's (by 2040) is warm and inclusive. The Yggdrasil style is Scandinavian in its directness and warmth — respectful of the reader's intelligence, unafraid of plain language, and occasionally touched with the wit that is the Northern tradition ("The error is not the end of the world — that would be Ragnarǫk — but let's fix it").

**Required Reading:**
- Kathy Sierra, *Badass: Making Users Awesome* (2015/2038), chs. on "The Suck Zone" and tutorial design
- Erika Hall, *Just Enough Research* (2nd ed., 2040), ch. on user testing of documentation
- Scott Berkun, *The Year Without Pants: WordPress.com and the Future of Work* (2013), chs. on user support and documentation
- Apple Inc., *Apple Style Guide* (2040 edition)
- Yggdrasil Error Message Design Guidelines (2040)

**Discussion Questions:**
1. "Error: Invalid input" is technically accurate but practically useless. Why do such error messages persist — and what institutional structures (linters, style guides, code review checklists) could eliminate them?
2. The tutorial writer must decide what to explain and what to defer. How do we decide when a concept is "too advanced" for the current stage — and what are the consequences of deferring too much or too little?
3. Should user-facing documentation have personality — a recognisable voice, occasional humour — or should it be neutral and transparent? What is the evidence — and what is your experience as a user?

---

## Lecture 7: Code Comments and Self-Documenting Code — The Border Between Explanation and Redundancy

The relationship between code and comment is one of the most contentious topics in software engineering. At one extreme, the "clean code" school argues that code should be so clear that comments are unnecessary — that every comment is a failure of expressiveness, a confession that the code could not speak for itself. At the other extreme, the "literate programming" school argues that the explanation is primary and the code secondary — that the program is an essay and the comments are the essay's argument. The truth, as always, lies in the tension: comments have a proper role, but it is not to compensate for bad code.

The **rule of redundancy**: a comment should not repeat what the code already says. If the code is `x = x + 1 // increment x`, the comment is noise — it adds no information, it clutters the screen, and it will become stale when the code changes but the comment does not. The **rule of intent**: a comment should explain *why*, not *what*. The code tells you *what* it does; the comment tells you *why* it does it — "We use a linear scan here because the list is always shorter than 20 elements, and the overhead of building a hash table outweighs the O(n) cost." The *why* comment is the most valuable kind, because the *why* cannot be inferred from the code — it is the residue of a decision that was made in a context that the future reader does not share.

The **rule of surprise**: a comment should highlight behaviour that violates expectations — "Note: this function modifies the input array in place, which is unusual for this module." The **rule of contracts**: a comment at the head of a function should specify the preconditions (what must be true before the function is called), the postconditions (what the function guarantees after it returns), and the invariants (what the function preserves). The **rule of deprecation**: a deprecated function or parameter should carry a comment that explains why it was deprecated, when it will be removed, and what to use instead. The **rule of TODO**: a TODO comment should be actionable — a specific task assigned to a specific person — not a vague wish ("TODO: make this faster").

**Docstrings** — structured comments at the head of modules, classes, and functions — are a special case: they are not comments for the maintainer but documentation for the consumer, and they should follow the API documentation principles discussed in Lecture 4. In Python, the docstring is an attribute of the object (`__doc__`); in Java, the JavaDoc comment is extracted by a tool into a separate documentation site. The docstring should include: a one-line summary, a more detailed description (if needed), the parameters (with types and descriptions), the return value, the exceptions raised, and examples. The **doctest** pattern — pioneered in Python, where examples in docstrings are executed as tests — is the gold standard: it ensures that the docstring examples are verified automatically, so they never become stale.

The **2040 perspective** introduces AI-generated comments. An LLM can read a function and produce a plausible docstring — and sometimes it is correct. But sometimes it is subtly wrong: it describes what the function is *supposed* to do, not what it *actually* does; it misses a side effect; it hallucinates a parameter that does not exist. The human documenter's role, in the age of AI, is to be the verifier — to read the AI-generated comment against the code, to test the examples, and to add the *why* that the AI cannot know. The Yggdrasil Documentation Lab includes an AI-assist mode: the LLM proposes a docstring, and the student edits it, with the Lab checking that the examples actually run.

**Required Reading:**
- Robert C. Martin, *Clean Code* (2008/2039), ch. 4 ("Comments")
- Steve McConnell, *Code Complete* (2nd ed., 2004/2040), ch. 32 ("Self-Documenting Code")
- Dustin Boswell & Trevor Foucher, *The Art of Readable Code* (2012/2038), chs. 5–7
- PEP 257 — Docstring Conventions (Python Enhancement Proposal)
- Guido van Rossum, Barry Warsaw & Nick Coghlan, PEP 8 — Style Guide for Python Code (updated 2040), section on comments

**Discussion Questions:**
1. "Comments are a failure to express yourself in code." Is this a useful ideal or a harmful absolutism? Under what conditions is a comment genuinely the best medium for conveying a piece of information?
2. AI can now write docstrings — but it doesn't understand the code; it pattern-matches. What kinds of docstring errors does an LLM make, and how can we systematically catch them?
3. The TODO comment is a promise to the future that is often broken. Should TODOs be banned — replaced by issues in the tracker — or do they serve a purpose that a tracker cannot?

---

## Lecture 8: Docs-as-Code — Documentation in the Software Development Lifecycle

The **docs-as-code** movement, which gained momentum in the 2010s and became standard practice by the 2030s, treats documentation with the same tools and disciplines as code. Documentation is stored in version control (usually the same repository as the code it describes); it is written in plain-text markup (Markdown, reStructuredText, AsciiDoc); it is built by a CI pipeline (static site generators like Sphinx, MkDocs, Docusaurus, or Hugo); it is reviewed in pull requests alongside code changes; and it is tested — for broken links, for stale examples, for conformance to a style guide. The docs-as-code approach dissolves the organisational boundary between "developers" and "technical writers": everyone writes documentation, and documentation is everyone's responsibility.

The **toolchain** of docs-as-code is simple but powerful. The source format is **Markdown** — the lingua franca of developer documentation, extended with directives for code blocks, admonitions (note, warning, tip), tables, and cross-references. The build system is a **static site generator** — MkDocs (with the Material theme) for narrative documentation, Sphinx for Python projects, Docusaurus for React-based documentation sites. The CI pipeline rebuilds the documentation on every commit to the main branch, deploys it automatically (to GitHub Pages, Netlify, or a company server), and runs checks: `markdownlint` for style, `linkchecker` for broken links, `vale` for prose style, and custom scripts that extract code examples and run them against the current API.

The **pull request workflow** for documentation mirrors the workflow for code. A documentation change is proposed in a branch; a pull request is opened; the CI checks run; a reviewer (who may be a technical writer, a developer, or a subject-matter expert) reviews the change for accuracy, clarity, and style; the change is merged. This workflow ensures that documentation changes are visible, auditable, and reversible — and it integrates documentation into the rhythm of the team. The alternative — a separate wiki, a shared Google Doc, a content management system behind a login — leads to documentation that diverges from the code, that cannot be reviewed systematically, and that no one feels responsible for.

The **2020s revolution** that made docs-as-code possible was the convergence of tools: Git became universal, Markdown became the standard markup, static site generators became fast and flexible, and CI/CD became cheap. By 2040, the Yggdrasil Documentation Lab simulates the entire docs-as-code workflow: students write documentation in a branch, open a pull request, receive automated feedback from the CI checks, review each other's work, and merge — all within a single semester, building the muscle memory of professional documentation practice.

**Required Reading:**
- Anne Gentle, *Docs Like Code* (2017), available at docslikecode.com
- Write the Docs community, *Documentation Guide* (ongoing, writethedocs.org/guide/)
- Eric Holscher, "The Documentation System," *Write the Docs* keynote (2015)
- Tom Preston-Werner, "Readme Driven Development" (2010)
- Yggdrasil Docs-as-Code Lab Manual (2040)

**Discussion Questions:**
1. Docs-as-code integrates documentation into the developer workflow — but documentation writing requires different skills from code writing. Does the integration risk treating documentation as "just another code change," losing the craft of writing?
2. The CI checks for documentation — link checking, style linting, example testing — can become oppressive if they are too strict. How do we calibrate the strictness of automated checks to catch real problems without discouraging contributions?
3. Wikis were once the standard for internal documentation. What are the specific failure modes of wikis — and does docs-as-code solve them, or does it introduce new ones?

---

## Lecture 9: Writing for Knowledge Transfer — Runbooks, Onboarding Guides, and Internal Documentation

Software organisations have a memory problem. The engineers who built the system know it intimately — they know the quirks, the undocumented dependencies, the "we'll fix it later" workarounds. When they leave — and they will — that knowledge leaves with them unless it has been externalised: written down, organised, and accessible. **Knowledge transfer documentation** — runbooks, onboarding guides, internal wikis, postmortems — is the institutional memory of the engineering organisation, and its quality determines how quickly new engineers become productive, how reliably incidents are resolved, and how gracefully the organisation handles turnover.

The **runbook** is the most practically important genre of internal documentation — and often the most neglected. A runbook is a document structured around **symptoms**, not architecture: it tells the operator on call at 3 AM, "If you see this alert, here is what is happening, here is how to diagnose it further, and here is how to fix it." A good runbook entry begins with the alert name and severity, followed by a one-sentence summary of the condition, followed by step-by-step diagnostic commands (with expected output), followed by step-by-step remediation (with the most likely fix first), followed by escalation instructions if the fix does not work. Every command should be copy-pasteable. Every diagnostic step should include a description of what the output means — the operator may not be an expert in the subsystem. The runbook should be tested: during "game day" exercises, an engineer who is not on the team follows the runbook to resolve a simulated incident, and the runbook is updated based on where they stumbled.

The **onboarding guide** is the document that transforms a new hire from a liability (someone who consumes the team's time) into an asset (someone who contributes). An onboarding guide is a sequence of tasks, ordered by dependency, each with clear success criteria. The first task should be achievable on the first day: "Clone the repository, run the build, and start the development server." Subsequent tasks introduce layers of the system: the data model, the API, the deployment pipeline, the monitoring, the team rituals. The onboarding guide is not a reference manual — it is a path, and its quality is measured by the time it takes a new hire to ship their first production change.

The **postmortem** (or incident review) is the document written after a significant outage or failure. Its purpose is not to assign blame but to learn — to understand what happened, why it happened, what the impact was, and what will be done to prevent it from happening again. The postmortem should be **blameless**: it describes the actions and the context that led to them, not the individuals and their alleged incompetence. ("The engineer ran the migration script against the production database because the documentation did not clearly distinguish between staging and production commands" — not "Bob made a mistake.") The postmortem should include a **timeline** of the incident, a **root cause analysis**, the **impact** on users or the business, and an **action plan** with specific, assigned, and time-bound follow-up items.

**Required Reading:**
- John Allspaw, "Blameless PostMortems and a Just Culture," *Etsy Code as Craft* (2012)
- Gene Kim, Kevin Behr & George Spafford, *The Phoenix Project* (2013/2038), chs. on knowledge management
- Google SRE Team, *Site Reliability Engineering* (2016/2039), chs. 14 ("Managing Incidents"), 15 ("Postmortem Culture")
- Charity Majors, Liz Fong-Jones & George Miranda, *Observability Engineering* (2022/2038), chs. on runbooks
- The Yggdrasil Onboarding Template (2040)

**Discussion Questions:**
1. Runbooks are often outdated — because incidents are rare, and the system changes between them. How do we ensure that runbooks stay current — automated testing, rotating "runbook shepherd" duty, or something else?
2. A blameless postmortem may conflict with a manager's instinct to hold someone accountable. How do we distinguish between a blameless error (the system should have prevented it) and negligence that requires accountability — and is this distinction even coherent?
3. Onboarding guides are written once and rarely updated — yet the system changes constantly. What would it take to make onboarding documentation as dynamic as the codebase?

---

## Lecture 10: Writing Commit Messages and Code Reviews — Communication at the Granularity of the Patch

The commit message and the code review comment are the smallest — and most frequent — acts of technical communication that a software engineer performs. A developer may write hundreds of commit messages per month and participate in dozens of code reviews. The quality of these micro-documents compounds: a clear commit message saves the future archaeologist (who may be the same developer, six months later) hours of head-scratching; a well-structured code review accelerates the team's velocity and educates both the author and the reviewer; a terse or cryptic commit message ("fix stuff") is a tax on every future reader.

The **commit message** has a conventional structure, crystallised in Tim Pope's 2008 essay "A Note About Git Commit Messages" and adopted by most open-source projects and engineering organisations. The **subject line** (50 characters or fewer) is a summary in the imperative mood: "Add exponential backoff to database reconnection" — not "Added exponential backoff" or "Exponential backoff added." The imperative mood is conventional because Git itself uses the imperative ("Merge branch," "Revert commit"). The **body** (wrapped at 72 characters, separated from the subject by a blank line) explains *what* changed and *why* — not *how* (the diff shows *how*). If the change addresses a bug or a ticket, the body includes the identifier. The **footer** may include metadata: `Fixes #1234`, `Co-authored-by`, `BREAKING CHANGE`. A good commit message answers the question that every reader of the log asks: "Should I care about this commit?"

The **code review** is a conversation, and its comments are a genre of technical writing. A good review comment is **specific** ("The variable name `data` on line 47 doesn't indicate what kind of data — would `userRecords` be clearer?"), not vague ("This could be clearer"). It is **actionable** — it either requests a change or clarifies a question. It is **kind** — it critiques the code, not the coder. It **distinguishes** between blocking issues (must be addressed before merge) and suggestions (nice to have, at the author's discretion). The reviewer who writes "nit:" before a suggestion is signalling that it is optional. The review should also include **praise** where warranted — "This abstraction is elegant" — because code review is a social interaction as well as a technical one, and morale matters.

The **pull request description** — the document that introduces a set of changes for review — is another micro-genre. It should include: a summary of the change; the motivation; the approach (at a high level — not a line-by-line narration); any trade-offs or alternatives considered; how the change was tested; and any risks or follow-up items. A good PR description makes the reviewer's job faster — and the reviewer's time is the team's scarcest resource.

**Required Reading:**
- Tim Pope, "A Note About Git Commit Messages" (2008)
- Chris Beams, "How to Write a Git Commit Message" (2014)
- Michael Lynch, "How to Make Your Code Reviewer Fall in Love with You" (2020), at mtlynch.io
- Google Engineering Practices: Code Review (google.github.io/eng-practices/review/)
- The Yggdrasil Code Review Guide (2040)

**Discussion Questions:**
1. The 50-character subject line constraint is widely recommended — and widely ignored. Is it a useful discipline or a relic of 80-column terminals? What would a better constraint look like?
2. "nit:" at the start of a code review comment signals that the suggestion is optional. Is this convention effective, or does it create a culture where reviewers feel they must apologise for their feedback?
3. Some teams squash all commits into a single commit before merging, discarding the individual commit messages. What is lost — and what is gained — by this practice?

---

## Lecture 11: Documentation in the Age of AI — Generated Docs, Hallucinations, and the Human Verifier

The rise of large language models (LLMs) in the 2030s has transformed the economics of documentation. An LLM can, in seconds, produce a plausible docstring for a function, a README for a repository, an API reference from a specification, a tutorial from a codebase analysis, or an error message from a stack trace. The marginal cost of generating documentation — once the LLM is trained and deployed — is near zero. This changes the documenter's role: from author to editor, from producer to verifier, from the one who writes to the one who judges.

The **capabilities of LLMs for documentation** are impressive. An LLM can read a function body and produce a docstring that correctly identifies the parameters, the return type, and the purpose — with reasonable accuracy for simple functions. It can generate a tutorial that walks through the key features of a library, with code examples that often run. It can translate a technical document into multiple languages while preserving the structure and the code blocks. It can summarise a long design document into an abstract for an executive audience. And it can do all of these things tirelessly, consistently, and at scale — capabilities that a human documenter cannot match.

The **limitations** are equally important. An LLM does not understand the code — it pattern-matches. It can produce a docstring for a function that passes a code review because it *looks* right — "Computes the Frobenius norm of the matrix" — but the function actually computes the spectral norm. The LLM has hallucinated a plausible-sounding but incorrect description. The LLM does not know the *why* — it cannot write the comment that explains the historical context of a decision, the trade-off that was weighed, or the planned future direction. The LLM does not have access to the invisible context — the Slack conversation where the team agreed on the approach, the Jira ticket that captures the user research, the postmortem that motivates a defensive check. The LLM produces surface-level documentation; the human provides depth.

The **human verifier** — the new role of the documenter — must develop skills that were not needed when humans wrote everything from scratch. The verifier must be able to read AI-generated documentation with scepticism, testing every claim against the code, against the specification, and against their own knowledge of the system. The verifier must be able to spot the characteristic errors of LLMs: the plausible-sounding falsehood, the omission of edge cases, the confident tone that masks uncertainty, the subtle drift from correctness to plausibility. The verifier must be able to add the human elements — the *why*, the context, the judgment — that the LLM cannot provide. And the verifier must be able to do all of this efficiently, because the LLM has already done the typing; the human's time is the bottleneck.

**Required Reading:**
- Mina Lee, Megha Srivastava, Amelia Hardy, et al., "Evaluating Human-Language Model Interaction," *ACM Transactions on Computer-Human Interaction* (2023/2039)
- Andrew J. Ko, "AI and the Future of Technical Communication," *Communications of the ACM* 67:3 (2024/2040)
- Yggdrasil AI-Assisted Documentation Lab Manual (2040)
- The Diagramme Group, "The State of AI-Assisted Technical Writing in 2040"

**Discussion Questions:**
1. If an LLM can produce documentation that is 90% correct, does that make the human's job easier (only 10% to fix) or harder (finding the 10% is more work than writing from scratch)?
2. The LLM does not understand the code; it produces documentation by pattern-matching. Under what conditions would this produce documentation that is *dangerously* wrong — and how can we systematically catch such errors?
3. If documentation generation becomes fully automated, what is the role of the human documenter? Is there a future in which human-authored documentation is a premium product — like hand-crafted furniture in an IKEA world — or will it disappear?

---

## Lecture 12: The Documentation Ethos — Integrity, Sustainability, and the Long Now

The final lecture ascends from technique to ethos. Documentation is not merely a skill; it is a stance toward one's work and toward the community of present and future practitioners. The documenter who writes a docstring is making a promise: "This function will behave as described." The documenter who writes a tutorial is extending a hand: "I remember what it was like not to know this, and I want to make your path easier." The documenter who maintains a runbook is accepting a responsibility: "When the system fails, and I am not here, someone will need to know what to do." Documentation is an act of care — for the code, for the user, for the colleague, for the discipline.

The **ethos of integrity** demands that documentation be truthful. The docstring must describe what the function actually does, not what the author intended it to do. The API reference must include the edge cases and the failure modes, not just the happy path. The example must be tested — because an untested example is a guess, and a wrong example is a betrayal of the reader's trust. Integrity in documentation is a form of professional honesty: the documenter who oversells the API, who glosses over the limitations, who omits the gotchas, is not merely sloppy — they are dishonest, and their dishonesty will be discovered, usually at the worst possible moment, by the reader who relied on the documentation.

The **ethos of sustainability** demands that documentation be maintainable. Documentation that cannot be kept current — because it is too voluminous, too detached from the code, too dependent on a single person — will become stale, and stale documentation is worse than no documentation (because it misleads). Sustainable documentation is modular (each document has a clear, bounded scope), automated (automated checks catch staleness), integrated (documentation changes are part of the code change workflow), and distributed (no single person is the bottleneck for documentation updates). The docs-as-code movement, discussed in Lecture 8, is fundamentally a movement for documentation sustainability.

The **ethos of the long now** — a phrase borrowed from the Long Now Foundation, which builds clocks designed to run for ten thousand years — demands that documentation be written for readers who are not yet born. The code we write today may outlast us. The systems we build — operating systems, network protocols, data formats — shape the infrastructure on which future generations will build. The documentation we write is the archaeological record of our intention: it tells the future why we made the choices we made, what we were trying to achieve, what we knew and what we didn't. The commit message is a primary source for the historian of software. The design document is a witness to the reasoning of an engineering culture. The documentation ethos, in its fullest expression, is the recognition that we are writing for the long now — and that our words may be read, and relied upon, long after we are gone.

The Norse skalds understood this. They composed poetry designed to be memorised and transmitted across generations — a technology of permanence. The rune-stones were carved with the knowledge that they would stand in the landscape for millennia, communicating with people who did not speak the carver's language but who could recognise the intent: "This place is ours. This person was here. This agreement was made." The software documenter of 2040, writing a README or a design doc or an API reference, is engaged in the same act: carving intention into a medium that will — we hope — endure.

**Required Reading:**
- Stewart Brand, *The Clock of the Long Now: Time and Responsibility* (1999/2040)
- Brian W. Kernighan, *UNIX: A History and a Memoir* (2019/2039), chs. on the culture of documentation at Bell Labs
- Matthew McCullough & Tim Berglund, *Building and Testing with Gradle* (2011), foreword on the importance of documentation culture
- The Long Now Foundation, *Principles for Civilisation* (ongoing)
- The Poetic Edda — reflecting on the permanence of the spoken and inscribed word

**Discussion Questions:**
1. Stale documentation is worse than no documentation — it actively misleads. Yet most projects have stale documentation. Is this an unavoidable consequence of limited resources, or is it a failure of engineering culture?
2. If your documentation were read by a programmer 500 years from now, what would you want them to know about your code, your system, and your intentions? What would you write differently?
3. The Norse skalds composed poetry designed to survive oral transmission across centuries. What are the equivalent "technologies of permanence" for software documentation — and are we using them?

---

## Final Examination Preparation

The final examination for CS108 consists of two components: a **documentation portfolio** (60% of the final grade) and a **written examination** (40%). The portfolio is assembled over the course of the semester and includes: (1) a complete API documentation suite (reference + conceptual guide + tutorial) for a small open-source library; (2) two design documents or ADRs for significant architectural decisions in a team project; (3) a runbook entry for a common production incident; and (4) a set of five commit messages and a code review demonstrating best practices. The written examination requires you to answer four questions from a choice of eight, each testing your ability to diagnose and improve documentation — rewriting a passage for clarity, identifying audience misalignment, critiquing a design document, or designing a documentation strategy for a given scenario.

### Sample Examination Questions

1. **(Audience Analysis)** You are the technical writer for a database startup. You need to document a new query language. Identify at least three distinct audiences, describe their needs and prior knowledge, and propose a documentation structure that serves all three without compromising clarity for any.

2. **(API Documentation Critique)** Below is an API reference entry for a fictional payment processing endpoint. Identify at least five specific problems with the documentation — missing elements, ambiguities, poor phrasing — and rewrite the entry to meet the standards taught in this course.

3. **(Design Document Evaluation)** You are reviewing a design document that proposes migrating a monolithic application to microservices. The document describes the proposed architecture in detail but does not include an "alternatives considered" section. Write a code review comment (300–500 words) explaining why this omission matters and what specific alternatives the author should address.

4. **(Error Message Redesign)** A compiler produces the following error: `Error: Type mismatch at line 47. Expected 'Int' but found 'String'.` Redesign this error message to be more helpful to a novice programmer, explaining what a type mismatch is, why it might have occurred, and how to fix it. Then, write a version of the same error message for an experienced developer, optimising for speed of diagnosis.

5. **(Runbook Construction)** You are the on-call engineer for a web application. The alert `HighLatencyP95 > 500ms` has fired. Write a runbook entry that an operator unfamiliar with the system could follow: include diagnostic steps (with commands), potential causes, remediation steps, and escalation instructions.

6. **(Commit Message Practice)** Below is a set of changes (a diff) that refactors a caching layer. Write a commit message — subject line and body — that follows the conventions taught in this course. Then, explain *why* each element of your message is structured the way it is.

7. **(Documentation Strategy)** You join a startup that has no documentation — no README, no API docs, no runbooks, nothing. The team of five engineers is sceptical about the value of documentation ("we move fast, docs slow us down"). Propose a strategy for introducing documentation gradually, with minimal friction, that demonstrates value at each step. Address: what to document first, what tools to use, how to integrate documentation into the development workflow, and how to measure success.

8. **(Philosophy of Documentation)** In his 1984 essay "Literate Programming," Donald Knuth wrote: "Let us change our traditional attitude to the construction of programs: Instead of imagining that our main task is to instruct a computer what to do, let us concentrate rather on explaining to human beings what we want a computer to do." Discuss this statement in light of the course's themes. Is literate programming the ideal toward which all documentation should aspire — or is it a specific technique suited to specific contexts? What would a "literate" approach to documentation look like in the domain of AI system design, or API development, or incident response?

---

## Course Summary and Learning Outcomes

By the end of CS108, students will be able to:
1. Analyse a documentation audience — novice user, experienced developer, operator, auditor — and tailor content, tone, and structure to that audience
2. Write clear, precise, well-structured API documentation — including signatures, parameter descriptions, return values, error conditions, and tested examples
3. Construct design documents and architecture decision records (ADRs) that capture technical decisions with their context, alternatives, rationale, and consequences
4. Produce user-facing documentation — tutorials, error messages, in-app help — that respects the reader's intelligence and reduces frustration
5. Write effective commit messages, code review comments, and pull request descriptions
6. Apply docs-as-code practices: version-controlled documentation, CI/CD for documentation builds, automated quality checks, and collaborative review
7. Critically evaluate AI-generated documentation: identify errors, omissions, and hallucinations, and add the human context that AI cannot provide
8. Articulate and practice the documentation ethos: integrity (truthfulness), sustainability (maintainability), and responsibility to the long-term community of practitioners

The course serves as a communication foundation for every subsequent course in the Computer Science programme — particularly CS201 (where students write design documents for data structure implementations), CS301 (where machine learning experiments must be documented for reproducibility), and the capstone CS407/CS408 sequence (where the thesis and project documentation are the primary deliverables). Technical communication is not a soft skill; it is the hard skill of making technical work legible, durable, and useful — and it is the skill that distinguishes the engineer who merely builds from the engineer who leads.
