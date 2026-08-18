"""Guard: no live-tenant data may be committed.

v1.5.0 shipped test fixtures captured from a real customer tenant — genuine
column names and business labels. No row data and no secrets, but a customer's
data model, published in the public repo and inside every wheel from 1.5.0 to
2.0.1. It was not ours to publish.

Fixtures are synthetic from 2.0.2 onward. This test is what makes that hold:
capturing live `$metadata` while developing is fine and often necessary, but it
stays in an untracked scratch directory and never reaches a commit.

If this fails on a token that is genuinely generic, prefer renaming the fixture
over widening the denylist — the list is meant to be uncomfortable.

Run with:  pytest tests/test_no_live_tenant_data.py -v
"""

import base64
import os
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent

#: Identifiers seen on real tenants this project has touched. Substring match,
#: case-insensitive. Tenant hosts, space ids, asset ids, and the SAP field names
#: that give a customer's model away.
#: Base64-encoded on purpose. This file ships inside the sdist, so spelling the
#: tokens literally here would re-publish the very identifiers it exists to keep
#: out — the guard would become the leak. Decoded at import; never logged.
_DENIED_B64 = [
    "cGFydHN0b3du",
    "cGFydHMgdG93bg==",
    "U0NNX0JVU0lORVNT",
    "T1BFTl9QT19ERVRBSUw=",
    "WkRfTUFURVJJQUw=",
    "WlJFVF9PcGVuX0xpbmVz",
    "UFJfUmVwb3J0X0RKTQ==",
    "RklOQU5DRV9CVVNJTkVTUw==",
    "UFJJQ0lOR19URUFN",
    "TUFUTlI=",
    "RUJFTE4=",
    "RUJFTFA=",
    "SU5GTlI=",
    "UFJPRFVDVFVVSUQ=",
    "UHVyY2hhc2luZyBEb2N1bWVudA==",
    "TWF0ZXJpYWwgTnVtYmVy",
    "cHVyY2hhc2luZyBpbmZvIHJlY29yZA=="
]
DENYLIST = [base64.b64decode(t).decode() for t in _DENIED_B64]
#: Deliberately NOT in the denylist, and worth explaining so nobody "fixes" it
#: by accident.
#:
#: ``ailien-test`` is this project's own development tenant, not a customer's,
#: and it appears in ~27 files — README-style docs, connector defaults, and
#: historical test-result records. Publishing your own tenant hostname is a
#: different question from publishing a customer's data model, and sweeping it
#: would rewrite records of what was actually tested. It is a scope decision
#: for the maintainer, not something this guard should force.
#:
#: ``SAP_CONTENT`` and the ``SAP_SC_*`` asset names are SAP's own shipped
#: business content, not any customer's data.
_NOT_DENIED_BY_DESIGN = ("ailien-test", "SAP_CONTENT", "SAP_SC_")

#: Only source that ships or is version-controlled. Excludes the scratch dir
#: where live captures are allowed to live locally.
SCAN_SUFFIXES = {".py", ".md", ".xml", ".json", ".yaml", ".yml", ".toml", ".txt", ".cfg"}
SKIP_DIRS = {".git", "node_modules", "htmlcov", "build", "dist", "__pycache__",
             ".pytest_cache", ".venv", "venv", "local-captures"}


def _iter_files():
    for path in REPO.rglob("*"):
        if not path.is_file() or path.suffix not in SCAN_SUFFIXES:
            continue
        if any(part in SKIP_DIRS or part.endswith(".egg-info") for part in path.parts):
            continue
        if path.name == pathlib.Path(__file__).name:   # this file names them on purpose
            continue
        yield path


@pytest.mark.parametrize("token", DENYLIST)
def test_no_live_tenant_identifier_is_committed(token):
    pattern = re.compile(re.escape(token), re.IGNORECASE)
    hits = []
    for path in _iter_files():
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if pattern.search(line):
                hits.append(f"{path.relative_to(REPO)}:{i}")
    assert not hits, (
        f"live-tenant identifier {token!r} found in tracked files: {hits[:8]}. "
        "Fixtures must be synthetic; keep live captures in an untracked scratch dir."
    )


def test_fixtures_are_the_synthetic_ones():
    """A positive assertion, so deleting the fixtures doesn't silently pass."""
    fixtures = sorted(p.name for p in (REPO / "tests" / "fixtures").glob("*.xml"))
    assert fixtures == [
        "odata_v4_analytical_ORDER_LINES.xml",
        "odata_v4_relational_ORDER_LINES.xml",
    ], fixtures


def test_synthetic_fixtures_still_carry_the_shapes_under_test():
    """Scrubbing identity must not scrub the structure the parser tests rely on.

    If a future scrub flattens these, the parser tests would still pass while
    testing nothing — so assert the annotations are actually present.
    """
    analytical = (REPO / "tests" / "fixtures" /
                  "odata_v4_analytical_ORDER_LINES.xml").read_text()
    relational = (REPO / "tests" / "fixtures" /
                  "odata_v4_relational_ORDER_LINES.xml").read_text()
    for needle in ("Annotations Target=", "Common.Label",
                   "Analytics.Dimension", "Analytics.measure",
                   "CountRestrictions"):
        assert needle in analytical, f"analytical fixture lost {needle}"
    for needle in ("Annotations Target=", "Common.Label", "<Key>"):
        assert needle in relational, f"relational fixture lost {needle}"


# ── Credential shapes ────────────────────────────────────────────────────────
#
# Deliberately pattern-based rather than a denylist of known values. A denylist
# would have to contain the secrets to match them, which is how a guard becomes
# the leak (see the base64 encoding above, added for exactly that reason). These
# patterns also catch credentials nobody has thought to add yet.

_CREDENTIAL_SHAPES = [
    # BTP OAuth client secret: <uuid>$<base64>
    (r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\$[A-Za-z0-9_\-]{20,}=",
     "OAuth client secret"),
    # BTP service-broker client id: sb-<uuid>!b<n>|client!b<n>
    (r"sb-[0-9a-f]{8}-[0-9a-f-]{20,}!b[0-9]+\|client!b[0-9]+",
     "OAuth client id"),
]


def test_no_credential_shaped_strings_in_tracked_files():
    """No live OAuth credential may be committed, in code or in prose.

    2.0.3 removed two client secrets and two client ids that had been sitting
    in the repository since 2025-10-25 -- in a connector factory, in a second
    connector, and across six documentation files. The docs mattered as much
    as the code: they carried complete, working values.
    """
    import re
    import subprocess

    tracked = subprocess.run(
        ["git", "ls-files"], cwd=REPO, capture_output=True, text=True
    ).stdout.split()

    offenders = []
    for rel in tracked:
        path = REPO / rel
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for pattern, label in _CREDENTIAL_SHAPES:
            for match in re.finditer(pattern, text):
                line = text[: match.start()].count("\n") + 1
                offenders.append(f"{rel}:{line} ({label})")

    assert not offenders, (
        "credential-shaped string(s) committed:\n  " + "\n  ".join(offenders)
    )


def test_no_tenant_default_in_server_config():
    """Live mode must not fall back to any particular tenant.

    DATASPHERE_BASE_URL defaulted to a real tenant host, so any install that
    forgot to set it addressed that tenant instead of failing.
    """
    import re
    src = (REPO / "sap_datasphere_mcp_server.py").read_text()
    defaults = re.findall(
        r"os\.getenv\(\s*['\"]DATASPHERE_(?:BASE_URL|TENANT_ID)['\"]\s*,\s*['\"]([^'\"]+)['\"]",
        src,
    )
    assert not defaults, f"tenant-specific default(s) in config: {defaults}"
