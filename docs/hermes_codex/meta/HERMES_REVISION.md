---
codex_id: HERMES_REVISION
title: Hermes Source Revision — Canonical Snapshot
role: Scribe
layer: Meta
status: draft
hermes_source_refs:
  - (whole-clone snapshot, no single file)
ember_subsystem_targets: []
cross_refs:
  - meta/MANIFEST
  - meta/SHARED_CONTEXT
  - meta/INDEX
---

# Hermes Revision — The Snapshot This Codex Was Written Against

This file is the Scribe's anchor. Every claim in every doc of this Codex points back to the Hermes source tree as it existed at the commit recorded below. If Hermes's upstream moves on — and it will; the project is fast — this snapshot is the version of Hermes the six authors saw. Future Scribes should re-pin this file before any major Codex revision.

A Codex without a pinned revision is a Codex that lies softly over time. We will not.

---

## Source Identity

- **Upstream:** `NousResearch/hermes-agent`
- **License:** MIT (Copyright (c) 2025 Nous Research) — see `/tmp/hermes-agent/LICENSE`
- **Clone location used by this Codex:** `/tmp/hermes-agent/` (local-only path; never embedded in any other doc — cites use repo-relative paths only)

## Commit Pinned

| Field | Value |
|---|---|
| Commit SHA (full) | `4e2c66a098340e349b8e2adae73a4df704f86987` |
| Commit subject | `chore(release): add AUTHOR_MAP entry for Stark-X` |
| Commit date | `2026-05-21 19:16:35 -0700` |
| Author | `Teknium` |
| Branch | `main` |
| `git describe` | `v2026.5.16-686-g4e2c66a09` |
| Most recent tagged release | `v2026.5.16` (this Codex commit is 686 commits ahead) |

The release tag scheme is `vYYYY.M.MINOR` — the `v2026.5.16` tag corresponds to a release cut on 2026-05-16. Hermes also publishes release notes per major: `RELEASE_v0.2.0.md` through `RELEASE_v0.14.0.md` live at the repo root and remain the best long-form record of *why* features were added.

## Codebase Scale (at the pinned commit)

| Measure | Count |
|---|---|
| Python files (`*.py`, excluding hidden dirs, excluding `node_modules`) | **1,800** |
| Python source lines (sum of `wc -l` across all `*.py`) | **871,611** |
| Tracked files (any extension, excluding `.git` and `node_modules`) | **3,614** |
| Tracked directories (excluding `.git` and `node_modules`) | **662** |
| Test files under `tests/` | **1,184** |

For an agent that calls itself "small enough for a $5 VPS", Hermes the codebase is large. This is not a contradiction — the surface area exists *so the runtime can be small*: the bulk is platform adapters, optional plugins, optional skills, and tests. Ember does not need to import 1,800 Python files to inherit a pattern. She needs to read one and re-implement its spine. The Forge layer of this Codex makes that translation; the rest of the layers describe what's worth translating.

## Top 20 Largest Python Files (by byte size)

These are the files where the most behaviour lives. The Architect, Forge, and Auditor layers concentrate their citations here.

| Rank | Size (bytes) | Lines | Path |
|---:|---:|---:|---|
| 1 | 856,440 | 18,207 | `gateway/run.py` |
| 2 | 662,814 | 14,560 | `cli.py` |
| 3 | 525,967 | 13,701 | `hermes_cli/main.py` |
| 4 | 294,945 | 7,468 | `hermes_cli/auth.py` |
| 5 | 255,700 | 5,656 | `gateway/platforms/telegram.py` |
| 6 | 253,262 | 5,705 | `gateway/platforms/discord.py` |
| 7 | 251,991 | 6,286 | `hermes_cli/kanban_db.py` |
| 8 | 242,726 | 6,680 | `tui_gateway/server.py` |
| 9 | 242,552 | 5,590 | `hermes_cli/config.py` |
| 10 | 230,929 | 5,289 | `agent/auxiliary_client.py` |
| 11 | 229,783 | 4,094 | `agent/conversation_loop.py` |
| 12 | 225,870 | 5,467 | `hermes_cli/gateway.py` |
| 13 | 210,841 | 5,058 | `gateway/platforms/feishu.py` |
| 14 | 192,534 | 4,874 | `gateway/platforms/yuanbao.py` |
| 15 | 180,851 | 4,153 | `run_agent.py` |
| 16 | 177,966 | 4,583 | `hermes_cli/web_server.py` |
| 17 | 161,278 | 3,812 | `gateway/platforms/base.py` |
| 18 | 160,365 | 3,796 | `tools/browser_tool.py` |
| 19 | 153,894 | (n/a) | `gateway/platforms/api_server.py` |
| 20 | 147,188 | (n/a) | `tools/mcp_tool.py` |

(Line counts come from `wc -l`; bytes come from `find -printf '%s'`. Where a line count is shown, the file was in the wc-l top-20 list; where it isn't, the file ranked by bytes but not by lines.)

Two observations the Architect layer will return to:

1. **`gateway/run.py` is the single biggest file in Hermes** — bigger than the CLI, bigger than the agent loop, bigger than the TUI server. The bulk of Hermes's lived complexity is in the messaging gateway, not the agent itself.
2. **`cli.py` and `hermes_cli/main.py` together are ~32k lines.** What Hermes ships as "a CLI" is a richly featured TUI orchestrator with skin engine, prompt-toolkit autocomplete, slash-command registry, kanban dispatcher, and web server — not a thin `argparse` wrapper. (Ember's Munnr is deliberately the latter; see Vow of Smallness.)

## Notable Documents in the Repo Root

These are the design-treatise files. Cite them by path only — they're text, but they're authoritative for *intent*.

- `AGENTS.md` (53 KB) — the development guide and architectural design treatise
- `CONTRIBUTING.md` (44 KB) — contribution flow and code style
- `SECURITY.md` (15 KB) — security model and disclosure process
- `README.md` (13 KB) — the public face
- `hermes-already-has-routines.md` — Nous Research's internal meta-note explaining how Hermes anticipated and absorbed the "agentic routines" pattern
- `RELEASE_v0.2.0.md` through `RELEASE_v0.14.0.md` — twelve release histories; the richest source of "why this exists"
- `.env.example` (~23 KB) and `cli-config.yaml.example` (~57 KB) — the canonical surface of all configurable knobs

## How to Reproduce This Snapshot

```bash
git clone https://github.com/NousResearch/hermes-agent.git /tmp/hermes-agent
cd /tmp/hermes-agent
git checkout 4e2c66a098340e349b8e2adae73a4df704f86987
```

If that SHA has been garbage-collected upstream (rebased branches sometimes lose orphan commits), use the tag plus offset:

```bash
git checkout v2026.5.16
# Then advance 686 commits along main, or accept the v2026.5.16 baseline.
```

The Codex's claims are **most accurate** at `4e2c66a09`. They are **probably still accurate** at later commits on `main`, but the Scribe makes no guarantee — re-verify before lifting code patterns directly.

## What the Scribe Has Verified

- Every path cited above exists at the pinned commit.
- Every byte/line count above was measured directly, not estimated.
- The license is MIT, as claimed in the README.
- The release-notes file series is complete v0.2 through v0.14.

## What the Scribe Has *Not* Verified

- That every cross-link inside individual Codex docs resolves — the Codex is still being authored in parallel. The Scribe will close this loop on the next pass once the six layers have settled.
- That every line-number citation in the other Codex docs lines up exactly with the pinned commit. The line numbers in each doc are written against *this* commit; if a future reader has pulled a newer Hermes, the line offsets may have shifted. The file paths are stable; the line offsets are advisory.

## Maintenance Note

When this Codex enters a second authoring wave, the new Scribe should:

1. Re-run the commands captured below.
2. Replace this file's "Commit Pinned" and "Codebase Scale" tables.
3. Diff the file lists — note new top-20 entries, retired modules.
4. Walk the citations in each layer doc; flag any that no longer resolve.

### Commands

```bash
# Identity
git -C /tmp/hermes-agent rev-parse HEAD
git -C /tmp/hermes-agent log -1 --format='%H%n%s%n%ai%n%an'
git -C /tmp/hermes-agent describe --tags --always
git -C /tmp/hermes-agent rev-parse --abbrev-ref HEAD

# Scale
find /tmp/hermes-agent -name "*.py" -not -path "*/.*" -not -path "*/node_modules/*" | wc -l
find /tmp/hermes-agent -name "*.py" -not -path "*/.*" -not -path "*/node_modules/*" -exec wc -l {} + | tail -1
find /tmp/hermes-agent -type f -not -path "*/.git/*" -not -path "*/node_modules/*" | wc -l
find /tmp/hermes-agent -type d -not -path "*/.git*" -not -path "*/node_modules*" | wc -l

# Top files
find /tmp/hermes-agent -name "*.py" -not -path "*/.*" -printf '%s %p\n' | sort -rn | head -20
```

## What This Means for Ember

A pinned revision is a small thing, but it carries one of the heaviest Vows: **the Vow of Honest Memory** *(SYSTEM_VISION §3)*. The Codex's authority comes from saying truthfully *which* Hermes it was written against. Without this file, future-Ember-developers reading a Codex doc that says "`gateway/run.py:1500` does X" have no way to check whether that line still exists, or whether the project has refactored. With this file, they can `git checkout 4e2c66a09` and see exactly what the six authors saw.

This file affects no True Name directly. It protects every True Name's reasoning chain by anchoring the evidence. Maintain it as you would a citation in a published paper — because that is what it is.
