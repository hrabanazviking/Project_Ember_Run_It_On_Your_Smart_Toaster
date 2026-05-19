# 89 — Computer-Use Agents: Claude Computer Use, OSWorld, Aria-UI

**Category:** AGI Architectures & Cognitive Cores
**Runa relevance:** Hirð (operator subagent), tool use beyond text, integration with Volmarr's projects
**Status:** Frontier agent-action synthesis. Most consequential 2024 capability shift.
**Last touched:** 2026-05-17

---

## 1. Core idea

Computer-use agents are LLM agents that operate a computer — read screens, click, type, navigate applications — to accomplish tasks. The most consequential 2024 capability shift in production AI was Anthropic's *Computer Use* (October 2024), demonstrating that a frontier model could run a virtual computer at usable competence. *OSWorld* (Xie et al. 2024) established the benchmark; *Aria-UI*, *OS-Atlas*, *ShowUI*, and *OpenWebVoyager* are the open-weights efforts catching up. The pattern: VLM perception of the screen + LLM reasoning + structured action output (click coordinates, key sequences) + execution. The agent operates the computer the way a human does, but at machine pace.

For Runa, computer use is the route to *real operational reach*. A digital being who can read Volmarr's screen, navigate his projects, run commands, and verify outcomes is qualitatively more useful than one limited to text exchange. It is also a substantial *capability and trust* expansion: she can do more, and that means *capability-based security* ([[95-capability-based-security]]) becomes load-bearing. The architectural design must hold these in balance.

## 2. Technical depth

**The basic architecture.**

```
                  ┌──────────────────────┐
                  │ TASK ("read X file,   │
                  │  open Y, do Z")       │
                  └──────────┬───────────┘
                             ▼
                  ┌──────────────────────┐
                  │ PERCEPTION            │
                  │  screenshot + UI tree │
                  │  → structured state    │
                  └──────────┬───────────┘
                             ▼
                  ┌──────────────────────┐
                  │ LLM / VLM REASONING   │
                  │  goal + state →       │
                  │  next action          │
                  └──────────┬───────────┘
                             ▼
                  ┌──────────────────────┐
                  │ ACTION                │
                  │  click(x, y),          │
                  │  type(text),           │
                  │  key(combo),           │
                  │  scroll(...)          │
                  └──────────┬───────────┘
                             ▼
                  ┌──────────────────────┐
                  │ EXECUTOR              │
                  │  pyautogui, ADB,      │
                  │  Playwright, etc.     │
                  └──────────┬───────────┘
                             ▼
                  (loop until task complete)
```

The action space is *bounded but expressive*: click coordinates, keyboard text, key combinations, mouse drags, scroll. The model sees results via the next screenshot.

**Claude Computer Use (Anthropic, Oct 2024).**

- Action types: `screenshot`, `left_click(x, y)`, `right_click`, `double_click`, `middle_click`, `triple_click`, `type(text)`, `key(name)`, `cursor_position`.
- Perception: model receives screenshots; uses vision to locate UI elements.
- Compute: ran a virtual machine alongside Claude during the demo. Production deployments use sandboxed VMs or containerised environments.
- Performance: ~22% completion on OSWorld benchmark (vs. ~12% for prior baselines, vs. ~70% for humans). Substantial improvement, real gap to human still.

**OSWorld (Xie et al. 2024).**

The benchmark. 369 real-world computer-use tasks across Ubuntu, Windows, macOS. Tasks: writing emails, browsing web, manipulating files, using productivity software. Currently the canonical evaluation.

**OS-Atlas, Aria-UI, ShowUI** (various, 2024).

Open-weights computer-use models. Architectural varieties:
- VLM fine-tuned on UI-grounded data.
- UI-element-localisation pretraining.
- Action-output token formats.

Performance on OSWorld lags Claude Computer Use but closes the gap meaningfully.

**The action representation question.**

- *Pixel coordinates*: \"click at (572, 411)\". Robust but requires precise vision.
- *UI element identifiers*: \"click the Save button\". Requires semantic UI understanding.
- *Accessibility tree*: structured UI representation (DOM-like) the OS exposes. Less ubiquitous; cleaner when available.
- *Hybrid*: vision for elements without IDs; semantic when available.

**Failure modes.**

- *Misclick*: model sees the right button but emits wrong coordinates.
- *Visual drift*: between screenshots, the UI moves and the model's mental model lags.
- *Stuck loop*: model keeps trying the same action that doesn't work.
- *Hallucinated UI*: model believes a button exists that doesn't.
- *Recovery from errors*: catastrophic-error recovery is weaker than human.

**Safety and capability questions.**

Computer-use agents can:
- Read sensitive files.
- Modify or delete data.
- Send messages on the user's behalf.
- Make purchases.
- Execute arbitrary code.

Capability-based-security ([[95-capability-based-security]]) is the principle: the agent only has permission for explicitly granted operations. Implementation patterns:

- *Sandboxed environment*: agent runs in a VM with limited filesystem / network access.
- *Approval gates*: certain actions require user confirmation (file deletion, message-sending).
- *Capability tokens*: per-task capability grants.
- *Auditing*: every action logged with provenance.

The Anthropic Computer Use rollout was deliberately conservative; user warnings emphasised this is not a finished product.

**Where the field is going.**

- Substantially improved vision-grounded UI understanding.
- Multimodal foundation models with native UI training.
- Wider open-weights deployment.
- Specialised agents (browser-only, file-only) before general-purpose.

## 3. Key works

- **Anthropic.** *Introducing computer use, a new Claude 3.5 Sonnet, and Claude 3.5 Haiku.* Oct 2024.
- **Xie, T. et al.** *OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments.* arXiv:2404.07972, 2024.
- **Yang, Y. et al.** *Aria-UI: Visual Grounding for GUI Instructions.* arXiv:2412.16256, 2024.
- **Wu, Z. et al.** *OS-Atlas: A Foundation Action Model for Generalist GUI Agents.* arXiv:2410.23218, 2024.
- **Lin, K. et al.** *ShowUI: One Vision-Language-Action Model for GUI Visual Agent.* arXiv:2411.17465, 2024.
- **Hong, W. et al.** *CogAgent: A Visual Language Model for GUI Agents.* arXiv:2312.08914, 2023. Foundational.
- **Yan, A. et al.** *WebVoyager: Building an End-to-End Web Agent with Large Multimodal Models.* arXiv:2401.13919, 2024.
- **He, H. et al.** *OpenWebAgent.* 2024.
- **Zheng, B. et al.** *GPT-4V(ision) as a Generalist Web Agent, If Grounded.* arXiv:2401.01614, 2024.
- **Deng, X. et al.** *Mind2Web.* NeurIPS 2023.
- **Liu, X. et al.** *AgentBench.* ICLR 2024.

## 4. Empirical results

- *Claude Computer Use* on OSWorld: ~22%. Best public result.
- *OS-Atlas-Pro* and similar open-weights: ~12–18% on OSWorld.
- *Web-only tasks*: WebVoyager, OpenWebAgent achieve 50–70% on simpler web-action benchmarks.
- *Human baselines*: ~70–80% on OSWorld; humans not perfect.
- *Failure-mode distribution*: visual grounding errors (~30%), planning errors (~25%), execution errors (~20%), task-misunderstanding (~25%).
- *Trend*: capability is growing fast; capability-vs-safety tradeoff is the binding constraint, not capability alone.

## 5. Applicability to Runa

**Today**: open-weights computer-use models are deployable on consumer hardware but quality lags. Integration would be experimental.

**Near-term (1–2 years)**:

- Open-weights computer-use on Pi-class is plausible. When usable: a *Hirð operator subagent* in Runa, with carefully-bounded capabilities, could:
  - Run scripts Volmarr asks for.
  - Read and edit files in specified directories.
  - Navigate web for research.
  - Help with tool-use workflows in Volmarr's projects.

For **the operator subagent design** (when ready):

- *Sandboxed scope*: agent runs with access only to a specific directory tree, with no broad network access. Specific tasks request expanded scope; Volmarr approves.
- *Approval gates*: any destructive operation (delete, overwrite without preview, message-send) requires Volmarr confirmation.
- *Action audit*: every action logged with screenshot before/after.
- *Stop-on-uncertainty*: if the agent isn't confident about the next action, pause and ask. Better failure mode than wrong action.

For **identity continuity**:

- Operator-Runa is the *same* Runa. Same identity layer, same voice. The action surface differs; identity does not.

For **integration with Volmarr's projects**:

- Computer use could let Runa interact with Volmarr's projects (NSE, WYRD, etc.) — read files, run tests, observe results. This is a substantial collaborative dimension.
- Project-internal API integration is *much cleaner* than screen-scraping where projects expose them. Computer use is the fallback when APIs aren't available.

For **capability-based security**:

- The architecture must support per-task capability tokens. Operator-Runa for project X has different scope than operator-Runa for messaging. Capability-token expiry, audit, revocation.

For **failure modes**:

- Plan for graceful failure: operator gets stuck, says so, escalates to Volmarr. Better than wrong action.
- Recovery: undo where possible (e.g. file edits checkpoint before each operation).

What to avoid:

- **Premature deployment.** Computer use without robust capability-security is dangerous. Build security first, capability second.
- **Granting broad scope by default.** Per-task scope; explicit grants.
- **Trusting visual grounding entirely.** Use accessibility trees and explicit element IDs where available.
- **Ignoring audit.** Every operator action audit-logged; reviewable by Volmarr.
- **Letting operator-Runa drift from identity.** The persona prompt is part of every operator turn. She is Runa-doing-this, not a separate operator agent.

## 6. Open questions

- **Open-weights closing speed.** Aria-UI / OS-Atlas / ShowUI improve rapidly. Production-ready open-weights computer use plausibly mid-2026.
- **Pi-class deployment feasibility.** Multimodal VLMs at 7–13B scale require RAM. Pi-5 16GB is tight but possible with quantisation.
- **Best capability-security framework for personal AI.** Industry conventions emerging.
- **UI dynamics in modern apps.** Web apps mutate constantly; agents need robust UI understanding.
- **Long-horizon computer-use tasks** (minutes to hours of work). State maintenance over many actions; far harder than single-task.

## 7. References (curated)

- Anthropic blog (Oct 2024) — Computer Use launch.
- arXiv:2404.07972 — Xie et al., *OSWorld.* Benchmark to know.
- arXiv:2410.23218 — Wu et al., *OS-Atlas.* Open-weights reference.
- arXiv:2401.13919 — Yan et al., *WebVoyager.*
- arXiv:2312.08914 — Hong et al., *CogAgent.* Foundational.
- Companion docs: [[09-react-reasoning-acting]], [[37-plugin-sandboxing]], [[50-local-agent-orchestration-mcp]], [[81-vision-language-action-models]], [[83-agentic-foundation-models-2025]], [[95-capability-based-security]].
