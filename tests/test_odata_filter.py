"""Tests for $filter validation on the Datasphere Consumption API (v1.6.0).

Covers the 1.6.0 work-order matrix. Written against the 1.5.x line
deliberately: the MCP SDK v2 port inherits these as regression coverage and
must keep them green.

Run with:  pytest tests/test_odata_filter.py -v
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from odata_filter import (  # noqa: E402
    COMPARISON_OPERATORS,
    FEDERATED_SAFE_OPERATORS,
    STRING_FUNCTIONS,
    FilterValidationError,
    federated_filter_error,
    uses_beyond_federated_subset,
    validate_filter_expression,
    validate_parameter_value,
)

# Stand-in for an asset's $metadata.
FIELDS = ["Product", "Country", "Value", "Status", "Notes", "Payload", "Ident"]
TYPES = {
    "Product": "Edm.String",
    "Country": "Edm.String",
    "Value": "Edm.Decimal",
    "Status": "Edm.String",
    "Notes": "cds.LargeString",
    "Payload": "Edm.Binary",
    "Ident": "Edm.Guid",
}


# ── The three string functions ───────────────────────────────────────────────


@pytest.mark.parametrize("func", sorted(STRING_FUNCTIONS))
def test_string_functions_accepted(func):
    expr = f"{func}(Product,'TV')"
    assert validate_filter_expression(expr, FIELDS, TYPES) == expr


@pytest.mark.parametrize(
    "expr",
    [
        "startswith(Product,'TV') and Country eq 'US'",
        "endswith(Product,'HD') or Country eq 'DE'",
        "(startswith(Product,'TV') or contains(Product,'Radio')) and Value gt 100",
        "not (contains(Country,'U'))",
        "contains(Product,'TV') and not (Status eq 'VOID')",
    ],
)
def test_string_functions_compose_with_comparisons(expr):
    """Function-form and comparison-form terms must combine via and/or/not/()."""
    assert validate_filter_expression(expr, FIELDS, TYPES) == expr


def test_exact_syntax_from_work_order():
    expr = "startswith(Product,'TV') and Country eq 'US'"
    assert validate_filter_expression(expr, FIELDS, TYPES) == expr


def test_substringof_v2_form_rejected_with_pointer_to_contains():
    """substringof is OData v2 and is not what shipped."""
    with pytest.raises(FilterValidationError) as exc:
        validate_filter_expression("substringof('TV',Product)", FIELDS, TYPES)
    assert "contains(" in str(exc.value)


def test_unsupported_function_rejected():
    with pytest.raises(FilterValidationError) as exc:
        validate_filter_expression("tolower(Product) eq 'tv'", FIELDS, TYPES)
    assert "tolower" in str(exc.value)


@pytest.mark.parametrize("expr", ["startswith(Product)", "contains(Product,'a','b')"])
def test_string_function_arity_enforced(expr):
    with pytest.raises(FilterValidationError):
        validate_filter_expression(expr, FIELDS, TYPES)


def test_string_function_second_arg_must_be_quoted():
    with pytest.raises(FilterValidationError):
        validate_filter_expression("startswith(Product,TV)", FIELDS, TYPES)


# ── Single quotes: reject, never escape ──────────────────────────────────────


def test_value_with_embedded_quote_rejected():
    with pytest.raises(FilterValidationError):
        validate_filter_expression("Country eq 'O'Brien'", FIELDS, TYPES)


def test_odata_quote_doubling_rejected_explicitly():
    """'' is the OData escape, and this API does not accept it.

    Without this check "'O''Brien'" would parse as two adjacent literals --
    the shape an injection attempt takes.
    """
    with pytest.raises(FilterValidationError) as exc:
        validate_filter_expression("Country eq 'O''Brien'", FIELDS, TYPES)
    message = str(exc.value).lower()
    assert "does not support" in message
    assert "escape" in message


def test_quote_rejection_message_blames_the_value_not_the_field():
    """The model must learn the value is unrepresentable, not that it picked
    the wrong field or asset."""
    with pytest.raises(FilterValidationError) as exc:
        validate_filter_expression("Country eq 'O''Brien'", FIELDS, TYPES)
    assert "O'Brien" in str(exc.value)


def test_unterminated_literal_rejected():
    with pytest.raises(FilterValidationError):
        validate_filter_expression("Country eq 'US", FIELDS, TYPES)


def test_parameter_value_rejects_single_quote():
    with pytest.raises(FilterValidationError) as exc:
        validate_parameter_value("Product_Name", "O'Brien")
    assert "Product_Name" in str(exc.value)


def test_parameter_value_rejects_double_quote():
    with pytest.raises(FilterValidationError):
        validate_parameter_value("Product_Name", 'say "hi"')


def test_parameter_value_accepts_ordinary_text():
    assert validate_parameter_value("Product_Name", "Product A") == "Product A"


# ── Non-filterable types ─────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "field,type_name",
    [("Notes", "cds.LargeString"), ("Payload", "Edm.Binary"), ("Ident", "Edm.Guid")],
)
def test_non_filterable_types_rejected_naming_the_type(field, type_name):
    with pytest.raises(FilterValidationError) as exc:
        validate_filter_expression(f"contains({field},'x')", FIELDS, TYPES)
    assert type_name in str(exc.value)


def test_non_filterable_type_also_rejected_in_comparison_form():
    with pytest.raises(FilterValidationError) as exc:
        validate_filter_expression("Notes eq 'x'", FIELDS, TYPES)
    assert "cds.LargeString" in str(exc.value)


@pytest.mark.parametrize("func", sorted(STRING_FUNCTIONS))
def test_string_function_on_numeric_column_rejected(func):
    """Confirmed against example-tenant (2026-08-07): the API answers
    contains(<Edm.Decimal>,'x') with HTTP 400 "The type 'Edm.Decimal' is not
    compatible to 'Edm.String'". Caught locally to save the round trip."""
    with pytest.raises(FilterValidationError) as exc:
        validate_filter_expression(f"{func}(Value,'10')", FIELDS, TYPES)
    message = str(exc.value)
    assert "Edm.Decimal" in message
    assert "text columns" in message


def test_string_function_message_suggests_an_operator_instead():
    with pytest.raises(FilterValidationError) as exc:
        validate_filter_expression("contains(Value,'10')", FIELDS, TYPES)
    assert "Value eq" in str(exc.value)


def test_large_text_surfacing_as_edm_string_stays_filterable():
    """cds.LargeString surfaces as Edm.String in $metadata, and the observed
    rejection mechanism is type-incompatibility with the string literal -- so
    it filters. The documentation's table implies otherwise; behaviour wins.
    Unverified directly: no LargeString column exists on the probe tenant."""
    types = dict(TYPES, Description="Edm.String")
    expr = "contains(Description,'widget')"
    assert validate_filter_expression(expr, FIELDS + ["Description"], types) == expr


def test_geometry_types_rejected():
    types = dict(TYPES, Shape="ST_GEOMETRY")
    with pytest.raises(FilterValidationError) as exc:
        validate_filter_expression("Shape eq 'x'", FIELDS + ["Shape"], types)
    assert "ST_GEOMETRY" in str(exc.value)


# ── Field-name validation against $metadata ──────────────────────────────────


def test_unknown_field_rejected():
    with pytest.raises(FilterValidationError) as exc:
        validate_filter_expression("Nonexistent eq 'x'", FIELDS, TYPES)
    assert "Nonexistent" in str(exc.value)


def test_unknown_field_in_string_function_rejected():
    with pytest.raises(FilterValidationError):
        validate_filter_expression("contains(Nonexistent,'x')", FIELDS, TYPES)


def test_wrong_case_field_reports_the_correct_spelling():
    with pytest.raises(FilterValidationError) as exc:
        validate_filter_expression("product eq 'TV'", FIELDS, TYPES)
    assert "'Product'" in str(exc.value)


def test_unquoted_value_is_caught_as_unknown_field():
    """The SAP documentation's own example, `Country eq US`, is malformed."""
    with pytest.raises(FilterValidationError):
        validate_filter_expression("Country eq US", FIELDS, TYPES)


def test_without_metadata_only_grammar_is_enforced():
    """Field checks are skipped when $metadata is unavailable, so a query that
    would have worked is not blocked by a failed metadata lookup."""
    expr = "contains(WhoKnows,'x')"
    assert validate_filter_expression(expr) == expr
    with pytest.raises(FilterValidationError):
        validate_filter_expression("substringof('x',WhoKnows)")


# ── Grammar ──────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("op", sorted(COMPARISON_OPERATORS))
def test_all_comparison_operators_accepted(op):
    expr = f"Value {op} 10"
    assert validate_filter_expression(expr, FIELDS, TYPES) == expr


@pytest.mark.parametrize("expr", ["(Country eq 'US'", "Country eq 'US')"])
def test_unbalanced_parentheses_rejected(expr):
    with pytest.raises(FilterValidationError):
        validate_filter_expression(expr, FIELDS, TYPES)


def test_empty_filter_rejected():
    with pytest.raises(FilterValidationError):
        validate_filter_expression("   ", FIELDS, TYPES)


def test_junk_token_rejected():
    with pytest.raises(FilterValidationError):
        validate_filter_expression("Country ~= 'US'", FIELDS, TYPES)


# ── Federated (non-replicated) lineage degradation ───────────────────────────


@pytest.mark.parametrize(
    "expr",
    [
        "startswith(Product,'TV')",
        "contains(Product,'TV')",
        "endswith(Product,'TV')",
        "Value gt 10",
        "Country ne 'US'",
    ],
)
def test_expressions_beyond_the_federated_subset_are_detected(expr):
    assert uses_beyond_federated_subset(expr) is True


@pytest.mark.parametrize(
    "expr",
    [
        "Country eq 'US'",
        "Country eq 'US' and Status eq 'ACTIVE'",
        "(Country eq 'US') or (Status eq 'NEW')",
    ],
)
def test_equality_only_expressions_are_federated_safe(expr):
    assert uses_beyond_federated_subset(expr) is False


def test_federated_subset_is_the_documented_one():
    assert FEDERATED_SAFE_OPERATORS == {"eq", "and", "or"}


def test_federated_error_is_actionable():
    """The message must name the limitation and show a retry, so the agent
    corrects rather than looping on the same rejected request."""
    message = federated_filter_error(
        "startswith(Product,'TV')", "SALES", "ORDERS"
    )
    assert "SALES/ORDERS" in message
    assert "startswith(Product,'TV')" in message
    for token in ("eq", "and", "or"):
        assert token in message
    assert "federated" in message.lower()
    assert "retry" in message.lower()


def test_federated_error_mentions_top_and_skip():
    """$top/$skip are lost under the same condition as the filter operators."""
    message = federated_filter_error("Value gt 1", "SALES", "ORDERS")
    assert "$top" in message and "$skip" in message


def test_largestring_is_not_claimed_string_compatible():
    """The two type tables must not contradict each other.

    check_field_filterable() runs before _check_field_string_compatible(), so a
    type in NON_FILTERABLE_TYPES can never reach the string-compatibility check.
    Listing cds.largestring in both asserted a path that cannot execute.
    """
    from odata_filter import NON_FILTERABLE_TYPES, STRING_COMPATIBLE_TYPES
    overlap = set(NON_FILTERABLE_TYPES) & STRING_COMPATIBLE_TYPES
    assert not overlap, f"unreachable: rejected before the string check: {overlap}"
