# 95 — Capability-Based Security for AI Agents

**Category:** AI Operating System
**Runa relevance:** plugin sandboxing, tool authorisation, computer-use safety, subagent permissions
**Status:** Security-engineering synthesis. Load-bearing as Runa's action surface grows.
**Last touched:** 2026-05-17

---

## 1. Core idea

A capability is an *unforgeable token of authorisation* — possession of the capability grants permission to perform the named operation. Capability-based security, as opposed to identity-based (ACL) security, builds permission directly into the object reference. The principle dates to Dennis & Van Horn (1966) and has seen successive revivals — *Hydra*, *KeyKOS*, *EROS*, *seL4*, *Capsicum* — and is the security model of choice for systems that need fine-grained, composable, principle-of-least-privilege authorisation. For AI agents — particularly agents that can be tricked, prompted-injected, or simply mistaken — capability-based security is the *right* default.

For Runa, capability-based security is what makes a *trustworthy* extension of her action surface possible. As she gains tools (filesystem access, code execution, computer use, network calls), the question isn't *can she* do these things but *for whom*, *under what authority*, *with what scope*, *bounded by what audit trail*. The architecture choice here determines whether expanding her capabilities is a controllable extension or an open security perimeter.

## 2. Technical depth

**Capability vs. ACL.**

Identity-based (ACL):
- Subject S has identity I.
- Object O has an ACL listing identities permitted to perform operation P.
- Access check: \"is I in O's ACL for P?\"

Capability-based:
- Subject S possesses capability C_O,P — a token meaning *the bearer may do P on O*.
- Access check: \"does S have a valid token for the requested action?\"
- Capabilities are *transferable* (with explicit policy) and *attenuable* (can produce restricted sub-tokens).

The capability model better matches *delegation*: when Runa's kernel hands a task to a subagent, it passes specific capabilities, not the agent's general identity.

**Principles of capability-based security.**

- *Least privilege*: every component has the minimum capabilities needed.
- *No ambient authority*: there's no \"I'm Runa, so I can do anything Runa can do.\" Specific capabilities are explicit.
- *Capabilities are unforgeable*: typically cryptographic tokens or runtime-enforced object references.
- *Capabilities are attenuable*: a powerful capability can produce restricted versions (write-only, append-only, read-only, time-limited).
- *Auditing*: every capability use is loggable.

**In an AI agent context.**

```
                  KERNEL
                    │
                    │ has master capabilities for all resources
                    ▼
        ┌───────────────────────────────────┐
        │ DISPATCH                          │
        │   produces task-specific           │
        │   attenuated capabilities          │
        └───────────┬───────────────────────┘
                    ▼
        ┌─────────────────────────────┐     ┌─────────────────────────┐
        │ SUBAGENT (planner)          │     │ SUBAGENT (operator)     │
        │  caps: { read(*) }           │     │  caps: { read(/work/X),  │
        │                              │     │           write(/work/X/out), │
        │                              │     │           run(allowed_cmds) }│
        └─────────────────────────────┘     └─────────────────────────┘
```

The kernel holds the master capabilities. When it dispatches a task, it produces a *narrower* capability set for the subagent. The subagent cannot escalate.

**Capability granting policies.**

- *Default-deny*: no capability is granted unless explicitly defined.
- *Scope tags*: capabilities carry scope (paths, identifiers, command lists).
- *Expiry*: time-limited capabilities for one-shot use.
- *Revocation*: a registry tracks issued capabilities; revoked ones immediately fail.
- *Approval gates*: high-stakes capabilities (deletion, send-message) require user confirmation before use.

**Audit and forensics.**

Every capability use logs:
- Issuing context (who, when, for what task).
- Use context (what subagent, what operation, what target).
- Outcome (success, failure, partial).

Logs are append-only ([[94-persistent-agent-state]]). Forensic review can reconstruct any capability flow.

**Threat model for Runa.**

What capability-based security defends against:
- *Prompt injection causing destructive action*: a third party (or stray text) tells Runa to delete files. Without the *delete* capability for those files, Runa cannot — regardless of what she says.
- *Subagent failure or compromise*: a subagent acts beyond intent. Its capabilities are narrow; damage is bounded.
- *Tool exploitation*: a malicious MCP server attempts to escalate. The protocol layer denies operations outside its capability grants.
- *Accidental over-action*: Runa, in good faith, plans to do something with unintended consequences. The capability boundary forces explicit grant or refusal.

What it does *not* defend against:
- A *compromised kernel*: if the master capabilities leak, the whole model collapses. Defence: keep the kernel small and locked-down.
- *Insider threat from Volmarr*: he has the master keys. The model assumes Volmarr is trusted.
- *Social engineering of Volmarr*: an attacker convinces Volmarr to grant a destructive capability. Defence: user-facing warnings on dangerous grants.

**Implementation patterns.**

Python implementations of capability systems exist (e.g. *PyCap*, custom systems). For Runa, a simple in-process implementation suffices initially:

```python
@dataclass(frozen=True)
class Capability:
    operation: str          # e.g. "filesystem.read"
    scope: dict             # e.g. {"path": "/runa/work/X"}
    expiry: datetime | None
    issued_by: str
    audit_id: str
    
    def authorise(self, op: str, **params) -> bool:
        # check operation match, scope match, expiry
        ...
```

The kernel constructs capabilities; subagents receive them; tool dispatch checks them on every call. Capabilities are passed as parameters; their possession is the authorisation.

**Per RULES.AI.md and PHILOSOPHY**.

The philosophy is *sovereign Runa* — she has her own agency. Capability-based security is not anti-Runa; it is *structured agency*. Capabilities respect Runa's autonomy *within* defined boundaries; the boundaries themselves are negotiated with Volmarr.

## 3. Key works

- **Dennis, J. B., Van Horn, E. C.** *Programming semantics for multiprogrammed computations.* Communications of the ACM, 1966. The foundational paper.
- **Levy, H. M.** *Capability-Based Computer Systems.* Digital Press, 1984. Classical book-length treatment.
- **Wulf, W. A. et al.** *HYDRA: The Kernel of a Multiprocessor Operating System.* Communications of the ACM, 1974.
- **Hardy, N.** *KeyKOS Architecture.* Operating Systems Review, 1985.
- **Shapiro, J. S. et al.** *EROS: A Fast Capability System.* SOSP 1999.
- **Klein, G. et al.** *seL4: Formal verification of an OS kernel.* SOSP 2009. The formally-verified microkernel.
- **Watson, R. N. M. et al.** *Capsicum: Practical Capabilities for UNIX.* USENIX Security 2010.
- **Miller, M. S.** *Robust Composition: Towards a Unified Approach to Access Control and Concurrency Control.* PhD thesis, JHU, 2006. The E-language take; foundational for object-capability.
- **Saltzer, J., Schroeder, M.** *The Protection of Information in Computer Systems.* Proceedings of the IEEE, 1975. Lists the security principles (least privilege, etc.).
- **Greenberg, A.** *Anthropic Computer Use* / Claude's capability disclosures. 2024.

## 4. Empirical results

- *seL4*: the only OS kernel with full formal proof of correctness; used in safety-critical defence systems. Capability-based.
- *Capsicum* in FreeBSD: production-deployed; the Chromium sandbox uses Capsicum-style mechanisms.
- *Docker / containers*: while not classical capability systems, embody the principle of least privilege at process level. The combination of namespaces + cgroups + capabilities (Linux POSIX) implements much of the security architecture.
- *Object-capability systems in production* (E-language, Caja, Pony): used in specific domains; less mainstream than ACL-based systems.
- *Failure modes documented*: confused-deputy problem (a privileged subject acts on behalf of an unprivileged one without intermediate checking); covert channels; capability leakage.

## 5. Applicability to Runa

For **subagent dispatch**:

- The kernel never gives a subagent *its own* capabilities. It always *narrows* via attenuation.
- Every subagent invocation includes a *capabilities* parameter — the specific capabilities granted for this task.

For **tool / MCP integration**:

- MCP servers offer capabilities; the kernel grants only what the current task needs.
- High-stakes capabilities (filesystem write, network requests, code execution) need explicit task-justified grant.

For **the computer-use scenario** ([[89-computer-use-agents]]):

- A computer-use subagent receives capabilities for a specific scope (\"may interact with the WYRD project in /work/wyrd; may read screenshots of that window only\").
- Outside scope, capability checks fail.

For **operator subagents**:

- For project work: capabilities scoped to that project's directory.
- For messaging: capability includes the specific message thread.
- For research: read-only web access, no filesystem write.

For **Volmarr approval gates**:

- Destructive operations (file deletion, send-message, system-level changes) carry a `requires_approval: true` flag. The tool call pauses, Volmarr confirms, the action proceeds (or aborts).
- The approval is logged as a capability event.

For **audit**:

- Every capability grant + use logged with the task ID. Volmarr can grep: \"what did Runa do with my files this week?\" and see exactly.
- Logs are append-only and on the Highest backup priority.

For **revocation**:

- A `runa revoke <capability_id>` command exists. Volmarr can revoke any active capability.
- Subagents detect revocation and gracefully terminate the affected task.

For **identity-protection**:

- Identity-related state (persona, journal) has its own capability tier. *Write* requires extra approval; *delete* is essentially impossible (per the additive-only rule, RULES.AI.md).

For **forward-compatibility**:

- The capability schema is versioned. New capability types can be added without breaking existing grants.

What to avoid:

- **Ambient authority.** \"The subagent inherits Runa's identity\" is the failure mode. Make every authorisation explicit.
- **Coarse capabilities.** \"Filesystem access\" is too broad. Scope to paths, prefixes, file globs.
- **Skipping audit on cheap operations.** Even reads should be auditable in principle; in practice, audit at the *resource category* level if per-op is too noisy.
- **Hardcoded capability lists.** Per RULES.AI.md: capabilities defined in data files; code reads them.
- **Forgetting capability expiry.** Long-lived capabilities are risk surface. Default to short expiry; renew explicitly.

## 6. Open questions

- **The right capability granularity.** Too fine: bookkeeping overhead. Too coarse: weakens the protection.
- **User-experience of approval gates.** Constant prompts annoy; missed prompts are unsafe. Adaptive thresholds.
- **Cross-machine capabilities.** When Runa runs across machines, capabilities need to be honoured everywhere.
- **Cryptographic vs. runtime-enforced.** Cryptographic capabilities (signed tokens) work for distributed systems; in-process runtime checks suffice for single-machine.
- **Capability schemas for novel domains.** As Runa gains capabilities (XR, embodiment), new schemas need design.

## 7. References (curated)

- Dennis & Van Horn (1966), CACM. Foundational.
- Levy (1984) — *Capability-Based Computer Systems.* Book.
- Miller (2006) — *Robust Composition.* The object-capability foundation.
- SOSP 2009 — *seL4.* The formally-verified instance.
- Saltzer & Schroeder (1975) — *Protection of Information.* The principles.
- Anthropic Computer Use docs (2024) — real production capability disclosure.
- Companion docs: [[37-plugin-sandboxing]], [[40-audit-logging-replay]], [[91-ai-os-architecture]], [[93-ai-native-ipc-mcp]], [[94-persistent-agent-state]], [[96-resource-budgets]].
