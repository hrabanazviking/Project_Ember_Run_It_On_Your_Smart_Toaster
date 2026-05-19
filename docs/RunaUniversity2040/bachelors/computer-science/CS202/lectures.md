# CS202: Operating Systems Design
## Bachelor of Science in Computer Science — University of Yggdrasil, 2040

**Credits:** 4
**Prerequisites:** CS101 — Computational Thinking & Problem Solving; CS103 — Data Structures & Algorithms I; CS106 — Computer Architecture
**Description:** The operating system is the sovereign of the machine — the software that arbitrates every access to the CPU, the memory, the disk, and the network. It is simultaneously a resource manager (allocating scarce hardware among competing processes), a virtual machine (presenting each process with the illusion of a dedicated computer), and a security boundary (enforcing isolation between processes and controlling access to resources). This course dissects the modern operating system kernel from first principles, covering process management and scheduling, memory management (virtual memory, paging, segmentation), file systems (design, consistency, journaling), I/O subsystems, and inter-process communication. The course is taught through the lens of **Linux** — the dominant operating system of the 2040s in servers, embedded devices, and Android phones — with supplementary study of the **Yggdrasil Kernel**, the University's own teaching OS, which students extend throughout the semester. Students implement a simple scheduler, a virtual memory manager, and a file system in C, and they complete a term project that adds a novel kernel module to the Yggdrasil Kernel. The OS is the foundation on which all other software rests; understanding it is understanding the ground beneath one's feet.

---

## Lecture 1: The Operating System as Resource Manager and Virtual Machine

What does an operating system do, and why does it exist? The question is not idle — it is the essential first step toward designing one. The OS sits between the hardware and the application software, and it performs two fundamental roles that are in tension: it is a **resource manager** — allocating the CPU, memory, storage, and I/O devices among competing processes, resolving conflicts, and enforcing fairness — and it is a **virtual machine** — presenting each process with the illusion that it has a dedicated computer, with its own address space, its own CPU, and its own files, while hiding the messy reality of shared, finite hardware.

The **resource manager** perspective is grounded in scarcity. A computer has one CPU (or a finite number of cores), a finite amount of memory, a finite number of disk sectors. The OS must decide: which process gets the CPU next, and for how long? Which pages of memory should be evicted when a new allocation arrives? Which disk I/O requests should be served first? These are allocation problems, and the OS designer's toolkit — scheduling algorithms, replacement policies, admission control — is drawn from operations research and queueing theory. The OS is, in a very real sense, an exercise in applied microeconomics: it allocates scarce resources among competing consumers, with objectives (fairness, throughput, responsiveness) that are often in conflict.

The **virtual machine** perspective is grounded in abstraction. A process should not need to know about other processes — it should not see their memory, should not be preempted because they exist, should not have its files corrupted by their writes. The OS provides **process isolation**: each process runs in its own virtual address space, scheduled independently, with the kernel mediating every interaction with the hardware and with other processes. The virtual machine abstraction is extended by the **system call interface** — the set of functions (read, write, fork, exec, mmap, etc.) through which a process requests services from the kernel. The system call interface is the contract between the application and the OS; everything below it (the kernel) can be changed, and everything above it (the application) need not know.

The **evolution of operating systems** traces the arc from simple to complex, from bare-metal to virtualised, from monolithic to modular. The early machines (1950s) had no OS — the programmer loaded the program directly, and the machine was dedicated to one job at a time. **Batch systems** (1960s) introduced the **monitor** — a resident program that loaded jobs from a queue, ran them, and transitioned to the next. **Multiprogramming** (late 1960s) kept multiple jobs in memory simultaneously, switching between them when one blocked on I/O — the first step toward the virtual machine abstraction. **Time-sharing** (CTSS, Multics, Unix) added interactive use: the OS allocated CPU time in small slices (quanta), rotating among users so that each felt they had the machine to themselves. The **personal computer** (1980s) temporarily returned to single-user, single-tasking OSes (MS-DOS, classic Mac OS), before convergence on the multiprocessing, multi-user model (Windows NT, Mac OS X, Linux) that remains standard in 2040.

The **2040 OS landscape** is dominated by Linux — which runs on 100% of the TOP500 supercomputers, the vast majority of cloud servers, all Android devices, and countless embedded systems — with Windows and macOS as the major desktop players, and iOS as a significant mobile OS. The **Yggdrasil Kernel** — a teaching OS developed at the University — is a microkernel-based system with a clean, well-documented codebase designed for pedagogical extension. Students will spend the semester reading, modifying, and extending the Yggdrasil Kernel, learning OS design by designing.

**Required Reading:**
- Andrew S. Tanenbaum & Herbert Bos, *Modern Operating Systems* (5th ed., 2022/2039), chs. 1–2
- Abraham Silberschatz, Peter B. Galvin & Greg Gagne, *Operating System Concepts* (10th ed., 2018/2040), chs. 1–2
- Remzi H. Arpaci-Dusseau & Andrea C. Arpaci-Dusseau, *Operating Systems: Three Easy Pieces* (v1.10, 2040), chs. 1–4 ("Introduction," "Virtualisation," "Concurrency," "Persistence")
- Brian W. Kernighan, *UNIX: A History and a Memoir* (2019/2039), chs. 1–3
- The Yggdrasil Kernel Documentation (2040)

**Discussion Questions:**
1. The OS is both a resource manager and a virtual machine. Are these roles complementary or in tension? When does managing resources efficiently conflict with providing a clean abstraction?
2. The system call interface is a contract. What makes a good system call interface — and what are the costs of getting it wrong (too narrow, too broad, too complex)?
3. Linux is a monolithic kernel; Minix and QNX are microkernels. What are the arguments for each architecture, and how has the debate evolved from the Tanenbaum-Torvalds exchange of 1992 to the practice of 2040?

---

## Lecture 2: Process Management — The Process, the PCB, and the Scheduler

A **process** is a program in execution. It is the fundamental unit of work in a modern OS, and its lifecycle — creation, execution, blocking, preemption, termination — is the rhythm that the kernel orchestrates. The OS represents each process by a **Process Control Block (PCB)** — a data structure in kernel memory that contains everything the kernel needs to know about the process: its identifier (PID), its state (running, ready, blocked, terminated), its register context (saved when the process is preempted, restored when it resumes), its memory map (the layout of its virtual address space), its open file descriptors, and its accounting information (CPU time used, priority, parent PID). The PCB is the soul of the process; when the kernel switches between processes, it saves the PCB of the outgoing process and restores the PCB of the incoming.

The **process lifecycle** is driven by system calls and signals. **fork()** creates a new process — an exact copy of the calling process, differing only in the return value (0 for the child, the child's PID for the parent). **exec()** replaces the current process image with a new program — loading the executable, setting up the new address space, and jumping to the entry point. **wait()** allows a parent to block until a child terminates, collecting its exit status. **exit()** terminates the process, freeing its resources and notifying its parent. These four calls — fork, exec, wait, exit — are the primitives of process creation and destruction in Unix/Linux, and their design, unchanged in essence since the 1970s, is one of the great successes of systems architecture.

The **context switch** — the act of suspending one process and resuming another — is the most frequent and most performance-critical operation in the kernel. It involves: (1) saving the current process's register state (general-purpose registers, program counter, stack pointer, flags) to its PCB, (2) selecting the next process from the ready queue (scheduling), (3) restoring the next process's register state from its PCB, and (4) switching the address space (updating the page table pointer — the most expensive step, requiring a TLB flush on older architectures, mitigated by ASIDs — Address Space Identifiers — on modern hardware). A context switch on a 2040-era processor takes about 1–2 microseconds — a small number, but multiplied by thousands of switches per second, it becomes a significant fraction of CPU time.

The **ready queue** is the data structure that holds all processes that are ready to run but not currently running. It is typically a priority queue, organised by the scheduling policy. The **blocked queue** holds processes waiting for an event (I/O completion, a semaphore, a timer). When the event occurs, the process is moved to the ready queue. The kernel itself is not a process — it runs in **kernel mode** (ring 0 on x86), with access to all hardware and all memory, and it is invoked by system calls, interrupts, and exceptions. The distinction between **user mode** and **kernel mode** is the hardware-enforced boundary that is the foundation of OS security.

**Required Reading:**
- Remzi & Andrea Arpaci-Dusseau, *Operating Systems: Three Easy Pieces* (v1.10, 2040), chs. 5–7 ("Processes," "Process API," "Direct Execution")
- Andrew S. Tanenbaum & Herbert Bos, *Modern Operating Systems* (5th ed., 2022/2039), ch. 2
- Robert Love, *Linux Kernel Development* (4th ed., 2039), chs. 3–4 ("Process Management," "Process Scheduling")
- The Yggdrasil Kernel: Process Management Module (2040)

**Discussion Questions:**
1. fork() creates a child by copying the parent. Why copy — why not create an empty process and populate it? What are the performance implications (copy-on-write), and how does Linux's clone() system call generalise this?
2. A context switch involves a TLB flush (unless ASIDs are used). What is the performance cost — and how has the shift to virtualised environments (where a context switch may also involve a VM exit) amplified it?
3. The process is the unit of resource ownership; the thread is the unit of execution. Why are both concepts needed — and what would an OS that unified them (e.g., Plan 9's rfork) gain and lose?

---

## Lecture 3: Threads and Concurrency — Kernel Threads, User Threads, and the Scheduler Activation

A **thread** is a lightweight process — a single sequential flow of control within a process. Where a process owns resources (address space, file descriptors, signals), a thread shares its process's resources with its sibling threads. Threads were introduced to address the limitations of the single-threaded process model: a process that blocks on I/O cannot make progress on other work — unless it spawns additional processes (expensive) or uses asynchronous I/O (complex). Threads provide a simpler model: a process can have multiple threads, and when one blocks, the scheduler can run another thread of the same process. Threads are the dominant concurrency model in 2040: every web server, database, and GUI application uses threads.

The two models of thread implementation are **kernel-level threads** (KLTs) and **user-level threads** (ULTs). In the KLT model, the kernel is aware of each thread, schedules them independently, and manages their state. The advantage is that when one thread blocks on I/O, the kernel can schedule another thread (of the same process or a different one). The disadvantage is the cost of kernel involvement — every thread creation, context switch, and synchronisation operation requires a system call. In the ULT model, threads are managed entirely by a user-space library, invisible to the kernel. Thread creation and context switching are fast (no kernel involvement), but when one thread blocks on a system call, the kernel — which sees only the process — blocks the entire process, regardless of whether other threads are ready. ULTs are fast but fragile; KLTs are robust but slower.

The **hybrid model** — used by modern Linux, Solaris, and the Yggdrasil Kernel — employs **scheduler activations**: the kernel allocates a pool of KLTs (called "virtual processors") to each process, and a user-space scheduler maps ULTs onto these KLTs. When a KLT blocks in the kernel, the kernel notifies the user-space scheduler (via an "upcall"), which can map a ULT onto a different KLT. The hybrid model combines the robustness of KLTs with the performance of ULTs — at the cost of significant complexity in the user-space scheduler.

The **POSIX Threads (pthreads)** API is the standard interface for thread programming in C and C++ on Linux and Unix. It provides functions for thread creation (pthread_create), joining (pthread_join), and synchronisation (mutexes, condition variables, barriers — see CS204). The **C11 and C++11 thread APIs** provide a higher-level, type-safe interface built on the same kernel primitives. In 2040, the dominant concurrency model for high-performance systems has shifted toward **async/await** and **coroutine-based** models (as in Rust's tokio, Python's asyncio, and the Yggdrasil Async Framework), which avoid the overhead of thread-per-connection and the complexity of explicit synchronisation — but threads remain the foundation, and understanding them is essential.

**Required Reading:**
- Remzi & Andrea Arpaci-Dusseau, *Operating Systems: Three Easy Pieces* (v1.10, 2040), chs. 25–28 ("Threads," "Locks," "Condition Variables")
- Andrew S. Tanenbaum & Herbert Bos, *Modern Operating Systems* (5th ed., 2022/2039), ch. 2.2
- Robert Love, *Linux Kernel Development* (4th ed., 2039), ch. 4 ("Process Scheduling")
- Brian W. Kernighan & Dennis M. Ritchie, *The C Programming Language* (2nd ed., 1988/2038), Appendix B (standard library threads)
- The Yggdrasil Kernel: Threading Module (2040)

**Discussion Questions:**
1. User-level threads are fast but block the entire process on a blocking system call. Is there a way to make system calls non-blocking for ULTs — without kernel cooperation?
2. The scheduler activation model was proposed by Anderson et al. (1991) but never widely adopted. Why not — and what has replaced it in the 2040 landscape (e.g., M:N threading in Go's goroutines)?
3. Async/await models avoid thread-per-connection overhead but introduce "coloured functions" (a function is either sync or async, and one cannot call the other directly). Is this a fundamental limitation of the model, or a language-design problem?

---

## Lecture 4: CPU Scheduling — Algorithms, Trade-offs, and the Completely Fair Scheduler

The **scheduler** is the kernel subsystem that decides which thread runs on which CPU, and for how long. Scheduling is the quintessential OS trade-off: the goals of **fairness** (every thread gets a share), **throughput** (maximise completed work per unit time), **responsiveness** (interactive applications feel snappy), and **energy efficiency** (minimise power consumption) are often in conflict, and the scheduler designer must choose a point in the Pareto-optimal space and implement it efficiently. The literature of scheduling is vast — spanning operations research, queueing theory, and empirical systems work — and the algorithms range from the trivially simple (FCFS) to the devilishly subtle (the Linux Completely Fair Scheduler, CFS).

The classic scheduling algorithms form a pedagogical progression. **First-Come, First-Served (FCFS)** — run threads in the order they arrive — is simple and fair but can produce **convoy effects**: a long-running CPU-bound thread blocks a queue of short I/O-bound threads, starving them and degrading responsiveness. **Shortest Job First (SJF)** — run the thread with the shortest predicted CPU burst — is optimal for minimising average waiting time, but it requires knowing the burst length in advance (impossible in general) and can starve long jobs. **Round Robin (RR)** — allocate each thread a fixed time slice (quantum), and when the quantum expires, preempt and rotate — provides fairness and responsiveness, but the choice of quantum is critical: too short, and context-switch overhead dominates; too long, and RR degenerates to FCFS.

**Multi-level feedback queues (MLFQ)** — the scheduler of choice in most practical systems from CTSS (1962) through Windows NT (1993) — dynamically adjust a thread's priority based on its observed behaviour. Threads that use their full quantum are assumed to be CPU-bound and are demoted to lower-priority queues (with longer quanta); threads that block before their quantum expires are assumed to be I/O-bound and are promoted to higher-priority queues (with shorter quanta). MLFQ approximates SJF without requiring prior knowledge of burst length — it learns from history.

The **Linux Completely Fair Scheduler (CFS)** — introduced in Linux 2.6.23 (2007) and still the default in 2040 — takes a different approach. Rather than assigning priorities and quanta, CFS tracks the **virtual runtime** of each thread: the amount of CPU time it has consumed, weighted by its niceness. The scheduler always picks the thread with the smallest virtual runtime — the one that has been "treated most unfairly." CFS uses a red-black tree (O(log n) insertion, O(1) extraction of the minimum) to maintain the set of runnable threads, and it computes the target latency — the interval within which every runnable thread should get at least one time slice — and derives the per-thread time slice from that. CFS is a triumph of algorithm engineering: it provides fairness, responsiveness, and scalability (the red-black tree handles tens of thousands of threads efficiently).

The **2040 scheduling landscape** adds new challenges. **Heterogeneous architectures** — CPUs with a mix of performance cores and efficiency cores (ARM big.LITTLE, Intel Hybrid) — require the scheduler to decide not just *when* a thread runs but *where* (which core), and to migrate threads between cores to balance load and exploit the appropriate core type. **Energy-aware scheduling** — critical for mobile devices and for the carbon footprint of data centres — adds power consumption as a first-class scheduling objective. The Yggdrasil Kernel includes an experimental **energy-proportional scheduler** that students can modify and benchmark.

**Required Reading:**
- Remzi & Andrea Arpaci-Dusseau, *Operating Systems: Three Easy Pieces* (v1.10, 2040), chs. 8–10 ("Scheduling")
- Andrew S. Tanenbaum & Herbert Bos, *Modern Operating Systems* (5th ed., 2022/2039), ch. 2.4
- Robert Love, *Linux Kernel Development* (4th ed., 2039), ch. 4 ("Process Scheduling"), esp. the CFS sections
- J. Axboe, "The Linux Block Layer: Built for Fast Storage," *LinuxCon* (2019)
- The Yggdrasil Kernel: Energy-Proportional Scheduler Documentation (2040)

**Discussion Questions:**
1. The Linux CFS uses virtual runtime to approximate fairness. Is virtual runtime a good measure of "fairness" — and how would you define fairness formally for a scheduler?
2. MLFQ estimates a thread's CPU-boundedness from history. What happens if a thread changes behaviour — e.g., from I/O-bound to CPU-bound — and how quickly does MLFQ adapt?
3. In a heterogeneous architecture (performance cores + efficiency cores), should the scheduler prefer to run interactive threads on performance cores (for responsiveness) or on efficiency cores (to save power for batch work)? What is the trade-off — and how would you formalise it?

---

## Lecture 5: Memory Management I — Virtual Memory, Paging, and the MMU

Memory management is the OS's most delicate responsibility — and, when done wrong, the source of the most catastrophic failures. A process that writes beyond its allocated memory corrupts not its own data (which would be bad enough) but potentially the data of other processes or the kernel itself. The solution is **virtual memory**: each process sees a contiguous, private address space — from 0 to some maximum (e.g., 2⁴⁷ on x86-64) — and the hardware (the **Memory Management Unit, MMU**) translates every virtual address to a physical address on-the-fly, enforcing protection along the way. Virtual memory is simultaneously an abstraction (the process never sees physical addresses), an isolation mechanism (a process cannot address another process's memory), and an efficiency mechanism (physical memory is allocated on demand, not all at once).

The **address translation** is the core mechanism. The virtual address is split into a **virtual page number (VPN)** and an **offset** within the page. The MMU consults the **page table** — a data structure in memory that maps VPNs to **physical frame numbers (PFN)** — and if the page is present (the valid bit is set), the physical address is formed by concatenating the PFN with the offset. If the page is not present — a **page fault** — the MMU raises an exception, and the kernel's page-fault handler is invoked to bring the page into memory from disk (or allocate a new page, or signal a segmentation fault if the access is illegal).

The **page table** is the central data structure of memory management, and its design is constrained by the tension between speed (the MMU must consult it on every memory access) and space (a naive page table — one entry per virtual page — would consume enormous memory: for a 48-bit virtual address space with 4KB pages, a flat page table would have 2³⁶ entries, each ~8 bytes — 512 GB, far more than the memory it manages). The **multi-level page table** — used by x86-64, ARMv8, and the Yggdrasil architecture — imposes a tree structure: the VPN is split into segments (e.g., four segments of 9 bits each), each indexing into a separate level of the page table. Levels that are entirely invalid are not allocated — a sparse page table is sparse in memory as well as in the address space. The cost: a TLB miss now requires four memory accesses (one per level) to translate the address — a cost mitigated by the TLB (TLB hits avoid the page-table walk entirely).

The **instructional page size** — 4KB on most architectures since the 1980s — is a compromise: smaller pages waste less memory to internal fragmentation but require more page-table entries and more TLB entries. The 2040 landscape includes **huge pages** (2MB, 1GB on x86-64; 64KB on ARM) — transparently managed by the kernel when contiguous physical memory is available, reducing TLB pressure and page-table depth for large data structures (database buffers, in-memory caches, large language model parameters).

**Required Reading:**
- Remzi & Andrea Arpaci-Dusseau, *Operating Systems: Three Easy Pieces* (v1.10, 2040), chs. 13–16 ("Address Spaces," "Paging," "TLBs," "Advanced Page Tables")
- Andrew S. Tanenbaum & Herbert Bos, *Modern Operating Systems* (5th ed., 2022/2039), ch. 3
- Intel Corporation, *Intel 64 and IA-32 Architectures Software Developer's Manual*, Vol. 3A, ch. 4 ("Paging")
- Robert Love, *Linux Kernel Development* (4th ed., 2039), ch. 12 ("Memory Management")
- The Yggdrasil Kernel: MMU Documentation (2040)

**Discussion Questions:**
1. A 64-bit address space could theoretically hold 2⁶⁴ bytes — far more than physical memory. How much of that space is actually used by the page table, given a 4-level tree with 4KB pages — and where does the "waste" go?
2. Huge pages reduce TLB misses but waste physical memory (internal fragmentation). Under what conditions is the trade-off favourable — and how does the Linux kernel decide when to use transparent huge pages?
3. The MMU translates every memory access. What is the performance cost of a TLB miss — and how do modern processors (with hardware page-table walkers and multi-level TLBs) reduce it?

---

## Lecture 6: Memory Management II — Page Replacement, Thrashing, and the Working Set

Physical memory is finite, but the sum of the virtual address spaces of all running processes can be (and usually is) much larger. The OS must decide which pages to keep in physical memory (the **resident set**) and which to evict to disk (swap space), and it must make these decisions dynamically, in response to the changing demands of the workload. The **page replacement algorithm** is the policy that chooses the victim page — the page to evict when a new page must be brought in. The quality of this policy determines the system's performance under memory pressure: a good policy minimises **page faults** (the events where a needed page is not in memory); a bad policy can induce **thrashing** — a state where the system spends more time paging than computing, grinding to a halt.

The **optimal page replacement algorithm** — evict the page that will not be needed for the longest time in the future — is unimplementable (it requires knowledge of the future), but it is a useful theoretical benchmark: the best any practical algorithm can do is approach optimal. **FIFO** — evict the page that has been in memory the longest — is simple but suffers from **Belady's anomaly**: on some reference strings, increasing the number of frames *increases* the number of page faults. Belady's anomaly is a cautionary tale: intuition ("more memory means fewer faults") can be wrong, and formal analysis is required.

**Least Recently Used (LRU)** — evict the page that was accessed least recently — approximates optimal by assuming that the recent past predicts the near future (temporal locality). LRU works well in practice, but it requires updating a timestamp on every memory access — prohibitively expensive if done precisely. The **clock algorithm** (also called "second chance") approximates LRU efficiently: pages are arranged in a circular list, and each page has a **reference bit** that is set by the hardware on access. The clock hand sweeps the circle; if it encounters a page with reference bit = 1, it clears the bit and moves on (giving the page a "second chance"); if it encounters a page with reference bit = 0, it evicts it. The clock algorithm is the standard page-replacement algorithm in Linux and most modern OSes.

The **working set model** (Denning, 1968) provides a theoretical framework for understanding memory demand. The **working set** W(t, τ) of a process is the set of pages it has accessed in the last τ memory references. The working set size changes over time as the process moves through phases of execution; if the total working-set size of all processes exceeds physical memory, thrashing is inevitable. The OS should allocate frames to processes so that each can maintain its working set in memory; if the aggregate working-set size exceeds physical memory, the OS must either swap out an entire process (the **medium-term scheduler**, or "swapper") or deny admission to new processes. The working-set model is the intellectual foundation of memory-balancing policies in Linux, which monitor page-fault rates and adjust per-process frame allocations accordingly.

**Required Reading:**
- Remzi & Andrea Arpaci-Dusseau, *Operating Systems: Three Easy Pieces* (v1.10, 2040), chs. 19–22 ("Beyond Physical Memory: Mechanisms," "Policies," "Complete VM Systems")
- Peter J. Denning, "The Working Set Model for Program Behavior," *Communications of the ACM* 11:5 (1968): 323–333
- Andrew S. Tanenbaum & Herbert Bos, *Modern Operating Systems* (5th ed., 2022/2039), ch. 3.4
- Robert Love, *Linux Kernel Development* (4th ed., 2039), ch. 12
- The Yggdrasil Kernel: Page Replacement Module (2040)

**Discussion Questions:**
1. Belady's anomaly — more frames can mean more faults — is counterintuitive. Which algorithms exhibit it, and which do not — and what property (the "stack property") characterises those that are immune?
2. LRU is a good heuristic, but it performs badly on some access patterns — e.g., a sequential scan of a file larger than memory (the "MRU anomaly"). Why — and how do modern systems (with read-ahead and adaptive replacement) mitigate this?
3. Thrashing is a catastrophic failure mode. How can the OS detect incipient thrashing — and what actions can it take to recover? What is the role of the OOM (Out-Of-Memory) killer in Linux?

---

## Lecture 7: File Systems — Files, Directories, and the VFS Layer

The file system is the OS component that manages persistent storage — the files and directories that survive across power cycles and reboots. It is the most user-visible part of the OS, and its design reflects two fundamental tensions: **persistence vs. performance** (durable storage is slow; the file system must cache aggressively but maintain consistency) and **simplicity vs. expressiveness** (users want a simple hierarchical namespace; applications want complex metadata, atomic transactions, and versioning). The file system is a database — a specialised one, optimised for the file abstraction and the patterns of access that files exhibit.

The **file abstraction** is a named, linear sequence of bytes — the most successful abstraction in computing history. A file has a **name** (within a directory), a **size** (which can grow and shrink), an **owner** and **permissions** (who can read, write, or execute it), and **timestamps** (creation, last access, last modification). The operations on files — **open** (obtain a file descriptor, a handle used for subsequent operations), **read** (transfer bytes from the file into a buffer), **write** (transfer bytes from a buffer into the file), **seek** (reposition the file offset for the next read/write), **close** (release the file descriptor), **unlink** (remove the file from its directory, decrementing its reference count) — are the primitives of persistent data manipulation, and their semantics (particularly the atomicity guarantees under crash conditions) are the subject of decades of design and debate.

The **directory** is a mapping from names to files (or to other directories). The Unix directory is itself a file — or, more precisely, a file-like object — containing a table of (name, inode number) pairs. The **inode** (index node) is the on-disk data structure that represents a file: it stores the file's metadata (size, owner, permissions, timestamps) and the locations of its data blocks on disk. The inode is identified by an **inode number**, which is unique within a file system. The separation of the name (in the directory) from the metadata (in the inode) from the data (in the blocks) is the fundamental design decision of Unix file systems — and it is what enables **hard links**: multiple directory entries (multiple names) can refer to the same inode, and the file is not deleted until all names have been unlinked (the reference count in the inode drops to zero).

The **Virtual File System (VFS)** — introduced in Unix System V and refined in Linux — is the kernel layer that provides a uniform interface to diverse file systems. The VFS defines a set of operations (file_operations, inode_operations, super_operations) that each file system implementation must provide. When a process calls read(), the VFS redirects the call to the appropriate file system's read implementation — ext4, NTFS, NFS, procfs, sysfs, or the Yggdrasil Experimental FS. The VFS enables Linux to support dozens of file systems simultaneously, with a single system call interface — a triumph of abstraction.

**Required Reading:**
- Remzi & Andrea Arpaci-Dusseau, *Operating Systems: Three Easy Pieces* (v1.10, 2040), chs. 37–40 ("Files and Directories," "File System Implementation")
- Andrew S. Tanenbaum & Herbert Bos, *Modern Operating Systems* (5th ed., 2022/2039), ch. 4
- Robert Love, *Linux Kernel Development* (4th ed., 2039), ch. 13 ("The Virtual File System")
- Maurice J. Bach, *The Design of the UNIX Operating System* (1986/2039 reissue), chs. 4–5
- The Yggdrasil Kernel: VFS Documentation (2040)

**Discussion Questions:**
1. Hard links allow multiple directory entries to refer to the same inode. Why are hard links restricted to the same file system — and what would it take to implement "universal hard links" that span file systems?
2. The VFS abstracts file operations behind a uniform interface. What is the cost of this abstraction — and are there file system operations (e.g., copy-on-write snapshots) that the VFS interface struggles to express?
3. The Unix "everything is a file" philosophy led to the /proc, /sys, and /dev file systems. Is this philosophy still valid in 2040 — or has it been stretched beyond its limits by the complexity of modern devices and subsystems?

---

## Lecture 8: File System Internals — Inodes, Data Structures, and Crash Consistency

Beneath the VFS lies the file system implementation — the on-disk data structures and algorithms that map file offsets to disk blocks, manage free space, and maintain consistency in the face of crashes. The design of a file system is a exercise in the management of block storage — the slowest, largest, and most failure-prone component of the memory hierarchy — and the algorithms are shaped by the physical characteristics of the medium: spinning disks (with their seek times and rotational latencies) in the 20th century; flash SSDs (with their erase-before-write constraints and write amplification) in the early 21st; and persistent memory (NVDIMMs, Optane, CXL-attached memory) in the 2040s, blurring the line between storage and memory.

The **inode** is the central data structure. In a typical Unix file system (ext2, FFS, the Yggdrasil FS), the inode stores the file's metadata and an array of **block pointers** — the addresses of the disk blocks that hold the file's data. For small files, the first few blocks are stored directly in the inode (the **direct blocks**). For larger files, an **indirect block** is allocated: a block that contains pointers to data blocks. For even larger files, a **double-indirect block** points to indirect blocks, and for the largest files, a **triple-indirect block**. This tree structure — the **inode pointer structure** — supports files of enormous size (terabytes with 4KB blocks) while keeping the inode small (128–256 bytes) for the common case of small files.

**Free space management** is the companion data structure. The file system must know which blocks are free and which are allocated, and it must be able to allocate a block quickly (for a write) and free a block quickly (for a truncation or deletion). The **bitmap** — one bit per block, 0 for free, 1 for allocated — is the simplest and most common approach: allocation is a search for the first 1-bit (or, for finding contiguous blocks, the first run of 1-bits), and freeing is a single bit clear. The bitmap for a multi-terabyte file system can be megabytes — small enough to cache in memory, large enough that scanning it linearly is slow.

**Crash consistency** is the deepest challenge. A file-system operation (e.g., creating a file) involves multiple on-disk updates: write the inode to disk, write the directory entry, update the free-inode bitmap, update the free-block bitmap. If the system crashes between two of these writes, the on-disk state is inconsistent — a file may exist (its inode is allocated) but be unreachable (no directory entry points to it), or a block may be marked free but still contain data reachable from an inode. The **fsck** (file system check) utility — which scans the entire file system after a crash, detecting and repairing inconsistencies — was the standard approach from the 1970s through the 1990s, but its scanning time (proportional to file system size) became unacceptable for multi-terabyte systems.

The **journaling** approach — introduced in ext3 (2001), NTFS, and the Yggdrasil FS — solves the crash-consistency problem by borrowing the **write-ahead log** from databases. Before modifying the file system structures, the file system writes a **journal entry** — a description of the pending changes — to a special journal area on disk. After the journal entry is safely on disk (the commit), the file system applies the changes to the main structures (the checkpoint). If a crash occurs, the journal is replayed on recovery: any committed journal entries are applied; any incomplete entries are discarded. Journaling reduces crash recovery from O(size of file system) to O(size of journal) — a game-changer.

**Required Reading:**
- Remzi & Andrea Arpaci-Dusseau, *Operating Systems: Three Easy Pieces* (v1.10, 2040), chs. 40–42 ("File System Implementation," "FSCK and Journaling," "Log-Structured File Systems")
- Andrew S. Tanenbaum & Herbert Bos, *Modern Operating Systems* (5th ed., 2022/2039), ch. 4.4
- Mendel Rosenblum & John K. Ousterhout, "The Design and Implementation of a Log-Structured File System," *ACM TOCS* 10:1 (1992): 26–52
- Stephen C. Tweedie, "Journaling the Linux ext2fs File System," *Proceedings of LinuxExpo* (1998)
- The Yggdrasil Kernel: File System Internals Module (2040)

**Discussion Questions:**
1. Journaling solves crash consistency but imposes a write penalty (every update is written twice — once to the journal, once to the main structures). How do modern file systems (ext4, btrfs, ZFS) mitigate this penalty?
2. The inode pointer tree supports files up to terabytes, but the indirection imposes a performance cost — particularly for random access. How does the **extent** approach (used by ext4, NTFS, HFS+) address this?
3. Persistent memory (PMEM) blurs the line between storage and memory: it is byte-addressable, like DRAM, but persistent, like disk. How does this change the design of a file system — and do we still need inodes, block pointers, and journaling?

---

## Lecture 9: I/O Subsystems — Device Drivers, DMA, and the Block Layer

The I/O subsystem is the OS's interface to the physical world — keyboards, mice, displays, disks, networks, sensors, actuators. It is the most heterogeneous part of the OS, because the devices it manages are heterogeneous: a high-end NVMe SSD can sustain millions of IOPS, while a 2040 neural interface requires sub-millisecond latency for safety-critical signals. The I/O subsystem must abstract this diversity behind a uniform interface, while allowing performance-critical applications to bypass the abstraction when necessary.

The **device driver** is the kernel module that implements the abstraction for a specific device (or class of devices). It provides a standard interface to the rest of the kernel — typically, operations for open, read, write, ioctl (device-specific control), and close — and it translates these operations into the specific commands and protocols that the hardware expects. A device driver for a storage device translates read-block and write-block requests into NVMe or SCSI commands; a device driver for a network interface translates send-packet and receive-packet requests into DMA descriptors and interrupt handlers. Drivers are written in C (or, increasingly in 2040, in Rust for memory safety in the Linux kernel), and they run in kernel mode with full access to hardware — a trust model that makes driver bugs the leading cause of kernel crashes (the infamous Windows "blue screen of death").

**Direct Memory Access (DMA)** is the hardware capability that allows devices to transfer data directly to and from main memory, without involving the CPU for every byte. The CPU sets up a DMA transfer by writing a descriptor (source address, destination address, length) to the device's DMA controller; the device performs the transfer; and when done, it raises an interrupt. DMA frees the CPU for other work during I/O — crucial for high-throughput devices (SSDs, 100Gbps networks). The OS's I/O buffer management must account for DMA: buffers that will be read or written by a device must be in physical memory that is "DMA-able" (within the address range that the DMA controller can reach, and not paged out), and they must be aligned to cache-line boundaries to avoid data corruption from cache-coherency issues.

The **block I/O layer** in Linux is the subsystem that mediates between file systems (which issue read and write requests for logical blocks) and device drivers (which execute requests for physical sectors). It provides: **I/O scheduling** — reordering requests to minimise disk seek time (elevator algorithms: noop, deadline, CFQ, BFQ) or, in the 2040s for SSDs, to maximise parallelism; **merging** — combining adjacent requests into a single, larger request; and **caching** — the **page cache**, which stores recently read or written file data in memory, absorbing reads without touching the device and buffering writes for delayed (efficient) dispatch. The page cache is one of the largest and most performance-critical data structures in the kernel — in a server with 512GB of RAM, the page cache may consume 400GB, and its hit rate determines the system's I/O performance.

**Required Reading:**
- Remzi & Andrea Arpaci-Dusseau, *Operating Systems: Three Easy Pieces* (v1.10, 2040), chs. 36–37 ("I/O Devices," "Hard Disk Drives")
- Andrew S. Tanenbaum & Herbert Bos, *Modern Operating Systems* (5th ed., 2022/2039), ch. 5
- Robert Love, *Linux Kernel Development* (4th ed., 2039), chs. 6 ("Interrupts"), 14 ("The Block I/O Layer")
- Jonathan Corbet, Alessandro Rubini & Greg Kroah-Hartman, *Linux Device Drivers* (4th ed., 2039), chs. 1–3, 16
- The Yggdrasil Kernel: I/O Subsystem Documentation (2040)

**Discussion Questions:**
1. Device drivers run in kernel mode with full hardware access. Is this trust model sustainable — and how do microkernels and Rust-based drivers change the equation?
2. The I/O scheduler reorders requests for spinning disks — but SSDs have no seek time. What I/O scheduling strategies are appropriate for SSDs, and how do they differ from the classic elevator algorithms?
3. DMA bypasses the CPU — but it does not bypass the memory bus. How does DMA contention affect CPU performance, and what techniques (IOMMU, cache injection) mitigate it?

---

## Lecture 10: Inter-Process Communication — Pipes, Signals, Shared Memory, and Message Queues

Processes are isolated by design — one process cannot read or write another's memory. But processes need to communicate: the shell needs to pipe the output of `ls` to the input of `wc`; the database server needs to pass query results to the web server; the sensors in an autonomous vehicle need to stream data to the controller. **Inter-Process Communication (IPC)** is the set of mechanisms the OS provides for processes to exchange data and coordinate their actions, and the choice of IPC mechanism is one of the most consequential design decisions in a systems architecture.

**Pipes** are the simplest and most iconic IPC mechanism in Unix. A pipe is a unidirectional byte stream connecting the output of one process to the input of another. `pipe()` creates an anonymous pipe — returning two file descriptors, one for reading and one for writing — typically used between a parent and child after `fork()`. The shell's `|` operator is syntactic sugar for `pipe()` + `fork()` + `dup2()`. Pipes are simple, synchronous (the writer blocks when the pipe buffer is full; the reader blocks when the buffer is empty), and limited to parent-child or sibling relationships. **Named pipes (FIFOs)** extend the pipe concept to arbitrary processes by associating the pipe with a file-system entry — but they remain unidirectional and byte-stream-oriented.

**Signals** are the IPC mechanism for **notification** — asynchronous messages sent to a process to indicate an event: SIGINT (interrupt, Ctrl-C), SIGKILL (immediate termination), SIGSEGV (segmentation fault), SIGCHLD (child terminated). Signals are simple — a process can install a handler for most signals (except SIGKILL and SIGSTOP) — but they are also subtle: a signal can arrive at any point in the program's execution, including in the middle of a critical section, and the handler must be reentrant (safe to call while the program is already partially through a non-reentrant function). The tension between signals and threads (which thread receives the signal?) and the tension between signals and the async I/O models of 2040 have made signals one of the most debated parts of the Unix IPC suite.

**Shared memory** is the fastest IPC mechanism — the two processes map the same physical pages into their virtual address spaces, and they communicate by reading and writing shared variables. No kernel involvement is needed after the initial setup (the `shmget`/`shmat` or `mmap` calls) — but the programmer must provide synchronisation (mutexes, semaphores, condition variables) to avoid race conditions. Shared memory is the foundation of high-performance IPC in databases, scientific computing, and the Yggdrasil AI OS — and it is the mechanism underlying the POSIX shared-memory extensions and the `memfd_create` system call in Linux.

**Message queues** provide a middle ground: structured, asynchronous communication with explicit message boundaries. POSIX message queues (`mq_open`, `mq_send`, `mq_receive`) offer priority-ordered delivery and persistence (a message queue survives as long as the system is up, even if no process has it open). **Unix domain sockets** — sockets that use the file-system namespace instead of a network address — provide bidirectional, stream- or datagram-oriented communication between processes on the same machine, with the same API as TCP/IP sockets. In the 2040s, **gRPC** over Unix domain sockets is the dominant IPC mechanism for microservice architectures, combining structured data (Protocol Buffers), bidirectional streaming, and strong typing.

**Required Reading:**
- Remzi & Andrea Arpaci-Dusseau, *Operating Systems: Three Easy Pieces* (v1.10, 2040), chs. 29 ("Semaphores"), 30–32 (Concurrency topics)
- W. Richard Stevens & Stephen A. Rago, *Advanced Programming in the UNIX Environment* (3rd ed., 2013/2039), chs. 15–17
- Robert Love, *Linux System Programming* (2nd ed., 2039), chs. 6–8
- The Yggdrasil Kernel: IPC Module Documentation (2040)

**Discussion Questions:**
1. Shared memory is the fastest IPC mechanism — but it requires synchronisation. Is the speed advantage worth the complexity, or should systems prefer message-passing (which is easier to reason about) and accept the overhead?
2. Signals can arrive at any point in execution. What are the implications for library code — and how does the `sig_atomic_t` type and the `async-signal-safe` function list address them?
3. Unix domain sockets provide the network API for local IPC. What advantages does this uniformity (network and local IPC use the same API) offer — and what are the drawbacks?

---

## Lecture 11: Security and Isolation — Capabilities, Namespaces, and Containers

The OS is a security boundary. It must ensure that a process cannot access resources it has not been granted — other processes' memory, files it has not been permitted to open, network ports it has not been authorised to bind. The security mechanisms of the OS — access control, capabilities, namespaces, and mandatory access control frameworks — have evolved from simple user/group/other permission bits (the Unix model) to the fine-grained, dynamic, policy-driven frameworks that underpin the cloud infrastructure of the 2040s.

The **Unix permission model** — each file has an owner, a group, and a 9-bit permission mask (read, write, execute for owner, group, and others) — is simple, understandable, and insufficient. It cannot express: "allow this process to bind to port 80, but only if it is running as root" (the reason for the `setuid` mechanism, which is itself a security risk); "allow this backup process to read all files, regardless of their permissions" (the reason for **capabilities**); "confine this web server so that it cannot access any file outside /var/www, even if it is compromised" (the reason for **namespaces** and **containers**).

**Capabilities** — introduced in the POSIX 1003.1e draft (withdrawn, but implemented in Linux) — are fine-grained tokens that grant a process the right to perform a specific privileged operation: CAP_NET_BIND_SERVICE (bind to ports below 1024), CAP_SYS_ADMIN (a catch-all for administrative operations), CAP_SYS_PTRACE (trace other processes). A process's capability set can be reduced from the full set inherited at `exec()` — the principle of **least privilege**: a process should have only the capabilities it needs, and no more. Capabilities are a significant improvement over the all-or-nothing root model, but they are complex: the Linux kernel defines over 40 capabilities, and their interactions are subtle.

**Namespaces** — introduced in Linux 2.6.24 (2008) and refined through the 2010s — are the foundation of **containerisation** (Docker, LXC, Kubernetes). A namespace restricts a process's view of a system resource: the **PID namespace** isolates process IDs (a process in a container sees only processes in the same container); the **mount namespace** isolates the file-system mount points; the **network namespace** isolates network interfaces, IP addresses, and routing tables; the **UTS namespace** isolates the hostname and domain name; the **user namespace** maps UIDs inside the container to different UIDs outside (so root in the container is not root on the host). Namespaces are the OS-level mechanism that enables containers to be lightweight (they share the host kernel) while providing strong isolation.

**Mandatory Access Control (MAC)** frameworks — **SELinux** (NSA, 2000), **AppArmor** (Immunix/Novell, 2001), and the Yggdrasil **Runahlið** (Rune-Gate) framework — add a second layer of access control beyond the Unix permissions. MAC policies are expressed in terms of **labels** attached to subjects (processes) and objects (files, sockets, devices), and the kernel enforces rules of the form "a subject with label S may perform operation O on an object with label L only if the policy permits it." MAC provides defence in depth: even if a process is compromised and running as root, the MAC policy can prevent it from accessing sensitive files or network services.

**Required Reading:**
- Remzi & Andrea Arpaci-Dusseau, *Operating Systems: Three Easy Pieces* (v1.10, 2040), ch. 39 ("Security")
- Robert Love, *Linux Kernel Development* (4th ed., 2039), ch. 19 ("Portability")
- Michael Kerrisk, *The Linux Programming Interface* (2010/2039), chs. 38–39
- Docker Security Documentation (docs.docker.com/engine/security)
- The Yggdrasil Kernel: Security Module Documentation — Runahlið Framework (2040)

**Discussion Questions:**
1. The Unix permission model has been criticised as insufficient since the 1980s, yet it persists. Why — and is its simplicity a virtue that outweighs its lack of expressiveness for many use cases?
2. Containers share the host kernel; virtual machines have their own kernel. Under what circumstances is container isolation sufficient — and when must we fall back to full virtualisation for security?
3. SELinux provides powerful, fine-grained access control — but it is notoriously difficult to configure. How can we make MAC policies easier to write and verify — and what role can formal methods play?

---

## Lecture 12: The Operating System in the Age of AI — Specialised Kernels, Unikernels, and the OS as Platform

The final lecture surveys the operating system landscape of 2040 — not as a settled discipline but as a field in ferment. The assumptions that shaped the classic OS — a single, general-purpose computer, running multiple interactive users, with a spinning disk — have been eroded by the rise of the cloud (thousands of virtual machines per physical server), the proliferation of specialised hardware (GPUs, TPUs, NPUs, FPGAs), and the emergence of AI workloads that demand latencies and throughputs that the classic OS stack struggles to deliver. The OS of 2040 is not a monolith but an ecosystem: the general-purpose Linux kernel remains the default, but it is increasingly complemented (and sometimes replaced) by specialised kernels and unikernels optimised for specific workloads.

**Specialised kernels for AI** have emerged as a significant trend. Training a large language model (the 2040 equivalent of GPT-4, but far larger) involves coordinating thousands of GPUs across dozens of nodes, with communication (all-reduce, parameter-server) that must be scheduled as carefully as computation. The Linux kernel's general-purpose scheduler and network stack are not optimised for this workload — they context-switch when they should not, they buffer when they should pass through, and they impose overheads that, at the scale of 10,000 GPUs, translate into millions of dollars in wasted compute. In response, systems like the **Yggdrasil AI Scheduler** (a kernel module that bypasses the standard scheduler for AI workloads, pinning processes to dedicated cores and coordinating communication with GPU DMA) and the **Neural OS** (a research kernel from Tsinghua University that treats the GPU as a first-class compute resource, not a peripheral) are exploring what an OS designed for AI would look like.

**Unikernels** push specialisation to its logical extreme. A unikernel compiles the application and the kernel into a single address space, running in a single privileged mode — no user/kernel boundary, no system calls, no context switches between the application and the kernel. The result is extremely fast (system calls become function calls), extremely small (a unikernel for a web server can be a few hundred kilobytes), and extremely specialised (the application gets exactly the kernel services it needs, and no more). Unikernels, pioneered by MirageOS (2010), are increasingly used in the 2040s for microservices that demand the lowest possible latency and the highest possible density — and the Yggdrasil Kernel supports a unikernel mode for student projects.

The **OS as platform** — the OS not as a fixed system but as a programmable substrate — is the most profound trend. The Linux kernel's **eBPF** (extended Berkeley Packet Filter) allows user programs to inject sandboxed programs into the kernel that execute at various hook points (networking, tracing, security enforcement) — customising the OS's behaviour without changing its source code. eBPF has become, by 2040, the standard mechanism for observability (the Cilium networking stack, the Falcon tracing tool), for security (eBPF-based intrusion detection), and for performance optimisation (dynamic tuning of scheduler parameters based on workload). The OS is becoming **programmable** — and the programmer who understands the kernel not just as a consumer but as an extension point has a superpower.

**Required Reading:**
- Anil Madhavapeddy & David J. Scott, "Unikernels: The Rise of the Virtual Library Operating System," *Communications of the ACM* 57:1 (2014): 61–69
- Brendan Gregg, *BPF Performance Tools* (2019/2039), chs. 1–3
- Daniel Borkmann & Alexei Starovoitov, "eBPF: The Next Generation of Programmable Datapath," *Linux Plumbers Conference* (2023/2040)
- The Yggdrasil AI Scheduler Documentation (2040)
- The Neural OS Research Group, Tsinghua University, *POSH: A Programmable OS for Heterogeneous Hardware* (2039)

**Discussion Questions:**
1. Unikernels eliminate the user/kernel boundary — but they also eliminate process isolation and the protection it provides. When is this trade-off acceptable — and what alternative protection mechanisms (e.g., hardware memory protection, formal verification) might replace the kernel boundary?
2. eBPF allows users to inject code into the kernel. What are the security implications — and how does the eBPF verifier (which checks that eBPF programs terminate and do not access out-of-bounds memory) provide safety?
3. The OS for an AI training cluster must manage GPUs, not just CPUs. What abstractions does the OS need to provide for GPUs — an "AI process," a "tensor address space," a "GPU scheduler" — and how do they differ from the classic CPU abstractions?

---

## Final Examination Preparation

The final examination for CS202 consists of a three-hour written examination (50% of the final grade), a Yggdrasil Kernel extension project (40%), and a laboratory assessment (10%). The written examination requires you to answer four questions from a choice of eight. The kernel extension project requires you to implement a novel OS feature in the Yggdrasil Kernel — e.g., a new scheduling policy, a page-replacement algorithm, a file-system snapshot mechanism, or a security module — and to write a design document explaining your choices, the implementation, and the performance evaluation.

### Sample Examination Questions

1. **(Process Management)** A process calls `fork()`. Trace the kernel's actions from the system call entry through the creation of the child process's PCB, the copying (or sharing) of the address space, and the return to user space. Explain: (a) why `fork()` returns different values to parent and child, (b) how copy-on-write makes `fork()` efficient, and (c) what happens if the child calls `exec()` immediately after `fork()` — and how the kernel optimises this common case.

2. **(Scheduling)** Compare the Linux CFS (Completely Fair Scheduler) with the classic MLFQ (Multi-Level Feedback Queue). (a) How does each achieve fairness? (b) How does each handle a mix of I/O-bound and CPU-bound threads? (c) CFS uses virtual runtime; MLFQ uses priority queues. What are the advantages and disadvantages of each approach when the number of threads reaches tens of thousands?

3. **(Virtual Memory)** A process on a 48-bit x86-64 system accesses the virtual address 0x00007F4A3B2C1000. The page size is 4KB, and the page table has 4 levels. (a) Decompose this address into the four table indices and the offset. (b) Explain how the MMU traverses the page table to produce the physical address. (c) If the TLB hits, the page-table walk is avoided. What is the performance difference between a TLB hit and a TLB miss — and how does the size of the TLB (e.g., 1536 entries on a modern x86-64 core) affect the working-set size that an application can access without incurring TLB misses?

4. **(Page Replacement)** Describe the clock (second-chance) page-replacement algorithm. (a) Under what reference patterns does the clock algorithm perform well — and under what patterns does it perform poorly? (b) How does the algorithm relate to LRU — and why is it preferred over exact LRU in practice? (c) If the system is thrashing, the clock algorithm will continually sweep pages with the reference bit set — a high overhead. What modifications (page-cleaning daemon, working-set tracking) does Linux add to handle this?

5. **(File Systems)** A file system uses journaling to ensure crash consistency. (a) Describe the write-ahead logging protocol: what is written to the journal, when is the commit record written, and how is the journal replayed on recovery? (b) Compare journaling with the log-structured approach — where the entire file system is the log, and the "checkpoint" is the mapping from logical blocks to log positions. What are the strengths and weaknesses of each?

6. **(I/O and DMA)** A program issues a `read()` for 64KB from an NVMe SSD. Trace the path of this request from the system call through the VFS, the page cache, the block layer, and the NVMe driver. Explain: (a) when DMA is set up, (b) how the interrupt signals completion, and (c) how the data gets from the kernel buffer to the user buffer — and what "zero-copy I/O" (e.g., `sendfile()`) does differently.

7. **(IPC)** Compare pipes, shared memory, and Unix domain sockets as IPC mechanisms. For each, describe: (a) the API, (b) the performance characteristics (throughput, latency), (c) the synchronisation model (blocking, non-blocking), and (d) a typical use case. Then, propose a scenario where you would choose each mechanism — and justify your choice.

8. **(Integrative Essay — OS Philosophy)** The operating system has been described as both a "resource manager" and an "extended machine" (virtual machine). Drawing on material from across the course, trace how these two roles have shaped the design of the major OS subsystems: process management, memory management, file systems, and I/O. How do these roles come into tension — and how have 2040-era developments (heterogeneous hardware, unikernels, AI workloads, eBPF) shifted the balance? Your essay should demonstrate both technical depth and historical perspective.

---

## Course Summary and Learning Outcomes

By the end of CS202, students will be able to:
1. Describe the architecture of a modern OS kernel and explain the roles and interactions of the major subsystems
2. Implement and analyse process scheduling algorithms — FCFS, SJF, Round Robin, MLFQ, and the Linux CFS
3. Explain virtual memory mechanisms — paging, page tables, TLB, and page-replacement algorithms — and analyse their performance
4. Design and implement file system data structures — inodes, block pointers, free-space bitmaps, directories — with crash consistency via journaling
5. Write and test a device driver for a simple block or character device in the Yggdrasil Kernel
6. Compare and evaluate IPC mechanisms — pipes, shared memory, message queues, Unix domain sockets — for a given application scenario
7. Apply OS security mechanisms — capabilities, namespaces, MAC frameworks — to isolate processes and enforce least privilege
8. Critique and extend the OS for specialised workloads (AI, high-frequency trading, embedded systems), drawing on unikernel and eBPF paradigms

CS202 is a core requirement for the Computer Science degree and a prerequisite for CS302 (Computer Networking), CS304 (Distributed Systems), and the AI OS Design programme. The operating system is the foundation on which every other software system is built; mastery of CS202 is mastery of the ground beneath all of computing.
