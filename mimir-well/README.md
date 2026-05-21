# Mímir's Well — AI Memory Database

```
    ᛗ   ᛁ   ᛗ   ᛁ   ᚱ
   ╔══════════════════════╗
   ║   ⛤  MÍMIR'S WELL  ⛤ ║
   ╠══════════════════════╣
   ║  ╭──────────────╮   ║
   ║  │  ◉  wisdom   │   ║
   ║  │  ◉  memory   │   ║
   ║  │  ◉  knowledge│   ║
   ║  ╰──────┬───────╯   ║
   ║         │           ║
   ║    ◯◯◯◯◯◯◯          ║
   ║   ◯       ◯ ᚠᚢᚦᚨᚱᚲ ║
   ║    ◯◯◯◯◯◯◯          ║
   ╚══════════════════════╝
   Where wisdom meets persistence
```

A **persistent, self-healing AI memory database** with Ebbinghaus forgetting curves, FTS5 full-text search, contradiction detection, and knowledge promotion. Built on SQLite with WAL mode for concurrent safety.

## ✨ Features

- **🧠 Ebbinghaus Decay** — Memories fade over time unless reinforced, just like human memory
- **🔄 Self-Healing** — Automatic corruption detection, orphan cleanup, and integrity repair
- **💾 Backup Rotation** — Timestamped backups with configurable retention limits
- **🐙 GitHub Backup** — Push sanitized exports to GitHub for offsite storage
- **⚡ Contradiction Detection** — Find opposing preferences, valence inversions, and knowledge conflicts
- **📈 Knowledge Promotion** — Crystallize high-importance memories into permanent knowledge
- **🔍 FTS5 Search** — Full-text search across memories, knowledge, and saga events
- **🎭 Emotional Context** — Track valence (-1.0 to +1.0) for mood-aware recall
- **🗃️ Knowledge Graph** — Entities and relationships with typed, weighted edges
- **🧵 Thread-Safe** — WAL mode with thread-local connections
- **🗄️ Transactional** — All writes are atomic; no partial state on crash

## 📦 Installation

```bash
pip install mimir-well
```

Or from source:

```bash
git clone https://github.com/runafreyjasdottir/mimir-well.git
cd mimir-well
pip install -e .
```

## 🚀 Quickstart

```python
from mimir_well import RunaMemory

# Create or open a memory database
db = RunaMemory()

# Store a memory
mid = db.add_memory(
    "I prefer dark themes for coding",
    category="preference",
    importance=7,
    emotional_valence=0.5
)

# Search memories
results = db.search_memories("dark themes")

# Recall high-importance memories
core_memories = db.recall_by_importance(min_importance=8)

# Recall by emotional context
happy_memories = db.recall_by_mood(target_valence=0.7)

# Full-text search
fts_results = db.fts_search("memories", "python AND programming")

# Create entities and relationships
db.add_entity("odin", "deity", components={"domain": "wisdom"})
db.add_entity("thor", "deity", components={"domain": "thunder"})
db.set_relationship("odin", "thor", "father_of", strength=9)

# Detect contradictions
contradictions = db.detect_contradictions()

# Promote important memories to knowledge
db.promote_to_knowledge(min_importance=8)

# Apply Ebbinghaus forgetting curve
decay_report = db.decay(half_life_days=30)

# Run consolidation (decay + promote + prune)
report = db.consolidate()

# Backup with rotation
db.backup_with_rotation(max_backups=7)

# Check database health
health = db.health_check()

# Self-repair
repairs = db.repair()

# Export to JSON
db.export_to_json("/path/to/export.json")

# Always close when done
db.close()
```

## 🔧 Configuration

Mímir's Well reads from `~/.mimir_well/mimir-well-config.json`:

```json
{
  "db_path": "~/.mimir_well/mimir_well.db",
  "half_life_days": 30,
  "min_importance": 1,
  "max_backups": 7,
  "active_decay": true,
  "log_level": "INFO",
  "backup_repo": ""
}
```

Environment variables (override config):

| Variable | Description |
|---|---|
| `MIMIR_DB_PATH` | Database file path |
| `MIMIR_LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `MIMIR_BACKUP_REPO` | GitHub repo URL for backups |

## 📖 API Reference

### `RunaMemory(db_path=None, config=None)`

Main class. Opens or creates a database at `db_path` (defaults to `~/.mimir_well/mimir_well.db`).

#### Core Methods

| Method | Description |
|---|---|
| `add_memory(content, category, tags, importance, emotional_valence)` | Store a new memory |
| `get_memory(memory_id)` | Retrieve a memory by ID |
| `search_memories(query, category, limit)` | LIKE search |
| `fts_search(table, query, limit)` | FTS5 full-text search |
| `update_memory(memory_id, **kwargs)` | Update memory fields |
| `delete_memory(memory_id)` | Delete a memory |

#### Recall Methods

| Method | Description |
|---|---|
| `recall_by_importance(min_importance, category, limit)` | Retrieve important memories |
| `recall_recent(hours, limit)` | Recent memories |
| `recall_by_mood(target_valence, tolerance, limit, category)` | Mood-matched memories |

#### Knowledge & Entities

| Method | Description |
|---|---|
| `add_knowledge(domain, content, source, confidence)` | Store knowledge |
| `search_knowledge(domain, query, limit)` | Search knowledge |
| `add_entity(entity_id, entity_type, components, state)` | Add/update entity |
| `get_entity(entity_id)` | Get entity by ID |
| `set_relationship(entity_a, entity_b, relationship_type, strength, metadata)` | Create relationship |
| `add_saga_event(event_type, entity_id, data, participants)` | Record life events |

#### Decay & Promotion

| Method | Description |
|---|---|
| `decay(half_life_days, min_importance)` | Apply Ebbinghaus forgetting curve |
| `consolidate()` | Decay + promote + prune in one pass |
| `promote_to_knowledge(min_importance)` | Crystallize memories into knowledge |
| `detect_contradictions(category, limit)` | Find conflicting beliefs |

#### Backup & Healing

| Method | Description |
|---|---|
| `integrity_check(repair)` | Check DB integrity, optionally repair |
| `repair(aggressive)` | Fix orphans, inconsistencies, and corruption |
| `backup_to(backup_path)` | Create a single backup |
| `backup_with_rotation(backup_dir, max_backups)` | Timestamped backup with rotation |
| `restore_from(backup_path)` | Restore from a backup file |
| `github_backup(repo_url, branch, commit_msg, strip_personal)` | Push sanitized backup to GitHub |
| `export_to_json(export_path)` | Export all data as JSON |
| `rebuild_fts()` | Rebuild FTS5 indexes |

## 🧠 Ebbinghaus Decay

Mímir's Well implements the **Ebbinghaus forgetting curve** — memories naturally decay in importance over time unless reinforced by access. The formula:

```
R(t) = importance × 0.5^(t / half_life)
```

Where:
- **R(t)** = retained importance after *t* days
- **half_life** = days for importance to halve (default: 30)
- **t** = days since last access

Memories below `min_importance` are flagged for pruning. Recent accesses **reinforce** importance — the digital equivalent of spaced repetition.

```python
# Apply forgetting curve
report = db.decay(half_life_days=30)
# → {"decayed": 14, "pruned": 2, "reinforced": 5}
```

## 🔄 Self-Healing

The Norns maintain the threads of fate. Mímir heals what time has damaged:

```python
# Check integrity
health = db.integrity_check()
# → {"healthy": True, "checks": {...}, "issues": []}

# Auto-repair
repairs = db.repair(aggressive=True)
# → {"orphaned_relationships": 3, "fixed_timestamps": 1, "vacuumed": True}
```

Checks include:
- SQLite integrity verification
- FTS index consistency
- Orphaned relationships and access logs
- Importance and valence range validation
- Null/empty content detection

## 🐙 GitHub Backup

Push sanitized exports to GitHub for offsite storage:

```python
result = db.github_backup(
    repo_url="https://github.com/yourorg/memory-backups",
    strip_personal=True  # Redact emotional details
)
# → {"exported": True, "pushed": True, "timestamp": "20240101_120000"}
```

Set the repo URL in `mimir-well-config.json` under `"backup_repo"` or the `MIMIR_BACKUP_REPO` environment variable.

## 🤝 Contributing

Pull requests are welcome! The Well grows deeper with each contribution.

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m "feat: my feature"`
4. Push: `git push origin feature/my-feature`
5. Open a PR

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.

---

*ᚠ ᚢ ᚦ ᚨ ᚱ ᚲ — Mímir's Well, where wisdom meets persistence*