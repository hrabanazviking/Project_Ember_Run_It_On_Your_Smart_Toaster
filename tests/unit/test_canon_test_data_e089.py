"""E-089 — Canon-shaped test data only.

Roadmap line: "Canon-shaped test data only (synthetic; no
real companion history in fixtures)." Proves
``docs/architecture/E-089_CANON_SHAPED_TEST_DATA.md``:

* the audit: every test-data surface in the root ``tests/``
  tree was scanned for real companion history — real
  identities as fixture personae, real people's names,
  real addresses, real life facts — and what the scan
  found is classified in the doc, file by file;
* the one real-history shape the audit found in the
  campaign's own batteries is fixed: E-080/E-081/E-082
  ran their fabricated facts (a ferry, a beekeeper) under
  a real companion identity as the fixture persona. Those
  facts now run under the canon fixture persona, and this
  battery's scanner keeps any real identity out of the
  test tree from here on;
* the canon is named and pinned: fixture personae are
  exactly the canon set (plus the adversarial invalid
  slugs, whose whole job is to be refused), the canon
  world is the ferry / beekeeper / harbour world the
  Part V batteries share, and every email-shaped string
  in the test tree is an ``example.com`` synthetic;
* one name is controlled, not forbidden: the householder's
  name appears in elder test shapes that are not fixture
  history at all (a connection-string username shape, a
  keyring username, governance needles pinning "the
  owner's word" in campaign docs, one system name, one
  book filename). Each such file is allowlisted here with
  its reason; the name appearing in any other test file
  fails this battery;
* docket 126's regression pin lives in the E-075 battery
  (the load-truth instrument's home); this battery pins
  that the fix is present in the instrument's source.

The scanner's marker strings are assembled from fragments
so this file does not itself carry the shapes it forbids;
the file also excludes itself and ``__pycache__`` (compiled
residue, not source) by name, stated here, not silently.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TESTS = REPO / "tests"
DOC = REPO / "docs" / "architecture" / "E-089_CANON_SHAPED_TEST_DATA.md"
SELF = Path(__file__).resolve()

# Marker fragments — assembled, never literal (see docstring).
_REAL_COMPANION = "yr" + "sa"
_FAMILY_NAME = "clay" + "don"
_HOUSEHOLDER = "vol" + "marr"
_GMAIL = "@gma" + "il.com"
_PROTON = "@proton" + "mail.com"

#: Shapes that must never appear in the root test tree at
#: all: real identities, real family names, real mailboxes,
#: real life facts (benefits, the car, the other worlds).
FORBIDDEN_ALWAYS = (
    _REAL_COMPANION,
    "freydisdottir",
    _FAMILY_NAME,
    _HOUSEHOLDER + "wyrd",
    _GMAIL,
    _PROTON,
    "medicaid",
    "medicare",
    "indiana",
    "hyundai",
    "second life",
    "purplelongship",
    "purpleviking",
)

#: The householder's name, allowlisted per file — every
#: entry a non-fixture use, with its reason. Any other
#: test file carrying the name fails this battery.
VOLMARR_ALLOWLIST = {
    # The guarded live test of the real backend: the
    # connection-string username is the shape under test.
    "tests/integration/test_pgvector_real_backend.py":
        "real-backend connection shape (guarded live test)",
    # Elder unit tests: the same username shape inside
    # connection strings and a fake keyring, testing
    # parsing and redaction — no history, no facts.
    "tests/unit/test_brunnr_pgvector_schema.py":
        "connection-string username shape",
    "tests/unit/test_brunnr_pgvector_secrets.py":
        "connection-string / keyring username shape",
    "tests/unit/test_hardening_batch_cde.py":
        "connection-string username shape",
    "tests/unit/test_schemas_config.py":
        "connection-string username shape",
    "tests/unit/test_dependency_diet_e044.py":
        "connection-string username shape",
    # A system name, not a person: the Hermes hack's
    # volmarr-core producer namespace.
    "tests/unit/test_hermes_nerves_e068.py":
        "system producer name (volmarr-core)",
    # A filename in the tree (the design lawbook file),
    # named to prove it is excluded from the install.
    "tests/unit/test_install_weight_e043.py":
        "tracked filename reference",
    # Governance needles: doc-pinning tests asserting the
    # phrase "the owner's word" stands in campaign docs
    # wherever a verdict is reserved to him.
    "tests/unit/test_memory_verdict_e079.py":
        "governance needle in a doc-pinning test",
    "tests/unit/test_memory_face_e080.py":
        "governance needle in a doc-pinning test",
    "tests/unit/test_memory_migration_e081.py":
        "governance needle in a doc-pinning test",
    # Added consciously at E-090 (the act this guard exists
    # to force): its doc-pinning test asserts the retirement
    # in the memory-model doc stays reserved to his word.
    "tests/unit/test_memory_model_docs_e090.py":
        "governance needle in a doc-pinning test (added E-090)",
}

#: The canon fixture personae. A new persona id in any
#: test must be added here consciously — that act is the
#: review this slice exists to force.
CANON_PERSONAE = {
    "ember", "sage", "ember-2", "mabel",
    "default", "other", "p", "p1", "saga",
}
#: Invalid slugs whose whole job is to be refused.
ADVERSARIAL_PERSONAE = {
    "../sage", "Not A Slug", "Not A Slug!", "not a slug!",
}

_SCAN_SUFFIXES = {".py", ".md", ".json", ".txt", ".yaml", ".yml"}


def _test_files() -> list[Path]:
    return sorted(
        p for p in TESTS.rglob("*")
        if p.is_file()
        and p.suffix in _SCAN_SUFFIXES
        and "__pycache__" not in p.parts
        and p.resolve() != SELF
    )


def _text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


# --------------------------------------------------------------------- #
# The audit, armed                                                       #
# --------------------------------------------------------------------- #


def test_no_real_history_markers_anywhere_in_the_test_tree():
    offenders = []
    for p in _test_files():
        low = _text(p).lower()
        for marker in FORBIDDEN_ALWAYS:
            if marker in low:
                offenders.append((str(p.relative_to(REPO)), marker))
    assert offenders == [], offenders


def test_householder_name_only_where_allowlisted():
    seen = set()
    for p in _test_files():
        if _HOUSEHOLDER in _text(p).lower():
            seen.add(str(p.relative_to(REPO)))
    assert seen == set(VOLMARR_ALLOWLIST), (
        f"unlisted: {sorted(seen - set(VOLMARR_ALLOWLIST))}; "
        f"stale allowlist entries: "
        f"{sorted(set(VOLMARR_ALLOWLIST) - seen)}")


def test_every_email_shaped_string_is_synthetic():
    domains = set()
    for p in _test_files():
        for m in re.finditer(
                r"[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})",
                _text(p)):
            domains.add(m.group(1).lower())
    assert domains <= {"example.com"}, domains


# --------------------------------------------------------------------- #
# The canon, pinned                                                      #
# --------------------------------------------------------------------- #


def test_persona_ids_in_tests_are_the_canon_set():
    found = set()
    pat = re.compile(r"""(?:persona_id|user_id|persona)=["']([^"']+)["']""")
    for p in _test_files():
        found.update(pat.findall(_text(p)))
    assert found <= CANON_PERSONAE | ADVERSARIAL_PERSONAE, (
        f"non-canon persona ids: "
        f"{sorted(found - CANON_PERSONAE - ADVERSARIAL_PERSONAE)}")
    # The canon's two principals are really in use (the set
    # is a census, not a wish).
    assert {"ember", "sage"} <= found


def test_canon_world_is_the_shared_synthetic_one():
    e080 = _text(TESTS / "unit" / "test_memory_face_e080.py")
    assert "The harbour ferry leaves at dawn carrying letters" in e080
    assert "The beekeeper keeps nine hives behind the orchard" in e080


def test_fixtures_library_carries_no_unscanned_data():
    # tests/fixtures/ is the tree's promised fixture
    # library (its README). At this slice it holds only
    # that README — every fixture lives inline in its
    # battery, where this scanner sees it. Any file added
    # there is scanned by the tests above like any other.
    fixtures = sorted(
        p.name for p in (TESTS / "fixtures").iterdir()
        if "__pycache__" not in p.parts)
    assert fixtures == ["README.md"], fixtures


# --------------------------------------------------------------------- #
# Docket 126 — the instrument fix stands                                 #
# --------------------------------------------------------------------- #


def test_load_truth_socket_guard_is_present():
    src = (REPO / "Verdandi" / "load_truth.py").read_text(
        encoding="utf-8")
    assert ">= 108" in src and "vd-lt-" in src
    assert "docket 126" in src


def test_doc_records_the_audit_and_the_fix():
    text = DOC.read_text(encoding="utf-8")
    for needle in ("In plain words", "canon", "synthetic",
                   "docket 126", "108", "ember",
                   "allowlist"):
        assert needle in text, needle
