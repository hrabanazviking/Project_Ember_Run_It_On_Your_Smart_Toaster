# IT201: System Administration (Linux + Windows)
## Bachelor of Science in Information Technology — University of Yggdrasil, 2040

**Credits:** 4
**Description:** A dual-platform deep dive into modern system administration, covering Linux and Windows Server architectures, automation, security hardening, performance tuning, and the 2040 landscape of AI-augmented operations.

**Prerequisites:** IT101 (Introduction to Information Technology)

**Instructor:** Prof. Björn Hǫggvason, Department of Information Technology

**Course Philosophy:** The sysadmin is the steward of digital infrastructure — the person who ensures the servers boot, the databases serve, the networks route, and the users work. This course treats system administration not as a collection of recipes but as a discipline of systematic thinking, debugging, and care. By learning both Linux and Windows — the two dominant server platforms of 2040 — students develop the conceptual flexibility to manage any system.

---

## Lectures

---

### Lecture 1: The Philosophy of System Administration — Stewardship, Discipline, and the Ops Mindset

**Course:** IT201 — System Administration (Linux + Windows)
**Degree:** Bachelor of Science in Information Technology, 2040

---

#### Overview

System administration is more than running commands — it is a practice of stewardship over systems that people depend on for work, health, communication, and safety. This lecture establishes the intellectual foundations of system administration: the operational mindset (how ops differs from development), the ethics of infrastructure stewardship, the discipline of change management, and the historical evolution from manual administration to the AI-augmented operations of 2040.

#### Key Topics

- **Defining System Administration:** System administration encompasses the installation, configuration, maintenance, monitoring, and security of computer systems. The sysadmin's work spans hardware (servers, storage, networking), operating systems (Linux, Windows Server), middleware (databases, web servers, message queues), and applications. The core competency is not knowing every command but knowing how to diagnose, how to learn, and how to maintain composure under pressure.
- **The Ops Mindset vs. The Dev Mindset:** Development and operations embody different values: developers optimize for change (new features, refactoring), while operators optimize for stability (uptime, predictability, recoverability). These values are in tension: every change is an opportunity for failure; every stability measure is an impediment to change. The DevOps movement (2010s) and SRE (Site Reliability Engineering, pioneered at Google) attempt to reconcile this tension through shared responsibility, automation, and error budgets. By 2040, the ops/dev distinction has blurred — platform engineering teams build internal platforms that make operations accessible to developers — but the ops mindset (paranoid, systematic, prepared) remains essential.
- **Ethics of Infrastructure Stewardship:** Sysadmins hold extraordinary access — root on Linux, Domain Admin on Windows. With that access comes ethical responsibility: (1) confidentiality — respecting user data; (2) integrity — not modifying systems for personal benefit; (3) availability — maintaining service for users who depend on it; (4) transparency — documenting actions so colleagues can understand what was done and why. The **IT Professional Ethics Code (2035)** codifies these responsibilities, including a duty to report unethical directives and to maintain competence through continuing education.
- **Change Management and the Blameless Postmortem:** Change is the primary source of outages. Effective sysadmins practice disciplined change management: all changes are planned, tested in staging, reviewed by peers, applied during maintenance windows, and documented. When outages do occur (and they will), the response is a blameless postmortem: a structured analysis of what happened, why, how it was detected, how it was resolved, and what will prevent recurrence — without blaming individuals. The **UoY Infrastructure Incident Database** (public, anonymized) contains over 10,000 postmortems analyzed by researchers to identify systemic patterns.

#### Lecture Notes

The history of system administration mirrors the history of computing. In the mainframe era, operators managed physical machines in raised-floor data centers. In the client-server era, sysadmins managed fleets of servers, often with manual processes (the "pets" model — each server is unique and cared for individually). In the cloud era, infrastructure became "cattle" — disposable, replaceable, managed via APIs. By 2040, the dominant model is the **self-managing infrastructure** — systems that monitor, heal, scale, and optimize themselves, with human sysadmins serving as governors rather than operators. The sysadmin of 2040 writes policies ("maintain 99.99% availability, cost under $X/month, latency under Yms"), and AI orchestration layers implement those policies across thousands of nodes.

Yet the fundamentals endure: understanding the kernel, the filesystem, the network stack, and the security model is not optional. When the AI makes a decision you don't understand, or when the self-healing system fails to heal, you must be able to go to the console and diagnose the problem yourself.

#### Required Reading

- Limoncelli, T., Hogan, C., & Chalup, S. (2035). *The Practice of System and Network Administration* (4th ed.). Addison-Wesley.
- Beyer, B., Jones, C., Petoff, J., & Murphy, N. R. (2032). *Site Reliability Engineering* (3rd ed.). O'Reilly Media.
- UoY Ethics Board. (2035). *IT Professional Ethics Code*.
- UoY Infrastructure Research Group. (2039). *10,000 Postmortems: What System Failures Teach Us*.

#### Discussion Questions

1. A sysadmin discovers that their employer's system is being used to surveil political dissidents. The employer says it's legal under local law. What should the sysadmin do? How do professional ethics guide this decision?
2. "Infrastructure as cattle, not pets" treats servers as disposable. But some systems (legacy databases, specialized hardware) resist disposability. How should organizations handle "cattle that became pets"?
3. If AI manages 95% of operational decisions, what skills does the human sysadmin of 2040 need that AI cannot provide? Is the sysadmin role shrinking or evolving?

#### Practice Problems

- Research a major outage (e.g., Facebook 2021, AWS 2017, Cloudflare 2023). Write a blameless postmortem following the UoY template: timeline, root cause, detection, resolution, impact, and prevention.
- Interview a practicing sysadmin (or research a published interview). What keeps them up at night? What tool or practice most improved their quality of life?
- Diagram the change management process for a typical enterprise in 2040. Identify every approval gate, testing step, and rollback mechanism.

---

### Lecture 2: Linux Architecture — Kernel, Processes, and the Extended Filesystem

**Course:** IT201 — System Administration (Linux + Windows)
**Degree:** Bachelor of Science in Information Technology, 2040

---

#### Overview

Linux is the dominant server operating system of 2040, running on over 85% of cloud instances and embedded in everything from Android devices to supercomputers. Understanding Linux architecture — the kernel, process model, memory management, and filesystem hierarchy — is foundational to system administration. This lecture examines the Linux kernel's design, the evolution of Linux distributions, and the 2040 kernel features that define modern server operations.

#### Key Topics

- **The Linux Kernel:** The kernel is the core of the operating system — the privileged software that manages hardware, schedules processes, allocates memory, and enforces security boundaries. Linux is a monolithic kernel (all core services run in kernel space) with a modular design (kernel modules can be loaded and unloaded dynamically). Key subsystems: (1) **Process Scheduler** — the Completely Fair Scheduler (CFS) replaced by EEVDF (Earliest Eligible Virtual Deadline First) in 2023, providing fair CPU allocation with bounded latency; (2) **Memory Manager** — virtual memory with demand paging, transparent huge pages, and by 2040, hardware-assisted memory compression for improved density; (3) **VFS (Virtual File System)** — an abstraction layer enabling Linux to support dozens of filesystem types (ext4, XFS, Btrfs, ZFS, and the 2040-native LFS) through a common interface; (4) **Network Stack** — full TCP/IP implementation with eBPF (extended Berkeley Packet Filter) enabling programmable, high-performance packet processing without kernel modification.
- **Processes, Threads, and Namespaces:** A process is a running program with its own virtual memory space. Linux provides: (1) **fork()/exec()** — the Unix process creation model; (2) **clone()** — creates threads sharing memory or namespaces for containers; (3) **cgroups (Control Groups)** — limit and account for resource usage per process group, foundational to containerization; (4) **namespaces** — isolate process views of system resources (PID, network, mount, user, etc.), the basis of Linux containers (Docker, Podman, LXC). By 2040, the kernel supports over 20 namespace types, including new namespaces for GPU, NPU (AI accelerators), and confidential computing enclaves.
- **The Linux Filesystem Hierarchy:** The Filesystem Hierarchy Standard (FHS) defines the directory structure: `/bin` (essential binaries), `/etc` (configuration), `/var` (variable data — logs, caches, databases), `/home` (user directories), `/tmp` (temporary files), `/proc` (process information pseudo-filesystem), `/sys` (kernel and device information). By 2040, `/run` (runtime variable data) and `/opt` (add-on software) are standardized across all major distributions, and `/sys/ai` exposes AI accelerator telemetry.
- **Linux Distributions in 2040:** The distribution landscape has consolidated around several major families: (1) **Debian/Ubuntu** — dominant in cloud and education, valued for stability and package ecosystem; (2) **RHEL/Fedora/CentOS Stream** — dominant in enterprise, valued for certification and support; (3) **SUSE/openSUSE** — strong in European enterprise and SAP environments; (4) **Arch/Gentoo** — rolling-release and source-based distributions, popular with advanced users; (5) **Immutable distributions** (Fedora Silverblue, openSUSE MicroOS, Ubuntu Core) — read-only root filesystem with atomic updates, the 2040 standard for security-sensitive deployments.

#### Lecture Notes

Linux's success is partly technical and partly social. The GPL (GNU General Public License) created a legal framework where contributions benefit everyone, and the decentralized, meritocratic development model — thousands of developers from competing companies collaborating on shared infrastructure — has proven remarkably resilient. The Linux kernel in 2040 contains over 40 million lines of code, contributed by over 25,000 developers from 2,000+ companies.

A defining kernel development of the 2030s was the **eBPF revolution**. eBPF allows user-space programs to load sandboxed programs into the kernel that execute at specific hook points — networking (XDP, TC), tracing (kprobes, tracepoints), security (LSM hooks), and more. By 2040, eBPF has largely replaced kernel modules for new functionality: networking, observability, security monitoring, and even filesystem implementations are eBPF-based. The advantage: eBPF programs are verified for safety before loading, eliminating the kernel panics that plagued traditional kernel modules.

The **Confidential Computing** extensions — Intel TDX, AMD SEV-SNP, ARM CCA — are fully integrated into the 2040 Linux kernel. These enable running VMs where memory is encrypted even from the hypervisor, allowing multiple organizations to collaborate on sensitive data without trusting the cloud provider. The kernel's memory manager has been extended with confidential memory regions, and the scheduler includes confidential-computing-aware placement.

#### Required Reading

- Kerrisk, M. (2035). *The Linux Programming Interface* (3rd ed.). No Starch Press.
- Love, R. (2038). *Linux Kernel Development* (5th ed.). Addison-Wesley.
- IETF/CNCF. (2039). *eBPF: The Universal In-Kernel Virtual Machine — Architecture and Applications*.
- UoY Systems Lab. (2040). *Confidential Computing on Linux: Architecture and Administration*.

#### Discussion Questions

1. Linux is a monolithic kernel, while MINIX and QNX use microkernels. What are the trade-offs? Does the eBPF revolution give Linux microkernel-like extensibility without microkernel-like overhead?
2. The GPL ensures Linux remains open source, but most cloud services are built on Linux without contributing back. Is the cloud model parasitic on open source, or is it a legitimate use that the GPL adequately addresses?
3. Immutable Linux distributions trade flexibility for security. What administrative tasks become harder on an immutable system? Are the security gains worth the operational cost?

#### Practice Problems

- Boot a Linux system and trace the boot process from UEFI to login prompt. Identify the bootloader (GRUB), kernel initialization, initramfs, and init system (systemd). Write a 500-word explanation.
- Use `strace` to trace the system calls of a running process. Identify the most frequent syscalls. What do they reveal about the program's behavior?
- Configure cgroups to limit a process's CPU and memory usage. Verify the limits with `systemd-cgtop` or direct cgroup inspection.

---

### Lecture 3: Windows Server Architecture — Registry, Services, and Active Directory

**Course:** IT201 — System Administration (Linux + Windows)
**Degree:** Bachelor of Science in Information Technology, 2040

---

#### Overview

Microsoft Windows Server powers a substantial fraction of enterprise infrastructure — Active Directory domains, Exchange email, SQL Server databases, and .NET application servers. By 2040, Windows Server has evolved significantly: the NT kernel has absorbed Linux compatibility (WSL 3 runs unmodified Linux binaries natively on the NT kernel), Active Directory federates with cloud identity providers, and Windows Admin Center provides a modern web-based management interface. This lecture surveys Windows Server architecture, contrasting it with Linux to build dual-platform fluency.

#### Key Topics

- **The Windows NT Kernel:** Windows NT (New Technology) is a hybrid kernel — combining aspects of microkernel and monolithic design. Key components: (1) **Executive** — the upper layer of the kernel, providing object management, process/thread management, memory management, I/O, and security; (2) **Kernel** — the lower layer, handling thread scheduling, interrupt dispatching, and multiprocessor synchronization; (3) **Hardware Abstraction Layer (HAL)** — abstracts hardware differences for portability. By 2040, the NT kernel supports over 8,192 logical processors and exabytes of memory, reflecting the massive scale of modern servers. The scheduler uses a priority-based preemptive model with CPU sets for NUMA-aware placement.
- **The Registry:** The Windows Registry is a hierarchical database storing system and application configuration. Unlike Linux's file-based configuration (`/etc`), the Registry is a binary database organized into hives: HKEY_LOCAL_MACHINE (system-wide), HKEY_CURRENT_USER (per-user), HKEY_CLASSES_ROOT (file associations and COM registration), HKEY_CURRENT_CONFIG (hardware profile). By 2040, the Registry is versioned (changes are logged and reversible), access-controlled at the key level, and replicated across domain controllers for Group Policy.
- **Windows Services:** Windows services are background processes managed by the Service Control Manager (SCM). Services have defined start types (Automatic, Manual, Disabled), recovery actions (restart, run program, reboot), and can run under specific user accounts (LocalSystem, NetworkService, or domain accounts). By 2040, Windows services support systemd-style dependency ordering, socket activation, and containerized service isolation via Windows Containers and Hyper-V isolation.
- **Active Directory (AD):** AD is Microsoft's directory service — a distributed database of users, groups, computers, and policies. Key concepts: (1) **Domain** — a security boundary managed by Domain Controllers (DCs); (2) **Organizational Units (OUs)** — containers for grouping objects and applying Group Policy; (3) **Group Policy Objects (GPOs)** — collections of policy settings applied to users and computers; (4) **LDAP** — the Lightweight Directory Access Protocol used to query AD; (5) **Kerberos** — the authentication protocol, using ticket-granting tickets and service tickets. By 2040, AD has evolved into **Entra ID Domain Services** (cloud-integrated, hybrid identity) — organizations can extend on-premises AD to the cloud, federate with external identity providers, and manage identity across Windows, Linux, and macOS systems from a single console.

#### Lecture Notes

Windows and Linux have converged in important ways by 2040. **WSL 3 (Windows Subsystem for Linux)** runs unmodified Linux binaries natively on the NT kernel — not emulation, not a VM, but Linux system calls implemented by the NT kernel. A Linux ELF binary can run on Windows Server by calling Linux syscalls that are directly handled by the NT kernel's Linux-compatibility layer. This means Linux server software — nginx, PostgreSQL, Redis — can run on Windows Server with near-native performance and no modification.

Conversely, **PowerShell 9** (2040) runs natively on Linux, providing a unified scripting and automation platform across both operating systems. PowerShell's object-pipeline model (passing structured objects between commands, rather than text streams) has proven valuable for automation, and by 2040, PowerShell is the preferred scripting language for cross-platform system administration, with modules for managing Linux, Windows, cloud resources, and Kubernetes clusters.

The 2040 sysadmin must be fluent in both platforms — not just because organizations run both, but because the conceptual flexibility gained from understanding two different operating system philosophies makes you a better administrator on either platform.

#### Required Reading

- Russinovich, M., Solomon, D., Ionescu, A., & Yosifovich, P. (2038). *Windows Internals* (9th ed.). Microsoft Press.
- Microsoft. (2039). *Windows Server 2040 Administration Guide*.
- Desmond, B., Richards, J., Allen, R., & Lowe-Norris, A. G. (2035). *Active Directory* (7th ed.). O'Reilly Media.
- UoY Cross-Platform Lab. (2040). *Linux and Windows Convergence: Administration in the Dual-Platform Era*.

#### Discussion Questions

1. The Windows Registry is a single binary database; Linux uses thousands of text files in `/etc`. Which model is better for administration, automation, and disaster recovery? Does the Registry's centralized design justify its opacity?
2. Active Directory provides integrated identity, policy, and management for Windows domains. Linux environments typically assemble equivalent functionality from LDAP, Kerberos, SSSD, and configuration management tools. Is Windows' integrated approach better, or does Linux's composability offer advantages?
3. WSL 3 allows Linux binaries to run on Windows. Does this represent a victory for Linux (its software runs everywhere) or a defeat (its platform is absorbed into Windows)?

#### Practice Problems

- Explore the Windows Registry using `regedit` or PowerShell. Locate the TCP/IP configuration, installed software list, and service definitions. Compare to the equivalent locations in Linux `/etc`.
- Create an Active Directory domain with two domain controllers, an organizational unit, and a group policy that enforces password complexity. Join a Windows client to the domain and verify policy application.
- Use PowerShell to query WMI (Windows Management Instrumentation) for system information: running processes, disk configuration, network adapters, and installed updates. Write a script that generates a system inventory report.

---

### Lecture 4: User and Group Management Across Platforms

**Course:** IT201 — System Administration (Linux + Windows)
**Degree:** Bachelor of Science in Information Technology, 2040

---

#### Overview

User and group management is the foundation of system security — controlling who can access what, with what privileges, and under what conditions. This lecture surveys identity management on Linux (local users/groups, PAM, NSS, SSSD, LDAP) and Windows (local SAM, Active Directory, Entra ID), emphasizing the principles that transcend platform: principle of least privilege, separation of duties, and auditable access control.

#### Key Topics

- **Linux Users and Groups:** Linux identifies users by UID (User ID) and groups by GID (Group ID). User accounts are defined in `/etc/passwd` (username, UID, GID, home directory, shell) with hashed passwords stored in `/etc/shadow` (readable only by root). Groups are defined in `/etc/group`. By 2040, Linux supports: (1) **subordinate UIDs/GIDs** — enabling unprivileged users to create container namespaces with their own UID/GID mappings; (2) **systemd-homed** — portable, encrypted home directories that can be moved between machines; (3) **FIDO2/WebAuthn** — hardware security keys for local and SSH authentication.
- **PAM (Pluggable Authentication Modules):** PAM is the authentication framework that decouples applications from authentication mechanisms. PAM modules stack — you can require password AND hardware token, or password OR biometric, or any combination. Common modules: `pam_unix` (traditional password), `pam_sss` (SSSD integration with LDAP/AD), `pam_faillock` (account lockout after failed attempts), `pam_u2f` (FIDO2 hardware tokens). By 2040, PAM supports: (1) continuous authentication — re-verify identity periodically during a session; (2) risk-based authentication — require stronger authentication when behavior deviates from baseline; (3) confidential computing attestation — verify that the system's TEE state is valid before authenticating.
- **Windows Users and Groups:** Windows identifies users and groups by Security Identifiers (SIDs) — globally unique strings like `S-1-5-21-...-500` (the built-in Administrator). Local accounts are stored in the SAM (Security Account Manager) hive; domain accounts are stored in Active Directory. Windows supports: (1) **Built-in groups** — Administrators, Users, Guests, Backup Operators, etc., with predefined rights; (2) **Group nesting** — groups can contain other groups, enabling hierarchical permission models; (3) **Managed Service Accounts (MSAs)** — automatically-managed service accounts with rotating passwords; (4) **Privileged Access Management (PAM)** — just-in-time (JIT) privileged access, where admin rights are granted temporarily and audited.
- **Centralized Identity — LDAP, Kerberos, SSSD:** In Linux environments, centralized identity is commonly implemented with: (1) **OpenLDAP/389 Directory Server** — LDAP directory storing users, groups, and their attributes; (2) **Kerberos** — authentication protocol providing single sign-on via tickets; (3) **SSSD (System Security Services Daemon)** — client-side daemon that caches credentials and provides offline authentication. By 2040, identity federation via SAML, OAuth 2.1, and OpenID Connect has largely replaced direct LDAP authentication for web applications, though LDAP remains the backend for many identity providers.

#### Lecture Notes

The 2040 identity landscape is dominated by the tension between centralized and decentralized identity. Centralized identity (AD, Entra ID, Okta) provides convenience and manageability but concentrates power. Decentralized identity (DIDs, Verifiable Credentials) distributes control but adds complexity. The emerging hybrid model is **federated identity with self-sovereign credentials**: organizations manage their employees' identities centrally, but credentials (degrees, certifications, professional licenses) are issued as VCs that the individual controls and presents across organizational boundaries.

A key 2040 development is **identity threat detection**. AI models analyze authentication patterns across an organization — unusual login times, impossible travel (Tokyo login followed by New York login 10 minutes later), privilege escalation patterns — and flag anomalies for investigation. The **UoY Identity Lab's 2040 Threat Report** found that AI-based detection catches 94% of credential-based attacks before damage occurs, compared to 47% for rule-based detection.

#### Required Reading

- UoY Systems Lab. (2039). *Linux Identity Management: PAM, SSSD, and the 2040 Stack*.
- Microsoft. (2040). *Entra ID: Hybrid Identity Architecture Guide*.
- W3C. (2035). *Decentralized Identifiers (DIDs) v1.1* and *Verifiable Credentials v2.0*.
- UoY Identity Lab. (2040). *Identity Threat Detection: AI and Behavioral Analytics*.

#### Discussion Questions

1. Centralized identity (Active Directory) simplifies management but creates a single point of failure and control. Decentralized identity (DIDs, VCs) distributes control but complicates management. Which approach is appropriate for which contexts?
2. Risk-based authentication requires collecting behavioral data (typing patterns, location, device fingerprinting) to assess risk. Does the security benefit justify the privacy cost? Where should the line be drawn?
3. The `root` account on Linux and `Administrator` on Windows have unlimited power. Should operating systems move toward capability-based security where no single account has all privileges, or is a superuser account a necessary safety valve?

#### Practice Problems

- Configure PAM on a Linux system to require: password + FIDO2 hardware token for SSH authentication. Test the configuration and verify that both factors are required.
- Create a complex Active Directory group structure: department groups nested into role groups, with resource groups granting access to file shares. Use `dsacls` or PowerShell to audit effective permissions.
- Implement SSSD to authenticate Linux users against an LDAP directory. Configure offline credential caching and test authentication when the LDAP server is unreachable.

---

### Lecture 5: Storage Management — File Systems, RAID, LVM, and the 2040 Storage Stack

**Course:** IT201 — System Administration (Linux + Windows)
**Degree:** Bachelor of Science in Information Technology, 2040

---

#### Overview

Storage is where data lives — and data is what gives systems their value. This lecture surveys storage management across Linux and Windows: filesystem types and their trade-offs, RAID configurations for redundancy and performance, logical volume management for flexibility, and the 2040 storage technologies (NVMe-oF, computational storage, zoned storage) that define modern infrastructure.

#### Key Topics

- **Filesystem Fundamentals:** A filesystem organizes data on storage devices, providing: named files, hierarchical directories, metadata (permissions, timestamps, ownership), and efficient allocation of blocks. Linux filesystems in 2040: (1) **ext4** — the stable workhorse, supported everywhere, limited to 1 exabyte volumes; (2) **XFS** — high-performance for large files, default on RHEL; (3) **Btrfs** — copy-on-write, snapshots, compression, integrated RAID, self-healing checksums; (4) **ZFS** — originally from Solaris, now native on Linux, offering pooled storage, snapshots, compression, deduplication, and end-to-end checksums; (5) **LFS (Log-structured File System 2040)** — designed for zoned storage and SMR drives, optimizing for sequential writes. Windows filesystems: (1) **NTFS** — the classic Windows filesystem, supporting ACLs, compression, encryption (EFS); (2) **ReFS (Resilient File System)** — Microsoft's next-generation filesystem for Windows Server, providing integrity checking, storage spaces integration, and large volume support; (3) **FAT32/exFAT** — still used for removable media and cross-platform compatibility.
- **RAID — Redundant Array of Independent Disks:** RAID combines multiple physical disks into a logical unit for redundancy (RAID 1, 5, 6), performance (RAID 0), or both. By 2040, hardware RAID controllers have largely been replaced by software RAID (Linux `mdraid`, ZFS RAID-Z, Windows Storage Spaces) due to: better performance on modern CPUs, no vendor lock-in, and easier recovery (software RAID volumes are portable between systems). The **Declustered RAID** paradigm — spreading data across many drives with flexible redundancy — is standard in hyperscale deployments.
- **LVM and Storage Virtualization:** Linux LVM (Logical Volume Manager) abstracts physical storage into a pool (Volume Group) from which Logical Volumes are allocated. Benefits: (1) **Resize volumes** without downtime; (2) **Snapshots** — point-in-time copies for backups; (3) **Thin provisioning** — allocate more space than physically available, adding storage as needed; (4) **Caching** — use SSDs as a cache for HDD volumes. By 2040, LVM integrates with: (1) **NVMe-oF (NVMe over Fabrics)** — remote NVMe storage accessed over RDMA or TCP with local-NVMe latency; (2) **Computational Storage** — drives with onboard processors that can filter, compress, or encrypt data before transferring to the host CPU.
- **Zoned Storage and SMR:** Shingled Magnetic Recording (SMR) and Zoned Namespaces (ZNS) SSDs impose write constraints: data must be written sequentially within zones. This increases density (20-30% more capacity) but requires filesystem cooperation. By 2040, LFS and Btrfs ZNS-aware modes manage these constraints transparently, and the sysadmin's role is capacity planning and zone health monitoring rather than manual optimization.

#### Lecture Notes

The 2040 storage hierarchy: (1) **Memory-tier** — persistent memory (PMem/Optane successor) and CXL-attached memory, providing DRAM-like latency with storage-like persistence; (2) **NVMe-tier** — high-performance NVMe SSDs for active datasets; (3) **HDD-tier** — high-capacity spinning disks for cold storage, now reaching 100TB per drive; (4) **Tape-tier** — LTO-14 tape for archival, with 500TB per cartridge. Automated tiering (promoting hot data to faster tiers, demoting cold data to slower tiers) is managed by AI models that predict access patterns.

A key 2040 development is **immutable storage** — append-only or WORM (Write Once Read Many) storage that prevents deletion or modification for a specified retention period. This is increasingly mandated for financial records, healthcare data, and legal evidence. Linux implements this via immutable filesystem attributes (`chattr +i`), append-only ZFS datasets, and WORM-capable object storage (S3 Object Lock). Windows implements it via the ReFS integrity stream with locked files.

#### Required Reading

- Nemeth, E., Snyder, G., Hein, T., Whaley, B., & Mackin, D. (2038). *UNIX and Linux System Administration Handbook* (6th ed.). Chapter 8: Storage.
- Sun Microsystems (now Oracle). (2035). *ZFS Administration Guide* (Updated for Linux).
- Microsoft. (2039). *Storage Spaces Direct: Architecture and Operations*.
- UoY Storage Lab. (2040). *The 2040 Storage Hierarchy: From Persistent Memory to Tape*.

#### Discussion Questions

1. Btrfs and ZFS provide checksums, snapshots, and self-healing. ext4 and XFS do not. Should checksumming filesystems be mandatory for production data, or is the performance/complexity cost sometimes justified?
2. Deduplication saves storage space but consumes RAM (for the dedup table) and CPU. Under what conditions is deduplication worth its cost? How does the 2040 availability of computational storage change this calculus?
3. Immutable storage protects against ransomware and insider threats but complicates legitimate data deletion (e.g., GDPR right-to-erasure requests). How should organizations balance immutability with data subject rights?

#### Practice Problems

- Create a ZFS pool with three virtual disks in RAID-Z1 configuration. Create a dataset, set compression, and take a snapshot. Roll back to the snapshot after modifying data.
- Configure LVM: create a volume group spanning two disks, create a logical volume, format it with XFS, and extend it after adding a third disk. Resize the filesystem to use the new space.
- Investigate a production server's storage configuration. Identify the filesystem types, RAID levels, and backup strategy. Write a 500-word assessment: what risks are present, and what would you improve?

---

### Lecture 6: Service Management — systemd and Windows Services

**Course:** IT201 — System Administration (Linux + Windows)
**Degree:** Bachelor of Science in Information Technology, 2040

---

#### Overview

Services are the programs that run persistently in the background — web servers, databases, message queues, monitoring agents. Managing services — starting, stopping, enabling at boot, monitoring health, and recovering from failure — is a core sysadmin responsibility. This lecture examines service management on Linux (systemd, the dominant init system) and Windows (Service Control Manager), including the 2040 innovations in declarative service definition, socket activation, and AI-driven service health management.

#### Key Topics

- **systemd — The Linux Service Manager:** systemd (system daemon) is the init system and service manager for virtually all Linux distributions by 2040. Key concepts: (1) **Units** — the fundamental objects managed by systemd: service units (`.service`), socket units (`.socket`), timer units (`.timer`, replacing cron), mount units (`.mount`), and more; (2) **Dependencies** — units declare `Requires=`, `Wants=`, `Before=`, `After=` relationships, and systemd resolves the ordering and parallelism automatically; (3) **cgroups integration** — every service runs in its own cgroup, enabling resource accounting and limiting; (4) **Socket activation** — systemd listens on behalf of services and starts them on-demand when a connection arrives, reducing resource usage for infrequently-used services; (5) **Journal** — systemd's structured, indexed logging system (journald), providing fast search and binary integrity. By 2040, systemd has absorbed additional functions: timer-based scheduled tasks (replacing cron), network configuration (systemd-networkd), DNS resolution (systemd-resolved), and container management (systemd-nspawn, integrated with Podman).
- **Service Unit Files:** A systemd service unit file (e.g., `/etc/systemd/system/nginx.service`) declares: (1) `ExecStart` — the command to run; (2) `Restart` — policy for automatic restart (`on-failure`, `always`, `no`); (3) `User`/`Group` — the user/group to run as (privilege separation); (4) `ProtectSystem=strict` — mount `/usr`, `/boot`, `/etc` as read-only to the service; (5) `PrivateTmp=true` — give the service its own `/tmp`; (6) `NoNewPrivileges=true` — prevent privilege escalation even if the service is compromised. These options implement the principle of least privilege at the service level — a compromised web server should not be able to write to the filesystem, access other services' temporary files, or escalate to root.
- **Windows Service Management:** Windows services are managed via: (1) **Services MMC snap-in** — GUI for service management; (2) **`sc.exe` (Service Control)** — command-line tool for creating, querying, and controlling services; (3) **PowerShell** — `Get-Service`, `Start-Service`, `New-Service`. Windows services support: (1) **Recovery actions** — restart, run a program, or reboot the computer on failure; (2) **Delayed Auto-Start** — start after system boot completes, reducing boot time contention; (3) **Trigger-Start** — start when a specific event occurs (e.g., device arrival); (4) **Service SID** — a per-service security identifier for fine-grained access control.
- **Declarative Service Management:** By 2040, both Linux and Windows are moving toward declarative service management — defining the desired state ("this service should be running, with these dependencies, on these hosts") and letting the system reconcile the actual state. On Linux, this is achieved via systemd's portable services and integration with configuration management (Ansible, Puppet). On Windows, Desired State Configuration (DSC) and Group Policy define declarative service states. The trend is toward **GitOps for infrastructure**: service definitions stored in Git, with operators continuously reconciling the declared state with reality.

#### Lecture Notes

systemd has been one of the most controversial pieces of Linux infrastructure. Critics argue it violates the Unix philosophy ("do one thing well") by absorbing too many functions. Supporters argue that the integrations (cgroups, journal, socket activation) are genuinely useful and that systemd's unified design eliminates the ad-hoc scripting that plagued SysV init. By 2040, the debate has largely settled: systemd won, and the practical benefits of its integrated design are accepted.

A 2040 innovation is **AI-Assisted Service Health Management**. Instead of simple binary health checks ("is the process running?"), AI models monitor service behavior — response latency distributions, error rates, resource consumption patterns — and detect anomalies that precede failures. The AI can then: restart a service before it crashes, scale resources proactively, or alert a human operator with a diagnosis. The **UoY Autonomous Operations Lab** has demonstrated AI health management maintaining 99.999% availability for a fleet of 10,000 services over a multi-year trial — compared to 99.95% for traditional health checks.

#### Required Reading

- systemd.io. (2040). *systemd Documentation*.
- Microsoft. (2039). *Windows Server Service Management*.
- UoY Autonomous Operations Lab. (2039). *AI-Assisted Service Health: From Binary Checks to Behavioral Prediction*.
- Beyer, B., et al. (2038). *Site Reliability Engineering: Service Management at Scale*.

#### Discussion Questions

1. systemd's broad scope (init, logging, networking, containers) has been criticized as violating Unix philosophy. Does this integration improve system administration, or does it create excessive complexity and coupling?
2. AI health management can predict and prevent failures, but when it makes a wrong decision (e.g., restarting a service unnecessarily), debugging is harder because the AI's reasoning is opaque. How should operators balance autonomy and explainability?
3. Declarative service management (GitOps) treats service configuration as code. What practices from software engineering (code review, testing, CI/CD) should apply to service definitions, and which don't translate well?

#### Practice Problems

- Write a systemd service unit for a Python web application. Include security hardening: `ProtectSystem=strict`, `PrivateTmp=true`, `NoNewPrivileges=true`, and a dedicated user. Test the service and verify the security restrictions with `/proc/<pid>/mounts`.
- Create a systemd timer unit that runs a backup script daily. Compare to an equivalent cron job. What advantages does the timer provide?
- Use PowerShell to query all Windows services with startup type "Automatic." Identify which services are not running. Write a script that alerts on any Automatic service in a stopped state.

---

### Lecture 7: Monitoring and Performance Tuning

**Course:** IT201 — System Administration (Linux + Windows)
**Degree:** Bachelor of Science in Information Technology, 2040

---

#### Overview

You cannot manage what you cannot measure. Monitoring — collecting, analyzing, and alerting on system metrics — is essential for capacity planning, incident detection, and performance optimization. This lecture covers the monitoring stack: metrics collection (Prometheus, Telegraf), visualization (Grafana), alerting (Alertmanager), and the 2040 evolution toward unified observability (metrics + logs + traces) and AI-driven anomaly detection.

#### Key Topics

- **The Four Golden Signals:** Google's SRE book defined four key metrics for any service: (1) **Latency** — how long requests take (p50, p95, p99); (2) **Traffic** — request rate; (3) **Errors** — the rate of failed requests; (4) **Saturation** — how "full" the service is (CPU, memory, I/O, connection pool). By 2040, the framework has expanded to include: (5) **Cost** — the cloud resource cost per request, enabling FinOps; (6) **Carbon** — the carbon footprint per request, enabling GreenOps; (7) **Security** — the rate of suspicious or blocked requests.
- **Linux Performance Tools:** The 2040 Linux sysadmin's toolkit: (1) **`top`/`htop`/`btop`** — interactive process and resource monitoring; (2) **`vmstat`, `iostat`, `mpstat`** — system, I/O, and CPU statistics; (3) **`perf`** — kernel-level profiling of CPU, cache, and branch prediction; (4) **eBPF-based tools** (bpftrace, BCC toolkit) — dynamic tracing without kernel modification, enabling analysis of filesystem, network, and scheduler behavior at fine granularity; (5) **Prometheus + Node Exporter** — time-series metrics collection with a powerful query language (PromQL); (6) **Grafana** — dashboarding and visualization.
- **Windows Performance Tools:** Windows equivalents: (1) **Task Manager / Resource Monitor** — basic resource monitoring; (2) **Performance Monitor (PerfMon)** — collects counters for CPU, memory, disk, network, and application-specific metrics; (3) **Windows Performance Recorder/Analyzer (WPR/WPA)** — event tracing for deep performance analysis; (4) **Telegraf + InfluxDB + Grafana** — the cross-platform metrics stack. By 2040, the Windows Subsystem for Linux enables running Linux monitoring tools (Prometheus exporters, eBPF probes) on Windows.
- **Observability — Metrics, Logs, Traces:** The 2040 standard, building on the OpenTelemetry project, is unified observability: (1) **Metrics** — numeric time series (CPU%, request count); (2) **Logs** — structured, timestamped text records of events; (3) **Traces** — records of a request's path through a distributed system, with spans for each service call. The key 2040 innovation is **correlation**: clicking on a spike in a metric shows the relevant logs and traces for that time window — no more jumping between tools and manually correlating timestamps.

#### Lecture Notes

A 2040 monitoring paradigm is **AI-Driven Anomaly Detection**. Traditional monitoring relies on fixed thresholds (e.g., "alert if CPU > 90% for 5 minutes"), which generate false positives (a legitimate batch job spikes CPU) and false negatives (a subtle memory leak stays under threshold until it's critical). AI models trained on historical metric patterns can detect deviations from normal behavior, even when absolute values stay within thresholds. The **UoY Observability Lab's 2040 benchmark** found that AI-driven alerting reduces false positives by 73% and detects incidents 12 minutes faster on average than threshold-based alerting.

A related trend is **predictive capacity planning**. Instead of reacting to resource exhaustion, AI models forecast future resource usage based on trends, planned launches, and seasonal patterns. Organizations can order hardware or adjust cloud reservations weeks before they're needed, avoiding both outages and over-provisioning. The accuracy of these forecasts by 2040 (MAPE under 8% for 30-day horizons) has made predictive capacity planning standard practice.

#### Required Reading

- Beyer, B., et al. (2038). *Site Reliability Engineering* (3rd ed.). Chapters 6, 10: Monitoring Distributed Systems.
- Prometheus Authors. (2040). *Prometheus: Up and Running* (4th ed.). O'Reilly Media.
- OpenTelemetry. (2039). *Unified Observability Specification v2.0*.
- UoY Observability Lab. (2040). *AI-Driven Anomaly Detection: Benchmarks and Best Practices*.

#### Discussion Questions

1. Monitoring generates enormous amounts of data — a 1,000-server fleet can produce millions of data points per second. How much monitoring is "enough"? What principles determine which metrics to collect and which to ignore?
2. AI-driven alerting reduces false positives but introduces opacity — the AI might miss an anomaly because its model didn't consider that pattern anomalous. How should organizations validate AI-driven alerting systems?
3. Predictive capacity planning enables optimization but also creates risk: if the prediction is wrong, the organization is either under-provisioned (outage) or over-provisioned (waste). Under what circumstances is predictive planning worth the risk?

#### Practice Problems

- Install Prometheus and Node Exporter on a Linux server. Query CPU, memory, and disk metrics using PromQL. Create a Grafana dashboard visualizing the "four golden signals" plus cost and carbon.
- Use eBPF tools (bpftrace or BCC) to trace filesystem operations on a running application. Identify which files are most frequently accessed and the I/O latency distribution.
- Configure AI-driven anomaly detection (using an open-source tool like LinkedIn's Third Eye or a cloud service) on a metrics stream. Compare the alerts generated by threshold-based vs. AI-driven detection over a week.

---

### Lecture 8: Automation and Configuration Management

**Course:** IT201 — System Administration (Linux + Windows)
**Degree:** Bachelor of Science in Information Technology, 2040

---

#### Overview

Manual system administration does not scale. Configuration management tools — Ansible, Puppet, Chef, Salt, and PowerShell DSC — enable sysadmins to define infrastructure as code, apply it consistently across thousands of servers, and verify compliance automatically. By 2040, the configuration management landscape has converged, with Ansible dominating for its simplicity and agentless architecture, while specialized tools address niche requirements. This lecture covers the principles and practice of infrastructure automation.

#### Key Topics

- **Infrastructure as Code (IaC):** IaC applies software engineering practices to infrastructure: (1) **Version control** — infrastructure definitions are stored in Git, enabling history, code review, and rollback; (2) **Idempotency** — applying the same configuration multiple times produces the same result (safe to re-run); (3) **Declarative vs. Imperative** — declarative ("ensure package nginx is installed") describes desired state; imperative ("run `apt-get install nginx`") describes steps. Declarative is generally preferred for infrastructure because it's easier to verify and idempotent by nature.
- **Ansible:** Ansible is the dominant configuration management tool of 2040. Key features: (1) **Agentless** — uses SSH (Linux) or WinRM (Windows) to connect to managed nodes, no agent to install; (2) **YAML playbooks** — human-readable configuration definitions; (3) **Modules** — idempotent operations for package management, file manipulation, service control, and cloud API calls; (4) **Roles** — reusable, shareable collections of tasks, variables, and handlers; (5) **Ansible Vault** — encrypts sensitive data (passwords, API keys) within playbooks; (6) **Ansible Automation Platform** — the 2040 enterprise offering with RBAC, scheduling, and AI-assisted playbook generation (describe what you want in prose, get a draft playbook).
- **Declarative State Reconciliation:** The 2040 paradigm shift is from "run the playbook now" to "continuously enforce the declared state." Kubernetes operators (custom controllers that reconcile desired state with actual state) have inspired a broader movement toward continuous reconciliation. Tools like **Crossplane** (infrastructure as Kubernetes custom resources) and **systemd's portable services with state enforcement** represent this paradigm. The sysadmin defines the desired state in Git; a reconciliation loop continuously applies it and alerts on drift.
- **Cross-Platform Automation:** By 2040, most organizations run both Linux and Windows. Automation tools must handle both. Ansible has mature Windows support (WinRM, PowerShell modules). PowerShell DSC works on Linux. The **Universal Automation Protocol (UAP, 2037)** — a W3C standard — enables heterogeneous automation tools to interoperate, so an Ansible playbook can trigger a Puppet run or a Windows DSC configuration.

#### Lecture Notes

A 2040 automation principle is **immutable infrastructure**: instead of updating running servers in place (patching, reconfiguring), build new server images with the changes and replace the old servers. Immutable infrastructure eliminates configuration drift (the divergence between servers that accumulates over time), simplifies rollback (just deploy the previous image), and makes testing more reliable (test the exact image that will be deployed). Containerization and cloud APIs have made immutable infrastructure practical for most workloads.

However, not everything can be immutable. Databases, stateful applications, and legacy systems often require in-place management. The 2040 practice is **layered automation**: immutable at the application layer (containers, serverless functions), declaratively managed at the OS layer (Ansible, DSC), with manual overrides carefully tracked and time-limited.

#### Required Reading

- Geerling, J. (2038). *Ansible for DevOps* (5th ed.). Leanpub.
- Microsoft. (2039). *PowerShell Desired State Configuration Guide*.
- UoY Automation Lab. (2040). *Infrastructure as Code: Best Practices for the 2040 Enterprise*.
- W3C. (2037). *Universal Automation Protocol v1.0*.

#### Discussion Questions

1. Immutable infrastructure eliminates configuration drift but requires rebuilding and redeploying servers for every change. Is the trade-off (more deployments, less drift) always worth it? When does mutable management make sense?
2. Ansible's agentless architecture simplifies setup but limits real-time enforcement (you must run the playbook to apply changes). Agent-based systems (Puppet, Chef) continuously enforce state but require maintaining agents. Which model is better for which contexts?
3. AI-assisted playbook generation (describe in prose, get a playbook) lowers the barrier to automation but risks generating insecure or inefficient configurations. How should organizations govern AI-assisted infrastructure code?

#### Practice Problems

- Write an Ansible playbook that configures a Linux web server: install nginx, configure a virtual host, set up TLS with Let's Encrypt, configure firewall rules, and set up log rotation. Test against a fresh VM.
- Create an Ansible role that hardens a Linux server: disable root SSH, configure fail2ban, enable automatic security updates, set password policies, and configure auditd. Apply to a test server and verify.
- Implement a PowerShell DSC configuration that ensures specific Windows features are installed (IIS, .NET Framework) and specific services are running. Test the configuration and verify compliance.

---

### Lecture 9: Backup, Recovery, and Disaster Planning

**Course:** IT201 — System Administration (Linux + Windows)
**Degree:** Bachelor of Science in Information Technology, 2040

---

#### Overview

Backups are the sysadmin's last line of defense. When hardware fails, ransomware encrypts, or an administrator accidentally deletes, backups are the difference between recovery and catastrophe. This lecture covers backup strategies (full, incremental, differential, continuous), recovery testing (untested backups are not backups), disaster recovery planning (RPO, RTO, business continuity), and the 2040 innovations in immutable backups and AI-assisted recovery.

#### Key Topics

- **The 3-2-1 Backup Rule and Its Evolution:** The classic rule: 3 copies of data, on 2 different media, with 1 off-site. By 2040, the rule has evolved to **4-3-2-1**: 4 copies, on 3 different media types, with 2 off-site (different geographic regions), and 1 immutable (air-gapped or WORM-protected against ransomware). The addition of immutability reflects the ransomware threat landscape of the 2030s–2040s.
- **Backup Types:** (1) **Full backup** — complete copy of all data; (2) **Incremental backup** — copies only data changed since the last backup (any type), minimizing storage and time; (3) **Differential backup** — copies data changed since the last full backup, balancing restore speed and storage; (4) **Continuous Data Protection (CDP)** — every write is replicated to a backup target in near-real-time, enabling recovery to any point in time (not just the last backup window); (5) **Snapshot-based backup** — filesystem or storage array snapshots provide instant, space-efficient point-in-time copies.
- **Linux Backup Tools:** The 2040 Linux backup toolkit: (1) **`rsync`** — file-level synchronization, efficient for incremental copies; (2) **BorgBackup / Restic** — deduplicating, compressed, encrypted backup tools designed for the cloud era; (3) **ZFS/Btrfs send/receive** — filesystem-level incremental replication, extremely efficient for snapshot-based backups; (4) **LVM snapshots** — point-in-time copies for consistent database backups; (5) **Bareos/Bacula** — enterprise backup management with scheduling, cataloging, and tape support.
- **Windows Backup Tools:** Windows equivalents: (1) **Windows Server Backup** — built-in backup with volume shadow copy (VSS) for application consistency; (2) **Azure Backup / MARS agent** — cloud-integrated backup with incremental forever and long-term retention; (3) **Veeam** — popular third-party backup for virtualized environments; (4) **ReFS block cloning** — fast, space-efficient copy of files within ReFS.
- **Disaster Recovery Planning:** DR planning defines: (1) **RPO (Recovery Point Objective)** — maximum acceptable data loss measured in time (e.g., 1 hour of lost data); (2) **RTO (Recovery Time Objective)** — maximum acceptable time to restore service (e.g., 4 hours); (3) **Business Impact Analysis (BIA)** — identifies which systems are critical and their RPO/RTO; (4) **DR runbook** — step-by-step procedures for recovery, kept current through regular testing. By 2040, DR runbooks are executable (not just documents) — scripts and automation that can be tested in isolated environments quarterly.

#### Lecture Notes

The most common backup failure mode is not media failure or software bugs — it's **untested restores**. A backup that has never been restored is not a backup; it is a hope. Organizations that test restores quarterly detect backup issues (corruption, missing dependencies, configuration errors) before they need them. Organizations that don't test discover the issues during an incident. The **UoY DR Research Group's 2040 survey** found that 34% of organizations had experienced a backup failure during an actual recovery — and 78% of those had not tested restores in the preceding quarter.

A 2040 innovation is **AI-assisted recovery orchestration**. When an incident occurs, the AI: (1) identifies which systems are affected and their dependencies; (2) determines the optimal recovery order (restore the database before the application server); (3) initiates restores from the appropriate backups; (4) validates that restored systems are functional (automated smoke tests); (5) provides a real-time dashboard of recovery progress. Organizations using AI recovery orchestration achieve RTOs 60% shorter than manual recovery, according to the UoY study.

#### Required Reading

- Preston, W. C. (2038). *Backup & Recovery* (4th ed.). O'Reilly Media.
- UoY DR Research Group. (2040). *The State of Disaster Recovery: Benchmarks and Failures*.
- NIST. (2039). SP 800-34 Rev. 2: Contingency Planning Guide for Information Technology Systems.
- UoY Autonomous Systems Lab. (2040). *AI-Assisted Recovery Orchestration*.

#### Discussion Questions

1. The 4-3-2-1 backup rule with immutability protects against ransomware but increases storage costs significantly. How should organizations decide what data merits this level of protection?
2. "Untested backups are not backups." Yet comprehensive restore testing is expensive and disruptive. How should organizations balance thorough testing with operational cost? What is the minimum acceptable testing frequency?
3. AI-assisted recovery orchestration can reduce RTO but introduces a new dependency: if the AI system itself is affected by the disaster, manual recovery may be required. How should DR planning address the scenario where the AI recovery system is unavailable?

#### Practice Problems

- Implement a backup strategy using BorgBackup or Restic: configure full and incremental backups, set retention policies (daily for 7 days, weekly for 4 weeks, monthly for 12 months), and test a restore. Document the RTO for a full system restore.
- Simulate a disaster: on a test system, delete critical files and attempt to restore from backup. Time the process and identify any issues. Write a 500-word postmortem.
- Create a DR runbook for a simple web application (web server + database). Include step-by-step recovery procedures, contact information, and validation tests. Execute the runbook in a test environment.

---

### Lecture 10: Security Hardening and Patch Management

**Course:** IT201 — System Administration (Linux + Windows)
**Degree:** Bachelor of Science in Information Technology, 2040

---

#### Overview

System hardening — configuring systems to minimize attack surface — and patch management — keeping software up to date — are fundamental security responsibilities. By 2040, the threat landscape includes AI-generated exploits, supply chain attacks, and quantum-accelerated cryptanalysis, making security hardening more important than ever. This lecture covers hardening frameworks (CIS Benchmarks, DISA STIGs), practical hardening techniques, vulnerability management, and the 2040 practice of continuous security compliance.

#### Key Topics

- **Security Hardening Frameworks:** Industry-standard hardening guides: (1) **CIS Benchmarks** (Center for Internet Security) — consensus-based configuration recommendations for operating systems, cloud platforms, and applications, updated annually; (2) **DISA STIGs** (Security Technical Implementation Guides) — U.S. Department of Defense hardening standards; (3) **PCI DSS** (Payment Card Industry Data Security Standard) — security requirements for payment processing; (4) **ISO 27001** — international information security management standard. By 2040, these frameworks have converged on a common core of recommendations, with automated compliance checking tools that map between frameworks.
- **Linux Hardening:** Key Linux hardening practices: (1) **Minimal installation** — install only necessary packages; (2) **Disable unnecessary services** — `systemctl disable` everything not needed; (3) **Firewall** — `iptables`/`nftables` or `firewalld`, default-deny inbound, restrict outbound; (4) **SSH hardening** — disable root login, use key-based authentication, restrict users/groups, use non-standard port (defense in depth); (5) **SELinux/AppArmor** — mandatory access control that confines services even if compromised; (6) **Auditd** — log security-relevant events (authentication, privilege escalation, file access); (7) **AIDE/Tripwire** — file integrity monitoring that detects unauthorized changes; (8) **Kernel hardening** — sysctl parameters for network security (disable IP forwarding, enable SYN cookies, restrict core dumps).
- **Windows Hardening:** Windows equivalents: (1) **Security Compliance Toolkit** — apply and audit security baselines; (2) **Windows Defender Firewall** — default-block inbound, restrict outbound by application; (3) **Credential Guard** — protect credentials using virtualization-based security; (4) **AppLocker/WDAC** — application control (only allow approved software to run); (5) **BitLocker** — full-disk encryption; (6) **LAPS (Local Administrator Password Solution)** — unique, rotated local admin passwords; (7) **Windows Defender ATP** — endpoint detection and response with AI-driven threat detection.
- **Patch Management:** Systematic patch management includes: (1) **Inventory** — know what software is installed on every system; (2) **Vulnerability scanning** — regularly scan for known vulnerabilities (using Nessus, OpenVAS, Qualys); (3) **Prioritization** — use CVSS (Common Vulnerability Scoring System) and exploitability to prioritize (CVSS 9+ with active exploit = patch immediately); (4) **Testing** — test patches in staging before production; (5) **Deployment** — staged rollout (canary → 10% → 50% → 100%), with automated rollback if issues detected; (6) **Verification** — rescan after patching to confirm vulnerabilities are remediated. By 2040, AI-assisted patch management predicts which patches will cause issues based on system configuration similarity and guides deployment scheduling.

#### Lecture Notes

A 2040 hardening paradigm is **immutable infrastructure as a security strategy**. Instead of hardening running systems (which can drift), build hardened images, test them for security compliance, and deploy them immutably. Any deviation from the hardened image is treated as a security incident and triggers automatic replacement. This approach, combined with continuous compliance scanning, eliminates the gap between "configured securely" and "remaining secure over time."

Another 2040 development is **supply chain security**. The SolarWinds attack (2020), Log4Shell (2021), and subsequent supply chain compromises demonstrated that even well-hardened systems can be compromised through trusted software. By 2040, organizations use: (1) **SBOMs (Software Bill of Materials)** — machine-readable inventories of all software components and their dependencies; (2) **Sigstore/cosign** — cryptographic signing and verification of software artifacts; (3) **SLSA (Supply-chain Levels for Software Artifacts)** — a framework for assessing supply chain security maturity; (4) **Reproducible builds** — independently verifiable that a binary matches its source code.

#### Required Reading

- CIS. (2040). *CIS Benchmarks: Linux and Windows Server*.
- NSA/CISA. (2039). *System Hardening Guidance for Critical Infrastructure*.
- UoY Security Lab. (2040). *Supply Chain Security: From SBOMs to Reproducible Builds*.
- NIST. (2039). SP 800-40 Rev. 3: Guide to Enterprise Patch Management.

#### Discussion Questions

1. SELinux/AppArmor can prevent even a root-compromised service from accessing sensitive files, but they add configuration complexity. Is the security benefit always worth the operational cost? Under what circumstances would you not use mandatory access control?
2. Immutable infrastructure eliminates configuration drift but requires rebuilding images for every security patch. If a critical CVE requires an emergency patch, the immutable rebuild-and-redeploy pipeline adds latency. How should organizations balance immutability with emergency response speed?
3. AI-assisted patch management predicts which patches will cause issues. When the AI is wrong (predicts no issues but issues occur), who is accountable? The sysadmin who deployed? The AI vendor? The organization that chose to trust the AI?

#### Practice Problems

- Apply the CIS Benchmark Level 1 recommendations to a Linux server. Use a compliance scanning tool (Lynis, OpenSCAP) to verify compliance. Document any findings that cannot be fully remediated and explain why.
- Implement AppArmor profiles for a web application (nginx + application server). Verify that the application runs correctly within the profile and that unauthorized access attempts are blocked and logged.
- Set up a vulnerability scanning pipeline: use OpenVAS to scan a test server, prioritize findings by CVSS score, create a remediation plan, patch the vulnerabilities, and rescan to verify remediation.

---

### Lecture 11: Containerization and Virtualization for System Administrators

**Course:** IT201 — System Administration (Linux + Windows)
**Degree:** Bachelor of Science in Information Technology, 2040

---

#### Overview

Containers and virtual machines are the building blocks of modern infrastructure — enabling isolation, density, and portability. By 2040, containers (Docker/Podman, Kubernetes) and VMs (KVM, Hyper-V, confidential VMs) coexist, each suited to different use cases. This lecture examines the technologies, operational practices, and the sysadmin's role in managing containerized and virtualized environments.

#### Key Topics

- **Virtual Machines:** A hypervisor creates and runs VMs — complete virtual computers with their own kernel, memory, and devices. Types: (1) **Type 1 (bare-metal)** — KVM (Linux), Hyper-V (Windows), ESXi (VMware); (2) **Type 2 (hosted)** — VirtualBox, VMware Workstation. Key VM concepts: (1) **Overcommit** — allocating more virtual CPUs or memory than physically available, relying on the hypervisor scheduler; (2) **Live migration** — moving a running VM between physical hosts without downtime; (3) **Snapshots** — point-in-time copies of VM state for backup or experimentation; (4) **Confidential VMs** — VMs where memory is encrypted even from the hypervisor (Intel TDX, AMD SEV-SNP, ARM CCA), enabling secure multi-tenant computing.
- **Containers:** Containers provide OS-level virtualization — isolated user-space instances sharing the host kernel. Containers are lighter than VMs (no separate kernel, faster startup), but provide weaker isolation (shared kernel). Key container concepts: (1) **Images** — layered, read-only templates built from Dockerfiles or Containerfiles; (2) **Registries** — repositories for storing and distributing images (Docker Hub, Quay.io, GitHub Container Registry); (3) **Orchestration** — Kubernetes (K8s) manages container deployment, scaling, networking, and storage across clusters. By 2040, Podman (daemonless, rootless containers) has largely replaced Docker for production Linux workloads due to its stronger security model, though Docker images remain the standard format (OCI).
- **Kubernetes for Sysadmins:** Kubernetes abstracts a cluster of machines into a unified compute platform. Key concepts: (1) **Pods** — the smallest deployable unit (one or more containers sharing network and storage); (2) **Services** — stable network endpoints for pods (which are ephemeral); (3) **Deployments** — declarative management of pod replicas, with rolling updates and rollback; (4) **ConfigMaps and Secrets** — configuration and sensitive data injection; (5) **Persistent Volumes** — storage that survives pod restarts. The sysadmin's K8s responsibilities include: node management (provisioning, patching), cluster networking (CNI plugins), storage (CSI drivers), security (RBAC, Pod Security Standards, network policies), and observability (metrics, logs).
- **VM vs. Container — Choosing the Right Tool:** By 2040, the VM vs. container debate has settled into complementary roles: (1) **Containers** for stateless applications, microservices, CI/CD pipelines, and workloads that benefit from density and fast scaling; (2) **VMs** for strong isolation requirements (multi-tenant environments), legacy applications that need a full OS, workloads requiring a different kernel, and confidential computing; (3) **KubeVirt and Kata Containers** blur the boundary — running VMs through the Kubernetes API (KubeVirt) or using lightweight VMs as container isolation (Kata Containers).

#### Lecture Notes

A 2040 development is **serverless containers** — containers that scale to zero when idle, billed per-invocation rather than per-hour. Platforms like AWS Fargate, Google Cloud Run, and Azure Container Instances implement this model. The sysadmin's role shifts from managing servers to managing scaling policies, cost optimization, and cold-start latency. The challenge: when a container scales from zero, the initial request incurs a cold-start latency (image pull, container start, application initialization). By 2040, snapshot-based restoration and image prefetching have reduced cold starts to under 50ms for most workloads.

Another trend is **WebAssembly on Kubernetes**. Wasm modules start faster and consume less memory than containers, making them ideal for event-driven workloads. The Krustlet and wasmCloud projects integrate Wasm runtimes into Kubernetes. The sysadmin of 2040 manages a heterogeneous cluster: Linux containers, Windows containers, Wasm modules, and confidential VMs — all scheduled by the same Kubernetes control plane.

#### Required Reading

- Hightower, K., Burns, B., & Beda, J. (2038). *Kubernetes: Up and Running* (4th ed.). O'Reilly Media.
- Poulton, N. (2039). *Docker and Podman Deep Dive* (3rd ed.).
- UoY Virtualization Lab. (2040). *Confidential Computing in Production: A Sysadmin's Guide*.
- CNCF. (2040). *Kubernetes Security Best Practices*.

#### Discussion Questions

1. Containers share the host kernel, creating a larger attack surface than VMs. Is the density and speed advantage of containers worth the security trade-off, or should security-sensitive workloads always use VMs?
2. Kubernetes abstracts away individual servers, but someone still needs to manage the Kubernetes nodes (patching, upgrading, troubleshooting). Has Kubernetes simplified or complicated the sysadmin's job?
3. WebAssembly on Kubernetes promises faster startup and smaller footprint than containers. Is Wasm a replacement for containers, or a complement? What workloads are best suited for each?

#### Practice Problems

- Create a Docker/Podman image for a web application. Write a Dockerfile that uses multi-stage builds to minimize image size. Run the container with resource limits (CPU, memory) and verify enforcement.
- Deploy a simple application to a local Kubernetes cluster (minikube or kind). Define a Deployment, Service, ConfigMap, and Ingress. Perform a rolling update and observe zero-downtime deployment.
- Configure a Container Registry (local or cloud) and push your image. Set up image vulnerability scanning (Trivy, Clair) and remediate any findings.

---

### Lecture 12: The 2040 Sysadmin — AIOps, Autonomous Operations, and the Human Role

**Course:** IT201 — System Administration (Linux + Windows)
**Degree:** Bachelor of Science in Information Technology, 2040

---

#### Overview

By 2040, AI has absorbed many traditional sysadmin tasks: monitoring, alerting, patching, scaling, and even incident response. What, then, is the human sysadmin's role? This lecture examines the transformation of system administration in the age of AIOps (AI for IT Operations), the skills that remain uniquely human, and the career trajectory for the 2040 infrastructure professional.

#### Key Topics

- **AIOps — AI for IT Operations:** AIOps is the application of AI/ML to operational tasks: (1) **Anomaly detection** — identifying deviations from normal system behavior; (2) **Root cause analysis** — correlating events across systems to identify the cause of an incident; (3) **Automated remediation** — executing predefined or AI-suggested actions to resolve issues; (4) **Capacity forecasting** — predicting future resource needs; (5) **Noise reduction** — grouping related alerts and suppressing false positives. By 2040, Gartner estimates that 80% of operational tasks are AI-assisted, up from 5% in 2020.
- **What AI Does Well:** AI excels at: (1) **Pattern recognition at scale** — correlating millions of metrics across thousands of systems; (2) **Repetitive, well-defined tasks** — applying patches, running health checks, executing runbooks; (3) **Continuous vigilance** — AI never sleeps, never gets distracted, never skips a step. AI does poorly at: (1) **Novel situations** — incidents unlike anything in the training data; (2) **Ethical judgment** — decisions that involve trade-offs between competing values (cost vs. reliability vs. privacy); (3) **Communication** — explaining technical issues to non-technical stakeholders, negotiating priorities with product teams, mentoring junior colleagues.
- **The 2040 Sysadmin Skill Set:** The human sysadmin's value has shifted from execution to governance: (1) **System architecture** — designing systems that are monitorable, maintainable, and fault-tolerant; (2) **AI governance** — setting policies for AI operators, auditing AI decisions, intervening when the AI makes the wrong call; (3) **Incident command** — when the AI can't fix it, the human takes over, coordinating response, communicating status, and making trade-off decisions; (4) **Vendor and technology evaluation** — understanding the landscape and choosing appropriate tools; (5) **Mentorship and culture** — building a team culture of blamelessness, curiosity, and continuous improvement.
- **Ethics and Accountability:** When an AI operator makes a decision that causes an outage, who is accountable? The sysadmin who configured the AI? The vendor who built it? The organization that chose to deploy it? The **2040 IT Accountability Framework** (ISO/IEC 42001) establishes that: (1) humans retain ultimate accountability; (2) AI decisions above a risk threshold require human approval; (3) AI systems must provide explainable reasoning for their actions; (4) organizations must maintain the capability to operate without AI (though possibly with degraded performance).

#### Lecture Notes

The history of system administration has been a history of automation eating the job from below. Shell scripts automated repetitive commands. Configuration management automated server setup. Monitoring automated health checks. AIOps automates detection, diagnosis, and remediation. At each stage, some sysadmins feared obsolescence, but the profession survived — and grew — because automation eliminated toil and freed humans for higher-value work. The 2040 sysadmin is not a machine operator but a systems thinker, an AI governor, and a steward of digital civilization.

The **UoY Infrastructure Career Study (2039)** tracked sysadmin careers over three decades and found that sysadmins who embraced automation and developed architecture, communication, and governance skills saw their compensation increase by 2.5x (inflation-adjusted) and their job satisfaction increase significantly. Those who resisted automation and focused on manual execution saw their roles shrink and their compensation stagnate. The lesson: the AI does not replace you. The sysadmin who uses AI replaces the sysadmin who does not.

A 2040 frontier is **autonomous infrastructure** — systems that not only detect and remediate issues but actively optimize themselves, negotiate with cloud providers for better pricing, and evolve their architecture based on usage patterns. The human role in this vision is **architect-governor**: defining constraints, values, and policies within which the autonomous infrastructure operates. The sysadmin becomes the author of the system's constitution, not the executor of its operations.

#### Required Reading

- UoY Infrastructure Research Group. (2039). *The 2040 Sysadmin: Career Trajectories in the Age of AIOps*.
- Gartner. (2039). *AIOps Market Guide 2040*.
- ISO/IEC. (2039). 42001: Artificial Intelligence Management System — Accountability Framework.
- UoY Autonomous Systems Lab. (2040). *Autonomous Infrastructure: A Research Roadmap to 2050*.

#### Discussion Questions

1. If AI handles 80% of operational tasks, what is the minimum viable team size for managing a given infrastructure? Does AIOps concentrate or distribute expertise?
2. "Humans retain ultimate accountability for AI decisions." But if an AI system makes thousands of decisions per second, human review of every decision is impossible. How should accountability scale?
3. Autonomous infrastructure that negotiates with cloud providers and evolves its architecture could optimize for cost, performance, or carbon — but whose values does it optimize for? How should organizations encode their values into autonomous systems?

#### Practice Problems

- Evaluate an existing monitoring and alerting system. Where would AI-driven anomaly detection improve outcomes? Where would it risk missing critical issues? Write a 500-word recommendation.
- Design a human-in-the-loop AIOps workflow for a critical system. Define: what the AI can do autonomously, what requires human approval, how the human is notified, and how the AI's decisions are audited.
- Research the ISO/IEC 42001 AI Accountability Framework. Draft a 1-page policy for an organization deploying AIOps, addressing accountability, transparency, and human override capabilities.

---

## Final Examination Preparation

The final examination will consist of 8 essay questions, from which students choose 4 (1,000–1,500 words each). Answers must demonstrate hands-on knowledge, architectural reasoning, and awareness of both Linux and Windows contexts.

### Sample Essay Questions

1. **Dual-Platform Fluency:** Linux and Windows Server have distinct architectures (kernel design, filesystem hierarchy, configuration management, security models) but are converging in important ways. Compare and contrast system administration on the two platforms, addressing: (a) where the platforms remain fundamentally different; (b) where they have converged; and (c) what the 2040 administrator gains from dual-platform expertise.

2. **The Automation Spectrum:** From shell scripts to Ansible to AIOps, automation has progressively absorbed operational tasks. Trace this evolution, analyzing: (a) what each wave of automation enabled; (b) what was lost at each transition; and (c) what remains uniquely human in infrastructure operations.

3. **Storage Strategy for the 2040 Enterprise:** Design a storage architecture for a medium-sized enterprise (500 servers) with diverse workloads (transactional database, log analytics, user home directories, archival records). Justify your filesystem, RAID, tiering, and backup choices with reference to the technologies studied in this course.

4. **Security Hardening in Depth:** Describe a comprehensive security hardening strategy for a mixed Linux/Windows environment. Address: (a) OS-level hardening; (b) network security; (c) identity and access management; (d) supply chain security; and (e) how immutability and continuous compliance change the security posture.

5. **Containers vs. Virtual Machines:** Analyze the trade-offs between containers and VMs for different workload types. Under what circumstances is the stronger isolation of VMs necessary? Under what circumstances is the density and speed of containers preferable? How do confidential VMs and Wasm modules change the calculus?

6. **The AI-Augmented Sysadmin:** AIOps promises to reduce toil and improve reliability, but introduces new risks (opaque decisions, accountability gaps, over-reliance). Evaluate the appropriate role of AI in system administration: what should be automated, what should remain human, and what governance structures are needed.

7. **Backup and Disaster Recovery Architecture:** Design a backup and DR strategy for a healthcare organization subject to strict RPO/RTO requirements and data immutability mandates. Address backup types, storage tiers, off-site replication, testing procedures, and the role of AI in recovery orchestration.

8. **The Future of System Administration:** Based on the trends studied in this course (AIOps, immutable infrastructure, confidential computing, cross-platform convergence), project the sysadmin role to 2060. What will have changed fundamentally? What human skills will remain essential? Defend your predictions with evidence.

### Final Project Option

Students may substitute a comprehensive final project: **Operate a multi-platform environment for one semester.** Manage a small fleet (4+ servers, Linux and Windows) running production-like workloads. Maintain an operations log documenting: incidents and resolutions, performance tuning, security patches, backup/restore tests, and automation improvements. Submit the log along with a reflective essay on lessons learned.

---

**Þǫkk — May your systems stay up and your backups restore.**
