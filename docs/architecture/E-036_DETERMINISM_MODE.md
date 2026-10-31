# E-036 — Determinism mode for tests/benchmarks (seeded)

*Part II, slice E-036. Roadmap line: "Determinism mode for
tests/benchmarks (seeded)."*

## Why

A test or a benchmark that cannot be re-run is an anecdote.
Before E-036, Ember's generation requests carried the
operator's conversational sampling (temperature 0.7, top_p
0.9) and **no seed at all** — neither implemented backend was
ever told a seed, so the same prompt against the same model
could legitimately answer differently on every run, and
nothing in Ember could ask it not to. There was also no
one-run way to ask: a benchmark meant editing the config
file and hoping the sampling change was the only difference.

## The mode

Determinism mode is a switch in the one config surface
(E-033), judged in exactly one place
(`ember.spark.funi.determinism`):

- **Config:** `funi.determinism.enabled` (default `false`)
  and `funi.determinism.seed` (default `42`), documented in
  `config/ember.example.yaml`. **One-run CLI:** `ember
  --deterministic …` uses the configured seed; `ember
  --seed N …` turns the mode on for that invocation with
  seed N. Neither flag is ever saved (the `--allow-tools`
  overlay shape).
- **Off (the default):** nothing changes. The effective
  options are the operator's configured options, copied, and
  **no `seed` key exists in any request** — a normal request
  is byte-identical to its pre-E-036 shape, pinned by
  wire-level tests on both backends.
- **On:** the *effective* options for every generation
  request carry the configured seed and a temperature of
  **0.0** (greedy decoding). The operator's configured
  temperature is never mutated — adapters compute effective
  options at open time through
  `determinism.effective_options(...)`, and switching the
  mode off restores the configured sampling exactly. Every
  other option (top_p, num_predict / max_tokens, timeout)
  rides as configured.
- **Per backend, in its own grammar:** Ollama receives the
  seed as its `seed` generation option (inside `options`);
  Aesir receives it as the native route's top-level `seed`
  field — a field Aesir's API support matrix v1 explicitly
  names — present only when the mode is on, in both the
  complete and streaming request bodies.
- **A bad seed is refused, never repaired:** with the mode
  enabled, a negative or non-integer seed (a bool is not a
  seed) makes each adapter's `open()` return its typed
  `Unavailable(CONFIG_INVALID)` naming the seed, before any
  request is sent — Ollama does not even probe, and Aesir
  judges the seed before its key file is read. A disabled
  mode's seed is inert data and is not judged.

## Retrieval: deterministic by construction, always

Generation was the variable half; the audit also checked
what Ember itself ranks. The chunker and the extractive
summariser are pure functions, ingest walks files in sorted
order, and **the core uses no `random` module anywhere**
(grep-proven this slice). One real nondeterminism was found
and FIXED in scope: hybrid search fused its two ranked
lists with RRF and broke score ties by **dict insertion
order** — i.e. by which search happened to return a chunk
first — in both Brunnr adapters, and the underlying SQL
rankings (`ORDER BY distance` / `ORDER BY rank` /
`ORDER BY embedding <=>` / `ORDER BY ts_rank`) named no
tie-break at all, leaving equal-score order to the engine.
Both adapters now break every tie on the chunk's id:
RRF sorts by `(-score, chunk_id)`, and the SQL orderings
carry the id as a secondary key — with one proven
exception: sqlite_vec's vector search cannot take a
second ORDER BY key (vec0 KNN queries allow ONLY a single
`ORDER BY distance` clause; the first E-036 gate run
raised `OperationalError` on exactly that, in 5 tests),
so its returned hits are re-sorted by `(-score, chunk_id)`
in Python instead, with the reason recorded at the site.
The fused-order fixture (two chunks swapping ranks
between the vector and text searches, exactly equal RRF
scores) returns id order under both arrival orders.
One honest residue: when equal-distance chunks straddle
the KNN `k` boundary itself, which of them the engine
returns is vec0's choice, below Ember's floor. This is
always on, not a mode: ranking the same store the same
way is not a benchmark feature, it is correctness.

## Honest limits

- **The mode makes Ember's requests reproducible; it does
  not promise byte-identical answers.** Whether a given
  model + engine build honours its seed contract (and how
  floating-point batching on a given accelerator treats
  greedy decoding) is that backend's truth. No live model
  was run for this slice: every claim above is proven over
  mocked transports shaped from the backends' own
  contracts, the E-022/E-023 pattern. A live seeded-repeat
  proof belongs with Part III's real-hardware work, on a
  named device.
- **Records are not frozen.** Timestamps (episode times,
  diary dates, audit stamps) and generated ids (tool-call
  uuids, pending-journal filenames, Smiðja job ids) still
  carry wall-clock and random values — by design: they are
  records of *when* and *which*, not inputs to generation.
  A benchmark comparing replies should compare reply text
  and finish reasons, not the diary.
- **ThoughtForge (E-024, candidate) is not covered:** its
  frozen `think()` surface takes no seed from Ember, and
  Ember does not shadow ThoughtForge's config — if the
  layer is ever wired into the turn, seeded cognition is
  its own slice, judged against its own contract then.
- The unimplemented runtimes (llamacpp, lmstudio,
  phi_silica, apple_foundation) have no requests to seed;
  when one is bound it must route its options through
  `effective_options` like the two implemented adapters —
  the registry/conformance shape leaves it nowhere else
  honest to go.

## Tests

`tests/unit/test_determinism_mode_e036.py` — **19 passed,
2 skipped** in the default env (the skips are the two
fixtures needing the sqlite_vec extra), **21 passed** with
extras: the pure contract (off = unchanged + seedless,
on = greedy + seed + the rest preserved, repeat-identical,
base dict never mutated), seed judgement (negative ×2,
bool, inert-when-off), the TOML config load, the CLI
overlay (no-flag identity, `--deterministic`, `--seed`
implies the mode, parser shape), Ollama on the wire
(seedless default request; seeded greedy request; negative
seed refused with zero requests sent), Aesir on the wire
(no seed by default; native seed field in complete and
streaming bodies; seed judged before the key file), the
RRF tie fixture under both arrival orders, and the
real-store vector tie fixture (identical embeddings,
chunk_id order).
