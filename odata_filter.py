"""Validation for OData ``$filter`` expressions on the Datasphere Consumption API.

The Consumption API accepts a deliberately small filter grammar. This module
validates model-supplied expressions against it *before* anything reaches the
wire, so that a bad expression becomes a clear, actionable message rather than
a bare HTTP 400 the agent cannot learn from.

Supported grammar (SAP Datasphere, Consuming Data via the OData API):

* comparison: ``eq ne gt ge lt le``
* string functions: ``startswith(<field>,'<value>')``, ``endswith(...)``,
  ``contains(...)``  -- these are the OData **v4** spellings; the v2
  ``substringof`` form is not accepted by this API
* logical: ``and`` ``or`` ``not``, grouping with ``()``

Two restrictions are enforced rather than worked around:

1. **Single quotes in values are rejected, not escaped.** The API documents
   that "values containing single quotes cannot be used", and does not accept
   the OData ``''`` doubling escape. Interpolating a model-supplied value that
   contains a quote is an injection path, so such values are refused outright.

2. **Field types that cannot be filtered are rejected early**, naming the type,
   so the caller learns the column is unusable rather than seeing a 400.

Note on per-asset capability: if any source in an asset's lineage is federated
rather than replicated, the API narrows ``$filter`` to ``eq``/``and``/``or``/``()``
for that asset only. That is not knowable from the expression alone, so it is
handled at execution time by mapping the failure -- see
``federated_filter_error``.
"""

import re
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

# ── Grammar ──────────────────────────────────────────────────────────────────

COMPARISON_OPERATORS = frozenset({"eq", "ne", "gt", "ge", "lt", "le"})
LOGICAL_OPERATORS = frozenset({"and", "or", "not"})
STRING_FUNCTIONS = frozenset({"startswith", "endswith", "contains"})

#: Operators still available when an asset has federated (non-replicated)
#: sources in its lineage. Everything else degrades for that asset only.
FEDERATED_SAFE_OPERATORS = frozenset({"eq", "and", "or"})

#: Literal constants permitted as operands.
_LITERAL_KEYWORDS = frozenset({"true", "false", "null"})

#: CDS / EDM types the Consumption API documents as not filterable. Values are
#: matched case-insensitively against both the CDS name and the Edm name the
#: type is surfaced as, since geometry types are overwritten to Edm.String.
NON_FILTERABLE_TYPES: Dict[str, str] = {
    "cds.largestring": "cds.LargeString",
    "cds.uuid": "cds.UUID",
    "cds.binary": "cds.Binary",
    "cds.largebinary": "cds.LargeBinary",
    "cds.hana.binary": "cds.hana.BINARY",
    "cds.hana.st_geometry": "ST_GEOMETRY",
    "cds.hana.st_point": "ST_POINT",
    "st_geometry": "ST_GEOMETRY",
    "st_point": "ST_POINT",
    "edm.binary": "Edm.Binary",
    "edm.guid": "Edm.Guid",
}

#: Types the three string functions accept. Applying them to anything else is
#: rejected by the API with "The type '<X>' is not compatible to 'Edm.String'"
#: (confirmed against example-tenant, 2026-08-07), so it is caught locally instead.
STRING_COMPATIBLE_TYPES = frozenset({
    "edm.string", "cds.string", "cds.largestring", "cds.hana.varchar",
    "cds.hana.nvarchar", "cds.hana.char", "cds.hana.nchar", "cds.hana.clob",
})

_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_/.]*$")
_NUMERIC_RE = re.compile(r"^-?\d+(\.\d+)?$")
_DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(T[\d:.]+(Z|[+-]\d{2}:\d{2})?)?$")

_LITERAL_PLACEHOLDER = "\x00LIT\x00"


class FilterValidationError(ValueError):
    """Raised when a ``$filter`` expression cannot be represented by this API.

    The message is written to be read by a model: it should make clear whether
    the problem is the *value*, the *field*, or the *operator*, so the agent
    can correct the right part rather than retrying blindly.
    """


# ── Literal scanning ─────────────────────────────────────────────────────────

def _scan_string_literals(expression: str) -> List[Tuple[int, int, str]]:
    """Return ``(start, end, value)`` for each single-quoted literal.

    Rejects unterminated literals and the OData ``''`` doubling escape. The
    doubling check is what stops ``'O''Brien'`` from being silently read as two
    adjacent literals, which is the shape an injection attempt would take.
    """
    spans: List[Tuple[int, int, str]] = []
    i, n = 0, len(expression)
    while i < n:
        if expression[i] != "'":
            i += 1
            continue
        j = i + 1
        while j < n and expression[j] != "'":
            j += 1
        if j >= n:
            raise FilterValidationError(
                "Unterminated quoted value in $filter: every text value must "
                "open and close with a single quote, e.g. Country eq 'US'."
            )
        if j + 1 < n and expression[j + 1] == "'":
            raise FilterValidationError(
                "This API does not support single quotes inside filter values, "
                "and does not accept the OData '' escape. A value such as "
                "\"O'Brien\" cannot be filtered on through the Consumption API "
                "at all. Filter on a different field, or use a value with no "
                "apostrophe."
            )
        spans.append((i, j, expression[i + 1:j]))
        i = j + 1
    return spans


def _strip_literals(expression: str) -> Tuple[str, List[str]]:
    """Replace quoted literals with a placeholder so structure can be parsed."""
    spans = _scan_string_literals(expression)
    if not spans:
        return expression, []
    out, values, cursor = [], [], 0
    for start, end, value in spans:
        out.append(expression[cursor:start])
        out.append(_LITERAL_PLACEHOLDER)
        values.append(value)
        cursor = end + 1
    out.append(expression[cursor:])
    return "".join(out), values


# ── Field checks ─────────────────────────────────────────────────────────────

def _normalise_type(type_name: str) -> str:
    return (type_name or "").strip().lower()


def check_field_filterable(
    field: str,
    field_types: Optional[Dict[str, str]],
) -> None:
    """Raise if ``field`` has a type the API refuses to filter on."""
    if not field_types:
        return
    declared = field_types.get(field)
    if declared is None:
        for known, known_type in field_types.items():
            if known.lower() == field.lower():
                declared = known_type
                break
    if declared is None:
        return
    key = _normalise_type(declared)
    if key in NON_FILTERABLE_TYPES:
        raise FilterValidationError(
            f"Field '{field}' has type {NON_FILTERABLE_TYPES[key]}, which the "
            f"Consumption API cannot filter on. Filter on a different column, "
            f"or retrieve the rows and narrow them afterwards."
        )


def _declared_type(field: str, field_types: Optional[Dict[str, str]]) -> Optional[str]:
    if not field_types:
        return None
    if field in field_types:
        return field_types[field]
    for known, known_type in field_types.items():
        if known.lower() == field.lower():
            return known_type
    return None


def _check_field_string_compatible(
    field: str,
    function_name: str,
    field_types: Optional[Dict[str, str]],
) -> None:
    """Raise if a string function is applied to a non-text column.

    The API answers this with HTTP 400 "The type 'Edm.Decimal' is not
    compatible to 'Edm.String'"; catching it locally saves the round trip and
    tells the model which column is at fault.
    """
    declared = _declared_type(field, field_types)
    if declared is None:
        return
    if _normalise_type(declared) not in STRING_COMPATIBLE_TYPES:
        raise FilterValidationError(
            f"{function_name}() only works on text columns, but '{field}' is "
            f"{declared}. Compare it with an operator instead, for example "
            f"\"{field} eq <value>\" or \"{field} gt <value>\"."
        )


def _check_field_known(field: str, known_fields: Optional[Sequence[str]]) -> None:
    """Raise if ``field`` is not present in the asset's metadata."""
    if not known_fields:
        return
    if field in known_fields:
        return
    lowered = {f.lower(): f for f in known_fields}
    if field.lower() in lowered:
        raise FilterValidationError(
            f"Unknown field '{field}' in $filter. Field names are "
            f"case-sensitive; this asset declares it as "
            f"'{lowered[field.lower()]}'."
        )
    sample = ", ".join(sorted(known_fields)[:12])
    raise FilterValidationError(
        f"Unknown field '{field}' in $filter. This asset's filterable fields "
        f"include: {sample}."
    )


# ── Expression validation ────────────────────────────────────────────────────

def _validate_string_function_calls(
    expression: str,
    known_fields: Optional[Sequence[str]],
    field_types: Optional[Dict[str, str]],
) -> str:
    """Validate every ``func(field,'value')`` call; return expression with calls blanked.

    Each call is replaced by a neutral token so the remaining structure can be
    checked without re-parsing the calls.
    """
    # No whitespace allowed between name and '(' so that "not (X eq 'Y')"
    # reads as grouping rather than as a call to a function named "not".
    pattern = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\(([^()]*)\)")
    result = expression
    while True:
        match = pattern.search(result)
        if match is None:
            return result
        name, args = match.group(1), match.group(2)
        lowered = name.lower()
        if lowered in LOGICAL_OPERATORS:
            # "not(X eq 'Y')" is grouping written without a space. Normalise it
            # so this iteration makes progress and the loop terminates.
            result = result[:match.end(1)] + " " + result[match.end(1):]
            continue
        if lowered not in STRING_FUNCTIONS:
            if lowered == "substringof":
                raise FilterValidationError(
                    "substringof() is the OData v2 form and is not supported "
                    "by this API. Use contains(Field,'value') instead."
                )
            raise FilterValidationError(
                f"Function '{name}' is not supported in $filter. This API "
                f"accepts only: " + ", ".join(sorted(STRING_FUNCTIONS)) + "."
            )
        parts = [p.strip() for p in args.split(",")]
        if len(parts) != 2:
            raise FilterValidationError(
                f"{lowered}() takes exactly two arguments: a field and a "
                f"quoted value, e.g. {lowered}(Product,'TV')."
            )
        field, value = parts
        if not _IDENTIFIER_RE.match(field):
            raise FilterValidationError(
                f"First argument to {lowered}() must be a field name, got "
                f"'{field}'. Correct form: {lowered}(Product,'TV')."
            )
        if value != _LITERAL_PLACEHOLDER:
            raise FilterValidationError(
                f"Second argument to {lowered}() must be a quoted text value, "
                f"e.g. {lowered}({field},'TV')."
            )
        _check_field_known(field, known_fields)
        check_field_filterable(field, field_types)
        _check_field_string_compatible(field, lowered, field_types)
        result = result[:match.start()] + _LITERAL_PLACEHOLDER + result[match.end():]


def _validate_tokens(
    expression: str,
    known_fields: Optional[Sequence[str]],
    field_types: Optional[Dict[str, str]],
) -> None:
    """Validate the comparison/logical skeleton left after functions are blanked."""
    spaced = expression.replace("(", " ( ").replace(")", " ) ")
    tokens = [t for t in spaced.split() if t]

    depth = 0
    for token in tokens:
        if token == "(":
            depth += 1
            continue
        if token == ")":
            depth -= 1
            if depth < 0:
                raise FilterValidationError(
                    "Unbalanced parentheses in $filter."
                )
            continue

    if depth != 0:
        raise FilterValidationError("Unbalanced parentheses in $filter.")

    expect_operand = True
    for token in tokens:
        if token in ("(", ")"):
            continue
        lowered = token.lower()

        if lowered in LOGICAL_OPERATORS:
            expect_operand = True
            continue
        if lowered in COMPARISON_OPERATORS:
            expect_operand = True
            continue

        # Anything else must be an operand: literal, number, or field name.
        if token == _LITERAL_PLACEHOLDER or _NUMERIC_RE.match(token) \
                or _DATETIME_RE.match(token) or lowered in _LITERAL_KEYWORDS:
            expect_operand = False
            continue

        if _IDENTIFIER_RE.match(token):
            _check_field_known(token, known_fields)
            check_field_filterable(token, field_types)
            expect_operand = False
            continue

        raise FilterValidationError(
            f"Unrecognised token '{token}' in $filter. Supported: "
            f"{', '.join(sorted(COMPARISON_OPERATORS))}; "
            f"{', '.join(sorted(STRING_FUNCTIONS))}(Field,'value'); "
            f"and/or/not with parentheses. Text values must be quoted, "
            f"e.g. Country eq 'US'."
        )


def validate_filter_expression(
    expression: str,
    known_fields: Optional[Iterable[str]] = None,
    field_types: Optional[Dict[str, str]] = None,
) -> str:
    """Validate a ``$filter`` expression, returning it unchanged if acceptable.

    ``known_fields`` and ``field_types`` come from the asset's ``$metadata``.
    When omitted, field-level checks are skipped and only the grammar and the
    quoting rules are enforced.

    Raises :class:`FilterValidationError` with a message intended to be shown
    to the model.
    """
    if expression is None:
        return expression
    text = expression.strip()
    if not text:
        raise FilterValidationError("$filter expression is empty.")

    fields = list(known_fields) if known_fields is not None else None

    stripped, _values = _strip_literals(text)
    blanked = _validate_string_function_calls(stripped, fields, field_types)
    _validate_tokens(blanked, fields, field_types)
    return expression


def validate_parameter_value(name: str, value: str) -> str:
    """Validate an input-parameter / variable value, e.g. ``(Product_Name='Product A')``.

    Carries the same quoting restriction as ``$filter``: the API documents that
    text values containing single or double quotes are not supported.
    """
    if value is None:
        return value
    if "'" in value:
        raise FilterValidationError(
            f"Input parameter '{name}' contains a single quote. This API does "
            f"not support quotes in parameter values, and offers no escape "
            f"form, so this value cannot be passed at all."
        )
    if '"' in value:
        raise FilterValidationError(
            f"Input parameter '{name}' contains a double quote, which this API "
            f"does not support in parameter values."
        )
    return value


# ── Execution-time capability mapping ────────────────────────────────────────

def uses_beyond_federated_subset(expression: str) -> bool:
    """True if ``expression`` needs more than a federated asset can serve.

    Federated (non-replicated) lineage narrows ``$filter`` to ``eq``/``and``/
    ``or``/``()``. Used to explain a failure after the fact, not to pre-empt it
    -- lineage is not knowable from the expression.
    """
    if not expression:
        return False
    lowered = expression.lower()
    if any(f"{fn}(" in lowered.replace(" ", "") for fn in STRING_FUNCTIONS):
        return True
    tokens = {t.strip("()") for t in lowered.split()}
    disallowed = (COMPARISON_OPERATORS | LOGICAL_OPERATORS) - FEDERATED_SAFE_OPERATORS
    return bool(tokens & disallowed)


def federated_filter_error(expression: str, space_id: str, asset_id: str) -> str:
    """Message for a filter rejected because the asset has federated sources."""
    return (
        f"The filter was rejected by {space_id}/{asset_id}.\n\n"
        f"This usually means at least one source in the asset's lineage is "
        f"federated rather than replicated into SAP Datasphere. For those "
        f"assets the API supports only 'eq', 'and', 'or' and parentheses in "
        f"$filter -- startswith/endswith/contains, and the comparison "
        f"operators ne/gt/ge/lt/le, are unavailable, as are $top and $skip.\n\n"
        f"Rejected expression:\n  {expression}\n\n"
        f"Retry with an equality filter, for example:\n"
        f"  Country eq 'US' and Status eq 'ACTIVE'\n\n"
        f"If you need partial matching on this asset, retrieve a page of rows "
        f"and narrow them yourself."
    )
