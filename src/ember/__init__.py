"""Ember Agent — a small, tethered, runs-anywhere AI companion.

The compact statement of intent lives at ``docs/SYSTEM_VISION.md``.
The compact statement of method lives at ``MYTHIC_ENGINEERING.md``.
The map of every subpackage lives at ``docs/architecture/DOMAIN_MAP.md``.
The plan of the first slice lives at ``docs/architecture/EMBER_FIRST_SLICE_PLAN.md``.

Phase 2 of the first slice is complete: the typed schemas under
:mod:`ember.schemas` are populated and shape-tested. The runtime
subpackages (:mod:`ember.well`, :mod:`ember.thread`, :mod:`ember.spark`,
:mod:`ember.cli`) remain scaffolds; ``python -m ember`` raises
``NotImplementedError`` with a friendly pointer to the plan.
"""

__version__ = "0.0.0"
