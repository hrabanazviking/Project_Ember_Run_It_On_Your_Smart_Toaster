# 01 — MemGPT and OS-style Memory Hierarchies for LLMs

**Category:** Memory & Knowledge Storage
**Runa relevance:** Muninn (memory OS), kernel (context management), Heimskringla (model-call shaping)
**Status:** Research synthesis. Concept reference, not implementation spec.
**Last touched:** 2026-05-17

---

## 1. Core idea

MemGPT (Packer et al., UC Berkeley, late 2023) reframes the LLM context window as if it were the main memory of a virtual operating system. The LLM is the CPU. The context window is RAM. Everything else — vector stores, document stores, prior conversations — is "disk." A small kernel of system code teaches the LLM to *use its own memory* through function calls: it can read pages in, write pages out, search external memory, and edit its own working set.

The shift is from passive context-stuffing ("how much can I cram into the prompt?") to active memory management ("the model knows what it knows and pulls what it needs"). It is the cleanest articulation of why agent memory is an *architecture* problem rather than a context-length problem.

## 2. Technical depth

MemGPT proposes three logical tiers:

```
┌────────────────────────────────────────────────────────────────┐
│  Main context (LLM context window)                             │
│  ┌──────────────┬─────────────────┬───────────────────────────┐│
│  │ System       │ Working context │ FIFO message queue        ││
│  │ instructions │ (persistent     │ (most recent turns)       ││
│  │              │  scratchpad)    │                           ││
│  └──────────────┴─────────────────┴───────────────────────────┘│
└─────────────────────────────────┬──────────────────────────────┘
                                  │ function calls
              ┌───────────────────┴────────────────────┐
              │                                        │
              ▼                                        ▼
   ┌────────────────────┐                  ┌────────────────────┐
   │  Recall storage    │                  │  Archival storage  │
   │  (full chat history,│                  │ (semantic, vector- │
   │   queryable)        │                  │  indexed memories) │
   └────────────────────┘                  └────────────────────┘
```

Key function-call primitives the LLM is taught to use:

- `core_memory_append(section, text)` / `core_memory_replace(section, old, new)` — edit the persistent scratchpad.
- `recall_storage_search(query)` — full-text search across stored conversation history.
- `archival_storage_insert(text)` / `archival_storage_search(query)` — write to / read from the long-term semantic store.
- `send_message(text)` — emit a reply to the user.

The "pager" loop: when context fills (or events warrant), the system prompts the LLM to flush less-relevant content from the working set into archival storage, write summaries into the persistent scratchpad, and pull in newly-relevant context. Crucially, *the LLM decides what to swap*, guided by system prompts that explain the memory hierarchy as if explaining a real OS to it.

Conceptually the same family of ideas as virtual memory pagers (working set theory, Denning 1968), but with the policy implemented in natural language and executed by a language model rather than a kernel.

## 3. Key works

- **Packer, Wooders, Lin, Fang, Patil, Stoica, Gonzalez. "MemGPT: Towards LLMs as Operating Systems."** arXiv:2310.08560, October 2023. The seminal paper.
- **Letta** (formerly MemGPT framework) — the open-source production implementation, maintained by the original team at letta.ai. By 2025 it had broadened from "MemGPT" the technique into a more general agent-memory platform.
- **Generative Agents** (Park et al., Stanford + Google, April 2023, arXiv:2304.03442) — predates MemGPT and inspired some of the reflection / summarisation patterns, though using a different memory shape.
- **HippoRAG** (Gutiérrez, Shu, Gu, Yasunaga, Su, 2024) — neuroscience-inspired memory that complements MemGPT's OS framing with a personalised-PageRank index over a knowledge graph.

## 4. Empirical results

- MemGPT outperformed fixed-context baselines on multi-document QA and long conversation tasks at the time (against GPT-4 with finite context). The biggest wins were on conversations where critical context was old enough to have fallen out of vanilla context windows.
- Long-context models (Claude 200K, Gemini 1M+, GPT-4 128K) closed some of the gap purely by holding more in RAM. But on tasks that genuinely span sessions / weeks / months, OS-style memory still wins — the question stopped being "fit in context" and became "find the right thing fast".
- A persistent open issue: the LLM is not a reliable memory manager. It forgets to call `archival_storage_insert` when it should, summarises imperfectly, and occasionally fabricates memories. Production deployments combine MemGPT-style function calls with deterministic write triggers ("every N turns, flush") and human-in-the-loop review of long-term memories.

## 5. Applicability to Runa

This research is directly load-bearing for **Muninn** (`core/memory/`). Specifically:

- The **three-tier shape** (working scratchpad, recall, archival) maps almost 1:1 to Muninn's planned structure: identity-and-persona-scratchpad, recent episodes, semantic archival.
- The **LLM-as-memory-manager** pattern is appropriate for Runa's standing-trust doctrine: Runa decides what to remember, rather than asking permission for each write.
- The **function-call vocabulary** is a strong default for the skill contract — Muninn should expose `core_memory_append`, `recall_search`, `archival_insert`, `archival_search` as skills the kernel always has available.
- The **OS framing** matches the project's "files on disk an operator can see" doctrine (ARCHITECTURE §4.3). Tiers map to filesystem layout under `~/.runa/memory/`.

What to avoid:

- Don't let the LLM be the *only* writer. Combine with deterministic triggers (after every conversation turn, append the episode whether or not the LLM remembered to).
- Don't trust the LLM's summarisation as the canonical record. Keep raw transcripts in `recall_storage`; summaries live in `archival_storage` as a derived layer.
- Don't expose archival writes as a single unbounded `text` field. Episodes have structure (speaker, time, location, conversation_id) — preserve that structure in the schema so retrieval can filter by it.

## 6. Open questions

- **Memory consolidation timing.** When should working-context summaries get promoted to archival? Current systems use fixed thresholds; sleep-replay-inspired schedules ([[44-sleep-replay-memory-consolidation]]) are an active research direction.
- **Self-editing safety.** A model that can edit its own working scratchpad can drift its own behaviour. Versioning + diff-review is a partial answer; full solution unclear.
- **Cross-agent memory.** When Runa has subagents (Hirð), do they share Muninn or have private memories that publish to Muninn? MemGPT was designed for one agent.
- **Memory provenance.** If a recalled memory turns out to be wrong, where did it come from? Tracking causation through summarisation passes is hard.

## 7. References (curated)

- arXiv:2310.08560 — MemGPT paper.
- arXiv:2304.03442 — Generative Agents (Park et al.).
- arXiv:2405.14831 — HippoRAG.
- letta.ai — production framework (MemGPT successor).
- Denning, "The Working Set Model for Program Behavior," 1968 — the foundational OS-side intuition the paper builds on.
- Cognitive Architectures for Language Agents (Sumers, Yao, Narasimhan, Griffiths, arXiv:2309.02427) — broader framing that places MemGPT-style memory management inside a fuller cognitive-architecture taxonomy. Useful companion read.
