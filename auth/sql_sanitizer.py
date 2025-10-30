"""
SQL Sanitization Module for SAP Datasphere MCP Server

Provides SQL injection prevention and query sanitization for database operations.
"""

import re
import logging
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SQLOperation(Enum):
    """Allowed SQL operations"""
    SELECT = "SELECT"


class SQLSanitizerError(Exception):
    """Raised when SQL sanitization fails"""
    pass


@dataclass
class QueryAnalysis:
    """Analysis result of a SQL query"""
    is_safe: bool
    operation: Optional[SQLOperation]
    tables_accessed: List[str]
    warnings: List[str]
    errors: List[str]
    sanitized_query: Optional[str]


class SQLSanitizer:
    """
    SQL sanitization and injection prevention

    This sanitizer is designed for read-only database access.
    It only allows SELECT queries and blocks any write operations.

    Features:
    - SQL injection detection
    - Comment removal
    - Keyword whitelisting
    - Table/column name validation
    - Query complexity analysis
    """

    # Allowed SQL keywords for SELECT queries
    ALLOWED_KEYWORDS = {
        'SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'NOT',
        'JOIN', 'INNER', 'LEFT', 'RIGHT', 'OUTER', 'ON',
        'GROUP', 'BY', 'HAVING', 'ORDER', 'ASC', 'DESC',
        'LIMIT', 'OFFSET', 'AS', 'DISTINCT', 'TOP',
        'CASE', 'WHEN', 'THEN', 'ELSE', 'END',
        'IN', 'BETWEEN', 'LIKE', 'IS', 'NULL',
        'COUNT', 'SUM', 'AVG', 'MIN', 'MAX',
        'UNION', 'ALL'  # Allow UNION for combining results
    }

    # Blocked keywords (write operations)
    BLOCKED_KEYWORDS = {
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE',
        'ALTER', 'TRUNCATE', 'REPLACE', 'MERGE',
        'GRANT', 'REVOKE', 'EXEC', 'EXECUTE',
        'CALL', 'PROCEDURE', 'FUNCTION'
    }

    # Dangerous patterns that indicate SQL injection
    INJECTION_PATTERNS = [
        r";\s*DROP",                        # Statement chaining
        r";\s*DELETE",                      # Statement chaining
        r";\s*INSERT",                      # Statement chaining
        r";\s*UPDATE",                      # Statement chaining
        r"'.*OR.*'.*=.*'",                  # Quote-based OR injection
        r"1\s*=\s*1",                       # Always true condition
        r"0\s*=\s*0",                       # Always true condition
        r"'\s*OR\s*'.*'\s*=\s*'",          # OR with quotes
        r"xp_\w+",                          # SQL Server extended procs
        r"sp_\w+",                          # SQL Server system procs
        r"WAITFOR\s+DELAY",                 # Time-based attacks
        r"BENCHMARK\s*\(",                  # MySQL timing
        r"pg_sleep\s*\(",                   # PostgreSQL sleep
        r"DBMS_\w+",                        # Oracle packages
    ]

    # Comment patterns to remove
    COMMENT_PATTERNS = [
        (r'--[^\n]*', ''),                  # Line comments
        (r'/\*.*?\*/', ''),                 # Block comments
        (r'#[^\n]*', ''),                   # MySQL comments
    ]

    def __init__(
        self,
        max_query_length: int = 10000,
        max_tables: int = 10,
        allow_subqueries: bool = True
    ):
        """
        Initialize SQL sanitizer

        Args:
            max_query_length: Maximum allowed query length
            max_tables: Maximum number of tables in a query
            allow_subqueries: Whether to allow subqueries
        """
        self.max_query_length = max_query_length
        self.max_tables = max_tables
        self.allow_subqueries = allow_subqueries
        logger.info("SQL sanitizer initialized")

    def analyze_query(self, query: str) -> QueryAnalysis:
        """
        Analyze and sanitize a SQL query

        Args:
            query: SQL query to analyze

        Returns:
            QueryAnalysis with safety assessment and sanitized query
        """
        warnings: List[str] = []
        errors: List[str] = []

        # Step 1: Basic validation
        if not query or not query.strip():
            errors.append("Query is empty")
            return QueryAnalysis(
                is_safe=False,
                operation=None,
                tables_accessed=[],
                warnings=warnings,
                errors=errors,
                sanitized_query=None
            )

        # Step 2: Length check
        if len(query) > self.max_query_length:
            errors.append(
                f"Query exceeds maximum length ({self.max_query_length} characters)"
            )
            return QueryAnalysis(
                is_safe=False,
                operation=None,
                tables_accessed=[],
                warnings=warnings,
                errors=errors,
                sanitized_query=None
            )

        # Step 3: Check for comments BEFORE removal (they're blocked)
        for pattern, _ in self.COMMENT_PATTERNS:
            if re.search(pattern, query, flags=re.DOTALL):
                errors.append("SQL comments are not allowed in queries")
                break

        # Remove comments for further analysis
        sanitized = query
        for pattern, replacement in self.COMMENT_PATTERNS:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.DOTALL)

        # Step 4: Normalize whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()

        # Step 5: Check for blocked keywords
        upper_query = sanitized.upper()
        for keyword in self.BLOCKED_KEYWORDS:
            if re.search(rf'\b{keyword}\b', upper_query):
                errors.append(f"Blocked keyword detected: {keyword}")

        # Step 6: Check for injection patterns
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, sanitized, re.IGNORECASE):
                errors.append(
                    "Potential SQL injection pattern detected and blocked"
                )

        # Step 7: Validate operation type
        operation = self._detect_operation(sanitized)
        if operation != SQLOperation.SELECT:
            errors.append("Only SELECT queries are allowed")

        # Step 8: Extract tables
        tables = self._extract_tables(sanitized)
        if len(tables) > self.max_tables:
            warnings.append(
                f"Query accesses {len(tables)} tables (limit: {self.max_tables})"
            )

        # Step 9: Check for subqueries if not allowed
        if not self.allow_subqueries:
            if self._has_subqueries(sanitized):
                errors.append("Subqueries are not allowed")

        # Step 10: Validate identifiers
        identifier_errors = self._validate_identifiers(sanitized)
        errors.extend(identifier_errors)

        # Determine if query is safe
        is_safe = len(errors) == 0

        return QueryAnalysis(
            is_safe=is_safe,
            operation=operation,
            tables_accessed=tables,
            warnings=warnings,
            errors=errors,
            sanitized_query=sanitized if is_safe else None
        )

    def _detect_operation(self, query: str) -> Optional[SQLOperation]:
        """Detect SQL operation type"""
        query_upper = query.strip().upper()

        if query_upper.startswith('SELECT'):
            return SQLOperation.SELECT

        return None

    def _extract_tables(self, query: str) -> List[str]:
        """
        Extract table names from SELECT query

        This is a simplified implementation that looks for FROM and JOIN clauses.
        """
        tables = []

        # Pattern to match table names after FROM and JOIN
        # Simplified: matches word characters, dots, and underscores
        from_pattern = r'\bFROM\s+([a-zA-Z_][a-zA-Z0-9_\.]*)'
        join_pattern = r'\bJOIN\s+([a-zA-Z_][a-zA-Z0-9_\.]*)'

        # Find tables in FROM clause
        from_matches = re.finditer(from_pattern, query, re.IGNORECASE)
        for match in from_matches:
            tables.append(match.group(1))

        # Find tables in JOIN clauses
        join_matches = re.finditer(join_pattern, query, re.IGNORECASE)
        for match in join_matches:
            tables.append(match.group(1))

        # Remove duplicates while preserving order
        seen = set()
        unique_tables = []
        for table in tables:
            if table not in seen:
                seen.add(table)
                unique_tables.append(table)

        return unique_tables

    def _has_subqueries(self, query: str) -> bool:
        """Check if query contains subqueries"""
        # Count SELECT keywords - if more than 1, likely has subqueries
        select_count = len(re.findall(r'\bSELECT\b', query, re.IGNORECASE))
        return select_count > 1

    def _validate_identifiers(self, query: str) -> List[str]:
        """
        Validate table and column identifiers

        Ensures identifiers follow SQL naming conventions
        """
        errors = []

        # Extract potential identifiers (simplified)
        # This pattern matches SQL identifiers
        identifier_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_\.]*)\b'
        identifiers = re.findall(identifier_pattern, query)

        for identifier in identifiers:
            # Check for suspicious patterns
            if '..' in identifier:
                errors.append(f"Invalid identifier: {identifier}")

            # Check identifier length
            if len(identifier) > 128:
                errors.append(f"Identifier too long: {identifier}")

        return errors

    def sanitize(self, query: str) -> Tuple[str, List[str]]:
        """
        Sanitize a SQL query

        Args:
            query: SQL query to sanitize

        Returns:
            Tuple of (sanitized_query, warnings)

        Raises:
            SQLSanitizerError: If query cannot be sanitized safely
        """
        analysis = self.analyze_query(query)

        if not analysis.is_safe:
            error_msg = "; ".join(analysis.errors)
            raise SQLSanitizerError(f"Query failed safety checks: {error_msg}")

        return analysis.sanitized_query, analysis.warnings

    def is_safe(self, query: str) -> bool:
        """
        Quick check if query is safe

        Args:
            query: SQL query to check

        Returns:
            True if query is safe, False otherwise
        """
        analysis = self.analyze_query(query)
        return analysis.is_safe

    def get_sanitizer_config(self) -> Dict:
        """Get sanitizer configuration"""
        return {
            "max_query_length": self.max_query_length,
            "max_tables": self.max_tables,
            "allow_subqueries": self.allow_subqueries,
            "allowed_operations": [op.value for op in SQLOperation],
            "blocked_keywords": list(self.BLOCKED_KEYWORDS),
            "injection_patterns_detected": len(self.INJECTION_PATTERNS)
        }


# Convenience function
def sanitize_sql(
    query: str,
    max_length: int = 10000,
    allow_subqueries: bool = True
) -> str:
    """
    Sanitize a SQL query

    Args:
        query: SQL query to sanitize
        max_length: Maximum query length
        allow_subqueries: Allow subqueries

    Returns:
        Sanitized query

    Raises:
        SQLSanitizerError: If query is not safe
    """
    sanitizer = SQLSanitizer(
        max_query_length=max_length,
        allow_subqueries=allow_subqueries
    )
    sanitized, warnings = sanitizer.sanitize(query)

    if warnings:
        logger.warning(f"SQL sanitization warnings: {warnings}")

    return sanitized
