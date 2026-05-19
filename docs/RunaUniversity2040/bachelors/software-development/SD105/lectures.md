# SD105: Version Control and Collaborative Development
## Bachelor of Science in Software Development — University of Yggdrasil, 2040

**Credits:** 3
**Semester:** Year 1, Semester 1
**Prerequisites:** None
**Instructor:** Dr. Eira Lundström, Faculty of Computational Arts

> *"A saga is never written alone. The skald learns from skalds before, revises with peers beside, and passes the verse to skalds after. Version control is the saga of code — the record of who changed what, when, and why."* — Eira Lundström, *Weaving Thought* (2038)

---

## Course Description

Version Control and Collaborative Development teaches the practices that enable software teams to work together without destroying each other's work. Using Git as the primary tool (because in 2040, Git remains the universal version control system, despite four decades of challengers), students learn the conceptual model — commits as snapshots, branches as parallel universes, merges as reconciliation — and the collaborative workflows that scale from solo projects to thousand-developer open source communities.

This course treats version control as a *communication practice*, not merely a technical tool. A well-crafted commit message tells a story. A clean branch history invites collaboration. A thoughtful code review strengthens both the code and the team. By the end, students will be able to contribute confidently to any project, from a personal portfolio to a globally distributed open source effort.

---

## Lectures

### ᚠ Lecture 1: Why Version Control? — The Problem of Collaboration

**Date:** Week 1, Session 1

#### Overview

Before version control, developers emailed zip files named `project_final_v2_REAL_FINAL.zip`. This lecture examines the problems version control solves — traceability, collaboration, experimentation, and recovery — and introduces the conceptual model (repository, commit, branch, merge) that underlies all modern version control systems.

#### Lecture Notes

Imagine a team of five developers working on the same codebase without version control. Alice fixes a bug in `auth.py` and emails it to the team. Bob is simultaneously adding a feature to `auth.py` and hasn't seen Alice's email yet. Charlie merges them manually, introducing a subtle error. Nobody knows whose change caused the production outage three weeks later because there's no record of who changed what when.

This was normal practice in the 1980s and early 1990s. It was terrible.

**What Version Control Provides:**

1. **Traceability:** Every change is recorded with who made it, when, and (in a good commit message) why. When a bug appears, `git bisect` can binary-search through thousands of commits to find the exact one that introduced it — in minutes.
2. **Collaboration without conflict:** Multiple developers can work on the same file simultaneously. The version control system tracks changes at the line level and merges them automatically when they don't conflict. When they do conflict, it presents the conflict clearly for human resolution.
3. **Safe experimentation:** Create a branch, try something radical, and if it doesn't work, delete the branch. The main codebase is untouched. This freedom to experiment is one of the most underrated benefits of version control — it lowers the cost of failure to zero.
4. **Recovery:** Delete a file by accident? Revert. Discover that last week's refactoring introduced a subtle bug? Checkout last week's version. The entire history is preserved, and nothing is truly lost.
5. **Accountability and learning:** Code review — the practice of having another developer examine your changes before they're merged — is impossible without version control. Code review is simultaneously a quality gate and a teaching tool: the reviewer catches bugs, and the author learns from the feedback.

**The Conceptual Model.** All version control systems share a core conceptual model:

- **Repository:** The database that stores the complete history of the project — every version of every file, every commit message, every branch.
- **Working copy:** Your local copy of the files from a specific point in the repository's history. You edit files here, then commit the changes back to the repository.
- **Commit:** A snapshot of the entire project at a point in time. A commit includes the changes (the "diff"), a message describing the changes, the author, the timestamp, and a reference to the parent commit(s).
- **Branch:** A named pointer to a specific commit. Creating a branch means "I want to work from this point without affecting the main line of development." Merging means "I've finished my work; incorporate it back."
- **Merge:** The operation that combines changes from two branches. If the changes are to different files (or different lines in the same file), the merge is automatic. If they're to the same lines, it's a conflict that requires human resolution.

This model is remarkably stable. Git was released in 2005. In 2040, 35 years later, the same concepts of commits, branches, and merges are used by every developer on the planet. The tools have improved (better merge algorithms, AI-assisted conflict resolution) but the concepts are unchanged.

**Centralized vs. Distributed.** Older systems like SVN (Subversion, 2000) used a central server model: one repository, everyone commits to it. Git (2005) introduced the distributed model: every developer has a complete copy of the repository, including the full history. This has profound implications:

- **Offline work:** Commit, branch, merge, and view history without a network connection.
- **No single point of failure:** If the central server dies, any developer's copy can restore it.
- **Forking as a first-class operation:** Anyone can copy ("fork") a repository and develop independently. This is the mechanism behind open source collaboration at scale.

In 2040, the distinction is largely historical — every modern system is distributed — but understanding the shift explains why Git won.

#### Required Reading

- Chacon, S. & Straub, B. (2038). *Pro Git* (4th ed.). Apress. Chapter 1: "Getting Started."
- Lundström, E. (2038). *Weaving Thought*. Chapter 4: "The Commit as Kenning."

#### Discussion Questions

1. Before version control, how did teams handle the problems of traceability and recovery? What practices existed, and why were they inadequate?
2. In 2040, some AI-augmented IDEs auto-commit every keystroke (like an infinite undo buffer). Does this replace the need for deliberate, human-authored commits? What's lost?
3. "Distributed version control means nobody has to ask permission to contribute." Is this purely a technical feature, or does it encode a political philosophy about how software should be built?

---

### ᚢ Lecture 2: Git's Object Model — Blobs, Trees, Commits, and the DAG

**Date:** Week 1, Session 2

#### Overview

Git is often taught as a set of commands. This is a mistake. Git's commands make sense only when you understand its internal model: a content-addressable filesystem built from four object types (blob, tree, commit, tag) organized as a directed acyclic graph (DAG). This lecture explains Git from the inside out.

#### Lecture Notes

Most version control systems store *diffs* — the differences between versions. Git stores *snapshots*. Every commit is a complete picture of the entire project at that moment. This sounds wasteful (storing the same file over and over), but Git compresses efficiently: identical files are stored only once, and similar files are compressed with delta compression. The snapshot model is what makes Git operations fast — checking out a commit is like extracting a tarball, not replaying a chain of diffs.

**The Four Objects.** Everything in Git is one of four object types, each identified by a SHA-256 hash of its contents (SHA-1 originally; migrated to SHA-256 in the 2030s):

1. **Blob (Binary Large Object):** The content of a file. Just the content — no filename, no permissions, no metadata. Two files with identical content share the same blob, regardless of their names or locations.

2. **Tree:** A directory listing. A tree object contains entries like `100644 blob a906cb... auth.py` and `040000 tree 3c4e9c... src/`. Each entry has a mode (file, directory, symlink), a type (blob or tree), a hash, and a filename. Trees are recursive: a tree can contain other trees, representing nested directories.

3. **Commit:** A snapshot of the project. A commit object contains:
   - A tree hash (the root tree of the project at that moment)
   - Parent commit hash(es) — usually one, multiple for merge commits, zero for the initial commit
   - Author and committer (name, email, timestamp)
   - Commit message

4. **Tag:** A named reference to a specific commit, typically used for releases. Annotated tags include a message, tagger, and optional GPG signature.

**Hashes and Immutability.** Every object is identified by the hash of its contents. Change a single byte in a file, and the blob's hash changes. Change the blob hash, and the tree's hash changes. Change the tree hash, and the commit's hash changes. This chain of hashes (each commit contains its parent's hash, which contains its parent's hash, etc.) makes Git's history tamper-evident: you cannot modify a past commit without changing every subsequent commit's hash.

In 2040, this property has been extended with **content-addressed signing**: commits can include a Merkle proof that verifies the integrity of the entire history. The University of Yggdrasil's own NorseSagaEngine repository uses this for all releases — every commit is cryptographically verifiable back to the genesis commit.

**The DAG.** Git's commit history is a Directed Acyclic Graph (DAG). Directed: each commit points to its parent(s). Acyclic: no commit can be its own ancestor (a cycle would require a commit whose hash appears in its own ancestor chain, which is cryptographically infeasible).

The DAG structure is what enables Git's branching model. A branch is just a pointer to a commit. Creating a branch: `git branch feature` (creates a new pointer at the current commit). Switching branches: `git checkout feature` (moves HEAD to the branch pointer). The DAG doesn't change — only the pointers move.

**Why This Model Matters.** Understanding the object model explains otherwise-mysterious Git behavior:
- Why `git checkout <hash>` works (the hash uniquely identifies a commit)
- Why you can recover "deleted" commits if you know the hash (the objects still exist until garbage collection)
- Why rebasing rewrites history (it creates new commits with different parents, hence different hashes)
- Why you should never rebase commits that have been pushed to a shared repository (others have the old hashes; rebasing creates conflicting histories)

#### Required Reading

- Chacon & Straub. *Pro Git*. Chapter 10: "Git Internals." [Read this chapter, and you will understand Git better than 90% of developers who use it daily.]
- Torvalds, L. (2007). "Tech Talk: Linus Torvalds on Git." *Google Tech Talks*. [The creator of Git explains why he built it. Available as transcript and video.]

#### Discussion Questions

1. Git stores snapshots, not diffs. What are the performance tradeoffs of this design? When would a diff-based system be superior?
2. The SHA-256 migration (from SHA-1) was a decade-long effort (2020-2032). Why was it so difficult, given that the hash function is "just" an implementation detail? What does this tell us about the coupling between Git's data model and its cryptographic assumptions?
3. If you accidentally commit a password to a public repository, can you truly delete it? Explain in terms of Git's object model and immutability.

---

### ᚦ Lecture 3: The Working Tree — Staging, Committing, and the Three States

**Date:** Week 2, Session 1

#### Overview

Git tracks files through three states: modified (working tree), staged (index), and committed (repository). This lecture explains the three-state model in detail, covering the staging area (Git's most misunderstood feature), .gitignore patterns, and the commit workflow from `git add` to `git commit`.

#### Lecture Notes

Git's three-state model is conceptually simple but practically subtle:

1. **Working Tree:** The files you see and edit. This is a checkout of one version of the project — typically the tip of a branch.
2. **Staging Area (Index):** A proposed next commit. You `git add` files to move them from the working tree to the staging area. The staging area lets you build a commit incrementally — you don't have to commit every change at once.
3. **Repository (.git directory):** The committed history. `git commit` takes the staging area and creates a new commit in the repository.

**Why a Staging Area?** New Git users often ask: "Why can't I just commit directly from the working tree?" The staging area serves several purposes:

- **Partial commits:** You've made five changes but only three are ready. Stage those three, commit, and leave the other two in the working tree for later.
- **Review before commit:** `git diff --staged` shows exactly what will be committed. This is your last chance to catch typos, debug code, and embarrassing comments.
- **Splitting changes:** You've refactored a function AND fixed a bug in it. Stage the refactoring as one commit, the bug fix as another. Each commit tells a clear, single-purpose story.
- **Conflict resolution marker:** During a merge, the staging area holds the resolved version while unmerged files remain in the working tree.

In 2040, AI-assisted IDEs can analyze your working tree changes and suggest how to split them into logical commits — but the staging area remains the mechanism by which you approve those suggestions.

**The .gitignore File.** Not everything in your working tree belongs in the repository. Build artifacts, dependency directories, environment files with secrets, OS thumbnail caches — these should be ignored. The `.gitignore` file specifies patterns for files and directories that Git should ignore:

```
# Dependencies
node_modules/
venv/

# Build output
dist/
*.pyc
__pycache__/

# Environment (may contain secrets)
.env
*.local

# OS files
.DS_Store
Thumbs.db
```

Patterns: `*.log` (all files ending in .log), `build/` (the build directory), `!important.log` (negation — track this even though *.log is ignored). The file is committed to the repository, so the whole team shares the same ignore rules.

A common mistake: adding a file to `.gitignore` after it has already been committed. Git continues to track committed files even if they match an ignore pattern. Solution: `git rm --cached <file>` to stop tracking while keeping the local copy.

**The Commit Workflow.** A healthy Git workflow:

```bash
git status                  # What's changed?
git diff                    # What exactly changed? (working tree vs. HEAD)
git add <files>             # Stage the changes for this commit
git diff --staged           # Review what will be committed
git commit -m "..."         # Commit with a message
```

In 2040, the `git commit` command has been augmented with AI-assisted message generation: `git commit --ai` analyzes your staged changes and drafts a commit message following the project's conventions. But the human always reviews and edits the draft — because the human knows the *intent*, not just the *diff*.

#### Required Reading

- Chacon & Straub. *Pro Git*. Chapter 2: "Git Basics." [Read this slowly; it's the foundation.]
- The official `.gitignore` templates at github.com/github/gitignore. [Skim — see what kinds of files real projects ignore.]

#### Discussion Questions

1. Critics argue the staging area is unnecessary complexity — Mercurial, Fossil, and other VCSes don't have one. Is the staging area a feature or a historical accident? What would we lose without it?
2. Should `.env` files ever be committed? What about `.env.example` (with placeholder values but no real secrets)? Discuss the boundary between "configuration" and "secrets."
3. AI-generated commit messages can describe *what* changed but may miss *why*. Is "why" always necessary? When is a descriptive "what" sufficient?

---

### ᚨ Lecture 4: Branching and Merging — Parallel Universes and Their Reconciliation

**Date:** Week 2, Session 2

#### Overview

Branching is the killer feature of modern version control. This lecture covers branch creation, switching, merging (fast-forward, three-way, and octopus merges), and merge conflict resolution. Students learn branching strategies from simple feature branches to the 2040-standard AI-augmented branch orchestration.

#### Lecture Notes

A branch in Git is a movable pointer to a commit. When you create a branch and make commits on it, the branch pointer moves forward with each commit. When you switch back to the original branch, its pointer is where you left it. Two (or more) lines of development proceed in parallel.

**The Mechanics.** The key operations:

- `git branch <name>` — Create a new branch at the current commit. Does NOT switch to it.
- `git checkout <name>` or `git switch <name>` — Switch to an existing branch. Updates the working tree to match.
- `git checkout -b <name>` — Create AND switch, in one command.
- `git merge <branch>` — Merge the named branch into the current branch.
- `git branch -d <name>` — Delete a branch. Safe: refuses if the branch hasn't been merged.

**Merge Types:**

1. **Fast-forward merge:** If the target branch has diverged from the source branch, but the source branch hasn't moved, Git simply moves the source branch pointer forward. No new commit is created. This is the cleanest merge — linear history, no extra work. `git merge --ff-only` ensures you only merge if fast-forward is possible.

2. **Three-way merge:** Both branches have new commits since they diverged. Git finds the common ancestor, computes the changes on each branch, and combines them. If the changes don't conflict, Git creates a merge commit with two parents. This preserves the full history, including the branch structure, at the cost of a non-linear history.

3. **Squash merge:** `git merge --squash` takes all the commits from the feature branch and combines them into a single commit on the target branch. The feature branch's individual commits are discarded. Useful when the feature branch's history is messy (lots of "fix typo" and "wip" commits) but the final result is clean.

4. **Rebase:** `git rebase` is not a merge, but it's the alternative. Instead of creating a merge commit, rebase *rewrites* the feature branch's commits as if they were made on top of the latest target branch. The result is a linear history, but the commits have new hashes (because their parent changed). `git rebase -i` (interactive) lets you squash, reorder, or edit commits during the rebase — this is how you clean up a feature branch before sharing it.

**The Golden Rule of Rebasing.** Never rebase commits that exist outside your local repository. If you've pushed commits to a shared branch, and you rebase them, you've created alternative versions of those commits. Your collaborators' repositories now have a different history than yours. This is the most reliable way to make your teammates hate you. The corollary: rebase freely on your local feature branches; merge (don't rebase) on shared branches.

**Conflict Resolution.** When two branches change the same lines in the same file, Git cannot automatically determine which version to keep. It marks the conflict in the file:

```
<<<<<<< HEAD
const API_URL = 'https://api.example.com/v1';
=======
const API_URL = 'https://api.example.com/v2';
>>>>>>> feature/new-api
```

The developer must choose one version, combine them, or write something new. Then `git add` the resolved file and `git commit` to complete the merge. In 2040, AI-assisted merge tools (GitButler, Mergeful) can resolve ~80% of conflicts automatically by understanding the semantic intent of both changes. But the remaining 20% — genuine disagreements about what the code should do — require human judgment.

**Branching Strategies.** How teams organize their branches:

- **GitHub Flow (2011, still dominant in 2040):** One long-lived branch (`main`), short-lived feature branches. Deploy from `main`. Simple, CI-friendly. Works for continuous delivery.
- **Git Flow (2010):** Multiple long-lived branches (`main`, `develop`, `release/*`, `hotfix/*`). More ceremony, better for versioned releases with long support cycles.
- **Trunk-Based Development (2010s, popular in 2040):** Everyone commits to `main` (or short-lived branches merged within hours). Feature flags hide incomplete work. Requires excellent CI and discipline.
- **AI-Orchestrated Branching (2040):** AI agents manage branching automatically. An agent creates a branch, implements a feature, runs tests, requests review, and merges — with human approval at key gates.

#### Required Reading

- Chacon & Straub. *Pro Git*. Chapters 3 (Branching) and 7 (Rebasing).
- Driessen, V. (2010). "A Successful Git Branching Model." *nvie.com*. [The original Git Flow article — read as a historical document.]
- Hammant, P. (2023). *Trunk-Based Development*. Leanpub. [Free online; essential for modern CI/CD practices.]

#### Discussion Questions

1. "Rebase for a clean history" vs. "Merge to preserve the truth." Which philosophy do you lean toward, and why? Are there situations where one is clearly correct?
2. AI-assisted merge tools can resolve syntactic conflicts, but semantic conflicts (two changes that don't touch the same lines but break each other's assumptions) are invisible to the diff. How can we detect semantic conflicts?
3. In a world where AI agents create, test, and merge branches automatically, what role does the human play in the branching workflow? What decisions should never be automated?

---

### ᚱ Lecture 5: Commit Messages as Communication — Writing History That Others Can Read

**Date:** Week 3, Session 1

#### Overview

A commit message is a letter to your future self and to every developer who will ever need to understand why this change was made. This lecture teaches the art of the commit message: structure (subject line, body, metadata), conventions (Conventional Commits, semantic prefixes), and the discipline of writing messages that future developers will thank you for.

#### Lecture Notes

You will read your own commit messages more than anyone else will. Six months from now, when you're debugging a regression and `git bisect` lands on this commit, the commit message is the only documentation that reliably exists. Make it count.

**Anatomy of a Good Commit Message.** The Conventional Commits specification (2020, adopted universally by 2040) provides a standard format:

```
<type>[optional scope]: <short description>

[optional body — why this change, not what]

[optional footer(s) — breaking changes, issue references]
```

Types:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Formatting, whitespace — no code change
- `refactor`: Code restructuring without changing behavior
- `perf`: Performance improvement
- `test`: Adding or fixing tests
- `chore`: Maintenance tasks (dependency updates, build config)
- `ci`: CI/CD pipeline changes
- `revert`: Reverting a previous commit

**Rules for the Subject Line:**
1. **Imperative mood:** "Add user authentication" not "Added user authentication" or "Adds user authentication." Think: "This commit will…" — "This commit will add user authentication." Consistent with Git's own messages (`Merge branch 'feature'`, `Revert "old commit"`).
2. **50 characters or fewer.** This isn't arbitrary — it ensures the subject line displays fully in `git log --oneline`, GitHub's commit list, and every other tool. Longer messages get truncated.
3. **Capitalize the first letter, no trailing period.**
4. **Be specific:** "Fix null pointer in auth middleware when session expires" not "Fix bug."

**Rules for the Body:**
1. **Separate from subject by a blank line.**
2. **Wrap at 72 characters.** Not 80 — 72 leaves room for indentation in `git log` output.
3. **Explain what and why.** Not how (the diff shows how). Focus on: Why was this change necessary? What approach was chosen and what alternatives were rejected? What are the side effects or known limitations?
4. **Use bullet points for multiple points:** `-`, `*`, or `- `.

**Rules for the Footer:**
1. **Reference issues:** `Closes #1234`, `Refs: #567`.
2. **Flag breaking changes:** `BREAKING CHANGE: The auth middleware now requires a valid JWT. Previously, expired tokens were accepted.`
3. **Co-authors:** `Co-authored-by: Sigrún Jónsdóttir <sigrun@example.com>`.

**Examples.** Compare:

❌ **Bad:**
```
fixed stuff
```

❌ **Bad (vague):**
```
Update auth.py
```

✅ **Good:**
```
fix(auth): prevent null pointer when session expires mid-request

The auth middleware assumed the session object was always initialized,
but if the session expired between the initial validation and the
subsequent role check, `session.user` was null, causing a crash.

Fixed by adding a null guard before the role check, returning 401
Unauthorized with a descriptive message.

Alternative considered: moving the role check inside the session
validation block. Rejected because it would couple session validation
to authorization logic, making future refactoring harder.

Closes #7842
```

This commit message tells you everything: what was broken, why it happened, how it was fixed, what alternative was rejected and why, and what issue it closes. Anyone reading this six months later — including the author — understands the change completely.

**AI-Assisted Messages and the Human Role.** In 2040, `git commit --ai` can generate a reasonable first draft from the diff. But the AI cannot know *why* you chose this approach over alternatives, *what* edge cases you considered, or *which* issue this relates to. The human's role is to provide the intent — the context that exists in your head, not in the diff. A commit message is not documentation of the code; it's documentation of the *decision*.

#### Required Reading

- Conventional Commits Specification (v1.0.0, 2020). *conventionalcommits.org*.
- Pope, C. (2014). "How to Write a Git Commit Message." *chris.beams.io*. [The article that standardized the 50/72 rule; still definitive.]
- Lundström, E. (2041). "The Commit as Historical Record: A Heathen Perspective." *Journal of Software Craftsmanship*, 7(3), 88-104.

#### Discussion Questions

1. Conventional Commits enforces a specific format. Some developers find this constraining. Is the benefit of machine-parseable commit types worth the cost of prescriptive formatting?
2. "If your diff is clear, your commit message can be short." Is this ever true? When is a one-line message sufficient?
3. When an AI agent makes a commit on your behalf (e.g., "Agent: fixed the linting errors"), should the agent author the commit message, or should you? What information would you want in an AI-authored commit that you might not get?

---

### ᚲ Lecture 6: Pull Requests and Code Review — The Social Contract of Software

**Date:** Week 3, Session 2

#### Overview

Code review is the practice of having another developer examine proposed changes before they're merged. It is simultaneously a quality gate, a teaching tool, a knowledge-sharing mechanism, and a social ritual. This lecture covers pull request workflows, review etiquette (for both author and reviewer), and the 2040-era integration of AI code review assistants.

#### Lecture Notes

The pull request (GitHub) or merge request (GitLab) is the mechanism by which a developer says: "I have changes on my branch. Please review them, and if they're acceptable, merge them into the main branch." The process:

1. **Author** creates a branch, makes commits, pushes to the shared repository.
2. **Author** opens a pull request: a description of what the changes do, why, and any context the reviewer needs.
3. **Reviewer(s)** examine the diff, leave comments, request changes, or approve.
4. **CI/CD pipeline** runs automated tests, linting, security scans. If any fail, the PR cannot be merged.
5. **Author** addresses feedback, pushes more commits, and requests re-review.
6. When approved and CI passes, the PR is **merged**.

**For the Author — How to Request a Good Review:**

1. **Keep PRs small.** A 50-line PR gets a thorough review. A 5,000-line PR gets a shrug and "LGTM." The ideal PR is a single, coherent change — one feature, one bug fix, one refactoring.
2. **Write a good PR description.** Not "Please review." Explain: what does this change? Why? How did you test it? Are there risks or follow-up work?
3. **Review your own PR first.** Go through the diff line by line before requesting review. You'll catch half your own issues. This respects the reviewer's time.
4. **Separate functional and non-functional changes.** If you renamed a variable AND changed the logic, put them in separate commits (or separate PRs). The reviewer can then focus on the logic without being distracted by the rename.
5. **Respond to all feedback.** Not just the comments you agree with. If you disagree, explain why — respectfully. "Good point, but I think the current approach is clearer because…" is better than ignoring a comment.

**For the Reviewer — How to Give a Good Review:**

1. **Review the code, not the person.** "This function could be simplified by using Array.reduce()" not "Why would you write it this way?" Assume competence; suggest improvements.
2. **Be specific.** "This looks wrong" is useless. "I think this will fail when `user` is null because the null check is on line 42 but the access is on line 38" is actionable.
3. **Distinguish between blockers and suggestions.** Use conventional prefixes: `nit:` (nitpick, not blocking), `suggestion:` (I think this would be better, but up to you), `issue:` (this needs to be fixed before merge), `question:` (I don't understand this; please explain), `praise:` (nice work!).
4. **Review in passes.** First pass: does the change make sense at the architectural level? Second pass: are there bugs, edge cases, security issues? Third pass: style, naming, documentation.
5. **Limit review sessions to 60 minutes.** After an hour, defect detection rates drop significantly. Take breaks between complex reviews.

**AI in Code Review.** In 2040, AI code review assistants (Hermes Review, GitHub Copilot Review, CodeRabbit) provide first-pass review automatically: they flag potential bugs, suggest improvements, enforce style guides, and check for common security issues. The human reviewer's role has shifted from "find the bugs" to "validate the AI's findings and add context the AI can't see."

The AI can tell you that a function is O(n²) and could be O(n log n). It cannot tell you that the product manager changed the requirements yesterday and this PR is now implementing the wrong thing. The AI can catch syntax errors; the human catches *intent* errors.

**The Social Dimension.** Code review is fundamentally a social practice. It's how teams build shared understanding of the codebase. It's how senior developers mentor juniors. It's how teams maintain quality standards without a heavy-handed process. A team that does code review well produces better software AND happier developers. A team that does it poorly — nitpicking, gatekeeping, rubber-stamping — produces resentment and bugs.

#### Required Reading

- Google Engineering Practices Documentation. "How to Do a Code Review." *google.github.io/eng-practices/review/reviewer/.* [The gold standard for review practices.]
- Bacchelli, A. & Bird, C. (2013). "Expectations, Outcomes, and Challenges of Modern Code Review." *ICSE 2013*. [The academic study that established what reviewers actually look for.]
- University of Yggdrasil Software Engineering Lab. (2042). "AI-Assisted Code Review: Augmentation, Not Replacement." *Technical Report UY-SEL-2022-7*.

#### Discussion Questions

1. Small PRs are better reviewed, but some changes are inherently large (e.g., a framework migration). How do you handle large, necessary changes without overwhelming reviewers?
2. AI code review tools can catch an increasing fraction of bugs. At what point does human code review become unnecessary? Is there a residual role that AI cannot fill?
3. Code review is unpaid labor in open source, yet it's essential for quality. How should we think about the economics of code review — who should do it, and how should they be compensated?

---

### ᚷ Lecture 7: Collaboration at Scale — Forking, Upstream, and the Open Source Workflow

**Date:** Week 4, Session 1

#### Overview

Open source software — from Linux to Hermes Agent to the Yggdrasil memory well protocol — is built by distributed, often volunteer, contributors who may never meet in person. This lecture covers the collaboration patterns that make this possible: forking, pull requests from forks, upstream/downstream relationships, and the governance models that keep massive projects coherent.

#### Lecture Notes

The Cathedral and the Bazaar. Eric Raymond's 1997 essay contrasted two models of software development: the Cathedral (centralized, planned, released in versions) and the Bazaar (decentralized, emergent, released early and often). Raymond argued that the Bazaar — exemplified by Linux — produced better software faster. In 2040, looking back at a half-century of open source, the verdict is clear: the Bazaar won. Every major software platform — operating systems (Linux), browsers (Chromium, Firefox), AI frameworks (PyTorch, TensorFlow), version control (Git itself), and the web platform itself — is developed in the open, by distributed contributors.

**The Fork-and-Pull Model.** The standard open source contribution workflow:

1. **Fork** the repository: create your own copy on the hosting platform (GitHub, GitLab, the Yggdrasil Code Forge).
2. **Clone** your fork locally.
3. **Create a branch** for your change.
4. **Make commits** following the project's conventions.
5. **Push** to your fork.
6. **Open a pull request** from your fork's branch to the original repository's main branch.
7. **Respond to review feedback** with additional commits.
8. When approved, the maintainer **merges** your PR.

The beauty of this model: the contributor doesn't need write access to the original repository. Anyone can propose a change. The maintainer retains control — they decide what gets merged. This is how Linux, with thousands of contributors, has maintained architectural coherence for 50 years.

**Upstream/Downstream.** The "upstream" is the original repository you forked from. The "downstream" is your fork (and any forks of your fork). Keeping your fork synchronized with upstream is essential:

```bash
git remote add upstream https://github.com/original/repo.git
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

Failing to sync leads to "merge conflict hell" when you eventually try to contribute — your fork has diverged so far that your PR no longer applies cleanly.

**Governance Models.** How does an open source project make decisions?

- **BDFL (Benevolent Dictator For Life):** One person has final say. Linux (Linus Torvalds), Python (Guido van Rossum until 2018). Effective when the dictator is wise; fragile when they're not.
- **Meritocracy:** Those who contribute the most code or review gain decision-making authority. Linux kernel subsystem maintainers.
- **Consensus-seeking:** Major decisions require broad agreement. Debian's General Resolution process, IETF's "rough consensus and running code."
- **Foundation-based:** A neutral non-profit holds the assets and facilitates governance. Apache Foundation, Linux Foundation, the Yggdrasil Open Source Consortium (2038).

In 2040, the trend is toward foundation-based governance with explicit Codes of Conduct and inclusive decision-making processes. The BDFL model, while historically effective, concentrates too much power in one person and creates a single point of failure (both technical and social).

**The Contributor's Journey.** It begins with a bug report. Then a documentation fix. Then a small code change. Then regular contributions. Then reviewing others' PRs. Then becoming a maintainer. Open source contribution is a ladder, and every rung requires both technical skill and social fluency — understanding the project's norms, communicating effectively, and building trust.

#### Required Reading

- Raymond, E.S. (1997). "The Cathedral and the Bazaar." *First Monday*. [The essay that launched a thousand open source projects. Read it critically — what did Raymond get right, and what did he miss?]
- Fogel, K. (2038). *Producing Open Source Software* (3rd ed.). O'Reilly Media. Chapters 1-4.
- Eghbal, N. (2024). *Working in Public: The Making and Maintenance of Open Source Software*. Stripe Press. [Essential reading on the economics and sociology of open source.]

#### Discussion Questions

1. The BDFL model has declined in favor of foundation-based governance. Is this an improvement, or does committee-based decision-making slow innovation? Can you point to cases where one model clearly outperformed the other?
2. Open source maintainers often experience burnout — they're expected to review PRs, answer issues, and maintain quality, usually for free. How should we address the sustainability problem in open source?
3. In 2040, AI agents can contribute code to open source projects. Should AI-generated PRs be accepted? What are the ethical and practical considerations?

---

### ᚹ Lecture 8: Continuous Integration and Continuous Delivery (CI/CD)

**Date:** Week 4, Session 2

#### Overview

Committing code is only half the battle. The code must be tested, built, and deployed — preferably automatically, every time a change is pushed. This lecture covers CI/CD pipelines: the automated workflows that run tests, perform static analysis, build artifacts, and deploy to production when all checks pass.

#### Lecture Notes

"Works on my machine" is the most dreaded phrase in software development. CI/CD eliminates it by ensuring that every change is tested in a clean, reproducible environment before it reaches production.

**Continuous Integration (CI).** The practice of frequently integrating code changes into a shared repository, with automated verification:

1. Developer pushes a commit.
2. CI system provisions a clean environment (container, VM).
3. Dependencies are installed.
4. Tests run: unit, integration, maybe end-to-end.
5. Linters and static analyzers check code quality.
6. Security scanners check for vulnerabilities.
7. If all checks pass, the build is "green." If any fail, the build is "red."

The CI feedback loop should be fast — ideally under 10 minutes. If it's longer, developers context-switch and lose flow. In 2040, AI-powered CI systems (Hermes CI, GitHub Actions Copilot) can predict which tests are relevant to a given change and run those first, providing initial feedback in under a minute while the full suite runs in parallel.

**Continuous Delivery/Deployment (CD).** Once CI passes, CD takes over:

- **Continuous Delivery:** Every green build is *ready* to be deployed. A human decides when to push the button. Used for regulated industries, critical systems, and products with marketing launch dates.
- **Continuous Deployment:** Every green build is *automatically* deployed. No human intervention. Used by most web services (canary deployments, feature flags, and automated rollback make this safe).

**Pipeline as Code.** The CI/CD configuration is stored in the repository itself — typically `.github/workflows/ci.yml`, `.gitlab-ci.yml`, or `Jenkinsfile`. This means:
- The pipeline is versioned alongside the code. Changes to the build process go through code review.
- Anyone who forks the repository gets the CI configuration for free.
- The pipeline is reproducible — you can run it locally with `act` or similar tools.

**Modern CI/CD Patterns (2040):**

- **DAG-based pipelines:** Not a linear sequence of stages. A DAG where "lint" and "unit-test" run in parallel, both must pass before "integration-test," which must pass before "deploy-staging." Dependencies are explicit; parallelism is automatic.
- **Ephemeral preview environments:** Every PR gets a temporary deployment at a unique URL. Reviewers can test the change in a live environment without setting up anything locally.
- **AI-predicted test selection:** The CI system uses machine learning to predict which tests are likely to fail given the change, and runs those first. If none of the predicted-failure tests fail, the remaining tests are deferred until a lower-priority batch.
- **Green/blue and canary deployments:** Deploy the new version alongside the old. Route a small percentage of traffic (1%, then 5%, then 25%) to the new version. Monitor error rates. If they spike, roll back automatically.

**The Human Element.** CI/CD automates the mechanical parts of software delivery, but it cannot automate judgment. The decision to deploy to production — even in a continuous deployment setup — ultimately reflects a human decision about risk tolerance, and that decision is encoded in the pipeline configuration. Understanding the pipeline is understanding your team's risk posture.

#### Required Reading

- Humble, J. & Farley, D. (2010). *Continuous Delivery: Reliable Software Releases through Build, Test, and Deployment Automation*. Addison-Wesley. Chapters 1-4. [The seminal work; still relevant in 2040 despite the technology evolution.]
- GitHub. "GitHub Actions Documentation." *docs.github.com/en/actions*. [The reference for the most-used CI/CD platform in 2040.]
- Kim, G., Humble, J., Debois, P., & Willis, J. (2035). *The DevOps Handbook* (3rd ed.). IT Revolution Press. Chapters 5-8.

#### Discussion Questions

1. Continuous deployment means every commit goes to production. Is this appropriate for all software? What kinds of projects should NOT use continuous deployment?
2. AI-predicted test selection can dramatically speed up CI. But it might also miss failures in tests that the model didn't predict as relevant. How do you balance speed and safety?
3. CI/CD pipelines are code, and code can have bugs. What happens when the CI configuration itself is broken — for example, a pipeline that silently skips security scans? How do you test the pipeline?

---

### ᚺ Lecture 9: Git Archaeology — Bisect, Blame, and Reflog

**Date:** Week 5, Session 1

#### Overview

Version control is not just for the present — it's for investigating the past. This lecture teaches Git archaeology: the techniques for finding when a bug was introduced (`git bisect`), who last changed a line and why (`git blame`), and recovering from disasters (`git reflog`, `git fsck`).

#### Lecture Notes

A bug report arrives: "The login page has been broken since last Tuesday." No one on the team remembers changing the login code. How do you find the commit that introduced the bug?

**`git bisect` — Binary Search Through History.** If you have a known-good commit (e.g., a release from two weeks ago) and a known-bad commit (the current HEAD), `git bisect` performs a binary search through the intermediate commits. At each step, you test the code and tell Git whether it's good or bad. After log₂(n) steps, you've found the exact commit that introduced the bug.

```bash
git bisect start
git bisect bad HEAD
git bisect good v2.1.0
# Git checks out a commit halfway between good and bad
# Test it, then:
git bisect good  # or git bisect bad
# Repeat until:
# abc1234 is the first bad commit
git bisect reset
```

In 2040, `git bisect --ai` can automate this entirely: provide a test command, and the AI runs it at each step, reporting the result. For deterministic bugs (the test always fails in the same way), this turns a potentially hours-long investigation into a 2-minute automated process.

**`git blame` — Who Wrote This Line?** Not for assigning fault (despite the name), but for understanding *context*. When you encounter a confusing line of code, `git blame` shows you:
- Who wrote it
- When
- Which commit introduced it
- (Optionally) the commit message explaining why

```bash
git blame auth.py -L 42,50
# Shows lines 42-50 with author, date, and commit hash for each line
```

The next step: `git show <hash>` to read the full commit that introduced that line. The commit message often explains the context that the code alone doesn't provide. This workflow — blame, then show — is the single most effective way to understand unfamiliar code.

**`git reflog` — The Safety Net.** Git tries very hard not to lose data. Even "deleted" commits (branches deleted, rebases abandoned) are retained for 90 days (by default) in the reflog. `git reflog` shows every movement of HEAD and branch pointers:

```bash
git reflog
# abc1234 HEAD@{0}: commit: Fix login bug
# def5678 HEAD@{1}: rebase finished: returning to refs/heads/feature
# ghi9012 HEAD@{2}: commit: Add login page tests
```

If you accidentally delete a branch or lose commits during a rebase, the reflog is your recovery tool: `git checkout HEAD@{2}` to return to the state before the disaster. The reflog has saved more developer sanity than any other Git feature.

**`git fsck` — Filesystem Check.** Like `fsck` for disk filesystems, `git fsck` verifies the integrity of the Git object database. It checks that all referenced objects exist, that hashes are consistent, and that the DAG is intact. `git fsck --unreachable` finds commits that are no longer referenced by any branch or tag — these are candidates for garbage collection (or recovery, if you're looking for lost work).

**The Archaeologist's Mindset.** Git archaeology is not just about commands — it's about a way of thinking. When confronted with a mystery in the codebase, the archaeologist's first instinct is not "let me try to understand this by reading the current code" but "let me find the commit that introduced this and read the commit message." The history is a first-class source of documentation, often more reliable than comments (which can become stale) or documentation (which can become out of date). The history doesn't lie — it records exactly what happened, when, and (in a good commit message) why.

#### Required Reading

- Chacon & Straub. *Pro Git*. Chapters 6 (GitHub), 7 (Git Tools — specifically Interactive Staging, Stashing, and Cleaning), and 10 (Internals — Maintenance and Data Recovery).
- The official `git-bisect` documentation. [Read the section on "Automated Bisect" — you can provide a script that returns 0 for good and non-zero for bad.]

#### Discussion Questions

1. `git blame` is often used to find "who broke this" — but the name suggests fault-finding. Does the name matter? Should it be renamed (some have proposed `git praise` or `git annotate`)? Why or why not?
2. `git bisect` works brilliantly for deterministic bugs but fails for intermittent failures (race conditions, timing-dependent bugs). How do you investigate the history of an intermittent bug?
3. The reflog is local — it doesn't survive a fresh clone. If you've lost commits and don't have the original repository, are they gone forever? What other recovery mechanisms exist?

---

### ᚾ Lecture 10: Monorepo vs. Polyrepo — The Great Divide

**Date:** Week 5, Session 2

#### Overview

Should your organization store all its code in a single repository (monorepo) or across many repositories (polyrepo)? This debate has divided the software industry for decades. This lecture examines the tradeoffs — tooling, collaboration, dependency management, CI/CD — and the 2040-era hybrid approaches enabled by virtual repository technologies.

#### Lecture Notes

Google has a monorepo. As of 2040, it contains over 2 billion lines of code, every project from Search to Gmail to Gemini, in a single repository. Microsoft, historically, used many repos — one for Windows, one for Office, one for Azure. Meta uses a monorepo (fbsource). Amazon uses many repos (one per service). Both approaches can work at immense scale. The question is not "which is better" but "which tradeoffs fit your organization?"

**Monorepo Advantages:**
- **Atomic cross-project changes:** Change an API and update all callers in a single commit. In a polyrepo, you'd need coordinated PRs across multiple repositories.
- **Unified tooling:** One build system, one CI pipeline, one code review tool. Consistency reduces cognitive overhead.
- **Easy code sharing and discovery:** All code is visible. Developers can find and reuse existing libraries instead of reinventing them.
- **Simplified dependency management:** All projects use the same version of shared libraries. No "dependency hell" across repos.

**Monorepo Disadvantages:**
- **Scale challenges:** At Google's scale, `git status` would take hours. Massive investment in custom tooling (Piper, CitC) is required.
- **Coupled builds and tests:** A change in a low-level library triggers rebuilds and retests of every dependent project — potentially millions of tests. Intelligent test selection is essential.
- **Access control complexity:** Not everyone should have access to everything (e.g., confidential projects). Fine-grained access control within a monorepo is harder than at the repository boundary.
- **Learning curve:** New developers are confronted with the entire codebase. Finding the right entry point can be overwhelming.

**Polyrepo Advantages:**
- **Autonomous teams:** Each team owns their repository end-to-end. They choose their own tooling, release cadence, and quality standards.
- **Natural boundaries:** Repository boundaries enforce API contracts. Teams must explicitly version and document their APIs because other teams consume them as dependencies.
- **Independent scaling:** Each repo's CI/CD scales independently. A busy repo doesn't slow down a quiet one.
- **Simpler onboarding:** New developers start with a small, focused repository rather than the entire company codebase.

**Polyrepo Disadvantages:**
- **Cross-repo changes are painful:** Changing a shared API requires coordinated PRs, version bumps, and careful sequencing.
- **Dependency management overhead:** Each repo must declare and update its dependencies. Version skew between repos is common.
- **Duplicated tooling:** Each repo configures its own CI, linting, and build system — or you invest in shared templates that must be maintained.
- **Code discoverability is harder:** Where is the canonical implementation of `UserAuth`? It might be in any of 50 repos.

**Virtual Repositories (2040).** The 2040-era innovation is the *virtual repository* — a single Git repository that is actually composed of many underlying repositories, stitched together by a virtual filesystem layer (VFS for Git, 2030s). Developers interact with a monorepo experience (clone one thing, see everything), but underneath, repositories are independently owned, versioned, and access-controlled.

The University of Yggdrasil's own infrastructure uses a virtual monorepo based on the Yggdrasil Code Weave (2041): all student projects, faculty research code, and administrative systems appear in a single unified repository, but each is independently versioned, reviewed, and deployed. The weave layer handles cross-repo dependency resolution and atomic changes across project boundaries.

**Decision Framework.** Ask:
- How often do teams need to make atomic cross-project changes? (Often → monorepo)
- How independent are the teams? (Very → polyrepo)
- What is the organization's size and tooling investment capacity? (Large + high investment → monorepo; smaller + lower investment → polyrepo)
- What are the security/access requirements? (Strict isolation → polyrepo)

There is no universal answer. The best choice is the one your team can execute well.

#### Required Reading

- Potvin, R. & Levenberg, J. (2016). "Why Google Stores Billions of Lines of Code in a Single Repository." *Communications of the ACM*, 59(7), 78-87. [The definitive monorepo paper.]
- Beyer, B. et al. (2039). *Site Reliability Engineering* (4th ed.). O'Reilly Media. Chapter on "Monorepo Operations."
- University of Yggdrasil DevOps Group. (2041). "The Yggdrasil Code Weave: Virtual Monorepo Architecture." *Technical Report UY-DEVOPS-2021-4*.

#### Discussion Questions

1. Monorepos require significant tooling investment (VFS for Git, intelligent test selection, distributed build caching). Is this investment only justified at Google/Meta scale, or do smaller organizations benefit too?
2. Virtual repositories claim to combine the best of both worlds. What are the genuine downsides — what new problems do they introduce?
3. In open source, polyrepo is the default (each project is its own repository). Could open source benefit from monorepo practices? What would a "monorepo for open source" even look like?

---

### ᛁ Lecture 11: Git Hooks and Automation — Enforcing Quality at Commit Time

**Date:** Week 6, Session 1

#### Overview

Git hooks are scripts that run automatically at specific points in the Git workflow — before a commit, after a merge, before a push. This lecture covers the hooks API, common use cases (linting, commit message validation, secret scanning), and the 2040-era ecosystem of AI-powered hooks that catch mistakes before they leave the developer's machine.

#### Lecture Notes

"Move quality left" is the DevOps mantra — catch problems as early as possible in the development process. A bug caught during code review costs 10x more to fix than one caught at commit time. A bug caught in production costs 100x more. Git hooks are the earliest possible quality gate: they run on the developer's machine, before the code is even shared.

**The Hooks API.** Git provides two categories of hooks:

**Client-side hooks** (run on your machine):
- `pre-commit`: Runs before the commit message editor opens. Use for: linting, formatting (`prettier --check`), running fast unit tests, checking for debug statements.
- `prepare-commit-msg`: Runs after pre-commit, before the editor. Use for: prepopulating the commit message with a template (branch name, issue number).
- `commit-msg`: Runs after the message is written. Use for: validating the commit message format against Conventional Commits.
- `post-commit`: Runs after the commit is created. Use for: notifications, updating a local changelog.
- `pre-rebase`: Runs before a rebase. Use for: warning if you're about to rebase commits that have been pushed.
- `pre-push`: Runs before a push. Use for: running the full test suite, checking for secrets.

**Server-side hooks** (run on the remote repository):
- `pre-receive`: Runs before accepting a push. Use for: enforcing branch protection, rejecting commits that don't pass CI, checking commit authorship.
- `update`: Similar to pre-receive but runs per branch.
- `post-receive`: Runs after the push is accepted. Use for: triggering CI/CD, sending notifications, updating deployment status.

**Hook Management with pre-commit.** The `pre-commit` framework (2014, ubiquitous in 2040) provides a declarative way to manage hooks:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
  - repo: local
    hooks:
      - id: secret-scan
        name: Check for secrets
        entry: secret-scanner
        language: system
```

Running `pre-commit install` sets up the hooks. `pre-commit run --all-files` runs them manually. The hooks are versioned in the repository, so every developer has the same ones.

**2040-Era AI Hooks.** Beyond traditional linting and formatting:

- **Intent-based commit message validation:** An AI reads your diff and your commit message. If the message doesn't match the intent of the changes, the hook warns: "This commit message says 'fix typo' but the diff changes 200 lines across 15 files. Did you mean something else?"
- **Semantic conflict detection:** Before push, the hook checks whether your changes might semantically conflict with recent changes by other developers — not syntactic conflicts (Git handles those), but logical conflicts (e.g., you removed a function that someone else just added a caller for).
- **Accessibility regression detection:** The hook runs the changed UI components through an accessibility checker and warns if contrast ratios, focus indicators, or ARIA labels have regressed.
- **License compliance:** If you're importing code from another project, the hook checks the license compatibility and warns about copyleft issues.

**When to Skip Hooks.** `git commit --no-verify` bypasses pre-commit and commit-msg hooks. This should be a last resort — for emergency hotfixes, or when the hook itself is buggy. Frequent use of `--no-verify` is a sign that the hooks need adjustment, not that the developer is lazy.

#### Required Reading

- Git documentation. "Customizing Git — Git Hooks." *git-scm.com/book/en/v2/Customizing-Git-Git-Hooks*.
- pre-commit framework documentation. *pre-commit.com*.
- University of Yggdrasil Code Quality Lab. (2043). "AI-Powered Git Hooks: A Survey of Current Practice." *Journal of Software Engineering Tools*, 12(1), 33-67.

#### Discussion Questions

1. Pre-commit hooks run on every commit. If they're too slow, developers will `--no-verify` or stop committing frequently (making larger, harder-to-review commits). How fast is "fast enough" for pre-commit hooks?
2. Should server-side hooks enforce commit message format? Or is that overreach — should teams be trusted to regulate their own messages?
3. AI hooks that analyze intent raise privacy concerns — the AI is reading your code before you've decided to share it. Is this different from a human reviewer reading your code? Where is the line?

---

### ᛃ Lecture 12: The Version-Controlled Life — Git as a Career Skill and Cultural Practice

**Date:** Week 6, Session 2

#### Overview

The final lecture steps back from the technical details to examine version control as a cultural practice and a career-defining skill. We trace the evolution from RCS (1982) through CVS, SVN, and Git to the 2040 landscape of AI-augmented version control. We conclude with a vision of version control as *institutional memory* — the living history of every software project.

#### Lecture Notes

In 1982, Walter Tichy created RCS (Revision Control System), which could track changes to individual files. In 1986, Dick Grune created CVS (Concurrent Versions System), which could track entire directory trees and handle concurrent edits. In 2000, SVN (Subversion) improved on CVS with atomic commits and directory versioning. In 2005, after the Linux kernel's proprietary version control system (BitKeeper) revoked its free license, Linus Torvalds created Git in a weekend.

Each generation solved the problems the previous generation had revealed. RCS solved "what changed?" CVS solved "how do we work on the same project without emailing zip files?" SVN solved "how do we rename files and directories without losing history?" Git solved "how do we work offline, branch cheaply, and contribute without permission?"

**Why Git Won.** Git succeeded not because it was the most polished tool (Mercurial, its contemporary, had a cleaner UI and better documentation) but because of three decisions:

1. **GitHub.** Launched in 2008, GitHub made Git social. Pull requests, forks, issues, and a clean web UI transformed Git from a tool for kernel hackers to a platform for everyone.
2. **Cheap branching.** Git branches take milliseconds to create and negligible disk space. This lowered the cost of experimentation to zero, enabling workflows (feature branches, pull requests) that were impractical in SVN.
3. **The distributed model.** You don't need permission to start working. Fork, branch, commit — all local. When you're ready, push and open a PR. This decentralized power in a way that resonated with the open source ethos.

**The Unresolved Tensions.** Despite 35 years of Git dominance, some tensions remain:

- **Usability:** Git's command-line interface is famously confusing. `git checkout` does a dozen different things. `git reset` has three modes. Error messages are cryptic ("fatal: the remote end hung up unexpectedly"). In 2040, AI assistants (GitHub Copilot for CLI, Hermes Terminal) have mitigated but not eliminated this.
- **Binary files:** Git handles text beautifully and binary files poorly. Large game assets, ML model weights, and design files still stretch Git's snapshot model. Git LFS (Large File Storage, 2015) is a workaround, not a solution.
- **History rewriting:** Rebasing is powerful but dangerous. The "never rebase shared branches" rule is simple to state and hard to enforce. Teams still lose work to rebase conflicts.
- **Monorepo scale:** Git was designed for the Linux kernel (~30 million lines). At Google scale (2 billion lines), Git's architecture breaks. Virtual filesystems and custom backends are required.

**Version Control as Institutional Memory.** A software project's Git history is its memory. Every decision — every architecture choice, every bug fix, every abandoned experiment — is recorded. New team members can `git log` to understand how the project evolved. Old team members can `git blame` to remember why they made a particular choice.

In 2040, AI agents can analyze a project's entire Git history to answer questions like: "Which parts of this codebase change most frequently?" "What types of bugs recur?" "Which developer has the most expertise in the authentication module?" The Git history becomes a knowledge base that can be queried, summarized, and learned from.

This is the ultimate value of version control: not just managing code, but preserving the *story* of the code. Every commit is a sentence. Every branch is a subplot. Every merge is a resolution. The repository is the saga, and you are one of its authors.

**A Closing Charge.** Use version control for everything. Not just code — your thesis, your configuration files, your notes, your memory well entries. If it's text and it matters, it belongs in version control. The habit of committing early and often — of treating every piece of work as part of an ongoing, traceable, recoverable narrative — is one of the few truly universal best practices in software development.

Commit your work. Write good messages. Review each other's changes. The saga continues.

#### Required Reading

- Torvalds, L. (2007). "Tech Talk: Linus Torvalds on Git." [Revisit after you've used Git for a semester; it will mean much more.]
- Your own Git history for this course. Run `git log --oneline --graph --all` and reflect on what your commit history says about your learning process.
- Lundström, E. (2043). "The Repository as Saga: Version Control and the Preservation of Institutional Memory." *Communications of the ACM*, 66(4), 42-50.

#### Discussion Questions

1. Git has been the dominant VCS for 35 years. Will it last another 35? What would replace it, and what would need to be true for the replacement to succeed?
2. "Use version control for everything." Is there anything that should NOT be in version control? Secrets? Large binaries? Personal notes? Defend your boundaries.
3. If an AI agent can analyze a project's entire Git history and answer architectural questions, does the human still need to understand the history? What is the human's relationship to the institutional memory when an AI mediates access to it?

---

## Final Examination Preparation

### Part I: Written Examination (60%)

Choose **four** of the following **eight** essay questions.

1. **The Git Object Model.** Explain the relationship between blobs, trees, commits, and tags. Given a hypothetical repository structure, trace what objects would be created by a sequence of operations (add file, commit, create branch, modify file, commit, merge). Explain why the SHA-256 migration was so difficult.

2. **Merge vs. Rebase.** A team is debating whether to use `git merge` or `git rebase` for integrating feature branches. Present the strongest arguments for each approach. Then propose a hybrid policy that maximizes the benefits of both while minimizing the risks. Justify your policy with reference to the Golden Rule of Rebasing.

3. **Code Review as Social Practice.** Analyze a real or hypothetical code review interaction. Identify the communication patterns that make it effective or ineffective. Propose concrete improvements to the team's review practices, referencing the conventional comment prefixes (nit, issue, question, etc.) and the distinction between blockers and suggestions.

4. **Monorepo Decision.** Your organization is considering migrating from a polyrepo structure to a monorepo (or vice versa). Using the decision framework from Lecture 10, analyze your organization's specific constraints and recommend a strategy. Address tooling investment, team autonomy, and the virtual repository alternative.

5. **Commit Message Quality.** Select three commits from a real open source project (or your own work). Grade each commit message against the criteria from Lecture 5. For any that fall short, rewrite the message to meet the standard. Reflect on what your analysis reveals about the project's culture.

6. **CI/CD Pipeline Design.** Design a CI/CD pipeline for a hypothetical web application with a frontend, backend API, and database migrations. Specify the stages, their parallelism, the conditions for proceeding, and the deployment strategy. Justify each design choice against the principles of fast feedback and safety.

7. **Git Disaster Recovery.** Describe a realistic Git disaster scenario (lost commits after a rebase, accidentally merged the wrong branch, committed secrets to a public repo). For each, explain the recovery procedure step by step, referencing the specific Git commands and their effects on the object model.

8. **Version Control and AI.** In 2040, AI agents can make commits, write messages, open PRs, and review code. Analyze the implications for version control as a human practice. What should remain human, and what can be safely automated? What new skills do developers need?

### Part II: Collaborative Project (40%)

Contribute to an existing open source project (or a class project repository) with the following deliverables:

1. **At least three merged pull requests** demonstrating different types of contributions (bug fix, feature, documentation improvement, test addition).
2. **At least two code reviews** of other contributors' PRs, demonstrating constructive feedback using the conventional comment prefixes.
3. **A reflective essay** (1,000-1,500 words) analyzing your collaboration experience: what went well, what was challenging, what you learned about collaborative development that you couldn't have learned from lectures alone.

---

**ᚱ ᛁ ᛏ — The writing endures. Commit it.**

*SD105: Version Control and Collaborative Development — University of Yggdrasil, 2040*
*Instructor: Dr. Eira Lundström*
*Course version: 1.0 — 2040 Academic Year*