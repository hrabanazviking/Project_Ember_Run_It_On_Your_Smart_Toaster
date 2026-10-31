# E-039 — Core docs + runnable examples

*Part II, slice E-039. Roadmap line: "Core docs + runnable
examples." Docket 84's DATA_FLOW half lands here (the
whole-docs reconciliation stays E-194's); new docket 89
records the one gap this slice could see but must not touch.*

## The state this slice found

Part II built the core slice by slice, and each slice filed
its own doc — the map (E-019), the tethering spec (E-020),
hardening (E-021), the backend contract (E-022), Aesir
(E-023), ThoughtForge (E-024), personae (E-025), tools
(E-026/E-027), streaming (E-028), offline truth (E-029),
error honesty (E-030), persistence (E-031), the day-one flow
(E-032), config (E-033), the diary (E-034), conversations
(E-035), determinism (E-036), the API freeze (E-037), and
concurrency (E-038) — all under `docs/architecture/`, beneath
the canonical trio `docs/architecture/ARCHITECTURE.md`,
`docs/architecture/DATA_FLOW.md`, and
`docs/architecture/DOMAIN_MAP.md`. The documentation *of the
core* was therefore complete but scattered, and two holes
stood open:

- **No runnable example existed anywhere.** `examples/` held
  only scaffold READMEs (E-014's census), while the folder's
  own stated law is that "examples must actually run against
  the current `src/ember/`" — a law nothing in the tree could
  be checked against, because there was nothing to run.
- **`docs/architecture/DATA_FLOW.md` had gone stale against
  the code** (docket 84): retrieval drawn at k=8 where the
  code searches k=5, a §7 that denies streaming and tool use
  the shipped core has, a typed `AskTurn` the code never had,
  and the pending journal drawn as "a tiny SQLite file" where
  E-031 built per-turn JSON files.

## What E-039 files

### Runnable examples (`examples/`)

Three standalone programs and one worked config, each
runnable from the repo root in the bare stdlib-only
environment, each keeping its state in a temporary folder
and leaving the caller's directory untouched:

| Example | Run | What it proves |
|---|---|---|
| `examples/first_chat.py` | `PYTHONPATH=src python3 examples/first_chat.py` | The real conversation loop (`ember.spark.munnr.chat.run`) takes a typed line, streams a reply, and remembers the turn — against a clearly labelled fake model and an in-memory Well stand-in. |
| `examples/member_binding.py` | `PYTHONPATH=src python3 examples/member_binding.py` | A member binds through frozen API v1 only: the version gate, the 155-name manifest verified intact, config loaded through the frozen loader, typed refusals from the frozen registries, persona/conversation tagging. |
| `examples/offline_turns.py` | `PYTHONPATH=src python3 examples/offline_turns.py` | Offline truth lived: the Well unreachable, the banner spoken, the turn saved to the pending journal, the diary kept in facts only — then the journal draining into a reachable Well, in order. |
| `examples/configs/phone-class.toml` | loaded by `examples/member_binding.py` and by the tests | A complete worked config in TOML shape (the shape a no-PyYAML install reads with the stdlib alone): phone profile, 1024-token history, diary on. Copyable to `~/.ember/config/ember.toml`. |

Two of the examples' own first drafts failed when run —
a stream chunk built without its `done` flag, and a config
class imported from the wrong schema module. Both were
caught by *running* the examples (the thing this slice
exists to make normal), fixed in the examples, and are the
standing argument for the subprocess tests below: an example
that is never executed is a claim, not an example.

### The docs, corrected and indexed

- `docs/architecture/DATA_FLOW.md` is corrected in place
  for docket 84 — facts only, owned at the doc's head with
  the correction dated and the slice named: retrieval k=5
  (hybrid and text), streaming as the default turn shape
  with the tool loop on both paths, §7's negative space
  rewritten to the shipped truth (tools off by default and
  approval-gated when enabled; streaming the default,
  interruptible per E-028), the `AskTurn` removed (the
  operator's line is what travels), and §2.2's pending
  journal drawn as E-031 built it (one small JSON file per
  turn, atomic; drained by the next connected session;
  damaged files quarantined, never deleted). The grammar,
  the flows, and the Cartographer's voice stand untouched.
- This doc is the Part II core-docs index: the per-slice
  docs listed above are the core's documentation, each
  filed beside the code it describes, and E-194
  (`docs/architecture/` whole) reconciles the builder docs
  against them at the end of the campaign.

## Docket 89 — new, assigned to E-195

The `examples/` scaffold READMEs are Runa-era text: they
name planned files that were never written (`pi-only.yaml`,
a skill loader under a Runa-named source tree that does
not exist in this tree, session transcripts of "Runa")
and describe the folder as an empty scaffold, which
stops being true with this slice. They are README.md files:
this campaign never touches one, in any slice, for any
reason — so the correction belongs to E-195 (README care,
the slice Volmarr's law reserves for exactly this, extending
by hand with all existing text preserved). Recorded here so
the staleness is a docketed fact, not a surprise.

## Honest limits

- **No live model ran.** The examples' model is a fake by
  design — that is what makes them runnable anywhere,
  including a toaster-profile install with no model program
  present. A real-model run remains Part III's proof burden
  (E-047/E-049), not this slice's claim.
- **The chat examples drive the operator surface through
  its seams** (`chat.run` with injected openers — the same
  seams the suite's own tests use). `chat` is deliberately
  NOT frozen API (E-037); only `examples/member_binding.py`
  is held to the frozen-import discipline, and the tests
  AST-scan it for exactly that.
- **One worked config, not a library of them.** The
  scaffold's planned fleet (`pi-only`, `dev-laptop`, …)
  belongs to real deployment shapes as they are proven
  (Parts III/XII); one verified phone-class file now, more
  when their profiles are measured — never a folder of
  unrun paper configs.
- DATA_FLOW's other elder statements (the ingest journal's
  shape, Hjarta's prompt files) were not re-audited here;
  docket 84 named four facts and those four are what this
  slice corrected. E-194 owns the whole-docs pass.

## Tests and gate

`tests/unit/test_core_docs_examples_e039.py` — the three
examples run as real subprocesses (exit 0, expected output,
caller's directory untouched), the member example's imports
AST-scanned against the frozen bind points, the example
config loaded through the frozen loader with its phone
numbers pinned, DATA_FLOW's four corrected facts pinned,
and this doc's named paths all proven to exist. Gate counts
are recorded in `CAMPAIGN_STATE.md` at banking.
