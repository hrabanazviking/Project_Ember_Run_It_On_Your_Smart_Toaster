# 33 — Snapshot and Golden-File Testing

**Category:** Testing
**Runa relevance:** Saga prose generation, Heimskringla prompt translation, audit-log shapes
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

A **snapshot test** (or **golden-file test**) captures the output of code at one point in time, stores it on disk ("the golden"), and verifies on every test run that the output still matches. When the output legitimately changes (a refactor changes whitespace; a new feature adds a field), the diff is reviewed; if intended, the golden is updated. If unintended, the test catches the regression.

For Runa, snapshot tests are the right tool for outputs that are *not easily characterised by assertions*: Saga's narrative chapters, Heimskringla's prompt translations, formatted audit-log entries, README-renderable diagrams. Things where "looks right" is the criterion and any unintended drift is a bug.

## 2. Technique / mechanism

**Tools:**

- **`syrupy`** — github.com/syrupy-project/syrupy. Modern Python snapshot library.
- **`pytest-snapshot`** — github.com/joseph-roitman/pytest-snapshot.
- **`snapshottest`** — older.

**Usage with syrupy:**

```python
def test_saga_prose_chapter(snapshot, episode_log_fixture):
    chapter = saga.write_chapter(episode_log_fixture)
    assert chapter == snapshot
```

First run: snapshot captured to `tests/__snapshots__/test_saga.ambr` (or similar).
Subsequent runs: compared. Diff shown if mismatch.

To regenerate after an intentional change:

```bash
pytest --snapshot-update
```

Then review the diff in git, commit if intentional.

**Golden-file pattern (manual):**

```python
def test_prompt_translation(tmp_path):
    output = heimskringla.translate(logical_prompt, model="claude-sonnet")
    golden = (Path(__file__).parent / "goldens" / "claude_prompt.txt").read_text()
    assert output == golden
```

Manual but simple. The `goldens/` directory is committed to git; updates are explicit file edits.

**Snapshot of structured data:**

```python
def test_audit_entry_shape(snapshot):
    entry = build_audit_entry(some_event)
    # Snapshot the dict representation, not the object
    assert entry.model_dump(mode="json") == snapshot
```

Snapshot of dicts / JSON serialisable forms compares cleanly.

**Snapshot vs deterministic:**

Snapshot only works if the output is *deterministic*. LLM outputs at temperature > 0 are not. Workarounds:
- Pin temperature to 0 in tests.
- Snapshot only the structural shape, not the content.
- Use LLM-as-judge eval ([[48-testing-ai-agents]] in research corpus) for non-deterministic outputs.

**Ignoring volatile fields:**

```python
@pytest.fixture
def stable_audit_entry():
    entry = build_audit_entry(event)
    entry.timestamp = "2026-01-01T00:00:00Z"  # stabilise
    entry.event_id = "FIXED-UUID"
    return entry
```

Or use snapshot tools that support field filtering.

**Multiple snapshots per test:**

```python
def test_multi(snapshot):
    assert step_a() == snapshot
    assert step_b() == snapshot
```

Snapshots are indexed by test name + assertion order.

## 3. Key works / libraries

- **Jest's snapshot testing** (JavaScript) — popularised the pattern.
- **`syrupy`** — github.com/syrupy-project/syrupy.
- **`pytest-snapshot`** — github.com/joseph-roitman/pytest-snapshot.
- **Approval Testing** — books by Llewellyn Falco; conceptual lineage.

## 4. Pitfalls and gotchas

- **Snapshots that drift "naturally".** A snapshot of a model output that changes when the model updates → noisy.
- **Snapshots of huge outputs.** A 100KB snapshot file is hard to review diffs in.
- **Failure to update.** Tests fail "because snapshot is stale"; developer updates without thinking → real regression slips through.
- **Snapshot of non-deterministic output.** Race conditions, random IDs, timestamps. Stabilise or skip.
- **Snapshot of platform-specific output.** Line endings, path separators. Normalise.
- **Snapshot bloat.** Old snapshots not removed when tests change. Periodic prune.
- **`--snapshot-update` as habit.** Updating without review defeats the purpose.

## 5. Applicability to Runa

For **Saga prose generation**:

- Snapshot Saga chapters built from canonical event-log fixtures.
- Update reviewed explicitly when Saga voice changes.

For **Heimskringla prompt translation**:

- Snapshot translated prompts per (logical_prompt, model) pair.
- Catches per-model template drift.

For **audit-log entry shape**:

- Snapshot the JSON shape of each event type. Catches schema drift.

For **REPO_MAP-style generated artifacts**:

- Diagrams or summaries auto-generated from code: snapshot.

What to avoid:

- Don't snapshot LLM outputs at temperature > 0.
- Don't snapshot huge blobs without review tooling.
- Don't auto-update snapshots in CI. Review.
- Don't snapshot things with embedded random UUIDs / timestamps without stabilising.

## 6. Open questions

- **Snapshot for partially-generative output.** LLM-judged similarity instead of strict equality. Possible; immature.
- **Visual diff tooling.** For large snapshots, diff UX matters.
- **Per-environment snapshots.** Different OS, different outputs. Normalise or branch.

## 7. References (curated)

- syrupy-project.github.io/syrupy/.
- github.com/joseph-roitman/pytest-snapshot.
- jestjs.io/docs/snapshot-testing — Jest docs (conceptual).
- Companion docs: [[30-pytest-mastery]], [[34-integration-e2e-testing]], [[48-testing-ai-agents]] (research corpus).
