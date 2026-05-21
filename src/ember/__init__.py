"""Ember Agent — a small, tethered, runs-anywhere AI companion.

The compact statement of intent lives at ``docs/SYSTEM_VISION.md``.
The compact statement of method lives at ``MYTHIC_ENGINEERING.md``.
The map of every subpackage lives at ``docs/architecture/DOMAIN_MAP.md``.

**0.1.5 (slice-2 Phase 9): operator config loader live.**

Edit ``~/.ember/config/ember.yaml`` to change Funi model, Brunnr path,
chunker defaults, logging, etc. — every key is optional and falls
through to defaults if absent. Environment variables (e.g.
``OLLAMA_HOST``) overlay on top of file values. Hjarta writes the
initial file at first-run.

First slice (0.1.0) ratified 2026-05-21. Slice 2 in progress per
``docs/architecture/EMBER_SECOND_SLICE_PLAN.md``.
"""

__version__ = "0.1.5"
