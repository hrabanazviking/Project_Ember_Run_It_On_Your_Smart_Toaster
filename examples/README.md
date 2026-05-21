# examples/

Reference material that shows how things are *meant* to look. Read
this folder to learn the shape; copy from it when starting your own.

**Last touched:** 2026-05-21 (slice 2 ratified).

---

## Subfolders

| Folder | Holds | State |
|---|---|---|
| `configs/` | Fully-worked example `ember.yaml` files for common deployment shapes. | Scaffold; the operator-facing `config/ember.example.yaml` is the load-bearing template until rich examples are contributed. |
| `sessions/` | Transcripts of meaningful Ember sessions, used as documentation and as evaluation fixtures. | Scaffold; first real session transcripts arrive when slice-2 operators share theirs. |
| `skills/` | Reserved for the (deferred) skill-package pattern. ADR 0013 §3 lists skills as an out-of-scope-for-slice-2 deferral. | Scaffold only; will populate in a future slice. |
| `plugins/` | Reserved for the (deferred) plugin pattern. ADR 0013 §2.7 keeps the plugin scaffold empty until slice 3 drafts the contract. | Scaffold only. |

---

## Rules

- **Examples must actually run against the current `src/ember/`.** CI
  verifies this (when CI is wired; until then, the slice-2 acceptance
  test `tests/integration/test_phase17_acceptance.py` exercises the
  full operator flow against real `sqlite_vec` + mocked Funi).
- **No real secrets, no real personal data.** Use obvious placeholders
  (`OPENROUTER_API_KEY=sk-fake-example`, `volmarr@gungnir` → `you@your-host`).
- **Match the canonical config shape.** Every example yaml is a
  copyable starting point — if it doesn't load via
  `ember.config.load_ember_config()`, it's broken.

---

## Where the real examples live today

Until this folder grows real recipes, operators should look at:

- **`config/ember.example.yaml`** — the full operator-config template
  with every knob and inline comments (slice-2 current).
- **`config/storage.example.yaml`** — three Brunnr setups
  (sqlite_vec / personal Gungnir / shared-Gungnir read-only).
- **`deploy/pi/INSTALL.md`** — eleven sections of operator walkthroughs
  for the slice-2 capability set.

---

## What slice-2 graduates from "example" to "production-grade"

The first slice (0.1.0) shipped with empty example dirs. Slice 2
populated the canonical config templates at `config/*.example.yaml`;
this folder remains a scaffold for the *richer* operator examples
that emerge from real deployments. The intent: when an operator
shares a working multi-host Pi-plus-laptop split that exercises
streaming + pgvector + tools, that recipe lands here as
`configs/pi-laptop-split.yaml` plus a `sessions/` transcript showing
the conversation flow.
