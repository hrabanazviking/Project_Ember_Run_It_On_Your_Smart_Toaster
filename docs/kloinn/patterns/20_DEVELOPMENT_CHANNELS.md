# 20 — Development Channels

OpenClaw's three-track release model: stable / beta / dev. Why
it matters; what Ember can adopt.

---

## The three channels

### stable

Tagged releases. Battle-tested. Recommended for operators
who want reliability over recent-features.

```bash
npm install -g openclaw@latest
```

### beta

Prerelease tags. Newer features; possible bugs. For
early adopters.

```bash
npm install -g openclaw@beta
```

### dev

Moving `main` branch. Bleeding edge; possible breakage. For
contributors / power users.

```bash
npm install -g openclaw@dev
```

---

## Why this matters

### Stable operators get stability

The cohort that wants "AI assistant that just works" gets
software vetted through beta + dev before reaching them.

### Beta operators help find bugs

Early adopters opt into testing in exchange for early access.
Their bug reports improve stable releases.

### Dev operators ship features

Contributors and power users run the latest code; their
feedback shapes near-term direction.

### All cohorts coexist

Different operators, different tolerances. The channel system
respects this.

---

## What Ember has

PyPI releases. Single channel. No formal beta/dev distinction.

Operators can install from main branch via git:

```bash
pip install git+https://github.com/.../Project_Ember_Run_It_On_Your_Smart_Toaster.git
```

…but this is unofficial; no PyPI integration.

---

## What Ember should adopt

🔵 **Borrow as-is**:

### Three PyPI channels

PyPI supports prereleases. Three channels via versioning:

| Channel | Install command | Version pattern |
|---|---|---|
| **stable** | `pip install ember-agent` | `0.2.0`, `0.3.0`, ... |
| **beta** | `pip install --pre ember-agent` | `0.3.0b1`, `0.3.0rc1` |
| **dev** | `pip install -e .` (from source) | `0.3.0.dev1+sha.abc123` |

`pip install --pre` includes prereleases. By default, pip
ignores them (gives stable users stability).

---

## Versioning discipline

For this to work, we need:

### 1. Semantic versioning

`MAJOR.MINOR.PATCH` for stable.
`MAJOR.MINOR.PATCH-betaN` or `-rcN` for prereleases.

### 2. Clear release notes

Each stable release: what changed, what's deprecated, migration
notes.

### 3. Backward compatibility

Within a major version, never break existing operators. Use
deprecation warnings; remove in next major.

### 4. Test discipline

CI must run on `main` to catch regressions before they hit dev
channel.

---

## What dev-channel operators get

If we ship `0.3.0.dev1+sha.abc123` as a dev release:

- Latest features, possibly half-baked.
- Possible breakage.
- Operator opts into bug-reporting (file issues; we appreciate).

In return:
- Earliest access.
- Shape the direction.
- Recognition (contributor list, etc.).

---

## What beta-channel operators get

- Features not yet in stable but more polished than dev.
- Lower breakage risk than dev.
- Their bug reports improve stable.
- Used to test specific features before stable release.

---

## When to ship beta

A beta release is appropriate when:
- A significant feature is *implemented* but not yet *battle-
  tested*.
- Schema or config changes that operators should review.
- New surface (e.g., Stofa Phase 1 launch).

A beta gives the operator base 2-4 weeks to use the feature in
real workflows before stable.

---

## When to ship dev

Continuously. Every commit on `main` could be a dev release
(via CI auto-publish to PyPI dev channel).

This is *more aggressive* than OpenClaw's "git-cloned dev"
model. PyPI dev releases are *installable like any other*,
without git knowledge.

Risk: clutters PyPI history. Mitigation: delete old dev
releases periodically (keep latest 5-10).

---

## Configuration of channel preference

Operators don't change their channel through Ember config —
they change it via their pip command:

```bash
pip install ember-agent           # stable
pip install --pre ember-agent     # beta
pip install ember-agent==0.3.0.dev5+sha.abc123  # specific dev
```

Ember can offer a CLI helper:

```bash
ember channel current    # shows current installed version's channel
ember channel switch beta # suggests pip command
```

---

## CI pipeline implications

CI needs to:

1. **Run tests** on `main` push.
2. **Auto-publish dev release** to PyPI on every green main
   commit (limit frequency to avoid PyPI quota).
3. **Tag-trigger beta release** when maintainer tags `vX.Y.Zrc1`.
4. **Tag-trigger stable release** when maintainer tags `vX.Y.Z`.

The GitHub Actions setup is moderate; maybe 100 lines of
workflow YAML.

---

## Documentation per channel

Each channel needs:
- A clear "what's in this release" page.
- Known issues.
- Migration notes (if breaking).

OpenClaw has CHANGELOG.md. Ember should too.

---

## What this looks like at scale

After we adopt this:

```
PyPI:
  ember-agent: 0.5.0 (stable, current)
  ember-agent: 0.6.0rc1 (beta)
  ember-agent: 0.6.0.dev34+sha.abc (dev, continuously)

Operators install:
  • 80% on stable
  • 15% on beta
  • 5% on dev

Bug reports flow:
  dev → finds issue → file issue
  beta → confirms issue → file
  stable → unaffected (we fixed it before stable)
```

This is *the open-source release discipline of mature projects*.
Ember should adopt it before V1.0 stable lands.

---

## Risks and mitigations

### Risk: complexity for operators

Three channels = three ways to install. Confusing.

Mitigation: default is stable. Other channels are *opt-in*. No
operator is surprised.

### Risk: maintainer overhead

Maintaining three channels = more work.

Mitigation: dev is automated. Beta is rare. Stable is what we
do anyway.

### Risk: dev releases break user installs

Dev releases on PyPI risk breaking operators who don't pin.

Mitigation: PyPI's `--pre` flag is required; default pip
ignores dev releases. No operator installs them by accident.

---

## What about LTS

Some projects have **Long-Term Support** releases (e.g., Ubuntu
LTS). Backported security fixes for years.

Ember is too small for LTS. We support the *current stable*
and *previous stable* (no further). Operators on older versions
must upgrade for fixes.

This is acceptable for a small project; it would be problematic
for a mass-adopted one. (OpenClaw probably needs LTS at 373k
operators; we don't.)

---

## Closing

Development Channels are **OpenClaw's release discipline at
scale**. Three tracks; clear expectations; operators opt in.

Ember should:
- 🔵 Adopt three-channel PyPI distribution.
- 🟢 Automate dev releases via CI.
- 🟢 Beta when significant features arrive.
- 🟢 Stable on a regular cadence (every 2-4 weeks ideal).
- 🟢 Clear CHANGELOG, migration notes, deprecation policy.

This is a Phase 1 Klóinn adoption — *cheap to implement*,
*high-value for operators*, *signals seriousness*.

Adopt early; benefit forever.
