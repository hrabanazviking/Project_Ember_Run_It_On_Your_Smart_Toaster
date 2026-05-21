# tools/ — developer / repo tooling

**Developer tooling that operates *on the repository itself*** rather
than as part of the running Ember agent.

> ⚠️ **Naming clarification:** there are two `tools/` directories in
> this repo:
>
> - **`tools/`** (this directory) — *repo-level developer tooling*.
>   Link-checkers, drift detectors, ad-hoc importers. Not shipped.
> - **`src/ember/tools/`** — *first-party Ember tools* (the slice-2
>   tool-use feature). `search_well`, `read_local_file`, `fetch_url`.
>   Shipped 0.2.0.
>
> See `src/ember/tools/README.md` for the latter.

**Last touched:** 2026-05-21 (slice 2 ratified).

---

## Subfolders

| Folder | Holds | Slice-2 state |
|---|---|---|
| `repo/` | Repo-shape checks: link-checker, README consistency, ORIGINS.md drift detector, INTERFACE.md presence validator. | Scaffold only — the closest active equivalent is the slice-2 doc-pass audit (Cartographer's Read-the-tree-and-report flow). |
| `diagnostics/` | Live-system diagnostics: snapshot a running Ember's state, dump event bus traffic, inspect memory store integrity. | Scaffold only; `ember doctor` covers most operator-side diagnostics for slice 2. |
| `importers/` | One-way importers that pull material from other Volmarr projects (NSE, MindSpark, WYRD, …) into this repo. Used carefully, never on schedule. | Scaffold only; the slice-1 fork from Runa was a one-time manual `git format-patch` / `cp -r` operation; no importer was needed. |

---

## Rules

- **Tools never modify deployed state.** Read-only by default;
  mutations are opt-in and logged.
- **Tools live here, not in `scripts/`**, because they reason about
  the *repository* or a *live Ember* rather than performing routine
  operator tasks.
- **Tools are not packaged.** They're not in `[project.scripts]`;
  they're meant for contributors and maintainers to invoke directly.

---

## What's NOT here yet

| Script | Why it's not here yet | Slice |
|---|---|---|
| `repo/check_links.py` | The slice-2 doc tree has ~80 internal links; not yet enough to need automated checking. Would land if/when a doc PR breaks links. | Slice 3+ candidate |
| `repo/check_origins_drift.py` | `ORIGINS.md` §6 already names this as planned. Would flag any root file or top-level directory present in the repo but not represented in ORIGINS. | Slice 3+ candidate (already named in ORIGINS) |
| `repo/check_interface_md_presence.py` | Every `src/ember/*/` subpackage should have an `INTERFACE.md`. The slice-2 doc-pass audit verified this manually; a check script would automate the audit. | Slice 3+ candidate |
| `diagnostics/snapshot_well.py` | An `ember well dump` subcommand would do the same job; that's a Munnr extension, not a repo tool. | Reconsider — might belong in `src/ember/spark/munnr/` instead |
| `diagnostics/dump_audit.py` | `cat ~/.ember/state/tool_audit/*.jsonl \| jq` does the job today. An `ember tool audit` subcommand (slice-3 candidate per ADR 0013 §6) would supersede this. | Slice 3+ candidate (becomes `ember tool audit`) |
| `importers/from_runa.py` | The slice-1 fork was manual; no future Runa→Ember import is anticipated. | Probably unnecessary |

---

## How to add a tool here

If a repo-shape check or live-Ember diagnostic would be useful:

1. **Add a top-of-file docstring** naming the input + output + side
   effects.
2. **Default to read-only** — any mutation needs `--apply`.
3. **Print to stdout, exit non-zero on findings.** That makes it
   usable as a CI check.
4. **Update this README's "What's NOT here yet" → "What's here"** to
   document the shipped tool.

If it's a `repo/` check that mostly walks the tree and grep-checks
patterns, an Explore-style subagent invocation often does the job
without needing a permanent script. Save the script form for things
that an operator would actually run multiple times.
