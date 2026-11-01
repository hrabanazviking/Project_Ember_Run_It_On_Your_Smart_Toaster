"""E-098 — Entry kinds: the toaster set.

Pins ``docs/architecture/E-098_ENTRY_KINDS.md``:

* the toaster set is passwords, tokens, URLs,
  notes — ``credential``, ``apikey``, ``url``,
  ``note`` — standing in the code as
  ``TOASTER_ENTRY_TYPES``;
* five credential-family kinds are KEPT (totp,
  license, sshkey, certificate, identity): in the
  program, working, unpromised — kept because
  removing a kind strands its entries;
* five kinds belong to the other road (astrology,
  character-sheet, rune-reading, tarot-reading,
  markdown): the ai-folder Kista's wider ambitions
  (states, prompts, habits) recorded as its road,
  not silently merged — a NEW entry of one is
  announced in words at the moment it is added and
  kept exactly as given, while custody of existing
  entries (get/list/update/remove) stays silent;
* docket 50 is CLOSED: add-soul and
  add-cron-backup are the other road's and announce
  themselves; github-backup is a backup road,
  E-101's, not an entry kind;
* docket 137 is CLOSED in scope: the dead add
  roads are repaired — every kind adds by its
  general road and its shortcut road — and the
  advertised-but-absent add-url shortcut is built,
  taking the surface 34 -> 35 subcommands (E-094's
  battery re-pinned consciously at this slice).

The probes never touch a real vault home: each
runs with a scratch home, the member directory on
its path, and the user site-packages that carry
the member's one dependency — the custody
discipline the campaign works under. Synthetic
entries only; the soul and crontab probes run
against synthetic files in the scratch home and a
synthetic crontab stand-in on the probe's PATH.
"""

from __future__ import annotations

import ast
import importlib.util
import os
import site
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "docs" / "architecture" / "E-098_ENTRY_KINDS.md"
KISTA = REPO / "kista"
CREDSTORE = KISTA / "scripts" / "credstore.py"

TOASTER = {"credential", "apikey", "url", "note"}
KEPT = {"totp", "license", "sshkey", "certificate",
        "identity"}
OTHER_ROAD = {"astrology", "character-sheet",
              "rune-reading", "tarot-reading", "markdown"}
NOTICE = "not one of the toaster-Kista's own kinds"


def _source() -> str:
    return CREDSTORE.read_text(encoding="utf-8")


# ── The slice record, on file ───────────────────────────


def test_doc_records_entry_kinds():
    text = DOC.read_text(encoding="utf-8").lower()
    for needle in ("in plain words", "toaster set",
                   "passwords, tokens, urls, notes",
                   "not silently merged", "states, prompts, habits",
                   "docket 50", "closed", "docket 137",
                   "kept here exactly as given",
                   "github-backup", "e-099", "e-100",
                   "e-101", "e-104", "add-url",
                   "34 → 35"):
        assert needle in text, needle


# ── The partition is the code's partition ───────────────


def _named_sets() -> dict[str, set]:
    tree = ast.parse(_source())
    found: dict[str, set] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            name = getattr(target, "id", "")
            if name == "ENTRY_TYPE_SCHEMAS":
                found[name] = {k.value for k in node.value.keys}
            elif name in ("TOASTER_ENTRY_TYPES",
                          "KEPT_ENTRY_TYPES",
                          "OTHER_ROAD_ENTRY_TYPES"):
                call = node.value
                literal = ast.literal_eval(call.args[0])
                found[name] = set(literal)
    return found


def test_partition_is_exact_and_complete():
    sets = _named_sets()
    schemas = sets["ENTRY_TYPE_SCHEMAS"]
    assert sets["TOASTER_ENTRY_TYPES"] == TOASTER
    assert sets["KEPT_ENTRY_TYPES"] == KEPT
    assert sets["OTHER_ROAD_ENTRY_TYPES"] == OTHER_ROAD
    three = (sets["TOASTER_ENTRY_TYPES"]
             | sets["KEPT_ENTRY_TYPES"]
             | sets["OTHER_ROAD_ENTRY_TYPES"])
    # Exact partition: together they are all 14 kinds,
    # and no kind stands in two sets at once.
    assert three == schemas and len(schemas) == 14
    assert len(TOASTER) + len(KEPT) + len(OTHER_ROAD) == 14


def test_notice_shape_in_code():
    src = _source()
    assert "def _note_other_road_kind" in src
    assert "entry_type in OTHER_ROAD_ENTRY_TYPES" in src
    assert "a soul backup is not one of the" in src
    assert "a crontab backup is not one of the" in src


def test_surface_is_thirty_five_with_add_url_restored():
    src = _source()
    # add-url stands in all three shortcut maps and
    # in the parser loop (docket 137's full shape).
    assert '"add-url": "url"' in src
    assert '"add-url": "add"' in src
    assert '("url", "Add a URL entry")' in src
    assert 'elif entry_type == "url":' in src


# ── Probes against a scratch vault ──────────────────────


def _run(tmp_path: Path, vault: Path, *argv: str,
         program: str | None = None,
         extra_env: dict | None = None,
         check: bool = True) -> subprocess.CompletedProcess:
    if importlib.util.find_spec("cryptography") is None:
        import pytest
        pytest.skip("cryptography absent in this environment")
    home = tmp_path / "home"
    home.mkdir(exist_ok=True)
    env = dict(os.environ)
    env["HOME"] = str(home)
    env["KISTA_DIR"] = str(vault)
    env.pop("KISTA_PROGRAM", None)
    env.pop("KISTA_PASSPHRASE", None)
    if program is not None:
        env["KISTA_PROGRAM"] = program
    if extra_env:
        env.update(extra_env)
    parts = [str(KISTA), site.getusersitepackages(),
             env.get("PYTHONPATH", "")]
    env["PYTHONPATH"] = os.pathsep.join(p for p in parts if p)
    return subprocess.run(
        [sys.executable, str(CREDSTORE), *argv],
        capture_output=True, text=True, env=env, check=check,
        stdin=subprocess.DEVNULL)


def _file(tmp_path: Path, name: str, value: str) -> str:
    f = tmp_path / name
    f.write_text(value)
    return str(f)


def _vault(tmp_path: Path) -> Path:
    vault = tmp_path / "vault"
    _run(tmp_path, vault, "init")
    return vault


def test_probe_toaster_kinds_add_in_silence(tmp_path):
    vault = _vault(tmp_path)
    pw = _file(tmp_path, "pw.txt", "synthetic-pw")
    runs = [
        ("add", "site", "--username", "u",
         "--password-file", pw),
        ("add", "key", "--type", "apikey",
         "--key", "synthetic-token"),
        ("add", "link", "--type", "url",
         "--url", "https://example.com",
         "--title", "Example"),
        ("add", "memo", "--type", "note",
         "--content", "synthetic note body"),
        ("add-url", "shortcut-link",
         "--url", "https://example.org"),
    ]
    for argv in runs:
        out = _run(tmp_path, vault, *argv).stdout
        assert NOTICE not in out, argv
    assert "synthetic-pw" in _run(
        tmp_path, vault, "get", "site").stdout
    assert "https://example.org" in _run(
        tmp_path, vault, "get", "shortcut-link").stdout


def test_probe_kept_kinds_add_in_silence(tmp_path):
    vault = _vault(tmp_path)
    key = _file(tmp_path, "key.txt", "synthetic-key-body")
    cert = _file(tmp_path, "cert.txt", "synthetic-cert-body")
    runs = [
        ("add", "otp", "--type", "totp",
         "--secret", "SYNTHETICSECRET"),
        ("add", "lic", "--type", "license",
         "--key", "LIC-SYNTHETIC-1"),
        ("add", "me", "--type", "identity",
         "--full-name", "Synthetic Person"),
        ("add", "ssh", "--type", "sshkey",
         "--key-file", key),
        ("add", "crt", "--type", "certificate",
         "--cert-file", cert),
    ]
    for argv in runs:
        out = _run(tmp_path, vault, *argv).stdout
        assert NOTICE not in out, argv
    assert "Synthetic Person" in _run(
        tmp_path, vault, "get", "me").stdout


# Required-field arguments for the other road's kinds,
# general road first, then the shortcut road.
_GENERAL_FOREIGN = [
    (("add", "chart", "--type", "astrology",
      "--sign", "Pisces"), "Pisces"),
    (("add", "hero", "--type", "character-sheet",
      "--name", "Synthetic Hero", "--level", "3"),
     "Synthetic Hero"),
    (("add", "runes", "--type", "rune-reading",
      "--spread-type", "single"), "single"),
    (("add", "cards", "--type", "tarot-reading",
      "--spread-type", "three-card"), "three-card"),
    (("add", "doc", "--type", "markdown",
      "--title", "Synthetic Doc",
      "--content", "synthetic doc body"),
     "synthetic doc body"),
]
_SHORTCUT_FOREIGN = [
    (("add-astrology", "s-chart",
      "--sign", "Leo"), "Leo"),
    (("add-character-sheet", "s-hero",
      "--name", "Shortcut Hero"), "Shortcut Hero"),
    (("add-rune-reading", "s-runes",
      "--spread-type", "three-rune"), "three-rune"),
    (("add-tarot-reading", "s-cards",
      "--spread-type", "celtic-cross"), "celtic-cross"),
    (("add-markdown", "s-doc", "--title", "Shortcut Doc",
      "--content", "shortcut doc body"),
     "shortcut doc body"),
]


def test_probe_other_road_general_road_announces(tmp_path):
    vault = _vault(tmp_path)
    for argv, marker in _GENERAL_FOREIGN:
        out = _run(tmp_path, vault, *argv).stdout
        assert NOTICE in out, argv
        assert "kept here exactly as given" in out
        service = argv[1]
        got = _run(tmp_path, vault, "get", service).stdout
        assert marker in got, argv


def test_probe_other_road_shortcuts_announce(tmp_path):
    vault = _vault(tmp_path)
    for argv, marker in _SHORTCUT_FOREIGN:
        out = _run(tmp_path, vault, *argv).stdout
        assert NOTICE in out, argv
        service = argv[1]
        got = _run(tmp_path, vault, "get", service).stdout
        assert marker in got, argv


def test_probe_custody_of_existing_entries_is_silent(tmp_path):
    vault = _vault(tmp_path)
    _run(tmp_path, vault, "add-astrology", "chart",
         "--sign", "Pisces")
    got = _run(tmp_path, vault, "get", "chart").stdout
    assert "Pisces" in got and NOTICE not in got
    listing = _run(tmp_path, vault, "list").stdout
    assert "chart" in listing and NOTICE not in listing


def test_probe_add_soul_announces(tmp_path):
    home = tmp_path / "home"
    (home / ".hermes" / "personality").mkdir(parents=True)
    (home / ".hermes" / "SOUL.md").write_text(
        "SYNTHETIC SOUL TEXT")
    (home / ".hermes" / "personality"
     / "runa-identity.md").write_text(
        "SYNTHETIC IDENTITY TEXT")
    vault = _vault(tmp_path)
    out = _run(tmp_path, vault, "add-soul").stdout
    assert "a soul backup is not one of the" in out
    got = _run(tmp_path, vault, "get",
               "soul-backup-soul").stdout
    assert "SYNTHETIC SOUL TEXT" in got


def test_probe_add_cron_backup_announces(tmp_path):
    bindir = tmp_path / "bin"
    bindir.mkdir()
    fake = bindir / "crontab"
    fake.write_text(
        '#!/bin/sh\necho "0 1 * * * synthetic-job"\n')
    fake.chmod(0o755)
    vault = _vault(tmp_path)
    env = {"PATH": str(bindir) + os.pathsep
           + os.environ.get("PATH", "")}
    out = _run(tmp_path, vault, "add-cron-backup",
               extra_env=env).stdout
    assert "a crontab backup is not one of the" in out
    got = _run(tmp_path, vault, "get", "cron-backup").stdout
    assert "synthetic-job" in got


def test_probe_legacy_soul_key_heals_on_load(tmp_path):
    # Docket 137's third shape: a soul backup stored
    # before this slice sits under a mixed-case key
    # (soul-backup-SOUL) that the lowercased lookups
    # could never reach. Recreate that exact shape
    # in-process, then the ordinary get road must
    # find the entry — the load normalises the key.
    vault = _vault(tmp_path)
    _run(tmp_path, vault, "add", "placeholder",
         "--username", "u", "--password-file",
         _file(tmp_path, "pw.txt", "synthetic-pw"))
    home = tmp_path / "home"
    env = dict(os.environ)
    env["HOME"] = str(home)
    env["KISTA_DIR"] = str(vault)
    parts = [str(KISTA), site.getusersitepackages(),
             env.get("PYTHONPATH", "")]
    env["PYTHONPATH"] = os.pathsep.join(p for p in parts if p)
    snippet = (
        "import scripts.credstore as cs\n"
        "key = cs._get_key()\n"
        "vault = cs._load_vault(key)\n"
        "vault['entries']['soul-backup-SOUL'] = {\n"
        "    'service': 'soul-backup-SOUL',\n"
        "    'entry_type': 'markdown',\n"
        "    'title': 'SOUL',\n"
        "    'content': 'LEGACY SOUL TEXT',\n"
        "}\n"
        "cs._save_vault(vault, key)\n"
    )
    subprocess.run([sys.executable, "-c", snippet],
                   capture_output=True, text=True, env=env,
                   check=True, stdin=subprocess.DEVNULL)
    got = _run(tmp_path, vault, "get",
               "soul-backup-soul").stdout
    assert "LEGACY SOUL TEXT" in got


def test_probe_notice_composes_with_program_access(tmp_path):
    # E-097 + E-098: a program caller adding an
    # other-road kind under its own name hears the
    # same notice, and the entry is stamped and
    # scoped exactly as any other of its entries.
    vault = _vault(tmp_path)
    out = _run(tmp_path, vault, "add-astrology", "chart",
               "--sign", "Pisces",
               program="ember-core").stdout
    assert NOTICE in out
    got = _run(tmp_path, vault, "get", "chart",
               program="ember-core").stdout
    assert "Pisces" in got
    refused = _run(tmp_path, vault, "get", "chart",
                   program="other-app", check=False)
    assert refused.returncode == 1
    assert "Pisces" not in refused.stdout
