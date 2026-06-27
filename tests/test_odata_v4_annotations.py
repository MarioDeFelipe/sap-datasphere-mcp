"""Unit tests for odata_v4_annotations.

Validates that the V4 annotation parser:
  * extracts ``Common.Label`` strings from external ``<Annotations Target=…>``
    blocks on the real Datasphere consumption fixtures
    (DEMO_SALES/ORDER_LINES captured live from example-tenant, 2026-06-27);
  * resolves ``Analytics.Dimension`` / ``Analytics.measure`` Bool flags to
    populated dimensions and measures;
  * still parses V2-era ``sap:*`` attributes via the legacy fallback.

Run with:  pytest tests/test_odata_v4_annotations.py -v
"""

import os
import sys
import xml.etree.ElementTree as ET

# Ensure repo root is on sys.path so we can import the helper directly.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from odata_v4_annotations import (  # noqa: E402
    SAP_DATA_NS,
    extract_property_semantics,
    make_semantics_extractor,
)


FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
NS = {
    "edmx": "http://docs.oasis-open.org/odata/ns/edmx",
    "edm":  "http://docs.oasis-open.org/odata/ns/edm",
}


def _load(name):
    return ET.parse(os.path.join(FIXTURE_DIR, name)).getroot()


# ─────────────────────────────────────────────────────────────────────────────
# Real-fixture tests — DEMO_SALES / ORDER_LINES on example-tenant
# ─────────────────────────────────────────────────────────────────────────────


def test_relational_fixture_labels_non_empty():
    root = _load("odata_v4_relational_ORDER_LINES.xml")
    get_sem = make_semantics_extractor(root, NS)
    entity_type = root.find(".//edm:EntityType", NS)
    assert entity_type.get("Name") == "ORDER_LINES"

    labels = {
        prop.get("Name"): get_sem(prop, entity_type)["label"]
        for prop in entity_type.findall("edm:Property", NS)
    }
    # The fixture's real key columns must carry labels
    assert labels["ORDER_ID"] == "Order Identifier"
    assert labels["LINE_NO"] == "Order Line Number"
    # At least the majority of columns must be labeled — bug was 0 labels
    labeled = [n for n, lbl in labels.items() if lbl]
    assert len(labeled) >= 10, f"expected many labels, got {labeled!r}"


def test_relational_fixture_keys_preserved():
    root = _load("odata_v4_relational_ORDER_LINES.xml")
    entity_type = root.find(".//edm:EntityType", NS)
    key_names = [
        ref.get("Name")
        for ref in entity_type.findall("edm:Key/edm:PropertyRef", NS)
    ]
    assert key_names == ["ORDER_ID", "LINE_NO"]


def test_analytical_fixture_dimensions_and_measures_non_empty():
    """Regression for the empty-dimensions/empty-measures bug."""
    root = _load("odata_v4_analytical_ORDER_LINES.xml")
    get_sem = make_semantics_extractor(root, NS)
    entity_type = root.find(".//edm:EntityType", NS)
    assert entity_type.get("Name") == "ORDER_LINES"

    dims, meas = [], []
    for prop in entity_type.findall("edm:Property", NS):
        sem = get_sem(prop, entity_type)
        if sem["is_dimension"]:
            dims.append(prop.get("Name"))
        if sem["is_measure"]:
            meas.append(prop.get("Name"))

    assert dims, "expected at least one dimension, got none — V4 parser regressed"
    assert meas, "expected at least one measure, got none — V4 parser regressed"
    # The single measure in this fixture is NET_AMOUNT (Analytics.measure Bool=true)
    assert "NET_AMOUNT" in meas
    # A couple of known dimensions
    for expected in ("ORDER_ID", "PRODUCT_CODE", "PLANT"):
        assert expected in dims, f"missing dimension {expected!r}"


def test_analytical_fixture_dimension_labels_populated():
    root = _load("odata_v4_analytical_ORDER_LINES.xml")
    get_sem = make_semantics_extractor(root, NS)
    entity_type = root.find(".//edm:EntityType", NS)
    sem_by_name = {
        prop.get("Name"): get_sem(prop, entity_type)
        for prop in entity_type.findall("edm:Property", NS)
    }
    assert sem_by_name["ORDER_ID"]["label"] == "Order Identifier"
    assert sem_by_name["PRODUCT_CODE"]["label"] == "Product Code"


def test_analytical_fixture_dimension_count_matches_fixture():
    """All 17 dimension annotations in the fixture must be resolved."""
    root = _load("odata_v4_analytical_ORDER_LINES.xml")
    get_sem = make_semantics_extractor(root, NS)
    entity_type = root.find(".//edm:EntityType", NS)
    dims = [
        prop.get("Name")
        for prop in entity_type.findall("edm:Property", NS)
        if get_sem(prop, entity_type)["is_dimension"]
    ]
    # The live fixture marks every property except NET_AMOUNT as a dimension.
    assert len(dims) == 17


# ─────────────────────────────────────────────────────────────────────────────
# V2 fallback — synthetic CSDL with legacy sap:* attributes
# ─────────────────────────────────────────────────────────────────────────────


V2_XML = """\
<edmx:Edmx Version="1.0"
           xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx">
  <edmx:DataServices>
    <Schema Namespace="LegacyService"
            xmlns="http://docs.oasis-open.org/odata/ns/edm"
            xmlns:sap="{sap}">
      <EntityType Name="LEGACY_FACT">
        <Property Name="REGION" Type="Edm.String" sap:label="Region"
                  sap:aggregation-role="dimension"/>
        <Property Name="REVENUE" Type="Edm.Decimal" sap:label="Revenue"
                  sap:aggregation-role="measure"
                  sap:aggregation="sum" sap:unit="USD"/>
      </EntityType>
    </Schema>
  </edmx:DataServices>
</edmx:Edmx>
""".format(sap=SAP_DATA_NS)


def test_v2_fallback_resolves_label_and_roles():
    root = ET.fromstring(V2_XML)
    get_sem = make_semantics_extractor(root, NS)
    entity_type = root.find(".//edm:EntityType", NS)
    by_name = {
        prop.get("Name"): get_sem(prop, entity_type)
        for prop in entity_type.findall("edm:Property", NS)
    }
    assert by_name["REGION"]["label"] == "Region"
    assert by_name["REGION"]["is_dimension"] is True
    assert by_name["REVENUE"]["label"] == "Revenue"
    assert by_name["REVENUE"]["is_measure"] is True
    assert by_name["REVENUE"]["aggregation"] == "sum"
    assert by_name["REVENUE"]["unit"] == "USD"


def test_extract_property_semantics_unknown_prop_returns_defaults():
    """No annotations + no V2 attrs → defaults across the board."""
    root = ET.fromstring(
        '<Schema xmlns="http://docs.oasis-open.org/odata/ns/edm" Namespace="X">'
        '<EntityType Name="E"><Property Name="P" Type="Edm.String"/></EntityType>'
        '</Schema>'
    )
    entity_type = root.find("edm:EntityType", NS)
    prop = entity_type.find("edm:Property", NS)
    sem = extract_property_semantics(prop, "E", "X", root, NS)
    assert sem["label"] is None
    assert sem["is_dimension"] is False
    assert sem["is_measure"] is False
    assert sem["terms"] == []
