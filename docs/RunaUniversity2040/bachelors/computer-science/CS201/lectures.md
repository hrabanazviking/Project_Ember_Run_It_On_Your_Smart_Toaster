# CS201: Data Structures & Algorithms II
## Bachelor of Science in Computer Science — University of Yggdrasil, 2040

**Credits:** 4
**Prerequisites:** CS101 — Computational Thinking & Problem Solving; CS102 — Discrete Mathematics for CS; CS103 — Data Structures & Algorithms I
**Description:** This course elevates algorithmic reasoning from the linear and the tree-structured to the general and the intractable. Building on the asymptotic analysis, sorting, searching, and basic data structures of CS103, CS201 takes on the algorithmist's most powerful tools: graph algorithms (traversal, shortest paths, network flow), dynamic programming (the art of optimal substructure), NP-completeness (the boundary between the feasible and the intractable), and randomised algorithms (the deliberate use of chance to achieve simplicity, speed, or both). Each topic is motivated by real computational problems — routing in networks, parsing in compilers, scheduling in operating systems, alignment in bioinformatics, recommendation in e-commerce — and each algorithm is analysed rigorously for correctness and complexity. Students implement a portfolio of algorithms in Python and C++, and they complete a term project that applies algorithmic design to a problem of their choosing. The course is taught in the spirit of Norðrljós (Northern Lights): shining light on problems from unexpected angles, illuminating structure where none was visible before.

---

## Lecture 1: Graph Representations and Traversal — BFS, DFS, and the Topological Sort

A graph — a set of vertices connected by edges — is the most general data structure in the computer scientist's repertoire. Trees, linked lists, arrays, and hash tables are all restricted graphs; the graph is what remains when all the restrictions are lifted. The generality of graphs makes them the natural model for a vast range of computational problems: social networks (vertices are people, edges are friendships), the World Wide Web (vertices are pages, edges are hyperlinks), road networks (vertices are intersections, edges are roads), compiler internals (vertices are basic blocks, edges are control-flow transfers), and the dependency structure of build systems (vertices are compilation units, edges are dependencies). The first task of the graph algorithmist is representation — the choice of data structure that determines the efficiency of every subsequent operation.

The two canonical representations of a graph G = (V, E) are the **adjacency matrix** and the **adjacency list**. The adjacency matrix is an |V| × |V| array A, where A[i][j] = 1 if (i, j) ∈ E (for an unweighted graph) or A[i][j] = w where w is the weight of edge (i, j) (for a weighted graph). The adjacency matrix supports O(1) edge-existence queries — "is there an edge from i to j?" — but consumes Θ(|V|²) space and requires Θ(|V|) time to enumerate the neighbours of a vertex, even in a sparse graph. For dense graphs (|E| ≈ |V|²), the adjacency matrix is memory-efficient and algorithmically convenient; for sparse graphs (|E| ≪ |V|²) — which describe most real-world networks — it is wasteful. The adjacency list stores, for each vertex, a list (or array) of its outgoing neighbours. It consumes Θ(|V| + |E|) space and supports O(degree(v)) neighbour enumeration — optimal for sparse graphs and the default representation unless the graph is dense or edge-existence queries dominate.

**Breadth-First Search (BFS)** is the algorithm that explores a graph in concentric layers — all vertices at distance 1 from the source, then all at distance 2, and so on. BFS uses a queue: it enqueues the source, then repeatedly dequeues a vertex, examines its unexplored neighbours, and enqueues them. BFS runs in O(|V| + |E|) time (with an adjacency list) and produces two side-effects that are as valuable as the exploration itself: the **distance** from the source to every reachable vertex (the fewest edges in the path), and a **BFS tree** — a spanning tree rooted at the source whose edges are the "discovery edges" through which vertices were first reached. The BFS tree encodes the shortest paths from the source (in the unweighted sense), and it is the foundation of algorithms for bipartiteness testing (Lecture 3), connected components, and the "small-world" property of social networks.

**Depth-First Search (DFS)** is the algorithm that explores a graph by following a path as far as it can go before backtracking. DFS uses recursion (or an explicit stack): it visits a vertex, marks it as discovered, then recursively explores each undiscovered neighbour. DFS also runs in O(|V| + |E|) time and produces a **DFS forest** (a collection of DFS trees, one per connected component). The DFS forest classifies every edge of the graph into one of four types: **tree edges** (edges that are part of the DFS tree), **back edges** (edges that connect a vertex to an ancestor in the DFS tree — these indicate cycles in a directed graph), **forward edges** (edges that connect a vertex to a non-child descendant), and **cross edges** (edges that connect vertices in different branches of the tree). This classification is the key to many graph algorithms: cycle detection, topological sorting, and the computation of strongly connected components (Lecture 2).

The **topological sort** of a directed acyclic graph (DAG) is a linear ordering of its vertices such that for every directed edge (u, v), u appears before v in the ordering. Topological sort — which can be computed by DFS (by ordering vertices by decreasing finish time) or by Kahn's algorithm (iteratively removing vertices with in-degree 0) — is the algorithmic expression of dependency resolution: if vertices are tasks and edges are "must be done before" constraints, a topological sort is a valid execution order. Topological sort is the engine behind build systems (Make, Bazel), package managers (apt, pip), and instruction scheduling in compilers — and it is a prerequisite for many DP algorithms on DAGs, where the topological order provides a valid evaluation order.

**Required Reading:**
- Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest & Clifford Stein, *Introduction to Algorithms* (4th ed., 2040), chs. 20 (Graph Representations), 21 (BFS), 22 (DFS), 23 (Topological Sort)
- Robert Sedgewick & Kevin Wayne, *Algorithms* (4th ed., 2011/2039), chs. 4.1 (Undirected Graphs), 4.2 (Directed Graphs)
- Steven S. Skiena, *The Algorithm Design Manual* (3rd ed., 2038), chs. 5, 7
- Yggdrasil Graph Visualization Suite: BFS/DFS Module (2040)

**Discussion Questions:**
1. The adjacency matrix supports O(1) edge queries but uses Θ(|V|²) space. For what kinds of graphs — and what kinds of queries — is the matrix representation clearly superior?
2. BFS computes shortest paths in unweighted graphs. What happens when edges have weights — and why does BFS not generalise directly?
3. DFS classifies edges into four types. Why does the classification matter — and what would go wrong if we tried to detect cycles in a directed graph using BFS?

---

## Lecture 2: Strongly Connected Components and the Structure of Directed Graphs

A directed graph has a richer — and more subtle — connectivity structure than an undirected graph. In an undirected graph, connectivity is simple: two vertices are connected if there is a path between them, and the connected components partition the graph. In a directed graph, a path from u to v does not imply a path from v to u. The **strongly connected components (SCCs)** of a directed graph are the maximal subsets of vertices within which every pair is mutually reachable — for every u and v in the same SCC, there is a path from u to v and a path from v to u. The SCCs partition the vertices, and the **component graph** — formed by contracting each SCC into a single "super-vertex" and adding an edge from SCC A to SCC B if there is an edge from any vertex in A to any vertex in B — is always a DAG. The component graph reveals the "macro-structure" of the directed graph: the flow of information, the hierarchy of dependencies, the irreducible complexity.

The **Kosaraju-Sharir algorithm** computes SCCs in two passes of DFS — an elegant construction that reveals the deep connection between SCCs and the reversal of edges. **First pass:** perform DFS on the original graph G, recording the vertices in order of *finish time* (the order in which the DFS completes exploring each vertex). **Second pass:** perform DFS on the **reverse graph** G^R (obtained by reversing the direction of every edge), processing vertices in *decreasing* order of the finish times from the first pass. Each tree in the DFS forest of the second pass is an SCC. The algorithm runs in O(|V| + |E|) time — optimal — and its correctness is a small masterpiece of algorithmic reasoning: the vertex with the latest finish time in the first pass belongs to a "source" SCC in the component graph; reversing the edges turns source SCCs into sink SCCs; and visiting in reverse finish-time order ensures that each SCC is explored in isolation, without "leaking" into other SCCs.

**Tarjan's algorithm** — discovered independently by Robert Tarjan in 1972 — computes SCCs in a *single* DFS pass, using the clever concept of the **low-link value**: low[v] = the smallest discovery time of a vertex reachable from v (including v itself) by following tree edges and at most one back edge or cross edge. Vertices that share the same low-link value (and the same root) belong to the same SCC. Tarjan's algorithm is more space-efficient than Kosaraju-Sharir (it does not require building the reverse graph) and is the standard implementation in practice.

The **applications** of SCC decomposition are manifold. In program analysis, the call graph of a program — vertices are functions, edges are calls — can be decomposed into SCCs to identify **mutually recursive** functions (an SCC of size > 1) and to order the functions for separate compilation (the topological order of the component DAG). In the analysis of the Web, SCC decomposition reveals the "bow-tie" structure of the web graph: a giant SCC (the "core"), with "IN" (vertices that can reach the core but are not in it), "OUT" (vertices reachable from the core but not in it), and "tendrils" — a structure discovered by Broder et al. (2000) that remains one of the most influential results in web science. In Boolean satisfiability, the **implication graph** of a 2-SAT formula — where each variable x has two vertices (x and ¬x), and each clause (a ∨ b) yields two implications (¬a → b and ¬b → a) — can be decomposed into SCCs: the formula is satisfiable iff no variable x has x and ¬x in the same SCC. This reduces 2-SAT to SCC decomposition — linear time, elegant, and practical.

**Required Reading:**
- Thomas H. Cormen et al., *Introduction to Algorithms* (4th ed., 2040), ch. 22 (DFS), §22.5 (SCCs)
- Robert Tarjan, "Depth-First Search and Linear Graph Algorithms," *SIAM Journal on Computing* 1:2 (1972): 146–160
- Andrei Broder et al., "Graph Structure in the Web," *Computer Networks* 33:1–6 (2000): 309–320
- Sanjoy Dasgupta, Christos Papadimitriou & Umesh Vazirani, *Algorithms* (2006/2038), ch. 3
- Yggdrasil SCC Visualisation Module (2040)

**Discussion Questions:**
1. Kosaraju-Sharir uses two passes of DFS with a reversed graph. Tarjan uses one pass with low-link values. Under what circumstances would you choose each — and does the difference in constant factors matter?
2. The component graph of SCCs is always a DAG. What does this DAG tell us about the structure of the original graph — and how can we use it to answer reachability queries efficiently?
3. The web's "bow-tie" structure was a landmark empirical discovery. How would you design an algorithm to identify the IN, OUT, core, and tendril components — and how does this structure affect the design of web crawlers?

---

## Lecture 3: Shortest Paths — Dijkstra, Bellman-Ford, and the Hunt for Negative Cycles

The shortest-path problem — find the minimum-weight path from a source vertex s to every other vertex in a weighted graph — is one of the most practically important problems in algorithmics. It underlies GPS navigation (vertices are locations, edges are road segments, weights are travel times), network routing (vertices are routers, edges are links, weights are latency or cost), and the Viterbi algorithm for hidden Markov models (the trellis is a DAG, and the most likely sequence of hidden states is the shortest path). The history of shortest-path algorithms is a story of progressive generalisation: Dijkstra (1959) handles non-negative weights; Bellman-Ford (1958/1962) handles arbitrary weights but is slower; Johnson (1977) reduces the general case to the non-negative case; and the A* algorithm (Hart, Nilsson & Raphael, 1968) incorporates heuristics to speed up search in geometric spaces.

**Dijkstra's algorithm** is the crown jewel. It maintains a set S of vertices whose shortest-path distance from s is definitively known, and a priority queue Q of vertices not yet in S, keyed by the current best estimate of their distance. At each iteration, it extracts from Q the vertex u with the smallest estimate — call it d[u] — adds u to S, and **relaxes** every outgoing edge (u, v): if d[v] > d[u] + w(u, v), then d[v] is updated to d[u] + w(u, v). The algorithm terminates when all vertices are in S (or when the target vertex is extracted, for single-pair queries). Dijkstra's algorithm runs in O((|V| + |E|) log |V|) time when implemented with a binary heap (or O(|E| + |V| log |V|) with a Fibonacci heap) — and it is correct only when all edge weights are **non-negative**. The non-negativity requirement is not merely a detail; it is essential to the algorithm's greedy choice: once a vertex is extracted from the priority queue, its distance is final — and this is guaranteed only if there are no negative edges that could later improve it.

**Bellman-Ford** relaxes the non-negativity restriction at the cost of a higher running time: O(|V| · |E|). The algorithm makes |V| − 1 passes over all edges, relaxing each edge in turn. After the |V| − 1 passes, any shortest path — which has at most |V| − 1 edges (in a graph with no negative cycles) — will have been discovered. Bellman-Ford also detects **negative cycles**: if a |V|-th pass relaxes any edge further, a negative cycle exists (reachable from s). Negative cycles are not merely a mathematical curiosity — they represent arbitrage opportunities in currency exchange graphs (where vertices are currencies, edges are exchange rates, and the weight is −log(rate), turning a product of rates > 1 into a negative cycle), and they break the very notion of a "shortest" path (you can loop around the negative cycle indefinitely, making the weight arbitrarily low).

**Johnson's algorithm** solves the all-pairs shortest-paths problem — compute the shortest distance between every pair of vertices — for a graph that may have negative edges but no negative cycles. The naive approach — run Bellman-Ford from each vertex — takes O(|V|² · |E|), which is prohibitive. Johnson's insight is to **reweight** the edges so that all weights become non-negative, then run Dijkstra from each vertex. The reweighting uses a potential function derived from the shortest-path distances from a new "super-source" vertex (computed by Bellman-Ford). The result is O(|V|² log |V| + |V| · |E|) — asymptotically superior to Bellman-Ford for all-pairs, and competitive with Floyd-Warshall (O(|V|³), simpler but less flexible) for sparse graphs.

**Required Reading:**
- Thomas H. Cormen et al., *Introduction to Algorithms* (4th ed., 2040), chs. 22 (Shortest Paths: single-source), 23 (All-Pairs Shortest Paths)
- Edsger W. Dijkstra, "A Note on Two Problems in Connexion with Graphs," *Numerische Mathematik* 1 (1959): 269–271
- Richard Bellman, "On a Routing Problem," *Quarterly of Applied Mathematics* 16 (1958): 87–90
- Donald B. Johnson, "Efficient Algorithms for Shortest Paths in Sparse Networks," *JACM* 24:1 (1977): 1–13
- Andrew V. Goldberg & Chris Harrelson, "Computing the Shortest Path: A* Search Meets Graph Theory," *SODA* (2005): 422–432

**Discussion Questions:**
1. Dijkstra's algorithm requires non-negative edge weights. Why — and what would the algorithm compute if, by mistake, we ran it on a graph with negative edges but no negative cycles?
2. Bellman-Ford does |V| − 1 passes. Why |V| − 1 — and can we terminate early if no edges are relaxed in a pass?
3. Johnson's reweighting technique transforms negative edges into positive ones. Why does this transformation preserve the relative ordering of path lengths — and could we use it to run Dijkstra for single-source shortest paths on a graph with negative edges?

---

## Lecture 4: Minimum Spanning Trees — Prim, Kruskal, and the Greedy Paradigm

A **spanning tree** of a connected, undirected graph G = (V, E) is a subgraph T = (V, E_T) that is a tree (connected and acyclic) and includes all |V| vertices. A **minimum spanning tree (MST)** is a spanning tree whose total edge weight Σ_{e∈E_T} w(e) is minimum among all spanning trees. The MST problem is one of the simplest and most elegant optimisation problems in computer science — and its algorithms, Prim and Kruskal, are canonical examples of the **greedy paradigm**: at each step, make the locally optimal choice, and the globally optimal solution will emerge.

The **greedy-choice property** for MSTs — the mathematical reason that greedy algorithms work — is captured by the **cut property**: for any cut (a partition of V into two non-empty subsets S and V \ S), the minimum-weight edge crossing the cut belongs to *some* MST. The companion **cycle property** states: for any cycle in G, the maximum-weight edge on the cycle does *not* belong to any MST. These two properties — cut and cycle — are the yin and yang of MST algorithms, and every MST algorithm can be understood as a systematic application of one or the other.

**Kruskal's algorithm** (1956) applies the cycle property: it sorts all edges by weight and iterates through them in increasing order, adding an edge to the growing forest if and only if it does not create a cycle. The cycle check is performed by a **disjoint-set (union-find)** data structure: each vertex initially belongs to its own set; when considering edge (u, v), if u and v are in different sets, the edge is added to the MST, and the two sets are merged. Kruskal's algorithm runs in O(|E| log |E|) time (dominated by the edge sort), or O(|E| α(|V|)) if the edges are already sorted or can be sorted in linear time (bucket sort). The algorithm is simple, robust, and easy to parallelise — the edge sort is embarrassingly parallel.

**Prim's algorithm** (1957) applies the cut property: it grows a single tree from an arbitrary starting vertex, and at each step, it adds the minimum-weight edge that connects the current tree to a vertex not yet in the tree. Prim's algorithm is, in structure, identical to Dijkstra's algorithm — the priority queue holds vertices not yet in the tree, keyed by the minimum weight of an edge connecting them to the tree. Prim runs in O(|E| log |V|) with a binary heap (or O(|E| + |V| log |V|) with a Fibonacci heap) — essentially identical to Dijkstra.

The **MST as a data-structure problem** reveals an important lesson: the optimal algorithm depends on the density of the graph. For sparse graphs (|E| = O(|V|)), both Kruskal and Prim run in O(|V| log |V|) — essentially optimal. For dense graphs (|E| = Θ(|V|²)), Prim with a simple array (no heap) achieves O(|V|²) — optimal and simpler than the heap-based version. The algorithmist who knows only one MST algorithm will write suboptimal code for some inputs; the algorithmist who understands the trade-offs will choose the right tool for the graph at hand.

**2040 applications** of MSTs include the design of low-latency overlay networks (where the MST of the latency graph is the backbone), the clustering of data points (single-linkage clustering is exactly Kruskal's algorithm, stopped when the desired number of clusters is reached), and the reconstruction of phylogenetic trees (where the MST of genetic distance is a first approximation to the evolutionary tree).

**Required Reading:**
- Joseph B. Kruskal, "On the Shortest Spanning Subtree of a Graph and the Traveling Salesman Problem," *PAMS* 7 (1956): 48–50
- R.C. Prim, "Shortest Connection Networks and Some Generalizations," *BSTJ* 36 (1957): 1389–1401
- Thomas H. Cormen et al., *Introduction to Algorithms* (4th ed., 2040), ch. 21 (MSTs), ch. 19 (Disjoint Sets)
- Robert Tarjan, *Data Structures and Network Algorithms* (1983/2038), ch. 6

**Discussion Questions:**
1. The cut property and the cycle property are dual. Prove one from the other — or, failing that, explain why both perspectives are useful even if they are mathematically equivalent.
2. Kruskal's algorithm sorts all edges first; Prim's algorithm uses a priority queue. For a graph that is 99% sorted (edges are read from a mostly-sorted source), which algorithm is likely to be faster — and how could we adapt either to exploit the partial sorting?
3. The MST of a complete graph on n points in Euclidean space (where edge weights are Euclidean distances) can be computed in O(n log n) time, despite the O(n²) potential edges. How — and what does this teach us about exploiting geometric structure?

---

## Lecture 5: Introduction to Dynamic Programming — Optimal Substructure and Overlapping Subproblems

Dynamic programming (DP) is not a specific algorithm but a **design paradigm** — a strategy for solving optimisation problems that exhibit two properties: **optimal substructure** (an optimal solution can be constructed from optimal solutions of its subproblems) and **overlapping subproblems** (the same subproblems arise repeatedly, so caching their solutions — memoisation — avoids redundant computation). The name "dynamic programming" was coined by Richard Bellman in the 1950s, chosen to sound impressive — and vague — to his RAND Corporation employers, who were funding research into multi-stage decision processes. The name has nothing to do with computer programming; it refers to a "program" in the sense of a schedule or a plan.

The **core technique** of DP is to express the value of an optimal solution recursively in terms of the values of optimal solutions to smaller subproblems, and then to evaluate this recurrence in a systematic order — typically bottom-up, filling a table — that ensures each subproblem is solved only once. The alternative, **memoisation** (top-down DP), solves subproblems on demand and caches the results. Memoisation is often simpler to implement (the recurrence is translated directly into a recursive function with a cache) but may incur the overhead of recursion; bottom-up DP avoids recursion but requires the programmer to identify a valid evaluation order (typically a topological order of the dependency graph among subproblems).

The **Fibonacci numbers** — F(n) = F(n−1) + F(n−2), with F(0) = 0, F(1) = 1 — are the "hello world" of DP. The naive recursive computation takes exponential time (Θ(ϕⁿ)), because it redundantly recomputes the same subproblems billions of times. Memoisation reduces the time to O(n), and bottom-up DP — filling an array from left to right — does the same with O(1) space (storing only the last two values). The Fibonacci example illustrates a crucial principle: DP is effective when the subproblem graph is a DAG, and the DP table is filled in topological order.

The **0/1 knapsack problem** is the archetypal DP problem: given n items, each with weight wᵢ and value vᵢ, and a capacity W, choose a subset of items whose total weight does not exceed W and whose total value is maximised. The DP recurrence: let K(i, w) be the maximum value achievable using items 1…i with capacity w. Then K(i, w) = max(K(i−1, w), vᵢ + K(i−1, w − wᵢ)) if wᵢ ≤ w; otherwise K(i, w) = K(i−1, w). The base case: K(0, w) = 0 for all w. The table has (n+1) × (W+1) entries, and each entry is computed in O(1) time — so the algorithm runs in O(nW) time. This is **pseudopolynomial**: it is polynomial in the numeric value W, not in the bit-length of W (log W). When W is large, O(nW) is impractical, and knapsack is NP-hard — a distinction that this lecture makes concrete.

**Longest Common Subsequence (LCS)** is the second archetypal DP problem: given two sequences X = x₁…ₘ and Y = y₁…ₙ, find the longest sequence that is a subsequence of both. Applications: diff (the Unix command that compares two files), bioinformatics (aligning DNA sequences), and plagiarism detection. The recurrence: let L(i, j) be the LCS length of prefixes X[1…i] and Y[1…j]. If xᵢ = yⱼ, then L(i, j) = 1 + L(i−1, j−1); otherwise, L(i, j) = max(L(i−1, j), L(i, j−1)). The table fills in O(mn) time.

**Required Reading:**
- Richard Bellman, *Dynamic Programming* (1957/2003), chs. 1–3
- Thomas H. Cormen et al., *Introduction to Algorithms* (4th ed., 2040), ch. 14 (Dynamic Programming)
- Jon Kleinberg & Éva Tardos, *Algorithm Design* (2006/2038), ch. 6
- Steven S. Skiena, *The Algorithm Design Manual* (3rd ed., 2038), ch. 10
- David J.C. MacKay, *Information Theory, Inference, and Learning Algorithms* (2003/2039), ch. 16 (DP and message passing)

**Discussion Questions:**
1. Memoisation (top-down) and bottom-up DP both achieve O(nW) for knapsack. In what situations is one preferable to the other — and what are the hidden costs of recursion (stack depth, cache behaviour) that the asymptotic analysis obscures?
2. The 0/1 knapsack is NP-hard, yet the DP algorithm runs in O(nW) — which is polynomial in W. Explain why this does not resolve the P vs. NP question — and what "pseudopolynomial" means precisely.
3. The DP recurrence for LCS can be extended to compute the actual subsequence (not just its length) by backtracking through the DP table. How much memory does backtracking require, and is there a way to recover the LCS without storing the full table?

---

## Lecture 6: Advanced Dynamic Programming — Matrix Chain, Edit Distance, and DP on Trees

Dynamic programming is a universe, not a recipe. This lecture explores three advanced domains where DP reveals its full power: the optimisation of computation itself (matrix chain multiplication), the measurement of similarity (edit distance), and the extension of DP to non-linear structures (trees).

The **matrix chain multiplication** problem: given a chain of n matrices A₁, A₂, …, Aₙ, where Aᵢ has dimensions pᵢ₋₁ × pᵢ, find the parenthesisation that minimises the total number of scalar multiplications. The product of matrices is associative — (AB)C = A(BC) — but the cost of multiplication is not: multiplying a 10×100 matrix by a 100×5 matrix costs 10·100·5 = 5000 scalar multiplications, while multiplying a 100×5 by a 5×50 costs 100·5·50 = 25,000 — so the parenthesisation matters enormously. The DP recurrence: let m[i, j] be the minimum cost to multiply the chain Aᵢ…Aⱼ. Then m[i, j] = min_{i ≤ k < j} (m[i, k] + m[k+1, j] + pᵢ₋₁ pₖ pⱼ). The base case: m[i, i] = 0. The evaluation order: chains of length ℓ = 2, 3, …, n. The time complexity is O(n³) — cubic, but optimal (assuming no faster matrix multiplication algorithm is exploited, which is itself an active research frontier in 2040 with the rise of α-Tensor-based multiplication schemes).

The **edit distance (Levenshtein distance)** problem: given two strings A and B, find the minimum number of operations — insertions, deletions, and substitutions — to transform A into B. Edit distance is the foundation of spell checkers, fuzzy search, and the diff algorithm. The recurrence: let D(i, j) be the edit distance between A[1…i] and B[1…j]. Then D(i, j) = min(D(i−1, j) + 1, D(i, j−1) + 1, D(i−1, j−1) + (A[i] ≠ B[j] ? 1 : 0)). The base cases: D(i, 0) = i, D(0, j) = j. The table fills in O(mn) time. Variants: the **Needleman-Wunsch algorithm** for global sequence alignment in bioinformatics uses a similar recurrence but with a scoring matrix that assigns different costs to different substitutions (a purine-to-purine substitution may be less "costly" than purine-to-pyrimidine). The **Smith-Waterman algorithm** modifies the recurrence for local alignment — finding the most similar subsequence rather than the most similar whole sequence.

**DP on trees** extends the paradigm to problems where the subproblems are defined on a rooted tree, and the optimal solution at a node depends on the optimal solutions of its children. The classic problem is **maximum independent set on a tree**: given a tree with vertex weights w(v), choose a subset of vertices, no two adjacent, maximising total weight. The DP recurrence: for each node v, define two values: include[v] = w(v) + Σ_{child c} exclude[c] (if we include v, we must exclude all its children), and exclude[v] = Σ_{child c} max(include[c], exclude[c]) (if we exclude v, each child may be included or excluded, independently). A post-order traversal (children before parent) computes both values for every node in O(n) time. The technique generalises to "DP on trees" for problems with optimal substructure on tree-structured data — and it is the computational foundation of **phylogenetic tree reconstruction**, **syntax-tree optimisation in compilers**, and the **max-sum algorithm on trees** (a special case of belief propagation in graphical models).

**Required Reading:**
- Thomas H. Cormen et al., *Introduction to Algorithms* (4th ed., 2040), ch. 14 (§14.2, matrix chain), §14.4 (LCS and edit distance)
- Dan Gusfield, *Algorithms on Strings, Trees, and Sequences* (1997/2039), chs. 11–12
- Vladimir I. Levenshtein, "Binary Codes Capable of Correcting Deletions, Insertions, and Reversals," *Soviet Physics Doklady* 10:8 (1966): 707–710
- Richard Durbin, Sean R. Eddy, Anders Krogh & Graeme Mitchison, *Biological Sequence Analysis* (1998/2038), chs. 2–3

**Discussion Questions:**
1. Matrix chain multiplication takes O(n³) — but the optimal parenthesisation can be found in O(n log n) if we exploit the fact that the optimal tree is always a *binary search tree* on the dimensions. What does this reveal about the gap between general DP and exploiting structure?
2. Edit distance and LCS are closely related: edit distance with only insertions and deletions is exactly |A| + |B| − 2 · LCS. Why does adding substitutions break this relationship — and how does the nature of the problem change?
3. DP on trees works because trees have no cycles — the subproblem DAG is exactly the tree itself. What happens when the graph has cycles — and how does the **junction tree algorithm** (for general graphical models) extend DP to cyclic graphs?

---

## Lecture 7: NP-Completeness — The Boundary Between the Feasible and the Intractable

The most profound question in theoretical computer science — P versus NP — asks whether every problem whose solution can be **verified** quickly (in polynomial time) can also be **found** quickly. The question was crystallised independently by Stephen Cook (1971) and Leonid Levin (1973), building on the earlier work of John Edmonds (who introduced the notion of a "good" — polynomial-time — algorithm in 1965) and Jack Edmonds and Alan Cobham (who articulated the **Cobham-Edmonds thesis**: the class of feasible problems is exactly P, the set of decision problems solvable by a deterministic Turing machine in polynomial time). NP is the class of decision problems whose solutions can be **verified** in polynomial time by a non-deterministic Turing machine — equivalently, for which a "certificate" (a proposed solution) can be checked in polynomial time. The question "does P = NP?" has motivated fifty years of research, a million-dollar Clay Millennium Prize, and a deep structural understanding of computation — and we still do not know the answer.

The concept of **NP-completeness** is the engine that drives the theory. A problem L is NP-complete if (1) L ∈ NP and (2) every problem in NP is **polynomial-time reducible** to L (written L' ≤ₚ L): given an instance x of any problem L' ∈ NP, we can transform it in polynomial time to an instance f(x) of L such that x ∈ L' iff f(x) ∈ L. If *any* NP-complete problem can be solved in polynomial time, then P = NP; if *any* NP-complete problem requires exponential time, then P ≠ NP. The first NP-complete problem was **Boolean satisfiability (SAT)** — Cook's theorem (1971) proved that every problem in NP reduces to SAT. The proof is a tour de force: it encodes the entire computation of a non-deterministic Turing machine as a Boolean formula, such that the formula is satisfiable iff the machine accepts. Cook's theorem opened the floodgates: Richard Karp (1972) proved 21 more problems NP-complete (including clique, vertex cover, Hamiltonian cycle, and knapsack), and today thousands of problems — from scheduling to protein folding to optimal circuit layout — are known to be NP-complete.

The practical import of NP-completeness is a **weapon of mass recognition**. When you encounter a new computational problem, and you suspect it is hard, the NP-completeness framework gives you a systematic method: (1) restate the problem as a decision problem, (2) show that it is in NP (exhibit a polynomial-time verifier), (3) reduce a known NP-complete problem to yours. If you succeed, you have proved that your problem is NP-hard — and you can stop looking for an efficient exact algorithm and turn your attention to approximation, heuristics, special cases, or exponential algorithms that are feasible for small instances.

**The 2040 landscape** of complexity theory has been enriched by several developments. **Fine-grained complexity** asks not just "is this problem in P?" but "what is the exact exponent?" — proving, under plausible conjectures (the Strong Exponential Time Hypothesis, SETH), that problems like edit distance cannot be solved in O(n^(2−ε)) time, and that the all-pairs shortest paths problem cannot be solved in O(n^(3−ε)) time. **Parameterised complexity** — pioneered by Downey and Fellows in the 1990s — identifies structural parameters (treewidth, vertex cover number, feedback edge set) such that problems that are NP-hard in general become fixed-parameter tractable (FPT) when the parameter is small. This has transformed the practice of algorithm design: rather than despairing when a problem is NP-hard, we ask "what is the parameter that bounds the complexity in my data?"

**Required Reading:**
- Stephen A. Cook, "The Complexity of Theorem-Proving Procedures," *STOC* (1971): 151–158
- Richard M. Karp, "Reducibility Among Combinatorial Problems," in *Complexity of Computer Computations* (1972): 85–103
- Michael R. Garey & David S. Johnson, *Computers and Intractability: A Guide to the Theory of NP-Completeness* (1979/2040 edition)
- Sanjeev Arora & Boaz Barak, *Computational Complexity: A Modern Approach* (2009/2038), chs. 1–3
- Rodney G. Downey & Michael R. Fellows, *Fundamentals of Parameterized Complexity* (2013/2040), chs. 1–3

**Discussion Questions:**
1. The Cook-Levin theorem proves that SAT is NP-complete by encoding a Turing machine's computation as a Boolean formula. The proof is constructive but the formula is enormous. What does this tell us about the relationship between problem reduction and practical algorithmic difficulty?
2. If P = NP, the consequences would be enormous — but the proof might be non-constructive (it might not give us a practical polynomial algorithm for SAT). Would a non-constructive proof of P = NP change how we approach computational problems?
3. Parameterised complexity provides an escape hatch: problems that are NP-hard in general become FPT when a parameter is small. Is treewidth the "right" parameter for most graph problems — and what other parameters capture practical tractability?

---

## Lecture 8: Coping with NP-Completeness I — Approximation Algorithms

When a problem is NP-complete, the algorithmist's instinct shifts from "solve it exactly, fast" to "solve it approximately, with a guarantee." An **approximation algorithm** for an optimisation problem runs in polynomial time and produces a solution whose value is within a provable factor of the optimal value. The **approximation ratio** ρ(n) is the worst-case ratio between the value of the algorithm's solution and the optimal value: for a minimisation problem, ALG/OPT ≤ ρ; for a maximisation problem, OPT/ALG ≤ ρ. The quest for tight approximation ratios — and for proofs that certain ratios cannot be improved (unless P = NP) — is the central thread of modern approximation algorithms.

The **greedy approximation for set cover** is the simplest illustration. Given a universe U of n elements and a collection S of m subsets of U with costs c(S), choose a minimum-cost subcollection that covers all elements. The greedy algorithm — at each step, choose the set that minimises cost per newly covered element — achieves an approximation ratio of H_n ≈ ln n. This is essentially optimal: Feige (1998) proved that set cover cannot be approximated to within (1 − ε) ln n unless NP ⊆ DTIME(n^(log log n)). The proof of the greedy approximation ratio uses a beautiful charging argument: each time an element is covered, charge its cost to the sets in the optimal solution that cover it — and the harmonic sum emerges naturally.

The **Christofides algorithm** for the metric TSP (travelling salesman problem with triangle inequality) achieves a 3/2-approximation — a classic result that, remarkably, has not been improved for general metrics since 1976. The algorithm: (1) compute an MST T, (2) find a minimum-weight perfect matching M on the odd-degree vertices of T, (3) the multigraph T ∪ M is Eulerian (all vertices have even degree), (4) take an Eulerian tour and shortcut it (skip repeated vertices) to obtain a Hamiltonian cycle. The cost of T is at most OPT (removing any edge from the optimal tour yields a spanning tree). The cost of M is at most OPT/2 (the optimal tour on the odd-degree vertices can be shortcut into two matchings, one of which has weight ≤ OPT/2). So the total is at most 1.5 · OPT. The elegance of Christofides is that it combines two polynomial-time solvable problems — MST and minimum-weight perfect matching — to approximate an NP-hard problem.

The **fully polynomial-time approximation scheme (FPTAS)** for knapsack is a different kind of achievement: for any ε > 0, the algorithm produces a solution within a factor (1 − ε) of optimal in time poly(n, 1/ε) — fully polynomial because the running time is polynomial in both n and 1/ε. The idea is to scale the item values down (rounding vᵢ to ⌊vᵢ / K⌋ for K = (ε · max vᵢ) / n), solve the resulting problem exactly by DP (which is fast because the scaled values are small integers), and bound the error introduced by the rounding. The FPTAS for knapsack is a template: many NP-hard problems with pseudopolynomial algorithms admit an FPTAS by scaling and rounding.

The **2040 frontier** of approximation algorithms includes **approximation algorithms for problems on large graphs** — where the graph is too large to fit in memory, and algorithms must operate in streaming or distributed models — and **approximation-preserving reductions** that let us transfer inapproximability results from one problem to another (the PCP theorem and its descendants).

**Required Reading:**
- Vijay V. Vazirani, *Approximation Algorithms* (2003/2040), chs. 1–5, 13–15
- David P. Williamson & David B. Shmoys, *The Design of Approximation Algorithms* (2011/2039), chs. 1–3
- Nicos Christofides, "Worst-Case Analysis of a New Heuristic for the Travelling Salesman Problem," GSIA, Carnegie-Mellon (1976)
- Uriel Feige, "A Threshold of ln n for Approximating Set Cover," *JACM* 45:4 (1998): 634–652

**Discussion Questions:**
1. The greedy set cover algorithm achieves H_n ≈ ln n, and this is essentially optimal (modulo complexity assumptions). But for specific instances — e.g., vertex cover — better approximations exist. Why does the hardness of the general case not preclude a better algorithm for the special case?
2. Christofides' 3/2-approximation for metric TSP has stood since 1976. Why hasn't it been improved — and what complexity-theoretic barriers (e.g., the "integrality gap" of the Held-Karp relaxation) prevent better approximation?
3. An FPTAS provides arbitrarily good approximation in time polynomial in 1/ε. But as ε → 0, the running time grows. At what ε does the FPTAS become slower than an exact exponential algorithm — and how do we decide which approach to use?

---

## Lecture 9: Coping with NP-Completeness II — Exact Exponential Algorithms and Constraint Programming

Approximation algorithms provide guarantees but may leave a gap. When the gap is unacceptable — when the solution must be exact — the algorithmist turns to **exact exponential algorithms**: algorithms whose worst-case running time is exponential in the input size, but whose exponent is small enough — and whose pruning heuristics are effective enough — to be practical for instances of moderate size. The design of exact exponential algorithms is a craft: it combines worst-case analysis (to prove that the algorithm is not merely heuristic), parameterised analysis (to identify the structural features that make instances hard or easy), and engineering (to implement pruning rules that dramatically outperform the worst-case bound on real data).

The **branch-and-bound** framework is the foundation. The algorithm maintains a **branching** rule that partitions the solution space into disjoint subspaces, and a **bounding** rule that computes, for each subspace, a lower bound (for minimisation) on the best solution within it. If the lower bound exceeds the value of the best solution found so far (the **incumbent**), the subspace is pruned — discarded with no further exploration. Branch-and-bound is a meta-algorithm: its power depends on the quality of the bounds and the order of exploration. For the TSP, the Held-Karp lower bound — the value of the minimum spanning tree on the remaining vertices plus the cheapest two edges incident to each — is strong enough to solve instances with thousands of cities, despite TSP being NP-hard.

The **backtracking search** for constraint satisfaction problems (CSPs) — graph colouring, Boolean satisfiability, scheduling — is branch-and-bound specialised for feasibility (rather than optimisation). Modern SAT solvers (CDCL — Conflict-Driven Clause Learning), which can solve industrial SAT instances with millions of variables, are a triumph of backtracking enhanced by: (1) **unit propagation** (simplifying the formula after each decision), (2) **conflict analysis** (learning new clauses from failures to prune the search), (3) **activity-based heuristics** (VSIDS — choosing variables that appear in recent conflicts), and (4) **restarts** (periodically abandoning the current search to exploit newly learned clauses). The CDCL solver is a case study in how theoretical worst-case bounds (exponential) can be side-stepped by engineering for the instances that actually arise.

**Parameterised exact algorithms** use the parameter k — the "distance from triviality" — to achieve running times of the form f(k) · n^O(1), where f may be exponential but n^O(1) is polynomial. The **vertex cover** problem — find a set of at most k vertices that touches every edge — exemplifies the approach: a simple branching algorithm chooses an edge (u, v), and branches: either u is in the cover, or v is in the cover. The recurrence T(k) ≤ T(k−1) + T(k−1) = 2 T(k−1) gives T(k) = O(2ᵏ · n), and with more sophisticated branching rules, the base 2 can be reduced to 1.2738ᵏ. Parameterised exact algorithms are practical when k is small (tens, not hundreds), and they provide a smooth trade-off between exactness and efficiency that approximation algorithms do not.

**Required Reading:**
- F.V. Fomin & D. Kratsch, *Exact Exponential Algorithms* (2010/2038), chs. 1–3
- Armin Biere, Marijn Heule, Hans van Maaren & Toby Walsh (eds.), *Handbook of Satisfiability* (2nd ed., 2039), chs. 1–4, 8
- Rolf Niedermeier, *Invitation to Fixed-Parameter Algorithms* (2006/2040), chs. 1, 3–4
- Donald E. Knuth, *The Art of Computer Programming*, Vol. 4B: *Combinatorial Algorithms, Part 2* (in preparation/2040 fascicles), §7.2.2 (Backtracking)

**Discussion Questions:**
1. CDCL SAT solvers solve industrial instances with millions of variables, despite SAT being NP-complete. What properties of "industrial" instances make them tractable — and can these properties be formalised?
2. The branching factor for vertex cover can be reduced from 2 to 1.2738 using more sophisticated branching rules. What is the limiting factor — can the base be made arbitrarily close to 1, or is there a theoretical barrier?
3. Branch-and-bound and backtracking are general frameworks. What makes a good bounding function — and how do we trade off the time to compute the bound against the pruning it achieves?

---

## Lecture 10: Randomized Algorithms — Monte Carlo, Las Vegas, and the Power of Chance

A **randomised algorithm** flips coins — it makes random choices during its execution — and its behaviour (running time, output, or both) is a random variable. The deliberate use of randomness can achieve results that are impossible (or impractical) for deterministic algorithms: simpler code, faster expected running time, or solutions to problems for which no efficient deterministic algorithm is known. The two families of randomised algorithms are **Las Vegas** — the output is always correct, but the running time is a random variable (e.g., randomised quicksort, where the pivot is chosen randomly, and the expected running time is O(n log n)) — and **Monte Carlo** — the running time is fixed, but the output may be incorrect with some (small, controllable) probability (e.g., the Miller-Rabin primality test, which may falsely report a composite number as prime with probability at most 1/4 per test).

The **randomised min-cut algorithm** (Karger, 1993) is a masterpiece of simplicity and elegance. The problem: given an undirected graph, find a cut (a partition of the vertices into two non-empty sets) that minimises the number of crossing edges. Karger's algorithm: repeatedly choose an edge uniformly at random and **contract** it (merge its two endpoints into a single super-vertex, keeping parallel edges), until only two vertices remain. The edges between these two super-vertices form a cut. The probability that this cut is a minimum cut is at least 1 / C(|V|, 2) — which is small. But the algorithm is fast (O(|V|²)), and by repeating it O(|V|² log |V|) times, the probability of never finding a minimum cut is driven below 1/|V|. The analysis — that a specific minimum cut survives all |V| − 2 contractions with probability at least 2/(|V|(|V|−1)) — is a gem of probabilistic reasoning: at each step, the minimum cut has size k, the contracted edge is one of ≥ k|V|/2 edges (since every vertex has degree ≥ k), so the probability the contracted edge is *in* the minimum cut is ≤ 2/|V| — and multiplying the survival probabilities yields the bound.

The **hashing** application of randomness (already discussed in CS107) is the computational workhorse: **universal hashing** (Carter & Wegman, 1979) guarantees that for any pair of distinct keys, the probability of collision is at most 1/m (the reciprocal of the table size), providing the randomness that probabilistic analyses assume — without requiring a truly random hash function (which would need too many bits to specify).

The **Monte Carlo method** — estimating a quantity by random sampling — is, in the 2040s, the foundation of Bayesian inference (Markov chain Monte Carlo), of the evaluation of AI systems (bootstrapping for confidence intervals on benchmark scores), and of the rendering of photorealistic images (path tracing, which samples light paths randomly). The convergence rate — O(1/√n) independent of dimension — makes Monte Carlo the method of choice for high-dimensional integration.

**Required Reading:**
- Rajeev Motwani & Prabhakar Raghavan, *Randomized Algorithms* (1995/2040), chs. 1–4
- Michael Mitzenmacher & Eli Upfal, *Probability and Computing* (2nd ed., 2038), chs. 1–2, 5
- David R. Karger, "Global Min-Cuts in RNC, and Other Ramifications of a Simple Min-Cut Algorithm," *SODA* (1993): 21–30
- J. Lawrence Carter & Mark N. Wegman, "Universal Classes of Hash Functions," *JCSS* 18:2 (1979): 143–154

**Discussion Questions:**
1. Karger's min-cut algorithm has probability of success 2/(n(n−1)) — tiny. Why is repeating O(n² log n) times acceptable, and what does this say about the relationship between success probability and running time in Monte Carlo algorithms?
2. A Las Vegas algorithm is always correct, and its expected running time is good — but the actual running time is unbounded. How do we handle the tail risk — the (tiny but non-zero) chance that the algorithm takes centuries?
3. Universal hashing provides probabilistic guarantees — but real hash functions (SHA-256, BLAKE3) are deterministic. How do we justify using deterministic hash functions in randomised algorithms — and what is the formal notion of a "random oracle"?

---

## Lecture 11: Graph Algorithms in the 2040s — Streaming, Distributed, and Learned Graph Processing

The graph problems studied in classical algorithmics — shortest paths, connectivity, clustering — assume that the graph fits in memory and that we have random access to all vertices and edges. In the 2040s, these assumptions are routinely violated. The **web graph** has trillions of edges; the **social graph** of a large platform has billions of vertices; the **knowledge graph** of an AI system is continuously updated. Processing such graphs requires new algorithmic models — streaming, distributed, and learned — that trade completeness and exactness for speed and scalability.

**Graph streaming algorithms** process the graph as a sequence of edges (or edge insertions and deletions), using memory that is sublinear (ideally polylogarithmic) in the size of the graph. The classic problem is **connected components** in the semi-streaming model (O(n polylog n) memory, where n = |V|): maintain a spanning forest, merging components as edges arrive, with a union-find structure. For problems like shortest paths and matching, the semi-streaming model can achieve constant-factor approximations but not exact solutions (provably — lower bounds from communication complexity). The **sketching** approach — pioneered for graph problems by Ahn, Guha, and McGregor (2012) — maintains a small random linear projection (a sketch) of the graph's adjacency matrix or edge incidence matrix, from which properties like connectivity and bipartiteness can be tested with high probability.

**Distributed graph processing** — in frameworks like Pregel (Google, 2010), GraphX (Spark), and the 2040 standard, the **Yggdrasil Distributed Graph Engine (YDGE)** — partitions the graph across hundreds or thousands of machines, each holding a subset of vertices and their incident edges. The computational model is **vertex-centric**: each vertex maintains a state, receives messages from its neighbours, updates its state, and sends messages to its neighbours — iterating until convergence (for iterative algorithms like PageRank) or until a termination condition is met (for BFS or shortest paths). The challenge is **communication**: the graph partition must minimise edge cuts (to reduce cross-machine messages), and the algorithm must be designed to tolerate asynchrony and stragglers (the "tail at scale" problem).

The **learned graph algorithms** of the 2040s integrate machine learning into the algorithmic loop. A small neural network is trained to predict, for a given graph and a given problem, which algorithmic choices (branching decisions, pivot selections, edge ordering) will lead to the fastest solution. The learned algorithm is not a black box — it is a classical algorithm with a learned heuristic. For example, **learned Dijkstra** uses a neural network to predict which vertices are likely to be on the shortest path and prunes the search accordingly — trading a small probability of suboptimality for a large speedup. **Learned branch-and-bound** for integer programming — the 2040 state of the art for supply-chain optimisation — uses reinforcement learning to choose branching variables, outperforming decades of hand-tuned heuristics.

**Required Reading:**
- Andrew McGregor, "Graph Stream Algorithms: A Survey," *SIGMOD Record* 43:1 (2014): 9–20
- Grzegorz Malewicz et al., "Pregel: A System for Large-Scale Graph Processing," *SIGMOD* (2010): 135–146
- Ahn, Guha & McGregor, "Analyzing Graph Structure via Linear Measurements," *SODA* (2012): 459–467
- Elias Khalil et al., "Learning to Branch," *ICML* (2016), and follow-up work through 2040
- Yggdrasil Distributed Graph Engine (YDGE) Documentation (2040)

**Discussion Questions:**
1. The semi-streaming model allows O(n polylog n) memory — enough to store a spanning forest but not the full graph. What graph problems *require* more than semi-streaming memory, and how do we prove this?
2. Learned algorithms use ML to guide the algorithmic search — but the ML model itself takes time to evaluate. When does the speedup from better decisions outweigh the cost of inference — and how do we analyse this trade-off formally?
3. Vertex-centric distributed graph processing is elegant but can be communication-heavy. What alternatives — subgraph-centric, edge-centric — exist, and what classes of algorithms do they make more efficient?

---

## Lecture 12: The Algorithmic Imagination — From Problem to Proof to Program

The final lecture steps back from specific algorithms and problems to reflect on the craft of algorithmic design — the mental habits, the heuristics, the ways of seeing that distinguish the skilled algorithmist. Algorithmic design is not a mechanical process of applying templates; it is a creative act of seeing a problem from the right angle, of finding the structure that simplifies, of knowing when to generalise and when to specialise. The twelve lectures of CS201 have surveyed the canonical algorithms; this lecture asks: what patterns of thought produced them?

The **first heuristic** of algorithm design is **reduction**: transform your problem into a problem you already know how to solve. The shortest-path problem in a DAG reduces to topological sort followed by one pass of relaxation. The 2-SAT problem reduces to SCC decomposition. The maximum bipartite matching reduces to max flow. The algorithmist who has a rich library of "known problems" — and the ability to see the structural isomorphism between a new problem and a known one — is never starting from scratch. The corollary is: build your library. Every algorithm you learn is a tool, and the more tools you have, the more problems you can recognise.

The **second heuristic** is **simplification**: can you solve a restricted version of the problem first, and then extend? Dijkstra solved the single-source shortest-paths problem for non-negative weights first; later, the restriction was lifted. Kruskal and Prim solved the MST problem on graphs with distinct edge weights (where the MST is unique); the extension to equal weights is straightforward. The knapsack problem without weights (the subset-sum problem) is solvable by DP; adding weights introduces the value dimension. The algorithmist who is stuck on the general problem should ask: what special case can I solve — and what is the gap between the special case and the general problem?

The **third heuristic** is **abstraction**: identify the essential structure and ignore the rest. The graph is an abstraction of a network; the MST is an abstraction of the "least expensive way to connect everything"; the DP table is an abstraction of the space of subproblem solutions. The algorithmist who can abstract — who can see that a scheduling problem is a shortest-path problem on a DAG of states, or that a parsing problem is a DP on the substring decomposition — sees through the surface complexity to the algorithmic core.

The **Norse algorithmic imagination** — the connection between the algorithmic thinking taught at Yggdrasil and the intellectual traditions of the North — values simplicity, directness, and the elegance that emerges from deep engagement with complexity. The rune-carver who selects the right rune for the right sound is making an algorithmic choice. The skald who composes a dróttkvætt stanza — a metre of extraordinary complexity, with internal rhyme, alliteration, and a fixed syllable count — is solving a constraint satisfaction problem. The Norse intellectual tradition, often stereotyped as "merely" martial, is in fact a tradition of pattern, structure, and the creative resolution of constraints — and it is this tradition that the Algorithmic Imagination course at Yggdrasil celebrates and extends into the computational domain.

**Required Reading:**
- George Pólya, *How to Solve It* (2nd ed., 1957/2040), entire
- Donald E. Knuth, *The Art of Computer Programming*, Vol. 1 (3rd ed., 1997/2038), §1.4 (on algorithmic thinking)
- Jon Kleinberg & Éva Tardos, *Algorithm Design* (2006/2038), ch. 1 (Introduction to Algorithm Design)
- Edsger W. Dijkstra, "The Humble Programmer," *ACM Turing Lecture* (1972)
- University of Yggdrasil Algorithmic Imagination Reader (2040) — selected excerpts from the Eddas demonstrating structural and combinatorial thinking

**Discussion Questions:**
1. Pólya's *How to Solve It* was written for mathematicians in 1945, but it has become a classic text for computer scientists. What aspects of Pólya's method transfer to algorithm design — and what aspects of algorithmic thinking are *not* captured by mathematical problem-solving?
2. The "reduction" heuristic works only if you have a library of known problems to reduce to. How do you build that library — and how do you maintain the ability to recognise structural isomorphisms across domains?
3. The Norse skalds composed in dróttkvætt — a metre with strict constraints on syllable count, alliteration, and internal rhyme. Is this a useful metaphor for algorithm design — or is it merely ornamental? Can constraints that seem purely aesthetic sharpen the mind for constraints that are computational?

---

## Final Examination Preparation

The final examination for CS201 consists of a three-hour written examination (60% of the final grade) and an algorithmic design project (40%). The written examination requires you to answer four questions from a choice of eight, each combining algorithm design, complexity analysis, and proof of correctness. The project requires you to select a computational problem (from the Yggdrasil Problem Repository or from your own interests), design and implement at least two algorithmic approaches (exact and approximate, or deterministic and randomised, or sequential and parallel), analyse their performance empirically and theoretically, and write a report (2500–3500 words) presenting the problem, the algorithms, the analysis, and the lessons learned.

### Sample Examination Questions

1. **(Graph Traversal and SCCs)** A directed graph represents the "call graph" of a large software system: vertices are functions, and an edge (u, v) means function u calls function v. (a) Design an algorithm to identify all functions that are part of a mutual recursion cycle (i.e., belong to an SCC of size ≥ 2). (b) Explain how to order the functions for separate compilation — i.e., if f calls g, then f must be compiled after g (or they must be in the same SCC). (c) Discuss how your algorithm would handle the addition of a new function — must the entire SCC decomposition be recomputed?

2. **(Shortest Paths)** You are designing the routing algorithm for a delivery drone network. The graph has vertices (charging stations) and edges (flight corridors), with edge weights that represent energy consumption — which depends on wind speed and direction, and may be negative (tailwind). (a) Design an algorithm to find the minimum-energy path between any two vertices. (b) Analyse its complexity. (c) If the graph also contains positive cycles (detours that actually *generate* energy — not physically possible, but a useful modelling tool for regenerative battery systems), how does this change the problem — and can it still be solved?

3. **(Dynamic Programming)** Two DNA sequences of length n and m need to be aligned, but the alignment must respect a "conserved block" — a subsequence that must appear contiguously in both strings. (a) Formulate the problem as a DP and give the recurrence. (b) Analyse the time and space complexity. (c) Propose a space-efficient version that recovers the alignment without storing the full DP table, and discuss the trade-offs.

4. **(NP-Completeness)** You are consulting for a startup that wants to "solve" the problem of assigning employees to desks in an open-plan office, subject to constraints: some employees cannot sit next to each other, some must sit near windows, some require adjacent desks. (a) Formalise this problem — what is the underlying combinatorial structure? (b) Prove that the problem, in its general form, is NP-complete — by reduction from a known NP-complete problem. (c) Propose an approximation algorithm or a parameterised exact algorithm for a realistic special case.

5. **(Approximation Algorithms)** The set cover problem is NP-hard, but the greedy algorithm achieves a ln n approximation. (a) State the greedy algorithm and prove its approximation ratio. (b) Is the analysis tight — can you construct an instance where the greedy algorithm achieves *exactly* H_n times the optimal? (c) Discuss why set cover is hard to approximate better than ln n — what is the role of the PCP theorem in inapproximability?

6. **(Randomized Algorithms)** Consider the problem of finding the *second* smallest element in an unsorted array of n distinct elements. (a) Design a deterministic algorithm that makes n + ⌈log₂ n⌉ − 2 comparisons. (b) Is this optimal? (c) Consider the generalised problem: find the k-th smallest element. Describe the linear expected-time randomised selection algorithm, prove its expected running time, and discuss the conditions under which the worst-case occurs.

7. **(Streaming Graphs)** You are monitoring a social network in real time — edges arrive as a stream, representing new friendships — and you need to maintain, at all times, the size of the largest connected component, using memory that is O(n polylog n) where n is the number of vertices. (a) Design an algorithm. (b) Prove its correctness — or, if exact maintenance is impossible in this memory bound, prove a lower bound and design an approximation. (c) How does the problem change if edges can also be *deleted* (friendships dissolve)?

8. **(Integrative Essay — The Algorithmic Imagination)** Choose one of the following algorithms studied in this course: Dijkstra's shortest-paths algorithm, the Bellman-Ford algorithm, Kruskal's MST algorithm, the Floyd-Warshall algorithm, or the Karger min-cut algorithm. Describe the algorithm precisely, trace its intellectual history (who discovered it, when, and in what context), analyse its correctness and complexity, and reflect on what the algorithm teaches us about the nature of algorithmic thinking. What makes this algorithm "beautiful" — or, if you do not find it beautiful, why not? Your essay will be judged not on whether you praise the algorithm but on the depth and precision of your engagement.

---

## Course Summary and Learning Outcomes

By the end of CS201, students will be able to:
1. Represent graphs in adjacency list and matrix forms and choose the appropriate representation for a given problem
2. Implement and analyse BFS, DFS, topological sort, and strongly connected component decomposition
3. Solve shortest-path problems using Dijkstra, Bellman-Ford, and Johnson's algorithms, recognising the constraints and failure modes of each
4. Construct minimum spanning trees using Prim's and Kruskal's algorithms and articulate the cut and cycle properties
5. Design dynamic programming solutions for problems with optimal substructure: knapsack, LCS, edit distance, matrix chain multiplication, and DP on trees
6. Recognise NP-complete problems, construct polynomial-time reductions, and apply approximation algorithms with provable guarantees
7. Implement randomised algorithms (Las Vegas and Monte Carlo) and analyse their expected running time and error probabilities
8. Apply graph algorithms to streaming, distributed, and learned contexts in the 2040 computing landscape

CS201 is the second pillar of the Computer Science core, alongside CS103 (Data Structures & Algorithms I) and CS107 (Probability & Statistics for CS). It prepares students for CS301 (Machine Learning — where DP and graph algorithms underpin sequence models and graphical models), CS305 (Cryptography — where randomised algorithms and number-theoretic hardness are central), CS401 (AI Systems — where heuristic search, constraint satisfaction, and learned algorithms converge), and the AI OS Design and AI World Modeling programmes (where the algorithmic principles of optimal substructure and approximation drive the design of autonomous systems).
