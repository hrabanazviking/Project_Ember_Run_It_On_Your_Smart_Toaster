"""Ember Agent — a small, tethered, runs-anywhere AI companion.

The compact statement of intent lives at ``docs/SYSTEM_VISION.md``.
The compact statement of method lives at ``MYTHIC_ENGINEERING.md``.
The map of every subpackage lives at ``docs/architecture/DOMAIN_MAP.md``.
The plan of the first slice lives at ``docs/architecture/EMBER_FIRST_SLICE_PLAN.md``.

Phases 1-6 of the first slice are complete: schemas, Well, Thread,
Funi, Hjarta, and Munnr are all populated; :mod:`ember.cli.main`
dispatches the ``ember`` console script. Running ``ember chat`` on a
host with Ollama walks Hjarta on first launch, then enters an
interactive REPL with retrieval + the graceful-offline banner. Phase 7
(acceptance polish + Pi5 install guide) closes the slice.
"""

__version__ = "0.0.0"
