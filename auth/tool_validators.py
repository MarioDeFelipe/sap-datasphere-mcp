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
            "list_database_users": ToolValidators._list_database_users_rules(),
            "create_database_user": ToolValidators._create_database_user_rules(),
            "reset_database_user_password": ToolValidators._reset_database_user_password_rules(),
            "update_database_user": ToolValidators._update_database_user_rules(),
            "delete_database_user": ToolValidators._delete_database_user_rules(),
            "list_catalog_assets": ToolValidators._list_catalog_assets_rules(),
            "get_asset_details": ToolValidators._get_asset_details_rules(),
            "get_asset_by_compound_key": ToolValidators._get_asset_by_compound_key_rules(),
            "get_space_assets": ToolValidators._get_space_assets_rules(),
            "search_catalog": ToolValidators._search_catalog_rules(),
            "search_repository": ToolValidators._search_repository_rules(),
            "get_catalog_metadata": ToolValidators._get_catalog_metadata_rules(),
            "get_consumption_metadata": ToolValidators._get_consumption_metadata_rules(),
            "get_analytical_metadata": ToolValidators._get_analytical_metadata_rules(),
            "get_relational_metadata": ToolValidators._get_relational_metadata_rules(),
            "get_repository_search_metadata": ToolValidators._get_repository_search_metadata_rules(),
            "list_analytical_datasets": ToolValidators._list_analytical_datasets_rules(),
            "get_analytical_model": ToolValidators._get_analytical_model_rules(),
            "query_analytical_data": ToolValidators._query_analytical_data_rules(),
            "get_analytical_service_document": ToolValidators._get_analytical_service_document_rules(),
            "list_repository_objects": ToolValidators._list_repository_objects_rules(),
            "get_object_definition": ToolValidators._get_object_definition_rules(),
            "get_deployed_objects": ToolValidators._get_deployed_objects_rules(),
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
    def _list_database_users_rules() -> List[ValidationRule]:
        """Validation rules for list_database_users tool"""
        return [
            ValidationRule(
                param_name="space_id",
                validation_type=ValidationType.SPACE_ID,
                required=True,
                min_length=2,
                max_length=64
            ),
            ValidationRule(
                param_name="output_file",
                validation_type=ValidationType.STRING,
                required=False,
                min_length=1,
                max_length=256,
                pattern=r'^[\w\-./\\]+\.json$'  # Must end with .json
            )
        ]

    @staticmethod
    def _create_database_user_rules() -> List[ValidationRule]:
        """Validation rules for create_database_user tool (high-risk)"""
        return [
            ValidationRule(
                param_name="space_id",
                validation_type=ValidationType.SPACE_ID,
                required=True,
                min_length=2,
                max_length=64
            ),
            ValidationRule(
                param_name="database_user_id",
                validation_type=ValidationType.STRING,
                required=True,
                min_length=1,
                max_length=64,
                pattern=r'^[A-Z][A-Z0-9_]*$'  # Uppercase, alphanumeric with underscores
            ),
            ValidationRule(
                param_name="user_definition",
                validation_type=ValidationType.STRING,  # Will be validated as JSON object
                required=True
            ),
            ValidationRule(
                param_name="output_file",
                validation_type=ValidationType.STRING,
                required=False,
                min_length=1,
                max_length=256,
                pattern=r'^[\w\-./\\]+\.json$'
            )
        ]

    @staticmethod
    def _reset_database_user_password_rules() -> List[ValidationRule]:
        """Validation rules for reset_database_user_password tool (high-risk)"""
        return [
            ValidationRule(
                param_name="space_id",
                validation_type=ValidationType.SPACE_ID,
                required=True,
                min_length=2,
                max_length=64
            ),
            ValidationRule(
                param_name="database_user_id",
                validation_type=ValidationType.STRING,
                required=True,
                min_length=1,
                max_length=64,
                pattern=r'^[A-Z][A-Z0-9_]*$'
            ),
            ValidationRule(
                param_name="output_file",
                validation_type=ValidationType.STRING,
                required=False,
                min_length=1,
                max_length=256,
                pattern=r'^[\w\-./\\]+\.json$'
            )
        ]

    @staticmethod
    def _update_database_user_rules() -> List[ValidationRule]:
        """Validation rules for update_database_user tool (high-risk)"""
        return [
            ValidationRule(
                param_name="space_id",
                validation_type=ValidationType.SPACE_ID,
                required=True,
                min_length=2,
                max_length=64
            ),
            ValidationRule(
                param_name="database_user_id",
                validation_type=ValidationType.STRING,
                required=True,
                min_length=1,
                max_length=64,
                pattern=r'^[A-Z][A-Z0-9_]*$'
            ),
            ValidationRule(
                param_name="updated_definition",
                validation_type=ValidationType.STRING,  # Will be validated as JSON object
                required=True
            ),
            ValidationRule(
                param_name="output_file",
                validation_type=ValidationType.STRING,
                required=False,
                min_length=1,
                max_length=256,
                pattern=r'^[\w\-./\\]+\.json$'
            )
        ]

    @staticmethod
    def _delete_database_user_rules() -> List[ValidationRule]:
        """Validation rules for delete_database_user tool (high-risk)"""
        return [
            ValidationRule(
                param_name="space_id",
                validation_type=ValidationType.SPACE_ID,
                required=True,
                min_length=2,
                max_length=64
            ),
            ValidationRule(
                param_name="database_user_id",
                validation_type=ValidationType.STRING,
                required=True,
                min_length=1,
                max_length=64,
                pattern=r'^[A-Z][A-Z0-9_]*$'
            ),
            ValidationRule(
                param_name="force",
                validation_type=ValidationType.BOOLEAN,
                required=False
            )
        ]

    @staticmethod
    def _list_catalog_assets_rules() -> List[ValidationRule]:
        """Validation rules for list_catalog_assets tool"""
        return [
            ValidationRule(
                param_name="filter_expression",
                validation_type=ValidationType.STRING,
                required=False,
                min_length=1,
                max_length=500
            ),
            ValidationRule(
                param_name="top",
                validation_type=ValidationType.INTEGER,
                required=False
            ),
            ValidationRule(
                param_name="skip",
                validation_type=ValidationType.INTEGER,
                required=False
            ),
            ValidationRule(
                param_name="include_count",
                validation_type=ValidationType.BOOLEAN,
                required=False
            )
        ]

    @staticmethod
    def _get_asset_details_rules() -> List[ValidationRule]:
        """Validation rules for get_asset_details tool"""
        return [
            ValidationRule(
                param_name="space_id",
                validation_type=ValidationType.SPACE_ID,
                required=True,
                min_length=2,
                max_length=64
            ),
            ValidationRule(
                param_name="asset_id",
                validation_type=ValidationType.STRING,
                required=True,
                min_length=1,
                max_length=128,
                pattern=r'^[A-Za-z0-9_\-]+$'  # Asset IDs are alphanumeric with underscores/hyphens
            )
        ]

    @staticmethod
    def _get_asset_by_compound_key_rules() -> List[ValidationRule]:
        """Validation rules for get_asset_by_compound_key tool"""
        return [
            ValidationRule(
                param_name="space_id",
                validation_type=ValidationType.SPACE_ID,
                required=True,
                min_length=2,
                max_length=64
            ),
            ValidationRule(
                param_name="asset_id",
                validation_type=ValidationType.STRING,
                required=True,
                min_length=1,
                max_length=128,
                pattern=r'^[A-Za-z0-9_\-]+$'
            )
        ]

    @staticmethod
    def _get_space_assets_rules() -> List[ValidationRule]:
        """Validation rules for get_space_assets tool"""
        return [
            ValidationRule(
                param_name="space_id",
                validation_type=ValidationType.SPACE_ID,
                required=True,
                min_length=2,
                max_length=64
            ),
            ValidationRule(
                param_name="filter_expression",
                validation_type=ValidationType.STRING,
                required=False,
                min_length=1,
                max_length=500
            ),
            ValidationRule(
                param_name="top",
                validation_type=ValidationType.INTEGER,
                required=False
            ),
            ValidationRule(
                param_name="skip",
                validation_type=ValidationType.INTEGER,
                required=False
            )
        ]

    @staticmethod
    def _search_catalog_rules() -> List[ValidationRule]:
        """Validation rules for search_catalog tool"""
        return [
            ValidationRule(
                param_name="query",
                validation_type=ValidationType.STRING,
                required=True,
                min_length=1,
                max_length=500
            ),
            ValidationRule(
                param_name="top",
                validation_type=ValidationType.INTEGER,
                required=False
            ),
            ValidationRule(
                param_name="skip",
                validation_type=ValidationType.INTEGER,
                required=False
            ),
            ValidationRule(
                param_name="include_count",
                validation_type=ValidationType.BOOLEAN,
                required=False
            ),
            ValidationRule(
                param_name="include_why_found",
                validation_type=ValidationType.BOOLEAN,
                required=False
            ),
            ValidationRule(
                param_name="facets",
                validation_type=ValidationType.STRING,
                required=False,
                min_length=1,
                max_length=200
            ),
            ValidationRule(
                param_name="facet_limit",
                validation_type=ValidationType.INTEGER,
                required=False
            )
        ]

    @staticmethod
    def _search_repository_rules() -> List[ValidationRule]:
        """Validation rules for search_repository tool"""
        return [
            ValidationRule(
                param_name="search_terms",
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
            ),
            ValidationRule(
                param_name="top",
                validation_type=ValidationType.INTEGER,
                required=False
            ),
            ValidationRule(
                param_name="skip",
                validation_type=ValidationType.INTEGER,
                required=False
            ),
            ValidationRule(
                param_name="include_dependencies",
                validation_type=ValidationType.BOOLEAN,
                required=False
            ),
            ValidationRule(
                param_name="include_lineage",
                validation_type=ValidationType.BOOLEAN,
                required=False
            )
        ]

    @staticmethod
    def _get_catalog_metadata_rules() -> List[ValidationRule]:
        """Validation rules for get_catalog_metadata tool"""
        return [
            ValidationRule(
                param_name="endpoint_type",
                validation_type=ValidationType.STRING,
                required=False,
                allowed_values=["consumption", "catalog", "legacy"]
            ),
            ValidationRule(
                param_name="parse_metadata",
                validation_type=ValidationType.BOOLEAN,
                required=False
            )
        ]

    @staticmethod
    def _get_consumption_metadata_rules() -> List[ValidationRule]:
        """Validation rules for get_consumption_metadata tool"""
        return [
            ValidationRule(
                param_name="parse_xml",
                validation_type=ValidationType.BOOLEAN,
                required=False
            ),
            ValidationRule(
                param_name="include_annotations",
                validation_type=ValidationType.BOOLEAN,
                required=False
            )
        ]

    @staticmethod
    def _get_analytical_metadata_rules() -> List[ValidationRule]:
        """Validation rules for get_analytical_metadata tool"""
        return [
            ValidationRule(
                param_name="space_id",
                validation_type=ValidationType.SPACE_ID,
                required=True,
                min_length=2,
                max_length=64
            ),
            ValidationRule(
                param_name="asset_id",
                validation_type=ValidationType.STRING,
                required=True,
                min_length=1,
                max_length=128,
                pattern=r'^[A-Za-z0-9_\-]+$'
            ),
            ValidationRule(
                param_name="identify_dimensions_measures",
                validation_type=ValidationType.BOOLEAN,
                required=False
            )
        ]

    @staticmethod
    def _get_relational_metadata_rules() -> List[ValidationRule]:
        """Validation rules for get_relational_metadata tool"""
        return [
            ValidationRule(
                param_name="space_id",
                validation_type=ValidationType.SPACE_ID,
                required=True,
                min_length=2,
                max_length=64
            ),
            ValidationRule(
                param_name="asset_id",
                validation_type=ValidationType.STRING,
                required=True,
                min_length=1,
                max_length=128,
                pattern=r'^[A-Za-z0-9_\-]+$'
            ),
            ValidationRule(
                param_name="map_to_sql_types",
                validation_type=ValidationType.BOOLEAN,
                required=False
            )
        ]

    @staticmethod
    def _get_repository_search_metadata_rules() -> List[ValidationRule]:
        """Validation rules for get_repository_search_metadata tool"""
        return [
            ValidationRule(
                param_name="include_field_details",
                validation_type=ValidationType.BOOLEAN,
                required=False
            )
        ]

    @staticmethod
    def _list_analytical_datasets_rules() -> List[ValidationRule]:
        """Validation rules for list_analytical_datasets tool"""
        return [
            ValidationRule(
                param_name="space_id",
                validation_type=ValidationType.SPACE_ID,
                required=True,
                min_length=2,
                max_length=64
            ),
            ValidationRule(
                param_name="asset_id",
                validation_type=ValidationType.STRING,
                required=True,
                min_length=1,
                max_length=128,
                pattern=r'^[A-Za-z0-9_\-]+$'
            ),
            ValidationRule(
                param_name="top",
                validation_type=ValidationType.INTEGER,
                required=False
            ),
            ValidationRule(
                param_name="skip",
                validation_type=ValidationType.INTEGER,
                required=False
            )
        ]

    @staticmethod
    def _get_analytical_model_rules() -> List[ValidationRule]:
        """Validation rules for get_analytical_model tool"""
        return [
            ValidationRule(
                param_name="space_id",
                validation_type=ValidationType.SPACE_ID,
                required=True,
                min_length=2,
                max_length=64
            ),
            ValidationRule(
                param_name="asset_id",
                validation_type=ValidationType.STRING,
                required=True,
                min_length=1,
                max_length=128,
                pattern=r'^[A-Za-z0-9_\-]+$'
            ),
            ValidationRule(
                param_name="include_metadata",
                validation_type=ValidationType.BOOLEAN,
                required=False
            )
        ]

    @staticmethod
    def _query_analytical_data_rules() -> List[ValidationRule]:
        """Validation rules for query_analytical_data tool"""
        return [
            ValidationRule(
                param_name="space_id",
                validation_type=ValidationType.SPACE_ID,
                required=True,
                min_length=2,
                max_length=64
            ),
            ValidationRule(
                param_name="asset_id",
                validation_type=ValidationType.STRING,
                required=True,
                min_length=1,
                max_length=128,
                pattern=r'^[A-Za-z0-9_\-]+$'
            ),
            ValidationRule(
                param_name="entity_set",
                validation_type=ValidationType.STRING,
                required=True,
                min_length=1,
                max_length=128,
                pattern=r'^[A-Za-z0-9_\-]+$'
            ),
            ValidationRule(
                param_name="select",
                validation_type=ValidationType.STRING,
                required=False,
                min_length=1,
                max_length=500
            ),
            ValidationRule(
                param_name="filter",
                validation_type=ValidationType.STRING,
                required=False,
                min_length=1,
                max_length=1000
            ),
            ValidationRule(
                param_name="orderby",
                validation_type=ValidationType.STRING,
                required=False,
                min_length=1,
                max_length=200
            ),
            ValidationRule(
                param_name="top",
                validation_type=ValidationType.INTEGER,
                required=False
            ),
            ValidationRule(
                param_name="skip",
                validation_type=ValidationType.INTEGER,
                required=False
            ),
            ValidationRule(
                param_name="count",
                validation_type=ValidationType.BOOLEAN,
                required=False
            ),
            ValidationRule(
                param_name="apply",
                validation_type=ValidationType.STRING,
                required=False,
                min_length=1,
                max_length=1000
            )
        ]

    @staticmethod
    def _get_analytical_service_document_rules() -> List[ValidationRule]:
        """Validation rules for get_analytical_service_document tool"""
        return [
            ValidationRule(
                param_name="space_id",
                validation_type=ValidationType.SPACE_ID,
                required=True,
                min_length=2,
                max_length=64
            ),
            ValidationRule(
                param_name="asset_id",
                validation_type=ValidationType.STRING,
                required=True,
                min_length=1,
                max_length=128,
                pattern=r'^[A-Za-z0-9_\-]+$'
            )
        ]

    @staticmethod
    def _list_repository_objects_rules() -> List[ValidationRule]:
        """Validation rules for list_repository_objects tool"""
        return [
            ValidationRule(
                param_name="space_id",
                validation_type=ValidationType.SPACE_ID,
                required=True,
                min_length=2,
                max_length=64
            ),
            ValidationRule(
                param_name="object_types",
                validation_type=ValidationType.STRING,
                required=False
            ),
            ValidationRule(
                param_name="status_filter",
                validation_type=ValidationType.STRING,
                required=False,
                min_length=1,
                max_length=50
            ),
            ValidationRule(
                param_name="include_dependencies",
                validation_type=ValidationType.BOOLEAN,
                required=False
            ),
            ValidationRule(
                param_name="top",
                validation_type=ValidationType.INTEGER,
                required=False
            ),
            ValidationRule(
                param_name="skip",
                validation_type=ValidationType.INTEGER,
                required=False
            )
        ]

    @staticmethod
    def _get_object_definition_rules() -> List[ValidationRule]:
        """Validation rules for get_object_definition tool"""
        return [
            ValidationRule(
                param_name="space_id",
                validation_type=ValidationType.SPACE_ID,
                required=True,
                min_length=2,
                max_length=64
            ),
            ValidationRule(
                param_name="object_id",
                validation_type=ValidationType.STRING,
                required=True,
                min_length=1,
                max_length=128,
                pattern=r'^[A-Za-z0-9_\-]+$'
            ),
            ValidationRule(
                param_name="include_full_definition",
                validation_type=ValidationType.BOOLEAN,
                required=False
            ),
            ValidationRule(
                param_name="include_dependencies",
                validation_type=ValidationType.BOOLEAN,
                required=False
            )
        ]

    @staticmethod
    def _get_deployed_objects_rules() -> List[ValidationRule]:
        """Validation rules for get_deployed_objects tool"""
        return [
            ValidationRule(
                param_name="space_id",
                validation_type=ValidationType.SPACE_ID,
                required=True,
                min_length=2,
                max_length=64
            ),
            ValidationRule(
                param_name="object_types",
                validation_type=ValidationType.STRING,
                required=False
            ),
            ValidationRule(
                param_name="runtime_status",
                validation_type=ValidationType.STRING,
                required=False,
                min_length=1,
                max_length=50
            ),
            ValidationRule(
                param_name="include_metrics",
                validation_type=ValidationType.BOOLEAN,
                required=False
            ),
            ValidationRule(
                param_name="top",
                validation_type=ValidationType.INTEGER,
                required=False
            ),
            ValidationRule(
                param_name="skip",
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
            "execute_query",
            "list_database_users",
            "create_database_user",
            "reset_database_user_password",
            "update_database_user",
            "delete_database_user",
            "list_catalog_assets",
            "get_asset_details",
            "get_asset_by_compound_key",
            "get_space_assets",
            "search_catalog",
            "search_repository",
            "get_catalog_metadata",
            "get_consumption_metadata",
            "get_analytical_metadata",
            "get_relational_metadata",
            "get_repository_search_metadata",
            "list_analytical_datasets",
            "get_analytical_model",
            "query_analytical_data",
            "get_analytical_service_document",
            "list_repository_objects",
            "get_object_definition",
            "get_deployed_objects"
        ]

    @staticmethod
    def has_validator(tool_name: str) -> bool:
        """Check if tool has validator rules defined"""
        return tool_name in ToolValidators.get_all_tool_names()
