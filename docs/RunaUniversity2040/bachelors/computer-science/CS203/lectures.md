# CS203: Database Systems
## Bachelor of Science in Computer Science — University of Yggdrasil, 2040

**Credits:** 4
**Prerequisites:** CS101 — Computational Thinking; CS103 — Data Structures & Algorithms I
**Description:** The database is the memory of civilisation. Every transaction, every medical record, every social media post, every scientific observation — the data that constitutes the modern world resides in databases, and the systems that store, query, and manage that data are among the most sophisticated artefacts of software engineering. This course covers the full stack of database technology: the relational model and relational algebra; SQL as a declarative query language; database design through normalisation and entity-relationship modelling; transaction processing and concurrency control (ACID); query optimisation and indexing; and the post-relational landscape of the 2040s — NoSQL stores, distributed databases, vector databases for AI embeddings, and the emerging convergence of databases and machine learning. Students design and query relational databases in PostgreSQL, explore document and graph databases, build a simple query optimiser, and complete a term project that designs a database for a real-world application. The course is animated by a conviction that databases are not merely storage engines but **logical systems** — that the design of a database schema is an act of philosophy, a commitment to a particular ontology of the world that shapes every query that follows.

---

## Lecture 1: The Relational Model — Tuples, Relations, and the Algebra of Data

The relational model, proposed by E.F. Codd in his landmark 1970 paper "A Relational Model of Data for Large Shared Data Banks," is the most successful abstraction in the history of data management. It rests on a simple, mathematically crisp idea: all data can be represented as **relations** — sets of tuples, each tuple being a mapping from attribute names to values. A relation is a **set** (no duplicate tuples, no ordering of tuples), and the attributes are drawn from **domains** (data types: integers, strings, dates, etc.). The relational model is not a physical storage scheme — it is a **logical model**, independent of how the data is stored on disk. This separation of logical and physical is the model's great innovation: the user (or application) queries the logical relations, and the database system determines how to execute the query efficiently using the physical structures (indexes, page layouts, buffer pools).

The **relational algebra** is the formal language of the relational model — a set of operations on relations that produce new relations. The core operations are: **selection (σ)** — filter tuples by a predicate (σ_{age > 30}(Person) — all persons older than 30); **projection (π)** — select a subset of columns (π_{name, age}(Person)); **union (∪), intersection (∩), and difference (−)** — the set operations, applied to relations with identical schemas; **Cartesian product (×)** — combine every tuple of relation R with every tuple of relation S; and **join (⨝)** — the most powerful operation: combine tuples from two relations when they agree on a common attribute. The natural join (R ⨝ S) is the Cartesian product followed by selection (on equality of common attributes) followed by projection (to eliminate duplicate columns). Joins are the heart of relational querying — they are what allow us to connect data across tables and extract complex, multi-table answers.

The relational algebra is **procedural** (it specifies *how* to compute the result), but it is the foundation for **declarative** query languages (which specify *what* result is desired). SQL — the Structured Query Language, standardised by ANSI and ISO since 1986 — is the dominant declarative query language, and it is (loosely) based on the relational calculus, which is equivalent in expressive power to the relational algebra (Codd's theorem). A SQL query — `SELECT name FROM Person WHERE age > 30` — is translated by the query optimiser into a relational-algebra expression, which is then translated into a physical execution plan.

The **theoretical foundations** of the relational model extend beyond the algebra. **Functional dependencies** (X → Y: if two tuples agree on X, they must agree on Y) are the basis of database design and normalisation (Lecture 4). **Multivalued dependencies** and **join dependencies** extend the theory. And the **relational calculus** — the logical formulation of queries in first-order logic — connects databases to the broader tradition of formal logic. Codd's genius was to see that data management could be grounded in logic rather than in the idiosyncrasies of physical storage — and the rest of the database field has been an extended exploration of that insight.

**Required Reading:**
- E.F. Codd, "A Relational Model of Data for Large Shared Data Banks," *Communications of the ACM* 13:6 (1970): 377–387
- C.J. Date, *An Introduction to Database Systems* (8th ed., 2003/2039), chs. 1–6
- Abraham Silberschatz, Henry F. Korth & S. Sudarshan, *Database System Concepts* (7th ed., 2039), chs. 1–2
- H. Garcia-Molina, Jeffrey D. Ullman & Jennifer Widom, *Database Systems: The Complete Book* (2nd ed., 2008/2038), chs. 2, 5

**Discussion Questions:**
1. The relational model represents everything as sets — no duplicates, no ordering. Why are duplicates and ordering so important in practice (consider SQL's `ORDER BY` and the allowance of duplicate rows), and what does this tension between theory and practice reveal?
2. Codd's relational model separates logical and physical. Is this separation always desirable — or are there situations where the physical structure *should* influence the logical model (e.g., for performance-critical applications)?
3. The relational algebra has five primitive operations. Are all five necessary — or can some be expressed in terms of others? Which is the minimal set of operations that is relationally complete?

---

## Lecture 2: SQL — The Language of Data, from SELECT to Window Functions

SQL is the lingua franca of data — the most widely used declarative language in computing, spoken (with dialectal variations) by every database system from embedded SQLite to distributed Google Spanner. SQL is simultaneously simple (a novice can write `SELECT * FROM users WHERE name = 'Alice'` in minutes) and deep (an expert can write a query spanning fifty lines with common table expressions, window functions, recursive queries, and lateral joins). This lecture surveys SQL from foundations to advanced features, with an emphasis on the **declarative mindset**: the SQL programmer describes the desired result, not the algorithm to produce it.

The **core SQL structure** — `SELECT … FROM … WHERE … GROUP BY … HAVING … ORDER BY` — is a pipeline of logical operations, evaluated in a specific conceptual order (not necessarily the physical execution order). **FROM** identifies the source tables and performs joins; **WHERE** filters rows based on a predicate; **GROUP BY** partitions rows into groups; **HAVING** filters groups (after aggregation); **SELECT** computes the output columns (including aggregate functions: COUNT, SUM, AVG, MIN, MAX); **ORDER BY** sorts the result. The conceptual order matters: you cannot filter on an aggregate in the WHERE clause (the aggregates haven't been computed yet) — that goes in HAVING.

**Joins** are the soul of SQL, and their syntax has evolved. The **explicit JOIN** syntax (`A INNER JOIN B ON A.id = B.a_id`) is clearer than the implicit join (`FROM A, B WHERE A.id = B.a_id`) and is the standard in 2040. **LEFT JOIN** preserves all rows from the left table, filling unmatched rows with NULLs — essential for reporting ("show all customers and their orders, including customers with no orders"). **RIGHT JOIN** is the mirror; **FULL OUTER JOIN** preserves both sides. **CROSS JOIN** is the Cartesian product — useful when combined with a WHERE filter, but dangerous on large tables. **SELF JOIN** — joining a table with itself — is the standard technique for hierarchical data (employee-manager) or comparing rows within the same table.

**Advanced SQL** features have transformed from esoterica to everyday tools. **Common Table Expressions (CTEs)** — `WITH` clauses — allow the programmer to name intermediate results and compose complex queries from simpler parts, improving readability and (sometimes) performance. **Recursive CTEs** — `WITH RECURSIVE` — enable queries on hierarchical or graph-structured data (the org chart, the bill of materials, the social network's transitive closure) in pure SQL. **Window functions** — `ROW_NUMBER(), RANK(), LAG(), LEAD(), SUM() OVER (PARTITION BY … ORDER BY …)` — compute values across a "window" of rows related to the current row, without collapsing the rows into groups. Window functions have revolutionised SQL analytics: "give me each employee's salary and the average salary in their department" is a single window-function query, where previously it required a subquery or a join.

The **NULL problem** is SQL's most persistent philosophical difficulty. NULL is not a value — it is a marker for "unknown" or "inapplicable." NULL violates the relational model's foundations (Codd's relations contain no NULLs), but it is indispensible in practice (every real database has missing data). NULL propagates through expressions (`age + 1` is NULL if age is NULL), and NULL comparisons use three-valued logic (TRUE, FALSE, UNKNOWN), which requires special handling (`IS NULL` rather than `= NULL`). The NULL problem is a reminder that practical systems always deviate from theoretical purity — and that the database designer's task is to manage that deviation gracefully.

**Required Reading:**
- Don Chamberlin, *A Complete Guide to DB2 Universal Database* (1998), chs. on SQL history and design
- Chris J. Date, *SQL and Relational Theory: How to Write Accurate SQL Code* (3rd ed., 2039), chs. 1–5
- Markus Winand, *SQL Performance Explained* (2012/2038), chs. 1–3
- PostgreSQL Documentation, Part II: The SQL Language (PostgreSQL 32, 2040)
- The Yggdrasil SQL Sandbox (2040)

**Discussion Questions:**
1. SQL is declarative — you specify *what*, not *how*. But the query optimiser can produce a bad plan, and the programmer may need to "trick" the optimiser with hints or rewrites. Does this compromise the declarative ideal — and is there a better way?
2. NULLs violate the relational model yet are indispensible. What alternatives to NULL have been proposed (e.g., default values, special marker tables, option types), and why has NULL survived?
3. Window functions are powerful but can be confusing. When is a window function the right tool, and when is it an overcomplication that would be better expressed as a subquery or a CTE?

---

## Lecture 3: Database Design — Entity-Relationship Modelling and the Art of Conceptual Structure

Before a database schema is written in SQL, it must be designed in thought. **Database design** is the process of translating a domain — a library, a hospital, an e-commerce platform, a social network — into a set of tables, columns, relationships, and constraints that faithfully and efficiently represent the domain. Good design minimises redundancy, prevents anomalies, and makes queries natural (the database structure mirrors the structure of the domain). Bad design leads to update anomalies (changing a fact requires updating multiple rows, and missing one leaves the database inconsistent), insertion anomalies (you can't record a fact without also recording an unrelated fact), and deletion anomalies (removing a fact accidentally removes other facts). Database design is not a mechanical process; it is an act of conceptual modelling — and the entity-relationship model is the sketchpad.

The **Entity-Relationship (ER) model**, introduced by Peter Chen in 1976, is the standard tool for conceptual database design. The ER model represents the domain as **entities** (things that exist independently: a student, a course, a department) and **relationships** (associations among entities: a student *enrols in* a course, a course *is offered by* a department). Entities have **attributes** (name, date of birth, credit hours). Relationships have **cardinality**: one-to-one (a person has one passport; a passport belongs to one person), one-to-many (a department has many courses; a course belongs to one department), many-to-many (a student takes many courses; a course has many students). The ER diagram — boxes for entities, diamonds for relationships, ovals for attributes, lines connecting them — is a visual language for the domain ontology.

The **translation from ER to relational** follows systematic rules. Each entity becomes a table; its attributes become columns; its primary key is chosen. Each many-to-many relationship becomes a table of its own, with foreign keys referencing the participating entities. One-to-many relationships are typically folded into the "many" table as a foreign key. One-to-one relationships can be folded into either table, or into a separate table. The translation is algorithmic — and it is the algorithm that the Yggdrasil ER-to-SQL tool implements, translating diagrams to DDL with a single click — but the quality of the resulting schema depends entirely on the quality of the ER model. Garbage in, garbage in tidy tables.

The **design process** is iterative. Begin by identifying the entity types — the nouns of the domain. What are the things that the system needs to track? In a library: Book, Patron, Loan, Author. Identify the attributes of each entity. Identify the relationships. Draw the ER diagram. Test it against scenarios: "Can I record that a patron checked out a book on a specific date?" "Can I find all books by a given author?" "Can I record that a book has multiple authors?" Revise. Repeat. The process is not water-fall but spiral — each iteration tightens the model and reveals gaps. The designer who skips the ER modelling stage and goes straight to SQL will create a schema that works for the first few queries and then collapses under the weight of the unanticipated ones.

**Required Reading:**
- Peter Pin-Shan Chen, "The Entity-Relationship Model — Toward a Unified View of Data," *ACM Transactions on Database Systems* 1:1 (1976): 9–36
- C.J. Date, *An Introduction to Database Systems* (8th ed., 2003/2039), chs. 13–14
- Toby J. Teorey, Sam S. Lightstone, Tom Nadeau & H.V. Jagadish, *Database Modeling and Design: Logical Design* (5th ed., 2011/2038), chs. 1–4
- The Yggdrasil ER-to-SQL Tool Documentation (2040)

**Discussion Questions:**
1. The ER model is conceptual — but the relational schema is what gets implemented. Where does the ER model fall short — what aspects of a good database design cannot be captured in an ER diagram?
2. Many-to-many relationships become join tables. Is this always the right translation — or are there cases where an array column (PostgreSQL arrays) or a JSON column is a better representation?
3. The ER model was introduced in 1976. How has the rise of NoSQL — document stores, graph databases — changed the practice of conceptual modelling, and does the ER model still apply?

---

## Lecture 4: Normalisation — Functional Dependencies and the Elimination of Redundancy

**Normalisation** is the systematic process of refining a database schema to eliminate redundancy and prevent the anomalies it causes. It is grounded in the theory of **functional dependencies (FDs)**: if X → Y (read "X determines Y"), then for any two tuples that agree on the attributes X, they must also agree on the attributes Y. For example, in a university database: `student_id → student_name` (a given student ID determines a unique student name), and `course_id → department` (a given course belongs to exactly one department). FDs are statements about the domain, not about the current data — they are constraints that must hold in every possible instance of the database.

The **normal forms** are a hierarchy of schema quality, each defined by the FDs it satisfies. **First Normal Form (1NF):** all attributes are atomic — no repeating groups, no arrays, no nested relations. A table that stores multiple phone numbers in a single column (as a comma-separated list) violates 1NF. **Second Normal Form (2NF):** 1NF + every non-key attribute is fully functionally dependent on the *entire* primary key (no partial dependencies). A table with composite key (student_id, course_id) and attribute course_name — which depends only on course_id, not on the full key — violates 2NF. **Third Normal Form (3NF):** 2NF + no transitive dependencies — a non-key attribute should not depend on another non-key attribute. A table with columns (employee_id, department_id, department_name) has a transitive dependency: employee_id → department_id → department_name; department_name should be in the Department table, not the Employee table.

**Boyce-Codd Normal Form (BCNF)** is a stricter version of 3NF that handles cases where there are multiple candidate keys with overlapping attributes. A schema is in BCNF if, for every non-trivial FD X → Y, X is a superkey. BCNF is the practical target for most well-designed databases — it eliminates the vast majority of anomalies — though there are edge cases where achieving BCNF requires splitting a table in a way that loses a dependency that should be preserved. The theory of **dependency preservation** and **lossless join decomposition** provides the tools for navigating these edge cases.

The **normalisation process** is a decomposition: start with a "universal relation" containing all attributes, and iteratively split it based on FDs that violate the desired normal form. Each split must be **lossless** — the original relation can be reconstructed by joining the decomposed relations (guaranteed if the split is along an FD X → Y and we create one relation with X ∪ Y and another with X ∪ (R − Y)). The process continues until the schema reaches BCNF (or 3NF, if dependency preservation is required). The result is a schema with minimal redundancy — but also, potentially, many small tables, which can make queries complex (many joins). The decision of *how far* to normalise is a design trade-off: denormalisation (deliberately introducing redundancy) can improve query performance at the cost of update complexity — and the database designer must weigh these costs against the application's query and update patterns.

**Required Reading:**
- E.F. Codd, "Further Normalization of the Data Base Relational Model," in *Data Base Systems* (1972): 33–64
- C.J. Date, *An Introduction to Database Systems* (8th ed., 2003/2039), chs. 11–12
- William Kent, "A Simple Guide to Five Normal Forms in Relational Database Theory," *Communications of the ACM* 26:2 (1983): 120–125
- H. Garcia-Molina, Jeffrey D. Ullman & Jennifer Widom, *Database Systems: The Complete Book* (2nd ed., 2008/2038), ch. 3

**Discussion Questions:**
1. BCNF eliminates more anomalies than 3NF but does not guarantee dependency preservation. When should the designer choose 3NF over BCNF — and is this a common enough situation to matter in practice?
2. Normalisation reduces redundancy — but it also increases the number of tables and the number of joins. At what point (the "denormalisation threshold") does the query-performance cost of normalisation outweigh the update-consistency benefit?
3. The normal forms were developed in the 1970s, when storage was expensive and redundancy was primarily a concern of wasted space. In the 2040s, storage is cheap, and redundancy is primarily a concern of consistency. How has this shift changed the practice of normalisation?

---

## Lecture 5: Storage and Indexing — B-Trees, Hash Indexes, and the Physical Layer

The relational model is logical; the database must be physical. The **storage manager** is the subsystem that maps the logical abstraction (tables, rows, columns) onto the physical medium (pages on disk, or in the 2040s, pages in persistent memory). The storage manager's design determines the database's performance at the most fundamental level: how quickly a row can be found by its primary key, how efficiently a full table scan can be performed, how much I/O a query requires. This lecture descends from the logical to the physical: how data is laid out on disk (or in persistent memory), and how **indexes** — auxiliary data structures — accelerate access.

The **page** is the unit of I/O — typically 4KB or 8KB, aligned with the OS's page size and the disk's sector size. A table is stored as a collection of pages, each containing a set of rows (or, for wide rows, a portion of a row). The pages are linked — in a **heap file**, pages are linked in a list or tracked in a page directory; in an **index-organised table** (IOT), rows are stored in the leaf pages of the primary-key index. The storage manager maintains a **buffer pool** — a cache of pages in memory — and a **page-replacement policy** (clock, LRU, 2Q) to manage it. A well-tuned buffer pool can absorb 99% of reads, making the database's performance nearly independent of the disk's speed (for reads, at least).

**Indexes** are auxiliary data structures that map key values to the locations of rows with those values. An index can be **clustered** (the rows are physically stored in the order of the index — typically the primary key index) or **non-clustered** (the index stores key values and row pointers, and the rows are stored elsewhere). A table can have at most one clustered index (the physical ordering) but many non-clustered indexes.

The **B-tree** — actually, the B+ tree, in which all key-pointer pairs are stored in the leaves, and the internal nodes serve only as a directory — is the dominant index structure in relational databases. A B+ tree of order m has the properties: (1) every internal node has between ⌈m/2⌉ and m children, (2) all leaves are at the same depth, (3) the leaves are linked in a doubly-linked list, enabling efficient range scans. The B+ tree supports point queries (find the row with key = K) in O(logₘ n) I/Os, and range queries (find all rows with key between K₁ and K₂) in O(logₘ n + (number of results)/B) I/Os — the logarithmic search to the first matching leaf, then a sequential scan along the leaf list. The B+ tree is self-balancing and adapts to insertions and deletions by splitting and merging nodes — algorithms that are a marvel of systems engineering, keeping the tree balanced and the pages at least half-full without excessive reorganisation.

**Hash indexes** provide O(1) point-query performance but cannot support range queries. They are implemented as **extendible hashing** (a directory of hash buckets that doubles as buckets overflow) or **linear hashing** (buckets are split one at a time, in order). Hash indexes are ideal for workloads dominated by point lookups (e.g., session stores, URL caches), but they are secondary to B-trees in most relational databases.

**2040 indexing** innovations include **learned indexes** (Kraska et al., 2018/2039): instead of a B-tree, a small neural network learns the cumulative distribution function (CDF) of the keys, and the index lookup is a model inference — tens of nanoseconds rather than hundreds of nanoseconds for a B-tree traversal, with a small space overhead for the model. Learned indexes are an active area of research and deployment in the 2040s, with the Yggdrasil Learned Index Engine (LIE) supporting experimental deployments.

**Required Reading:**
- H. Garcia-Molina, Jeffrey D. Ullman & Jennifer Widom, *Database Systems: The Complete Book* (2nd ed., 2008/2038), chs. 13–15
- Douglas Comer, "The Ubiquitous B-Tree," *ACM Computing Surveys* 11:2 (1979): 121–137
- Tim Kraska, Alex Beutel, Ed H. Chi, Jeffrey Dean & Neoklis Polyzotis, "The Case for Learned Index Structures," *SIGMOD* (2018): 489–504
- The Yggdrasil Learned Index Engine Documentation (2040)

**Discussion Questions:**
1. The B+ tree is balanced and logarithmic — but the constant factors matter. How many I/Os does it take to find a row in a table of 1 billion rows, with a B+ tree of order 200 and a page size of 8KB — and how does the buffer pool affect this?
2. A learned index replaces the B-tree with a neural network. What are the failure modes — and in what situations (skewed distributions, updates, range queries) does the learned index underperform the B-tree?
3. Why can a table have at most one clustered index — and what are the consequences of choosing the "wrong" column for clustering?

---

## Lecture 6: Query Optimisation — From Declarative to Procedural, Cost-Based Execution

When a user issues a SQL query, the database must decide how to execute it. The query optimiser — the most intellectually sophisticated component of a relational DBMS — translates the declarative query into a procedural **execution plan**: a tree of physical operators (table scans, index scans, hash joins, merge joins, sorts, aggregations) with estimated costs, and it chooses the plan with the lowest estimated cost. The difference between a good plan and a bad plan can be the difference between a query that returns in milliseconds and one that runs for hours — and the optimiser's ability to find good plans automatically, without programmer intervention, is what makes the declarative SQL model work.

The **optimisation pipeline** begins with **parsing and semantic analysis**: the SQL is parsed into an abstract syntax tree, and the database catalog is consulted to resolve names and check types. The result is a **logical query plan** — an expression in extended relational algebra. The optimiser then applies **heuristic transformations** — rules that are always (or almost always) beneficial: push selections down the tree (filter as early as possible to reduce the size of intermediate results); push projections down (eliminate unnecessary columns early); replace Cartesian products with joins when a join condition is present; reorder joins to minimise the sizes of intermediate relations.

The **cost-based optimisation** phase enumerates alternative physical plans for the transformed logical plan. For each logical operation (join, selection, aggregation), there are multiple physical operators: for selection, table scan vs. index scan; for join, nested-loop join vs. hash join vs. merge join. The optimiser uses **cost formulas** — functions of the sizes of the input relations, the available indexes, the buffer-pool size, and the I/O and CPU costs per operation — to estimate the cost of each candidate plan. The **statistics** in the catalog — the number of rows in each table, the number of distinct values in each column (cardinality), the distribution of values (histograms) — are the raw material of cost estimation. Good statistics are essential: the optimiser can only make good decisions if its estimates of intermediate result sizes are accurate.

The **join ordering** problem is the optimiser's central challenge. For a query joining n tables, there are (2n−2)! / ((n−1)!) possible join orders — too many to enumerate for n > 10 or so. The standard approach is **dynamic programming** (the Selinger-style optimiser, from System R, 1979): build optimal plans for subsets of tables, from smallest to largest, and at each step, consider all ways to join a new table to the optimal plan for the subset. The DP approach works well for up to ~15 tables; beyond that, heuristics (greedy join ordering, genetic algorithms) are used.

**2040 optimiser** research explores **learned query optimisation**: instead of hand-tuned cost formulas, a neural network trained on actual query executions predicts the cost of candidate plans, adapting to the specific hardware and data distribution. The Yggdrasil Optimiser Lab allows students to compare the classic cost-based optimiser with a learned optimiser on a benchmark of queries and observe the trade-offs — accuracy, robustness, and overhead.

**Required Reading:**
- Patricia G. Selinger, Morton M. Astrahan, Donald D. Chamberlin, Raymond A. Lorie & Thomas G. Price, "Access Path Selection in a Relational Database Management System," *SIGMOD* (1979): 23–34
- Surajit Chaudhuri, "An Overview of Query Optimization in Relational Systems," *PODS* (1998): 34–43
- H. Garcia-Molina, Jeffrey D. Ullman & Jennifer Widom, *Database Systems: The Complete Book* (2nd ed., 2008/2038), ch. 16
- Ryan Marcus & Olga Papaemmanouil, "Deep Learning for Query Optimization," *CIDR* (2019/2040)
- The Yggdrasil Optimiser Lab Documentation (2040)

**Discussion Questions:**
1. The Selinger optimiser uses dynamic programming to search the space of join orders. What is the complexity — and why is it tractable for 15 tables but not for 50? What do commercial systems do for queries with many joins?
2. The cost formulas depend on statistics (row counts, cardinalities, histograms). What happens when the statistics are stale — and how do modern systems keep them current without excessive overhead?
3. Learned query optimisation replaces analytical cost formulas with a learned model. What are the risks — and in what situations might the learned optimiser produce catastrophic plans that the analytical optimiser would avoid?

---

## Lecture 7: Transaction Management — ACID, Concurrency, and the Two-Phase Lock

A **transaction** is a sequence of database operations that form a single logical unit of work — transferring money between accounts, booking a flight, updating an inventory. The transaction concept, introduced by Jim Gray in the 1970s, is one of the great software abstractions: it guarantees that the database moves from one consistent state to another, despite concurrency (multiple transactions executing simultaneously) and despite failures (system crashes, power loss, disk errors). The guarantees are summarised by the **ACID** acronym.

**Atomicity:** a transaction is all-or-nothing. If any operation in the transaction fails, the entire transaction is **rolled back** — all its effects are undone, and the database is left as if the transaction had never begun. The implementation relies on **logging**: before modifying a page, the transaction writes a log record describing the old value (for undo) and the new value (for redo). If the transaction aborts, the undo log records are used to reverse its changes (the **rollback**). If the system crashes, the log is replayed during recovery to undo incomplete transactions and redo committed ones (the **ARIES** algorithm).

**Consistency:** a transaction, when executed alone on a consistent database, leaves the database consistent. Consistency is partly the responsibility of the DBMS (enforcing integrity constraints — primary keys, foreign keys, CHECK constraints) and partly the responsibility of the application programmer (the transfer transaction must ensure that the sum of the two account balances is unchanged).

**Isolation:** concurrent transactions should not interfere with each other. The gold standard is **serialisability** — the execution of concurrent transactions is equivalent to some serial execution (one at a time). The implications of weaker isolation levels will be explored in Lecture 8.

**Durability:** once a transaction commits, its effects are permanent — they survive system crashes and media failures. Durability is achieved by writing the transaction's log records to stable storage (disk, or persistent memory) before the commit is acknowledged (the **write-ahead log** protocol).

**Concurrency control** ensures isolation. The dominant mechanism is **two-phase locking (2PL)** : (1) a transaction must acquire a **shared lock** (S) before reading an object, and an **exclusive lock** (X) before writing; (2) a transaction may not acquire any locks after it has released its first lock (the "two-phase" rule). Strict 2PL (S2PL) — release all locks only at commit — is the variant used in practice, because it avoids **cascading aborts** (if T1 writes and T2 reads T1's uncommitted write, and T1 aborts, T2 must also abort — cascade). 2PL guarantees serialisability, but it can cause **deadlocks**: T1 holds an S-lock on A and wants an X-lock on B; T2 holds an S-lock on B and wants an X-lock on A — each waits for the other, and no progress is made. Deadlocks are handled by **detection** (building a waits-for graph and looking for cycles) or **prevention** (e.g., the wound-wait scheme: an older transaction that wants a lock held by a younger transaction "wounds" — aborts — the younger one).

**Required Reading:**
- Jim Gray & Andreas Reuter, *Transaction Processing: Concepts and Techniques* (1993/2038), chs. 1–4
- H. Garcia-Molina, Jeffrey D. Ullman & Jennifer Widom, *Database Systems: The Complete Book* (2nd ed., 2008/2038), chs. 18–19
- C. Mohan, Don Haderle, Bruce Lindsay, Hamid Pirahesh & Peter Schwarz, "ARIES: A Transaction Recovery Method Supporting Fine-Granularity Locking and Partial Rollbacks Using Write-Ahead Logging," *ACM TODS* 17:1 (1992): 94–162
- The Yggdrasil Transaction Lab (2040)

**Discussion Questions:**
1. 2PL guarantees serialisability, but it can cause deadlocks. How does snapshot isolation (used by Oracle and PostgreSQL) avoid locking — and what anomalies does it allow that serialisability would prevent?
2. The ARIES recovery algorithm uses a write-ahead log. Why must the log be written *before* the data pages — and what would happen if the order were reversed?
3. Atomicity and durability are achieved by logging; consistency is achieved by constraints. What is the relationship between the isolation level and the application's consistency guarantees — and can a weak isolation level be compensated for by careful application design?

---

## Lecture 8: Isolation Levels and Snapshot Isolation — The Spectrum of Consistency

Serialisability is the gold standard for isolation, but it is expensive — 2PL reduces concurrency, and deadlocks waste work. In practice, most databases offer a menu of **isolation levels** — each weaker than serialisability, each allowing certain anomalies, each offering higher concurrency. The isolation levels are defined by the anomalies they prevent, and the choice of level is one of the most consequential decisions in database application design.

The **SQL standard** defines four isolation levels, characterised by the phenomena they prevent. **READ UNCOMMITTED:** a transaction may read uncommitted (dirty) data from another transaction — "dirty read." Almost never appropriate. **READ COMMITTED:** a transaction sees only committed data — no dirty reads — but may see different values for the same row if another transaction updates it between reads ("non-repeatable read"). READ COMMITTED is the default in PostgreSQL and many systems. **REPEATABLE READ:** a transaction that reads the same row twice sees the same values — no non-repeatable reads — but may see new rows inserted by another transaction ("phantom read"). **SERIALISABLE:** no anomalies — concurrent execution is equivalent to some serial execution.

**Snapshot isolation (SI)** — used by Oracle (since 1986) and by PostgreSQL (since version 9.1, as "SERIALIZABLE" via SSI) — is a popular alternative to lock-based isolation. Under SI, each transaction reads from a **snapshot** of the database as it existed at the start of the transaction (or at the start of the first statement, depending on the variant). A transaction never sees uncommitted data, and it never blocks on reads (there are no read locks). Writes are checked for **write-write conflicts**: if T1 and T2 both attempt to modify the same row, the second to commit is aborted (the "first-committer-wins" rule). SI avoids the common anomalies of lock-based systems but allows **write skew**: T1 reads X and writes Y; T2 reads Y and writes X; under SI, both can commit because they modify different rows — but the result may violate a global constraint (X + Y should be constant; after both commit, X + Y has changed by the sum of the two deltas — a violation).

**Serializable Snapshot Isolation (SSI)** — introduced by Cahill et al. (2008) and implemented in PostgreSQL 9.1 — enhances SI to guarantee serialisability by detecting the "dangerous structure" of read-write dependencies that could lead to anomalies (the "pivot" pattern), and aborting one of the transactions involved. SSI has been the standard in PostgreSQL for serialisable transactions since 2012, and it provides full serialisability without the overhead and deadlock risks of 2PL.

The **2040 landscape** of isolation is shaped by the needs of **distributed transactions** (where the cost of 2PL across network boundaries is prohibitive) and **globally distributed databases** (Google Spanner, CockroachDB, the Yggdrasil Global DB) that use **strict serialisability** — serialisability combined with a real-time ordering constraint — implemented via atomic clocks (TrueTime in Spanner) or hybrid logical clocks.

**Required Reading:**
- Hal Berenson, Phil Bernstein, Jim Gray, Jim Melton, Elizabeth O'Neil & Patrick O'Neil, "A Critique of ANSI SQL Isolation Levels," *SIGMOD* (1995): 1–10
- Michael J. Cahill, Uwe Röhm & Alan D. Fekete, "Serializable Isolation for Snapshot Databases," *SIGMOD* (2008): 729–738
- Alan Fekete, Dimitrios Liarokapis, Elizabeth O'Neil, Patrick O'Neil & Dennis Shasha, "Making Snapshot Isolation Serializable," *ACM TODS* 30:2 (2005): 492–528
- The Yggdrasil Isolation Lab (2040)

**Discussion Questions:**
1. READ COMMITTED is the default in PostgreSQL and many other systems. Is this a reasonable default — or does it encourage developers to ignore the anomalies it allows, leading to subtle bugs?
2. Write skew is the classic SI anomaly. Can you construct a realistic example (beyond the textbook X + Y constraint) where write skew would cause a serious application error?
3. SSI detects "dangerous structures" of read-write dependencies. What is the overhead of this detection — and in what workloads does it cause many transaction aborts, negating the concurrency benefits of SI?

---

## Lecture 9: The NoSQL Movement — Document Stores, Key-Value Stores, and Graph Databases

In the late 2000s, a loosely organised movement — "NoSQL" (originally "Not Only SQL") — challenged the relational monopoly. The motivations were several: the relational model's rigid schemas made it difficult to accommodate semi-structured data (JSON, XML) and rapid iteration; the transactional guarantees (ACID) imposed overhead that was unnecessary for many web-scale applications (where "eventual consistency" was acceptable); and horizontal scaling (sharding) in relational databases was difficult and expensive, while the new distributed stores — designed from the start for scale-out on commodity hardware — handled it natively. The NoSQL movement did not kill SQL — far from it — but it expanded the database landscape, creating a rich ecosystem of specialised systems.

**Document stores** — MongoDB, CouchDB, the Yggdrasil DocStore — store data as **documents**, typically JSON or BSON. Each document is a self-contained record with a flexible schema: one document may have fields that another lacks, and the structure can evolve over time without schema migrations. Documents are grouped into **collections** (analogous to tables), and they are queried by field values, by ranges, or by full-text search. Document stores are ideal for content management, catalogues, user profiles, and any application where the data is naturally document-shaped and schema flexibility is valuable. The cost: no joins (or very limited joins), no standard query language (though MongoDB's aggregation pipeline and SQL-like interfaces have narrowed the gap), and weaker transactional guarantees (though multi-document ACID transactions were added to MongoDB in 2018 and are standard in 2040).

**Key-value stores** — Redis, RocksDB, Amazon DynamoDB — are the simplest database abstraction: a map from keys to values. Put(key, value), Get(key). No query language, no schema, no joins — just raw speed. Key-value stores are used for caching, session storage, message queues, and real-time analytics. Redis, in particular, has evolved far beyond a simple key-value store: it supports data structures (lists, sets, sorted sets, hashes, streams), pub/sub messaging, Lua scripting, and modules that add capabilities (RedisGraph, RedisSearch, RedisAI).

**Graph databases** — Neo4j, TigerGraph, Amazon Neptune — store data as **nodes** and **edges**, with properties on both. They are optimised for queries that traverse relationships — "find all friends of friends who bought this product," "find the shortest path between these two proteins in the interaction network," "find all accounts involved in a money-laundering ring." The query language, typically **Cypher** (Neo4j) or **Gremlin** (Apache TinkerPop), expresses graph patterns declaratively: `MATCH (a:Person)-[:KNOWS]->(b:Person)-[:KNOWS]->(c:Person) WHERE a.name = 'Alice' RETURN c`. Graph databases are the natural choice for social networks, recommendation engines, fraud detection, and knowledge graphs.

The **2040 convergence** has blurred the lines. PostgreSQL — the relational stalwart — supports JSONB columns with indexing, enabling document-store use cases within a relational framework. MongoDB supports SQL queries and ACID transactions. Redis supports disk persistence and secondary indexes. The future is not "relational vs. NoSQL" but "the right tool for the right job" — and the database professional who knows the full landscape, and can match the system to the workload, is the professional who thrives.

**Required Reading:**
- Martin Kleppmann, *Designing Data-Intensive Applications* (2017/2039), chs. 2–3
- Pramod J. Sadalage & Martin Fowler, *NoSQL Distilled* (2013/2038)
- MongoDB Documentation (docs.mongodb.com, 2040 edition)
- Neo4j Graph Database Documentation (neo4j.com/docs, 2040 edition)
- The Yggdrasil Multi-Model Database Architecture Report (2040)

**Discussion Questions:**
1. Document stores offer schema flexibility — but schemas are a form of documentation and validation. How do document stores compensate for the loss of schemas — and is "schema-on-read" a sufficient substitute for "schema-on-write"?
2. Graph databases are optimised for traversals — but relational databases can also do joins. At what point (depth of traversal, size of graph) does a graph database become clearly superior to a relational database for graph queries?
3. JSON/JSONB support in PostgreSQL means you can use a relational database as a document store. Is this the best of both worlds — or the worst, combining relational complexity with the lack of schema validation?

---

## Lecture 10: Distributed Databases — Replication, Partitioning, and the CAP Theorem

A single database server cannot store the data of Google, Amazon, or Meta — nor can it serve the throughput demanded by a popular application. **Distributed databases** spread data across multiple servers (nodes) to achieve **scalability** (handle more data and more queries by adding nodes), **availability** (continue to serve queries even when some nodes fail), and **geographic distribution** (serve users from the nearest data centre). The design of a distributed database is the art of managing the tension between these goals — a tension that is formalised, if imperfectly, by the **CAP theorem**.

The **CAP theorem** (Brewer, 2000; proved by Gilbert & Lynch, 2002) states that a distributed data store can provide at most two of the following three guarantees simultaneously: **Consistency** (every read sees the most recent write — or receives an error); **Availability** (every request to a non-failing node yields a response — no errors, no timeouts); and **Partition tolerance** (the system continues to operate despite network partitions — some messages between nodes are lost or delayed). Since network partitions are inevitable in a distributed system (the network is not perfectly reliable), the practical choice is: **CP** (consistent under partition — sacrifice availability: the system may refuse reads/writes during a partition, as in HBase, MongoDB with majority writes) or **AP** (available under partition — sacrifice consistency: reads may return stale data, as in Cassandra, DynamoDB with eventual consistency). The "CA" quadrant (consistent and available, but not partition-tolerant) is not achievable in a distributed system — there is no such thing as a distributed system without partitions.

**Replication** — storing copies of data on multiple nodes — is the mechanism for fault tolerance and read scalability. The **primary-standby** (or leader-follower) model: one node is the primary (leader), which accepts writes and replicates them to the standbys (followers); reads can be served by any node. If the primary fails, a standby is promoted to primary (failover). The **multi-leader** model: multiple nodes accept writes, which are asynchronously replicated to each other — higher write throughput, but risk of **write conflicts** (two leaders accept conflicting updates to the same record). **Leaderless** (or quorum-based) replication: writes and reads are sent to multiple nodes, and a quorum (typically majority) must agree; the system tolerates node failures as long as a quorum is available (Dynamo, Cassandra).

**Partitioning** (sharding) — splitting the data across nodes by some key range or hash — is the mechanism for scaling data size. Each node is responsible for a subset of the data (its partition or shard), and a query that touches data in a single partition is fast; a query that spans partitions requires coordination. The **partitioning key** is the most consequential design decision: it determines the locality of data — and thus the performance of queries, the distribution of load, and the ease of adding new nodes. Hash partitioning (evenly distributes data) vs. range partitioning (supports range scans but risks hot spots).

**Required Reading:**
- Eric Brewer, "Towards Robust Distributed Systems," *PODC Keynote* (2000)
- Seth Gilbert & Nancy Lynch, "Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services," *ACM SIGACT News* 33:2 (2002): 51–59
- Martin Kleppmann, *Designing Data-Intensive Applications* (2017/2039), chs. 5–8
- Werner Vogels, "Eventually Consistent," *Communications of the ACM* 52:1 (2009): 40–44
- The Yggdrasil Distributed DB Lab (2040)

**Discussion Questions:**
1. The CAP theorem is often oversimplified to "choose CP or AP." Is this a useful simplification — or does it obscure the fact that many systems can be tuned along a spectrum of consistency and availability?
2. Leaderless replication with quorum reads/writes can provide strong consistency if R + W > N (where R is read quorum, W is write quorum, N is replication factor). Why does this guarantee consistency — and what are the performance implications?
3. Hash partitioning evenly distributes data but makes range queries expensive. How do modern distributed databases (Spanner, CockroachDB) handle this trade-off — and what is the role of interleaved tables?

---

## Lecture 11: Vector Databases and AI-Native Storage — The 2040 Frontier

The rise of AI has created a new category of data — **embeddings** — and a new category of database — the **vector database**. An embedding is a dense, high-dimensional vector of floating-point numbers that represents the "meaning" of a piece of content — a text, an image, a user profile, a product description — in the latent space of a neural network. Two embeddings that are close (by cosine similarity or Euclidean distance) correspond to content that is semantically similar. The vector database stores these embeddings and supports **approximate nearest neighbour (ANN)** queries: given a query vector q, find the k stored vectors that are closest to q. This primitive underlies semantic search, image retrieval, recommendation, anomaly detection, and the retrieval-augmented generation (RAG) architecture that is the dominant AI application paradigm of the 2040s.

**Vector indexes** are the core data structure. Exact nearest-neighbour search in high dimensions is prohibitively expensive (the "curse of dimensionality" — all indexing structures degrade to linear scan as the dimension grows). **Approximate nearest neighbour (ANN)** algorithms trade a small, controllable probability of missing the true nearest neighbour for orders-of-magnitude speedups. The leading algorithms: **HNSW (Hierarchical Navigable Small World)** — a multi-layer graph where the top layer is sparse and navigable, and the bottom layer is dense and accurate; **IVF (Inverted File)** — partition the vector space into clusters, and at query time, search only the clusters closest to the query vector; **PQ (Product Quantisation)** — compress vectors into compact codes that can be compared quickly in the compressed space. The Yggdrasil Vector Engine implements all three, allowing students to benchmark and compare.

**Vector databases in the 2040s** — Pinecone, Weaviate, Milvus, pgvector (PostgreSQL extension), and the Yggdrasil VStore — integrate vector search with metadata filtering ("find images similar to this one, but only those taken after 2040 and tagged 'landscape'") and with hybrid search (combining vector similarity with full-text BM25 scores). The query language has evolved: a typical 2040 query combines a SQL-like filter with a vector similarity clause, all optimised by a mixed query planner that decides whether to filter first then search, search first then filter, or interleave.

The broader trend is **AI-native storage**: databases that are not merely augmented with vector search but designed from the ground up for AI workloads. These systems store model **gradients** (for distributed training), manage **model checkpoints** (versioned, indexed by training progress), and support **continuous learning** (new data is incrementally incorporated into the model, with the database managing the data-to-model pipeline). The convergence of databases and machine learning — predicted since the 1990s (the "Inductive Databases" vision of Imielinski and Mannila) — is finally happening, and CS203 graduates are positioned at the frontier.

**Required Reading:**
- J. Johnson, M. Douze & H. Jégou, "Billion-Scale Similarity Search with GPUs," *IEEE Transactions on Big Data* 7:3 (2021): 535–547 (FAISS)
- Yu.A. Malkov & D.A. Yashunin, "Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs," *IEEE TPAMI* 42:4 (2020): 824–836
- The Yggdrasil Vector Engine Documentation (2040)
- Pinecone Technical Architecture Report (2040)

**Discussion Questions:**
1. HNSW builds a multi-layer graph. What is the role of the top layers (few vertices, long edges) — and how do they enable "navigable small world" behaviour with logarithmic search complexity?
2. Product Quantisation compresses vectors — but the compression is lossy. How does PQ balance compression ratio against search accuracy, and in what scenarios does it outperform graph-based methods?
3. Vector databases currently store embeddings generated by separate models. What would it mean for the database to *learn* the embeddings — i.e., to train the model as data is ingested — and what new challenges (consistency, staleness, training-serving skew) would arise?

---

## Lecture 12: The Database Profession — Design Principles, Ethics, and the Long View

The final lecture surveys the database profession as it stands in 2040 — its principles, its ethics, and its trajectory. The databases we design today will store data that outlives their designers — medical records that span a lifetime, financial transactions that are audited decades later, scientific observations that become the raw material of discoveries not yet imagined. The database designer is a steward of data across time, and stewardship is an ethical responsibility.

The **design principles** that have emerged across the history of database systems — from Codd's relational manifesto through the NoSQL revolution to the AI-native databases of the 2040s — are: **data independence** (the logical schema should be independent of the physical storage); **declarative access** (the user specifies *what*, not *how*); **integrity** (the database enforces constraints, not the application — the database is the last line of defence against corrupted data); **durability** (once committed, a transaction should survive hardware failure, software failure, and the passage of time); and **evolution** (the schema should be able to change without losing data — migrations should be scripted, versioned, and reversible). These principles have proven remarkably resilient across generations of technology, and they constitute the core of the database profession's identity.

**Data ethics** has become, by 2040, a central concern of the database profession. The databases we design embody choices about what data to collect, how long to retain it, who can access it, and how it can be used. The database designer who creates a schema that tracks every user click, indefinitely, with no mechanism for deletion, is making an ethical decision — whether acknowledged or not. The principles of **data minimisation** (collect only what you need), **purpose limitation** (use data only for the purpose for which it was collected), **right to erasure** (the technical ability to delete a user's data, not just mark it as "inactive"), and **algorithmic fairness** (the database should not embed biases that produce discriminatory outcomes) are not merely legal requirements (of GDPR, CCPA, and their 2040 successors) — they are professional obligations.

The **2040 horizon** includes databases that are **self-tuning** (the optimiser learns from query history and adjusts indexes, materialised views, and partitioning strategies automatically), **self-healing** (the database detects corruptions and inconsistencies and repairs them using checksums and consensus protocols), and **self-securing** (the database enforces fine-grained access control, detects anomalous access patterns that suggest a breach, and encrypts data at rest and in transit by default). The database professional of 2040 is not a passive operator of a static system but an active designer of a living, adaptive data ecosystem.

The **connection to the Norse intellectual tradition** — always present at Yggdrasil — lies in the commitment to enduring memory. The Norse sagas, the rune-stones, the laws inscribed on rock — these were databases, technologies for preserving knowledge across generations in a reliable, verifiable form. The database professional of 2040 is engaged in the same project: carving memory into a durable medium, with care for its accuracy, its integrity, and its accessibility to those who will come after.

**Required Reading:**
- Martin Kleppmann, *Designing Data-Intensive Applications* (2017/2039), ch. 12 ("The Future of Data Systems")
- Pat Helland, "Immutability Changes Everything," *Communications of the ACM* 59:1 (2016): 64–70
- GDPR (General Data Protection Regulation) and the 2040 Global Data Ethics Framework
- The Yggdrasil Data Ethics Handbook (2040)
- The Poetic Edda, Hávamál — on the value of memory and the transience of the unwritten

**Discussion Questions:**
1. "The database is the last line of defence against corrupted data" — but many applications implement their own validation. Where should the boundary lie between application-layer validation and database constraints — and what are the consequences of getting it wrong?
2. The right to erasure (GDPR Article 17) is technically difficult in a relational database with foreign keys, cascading deletes, and backups. How should a database system implement "true deletion" — and what is the role of cryptographic erasure?
3. Self-tuning databases automate the tasks of a DBA. What becomes of the DBA — and what skills remain uniquely human when the database can tune itself?

---

## Final Examination Preparation

The final examination for CS203 consists of a three-hour written examination (50% of the final grade) and a database design and implementation project (50%). The written examination requires you to answer four questions from a choice of eight. The project requires you to design a database for a real-world domain (selected from the Yggdrasil Problem Repository), implement it in PostgreSQL, populate it with realistic data, and write a suite of queries demonstrating the schema's capabilities — all accompanied by a design document explaining the ER model, the normalisation decisions, the indexing strategy, and the query performance analysis.

### Sample Examination Questions

1. **(Relational Algebra and SQL)** Given a university schema — Student(sid, name, major), Course(cid, title, dept), Enrol(sid, cid, grade, semester) — write the following queries in (a) relational algebra and (b) SQL: (i) find the names of students who have taken every course in the 'CS' department; (ii) find the departments whose average grade across all courses is above 3.0; (iii) find, for each student, the course in which they received their highest grade (if tied, list all such courses).

2. **(Normalisation)** Given a relation R(A, B, C, D, E, F) with functional dependencies: AB → C, C → D, D → E, E → F, and F → A. (a) Identify all candidate keys. (b) Decompose R into BCNF. (c) Is your decomposition dependency-preserving? If not, propose a 3NF decomposition that is.

3. **(Indexing)** You are designing the indexing strategy for a social media platform's posts table: posts(post_id, user_id, timestamp, content, like_count). The workload consists of: (a) lookups by post_id (fetch a single post); (b) range queries by timestamp (fetch posts from the last hour); (c) range queries by like_count (top 100 posts by likes). For each query type, recommend the appropriate index (clustered or non-clustered, B-tree or hash) and justify your choice.

4. **(Transactions and Isolation)** Two transactions execute concurrently on an account table: T1 transfers $100 from account A to B; T2 computes the total balance across all accounts. Describe the possible outcomes under READ COMMITTED, REPEATABLE READ, and SERIALIZABLE. In particular: can T2 see A's balance before the transfer and B's balance after, yielding an inconsistent total?

5. **(Query Optimisation)** Given the query: `SELECT * FROM R JOIN S ON R.a = S.b WHERE R.c > 10 AND S.d = 'yes'`, with statistics: |R| = 1,000,000, |S| = 100,000, R.c is uniformly distributed from 0 to 100, S.d is 'yes' for 10% of rows, and there are no indexes. (a) Estimate the size of the intermediate results after each operation. (b) Propose a physical plan (join method, access methods) and estimate its I/O cost. (c) How would the plan change if there were a B-tree index on R(c)?

6. **(Distributed Databases)** You are designing a globally distributed database for a social network. User profiles are read frequently and written occasionally; users mostly interact with others in the same geographic region but occasionally with users anywhere. (a) Propose a partitioning and replication strategy. (b) How do you handle consistency for profile updates — and what isolation anomalies might users experience if you choose eventual consistency? (c) Discuss the implications of the CAP theorem for your design.

7. **(Vector Databases and AI)** You are building a semantic search system over a corpus of 10 million academic papers. Each paper has metadata (title, authors, year, venue) and a 768-dimensional embedding. The query is a natural-language search string. (a) Design the database schema — what data structures (relational, vector, or hybrid) would you use? (b) Describe the query execution pipeline, from text-to-embedding conversion through hybrid search. (c) How would you benchmark the search quality and performance?

8. **(Integrative Essay — Data Stewardship)** Drawing on material from across the course, articulate a philosophy of data stewardship. Address: the role of the database in preserving knowledge across time; the ethical responsibilities of the database designer (data minimisation, right to erasure, algorithmic fairness); and the tension between the database as a tool of efficiency and the database as a tool of control. Reference the course's connection to the Norse tradition of enduring memory — and argue for or against the proposition that the database designer of 2040 is the skald of the information age.

---

## Course Summary and Learning Outcomes

By the end of CS203, students will be able to:
1. Express queries in relational algebra and SQL, including complex joins, aggregations, subqueries, CTEs, and window functions
2. Design a database schema using entity-relationship modelling and normalise it to BCNF (or 3NF with justification)
3. Explain the physical storage of relational data — pages, buffer pools, B+ trees, hash indexes — and choose appropriate indexes for a given workload
4. Describe the query optimisation pipeline — parsing, heuristic rewriting, cost-based plan selection, and join ordering — and analyse the performance of execution plans
5. Implement transactions with ACID guarantees, apply two-phase locking and snapshot isolation, and reason about the anomalies permitted by each isolation level
6. Compare relational, document, key-value, graph, and vector databases — and select the appropriate system (or combination of systems) for a given application
7. Design distributed databases with replication and partitioning, and reason about the trade-offs codified by the CAP theorem
8. Articulate the ethical responsibilities of the database professional — data minimisation, privacy, fairness, and the stewardship of data across time

CS203 is the data-management pillar of the Computer Science degree and a prerequisite for CS304 (Distributed Systems), CS401 (AI Systems), and the AI World Modeling programme (where databases of world state, embeddings, and simulation outputs are fundamental). Data is the memory of civilisation; this course is the craft of its curation.
