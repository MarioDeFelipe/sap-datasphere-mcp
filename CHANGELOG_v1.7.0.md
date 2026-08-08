# Changelog - v1.7.0 (input validation hardening)

**Release Date:** 2026-08-08

Acts on `VALIDATION_AUDIT_FINDINGS.md`. This is the last release on the 1.x
line before the MCP SDK v2 port; the `mcp>=1.28,<2` pin is unchanged, and
everything here forward-ports into 2.x.

---

## What the audit found, and what changed

The audit counted **42 of 150 tool inputs with no validation rule**, of which
**18 were identifiers interpolated raw into URL paths** across 9 tools. Path
segments are the ones that matter: query values are URL-encoded by the HTTP
client before transmission, so an unvalidated one produces a bad request at
worst, while a path segment containing `/`, `?` or `..` changes what the
request addresses.

Implementing the fix surfaced two further problems the audit could not see,
both of the same kind — **validation that exists and silently does not run**.

### 1. The validator registry had drifted (the more serious one)

`has_validator()` consulted a hand-maintained list, while
`get_validator_rules()` consulted a separate dict. They had diverged:
`analyze_column_distribution` and `find_assets_by_column` had complete rule
sets that were **never executed**, because the list omitted them. Nine inputs
were affected.

This also means the audit's headline understated the problem: **51 of 150
inputs were effectively unvalidated**, not 42.

`get_all_tool_names()` and `has_validator()` now derive from a single
`_rule_builders()` registry, so the two can no longer disagree.

### 2. `allowed_values` was a no-op on `STRING` rules

Only `_validate_enum` consulted `allowed_values`, so any rule written as
`ValidationType.STRING` + `allowed_values` enforced nothing. That included a
pre-existing rule — `get_catalog_metadata.endpoint_type` accepted any string
despite declaring three permitted values.

`_validate_string` now honours `allowed_values`, which fixes the existing rule
as well as the new ones.

### 3. Rules for the 12 tools that had none

`smart_query`, `get_asset_variables`, `list_relational_entities`,
`get_relational_entity_metadata`, `query_relational_entity`,
`get_relational_odata_service`, `run_task_chain`, `get_task_log`,
`get_task_history`, and the three `test_*` diagnostics.

No new mechanism was invented: `space_id` reuses `ValidationType.SPACE_ID`
(`^[A-Z][A-Z0-9_-]*$`, already used by 25 tools) and path identifiers reuse the
established `^[A-Za-z0-9_\-]+$` pattern, now named `PATH_SEGMENT_PATTERN`.

**Coverage is now 45/45 tools and 145/150 inputs.** The remaining five are
object- and array-typed body/query parameters (`user_definition`,
`updated_definition`, `select_fields`, `expand_fields`, `object_types`) — none
reach a path segment.

### 4. Path segments are percent-encoded as a backstop

Validation is the primary control and produces the clear message. But this
release found validation silently not running twice, so identifiers now also
pass through `_seg()` (`quote(value, safe='')`) at the 29 sites where they are
interpolated into a URL path. If a tool is ever added without rules — which is
exactly how this defect arose — its identifiers still cannot alter the
request's structure.

Verified as a no-op for real identifiers (`DEMO_SALES`, `ORDER_LINES`,
`DEMO_Open_Lines`, `DEMO_PRODUCTS` are unchanged) and confirmed live against the
test tenant tenant: the quoted path returns rows normally.

### 5. `validate_parameter_value` is documented as deliberately unwired

Added in 1.6.0 with quote rejection and unit tests, then never called. The
audit found the reason: **no handler builds the `(<param>='<value>')/Set` URL
form at all** — `get_asset_variables` only reads variable declarations out of
`$metadata`. It is kept and tested so the restriction is already enforced when
parameterised-asset execution is implemented, its docstring explains the
status, and it is no longer imported into the server, since an unused import
implied a wiring that does not exist.

A test pins this: if that URL form is ever built, the test fails and asks for
the validator to be wired in.

---

## Also fixed while in here

`analyze_column_distribution` interpolates `asset_name` and `column_name` into
a SQL string (`FROM {asset_name}`). That query is **built but never executed** —
the handler returns a mock-shaped result, and the code says "in production,
parse SQL results". It is not a live injection today, but it will become one
the moment someone wires it up, so both identifiers are now pattern-constrained.

---

## Tests

`tests/test_input_validation.py` — 38 cases. The important one is
`test_every_tool_with_inputs_has_a_validator`: shipping a tool without rules is
the defect this release fixes, and it now fails in CI rather than reaching a
user. Alongside it: registry-integrity checks, traversal rejection across the
newly-covered tools, `allowed_values` enforcement including the pre-existing
case, and a source-level check that no path f-string interpolates an identifier
without `_seg()`.

Full suite: **142 passed**.

Written against 1.x deliberately — the SDK v2 port inherits them and must keep
them green.

---

## Not in this release

No SDK v2 work; `mcp>=1.28,<2` unchanged. The five object/array inputs remain
unvalidated. Whether `NON_FILTERABLE_TYPES` should become a general
literal-to-column compatibility rule is still open, and still 1.x hardening
rather than port work.
