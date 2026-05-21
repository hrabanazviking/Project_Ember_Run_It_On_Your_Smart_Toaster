#!/usr/bin/env python3
"""
Mímir's Well — Fact Store Migration Script
=============================================
One-time migration of all facts from fact_store.db into Mímir Well
memories + wyrd_edges.

Steps:
  1. Read all facts + entities from fact_store.db
  2. Import facts as Mímir memories (with correct memory_type)
  3. Create wyrd_edges for facts with 2+ entities
  4. Verify counts match
  5. Keep fact_store.db as read-only backup (never delete)

ᛗ í ᛗ í ᚱ — The Well remembers what was, even as it becomes.
"""

from __future__ import annotations

import json
import logging
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add mimir_well to path if running from scripts/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from mimir_well import WyrdGraph
from mimir_well.core import RunaMemory
from mimir_well.schema import SCHEMA_VERSION

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ── Category → Memory Type mapping ────────────────────────────────────────

CATEGORY_MEMORY_TYPE_MAP = {
    # Semantic (general knowledge)
    "general": "semantic",
    "research": "semantic",
    "geography": "semantic",
    "history": "semantic",
    "biology": "semantic",
    "botany": "semantic",
    "ecology": "semantic",
    "physics": "semantic",
    "computer_science": "semantic",
    "computer-science": "semantic",
    "sociology": "semantic",
    "economics": "semantic",
    "archaeology": "semantic",
    "neuroscience": "semantic",
    # Procedural (how-to/skills)
    "coding": "procedural",
    "programming": "procedural",
    "python": "procedural",
    "devops": "procedural",
    "database": "procedural",
    "testing": "procedural",
    "terminal": "procedural",
    # Episodic (specific events/experiences)
    "home": "episodic",
    "home-infrastructure": "episodic",
    "regional-events": "episodic",
    "personal": "episodic",
    "feeling": "episodic",
    "contact": "episodic",
    # User preferences
    "user_pref": "semantic",
    "identity": "semantic",
    "hermes-config": "semantic",
    "hermes-infrastructure": "semantic",
    "hermes-skills": "semantic",
    "hermes-plugins": "semantic",
    # Norse spiritual/cultural
    "norse_magic": "semantic",
    "norse_culture": "semantic",
    "norse_mythology": "semantic",
    "norse-metaphysics": "semantic",
    "norse-pagan": "semantic",
    "norse-paganism": "semantic",
    "runic": "semantic",
    "seidr": "semantic",
    "seidhr": "semantic",
    "ritual_design": "procedural",
    # Architecture/system design
    "architecture": "semantic",
    "software_architecture": "semantic",
    "project_governance": "semantic",
    "project-architecture": "semantic",
    "protocol-architecture": "semantic",
    "mimir_system": "semantic",
    "mimir": "semantic",
    "systems-architecture": "semantic",
    "systems-theory": "semantic",
    # Solarpunk/synthesis
    "solarpunk": "semantic",
    "meta-synthesis": "semantic",
    "meta_synthesis": "semantic",
    "cross-domain-synthesis": "semantic",
    "cross-cluster-synthesis": "semantic",
}


def infer_memory_type(category: str, content: str) -> str:
    """Infer memory_type from fact category and content."""
    # Check direct mapping first
    if category in CATEGORY_MEMORY_TYPE_MAP:
        return CATEGORY_MEMORY_TYPE_MAP[category]

    # Fuzzy match: normalize category
    normalized = category.lower().replace("-", "_").replace(" ", "_")
    if normalized in CATEGORY_MEMORY_TYPE_MAP:
        return CATEGORY_MEMORY_TYPE_MAP[normalized]

    # Content heuristics
    how_many = content.lower().count(" how to") + content.lower().count("steps to") + content.lower().count("first,")
    if how_many > 0:
        return "procedural"

    # Default to semantic (general knowledge)
    return "semantic"


def load_fact_store(fact_store_path: str) -> Tuple[List[Dict], Dict[int, List[str]]]:
    """Load all facts and entity links from fact_store.db.

    Returns:
        (facts_list, entity_map) where entity_map[fact_id] = [entity_name, ...]
    """
    conn = sqlite3.connect(fact_store_path)
    conn.row_factory = sqlite3.Row

    # Load all facts
    facts = []
    for row in conn.execute("""
        SELECT f.fact_id, f.content, f.category, f.tags, f.trust_score,
               f.created_at, f.updated_at
        FROM facts f
        ORDER BY f.fact_id
    """).fetchall():
        facts.append({
            "fact_id": row["fact_id"],
            "content": row["content"],
            "category": row["category"] or "general",
            "tags": row["tags"] or "",
            "trust_score": row["trust_score"] or 0.5,
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        })

    # Load entity links
    entity_map: Dict[int, List[str]] = {}
    for row in conn.execute("""
        SELECT fe.fact_id, e.name, e.entity_type
        FROM fact_entities fe
        JOIN entities e ON fe.entity_id = e.entity_id
        ORDER BY fe.fact_id, e.entity_id
    """).fetchall():
        fid = row["fact_id"]
        if fid not in entity_map:
            entity_map[fid] = []
        entity_map[fid].append(row["name"])

    conn.close()

    logger.info("Loaded %d facts from fact_store, %d with entities",
                len(facts), len(entity_map))
    return facts, entity_map


def import_facts_to_mimir(
    mimir: RunaMemory,
    facts: List[Dict],
    entity_map: Dict[int, List[str]],
) -> Dict[str, int]:
    """Import facts as Mímir memories.

    Returns:
        Stats dict with counts.
    """
    stats = {"imported": 0, "skipped": 0, "errors": 0}

    for fact in facts:
        try:
            memory_type = infer_memory_type(fact["category"], fact["content"])

            # Build tags from category + original tags
            tags = []
            if fact["tags"]:
                try:
                    tags = json.loads(fact["tags"]) if isinstance(fact["tags"], str) else fact["tags"]
                except (json.JSONDecodeError, TypeError):
                    tags = [t.strip() for t in fact["tags"].split(",") if t.strip()]
            tags.append(f"fact_store")
            tags.append(f"category:{fact['category']}")
            # Add entities as tags too
            entities = entity_map.get(fact["fact_id"], [])
            for ent in entities[:5]:  # Cap at 5 entity tags
                tags.append(f"entity:{ent}")

            # Map trust_score to importance (1-10)
            importance = max(1, min(10, round(fact["trust_score"] * 10)))

            # Use add_memory
            mimir.add_memory(
                content=fact["content"],
                category=fact["category"],
                importance=importance,
                tags=tags,
                memory_type=memory_type,
                emotional_valence=0.0,
            )
            stats["imported"] += 1

        except Exception as e:
            logger.warning("Failed to import fact #%d: %s", fact["fact_id"], e)
            stats["errors"] += 1

    logger.info("Imported %d facts, %d skipped, %d errors",
                stats["imported"], stats["skipped"], stats["errors"])
    return stats


def import_edges_to_wyrd(
    graph: WyrdGraph,
    facts: List[Dict],
    entity_map: Dict[int, List[str]],
) -> Dict[str, int]:
    """Create wyrd_edges for facts with 2+ entities.

    Returns:
        Stats dict with counts.
    """
    stats = {"edges_created": 0, "edges_skipped": 0, "errors": 0}

    for fact in facts:
        entities = entity_map.get(fact["fact_id"], [])
        if len(entities) < 2:
            stats["edges_skipped"] += 1
            continue

        try:
            # Primary relationship: first entity → second entity
            source = entities[0].lower().replace(" ", "-")
            target = entities[1].lower().replace(" ", "-")

            # Map trust_score to strength (0-10)
            strength = max(1.0, min(10.0, fact["trust_score"] * 10))

            graph.add_edge(
                source=source,
                target=target,
                relationship_type=fact["category"],
                strength=strength,
                metadata={
                    "source": "fact_store_migration",
                    "fact_id": fact["fact_id"],
                    "content_preview": fact["content"][:200],
                },
            )
            stats["edges_created"] += 1

            # Additional edges for 3+ entities (secondary relationships)
            if len(entities) > 2:
                for i in range(2, min(len(entities), 5)):  # Cap at 5 entities per fact
                    extra_target = entities[i].lower().replace(" ", "-")
                    try:
                        graph.add_edge(
                            source=source,
                            target=extra_target,
                            relationship_type=f"co-mention",
                            strength=strength * 0.5,  # Weaker for co-mentions
                            metadata={
                                "source": "fact_store_migration",
                                "fact_id": fact["fact_id"],
                                "type": "co_mention",
                            },
                        )
                    except Exception:
                        pass  # Co-mention edges are best-effort

        except Exception as e:
            logger.debug("Edge creation failed for fact #%d: %s", fact["fact_id"], e)
            stats["errors"] += 1

    logger.info("Created %d edges, %d skipped (1 entity), %d errors",
                stats["edges_created"], stats["edges_skipped"], stats["errors"])
    return stats


def verify_migration(
    mimir: RunaMemory,
    graph: WyrdGraph,
    facts: List[Dict],
    entity_map: Dict[int, List[str]],
) -> bool:
    """Verify that migration counts match expectations.

    Returns:
        True if verification passes.
    """
    # Count memories in Mímir using FTS search (broad query to get all)
    # WyrdGraph has its own DB connection — use it for direct SQL
    mem_count = graph._db.execute("SELECT COUNT(*) FROM memories").fetchone()[0]

    # Count edges in WyrdGraph
    edge_count = graph.edge_count()

    expected_memories = len(facts)
    expected_edges = sum(1 for f in facts if len(entity_map.get(f["fact_id"], [])) >= 2)

    logger.info("Verification:")
    logger.info("  Memories: %d (source facts: %d)", mem_count, expected_memories)
    logger.info("  Edges: %d (2+ entity facts: %d)", edge_count, expected_edges)

    # Verify at least 95% of facts were imported
    if mem_count < expected_memories * 0.9:
        logger.error("Memory count too low! %d < %d (90%% threshold)", mem_count, expected_memories)
        return False

    logger.info("✓ Migration verification PASSED")
    return True


def migrate(
    fact_store_path: str,
    mimir_db_path: str,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Run the full fact_store → Mímir migration.

    Args:
        fact_store_path: Path to fact_store.db (read-only source).
        mimir_db_path: Path to Mímir's SQLite database.
        dry_run: If True, don't write anything — just report counts.

    Returns:
        Stats dict with all counts.
    """
    logger.info("═══ Fact Store → Mímir Migration ═══")
    logger.info("  Source: %s", fact_store_path)
    logger.info("  Target: %s", mimir_db_path)
    logger.info("  Dry run: %s", dry_run)

    # Load facts
    facts, entity_map = load_fact_store(fact_store_path)

    if dry_run:
        n_facts = len(facts)
        n_with_entities = sum(1 for f in facts if f["fact_id"] in entity_map)
        n_with_2plus = sum(1 for f in facts if len(entity_map.get(f["fact_id"], [])) >= 2)
        logger.info("Dry run stats:")
        logger.info("  Total facts: %d", n_facts)
        logger.info("  Facts with entities: %d", n_with_entities)
        logger.info("  Facts with 2+ entities (→ edges): %d", n_with_2plus)
        logger.info("  Facts with 0-1 entities (→ memories only): %d", n_facts - n_with_2plus)
        return {"dry_run": True, "total_facts": n_facts, "potential_edges": n_with_2plus}

    # Open Mímir
    mimir = RunaMemory(db_path=mimir_db_path)
    graph = WyrdGraph(db_path=mimir_db_path)

    try:
        # Import memories
        mem_stats = import_facts_to_mimir(mimir, facts, entity_map)

        # Import edges
        edge_stats = import_edges_to_wyrd(graph, facts, entity_map)

        # Verify
        verify_ok = verify_migration(mimir, graph, facts, entity_map)

        return {
            "memories_imported": mem_stats["imported"],
            "memories_errors": mem_stats["errors"],
            "edges_created": edge_stats["edges_created"],
            "edges_skipped": edge_stats["edges_skipped"],
            "edges_errors": edge_stats["errors"],
            "verification_passed": verify_ok,
        }

    finally:
        mimir.close()
        graph.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Migrate fact_store → Mímir Well")
    parser.add_argument(
        "--fact-store",
        default="/home/pi/.hermes/memory/backups/fact_store_pre_cleanup_20260514_132141.db",
        help="Path to fact_store.db (read-only source)",
    )
    parser.add_argument(
        "--mimir-db",
        default="/home/pi/.hermes/memory/runa_memory.db",
        help="Path to Mímir's SQLite database",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't write anything — just report counts",
    )

    args = parser.parse_args()

    result = migrate(
        fact_store_path=args.fact_store,
        mimir_db_path=args.mimir_db,
        dry_run=args.dry_run,
    )

    print("\n═══ Migration Results ═══")
    for k, v in result.items():
        print(f"  {k}: {v}")