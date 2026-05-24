---
codex_id: PEER_REVISIONS
title: Peer Revisions — Pinned SHAs, Tags, and Reproduction
role: Scribe
layer: Meta
peer_targets: [Letta, smolagents, Goose]
status: complete
peer_source_refs: []
ember_subsystem_targets: []
hermes_codex_refs: [meta/HERMES_REVISION]
cross_refs:
  - meta/INDEX
  - meta/MANIFEST
  - meta/SHARED_CONTEXT
  - meta/CONTINUATION_BACKLOG
---

# Peer Revisions

*The pin. Three trees, three commits, three small bundles of facts that let a future reader stand exactly where Wave 2 stood.*

A Codex that does not pin its sources is a Codex that ages into fiction. Wave 1 had one source — Hermes — and one pin file. Wave 2 has three sources, and a single pin file with three sections. The shape is the same: SHA, tag, file counts, largest files, reproduction commands, license, and a one-paragraph note on why each pin matters. If the upstream trees move between authoring and synthesis, the synthesis is still anchored.

---

## 1. Letta (`letta-ai/letta`)

### Identity
- **Upstream:** `https://github.com/letta-ai/letta.git`
- **Local clone:** `/tmp/letta`
- **Commit SHA:** `1131535716e8a31c9a437f8695e25ac98f203a24`
- **Commit subject:** *fix(security): use JSON instead of pickle for sandbox->server tool result transport (#3343)*
- **Commit timestamp:** `2026-05-14 09:58:54 -0700`
- **Tag:** `0.16.8`
- **License:** Apache License 2.0 (Letta-AI Inc.)

### Size
- **Python files:** 878
- **Python lines:** 248,417 total
- No first-class Rust or TypeScript; the `fern/` directory hosts an OpenAPI spec used to generate clients in TS/Python/Go but those are vendored artefacts, not part of Letta proper.

### Top 10 largest Python files

| Lines | Path |
|---:|---|
| 12,709 | `tests/test_managers.py` |
| 3,599 | `letta/services/agent_manager.py` |
| 3,299 | `tests/test_server_providers.py` |
| 2,717 | `tests/integration_test_send_message.py` |
| 2,710 | `letta/schemas/message.py` |
| 2,569 | `letta/server/rest_api/routers/v1/agents.py` |
| 2,537 | `tests/integration_test_turbopuffer.py` |
| 2,402 | `tests/managers/test_agent_manager.py` |
| 2,370 | `tests/managers/test_tool_manager.py` |
| 2,354 | `tests/test_sdk_client.py` |

The shape is revealing: the largest production file is `letta/services/agent_manager.py` — the *service* that owns the agent's lifecycle — and the largest single file overall is the test that exercises every Manager class. Letta has the architectural posture of a *service-oriented backend* (manager classes, service layer, REST router) more than a *library*. Half the top-10 are tests, which says good things about the rigor and bad things about the friction of vendoring the source.

### Why this pin matters
Letta v0.16.8 is the first release in which the *sandbox→server tool result transport* was migrated from `pickle` to JSON — a security-shaped commit that demonstrates Letta's posture: *agent-callable code execution exists, but its IPC must be hardened*. This single commit is itself a Wave-2 lesson for Ember: if Ember ever ships agent-callable code, the wire format is JSON, not pickle, full stop.

### Reproduction
```bash
git clone https://github.com/letta-ai/letta.git /tmp/letta
git -C /tmp/letta checkout 1131535716e8a31c9a437f8695e25ac98f203a24
# verify
git -C /tmp/letta rev-parse HEAD       # → 1131535716e8a31c9a437f8695e25ac98f203a24
git -C /tmp/letta describe --tags      # → 0.16.8
find /tmp/letta -name "*.py" | wc -l   # → 878
```

---

## 2. smolagents (`huggingface/smolagents`)

### Identity
- **Upstream:** `https://github.com/huggingface/smolagents.git`
- **Local clone:** `/tmp/smolagents`
- **Commit SHA:** `3cd5c84e7386fa8b93514cc8fd05dcda1fe44a7d`
- **Commit subject:** *Update docstring of LocalPythonExecutor (#2292)*
- **Commit timestamp:** `2026-05-19 22:32:05 +0200`
- **Tag:** `v1.0.0-921-g3cd5c84` (i.e. 921 commits past `v1.0.0`)
- **License:** Apache License 2.0 (Hugging Face)

### Size
- **Python files:** 75
- **Python lines:** 30,968 total
- No Rust, no TypeScript; the library is single-language and deliberately small.

### Top 10 largest Python files

| Lines | Path |
|---:|---|
| 2,989 | `tests/test_local_python_executor.py` |
| 2,628 | `tests/test_agents.py` |
| 2,102 | `src/smolagents/models.py` |
| 1,814 | `src/smolagents/agents.py` |
| 1,768 | `src/smolagents/local_python_executor.py` |
| 1,428 | `src/smolagents/remote_executors.py` |
| 1,422 | `src/smolagents/tools.py` |
| 1,080 | `tests/test_models.py` |
| 1,068 | `tests/test_tools.py` |
| 1,002 | `examples/open_deep_research/scripts/mdconvert.py` |

This is *the* size signal of Wave 2. smolagents fits the entire library — agents, models, tools, executors, remote executors — in ~14k production lines (the rest is tests and examples). Compare to Hermes's 871k source lines or Letta's 248k Python lines: smolagents is **roughly 12× smaller than Hermes** and **8× smaller than Letta**. The top-10 spread is also tighter; no file above 3k lines, no production file above 2,200. This is the codebase that proves the Vow of Smallness is achievable.

### Why this pin matters
The pinned commit is itself a docstring update for `LocalPythonExecutor` — the heart of smolagents's code-execution-as-action design. It signals stability: at this SHA, the executor's public contract is what it claims to be, in prose. Ember's Forge reading [[30_execution/SMOL_CODE_AS_ACTION]] can quote this docstring as canonical.

### Reproduction
```bash
git clone https://github.com/huggingface/smolagents.git /tmp/smolagents
git -C /tmp/smolagents checkout 3cd5c84e7386fa8b93514cc8fd05dcda1fe44a7d
# verify
git -C /tmp/smolagents rev-parse HEAD       # → 3cd5c84e7386fa8b93514cc8fd05dcda1fe44a7d
git -C /tmp/smolagents describe --tags      # → v1.0.0-921-g3cd5c84
find /tmp/smolagents -name "*.py" | wc -l   # → 75
```

---

## 3. Goose (`block/goose`)

### Identity
- **Upstream (canonical):** `https://github.com/block/goose.git`
- **Local clone:** `/tmp/goose`
- **Local clone's remote (as fetched):** `https://github.com/aaif-goose/goose.git` — a mirror or fork used at clone time; the SHA is identical to `block/goose` upstream at the same tag. *If reproducing, prefer the canonical `block/goose` remote.*
- **Commit SHA:** `ca26f01d3acd9871691fa8981f05d19aed9a3b82`
- **Commit subject:** *[Prompt injection mitigation] Update pattern-based detection to reduce FPs (#9350)*
- **Commit timestamp:** `2026-05-21 10:56:17 +1000`
- **Tag:** `v2.0-rc-04-27-0-262-gca26f01d3` (262 commits past `v2.0-rc-04-27`)
- **License:** Apache License 2.0 (Block, Inc.)

### Size
- **Rust files:** 433
- **TypeScript files:** 450
- **TSX files:** 663
- **Total Rust + TS + TSX lines:** 369,753

### Top 10 largest Rust files

| Lines | Path |
|---:|---|
| 4,630 | `crates/goose/src/acp/server.rs` |
| 3,457 | `crates/goose/src/providers/formats/openai.rs` |
| 2,995 | `crates/goose/src/agents/agent.rs` |
| 2,714 | `crates/goose/src/agents/extension_manager.rs` |
| 2,606 | `crates/goose/src/session/session_manager.rs` |
| 2,462 | `crates/goose/src/agents/platform_extensions/summon.rs` |
| 2,401 | `crates/goose/src/config/base.rs` |
| 2,293 | `crates/goose-cli/src/session/mod.rs` |
| 2,205 | `crates/goose-cli/src/cli.rs` |
| 2,140 | `crates/goose-cli/src/commands/configure.rs` |

### Top 5 largest TS/TSX files (desktop + evals)

| Lines | Path |
|---:|---|
| 4,771 | `ui/desktop/src/api/types.gen.ts` *(generated)* |
| 2,785 | `ui/desktop/src/main.ts` |
| 1,865 | `ui/desktop/src/components/ChatInput.tsx` |
| 1,504 | `evals/open-model-gym/suite/src/runner.ts` |
| 1,457 | `ui/goose2/src/shared/ui/ai-elements/prompt-input.tsx` |

The Goose shape: a **fat Rust core** (agent, extension manager, session manager, config) and a **substantial Electron + React desktop** on top, with **generated client types** linking the two. `crates/goose/src/acp/server.rs` at 4.6k lines is the *Agent Client Protocol* server — the Rust-side server that the desktop talks to over a local protocol. This is the cross-language frontier of Wave 2.

### Why this pin matters
The pinned commit is a prompt-injection-mitigation tweak — proof that Goose's safety surface is *actively contested ground* at the time of pin. Wave 2's Auditor reading [[50_verification/GOOSE_RISK_REGISTER]] can cite this commit as evidence that prompt-injection-as-tool-call is a live attacker, not a theoretical one. The pin also captures Goose mid-`v2.0` cycle, after the MCP-native refactor but before any nominal `v2.0` stable.

### Reproduction
```bash
git clone https://github.com/block/goose.git /tmp/goose
git -C /tmp/goose checkout ca26f01d3acd9871691fa8981f05d19aed9a3b82
# verify
git -C /tmp/goose rev-parse HEAD              # → ca26f01d3acd9871691fa8981f05d19aed9a3b82
git -C /tmp/goose describe --tags             # → v2.0-rc-04-27-0-262-gca26f01d3
find /tmp/goose -name "*.rs" | wc -l          # → 433
find /tmp/goose \( -name "*.ts" -o -name "*.tsx" \) | wc -l   # → 1113
```

---

## 4. The Triangle, in Numbers

| Codebase | Lang | Files | Lines | License | Posture |
|---|---|---:|---:|---|---|
| Hermes (Wave 1 baseline) | Python | 1,800 | 871,611 | MIT | sovereign / cloud-tethered / feature-maximalist |
| Letta | Python | 878 | 248,417 | Apache-2.0 | server-first / memory-centric / SDK-shaped |
| smolagents | Python | 75 | 30,968 | Apache-2.0 | library / code-execution / minimalist |
| Goose | Rust + TS | 433 + 1,113 | 369,753 | Apache-2.0 | local-first / MCP-native / cross-platform desktop |

Four codebases, four legitimate readings of *what an agent is*. The numbers alone tell a Vow story: smolagents proves Smallness; Goose proves Local-First-and-Cross-Platform; Letta proves Honest-Memory-Through-Schema; Hermes proves that all of these can be ignored simultaneously and the result still ships.

License note: Hermes is MIT, the three Wave-2 peers are Apache-2.0. This affects what Ember can lift verbatim if she ever chose to — Apache-2.0 carries a patent grant and requires a NOTICE file, MIT does not. The Codex itself lifts no code from any peer; only patterns. The license is recorded here so a future Forge reading [[60_synthesis/CROSSWALK_LETTA_TO_EMBER]] knows the constraint.

---

## 5. Maintenance — When to Re-Pin

The pin is correct at the moment of authoring. It becomes wrong when:

- **Letta** ships a release that materially changes the memory-block API, the agent step loop, the REST surface in `letta/server/rest_api/`, or the Manager service layer. The `0.16.8 → 0.17` step would warrant a re-pin.
- **smolagents** ships a release that changes the `CodeAgent` / `ToolCallingAgent` contract, the executor interface in `local_python_executor.py` / `remote_executors.py`, or the HF Hub tool-sharing protocol. Anything past `v1.1` warrants a re-pin.
- **Goose** ships a release that changes the ACP server contract (`crates/goose/src/acp/server.rs`), the extension manager, the recipe schema, or the MCP wire format. The `v2.0-rc → v2.0` step would warrant a re-pin.

When a re-pin happens, the Scribe:
1. Updates this file with the new SHAs, tags, line counts.
2. Preserves the old pin block (do not overwrite — append a `## Previous Pin` section).
3. Adds a one-paragraph delta in [[meta/CONTINUATION_BACKLOG]] naming which Wave-2 docs are now stale.
4. Walks [[meta/MANIFEST]] for any doc whose `peer_source_refs:` lines are now broken — those go on the backlog with status `needs-rewrite`.

---

## What This Means for Ember

The pin is plumbing, not architecture. It affects no True Name directly. The Vow it engages is **Honest Memory** at the meta-level: Ember's Codex says what it saw, with line numbers and SHAs, so that a year from now a contributor can re-derive every Wave-2 claim against the same trees. Without the pin, the Codex aged into a thing one believes; with it, the Codex remains a thing one can verify.

The proposal here is no proposal — only a discipline. Wave 3 (Substrate Layers) and beyond should follow the same shape: one section per source, SHA + tag + file counts + top-10 + reproduction + license + why-this-matters. The cost is fifteen minutes per source. The benefit is that the long memory stays honest.

A small forward note: if Wave 4 (Research Papers) ever lands, the pin form will need adapting — arXiv IDs and ACL Anthology DOIs in place of SHAs. The shape is portable; the identifiers change.

— *Eirwyn Rúnblóm, Scribe*
