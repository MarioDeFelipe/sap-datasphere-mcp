# Changelog - v2.0.2 (remove live-tenant metadata from the distribution)

**Release Date:** 2026-08-08 · **Base:** 2.0.1 (`b293317`)

No functional change. This release exists to stop distributing something that
was not ours to distribute.

## What was wrong

The test fixtures added in **v1.5.0** were real SAP Datasphere `$metadata`
captured from a live customer tenant: genuine element names and business
labels from one of their assets. No row data and no credentials — but a
customer's data model, and it was not our decision to publish it.

It was present in the public repository and inside **every published wheel and
sdist from 1.5.0 through 2.0.1**, plus references scattered through four
changelogs, four test modules, and one source docstring.

## What changed

Fixtures are now synthetic. The *shape* is preserved exactly — OData V4
envelope, external `<Annotations Target=…>` blocks, `Common.Label`,
`Analytics.Dimension` / `Analytics.measure`, the `Capabilities.CountRestrictions`
annotation the capability layer reads, two-key `<Key>` on the relational side —
so the parser and capability tests still exercise the same code paths. Only the
identity changed: namespace, space, asset, every element name and every label.

Verified after the swap: 18 properties, 17 dimensions, 1 measure, 12 labels,
`Countable:false` on analytical and absent on relational — the same numbers the
real fixtures produced. **190 tests pass.**

Customer identifiers were also removed from `CHANGELOG_v1.5.0.md`,
`v1.6.0.md`, `v1.7.0.md` and `v2.0.1.md`, which ship inside the wheel via
`package-data`.

## Preventing recurrence

`tests/test_no_live_tenant_data.py` fails the build if a known live-tenant
identifier reaches a tracked file. It caught two stragglers the manual sweep
missed within minutes of being written.

Live captures now belong in an untracked `local-captures/` directory.
Capturing real `$metadata` while developing is fine and often necessary; it
just never becomes a commit.

## Scope, stated plainly

This release stops **forward** distribution. Artifacts already published as
1.5.0 – 2.0.1 still contain the original fixtures, and the repository history
still contains them. Removing those is a separate decision, deliberately not
bundled here.

Not swept, and deliberately: `ailien-test` is this project's own development
tenant rather than a customer's, and appears in ~27 files including historical
test-result records; `SAP_CONTENT` and `SAP_SC_*` are SAP's own shipped
business content. Both are noted in the guard so nobody removes them by
reflex.
