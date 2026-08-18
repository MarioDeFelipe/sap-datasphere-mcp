# Changelog - v1.7.1 (restore an installable 1.x line)

**Release Date:** 2026-08-18 · **Base:** 1.7.0

No functional change from 1.7.0. This release exists because **1.7.0 no longer
exists on PyPI** — it, along with 1.5.0 through 2.0.1, was deleted during the
customer-data remediation. That left `pip install "sap-datasphere-mcp<2"`
resolving to **1.3.0**, whose dependency is the unbounded `mcp>=1.2.0`, so it
pulls MCP SDK 2.0.0 and crashes at import with

```
AttributeError: 'Server' object has no attribute 'list_resources'
```

1.7.1 is 1.7.0's code with the correct `mcp>=1.28,<2` pin, republished under a
version number PyPI will accept — the deleted strings are burned permanently
and cannot be reused.

## Which version should I install?

| Want | Command | Gets you |
|---|---|---|
| Current | `pip install sap-datasphere-mcp` | 2.x on MCP SDK 2.x |
| SDK 1.x line | `pip install "sap-datasphere-mcp<2"` | **1.7.1** on MCP SDK 1.28–1.29.x |

The 2.x server is dual-era and answers both the modern `server/discover`
handshake and the legacy `initialize` one, so most people want 2.x. Stay on 1.x
only if your environment cannot install SDK 2.x.

## Also in this release

The test fixtures on this branch are the **synthetic** ones introduced in
2.0.2. The history rewrite removed the originals without replacing them, so
`tests/fixtures/` was empty on this branch and the parser tests had nothing to
read; the synthetic fixtures preserve the OData V4 shape — external
`<Annotations Target=…>` blocks, `Common.Label`, `Analytics.Dimension` /
`Analytics.measure`, two-key `<Key>` — while carrying no customer identity.

`tests/test_no_live_tenant_data.py` is ported here too, so the 1.x line has the
same guard as 2.x: the build fails if a known live-tenant identifier reaches a
tracked file.

**One correction worth recording.** The guard now matches with word boundaries
in Python. It previously used plain substring matching, and the verification
around it used `git grep -E '\b…'` — but neither `git grep -E` nor BSD
`grep -E` treats `\b` as a word boundary, so both reported clean on files that
plainly contained the token. That false negative is why this branch still held
customer values after the first remediation pass. Verification of this kind
must be done in Python, or with a fixed-string grep.

## Older 1.x releases

Every 1.x release before this one declares an unbounded `mcp` dependency and
will pull SDK 2.x, which this code cannot run. They are yanked: still
installable by exact pin, but no longer selected by a range.

## Tests

**174 passed** on MCP SDK 1.29.0.
