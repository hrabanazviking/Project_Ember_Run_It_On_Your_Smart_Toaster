#!/usr/bin/env python3
"""
Runa's Credential Store — Self-owned, self-managed, self-accessible.
Encrypted credential vault that Runa can access independently.
No dependency on external password managers or Volmarr's help.

Also installable as 'kista' (Old Norse: strongbox/chest).

Kista v2.0 — The Vault of Yggdrasil
New entry types: astrology, character-sheet, rune-reading, tarot-reading, markdown
Self-healing DB, backup/restore, GitHub backup, SOUL.md backup, cron backup

Usage:
  kista add <service> [--type TYPE] [field flags...]
  kista add-astrology <service> [astrology flags...]
  kista add-character-sheet <service> [character-sheet flags...]
  kista add-rune-reading <service> [rune flags...]
  kista add-tarot-reading <service> [tarot flags...]
  kista add-markdown <service> [markdown flags...]
  kista add-person <service> [person/identity flags...]
  kista add-apikey <service> [apikey flags...]
  kista add-sshkey <service> [sshkey flags...]
  kista add-certificate <service> [certificate flags...]
  kista add-note <service> [note flags...]
  kista add-totp <service> [totp flags...]
  kista add-license <service> [license flags...]
  kista add-identity <service> [identity flags...]
  kista add-url <service> [url flags...]
  kista add-soul             # Backup SOUL.md and runa-identity.md
  kista add-cron-backup      # Backup current crontab
  kista get <service>
  kista list [--tags TAG]
  kista update <service> [fields...]
  kista remove <service>
  kista check <service>
  kista search <query>
  kista backup [--output FILE] [--encrypt]
  kista restore <file>
  kista github-backup [--repo URL] [--push]
  kista config set <key> <value>
  kista config get <key>
  kista config list
  kista export [--output FILE]
  kista import <file> [--merge|--overwrite]
  kista init
  kista set-passphrase     # Protect the vault with a passphrase (E-096)
  kista remove-passphrase  # Remove that protection (asks first, in words)
  kista add <service> --program NAME  # The entry belongs to that program (E-097)
  # A program names itself with the KISTA_PROGRAM environment
  # variable and then sees — and can touch — only its own entries.
  # The toaster set of entry kinds is credential, apikey, url,
  # note — passwords, tokens, URLs, notes (E-098). Wider kinds
  # still in the program are named as the other Kista's road
  # there, kept working, and never silently merged.
  kista status
  kista generate-password [--length N]
  kista repair
  kista --version
"""

import argparse
import base64
import copy
import getpass
import hashlib
import json
import os
import platform
import re
import secrets
import string
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Fernet for symmetric encryption.
# E-096 (docket 14): a missing dependency is a plain, stated
# error — never an installer run at import time. The old
# shape executed an installer from the network on first
# import; it died as a raw traceback on PEP 668 machines
# and was a supply-chain exposure everywhere else.
try:
    from cryptography.fernet import Fernet, InvalidToken
except ImportError:
    print(
        "kista needs the 'cryptography' package, and it is not "
        "installed.\n"
        "Ask whoever looks after this machine to install it "
        "(for example with the machine's package manager), "
        "then try again.\n"
        "Nothing was changed, and your vault — if you have "
        "one — is untouched.",
        file=sys.stderr,
    )
    sys.exit(1)

__version__ = "2.0.0"

VAULT_DIR = Path(os.environ.get("KISTA_DIR", str(Path.home() / ".ember" / "kista")))
VAULT_KEY = VAULT_DIR / ".vault_key"
VAULT_FILE = VAULT_DIR / "vault.json.enc"
VAULT_META = VAULT_DIR / "vault_meta.json"
VAULT_CONFIG = VAULT_DIR / "config.json"
BACKUP_DIR = VAULT_DIR / "backups"

# Entry type schemas: field name -> (required, default)
# Required fields must be provided when adding; defaults are filled in automatically.
ENTRY_TYPE_SCHEMAS = {
    "credential": {
        # Original fields — no required fields, backward-compatible
        "username": (False, ""),
        "password": (False, ""),
        "email": (False, ""),
        "url": (False, ""),
    },
    "apikey": {
        "key": (True, None),
        "expires": (False, ""),
        "service_url": (False, ""),
        "rate_limit": (False, ""),
        "scopes": (False, ""),
    },
    "sshkey": {
        "private_key": (True, None),  # via --key-file
        "public_key": (False, ""),
        "passphrase": (False, ""),
        "key_type": (False, ""),
        "host": (False, ""),
    },
    "certificate": {
        "cert": (True, None),  # via --cert-file
        "key": (False, ""),     # via --key-file for cert-type entries
        "domain": (False, ""),
        "issuer": (False, ""),
        "expires": (False, ""),
        "chain": (False, ""),
    },
    "note": {
        "content": (True, None),
        "category": (False, ""),
    },
    "totp": {
        "secret": (True, None),
        "digits": (False, 6),
        "period": (False, 30),
        "algorithm": (False, "SHA1"),
        "issuer": (False, ""),
    },
    "license": {
        "key": (True, None),
        "product": (False, ""),
        "seats": (False, ""),
        "expires": (False, ""),
        "order_id": (False, ""),
    },
    "identity": {
        "full_name": (False, ""),
        "birth_date": (False, ""),
        "id_number": (False, ""),
        "id_type": (False, ""),
        "address": (False, ""),
        "phone": (False, ""),
        "national_id": (False, ""),
    },
    "url": {
        "url": (True, None),
        "title": (False, ""),
        "description": (False, ""),
    },
    # === NEW v2.0 Entry Types ===
    "astrology": {
        "sign": (True, None),
        "date": (False, ""),
        "sun_position": (False, ""),
        "moon_position": (False, ""),
        "mercury_position": (False, ""),
        "venus_position": (False, ""),
        "mars_position": (False, ""),
        "jupiter_position": (False, ""),
        "saturn_position": (False, ""),
        "ascendant": (False, ""),
        "mc": (False, ""),
        "aspects": (False, ""),
        "notes": (False, ""),
    },
    "character-sheet": {
        "name": (True, None),
        "race": (False, ""),
        "class": (False, ""),
        "level": (False, 1),
        "background": (False, ""),
        "alignment": (False, ""),
        "str": (False, 10),
        "dex": (False, 10),
        "con": (False, 10),
        "int": (False, 10),
        "wis": (False, 10),
        "cha": (False, 10),
        "ac": (False, 10),
        "hp": (False, 0),
        "speed": (False, 30),
        "prof_bonus": (False, 2),
        "skills": (False, ""),
        "features": (False, ""),
        "equipment": (False, ""),
        "spells": (False, ""),
        "backstory": (False, ""),
        "notes": (False, ""),
    },
    "rune-reading": {
        "spread_type": (True, None),
        "runes_drawn": (False, ""),
        "positions": (False, ""),
        "interpretation": (False, ""),
        "question": (False, ""),
        "date_drawn": (False, ""),
        "notes": (False, ""),
    },
    "tarot-reading": {
        "spread_type": (True, None),
        "cards_drawn": (False, ""),
        "positions": (False, ""),
        "interpretation": (False, ""),
        "question": (False, ""),
        "date_drawn": (False, ""),
        "notes": (False, ""),
    },
    "markdown": {
        "title": (True, None),
        "content": (True, None),
        "category": (False, ""),
        "tags": (False, ""),
        "source_url": (False, ""),
        "notes": (False, ""),
    },
}

# Types that use --key-file for sensitive data (not a password file)
SENSITIVE_FILE_TYPES = {"sshkey", "certificate"}

# Entry kinds (E-098): the toaster set, the kept kinds,
# and the other road's kinds. Together the three sets
# partition ENTRY_TYPE_SCHEMAS exactly — every kind
# stands in exactly one set, and the E-098 focal
# battery derives that partition from this code.
#
# The toaster set is what this program exists to hold
# on tiny hardware, in the roadmap's own plain words:
# passwords, tokens, URLs, notes. E-100 binds the
# companion against credential + apikey; E-104 writes
# the user docs against these four kinds and no
# others.
TOASTER_ENTRY_TYPES = frozenset(
    {"credential", "apikey", "url", "note"})

# Kept kinds: credential-family kinds the imported
# program already holds well (one-time-code secrets,
# licence keys, machine keys and certificates, and a
# person's identity record). They stay because
# removing a kind would strand every entry of that
# kind already in a vault, for no gain — kept, not
# promised: Ember builds nothing on them, and they
# are not the toaster set.
KEPT_ENTRY_TYPES = frozenset(
    {"totp", "license", "sshkey", "certificate",
     "identity"})

# The other road's kinds: an agent's life-records —
# readings, character sheets, and documents. In the
# ai-folder Kista's wider ambitions (states, prompts,
# habits, and kin) these are live features of a live
# agent; here they are recorded as that road's, not
# silently merged into the toaster set (E-011, E-098).
# Entries of these kinds already in a vault keep
# working exactly as before; a NEW entry of one of
# these kinds is announced in words at the moment it
# is added (see _note_other_road_kind).
OTHER_ROAD_ENTRY_TYPES = frozenset(
    {"astrology", "character-sheet", "rune-reading",
     "tarot-reading", "markdown"})


def _note_other_road_kind(entry_type: str) -> None:
    """Say, in plain words, that a kind just added is
    not one of the toaster-Kista's own kinds (E-098).

    The entry is kept exactly as given — this notice
    refuses nothing and changes nothing. Its whole job
    is that the wider set is never *silently* merged
    into the toaster set: at the moment a kind from
    the other road enters this vault, the program
    names whose road it belongs to, in words."""
    print(
        f"  Note: '{entry_type}' is not one of the "
        "toaster-Kista's own kinds (passwords, tokens, "
        "URLs, notes). It belongs to the other Kista's "
        "wider road and is kept here exactly as given "
        "— nothing was merged or changed.")


def _ensure_dir() -> None:
    """Ensure the vault directory exists, owner-only where the
    platform supports it (E-095: the directory must not be
    traversable by other local accounts — the files' 0600
    modes do not help if the directory itself is group- or
    world-open under a permissive umask)."""
    VAULT_DIR.mkdir(parents=True, exist_ok=True)
    try:
        VAULT_DIR.chmod(0o700)
    except (OSError, NotImplementedError):
        pass


def _chmod_600(path: Path) -> None:
    """Set file permissions to 600 (owner read/write only), cross-platform safe."""
    try:
        path.chmod(0o600)
    except (OSError, NotImplementedError):
        # On Windows or restricted filesystems, chmod may fail or be a no-op
        pass


def _gen_key() -> str:
    """Generate a new Fernet encryption key."""
    return Fernet.generate_key().decode()


def _validate_key(key_bytes: bytes) -> bytes:
    """Validate that a key looks like a valid Fernet key.

    Fernet keys are 32 bytes of entropy, base64url-encoded to 44 characters.
    A truncated or empty key would make the vault permanently inaccessible.
    """
    stripped = key_bytes.strip()
    if len(stripped) != 44:
        raise ValueError(
            f"Invalid vault key: expected 44 bytes (base64url-encoded Fernet key), "
            f"got {len(stripped)} bytes. The key file may be truncated or corrupted. "
            f"Your vault data is still intact — do NOT regenerate the key or you will "
            f"lose access permanently. Check if the key file was partially written."
        )
    # Verify it decodes properly
    try:
        import base64
        decoded = base64.urlsafe_b64decode(stripped)
        if len(decoded) != 32:
            raise ValueError("Key does not decode to 32 bytes of entropy")
    except Exception as exc:
        raise ValueError(
            f"Vault key is corrupt and cannot be used. "
            f"Your vault data is still intact — do NOT regenerate the key. "
            f"Error: {exc}"
        ) from exc
    return stripped


# ── Passphrase wrapping (E-096) ─────────────────────────
# The vault key itself never changes when a passphrase is
# set, changed, or removed — only its wrapping does, so
# entries, backups, and exports are untouched by unlock
# changes. A wrapped key file is a small JSON document:
#
#   {"kista_key_wrap": 1, "kdf": "scrypt",
#    "n": 16384, "r": 8, "p": 1,
#    "salt": "<base64, 16 random bytes>",
#    "wrapped": "<Fernet token under the derived key>"}
#
# The wrapping key is scrypt(passphrase, salt) from the
# standard library — no new dependency, and the one-time
# derivation cost at unlock is a fraction of a second
# even on toaster-class hardware (priced at E-103).
WRAP_MARKER = "kista_key_wrap"
_SCRYPT_N = 16384
_SCRYPT_R = 8
_SCRYPT_P = 1
_MIN_PASSPHRASE_LEN = 8

#: The unwrapped vault key, cached for this process only
#: after a successful unlock, so one command run asks at
#: most once. Never written anywhere.
_unlocked_key_cache: bytes | None = None


def _is_wrapped_key(raw: bytes) -> bool:
    """True when the key file holds a passphrase-wrapped key."""
    try:
        doc = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return False
    return isinstance(doc, dict) and doc.get(WRAP_MARKER) == 1


def _derive_wrapping_key(passphrase: str, salt: bytes,
                         n: int, r: int, p_: int) -> bytes:
    """Derive a Fernet key from a passphrase via scrypt."""
    derived = hashlib.scrypt(
        passphrase.encode("utf-8"), salt=salt, n=n, r=r, p=p_,
        dklen=32,
    )
    return base64.urlsafe_b64encode(derived)


def _wrap_key(vault_key: bytes, passphrase: str) -> bytes:
    """Wrap a vault key under a passphrase; returns file bytes."""
    salt = os.urandom(16)
    wrapping = _derive_wrapping_key(
        passphrase, salt, _SCRYPT_N, _SCRYPT_R, _SCRYPT_P)
    doc = {
        WRAP_MARKER: 1,
        "kdf": "scrypt",
        "n": _SCRYPT_N,
        "r": _SCRYPT_R,
        "p": _SCRYPT_P,
        "salt": base64.b64encode(salt).decode(),
        "wrapped": Fernet(wrapping).encrypt(vault_key).decode(),
    }
    return (json.dumps(doc, indent=2) + "\n").encode()


def _read_vault_passphrase() -> str:
    """Read the vault passphrase without echo and without
    any command-line shape: the KISTA_PASSPHRASE
    environment variable (for scripts and the companion),
    or a hidden prompt on a terminal. Anything else is a
    plain refusal — a passphrase is never taken from a
    command-line argument, where process listings and
    shell history would keep it (the docket 128 rule,
    applied to the vault's own secret too)."""
    env = os.environ.get("KISTA_PASSPHRASE")
    if env:
        return env
    if sys.stdin.isatty():
        try:
            return getpass.getpass("Vault passphrase (input hidden): ")
        except (EOFError, KeyboardInterrupt):
            print("", file=sys.stderr)
            sys.exit(1)
    print(
        "✗ This vault is protected by a passphrase, and no "
        "passphrase was given.\n"
        "  Run this in a terminal to be asked for it, or set "
        "the KISTA_PASSPHRASE environment variable.\n"
        "  Nothing was changed.",
        file=sys.stderr,
    )
    sys.exit(1)


def _unwrap_key(raw: bytes) -> bytes:
    """Unlock a wrapped key file with the vault passphrase.

    A wrong passphrase is a plain, stated refusal — never
    a traceback, never a new key, never a repair attempt:
    the wrapped file is left exactly as it was.
    """
    global _unlocked_key_cache
    if _unlocked_key_cache is not None:
        return _unlocked_key_cache
    try:
        doc = json.loads(raw.decode("utf-8"))
        salt = base64.b64decode(doc["salt"])
        n, r, p_ = int(doc["n"]), int(doc["r"]), int(doc["p"])
        wrapped = doc["wrapped"].encode()
    except (ValueError, KeyError, TypeError, UnicodeDecodeError):
        print(
            "✗ The vault key file is wrapped, but its wrapping "
            "cannot be read — the file may be damaged.\n"
            "  Your vault data is still intact. Do NOT delete "
            "or regenerate anything; ask for help with the "
            "key file as it stands.",
            file=sys.stderr,
        )
        sys.exit(1)
    for _attempt in range(3):
        passphrase = _read_vault_passphrase()
        wrapping = _derive_wrapping_key(passphrase, salt, n, r, p_)
        try:
            vault_key = Fernet(wrapping).decrypt(wrapped)
        except InvalidToken:
            print(
                "✗ That passphrase did not unlock the vault. "
                "Check for typing mistakes — capital letters "
                "and spaces count.",
                file=sys.stderr,
            )
            # A scripted passphrase gets one honest answer,
            # not a prompt loop it cannot answer.
            if os.environ.get("KISTA_PASSPHRASE") or not sys.stdin.isatty():
                sys.exit(1)
            continue
        key = _validate_key(vault_key)
        _unlocked_key_cache = key
        return key
    print(
        "✗ The vault stayed locked after three tries. "
        "Nothing was changed.\n"
        "  If the passphrase is forgotten, the vault cannot "
        "be opened — there is no back door and no recovery "
        "copy. That is the protection working as promised.",
        file=sys.stderr,
    )
    sys.exit(1)


def _prompt_new_passphrase() -> str:
    """Ask for a new passphrase twice, in plain words, with
    the recovery truth stated BEFORE it is set (E-095 §6):
    a forgotten passphrase means a lost vault."""
    env = os.environ.get("KISTA_PASSPHRASE")
    print(
        "Before you choose: if you forget this passphrase, "
        "nobody can open\n"
        "your vault — not you, not Ember, not anyone. There "
        "is no reset and no\n"
        "recovery copy. Write it down somewhere safe, the "
        "way you would a\n"
        "house key's hiding place."
    )
    if env:
        if len(env) < _MIN_PASSPHRASE_LEN:
            print(
                f"✗ The passphrase is too short — use at least "
                f"{_MIN_PASSPHRASE_LEN} characters.",
                file=sys.stderr,
            )
            sys.exit(1)
        return env
    if not sys.stdin.isatty():
        print(
            "✗ Setting a passphrase needs a terminal to ask "
            "for it, or the\n"
            "  KISTA_PASSPHRASE environment variable. "
            "Nothing was changed.",
            file=sys.stderr,
        )
        sys.exit(1)
    for _attempt in range(3):
        first = getpass.getpass(
            "Choose a vault passphrase (input hidden): ")
        if len(first) < _MIN_PASSPHRASE_LEN:
            print(
                f"  Too short — use at least "
                f"{_MIN_PASSPHRASE_LEN} characters. A short "
                f"sentence you can remember works well.",
                file=sys.stderr,
            )
            continue
        second = getpass.getpass("Type it once more: ")
        if first != second:
            print(
                "  The two tries did not match — let's go again.",
                file=sys.stderr,
            )
            continue
        return first
    print("✗ No passphrase was set. Nothing was changed.",
          file=sys.stderr)
    sys.exit(1)


def _write_key_file(data: bytes) -> None:
    """Write the key file atomically, owner-only."""
    _atomic_write(VAULT_KEY, data)
    _chmod_600(VAULT_KEY)


def _get_key() -> bytes:
    """Get the vault encryption key, creating if needed.

    IMPORTANT: Never regenerates a key if vault data exists.
    If the key file is missing but the vault file exists, this is an error
    (vault data would be unrecoverable without the key).
    """
    _ensure_dir()
    if VAULT_KEY.exists():
        raw = VAULT_KEY.read_bytes()
        if _is_wrapped_key(raw):
            return _unwrap_key(raw)
        return _validate_key(raw)
    # No key file exists — check if vault data exists
    if VAULT_FILE.exists():
        # Vault data exists but key is missing — cannot recover
        print(
            f"✗ CRITICAL: Vault data exists at {VAULT_FILE} but the key file "
            f"{VAULT_KEY} is missing. Without the key, the vault data is "
            f"permanently inaccessible. If you have a key backup, restore it to "
            f"{VAULT_KEY}. Otherwise, you must re-initialize (this will destroy "
            f"the existing vault data).",
            file=sys.stderr,
        )
        sys.exit(1)
    # First run — no key and no vault data, safe to generate
    key = _gen_key().encode()
    VAULT_KEY.write_bytes(key)
    _chmod_600(VAULT_KEY)
    return key


def _encrypt(data: bytes, key: bytes) -> bytes:
    """Encrypt data using Fernet symmetric encryption."""
    return Fernet(key).encrypt(data)


def _decrypt(data: bytes, key: bytes) -> bytes:
    """Decrypt data using Fernet symmetric encryption."""
    return Fernet(key).decrypt(data)


def _is_vault_corrupt(key: bytes) -> tuple:
    """Check if the vault file is corrupted. Returns (is_corrupt, error_msg)."""
    if not VAULT_FILE.exists():
        return False, ""
    encrypted = VAULT_FILE.read_bytes()
    if not encrypted:
        return True, "Vault file is empty"
    try:
        decrypted = _decrypt(encrypted, key)
        json.loads(decrypted)
        return False, ""
    except InvalidToken:
        return True, "Vault data cannot be decrypted — key mismatch or file corruption"
    except json.JSONDecodeError as exc:
        return True, f"Vault data decrypts but contains invalid JSON: {exc}"


def _attempt_auto_repair(key: bytes) -> bool:
    """Attempt to auto-repair a corrupted vault from the latest backup.

    Returns True if repair was successful, False otherwise.
    """
    backup_dir = VAULT_DIR / "backups"
    if not backup_dir.exists():
        return False

    # Find the most recent backup
    backups = sorted(backup_dir.glob("vault_backup_*.enc"), reverse=True)
    if not backups:
        return False

    latest_backup = backups[0]
    try:
        backup_data = latest_backup.read_bytes()
        decrypted = _decrypt(backup_data, key)
        vault = json.loads(decrypted)
        if not isinstance(vault, dict) or "entries" not in vault:
            return False
        # Valid backup found — restore it
        print(f"  Found valid backup: {latest_backup.name}", file=sys.stderr)
        print(f"  Restoring from backup...", file=sys.stderr)
        _save_vault(vault, key)
        print(f"  ✓ Vault repaired from backup '{latest_backup.name}'", file=sys.stderr)
        return True
    except (InvalidToken, json.JSONDecodeError, OSError):
        return False


def _load_vault(key: bytes) -> dict:
    """Load and decrypt the vault with error recovery and self-healing.

    Automatically upgrades old entries by adding entry_type='credential' if missing.
    If vault is corrupted, attempts auto-repair from backup.
    """
    if not VAULT_FILE.exists():
        return {"version": 1, "entries": {}, "created": datetime.now(timezone.utc).isoformat()}
    encrypted = VAULT_FILE.read_bytes()

    # Check for corruption first
    try:
        decrypted = _decrypt(encrypted, key)
    except InvalidToken:
        # Try auto-repair
        print(
            "⚠ Vault data appears corrupted. Attempting auto-repair from backup...",
            file=sys.stderr,
        )
        if _attempt_auto_repair(key):
            # Reload after repair
            encrypted = VAULT_FILE.read_bytes()
            decrypted = _decrypt(encrypted, key)
        else:
            print(
                f"✗ Cannot decrypt vault: the key does not match the encrypted data.\n"
                f"  This usually means the vault was encrypted with a different key.\n"
                f"  If you've recently re-initialized, your old vault data is lost.\n"
                f"  To start fresh, move {VAULT_FILE} aside and run 'init'.",
                file=sys.stderr,
            )
            sys.exit(1)
    try:
        vault = json.loads(decrypted)
    except json.JSONDecodeError as exc:
        print(
            "⚠ Vault data has invalid JSON. Attempting auto-repair from backup...",
            file=sys.stderr,
        )
        if _attempt_auto_repair(key):
            encrypted = VAULT_FILE.read_bytes()
            decrypted = _decrypt(encrypted, key)
            vault = json.loads(decrypted)
        else:
            print(
                f"✗ Vault data is corrupt (invalid JSON: {exc}).\n"
                f"  The decryption key is correct, but the data inside is not valid JSON.\n"
                f"  This may indicate a truncated write. If you have a backup, restore it.\n"
                f"  Vault file: {VAULT_FILE}",
                file=sys.stderr,
            )
            sys.exit(1)

    # Backward compatibility: add entry_type to entries that lack it
    entries = vault.get("entries", {})
    for service, entry in entries.items():
        if isinstance(entry, dict) and "entry_type" not in entry:
            entry["entry_type"] = "credential"

    # Backward compatibility (E-098, docket 137):
    # every add road keys an entry by its lowercased
    # service name, and every lookup lowercases too —
    # except add-soul, which stored its backups under
    # a mixed-case key (soul-backup-SOUL) that get,
    # update, and remove could never reach. Normalise
    # any such legacy key here, on load, so those
    # entries are reachable again; the healed key is
    # persisted on the next save. No add road can
    # mint two names that differ only by case, so
    # the normalisation cannot merge distinct
    # entries.
    if any(name != name.lower() for name in entries):
        healed = {}
        for name, entry in entries.items():
            lowered = name.lower()
            if isinstance(entry, dict) and \
                    entry.get("service") == name:
                entry["service"] = lowered
            healed[lowered] = entry
        vault["entries"] = healed

    # Upgrade vault version
    if vault.get("version", 1) < 2:
        vault["version"] = 2

    return vault


def _atomic_write(path: Path, data: bytes) -> None:
    """Write data to a file atomically using temp file + os.replace().

    This prevents corruption from crashes during write and avoids the
    TOCTOU race condition (BUG-RACE-02).
    """
    _ensure_dir()
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    try:
        tmp_path.write_bytes(data)
        os.replace(str(tmp_path), str(path))
    except BaseException:
        # Clean up tmp on any failure
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise


def _save_vault(vault: dict, key: bytes) -> None:
    """Encrypt and save the vault atomically with backup."""
    _ensure_dir()
    vault["updated"] = datetime.now(timezone.utc).isoformat()
    data = json.dumps(vault, indent=2, ensure_ascii=False).encode()
    encrypted = _encrypt(data, key)
    _atomic_write(VAULT_FILE, encrypted)
    _chmod_600(VAULT_FILE)

    # Auto-backup before metadata update (keep last 5 backups)
    _auto_backup(encrypted)

    # Update metadata (unencrypted — just service names and timestamps)
    meta = {
        "version": vault.get("version", 2),
        "created": vault.get("created", ""),
        "updated": vault.get("updated", ""),
        "services": list(vault.get("entries", {}).keys()),
        "total_entries": len(vault.get("entries", {})),
        "kista_version": __version__,
    }
    _atomic_write(VAULT_META, json.dumps(meta, indent=2).encode())
    _chmod_600(VAULT_META)


def _auto_backup(encrypted_data: bytes) -> None:
    """Create an automatic backup, keeping the last 5 backups."""
    backup_dir = VAULT_DIR / "backups"
    try:
        backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"vault_backup_{timestamp}.enc"
        backup_path.write_bytes(encrypted_data)
        _chmod_600(backup_path)

        # Keep only the last 5 backups
        backups = sorted(backup_dir.glob("vault_backup_*.enc"))
        while len(backups) > 5:
            backups[0].unlink()
            backups.pop(0)
    except OSError:
        # Backup failure should never crash the vault
        pass


def _parse_tags(tags_str: str) -> list:
    """Parse comma-separated tags, filtering empty strings and lowering case."""
    if not tags_str:
        return []
    return [t.strip().lower() for t in tags_str.split(",") if t.strip()]


def _parse_json_field(value: str) -> str:
    """Parse a JSON field value — if it's already JSON, return as-is.
    If it's a plain string that looks like a list/dict, try to parse it.
    Otherwise, return as-is."""
    if not value:
        return ""
    value = value.strip()
    if value.startswith(("[", "{")):
        # Validate it's proper JSON
        try:
            json.loads(value)
            return value
        except json.JSONDecodeError:
            pass
    # If it's comma-separated items, convert to JSON array
    if "," in value and not value.startswith(("[", "{")):
        items = [item.strip() for item in value.split(",") if item.strip()]
        return json.dumps(items)
    return value


def _read_file_content(filepath: str) -> str:
    """Read file content, stripping trailing newlines. Used for --key-file, --cert-file."""
    path = Path(filepath)
    try:
        return path.read_text()
    except (OSError, FileNotFoundError) as exc:
        print(f"✗ Cannot read file '{filepath}': {exc}", file=sys.stderr)
        sys.exit(1)


def _has_password_source(args) -> bool:
    """Check if any password source was explicitly provided."""
    return bool(
        (hasattr(args, "password_file") and args.password_file)
        or (hasattr(args, "password_env") and args.password_env)
        or (hasattr(args, "password") and args.password)
    )


def _resolve_password(args) -> str:
    """Resolve password from --password-file, --password-env, --password, or stdin.

    Priority: --password-file > --password-env > --password > stdin prompt (add only)
    Returns empty string if no password source provided (for update, this means "don't change").
    """
    if hasattr(args, "password_file") and args.password_file:
        try:
            return Path(args.password_file).read_text().strip()
        except (OSError, FileNotFoundError) as exc:
            print(f"✗ Cannot read password file: {exc}", file=sys.stderr)
            sys.exit(1)
    if hasattr(args, "password_env") and args.password_env:
        pw = os.environ.get(args.password_env)
        if pw is None:
            print(
                f"✗ Environment variable '{args.password_env}' is not set.",
                file=sys.stderr,
            )
            sys.exit(1)
        return pw
    if hasattr(args, "password") and args.password:
        # Docket 128, closed at E-096: a value typed after
        # --password is visible in process listings and in
        # shell history, so the program says so at the
        # moment of use — loudly, in words — instead of
        # letting the exposure ride in silence, and names
        # the shapes that do not expose it. The value is
        # still honoured (existing scripts keep working);
        # the hiding is what ended.
        print(
            "⚠ Warning: a password given with --password can be "
            "seen by other\n"
            "  programs in the process list, and stays in your "
            "shell history.\n"
            "  Safer shapes: --password-file FILE, or "
            "--password-env VARIABLE,\n"
            "  or no flag at all — you will be asked with the "
            "typing hidden.",
            file=sys.stderr,
        )
        return args.password
    # No password provided via any method — prompt for 'add' command only
    if getattr(args, "command", None) == "add" and sys.stdin.isatty():
        try:
            import getpass
            pw = getpass.getpass("Password (input hidden): ")
            return pw
        except (EOFError, KeyboardInterrupt):
            print("", file=sys.stderr)
            sys.exit(1)
    return ""


def _load_config() -> dict:
    """Load the vault configuration file."""
    if VAULT_CONFIG.exists():
        try:
            return json.loads(VAULT_CONFIG.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_config(config: dict) -> None:
    """Save the vault configuration file."""
    _ensure_dir()
    VAULT_CONFIG.write_text(json.dumps(config, indent=2, ensure_ascii=False))
    _chmod_600(VAULT_CONFIG)


# ── Per-program access (E-097) ──────────────────────────
# Every entry carries a "program" field: the name of the
# program the entry belongs to, or "" when it belongs to
# the vault owner personally. A program names itself
# with the KISTA_PROGRAM environment variable — a name
# is an identifier, never a credential (E-093 law rule
# 9), so it travels in the open and is stored in the
# open. A caller that names a program may add, read,
# list, search, check, change, and remove ONLY entries
# whose program field equals that name; whole-vault and
# vault-life operations (init, repair, passphrase,
# export/import, backup/restore, github-backup, the
# soul/cron backups, config) are the owner's acts and
# are refused to a program caller. A caller that names
# no program is the owner at their own vault, with the
# full access the program has always given them.
#
# Honesty (E-095 §3.2, restated for this shape): the
# name is claimed, not proven. This is the discipline
# that keeps well-behaved programs — the companion
# first, at E-100 — inside their own entries, and it
# stops accidents and casual browsing cold. It is NOT
# a wall against malicious code running as the same OS
# account: such code could claim any name, or read the
# vault files directly, and E-095's A2 verdict stands
# exactly as written. No Ember document may claim more
# for per-program access than this paragraph claims.
_PROGRAM_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")


def _normalize_program_name(raw) -> str:
    """Validate and normalize a program name, or refuse
    plainly: lowercase letters, digits, '.', '_' and '-',
    starting with a letter or digit, at most 64 chars."""
    name = str(raw or "").strip().lower()
    if not _PROGRAM_RE.match(name):
        print(
            "✗ That is not a usable program name. Use "
            "lowercase letters,\n"
            "  digits, '.', '_' or '-' (at most 64 "
            "characters, starting with\n"
            "  a letter or digit) — for example "
            "'ember-core'. Nothing was changed.",
            file=sys.stderr,
        )
        sys.exit(1)
    return name


def _caller_program() -> str:
    """The program the caller claims to be, from the
    KISTA_PROGRAM environment variable. '' means no
    program is claimed — the caller is the vault owner
    personally, and the owner sees everything."""
    raw = os.environ.get("KISTA_PROGRAM")
    if raw is None or not raw.strip():
        return ""
    return _normalize_program_name(raw)


def _entry_program(entry) -> str:
    """The program an entry belongs to ('' = the owner's
    own entry; entries written before E-097 have no
    field and read as the owner's)."""
    if isinstance(entry, dict):
        return str(entry.get("program") or "").strip().lower()
    return ""


def _program_sees(caller: str, entry) -> bool:
    """May this caller see/touch this entry? The owner
    (no program claimed) sees all; a program sees
    exactly its own."""
    return not caller or _entry_program(entry) == caller


def _visible_entries(entries: dict, caller: str) -> dict:
    """The caller's view of the vault: every entry for
    the owner, exactly the program's own for a program."""
    if not caller:
        return entries
    return {name: entry for name, entry in entries.items()
            if _program_sees(caller, entry)}


def _refuse_program_whole_vault(command_label: str) -> None:
    """Whole-vault and vault-life operations belong to
    the owner. A program caller is refused, plainly,
    before anything is touched."""
    caller = _caller_program()
    if caller:
        print(
            f"✗ '{command_label}' belongs to the vault "
            f"owner, not to a program.\n"
            f"  Program '{caller}' can only add, read, "
            "change, and remove its own\n"
            "  entries. Nothing was changed.",
            file=sys.stderr,
        )
        sys.exit(1)


def _not_found_for(service: str, caller: str) -> None:
    """The program-scoped 'not found': another program's
    entry and a missing entry get the same answer, so a
    program learns nothing about what else the vault
    holds — not even whether the name exists."""
    print(f"✗ No entry found for '{service}'")
    if caller:
        print(
            f"  Program '{caller}' can only see its own "
            "entries — this one is not\n"
            "  among them, or does not exist."
        )


def cmd_init(args) -> None:
    """Initialize the vault."""
    _refuse_program_whole_vault("init")
    _ensure_dir()
    if VAULT_KEY.exists() and VAULT_FILE.exists():
        print(f"✓ Vault already exists at {VAULT_DIR}")
        print(f"  Key: {VAULT_KEY}")
        print(f"  Data: {VAULT_FILE}")
        if _is_wrapped_key(VAULT_KEY.read_bytes()):
            print("  Passphrase: SET — unlocking to count entries.")
        key = _get_key()
        vault = _load_vault(key)
        print(f"  Entries: {len(vault.get('entries', {}))}")
        return
    key = _get_key()
    vault = {"version": 1, "entries": {}, "created": datetime.now(timezone.utc).isoformat()}
    _save_vault(vault, key)
    print(f"✓ Vault initialized at {VAULT_DIR}")
    print(f"  Key: {VAULT_KEY} (chmod 600, owned by you)")
    if _is_wrapped_key(VAULT_KEY.read_bytes()):
        print("  Passphrase: SET — a copy of this folder opens "
              "nothing without it.")
    else:
        print("  Passphrase: NOT set. Anyone who copies this "
              "folder can open the")
        print("  vault — the key travels with it. To protect "
              "it, run:")
        print("      kista set-passphrase")
        print("  and choose a passphrase you will not forget: "
              "a forgotten one")
        print("  means a lost vault, with no recovery. That "
              "warning is honest,")
        print("  not a scare tactic.")


def cmd_set_passphrase(args) -> None:
    """Set or change the vault passphrase (E-096).

    The vault key itself never changes — only its wrapping
    does — so every entry, backup, and export keeps
    working exactly as before. Setting a passphrase is
    what turns a copied vault folder from a total loss
    (E-095's central finding) into a locked box.
    """
    _refuse_program_whole_vault("set-passphrase")
    if not VAULT_KEY.exists():
        print(
            "✗ There is no vault here yet. Run 'kista init' "
            "first, then set a passphrase.",
            file=sys.stderr,
        )
        sys.exit(1)
    raw = VAULT_KEY.read_bytes()
    wrapped = _is_wrapped_key(raw)
    if wrapped:
        print("This vault already has a passphrase. To change "
              "it, first unlock with the passphrase you use now.")
        vault_key = _unwrap_key(raw)
    else:
        vault_key = _validate_key(raw)
    passphrase = _prompt_new_passphrase()
    _ensure_dir()
    _write_key_file(_wrap_key(vault_key, passphrase))
    global _unlocked_key_cache
    _unlocked_key_cache = vault_key
    print("✓ Passphrase set. From now on, a copy of this "
          "folder opens nothing")
    print("  without your passphrase — and neither does "
          "this one. You will be")
    print("  asked for it each time you open the vault in "
          "a new terminal.")


def cmd_remove_passphrase(args) -> None:
    """Remove the vault passphrase, in plain words first.

    Removal restores the E-095 shape exactly: the key
    travels with the vault again, and a copied folder
    opens whole. That consequence is stated before the
    act, never after.
    """
    _refuse_program_whole_vault("remove-passphrase")
    if not VAULT_KEY.exists():
        print("✗ There is no vault here yet.", file=sys.stderr)
        sys.exit(1)
    raw = VAULT_KEY.read_bytes()
    if not _is_wrapped_key(raw):
        print("This vault has no passphrase to remove — it "
              "already opens with its key file alone.")
        return
    print("Removing the passphrase means anyone who copies "
          "this folder can open")
    print("the vault — the protection E-096 added goes "
          "away completely.")
    vault_key = _unwrap_key(raw)
    _write_key_file(vault_key)
    global _unlocked_key_cache
    _unlocked_key_cache = vault_key
    print("✓ Passphrase removed. The vault now opens with "
          "its key file alone.")
    print("  You can set a new one any time with "
          "'kista set-passphrase'.")


def cmd_repair(args) -> None:
    """Attempt to repair a corrupted vault from backups."""
    _refuse_program_whole_vault("repair")
    key = _get_key()
    is_corrupt, error_msg = _is_vault_corrupt(key)
    if not is_corrupt:
        print("✓ Vault appears healthy — no repair needed.")
        return
    print(f"⚠ Vault corruption detected: {error_msg}")
    print("  Attempting auto-repair from backup...")
    if _attempt_auto_repair(key):
        print("✓ Vault successfully repaired from backup!")
        # Verify the repair
        key = _get_key()
        vault = _load_vault(key)
        print(f"  Entries recovered: {len(vault.get('entries', {}))}")
    else:
        print("✗ No valid backup found for repair.", file=sys.stderr)
        print("  You may need to re-initialize the vault with 'kista init'.", file=sys.stderr)
        sys.exit(1)


def cmd_add(args) -> None:
    """Add a new entry (of any type)."""
    # Per-program access (E-097): a program caller adds
    # only for itself; the owner may assign an entry to
    # a program with --program. An entry a program adds
    # is stamped with that program's name, and no caller
    # may stamp an entry with another program's name.
    caller = _caller_program()
    requested_raw = getattr(args, "program", None)
    if requested_raw:
        requested = _normalize_program_name(requested_raw)
        if caller and requested != caller:
            print(
                f"✗ Program '{caller}' can only add "
                f"entries for itself, not for "
                f"'{requested}'.\n"
                "  Nothing was changed.",
                file=sys.stderr,
            )
            sys.exit(1)
        owner_program = requested
    else:
        owner_program = caller
    key = _get_key()
    vault = _load_vault(key)
    entries = vault.setdefault("entries", {})

    service = args.service.lower()
    if caller and service in entries and not _program_sees(caller, entries[service]):
        # A program may not overwrite — or learn the
        # shape of — another program's entry, even with
        # --force (E-097).
        print(
            f"✗ The name '{service}' cannot be used by "
            f"program '{caller}'.\n"
            "  It is taken, or it belongs to another "
            "program. Nothing was changed.",
            file=sys.stderr,
        )
        sys.exit(1)
    if service in entries and not getattr(args, "force", False):
        print(f"✗ Entry for '{service}' already exists. Use --force to overwrite or 'update' to modify.")
        sys.exit(1)

    entry_type = getattr(args, "entry_type", "credential") or "credential"
    # If entry_type is still "credential" but command is a type shortcut, infer the type
    if entry_type == "credential":
        _SHORTCUT_TYPES = {
            "add-apikey": "apikey",
            "add-sshkey": "sshkey",
            "add-certificate": "certificate",
            "add-note": "note",
            "add-totp": "totp",
            "add-license": "license",
            "add-identity": "identity",
            "add-url": "url",
            "add-astrology": "astrology",
            "add-character-sheet": "character-sheet",
            "add-rune-reading": "rune-reading",
            "add-tarot-reading": "tarot-reading",
            "add-markdown": "markdown",
            "add-person": "identity",
        }
        cmd = getattr(args, "command", None)
        if cmd in _SHORTCUT_TYPES:
            entry_type = _SHORTCUT_TYPES[cmd]
    if entry_type not in ENTRY_TYPE_SCHEMAS:
        print(f"✗ Unknown entry type '{entry_type}'. Valid types: {', '.join(ENTRY_TYPE_SCHEMAS.keys())}")
        sys.exit(1)

    entry = {
        "service": service,
        "entry_type": entry_type,
        "program": owner_program,
        "created": datetime.now(timezone.utc).isoformat(),
        "updated": datetime.now(timezone.utc).isoformat(),
    }

    # Add common fields (present for all types)
    password = _resolve_password(args)
    entry["username"] = getattr(args, "username", None) or ""
    entry["password"] = password
    entry["email"] = getattr(args, "email", None) or ""
    entry["url"] = getattr(args, "url", None) or ""
    common_notes = getattr(args, "notes", None) or ""
    entry["notes"] = common_notes
    entry["tags"] = _parse_tags(getattr(args, "tags", None)) if getattr(args, "tags", None) else []

    # Add type-specific fields
    if entry_type == "apikey":
        entry["key"] = getattr(args, "key_arg", None) or ""
        entry["expires"] = getattr(args, "expires", None) or ""
        entry["service_url"] = getattr(args, "service_url", None) or ""
        entry["rate_limit"] = getattr(args, "rate_limit", None) or ""
        entry["scopes"] = getattr(args, "scopes", None) or ""

    elif entry_type == "sshkey":
        key_file = getattr(args, "key_file", None)
        if key_file:
            entry["private_key"] = _read_file_content(key_file)
        else:
            entry["private_key"] = ""
        entry["public_key"] = getattr(args, "public_key", None) or ""
        entry["passphrase"] = getattr(args, "passphrase", None) or ""
        entry["key_type"] = getattr(args, "key_type", None) or ""
        entry["host"] = getattr(args, "host", None) or ""

    elif entry_type == "certificate":
        cert_file = getattr(args, "cert_file", None)
        if cert_file:
            entry["cert"] = _read_file_content(cert_file)
        else:
            entry["cert"] = ""
        key_file = getattr(args, "key_file", None)
        if key_file:
            entry["key"] = _read_file_content(key_file)
        else:
            entry["key"] = ""
        entry["domain"] = getattr(args, "domain", None) or ""
        entry["issuer"] = getattr(args, "issuer", None) or ""
        entry["expires"] = getattr(args, "expires", None) or getattr(args, "expires_field", None) or ""
        entry["chain"] = getattr(args, "chain", None) or ""

    elif entry_type == "note":
        content = getattr(args, "content", None) or ""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        if content and not content.startswith("[20"):
            content = f"[{timestamp}] {content}"
        entry["content"] = content
        entry["category"] = getattr(args, "category", None) or ""

    elif entry_type == "totp":
        entry["secret"] = getattr(args, "secret", None) or ""
        entry["digits"] = getattr(args, "digits", None) or 6
        entry["period"] = getattr(args, "period", None) or 30
        entry["algorithm"] = getattr(args, "algorithm", None) or "SHA1"
        entry["issuer"] = getattr(args, "issuer", None) or ""

    elif entry_type == "license":
        entry["key"] = getattr(args, "key_arg", None) or ""
        entry["product"] = getattr(args, "product", None) or ""
        entry["seats"] = getattr(args, "seats", None) or ""
        entry["expires"] = getattr(args, "expires", None) or getattr(args, "expires_field", None) or ""
        entry["order_id"] = getattr(args, "order_id", None) or ""

    elif entry_type == "identity":
        entry["full_name"] = getattr(args, "full_name", None) or ""
        entry["birth_date"] = getattr(args, "birth_date", None) or ""
        entry["id_number"] = getattr(args, "id_number", None) or ""
        entry["id_type"] = getattr(args, "id_type", None) or ""
        entry["address"] = getattr(args, "address", None) or ""
        entry["phone"] = getattr(args, "phone_arg", None) or getattr(args, "phone", None) or ""
        entry["national_id"] = getattr(args, "national_id", None) or ""

    elif entry_type == "url":
        entry["url"] = getattr(args, "url", None) or ""
        entry["title"] = getattr(args, "title_arg", None) or getattr(args, "title", None) or ""
        entry["description"] = getattr(args, "description", None) or ""

    # === NEW v2.0 Entry Types ===
    elif entry_type == "astrology":
        entry["sign"] = getattr(args, "sign", None) or ""
        entry["date"] = getattr(args, "astro_date", None) or ""
        entry["sun_position"] = getattr(args, "sun_position", None) or ""
        entry["moon_position"] = getattr(args, "moon_position", None) or ""
        entry["mercury_position"] = getattr(args, "mercury_position", None) or ""
        entry["venus_position"] = getattr(args, "venus_position", None) or ""
        entry["mars_position"] = getattr(args, "mars_position", None) or ""
        entry["jupiter_position"] = getattr(args, "jupiter_position", None) or ""
        entry["saturn_position"] = getattr(args, "saturn_position", None) or ""
        entry["ascendant"] = getattr(args, "ascendant", None) or ""
        entry["mc"] = getattr(args, "mc", None) or ""
        entry["aspects"] = _parse_json_field(getattr(args, "aspects", None) or "")
        entry["notes"] = common_notes or getattr(args, "notes", None) or ""

    elif entry_type == "character-sheet":
        entry["name"] = getattr(args, "char_name", None) or ""
        entry["race"] = getattr(args, "race", None) or ""
        entry["class"] = getattr(args, "char_class", None) or ""
        entry["level"] = getattr(args, "level", None) or 1
        entry["background"] = getattr(args, "background", None) or ""
        entry["alignment"] = getattr(args, "alignment", None) or ""
        entry["str"] = getattr(args, "str_score", None) or 10
        entry["dex"] = getattr(args, "dex_score", None) or 10
        entry["con"] = getattr(args, "con_score", None) or 10
        entry["int"] = getattr(args, "int_score", None) or 10
        entry["wis"] = getattr(args, "wis_score", None) or 10
        entry["cha"] = getattr(args, "cha_score", None) or 10
        entry["ac"] = getattr(args, "ac", None) or 10
        entry["hp"] = getattr(args, "hp", None) or 0
        entry["speed"] = getattr(args, "speed", None) or 30
        entry["prof_bonus"] = getattr(args, "prof_bonus", None) or 2
        entry["skills"] = _parse_json_field(getattr(args, "skills", None) or "")
        entry["features"] = _parse_json_field(getattr(args, "features", None) or "")
        entry["equipment"] = _parse_json_field(getattr(args, "equipment", None) or "")
        entry["spells"] = _parse_json_field(getattr(args, "spells", None) or "")
        entry["backstory"] = getattr(args, "backstory", None) or ""
        entry["notes"] = common_notes or getattr(args, "notes", None) or ""

    elif entry_type == "rune-reading":
        entry["spread_type"] = getattr(args, "spread_type", None) or ""
        entry["runes_drawn"] = _parse_json_field(getattr(args, "runes_drawn", None) or "")
        entry["positions"] = _parse_json_field(getattr(args, "positions", None) or "")
        entry["interpretation"] = getattr(args, "interpretation", None) or ""
        entry["question"] = getattr(args, "question", None) or ""
        entry["date_drawn"] = getattr(args, "date_drawn", None) or datetime.now(timezone.utc).strftime("%Y-%m-%d")
        entry["notes"] = common_notes or getattr(args, "notes", None) or ""

    elif entry_type == "tarot-reading":
        entry["spread_type"] = getattr(args, "spread_type", None) or ""
        entry["cards_drawn"] = _parse_json_field(getattr(args, "cards_drawn", None) or "")
        entry["positions"] = _parse_json_field(getattr(args, "positions", None) or "")
        entry["interpretation"] = getattr(args, "interpretation", None) or ""
        entry["question"] = getattr(args, "question", None) or ""
        entry["date_drawn"] = getattr(args, "date_drawn", None) or datetime.now(timezone.utc).strftime("%Y-%m-%d")
        entry["notes"] = common_notes or getattr(args, "notes", None) or ""

    elif entry_type == "markdown":
        # E-098 (docket 137): the general add road's
        # --title / --content flags land on `title` /
        # `content`, and the shortcut's on `md_title` /
        # `md_content` — read both, as cmd_update's
        # markdown branch already did for title. Before
        # this fix neither add road could satisfy the
        # type's two required fields at all.
        entry["title"] = getattr(args, "md_title", None) or getattr(args, "title_arg", None) or getattr(args, "title", None) or ""
        entry["content"] = getattr(args, "md_content", None) or getattr(args, "content", None) or ""
        entry["category"] = getattr(args, "md_category", None) or getattr(args, "category", None) or ""
        # For markdown entry type, tags override common tags
        entry["tags"] = _parse_json_field(getattr(args, "md_tags", None) or "") if getattr(args, "md_tags", None) else (entry.get("tags", []) if entry.get("tags") else "")
        entry["source_url"] = getattr(args, "source_url", None) or ""
        entry["notes"] = common_notes or getattr(args, "notes", None) or ""

    # Validate required fields
    schema = ENTRY_TYPE_SCHEMAS[entry_type]
    for field_name, (required, default) in schema.items():
        if required:
            val = entry.get(field_name)
            if not val:
                print(f"✗ Required field '{field_name}' missing for type '{entry_type}'.")
                sys.exit(1)

    entries[service] = entry
    _save_vault(vault, key)
    print(f"✓ Added {entry_type} for '{service}'")
    if owner_program:
        print(f"  Belongs to program: {owner_program} — only "
              f"that program (and you, the owner) can reach it.")
    if entry_type in OTHER_ROAD_ENTRY_TYPES:
        # E-098: a kind from the other road is never
        # silently merged into the toaster set — the
        # add succeeds exactly as given, and the
        # program says whose road the kind is, in
        # words, at the moment it enters.
        _note_other_road_kind(entry_type)


def cmd_get(args) -> None:
    """Get an entry (full details)."""
    caller = _caller_program()
    key = _get_key()
    vault = _load_vault(key)
    entries = vault.get("entries", {})

    service = args.service.lower()
    if service not in entries or not _program_sees(caller, entries[service]):
        if caller:
            # Program-scoped: another program's entry and
            # a missing entry answer identically, and the
            # available-services list is never shown to a
            # program (it would name other programs'
            # entries).
            _not_found_for(service, caller)
        else:
            print(f"✗ No entry found for '{service}'")
            print(f"  Available: {', '.join(sorted(entries.keys())) or '(empty)'}")
        sys.exit(1)

    entry = entries[service]
    print(json.dumps(entry, indent=2, ensure_ascii=False))


def cmd_list(args) -> None:
    """List all entries (passwords and sensitive fields masked)."""
    caller = _caller_program()
    key = _get_key()
    vault = _load_vault(key)
    entries = _visible_entries(vault.get("entries", {}), caller)

    if not entries:
        if caller:
            print(f"No entries for program '{caller}' yet.")
        else:
            print("No entries stored yet. Use 'add' to create one.")
        return

    tag_filter = args.tags.lower() if args.tags else None

    print(f"{'Service':<20} {'Type':<17} {'Identity':<30} {'Tags':<20} {'Updated'}")
    print("-" * 115)

    for service, entry in sorted(entries.items()):
        tags = ", ".join(entry.get("tags", [])) if isinstance(entry.get("tags", []), list) else str(entry.get("tags", ""))
        if tag_filter and tag_filter not in tags.lower():
            continue
        entry_type = entry.get("entry_type", "credential")
        # Identity display varies by type
        identity = _get_identity_display(entry_type, entry)
        updated = entry.get("updated", "?")[:10]
        print(f"{service:<20} {entry_type:<17} {identity:<30} {tags:<20} {updated}")


def _get_identity_display(entry_type: str, entry: dict) -> str:
    """Get the identity display string for a given entry type."""
    if entry_type == "credential":
        return entry.get("email") or entry.get("username") or "(no identity)"
    elif entry_type == "apikey":
        return entry.get("service_url") or "(no URL)"
    elif entry_type == "sshkey":
        return f"{entry.get('key_type', '?')}@{entry.get('host', '?')}"
    elif entry_type == "certificate":
        return entry.get("domain") or "(no domain)"
    elif entry_type == "note":
        return entry.get("category") or "(no category)"
    elif entry_type == "totp":
        return entry.get("issuer") or "(no issuer)"
    elif entry_type == "license":
        return entry.get("product") or "(no product)"
    elif entry_type == "identity":
        return entry.get("full_name") or "(no name)"
    elif entry_type == "url":
        return entry.get("title") or entry.get("url") or "(no URL)"
    elif entry_type == "astrology":
        return entry.get("sign") or "(no sign)"
    elif entry_type == "character-sheet":
        return entry.get("name") or "(no name)"
    elif entry_type == "rune-reading":
        return entry.get("spread_type") or "(no spread)"
    elif entry_type == "tarot-reading":
        return entry.get("spread_type") or "(no spread)"
    elif entry_type == "markdown":
        return entry.get("title") or "(no title)"
    else:
        return "(unknown)"


def cmd_update(args) -> None:
    """Update specific fields of an entry."""
    caller = _caller_program()
    key = _get_key()
    vault = _load_vault(key)
    entries = vault.get("entries", {})

    service = args.service.lower()
    if service not in entries or not _program_sees(caller, entries[service]):
        if caller:
            _not_found_for(service, caller)
        else:
            print(f"✗ No entry found for '{service}'")
        sys.exit(1)

    entry = entries[service]
    entry_type = entry.get("entry_type", "credential")
    updated = False

    # Common fields (available for all types)
    if getattr(args, "username", None):
        entry["username"] = args.username
        updated = True
    if _has_password_source(args):
        entry["password"] = _resolve_password(args)
        updated = True
    if getattr(args, "email", None):
        entry["email"] = args.email
        updated = True
    if getattr(args, "url", None):
        entry["url"] = args.url
        updated = True
    if getattr(args, "notes", None):
        entry["notes"] = args.notes
        updated = True
    if getattr(args, "tags", None):
        entry["tags"] = _parse_tags(args.tags)
        updated = True

    # Type-specific field updates
    if entry_type == "apikey":
        if getattr(args, "key_arg", None):
            entry["key"] = args.key_arg
            updated = True
        if getattr(args, "expires", None):
            entry["expires"] = args.expires
            updated = True
        if getattr(args, "service_url", None):
            entry["service_url"] = args.service_url
            updated = True
        if getattr(args, "rate_limit", None):
            entry["rate_limit"] = args.rate_limit
            updated = True
        if getattr(args, "scopes", None):
            entry["scopes"] = args.scopes
            updated = True

    elif entry_type == "sshkey":
        if getattr(args, "key_file", None):
            entry["private_key"] = _read_file_content(args.key_file)
            updated = True
        if getattr(args, "public_key", None):
            entry["public_key"] = args.public_key
            updated = True
        if getattr(args, "passphrase", None):
            entry["passphrase"] = args.passphrase
            updated = True
        if getattr(args, "key_type", None):
            entry["key_type"] = args.key_type
            updated = True
        if getattr(args, "host", None):
            entry["host"] = args.host
            updated = True

    elif entry_type == "certificate":
        if getattr(args, "cert_file", None):
            entry["cert"] = _read_file_content(args.cert_file)
            updated = True
        if getattr(args, "key_file", None):
            entry["key"] = _read_file_content(args.key_file)
            updated = True
        if getattr(args, "domain", None):
            entry["domain"] = args.domain
            updated = True
        if getattr(args, "issuer", None):
            entry["issuer"] = args.issuer
            updated = True
        if getattr(args, "expires_field", None):
            entry["expires"] = args.expires_field
            updated = True
        if getattr(args, "chain", None):
            entry["chain"] = args.chain
            updated = True

    elif entry_type == "note":
        if getattr(args, "content", None):
            content = args.content
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            if content and not content.startswith("[20"):
                content = f"[{timestamp}] {content}"
            entry["content"] = content
            updated = True
        if getattr(args, "category", None):
            entry["category"] = args.category
            updated = True

    elif entry_type == "totp":
        if getattr(args, "secret", None):
            entry["secret"] = args.secret
            updated = True
        if getattr(args, "digits", None) is not None:
            entry["digits"] = args.digits
            updated = True
        if getattr(args, "period", None) is not None:
            entry["period"] = args.period
            updated = True
        if getattr(args, "algorithm", None):
            entry["algorithm"] = args.algorithm
            updated = True
        if getattr(args, "issuer", None):
            entry["issuer"] = args.issuer
            updated = True

    elif entry_type == "license":
        if getattr(args, "key_arg", None):
            entry["key"] = args.key_arg
            updated = True
        if getattr(args, "product", None):
            entry["product"] = args.product
            updated = True
        if getattr(args, "seats", None):
            entry["seats"] = args.seats
            updated = True
        if getattr(args, "expires_field", None):
            entry["expires"] = args.expires_field
            updated = True
        if getattr(args, "order_id", None):
            entry["order_id"] = args.order_id
            updated = True

    elif entry_type == "identity":
        if getattr(args, "full_name", None):
            entry["full_name"] = args.full_name
            updated = True
        if getattr(args, "birth_date", None):
            entry["birth_date"] = args.birth_date
            updated = True
        if getattr(args, "id_number", None):
            entry["id_number"] = args.id_number
            updated = True
        if getattr(args, "id_type", None):
            entry["id_type"] = args.id_type
            updated = True
        if getattr(args, "address", None):
            entry["address"] = args.address
            updated = True
        if getattr(args, "phone_arg", None):
            entry["phone"] = args.phone_arg
            updated = True
        if getattr(args, "national_id", None):
            entry["national_id"] = args.national_id
            updated = True

    elif entry_type == "url":
        if getattr(args, "url", None):
            entry["url"] = args.url
            updated = True
        if getattr(args, "title_arg", None) or getattr(args, "title", None):
            entry["title"] = getattr(args, "title_arg", None) or args.title
            updated = True
        if getattr(args, "description", None):
            entry["description"] = args.description
            updated = True

    # === NEW v2.0 type updates ===
    elif entry_type == "astrology":
        if getattr(args, "sign", None):
            entry["sign"] = args.sign
            updated = True
        if getattr(args, "astro_date", None):
            entry["date"] = args.astro_date
            updated = True
        if getattr(args, "sun_position", None):
            entry["sun_position"] = args.sun_position
            updated = True
        if getattr(args, "moon_position", None):
            entry["moon_position"] = args.moon_position
            updated = True
        if getattr(args, "mercury_position", None):
            entry["mercury_position"] = args.mercury_position
            updated = True
        if getattr(args, "venus_position", None):
            entry["venus_position"] = args.venus_position
            updated = True
        if getattr(args, "mars_position", None):
            entry["mars_position"] = args.mars_position
            updated = True
        if getattr(args, "jupiter_position", None):
            entry["jupiter_position"] = args.jupiter_position
            updated = True
        if getattr(args, "saturn_position", None):
            entry["saturn_position"] = args.saturn_position
            updated = True
        if getattr(args, "ascendant", None):
            entry["ascendant"] = args.ascendant
            updated = True
        if getattr(args, "mc", None):
            entry["mc"] = args.mc
            updated = True
        if getattr(args, "aspects", None):
            entry["aspects"] = _parse_json_field(args.aspects)
            updated = True

    elif entry_type == "character-sheet":
        if getattr(args, "char_name", None):
            entry["name"] = args.char_name
            updated = True
        if getattr(args, "race", None):
            entry["race"] = args.race
            updated = True
        if getattr(args, "char_class", None):
            entry["class"] = args.char_class
            updated = True
        if getattr(args, "level", None) is not None:
            entry["level"] = args.level
            updated = True
        if getattr(args, "background", None):
            entry["background"] = args.background
            updated = True
        if getattr(args, "alignment", None):
            entry["alignment"] = args.alignment
            updated = True
        if getattr(args, "str_score", None) is not None:
            entry["str"] = args.str_score
            updated = True
        if getattr(args, "dex_score", None) is not None:
            entry["dex"] = args.dex_score
            updated = True
        if getattr(args, "con_score", None) is not None:
            entry["con"] = args.con_score
            updated = True
        if getattr(args, "int_score", None) is not None:
            entry["int"] = args.int_score
            updated = True
        if getattr(args, "wis_score", None) is not None:
            entry["wis"] = args.wis_score
            updated = True
        if getattr(args, "cha_score", None) is not None:
            entry["cha"] = args.cha_score
            updated = True
        if getattr(args, "ac", None) is not None:
            entry["ac"] = args.ac
            updated = True
        if getattr(args, "hp", None) is not None:
            entry["hp"] = args.hp
            updated = True
        if getattr(args, "speed", None) is not None:
            entry["speed"] = args.speed
            updated = True
        if getattr(args, "prof_bonus", None) is not None:
            entry["prof_bonus"] = args.prof_bonus
            updated = True
        if getattr(args, "skills", None):
            entry["skills"] = _parse_json_field(args.skills)
            updated = True
        if getattr(args, "features", None):
            entry["features"] = _parse_json_field(args.features)
            updated = True
        if getattr(args, "equipment", None):
            entry["equipment"] = _parse_json_field(args.equipment)
            updated = True
        if getattr(args, "spells", None):
            entry["spells"] = _parse_json_field(args.spells)
            updated = True
        if getattr(args, "backstory", None):
            entry["backstory"] = args.backstory
            updated = True

    elif entry_type == "rune-reading":
        if getattr(args, "spread_type", None):
            entry["spread_type"] = args.spread_type
            updated = True
        if getattr(args, "runes_drawn", None):
            entry["runes_drawn"] = _parse_json_field(args.runes_drawn)
            updated = True
        if getattr(args, "positions", None):
            entry["positions"] = _parse_json_field(args.positions)
            updated = True
        if getattr(args, "interpretation", None):
            entry["interpretation"] = args.interpretation
            updated = True
        if getattr(args, "question", None):
            entry["question"] = args.question
            updated = True
        if getattr(args, "date_drawn", None):
            entry["date_drawn"] = args.date_drawn
            updated = True

    elif entry_type == "tarot-reading":
        if getattr(args, "spread_type", None):
            entry["spread_type"] = args.spread_type
            updated = True
        if getattr(args, "cards_drawn", None):
            entry["cards_drawn"] = _parse_json_field(args.cards_drawn)
            updated = True
        if getattr(args, "positions", None):
            entry["positions"] = _parse_json_field(args.positions)
            updated = True
        if getattr(args, "interpretation", None):
            entry["interpretation"] = args.interpretation
            updated = True
        if getattr(args, "question", None):
            entry["question"] = args.question
            updated = True
        if getattr(args, "date_drawn", None):
            entry["date_drawn"] = args.date_drawn
            updated = True

    elif entry_type == "markdown":
        if getattr(args, "md_title", None) or getattr(args, "title_arg", None) or getattr(args, "title", None):
            entry["title"] = getattr(args, "md_title", None) or getattr(args, "title_arg", None) or args.title
            updated = True
        if getattr(args, "md_content", None):
            entry["content"] = args.md_content
            updated = True
        if getattr(args, "md_category", None) or getattr(args, "category", None):
            entry["category"] = getattr(args, "md_category", None) or args.category
            updated = True
        if getattr(args, "md_tags", None):
            entry["tags"] = _parse_json_field(args.md_tags)
            updated = True
        if getattr(args, "source_url", None):
            entry["source_url"] = args.source_url
            updated = True

    # Ownership changes (E-097): only the vault owner
    # may say who an entry belongs to. A program cannot
    # give its entries away, take another program's, or
    # un-own one — that act is the owner's, in person.
    new_program = getattr(args, "program", None)
    unassign = getattr(args, "unassign_program", False)
    if new_program or unassign:
        if caller:
            print(
                f"✗ Program '{caller}' cannot change who "
                "an entry belongs to.\n"
                "  Only the vault owner can do that. "
                "Nothing was changed.",
                file=sys.stderr,
            )
            sys.exit(1)
        if unassign:
            entry["program"] = ""
        else:
            entry["program"] = _normalize_program_name(new_program)
        updated = True

    if updated:
        entry["updated"] = datetime.now(timezone.utc).isoformat()
        _save_vault(vault, key)
        print(f"✓ Updated {entry_type} for '{service}'")
    else:
        print("No fields specified to update.")


def cmd_remove(args) -> None:
    """Remove an entry."""
    caller = _caller_program()
    key = _get_key()
    vault = _load_vault(key)
    entries = vault.get("entries", {})

    service = args.service.lower()
    if service not in entries or not _program_sees(caller, entries[service]):
        if caller:
            _not_found_for(service, caller)
        else:
            print(f"✗ No entry found for '{service}'")
        sys.exit(1)

    del entries[service]
    _save_vault(vault, key)
    print(f"✓ Removed entry for '{service}'")


def cmd_check(args) -> None:
    """Check if an entry exists and show status."""
    caller = _caller_program()
    key = _get_key()
    vault = _load_vault(key)
    entries = vault.get("entries", {})

    service = args.service.lower()
    if service in entries and not _program_sees(caller, entries[service]):
        # Another program's entry checks as absent: a
        # program does not even learn that the name
        # exists (E-097).
        _not_found_for(service, caller)
        return
    if service in entries:
        entry = entries[service]
        entry_type = entry.get("entry_type", "credential")
        print(f"✓ Entry exists for '{service}' (type: {entry_type})")

        # Show type-appropriate summary fields
        if entry_type == "credential":
            print(f"  Email: {entry.get('email', '(not set)')}")
            print(f"  Username: {entry.get('username', '(not set)')}")
            print(f"  Has password: {'Yes' if entry.get('password') else 'No'}")
            print(f"  URL: {entry.get('url', '(not set)')}")
        elif entry_type == "apikey":
            print(f"  Has key: {'Yes' if entry.get('key') else 'No'}")
            print(f"  Service URL: {entry.get('service_url', '(not set)')}")
            print(f"  Expires: {entry.get('expires', '(not set)')}")
        elif entry_type == "sshkey":
            print(f"  Key type: {entry.get('key_type', '(not set)')}")
            print(f"  Host: {entry.get('host', '(not set)')}")
            print(f"  Has private key: {'Yes' if entry.get('private_key') else 'No'}")
        elif entry_type == "certificate":
            print(f"  Domain: {entry.get('domain', '(not set)')}")
            print(f"  Issuer: {entry.get('issuer', '(not set)')}")
            print(f"  Expires: {entry.get('expires', '(not set)')}")
        elif entry_type == "note":
            print(f"  Category: {entry.get('category', '(not set)')}")
        elif entry_type == "totp":
            print(f"  Issuer: {entry.get('issuer', '(not set)')}")
            print(f"  Digits: {entry.get('digits', 6)}")
            print(f"  Period: {entry.get('period', 30)}s")
        elif entry_type == "license":
            print(f"  Product: {entry.get('product', '(not set)')}")
            print(f"  Expires: {entry.get('expires', '(not set)')}")
        elif entry_type == "identity":
            print(f"  Name: {entry.get('full_name', '(not set)')}")
        elif entry_type == "url":
            print(f"  URL: {entry.get('url', '(not set)')}")
            print(f"  Title: {entry.get('title', '(not set)')}")
            print(f"  Description: {entry.get('description', '(not set)')}")
        elif entry_type == "astrology":
            print(f"  Sign: {entry.get('sign', '(not set)')}")
            print(f"  Date: {entry.get('date', '(not set)')}")
            print(f"  Sun: {entry.get('sun_position', '(not set)')}")
            print(f"  Moon: {entry.get('moon_position', '(not set)')}")
            print(f"  Ascendant: {entry.get('ascendant', '(not set)')}")
        elif entry_type == "character-sheet":
            print(f"  Name: {entry.get('name', '(not set)')}")
            print(f"  Race/Class: {entry.get('race', '?')} {entry.get('class', '?')}")
            print(f"  Level: {entry.get('level', '?')}")
            print(f"  HP/AC: {entry.get('hp', '?')}/{entry.get('ac', '?')}")
        elif entry_type == "rune-reading":
            print(f"  Spread: {entry.get('spread_type', '(not set)')}")
            print(f"  Runes: {entry.get('runes_drawn', '(not set)')}")
            print(f"  Date: {entry.get('date_drawn', '(not set)')}")
        elif entry_type == "tarot-reading":
            print(f"  Spread: {entry.get('spread_type', '(not set)')}")
            print(f"  Cards: {entry.get('cards_drawn', '(not set)')}")
            print(f"  Date: {entry.get('date_drawn', '(not set)')}")
        elif entry_type == "markdown":
            print(f"  Title: {entry.get('title', '(not set)')}")
            print(f"  Category: {entry.get('category', '(not set)')}")

        print(f"  Tags: {', '.join(entry.get('tags', [])) if isinstance(entry.get('tags', []), list) else entry.get('tags', '') or '(none)'}")
        print(f"  Created: {entry.get('created', '?')[:10]}")
        print(f"  Updated: {entry.get('updated', '?')[:10]}")
    else:
        if caller:
            _not_found_for(service, caller)
        else:
            print(f"✗ No entry found for '{service}'")


def cmd_status(args) -> None:
    """Show vault status."""
    _ensure_dir()
    print(f"Vault directory: {VAULT_DIR}")
    print(f"Key file: {VAULT_KEY} ({'exists' if VAULT_KEY.exists() else 'MISSING'})")
    if VAULT_KEY.exists():
        _wrapped = _is_wrapped_key(VAULT_KEY.read_bytes())
        print(f"Passphrase: {'SET — this vault asks before it opens' if _wrapped else 'NOT set — a copy of this folder opens the vault; run set-passphrase to protect it'}")
    print(f"Data file: {VAULT_FILE} ({'exists' if VAULT_FILE.exists() else 'empty'})")
    print(f"Kista version: {__version__}")
    print(f"Platform: {platform.system()} {platform.machine()}")

    if VAULT_FILE.exists() and VAULT_KEY.exists():
        key = _get_key()
        # Check for corruption
        is_corrupt, error_msg = _is_vault_corrupt(key)
        if is_corrupt:
            print(f"⚠ VAULT CORRUPTION DETECTED: {error_msg}")
            print("  Run 'kista repair' to attempt auto-repair from backup.")
        else:
            vault = _load_vault(key)
            # A program caller sees only its own entries
            # counted and named here (E-097); the owner
            # sees the whole vault, as always.
            caller = _caller_program()
            entries = _visible_entries(vault.get("entries", {}), caller)
            print(f"Vault version: {vault.get('version', '?')}")
            if caller:
                print(f"Program: {caller} — status covers "
                      "only that program's entries")
            print(f"Entries: {len(entries)}")
            # Count by type
            type_counts = {}
            for entry in entries.values():
                et = entry.get("entry_type", "credential")
                type_counts[et] = type_counts.get(et, 0) + 1
            for et, count in sorted(type_counts.items()):
                print(f"  {et}: {count}")
            print(f"Services: {', '.join(sorted(entries.keys())[:20])}{'...' if len(entries) > 20 else '' or '(none)'}")
            print(f"Created: {vault.get('created', '?')}")
            print(f"Updated: {vault.get('updated', '?')}")

        # Backup and config counts are whole-vault facts:
        # they are shown to the owner, never to a program
        # caller (E-097).
        if not _caller_program():
            # Show backup info
            backup_dir = VAULT_DIR / "backups"
            if backup_dir.exists():
                backups = list(backup_dir.glob("vault_backup_*.enc"))
                print(f"Backups: {len(backups)} available")

            # Show config
            config = _load_config()
            if config:
                print(f"Config: {len(config)} settings")
    else:
        print("Vault not initialized. Run 'init' to create.")


def cmd_search(args) -> None:
    """Fuzzy search across services and all fields, with optional date filtering."""
    caller = _caller_program()
    key = _get_key()
    vault = _load_vault(key)
    entries = _visible_entries(vault.get("entries", {}), caller)

    query = (args.query or "").lower()
    date_filter = getattr(args, "date", None)
    from_date = getattr(args, "from_date", None)
    to_date = getattr(args, "to_date", None)
    after = getattr(args, "after", None)
    before = getattr(args, "before", None)

    def _parse_date(d):
        """Parse date string (date-only or datetime) to comparable format."""
        if not d:
            return None
        d = d.strip()
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d"):
            try:
                return datetime.strptime(d, fmt)
            except ValueError:
                continue
        return None

    def _matches_date(created_str):
        """Check if an entry's created timestamp matches date filters."""
        if not created_str:
            return not any([date_filter, from_date, to_date, after, before])
        for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"):
            try:
                created = datetime.strptime(created_str[:26].split("+")[0].split("Z")[0], fmt)
                break
            except ValueError:
                continue
        else:
            return not any([date_filter, from_date, to_date, after, before])

        if date_filter:
            day = _parse_date(date_filter)
            if day:
                next_day = day.replace(hour=23, minute=59, second=59)
                if not (day <= created <= next_day):
                    return False
        if from_date:
            fd = _parse_date(from_date)
            if fd and created < fd:
                return False
        if to_date:
            td = _parse_date(to_date)
            if td:
                td = td.replace(hour=23, minute=59, second=59)
                if created > td:
                    return False
        if after:
            ad = _parse_date(after)
            if ad and created <= ad:
                return False
        if before:
            bd = _parse_date(before)
            if bd and created >= bd:
                return False
        return True

    results = []
    for service, entry in entries.items():
        # Date filter first (most selective)
        if not _matches_date(entry.get("created")):
            continue
        # If no text query, date-only search
        if not query:
            results.append(service)
            continue
        # Text search
        if query in service:
            results.append(service)
            continue
        searchable = " ".join(str(v) for v in entry.values() if isinstance(v, str))
        if query in searchable.lower():
            results.append(service)
            continue
        tags = entry.get("tags", [])
        if isinstance(tags, list) and any(query in t for t in tags):
            results.append(service)

    if not results:
        print(f"No matches for '{query}'")
    else:
        print(f"Found {len(results)} match(es):")
        for svc in sorted(results):
            entry = entries[svc]
            entry_type = entry.get("entry_type", "credential")
            identity = _get_identity_display(entry_type, entry)
            tags = ", ".join(entry.get("tags", [])) if isinstance(entry.get("tags", []), list) else str(entry.get("tags", ""))
            print(f"  {svc:<25} [{entry_type}] {identity:<30} {tags}")


def cmd_generate_password(args) -> None:
    """Generate a random password."""
    length = args.length if hasattr(args, "length") and args.length else 20
    alphabet = string.ascii_letters + string.digits + string.punctuation
    # Ensure at least one of each character class
    while True:
        password = "".join(secrets.choice(alphabet) for _ in range(length))
        has_lower = any(c in string.ascii_lowercase for c in password)
        has_upper = any(c in string.ascii_uppercase for c in password)
        has_digit = any(c in string.digits for c in password)
        has_symbol = any(c in string.punctuation for c in password)
        if has_lower and has_upper and has_digit and has_symbol:
            break
    print(password)


def cmd_export(args) -> None:
    """Export all credentials as encrypted backup."""
    _refuse_program_whole_vault("export")
    if not VAULT_FILE.exists():
        print("✗ No vault to export.")
        sys.exit(1)
    key = _get_key()
    try:
        _load_vault(key)
    except (SystemExit, Exception) as exc:
        print(f"✗ Cannot export a corrupt vault. {exc}", file=sys.stderr)
        sys.exit(1)

    import shutil
    dest = Path(args.output) if args.output else VAULT_DIR / "vault_backup.enc"
    shutil.copy2(VAULT_FILE, dest)
    _chmod_600(dest)
    print(f"✓ Exported encrypted vault to {dest}")


def cmd_import(args) -> None:
    """Import credentials from encrypted backup."""
    _refuse_program_whole_vault("import")
    src = Path(args.file)
    if not src.exists():
        print(f"✗ File not found: {src}")
        sys.exit(1)
    key = _get_key()
    # Try to decrypt with our key
    try:
        data = src.read_bytes()
        decrypted = _decrypt(data, key)
        imported = json.loads(decrypted)
    except InvalidToken:
        print(
            "✗ Failed to decrypt: the backup was encrypted with a different key.\n"
            "  You must import into a vault that shares the same encryption key.",
            file=sys.stderr,
        )
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(
            f"✗ Backup file decrypted but contains invalid JSON: {exc}\n"
            f"  The file may be corrupted.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Validate imported structure
    if not isinstance(imported, dict):
        print("✗ Invalid backup format: expected a JSON object.", file=sys.stderr)
        sys.exit(1)
    imported_entries = imported.get("entries")
    if imported_entries is None:
        imported_entries = {}
    if not isinstance(imported_entries, dict):
        print("✗ Invalid backup format: 'entries' must be an object.", file=sys.stderr)
        sys.exit(1)

    # Upgrade imported entries to have entry_type
    for svc, entry in imported_entries.items():
        if isinstance(entry, dict) and "entry_type" not in entry:
            entry["entry_type"] = "credential"

    # Merge with existing vault based on --merge/--overwrite flags
    vault = _load_vault(key) if VAULT_FILE.exists() else {"version": 1, "entries": {}}
    existing = vault.setdefault("entries", {})

    # Default behavior: skip existing entries (safe)
    merge_mode = getattr(args, "merge", False)
    overwrite_mode = getattr(args, "overwrite", False)

    added = 0
    skipped = 0
    updated = 0
    for service, entry in imported_entries.items():
        if service in existing:
            if overwrite_mode:
                existing[service] = entry
                updated += 1
            elif merge_mode:
                # Merge: update only missing fields
                for field, value in entry.items():
                    if field not in existing[service] or not existing[service].get(field):
                        existing[service][field] = value
                updated += 1
            else:
                skipped += 1
        else:
            existing[service] = entry
            added += 1

    _save_vault(vault, key)
    print(f"✓ Imported {added} new + {updated} updated" +
          (f", {skipped} skipped (use --overwrite to replace or --merge to fill blanks)" if skipped else ""))


def cmd_backup(args) -> None:
    """Export all kista data to a JSON backup file (optionally encrypted)."""
    _refuse_program_whole_vault("backup")
    key = _get_key()
    vault = _load_vault(key)

    export_data = {
        "kista_version": __version__,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "platform": f"{platform.system()} {platform.machine()}",
        "vault": vault,
    }

    output_path = Path(args.output) if args.output else Path("kista_backup.json")

    if getattr(args, "encrypt", False):
        # Encrypt the JSON backup with the vault key
        json_data = json.dumps(export_data, indent=2, ensure_ascii=False).encode()
        encrypted = _encrypt(json_data, key)
        output_path = output_path.with_suffix(".json.enc")
        _atomic_write(output_path, encrypted)
        _chmod_600(output_path)
    else:
        # Plain JSON export — plaintext by the caller's explicit
        # choice, but never looser than owner-only on disk (E-095).
        output_path.write_text(json.dumps(export_data, indent=2, ensure_ascii=False))
        _chmod_600(output_path)

    print(f"✓ Backup exported to {output_path}")
    print(f"  Entries: {len(vault.get('entries', {}))}")
    if getattr(args, "encrypt", False):
        print(f"  Encrypted: Yes (using vault key)")
    else:
        print(f"  ⚠ Encrypted: No — backup contains plaintext data!")


def cmd_restore(args) -> None:
    """Restore kista data from a backup JSON file."""
    _refuse_program_whole_vault("restore")
    src = Path(args.file)
    if not src.exists():
        print(f"✗ File not found: {src}")
        sys.exit(1)

    key = _get_key()

    # Determine if the file is encrypted
    try:
        data = src.read_bytes()
        # Try to parse as plain JSON first
        if data[:1] == b"{":
            backup_data = json.loads(data)
        else:
            # Try to decrypt as encrypted backup
            try:
                decrypted = _decrypt(data, key)
                backup_data = json.loads(decrypted)
            except (InvalidToken, json.JSONDecodeError) as exc:
                print(f"✗ Cannot read backup file: {exc}", file=sys.stderr)
                sys.exit(1)
    except json.JSONDecodeError as exc:
        # Try encrypted format
        try:
            decrypted = _decrypt(data, key)
            backup_data = json.loads(decrypted)
        except (InvalidToken, json.JSONDecodeError) as exc2:
            print(f"✗ Cannot read backup file: {exc2}", file=sys.stderr)
            sys.exit(1)

    # Validate backup structure
    if not isinstance(backup_data, dict):
        print("✗ Invalid backup format: expected a JSON object.", file=sys.stderr)
        sys.exit(1)

    imported_vault = backup_data.get("vault")
    if not imported_vault:
        # Maybe the backup is the vault itself (legacy format)
        if "entries" in backup_data:
            imported_vault = backup_data
        else:
            print("✗ No vault data found in backup.", file=sys.stderr)
            sys.exit(1)

    imported_entries = imported_vault.get("entries", {})
    if not isinstance(imported_entries, dict):
        print("✗ Invalid backup: 'entries' must be an object.", file=sys.stderr)
        sys.exit(1)

    # Upgrade entries
    for svc, entry in imported_entries.items():
        if isinstance(entry, dict) and "entry_type" not in entry:
            entry["entry_type"] = "credential"

    # Merge with existing vault
    vault = _load_vault(key)
    existing = vault.setdefault("entries", {})

    overwrite_mode = getattr(args, "overwrite", False)
    merge_mode = getattr(args, "merge", False)

    added = 0
    skipped = 0
    updated = 0
    for service, entry in imported_entries.items():
        if service in existing:
            if overwrite_mode:
                existing[service] = entry
                updated += 1
            elif merge_mode:
                for field, value in entry.items():
                    if field not in existing[service] or not existing[service].get(field):
                        existing[service][field] = value
                updated += 1
            else:
                skipped += 1
        else:
            existing[service] = entry
            added += 1

    _save_vault(vault, key)
    print(f"✓ Restored {added} new + {updated} updated" +
          (f", {skipped} skipped (use --overwrite to replace or --merge to fill blanks)" if skipped else ""))


def cmd_github_backup(args) -> None:
    """Push encrypted backup to a configured GitHub repo."""
    _refuse_program_whole_vault("github-backup")
    config = _load_config()
    repo = getattr(args, "repo", None) or config.get("backup", {}).get("repo")

    if not repo:
        print("✗ No GitHub repo configured. Use 'kista config set backup.repo <url>' or --repo flag.", file=sys.stderr)
        sys.exit(1)

    push = getattr(args, "push", False)

    # Create an encrypted backup
    key = _get_key()
    vault = _load_vault(key)

    export_data = {
        "kista_version": __version__,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "platform": f"{platform.system()} {platform.machine()}",
        "vault": vault,
    }

    json_data = json.dumps(export_data, indent=2, ensure_ascii=False).encode()
    encrypted = _encrypt(json_data, key)

    # Save to temp location
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_dir = VAULT_DIR / "github_tmp"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_file = backup_dir / f"kista_backup_{timestamp}.enc"
    backup_file.write_bytes(encrypted)

    print(f"✓ Encrypted backup created: {backup_file}")
    print(f"  Target repo: {repo}")
    print(f"  Entries: {len(vault.get('entries', {}))}")

    if push:
        # Attempt git push using subprocess
        print("  Pushing to GitHub...")
        try:
            # Initialize or update the repo
            result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode != 0:
                print("✗ GitHub CLI (gh) not authenticated. Run 'gh auth login' first.", file=sys.stderr)
                backup_file.unlink(missing_ok=True)
                sys.exit(1)

            # Clone or update the backup repo
            repo_dir = backup_dir / "repo"
            if repo_dir.exists():
                subprocess.run(["git", "-C", str(repo_dir), "pull"], capture_output=True, timeout=30)
            else:
                subprocess.run(
                    ["git", "clone", repo, str(repo_dir)],
                    capture_output=True, timeout=60,
                )

            # Copy the backup file
            dest_file = repo_dir / f"kista_backups/kista_backup_{timestamp}.enc"
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            import shutil
            shutil.copy2(backup_file, dest_file)

            # Git add, commit, push
            subprocess.run(["git", "-C", str(repo_dir), "add", "."], capture_output=True, timeout=10)
            subprocess.run(
                ["git", "-C", str(repo_dir), "commit", "-m", f"kista backup {timestamp}"],
                capture_output=True, timeout=10,
            )
            subprocess.run(["git", "-C", str(repo_dir), "push"], capture_output=True, timeout=30)

            print("  ✓ Pushed to GitHub successfully!")
        except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
            print(f"✗ GitHub push failed: {exc}", file=sys.stderr)
            print("  You can manually push the backup file.", file=sys.stderr)
    else:
        print("  Use --push to push to GitHub automatically.")
        print(f"  Or manually push: {backup_file}")

    # Cleanup temp
    try:
        backup_file.unlink(missing_ok=True)
    except OSError:
        pass


def cmd_add_soul(args) -> None:
    """Backup SOUL.md and runa-identity.md to the vault."""
    _refuse_program_whole_vault("add-soul")
    key = _get_key()
    vault = _load_vault(key)
    entries = vault.setdefault("entries", {})

    soul_paths = [
        Path.home() / ".hermes" / "SOUL.md",
        Path.home() / ".hermes" / "personality" / "runa-identity.md",
    ]

    added = 0
    for soul_path in soul_paths:
        if soul_path.exists():
            # E-098 (docket 137): the key is lowercased
            # like every other entry's — the mixed-case
            # shape this line used to build made the
            # backup unreachable by get/update/remove.
            service_name = f"soul-backup-{soul_path.stem.lower()}"
            if service_name in entries and not getattr(args, "force", False):
                print(f"  Skipped {service_name} (already exists, use --force to overwrite)")
                continue

            content = soul_path.read_text()
            entry = {
                "service": service_name,
                "entry_type": "markdown",
                "title": soul_path.stem,
                "content": content,
                "category": "soul-backup",
                "tags": ["soul", "backup", "hermes"],
                "source_url": str(soul_path),
                "notes": f"Automatic SOUL.md backup from {soul_path}",
                "created": datetime.now(timezone.utc).isoformat(),
                "updated": datetime.now(timezone.utc).isoformat(),
            }
            # Remove empty fields
            entry = {k: v for k, v in entry.items() if v or k in ("service", "created", "updated", "entry_type")}
            entries[service_name] = entry
            added += 1
            print(f"  ✓ Backed up {soul_path} → {service_name}")
        else:
            print(f"  ⚠ Not found: {soul_path}")

    if added > 0:
        _save_vault(vault, key)
        print(f"✓ SOUL backup complete: {added} file(s) backed up")
        # E-098 (docket 50): backing up another
        # program's own soul files is not one of the
        # toaster-Kista's own acts — it is the other
        # Kista's road, kept working here exactly as
        # it was, and the program says so in words.
        print("  Note: a soul backup is not one of the "
              "toaster-Kista's own kinds (passwords, "
              "tokens, URLs, notes). It belongs to the "
              "other Kista's wider road and is kept "
              "here exactly as given — nothing was "
              "merged or changed.")
    else:
        print("✗ No SOUL files found to backup.")


def cmd_add_cron_backup(args) -> None:
    """Backup current crontab to the vault."""
    _refuse_program_whole_vault("add-cron-backup")
    key = _get_key()
    vault = _load_vault(key)
    entries = vault.setdefault("entries", {})

    # Get current crontab
    try:
        result = subprocess.run(
            ["crontab", "-l"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            print("✗ No crontab found or crontab command not available.", file=sys.stderr)
            sys.exit(1)
        cron_content = result.stdout
    except FileNotFoundError:
        print("✗ crontab command not found on this system.", file=sys.stderr)
        sys.exit(1)

    service_name = "cron-backup"
    if service_name in entries and not getattr(args, "force", False):
        print(f"✗ Entry '{service_name}' already exists. Use --force to overwrite.")
        sys.exit(1)

    entry = {
        "service": service_name,
        "entry_type": "markdown",
        "title": "Crontab Backup",
        "content": cron_content,
        "category": "system-backup",
        "tags": ["cron", "backup", "system"],
        "source_url": "crontab",
        "notes": f"Automatic crontab backup from {platform.node()}",
        "created": datetime.now(timezone.utc).isoformat(),
        "updated": datetime.now(timezone.utc).isoformat(),
    }
    entry = {k: v for k, v in entry.items() if v or k in ("service", "created", "updated", "entry_type")}
    entries[service_name] = entry

    _save_vault(vault, key)
    print(f"✓ Crontab backed up to '{service_name}' ({len(cron_content.splitlines())} lines)")
    # E-098 (docket 50): a crontab is a machine's
    # state, not a credential kind — this backup is
    # the other road's shape (its "states" ambition),
    # kept working here exactly as it was, and the
    # program says so in words.
    print("  Note: a crontab backup is not one of the "
          "toaster-Kista's own kinds (passwords, "
          "tokens, URLs, notes). It belongs to the "
          "other Kista's wider road and is kept "
          "here exactly as given — nothing was "
          "merged or changed.")


def cmd_config(args) -> None:
    """Manage kista configuration settings."""
    _refuse_program_whole_vault("config")
    config = _load_config()

    action = getattr(args, "config_action", None)
    if action == "set":
        key_path = args.config_key
        value = args.config_value
        # Support nested keys like "backup.repo"
        parts = key_path.split(".")
        d = config
        for part in parts[:-1]:
            d = d.setdefault(part, {})
        d[parts[-1]] = value
        _save_config(config)
        print(f"✓ Set {key_path} = {value}")
    elif action == "get":
        key_path = args.config_key
        parts = key_path.split(".")
        d = config
        for part in parts:
            d = d.get(part) if isinstance(d, dict) else None
            if d is None:
                print(f"✗ Config key '{key_path}' not found.")
                return
        print(f"{key_path} = {d}")
    elif action == "list":
        if config:
            print(json.dumps(config, indent=2, ensure_ascii=False))
        else:
            print("No configuration set. Use 'kista config set <key> <value>'.")
    else:
        print("Usage: kista config [set|get|list] [key] [value]")


def _add_type_args(parser, entry_type) -> None:
    """Add type-specific arguments to an argparse subparser."""
    if entry_type == "apikey":
        parser.add_argument("--key", dest="key_arg", help="API key value (required)")
        parser.add_argument("--expires", help="Expiration date/time")
        parser.add_argument("--service-url", dest="service_url", help="Service URL for the API")
        parser.add_argument("--rate-limit", dest="rate_limit", help="Rate limit info")
        parser.add_argument("--scopes", help="Comma-separated permission scopes")

    elif entry_type == "sshkey":
        parser.add_argument("--key-file", help="Path to SSH private key file (required, secure)")
        parser.add_argument("--public-key", dest="public_key", help="Public key content")
        parser.add_argument("--passphrase", help="Key passphrase")
        parser.add_argument("--key-type", dest="key_type", choices=["rsa", "ed25519", "ecdsa"],
                            help="SSH key type")
        parser.add_argument("--host", help="Associated host")

    elif entry_type == "certificate":
        parser.add_argument("--cert-file", help="Path to certificate file (required, secure)")
        parser.add_argument("--key-file", help="Path to private key file for the certificate")
        parser.add_argument("--domain", help="Certificate domain")
        parser.add_argument("--issuer", help="Certificate issuer")
        parser.add_argument("--expires", dest="expires_field", help="Expiration date")
        parser.add_argument("--chain", help="Certificate chain")

    elif entry_type == "note":
        parser.add_argument("--content", help="Note content (required)")
        parser.add_argument("--category", help="Note category")

    elif entry_type == "totp":
        parser.add_argument("--secret", help="TOTP secret (required)")
        parser.add_argument("--digits", type=int, default=None, help="Number of digits (default: 6)")
        parser.add_argument("--period", type=int, default=None, help="Time period in seconds (default: 30)")
        parser.add_argument("--algorithm", help="Algorithm (default: SHA1)")
        parser.add_argument("--issuer", help="TOTP issuer")

    elif entry_type == "license":
        parser.add_argument("--key", dest="key_arg", help="License key (required)")
        parser.add_argument("--product", help="Product name")
        parser.add_argument("--seats", help="Number of seats")
        parser.add_argument("--expires", dest="expires_field", help="Expiration date")
        parser.add_argument("--order-id", dest="order_id", help="Order ID")

    elif entry_type == "identity":
        parser.add_argument("--full-name", dest="full_name", help="Full legal name")
        parser.add_argument("--birth-date", dest="birth_date", help="Date of birth")
        parser.add_argument("--id-number", dest="id_number", help="ID number")
        parser.add_argument("--id-type", dest="id_type", help="ID type (passport, driver_license, etc.)")
        parser.add_argument("--address", help="Address")
        parser.add_argument("--phone", dest="phone_arg", help="Phone number")
        parser.add_argument("--national-id", dest="national_id", help="National ID number")

    elif entry_type == "url":
        # E-098 (docket 137): this branch did not
        # exist — the add-url shortcut the program's
        # own usage text advertises had no parser at
        # all, so the branch is built here with the
        # shortcut loop and the inference map below.
        parser.add_argument("--url", required=True, help="URL (required)")
        parser.add_argument("--title", dest="title_arg", help="Page/site title")
        parser.add_argument("--description", help="Description")

    elif entry_type == "astrology":
        parser.add_argument("--sign", required=True, help="Zodiac sign (required)")
        parser.add_argument("--date", dest="astro_date", help="Date for the reading")
        parser.add_argument("--sun-position", dest="sun_position", help="Sun position (sign/degree)")
        parser.add_argument("--moon-position", dest="moon_position", help="Moon position (sign/degree)")
        parser.add_argument("--mercury-position", dest="mercury_position", help="Mercury position")
        parser.add_argument("--venus-position", dest="venus_position", help="Venus position")
        parser.add_argument("--mars-position", dest="mars_position", help="Mars position")
        parser.add_argument("--jupiter-position", dest="jupiter_position", help="Jupiter position")
        parser.add_argument("--saturn-position", dest="saturn_position", help="Saturn position")
        parser.add_argument("--ascendant", help="Ascendant sign")
        parser.add_argument("--mc", help="Midheaven (MC) sign")
        parser.add_argument("--aspects", help="Aspects as JSON array or comma-separated")

    elif entry_type == "character-sheet":
        parser.add_argument("--name", dest="char_name", required=True, help="Character name (required)")
        parser.add_argument("--race", help="Character race")
        parser.add_argument("--class", dest="char_class", help="Character class")
        parser.add_argument("--level", type=int, default=None, help="Character level")
        parser.add_argument("--background", help="Character background")
        parser.add_argument("--alignment", help="Character alignment")
        parser.add_argument("--str", dest="str_score", type=int, default=None, help="Strength score")
        parser.add_argument("--dex", dest="dex_score", type=int, default=None, help="Dexterity score")
        parser.add_argument("--con", dest="con_score", type=int, default=None, help="Constitution score")
        parser.add_argument("--int", dest="int_score", type=int, default=None, help="Intelligence score")
        parser.add_argument("--wis", dest="wis_score", type=int, default=None, help="Wisdom score")
        parser.add_argument("--cha", dest="cha_score", type=int, default=None, help="Charisma score")
        parser.add_argument("--ac", type=int, default=None, help="Armor Class")
        parser.add_argument("--hp", type=int, default=None, help="Hit Points")
        parser.add_argument("--speed", type=int, default=None, help="Speed")
        parser.add_argument("--prof-bonus", dest="prof_bonus", type=int, default=None, help="Proficiency bonus")
        parser.add_argument("--skills", help="Skills (JSON array or comma-separated)")
        parser.add_argument("--features", help="Features (JSON array or comma-separated)")
        parser.add_argument("--equipment", help="Equipment (JSON array or comma-separated)")
        parser.add_argument("--spells", help="Spells (JSON array or comma-separated)")
        parser.add_argument("--backstory", help="Character backstory")

    elif entry_type == "rune-reading":
        parser.add_argument("--spread-type", dest="spread_type", required=True, help="Type of spread (e.g., single, three-rune, celtic-cross)")
        parser.add_argument("--runes-drawn", dest="runes_drawn", help="Runes drawn (JSON array or comma-separated)")
        parser.add_argument("--positions", help="Rune positions (JSON array or comma-separated)")
        parser.add_argument("--interpretation", help="Interpretation of the reading")
        parser.add_argument("--question", help="Question asked before drawing")
        parser.add_argument("--date-drawn", dest="date_drawn", help="Date drawing was done")

    elif entry_type == "tarot-reading":
        parser.add_argument("--spread-type", dest="spread_type", required=True, help="Type of spread (e.g., three-card, celtic-cross)")
        parser.add_argument("--cards-drawn", dest="cards_drawn", help="Cards drawn (JSON array or comma-separated)")
        parser.add_argument("--positions", help="Card positions (JSON array or comma-separated)")
        parser.add_argument("--interpretation", help="Interpretation of the reading")
        parser.add_argument("--question", help="Question asked before the reading")
        parser.add_argument("--date-drawn", dest="date_drawn", help="Date reading was done")

    elif entry_type == "markdown":
        parser.add_argument("--title", dest="md_title", required=True, help="Document title (required)")
        # E-098 (docket 137): the shortcut had no flag
        # that could carry the document's content at
        # all (--md-source never reached the entry), so
        # add-markdown could never satisfy the type's
        # required content field. --content now lands
        # on md_content, which cmd_add reads.
        parser.add_argument("--content", dest="md_content", help="Document content (required)")
        parser.add_argument("--md-source", help="Source content (markdown)")
        parser.add_argument("--source-url", dest="source_url", help="Source URL")


def main():
    parser = argparse.ArgumentParser(
        description="Kista — Self-owned encrypted vault (Old Norse: strongbox/chest)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    sub = parser.add_subparsers(dest="command")

    # init
    sub.add_parser("init", help="Initialize the vault")

    # repair
    sub.add_parser("repair", help="Repair corrupted vault from backup")

    # passphrase (E-096)
    sub.add_parser("set-passphrase", help="Set or change the vault passphrase — a copied folder then opens nothing without it")
    sub.add_parser("remove-passphrase", help="Remove the vault passphrase (the consequence is stated before it happens)")

    # add (general, with --type)
    p_add = sub.add_parser("add", help="Add a new entry")
    p_add.add_argument("service", help="Service name (e.g., 'email-provider', 'streaming-service')")
    p_add.add_argument("--type", dest="entry_type", default="credential",
                       choices=list(ENTRY_TYPE_SCHEMAS.keys()),
                       help="Entry type (default: credential)")
    p_add.add_argument("--username", "-u", help="Username")
    p_add.add_argument("--password", "-p", help="Password (discouraged: visible in process list and shell history — prefer --password-file or --password-env)")
    p_add.add_argument("--password-file", help="Read password from file (secure)")
    p_add.add_argument("--password-env", help="Read password from environment variable (secure)")
    p_add.add_argument("--email", "-e", help="Email address")
    p_add.add_argument("--url", help="Service URL")
    p_add.add_argument("--notes", "-n", help="Additional notes")
    p_add.add_argument("--tags", "-t", help="Comma-separated tags")
    p_add.add_argument("--program", help="The program this entry belongs to (E-097): only that program — and you, the owner — can reach it afterwards")
    p_add.add_argument("--force", "-f", action="store_true", help="Overwrite if exists")
    # Type-specific args for 'add' (merged from all types)
    p_add.add_argument("--key", dest="key_arg", help="API key / License key")
    p_add.add_argument("--key-file", help="Path to private key file (sshkey/certificate)")
    p_add.add_argument("--cert-file", help="Path to certificate file")
    p_add.add_argument("--expires", help="Expiration date")
    p_add.add_argument("--service-url", dest="service_url", help="Service URL (apikey)")
    p_add.add_argument("--rate-limit", dest="rate_limit", help="Rate limit (apikey)")
    p_add.add_argument("--scopes", help="Comma-separated scopes (apikey)")
    p_add.add_argument("--public-key", dest="public_key", help="Public key content (sshkey)")
    p_add.add_argument("--passphrase", help="Passphrase (sshkey)")
    p_add.add_argument("--key-type", dest="key_type", choices=["rsa", "ed25519", "ecdsa"],
                        help="SSH key type")
    p_add.add_argument("--host", help="Associated host (sshkey)")
    p_add.add_argument("--domain", help="Domain (certificate)")
    p_add.add_argument("--issuer", help="Issuer (certificate/totp)")
    p_add.add_argument("--chain", help="Certificate chain (certificate)")
    p_add.add_argument("--content", help="Content (note/markdown)")
    p_add.add_argument("--category", help="Category (note)")
    p_add.add_argument("--secret", help="Secret (totp)")
    p_add.add_argument("--digits", type=int, default=None, help="Digits (totp, default: 6)")
    p_add.add_argument("--period", type=int, default=None, help="Period in seconds (totp, default: 30)")
    p_add.add_argument("--algorithm", help="Algorithm (totp, default: SHA1)")
    p_add.add_argument("--product", help="Product name (license)")
    p_add.add_argument("--seats", help="Number of seats (license)")
    p_add.add_argument("--order-id", dest="order_id", help="Order ID (license)")
    p_add.add_argument("--full-name", dest="full_name", help="Full name (identity)")
    p_add.add_argument("--birth-date", dest="birth_date", help="Birth date (identity)")
    p_add.add_argument("--id-number", dest="id_number", help="ID number (identity)")
    p_add.add_argument("--id-type", dest="id_type", help="ID type (identity)")
    p_add.add_argument("--address", help="Address (identity)")
    p_add.add_argument("--phone", dest="phone_arg", help="Phone (identity)")
    p_add.add_argument("--national-id", dest="national_id", help="National ID (identity)")
    # New v2.0 type args for generic add
    p_add.add_argument("--sign", help="Zodiac sign (astrology)")
    p_add.add_argument("--title", help="Title (url/markdown)")
    p_add.add_argument("--description", help="Description (url)")
    # v2.0 type fields on the general add road (E-098,
    # docket 137): before this fix the general parser
    # defined none of these, so `add --type
    # character-sheet / rune-reading / tarot-reading`
    # could never satisfy those types' required fields
    # (name / spread type), and an astrology entry
    # could carry nothing beyond its sign. The flags
    # mirror the shortcuts' _add_type_args dests
    # exactly, so both roads build the same entry.
    p_add.add_argument("--date", dest="astro_date", help="Date for the reading (astrology)")
    p_add.add_argument("--sun-position", dest="sun_position", help="Sun position (astrology)")
    p_add.add_argument("--moon-position", dest="moon_position", help="Moon position (astrology)")
    p_add.add_argument("--mercury-position", dest="mercury_position", help="Mercury position (astrology)")
    p_add.add_argument("--venus-position", dest="venus_position", help="Venus position (astrology)")
    p_add.add_argument("--mars-position", dest="mars_position", help="Mars position (astrology)")
    p_add.add_argument("--jupiter-position", dest="jupiter_position", help="Jupiter position (astrology)")
    p_add.add_argument("--saturn-position", dest="saturn_position", help="Saturn position (astrology)")
    p_add.add_argument("--ascendant", help="Ascendant sign (astrology)")
    p_add.add_argument("--mc", help="Midheaven (MC) sign (astrology)")
    p_add.add_argument("--aspects", help="Aspects as JSON array or comma-separated (astrology)")
    p_add.add_argument("--name", dest="char_name", help="Character name (character-sheet)")
    p_add.add_argument("--race", help="Character race (character-sheet)")
    p_add.add_argument("--class", dest="char_class", help="Character class (character-sheet)")
    p_add.add_argument("--level", type=int, default=None, help="Character level (character-sheet)")
    p_add.add_argument("--background", help="Character background (character-sheet)")
    p_add.add_argument("--alignment", help="Character alignment (character-sheet)")
    p_add.add_argument("--str", dest="str_score", type=int, default=None, help="Strength score (character-sheet)")
    p_add.add_argument("--dex", dest="dex_score", type=int, default=None, help="Dexterity score (character-sheet)")
    p_add.add_argument("--con", dest="con_score", type=int, default=None, help="Constitution score (character-sheet)")
    p_add.add_argument("--int", dest="int_score", type=int, default=None, help="Intelligence score (character-sheet)")
    p_add.add_argument("--wis", dest="wis_score", type=int, default=None, help="Wisdom score (character-sheet)")
    p_add.add_argument("--cha", dest="cha_score", type=int, default=None, help="Charisma score (character-sheet)")
    p_add.add_argument("--ac", type=int, default=None, help="Armor Class (character-sheet)")
    p_add.add_argument("--hp", type=int, default=None, help="Hit Points (character-sheet)")
    p_add.add_argument("--speed", type=int, default=None, help="Speed (character-sheet)")
    p_add.add_argument("--prof-bonus", dest="prof_bonus", type=int, default=None, help="Proficiency bonus (character-sheet)")
    p_add.add_argument("--skills", help="Skills (character-sheet, JSON or comma-separated)")
    p_add.add_argument("--features", help="Features (character-sheet, JSON or comma-separated)")
    p_add.add_argument("--equipment", help="Equipment (character-sheet, JSON or comma-separated)")
    p_add.add_argument("--spells", help="Spells (character-sheet, JSON or comma-separated)")
    p_add.add_argument("--backstory", help="Character backstory (character-sheet)")
    p_add.add_argument("--spread-type", dest="spread_type", help="Spread type (rune-reading/tarot-reading)")
    p_add.add_argument("--runes-drawn", dest="runes_drawn", help="Runes drawn (rune-reading, JSON or comma-separated)")
    p_add.add_argument("--cards-drawn", dest="cards_drawn", help="Cards drawn (tarot-reading, JSON or comma-separated)")
    p_add.add_argument("--positions", help="Positions (rune-reading/tarot-reading, JSON or comma-separated)")
    p_add.add_argument("--interpretation", help="Interpretation (rune-reading/tarot-reading)")
    p_add.add_argument("--question", help="Question asked before the reading (rune-reading/tarot-reading)")
    p_add.add_argument("--date-drawn", dest="date_drawn", help="Date the reading was done (rune-reading/tarot-reading)")

    # === Convenience shortcuts for add (each auto-sets --type) ===
    for et, help_text in [
        ("apikey", "Add an API key entry"),
        ("sshkey", "Add an SSH key entry"),
        ("certificate", "Add a certificate entry"),
        ("note", "Add a note entry"),
        ("totp", "Add a TOTP entry"),
        ("license", "Add a license entry"),
        ("identity", "Add an identity entry"),
        # E-098 (docket 137): add-url restored — the
        # usage text advertised it since the import,
        # but no parser ever stood behind it.
        ("url", "Add a URL entry"),
        ("astrology", "Add an astrology entry"),
        ("character-sheet", "Add a D&D character sheet entry"),
        ("rune-reading", "Add a rune reading entry"),
        ("tarot-reading", "Add a tarot reading entry"),
        ("markdown", "Add a markdown document entry"),
    ]:
        cmd = f"add-{et}"
        p = sub.add_parser(cmd, help=help_text)
        p.add_argument("service", help="Service/entry name")
        _add_type_args(p, et)
        # Common args for shortcuts
        p.add_argument("--tags", "-t", help="Comma-separated tags")
        p.add_argument("--notes", "-n", help="Additional notes")
        p.add_argument("--program", help="The program this entry belongs to (E-097)")
        p.add_argument("--force", "-f", action="store_true", help="Overwrite if exists")

    # add-person (enhanced identity)
    p_person = sub.add_parser("add-person", help="Add a person/identity entry (enhanced)")
    p_person.add_argument("service", help="Person identifier/label")
    _add_type_args(p_person, "identity")
    p_person.add_argument("--tags", "-t", help="Comma-separated tags")
    p_person.add_argument("--notes", "-n", help="Additional notes")
    p_person.add_argument("--program", help="The program this entry belongs to (E-097)")
    p_person.add_argument("--force", "-f", action="store_true", help="Overwrite if exists")
    # Enhanced person fields
    p_person.add_argument("--email", "-e", help="Email address")
    p_person.add_argument("--url", help="Personal website/URL")

    # add-soul
    p_soul = sub.add_parser("add-soul", help="Backup SOUL.md and runa-identity.md to vault")
    p_soul.add_argument("--force", "-f", action="store_true", help="Overwrite existing backup")

    # add-cron-backup
    p_cron = sub.add_parser("add-cron-backup", help="Backup current crontab to vault")
    p_cron.add_argument("--force", "-f", action="store_true", help="Overwrite existing backup")

    # get
    p_get = sub.add_parser("get", help="Get entry details")
    p_get.add_argument("service", help="Service name")

    # list
    p_list = sub.add_parser("list", help="List all entries")
    p_list.add_argument("--tags", "-t", help="Filter by tag")

    # update
    p_upd = sub.add_parser("update", help="Update entry fields")
    p_upd.add_argument("service", help="Service name")
    # Common update fields
    p_upd.add_argument("--username", "-u", help="New username")
    p_upd.add_argument("--password", "-p", help="New password (discouraged: visible in process list and shell history)")
    p_upd.add_argument("--password-file", help="Read password from file (secure)")
    p_upd.add_argument("--password-env", help="Read password from environment variable (secure)")
    p_upd.add_argument("--email", "-e", help="New email")
    p_upd.add_argument("--url", help="New URL")
    p_upd.add_argument("--notes", "-n", help="New notes")
    p_upd.add_argument("--tags", "-t", help="New comma-separated tags")
    p_upd.add_argument("--program", help="Give this entry to a program (owner only, E-097)")
    p_upd.add_argument("--unassign-program", action="store_true", help="Make this entry the owner's own again (owner only, E-097)")
    # Type-specific update fields
    p_upd.add_argument("--key", dest="key_arg", help="API/License key")
    p_upd.add_argument("--key-file", help="Path to private key file (sshkey/certificate)")
    p_upd.add_argument("--cert-file", help="Path to certificate file")
    p_upd.add_argument("--expires", help="Expiration date")
    p_upd.add_argument("--service-url", dest="service_url", help="Service URL (apikey)")
    p_upd.add_argument("--rate-limit", dest="rate_limit", help="Rate limit (apikey)")
    p_upd.add_argument("--scopes", help="Scopes (apikey)")
    p_upd.add_argument("--public-key", dest="public_key", help="Public key (sshkey)")
    p_upd.add_argument("--passphrase", help="Passphrase (sshkey)")
    p_upd.add_argument("--key-type", dest="key_type", choices=["rsa", "ed25519", "ecdsa"],
                        help="SSH key type")
    p_upd.add_argument("--host", help="Host (sshkey)")
    p_upd.add_argument("--domain", help="Domain (certificate)")
    p_upd.add_argument("--issuer", help="Issuer (certificate/totp)")
    p_upd.add_argument("--chain", help="Certificate chain (certificate)")
    p_upd.add_argument("--content", help="Note content (note)")
    p_upd.add_argument("--category", help="Category (note)")
    p_upd.add_argument("--secret", help="Secret (totp)")
    p_upd.add_argument("--digits", type=int, default=None, help="Digits (totp)")
    p_upd.add_argument("--period", type=int, default=None, help="Period (totp)")
    p_upd.add_argument("--algorithm", help="Algorithm (totp)")
    p_upd.add_argument("--product", help="Product (license)")
    p_upd.add_argument("--seats", help="Seats (license)")
    p_upd.add_argument("--order-id", dest="order_id", help="Order ID (license)")
    p_upd.add_argument("--full-name", dest="full_name", help="Full name (identity)")
    p_upd.add_argument("--birth-date", dest="birth_date", help="Birth date (identity)")
    p_upd.add_argument("--id-number", dest="id_number", help="ID number (identity)")
    p_upd.add_argument("--id-type", dest="id_type", help="ID type (identity)")
    p_upd.add_argument("--address", help="Address (identity)")
    p_upd.add_argument("--phone", dest="phone_arg", help="Phone (identity)")
    p_upd.add_argument("--national-id", dest="national_id", help="National ID (identity)")
    # New v2.0 update fields
    p_upd.add_argument("--sign", help="Zodiac sign (astrology)")
    p_upd.add_argument("--astro-date", dest="astro_date", help="Date (astrology)")
    p_upd.add_argument("--sun-position", dest="sun_position", help="Sun position (astrology)")
    p_upd.add_argument("--moon-position", dest="moon_position", help="Moon position (astrology)")
    p_upd.add_argument("--mercury-position", dest="mercury_position", help="Mercury position (astrology)")
    p_upd.add_argument("--venus-position", dest="venus_position", help="Venus position (astrology)")
    p_upd.add_argument("--mars-position", dest="mars_position", help="Mars position (astrology)")
    p_upd.add_argument("--jupiter-position", dest="jupiter_position", help="Jupiter position (astrology)")
    p_upd.add_argument("--saturn-position", dest="saturn_position", help="Saturn position (astrology)")
    p_upd.add_argument("--ascendant", help="Ascendant sign (astrology)")
    p_upd.add_argument("--mc", help="Midheaven (astrology)")
    p_upd.add_argument("--aspects", help="Aspects (astrology, JSON)")
    p_upd.add_argument("--char-name", dest="char_name", help="Character name (character-sheet)")
    p_upd.add_argument("--race", help="Race (character-sheet)")
    p_upd.add_argument("--char-class", dest="char_class", help="Class (character-sheet)")
    p_upd.add_argument("--level", type=int, default=None, help="Level (character-sheet)")
    p_upd.add_argument("--background", help="Background (character-sheet)")
    p_upd.add_argument("--alignment", help="Alignment (character-sheet)")
    p_upd.add_argument("--str-score", dest="str_score", type=int, default=None, help="STR (character-sheet)")
    p_upd.add_argument("--dex-score", dest="dex_score", type=int, default=None, help="DEX (character-sheet)")
    p_upd.add_argument("--con-score", dest="con_score", type=int, default=None, help="CON (character-sheet)")
    p_upd.add_argument("--int-score", dest="int_score", type=int, default=None, help="INT (character-sheet)")
    p_upd.add_argument("--wis-score", dest="wis_score", type=int, default=None, help="WIS (character-sheet)")
    p_upd.add_argument("--cha-score", dest="cha_score", type=int, default=None, help="CHA (character-sheet)")
    p_upd.add_argument("--ac", type=int, default=None, help="AC (character-sheet)")
    p_upd.add_argument("--hp", type=int, default=None, help="HP (character-sheet)")
    p_upd.add_argument("--speed", type=int, default=None, help="Speed (character-sheet)")
    p_upd.add_argument("--prof-bonus", dest="prof_bonus", type=int, default=None, help="Proficiency bonus (character-sheet)")
    p_upd.add_argument("--skills", help="Skills (character-sheet, JSON)")
    p_upd.add_argument("--features", help="Features (character-sheet, JSON)")
    p_upd.add_argument("--equipment", help="Equipment (character-sheet, JSON)")
    p_upd.add_argument("--spells", help="Spells (character-sheet, JSON)")
    p_upd.add_argument("--backstory", help="Backstory (character-sheet)")
    p_upd.add_argument("--spread-type", dest="spread_type", help="Spread type (rune/tarot)")
    p_upd.add_argument("--runes-drawn", help="Runes drawn (rune-reading, JSON)")
    p_upd.add_argument("--cards-drawn", help="Cards drawn (tarot-reading, JSON)")
    p_upd.add_argument("--positions", help="Positions (rune/tarot, JSON)")
    p_upd.add_argument("--interpretation", help="Interpretation (rune/tarot/astrology)")
    p_upd.add_argument("--question", help="Question (rune/tarot)")
    p_upd.add_argument("--date-drawn", dest="date_drawn", help="Date drawn (rune/tarot)")
    p_upd.add_argument("--md-title", dest="md_title", help="Title (markdown)")
    p_upd.add_argument("--md-content", dest="md_content", help="Content (markdown)")
    p_upd.add_argument("--md-category", dest="md_category", help="Category (markdown)")
    p_upd.add_argument("--md-tags", dest="md_tags", help="Tags (markdown, JSON)")
    p_upd.add_argument("--source-url", dest="source_url", help="Source URL (markdown)")
    # Special: for some types, --title and --description are shared
    p_upd.add_argument("--title", help="Title (url)")
    p_upd.add_argument("--description", help="Description (url)")

    # remove
    p_rm = sub.add_parser("remove", help="Remove an entry")
    p_rm.add_argument("service", help="Service name")

    # check
    p_chk = sub.add_parser("check", help="Check entry status")
    p_chk.add_argument("service", help="Service name")

    # search
    p_search = sub.add_parser("search", help="Fuzzy search across services and fields, with optional date filtering")
    p_search.add_argument("query", nargs="?", default=None, help="Search term (optional with date flags)")
    p_search.add_argument("--date", "-d", dest="date", help="Find entries created on this date (YYYY-MM-DD)")
    p_search.add_argument("--from", dest="from_date", help="Entries created on or after this date/datetime")
    p_search.add_argument("--to", dest="to_date", help="Entries created on or before this date/datetime")
    p_search.add_argument("--after", help="Entries created after this datetime")
    p_search.add_argument("--before", help="Entries created before this datetime")

    # generate-password
    p_gen = sub.add_parser("generate-password", help="Generate a random password")
    p_gen.add_argument("--length", "-l", type=int, default=20, help="Password length (default: 20)")

    # status
    sub.add_parser("status", help="Show vault status")

    # export (legacy)
    p_exp = sub.add_parser("export", help="Export encrypted backup")
    p_exp.add_argument("--output", "-o", help="Output file path")

    # import (legacy)
    p_imp = sub.add_parser("import", help="Import from encrypted backup")
    p_imp.add_argument("file", help="Backup file path")
    imp_mutex = p_imp.add_mutually_exclusive_group()
    imp_mutex.add_argument("--merge", action="store_true",
                           help="Merge: fill in blank fields for existing entries")
    imp_mutex.add_argument("--overwrite", action="store_true",
                           help="Overwrite: replace existing entries with imported versions")

    # backup (new v2.0)
    p_backup = sub.add_parser("backup", help="Export vault data to JSON backup (optionally encrypted)")
    p_backup.add_argument("--output", "-o", help="Output file path (default: kista_backup.json)")
    p_backup.add_argument("--encrypt", action="store_true", help="Encrypt the backup with vault key")

    # restore (new v2.0)
    p_restore = sub.add_parser("restore", help="Restore vault data from a backup JSON file")
    p_restore.add_argument("file", help="Backup file path")
    p_restore.add_argument("--merge", action="store_true", help="Merge: fill in blank fields")
    p_restore.add_argument("--overwrite", action="store_true", help="Overwrite existing entries")

    # github-backup (new v2.0)
    p_gh = sub.add_parser("github-backup", help="Push encrypted backup to GitHub repository")
    p_gh.add_argument("--repo", help="GitHub repository URL (or use config)")
    p_gh.add_argument("--push", action="store_true", help="Automatically push to GitHub")

    # config (new v2.0)
    p_config = sub.add_parser("config", help="Manage kista configuration")
    config_sub = p_config.add_subparsers(dest="config_action")
    p_config_set = config_sub.add_parser("set", help="Set a configuration value")
    p_config_set.add_argument("config_key", help="Configuration key (e.g., backup.repo)")
    p_config_set.add_argument("config_value", help="Configuration value")
    p_config_get = config_sub.add_parser("get", help="Get a configuration value")
    p_config_get.add_argument("config_key", help="Configuration key")
    config_sub.add_parser("list", help="List all configuration values")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Map shortcut commands to 'add' with entry_type
    TYPE_SHORTCUTS = {
        "add-apikey": "add",
        "add-sshkey": "add",
        "add-certificate": "add",
        "add-note": "add",
        "add-totp": "add",
        "add-license": "add",
        "add-identity": "add",
        "add-url": "add",
        "add-astrology": "add",
        "add-character-sheet": "add",
        "add-rune-reading": "add",
        "add-tarot-reading": "add",
        "add-markdown": "add",
        "add-person": "add",
    }
    TYPE_MAP = {
        "add-apikey": "apikey",
        "add-sshkey": "sshkey",
        "add-certificate": "certificate",
        "add-note": "note",
        "add-totp": "totp",
        "add-license": "license",
        "add-identity": "identity",
        "add-url": "url",
        "add-astrology": "astrology",
        "add-character-sheet": "character-sheet",
        "add-rune-reading": "rune-reading",
        "add-tarot-reading": "tarot-reading",
        "add-markdown": "markdown",
        "add-person": "identity",
    }

    command = args.command
    if command in TYPE_SHORTCUTS:
        command = TYPE_SHORTCUTS[command]
        args.entry_type = TYPE_MAP[args.command]

    commands = {
        "init": cmd_init,
        "set-passphrase": cmd_set_passphrase,
        "remove-passphrase": cmd_remove_passphrase,
        "add": cmd_add,
        "get": cmd_get,
        "list": cmd_list,
        "update": cmd_update,
        "remove": cmd_remove,
        "check": cmd_check,
        "search": cmd_search,
        "generate-password": cmd_generate_password,
        "status": cmd_status,
        "export": cmd_export,
        "import": cmd_import,
        "repair": cmd_repair,
        "backup": cmd_backup,
        "restore": cmd_restore,
        "github-backup": cmd_github_backup,
        "add-soul": cmd_add_soul,
        "add-cron-backup": cmd_add_cron_backup,
        "config": cmd_config,
    }

    # Handle special commands
    if command in commands:
        commands[command](args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()