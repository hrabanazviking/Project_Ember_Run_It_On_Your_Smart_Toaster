# SA102: Advanced Linux Systems Administration — The Command Line, Automation, and the Server
## Bachelor of Science in Computer Systems Administration — University of Yggdrasil, 2040

**Credits:** 4
**Prerequisites:** SA101
**Description:** Deep dive into Linux systems administration focusing on advanced command-line operations, shell scripting, text processing, system services, logging, and the foundational automation skills that define the 2040 SA. Students master the tools and mental models for managing servers at scale.

**Instructor:** Dr. Sven Halldórsson, Professor of Systems Administration
**Lab:** Mjölnir Systems Lab, Sublevel 2, Hákon Computing Centre

---

## Lectures

ᚠ **Lecture 1: The Linux Philosophy — Everything Is a File**

**Course:** SA102 — Advanced Linux Systems Administration
**Degree:** Bachelor of Science in Computer Systems Administration, University of Yggdrasil, 2040

---

### Overview

The Unix philosophy — "do one thing and do it well," "everything is a file," "text streams are the universal interface" — remains the foundation of Linux administration in 2040. This lecture covers the design principles of Unix/Linux, the shell as a programming environment, and the 2040 evolution toward declarative and immutable infrastructure.

### Key Topics

- **Unix Philosophy:** Small, composable tools. Pipes and filters. The power of text streams. Why the command line persists in an age of GUIs.
- **The Shell as Interface:** Bash, zsh, and the 2040 *Norn Shell* — an AI-augmented shell that suggests commands, explains output, and automates routine tasks. The shell as the primary interface between human and system.
- **Everything Is a File:** Regular files, directories, devices (/dev), processes (/proc), network sockets, and the 2040 *Neural Interface File System* (NIFS) that exposes neuromorphic chip state as readable files.
- **Text Processing:** grep, sed, awk, cut, sort, uniq, and the 2040 *Pattern Weaver* — an AI tool that generates regex and awk scripts from natural language descriptions.

### Lecture Notes

The command line is not a relic; it is a force multiplier. A proficient SA can accomplish in one piped command what would take minutes of GUI clicking. The shell is also the foundation of automation: every script is a sequence of shell commands, and every orchestration tool ultimately generates shell commands on remote systems. The GUI is for exploration; the shell is for execution.

The Norn Shell, deployed at Yggdrasil for SA training, augments traditional shell interaction with AI assistance. Type a partial command and the Norn suggests completions based on context. Receive error output and the Norn explains the likely cause and fix. Ask "show me the largest log files" and the Norn generates the appropriate `find` and `du` pipeline. But the Norn is an assistant, not a replacement: the SA must understand what the generated commands do, or they cannot debug failures or adapt to edge cases.

### Required Reading

- Kernighan, B.W. & Pike, R. (2033). *The Unix Programming Environment*, 3rd Edition. Prentice Hall. Chapters 1-3.
- Yggdrasil Norn Shell Documentation (2040). UoY Digital Press.

### Discussion Questions

1. The GUI is more discoverable than the command line. Should beginner SAs start with GUI tools and transition to the command line, or learn the command line first?
2. The Norn Shell generates commands from natural language. What are the risks of executing AI-generated commands without understanding them? How would you balance productivity and safety?
3. "Everything is a file" simplifies the interface but creates security risks (e.g., /proc exposes process state). How would you design a system that preserves the simplicity while limiting exposure?

---

ᚢ **Lecture 2: Shell Scripting Mastery**

**Course:** SA102 — Advanced Linux Systems Administration
**Degree:** Bachelor of Science in Computer Systems Administration, University of Yggdrasil, 2040

---

### Overview

Shell scripting is the SA's primary automation tool. This lecture covers advanced bash programming: variables, arrays, conditionals, loops, functions, error handling, and the 2040 best practices that produce reliable, maintainable, and secure scripts.

### Key Topics

- **Variables and Arrays:** Local vs. global variables. Arrays and associative arrays. Quoting and word splitting. The 2040 *Type-Safe Shell* (tss) — an experimental shell that adds static typing to bash.
- **Control Structures:** if/then/else, case, for, while, until. The 2040 *Structured Bash* standard: mandatory indentation, explicit variable declaration, and prohibited globbing.
- **Functions and Modularity:** Defining and calling functions. Return codes and exit statuses. Source files and script libraries. The 2040 *Bash Module System* (bms) — importing reusable script modules.
- **Error Handling:** set -euo pipefail. Traps for signals and errors. Logging and alerting on script failures. The 2040 *Fail-Fast* philosophy: scripts should fail immediately and loudly, not silently and slowly.
- **Security:** Command injection, path manipulation, and the dangers of eval. Input validation and sanitization. The 2040 *Shell Security Audit* (SSA) tool that scans scripts for common vulnerabilities.

### Lecture Notes

Reliable shell scripts are rare. Most scripts written by junior SAs are brittle: they fail silently on error, break when filenames contain spaces, and assume commands exist that may not be installed. The Yggdralis Scripting Standard, enforced in all production environments, requires: shebang line, `set -euo pipefail`, quoted variables, explicit exit codes, and comments explaining non-obvious logic. Scripts that do not meet this standard are rejected in code review.

The fail-fast philosophy is essential for operational reliability. A script that encounters an error and continues may produce partial results, corrupt data, or leave the system in an inconsistent state. Better to fail immediately, alert the operator, and leave the system in a known (if non-functional) state than to continue blindly and create a worse problem. The `set -e` option causes the script to exit on any command failure. Combined with `set -u` (fail on undefined variables) and `set -o pipefail` (catch failures in pipelines), it creates a script that fails safely.

### Required Reading

- Blum, R. & Bresnahan, C. (2034). *Linux Command Line and Shell Scripting Bible*, 5th Edition. Wiley. Chapters 11-15.
- Yggdrasil Scripting Standard (2040). UoY Digital Press.

### Discussion Questions

1. A junior SA writes a backup script without `set -e`. The script runs nightly but silently fails when the destination disk is full. How would you redesign the script to detect and report this failure?
2. The `eval` command is powerful but dangerous. Under what circumstances is `eval` justified, and how would you mitigate its risks?
3. A script must process filenames that may contain spaces, newlines, and special characters. Design a robust approach that handles all cases safely.

---

ᚦ **Lecture 3: Text Processing and Data Transformation**

**Course:** SA102 — Advanced Linux Systems Administration
**Degree:** Bachelor of Science in Computer Systems Administration, University of Yggdrasil, 2040

---

### Overview

Text is the universal data format of Unix. This lecture covers the tools for processing, transforming, and analyzing text: grep, sed, awk, regular expressions, and the 2040 AI-augmented text processing tools.

### Key Topics

- **Regular Expressions:** Basic and extended regex. Character classes, quantifiers, anchors, grouping, and backreferences. The 2040 *Neural Regex* tool that generates regex from examples.
- **grep and ripgrep:** Pattern matching in text streams. The 2040 *Semantic Grep* that matches meaning, not just strings (e.g., matching "disk full," "no space," and "ENOSPC" as equivalent concepts).
- **sed:** Stream editing. Substitution, deletion, insertion, and address ranges. The 2040 *Visual Sed* tool that shows changes in real time.
- **awk:** Pattern-action programming. Fields, records, variables, and built-in functions. The 2040 *Awk Compiler* that generates optimized C code from awk scripts for performance-critical applications.
- **jq and JSON Processing:** Parsing and transforming JSON data. The 2040 *Structured Query Shell* (sqsh) that queries JSON, XML, YAML, and TOML with SQL-like syntax.

### Lecture Notes

Text processing is the SA's daily bread. Logs are text. Configurations are text. Output from commands is text. The ability to extract, transform, and summarize text separates the proficient SA from the novice. A single awk command can replace hundreds of lines of Python for simple data transformation tasks.

Neural Regex represents the 2040 evolution of pattern matching. Instead of writing a regex manually, the SA provides positive and negative examples: "match 'disk full' and 'no space left' but not 'space station' and 'disk drive'.