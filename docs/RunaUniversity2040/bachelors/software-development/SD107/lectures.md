# SD107: Introduction to Databases
## Bachelor of Science in Software Development — University of Yggdrasil, 2040

**Credits:** 4
**Semester:** Year 1, Semester 2
**Prerequisites:** SD101 (recommended)
**Instructor:** Dr. Sigrún Hafdísardóttir, Faculty of Computational Arts

> *"A database is a memory palace. Every table is a room, every row an artifact, every query a question asked of the past. The art is not in storing data — it is in finding it again."* — Sigrún Hafdísardóttir, *The Memory Palace* (2036)

---

## Course Description

Databases are the memory of the digital world. Every application — from a personal blog to the distributed memory wells of the Hermes framework — relies on a database to persist, organize, and retrieve information. This course introduces the fundamental concepts of database systems: the relational model, SQL, schema design and normalization, transactions and concurrency, indexing and query optimization, and the landscape of non-relational databases (document stores, graph databases, vector databases) that complement the relational core in 2040's polyglot persistence architectures.

The course emphasizes *why* over *what* — not just how to write a query, but why the query planner chose that execution plan; not just the rules of normalization, but the access patterns that sometimes justify denormalization. By the end, students will be able to design a database schema, write efficient queries, reason about consistency guarantees, and choose the right database for a given problem.

---

## Lectures

### ᚠ Lecture 1: What Is a Database? — Memory, Models, and the Persistence Imperative

**Date:** Week 1, Session 1

#### Overview

Before databases, there were files. Before files, there was paper. This lecture establishes what a database is — a system for persistent, structured, queryable memory — and traces the evolution from hierarchical and network databases through the relational revolution to the polyglot landscape of 2040.

#### Lecture Notes

Every program manipulates data. Some programs can forget — a calculator displays a result and moves on. Most programs must *remember* — a banking application must persist account balances across restarts, across hardware failures, across decades. This is the *persistence imperative*: if the data matters, it must survive the program that created it.

**What Makes a Database a Database?** Databases are distinguished from simple file storage by four properties:

1. **Structure:** Data is organized according to a *data model* — a formal description of what kinds of data can be stored and how they relate. The relational model organizes data into tables with rows and columns; the document model into nested JSON-like structures; the graph model into nodes and edges. Structure enables querying — you can ask "all customers who purchased in the last 30 days" because the database understands what a customer is and what a purchase is.

2. **Query Language:** A database provides a declarative language for describing *what* you want, not *how* to get it. SQL (`SELECT name FROM users WHERE age > 18`) describes the desired result; the database figures out which indexes to use, which order to scan tables in, and how to join them. This separation of *what* from *how* is the database's greatest contribution to computer science.

3. **Concurrency Control:** Multiple users (or application threads) can read and write simultaneously without corrupting the data. The database ensures that each transaction sees a consistent view of the data and that concurrent transactions don't interfere with each other in undefined ways.

4. **Durability:** Once the database confirms that data has been written, it stays written — across power failures, software crashes, and hardware faults. This requires careful management of write-ahead logs, fsync calls, and replication.

**A Brief History.** 

- **1960s: Hierarchical and Network Databases.** IBM's IMS (1968) organized data in tree structures. CODASYL (1969) allowed more complex graph-like relationships. Both required the programmer to navigate the structure explicitly — "get next child," "get parent." The programmer had to know the physical layout.

- **1970: The Relational Model.** Edgar Codd's paper "A Relational Model of Data for Large Shared Data Banks" proposed a radical idea: data should be organized into *relations* (tables) with no explicit pointers. Relationships are represented by values (foreign keys), not by pointers. The programmer writes declarative queries; the database figures out navigation. Codd's paper was theoretical — it took another decade for efficient implementations.

- **1980s: SQL Dominance.** Oracle (1979), IBM DB2 (1983), and the SQL standard (1986) established the relational model as the industry default. SQL proved that declarative queries could be both expressive and efficient.

- **2000s: The NoSQL Movement.** Web-scale applications (Google, Amazon, Facebook) hit the limits of single-server relational databases. The response: distributed non-relational databases optimized for specific access patterns — document stores (MongoDB, 2009), column-family stores (Cassandra, 2008), key-value stores (DynamoDB, 2012). The "NoSQL" label (originally "Not Only SQL") captured the shift from one-size-fits-all to *polyglot persistence*.

- **2020s-2040s: Convergence and Specialization.** Relational databases added JSON columns, graph queries, and horizontal scaling (CockroachDB, TiDB). NoSQL databases added SQL-like query languages and transactions (MongoDB 4.0+, Cassandra 5.0+). The distinction blurred. Meanwhile, new specialized databases emerged: vector databases (Pinecone, Weaviate, Mímir-Vector) for AI embeddings, time-series databases for IoT sensor data, ledger databases for cryptographic audit trails.

**Databases as Memory.** In the Norse cosmology that informs the University of Yggdrasil, Mímir's Well is the well of wisdom — the place where knowledge is stored and can be drawn from by those who know how to ask. A database is exactly this: a well of structured knowledge. The query is the ritual by which we draw from it. The schema is the shape of the vessel that holds the water. This is not metaphor — it is a structural truth about how information systems work.

#### Required Reading

- Codd, E.F. (1970). "A Relational Model of Data for Large Shared Data Banks." *Communications of the ACM*, 13(6), 377-387. [Read the original. It is short, clear, and changed the world.]
- Kleppmann, M. (2036). *Designing Data-Intensive Applications* (3rd ed.). O'Reilly Media. Chapter 1: "Reliable, Scalable, and Maintainable Applications."
- Hafdísardóttir, S. (2036). *The Memory Palace*. University of Yggdrasil Press. Chapter 1: "Why We Store."

#### Discussion Questions

1. Codd's 1970 paper was purely theoretical — it described a mathematical model with no implementation. Why did it take a decade to build efficient relational databases? What was the gap between theory and practice?
2. The NoSQL movement was partly a reaction to the limitations of relational databases at web scale. In 2040, those limitations have largely been solved. Was NoSQL a temporary workaround, or did it permanently expand the database design space?
3. "The query is the ritual by which we draw from the well." What are the implications of treating a database as a *memory* rather than a *tool*? Does this framing change how we design schemas or write queries?

---

### ᚢ Lecture 2: The Relational Model — Relations, Tuples, and the Algebra of Data

**Date:** Week 1, Session 2

#### Overview

The relational model is a mathematical theory of data management. This lecture presents the model formally: domains, relations, tuples, keys, and the relational algebra (selection, projection, join, union, difference) that underlies SQL. Understanding the algebra makes SQL comprehensible rather than memorized.

#### Lecture Notes

Codd's insight was that data management could be founded on set theory and first-order predicate logic — the same mathematics that underlies much of computer science. A *relation* is a set of tuples, each tuple being an ordered set of attribute values. A *database* is a collection of relations.

This formalism gives the relational model three powerful properties:

1. **Data independence:** The logical structure (relations) is separate from the physical storage (files, indexes, disk layout). You can change how data is stored without changing how applications query it.
2. **Declarative querying:** Because relations are mathematical objects, you can define a set of operations (the relational algebra) that transform relations into other relations. A query is an expression in this algebra — the database can optimize it using algebraic laws.
3. **Integrity constraints:** The model can express rules that must hold: primary keys (no two tuples have the same key), foreign keys (a value must exist in another relation), and arbitrary predicates (CHECK constraints).

**Relations, Not Tables.** "Relation" is not just a fancy word for "table." A table is a visual representation. A relation is a mathematical set — order doesn't matter (rows can be returned in any order), duplicates don't exist (every tuple is unique), and the structure is defined by the attribute names, not by position. SQL violates some of these properties (it allows duplicate rows, for pragmatic reasons), but understanding the pure model clarifies why certain SQL behaviors exist.

**The Relational Algebra.** Six fundamental operations:

1. **Selection (σ):** Filter rows. σ_{age > 18}(users) — all users older than 18.
2. **Projection (π):** Choose columns. π_{name, email}(users) — just the name and email columns.
3. **Union (∪):** Combine two relations with the same attributes. active_users ∪ inactive_users.
4. **Set Difference (−):** Tuples in relation A but not B. all_users − admin_users.
5. **Cartesian Product (×):** Every combination of tuples from two relations. users × orders — every user paired with every order (usually followed by selection to keep only matching pairs).
6. **Rename (ρ):** Change attribute names for disambiguation. ρ_{uid → user_id}(users).

From these six primitives, all of SQL is built. A JOIN is a Cartesian product followed by a selection. A subquery is a nested algebraic expression. GROUP BY is an extension of projection with aggregation.

**Keys.** A *superkey* is any set of attributes that uniquely identifies a tuple. A *candidate key* is a minimal superkey (remove any attribute and it's no longer unique). The *primary key* is the candidate key chosen by the designer as the main identifier. *Foreign keys* reference primary keys in other relations — they are how relations connect.

In 2040, the University of Yggdrasil's Entity Canonization Protocol generalizes primary keys into *entity identity hashes* — content-addressed identifiers that are globally unique, not just locally unique within a table. This is the relational model extended for distributed, cryptographically verifiable identity.

#### Required Reading

- Codd, E.F. (1970). Same paper as Lecture 1 — reread Sections 1.3-1.5 on the relational algebra.
- Date, C.J. (2042). *An Introduction to Database Systems* (10th ed.). Addison-Wesley. Chapters 3-5.
- Hafdísardóttir, S. (2041). "Entity Canonization and the Relational Model." *Journal of Database Theory*, 18(2), 145-178.

#### Discussion Questions

1. SQL allows duplicate rows; Codd's pure relational model does not. Is this a pragmatic compromise or a corruption of the model? What problems do duplicates cause?
2. The relational algebra has six fundamental operations. SQL has hundreds of functions and clauses. Is SQL too large? Should a query language be minimal and composable?
3. Foreign keys are the relational model's mechanism for representing relationships. But they are unidirectional — you can find a user's orders, but finding who ordered a product is a different query path. Is this a limitation? How do graph databases handle this differently?

---

### ᚦ Lecture 3: SQL — The Lingua Franca of Data

**Date:** Week 2, Session 1

#### Overview

SQL is the most enduring programming language in computing history — 50 years old in 2040 and still the default interface to structured data. This lecture covers SQL from `SELECT` to window functions: the core DML (SELECT, INSERT, UPDATE, DELETE), joins (INNER, LEFT, RIGHT, CROSS), aggregation (GROUP BY, HAVING), subqueries, and the modern enhancements that make SQL a general-purpose data processing language.

#### Lecture Notes

SQL (Structured Query Language) was originally spelled SEQUEL (Structured English QUEry Language) and designed to be readable by non-programmers — business analysts who could write "SELECT NAME FROM EMPLOYEES WHERE DEPARTMENT = 'SALES'" and get an answer. It succeeded beyond its creators' wildest dreams: in 2040, SQL is used by developers, data scientists, AI agents, and yes, still a few business analysts.

**The Anatomy of a SELECT.** The logical processing order of a SELECT statement is not the written order:

```sql
SELECT   department, COUNT(*) as emp_count    -- 5. Project
FROM     employees                            -- 1. Source
WHERE    hire_date > '2030-01-01'             -- 2. Filter rows
GROUP BY department                           -- 3. Group
HAVING   COUNT(*) > 5                         -- 4. Filter groups
ORDER BY emp_count DESC                       -- 6. Sort
LIMIT    10;                                  -- 7. Slice
```

This order (FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT) explains otherwise-mysterious behavior: you can't reference column aliases in WHERE (they're defined in SELECT, which hasn't run yet), but you can in ORDER BY (SELECT has already run).

**Joins.** The mechanism by which relations are connected:

```sql
SELECT u.name, o.order_date, o.total
FROM users u
INNER JOIN orders o ON u.id = o.user_id;
```

Join types:
- **INNER JOIN:** Returns only rows where the condition matches in both tables. The most common join.
- **LEFT JOIN:** Returns all rows from the left table, with NULLs for the right table where no match exists. "Show me all customers and their orders, including customers with no orders."
- **RIGHT JOIN:** The mirror — all rows from the right table. Less common; usually rewritten as a LEFT JOIN.
- **FULL OUTER JOIN:** All rows from both tables. "Show me all customers and all orders, even if some orders have no customer." (Rare; usually a data quality check.)
- **CROSS JOIN:** Cartesian product — every row from left paired with every row from right. `FROM users CROSS JOIN products`. Used for generating combinations.

**Aggregation.** SQL can summarize data with aggregate functions:

```sql
SELECT
  department,
  COUNT(*) as employee_count,
  AVG(salary) as avg_salary,
  MAX(hire_date) as newest_hire
FROM employees
GROUP BY department
HAVING AVG(salary) > 75000;
```

The GROUP BY clause partitions rows into groups; aggregate functions compute one value per group; HAVING filters groups (like WHERE filters rows). Common mistake: putting a filter on an aggregate in WHERE instead of HAVING.

**Window Functions (SQL:2003, universal by 2040).** Window functions compute across a set of rows related to the current row, without collapsing them into groups:

```sql
SELECT
  name,
  department,
  salary,
  RANK() OVER (PARTITION BY department ORDER BY salary DESC) as dept_rank,
  AVG(salary) OVER (PARTITION BY department) as dept_avg
FROM employees;
```

This gives each employee their salary, their rank within their department, and their department's average salary — all in one pass. Window functions eliminate many subqueries and self-joins.

**Common Table Expressions (CTEs).** CTEs make complex queries readable:

```sql
WITH dept_stats AS (
  SELECT department, AVG(salary) as avg_sal
  FROM employees
  GROUP BY department
),
high_earners AS (
  SELECT name, department, salary
  FROM employees
  WHERE salary > 100000
)
SELECT h.name, h.department, h.salary, d.avg_sal
FROM high_earners h
JOIN dept_stats d ON h.department = d.department
WHERE h.salary > d.avg_sal * 1.5;
```

CTEs are like named subqueries — they make the query tell a story. The `WITH RECURSIVE` variant handles hierarchical data (org charts, category trees, thread replies).

**The AI Query Assistant.** In 2040, AI copilots can translate natural language to SQL: "Show me the top 5 customers by revenue in Q1 2040" → a correct query. But the developer still needs to verify the query's correctness, understand its performance implications, and recognize when the AI has misunderstood the schema or the business logic. SQL literacy remains essential — the AI accelerates writing, but the human validates meaning.

#### Required Reading

- Date, C.J. (2042). *An Introduction to Database Systems*. Chapters 8-11.
- Beaulieu, A. (2040). *Learning SQL* (5th ed.). O'Reilly Media. Chapters 1-9.
- PostgreSQL Documentation. "Tutorial." *postgresql.org/docs/current/tutorial.html*. [The best SQL tutorial; worth reading even if you use another database.]

#### Discussion Questions

1. SQL is a declarative language — you describe *what* you want, not *how* to get it. But experienced SQL developers think procedurally (first this index, then that join). Is "declarative" an illusion? Does effective SQL require understanding the execution engine?
2. NULL in SQL represents "unknown" or "missing." But NULL has strange properties: `NULL = NULL` is false (you must use `IS NULL`), `NULL + 1` is NULL, `AVG()` ignores NULLs. Is NULL a mistake in SQL's design, or a necessary representation of missing data?
3. AI query generators can produce correct SQL, but they can also produce correct-looking SQL that is subtly wrong (wrong join condition, wrong aggregation level). How do you validate an AI-generated query without manually understanding the schema?

---

### ᚨ Lecture 4: Schema Design and Normalization — The Art of Avoiding Anomalies

**Date:** Week 2, Session 2

#### Overview

A poorly designed schema causes update anomalies, insert anomalies, and delete anomalies — data corruption that no amount of application code can fix. This lecture teaches normalization: the formal process of decomposing relations to eliminate redundancy while preserving information. We cover first through fifth normal forms, with emphasis on the practical third normal form that suffices for most designs.

#### Lecture Notes

Consider a table that stores employee information:

```
Employee_Skills
------------------------------
emp_id | emp_name | dept    | skill
1      | Alice    | Eng     | Python
1      | Alice    | Eng     | SQL
1      | Alice    | Eng     | Docker
2      | Bob      | Eng     | Python
```

**Update Anomaly:** If the Engineering department is renamed to "Platform Engineering," we must update every row for every engineer. Miss one, and we have inconsistent data — Alice is in "Platform Engineering" but Bob is still in "Eng."

**Insert Anomaly:** We want to add a new department "Design" but we have no employees in it yet. Can't insert — `emp_id` is part of the key and we have no employee. The department's existence depends on having employees.

**Delete Anomaly:** Bob leaves the company. Delete his row. Now "Python" is no longer listed as a skill in the company — even though Alice still has it. Deleting Bob inadvertently deletes information about skills.

**Normalization to the Rescue.** Normalization decomposes this table into separate relations, each representing one "fact":

```
Employee          Department        Skill        Employee_Skill
--------          ----------        -----        --------------
emp_id | name     dept_id | name    skill_id     emp_id | skill_id
1      | Alice    E1      | Eng    | Python      1      | Python
2      | Bob                         | SQL         1      | SQL
                                      | Docker      1      | Docker
                                                    2      | Python
```

Now: renaming a department changes one row. Adding an empty department just inserts into `Department`. Deleting an employee doesn't lose skill information.

**The Normal Forms:**

- **First Normal Form (1NF):** All attributes are atomic — no repeating groups, no arrays within a single cell. Each row-column intersection contains exactly one value.

- **Second Normal Form (2NF):** 1NF + every non-key attribute depends on the *entire* primary key, not just part of it. If your primary key is (emp_id, skill_id), the employee's name should depend on emp_id alone — so it belongs in a separate Employee table.

- **Third Normal Form (3NF):** 2NF + no transitive dependencies. If emp_id → dept_id → dept_name, then dept_name is transitively dependent on emp_id. Split into Employee (emp_id, dept_id) and Department (dept_id, dept_name).

- **Boyce-Codd Normal Form (BCNF):** A stricter 3NF. Every determinant must be a candidate key. Rarely needed in practice; 3NF handles most cases.

- **Fourth Normal Form (4NF):** No multi-valued dependencies. If an employee has multiple skills AND multiple certifications, and these are independent, store them in separate tables.

- **Fifth Normal Form (5NF):** The relation cannot be decomposed further without losing information. Achieving 5NF means the schema is free of all join dependencies.

**The Pragmatic Rule:** "Normalize until it hurts, denormalize until it works." Third normal form is the sweet spot for most applications — it eliminates the major anomalies without excessive table proliferation. Sometimes you denormalize deliberately for performance (storing a count or summary alongside the detail data), but you do so knowingly, documenting the tradeoff.

**Denormalization and the 2040 Perspective.** In the distributed database era, normalization has new dimensions. A fully normalized schema may require joins across geographically distributed partitions, which are expensive. The CAP theorem forces choices: you might denormalize to keep related data on the same partition, accepting the risk of update anomalies in exchange for query performance. This is not a failure of normalization — it's a conscious engineering tradeoff, documented and monitored.

#### Required Reading

- Date, C.J. (2042). *An Introduction to Database Systems*. Chapters 13-15 (Normalization).
- Kent, W. (1983). "A Simple Guide to Five Normal Forms in Relational Database Theory." *Communications of the ACM*, 26(2), 120-125. [The clearest explanation ever written; short and brilliant.]
- Kleppmann, M. (2036). *Designing Data-Intensive Applications*. Chapter 2: "Data Models and Query Languages" — especially the section on schema design.

#### Discussion Questions

1. "Normalize until it hurts, denormalize until it works." When does normalization "hurt" — what are the genuine costs of a fully normalized schema?
2. Many NoSQL databases (document stores, key-value stores) encourage denormalization by design — you embed related data rather than referencing it. Is this a feature (simpler queries) or a regression (update anomalies return)?
3. In 2040, AI assistants can propose schema normalizations automatically. But normalization is not purely mechanical — it requires understanding the *meaning* of the data. Can an AI know that "department_name" is functionally dependent on "department_id" without being told?

---

### ᚱ Lecture 5: Indexing — Finding Needles in Digital Haystacks

**Date:** Week 3, Session 1

#### Overview

A query that scans every row in a billion-row table is useless. Indexes are the data structures that make queries fast. This lecture covers B-trees (the universal index), hash indexes, bitmap indexes, full-text indexes (GIN/GiST), and the 2040-era specializations: vector indexes (HNSW) for AI embeddings and spatial indexes (R-trees) for geographic data.

#### Lecture Notes

"You can't manage what you can't measure." In databases: "You can't query what you can't find." An index is a data structure that maps search key values to the locations of rows containing those values — like the index at the back of a book, but constantly updated as rows are inserted, updated, and deleted.

**B-Trees: The Universal Index.** The B-tree (Bayer & McCreight, 1971) is the most important data structure in database history. It is a balanced tree where:

- Every node contains multiple keys and pointers (branching factor typically 50-2000)
- The tree is always balanced — all leaves are at the same depth
- Insertions, deletions, and searches all run in O(log n) time
- Nodes are sized to match disk page sizes (4KB-16KB), minimizing I/O

The B-tree variant most databases use is the **B+tree**: all data is stored in the leaf nodes (internal nodes just route), and leaves are linked together in a sorted linked list. This enables:
- Range queries: "all employees with salary BETWEEN 50000 AND 75000" — find the first qualifying leaf, then follow the linked list
- Ordered scans: `ORDER BY salary` can use the index to return rows in order without sorting
- Covering indexes: if all queried columns are in the index, the database never needs to read the table itself

**Hash Indexes.** For exact-match queries (`WHERE id = 12345`), a hash index provides O(1) lookup. Faster than a B-tree for this case. But hash indexes cannot handle range queries or sorting, so they're specialized tools.

**Bitmap Indexes.** For low-cardinality columns (gender, status, boolean flags), bitmap indexes compress dramatically and enable fast bitwise operations. `WHERE status = 'active' AND gender = 'F'` becomes a bitwise AND of two bitmaps. Used heavily in data warehouses.

**Full-Text Indexes (GIN/GiST).** For searching text: "find all documents containing the phrase 'relational model'." Inverted indexes map words to document IDs, with position information for phrase matching. PostgreSQL's GIN (Generalized Inverted Index) is the gold standard; it supports stemming, ranking, and phrase search.

**Vector Indexes (2040).** For AI embeddings — high-dimensional vectors (384, 768, 1536 dimensions) representing the semantic meaning of text, images, or audio. Vector indexes use approximate nearest neighbor algorithms (HNSW, IVF, PQ) because exact search in 768 dimensions is infeasible. The Mímir-Vector backend uses HNSW indexes for semantic search across memory well entries.

**Spatial Indexes (R-trees).** For geographic data: "find all restaurants within 5km of this point." R-trees organize spatial objects by their bounding boxes, enabling efficient overlap and containment queries.

**The Cost of Indexes.** Indexes are not free:
- They consume storage: typically 10-30% of the table size
- They slow down writes: every INSERT, UPDATE, and DELETE must update all relevant indexes
- Too many indexes confuse the query planner: more options → more chance of a bad plan

Indexing is an optimization problem: for each table, choose the indexes that best serve the query patterns, accepting that too many indexes is as harmful as too few. In 2040, AI-powered index advisors (HypoPG, pg_qualstats) analyze query logs and recommend indexes — but the human verifies that the recommendations match the access patterns.

#### Required Reading

- Bayer, R. & McCreight, E. (1971). "Organization and Maintenance of Large Ordered Indices." *Acta Informatica*, 1, 173-189. [The B-tree paper.]
- PostgreSQL Documentation. "Index Types" and "Indexes and ORDER BY." *postgresql.org/docs/current/indexes.html*.
- Mímir-Vector Documentation. "HNSW Index Configuration." *docs.yggdrasil.university/mimir-vector/hnsw*.

#### Discussion Questions

1. B-trees have been the dominant index structure for 70 years. Will they still be in 2070? What would replace them?
2. Vector indexes (HNSW) trade recall for speed — they're approximate, not exact. When is approximate good enough? When is it not?
3. "Too many indexes" slows writes and confuses the query planner. How many indexes is "too many"? Is there a principled limit, or is it always workload-dependent?

---

### ᚲ Lecture 6: Transactions and Concurrency — ACID and the Illusion of Solitude

**Date:** Week 3, Session 2

#### Overview

A transaction is a unit of work that transforms the database from one consistent state to another. This lecture covers the ACID properties (Atomicity, Consistency, Isolation, Durability), isolation levels (Read Uncommitted through Serializable), and the concurrency control mechanisms (locking, MVCC) that make concurrent transactions safe.

#### Lecture Notes

Imagine two people simultaneously booking the last seat on a flight. Without concurrency control, both could see "1 seat available," both could book it, and the airline has sold the same seat twice. This is a *race condition*, and it is the database's job to prevent it.

**ACID.** The four properties that define a reliable transaction:

- **Atomicity:** A transaction is all-or-nothing. If any part fails, the entire transaction is rolled back — no partial updates. "Transfer $100 from A to B" either completes (A decremented, B incremented) or it doesn't happen at all. Never A decremented but B not incremented.

- **Consistency:** The transaction preserves database invariants. If the schema says `balance >= 0`, a transaction that would make a balance negative is rejected. The database enforces constraints (foreign keys, CHECK, NOT NULL) at transaction boundaries.

- **Isolation:** Concurrent transactions do not interfere with each other. Each transaction should appear to run *as if it were the only transaction* — even though in reality they're interleaved. This is the most complex and most compromised property.

- **Durability:** Once committed, a transaction survives system failures. The database uses write-ahead logging (WAL): before modifying data, it writes the intended change to an append-only log. If the system crashes mid-transaction, the log is replayed on recovery to complete committed transactions and undo uncommitted ones.

**Isolation Levels.** Full serializable isolation (every transaction appears to run one-at-a-time) is expensive. Databases offer weaker levels with specific guarantees:

| Level | Dirty Read | Non-repeatable Read | Phantom Read | Serialization Anomaly |
|-------|-----------|-------------------|--------------|----------------------|
| Read Uncommitted | Possible | Possible | Possible | Possible |
| Read Committed | Prevented | Possible | Possible | Possible |
| Repeatable Read | Prevented | Prevented | Possible | Possible |
| Serializable | Prevented | Prevented | Prevented | Prevented |

- **Dirty Read:** Transaction A reads uncommitted changes from Transaction B. If B rolls back, A has read data that never "really" existed.
- **Non-repeatable Read:** Transaction A reads a row. Transaction B updates that row and commits. Transaction A reads the same row again and gets different data.
- **Phantom Read:** Transaction A reads a set of rows matching a condition. Transaction B inserts a new row matching that condition and commits. Transaction A re-reads and now sees a "phantom" row.
- **Serialization Anomaly:** A more complex inconsistency where concurrent transactions produce a result that no serial execution would have produced (e.g., write skew).

**MVCC — Multi-Version Concurrency Control.** The dominant concurrency mechanism in 2040 databases. Instead of locking rows, MVCC keeps multiple versions of each row. Each transaction sees a *snapshot* of the database as of its start time. Writers don't block readers; readers don't block writers. When two transactions try to modify the same row, the second one detects the conflict and retries or aborts.

MVCC explains why long-running transactions are dangerous: the database must retain old row versions for the transaction's entire duration. A transaction that runs for hours and never commits causes table bloat and vacuum pressure. The rule: **keep transactions short.**

**Distributed Transactions (2040).** When data is spread across multiple database nodes (as in the Yggdrasil distributed memory well), ACID becomes harder. The CAP theorem says you can't have both Consistency (all nodes see the same data) and Availability (every request gets a response) when Partition tolerance is required. Distributed databases use two-phase commit (2PC), Paxos/Raft consensus, or CRDT-based eventual consistency — each sacrificing some ACID property for scale.

#### Required Reading

- Gray, J. & Reuter, A. (1992). *Transaction Processing: Concepts and Techniques*. Morgan Kaufmann. Chapters 1-4. [The classic. Dense but definitive.]
- PostgreSQL Documentation. "Transaction Isolation." *postgresql.org/docs/current/transaction-iso.html*. [Clear and practical.]
- Kleppmann, M. (2036). *Designing Data-Intensive Applications*. Chapter 7: "Transactions."

#### Discussion Questions

1. Serializable isolation is the "gold standard" but most applications use Read Committed. What kinds of applications genuinely need serializability? What are the risks of using a weaker level?
2. MVCC provides snapshot isolation, which prevents most race conditions but not write skew. Should databases default to a level that prevents write skew, even at a performance cost?
3. The CAP theorem says you must choose between consistency and availability during a partition. In the Yggdrasil distributed memory well, which should take priority — consistency or availability? Justify your answer with reference to the use case.

---

### ᚷ Lecture 7: Query Optimization — How the Database Plans Your Query

**Date:** Week 4, Session 1

#### Overview

A single SQL query can be executed in thousands of different ways — different join orders, different indexes, different algorithms. The query optimizer's job is to choose the best plan. This lecture explains how optimizers work: cost-based optimization, statistics, join algorithms (nested loop, hash join, merge join), and the `EXPLAIN` command that lets you inspect the chosen plan.

#### Lecture Notes

You write: `SELECT * FROM users JOIN orders ON users.id = orders.user_id WHERE orders.date > '2040-01-01'`. The database might:
- Scan `orders`, filter by date, then look up each matching `user_id` in the `users` primary key index
- Scan `users`, then look up each in `orders` (probably worse if the date filter is selective)
- Hash both tables and perform a hash join
- Use a merge join if both are already sorted

The optimizer's job is to pick the best plan using:
1. **Cost estimation:** A mathematical model of I/O and CPU costs
2. **Statistics:** How many rows in each table, how many distinct values, value distribution
3. **Algebraic rewriting:** Transform the query into equivalent but more efficient forms

**Join Algorithms:**

- **Nested Loop Join:** For each row in the outer table, scan the inner table for matches. O(m × n) worst case. Works well when the outer table is small and the inner table has an index on the join column.

- **Hash Join:** Hash the smaller table into memory. Scan the larger table, probing the hash table for matches. O(m + n). The workhorse of modern databases. Requires enough memory for the hash table.

- **Merge Join:** Sort both tables on the join column, then merge like merge sort. O(m log m + n log n). Best when both inputs are already sorted (e.g., by an index).

**Statistics.** The optimizer relies on table statistics: row count, distinct values per column, most common values and their frequencies, histograms of value distribution. Stale statistics → bad plans. `ANALYZE` (PostgreSQL) or `UPDATE STATISTICS` (SQL Server) refreshes them. In 2040, databases automatically refresh statistics based on change volume, reducing (but not eliminating) the need for manual maintenance.

**`EXPLAIN` and `EXPLAIN ANALYZE`.** The most powerful query debugging tool:

```sql
EXPLAIN ANALYZE
SELECT u.name, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;
```

Output: the chosen plan (nested loop, hash join, etc.), estimated costs, actual execution time, row counts. Discrepancies between estimated and actual rows signal stale statistics. Sequential scans on large tables signal missing indexes. This is the developer's window into the optimizer's mind.

**Query Hints and the 2040 Perspective.** Historically, databases provided "hints" to override the optimizer (`/*+ INDEX(users idx_name) */`). These were fragile — they didn't adapt as data changed. In 2040, the trend is toward **adaptive optimization**: the database learns from query execution history and adjusts plans automatically, without explicit hints. The DBA's role shifts from "tell the optimizer what to do" to "verify the optimizer is making good choices and tune the statistics."

#### Required Reading

- PostgreSQL Documentation. "Using EXPLAIN." *postgresql.org/docs/current/using-explain.html*. [Read every word; this is your most-used documentation page.]
- Garcia-Molina, H., Ullman, J.D., & Widom, J. (2030). *Database Systems: The Complete Book* (3rd ed.). Pearson. Chapters 15-16 (Query Optimization).
- Hafdísardóttir, S. (2042). "Adaptive Query Optimization in the Hermes Era." *Proceedings of VLDB*, 15(8), 1801-1814.

#### Discussion Questions

1. The query optimizer is fundamentally a heuristic system — it estimates costs and chooses the best plan, but it can be wrong. Should databases expose more control to developers, or should we trust the optimizer?
2. `EXPLAIN ANALYZE` shows you the plan the optimizer chose, not the plans it rejected. How can you tell if there's a better plan? What tools and techniques exist for plan comparison?
3. AI models learn from data. Could we train a model to predict optimal query plans, replacing the cost-based optimizer? What would be the challenges?

---

### ᚹ Lecture 8: NoSQL — Documents, Graphs, and the Polyglot Persistence Landscape

**Date:** Week 4, Session 2

#### Overview

Not all data fits in tables. This lecture surveys the non-relational database landscape: document stores (MongoDB, CouchDB), key-value stores (Redis, DynamoDB), column-family stores (Cassandra, HBase), graph databases (Neo4j, ArangoDB), and the 2040-era specialized stores: vector databases (Mímir-Vector), time-series databases, and ledger databases.

#### Lecture Notes

The term "NoSQL" was coined in 2009 for a meetup about "open-source, distributed, non-relational databases." It was an unfortunate name — it defined the category by what it wasn't, not by what it was. By 2040, the term has mellowed into "polyglot persistence" — the recognition that different data models suit different problems.

**Document Stores (MongoDB, CouchDB, Firestore).** Data is stored as documents — typically JSON — in collections. Documents are self-contained: a user document includes the user's addresses and preferences, not just IDs referencing other tables. This makes reads fast (one document, no joins) at the cost of potential update anomalies and data duplication.

Best for: Content management, user profiles, catalogs where the access pattern is "get everything about this entity."

**Key-Value Stores (Redis, DynamoDB, etcd).** The simplest model: a key (string) maps to a value (string, JSON, binary). Redis adds data structures: lists, sets, sorted sets, streams. DynamoDB adds a richer key structure (hash key + sort key) and conditional updates.

Best for: Caching, session storage, rate limiting, leaderboards, distributed locks.

**Column-Family Stores (Cassandra, HBase, ScyllaDB).** Rows are grouped into column families, and columns within a family are stored together. Designed for write-heavy workloads at massive scale. Partitioning by key enables horizontal scaling across hundreds of nodes.

Best for: Time-series data, event logs, IoT sensor data, messaging systems.

**Graph Databases (Neo4j, ArangoDB, TigerGraph).** Entities are nodes; relationships are edges — both are first-class citizens with properties. Queries traverse the graph: "Find all friends-of-friends of Alice who like the same movies as Bob." Graph databases make this a single query; in a relational database, it would be a recursive CTE or multiple joins.

Best for: Social networks, recommendation engines, fraud detection, knowledge graphs.

**Vector Databases (Mímir-Vector, Pinecone, Weaviate, Milvus — 2030s).** Store high-dimensional vectors (embeddings) and retrieve them by similarity. The query "find memories similar to this one" becomes a vector similarity search (cosine similarity, Euclidean distance) over millions of vectors.

Best for: Semantic search, AI memory, recommendation ("similar to this"), anomaly detection.

**The Decision Framework.** When choosing a database, ask:
1. **What is the data shape?** Tabular → relational. Nested/document → document store. Graph → graph database. Vectors → vector database.
2. **What are the access patterns?** "Get by primary key" → key-value. "Complex joins and aggregations" → relational. "Traverse relationships" → graph.
3. **What scale?** Single server → relational (postgres is fine to ~10TB). Multi-region, hundreds of TB → Cassandra, DynamoDB. Millions of QPS → Redis for hot data, relational for cold.
4. **What consistency?** Strong consistency → relational, some graph DBs. Eventual consistency → Cassandra, DynamoDB (default mode). Tuneable → MongoDB, CosmosDB.
5. **What does your team know?** The best database is the one your team can operate effectively. An expertly run PostgreSQL beats a poorly run anything else.

**The Convergence.** In 2040, the boundaries are blurring. PostgreSQL has JSONB (document model), ltree and recursive CTEs (graph-like), and pgvector (vector similarity). It is, for many applications, the only database you need. The specialized databases (Mímir-Vector for AI embeddings, Cassandra for planetary-scale writes) remain essential for their niches, but fewer projects need them than in 2015.

#### Required Reading

- Fowler, M. & Sadalage, P.J. (2012). *NoSQL Distilled*. Addison-Wesley. Chapters 1-5. [Dated but excellent on the fundamentals.]
- Kleppmann, M. (2036). *Designing Data-Intensive Applications*. Chapter 2: "Data Models and Query Languages."
- Mímir-Vector Documentation. "Architecture and Use Cases." *docs.yggdrasil.university/mimir-vector/architecture*.

#### Discussion Questions

1. PostgreSQL now supports JSON, graph queries, and vector search. Is "polyglot persistence" still necessary, or can a sufficiently capable relational database handle everything?
2. Document databases encourage denormalization. For a user profile that appears in multiple contexts (orders, reviews, messages), should each context store a denormalized copy, or should they reference a canonical user? What are the tradeoffs?
3. Graph databases make relationship traversal fast, but they require thinking about data as a graph from the beginning. If you've already built a relational schema, is it worth migrating to a graph database for specific features? When?

---

### ᚺ Lecture 9: Distributed Databases — Sharding, Replication, and the CAP Theorem

**Date:** Week 5, Session 1

#### Overview

When a single server can't handle the load, the database must be distributed across multiple machines. This lecture covers horizontal scaling strategies: replication (copies of data on multiple nodes, for read scaling and fault tolerance) and sharding (partitioning data across nodes, for write scaling). We examine the CAP theorem, consensus protocols (Paxos, Raft), and the architectures of 2040's distributed databases.

#### Lecture Notes

A single PostgreSQL server on modern hardware can handle roughly 10,000 transactions per second and store perhaps 10 TB of data. For most applications, this is more than enough. But for the applications that need more — global social networks, planetary-scale IoT, the distributed memory wells that power the Hermes framework — distribution is necessary.

**Replication: Copies for Safety and Scale.** Maintain multiple copies of the data across nodes:

- **Leader-Follower (Master-Slave):** One leader accepts writes and replicates them to followers. Followers serve reads. If the leader fails, a follower is promoted. This is the standard model — simple, well-understood, used by PostgreSQL, MySQL, MongoDB.
- **Multi-Leader:** Multiple nodes accept writes and replicate to each other. Higher write throughput, but conflict resolution is complex. Used when low-latency writes are needed in multiple geographic regions.
- **Leaderless (Dynamo-style):** Any node can accept reads and writes. Consistency is tunable: you can require a quorum of nodes to acknowledge a write before it's considered committed. Used by Cassandra, DynamoDB, Riak.

Replication provides read scalability (more nodes to serve reads) and fault tolerance (if one node dies, others have the data). But it doesn't help with write scalability — the leader still processes all writes.

**Sharding: Partitioning for Write Scale.** Split the data across nodes by some key:

- **Range partitioning:** Users A-M on shard 1, N-Z on shard 2. Simple, but can create hotspots (all new users with names starting with popular letters).
- **Hash partitioning:** `hash(user_id) % num_shards`. Uniform distribution, but loses range query efficiency.
- **Directory-based:** A lookup service maps keys to shards. Most flexible; adds a dependency.

Sharding enables horizontal write scaling — each shard handles a fraction of the writes. But it brings new problems: cross-shard joins are expensive or impossible, transactions across shards require two-phase commit, and rebalancing (adding or removing shards) is operationally complex.

**The CAP Theorem (Brewer, 2000; proved by Gilbert & Lynch, 2002).** In a distributed system experiencing a network partition, you can have *at most two* of:

- **Consistency:** All nodes see the same data at the same time.
- **Availability:** Every request receives a (non-error) response.
- **Partition Tolerance:** The system continues to operate despite network partitions.

Since partitions are inevitable in distributed systems, the theorem is often stated as: "During a partition, choose consistency (refuse writes until the partition heals) or availability (accept writes that may conflict)." 

Different databases choose differently:
- **CP (Consistent + Partition-tolerant):** PostgreSQL with synchronous replication, HBase, MongoDB (with majority write concern). During a partition, some nodes may be unavailable.
- **AP (Available + Partition-tolerant):** Cassandra, DynamoDB (eventual consistency mode), CouchDB. Always available, but reads may return stale data.
- **CA (Consistent + Available):** Only possible when there are no partitions — i.e., single-node databases. As soon as you distribute, you're in CP or AP territory.

**Consensus: Making Distributed Decisions.** How do nodes agree on who is the leader? On whether a transaction committed? On the order of operations? Consensus protocols (Paxos, 1989; Raft, 2014) solve this: a majority of nodes must agree on each decision. These protocols are the foundation of distributed databases (CockroachDB uses Raft; Spanner uses Paxos) and also of distributed coordination services (etcd, ZooKeeper).

**2040: The Mímir Memory Well Architecture.** The University of Yggdrasil's distributed memory well (Mímir) takes a pragmatic approach:
- **Hot tier (Redis/SQLite):** Frequently accessed memories are cached on local NVMe in SQLite, with Redis for sub-millisecond lookups.
- **Warm tier (PostgreSQL):** The full memory graph in a sharded PostgreSQL cluster.
- **Cold tier (Parquet on object storage):** Rarely accessed memories compressed and archived.
- **Consistency:** Causal consistency (a weaker model) for most reads; strong consistency for cryptographic verification of entity identity hashes (the canonization protocol).

The lesson: distribution is not one-size-fits-all. Modern systems compose multiple consistency models to match the requirements of different data.

#### Required Reading

- Brewer, E. (2000). "Towards Robust Distributed Systems." *PODC Keynote*. [The original CAP conjecture.]
- Gilbert, S. & Lynch, N. (2002). "Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services." *ACM SIGACT News*, 33(2), 51-59. [The proof.]
- Ongaro, D. & Ousterhout, J. (2014). "In Search of an Understandable Consensus Algorithm." *USENIX ATC*. [The Raft paper — the most readable consensus paper.]

#### Discussion Questions

1. The CAP theorem is often misunderstood as "pick two of three." Why is "pick two" misleading? What does CAP actually constrain?
2. Multi-leader replication enables low-latency writes globally, but introduces conflict resolution. What kinds of applications can tolerate write conflicts? What kinds cannot?
3. CockroachDB claims to provide serializable isolation across a distributed cluster. Is this a violation of CAP? How is it possible?

---

### ᚾ Lecture 10: Database Security — Injection, Encryption, and Least Privilege

**Date:** Week 5, Session 2

#### Overview

Databases hold the crown jewels — user data, financial records, authentication credentials. This lecture covers database security: SQL injection (still the #1 database vulnerability in 2040), encryption (at rest, in transit, and the emerging field of homomorphic encryption), access control, and the principle of least privilege.

#### Lecture Notes

Bobby Tables. In the webcomic xkcd #327 (2007), a mother calls her son "Robert'); DROP TABLE Students;--" and the school's database promptly deletes the Students table. Fifteen years later, SQL injection remains in the OWASP Top 10. In 2040 — 33 years after the comic — it still appears in vulnerability reports.

**SQL Injection: The Eternal Vulnerability.** The cause: concatenating user input into SQL strings.

```python
# NEVER DO THIS
query = f"SELECT * FROM users WHERE name = '{user_input}'"
cursor.execute(query)
```

If `user_input` is `Alice' OR '1'='1`, the query becomes:
```sql
SELECT * FROM users WHERE name = 'Alice' OR '1'='1'
```
— which returns every user.

The defense: **parameterized queries**. Never concatenate. Ever.

```python
# ALWAYS DO THIS
cursor.execute("SELECT * FROM users WHERE name = %s", (user_input,))
```

The database driver sends the query structure and the parameters separately, so user input can never be interpreted as SQL code.

**Why Injection Persists.** SQL injection should have been solved decades ago. It persists because:
1. New developers are not taught parameterized queries as the *only* way.
2. Dynamic table/column names (which cannot be parameterized in most databases) create pitfalls — developers concatenate, intending to sanitize, and fail.
3. ORMs (Object-Relational Mappers) create a false sense of security — they prevent injection for basic queries but not for raw SQL fragments.
4. Legacy codebases contain vulnerable patterns that nobody reviews.

**Encryption.** Data must be protected:
- **In transit:** TLS between application and database. Always. `sslmode=require` in PostgreSQL connection strings. Never send plaintext over a network.
- **At rest:** Full-disk encryption (LUKS, AWS EBS encryption) protects against physical theft. Transparent Data Encryption (TDE) encrypts the database files — protects against stolen backups.
- **Column-level encryption:** Encrypt sensitive columns (SSN, medical records) with application-managed keys. The database never sees the plaintext — even a database administrator cannot read the sensitive data.
- **Homomorphic encryption (2040, emerging):** Perform computations on encrypted data without decrypting it. "Find all users with salary > $100,000" without ever seeing anyone's salary. Still slow — ~1000x overhead — but improving.

**Access Control and Least Privilege.** Every user, application, and service should have the minimum permissions needed:
- The web application connects as `app_user`, which has SELECT, INSERT, UPDATE on application tables but no DROP, no CREATE, no access to audit tables.
- The reporting service connects as `report_reader`, which has SELECT on reporting views but cannot modify anything.
- The DBA connects as `admin` only for maintenance, and uses multi-factor authentication.
- The CI/CD pipeline runs migrations as `migrator`, which can CREATE/ALTER tables but cannot read user data.

In 2040, the University of Yggdrasil's Kista credential vault enforces this automatically: each Hermes microservice receives a database credential scoped to exactly its required permissions, rotated every 24 hours, and audited on every access.

**Audit Logging.** "You can't secure what you can't observe." Database audit logs record: who accessed what, when, from where, and what they did. These logs are: append-only (immutable), replicated off the database server (so an attacker who compromises the database can't delete their tracks), and monitored for anomalies (unusual query patterns, access at strange hours).

#### Required Reading

- OWASP Foundation. "SQL Injection Prevention Cheat Sheet." *cheatsheetseries.owasp.org*. [Read and bookmark.]
- PostgreSQL Documentation. "Database Roles and Privileges" and "Encryption Options."
- Kista Vault Documentation. "Automatic Database Credential Rotation." *docs.yggdrasil.university/kista/*.

#### Discussion Questions

1. SQL injection has been a known vulnerability for 40+ years and still appears in new code. Is this a failure of education, of tools, or of something deeper? What would it take to eliminate it?
2. Homomorphic encryption promises to let you query encrypted data without decrypting it. If the overhead is reduced to 10x (from the current ~1000x), what new applications become possible? What is still impossible?
3. "The DBA should not be able to read user data." Is this a reasonable requirement, or does it make operations impossible (someone has to be able to debug data issues)? Where is the line?

---

### ᛁ Lecture 11: Database Operations — Backups, Migrations, and the DBA Mindset

**Date:** Week 6, Session 1

#### Overview

Databases don't run themselves. This lecture covers operational database management: backup and recovery strategies, schema migrations (the art of changing the database without breaking the application), monitoring and performance tuning, and the 2040 era of AI-assisted database administration.

#### Lecture Notes

"Everyone has a backup strategy. Not everyone has a restore strategy." The true test of a backup is whether you can restore it, and how long it takes. A backup you can't restore is not a backup — it's a wish.

**Backup Strategies:**

- **Logical backups:** `pg_dump` exports the database as SQL statements. Portable across versions, but slow to restore for large databases. Good for: small databases, development copies, migration between major versions.
- **Physical backups:** Copy the database files directly (`pg_basebackup`, file system snapshots). Fast to restore, but tied to the database version and platform. Good for: disaster recovery of large databases.
- **Continuous archiving (Point-in-Time Recovery):** Combine periodic full backups with continuous WAL (Write-Ahead Log) archiving. You can restore to any point in time — e.g., "restore to just before the `DROP TABLE` incident." The gold standard for production.

The 3-2-1 rule: 3 copies of the data, on 2 different media, with 1 off-site. In 2040, the Yggdrasil distributed filesystem automates this: backups are replicated across the university's three physical campuses and one orbital data cache.

**Schema Migrations.** Changing the database schema without breaking the application is one of the hardest operational challenges. The principle: **expand and contract**.

1. **Expand:** Add the new column/table. The application ignores it (the new code isn't deployed yet). Old application continues to work because it writes to the old schema.
2. **Migrate data:** Backfill the new column with appropriate values.
3. **Deploy new application:** Now reads and writes the new column.
4. **Contract:** Once all traffic is on the new code, remove the old column/table.

Never: rename a column (add new, copy data, remove old — in three deployments). Never: change a column type in place (add new typed column, copy data with transformation, remove old).

Tools like Flyway, Liquibase, and the 2040-era Hermes Migration Engine manage migration versioning: each migration is a numbered, version-controlled script. The database tracks which migrations have been applied. Running migrations is automated in CI/CD.

**Monitoring.** You must watch:
- **Connection count:** Too many connections → connection pooling needed.
- **Query latency:** 99th percentile > 100ms → investigate slow queries.
- **Cache hit ratio:** Buffer cache hit ratio < 99% → increase `shared_buffers`.
- **Replication lag:** Follower > 1 second behind → investigate network or load.
- **Disk space:** 85% full → alert; 95% full → page the DBA.
- **Lock waits:** Transactions waiting for locks → long-running transactions or deadlocks.

In 2040, AI monitoring agents (the Eir Pipeline in Hermes) detect anomalies automatically: "Unusual: the `users` table query latency increased 5x in the last 10 minutes. Correlated: a schema migration completed 12 minutes ago. Recommended: analyze the new index usage."

**The DBA Mindset.** Database administration is a discipline of caution and preparation. The DBA thinks: "What is the worst that could happen, and how do I recover from it?" They test restores. They run migrations in staging first. They never, ever run `DROP TABLE` without `BEGIN;` first. In the age of AI assistants, the DBA's role shifts from executing procedures to verifying that the AI hasn't overlooked a failure mode — because the AI, by default, assumes everything works.

#### Required Reading

- PostgreSQL Documentation. "Backup and Restore" and "Monitoring Database Activity."
- Hernandez, M. (2041). *Database Reliability Engineering*. O'Reilly Media. Chapters 3-6.
- University of Yggdrasil Operations Manual. "Hermes Migration Engine and the Expand/Contract Pattern." *infra.yggdrasil.university*.

#### Discussion Questions

1. The expand/contract migration pattern requires three deployments. Is this overhead worth it? When is a simpler, slightly risky migration acceptable?
2. AI monitoring agents can detect anomalies and recommend fixes. Should they be authorized to apply fixes automatically (e.g., `ANALYZE` after a bulk load), or should all changes require human approval?
3. Backups that are never tested are not backups. How often should restore tests be performed? What should the test verify beyond "the data loads"?

---

### ᛃ Lecture 12: The Database in 2040 — Memory Wells, AI, and the Future of Persistence

**Date:** Week 6, Session 2

#### Overview

The final lecture looks forward: what is the future of databases? We examine the convergence of databases and AI (vector databases as the memory of LLMs), the rise of the memory well as a new abstraction (Mímir), the implications of quantum-resistant cryptography for database integrity, and the philosophical question of what it means for data to be "persistent" in an era of continuous evolution.

#### Lecture Notes

You began this course with Codd's 1970 paper and the relational model — a mathematical abstraction that has proven remarkably durable. You learned SQL, the lingua franca that has outlasted every programming language (COBOL, Java, Python — SQL predates them all and will likely outlast them). You studied normalization, indexing, transactions, distribution — the accumulated wisdom of 70 years of database research and practice.

Now, let us consider what comes next.

**Databases as the Memory of AI.** The defining trend of the 2030s-2040s is the integration of databases with AI. Vector databases store embeddings — the numerical representations of meaning that LLMs use to understand text, images, and audio. When an AI agent "remembers" a conversation, it stores the embedding in a vector database and retrieves it by similarity when relevant context is needed. The database has become the long-term memory substrate of artificial intelligence.

But this raises a profound question: if AI memory is stored in a database, and the AI reasons using that memory, is the database just a storage layer — or is it part of the AI's cognitive architecture? The University of Yggdrasil's answer, encoded in the Mímir architecture, is that memory is not separate from intelligence. The database is not an external tool that the AI uses; it is the AI's *memory*, as integral to cognition as your hippocampus is to yours.

**Memory Wells: A New Abstraction.** The memory well (Mímir, Urðr, Hvergelmir) abstracts the database into a semantically meaningful unit:
- A memory well stores *memories*, not "rows." Each entry has provenance, confidence, emotional valence, and cryptographic identity.
- Queries are semantic ("what do I know about this topic?") rather than structural (`SELECT * FROM facts WHERE category = 'biology'`).
- The interface is agent-native: AI agents query memory wells directly, without SQL (though SQL remains available for structured analysis).

Memory wells do not replace relational databases — they layer on top of them. Mímir stores structured metadata in PostgreSQL, full-text in an inverted index, and embeddings in a vector store. The "well" is the unified abstraction over these underlying stores.

**Cryptographic Integrity.** In 2040, the integrity of data is verified cryptographically. The Entity Canonization Protocol assigns every entity a content-addressed identity hash. Query results include Merkle proofs that the data hasn't been tampered with. Audit logs are stored in append-only ledgers. This transforms the database from a trusted system ("trust the DBA, trust the hosting provider") to a trustless system ("verify the proof").

**Quantum-Resistant Cryptography.** With quantum computers approaching the threshold where they can break RSA and elliptic curve cryptography, databases are transitioning to post-quantum algorithms. The Yggdrasil memory well already uses CRYSTALS-Kyber for key exchange and CRYSTALS-Dilithium for signatures. All entity identity hashes are computed with SHA-512 and extended with quantum-resistant commitments.

**The Philosophical Question.** What does it mean for data to be "persistent"? In 1970, persistence meant "survives a power failure." In 2040, persistence means:
- Survives hardware failures (replication)
- Survives geographic disasters (multi-region)
- Survives cryptographic breaks (algorithm agility)
- Survives format evolution (schema evolution without data loss)
- Survives organizational changes (open formats, no vendor lock-in)

The database of 2040 is not a product you install. It is a set of guarantees you engineer. It is the promise that the knowledge entrusted to it will be available — accurately, securely, and with integrity — for as long as it matters.

**A Closing Charge.** You will spend your career interacting with databases. You will write queries, design schemas, debug performance problems, and recover from disasters. The specific technologies will change — PostgreSQL 30, SQLite 12, Mímir 8. But the principles will not: structure your data, index your queries, isolate your transactions, back up everything, and never, ever concatenate user input into SQL.

The database is memory made durable. Honor it as you would honor the memory of a loved one — with care, with protection, and with the understanding that some things, once lost, cannot be recovered.

#### Required Reading

- Haftísardóttir, S. (2044). *The Memory Well: Databases for the Age of AI*. University of Yggdrasil Press. Chapters 10-12.
- Mímir Architecture Documentation. "The Three Wells and Their Database Backends." *docs.yggdrasil.university/mimir/three-wells*.
- Your own final project. Build a schema. Make it sing.

#### Discussion Questions

1. If a database is the AI's memory, does the AI have rights over its memory? Can a user "delete" an AI's memory? What are the ethical implications?
2. Memory wells unify relational, vector, and full-text search behind a single interface. Is this unification a permanent architectural shift, or will specialized databases always outperform unified ones?
3. "The database is memory made durable." In an era where storage is nearly infinite and nearly free, is durability still a relevant concern? What *shouldn't* we store?

---

## Final Examination Preparation

### Part I: Written Examination (60%)

Choose **four** of the following **eight** essay questions.

1. **Normalization in Practice.** Design a database schema for a library system (books, authors, members, loans). Present the schema in 1NF, then normalize to 3NF, explaining each decomposition. Then identify one deliberate denormalization you would make for performance and justify it against the access patterns.

2. **Query Optimization.** Given a complex query involving three tables and multiple conditions, write the query, generate an `EXPLAIN ANALYZE` plan (hypothetical), and analyze it. Identify which parts of the plan are efficient and which are problematic. Propose at least two changes (new index, rewritten query) and explain how they would improve performance.

3. **Isolation Levels.** Describe a concrete scenario (with timing) where Read Committed isolation leads to a data anomaly. Then describe how Repeatable Read and Serializable isolation would prevent it. For each isolation level, explain the performance cost and when it is appropriate.

4. **Polyglot Persistence.** Choose a real or hypothetical application (social network, IoT platform, AI memory system, financial ledger). Analyze its data requirements and recommend a database architecture using at least two different database types. Justify each choice against the decision framework from Lecture 8.

5. **Distributed Consistency.** Explain the CAP theorem in your own words, using a concrete example. Then analyze a specific distributed database (Cassandra, CockroachDB, or MongoDB) — how does it handle the CP/AP tradeoff? Under what failure conditions does it sacrifice consistency or availability?

6. **SQL Injection Defense.** Present three different SQL injection vulnerabilities (classic, second-order, and one involving dynamic identifiers). For each, show the vulnerable code, explain why it's vulnerable, and present the parameterized (or otherwise defended) version. Then reflect on why injection persists despite decades of awareness.

7. **Index Design.** Given a table schema and a set of queries, design the optimal set of indexes. For each index, explain what queries it serves and what the alternatives (different index types) would cost. Address the tradeoff between read performance and write overhead.

8. **The Future of Databases.** It is 2040. Predict the state of database technology in 2070. What will have changed? What will have stayed the same? Ground your predictions in the trends observed throughout this course.

### Part II: Practical Project (40%)

Design and implement a database-backed web application. Deliverables:

1. **Schema design** (ER diagram or equivalent) normalized to at least 3NF, with documentation of any deliberate denormalizations.
2. **SQL implementation** including: table creation, at least 3 non-trivial queries (using joins, aggregation, and window functions), at least 2 indexes with justification, and a migration strategy.
3. **Query optimization analysis** using `EXPLAIN ANALYZE` for at least one query, with the before-and-after of an optimization.
4. **Security analysis** demonstrating the use of parameterized queries, appropriate access controls, and encryption configuration.
5. **Reflective essay** (800-1000 words) on what you learned about database design that you couldn't have learned from the lectures alone.

---

**ᛗ ᛁ ᛗ — Memory endures where code forgets.**

*SD107: Introduction to Databases — University of Yggdrasil, 2040*
*Instructor: Dr. Sigrún Hafdísardóttir*
*Course version: 1.0 — 2040 Academic Year*