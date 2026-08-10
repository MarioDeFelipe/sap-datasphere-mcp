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
