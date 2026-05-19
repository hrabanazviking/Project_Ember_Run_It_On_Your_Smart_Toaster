# CS106: Linear Algebra & Matrix Computation
## Bachelor of Science in Computer Science — University of Yggdrasil, 2040

**Credits:** 4
**Prerequisites:** CS102 (Discrete Mathematics)
**Co-requisite:** CS105 (Data Structures & Algorithms I)
**Description:** A rigorous introduction to linear algebra from the computational perspective. Vectors, matrices, linear transformations, eigenvalues, singular value decomposition, and their applications to machine learning, computer graphics, and scientific computing. Emphasis on algorithmic thinking — how to compute these operations efficiently on the Yggdrasil-9's heterogeneous hardware — and on geometric intuition. Programming assignments in Python (NumPy, JAX) and Rust (nalgebra, faer).

---

## Lectures

### Lecture 1: Vectors and Spaces — The Geometry of Data

**Course:** CS106 — Linear Algebra & Matrix Computation
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

A vector is simultaneously a geometric arrow (magnitude and direction), an algebraic tuple (ordered list of numbers), and a computational object (the fundamental unit of data in machine learning). This lecture develops all three perspectives, establishing ℝⁿ as the vector space in which virtually all of data science and AI operates. By the end, students should be able to visualize operations in 2D and 3D, reason algebraically in n dimensions, and implement vector operations efficiently in NumPy and Rust.

#### Lecture Notes

The *geometric* view: a vector in ℝ² or ℝ³ is an arrow from the origin to a point. Vector addition is the parallelogram law (or tip-to-tail). Scalar multiplication stretches or shrinks (and possibly reverses) the vector. These two operations — addition and scalar multiplication — define a *vector space*, an abstract algebraic structure whose power lies in its generality. The same axioms that govern arrows in 3D space also govern the space of all polynomials of degree ≤ n, the space of all continuous functions on [0,1], and the 768-dimensional embedding space in which a language model represents the word "Yggdrasil."

The *algebraic* view: a vector in ℝⁿ is an n-tuple (v₁, v₂, ..., vₙ). Addition is component-wise: (u+v)ᵢ = uᵢ + vᵢ. Scalar multiplication: (cv)ᵢ = c·vᵢ. This is the view that NumPy's `ndarray` and Rust's `nalgebra::DVector` implement directly. The component-wise operations are trivially parallelizable — each component can be computed independently — making vector operations ideal for GPU acceleration. A single CUDA kernel launch can add two vectors of length 10⁶ in microseconds, which is why the BLAS (Basic Linear Algebra Subprograms) Level 1 operations (vector-vector) are the foundation of high-performance computing.

The *dot product* (inner product) u·v = Σ uᵢvᵢ is the most important operation on vectors. It measures *alignment*: u·v = ‖u‖ ‖v‖ cos θ, where θ is the angle between u and v. If u·v = 0, the vectors are orthogonal (perpendicular). If u·v > 0, they point in similar directions. If u·v < 0, they point in opposite directions. The dot product is the engine of geometric reasoning: it computes projections (the projection of u onto v is ((u·v)/(v·v)) v), determines orthogonality, and underlies the entire edifice of least-squares regression, PCA, and the Gram-Schmidt process. In neural networks, the dot product is the fundamental operation: a neuron's activation is σ(w·x + b), where w and x are weight and input vectors.

The *norm* ‖v‖ = √(v·v) measures length (the Euclidean norm, ℓ₂). Other norms are useful: the ℓ₁ norm ‖v‖₁ = Σ |vᵢ| induces sparsity (used in Lasso regression); the ℓ_∞ norm ‖v‖_∞ = max |vᵢ| gives the maximum absolute component. The choice of norm fundamentally affects the geometry of the space — the set {v : ‖v‖ ≤ 1} is a diamond for ℓ₁, a circle/sphere for ℓ₂, and a square/cube for ℓ_∞. This geometric intuition is essential for understanding regularization in machine learning: ℓ₂ regularization ("ridge," "weight decay") encourages small weights in all directions; ℓ₁ regularization ("lasso") encourages many weights to become exactly zero, performing feature selection.

We close with *linear combinations* and *span*. A linear combination of vectors v₁, ..., vₖ is any expression c₁v₁ + ... + cₖvₖ. The *span* of a set of vectors is the set of all their linear combinations — the subspace "generated" by those vectors. The concepts of linear dependence (a set is linearly dependent if some vector can be expressed as a linear combination of the others) and linear independence (no vector can be so expressed) are the gateway to basis and dimension — the concepts that structure the rest of the course.

#### Key Concepts
- Vectors: geometric (arrows), algebraic (tuples), computational (arrays)
- Vector addition and scalar multiplication: the vector space axioms
- Dot product: alignment measure, projection, orthogonality
- Norms: ℓ₂ (Euclidean), ℓ₁ (Manhattan), ℓ_∞ (max); unit balls
- Linear combinations and span
- Linear dependence and independence
- NumPy: `np.array`, broadcasting, `np.dot`, `np.linalg.norm`; Rust: `nalgebra::DVector`

#### Required Reading
- Strang, G. *Introduction to Linear Algebra*, 6th ed. (2036), Chapters 1.1–1.3
- Boyd, S. and Vandenberghe, L. *Introduction to Applied Linear Algebra* (2038), Chapters 1–3 — a modern, computation-focused approach
- *NumPy User Guide*, Sections on array basics and `numpy.linalg`

#### Discussion Questions
1. The dot product u·v = ‖u‖ ‖v‖ cos θ is defined algebraically (sum of products) and geometrically (lengths times cosine). Prove these definitions are equivalent in ℝ² using the law of cosines. Does the geometric definition generalize to ℝⁿ?
2. ℓ₁ regularization produces sparse solutions (many zero weights). Why, geometrically, does the ℓ₁ ball (diamond shape) encourage sparsity more than the ℓ₂ ball (circle)? Draw the geometry of the optimization problem.
3. In a 768-dimensional embedding space, what does "orthogonal" mean? Can two word embeddings be orthogonal? If so, what does that imply about their semantic relationship?

#### Practice Problems
- In NumPy: generate two random vectors of size 10⁶. Compute their dot product using (a) `np.dot`, (b) a manual loop (don't — just observe that `np.dot` is 1000× faster because it uses BLAS). Time both.
- Prove the Cauchy-Schwarz inequality: |u·v| ≤ ‖u‖ ‖v‖. When does equality hold? Interpret geometrically.
- Given vectors u = (3, 4) and v = (1, 2) in ℝ², find the projection of u onto v, and the component of u orthogonal to v. Verify that the projection and the orthogonal component sum to u.

---

### Lecture 2: Matrices as Linear Transformations — The Universal Machine of Applied Math

**Course:** CS106 — Linear Algebra & Matrix Computation
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

If vectors are the nouns of linear algebra, matrices are the verbs — they *act* on vectors, transforming them. A matrix A ∈ ℝ^(m×n) represents a linear transformation from ℝⁿ to ℝᵐ: input a vector x, output Ax. This lecture develops matrices from three complementary perspectives: as collections of column vectors, as linear transformations, and as computational objects optimized by BLAS Level 3. We also cover matrix multiplication — the most important operation in scientific computing — in depth.

#### Lecture Notes

A *matrix* A ∈ ℝ^(m×n) is a rectangular array of numbers with m rows and n columns. The entry aᵢⱼ is in row i, column j. We can view A as a collection of n column vectors (each in ℝᵐ) or m row vectors (each in ℝⁿ). The *matrix-vector product* Ax is a linear combination of the columns of A with coefficients from x: Ax = x₁(col₁) + x₂(col₂) + ... + xₙ(colₙ). This column-picture of matrix multiplication is the key to geometric intuition: Ax is the vector you get by taking x₁ steps in the direction of column 1, x₂ steps in column 2, and so on. The columns of A are the images of the standard basis vectors: Aeⱼ = column j of A.

This reveals the deep truth: *every linear transformation from ℝⁿ to ℝᵐ is matrix multiplication by some m×n matrix*. A transformation T is linear if T(u+v) = T(u) + T(v) and T(cv) = cT(v). Given such a T, the matrix A whose j-th column is T(eⱼ) satisfies T(x) = Ax for all x. This equivalence — linear transformations are matrices, and matrices are linear transformations — is the central unifying theorem of linear algebra. It means that to study linear transformations, we study matrices; and to multiply matrices, we compose linear transformations: (AB)x = A(Bx).

*Matrix multiplication* C = AB (where A is m×p, B is p×n) has four complementary views: (1) the *dot-product* view: cᵢⱼ = (row i of A)·(column j of B); (2) the *column* view: column j of C is a linear combination of the columns of A, with coefficients from column j of B; (3) the *row* view: row i of C is a linear combination of the rows of B, with coefficients from row i of A; (4) the *outer-product* view: C = Σₖ (column k of A)(row k of B). Each view provides different insights and suggests different computational optimizations. The dot-product view is the standard textbook definition. The outer-product view reveals that matrix multiplication is a sum of rank-1 matrices — which is the basis for low-rank approximation (Lecture 8, SVD). The column view reveals that C's columns are transformations of B's columns by A.

The computational complexity of naive matrix multiplication is Θ(mnp) — for square matrices, Θ(n³). *Strassen's algorithm* (1969) reduced this to O(n^log₂7) ≈ O(n^2.807) by trading one multiplication for several additions. The current theoretical best is O(n^2.37188) (Alman and Williams, 2024), but the constants are galactic. In 2040, practical matrix multiplication uses *blocked* algorithms that optimize for the cache hierarchy (CS104): divide the matrices into sub-blocks that fit in L1/L2/L3 cache, multiply the blocks using optimized micro-kernels (often hand-tuned in assembly or generated by autotuners like ATLAS or LIBXSMM), and accumulate the results. The Yggdrasil-9's H200 GPUs use Tensor Cores that multiply 16×16 blocks in a single cycle, achieving >1 PFLOPS of dense matrix performance. The gap between theoretical and practical matrix multiplication is a case study in the importance of hardware-conscious algorithm design.

Matrix *transpose* Aᵀ swaps rows and columns: (Aᵀ)ᵢⱼ = Aⱼᵢ. The transpose has profound algebraic significance: (AB)ᵀ = BᵀAᵀ, and AᵀA is always symmetric and positive semidefinite — a fact that underlies the normal equations of least squares and the Gram matrix of machine learning. *Symmetric* matrices (A = Aᵀ) have special properties — real eigenvalues, orthogonal eigenvectors — that make them computationally and theoretically central.

We close with special matrices: the *identity matrix* I (1s on diagonal, 0s elsewhere; IA = AI = A), *diagonal matrices* (non-zero only on diagonal — cheap to multiply, representing independent scaling along axes), *permutation matrices* (exactly one 1 per row and column — representing reordering), and *orthogonal matrices* (QᵀQ = I — representing rotations and reflections; they preserve lengths and angles, making them numerically stable). These special matrices are the building blocks of matrix factorizations: LU = (lower triangular)(upper triangular) for solving linear systems; QR = (orthogonal)(upper triangular) for least squares; SVD = (orthogonal)(diagonal)(orthogonal) for everything.

#### Key Concepts
- Matrix as linear transformation: column picture, standard basis
- Matrix-vector multiplication: linear combination of columns
- Matrix-matrix multiplication: four views (dot, column, row, outer)
- Computational complexity: naive Θ(n³), Strassen O(n^2.807), practical blocked algorithms
- Transpose: (AB)ᵀ = BᵀAᵀ; symmetric matrices
- Special matrices: identity, diagonal, permutation, orthogonal
- BLAS Level 3: matrix-matrix operations, the peak of computational throughput

#### Required Reading
- Strang, *Introduction to Linear Algebra*, Chapters 2.1–2.5
- Golub, G.H. and Van Loan, C.F. *Matrix Computations*, 5th ed. (2037), Chapter 1 (Matrix Multiplication) — the definitive reference
- Alman, J. and Williams, V.V. "A Refined Laser Method and Faster Matrix Multiplication," *STOC 2024* — the current theoretical frontier

#### Discussion Questions
1. Matrix multiplication is associative: (AB)C = A(BC). But the computational cost can vary dramatically depending on the evaluation order. For matrices of sizes 100×500, 500×10, and 10×1000, which parenthesization minimizes operations?
2. An orthogonal matrix Q satisfies QᵀQ = I. Geometrically, it preserves lengths and angles. Why are orthogonal matrices numerically stable — why does computing with them not amplify roundoff errors?
3. Tensor Cores multiply 16×16 blocks in hardware. How should algorithms be restructured to exploit this? Consider a convolution — how would you transform it to use matrix multiplication (im2col)?

#### Practice Problems
- In Python: implement naive matrix multiplication and blocked matrix multiplication (block size 64). Benchmark on 1024×1024 matrices. Compare with `np.dot` and `np.matmul`. Explain the performance ratios.
- Prove that (AB)ᵀ = BᵀAᵀ. Then prove that AᵀA is symmetric and that xᵀ(AᵀA)x = ‖Ax‖² ≥ 0 for all x — hence AᵀA is positive semidefinite.
- Given the linear transformation T: ℝ² → ℝ² that rotates vectors by θ counterclockwise, find its matrix representation. Then find the matrix for reflection across the line y = x.

---

### Lecture 3: Solving Linear Systems — Gaussian Elimination and the LU Factorization

**Course:** CS106 — Linear Algebra & Matrix Computation
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

The most fundamental computational problem in linear algebra: given A ∈ ℝ^(n×n) and b ∈ ℝⁿ, find x ∈ ℝⁿ such that Ax = b. Gaussian elimination — the algorithm every high school student learns — is, when analyzed deeply, a matrix factorization: A = LU, where L is lower triangular (the multipliers) and U is upper triangular (the eliminated matrix). This lecture covers Gaussian elimination, LU factorization, the role of pivoting for numerical stability, and the computational complexity that makes solving linear systems the cornerstone of simulation, optimization, and machine learning.

#### Lecture Notes

*Gaussian elimination* transforms Ax = b into Ux = c (where U is upper triangular) through a sequence of elementary row operations: (1) swap rows (partial pivoting, for numerical stability); (2) add a multiple of one row to another (elimination). Once in upper triangular form, the system is solved by *back substitution*: solve the last equation for xₙ, substitute into the (n-1)-th, and so on. The elimination phase is Θ(n³); back substitution is Θ(n²) — the cubic dominates for large n.

The *LU factorization* formalizes elimination as a matrix decomposition: A = LU, where L is lower triangular (with 1s on the diagonal) and U is upper triangular (the result of elimination). The entries of L are the *multipliers* — the numbers by which rows were multiplied before subtraction during elimination. Once A = LU is computed, solving Ax = b reduces to two triangular solves: (1) solve Ly = b by *forward substitution* (Θ(n²)); (2) solve Ux = y by *back substitution* (Θ(n²)). For multiple right-hand sides (b₁, b₂, ..., bₖ), the expensive factorization is done once (Θ(n³)), and each solve is cheap (Θ(n²)) — a massive win for applications that solve many systems with the same A but different b.

*Partial pivoting* is essential for numerical stability. Consider elimination on a matrix where the pivot (the diagonal entry being used to eliminate below) is very small, say 10⁻¹⁸. Dividing by this tiny pivot amplifies roundoff errors, destroying accuracy. Partial pivoting swaps rows to bring the largest (in absolute value) eligible entry to the pivot position. With partial pivoting, the factorization is PA = LU, where P is a permutation matrix. In practice, partial pivoting is almost always sufficient for stability — *complete pivoting* (swapping both rows and columns) provides stronger guarantees but is rarely needed and costs O(n³) extra. In 2040, the Yggdrasil-9's NPU uses mixed-precision LU (FP16 for the bulk computation, FP32 for critical accumulations) to accelerate training while maintaining stability — a technique that requires deep understanding of where and why pivoting matters.

*Cholesky factorization* is the specialization of LU for *symmetric positive definite* (SPD) matrices: A = LLᵀ where L is lower triangular. It requires half the operations of LU (n³/6 vs. n³/3) and is more stable (no pivoting needed for SPD matrices). Many matrices in machine learning and optimization are SPD: the Gram matrix XᵀX, the Hessian of convex objectives, the covariance matrix in Gaussian processes. Recognizing SPD structure and reaching for Cholesky rather than general LU is a hallmark of numerical maturity.

We close with a discussion of *sparse linear systems*. When A is sparse (most entries are zero), storing the full LU factors would destroy sparsity — L and U are typically much denser than A, a phenomenon called *fill-in*. *Sparse direct solvers* (like UMFPACK, SuperLU, and the 2040 successor `sparse-ygg`) use graph-theoretic reorderings (minimum degree, nested dissection) to minimize fill-in, enabling the solution of sparse systems with millions of unknowns. *Iterative methods* (conjugate gradient, GMRES), covered in CS302 (Numerical Methods), take a different approach: they never form L and U at all, instead repeatedly multiplying A by vectors — exploiting sparsity to achieve O(nnz) per iteration. The choice between direct and iterative solvers is a central theme in scientific computing.

#### Key Concepts
- Gaussian elimination: forward elimination + back substitution, Θ(n³)
- LU factorization: A = LU, forward + back substitution for multiple RHS
- Partial pivoting: PA = LU, numerical stability
- Cholesky factorization: A = LLᵀ for SPD matrices, 2× faster
- Fill-in in sparse matrices; reordering strategies
- Direct vs. iterative solvers
- NumPy: `np.linalg.solve`, `np.linalg.lu`; Rust: `nalgebra::linalg::LU`, `faer::linalg::solvers::FullPivLu`

#### Required Reading
- Strang, *Introduction to Linear Algebra*, Chapters 2.6–2.7
- Golub and Van Loan, *Matrix Computations*, Chapters 3 (Linear Systems) and 4 (LU Factorization)
- Davis, T.A. *Direct Methods for Sparse Linear Systems* (2006, updated 2037), Chapters 1–4

#### Discussion Questions
1. Partial pivoting chooses the largest eligible pivot. But scaling the rows of A changes what "largest" means. Should we scale before pivoting? What is the "equilibration" problem, and why is it hard?
2. Cholesky factorization is 2× faster than LU but requires SPD. How can you check whether a matrix is SPD? (Hint: attempt Cholesky — if a pivot becomes ≤ 0, the matrix is not SPD. This is the cheapest test.)
3. In mixed-precision LU (FP16/FP32), where does numerical error accumulate? How would you detect that an FP16 factor is too inaccurate and needs refinement?

#### Practice Problems
- In Python: implement Gaussian elimination without pivoting. Solve a random 100×100 system and compare with `np.linalg.solve`. Then implement partial pivoting and demonstrate its necessity on a matrix with a small pivot.
- Compute the LU factorization of a 1000×1000 matrix. Time the factorization; then solve for 100 different right-hand sides using the LU factors. Compare total time with calling `np.linalg.solve` 100 times (which re-factors each time).
- For the SPD matrix A = [4, 2; 2, 3], compute its Cholesky factorization by hand. Verify LLᵀ = A.

---

### Lecture 4: Vector Spaces and Subspaces — The Four Fundamental Subspaces

**Course:** CS106 — Linear Algebra & Matrix Computation
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

Every matrix A ∈ ℝ^(m×n) defines four fundamental subspaces: the *column space* C(A) (all linear combinations of columns), the *nullspace* N(A) (all vectors x with Ax = 0), the *row space* C(Aᵀ) (all linear combinations of rows), and the *left nullspace* N(Aᵀ) (all vectors y with yᵀA = 0). These four subspaces form an orthogonal decomposition of ℝⁿ (domain) and ℝᵐ (codomain), and their dimensions — the *rank* and *nullity* — are the first invariants of a matrix. This lecture develops the subspace framework that unifies solutions to Ax = b, least squares, and dimensionality reduction.

#### Lecture Notes

The *column space* C(A) is the set of all vectors that can be expressed as Ax for some x — that is, the set of all possible outputs of the linear transformation A. The equation Ax = b has a solution if and only if b ∈ C(A). The *rank* r = dim(C(A)) measures the "effective dimension" of A's output — the number of linearly independent columns. An m×n matrix has *full column rank* if r = n (columns are independent, N(A) = {0}); *full row rank* if r = m; *full rank* if r = min(m,n).

The *nullspace* N(A) is the set of all x such that Ax = 0. If N(A) contains non-zero vectors, the linear transformation A is not injective — different inputs can produce the same output (since A(x + n) = Ax + An = Ax for n ∈ N(A)). The dimension of the nullspace is n - r (the *rank-nullity theorem*). In data science, the nullspace represents *redundant features* — directions in the input space that have no effect on the output.

The *row space* C(Aᵀ) has dimension r. It is orthogonal to the nullspace: every vector in the row space is orthogonal to every vector in the nullspace. This is the *Fundamental Theorem of Linear Algebra, Part I*: ℝⁿ = C(Aᵀ) ⊕ N(A) — the domain decomposes into the row space and the nullspace, and they are orthogonal complements. Similarly, ℝᵐ = C(A) ⊕ N(Aᵀ) — the codomain decomposes into the column space and the left nullspace. These orthogonal decompositions are not just elegant; they are the theoretical foundation for least squares (Lecture 5), PCA (Lecture 8), and the entire edifice of statistical linear models.

*Basis and dimension* formalize the notion of "size" for subspaces. A *basis* is a set of linearly independent vectors that span the subspace. Every basis has the same number of vectors — the *dimension*. Finding a basis for C(A) is as simple as identifying the pivot columns during Gaussian elimination. Finding a basis for N(A) requires solving Ax = 0 — the free variables (those not in pivot columns) parameterize the nullspace. In NumPy, `np.linalg.matrix_rank` computes rank via SVD (the most reliable method, as it handles numerical near-zero singular values gracefully); `scipy.linalg.null_space` computes an orthonormal basis for the nullspace.

The *rank* of a matrix is simultaneously: the number of pivot columns; the dimension of the column space; the dimension of the row space; the number of non-zero singular values; and (for square matrices) n minus the dimension of the nullspace. This multiplicity of characterizations is typical of linear algebra — the same number emerges from different perspectives, each providing different computational access. *Rank-deficient* matrices (rank < min(m,n)) are "almost" singular — small changes can make them full rank, and small errors can dramatically change the solution to Ax = b. *Regularization* (Tikhonov, ridge regression) adds λI to AᵀA to make it full rank, stabilizing the solution — a technique at the heart of machine learning.

We close with *orthogonal bases* and the *Gram-Schmidt process*. Given any basis {v₁, ..., vₖ} of a subspace, Gram-Schmidt produces an *orthogonal* basis {q₁, ..., qₖ} (q_i · q_j = 0 for i ≠ j) and, with normalization, an *orthonormal* basis (‖q_i‖ = 1). Orthonormal bases are computationally ideal: to express a vector in the basis, just compute dot products (coordinates c_i = v·q_i); to project onto the subspace, sum the projections onto each basis vector. Gram-Schmidt is the conceptual foundation of QR factorization (Lecture 5), but in practice, *modified Gram-Schmidt* or *Householder reflections* are preferred for numerical stability.

#### Key Concepts
- Four fundamental subspaces: C(A), N(A), C(Aᵀ), N(Aᵀ); orthogonal decomposition
- Rank: number of pivots, dimension of column/row space, number of non-zero singular values
- Rank-nullity theorem: dim C(Aᵀ) + dim N(A) = n
- Basis and dimension; pivot columns and free variables
- Rank deficiency and regularization
- Gram-Schmidt orthogonalization; orthonormal bases

#### Required Reading
- Strang, *Introduction to Linear Algebra*, Chapters 3.1–3.5
- Strang, G. "The Fundamental Theorem of Linear Algebra," *American Mathematical Monthly*, 1993 — the classic exposition
- Trefethen, L.N. and Bau, D. *Numerical Linear Algebra* (1997, 2nd ed. 2037), Chapters 1–2

#### Discussion Questions
1. The Fundamental Theorem says ℝⁿ = C(Aᵀ) ⊕ N(A). Given a vector x, how would you decompose it into its row-space and nullspace components? What does this decomposition tell you about the solution to Ax = b?
2. Gram-Schmidt is conceptually simple but numerically unstable (in classical form). What goes wrong when vectors are nearly parallel? How does modified Gram-Schmidt mitigate this?
3. In a 2040 neural network, the weight matrices of intermediate layers are often rank-deficient (many singular values near zero). What does this imply about the effective dimension of the representation? How could you exploit rank deficiency for model compression?

#### Practice Problems
- For the matrix A = [1,2,3; 4,5,6; 7,8,9], compute its rank. Find bases for the four fundamental subspaces. Verify the rank-nullity theorem and the orthogonal decomposition.
- In Python: generate a 100×50 random matrix (entries ~ N(0,1)). Compute its rank using `np.linalg.matrix_rank`. Add noise (ε ~ N(0, 10⁻¹⁰)) and recompute. How does the rank change? What tolerance should `matrix_rank` use?
- Apply the Gram-Schmidt process to the vectors {(1,1,1), (1,0,1), (0,1,1)} to obtain an orthonormal basis. Verify orthonormality by computing the dot products between basis vectors.

---

### Lecture 5: Least Squares and Projections — Finding the Best Fit When Perfection Is Impossible

**Course:** CS106 — Linear Algebra & Matrix Computation
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

What if Ax = b has no solution? This is the typical case: we have more equations than unknowns (overdetermined system), and measurement noise makes exact satisfaction impossible. The *least squares* solution minimizes ‖Ax - b‖² — the squared Euclidean distance between the model's predictions and the observed data. This lecture develops least squares from first principles: the geometry of projection, the normal equations, the QR factorization, and the connection to maximum likelihood estimation that makes least squares the foundation of regression, Kalman filtering, and the linear layers of neural networks.

#### Lecture Notes

When Ax = b has no solution, the best we can do is to choose x̂ that makes the *residual* r = b - Ax̂ as small as possible. Minimizing ‖r‖² is the *least squares problem*. Geometrically: Ax̂ is the *projection* of b onto the column space C(A). The residual r is orthogonal to C(A) — any component of b in C(A) would be captured by Ax̂; the residual is what remains, orthogonal to every column of A. This orthogonality condition, Aᵀr = 0, gives the *normal equations*: AᵀAx̂ = Aᵀb. If A has full column rank, AᵀA is invertible (positive definite), and x̂ = (AᵀA)⁻¹Aᵀb. The matrix (AᵀA)⁻¹Aᵀ is the *pseudoinverse* (Moore-Penrose) A⁺.

The normal equations are conceptually clean but computationally hazardous. Forming AᵀA squares the condition number: κ(AᵀA) = κ(A)², where κ is the ratio of largest to smallest singular value. If A is ill-conditioned (nearly rank-deficient), AᵀA is disastrously ill-conditioned, and solving the normal equations directly amplifies roundoff errors. The *QR factorization* provides a numerically superior approach: factor A = QR (Q orthogonal, R upper triangular), then x̂ = R⁻¹Qᵀb. Since Q is orthogonal, it preserves lengths and doesn't amplify errors; since R is triangular, the solve is stable. The QR approach is the workhorse of production least-squares solvers (NumPy's `np.linalg.lstsq` uses SVD or QR depending on the matrix properties).

*Weighted least squares* generalizes the problem: minimize (Ax - b)ᵀW(Ax - b) where W is a diagonal (or general positive definite) weight matrix. This is equivalent to ordinary least squares on the transformed system W^(1/2)Ax = W^(1/2)b. Weighted least squares is essential when observations have different reliabilities (heteroscedasticity) — for example, in the Yggdrasil OS's sensor fusion module, GPS measurements (high variance) receive lower weight than LIDAR measurements (low variance).

The *statistical interpretation* of least squares is profound: if the residual r is normally distributed with mean 0 and covariance σ²I, then the least squares estimator x̂ is the *maximum likelihood estimator* (MLE) — the value of x that maximizes the probability of observing the data b. Moreover, x̂ is the *best linear unbiased estimator* (BLUE) by the Gauss-Markov theorem: among all linear unbiased estimators, x̂ has minimum variance. This dual optimality — geometric (minimum distance) and statistical (maximum likelihood, minimum variance) — explains least squares' central role across science and engineering.

In 2040, least squares extends beyond classical regression. The *linear layers* of neural networks (fully connected layers: y = Wx + b) are trained by stochastic gradient descent, but the linear algebra of the forward and backward passes is least squares at scale: the forward pass computes projections; the backward pass computes transposed projections. *Kalman filters*, used in the Yggdrasil OS's state estimation (OS103), recursively apply weighted least squares to fuse predictions with measurements. The *normalizing flows* in generative AI use compositions of linear transformations to model complex probability distributions. Least squares — a 200-year-old technique (Gauss, 1809; Legendre, 1805) — remains indispensable because its mathematical structure is the structure of inference from noisy data.

#### Key Concepts
- Least squares: minimize ‖Ax - b‖²; geometric projection onto C(A)
- Normal equations: AᵀAx̂ = Aᵀb; pseudoinverse: A⁺ = (AᵀA)⁻¹Aᵀ
- QR factorization for stable solving: A = QR, x̂ = R⁻¹Qᵀb
- Weighted least squares; heteroscedasticity
- Statistical interpretation: MLE, BLUE, Gauss-Markov theorem
- Condition number κ(A) and its effect on solution accuracy; κ(AᵀA) = κ(A)²
- Applications: regression, Kalman filtering, neural network linear layers

#### Required Reading
- Strang, *Introduction to Linear Algebra*, Chapter 4.1–4.3
- Golub and Van Loan, *Matrix Computations*, Chapter 5 (Orthogonalization and Least Squares)
- Gauss, C.F. *Theoria Motus Corporum Coelestium* (1809) — the original least squares (for orbit determination!)

#### Discussion Questions
1. The normal equations solve least squares but can be numerically unstable. Yet they are widely used in closed-form solutions for small systems. At what matrix size or condition number would you switch from normal equations to QR?
2. The pseudoinverse A⁺ exists for any matrix (not just full column rank). How does the SVD-based pseudoinverse work? What is the minimum-norm solution when A is rank-deficient?
3. In a Kalman filter, the state covariance evolves according to Pₖ = APₖ₋₁Aᵀ + Q. What is the significance of the AₖPₖ₋₁Aₖᵀ term? Why does it involve A and its transpose?

#### Practice Problems
- In Python: generate a noisy linear dataset y = Ax_true + ε where ε ~ N(0, 0.1). Solve for x̂ using (a) normal equations, (b) `np.linalg.lstsq`. Compare the solutions and the condition numbers.
- Compute the QR factorization of a 100×20 matrix using (a) Gram-Schmidt, (b) `np.linalg.qr` (Householder). Compare the orthogonality of Q (‖QᵀQ - I‖) for both methods.
- Fit a quadratic model y = ax² + bx + c to data using least squares. Set up the design matrix A (columns: x², x, 1) and solve. Plot the data and the fitted curve.

---

### Lecture 6: Determinants — Volume, Invertibility, and the Geometry of Scale

**Course:** CS106 — Linear Algebra & Matrix Computation
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

The determinant det(A) is a single number that answers the most fundamental question about a square matrix: does A⁻¹ exist? det(A) ≠ 0 if and only if A is invertible. But the determinant is also a geometric quantity: |det(A)| is the volume of the parallelepiped spanned by A's columns (or rows). This lecture develops determinants from their axiomatic definition through computational strategies (LU factorization: det(A) = det(L)det(U) = product of U's diagonal entries, since det(L) = 1 for unit triangular) to their role in spectral theory (the characteristic polynomial det(A - λI) = 0 for eigenvalues).

#### Lecture Notes

The determinant is defined by three axioms: (1) det(I) = 1; (2) swapping two rows flips the sign of the determinant; (3) the determinant is linear in each row separately. From these axioms, all properties follow: det(A) = 0 if rows are linearly dependent; det(AB) = det(A)det(B); det(A⁻¹) = 1/det(A); det(Aᵀ) = det(A). The explicit formula — det(A) = Σ_σ sign(σ) a_{1,σ(1)} a_{2,σ(2)} ... a_{n,σ(n)} — sums over all n! permutations and is computationally infeasible for n > 20. This is why we never compute determinants by the permutation formula; instead, we compute LU factorization (or, for symmetric matrices, Cholesky) and take the product of diagonal entries. The determinant of a triangular matrix is the product of its diagonal entries.

The geometric interpretation makes the determinant intuitive. In ℝ², det([a b; c d]) = ad - bc is ± the area of the parallelogram spanned by (a,c) and (b,d). In ℝ³, the determinant is ± the volume of the parallelepiped. A linear transformation with matrix A scales volumes by |det(A)|. If det(A) = 0, the transformation collapses at least one dimension — the columns are linearly dependent, the transformation is not invertible, and the image is a lower-dimensional subspace. This geometric collapse is exactly what we mean by "singular."

The determinant is the bridge to eigenvalues. The *characteristic polynomial* p(λ) = det(A - λI) is a degree-n polynomial whose roots are the eigenvalues of A. Computing p(λ) explicitly (expanding the determinant) is numerically unstable for n > 5; in practice, eigenvalues are computed by iterative methods (QR algorithm, divide-and-conquer) that never form the characteristic polynomial. But the determinant's connection to eigenvalues — det(A) = λ₁λ₂...λₙ (the product of all eigenvalues) — is essential theoretical knowledge. The *trace* tr(A) = Σ a_ii = λ₁ + λ₂ + ... + λₙ (sum of eigenvalues) is similarly elegant and useful.

*Cramer's rule* — xⱼ = det(Aⱼ)/det(A), where Aⱼ is A with column j replaced by b — is a beautiful theoretical formula for solving Ax = b. It shows that the solution is a rational function of the data. But it is computationally horrific: computing n+1 determinants of n×n matrices costs O(n·n!), making it exponentially worse than Gaussian elimination. Cramer's rule is a theoretical tool, not a computational one — a distinction students must learn to make.

In 2040, the determinant finds application in *change of variables* for probability distributions. When a generative model applies a transformation y = f(x) to a random variable x, the density of y involves |det(J)| where J is the Jacobian matrix of f. *Normalizing flows* — a powerful class of generative models — are built by composing invertible transformations whose Jacobian determinants are easy to compute. The *RealNVP* and *Glow* architectures, still used in 2040 for density estimation in the Yggdrasil AI's world model (WM303), are exercises in structured determinant computation.

#### Key Concepts
- Determinant axioms and properties: det(I)=1, row swap sign, row linearity
- Geometric interpretation: signed volume; det=0 → collapse of dimension
- Computation via LU: det(A) = Π u_ii (for LU without pivoting)
- Characteristic polynomial: p(λ) = det(A - λI); eigenvalues as roots
- Trace: tr(A) = Σ a_ii = Σ λ_i
- Cramer's rule: beautiful theory, disastrous computation
- Jacobian determinant in normalizing flows

#### Required Reading
- Strang, *Introduction to Linear Algebra*, Chapter 5
- Axler, S. *Linear Algebra Done Right*, 4th ed. (2038), Chapter 10 (Trace and Determinant) — an elegant, coordinate-free treatment
- Dinh, L., Sohl-Dickstein, J., and Bengio, S. "Density Estimation Using Real NVP," *ICLR 2017* — for the modern application of Jacobian determinants

#### Discussion Questions
1. The determinant is multiplicative: det(AB) = det(A)det(B). The trace is additive: tr(A+B) = tr(A) + tr(B). Why does the determinant multiply while the trace adds? What does this tell us about the algebraic nature of each?
2. Computing the determinant from the permutation formula costs O(n!). Computing it from LU costs O(n³). Why is there such a vast gap? What property does LU exploit that the permutation formula doesn't?
3. In normalizing flows, the Jacobian must be easy to compute for the model to be trainable. What structural constraints on the transformation matrix (triangular? orthogonal? low-rank update?) make the determinant cheap?

#### Practice Problems
- Compute the determinant of A = [2,1,3; 4,5,0; 1,6,2] by (a) the permutation formula (tedious!), (b) LU factorization using Python. Compare the effort.
- Prove that det(AB) = det(A)det(B) using the axioms (for 2×2 matrices, then argue by induction for general n — or, more realistically, sketch the proof).
- For the matrix A = [1,ε; ε,1] with ε = 10⁻⁸, compute the determinant directly and via the characteristic polynomial. How does numerical precision affect the eigenvalues computed as roots of the characteristic polynomial?

---

### Lecture 7: Eigenvalues and Eigenvectors — The Natural Axes of Linear Transformations

**Course:** CS106 — Linear Algebra & Matrix Computation
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

An *eigenvector* of a square matrix A is a non-zero vector v that A merely stretches: Av = λv. The scalar λ is the *eigenvalue*. Eigenvectors are the "natural axes" of the transformation A — directions that remain unchanged in orientation (only scaled). This lecture develops the eigenvalue problem, the characteristic equation, diagonalization, and the spectral theorem for symmetric matrices, which provides the theoretical foundation for PCA, spectral clustering, and the analysis of dynamical systems.

#### Lecture Notes

The eigenvalue equation Av = λv rearranges to (A - λI)v = 0. For a non-zero solution v to exist, the matrix A - λI must be singular — its determinant must be zero. The *characteristic equation* det(A - λI) = 0 is a polynomial of degree n whose roots are the eigenvalues. An n×n matrix has exactly n eigenvalues (counting multiplicities) over the complex numbers, but may have fewer real eigenvalues.

Once eigenvalues are found, eigenvectors are computed by solving (A - λI)v = 0 — they are the nullspace of A - λI. For each distinct eigenvalue λ, the set of eigenvectors (plus the zero vector) forms the *eigenspace*. The *geometric multiplicity* of λ is the dimension of its eigenspace; the *algebraic multiplicity* is its multiplicity as a root of the characteristic polynomial. Geometric ≤ algebraic always; when they're equal for all eigenvalues, the matrix is *diagonalizable*.

*Diagonalization* is the eigen-decomposition: A = PDP⁻¹, where D is diagonal (eigenvalues on the diagonal) and P has eigenvectors as columns. This factorization reveals A's action: P⁻¹ changes basis to the eigenvector basis, D scales along each eigenvector axis, and P changes back. Powers of A become trivial: Aᵏ = PDᵏP⁻¹. This is the basis for analyzing Markov chains (the steady-state distribution is the eigenvector for λ=1), for understanding the stability of dynamical systems (eigenvalues inside the unit circle → stable), and for the PageRank algorithm (the PageRank vector is the dominant eigenvector of the Google matrix).

Computing eigenvalues in practice is a triumph of numerical linear algebra. The *QR algorithm* (Francis, 1961; Kublanovskaya, 1961) iterates A₀ = A; Aₖ = QₖRₖ (QR factorization); Aₖ₊₁ = RₖQₖ. The Aₖ converge to an upper triangular (or quasi-triangular real Schur) form whose diagonal entries are the eigenvalues. With shifts (subtracting an estimate of an eigenvalue before the QR step to accelerate convergence), the QR algorithm converges cubically and is the engine behind every production eigenvalue solver (`np.linalg.eig`, LAPACK's `dgeev`). For large sparse matrices, *Krylov subspace methods* (Arnoldi, Lanczos) compute a few extremal eigenvalues without forming the full matrix — essential for the billion-dimensional sparse matrices of web graphs and social networks.

The *spectral theorem* for symmetric matrices is the crown jewel of eigenvalue theory: every real symmetric matrix A has *real* eigenvalues and *orthogonal* eigenvectors. Thus, A = QΛQᵀ, where Q is orthogonal (QᵀQ = I) and Λ is diagonal. This is the *spectral decomposition*. It means symmetric matrices are completely characterized by their eigenvalues (the "spectrum") and eigenvectors (the "principal axes"). The spectral theorem is the mathematical foundation of Principal Component Analysis (PCA), spectral clustering, and the graph Fourier transform — all essential tools in the data scientist's and AI engineer's toolkit.

#### Key Concepts
- Eigenvalue equation: Av = λv; characteristic polynomial
- Algebraic vs. geometric multiplicity; defectiveness
- Diagonalization: A = PDP⁻¹, powers Aᵏ = PDᵏP⁻¹
- QR algorithm for eigenvalue computation (iterative, cubic convergence)
- Spectral theorem for symmetric matrices: A = QΛQᵀ, real eigenvalues, orthogonal eigenvectors
- Applications: PageRank, dynamical systems, PCA, spectral clustering

#### Required Reading
- Strang, *Introduction to Linear Algebra*, Chapter 6
- Trefethen and Bau, *Numerical Linear Algebra*, Chapters 24–28 (Eigenvalue Problems)
- Parlett, B.N. *The Symmetric Eigenvalue Problem* (1980, reprinted 2040), Chapters 1–2

#### Discussion Questions
1. A defective matrix (geometric multiplicity < algebraic multiplicity for some eigenvalue) cannot be diagonalized. What is the "next best" factorization? (The Jordan canonical form — but it is numerically unstable. In practice, every matrix is numerically diagonalizable.)
2. The QR algorithm converges to the eigenvalues without explicitly forming the characteristic polynomial. Why is avoiding the characteristic polynomial essential for numerical stability?
3. The spectral theorem requires symmetry. What happens to the eigenvalues and eigenvectors of a non-symmetric matrix? Can they be complex? What does a complex eigenvalue mean geometrically? (Hint: rotation.)

#### Practice Problems
- Compute the eigenvalues and eigenvectors of A = [3,1; 1,3] by hand. Diagonalize A and compute A¹⁰ using the diagonalization.
- In Python: generate a random 100×100 symmetric matrix. Compute its eigenvalues using `np.linalg.eigh` (optimized for symmetric). Verify that A = QΛQᵀ by checking ‖A - QΛQᵀ‖.
- Implement the power method (repeatedly multiply by A and normalize) to find the dominant eigenvalue and eigenvector of a matrix. Test on a random matrix and compare with `np.linalg.eig`.

---

### Lecture 8: The Singular Value Decomposition — The Swiss Army Knife of Data

**Course:** CS106 — Linear Algebra & Matrix Computation
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

The Singular Value Decomposition (SVD) is the most important matrix factorization — more general than eigendecomposition, more stable than LU, and the mathematical engine behind PCA, latent semantic analysis, collaborative filtering, image compression, and the low-rank structure that makes modern AI tractable. Any matrix A ∈ ℝ^(m×n) can be factored as A = UΣVᵀ, where U and V are orthogonal and Σ is diagonal (the singular values). This lecture develops the SVD, its geometry (rotation → scaling → rotation), and its myriad applications.

#### Lecture Notes

The SVD theorem states: for any m×n matrix A of rank r, there exist orthogonal matrices U ∈ ℝ^(m×m) and V ∈ ℝ^(n×n) and a diagonal matrix Σ ∈ ℝ^(m×n) with non-negative entries σ₁ ≥ σ₂ ≥ ... ≥ σᵣ > 0 = σ_{r+1} = ... = σ_min(m,n) such that A = UΣVᵀ. The σᵢ are the *singular values*; the columns of U are the *left singular vectors*; the columns of V are the *right singular vectors*. The SVD always exists (unlike eigendecomposition, which requires diagonalizability), is always computable (unlike Jordan form, which is numerically unstable), and reveals everything worth knowing about A.

Geometrically, the SVD decomposes the linear transformation A into three simple steps: (1) Vᵀ: rotate/reflect the input to align the principal axes with the coordinate axes; (2) Σ: scale along those axes by the singular values, possibly embedding into a higher-dimensional space (if m > n) or projecting onto a lower-dimensional one (if m < n); (3) U: rotate/reflect the result to the output coordinate system. Every linear transformation is a composition of an isometry, a scaling, and another isometry. This geometric clarity is unmatched by any other factorization.

The SVD reveals the *four fundamental subspaces* directly: the first r columns of U are an orthonormal basis for C(A); the remaining m-r columns of U are a basis for N(Aᵀ); the first r columns of V are a basis for C(Aᵀ); the remaining n-r columns of V are a basis for N(A). The singular values measure the "strength" of each dimension: σ_i is the factor by which A stretches vectors in the direction of v_i. The *condition number* κ(A) = σ₁/σᵣ (or σ₁/σ_min for full-rank matrices) quantifies sensitivity to perturbations.

The *low-rank approximation* property is the SVD's superpower: the best rank-k approximation to A (minimizing ‖A - Aₖ‖ in both spectral and Frobenius norms) is Aₖ = UₖΣₖVₖᵀ, where we keep only the first k singular values and vectors. This is the *Eckart-Young-Mirsky theorem*. In practice, many matrices are well-approximated by low rank — the singular values decay rapidly. A 1000×1000 matrix of image pixel values might have an effective rank of 50 (the remaining 950 singular values are near zero, contributing only noise). This is why JPEG compression works (it's essentially SVD on 8×8 blocks, with small singular values quantized to zero). This is why PCA reduces dimensionality (keep the first k principal components). This is why recommender systems work (the user-item rating matrix is approximately low-rank — people's preferences are explained by a small number of latent factors).

Computing the SVD for large matrices is challenging — the full SVD is O(mn²) (assuming m ≥ n). In 2040, *randomized SVD* (Halko, Martinsson, Tropp, 2011) has become standard for large-scale applications: multiply A by a random matrix to sample its column space, compute the SVD of the much smaller projected matrix, and recover the approximate SVD. Randomized SVD can compute a rank-100 approximation to a billion-entry matrix in seconds — fast enough for interactive data exploration and real-time AI model updates. The Yggdrasil OS's memory subsystem (OS203) uses randomized SVD to compress episodic memory embeddings, reducing storage by 90% while preserving similarity search accuracy.

#### Key Concepts
- SVD: A = UΣVᵀ, universal existence, orthogonal U and V, diagonal Σ
- Geometric interpretation: rotation → scaling → rotation
- Four fundamental subspaces from SVD
- Low-rank approximation: Eckart-Young-Mirsky theorem, Aₖ = UₖΣₖVₖᵀ
- Applications: PCA, image compression, recommender systems, latent semantic analysis
- Randomized SVD for large-scale computation
- Condition number: κ(A) = σ₁/σᵣ

#### Required Reading
- Strang, *Introduction to Linear Algebra*, Chapter 7
- Trefethen and Bau, *Numerical Linear Algebra*, Chapters 4–5 and 31
- Halko, N., Martinsson, P.G., and Tropp, J.A. "Finding Structure with Randomness: Probabilistic Algorithms for Constructing Approximate Matrix Decompositions," *SIAM Review*, 2011 — the randomized SVD paper

#### Discussion Questions
1. The SVD exists for *any* matrix. The eigendecomposition exists only for diagonalizable matrices. What makes the SVD more universal? (Hint: AᵀA is always symmetric positive semidefinite, hence always diagonalizable.)
2. The Eckart-Young-Mirsky theorem says the truncated SVD is the optimal low-rank approximation in the spectral norm. If you want the optimal low-rank approximation in the Frobenius norm, is the truncated SVD still optimal? (Yes — the theorem holds for all unitarily invariant norms.)
3. Randomized SVD is approximate — it introduces error in exchange for speed. In the OS203 memory compression application, what is the tradeoff between compression ratio (how many singular values to keep) and retrieval accuracy (how well the compressed embeddings preserve similarity rankings)?

#### Practice Problems
- Compute the SVD of A = [1,2; 3,4; 5,6] by hand (find eigenvalues of AᵀA, then eigenvectors, then U). Verify with `np.linalg.svd`.
- In Python: load an image (as a grayscale matrix). Compute its SVD and reconstruct it using k = 5, 10, 20, 50 singular values. Display the reconstructions. How many singular values are needed for visual fidelity?
- Implement randomized SVD for rank-k approximation. Compare its speed and accuracy with the full SVD on a 10,000×10,000 random matrix with rapidly decaying singular values.

---

### Lecture 9: Principal Component Analysis — Finding Structure in High-Dimensional Data

**Course:** CS106 — Linear Algebra & Matrix Computation
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

Principal Component Analysis (PCA) is the workhorse of dimensionality reduction. Given n data points in ℝᵈ, PCA finds the k ≪ d orthogonal directions (principal components) that capture the most variance in the data. Mathematically, PCA is the eigendecomposition of the covariance matrix (or equivalently, the SVD of the centered data matrix). This lecture develops PCA from its geometric intuition (find the line that best fits the data in the least-squares sense) through its mathematical formulation (maximize variance, minimize reconstruction error) to its modern applications in visualization, preprocessing, and the interpretation of neural network representations.

#### Lecture Notes

Given centered data points x₁, ..., xₙ ∈ ℝᵈ (mean subtracted), the *first principal component* is the direction w₁ (‖w₁‖ = 1) that maximizes the variance of the projected data: max_{‖w‖=1} Σ (w·xᵢ)². This is equivalent to finding the eigenvector of the covariance matrix C = (1/n) Σ xᵢxᵢᵀ corresponding to the largest eigenvalue. The second principal component maximizes variance among directions orthogonal to the first — the eigenvector for the second-largest eigenvalue. And so on. The k principal components are the eigenvectors for the k largest eigenvalues of C.

Equivalently, if we form the data matrix X ∈ ℝ^(n×d) (rows are data points), then the principal components are the right singular vectors of X (or the eigenvectors of XᵀX). The *explained variance ratio* — λᵢ / Σ λⱼ — tells us what fraction of the total variance is captured by each component. In practice, we often find that the first few components capture the vast majority of variance: "the intrinsic dimensionality of the data is low." This is the empirical fact that makes PCA useful.

PCA is a *linear* dimensionality reduction technique. It can only find linear structure — lines, planes, hyperplanes. For data with nonlinear structure (swiss rolls, toruses, complex manifolds), *kernel PCA*, *t-SNE*, *UMAP*, and *autoencoders* are more appropriate. But PCA remains the first tool to reach for because it is interpretable (the principal components are directions in the original feature space), computationally efficient (SVD on the data matrix), and often surprisingly effective. In the AI OS curriculum, PCA is used in WM201 for understanding the structure of world-model embeddings and in OS205 for compressing neural representations before storage in episodic memory.

The *scree plot* — a bar chart of eigenvalues sorted by magnitude — is the diagnostic tool for choosing k. We look for the *elbow*: the point where eigenvalues stop decreasing rapidly and level off. This is the practical dimension of the data. But subjective judgment is required; there is no universally optimal k. In 2040, *probabilistic PCA* (Tipping and Bishop, 1999) and *Bayesian PCA* provide automatic relevance determination, learning the effective dimension from data with principled uncertainty estimates — a preview of the advanced techniques studied in CS401 and WM303.

PCA has important connections to the SVD. Computing the covariance matrix C and its eigendecomposition is O(d²n + d³). Computing the SVD of X directly is O(dn min(d,n)). When n ≫ d (many data points, few features), the covariance approach is fine. When d ≫ n (genomics, where we have thousands of genes but only dozens of patients), the "dual" approach — SVD of X yields the same principal components — is much faster. Knowing which computational path to take is an essential practical skill.

We close with a cautionary tale. PCA maximizes variance, not discriminability. Two classes that are perfectly separable by a subtle feature might be collapsed by PCA if that feature has low variance compared to irrelevant high-variance dimensions (like overall brightness in images). *Linear discriminant analysis* (LDA) addresses this by maximizing class separability rather than variance. The lesson: know what your objective function rewards, and verify that it aligns with your actual goal.

#### Key Concepts
- PCA: maximize variance of projected data → eigendecomposition of covariance
- Principal components = eigenvectors of C = right singular vectors of X
- Explained variance ratio; scree plot and elbow method
- PCA as optimal linear compression (minimizes reconstruction error)
- Computational strategies: covariance eigendecomposition vs. SVD of data matrix
- Probabilistic PCA and Bayesian PCA
- Limitations: linear only, maximizes variance not discriminability

#### Required Reading
- Jolliffe, I.T. *Principal Component Analysis*, 3rd ed. (2036), Chapters 1–3
- Tipping, M.E. and Bishop, C.M. "Probabilistic Principal Component Analysis," *JRSS-B*, 1999
- Shlens, J. "A Tutorial on Principal Component Analysis," 2014 (updated 2038) — the most-read PCA tutorial on the internet

#### Discussion Questions
1. PCA finds the directions of maximum variance. Why is variance a good proxy for "interesting structure"? When is it a bad proxy — when would the direction of maximum variance be the least informative axis?
2. The dual formulation (SVD of X vs. eigendecomposition of XᵀX) is faster when d ≫ n. Why? What is the computational complexity of each approach?
3. In neural network interpretability, researchers apply PCA to the activations of hidden layers. What does the spectrum of singular values of the activation matrix tell us about the network's representations? What would a rapidly decaying spectrum suggest?

#### Practice Problems
- In Python: load the classic Iris dataset. Center the data, compute PCA, and project onto the first two principal components. Plot the projected data, colored by species. What fraction of variance is explained?
- Implement PCA from scratch using `np.linalg.eigh` on the covariance matrix. Compare your results with `sklearn.decomposition.PCA`. Verify that the principal components are orthonormal.
- Generate synthetic data on a "swiss roll" manifold. Apply PCA and observe that it fails to unroll the manifold. Then apply `sklearn.manifold.Isomap` or UMAP. Write a brief explanation of why PCA fails for nonlinear manifolds.

---

### Lecture 10: Computational Linear Algebra — BLAS, LAPACK, and the Art of Fast Matrix Ops

**Course:** CS106 — Linear Algebra & Matrix Computation
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

The mathematical elegance of linear algebra is useless without efficient computation. This lecture bridges theory and practice: how are linear algebra operations implemented on real hardware? We cover the BLAS (Basic Linear Algebra Subprograms) hierarchy, the LAPACK library that implements factorizations and decompositions, and the hardware-specific optimizations (SIMD, GPU, Tensor Cores) that achieve near-peak performance. Students will profile matrix operations on the Yggdrasil-9, understanding where the cycles go and how to write code that the hardware loves.

#### Lecture Notes

*BLAS* (Basic Linear Algebra Subprograms) is the computational bedrock of scientific computing. It defines three levels: *Level 1* (vector-vector: dot product, axpy, nrm2 — O(n) operations, O(n) data, memory-bound); *Level 2* (matrix-vector: gemv, trsv — O(n²) operations, O(n²) data, balanced); *Level 3* (matrix-matrix: gemm, trsm — O(n³) operations, O(n²) data, compute-bound). The compute intensity (operations per byte) increases with the level: Level 1 is memory-bound (limited by how fast data can be fetched), Level 3 is compute-bound (limited by FLOPS). This is why blocked algorithms that express work in terms of Level-3 BLAS are essential for high performance — they amortize memory access over many floating-point operations.

*LAPACK* (Linear Algebra PACKage) builds on BLAS to provide factorizations (LU, Cholesky, QR, SVD, eigendecomposition) and solvers (linear systems, least squares, eigenvalue problems). LAPACK routines are carefully designed to maximize Level-3 BLAS usage through block algorithms. For example, blocked LU factorization operates on panels (blocks of columns), using Level-3 BLAS for the trailing matrix update — the same algorithmic pattern we explored in Lecture 3. LAPACK is written in Fortran 90 (with C interfaces), and its routines have been tuned over 40 years to be numerically stable and performant. In 2040, the *FlexiBLAS* library provides a pluggable BLAS/LAPACK backend: applications link against FlexiBLAS, and at runtime, the system selects the optimal implementation (OpenBLAS, MKL, BLIS, or the Yggdrasil-9's custom `ygg-blas` that leverages the cluster's heterogeneous architecture).

*GEMM* (GEneral Matrix Multiply) is the most important function in scientific computing — the "hello world" of high-performance computing. The operation C = αAB + βC (where A, B, C are matrices, α, β are scalars) consumes a large fraction of cycles in machine learning, simulation, and data analysis. Optimizing GEMM for a specific hardware platform involves: *cache blocking* (divide matrices into tiles that fit in each cache level), *register blocking* (micro-kernel: an unrolled loop operating on small blocks in registers), *SIMD vectorization* (using AVX-512, NEON, or RISC-V V extension to process multiple elements per instruction), *prefetching* (anticipating data needs to hide memory latency), and *instruction scheduling* (interleaving arithmetic and memory instructions to keep all execution units busy). A hand-tuned GEMM can achieve >95% of theoretical peak FLOPS — a testament to decades of cumulative optimization.

In 2040, the frontier of linear algebra computation is *mixed precision* and *approximate computing*. Training neural networks in FP16 (half precision) reduces memory bandwidth and increases throughput, with FP32 accumulation preserving accuracy. The *bfloat16* format (same exponent range as FP32, truncated mantissa) simplifies conversion. *INT8* and *INT4* quantization (common for inference) require careful linear algebra to minimize accuracy loss — re-scaling activations, using the SVD to identify sensitive directions. The Yggdrasil-9's H200 GPUs include *Transformer Engine* support that dynamically selects precision per layer. Understanding the linear algebra beneath these technologies is what separates the user of AI tools from the builder.

We close with a hands-on profiling exercise. Students instrument matrix multiplication in Python (NumPy vs. naive loops), Rust (nalgebra vs. faer), and CUDA (cublas vs. custom kernel), measuring FLOPS and memory bandwidth. The results — NumPy using OpenBLAS achieving 200 GFLOPS on a single core, the custom kernel struggling to hit 10 GFLOPS — teach a lesson that no lecture can convey: the algorithm that's theoretically optimal may be practically terrible if it ignores the hardware.

#### Key Concepts
- BLAS levels: 1 (memory-bound), 2 (balanced), 3 (compute-bound)
- LAPACK: factorizations and solvers on top of BLAS
- GEMM optimization: cache blocking, register blocking, SIMD, prefetching
- Mixed precision: FP32, FP16, bfloat16, INT8, INT4
- FlexiBLAS and runtime backend selection
- Profiling: measuring FLOPS, memory bandwidth, identifying bottlenecks

#### Required Reading
- *BLAS Technical Forum Standard* (2002, updated 2030) — the specification
- *LAPACK Users' Guide*, 4th ed. (2038) — the reference manual
- Goto, K. and van de Geijn, R. "Anatomy of High-Performance Matrix Multiplication," *ACM TOMS*, 2008 — the definitive paper on how to optimize GEMM
- *NVIDIA CUDA C++ Best Practices Guide*, Section on Tensor Cores (online, continuously updated)

#### Discussion Questions
1. Level-1 BLAS is memory-bound: the operation count equals the data movement (O(n) operations, O(n) data). Level-3 BLAS is compute-bound: O(n³) operations for O(n²) data. What is the cross-over point — at what matrix size does Level-3 BLAS become faster than repeated Level-1 operations for the same computation?
2. Mixed-precision training uses FP16 for forward/backward passes and FP32 for weight updates. Why is FP32 needed for the weight update specifically? What would happen if weights were accumulated in FP16?
3. Profiling shows a naive matrix multiplication achieving 5% of peak FLOPS. List, in order of importance, the optimizations that would close the gap. At what point do diminishing returns set in?

#### Practice Problems
- In Python: implement matrix multiplication four ways: (a) triple nested loop (i-j-k), (b) using `np.dot`, (c) using `np.einsum`, (d) using `@` operator. Time them on 2048×2048 matrices and explain the performance differences.
- In Rust: use `nalgebra` and `faer` to multiply two 4096×4096 matrices. Benchmark and compare. Profile with `perf` to identify where cycles are spent.
- In CUDA (on the Yggdrasil-9): write a simple matrix multiplication kernel. Compare its performance with `cublasSgemm`. Iteratively add optimizations (coalesced memory access, shared memory tiling) and measure the improvement.

---

### Lecture 11: Linear Algebra for Machine Learning — From Linear Models to Deep Networks

**Course:** CS106 — Linear Algebra & Matrix Computation
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

Linear algebra is the native language of machine learning. A linear regression is least squares. A neural network layer is an affine transformation followed by a nonlinearity. The backpropagation algorithm is the chain rule applied to matrix derivatives. This lecture surveys the linear algebra that powers modern ML: linear models, the matrix calculus of backpropagation, batch normalization, attention mechanisms, and the role of spectral analysis in understanding generalization. By the end, students will see their ML coursework (WM201, AI301) through a linear-algebraic lens.

#### Lecture Notes

*Linear regression* is the simplest ML model: y ≈ Xw + b, where X ∈ ℝ^(n×d) is the design matrix and w ∈ ℝᵈ is the weight vector. The least-squares solution ŵ = (XᵀX)⁻¹Xᵀy is the MLE under Gaussian noise. *Ridge regression* adds ℓ₂ regularization: ŵ = (XᵀX + λI)⁻¹Xᵀy — making the problem always well-posed. *Lasso* adds ℓ₁ regularization, which has no closed form but can be solved by coordinate descent or proximal gradient methods. These linear models are the foundation; deep learning extends them through composition.

A *fully-connected neural network layer* computes z = Wx + b, a = σ(z), where W ∈ ℝ^(out×in) is the weight matrix and σ is a nonlinear activation. Stacking L such layers: a^(L) = σ_L(W_L σ_{L-1}(... σ₁(W₁x + b₁) ... ) + b_L). The forward pass is a sequence of matrix-vector multiplications. The *backward pass* (backpropagation) computes gradients with respect to weights using the chain rule: ∂L/∂W_ℓ = δ_ℓ (a_{ℓ-1})ᵀ, where δ_ℓ = (W_{ℓ+1}ᵀ δ_{ℓ+1}) ⊙ σ'_ℓ(z_ℓ) is the "error" propagating backward. Backpropagation is linear algebra — matrix multiplications and transpositions — applied in reverse.

*Batch normalization* (Ioffe and Szegedy, 2015), still standard in 2040 architectures, normalizes the activations of each layer to zero mean and unit variance across the batch: x̂ = (x - μ)/√(σ² + ε). This is linear algebra with statistics: computing means and variances over the batch dimension, then applying an affine transformation with learned parameters γ, β. The forward pass is differentiable, so backpropagation flows through the normalization — requiring careful derivation of gradients through the mean and variance computations.

The *attention mechanism* (Vaswani et al., 2017), the core of transformer architectures, is a tour de force of linear algebra: Attention(Q, K, V) = softmax(QKᵀ/√dₖ)V. Queries Q, Keys K, and Values V are matrices (each row is a token's embedding). QKᵀ computes dot-product similarities between all pairs of tokens — an n×n matrix for a sequence of length n. The softmax normalizes each row to a probability distribution. Multiplying by V produces a weighted sum of value vectors. This is O(n²d) — quadratic in sequence length — which is why efficient attention (linear attention, flash attention) is the central research challenge of 2040 transformer scaling. The Yggdrasil OS's language module uses flash attention on the GPU to process context windows of up to 10⁶ tokens.

*Spectral analysis for generalization* connects the linear algebra of weight matrices to the learning dynamics of neural networks. The *Hessian* of the loss — the matrix of second derivatives — has an eigenvalue spectrum that reveals the local geometry of the loss landscape. Sharp minima (large Hessian eigenvalues) generalize poorly; flat minima generalize well (Hochreiter and Schmidhuber, 1997; Keskar et al., 2017). Regularization techniques (weight decay, dropout, batch normalization) can be understood as manipulating the Hessian spectrum. In 2040, *spectral regularization* — explicitly penalizing large eigenvalues of the weight matrices — is a standard technique in the Yggdrasil AI's training pipeline.

The lecture closes with the *linear-algebraic interpretation of representational similarity*. Given two neural networks (or two layers) processing the same inputs, how similar are their representations? *Canonical Correlation Analysis* (CCA) and *Centered Kernel Alignment* (CKA) use SVD to compare the subspaces spanned by their activations — techniques developed in the 2010s–2030s and now standard in the interpretability toolkit of AI OS engineers (OS403).

#### Key Concepts
- Linear regression: least squares, ridge, lasso
- Forward pass: sequence of affine transformations + nonlinearities
- Backward pass (backpropagation): transposed matrices, gradient propagation via chain rule
- Batch normalization: mean/variance computation, differentiable affine transformation
- Attention: softmax(QKᵀ/√dₖ)V, quadratic complexity, flash attention
- Hessian spectrum, sharp vs. flat minima, spectral regularization
- Representational similarity: CCA, CKA, SVD-based subspace comparison

#### Required Reading
- Goodfellow, I., Bengio, Y., and Courville, A. *Deep Learning* (2016), Chapters 2 (Linear Algebra), 6 (Deep Feedforward Networks)
- Vaswani, A. et al. "Attention Is All You Need," *NeurIPS 2017* — the transformer paper
- Dao, T. et al. "FlashAttention: Fast and Memory-Efficient Exact Attention," *NeurIPS 2022* — and "FlashAttention-3," 2038 — the efficient attention lineage

#### Discussion Questions
1. Backpropagation is the chain rule: ∂L/∂W = ∂L/∂a · ∂a/∂z · ∂z/∂W. Each factor is a matrix (or higher-order tensor). Why does the backward pass involve *transposes* of the weight matrices? What is the geometric intuition?
2. The attention matrix QKᵀ is n×n. For n=10⁶ (a 2040 context window), storing this matrix explicitly requires 4 TB in FP32. How does flash attention avoid materializing this matrix?
3. The Hessian eigenvalue spectrum of a trained network often shows a few large eigenvalues (directions of high curvature) and many near-zero eigenvalues (flat directions). What does this imply about the effective number of parameters? Could you prune the network by removing flat directions?

#### Practice Problems
- Implement a simple neural network (2 layers, ReLU activation) in Python using only NumPy — no PyTorch/TensorFlow. Implement the forward pass and backward pass (backpropagation) manually. Train on a synthetic dataset and verify gradient correctness using finite differences.
- Implement scaled dot-product attention from scratch: compute Q, K, V from input embeddings (as learned linear projections), compute Attention(Q,K,V), and verify the output shapes and that row sums ≈ 1 (after softmax).
- Compute the Hessian-vector product for a small network (using automatic differentiation or finite differences). Use the power method to find the largest Hessian eigenvalue. Does your trained network have sharp or flat minima?

---

### Lecture 12: Linear Algebra in the AI OS — The Mathematical Spine of Yggdrasil

**Course:** CS106 — Linear Algebra & Matrix Computation
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

The Yggdrasil AI OS is, at its mathematical core, a linear algebra machine. The world model (WM201) represents states as vectors, transitions as matrices, and predictions as matrix-vector products. The memory system (OS203) uses SVD for compression and dot products for similarity search. The governance layer (OS401) solves linear systems and eigenvalue problems for resource allocation. This capstone lecture maps the linear algebraic structure of the entire AI OS curriculum, showing how the concepts of CS106 — vectors, matrices, factorizations, eigenvalues — are the mathematical spine that runs through every realm of Yggdrasil.

#### Lecture Notes

The *World Model* (WM201–WM407) is a linear algebra engine at scale. The state of the world is a vector s ∈ ℝᵈ, where d can be millions (representing positions, velocities, semantic features, uncertainty estimates). The transition function s_{t+1} = f(s_t, a_t) is locally approximated as s_{t+1} ≈ As_t + Ba_t (a linearization, used in the Kalman filter state estimator) or implemented as a neural network where each layer is an affine transformation. The prediction horizon — rolling out the model for T steps — is s_{t+T} ≈ Aᵀs_t + (A^{T-1}B a_t + ... + B a_{t+T-1}) — matrix powers appear. Eigenvalues of A determine stability: if |λ| > 1, perturbations grow exponentially (the model is unstable for long horizons). This is why WM303 (World Model Inference) devotes substantial effort to spectral analysis of the learned transition matrices.

The *Memory System* (OS203, OS205) uses linear algebra for storage and retrieval. Memories are embedded as vectors v ∈ ℝᵈ using a neural encoder. Similarity search — "find memories similar to this cue" — is nearest-neighbor search in ℝᵈ, implemented via dot products (or cosine similarity) with all stored memories. To scale to billions of memories, the system uses (1) *dimensionality reduction* via randomized SVD (Lecture 8), compressing embeddings from d=4096 to k=256 while preserving similarity rankings; (2) *quantization* via product quantization (encoding each vector as a sequence of cluster indices, enabling fast approximate search); (3) *graph-based indices* (HNSW) that organize memories into a proximity graph, navigating via dot products. The MuninnGate (OS203) serves billions of similarity queries per second using these techniques on the Yggdrasil-9's GPUs.

The *Governance Layer* (OS401) solves optimization problems that reduce to linear algebra. Resource allocation — deciding which compute resources to assign to which OS realms — is a constrained optimization: minimize cost subject to resource limits. With linear cost and linear constraints, this is a *linear program* solved by the simplex method or interior-point methods — both of which, at their core, solve linear systems. The governance layer maintains running estimates of each realm's resource utilization, modeling it as a *Kalman filter*: predict resource usage (linear transformation), observe actual usage, update (linear least squares). The *Þing* — the governance consensus protocol — requires solving eigenvalue problems on the trust graph (PageRank-like algorithms to determine voting weights). Linear algebra is not incidental to the AI OS; it is the operating system's mathematical substrate.

The *Verification Layer* (OS103) uses matrix factorizations to prove properties of OS components. A component's behavior is modeled as a linear dynamical system; its safety properties ("the component never enters state X") are verified by computing reachable sets — ellipsoids in state space described by Lyapunov equations AᵀPA - P = -Q (for discrete time). Solving Lyapunov equations requires matrix factorizations (Schur decomposition, Bartels-Stewart algorithm). The verification of the Yggdrasil kernel's scheduler was completed in 2039 using a combination of Lyapunov analysis and SMT solving — fundamentally, linear algebra plus logic.

The *Personality Layer* (OS403, "Weave of the Norns") uses linear algebra to compose and blend AI personality modules. Each personality module defines a set of basis vectors in "behavior space"; the composite personality is a linear combination of these basis vectors, with mixing weights determined by context. The stochastic composition — sampling from a distribution over personality weights — involves the SVD of the covariance matrix of behaviors, ensuring that sampled personalities are coherent. This is PCA on the space of possible behaviors, a direct application of the concepts from Lectures 8 and 9.

We close the course with a reflection. Linear algebra was developed in the 19th century (Cayley, Sylvester, Grassmann) to solve systems of linear equations. In the 20th century, it became the language of quantum mechanics (Heisenberg's matrix mechanics, 1925) and the tool of numerical computation (von Neumann, Turing, Wilkinson). In the 21st century, it has become the foundation of AI — from perceptrons to transformers, from Kalman filters to diffusion models. And in the Yggdrasil AI OS — the university's grand project to build a memory-bearing machine — linear algebra is the mathematical spine that connects perception to action, memory to governance, verification to personality. CS106 is not a prerequisite for AI OS design; it is the mathematics of AI OS design.

#### Key Concepts
- World model as linear(ized) dynamical system; eigenvalues and stability
- Memory as vector embeddings; SVD compression, dot-product similarity, HNSW
- Governance as constrained optimization; linear programming, Kalman filtering, PageRank
- Verification as Lyapunov equations; Schur decomposition
- Personality as linear combination in behavior space; PCA on behaviors
- The mathematical unity of the AI OS across realms

#### Required Reading
- All previous lectures in this course
- *Yggdrasil AI OS Technical Architecture*, UoY Internal Document TR-2040-01, Sections on Linear Algebraic Foundations
- Boyd, S. and Vandenberghe, L. *Convex Optimization* (2004, 4th printing 2038), Chapters 1, 5 (Duality), and 7 (Interior-Point Methods)

#### Discussion Questions
1. The AI OS uses linear approximations (Kalman filters, linearizations) for systems that are fundamentally nonlinear (neural networks, complex dynamics). When is linear approximation adequate? What are the failure modes?
2. The governance layer's resource allocation problem is, in general, NP-hard (integer constraints). What linear relaxations make it tractable? What is lost in the relaxation?
3. This lecture argues that linear algebra is the "mathematical spine" of the AI OS. Is there any major AI OS component that does *not* reduce to linear algebra at its computational core? If so, what mathematics governs those components?

#### Practice Problems
- Model a simple dynamical system (pendulum, with small-angle approximation) as s_{t+1} = As_t + Bu_t. Compute the eigenvalues of A. Is the system stable? For what time horizon does the linear approximation hold?
- Implement a simple vector-based memory: store 10,000 random 128-dimensional vectors. For a query vector, find the top-5 nearest neighbors by dot product (exhaustive search). Then implement approximate search using random projections (randomized SVD) to reduce to 32 dimensions, then exhaustive search. Compare speed and accuracy.
- Solve a toy resource allocation problem: 3 realms, 2 resource types, minimize cost using `scipy.optimize.linprog`. Interpret the dual variables as "shadow prices" — the marginal cost of relaxing each resource constraint.

---

## Final Examination Preparation

The CS106 final examination consists of a **three-hour written paper** (65%) and a **computational project** (35%).

### Written Examination Format

Answer **four (4) of eight (8)** questions. Each question integrates theory and computation.

**Sample Questions:**

1. **Fundamental Subspaces and Least Squares.** For a given matrix A, find bases for the four fundamental subspaces. Formulate and solve the least squares problem for an overdetermined system. Explain why the normal equations are numerically inferior to QR and demonstrate with a condition number analysis.

2. **Eigenvalues and PCA.** Compute the eigenvalues and eigenvectors of a covariance matrix. Perform PCA on a dataset, determine the number of significant principal components from the scree plot, and interpret the principal directions. Discuss the connection to SVD.

3. **SVD and Low-Rank Approximation.** Compute the truncated SVD of a matrix to rank k. Quantify the approximation error in the Frobenius norm. Apply to an image compression task and analyze the tradeoff between compression ratio and visual quality.

4. **Matrix Factorizations.** Compare LU, Cholesky, QR, and SVD factorizations: their existence conditions, computational complexity, numerical stability, and appropriate use cases. For a given problem (solving SPD system, least squares, computing rank), select the correct factorization and justify.

5. **Computational Linear Algebra.** Analyze the cache behavior of blocked matrix multiplication. Given cache sizes and matrix dimensions, determine optimal block sizes. Explain how the BLAS hierarchy (Levels 1–3) relates to the roofline model of performance.

6. **Linear Algebra in ML.** Derive the gradient of the loss with respect to weights for a two-layer neural network. Express the forward and backward passes in matrix notation. Discuss the role of the Hessian in understanding generalization.

7. **Eigenvalue Computation.** Describe the QR algorithm for eigenvalue computation. Explain why it converges and the role of shifts. Contrast with the power method for large sparse matrices.

8. **AI OS Applications.** Choose an AI OS component (world model, memory, governance, verification, or personality). Describe its linear-algebraic structure in detail: what matrices appear, what factorizations are used, what eigenvalue problems arise. Analyze the computational bottlenecks and propose optimizations.

### Computational Project (35%)

A two-week project applying linear algebra to a real dataset from the Yggdrasil OS's telemetry. Options include: (a) PCA-based anomaly detection in OS performance metrics, (b) low-rank approximation of memory embeddings with accuracy-speed tradeoff analysis, (c) spectral clustering of OS components by communication patterns. Deliverables: code (Python or Rust), 5-page report with mathematical analysis and benchmarks on the Yggdrasil-9 cluster.

---

**Course Code:** CS106
**Last Updated:** 2040-08-15
**Department:** Computer Science, University of Yggdrasil
**Instructor of Record:** Prof. Anya Volkov, Ph.D. (Stanford)
**Contact:** a.volkov@uoy.edu.aks
