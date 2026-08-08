"""Validation-hardening tests (v1.7.0).

Written against the 1.x line deliberately: the SDK v2 port inherits these as
regression coverage and must keep them green.

The audit that motivated this release found two ways validation can exist and
silently not run. Both are pinned here, because a passing suite previously
asserted correctness that wasn't there:

* the tool registry and the ``has_validator`` list were maintained separately
  and drifted, disabling rules for two tools;
* ``allowed_values`` was only consulted by ``_validate_enum``, so rules written
  as ``STRING`` + ``allowed_values`` enforced nothing.

Run with:  pytest tests/test_input_validation.py -v
"""

import asyncio
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ.setdefault("USE_MOCK_DATA", "true")

from auth.input_validator import InputValidator  # noqa: E402
from auth.tool_validators import PATH_SEGMENT_PATTERN, ToolValidators  # noqa: E402


@pytest.fixture(scope="module")
def validator():
    return InputValidator(strict_mode=True)


@pytest.fixture(scope="module")
def advertised_tools():
    """Every tool the server advertises with the widest profile."""
    os.environ["DATASPHERE_TOOL_PROFILE"] = "full"
    os.environ["DATASPHERE_EXPOSE_DIAGNOSTICS"] = "true"
    import sap_datasphere_mcp_server as server
    return asyncio.run(server.handle_list_tools())


def _rules_for(tool_name):
    return {r.param_name: r for r in ToolValidators.get_validator_rules(tool_name)}


# ── Registry integrity ───────────────────────────────────────────────────────


def test_registry_is_the_single_source_of_truth():
    """has_validator and get_all_tool_names must both derive from the registry.

    They were separate lists once, and the drift silently disabled validation
    for analyze_column_distribution and find_assets_by_column.
    """
    registry = set(ToolValidators._rule_builders().keys())
    assert set(ToolValidators.get_all_tool_names()) == registry
    for name in registry:
        assert ToolValidators.has_validator(name), name


@pytest.mark.parametrize(
    "tool", ["analyze_column_distribution", "find_assets_by_column"]
)
def test_previously_orphaned_tools_are_enforced(tool):
    """Regression: these had rules that has_validator never acknowledged."""
    assert ToolValidators.has_validator(tool)
    assert _rules_for(tool), f"{tool} should have rules"


def test_every_registered_tool_builds_rules_without_error():
    for name in ToolValidators.get_all_tool_names():
        assert ToolValidators.get_validator_rules(name), name


# ── Coverage guard: the failure mode that produced this release ──────────────


def test_every_tool_with_inputs_has_a_validator(advertised_tools):
    """A tool shipped without rules is the exact defect 1.7.0 fixes.

    This is the guard: adding a tool and forgetting its rules fails here rather
    than reaching a customer as unvalidated wire input.
    """
    missing = [
        t.name for t in advertised_tools
        if (t.inputSchema or {}).get("properties")
        and not ToolValidators.has_validator(t.name)
    ]
    assert not missing, f"tools advertised with inputs but no validation rules: {missing}"


def test_path_identifiers_are_all_constrained(advertised_tools):
    """Every identifier interpolated into a URL path must be pattern-bound.

    Query values are URL-encoded by the client and can only produce a bad
    request; path segments change what the request addresses.
    """
    PATH_PARAMS = {"space_id", "asset_id", "entity_name", "object_id", "asset_name"}
    unconstrained = []
    for tool in advertised_tools:
        props = (tool.inputSchema or {}).get("properties", {})
        rules = _rules_for(tool.name)
        for param in props:
            if param not in PATH_PARAMS:
                continue
            rule = rules.get(param)
            if rule is None:
                unconstrained.append(f"{tool.name}.{param} (no rule)")
            elif not rule.pattern and rule.validation_type.value not in ("space_id", "table_name"):
                unconstrained.append(f"{tool.name}.{param} (no pattern)")
    assert not unconstrained, f"unconstrained path identifiers: {unconstrained}"


# ── Traversal rejection ──────────────────────────────────────────────────────


HOSTILE = [
    "SPACE/../../admin",
    "../../etc/passwd",
    "A/B",
    "A?x=1",
    "A#frag",
    "A%2F..%2Fb",
    "A'B",
]


@pytest.mark.parametrize("value", HOSTILE)
def test_hostile_asset_id_rejected(validator, value):
    ok, errors = validator.validate_params(
        {"space_id": "DEMO_SALES", "asset_id": value, "entity_name": "E"},
        ToolValidators.get_validator_rules("query_relational_entity"),
    )
    assert not ok, f"{value!r} should be rejected"
    assert errors


@pytest.mark.parametrize("value", HOSTILE)
def test_hostile_space_id_rejected(validator, value):
    ok, _ = validator.validate_params(
        {"space_id": value, "asset_id": "A", "entity_name": "E"},
        ToolValidators.get_validator_rules("query_relational_entity"),
    )
    assert not ok, f"{value!r} should be rejected"


@pytest.mark.parametrize(
    "tool,params",
    [
        ("run_task_chain", {"space_id": "DEMO_SALES", "object_id": "CHAIN/../x"}),
        ("get_task_history", {"space_id": "DEMO_SALES", "object_id": "../x"}),
        ("get_asset_variables", {"space_id": "DEMO_SALES", "asset_id": "../x"}),
        ("list_relational_entities", {"space_id": "DEMO_SALES", "asset_id": "a/b"}),
        ("get_relational_odata_service", {"space_id": "DEMO_SALES", "asset_id": "a?b"}),
    ],
)
def test_traversal_rejected_across_newly_covered_tools(validator, tool, params):
    ok, _ = validator.validate_params(params, ToolValidators.get_validator_rules(tool))
    assert not ok


def test_legitimate_identifiers_still_accepted(validator):
    ok, errors = validator.validate_params(
        {
            "space_id": "DEMO_SALES",
            "asset_id": "ORDER_LINES",
            "entity_name": "ORDER_LINES",
            "top": 100,
        },
        ToolValidators.get_validator_rules("query_relational_entity"),
    )
    assert ok, errors


def test_real_world_asset_names_accepted(validator):
    """Names taken from the live test tenant catalog."""
    for asset in ["DEMO_Open_Lines", "DEMO_Report", "DEMO_PRODUCTS", "ORDER_LINES"]:
        ok, errors = validator.validate_params(
            {"space_id": "DEMO_SALES", "asset_id": asset},
            ToolValidators.get_validator_rules("get_asset_variables"),
        )
        assert ok, f"{asset}: {errors}"


# ── allowed_values must actually be enforced ─────────────────────────────────


@pytest.mark.parametrize(
    "tool,param,good,bad",
    [
        ("smart_query", "mode", "analytical", "evil"),
        ("get_task_log", "detail_level", "detailed", "nope"),
        ("get_catalog_metadata", "endpoint_type", "consumption", "bogus"),
    ],
)
def test_allowed_values_enforced_on_string_rules(validator, tool, param, good, bad):
    """Regression: allowed_values was only honoured by _validate_enum.

    get_catalog_metadata.endpoint_type is the pre-existing case -- it declared
    allowed_values and enforced nothing before 1.7.0.
    """
    base = {
        "smart_query": {"space_id": "DEMO_SALES", "query": "x"},
        "get_task_log": {"space_id": "DEMO_SALES", "log_id": 1},
        "get_catalog_metadata": {},
    }[tool]
    rules = ToolValidators.get_validator_rules(tool)

    ok, errors = validator.validate_params({**base, param: good}, rules)
    assert ok, errors

    ok, errors = validator.validate_params({**base, param: bad}, rules)
    assert not ok, f"{param}={bad!r} should be rejected"
    assert param in errors[0]


# ── The quoting backstop ─────────────────────────────────────────────────────


def test_seg_is_a_noop_for_legitimate_identifiers():
    from sap_datasphere_mcp_server import _seg
    for value in ["DEMO_SALES", "ORDER_LINES", "DEMO_Open_Lines", "DEMO_PRODUCTS"]:
        assert _seg(value) == value


@pytest.mark.parametrize(
    "value,must_not_contain",
    [("A/B", "/"), ("../x", "/"), ("A?x=1", "?"), ("A#f", "#"), ("A'B", "'")],
)
def test_seg_neutralises_structural_characters(value, must_not_contain):
    """Defence in depth: even if validation were bypassed, the value cannot
    escape its path segment."""
    from sap_datasphere_mcp_server import _seg
    assert must_not_contain not in _seg(value)


def test_no_unquoted_identifier_interpolation_remains():
    """Every path f-string must route identifiers through _seg().

    Covers inline f-strings passed straight to a connector call as well as
    assignments -- the first sweep only matched assignments and missed one.
    """
    import re
    src = open(os.path.join(os.path.dirname(__file__), "..",
                            "sap_datasphere_mcp_server.py")).read()
    interesting = re.compile(
        r'\b(endpoint|url|search_endpoint|metadata_endpoint)\s*=\s*f"'
        r'|(connector\.(get|post|put|delete)|_make_request)\(\s*f"'
    )
    raw_identifier = re.compile(
        r'/\{(space_id|asset_id|entity_name|object_id|space_id_current|asset_name)\}'
    )
    offenders = [
        line.strip()[:90]
        for line in src.split("\n")
        if interesting.search(line) and raw_identifier.search(line)
    ]
    assert not offenders, f"unquoted path interpolation: {offenders}"


# ── The deliberately-unwired validator ───────────────────────────────────────


def test_parameter_validator_exists_but_is_not_wired():
    """validate_parameter_value guards a URL form no handler builds.

    Pinned so its status is a decision on record rather than a latent surprise:
    if someone implements (<param>='<value>')/Set, this test should be updated
    at the same time as the wiring.
    """
    import odata_filter
    import sap_datasphere_mcp_server as server

    assert hasattr(odata_filter, "validate_parameter_value")
    assert not hasattr(server, "validate_parameter_value"), (
        "validate_parameter_value is imported into the server, which implies a "
        "wiring that does not exist"
    )
    # Look for the URL form being *built*, i.e. inside an f-string, rather than
    # merely mentioned -- the explanatory comment in the server names it too.
    import re
    src = open(os.path.join(os.path.dirname(__file__), "..",
                            "sap_datasphere_mcp_server.py")).read()
    built = [
        line.strip()[:90]
        for line in src.split("\n")
        if re.search(r'f"[^"]*\)/Set', line)
    ]
    assert not built, (
        f"a parameterised-asset URL is now built ({built}) -- wire "
        "validate_parameter_value into it and update this test"
    )
