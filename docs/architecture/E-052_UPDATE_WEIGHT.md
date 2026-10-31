# E-052 — Update weight: the price of an update, per profile

*Part III, slice E-052. Roadmap line: "Update weight: an
update's download + apply cost per profile (metered
connections respected)." The pricing and the manners live
in `ember.updates`; the measured anchors live in the
budget book (`ember.budgets`, `MEASURED_UPDATE_*`); the
gate tests are `tests/unit/test_updates_e052.py`.*

## In plain words

**Keeping Ember up to date is cheap — and now that is
measured, and the rules for spending a person's metered
data are written down before any update channel exists.**
Downloading a whole new Ember core costs about **293 KB**
— less than one photograph on most phones. Applying it
needs, at the very peak, about **1.8 MB** of spare disk
for a moment. That fits every profile in the book, even
the toaster, with room to spare. But cheap is not the same
as free, and it is never silent: on a metered connection —
a capped phone plan, a shared link where bytes are money —
Ember's rule is **ask first, with the price stated**, at
any size. And even on an unmetered connection an update
only ever travels when the person has invited it. The
channel that will carry updates (E-183, signed and
user-invited) now has its costs and its manners ready
before it exists, so it cannot be built careless.

## 1. What existed before (audited this slice)

No updater, no update channel, no pricing anywhere in
`src/ember`: the only "update" hits in the core are config
overlays and storage adapters. The version is 0.2.0 in both
`pyproject.toml` and `ember.__init__`. An operator updates
today the way they installed: by hand, with pip — which is
exactly the shape this slice prices (a wheel download +
a replace-in-place apply), because E-183's channel will
carry the same artefact.

## 2. The price (VM profile, 2026-10-31)

Method: `ember.updates`' own functions on the slice's
final tree (`src/ember`, 125 files before this slice's
module; probe in `~/workspace/.verify-tmp/ember-e052/`).
The download is the wheel shape — the package tree
deflated into a zip (entries sorted, deflate level 9,
built in memory); no real wheel was built because the
build backend is not installed in the campaign env, and
the doc says so rather than dressing the shape up as one.
Bytecode caches excluded, the book's standing rule.

| Cost | Bytes | Note |
|---|---|---|
| Download (wheel shape, deflated) | **293,387 B** (~0.28 MiB) | the same tree stored uncompressed would be ~781 KB — deflation earns its keep |
| Installed (the tree it unpacks to) | **775,675 B** | E-041's package was 729,802 B; the core grew by the slices since, and still weighs under a megabyte |
| Apply peak disk | **1,844,737 B** (~1.76 MiB) | download + old + new: the installer's moment when the wheel, the old package, and the new package all stand on disk at once |

**Per profile** (download ceiling = the profile's install
ceiling from the budget book — an update may not download
more than a whole install may weigh):

| Profile | Download ceiling | This update | Headroom |
|---|---|---|---|
| toaster | 2 MiB | 293,387 B | ~7.1× |
| phone | 4 MiB | 293,387 B | ~14× |
| pi | 8 MiB | 293,387 B | ~28× |
| laptop | 16 MiB | 293,387 B | ~57× |

The apply peak (~1.76 MiB) is likewise inside every
profile's room. One honest boundary: these prices are the
**core's** update. An update that also refreshed the
default extra would add sqlite-vec's wheel to the
download (its installed weight is 165,939 B, E-041); a
*model* pull is never an Ember update — gigabytes, the
model ladder's own act, its own consent.

## 3. The manners (`decide_update`)

One verdict per update, the ladder in order — the first
rung that speaks decides, and every reason states the
byte price:

1. **Over the profile's download ceiling →
   EXCEEDS_BUDGET.** Whatever the connection, whoever
   invited it: the profile cannot carry it as an update.
2. **Metered → ASK_FIRST, at any size.** Even a one-byte
   update asks (a test pins exactly that): metered bytes
   are the operator's money, smallness is not consent,
   and a general invitation given earlier is not consent
   to *this* download at *this* price.
3. **Uninvited → INVITE_REQUIRED.** No silent
   auto-anything — E-183's law, stated here where the
   costs live, so the channel inherits it as a tested
   rung rather than a slogan.
4. **Invited + unmetered + within ceiling → READY.**

Whether a connection *is* metered is the channel's and
the host's to report (E-183); this slice defines what
Ember must do with the fact, and its tests pin the
behaviour for both values. Nothing in this slice
downloads or applies anything: it prices and judges.

## 4. Honest limits

- **Wheel shape, not a built wheel.** A real hatchling
  wheel adds dist-info metadata (83,102 B at E-041,
  uncompressed inside the zip) to the download; the
  deflated total would land modestly above 293,387 B —
  still ~6× under the toaster's ceiling. Re-weigh against
  a real wheel when a build backend first enters the
  campaign env (E-183's ground, at the latest).
- **Same-version apply shape.** The peak formula prices
  old ≈ new. A much larger future version raises the peak
  by its own growth — the formula, not the constant, is
  the durable claim.
- **VM numbers.** x86, Python 3.12.3. Zip deflation is
  platform-stable for the same tree, so the download
  figure travels better than the RAM anchors do; the
  apply peak is arithmetic on it and the installed tree.
- **Extras and members are not in this price.** A member
  is updated by repo checkout (E-043's shape); optional
  extras ride their own wheels when a channel chooses to
  refresh them, priced by the same functions.

## Tests

- `tests/unit/test_updates_e052.py` — **13 passed**
  (default env): tree weighing with caches excluded; the
  download deterministic and smaller than its tree; the
  apply-peak formula; the anchors pinned exactly and
  internally consistent; the measured update fitting
  every profile's ceiling (~7× headroom on the toaster);
  the ceiling derived from the book, never a copy; the
  decision ladder rung by rung (ready / metered asks
  with the price stated, down to a 1-byte update /
  uninvited never silent / over-ceiling refused even
  invited and unmetered, and fitted by the laptop's wider
  ceiling / budget rung speaking before the metered
  rung); and a live-tree re-derivation that fails loudly
  if the core ever outgrows the toaster's ceiling.

- Slice gate Run B (default env, pgvector file excluded):
  **1002 passed, 6 proven-environment failures, 25 skipped,
  1 warning** — the E-051 baseline of 989 plus this
  slice's 13; the 6 failures are the proven environment
  failures (E-004/E-017).
- Slice gate Run D (whole, extras): **1059 passed,
  0 failed, 19 skipped, 1 warning**, exit 0 — the whole
  suite green in the extras shape, the new tests passing
  there as real tests. Method note: by gate time the VM's
  `tempfile` probe had begun refusing new processes
  (EPERM on its O_EXCL probe creates — VM-wide, proven
  across independent agents; /tmp itself stood 99% free
  after a stale 509 MB pytest basetemp from a finished
  foreign run was removed), so Run D ran through a
  wrapper that pre-sets `tempfile.tempdir` before pytest
  loads, bypassing only the probe; every test then ran
  in the canonical shape and the counts are the runner's
  own (log: `~/workspace/.verify-tmp/ember-e052/gate/`).

*Filed by the E-052 slice, 2026-10-31. Next: E-053 —
battery-shaped behaviour (phone-class): duty cycling, no
busy-wait, measured drain shape.*
