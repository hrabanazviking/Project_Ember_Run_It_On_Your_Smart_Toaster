# CS302: Compiler Design & Code Generation
## Bachelor of Science in Computer Science — University of Yggdrasil, 2040

**Credits:** 4  
**Description:** Lexing, parsing, IR, optimization, LLVM, JIT, AOT

---

## Lectures

ᛉ **Lecture 1: The Craft of Compilation — From Source to Machine and Beyond**

**Course:** CS302 — Compiler Design & Code Generation  
**Degree:** Bachelor of Science in Computer Science, 2040

---

### Overview

A compiler is a translator — a smith who takes raw ore (source code) and forges it into a blade (machine code) fit for battle (execution). Like the dwarf-smiths of Svartálfaheimr who crafted Gungnir for Odin, the compiler must understand both the material it works with and the purpose its product will serve.

This course traces the full journey of a compiler: from the raw characters of source text through the structure of syntax, the meaning of types, the transformation of intermediate representations, and finally the emission of machine code that runs on real hardware. Along the way, we will study the great algorithms that make this translation possible — algorithms that have remained relevant for sixty years and continue to evolve in the age of multi-target compilation, just-in-time execution, and AI-guided optimization.

### The Compilation Pipeline

A compiler is organized as a pipeline of phases, each transforming its input into a more refined form:

```
Source Code
    │
    ▼
┌──────────┐     ┌──────────┐     ┌──────────────┐
│  Lexical  │────▶│  Syntax  │────▶│   Semantic    │
│ Analysis  │     │ Analysis │     │   Analysis    │
│ (Scanner) │     │ (Parser) │     │ (Type Checker)│
└──────────┘     └──────────┘     └──────────────┘
      │                │                  │
   Tokens          Parse Tree      Annotated Tree
                                         │
                                         ▼
                                 ┌──────────────┐
                                 │ Intermediate │
                                 │ Representation│
                                 │  Generation   │
                                 └──────────────┘
                                         │
                                         ▼
                                 ┌──────────────┐
                                 │ Optimization  │
                                 │   (multiple   │
                                 │    passes)    │
                                 └──────────────┘
                                         │
                                         ▼
                                 ┌──────────────┐
                                 │    Code       │
                                 │  Generation   │
                                 └──────────────┘
                                         │
                                         ▼
                                    Machine Code
```

**Front End**: Language-dependent phases (lexical analysis, syntax analysis, semantic analysis). Converts source text to an intermediate representation.

**Middle End**: Language- and machine-independent optimization. Transforms IR into more efficient equivalent IR.

**Back End**: Machine-dependent code generation. Selects instructions, allocates registers, and emits assembly or machine code.

This three-part structure is crucial. It is what allows a single optimizer to serve many languages (C, C++, Rust, Swift all compile to LLVM IR) and many targets (x86, ARM, RISC-V, WASM all share the same optimization pipeline).

### Historical Arc

- **1954**: FORTRAN compiler for IBM 704. First optimizing compiler. Led by John Backus, it produced code competitive with hand-written assembly.
- **1960s**: Theory of formal languages develops. Chomsky hierarchy (1956) provides the mathematical foundation for parsing.
- **1970s**: LR parsing (Knuth, 1965), LALR parsing (DeRemer, 1971), and the yacc/bison toolchain. Unix pipeline philosophy (Thompson, Ritchie) influences compiler architecture.
- **1980s**: SSA form (Rosen, Wegman, Zadeck, 1988) revolutionizes optimization. GCC emerges as the dominant open-source compiler.
- **1990s**: Java introduces JIT compilation to the mainstream (HotSpot JVM, 1999). Just-In-Time compilation becomes practical for managed languages.
- **2000s**: LLVM (Lattner, 2000-2004) demonstrates that a clean, retargetable IR can serve as the backbone for a compiler infrastructure supporting many languages and targets.
- **2010s-2040s**: Compiler infrastructure evolves into an ecosystem. Profile-guided optimization, auto-vectorization, polyhedral models, and ML-guided optimization become standard. Verified compilers (CompCert) prove correctness end-to-end.

### The 2040 Context

At UoY, our compiler lab uses LLVM 28 as the primary infrastructure. Students implement a full front end for a teaching language (NornScript), generate LLVM IR, and leverage LLVM's optimization passes before targeting x86-64, RISC-V, and WASM. The final project requires implementing at least one custom optimization pass and evaluating its impact on real benchmarks.

By 2040, compilers are no longer passive translators. They are:
- **Adaptive**: ML-guided optimization profiles the code at runtime and adjusts inlining, vectorization, and register allocation accordingly.
- **Verified**: Tools like CompCert and CakeML prove that the compiler preserves the semantics of the source program.
- **Multi-target**: A single IR compiles to CPUs, GPUs, TPUs, and WASM without source changes.
- **Collaborative**: The IDE and the compiler work together — the compiler provides diagnostics, suggestions, and refactoring assistance in real time.

### Key Terminology

- **Token**: The smallest meaningful unit recognized by the lexer (identifier, keyword, literal, operator).
- **Parse tree**: A tree representation of the syntactic structure of the source program according to the grammar.
- **AST (Abstract Syntax Tree)**: A simplified parse tree that omits syntactic sugar (parentheses, semicolons) and retains essential structure.
- **IR (Intermediate Representation)**: A machine-independent representation that serves as the interface between the front end and back end.
- **Basic block**: A maximal sequence of instructions with one entry point and one exit point.
- **Control flow graph (CFG)**: A graph of basic blocks with edges representing possible execution paths.
- **SSA (Static Single Assignment)**: An IR form where each variable is assigned exactly once, making dataflow analysis simpler and more powerful.

### Required Reading

- Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D. (2006). *Compilers: Principles, Techniques, and Tools* (2nd ed.). Pearson. Chapters 1-2.
- Lattner, C. & Adve, V. (2004). "LLVM: A Compilation Framework for Lifelong Program Analysis & Transformation." *CGO*.
- Cooper, K. D. & Torczon, L. (2022). *Engineering a Compiler* (3rd ed.). Morgan Kaufmann. Chapter 1.

### Discussion Questions

1. If a compiler is a translator, what is "lost in translation"? Can a compiled program ever be more correct than its source?
2. LLVM's three-phase architecture (front-middle-back) enables language and target independence. What are the costs of this generality? Are there cases where a single-pass compiler outperforms a multi-stage compiler?
3. The FORTRAN I compiler (1954) produced code competitive with hand-written assembly. If you were designing a compiler in 2040, what would "competitive with hand-written code" mean for modern architectures?

### Practice Problems

1. **Pipeline trace**: Given the C expression `x = a + b * c`, trace each compiler phase from source text through tokens, parse tree, AST, IR, and assembly (x86-64).
2. **Phase identification**: For each task, identify the compiler phase: (a) detecting that a variable is used before being defined, (b) converting `if` statements to conditional branches, (c) replacing `2 * x` with `x << 1`, (d) detecting that `/` is a division operator.
3. **Design decision**: You are building a compiler for a new language that runs on both embedded ARM microcontrollers and cloud x86 servers. How does the three-phase architecture help? What optimizations differ between the two targets?

---

ᛉ **Lecture 2: Lexical Analysis — Where Characters Become Tokens**

**Course:** CS302 — Compiler Design & Code Generation  
**Degree:** Bachelor of Science in Computer Science, 2040

---

### Overview

Lexical analysis (scanning) is the compiler's first encounter with the source text. It transforms a stream of characters into a stream of tokens — the smallest meaningful units of the language. The scanner strips whitespace and comments, groups characters into identifiers, keywords, literals, and operators, and passes the token stream to the parser.

This lecture covers the mathematical foundations of lexical analysis (regular expressions and finite automata), the algorithms for constructing efficient scanners (NFA → DFA → minimized DFA), and the practical concerns of building a lexer by hand or using tools like flex and re2c.

### Regular Expressions

Regular expressions define the patterns that the scanner recognizes. Each token class is specified as a regular expression:

```
Identifier:  [a-zA-Z_][a-zA-Z0-9_]*
Integer:     [0-9]+
Float:       [0-9]+\.[0-9]+([eE][+-]?[0-9]+)?
Keyword:     if | else | while | for | return | ...
Operator:    + | - | * | / | = | == | != | < | > | <= | >= | && | || | ...
String:      "([^"\\]|\\.)*"
Comment:     //.*$ | /\*([^*]|\*+[^*/])*\*+/
Whitespace:  [ \t\r\n]+
```

Regular expressions are built from three operations:
1. **Union** (R1 | R2): Matches either R1 or R2.
2. **Concatenation** (R1 R2): Matches R1 followed by R2.
3. **Kleene star** (R*): Matches zero or more repetitions of R.

These three operations, plus ε (empty string) and ∅ (empty language), form the foundation of pattern matching in the scanner.

### Finite Automata

**Deterministic Finite Automaton (DFA)**: A 5-tuple (Q, Σ, δ, q₀, F) where Q is a finite set of states, Σ is the input alphabet, δ: Q × Σ → Q is the transition function, q₀ is the start state, and F ⊆ Q is the set of accepting states. Each input character causes exactly one transition.

**Nondeterministic Finite Automaton (NFA)**: δ maps each (state, symbol) pair to a *set* of states. ε-transitions allow movement between states without consuming input. An NFA accepts a string if *some* path from q₀ to a state in F consumes the entire string.

**Key theorems**:
- For every NFA, there exists an equivalent DFA (subset construction).
- For every regular expression, there exists an NFA that recognizes the same language (Thompson's construction).
- Every regular language can be expressed as a regular expression (Kleene's theorem).
- A DFA with n states can be minimized to a unique canonical form with at most n states.

### Thompson's Construction

Given a regular expression R, Thompson's construction builds an NFA with at most 2|R| states (where |R| is the number of symbols and operators in R). The construction rules are:

1. **ε**: NFA with two states connected by an ε-transition.
2. **a**: NFA with two states connected by a transition on symbol a.
3. **R1 | R2**: Create new start and accepting states. ε-transition from new start to starts of R1 and R2. ε-transitions from accepting states of R1 and R2 to new accepting state.
4. **R1 R2**: Concatenation: accepting state of R1 becomes start state of R2 (via ε-transition).
5. **R***: Create new start and accepting states. ε-transition from new start to new accepting and to start of R. ε-transition from accepting state of R to start of R and to new accepting state.

### NFA to DFA: Subset Construction

The subset construction converts an NFA with n states to a DFA with at most 2ⁿ states. For each DFA state, which is a set of NFA states:

1. Compute ε-closure of the current state set.
2. For each input symbol, compute the set of NFA states reachable from the current set.
3. The new state set is the ε-closure of the reachable states.
4. Mark sets containing NFA accepting states as DFA accepting states.

**Minimization**: After construction, minimize the DFA using Hopcroft's algorithm (O(n log n) for n states). The minimized DFA is unique up to state renaming.

### Practical Lexer Construction

**The Maximal Munch Rule**: When the scanner reads characters, it keeps consuming as long as the current prefix matches some pattern. When no extension matches, it backs up one character and emits the longest match. This ensures `==` is tokenized as one token (equality), not two (`=` assignment, `=` assignment).

**Priority Rules**: When two patterns match the same longest string, the scanner uses the *first* pattern in the specification. This means keyword patterns should appear before the identifier pattern.

**Lexical Ambiguities**:
- `ifelse` → identifier (no keyword matches), not `if` + `else`
- `2e3` → float (2.0 × 10³), not `2` + identifier `e3`
- `a+++b` → `a` `++` `+` `b`, not `a` `+` `++` `b` (maximal munch for `+++` fails; longest valid token is `++`)

### Hand-Written vs. Generated Lexers

**Generated (flex, re2c)**:
- Pros: Fast to develop, mathematically correct, handles complex patterns easily.
- Cons: Slower than hand-written (table-driven dispatch), harder to debug, generated code is unreadable.

**Hand-written**:
- Pros: Full control, faster execution, easier to add context-sensitive rules (e.g., string interpolation).
- Cons: More error-prone, more code to maintain, harder to verify correctness.

**Modern approach (2040)**: Most production compilers use hand-written lexers. GCC, Clang, V8, and Go all use hand-written scanners. The reason is speed — a table-driven DFA has 1-2 orders of magnitude more branch mispredictions than a hand-written lexer that can exploit the structure of the language. The generated lexer approach is used in teaching and prototyping, and in compiler-compilers like ANTLR.

### Required Reading

- Aho et al. (2006). *Compilers*, Chapter 3 (Lexical Analysis).
- Appel, A. (2004). *Modern Compiler Implementation in ML*, Chapter 2.
- Lesk, M. E. (1975). "Lex — A Lexical Analyzer Generator." *Unix Programmer's Manual*.

### Discussion Questions

1. Why do most production compilers use hand-written lexers despite the availability of tools like flex? Under what circumstances would a generated lexer be preferable?
2. A language allows nested comments (`/* /* inner */ outer */`). Can a DFA-based scanner handle nested comments? How about an NFA? What approach would you use?
3. Regular expressions cannot match balanced parentheses (this is a context-free language). Yet most scanners use regexes to describe tokens. Why is this not a problem?

### Practice Problems

1. **NFA construction**: Build the NFA for the regular expression `(a|b)*abb` using Thompson's construction. Show all ε-transitions.
2. **Subset construction**: Convert your NFA to a DFA using subset construction. Show the transition table.
3. **Tokenization**: Given the input `if(x<=y+3)`, and the token classes [if, identifier, lparen, le, identifier, plus, integer, rparen], trace the scanner's token-by-token output. What happens if the scanner sees `x<y` and the patterns include both `<` and `<=`?

---

ᛉ **Lecture 3: Context-Free Grammars & Top-Down Parsing — Building Structure from Tokens**

**Course:** CS302 — Compiler Design & Code Generation  
**Degree:** Bachelor of Science in Computer Science, 2040

---

### Overview

The scanner gives us tokens; the parser gives us *structure*. Parsing is the process of determining whether a sequence of tokens conforms to the grammar of the language and, if so, constructing a parse tree (or AST) that represents its hierarchical structure.

This lecture covers context-free grammars (CFGs), top-down parsing strategies (recursive descent, predictive parsing), and the mathematical tools (FIRST and FOLLOW sets) that make deterministic parsing possible.

### Context-Free Grammars

A context-free grammar G = (V, Σ, R, S) consists of:
- **V**: A finite set of nonterminal symbols (e.g., Stmt, Expr, Type)
- **Σ**: A finite set of terminal symbols (tokens from the scanner)
- **R**: Production rules of the form A → α, where A ∈ V and α ∈ (V ∪ Σ)*
- **S**: The start symbol (S ∈ V)

**Example — simplified expression grammar**:
```
E  → E + T | T
T  → T * F | F
F  → ( E ) | id | num
```

This grammar is **left-recursive**, which causes top-down parsers to loop infinitely. We eliminate left recursion by rewriting:

```
E  → T E'
E' → + T E' | ε
T  → F T'
T' → * F T' | ε
F  → ( E ) | id | num
```

**Ambiguity**: A grammar is ambiguous if some string has two or more distinct parse trees. The classic example is the dangling else:

```
Stmt → if Expr then Stmt else Stmt
     | if Expr then Stmt
     | other
```

For `if E1 then if E2 then S1 else S2`, the `else` can bind to either `if`. Most languages resolve this by associating `else` with the nearest `if`, which can be enforced by restructuring the grammar.

### Predictive Parsing: LL(1)

An LL(1) parser uses a single lookahead token to decide which production to apply. It is called LL(1) because it scans the input **L**eft-to-right, constructs a **L**eftmost derivation, with **1** token of lookahead.

**FIRST set**: For a string α of grammar symbols, FIRST(α) is the set of terminals that begin strings derivable from α. If α can derive ε, then ε ∈ FIRST(α).

**FOLLOW set**: For a nonterminal A, FOLLOW(A) is the set of terminals that can appear immediately to the right of A in some sentential form. If A can be the rightmost symbol, then $ ∈ FOLLOW(A).

**Computing FIRST**:
1. If X is a terminal, FIRST(X) = {X}.
2. If X → ε, add ε to FIRST(X).
3. If X → Y₁Y₂...Yₖ, add FIRST(Y₁) - {ε} to FIRST(X). If ε ∈ FIRST(Y₁), add FIRST(Y₂) - {ε} to FIRST(X). Continue. If ε is in all FIRST(Yᵢ), add ε to FIRST(X).

**Computing FOLLOW**:
1. Add $ to FOLLOW(S) (start symbol).
2. If A → αBβ, add FIRST(β) - {ε} to FOLLOW(B).
3. If A → αB or A → αBβ where ε ∈ FIRST(β), add FOLLOW(A) to FOLLOW(B).

**LL(1) parse table**: For each production A → α and terminal a ∈ FIRST(α), add A → α to M[A, a]. If ε ∈ FIRST(α), add A → α to M[A, b] for each b ∈ FOLLOW(A). If there's a conflict (two entries in the same cell), the grammar is not LL(1).

### Recursive Descent Parsing

Recursive descent is the simplest and most common top-down parsing technique. Each nonterminal becomes a function:

```python
def parse_E():
    parse_T()
    parse_E_prime()

def parse_E_prime():
    if lookahead == '+':
        match('+')
        parse_T()
        parse_E_prime()
    # else: ε-production (do nothing)

def parse_T():
    parse_F()
    parse_T_prime()

def parse_T_prime():
    if lookahead == '*':
        match('*')
        parse_F()
        parse_T_prime()
    # else: ε-production

def parse_F():
    if lookahead == '(':
        match('(')
        parse_E()
        match(')')
    elif lookahead == 'id':
        match('id')
    elif lookahead == 'num':
        match('num')
    else:
        error(f"expected '(', id, or num, got {lookahead}")
```

**Error recovery**: When the parser encounters an unexpected token, it can:
1. **Panic mode**: Skip tokens until a FOLLOW set member is found.
2. **Phrase-level recovery**: Insert or delete tokens to fix common errors.
3. **Error productions**: Add grammar rules that match common errors and produce helpful diagnostics.

### 2040: Practical Parsers

By 2040, most production compilers use hand-written **recursive descent parsers** with error recovery (Clang, GCC, Go, Rust, Swift). The reasons:
- Better error messages than generated parsers.
- More control over context-sensitive parsing (e.g., C's typedef-name ambiguity).
- Performance comparable to or better than table-driven parsers.

**Parser combinators** (functional programming approach): Libraries like Parsec (Haskell), FastParse (Scala), and Nom (Rust) compose small parsers into larger ones. Popular in domain-specific languages and data format parsers.

**PEG (Parsing Expression Grammars)**: An alternative to CFGs. PEGs use ordered choice (/) instead of unordered alternation (|), making them unambiguous by definition. Packrat parsing provides linear-time PEG parsing. Used in many modern language tools.

### Required Reading

- Aho et al. (2006). *Compilers*, Chapter 4 (Syntax Analysis, sections 4.1-4.4).
- Appel (2004). *Modern Compiler Implementation*, Chapter 3.
- Ford, B. (2004). "Parsing Expression Grammars: A Recognition-Based Syntactic Foundation." *POPL*.

### Discussion Questions

1. C's grammar requires the parser to know whether an identifier is a typedef name or an ordinary identifier. How does a recursive descent parser handle this? How would a generated parser handle it?
2. PEG grammars are never ambiguous. Why isn't PEG the universal solution for all language parsing? What are the disadvantages of ordered choice?
3. Most JSON parsers are hand-written. Why? What makes JSON amenable to hand-written parsing?

### Practice Problems

1. **FIRST/FOLLOW**: Given the grammar `E → T E', E' → + T E' | ε, T → F T', T' → * F T' | ε, F → ( E ) | id`, compute FIRST and FOLLOW for all nonterminals.
2. **LL(1) check**: Is the grammar from problem 1 LL(1)? Construct the parse table and check for conflicts.
3. **Left factoring**: The grammar `S → if E then S else S | if E then S | a` is not LL(1) due to common prefixes. Left-factor it and verify the result is LL(1).

---

ᛉ **Lecture 4: Bottom-Up Parsing — LR Parsing and Its Variants**

**Course:** CS302 — Compiler Design & Code Generation  
**Degree:** Bachelor of Science in Computer Science, 2040

---

### Overview

Bottom-up parsers build the parse tree from the leaves (terminals) upward to the root (start symbol). They are more powerful than top-down parsers — every LL(1) grammar is LR(1), but not vice versa. Bottom-up parsers can handle a wider class of grammars, including most programming language grammars without modification.

This lecture covers LR(0), SLR, LALR(1), and CLR(1) parsing, their construction algorithms, and their practical applications in tools like yacc, bison, and their descendants.

### Shift-Reduce Parsing

An LR parser maintains a **stack** of grammar symbols and parser states, and reads input from left to right. At each step, it performs one of two actions:

1. **Shift**: Push the next input symbol onto the stack and transition to the appropriate state.
2. **Reduce**: Pop the right-hand side of a production from the stack, push the left-hand side, and transition to the state indicated by the goto table.

The parser uses two tables:
- **ACTION table**: Maps (state, lookahead) to shift, reduce, accept, or error.
- **GOTO table**: Maps (state, nonterminal) to a new state (used after reductions).

### LR(0) Items and States

An LR(0) item is a production with a dot (•) indicating how much has been seen. For the production `A → XYZ`:
- `A → •XYZ` (nothing seen yet)
- `A → X•YZ` (X seen, expecting Y)
- `A → XY•Z` (XY seen, expecting Z)
- `A → XYZ•` (complete — ready to reduce)

The **closure** of a set of items adds all items that can be derived from the current position of the dot. The **goto** operation moves the dot past a symbol and takes the closure of the result.

An LR(0) parser is constructed by:
1. Computing the closure of the initial item set {S' → •S$}.
2. Computing goto sets for each grammar symbol.
3. Repeating until no new item sets exist.

### SLR (Simple LR)

SLR parsing uses LR(0) items but restricts reductions: a reduction `A → α` is performed only when the lookahead is in FOLLOW(A). This is more restrictive than LR(0), which reduces whenever the dot is at the end of any production.

**SLR limitations**: FOLLOW sets may be too large, causing spurious reductions. Not all grammars that are LR(1) are SLR.

### LALR(1) (Look-Ahead LR)

LALR(1) is the most commonly used variant. It merges LR(1) item sets that have the same core (same LR(0) items) but different lookaheads. This dramatically reduces the number of states (same as SLR) while maintaining most LR(1) power.

**Construction**: Start with LR(1) items. Merge states with the same core. Propagate lookaheads through the merged states.

**LALR(1) vs LR(1)**: LALR(1) may introduce reduce-reduce conflicts that LR(1) does not have. In practice, these conflicts are rare and can be resolved by restructuring the grammar.

**bison/yacc**: The most widely used LALR(1) parser generators. Bison produces C code from a grammar specification with embedded actions. Modern bison supports GLR (Generalized LR) parsing for ambiguous grammars.

### CLR(1) (Canonical LR)

CLR(1) is the most powerful LR variant. It uses full LR(1) items without merging, resulting in many more states but accepting the largest class of LR grammars. In practice, CLR(1) parsers are rarely used because the state count is too large for most programming languages.

### Practical Considerations

**Shift-reduce conflicts**: Occur when the parser can either shift the next token or reduce by a production. Bison resolves these by shifting (the "shift" resolution), which corresponds to the "dangling else" resolution.

**Reduce-reduce conflicts**: Occur when two productions can be reduced with the same lookahead. Always indicate a grammar problem. Bison resolves by choosing the production listed first.

**Operator precedence**: Bison allows specifying precedence rules that resolve shift-reduce conflicts for expressions. `%left`, `%right`, `%nonassoc` declarations control associativity and precedence.

### 2040: The State of Parsing

**GLR parsing**: Bison's GLR mode handles ambiguous grammars by exploring all possible parses simultaneously. Used for C++ (which has inherently ambiguous grammar), COBOL, and other complex languages.

**Error recovery**: Modern parsers (bison, tree-sitter) use error recovery strategies to continue parsing after syntax errors:
- **Error token**: Bison's `error` special token skips input until a synchronizing token is found.
- **Error productions**: Grammar rules that match common error patterns.
- **Partial parsing**: Tree-sitter can parse files with multiple errors, producing a partial AST for IDE features like syntax highlighting and code completion.

**Incremental parsing**: Tree-sitter and similar tools support incremental parsing — re-parsing only the portion of the file that changed. Enables real-time IDE features with <1ms parse times for files under 10,000 lines.

### Required Reading

- Aho et al. (2006). *Compilers*, Chapter 4 (sections 4.5-4.7).
- Appel (2004). *Modern Compiler Implementation*, Chapter 5.
- Grune, D. & Jacobs, C. (2008). *Parsing Techniques: A Practical Guide* (2nd ed.). Springer.

### Discussion Questions

1. Every LL(1) grammar is LR(1), but not vice versa. Give an example of a common programming language construct that is LR(1) but not LL(1). How is this construct handled in practice?
2. LALR(1) merges LR(1) states with the same core. Under what conditions does this merging introduce reduce-reduce conflicts?
3. C++ has an inherently ambiguous grammar (the "most vexing parse"). How do real C++ parsers handle this? Why can't a deterministic parser handle it?

### Practice Problems

1. **LR(0) item sets**: Given the grammar `S → S S + | S S * | a`, construct all LR(0) item sets and the goto table.
2. **SLR parse table**: Using the item sets from problem 1, construct the SLR ACTION and GOTO tables. Show any conflicts.
3. **Shift-reduce resolution**: The expression grammar `E → E + E | E * E | ( E ) | id` has shift-reduce conflicts for `+` and `*`. Using precedence (multiplication before addition, left-associativity), show which actions the parser takes for the input `id + id * id`.

---

ᛉ **Lecture 5: Semantic Analysis & Type Systems — Meaning from Structure**

**Course:** CS302 — Compiler Design & Code Generation  
**Degree:** Bachelor of Science in Computer Science, 2040

---

### Overview

The parser produces a tree, but trees don't execute. Before the compiler can generate code, it must verify that the program is *well-formed*: types are consistent, variables are declared before use, functions are called with the right number of arguments, and operations are applied to compatible operands. This phase is semantic analysis, and its backbone is the type system.

### Type Systems: The Logic of Data

A type system is a tractable syntactic method for proving the absence of certain program behaviors by classifying phrases according to the kinds of values they compute. (Pierce, 2002)

**Static vs. Dynamic Typing**:
- **Static**: Types checked at compile time. Errors caught before execution. (C, Java, Rust, Haskell)
- **Dynamic**: Types checked at runtime. More flexible, more runtime overhead. (Python, JavaScript, Ruby)
- **Gradual**: Mix of static and dynamic. Optional type annotations. (TypeScript, Python with type hints, Reticulated Python)

**Type Soundness** (safety): If a well-typed program compiles, it will not get stuck at runtime (it will either run forever or produce a value of the expected type). This is the combination of **progress** (well-typed programs can always take a step) and **preservation** (well-typed programs remain well-typed after each step).

### Type Checking Rules

Type checking rules are specified as inference rules:

```
Γ ⊢ e₁ : τ₁    Γ ⊢ e₂ : τ₂    τ₂ ≤ τ₁
───────────────────────────────────────────────  (T-Assign)
        Γ ⊢ e₁ = e₂ : τ₁
```

"Under typing environment Γ, if expression e₁ has type τ₁ and e₂ has type τ₂, and τ₂ is a subtype of τ₁, then the assignment e₁ = e₂ has type τ₁."

**Subtyping**: τ₁ ≤ τ₂ means τ₁ is a subtype of τ₂ (every τ₁ value is also a τ₂ value). For records, subtyping is width- and depth-subtyping.

### Symbol Tables and Scopes

The symbol table maps identifiers to their declarations. It must handle nested scopes:

```python
class SymbolTable:
    def __init__(self, parent=None):
        self.parent = parent  # enclosing scope
        self.symbols = {}     # name → (type, kind, offset)
    
    def lookup(self, name):
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None  # undefined
    
    def define(self, name, type, kind, offset):
        self.symbols[name] = (type, kind, offset)
```

**Scope levels**: Global → module → class → function → block. Each level has its own symbol table with a pointer to the enclosing scope.

**Name resolution**: When the compiler encounters an identifier, it looks up the name in the symbol table chain, starting from the innermost scope and proceeding outward. This process is called **environment lookup**.

### Type Inference

For languages with type inference (Haskell, ML, Rust), the compiler doesn't require explicit type annotations. Instead, it infers types from usage using **Hindley-Milner type inference** (Algorithm W):

1. Assign a fresh type variable to each expression whose type is unknown.
2. Generate constraints from the program structure (e.g., `+` requires both operands to be `int` or both to be `float`).
3. Unify the constraints to solve for type variables.

**Unification**: The process of making two types equal by substituting type variables. If we have constraint `α = int → β` and constraint `α = γ → bool`, unification gives `α = int → bool`, `β = bool`, `γ = int`.

### Error Reporting

A good compiler produces helpful error messages. The type checker should report:
- **Location**: File, line, column of the error.
- **Expected vs. actual**: "Expected `int`, found `string`" rather than "Type mismatch."
- **Suggestion**: "Did you mean `x.to_int()`?"
- **Context**: Show the full expression where the error occurs, with the problematic sub-expression highlighted.

**Error recovery**: After detecting one type error, the compiler should continue checking (not stop at the first error). This requires synthesizing default types for ill-typed expressions.

### 2040: Modern Type Systems

By 2040, type systems have become far more expressive than the simple systems of the 1990s:

- **Dependent types** (Idris, Agda): Types can depend on values. `Vec Int n` is a vector of integers of length n. Allows proving properties in the type system.
- **Ownership types** (Rust): Track ownership and borrowing at the type level, guaranteeing memory safety without garbage collection.
- **Effect systems** (Koka, Eff): Track side effects in types. A function's type indicates whether it can throw exceptions, access I/O, or modify mutable state.
- **Linear types** (Rust, Clean): Values that must be used exactly once. Prevent double-free and use-after-free bugs at compile time.
- **Refinement types** (F*, Liquid Haskell): Types with logical predicates. `{x : int | x > 0}` is a positive integer. Complemented by SMT solvers for automatic verification.

### Required Reading

- Pierce, B. C. (2002). *Types and Programming Languages*. MIT Press. Chapters 1-9 (core type systems), 15-16 (subtyping).
- Aho et al. (2006). *Compilers*, Chapter 5 (Syntax-Directed Translation) and Chapter 6 (Type Checking).
- Nielson, F., Nielson, H. R., & Hankin, C. (2015). *Principles of Program Analysis*. Springer. Chapter 4 (Type-Based Analysis).

### Discussion Questions

1. Rust's ownership system prevents use-after-free bugs at compile time. What is the compile-time cost of this guarantee? How does it affect the expressiveness of the language?
2. TypeScript uses gradual typing to add optional type annotations to JavaScript. Does gradual typing provide the same safety guarantees as a fully statically-typed language? What are the holes?
3. Dependent types allow proving program properties in the type system. Why aren't all mainstream languages dependent? What are the practical barriers?

### Practice Problems

1. **Type checking**: Given the environment `{x: int, y: float, f: int → float}`, type-check the expression `f(x) + y`. Show all inference rule applications.
2. **Type inference**: Infer the type of `λf. λx. f(f(x))` using Algorithm W. Show the type variable assignments and unification steps.
3. **Subtyping**: Given `Cat ≤ Animal`, `Dog ≤ Animal`, and `Animal ≤ Object`, which of the following are valid subtyping relationships? (a) `List<Cat> ≤ List<Animal>`, (b) `List<Animal> ≤ List<Cat>`, (c) `Function<Animal, Cat> ≤ Function<Cat, Animal>`.

---

ᛉ **Lecture 6: Intermediate Representations — The Compiler's Common Tongue**

**Course:** CS302 — Compiler Design & Code Generation  
**Degree:** Bachelor of Science in Computer Science, 2040

---

### Overview

The intermediate representation (IR) is the compiler's lingua franca — the common language shared between the front end and the back end. A well-designed IR enables language-independent optimization and retargetable code generation. This lecture covers the major IR forms, their properties, and the trade-offs between expressiveness and optimizability.

### Three-Address Code

The simplest IR is three-address code (TAC), where each instruction has at most one operator and at most three operands:

```
t1 = b * c
t2 = a + t1
x = t2
if x < 10 goto L1
t3 = x - 1
y = t3
goto L2
L1: y = x
L2: ...
```

Properties: Simple, easy to generate, easy to optimize. But unstructured (goto-heavy) and does not preserve high-level information.

### Static Single Assignment (SSA)

SSA form requires that each variable is assigned exactly once. Every use of a variable refers to a single definition point, making dataflow analysis dramatically simpler.

```
Original code:        SSA form:
x = 1                 x₁ = 1
x = 2                 x₂ = 2
y = x + x            y₁ = x₂ + x₂
x = 3                 x₃ = 3
z = x + y            z₁ = x₃ + y₁
```

**φ-functions**: At control flow merge points (where multiple definitions of a variable reach the same point), SSA inserts φ-functions that "select" the appropriate definition based on which predecessor block was executed:

```
if condition:
    x₁ = 1
else:
    x₂ = 2
x₃ = φ(x₁, x₂)  // x₃ = x₁ if came from then, x₂ if came from else
y = x₃ + 1
```

**SSA construction algorithm**:
1. Compute dominators and dominance frontiers for all blocks.
2. Place φ-functions at the dominance frontier of each variable's definition.
3. Rename variables: walk the dominator tree, replacing each use with the current version of the variable.

**SSA advantages**:
- **Simpler dataflow analysis**: Reaching definitions, live variables, and constant propagation become trivial — each use has exactly one definition.
- **Better optimization**: Common subexpression elimination, dead code elimination, and register allocation all benefit from SSA.
- **Compact representation**: No need for def-use and use-def chains; SSA form encodes them directly.

### Control Flow Graphs (CFGs)

A CFG is a directed graph where nodes are basic blocks and edges represent possible control flow:

```
    [B1: entry]
    if (x > 0) goto B2 else goto B3
        │              │
        ▼              ▼
    [B2: then]    [B3: else]
    y = x              y = -x
        │              │
        └──────┬───────┘
               ▼
         [B4: join]
         return y
```

**Basic blocks** are maximal sequences of instructions with one entry point and one exit point.

### LLVM IR

LLVM IR is a low-level, typed, SSA-based IR:

```llvm
define i32 @example(i32 %a, i32 %b, i32 %c) {
entry:
  %1 = mul i32 %b, %c
  %2 = add i32 %a, %1
  ret i32 %2
}
```

### Other IR Forms

**Sea of Nodes**: Used in Java HotSpot JIT and V8 TurboFan. Nodes are values; edges represent data dependencies. Control flow is implicit, enabling aggressive reordering.

**ANF (A-Normal Form)**: Every intermediate result is named. Used in Scala, Kotlin, and many functional language compilers.

### Required Reading

- Appel (2004). *Modern Compiler Implementation*, Chapter 6.
- Lattner & Adve (2004). "LLVM: A Compilation Framework for Lifelong Program Analysis & Transformation." *CGO*.
- Cytron et al. (1991). "Efficiently Computing Static Single Assignment Form." *ACM TOPLAS*.

### Discussion Questions

1. SSA form requires φ-functions at join points. What happens during code generation — how are φ-functions eliminated?
2. LLVM IR uses infinite virtual registers. At what point does the number of registers become finite? What algorithm bridges this gap?
3. A "sea of nodes" IR has no fixed instruction ordering. How does the back end decide the order in which to emit instructions?

### Practice Problems

1. **SSA construction**: Convert the following code to SSA form:
   ```
   x = 1
   y = 2
   if (c) {
       x = 3
   } else {
       x = 4
   }
   y = x + y
   ```
   Show all φ-functions.

2. **CFG construction**: Given the following code, identify basic block leaders, construct the CFG, and list all edges.

3. **LLVM IR**: Write LLVM IR for a simple C function that computes the factorial of n.

---

ᛉ **Lecture 7: Machine-Independent Optimization — Making Code Faster Without Hardware**

**Course:** CS302 — Compiler Design & Code Generation  
**Degree:** Bachelor of Science in Computer Science, 2040

---

### Overview

Optimization transforms a program into a semantically equivalent program that executes faster, uses less memory, or both. "Machine-independent" optimizations operate on the IR without considering target-machine details — they exploit algebraic identities, redundancy, and program structure to reduce work.

### The Optimization Hierarchy

Optimizations are ordered by their scope:

1. **Peephole** (local): Examine a small window of instructions. Examples: constant folding, strength reduction.
2. **Local** (within a basic block): Examples: common subexpression elimination, constant propagation.
3. **Global** (across basic blocks): Examples: global CSE, global constant propagation, dead code elimination.
4. **Interprocedural** (across functions): Examples: inlining, interprocedural constant propagation, alias analysis.

### Peephole Optimizations

**Constant folding**: Evaluate constant expressions at compile time.
```
x = 3 + 5 * 2  →  x = 13
```

**Constant propagation**: If a variable is known to have a constant value, replace uses with the constant.
```
x = 5
y = x + 3  →  y = 8
```

**Strength reduction**: Replace expensive operations with cheaper ones.
```
x = y * 2    →  x = y << 1
x = y * 16   →  x = y << 4
x = y / 8    →  y >> 3
x = y % 8    →  y & 7
```

**Dead code elimination**: Remove code that cannot be reached or whose results are never used.

**Algebraic simplification**:
```
x = y + 0    →  x = y
x = y * 1    →  x = y
x = y * 0    →  x = 0
```

### Common Subexpression Elimination (CSE)

If two expressions compute the same value, the second can reuse the first's result:

```
Before:                    After:
t1 = b * c                t1 = b * c
t2 = a + t1               t2 = a + t1
t3 = b * c                t3 = t1           // CSE
t4 = d + t3               t4 = d + t3
```

### Loop Optimizations

**Loop-Invariant Code Motion (LICM)**: Move computation outside the loop if it produces the same result every iteration.

**Induction variable elimination**: Replace derived induction variables with computations based on the primary induction variable, or eliminate the primary variable entirely.

**Loop unrolling**: Replicate the loop body to reduce loop overhead and enable further optimizations.

**Loop interchange**: Reverse loop nesting to improve cache locality (row-major vs. column-major).

**Loop fusion**: Combine two loops with the same bounds into one loop.

**Loop tiling (blocking)**: Process data in cache-sized blocks to improve locality for large matrices.

### Function Inlining

Replace a function call with the body of the called function. Benefits: eliminates call overhead, exposes further optimization. Costs: increases code size, compilation time.

**Inlining heuristics (2040)**:
- Small functions (≤10 instructions): always inline.
- Medium functions: inline if called from hot paths (profile-guided).
- Large functions: inline only if call frequency justifies code size increase.
- Virtual/dynamic calls: inline after devirtualization (type profiling).

### Required Reading

- Aho et al. (2006). *Compilers*, Chapter 8 (sections 8.1-8.5).
- Cooper & Torczon (2022). *Engineering a Compiler*, Chapters 8-9.
- Muchnick (1997). *Advanced Compiler Design*, Chapters 12-13.

### Discussion Questions

1. Constant propagation can enable further optimizations. Give an example where constant propagation alone doesn't help but enables a second optimization that does.
2. Loop unrolling increases code size. At what point does unrolling become counterproductive?
3. Inlining a virtual call requires devirtualization. How does profile-guided optimization help?

### Practice Problems

1. **Constant propagation cascade**: Apply constant propagation and folding to a block of code, showing the fully optimized result.
2. **CSE**: Find and eliminate common subexpressions in a given basic block.
3. **Loop optimization**: Apply LICM, strength reduction, and induction variable elimination to a given loop.

---

ᛉ **Lecture 8: Dataflow Analysis & Loop Optimizations — Understanding the Flow of Data**

**Course:** CS302 — Compiler Design & Code Generation  
**Degree:** Bachelor of Science in Computer Science, 2040

---

### Overview

Dataflow analysis is the mathematical foundation for most compiler optimizations. By analyzing how data flows through the program, the compiler can safely transform it.

### The Dataflow Analysis Framework

A dataflow analysis is specified by:
1. **Domain**: The set of values computed over (sets of definitions, sets of variables).
2. **Direction**: Forward (entry→exit) or backward (exit→entry).
3. **Transfer function**: How each statement transforms information.
4. **Meet operator**: How information from multiple paths is combined (∪ for may analyses, ∩ for must analyses).
5. **Boundary condition**: Initial value at entry (forward) or exit (backward).

```
Forward:  IN[B] = meet(OUT[P] for all predecessors P)
          OUT[B] = f_B(IN[B])

Backward: OUT[B] = meet(IN[S] for all successors S)
          IN[B] = f_B(OUT[B])
```

### Reaching Definitions

**Question**: Which definitions of a variable reach each point?

**Transfer**: OUT[B] = gen_B ∪ (IN[B] - kill_B)
**Meet**: ∪ (union — any definition reaching through any path)
**Application**: Constant propagation, type-based optimizations, detecting undefined variable uses.

### Live Variable Analysis

**Question**: Which variables are live (will be used later) at each point?

**Transfer**: IN[B] = use_B ∪ (OUT[B] - def_B)
**Direction**: Backward
**Application**: Dead code elimination, register allocation.

### Available Expressions

**Question**: Which expressions have already been computed at each point?

**Meet**: ∩ (intersection — available on ALL paths)
**Application**: Global common subexpression elimination.

### Very Busy Expressions

**Question**: Which expressions are guaranteed to be computed later?

**Meet**: ∩ (intersection — busy on ALL paths)
**Application**: Code hoisting.

### Lattice Theory Foundation

Each analysis corresponds to a lattice with partial order, top, bottom, and meet operator. The fixed-point algorithm iterates until convergence, guaranteed in O(n × d) iterations.

### Advanced Loop Optimizations

**Loop-carried dependencies**: Dependencies between iterations that prevent parallelization.

**Polyhedral model**: Represents loop iterations as integer points in a polyhedron, enabling transformations like tiling, fusion, and interchange as affine transformations.

**Auto-vectorization**: Detects loop iterations that can execute in parallel using SIMD instructions (SSE, AVX, NEON).

### 2040: ML-Guided Optimization

By 2040, compilers use machine learning to guide optimization decisions:

- **Inlining decisions**: ML models predict profitability based on call frequency, function size, and historical performance.
- **Loop transformation ordering**: ML models learn which sequences yield the best performance.
- **Register allocation heuristics**: ML models predict spilling behavior.

LLVM's MLGO project uses reinforcement learning to train inlining and register allocation policies that outperform hand-tuned heuristics.

### Required Reading

- Aho et al. (2006). *Compilers*, Chapter 9.
- Nielson, Nielson & Hankin (2015). *Principles of Program Analysis*, Chapters 2-3.
- Muchnick (1997). *Advanced Compiler Design*, Chapters 6-7.

### Discussion Questions

1. What would a "must-be-live" analysis (intersection instead of union) be useful for?
2. The polyhedral model enables powerful transformations. Why isn't it used for all loops?
3. ML-guided optimization outperforms hand-tuned heuristics on benchmarks. How would you verify correctness?

### Practice Problems

1. **Reaching definitions**: Compute reaching definitions for a given CFG after fixed-point iteration.
2. **Live variables**: Compute live variables for each block (backward analysis).
3. **Available expressions**: Compute available expressions for a given program.

---

ᛉ **Lecture 9: Code Generation & Register Allocation — From IR to Machine**

**Course:** CS302 — Compiler Design & Code Generation  
**Degree:** Bachelor of Science in Computer Science, 2040

---

### Overview

Code generation transforms the optimized IR into target machine code. The two central problems: instruction selection (choosing machine instructions) and register allocation (assigning values to registers vs. memory).

### Instruction Selection

Maps IR operations to target machine instructions. Multiple implementations may exist for the same IR operation:

```
IR: x = y * 4
Option 1: imul r1, y, 4; mov x, r1    // multiply
Option 2: shl r1, y, 2; mov x, r1       // shift
Option 3: add r1, y, y; add r1, r1, r1  // double twice
```

**Tree pattern matching**: IR and instructions are tree patterns. Instruction selection finds the cheapest tiling of the IR tree.

**LR(1)-based selection**: Used in BURG/IBURG. Produces optimal instruction sequences in O(n) time.

### Register Allocation

The difference between all values in registers and all values in memory can be **2-10x** in performance.

**Graph coloring register allocation** (Chaitin, 1982):
1. Build interference graph (nodes = registers, edges = simultaneous liveness).
2. Simplify: remove nodes with degree < k.
3. Spill: if all nodes have degree ≥ k, select a node for spilling.
4. Select: assign colors (registers) to removed nodes.
5. Start over if spills occurred.

**Coalescing**: When `mov x, y` exists and x, y don't interfere, assign them the same register, eliminating the copy.

**Linear scan** (Poletto & Sarkar, 1999): O(n) time. Sort intervals by start, assign/free registers greedily. Used in JIT compilers where compilation speed matters.

### SSA-Based Register Allocation

SSA form simplifies register allocation because the interference graph is a **chordal graph**, which can be optimally colored in O(|V|) time. This makes register allocation tractable (polynomial time) in SSA form, unlike general register allocation which is NP-complete.

**Spill code**: Inserting load/store instructions for values that can't fit in registers. Heuristics: spill variables with fewest uses, spill variables not in loops, rematerialization (recompute instead of load).

### Instruction Scheduling

Reorder instructions to minimize pipeline stalls:

- **RAW (Read After Write)**: Instruction B uses A's result. B must wait.
- **List scheduling**: Build dependence DAG, assign priorities (longest path to exit), schedule highest-priority ready instruction first.

### Required Reading

- Aho et al. (2006). *Compilers*, Chapter 8 (sections 8.6-8.7).
- Cooper & Torczon (2022). *Engineering a Compiler*, Chapter 13.
- Chaitin (1982). "Register Allocation & Spilling via Graph Coloring." *SIGPLAN*.

### Discussion Questions

1. Why do most production compilers still use graph coloring instead of SSA-based allocation?
2. Is linear scan "good enough" for JIT-compiled code? When would you want something better?
3. Instruction scheduling and register allocation interact. How do production compilers resolve this chicken-and-egg problem?

### Practice Problems

1. **Interference graph**: Build and color an interference graph given live ranges.
2. **Graph coloring allocation**: Apply Chaitin's algorithm with k=3 registers.
3. **Instruction scheduling**: Schedule instructions to minimize pipeline stalls on a machine with 2-cycle load latency.

---

ᛉ **Lecture 10: LLVM — Architecture, IR, and Passes**

**Course:** CS302 — Compiler Design & Code Generation  
**Degree:** Bachelor of Science in Computer Science, 2040

---

### LLVM Architecture

LLVM is a compiler infrastructure designed as a set of reusable libraries with well-defined interfaces:

```
┌─────────────┐  ┌─────────────┐  ┌──────────┐  ┌──────────┐
│ Clang (C/C++)│  │  Rustc      │  │ Swift    │  │  Others   │
│  Front End   │  │  Front End  │  │ Front End│  │ Front Ends│
└──────┬───────┘  └──────┬──────┘  └────┬─────┘  └─────┬────┘
       │                  │              │              │
       └──────────────────┴──────────────┴──────────────┘
                          │
                     LLVM IR (.ll / .bc)
                          │
               ┌──────────┴──────────┐
               │   Optimization      │
               │   Passes           │
               │  (-O0 to -O3, -Os) │
               └──────────┬──────────┘
                          │
       ┌──────────────────┼──────────────────┐
       │                  │                  │
  ┌────┴─────┐     ┌─────┴─────┐     ┌─────┴─────┐
  │ x86-64   │     │  ARM64    │     │   WASM    │
  │ Back End │     │ Back End  │     │ Back End  │
  └──────────┘     └───────────┘     └───────────┘
```

### LLVM IR in Detail

LLVM IR is strongly typed, SSA-based, with infinite virtual registers:

**Types**: i1, i8, i16, i32, i64, float, double, ptr, arrays, structs, vectors, functions.

**Instructions**: add, sub, mul, udiv, sdiv, fadd, fsub, fmul, and, or, xor, shl, lshr, ashr, alloca, load, store, getelementptr, icmp, fcmp, br, ret, call, phi.

Example — `max(a, b)`:
```llvm
define i32 @max(i32 %a, i32 %b) {
entry:
  %cmp = icmp sgt i32 %a, %b
  br i1 %cmp, label %then, label %else
then:
  br label %merge
else:
  br label %merge
merge:
  %result = phi i32 [%a, %then], [%b, %else]
  ret i32 %result
}
```

### Optimization Passes

- **Analysis passes**: Compute information without modifying IR (dominators, loops, alias analysis).
- **Transformation passes**: Modify IR (constant propagation, dead code elimination, loop unrolling, inlining, vectorization).

**Pass pipeline at -O2**: Always Inliner → Instruction Combine → GVN → CFG Simplification → Loop Simplify → SLP Vectorizer → Loop Vectorizer → DCE → Tail Call Opt → Merge Functions.

### Writing a Custom LLVM Pass

```cpp
#include "llvm/IR/Function.h"
#include "llvm/Pass.h"
#include "llvm/Support/raw_ostream.h"

struct HelloPass : public FunctionPass {
  static char ID;
  HelloPass() : FunctionPass(ID) {}
  bool runOnFunction(Function &F) override {
    errs() << "Hello from: " << F.getName() << "\n";
    return false;
  }
};
```

### Required Reading

- Lattner & Adve (2004). "LLVM: A Compilation Framework for Lifelong Program Analysis & Transformation." *CGO*.
- LLVM Language Reference Manual
- LLVM Pass Infrastructure documentation

### Discussion Questions

1. LLVM IR has no fixed instruction ordering within a basic block. How does LLVM decide ordering for emission?
2. What are the advantages and disadvantages of opaque pointer type (ptr) vs. typed pointers?
3. Why would you write a custom LLVM pass? Give a concrete example.

### Practice Problems

1. **LLVM IR writing**: Write LLVM IR for a C function that sums an array.
2. **Pass analysis**: Write an LLVM analysis pass that counts basic blocks per function.
3. **Optimization trace**: Trace optimizations that -O1 would apply to `x = a + 0`.

---

ᛉ **Lecture 11: Just-In-Time & Ahead-Of-Time Compilation — When to Compile and Why**

**Course:** CS302 — Compiler Design & Code Generation  
**Degree:** Bachelor of Science in Computer Science, 2040

---

### The Compilation Continuum

```
AOT ──────────────── JIT ──────────────── Interpreter
(compile before run) (compile during run)   (no compilation)
Fast execution       Balances startup/      Fastest startup
Slower startup       throughput             Slowest execution
No runtime info      Adapts to patterns     No optimization
```

### Just-In-Time Compilation

**Tiered compilation** (V8 pipeline):
```
Source → Parser → Ignition (interpreter, collects profiles)
                    ↓ (hot function detected)
                Sparkplug (non-optimizing JIT, fast compilation)
                    ↓ (very hot function detected)
                TurboFan (optimizing JIT, slow compilation, fast code)
```

**Profiling data**: Type feedback, branch frequencies, call frequencies, inline cache hits.

**Deoptimization**: When an optimizing JIT makes an assumption that fails at runtime, it must revert to interpreter state. Requires mapping JIT state to interpreter state and transitioning execution.

### Profile-Guided Optimization (PGO)

1. Instrumented build: compile with profiling counters.
2. Profile collection: run on representative workloads.
3. Optimized build: compile using profile data.

PGO enables better inlining, branch layout, code placement, and register allocation.

**AutoFDO**: Uses hardware performance counters (Linux perf) for near-zero overhead profiling.

### Ahead-Of-Time Compilation

**Advantages**: No startup cost, no profiling overhead, predictable performance.
**Disadvantages**: No runtime information, must optimize for general case, platform-specific binaries.

**2040 AOT landscape**: Native AOT (Go, Rust, C++), Java GraalVM Native Image, .NET AOT, WASM AOT.

### WebAssembly

WASM is a portable, size-efficient binary format designed as a compilation target:
- **Portable**: Architecture-independent
- **Safe**: Sandboxed execution
- **Efficient**: Binary format, streams and compiles fast
- **Multi-language**: C, C++, Rust, Go, C# compile to WASM
- **WASI**: System interface for OS features

### 2040: Blurring the Lines

- **Speculative AOT**: Compile with speculative optimizations, guard with runtime checks.
- **Progressive compilation**: Start unoptimized, progressively optimize as the program runs.
- **Continuous compilation**: In long-running systems, re-optimize as workloads change.
- **ML-guided compilation**: ML models predict optimization effectiveness in real-time.

### Required Reading

- Aycock (2003). "A Brief History of Just-In-Time." *ACM Computing Surveys*, 35(2).
- Haas et al. (2017). "Bringing the Web up to Speed with WebAssembly." *PLDI*.

### Discussion Questions

1. What is the optimal tier transition threshold for JIT compilation? How would you determine it?
2. What are the trade-offs of WASM compared to native AOT? When would you prefer WASM?
3. What happens when PGO profiling workloads don't match production workloads?

### Practice Problems

1. **Tiered compilation ROI**: A function runs at 1/100 native speed in the interpreter. The optimizing JIT takes 10ms to compile but produces native speed. After how many calls is JIT compilation worth the cost?
2. **Deoptimization steps**: Describe the steps to deoptimize when a JIT assumption fails.
3. **PGO branch layout**: Given 95/5 branch ratio, how should the compiler lay out code?

---

ᛉ **Lecture 12: The 2040 Compiler Landscape — ML, Verification, and Multi-Target Compilation**

**Course:** CS302 — Compiler Design & Code Generation  
**Degree:** Bachelor of Science in Computer Science, 2040

---

### ML-Guided Optimization

**MLGO (Machine Learning Guided Optimization)** — LLVM's ML framework:
- Uses reinforcement learning for inlining and register allocation policies.
- Trained on large corpora of real programs and continuously improved.

**AutoTVM / Ansor** — ML-based schedule generation for tensor operators:
- Searches the space of possible schedules for deep learning operators.
- Achieves 2-10x speedups over hand-tuned schedules.

**ML-based phase ordering**: The order of optimization passes affects code quality. ML models learn optimal orderings.

**Learning to compile**: End-to-end models that take source code and emit optimized machine code. Still experimental.

### Verified Compilers

**CompCert** (Leroy, 2009): Verified C compiler in Coq. Proves compiled code behaves exactly as the source specifies.

**CakeML**: Verified ML compiler in HOL4. Proves correctness end-to-end including the compiler itself.

**Vellvm**: Verified LLVM IR subset. Proves optimization passes preserve semantics.

**Challenge**: Verified compilers handle language subsets and are slower than production compilers, but are invaluable for safety-critical systems.

### Multi-Target Compilation

By 2040, a single program must compile to: x86-64, ARM64, RISC-V, GPU (CUDA/ROCm/SPIR-V), TPU/NPU, WASM.

**LLVM's approach**: Each target implements `TargetLowering`. Optimization passes are target-independent; only final lowering and emission are target-specific.

**Tensor compilers** (TVM, XLA, MLIR): Compile computational graphs to diverse hardware:
```
PyTorch/TF Model → Relay IR → TVM/Ansor → x86-64 | ARM64 | CUDA | WASM
```

**MLIR (Multi-Level IR)**: Framework for defining domain-specific IRs:
- `affine`: Loop nest transformations (polyhedral model)
- `linalg`: Linear algebra operations
- `gpu`: GPU kernel abstractions
- `spirv`: SPIR-V compilation target
- `llvm`: Lowering to LLVM IR

### Compilation for AI

AI compilers (TVM, XLA, TensorRT, TorchInductor) compile ML models:
- **Graph optimization**: Constant folding, operator fusion, dead code elimination.
- **Kernel generation**: Auto-generating optimized GPU kernels.
- **Quantization**: Reducing precision (FP32 → FP16 → INT8 → INT4).
- **Memory optimization**: Recomputation, operator scheduling, memory planning.

### The Synthesis: Compilers in 2040

The compiler of 2040 is:
1. **Verified**: Safety-critical code compiled by verified compilers proving correctness.
2. **Adaptive**: ML-guided optimization learns from runtime profiles.
3. **Multi-target**: A single source compiles to CPUs, GPUs, TPUs, WASM.
4. **Collaborative**: IDE and compiler work together for real-time feedback.
5. **AI-augmented**: Large language models assist code generation, refactoring, debugging.

The fundamental insight remains: translate source programs to machine programs while preserving semantics and improving efficiency. What has changed is the scale, diversity, and intelligence of the translation.

At the University of Yggdrasil, we believe that the compiler is the rune-smith's forge — the place where abstract thought becomes concrete action. The front end is the incantation, the IR is the seidr that transforms form, and the back end is the hammer that shapes the final blade. May your compilations be correct, your optimizations fast, and your registers ever sufficient.

### Required Reading

- Leroy (2009). "Formal Verification of a Realistic Compiler." *CACM*, 52(7).
- Lattner et al. (2021). "MLIR: Scaling Compiler Infrastructure for Domain Specific Computation." *CGO*.
- Chen et al. (2018). "TVM: An Automated End-to-End Optimizing Compiler for Deep Learning." *OSDI*.

### Discussion Questions

1. A verified compiler proves compilation correctness. Does this mean the compiled program is correct? What assumptions does the verification make?
2. ML-guided optimization learns from profiling data. If training data is biased, what optimizations might it miss?
3. What are the challenges of compiling to a TPU vs. an x86 CPU? How does the strategy differ?

### Practice Problems

1. **ML policy design**: Design a reward function for RL agent controlling inlining decisions. What metrics should it include?
2. **Verification sketch**: Write an informal proof that constant folding is correct: if source has `x = 3 + 5`, compiled has `x = 8`. What invariants must hold?
3. **MLIR dialect**: Design a `quantum` dialect for MLIR with gates (H, X, CNOT), measurements, and classical control flow. Give operations and types.

---

## Final Examination Preparation

### Exam Format

**Part A: Analytical Problems (60 points)** — 8 short-answer problems covering:
- Lexical analysis and regular expressions (Lectures 1-2)
- Parsing and grammar analysis (Lectures 3-4)
- Type systems and type checking (Lecture 5)
- Intermediate representations (Lecture 6)
- Optimization techniques (Lectures 7-8)
- Code generation and register allocation (Lecture 9)
- LLVM architecture (Lecture 10)
- JIT and AOT compilation (Lecture 11)

**Part B: Design Problem (40 points)** — One comprehensive problem requiring lexer/parser design, type system design, IR generation, optimization selection, register allocation, and target-specific code generation.

### Sample Exam Problems

**Part A:**
1. Construct NFA for `(a|b)*abb` using Thompson's construction, convert to DFA.
2. Compute FIRST/FOLLOW sets, construct LL(1) parse table.
3. Perform type checking on a given expression with subtyping rules.
4. Convert code to SSA form, showing all φ-functions.
5. Apply constant propagation, CSE, and dead code elimination.
6. Perform reaching definitions analysis on a given CFG.
7. Color an interference graph with minimum colors. Show spills with k=3.
8. Write LLVM IR for a given C function.

**Part B:** Design a compiler front end for a simple language with integer/boolean types, arithmetic/comparison operators, if-else/while statements, and functions. Address: lexer specification, grammar, type checking rules, IR generation, and three optimizations with justification.

### Study Guide

**Key algorithms to trace**: Subset construction, LL(1) table construction, LR(0) items, SSA construction, graph coloring register allocation, list scheduling.

**Key concepts to explain**: Left recursion, SLR vs LALR(1) vs CLR(1), SSA simplification of dataflow analysis, graph coloring vs linear scan, JIT pipeline, PGO benefits.

**Key systems to compare**: LLVM vs GCC, JIT vs AOT, SSA vs three-address code.

### Farewell

As the Norns weave the threads of fate at the foot of Yggdrasil, so too does the compiler weave the threads of source into the fabric of execution. The front end reads the runes of your intent, the middle end reshapes them into more efficient patterns, and the back end stamps them into the iron of machine code. May your parsing tables be unambiguous, your dataflow analyses converge swiftly, and your registers never spill. Hail the rune-smiths — the compilation never ends.