# 61 — The Shed Protocol

A new method for *deprecation, migration, and updating
gracefully* — informed by OpenClaw's release discipline and
Ember's Vow of The Unbroken Whole. Named after Molty's
molting.

---

## What "shedding" means

Lobsters molt (shed shells) to grow. Software *also* must shed:
- Old config schemas.
- Deprecated APIs.
- Stale skills.
- Outdated tool implementations.

The **Shed Protocol** is *how* Ember handles these transitions
without breaking operators.

---

## The principle

Every change that *removes or alters* something operator-facing
follows the Shed Protocol:

1. **Announce**: deprecation warning ~2 minor versions before
   removal.
2. **Document**: clear migration path in CHANGELOG.
3. **Tool**: `ember shed migrate <component>` automates
   migration where possible.
4. **Remove**: in the planned future version.
5. **Recover**: snapshot before; rollback if operator finds
   issues.

This is **structured molting** of the codebase.

---

## Example: deprecating identity.json

Suppose V4 deprecates `identity.json` in favor of `AGENTS.md`
(workspace prompt file).

### V4 release (announcement)

```bash
$ ember chat
Warning: identity.json is deprecated in V4; will be removed
in V6. Migrate to AGENTS.md (workspace prompt file).

Run: ember shed migrate identity-to-agents-md

Continuing for now (still works).
```

Operator sees warning; understands timeline.

### V4-V5 (migration available)

```bash
$ ember shed migrate identity-to-agents-md

Migrating identity.json → workspace AGENTS.md...

Current identity.json:
  agent_name: ember
  operator_name: volmarr
  primary_register: warm
  ...

Proposed AGENTS.md:
  # Ember
  You are Ember, sovereign companion.
  Your operator is Volmarr.
  Register: warm by default.
  ...

Apply migration? [y/n]: y

  Created: ~/.ember/workspace/AGENTS.md
  Backed up: ~/.ember/identity.json.shed-2026-05-22
  
Migration complete. identity.json no longer required.
You can delete the .shed-* backup once confident.
```

Migration is *one command*; operator-visible; reversible.

### V6 release (removal)

```bash
$ ember chat
identity.json was deprecated in V4 and is being removed in V6.

Your installation still has identity.json. You should migrate:

  ember shed migrate identity-to-agents-md

After migration, the file can be safely removed.
Without migration, some V6 features may not work properly.

Continue with legacy identity.json (V6 may not behave correctly)? [y/n]:
```

Operator gets fair warning + path forward.

---

## What the protocol covers

### Config schema changes

```yaml
# V4
ember:
  brunnr:
    backend: sqlite_vec
    sqlite_vec_path: ~/.ember/well.db   # field name

# V5 (renamed)
ember:
  brunnr:
    backend: sqlite_vec
    sqlite_vec:
      path: ~/.ember/well.db            # nested
```

Shed Protocol:
1. V5 accepts both forms; warns on old.
2. Auto-migration via `ember shed migrate config-schema-v4-to-v5`.
3. V7 removes old form (after 2-version warning).

### Skill API changes

If V6 changes the Skill Protocol, community skill authors get:
- Warning when their skill registers via old protocol.
- Migration guide in changelog.
- 2-version transition period.

### Tool removal

If a tool is removed:
- V4: deprecation warning.
- V5: continued availability with warning.
- V6: removed; operator must use alternative or disable.

---

## The shed snapshot

Before any migration, Shed takes a snapshot:

```
~/.ember/shed/snapshots/
  2026-05-22T14-30-00_pre-identity-migration/
    identity.json
    ember.yaml
    ...
```

Operator can:
- Inspect: `ember shed inspect 2026-05-22T14-30-00_*`.
- Restore: `ember shed restore 2026-05-22T14-30-00_*`.
- Delete: `ember shed delete 2026-05-22T14-30-00_*`.

---

## What this is NOT

🔴 **Reject**:

### 1. Silent migrations

We *never* migrate without operator consent. The migration is
*explicit*; the operator runs the command.

### 2. Forced migrations

Operators can refuse to migrate. Some features may degrade
(e.g., stuck on legacy config); but Ember doesn't break.

### 3. Migration-as-uninstall

Migrations don't remove functionality. They *transition* one
shape to another.

---

## Configuration shape

```yaml
ember:
  shed:
    enabled: true
    
    deprecation_warnings:
      enabled: true
      show_on_every_run: false      # tiresome; show once per day
      show_in_doctor: true
    
    snapshots:
      enabled: true                  # take before any migration
      retention_days: 60
    
    auto_migrate:                    # tools available
      - identity-to-agents-md
      - config-schema-v4-to-v5
      - ...
```

---

## The "shed history" command

```bash
ember shed history

Recent shed events:

  2026-05-22 14:30   migration   identity-to-agents-md   [success]
  2026-05-15 09:12   warning     deprecation: ember.brunnr.sqlite_vec_path
  2026-04-30 18:45   migration   config-schema-v3-to-v4   [success]

Total: 3 events.
Snapshots retained: 2 (1 deletable).
```

Operator-visible history of system evolution.

---

## How this composes with the Norns

Per Yggdrasil's Norns backup system: full daily snapshots.

Shed Protocol's snapshots are *targeted* — just the files being
migrated. Smaller, faster, scope-specific.

Both exist:
- **Norns**: full state snapshot every day during dreamstate.
- **Shed**: targeted snapshot before each migration.

Restore via either works.

---

## What about V0 → V1 transitions

When Ember reaches V1.0 (post-Yggdrasil-Phase-1?), the V0
series ends. V0 operators upgrading to V1 will face a
"major version migration."

Shed Protocol handles this:

```bash
$ pip install --upgrade ember-agent
Installing ember-agent 1.0.0...

⚠  Major version upgrade (0.x → 1.0).

The Shed Protocol will guide you through any required
migrations. Run:

  ember shed migrate v0-to-v1

This will:
  - Migrate config schema (if changed).
  - Migrate identity.json to workspace prompt files.
  - Migrate sessions to new format.
  - Take a snapshot first; reversible.

Proceed? [y/n]
```

Operator-controlled; explicit; documented; reversible.

---

## Migration discovery

Available migrations:

```bash
$ ember shed list

Available migrations:
  identity-to-agents-md        — Move identity.json to workspace AGENTS.md
  config-schema-v4-to-v5       — Migrate to nested brunnr config
  episode-format-v1-to-v2      — Upgrade episode storage format
  session-tags-v0-to-v1        — Add session tagging support

Run `ember shed describe <name>` for details.
Run `ember shed migrate <name>` to apply.
```

Operator sees what's available; chooses what to apply.

---

## Migrations are scripts

Each migration is a small Python script in `src/ember/shed/migrations/`:

```python
class IdentityToAgentsMdMigration:
    NAME = "identity-to-agents-md"
    DESCRIPTION = "Move identity.json to workspace AGENTS.md"
    
    def detect(self, ember_root: Path) -> bool:
        """Is this migration needed for the current install?"""
        return (ember_root / "identity.json").exists() and not (
            ember_root / "workspace" / "AGENTS.md"
        ).exists()
    
    def plan(self, ember_root: Path) -> MigrationPlan:
        """What will the migration do?"""
        return MigrationPlan(
            actions=["create AGENTS.md", "preserve identity.json"],
            preview="...",
        )
    
    async def apply(self, ember_root: Path) -> MigrationResult:
        """Run the migration."""
        # ... implementation ...
```

Each migration is *contained* + *inspectable*. CI tests each.

---

## What about *runtime* deprecation

Some deprecations happen at runtime, not config:

```python
# In code:
warnings.warn(
    "Ember.brunnr.read_chunks() is deprecated; use search_well() instead. "
    "Will be removed in V6.",
    DeprecationWarning,
)
```

Operators using Ember as a library see these via Python's
warnings. Operators using CLI/Stofa see via Doctor.

---

## What about *operator-authored* skills

When core changes affect skill APIs:

```bash
$ ember chat
Warning: skill 'ember-skill-X' uses deprecated tool registration API.
This will not work in V6. Contact skill author or migrate.

Continuing for now.
```

Skill authors maintain their own migration. Ember can offer
a `ember skill migrate <skill>` if author provides a migration
script.

---

## Risks + mitigations

| Risk | Mitigation |
|---|---|
| Operator misses deprecation warning | Doctor screen shows; `ember shed list` shows |
| Migration script bug breaks operator | Snapshot first; restore command |
| Migration is incomplete | Lock CI tests per migration |
| Operator refuses migration; later breaks | Honest warnings about consequences |

---

## Closing

The Shed Protocol is **Ember's discipline for graceful
evolution**. Named for Molty's molting (acknowledging
OpenClaw). Used to:

- Deprecate old shapes.
- Migrate operators to new shapes.
- Snapshot before; restore if needed.
- Communicate clearly throughout.

This is **The Unbroken Whole made operational**. Ember can
*change* without *breaking* operators. The shell grows;
nothing is lost.

Implementation cost: modest. Long-term value: enormous. Ship
in V1 release as foundational discipline.
