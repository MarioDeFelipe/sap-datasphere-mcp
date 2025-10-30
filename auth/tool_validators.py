"""
Tool-specific validation rules for SAP Datasphere MCP Server

Defines validation rules for each MCP tool to ensure safe parameter handling.
"""

from typing import Dict, List
from auth.input_validator import ValidationRule, ValidationType


class ToolValidators:
    """Validation rules registry for all MCP tools"""

    @staticmethod
    def get_validator_rules(tool_name: str) -> List[ValidationRule]:
        """
        Get validation rules for a specific tool

        Args:
            tool_name: Name of the tool

        Returns:
            List of validation rules for the tool
        """
        validators = {
            "list_spaces": ToolValidators._list_spaces_rules(),
            "get_space_info": ToolValidators._get_space_info_rules(),
            "search_tables": ToolValidators._search_tables_rules(),
            "get_table_schema": ToolValidators._get_table_schema_rules(),
            "list_connections": ToolValidators._list_connections_rules(),
            "get_task_status": ToolValidators._get_task_status_rules(),
            "browse_marketplace": ToolValidators._browse_marketplace_rules(),
            "execute_query": ToolValidators._execute_query_rules(),
        }

        return validators.get(tool_name, [])

    @staticmethod
    def _list_spaces_rules() -> List[ValidationRule]:
        """Validation rules for list_spaces tool"""
        return [
            ValidationRule(
                param_name="include_details",
                validation_type=ValidationType.BOOLEAN,
                required=False
            )
        ]

    @staticmethod
    def _get_space_info_rules() -> List[ValidationRule]:
        """Validation rules for get_space_info tool"""
        return [
            ValidationRule(
                param_name="space_id",
                validation_type=ValidationType.SPACE_ID,
                required=True,
                min_length=2,
                max_length=64
            )
        ]

    @staticmethod
    def _search_tables_rules() -> List[ValidationRule]:
        """Validation rules for search_tables tool"""
        return [
            ValidationRule(
                param_name="search_term",
                validation_type=ValidationType.STRING,
                required=True,
                min_length=1,
                max_length=256
            ),
            ValidationRule(
                param_name="space_id",
                validation_type=ValidationType.SPACE_ID,
                required=False,
                min_length=2,
                max_length=64
            )
        ]

    @staticmethod
    def _get_table_schema_rules() -> List[ValidationRule]:
        """Validation rules for get_table_schema tool"""
        return [
            ValidationRule(
                param_name="space_id",
                validation_type=ValidationType.SPACE_ID,
                required=True,
                min_length=2,
                max_length=64
            ),
            ValidationRule(
                param_name="table_name",
                validation_type=ValidationType.TABLE_NAME,
                required=True,
                min_length=1,
                max_length=128
            )
        ]

    @staticmethod
    def _list_connections_rules() -> List[ValidationRule]:
        """Validation rules for list_connections tool"""
        return [
            ValidationRule(
                param_name="connection_type",
                validation_type=ValidationType.CONNECTION_TYPE,
                required=False
            )
        ]

    @staticmethod
    def _get_task_status_rules() -> List[ValidationRule]:
        """Validation rules for get_task_status tool"""
        return [
            ValidationRule(
                param_name="task_id",
                validation_type=ValidationType.STRING,
                required=False,
                min_length=1,
                max_length=128,
                pattern=r'^[A-Z][A-Z0-9_-]*$'  # Task IDs are uppercase
            ),
            ValidationRule(
                param_name="space_id",
                validation_type=ValidationType.SPACE_ID,
                required=False,
                min_length=2,
                max_length=64
            )
        ]

    @staticmethod
    def _browse_marketplace_rules() -> List[ValidationRule]:
        """Validation rules for browse_marketplace tool"""
        return [
            ValidationRule(
                param_name="category",
                validation_type=ValidationType.STRING,
                required=False,
                min_length=1,
                max_length=100
            ),
            ValidationRule(
                param_name="search_term",
                validation_type=ValidationType.STRING,
                required=False,
                min_length=1,
                max_length=256
            )
        ]

    @staticmethod
    def _execute_query_rules() -> List[ValidationRule]:
        """Validation rules for execute_query tool (high-risk)"""
        return [
            ValidationRule(
                param_name="space_id",
                validation_type=ValidationType.SPACE_ID,
                required=True,
                min_length=2,
                max_length=64
            ),
            ValidationRule(
                param_name="sql_query",
                validation_type=ValidationType.SQL_QUERY,
                required=True,
                min_length=1,
                max_length=10000
            ),
            ValidationRule(
                param_name="limit",
                validation_type=ValidationType.INTEGER,
                required=False
            )
        ]

    @staticmethod
    def get_all_tool_names() -> List[str]:
        """Get list of all tools with validators"""
        return [
            "list_spaces",
            "get_space_info",
            "search_tables",
            "get_table_schema",
            "list_connections",
            "get_task_status",
            "browse_marketplace",
            "execute_query"
        ]

    @staticmethod
    def has_validator(tool_name: str) -> bool:
        """Check if tool has validator rules defined"""
        return tool_name in ToolValidators.get_all_tool_names()
