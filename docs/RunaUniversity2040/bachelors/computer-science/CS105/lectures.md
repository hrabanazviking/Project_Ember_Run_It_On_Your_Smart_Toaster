# CS105: Data Structures & Algorithms I
## Bachelor of Science in Computer Science — University of Yggdrasil, 2040

**Credits:** 4
**Prerequisites:** CS101 (Introduction to Programming), CS102 (Discrete Mathematics), CS103 (Programming Fundamentals — co-requisite)
**Description:** The foundational course in algorithmic thinking. Covers asymptotic analysis (Big-O, Ω, Θ), fundamental data structures (arrays, linked lists, stacks, queues, hash tables, binary search trees, heaps), and core algorithms (searching, sorting, selection, graph traversal). Emphasis on correctness proofs, worst-case and average-case analysis, and the practical tradeoffs that no amount of theory can fully capture. Programming assignments in Rust and Python.

---

## Lectures

### Lecture 1: Algorithmic Thinking — What It Means to Compute Well

**Course:** CS105 — Data Structures & Algorithms I
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

An algorithm is not merely a sequence of instructions. It is a solution, formalized — a finite, unambiguous procedure that transforms input to output and terminates. This opening lecture develops the conceptual framework of algorithmic thinking: the distinction between a problem and its instances, the notion of algorithmic efficiency, and the central question that drives the course: "Can we do better?" We introduce asymptotic analysis as the mathematical language in which answers to that question are expressed.

#### Lecture Notes

A *problem* defines a relationship between input and output. Sorting: given a sequence of n elements with a total order, produce a permutation in non-decreasing order. Searching: given a set and a query element, determine whether the query is in the set. A problem is a specification; an *algorithm* is a concrete procedure that satisfies the specification for every possible input. The same problem admits many algorithms. Sorting can be accomplished by insertion sort, merge sort, quicksort, heapsort, timsort — each with different performance characteristics. The craft of algorithm design begins with recognizing that multiple algorithms exist for the same problem and ends with choosing the right one for the constraints at hand.

*Efficiency* is measured in resources consumed: time (how many operations), space (how much memory), energy (increasingly relevant in 2040, where the carbon cost of computation is priced), and communication (for distributed algorithms). We focus primarily on time, measured not in seconds (which depend on the hardware) but in abstract *operations* — the number of "primitive steps" as a function of input size n. The constant factors matter in practice (a factor of 2 can mean the difference between a responsive UI and a sluggish one), but *asymptotic* behavior — how the running time grows as n → ∞ — is the first-order concern. If algorithm A takes n² steps and algorithm B takes n log n steps, then for n > 10⁶, B will be faster regardless of constant factors on any plausible hardware.

*Asymptotic notation* formalizes this intuition. O(g(n)) ("big-O") is an *upper bound*: f(n) ∈ O(g(n)) if there exist constants c > 0 and n₀ such that f(n) ≤ c·g(n) for all n ≥ n₀. Intuitively: f grows no faster than g. Ω(g(n)) ("big-Omega") is a *lower bound*: f(n) ∈ Ω(g(n)) if f(n) ≥ c·g(n) for large n. Θ(g(n)) ("big-Theta") is a *tight bound*: both O and Ω. We prove membership using the definition: to show 3n² + 2n + 1 ∈ O(n²), we find c = 6 and n₀ = 1 (since 3n² + 2n + 1 ≤ 3n² + 2n² + n² = 6n² for n ≥ 1). The strategic choice of c and n₀, while initially mysterious, becomes second nature with practice.

We emphasize *common growth rates* and their real-world implications. O(1): constant time — the holy grail (hash table lookup, array indexing). O(log n): logarithmic — doubles when n squares (binary search, balanced tree operations). O(n): linear — proportional to input (scanning an array). O(n log n): linearithmic — the sweet spot for comparison-based sorting (merge sort, heapsort). O(n²): quadratic — feasible for n up to ~10⁴ (simple sorting, naive matrix multiplication). O(2ⁿ): exponential — feasible only for n up to ~30 (brute-force subset enumeration, the reason NP-completeness matters). O(n!): factorial — feasible only for n up to ~12 (brute-force TSP). These are not abstract categories; they are the difference between "instant" and "the heat death of the universe."

The lecture closes with a caution: asymptotic analysis is a model, not reality. It ignores constant factors, memory hierarchy effects (a O(n²) algorithm with excellent cache locality can beat a O(n log n) algorithm with poor locality for moderate n), and hardware-specific optimizations. In 2040, the Yggdrasil-9's heterogeneous architecture means that the "best" algorithm depends on which device is executing it — an O(n²) algorithm on the GPU might beat an O(n log n) algorithm on the CPU for n up to 10⁶. Algorithmic analysis provides the asymptotic landscape; engineering judgment fills in the details.

#### Key Concepts
- Problem vs. algorithm: specification vs. implementation
- Efficiency: time, space, energy, communication
- Asymptotic analysis: O, Ω, Θ — formal definitions and proof technique
- Common growth rates: O(1), O(log n), O(n), O(n log n), O(n²), O(2ⁿ), O(n!)
- The limits of asymptotic analysis: constant factors, memory hierarchy, hardware heterogeneity
- The central question: "Can we do better?"

#### Required Reading
- Cormen, T.H., Leiserson, C.E., Rivest, R.L., and Stein, C. *Introduction to Algorithms* (CLRS), 5th ed. (2038), Chapters 1–3
- Knuth, D.E. *The Art of Computer Programming*, Volume 1, 4th ed. (2040), Chapter 1 (Basic Concepts) — for Knuth's unmatched depth and the origin of many algorithmic ideas
- Sedgewick, R. and Wayne, K. *Algorithms*, 5th ed. (2039), Chapter 1 (Fundamentals)

#### Discussion Questions
1. "f(n) ∈ O(g(n))" is often written as "f(n) = O(g(n))." Why is this notation abusive? What property of equality does it violate? Why has the abuse persisted?
2. A O(n²) algorithm on a GPU runs 100× faster than a O(n log n) algorithm on a CPU for n = 10⁵. Which is "better"? What additional information do you need to make this judgment?
3. If P = NP (as some 2040 researchers suspect, though no proof exists), would the distinction between polynomial and exponential time remain useful? What other distinctions might become important?

#### Practice Problems
- Prove from the definition: 5n³ - 2n² + n - 7 ∈ O(n³). Find explicit c and n₀.
- Rank the following functions by asymptotic growth rate (slowest to fastest): log n, n, n log n, n², n² log n, 1.5ⁿ, n!, log log n, √n.
- Example: f(n) = n² for even n, f(n) = n for odd n. Is f(n) ∈ O(n²)? Is f(n) ∈ Ω(n)? Is f(n) ∈ Θ(n)? Is f(n) ∈ Θ(n²)?

---

### Lecture 2: Arrays, Linked Lists, and the Memory of Sequences

**Course:** CS105 — Data Structures & Algorithms I
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

The simplest data structure — a sequence of elements — admits two fundamentally different implementations: the array (contiguous memory, O(1) access, O(n) insertion/deletion) and the linked list (dispersed memory, O(n) access, O(1) insertion/deletion at known positions). This lecture develops both, analyzes their operations, and introduces the *amortized analysis* that explains why dynamic arrays (like Rust's `Vec` and Python's `list`) achieve O(1) amortized push despite occasional O(n) reallocations.

#### Lecture Notes

An *array* stores elements in a contiguous block of memory. Element i is at address `base + i × size`. This simple address arithmetic gives arrays their defining strength: *constant-time random access* — to read or write any element, compute its address, dereference. No traversal, no pointer chasing. This is why arrays underpin virtually every high-performance data structure: hash tables use arrays of buckets, heaps use arrays for tree representation, and matrices use arrays (or arrays of arrays) for dense storage.

But contiguity has a cost. Inserting an element at position k requires shifting elements k through n-1 one position to the right, which takes O(n - k) = O(n) time. Deleting requires shifting left. A *dynamic array* (Rust's `Vec<T>`, Python's `list`) mitigates the insertion cost for the common case of appending to the end: it allocates more capacity than currently used, and when the capacity is exhausted, it allocates a new, larger block (typically 2× the size) and copies all elements. The copy is O(n), but it happens rarely. The *amortized analysis* of dynamic arrays is a classic: with doubling, the total cost of n push operations is at most 3n (each element is copied at most log₂ n times, sum of geometric series 1 + 2 + 4 + ... = O(n)). Thus, each push costs O(1) *amortized* — the average over any sequence of n operations is constant.

A *linked list* takes the opposite approach: each element (a *node*) is allocated separately and linked to its successor (and predecessor, for doubly-linked lists) through pointers. Insertion at the front (or at any position where you have a reference to the predecessor node) is O(1): allocate a node, adjust pointers. No shifting. Deletion is similarly O(1). The cost: O(n) random access — to reach element k, you must traverse k nodes from the head. Linked lists also suffer from poor cache locality (nodes are scattered in memory) and pointer overhead (each node stores 1–2 pointers in addition to its data). In 2040, the cache penalty of pointer chasing is so severe (L1 cache miss: ~10 cycles; L2: ~40; L3: ~150; DRAM: ~300) that linked lists are rarely the right choice for performance-critical code. Yet they remain fundamental: they are the substrate of functional programming's cons lists, the implementation of free lists in memory allocators, and the structure behind adjacency lists in graph representations.

We compare the two approaches through the lens of the *abstract data type* (ADT) — the List ADT, which specifies operations (insert, delete, access, search) without committing to an implementation. The choice between array and linked list is a choice about which operations are common and which are rare. An algorithm that accesses elements by index frequently and mutates rarely should use an array. An algorithm that inserts and deletes at the front frequently (e.g., a queue implemented as a linked list with head and tail pointers) should use a linked list. An algorithm that does both? Consider a balanced tree, a skip list, or a rope — data structures that blend array and linked-list properties, which we will encounter in CS201.

We close with Rust-specific considerations. Rust's `Vec<T>` is a heap-allocated dynamic array with ownership. Rust's `LinkedList<T>` (from `std::collections`) is a doubly-linked list — but it is rarely used, because `VecDeque<T>` (a ring buffer, providing O(1) push/pop at both ends) covers most use cases with better cache behavior. The Rust standard library's relative neglect of linked lists is a language-design lesson: in a language with ownership and borrowing, doubly-linked lists (where each node is owned by two previous nodes in some sense — the list and the predecessor node) are awkward. This is not a flaw; it's a reflection that doubly-linked lists, despite their conceptual simplicity, are rarely the optimal data structure.

#### Key Concepts
- Array: contiguous memory, O(1) indexed access, O(n) insert/delete
- Dynamic array: amortized O(1) push, doubling strategy, geometric series analysis
- Linked list: scattered nodes, O(n) indexed access, O(1) front insertion/deletion
- The cache penalty of pointer chasing
- Abstract Data Type (ADT) vs. concrete data structure
- Rust: `Vec`, `VecDeque`, `LinkedList` — when each is appropriate

#### Required Reading
- CLRS, Chapter 10 (Elementary Data Structures)
- Sedgewick and Wayne, *Algorithms*, Chapter 1.3 (Bags, Queues, and Stacks)
- *The Rust Book*, Chapter 8 (Common Collections) and Chapter 15 (Smart Pointers — for `Box`, `Rc`, and how linked lists work in Rust)
- *Learn Rust With Entirely Too Many Linked Lists* (online, continuously updated) — the canonical guide to the subtleties of linked structures in Rust

#### Discussion Questions
1. Amortized analysis says dynamic array push is O(1). But any individual push could be O(n) when reallocation occurs. In a real-time system where worst-case latency matters, is a dynamic array acceptable? What alternatives exist?
2. The Rust standard library's `LinkedList` is rarely recommended. Is this a failure of the language design, or a reflection of the genuine rarity of linked-list-optimal problems? What problems *are* linked-list optimal for?
3. A `VecDeque` (ring buffer) provides O(1) push/pop at both ends. How is it implemented? What is the tradeoff compared to a doubly-linked list?

#### Practice Problems
- In Rust: implement a dynamic array (`MyVec<T>`) from scratch, supporting `push`, `pop`, `insert`, `remove`, and indexed access. Handle reallocation with doubling. Use unsafe Rust if necessary for raw memory management, but ensure memory safety (no leaks, no double-frees).
- Analyze the amortized cost of push when the growth factor is 1.5× instead of 2×. Show that it is still O(1) but with a different constant.
- In Python: implement a singly-linked list with `push_front`, `pop_front`, and `find`. Compare performance with Python's built-in `list` for (a) appending 10⁶ elements, (b) prepending 10⁵ elements, (c) searching for an element in the middle. Explain the results using the concepts from this lecture.

---

### Lecture 3: Stacks and Queues — Order, Discipline, and the Structures of Process

**Course:** CS105 — Data Structures & Algorithms I
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

Stacks and queues are the simplest abstract data types beyond the list — and among the most ubiquitous. A stack (LIFO: Last-In, First-Out) models the call stack of every programming language, the undo history of every editor, and the backtracking mechanism of every depth-first search. A queue (FIFO: First-In, First-Out) models the print spooler, the BFS frontier, and the message buffers of every concurrent system. This lecture develops both ADTs, their implementations, and their far-reaching applications.

#### Lecture Notes

A *stack* supports three fundamental operations: `push(x)` — add x to the top; `pop()` — remove and return the top element; and `peek()` — return the top element without removing it. The ADT specifies *what* it does, not *how*. The simplest implementation uses a dynamic array (or linked list) where push appends and pop removes from the end — both O(1). The stack is so simple that it barely feels like a data structure, yet its applications are profound.

The *call stack* is the stack's most fundamental application. When a function calls another, the caller's local variables, return address, and saved registers are pushed onto the stack; when the callee returns, they are popped. This mechanism — which every CS101 student takes for granted — is a stack managing the depth of nested function calls. Recursion, which we'll study in depth in Lecture 5, is the algorithmic expression of the call stack: a recursive function "pushes" a new problem instance onto the call stack and "pops" it when the base case is reached. Understanding the stack is understanding how programs execute.

*Expression evaluation* is another classic application. The shunting-yard algorithm (Dijkstra, 1961) converts infix expressions (`3 + 4 × 2`) to postfix (`3 4 2 × +`) using a stack for operators. Postfix evaluation uses a stack for operands: push numbers; when an operator is encountered, pop two numbers, apply the operator, push the result. Both algorithms are O(n) and form the basis of every calculator and compiler's expression parser. The elegance of stack-based evaluation — no parentheses needed, no precedence rules — is a testament to the power of choosing the right intermediate representation.

A *queue* supports `enqueue(x)` — add x to the rear; `dequeue()` — remove and return the element at the front; `peek()` — return the front element. A linked list with both head and tail pointers provides O(1) enqueue and dequeue. A circular buffer (ring buffer) — an array with head and tail indices that wrap around — provides O(1) operations with better cache locality and no allocation overhead. Rust's `VecDeque` is a circular buffer. Queues model any system where entities arrive, wait, and are served in order: OS process schedulers, network packet buffers, the BFS frontier that explores a graph layer by layer.

*Priority queues* generalize queues: each element has a priority, and `dequeue` returns the highest-priority element (not necessarily the oldest). We preview this structure — which will be the subject of Lecture 8 (heaps) — through applications: Dijkstra's shortest-path algorithm uses a priority queue to always process the closest unvisited vertex; OS schedulers use priority queues to balance responsiveness and throughput; the A* search in AI (AI301) uses a priority queue ordered by estimated total cost.

The lecture closes with an application from the Yggdrasil AI OS: the *MuninnGate* message buffer (OS203). Messages between OS realms are FIFO within priority bands: high-priority messages (kernel panics, security alerts) use one queue; normal messages (sensor updates, routine queries) use another; the dispatcher drains the high-priority queue before touching the normal one. This is a *multilevel queue* — a composition of the simple structures from this lecture into a system that balances urgency and fairness.

#### Key Concepts
- Stack: LIFO, O(1) push/pop/peek, array and linked-list implementations
- Call stack and recursion as stack applications
- Expression evaluation: infix → postfix, shunting-yard, postfix evaluation
- Queue: FIFO, O(1) enqueue/dequeue, linked-list and circular buffer implementations
- Priority queue: highest-priority-first, preview of heap implementation
- Deque (double-ended queue): push/pop at both ends
- Multilevel queues and OS message dispatching

#### Required Reading
- CLRS, Chapter 10.1 (Stacks and Queues)
- Sedgewick and Wayne, *Algorithms*, Chapter 1.3 (Stacks, Queues, and Bags)
- Dijkstra, E.W. "Algol 60 Translation," 1961 — the original description of the shunting-yard algorithm

#### Discussion Questions
1. A stack is LIFO; a queue is FIFO. What real-world scheduling scenarios require intermediate policies? (Hint: think about elevator scheduling, where fairness and efficiency are both goals.)
2. Postfix notation (Reverse Polish Notation) eliminates the need for parentheses. Why don't programming languages use postfix for their syntax, if it's so elegant? What is lost?
3. The MuninnGate multilevel queue prevents starvation of low-priority messages by occasionally promoting an old low-priority message to the high-priority queue (a technique called *aging*). How would you implement aging efficiently? What is the tradeoff between starvation prevention and priority inversion?

#### Practice Problems
- In Rust: implement a generic `Stack<T>` using `Vec<T>` as the backing store. Add an `Iterator` implementation that yields elements in LIFO order without consuming the stack. Then implement `Queue<T>` using a circular buffer with a fixed capacity, returning `Result` or `Option` on overflow.
- Write a postfix calculator in Python. The input is a string like `"3 4 + 2 *"` — tokens separated by spaces; numbers are pushed onto a stack; operators pop operands and push results. Handle division by zero and invalid input gracefully.
- Using two stacks, implement a queue with O(1) amortized enqueue and dequeue. (Hint: the "two-stack queue" uses one stack for enqueue, another for dequeue; when dequeue stack is empty, transfer all elements from enqueue stack.) Prove the amortized bound.

---

### Lecture 4: Hashing — The Magic of O(1) Lookup

**Course:** CS105 — Data Structures & Algorithms I
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

A hash table answers the question: "Is x in this set?" in expected O(1) time, regardless of set size. It achieves this through a brilliant idea: map each element to an array index via a *hash function*, store it there, and handle collisions (when two elements map to the same index) gracefully. This lecture develops hash tables from the hash function through collision resolution (chaining and open addressing) to the practical engineering that makes them the most-used data structure in computing.

#### Lecture Notes

The *hash function* h: U → {0, 1, ..., m-1} maps elements from a potentially enormous universe U (e.g., all possible strings) to a small number of buckets. An ideal hash function distributes elements *uniformly* — each bucket receives roughly n/m elements, where n is the number of stored elements and m is the table size. Uniformity is a property of the hash function relative to the input distribution; a function that is uniform for random English words may be terrible for URLs or genomic sequences. In practice, *universal hashing* (Carter and Wegman, 1979) provides a theoretical guarantee: choose a hash function randomly from a family H such that for any distinct x, y, the probability (over the random choice of h) that h(x) = h(y) is at most 1/m. This guarantee holds for *any* input, even adversarially chosen, making universal hashing the gold standard for security-sensitive applications.

*Collision resolution* is the art of handling the inevitable case where h(x) = h(y) but x ≠ y. Two main strategies exist. *Separate chaining*: each bucket stores a linked list (or balanced tree) of all elements that hash to that index. Search: hash to bucket, then traverse the list. Worst-case O(n) if all elements hash to the same bucket (a pathological hash function or an adversarial input), but expected O(1 + α) where α = n/m is the *load factor*. *Open addressing*: all elements are stored in the table itself; on collision, probe a sequence of alternative locations. *Linear probing*: h(k, i) = (h'(k) + i) mod m — probes consecutive slots, simple and cache-friendly but suffers from *primary clustering* (long runs of occupied slots). *Quadratic probing*: h(k, i) = (h'(k) + c₁i + c₂i²) mod m — avoids primary clustering but can suffer from *secondary clustering*. *Double hashing*: h(k, i) = (h₁(k) + i·h₂(k)) mod m — uses a second hash function for the step size, achieving performance close to uniform probing. In 2040, open addressing with a good probe sequence (Robin Hood hashing, Swiss tables) dominates production hash table implementations because of its cache efficiency — probing adjacent memory locations means L1 cache hits.

*Deletion* in open addressing is tricky: you cannot simply empty a slot, because that would break the probe sequence for elements that probed past it. The solution is *tombstones* — mark deleted slots as "deleted" (distinct from "empty"). Deleted slots can be reused by insertions but not by searches (which must continue past them). Over time, the table accumulates tombstones, degrading performance; the remedy is *rehashing* — allocate a new table, reinsert all non-deleted elements. The same technique handles load factor growth: when α exceeds a threshold (typically 0.7–0.9 for open addressing), rehash to a larger table (typically 2× size).

The Python `dict` and Rust `HashMap` are among the most heavily optimized hash table implementations in existence. Python's `dict` (since CPython 3.6) uses a variant of open addressing with *compact storage*: entries are stored in a dense array (for iteration speed), and a separate sparse array of indices maps hashes to positions in the dense array. Rust's `std::collections::HashMap` uses *Swiss tables* (ported from Google's Abseil library), which use SIMD instructions to probe 16 buckets simultaneously — a brilliant fusion of data structures and computer architecture (CS104) that achieves near-optimal cache behavior.

We close with *cryptographic hash functions* — SHA-256, BLAKE3 — which are designed for a different purpose: they must be collision-resistant (it is computationally infeasible to find x ≠ y with h(x) = h(y)) and preimage-resistant (given h(x), infeasible to find x). Cryptographic hashes are overkill for in-memory hash tables (they are slower and produce wider outputs) but essential for digital signatures, Merkle trees (used in the Yggdrasil OS's integrity verification), and blockchain consensus. The hash functions used for hash tables (FxHash, SipHash) prioritize speed and uniform distribution; SipHash additionally provides protection against *hash flooding* attacks (where an adversary crafts inputs that all collide, degrading the server to O(n) per operation).

#### Key Concepts
- Hash function: mapping a universe to m buckets; uniformity, universal hashing
- Separate chaining: linked lists per bucket, O(1 + α) expected
- Open addressing: linear probing, quadratic probing, double hashing; primary/secondary clustering
- Deletion with tombstones; rehashing on load factor threshold
- Production implementations: Python dict (compact storage), Rust HashMap (Swiss tables, SIMD probing)
- Cryptographic hash functions vs. hash-table hash functions
- Hash flooding and SipHash

#### Required Reading
- CLRS, Chapter 11 (Hash Tables)
- Sedgewick and Wayne, *Algorithms*, Chapter 3.4 (Hash Tables)
- Carter, J.L. and Wegman, M.N. "Universal Classes of Hash Functions," *JCSS*, 1979 — the foundational paper
- *The Rust Performance Book*, Section on HashMap optimization (online, continuously updated)

#### Discussion Questions
1. Separate chaining degrades gracefully when the load factor exceeds 1 (you just get longer chains). Open addressing fails when the table is full. Why, then, do production implementations overwhelmingly prefer open addressing?
2. Hash flooding attacks exploit predictable hash functions to force collisions. SipHash mitigates this with a keyed hash. What other defenses exist? What is the performance cost of SipHash compared to a fast non-cryptographic hash?
3. In 2040, the OS203 "Gate of Remembrance" uses hash tables for indexing memories by key. What are the implications of hash table rehashing for a real-time AI OS? How might you design a hash table that avoids latency spikes?

#### Practice Problems
- In Rust: implement a hash table from scratch using open addressing with linear probing. Support `insert`, `get`, `remove` (with tombstones), and `rehash`. Use a simple hash function (e.g., FNV-1a). Test with random insertions and measure the average probe length vs. load factor.
- In Python: implement a hash table using separate chaining. Compare its performance with Python's built-in `dict` for 10⁶ insertions and lookups. Explain the performance gap.
- Design a hash function for a 2D point (x, y coordinates as i64). Your hash should map nearby points to different buckets (to avoid clustering). Test your function by hashing a grid of points and measuring bucket size variance.

---

### Lecture 5: Recursion — The Divide-and-Conquer Mind

**Course:** CS105 — Data Structures & Algorithms I
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

Recursion is the algorithmic expression of self-reference: a function that calls itself to solve smaller instances of the same problem. It is simultaneously one of the most powerful problem-solving techniques — enabling elegantly concise solutions to problems that would be nightmarishly complex iteratively — and one of the most abused, leading to exponential blowups when applied without memoization or when the recursion tree is not pruned. This lecture develops recursion as a rigorous problem-solving methodology, from the base case and the inductive step to the analysis of recursive algorithms via recurrence relations.

#### Lecture Notes

Every recursive algorithm must satisfy three conditions to be correct and terminating: (1) a *base case* — a smallest instance that can be solved directly, without recursion; (2) a *recursive step* — a reduction from the current instance to one or more strictly smaller instances; (3) *progress* — the recursive calls must eventually reach the base case. These conditions mirror mathematical induction (CS102, Lecture 4): the base case is P(0), the recursive step is P(k) → P(k+1), and progress ensures the induction is well-founded. This is not a coincidence; recursion *is* induction, applied to computation.

The classic examples — factorial, Fibonacci, Tower of Hanoi — illustrate the power and the peril. Factorial: `fact(n) = n * fact(n-1)`, base case `fact(0) = 1`. This is O(n) time and O(n) stack space. Fibonacci: `fib(n) = fib(n-1) + fib(n-2)`, base cases `fib(0)=0, fib(1)=1`. This naive recursion is *exponentially* slow — O(φⁿ) — because it recomputes the same subproblems exponentially many times. The fix is *memoization* (caching results) or *dynamic programming* (building the table bottom-up), which we'll study in CS201. The lesson: recursion is a specification, not always an implementation strategy; sometimes it specifies the problem beautifully but must be transformed into iteration (with explicit stacks or tables) for efficiency.

*Divide-and-conquer* is the most important recursive paradigm. The template: (1) *divide* the problem into a number of subproblems that are smaller instances of the same problem; (2) *conquer* the subproblems recursively; (3) *combine* the solutions to the subproblems into the solution to the original problem. Merge sort exemplifies this: divide the array into two halves (O(1) with index arithmetic), recursively sort each half, and merge the sorted halves (O(n)). The recurrence T(n) = 2T(n/2) + O(n) solves to T(n) = O(n log n). Binary search is a trivial divide-and-conquer: divide the search space in half, recurse on one half, no combine step needed. T(n) = T(n/2) + O(1) → O(log n).

*Tail recursion* is an optimization concern. A recursive call is in *tail position* if it is the last action the function performs; the function's stack frame can be reused for the recursive call (tail-call optimization, TCO). In functional languages (Haskell, Scheme), TCO is guaranteed. In Rust, LLVM performs TCO when optimizations are enabled, but Rust does not guarantee it — recursive functions that would overflow the stack should be rewritten as loops. In Python, TCO is explicitly *not* supported (Guido van Rossum argued it would complicate debugging and stack traces). Understanding when to use recursion and when to transform it into iteration is an essential programming skill.

The lecture closes with *tree recursion* — the paradigm behind backtracking search, where we explore a space of possibilities by making a choice, recursing, and undoing the choice (backtracking). The N-Queens problem — place N queens on an N×N chessboard so that no two attack each other — is a canonical example. It can be solved by a recursive backtracking search that is O(N!) in the worst case but far faster in practice with pruning (column, diagonal constraints). Backtracking is the algorithmic heart of constraint solving, SAT, and the planning systems that AI agents (AI301) use to navigate complex decision spaces.

#### Key Concepts
- Recursion: base case, recursive step, progress guarantee
- Recursion and induction: structural equivalence
- Divide-and-conquer: divide, conquer, combine; merge sort, binary search
- Recurrence relations for recursive algorithms: T(n) = aT(n/b) + f(n)
- Tail recursion and tail-call optimization
- Memoization and the recursion-to-DP transformation
- Backtracking: the state-space tree, pruning, N-Queens

#### Required Reading
- CLRS, Chapters 2.3 (Designing Algorithms — divide and conquer) and 4 (Divide-and-Conquer)
- Sedgewick and Wayne, *Algorithms*, Chapter 1.1 (Basic Programming Model — recursion sections)
- Wirth, N. *Algorithms + Data Structures = Programs* (1976), Chapter on Recursion — a classic exposition

#### Discussion Questions
1. Every recursive algorithm can be transformed into an iterative one (by maintaining an explicit stack). Every iterative algorithm can be expressed recursively. When is recursion clearer? When is iteration clearer? Is there an objective metric, or is it purely a matter of taste and training?
2. Python limits recursion depth (default: 1000) and does not support TCO. What are the implications for writing recursive algorithms in Python? How do Python programmers work around these limitations?
3. Backtracking explores a tree of possibilities, pruning branches that cannot lead to a solution. How does this relate to the branch-and-bound technique in optimization? What is the role of heuristics (choosing which branch to explore next) in search efficiency?

#### Practice Problems
- Implement merge sort recursively in Rust. Count comparisons. Then implement an iterative (bottom-up) merge sort. Compare performance for arrays of size 10² to 10⁶. Is the recursive version's overhead measurable?
- Solve the N-Queens problem in Python using recursive backtracking. For N=8, count the number of solutions. Add pruning — is it safe to place a queen at (row, col)? Report the number of positions explored with and without pruning.
- Write a recursive function to compute C(n, k) (binomial coefficient) using the identity C(n, k) = C(n-1, k-1) + C(n-1, k). Time it for n=30. Then add memoization (using `@functools.lru_cache`). Time it again. Explain the dramatic difference.

---

### Lecture 6: Sorting I — Quadratic Sorts, Merge Sort, and the Lower Bound

**Course:** CS105 — Data Structures & Algorithms I
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

Sorting is the most studied problem in computer science — not because it is the most important (though it is important), but because it is universal enough to admit deep analysis while simple enough to be taught in a first course. This lecture covers three sorting algorithms: insertion sort (O(n²), but adaptive — O(n) on nearly-sorted data), merge sort (O(n log n) worst-case, the gold standard for guaranteed performance), and the comparison-based sorting lower bound (Ω(n log n)), which proves that merge sort is asymptotically optimal.

#### Lecture Notes

*Insertion sort* builds the sorted array one element at a time: for each element from left to right, insert it into its correct position among the already-sorted elements to its left. This is how you sort a hand of playing cards. The inner loop shifts elements right until the correct position is found. Worst-case: O(n²) when the input is reverse-sorted. Best-case: O(n) when the input is already sorted — insertion sort simply verifies each element is in place. This *adaptivity* makes insertion sort useful as a subroutine in hybrid sorts (Timsort, used in Python and Rust's `sort`, switches to insertion sort for small subarrays, typically n ≤ 32). Insertion sort is also *stable* — equal elements maintain their relative order — a property that matters when sorting by multiple keys.

*Merge sort* is the canonical divide-and-conquer sort. Divide the array into two halves; recursively sort each half; merge the sorted halves. The merge step — interleaving two sorted sequences into one — is O(n) and is the algorithm's workhorse. The recurrence T(n) = 2T(n/2) + O(n) solves to O(n log n), and this bound holds for *all* inputs, not just the average case. Merge sort is stable and predictable — it is the sort of choice when guaranteed O(n log n) is required and when the data is in a linked list (merge sort on linked lists requires no auxiliary array; merging is still O(1) space with pointer manipulation). The main drawback: O(n) auxiliary space for the merge (though in-place variants exist, they are significantly more complex).

The *comparison-based sorting lower bound* is one of the most elegant proofs in computer science. Any comparison-based sorting algorithm can be modeled as a *decision tree*: each internal node represents a comparison (aᵢ < aⱼ?), and each leaf represents a permutation of the input. For n distinct elements, there are n! possible permutations, so the decision tree must have at least n! leaves. A binary tree of height h has at most 2ʰ leaves. Therefore, h ≥ log₂(n!), and by Stirling's approximation, log₂(n!) ≈ n log₂ n - n log₂ e = Ω(n log n). The height of the tree is the number of comparisons in the worst case. Thus, *any* comparison-based sorting algorithm requires Ω(n log n) comparisons in the worst case. This is a *lower bound* — it says "you cannot do better," not "here is how to do it." Merge sort and heapsort achieve this bound; no comparison-based sort can be asymptotically faster.

But what about algorithms that *don't* use comparisons? *Counting sort* and *radix sort* exploit the structure of the keys (they must be integers in a known range) to achieve O(n) time — beating the Ω(n log n) lower bound because they aren't comparison-based. Counting sort: count frequencies of each key, compute cumulative counts (which give the final position of each key), place elements. Radix sort: sort by the least significant digit, then the next, and so on — using a stable sort (like counting sort) for each digit. If keys are d-digit numbers in base b, radix sort takes O(d(n + b)) time. When d is constant and b = O(n), this is O(n). These algorithms are the basis of string sorting and integer sorting in database systems and are increasingly relevant in 2040 for sorting the massive embedding vectors used in AI similarity search.

We close with a practical comparison across our two languages. Python's `list.sort()` uses Timsort, a hybrid of merge sort and insertion sort that is stable, adaptive, and O(n log n) worst case. Rust's `slice::sort()` uses a pattern-defeating quicksort (pdqsort) that is O(n log n) average case with O(n log n) worst case via heapsort fallback; `slice::sort_unstable()` uses pdqsort without the stability guarantee, yielding a modest speedup. Understanding what your language's sort *actually does* is essential for debugging performance anomalies — a "sort" that's mysteriously slow might be hitting pdqsort's worst case, which the Rust docs warn about.

#### Key Concepts
- Insertion sort: O(n²) worst, O(n) best, stable, adaptive
- Merge sort: O(n log n) always, stable, O(n) auxiliary space
- The comparison-based sorting lower bound: decision tree, Ω(n log n)
- Counting sort and radix sort: non-comparison O(n) sorting
- Timsort (Python) and pdqsort (Rust): production hybrid sorts
- Stability and its significance for multi-key sorting

#### Required Reading
- CLRS, Chapters 2.1 (Insertion Sort), 2.3 (Merge Sort), 8 (Sorting in Linear Time)
- Sedgewick and Wayne, *Algorithms*, Chapters 2.1–2.3 (Elementary Sorts through Quicksort)
- Peters, T. "Timsort," Python-Dev mailing list, 2002 — the original description of the algorithm now used by Python, Java, and Android

#### Discussion Questions
1. The decision-tree lower bound proves Ω(n log n) for comparison-based sorting. But what if we have partial information? If the input is known to be "nearly sorted" (at most k inversions), can we sort faster in terms of n and k?
2. Radix sort is O(n) — why isn't it always used instead of O(n log n) sorts? What are the hidden constants and restrictions?
3. Timsort is a marvel of engineering, combining merge sort and insertion sort with extensive heuristics (galloping mode, run detection). Should we teach Timsort in an algorithms course, or is it too specialized? What is the educational value of studying production implementations?

#### Practice Problems
- Implement insertion sort, merge sort, and counting sort in Rust. Benchmark them on: (a) random arrays of size 10⁴, (b) already-sorted arrays, (c) reverse-sorted arrays. Report and explain the results.
- Prove, by constructing a decision tree, that finding the maximum element in an unsorted array requires at least n-1 comparisons.
- Implement radix sort for 32-bit unsigned integers, using counting sort as the stable subroutine for each 8-bit digit. Compare performance with Rust's `slice::sort_unstable()` for arrays of 10⁶ random integers. Which is faster, and why?

---

### Lecture 7: Sorting II — Quicksort, Heapsort, and the Practical Art of Fast Sorting

**Course:** CS105 — Data Structures & Algorithms I
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

Merge sort is asymptotically optimal but requires O(n) extra space. Quicksort is O(n log n) on average, O(n²) worst-case (mitigated by randomization), and O(log n) extra space — and in practice, its cache-friendly in-place partitioning makes it faster than merge sort on arrays. Heapsort is O(n log n) worst-case, in-place, and not stable — a reliable workhorse when worst-case guarantees matter more than constant factors. This lecture completes the sorting story, developing quicksort and heapsort and comparing them against the field.

#### Lecture Notes

*Quicksort* (Hoare, 1960) is the poster child for randomized algorithms. The idea: choose a *pivot* element; *partition* the array so that elements less than the pivot are on the left and elements greater are on the right; recursively sort the left and right subarrays. The partitioning is the entire algorithm: it can be done in-place with two pointers (Lomuto's scheme, simpler but more swaps; Hoare's scheme, the original, fewer swaps). The performance depends entirely on the pivot. If the pivot is always the median, the recurrence is T(n) = 2T(n/2) + O(n) = O(n log n). If the pivot is always the minimum or maximum, the recurrence is T(n) = T(n-1) + O(n) = O(n²). The worst case occurs on already-sorted input with a naive pivot choice (e.g., always the first element).

The fix is *randomization*: choose the pivot uniformly at random. The probability of a "bad" pivot (one that splits the array worse than 25–75) is 1/2 — but after O(log n) bad pivots, the subproblem sizes shrink geometrically, and the expected running time is O(n log n) for *any* input. This is the magic of randomized algorithms: they replace assumptions about the input distribution with a guarantee about the algorithm's behavior on *every* input, in expectation. The analysis is a classic: expected comparisons = 2(n+1)H_n - 8n ≈ 2n ln n ≈ 1.39 n log₂ n — about 39% more comparisons than merge sort's ~n log₂ n, but quicksort's cache behavior and low overhead make it faster in practice.

*Heapsort* takes a different approach: build a *max-heap* from the array (O(n) with the bottom-up heapify), then repeatedly extract the maximum (swap it with the last element, shrink the heap, sift down) — O(n log n) total. Heapsort is in-place (no auxiliary array needed, unlike merge sort) and O(n log n) worst-case (unlike quicksort). But its constant factors are larger (heap operations involve more comparisons and swaps than quicksort's partitioning), and it has poor cache locality (heap access patterns jump around memory). In practice, heapsort is rarely the fastest sort, but it serves as a fallback — pdqsort, Rust's unstable sort, switches to heapsort when quicksort's recursion depth exceeds log₂ n, guaranteeing O(n log n) worst case.

*Selection* is a related problem: find the k-th smallest element. Sorting solves it in O(n log n). But *quickselect* (quicksort's cousin) solves it in expected O(n): partition around a random pivot; if the pivot is at position k, return it; if the pivot is to the right of k, recurse left; otherwise recurse right. The analysis: expected comparisons ≈ 2n + 2k log(n/k) + 2(n-k) log(n/(n-k)), which is O(n). The *BFPRT* algorithm (Blum, Floyd, Pratt, Rivest, Tarjan, 1973) achieves O(n) *worst-case* selection using a deterministic "median of medians" pivot strategy — a beautiful theoretical result that is rarely used in practice because the constant factors are large.

The lecture closes with a taxonomy of sorting algorithms, mapping them onto the Yggdrasil-9's heterogeneous architecture. For small arrays (n < 100): insertion sort on the CPU. For medium arrays (100 ≤ n < 10⁶) fitting in cache: quicksort (pdqsort) on the CPU. For large arrays (n ≥ 10⁶): parallel merge sort on the GPU (using CUDA's Thrust library or Rust's `gpu_mergesort`). For integers in a bounded range: radix sort on the GPU (exploiting massive parallelism for counting). Choosing the right sort is not about knowing the asymptotics; it's about knowing the hardware.

#### Key Concepts
- Quicksort: pivot, partition (Lomuto, Hoare), randomized analysis, expected O(n log n)
- Quicksort pitfalls: worst-case O(n²), stack overflow on deep recursion
- Heapsort: build-heap O(n), extract-max O(log n), O(n log n) total, in-place
- Quickselect: O(n) expected selection; BFPRT: O(n) worst-case selection
- Production sorts: pdqsort (quicksort + heapsort fallback + insertion sort for small arrays)
- Sorting on heterogeneous hardware: CPU, GPU, SIMD

#### Required Reading
- CLRS, Chapters 7 (Quicksort), 6 (Heapsort), 9 (Medians and Order Statistics)
- Hoare, C.A.R. "Quicksort," *The Computer Journal*, 1962 — the original paper
- Blum, M. et al. "Time Bounds for Selection," *JCSS*, 1973 — the BFPRT algorithm
- Orson, P. "Pattern-Defeating Quicksort," *arXiv*, 2021 — the pdqsort paper, describing Rust's unstable sort

#### Discussion Questions
1. Quicksort's expected running time is O(n log n) even on already-sorted input if the pivot is randomized. But if you *know* the input is nearly sorted, would you still use quicksort? What alternatives are better?
2. Heapsort is in-place and O(n log n) worst case. Why, then, is it almost never the default sorting algorithm? What specific microarchitectural factors hurt its performance?
3. Quickselect is O(n) expected, BFPRT is O(n) worst case. In practice, quickselect is used, BFPRT is not. Is this a case of theory being "too clever"? What does this tell us about the role of worst-case analysis in algorithm design?

#### Practice Problems
- Implement quicksort in Rust with Lomuto partitioning. Use a random pivot. Compare performance with merge sort for random, sorted, and reverse-sorted arrays of size 10⁵. Add the pdqsort optimization: switch to insertion sort for subarrays of size ≤ 32.
- Implement heapsort in Python. Profile the heap operations: how many comparisons and swaps for an array of 10⁴ random elements? Compare with quicksort and merge sort.
- Implement quickselect to find the median of an unsorted array. Verify it is correct by comparing with the sorted array's median. Benchmark on arrays of size 10⁶ and compare with sorting-then-indexing.

---

### Lecture 8: Heaps and Priority Queues — The Structure of Priority

**Course:** CS105 — Data Structures & Algorithms I
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

A heap is a tree-based data structure that maintains the *heap property*: every parent is ≥ (max-heap) or ≤ (min-heap) its children. This simple invariant enables O(1) access to the extreme element and O(log n) insertion and extraction — making heaps the implementation of choice for priority queues. This lecture develops the binary heap (array-based, implicit tree structure), the heap operations (sift-up, sift-down, heapify), and the algorithms — heapsort, Dijkstra's, Prim's — that depend on priority queues.

#### Lecture Notes

A *binary heap* is a complete binary tree stored in an array: for a node at index i (1-indexed, or 0-indexed with adjusted formulas), its left child is at 2i, right child at 2i+1, parent at ⌊i/2⌋. The "complete binary tree" property — all levels are full except possibly the last, which is filled left to right — ensures that the array representation is compact (no pointer overhead) and that the tree height is ⌊log₂ n⌋. This array-based representation, pioneered by Williams (1964) for heapsort, is a masterstroke of data structure design: it achieves the flexibility of a tree with the cache efficiency of an array.

The two fundamental heap operations are *sift-up* (bubble-up, swim) and *sift-down* (bubble-down, sink). *Sift-up* restores the heap property after an insertion: place the new element at the end (next available leaf position), then repeatedly swap it with its parent if the heap property is violated. Each swap moves the element up one level; at most ⌊log₂ n⌋ swaps, so O(log n). *Sift-down* restores the heap property after extracting the root: move the last element to the root, then repeatedly swap it with its larger (max-heap) or smaller (min-heap) child until the heap property is restored. Also O(log n). *Heapify* builds a heap from an unsorted array in O(n) time by calling sift-down on each non-leaf node, from bottom to top. The analysis — Σ_{h=0}^{⌊log n⌋} ⌈n/2^{h+1}⌉ · O(h) = O(n) — is a classic use of geometric series and is one of those surprising results (like dynamic array amortization) where naive analysis overestimates the cost.

Heaps implement the *priority queue* ADT: `insert(key)`, `extract_max()` (or `extract_min()`), `peek()`, `increase_key()`, `decrease_key()`. The last two — changing a key's priority and restoring the heap property — require knowing the position of the element in the heap. This motivates *augmented heaps* that store a `HashMap` mapping elements to their array indices, enabling O(log n) key updates. Dijkstra's shortest-path algorithm and Prim's minimum spanning tree algorithm both require `decrease_key` on the priority queue — without it, you either accept stale entries (lazy deletion, which bloats the heap) or use a Fibonacci heap (which provides O(1) amortized `decrease_key`, at the cost of significant constant factors and implementation complexity).

Beyond binary heaps, a family of *mergeable heaps* supports union operations. *Binomial heaps* (Vuillemin, 1978) support merge in O(log n). *Fibonacci heaps* (Fredman and Tarjan, 1987) achieve O(1) amortized insert, decrease-key, and merge, with O(log n) amortized extract-min — theoretically optimal for algorithms that do many decrease-key operations. *Pairing heaps* (Fredman et al., 1986) are simpler than Fibonacci heaps and competitive in practice. In 2040, the Rust ecosystem provides binary heaps (`std::collections::BinaryHeap`) and pairing heaps (via the `pairing-heap` crate), but Fibonacci heaps remain rare outside research code due to their complexity.

The lecture closes with an application from AI: *beam search*, used in neural sequence generation (language models, machine translation). Beam search maintains a bounded priority queue of the k most promising partial sequences; at each step, it expands all k, scores the extensions, and keeps the top k. A max-heap of size k, with `extract_min` to discard the worst when the heap exceeds k, implements this efficiently. The Yggdrasil OS's language module (OS205) uses a beam-search variant with a pairing heap, processing millions of hypotheses per second.

#### Key Concepts
- Binary heap: complete binary tree, array representation, parent/child index formulas
- Sift-up: O(log n) insertion
- Sift-down: O(log n) extraction
- Heapify: O(n) bottom-up construction
- Priority queue ADT and operations: insert, extract, peek, increase/decrease key
- Augmented heaps with position tracking for key updates
- Fibonacci heaps, pairing heaps: theoretical vs. practical performance
- Applications: Dijkstra, Prim, beam search, event-driven simulation

#### Required Reading
- CLRS, Chapter 6 (Heapsort) and Chapter 19 (Fibonacci Heaps)
- Sedgewick and Wayne, *Algorithms*, Chapter 2.4 (Priority Queues)
- Fredman, M.L. and Tarjan, R.E. "Fibonacci Heaps and Their Uses in Improved Network Optimization Algorithms," *JACM*, 1987 — the paper that introduced Fibonacci heaps

#### Discussion Questions
1. Binary heaps are O(log n) for all operations. Fibonacci heaps are O(1) amortized for insert and decrease-key. Why has the binary heap remained the default in standard libraries? What does "amortized O(1)" hide that matters in practice?
2. A binary heap stored in an array has excellent cache locality for the first few levels (they occupy contiguous memory). As you go deeper, locality degrades. Would a d-ary heap (each node has d children, making the tree shallower) improve cache behavior? What is the optimal d for modern cache line sizes?
3. The augmented heap for Dijkstra's algorithm requires a `HashMap` from vertices to heap positions. In 2040, with the memory wall (CS104), is the overhead of the `HashMap` justified, or is lazy deletion (accepting stale entries) actually faster?

#### Practice Problems
- In Rust: implement a `BinaryHeap<T>` (max-heap) from scratch using a `Vec<T>` as backing storage. Support `push`, `pop`, `peek`, and `heapify` (constructor from `Vec<T>`). Implement `Iterator` that yields elements in arbitrary order (not sorted — that would require extracting all, which is O(n log n)).
- Use your heap to implement heapsort: `heapify` the array, then repeatedly `pop` and place at the end. Compare performance with Rust's `slice::sort_unstable()`.
- Implement Dijkstra's shortest-path algorithm using your binary heap. For a graph with V=10⁴ vertices and E=10⁵ edges, how many heap operations (push, pop, decrease_key) are performed? What fraction of time is spent in the heap vs. adjacency list traversal?

---

### Lecture 9: Binary Search Trees — Ordered Storage and the Cost of Imbalance

**Course:** CS105 — Data Structures & Algorithms I
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

A binary search tree (BST) combines the flexibility of a linked structure with the discipline of an ordering invariant: for any node, all elements in its left subtree are smaller, and all in its right subtree are larger. This invariant enables O(h) search, insertion, and deletion, where h is the tree height. In the best case — a balanced tree — h = O(log n), and BST operations match the asymptotic performance of binary search on a sorted array while supporting dynamic updates. In the worst case — a degenerate chain — h = O(n), and the BST is no better than a linked list. This lecture covers BST fundamentals and motivates the self-balancing trees of CS201.

#### Lecture Notes

The *BST property* is elegantly recursive: a binary tree is a BST if, for every node x, all keys in x's left subtree are ≤ x.key, all keys in x's right subtree are ≥ x.key, and the left and right subtrees are themselves BSTs. (The ≤/≥ convention allows duplicate keys; for unique keys, use </>.) Search follows the property: starting at the root, compare the query key with the current node's key; if equal, found; if less, go left; if greater, go right. Each comparison eliminates half the remaining tree *if the tree is balanced* — in the worst case of a chain, each comparison eliminates exactly one node.

*Insertion* finds the correct leaf position by following the search path, then attaches the new node there. *Deletion* has three cases: (1) the node is a leaf — just remove it; (2) the node has one child — replace it with its child; (3) the node has two children — find the *successor* (the smallest node in the right subtree), swap keys (or copy the successor's key into the node), and delete the successor (which falls into case 1 or 2). All operations are O(h), where h is the tree height.

The height of a randomly built BST (inserting n distinct keys in random order) is approximately 2.99 log₂ n on average — O(log n). This is a classic result (Devroye, 1986): the expected height of a random BST is ~4.311 log₂ n, but the constant makes it practical for moderate n. However, in adversarial or real-world scenarios (inserting sorted data yields a chain), the height can be Ω(n), destroying performance. This fragility motivates *self-balancing BSTs* — red-black trees, AVL trees, B-trees — which maintain O(log n) height through rotations and color/maintenance rules. These are the subject of CS201; in CS105, we establish the BST foundation and the need for balance.

*Tree traversals* are the BST's superpower beyond search. *In-order traversal* (left, node, right) visits keys in sorted order — O(n) time. *Pre-order* (node, left, right) produces a prefix notation; *post-order* (left, right, node) produces postfix. These traversals are the basis for serializing and deserializing trees, for range queries ("find all keys between a and b"), and for the tree-based algorithms in compilers (abstract syntax trees) and AI (decision trees, Monte Carlo tree search).

We also cover *augmented BSTs* — trees that store additional information at each node to support queries beyond simple search. An *order-statistic tree* stores at each node the size of its subtree; the k-th smallest element can be found in O(log n) by comparing k with the left subtree size. An *interval tree* stores the maximum endpoint in each subtree, enabling O(log n) overlap queries ("find an interval that overlaps [low, high]"). Augmentation is a general technique: compute the augmented value from the node's key and the augmented values of its children, and update it on insertions and rotations. This is the data-structure equivalent of adding a column to a database table — it extends functionality without restructuring.

#### Key Concepts
- BST property: left ≤ node ≤ right, recursively
- Search, insertion, deletion: O(h) where h = height
- Three deletion cases: leaf, one child, two children (successor)
- Random BST height: O(log n) expected; adversarial: O(n) worst
- Tree traversals: in-order (sorted), pre-order, post-order; O(n)
- Augmented BSTs: order-statistic tree, interval tree
- Motivation for self-balancing trees (CS201)

#### Required Reading
- CLRS, Chapters 12 (Binary Search Trees), 14 (Augmenting Data Structures)
- Sedgewick and Wayne, *Algorithms*, Chapter 3.2 (Binary Search Trees)
- Devroye, L. "A Note on the Height of Binary Search Trees," *JACM*, 1986 — the random BST height analysis

#### Discussion Questions
1. A BST can degrade to O(n) height. Why, then, does Python not include a BST in its standard library? (Python uses hash tables for dicts/sets and leaves ordered structures to third-party packages.) What does this say about the relative importance of ordered vs. unordered data structures?
2. Deletion by successor replacement (case 3) works, but it has a subtle asymmetry: repeatedly deleting and reinserting can unbalance the tree even if it started balanced. Why? Is there a symmetric deletion strategy?
3. An order-statistic tree augments each node with subtree size. What other queries can be supported with augmentation? How would you design an augmented BST to answer "how many keys in the range [a, b]?" in O(log n)?

#### Practice Problems
- In Rust: implement a generic `BST<K, V>` with insertion, search, deletion, and in-order traversal (as an iterator). Do not implement balancing — accept O(n) worst case. Test with random insertions and measure the average height vs. 2.99 log₂ n.
- Implement an order-statistic tree by augmenting your BST with subtree sizes. Support `kth_smallest(k: usize) -> Option<&K>` and `rank(key: &K) -> usize`. Test with random data.
- Demonstrate the adversarial input: insert keys 1, 2, 3, ..., 1000 in order and measure the resulting tree height. Then insert the same keys in random order and compare.

---

### Lecture 10: Graphs — Representation, Traversal, and the Web of Connection

**Course:** CS105 — Data Structures & Algorithms I
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

Graphs model relationships: friendships in a social network, hyperlinks in the web, dependencies in a build system, transitions in a state machine. This lecture picks up where CS102's graph theory left off, focusing on the *algorithmic* treatment: graph representations (adjacency lists, adjacency matrices), the two fundamental traversal algorithms (BFS and DFS), and their applications — shortest paths, connectivity, topological sorting, and cycle detection.

#### Lecture Notes

We begin with the critical engineering decision: how to represent a graph in memory. An *adjacency matrix* — a |V| × |V| boolean (or weighted) matrix where M[i][j] is 1 if edge (i,j) exists — provides O(1) edge queries and is ideal for dense graphs (|E| ≈ |V|²). But for sparse graphs (|E| ≪ |V|²), the O(|V|²) space is wasteful. An *adjacency list* — an array of size |V|, where entry i is a list of vertices adjacent to i — provides O(degree(v)) edge queries and O(|V|+|E|) space, optimal for sparse graphs. In 2040, virtually all real-world graphs are sparse (social networks: average degree < 200; web graphs: < 20; road networks: < 4), making adjacency lists the default. Rust's `petgraph` crate and Python's `networkx` library both use adjacency-list-like representations internally.

*Breadth-first search* (BFS) explores a graph in layers, like ripples from a stone dropped in water. Starting from a source vertex s, BFS discovers all vertices at distance 1, then all at distance 2, and so on. It uses a FIFO queue: initially containing s; while the queue is not empty, dequeue a vertex, and for each unvisited neighbor, mark it visited, set its distance to current distance + 1, and enqueue it. BFS runs in O(|V|+|E|) time and computes shortest paths in *unweighted* graphs — the number of edges on the shortest path from s to v is exactly the BFS distance. Applications: web crawling (BFS from a seed page), social network analysis (degrees of separation), and the "Six Degrees of Kevin Bacon" phenomenon (the Bacon number is the BFS distance in the actor-movie graph).

*Depth-first search* (DFS) explores by going as deep as possible along each branch before backtracking. It can be implemented recursively (using the call stack) or iteratively (using an explicit stack). DFS classifies edges into: *tree edges* (edges that discover new vertices), *back edges* (edges that connect a vertex to an ancestor — indicating a cycle), *forward edges* (connecting to a descendant, in directed graphs), and *cross edges* (all others). This classification reveals structural properties: an undirected graph has a cycle iff DFS finds a back edge; a directed graph is acyclic iff DFS finds no back edges.

*Topological sorting* orders the vertices of a directed acyclic graph (DAG) so that for every edge (u, v), u comes before v. It is the foundation of dependency resolution: if A depends on B, B must be built before A. DFS-based topological sort: run DFS, and as each vertex finishes (all descendants explored), prepend it to a list. The list is a topological order. An alternative is Kahn's algorithm: repeatedly remove vertices with in-degree 0. Both run in O(|V|+|E|). Topological sort appears in build systems (Make, Bazel), in instruction scheduling (reordering instructions to respect data dependences), and in the OS205 module loading order for the Yggdrasil AI OS.

*Strongly connected components* (SCCs) are maximal sets of vertices in a directed graph where every vertex can reach every other. SCCs are the "skeleton" of a directed graph — collapsing each SCC into a supernode yields a DAG called the *condensation graph*. Kosaraju's algorithm finds SCCs with two passes of DFS (forward, then reverse graph) in O(|V|+|E|). Tarjan's algorithm does it in a single DFS pass using a stack and low-link values. SCC decomposition is fundamental for understanding the structure of the web (SCCs correspond to communities of mutually referencing pages), for analyzing Markov chains, and for optimizing compilers (SCCs in the call graph identify mutual recursion).

#### Key Concepts
- Adjacency matrix vs. adjacency list: space and query tradeoffs
- BFS: layer-by-layer, unweighted shortest paths, O(|V|+|E|)
- DFS: edge classification (tree, back, forward, cross), cycle detection
- Topological sorting: DAGs, dependency resolution, Kahn's algorithm
- Strongly connected components: Kosaraju, Tarjan, condensation DAG
- Applications: web crawling, build systems, social network analysis

#### Required Reading
- CLRS, Chapter 22 (Elementary Graph Algorithms)
- Sedgewick and Wayne, *Algorithms*, Chapter 4.1 (Undirected Graphs) and 4.2 (Directed Graphs)
- Tarjan, R.E. "Depth-First Search and Linear Graph Algorithms," *SIAM Journal on Computing*, 1972 — the paper that unified BFS/DFS/topological-sort/SCC in a single framework

#### Discussion Questions
1. BFS uses a queue; DFS uses a stack. What if you use a priority queue? You get *best-first search*, the basis of A* (AI301). How does the choice of data structure determine the search behavior?
2. Tarjan's SCC algorithm runs in O(|V|+|E|) but is notoriously subtle. Is the educational value of teaching Tarjan's algorithm worth the time, or should we only teach Kosaraju's (two-pass, more intuitive)?
3. In a social network graph with 10⁹ vertices and 10¹¹ edges, even O(|V|+|E|) algorithms may be too slow for interactive queries. What approximation or preprocessing techniques can answer connectivity queries in sublinear time?

#### Practice Problems
- Implement BFS and DFS in Rust for a graph represented as adjacency lists. Test on a graph of Wikipedia articles (provided dataset on the UoY cluster): find the shortest path (by links) between two given articles.
- Implement topological sort using both DFS and Kahn's algorithm. Verify they produce valid topological orders for a DAG. Test that they detect cycles when given a non-DAG input.
- Implement Kosaraju's algorithm for SCCs. Test on a directed graph derived from the UoY course dependency graph (CS104 → CS201 → CS301, etc.). Identify the SCCs and interpret the condensation DAG.

---

### Lecture 11: Searching — Binary Search, Interpolation Search, and the Art of Finding

**Course:** CS105 — Data Structures & Algorithms I
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

Searching — determining whether a query element exists in a collection, and if so, where — is the most frequent operation in computing. Databases search indexes, compilers search symbol tables, AI agents search state spaces. This lecture covers the fundamental search algorithms for ordered collections: binary search (the O(log n) classic), interpolation search (O(log log n) for uniform distributions), and an introduction to search in higher dimensions (kd-trees, preview of spatial data structures).

#### Lecture Notes

*Binary search* operates on a sorted array by repeatedly comparing the query with the middle element and eliminating half the remaining search space. If the array has n elements, binary search performs at most ⌊log₂ n⌋ + 1 comparisons. The algorithm is conceptually trivial — a loop that adjusts low and high pointers — but notoriously bug-prone. A 2006 study found that 90% of textbook implementations contained bugs, most commonly integer overflow in `mid = (low + high) / 2`. The fix: `mid = low + (high - low) / 2`. In Rust, `slice::binary_search` and `slice::binary_search_by` provide correct, optimized implementations; in Python, the `bisect` module.

Binary search is the algorithmic core of many data structures beyond sorted arrays. A *binary search tree* (Lecture 9) performs binary search implicitly through its tree structure. A *B-tree* (CS201) generalizes binary search to nodes with multiple keys and children, optimizing for disk access. The *skip list* (a probabilistic alternative to balanced trees) uses multiple levels of linked lists, where search at each level eliminates half the remaining elements in expectation — a binary search on a linked structure. Binary search is not merely an algorithm; it is a *design pattern* — *divide and conquer on sorted data* — that recurs throughout computer science.

*Interpolation search* improves on binary search when the keys are uniformly distributed. Instead of always probing the middle, it probes the position where the query would be if the keys were evenly spaced: `pos = low + ((query - arr[low]) * (high - low)) / (arr[high] - arr[low])`. For uniform distributions, the expected number of probes is O(log log n) — a double-logarithm that is effectively constant for any practical n (log log 10⁹ ≈ 4.5). However, for non-uniform distributions, interpolation search degrades to O(n) worst case. The lesson: exploiting knowledge of the input distribution can yield dramatic improvements, but at the risk of catastrophic degradation when that knowledge is wrong. This is a microcosm of the algorithm designer's dilemma: specialization vs. robustness.

*Search in higher dimensions* is a fundamental challenge for AI and graphics. Given a set of points in d-dimensional space, find the nearest neighbor to a query point. The naive O(dn) scan is infeasible for large n. *kd-trees* (Bentley, 1975) partition space with axis-aligned hyperplanes, alternating dimensions at each level. Search in a kd-tree prunes subtrees that are entirely farther than the current best distance, achieving O(log n) expected query time for low dimensions (d ≪ log n). In high dimensions, however, kd-trees degrade to linear scan — the "curse of dimensionality." In 2040, *approximate nearest neighbor* methods (locality-sensitive hashing, graph-based indices like HNSW, and learned indices that use neural networks to predict data positions) dominate production systems. AI OS components like the Muninn memory's similarity search (OS203) use HNSW indices over embedding vectors, achieving sub-millisecond queries over billion-entry databases. We preview these techniques, which are explored in depth in CS401 (Advanced Algorithms) and WM303 (World Model Inference).

We also cover *search in strings*: given a text T of length n and a pattern P of length m, find all occurrences of P in T. The naive O(nm) algorithm is the starting point. The *Knuth-Morris-Pratt* (KMP) algorithm preprocesses P to build a prefix function (the "failure function" — the length of the longest proper prefix of P that is also a suffix of the current prefix), enabling O(n+m) worst-case search by never backing up in T. The *Boyer-Moore* algorithm preprocesses P and matches from right to left, skipping large portions of T using the "bad character" and "good suffix" heuristics — O(n/m) best case (sublinear!) but O(nm) worst case. The *Rabin-Karp* algorithm uses rolling hashes to achieve O(n+m) expected time. In practice, Boyer-Moore is often the fastest for natural-language text; KMP is theoretically clean and never backtracks. Rust's standard library uses a variant of Two-Way (a simplification of KMP) for string search.

#### Key Concepts
- Binary search: O(log n), integer overflow bug, implementation in Rust/Python
- Interpolation search: O(log log n) expected, O(n) worst; the specialization-robustness tradeoff
- Search in higher dimensions: kd-trees, the curse of dimensionality, approximate nearest neighbors
- String search: naive O(nm), KMP O(n+m), Boyer-Moore sublinear best case, Rabin-Karp rolling hash
- Learned indices: using neural networks for search, preview of CS401

#### Required Reading
- CLRS, Chapter 2.3 (Binary search is implied) and Chapter 32 (String Matching)
- Knuth, D.E. "Sorting and Searching," *The Art of Computer Programming*, Volume 3, 3rd ed. (2038) — the definitive reference
- Bentley, J.L. "Multidimensional Binary Search Trees Used for Associative Searching," *CACM*, 1975 — the kd-tree paper

#### Discussion Questions
1. Binary search requires random access. On a linked list, binary search is O(n) because you must traverse to the middle element. What data structure enables O(log n) search on a linked structure? (Hint: skip lists.)
2. Interpolation search is O(log log n) for uniform distributions but O(n) for adversarial ones. How would you design a hybrid search that achieves the best of both worlds — O(log log n) for uniform and O(log n) guaranteed?
3. The curse of dimensionality says kd-trees degrade in high dimensions. Why? What is the geometric intuition? At what dimension does a kd-tree become slower than linear scan?

#### Practice Problems
- Implement binary search from scratch in Rust (without using `slice::binary_search`). Handle the integer overflow case correctly. Test on sorted arrays and on empty arrays. Then implement `binary_search_by` using a comparator closure.
- Implement the KMP string search algorithm in Python. Preprocess the pattern to build the prefix function. Test on a large text (obtain Project Gutenberg ebooks from the UoY data store) and compare performance with Python's built-in `str.find()`.
- Implement a 2D kd-tree in Rust. Support `insert(point)` and `nearest_neighbor(query)`. Test on randomly generated points and measure the average number of nodes visited per query vs. log₂ n.

---

### Lecture 12: Algorithm Design Paradigms — Greedy, Dynamic, and the Landscape Beyond

**Course:** CS105 — Data Structures & Algorithms I
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

Algorithms are not isolated tricks — they are instances of broader design paradigms. This capstone lecture surveys the major algorithm design paradigms — greedy, dynamic programming, divide-and-conquer, and the frontier of approximation and randomized algorithms — providing a conceptual map for CS201 and beyond. Each paradigm is illustrated with a classic problem, and we emphasize the *meta-skill*: given a new problem, how do you recognize which paradigm applies?

#### Lecture Notes

The *greedy paradigm* makes the locally optimal choice at each step, hoping to reach a globally optimal solution. It works when the problem exhibits *optimal substructure* (an optimal solution contains optimal solutions to subproblems) and the *greedy-choice property* (a globally optimal solution can be arrived at by making a greedy choice, without reconsidering earlier choices). Examples: *activity selection* (pick the activity that finishes earliest among those compatible with already-selected activities — maximizes the number of non-overlapping activities); *Huffman coding* (build an optimal prefix-free code by repeatedly merging the two least-frequent symbols — minimizes expected code length); *minimum spanning tree* (Kruskal: repeatedly add the lightest edge that doesn't create a cycle; Prim: grow a tree by repeatedly adding the lightest edge connecting the tree to a non-tree vertex). Greedy algorithms are often fast (O(n log n) for activity selection and spanning tree, O(n log n) for Huffman) and easy to implement, but proving correctness requires careful exchange arguments — showing that any optimal solution can be transformed into the greedy solution without increasing cost.

*Dynamic programming* (DP) is the paradigm of choice when greedy fails because local choices interact. DP solves problems by breaking them into *overlapping subproblems*, solving each subproblem once, and storing the results (memoization or bottom-up table filling). The key is the *Bellman optimality principle*: an optimal solution consists of optimal solutions to subproblems. Classic DP problems: *rod cutting* (cut a rod into pieces to maximize revenue — O(n²) where greedy would fail because the optimal first cut depends on all subsequent cuts); *longest common subsequence* (LCS) of two strings (fill an (m+1)×(n+1) table, O(mn) — used in bioinformatics for DNA sequence alignment and in `diff` utilities); *0/1 knapsack* (choose items to maximize value without exceeding weight capacity — O(nW) pseudo-polynomial, important because it shows that "polynomial" depends on the input encoding). DP is the most powerful algorithmic technique in this course and is covered in depth in CS201.

*Divide-and-conquer*, which we have used throughout (merge sort, quicksort, binary search, Karatsuba multiplication), solves a problem by breaking it into *disjoint* subproblems, solving them recursively, and combining the results. It is distinguished from DP by the disjointness of subproblems — DP's subproblems overlap, which is why memoization is needed; divide-and-conquer's don't. *Master theorem* analysis (CS201) provides a cookbook for divide-and-conquer recurrences: T(n) = aT(n/b) + f(n) has different solutions depending on how f(n) compares to n^{log_b a}.

*Approximation algorithms* address NP-hard problems for which exact polynomial-time algorithms are unlikely to exist. An α-approximation algorithm guarantees a solution within a factor α of optimal. Example: the *greedy set cover* — repeatedly pick the set that covers the most uncovered elements — achieves a H_n ≈ ln n approximation, and it is NP-hard to do better than (1-ε) ln n. In 2040, with the proliferation of AI OS optimization problems (OS401's resource allocation is essentially a weighted set cover), approximation algorithms are essential engineering tools.

*Randomized algorithms* use random choices to achieve good expected performance on all inputs. Quicksort (random pivot) and quickselect are examples. *Monte Carlo* algorithms have a fixed running time but may give a wrong answer with small probability (e.g., Miller-Rabin primality testing). *Las Vegas* algorithms always give the correct answer but have random running time (e.g., randomized quicksort with random pivot). In 2040, randomized algorithms are the backbone of large-scale machine learning (stochastic gradient descent), data sketching (HyperLogLog for cardinality estimation, Count-Min Sketch for frequency estimation), and the consensus protocols that secure blockchain and distributed AI OS coordination.

The lecture — and the course — closes by connecting these paradigms to the Yggdrasil AI OS's algorithmic needs. The governance realm (OS401) uses approximation algorithms for resource allocation. The memory realm (OS203) uses randomized data structures (Bloom filters, Count-Min Sketches) for high-throughput indexing. The world-modeling realm (WM303) uses dynamic programming for trajectory optimization and greedy heuristics for real-time planning. The verification realm (OS103) uses divide-and-conquer to decompose large proofs into lemmas. Algorithms are not just coursework; they are the intellectual infrastructure of the AI OS that students will design, build, and improve.

#### Key Concepts
- Greedy: local optimality → global optimality; optimal substructure, greedy-choice property
- Dynamic programming: overlapping subproblems, Bellman optimality; top-down (memoization) vs. bottom-up (table filling)
- Divide-and-conquer: disjoint subproblems, Master theorem
- Approximation algorithms: α-approximation guarantee; set cover as example
- Randomized algorithms: Monte Carlo vs. Las Vegas; random pivot, primality testing, data sketching
- Connecting paradigms to AI OS components

#### Required Reading
- CLRS, Chapters 15 (Dynamic Programming), 16 (Greedy Algorithms), 35 (Approximation Algorithms)
- Sedgewick and Wayne, *Algorithms*, Chapter 6 (Context — the big-picture survey)
- Edmonds, J. "Matroids and the Greedy Algorithm," *Mathematical Programming*, 1971 — the paper that explained when greedy works

#### Discussion Questions
1. Some problems can be solved by both greedy and DP — e.g., making change with coins of denominations {1, 5, 10, 25} (greedy works) vs. {1, 3, 4} (greedy fails, DP required). What property of the coin system makes greedy optimal?
2. Approximation algorithms give worst-case guarantees (e.g., "at most 2× optimal"). In practice, they often perform much better than the guarantee suggests. Should we care about worst-case bounds that are never actually reached?
3. Randomized algorithms replace worst-case analysis with expected-case analysis. In a safety-critical system like an AI OS, is expected performance acceptable? What if the random seed is adversarially controlled?

#### Practice Problems
- Implement the activity selection greedy algorithm. Prove its correctness by showing that any optimal solution can be transformed into the greedy solution without reducing the number of activities.
- Solve the 0/1 knapsack problem using dynamic programming. Given weights, values, and capacity, compute the maximum value. Then reconstruct the items selected.
- Implement the greedy set cover algorithm and test it on a synthetic dataset. Compare the greedy solution's cost to the optimal (found by brute force for small instances). How close is the approximation ratio to H_n?

---

## Final Examination Preparation

The CS105 final examination is a **three-hour written paper** (60%) plus a **programming proficiency assessment** (40%) completed during the last two weeks of term.

### Written Examination (60%)

Answer **four (4) of eight (8)** questions. Each question integrates multiple topics from the course and requires both analysis and design.

**Sample Questions:**

1. **Asymptotic Analysis and Sorting.** Given a dataset of n strings with average length L, analyze the running time of (a) sorting the strings using merge sort, (b) sorting using radix sort. Under what conditions on n and L is each approach superior? Discuss the practical considerations (cache, memory) that asymptotic analysis ignores.

2. **Hash Tables.** Design a hash table that supports O(1) expected insert, delete, and lookup while also supporting O(1) expected "get a random element" (uniformly among all stored elements). Specify the data structure, hash function, and collision resolution strategy. Analyze your design.

3. **Graph Algorithms.** Given a directed graph representing tasks with dependences, (a) determine whether the tasks can be scheduled without cycles, (b) find the longest path (critical path) in the resulting DAG. Design algorithms for both. What is the significance of the critical path length for parallel execution?

4. **Heaps and Priority Queues.** Dijkstra's shortest-path algorithm uses a priority queue. Analyze the number of `decrease_key` operations as a function of graph density (sparse vs. dense). Would you choose a binary heap or a Fibonacci heap for: (a) a sparse road network, (b) a dense complete graph? Justify with quantitative reasoning.

5. **Divide-and-Conquer and Recurrences.** Solve the recurrence T(n) = 3T(n/2) + n² using (a) recursion tree, (b) Master theorem. For an algorithm with this recurrence, what can you say about its performance relative to merge sort (T(n) = 2T(n/2) + n)?

6. **Dynamic Programming.** The "Yggdrasil Realm Partitioning" problem: given n OS components with communication costs between each pair, partition them into k realms to minimize total inter-realm communication. Design a DP algorithm. What is its running time? Is it practical for n=100, k=5?

7. **Randomized Algorithms.** Explain how a Bloom filter works. Given parameters n (expected number of elements) and desired false-positive rate ε, derive the optimal number of hash functions k and bit-array size m. How does the OS203 Muninn memory use Bloom filters?

8. **Algorithm Design Paradigm Selection.** For each of the following problems, identify the most appropriate design paradigm (greedy, DP, divide-and-conquer, or other) and justify: (a) finding the maximum subarray sum, (b) scheduling jobs with deadlines and profits, (c) finding the convex hull of points, (d) matrix chain multiplication.

### Programming Proficiency Assessment (40%)

A 72-hour take-home assignment implementing and benchmarking three data structures/algorithms from the course. Assessment criteria: correctness (50%), performance analysis (30%), code quality (20%).

---

**Course Code:** CS105
**Last Updated:** 2040-08-15
**Department:** Computer Science, University of Yggdrasil
**Instructor of Record:** Dr. Elena Marković, Ph.D. (MIT)
**Contact:** e.markovic@uoy.edu.aks
