# IT203: Database Administration & Data Management
## Bachelor of Science in Information Technology — University of Yggdrasil, 2040

**Credits:** 4  
**Prerequisites:** IT101 (Introduction to Information Technology), IT105 (Programming for IT)  
**Description:** Data is the most valuable asset of any 2040 organisation, and the database administrator (DBA) is its steward. This course covers the full lifecycle of data management: relational database design and normalisation, SQL mastery for querying and administration, the operational disciplines of backup, recovery, replication, and high availability, and the NoSQL paradigms that have reshaped the data landscape. Students administer real PostgreSQL and MongoDB clusters in the YggLab Data Forge, confront simulated disasters (corrupted tables, failed replicas, ransomware-encrypted backups), and emerge with the diagnostic instinct that separates the professional DBA from the query writer.

**Instructor:** Dr. Sigrún Vérendóttir, Department of Information Technology  
**Lab:** YggLab Data Forge, Muninn Computing Centre, First Floor  
**Office Hours:** Mondays and Wednesdays, 10:00–12:00 UTC

---

## Lectures

---

### Lecture 1: The Database Administrator — Steward of the Organisation's Memory

**Course:** IT203 — Database Administration & Data Management  
**Degree:** Bachelor of Science in Information Technology, University of Yggdrasil, 2040

---

#### Overview

Every organisation runs on data: customer records, financial transactions, inventory, user-generated content, sensor readings, machine learning features. The database administrator is the professional responsible for ensuring that data is stored reliably, retrieved efficiently, protected from loss and unauthorised access, and governed according to regulatory requirements. This opening lecture establishes the DBA's professional identity, traces the evolution of data management from hierarchical databases of the 1960s to the AI-augmented, multi-model databases of 2040, and introduces the operational mindset — paranoia about data loss, obsession with query performance, and reverence for ACID — that distinguishes the DBA from the developer who merely writes queries.

#### Key Topics

- **What Is a DBA?** The DBA's responsibilities: installation and configuration, schema design and normalisation, query optimisation and indexing, backup and recovery planning, replication and high availability, security (access control, encryption, auditing), capacity planning, performance monitoring and tuning, and migration. The distinction between a development DBA (works with application teams on schema design and query tuning) and an operations DBA (manages production infrastructure — replication, backups, monitoring, incident response). In 2040, the line has blurred: SRE-style database engineering combines both roles.
- **The Evolution of Data Management:** Hierarchical databases (IMS, 1960s), network databases (CODASYL, 1970s), relational databases (E.F. Codd's 1970 paper — data as tables with SQL — the insight that data independence matters), object-oriented databases (1990s), NoSQL (2000s–2010s — key-value, document, column-family, graph), NewSQL (2010s–2020s — relational with horizontal scaling — CockroachDB, Spanner, TiDB), and the 2040 multi-model landscape (SurrealDB, EdgeDB, PostgreSQL with extensions combining relational, document, graph, and vector search).
- **The ACID Contract:** Atomicity: a transaction is all-or-nothing. Consistency: a transaction moves the database from one valid state to another. Isolation: concurrent transactions do not interfere — the isolation levels (Read Uncommitted, Read Committed, Repeatable Read, Serializable) trade correctness for performance. Durability: committed transactions survive crashes — the write-ahead log (WAL) is the mechanism. The lecture walks through a two-account bank transfer, showing how the WAL records every change before it reaches data files and how crash recovery replays the WAL.
- **The CAP Theorem:** Eric Brewer's theorem: a distributed database can provide at most two of Consistency, Availability, and Partition Tolerance. CP systems (etcd, HBase) refuse writes during partitions. AP systems (Cassandra, DynamoDB) accept writes that may conflict. The PACELC extension: when there is no partition, optimise for latency or consistency. The 2040 reality: cloud databases finesse CAP with TrueTime (Spanner) and hybrid logical clocks (CockroachDB) providing external consistency.
- **The 2040 Data Landscape:** AI-managed databases (self-tuning, self-patching), vector databases (pgvector, Pinecone — storing embeddings for semantic search and RAG), real-time analytics (ClickHouse, Materialize — sub-second queries over streaming data), and data mesh architectures (decentralised data ownership with federated governance).

#### Lecture Notes

The DBA's relationship with data is fiduciary. A developer can deploy buggy code and roll it back; a DBA who drops the wrong table without a verified backup has committed an irreversible act. This asymmetry explains the DBA culture of caution, verification, and "measure twice, cut once."

The DBA's toolkit: `psql` (PostgreSQL's interactive terminal), `pg_stat_statements` (query performance analysis), `pgBadger` (log analysis), `pg_dump` / `pg_restore` (backup and restore), `pg_basebackup` (physical backup), and the monitoring ecosystem (Prometheus with PostgreSQL exporter, Grafana dashboards).

The Norse metaphor: the database is the community's memory-hoard — the oral traditions, legal precedents, and genealogies stored by the lawspeaker at the Althing. The DBA is the lawspeaker's successor, preserving the hoard against fire (disk failure), theft (security breach), and forgetting (data corruption). To lose the hoard is to lose the community's identity.

#### Required Reading

- Codd, E.F. (1970). "A Relational Model of Data for Large Shared Data Banks." *Communications of the ACM*, 13(6), 377–387.
- Kleppmann, M. (2034). *Designing Data-Intensive Applications*, 4th Edition. O'Reilly Media. Chapters 1, 5, 7.
- Brewer, E.A. (2012). "CAP Twelve Years Later: How the 'Rules' Have Changed." *IEEE Computer*, 45(2), 23–29.
- PostgreSQL Documentation (2040). "Chapter 29: Reliability and the Write-Ahead Log."

#### Discussion Questions

1. Codd's relational model separated logical data structure from physical storage — a radical idea in 1970. Why did this separation take 15 years to achieve commercial dominance? What analogous separation is occurring in 2040?
2. Google Spanner provides external consistency with five-nines availability. Is Spanner violating CAP, or is the theorem's definition of "partition" too narrow?
3. A DBA runs `DROP TABLE orders;` in production. The backup is 23 hours old. The orders table received 47,000 inserts in those 23 hours. Describe the recovery process. What operational practices would have prevented this mistake?

---

### Lecture 2: Relational Database Design and Normalisation

**Course:** IT203 — Database Administration & Data Management  
**Degree:** Bachelor of Science in Information Technology, University of Yggdrasil, 2040

---

#### Overview

A database designed without normalisation is a database designed for corruption. This lecture teaches the DBA's foundational skill: translating real-world business requirements into a set of related tables that are free of redundancy, resistant to update anomalies, and efficient to query. Students learn the normal forms (1NF through BCNF, with acknowledgment of 4NF and 5NF), practice normalising a denormalised dataset, and confront the operational reality that production databases are almost never fully normalised — the art is knowing which denormalisations are worth their cost.

#### Key Topics

- **The Problem Normalisation Solves:** Update anomalies (a customer changes address but not every row is updated), insert anomalies (cannot store a customer without an order), delete anomalies (deleting the last order for a product loses the product's price). Normalisation eliminates these by separating facts into appropriate tables.
- **The Normal Forms:** 1NF: eliminate repeating groups — every column contains atomic values. 2NF: eliminate partial dependencies — every non-key column depends on the entire primary key. 3NF: eliminate transitive dependencies — non-key columns depend only on the key. BCNF: every determinant must be a candidate key. The lecture walks through normalising a university course registration dataset from a single unnormalised table to BCNF tables (Students, Courses, Instructors, Enrollments, Prerequisites).
- **Denormalisation — When and Why:** Normalisation reduces redundancy but increases JOINs. A query retrieving student name, course title, and instructor name might join four tables. Denormalisation reintroduces controlled redundancy to reduce JOINs: caching instructor name in Courses, storing aggregate totals in Customers, maintaining materialised views. The operational pattern: document every denormalisation in a "denormalisation register" — what was denormalised, why, what consistency guarantees are provided, and how to recover if they're violated.
- **Schema Design in 2040:** Entity-relationship diagrams (ERDs) remain the lingua franca. Tools: dbdiagram.io, pgModeler, and AI-assisted schema design (describe your domain in natural language; AI proposes a normalised schema — useful for initial drafts, always reviewed by a human DBA). Practical exercise: design a hospital data management schema (patients, doctors, appointments, prescriptions, billing, insurance) with ERD, CREATE TABLE statements, and denormalisation register.

#### Lecture Notes

Normalisation is a tool, not a religion. The most important schema design decisions are made in the first week of a project, by people who understand the business domain least at that point. The DBA's role is to anticipate change: use enumerated types sparingly, prefer separate tables over nullable columns, design for eventual partition-by-time.

The 2040 perspective: schema-on-write (relational — structure enforced at insert time) vs. schema-on-read (document stores — structure interpreted at query time). Schema-on-write is the better default for data that will outlive the application that created it. The JSON column in PostgreSQL (`jsonb`) represents a pragmatic middle ground.

#### Required Reading

- Date, C.J. (2036). *An Introduction to Database Systems*, 10th Edition. Addison-Wesley.
- Celko, J. (2037). *Joe Celko's SQL for Smarties*, 7th Edition. Morgan Kaufmann.
- PostgreSQL Documentation (2040). "Chapter 5: Data Definition" and "Section 8.14: JSON Types."
- Kimball, R. & Ross, M. (2038). *The Data Warehouse Toolkit*, 5th Edition. Wiley.

#### Discussion Questions

1. A fully normalised schema may require 10-table joins for a report. You denormalise by adding `last_order_date` to `customers`, updated by a trigger. A batch job bypasses the trigger. Diagnose the corruption sequence and prevent it.
2. Schema-on-write vs. schema-on-read: a startup's data model changes weekly. At what point should the startup migrate to a relational schema? Define criteria.
3. Design the schema for a 2040 content moderation system: posts, users, reports, moderator actions, appeals. Ensure full audit trail. Identify normalisation decisions and intentional denormalisations.

---

### Lecture 3: SQL Mastery — Querying, Aggregation, and Window Functions

**Course:** IT203 — Database Administration & Data Management  
**Degree:** Bachelor of Science in Information Technology, University of Yggdrasil, 2040

---

#### Overview

SQL is the universal language of data, having outlasted every competitor and survived the NoSQL revolution. This lecture covers SQL at the professional DBA level: beyond `SELECT * FROM`, into CTEs, window functions, lateral joins, recursive queries, and set operations that separate the query writer from the query master. Students solve progressively complex problems against a realistic e-commerce dataset.

#### Key Topics

- **SELECT Execution Order:** FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT. Understanding this order (different from the written order) is essential for reasoning about query behaviour. JOIN types: INNER, LEFT, RIGHT (rarely used), FULL OUTER, CROSS, and LATERAL (correlated subquery in FROM — one of PostgreSQL's most powerful features).
- **Common Table Expressions (CTEs):** `WITH ... AS (...)` for readability, recursion (organisational charts, category hierarchies, bill-of-materials), and (when declared `MATERIALIZED`) optimisation fences. Recursive CTE: an `employees` table with `manager_id` — write a query returning each employee's full reporting chain to the CEO.
- **Window Functions:** The most powerful and least widely understood SQL feature. `ROW_NUMBER()`, `RANK()`, `DENSE_RANK()`, `LAG()`/`LEAD()`, `SUM()`/`AVG()` as window aggregates. `PARTITION BY` divides rows into groups; `ORDER BY` determines sort order; the frame clause restricts the window. Examples: rank customers by lifetime value within each country, compare each day's revenue to the previous day, calculate a 7-day moving average.
- **Set Operations and Advanced Patterns:** UNION, INTERSECT, EXCEPT. The `FILTER` clause (PostgreSQL extension): `COUNT(*) FILTER (WHERE status = 'active')`. `DISTINCT ON` for first row per distinct value.

#### Lecture Notes

The most common SQL mistake is not a syntax error but a logic error: queries producing correct-looking results that are subtly wrong — a JOIN that multiplies rows, a WHERE clause filtering out NULLs silently, a GROUP BY aggregating at the wrong granularity. The DBA's skill: mentally verify the row count at each stage.

Practical exercise: given an e-commerce database (customers, orders, order_items, products, categories, reviews), answer complex business questions requiring combinations of multiple techniques.

The 2040 reality: AI code assistants generate SQL from natural language. The DBA must read and validate generated SQL, catching subtle errors that AI produces when business logic is complex.

#### Required Reading

- Beaulieu, A. (2038). *Learning SQL*, 5th Edition. O'Reilly Media. Chapters 5, 8, 14.
- PostgreSQL Documentation (2040). "Chapter 3: Advanced Features" and "Chapter 9: Functions and Operators."
- Winand, M. (2036). *SQL Performance Explained*, 4th Edition. Use The Index, Luke!

#### Discussion Questions

1. `ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC)` — why must `WHERE rn = 1` be in an outer query rather than the same WHERE clause?
2. Recursive CTE for organisational hierarchy: how to detect and handle cycles (A reports to B, B reports to A)?
3. A query with `WHERE order_date > '2040-01-01' GROUP BY customer_id HAVING COUNT(*) > 10` excludes customers with zero orders. Rewrite to include all customers with zero counts. Why is a LEFT JOIN necessary?

---

### Lecture 4: Indexing and Query Performance

**Course:** IT203 — Database Administration & Data Management  
**Degree:** Bachelor of Science in Information Technology, University of Yggdrasil, 2040

---

#### Overview

A query scanning a million-row table takes seconds; the same query with a well-chosen index takes milliseconds. Indexing is the single most impactful skill for database performance. This lecture covers: the data structures powering indexes (B-trees, hash, GiST, GIN, BRIN, HNSW), the art of reading query plans (`EXPLAIN ANALYZE`), strategies for choosing indexes (covering, partial, composite column ordering), and the operational cost of indexing (write overhead, storage, maintenance).

#### Key Topics

- **How Indexes Work:** B-tree balanced tree structure — O(log n) lookups vs. O(n) sequential scans. Page splits, index bloat (dead tuples from UPDATE/DELETE — remedied by `REINDEX` or `VACUUM`). PostgreSQL index types: B-tree (default, equality and range), Hash (equality only), GiST (geometric, full-text), GIN (array containment, JSON key existence, trigram text), BRIN (very large tables with natural sort order), HNSW (vector similarity via pgvector).
- **Reading EXPLAIN ANALYZE:** Query plans: sequential scan (fast for small tables or >5–10% of rows), index scan (index then heap fetch), index-only scan (all columns in index), bitmap index scan (multiple indexes combined), nested loop join, hash join, merge join. Practical exercise: five slow queries with EXPLAIN output — identify bottlenecks (missing index, stale statistics, poor join strategy).
- **Indexing Strategies:** Covering indexes: `CREATE INDEX ON orders (customer_id) INCLUDE (order_date, total)` — index-only scans possible. Partial indexes: index a subset of rows — smaller, faster. Composite index column ordering: index on `(a, b)` supports queries on `(a)` and `(a, b)` but NOT `(b)` alone. Expression indexes: `CREATE INDEX ON users (lower(email))`.
- **Operational Cost:** Every index must be updated on INSERT, UPDATE, DELETE. A table with 10 indexes pays 10× write cost. Monitor: `pg_stat_user_indexes` — identify unused indexes (candidates for removal). Duplicate indexes: `(a, b)` makes `(a)` redundant for most queries.

#### Lecture Notes

The most valuable 30 minutes a DBA can spend: reviewing `pg_stat_statements`, identifying top 10 queries by total execution time. Optimising the slowest query often delivers more improvement than all other tuning combined. Diagnostic framework: (1) Is the query slow because it does too much work, or because the database does unnecessary work? (2) Can the query be rewritten? (3) What index eliminates the sequential scan? (4) Does this index benefit other queries? (5) After creating the index, did the query plan change as expected?

The Norse metaphor: indexes are the runic catalogue on a scroll-hoard — find the scroll by its first word rather than reading every scroll in the longhouse.

#### Required Reading

- Winand, M. (2036). *SQL Performance Explained*, 4th Edition. Full text.
- PostgreSQL Documentation (2040). "Chapter 11: Indexes" and "Chapter 14: Performance Tips."
- pgMustard (2040). "How to Read EXPLAIN ANALYZE." Online guide.

#### Discussion Questions

1. An index on `(country, city, postal_code)` supports queries on `country`, `country AND city`, and all three — but NOT `city` alone. Why? Explain the B-tree structure.
2. You inherit a database with 47 indexes, 12 with `idx_scan = 0` over 90 days. Should you drop all 12? What are the risks?
3. A query with `ORDER BY created_at DESC LIMIT 10` still scans 500 million rows despite a B-tree index on `created_at`. Diagnose. Hint: consider data types, NULL ordering, and WHERE conditions.

---

### Lecture 5: PostgreSQL Administration — The Operational DBA

**Course:** IT203 — Database Administration & Data Management  
**Degree:** Bachelor of Science in Information Technology, University of Yggdrasil, 2040

---

#### Overview

PostgreSQL is the University of Yggdrasil's recommended relational database and the most popular open-source RDBMS in 2040. This lecture covers PostgreSQL from the operational DBA's perspective: architecture, configuration of `postgresql.conf`, user and role management, and the maintenance tasks — `VACUUM`, `ANALYZE`, `REINDEX` — that keep a PostgreSQL cluster healthy.

#### Key Topics

- **PostgreSQL Architecture:** A cluster of databases served by a single postmaster process. Each client connection spawns a backend process. Shared memory: `shared_buffers` (page cache — 25% of RAM), `wal_buffers`. Background processes: WAL writer, background writer, autovacuum launcher and workers, statistics collector, archiver. Monitoring: `pg_stat_activity`, `pg_stat_bgwriter`.
- **Configuration Tuning:** Memory: `shared_buffers` (25% of RAM), `effective_cache_size` (50–75% of RAM — planner hint), `work_mem` (per-operation sort/hash memory), `maintenance_work_mem`. WAL: `wal_level`, `max_wal_size`, `checkpoint_timeout`. Connections: `max_connections` (use PgBouncer to pool). Tuning methodology: measure → hypothesise → change one setting → measure → accept or roll back.
- **User and Role Management:** Roles as login roles or group roles. Privileges: CONNECT, USAGE, SELECT/INSERT/UPDATE/DELETE, EXECUTE, USAGE on sequences. Row-level security (RLS): policies restricting which rows a role can see. Practical exercise: create a multi-tenant database with three departments, each with its own schema and role, using RLS to isolate data.
- **Maintenance Operations:** `VACUUM`: garbage collector for dead tuples from UPDATE/DELETE. Autovacuum runs automatically; large tables may need manual `VACUUM FULL` or `pg_repack`. `ANALYZE`: updates table statistics — stale statistics cause poor query plans. `REINDEX`: rebuilds bloated indexes. The transaction ID wraparound problem: PostgreSQL's 32-bit XID counter wraps around; VACUUM must "freeze" old rows to prevent data loss — neglecting autovacuum triggers emergency shutdown.

#### Lecture Notes

The DBA who masters PostgreSQL configuration, user management, and maintenance is employable anywhere. Automate everything: autovacuum tuned (not disabled), backups cron-scheduled, monitoring alerting before users notice problems. A DBA who manually runs automatable commands will be woken at 03:00 by a preventable outage.

The 2040 perspective: managed PostgreSQL services (RDS, Cloud SQL, Supabase) absorb traditional DBA tasks — automated backups, patching, failover, scaling. The DBA who only knows the managed console is a consumer; the DBA who understands what the service does underneath can diagnose problems the console cannot explain.

#### Required Reading

- PostgreSQL Documentation (2040). "Chapter 18: Server Setup," "Chapter 19: Server Configuration," "Chapter 21: Database Roles," "Chapter 24: Routine Database Maintenance."
- Riggs, S. et al. (2039). *PostgreSQL 18 Administration Cookbook*. Packt Publishing.
- PgBouncer Documentation (2040). "Configuration and Usage."

#### Discussion Questions

1. `work_mem = 256MB` with `max_connections = 100` could consume 25.6GB for sorts in worst case. How do you set `work_mem` safely? What monitoring detects when a query spills to disk?
2. Compare RLS-based isolation to schema-per-tenant isolation for multi-tenant databases. Consider security, performance, and operational complexity.
3. Your monitoring alerts that the oldest unfrozen XID is approaching wraparound. Autovacuum cannot keep up on a 2TB table with 500M rows. Describe your emergency response and long-term changes.

---

### Lecture 6: Backup, Recovery, and Disaster Planning

**Course:** IT203 — Database Administration & Data Management  
**Degree:** Bachelor of Science in Information Technology, University of Yggdrasil, 2040

---

#### Overview

A database without a tested backup is a ticking bomb. This lecture covers: backup types (logical vs. physical, full vs. incremental), recovery point objective (RPO) and recovery time objective (RTO), and recovery procedures (point-in-time recovery) that must be practised, not just documented. Includes a live disaster recovery drill.

#### Key Topics

- **RPO and RTO:** RPO answers "how much data can the organisation lose?" For a trading system, zero (requires synchronous replication). For an internal wiki, 24 hours. RTO answers "how long can the database be unavailable?" For e-commerce, 5 minutes. For analytics, 4 hours. The DBA translates RPO/RTO into technical architecture and ensures it actually delivers.
- **Backup Types:** Logical: `pg_dump` (single database), `pg_dumpall` (entire cluster). Portable, selective restore possible, but no PITR support. Physical: `pg_basebackup` (binary copy for streaming replication and PITR). File-system snapshots (ZFS, EBS). The 2040 standard: continuous WAL archiving to object storage with weekly base backups, enabling PITR to any point within the retention window.
- **Point-in-Time Recovery (PITR):** Restore base backup → configure recovery settings (`restore_command`, `recovery_target_time`) → start PostgreSQL → WAL replays to target time. Practical exercise: an instructor corrupts a critical table at 14:23 UTC. Students must restore to 14:22 UTC using the 06:00 base backup and WAL archives, verify data, bring the database online — 30 minutes.
- **Testing Backups:** The most dangerous sentence: "the backups are running." Mandatory regimen: (1) automated daily validation — restore most recent backup, verify row counts; (2) quarterly full DR drill — simulate total data centre loss; (3) annual chaos drill — novel failure mode. The DBA who drills sleeps well.
- **The 2040 Disaster Landscape:** Ransomware is the most common data-loss scenario — attackers encrypt data files and delete backups. Defence: immutable backups (S3 Object Lock compliance mode, WORM storage), air-gapped backups (tape or isolated cloud account with separate credentials). Case study: a 2038 European hospital attack where attackers encrypted primary, replicas, and S3 backups (same IAM role) — total data loss, $40 million in damages.

#### Lecture Notes

Backup is the least glamorous and most important part of database administration. For every hour on performance tuning, spend at least 15 minutes on backup/recovery practice. Before any manual schema change in production, run `pg_dump -t table_name` — takes 10 seconds, has saved countless careers.

#### Required Reading

- PostgreSQL Documentation (2040). "Chapter 25: Backup and Restore" and "Chapter 26: High Availability."
- AWS Well-Architected Framework (2040). "Reliability Pillar — Backup and Disaster Recovery."
- NIST SP 800-209 (2037). "Security Guidelines for Storage Infrastructure."
- Yggdrasil DBA Runbook (2040). "Disaster Recovery Procedure."

#### Discussion Questions

1. RPO 5 minutes, RTO 15 minutes. Design the backup architecture. What is the minimum infrastructure?
2. A developer deletes a row that cascades to 125 child rows. Backup is 6 hours old with 3,000 new orders. Restore only the deleted data without losing new orders.
3. S3 WAL archives have Object Lock with 30-day compliance retention. GDPR requires deleting a specific record from archived WAL. Can you comply? What tension does this reveal?

---

### Lecture 7: Replication and High Availability

**Course:** IT203 — Database Administration & Data Management  
**Degree:** Bachelor of Science in Information Technology, University of Yggdrasil, 2040

---

#### Overview

A single database server is a single point of failure. Replication enables high availability, read scaling, and geographic distribution. This lecture covers PostgreSQL's replication architecture: streaming replication, synchronous vs. asynchronous commit, automatic failover with Patroni, and the operational patterns that make replication reliable in production.

#### Key Topics

- **Streaming Replication:** Primary streams WAL records to standby servers. Configuration: primary — `wal_level = replica`, `max_wal_senders`, `archive_mode = on`; standby — `primary_conninfo`, `restore_command`. Replication slots track standby progress — prevent primary from removing needed WAL but risk disk exhaustion if a standby disconnects.
- **Synchronous vs. Asynchronous:** Synchronous: `synchronous_commit = on` — transaction not acknowledged until standby writes WAL to disk. RPO = 0 but adds network latency. Asynchronous: primary acknowledges immediately; standby may lag; on primary failure, some committed transactions may be lost. 2040 standard: `synchronous_commit = remote_apply` for read-your-writes consistency.
- **Patroni and Automatic Failover:** Patroni uses a distributed configuration store (etcd, Consul) to elect a primary and perform automatic failover. Architecture: Patroni agent on each node → DCS → leader election → standby promoted → VIP/DNS updated → remaining standbys reconfigured. The split-brain prevention: DCS leader lock ensures only one primary. Test failover regularly.
- **Logical Replication:** Row-level replication for specific tables. Use cases: zero-downtime major version upgrades, selective replication, multi-master topologies. Covers conflict resolution and monitoring challenges.
- **Connection Pooling:** PgBouncer multiplexes client connections over fewer server connections. Pgpool-II adds read/write splitting and automatic failover detection. 2040 pattern: applications connect to PgBouncer, which routes based on declared intent.

#### Lecture Notes

Replication is a trade-off between durability, latency, and complexity. The DBA's skill: choosing the architecture matching business RPO/RTO requirements. Practical exercise: deploy a three-node Patroni cluster with synchronous replication, test failover, measure replication lag.

The Norse metaphor: a single server is a single longship. Replication is the fleet — if one ship founders, others continue the voyage. The DBA is the fleet commander.

#### Required Reading

- PostgreSQL Documentation (2040). "Chapter 26: High Availability" and "Chapter 30: Logical Replication."
- Patroni Documentation (2040). "Architecture," "Configuration," and "Failover."
- Kleppmann, M. (2034). *Designing Data-Intensive Applications*, 4th Edition. Chapters 5, 8.

#### Discussion Questions

1. Synchronous replication — minimum latency added to every commit with 2ms round-trip to standby?
2. Patroni cluster network partition: primary reaches DCS but not standbys; standbys reach each other but not DCS. Walk through expected behaviour and split-brain prevention.
3. Logical replication for zero-downtime upgrade from PostgreSQL 17 to 18 with 2TB data and 5,000 TPS. Describe: initial schema setup, initial data copy, ongoing replication, application cutover, rollback plan.

---

### Lecture 8: NoSQL and Multi-Model Databases

**Course:** IT203 — Database Administration & Data Management  
**Degree:** Bachelor of Science in Information Technology, University of Yggdrasil, 2040

---

#### Overview

The relational model is not the only data model. This lecture covers NoSQL families: document stores (MongoDB), key-value stores (Redis), wide-column stores (Cassandra/ScyllaDB), and graph databases (Neo4j). Includes the 2040 trend toward multi-model databases combining paradigms in a single system.

#### Key Topics

- **MongoDB — Document Model:** BSON documents in collections. Schema flexibility, embedded documents and arrays (avoiding JOINs), horizontal scaling via sharding. Operational concerns: eventual consistency by default, lack of true ACID across collections until 4.0, unbounded document growth risk. Aggregation pipeline, indexing (including vector search), monitoring.
- **Redis — Data Structure Server:** In-memory with persistence. Data structures: strings (caching, counters), lists (message queues), sets (social graph intersection), sorted sets (leaderboards), hashes (object storage), streams (Redis's Kafka), geospatial indexes. Operational concerns: memory as primary constraint, persistence options (RDB + AOF hybrid in 2040), replication with Sentinel for automatic failover.
- **Cassandra/ScyllaDB — Wide-Column:** Write-heavy, horizontally scalable, AP under CAP. Peer-to-peer architecture, consistent hashing, CQL (looks like SQL but query-first schema design). Compaction strategies, tombstones, capacity planning.
- **Neo4j — Graph Model:** Nodes and relationships with properties. Cypher query language: path traversals natural in Cypher require multiple JOINs in SQL. Graph algorithms (PageRank, community detection). 2040 landscape: recommendation engines, fraud detection, AI knowledge graphs.
- **Decision Framework:** Stable, known schema with complex relationships → PostgreSQL. Variable structure per entity → MongoDB. Sub-millisecond latency, simple access → Redis. Write-heavy, distributed, known queries → Cassandra. Relationships more important than entities → Neo4j. Multiple needs → Multi-model (SurrealDB, PostgreSQL with extensions).

#### Lecture Notes

The DBA who knows only relational databases is a carpenter who knows only hammers. Each data model solves specific problems elegantly and others poorly. The 2040 DBA recommends the right tool for each workload — even when that means managing multiple database systems.

#### Required Reading

- Bradshaw, S. et al. (2039). *MongoDB: The Definitive Guide*, 5th Edition. O'Reilly Media. Chapters 1–4, 11–12.
- Carlson, J.L. (2038). *Redis in Action*, 3rd Edition. Manning. Chapters 1–3, 6.
- Carpenter, J. & Hewitt, E. (2037). *Cassandra: The Definitive Guide*, 4th Edition. O'Reilly Media.
- Robinson, I. et al. (2038). *Graph Databases*, 4th Edition. O'Reilly Media.

#### Discussion Questions

1. Social media feed: PostgreSQL with JOINs vs. Redis sorted sets. Compare latency, consistency, storage cost, and failure modes.
2. MongoDB document 16MB limit vs. viral blog post with 500,000 comments. Describe schema evolution from embedded to referenced.
3. Cassandra requires query-first schema design. A startup's requirements change monthly. Is Cassandra wrong? What alternatives?

---

### Lecture 9: Database Security — Access Control, Encryption, and Auditing

**Course:** IT203 — Database Administration & Data Management  
**Degree:** Bachelor of Science in Information Technology, University of Yggdrasil, 2040

---

#### Overview

The database contains the organisation's crown jewels. Securing it is the DBA's core responsibility. This lecture covers the security triad: access control (least privilege), encryption (at rest, in transit, in use), and auditing (who did what and when). Includes hardening against the CIS PostgreSQL Benchmark.

#### Key Topics

- **Access Control — Least Privilege:** PostgreSQL's privilege system: roles, GRANT/REVOKE, hierarchy of database → schema → table → column → row (RLS). Revoke PUBLIC privileges (CONNECT on databases, USAGE on public schema). Group roles pattern: `readonly` group with SELECT; add users to groups. Application user pattern: minimum required privileges — not owner, not superuser.
- **Encryption:** At rest: file-system-level (LUKS), transparent data encryption (pg_tde), column-level (application encrypts — complicates indexing). In transit: TLS (forced via `pg_hba.conf` — `hostssl`), certificate validation (`sslmode=verify-full`), mutual TLS (mTLS — strong authentication without passwords). In use: confidential computing (AMD SEV, Intel SGX, AWS Nitro Enclaves) and homomorphic encryption (frontier technology).
- **Auditing:** `log_statement = 'ddl'` (minimum), `log_statement = 'mod'` (data modifications), `log_connections`/`log_disconnections`. `pgAudit` extension: detailed session and object audit logging. Tension between auditing and performance. Regulatory landscape: GDPR, SOX, HIPAA.
- **The 2040 Threat Model:** AI-generated attacks, supply chain attacks on extensions, credential leakage. Hardening checklist: revoke PUBLIC, enforce TLS, enable logging, install pgAudit, configure pg_hba.conf, enable passwordcheck, set statement_timeout, implement CIS Benchmark.

#### Lecture Notes

Database security failures are almost never sophisticated cryptographic attacks. They are: a developer committing a `.env` file to public GitHub, an analyst granted SELECT on everything when they needed only a view, a former employee whose role was never revoked. The DBA's security discipline is configuration, review, and continuous vigilance.

Practical exercise: harden a deliberately insecure PostgreSQL instance to pass the CIS Benchmark scanner.

The Norse metaphor: database security is the longhouse gate with carved wards — runes marking who may enter, who may speak, who may touch the hearth-fire. The DBA is the gate-keeper.

#### Required Reading

- PostgreSQL Documentation (2040). "Chapter 20: Client Authentication" and "Chapter 18.9: SSL."
- CIS (2040). *CIS PostgreSQL 18 Benchmark*.
- OWASP (2040). "Database Security Cheat Sheet."
- NIST SP 800-53 (2039). Database-relevant controls.

#### Discussion Questions

1. Revoking PUBLIC USAGE on public schema breaks the application. Diagnose and fix while maintaining security.
2. Column-level encryption: key lives on the application server. If the server is compromised, attacker has encrypted data and key. Does column-level encryption improve security? Analyse the threat model.
3. pgAudit logs to a file on the database server. A superuser DBA can modify or delete logs. How do you create a tamper-proof audit trail? Consider remote syslog, append-only cloud storage, cryptographic log chains.

---

### Lecture 10: Cloud Databases and Database-as-a-Service

**Course:** IT203 — Database Administration & Data Management  
**Degree:** Bachelor of Science in Information Technology, University of Yggdrasil, 2040

---

#### Overview

By 2040, 75% of new database deployments are on cloud platforms. This lecture covers the DBA's role in the cloud era: evaluating managed services, managing costs, and navigating multi-cloud and hybrid-cloud architectures.

#### Key Topics

- **The Managed Spectrum:** IaaS (you manage everything) → semi-managed (RDS — provider handles installation, patching, backups, replication setup) → fully managed serverless (Aurora Serverless v3 — automatic scaling) → cloud-native (DynamoDB, Spanner — databases designed for cloud scale). Trade-off: more management burden = more control; less burden = less control and higher vendor lock-in.
- **AWS RDS and Aurora:** RDS: automated backups, Multi-AZ (synchronous standby, automatic failover ~60s), up to 15 read replicas, parameter groups. Aurora: rearchitected storage engine — log is the database, distributed across 3 AZs with 6-way replication. Faster failover (~30s), automatic storage scaling to 128TB. 20–30% more expensive than RDS.
- **Google Spanner and CockroachDB:** NewSQL: SQL semantics with horizontal scalability. Spanner's TrueTime (atomic clocks + GPS globally synchronised clock). CockroachDB's hybrid logical clocks. Trade-off: Spanner = stronger consistency, Google-only, higher cost; CockroachDB = open-source option, runs anywhere. Globally distributed transactions add latency — 200ms minimum for 3-continent writes.
- **Cost Management:** Compute (instance hours), storage (GB-month), I/O (per million requests — unpredictable), data transfer (free within AZ, charged between AZs and regions — hidden cost), backups (snapshot storage). Cost-modelling exercise: 500 TPS, 2TB data, multi-AZ with replica, 30-day retention — estimate RDS vs. Aurora vs. EC2 vs. CockroachDB.
- **Multi-Cloud and Hybrid:** Use PostgreSQL for portability. Avoid cloud-specific extensions. Consider cross-cloud logical replication. Cautionary tale: company built on DynamoDB, then needed to deploy in a country without AWS — multi-year, multi-million-dollar migration.

#### Lecture Notes

The cloud has changed the DBA's work, not eliminated it. Configuration management becomes parameter group design. Query optimisation remains query optimisation. The cloud DBA who treats the managed service as a black box is a liability. Evaluation framework: HA, backup/recovery, performance, security, cost, lock-in.

#### Required Reading

- AWS Documentation (2040). "Amazon RDS for PostgreSQL User Guide" and "Amazon Aurora User Guide."
- Google Cloud Documentation (2040). "Cloud Spanner Documentation."
- CockroachDB Documentation (2040). "Architecture Overview."
- Barr, J. & Varia, J. (2038). *Cloud Financial Management for DBAs*, 3rd Edition.

#### Discussion Questions

1. Aurora faster failover: explain the architecture (storage/compute separation). What happens to in-flight transactions?
2. Startup chooses DynamoDB; three years later needs complex joins, multi-item ACID, and on-premises deployment. Early warning signs? How should they have designed for this?
3. RDS primary in us-east-1, read replica in eu-west-1. European user data must not leave EU, but primary (and WAL) is in US. Does this violate data residency? How to redesign?

---

### Lecture 11: Data Warehousing, ETL, and Analytics

**Course:** IT203 — Database Administration & Data Management  
**Degree:** Bachelor of Science in Information Technology, University of Yggdrasil, 2040

---

#### Overview

The DBA who only manages operational databases is missing half the picture. The data warehouse powers business intelligence, reporting, and decision-making. This lecture covers dimensional modelling (star schemas), ETL/ELT pipelines, and the 2040 real-time analytics movement (Apache Kafka + ClickHouse / Materialize).

#### Key Topics

- **OLTP vs. OLAP:** OLTP: fast, small transactions, row-oriented storage. OLAP: complex queries over large datasets, column-oriented storage. A query `SELECT AVG(revenue) FROM orders WHERE year = 2040` reads every column in a row store but only the revenue column in a column store — 10–100× I/O reduction.
- **Dimensional Modelling — The Star Schema:** Fact tables (quantitative events) and dimension tables (descriptive attributes). Slowly changing dimensions (Type 1: overwrite; Type 2: new row with effective dates; Type 3: previous value column). The date dimension: pre-populated with every date through 2050, with day_of_week, is_holiday, fiscal_year — enables time-series analysis without date arithmetic in every query. Degenerate dimensions.
- **ETL and ELT:** ETL: extract, transform, load (traditional). ELT: extract, load, transform (2040 pattern — raw data never lost, transformations re-runnable). dbt: standard transformation tool — SQL-based, version-controlled, testable, data lineage. Incremental loading: full refresh, incremental append, merge/upsert, change data capture (CDC). Data freshness monitoring.
- **Real-Time Analytics:** Operational events → Kafka → analytical engines. ClickHouse: columnar, queries billions of rows in milliseconds, materialised views for pre-aggregation. Materialize: streaming SQL, incrementally updated materialised views over Kafka. Kappa architecture: all data treated as streams.

#### Lecture Notes

The DBA understanding both OLTP and OLAP bridges the gap siloing most organisations. The operational database's schema design affects ETL complexity; ETL latency affects data freshness; warehouse query performance affects whether business decisions are data-driven.

The Norse metaphor: the operational database is the daily logbook of the longship. The data warehouse is the winter feast's saga — the long view revealing patterns invisible in daily entries. The DBA is both scribe and skald.

#### Required Reading

- Kimball, R. & Ross, M. (2038). *The Data Warehouse Toolkit*, 5th Edition. Wiley. Chapters 1–3, 19.
- dbt Labs (2040). *dbt Documentation*.
- ClickHouse Documentation (2040). "Getting Started" and "Materialized Views."
- Kleppmann, M. (2039). *Making Sense of Stream Processing*, 2nd Edition. O'Reilly Media.

#### Discussion Questions

1. OLTP normalised schema → OLAP star schema. Write ETL logic for daily aggregations. How to handle cancelled orders?
2. Columnar storage accelerates analytics but slows writes. Why do columnar databases like ClickHouse achieve high write throughput?
3. Streaming pipeline (PostgreSQL → Debezium → Kafka → Materialize) has 10-second SLA. Materialize shows 45-second lag. Walk through diagnosis — where could lag accumulate?

---

### Lecture 12: The 2040 Database Landscape — Vectors, AI, and Autonomous Databases

**Course:** IT203 — Database Administration & Data Management  
**Degree:** Bachelor of Science in Information Technology, University of Yggdrasil, 2040

---

#### Overview

The database landscape of 2040 is reshaped by three forces: vector databases enabling semantic search and RAG for AI, AI agents managing databases autonomously, and the convergence of transactional and analytical workloads into translytical databases. This final lecture surveys the frontier and asks students to envision data management in 2050.

#### Key Topics

- **Vector Databases and AI Integration:** Pinecone, Weaviate, Milvus, Qdrant, and pgvector store high-dimensional embeddings. HNSW and IVF algorithms for approximate nearest neighbour search over billions of vectors. RAG pipelines: retrieve context → augment prompt → generate grounded response. Operational concerns: embedding freshness, HNSW graph maintenance, storage costs (1,536-dimension × float32 = 6KB; 1 billion embeddings = 6TB). Hybrid search: vector similarity + keyword relevance + structured filters.
- **AI-Managed Databases:** Oracle Autonomous Database (self-patching, self-tuning, self-repairing). AWS DevOps Guru for RDS (ML anomaly detection). OtterTune (ML-driven tuning). What AI does well: index recommendations, anomaly detection. What AI does poorly: understanding business context (this slow query is a monthly report with no SLA). The DBA's evolving role: from manual tuner to AI supervisor.
- **Translytical Databases:** HTAP — Hybrid Transactional/Analytical Processing. SingleStore (in-memory rowstore + on-disk columnstore), TiDB (distributed SQL with HTAP), AlloyDB (columnar accelerator). Promise: one database instead of two, no ETL latency. Reality: good not great — dedicated systems still outperform for specialised workloads. Decision framework: when simplicity of one database outweighs performance of two.
- **The DBA of 2050:** Student projections and instructor predictions: (1) SQL will still be dominant. (2) The database will become an "AI memory system" — storing data, embeddings, model weights, and inference results. (3) The DBA's value proposition shifts from "I keep the database running" to "I keep the organisation's data trustworthy" — in a world of AI-generated content, data provenance and integrity become the defining challenge.

#### Lecture Notes

The DBA who learns PostgreSQL and stops there is a 2020 DBA. The DBA who learns PostgreSQL, MongoDB, Redis, Cassandra, ClickHouse, Kafka, and dbt — understanding when to use each — is a 2040 DBA. The DBA who stays curious about the frontier shapes the role for 2050.

The database is not a technical artefact; it is the organisation's memory. The DBA is the steward of that memory — responsible for its accuracy, availability, and protection. In a world drowning in data, the DBA who extracts signal from noise, answers business questions with confidence, and guarantees the answer is correct — that DBA is indispensable.

The Norse closing: the Norns carve runes of fate into the World Tree. The DBA carves schema into the relational model. Both are acts of inscription that shape what can be known. The database, like the runes, outlasts its creators. Carve well. ᛟ

#### Required Reading

- Johnson, J. et al. (2039). "Billion-Scale Similarity Search with HNSW." *IEEE Transactions on Knowledge and Data Engineering*.
- Oracle (2040). "Autonomous Database Technical Whitepaper."
- SingleStore Documentation (2040). "HTAP — Hybrid Transactional and Analytical Processing."
- Lewis, C.S. (2039). *The Database as Memory: Philosophical Perspectives on Data Persistence*. University of Yggdrasil Press.

#### Discussion Questions

1. Vector databases enable semantic search: "find documents about renewable energy policy" without exact phrase matching. How does this change data modelling? Does the relational model lose relevance?
2. An AI agent recommends 14 indexes, 5 duplicate existing ones. How do you evaluate? What operational process before implementing AI-suggested changes?
3. In 2050, databases and AI models blur — databases store embeddings and generate inferences; AI models store facts and answer queries. How do you ensure data integrity when the system that stores data also generates new data? What new concepts of backup, consistency, and audit are needed?

---

## Final Examination Preparation

### Component A: Written Examination (60%)

Select **five** of the following eight questions. Each answer should demonstrate technical depth, operational reasoning, and the ability to apply database administration principles to realistic scenarios.

1. **Disaster Recovery Scenario:** At 09:47 UTC, a storage array failure corrupts the primary PostgreSQL database's data directory. The synchronous standby in the same data centre also fails (common power supply). The asynchronous standby in a different region is 8 seconds behind. RPO: 5 minutes, RTO: 30 minutes. Describe the step-by-step recovery process: determining which transactions were lost, bringing the asynchronous standby online as the new primary, reconfiguring replication, and verifying data integrity. What if the asynchronous standby had been 7 minutes behind?

2. **Schema Design and Normalisation:** A startup's "orders" table has columns: order_id, customer_name, customer_address, customer_city, customer_country, product_name, product_category, product_price, quantity, order_date, shipping_method, shipping_cost. Normalise to BCNF. Write all CREATE TABLE statements. Then the startup asks you to denormalise customer_country into orders because "every report filters by country." Document this denormalisation: what anomaly does it introduce, how maintain consistency, under what circumstances reverse the decision?

3. **Query Performance Tuning:** Top query by total execution time joins 6 tables, includes `WHERE EXTRACT(YEAR FROM order_date) = 2040`, scans all tables sequentially. The orders table has 500 million rows with a B-tree index on order_date. The query plan shows sequential scans because EXTRACT() prevents index usage. Rewrite the query to use the index, describe alternative strategies (expression index, partial index, materialised view), and justify your choice based on performance vs. write overhead vs. storage.

4. **Replication Architecture:** Design database architecture for a global e-commerce platform (North America, Europe, Asia-Pacific). Requirements: sub-50ms local write latency, zero data loss for payment processing, sub-10ms local reads for product catalogue, survive a single AWS region failure. Specify: topology, replication strategy per data category, conflict resolution for simultaneous profile updates from two regions, failover procedure.

5. **Security Hardening:** Audit findings: (a) PUBLIC has CONNECT on all databases, (b) pg_hba.conf allows trust authentication for local connections, (c) log_statement = 'none', (d) three roles have SUPERUSER, (e) TLS configured but sslmode is 'prefer' (allows non-TLS fallback), (f) statement_timeout not set. For each: explain the risk, provide remediation, describe how to test without breaking the application.

6. **NoSQL Selection:** New application requires: (a) user profiles with variable fields (some 100 attributes, some 10), (b) real-time leaderboard (top 100 scores updated 1,000 times/second), (c) session storage with 30-minute TTL, (d) recommendation engine — "users who bought X also bought Y" (graph traversal). For each: recommend a database type, justify. Then: could a single multi-model database handle all four? Compare single-database approach to polyglot persistence.

7. **ETL Pipeline Design:** Operational PostgreSQL with 250 normalised tables. Analytics team needs a daily-updated star schema with 5 fact tables and 15 dimension tables. Design the ETL pipeline: extraction method, transformation logic (slowly changing dimensions, late-arriving facts), loading strategy, error handling, and monitoring (data freshness and correctness). Discuss ETL vs. ELT trade-off for this scenario.

8. **The 2050 Database:** Based on trends — vector databases, AI-managed databases, translytical engines, decentralised data, privacy-enhancing computation — construct a technically detailed vision of the database landscape in 2050. Describe: dominant data model(s), the DBA's role, how data privacy is enforced (GDPR evolved to what?), how organisations maintain data integrity when AI generates as much data as humans. Defend each element with reference to current trajectory and unresolved challenges.

### Component B: Practical Lab Examination (40%)

A 4-hour practical examination in YggLab Data Forge. Students are given a scenario — "Recover and Harden a Compromised Database" — and must:

1. Restore a PostgreSQL database from a base backup and WAL archives to a specific point in time (15 minutes before simulated data corruption).
2. Verify restored data integrity: row counts match pre-corruption snapshots, foreign keys intact, no duplicate transactions.
3. Design and create a normalised schema for an inventory management system (products, warehouses, stock levels, suppliers, purchase orders) from a natural-language specification.
4. Optimise three slow queries against the restored database using EXPLAIN ANALYZE output to justify index creation.
5. Configure replication: set up streaming replication from primary to standby, verify replication active, test failover.
6. Implement security hardening: apply CIS PostgreSQL Benchmark Level 1, configure pgAudit for DML auditing on financial tables, verify with CIS scanner.

**Evaluation Criteria:**
- Correctness (all services functional, data integrity verified)
- Performance (appropriate indexes, query plans verified)
- Security (CIS benchmark compliance, audit logging functional)
- Reliability (replication configured, failover tested)
- Documentation (operational runbook describing recovery, schema design decisions, and index justifications)

---

*Data outlasts the systems that create it, the servers that store it, and the DBAs who steward it. The database is the closest thing to immortality that information technology provides. Guard it as you would guard the memory of your ancestors — for in a real sense, that is exactly what it is.* ᛟ

— Dr. Sigrún Vérendóttir, University of Yggdrasil, 2040
