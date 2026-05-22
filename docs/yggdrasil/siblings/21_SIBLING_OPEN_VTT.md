# 21 — Sibling: Open-VTT

> *"Not part of Yggdrasil."*

A separate project. Godot-based virtual tabletop. Kept in the
monorepo for archival reasons.

---

## What it is

Open-VTT is a virtual tabletop (VTT) for tabletop role-playing
games — like Roll20 or Foundry VTT, but self-hosted and built
in Godot.

Per memory ([[project-environment]]), this is the operator's
bachelor's thesis basis. It lives in the monorepo for
historical reasons; it isn't part of the Yggdrasil
integration plan.

---

## Why this is in the matrix anyway

For completeness. Future readers of this design tree may
notice the `Open-VTT/` directory and wonder why it isn't
addressed. This file says: *we know; it's intentional.*

---

## What we will NOT do with Open-VTT

- **Integrate it into Ember.** No realm role.
- **Refactor it.** Independent project; independent
  development.
- **Use it as a "Stofa for D&D" surface.** Not the right
  shape; Stofa is a single-operator AI hall, not multi-
  player game support.
- **Bridge their cosmologies.** Open-VTT may use D&D-style
  fantasy; Yggdrasil uses Norse household register. Not a
  match.

## What we MIGHT do (long-horizon)

If, in some distant future, Ember gains a "play tabletop RPG
with me" mode:

- An Ember-as-game-master MCP server (slice-4+).
- Could plug into Open-VTT as a player.
- Could read campaign notes from the Well.
- Could roll dice via a math tool.

This is **decades out** if it happens at all. Not planned.

---

## What we WILL do (immediate)

- **Document the relationship** (this file).
- **Leave the directory in place.**
- **Update `.gitignore` / `pyproject.toml`** to make sure
  Open-VTT contents don't sneak into Ember's PyPI sdist
  (the existing `[tool.hatch.build.targets.sdist]` exclude
  list handles this).

---

## Closing

Open-VTT is a real project. It's just not Ember's project.
The monorepo can hold multiple operator projects without them
needing to know about each other.

Yggdrasil binds eleven siblings. Open-VTT is the twelfth
sibling in the monorepo but NOT in the constellation. That's
fine. The cosmos has room for things outside the tree.
