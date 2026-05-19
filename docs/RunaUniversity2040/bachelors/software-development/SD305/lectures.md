# SD305: Real-Time & Embedded Systems
## Bachelor of Science in Software Development — University of Yggdrasil, 2040

**Credits:** 4
**Semester:** Year 3, Semester 1
**Prerequisites:** SD203 (Software Architecture & Design), SD205 (DevOps & Continuous Delivery)
**Instructor:** Dr. Eldgrímr Kveldúlfsson, Faculty of Computational Arts

> *"A longship in a storm does not wait for the helmsman's deliberation. The sea demands response now — or the ship founders. So it is with real-time systems: the world does not pause for our code."* — Eldgrímr Kveldúlfsson, *The Unforgiving Sea* (2037)

---

## Course Description

Real-Time & Embedded Systems is the discipline of software that must respond to the world on the world's schedule — not when it's convenient, not when the garbage collector feels like it, not after the next iteration of the event loop, but *now*. This course teaches students to build systems where timing is not a performance concern but a correctness concern: a late answer is a wrong answer.

The course is organized around the metaphor of the longship in a storm. A longship navigating a tempest must respond to wind and wave within seconds — not minutes, not "eventually." A real-time system operating a surgical robot, an autonomous vehicle, or a power grid must respond to events within microseconds to milliseconds. The consequences of failure are similarly severe: a ship founders, a patient dies, a reactor melts down.

Students learn hard real-time vs. soft real-time scheduling theory, real-time operating system (RTOS) kernels, interrupt handling, deterministic memory management, real-time communication protocols (CAN, SPI, I2C, MQTT, DDS), embedded hardware constraints, power-aware computing, safety-critical software certification (DO-178C, ISO 26262), and the unique debugging techniques required when you cannot attach a debugger to a running medical device. The course includes hands-on work with the University's RúnarRT platform — a real-time framework built on FreeRTOS and Zephyr — running on ARM Cortex-M and RISC-V microcontrollers.

The 2040 landscape adds new urgency: AI inference at the edge, autonomous vehicles, surgical robotics, smart infrastructure, and IoT devices with hard real-time constraints all demand engineers who understand that *when* matters as much as *what*.

---

## Lectures

### ᚠ Lecture 1: The Unforgiving Sea — What Makes Real-Time Different

**Date:** Week 1, Session 1

#### Overview

"Real-time" does not mean "fast." It means "predictable." This opening lecture establishes the fundamental distinction between real-time systems and general-purpose computing, introduces the taxonomy of real-time constraints (hard, firm, soft), and begins the lifelong practice of thinking about time as a correctness property. The longship metaphor runs through the entire course: a system that computes the correct answer but delivers it after the deadline has passed is like a helmsman who plots the perfect course but arrives after the ship has foundered.

#### Lecture Notes

**Real-Time: It's Not About Speed.** The most common misconception about real-time systems is that they are "fast systems." They are not. A real-time system may be slow — a pacemaker that responds within 10ms is a hard real-time system, even though 10ms is glacial by CPU standards. What makes a system real-time is not the *speed* of its response, but the *predictability* of its response. A general-purpose system that sometimes responds in 1ms and sometimes in 500ms is *not* a real-time system, even though its average response is fast. A real-time system that always responds in exactly 10ms *is* a real-time system, even though its response is slower than the general-purpose system's best case.

The formal definition: a **real-time system** is one in which the correctness of the result depends not only on the logical correctness of the computation but also on the time at which the result is produced. A late correct answer is an incorrect answer.

**The Taxonomy of Deadlines.** Not all real-time constraints are created equal. The taxonomy, originally from Stanica and Ravindran (1999) and refined by the IEC and IEEE over subsequent decades:

| Type | Definition | Example | Late Result |
|------|------------|---------|--------------|
| **Hard real-time** | Missing a deadline causes catastrophic failure | Airbag deployment, pacemaker, nuclear reactor SCRAM | System failure, potential loss of life |
| **Firm real-time** | Missing a deadline makes the result useless, but no catastrophe | Video frame rendering, financial trading, teleoperation | Result is discarded; system degrades |
| **Soft real-time** | Missing a deadline reduces quality of service | Video streaming, web page loads, gaming | System degrades gracefully; user notices |

The distinction matters because hard real-time constraints require fundamentally different engineering approaches than soft real-time constraints. A hard real-time system must provide *guaranteed* worst-case response times, which requires deterministic scheduling, bounded memory allocation, and provable timing analysis. A soft real-time system can use probabilistic guarantees ("99.9% of responses within 10ms") — which is a much weaker but often sufficient constraint.

**The Longship Analogy: Navigating the Maelstrom.** Consider a Viking longship navigating a narrow fjord in a storm. The helmsman has:

- **Hard deadlines:** Respond to a breaking wave within 2 seconds or the ship capsizes.
- **Firm deadlines:** Adjust the sail within 5 seconds or the wind shift is past. A late adjustment is useless — the opportunity is gone.
- **Soft deadlines:** Monitor the horizon for other ships. If the check happens 10 seconds late, navigation quality degrades but the ship doesn't founder.

The helmsman must prioritize hard deadlines over firm deadlines over soft deadlines. The same priority structure applies to real-time software: an airbag must deploy within 30ms (hard), the dashboard must update the speedometer within 100ms (firm), and the infotainment system can be delayed by 500ms (soft). If the airbag and the infotainment compete for CPU time, the airbag always wins.

**Why General-Purpose OSes Are Not Real-Time.** A general-purpose operating system (Linux, Windows, macOS) is designed to maximize *average* throughput and *average* response time. It achieves this through techniques that are fundamentally incompatible with real-time guarantees:

- **Virtual memory and paging** — The OS may swap a page to disk at any time, pausing the process for milliseconds to tens of milliseconds. A real-time system cannot tolerate unpredictable multi-millisecond pauses.
- **Preemptive multitasking with unbounded priority inversion** — A low-priority thread holding a lock can block a high-priority thread for an unbounded time. The priority inheritance protocol (discussed in Lecture 5) mitigates this but is not implemented in standard Linux.
- **Garbage collection** — Managed languages (Java, C#, Python) pause all threads during garbage collection. Even "concurrent" garbage collectors add latency spikes. A real-time Java implementation exists (JSR-302, Real-Time Specification for Java) but has not achieved mainstream adoption.
- **Dynamic scheduling with no timing guarantees** — The Linux CFS (Completely Fair Scheduler) maximizes fairness, not determinism. A real-time scheduler must maximize *predictability* — ensuring the highest-priority task always runs within a bounded time after it becomes ready.

**The Real-Time Operating System (RTOS).** An RTOS solves these problems by providing:

1. **Deterministic scheduling** — The scheduler guarantees that the highest-priority ready task will run within a bounded time (the scheduling latency, typically 1-10μs on modern ARM Cortex-M processors).
2. **Priority inheritance or priority ceiling protocols** — When a low-priority task holds a resource needed by a high-priority task, the low-priority task's priority is temporarily elevated to prevent unbounded priority inversion.
3. **Bounded interrupt latency** — Interrupts are serviced within a guaranteed maximum time. The RTOS supports nested interrupts (higher-priority interrupts can preempt lower-priority interrupt handlers) and provides deterministic interrupt dispatch times.
4. **Deterministic memory allocation** — No virtual memory, no paging, no heap fragmentation. Memory is allocated statically (at compile time) or from fixed-size memory pools (at runtime, with O(1) allocation and deallocation).

Popular RTOSes in 2040 include FreeRTOS (open source, widely used in IoT and embedded), Zephyr (Linux Foundation, growing rapidly for connected devices), VxWorks (Wind River, used in aerospace, defense, and automotive), and QNX (BlackBerry, used in automotive and medical devices).

**The Response Time Equation.** The fundamental equation of hard real-time scheduling is the response time方程:

R_i = C_i + B_i + ∑(⌈R_i / T_j⌉ × C_j) for all j with higher priority than i

Where:
- R_i = worst-case response time of task i
- C_i = worst-case execution time of task i
- B_i = worst-case blocking time of task i (time spent waiting for lower-priority tasks to release shared resources)
- T_j = period of higher-priority task j
- C_j = worst-case execution time of higher-priority task j

The ⌈R_i / T_j⌉ term represents the number of times higher-priority task j will preempt task i during its execution. The equation is solved iteratively (start with R_i = C_i + B_i, substitute, repeat until convergence).

A task set is *schedulable* if R_i ≤ D_i for all tasks i (where D_i is the deadline of task i). This is the fundamental test: if every task meets its deadline under worst-case conditions, the system is schedulable.

**The Longship's Wake: What This Course Will Cover.** The 12 lectures of this course span the full arc of real-time and embedded systems development:

1. Foundations and taxonomy (this lecture)
2. Scheduling theory: rate-monotonic, deadline-monotonic, EDF
3. RTOS architecture: kernels, tasks, and interrupts
4. Synchronization and resource sharing in real-time systems
5. Memory management: static allocation, pools, and the prohibition of malloc
6. Real-time communication: CAN, SPI, I2C, and DDS
7. Embedded hardware: microcontrollers, FPGAs, and the edge
8. Safety-critical software: DO-178C, ISO 26262, and certification
9. Real-time debugging: when you can't printf and you can't pause
10. AI at the edge: real-time inference on resource-constrained devices
11. Power-aware computing: when the battery is the constraint
12. Synthesis: building a complete real-time system from requirements to deployment

#### Required Reading

- Kveldúlfsson, E. (2037). *The Unforgiving Sea: Real-Time Systems for Safety-Critical Applications*. University of Yggdrasil Press. Chapters 1-2.
- Buttazzo, G. C. (2011). *Hard Real-Time Computing Systems: Predictable Scheduling Algorithms and Applications* (3rd ed.). Springer. Chapters 1-2.
- Klein, M., et al. (1993). *A Practitioner's Handbook for Real-Time Analysis: Guide to Rate Monotonic Analysis for Real-Time Systems*. Kluwer Academic. Chapter 1.
- FreeRTOS Documentation (2040). *What is FreeRTOS?* https://www.freertos.org/About.html

#### Discussion Questions

1. The lecture states that "a late correct answer is an incorrect answer." But what about answers that arrive *slightly* late? If an airbag deploys in 31ms instead of 30ms, is it really "incorrect"? How should engineers determine the appropriate tolerance for hard real-time deadlines?
2. General-purpose OSes like Linux with PREEMPT_RT can achieve real-time latencies under 100μs. Why do hard real-time systems still use dedicated RTOSes? What can an RTOS guarantee that PREEMPT_RT Linux cannot?
3. Consider a soft real-time system (e.g., video streaming) and a hard real-time system (e.g., a pacemaker). If you had to engineer both with a single tool, would you use a hard real-time approach for both, or would you use different approaches? What are the tradeoffs?

---

### ᚢ Lecture 2: The Tides of Time — Scheduling Theory for Real-Time Systems

**Date:** Week 1, Session 2

#### Overview

Every real-time system must decide *which task to run next*. This is the scheduling problem — the heart of real-time systems theory. This lecture covers the three foundational scheduling algorithms (Rate-Monotonic, Deadline-Monotonic, and Earliest Deadline First), their schedulability tests, their optimality properties, and the boundary conditions where theory meets reality.

#### Lecture Notes

**The Theory of Fixed-Priority Scheduling.** Real-time scheduling theory begins with Liu and Layland's 1973 paper, "Scheduling Algorithms for Multiprogramming in a Hard Real-Time Environment" — one of the most cited papers in computer science. Liu and Layland proved two fundamental results:

1. **Rate-Monotonic (RM) scheduling** — Assign higher priority to tasks with shorter periods. RM is *optimal* among fixed-priority schedulers: if any fixed-priority schedule can meet all deadlines, RM can do it.

2. **Schedulability bound** — A set of n periodic, independent tasks is guaranteed schedulable under RM if the total utilization U = Σ(C_i / T_i) ≤ n(2^(1/n) - 1). For n=1, the bound is 100%. For n=2, it's 82.8%. As n → ∞, the bound approaches ln(2) ≈ 69.3%.

The schedulability bound is sufficient but not necessary. A task set with total utilization of 80% may still be schedulable under RM — the bound only guarantees that utilization up to 69.3% is *always* schedulable. For any specific task set, the exact response time analysis (from Lecture 1) gives a precise answer.

**Deadline-Monotonic (DM) Scheduling.** When task deadlines differ from task periods (i.e., a task with period 100ms has a deadline of 50ms), RM is no longer optimal. Deadline-Monotonic scheduling (Leung and Whitehead, 1982) assigns higher priority to tasks with shorter *deadlines*, not shorter periods. DM is optimal among fixed-priority schedulers when D_i ≤ T_i for all tasks.

**Earliest Deadline First (EDF) Scheduling.** EDF is a *dynamic-priority* scheduler: at any moment, the task with the earliest deadline has the highest priority. Liu and Layland proved that EDF is optimal among *all* uniprocessor schedulers: if any scheduler can meet all deadlines, EDF can. Moreover, EDF's schedulability bound is 100% — any task set with total utilization ≤ 1.0 is schedulable under EDF.

If EDF is optimal and can achieve 100% utilization, why isn't it the universal scheduler? The answer has four parts:

1. **Implementation complexity** — EDF requires sorting tasks by deadline at every scheduling point. On a system with 100 tasks, this adds overhead that RM doesn't have (RM assigns priorities once at design time).
2. **Overload behavior** — When a task set becomes unschedulable (total utilization > 100%), EDF's behavior is *unpredictable*. Any task may miss its deadline — not just the lowest-priority task. RM, in contrast, guarantees that the highest-priority tasks (the most critical ones) still meet their deadlines under overload.
3. **Pragmatic concerns** — Most RTOSes implement fixed-priority scheduling (RM or DM) because it's simpler, more predictable under overload, and sufficient for most task sets. EDF is used when utilization must be maximized and overload is handled by admission control.
4. **Certification** — DO-178C and ISO 26262 certification requires *demonstrable* timing guarantees. Fixed-priority scheduling is easier to analyze and verify than dynamic-priority scheduling. EDF's optimality is theoretically attractive but practically difficult to certify.

**Response Time Analysis: The Practitioner's Tool.** While the Liu-Layland bound provides a quick schedulability test, it's conservative. For a specific task set, response time analysis provides the exact worst-case response time for each task:

R_i = C_i + B_i + Σ(⌈R_i / T_j⌉ × C_j) for all j > hp(i)

This iterative equation is solved by starting with R_i⁰ = C_i + B_i and iterating until R_i^(n+1) = R_i^n (convergence) or R_i > D_i (deadline miss).

Example: Consider three tasks with the following parameters:

| Task | C (execution time) | T (period) | D (deadline) | Priority (RM) |
|------|-------------------|------------|--------------|----------------|
| τ₁ | 1 | 4 | 4 | Highest |
| τ₂ | 2 | 6 | 6 | Medium |
| τ₃ | 1 | 12 | 12 | Lowest |

**R₁ = C₁ = 1** (no higher-priority task can preempt). 1 ≤ 4 ✓

**R₂** iteration:
- R₂⁰ = C₂ + ⌈1/4⌉ × C₁ = 2 + 1 × 1 = 3
- R₂¹ = C₂ + ⌈3/4⌉ × C₁ = 2 + 1 × 1 = 3 (converged). 3 ≤ 6 ✓

**R₃** iteration:
- R₃⁰ = C₃ + ⌈1/4⌉ × C₁ + ⌈1/6⌉ × C₂ = 1 + 1 + 2 = 4
- R₃¹ = C₃ + ⌈4/4⌉ × C₁ + ⌈4/6⌉ × C₂ = 1 + 1 + 2 = 4 (converged). 4 ≤ 12 ✓

All tasks meet their deadlines. The task set is schedulable under RM.

**The Critical Instant: Worst-Case Arrives Together.** The response time analysis assumes the "critical instant" — the scenario where all higher-priority tasks arrive simultaneously with the task under analysis. This is the worst-case scenario for response time because it maximizes preemption from higher-priority tasks. Liu and Layland proved that the critical instant always produces the worst-case response time for fixed-priority scheduling, so the analysis is safe (it never underestimates the response time).

**Non-Periodic Tasks: Sporadic and Aperiodic.** Real systems include events that arrive at unpredictable times: interrupts, user inputs, network packets. These are modeled as sporadic tasks (with a minimum inter-arrival time) or aperiodic tasks (no minimum inter-arrival time, handled by a sporadic server or polling task).

The sporadic server is a periodic task that "reserves" bandwidth for aperiodic events. Its period and execution time are chosen based on the expected aperiodic load, and its priority is set to provide the desired response time. This converts the unbounded aperiodic load into a bounded periodic task that can be analyzed with the same response time equations.

#### Required Reading

- Buttazzo, G. C. (2011). *Hard Real-Time Computing Systems* (3rd ed.). Chapters 3-4.
- Liu, C. L., & Layland, J. W. (1973). "Scheduling Algorithms for Multiprogramming in a Hard Real-Time Environment." *Journal of the ACM*, 20(1), 46-61. [The foundational paper.]
- Kveldúlfsson, E. (2037). *The Unforgiving Sea*. Chapter 3: "The Tides of Priority."
- Joseph, M., & Pandya, P. (1986). "Finding Response Times in a Real-Time System." *The Computer Journal*, 29(5), 390-395. [The response time analysis paper.]

#### Discussion Questions

1. The Liu-Layland bound guarantees schedulability for utilization up to n(2^(1/n) - 1), which approaches 69.3% as n → ∞. This means 30.7% of the CPU is "wasted" in the worst case. Is this acceptable for safety-critical systems? What are the alternatives?
2. EDF achieves 100% utilization but behaves unpredictably under overload. In a system where overload is possible but rare (e.g., a medical device that occasionally receives bursty sensor data), is EDF preferable to RM? How would you mitigate the overload risk?
3. The critical instant analysis assumes all higher-priority tasks arrive simultaneously. This is a worst-case bound that is extremely unlikely in practice. Is there a better analysis that captures average-case behavior while still providing safety guarantees?

---

### ᚦ Lecture 3: The Ship's Rudder — RTOS Architecture: Kernels, Tasks, and Interrupts

**Date:** Week 2, Session 1

#### Overview

The RTOS kernel is the rudder of the real-time ship — the mechanism through which all control flows. This lecture covers the internal architecture of an RTOS: task states and transitions, the scheduler, context switching, interrupt handling, and the kernel services that make real-time programming possible. Students work with the University's RúnarRT platform (based on FreeRTOS and Zephyr) on ARM Cortex-M and RISC-V microcontrollers.

#### Lecture Notes

**The RTOS Kernel: A Minimal Operating System.** Unlike a general-purpose OS, which provides thousands of system calls, file systems, networking stacks, and device frameworks, an RTOS kernel provides the absolute minimum needed for real-time scheduling:

1. **Task management** — Create, delete, suspend, and resume tasks. Set task priorities. Provide task-local storage.
2. **Scheduler** — Select the highest-priority ready task to run. Perform context switches with deterministic latency.
3. **Synchronization primitives** — Semaphores, mutexes (with priority inheritance), and event flags.
4. **Inter-task communication** — Message queues, mailboxes, and pipes with bounded blocking times.
5. **Timer services** — Periodic timers, one-shot timers, and delay functions with deterministic accuracy.
6. **Interrupt management** — Install, enable, and disable interrupt handlers with bounded latency.

Everything else (file systems, networking, USB, graphics) is optional and provided as separate libraries or middleware. This minimalist design is intentional: every line of code in the kernel must be analyzable for worst-case execution time, and complexity is the enemy of determinism.

**Task States and Transitions.** An RTOS task can be in one of five states:

- **Running** — The task is currently executing on the CPU. Only one task can be in the Running state at a time (on a single-core processor).
- **Ready** — The task is ready to execute but a higher-priority task is currently Running. The task will execute as soon as it becomes the highest-priority Ready task.
- **Blocked** — The task is waiting for an event (a semaphore, a message queue, a timer). It will not execute until the event occurs.
- **Suspended** — The task has been explicitly suspended by the application and is not available for scheduling. It will not execute until explicitly resumed.
- **Terminated** — The task has completed execution and has been deleted or has returned from its entry function.

The state transitions are deterministic and bounded:

- Running → Blocked: A task calls a blocking API (e.g., waiting on a semaphore). The context switch time is bounded (typically 1-10μs on ARM Cortex-M at 100MHz).
- Running → Ready: A higher-priority task becomes Ready (e.g., an interrupt releases a semaphore that unblocks a higher-priority task). The preempted task is moved to Ready. The context switch time is bounded (same as above).
- Blocked → Ready: The event the task was waiting for occurs. The task is moved to Ready. If the task has higher priority than the current Running task, an immediate context switch occurs.
- Ready → Running: The task becomes the highest-priority Ready task (either because the current Running task blocked or because the scheduler was invoked by a timer interrupt). The context switch time is bounded.

**Context Switching: The Cost of Preempting.** When the scheduler switches from one task to another, it must save the current task's register state and restore the next task's register state. This context switch has a deterministic cost:

On ARM Cortex-M at 100MHz:
- Register save/restore: 8 floating-point registers + 16 integer registers = 24 registers × 4 bytes = 96 bytes of stack writes/reads
- Context switch time: approximately 2-4μs (hardware-assisted by the Cortex-M exception model)
- Total overhead per context switch: approximately 3-5μs

This is the *hidden cost* of multitasking. If the system runs 100 tasks with an average time slice of 1ms, the context switch overhead is approximately (100 × 5μs) / 1000ms = 0.05% — negligible. But if the time slice is 10μs (a pathological case), the overhead becomes (100 × 5μs) / (100 × 10μs) = 50% — half the CPU time is spent switching tasks. This is why RTOSes allow the designer to set time slices appropriately, and why tickless idle modes exist for low-power systems.

**Interrupt Handling: The Signal from the World.** Interrupts are the mechanism by which the outside world signals the RTOS. When an interrupt occurs (e.g., a sensor triggers, a timer expires, a network packet arrives), the CPU:

1. Saves the current context (automatically, by hardware on ARM Cortex-M)
2. Transfers control to the interrupt handler (ISR — Interrupt Service Routine)
3. The ISR processes the interrupt and may signal a task (e.g., release a semaphore, send to a message queue)
4. The ISR returns, and the scheduler determines whether to return to the interrupted task or switch to a higher-priority task that was unblocked by the ISR

The critical timing properties of interrupt handling in an RTOS:

- **Interrupt latency** — The time from the interrupt signal to the first instruction of the ISR. On ARM Cortex-M, this is typically 12-16 clock cycles (120-160ns at 100MHz).
- **ISR execution time** — The time to execute the ISR. Must be kept as short as possible — typically under 10μs for hard real-time systems. Long ISRs violate the timing guarantees of lower-priority tasks.
- **Interrupt dispatch latency** — The time from the ISR completing to the unblocked task starting to execute. On FreeRTOS with priority inheritance, this is typically 5-10μs.

The rule of thumb for ISR design: **Do the minimum in the ISR.** Read the hardware register, clear the interrupt, and signal a task. Let the task do the real work. An ISR that takes more than 10-20μs is too long and must be refactored.

**The RúnarRT Platform.** The University of Yggdrasil's RúnarRT platform is a real-time framework built on top of Zephyr RTOS (for connected devices) and FreeRTOS (for deeply embedded systems). It provides:

- A task configuration DSL (domain-specific language) for declaring tasks, priorities, periods, and deadlines
- Automatic generation of response time analysis reports from the task configuration
- Priority inheritance mutexes with bounded priority inversion
- Fixed-size message queues and memory pools (no dynamic allocation at runtime)
- A deterministic logging system that stores logs in a ring buffer and flushes only when the system is idle
- Integration with the University's SleipnirProf real-time profiling system

Students will use RúnarRT throughout the course for hands-on labs. The development environment consists of a VS Code extension with the Zephyr/FreeRTOS SDK, an ARM Cortex-M4 development board (STM32F407), and a RISC-V board (ESP32-C3) for comparison.

#### Required Reading

- Kveldúlfsson, E. (2037). *The Unforgiving Sea*. Chapter 4: "The Rudder and the Helm."
- FreeRTOS Documentation (2040). *Task Management*, *Queue Management*, *Semaphore/Mutex*. https://www.freertos.org/
- Zephyr Project Documentation (2040). *Kernel Services*, *Scheduling*, *Interrupts*. https://docs.zephyrproject.org/
- Labrosse, J. J. (2002). *MicroC/OS-II: The Real-Time Kernel* (2nd ed.). CMP Books. Chapters 2-4. [A classic RTOS implementation reference.]

#### Discussion Questions

1. The lecture states that ISR execution time should be under 10μs. But what if the hardware requires a longer operation (e.g., reading a 256-byte SPI flash page)? How should the ISR and task divide the work?
2. Context switch overhead is approximately 3-5μs on ARM Cortex-M. On a system with 50 tasks all switching at 1kHz, how much CPU time is spent on context switching? Is this acceptable?
3. The RúnarRT platform generates response time analysis reports from the task configuration. What happens when the analysis says the task set is unschedulable? Should the platform refuse to start, or should it flag the issue and continue?

---

### ᚨ Lecture 4: The Lock and the Key — Synchronization and Resource Sharing in Real-Time Systems

**Date:** Week 2, Session 2

#### Overview

In a real-time system, tasks must share resources: data structures, hardware peripherals, communication channels. Sharing requires synchronization — mutual exclusion, in the simplest case. But synchronization in a real-time system is fundamentally different from synchronization in a general-purpose system. A mutex that works perfectly in Linux may cause a real-time system to crash, miss deadlines, or — worst of all — work perfectly in testing and fail unpredictably in the field. This lecture covers the priority inversion problem, the Priority Inheritance Protocol, the Priority Ceiling Protocol, and the design of deterministic synchronization primitives for hard real-time systems.

#### Lecture Notes

**The Priority Inversion Disaster: Mars Pathfinder (1997).** The canonical example of priority inversion in a real-time system is the Mars Pathfinder mission, which experienced a system reset on July 4, 1997, within days of landing on Mars. The root cause:

1. A low-priority task (the data distribution task) acquired a mutex protecting a shared data structure.
2. A medium-priority task (the communications task) preempted the low-priority task, preventing it from releasing the mutex.
3. A high-priority task (the attitude control task) needed the mutex but was blocked by the low-priority task, which was preempted by the medium-priority task.

The high-priority task was blocked indefinitely — not by a higher-priority task, but by a *medium*-priority task. This is priority inversion: a high-priority task is blocked by a lower-priority task that holds a resource it needs. The watchdog timer eventually triggered a system reset, which recovered the Pathfinder, but the incident highlighted a fundamental flaw in naive mutex usage for real-time systems.

**The Priority Inheritance Protocol (PIP).** The solution implemented on the Pathfinder (after a software patch was uploaded from Earth) is the Priority Inheritance Protocol:

When a high-priority task H is blocked on a mutex held by a low-priority task L, L's priority is *temporarily elevated* to H's priority. This prevents medium-priority tasks from preempting L, allowing L to complete its critical section and release the mutex quickly. Once the mutex is released, L's priority returns to its original value.

PIP is simple to implement and effective for most uniprocessor real-time systems. However, it has limitations:

- **Chained blocking** — If H is blocked by L on mutex M₁, and L is blocked by task M on mutex M₂, the chain of priority inheritance can grow arbitrarily long. In the worst case, a high-priority task can be blocked for the sum of all lower-priority critical sections.
- **Deadlock** — PIP does not prevent deadlock. If H holds mutex M₁ and waits for M₂, while task L holds M₂ and waits for M₁, both tasks are deadlocked regardless of priority inheritance.

**The Priority Ceiling Protocol (PCP).** The Priority Ceiling Protocol (Sha, Rajkumar, and Lehoczky, 1990) addresses the limitations of PIP by assigning each mutex a *priority ceiling* — the maximum priority of any task that may acquire the mutex. When a task acquires a mutex, its priority is set to the ceiling of that mutex, not just to the priority of the task it's blocking.

PCP prevents both chained blocking and deadlock:

- **No chained blocking** — A task can only be blocked by at most one lower-priority task (the one holding the mutex with the highest ceiling). Once that task releases the mutex, the high-priority task runs immediately.
- **No deadlock** — A task can only acquire a mutex if its priority is strictly higher than the highest ceiling of all currently locked mutexes. This prevents circular wait, which is one of the four necessary conditions for deadlock (Coffman conditions).

The priority ceiling of a mutex is computed at design time: `ceiling(M) = max(priority(T))` for all tasks T that may acquire mutex M. This requires knowing all tasks and their mutex usage at design time — which is standard practice in hard real-time systems, where all tasks and their interactions must be fully analyzed before deployment.

**Stack Resource Policy (SRP).** The Stack Resource Policy (Baker, 1991) is an alternative to PCP that also prevents unbounded priority inversion and deadlock. SRP uses the concept of *preemption levels* (inversely related to priorities) and a *system ceiling* (the maximum preemption level of all currently locked resources). A task can only start a new critical section if its preemption level is greater than the current system ceiling.

SRP has an advantage over PCP in multiprocessor systems: it can be extended to multiprocessor scheduling (MSRP — Multiprocessor Stack Resource Policy), while PCP is fundamentally a uniprocessor protocol. In 2040, as multi-core microcontrollers become common (ARM Cortex-M55, RISC-V multi-core), SRP is gaining traction for deterministic multi-core real-time systems.

**Spinlocks vs. Mutexes vs. Semaphores.** The choice of synchronization primitive depends on the context:

| Primitive | Use When | Blocking | Overhead | Priority Inversion Risk |
|-----------|----------|----------|----------|------------------------|
| Spinlock | Very short critical sections (< context switch time) | Wait in busy loop | Low (no context switch) | None on single-core (interrupts disabled); moderate on multi-core |
| Mutex (with PIP) | Medium critical sections, uniprocessor | Task Blocked, priority boosted | Medium (context switch) | Bounded (one blocking chain) |
| Mutex (with PCP) | Safety-critical, uniprocessor | Task Blocked, ceiling priority set | Medium (context switch) | Eliminated |
| Semaphore | Signaling (not mutual exclusion) | Task Blocked | Medium (context switch) | Not applicable (signaling, not exclusion) |

Critical design rule: **Never use a semaphore for mutual exclusion in a real-time system.** Semaphores count signals; they don't enforce exclusive access. The classic "binary semaphore used as mutex" pattern has no priority inheritance and can cause unbounded priority inversion. Use a mutex with PIP or PCP.

#### Required Reading

- Sha, L., Rajkumar, R., & Lehoczky, J. P. (1990). "Priority Inheritance Protocols: An Approach to Real-Time Synchronization." *IEEE Transactions on Computers*, 39(9), 1175-1185. [The foundational paper on PIP and PCP.]
- Buttazzo, G. C. (2011). *Hard Real-Time Computing Systems* (3rd ed.). Chapter 5: "Resource Sharing."]
- Kveldúlfsson, E. (2037). *The Unforgiving Sea*. Chapter 5: "The Lock and the Key."
- Baker, T. P. (1991). "Stack-Based Scheduling of Realtime Processes." *Real-Time Systems*, 3(1), 67-100. [The SRP paper.]

#### Discussion Questions

1. The Mars Pathfinder priority inversion was resolved by uploading a software patch from Earth — a process that took days. In a safety-critical system (e.g., a pacemaker, an autonomous vehicle), you cannot upload patches while the system is running. How should real-time systems be designed to prevent priority inversion from reaching the field?
2. PCP prevents deadlock by ensuring that a task can only acquire a mutex if its priority is higher than the highest ceiling of all locked mutexes. But this means a low-priority task might be unable to acquire a mutex even though no high-priority task currently holds it. Is this acceptable? What are the utilization implications?
3. On a multi-core processor, spinlocks are preferable to mutexes for very short critical sections because spinning avoids the context switch overhead. But spinning wastes CPU cycles on the other core. How should the real-time engineer decide the threshold below which spinning is preferable to blocking?

---

### ᚱ Lecture 5: Iron Memories — Deterministic Memory Management for Real-Time Systems

**Date:** Week 3, Session 1

#### Overview

A ship's hull must be watertight — any leak, however small, can become catastrophic over time. A real-time system's memory management must be similarly deterministic: any unbounded allocation, any fragmentation, any garbage collection pause can violate a deadline. This lecture covers static allocation, memory pools, stack analysis, and the iron rule of hard real-time: *never call malloc() after initialization*.

#### Lecture Notes

**Why malloc() Is the Enemy of Determinism.** The standard C library's `malloc()` function is fundamentally incompatible with hard real-time constraints. Here's why:

1. **Unbounded allocation time** — `malloc()` must search the free list for a block of the right size. In the worst case, this search is O(n) where n is the number of free blocks. Under memory pressure, `malloc()` may also coalesce adjacent free blocks (another O(n) operation), call the operating system for more memory (an unbounded system call), or fail entirely (returning NULL).

2. **Fragmentation** — Over time, `malloc()` and `free()` fragment the heap into small, non-contiguous free blocks. Even if the total free memory is sufficient, no single block may be large enough for a new allocation. Fragmentation is data-dependent and cannot be predicted at design time.

3. **Garbage collection** — If the language uses garbage collection (Java, C#, Python, Rust with certain allocators), the GC must periodically pause all threads to reclaim unused memory. Even "concurrent" garbage collectors introduce latency spikes of 100μs-10ms — unacceptable for hard real-time deadlines in the 10-100μs range.

The iron rule of hard real-time: **Allocate all memory at system initialization. Never allocate or deallocate memory during the mission phase.** This eliminates all three problems: allocation time is zero (the memory is pre-allocated), fragmentation is impossible (no deallocation means no fragmentation), and garbage collection is unnecessary (no garbage is generated).

**Static Allocation: The Foundation.** In a hard real-time system, all memory is allocated at compile time or during system initialization:

```c
// Static allocation for a real-time task's stack and data
#define TASK_STACK_SIZE 512  // bytes
#define MAX_MESSAGES 32

// Task stack — allocated statically, not from the heap
static StackType_t taskStack[TASK_STACK_SIZE / sizeof(StackType_t)];

// Task control block — allocated statically
static StaticTask_t taskControlBlock;

// Message queue storage — allocated statically
static uint8_t messageQueueStorage[MAX_MESSAGES * sizeof(Message_t)];
static StaticQueue_t queueControlBlock;

// Create task with static allocation
TaskHandle_t task = xTaskCreateStatic(
    taskFunction,
    "SensorTask",
    TASK_STACK_SIZE / sizeof(StackType_t),
    NULL,
    PRIORITY_SENSOR,
    taskStack,
    &taskControlBlock
);
```

There are no calls to `malloc()`, `free()`, `new`, or `delete`. Every byte of memory is accounted for at compile time. The total memory usage is known before the system boots, and the memory layout is fixed.

**Memory Pools: Fixed-Size Allocation for Necessary Dynamic Allocation.** Some real-time systems genuinely need dynamic allocation — message queues of variable depth, dynamically created tasks, or data structures that grow and shrink. For these cases, the solution is *memory pools*: pre-allocated blocks of fixed-size memory that can be claimed and released in O(1) time.

A memory pool is created at initialization with a fixed number of fixed-size blocks:

```c
// Create a memory pool for messages
#define POOL_BLOCK_SIZE sizeof(Message_t)
#define POOL_BLOCK_COUNT 64

static uint8_t poolStorage[POOL_BLOCK_COUNT * POOL_BLOCK_SIZE];
static MemoryPool_t messagePool;

MemoryPool_Create(&messagePool, poolStorage, POOL_BLOCK_COUNT, POOL_BLOCK_SIZE);
```

Allocation from a pool is O(1): take the first free block from the free list. Deallocation is O(1): add the block back to the free list. There is no fragmentation because all blocks are the same size. There is no `malloc()` search because the free list is a simple linked list.

Memory pools do have a limitation: the number of blocks is fixed. If the pool is exhausted, the allocation fails. This is a feature, not a bug — in a hard real-time system, running out of memory is a *design error*, not a runtime surprise. The engineer must analyze the worst-case memory requirements at design time and allocate enough blocks.

****Stack Analysis: The Most Overlooked Source of Failures.** Stack overflow is one of the most common and most insidious bugs in real-time systems. Unlike heap overflow (which causes a crash or corruption that's relatively easy to diagnose), stack overflow corrupts memory silently — the stack grows into adjacent memory, overwrites other data structures, and the system continues running with corrupted state until an unrelated operation fails hours or days later.

The worst-case stack usage for each task must be analyzed at design time. This analysis includes:

1. **Local variables** — The sum of all local variable sizes in the task's call chain. This is straightforward for non-recursive tasks: trace every possible call path and sum the local variable sizes.
2. **Register context** — The size of the saved register context during a context switch (approximately 100-200 bytes on ARM Cortex-M, depending on whether floating-point registers are saved).
3. **Interrupt context** — The maximum stack space consumed by interrupt handlers. On ARM Cortex-M, nested interrupts can stack their contexts on the task's stack, consuming additional space.
4. **Function call overhead** — The frame pointer, return address, and alignment padding for each function call (typically 8-16 bytes per call on ARM).

The total worst-case stack size is: `Stack = Σ(local_vars) + register_context + interrupt_context + Σ(call_overhead) + safety_margin`

The safety margin is typically 20-30% of the calculated stack size. In practice, tools like Stack Analysis for Embedded Systems (SATAN) and the RúnarRT stack analyzer can compute worst-case stack usage automatically by analyzing the binary's call graph. The ARM Cortex-M also provides hardware stack checking: the `PSP` (Process Stack Pointer) can be compared against a `MSPLIM` (Main Stack Pointer Limit) register, generating a MemManage exception on stack overflow.

**Memory-Mapped I/O: The Hardware-Software Contract.** Embedded systems communicate with hardware peripherals through memory-mapped I/O — special memory addresses that, when read or written, control hardware instead of storing data. On ARM Cortex-M, the peripheral registers are mapped in the address range 0x40000000-0x4FFFFFFF.

The `volatile` keyword in C is essential for memory-mapped I/O. It tells the compiler that the variable's value may change at any time (because the hardware can modify it) and prevents the compiler from optimizing away reads or writes:

```c
// Without volatile: compiler may optimize away repeated reads
volatile uint32_t * const UART_DR = (volatile uint32_t *)0x40000000;  // UART data register
volatile uint32_t * const UART_SR = (volatile uint32_t *)0x40000004;  // UART status register

// Read a byte from UART (spin until data is ready)
while ((*UART_SR & 0x01) == 0) {  // Wait for RXNE (receive not empty) flag
    // Without volatile, the compiler might read UART_SR once and cache the result
}
char data = *UART_DR;
```

Without `volatile`, the compiler is free to read the status register once and cache the result in a register — spinning forever because the cached value never changes. This is one of the most common bugs in embedded systems programming, and it's invisible in testing because compiler optimizations vary across build configurations.

**Worst-Case Execution Time (WCET) Analysis.** Stack analysis is a subset of a larger discipline: Worst-Case Execution Time (WCET) analysis. WCET is the maximum time a task can take to execute, considering all possible inputs, all possible code paths, and all possible hardware states. WCET analysis is required for:

- **Schedulability analysis** — The C_i term in the response time equation must be the WCET, not the average execution time.
- **Certification** — DO-178C (avionics) and ISO 26262 (automotive) require WCET analysis for all tasks with safety-critical deadlines.
- **Watchdog timer configuration** — The watchdog timeout must be set to at least the worst-case execution time of the longest task, plus overhead.

WCET analysis methods:

| Method | Accuracy | Effort | Certification |
|--------|----------|--------|---------------|
| Measurement-based | Under-approximates (may miss worst case) | Low | Not acceptable for hard real-time |
| Static analysis | Over-approximates (safe but pessimistic) | High | Acceptable for DO-178C, ISO 26262 |
| Hybrid (measurement + static) | Tight over-approximation | Moderate | Acceptable with justification |

Static WCET analysis tools (aiT, OTAWA, SWEET) analyze the binary's control flow graph, identify loops and recursive calls, and compute the worst-case path through the code. The analysis must account for:

- **Pipeline effects** — Instruction pipeline stalls, branch prediction misses, cache misses
- **Bus contention** — Multiple masters competing for the memory bus
- **Interrupt overhead** — Time spent in interrupt handlers during task execution
- **Processor-specific timing** — The same instruction can take different numbers of cycles depending on the processor state

In 2040, the University's RúnarRT platform includes a WCET analyzer that produces certified-exempt reports (the analyzer itself is not certified, but its output is used as engineering evidence for DO-178C/ISO 26262 certification).

#### Required Reading

- Kveldúlfsson, E. (2037). *The Unforgiving Sea*. Chapter 6: "Iron Memories."
- Buttazzo, G. C. (2011). *Hard Real-Time Computing Systems* (3rd ed.). Chapter 7: "Memory Management."
- Wilhelm, R., et al. (2008). "The Worst-Case Execution-Time Problem — Overview of Methods and Survey of Tools." *ACM Transactions on Embedded Computing Systems*, 7(3), 1-53.
- FreeRTOS Documentation (2040). *Stack Overflow Detection*, *Memory Pools*. https://www.freertos.org/

#### Discussion Questions

1. The iron rule says "never call malloc() after initialization." But many off-the-shelf libraries (JSON parsers, XML parsers, network stacks) use malloc internally. How should a real-time engineer deal with libraries that allocate memory dynamically?
2. Memory pools require the engineer to specify the maximum number of blocks at design time. If the pool is too small, the system fails; if it's too large, the system wastes memory. How should the engineer determine the right pool size for a system with 95th-percentile load and 99.999th-percentile load?
3. Static WCET analysis over-approximates — it may report a WCET of 500μs when the actual worst case is 200μs. This pessimism reduces the schedulable utilization of the system. Is there a way to get tighter WCET bounds without sacrificing safety?

---

### ᚲ Lecture 6: Speaking Across the Void — Real-Time Communication Protocols

**Date:** Week 3, Session 2

#### Overview

A longship's crew communicates through shouted commands, hand signals, and the rhythm of the drum. Embedded systems communicate through protocols: CAN, SPI, I2C, UART, MQTT, DDS. This lecture covers the communication protocols used in real-time and embedded systems, their timing guarantees, their failure modes, and how to choose the right protocol for the right task.

#### Lecture Notes

**The Communication Hierarchy.** Embedded systems communicate at multiple scales:

| Range | Protocol | Speed | Latency | Use Case |
|-------|----------|-------|---------|----------|
| On-chip | AMBA AHB/APB | 100+ MHz | <10ns | CPU ↔ peripherals |
| Board-level | SPI | 1-100 MHz | <1μs | MCU ↔ sensors, displays |
| Board-level | I2C | 100kHz-3.4MHz | <10μs | MCU ↔ low-speed devices |
| Board-level | UART | 9600-10Mbps | Variable | MCU ↔ MCU, GPS, Bluetooth |
| Vehicle-level | CAN | 1Mbps | <1ms | ECU ↔ ECU |
| Vehicle-level | CAN FD | 5-8Mbps | <1ms | ECU ↔ ECU (higher bandwidth) |
| Building-level | MQTT | Variable | 10-100ms | IoT ↔ cloud |
| Building-level | DDS | Variable | 100μs-10ms | IoT ↔ IoT (real-time) |

Each protocol trades off speed, latency, determinism, reliability, and complexity. The real-time engineer must choose the protocol that meets the timing requirements with the minimum complexity.

**CAN Bus: The Workhorse of Automotive and Industrial.** The Controller Area Network (CAN) bus, developed by Bosch in 1983 and standardized as ISO 11898, is the dominant protocol for in-vehicle communication. A modern automobile has 50-100 Electronic Control Units (ECUs) communicating over 5-10 CAN buses.

CAN's key properties for real-time systems:

- **Priority-based bus arbitration** — When two nodes transmit simultaneously, the node with the lower message ID wins access to the bus (wired-AND dominant bit logic). This is priority-based arbitration — the most important message always wins, with no collision overhead.
- **Bounded worst-case latency** — For a CAN bus operating at 1Mbps, the worst-case latency for an 8-byte standard frame is approximately 130μs. This is provably bounded, making CAN suitable for hard real-time.
- **Built-in error detection** — CRC, bit stuffing, and ACK mechanisms detect transmission errors. A node that detects an error transmits an error frame, causing all nodes to discard the corrupted message.
- **Fault confinement** — A node that repeatedly generates errors is automatically disconnected from the bus ( Error Passive → Bus Off), preventing a faulty node from disrupting the entire network.

**SPI and I2C: Board-Level Communication.** SPI (Serial Peripheral Interface) and I2C (Inter-Integrated Circuit) are the two dominant protocols for short-range communication between a microcontroller and peripheral devices (sensors, displays, ADCs, DACs).

SPI is full-duplex, high-speed (up to 100MHz), and requires four wires (SCLK, MOSI, MISO, CS). It's simple, fast, and deterministic — the master controls the clock, so there are no bus arbitration issues. The disadvantage is the number of chip-select lines: each peripheral requires a separate CS pin, which limits scalability.

I2C is half-duplex, slower (up to 3.4MHz in High-Speed mode), and requires only two wires (SDA, SCL). It supports multi-master operation with bus arbitration (similar to CAN but simpler). The disadvantage is that arbitration can add latency and the protocol is more complex than SPI.

**MQTT and DDS: From Edge to Cloud.** MQTT (Message Queuing Telemetry Transport) is the dominant protocol for IoT device communication with cloud services. It's lightweight (a minimal MQTT client fits in 10KB of RAM), supports three quality-of-service levels (QoS 0: at most once, QoS 1: at least once, QoS 2: exactly once), and works well over unreliable networks (TCP with automatic reconnection).

However, MQTT is not suitable for hard real-time communication. It provides no latency guarantees, has no built-in data model (messages are opaque blobs), and the broker architecture (all messages pass through a central server) creates a single point of failure and a latency bottleneck.

DDS (Data Distribution Service) is the real-time alternative to MQTT. DDS is an OMG standard for publish-subscribe communication with quality-of-service policies that include:

- **Reliability** — Best-effort or reliable delivery
- **Latency** — Maximum acceptable latency (deadline)
- **History** — Keep last N samples, keep all samples, or keep none
- **Durability** — Transient-local (new subscribers receive last value), persistent (values survive restarts)
- **Presentation** — Coherent access (transactions) or instance-level access

DDS is used in military, aerospace, and autonomous vehicle systems where real-time data distribution is required. In 2040, DDS is the communication backbone of the University's RúnarRT edge computing platform, providing deterministic data distribution between sensors, actuators, and AI inference nodes.

#### Required Reading

- Kveldúlfsson, E. (2037). *The Unforgiving Sea*. Chapter 7: "Speaking Across the Void."
- ISO 11898-1:2015. *Road vehicles — Controller area network (CAN) — Part 1: Data link layer and physical signalling.*
- Object Management Group (2015). *Data Distribution Service (DDS) Version 1.4.* https://www.omg.org/spec/DDS/
- Corrigan, S. (2008). *Controller Area Network (CAN) Basics.* Texas Instruments Application Report SLOA101.

#### Discussion Questions

1. CAN uses priority-based arbitration where the lowest message ID always wins the bus. But this means low-priority messages can be starved indefinitely under heavy load. How should a real-time engineer design the message ID assignment to prevent starvation while ensuring the most critical messages get bus access?
2. SPI requires a separate chip-select line for each peripheral. In a system with 20 SPI devices, this means 20 GPIO pins just for chip selects — a significant cost on a 48-pin microcontroller. What are the alternatives, and what are their tradeoffs?
3. DDS provides QoS policies for latency, reliability, and history. But configuring these policies for a system with 1000 topics and 100 publishers is a combinatorial challenge. How should the real-time engineer approach DDS QoS configuration?

---

### ᚷ Lecture 7: The Smith's Forge — Embedded Hardware: Microcontrollers, FPGAs, and the Edge

**Date:** Week 4, Session 1

#### Overview

Every real-time system runs on hardware, and the hardware constrains the software. The smith cannot forge a sword from clay; the real-time engineer cannot achieve microsecond latency on a Raspberry Pi running Linux. This lecture covers the hardware platforms used in real-time and embedded systems: microcontrollers (ARM Cortex-M, RISC-V), FPGAs, and the emerging edge-AI platforms that are reshaping the landscape in 2040.

#### Lecture Notes

**The Microcontroller Landscape in 2040.** The microcontroller is the workhorse of embedded systems — a single chip containing a CPU core, flash memory, SRAM, and a rich set of peripherals. The dominant architectures in 2040:

| Platform | Core | Clock | Flash | SRAM | Target Applications |
|----------|------|-------|-------|------|---------------------|
| STM32F4 (Cortex-M4) | ARM Cortex-M4F | 168MHz | 512KB-2MB | 192KB-256KB | General-purpose real-time |
| STM32H7 (Cortex-M7) | ARM Cortex-M7 | 480MHz | 1-2MB | 1MB | High-performance real-time |
| ESP32-C6 (RISC-V) | RISC-V RV32IMAC | 160MHz | 512KB | 512KB | IoT, wireless connectivity |
| ESP32-P4 (RISC-V) | RISC-V dual-core | 400MHz | 2MB | 1MB | Edge AI, multimedia |
| NXP i.MX RT1180 | Cortex-M33 + Cortex-M7 | 600MHz | 4.8MB | 5MB | Automotive, industrial |
| Nordic nRF54 | Cortex-M33 | 320MHz | 2MB | 1.5MB | Bluetooth, low-power IoT |

Key trends in 2040:

- **RISC-V adoption** — RISC-V is gaining ground in embedded systems due to its open ISA, customizability, and freedom from ARM licensing fees. The ESP32-C6 and ESP32-P4 are leading RISC-V microcontrollers for IoT.
- **Multi-core microcontrollers** — Heterogeneous cores (Cortex-M33 for security + Cortex-M7 for performance) are increasingly common. The NXP i.MX RT1180 runs a secure firmware on the Cortex-M33 and the real-time application on the Cortex-M7.
- **On-chip AI accelerators** — Microcontrollers with built-in neural network accelerators (ARM Ethos-U55, Cadence Tensilica NNE) enable edge AI inference at <10mW power consumption. This is the hardware foundation for the "AI at the edge" lecture (Lecture 10).

**Peripheral Interfacing: The Microcontroller's Senses and Hands.** A microcontroller's peripherals are its connection to the physical world. The key peripherals for real-time systems:

- **GPIO** — General-purpose input/output. The simplest peripheral: set a pin high or low, or read its state. Used for LED control, button input, relay driving.
- **ADC/DAC** — Analog-to-digital and digital-to-analog converters. Convert analog sensor signals (temperature, pressure, voltage) to digital values and vice versa. Resolution is typically 12 bits (4096 levels) to 16 bits (65536 levels).
- **PWM** — Pulse-width modulation. Generate a square wave with controllable duty cycle for motor control, LED dimming, and power conversion.
- **Timers** — The heartbeat of real-time systems. Hardware timers generate periodic interrupts (for task scheduling), measure elapsed time (for performance profiling), and produce PWM signals.
- **DMA** — Direct Memory Access. Offload data transfer from the CPU to a dedicated hardware controller. DMA can transfer data from ADC to SRAM, or from SRAM to a peripheral, without CPU intervention — freeing the CPU for real-time tasks.

**FPGA: The Configurable Forge.** Field-Programmable Gate Arrays (FPGAs) are chips whose hardware can be reconfigured after manufacturing. An FPGA contains an array of configurable logic blocks (CLBs), programmable interconnects, and dedicated hardware blocks (DSP slices, block RAM, transceivers).

FPGAs are used in real-time systems when:

- **Sub-microsecond latency is required** — The FPGA processes data in hardware, not software. There is no instruction fetch, no instruction decode, no cache miss. A pipeline from sensor input to actuator output can be implemented in 1-10 clock cycles (10-100ns at 100MHz).
- **Massive parallelism is required** — Image processing, signal processing, and cryptographic operations benefit from the FPGA's ability to process thousands of data elements simultaneously.
- **Custom protocols are needed** — Industrial protocols (PROFINET, EtherCAT, SERCOS) require precise timing that general-purpose processors can't provide. FPGAs implement these protocols in hardware.
- **Safety certification requires hardware determinism** — FPGAs have no caches, no pipelines (in the CPU sense), and no interrupts. Every operation takes a known number of clock cycles. This makes WCET analysis straightforward.

The primary disadvantages of FPGAs are: (1) higher cost than microcontrollers, (2) higher power consumption, (3) longer development time (HDL coding is more complex than C/C++ coding), and (4) a smaller pool of developers compared to C/C++.

**The Edge-AI Revolution.** The most significant development in embedded hardware in the 2020-2040 decade is the emergence of edge-AI accelerators — small, low-power chips that can run neural network inference at the edge without cloud connectivity:

- **ARM Ethos-U55/U65** — MicroNPU for Cortex-M systems. 32-256 MAC/cycle, 0.5-2 TOPS, <10mW. Runs quantized INT8 models.
- **Google Edge TPU** — Custom ASIC for TensorFlow Lite inference. 4 TOPS, <2W. Used in Coral Dev Board.
- **Intel Movidius VPU** — Vision Processing Unit for camera-based inference. 4 TOPS, <1W.
- **Cadence Tensilica NNE** — Configurable neural network engine for custom SoC designs.

These chips enable real-time AI inference on battery-powered devices: anomaly detection on vibration sensors, object detection on drone cameras, voice recognition on hearing aids. The challenge for the real-time engineer is that neural network inference is *data-dependent* — the execution time varies based on the input data. A quantized INT8 model may take 1ms for one input and 1.5ms for another. This variability makes WCET analysis challenging and requires either pessimistic bounds or model-specific timing analysis.

#### Required Reading

- Kveldúlfsson, E. (2037). *The Unforgiving Sea*. Chapter 8: "The Smith's Forge."
- Yiu, J. (2013). *The Definitive Guide to ARM Cortex-M0 and Cortex-M0+ Processors*. Newnes. [Updated for Cortex-M4/M7 in 2040 editions.]
- Pong, P. K. T. (2020). *FPGA Prototyping by VHDL Examples: Xilinx MicroBlaze MCS*. Wiley.
- MITRE Corporation (2040). *Edge AI for Safety-Critical Systems: Challenges and Opportunities.* Technical Report MTR-2040-017.

#### Discussion Questions

1. FPGAs provide hardware-level determinism but require HDL expertise. Microcontrollers with NVIC (ARM Cortex-M) provide microsecond-level determinism with C/C++ development. When is the FPGA's sub-microsecond determinism worth the development cost?
2. The lecture notes that neural network inference is data-dependent — execution time varies based on input. This violates the deterministic execution requirement of hard real-time. How should the real-time engineer handle this for safety-critical systems?
3. RISC-V is gaining ground against ARM in embedded systems due to its open ISA. What are the implications for real-time software — does the instruction set architecture affect real-time scheduling, or is the programming model more important?

---

### ᚹ Lecture 8: The Shipwright's Oath — Safety-Critical Software Certification

**Date:** Week 4, Session 2

#### Overview

A shipwright who builds a vessel that sinks is disgraced. A software engineer who builds a system that kills is something far worse. Safety-critical software — software whose failure can cause loss of life, significant property damage, or environmental harm — requires a level of rigor that goes beyond good engineering practice. It requires *certification*: a formal process by which an independent authority verifies that the software meets safety requirements. This lecture covers the major safety standards (DO-178C for aviation, ISO 26262 for automotive, IEC 62304 for medical devices), the certification process, and the cost and effort involved.

#### Lecture Notes

**The Safety Standards Landscape.** Three safety standards dominate the embedded systems industry:

| Standard | Domain | Safety Integrity Levels | Top Level | Typical Cost |
|----------|--------|------------------------|-----------|-------------|
| DO-178C | Aviation | DAL A-E (A = catastrophic, E = no effect) | DAL A: ~$10K per line of code | $5-50M per project |
| ISO 26262 | Automotive | ASIL A-D (D = highest safety) | ASIL D: ~$5K per line of code | $2-20M per project |
| IEC 62304 | Medical | Class A-C (C = highest risk) | Class C: ~$2K per line of code | $1-10M per project |

These standards share a common philosophy: the rigor of the development process must be proportional to the risk of the software's failure. Software whose failure could cause a plane to crash (DO-178C DAL A) requires far more evidence than software whose failure could cause a minor inconvenience (DO-178C DAL E).

**DO-178C: The Gold Standard.** DO-178C ("Software Considerations in Airborne Systems and Equipment Certification") is the most rigorous and most expensive safety standard in the world. It defines five Design Assurance Levels (DALs):

- **DAL A** — Software whose failure could cause a catastrophic failure condition (loss of the aircraft, multiple fatalities). Examples: primary flight controls, engine control, navigation.
- **DAL B** — Software whose failure could cause a hazardous failure condition (significant reduction in safety margins, physical distress). Examples: autopilot, air data system.
- **DAL C** — Software whose failure could cause a major failure condition (significant reduction in safety margins, passenger discomfort). Examples: cabin pressure control.
- **DAL D** — Software whose failure could cause a minor failure condition (slight reduction in safety margins). Examples: maintenance systems, entertainment.
- **DAL E** — Software whose failure would have no effect on safety. Examples: passenger Wi-Fi.

For DAL A software, DO-178C requires:

- **Requirements traceability** — Every requirement must be traceable to a system requirement, and every test must be traceable to a software requirement. No orphan requirements, no untested code.
- **Structural coverage** — MC/DC (Modified Condition/Decision Coverage) testing. Every condition in a decision must independently affect the outcome. For a compound condition `A && B`, MC/DC requires four tests: A=true/B=true, A=false/B=true, A=true/B=false, A=false/B=false.
- **Independence** — Reviews, testing, and verification must be performed by personnel independent of the developers. The developer cannot review their own code.
- **Configuration management** — Every change to the software, the requirements, or the development environment must be tracked, reviewed, and approved.
- **Tool qualification** — Any tool used in the development process (compiler, linker, test generator) must be qualified for the appropriate DAL level. This means verifying that the tool produces correct output — which for a compiler means verifying that it generates correct machine code for all inputs.

The certification process for a DAL A avionics system takes 3-7 years and costs $10-50 million. For DAL B, 2-5 years and $5-25 million. The cost is dominated by the verification activities: the rule of thumb is that verification (testing, reviews, analysis) costs 3-5× the development cost.

**ISO 26262: Automotive Functional Safety.** ISO 26262 is the automotive equivalent of DO-178C. It defines four Automotive Safety Integrity Levels (ASILs):

- **ASIL D** — Highest safety integrity. Examples: steering, braking, airbag deployment.
- **ASIL C** — High safety integrity. Examples: adaptive cruise control, lane keeping assist.
- **ASIL B** — Medium safety integrity. Examples: dashboard, rear camera.
- **ASIL A** — Low safety integrity. Examples: infotainment, convenience features.

ISO 26262 is less prescriptive than DO-178C. It specifies *what* must be verified but gives more flexibility in *how*. For example, ISO 26262 allows the use of formal methods (model checking, theorem proving) in place of some testing requirements, whereas DO-178C only grudgingly accepts formal methods (through DO-333, the formal methods supplement).

**The Cost of Certification.** Safety certification is expensive. The cost per line of code varies by integrity level:

- DAL A / ASIL D: $5,000-10,000 per line of code (including development, verification, and certification)
- DAL B / ASIL C: $2,000-5,000 per line of code
- DAL C / ASIL B: $500-2,000 per line of code

These costs drive a fundamental design principle of safety-critical software: **minimize the amount of safety-critical code.** Partition the system into safety-critical components (which must be certified) and non-safety-critical components (which need not be certified at the same level). Use hardware isolation (memory protection, watchdog timers) to ensure that failures in non-safety-critical components cannot propagate to safety-critical components.

**The University's Certification Support.** The University of Yggdrasil's RúnarRT platform includes a certification support package that generates the traceability documentation, structural coverage reports, and configuration management artifacts required by DO-178C and ISO 26262. The package is not itself certified (certification of tools is a separate, expensive process), but it produces artifacts that significantly reduce the cost of certification by automating the most tedious and error-prone parts of the process.

#### Required Reading

- RTCA (2012). *DO-178C: Software Considerations in Airborne Systems and Equipment Certification.* [The primary reference for avionics certification — not freely available, but essential.]
- ISO (2018). *ISO 26262: Road vehicles — Functional safety.* Parts 1-10. [The primary reference for automotive certification.]
- Kveldúlfsson, E. (2037). *The Unforgiving Sea*. Chapter 9: "The Shipwright's Oath."
- Leveson, N. (2012). *Engineering a Safer World: Systems Thinking Applied to Safety*. MIT Press. Chapters 1-4. [A critical perspective on certification — why it helps and why it's not enough.]

#### Discussion Questions

1. DO-178C DAL A certification costs $10K per line of code. A modern airbag controller has approximately 100,000 lines of code. Should safety-critical systems be smaller? What are the tradeoffs between safety (more code for more features) and certification cost (less code is cheaper to certify)?
2. ISO 26262 allows formal methods (model checking, theorem proving) to replace some testing requirements. DO-178C is more conservative. Should aviation adopt formal methods more aggressively? What are the risks?
3. The lecture notes that the cost of certification drives the principle of minimizing safety-critical code. But this creates a partition between "safety-critical" and "non-safety-critical" code. What happens when a failure in non-safety-critical code (e.g., infotainment) propagates to safety-critical code (e.g., brakes) through a shared resource (e.g., CAN bus)? How should the engineer prevent this?

---

### ᚺ Lecture 9: Navigating Without Stars — Real-Time Debugging Without Printf

**Date:** Week 5, Session 1

#### Overview

A Viking navigator who cannot see the stars must rely on the wave patterns, the wind direction, and the smell of the shore. A real-time engineer who cannot pause the system or print to a console must rely on trace buffers, logic analyzers, and the ancient art of reasoning about system behavior from indirect evidence. This lecture covers the techniques for debugging real-time systems where traditional debugging methods (printf, breakpoints, single-stepping) are unavailable or distort the system's timing.

#### Lecture Notes

**Why You Can't Debug Real-Time Systems Like General-Purpose Systems.** Three fundamental constraints make traditional debugging methods ineffective or dangerous in real-time systems:

1. **Timing distortion** — `printf()` takes 10-100μs per call (depending on UART baud rate and buffer size). In a system with 100μs task periods, adding `printf()` changes the system's timing by 10-100%, making the bug unreproducible. This is Heisenbug: observing the system changes its behavior.
2. **Non-determinism from breakpoints** — Setting a breakpoint pauses the entire system. All task deadlines are missed during the pause. The system is not behaving as it would without the breakpoint.
3. **Safety constraints** — In deployed systems (medical devices, vehicles, industrial controllers), there is no debugger attached. You cannot single-step a pacemaker that is keeping someone's heart beating. You must diagnose from the evidence the system provides.

**Trace Buffers: The Real-Time Engineer's Black Box.** A trace buffer is a circular buffer in RAM that stores timestamped events without disrupting the system's timing. The event format is designed for minimal overhead:

```c
typedef struct {
    uint32_t timestamp;  // Hardware timer count (4 bytes, ~1μs resolution)
    uint8_t  event_id;   // Event type (1 byte, enum)
    uint8_t  arg1;       // First argument (1 byte)
    uint16_t arg2;       // Second argument (2 bytes)
} TraceEvent_t;  // Total: 8 bytes per event

// Trace buffer in RAM (not on the stack)
#define TRACE_BUFFER_SIZE 4096
static TraceEvent_t traceBuffer[TRACE_BUFFER_SIZE];
static volatile uint32_t traceIndex = 0;

// Inline trace function with minimal overhead
static inline void trace(uint8_t eventId, uint8_t arg1, uint16_t arg2) {
    uint32_t idx = traceIndex++;
    if (idx < TRACE_BUFFER_SIZE) {
        traceBuffer[idx].timestamp = DWT->CYCCNT;  // ARM Cortex-M cycle counter
        traceBuffer[idx].event_id = eventId;
        traceBuffer[idx].arg1 = arg1;
        traceBuffer[idx].arg2 = arg2;
    }
}
```

This trace function takes approximately 5-10 clock cycles (50-100ns at 100MHz) — fast enough to use in hard real-time tasks without affecting timing. The trace buffer is read out after the system fails (or periodically during development) and analyzed offline to reconstruct the system's behavior.

**Logic Analyzers and Oscilloscopes: Seeing the Signals.** When software trace isn't enough, the real-time engineer turns to hardware debugging tools:

- **Logic analyzer** — Captures digital signals on multiple channels simultaneously. Used to verify protocol timing (SPI, I2C, CAN), measure interrupt latency, and debug bus communication. In 2040, the Saleae Logic Pro 34 and the Siglent SDS series are standard equipment in embedded labs.
- **Oscilloscope** — Captures analog signals with high bandwidth and resolution. Used to measure signal integrity, power supply noise, and PWM timing. Essential for debugging analog sensor interfaces.
- **Protocol analyzer** — Specialized tool that decodes a specific protocol (CAN, USB, Ethernet) and presents the decoded frames. The CANalyzer (Vector) and Wireshark (for Ethernet) are industry standards.

**Post-Mortem Debugging: Reading the Wreckage.** When a real-time system crashes, the trace buffer contains the last N events before the crash (where N is the buffer size). This is the embedded systems equivalent of a flight data recorder (black box).

Post-mortem debugging proceeds as follows:

1. **Identify the crash location** — The program counter (PC) at the time of the crash (stored in the exception frame on ARM Cortex-M) tells you exactly which instruction caused the fault.
2. **Examine the stack** — The stack contents at the time of the crash reveal the call chain and local variables.
3. **Correlate with trace events** — The trace buffer shows what happened in the N events before the crash: which tasks ran, which interrupts fired, which mutexes were acquired. This timeline allows the engineer to reconstruct the sequence of events leading to the fault.
4. **Check hardware registers** — The fault status registers (CFSR, HFSR, MMFAR, BFAR on ARM Cortex-M) provide detailed information about the fault type: stack overflow, memory access violation, division by zero, undefined instruction.

The University's RúnarRT platform includes a built-in fault handler that captures the exception frame, the stack contents, and the trace buffer, formats them as a crash report, and stores the report in a reserved region of flash memory. On reboot, the crash report can be read out and analyzed using the RúnarRT Analyzer tool.

**Watchdog Timers: The Last Line of Defense.** A watchdog timer is a hardware timer that must be "kicked" (reset) periodically by the software. If the software fails to kick the watchdog within the timeout period, the watchdog resets the entire system. This is the last line of defense against software hangs:

- **Independent watchdog** — Driven by a separate clock (typically the LSI — Low-Speed Internal oscillator on ARM Cortex-M). Cannot be disabled by software. Used for safety-critical supervision.
- **Window watchdog** — Must be kicked within a time *window* (not too early, not too late). Kicking too early indicates the software is running too fast (possibly stuck in a tight loop). Kicking too late indicates the software is running too slow (possibly blocked or crashed).

Watchdog configuration is a non-trivial design decision. The timeout must be long enough to allow the longest legitimate task execution (plus interrupt overhead, plus scheduling overhead), but short enough to recover before the deadline is missed. For a system with a 100ms task period and a 10ms worst-case execution time, a watchdog timeout of 50ms provides a margin: any task that takes more than 50ms (five times its normal execution time) is clearly stuck.

#### Required Reading

- Kveldúlfsson, E. (2037). *The Unforgiving Sea*. Chapter 10: "Navigating Without Stars."
- Ganssle, J. (2008). *The Art of Debugging Embedded Systems*. Newnes. Chapters 1-4.
- ARM Limited (2040). *Cortex-M4 Technical Reference Manual: Debug and Trace*. https://developer.arm.com/
- Barr, M. (2006). *Programming Embedded Systems in C and C++*. O'Reilly. Chapter 11: "Debugging."

#### Discussion Questions

1. The trace buffer uses 8 bytes per event. A system with a 100MHz timer and a 4096-event buffer can store approximately 40ms of events. Is this sufficient for diagnosing bugs that manifest over seconds or minutes? How would you extend the trace duration without exceeding RAM limits?
2. Watchdog timers reset the entire system when the software fails to kick them. But what if the bug causes the system to enter a tight loop that kicks the watchdog correctly but doesn't perform its real function? How do you guard against this?
3. Post-mortem debugging relies on the trace buffer surviving the crash. But if the crash corrupts RAM (e.g., a stack overflow that writes over the trace buffer), the trace data is lost. How should the trace buffer be protected?

---

### ᚾ Lecture 10: The Seer at the Edge — Real-Time AI Inference on Resource-Constrained Devices

**Date:** Week 5, Session 2

#### Overview

The völva (seeress) of Norse tradition could see the future while standing in the present — a power analogous to real-time AI inference at the edge. In 2040, AI is no longer confined to cloud data centers; it runs on microcontrollers, edge processors, and embedded systems that must deliver predictions within hard timing constraints. This lecture covers the techniques for deploying neural network models on resource-constrained devices, the timing challenges of data-dependent computation, and the emerging discipline of real-time AI safety.

#### Lecture Notes

**The Edge-AI Inference Pipeline.** A real-time edge-AI system follows a strict pipeline:

1. **Sense** — Acquire data from sensors (camera, microphone, IMU, LIDAR). Real-time constraint: sampling rate must meet Nyquist requirements.
2. **Preprocess** — Normalize, filter, and transform the raw data into the model's input format. Real-time constraint: preprocessing must complete within the sensor's sample period.
3. **Infer** — Run the neural network model on the preprocessed data. Real-time constraint: inference must complete within the task's deadline.
4. **Decide** — Post-process the model's output (threshold, filter, aggregate) and make a control decision. Real-time constraint: decision must be made before the actuator's deadline.
5. **Act** — Send the control signal to the actuator. Real-time constraint: actuation must occur within the system's safety deadline.

The end-to-end latency from sense to act must be deterministic and bounded. A self-driving car that detects a pedestrian 50ms late has failed, regardless of whether the detection was correct.

**Model Compression for Edge Deployment.** Neural network models designed for cloud deployment (ResNet-152, BERT-Large, GPT-4) are too large and too slow for edge devices. The real-time engineer must compress the model while maintaining acceptable accuracy:

- **Quantization** — Reduce the model's numerical precision from 32-bit float (FP32) to 16-bit float (FP16), 8-bit integer (INT8), or even 4-bit integer (INT4). Quantization reduces model size by 2-8× and inference time by 2-4×, with typically <1% accuracy loss for INT8.
- **Pruning** — Remove weights (or entire channels) that have little impact on the output. Structured pruning (removing entire filters or channels) is hardware-friendly because it reduces the model's computational cost proportionally. Unstructured pruning (removing individual weights) requires sparse matrix operations that most accelerators don't support efficiently.
- **Knowledge distillation** — Train a smaller "student" model to mimic the behavior of a larger "teacher" model. The student model inherits the teacher's knowledge but at a fraction of the size and cost. DistilBERT (66M parameters) achieves 97% of BERT's (110M parameters) performance on GLUE benchmarks.
- **Neural Architecture Search (NAS) for Edge** — Automatically search for model architectures that meet the device's constraints (memory, latency, power). The University's RúnarRT Edge-AI toolkit uses a NAS agent that explores the architecture space with real hardware feedback, finding models that meet both accuracy and latency targets.

**WCET Analysis for Neural Networks.** The fundamental challenge of real-time AI is that neural network inference time is *data-dependent*. A quantized INT8 model may take 1.0ms for one input and 1.5ms for another (due to early-exit branches, dynamic sparsity, or conditional execution). This variability makes WCET analysis challenging.

Three approaches to bounding inference time:

1. **Pessimistic bounding** — Measure the maximum observed inference time across all test inputs and add a safety margin (typically 20-50%). This is simple but may be overly pessimistic, reducing schedulable utilization.
2. **Architecture-based analysis** — For models without dynamic execution (no early exits, no conditional branches), the inference time is determined solely by the model architecture and the accelerator's throughput. Count the number of MAC operations, divide by the accelerator's throughput, add memory access latency. This gives a tight bound.
3. **Input-dependent analysis** — For models with dynamic execution, partition the input space into regions with similar execution paths and compute WCET for each region. This is more precise but requires understanding the model's internal behavior.

The RúnarRT Edge-AI toolkit includes a timing analyzer that measures inference time on the target hardware for a representative input distribution and produces a WCET estimate with a confidence interval. For ASIL B systems (where a missed deadline is "major" but not "catastrophic"), the analyzer's 99.9th percentile estimate is used as the WCET. For ASIL D systems (where a missed deadline is "catastrophic"), the analyzer's maximum observed time plus a safety margin is used.

**Real-Time AI Safety: The guardians of the Seer.** An AI model that makes incorrect predictions poses a fundamentally different risk from a traditional software bug. A traditional bug either manifests or doesn't — it's deterministic. An AI model makes probabilistic predictions with probabilistic accuracy. The real-time engineer must add safety guardians around the model:

- **Input validation** — Check that the input is within the model's training distribution. Out-of-distribution inputs produce unreliable predictions.
- **Output validation** — Check that the output is within plausible bounds. A temperature prediction of -50°C in a desert is implausible and should be flagged.
- **Confidence thresholding** — If the model's confidence (softmax output, uncertainty estimate) is below a threshold, don't act on the prediction. Flag it for human review or fall back to a simpler, deterministic model.
- **Temporal consistency** — If the model's prediction changes drastically between consecutive time steps (and the input hasn't changed drastically), the prediction is unstable and should be filtered.
- **Redundancy** — Run two or more models with different architectures on the same input and compare their predictions. If they disagree, fall back to the deterministic path.

These guardians are themselves software, and they must meet the same real-time deadlines as the model. A guardian that takes 5ms to validate a model that produces results in 10ms increases the total inference time to 15ms — which must still fit within the task's deadline.

#### Required Reading

- Kveldúmr, E. (2037). *The Unforgiving Sea*. Chapter 11: "The Seer at the Edge."
- Jacob, B., et al. (2018). "Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference." *CVPR 2018*. [The foundational paper on INT8 quantization for edge deployment.]
- Howard, A. G., et al. (2017). "MobileNets: Efficient Convolutional Neural Networks for Mobile Vision Applications." *arXiv:1704.04861*.
- University of Yggdrasil Edge-AI Group (2040). *RúnarRT Edge-AI Toolkit: Timing Analysis and Safety Guardians*. Internal Technical Report UoY-EAI-2040-03.

#### Discussion Questions

1. A quantized INT8 model is 4× smaller and 2-4× faster than an FP32 model, but it introduces quantization error. In a safety-critical system (e.g., autonomous driving), is the accuracy loss from quantization acceptable? How should the engineer determine the right quantization level?
2. The real-time AI pipeline requires deterministic inference time. But neural network inference is data-dependent. Should the engineer use pessimistic bounding (wasteful but safe), architecture-based analysis (precise but hard to compute), or give up and use a deterministic algorithm instead?
3. Safety guardians (input validation, output validation, confidence thresholding) add latency to the inference pipeline. How should the engineer trade off between safety (more guardians) and latency (fewer guardians)?

---

### ᛁ Lecture 11: The Long Night — Power-Aware Real-Time Computing

**Date:** Week 6, Session 1

#### Overview

Some voyages must be made during the long night of winter, when every resource is scarce and every use of energy must be justified. Battery-powered embedded systems — pacemakers, wildlife trackers, remote sensors — face a similar constraint: they must operate for months or years on a limited energy budget. This lecture covers the intersection of real-time constraints and power constraints: low-power design, sleep modes, energy harvesting, and the discipline of doing exactly enough work and no more.

#### Lecture Notes

**The Energy Budget: A Different Kind of Deadline.** For battery-powered embedded systems, energy is as critical as time. The system must complete all its tasks before its deadline *and* before its battery is depleted. The energy budget defines how much energy is available per time unit:

- A pacemaker with a 5-year battery life and a 5mAh battery must consume less than 1μW average power.
- A wildlife GPS tracker with a 3-year battery life and a 2000mAh Li-Ion battery can afford approximately 200μW average power.
- A smart watch with a 1-day battery life and a 300mAh battery can afford approximately 100mW average power.

These energy budgets constrain every aspect of the system: the microcontroller choice, the radio protocol, the sensing frequency, and the software architecture.

**Sleep Modes: The Art of Doing Nothing.** The most effective power-saving technique is to do nothing as much as possible. Modern microcontrollers support multiple sleep modes with decreasing power consumption and increasing wake-up latency:

| Sleep Mode | ARM Cortex-M4 Power | Wake-up Time | Peripheral State |
|-------------|---------------------|-------------|-----------------|
| Active | 10-50 mA | 0 | All running |
| Sleep | 1-5 mA | ~1μs | CPU halted, peripherals running |
| Deep Sleep | 10-50 μA | ~10μs | CPU halted, most peripherals off, RAM retained |
| Standby | 1-5 μA | ~1ms | CPU halted, all peripherals off, RAM retained |
| Shutdown | 0.1-0.5 μA | ~10ms | CPU halted, all peripherals off, RAM lost |

A typical low-power duty cycle:

1. Wake from Deep Sleep on timer interrupt (takes ~10μs)
2. Read sensors (takes ~1ms)
3. Process data (takes ~5ms)
4. Transmit result via radio (takes ~10ms)
5. Enter Deep Sleep until next cycle

If the duty cycle period is 1 second, the system is active for 16ms and sleeping for 984ms. Average power = 16ms × 10mA + 984ms × 50μA ≈ 206μA. With a 2000mAh battery, the system lasts 2000mAh / 0.206mA = 9700 hours ≈ 13 months.

**Tickless Idle: Eliminating the Timer Tick.** In a traditional RTOS, the system tick timer fires every 1ms, waking the CPU from sleep to check for expired timers. This means the CPU can never sleep for more than 1ms — even when no tasks are ready to run. This wastes power.

Tickless idle eliminates the periodic tick: when all tasks are blocked and the system is about to enter sleep mode, the RTOS calculates the time until the next timer event and programs the hardware timer to wake the CPU exactly at that time. The CPU sleeps for the full idle period instead of waking every millisecond.

On ARM Cortex-M, tickless idle is implemented using the SysTick timer's reload register. Instead of reloading every 1ms, the reload value is set to the number of ticks until the next event. This can extend sleep periods from 1ms to seconds or minutes, reducing average power consumption by 10-100×.

**Energy Harvesting: Power from the Environment.** For truly battery-free operation, embedded systems can harvest energy from their environment:

- **Solar** — Indoor solar cells produce 10-100μW/cm² under typical office lighting. Outdoor solar produces 10-100mW/cm² in direct sunlight.
- **Vibration** — Piezoelectric harvesters produce 10-100μW from ambient vibration (bridges, machinery, HVAC).
- **Thermal** — Thermoelectric generators produce 10-100μW from temperature differentials of 5-20°C (body heat, industrial pipes).
- **RF** — RF energy harvesters produce 1-10μW from ambient Wi-Fi, cellular, and broadcast signals.

Energy harvesting adds a new constraint: the system can only operate when sufficient energy is available. The system must be designed to tolerate intermittent power loss — saving state to non-volatile memory before power failure and resuming from the saved state when power returns. This is the domain of **intermittent computing** (Lucia and Ransford, 2018-2040), where programs are checkpointed at strategic points and can resume after a power interruption.

**The Power-Aware Scheduling Problem.** Traditional real-time scheduling (RM, EDF) minimizes deadline misses. Power-aware scheduling adds a second objective: minimize energy consumption. The key technique is **Dynamic Voltage and Frequency Scaling (DVFS)** — reducing the CPU's clock frequency and voltage during low-demand periods. Since power consumption is proportional to V²f (where V is voltage and f is frequency), reducing both by 50% reduces power consumption by 87.5%.

DVFS scheduling problems:

- **Intra-task DVFS** — Scale voltage/frequency within a task's execution. Scale up for critical sections, scale down for non-critical sections. Requires hardware support (ARM DVFS, Intel Speed Shift).
- **Inter-task DVFS** — Scale voltage/frequency between tasks. Use the minimum frequency that allows each task to meet its deadline. This is the more common approach in real-time systems because it requires less hardware support.
- **Energy-optimal EDF** — Run tasks at the lowest frequency that meets all deadlines. For EDF-scheduled systems with predictable workloads, this can be computed analytically.

The University's RúnarRT platform includes a power-aware scheduler that combines EDF scheduling with DVFS. For each scheduling point, the scheduler computes the minimum CPU frequency that allows all remaining tasks to meet their deadlines and sets the frequency accordingly. On an ARM Cortex-M7 with DVFS support, this reduces average power consumption by 40-60% compared to fixed-frequency scheduling while guaranteeing all deadlines.

#### Required Reading

- Kveldúlfsson, E. (2037). *The Unforgiving Sea*. Chapter 12: "The Long Night."
- Lucia, B., & Ransford, B. (2018). "A Longer Road to Intermittent Computing." *IEEE Computer*, 51(10), 24-29. [Updated in 2040 with results from the University of Yggdrasil Intermittent Computing Lab.]
- Devadas, S., et al. (2038). *Power-Aware Real-Time Scheduling: Theory and Practice*. Springer. Chapters 1-3.
- FreeRTOS Documentation (2040). *Tickless Idle Mode*. https://www.freertos.org/low-power-tickless-rtos.html

#### Discussion Questions

1. A wildlife tracker must operate for 5 years on a 2000mAh battery. The GPS module consumes 20mA for 10 seconds per acquisition. How many GPS fixes per day can the system afford if all other components consume 50μA average? Show your work.
2. Energy harvesting from indoor solar provides 10-100μW/cm². A sensor node needs 5mW for 1 second every minute to acquire and transmit a reading. Is energy harvesting viable for this application? What area of solar cells would be needed?
3. DVFS reduces power consumption but increases execution time (because the CPU runs slower). In a hard real-time system, the scheduler must guarantee all deadlines even at the lower frequency. How does the scheduler determine the minimum frequency?

---

### ᛃ Lecture 12: The Longship Launched — Synthesis: Building a Complete Real-Time System

**Date:** Week 6, Session 2

#### Overview

A longship is not a collection of planks, rivets, and rope — it is a unified whole designed to cross the open sea. A real-time system is not a collection of tasks, interrupts, and protocols — it is a unified whole designed to meet its deadlines under all conditions. This final lecture synthesizes the entire course into a complete real-time system design methodology, presents a capstone project, and reflects on the unique discipline of real-time engineering.

#### Lecture Notes

**The Real-Time System Design Process: From Requirements to Deployment.** A real-time system is designed from the outside in — starting with the deadlines and working backward to the implementation:

1. **Requirements analysis** — Identify all timing requirements: task periods, deadlines, jitter constraints, and ordering constraints. Classify each requirement as hard, firm, or soft. For hard deadlines, specify the consequences of a deadline miss (safety analysis).
2. **Task design** — Decompose the system into concurrent tasks with defined periods, deadlines, worst-case execution times, and resource requirements. Apply the task decomposition criteria (cohesion, coupling, timing independence).
3. **Schedulability analysis** — Apply response time analysis (RM, DM, or EDF) to verify that all tasks meet their deadlines under worst-case conditions. If the task set is unschedulable, redesign: reduce execution times, increase periods, or reduce deadline requirements.
4. **Resource analysis** — Verify that the system has sufficient memory (stack + heap + static), sufficient peripherals (UART, SPI, I2C channels), and sufficient I/O bandwidth for the task set.
5. **Implementation** — Write the code, following the iron rules: no malloc at runtime, no unbounded loops, no blocking calls in ISRs, all shared resources protected by PIP or PCP mutexes.
6. **Verification** — Measure WCET for all tasks on the target hardware. Verify schedulability with measured (not estimated) execution times. Run stress tests at maximum load. Inject faults (bit flips, sensor failures, bus errors) and verify that the system degrades gracefully.
7. **Certification** — If the system is safety-critical, produce the certification artifacts (requirements traceability, structural coverage analysis, WCET reports, code reviews) and submit for independent verification.

**Capstone Project: A Real-Time Patient Monitor.** The course capstone project is a real-time patient monitoring system that:

- Reads ECG, SpO2, and blood pressure from three sensors at 250Hz, 100Hz, and 50Hz respectively
- Detects cardiac arrhythmias (bradycardia, tachycardia, atrial fibrillation) within 500ms of onset
- Detects hypoxemia (SpO2 < 90%) within 1 second
- Displays real-time waveforms on a 240×320 LCD screen, updated at 30Hz
- Transmits alarms to a central monitoring station via DDS with <100ms latency
- Operates on an ARM Cortex-M7 (STM32H7) with 1MB SRAM, 2MB Flash
- Must meet IEC 62304 Class C requirements (life-supporting equipment)

Students must:

1. Design the task set (periods, deadlines, WCETs, priorities) and prove schedulability
2. Implement the system on RúnarRT with static memory allocation
3. Verify WCET using the RúnarRT analyzer and SleipnirProf
4. Demonstrate correct behavior under maximum load (all sensors at maximum rate)
5. Demonstrate graceful degradation under fault injection (sensor disconnect, bus error, memory corruption)
6. Produce a requirements traceability matrix and WCET analysis report

The capstone project is worth 40% of the course grade. Students work in pairs and present their results in a final demonstration during the examination period.

**The Discipline of Real-Time Engineering.** Throughout this course, we've emphasized a discipline that distinguishes real-time engineering from general-purpose software engineering:

- **Measure, don't assume.** Every WCET is measured on the target hardware. Every stack size is analyzed. Every priority assignment is verified by schedulability analysis.
- **Analyze, don't hope.** The system is proven schedulable before deployment, not tested for schedulability in the lab. Testing can show the presence of bugs but not their absence.
- **Simplify, don't complicate.** Every line of code in a safety-critical system must be justified. Every dynamic feature (dynamic task creation, heap allocation, dynamic priority change) is a potential source of non-determinism that must be carefully analyzed.
- **Document, don't improvise.** Every requirement is traced. Every design decision is recorded. Every test is documented with its pass/fail criteria and actual results.
- **Guard, don't trust.** Watchdog timers, stack canaries, input validation, and output validation protect the system from the unexpected. The real world is hostile, and the system must be designed to survive.

**Future Directions: Real-Time Systems in 2040 and Beyond.** The field of real-time and embedded systems is evolving rapidly:

- **Multi-core real-time** — As single-core processors reach their frequency limits, multi-core MCUs (2-4 cores) are becoming common. Multi-core scheduling is fundamentally harder than uniprocessor scheduling — tasks can migrate between cores, shared caches introduce non-deterministic timing, and inter-core communication adds latency. The 2040 research frontier is deterministic multi-core scheduling with cache-aware analysis.
- **AI at the edge** — As discussed in Lecture 10, real-time AI inference on edge devices is a major growth area. The challenge is bridging the probabilistic nature of AI with the deterministic requirements of real-time systems.
- **Safety and security convergence** — Traditionally, safety (preventing harm from random faults) and security (preventing harm from intentional attacks) have been separate disciplines. In 2040, they are converging: a security vulnerability can cause a safety failure (e.g., a hacked pacemaker), and a safety measure can create a security vulnerability (e.g., a debug port left open for maintenance).
- **Intermittent computing** — As energy harvesting becomes viable, systems that can tolerate power loss and resume computation will enable new applications (implable sensors, environmental monitoring, space exploration). The research challenge is programming models and operating systems that support checkpoint/resume at arbitrary points.

**The Longship's Wake.** This course has taken you from the fundamentals of real-time scheduling theory to the cutting edge of edge-AI and intermittent computing. The central lesson is this: in real-time systems, *when* is as important as *what*. A correct answer that arrives late is wrong. A fast system that misses a deadline is failed. The real-time engineer's discipline is to make time a first-class concern — to design for timing, to verify for timing, and to never forget that the sea does not wait for the helmsman.

#### Required Reading

- Kveldúlfsson, E. (2037). *The Unforgiving Sea*. Chapters 13-15: "Synthesis," "Certification in Practice," and "The Longship Launched."
- Buttazzo, G. C. (2011). *Hard Real-Time Computing Systems* (3rd ed.). Chapters 13-14 (Multiprocessor Scheduling, Real-Time Operating Systems).
- Kleppmann, M. (2017). *Designing Data-Intensive Applications*. O'Reilly. Chapter 12: "The Future of Distributed Systems." [For context on how real-time systems fit into broader software architecture.]
- University of Yggdrasil Real-Time Systems Lab (2040). *RúnarRT Capstone Project Guide*. Internal.

#### Discussion Questions

1. The design process says "analyze, don't hope" — prove schedulability before deployment. But in practice, WCET analysis is often overly pessimistic, and the measured execution time is much lower than the analyzed WCET. Does this pessimism lead to over-engineered systems? How should the engineer balance safety (pessimistic analysis) with utilization (less pessimistic analysis)?
2. The capstone project requires IEC 62304 Class C certification evidence for a patient monitor. What are the most difficult aspects of producing this evidence? Which parts can be automated, and which require human judgment?
3. The field is moving toward multi-core real-time systems, but multi-core timing analysis is fundamentally harder due to shared caches and inter-core interference. Should safety-critical systems continue to use single-core processors until multi-core timing analysis catches up, or should they begin adopting multi-core now with conservative timing bounds?

---

## Final Examination Preparation

### Format

The final examination consists of **8 essay questions**. Students must **choose 4** to answer in depth. Each answer should be 800-1200 words and demonstrate mastery of course concepts, ability to apply them to novel situations, and critical engagement with the readings.

### Sample Questions

1. **Schedulability Crisis.** You are developing a real-time system with 6 periodic tasks under Rate-Monotonic scheduling. Response time analysis shows that τ₅ (priority 5, C₅=3ms, T₅=50ms, D₅=50ms) misses its deadline by 2ms. The system cannot be redesigned. Propose three specific strategies to make the task set schedulable, analyze the tradeoffs of each, and recommend the best approach for a safety-critical system (ASIL D).

2. **The_malloc()_Dilemma.** A development team wants to use an off-the-shelf JSON library in their DO-178C DAL B avionics system. The library calls malloc() internally. The team argues that "we'll pre-allocate enough heap memory so malloc() never fails." Critique this argument from a real-time systems perspective, identify at least three specific risks, and propose a solution that allows the team to use the library while meeting certification requirements.

3. **Priority Inheritance vs. Priority Ceiling.** Compare and contrast the Priority Inheritance Protocol (PIP) and the Priority Ceiling Protocol (PCP) for real-time synchronization. For each protocol, provide: (a) the worst-case blocking bound for a high-priority task, (b) a scenario where the protocol prevents a deadline miss that the other protocol would not, and (c) the implementation complexity. Which protocol would you recommend for a single-core automotive ECU with 20 tasks and 8 shared resources?

4. **Edge-AI Safety Architecture.** Design a safety architecture for real-time object detection on an autonomous drone. The drone must detect obstacles within 50ms and transmit avoidance commands within 10ms of detection. Propose: (a) the model compression strategy (quantization, pruning, distillation), (b) the safety guardian architecture, (c) the WCET bound and how you would verify it, and (d) the graceful degradation strategy when the model's confidence is low.

5. **Energy Budget Analysis.** A remote weather station is powered by a 10,000mAh Li-Ion battery and must operate for 5 years. The station wakes every 10 minutes, reads 4 sensors (5ms total), processes data on an ARM Cortex-M4 (10ms), and transmits via LoRa (100ms at 45mA). In Deep Sleep, the system draws 5μA. Calculate the expected battery life and determine whether the system meets the 5-year requirement. If it does not, propose three specific changes to meet the requirement.

6. **Certification and Cost Trade-offs.** A medical device company is developing a Class C (IEC 62304) infusion pump. The software team estimates 50,000 lines of code. At $2,000 per line of code for Class C certification, the total cost is $100M — more than the company can afford. Propose a strategy to reduce certification cost while maintaining safety. Your strategy should include at least three specific technical approaches and estimate the cost reduction for each.

7. **Multi-Core Real-Time: The New Frontier.** A dual-core ARM Cortex-M7 processor is being considered for a next-generation autonomous vehicle ECU. The vehicle's safety requirement is ASIL D (ISO 26262). Identify the three most significant timing analysis challenges for hard real-time scheduling on a dual-core processor with shared L2 cache, and for each challenge, propose a mitigation strategy. Discuss whether single-core processors are a better choice for ASIL D systems in 2040.

8. **Debugging the Undebuggable.** A deployed medical device (Class C, IEC 62304) is experiencing intermittent resets in the field — approximately 1 reset per 10,000 operating hours. The resets cannot be reproduced in the lab. Design a comprehensive debugging strategy that includes: (a) what data to capture in the trace buffer before each reset, (b) how to constrain the problem to specific modules, (c) how to use watchdog timer behavior to narrow the cause, and (d) how to verify the fix without a full re-certification cycle.

---

## Grading Criteria

- **A (90-100%):** Demonstrates deep understanding of all course concepts, applies them to novel situations with creativity and rigor, engages critically with the readings, and produces well-organized, clearly written answers that could serve as teaching materials.
- **B (80-89%):** Demonstrates solid understanding of most course concepts, applies them correctly to the given situations, and writes clearly organized answers with specific references to course material.
- **C (70-79%):** Demonstrates adequate understanding of core course concepts, applies them with occasional errors, and writes adequately organized answers with limited references to course material.
- **D (60-69%):** Demonstrates partial understanding of course concepts, applies them with significant errors, or writes poorly organized answers with minimal references to course material.
- **F (below 60%):** Demonstrates insufficient understanding of course concepts, fails to apply them to the given situations, or writes incoherent or off-topic answers.

---

*This course was woven by Dr. Eldgrímr Kveldúlfsson, Faculty of Computational Arts, University of Yggdrasil. The longship sails on — may your deadlines be met and your stacks never overflow.*