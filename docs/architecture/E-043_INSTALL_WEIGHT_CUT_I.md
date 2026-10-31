# E-043 — Install weight cut I

*Part III, slice E-043. Roadmap line: "Install weight cut I:
the heaviest members measured; optional members made truly
optional at install."*

## The cut, in plain words

**Installing Ember from source used to mean downloading the
whole monorepo.** The little wheel was always honest — 305 KB,
the core and nothing else — but the source package (what you
get from a git URL, a tarball or a mirror) weighed **45 MB**,
because it carried every optional member along: a memory
palace's 57 MB of benchmark data, a 24 MB dictionary, a Godot
tabletop, the design lawbook's 11.6 MB PDF. None of those
programs is part of Ember-the-package; the core never imports
any of them. They just happened to live in the same repository,
so they rode along on every source install.

Now they don't. The source package weighs **1.1 MB** — a
**41× cut** — and contains the core, its tests and its
architecture docs. The members are untouched in the repo and
still run from a checkout, exactly as they always have; they
are now *truly optional at install* instead of silently
mandatory. A clean install from the cut source package was
proven end to end (below).

## 1. The heaviest members, measured

Tracked weight per member (working tree, `git ls-files`,
2026-10-31), and what each contributed to the *old* sdist
(unpacked; hatchling already honoured `.gitignore`, so the
two columns differ where a member keeps bulk untracked):

| Member | Tracked | In old sdist |
|---|---|---|
| mempalace | 59,049,715 B | 56,960,935 B (45 MB of it benchmarks/) |
| cleasby-vigfusson-old-norse-dict | 24,221,782 B | 24,075,953 B (18.6 MB test snapshots) |
| Verdandi | 16,800,240 B | 1,610,196 B |
| astrology-engine | 7,477,309 B | 246,799 B |
| Open-VTT | 6,768,730 B | 6,251,917 B (5.3 MB README-IMG/) |
| CloakBrowser (vendored) | 6,420,853 B | 1,341,033 B |
| Hamr | 6,081,769 B | 2,463,468 B |
| kista | 2,770,218 B | 334,483 B |
| mimir-well | 607,675 B | 607,675 B |
| seidr_engine | 103,728 B | 103,728 B |
| bifrost | 77,916 B | 77,916 B |

Not members, but riding in the old sdist: the docs heritage
corpora (codex + Mythic Plan trees, ~16.4 MB unpacked), the
design lawbook PDF (11,595,685 B) + Markdown (1,471,984 B),
and this campaign's own state file (150,892 B). The core
itself: `src/` 740,923 B, `tests/` 728,016 B.

## 2. What was cut, and how

One file changed: `pyproject.toml`, the sdist target's
`exclude` list (the wheel target already shipped
`src/ember` only and is unchanged). Added:

- **Every optional member directory** (the eleven above).
  An sdist exclude is a shipping decision, not a removal —
  nothing was deleted from the repo, and CloakBrowser's
  vendored licences are untouched, as the campaign laws
  require.
- **The docs heritage corpora** — the five codex trees, the
  nine `*_Mythic_Plan` trees, `yggdrasil`, `tui`, `kloinn` —
  the same class as the university corpora the list already
  excluded. Kept in the sdist: `docs/architecture`,
  `docs/audit`, `docs/decisions`, `docs/design`,
  `docs/adapters`, `docs/operations` and the top-level docs.
- **Repo furniture**: `*.pdf`, the lawbook Markdown, and
  `CAMPAIGN_STATE.md`.

## 3. Before / after (hatchling builds, VM, 2026-10-31)

| Shape | Before | After |
|---|---|---|
| sdist .tar.gz | ~45 MB | **1.1 MB** |
| sdist unpacked | 127,162,419 B | **3,464,529 B** |
| wheel | 305 KB | 305 KB (unchanged) |
| files in sdist | ~2,900 | 364 |

Proofs run this slice (scripts + artefacts in
`~/workspace/.verify-tmp/ember-e043/`):

- Both builds made with `python -m build` (hatchling 1.33.0)
  before and after the edit; contents listed and weighed
  per top-level member from the tarballs themselves.
- **Clean source install**: a fresh venv installed from the
  *after* sdist; `ember --help` exits 0, `import ember`
  resolves inside the venv, and no member directory exists
  in site-packages. Installed package + dist-info: 1,491,175 B
  including install-time bytecode caches (the E-041 anchor of
  978,843 B excluded caches and stands).
- The test suite's re-derivation of the sdist file set (from
  `git ls-files` under the declared exclude rules) matches
  hatchling's actual after-build selection **file for file**
  (363 files; the only extra in the real tarball is the
  generated `PKG-INFO`).

## 4. Tests

`tests/unit/test_install_weight_e043.py` — **5 tests**:
every optional member named in the excludes (and still
present in the tree); repo furniture excluded; wheel
core-only with empty core dependencies and no member hiding
in any extra; no member inside `src/ember`; and the
re-derived sdist (a real tar.gz built from the selected
tracked files) must weigh under 2 MiB — the toaster install
ceiling from E-041's book — contain no member path, and
still contain the package, tests and architecture docs.
First run caught a defect in the test itself: plain
`git ls-files` quotes the tree's two non-ASCII paths, so the
reader uses `-z` (recorded in the test).

## 5. Honest limits

- **PyPI serves the wheel first.** Most `pip install
  ember-agent` users already got the 305 KB wheel; this cut
  serves source installs (git URLs, sdists, mirrors,
  `--no-binary`) — a real road on small hardware and slow
  connections, but not the only one.
- **Members have no pip install story, still.** "Truly
  optional at install" means the core install no longer
  *drags* them; giving a member its own installable shape
  belongs to its own Part (IV–X) if it ever needs one.
- **The repo checkout is still 218 MB tracked.** That is a
  clone cost, not an install cost; E-044 continues the diet
  on the dependency side, and E-057 prices every member.
- The installed-size anchor (978,843 B) did not move: the
  wheel is byte-shape-identical, so E-042's budget gate
  stands unmodified.
