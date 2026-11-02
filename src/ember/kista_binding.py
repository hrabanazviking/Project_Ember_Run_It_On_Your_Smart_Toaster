"""The Ember core's binding to the toaster-Kista (E-100).

Roadmap line: "Ember core binding: the companion fetches its
model/API credentials from toaster-Kista under E-097."

The shape, in plain words: the companion is one *program*
calling its own machine's toaster-Kista. It names itself
``ember-core`` (E-097's ``KISTA_PROGRAM``), so the vault hands
it only the entries the owner has given to that program — any
other entry and a missing entry answer identically, and this
module cannot tell them apart either. When the vault is locked
(E-096), the passphrase travels in the environment variable the
config *names* (``KISTA_PASSPHRASE`` by default) — never in a
config value, never on a command line, and never by prompt: a
programmatic fetch does not block on a hidden prompt, it fails
with the vault's own stated reason.

What is fetched: the toaster set's credential kinds only
(E-098) — a ``credential`` entry yields its ``password``, an
``apikey`` entry yields its ``key``. Any other kind is refused
by this module with a typed reason: model/API credentials are
the binding's whole charter, and a note, a URL, or an identity
is not one, however the vault stores it.

Custody (E-093): the fetched value is held in memory only. It
is never logged, never written anywhere, never placed in a
config, and never named — in whole or in part — in any reason
this module returns. Reasons name the *source* that failed and
the *shape* of the failure, in the Well resolver's manner
(``src/ember/well/brunnr/pgvector/secrets.py``).

The binding is fetch-only. The core never adds, changes, or
removes a vault entry: custody stays the owner's act at the
Kista's own command line (E-097). It follows that the binding
never *writes* to the vault — but owners do, from the CLI,
while the companion runs; the write side of that concurrency
is the inter-process lock E-100 builds into the vault program
itself (docket 134, drilled at E-102).

The vault is reached by running the toaster-Kista program
(``kista/scripts/credstore.py``) as a subprocess — the only
programmatic face the program has (E-094). No new dependency:
the subprocess carries the member directory and the user
site-packages on its path exactly as the campaign's probes do,
so the member's one dependency (``cryptography``) resolves the
same way it does for the owner's own runs. If that dependency
is absent, the program's own plain refusal is the reason.
"""

from __future__ import annotations

import json
import os
import site
import subprocess
import sys
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from ember.schemas.config import KistaConfig

#: The program name the core claims at the vault (E-097 §3:
#: the binding shape this slice was handed).
CORE_PROGRAM: Final[str] = "ember-core"

#: The credential kinds this binding may fetch, and the entry
#: field that carries the secret for each (E-098's toaster set:
#: ``credential`` and ``apikey`` are the kinds a model/API
#: credential can be; ``url`` and ``note`` carry no secret).
SECRET_FIELDS: Final[dict[str, str]] = {
    "credential": "password",
    "apikey": "key",
}

#: A fetch is a local subprocess call; a vault that has not
#: answered in this long is stuck, not slow — scrypt unlock
#: included, this is two orders of magnitude past its cost.
FETCH_TIMEOUT_S: Final[float] = 30.0

#: Shape of the injectable runner: (argv, env) -> a completed
#: process with ``returncode`` / ``stdout`` / ``stderr`` text.
Runner = Callable[[list[str], Mapping[str, str]], "subprocess.CompletedProcess[str]"]


@dataclass(frozen=True, slots=True)
class KistaResolution:
    """The outcome of a fetch attempt.

    Either ``secret`` is set (success) or ``reason`` is set
    (failure) — never both. ``reason`` is operator-facing: it
    explains which source was tried and why it did not yield,
    and it never contains any part of a secret value.
    """

    secret: str | None
    reason: str | None

    @classmethod
    def found(cls, secret: str) -> KistaResolution:
        return cls(secret=secret, reason=None)

    @classmethod
    def missing(cls, reason: str) -> KistaResolution:
        return cls(secret=None, reason=reason)


def default_credstore_path() -> Path:
    """The in-tree toaster-Kista program of this monorepo.

    ``src/ember/kista_binding.py`` → repo root is two parents
    up from ``src/``. An installed copy without the member
    beside it gets a path that does not exist, and the fetch
    says so plainly, naming the config knob that points at a
    real program.
    """
    return Path(__file__).resolve().parents[2] / "kista" / "scripts" / "credstore.py"


def fetch_credential(
    entry_name: str,
    *,
    config: KistaConfig,
    env: Mapping[str, str] | None = None,
    runner: Runner | None = None,
) -> KistaResolution:
    """Fetch one model/API credential from the toaster-Kista.

    ``entry_name`` is the vault entry the owner gave to the
    core's program. ``env`` defaults to ``os.environ``; tests
    pass a mapping so the real environment is never touched.
    ``runner`` defaults to a real subprocess call; tests inject
    a fake. This function never raises for a vault-side failure:
    every refusal is a :class:`KistaResolution` with a reason.
    """
    env_map: Mapping[str, str] = os.environ if env is None else env
    name = entry_name.strip().lower()
    if not name:
        return KistaResolution.missing("kista fetch: no entry name was given")

    credstore = (
        Path(config.credstore_path).expanduser()
        if config.credstore_path is not None
        else default_credstore_path()
    )
    if not credstore.is_file():
        return KistaResolution.missing(
            f"kista program not found at {credstore} — point "
            "kista.credstore_path at the toaster-Kista program "
            "(kista/scripts/credstore.py in this monorepo)"
        )

    program = config.program or CORE_PROGRAM
    child_env = dict(env_map)
    child_env["KISTA_DIR"] = str(Path(config.vault_dir).expanduser())
    child_env["KISTA_PROGRAM"] = program
    # The passphrase travels by its named variable only. When
    # the caller's environment carries it, it is passed through
    # untouched; when it does not, the child gets none and the
    # vault's own refusal (never a prompt — stdin is closed)
    # is the answer.
    passphrase_env = config.passphrase_env or "KISTA_PASSPHRASE"
    if passphrase_env != "KISTA_PASSPHRASE":
        value = child_env.pop(passphrase_env, "")
        if value:
            child_env["KISTA_PASSPHRASE"] = value
        else:
            child_env.pop("KISTA_PASSPHRASE", None)
    parts = [
        str(credstore.parent.parent),
        site.getusersitepackages(),
        child_env.get("PYTHONPATH", ""),
    ]
    child_env["PYTHONPATH"] = os.pathsep.join(p for p in parts if p)

    run = _default_runner if runner is None else runner
    try:
        proc = run([sys.executable, str(credstore), "get", name], child_env)
    except subprocess.TimeoutExpired:
        return KistaResolution.missing(
            f"kista fetch for entry {name!r} timed out after "
            f"{FETCH_TIMEOUT_S:.0f}s — the vault did not answer"
        )
    except OSError as exc:
        return KistaResolution.missing(
            f"kista fetch for entry {name!r} could not start the "
            f"vault program: {type(exc).__name__}"
        )

    if proc.returncode != 0:
        detail = _first_line(proc.stderr) or _first_line(proc.stdout)
        suffix = f": {detail}" if detail else ""
        return KistaResolution.missing(
            f"kista fetch for entry {name!r} was refused by the "
            f"vault (exit {proc.returncode}){suffix}"
        )

    try:
        entry = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return KistaResolution.missing(
            f"kista fetch for entry {name!r} returned output that "
            "is not the vault's entry shape"
        )
    if not isinstance(entry, dict):
        return KistaResolution.missing(
            f"kista fetch for entry {name!r} returned output that "
            "is not the vault's entry shape"
        )

    kind = str(entry.get("entry_type", "credential"))
    field = SECRET_FIELDS.get(kind)
    if field is None:
        return KistaResolution.missing(
            f"kista entry {name!r} is a {kind!r} entry, not a "
            "model/API credential — the core binding fetches only "
            "credential and apikey entries (E-098)"
        )
    value = entry.get(field)
    if not isinstance(value, str) or not value:
        return KistaResolution.missing(
            f"kista entry {name!r} holds no {field} — the entry "
            "exists for this program but its credential is empty"
        )
    return KistaResolution.found(value)


def _default_runner(
    argv: list[str], env: Mapping[str, str]
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        capture_output=True,
        text=True,
        env=dict(env),
        stdin=subprocess.DEVNULL,
        timeout=FETCH_TIMEOUT_S,
        check=False,
    )


def _first_line(text: str) -> str:
    """The first non-empty line of a program's output, bounded.

    The vault's refusal lines never carry a secret (a refusal
    happens before any value is read out), and the bound keeps
    a reason from becoming a transcript.
    """
    for line in (text or "").splitlines():
        stripped = line.strip()
        if stripped:
            return stripped[:200]
    return ""


__all__ = [
    "CORE_PROGRAM",
    "FETCH_TIMEOUT_S",
    "SECRET_FIELDS",
    "KistaResolution",
    "default_credstore_path",
    "fetch_credential",
]
