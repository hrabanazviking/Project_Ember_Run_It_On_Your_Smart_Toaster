"""
Mímir's Eye — The All-Seeing Dashboard
=========================================

Flask web UI that peers into Mímir's Well, showing memory stats,
search, relationship graph, and knowledge insights.

ᛖ ᛃ ᛖ — The Eye sees all that the Well holds.

Author: Runa Gridweaver Freyjasdottir
Created: 2026-05-14 (T2-2)
"""

from flask import Flask, render_template_string, request, jsonify, redirect, url_for
import json
import sqlite3
import os
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter

# ─── Configuration ─────────────────────────────────────────────────────
DEFAULT_DB_PATH = str(Path.home() / ".hermes" / "memory" / "runa_memory.db")
DEFAULT_FACT_DB = str(Path.home() / ".hermes" / "memory_store.db")
DEFAULT_PORT = 8421

app = Flask(__name__)
app.config["DB_PATH"] = os.environ.get("MIMIR_DB_PATH", DEFAULT_DB_PATH)
app.config["FACT_DB_PATH"] = os.environ.get("FACT_DB_PATH", DEFAULT_FACT_DB)


# ─── Database helpers ──────────────────────────────────────────────────
def get_db(db_key="DB_PATH"):
    path = app.config.get(db_key, DEFAULT_DB_PATH if db_key == "DB_PATH" else DEFAULT_FACT_DB)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def query_db(db_key, sql, args=(), one=False):
    conn = get_db(db_key)
    try:
        cur = conn.execute(sql, args)
        rv = cur.fetchone() if one else cur.fetchall()
        return rv
    finally:
        conn.close()


# ─── Template ──────────────────────────────────────────────────────────
DASHBOARD_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ᛗ Mímir's Eye — Memory Dashboard</title>
    <style>
        :root {
            --bg: #0a0a0f;
            --surface: #12121a;
            --border: #2a2a3a;
            --text: #e0e0e8;
            --text-dim: #888898;
            --accent: #7b68ee;
            --accent-dim: #5a4fcf;
            --runa-blue: #4fc3f7;
            --runa-green: #66bb6a;
            --runa-red: #ef5350;
            --runa-gold: #ffd54f;
            --norse-purple: #9c27b0;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: var(--bg);
            color: var(--text);
            font-family: 'JetBrains Mono', 'Fira Code', monospace;
            font-size: 14px;
            min-height: 100vh;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            text-align: center;
            font-size: 28px;
            color: var(--accent);
            margin: 20px 0 5px;
            letter-spacing: 3px;
        }
        .subtitle {
            text-align: center;
            color: var(--text-dim);
            font-size: 13px;
            margin-bottom: 30px;
        }
        .nav {
            display: flex;
            gap: 12px;
            justify-content: center;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        .nav a {
            color: var(--accent);
            text-decoration: none;
            padding: 8px 16px;
            border: 1px solid var(--border);
            border-radius: 6px;
            transition: all 0.2s;
            font-size: 13px;
        }
        .nav a:hover, .nav a.active {
            background: var(--accent);
            color: var(--bg);
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }
        .card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 20px;
        }
        .card h2 {
            color: var(--accent);
            font-size: 16px;
            margin-bottom: 12px;
            letter-spacing: 1px;
        }
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
        }
        .stat {
            text-align: center;
            padding: 10px;
        }
        .stat .value {
            font-size: 28px;
            font-weight: bold;
            color: var(--runa-blue);
        }
        .stat .label {
            font-size: 11px;
            color: var(--text-dim);
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .stat.dim .value { color: var(--text-dim); }
        .stat.green .value { color: var(--runa-green); }
        .stat.gold .value { color: var(--runa-gold); }
        .stat.red .value { color: var(--runa-red); }
        .stat.purple .value { color: var(--norse-purple); }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 8px 12px;
            text-align: left;
            border-bottom: 1px solid var(--border);
            font-size: 13px;
        }
        th {
            color: var(--accent);
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        tr:hover { background: rgba(123, 104, 238, 0.08); }
        .tag {
            display: inline-block;
            padding: 2px 8px;
            background: rgba(123, 104, 238, 0.15);
            border: 1px solid var(--accent-dim);
            border-radius: 4px;
            font-size: 11px;
            margin: 2px;
        }
        .importance {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }
        .importance.high { background: rgba(239, 83, 80, 0.2); color: var(--runa-red); }
        .importance.mid { background: rgba(255, 213, 79, 0.2); color: var(--runa-gold); }
        .importance.low { background: rgba(102, 187, 106, 0.2); color: var(--runa-green); }
        .search-bar {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .search-bar input {
            flex: 1;
            padding: 10px 16px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 6px;
            color: var(--text);
            font-family: inherit;
            font-size: 14px;
        }
        .search-bar input:focus {
            outline: none;
            border-color: var(--accent);
        }
        .search-bar button, .btn {
            padding: 10px 20px;
            background: var(--accent);
            color: var(--bg);
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-family: inherit;
            font-weight: bold;
            font-size: 13px;
        }
        .btn:hover { opacity: 0.9; }
        .bar {
            height: 8px;
            background: var(--border);
            border-radius: 4px;
            overflow: hidden;
            margin-top: 4px;
        }
        .bar-fill {
            height: 100%;
            border-radius: 4px;
            transition: width 0.5s ease;
        }
        .memory-item {
            padding: 12px;
            margin: 8px 0;
            background: rgba(123, 104, 238, 0.04);
            border-left: 3px solid var(--accent);
            border-radius: 4px;
        }
        .memory-item .meta {
            color: var(--text-dim);
            font-size: 11px;
            margin-bottom: 4px;
        }
        .memory-item .content {
            font-size: 13px;
            line-height: 1.4;
        }
        .full-width {
            grid-column: 1 / -1;
        }
        footer {
            text-align: center;
            color: var(--text-dim);
            font-size: 11px;
            margin-top: 40px;
            padding: 20px;
            border-top: 1px solid var(--border);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>ᛗ Mímir's Eye</h1>
        <div class="subtitle">The Well of Wisdom — Memory Dashboard</div>

        <div class="nav">
            <a href="/" class="{{ 'active' if tab == 'overview' else '' }}">Overview</a>
            <a href="/?tab=memories" class="{{ 'active' if tab == 'memories' else '' }}">Memories</a>
            <a href="/?tab=relationships" class="{{ 'active' if tab == 'relationships' else '' }}">Relationships</a>
            <a href="/?tab=knowledge" class="{{ 'active' if tab == 'knowledge' else '' }}">Knowledge</a>
            <a href="/?tab=factstore" class="{{ 'active' if tab == 'factstore' else '' }}">Fact Store</a>
        </div>

        {% if tab == 'overview' %}
        <!-- ─── Overview ──────────────────────────────────────────── -->
        <div class="grid">
            <div class="card full-width">
                <h2>ᛗ Memory Well — Statistics</h2>
                <div class="stat-grid">
                    <div class="stat blue">
                        <div class="value">{{ stats.total_memories }}</div>
                        <div class="label">Memories</div>
                    </div>
                    <div class="stat green">
                        <div class="value">{{ stats.total_knowledge }}</div>
                        <div class="label">Knowledge</div>
                    </div>
                    <div class="stat gold">
                        <div class="value">{{ stats.total_relationships }}</div>
                        <div class="label">Relationships</div>
                    </div>
                    <div class="stat purple">
                        <div class="value">{{ stats.total_entities }}</div>
                        <div class="label">Entities</div>
                    </div>
                    <div class="stat">
                        <div class="value">{{ stats.total_saga }}</div>
                        <div class="label">Saga Events</div>
                    </div>
                    <div class="stat">
                        <div class="value">{{ stats.total_conversations }}</div>
                        <div class="label">Conversations</div>
                    </div>
                </div>
            </div>

            <div class="card">
                <h2>Category Distribution (Top 15)</h2>
                {% for cat, count in stats.categories %}
                <div>
                    <span style="color: var(--text-dim); font-size: 12px;">{{ cat }}</span>
                    <span style="float: right; font-size: 12px;">{{ count }}</span>
                    <div class="bar"><div class="bar-fill" style="width: {{ (count / stats.cat_max * 100)|int }}%; background: var(--accent);"></div></div>
                </div>
                {% endfor %}
            </div>

            <div class="card">
                <h2>Importance Distribution</h2>
                {% for imp, count in stats.importance_dist %}
                <div>
                    <span style="font-size: 12px;">Importance {{ imp }}</span>
                    <span style="float: right; font-size: 12px;">{{ count }}</span>
                    <div class="bar"><div class="bar-fill" style="width: {{ (count / stats.imp_max * 100)|int }}%; background: {% if imp >= 8 %}var(--runa-red){% elif imp >= 5 %}var(--runa-gold){% else %}var(--runa-green){% endif %};"></div></div>
                </div>
                {% endfor %}
            </div>

            <div class="card">
                <h2>Relationship Types (Top 15)</h2>
                {% for rtype, count in stats.relationship_types %}
                <div>
                    <span style="font-size: 12px;">{{ rtype }}</span>
                    <span style="float: right; font-size: 12px;">{{ count }}</span>
                    <div class="bar"><div class="bar-fill" style="width: {{ (count / stats.rel_max * 100)|int }}%; background: var(--norse-purple);"></div></div>
                </div>
                {% endfor %}
            </div>

            <div class="card">
                <h2>Top Entities by Connections</h2>
                <table>
                    <tr><th>Entity</th><th>Connections</th></tr>
                    {% for name, count in stats.top_entities %}
                    <tr><td>{{ name }}</td><td>{{ count }}</td></tr>
                    {% endfor %}
                </table>
            </div>

            <div class="card">
                <h2>Recent High-Importance Memories</h2>
                {% for mem in stats.recent_important %}
                <div class="memory-item">
                    <div class="meta">#{{ mem.id }} · {{ mem.category }} · ⭐{{ mem.importance }} · {{ mem.timestamp[:16] }}</div>
                    <div class="content">{{ mem.content[:200] }}{% if mem.content|length > 200 %}...{% endif %}</div>
                </div>
                {% endfor %}
            </div>

            <div class="card">
                <h2>Fact Store Bridge</h2>
                <div class="stat-grid">
                    <div class="stat blue">
                        <div class="value">{{ fact_stats.total_facts }}</div>
                        <div class="label">Facts</div>
                    </div>
                    <div class="stat green">
                        <div class="value">{{ fact_stats.total_entities }}</div>
                        <div class="label">Entities</div>
                    </div>
                    <div class="stat gold">
                        <div class="value">{{ fact_stats.total_links }}</div>
                        <div class="label">Links</div>
                    </div>
                </div>
            </div>
        </div>

        {% elif tab == 'memories' %}
        <!-- ─── Memories ──────────────────────────────────────────── -->
        <div class="card full-width">
            <h2>Search Memories</h2>
            <form class="search-bar" method="get">
                <input type="hidden" name="tab" value="memories">
                <input type="text" name="q" placeholder="Search memories..." value="{{ query }}" autofocus>
                <select name="category" style="padding: 10px; background: var(--surface); border: 1px solid var(--border); color: var(--text); border-radius: 6px;">
                    <option value="">All Categories</option>
                    {% for cat in categories %}
                    <option value="{{ cat }}" {% if selected_cat == cat %}selected{% endif %}>{{ cat }}</option>
                    {% endfor %}
                </select>
                <select name="min_importance" style="padding: 10px; background: var(--surface); border: 1px solid var(--border); color: var(--text); border-radius: 6px;">
                    <option value="0">Any Importance</option>
                    {% for i in range(1, 11) %}
                    <option value="{{ i }}" {% if min_imp == i|string %}selected{% endif %}>Importance ≥ {{ i }}</option>
                    {% endfor %}
                </select>
                <button type="submit">Search</button>
            </form>
        </div>

        <div class="card full-width">
            <h2>Results ({{ results|length }})</h2>
            {% for mem in results %}
            <div class="memory-item">
                <div class="meta">
                    #{{ mem.id }} · <span class="tag">{{ mem.category }}</span>
                    · <span class="importance {% if mem.importance >= 8 %}high{% elif mem.importance >= 5 %}mid{% else %}low{% endif %}">⭐{{ mem.importance }}</span>
                    · {{ mem.timestamp[:16] }}
                    {% if mem.tags %}{% for t in mem.tags_list %}<span class="tag">{{ t }}</span>{% endfor %}{% endif %}
                </div>
                <div class="content">{{ mem.content }}</div>
            </div>
            {% endfor %}
            {% if not results %}
            <p style="color: var(--text-dim); text-align: center; padding: 40px;">
                No memories found. Try a different search.
            </p>
            {% endif %}
        </div>

        {% elif tab == 'relationships' %}
        <!-- ─── Relationships ──────────────────────────────────────── -->
        <div class="card full-width">
            <h2>Entity Relationships</h2>
            <form class="search-bar" method="get">
                <input type="hidden" name="tab" value="relationships">
                <input type="text" name="entity" placeholder="Search entity..." value="{{ rel_entity }}">
                <select name="rel_type" style="padding: 10px; background: var(--surface); border: 1px solid var(--border); color: var(--text); border-radius: 6px;">
                    <option value="">All Types</option>
                    {% for rt in rel_types %}
                    <option value="{{ rt }}" {% if selected_rel_type == rt %}selected{% endif %}>{{ rt }}</option>
                    {% endfor %}
                </select>
                <button type="submit">Search</button>
            </form>
            <table>
                <tr><th>Entity A</th><th>Type</th><th>Entity B</th><th>Strength</th></tr>
                {% for rel in rel_results %}
                <tr>
                    <td>{{ rel.entity_a }}</td>
                    <td><span class="tag">{{ rel.rtype }}</span></td>
                    <td>{{ rel.entity_b }}</td>
                    <td><span class="importance {% if rel.strength >= 8 %}high{% elif rel.strength >= 5 %}mid{% else %}low{% endif %}">{{ rel.strength }}</span></td>
                </tr>
                {% endfor %}
            </table>
        </div>

        {% elif tab == 'knowledge' %}
        <!-- ─── Knowledge ─────────────────────────────────────────── -->
        <div class="card full-width">
            <h2>Knowledge Base</h2>
            <form class="search-bar" method="get">
                <input type="hidden" name="tab" value="knowledge">
                <input type="text" name="q" placeholder="Search knowledge..." value="{{ knowledge_query }}">
                <select name="domain" style="padding: 10px; background: var(--surface); border: 1px solid var(--border); color: var(--text); border-radius: 6px;">
                    <option value="">All Domains</option>
                    {% for d in domains %}
                    <option value="{{ d }}" {% if selected_domain == d %}selected{% endif %}>{{ d }}</option>
                    {% endfor %}
                </select>
                <button type="submit">Search</button>
            </form>
            {% for k in knowledge_results %}
            <div class="memory-item">
                <div class="meta">
                    #{{ k.id }} · <span class="tag">{{ k.domain }}</span>
                    · confidence: {{ k.confidence }}
                    {% if k.source %}· {{ k.source }}{% endif %}
                </div>
                <div class="content">{{ k.content }}</div>
            </div>
            {% endfor %}
        </div>

        {% elif tab == 'factstore' %}
        <!-- ─── Fact Store ────────────────────────────────────────── -->
        <div class="card full-width">
            <h2>Fact Store (Connection Graph Bridge)</h2>
            <form class="search-bar" method="get">
                <input type="hidden" name="tab" value="factstore">
                <input type="text" name="q" placeholder="Search facts..." value="{{ fact_query }}">
                <button type="submit">Search</button>
            </form>
            <table>
                <tr><th>ID</th><th>Content</th><th>Category</th><th>Trust</th><th>Tags</th></tr>
                {% for f in fact_results %}
                <tr>
                    <td>{{ f.fact_id }}</td>
                    <td style="max-width: 500px; overflow: hidden; text-overflow: ellipsis;">{{ f.content[:120] }}{% if f.content|length > 120 %}...{% endif %}</td>
                    <td><span class="tag">{{ f.category }}</span></td>
                    <td>{{ f.trust_score }}</td>
                    <td>{% for t in f.tags_list %}<span class="tag">{{ t }}</span>{% endfor %}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        {% endif %}

        <footer>
            ᛗ Mímir's Eye v1.0 · The Well of Wisdom · {{ timestamp }} · DB: {{ db_size }}MB
        </footer>
    </div>
</body>
</html>
"""


# ─── Routes ─────────────────────────────────────────────────────────────
@app.route("/")
def dashboard():
    tab = request.args.get("tab", "overview")
    db_path = app.config["DB_PATH"]
    fact_db = app.config["FACT_DB_PATH"]

    # ─── Overview ─────────────────────────────────────────────────
    try:
        conn = get_db()
        total_memories = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
        total_knowledge = conn.execute("SELECT COUNT(*) FROM knowledge").fetchone()[0]
        total_relationships = conn.execute("SELECT COUNT(*) FROM relationships").fetchone()[0]
        total_entities = conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
        total_saga = conn.execute("SELECT COUNT(*) FROM saga_events").fetchone()[0]
        total_conversations = conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]

        categories = conn.execute(
            "SELECT category, COUNT(*) as cnt FROM memories GROUP BY category ORDER BY cnt DESC LIMIT 15"
        ).fetchall()
        cat_max = max(c[1] for c in categories) if categories else 1

        importance_dist = conn.execute(
            "SELECT importance, COUNT(*) as cnt FROM memories GROUP BY importance ORDER BY importance DESC"
        ).fetchall()
        imp_max = max(i[1] for i in importance_dist) if importance_dist else 1

        relationship_types = conn.execute(
            "SELECT relationship_type, COUNT(*) as cnt FROM relationships GROUP BY relationship_type ORDER BY cnt DESC LIMIT 15"
        ).fetchall()
        rel_max = max(r[1] for r in relationship_types) if relationship_types else 1

        top_entities = conn.execute("""
            SELECT e.name, COUNT(*) as cnt
            FROM relationships r
            JOIN entities e ON (r.entity_a = e.entity_id OR r.entity_b = e.entity_id)
            GROUP BY e.name
            ORDER BY cnt DESC LIMIT 15
        """).fetchall()

        recent_important = conn.execute(
            "SELECT id, category, content, importance, timestamp FROM memories WHERE importance >= 8 ORDER BY timestamp DESC LIMIT 10"
        ).fetchall()

        conn.close()
    except Exception as e:
        total_memories = total_knowledge = total_relationships = 0
        total_entities = total_saga = total_conversations = 0
        categories = importance_dist = relationship_types = top_entities = recent_important = []
        cat_max = imp_max = rel_max = 1

    # Fact Store stats
    try:
        fs_conn = get_db("FACT_DB_PATH")
        total_facts = fs_conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
        total_fs_entities = fs_conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
        total_links = fs_conn.execute("SELECT COUNT(*) FROM fact_entities").fetchone()[0]
        fs_conn.close()
    except Exception:
        total_facts = total_fs_entities = total_links = 0

    db_size = round(os.path.getsize(db_path) / (1024 * 1024), 1) if os.path.exists(db_path) else 0

    stats = {
        "total_memories": total_memories,
        "total_knowledge": total_knowledge,
        "total_relationships": total_relationships,
        "total_entities": total_entities,
        "total_saga": total_saga,
        "total_conversations": total_conversations,
        "categories": categories,
        "cat_max": cat_max,
        "importance_dist": importance_dist,
        "imp_max": imp_max,
        "relationship_types": relationship_types,
        "rel_max": rel_max,
        "top_entities": top_entities,
        "recent_important": recent_important,
    }
    fact_stats = {
        "total_facts": total_facts,
        "total_entities": total_fs_entities,
        "total_links": total_links,
    }

    return render_template_string(
        DASHBOARD_HTML,
        tab=tab,
        stats=stats,
        fact_stats=fact_stats,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        db_size=db_size,
        # Placeholder for other tabs
        query="", categories=[], selected_cat="", min_imp="0",
        results=[], rel_entity="", rel_types=[], selected_rel_type="",
        rel_results=[], knowledge_query="", domains=[], selected_domain="",
        knowledge_results=[], fact_query="", fact_results=[],
    )


@app.route("/?tab=memories")
def memories_tab():
    tab = "memories"
    query = request.args.get("q", "")
    selected_cat = request.args.get("category", "")
    min_imp = request.args.get("min_importance", "0")

    conn = get_db()
    categories = [r[0] for r in conn.execute("SELECT DISTINCT category FROM memories ORDER BY category").fetchall()]

    sql = "SELECT id, category, content, importance, timestamp, tags FROM memories WHERE 1=1"
    params = []
    if query:
        sql += " AND (content LIKE ? OR category LIKE ? OR tags LIKE ?)"
        params.extend([f"%{query}%", f"%{query}%", f"%{query}%"])
    if selected_cat:
        sql += " AND category = ?"
        params.append(selected_cat)
    if min_imp and min_imp != "0":
        sql += " AND importance >= ?"
        params.append(int(min_imp))
    sql += " ORDER BY importance DESC, timestamp DESC LIMIT 100"

    rows = conn.execute(sql, params).fetchall()
    results = []
    for r in rows:
        r_dict = dict(r)
        try:
            r_dict["tags_list"] = json.loads(r_dict.get("tags", "[]")) if r_dict.get("tags") else []
        except (json.JSONDecodeError, TypeError):
            r_dict["tags_list"] = []
        results.append(type("Memory", (), r_dict))

    conn.close()

    # Base stats for template
    base = _get_base_stats()

    return render_template_string(
        DASHBOARD_HTML,
        tab=tab, query=query, categories=categories, selected_cat=selected_cat,
        min_imp=min_imp, results=[type("Memory", (), dict(r)) for r in rows],
        stats=base["stats"], fact_stats=base["fact_stats"],
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        db_size=base["db_size"],
        rel_entity="", rel_types=[], selected_rel_type="",
        rel_results=[], knowledge_query="", domains=[], selected_domain="",
        knowledge_results=[], fact_query="", fact_results=[],
    )


@app.route("/?tab=relationships")
def relationships_tab():
    tab = "relationships"
    rel_entity = request.args.get("entity", "")
    selected_rel_type = request.args.get("rel_type", "")

    conn = get_db()
    rel_types = [r[0] for r in conn.execute("SELECT DISTINCT relationship_type FROM relationships ORDER BY relationship_type").fetchall()]

    sql = "SELECT entity_a, entity_b, relationship_type as rtype, strength FROM relationships WHERE 1=1"
    params = []
    if rel_entity:
        sql += " AND (entity_a LIKE ? OR entity_b LIKE ?)"
        params.extend([f"%{rel_entity}%", f"%{rel_entity}%"])
    if selected_rel_type:
        sql += " AND relationship_type = ?"
        params.append(selected_rel_type)
    sql += " ORDER BY strength DESC LIMIT 200"

    rel_results = conn.execute(sql, params).fetchall()
    conn.close()

    base = _get_base_stats()

    return render_template_string(
        DASHBOARD_HTML,
        tab=tab, rel_entity=rel_entity, rel_types=rel_types,
        selected_rel_type=selected_rel_type,
        rel_results=rel_results,
        stats=base["stats"], fact_stats=base["fact_stats"],
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        db_size=base["db_size"],
        query="", categories=[], selected_cat="", min_imp="0",
        results=[], knowledge_query="", domains=[], selected_domain="",
        knowledge_results=[], fact_query="", fact_results=[],
    )


@app.route("/?tab=knowledge")
def knowledge_tab():
    tab = "knowledge"
    knowledge_query = request.args.get("q", "")
    selected_domain = request.args.get("domain", "")

    conn = get_db()
    domains = [r[0] for r in conn.execute("SELECT DISTINCT domain FROM knowledge ORDER BY domain").fetchall()]

    sql = "SELECT id, domain, content, confidence, source FROM knowledge WHERE 1=1"
    params = []
    if knowledge_query:
        sql += " AND (content LIKE ? OR domain LIKE ?)"
        params.extend([f"%{knowledge_query}%", f"%{knowledge_query}%"])
    if selected_domain:
        sql += " AND domain = ?"
        params.append(selected_domain)
    sql += " ORDER BY confidence DESC LIMIT 100"

    knowledge_results = conn.execute(sql, params).fetchall()
    conn.close()

    base = _get_base_stats()

    return render_template_string(
        DASHBOARD_HTML,
        tab=tab, knowledge_query=knowledge_query, domains=domains,
        selected_domain=selected_domain, knowledge_results=knowledge_results,
        stats=base["stats"], fact_stats=base["fact_stats"],
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        db_size=base["db_size"],
        query="", categories=[], selected_cat="", min_imp="0",
        results=[], rel_entity="", rel_types=[], selected_rel_type="",
        rel_results=[], fact_query="", fact_results=[],
    )


@app.route("/?tab=factstore")
def factstore_tab():
    tab = "factstore"
    fact_query = request.args.get("q", "")

    fs_conn = get_db("FACT_DB_PATH")
    if fact_query:
        fact_results = fs_conn.execute(
            "SELECT fact_id, content, category, trust_score, tags FROM facts WHERE content LIKE ? ORDER BY trust_score DESC LIMIT 100",
            (f"%{fact_query}%",),
        ).fetchall()
    else:
        fact_results = fs_conn.execute(
            "SELECT fact_id, content, category, trust_score, tags FROM facts ORDER BY trust_score DESC LIMIT 100"
        ).fetchall()

    # Add tags_list to results
    processed = []
    for f in fact_results:
        f_dict = dict(f)
        try:
            f_dict["tags_list"] = f_dict.get("tags", "").split(",") if f_dict.get("tags") else []
        except Exception:
            f_dict["tags_list"] = []
        processed.append(type("Fact", (), f_dict))
    fs_conn.close()

    base = _get_base_stats()

    return render_template_string(
        DASHBOARD_HTML,
        tab=tab, fact_query=fact_query, fact_results=processed,
        stats=base["stats"], fact_stats=base["fact_stats"],
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        db_size=base["db_size"],
        query="", categories=[], selected_cat="", min_imp="0",
        results=[], rel_entity="", rel_types=[], selected_rel_type="",
        rel_results=[], knowledge_query="", domains=[], selected_domain="",
        knowledge_results=[],
    )


# ─── API routes ─────────────────────────────────────────────────────────
@app.route("/api/stats")
def api_stats():
    """JSON API for stats."""
    try:
        conn = get_db()
        stats = {
            "memories": conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0],
            "knowledge": conn.execute("SELECT COUNT(*) FROM knowledge").fetchone()[0],
            "relationships": conn.execute("SELECT COUNT(*) FROM relationships").fetchone()[0],
            "entities": conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0],
            "saga_events": conn.execute("SELECT COUNT(*) FROM saga_events").fetchone()[0],
        }
        conn.close()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/search")
def api_search():
    """JSON API for memory search."""
    q = request.args.get("q", "")
    limit = min(int(request.args.get("limit", 50)), 200)
    if not q:
        return jsonify({"error": "Missing query parameter 'q'"}), 400

    try:
        conn = get_db()
        # FTS5 with content=external table — must join back to memories
        results = conn.execute(
            """SELECT m.id, m.category, m.content, m.importance, m.timestamp
               FROM memories m
               JOIN memories_fts fts ON m.id = fts.rowid
               WHERE memories_fts MATCH ?
               ORDER BY m.importance DESC
               LIMIT ?""",
            (q, limit),
        ).fetchall()
        conn.close()
        return jsonify([dict(r) for r in results])
    except Exception as e:
        # Fallback to LIKE search if FTS fails
        try:
            conn = get_db()
            results = conn.execute(
                "SELECT id, category, content, importance, timestamp FROM memories WHERE content LIKE ? ORDER BY importance DESC LIMIT ?",
                (f"%{q}%", limit),
            ).fetchall()
            conn.close()
            return jsonify([dict(r) for r in results])
        except Exception as e2:
            return jsonify({"error": str(e2)}), 500


@app.route("/health")
def health():
    """Health check endpoint."""
    try:
        conn = get_db()
        count = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
        conn.close()
        return jsonify({"status": "ok", "memories": count})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 5003


# ─── Helpers ────────────────────────────────────────────────────────────
def _get_base_stats():
    """Get base stats needed by all tabs."""
    db_path = app.config["DB_PATH"]
    fact_db = app.config["FACT_DB_PATH"]

    try:
        conn = get_db()
        total_memories = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
        total_knowledge = conn.execute("SELECT COUNT(*) FROM knowledge").fetchone()[0]
        total_relationships = conn.execute("SELECT COUNT(*) FROM relationships").fetchone()[0]
        total_entities_count = conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
        total_saga = conn.execute("SELECT COUNT(*) FROM saga_events").fetchone()[0]
        total_conversations = conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]

        categories = conn.execute(
            "SELECT category, COUNT(*) as cnt FROM memories GROUP BY category ORDER BY cnt DESC LIMIT 15"
        ).fetchall()
        cat_max = max(c[1] for c in categories) if categories else 1

        importance_dist = conn.execute(
            "SELECT importance, COUNT(*) as cnt FROM memories GROUP BY importance ORDER BY importance DESC"
        ).fetchall()
        imp_max = max(i[1] for i in importance_dist) if importance_dist else 1

        relationship_types = conn.execute(
            "SELECT relationship_type, COUNT(*) as cnt FROM relationships GROUP BY relationship_type ORDER BY cnt DESC LIMIT 15"
        ).fetchall()
        rel_max = max(r[1] for r in relationship_types) if relationship_types else 1

        recent_important = conn.execute(
            "SELECT id, category, content, importance, timestamp FROM memories WHERE importance >= 8 ORDER BY timestamp DESC LIMIT 10"
        ).fetchall()
        conn.close()
    except Exception:
        total_memories = total_knowledge = total_relationships = 0
        total_entities_count = total_saga = total_conversations = 0
        categories = importance_dist = relationship_types = recent_important = []
        cat_max = imp_max = rel_max = 1

    try:
        fs_conn = get_db("FACT_DB_PATH")
        total_facts = fs_conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
        total_fs_entities = fs_conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
        total_links = fs_conn.execute("SELECT COUNT(*) FROM fact_entities").fetchone()[0]
        fs_conn.close()
    except Exception:
        total_facts = total_fs_entities = total_links = 0

    stats = {
        "total_memories": total_memories,
        "total_knowledge": total_knowledge,
        "total_relationships": total_relationships,
        "total_entities": total_entities_count,
        "total_saga": total_saga,
        "total_conversations": total_conversations,
        "categories": categories,
        "cat_max": cat_max,
        "importance_dist": importance_dist,
        "imp_max": imp_max,
        "relationship_types": relationship_types,
        "rel_max": rel_max,
        "top_entities": [],
        "recent_important": recent_important,
    }
    fact_stats = {
        "total_facts": total_facts,
        "total_entities": total_fs_entities,
        "total_links": total_links,
    }
    db_size = round(os.path.getsize(db_path) / (1024 * 1024), 1) if os.path.exists(db_path) else 0

    return {"stats": stats, "fact_stats": fact_stats, "db_size": db_size}


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Mímir's Eye — Memory Dashboard")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port to listen on")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--db", default=DEFAULT_DB_PATH, help="Path to Mímir DB")
    parser.add_argument("--fact-db", default=DEFAULT_FACT_DB, help="Path to Fact Store DB")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    app.config["DB_PATH"] = args.db
    app.config["FACT_DB_PATH"] = args.fact_db

    print(f"ᛗ Mímir's Eye starting on {args.host}:{args.port}")
    print(f"  Mímir DB: {args.db}")
    print(f"  Fact Store: {args.fact_db}")
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()