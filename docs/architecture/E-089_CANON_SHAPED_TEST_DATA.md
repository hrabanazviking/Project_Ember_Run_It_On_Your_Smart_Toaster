# E-089 — Canon-shaped test data only

*Part V, slice E-089. Roadmap line: "Canon-shaped test
data only (synthetic; no real companion history in
fixtures)." The conformance battery is
`tests/unit/test_canon_test_data_e089.py`; the first-duty
finding that outgrew this slice — docket 126 — is
recorded in §4, with its regression pin in the E-075
battery.*

## In plain words

**No test in this tree remembers anything real.** Every
fact, conversation, and person the root test suite has
ever fed the companion's memory is invented — a harbour
ferry that leaves at dawn, a beekeeper with nine hives,
two fixture companions called Ember and Sage. This slice
audited the whole root test tree to prove that, fixed
the one place it was not quite true, and left a guard
running so it stays true.

The one place: three of Part V's own batteries
(E-080/E-081/E-082) ran their invented facts under a
**real companion identity** as the fixture persona — the
fabricated ferry and beekeeper facts were filed under
the name of Volmarr's actual companion. No real history
was in the data; the *name* was real, and a fabricated
fact under a real name is exactly the shape this slice
exists to prevent. Those batteries now run under the
canon fixture persona **ember**, unchanged in every other
respect, and their gates re-ran green (the slice record
carries the counts).

And the first duty outgrew its errand: the owed clean
Run D turned out never to have been blocked by machine
load at all. Its recurring single failure was a
**125-byte Unix socket path** — over the 108-byte limit —
created by the campaign's own gate method (a deep
overlay TMPDIR under a long pytest test name). That is
docket 126, §4 below: proven, fixed in the instrument,
and regression-pinned. The "load-truth contention
artifact" classification carried by E-083–E-088's
records is corrected there.

## 1. The audit — method

Surfaces scanned (this slice's scope, stated):

- the root `tests/` tree, every source-shaped file
  (`.py`, `.md`, `.json`, `.txt`, `.yaml`, `.yml`),
  excluding `__pycache__` (compiled residue, not source);
- the campaign batteries under `tests/unit/` were read
  individually where the scan flagged them;
- `examples/` was read for the same shapes (its one
  credential-shaped string is a `<redacted>` placeholder
  in a README, not data);
- member suites (`mimir-well/tests/`, `Verdandi/tests/`,
  and kin) were **sampled, not swept**: they are elder
  member code with their own custody (E-005's rule), and
  §3 classifies what the sample showed. The guard in
  this slice governs the root tree — the campaign's own
  fixtures — and says so.

Markers hunted: real identity names (the companion's,
the householder's, family names), real mailbox domains,
real life facts (benefits programmes, the car, other
worlds and machines by name), credential shapes, and
every `persona_id` / `user_id` / `persona` value in the
tree, censused exactly.

## 2. What the scan found

**The canon, as it already stood.** Part V's batteries
share one invented world, deliberately: the harbour
ferry leaving at dawn carrying letters between the
islands (FERRY), its reworded question (the boat carrying
post between the isles), and the beekeeper who keeps
nine hives behind the orchard and trades honey at the
winter market (BEES). Around it, smaller synthetic
shapes per slice: Sage's adversarial notes and vault
word (E-083), Mabel's year of ferry-and-honey days
(E-088), the diary whose ferry bell wakes the writer
(E-081). Fixture personae across the whole root tree,
censused by the battery: **ember (the principal), sage,
ember-2 (the near-miss namesake), mabel, default, other,
p, p1, saga** (E-031's one-off tagged persona) — plus
four invalid slugs (`../sage`, `Not A Slug`,
`Not A Slug!`, `not a slug!`) whose whole job is to be
refused by persona validation. The battery pins this set:
a new persona id appearing in any test fails the gate
until it is added to the canon consciously. (The pin
earned its keep inside this very slice: its first run
caught `saga` and `Not A Slug!`, which the hand census
had missed — both synthetic, both now in the set by
name, which is exactly the conscious act the pin
exists to force.)

**The one real-history shape — fixed.** As §0 states:
35 persona/user references in E-080/E-081/E-082 named a
real companion identity. Renamed to the canon persona
`ember` (36 lines touched across the three files,
including one comment), semantics unchanged — each use
was the battery's principal persona, opposed to `other`
or to no one. The three batteries re-ran green after
the rename (slice record).

**Emails and credentials.** Exactly one email-shaped
string exists in the root test tree:
`alice:hunter2@example.com` in the elder fetch-url
hardening tests — a synthetic credential-in-URL shape,
on the reserved example domain. The battery pins that
every email-shaped string in the tree ends at
`example.com`.

**The fixtures library is empty — recorded, not
"fixed".** `tests/fixtures/` holds only its README,
which promises "seed memories, sample conversations,
mock model responses…" as a shared library. In fact
every fixture in the campaign lives inline in its own
battery (the ferry/beekeeper world is re-declared per
file, E-080's embedder copied forward by E-082–E-088).
That is a broken promise in a README-shaped place, but
it is also why the audit was tractable: there is no
unswept fixture store. This slice does not refactor
eight batteries onto a shared module (churn without a
defect); it records the truth here and in the battery,
which pins the fixtures directory's current contents
so any file added there enters the scanner's census
loudly. Whether the library should be built for real
is a Part XII docs question (E-193/E-194), not a
Part V data question.

## 3. The controlled name — an allowlist, with reasons

One real name does appear in the root test tree, in
eleven files, and none of them is fixture history. The
battery holds the exact set as an allowlist — the name
appearing in any other test file fails the gate — and
each entry's reason is stated in the battery itself
(`VOLMARR_ALLOWLIST`). In summary:

- **Connection-shape username (6 files):** elder tests
  for the pgvector adapter put the householder's name
  in connection strings and a fake keyring, because the
  documented real backend's shape is what parsing and
  redaction tests must prove against. No facts, no
  history — a username in a URL.
- **The guarded live test (1 file):**
  `test_pgvector_real_backend.py` names the real corpus
  it would run against *if* its backend were reachable;
  it is skip-guarded and is a live-integration shape,
  not a fixture.
- **Governance needles (3 files):** Part V doc-pinning
  tests assert the phrase "Volmarr's word" stands in
  campaign docs where a verdict is reserved to him —
  the name appears as an authority marker in prose
  about decisions, never as remembered data.
- **A system name (1 file):** the Hermes hack's
  `volmarr-core` producer namespace (E-068) — a program's
  name, not a person's history.
- **A filename (1 file):** the design lawbook's tracked
  filename, named by E-043 to prove it is excluded from
  the install weight.

Member suites, sampled: `mimir-well/tests/` uses the
householder's name the same way its product code does —
the member's own trust model names its trusted source
(`TRUSTED_SOURCES`), and its namespacing tests exercise
that name as a user id with invented one-line contents
("built a solar water heater"). That is the member's
own elder test estate, written against its own product
shape before this campaign; it is classified here as
**the member's house style, not root fixtures**, and is
not rewritten by this slice. If Volmarr wants the
member estate held to the root rule, that is a Part XI
stewardship question on his word — recorded as an open
note, not silently decided either way.

## 4. Docket 126 — the clean Run D was blocked by a socket path, not by load

**The duty.** E-085 through E-088 each closed with the
same note: Run D (the whole root suite with its optional
extras supplied) kept finishing one failure short of
clean, the failure always
`test_load_truth_e075.py::test_live_mini_run_is_correct`,
classified — on the evidence then gathered — as a
load/contention artifact of the live-hub mini-run.

**This slice's evidence.** E-089's first-duty Run D:
**1529 passed, 1 failed, 20 skipped** (605.30 s), the
same single failure. But the standalone re-runs then
failed **consistently, at low load** (1 failed / 7
passed, three times, load ~1.3–5) — which contention
cannot explain. Running the hub by hand under the same
environment stayed up indefinitely. The difference
between the hand run and the instrument's run was the
address: the instrument boots the hub with
`VERDANDI_HOME` under the caller's workdir, and the
hub's socket is `runa.sock` inside it. Under the
campaign's gate method the caller's workdir is a pytest
`tmp_path` under the overlay TMPDIR —

```
/home/hatch/workspace/.verify-tmp/ember-e089/tmp2/
pytest-of-root/pytest-0/test_live_mini_run_is_correct0/
state-mini/runa.sock        = 125 bytes
```

— and a Unix domain socket path is capped at **108
bytes** (`sun_path`, NUL included). The hub's bind
failed, the hub exited rc=1, and the instrument
reported "hub exited early rc=1". Re-running the same
test with a short TMPDIR: **8 passed**. Every Run D and
Run B since E-083 that used the deep overlay TMPDIR
carried this trap armed; whether load *also* hurt some
of those runs is unknowable now, and the earlier
records' classification is hereby corrected to:
**mechanism proven — socket path length; contention
unproven and no longer needed as an explanation.**

**The fix** (`Verdandi/load_truth.py`, the instrument
itself — the hub is innocent): when the natural socket
path would reach 108 bytes, `measure_profile` relocates
its state dir to a short scratch dir (`vd-lt-` prefix)
directly under the system temp root, measures exactly
as before, and removes the scratch dir in its `finally`,
after the hub is stopped. Proven in the formerly
failing shape: with the deep overlay TMPDIR the E-075
battery runs **8 passed** (now 9, with the pin below),
and no `vd-lt-` directory is left behind.

**The pin** (E-075 battery, the instrument's home):
`test_live_mini_run_survives_a_deep_workdir` builds a
workdir whose natural socket path is ≥108 bytes by
construction, asserts the trap is armed, and requires
a correct measurement with no errors and no leftovers.

**Consequence for the gate.** With the trap disarmed,
the campaign's gate method (overlay TMPDIR) no longer
manufactures this failure: this slice's closing Run D
is the first one run with the fix in the tree, and its
result stands in the slice record as the clean-Run-D
question's answer, one way or the other, from the
runner's own log.

## 5. What this slice did not do

- No member test estate was rewritten (§3's open note
  is Volmarr's to call, via Part XI).
- No shared fixture module was built (§2: churn
  without a defect; the census guard is the substance).
- No elder test was edited except the three Part V
  batteries' persona rename, and no README anywhere
  was touched.
- The pgvector username shapes were classified, not
  scrubbed: they test redaction against the real
  documented shape, and scrubbing them would weaken
  the very tests that keep real credentials out of
  logs.
