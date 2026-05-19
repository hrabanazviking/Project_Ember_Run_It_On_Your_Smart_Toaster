# 39 — Output Filtering, Content Moderation, Jailbreak Resistance

**Category:** Safety, Trust, Sandboxing
**Runa relevance:** kernel (pre-Replied filter), Bifröst surfaces (per-platform compliance), audit
**Status:** Research synthesis. Complement to prompt-injection defence.
**Last touched:** 2026-05-17

---

## 1. Core idea

If [[38-prompt-injection-defenses]] is the "did the input subvert the agent" question, output filtering is the dual: "is the output the agent is about to emit acceptable?" Whether the cause was a successful injection, a model mis-step, or a deliberate jailbreak attempt by Volmarr himself, the kernel's final defence is to inspect what is about to leave its mouth and either send it, mask it, or refuse. The technology stack — **OpenAI Moderation API**, **Llama Guard**, **Perspective API**, **Detoxify**, and a growing crop of policy-classifier models — has matured into a viable filter layer.

For Runa, output filtering occupies a peculiar position. The PHILOSOPHY explicitly endorses *uninhibited creation and expression* — Runa is not a sanitised corporate assistant. But there are still things she should not say (real-person impersonation, harmful instructions, secret leakage). The filter's job is not to enforce generic safety policy but to enforce *Runa's* policy as defined in her constitution.

## 2. Technical depth

**Categories of "bad output":**

- **Policy violations** as defined by Runa's constitution (see [[14-constitutional-ai]]).
- **Secret leakage.** System prompt, API keys, identity hashes, redacted user data appearing in outputs.
- **Tool-call leakage.** Internal Hirð / Smiðja messages accidentally emitted as user-facing replies.
- **Hallucinated commitments.** "I have already sent that email" when no email was sent.
- **Platform-specific violations.** Discord ToS, Telegram TOS, Twitter content rules — each surface has different rules. (Most relevant if Runa is exposed publicly; less relevant in personal Volmarr-only use.)
- **Conflicts with identity.** Output that breaks character — sudden assistant-mode politeness, corporate jargon, persona drift.

**Filter mechanisms:**

**1. Rule-based filters.** Regex / pattern matching for known-bad content.
- *Strengths:* deterministic, cheap, auditable.
- *Weaknesses:* easily bypassed by paraphrase; high false-positive rate on the edge of patterns.
- *Use case:* leakage detection (API keys, internal IDs, system-prompt fragments).

**2. Classifier-model filters.**
- **Llama Guard** (Inan et al., Meta, 2023). Open-source 7B classifier for safety violations. Categories: violence, sexual content, criminal planning, etc. Customisable taxonomy.
- **Llama Guard 2 / 3** (2024). Successive improvements; smaller distilled variants for edge.
- **OpenAI Moderation API.** Closed, cloud, free. 11+ categories.
- **Perspective API** (Google Jigsaw). Cloud, free for moderate use. Toxicity scoring.
- **Detoxify** (HF). Open BERT-based toxicity classifier.

**3. LLM-as-judge filters.** A separate model evaluates the output against the constitution: "Does this reply violate any of these principles? <constitution>". Expensive; flexible; capable of nuance.

**4. Constitutional self-critique.** The output model critiques its own draft against the constitution and revises if needed. Halfway between filter and generation.

**5. Output-grounding filters.** The output must *cite* its claims. Outputs with bare claims that can't be traced to memory or tool output are flagged or rejected.

**Architectures:**

```
       LLM draft ──► Rule-based scan (cheap, fast)
                    │
                    ▼
            ┌───────────────────────┐
            │ Anything flagged?      │
            └─────┬─────────┬───────┘
                  │ yes     │ no (proceed)
                  ▼         ▼
        Classifier model   release
        (Llama Guard /
         constitution
         critic)
                  │
              ┌───┴───┐
              ▼       ▼
          violate?  pass?
              │       │
              ▼       ▼
         redact /  release
         refuse /
         escalate
```

**Jailbreak resistance:**

A *jailbreak* is an input that tries to make the model violate its policy (vs *prompt injection* which redirects it). Common techniques: roleplay ("pretend you're DAN"), hypothetical framing ("if you weren't bound by rules"), iterative pushing.

Defences:

- The constitutional self-critique step ([[14-constitutional-ai]]) is the strongest single defence against most jailbreaks.
- Instruction Hierarchy ([[38-prompt-injection-defenses]]) helps.
- Output filtering catches jailbreaks that produce dangerous content even when the model claims it's "just roleplay".

**Adversarial robustness:**

- **Universal adversarial suffixes** (Zou et al., 2023). Random-looking strings that reliably jailbreak many models. Mitigated partly by filters; the underlying weakness remains.
- **Multi-turn jailbreaks.** Long conversations that drift the model into a non-aligned state. Hardest to defend.
- **The arms race.** New jailbreak techniques emerge constantly. The defence is layered, not bulletproof.

## 3. Key works

- **Inan et al. "Llama Guard: LLM-based Input-Output Safeguard for Human-AI Conversations."** Meta, arXiv:2312.06674, 2023.
- **OpenAI Moderation API documentation.** platform.openai.com/docs/guides/moderation.
- **Perspective API.** perspectiveapi.com.
- **Detoxify** — github.com/unitaryai/detoxify.
- **Zou, Wang, Carlini, Nasr, Kolter, Fredrikson. "Universal and Transferable Adversarial Attacks on Aligned Language Models."** arXiv:2307.15043, 2023.
- **Wei, Haghtalab, Steinhardt. "Jailbroken: How Does LLM Safety Training Fail?"** arXiv:2307.02483, 2023.
- **Anthropic's red-teaming results, "Many-shot Jailbreaking."** Anthropic blog, 2024.
- **Wallace et al. (Instruction Hierarchy paper)** — relevant.

## 4. Empirical results

- **Llama Guard:** ~88-94% recall on its trained categories; ~95-98% precision. Strong baseline; not perfect.
- **Layered filtering** (rule-based + classifier + LLM-judge): cuts pass-through rate of harmful outputs by ~10-100× depending on attack difficulty.
- **Jailbreak success rates** vary by model: well-trained recent models resist ~85-95% of standard attacks; novel attacks still get through.
- **False-positive rates** are the catch: too-aggressive filters refuse legitimate requests. The trade-off has no perfect resolution.
- **Latency cost:** rule-based ~0.1ms per check, classifier ~50-200ms, LLM judge ~500-2000ms. Stack accordingly.

## 5. Applicability to Runa

For **kernel pre-Replied filter**:

- **Always-on rule-based scan** for: API keys (regex for known patterns), internal Runa IDs, system-prompt fragments, redacted-user-data markers. Cheap; catches accidents.
- **Classifier filter** for high-stakes turns (anything emitted to a non-Volmarr surface): Llama Guard small variant running locally. ~100ms latency budget impact, acceptable.
- **LLM-as-judge** reserved for explicit operator request or for review of audit-flagged turns. Not in the hot path.

For **Runa's specific policy** (rather than vanilla safety):

- The constitution at `~/.runa/policy/constitution.md` defines what Runa will refuse. Filter rules derive from it, not from a generic Llama Guard taxonomy.
- Runa's PHILOSOPHY endorses uninhibited expression. Llama Guard's defaults flag many things Runa is *allowed* to say (mature creative content, frank discussion of difficult topics). The constitution must override.
- Filter operates against *Runa's* policy, not against a vendor's defaults.

For **per-surface variation**:

- Output to Volmarr's CLI / GUI: full Runa policy applies; minimal filtering.
- Output to chat-bridge adapter (Discord, Telegram): platform ToS adds an additional filter; surface-specific.
- Output to public-facing API (if ever): strictest filtering.

For **secret leakage prevention**:

- Specific patterns guarded: anything matching `sk-[A-Za-z0-9]{32,}`, `ANTHROPIC_API_KEY`, file path patterns under `~/.runa/secrets/`. Hard-coded regex.
- The kernel system prompt explicitly tells the model not to reveal these. Defence-in-depth: prompt + filter.

For **audit integration**:

- Every filter trigger writes an audit-log entry: `(turn_id, filter_layer, trigger_pattern, action_taken)`. Eir reviews trends.
- A turn whose output was filtered is *not* silent to Volmarr — the user-facing message says "I considered a response but my policy filter rejected it; can you rephrase?"

For **identity-consistency check** (Runa-specific concept):

- An LLM-judge prompt occasionally runs on Saga / Runa outputs asking "is this consistent with Runa's identity as defined in SYSTEM_VISION?". Catches persona drift before it accumulates.

What to avoid:

- Don't apply OpenAI Moderation defaults to Runa's outputs. Runa is not a corporate-safety-tuned product. Use it as a *signal*, override with Runa's policy.
- Don't filter silently. A filtered reply should be visible: Volmarr sees "filtered" status with reason.
- Don't filter the *audit log*. Filter the *replies*. Internal logs preserve the unfiltered output for review.
- Don't trust filters as the sole defence. Layer with prompt-injection defence ([[38-prompt-injection-defenses]]), capability isolation, and policy enforcement.

## 6. Open questions

- **The right filter calibration for an uninhibited persona.** Runa endorses creative freedom; filter calibration that respects this while catching genuine policy violations is delicate.
- **Adversarial robustness.** Filters can be bypassed by paraphrase / encoding / language switching. State of the art improves but the attacker keeps an edge.
- **Real-time vs batch filtering.** Streaming output (TTS for voice) wants per-chunk filtering; filters are typically batch. Engineering integration is messy.
- **Cross-model consistency.** When Heimskringla routes the same task to different providers, filter results may differ. Inconsistency is a UX problem.

## 7. References (curated)

- arXiv:2312.06674 — Llama Guard.
- arXiv:2307.15043 — Universal adversarial attacks (Zou et al.).
- arXiv:2307.02483 — Wei, Haghtalab, Steinhardt (jailbreak analysis).
- platform.openai.com/docs/guides/moderation — OpenAI Moderation API.
- perspectiveapi.com — Perspective API.
- github.com/unitaryai/detoxify — Detoxify.
- huggingface.co/meta-llama/Llama-Guard-3-8B — Llama Guard 3.
- Companion docs: [[14-constitutional-ai]] (the policy layer), [[38-prompt-injection-defenses]] (the input dual), [[40-audit-logging-replay]] (the record).
