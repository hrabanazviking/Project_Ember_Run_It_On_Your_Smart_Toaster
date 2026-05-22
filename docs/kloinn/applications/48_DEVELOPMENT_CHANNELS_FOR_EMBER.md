# 48 — Development Channels for Ember

How specifically to adopt OpenClaw's stable/beta/dev release
discipline.

---

## When this lands

🔵 **Phase 1 of Klóinn adoption** — *immediately*. This is one
of the cheapest adoptions.

---

## What changes

Ember currently releases via PyPI tagged versions:

```
0.1.0 → 0.1.5 → 0.1.7 → 0.1.9 → 0.2.0
```

We add the discipline of:

- **stable**: tagged on `main`; production-ready.
- **beta** (or `rc`): tagged on `main`; near-stable; for early
  adopters.
- **dev**: auto-published on every green `main` push.

---

## Versioning

PyPI version pattern:

```
0.3.0           # stable
0.3.0rc1        # release candidate
0.3.0b1         # beta
0.3.0.dev42+sha.abc123  # dev (auto-published)
```

PyPI's `--pre` flag includes prereleases.

```bash
pip install ember-agent           # 0.3.0 stable
pip install --pre ember-agent     # 0.3.0rc1 latest prerelease
pip install ember-agent==0.3.0.dev42+sha.abc123  # specific dev
```

---

## CI pipeline

Add to `.github/workflows/`:

### release-stable.yml

Triggered when maintainer tags `vX.Y.Z`:

```yaml
on:
  push:
    tags:
      - 'v[0-9]+.[0-9]+.[0-9]+'

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - checkout
      - setup python
      - install build deps
      - pytest                  # run tests
      - python -m build         # build wheel + sdist
      - twine upload            # to PyPI
```

### release-beta.yml

Triggered when maintainer tags `vX.Y.ZrcN` or `vX.Y.ZbN`:

```yaml
on:
  push:
    tags:
      - 'v[0-9]+.[0-9]+.[0-9]+rc[0-9]+'
      - 'v[0-9]+.[0-9]+.[0-9]+b[0-9]+'

jobs:
  publish_pre:
    # ... similar to stable ...
```

### release-dev.yml

Triggered on green main pushes (after CI):

```yaml
on:
  workflow_run:
    workflows: ["CI"]
    branches: [main]
    types: [completed]

jobs:
  dev_release:
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    runs-on: ubuntu-latest
    steps:
      - checkout
      - setup python
      - install build deps
      - python scripts/bump_dev_version.py  # adds .devN+sha
      - python -m build
      - twine upload --skip-existing        # to PyPI
```

`bump_dev_version.py` reads current version, appends
`.devN+sha.abc123` where N is the commit count since last
release.

---

## CHANGELOG.md

Per OpenClaw practice, maintain `CHANGELOG.md`:

```markdown
# Changelog

All notable changes to this project will be documented here.
Format: Keep a Changelog (https://keepachangelog.com).
Versioning: Semantic Versioning (https://semver.org).

## [Unreleased]

### Added
- Klóinn-inspired workspace prompt files.
- ember onboard guided tour.

### Changed
- Hjarta setup wizard branches by operator intent.

## [0.3.0] - 2026-06-15

### Added
- Sessions (Klóinn pattern).
- Three release channels.

### Changed
- ember.yaml schema extended for sessions.

### Deprecated
- Direct identity.json editing (use workspace prompt files).
```

Updated per release. Operator-readable.

---

## Documentation

`docs/RELEASES.md`:

```markdown
# Release Channels

Ember releases on three PyPI channels.

## stable

Production-ready. Run:

    pip install ember-agent

## beta

Recent features; possible bugs. Run:

    pip install --pre ember-agent

## dev

Bleeding edge; possible breakage. Run:

    pip install --pre --upgrade --force-reinstall \
        ember-agent==0.3.0.dev*

## Choosing your channel

- **Day-to-day use**: stable.
- **Test upcoming features + report bugs**: beta.
- **Contribute / experimental work**: dev.

You can switch anytime by reinstalling.

## Update cadence

- stable: ~every 2-4 weeks; sometimes longer for major features.
- beta: when a stable release is ~1 week away.
- dev: continuous, per green main commit.

## Deprecation policy

Within a major version, deprecations are warnings; not
removals. We provide ~2 minor versions of warning before
removal in the next major.
```

---

## What about LTS

For now: **no LTS**. Ember supports current stable + previous
stable.

If we reach 100k+ stars with hospital / production users,
revisit. Until then: small project, no LTS overhead.

---

## What dev releases enable

Operators on dev channel can:
- Use new features immediately.
- Report bugs while context is fresh.
- Test specific feature branches via dev builds.

Maintainers gain:
- Faster bug feedback.
- Better confidence in stable releases.
- Early signal on feature reception.

---

## What about breaking changes

Within stable: no breaking changes per minor version.
Between major versions: documented breaking changes; migration
guide.

In beta + dev: breaking changes possible. Operators on these
channels accept this.

---

## Configuration shape

```yaml
ember:
  release:
    channel: stable               # display only; doesn't change anything
    update_check:
      enabled: true               # default on
      auto_check_interval_hours: 168  # weekly
      channel_to_check: stable    # operator's preferred
```

Update check is informational:

```bash
ember update check

You're on ember-agent 0.3.0 (stable).
A newer stable is available: 0.3.1.

Changelog summary:
  - Fixed: pgvector ConnectionError on read_only Wells.
  - Added: ember session export command.

To update:
  pip install --upgrade ember-agent

(Update is not auto-applied.)
```

---

## Operator workflow per channel

### Stable operator

```bash
pip install ember-agent
# ... uses Ember ...
# every few weeks:
ember update check
pip install --upgrade ember-agent
ember upgrade   # post-update tour
```

### Beta operator

```bash
pip install --pre ember-agent
# ... uses Ember; might see bugs ...
# files issues with details ...
# updates more frequently:
pip install --pre --upgrade ember-agent
```

### Dev operator

```bash
pip install --pre ember-agent
# ... daily updates ...
# (auto-update tool: optional cron script)
```

---

## Maintainer workflow

### Cutting a stable release

1. Update CHANGELOG.md.
2. Bump version in `pyproject.toml`.
3. Commit, push.
4. Tag: `git tag v0.3.0 && git push --tags`.
5. CI auto-publishes to PyPI.
6. Update Doctor screen / docs / README highlights.
7. Tweet / announce / etc.

### Cutting a beta

1. Bump version to `0.4.0rc1`.
2. Commit, tag `v0.4.0rc1`.
3. CI publishes.
4. Announce to beta testers.

### Dev releases

1. Push to main with passing CI.
2. CI auto-publishes dev release.
3. Nothing else needed.

This is *the standard discipline of mature open-source*.

---

## What about pre-1.0

We're at 0.2.0 currently. Pre-1.0 conventions:
- Minor version bumps for breaking changes.
- Otherwise mostly compatible.

After 1.0 (post-Yggdrasil-Phase-1?), strict semver:
- Major = breaking.
- Minor = features (compatible).
- Patch = fixes.

---

## What about version pinning by operators

Operators can pin to specific versions:

```bash
pip install ember-agent==0.3.0   # exact
pip install ember-agent~=0.3.0   # 0.3.x
```

For production / Pi-class operators wanting stability: pinning
is sane.

---

## Risk + mitigations

| Risk | Mitigation |
|---|---|
| Dev releases break operators | `--pre` opt-in; default ignores |
| Maintainer forgets to update CHANGELOG | Pre-commit hook check |
| Breaking change shipped to stable accidentally | CI test of common usage patterns |
| Version-numbering confusion | RELEASES.md doc + scripts |

---

## Closing

Development Channels for Ember are **Phase 1 Klóinn
adoption**. Cheap to implement; high signal to operators
that Ember is *seriously maintained*.

Components:
- Three PyPI channels (stable, beta, dev).
- CI workflows for each.
- CHANGELOG.md maintained.
- RELEASES.md documentation.
- `ember update check` command.

This is **engineering discipline shipped as feature**.
Operators benefit; we benefit; the project benefits.

Adopt early — by V1.0 latest. Probably V0.3.
