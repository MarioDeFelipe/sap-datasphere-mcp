# v2.0.3 — credential removal, and the rest of the path-encoding sweep

This is a **security release**. Upgrade if you use any version before 2.0.3.

---

## Committed OAuth credentials removed

Two OAuth client secrets and two client ids were committed to this repository
on 2025-10-25 and had been present ever since — in `datasphere_connector.py`,
in `enhanced_datasphere_connector.py`, and across six documentation files that
carried complete, working values.

**Scope of exposure:**

| Surface | Exposed? | Why |
|---|---|---|
| PyPI wheel | **No** | These modules are not in `[tool.setuptools] py-modules` |
| PyPI sdist | **No** | Confirmed by unpacking the published 2.0.2 sdist |
| npm package | **No** | Thin wrapper; ships no Python source |
| **Public GitHub repo** | **Yes** | Tracked files, and still present in history |

The credentials belong to the maintainer's own test tenant — no customer
credential was involved. They are removed from the working tree; **rotation
and history rewrite are tracked separately**, because removing a secret from
the tip of a branch does not remove it from the history.

All four values now come from the environment. `create_datasphere_connector()`
raises a `ValueError` naming the missing variables instead of falling back to
anything.

## No more tenant default

`DATASPHERE_BASE_URL` and `DATASPHERE_TENANT_ID` defaulted to a specific
tenant's host and id. Any install that ran outside mock mode without setting
`DATASPHERE_BASE_URL` silently addressed **that tenant** rather than failing.

Both defaults are gone. `_require_tenant_config()` now raises at startup with
a message naming the variable and pointing at `.env.example`. Mock mode is
exempt, so tests and demos need no tenant configuration.

## Path encoding finished

1.7.0 introduced `_seg()` to percent-encode values interpolated into URL
paths, but ten sites were missed. All ten now route through it:

- `get_task_status` — `tasks/{task_id}`
- `find_assets_by_column` — `analytical/{space_id}/{asset_name}/$metadata`
- `get_analytical_metadata` — `spaces('{space_id}')/assets('{asset_id}')`
- `get_object_definition` — `spaces('{space_id}')/assets('{object_id}')`
- `test_analytical_endpoints` — six diagnostic endpoints

The two `spaces('X')/assets('Y')` sites are OData **key predicates**, where a
single quote would close the literal early rather than merely mis-address the
request. Percent-encoding alone is not a sufficient control there — the real
control is validation, and `PATH_SEGMENT_PATTERN` and `SPACE_ID_PATTERN`
already rejected quotes on every affected parameter. No new rule was needed;
`test_seg_covers_odata_key_predicate_positions` pins that no such URL is ever
built from an unencoded value.

**The guard that should have caught this has been rewritten.** It matched a
hardcoded list of identifier names and only inspected assignments to a few
known variable names, so it was blind to `test_model_id` / `test_space_id`
and to every `"endpoint": f"..."` dict entry. It is now structural: anything
that looks like an API path is checked, whatever the placeholder is called,
with a single documented exception for `base_url` (operator-supplied config
carrying scheme and host, which percent-encoding would destroy).

## Contradictory filter type tables

`cds.largestring` appeared in both `NON_FILTERABLE_TYPES` and
`STRING_COMPATIBLE_TYPES`. Since `check_field_filterable()` runs *before*
`_check_field_string_compatible()`, the second entry could never be reached —
it asserted a working code path that does not exist. Removed from
`STRING_COMPATIBLE_TYPES`; behaviour is unchanged, because it was unreachable.

The `NON_FILTERABLE_TYPES` entry stays: it fires only when `$metadata`
declares the CDS name literally, whereas the Consumption API surfaces
LargeString as `Edm.String`, and in that form it filters normally.

## New guards

- `test_no_credential_shaped_strings_in_tracked_files` — pattern-based, not a
  denylist. A denylist has to contain the secret to match it, which is how a
  guard becomes the leak; this also catches credentials nobody has added yet.
- `test_no_tenant_default_in_server_config`
- `test_largestring_is_not_claimed_string_compatible`

Each was mutation-tested — planted the defect, confirmed the guard fails,
reverted, confirmed it passes.

## Documentation

`README.md` claimed 42, 45, and 48 tools in different places; the server
advertises **39** by default and **49** with diagnostics enabled. All counts
reconciled and the historical v1.0.9 test-results block dated as such.
`pii_masking.py`, `telemetry.py`, `odata_v4_annotations.py`, `odata_filter.py`,
`asset_capability.py`, `error_helpers.py` and `tool_descriptions.py` were
shipping undocumented and are now in the project structure.

---

**No API changes.** Upgrading from 2.0.x requires no code changes unless you
relied on the tenant default, which now raises instead.
