# Changelog - v1.6.0 (partial text matching in `$filter`)

**Release Date:** 2026-08-07

SAP Datasphere added three OData v4 string functions to `$filter` on the
Consumption API:

```
startswith(<field>,'<value>')
endswith(<field>,'<value>')
contains(<field>,'<value>')
```

This matters disproportionately for an MCP server: an agent rarely knows exact
stored values, so partial matching removes a whole class of "list the distinct
values first" round trips that burn tokens and truncate.

These are the OData **v4** spellings. The v2 `substringof` form is not accepted
by this API, and is now rejected with a message pointing at `contains`.

---

## Tenant probe results

Run against `the test tenant` (US20) on 2026-08-07. Two things the SAP
documentation does not state:

### Filtering is case-sensitive

Confirmed on `DEMO_SALES/ORDER_LINES`, whose stored values are uppercase:

| Filter | Rows |
|---|---|
| `contains(PRODUCT_CODE,'DEMO')` | 6 |
| `contains(PRODUCT_CODE,'demo')` | **0** |
| `startswith(SITE,'US')` | 50 |
| `startswith(SITE,'us')` | **0** |
| `SITE eq 'SITE1'` | 50 |
| `SITE eq 'site1'` | **0** |

This applies to `eq` as well as to the three functions. There is no server-side
workaround: the supported function list is closed and `tolower()` is not in it.
The tool descriptions therefore state the behaviour plainly.

### Non-filterable types reject on type incompatibility

`Edm.Binary` rejects both `contains()` **and** `eq '<literal>'`, with the same
error:

```
400  The type 'Edm.Binary' is not compatible to 'Edm.String'
```

So the mechanism is incompatibility with the string literal rather than a
distinct "not filterable" flag. The same error rejects `contains()` applied to
an `Edm.Decimal` column.

One consequence worth recording: `cds.LargeString` surfaces in `$metadata` as
`Edm.String`, so by this mechanism it should filter normally -- which is at
odds with the documentation's annotation-limitations table. **Unverified**: no
`LargeString` column exists in the 80 assets scanned across seven spaces
(observed types were `Edm.String`, `Decimal`, `Double`, `Date`,
`DateTimeOffset`, `TimeOfDay`, `Binary`). The validator follows the observed
mechanism rather than the table.

### `$count` asymmetry

Confirmed independent of lineage:

* relational -- `$count=true` returns `200`
* analytical -- `$count=true` returns `400 Not supported: $count on entity with
  annotation @Capabilities.CountRestrictions.Countable: false`

The analytical entity declares `Countable: false` in its own `$metadata`, so
this is discoverable rather than something to hard-code. No relational asset in
the scan declared `CountRestrictions`.

---

## What changed

### New module -- `odata_filter.py`

There was previously **no `$filter` validation at all**: `filter` was accepted
as a bare string capped at 500 characters and passed through to the wire. This
release adds a validator so that a bad expression becomes an actionable message
instead of an opaque `400`.

* the three string functions, composing freely with comparison terms via
  `and` / `or` / `not` / `()`
* field names checked against the asset's live `$metadata`
* string functions rejected on non-text columns, naming the type
* `substringof` rejected with a pointer to `contains`

The validator **fails soft**: if `$metadata` cannot be fetched, field-level
checks are skipped and only grammar is enforced, so a failed metadata lookup
never blocks a query that would have worked.

### Single quotes are rejected, never escaped

The API documents that values containing single quotes cannot be used, and does
not accept the OData `''` doubling escape. Interpolating a model-supplied value
containing a quote is an injection path, so such values are refused outright --
including the `''` form, which would otherwise parse as two adjacent literals.
The same restriction is enforced on input-parameter / variable values.

The error names the *value* as unrepresentable rather than blaming the field or
the asset, so the agent corrects the right thing.

### Federated lineage produces a recoverable error

If any source in an asset's lineage is federated rather than replicated, the API
narrows `$filter` to `eq`/`and`/`or`/`()` for that asset and drops `$top` and
`$skip`. Capability therefore varies **per asset, not per tenant**, and is not
knowable from the expression.

1.6.0 executes optimistically and maps the failure into a message naming the
limitation and showing an equality-filter retry. A capability-probe layer is
deliberately **not** built here -- it belongs on the SDK v2 foundations rather
than on code about to be rewritten.

### `$count` no longer sent on analytical requests

`query_analytical_data` was emitting `$count=true`, which fails the entire
query. The argument is now honoured by counting the returned rows, labelled as
covering the current page only.

### `dwc` path sweep

`/api/v1/dwc/` is deprecated in favour of `/api/v1/datasphere/`. Swept from
source and planning docs.

Two files were **deliberately left alone**: `OAUTH_VALIDATION_SUMMARY.md` and
one line of `REPOSITORY_TOOLS_INVESTIGATION.md` record endpoints alongside the
HTTP status codes they actually returned. Rewriting those paths would turn a
test record into a claim about a URL nobody tested.

### Tool descriptions

The two Consumption-API tools that accept a filter now advertise the functions,
the case-sensitivity behaviour, the single-quote restriction, and the
federated-asset caveat. `query_analytical_data`'s example previously used double
quotes around a value (`Currency eq "USD"`), which OData rejects -- it had been
teaching the model invalid syntax.

Catalog-API tools were left unchanged: they are a different surface, and the
rules verified here do not necessarily apply to them.

### README

The time-bound `[!IMPORTANT]` advisory added in `c1eca78` for the 1.5.2 MCP SDK
pin has been removed.

---

## Tests

`tests/test_odata_filter.py` -- 57 cases covering the work-order matrix:
the three functions, composition with comparison terms, single-quote rejection
including the `''` form, non-filterable and non-text types, unknown and
wrong-case field names, and the federated-subset detection and message.

Full suite: **104 passed**.

These are written against the 1.5.x line deliberately. The SDK v2 port inherits
them as regression coverage and must keep them green.

---

## Not in this release

No MCP SDK v2 port; the `mcp>=1.28,<2` pin is unchanged. No per-asset capability
layer -- see the port spec, which should keep "capability descriptor keyed by
asset" in mind as a future consumer when `ttlMs` / `cacheScope` are reworked out
of `CacheManager`.
