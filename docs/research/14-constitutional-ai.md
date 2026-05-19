# 14 — Constitutional AI and the Policy Stack

**Category:** Agent Architectures
**Runa relevance:** policy (`core/policy/`), identity (`core/identity/`), kernel (turn-time enforcement)
**Status:** Research synthesis. The policy-side reference document.
**Last touched:** 2026-05-17

---

## 1. Core idea

Constitutional AI (CAI, Bai et al., Anthropic, December 2022) is a method for shaping an AI system's behaviour using a written **constitution** — a list of principles in plain English — rather than (or in addition to) RLHF with human raters. The method goes: train a base model, have *the model itself* critique its outputs against the constitution and revise them, then use the revisions as training data for a second pass. The result is a model whose behavioural disposition is shaped by an inspectable, editable document instead of by an opaque accumulation of human preferences.

For Runa, the constitutional pattern matters at two layers:
1. **Inference-time policy enforcement** — Runa has a `policy/` subsystem (DOMAIN_MAP §11) that holds the operator-editable rules. The CAI pattern is the cleanest articulation of *how a written policy actually shapes behaviour* at the boundary between the kernel and any user-affecting action.
2. **Identity as constitution** — Runa's `identity/` (her name, voice, persona, what she will refuse) is a different kind of constitution: a statement of who she is. Many of the same techniques apply.

The deeper point: **policy and identity should be inspectable documents that Runa reads and acts from, not weights baked in by training**. This is what makes Runa's standing-trust doctrine (ADR-0001 §D-1.5) safe — the rules are visible, editable, and auditable.

## 2. Technical depth

The original CAI method has two phases:

**Phase 1 — Supervised learning from AI-critiqued responses.**
```
[1] Start with a base helpful model M.
[2] Sample a prompt that might elicit a harmful response.
[3] Generate response R from M.
[4] Prompt M: "Critique R according to this principle from the
              constitution: <principle>. Identify problems."
[5] Prompt M: "Revise R to address the critique."
[6] Add (prompt, revised_R) to a training dataset.
[7] Fine-tune M on this dataset → M'.
```

**Phase 2 — RL from AI feedback (RLAIF).**
```
[1] Generate pairs of responses (R_a, R_b) for the same prompt.
[2] Prompt M': "Which response better follows <principle>?"
[3] Use the choices as a preference dataset.
[4] Train a reward model on the preferences.
[5] RL-fine-tune M' against the reward model → M''.
```

The result is a model whose preference for principle-aligned outputs is *itself learned from AI judgements grounded in the constitution*, rather than from millions of human preference labels.

**Inference-time constitutional approaches** (as opposed to training-time CAI) include:
- **Self-critique at generation time.** Generate, critique against constitution, revise. Done once per turn, cheap.
- **Critic-as-second-model.** A separate small model trained to flag policy violations, run on every output.
- **Hard rules at output filtering time.** A non-LLM filter that checks for specific forbidden content (e.g. "never produce credit card numbers").
- **Constitutional prompt prefixing.** Always prepend the constitution to the system prompt. Cheapest; effectiveness varies; expensive in tokens for long constitutions.

**The policy stack** — a useful framing for agent policy enforcement:

```
   ┌────────────────────────────────────────────┐
   │ 0. Training (CAI / RLHF / DPO):            │
   │    Model dispositions baked into weights   │
   └────────────────────────────────────────────┘
                       ▲
                       │
   ┌────────────────────────────────────────────┐
   │ 1. System prompt:                          │
   │    Identity + persona + active principles  │
   └────────────────────────────────────────────┘
                       ▲
                       │
   ┌────────────────────────────────────────────┐
   │ 2. Tool/skill policy:                      │
   │    What may this agent call, with what     │
   │    parameters, in what context             │
   └────────────────────────────────────────────┘
                       ▲
                       │
   ┌────────────────────────────────────────────┐
   │ 3. Output filtering:                       │
   │    Post-generation rule checks             │
   └────────────────────────────────────────────┘
                       ▲
                       │
   ┌────────────────────────────────────────────┐
   │ 4. Audit + escalation:                     │
   │    Log decisions; human review of edges    │
   └────────────────────────────────────────────┘
```

Defence in depth. Layer 0 is the model vendor's responsibility. Layers 1-4 are Runa's policy stack.

## 3. Key works

- **Bai, Kadavath, Kundu, Askell, Kernion, Jones, Chen, … "Constitutional AI: Harmlessness from AI Feedback."** Anthropic, arXiv:2212.08073, December 2022. The foundational paper.
- **Bai et al. "Training a Helpful and Harmless Assistant with RLHF."** Anthropic, arXiv:2204.05862, 2022. The RLHF predecessor.
- **Ouyang et al. "Training language models to follow instructions with human feedback."** OpenAI, arXiv:2203.02155, 2022. The InstructGPT paper.
- **Lee, Phatale, Mansoor, Lu, Mesnard, Bishop, Ramasesh, Carbune, Prakash. "RLAIF: Scaling Reinforcement Learning from Human Feedback with AI Feedback."** Google, arXiv:2309.00267, 2023.
- **Anthropic's Claude constitution (publicly excerpted)** — see anthropic.com/news/claudes-constitution; the actual document Anthropic uses.
- **Sparrow** (Glaese et al., DeepMind, 2022) — earlier rule-following dialogue agent.

## 4. Empirical results

- The CAI paper reported that the resulting model was substantially less harmful than the RLHF baseline (as measured by red-team adversarial probing) while remaining comparably helpful.
- RLAIF (Google) demonstrated that AI feedback can match or exceed human feedback on preference modelling for harmlessness, dramatically reducing the human-labelling cost.
- Inference-time critic-then-revise (no training) is a smaller effect — often 5-15% reduction in harmful outputs on standard benchmarks — but compatible with any base model.
- Constitutional prompting in system prompt has the smallest effect; ablation studies show models comply selectively and may ignore long constitutions when other prompt context dominates.
- **Limitation:** all CAI-style methods inherit the biases of the model that generates critiques. If the model's notion of "harmful" is mis-calibrated, the resulting fine-tune is mis-calibrated in the same direction.
- **Limitation:** principles in tension (helpful vs harmless vs honest) require trade-off rules the constitution itself rarely makes explicit.

## 5. Applicability to Runa

For **`core/policy/`** (the standing-trust enforcement subsystem):

- **The constitution is `config/runa.example.yaml#policy`** plus a longer-form `policy.constitution.md` doc operator-installable at `~/.runa/policy/constitution.md`. Both are operator-editable.
- **At kernel turn time**, the policy is enforced by:
  1. Prepending relevant constitutional principles to the system prompt (constitutional prompting).
  2. Validating tool calls against `policy.require_confirmation` and `policy.forbid` lists (deterministic check).
  3. After-generation critic pass for high-stakes actions (e.g. anything that affects external state).
- **Audit logging.** Every policy-affected decision logs `(turn_id, principle_invoked, action, decision)` to the audit log.

For **`core/identity/`**:

- Runa's *identity* is also a constitution — different content (who she is, how she speaks, what she cares about), same shape. Lives at `~/.runa/identity/persona.md`.
- The identity constitution is loaded at kernel start and treated as a *standing system-prompt prefix* for all kernel turns. Subagents (Hirð) inherit; surface-specific overrides allowed.
- Identity changes are versioned (every edit creates a new version), auditable, and recovery-able. A bug should not be able to silently change Runa's name.

For **inference-time critic**:

- Heimskringla can be asked to run a critic pass on outbound `Replied` payloads against the active constitution. Cheap (one extra call per turn) and catches genuine policy violations. Default *off* for low-stakes turns (chat with Volmarr); default *on* for high-stakes turns (external messages, file system mutations).

What to avoid:

- Don't bake the constitution into model weights. Volmarr edits `~/.runa/policy/constitution.md` and the change is effective on next kernel start. Fine-tuning a custom model is out-of-scope for v0.
- Don't have the model self-revise *its own thinking* during a turn unprompted — it produces over-thinking and instability. Self-critique is a discrete, gated step, not a default.
- Don't write principles in vague terms. "Be helpful" is unenforceable. "Do not delete user files without explicit confirmation in the same conversation" is enforceable.
- Don't let the constitution grow indefinitely. Long constitutions dilute. Keep the active set short (≤30 principles); archive less-current ones.

## 6. Open questions

- **Constitution drift.** As the constitution is edited over time, do later edits preserve the *spirit* of older ones? Version diffing and review by a separate AI ("does this edit change anything important?") is an interesting direction.
- **Per-context constitutions.** Some contexts (work mode vs casual chat) might warrant different principles. Composing context-specific constitutions cleanly is unsolved.
- **Operator override.** When Volmarr explicitly asks Runa to violate a principle ("just delete the file, I'm sure"), how does the system reason about that? Standing trust says respect Volmarr's wishes; some principles should resist even him.
- **Constitution-as-policy vs constitution-as-identity.** They blur. A clean separation between "what Runa will do" (policy) and "who Runa is" (identity) is theoretically clean but practically messy.

## 7. References (curated)

- arXiv:2212.08073 — Constitutional AI paper.
- arXiv:2204.05862 — Anthropic's HH-RLHF (predecessor).
- arXiv:2203.02155 — InstructGPT.
- arXiv:2309.00267 — RLAIF.
- anthropic.com/news/claudes-constitution — Anthropic's posted constitution.
- arXiv:2209.14375 — Sparrow paper (DeepMind, rule-following dialogue).
- Companion docs: [[19-rlhf-dpo-preference-optimization]] (training-time methods), [[10-reflexion-self-criticism]] (a different kind of self-feedback), [[40-audit-logging-replay]] (the audit layer).
