# src/runa/skills/

First-party agent-facing capabilities. "Things Runa can do" that are too small to be subsystems and too internal to be adapters.

A skill is a self-contained unit: a name, a contract, a `run(context, args) -> result`, and a registration so the kernel and the task ledger can find it.

See `INTERFACE.md` for the skill contract.
