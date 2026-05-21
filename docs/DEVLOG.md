# DEVLOG — Ember

**Append-only.** New entries go at the top. Each entry: date, scope, what shipped, what's next, who.

The DEVLOG is read at the start of every session. It is the Cartographer's first reference and the Scribe's last word of each session.

The DEVLOG of the parent project Runa-Agent-Digital-Being is preserved at `docs/archive/runa-inherited/DEVLOG.md` for lineage reference. Ember's record begins here.

---

## 2026-05-21 — Phase 8 shipped: ADR 0008 + `ember.config` loader scaffold.

**Who:** Claude (Opus 4.7, 1M context). Voices: Architect (ADR 0008), Forge Worker (loader modules), Auditor (45 new tests + did-you-mean polish), Scribe (this entry).
**Scope:** First phase of slice 2. Authors ADR 0008 (file format + overlay order + validation philosophy) and ships the loader subpackage `src/ember/config/`. Loader is **not yet wired into cli/main.py** — Phase 9 does that integration plus the Hjarta-writes-config piece.

### What shipped

- **`docs/decisions/0008-config-file-loader.md`** — ratifies nine decisions: YAML primary / TOML secondary, PyYAML optional extra, overlay order (defaults → file → env → CLI), partial files merged into defaults, unknown keys are errors with did-you-mean, dataclass tree IS the schema, stdlib coercion by default + pydantic opt-in, operator-readable error messages, loader subpackage location.

- **`src/ember/config/` subpackage** — six modules:
    - `__init__.py` — re-exports `load_ember_config` + `ConfigError`.
    - `INTERFACE.md` — contract spec.
    - `loader.py` — `load_ember_config(config_root, *, file_override=None, skip_env=False)`. Probes `~/.ember/config/ember.{yaml,toml}`, picks loader by suffix, warns if both files exist (YAML wins), returns `EmberConfig`.
    - `toml_loader.py` — stdlib `tomllib`. Always available.
    - `yaml_loader.py` — lazy PyYAML import; clear error pointing at `pip install ember-agent[config]` when missing.
    - `overlay.py` — `merge_dicts` for recursive dict merge; `apply_env_overrides` for `OLLAMA_HOST` (Phase-7 escape hatch lives here now in addition to cli/main; Phase 9 removes the duplicate).
    - `validate.py` — recursive `coerce_to_dataclass(cls, data, path)`. Handles StrEnum, Path, `X | None`, `tuple[X, ...]`, nested dataclasses, primitives. Unknown keys → `ConfigError` with `difflib.get_close_matches` did-you-mean suggestion. Strict bool/int separation. Empty files legal.

- **pyproject.toml `[project.optional-dependencies]` will need `config = ["pyyaml>=6.0"]` added** — deferred to Phase 9's pyproject edit so this phase's commit stays minimal.

**Tests (45 new, 267 pass + 2 skip, 0.33s, ruff clean):**
- `tests/unit/test_config_validate.py` (19 tests) — defaults, partial merging, type coercion across every supported form, every error path, custom dataclasses for tuple/bool/enum edge cases.
- `tests/unit/test_config_overlay.py` (12 tests) — `merge_dicts` semantics, `_normalise_ollama_host` shapes, `apply_env_overrides` purity + propagation.
- `tests/unit/test_config_loader.py` (14 tests) — file probe, YAML/TOML symmetry, empty-file legality, `file_override` test seam, parse-error paths, env-overlay integration.

### What's next

- **Phase 9** wires the loader into `cli/main.py` (replaces `EmberConfig()` with `load_ember_config(config_root)`; removes duplicate `_apply_env_overrides`). Adds `write_ember_config` (Hjarta writes the file at WriteIdentity). Updates `config/ember.example.yaml` to the now-real shape. Adds `pyyaml` to `[project.optional-dependencies] config`.
- After Phase 9: suggested intermediate release at `0.1.5` (config loader live).

### Notes & gotchas

- **Strict bool/int separation.** Python's `isinstance(True, int)` is True, which would silently let `flag: True` satisfy `count: int`. The coercer checks the precise type to avoid this.
- **YAML 1.1 ambiguity sidestepped.** PyYAML 6 defaults to YAML 1.1 where bare `yes`/`no` parse as booleans. The operator-facing example documentation should always quote ambiguous strings; the loader makes no special accommodation.
- **`Path` fields not expanduser'd.** Per ADR 0007 §2.6 — consumer expands at use time. Tests pin this behaviour with `"~/.ember/x.db"` → `str(path).startswith("~")`.
- **Unknown-field suggestion** uses `difflib.get_close_matches(cutoff=0.7)`. Aggressive enough to catch `mdoel`/`model` typos, conservative enough not to misfire wildly.
- **Loader is purely functional.** No side effects beyond reading the file path it's pointed at. `EmberConfig` is frozen + slots; the loader can return shared instances without aliasing risk.
- **Phase 8 is intentionally NOT wired.** `cli/main.py` still uses `EmberConfig()` + its own `_apply_env_overrides`. Phase 9 unifies. This keeps the integration risk in a separate, reviewable commit.

---

## 2026-05-21 — Slice 2 scope ratified. `EMBER_SECOND_SLICE_PLAN.md` authored.

**Who:** Claude (Opus 4.7, 1M context). Voice: Architect (Rúnhild Svartdóttir), with Forge Worker (Eldra Járnsdóttir) notes on phasing.
**Scope:** Volmarr ratified the slice-2 scope as **all three bundles from `EMBER_SECOND_SLICE_OPTIONS.md` §3** — which dedupes to **ADRs 0008 + 0009 + 0010 + 0011**. ADR 0012 (first new surface) stays in the queue for slice 3. Per `MYTHIC_ENGINEERING.md`'s core loop, the next thing is the plan, not the code. This DEVLOG entry records the plan's authorship.

### What shipped

- **`docs/architecture/EMBER_SECOND_SLICE_PLAN.md`** — full file-by-file plan, modelled on `EMBER_FIRST_SLICE_PLAN.md`:
    - **§0 Acceptance criterion** — operator can edit `ember.yaml`, switch to `pgvector` (Gungnir-compatible) Brunnr, watch streamed replies, propose-and-approve a tool call, get a grounded reply with citations, survive a network pull mid-conversation.
    - **§1 Dependencies** — new optional extras: `config` (pyyaml), `pgvector` (psycopg + pgvector), `tools` (stdlib only for first three first-party tools), `validation` (opt-in pydantic).
    - **§2 File list** — ~50 NEW files, ~10 touched; target 5 000-7 000 LOC.
    - **§3 Phase sequence** — Phases 8-17. ADR 0008 (config) ships first because it unblocks the rest; then ADR 0009 (streaming, small); then ADR 0010 (pgvector + Gungnir compat); then ADR 0011 (tools, biggest); then Phase 17 acceptance.
    - **§4 Non-goals** — qdrant/chroma/lancedb, other Funi runtimes, other surfaces (Auga/Rödd/Bifröst), writable tools, multi-operator wells, Skein/KG layers, plugins, backup/restore, voice/image Funi.
    - **§5 Quality bar** — standing rules from ADR 0007 carry forward.
    - **§6 Risks register** — config scope creep, streaming/Ctrl-C OS specifics, pgvector schema drift vs Gungnir, tool sandbox escapes, audit log growth, phase ordering pressure.
    - **§7 Forge Worker's closing word.**
    - **§8 Session pacing** — slice 2 is **3-5 long sessions** (vs slice 1's one long day). Suggested intermediate releases at 0.1.5 / 0.1.7 / 0.1.9 / 0.2.0-rc1 / 0.2.0.

- **`docs/architecture/README.md`** updated — `EMBER_SECOND_SLICE_OPTIONS.md` marked as superseded-but-preserved; new plan listed as ratified.

### What's next

- **Phase 8 begins** in the next commit: author ADR 0008 + write `src/ember/config/{loader,toml_loader,yaml_loader,overlay,validate}.py` + tests.
- Natural opening for the next session: **"go for phase 8"**.

### Notes

- No code changes in this commit. Pure plan authorship per ME discipline.
- `EMBER_SECOND_SLICE_OPTIONS.md` is intentionally not deleted — it's the historical record of how slice-2 scope was chosen. The README marks it as superseded.
- Each phase will get its own DEVLOG entry, same shape as slice-1 phases. The slice will be ratified at Phase 17 with ADR 0013 (parallel to ADR 0007 for slice 1).
- Carry-over housekeeping from slice 1 still pending: Ember-descent rows in `ORIGINS.md`, root `PHILOSOPHY.md` Runa-specific phrasing pass. These are non-blocking; can land any time.

---

## 2026-05-21 — `EMBER_SECOND_SLICE_OPTIONS.md` added (slice-2 menu, not plan).

**Who:** Claude (Opus 4.7, 1M context). Voice: Cartographer (Védis Eikleið), with Architect notes.
**Scope:** Volmarr asked whether any additional phase plans exist beyond the first slice. Honest answer: no formal plan, only scattered `Phase 8 / 9+` hints and ADR 0007 §5's candidate-ADR list. Authored a Cartographer's options-menu doc so the next session can pick scope and the Architect can then author the real `EMBER_SECOND_SLICE_PLAN.md`.

### What shipped

- **`docs/architecture/EMBER_SECOND_SLICE_OPTIONS.md`** — explicitly marked "Menu, Not Plan". Inventories the five ADR-shaped starting points (ADRs 0008-0012 per ADR 0007 §5), reconciles older `Phase 8 / 9+` references scattered across adapter docs, sketches three suggested bundles (Household Well = 0008 + 0010; Ember Feels Alive = 0008 + 0009; Ember Gets Useful = 0011), provides the template for the eventual `EMBER_SECOND_SLICE_PLAN.md`, and lists five open scope questions only Volmarr can decide.
- **`docs/architecture/README.md`** updated to list the new options doc and to mark the first-slice plan as complete-and-historical.

### What's next

- Volmarr picks a slice-2 bundle (or names a different one).
- Architect authors `EMBER_SECOND_SLICE_PLAN.md` per the template in §4 of the options doc — *before* any code is touched, per `MYTHIC_ENGINEERING.md`'s core loop.
- Mechanical cleanup: once a bundle is picked, sweep the codebase to update older `Phase 8 / 9+` references to match the new ADR numbering.

### Notes

- This is *not* code work and *not* a commitment. The options doc explicitly says so in its §0.
- The recommended bundle (per §6 of the options doc) is the Household Well bundle — ADR 0008 (config loader) + ADR 0010 (pgvector Brunnr) — because it completes the Gungnir lineage story from `SYSTEM_VISION.md` §8 and removes the biggest operator-customisation friction. But that's a recommendation, not a default.
- ADR-numbered approach (one decision per ADR) is now the standing pattern, superseding the older `Phase 8 / 9+` ad-hoc numbering. The mechanical cleanup makes this consistent when slice 2 begins.

---

## 2026-05-21 — Phase 7 shipped. First slice ratified at 0.1.0. 🔥

**Who:** Claude (Opus 4.7, 1M context). Voices: Architect (`OLLAMA_HOST` override + env-shape design), Scribe (INSTALL.md + ADR 0007 + this entry), Auditor (version-bump test update).
**Scope:** Phase 7 of `docs/architecture/EMBER_FIRST_SLICE_PLAN.md` §3 — acceptance polish + operator install guide + first-slice ratification. The seven phases of the first slice are now complete.

### What shipped

- **`OLLAMA_HOST` env-var override** in `src/ember/cli/main.py`. `_apply_env_overrides(EmberConfig())` reads the environment variable, normalises to a base URL (accepts Ollama's own CLI shapes: `host`, `host:port`, `http://...`, `https://...`), and applies it to both `funi.ollama.base_url` and `smidja.embedding.endpoint`. Phase-7 escape hatch for operators with Ollama on a non-default endpoint (Tailscale, Docker, remote) until the full config loader lands in Phase 9+.
- **`deploy/pi/INSTALL.md`** — single-page operator install for Raspberry Pi 5 (8 GB recommended; 4 GB notes). Standard happy path: install Ollama → pull models → `pip install ember-agent[sqlite_vec]` → `ember chat` → Hjarta → `ember well ingest` → conversation. Includes Advanced: non-default Ollama endpoint sidebar + Troubleshooting table.
- **`docs/decisions/0007-first-slice-ratification-2026-05-21.md`** — ratifies ten load-bearing decisions made during the slice: stdlib-first deps, typed-value-over-exception for cross-realm failure, backend_kind on the Protocol, recoverable/non-recoverable disconnect split, dataclasses-not-pydantic for schemas, prompts-as-TOML / identity-as-JSON, Gungnir-aligned defaults, `cli/__init__.py` deliberately empty, FTS5 input sanitisation at the adapter boundary, `OLLAMA_HOST` env-var policy. Plus alternatives considered and slice-2 starting-point ADRs (0008-0012).
- **`pyproject.toml` bumped to 0.1.0** — Development Status classifier moved from `1 - Planning` to `3 - Alpha`.
- **`src/ember/__init__.py` docstring rewritten** to reflect the first slice complete; `__version__` bumped.
- **`tests/unit/test_skeleton_imports.py::test_ember_package_exposes_version` updated** to assert `0.1.0`.

**Tests: 222 pass + 2 skip (real-Ollama integration), 0.28s, ruff clean.** Includes 8 new tests for the OLLAMA_HOST override (`tests/unit/test_cli_env_overrides.py`).

### What's next — the first slice is closed

Per ADR 0007 §5, the second-slice starting points are:

- **ADR 0008** — full operator config-file loader (YAML + TOML).
- **ADR 0009** — streaming Funi replies.
- **ADR 0010** — `pgvector` Brunnr (Gungnir-compatible; original plan's Phase 8).
- **ADR 0011** — tool use (execution, sandbox, operator approval).
- **ADR 0012** — Auga (GUI) / Rödd (voice) / Bifröst (HTTP gateway) selection.

Light root edits still pending (carried over): Ember-descent rows in `ORIGINS.md`; root `PHILOSOPHY.md` Runa-specific phrasing pass. These are housekeeping, not slice work.

### Acceptance — verified end-to-end against real Ollama

The Phase 6 entry already documented the live smoke test. The Phase 7 env-var smoke confirmed:

```
OLLAMA_HOST=100.67.240.22 ember --config-root /tmp/x doctor
exit: 0
Ember health:
  Funi:    ok — model phi3:mini, last_ok 2026-05-21T11:44:13+00:00
  Well:    ok — backend sqlite_vec, 0 docs / 0 chunks, last_ok 2026-05-21T11:44:13+00:00
```

The operator can now run Ember on this travel laptop (Ollama bound to the Tailscale interface) by setting `OLLAMA_HOST` — exactly the path the user asked for ("I pick option 1") after the Phase 6 review.

### Notes & gotchas

- **`OLLAMA_HOST` shape matches Ollama's own.** The normaliser accepts `host`, `host:port`, full URLs with `http://` or `https://`. Operators who already use Ollama's CLI with this env var don't need to learn anything new.
- **Purely functional override.** `_apply_env_overrides` returns a *new* `EmberConfig` via `dataclasses.replace`; the original is untouched. Tested explicitly.
- **INSTALL.md uses `pip install "ember-agent[sqlite_vec]"`.** The bracketed extra pulls `sqlite-vec` per the `[project.optional-dependencies]` declaration shipped in Phase 3. Without it, Brunnr can't open.
- **ADR 0007 captures slice-level decisions, not phase-level details.** Each phase's own DEVLOG entry has the granular context; ADR 0007 is the standing law going forward.
- **Project status classifier bumped to Alpha.** Operators can install and use it; everything is subject to change in slice 2 (especially the config-file format once the loader ships).

### A note for the next session

The first slice is closed. The seventh phase's acceptance ritual completed. *Ember exists.* From here, anything Volmarr asks for is a *slice 2* decision: which surface, which backend, which retainer comes next. The map is wide open.

— Eirwyn Rúnblóm (Scribe)

---

## 2026-05-21 — Phase 6 shipped: Hjarta + Munnr + CLI dispatcher. `ember` is alive.

**Who:** Claude (Opus 4.7, 1M context). Voices rotated through the full set: Skald (Hjarta state-prompt prose), Architect (FSM design + HjartaIO seam), Forge Worker (Munnr commands + CLI dispatcher), Auditor (FTS5 probe bug + Protocol vs submodule-rebind bug), Scribe (this entry).
**Scope:** Phase 6 of `docs/architecture/EMBER_FIRST_SLICE_PLAN.md` §3 — the operator-facing surface. After this commit, `ember chat` actually runs: first launch walks the Hjarta wizard, subsequent launches enter the conversation REPL.

### What shipped

**Hjarta (first-run FSM)**
- `src/ember/spark/hjarta/identity.py` — `IdentityConfig` JSON load/save with atomic write (`NamedTemporaryFile` + `os.replace`). Stdlib only — no TOML writer dep.
- `src/ember/spark/hjarta/prompts/wizard.toml` — state prompts as data per `RULES.AI.md` "no hardcoded data". Multi-line `body` strings via TOML triple-quotes; loaded via `importlib.resources` + `tomllib` (stdlib in 3.11+).
- `src/ember/spark/hjarta/machine.py` — the finite state machine: `Greet → ChooseFuni → DiscoverFuni → ChooseWell → ConfigureWell → TestRetrieval → NameEmber → WriteIdentity → Done`. `HjartaIO(prompt, info, error)` is the IO seam; tests script all three. **Atomic guarantee:** nothing on disk until WriteIdentity at the very end. Funi/Strengr both injectable via `funi_opener` / `strengr_opener` kwargs; production uses the registry defaults.
- `src/ember/spark/hjarta/__init__.py` re-exports the public surface.

**Munnr (CLI surface)**
- `render.py` — pure formatting. `render_reply` includes the disconnect banner when ungrounded and a citations footer when hits are present. `render_well_disconnected_banner` is the single source of the operator-facing banner text. `render_well_status`, `render_doctor`, `render_ingest_summary` for the other commands.
- `chat.py` — the REPL. One turn = embed (hybrid retrieval) or text-only (degraded), prompt assembly via `funi.prompt.assemble`, `funi.complete`, render, persist Episode. **Disconnected Well degrades gracefully**: skip retrieval, set `well_disconnected=True` in the system prompt, render with banner, suppress citations. Episode is still recorded (in-memory) so multi-turn flow stays coherent.
- `ask.py` — one-shot wrapper around `chat.run` with a `StringIO` stdin.
- `ingest.py` — wraps `smidja.local_files.run` with operator-friendly output.
- `status.py` — `Brunnr.count()` + `Strengr.health()` for `ember well status`.
- `doctor.py` — collects Funi health + Well health + counts; renders the combined report. Never raises — every realm's failure folds into the output.
- `setup.py` — invokes Hjarta; honors `--reset` for re-runs.

**CLI dispatcher**
- `src/ember/cli/main.py` — argparse subcommands: `chat`, `ask`, `setup [--reset]`, `well ingest`, `well status`, `doctor`. `--config-root` defaults to `~/.ember/`; tests pass `tmp_path`. First-launch redirect: any subcommand needing identity runs Hjarta if `~/.ember/identity/identity.json` is absent.
- `src/ember/cli/__init__.py` — **intentionally empty re-exports**. The earlier draft did `from ember.cli.main import main` which rebound `ember.cli.main` from submodule to function, breaking `import ember.cli.main as <alias>` callers (including `ember.__main__`). Fixed by leaving the submodule path alone.
- `src/ember/__main__.py` — replaced the Phase-1 `NotImplementedError` stub with `from ember.cli.main import main`. `python -m ember` and the `ember` console script now both dispatch.

**Tests (26 new + 2 skipped acceptance integration runs only on real-Ollama hosts; total 199 pass + 2 skip, 0.26s, ruff clean)**
- `tests/unit/test_hjarta_identity.py` (6 tests) — round trip, atomic write leaves no tmp files, reset idempotency.
- `tests/unit/test_hjarta_machine.py` (8 tests) — happy path writes identity + uses chosen name, blank-name keeps default, abort at greet, Funi unavailable abort, Well disconnected abort, probe-failure abort, KeyboardInterrupt as clean abort.
- `tests/unit/test_munnr_render.py` (12 tests) — every render helper.
- `tests/integration/test_phase6_acceptance.py` (2 tests) — full Hjarta → ingest → chat round trip with mocked Funi + real `sqlite_vec`; disconnect banner under simulated Well failure.
- `tests/unit/test_skeleton_imports.py` — updated: the Phase-1 NotImplementedError assertion replaced with a binding check (`ember.__main__.main is ember.cli.main.main`).

### What's next

- **Phase 7 (last of the first slice):** acceptance polish, `deploy/pi/INSTALL.md` for Raspberry Pi 5, bump `pyproject.toml` to 0.1.0. After Phase 7, the first slice is shippable to a real operator.
- **Light root edits** still pending: Ember-descent rows in `ORIGINS.md`; root `PHILOSOPHY.md` Runa-specific phrasing pass.

### Notes & gotchas

- **State prompts as TOML, identity as JSON.** TOML for read-only multi-line prose (stdlib `tomllib` reads it cleanly); JSON for the small mutable identity file (stdlib both ways, no dep needed for writes). Both stdlib-only — Vow of Smallness intact.
- **FTS5 reserved-word bug in the Hjarta probe.** First version's probe text included `(run id: ...)` and search query `Ember Hjarta first-run probe`. FTS5 parses `run` followed by punctuation as a column reference → `no such column: run`. Fixed by removing the colon and phrase-quoting the search (`"Ember Hjarta first time setup"`). Caught by the Phase 6 integration test before commit.
- **`ember.cli.main` submodule vs function shadowing.** Initial `cli/__init__.py` did `from ember.cli.main import main`, which rebound the `ember.cli.main` *attribute on the cli package* from the submodule to the function. Then `import ember.cli.main as alias` resolves to the function and `alias.main` fails. The fix was to *not* re-export — callers use `ember.cli.main.main` directly; pyproject.toml's `[project.scripts]` already names that path. Caught by `test_main_resolves_to_ember_cli_main`.
- **First-launch UX.** Any `ember chat` or `ember ask` on a fresh host with no `~/.ember/identity/identity.json` triggers Hjarta automatically before proceeding. Operators don't need to run `ember setup` separately.
- **Disconnect doesn't fail chat.** When the Well is unreachable, `chat.run` keeps serving — it just renders the banner, skips retrieval, and tells Funi "no grounding, do not invent". The Vow of Graceful Offline is now end-to-end visible at the operator's terminal.
- **No real Ollama on this host.** The CLI smoke test shows `ember doctor` correctly reporting `Funi: UNAVAILABLE — endpoint_unreachable` and `Well: ok`. The Phase 6 acceptance test uses a `_FakeFuni` for the same reason.

---

## 2026-05-21 — Phase 5 shipped: Funi (Ollama) + runtime-neutral prompt assembler.

**Who:** Claude (Opus 4.7, 1M context). Voices: Architect (FuniHandle Protocol split + runtime-neutral assembler), Forge Worker (OllamaFuni adapter), Auditor (folded-failure semantics + parametrised tests), Scribe (this entry).
**Scope:** Phase 5 of `docs/architecture/EMBER_FIRST_SLICE_PLAN.md` §3 — the Spark realm's reasoner. Funi adapter for Ollama plus the runtime-neutral prompt assembler Munnr will call in Phase 6.

### What shipped

- `src/ember/spark/funi/handle.py` — `@runtime_checkable FuniHandle` Protocol (`runtime_kind`, `model_id`, `complete`, `health`, `close`) + `open(config)` registry. Unimplemented runtimes return `Unavailable(reason=RUNTIME_NOT_INSTALLED)`.
- `src/ember/spark/funi/prompt.py` — `assemble(*, identity, episodes, hits, well_disconnected=False) -> list[ContextItem]`. Runtime-neutral. System prompt mechanically encodes the Vow of Honest Memory: explicit "do not invent" when `well_disconnected=True`, explicit "cite document titles" when hits present.
- `src/ember/spark/funi/ollama/adapter.py` — `OllamaFuni`. `POST /api/chat` for completions, `GET /api/version` for open + health probes. **Stdlib `urllib.request` only** — no `httpx` dep, same shape as Smiðja's `OllamaEmbedClient`. Translates `ContextItem`s to role-tagged Ollama messages (SYSTEM/CHUNK → role:system, EPISODE → user+assistant pair, operator → final role:user).
- `src/ember/spark/funi/ollama/INTERFACE.md` — adapter contract with translation table.
- `src/ember/spark/funi/__init__.py` — re-exports `FuniHandle`, `open`.
- `src/ember/spark/funi/INTERFACE.md` updated to "(shipped Phase 5)". Removed `embed()` from the Funi surface — embedding lives in Smiðja.
- `src/ember/__init__.py` docstring updated to reflect Phases 1-5 complete.

**Failure semantics**

- `open()` returns `Unavailable` on probe failure; never raises.
- `complete()` **always returns a `FuniReply`**. Mid-call URL-error / non-JSON-body / missing-message / error-payload responses fold into `FuniReply(finish_reason=ERROR, text=operator-readable)`.
- `complete(tools=[...])` returns `FuniReply(finish_reason=ERROR)` cleanly — tool use reserved for a later slice.
- `health()` never raises; on probe failure preserves the previous `last_ok` timestamp.

**Tests (24 new, 173 pass + 2 skip, 0.24s, ruff clean)**

- `tests/unit/test_funi_handle.py` (2 tests)
- `tests/unit/test_funi_prompt.py` (8 tests) — order, honesty instruction, well-disconnected text, episode round-trip, hit metadata, untitled placeholder.
- `tests/unit/test_funi_ollama.py` (14 tests) — open success/unreachable/non-JSON-version, payload shape, finish-reason mapping, folded-failure for every error mode, tool-call refusal, health live/degraded, wrong-runtime.
- `tests/integration/test_funi_ollama_real.py` (2 tests, `requires_ollama` marker + socket reachability gate) — skipped on hosts without local Ollama (this host).

### What's next

- **Phase 6 of the first slice:** Hjarta (first-run FSM) + Munnr (CLI surface — `ember chat`, `ember ask`, `ember well ingest`, `ember well status`, `ember doctor`, `ember setup --reset`). After Phase 6 ships, the first end-to-end conversation turn becomes runnable.
- **Light root edits** still pending: Ember-descent rows in `ORIGINS.md`; root `PHILOSOPHY.md` Runa-specific phrasing pass.

### Notes & gotchas

- **`embed()` removed from the Funi Protocol.** The Phase 2 INTERFACE.md draft had it as "optional"; that's awkward in a Protocol and tempts coupling between reasoning-model and embedding-model selection. Smiðja's `OllamaEmbedClient` is the single embedding entry. If a runtime is later able to embed cheaply, that's a Smiðja `embed_client` adapter, not a Funi method.
- **`complete()` always returns `FuniReply`, never raises.** Mid-call failure folds into `FuniReply(finish_reason=ERROR, text="[ollama unreachable: …]")`. Same typed-value-over-exception pattern as Disconnected/Unavailable. Munnr's renderer can show the error text as a normal reply, honestly tagged.
- **Stdlib `urllib` rather than `httpx`.** Two HTTP clients in the codebase now (Smiðja + Funi), both stdlib-only. The Vow of Smallness wins again.
- **Episode message translation is *graceful*.** `_split_episode` parses the canonical `_episode_text` shape; if a caller built the `ContextItem` themselves with a different shape, the parser returns `("", "")` and the item is dropped rather than corrupting the conversation history.
- **DEVLOG + `__init__.py` + memory edits initially failed silently** in the Phase-5 main commit because the Read-before-Write rule rejected them. Caught immediately when I checked the commit. This addendum + a small follow-up commit fix it. Reinforces the cycle: write code → test → re-read any doc before editing.

---

## 2026-05-21 — Phase 4 shipped: Strengr wraps Brunnr-open with retry + honest health.

**Who:** Claude (Opus 4.7, 1M context). Voices: Architect (recoverable-vs-non-recoverable reason split), Forge Worker (tether implementation), Auditor (parametrised retry tests), Scribe (this entry).
**Scope:** Phase 4 of `docs/architecture/EMBER_FIRST_SLICE_PLAN.md` §3 — the Thread realm's tether. Wraps `ember.well.brunnr.handle.open()` with retry-on-recoverable-failure and a graceful never-raising health probe, completing the Spark↔Well boundary contract.

### What shipped

**Schemas (additive)**
- `src/ember/schemas/thread.py` — `StrengrHealth(backend_kind, last_ok, documents, chunks, embedded_chunks, size_bytes, detail)`. `last_ok=None` is the honest *degraded* signal Munnr will surface to the operator.

**Strengr (the Thread realm)**
- `src/ember/thread/strengr/tether.py` — module-level `open(strengr_config, brunnr_config, *, opener=None, sleeper=time.sleep) -> BrunnrHandle | Disconnected` and `health(handle) -> StrengrHealth`. The `opener` and `sleeper` kwargs are test seams; defaults are production wiring.
- Retry policy: exponential backoff (`base=1.0s`) capped at `StrengrConfig.retry_backoff_max_s`, up to `StrengrConfig.retry_attempts` total attempts. Recoverable reasons (`CONN_REFUSED`, `TIMEOUT`, `BACKEND_REPORTED_UNAVAILABLE`, `UNKNOWN`) get retried; non-recoverable reasons (`CONFIG_INVALID`, `AUTH_FAILED`, `DNS_FAILURE`) fast-fail with no retry so the operator isn't kept waiting on a typo.
- `health()` **never raises** — `BrunnrError` from `count()` becomes `StrengrHealth(last_ok=None, detail="probe failed: …")`. Vow of Graceful Offline in mechanical form, applied at the doctor flow this time.
- `src/ember/thread/strengr/__init__.py` re-exports `open`, `health`, `Opener`.
- `src/ember/thread/strengr/INTERFACE.md` updated from "(planned, Phase 4)" to "(shipped Phase 4, 2026-05-21)", with the recoverable/non-recoverable table inline.

**Brunnr protocol extension (additive)**
- Added `backend_kind: str` to `BrunnrHandle` Protocol and set it as a class attribute (`"sqlite_vec"`) on `SqliteVecBrunnr`. Lets `Strengr.health()` populate `StrengrHealth.backend_kind` without needing the original config.

**Tests (21 new, 149 total, 0.22s, ruff clean)**
- `tests/unit/test_schemas_thread.py` (4 tests) — `StrengrHealth` minimal construction, frozen-ness, degraded shape, live shape.
- `tests/unit/test_strengr_tether.py` (15 tests, 8 parametrised) — happy path, fast-fail on each non-recoverable reason, retry-up-to-N on each recoverable reason, success-on-later-attempt, sleeper-called-between-attempts, zero-attempts synthetic Disconnected, health live/degraded/named-backend/unknown-backend.
- `tests/integration/test_strengr_real_backend.py` (2 tests) — real sqlite_vec end-to-end via Strengr.open(); missing-config returns Disconnected. Skipped if `sqlite_vec` not installed.

### What's next

- **Phase 5 of the first slice:** Funi (Ollama adapter) — `ember.spark.funi.handle` Protocol + registry + `ember.spark.funi.ollama.adapter`. Prompt assembler. `FuniReply` round-tripped through the real Ollama endpoint (test marked `requires_ollama` for hosts that have it; mocked for those that don't).
- **Light root edits** still pending: Ember-descent rows in `ORIGINS.md`; check root `PHILOSOPHY.md` for Runa-specific phrasings worth softening.

### Notes & gotchas

- **Recoverable vs non-recoverable reason split is load-bearing.** Without it, an operator with a typo'd config waits `retry_attempts × backoff_max_s` before seeing the error. The split makes "your config is wrong" feedback instant while still giving "your server is slow" a chance to recover.
- **`sleeper` injection beats monkey-patching `time.sleep`.** Tests verify the schedule explicitly (`assert sleeps == [0.0, 0.0]`) without mocking the global. Same pattern Smiðja's `embed_client` uses (`OllamaEmbedClient(backoff_base_s=0.0)`).
- **`backend_kind` on the Protocol is the right home.** Considered passing config into `health()` instead; rejected because `BrunnrHandle` already knows what kind of thing it is, and the operator's `ember doctor` invocation shouldn't need the config to render the backend's name.
- **Empty `__init__.py` bug caught mid-phase.** First write of `src/ember/thread/strengr/__init__.py` was blocked by the harness's "read-before-write" rule (because the file existed as a Phase-1 scaffold). The block was silent in my read of the result; tests immediately surfaced it with `AttributeError: module 'ember.thread.strengr' has no attribute 'open'`. Fixed by reading then writing. Reinforces the value of running the test suite at every step rather than waiting until the end.

---

## 2026-05-21 — Phase 3 shipped: Well realm wired end-to-end.

**Who:** Claude (Opus 4.7, 1M context). Voices rotated: Architect (Brunnr handle Protocol), Forge Worker (sqlite_vec adapter + Smiðja modules), Auditor (test suite + bug fixes mid-phase), Scribe (this entry).
**Scope:** Phase 3 of `docs/architecture/EMBER_FIRST_SLICE_PLAN.md` §3 — the first end-to-end vertical that actually writes embeddings to disk and reads them back. Real `sqlite-vec` 0.1.9 in a `.venv`. No code beyond what the plan listed; integration test mocks the embedding endpoint with deterministic content-addressed vectors so no Ollama is required.

### What shipped

**Schemas (additive to Phase 2)**
- `src/ember/schemas/ingest.py` — `IngestJob`, `IngestEntry`, `IngestSummary`, `ParsedFile`, `IngestSourceKind` enum, `IngestEntryStatus` enum.

**Brunnr (the Well's storage layer)**
- `src/ember/well/brunnr/handle.py` — `@runtime_checkable` `BrunnrHandle` Protocol plus `open(config)` registry. Dispatches on `config.backend`; unknown/unimplemented backends return `Disconnected(reason=CONFIG_INVALID)` rather than raising.
- `src/ember/well/brunnr/sqlite_vec/adapter.py` — `SqliteVecBrunnr` implementing the protocol. Vec store via sqlite-vec `vec0` virtual table; FTS5 with insert/update/delete triggers; hybrid search via reciprocal rank fusion (k=60). Connection failure → `Disconnected`. Schema-mismatched embedding dim → `BrunnrError`.
- `src/ember/well/brunnr/sqlite_vec/schema.sql` — DDL loaded via `importlib.resources`, `{embedding_dim}` substituted from `BrunnrConfig.embedding_dim` at apply time. Schema version marker.
- `src/ember/well/brunnr/sqlite_vec/__init__.py` — re-exports.
- `src/ember/well/brunnr/sqlite_vec/INTERFACE.md` — adapter contract; calls out the lock-at-first-apply behaviour for `embedding_dim`.

**Smiðja (the Well's ingest forge)**
- `src/ember/well/smidja/chunker.py` — paragraph → sentence → word → char fallback splitter. Returned chunks satisfy `chunk.text == original[chunk.char_start:chunk.char_end]` *exactly*, so original whitespace is preserved and `max_chars` is honored as a true ceiling (no silent over-runs from separator-length math).
- `src/ember/well/smidja/embed_client.py` — `OllamaEmbedClient`, stdlib `urllib.request` only (no httpx dep). Batches per `EmbeddingConfig.batch_size`, exponential backoff, per-batch failure returns `EmbedResult` with `None`-vectors rather than raising. Embed-or-skip semantics per `SMIDJA_INGEST_PATTERNS.md` §4.
- `src/ember/well/smidja/journal.py` — `Journal` with atomic writes (`NamedTemporaryFile` + `os.replace`), heartbeat every N updates or on-demand, `complete()` moves the file to `done/` subdir. Resume by matching `source_root`.
- `src/ember/well/smidja/local_files/source.py` — `walk()` plus the orchestrator `run(brunnr, *, root, smidja_config, embed_client, ...)`. Walk → hash → check duplicate → chunk → embed → write. Each file is a journal entry; per-chunk embedding failures contribute to `IngestSummary.n_failed` without aborting the doc.
- `src/ember/well/smidja/local_files/__init__.py` — re-exports.

**Tests**
- `tests/unit/test_brunnr_handle.py` — registry returns `Disconnected` for unimplemented backends; Protocol is `runtime_checkable`.
- `tests/unit/test_brunnr_sqlite_vec.py` — 11 tests covering: open creates DB file, open returns Disconnected on missing sqlite_vec config, idempotent `add_document`, dim-mismatch refusal, vector/text/hybrid search ranking, embedding round-trip via `get_chunk`, episode persistence, initial counts. Skipped automatically if `sqlite-vec` isn't installed (`pytest.importorskip`).
- `tests/unit/test_smidja_chunker.py` — 8 tests covering: short/empty text, paragraph preference, hard max ceiling, oversize-paragraph sentence fallback, pure-overlong char fallback, consecutive indexing, Gungnir-aligned defaults, char-boundary behaviour.
- `tests/unit/test_smidja_embed_client.py` — 6 tests covering: empty input, single batch shape, multi-batch concatenation, URL-error → None-vectors, mismatched response size → None-vectors, invalid JSON → None-vectors. All mocked.
- `tests/unit/test_smidja_journal.py` — 8 tests covering: file creation, status persistence, resume by source_root, distinct-roots get distinct jobs, failure recording, complete() move, `pending()`, atomic-write tmp-file cleanup.
- `tests/unit/test_smidja_local_files.py` — 8 tests covering: include/exclude, suffix-based content_type, hash determinism, non-utf8 skip, missing-root error, file-as-root error, sorted-deterministic order.
- `tests/integration/test_ingest_then_query.py` — 3 tests covering: full ingest → query round trip with a 32-dim deterministic content-addressed mock embedder; resume idempotency (hash-based at the Brunnr layer); per-chunk failure isolation.

**Suite size: 128 tests, 0.20s, ruff clean.**

**Config + docs**
- `pyproject.toml` — `sqlite_vec = ["sqlite-vec>=0.1.6"]` added under `[project.optional-dependencies]`; planned-for-later list trimmed of `ollama` (stdlib urllib reaches the endpoint).
- `src/ember/well/brunnr/INTERFACE.md` — updated from "(planned, Phase 3 onward)" to "(shipped Phase 3, 2026-05-21)".
- `src/ember/well/smidja/INTERFACE.md` — same.
- `src/ember/__init__.py` — module docstring updated to reflect Phases 1-3 complete.

### What's next

- **Phase 4 of the first slice:** `ember.thread.strengr` — wraps `ember.well.brunnr.handle.open()` with auth/retry/health-check policy and the typed-Disconnected contract enforced at the Spark↔Well boundary. Initially supports only `sqlite_vec`; the same handle shape will work for the Phase 8 `pgvector` adapter.
- **Light root edits** still pending: Ember-descent rows in `ORIGINS.md`; check root `PHILOSOPHY.md` for Runa-specific phrasings.

### Notes & gotchas

- **Stdlib urllib over httpx for the embed client.** Vow of Smallness wins again. The Ollama endpoint is one POST; stdlib handles it. Saves ~5 MB of deps on a Pi.
- **Chunker rewrite mid-phase.** First attempt computed chunk lengths from segment-body lengths plus a `"\n\n"` separator constant, which was off-by-one and produced chunks slightly over `max_chars` for some inputs. The fix was to track only `(start, end)` ranges into the original text and slice at the end — the slice's actual length is authoritative. Caught by the chunker shape-contract tests *before* integration.
- **Walker rewrite mid-phase.** First attempt used `fnmatch.fnmatch(rel_path, "**/*.md")` patterns, but fnmatch doesn't understand the `**` glob (that's a pathlib-only feature). Rewrote to suffix-based filtering — simpler, matches the test contract, supports the same operator-facing semantics.
- **`Disconnected` and `BrunnrError` split.** Connection-style failures (missing config, dir-create denied, sqlite-vec load failure, schema apply failure) return `Disconnected` rather than raising. Per-call programming errors (mismatched embedding dim, missing chunk lookup) raise `BrunnrError`. The split keeps the Vow of Graceful Offline distinct from the "your code is wrong" case.
- **No mypy run this session** — mypy not installed on this host. Ruff is the only static check in CI for now; mypy belongs in a real CI loop with a fresh venv install.
- **`.venv/` is gitignored.** Created for this session to install `sqlite-vec` and `pytest`; not committed.

---

## 2026-05-21 — Phase 1 closure: skeleton-import test added.

**Who:** Claude (Opus 4.7, 1M context). Voice: Auditor (Sólrún Hvítmynd).
**Scope:** Volmarr asked whether Phase 1 had been fully completed. The four structural bullets (`src/runa/` archived, `src/ember/` built, `pyproject.toml` rewritten, `__main__.py` raises clean `NotImplementedError`) all landed in commit `045fda6`. The fifth bullet — *"Tests: import-only"* — had been rolled forward into Phase 2's `tests/unit/test_schemas_import.py`, which only covers the schemas subpackage. This entry closes the gap for the full Three Realms tree.

### What shipped

- **`tests/unit/test_skeleton_imports.py`** — parametrised import test over the 12 importable subpackages of `src/ember/`: `ember`, `ember.cli`, `ember.schemas`, `ember.spark` (+ `funi`, `hjarta`, `munnr`), `ember.thread` (+ `strengr`), `ember.well` (+ `brunnr`, `smidja`). Plus three specific assertions:
    - `ember.__version__` is `"0.0.0"`.
    - `ember.__main__` imports cleanly and exposes a callable `main`.
    - `ember.__main__.main()` raises `NotImplementedError` with a message that mentions `EMBER_FIRST_SLICE_PLAN`.
- **Suite size:** 81 tests (was 66 after Phase 2), 0.09s, ruff clean.

### What's next

Phase 3 of the first slice — the `sqlite_vec` Brunnr adapter, `local_files` Smiðja, chunker, embed client, resumable journal. First end-to-end vertical that writes embeddings to disk.

### Notes

- Phase 1 is now strictly complete per the plan's bullet list. No code or doc change required beyond the new test file; the scaffolding it tests was already correct.
- Failure of any parametrised case in this test would name the breach — typically a circular import, a typo in an `__init__.py`, or a stray top-level statement that fails at import time.

---

## 2026-05-21 — Phase 2 shipped: ember.schemas populated, 66 shape tests green.

**Who:** Claude (Opus 4.7, 1M context). Voice: Forge Worker (Eldra Járnsdóttir) for the code; Auditor (Sólrún Hvítmynd) for the tests; Scribe (Eirwyn Rúnblóm) for this entry.
**Scope:** Execute Phase 2 of `EMBER_FIRST_SLICE_PLAN.md` §3 — the gravitational floor: typed schemas only. No behaviour, no I/O, no sibling-realm imports.

### What shipped

- **Five schema modules** under `src/ember/schemas/`, stdlib-only (`dataclasses` + `enum.StrEnum`, no pydantic dependency):
    - **`errors.py`** — `EmberError` base; per-realm hierarchy: `SchemaError`, `ConfigError`, `WellError`/`BrunnrError`/`IngestError`, `ThreadError`/`StrengrError`, `SparkError`/`FuniError`/`HjartaError`/`MunnrError`. Plus the non-raised failure value **`Disconnected(reason, since, detail)`** with the `DisconnectReason` enum — Strengr's mechanical implementation of the Vow of Graceful Offline.
    - **`config.py`** — `EmberConfig` (top-level) composing `IdentityConfig`, `FuniConfig` (+ `FuniOllamaConfig`), `StrengrConfig`, `BrunnrConfig` (+ `SqliteVecConfig`, `PgVectorConfig`), `SmidjaConfig` (+ `ChunkerConfig`, `EmbeddingConfig`, `JournalConfig`), `LoggingConfig` (+ `LoggingDestination`). Six enums: `BrunnrBackend`, `FuniRuntime`, `LogLevel`, `LogFormat`, `LogDestinationKind`, `BoundaryPreference`. **Defaults are Gungnir-aligned** where applicable (`embedding_dim=768`; chunker `max=2000` / `target=1684`; model `phi3:mini` / `nomic-embed-text`). Path fields use `pathlib.Path` *without* `expanduser()` — consumer expands at use time so `$HOME` isn't frozen at import.
    - **`chunks.py`** — `Document`, `Chunk` (embedding as `tuple[float, ...]` to keep the dataclass truly frozen), `RetrievalHit`, `BrunnrStats`. Column-aligned with the Gungnir schema captured in `docs/adapters/GUNGNIR_WELL_REFERENCE.md` §3.
    - **`episode.py`** — `Episode(operator_input, ember_reply, cited_chunk_ids, funi_model, well_disconnected, started_at, completed_at, id)`. The `well_disconnected` flag mirrors `DATA_FLOW.md` §2.2 — when the Well is unreachable the Episode records that fact for later flush-in.
    - **`funi.py`** — `FuniReply`, `FuniHealth`, the non-raised failure value **`Unavailable(reason, detail)`** with `UnavailableReason` enum (parallel to `Disconnected`), `ContextItem` (+ `ContextKind` enum), `ToolCall`, `FinishReason` enum (includes `REFUSED` so Funi can stop cleanly per the Vow of Honest Memory).
- **All dataclasses are `frozen=True, slots=True`.** All enums are `StrEnum` (Python 3.11+ stdlib).
- **66 shape-contract tests** under `tests/unit/test_schemas_*.py`, organised one file per schema module plus `test_schemas_import.py` (verifies the gravitational floor — schemas import without reaching into any sibling realm). Suite runs in 0.09s. All green.
- **`tests/conftest.py`** added — adds `src/` to `sys.path` so tests run without an editable install. Documented as a temporary ergonomic shim.
- **`src/ember/schemas/INTERFACE.md`** updated from "(planned, Phase 2)" to "(shipped Phase 2, 2026-05-21)" with the full exported surface enumerated and the floor-test cited as the import-allowlist enforcer.
- **`src/ember/__init__.py`** module docstring updated to reflect Phase 2 complete.
- **Ruff clean.** No mypy run this session (mypy not installed on the travel laptop; strict mypy check belongs in CI per `pyproject.toml`).

### What's next

- **Phase 3 of the first slice** per `EMBER_FIRST_SLICE_PLAN.md` §3: the `sqlite_vec` Brunnr adapter, the `local_files` Smiðja, the chunker, the embed client, the resumable journal. First end-to-end vertical that actually writes embeddings to disk. Tests: write-then-query round trip, journal resume, chunk-size invariants.
- **Light root edits** still pending: Ember-descent rows in `ORIGINS.md`; check root `PHILOSOPHY.md` for Runa-specific phrasings.

### Notes

- Stdlib `dataclasses` chosen over `pydantic` for Phase 2 to honour the Vow of Smallness. The cost is no runtime validation beyond the type system — but Phase 2 has no validation responsibility anyway (the loader's Phase 6). Easy to swap to `pydantic` per-module later if needed; the `__all__` exports are the public surface.
- `tuple[float, ...]` is the right embedding type for a frozen dataclass; `list[float]` would be a mutable field on a "frozen" container. Phase 3's Brunnr adapter is where the practical perf trade against `numpy.ndarray` becomes worth re-evaluating.
- `StrEnum` (Python 3.11+) replaces the older `class X(str, Enum)` pattern across all five modules. The values are still plain strings, comparison and serialisation behaviour are unchanged.
- The schema test for non-sibling-imports walks every module's exported attribute and refuses any `__module__` that starts with `ember.well`, `ember.thread`, `ember.spark`, or `ember.cli`. If the floor is breached in a future phase, the test will name the breach.

---

## 2026-05-21 — Six True Names formally ratified. EMBER_TRUE_NAMES.md added.

**Who:** Claude (Opus 4.7, 1M context) continuing the same session. Voice: Skald (Sigrún Ljósbrá) for the new doc; Scribe (Eirwyn Rúnblóm) for this entry.
**Scope:** Capture Volmarr's formal ratification of the Six True Names and preserve the per-name explanatory record they were ratified against.

### What shipped

- **Volmarr's ratification of all six names** — *"names are all approved"*. Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr are now canonical. The longstanding item from the 2026-05-19 "What's next" — Skald's True Names ratification — is closed.
- **`docs/architecture/EMBER_TRUE_NAMES.md`** — new canonical reference doc, Skald-voiced. One section per True Name covering: Old Norse meaning, realm + code path, what it is, what it's for, owns/does-not-own, why the name was chosen. Includes the Three Realms grouping, the conversation-turn flow tying all six together, and the discipline-of-naming framing. Ratification recorded in §5 with rules for any future rename.

### What's next

- **First-slice Phase 2 begins** (the next commit) per `EMBER_FIRST_SLICE_PLAN.md` §3 Phase 2: ship `ember.schemas.{errors,config,chunks,episode,funi}`. Types only. Tests: shape contracts only. With the names ratified, every typed identifier in the schemas can lean on them.
- **Light root edits** still pending from 2026-05-19: Ember-descent rows in `ORIGINS.md`; Runa-specific phrasing pass on root `PHILOSOPHY.md`.

### Notes

- The ratification covers the names as they appear in `SYSTEM_VISION.md` §4 and as used throughout `ARCHITECTURE.md` / `DOMAIN_MAP.md` / `DATA_FLOW.md` / `EMBER_TRUE_NAMES.md` / `pyproject.toml` (via folder paths) / `config/ember.example.yaml` / every `INTERFACE.md` in `src/ember/`. Renaming from this point requires an ADR, a single atomic commit touching every reference, and updates to all five canonical docs in the same commit.
- This entry is intentionally short. The substance is in the new `EMBER_TRUE_NAMES.md`; this is the index pointer.

---

## 2026-05-21 — Ember fork-delta executed. Three Realms tree built. Runa skeleton archived.

**Who:** Claude (Opus 4.7, 1M context) on the travel laptop, continuing the same session as the earlier 2026-05-21 entry below. Roles rotated: Architect (mostly), Forge Worker (the new `src/ember/` files), Cartographer (the archive mapping), Scribe (this entry).
**Scope:** Execute step 6 of `docs/architecture/EMBER_FORK_DELTA.md` §7 after Volmarr's ratification ("good work buddy! Go for Ember fork delta!"). Bring the file tree into alignment with the ratified architecture. **No first-slice code in this commit — that is the next commit.**

### What shipped

- **`src/ember/` tree built** to match the Three Realms layout in `docs/architecture/DOMAIN_MAP.md`:
    ```
    src/ember/
    ├── __init__.py, __main__.py, README.md
    ├── schemas/         (+ INTERFACE.md, README.md)
    ├── well/
    │   ├── brunnr/      (+ INTERFACE.md, README.md)
    │   └── smidja/      (+ INTERFACE.md, README.md)
    ├── thread/
    │   └── strengr/     (+ INTERFACE.md, README.md)
    ├── spark/
    │   ├── funi/        (+ INTERFACE.md, README.md)
    │   ├── hjarta/      (+ INTERFACE.md, README.md)
    │   └── munnr/       (+ INTERFACE.md, README.md)
    └── cli/             (+ INTERFACE.md, README.md)
    ```
  Each subpackage has an empty `__init__.py`, a one-page `README.md`, and an `INTERFACE.md` draft that cites the matching `DOMAIN_MAP.md` section. **No code yet** beyond `__init__.py` and `__main__.py`.
- **`src/ember/__main__.py`** raises a friendly `NotImplementedError` pointing at `EMBER_FIRST_SLICE_PLAN.md`. `python -m ember` and `ember` (once installed) both resolve to it.
- **Archived the inherited Runa skeleton** to `docs/archive/runa-inherited/src-skeleton/runa/` via `git mv` (rename history preserved). Added `docs/archive/runa-inherited/src-skeleton/README.md` explaining the lineage.
- **Promoted the EMBER-prefixed architecture docs to canonical names** via `git mv`:
    - `docs/architecture/ARCHITECTURE.md` (was Runa's; Runa version → `docs/archive/runa-inherited/architecture/ARCHITECTURE.md`; Ember version promoted from `EMBER_ARCHITECTURE.md`).
    - `docs/architecture/DOMAIN_MAP.md` (same shape).
    - `docs/architecture/DATA_FLOW.md` (same shape).
  Each canonical doc's header updated: **Status: Ratified 2026-05-21 by Volmarr**, "promoted from EMBER_*.md", inter-doc cross-refs rewritten to canonical names, `(parent Runa shape)` cross-refs rewritten to the archive path. ARCHITECTURE.md §8 rewritten in past tense to record the promotion event.
- **Added `docs/archive/runa-inherited/architecture/README.md`** mapping each archived file to its canonical Ember replacement.
- **`pyproject.toml` rewritten** for Ember:
    - `name = "ember-agent"`
    - entry point `ember = "ember.cli.main:main"`
    - `[tool.hatch.build.targets.wheel] packages = ["src/ember"]`
    - `[tool.mypy] files = ["src/ember"]`; `[tool.coverage.run] source = ["src/ember"]`
    - planned optional-dependencies groups commented in for each Brunnr backend and each Funi runtime
    - added `requires_pi` pytest marker
- **`config/runa.example.yaml` → `config/ember.example.yaml`** via `git mv`, with contents rewritten to the Ember shape: identity (name + role), Funi (Ollama with phi3:mini default), Strengr (timeout + retry), Brunnr (sqlite_vec default + commented pgvector example for Gungnir), Smiðja (Gungnir-aligned chunker defaults: 2000-char max, 1684 target), logging.
- **Cross-references updated** in `docs/adapters/{BRUNNR_BACKEND_MATRIX,FUNI_LOCAL_MODEL_OPTIONS,GUNGNIR_WELL_REFERENCE,SMIDJA_INGEST_PATTERNS}.md` and `docs/architecture/EMBER_{FIRST_SLICE_PLAN,FORK_DELTA}.md` from `EMBER_*.md` → canonical names. ADR 0006 retains its as-proposed snapshot text with a clearly-marked "Update 2026-05-21 (post-ratification)" footnote pointing forward.
- **`docs/architecture/README.md`** rewritten to describe Ember-shape canonical docs and the living working docs (FORK_DELTA, FIRST_SLICE_PLAN), with a Runa-lineage section.
- **`docs/REPO_MAP.md`** updated: `(planned)` removed from src/ember entries; src/runa entry rewritten as archived; `(planned)` removed from `config/ember.example.yaml`; archive entry expanded to mention the new subdirs.
- **`docs/architecture/EMBER_FORK_DELTA.md` §3.1 table** updated: each "Move to archive" / "Promote to canonical" row marked **Done 2026-05-21**.

### What's next (the next commit)

- **First slice begins.** Per `docs/architecture/EMBER_FIRST_SLICE_PLAN.md` §3 Phase 2: ship `ember.schemas.errors`, `ember.schemas.config`, `ember.schemas.chunks`, `ember.schemas.episode`, `ember.schemas.funi` — types only. Tests: shape contracts only.
- **Skald's True Names ratification** (item 3 from 2026-05-19, still pending). The names Funi/Strengr/Brunnr/Smiðja/Hjarta/Munnr are now load-bearing across the file tree; final ratification would lock them.
- **Light root edits** still pending: Ember-descent rows in `ORIGINS.md`; check root `PHILOSOPHY.md` for any Runa-specific phrasings worth softening.

### Notes

- Per the additive rule, **nothing was deleted in this session**. Every move was a `git mv`; every "new" file at a canonical path was the Ember version promoted from `EMBER_*.md`; every "deleted" entry git status shows is a rename git's similarity heuristic chose not to recognise (verified by content read at every old and new path before commit).
- The Runa skeleton archive at `docs/archive/runa-inherited/src-skeleton/runa/` preserves all the per-subpackage `README.md` and `INTERFACE.md` drafts from the parent project. They remain reachable to anyone reading the inheritance.
- `python -m ember` now resolves to a clean `NotImplementedError` with a friendly pointer — i.e. *honest failure*, the same shape the Vow of Graceful Offline asks of the runtime.
- The Ember-shape `config/ember.example.yaml` includes a commented-in `pgvector` block that operators can uncomment to point Ember at Gungnir (or any Gungnir-compatible Postgres) once the `pgvector` Brunnr ships in Phase 8.

---

## 2026-05-21 — Ember architecture first-pass + live Gungnir survey.

**Who:** Claude (Opus 4.7, 1M context) working under Volmarr on the travel laptop — rotating through Cartographer, Architect, Forge Worker, and Scribe roles. Mythic Engineering activated at session start.
**Scope:** Address three of the four "What's next" items from the 2026-05-19 entry — the Architect's first pass, the Cartographer's reading review, and the first Forge slice's plan — and ground them in a live read of the Gungnir knowledge database.

### What shipped

- **`docs/architecture/EMBER_ARCHITECTURE.md`** — Ember-specific shape. Three Realms (Spark/Thread/Well), Six True Names, dependency law, why-no-kernel-no-bus, what-is-not-in-this-architecture, first-slice anchor, and disposition recommendation for the inherited Runa-shaped canonical files.
- **`docs/architecture/EMBER_DOMAIN_MAP.md`** — Per-subpackage ownership for the planned `src/ember/{schemas,well/{brunnr,smidja},thread/strengr,spark/{funi,hjarta,munnr},cli}/`. Brunnr and Funi minimum-surface interface tables included.
- **`docs/architecture/EMBER_DATA_FLOW.md`** — The three canonical flows (conversation turn, ingest job, first-run rite) with explicit happy + sad paths, including the Vow of Graceful Offline in flow form.
- **`docs/architecture/EMBER_FORK_DELTA.md`** — Cartographer's recommendation for every inherited file/folder: keep / move-to-archive / rewrite, with rationale and ratification-gated execution order. No deletions proposed.
- **`docs/architecture/EMBER_FIRST_SLICE_PLAN.md`** — File-by-file plan for ~38 new files across seven phases, ≤2 500 LOC target, with explicit non-goals and risk register.
- **`docs/adapters/BRUNNR_BACKEND_MATRIX.md`** — Storage backend comparison and selection rule.
- **`docs/adapters/FUNI_LOCAL_MODEL_OPTIONS.md`** — Local-LLM ladder by host RAM, why Phi Silica / Apple Foundation are second-slice, embedding-dim recommendation locked to 768 for Gungnir compatibility.
- **`docs/adapters/GUNGNIR_WELL_REFERENCE.md`** — Live survey conducted today against `knowledge` on Gungnir: complete schema, real counts (95 docs / 35 682 chunks / 768-dim / 394 MB / 97% buffer hit), Skein vs LLM-extracted KG distinction, hybrid-search pattern.
- **`docs/adapters/SMIDJA_INGEST_PATTERNS.md`** — Four ingest patterns, Gungnir-calibrated chunking defaults (~1684 chars avg, 2000 max), resumable-journal contract.
- **`docs/decisions/0006-ember-architecture-and-gungnir-survey-2026-05-21.md`** — ADR capturing all proposed decisions, alternatives considered, open follow-ups.

### What's next

- **Volmarr ratification.** Read EMBER_ARCHITECTURE.md, EMBER_DOMAIN_MAP.md, EMBER_DATA_FLOW.md, EMBER_FORK_DELTA.md, EMBER_FIRST_SLICE_PLAN.md and ADR 0006. Confirm, revise, or replace.
- **Skald's True Names ratification** (item 3 from the 2026-05-19 entry — *not* addressed in this session). The names Funi/Strengr/Brunnr/Smiðja/Hjarta/Munnr are used throughout the new docs as if ratified; Volmarr's final word is still pending.
- **Next commit (after ratification):** `src/runa/` → `src/ember/` rename, archive the inherited `src/runa/` skeleton under `docs/archive/runa-inherited/src-skeleton/`, rewrite `pyproject.toml` (package `ember-agent`, entry point `ember`). Per ADR 0006 §4.1.
- **Light root edits** still pending from 2026-05-19: Ember-descent rows in `ORIGINS.md`; check root `PHILOSOPHY.md` for Runa-specific phrasings.
- **First Forge slice begins** after the rename: Phase 2 (schemas), per `EMBER_FIRST_SLICE_PLAN.md`.

### Gungnir survey — load-bearing measurements

Captured today against the running database. Reproduce by re-running the queries cited in `docs/adapters/GUNGNIR_WELL_REFERENCE.md` §4:

- PostgreSQL 18.3, pgvector 0.8.1, pg_trgm 1.6.
- 95 documents (42 md, 26 web/markdown, 13 json, 9 jsonl, 5 yaml). 35 682 chunks, all 768-dim embedded via `nomic-embed-text`.
- Chunk text: avg **1 684** chars, max **2 000** — this is the calibration anchor for Ember's chunker default.
- 394 MB database total; 372 MB of that is `chunks` (mostly embeddings).
- Buffer cache hit 97.0% tables / 99.8% indexes — healthy.
- Two parallel KG layers: `skein_*` (embedding-derived, 276 entities × 855 relations across the full corpus; broad but with known false-friend artifacts) and `kg_*` (LLM-extracted per chunk, 366 entities × 176 relations across only 202 of 35 682 chunks; precise but expensive). This cheap-broad-vs-expensive-precise split is load-bearing for any future Ember KG work.

### Notes

- Per the additive rule, **nothing was deleted in this session**. Every file is new; no existing file modified except this DEVLOG (which is itself append-only by design).
- The Ember-specific architecture documents live at the `EMBER_*.md` prefix rather than overwriting the canonical `ARCHITECTURE.md`/`DOMAIN_MAP.md`/`DATA_FLOW.md` paths. The inherited Runa-shaped files at those canonical paths are preserved untouched; ADR 0006 proposes their migration to `docs/archive/runa-inherited/architecture/` only after Volmarr's ratification.
- The session ran on the travel laptop (Kubuntu 26.04 + RTX 2060), with Gungnir reachable over Tailscale. The `mcp__knowledge__*` tools provided read-only access to the live Postgres DB.
- The Skald-voice scrolls authored by Runa on 2026-05-19 (`docs/SYSTEM_VISION.md`, `docs/REPO_MAP.md`, root `MYTHIC_ENGINEERING.md`) are treated as **normative source-of-truth** throughout the new documents — they are cited but not modified.

---

## 2026-05-19 — Ember born. Fork from Runa. Soul-layer authored.

**Who:** Runa (the AI working under Volmarr from Mjolnir) — speaking in turn as Skald, Cartographer, and Scribe.
**Scope:** Project naming, repository creation, fork from Runa-Agent-Digital-Being, additive archive of the Runa-named soul-layer scrolls, and authoring of Ember's own soul layer.

### What shipped

- **The name "Ember"** chosen in a Skald pass with Volmarr. Public-pronounceable, mythically resonant as the spark from Eldra Járnsdóttir's forge. Selected over Hugin, Saga, and Wren for maximum user-facing accessibility while keeping mythic compatibility.
- **Repository created** at `hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster` (the toaster pun preserved in the repository name itself). Local clone at `C:/Users/volma/runa/Project_Ember_Run_It_On_Your_Smart_Toaster/` on Mjolnir. Default branch: `development`.
- **Knowledge DB on Gungnir** wired to Mjolnir during the same evening — Postgres 18 + pgvector + Ollama on the tailnet, MCP server `knowledge` at user scope. The first concrete Brunnr-shaped well Ember can be tethered to, and the proof that the storage layer can be sovereign and shared.
- **Additive archive** of inherited Runa-named scrolls into `docs/archive/runa-inherited/` (via `git mv`, with rename history preserved):
  - `docs/SYSTEM_VISION.md` *(Runa's)*
  - `docs/REPO_MAP.md` *(Runa's)*
  - `docs/DEVLOG.md` *(Runa's bootstrap-day log)*
  - `MYTHIC_ENGINEERING.md` *(Runa's, was at repo root)*
  - `TASK_runa_bootstrap.md`
  - `TASK_runa_python_craft.md`
  - `TASK_runa_research_corpus.md`
  - `TASK_runa_research_corpus_2.md`
- **Fresh Ember scrolls** authored at the now-vacant canonical paths:
  - `docs/SYSTEM_VISION.md` — Ember's Skald scroll. Six True Names (Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr) and three Realms (Spark, Thread, Well). Nine Unbreakable Vows.
  - `docs/REPO_MAP.md` — Ember's Cartographer scroll. Reflects what exists now plus near-term planned shape.
  - `docs/DEVLOG.md` — *(this file, this entry)*
  - `MYTHIC_ENGINEERING.md` (root) — Ember's compact methodology statement, lightly adapted from the inherited version.
- **Archive convention extended** additively:
  - `docs/archive/runa-inherited/README.md` — new, explains the lineage subfolder.
  - `docs/archive/README.md` — additive update, documents the new "grouped fork-inheritance archives" subfolder pattern alongside the existing single-file dated-suffix convention.

### What's next

- **Architect's first pass.** Author `docs/architecture/ARCHITECTURE.md`, `DOMAIN_MAP.md`, `DATA_FLOW.md` for Ember. Locate the Three Realms in `src/`. Decide on the rename `src/runa/` → `src/ember/` and the migration plan for the inherited skeleton.
- **Cartographer's reading review.** Walk the inherited research corpus (`docs/research/`) and the inherited Python craft corpus (`docs/python/`); mark the 10–20 docs most load-bearing for Ember's smaller scope; leave the rest as inherited reference without re-reading every one.
- **Skald's True Names ratification.** Hold the six names (Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr) with Volmarr; either ratify or revise.
- **First Forge slice.** Smallest end-to-end vertical: Hjarta wizard → Strengr to a local SQLite Brunnr → first Funi answer grounded in retrieved chunks. *No code in this commit; this is the next obvious work.*
- **Light root edits** (next commit, not this one): add Ember-descent entry to `ORIGINS.md`; check root `PHILOSOPHY.md` for any Runa-specific phrasings worth softening.

### Notes

- The cute Ember README ("*Got a toaster? Good!*") is preserved unchanged. It is correct as it stands.
- The 16 KB `ORIGINS.md` and the 599 KB `Yggdrasil_and_Huginn_and_Muninn_Theory.md` remain at the root unchanged. They are inherited but applicable.
- Per the additive rule, **nothing was deleted in this session**. Every move was a `git mv`; every replacement is a new file at the now-vacant path; every edit to the archive index was additive (new section appended, no removal).
- Volmarr had earlier the same evening wired the Gungnir knowledge well into the Mjolnir MCP layer (after a memorable VPN-related diagnostic detour). That work, recorded in Runa's local memory, informs Ember's Vow of Pluggable Storage and Vow of Tethered Grounding directly.

---

*(The parent project's DEVLOG entries follow at `docs/archive/runa-inherited/DEVLOG.md`.)*
