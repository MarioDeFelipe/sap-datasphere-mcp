#!/usr/bin/env python3
"""
Data Filter for SAP Datasphere MCP Server
Filters and redacts sensitive information from API responses
"""

import logging
import re
from typing import Any, Dict, List, Set, Optional
from copy import deepcopy

logger = logging.getLogger(__name__)


class DataFilter:
    """
    Filters sensitive data from API responses

    Features:
    - PII detection and masking
    - Credential redaction
    - Connection string filtering
    - Configurable sensitive field patterns
    """

    # Sensitive field patterns (case-insensitive)
    SENSITIVE_FIELD_PATTERNS = [
        # Credentials and secrets
        r".*password.*",
        r".*secret.*",
        r".*token.*",
        r".*api[_-]?key.*",
        r".*auth.*key.*",
        r".*private[_-]?key.*",

        # Connection strings
        r".*connection[_-]?string.*",
        r".*jdbc[_-]?url.*",
        r".*dsn.*",

        # Personal information
        r".*ssn.*",
        r".*social[_-]?security.*",
        r".*credit[_-]?card.*",
        r".*card[_-]?number.*",
        r".*cvv.*",

        # Authentication
        r".*bearer.*",
        r".*authorization.*",
        r".*credentials.*",
    ]

    # Exact sensitive field names
    SENSITIVE_FIELD_NAMES = {
        "password", "secret", "token", "api_key", "apikey",
        "client_secret", "private_key", "access_token",
        "refresh_token", "session_id", "sessionid",
        "ssn", "credit_card", "cvv", "pin"
    }

    # Patterns for sensitive values in strings
    SENSITIVE_VALUE_PATTERNS = [
        # API keys
        (r'[A-Za-z0-9]{32,}', "API_KEY_REDACTED"),
        # Tokens (JWT-like)
        (r'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}', "JWT_TOKEN_REDACTED"),
        # Connection strings
        (r'(?:mongodb|mysql|postgresql|jdbc):\/\/[^\s;]+', "CONNECTION_STRING_REDACTED"),
        # Email addresses (optional - might be legitimate data)
        # (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', "EMAIL_REDACTED"),
    ]

    def __init__(
        self,
        redact_pii: bool = True,
        redact_credentials: bool = True,
        redact_connections: bool = True,
        custom_patterns: Optional[List[str]] = None
    ):
        """
        Initialize data filter

        Args:
            redact_pii: Redact personally identifiable information
            redact_credentials: Redact credentials and secrets
            redact_connections: Redact connection strings
            custom_patterns: Additional regex patterns for sensitive fields
        """
        self.redact_pii = redact_pii
        self.redact_credentials = redact_credentials
        self.redact_connections = redact_connections

        # Compile regex patterns
        self.field_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.SENSITIVE_FIELD_PATTERNS
        ]

        if custom_patterns:
            self.field_patterns.extend([
                re.compile(pattern, re.IGNORECASE)
                for pattern in custom_patterns
            ])

        # Compile value patterns
        self.value_patterns = [
            (re.compile(pattern), replacement)
            for pattern, replacement in self.SENSITIVE_VALUE_PATTERNS
        ]

        logger.info("Data filter initialized")

    def filter_response(self, data: Any) -> Any:
        """
        Filter sensitive data from API response

        Args:
            data: Response data (dict, list, or primitive)

        Returns:
            Filtered copy of the data
        """
        # Create a deep copy to avoid modifying original
        filtered_data = deepcopy(data)

        # Recursively filter
        return self._filter_recursive(filtered_data)

    def _filter_recursive(self, data: Any, path: str = "") -> Any:
        """
        Recursively filter data structure

        Args:
            data: Data to filter
            path: Current path in data structure (for logging)

        Returns:
            Filtered data
        """
        if isinstance(data, dict):
            return self._filter_dict(data, path)
        elif isinstance(data, list):
            return self._filter_list(data, path)
        elif isinstance(data, str):
            return self._filter_string(data, path)
        else:
            return data

    def _filter_dict(self, data: Dict, path: str) -> Dict:
        """Filter dictionary data"""
        filtered = {}

        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key

            # Check if field should be redacted
            if self._is_sensitive_field(key):
                filtered[key] = self._redact_value(value, key)
                logger.debug(f"Redacted sensitive field: {current_path}")
            else:
                # Recursively filter value
                filtered[key] = self._filter_recursive(value, current_path)

        return filtered

    def _filter_list(self, data: List, path: str) -> List:
        """Filter list data"""
        return [
            self._filter_recursive(item, f"{path}[{i}]")
            for i, item in enumerate(data)
        ]

    def _filter_string(self, data: str, path: str) -> str:
        """Filter string data for sensitive patterns"""
        filtered = data

        # Apply value pattern replacements
        for pattern, replacement in self.value_patterns:
            if pattern.search(filtered):
                filtered = pattern.sub(replacement, filtered)
                logger.debug(f"Redacted sensitive pattern in: {path}")

        return filtered

    def _is_sensitive_field(self, field_name: str) -> bool:
        """
        Check if a field name indicates sensitive data

        Args:
            field_name: Field name to check

        Returns:
            True if field is sensitive
        """
        field_lower = field_name.lower()

        # Check exact matches
        if field_lower in self.SENSITIVE_FIELD_NAMES:
            return True

        # Check pattern matches
        for pattern in self.field_patterns:
            if pattern.match(field_lower):
                return True

        return False

    def _redact_value(self, value: Any, field_name: str) -> str:
        """
        Redact a sensitive value

        Args:
            value: Value to redact
            field_name: Name of the field

        Returns:
            Redacted placeholder
        """
        if value is None:
            return None

        # Determine redaction type
        field_lower = field_name.lower()

        if any(pattern in field_lower for pattern in ["password", "secret", "token"]):
            return "***REDACTED_CREDENTIAL***"
        elif any(pattern in field_lower for pattern in ["connection", "url", "dsn"]):
            return "***REDACTED_CONNECTION***"
        elif any(pattern in field_lower for pattern in ["ssn", "credit", "card"]):
            return "***REDACTED_PII***"
        else:
            return "***REDACTED***"

    def filter_connection_info(self, connection: Dict) -> Dict:
        """
        Filter connection information specifically

        Args:
            connection: Connection dictionary

        Returns:
            Filtered connection info
        """
        filtered = self.filter_response(connection)

        # Additional connection-specific filtering
        sensitive_connection_fields = [
            "host", "hostname", "server", "port",
            "username", "user", "password", "credentials",
            "connection_string", "jdbc_url", "dsn"
        ]

        for field in sensitive_connection_fields:
            if field in filtered:
                if field in ["host", "hostname", "server"]:
                    # Partially redact hostname (keep domain)
                    filtered[field] = self._partially_redact_hostname(filtered[field])
                elif field == "port":
                    # Keep port visible (not sensitive)
                    pass
                else:
                    # Fully redact
                    filtered[field] = "***REDACTED***"

        return filtered

    def _partially_redact_hostname(self, hostname: str) -> str:
        """
        Partially redact hostname while keeping domain visible

        Example: "mydb.company.com" -> "*****.company.com"

        Args:
            hostname: Hostname to redact

        Returns:
            Partially redacted hostname
        """
        if not isinstance(hostname, str):
            return hostname

        parts = hostname.split(".")
        if len(parts) > 2:
            # Keep last two parts (domain)
            return "*****." + ".".join(parts[-2:])
        else:
            return "*****"

    def get_redaction_summary(self, original: Any, filtered: Any) -> Dict:
        """
        Get summary of redactions performed

        Args:
            original: Original data
            filtered: Filtered data

        Returns:
            Summary of redactions
        """
        original_str = str(original)
        filtered_str = str(filtered)

        redaction_count = filtered_str.count("***REDACTED")

        return {
            "total_redactions": redaction_count,
            "credentials_redacted": filtered_str.count("***REDACTED_CREDENTIAL***"),
            "connections_redacted": filtered_str.count("***REDACTED_CONNECTION***"),
            "pii_redacted": filtered_str.count("***REDACTED_PII***"),
            "original_size": len(original_str),
            "filtered_size": len(filtered_str)
        }


# Convenience function for quick filtering
def filter_sensitive_data(
    data: Any,
    redact_credentials: bool = True,
    redact_connections: bool = True,
    redact_pii: bool = True
) -> Any:
    """
    Quick function to filter sensitive data

    Args:
        data: Data to filter
        redact_credentials: Redact credentials
        redact_connections: Redact connection strings
        redact_pii: Redact PII

    Returns:
        Filtered data
    """
    filter_instance = DataFilter(
        redact_pii=redact_pii,
        redact_credentials=redact_credentials,
        redact_connections=redact_connections
    )

    return filter_instance.filter_response(data)
