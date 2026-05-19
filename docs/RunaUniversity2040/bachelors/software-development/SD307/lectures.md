# SD307: Open Source Contribution Practicum
## Bachelor of Science in Software Development — University of Yggdrasil, 2040

**Credits:** 4
**Semester:** Year 3, Semester 2
**Prerequisites:** SD205 (DevOps & Continuous Delivery), SD207 (Software Maintenance & Evolution)
**Instructor:** Dr. Þórhildr Vébjörnsdóttir, Faculty of Computational Arts

> *"The smith who shares their tools forges a stronger community than the smith who hoards them. Open source is the modern longship — built by many hands, sailing for all shores."* — Þórhildr Vébjörnsdóttir, *The Forge Assembled* (2039)

---

## Course Description

Open Source Contribution Practicum is the course where students stop writing code in isolation and start writing code in the world. This is not a course about open source theory — it is a course about open source practice. Students will identify, contribute to, and maintain open source projects across a full semester, navigating the social, technical, and legal complexities of collaborative software development at global scale.

The course is organized around the metaphor of the thing — the Norse assembly where free people gathered to make law, settle disputes, and build community. An open source project is a digital thing: a gathering of contributors who negotiate architecture, review code, resolve conflicts, and build something together that no one person could build alone. Like the thing, open source projects have norms, power structures, and governance. Like the thing, they work best when participants understand the customs and contribute constructively.

Students will make at least four substantive contributions to open source projects during the semester: one bug fix, one feature implementation, one documentation improvement, and one contribution of their choice. They will write pull requests, respond to code reviews, participate in issue discussions, and maintain a contribution log. The course culminates in a "thing presentation" where each student presents their contributions, the challenges they faced, and what they learned about collaborative software development.

The 2040 open source landscape is more complex than ever: AI-assisted coding tools generate millions of pull requests, license compliance is a legal minefield, security vulnerabilities in dependencies are a constant threat, and the sustainability of open source projects is an ongoing crisis. This course prepares students to navigate this landscape with skill, ethics, and creativity.

---

## Lectures

### ᚠ Lecture 1: The Digital Thing — Open Source History, Philosophy, and Ecology

**Date:** Week 1, Session 1

#### Overview

Before contributing to open source, students must understand what open source is, where it came from, and why it matters. This lecture covers the history of free and open source software, the philosophical distinctions between "free software" and "open source," the anatomy of an open source project, and the ecological dynamics that sustain (or destroy) open source communities.

#### Lecture Notes

**From Sharing to Stallman: The Prehistory of Open Source.** The practice of sharing source code predates the term "open source" by decades. In the 1950s and 1960s, software was typically distributed with its source code — it was a service, not a product. IBM's mainframe software came with complete source code, and the SHARE user group (founded 1955) distributed software modifications freely among its members. This was not idealism; it was pragmatism. Software was useless without the ability to modify it for your specific hardware and requirements.

The commercialization of software in the 1970s changed this. IBM's unbundling of software from hardware (1969) and the rise of proprietary software companies (Microsoft, Oracle, SAP) created a market where source code was a trade secret. By the early 1980s, most commercial software was distributed as object code only, with explicit license terms prohibiting reverse engineering, modification, and redistribution.

Richard Stallman's response was the Free Software Movement, launched in 1983 with the GNU Project and formalized in 1985 with the founding of the Free Software Foundation (FSF). Stallman's philosophy was explicitly ethical: software should be free (as in freedom) because restricting users' freedom to study, modify, and share software is morally wrong. The GNU General Public License (GPL), first published in 1989, embodied this philosophy by requiring that all derivative works also be distributed under the GPL — the "copyleft" principle.

**The Pragmatic Turn: Open Source.** In 1998, a group of developers including Eric Raymond, Bruce Perens, and Tim O'Reilly coined the term "open source" at a strategy session in Palo Alto. Their motivation was pragmatic, not ethical. They believed that Stallman's moral rhetoric was alienating businesses and that the practical benefits of open source (better quality, faster development, lower cost) were more persuasive than philosophical arguments about freedom.

The Open Source Initiative (OSI) was founded to codify the "Open Source Definition" — a set of criteria that a license must meet to be considered open source. The key criteria:

1. **Free redistribution** — The license must not restrict anyone from selling or giving away the software.
2. **Source code** — The program must include source code, or allow source code to be easily obtained.
3. **Derived works** — The license must allow modifications and derived works.
4. **Integrity of the author's source code** — The license may require modified versions to be distributed under a different name or version number (to protect the original author's reputation).
5. **No discrimination against persons or groups.**
6. **No discrimination against fields of endeavor.**
7. **Distribution of license** — The rights attached to the program must apply to all without additional licenses.
8. **License must not be specific to a product.**
9. **License must not restrict other software.**
10. **License must be technology-neutral.**

**The Anatomy of an Open Source Project.** Every open source project has an ecosystem of artifacts, people, and processes. Understanding this anatomy is the first step to effective contribution:

| Component | Description | Example |
|-----------|-------------|---------|
| **Repository** | The code storage (usually Git) | github.com/torvalds/linux |
| **README** | The project's front door | What the project does, how to install it |
| **CONTRIBUTING.md** | How to contribute | Coding standards, PR process, CLA requirements |
| **CODE_OF_CONDUCT.md** | Community behavior norms | Contributor Covenant, NCoC |
| **LICENSE** | The legal terms | MIT, Apache-2.0, GPL-3.0 |
| **Issue tracker** | Bug reports, feature requests | GitHub Issues, GitLab Issues |
| **CI/CD pipeline** | Automated testing and deployment | GitHub Actions, GitLab CI |
| **Communication channels** | Where contributors discuss | Discord, Slack, mailing list, forum |
| **Governance** | Who makes decisions | BDFL, meritocracy, foundation, corporate |
| **Maintainers** | People with merge authority | Listed in CODEOWNERS or MAINTAINERS |

Projects without clear documentation (no README, no CONTRIBUTING.md, no issue templates) are difficult to contribute to. The best-maintained projects have all of these components and make them easy to find.

**The Ecology of Open Source.** Open source projects exist within an ecosystem of dependencies, contributors, and funding. Understanding this ecology reveals the dynamics that make open source vibrant and fragile:

- **Dependency chains** — A typical 2040 software project depends on 500-2000 open source packages, which themselves depend on 10,000-50,000 transitive dependencies. The 2021 Log4Shell vulnerability (CVE-2021-44228) demonstrated the systemic risk: a single vulnerability in a widely-used logging library affected millions of applications.
- **The maintainer burden** — Most open source projects are maintained by 1-3 people, often unpaid. The maintainer must review pull requests, triage issues, fix bugs, release new versions, and answer community questions — all while working a full-time job. Burnout is endemic.
- **The free-rider problem** — 99% of open source users never contribute. Corporations build billion-dollar products on open source foundations while the maintainers struggle to pay for hosting. The 2021 Svelte incident, where a single maintainer of a popular framework was working 60-hour weeks while corporations built products on their code, crystallized the sustainability crisis.
- **Corporate open source** — Companies like Google, Microsoft, Meta, and Amazon open-source strategic software (Kubernetes, VS Code, React, OpenSearch) to encourage ecosystem growth and commoditize their competitors. This is beneficial for the community but serves corporate interests first.

**The 2040 Landscape: AI-Assisted Contribution and the New Challenges.** In 2040, the open source landscape has been transformed by AI-assisted coding tools. GitHub Copilot, Cursor, and similar AI assistants can generate pull requests that are syntactically correct but may not understand the project's architectural vision. This has created several new challenges:

- **AI-generated contributions** — Projects are receiving large volumes of AI-generated pull requests that are superficially correct but miss the maintainers' intent. Maintainers must review these carefully, spending time that could be spent on substantive improvements.
- **Contributor identity** — When AI writes the code, who is the contributor? The person who prompted the AI? The AI model? The organization that trained the AI? Legal frameworks are still evolving.
- **Quality at scale** — AI tools make it easy to submit thousands of pull requests for minor improvements (typo fixes, linting changes). This overwhelms project maintainers and adds noise to the review process.
- **The premium on deep understanding** — In a world where AI can generate superficial contributions, the value of deep, thoughtful contributions has increased. Maintainers prize contributors who understand the project's architecture, history, and community norms.

#### Required Reading

- Raymond, E. S. (1999). *The Cathedral and the Bazaar: Musings on Linux and Open Source by an Accidental Revolutionary*. O'Reilly. Chapters 1-4.
- Þórhildr Vébjörnsdóttir, (2039). *The Forge Assembled: Open Source Governance in the Age of AI*. University of Yggdrasil Press. Chapters 1-2.
- Eghbal, N. (2020). *Working in Public: The Making and Maintenance of Open Source Software*. Stripe Press. Chapters 1-3.
- Open Source Initiative (2040). *The Open Source Definition*. https://opensource.org/osd

#### Discussion Questions

1. Stallman argues that software should be "free as in freedom" — that restricting users' ability to study, modify, and share software is morally wrong. The open source movement takes a pragmatic approach: open source produces better software. Are these positions compatible? Can you believe both, or are they fundamentally different philosophies?
2. The 2021 Log4Shell vulnerability demonstrated the systemic risk of dependency chains — a single vulnerability in a widely-used library affected millions of applications. Who bears responsibility for this: the library maintainer (who works for free), the downstream developers (who didn't audit their dependencies), or the corporations (who built products on free software without contributing back)?
3. AI-generated pull requests are overwhelming open source maintainers. Should projects adopt policies requiring contributors to disclose AI assistance? Should projects reject AI-generated contributions entirely? What are the implications for open source's collaborative ethos?

---

### ᚢ Lecture 2: The Law of the Thing — Licenses, CLAs, and Legal Frameworks

**Date:** Week 1, Session 2

#### Overview

Open source is defined by its licenses, not by its code. This lecture covers the major open source licenses (MIT, Apache-2.0, GPL-2.0, GPL-3.0, AGPL-3.0, MPL-2.0, LGPL-2.1), the legal implications of each, Contributor License Agreements (CLAs), and the emerging legal issues of AI-generated code. Understanding the law of the thing is essential before contributing — the wrong license choice can destroy a project or expose a contributor to legal risk.

#### Lecture Notes

**The License Spectrum: From Permissive to Copyleft.** Open source licenses exist on a spectrum from permissive (minimal restrictions on downstream use) to copyleft (strong requirements to share source code):

| License | Type | Copyleft? | Patent Grant? | Compatibility | Popularity (2040) |
|---------|------|-----------|---------------|---------------|-------------------|
| MIT | Permissive | No | No | Universal | ~25% |
| Apache-2.0 | Permissive | No | Yes | Universal (except GPLv2) | ~20% |
| BSD-3-Clause | Permissive | No | No | Universal | ~5% |
| MPL-2.0 | Weak copyleft | File-level | Yes | Broad | ~3% |
| LGPL-2.1 | Weak copyleft | Library-level | No | Broad | ~4% |
| GPL-2.0 | Strong copyleft | Yes | No | GPLv2-compatible only | ~5% |
| GPL-3.0 | Strong copyleft | Yes | Yes | GPLv3-compatible | ~15% |
| AGPL-3.0 | Strong copyleft | Yes (network) | Yes | AGPL-compatible only | ~3% |

The key distinction is **copyleft** — the requirement that derivative works be distributed under the same license. MIT and Apache-2.0 impose no such requirement: you can take MIT-licensed code, incorporate it into a proprietary product, and distribute only the object code. GPL-3.0 requires that any derivative work be distributed under GPL-3.0, which means distributing the source code.

**Permissive Licenses: MIT and Apache-2.0.** The MIT license is the most popular open source license because it is the shortest and simplest:

```
MIT License

Copyright (c) [year] [fullname]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software...
```

The MIT license grants unlimited permission to use, modify, and distribute the software, with only two restrictions: (1) include the copyright notice, and (2) the software is provided "as is" with no warranty.

Apache-2.0 adds two important provisions beyond MIT: (1) an explicit patent grant (if the licensor holds patents that the software infringes, they grant a license to use those patents), and (2) a requirement to state changes made to the original software. These provisions make Apache-2.0 a better choice for corporate projects because they provide clearer legal protection.

**Copyleft Licenses: GPL and AGPL.** The GNU General Public License (GPL) is the most widely used copyleft license. Its key provisions:

- **Section 2** — You may modify the software and distribute your modifications, but only under the GPL.
- **Section 3** — When you distribute the software (or a derivative work), you must also distribute the complete corresponding source code, or a written offer to provide it.
- **Section 6** — You may not impose any further restrictions on the recipients' exercise of the rights granted by the GPL.

The "viral" nature of the GPL — the requirement that derivative works also be GPL-licensed — is its most controversial feature. Companies that use GPL-licensed code in their proprietary products must either release their product under the GPL or stop using the code. This has led to a vast ecosystem of GPL-compliant alternatives and GPL-incompatible licenses.

The Affero General Public License (AGPL-3.0) extends the GPL's copyleft requirement to network use. Under the GPL, you can use GPL-licensed code on a server without distributing the source code (because you're not "distributing" the software — you're providing a network service). The AGPL closes this "SaaS loophole" by requiring that anyone who interacts with the software over a network must also receive the source code. This makes AGPL the preferred license for projects that want to prevent cloud providers from offering their software as a service without contributing back.

**Weak Copyleft: MPL-2.0 and LGPL-2.1.** Weak copyleft licenses occupy a middle ground: they require sharing modifications to the licensed files (MPL) or the library (LGPL), but they allow linking the licensed code with proprietary code in a larger work. This makes them suitable for libraries that want to ensure improvements are shared back while allowing proprietary applications to use the library.

**Contributor License Agreements (CLAs).** Many open source projects require contributors to sign a Contributor License Agreement before their pull requests are accepted. A CLA is a legal agreement between the contributor and the project that defines the terms under which the contributor's code is licensed to the project.

There are two types of CLAs:

1. **Inbound CLA** — The contributor grants the project a license to use their contribution. This may be an exclusive license (the project is the only entity that can distribute the code) or a non-exclusive license (the contributor retains the right to use their own code elsewhere). Most projects use a non-exclusive inbound CLA.
2. **Outbound CLA** — The contributor assigns copyright to the project. This gives the project the right to re-license the code in the future. Some projects (like the Free Software Foundation) require copyright assignment to simplify enforcement of the GPL.

CLAs are controversial in the open source community. Proponents argue that CLAs protect the project by ensuring that all contributions are properly licensed. Opponents argue that CLAs give the project operator (often a corporation) the right to re-license contributions under a non-open license, effectively appropriating community contributions for proprietary use.

The 2040 best practice, endorsed by the University of Yggdrasil's Open Source Governance Lab, is the **Developer Certificate of Origin (DCO)** model: instead of signing a CLA, contributors add a `Signed-off-by:` line to each commit, certifying that they have the right to submit the code under the project's license. This is simpler than a CLA, preserves contributors' copyright, and provides legal clarity without the overhead of a full legal agreement.

**The Emerging Law of AI-Generated Code.** In 2040, the legal status of AI-generated code is still evolving. Key questions:

- **Copyrightability** — Can AI-generated code be copyrighted? The US Copyright Office has consistently held that only works created by humans can be copyrighted. If an AI generates code based on a prompt, the human who wrote the prompt may not have a copyright claim on the generated code.
- **License compliance** — If an AI model was trained on GPL-licensed code, does the output infringe the GPL? This is an active area of litigation. If the AI produces code that is substantially similar to training data, the license of the training data may apply.
- **Contributor liability** — If a contributor submits AI-generated code to an open source project, and the code infringes a copyright or patent, who is liable? The contributor? The AI vendor? The project maintainers? Current law provides no clear answer.
- **Disclosure requirements** — Should contributors be required to disclose that their code was AI-generated? The Open Source Initiative's 2039 position paper recommends voluntary disclosure but stops short of requiring it.

The University of Yggdrasil's Open Source Governance Lab has published guidelines for contributing AI-assisted code: (1) disclose AI assistance in the pull request description, (2) verify that the generated code does not reproduce training data verbatim, (3) understand and test the generated code before submitting, and (4) be prepared to defend the contribution on its technical merits, not just the AI's authority.

#### Required Reading

- Þórhildr Vébjörnsdóttir, (2039). *The Forge Assembled*. Chapter 3: "The Law of the Thing: Licenses, CLAs, and Legal Frameworks."
- Meeker, D. J. (2020). *Open (Source) for Business: A Practical Guide to Open Source Software Licensing* (3rd ed.). [A comprehensive reference on open source licensing.]
- Developer Certificate of Origin (2040). https://developercertificate.org/
- University of Yggdrasil Open Source Governance Lab (2040). *Guidelines for AI-Assisted Contributions*. Technical Report UoY-OSGL-2040-01.

#### Discussion Questions

1. A startup wants to use an AGPL-3.0-licensed library in their proprietary web application. The AGPL requires them to release their entire application's source code to anyone who interacts with the application over a network. Is this a reasonable requirement, or does it unfairly restrict commercial use? What should the startup do?
2. A contributor submits a pull request to your project that includes code generated by an AI assistant. The AI was trained on a mix of MIT, Apache-2.0, and GPL-licensed code. The contributor has not disclosed the AI assistance. What should you do as a maintainer? What are the legal risks?
3. The Linux kernel requires a Developer Certificate of Origin (DCO) but does not require a CLA. The Free Software Foundation requires copyright assignment (a type of CLA). What are the advantages and disadvantages of each approach? Under which circumstances would you recommend one over the other?

---

### ᚦ Lecture 3: Reading the Runes — Understanding an Unfamiliar Codebase

**Date:** Week 2, Session 1

#### Overview

Before you can contribute to an open source project, you must understand it. But most open source projects have tens of thousands to millions of lines of code, written by hundreds of contributors over many years, with minimal documentation. This lecture covers strategies for reading and understanding an unfamiliar codebase: the architecture-first approach, the test-driven reading approach, the commit history approach, and the use of AI-assisted code understanding tools.

#### Lecture Notes

**The Architecture-First Approach.** When approaching a new codebase, most developers instinctively start reading code from the entry point (typically `main()` or `index.js`). This is the wrong approach. The entry point tells you what the program does first, not what it does most importantly. Instead, start with the architecture:

1. **Read the documentation first** — README, CONTRIBUTING.md, architecture docs, design docs. If the project has an ARCHITECTURE.md or ADR (Architecture Decision Record) directory, read those. They contain the decisions that shaped the codebase — and understanding the decisions helps you understand the code.
2. **Identify the module boundaries** — Most projects are organized into modules or packages. List the top-level directories and their purposes. For each module, read its README or header file to understand its responsibility.
3. **Trace the data flow** — Identify the primary data structures and follow how data enters the system, is transformed, and exits the system. This is usually more informative than tracing the control flow.
4. **Map the dependency graph** — Which modules depend on which? Which modules are core (depended upon by many) and which are peripheral (depended upon by few)? The core modules are the ones you need to understand most deeply.

Practical exercise: Choose an unfamiliar open source project (suggestions: Redis, Django, Zig compiler, RúnarRT). Spend 30 minutes reading its high-level documentation and listing its modules. Then draw a rough dependency graph. You will have a surprisingly good mental model of the project's architecture — without having read a single line of implementation code.

**The Test-Driven Reading Approach.** Tests are the best documentation of a codebase's intended behavior. A well-written test tells you what the code is supposed to do, what inputs it accepts, what outputs it produces, and what edge cases it handles. To read a codebase through its tests:

1. **Find the test directory** — Usually `tests/`, `test/`, `spec/`, or `__tests__/`. Read the test file names to understand the major features and edge cases.
2. **Read the test for the feature you want to modify** — This tells you exactly what the feature does (or is supposed to do) before you try to change it.
3. **Run the tests before making changes** — This verifies that your environment is set up correctly and establishes a baseline of passing tests.
4. **Write a failing test for your change before implementing** — This is test-driven development (TDD), and it's the safest way to contribute to an unfamiliar codebase. If your test fails for the right reason, you understand the code well enough to make your change.

The student who tries to fix a bug by reading the implementation code first is the student who spends three hours understanding the code only to discover that the bug is in an interaction between two modules they haven't read yet. The student who reads the test for the bug first is the student who understands the expected behavior in ten minutes and can focus their investigation on the code that violates the expectation.

**The Commit History Approach.** Git is a time machine. Every commit is a snapshot of the project at a specific moment, with a message explaining what changed and why. The commit history tells the story of the project — what problems arose, how they were solved, and who solved them:

- `git log --oneline --graph` — See the project's branch structure and merge history.
- `git log --author="username"` — See all commits by a specific contributor. This helps you understand who is responsible for which parts of the codebase.
- `git log -S "function_name" -- source_file` — Find all commits that added or removed a specific function. This is invaluable for understanding why a function exists.
- `git blame source_file` — See who last modified each line. This helps you identify the current expert on a particular piece of code.
- `git log -p -- path/to/file` — See every change to a specific file, with full diffs. This is the history of the file, told by the people who wrote it.

The commit history is particularly useful for understanding architectural decisions. When you encounter a design choice that seems odd, `git log -S "odd_choice" -- .` will often reveal the commit that introduced it, with a commit message explaining *why*. The reason is usually either a constraint you don't know about (backward compatibility, performance requirement, platform limitation) or a historical accident that no one has gotten around to fixing.

**AI-Assisted Code Understanding: The 2040 Landscape.** In 2040, AI-assisted code understanding tools have become essential for navigating large codebases. The University's RúnarCode platform provides:

- **Architecture extraction** — Automatically generates module dependency graphs, data flow diagrams, and call graphs from source code. The output is a structured representation of the codebase's architecture that can be queried and explored interactively.
- **Natural language codebase search** — Ask questions like "where does the authentication logic handle expired tokens?" and get code snippets with context. This is far more effective than grep for understanding unfamiliar code.
- **Behavioral summarization** — For each function, generates a natural language description of its behavior, including inputs, outputs, side effects, and error conditions. This is like documentation, but generated from the code itself and always up to date.
- **Commit narrative generation** — Summarizes a series of commits as a narrative, identifying themes, key decisions, and contributors. This makes it possible to understand months of project history in minutes.

These tools are powerful, but they have limitations:

- **Hallucination** — AI-generated summaries may describe behavior that doesn't exist or misattribute responsibilities. Always verify AI-generated understanding against the actual code.
- **Context window limitations** — Large codebases exceed the context window of even the most capable AI assistants. Architecture extraction works well; detailed code understanding requires targeted queries.
- **Bias toward recent code** — AI tools are trained to understand current code, not historical code. They may not understand deprecated patterns or the reasons for legacy design decisions.
- **Over-reliance** — The biggest risk is that developers trust AI summaries without verifying them. This leads to misunderstandings that are more insidious than ignorance, because the developer *thinks* they understand the code when they don't.

The best practice for 2040 is to use AI tools as a **reading accelerator**, not a reading replacement. Use them to quickly map the architecture and find relevant code, then read the actual code to verify your understanding before making changes.

#### Required Reading

- Þórhildr Vébjörnsdóttir, (2039). *The Forge Assembled*. Chapter 4: "Reading the Runes: Understanding an Unfamiliar Codebase."
- Forsgren, N., Storey, M.-A., Maddila, C., et al. (2023). *Measuring Developer Experience at Microsoft.* IEEE Software.
- UoY Open Source Governance Lab (2040). *RúnarCode: AI-Assisted Code Understanding Tool*. Internal documentation.
- Boulton, C. (2038). "AI-Assisted Code Review: Promises, Pitfalls, and Best Practices." *Communications of the ACM*, 61(9), 28-35.

#### Discussion Questions

1. You're trying to contribute to a project with no documentation, no architecture docs, and no ADR directory. The code is 500,000 lines of C++. How do you build a mental model of the project? Which approach (architecture-first, test-driven, commit history, AI-assisted) would you prioritize, and why?
2. The test-driven reading approach assumes that the tests are accurate representations of the intended behavior. But in many projects, tests are incomplete, outdated, or even incorrect. How do you verify that the tests match the intended behavior when the documentation is also unreliable?
3. AI-assisted code understanding tools can generate natural language descriptions of code behavior. But these descriptions may hallucinate — describing behavior that doesn't exist. How should a developer balance the efficiency of AI summaries against the risk of misunderstanding?

---

### ᚨ Lecture 4: The Well-Made Pull Request — Code Contribution Best Practices

**Date:** Week 2, Session 2

#### Overview

The pull request (or merge request, in GitLab terminology) is the fundamental unit of open source contribution. A well-made pull request is a gift to the project — clear, focused, well-documented, and easy to review. A poorly-made pull request is a burden — sprawling, unfocused, undocumented, and difficult to review. This lecture covers the art of making pull requests that maintainers want to merge: choosing the right scope, writing clear commit messages, responding to review feedback, and handling the social dynamics of code review.

#### Lecture Notes

**Scope: Small Is Beautiful.** The single most important characteristic of a good pull request is small scope. A pull request that touches 10-50 lines across 2-5 files is easy to review. A pull request that touches 1,000 lines across 30 files is nearly impossible to review thoroughly, no matter how well-written.

The Linux kernel development community has a saying: "Each commit should do one thing." The same applies to pull requests. Each PR should address one issue, implement one feature, or fix one bug. If you're fixing a typo and refactoring a function, make two PRs. If you're adding a feature and cleaning up nearby code, make two PRs. Reviewers cannot effectively evaluate a PR that mixes concerns.

Practical guidelines for scope:

- **One logical change per PR** — A typo fix, a bug fix, a feature addition, and a refactor are four PRs, not one.
- **10-50 lines of changed code** — This is the sweet spot. Below 10 lines, it's probably too trivial for a PR (but it's still a valid PR!). Above 50 lines, consider splitting the PR into multiple smaller PRs.
- **Explain the "why," not the "what"** — The code shows *what* changed. The PR description should explain *why* it changed. What issue does it fix? What problem does it solve? What design constraint does it satisfy?
- **Include tests** — Every PR that changes behavior should include tests that verify the change. A PR without tests is a PR that asks reviewers to trust the contributor instead of verifying the change.

**Commit Messages: The Narrative of Change.** A commit message is a letter to the future. Six months from now, someone will run `git blame` on your code and read your commit message to understand why the code is the way it is. Write for that person.

The conventional commit message format (used by most large open source projects):

```
<type>(<scope>): <subject>

<body>

<footer>
```

Where:
- **type** — feat, fix, docs, style, refactor, perf, test, build, ci, chore
- **scope** — The module or component affected (optional)
- **subject** — A concise description of the change (imperative mood: "add feature" not "added feature")
- **body** — A detailed description of *why* the change was made, including context and alternatives considered
- **footer** — Related issues, breaking changes, etc.

Example:
```
fix(auth): handle expired tokens in refresh flow

When a user's access token expires, the refresh token handler
was not checking for null before attempting to parse the token
payload. This caused a NullPointerException in production when
the auth server returned an empty refresh token response.

The fix adds a null check before parsing and returns a clear
error message when the refresh token is missing.

Fixes #1234
```

This commit message tells the reviewer: (1) what the fix does, (2) why it's needed, (3) what the root cause was, and (4) which issue it resolves. A commit message like "fix bug" or "update auth" tells the reviewer nothing.

**Responding to Review Feedback: The Art of Constructive Dialogue.** Code review is a conversation, not a verdict. When a maintainer requests changes to your PR, they are not rejecting your contribution — they are improving it. The best contributors treat review feedback as a gift:

1. **Read the feedback carefully** — Before responding, read each comment twice. Make sure you understand the reviewer's concern. If you don't understand, ask for clarification.
2. **Respond to every comment** — Even if you don't agree with the feedback, acknowledge it. "I hear your concern about X. Here's why I chose Y instead: [reasoning]. What do you think?"
3. **Don't take it personally** — The reviewer is critiquing the code, not the person. Most maintainers are grateful for contributions and want to help you succeed.
4. **Push changes promptly** — After addressing feedback, push the changes within 24-48 hours. Delays signal disinterest and make it harder for the reviewer to remember the context.
5. **Know when to push back** — If you disagree with a review comment, explain your reasoning clearly and respectfully. Maintainers respect contributors who can defend their decisions with good arguments. But if the maintainer insists, accept their decision — it's their project.

**The Social Dynamics of Code Review.** Code review is not just a technical process — it is a social process embedded in power dynamics, cultural norms, and personal relationships. Understanding these dynamics is essential for effective contribution:

- **Newcomer anxiety** — First-time contributors often feel intimidated by the review process. They may perceive critical feedback as personal rejection. Projects can mitigate this by using welcoming language, providing mentorship programs, and labeling first-time contributor issues.
- **Maintainer burnout** — Maintainers review PRs on top of their regular work. A maintainer who is reviewing 20 PRs a week may not have the bandwidth to provide detailed feedback on a 500-line PR. This is one reason why small PRs are better — they reduce the review burden.
- **Cultural differences** — Code review norms vary across cultures and projects. Some projects are blunt and direct (the Linux kernel is famously harsh in its review feedback). Others are gentle and supportive (the Rust project has a detailed code of conduct that emphasizes respect and inclusion). Before contributing, read the project's code of conduct and contributing guide to understand its norms.
- **Power imbalances** — The maintainer has merge authority. The contributor does not. This is by design (the maintainer is responsible for the project's quality), but it can create a power imbalance where the contributor's voice is less valued. Good maintainers mitigate this by explaining their decisions, being open to discussion, and acknowledging good contributions publicly.

#### Required Reading

- Þórhildr Vébjörnsdóttir, (2039). *The Forge Assembled*. Chapter 5: "The Well-Made Pull Request."
- Submitting Patches to the Linux Kernel. https://www.kernel.org/doc/html/latest/process/submitting-patches.html [The gold standard for commit message format and contribution process.]
- Google Engineering Practices Documentation (2040). *Code Review Developer Guide*. https://google.github.io/eng-practices/review/
- Dagenais, B., & Robillard, M. P. (2018). "Creating and Evolving Developer Documentation." *ICSE 2018*.

#### Discussion Questions

1. A maintainer asks you to refactor your entire PR because they prefer a different architectural approach. Your approach works and is well-tested, but their approach is cleaner. How do you handle this situation? Do you rewrite the PR to match their vision, argue for your approach, or withdraw the PR?
2. You submit a PR that fixes a critical security vulnerability. The maintainer doesn't respond for two weeks. The vulnerability is publicly known. What should you do? What are the ethical considerations of disclosing the vulnerability before the fix is merged?
3. A first-time contributor submits a PR with good code but poor commit messages and no tests. As a maintainer, how do you review this PR in a way that encourages the contributor to continue contributing while maintaining the project's quality standards?

---

### ᚱ Lecture 5: The Web of Trust — Issue Triage, Bug Reports, and Community Participation

**Date:** Week 3, Session 1

#### Overview

The thing was not just a legislative assembly — it was also a court, a market, and a social gathering. Open source contribution is not just writing code — it's also triaging issues, filing bug reports, participating in discussions, and building the web of trust that sustains the community. This lecture covers the non-code aspects of open source contribution that are just as important as the code itself.

#### Lecture Notes

**Issue Triage: The Front Lines of Open Source.** Issue triage is the process of reviewing, categorizing, and prioritizing incoming bug reports and feature requests. It is one of the most valuable contributions a community member can make, because it directly reduces the maintainer's workload and improves the project's responsiveness.

Triage involves:

1. **Reproducing the bug** — Can you reproduce the reported behavior? If not, ask the reporter for more information (operating system, version, steps to reproduce, expected vs. actual behavior).
2. **Categorizing the issue** — Is it a bug, a feature request, a question, or a duplicate? Apply the appropriate labels.
3. **Assessing severity** — Is it a critical security vulnerability, a major functionality break, a minor inconvenience, or a cosmetic issue?
4. **Assigning to the right person** — If you know the codebase, tag the maintainer responsible for the affected module.
5. **Closing invalid issues** — Duplicate reports, unreproducible bugs, and questions that are already answered in the documentation can be closed with a polite explanation and a reference to the relevant information.

Effective triage requires empathy. The person filing the issue is often frustrated — they've encountered a bug that is blocking their work. A triage response that says "works for me, closing" is dismissive and hostile. A response that says "Thank you for the report. I can't reproduce this on my system. Could you share more details about your environment?" is welcoming and constructive.

**Writing Excellent Bug Reports.** A bug report is a story: the protagonist (the user) encounters an obstacle (the bug) and needs a resolution (the fix). Like any good story, a bug report needs a clear beginning, middle, and end:

1. **Title** — A concise summary of the problem. "App crashes on startup" is too vague. "NullPointerException in AuthHandler.refreshToken() when accessToken is null on v2.3.1" is specific and actionable.
2. **Environment** — Operating system, software version, hardware, network conditions. Everything that could affect the bug.
3. **Steps to reproduce** — A numbered list of actions that reliably trigger the bug. "It sometimes crashes" is not reproducible. "1. Open the app, 2. Navigate to Settings, 3. Click 'Clear Cache', 4. App crashes at line 142 of AuthHandler.java" is reproducible.
4. **Expected behavior** — What should happen.
5. **Actual behavior** — What actually happens, including error messages, stack traces, and screen captures.
6. **Workaround** — If you've found a way to avoid the bug, share it. This helps other users and gives the maintainer a clue about the root cause.

The University of Yggdrasil's RúnarBug framework provides a bug report template that enforces these elements. Projects that use RúnarBug report 40% faster resolution times than projects with free-form issue reporting.

**Community Participation: Building the Web of Trust.** Open source projects are communities, and communities run on trust. A contributor who consistently submits high-quality code, responds to reviews promptly, and helps other contributors will find that their PRs are reviewed faster, their issues are triaged sooner, and their opinions carry more weight. This is the "web of trust" — the network of relationships that sustains open source projects.

Practical ways to build trust:

- **Review other people's PRs** — Even if you're not a maintainer, reviewing PRs is valuable. A thorough review that catches bugs, suggests improvements, or asks clarifying questions is a gift to both the contributor and the maintainer.
- **Help in the community forum** — Answer questions, share solutions, and welcome newcomers. The Ubuntu community's motto is "Ubuntu: I am what I am because of who we all are."
- **File well-written bug reports** — Even if you can't fix a bug, a well-written bug report makes it easier for others to fix.
- **Improve documentation** — Documentation improvements are often the easiest way to contribute to a project. If you figured something out by reading the code, write it down so the next person doesn't have to.
- **Be patient and respectful** — Maintainers are often volunteers. It may take days or weeks for them to review your PR. Be patient, be polite, and be constructive.

**The Economics of Open Source: Who Pays?** The open source ecosystem has a fraught relationship with money. Most maintainers are volunteers. Most users are corporations. The economic model is:

- **Corporate sponsorship** — Companies pay developers to work on open source projects that are strategic for their business. Google employs developers to work on Kubernetes, Facebook on React, and Microsoft on VS Code. This funds development but creates power imbalances — corporate priorities may not align with community priorities.
- **Donations and sponsorships** — GitHub Sponsors, Open Collective, and Patreon allow users to donate to maintainers. This provides income but is rarely enough to fund full-time development.
- **Open core** — Companies offer a free open source version and sell proprietary add-ons (enterprise features, support, hosting). GitLab, Grafana, and Elastic use this model.
- **Consulting and training** — Maintainers earn money by consulting on their own projects or offering training courses. This is sustainable but takes time away from development.
- **Foundations** — The Linux Foundation, Apache Foundation, and Cloud Native Computing Foundation provide legal and financial infrastructure for open source projects. They accept donations and distribute grants, but they are not direct funders of development.

The 2040 sustainability challenge is that open source is critical infrastructure that is maintained by a small number of underfunded developers. The University of Yggdrasil's research shows that the top 1% of open source projects (by download count) have corporate backing, while the bottom 99% are maintained by volunteers who are increasingly burned out. New models (government funding, usage-based taxation, insurance-based maintenance pools) are being explored, but no model has yet achieved mainstream adoption.

#### Required Reading

- Þórhildr Vébjörnsdóttir, (2039). *The Forge Assembled*. Chapter 6: "The Web of Trust."
- Eghbal, N. (2020). *Working in Public: The Making and Maintenance of Open Source Software*. Chapters 4-6.
- Mozilla Foundation (2038). *Healthy OSS Communities: A Framework for Assessment*. https://healthy-oss.mozilla.org/
- Steinmacher, I., et al. (2015). "A Systematic Literature Review on the Barriers Faced by Newcomers to Open Source Software Projects." *Information and Software Technology*, 59, 67-85.

#### Discussion Questions

1. You've filed a bug report on a popular open source library. The maintainer responds: "This is the first report of this issue. Can you provide a minimal reproducible example?" You cannot reproduce the bug in isolation — it only occurs in your production environment with specific data. How should you proceed?
2. Some open source projects have a "good first issue" label to help newcomers find easy contributions. Other projects argue that this label creates a "tourist" mentality — contributors make one trivial PR and never return. What are the advantages and disadvantages of "good first issue" labels? Are there better ways to onboard new contributors?
3. A company is using your open source library in their commercial product. They have never contributed code, documentation, or financial support. They file a critical bug report and demand an immediate fix. How should you respond as a maintainer? What are your obligations to users who don't contribute back?

---

### ᚲ Lecture 6: The Weaver's Pattern — Open Source Project Governance

**Date:** Week 3, Session 2

#### Overview

Every open source project has governance, whether it's documented or not. Governance determines who can make decisions, how disputes are resolved, and how the project evolves. This lecture covers the major governance models (BDFL, meritocracy, foundation, corporate, consensus), the role of governance in project health, and the 2040 trend toward more structured governance models.

#### Lecture Notes

**Governance Models.** Open source projects use a variety of governance models, each with its own power structures, decision-making processes, and failure modes:

| Model | Description | Examples | Strengths | Weaknesses |
|-------|-------------|----------|-----------|------------|
| **BDFL** (Benevolent Dictator for Life) | A single person has final say on all decisions | Linux (Linus Torvalds), Python (Guido van Rossum, until 2018) | Fast decisions, clear vision | Bottleneck, succession crisis, abuse of power |
| **Meritocracy** | Decision-making power is earned through contributions | Apache Foundation projects, FreeBSD | Rewards productive contributors, encourages participation | Entrenchment, "merit" defined by incumbents |
| **Foundation** | A non-profit foundation owns the project and provides governance | Kubernetes (CNCF), Node.js (OpenJS Foundation) | Legal protection, neutral governance, funding | Bureaucracy, slow decisions, corporate capture |
| **Corporate** | A single company controls the project | MongoDB (MongoDB Inc.), Android (Google) | Consistent vision, well-funded development | Community has no real power, risk of license change |
| **Consensus** | Decisions are made by consensus among contributors | Debian, NixOS | Inclusive, democratic | Slow, can be blocked by minorities |

**The BDFL Model: Power and Peril.** The BDFL model is the most common governance structure for small and medium-size projects. The founder of the project (or a designated successor) has final decision-making authority. This model works well when:

- The BDFL is technically excellent and makes good decisions
- The BDFL is present and responsive
- The community trusts the BDFL's judgment

The model breaks down when:
- The BDFL becomes unavailable (illness, burnout, death) — this happened with numerous projects where the founder stepped away without a succession plan
- The BDFL makes a decision the community disagrees with — the community can fork the project, but this is costly and divisive
- The BDFL's judgment is flawed — there is no mechanism to override the dictator

Guido van Rossum's resignation as Python's BDFL in 2018 is instructive. He stepped down after a contentious debate about the assignment expression (PEP 572, the "walrus operator" `:=`). The community realized that Python needed a governance model that didn't depend on a single person, and they transitioned to a Steering Council model. The lesson: even BDFLs need a succession plan.

**The Meritocracy Controversy.** The term "meritocracy" in open source has come under increasing scrutiny. The argument for meritocracy is straightforward: people who contribute more should have more influence. This rewards productive contributors and encourages participation.

The argument against meritocracy is that "merit" is defined by the people who already have power, which creates a self-reinforcing cycle. People who have the time, education, and social capital to contribute are disproportionately from privileged backgrounds. Meritocracy, in practice, can reproduce existing social inequalities in the open source world.

In 2040, many projects have moved away from the word "meritocracy" (though not always from the underlying model). The Apache Foundation, which coined the term "Apache Meritocracy," now uses "community-driven development" in its materials. The Rust project uses a "community governance" model that explicitly includes non-technical contributions (documentation, community management, event organization) as pathways to decision-making authority.

**Foundation Governance: The Institutional Approach.** Foundation governance transfers ownership of the project's intellectual property to a non-profit foundation, which provides legal protection, financial infrastructure, and neutral governance. Major foundations in 2040:

- **Linux Foundation** — Hosts Kubernetes, Node.js, Hyperledger, and many other projects. Funded by corporate memberships ($15K-$500K/year).
- **Apache Software Foundation** — One of the oldest open source foundations. Uses a formal meritocratic model with a strict incubation process for new projects.
- **Cloud Native Computing Foundation (CNCF)** — A Linux Foundation subsidiary focused on cloud-native technologies. Graduated projects include Kubernetes, Prometheus, and Envoy.
- **Python Software Foundation** — Manages Python's intellectual property and organizes PyCon. Uses a Steering Council model.
- **Eclipse Foundation** — Focuses on enterprise Java and IoT. Uses a transparent specification process.

Foundation governance provides legal protection (the foundation can enforce the project's license), financial stability (the foundation can accept and distribute donations), and credibility (the foundation's name provides assurance to corporate users). However, foundations can be slow to make decisions, tend to favor corporate interests over individual contributors, and add bureaucracy that small projects don't need.

**The 2040 Governance Landscape.** Several trends in 2040 are reshaping open source governance:

- **AI-assisted governance** — Projects are using AI to triage issues, suggest reviewers, and detect toxic behavior. The University of Yggdrasil's RúnarModerate system analyzes comment sentiment and flags potential conflicts before they escalate.
- **Multi-stakeholder governance** — Projects are increasingly including users, not just developers, in governance decisions. The Rust project's RFC process now includes a "community feedback" phase where users can comment on proposed changes.
- **Sustainability mandates** — Some foundations now require projects to have a sustainability plan (funding, maintainer succession) as a condition of graduation. This is a response to the maintainer burnout crisis.
- **Legal vulnerability insurance** — The Open Source Security Foundation (OpenSSF) provides legal insurance for maintainers who face lawsuits or cease-and-desist orders related to their projects. This is increasingly necessary as open source software becomes critical infrastructure.

#### Required Reading

- Þórhildr Vébjörnsdóttir, (2039). *The Forge Assembled*. Chapter 7: "The Weaver's Pattern: Governance in Open Source."
- Eghbal, N. (2020). *Working in Public*. Chapter 7: "Structures."
- Omidvar, A., & Adams, B. (2022). "Governance in Open Source Software Projects: A Taxonomy and Survey." *ACM Computing Surveys*, 55(3), 1-35.
- Open Source Security Foundation (2040). *Maintainer Legal Protection Program*. https://openssf.org/maintainer-protection/

#### Discussion Questions

1. The BDFL model concentrates decision-making power in one person, which enables fast decisions but creates a single point of failure. What governance structure would you recommend for a new open source project with 5-10 contributors? Consider the tradeoffs between speed, inclusivity, and sustainability.
2. The term "meritocracy" has been criticized for reproducing existing social inequalities under the guise of objectivity. What alternative governance models could provide inclusive decision-making while still rewarding productive contributors? How would you define "merit" in a way that includes non-technical contributions?
3. A large corporation wants to donate a project to a foundation. The corporation will continue to employ 80% of the project's contributors. Does the foundation provide real community governance, or is it a mechanism for the corporation to maintain control while appearing neutral? How should the foundation structure itself to prevent corporate capture?

---

### ᚷ Lecture 7: The Harbor's Security — Dependency Management, Supply Chain, and Security

**Date:** Week 4, Session 1

#### Overview

A harbor that welcomes all ships must also guard against pirates. Open source software depends on a vast supply chain of dependencies, each of which is a potential vector for security vulnerabilities, license violations, and supply chain attacks. This lecture covers dependency management, vulnerability detection, software bill of materials (SBOMs), and the emerging discipline of open source supply chain security.

#### Lecture Notes

**The Dependency Graph: Scale and Risk.** Modern software is built on a mountain of dependencies. A typical Node.js application depends on 500-2000 packages, which transitively depend on 10,000-50,000 packages. A typical Python application depends on 50-200 packages, which transitively depend on 500-5000 packages. Even a "minimal" Rust application depends on 50-100 crates.

The dependency graph creates three classes of risk:

1. **Vulnerability risk** — A vulnerability in any transitive dependency is a vulnerability in your application. The 2021 Log4Shell vulnerability (CVE-2021-44228) affected millions of applications because they depended, often unknowingly, on Apache Log4j.
2. **Availability risk** — If a dependency is removed from its registry (by the author or by legal action), all applications that depend on it break. The 2016 left-pad incident (a 11-line npm package that was unpublished, breaking thousands of projects) demonstrated this risk.
3. **License risk** — If a transitive dependency uses a license that is incompatible with your application's license, you may be in legal violation. A GPL-licensed dependency in a proprietary application is a license violation, even if you didn't know the dependency was there.

**Software Bill of Materials (SBOM).** An SBOM is a formal, machine-readable inventory of all components in a software system, including their versions, licenses, and known vulnerabilities. SBOMs are the foundation of supply chain security:

- **NTIA/SBOM Minimum Elements** (2021) — Author, component name, version, dependency relationship, and other fields.
- **SPDX** (Software Package Data Exchange) — A Linux Foundation standard for SBOM format. Supports JSON, YAML, and RDF.
- **CycloneDX** — An OWASP standard for SBOM format. Lightweight and designed for security use cases.

In 2040, SBOMs are required by US Executive Order 14028 ("Improving the Nation's Cybersecurity") for all software sold to the federal government, and the EU Cyber Resilience Act imposes similar requirements. Major package managers (npm, PyPI, Maven, Cargo) generate SBOMs automatically.

**Vulnerability Detection and Remediation.** The open source security ecosystem in 2040 provides several tools for detecting vulnerabilities in dependencies:

- **OSV (Open Source Vulnerabilities)** — An aggregator that collects vulnerability data from multiple sources (CVE, GitHub Security Advisories, NPM Audit, PyPI Advisory) and provides a unified API.
- **Dependabot / Snyk / Socket** — Automated dependency scanning tools that detect known vulnerabilities in dependencies and generate pull requests to update to fixed versions.
- **Static Application Security Testing (SAST)** — Tools that scan source code for vulnerability patterns (SQL injection, buffer overflow, insecure deserialization). SonarQube, CodeQL, and Semgrep are popular SAST tools in 2040.
- **Software Composition Analysis (SCA)** — Tools that scan binary artifacts (compiled libraries, Docker images) for known vulnerabilities. Snyk, Grype, and Trivy are popular SCA tools.

The remediation lifecycle for a dependency vulnerability:

1. **Detection** — A vulnerability scanner identifies a vulnerability in a dependency.
2. **Assessment** — Is the vulnerability exploitable in your application? (Many vulnerabilities are in code paths that your application doesn't use.)
3. **Prioritization** — How severe is the vulnerability? (CVSS score, exploitability, business impact.)
4. **Remediation** — Update the dependency to a fixed version, or apply a patch, or implement a workaround.
5. **Verification** — Confirm that the fix resolves the vulnerability and doesn't introduce new issues.

**Supply Chain Attacks: The Modern Pirate.** In the 2020-2040 period, supply chain attacks emerged as a major threat. The most notable attacks:

- **SolarWinds (2020)** — Russian intelligence compromised the build system of SolarWinds Orion, inserting a backdoor into the update process. 18,000 organizations were affected, including US government agencies.
- **Codecov (2021)** — Attackers compromised the Codecov bash uploader, exfiltrating CI/CD environment variables from thousands of projects.
- **UA Parser JS (2021)** — The npm package ua-parser-js was hijacked by a malicious maintainer who replaced the legitimate package with one that installed cryptocurrency miners.
- **XZ Utils (2024)** — A multi-year social engineering attack where a contributor named "Jia Tan" gained maintainer access to the xz compression utility and inserted a backdoor in the build process. The backdoor was discovered by a systemd developer who noticed unusual SSH authentication latency.

These attacks demonstrate that supply chain security is not just about vulnerabilities in the code — it's about the integrity of the entire development pipeline, including the people who write and review the code.

**Defending the Supply Chain.** In 2040, the best practices for supply chain defense include:

- **Reproducible builds** — Build the software from source and verify that the binary matches the official release. This ensures that the build process hasn't been tampered with.
- **Signed artifacts** — Use digital signatures (GPG, Sigstore) to verify that the package was published by the expected author.
- **Pinned dependencies** — Specify exact versions (not version ranges) in your dependency declarations. This prevents supply chain attacks that publish malicious versions within an allowed range.
- **Dependency review** — Before adding a new dependency, review its source code, license, maintenance status, and security history. Use automated tools (Socket, Phylum) to check for known issues.
- **Supply chain levels for software artifacts (SLSA)** — A framework for ensuring the integrity of software artifacts throughout the software supply chain. SLSA defines four levels of increasing assurance, from SLSA 1 (build process documented) to SLSA 4 (hermetic, reproducible, verifiable builds).

#### Required Reading

- Þórhildr Vébjörnsdóttir, (2039). *The Forge Assembled*. Chapter 8: "The Harbor's Security: Dependency Management and Supply Chain Security."
- Open Source Security Foundation (2040). *SLSA Specification v1.1*. https://slsa.dev/spec/v1.1/
- Google (2024). *Supply Chain Security: Lessons from the XZ Utils Incident*. https://security.googleblog.com/
- Zaddach, J., et al. (2023). "FragmentManager: A Framework for the Life-Cycle Management of Open-Source Software Vulnerabilities." *IEEE Transactions on Software Engineering*, 49(8), 4723-4742.

#### Discussion Questions

1. A vulnerability scanner reports a critical vulnerability in one of your transitive dependencies. The vulnerability is in a code path your application never uses. Should you update the dependency anyway (risking breaking changes), or should you accept the risk (knowing it appears in your SBOM)? What are the tradeoffs?
2. The XZ Utils attack took two years of social engineering to execute. The attacker built trust by making legitimate contributions before introducing the backdoor. How can open source projects defend against long-term social engineering attacks without making it harder for genuine contributors to participate?
3. Reproducible builds require that the build process produce identical output regardless of the build environment. This is technically challenging (different compiler versions, different system libraries, different timestamps). How should a small open source project with limited resources implement reproducible builds?

---

### ᚹ Lecture 8: The Runecrafter's Tools — Development Environment and CI/CD for Open Source

**Date:** Week 4, Session 2

#### Overview

An open source project's development environment and CI/CD pipeline are its public infrastructure — visible to all contributors and essential for productive collaboration. This lecture covers setting up a development environment for open source contribution, configuring CI/CD for open source projects, and the emerging practice of "development experience as a product."

#### Lecture Notes

**The README as Onboarding.** A project's README is the first thing a new contributor sees. It should answer three questions within 30 seconds: (1) What does this project do? (2) How do I install it? (3) How do I contribute? A README that answers only the first question is a brochure, not onboarding.

The University of Yggdrasil's RúnarOnboard framework rates open source project READMEs on five dimensions:

| Dimension | Question | Importance |
|------------|----------|------------|
| **Purpose** | What does this project do? | Essential |
| **Installation** | How do I install and run it? | Essential |
| **Quick Start** | What's the simplest way to see it working? | Essential |
| **Contribution** | How do I contribute? Where is CONTRIBUTING.md? | Important |
| **Architecture** | How is the codebase organized? | Helpful |

Projects that score high on all five dimensions (like Django, Next.js, and the University's own RúnarRT) attract and retain more contributors than projects that only describe the purpose and installation.

**Development Environment Setup.** The most common barrier to open source contribution is the difficulty of setting up the development environment. A project that requires 17 manual steps to build, 5 proprietary tools, and 3 platform-specific scripts is a project that most contributors will abandon before their first PR.

Best practices for development environments in 2040:

- **Containerized development** — Use Docker or Dev Containers to provide a reproducible development environment. A `docker-compose up` or `devcontainer open` should give the contributor a fully configured development environment in under 5 minutes.
- **One-command build** — `make`, `npm run build`, or `cargo build` should produce a working artifact. If the build requires environment variables, create a `.env.example` file with defaults.
- **One-command test** — `make test`, `npm test`, or `cargo test` should run the full test suite. If the test suite requires external services (databases, APIs), use Docker Compose or test containers to start them automatically.
- **Automated formatting** — Use Prettier, Black, clang-format, or rustfmt to enforce consistent code formatting. Formatting should be automated, not debated.
- **Linting** — Use ESLint, Ruff, Clippy, or equivalent tools to catch common errors before CI. Configure the linter to be helpful, not punitive.

**CI/CD for Open Source Projects.** Continuous Integration (CI) and Continuous Deployment (CD) are the automated quality gates for an open source project. Every pull request triggers the CI pipeline, which runs the test suite, linters, and security scanners. If any check fails, the PR cannot be merged.

The 2040 CI/CD stack for an open source project:

| Component | Tool | Purpose |
|-----------|------|---------|
| **CI/CD** | GitHub Actions, GitLab CI | Run tests, linters, security scanners on every PR |
| **Testing** | pytest, Jest, cargo test | Verify correctness |
| **Coverage** | Codecov, Coveralls | Track test coverage |
| **Linting** | ESLint, Ruff, Clippy | Catch common errors |
| **Formatting** | Prettier, Black, rustfmt | Enforce consistent style |
| **Security** | Dependabot, Snyk, CodeQL | Detect vulnerabilities |
| **SBOM** | Syft, CycloneDX | Generate SBOMs |
| **Release** | Semantic Release, GoReleaser | Automate version bumps and changelog generation |

A well-configured CI pipeline gives contributors fast, clear feedback. A PR that fails CI should receive a comment within 2-5 minutes explaining which check failed and how to fix it. A PR that passes CI should receive a "ready for review" label.

**Development Experience as a Product.** In 2040, the most successful open source projects treat their development experience (DX) as a product — something that must be designed, tested, and improved. The DX includes:

- The CLONE-TO-CONTRIBUTE time — how long does it take from cloning the repository to submitting the first PR? The best projects (Next.js, Django, FastAPI) have a CLONE-TO-CONTRIBUTE time of under 30 minutes.
- The FEEDBACK cycle time — how long does it take to get CI results? Under 5 minutes is good; under 10 minutes is acceptable; over 20 minutes is too slow.
- The REVIEW cycle time — how long does it take to get a review? Under 48 hours is good; under 1 week is acceptable; over 2 weeks risks losing the contributor.
- The FIRST-CONTRIBUTION SUCCESS RATE — what percentage of first-time contributors have their PRs merged? Projects with mentorship programs (like Outreachy and Google Summer of Code) achieve 60-80%. Projects without them achieve 20-40%.

The University of Yggdrasil's DX Lab measures these metrics for 1000+ open source projects and publishes an annual "State of Open Source DX" report. The 2039 report found that projects with a CLONE-TO-CONTRIBUTE time under 30 minutes had 3× more contributors than projects with a CLONE-TO-CONTRIBUTE time over 2 hours.

#### Required Reading

- Þórhildr Vébjörnsdóttir, (2039). *The Forge Assembled*. Chapter 9: "The Runecrafter's Tools: Development Environment and CI/CD."
- Ford, J. (2038). "The State of Open Source Developer Experience, 2039." University of Yggdrasil DX Lab. https://dx-lab.yggdrasil.edu/state-of-dx-2039
- Nakabori, D., & Storey, M. A. (2022). "Why Developers Don't Contribute to Open Source: A Systematic Literature Review." *IEEE Software*, 39(6), 48-57.
- GitHub (2040). *About GitHub Actions*. https://docs.github.com/en/actions

#### Discussion Questions

1. You're contributing to a project that has a 45-minute build time and a 25-minute CI pipeline. Your PR fails CI, and you need to iterate. Each iteration takes 70 minutes (45 min build + 25 min CI). How can you reduce the feedback cycle time without changing the project's CI pipeline?
2. Some projects require contributors to sign a CLA before their first PR is accepted. Others use DCO (Developer Certificate of Origin). Which approach provides better DX? Which provides better legal protection for the project? Can a project have both?
3. AI-assisted PR review tools (like GitHub Copilot for Pull Requests) can automatically suggest code changes, write summaries, and identify potential issues. Should projects use these tools as part of their CI pipeline? What are the risks of over-reliance on AI review?

---

### ᚺ Lecture 9: The Thing's Law — Documentation, Accessibility, and Inclusive Contribution

**Date:** Week 5, Session 1

#### Overview

The thing was a gathering for all free people — not just the powerful, not just the warriors, but everyone with a stake in the community's decisions. In the same way, an open source project should be accessible to all potential contributors, regardless of their language, disability status, geographic location, or level of experience. This lecture covers documentation as a contribution multiplier, accessibility in open source, and the practice of inclusive contribution.

#### Lecture Notes

**Documentation: The Contribution Multiplier.** Good documentation multiplies the effectiveness of every contributor. A contributor who reads clear documentation can make their first contribution in 30 minutes. A contributor who must reverse-engineer the code to understand it may take days or give up entirely.

The documentation hierarchy for an open source project:

1. **README** — Project purpose, installation, quick start, contribution link. Every contributor reads this.
2. **CONTRIBUTING.md** — How to contribute: coding standards, PR process, CLA/DCO requirements, development environment setup. This is the most important document for new contributors.
3. **Architecture docs** — High-level description of the project's modules, data flow, and design decisions. Essential for contributors who want to make non-trivial changes.
4. **API docs** — Auto-generated documentation for every public API (function, class, method). Tools: Sphinx, JSDoc, Rustdoc, Doxygen.
5. **Tutorials** — Step-by-step guides for common tasks. "How to add a new data source," "How to write a plugin," "How to debug a failing test."
6. **ADR (Architecture Decision Records)** — Documentation of important design decisions, including the context, the decision, and the consequences. ADRs answer the question "why is the code this way?" which is the most important question for new contributors.

The University's RúnarDoc framework generates documentation from code comments, ADRs from commit messages, and tutorials from test cases. It reduces the documentation burden by 40-60% by reusing information that is already being written.

**Accessibility: Designing for Everyone.** Accessibility in open source means ensuring that people with disabilities can both use and contribute to the project. This includes:

- **Visual accessibility** — Color contrast, screen reader compatibility, alternative text for images, keyboard navigation. The Web Content Accessibility Guidelines (WCAG) 2.2 AA standard is the minimum for web-based projects.
- **Motor accessibility** — Keyboard-only navigation, voice control compatibility, customizable keyboard shortcuts. Projects should not require mouse-only interactions.
- **Cognitive accessibility** — Plain language documentation, clear error messages, predictable navigation. The plain language standard (US Plain Writing Act of 2010) is a good baseline.
- **International accessibility** — Multi-language documentation, right-to-left text support, culturally neutral examples. English is the lingua franca of open source, but not all contributors are native English speakers.

The accessibility contribution multiplier: for every 1% increase in accessibility, a project reaches approximately 1% more potential contributors. The World Health Organization estimates that 15% of the global population has a significant disability. Projects that are not accessible are excluding up to 15% of their potential contributor base.

**Inclusive Contribution: Beyond Code.** The most common mistake in open source is equating "contribution" with "code." Code is just one form of contribution. Other equally valuable contributions:

- **Documentation** — Writing, editing, translating, and updating docs.
- **Issue triage** — Reproducing bugs, categorizing issues, finding duplicates.
- **Code review** — Reviewing PRs, providing feedback, suggesting improvements.
- **Community moderation** — Enforcing the code of conduct, welcoming newcomers, managing conflicts.
- **Design** — Creating logos, UI mockups, and visual assets.
- **Translation** — Translating documentation, UI strings, and error messages into other languages.
- **Testing** — Writing test cases, running manual tests, reporting results.
- **Evangelism** — Writing blog posts, giving talks, creating tutorials, and answering questions on Stack Overflow and forums.

Projects that recognize and celebrate non-code contributions have healthier communities and more sustainable development. The University's research shows that projects with diverse contribution types (code, docs, community, design) have 2.5× higher maintainer satisfaction and 1.8× lower burnout rates than projects that only recognize code contributions.

**Inclusive Language and Communication.** Language shapes culture. The terms we use in our code, documentation, and communication reflect our values and affect who feels welcome in our community:

- **Main branch, not master** — The term "master" has connotations of slavery. Most open source projects moved from `master` to `main` as their default branch in 2020-2021.
- **Allowlist / denylist, not whitelist / blacklist** — These terms associate "white" with "permitted" and "black" with "blocked," reinforcing racial hierarchies.
- **Primary / secondary, not master / slave** — In hardware and database replication, the terms "primary" and "secondary" (or "leader" and "follower") are clearer and more neutral.
- **Gender-neutral language** — Use "they" instead of "he or she," "chairperson" instead of "chairman," and "humanity" instead of "mankind."

The Linux kernel, Python, and many other large projects have adopted inclusive language guidelines. The University's RúnarStyle linter automatically flags non-inclusive language in code comments, documentation, and commit messages.

#### Required Reading

- Þórhildr Vébjörnsdóttir, (2039). *The Forge Assembled*. Chapter 10: "The Thing's Law: Documentation, Accessibility, and Inclusive Contribution."
- W3C (2023). *Web Content Accessibility Guidelines (WCAG) 2.2*. https://www.w3.org/TR/WCAG22/
- Agerbo, A., & Tapia, J. (2038). "Documentation as a Contribution Multiplier: Measuring the Impact of Good Docs on Open Source Communities." *Journal of Open Source Software*, 3(32), 891.
- Inclusive Naming Initiative (2040). *Word Replacement Lists*. https://inclusivenaming.org/

#### Discussion Questions

1. A project's documentation is outdated by 3 years and the current maintainers don't have time to update it. How would you prioritize which documentation to update first? What tools and processes would you use to keep the documentation current?
2. Some developers argue that inclusive language changes (e.g., "main" instead of "master") are cosmetic and distract from substantive issues (e.g., maintainer burnout, security vulnerabilities). How would you respond to this argument? Are inclusive language and substantive issues in conflict, or are they complementary?
3. A project receives contributions from developers in 20 countries, writing in 15 different languages. The project's primary language is English, but many contributors struggle with English proficiency. How should the project balance the efficiency of a single documentation language with the inclusivity of multilingual documentation? What are the practical options?

---

### ᛁ Lecture 10: The Weaver's Ethics — Open Source Sustainability, Burnout, and the Labor Question

**Date:** Week 5, Session 2

#### Overview

Open source software powers the global economy, but the people who maintain it often work for free, under impossible expectations, with no safety net. This lecture confronts the sustainability crisis in open source: maintainer burnout, the free-rider problem, the ethics of corporate dependence on volunteer labor, and the emerging models for sustainable open source.

#### Lecture Notes

**The Sustainability Crisis: By the Numbers.** The 2039 Open Source Sustainability Report, published by the University of Yggdrasil's Open Source Governance Lab, paints a stark picture:

- The top 1% of open source projects (by download count) are maintained by employees of large corporations (Google, Microsoft, Meta, Amazon). They are well-funded and well-staffed.
- The next 9% of projects are maintained by 1-3 people, typically volunteers with day jobs. These maintainers have no funding, no institutional support, and no backup when they burn out.
- The bottom 90% of projects have no active maintainer at all. They are "orphaned" — still widely used, but no one is fixing bugs, reviewing PRs, or releasing new versions.
- The average maintainer spends 10-20 hours per week on project maintenance (issue triage, PR review, release management, community management) on top of their full-time job.
- 60% of maintainers report symptoms of burnout (emotional exhaustion, depersonalization, reduced accomplishment).
- 40% of maintainers have considered quitting in the past year.

These numbers are not sustainable. The open source ecosystem is a commons — shared infrastructure that everyone depends on but few contribute to. The tragedy of the commons plays out in slow motion: projects degrade, bugs go unfixed, security vulnerabilities accumulate, and eventually the maintainer walks away.

**The Free-Rider Problem.** The economic model of open source is: many people benefit, few people contribute. This is the free-rider problem in its purest form:

- Google uses Linux in Android, Chrome OS, and Google Cloud. Google employs ~50 kernel developers. The kernel has ~2,000 contributors per release.
- Microsoft uses OpenSSL in Azure, Windows, and Office. Microsoft does not employ any OpenSSL maintainers.
- Amazon uses Elasticsearch (now OpenSearch) in AWS. Amazon forked Elasticsearch after Elastic changed its license, creating OpenSearch as a maintained alternative — but the original Elasticsearch maintainers received no compensation from Amazon's billions in AWS revenue.

The free-rider problem is not purely economic — many contributors contribute for intrinsic rewards (reputation, learning, community). But intrinsic rewards are not enough to sustain the thousands of hours of unglamorous work (bug triage, dependency updates, security patches) that keep open source projects alive.

**Burnout: The Quiet Killer.** Maintainer burnout is the most serious threat to the open source ecosystem. The symptoms are well-documented:

- **Emotional exhaustion** — Maintainers feel drained, cynical, and unable to care about the project. PRs pile up unreviewed, issues go unanswered, and releases are delayed.
- **Depersonalization** — Maintainers treat contributors as a burden rather than a community. Responses become curt or hostile.
- **Reduced accomplishment** — Maintainers feel that their work doesn't matter. "No one notices when I fix a bug, but everyone complains when I don't."
- **Imposter syndrome** — Maintainers feel unworthy of their role. "I just happened to create this project — I'm not really qualified to maintain it."

The causes of burnout are structural, not individual:

- **Infinite demand, finite supply** — The number of issues and PRs grows with the project's user base, but the number of maintainers does not.
- **Unreasonable expectations** — Users expect free, immediate support. "This critical bug is blocking my production deployment. Why haven't you fixed it yet? I opened it 2 hours ago."
- **Harassment** — Some users hurl abuse at maintainers when their issues aren't fixed or their PRs aren't merged. This is particularly acute for maintainers from underrepresented groups.
- **No financial reward** — The maintainer is volunteering their time and expertise while the companies that depend on the project profit from it.

**The Emerging Models of Sustainability.** Several models are being explored to address the sustainability crisis:

1. **Corporate sponsorship** — Companies pay maintainers (as employees, contractors, or grant recipients) to work on open source. This is the most common model for the top 1% of projects. GitHub Sponsors, Open Collective, and the Sovereign Tech Fund facilitate this model.

2. **Open core** — The project is open source, but a commercial version with enterprise features is sold. GitLab, Grafana, and Elastic use this model. The risk is that the commercial version's interests may diverge from the community's.

3. **Dual licensing** — The project is available under an open source license (typically GPL) and also under a commercial license for companies that don't want to comply with the GPL's copyleft requirements. MySQL, Qt, and MongoDB use this model.

4. **Foundations** — A non-profit foundation owns the project and accepts donations. The Linux Foundation, Apache Foundation, and Python Software Foundation use this model. Foundations provide legal protection and financial stability but can be slow to make decisions.

5. **Government funding** — Governments fund open source infrastructure as a public good. Germany's Sovereign Tech Fund, the EU's Next Generation Internet program, and the US CISA's Open Source Security Initiative are examples.

6. **Usage-based insurance** — Companies that depend on open source pay into an insurance pool that funds maintenance. If a critical vulnerability is discovered, the insurance pool pays for the fix. This is a new model being explored by the Open Source Security Foundation.

The University of Yggdrasil is experimenting with a seventh model: **academic sabbatical for maintainers**. The University partners with corporations to fund 6-month sabbaticals for maintainers of critical open source projects. During the sabbatical, the maintainer works full-time on their project, sponsored by the University. The first cohort (2039) included maintainers of OpenSSL, curl, and libxml2.

#### Required Reading

- Þórhildr Vébjörnsdóttir, (2039). *The Forge Assembled*. Chapter 11: "The Weaver's Ethics: Sustainability, Burnout, and the Labor Question."
- Eghbal, N. (2020). *Working in Public*. Chapters 8-10.
- University of Yggdrasil Open Source Governance Lab (2039). *State of Open Source Sustainability, 2039*. https://osgl.yggdrasil.edu/sustainability-2039
- Nadri, C., & Gousios, G. (2022). "The Maintenance Challenges of Open Source Software Projects." *IEEE Transactions on Software Engineering*, 48(11), 4293-4310.

#### Discussion Questions

1. A maintainer of a critical open source library (used by 100,000+ projects) is experiencing severe burnout and wants to step down. The library has no other maintainers. What should happen to the library? Who is responsible for ensuring its continued maintenance — the maintainer, the community, the corporations that depend on it, or the government?
2. The "open core" model provides funding for development but creates a tension between the open source version (which must remain useful enough to attract users) and the commercial version (which must be valuable enough to justify payment). How should an open source project manage this tension? Can the open source version ever be "too good"?
3. Some argue that mandatory corporate contributions (e.g., a "digital infrastructure tax" on companies that use open source software) would solve the sustainability crisis. Others argue that this would discourage companies from using open source and would be impossible to enforce. What are the merits and disadvantages of a mandatory contribution model?

---

### ᛃ Lecture 11: The Envoy's Path — Creating and Maintaining Your Own Open Source Project

**Date:** Week 6, Session 1

#### Overview

At some point, every developer will create a piece of software that others want to use. Whether it's a library, a tool, or a framework, releasing it as open source requires more than just pushing code to GitHub. This lecture covers the practical steps of creating and maintaining an open source project: choosing a license, writing documentation, setting up CI/CD, managing releases, building a community, and knowing when to hand the project off.

#### Lecture Notes

**Before You Open Source: Should You?** Not every piece of code benefits from open sourcing. Before creating an open source project, ask yourself:

1. **Who will use this?** If only you and your team will use it, internal sharing (a private repository or a company-internal package) is more appropriate.
2. **Are you willing to maintain it?** Open sourcing a project is a commitment. Users will file bugs, request features, and ask for help. If you're not willing to respond (even to say "I don't have time for this right now"), don't open source it.
3. **Is the code ready?** Minimum viable open source: the code works, the tests pass, the README explains what it does and how to install it, and there's a LICENSE file. If any of these are missing, wait until they're ready.
4. **Is there a legal risk?** Does your code include proprietary algorithms, patented methods, or data that belongs to your employer? Check your employment contract and your company's intellectual property policy before open sourcing anything you created at work.

**The Minimum Viable Open Source Project.** The minimum requirements before making a repository public:

- **README.md** — What the project does, how to install it, how to use it, and how to contribute. This is the project's front door.
- **LICENSE** — The open source license. Without a license, the code is technically all-rights-reserved and no one can legally use it. Choose the license that matches your goals: MIT for maximum adoption, GPL for maximum copyleft, Apache-2.0 for corporate-friendly patent protection.
- **CONTRIBUTING.md** — How to contribute. Coding standards, PR process, testing requirements. This is the project's hallway.
- **CODE_OF_CONDUCT.md** — The community's behavioral standards. The Contributor Covenant is the most widely used (and most controversial) code of conduct. It sets expectations for respectful behavior and provides a process for handling violations.
- **.gitignore** — Ignore build artifacts, IDE files, and secrets. Never commit secrets (API keys, passwords, certificates) to a repository.
- **CI pipeline** — At minimum, automated tests that run on every PR. This prevents regressions and gives contributors confidence that their changes don't break anything.

**Release Management: Semantic Versioning and the Art of the Changelog.** Every open source project needs a release process that users can depend on. Semantic Versioning (SemVer) is the standard:

```
MAJOR.MINOR.PATCH

MAJOR: Breaking changes (incompatible API changes)
MINOR: New features (backward-compatible)
PATCH: Bug fixes (backward-compatible)
```

When you release version 2.0.0, you're telling users that any code that depends on version 1.x.x may break. This is a commitment: you're promising that 2.0.0 contains breaking changes, and you're committing to maintain the 2.x branch until the next major version.

The changelog is the narrative of the project's evolution. Every release should include a changelog that describes:
- **Added** — New features
- **Changed** — Changes to existing functionality
- **Deprecated** — Features that will be removed in a future release
- **Removed** — Features that have been removed
- **Fixed** — Bug fixes
- **Security** — Vulnerability fixes

Tools like semantic-release, conventional-changelog, and Keep a Changelog automate changelog generation from commit messages.

**Building a Community: The Long Game.** The health of an open source project is measured not by its star count or download count, but by the number of active contributors and the quality of the community. Building a community is a long game that requires patience, generosity, and consistency:

1. **Respond to issues and PRs promptly** — Even a "Thanks, I'll review this this weekend" response within 24 hours shows contributors that their work is valued.
2. **Label issues as "good first issue"** — This helps newcomers find approachable contributions and signals that the project welcomes new contributors.
3. **Write a CONTRIBUTING.md that welcomes newcomers** — Include step-by-step instructions for setting up the development environment, running tests, and submitting a PR.
4. **Celebrate contributions** — Thank contributors in release notes, retweet their PR links, and acknowledge their work in community channels.
5. **Be patient with beginners** — Every maintainer was once a beginner. A kind response to a poorly-written PR can turn a one-time contributor into a lifelong contributor.
6. **Enforce the code of conduct** — A community that tolerates harassment and toxicity will drive away contributors, especially from underrepresented groups.

**Knowing When to Let Go.** Every open source project reaches a point where the original maintainer can no longer (or no longer wants to) maintain it. This is normal and healthy — people change jobs, interests shift, and life happens. The important thing is to handle the transition gracefully:

- **Find a successor** — Identify a contributor who has been active, knowledgeable, and reliable. Offer them maintainer status and mentor them through the transition.
- **Archive the repository** — If no successor is available, archive the repository on GitHub. This marks the project as read-only and signals to users that it is no longer maintained. Users can still fork it, but they know that the original maintainer is no longer active.
- **Transfer the project** — If the project has a community that wants to continue maintaining it, transfer ownership to a foundation or create a new organization with multiple maintainers.
- **Write a post-mortem** — Document what you learned, what went well, what went wrong, and what you'd do differently. This is invaluable for future maintainers.

The saddest end for an open source project is when the maintainer simply disappears — no announcement, no handoff, no archived status. The repository sits on GitHub, accumulating issues and PRs that no one will respond to, while users slowly discover that the project is unmaintained. This is the open source equivalent of a ship found drifting at sea with no crew.

#### Required Reading

- Þórhildr Vébjörnsdóttir, (2039). *The Forge Assembled*. Chapter 12: "The Envoy's Path: Creating and Maintaining Your Own Project."
- Preston-Werner, T. (2013). "Semantic Versioning 2.0.0." https://semver.org/
- Keep a Changelog (2040). https://keepachangelog.com/
- Eghbal, N. (2020). *Working in Public*. Chapter 11: "What Do Maintainers Want?"

#### Discussion Questions

1. You've created a small utility library that solves a common problem. It has 500 GitHub stars and 50 users. One user files a bug that would require a significant refactor to fix. You're no longer using the library personally and have limited time. What should you do? What are your obligations to the 50 users?
2. A major corporation (10,000+ employees) is using your open source library in their production system. They don't contribute code, documentation, or financial support. They file a critical bug and demand an immediate fix. How should you respond? What are the ethical obligations of the corporation?
3. Semantic Versioning requires that any breaking change triggers a major version bump. But in practice, many projects make small breaking changes in minor versions (removing a rarely-used API, changing a default value). How strictly should a project follow SemVer? What are the consequences of strict vs. loose versioning for downstream users?

---

### ᛏ Lecture 12: The Thing Assembled — Capstone: Making Your Mark in Open Source

**Date:** Week 6, Session 2

#### Overview

The thing was not just a gathering — it was an assembly of free people who came together to create law, settle disputes, and build community. In this capstone lecture, we reflect on the entire practicum experience, present contribution portfolios, and synthesize the skills and values that define an effective open source contributor. This is the culmination of the course: the moment where theory meets practice and where each student presents their contribution to the digital thing.

#### Lecture Notes

**The Contribution Portfolio.** Each student has spent the semester making at least four substantive contributions to open source projects:

- **Bug fix** — A code change that fixes a reported bug. The student found the bug, wrote a fix, submitted a PR, and responded to review feedback.
- **Feature implementation** — A code change that adds new functionality. The student discussed the feature with the maintainers, wrote the implementation, added tests, and shepherded the PR through review.
- **Documentation improvement** — A non-code contribution that improves the project's documentation. The student identified gaps in the docs, wrote new content, and submitted it as a PR.
- **Contribution of choice** — Any other substantive contribution: issue triage, code review, translation, accessibility improvement, community moderation, or a second contribution of any type.

The contribution portfolio is not just a list of PRs — it is a narrative of the student's engagement with open source. For each contribution, the student should reflect on:

1. **What I did** — The technical content of the contribution.
2. **Why I did it** — The motivation and context.
3. **What I learned** — The technical and social lessons from the experience.
4. **What I would do differently** — Reflection on what could have been done better.
5. **The project's response** — How the maintainers and community reacted.

**The Open Source Contributor's Credo.** Over the course of this semester, we have encountered a set of principles that define effective open source contribution. These principles form a credo — a statement of belief and commitment:

1. **I contribute with empathy** — I remember that every maintainer is a person, often volunteering their time. I write clear bug reports, concise PRs, and respectful comments. I do not demand immediate fixes or complain about response times.

2. **I contribute with humility** — I recognize that I am entering someone else's project. I follow their conventions, respect their decisions, and learn from their code before proposing changes.

3. **I contribute with rigor** — I test my changes, write clear commit messages, and include documentation. I do not submit code that I have not tested or documented.

4. **I contribute with patience** — I understand that review takes time. I wait for feedback, respond promptly when I receive it, and do not pressure maintainers to merge my PRs.

5. **I contribute with responsibility** — I understand that my code may be used by thousands of people. I write code that is secure, performant, and maintainable. I do not introduce dependencies without understanding their licenses and security implications.

6. **I contribute with generosity** — I share my knowledge, review others' PRs, answer questions, and welcome newcomers. I remember that someone helped me when I was a newcomer.

7. **I contribute with sustainability** — I support the projects I depend on — through code, documentation, financial contributions, or simply by saying thank you. I recognize that open source is a commons that requires stewardship.

**The 2040 Open Source Landscape: Where We Are and Where We're Going.** As we conclude this course, the open source landscape is at an inflection point:

- **AI-assisted contribution** — AI tools are generating an increasing volume of pull requests, issue reports, and code reviews. This is both an opportunity (more contributions, faster development) and a challenge (quality assurance, maintainer workload, attribution).
- **Supply chain security** — The XZ Utils attack and SolarWinds attack have demonstrated that open source supply chain security is a national security issue. Governments are mandating SBOMs, reproducible builds, and vulnerability disclosure. The open source community is responding with SLSA, Sigstore, and improved dependency management.
- **Sustainability** — The maintainer burnout crisis continues. New funding models (government grants, corporate sabbaticals, insurance pools) are emerging but have not yet achieved mainstream adoption. The University's academic sabbatical program is a small but promising step.
- **Inclusion** — The open source community is becoming more inclusive, but there is still a long way to go. Women, non-binary people, and people from underrepresented racial and ethnic groups remain underrepresented in open source. Code of Conducts, mentorship programs, and inclusive language guidelines are helping, but structural barriers persist.
- **Fragmentation** — The proliferation of open source licenses, foundations, and governance models is creating fragmentation. Projects fork over governance disputes (Node.js forked into io.js, Elasticsearch forked into OpenSearch), and communities splinter over ideological differences. The challenge for 2040 and beyond is to maintain the collaborative spirit that makes open source powerful while accommodating diverse values and priorities.

**Your Role in the Thing.** You are now equipped to enter the digital thing — the open source community — as a knowledgeable, ethical, and effective contributor. You understand the law of the thing (licenses and legal frameworks), the craft of the thing (code contribution and review), the community of the thing (governance and inclusion), and the spirit of the thing (sustainability and empathy).

The thing succeeds when its participants bring their best selves. The code contributions matter, but so do the documentation improvements, the issue triage, the welcoming words to newcomers, and the respectful engagement in disagreements. The thing fails when its participants retreat into cynicism, entitlement, or burnout.

Go forth and contribute. The community awaits you.

#### Required Reading

- Þórhildr Vébjörnsdóttir, (2039). *The Forge Assembled*. Epilogue: "The Thing Assembled."
- Eghbal, N. (2020). *Working in Public*. Conclusion.
- UNESCO (2039). *Open Source Software as a Public Good: Policy Recommendations for Governments and Institutions*. https://unesdoc.unesco.org/
- University of Yggdrasil Open Source Governance Lab (2040). *The State of Open Source, 2040*. https://osgl.yggdrasil.edu/state-2040

#### Discussion Questions

1. Reflect on your contribution portfolio. Which contribution was the most technically challenging? Which was the most socially challenging? What did you learn about yourself as a contributor from each?
2. The course credo says "I contribute with empathy" and "I contribute with responsibility." Can these values conflict? For example, what if empathetic communication (being kind to a contributor who submitted a security vulnerability) conflicts with responsible disclosure (reporting the vulnerability immediately)?
3. In 2040, AI tools can generate an entire pull request from a natural language description. If a contributor uses AI to generate a PR that is technically correct, well-documented, and passes all tests, did they really "contribute" to the project? Where is the line between AI-assisted contribution (acceptable) and AI-generated contribution (questionable)?

---

## Final Examination Preparation

### Format

The final examination consists of **8 essay questions**. Students must **choose 4** to answer in depth. Each answer should be 800-1200 words and demonstrate mastery of course concepts, ability to apply them to novel situations, and critical engagement with the readings and practicum experience.

### Sample Questions

1. **License Strategy.** You are starting a new open source project — a high-performance database engine that you believe could become the foundation of next-generation applications. You want maximum adoption but also want to prevent cloud providers from offering your database as a service without contributing back. Which license would you choose, and why? Discuss the tradeoffs of at least three licenses (MIT, Apache-2.0, GPL-3.0, AGPL-3.0) for your specific use case.

2. **Dependency Dilemma.** Your company's application depends on 847 open source packages. A vulnerability scanner reports that 23 of these packages have known vulnerabilities, but only 5 of the vulnerable packages are actually used in your application's code paths. The other 18 are transitive dependencies from features you don't use. Your security team wants you to update all 23 packages. Your engineering team is concerned about breaking changes. How would you prioritize and remediate these vulnerabilities? What is your policy for ongoing vulnerability management?

3. **Governance Design.** You are the founder of a new open source project that has gained unexpected popularity (50,000 GitHub stars, 200 external contributors). The project currently uses BDFL governance (you are the BDFL). You want to transition to a more sustainable governance model that can survive your departure. Propose a governance structure for the project, including: (a) the governance model, (b) the decision-making process, (c) the path from contributor to maintainer, and (d) the conflict resolution mechanism.

4. **AI Contribution Ethics.** Your project receives a pull request that is entirely AI-generated. The contributor used an AI assistant to write the code, run the tests, and generate the documentation, but the contribution is technically sound and well-documented. The contributor has disclosed the AI assistance. Should you accept this PR? What are the legal, ethical, and community implications? Draft a project policy on AI-assisted contributions.

5. **Sustainability Plan.** You maintain a widely-used open source library (1 million weekly downloads, 3 maintainers, no corporate sponsorship). You spend 15 hours per week on maintenance and are experiencing burnout. Design a sustainability plan that addresses: (a) immediate relief for the maintainer (how to reduce workload), (b) medium-term funding (how to generate revenue), and (c) long-term governance (how to ensure the project survives maintainer transitions).

6. **Inclusive Onboarding.** A study of your project's contributor pipeline shows that 80% of potential contributors clone the repository but never submit a PR. Exit interviews reveal that the most common reason is "I couldn't figure out how to set up the development environment." Design a comprehensive onboarding experience that reduces the CLONE-TO-CONTRIBUTE time from the current 4 hours to under 30 minutes. Include specific tools, documentation, and community interventions.

7. **Security Incident Response.** A critical vulnerability (CVSS 9.8) is discovered in your project. The vulnerability affects all versions released in the past 2 years and could lead to remote code execution. You have a patch ready, but it requires a breaking API change. Users on the old API will need to modify their code. Draft a security incident response plan that includes: (a) disclosure timeline, (b) communication channels, (c) patch distribution, (d) migration guide, and (e) post-incident review process.

8. **Contribution Portfolio Reflection.** Reflect on your four contributions this semester (bug fix, feature, documentation, and choice). For each contribution, describe: (a) the project and the contribution, (b) what you learned about the project's codebase, governance, and community, (c) what you would do differently, and (d) how the experience changed your understanding of open source. Which contribution was the most valuable to the project, and which was the most valuable to your learning?

---

## Grading Criteria

- **A (90-100%):** Demonstrates deep understanding of open source principles, practices, and ethics; applies them to novel situations with creativity and rigor; engages critically with the readings and practicum experience; and produces well-organized, clearly written answers that could serve as teaching materials.
- **B (80-89%):** Demonstrates solid understanding of most course concepts; applies them correctly to the given situations; and writes clearly organized answers with specific references to course material and practicum experience.
- **C (70-79%):** Demonstrates adequate understanding of core course concepts; applies them with occasional errors; and writes adequately organized answers with limited references to course material.
- **D (60-69%):** Demonstrates partial understanding of course concepts; applies them with significant errors; or writes poorly organized answers with minimal references to course material.
- **F (below 60%):** Demonstrates insufficient understanding of course concepts; fails to apply them to the given situations; or writes incoherent or off-topic answers.

---

*This course was woven by Dr. Þórhildr Vébjörnsdóttir, Faculty of Computational Arts, University of Yggdrasil. The thing is assembled — may your contributions be many and your reviews be kind.*