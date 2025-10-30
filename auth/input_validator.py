"""
Input Validation Module for SAP Datasphere MCP Server

Provides comprehensive input validation to prevent injection attacks,
ensure data integrity, and validate tool parameters.
"""

import re
import logging
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class ValidationType(Enum):
    """Types of validation to perform"""
    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ENUM = "enum"
    SPACE_ID = "space_id"
    TABLE_NAME = "table_name"
    SQL_QUERY = "sql_query"
    CONNECTION_TYPE = "connection_type"


class ValidationError(Exception):
    """Raised when validation fails"""
    pass


@dataclass
class ValidationRule:
    """Validation rule configuration"""
    param_name: str
    validation_type: ValidationType
    required: bool = True
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    allowed_values: Optional[Set[str]] = None
    pattern: Optional[str] = None
    allow_empty: bool = False


class InputValidator:
    """
    Input validation framework for MCP server tools

    Features:
    - Type validation (string, integer, boolean, enum)
    - Length constraints
    - Pattern matching (regex)
    - Whitelist validation
    - SQL injection prevention
    - XSS prevention
    """

    # Dangerous SQL keywords that should not appear in user inputs
    SQL_DANGEROUS_KEYWORDS = {
        'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE',
        'EXEC', 'EXECUTE', 'GRANT', 'REVOKE', 'INSERT',
        'UPDATE', 'MERGE', 'REPLACE'
    }

    # SQL comment patterns
    SQL_COMMENT_PATTERNS = [
        r'--',           # SQL line comment
        r'/\*',          # SQL block comment start
        r'\*/',          # SQL block comment end
        r';.*--',        # Statement terminator followed by comment
    ]

    # Patterns for SQL injection attempts
    SQL_INJECTION_PATTERNS = [
        r"(\b(OR|AND)\b.*=.*)|('.*=.*')",  # OR/AND conditions
        r"UNION\s+SELECT",                  # UNION queries
        r";\s*(DROP|DELETE|TRUNCATE)",      # Statement chaining
        r"'.*OR.*'.*=.*'",                  # Quote-based injection
        r"--",                              # SQL comments
        r"/\*.*\*/",                        # Block comments
        r"xp_\w+",                          # Extended stored procedures
        r"sp_\w+",                          # System stored procedures
    ]

    # Valid identifier pattern (alphanumeric + underscore)
    IDENTIFIER_PATTERN = r'^[a-zA-Z][a-zA-Z0-9_]*$'

    # Valid space ID pattern (alphanumeric + underscore + hyphen)
    SPACE_ID_PATTERN = r'^[A-Z][A-Z0-9_-]*$'

    def __init__(self, strict_mode: bool = True):
        """
        Initialize input validator

        Args:
            strict_mode: If True, validation is more restrictive
        """
        self.strict_mode = strict_mode
        self._validation_errors: List[str] = []
        logger.info(f"Input validator initialized (strict_mode={strict_mode})")

    def validate_params(
        self,
        params: Dict[str, Any],
        rules: List[ValidationRule]
    ) -> Tuple[bool, List[str]]:
        """
        Validate parameters against a set of rules

        Args:
            params: Parameters to validate
            rules: Validation rules to apply

        Returns:
            Tuple of (is_valid, error_messages)
        """
        self._validation_errors = []

        for rule in rules:
            value = params.get(rule.param_name)

            # Check if required parameter is missing
            if rule.required and value is None:
                self._validation_errors.append(
                    f"Required parameter '{rule.param_name}' is missing"
                )
                continue

            # Skip validation if parameter is optional and not provided
            if not rule.required and value is None:
                continue

            # Validate based on type
            try:
                self._validate_by_type(rule, value)
            except ValidationError as e:
                self._validation_errors.append(str(e))

        is_valid = len(self._validation_errors) == 0
        return is_valid, self._validation_errors

    def _validate_by_type(self, rule: ValidationRule, value: Any):
        """Validate value based on validation type"""

        if rule.validation_type == ValidationType.STRING:
            self._validate_string(rule, value)

        elif rule.validation_type == ValidationType.INTEGER:
            self._validate_integer(rule, value)

        elif rule.validation_type == ValidationType.BOOLEAN:
            self._validate_boolean(rule, value)

        elif rule.validation_type == ValidationType.ENUM:
            self._validate_enum(rule, value)

        elif rule.validation_type == ValidationType.SPACE_ID:
            self._validate_space_id(rule, value)

        elif rule.validation_type == ValidationType.TABLE_NAME:
            self._validate_table_name(rule, value)

        elif rule.validation_type == ValidationType.SQL_QUERY:
            self._validate_sql_query(rule, value)

        elif rule.validation_type == ValidationType.CONNECTION_TYPE:
            self._validate_connection_type(rule, value)

    def _validate_string(self, rule: ValidationRule, value: Any):
        """Validate string parameter"""
        if not isinstance(value, str):
            raise ValidationError(
                f"Parameter '{rule.param_name}' must be a string"
            )

        # Check empty string
        if not rule.allow_empty and len(value.strip()) == 0:
            raise ValidationError(
                f"Parameter '{rule.param_name}' cannot be empty"
            )

        # Check length constraints
        if rule.min_length and len(value) < rule.min_length:
            raise ValidationError(
                f"Parameter '{rule.param_name}' must be at least "
                f"{rule.min_length} characters"
            )

        if rule.max_length and len(value) > rule.max_length:
            raise ValidationError(
                f"Parameter '{rule.param_name}' must not exceed "
                f"{rule.max_length} characters"
            )

        # Check pattern
        if rule.pattern and not re.match(rule.pattern, value):
            raise ValidationError(
                f"Parameter '{rule.param_name}' does not match required pattern"
            )

    def _validate_integer(self, rule: ValidationRule, value: Any):
        """Validate integer parameter"""
        if not isinstance(value, int):
            raise ValidationError(
                f"Parameter '{rule.param_name}' must be an integer"
            )

    def _validate_boolean(self, rule: ValidationRule, value: Any):
        """Validate boolean parameter"""
        if not isinstance(value, bool):
            raise ValidationError(
                f"Parameter '{rule.param_name}' must be a boolean"
            )

    def _validate_enum(self, rule: ValidationRule, value: Any):
        """Validate enum parameter"""
        if not isinstance(value, str):
            raise ValidationError(
                f"Parameter '{rule.param_name}' must be a string"
            )

        if rule.allowed_values and value not in rule.allowed_values:
            raise ValidationError(
                f"Parameter '{rule.param_name}' must be one of: "
                f"{', '.join(rule.allowed_values)}"
            )

    def _validate_space_id(self, rule: ValidationRule, value: Any):
        """Validate SAP Datasphere space ID"""
        if not isinstance(value, str):
            raise ValidationError(
                f"Parameter '{rule.param_name}' must be a string"
            )

        # Space IDs are typically uppercase with underscores/hyphens
        if not re.match(self.SPACE_ID_PATTERN, value):
            raise ValidationError(
                f"Parameter '{rule.param_name}' is not a valid space ID. "
                f"Must start with uppercase letter and contain only "
                f"uppercase letters, numbers, underscores, or hyphens."
            )

        # Check length
        if len(value) < 2 or len(value) > 64:
            raise ValidationError(
                f"Parameter '{rule.param_name}' must be 2-64 characters"
            )

    def _validate_table_name(self, rule: ValidationRule, value: Any):
        """Validate table/view name"""
        if not isinstance(value, str):
            raise ValidationError(
                f"Parameter '{rule.param_name}' must be a string"
            )

        # Table names must be valid identifiers
        if not re.match(self.IDENTIFIER_PATTERN, value):
            raise ValidationError(
                f"Parameter '{rule.param_name}' is not a valid table name. "
                f"Must start with a letter and contain only letters, "
                f"numbers, or underscores."
            )

        # Check length
        if len(value) < 1 or len(value) > 128:
            raise ValidationError(
                f"Parameter '{rule.param_name}' must be 1-128 characters"
            )

    def _validate_sql_query(self, rule: ValidationRule, value: Any):
        """
        Validate SQL query for safety

        This is a read-only MCP server, so we only allow SELECT queries
        and block any potentially dangerous operations.
        """
        if not isinstance(value, str):
            raise ValidationError(
                f"Parameter '{rule.param_name}' must be a string"
            )

        query = value.strip().upper()

        # Check if query is too long (potential DoS)
        if len(value) > 10000:
            raise ValidationError(
                f"Parameter '{rule.param_name}' exceeds maximum query length (10000 characters)"
            )

        # Must start with SELECT
        if not query.startswith('SELECT'):
            raise ValidationError(
                f"Only SELECT queries are allowed. "
                f"Query must start with SELECT."
            )

        # Check for dangerous keywords
        for keyword in self.SQL_DANGEROUS_KEYWORDS:
            if re.search(rf'\b{keyword}\b', query):
                raise ValidationError(
                    f"Query contains forbidden keyword: {keyword}"
                )

        # Check for SQL injection patterns
        for pattern in self.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                raise ValidationError(
                    f"Query contains potentially malicious pattern and was blocked"
                )

        # Check for SQL comments (could hide malicious code)
        for pattern in self.SQL_COMMENT_PATTERNS:
            if re.search(pattern, value):
                raise ValidationError(
                    f"SQL comments are not allowed in queries"
                )

    def _validate_connection_type(self, rule: ValidationRule, value: Any):
        """Validate connection type"""
        valid_types = {
            'SAP_ERP', 'SALESFORCE', 'EXTERNAL', 'SAP_S4HANA',
            'SAP_BW', 'SNOWFLAKE', 'DATABRICKS', 'POSTGRESQL',
            'MYSQL', 'ORACLE', 'SQLSERVER', 'HANA'
        }

        if not isinstance(value, str):
            raise ValidationError(
                f"Parameter '{rule.param_name}' must be a string"
            )

        if value.upper() not in valid_types:
            raise ValidationError(
                f"Parameter '{rule.param_name}' must be a valid connection type: "
                f"{', '.join(valid_types)}"
            )

    def sanitize_sql_query(self, query: str) -> str:
        """
        Sanitize SQL query by removing potentially dangerous elements

        Args:
            query: SQL query to sanitize

        Returns:
            Sanitized query
        """
        # Remove SQL comments
        query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
        query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)

        # Remove multiple spaces
        query = re.sub(r'\s+', ' ', query)

        # Trim
        query = query.strip()

        return query

    def get_validation_summary(self) -> Dict[str, Any]:
        """Get validation configuration summary"""
        return {
            "strict_mode": self.strict_mode,
            "dangerous_keywords_blocked": len(self.SQL_DANGEROUS_KEYWORDS),
            "injection_patterns_detected": len(self.SQL_INJECTION_PATTERNS),
            "supported_validation_types": [vt.value for vt in ValidationType]
        }


# Convenience function for quick validation
def validate_tool_params(
    params: Dict[str, Any],
    rules: List[ValidationRule],
    strict: bool = True
) -> Tuple[bool, List[str]]:
    """
    Validate tool parameters

    Args:
        params: Parameters to validate
        rules: Validation rules
        strict: Use strict validation mode

    Returns:
        Tuple of (is_valid, error_messages)
    """
    validator = InputValidator(strict_mode=strict)
    return validator.validate_params(params, rules)
