# 12 — Voyager: Lifelong Learning in Open-Ended Environments

**Category:** Agent Architectures
**Runa relevance:** Hirð (skill acquisition), Skuld (curriculum), Smiðja (skill registry), Eir (skill repair)
**Status:** Research synthesis.
**Last touched:** 2026-05-17

---

## 1. Core idea

Voyager (Wang et al., NVIDIA + Caltech + UT Austin, May 2023) was the first agent to demonstrate genuine *lifelong, self-curricular* learning powered by an LLM. Dropped into Minecraft with no objective, no game knowledge, and only the ability to write JavaScript code that drives the game, Voyager *invented its own tasks*, *wrote code to solve them*, *verified the code worked*, and *added the successful programs to a growing skill library* it could reuse forever.

The core loop — propose next task → write code → execute → check → store as skill if successful, reflect-and-retry if not — is the closest thing the field has to a working template for an agent that *grows* over its lifetime rather than running a fixed policy forever. For Runa, this matters because Runa is by design lifelong, and the question of "how does she acquire new capabilities over time without re-training" needs an answer. Voyager's answer — *write small skills, library them, reuse and compose* — is the most concrete one we have.

## 2. Technical depth

Voyager has three coupled components:

**1. Automatic curriculum.** A separate LLM (the "curriculum agent") proposes the next task based on:
- The current state of the world (inventory, surroundings, time of day).
- The agent's skill library (what it can already do).
- A "novelty" pressure (try things you haven't tried).

Example proposed tasks: "obtain wood from a tree", "craft a wooden pickaxe", "find iron ore". The curriculum is *adaptive* — it picks tasks that are *just hard enough* given current skills (the zone of proximal development).

**2. Skill library.** A growing collection of named, parameterised programs:

```
skill: chop_wood(amount=10)
  - find nearest tree
  - move to tree
  - mine wood until amount reached
  - return inventory delta

skill: smelt_iron(amount=5, fuel='coal')
  - check furnace exists; if not, craft furnace
  - check inventory has iron ore and fuel
  - place items in furnace
  - wait until smelting complete
```

Each skill is stored as both code and an embedded description (for retrieval). When proposing a new task, the curriculum agent searches the library for relevant prior skills and composes them.

**3. Iterative prompting with self-verification.** When writing code for a new task:

```
[1] Generate code.
[2] Execute in Minecraft.
[3] Inspect the game state — did the task succeed?
    - If yes: store the code as a new skill.
    - If no: feed the error / state-mismatch back into the prompt
             and try again, up to a max of 4 attempts.
```

The self-verification step (step 3) is what distinguishes Voyager from "LLM writes code, run it, hope" — the model gets honest feedback from the world and refines.

**Compositionality** is the key emergent property: each new skill *uses* prior skills. By the end of a run, Voyager has skills that call dozens of prior skills, building competence the way humans build competence.

## 3. Key works

- **Wang, Xie, Jiang, Mandlekar, Xiao, Zhu, Fan, Anandkumar. "Voyager: An Open-Ended Embodied Agent with Large Language Models."** NVIDIA + UT Austin + Caltech, arXiv:2305.16291, May 2023.
- **Park et al. "Generative Agents."** arXiv:2304.03442 — contemporaneous open-ended agent work.
- **Du et al. "Guiding Pretraining in Reinforcement Learning with Large Language Models."** arXiv:2302.06692 — earlier LLM-as-curriculum work.
- **Eureka** (Ma et al., NVIDIA, arXiv:2310.12931, 2023) — LLM-designed reward functions; pairs naturally with Voyager-style skill learning.
- **GITM** (Zhu et al., 2023) — another Minecraft agent using LLM with goal decomposition.
- **DEPS** (Wang et al., 2023) — describe-explain-plan-select; structured planning in Minecraft.

## 4. Empirical results

- Voyager (with GPT-4) discovered *significantly more* item types than baselines in the same time budget — by a factor of 3-15× depending on baseline.
- Voyager covered the Minecraft "tech tree" (wood → stone → iron → diamond) faster and more reliably than ReAct, Reflexion, and AutoGPT baselines.
- **Skill library compositionality:** quantified by counting how many prior skills each new skill called — averaged 1-3 prior-skill calls per new skill by mid-run, growing over time. Demonstrably compositional, not just additive.
- **The curriculum is critical:** ablating the automatic curriculum (replacing with random or fixed tasks) cut performance by half-or-more. The right next-task is harder to choose than the right code-for-task.
- **GPT-4 was important.** Earlier / smaller models in the same harness produced syntactically valid but semantically broken code far more often, breaking the lifelong-learning loop. The technique benefits substantially from a strong code model.
- **Transferability:** skills learned in one Minecraft world transferred cleanly to other worlds — the skill library is a portable artefact.

## 5. Applicability to Runa

This is the closest published template for a key Runa question: *how does Runa acquire new capabilities over her lifetime?*

For **Smiðja (tool forge) + skills registry**:

- The skill registry is the analogue of Voyager's skill library. Each skill has a name, a parameterised interface, an implementation, and an embedding description.
- New skills can be acquired in two ways:
  - **Volmarr-authored** (the normal path).
  - **Runa-authored via Voyager-style learning** (the lifelong path). When Runa repeatedly hits a task that doesn't fit any existing skill, Völundr can be asked to *synthesise a new skill* from the pattern of attempts.
- Skill verification before promotion to library: run on a test fixture, require success. A skill that fails verification stays in a "candidate" pool.

For **Hirð / Skuld**:

- Skuld is the natural place for a self-proposed task queue. The "curriculum" for Runa is mostly Volmarr-driven (Volmarr asks Runa to do things), but a background process can propose *novelty* tasks — "learn to use this new MCP server", "explore this corner of the filesystem", "summarise the day's emails". Run during quiet windows.

For **Hirð / Völundr (codegen)**:

- Völundr is the natural retainer to *write* new skills (Voyager's code-generation role). Iterative prompting with self-verification — exactly Voyager's loop — fits Völundr's specialty.

For **Eir**:

- Eir maintains skill health: detects skills that fail in the field, attempts repair (regenerate with newer model, patch around environment changes), demotes irreparable skills.

What to avoid:

- Don't let Runa silently install new skills without Volmarr's awareness. Voyager-discovered skills should be *proposed* to Volmarr (via Notified or a queued review) before becoming first-class. Standing-trust applies to *using* existing skills, not to *adding new* capabilities.
- Don't allow self-rewriting of existing skills. New skills can be added; existing skills are versioned and immutable.
- Don't run the self-curricular loop without bounds. Cap proposed-tasks per day, cap context spent on it, cap any tool's call-rate.
- Don't rely on a single code-generation model. Multiple models with cross-verification ([[33-model-routing-ensembles]]) catch each other's mistakes.

## 6. Open questions

- **The "Minecraft" of Runa.** Voyager succeeded partly because Minecraft is a closed, well-defined sandbox. Runa's world is the operating system + the internet + chat platforms — much messier. What's the equivalent of "the agent's environment" for lifelong learning at the OS level?
- **Skill bloat.** Over a year, Runa might accumulate thousands of self-generated skills. Pruning, generalising, and merging them is unsolved.
- **Safety of self-extended capability.** A self-generated skill that accidentally rm-rf's `~/.runa/` is a real failure mode. Sandbox + verification + Volmarr-review gating are partial answers.
- **Cross-agent skill sharing.** If Sigrid (VGSK), Runa, and other Volmarr-AIs each Voyager-style learn skills, should those libraries cross-pollinate? Promising; hard.

## 7. References (curated)

- arXiv:2305.16291 — Voyager paper.
- voyager.minedojo.org — Voyager project site.
- arXiv:2310.12931 — Eureka (related, reward-design).
- arXiv:2302.06692 — Du et al., LLM-as-curriculum.
- arXiv:2305.17144 — GITM (related Minecraft agent).
- Companion docs: [[09-react-reasoning-acting]] (the per-skill loop), [[10-reflexion-self-criticism]] (failure-driven refinement), [[45-continual-learning]] (the weight-update alternative), [[47-self-play-curricula]].
