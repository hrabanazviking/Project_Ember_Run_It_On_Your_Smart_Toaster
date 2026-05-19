# AI103: Data Structures & Algorithms
## Bachelor of Science in AI Agent Automation — University of Yggdrasil, 2040

**Credits:** 4
**Prerequisites:** None (foundational course; concurrent with AI101 and AI102)
**Description:** This course provides a rigorous introduction to the fundamental data structures and algorithms that underpin all of computer science and, crucially, all of AI agent engineering. Students will learn to analyze algorithmic complexity, implement core data structures, and apply algorithmic thinking to the design of intelligent systems. Special emphasis is placed on how data structures and algorithms are used in AI agent architectures — from search trees and priority queues in planning, to hash tables in memory systems, to graph algorithms in knowledge representation.

---

## Lectures

### ᚠ Lecture 1: Foundations — Why Data Structures and Algorithms Matter for AI

**Course:** AI103 — Data Structures & Algorithms
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Every program, from the simplest script to the most sophisticated AI agent, is built on two foundations: the data structures that organize information and the algorithms that process it. These are not abstract academic concerns — they are the warp and weft of the computational tapestry, the structural choices that determine whether a system runs in milliseconds or millennia, whether it fits in memory or exhausts it, whether it scales to millions of users or collapses under the weight of ten. Understanding data structures and algorithms is not merely useful for an AI engineer; it is essential. You cannot build an agent that reasons efficiently if you do not understand how to represent its knowledge, and you cannot represent its knowledge efficiently if you do not understand the data structures that support it.

A **data structure** is a systematic way of organizing and storing data so that it can be accessed and modified efficiently. The same data can be stored in many different structures, and the choice of structure has profound consequences. A phone book stored as a sorted array can be searched in O(log n) time using binary search; the same phone book stored as an unsorted linked list requires O(n) time for each lookup. When n is a million names, this is the difference between 20 comparisons and a million — a factor of fifty thousand. For an AI agent managing a knowledge base of billions of facts, the difference between data structures is the difference between responding in real time and being so slow that the user gives up.

An **algorithm** is a finite sequence of well-defined instructions that solves a computational problem. Algorithms are distinguished from ad hoc code by their generality (they work for any valid input), their determinism (each step is precisely specified), and their finiteness (they always terminate). The study of algorithms focuses on correctness (does the algorithm produce the right answer?), efficiency (how much time and space does it require?), and optimality (is this the best possible algorithm for this problem, or could we do better?).

The analysis of algorithmic efficiency relies on **asymptotic notation**, which describes the growth rate of an algorithm's resource requirements as the input size increases. Big-O notation (O) provides an upper bound: an algorithm that runs in O(n²) time takes at most *cn²* steps for some constant *c* and sufficiently large *n*. Big-Ω (omega) provides a lower bound: a problem that requires Ω(n log n) time cannot be solved faster than that in the worst case. Big-Θ (theta) provides a tight bound: merge sort runs in Θ(n log n), meaning it is both O(n log n) and Ω(n log n). These notations abstract away constant factors and focus on the dominant term, which is appropriate because constant factors are hardware-dependent and the dominant term dominates as n grows.

Common complexity classes that every AI engineer must know by heart: **O(1)** — constant time, independent of input size (hash table lookup, array indexing). **O(log n)** — logarithmic time, the time grows as the logarithm of the input (binary search, balanced tree operations). **O(n)** — linear time, the time grows proportionally with the input (sequential scan, linear search). **O(n log n)** — linearithmic time, the time grows as n times the logarithm of n (efficient sorting, merge sort, quicksort on average). **O(n²)** — quadratic time, the time grows as the square of the input (bubble sort, insertion sort, all pairs comparison). **O(2ⁿ)** — exponential time, the time doubles with each additional input element (brute-force subset enumeration, traveling salesman by exhaustive search). **O(n!)** — factorial time, the time grows as n factorial (permutation enumeration, worst-case SAT solving).

To make this concrete for AI agents: an agent that stores its knowledge in a sorted array can retrieve a fact in O(log n) time — for a billion facts, this is about 30 comparisons. An agent that stores the same knowledge in a hash table can retrieve it in O(1) time — a single lookup. An agent that stores its knowledge in an unsorted array must scan the entire collection in O(n) time — a billion comparisons. The choice of data structure is not a minor implementation detail; it determines whether the agent can respond in real-time or whether it spends seconds per query, which in an interactive system is the difference between usable and unusable.

The relationship between data structures and algorithms is not one-directional. Data structures suggest algorithms (a sorted array suggests binary search; a graph suggests traversal) and algorithms require data structures (Dijkstra's algorithm requires a priority queue; depth-first search requires a stack or recursive call stack). The most elegant and efficient solutions to computational problems often arise from finding the right pairing of data structure and algorithm — the right vessel for the right operation, like a Völva selecting the right vessel for the right völ (sacred mead).

The Norse concept of *hlutr* — the lot or portion cast by the Norse for divination — is an apt metaphor. Divination by lot involves drawing a marked piece from a collection, and the efficiency of that draw depends on how the lots are stored and organized. A pile of lots drawn blindly is O(n) search; a sorted set of lots is O(log n) search; a hash-mapped collection of lots is O(1) search. The divinatory outcome depends not on the lots themselves but on how they are organized and accessed. Similarly, an agent's performance depends not merely on what data it possesses but on how that data is structured and how efficiently it can be queried and updated.

Throughout this course, we will maintain a dual focus: on the classical theory of data structures and algorithms (which has been refined over seven decades and remains as relevant as ever), and on their application to AI agent systems (which requires understanding how these structures are used in practice — in search, in planning, in memory, in communication). Every data structure we study will be accompanied by an example of its use in the architecture of a real or hypothetical AI agent. Every algorithm we analyze will be connected to a computational problem that agents actually face. This is not a course in abstract theory; it is a course in the structural foundations of intelligent systems.

**Key Topics:**

- **Data structures and algorithms defined:** What they are, why they matter, and how they relate
- **Asymptotic notation:** Big-O, Big-Ω, Big-Θ, and the meaning of complexity classes
- **Common complexity classes:** O(1), O(log n), O(n), O(n log n), O(n²), O(2ⁿ), O(n!) — with AI agent examples
- **The data structure–algorithm relationship:** How structures suggest algorithms and algorithms require structures
- **The *hlutr* metaphor:** Organization and access efficiency in divination and computation

**Required Reading:**

- Cormen, T.H., Leiserson, C.E., Rivest, R.L., & Stein, C. *Introduction to Algorithms* (4th ed., 2038), Chapters 1–3
- Sedgewick, R. & Wayne, K. *Algorithms* (5th ed., 2039), Chapter 1
- Skiena, S.S. *The Algorithm Design Manual* (3rd ed., 2038), Chapter 1

**Discussion Questions:**

1. An AI agent with a billion facts must answer queries in under 100 milliseconds. Which complexity classes are acceptable? Which rule out certain data structures? Design the constraints.
2. Why does asymptotic notation ignore constant factors? Under what conditions would constant factors matter more than asymptotic complexity for an AI agent?
3. The *hlutr* metaphor suggests that the same information, differently organized, yields different results. Can you think of examples in AI where the same data, structured differently, enables fundamentally different capabilities?

---

### ᚢ Lecture 2: Arrays, Linked Lists, and Memory — The Building Blocks

**Course:** AI103 — Data Structures & Algorithms
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Arrays and linked lists are the two fundamental ways of organizing a collection of items in memory. Every other data structure — stacks, queues, trees, graphs, hash tables — is built on one or both of these foundations. Understanding their properties, tradeoffs, and performance characteristics is the first step toward understanding all of computer science.

An **array** is a contiguous block of memory that stores items of the same type, accessed by their index. The critical property of an array is that any element can be accessed in O(1) time by computing its address: if the array starts at address *base* and each element occupies *k* bytes, then element *i* is at address *base + i × k*. This direct addressability makes arrays ideal for random access — reading or writing any element in constant time regardless of the array's size. However, arrays have two significant limitations: their size is typically fixed at creation (though dynamic arrays like Python's *list* and Java's *ArrayList* amortize this cost), and inserting or deleting an element in the middle requires shifting all subsequent elements, which takes O(n) time.

**Linked lists** take a different approach. Instead of storing items in contiguous memory, each item (called a node) stores its value and a pointer to the next node. This pointer-based structure means that insertions and deletions are O(1) — you simply redirect the relevant pointers. However, accessing the i-th element requires traversing the list from the head, which takes O(i) time. A linked list is ideal when you need frequent insertions and deletions at known positions and you don't need random access.

The tradeoff between arrays and linked lists is a fundamental pattern that recurs throughout computer science: **contiguous vs. pointer-based representation**, or equivalently, **random access vs. efficient modification**. This tradeoff is not merely technical; it shapes the entire architecture of AI systems. Consider an AI agent's conversation history. If the history is stored as an array (or dynamic array), the agent can jump to any past message in O(1) time — useful for retrieving a specific turn. If it is stored as a linked list, the agent can efficiently splice in new context or delete outdated messages without reshuffling the entire history. Modern agent frameworks typically use dynamic arrays (like Python lists) for conversation context, because the dominant operations are appending new messages (O(1) amortized) and sequential access (O(1)), while mid-sequence deletions are rare.

**Doubly linked lists** add a pointer from each node to its predecessor as well as its successor, enabling O(1) insertion and deletion at both ends. This is useful for implementing **deques** (double-ended queues), which are a fundamental data structure in many algorithms. In AI agents, a doubly linked list can represent a bidirectional chain of reasoning steps, where each step points forward to its consequence and backward to its justification.

**Dynamic arrays** (also called resizable arrays or growable arrays) solve the fixed-size limitation of static arrays by automatically expanding when capacity is exceeded. Python's *list*, Java's *ArrayList*, and C++'s *std::vector* are all dynamic arrays. When the array is full and a new element must be added, the implementation allocates a new array (typically twice the current size), copies the existing elements, and frees the old array. This resizing operation is O(n), but it happens infrequently — specifically, the amortized cost of appending *n* elements is O(1) per append. The key insight is that the resizing cost is "paid for" by the cheap appends that follow, just as a farmer who builds a larger barn amortizes the construction cost over the additional years of use.

The memory layout of data structures has performance implications beyond asymptotic complexity. Modern processors have multiple levels of cache (L1, L2, L3) that are much faster than main memory. Contiguous arrays benefit from **cache locality**: when one element is loaded into cache, adjacent elements are loaded too, making sequential access extremely fast. Linked lists, with their scattered memory allocation, suffer from **cache misses**: each node may be in a different cache line, causing expensive memory accesses. On modern hardware, the constant-factor advantage of cache locality can make arrays 10–100× faster than linked lists for sequential access, even though both are O(n) asymptotically. This is why, in practice, arrays are preferred for most applications — the theoretical advantage of linked lists (O(1) insertion/deletion) is often outweighed by the practical advantage of arrays (cache locality).

For AI agents, the array-vs-linked-list tradeoff manifests in several specific design decisions. **Token sequences** in language models are stored as arrays, enabling O(1) access to any position in the sequence — essential for the self-attention mechanism, which must compute relationships between all pairs of positions. **Experience replay buffers** in reinforcement learning are typically implemented as circular arrays (fixed-size buffers that overwrite old data), because the dominant operations are appending new experiences and randomly sampling old ones. **Message queues** in multi-agent systems may be implemented as linked lists when messages are frequently inserted and removed from the front, or as arrays when the dominant operation is sequential processing.

**Memory management** is a concern that underlies all data structure choices. In languages with automatic garbage collection (Python, Java), the programmer does not manually allocate and free memory, but the garbage collector incurs runtime overhead and can cause unpredictable pauses. In languages with manual memory management (C, C++, Rust), the programmer controls allocation precisely but must avoid leaks (forgetting to free memory) and double-frees (freeing memory twice). Rust's ownership system provides a third option: the compiler enforces memory safety at compile time, without garbage collection overhead. For AI agent systems that run continuously — agents that operate 24/7, managing conversations, updating knowledge, and processing requests — memory management is not a minor concern; it is a core architectural decision that affects performance, reliability, and security.

**Key Topics:**

- **Arrays:** Contiguous memory, O(1) random access, O(n) insertion/deletion, cache locality advantages
- **Linked lists:** Pointer-based structure, O(1) insertion/deletion at known positions, O(n) random access, cache misses
- **Doubly linked lists:** Bidirectional traversal, O(1) insertion/deletion at both ends
- **Dynamic arrays:** Amortized O(1) append, resizing policy, and practical performance
- **Cache locality:** Why arrays often outperform linked lists despite similar asymptotic complexity
- **Memory management:** Garbage collection, manual management, Rust's ownership model, and implications for AI agents

**Required Reading:**

- Cormen et al., *Introduction to Algorithms* (4th ed.), Chapter 10 (Elementary Data Structures)
- Sedgewick & Wayne, *Algorithms* (5th ed.), Chapter 1.3 (Bags, Queues, and Stacks)
- Drepper, U. "What Every Programmer Should Know About Memory" (2007, revised 2038)

**Discussion Questions:**

1. In theory, linked lists offer O(1) insertion while arrays offer O(n). In practice, arrays often outperform linked lists. Under what conditions does the theoretical advantage of linked lists actually matter? When should an AI agent engineer choose a linked list over an array?
2. Cache locality can make a 10× performance difference. Should algorithmic complexity analysis include cache effects, or should we treat it as a "constant factor" that hardware will eventually solve?
3. An AI agent that runs continuously for months or years must manage memory carefully. What are the risks of memory leaks in agent systems, and how does the choice of data structure affect memory management?

---

### ᚦ Lecture 3: Stacks, Queues, and Deques — Order from Chaos

**Course:** AI103 — Data Structures & Algorithms
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Stacks and queues are the simplest and most ubiquitous abstract data types in computer science. They are also, surprisingly, among the most powerful. A stack is a Last-In-First-Out (LIFO) structure: the last item added is the first item removed. A queue is a First-In-First-Out (FIFO) structure: the first item added is the first item removed. A deque (double-ended queue) generalizes both, allowing insertion and removal at both ends. These three structures impose order on data — not the sorted order of a search tree, but the operational order that underlies virtually every algorithm and system.

The **stack** operates on a single principle: push an item onto the top, pop an item off the top. There is no access to items below the top. This LIFO discipline is the mechanism behind function call stacks (where each recursive call pushes a new frame, and each return pops the frame), expression evaluation (where operators are applied to the most recently pushed operands), and depth-first search (where the most recently discovered node is explored first, naturally matching the LIFO order).

In AI agent systems, stacks are ubiquitous. The **call stack** of a program is a stack — when an agent calls a function, it pushes a frame; when the function returns, it pops the frame. The **undo stack** in an editor (or an agent's action rollback system) is a stack — the most recent action is the first to be undone. The **parenthesis matching** problem (checking that brackets in an expression are properly nested) is solved by a stack. The **breadcrumb trail** — the path of reasoning steps that an agent has taken — is a stack that enables backtracking when a line of reasoning leads to a dead end.

The **queue** operates on the complementary principle: enqueue an item at the back, dequeue an item from the front. This FIFO discipline is the mechanism behind task scheduling (first come, first served), breadth-first search (where nodes are explored in the order they were discovered), and message passing between concurrent processes. When an agent receives multiple requests, it typically processes them in a queue — first in, first out. When an agent spawns sub-tasks, they are queued for execution. When messages arrive from other agents in a multi-agent system, they are placed in a message queue and processed in order.

**Priority queues** extend the basic queue concept by associating a priority with each item and always dequeuing the highest-priority item, not the first-arrived item. Priority queues are essential in AI: **A* search** uses a priority queue to always expand the most promising node; **Dijkstra's algorithm** uses a priority queue to always process the closest unvisited node; **task scheduling** in operating systems uses priority queues to allocate CPU time to the most important process; **event-driven simulation** uses priority queues to process events in chronological order. A priority queue is typically implemented using a **binary heap** — a complete binary tree stored in an array where each parent node has higher priority than its children — which supports insertion and extraction in O(log n) time.

**Deques** (double-ended queues) allow insertion and removal at both ends in O(1) time. They are used in algorithms that require access to both the front and back of a sequence — for example, the **sliding window maximum** algorithm, which maintains a deque of candidate maxima as a window slides across an array. In AI systems, deques are used for **experience replay** (where old experiences are removed from the front and new experiences added to the back), for **bidirectional message queues** (where agents can send and receive from both ends), and for **circular buffers** (where a fixed-size deque wraps around, overwriting old data when full).

The implementation of stacks and queues is straightforward. A stack can be implemented using an array (with a pointer to the top) or a linked list (with a pointer to the head). A queue can be implemented using an array (with pointers to the front and back, wrapping around to form a circular buffer) or a linked list (with pointers to the head and tail). The choice depends on whether random access is needed (array-based) or whether the structure must grow and shrink dynamically (linked list-based). In practice, most production systems use dynamic array-based implementations (like Python's *collections.deque*) that offer O(1) operations at both ends with good cache locality.

For AI agents, the stack-queue duality maps onto a fundamental architectural choice: **depth-first vs. breadth-first processing**. An agent that processes its inputs and sub-tasks using a stack is doing depth-first exploration: it pursues the most recently discovered lead as far as possible before backtracking. An agent that processes its inputs using a queue is doing breadth-first exploration: it processes all leads at the current level before moving deeper. The ReAct (Reason + Act) architecture, which alternates between thinking and doing, can be understood as a system that maintains both a stack (of reasoning moves) and a queue (of action items), interleaving LIFO reasoning with FIFO execution.

The Norse concept of **hafnarbraut** — harbor approach — captures this distinction. A ship approaching a harbor follows one of two strategies: it can thread through narrow channels one at a time (depth-first, like a stack) or it can survey all visible channels before choosing the best one (breadth-first, like a queue). Neither strategy is universally superior; depth-first is efficient when the first promising lead is likely correct, while breadth-first is robust when the best path is not known in advance. An AI agent must choose between these strategies — or, better, combine them — based on the structure of the problem it faces.

**Key Topics:**

- **Stacks:** LIFO principle, push/pop operations, call stacks, undo stacks, DFS
- **Queues:** FIFO principle, enqueue/dequeue operations, BFS, task scheduling, message passing
- **Priority queues:** Always dequeue the highest-priority item, heap implementation, O(log n) operations
- **Deques:** Double-ended operations, sliding window algorithms, circular buffers
- **Implementation choices:** Array-based vs. linked list-based, cache locality, dynamic resizing
- **Depth-first vs. breadth-first processing in agents:** The architectural choice between exploration strategies

**Required Reading:**

- Cormen et al., *Introduction to Algorithms* (4th ed.), Chapters 10.1–10.3
- Sedgewick & Wayne, *Algorithms* (5th ed.), Chapters 1.3–1.4
- Knuth, D.E. *The Art of Computer Programming, Vol. 1* (3rd ed.), Section 2.2.1–2.2.2

**Discussion Questions:**

1. An AI agent could implement its task queue as a stack (LIFO) or a queue (FIFO). Under what conditions would each be more appropriate? What about a priority queue?
2. The call stack in a recursive algorithm can grow to O(n) depth. What happens when an AI agent's reasoning chain exceeds the stack limit? How can this be managed?
3. Priority queues are used in A* search to always expand the most promising node. What would happen if you used a FIFO queue instead? What about a LIFO stack? Describe the resulting search behavior.

---

### ᚬ Lecture 4: Trees — From Roots to Branches

**Course:** AI103 — Data Structures & Algorithms
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Trees are among the most versatile and widely used data structures in computer science. A tree is a hierarchical structure consisting of nodes connected by edges, with a single root node at the top, internal nodes in the middle, and leaf nodes at the bottom. Every node (except the root) has exactly one parent, and every node has zero or more children. This hierarchical organization mirrors countless natural and artificial structures: file systems, organizational charts, parse trees, decision trees, classification hierarchies, and the evolutionary tree of life. In AI, trees are particularly important because they model the structure of search spaces, the organization of knowledge, and the decomposition of complex tasks into sub-tasks.

A **binary tree** is a tree in which each node has at most two children, referred to as the left child and the right child. Binary trees are the foundation of many important data structures and algorithms. A **binary search tree (BST)** is a binary tree where every node's left subtree contains only values less than the node, and every right subtree contains only values greater. Searching a BST takes O(log n) time on average (when the tree is balanced) but O(n) time in the worst case (when the tree degenerates into a linked list). This dramatic performance difference motivates the development of **self-balancing binary trees**, which maintain balance through rotations: AVL trees (which keep the height difference between subtrees at most 1) and red-black trees (which enforce coloring rules that guarantee O(log n) height). In Python's *sortedcontainers* library and Java's *TreeMap*, these balanced BSTs provide guaranteed O(log n) search, insertion, and deletion.

**Heaps** are a special kind of binary tree with two additional properties: the heap property (in a max-heap, every parent is greater than its children; in a min-heap, every parent is smaller) and the shape property (the tree is complete — all levels are filled except possibly the last, which is filled from left to right). Heaps are the natural implementation of priority queues: the maximum (or minimum) element is always at the root, and it can be extracted in O(log n) time. Heaps are also the backbone of **heapsort**, an O(n log n) sorting algorithm that sorts in-place (requires O(1) additional memory) — a property that makes it useful in memory-constrained environments.

**Tries** (also called prefix trees) are trees specialized for storing strings. Each edge represents a character, and each path from the root to a node represents a prefix. Tries enable O(k) prefix search, where k is the length of the prefix — independent of the number of strings stored. This makes tries ideal for autocomplete, spell-checking, and IP routing. In AI agents, tries are used for **efficient token lookup** in language models, for **command completion** in agent interfaces, and for **intent classification** in natural language understanding systems.

**B-trees** generalize binary search trees to nodes with many children, making them suitable for disk-based storage where the cost of reading a block of data is much higher than the cost of searching within a block. B-trees are the data structure underlying virtually all databases and file systems: when you query a database, the engine uses a B-tree index to find your data in O(log n) disk reads rather than scanning the entire table. In AI agent systems, B-trees are essential for **persistent knowledge bases** — the structured storage that agents query to retrieve facts, rules, and procedures.

Beyond these standard structures, trees appear throughout AI in less obvious but equally important forms. **Decision trees** are models that classify instances by following a path from the root (which represents the entire dataset) to a leaf (which represents a prediction). Each internal node tests a feature, and each branch corresponds to a value of that feature. Decision trees are interpretable, efficient, and widely used in both machine learning and automated reasoning. **Parse trees** represent the grammatical structure of sentences in natural language processing. **Game trees** represent the possible sequences of moves in a two-player game, with minimax search pruning branches that are provably suboptimal. **Behavior trees** are used in game AI and robotics to represent hierarchical task decompositions, where complex behaviors are composed from simpler sub-behaviors.

The **trie of Yggdrasil** is an apt metaphor — perhaps more than a metaphor. Yggdrasil, the World Tree of Norse cosmology, connects the nine realms through its roots, trunk, and branches. It is a hierarchical structure where each node (realm) is reachable from the root (the trunk) by a unique path. The Norns tend the tree, watering its roots and weaving the fate of all who dwell in its branches. An AI agent's knowledge base is a similar structure: a hierarchical tree of concepts, where each concept is reachable from the root by a unique path of hyponymic (IS-A) and meronymic (PART-OF) relations. Maintaining this tree — keeping it balanced, watering its roots with new data, pruning dead branches — is the ongoing labor of the AI engineer, not unlike the labor of the Norns.

Tree traversal algorithms are fundamental operations that visit every node in a tree in a specific order. **Pre-order traversal** (root, left, right) is used for copying trees and creating prefix expressions. **In-order traversal** (left, root, right) produces a sorted sequence when applied to a BST. **Post-order traversal** (left, right, root) is used for deleting trees and evaluating postfix expressions. **Level-order traversal** (breadth-first, level by level) is used for finding the shortest path in unweighted trees and for serializing trees. Each traversal order reveals different information about the tree, and choosing the right traversal is as important as choosing the right tree structure.

**Key Topics:**

- **Binary trees and BSTs:** Structure, search, insertion, deletion, and the importance of balance
- **Self-balancing trees:** AVL trees, red-black trees, and O(log n) guarantees
- **Heaps:** Max-heap, min-heap, priority queue implementation, heapsort
- **Tries:** Prefix search, autocomplete, token lookup, intent classification
- **B-trees:** Disk-based storage, database indexing, persistent knowledge bases
- **Decision trees, parse trees, game trees, behavior trees:** Tree structures in AI
- **Tree traversal:** Pre-order, in-order, post-order, level-order — and when to use each

**Required Reading:**

- Cormen et al., *Introduction to Algorithms* (4th ed.), Chapters 12–13 (BSTs, Red-Black Trees), Chapter 6 (Heaps)
- Sedgewick & Wayne, *Algorithms* (5th ed.), Chapters 3.2–3.4 (BSTs, Balanced Trees)
- Knuth, D.E. *The Art of Computer Programming, Vol. 3* (2nd ed.), Sections 6.2–6.3

**Discussion Questions:**

1. A degenerate BST (every node has only one child) is equivalent to a linked list, with O(n) search time. What strategies exist for keeping a BST balanced during dynamic operations, and what are their tradeoffs?
2. In an AI agent's knowledge base, some concepts have many subtypes and others have few. What data structure would you use to represent this uneven hierarchy efficiently? How would you handle queries like "find all instances of X or its subtypes"?
3. Yggdrasil connects nine realms through its roots and branches. If an AI agent's knowledge were organized as a tree, what would the root represent? What would the leaves represent? And how would you handle concepts that belong to multiple branches (the problem of cross-cutting concerns)?

---

### ᚱ Lecture 5: Hash Tables — The Art of Instant Lookup

**Course:** AI103 — Data Structures & Algorithms
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Hash tables are, in many ways, the most important data structure in modern computing. They provide O(1) average-case performance for insertion, deletion, and lookup — a claim so powerful that it seems to violate the laws of computation. How can you find an item among a million others without even looking? The answer is the hash function: a function that maps each key to a specific index in an array, allowing direct access to the location where the value is stored.

A **hash function** takes a key (which can be a string, a number, an object — anything hashable) and produces an integer, which is then used as an index into an array (the hash table). A good hash function has two essential properties: it is **deterministic** (the same key always produces the same hash value) and it **distributes keys uniformly** across the available indices. The latter property is crucial: if the hash function maps all keys to the same index, the hash table degenerates into a linked list with O(n) performance. In practice, hash functions like MurmurHash, CityHash, and SipHash are designed to distribute keys uniformly even for adversarial inputs, and they are used as the default in Python's *dict*, Java's *HashMap*, and C++'s *std::unordered_map*.

**Collision resolution** is necessary because the number of possible keys vastly exceeds the number of available indices, so different keys will inevitably map to the same index. Two main strategies exist. **Chaining** stores all keys that hash to the same index in a linked list (or other structure) at that index. The worst-case lookup time is O(n) if all keys hash to the same index, but the average case is O(1 + α), where α (the load factor) is the ratio of keys to indices. **Open addressing** stores all keys directly in the array, probing for the next available slot when a collision occurs. Linear probing (check the next slot), quadratic probing (check slots at quadratic distances), and double hashing (use a second hash function to determine the probe distance) are common strategies. Open addressing has better cache locality than chaining (all data is in one array), but it requires a lower load factor to maintain O(1) performance.

The **load factor** α = n/m (where n is the number of keys and m is the number of slots) is the critical parameter in hash table performance. When α approaches 1 (the table is nearly full), collisions become frequent and performance degrades. When α is low (the table is mostly empty), collisions are rare but memory is wasted. Most hash table implementations trigger **rehashing** — allocating a new, larger array and reinserting all keys — when α exceeds a threshold (typically 0.75). Rehashing is O(n) but happens infrequently, so the amortized cost of insertion remains O(1).

In AI agent systems, hash tables are everywhere. **Caching** is the most obvious application: when an agent computes a result (e.g., the embedding of a document, the translation of a phrase, the outcome of a function call), it stores the result in a hash table keyed by the input, so that future requests for the same input can be served in O(1) time. **Memoization** — caching the results of function calls — is a form of caching that transforms exponential-time recursive algorithms into polynomial-time ones. **Entity resolution** in knowledge bases uses hash tables to quickly find entities by name or ID. **Feature lookup** in machine learning uses hash tables (or their variants, like feature hashing) to map feature names to indices in a weight vector. **Session management** in web systems uses hash tables to map user IDs to session objects. In every case, the pattern is the same: a key must be mapped to a value in constant time, and a hash table provides exactly that.

**Consistent hashing** is a variant designed for distributed systems, where keys must be mapped to one of many servers. In consistent hashing, both keys and servers are mapped to points on a ring (using a hash function), and each key is assigned to the next server clockwise on the ring. When a server is added or removed, only the keys that would have been assigned to that server need to be remapped — minimizing disruption. Consistent hashing is used in distributed databases (Cassandra, DynamoDB), content delivery networks (Akamai), and distributed caching systems (Memcached). For AI agents deployed across multiple machines, consistent hashing is essential for distributing requests without hot spots.

**Bloom filters** are a probabilistic variant of hash tables that answer a simpler question: "is this key possibly in the set, or definitely not?" A Bloom filter uses *k* independent hash functions to set *k* bits in a bit array. To check membership, it computes the same *k* hash functions and checks whether all *k* bits are set. If any bit is not set, the key is definitely not in the set (no false negatives). If all bits are set, the key is probably in the set, but it might be a false positive (all *k* bits happened to be set by other keys). Bloom filters are useful when the cost of a false positive is low (a quick verification) and the cost of a full lookup is high (a database query). In AI systems, Bloom filters are used for **spell checking** (is this word possibly valid?), **crawler URL deduplication** (have we possibly seen this URL before?), and **cache filtering** (is this query possibly in the cache?).

The performance of hash tables depends critically on the quality of the hash function. A poor hash function maps many keys to the same index, degrading O(1) average-case performance to O(n) worst-case. This is not merely a theoretical concern: in 2012, a class of **hash-flooding attacks** was discovered in which an adversary could craft inputs that all hash to the same bucket, effectively turning O(1) operations into O(n) and causing denial of service. Modern hash functions include randomized seed values (keyed hashing) that prevent an adversary from predicting hash values, making hash-flooding attacks infeasible. For AI agents that accept untrusted input, using a keyed hash function is a security essential, not an optimization.

The Viking concept of **heimkart** — a home map, or mental map of one's territory — parallels the hash table. A Viking navigating by heimkart doesn't search through every possible location; they use landmarks, routes, and spatial memory to go directly to their destination. A hash function is the computational analogue: it maps a query directly to the location where the answer is stored. The quality of the heimkart (or the hash function) determines whether the navigation is fast (O(1)) or slow (O(n)). A well-constructed heimkart, like a well-designed hash function, distributes destinations evenly across the territory, avoiding congestion and ensuring fast access to every location.

**Key Topics:**

- **Hash functions:** Determinism, uniformity, MurmurHash, SipHash, keyed hashing
- **Collision resolution:** Chaining vs. open addressing, linear/quadratic/double hashing
- **Load factor and rehashing:** Performance tradeoffs, amortized analysis
- **Applications in AI agents:** Caching, memoization, entity resolution, session management
- **Consistent hashing:** Distributed systems, minimal remapping, server assignment
- **Bloom filters:** Probabilistic membership testing, false positives, no false negatives
- **Hash-flooding attacks:** Adversarial inputs, keyed hashing, security implications

**Required Reading:**

- Cormen et al., *Introduction to Algorithms* (4th ed.), Chapter 11 (Hash Tables)
- Sedgewick & Wayne, *Algorithms* (5th ed.), Chapter 3.5 (Hashing)
- Kirsch, A., Mitzenmacher, M. "Less Hashing, Same Performance: Hashing with Two Hash Functions" (2038 review)

**Discussion Questions:**

1. A hash table provides O(1) average-case lookup but O(n) worst-case. For an AI agent that must guarantee response times, is this acceptable? What strategies can mitigate worst-case behavior?
2. Bloom filters trade accuracy for space. In what AI applications is this tradeoff worthwhile? When would a false positive be unacceptable?
3. Consistent hashing minimizes disruption when servers are added or removed. How does this principle apply to AI agent memory systems, where knowledge is distributed across multiple storage nodes?

---

### ᚴ Lecture 6: Sorting — Putting Order into Chaos

**Course:** AI103 — Data Structures & Algorithms
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Sorting is one of the most fundamental operations in computer science. It is also one of the most studied: the problem of arranging items in order has spawned dozens of algorithms, deep theoretical results about computational lower bounds, and practical engineering insights about the interaction between algorithm and hardware. For AI agents, sorting is not merely an academic exercise — it is a daily necessity. Agents sort search results by relevance, messages by timestamp, tasks by priority, and knowledge items by confidence. Understanding sorting is understanding how to impose order on data, and order is the precondition for almost every useful operation.

The classic comparison-based sorting algorithms are defined by their time complexity. **Bubble sort** and **insertion sort** are O(n²) in the worst case — they compare each element with every other element, making them impractical for large datasets. But insertion sort has a useful property: it is O(n) for nearly-sorted input (when each element is close to its final position). **Merge sort** divides the array in half, recursively sorts each half, and merges the two sorted halves in O(n) time, yielding an overall O(n log n) guarantee. **Quicksort** selects a pivot element, partitions the array into elements less than and greater than the pivot, and recursively sorts each partition. Quicksort is O(n log n) on average but O(n²) in the worst case (when the pivot is always the smallest or largest element). In practice, quicksort is often faster than merge sort because it has better cache locality and does in-place partitioning, so most standard libraries use a hybrid of quicksort, insertion sort (for small subarrays), and heapsort (as a fallback) — this is the strategy behind Python's *sorted()* and Java's *Arrays.sort()*.

**Heapsort** converts the array into a max-heap in O(n) time, then repeatedly extracts the maximum element (O(log n) per extraction) to produce a sorted array. The total time is O(n log n), and heapsort has the advantage of sorting in-place (O(1) additional memory), but its cache performance is worse than quicksort's because heap operations access memory non-sequentially. **Timsort**, the default sort in Python and Java, is a hybrid of merge sort and insertion sort that detects already-sorted runs in the input and merges them efficiently, achieving O(n) performance on nearly-sorted data and O(n log n) in the worst case. Timsort's adaptability makes it the best general-purpose sort for real-world data, which is often partially sorted.

The theoretical lower bound for comparison-based sorting is **Ω(n log n)** — no algorithm that compares elements pairwise can sort n items in fewer than n log n comparisons in the worst case. This is because there are n! possible orderings of n items, and each comparison distinguishes at most two orderings, so at least log₂(n!) ≈ n log n comparisons are needed. However, **non-comparison sorts** can achieve O(n) time by exploiting additional information about the keys. **Counting sort** counts the occurrences of each distinct key and uses those counts to place items directly into their sorted positions. **Radix sort** sorts items digit by digit, starting from the least significant digit. **Bucket sort** distributes items into buckets based on their key ranges and sorts each bucket individually. These algorithms are O(n) when the keys are integers in a bounded range (counting sort) or when the keys can be decomposed into small digits (radix sort), but they require additional information about the key distribution that comparison sorts do not.

For AI agents, sorting is most relevant in the context of **result ranking**. When an agent searches its knowledge base, it must rank results by relevance, sorting millions of candidate items to find the top k. This is not a full sort — it is a **top-k selection** problem, which can be solved more efficiently using a min-heap of size k. The agent maintains a heap of the k most relevant items; for each new candidate, if it is more relevant than the least relevant item in the heap, it replaces that item. This runs in O(n log k) time rather than O(n log n) — a significant improvement when k << n.

**Stability** is another important property of sorting algorithms. A sort is **stable** if it preserves the relative order of equal elements. This matters when sorting on multiple keys: if you sort employees first by department and then by name, a stable sort on name will preserve the department ordering within each name group, ensuring that employees in the same department appear in name order. Merge sort and Timsort are stable; quicksort and heapsort are not. Stability is important in AI applications where multiple ranking signals must be combined: a stable sort ensures that a secondary ranking signal (e.g., recency) does not disrupt the primary signal (e.g., relevance).

The Norse concept of **rökkr** — twilight, the border between order and chaos — captures the essence of sorting. Before sorting, data is in a state of rökkr: disordered, chaotic, difficult to navigate. After sorting, order has been imposed: each item has its place, and every item can be found efficiently. The act of sorting is the act of creating order from disorder, of transforming a rökkr state into a state where every element has its designated position. But the Norse also understood that order is never permanent — entropy always increases, data always drifts toward disorder, and the need to sort again is a recurring necessity, not a one-time operation. An AI agent that sorts its knowledge once and never re-sorts will find that its knowledge is gradually corrupted by insertions, deletions, and updates that violate the sorted order.

**Key Topics:**

- **Comparison sorts:** Bubble sort, insertion sort, merge sort, quicksort, heapsort, Timsort
- **The Ω(n log n) lower bound:** Why no comparison sort can do better, and the proof
- **Non-comparison sorts:** Counting sort, radix sort, bucket sort — and when they achieve O(n)
- **Stability:** What it means, why it matters for multi-key sorting, which algorithms are stable
- **Top-k selection:** Efficient retrieval of the k best results using a min-heap
- **Sorting in AI agents:** Result ranking, knowledge organization, and the recurring need for order

**Required Reading:**

- Cormen et al., *Introduction to Algorithms* (4th ed.), Chapters 6–9
- Sedgewick & Wayne, *Algorithms* (5th ed.), Chapters 2.1–2.5

**Discussion Questions:**

1. Timsort achieves O(n) on nearly-sorted data. Why is this important for AI agents, which frequently update and re-sort data? What kinds of data are naturally nearly-sorted?
2. The Ω(n log n) lower bound applies to comparison sorts. For non-comparison sorts, what information about the data is required, and when is it available in AI applications?
3. An AI agent must return the top 10 results from a million candidates. Compare the time and space complexity of sorting all million and taking the first 10, versus using a min-heap of size 10. Which is better, and under what conditions?

---

### ᚺ Lecture 7: Graphs — The Web of Relations

**Course:** AI103 — Data Structures & Algorithms
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

A graph is a collection of vertices (nodes) connected by edges (links). Graphs are the most general and most powerful of the standard data structures, subsuming arrays (paths), trees (rooted graphs without cycles), and hash tables (bipartite graphs between keys and values). They model social networks, road maps, the internet, protein interactions, knowledge bases, and — critically for this course — the structure of AI agent reasoning, planning, and memory.

Formally, a graph G = (V, E) consists of a set V of vertices and a set E of edges, where each edge connects a pair of vertices. In a **directed graph** (digraph), edges have direction: (u, v) means "there is a path from u to v" but not necessarily from v to u. In an **undirected graph**, edges have no direction: {u, v} means "u and v are connected." In a **weighted graph**, each edge has a numerical weight representing distance, cost, or capacity. In a **labeled graph**, vertices and edges can carry additional attributes.

The two standard representations of a graph are the **adjacency matrix** and the **adjacency list**. An adjacency matrix is a |V| × |V| matrix where entry (i, j) is 1 if there is an edge from vertex i to vertex j, and 0 otherwise (or the edge weight, in a weighted graph). This representation enables O(1) edge lookup but uses O(|V|²) space, which is wasteful for sparse graphs (where most possible edges are absent). An adjacency list stores, for each vertex, a list of its neighbors. This uses O(|V| + |E|) space — linear in the size of the graph — and enables efficient iteration over a vertex's neighbors, which is the most common operation in graph algorithms. In practice, adjacency lists are preferred for sparse graphs (which most real-world graphs are), and adjacency matrices are used when the graph is dense or when O(1) edge lookup is essential.

**Graph traversal** — visiting all reachable vertices — is the foundational operation on which all other graph algorithms build. **Breadth-first search (BFS)** explores the graph level by level: starting from a source node, it visits all neighbors, then all neighbors of neighbors, and so on. BFS explores in concentric circles outward from the source, guaranteeing that the first time a node is reached, it is via the shortest path (in an unweighted graph). BFS uses a queue data structure and runs in O(|V| + |E|) time. **Depth-first search (DFS)** explores as far as possible along each branch before backtracking, using a stack (or recursion) to keep track of the frontier. DFS is useful for detecting cycles, performing topological sorting, and finding connected components. It also runs in O(|V| + |E|) time.

**Shortest path algorithms** are perhaps the most practically important class of graph algorithms. **Dijkstra's algorithm** finds the shortest paths from a single source to all other vertices in a weighted graph with non-negative edge weights. It uses a priority queue to always process the closest unvisited vertex, and it runs in O((|V| + |E|) log |V|) time with a binary heap. **Bellman-Ford** handles graphs with negative edge weights (detecting negative cycles in O(|V| |E|) time). **Floyd-Warshall** finds shortest paths between all pairs of vertices in O(|V|³) time — useful when you need the full distance matrix. **A* search** augments Dijkstra's algorithm with a heuristic function that estimates the remaining distance to the goal, often reducing the number of vertices explored. A* is the algorithm of choice for pathfinding in AI — it is the engine behind GPS navigation, game AI, and robot motion planning.

In AI agent systems, graphs are everywhere. **Knowledge graphs** represent entities as vertices and relations as directed, labeled edges. The agent's understanding of "Paris is the capital of France" is stored as the triple (Paris, CAPITAL-OF, France) — a directed edge from the vertex "Paris" to the vertex "France" with label "CAPITAL-OF." Graph traversal over such a structure enables reasoning: to answer "What is the capital of France?", traverse from "France" along "CAPITAL-OF" edges. To answer "Is France in Europe?", traverse from "France" along "PART-OF" edges. This graph-structured reasoning is the foundation of the neuro-symbolic architectures that you will study in AI303 (Memory Systems for Persistent Agents).

**Task graphs** represent the dependencies between subtasks in a complex task. An agent planning a multi-step operation (e.g., "book a trip": research flights → compare prices → book flight → book hotel → confirm itinerary) constructs a directed acyclic graph (DAG) of subtasks, where edges represent dependencies. Topological sorting of this DAG yields a valid execution order. Parallel subtasks (research flights and research hotels) can be executed concurrently.

**State-space graphs** represent the possible configurations of an environment, with edges representing actions that transition between states. Search algorithms (BFS, DFS, A*) explore this graph to find a path from the initial state to a goal state. An AI agent that navigates a building, solves a puzzle, or manages a workflow is performing graph search on a state-space graph.

The Norse concept of **vefr** — a web or weave — is a direct parallel to the graph. The web of wyrd (*vefr orðinn*, the woven web) is the interconnected network of causes and effects that binds all events together. Every event is a node; every causal link is an edge; and the web of wyrd is the directed acyclic graph of fate. Graph search is the art of navigating this web — of finding a path through the interconnected nodes from where you are to where you want to be. An AI agent that plans, reasons, or navigates is doing exactly this: searching the web of cause and effect for a sequence of edges (actions) that leads from the current state (the present) to a goal state (the desired future).

**Minimum spanning trees (MSTs)** are another important class of graph algorithms. Given a weighted, connected, undirected graph, an MST is a subset of edges that connects all vertices with minimum total weight. **Kruskal's algorithm** sorts edges by weight and adds them one by one, skipping any that would create a cycle. **Prim's algorithm** grows the MST from a starting vertex, always adding the cheapest edge that connects the tree to a new vertex. Both run in O(|E| log |V|) time. MSTs are used in network design (connecting nodes with minimum cable), clustering (minimum spanning tree clustering), and as a preprocessing step for approximation algorithms.

**Network flow** algorithms find the maximum flow of material through a network from a source to a sink, subject to edge capacity constraints. The Ford-Fulkerson algorithm and its more efficient variants (Edmonds-Karp, Dinic's algorithm) are foundational in operations research and have applications in AI for resource allocation, matching problems, and cut-based graph partitioning.

**Key Topics:**

- **Graph representations:** Adjacency matrix vs. adjacency list, space and time tradeoffs
- **Graph traversal:** BFS and DFS, their properties and applications
- **Shortest path algorithms:** Dijkstra, Bellman-Ford, Floyd-Warshall, A* search
- **Applications in AI:** Knowledge graphs, task graphs, state-space graphs
- **Minimum spanning trees:** Kruskal's and Prim's algorithms
- **Network flow:** Maximum flow, Ford-Fulkerson, and applications

**Required Reading:**

- Cormen et al., *Introduction to Algorithms* (4th ed.), Chapters 22–26
- Sedgewick & Wayne, *Algorithms* (5th ed.), Chapters 4.1–4.4

**Discussion Questions:**

1. In a knowledge graph with millions of entities and billions of relations, which graph representation is most efficient? How would you store and query such a graph in practice?
2. A* search is both a graph algorithm and an AI search algorithm. What properties must the heuristic function satisfy for A* to be optimal? What happens if the heuristic overestimates?
3. The web of wyrd (*vefr orðinn*) is a DAG of causes and effects. How does this differ from a general graph that may contain cycles? What does the absence of cycles imply about the structure of fate?

---

### ᚾ Lecture 8: Graph Algorithms — Traversal, Shortest Paths, and Connectivity

**Course:** AI103 — Data Structures & Algorithms
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

In the previous lecture, we introduced graphs and their basic traversal algorithms (BFS and DFS). This lecture deepens the analysis, examining advanced graph algorithms that are essential for AI agent systems: connected components, topological sorting, strongly connected components, and the shortest path algorithms that underpin planning and navigation.

**Connected components** are the maximal subgraphs in which every vertex is reachable from every other vertex. In an undirected graph, finding connected components is straightforward: run BFS or DFS from an unvisited vertex, marking all reachable vertices as visited; then repeat for the next unvisited vertex. Each run discovers one connected component. In a directed graph, the situation is more complex: even if there is a path from *u* to *v*, there may not be a path from *v* to *u*. The **strongly connected components (SCCs)** of a directed graph are the maximal subgraphs in which every vertex is reachable from every other vertex via directed paths. Finding SCCs is the first step in analyzing the structure of any directed graph: web pages (which SCCs of the web graph form communities?), social networks (which groups are mutually reachable?), and dependency graphs (which modules depend on each other?).

**Kosaraju's algorithm** for finding SCCs works in three steps: (1) perform a DFS of the entire graph, pushing vertices onto a stack in order of completion; (2) compute the transpose of the graph (reverse all edge directions); (3) perform DFS on the transposed graph in the order defined by the stack from step 1. Each DFS tree in step 3 is an SCC. The algorithm runs in O(|V| + |E|) time, making it efficient for large graphs. **Tarjan's algorithm** is an alternative that finds SCCs in a single DFS pass, using a clever combination of discovery times and low-link values.

**Topological sorting** applies to directed acyclic graphs (DAGs) and produces a linear ordering of vertices such that for every directed edge (u, v), vertex u comes before vertex v. This is equivalent to scheduling tasks with dependencies: if task u must be completed before task v can begin, then u must come before v in the topological order. Topological sorting is performed by repeatedly removing vertices with no incoming edges (sources). If at any point no source exists but vertices remain, the graph contains a cycle and cannot be topologically sorted. In AI agent systems, topological sorting is used for task planning: given a set of tasks and their dependencies, the agent produces a valid execution order. This is the data structure behind every build system (make, npm, cargo), every course prerequisite system, and every project dependency graph.

**Strongly connected components and the condensation graph** provide a hierarchical view of a directed graph. The condensation graph — formed by contracting each SCC into a single node — is always a DAG, regardless of how cyclic the original graph was. This DAG represents the coarse structure of the graph: the SCCs are the "modules" or "clusters," and the edges between them are the "dependencies" or "information flows." For an AI agent analyzing a complex system (a codebase, a knowledge base, a social network), computing the SCCs and the condensation graph is the first step toward understanding the system's modular structure.

For **shortest paths in weighted graphs**, Dijkstra's algorithm maintains a set of visited vertices and a priority queue of unvisited vertices, keyed by their current shortest-path estimate. At each step, it extracts the vertex with the minimum estimate, relaxes all outgoing edges, and updates the estimates of neighboring vertices. The algorithm terminates when all vertices have been visited (or when the destination is reached, in the single-source, single-destination variant). The key insight is that the first time a vertex is extracted from the priority queue, its shortest-path estimate is guaranteed to be optimal — this is the "greedy choice property" that makes Dijkstra's algorithm correct.

**A* search** enhances Dijkstra's algorithm with a heuristic estimate *h(v)* of the remaining distance from vertex *v* to the goal. Instead of processing vertices in order of distance from the source (as Dijkstra does), A* processes vertices in order of *f(v) = g(v) + h(v)*, where *g(v)* is the known shortest-path cost from the source to *v* and *h(v)* is the estimated cost from *v* to the goal. When *h(v)* is **admissible** (never overestimates the true remaining distance) and **consistent** (satisfies the triangle inequality), A* is guaranteed to find the optimal path and is typically much faster than Dijkstra because it explores fewer nodes. A* is the standard pathfinding algorithm in robotics, game AI, and automated planning.

In AI systems, A* and its variants are used for **planning** (finding a sequence of actions that achieves a goal), **navigation** (finding the shortest physical path through a map), and **puzzle solving** (finding a sequence of moves that solves a Rubik's Cube, a sliding tile puzzle, or a game level). The quality of the heuristic determines the efficiency of the search: a perfect heuristic (h(v) = exact remaining distance) makes A* explore only the nodes on the optimal path, while a trivial heuristic (h(v) = 0) reduces A* to Dijkstra's algorithm. Designing good heuristics is an art — it requires domain knowledge and creative insight — and it is one of the central skills in AI search.

**Bidirectional search** runs two simultaneous searches: one forward from the source and one backward from the goal. The search terminates when the two frontiers meet. In theory, bidirectional search can reduce the search space from O(b^d) to O(b^(d/2)), where b is the branching factor and d is the depth of the solution — a quadratic improvement. In practice, bidirectional search is effective when the graph is structured such that the forward and backward frontiers are equally explorable.

**Key Topics:**

- **Connected components and SCCs:** Kosaraju's and Tarjan's algorithms, O(V+E) time
- **Topological sorting:** DAG scheduling, dependency resolution, and task planning
- **Condensation graph:** Modular structure discovery via SCC contraction
- **Dijkstra's algorithm:** Greedy shortest paths, priority queue implementation
- **A* search:** Heuristic-guided pathfinding, admissibility, consistency, optimality
- **Bidirectional search:** Meeting in the middle, quadratic savings

**Required Reading:**

- Cormen et al., *Introduction to Algorithms* (4th ed.), Chapters 22.5 (SCCs), 24 (Single-Source Shortest Paths), 25 (All-Pairs Shortest Paths)
- Russell & Norvig, *Artificial Intelligence: A Modern Approach* (8th ed.), Chapter 3.5 (A* Search)

**Discussion Questions:**

1. Topological sorting assumes the graph is a DAG. What should an AI agent do when its task graph contains a cycle (i.e., circular dependencies)? How can it detect and resolve cycles?
2. A* is guaranteed optimal when the heuristic is admissible. But designing admissible heuristics requires domain knowledge. How can an agent learn heuristics from experience, and what are the risks of using learned (potentially inadmissible) heuristics?
3. The condensation graph of SCCs is always a DAG. What does this tell us about the modular structure of complex systems? How can an AI agent use this structure to decompose a large problem into independent subproblems?

---

### ᛁ Lecture 9: Dynamic Programming — Breaking Problems into Pieces

**Course:** AI103 — Data Structures & Algorithms
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Dynamic programming (DP) is the algorithmic technique for solving problems by breaking them into overlapping subproblems, solving each subproblem once, and storing the solution for future reuse. The name is peculiar — "dynamic programming" was coined by Richard Bellman in the 1950s as a marketing term to make his research sound more impressive to his employers at RAND Corporation — but the technique is profoundly important. DP solves problems that would be exponential or worse by naive approaches in polynomial time, by identifying the recursive structure of the problem and exploiting it through **memoization** (top-down, storing results as they are computed) or **tabulation** (bottom-up, filling in a table of results in the right order).

The **two key properties** that make a problem amenable to DP are **optimal substructure** and **overlapping subproblems**. Optimal substructure means that the optimal solution to the problem contains optimal solutions to its subproblems. Overlapping subproblems means that the same subproblems are encountered repeatedly during the recursion. Without optimal substructure, there is no guarantee that combining optimal sub-solutions yields an optimal solution. Without overlapping subproblems, a simple divide-and-conquer approach would suffice — there is no need for memoization.

The canonical example of DP is the **Fibonacci sequence**. A naive recursive implementation computes fib(n) by calling fib(n-1) and fib(n-2), resulting in exponential time because the same values are computed repeatedly. Memoizing the results (storing them in a table after the first computation) reduces the time to O(n). Tabulating the results (computing fib(0), fib(1), fib(2), ... in order) also takes O(n) time and O(1) space if we only keep the two most recent values. This dramatic speedup — from exponential to linear — illustrates the power of DP.

The **longest common subsequence (LCS)** problem finds the longest sequence of characters that appears in both of two input sequences. Given two strings of length m and n, a naive approach would examine all 2^m subsequences of the first string, which is exponential. DP reduces this to O(mn) by defining f(i, j) = the length of the LCS of the first i characters of the first string and the first j characters of the second string, and filling in a table of size (m+1) × (n+1) using the recurrence: if the current characters match, f(i, j) = f(i-1, j-1) + 1; otherwise, f(i, j) = max(f(i-1, j), f(i, j-1)). LCS is used in **diff** tools (for comparing file versions), in **bioinformatics** (for comparing DNA sequences), and in **version control systems** (for merging changes).

The **knapsack problem** is another DP classic. Given n items, each with a weight and a value, and a knapsack with a weight capacity W, select items to maximize the total value without exceeding the capacity. A naive approach examines all 2^n subsets of items. DP reduces this to O(nW) by defining f(i, w) = the maximum value achievable using items 1 through i with capacity w. This is the 0/1 knapsack problem; the unbounded knapsack variant (where items can be selected multiple times) is also solvable by DP with a slight modification. The knapsack problem models resource allocation in AI agents: given limited compute, memory, or time, which tasks should the agent prioritize?

**Sequence alignment** (the Needleman-Wunsch algorithm for global alignment and the Smith-Waterman algorithm for local alignment) is a DP-based method for comparing biological sequences. Given two sequences, it finds the alignment that maximizes a score function (rewarding matches, penalizing mismatches and gaps). The DP table has dimensions (m+1) × (n+1), and each cell is filled based on its three neighbors. This algorithm is the foundation of modern bioinformatics, and its structure is identical to the LCS recurrence — a reminder that the same DP pattern appears across many domains.

**Bellman equations** and the broader framework of **Markov Decision Processes (MDPs)** bring DP into the domain of AI. An MDP is defined by a set of states, a set of actions, a transition function (which state results from taking which action in which state), and a reward function (the immediate reward for each state-action pair). The goal is to find a policy (a mapping from states to actions) that maximizes the expected cumulative reward. The **Bellman equation** decomposes this problem: the value of a state equals the immediate reward plus the discounted value of the next state, averaged over possible transitions. This recursive decomposition is precisely the optimal substructure that DP exploits. **Value iteration** and **policy iteration** are DP algorithms that solve MDPs by iteratively applying the Bellman equation until convergence. These algorithms are the foundation of **reinforcement learning** — the paradigm that enables AI agents to learn from interaction with their environment.

The Norse concept of **þverráð** — crosswise counsel, working across multiple directions simultaneously — captures the spirit of DP. A DP algorithm doesn't solve the whole problem at once; it works on small pieces simultaneously, building up the solution by combining optimal sub-solutions from multiple directions. The pattern of filling in a DP table — working row by row, column by column, simultaneously satisfying constraints from the left, from above, and from the diagonal — is þverráð in action: crosswise computation that builds the global optimum from local pieces.

**Key Topics:**

- **Optimal substructure and overlapping subproblems:** The two properties that make DP applicable
- **Memoization vs. tabulation:** Top-down (recursive with caching) vs. bottom-up (iterative table-filling)
- **Classic DP problems:** Fibonacci, LCS, knapsack, sequence alignment
- **Bellman equations and MDPs:** DP in the domain of sequential decision-making
- **Value iteration and policy iteration:** Solving MDPs for optimal policies
- **Resource allocation in agents:** Knapsack and its variants for compute, memory, and time budgeting

**Required Reading:**

- Cormen et al., *Introduction to Algorithms* (4th ed.), Chapters 14–15
- Sutton & Barto, *Reinforcement Learning: An Introduction* (2nd ed., 2038), Chapters 3–4

**Discussion Questions:**

1. DP requires optimal substructure. Give an example of a problem that does NOT have optimal substructure. How would you solve such a problem?
2. An AI agent has limited compute time and must decide which tasks to execute. Model this as a knapsack problem. What are the items, the weights, the values, and the capacity? What are the assumptions this model makes?
3. The Bellman equation decomposes the value of a state into immediate reward plus discounted future value. What happens when the discount factor γ → 0? When γ → 1? What do these extremes mean for an agent's behavior?

---

### ᛃ Lecture 10: Algorithm Design Paradigms — Divide, Conquer, Greed, and Backtrack

**Course:** AI103 — Data Structures & Algorithms
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Beyond specific data structures and algorithms lies a higher level of abstraction: the **paradigm** or general strategy for designing algorithms. A paradigm is not an algorithm but a way of thinking about problems — a template that can be instantiated in many specific forms. The four major paradigms — divide and conquer, greedy, dynamic programming, and backtracking — cover the vast majority of algorithmic problems, and understanding them enables you to approach unfamiliar problems with a systematic toolkit.

**Divide and conquer** decomposes a problem into smaller subproblems of the same type, solves each subproblem recursively, and combines the solutions. Merge sort divides the array in half, sorts each half, and merges the two sorted halves. Quicksort partitions the array around a pivot, recursively sorts each partition, and concatenates the results. Binary search divides the search space in half and recurses into the half that contains the target. Strassen's algorithm multiplies matrices by dividing them into submatrices and combining the products in a way that reduces the number of recursive multiplications from 8 to 7. The master theorem provides a general framework for analyzing divide-and-conquer algorithms: if a problem of size n is divided into a subproblems of size n/b, and the combine step takes O(n^d) time, then the total running time is O(n^(log_b a)) if d < log_b(a), O(n^d log n) if d = log_b(a), and O(n^d) if d > log_b(a).

**The greedy paradigm** makes locally optimal choices at each step, hoping that these will lead to a globally optimal solution. Greedy algorithms are simple, fast, and often surprisingly effective — but they are not always correct. Kruskal's and Prim's algorithms for minimum spanning trees are greedy, and they produce correct results because the MST problem has the **greedy-choice property**: a locally optimal choice (the cheapest edge) is always part of a globally optimal solution. Dijkstra's algorithm is greedy (always processing the closest unvisited vertex). Huffman coding is greedy (always merging the two least frequent symbols). But greedy algorithms fail for problems that lack the greedy-choice property: the naive greedy approach to the knapsack problem (always taking the item with the highest value-to-weight ratio) does not produce optimal results, because a locally expensive item may be part of a globally optimal solution that includes several smaller, less valuable items.

In AI agent systems, greedy algorithms are used for **real-time decision-making**, where time constraints make exhaustive search infeasible. An agent that must choose an action in real time cannot afford to explore all possible futures; it makes the locally best choice and hopes for the best. This is the principle behind **greedy action selection** in reinforcement learning (choosing the action with the highest estimated value), **greedy task scheduling** (always executing the highest-priority task), and **greedy resource allocation** (always assigning a resource to the most deserving request). The risk of greed is myopia: optimizing for immediate reward may sacrifice long-term value. This is why reinforcement learning algorithms like ε-greedy exploration occasionally take random actions — to avoid getting stuck in locally optimal but globally suboptimal strategies.

**Backtracking** is the paradigm for systematic search through a potentially exponential space of possibilities. Given a set of constraints and a search space, backtracking enumerates partial solutions, checking at each step whether the current partial solution is still feasible (consistent with all constraints). If it is, the algorithm extends the partial solution by one more choice. If it is not, the algorithm backtracks — undoes the most recent choice and tries the next alternative. Backtracking solves constraint satisfaction problems (CSPs), combinatorial optimization problems, and puzzle solving (N-queens, Sudoku, graph coloring). In AI, backtracking is the engine behind **systematic planning** (enumerating possible action sequences), **constraint propagation** (pruning infeasible branches early), and **search with pruning** (cutting off branches that cannot lead to a better solution than the current best).

**Branch and bound** enhances backtracking with a bounding function that estimates the best possible solution reachable from the current partial solution. If the bound is worse than the current best solution, the branch can be pruned without further exploration. This dramatically reduces the search space for many problems. The traveling salesman problem (TSP), while NP-hard in general, can often be solved exactly for instances with hundreds of cities using branch and bound with good bounds. In AI, branch and bound is used for **optimal planning** (finding the shortest plan, not just any plan) and **game AI** (finding the best move in games like chess and Go).

The interaction between these paradigms is rich. Many algorithms combine multiple strategies: merge sort is divide and conquer, but the merge step is greedy (always taking the smaller element). Dijkstra's algorithm is greedy, but it uses a priority queue (heap) data structure. A* search combines greedy heuristic guidance with branch-and-bound pruning. Dynamic programming decomposes problems into subproblems (like divide and conquer) but stores solutions to overlapping subproblems (unlike divide and conquer, which re-solves subproblems independently).

The craft of algorithm design is knowing which paradigm to apply to a given problem. This is an acquired skill, developed through practice and pattern recognition. As you solve more problems, you begin to see structural patterns that suggest paradigms: problems with **optimal substructure and overlapping subproblems** suggest DP; problems with the **greedy-choice property** suggest greedy algorithms; problems with **exponential search spaces and constraints** suggest backtracking with pruning; problems that can be **recursively decomposed** suggest divide and conquer. The best algorithm designers are not those who memorize the most algorithms, but those who can recognize which paradigm fits a new problem and instantiate it effectively.

The Norse god Týr exemplifies a different kind of paradigm — the willingness to sacrifice for a larger goal. When the gods needed to bind the wolf Fenrir, Týr placed his hand in the wolf's mouth as a pledge of good faith, knowing that Fenrir would bite it off when the-binding proved the gods' deception. This is the greedy choice in its deepest form: a local sacrifice (Týr's hand) for a global gain (the binding of a world-threatening force). But Týr's choice was also informed by the constraint that any other approach would fail — the wolf could only be bound through a combination of deception and sacrifice. The lesson for algorithm designers is that the optimal strategy is not always obvious, and sometimes the globally best solution requires making a locally costly choice that seems suboptimal in the short term.

**Key Topics:**

- **Divide and conquer:** Merge sort, quicksort, binary search, Strassen's algorithm
- **The greedy paradigm:** Greedy-choice property, when greed works, when it fails
- **Greedy algorithms in AI:** Real-time decision-making, action selection, scheduling
- **Backtracking:** Constraint satisfaction, puzzle solving, systematic search
- **Branch and bound:** Pruning with bounds, TSP, optimal planning
- **Paradigm selection:** Recognizing which approach fits a given problem

**Required Reading:**

- Cormen et al., *Introduction to Algorithms* (4th ed.), Chapters 4 (Divide and Conquer), 15 (Greedy Algorithms), 16 (Amortized Analysis)
- Skiena, *The Algorithm Design Manual* (3rd ed.), Chapters 4–8

**Discussion Questions:**

1. Greedy algorithms are fast but not always correct. How can you determine whether a problem has the greedy-choice property? Give an example of a problem where greed fails, and explain why.
2. Backtracking with pruning can solve problems that are theoretically exponential. What makes pruning effective? What properties must a problem have for pruning to significantly reduce the search space?
3. An AI agent must make decisions in real time (under time pressure). When is a greedy strategy appropriate, and when should the agent invest more time in backtracking search? How can the agent decide?

---

### ᛇ Lecture 11: Computational Complexity — The Limits of Computation

**Course:** AI103 — Data Structures & Algorithms
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Not all problems can be solved efficiently. This is not a statement about our current knowledge or technology; it is a fundamental mathematical fact about the nature of computation. The theory of computational complexity classifies problems by how hard they are — not in the sense of how much effort is required to code a solution, but in the sense of how the resources required (time and space) scale with the size of the input. Understanding these limits is essential for AI engineers because it tells us which problems are tractable (solvable in polynomial time), which are intractable (requiring exponential time), and which are undecidable (having no algorithmic solution at all).

The class **P** (polynomial time) consists of all decision problems (problems with yes/no answers) that can be solved by a deterministic Turing machine in polynomial time. Sorting, searching, shortest paths, matrix multiplication, and many other problems we have studied are in P — they can be solved efficiently. The class **NP** (nondeterministic polynomial time) consists of all decision problems whose solutions can be *verified* in polynomial time, even if finding the solution may take exponential time. Equivalently, NP is the class of problems that can be solved by a nondeterministic Turing machine in polynomial time — a hypothetical machine that can explore all possible solutions in parallel and accept if any branch finds a valid solution.

The question of whether P = NP — whether every problem whose solution can be verified in polynomial time can also be solved in polynomial time — is the most famous open problem in computer science and one of the seven Millennium Prize Problems. Most computer scientists believe that P ≠ NP: that there exist problems in NP that cannot be solved in polynomial time. If P = NP, then many problems currently believed to be intractable — including integer factorization (the basis of RSA encryption), the traveling salesman problem, and protein folding — would have efficient solutions, transforming cryptography, optimization, and computational biology overnight.

**NP-hard** problems are those that are at least as hard as any problem in NP — if you could solve an NP-hard problem in polynomial time, you could solve every problem in NP in polynomial time. **NP-complete** problems are both in NP and NP-hard; they are the hardest problems in NP. The Cook-Levin theorem (1971) proved that the Boolean satisfiability problem (SAT) is NP-complete, establishing the first member of this class. Subsequently, Richard Karp (1972) showed that 21 other problems — including graph coloring, the knapsack problem, and the traveling salesman problem — are also NP-complete, by reducing SAT to each of them polynomially. This network of reductions demonstrated that NP-completeness is not a rare property but a widespread phenomenon: hundreds of important problems are NP-complete.

For AI agent engineers, the practical implication is clear: when you encounter an NP-complete problem, you must choose one of three strategies. **Approximation algorithms** find solutions that are provably close to optimal (e.g., a solution within a factor of 2 of the optimal). **Heuristics** find good solutions quickly without guarantees (e.g., genetic algorithms, simulated annealing, greedy algorithms). **Exact algorithms** find the optimal solution but may take exponential time on worst-case inputs (e.g., branch and bound, integer linear programming). The choice depends on the application: if you need a provably optimal solution (e.g., in circuit design or mission-critical scheduling), exact algorithms are necessary; if you need a good-enough solution quickly (e.g., in real-time path planning or recommendation systems), heuristics are appropriate.

**Reductions** are the tool that enables complexity analysis. To show that problem A is at least as hard as problem B, you construct a polynomial-time reduction from B to A — a function that transforms any instance of B into an instance of A such that the answer to A gives the answer to B. This proves that if A could be solved efficiently, then B could also be solved efficiently (by reducing B to A and solving A). Reductions are used both to prove NP-completeness (by reducing a known NP-complete problem to a new problem) and to design algorithms (by reducing a new problem to a well-studied problem for which efficient algorithms exist).

The theory of **undecidability** defines even more fundamental limits. The **halting problem** — given a program and its input, determine whether the program will eventually halt or run forever — was proved undecidable by Alan Turing in 1936. No algorithm can solve the halting problem for all possible program-input pairs. This is not a limitation of our current understanding; it is a logical impossibility. The proof is by self-reference: if a halting-detecting algorithm existed, it could be used to construct a contradiction (a program that halts if and only if it doesn't halt). This result has profound implications for AI: there is no general algorithm for verifying that an AI agent will terminate, for proving that it will not produce harmful outputs, or for determining whether it will eventually achieve its goal. These are not engineering challenges that can be overcome with more compute or better algorithms; they are fundamental limits of computation.

For AI agents, undecidability manifests in practical form. **Rice's theorem** (1953) generalizes the halting problem: any non-trivial property of the behavior of programs (i.e., any property that is true of some programs and false of others) is undecidable. This means that there is no general algorithm for determining whether an AI agent's behavior satisfies a given specification, whether two agents are behaviorally equivalent, or whether an agent's goal is achievable. These results do not mean that verification is impossible in practice (useful heuristics and bounded verifiers exist), but they do mean that no complete, general solution exists.

The Norse concept of **Ragnarök** — the inevitable, insurmountable fate that even the gods cannot escape — parallels the limits of computation. Just as the gods cannot prevent Ragnarök, no algorithm can solve the halting problem, and no polynomial-time algorithm is known for NP-complete problems. These are the computational fates — the boundaries that define what is and is not achievable through algorithmic means. Understanding these boundaries is not pessimistic; it is empowering. An engineer who knows what is impossible can focus their efforts on what is possible, choosing approximation, heuristics, or bounded solutions instead of chasing impossibility.

**Key Topics:**

- **P and NP:** Polynomial-time solvable vs. polynomial-time verifiable problems
- **The P vs. NP question:** The most important open problem in computer science
- **NP-hardness and NP-completeness:** The hardest problems in NP, Cook-Levin, Karp's 21 problems
- **Strategies for NP-hard problems:** Approximation algorithms, heuristics, exact algorithms with exponential worst case
- **Reductions:** Polynomial-time reductions, NP-completeness proofs, algorithmic design
- **Undecidability:** The halting problem, Rice's theorem, and implications for AI verification

**Required Reading:**

- Cormen et al., *Introduction to Algorithms* (4th ed.), Chapters 34–35
- Sipser, M. *Introduction to the Theory of Computation* (4th ed., 2039), Chapters 7–9
- Garey, M.R. & Johnson, D.S. *Computers and Intractability* (reprint, 2037), Chapters 1–3

**Discussion Questions:**

1. If P = NP were proved tomorrow, what would change in AI? What wouldn't change? How would the field of AI agent automation be affected?
2. The halting problem is undecidable in general, but many programs can be proved to halt using restricted verification techniques. How do these techniques work, and what are their limitations?
3. Rice's theorem says that no non-trivial behavioral property of programs is decidable. Does this mean that AI safety verification is impossible? How do engineers work around this theoretical impossibility in practice?

---

### ᛜ Lecture 12: Data Structures and Algorithms in AI Agent Systems — A Synthesis

**Course:** AI103 — Data Structures & Algorithms
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

In this final lecture, we bring together every thread woven throughout the course — arrays, linked lists, stacks, queues, trees, hash tables, graphs, sorting, searching, dynamic programming, greedy algorithms, backtracking, and complexity theory — and integrate them into a unified picture of how data structures and algorithms function within AI agent systems. This is not a review; it is a synthesis, showing how the foundational concepts you have learned compose into the architectures that make intelligent systems work.

Every AI agent, from the simplest chatbot to the most sophisticated autonomous system, operates through a cycle of **perceive, reason, act, and learn**. Each stage of this cycle relies on specific data structures and algorithms:

- **Perceive** — receiving and processing observations from the environment. The agent receives text, images, audio, or sensor data as input. Tokenization converts raw text into an array of tokens. Embedding lookups (hash table + vector operations) convert tokens into dense vectors. Convolutional and attention operations process these vectors through neural network layers. The result is a structured representation of the input: an array of embeddings, a stack of processed features, and a set of identified entities stored in a knowledge graph.

- **Reason** — drawing inferences, making plans, and evaluating options. The agent's reasoning engine queries its knowledge graph (graph traversal), retrieves relevant memories (hash table + similarity search), decomposes the task into subtasks (tree construction with topological sorting), and searches for a plan (A* search or backtracking with pruning). Dynamic programming may be used to compute optimal sub-policies, and greedy strategies may be used for real-time decisions when full search is too expensive.

- **Act** — executing the chosen action in the environment. The agent's action executor translates its plan into API calls (modeled as a sequence of operations, stored in a queue), monitors the results (using a stack for undo/rollback capability), and updates its internal state (modifying the knowledge graph and hash tables that constitute its world model). Priority queues ensure that the most important tasks are handled first.

- **Learn** — updating the agent's models based on experience. The agent stores new experiences in its episodic memory (a time-ordered dequeue), extracts patterns (using DP or statistical learning), updates its semantic knowledge (modifying the knowledge graph), and refines its procedural skills (updating hash tables and trees that encode learned behaviors). The agent's learning loop is itself a data structure — a priority queue of experiences, sorted by recency and importance, that determines what is learned first.

The **agent's memory system** is a mosaic of data structures. **Episodic memory** (what happened when) is a temporal dequeue — events are added at the back and expired at the front, with recent events more accessible. **Semantic memory** (facts about the world) is a knowledge graph — entities as vertices, relations as edges, with graph traversal for reasoning. **Procedural memory** (learned skills) is a hash table mapping situations to actions — a lookup table that improves with experience. **Working memory** (the current context) is a bounded array — a fixed-size buffer that holds the most recent and relevant information, often implemented as a circular buffer or a priority queue.

The **agent's planning system** is a search algorithm operating on a graph. The state space is represented as a directed graph where vertices are states and edges are actions. A* search, powered by a heuristic function (often learned from experience) and a priority queue (for the open set of nodes), finds the shortest path from the current state to the goal state. When A* is too slow (because the state space is too large), greedy strategies or Monte Carlo tree search provide approximate solutions. When the environment is dynamic (other agents act simultaneously), the planning problem becomes a game tree, and the agent must use **minimax** or **alpha-beta pruning** to reason about adversarial actions.

The **agent's communication system** relies on message queues, socket buffers, and protocol parsers. When multiple agents coordinate, they exchange messages through a distributed message queue (like Kafka or RabbitMQ), which is implemented as a persistent, replicated, and partitioned data structure that guarantees delivery ordering and at-least-once semantics. The Model Context Protocol (MCP), which standardizes tool interfaces for agents, is built on top of these data structures: each tool invocation is a message in a queue, each response is a message in a response queue, and each agent maintains a conversation context stored as a dynamic array of messages.

Throughout this course, we have encountered the Norse concept of **ný ráð** — new counsel, new solutions — in many forms. Sorting is ný ráð for finding order in chaos. Hash tables are ný ráð for instant access to knowledge. Graph algorithms are ný ráð for navigating webs of causation and dependence. Dynamic programming is ný ráð for breaking problems into manageable pieces. And complexity theory is ný ráð for understanding what is possible and what is not — for knowing when to seek an optimal solution and when to settle for a good-enough approximation.

The Norns weave at the foot of Yggdrasil. Urðr spins the thread of the past — the stored data, the historical context. Verðandi measures the thread of the present — the current state, the active computation. Skuld cuts the thread of the future — the decision, the output, the action. Every data structure is a way of organizing Urðr's thread. Every algorithm is a way of measuring Verðandi's thread. Every complexity bound is a way of understanding Skuld's cut — knowing which futures are reachable and which are out of reach. To master data structures and algorithms is to work alongside the Norns, weaving threads of computation into patterns of intelligence.

As you proceed through this degree program, you will encounter ever more complex systems built on these foundations. Neural networks are composed of matrix operations (arrays). Attention mechanisms are composed of hash-table-like lookups (queries, keys, values). Transformer architectures are composed of trees (the attention pattern hierarchy) and sequences (the token order). Agent systems are composed of graphs (knowledge bases), queues (task schedulers), and priority queues (planning systems). The data structures and algorithms you have learned in this course are not prerequisites that you can forget — they are the building blocks of every system you will build.

Weave well. The strength of the tapestry depends on the strength of each thread.

**Key Topics:**

- **The agent cycle:** How perceive, reason, act, and learn use specific data structures and algorithms
- **Agent memory systems:** Episodic (dequeue), semantic (graph), procedural (hash table), working (bounded array)
- **Agent planning:** A* search, greedy strategies, Monte Carlo tree search, minimax with alpha-beta pruning
- **Agent communication:** Message queues, protocol parsers, MCP, distributed data structures
- **Ný ráð — new counsel:** Each data structure and algorithm as a solution to a specific kind of problem
- **The Norns and the threads of computation:** Urðr (data), Verðandi (computation), Skuld (decisions)

**Required Reading:**

- Russell & Norvig, *Artificial Intelligence: A Modern Approach* (8th ed.), Chapters 3–5 (Search), 12–13 (Planning)
- Yao, S. et al. "ReAct: Synergizing Reasoning and Acting in Language Models" (2023), *ICLR*
- University of Yggdrasil AI Agent Systems Group: "Memory Architectures for Persistent Agents" (2039), *UoY Technical Report* No. 37

**Discussion Questions:**

1. Design the data structure architecture for a persistent AI agent that must maintain episodic, semantic, and procedural memory. What data structures would you use for each type of memory? How would you integrate them?
2. An agent that uses A* for planning must have a heuristic function. How should this heuristic be constructed? Should it be hand-coded, learned from data, or some combination? What are the risks of an inadmissible heuristic?
3. The Norns weave threads of past, present, and future. In what sense does an agent's memory system (past), reasoning engine (present), and planning algorithm (future) mirror this structure? Can an agent's decision-making be improved by explicitly modeling these three temporal dimensions?

---

## Final Examination Preparation

### Course: AI103 — Data Structures & Algorithms

**Format:** Choose 4 of the following 8 questions. Write a well-structured essay (800–1200 words) for each. Include pseudocode where appropriate. Analyze time and space complexity where relevant.

---

**Question 1:** Compare and contrast arrays and linked lists, including their time complexities for common operations, cache locality properties, and practical performance considerations. For each of the following AI agent operations, identify the optimal data structure and explain why: (a) storing conversation context, (b) implementing a task queue, (c) maintaining a knowledge base, (d) implementing an undo stack. Analyze the time complexity of each operation.

**Question 2:** Explain the property that distinguishes a binary search tree from a regular binary tree, and analyze the worst-case and average-case time complexities for search, insertion, and deletion. Explain why self-balancing trees (AVL, red-black) are necessary and how they maintain balance. Describe a scenario in an AI agent system where a BST would be preferred over a hash table, and vice versa.

**Question 3:** Prove that any comparison-based sorting algorithm requires Ω(n log n) comparisons in the worst case. Then describe a scenario where O(n) sorting is possible and explain what additional information about the data makes this possible. Analyze the time and space complexity of counting sort and radix sort. When should an AI agent use a comparison sort vs. a non-comparison sort?

**Question 4:** Implement BFS and DFS for graph traversal, and analyze their time complexities. Then explain how BFS can be modified to find shortest paths in unweighted graphs and how Dijkstra's algorithm extends this to weighted graphs. Describe a scenario in an AI agent system where BFS (or an unweighted shortest path algorithm) would be preferred over Dijkstra, and vice versa. What are the tradeoffs?

**Question 5:** A* search uses a heuristic function h(n) to guide search toward the goal. Explain the conditions under which A* is optimal (admissibility and consistency). Design a heuristic function for each of the following domains and prove whether it is admissible: (a) pathfinding on a 2D grid, (b) solving a sliding tile puzzle, (c) finding the minimum number of actions to achieve a goal in a planning domain. Discuss the tradeoff between heuristic accuracy and computational cost.

**Question 6:** Explain dynamic programming and its two key properties (optimal substructure and overlapping subproblems). Solve the following problem using DP: given an AI agent that can perform n different types of actions, each with a resource cost c[i] and a utility value u[i], and a total resource budget of C, find the combination of actions that maximizes total utility without exceeding the budget. Analyze the time and space complexity of your solution. How does this relate to the knapsack problem?

**Question 7:** Define P, NP, NP-hard, and NP-complete. Explain the significance of the P vs. NP question for AI. Choose an NP-complete problem and describe three approaches to solving it in practice: (a) an exact algorithm with exponential worst case, (b) an approximation algorithm with a provable bound, and (c) a heuristic with no guarantee. Under what conditions would an AI agent choose each approach?

**Question 8:** Design the complete data structure architecture for a persistent AI agent that must: (a) maintain a conversation history of up to 100k messages, (b) store a knowledge base of 10 million facts, (c) manage a task queue with priority ordering, (d) cache the results of expensive computations, and (e) support efficient similarity search over embeddings. For each component, identify the data structure(s) used, analyze the time complexity of the dominant operations, and explain how the components interact. Draw the architecture and describe the data flow.

---

*End of AI103 Course Materials*

*Every data structure is a vessel; every algorithm, a path. Weave them well.* ᛟ