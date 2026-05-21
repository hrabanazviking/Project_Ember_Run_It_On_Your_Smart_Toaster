"""Ember Agent — a small, tethered, runs-anywhere AI companion.

The compact statement of intent lives at ``docs/SYSTEM_VISION.md``.
The compact statement of method lives at ``MYTHIC_ENGINEERING.md``.
The map of every subpackage lives at ``docs/architecture/DOMAIN_MAP.md``.

**0.2.0 — slice 2 ratified by ADR 0013 (2026-05-21).**

Ember now supports the full slice-2 operator flow:

- Operator config at ``~/.ember/config/ember.yaml`` (single source of
  truth; Hjarta writes it at first run; env + CLI overlay).
- Streaming Funi replies live in ``ember chat``; Ctrl-C tags partial
  replies with ``[interrupted by operator]``.
- Pluggable Well: ``sqlite_vec`` (default, single file) or ``pgvector``
  (Gungnir-compatible Postgres; ``read_only: true`` protects shared
  Wells).
- Tool use — opt-in via ``tools.enabled: true`` or ``--allow-tools``.
  Three first-party tools: ``search_well`` (STANDING), ``read_local_file``
  (PER_CALL, sandboxed), ``fetch_url`` (PER_CALL, robots.txt). Every
  invocation appended to ``state/tool_audit/<date>.jsonl``.

Earlier slice baselines: 0.1.0 first slice (ADR 0007). Phase ladder
inside slice 2: 0.1.5 (config), 0.1.7 (streaming), 0.1.9 (pgvector),
0.2.0rc1 (tools rc), 0.2.0 (this — ratified).

Operator install guide: ``deploy/pi/INSTALL.md``. The next slice is
ADR 0012 (Auga / Rödd / Bifröst — alternate surfaces); it doesn't
block any current deployment.
"""

__version__ = "0.2.0"
