# Changelog - v1.5.0 (OData V4 annotation parsing)

**Release Date:** 2026-04-18

## Bug Fix: Restore empty labels and dimensions/measures on Datasphere consumption APIs

SAP Datasphere's consumption `$metadata` is OData **4.0**. The semantic
information that used to live in V2 `sap:*` attributes (`sap:label`,
`sap:aggregation-role`, `sap:dimension`, `sap:aggregation`, `sap:unit`,
`sap:hierarchy`, `sap:semantics`) is now emitted as `<Annotation Term="…">`
elements, almost always inside external
`<Annotations Target="<Schema>.<EntityType>/<Property>">` blocks at the schema
level. The OData V4 envelope was already parsed correctly (so column names,
types and keys came back fine) but every semantic field was still read as a
legacy V2 attribute — and therefore always `None`.

Observed on the test tenant (`DEMO_SALES / ORDER_LINES`) before
the fix:

- `get_relational_metadata` — all 18 columns returned, every `label` empty.
- `get_analytical_metadata` — all 18 properties returned, `dimensions: []`,
  `measures: []`, `hierarchies: []`.

After the fix the same calls return populated labels and the 17 dimensions /
1 measure that the model actually declares.

---

## What changed

### New module — `odata_v4_annotations.py`

A small, dependency-free helper that reads SAP OData-V4 vocabulary
annotations and falls back to the legacy V2 attributes:

| V2 attribute (gone in V4)       | V4 annotation Term (matched by suffix)           |
|---------------------------------|--------------------------------------------------|
| `sap:label`                     | `*.Label` (e.g. `Common.Label`)                  |
| `sap:dimension`                 | `*.Dimension` with `Bool="true"`                 |
| `sap:aggregation-role`          | `*.Dimension` / `*.measure` / `*.AggregationRole`|
| `sap:aggregation`               | `*.DefaultAggregation`                           |
| `sap:unit`                      | `*.Unit` / `*.ISOCurrency`                       |
| `sap:hierarchy`                 | `*.RecursiveHierarchy` / `*Hierarchy*`           |
| `sap:semantics`                 | `Common.*` / `Measures.*` semantic terms         |

The parser handles **both** inline `<Annotation>` children of `<Property>`
**and** external `<Annotations Target="…">` blocks — Datasphere analytic
models use the external form.

### Wired into the existing metadata tools

`sap_datasphere_mcp_server.py` parsing blocks now route through
`make_semantics_extractor(root, namespaces)` instead of reading
`{http://www.sap.com/Protocols/SAPData}*` attributes:

- `get_consumption_metadata` — column `label` annotations
- `get_analytical_metadata` — `dimensions`, `measures`, `aggregation`, `unit`,
  `hierarchy`
- `get_relational_metadata` — column `label` and `semantics`
- `get_analytical_model` (OData service-doc path) — dimension / measure split

The stale tool description on `get_analytical_model` that still advertised
`sap:aggregation-role='dimension'/'measure'` has been updated.

### V2 fallback is preserved

The legacy `sap:*` attribute read remains as a fallback after the annotation
walk, so any still-V2 source (older systems, on-premise ABAP-side metadata)
continues to parse without change.

---

## Tests

`tests/test_odata_v4_annotations.py` — 7 cases covering:

- Real CSDL fixtures captured live from the test tenant
  (`tests/fixtures/odata_v4_{analytical,relational}_ORDER_LINES.xml`).
- `ORDER_ID`/`LINE_NO` key preservation and labelling on the relational model.
- 17 dimensions + the single `NET_AMOUNT` measure on the analytical model.
- Synthetic V2-attribute CSDL parsing via the fallback path.
- Empty-property defaults.

Full suite: **47 passed**, no regressions in PII masking or other tooling.

---

## Reproduction (was broken in ≤ 1.4.0)

```python
get_relational_metadata(space_id="DEMO_SALES", asset_id="ORDER_LINES")
# before: every column.label is null
# after:  column.label populated where the tenant publishes one
#         (e.g. ORDER_ID → "Order Identifier")

get_analytical_metadata(space_id="DEMO_SALES", asset_id="ORDER_LINES")
# before: dimensions: [], measures: []
# after:  17 dimensions, 1 measure (NET_AMOUNT)
```

---

## Scope guardrails

The OData 4.0 envelope namespaces were already correct and were not touched.
No other tools, transports, or behaviours changed. No dependencies added —
the new helper is stdlib-only.
