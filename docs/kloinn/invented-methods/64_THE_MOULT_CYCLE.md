# 64 — The Moult Cycle

A new method for *periodic structural maintenance* of Ember's
state — informed by Molty's literal molting and Ember's
dreamstate. The lobster's regenerative cycle as software pattern.

---

## What molting is in lobsters

A lobster grows by:
1. **Stress**: shell becomes too tight as lobster grows.
2. **Pre-moult**: builds new shell underneath.
3. **Moult**: sheds old shell (very vulnerable).
4. **Post-moult**: new shell hardens; growth resumed.

The cycle is *regular but not constant* — happens when
biology signals.

---

## What "Moult Cycle" means for Ember

Ember accumulates *stress* (analogous to outgrowing shell):
- Mímir's pattern store grows with stale patterns.
- Episodes archive accumulates.
- Tool approval history has outdated entries.
- Workspace files have orphan sections.
- Operator preferences shift but old defaults remain.

These stresses *don't break* anything immediately. They
accumulate. Over months: clutter.

The **Moult Cycle** is *deliberate structural maintenance* —
periodic shedding of accumulated stress.

---

## What gets moulted

### Memory layer

- **Stale Muninn associations**: Hebbian weights below
  threshold for > 6 months → prune.
- **Decayed Mímir chunks**: weight near zero for > 12 months →
  archive (still retrievable; just deemphasized).

### Pattern store (meta-learning)

- Patterns with no recent reinforcement → reevaluate.
- Patterns the operator has rejected → mark dormant.

### Session history

- Sessions > 12 months old → archive.
- Sessions marked "not useful" by operator → archive.

### Workspace files

- TOOLS.md auto-regenerated periodically (drift-checked).
- AGENTS.md / SOUL.md: operator notification if very old.

### Tool approvals

- STANDING approvals not used in 6 months → demote to PER_CALL.
- Domains denied 100% of the time → suggest FORBIDDEN.

### Audit log

- Compact > 30 days old.
- Archive > 1 year old.

---

## When the cycle fires

Monthly. Operator-configurable.

```yaml
ember:
  moult_cycle:
    enabled: true
    schedule: "0 3 1 * *"        # 3 AM, 1st of each month
    surface_proposals: true
    auto_apply_low_risk: true
```

Or operator-triggered:

```bash
ember moult
```

---

## What happens during moult

```
[Moult Cycle 2026-05-22T03:00:00]

Examining state...

Memory layer:
  Muninn associations to prune: 47 (weight < 0.01 for > 6 months)
  Mímir chunks to archive: 122 (no access in 12 months)
  
Patterns:
  Reevaluating: 12 meta-learned patterns
  Suggested archive: 3 patterns operator rejected 5+ times
  
Sessions:
  Archive eligible: 89 sessions > 12 months old
  Total disk to recover: ~280 MB
  
Tool approvals:
  STANDING tools idle: 2 (fetch_url:facebook.com, ...)
  Suggested: demote both to PER_CALL
  
Workspace:
  TOOLS.md drift detected: 4 tools in registry not documented
  Suggested: refresh-tools
  
Audit log:
  Records > 30 days: 4,521 — compacting

Proposal summary:
  [Auto-apply, low-risk]
    - Compact audit log (4,521 records)
    - Refresh TOOLS.md
  [Operator review]
    - Prune 47 Muninn associations
    - Archive 122 Mímir chunks
    - Archive 3 patterns
    - Archive 89 sessions
    - Demote 2 STANDING approvals

Auto-applied: compact + refresh.
Surfaced for review: see ember moult review
```

---

## The review interface

```bash
ember moult review

Operator review of moult proposals:

[1/5] Prune 47 Muninn associations (weight < 0.01, 6+ months)
   Impact: Reduces noise in Bifrǫst's mutual reinforcement.
   Risk: Low. Associations can rebuild if relevant returns.
   ▶ Apply
     Skip
     Apply some (operator picks)

[2/5] Archive 122 Mímir chunks (no access in 12 months)
   ...
```

Each proposal shows impact, risk, and Apply/Skip/Custom.

---

## Snapshots before moult

Per Shed Protocol: snapshot before each moult.

```
~/.ember/moult/snapshots/
  2026-05-22T03:00_pre-moult/
    mimir.db
    muninn.db
    sessions/
    patterns.db
    ...
```

Operator can rollback any moult within ~60 days.

---

## What auto-applies vs requires review

Auto-apply (low risk):
- Compact audit log (no semantic change).
- Refresh TOOLS.md (regenerated).
- Vacuum SQLite (storage cleanup).

Requires review (semantic change):
- Pruning associations.
- Archiving sessions.
- Demoting approvals.
- Changing tool defaults.

This is *bounded autonomy* — Ember handles housekeeping,
asks for semantic decisions.

---

## How this composes with dreamstate

| | Dreamstate (Yggdrasil) | Moult Cycle (Klóinn) |
|---|---|---|
| **Frequency** | Nightly | Monthly |
| **Scope** | Recent (last day) | Long-term (months+) |
| **Operator action** | None (silent) | Review required |
| **Snapshot** | Daily (Norns) | Targeted (Shed) |
| **Purpose** | Consolidate memory | Shed accumulated stress |

They complement. Dreamstate keeps short-term memory healthy.
Moult addresses long-term drift.

---

## When operators benefit most

After 6+ months of regular Ember use:
- Pattern store has both useful + obsolete patterns.
- Mímir has rarely-accessed chunks competing with useful ones.
- Sessions accumulate.
- Tool approvals have stale entries.

The first moult is the *most impactful*. Subsequent moults
are smaller incremental cleanups.

---

## Configuration shape

```yaml
ember:
  moult_cycle:
    enabled: true
    
    schedule:
      kind: cron
      expression: "0 3 1 * *"        # 3 AM, 1st of month
      OR: "monthly_idle"             # next idle period after 1 month
    
    auto_apply:
      compact_audit: true
      vacuum_sqlite: true
      refresh_tools_md: true
      tighten_indexes: true
    
    review_required:
      prune_associations: true
      archive_old_chunks: true
      archive_old_sessions: true
      demote_approvals: true
    
    thresholds:
      muninn_weight_for_prune: 0.01
      muninn_months_for_prune: 6
      mimir_months_for_archive: 12
      sessions_months_for_archive: 12
      approval_idle_months_for_demote: 6
    
    snapshot:
      enabled: true
      retention_days: 60
```

---

## What the operator sees long-term

After year 1:
```bash
$ ember moult history

Moult cycles:
  2026-05-22  applied 8 proposals, archived 1.2 GB, 0 rollbacks.
  2026-04-22  applied 5, archived 0.3 GB, 0 rollbacks.
  2026-03-22  applied 12, archived 2.1 GB, 1 rollback.
  ...

Total disk recovered: 5.6 GB
Total entries pruned: 1,247
Snapshots retained: 6 (last 6 months)
```

The system *visibly evolves* — operator sees the cycle.

---

## What this gives Ember

### 1. Long-term sustainability

Without moult: Ember grows endlessly, eventually slow + cluttered.
With moult: continuous renewal, stable performance over years.

### 2. Operator-aligned evolution

Moult surfaces *what no longer fits* the operator. Operator
decides what to keep / archive.

### 3. Storage hygiene

Pi-class operators with limited disk benefit most. Old
sessions + archive prune frees significant space.

### 4. Trust in the system

Operators see *deliberate maintenance*. Not "magic auto-
cleanup" — visible, reviewable, rollback-able.

---

## Risk + mitigations

| Risk | Mitigation |
|---|---|
| Operator forgets to review proposals | Doctor banner reminder; queue persists |
| Auto-apply does wrong thing | Auto-apply is low-risk only; snapshot first |
| Operator rollback after auto-apply | Shed restore works |
| Sessions archived; operator wants back | Archived ≠ deleted; restore command available |

---

## V4+ ship plan

🟢 **Phase 4 of Klóinn adoption** — when operators have been
using Ember 6+ months, the cycle becomes valuable.

Implementation:
- Phase 4: basic moult command + auto-apply low-risk.
- Phase 5: full proposal interface + meta-learning of
  operator's review patterns.

---

## Closing

The Moult Cycle is **Ember's structural maintenance**. Named
for Molty's molting; designed for Ember's long-term care.

Monthly cycle. Auto-applies low-risk. Surfaces semantic
decisions for operator review. Snapshots before. Reversible.

Without it: Ember slowly degrades over years.
With it: Ember evolves cleanly, fitting the operator more
deeply each cycle.

This is *long-term Ember care*. Ship in V4-V5; operators
benefit by V6+.
