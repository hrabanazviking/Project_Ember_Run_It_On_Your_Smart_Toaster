# IT105: Programming for IT (Python, Bash, PowerShell)
## Bachelor of Science in Information Technology — University of Yggdrasil, 2040

**Credits:** 4  
**Prerequisites:** IT101  
**Description:** The foundational programming course for IT professionals. Students master the three languages that dominate operational automation in 2040: Python (the lingua franca of infrastructure scripting), Bash (the native tongue of Linux systems), and PowerShell (the automation engine of the Windows ecosystem). The course emphasises practical problem-solving over software engineering theory: reading log files, querying APIs, transforming data, orchestrating remote systems, and building tools that eliminate toil. Every lecture includes live coding and a lab assignment that solves a real operational problem.

**Instructor:** Dr. Sigrún Vérendóttir, Department of Information Technology  
**Lab:** YggLab Code Forge, Muninn Computing Centre, Second Floor  
**Office Hours:** Mondays and Wednesdays, 13:00-15:00 UTC

---

## Lectures

ᚠ **Lecture 1: The Automation Mindset — Why IT Professionals Must Program**

**Course:** IT105 — Programming for IT (Python, Bash, PowerShell)  
**Degree:** Bachelor of Science in Information Technology, University of Yggdrasil, 2040

---

### Overview

This opening lecture establishes programming not as an abstract skill but as the primary tool of the IT professional. The technician performs tasks manually; the professional writes code that performs tasks automatically, consistently, and at scale. The lecture introduces the "automation paradox" (automated systems require more skilled operators to design but less skilled operators to run), the economic case for automation (return on investment calculations), and the ethical dimension (automating away drudgery to free humans for creative and judgment-intensive work). Students write their first operational script before the lecture ends.

### Key Topics

- **The Technician versus the Professional:** A technician knows how to restart a service, create a user account, or check disk space. A professional writes a script that restarts the service with pre-flight health checks, creates user accounts from a CSV file with validation and logging, and monitors disk space continuously with predictive alerting. The lecture quantifies the difference: a task performed manually 100 times per year, taking 5 minutes each, costs 8.3 hours. A script that takes 2 hours to write and test pays for itself in the first year and generates 6.3 hours of saved time annually thereafter.
- **The Automation Paradox:** As systems become more automated, the remaining failures require deeper expertise to diagnose. A self-healing system that automatically replaces failed nodes reduces routine work but produces novel failure modes that no one has seen before. The lecture argues that automation does not eliminate the need for expertise; it elevates the expertise to a higher level. The IT professional of 2040 designs automation, debugs automation failures, and governs automated systems — they do not merely execute manual procedures.
- **When to Automate and When Not To:** The decision framework. Automate: tasks performed more than twice, tasks with high error rates, tasks requiring audit trails, tasks that scale linearly with system count. Do not automate: one-off tasks, tasks with rapidly changing requirements, tasks where human judgment is essential (e.g., incident triage for novel attacks), and tasks where the automation cost exceeds the manual cost. The lecture includes case studies of over-automation (a company that automated a quarterly report with 2,000 lines of Terraform and YAML when a 20-line Python script would have sufficed) and under-automation (a team that manually provisioned 500 VMs over three months).
- **The Three Languages of IT:** Python, Bash, and PowerShell as a triad. Python for complex logic, data processing, and API interaction. Bash for quick system tasks, text processing pipelines, and glue between tools. PowerShell for Windows ecosystem management and object-oriented automation. The lecture emphasises that fluency in all three is the 2040 baseline; professionals who know only one are limited in the environments they can operate.
- **Live Coding:** Students open a terminal and write a Bash one-liner that lists all files modified in the last 24 hours, sorted by size. Then they write a Python script that does the same thing with `pathlib` and `datetime`. Then they write a PowerShell command that achieves the same on Windows. The point is not the specific task but the realisation that the same operational concept maps to three different syntaxes.

### Lecture Notes

The automation mindset is a cultural shift as much as a technical one. Many IT organisations are trapped in a "ticket culture": every request becomes a ticket, assigned to a human, executed manually, and closed. This culture scales linearly with staff size and creates bottlenecks. The automation culture treats operational tasks as code: version-controlled, tested, reviewed, and deployed. A request to create 50 user accounts becomes a pull request to the identity management repository, reviewed by a peer, and applied automatically. The same governance (review, audit, rollback) applies, but the execution is machine-speed rather than human-speed.

The economic case for automation is often miscalculated. Managers see "2 hours to write a script" and compare it to "5 minutes to do it manually," concluding that automation is not worth it. But this ignores: the cumulative time over repetitions, the error rate of manual work (a 1% error rate on 1,000 manual operations means 10 errors to remediate), the opportunity cost (the human could be doing higher-value work), and the audit trail (manual actions are often unlogged; scripts log automatically). The lecture provides a calculator: given task frequency, manual time, error rate, and hourly cost, compute the break-even point for automation.

The ethical dimension is often overlooked. Repetitive manual IT work is soul-destroying: clicking through the same wizard 50 times, copying and pasting the same configuration with minor variations, checking the same dashboard every morning. Automation eliminates this drudgery, freeing humans for work that requires judgment, creativity, and empathy: designing resilient architectures, mentoring junior engineers, responding to novel incidents, and advocating for users. The Yggdrasil IT Department's automation charter explicitly states: "We automate tasks, not people. Every automation project must include a plan for redeploying the time saved to higher-value work."

### Required Reading

- Limoncelli, T.A. et al. (2032). *The Practice of System and Network Administration*, 4th Edition. Addison-Wesley. Chapter 21 (Automation).
- Sweigart, A. (2034). *Automate the Boring Stuff with Python*, 3rd Edition. No Starch Press. Introduction and Chapter 1.
- Jones, R. & Hicks, J. (2034). *PowerShell in Action*, 4th Edition. Manning. Chapter 1.
- Yggdrasil IT Automation Charter (2040). "Principles, Economics, and Ethics of Operational Automation."

### Discussion Questions

1. Your team spends 4 hours per week on manual certificate renewal. Estimate the total annual cost (including error remediation and opportunity cost) and the break-even point for full automation. Present your calculation with assumptions.
2. "Automation concentrates expertise." Explain this statement using the concept of the automation paradox. If routine tasks are automated, what happens to junior engineers who previously learned by performing those tasks?
3. The Norse *húskarl* maintained the longhouse not through sporadic heroic effort but through steady, disciplined daily labour. How does this quotidian stewardship inform the IT professional's approach to automation as a continuous practice rather than a one-time project?

---

ᚢ **Lecture 2: Python Fundamentals for Operations**

**Course:** IT105 — Programming for IT (Python, Bash, PowerShell)  
**Degree:** Bachelor of Science in Information Technology, University of Yggdrasil, 2040

---

### Overview

Python is the most important programming language for IT professionals in 2040. This lecture covers the Python fundamentals that every operator needs: data types, control flow, functions, file I/O, and the standard library modules most relevant to operations (`os`, `sys`, `pathlib`, `subprocess`, `json`, `csv`, `re`, `datetime`, `argparse`). The emphasis is not on software engineering (classes, inheritance, design patterns) but on practical scripting: reading data, processing it, and producing output.

### Key Topics

- **Python Syntax and Data Structures:** Variables, types (int, float, str, bool, None), collections (list, tuple, dict, set), and comprehensions (list comprehensions as the Pythonic replacement for filter-map). The lecture covers: truthiness (empty collections are falsy), string formatting (f-strings as the modern standard, with alignment, padding, and number formatting), and the `collections` module (`Counter`, `defaultdict`, `deque` for operational tasks).
- **Control Flow and Functions:** `if/elif/else`, `for` and `while` loops (with `break`, `continue`, `else` clauses), `try/except/finally` error handling, and function definition (positional and keyword arguments, default values, `*args` and `**kwargs`). The lecture emphasises: explicit error handling over silent failures ("errors should never pass silently" — The Zen of Python), and the use of `raise` with meaningful messages.
- **File I/O and Path Manipulation:** Reading and writing text and binary files (context managers with `with open(...)`), `pathlib.Path` as the modern replacement for `os.path` (path joining, globbing, iterating directories, checking existence and permissions), and temporary files (`tempfile` module). The hands-on lab: write a script that recursively finds all `.log` files in `/var/log`, counts lines in each, and produces a summary sorted by size.
- **The Standard Library for Operations:** `os` (environment variables, process ID, system calls), `sys` (command-line arguments, stdout/stderr, exit codes), `subprocess` (running external commands safely — the lecture warns against `os.system` and `shell=True` due to injection risks), `json` (parsing API responses), `csv` (reading spreadsheets), `re` (regular expressions for log parsing), `datetime` (timestamp manipulation, timezone handling with `zoneinfo`), and `argparse` (building CLI tools). The lecture includes a "standard library scavenger hunt": given a task, identify the correct module without importing external libraries.
- **The 2040 Python Ecosystem:** Type hints (`typing` module, `mypy` for static analysis), `pydantic` for data validation, `rich` for beautiful terminal output, `httpx` for modern HTTP client (async-capable, HTTP/2 support), and `typer` / `click` for CLI frameworks. The lecture covers: when to use external libraries (complex tasks, tested solutions) versus standard library (portability, no dependency management).

### Lecture Notes

Python's dominance in IT automation is not accidental. It is readable enough that a team member can understand a script written six months ago by a colleague who has since left. It has libraries for virtually every system and API. It runs on every platform. And it is interactive: the REPL (Read-Eval-Print Loop) allows experimentation, gradual script development, and immediate feedback. The IT professional who cannot drop into a Python REPL to test an API call or parse a JSON response is handicapped.

The `pathlib` module, introduced in Python 3.4 and mature by 2040, has largely replaced `os.path`. Instead of `os.path.join('/var', 'log', 'nginx')`, you write `Path('/var/log/nginx')`. Instead of `os.path.exists(path)`, you write `path.exists()`. Instead of `glob.glob('/var/log/*.log')`, you write `Path('/var/log').glob('*.log')`. The object-oriented approach is more readable, more composable, and less error-prone. The lecture includes a side-by-side comparison: the same file-finding task in `os.path` style (8 lines, hard to read) versus `pathlib` style (3 lines, explicit and chainable).

Error handling in operational scripts is critical. A script that fails silently is worse than no script at all, because it creates false confidence. The lecture teaches defensive scripting: validate inputs before processing, check return codes from subprocess calls, handle expected exceptions (file not found, network timeout, permission denied), and let unexpected exceptions propagate with full tracebacks (so they can be diagnosed). The `logging` module replaces `print()` for operational scripts: structured logs with timestamps, severity levels, and context are essential for debugging in production.

The `subprocess` module is the correct way to run external commands from Python. The lecture warns strongly against `os.system()` (deprecated, insecure, no output capture) and against `subprocess.call(..., shell=True)` (shell injection vulnerability if user input is passed). The correct pattern is `subprocess.run(['cmd', 'arg1', 'arg2'], capture_output=True, text=True, check=True)`, which: runs the command without a shell (safe from injection), captures stdout/stderr, decodes as text, and raises `CalledProcessError` if the command fails. The lecture includes a horror story: a 2032 cloud provider's automation script used `os.system(f"rm -rf {user_input}")` and a user named `; rm -rf /` deleted the entire system.

### Required Reading

- Sweigart, A. (2034). *Automate the Boring Stuff with Python*, 3rd Edition. No Starch Press. Chapters 1-6, 10-12.
- Reitz, K. & Schlusser, T. (2031). *The Hitchhiker's Guide to Python*, 2nd Edition. O'Reilly. Chapters 1-3.
- Python Software Foundation. (2040). "Python Standard Library Documentation: os, pathlib, subprocess, json, csv."

### Discussion Questions

1. Compare `os.path` and `pathlib` for a script that must find all configuration files (`*.conf`) in `/etc` and its subdirectories, skipping symbolic links. Write both versions and evaluate readability, safety, and maintainability.
2. A junior engineer writes `os.system(f"ping -c 4 {host}")` where `host` comes from user input. Explain the injection vulnerability and rewrite the code safely using `subprocess.run` with a list argument.
3. The Norse *rímur* (metrical sagas) followed strict formal rules that made them memorable and transmissible across generations. How does Python's emphasis on readability and "one obvious way to do it" parallel the formal constraints that preserve knowledge across time?

---

ᚦ **Lecture 3: Python for Systems Administration**

**Course:** IT105 — Programming for IT (Python, Bash, PowerShell)  
**Degree:** Bachelor of Science in Information Technology, University of Yggdrasil, 2040

---

### Overview

This lecture applies Python to real IT operational tasks: managing users and permissions, querying system state, interacting with APIs, and automating routine maintenance. Students write scripts that solve problems they will encounter in production: "list all processes consuming more than 1GB RAM," "find certificates expiring in the next 30 days," "synchronise user accounts between two systems via their REST APIs." The lecture emphasises the "sysadmin Python" style: pragmatic, robust, and focused on getting the job done.

### Key Topics

- **Process and System Information:** The `psutil` library as the cross-platform tool for process and system monitoring. The lecture covers: CPU (per-core usage, frequency, times), memory (virtual, resident, shared, swap), disk (partitions, usage, I/O counters), network (interfaces, connections, I/O counters), and sensors (temperatures, fans, battery). The hands-on lab: write a "system health" script that collects all these metrics and outputs a JSON report.
- **User and Permission Management:** Reading `/etc/passwd`, `/etc/shadow`, and `/etc/group` (with appropriate warnings about the sensitivity of shadow files). The `pwd` and `grp` modules for looking up user information. The `crypt` module (legacy) and the 2040 replacements (`passlib`, `bcrypt`, `argon2`) for password hashing. The lecture covers: creating users programmatically (with `subprocess` to `useradd` or platform APIs), setting passwords securely, and managing SSH authorized_keys files.
- **Interacting with APIs:** The `httpx` and `requests` libraries for HTTP operations. The lecture covers: GET, POST, PUT, DELETE, headers, query parameters, JSON payloads, authentication (Bearer tokens, API keys, basic auth), error handling (status codes, retries with `tenacity`, timeout management), and pagination (handling API responses that span multiple pages). The hands-on lab: query the GitHub API to list all repositories for an organisation, handling pagination and rate limits.
- **SSH and Remote Execution:** The `paramiko` library for SSHv2 connections, SFTP file transfer, and remote command execution. The lecture covers: host key verification (the security implications of `AutoAddPolicy`), key-based authentication, executing commands remotely and streaming output, and the `fabric` library as a higher-level orchestration tool. The 2040 additions: `asyncssh` for concurrent remote operations and `mitogen` for Ansible-like connection reuse.
- **Scheduled Tasks and Daemons:** The `schedule` library for in-process scheduling, `APScheduler` for more complex requirements, and integration with system cron (`python-crontab` for reading and writing crontabs). The lecture covers: when to use Python scheduling (complex logic, dynamic intervals) versus cron (simple, system-level, robust), and the 2040 best practice of containerising scheduled tasks as Kubernetes CronJobs.

### Lecture Notes

`psutil` is the Swiss Army knife of system monitoring in Python. It abstracts platform differences (Linux, Windows, macOS, FreeBSD) behind a consistent API. A script that reports CPU usage works identically on all platforms, which is invaluable in heterogeneous environments. The lecture includes a "system dashboard" script that uses `psutil` to collect metrics and `rich` to display a live-updating table of CPU, memory, disk, and network usage — a practical tool that students can deploy on their own servers.

API interaction is the dominant mode of systems integration in 2040. Whether provisioning cloud resources, updating DNS records, querying monitoring systems, or managing identity providers, the IT professional spends significant time writing HTTP clients. The lecture emphasises: always handle timeouts (an unresponsive API should not hang your script indefinitely), always retry transient failures (status 429, 502, 503, 504 with exponential backoff), and always validate responses (a 200 OK with malformed JSON is still a failure). The `httpx` library is preferred over `requests` in 2040 because it supports both sync and async APIs, HTTP/2, and connection pooling natively.

Remote execution via SSH is both powerful and dangerous. `paramiko` enables Python scripts to log into remote servers and execute commands, but this creates a security boundary: the script holds credentials, and a compromise of the script machine compromises all target machines. The lecture covers: using SSH agent forwarding rather than storing keys, restricting remote commands via `authorized_keys` command restrictions, and the principle that "if you are SSHing to more than three machines from a script, you should be using a configuration management tool (Ansible, Salt, Puppet) instead."

### Required Reading

- Sweigart, A. (2034). *Automate the Boring Stuff with Python*, 3rd Edition. Chapters 7-8, 12, 16.
- Reitz, K. & Schlusser, T. (2031). *The Hitchhiker's Guide to Python*, 2nd Edition. Chapters 4-5.
- GitHub API Documentation (2040). "REST API v3: Authentication, Pagination, Rate Limits."

### Discussion Questions

1. Design a Python script that monitors disk usage on 50 servers and sends an alert (via email or Slack webhook) when any disk exceeds 90% full. The script must handle SSH authentication securely, timeout gracefully on unreachable hosts, and produce a summary report. Outline your design and identify the key libraries.
2. A REST API returns paginated results with a `Link` header (RFC 5988). Write a Python generator that yields all items across all pages, handling rate limits (429 status with `Retry-After` header) and network timeouts.
3. The Norse *goði* mediated between local communities and the broader legal system, travelling between settlements to resolve disputes. How does this mediating, connecting role parallel the function of API integration scripts that bridge disparate systems?

---

ᚨ **Lecture 4: Text Processing and Data Transformation**

**Course:** IT105 — Programming for IT (Python, Bash, PowerShell)  
**Degree:** Bachelor of Science in Information Technology, University of Yggdrasil, 2040

---

### Overview

IT professionals spend an extraordinary amount of time processing text: log files, configuration files, CSV exports, JSON payloads, and command output. This lecture covers the tools and techniques for transforming unstructured or semi-structured text into structured, actionable information. Topics include regular expressions, log parsing strategies, data format conversions (CSV, JSON, YAML, XML), and the Python libraries that make text processing efficient and robust (`re`, `csv`, `json`, `pyyaml`, `xml.etree`, `pandas` for larger datasets).

### Key Topics

- **Regular Expressions:** The domain-specific language for pattern matching. The lecture covers: literal characters, character classes (`\d`, `\w`, `\s`, negated classes), quantifiers (`*`, `+`, `?`, `{m,n}`), anchors (`^`, `$`, ``), groups and capturing (`(...)`), non-capturing groups (`(?:...)`), backreferences, and lookahead/lookbehind. The practical focus is on log parsing: extracting IP addresses, timestamps, HTTP status codes, and error messages from web server logs. The hands-on lab: write a regex that parses a standard Apache combined log format line into its components.
- **Log Parsing Strategies:** The three approaches: simple regex (fast, brittle), structured parsing (parsing known formats with dedicated libraries), and heuristic parsing (guessing formats and extracting key-value pairs). The lecture covers: the `logging` module's format parsing, syslog format variations, JSON Lines (one JSON object per line, the 2040 standard for structured logging), and the ELK/PLG stack's ingestion pipelines. The 2040 reality: most modern applications emit structured logs (JSON) that require no regex parsing; legacy applications emit text that still requires the skills taught in this lecture.
- **Data Format Conversions:** CSV (the `csv` module: `DictReader` and `DictWriter` for header-aware processing, handling dialects and quoting), JSON (the `json` module: `load`, `loads`, `dump`, `dumps`, custom encoders for datetime and Decimal), YAML (the `PyYAML` library: safe loading with `safe_load` to prevent code execution, the 2040 security requirement), and XML (the `xml.etree.ElementTree` module for simple parsing, `lxml` for complex schemas). The hands-on lab: convert a CSV export of user data into JSON, validating that all required fields are present and email addresses match a regex pattern.
- **Working with Larger Datasets:** When text data exceeds available RAM (common with multi-gigabyte log files), the lecture covers: streaming processing (reading one line at a time rather than loading the entire file), generator expressions (memory-efficient pipelines), chunking (processing fixed-size blocks), and the `pandas` library for out-of-core analytics. The 2040 additions: `polars` (a faster DataFrame library written in Rust) and `duckdb` (an in-process analytical database that can query CSV and JSON directly with SQL).
- **Data Cleaning and Validation:** Real data is messy. The lecture covers: handling missing values (empty strings, `None`, `"N/A"`), normalising text (case folding, whitespace stripping, Unicode normalisation with `unicodedata`), detecting anomalies (outliers, impossible dates, invalid identifiers), and the `pydantic` library for declarative data validation (define a schema, validate incoming data, get clear error messages). The hands-on lab: clean a "dirty" dataset of server inventory with inconsistent date formats, mixed case hostnames, and missing serial numbers.

### Lecture Notes

Regular expressions are simultaneously indispensable and dangerous. They are indispensable because they can extract structure from unstructured text in a single line of code. They are dangerous because they are write-only: a regex written today is incomprehensible tomorrow, and subtle errors (greedy versus lazy quantifiers, unanchored matches, catastrophic backtracking) cause bugs that are difficult to diagnose. The lecture teaches the "readable regex" style: use verbose mode (`re.VERBOSE`) to add whitespace and comments, break complex patterns into named groups (`(?P<ip>\d{1,3}(?:\.\d{1,3}){3})`), and always test with a comprehensive suite of inputs including edge cases.

Catastrophic backtracking is the regex performance killer. A pattern like `(a+)+` on a long string of 'a's followed by a non-matching character causes exponential execution time. In 2037, a popular log analysis tool caused a production outage because a regex with nested quantifiers took 30 minutes to process a 100MB log file. The lesson: always test regex performance on large inputs, use possessive quantifiers (`++`, `*+`) where possible, and consider parser combinators or dedicated parsers for complex grammars instead of regex.

Structured logging (JSON Lines) has largely replaced plain text logging in 2040, but the IT professional still encounters legacy systems that emit unstructured text. The ability to write a regex, test it, and deploy it in a log shipping pipeline is a fundamental skill. The lecture includes a "regex debugging" session where students use `regex101.com` (or its 2040 successor) to step through pattern matching and understand why a particular string matches or fails.

Data validation with `pydantic` is a game-changer for operational scripts. Instead of manually checking `if 'email' in data and '@' in data['email']`, you define a model:
```python
from pydantic import BaseModel, EmailStr
class User(BaseModel):
    name: str
    email: EmailStr
    role: str = "student"
```
And `User(**data)` either returns a valid object or raises a detailed validation error. This pattern is used throughout the Yggdrasil automation codebase for API request validation, configuration parsing, and inventory management.

### Required Reading

- Friedl, J.E.F. (2033). *Mastering Regular Expressions*, 4th Edition. O'Reilly. Chapters 1-3, 6.
- Sweigart, A. (2034). *Automate the Boring Stuff with Python*, 3rd Edition. Chapters 12-13, 16.
- pydantic Documentation (2040). "Models, Validation, and Settings Management."

### Discussion Questions

1. A log file contains 10 million lines in an unknown custom format. Design a systematic approach to parsing it: how would you determine the format, prototype the parser, validate correctness, and optimise performance for production use?
2. Compare regex-based parsing with structured logging (JSON Lines) for operational data. What are the maintainability, performance, and reliability trade-offs? Under what conditions would you advocate migrating a legacy text-logging system to structured logging?
3. The Norse *rúnar* (runes) were a structured symbol system encoding both phonetic and magical information. How does the dual nature of runes — as practical writing and as structured data — parallel the evolution of log formats from human-readable text to machine-structured JSON?

---

ᚱ **Lecture 5: Bash and the Unix Shell — The Native Tongue of Linux**

**Course:** IT105 — Programming for IT (Python, Bash, PowerShell)  
**Degree:** Bachelor of Science in Information Technology, University of Yggdrasil, 2040

---

### Overview

Bash is the default shell on most Linux systems and the lingua franca of server administration. This lecture covers Bash fundamentals: variables, control structures, functions, and the composition of small tools into powerful pipelines. The emphasis is on the Unix philosophy (each tool does one thing well; tools are composed via pipes) and the practical skills that enable efficient system interaction: history expansion, job control, and environment configuration.

### Key Topics

- **Shell Fundamentals:** The command-line interface as a programming environment. Variables (local and exported), quoting (single vs. double quotes, the critical difference in expansion), special variables (`$?` for exit status, `$$` for PID, `$#`, `$*`, `$@` for arguments), and arithmetic (`$(( ))`). The lecture covers: the difference between shell builtins (`cd`, `echo`, `read`), external commands (`ls`, `grep`, `cat`), and functions; and why this distinction matters for performance and portability.
- **Pipes, Redirection, and Process Substitution:** The `|` pipe (connecting stdout of one command to stdin of another), redirection (`>`, `>>`, `<`, `2>`, `&>`, heredocs `<<EOF`), and process substitution (`<( )` and `>( )` — treating command output as a file). The lecture includes a "one-liner of the day" series: complex tasks accomplished by composing simple tools. Example: `find /var/log -name "*.log" -mtime +7 | xargs gzip` finds and compresses old logs.
- **Text Processing Tools:** `grep` (pattern matching with `-E` extended regex, `-v` inversion, `-c` count, `-o` only matching), `sed` (stream editing: substitution, deletion, address ranges), `awk` (field-oriented text processing, the underappreciated power tool), `cut` (column extraction), `sort` and `uniq` (with `-c` for counting duplicates), `tr` (character translation), `wc` (line/word/byte counts), and `head`/`tail` (with `-f` for following live logs). The hands-on lab: parse a web server access log to find the top 10 IP addresses by request count, using only these tools.
- **Control Structures and Scripting:** `if/then/elif/else/fi`, `for/in/do/done`, `while/do/done`, `case/esac`, and functions. The lecture covers: `set -euo pipefail` (the "strict mode" that makes scripts fail fast on errors, undefined variables, and pipeline failures), `trap` for signal handling and cleanup, and temporary file management (`mktemp`). The hands-on lab: write a robust backup script that checks preconditions, creates a timestamped archive, verifies the archive, and logs all actions.
- **Environment and Configuration:** Shell startup files (`.bashrc`, `.bash_profile`, `.profile`, `/etc/profile`, `/etc/bash.bashrc` — the loading order and when each applies), environment variables (`PATH`, `LANG`, `EDITOR`, `PS1` for the prompt), and aliases (when appropriate and when harmful). The lecture covers: the 2040 trend toward `direnv` (directory-specific environment variables) and `starship` (cross-shell prompt configuration), and the dangers of over-customising production shells.

### Lecture Notes

Bash is simultaneously simple and treacherous. Simple because any command you can type interactively can be placed in a script. Treacherous because the quoting rules are subtle, word splitting is automatic and often surprising, and error handling is opt-in rather than default. The lecture teaches defensive Bash: always use `set -euo pipefail` at the top of every script, always quote variables (`"$var"` not `$var`), always check exit codes, and never parse `ls` output.

The `set -euo pipefail` incantation is worth memorising: `-e` exits immediately if any command fails (non-zero exit status); `-u` treats unset variables as errors; `-o pipefail` causes a pipeline to fail if any command in it fails, not just the last one. Together, these options transform Bash from a language that silently continues past errors into one that fails fast and visibly. The lecture includes a demonstration: with `set -euo pipefail`, the script `rm -rf "$UNSET_VAR/"` fails immediately with an error; without it, the script expands to `rm -rf /` and deletes the entire filesystem.

Pipes are the compositional glue of the Unix philosophy. A command that outputs one record per line can be piped to `sort`, `uniq`, `grep`, `awk`, or any other line-oriented tool. This enables ad-hoc analysis: `awk '{print $1}' access.log | sort | uniq -c | sort -rn | head` extracts IP addresses, counts occurrences, and shows the top 10 — a complete log analysis in a single line. The lecture emphasises that this is not a gimmick but a design pattern: small, focused tools with line-oriented text interfaces compose into solutions more flexibly than monolithic applications.

`awk` is the most underappreciated tool in the sysadmin's kit. It is a full programming language (variables, conditionals, loops, functions, associative arrays) specialised for field-oriented text processing. An `awk` one-liner can replace 50 lines of Python for tasks like: summing a column, filtering records based on multiple conditions, reformatting tabular data, or building frequency tables. The lecture includes an `awk` tutorial: start with `{print $1}` (print the first field), progress to `$3 > 100 {sum += $3} END {print sum}` (sum the third field for records where it exceeds 100), and culminate in a script that generates a summary report from a CSV file.

### Required Reading

- Blum, R. & Bresnahan, C. (2033). *Linux Command Line and Shell Scripting Bible*, 6th Edition. Wiley. Chapters 1-5, 11-13, 19-20.
- Robbins, A. (2032). *Effective awk Programming*, 5th Edition. O'Reilly. Chapters 1-3, 7.
- Google Shell Style Guide (2040). "Best Practices for Bash in Production."

### Discussion Questions

1. A junior sysadmin writes: `for f in $(ls *.txt); do cat $f; done`. Identify at least three bugs or bad practices in this script and rewrite it robustly.
2. Explain the difference between `grep`, `sed`, and `awk` in terms of their primary use cases and processing models. For each, give an example of a task where it is the most appropriate tool and one where it is inappropriate.
3. The Norse *flokkr* (warband) was composed of individuals with specific roles (skirmishers, shield-bearers, archers) who combined into a coordinated force. How does this composition of specialised roles parallel the Unix pipeline philosophy of combining single-purpose tools?

---

ᚲ **Lecture 6: Advanced Bash — Orchestration, Error Handling, and Maintainability**

**Course:** IT105 — Programming for IT (Python, Bash, PowerShell)  
**Degree:** Bachelor of Science in Information Technology, University of Yggdrasil, 2040

---

### Overview

Beyond one-liners, Bash scripts can orchestrate complex workflows: deploying applications, running backups, provisioning infrastructure, and managing multi-step pipelines. This lecture covers advanced Bash scripting: arrays, associative arrays (dictionaries), string manipulation, error handling patterns, logging, parallelism, and testing. The emphasis is on writing Bash scripts that are robust enough for production — not merely "works on my machine" convenience scripts.

### Key Topics

- **Arrays and Associative Arrays:** Indexed arrays (`arr=(a b c)`, `${arr[0]}`, `${#arr[@]}` for length, `${arr[@]}` for all elements) and associative arrays (`declare -A dict`, `dict[key]=value`, `${dict[$key]}`). The lecture covers: iterating over arrays safely (`for item in "${arr[@]}"; do`), and the critical difference between `"$*"` (single string) and `"$@"` (array of strings) when passing arguments.
- **String Manipulation:** Bash's built-in string operations: substring extraction (`${var:offset:length}`), pattern removal (`${var#prefix}`, `${var%suffix}`), replacement (`${var/old/new}`), and length (`${#var}`). The lecture covers: when to use Bash string manipulation (simple cases, no external process) versus `sed` or `awk` (complex cases), and the performance implications.
- **Error Handling Patterns:** Beyond `set -e`: explicit error checking (`if ! cmd; then ...; fi`), custom error functions, `trap` for cleanup (removing temporary files, restoring state on script exit, handling `SIGINT` and `SIGTERM`), and the `ERR` trap for running code on any command failure. The lecture covers: idempotency (running the script twice should not cause errors), and the "main" function pattern that localises script logic.
- **Logging and Observability:** Writing scripts that produce structured, timestamped, severity-annotated logs. The lecture covers: `logger` (sending messages to syslog), `ts` (timestamping from `moreutils`), and the custom `log()` function pattern:
```bash
log() { local level=$1; shift; echo "$(date '+%Y-%m-%d %H:%M:%S') [$level] $*" >&2; }
```
The 2040 best practice: scripts should log to stderr by default, allowing stdout to be piped to other tools while logs are captured separately.
- **Parallelism and Job Control:** Background processes (`cmd &`), the `wait` builtin, `xargs -P` (parallel execution with xargs), and GNU `parallel` (more sophisticated parallel execution with load balancing). The lecture covers: process substitution for parallel output collection, `flock` for file-based locking (preventing concurrent script runs), and the dangers of uncontrolled parallelism (resource exhaustion, race conditions). The hands-on lab: write a script that backs up 100 directories in parallel, limiting concurrency to 8 jobs to avoid overwhelming the backup server.
- **Testing Bash Scripts:** The `bats` (Bash Automated Testing System) framework for unit-testing Bash scripts. The lecture covers: writing test cases, mocking commands (replacing real commands with test doubles), and CI integration. The 2040 reality: while many Bash scripts are untested, critical infrastructure scripts (deployment, backup, provisioning) must have test coverage.

### Lecture Notes

Bash scripts that grow beyond 50 lines become maintenance liabilities. The language lacks modules, classes, static typing, and comprehensive standard libraries. Every line of Bash is a line that can silently fail, misinterpret a variable, or behave differently on macOS versus Linux. The lecture teaches strategies for keeping Bash scripts manageable: break long scripts into functions, use `local` variables, add comments explaining intent (not mechanics), and — most importantly — consider whether the task has outgrown Bash and should be rewritten in Python or Go.

The associative array (`declare -A`) is Bash 4+ feature that enables dictionary-like data structures. This is invaluable for configuration management: `declare -A config=([host]="db1" [port]="5432" [user]="admin")`, then `${config[host]}` retrieves the value. The lecture includes a "configuration parser" script that reads key-value pairs from a file into an associative array, validates required keys, and applies defaults — a pattern used in many Yggdrasil operational scripts.

`trap` is the mechanism for ensuring cleanup regardless of how a script exits. A typical pattern:
```bash
tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT
```
This guarantees that the temporary directory is removed when the script exits normally, via `exit`, via `errexit` (`set -e`), or via `Ctrl+C` (`SIGINT`). Without `trap`, temporary files accumulate, consuming disk space and potentially exposing sensitive data. The lecture includes a case study: a backup script that created temporary archives in `/tmp` but did not clean them up; over six months, `/tmp` grew to 400GB, causing application failures.

Parallelism in Bash is deceptively simple. Running `cmd &` eight times and then `wait` launches eight background jobs. But what if one fails? `wait` returns the exit status of the last job waited for, not all jobs. The lecture teaches the "parallel with exit code collection" pattern using file descriptors or the `wait -n` loop. For production use, GNU `parallel` is preferred: it handles load balancing, rate limiting, output ordering, and progress reporting. The command `parallel -j 8 backup_dir ::: */` backs up all directories with 8 concurrent jobs, producing output in the order of completion.

### Required Reading

- Blum, R. & Bresnahan, C. (2033). *Linux Command Line and Shell Scripting Bible*, 6th Edition. Wiley. Chapters 14-18, 23.
- Cooper, M. (2031). *Advanced Bash-Scripting Guide*, 12th Edition. The Linux Documentation Project. Chapters 5, 15, 27.
- GNU Parallel Documentation (2040). "Tutorial, Examples, and Best Practices."

### Discussion Questions

1. A deployment script has grown to 300 lines of Bash with nested conditionals, temporary files, and remote SSH commands. Describe the symptoms that indicate this script has outgrown Bash, and propose a migration strategy to Python or Go that preserves existing functionality.
2. Design a Bash script that must run as a singleton (only one instance at a time) across multiple servers. Describe three locking mechanisms and their failure modes: file locks (`flock`), directory creation (`mkdir`), and network-based locks (Redis, Consul).
3. The Norse *lögrétta* (law-speaker's court) required formal procedures that were followed precisely regardless of circumstances. How does this formal rigour parallel the need for strict error handling and cleanup in production Bash scripts?

---

ᚷ **Lecture 7: PowerShell Fundamentals — Objects, Pipelines, and Discovery**

**Course:** IT105 — Programming for IT (Python, Bash, PowerShell)  
**Degree:** Bachelor of Science in Information Technology, University of Yggdrasil, 2040

---

### Overview

PowerShell is not "Bash for Windows." It is a fundamentally different paradigm: an object-oriented shell where the pipeline passes structured objects rather than text streams. This lecture covers PowerShell fundamentals: cmdlets, the object pipeline, providers, discovery commands (`Get-Command`, `Get-Help`, `Get-Member`), variables and types, control flow, and functions. Students learn to "think in objects" and leverage PowerShell's unique strengths for Windows administration and cross-platform automation.

### Key Topics

- **Cmdlets and Verb-Noun Naming:** PowerShell commands follow a strict `Verb-Noun` convention (`Get-Process`, `Set-Location`, `Invoke-RestMethod`). The lecture covers: the approved verb list (Get, Set, New, Remove, Start, Stop, Invoke, Out, Write, Read), the benefit of discoverability (you can guess command names), and aliases (convenient but discouraged in scripts for readability). The hands-on lab: use `Get-Command` and `Get-Help` to discover and learn about commands for managing Windows services.
- **The Object Pipeline:** Unlike Bash, where `ls | grep foo` filters text lines, PowerShell's `Get-Process | Where-Object {$_.Name -like "*foo*"}` filters objects by property. The lecture covers: `Where-Object` (filtering), `Select-Object` (choosing properties), `Sort-Object` (sorting by property), `Group-Object` (grouping), `Measure-Object` (aggregating: count, sum, average, min, max), and `ForEach-Object` (iterating and transforming). The power of object pipelines: you can filter, sort, group, and format data without fragile text parsing.
- **Providers and Drives:** PowerShell providers expose data stores as drives. The lecture covers: the FileSystem provider (`C:`, `/` on Linux), the Registry provider (`HKLM:`, `HKCU:`), the Certificate provider (`Cert:`), the Environment provider (`Env:`), and the Variable provider (`Variable:`). You can navigate and manipulate these stores using the same commands (`Get-ChildItem`, `Set-Location`, `Remove-Item`) regardless of the underlying store. The hands-on lab: use `Get-ChildItem` to list registry keys, environment variables, and certificates.
- **Variables, Types, and Operators:** PowerShell variables (`$var`) are loosely typed but can be strongly typed (`[int]$count = 0`). The lecture covers: arrays (`@()`) and hash tables (`@{}`), splatting (passing parameters as a hashtable), the range operator (`1..10`), and comparison operators (`-eq`, `-ne`, `-gt`, `-lt`, `-like`, `-match`, `-contains` — the source of many bugs for newcomers accustomed to `=`, `!=`, `>`). The 2040 additions: class definitions (PowerShell 5+), enums, and the `using` statement for namespace imports.
- **Control Flow and Functions:** `if/elseif/else`, `switch` (with wildcard, regex, and file matching modes), `for`, `foreach`, `while`, `do/while`, `break`, `continue`, and `return`. Functions: parameters (`param()` block), mandatory parameters, parameter validation (`[ValidateNotNullOrEmpty()]`, `[ValidateRange(1,100)]`), pipeline input (`ValueFromPipeline`), and comment-based help. The lecture emphasises: functions should be small, testable, and documented; scripts should use `CmdletBinding()` for advanced function features (verbose output, debug stepping, parameter validation).

### Lecture Notes

PowerShell's object pipeline is its defining feature and its steepest learning curve for Linux administrators accustomed to text. The key insight is that text is lossy: when you pipe `ls -l` to `awk '{print $5}'`, you are extracting the fifth whitespace-separated field, hoping it is the file size. If the output format changes (e.g., a filename with spaces), the extraction breaks. In PowerShell, `Get-ChildItem | Select-Object -Property Length` extracts the `Length` property by name; it will never break due to formatting changes because the property is typed and named.

The `Get-Member` cmdlet is the sysadmin's microscope for PowerShell objects. Piping any object to `Get-Member` reveals its type, properties, methods, and events. This is essential because cmdlets produce objects with dozens of properties, only some of which are displayed by default. `Get-Process | Get-Member` shows that process objects have properties like `Id`, `Name`, `CPU`, `WorkingSet`, `PagedMemorySize`, `Threads`, and methods like `Kill()`, `Refresh()`, `WaitForExit()`. Without `Get-Member`, you are guessing at available properties.

Splatting is a PowerShell technique that improves readability and enables dynamic parameter construction. Instead of:
```powershell
Get-WinEvent -LogName Security -MaxEvents 10 -FilterXPath "*[System[(EventID=4624)]]"
```
You write:
```powershell
$params = @{LogName="Security"; MaxEvents=10; FilterXPath="*[System[(EventID=4624)]]"}
Get-WinEvent @params
```
This is more readable, allows conditional parameter inclusion, and enables parameter reuse across multiple calls. The lecture includes a "dynamic parameter builder" pattern where parameters are constructed based on runtime conditions.

Comment-based help transforms a function into a self-documenting command. By adding a `<# .SYNOPSIS ... .DESCRIPTION ... .PARAMETER ... .EXAMPLE ... #>` block before the function, you enable `Get-Help` to display formatted help. This is not merely documentation; it is discoverable documentation that integrates with PowerShell's help system and IDE IntelliSense. The Yggdrasil PowerShell coding standard mandates comment-based help for all functions longer than 10 lines.

### Required Reading

- Jones, R. & Hicks, J. (2034). *PowerShell in Action*, 4th Edition. Manning. Chapters 1-3, 5-6.
- Wilson, E. (2032). *Windows PowerShell Step by Step*, 5th Edition. Microsoft Press. Chapters 1-4.
- Microsoft Learn. (2040). "PowerShell 101: Introduction to PowerShell."

### Discussion Questions

1. A Linux administrator argues that PowerShell's object pipeline is unnecessary complexity and that text-based pipelines are simpler. Counter this argument with specific examples where object pipelines prevent bugs that text pipelines would introduce.
2. Design a PowerShell function `Get-DiskHealthReport` that queries disk space, SMART status, and I/O statistics from multiple servers. The function should accept pipeline input for server names, support `-WhatIf` and `-Verbose`, and produce objects with properties for each metric. Include comment-based help.
3. The Norse *bragarfull* (chieftain's toast) followed a strict ritual form: who could speak, what could be vowed, the order of cups. How does this structured, typed ritual parallel PowerShell's typed objects and formal cmdlet naming conventions?

---

ᚹ **Lecture 8: PowerShell for Automation — Remoting, DSC, and Modules**

**Course:** IT105 — Programming for IT (Python, Bash, PowerShell)  
**Degree:** Bachelor of Science in Information Technology, University of Yggdrasil, 2040

---

### Overview

PowerShell's real power lies in its automation capabilities: managing remote systems, enforcing desired state, and packaging reusable code in modules. This lecture covers PowerShell Remoting (WinRM, SSH transport, JEA), Desired State Configuration (DSC), module development, and the 2040 cross-platform ecosystem. Students write a DSC configuration that enforces a standard web server setup and deploy it to a remote node.

### Key Topics

- **PowerShell Remoting:** The `Invoke-Command` cmdlet for executing commands on remote systems via WinRM (Windows Remote Management, based on WS-MAN) or SSH. The lecture covers: enabling remoting (`Enable-PSRemoting`), trusted hosts, credential management (`Get-Credential`, certificate-based authentication), and session reuse (`New-PSSession`, `Invoke-Command -Session`, `Enter-PSSession` for interactive remoting). The 2040 reality: SSH transport is now preferred over WinRM for cross-platform remoting, and PowerShell 7+ supports SSH natively.
- **Just Enough Administration (JEA):** The principle of least privilege applied to PowerShell remoting. JEA endpoints are constrained sessions where users can only run specific commands with specific parameters. The lecture covers: session configurations (`New-PSSessionConfigurationFile`), role definitions (`VisibleCmdlets`, `VisibleFunctions`), and the security benefits (an operator who needs to restart IIS should not have full admin rights). The hands-on lab: create a JEA endpoint that allows helpdesk staff to restart services and view event logs but nothing else.
- **Desired State Configuration (DSC):** Declarative configuration management for Windows (and, via DSC v3, Linux). The lecture covers: configuration documents (MOF files), resources (built-in: File, Registry, Service, Package, Script; community: from the PowerShell Gallery), local configuration manager (LCM, the engine that applies configurations), and pull mode (configurations hosted on a pull server, nodes check in periodically). The 2040 evolution: Azure Automanage, Azure Policy Guest Configuration, and the open-source `dsc` command-line tool that works cross-platform.
- **Modules and the PowerShell Gallery:** Packaging functions, cmdlets, providers, and DSC resources into reusable modules. The lecture covers: module structure (`.psd1` manifest, `.psm1` root module, nested modules), versioning (semantic versioning), publishing to the PowerShell Gallery (and private galleries like the Yggdrasil Internal Gallery), and dependency management (`RequiredModules` in the manifest). The hands-on lab: create a module containing three functions for certificate management, write Pester tests, and publish it to a local repository.
- **Cross-Platform PowerShell:** PowerShell 7+ runs on Linux and macOS, using .NET Core. The lecture covers: platform detection (`$IsLinux`, `$IsWindows`, `$IsMacOS`), path handling (`Join-Path` for cross-platform paths), and the limitations (some Windows-specific modules are not available on Linux). The 2040 reality: many organisations run PowerShell Core as their primary automation language across all platforms, using it as a consistent alternative to the Bash/Python split.

### Lecture Notes

PowerShell Remoting is the Windows equivalent of SSH, but with deeper integration into the operating system. Where SSH gives you a shell on a remote system, PowerShell remoting gives you the ability to execute commands on 1,000 systems simultaneously with a single `Invoke-Command` call. The `-ThrottleLimit` parameter controls concurrency; the `-AsJob` parameter runs commands in the background; and the `-FilePath` parameter executes an entire script on remote systems. This is the foundation of Windows fleet management at scale.

JEA is one of the most important security features in Windows administration. Without JEA, giving a junior admin remote access means giving them full administrative rights (or creating complex local accounts with restricted permissions). With JEA, you create a constrained endpoint that exposes only the commands the admin needs, with only the parameters they are allowed to use, running under a privileged virtual account that they never directly possess. If the junior admin's credentials are compromised, the attacker gains only the limited capability of the JEA endpoint — not full system access.

DSC represents the "infrastructure as code" philosophy for Windows. Instead of manually configuring a server (install IIS, set bindings, enable authentication, deploy content), you write a DSC configuration that describes the desired state. The LCM applies this state, correcting drift automatically. DSC can operate in push mode (admin pushes configuration to nodes) or pull mode (nodes check a central server for their configuration). The 2040 best practice is pull mode with Azure Policy Guest Configuration, which provides centralised reporting and compliance auditing.

Cross-platform PowerShell in 2040 is a mature reality. PowerShell 7.x runs on Linux, macOS, and Windows, and the module ecosystem has adapted. The `PSReadLine` module provides Bash-like line editing, the `z` module provides directory jumping, and the `oh-my-posh` theme engine provides beautiful prompts. For Linux administrators, the decision is no longer "Bash or PowerShell?" but "Which is more appropriate for this specific task?" The Yggdrasil standard: use Bash for quick system tasks on Linux; use PowerShell for cross-platform automation, Windows management, and API interaction.

### Required Reading

- Jones, R. & Hicks, J. (2034). *PowerShell in Action*, 4th Edition. Manning. Chapters 10-11, 13.
- Microsoft. (2039). *Desired State Configuration v3 — The Cross-Platform Guide*.
- Yggdrasil Windows Operations Team. (2040). "JEA Implementation and Best Practices."

### Discussion Questions

1. Compare SSH-based remote management (running commands via SSH keys) with PowerShell Remoting (WinRM/SSH with JEA) for a Windows server fleet of 500 machines. Evaluate security, auditability, performance, and operational complexity.
2. A DSC configuration drifted from the desired state because an administrator manually changed a setting. The LCM detected the drift and corrected it, but the application failed during the 2-minute correction window. How do you balance the benefits of automated drift correction against the risks of unexpected reconfiguration?
3. The Norse *heimþingi* (home assembly) gathered the household to settle domestic matters without waiting for the district *thing*. How does this distributed, household-level governance parallel the concept of local configuration management (DSC LCM) operating autonomously while coordinating with central policy?

---

ᚺ **Lecture 9: APIs and Web Services — The Glue of Modern Infrastructure**

**Course:** IT105 — Programming for IT (Python, Bash, PowerShell)  
**Degree:** Bachelor of Science in Information Technology, University of Yggdrasil, 2040

---

### Overview

Application Programming Interfaces (APIs) are the primary mechanism by which IT systems communicate in 2040. This lecture covers RESTful API design principles, HTTP fundamentals, authentication mechanisms, and practical client programming in Python and PowerShell. Students interact with real APIs: cloud provider APIs, monitoring system APIs, and the Yggdrasil internal API for infrastructure management.

### Key Topics

- **HTTP Fundamentals:** Methods (GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS), status codes (1xx informational, 2xx success, 3xx redirection, 4xx client error, 5xx server error — with emphasis on the most common: 200, 201, 204, 301, 400, 401, 403, 404, 409, 422, 429, 500, 502, 503, 504), headers (Content-Type, Accept, Authorization, User-Agent, Cache-Control, ETag, X-Request-ID), and the request/response cycle. The lecture includes a "status code bingo" game where students map scenarios to the correct status code.
- **RESTful Design Principles:** Resources identified by URIs, standard HTTP methods for CRUD operations, statelessness (each request contains all necessary information; the server does not store client state between requests), and HATEOAS (Hypermedia as the Engine of Application State — though the lecture notes that pure HATEOAS is rare in 2040, with OpenAPI specifications being the dominant contract format). The lecture covers: resource nesting (`/users/123/orders`), query parameters for filtering and pagination (`?limit=10&offset=20`), and the difference between PUT (idempotent replace) and PATCH (partial update).
- **Authentication and Security:** API keys (simple but limited), Basic Auth (username:password Base64-encoded, only over HTTPS), Bearer tokens (JWT access tokens with expiration, the 2040 standard), OAuth 2.0 / OIDC (the authorisation framework for delegated access: authorisation code flow, client credentials flow, PKCE for public clients), and mutual TLS (client certificates for high-security scenarios). The lecture covers: token refresh logic, storing credentials securely (environment variables, secret managers like HashiCorp Vault or Azure Key Vault, never hardcoded), and the principle of least privilege for API keys.
- **Python API Clients:** The `httpx` library (async-capable, HTTP/2, connection pooling) and `requests` (the classic synchronous library). The lecture covers: session objects (persistent cookies and connection reuse), retry strategies (`tenacity` library: exponential backoff, jitter, retry on specific status codes), timeout configuration (connect timeout vs. read timeout), and response validation (`pydantic` models for deserialising JSON responses). The hands-on lab: write a Python client for the Yggdrasil Infrastructure API that lists all VMs, filters by status, and exports to CSV.
- **PowerShell API Clients:** `Invoke-RestMethod` (higher-level, automatically parses JSON/XML) and `Invoke-WebRequest` (lower-level, returns raw response object). The lecture covers: `-Headers` for custom headers, `-Body` for request payloads, `-ContentType` and `-Method`, handling pagination (following `next` links in response headers), and credential management (`Get-Secret` from the `Microsoft.PowerShell.SecretManagement` module). The hands-on lab: replicate the Python VM client in PowerShell.

### Lecture Notes

HTTP is the universal protocol of IT integration. Whether provisioning a VM, updating a DNS record, querying a monitoring system, or sending a Slack notification, the mechanism is an HTTP request. The IT professional who cannot construct an HTTP request, interpret a status code, or debug a failed API call is as limited as a sailor who cannot tie a knot.

Status codes are not suggestions; they are contracts. A 404 means "the resource you requested does not exist" — retrying will not help unless the resource is created. A 429 means "you are rate-limited" — retrying immediately will fail and may increase the rate-limit penalty; you must wait (respecting the `Retry-After` header). A 503 means "the service is temporarily unavailable" — retrying with exponential backoff is appropriate. A 500 means "internal server error" — retrying might work if the error was transient, but persistent 500s indicate a bug. The lecture includes a "status code decision tree" that maps each code to the appropriate client action.

OAuth 2.0, despite its complexity, is the dominant authorisation framework in 2040. The lecture simplifies it to three flows relevant to IT automation: Client Credentials (machine-to-machine: your script authenticates as itself using a client ID and secret), Authorization Code (user-delegated: a user grants your application access to their resources), and Device Code (for input-constrained devices like TVs or IoT sensors). For IT scripts, Client Credentials is the norm: the script runs as a service principal with specific API permissions.

Token management is a common source of operational bugs. Access tokens expire (typically after 1 hour), and scripts must refresh them using a refresh token or by re-authenticating. A script that works for 59 minutes and then fails with 401 is not "intermittently buggy"; it is "correctly implementing an incorrect token refresh strategy." The lecture teaches the "token cache" pattern: acquire a token, use it until near expiry, refresh transparently, and share the cache across concurrent requests. The `msal` library (Microsoft Authentication Library) and `authlib` (general-purpose OAuth) handle this automatically in 2040.

### Required Reading

- Richardson, L. & Amundsen, M. (2034). *RESTful Web APIs*, 2nd Edition. O'Reilly. Chapters 1-3, 7-8.
- IETF RFC 9110 (HTTP Semantics) and RFC 9112 (HTTP/1.1) — selected sections.
- Microsoft Identity Platform Documentation (2040). "OAuth 2.0 and OpenID Connect Protocols."

### Discussion Questions

1. An API returns 500 Internal Server Error for 0.1% of requests. Your script currently retries all 500s with exponential backoff. A colleague argues that 500s should not be retried because they indicate server bugs, not transient failures. Evaluate both positions and design a retry policy that handles different 500 scenarios appropriately.
2. Compare API key authentication with OAuth 2.0 Client Credentials for a script that provisions cloud infrastructure. What are the security, auditability, and operational trade-offs? Under what conditions would you choose each?
3. The Norse *kaupmadr* (merchant) operated across linguistic and cultural boundaries, relying on shared protocols of trade: weights, measures, gestures, and the Thing's legal framework. How does this shared protocol parallel the function of REST APIs and OpenAPI specifications in enabling interoperability between disparate systems?

---

ᚾ **Lecture 10: Databases and Data Manipulation for IT**

**Course:** IT105 — Programming for IT (Python, Bash, PowerShell)  
**Degree:** Bachelor of Science in Information Technology, University of Yggdrasil, 2040

---

### Overview

IT professionals do not need to be database administrators, but they must be able to query, update, and manipulate data stored in databases. This lecture covers SQL fundamentals (SELECT, INSERT, UPDATE, DELETE, JOIN, aggregation), database access from Python (`sqlite3`, `psycopg` for PostgreSQL) and PowerShell (`Invoke-Sqlcmd`), and the practical data tasks that IT professionals encounter: inventory management, log analysis, configuration tracking, and reporting.

### Key Topics

- **SQL Fundamentals:** The relational model (tables, rows, columns, primary keys, foreign keys, constraints) and the core SQL commands: `SELECT` (with `WHERE`, `ORDER BY`, `LIMIT`/`OFFSET`, `DISTINCT`), `JOIN` (INNER, LEFT, RIGHT, FULL — with Venn diagrams illustrating each), `GROUP BY` and aggregation (`COUNT`, `SUM`, `AVG`, `MIN`, `MAX`, `HAVING`), `INSERT`, `UPDATE`, `DELETE`, and `CREATE TABLE`. The lecture covers: subqueries (correlated and non-correlated), Common Table Expressions (CTEs with `WITH`), and window functions (`ROW_NUMBER()`, `RANK()`, `LEAD()`, `LAG()` — the 2040 essential for advanced analytics). The hands-on lab: given a database of server inventory, write queries to find underutilised machines, track hardware warranty status, and generate a depreciation report.
- **Python Database Access:** The `sqlite3` module (built-in, file-based, perfect for scripts and local data stores) and `psycopg` (the PostgreSQL adapter, the 2040 standard for production databases). The lecture covers: connection strings, cursors, parameterized queries (essential for preventing SQL injection — never use string concatenation for SQL), transactions (`commit` and `rollback`), and context managers (`with conn:` for automatic cleanup). The hands-on lab: write a Python script that reads a CSV of new user accounts, validates the data, and inserts them into a SQLite database with error handling for duplicates.
- **PowerShell Database Access:** `Invoke-Sqlcmd` for SQL Server, and the `Npgsql` module for PostgreSQL. The lecture covers: executing queries and returning result sets as objects, parameterized queries with `SqlParameter`, and exporting results to CSV (`Export-Csv`) or JSON (`ConvertTo-Json`). The hands-on lab: write a PowerShell script that queries a database for certificates expiring in the next 60 days and emails a report to the security team.
- **NoSQL for IT Professionals:** Not all data is relational. The lecture introduces: document stores (MongoDB — querying JSON-like documents with `find` and aggregation pipelines), key-value stores (Redis — for caching, session management, and lightweight queues), and time-series databases (InfluxDB — for metrics and monitoring data). The 2040 reality: IT professionals increasingly encounter these databases in their infrastructure and must be able to query them for operational data.
- **Data Reporting and Export:** Generating reports from database queries. The lecture covers: CSV export (the universal interchange format), HTML report generation (using templating engines like Jinja2 in Python), and Excel export (using `openpyxl` or `ImportExcel` in PowerShell). The 2040 best practice: reports should be generated automatically by scheduled scripts, published to a dashboard or sent via email, and archived for audit purposes.

### Lecture Notes

SQL is the most durable skill in IT. It has been the standard query language for relational databases since the 1970s and remains essential in 2040. The IT professional who cannot write a `JOIN`, aggregate with `GROUP BY`, or use a CTE to break a complex query into readable steps is limited in their ability to extract insight from operational data. The lecture emphasises that SQL is not "developer work"; it is "data literacy," and every IT professional must be data-literate.

Parameterized queries are the single most important security practice in database access. SQL injection — the technique of manipulating input to alter the structure of a SQL query — remains one of the most common vulnerabilities in 2040, despite being well-understood for decades. The lecture includes a dramatic demonstration: a script that uses string concatenation (`query = "SELECT * FROM users WHERE name = '" + user_input + "'"`) and a malicious input (`'; DROP TABLE users; --`) that destroys data. The fix is simple and universal: use parameterized queries (`cursor.execute("SELECT * FROM users WHERE name = ?", (user_input,))`), which treat input as data, not as executable SQL.

Window functions are the most powerful SQL feature that many IT professionals do not know. Unlike aggregation functions that collapse rows into a single result, window functions calculate a value across a "window" of related rows while preserving the original rows. `ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC)` assigns a rank to each employee within their department by salary. `LEAD(order_date) OVER (PARTITION BY customer ORDER BY order_date)` retrieves the next order date for each customer, enabling gap analysis. These functions transform complex reporting queries from hundreds of lines into tens of lines.

### Required Reading

- Beaulieu, A. (2033). *Learning SQL*, 4th Edition. O'Reilly. Chapters 1-9, 14.
- psycopg Documentation (2040). "Basic Module Usage, SQL Composition, Performance."
- Yggdrasil Data Operations Guide (2040). "Query Standards and SQL Style Guide."

### Discussion Questions

1. A junior engineer writes: `query = "SELECT * FROM servers WHERE hostname = '" + hostname + "'"`. Explain the SQL injection vulnerability and rewrite the query using parameterised queries in Python (`psycopg`), PowerShell (`Invoke-Sqlcmd`), and Bash (`sqlite3` with bound parameters).
2. Design a SQL query that reports the monthly growth rate of a server fleet: total machines, new additions, decommissions, and net change. Use window functions to calculate running totals and month-over-month differences. Explain your schema assumptions.
3. The Norse *lögberg* (law rock) was where the lawspeaker recited the law from memory, and every free person had the right to know the law. How does this principle of accessible, structured public knowledge inform the design of database schemas and reporting systems that make organisational data transparent to those who need it?

---

ᛁ **Lecture 11: Configuration Management and Infrastructure as Code**

**Course:** IT105 — Programming for IT (Python, Bash, PowerShell)  
**Degree:** Bachelor of Science in Information Technology, University of Yggdrasil, 2040

---

### Overview

Manual configuration is the enemy of consistency and reproducibility. This lecture introduces Infrastructure as Code (IaC) and configuration management through the lens of IT automation: Ansible (agentless, Python-powered, YAML-based), Terraform (declarative infrastructure provisioning), and the emerging 2040 tools (Pulumi for general-purpose language IaC, Crossplane for Kubernetes-native infrastructure). Students write Ansible playbooks and Terraform configurations that provision and configure real lab infrastructure.

### Key Topics

- **Infrastructure as Code Principles:** The core concepts: idempotency (running the same code twice produces the same result), immutability (replacing rather than modifying infrastructure), declarative versus imperative paradigms, and version control (all infrastructure code in Git, with peer review and CI/CD). The lecture covers: the "cattle, not pets" metaphor (servers are replaceable instances, not unique snowflakes), and the 2040 reality that IaC is not optional for teams managing more than a handful of systems.
- **Ansible:** The agentless configuration management tool that uses SSH (or WinRM) to push configurations. The lecture covers: inventory files (static and dynamic), playbooks (YAML lists of tasks), modules (`copy`, `template`, `package`, `service`, `user`, `cron`, `debug`), variables and facts (`ansible_facts` for OS discovery), conditionals and loops, handlers (triggered actions), and roles (reusable, composable playbook components). The hands-on lab: write a playbook that hardens a Linux server: updates packages, configures SSH, sets up a firewall, creates a monitoring user, and installs the node_exporter service.
- **Terraform:** The declarative tool for provisioning infrastructure across cloud providers, on-premises systems, and SaaS services. The lecture covers: HCL (HashiCorp Configuration Language), providers (AWS, Azure, GCP, VMware, Kubernetes), resources and data sources, state management (local vs. remote state, state locking, state versioning), variables and outputs, and modules (reusable infrastructure components). The hands-on lab: write a Terraform configuration that provisions a virtual machine on the Yggdrasil Bifröst Cloud, attaches a disk, and configures a security group.
- **Pulumi and Crossplane:** The 2040 alternatives. Pulumi allows infrastructure definition in general-purpose languages (Python, TypeScript, Go) rather than HCL, enabling loops, conditionals, and abstraction that are awkward in Terraform. Crossplane treats infrastructure as Kubernetes custom resources, enabling GitOps workflows where `kubectl apply` provisions cloud resources. The lecture covers: when to choose each tool (Terraform for broad provider support and ecosystem; Pulumi for complex logic and team language preferences; Crossplane for Kubernetes-native shops).
- **Testing and Validation:** `ansible-lint` for playbook quality, `terraform validate` and `terraform plan` for pre-deployment verification, and the 2040 additions: OPA (Open Policy Agent) for policy-as-code ("no security group may allow 0.0.0.0/0 to port 22"), and Terratest (Go-based integration testing for Terraform). The lecture emphasises: always run `terraform plan` before `apply`, always review diffs, and never commit credentials to version control.

### Lecture Notes

Ansible's agentless architecture is both its greatest advantage and its limitation. Advantage: no software needs to be installed on target systems; you only need SSH access and Python. Limitation: Ansible pushes configuration from the control node, which does not scale to tens of thousands of targets without significant parallelism and can be slow for large fleets. For the Yggdrasil lab environment (50-100 servers), Ansible is ideal. For hyperscale environments (10,000+ nodes), agent-based tools (Salt, Puppet, Chef) or pull-based models (Ansible pull, Kubernetes controllers) are preferred.

Ansible's YAML syntax is readable but verbose. A simple task — copy a file, ensure a service is running — requires 4-6 lines of YAML. A complex playbook with conditionals, loops, and error handling can become unreadable. The lecture teaches the "Ansible readability" style: use comments, break large playbooks into roles, use variables rather than hardcoded values, and leverage Jinja2 templating for dynamic configuration. The Yggdrasil Ansible standard requires: all playbooks must pass `ansible-lint`, all variables must be documented in `defaults/main.yml`, and all tasks must have `name` descriptions.

Terraform's state file is its Achilles heel. Terraform maintains a mapping between the resources defined in HCL and the actual resources in the cloud provider. This state is stored in a file (local or remote) and is the source of truth for Terraform operations. If the state is lost or corrupted, Terraform cannot manage the infrastructure. If the state is accessed concurrently by two administrators, corruption is likely. The 2040 best practice: remote state with locking (Terraform Cloud, AWS S3 with DynamoDB locking, Azure Blob with leases) and state versioning (so previous states can be restored). The lecture includes a horror story: two administrators ran `terraform apply` simultaneously from their laptops, corrupting the state and orphaning 47 cloud resources that had to be manually reconciled.

The "Terraform plan before apply" rule is absolute. `terraform plan` shows what Terraform intends to do: create, modify, or destroy resources. Reviewing this plan is the primary safety mechanism against accidental destruction. The lecture mandates: no `terraform apply` without a prior `plan`, no `terraform apply -auto-approve` in production (the `-auto-approve` flag skips the confirmation prompt), and all plans must be reviewed by a second engineer before application. These rules have prevented countless outages at Yggdrasil.

### Required Reading

- Hochstein, L. & Moser, R. (2033). *Ansible: Up and Running*, 3rd Edition. O'Reilly. Chapters 1-6.
- Brikman, Y. (2034). *Terraform: Up and Running*, 4th Edition. O'Reilly. Chapters 1-5.
- Kief Morris. (2032). *Infrastructure as Code*, 2nd Edition. O'Reilly. Chapters 1-3, 8.

### Discussion Questions

1. Compare Ansible (agentless, push-based) and Salt (agent-based, pub-sub) for a university IT environment with 500 Linux servers, 200 Windows workstations, and 50 network switches. Evaluate scalability, security, complexity, and operational fit.
2. A `terraform plan` shows that it will destroy and recreate a database instance because the `instance_type` changed from `db.t3.medium` to `db.t3.large`. The database contains production data. What is your response? How would you modify the infrastructure code to avoid this risk in the future?
3. The Norse *hǫlmganga* (duel on an island) followed strict rules: the island was marked with hazel poles, and stepping outside meant forfeiture. How does this bounded, rule-governed arena parallel the concept of idempotent, declarative infrastructure code that produces predictable results within defined boundaries?

---

ᛃ **Lecture 12: The Automation Challenge — Capstone Practical**

**Course:** IT105 — Programming for IT (Python, Bash, PowerShell)  
**Degree:** Bachelor of Science in Information Technology, University of Yggdrasil, 2040

---

### Overview

The final lecture is a 48-hour capstone challenge. Students receive a realistic scenario: a new department needs 20 virtual machines provisioned, hardened, monitored, and documented. The challenge requires writing scripts in Python, Bash, and PowerShell; interacting with APIs; querying databases; and applying infrastructure-as-code principles. The evaluation criteria emphasise correctness, robustness, documentation, and the ability to explain design decisions.

### Key Topics

- **Challenge Specification:** Students must: (1) write a Python script that reads a CSV of server requirements and calls the Yggdrasil Cloud API to provision VMs, (2) write an Ansible playbook that hardens the VMs (updates, SSH config, firewall, monitoring agent), (3) write a Bash script that verifies the provisioning (checks VM status, pings each host, validates SSH access), (4) write a PowerShell script that generates a compliance report (VM names, IPs, OS versions, patch levels) and emails it to the instructor, and (5) write a Terraform configuration that provisions a shared database for the department and configures access controls.
- **Error Handling and Robustness:** All scripts must handle expected errors (API rate limits, network timeouts, SSH failures) and fail gracefully. The lecture reviews: retry logic with exponential backoff, idempotency (running the provisioning script twice should not create duplicate VMs), and rollback procedures (if provisioning fails halfway, the script should clean up partial resources).
- **Documentation and Handoff:** Every script must include: a header comment explaining purpose and usage, inline comments for complex logic, a README explaining dependencies and execution instructions, and a runbook for troubleshooting common failures. The lecture emphasises: code is written once and read many times; the author who does not document is condemning their colleagues to reverse-engineering.
- **Live Demonstration:** The final 30 minutes is a live demo where the student runs their scripts, explains their design, and responds to examiner questions. The examiner may introduce a failure (e.g., an API returns 503, a VM refuses SSH connections) and ask the student to diagnose and fix it in real time.

### Lecture Notes

The Automation Challenge is designed to be stressful and realistic. In production IT, deadlines are tight, requirements are vague, and things break unexpectedly. The challenge simulates this: the CSV has inconsistent data (missing fields, invalid formats), the API has rate limits that require throttling, and the Ansible playbook fails on one VM because it has a different OS version. Students who have mastered the course material will navigate these issues calmly; those who have merely memorised syntax will struggle.

Idempotency is the most important quality of operational scripts. A provisioning script that creates duplicate resources when run twice is dangerous; a hardening script that appends the same configuration line to a file every time it runs will eventually break the file. The lecture teaches idempotency patterns: check before create (`if not exists: create`), use Ansible's native idempotency (modules are designed to be safe to rerun), and design API clients to track state. The "safety check" pattern: before any destructive operation, log the intended action and require confirmation, or check a state file to verify the operation has not already been performed.

The live demonstration tests not just technical skill but operational composure. When a script fails during a demo, the professional does not panic; they read the error message, trace the execution flow, identify the assumption that was violated, and implement a fix. The examiner is not looking for perfection; they are looking for systematic reasoning under pressure. A student who says "I don't know why it failed, but here's how I would find out" scores higher than one who makes wild guesses.

### Required Reading

- Yggdrasil IT105 Challenge Brief (2040). "Scenario, Requirements, Evaluation Criteria, and Submission Guidelines."
- Kief Morris. (2032). *Infrastructure as Code*, 2nd Edition. O'Reilly. Chapter 12 (Testing and Delivery).

### Discussion Questions

1. Your provisioning script fails after creating 12 of 20 VMs due to an API rate limit. Design a resumable script that can be re-run safely, creating only the missing VMs without affecting the existing ones. What state management approach do you use?
2. A colleague argues that Bash is sufficient for all IT automation and that learning Python and PowerShell is unnecessary. Construct a counter-argument using specific examples where Bash is inadequate and Python or PowerShell provide essential capabilities.
3. The Norse *skald* composed poetry not merely for entertainment but to preserve knowledge — genealogies, laws, and heroic deeds — in memorable form. How does the skald's role as a knowledge preserver parallel the IT professional's obligation to document their automation in durable, transmissible form?

---

## Final Examination Preparation

The IT105 final examination assesses programming proficiency across Python, Bash, and PowerShell, with emphasis on practical operational problem-solving. It consists of two components:

### Component A: Written Examination (60%)

A 2.5-hour written examination with six questions, of which students must answer four.

**Sample Questions:**

1. **Python Scripting:** Write a Python script that parses a web server access log in combined log format, extracts all unique IP addresses, performs reverse DNS lookups, and outputs a CSV with columns: IP, hostname, request_count, last_request_time. Include error handling for DNS timeouts and malformed log lines.

2. **Bash Scripting:** Write a Bash script that takes a directory path as an argument, finds all files larger than 100MB modified in the last 30 days, compresses them individually with gzip, verifies the compressed archives (gzip -t), and logs all actions to a timestamped log file. The script must be robust: handle spaces in filenames, check preconditions, and exit with appropriate status codes.

3. **PowerShell Scripting:** Write a PowerShell function `Get-ServiceHealth` that accepts a list of server names via pipeline, queries the status of critical services (WinRM, DHCP, DNS) on each, and returns objects with properties: ServerName, ServiceName, Status, StartType, LastExitCode. Include comment-based help and support for `-Credential`.

4. **API Interaction:** A cloud provider's API requires OAuth 2.0 Client Credentials authentication. Describe the token acquisition flow, explain how your script would handle token refresh, and write the Python code (using `httpx` or `requests-oauthlib`) to authenticate and make a paginated API request.

5. **SQL Querying:** Given a database schema for server inventory (servers, departments, warranty_contracts), write SQL queries to: (a) find all servers in the "Engineering" department with warranties expiring in the next 90 days, (b) calculate the total hardware value per department, and (c) identify servers that have not had a maintenance record in the last year.

6. **Automation Design:** A company has 1,000 Linux servers that need quarterly security patching. Currently, a team of 4 engineers performs this manually over two weeks. Design an automated patching workflow using Ansible (or an alternative tool of your choice). Include: pre-patch validation, patch application, post-patch verification, rollback procedures, and reporting. Address the risks of automated patching and how you would mitigate them.

### Component B: Live Coding Examination (40%)

A 90-minute practical examination in the lab. Students are given three operational tasks (one suitable for Python, one for Bash, one for PowerShell) and must implement working solutions. Internet access is permitted for documentation lookup, but copying code from existing repositories is prohibited.

**Evaluation Criteria:**
- Correctness (script produces correct output for test cases)
- Robustness (handles edge cases, errors, and invalid input)
- Readability (clear variable names, comments, logical structure)
- Efficiency (appropriate algorithms, no unnecessary resource consumption)
- Style (follows language conventions and course style guides)

---

*Code is the sword of the IT professional. Wield it with precision, maintain it with discipline, and pass it to the next generation with clarity.* ᛟ

— Dr. Sigrún Vérendóttir, University of Yggdrasil, 2040
