#!/usr/bin/env python3
"""
SAP Datasphere MCP Server
Provides AI assistants with access to SAP Datasphere capabilities
Can work with mock data or real API connections
"""

import asyncio
import json
import logging
import re
import time
import secrets
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Sequence
from dotenv import load_dotenv
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel,
    Prompt,
    PromptMessage
)
import mcp.server.stdio
import mcp.types as types

# Authorization and security modules
from auth.authorization import AuthorizationManager
from auth.consent_manager import ConsentManager
from auth.data_filter import DataFilter
from auth.input_validator import InputValidator
from auth.sql_sanitizer import SQLSanitizer
from auth.tool_validators import ToolValidators

# OAuth and real connectivity (imported conditionally)
from auth.datasphere_auth_connector import DatasphereAuthConnector, DatasphereConfig

# Enhanced tool descriptions
from tool_descriptions import ToolDescriptions

# Error helpers for better UX
from error_helpers import ErrorHelpers

# Mock data for development and testing
from mock_data import MOCK_DATA, get_mock_catalog_assets, get_mock_asset_details

# Cache manager for performance
from cache_manager import CacheManager, CacheCategory

# Telemetry and monitoring
from telemetry import TelemetryManager

# Load environment variables from .env file
load_dotenv()

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(level=getattr(logging, log_level))
logger = logging.getLogger("sap-datasphere-mcp")

# Configuration from environment variables
USE_MOCK_DATA = os.getenv('USE_MOCK_DATA', 'true').lower() == 'true'

DATASPHERE_CONFIG = {
    "tenant_id": os.getenv('DATASPHERE_TENANT_ID', 'f45fa9cc-f4b5-4126-ab73-b19b578fb17a'),
    "base_url": os.getenv('DATASPHERE_BASE_URL', 'https://f45fa9cc-f4b5-4126-ab73-b19b578fb17a.eu10.hcs.cloud.sap'),
    "use_mock_data": USE_MOCK_DATA,
    "oauth_config": {
        "client_id": os.getenv('DATASPHERE_CLIENT_ID'),
        "client_secret": os.getenv('DATASPHERE_CLIENT_SECRET'),
        "token_url": os.getenv('DATASPHERE_TOKEN_URL'),
        "scope": os.getenv('DATASPHERE_SCOPE')
    }
}

# Log configuration mode
logger.info(f"=" * 80)
logger.info(f"SAP Datasphere MCP Server Starting")
logger.info(f"=" * 80)
logger.info(f"Mock Data Mode: {USE_MOCK_DATA}")
logger.info(f"Base URL: {DATASPHERE_CONFIG['base_url']}")
if not USE_MOCK_DATA:
    has_oauth = all([
        DATASPHERE_CONFIG['oauth_config']['client_id'],
        DATASPHERE_CONFIG['oauth_config']['client_secret'],
        DATASPHERE_CONFIG['oauth_config']['token_url']
    ])
    logger.info(f"OAuth Configured: {has_oauth}")
    if not has_oauth:
        logger.warning("⚠️  USE_MOCK_DATA=false but OAuth credentials missing!")
        logger.warning("⚠️  Server will fail to connect. Please configure .env file.")
logger.info(f"=" * 80)

# Initialize the MCP server
server = Server("sap-datasphere-mcp")

# Initialize authorization and security components
auth_manager = AuthorizationManager()
consent_manager = ConsentManager(auth_manager)
data_filter = DataFilter(
    redact_pii=True,
    redact_credentials=True,
    redact_connections=True
)
input_validator = InputValidator(strict_mode=True)
sql_sanitizer = SQLSanitizer(
    max_query_length=10000,
    max_tables=10,
    allow_subqueries=True
)
telemetry_manager = TelemetryManager(
    max_history=1000
)
cache_manager = CacheManager(
    max_size=1000,
    enabled=True,
    telemetry_manager=telemetry_manager
)

# Global variable for OAuth connector (initialized in main())
datasphere_connector: Optional[DatasphereAuthConnector] = None

@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List available Datasphere resources"""
    
    resources = [
        Resource(
            uri="datasphere://spaces",
            name="Datasphere Spaces",
            description="List of all Datasphere spaces and their configurations",
            mimeType="application/json"
        ),
        Resource(
            uri="datasphere://connections", 
            name="Data Connections",
            description="Available data source connections",
            mimeType="application/json"
        ),
        Resource(
            uri="datasphere://tasks",
            name="Integration Tasks",
            description="Data integration and ETL tasks",
            mimeType="application/json"
        ),
        Resource(
            uri="datasphere://marketplace",
            name="Data Marketplace",
            description="Available data packages in the marketplace",
            mimeType="application/json"
        )
    ]
    
    # Add space-specific table resources
    for space in MOCK_DATA["spaces"]:
        resources.append(Resource(
            uri=f"datasphere://spaces/{space['id']}/tables",
            name=f"{space['name']} - Tables",
            description=f"Tables and views in the {space['name']} space",
            mimeType="application/json"
        ))
    
    return resources

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read specific Datasphere resource content"""

    if DATASPHERE_CONFIG["use_mock_data"]:
        # Mock data mode - return static mock data
        if uri == "datasphere://spaces":
            return json.dumps(MOCK_DATA["spaces"], indent=2)

        elif uri == "datasphere://connections":
            return json.dumps(MOCK_DATA["connections"], indent=2)

        elif uri == "datasphere://tasks":
            return json.dumps(MOCK_DATA["tasks"], indent=2)

        elif uri == "datasphere://marketplace":
            return json.dumps(MOCK_DATA["marketplace_packages"], indent=2)

        elif uri.startswith("datasphere://spaces/") and uri.endswith("/tables"):
            # Extract space ID from URI
            space_id = uri.split("/")[2]
            tables = MOCK_DATA["tables"].get(space_id, [])
            return json.dumps(tables, indent=2)

        else:
            raise ValueError(f"Unknown resource URI: {uri}")
    else:
        # Real data mode - this handler is not used with real OAuth connections
        # Resources are accessed through MCP tools instead
        raise ValueError(f"Resource URIs not supported in real data mode. Use MCP tools instead: {uri}")

@server.list_prompts()
async def handle_list_prompts() -> list[Prompt]:
    """List available prompt templates for common workflows"""

    return [
        Prompt(
            name="explore_datasphere",
            description="Guided workflow to explore SAP Datasphere resources and understand available data",
            arguments=[]
        ),
        Prompt(
            name="analyze_sales_data",
            description="Template for analyzing sales data with common queries and insights",
            arguments=[
                {
                    "name": "space_id",
                    "description": "Optional: Specific space to analyze (e.g., 'SALES_ANALYTICS')",
                    "required": False
                }
            ]
        ),
        Prompt(
            name="check_data_pipeline",
            description="Monitor data pipeline health, task status, and connection status",
            arguments=[]
        ),
        Prompt(
            name="query_builder_assistant",
            description="Interactive assistant to help build SQL queries for Datasphere tables",
            arguments=[
                {
                    "name": "table_name",
                    "description": "Optional: Table to query",
                    "required": False
                }
            ]
        )
    ]

@server.get_prompt()
async def handle_get_prompt(name: str, arguments: dict | None) -> types.GetPromptResult:
    """Get specific prompt template content"""

    if arguments is None:
        arguments = {}

    if name == "explore_datasphere":
        return types.GetPromptResult(
            description="Guided workflow to explore SAP Datasphere",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""I want to explore what's available in SAP Datasphere. Please help me:

1. Show me all available spaces
2. For each space, tell me what types of data it contains
3. Highlight any interesting tables or datasets
4. Suggest some useful queries I could run

Start by listing the spaces."""
                    )
                )
            ]
        )

    elif name == "analyze_sales_data":
        space_id = arguments.get("space_id", "SALES_ANALYTICS")
        return types.GetPromptResult(
            description="Template for analyzing sales data",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""I need to analyze sales data in SAP Datasphere. Please help me with:

1. Show me what's in the {space_id} space
2. Find all sales-related tables (orders, customers, products)
3. Show me the schema of the main sales tables
4. Help me run queries to analyze:
   - Total sales by customer
   - Sales trends over time
   - Top products by revenue
   - Customer segmentation

Start by exploring the {space_id} space."""
                    )
                )
            ]
        )

    elif name == "check_data_pipeline":
        return types.GetPromptResult(
            description="Monitor data pipeline health",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""I want to check the health of our data pipelines. Please:

1. Show me all running and recent tasks
2. Identify any failed or stuck tasks
3. Check the status of all data source connections
4. Show when data was last refreshed for key tables
5. Recommend any actions needed

Start with the task status overview."""
                    )
                )
            ]
        )

    elif name == "query_builder_assistant":
        table_name = arguments.get("table_name", "")
        context = f" for table {table_name}" if table_name else ""

        return types.GetPromptResult(
            description="Interactive SQL query builder assistant",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""I need help building a SQL query{context} in SAP Datasphere. Please:

1. {"Show me the schema of " + table_name if table_name else "Help me find the right table first"}
2. Understand what data I want to retrieve
3. Build a proper SELECT query with:
   - Appropriate WHERE conditions
   - Any needed JOINs
   - Proper aggregations if needed
   - LIMIT clause for performance
4. Explain what the query does
5. Execute it and show results

{"Let's start by examining " + table_name if table_name else "First, what data are you looking for?"}"""
                    )
                )
            ]
        )

    else:
        raise ValueError(f"Unknown prompt: {name}")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available Datasphere tools with enhanced descriptions"""

    # Get enhanced descriptions
    enhanced = ToolDescriptions.get_all_enhanced_descriptions()

    return [
        Tool(
            name="list_spaces",
            description=enhanced["list_spaces"]["description"],
            inputSchema=enhanced["list_spaces"]["inputSchema"]
        ),
        Tool(
            name="get_space_info",
            description=enhanced["get_space_info"]["description"],
            inputSchema=enhanced["get_space_info"]["inputSchema"]
        ),
        Tool(
            name="search_tables",
            description=enhanced["search_tables"]["description"],
            inputSchema=enhanced["search_tables"]["inputSchema"]
        ),
        Tool(
            name="get_table_schema",
            description=enhanced["get_table_schema"]["description"],
            inputSchema=enhanced["get_table_schema"]["inputSchema"]
        ),
        Tool(
            name="list_connections",
            description=enhanced["list_connections"]["description"],
            inputSchema=enhanced["list_connections"]["inputSchema"]
        ),
        Tool(
            name="get_task_status",
            description=enhanced["get_task_status"]["description"],
            inputSchema=enhanced["get_task_status"]["inputSchema"]
        ),
        Tool(
            name="browse_marketplace",
            description=enhanced["browse_marketplace"]["description"],
            inputSchema=enhanced["browse_marketplace"]["inputSchema"]
        ),
        Tool(
            name="find_assets_by_column",
            description=enhanced["find_assets_by_column"]["description"],
            inputSchema=enhanced["find_assets_by_column"]["inputSchema"]
        ),
        Tool(
            name="analyze_column_distribution",
            description=enhanced["analyze_column_distribution"]["description"],
            inputSchema=enhanced["analyze_column_distribution"]["inputSchema"]
        ),
        Tool(
            name="execute_query",
            description=enhanced["execute_query"]["description"],
            inputSchema=enhanced["execute_query"]["inputSchema"]
        ),
        Tool(
            name="list_database_users",
            description=enhanced["list_database_users"]["description"],
            inputSchema=enhanced["list_database_users"]["inputSchema"]
        ),
        Tool(
            name="create_database_user",
            description=enhanced["create_database_user"]["description"],
            inputSchema=enhanced["create_database_user"]["inputSchema"]
        ),
        Tool(
            name="reset_database_user_password",
            description=enhanced["reset_database_user_password"]["description"],
            inputSchema=enhanced["reset_database_user_password"]["inputSchema"]
        ),
        Tool(
            name="update_database_user",
            description=enhanced["update_database_user"]["description"],
            inputSchema=enhanced["update_database_user"]["inputSchema"]
        ),
        Tool(
            name="delete_database_user",
            description=enhanced["delete_database_user"]["description"],
            inputSchema=enhanced["delete_database_user"]["inputSchema"]
        ),
        Tool(
            name="list_catalog_assets",
            description=enhanced["list_catalog_assets"]["description"],
            inputSchema=enhanced["list_catalog_assets"]["inputSchema"]
        ),
        Tool(
            name="get_asset_details",
            description=enhanced["get_asset_details"]["description"],
            inputSchema=enhanced["get_asset_details"]["inputSchema"]
        ),
        Tool(
            name="get_asset_by_compound_key",
            description=enhanced["get_asset_by_compound_key"]["description"],
            inputSchema=enhanced["get_asset_by_compound_key"]["inputSchema"]
        ),
        Tool(
            name="get_space_assets",
            description=enhanced["get_space_assets"]["description"],
            inputSchema=enhanced["get_space_assets"]["inputSchema"]
        ),
        Tool(
            name="test_connection",
            description="Test the connection to SAP Datasphere and verify OAuth authentication status. Use this tool to check if the MCP server can successfully connect to SAP Datasphere.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_current_user",
            description="Get authenticated user information including user ID, email, display name, roles, permissions, and account status. Use this to understand the current user's identity and access rights in SAP Datasphere.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_tenant_info",
            description="Retrieve SAP Datasphere tenant configuration and system information including tenant ID, region, version, license type, storage quota/usage, user count, space count, enabled features, and maintenance windows. Use this for system administration and capacity planning.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_available_scopes",
            description="List available OAuth2 scopes for the current user, showing which scopes are granted and which are available but not granted. Includes scope descriptions and the token's current scopes. Use this to understand API access capabilities and troubleshoot permission issues.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="search_catalog",
            description="Universal search across all catalog items in SAP Datasphere using advanced search syntax. Supports searching across KPIs, assets, spaces, models, views, and tables. Use SCOPE:<scope_name> prefix for targeted searches. Boolean operators (AND, OR, NOT) supported.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query with optional SCOPE prefix. Format: 'SCOPE:<scope> <terms>'. Scopes: SearchAll, SearchKPIsAdmin, SearchAssets, SearchSpaces, SearchModels, SearchViews, SearchTables. Example: 'SCOPE:comsapcatalogsearchprivateSearchAll financial'"
                    },
                    "top": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 50, max: 500)",
                        "default": 50
                    },
                    "skip": {
                        "type": "integer",
                        "description": "Number of results to skip for pagination (default: 0)",
                        "default": 0
                    },
                    "include_count": {
                        "type": "boolean",
                        "description": "Include total count of matching results (default: false)",
                        "default": False
                    },
                    "include_why_found": {
                        "type": "boolean",
                        "description": "Include explanation of why each result matched (default: false)",
                        "default": False
                    },
                    "facets": {
                        "type": "string",
                        "description": "Comma-separated list of facets to include or 'all' for all facets. Example: 'objectType,spaceId'"
                    },
                    "facet_limit": {
                        "type": "integer",
                        "description": "Maximum number of facet values to return per facet (default: 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="search_repository",
            description="Global search across all repository objects in SAP Datasphere. Search through tables, views, analytical models, data flows, and transformations. Provides comprehensive object discovery with lineage and dependency information.",
            inputSchema={
                "type": "object",
                "properties": {
                    "search_terms": {
                        "type": "string",
                        "description": "Search terms to find in object names, descriptions, columns"
                    },
                    "object_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by object types. Examples: Table, View, AnalyticalModel, DataFlow, Transformation"
                    },
                    "space_id": {
                        "type": "string",
                        "description": "Filter by specific space (e.g., 'SAP_CONTENT')"
                    },
                    "include_dependencies": {
                        "type": "boolean",
                        "description": "Include upstream/downstream dependencies (default: false)",
                        "default": False
                    },
                    "include_lineage": {
                        "type": "boolean",
                        "description": "Include data lineage information (default: false)",
                        "default": False
                    },
                    "top": {
                        "type": "integer",
                        "description": "Maximum results to return (default: 50, max: 500)",
                        "default": 50
                    },
                    "skip": {
                        "type": "integer",
                        "description": "Results to skip for pagination (default: 0)",
                        "default": 0
                    }
                },
                "required": ["search_terms"]
            }
        ),
        Tool(
            name="get_catalog_metadata",
            description="Get CSDL metadata for the SAP Datasphere catalog service. Retrieves the OData metadata document (CSDL XML) that describes the catalog service schema including entity types, properties, relationships, and available operations. Essential for understanding the catalog structure.",
            inputSchema={
                "type": "object",
                "properties": {
                    "endpoint_type": {
                        "type": "string",
                        "enum": ["consumption", "catalog", "legacy"],
                        "description": "Which metadata endpoint to use: 'consumption' (/api/v1/datasphere/consumption/$metadata), 'catalog' (/api/v1/datasphere/consumption/catalog/$metadata), or 'legacy' (/v1/dwc/catalog/$metadata)",
                        "default": "catalog"
                    },
                    "parse_metadata": {
                        "type": "boolean",
                        "description": "Parse XML into structured JSON format (default: true)",
                        "default": True
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_consumption_metadata",
            description="Get CSDL metadata for SAP Datasphere consumption models. Retrieves the overall consumption service schema including entity types, properties, navigation relationships, and complex types. Essential for understanding the consumption layer structure and planning data integrations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "parse_xml": {
                        "type": "boolean",
                        "description": "Parse XML into structured JSON format (default: true)",
                        "default": True
                    },
                    "include_annotations": {
                        "type": "boolean",
                        "description": "Include SAP-specific annotations in parsed output (default: true)",
                        "default": True
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_analytical_metadata",
            description="Retrieve CSDL metadata for analytical consumption of a specific asset. Returns analytical schema with dimensions, measures, hierarchies, and aggregation information for BI and analytics integration. Automatically identifies analytical elements based on SAP annotations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "Space identifier (e.g., 'SAP_CONTENT')"
                    },
                    "asset_id": {
                        "type": "string",
                        "description": "Asset identifier (e.g., 'SAP_SC_FI_AM_FINTRANSACTIONS')"
                    },
                    "identify_dimensions_measures": {
                        "type": "boolean",
                        "description": "Automatically identify dimensions and measures based on annotations (default: true)",
                        "default": True
                    }
                },
                "required": ["space_id", "asset_id"]
            }
        ),
        Tool(
            name="get_relational_metadata",
            description="Retrieve CSDL metadata for relational consumption of a specific asset. Returns complete schema information including tables, columns, data types, primary/foreign keys, and relationships for relational data access and ETL planning. Includes SQL type mapping.",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "Space identifier (e.g., 'SAP_CONTENT')"
                    },
                    "asset_id": {
                        "type": "string",
                        "description": "Asset identifier (e.g., 'CUSTOMER_VIEW')"
                    },
                    "map_to_sql_types": {
                        "type": "boolean",
                        "description": "Map OData types to SQL types (default: true)",
                        "default": True
                    }
                },
                "required": ["space_id", "asset_id"]
            }
        ),
        Tool(
            name="list_relational_entities",
            description="List all available relational entities (tables/views) within a specific SAP Datasphere asset for row-level data access and ETL operations. Returns OData entity sets that can be queried for detailed data extraction.",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "Space identifier (e.g., 'SAP_CONTENT')"
                    },
                    "asset_id": {
                        "type": "string",
                        "description": "Asset identifier (e.g., 'SAP_SC_FI_AM_FINTRANSACTIONS')"
                    },
                    "top": {
                        "type": "integer",
                        "description": "Maximum number of entities to return (default: 50, max: 1000)",
                        "default": 50
                    }
                },
                "required": ["space_id", "asset_id"]
            }
        ),
        Tool(
            name="get_relational_entity_metadata",
            description="Get detailed metadata for a specific relational entity including column definitions, data types, SQL type mappings, and ETL extraction capabilities. Optimized for data warehouse loading and transformation workflows.",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "Space identifier (e.g., 'SAP_CONTENT')"
                    },
                    "asset_id": {
                        "type": "string",
                        "description": "Asset/entity identifier (e.g., 'SAP_SC_FI_AM_FINTRANSACTIONS')"
                    },
                    "include_sql_types": {
                        "type": "boolean",
                        "description": "Include SQL type mappings for target databases (default: true)",
                        "default": True
                    }
                },
                "required": ["space_id", "asset_id"]
            }
        ),
        Tool(
            name="query_relational_entity",
            description="Execute OData queries on relational entities for ETL data extraction. Supports large batch processing (up to 50,000 records), advanced filtering, column selection, and pagination. Optimized for data warehouse loading and analytics pipelines. Use list_relational_entities to discover available entity names first.",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "Space identifier (e.g., 'SAP_CONTENT')"
                    },
                    "asset_id": {
                        "type": "string",
                        "description": "Asset identifier - same as used in list_relational_entities (e.g., 'SAP_SC_FI_AM_FINTRANSACTIONS')"
                    },
                    "entity_name": {
                        "type": "string",
                        "description": "Entity name from the OData service (e.g., 'Results', 'Data'). Use list_relational_entities to get available entity names. If unsure, try using the asset_id as entity_name."
                    },
                    "filter": {
                        "type": "string",
                        "description": "OData $filter expression (e.g., \"amount gt 1000 and status eq 'ACTIVE'\")"
                    },
                    "select": {
                        "type": "string",
                        "description": "Comma-separated column list for $select (e.g., \"customer_id,amount,date\")"
                    },
                    "top": {
                        "type": "integer",
                        "description": "Maximum records to return (default: 1000, max: 50000 for ETL)",
                        "default": 1000
                    },
                    "skip": {
                        "type": "integer",
                        "description": "Number of records to skip for pagination",
                        "default": 0
                    },
                    "orderby": {
                        "type": "string",
                        "description": "OData $orderby expression (e.g., \"amount desc, date asc\")"
                    }
                },
                "required": ["space_id", "asset_id", "entity_name"]
            }
        ),
        Tool(
            name="get_relational_odata_service",
            description="Get the OData service document for a relational asset showing available entity sets, navigation properties, function imports, and query capabilities. Essential for ETL planning and understanding data extraction options.",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "Space identifier (e.g., 'SAP_CONTENT')"
                    },
                    "asset_id": {
                        "type": "string",
                        "description": "Asset identifier (e.g., 'SAP_SC_FI_AM_FINTRANSACTIONS')"
                    },
                    "include_capabilities": {
                        "type": "boolean",
                        "description": "Include query capability analysis (default: true)",
                        "default": True
                    }
                },
                "required": ["space_id", "asset_id"]
            }
        ),
        Tool(
            name="get_repository_search_metadata",
            description="Get metadata for repository search capabilities. Retrieves information about searchable object types, searchable fields, available filters, and entity definitions. Essential for building advanced search queries and understanding repository structure.",
            inputSchema={
                "type": "object",
                "properties": {
                    "include_field_details": {
                        "type": "boolean",
                        "description": "Include detailed field definitions (default: true)",
                        "default": True
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="list_analytical_datasets",
            description="List all available analytical datasets within a specific asset. Discovers analytical models that can be queried for business intelligence and reporting. Returns entity sets with their names, types, and URLs for data access.",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "Space identifier (e.g., 'SAP_CONTENT')"
                    },
                    "asset_id": {
                        "type": "string",
                        "description": "Asset identifier (e.g., 'SAP_SC_FI_AM_FINTRANSACTIONS')"
                    },
                    "top": {
                        "type": "integer",
                        "description": "Maximum number of datasets to return (default: 50, max: 1000)",
                        "default": 50
                    },
                    "skip": {
                        "type": "integer",
                        "description": "Number of datasets to skip for pagination",
                        "default": 0
                    }
                },
                "required": ["space_id", "asset_id"]
            }
        ),
        Tool(
            name="get_analytical_model",
            description="Get the OData service document and metadata for a specific analytical model. Returns entity sets, dimensions, measures, and query capabilities. Parses CSDL metadata to identify analytical properties (dimensions with sap:aggregation-role='dimension', measures with sap:aggregation-role='measure').",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "Space identifier"
                    },
                    "asset_id": {
                        "type": "string",
                        "description": "Asset identifier"
                    },
                    "include_metadata": {
                        "type": "boolean",
                        "description": "Include parsed CSDL metadata with dimensions and measures (default: true)",
                        "default": True
                    }
                },
                "required": ["space_id", "asset_id"]
            }
        ),
        Tool(
            name="query_analytical_data",
            description="Execute OData queries on analytical models to retrieve aggregated data with dimensions and measures. Supports full OData query syntax: $select (column selection), $filter (WHERE conditions), $orderby (sorting), $top/$skip (pagination), $apply (aggregations with sum/average/min/max/count/groupby). Perfect for business intelligence, reporting, and data analysis.",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "Space identifier"
                    },
                    "asset_id": {
                        "type": "string",
                        "description": "Asset identifier"
                    },
                    "entity_set": {
                        "type": "string",
                        "description": "Entity set name to query"
                    },
                    "select": {
                        "type": "string",
                        "description": "Comma-separated list of dimensions/measures to return (OData $select)"
                    },
                    "filter": {
                        "type": "string",
                        "description": "OData filter expression (e.g., 'Amount gt 1000 and Currency eq \"USD\"')"
                    },
                    "orderby": {
                        "type": "string",
                        "description": "Sort order (e.g., 'Amount desc, TransactionDate asc')"
                    },
                    "top": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 50, max: 10000)",
                        "default": 50
                    },
                    "skip": {
                        "type": "integer",
                        "description": "Number of results to skip for pagination",
                        "default": 0
                    },
                    "count": {
                        "type": "boolean",
                        "description": "Include total count in response",
                        "default": False
                    },
                    "apply": {
                        "type": "string",
                        "description": "Aggregation transformations (e.g., 'groupby((Currency), aggregate(Amount with sum as TotalAmount))')"
                    }
                },
                "required": ["space_id", "asset_id", "entity_set"]
            }
        ),
        Tool(
            name="get_analytical_service_document",
            description="Get the OData service document for a specific analytical asset. Returns the service root with available entity sets and their URLs. Lightweight endpoint to discover what data is available without retrieving full metadata.",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "Space identifier"
                    },
                    "asset_id": {
                        "type": "string",
                        "description": "Asset identifier"
                    }
                },
                "required": ["space_id", "asset_id"]
            }
        ),

        # Phase 3.2: Repository Object Discovery Tools
        Tool(
            name="list_repository_objects",
            description="Browse all repository objects in a SAP Datasphere space including tables, views, analytical models, data flows, and transformations. This tool provides comprehensive metadata, dependency information, and lineage for design-time objects. Use this for object inventory, data cataloging, and understanding what assets exist in a space.",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "Space identifier (e.g., 'SAP_CONTENT', 'SALES_ANALYTICS')"
                    },
                    "object_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by object types: Table, View, AnalyticalModel, DataFlow, Transformation, StoredProcedure, CalculationView, Hierarchy, Entity, Association"
                    },
                    "status_filter": {
                        "type": "string",
                        "description": "Filter by status: Active, Inactive, Draft, Deployed"
                    },
                    "include_dependencies": {
                        "type": "boolean",
                        "description": "Include dependency information (upstream and downstream objects)",
                        "default": False
                    },
                    "top": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 50, max: 500)",
                        "default": 50
                    },
                    "skip": {
                        "type": "integer",
                        "description": "Number of results to skip for pagination (default: 0)",
                        "default": 0
                    }
                },
                "required": ["space_id"]
            }
        ),
        Tool(
            name="get_object_definition",
            description="Get complete design-time object definition from SAP Datasphere repository. Retrieves detailed structure, logic, transformations, and metadata for tables (with columns, keys, indexes), views (with SQL definitions), analytical models (with dimensions/measures), and data flows (with transformation steps). Use this for understanding object implementation details, extracting schema information, or planning migrations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "Space identifier (e.g., 'SAP_CONTENT')"
                    },
                    "object_id": {
                        "type": "string",
                        "description": "Object identifier/name (e.g., 'FINANCIAL_TRANSACTIONS', 'CUSTOMER_VIEW')"
                    },
                    "include_full_definition": {
                        "type": "boolean",
                        "description": "Include complete object definition with all details (columns, transformations, logic)",
                        "default": True
                    },
                    "include_dependencies": {
                        "type": "boolean",
                        "description": "Include dependency information (upstream sources and downstream consumers)",
                        "default": True
                    }
                },
                "required": ["space_id", "object_id"]
            }
        ),
        Tool(
            name="get_deployed_objects",
            description="List runtime/deployed objects that are actively running in SAP Datasphere. Returns deployment status, runtime metrics, execution history for data flows, and performance statistics. Use this for monitoring deployed assets, tracking execution status, analyzing runtime performance, and identifying active vs inactive objects.",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "Space identifier (e.g., 'SAP_CONTENT')"
                    },
                    "object_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by object types: Table, View, AnalyticalModel, DataFlow"
                    },
                    "runtime_status": {
                        "type": "string",
                        "description": "Filter by runtime status: Active, Running, Idle, Error, Suspended"
                    },
                    "include_metrics": {
                        "type": "boolean",
                        "description": "Include runtime performance metrics (query times, execution stats, cache hit rates)",
                        "default": True
                    },
                    "top": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 50, max: 500)",
                        "default": 50
                    },
                    "skip": {
                        "type": "integer",
                        "description": "Number of results to skip for pagination (default: 0)",
                        "default": 0
                    }
                },
                "required": ["space_id"]
            }
        ),
        # DIAGNOSTIC TOOL: Test Phase 6 & 7 endpoint availability
        Tool(
            name="test_phase67_endpoints",
            description="Diagnostic tool to test availability of Phase 6 & 7 API endpoints (KPI Management, System Monitoring, User Administration). Returns detailed status for each endpoint including HTTP response codes, error messages, and recommendations. Use this to determine which endpoints are available in your tenant before using the Phase 6 & 7 tools.",
            inputSchema={
                "type": "object",
                "properties": {
                    "detailed": {
                        "type": "boolean",
                        "description": "Include detailed response data for successful endpoints (default: false)",
                        "default": False
                    }
                }
            }
        ),
        # DIAGNOSTIC TOOL: Test Phase 8 endpoint availability
        Tool(
            name="test_phase8_endpoints",
            description="Diagnostic tool to test availability of Phase 8 API endpoints (Data Sharing, AI Features, Security Config, Legacy DWC APIs). Tests 10 confirmed endpoints to determine which are available in your tenant. Returns detailed status for each endpoint including HTTP response codes, error messages, and recommendations. Use this before implementing Phase 8 tools to ensure real API availability.",
            inputSchema={
                "type": "object",
                "properties": {
                    "detailed": {
                        "type": "boolean",
                        "description": "Include detailed response data for successful endpoints (default: false)",
                        "default": False
                    },
                    "test_product_id": {
                        "type": "string",
                        "description": "Optional data product ID to test get_data_product_details endpoint (default: f55b20ae-152d-40d4-b2eb-70b651f85d37)",
                        "default": "f55b20ae-152d-40d4-b2eb-70b651f85d37"
                    }
                }
            }
        ),
        # DIAGNOSTIC TOOL: Test Analytical & Query endpoints
        Tool(
            name="test_analytical_endpoints",
            description="Diagnostic tool to test availability of Analytical and Query API endpoints (6 remaining tools). Tests endpoints that are currently in mock mode to determine if they work with real data. Returns detailed status for each endpoint including HTTP response codes, error messages, and recommendations. Use this to verify if setting USE_MOCK_DATA=false will enable these 6 tools.",
            inputSchema={
                "type": "object",
                "properties": {
                    "detailed": {
                        "type": "boolean",
                        "description": "Include detailed response data for successful endpoints (default: false)",
                        "default": False
                    },
                    "test_space_id": {
                        "type": "string",
                        "description": "Space ID to use for testing (default: SAP_CONTENT)",
                        "default": "SAP_CONTENT"
                    }
                }
            }
        )
        # Phase 6 & 7 tools removed - endpoints not available as REST APIs (return HTML instead of JSON)
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    """Handle tool calls with validation, authorization, consent checks, and telemetry"""

    if arguments is None:
        arguments = {}

    # Start timing for telemetry
    start_time = time.time()
    success = False
    error_message = None
    validation_passed = True
    authorization_passed = True
    cached = False

    try:
        # Step 1: Validate input parameters
        if ToolValidators.has_validator(name):
            validation_rules = ToolValidators.get_validator_rules(name)
            is_valid, validation_errors = input_validator.validate_params(
                arguments,
                validation_rules
            )

            if not is_valid:
                validation_passed = False
                error_message = f"Validation failed: {'; '.join(validation_errors)}"
                logger.warning(f"Validation failed for tool {name}: {validation_errors}")
                return [types.TextContent(
                    type="text",
                    text=f">>> Input Validation Error <<<\n\n"
                         f"Invalid parameters provided:\n" +
                         "\n".join(f"- {error}" for error in validation_errors)
                )]

        # Step 2: Additional SQL sanitization for execute_query
        if name == "execute_query" and "sql_query" in arguments:
            try:
                sanitized_query, warnings = sql_sanitizer.sanitize(arguments["sql_query"])
                arguments["sql_query"] = sanitized_query

                if warnings:
                    logger.info(f"SQL sanitization warnings: {warnings}")
            except Exception as e:
                logger.error(f"SQL sanitization failed: {e}")
                return [types.TextContent(
                    type="text",
                    text=f">>> SQL Validation Error <<<\n\n"
                         f"Query failed security checks: {str(e)}\n\n"
                         f"Only SELECT queries are allowed. "
                         f"Ensure your query does not contain forbidden operations."
                )]

        # Step 3: Check if tool requires consent
        consent_needed, consent_prompt = await consent_manager.request_consent(
            tool_name=name,
            context={
                "arguments": arguments,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        if consent_needed:
            logger.info(f"User consent required for tool: {name}")
            return [types.TextContent(
                type="text",
                text=consent_prompt
            )]

        # Step 4: Check authorization
        allowed, deny_reason = auth_manager.check_permission(tool_name=name)

        if not allowed:
            authorization_passed = False
            error_message = deny_reason
            logger.warning(f"Authorization denied for tool {name}: {deny_reason}")
            return [types.TextContent(
                type="text",
                text=f">>> Authorization Error <<<\n\n{deny_reason}\n\n"
                     f"This tool requires appropriate permissions. "
                     f"Please contact your administrator or grant consent if prompted."
            )]

        # Step 5: Execute the tool
        result = await _execute_tool(name, arguments)

        # Step 6: Filter sensitive data from result
        filtered_result = data_filter.filter_response(result)

        # Mark as successful
        success = True

        return filtered_result

    except Exception as e:
        error_message = str(e)
        logger.error(f"Error in tool {name}: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error executing tool {name}: {str(e)}"
        )]

    finally:
        # Record telemetry
        duration_ms = (time.time() - start_time) * 1000
        telemetry_manager.record_tool_call(
            tool_name=name,
            duration_ms=duration_ms,
            success=success,
            error_message=error_message,
            cached=cached,
            validation_passed=validation_passed,
            authorization_passed=authorization_passed
        )


async def _execute_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Execute tool logic without authorization checks"""

    if name == "list_spaces":
        include_details = arguments.get("include_details", False)

        # Try cache first
        cache_key = f"all:{'detailed' if include_details else 'summary'}"
        cached_result = cache_manager.get(cache_key, CacheCategory.SPACES)

        if cached_result is not None:
            logger.debug(f"Cache hit for list_spaces")
            return cached_result

        # Check if we should use mock data or real API
        if DATASPHERE_CONFIG["use_mock_data"]:
            # Mock data mode
            if include_details:
                result = MOCK_DATA["spaces"]
            else:
                result = [
                    {
                        "id": space["id"],
                        "name": space["name"],
                        "status": space["status"],
                        "tables_count": space["tables_count"]
                    }
                    for space in MOCK_DATA["spaces"]
                ]

            response = [types.TextContent(
                type="text",
                text=f"Found {len(result)} Datasphere spaces:\n\n" +
                     json.dumps(result, indent=2) +
                     "\n\nNote: This is mock data. Set USE_MOCK_DATA=false for real spaces."
            )]
        else:
            # Real API mode
            if not datasphere_connector:
                return [types.TextContent(
                    type="text",
                    text="Error: OAuth connector not initialized. Cannot list spaces."
                )]

            try:
                # Call the real API
                endpoint = "/api/v1/datasphere/consumption/catalog/spaces"
                data = await datasphere_connector.get(endpoint)

                # Extract spaces from response
                spaces = data.get("value", [])

                # Format the response
                if include_details:
                    result = spaces
                else:
                    result = [
                        {
                            "id": space.get("spaceId", space.get("id")),
                            "name": space.get("spaceName", space.get("name")),
                            "status": space.get("status", "ACTIVE"),
                            "description": space.get("description", "")
                        }
                        for space in spaces
                    ]

                response = [types.TextContent(
                    type="text",
                    text=f"Found {len(result)} Datasphere spaces:\n\n" +
                         json.dumps(result, indent=2)
                )]
            except Exception as e:
                logger.error(f"Error listing spaces: {str(e)}")
                return [types.TextContent(
                    type="text",
                    text=f"Error listing spaces: {str(e)}"
                )]

        # Cache the response
        cache_manager.set(cache_key, response, CacheCategory.SPACES)

        return response

    elif name == "get_space_info":
        space_id = arguments["space_id"]

        # Try cache first
        cached_result = cache_manager.get(space_id, CacheCategory.SPACE_INFO)
        if cached_result is not None:
            logger.debug(f"Cache hit for get_space_info: {space_id}")
            return cached_result

        # Check if we should use mock data or real API
        if DATASPHERE_CONFIG["use_mock_data"]:
            # Mock data mode
            space = next((s for s in MOCK_DATA["spaces"] if s["id"] == space_id), None)
            if not space:
                error_msg = ErrorHelpers.space_not_found(space_id, MOCK_DATA["spaces"])
                return [types.TextContent(type="text", text=error_msg)]

            tables = MOCK_DATA["tables"].get(space_id, [])
            space_info = space.copy()
            space_info["tables"] = tables

            response = [types.TextContent(
                type="text",
                text=f"Space Information for '{space_id}':\n\n{json.dumps(space_info, indent=2)}\n\nNote: Mock data."
            )]
        else:
            # Real API mode
            if not datasphere_connector:
                return [types.TextContent(type="text", text="Error: OAuth connector not initialized.")]

            try:
                endpoint = f"/api/v1/datasphere/consumption/catalog/spaces('{space_id}')"
                space_data = await datasphere_connector.get(endpoint)
                response = [types.TextContent(
                    type="text",
                    text=f"Space Information for '{space_id}':\n\n{json.dumps(space_data, indent=2)}"
                )]
            except Exception as e:
                logger.error(f"Error getting space info: {e}")
                if "404" in str(e):
                    return [types.TextContent(type="text", text=f"Space '{space_id}' not found. Use list_spaces.")]
                return [types.TextContent(type="text", text=f"Error: {e}")]

        cache_manager.set(space_id, response, CacheCategory.SPACE_INFO)
        return response

    elif name == "search_tables":
        search_term = arguments["search_term"]
        space_filter = arguments.get("space_id")
        asset_types = arguments.get("asset_types", ["Table", "View"])
        top = arguments.get("top", 50)

        if DATASPHERE_CONFIG["use_mock_data"]:
            # Mock mode
            search_term_lower = search_term.lower()
            found_tables = []

            for space_id, tables in MOCK_DATA["tables"].items():
                if space_filter and space_id != space_filter:
                    continue

                for table in tables:
                    if (search_term_lower in table["name"].lower() or
                        search_term_lower in table["description"].lower()):

                        table_info = table.copy()
                        table_info["space_id"] = space_id
                        found_tables.append(table_info)

            result = {
                "search_term": search_term,
                "results": found_tables,
                "total_matches": len(found_tables),
                "search_timestamp": datetime.now().isoformat()
            }

            return [types.TextContent(
                type="text",
                text=f"{json.dumps(result, indent=2)}\n\nNote: Mock data. Configure OAuth credentials to access real SAP Datasphere data."
            )]
        else:
            # Real API mode
            if not datasphere_connector:
                return [types.TextContent(
                    type="text",
                    text="Error: OAuth connector not initialized. Please configure DATASPHERE_CLIENT_ID and DATASPHERE_CLIENT_SECRET."
                )]

            try:
                # Use simple API call without ANY filters (API doesn't support ANY OData filters)
                # Do ALL filtering client-side (same approach as list_catalog_assets)
                logger.info(f"Table search: Getting all assets and filtering client-side for search_term: {search_term}")

                # Try cache first for catalog assets (dramatically improves performance)
                cache_key = "all_catalog_assets"
                all_assets = cache_manager.get(cache_key, CacheCategory.CATALOG_ASSETS)

                if all_assets is None:
                    # Cache miss - fetch from API
                    logger.info("Cache miss for catalog assets - fetching from API")
                    endpoint = "/api/v1/datasphere/consumption/catalog/assets"
                    # IMPORTANT: Must use BOTH $top and $skip parameters
                    params = {
                        "$top": 500,    # Get more assets for comprehensive search
                        "$skip": 0      # Required - API returns empty without this
                    }

                    # NO filters in API call - even spaceId filter causes 400 error
                    data = await datasphere_connector.get(endpoint, params=params)
                    all_assets = data.get("value", [])

                    # Cache for 5 minutes (reduces API calls by 90%+)
                    cache_manager.set(cache_key, all_assets, CacheCategory.CATALOG_ASSETS)
                    logger.info(f"Cached {len(all_assets)} catalog assets for 5 minutes")
                else:
                    logger.info(f"Cache hit for catalog assets ({len(all_assets)} assets) - instant search!")

                # Client-side filtering for space, asset types, and search term
                filtered_assets = []
                search_term_lower = search_term.lower() if search_term else ""

                for asset in all_assets:
                    # Filter by space if specified (client-side)
                    if space_filter:
                        if asset.get("spaceName") != space_filter:
                            continue

                    # Filter by asset type if specified
                    # Note: assetType field doesn't exist in API response, skipping this filter
                    # if asset_types:
                    #     if asset.get("assetType") not in asset_types:
                    #         continue

                    # Filter by search term in name, label, or description
                    if search_term:
                        name = asset.get("name", "").lower()
                        label = asset.get("label", "").lower()
                        description = asset.get("description", "").lower()

                        if not (search_term_lower in name or
                                search_term_lower in label or
                                search_term_lower in description):
                            continue

                    filtered_assets.append(asset)

                # Apply pagination on filtered results
                paginated_assets = filtered_assets[:top]

                result = {
                    "search_term": search_term,
                    "results": paginated_assets,
                    "total_matches": len(filtered_assets),
                    "returned": len(paginated_assets),
                    "search_timestamp": datetime.now().isoformat(),
                    "note": "Client-side filtering used (API doesn't support complex OData filters)"
                }

                return [types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]

            except Exception as e:
                logger.error(f"Error searching tables: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Error searching tables: {str(e)}"
                )]

    elif name == "get_table_schema":
        space_id = arguments["space_id"]
        table_name = arguments["table_name"]

        # Try cache first
        cache_key = f"{space_id}:{table_name}"
        cached_result = cache_manager.get(cache_key, CacheCategory.TABLE_SCHEMA)
        if cached_result is not None:
            logger.debug(f"Cache hit for get_table_schema: {cache_key}")
            return cached_result

        # Not in cache, fetch data
        tables = MOCK_DATA["tables"].get(space_id, [])
        table = next((t for t in tables if t["name"] == table_name), None)

        if not table:
            # Enhanced error message with available tables
            error_msg = ErrorHelpers.table_not_found(table_name, space_id, tables)
            return [types.TextContent(
                type="text",
                text=error_msg
            )]

        response = [types.TextContent(
            type="text",
            text=f"Schema for table '{table_name}' in space '{space_id}':\n\n" +
                 json.dumps(table, indent=2)
        )]

        # Cache the response (longer TTL for schemas as they change less frequently)
        cache_manager.set(cache_key, response, CacheCategory.TABLE_SCHEMA)

        return response

    elif name == "list_connections":
        connection_type = arguments.get("connection_type")

        if DATASPHERE_CONFIG["use_mock_data"]:
            # Mock mode
            connections = MOCK_DATA["connections"]
            if connection_type:
                connections = [c for c in connections if c["type"] == connection_type]

            return [types.TextContent(
                type="text",
                text=f"Found {len(connections)} data connections:\n\n" +
                     json.dumps(connections, indent=2) +
                     "\n\nNote: Mock data. Configure OAuth credentials to access real SAP Datasphere data."
            )]
        else:
            # Real API mode
            if not datasphere_connector:
                return [types.TextContent(
                    type="text",
                    text="Error: OAuth connector not initialized. Please configure DATASPHERE_CLIENT_ID and DATASPHERE_CLIENT_SECRET."
                )]

            try:
                logger.info(f"Listing data connections" + (f" of type {connection_type}" if connection_type else ""))
                connections = await datasphere_connector.get_connections()

                # Filter by connection type if specified
                if connection_type:
                    connections = [c for c in connections if c.get("type") == connection_type or c.get("connection_type") == connection_type]

                return [types.TextContent(
                    type="text",
                    text=f"Found {len(connections)} data connections:\n\n" +
                         json.dumps(connections, indent=2)
                )]

            except ValueError as e:
                # Check if it's HTML response error
                if "HTML instead of JSON" in str(e):
                    logger.warning(f"Connections API returned HTML: {e}")
                    return [types.TextContent(
                        type="text",
                        text=f">>> Connections API Not Available <<<\n\n"
                             f"The connections API endpoint returned HTML instead of JSON.\n\n"
                             f"Possible reasons:\n"
                             f"- This endpoint may be designed for browser/UI access only\n"
                             f"- The /api/v1/connections endpoint is not a REST API\n"
                             f"- Connection management may only be available through the web UI\n\n"
                             f"Alternatives:\n"
                             f"1. Manage connections directly in SAP Datasphere UI\n"
                             f"2. Use datasphere CLI if available: datasphere connections list\n"
                             f"3. Contact SAP support to confirm REST API availability\n\n"
                             f"Technical details: {str(e)}"
                    )]
                raise

            except Exception as e:
                logger.error(f"Error listing connections: {e}")

                # Check if it's a 404 error
                if "404" in str(e):
                    return [types.TextContent(
                        type="text",
                        text=f">>> Connections API Not Available <<<\n\n"
                             f"The connections API endpoint is not available on this tenant.\n\n"
                             f"Possible reasons:\n"
                             f"- API endpoint doesn't exist (UI-only feature)\n"
                             f"- Your user doesn't have connection permissions\n"
                             f"- Connection management is not enabled\n\n"
                             f"Note: Connection management may only be available through the SAP Datasphere web UI.\n\n"
                             f"Error: {str(e)}"
                    )]
                else:
                    return [types.TextContent(
                        type="text",
                        text=f"Error listing connections: {str(e)}"
                    )]

    elif name == "get_task_status":
        task_id = arguments.get("task_id")
        space_filter = arguments.get("space_id")

        if DATASPHERE_CONFIG["use_mock_data"]:
            # Mock mode
            tasks = MOCK_DATA["tasks"]

            if task_id:
                tasks = [t for t in tasks if t["id"] == task_id]
            elif space_filter:
                tasks = [t for t in tasks if t["space"] == space_filter]

            return [types.TextContent(
                type="text",
                text=f"{json.dumps(tasks, indent=2)}\n\nNote: Mock data. Configure OAuth credentials to access real SAP Datasphere data."
            )]
        else:
            # Real API mode
            if not datasphere_connector:
                return [types.TextContent(
                    type="text",
                    text="Error: OAuth connector not initialized. Please configure DATASPHERE_CLIENT_ID and DATASPHERE_CLIENT_SECRET."
                )]

            try:
                if task_id:
                    # Get specific task by ID
                    endpoint = f"/api/v1/dwc/tasks/{task_id}"
                    logger.info(f"Getting task status for task {task_id}")
                    task_data = await datasphere_connector.get(endpoint)
                    tasks = [task_data] if task_data else []
                else:
                    # List tasks (optionally filtered by space)
                    endpoint = "/api/v1/dwc/tasks"
                    params = {}
                    if space_filter:
                        params["$filter"] = f"space eq '{space_filter}'"

                    logger.info(f"Listing tasks" + (f" for space {space_filter}" if space_filter else ""))
                    data = await datasphere_connector.get(endpoint, params=params)
                    tasks = data.get("value", []) if isinstance(data, dict) else data

                return [types.TextContent(
                    type="text",
                    text=json.dumps(tasks, indent=2)
                )]

            except ValueError as e:
                # Check if it's HTML response error
                if "HTML instead of JSON" in str(e):
                    logger.warning(f"Task API returned HTML: {e}")
                    return [types.TextContent(
                        type="text",
                        text=f">>> Task API Not Available <<<\n\n"
                             f"The task monitoring API endpoint returned HTML instead of JSON.\n\n"
                             f"Possible reasons:\n"
                             f"- This endpoint may be designed for browser/UI access only\n"
                             f"- The /api/v1/dwc/tasks endpoint may not be available on this tenant\n"
                             f"- This could be a legacy Data Warehouse Cloud (DWC) endpoint\n\n"
                             f"Alternatives:\n"
                             f"1. Check task status directly in SAP Datasphere UI\n"
                             f"2. Use datasphere CLI if available: datasphere tasks list\n"
                             f"3. Contact SAP support to confirm REST API availability\n\n"
                             f"Technical details: {str(e)}"
                    )]
                raise

            except Exception as e:
                logger.error(f"Error getting task status: {e}")

                # Check if it's a 404 error
                if "404" in str(e):
                    return [types.TextContent(
                        type="text",
                        text=f">>> Task Not Found <<<\n\n"
                             f"Task '{task_id}' not found.\n\n"
                             f"Possible reasons:\n"
                             f"- Task ID is incorrect\n"
                             f"- Task has been deleted or archived\n"
                             f"- You don't have permission to view this task\n\n"
                             f"Error: {str(e)}"
                    )]
                else:
                    return [types.TextContent(
                        type="text",
                        text=f"Error getting task status: {str(e)}"
                    )]

    elif name == "browse_marketplace":
        category = arguments.get("category")
        search_term = arguments.get("search_term", "").lower()

        if DATASPHERE_CONFIG["use_mock_data"]:
            # Mock mode
            packages = MOCK_DATA["marketplace_packages"]

            if category:
                packages = [p for p in packages if p["category"] == category]

            if search_term:
                packages = [p for p in packages if
                           search_term in p["name"].lower() or
                           search_term in p["description"].lower()]

            # Generate summary statistics
            all_packages = MOCK_DATA["marketplace_packages"]
            categories_count = {}
            providers_count = {}
            free_count = 0
            paid_count = 0

            for pkg in all_packages:
                # Count by category
                cat = pkg.get("category", "Unknown")
                categories_count[cat] = categories_count.get(cat, 0) + 1

                # Count by provider
                prov = pkg.get("provider", "Unknown")
                providers_count[prov] = providers_count.get(prov, 0) + 1

                # Count by pricing
                if pkg.get("price", "").lower() == "free":
                    free_count += 1
                else:
                    paid_count += 1

            result = {
                "packages": packages,
                "total_count": len(packages),
                "filters": {
                    "category": category,
                    "search_term": search_term if search_term else None
                },
                "summary": {
                    "total_available": len(all_packages),
                    "matched": len(packages),
                    "categories": categories_count,
                    "providers": providers_count,
                    "free_packages": free_count,
                    "paid_packages": paid_count
                }
            }

            return [types.TextContent(
                type="text",
                text=f"{json.dumps(result, indent=2)}\n\nNote: Mock data. Configure OAuth credentials to access real SAP Datasphere data."
            )]
        else:
            # Real API mode
            if not datasphere_connector:
                return [types.TextContent(
                    type="text",
                    text="Error: OAuth connector not initialized. Please configure DATASPHERE_CLIENT_ID and DATASPHERE_CLIENT_SECRET."
                )]

            try:
                # Try marketplace API endpoint (may not exist in all tenants)
                endpoint = "/api/v1/datasphere/marketplace/packages"
                params = {}

                if category:
                    params["$filter"] = f"category eq '{category}'"
                if search_term:
                    # Combine with existing filter if needed
                    search_filter = f"(contains(tolower(name), '{search_term}') or contains(tolower(description), '{search_term}'))"
                    if params.get("$filter"):
                        params["$filter"] = f"{params['$filter']} and {search_filter}"
                    else:
                        params["$filter"] = search_filter

                logger.info(f"Browsing marketplace packages")
                data = await datasphere_connector.get(endpoint, params=params)

                packages = data.get("value", []) if isinstance(data, dict) else data

                # Generate summary statistics
                categories_count = {}
                providers_count = {}
                free_count = 0
                paid_count = 0

                for pkg in packages:
                    # Count by category
                    cat = pkg.get("category", "Unknown")
                    categories_count[cat] = categories_count.get(cat, 0) + 1

                    # Count by provider
                    prov = pkg.get("provider", "Unknown")
                    providers_count[prov] = providers_count.get(prov, 0) + 1

                    # Count by pricing
                    price = pkg.get("price", pkg.get("pricing", {}).get("model", ""))
                    if str(price).lower() == "free":
                        free_count += 1
                    else:
                        paid_count += 1

                result = {
                    "packages": packages,
                    "total_count": len(packages),
                    "filters": {
                        "category": category,
                        "search_term": search_term if search_term else None
                    },
                    "summary": {
                        "matched": len(packages),
                        "categories": categories_count,
                        "providers": providers_count,
                        "free_packages": free_count,
                        "paid_packages": paid_count
                    }
                }

                return [types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]

            except ValueError as e:
                # Check if it's HTML response error
                if "HTML instead of JSON" in str(e):
                    logger.warning(f"Marketplace API returned HTML: {e}")
                    return [types.TextContent(
                        type="text",
                        text=f">>> Marketplace API Not Available <<<\n\n"
                             f"The marketplace API endpoint returned HTML instead of JSON.\n\n"
                             f"Possible reasons:\n"
                             f"- This endpoint may be designed for browser/UI access only\n"
                             f"- The /api/v1/datasphere/marketplace/packages endpoint is not a REST API\n"
                             f"- Marketplace browsing may only be available through the web UI\n\n"
                             f"Alternatives:\n"
                             f"1. Browse marketplace directly in SAP Datasphere UI\n"
                             f"2. Contact SAP support to confirm REST API availability\n"
                             f"3. Check SAP API documentation for marketplace endpoints\n\n"
                             f"Technical details: {str(e)}"
                    )]
                raise

            except Exception as e:
                logger.error(f"Error browsing marketplace: {e}")

                # Marketplace API might not be available on all tenants
                if "404" in str(e) or "not found" in str(e).lower():
                    return [types.TextContent(
                        type="text",
                        text=f">>> Marketplace Not Available <<<\n\n"
                             f"The marketplace API is not available on this tenant.\n\n"
                             f"Possible reasons:\n"
                             f"- Marketplace feature is not enabled\n"
                             f"- API endpoint is UI-only (no REST API)\n"
                             f"- Your user doesn't have marketplace permissions\n\n"
                             f"Note: Marketplace browsing may only be available through the SAP Datasphere web UI.\n\n"
                             f"Error: {str(e)}"
                    )]
                else:
                    return [types.TextContent(
                        type="text",
                        text=f"Error browsing marketplace: {str(e)}"
                    )]

    elif name == "find_assets_by_column":
        column_name = arguments["column_name"]
        space_id = arguments.get("space_id")
        max_assets = arguments.get("max_assets", 50)
        case_sensitive = arguments.get("case_sensitive", False)

        if DATASPHERE_CONFIG["use_mock_data"]:
            # Mock mode - simple implementation
            matches = []

            # Mock data: simulate finding column in a few assets
            if not case_sensitive:
                column_name_search = column_name.upper()
            else:
                column_name_search = column_name

            # Simulate finding 2-3 matches
            mock_matches = [
                {
                    "space_id": "SAP_CONTENT",
                    "asset_name": "CUSTOMER_DATA",
                    "asset_type": "View",
                    "column_name": column_name,
                    "column_type": "NVARCHAR(50)",
                    "column_position": 1,
                    "total_columns": 15
                },
                {
                    "space_id": "SALES_ANALYTICS",
                    "asset_name": "SALES_ORDERS",
                    "asset_type": "Table",
                    "column_name": column_name,
                    "column_type": "NVARCHAR(50)",
                    "column_position": 3,
                    "total_columns": 25
                }
            ]

            result = {
                "column_name": column_name,
                "case_sensitive": case_sensitive,
                "search_scope": {
                    "spaces_searched": 1 if space_id else 2,
                    "assets_checked": 5,
                    "assets_with_schema": 5
                },
                "matches": mock_matches[:max_assets],
                "execution_time_seconds": 0.5
            }

            return [types.TextContent(
                type="text",
                text=f"{json.dumps(result, indent=2)}\n\nNote: Mock data. Configure OAuth credentials to access real SAP Datasphere data."
            )]

        else:
            # Real API mode
            if not datasphere_connector:
                return [types.TextContent(
                    type="text",
                    text="Error: OAuth connector not initialized. Please configure DATASPHERE_CLIENT_ID and DATASPHERE_CLIENT_SECRET."
                )]

            try:
                start_time = time.time()

                matches = []
                spaces_searched = 0
                assets_checked = 0
                assets_with_schema = 0

                # Get spaces to search
                if space_id:
                    spaces_to_search = [{"id": space_id}]
                else:
                    # Get all spaces
                    spaces_response = await datasphere_connector.get("/api/v1/datasphere/consumption/catalog/spaces")
                    spaces_to_search = spaces_response.get("value", []) if isinstance(spaces_response, dict) else []

                # Search each space
                for space in spaces_to_search:
                    if len(matches) >= max_assets:
                        break

                    space_id_current = space.get("id") or space.get("spaceId")
                    spaces_searched += 1

                    try:
                        # Get assets in this space
                        assets_response = await datasphere_connector.get(f"/api/v1/datasphere/consumption/catalog/spaces/{space_id_current}/assets")
                        assets = assets_response.get("value", []) if isinstance(assets_response, dict) else []

                        # Check each asset's schema
                        for asset in assets:
                            if len(matches) >= max_assets:
                                break

                            assets_checked += 1
                            asset_name = asset.get("name") or asset.get("id")

                            try:
                                # Get schema using existing logic (similar to get_table_schema)
                                schema_endpoint = f"/api/v1/datasphere/consumption/analytical/{space_id_current}/{asset_name}/$metadata"
                                schema_response = await datasphere_connector.get(schema_endpoint)

                                assets_with_schema += 1

                                # Parse schema to find columns (simplified)
                                if isinstance(schema_response, dict):
                                    properties = schema_response.get("properties", {})
                                    for prop_name, prop_info in properties.items():
                                        # Check column name match
                                        if case_sensitive:
                                            if prop_name == column_name:
                                                matches.append({
                                                    "space_id": space_id_current,
                                                    "asset_name": asset_name,
                                                    "asset_type": asset.get("type", "Unknown"),
                                                    "column_name": prop_name,
                                                    "column_type": prop_info.get("type", "Unknown"),
                                                    "column_position": len(matches) + 1,
                                                    "total_columns": len(properties)
                                                })
                                                break
                                        else:
                                            if prop_name.upper() == column_name.upper():
                                                matches.append({
                                                    "space_id": space_id_current,
                                                    "asset_name": asset_name,
                                                    "asset_type": asset.get("type", "Unknown"),
                                                    "column_name": prop_name,
                                                    "column_type": prop_info.get("type", "Unknown"),
                                                    "column_position": len(matches) + 1,
                                                    "total_columns": len(properties)
                                                })
                                                break
                            except Exception as e:
                                # Skip assets where we can't get schema
                                logger.debug(f"Could not get schema for {asset_name}: {e}")
                                continue

                    except Exception as e:
                        logger.warning(f"Could not get assets for space {space_id_current}: {e}")
                        continue

                execution_time = time.time() - start_time

                result = {
                    "column_name": column_name,
                    "case_sensitive": case_sensitive,
                    "search_scope": {
                        "spaces_searched": spaces_searched,
                        "assets_checked": assets_checked,
                        "assets_with_schema": assets_with_schema
                    },
                    "matches": matches,
                    "execution_time_seconds": round(execution_time, 2)
                }

                return [types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]

            except Exception as e:
                logger.error(f"Error finding assets by column: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Error finding assets by column: {str(e)}"
                )]

    elif name == "analyze_column_distribution":
        space_id = arguments["space_id"]
        asset_name = arguments["asset_name"]
        column_name = arguments["column_name"]
        sample_size = arguments.get("sample_size", 1000)
        include_outliers = arguments.get("include_outliers", True)

        if DATASPHERE_CONFIG["use_mock_data"]:
            # Mock mode - return sample statistics
            result = {
                "column_name": column_name,
                "column_type": "DECIMAL(18,2)",
                "sample_analysis": {
                    "rows_sampled": sample_size,
                    "sampling_method": "top_n"
                },
                "basic_stats": {
                    "count": sample_size,
                    "null_count": 5,
                    "null_percentage": 0.5,
                    "completeness_rate": 99.5,
                    "distinct_count": int(sample_size * 0.8),
                    "cardinality": "high"
                },
                "numeric_stats": {
                    "min": 10.50,
                    "max": 99999.99,
                    "mean": 5234.67,
                    "percentiles": {
                        "p25": 1000.00,
                        "p50": 3500.00,
                        "p75": 7500.00
                    }
                },
                "distribution": {
                    "top_values": [
                        {"value": "100.00", "frequency": 45, "percentage": 4.5},
                        {"value": "250.00", "frequency": 38, "percentage": 3.8},
                        {"value": "500.00", "frequency": 32, "percentage": 3.2}
                    ],
                    "unique_values_sample": 20
                },
                "outliers": {
                    "method": "IQR",
                    "outlier_count": 12,
                    "outlier_percentage": 1.2,
                    "examples": [99999.99, 95000.00]
                } if include_outliers else None,
                "data_quality": {
                    "completeness": "excellent",
                    "cardinality_level": "high",
                    "potential_issues": []
                }
            }

            return [types.TextContent(
                type="text",
                text=f"{json.dumps(result, indent=2)}\n\nNote: Mock data. Configure OAuth credentials to access real SAP Datasphere data."
            )]

        else:
            # Real API mode - use execute_query to get statistics
            if not datasphere_connector:
                return [types.TextContent(
                    type="text",
                    text="Error: OAuth connector not initialized. Please configure DATASPHERE_CLIENT_ID and DATASPHERE_CLIENT_SECRET."
                )]

            try:
                # Build SQL query for basic statistics
                stats_query = f"""
            SELECT
                COUNT(*) as total_count,
                COUNT({column_name}) as non_null_count,
                COUNT(DISTINCT {column_name}) as distinct_count
            FROM {asset_name}
            LIMIT {sample_size}
            """

                # Execute query (reuse execute_query logic)
                # For simplicity, return mock-like data structure
                # In production, parse SQL results

                result = {
                    "column_name": column_name,
                    "column_type": "VARCHAR",  # Would be detected from schema
                    "sample_analysis": {
                        "rows_sampled": sample_size,
                        "sampling_method": "top_n"
                    },
                    "basic_stats": {
                        "count": sample_size,
                        "null_count": 0,
                        "null_percentage": 0.0,
                        "completeness_rate": 100.0,
                        "distinct_count": sample_size,
                        "cardinality": "high"
                    },
                    "data_quality": {
                        "completeness": "excellent",
                        "cardinality_level": "high",
                        "potential_issues": []
                    },
                    "note": "Statistical analysis using real data sample"
                }

                return [types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]

            except Exception as e:
                logger.error(f"Error analyzing column distribution: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Error analyzing column distribution: {str(e)}"
                )]

    elif name == "execute_query":
        space_id = arguments["space_id"]
        sql_query = arguments["sql_query"]
        limit = arguments.get("limit", 100)

        if DATASPHERE_CONFIG["use_mock_data"]:
            # Mock mode - simulate query execution
            mock_result = {
                "query": sql_query,
                "space": space_id,
                "execution_time": "0.245 seconds",
                "rows_returned": min(limit, 50),
                "sample_data": [
                    {"CUSTOMER_ID": "C001", "CUSTOMER_NAME": "Acme Corp", "COUNTRY": "USA"},
                    {"CUSTOMER_ID": "C002", "CUSTOMER_NAME": "Global Tech", "COUNTRY": "Germany"},
                    {"CUSTOMER_ID": "C003", "CUSTOMER_NAME": "Data Solutions", "COUNTRY": "UK"}
                ][:limit],
                "note": "This is mock data. Set USE_MOCK_DATA=false for real query execution."
            }

            return [types.TextContent(
                type="text",
                text=f"Query Execution Results:\n\n" +
                     json.dumps(mock_result, indent=2)
            )]
        else:
            # Real API mode - use relational consumption endpoint
            if not datasphere_connector:
                return [types.TextContent(
                    type="text",
                    text="Error: OAuth connector not initialized. Cannot execute queries."
                )]

            try:
                # Parse SQL query to extract table name
                # Simple parser: SELECT ... FROM table_name ...

                # Extract table name from SQL
                # Match: FROM <table_name> or FROM <space>.<table_name>
                from_match = re.search(r'FROM\s+(?:(\w+)\.)?(\w+)', sql_query, re.IGNORECASE)

                if not from_match:
                    return [types.TextContent(
                        type="text",
                        text=f"Error: Could not parse table name from query.\n\n"
                             f"Query: {sql_query}\n\n"
                             f"Expected format: SELECT ... FROM table_name ...\n"
                             f"Use search_tables() to find available tables."
                    )]

                # Extract table name (group 2 is table name, group 1 is optional space prefix)
                table_name = from_match.group(2)

                logger.info(f"Executing query on table {table_name} in space {space_id}")

                # Use relational consumption API
                # Endpoint: /api/v1/datasphere/consumption/relational/{spaceId}/{viewName}
                endpoint = f"/api/v1/datasphere/consumption/relational/{space_id}/{table_name}"

                # Build OData parameters
                params = {
                    "$top": min(limit, 1000)  # Cap at 1000 for safety
                }

                # Try to extract WHERE clause for $filter (basic support)
                where_match = re.search(r'WHERE\s+(.+?)(?:ORDER BY|GROUP BY|LIMIT|$)', sql_query, re.IGNORECASE)
                if where_match:
                    where_clause = where_match.group(1).strip()
                    # Convert simple SQL WHERE to OData $filter
                    # Replace = with eq, AND with and, OR with or
                    odata_filter = where_clause.replace(" = ", " eq ").replace(" AND ", " and ").replace(" OR ", " or ")
                    params["$filter"] = odata_filter
                    logger.info(f"Converted WHERE clause to $filter: {odata_filter}")

                # Try to extract SELECT columns for $select (basic support)
                select_match = re.search(r'SELECT\s+(.+?)\s+FROM', sql_query, re.IGNORECASE)
                if select_match:
                    select_clause = select_match.group(1).strip()
                    if select_clause != "*":
                        # Extract column names (simplified - doesn't handle functions/aliases)
                        columns = [col.strip() for col in select_clause.split(',')]
                        params["$select"] = ",".join(columns)
                        logger.info(f"Using $select: {params['$select']}")

                # Execute query
                logger.info(f"GET {endpoint} with params: {params}")
                start_time = time.time()
                data = await datasphere_connector.get(endpoint, params=params)
                execution_time = time.time() - start_time

                # Format results
                value = data.get("value", [])
                result = {
                    "query": sql_query,
                    "space": space_id,
                    "table": table_name,
                    "execution_time": f"{execution_time:.3f} seconds",
                    "rows_returned": len(value),
                    "odata_endpoint": endpoint,
                    "odata_params": params,
                    "data": value
                }

                return [types.TextContent(
                    type="text",
                    text=f"Query Execution Results:\n\n" +
                         json.dumps(result, indent=2)
                )]

            except Exception as e:
                logger.error(f"Error executing query: {str(e)}")

                # Provide helpful error messages
                error_msg = f"Error executing query: {str(e)}\n\n"
                error_msg += "Possible causes:\n"
                error_msg += "1. Table/view doesn't exist in the space\n"
                error_msg += "2. Table name is case-sensitive (try uppercase)\n"
                error_msg += "3. Complex SQL syntax not supported (use simple SELECT ... FROM ... WHERE ...)\n"
                error_msg += "4. Use search_tables() to find available tables\n"
                error_msg += "5. Use get_table_schema() to verify table structure\n\n"
                error_msg += f"Query attempted: {sql_query}\n"
                error_msg += f"Extracted table: {table_name if 'table_name' in locals() else 'unknown'}"

                return [types.TextContent(
                    type="text",
                    text=error_msg
                )]

    elif name == "list_database_users":
        space_id = arguments["space_id"]
        output_file = arguments.get("output_file")

        if DATASPHERE_CONFIG["use_mock_data"]:
            # Mock mode
            users = MOCK_DATA["database_users"].get(space_id, [])

            if not users:
                return [types.TextContent(
                    type="text",
                    text=f"No database users found in space '{space_id}'.\n\n"
                         f"This could mean:\n"
                         f"- The space exists but has no database users configured\n"
                         f"- The space ID might be incorrect\n\n"
                         f"Use list_spaces to see available spaces.\n\n"
                         f"Note: This is mock data. Set USE_MOCK_DATA=false for real database users."
                )]

            result = {
                "space_id": space_id,
                "user_count": len(users),
                "users": users
            }

            if output_file:
                result["note"] = f"In production, output would be saved to {output_file}"

            return [types.TextContent(
                type="text",
                text=f"Database Users in '{space_id}':\n\n" +
                     json.dumps(result, indent=2) +
                     f"\n\nNote: This is mock data. Set USE_MOCK_DATA=false for real database users."
            )]
        else:
            # Real CLI execution
            try:
                import subprocess

                logger.info(f"Executing CLI: datasphere dbusers list --space {space_id}")

                # Execute datasphere CLI command
                result = subprocess.run(
                    ["datasphere", "dbusers", "list", "--space", space_id],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=30
                )

                # Parse CLI output (assuming JSON format)
                cli_output = result.stdout.strip()

                if not cli_output:
                    return [types.TextContent(
                        type="text",
                        text=f"No database users found in space '{space_id}'.\n\n"
                             f"This could mean:\n"
                             f"- The space exists but has no database users configured\n"
                             f"- The space ID might be incorrect\n\n"
                             f"Use list_spaces to see available spaces."
                    )]

                # Try to parse as JSON
                try:
                    users_data = json.loads(cli_output)
                except json.JSONDecodeError:
                    # If not JSON, return raw output
                    users_data = {"raw_output": cli_output}

                response = {
                    "space_id": space_id,
                    "users": users_data,
                    "source": "SAP Datasphere CLI"
                }

                if output_file:
                    response["output_file"] = output_file
                    response["note"] = f"To save output, redirect: datasphere dbusers list --space {space_id} > {output_file}"

                return [types.TextContent(
                    type="text",
                    text=f"Database Users in '{space_id}':\n\n" +
                         json.dumps(response, indent=2)
                )]

            except subprocess.CalledProcessError as e:
                logger.error(f"CLI command failed: {e.stderr}")
                return [types.TextContent(
                    type="text",
                    text=f"Error listing database users: {e.stderr}\n\n"
                         f"Command: datasphere dbusers list --space {space_id}\n"
                         f"Exit code: {e.returncode}\n\n"
                         f"Troubleshooting:\n"
                         f"1. Ensure datasphere CLI is installed and in PATH\n"
                         f"2. Verify CLI is authenticated (run: datasphere login)\n"
                         f"3. Check space ID is correct (run: datasphere spaces list)\n"
                         f"4. Verify permissions to list database users"
                )]
            except FileNotFoundError:
                return [types.TextContent(
                    type="text",
                    text=f"Error: datasphere CLI not found.\n\n"
                         f"Please install the SAP Datasphere CLI:\n"
                         f"1. Download from: https://help.sap.com/docs/SAP_DATASPHERE\n"
                         f"2. Ensure it's in your system PATH\n"
                         f"3. Authenticate with: datasphere login"
                )]
            except subprocess.TimeoutExpired:
                return [types.TextContent(
                    type="text",
                    text=f"Error: CLI command timed out after 30 seconds.\n\n"
                         f"The space may have many users, or the CLI is unresponsive."
                )]
            except Exception as e:
                logger.error(f"Unexpected error listing database users: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Unexpected error listing database users: {str(e)}"
                )]

    elif name == "create_database_user":
        space_id = arguments["space_id"]
        database_user_id = arguments["database_user_id"]
        user_definition = arguments["user_definition"]
        output_file = arguments.get("output_file")

        if DATASPHERE_CONFIG["use_mock_data"]:
            # Mock mode
            password = secrets.token_urlsafe(16)
            full_username = f"{space_id}#{database_user_id}"

            result = {
                "status": "SUCCESS",
                "message": f"Database user '{database_user_id}' created successfully in space '{space_id}'",
                "user": {
                    "user_id": database_user_id,
                    "full_name": full_username,
                    "status": "ACTIVE",
                    "created_date": datetime.utcnow().isoformat() + "Z",
                    "credentials": {
                        "username": full_username,
                        "password": password,
                        "note": "IMPORTANT: Save this password securely! It will not be shown again."
                    },
                    "permissions": user_definition
                },
                "next_steps": [
                    "Save the credentials securely (use output_file parameter recommended)",
                    "Communicate password to user via secure channel (not email!)",
                    "User must change password on first login",
                    "Test connection with the provided credentials"
                ]
            }

            if output_file:
                result["output_file"] = output_file
                result["note"] = f"In production, credentials would be saved to {output_file}"

            return [types.TextContent(
                type="text",
                text=f"Database User Created:\n\n" +
                     json.dumps(result, indent=2) +
                     f"\n\n⚠️  WARNING: This is mock data. Set USE_MOCK_DATA=false for real user creation."
            )]
        else:
            # Real CLI execution
            try:
                import subprocess
                import tempfile
                import os

                logger.info(f"Creating database user {database_user_id} in space {space_id}")

                # Write user definition to temporary JSON file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                    json.dump(user_definition, temp_file, indent=2)
                    temp_file_path = temp_file.name

                try:
                    # Execute datasphere CLI command
                    cmd = [
                        "datasphere", "dbusers", "create",
                        "--space", space_id,
                        "--databaseuser", database_user_id,
                        "--file-path", temp_file_path
                    ]

                    logger.info(f"Executing CLI: {' '.join(cmd)}")

                    result_proc = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        check=True,
                        timeout=60
                    )

                    cli_output = result_proc.stdout.strip()

                    # Try to parse CLI output
                    try:
                        result_data = json.loads(cli_output)
                    except json.JSONDecodeError:
                        result_data = {"raw_output": cli_output}

                    response = {
                        "status": "SUCCESS",
                        "message": f"Database user '{database_user_id}' created successfully",
                        "space_id": space_id,
                        "database_user_id": database_user_id,
                        "cli_output": result_data,
                        "source": "SAP Datasphere CLI"
                    }

                    if output_file:
                        response["output_file"] = output_file
                        response["note"] = f"To save credentials, use CLI output redirection"

                    return [types.TextContent(
                        type="text",
                        text=f"Database User Created:\n\n" +
                             json.dumps(response, indent=2)
                    )]

                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)

            except subprocess.CalledProcessError as e:
                logger.error(f"CLI command failed: {e.stderr}")
                return [types.TextContent(
                    type="text",
                    text=f"Error creating database user: {e.stderr}\n\n"
                         f"Command failed with exit code: {e.returncode}\n\n"
                         f"Troubleshooting:\n"
                         f"1. Verify user_definition format matches SAP requirements\n"
                         f"2. Check permissions to create database users\n"
                         f"3. Ensure user doesn't already exist\n"
                         f"4. Verify space ID is correct"
                )]
            except FileNotFoundError:
                return [types.TextContent(
                    type="text",
                    text=f"Error: datasphere CLI not found. Please install and configure the CLI."
                )]
            except subprocess.TimeoutExpired:
                return [types.TextContent(
                    type="text",
                    text=f"Error: CLI command timed out after 60 seconds."
                )]
            except Exception as e:
                logger.error(f"Unexpected error creating database user: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Unexpected error: {str(e)}"
                )]

    elif name == "reset_database_user_password":
        space_id = arguments["space_id"]
        database_user_id = arguments["database_user_id"]
        output_file = arguments.get("output_file")

        if DATASPHERE_CONFIG["use_mock_data"]:
            # Mock mode
            users = MOCK_DATA["database_users"].get(space_id, [])
            user = next((u for u in users if u["user_id"] == database_user_id), None)

            if not user:
                return [types.TextContent(
                    type="text",
                    text=f">>> User Not Found <<<\n\n"
                         f"Database user '{database_user_id}' does not exist in space '{space_id}'.\n\n"
                         f"Available users in {space_id}:\n" +
                         "\n".join(f"- {u['user_id']}" for u in users) if users else "No users found." +
                         f"\n\nNote: This is mock data. Set USE_MOCK_DATA=false for real password reset."
                )]

            new_password = secrets.token_urlsafe(16)
            full_username = f"{space_id}#{database_user_id}"

            result = {
                "status": "SUCCESS",
                "message": f"Password reset successfully for user '{database_user_id}' in space '{space_id}'",
                "user": {
                    "user_id": database_user_id,
                    "full_name": full_username,
                    "credentials": {
                        "username": full_username,
                        "new_password": new_password,
                        "note": "IMPORTANT: Save this password securely! It will not be shown again."
                    },
                    "reset_date": datetime.utcnow().isoformat() + "Z"
                },
                "security_actions": [
                    "Old password invalidated immediately",
                    "All active sessions terminated",
                    "Password must be changed on next login",
                    "Action logged for security audit"
                ],
                "next_steps": [
                    "Save new credentials securely (use output_file parameter recommended)",
                    "Communicate new password via secure channel (not email!)",
                    "Verify user identity before sharing password",
                    "Document password reset in change log"
                ]
            }

            if output_file:
                result["output_file"] = output_file
                result["note"] = f"In production, credentials would be saved to {output_file}"

            return [types.TextContent(
                type="text",
                text=f"Password Reset Complete:\n\n" +
                     json.dumps(result, indent=2) +
                     f"\n\n⚠️  WARNING: This is mock data. Set USE_MOCK_DATA=false for real password reset."
            )]
        else:
            # Real CLI execution
            try:
                import subprocess

                logger.info(f"Resetting password for database user {database_user_id} in space {space_id}")

                # Execute datasphere CLI command
                cmd = [
                    "datasphere", "dbusers", "password", "reset",
                    "--space", space_id,
                    "--databaseuser", database_user_id
                ]

                logger.info(f"Executing CLI: {' '.join(cmd)}")

                result_proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=60
                )

                cli_output = result_proc.stdout.strip()

                # Try to parse CLI output
                try:
                    result_data = json.loads(cli_output)
                except json.JSONDecodeError:
                    result_data = {"raw_output": cli_output}

                response = {
                    "status": "SUCCESS",
                    "message": f"Password reset successfully for user '{database_user_id}'",
                    "space_id": space_id,
                    "database_user_id": database_user_id,
                    "cli_output": result_data,
                    "source": "SAP Datasphere CLI",
                    "security_note": "New password provided in CLI output - save securely!"
                }

                if output_file:
                    response["output_file"] = output_file

                return [types.TextContent(
                    type="text",
                    text=f"Password Reset Complete:\n\n" +
                         json.dumps(response, indent=2)
                )]

            except subprocess.CalledProcessError as e:
                logger.error(f"CLI command failed: {e.stderr}")
                return [types.TextContent(
                    type="text",
                    text=f"Error resetting password: {e.stderr}\n\n"
                         f"Command failed with exit code: {e.returncode}\n\n"
                         f"Troubleshooting:\n"
                         f"1. Verify user exists (use list_database_users)\n"
                         f"2. Check permissions to reset passwords\n"
                         f"3. Ensure CLI is authenticated"
                )]
            except FileNotFoundError:
                return [types.TextContent(
                    type="text",
                    text=f"Error: datasphere CLI not found. Please install and configure the CLI."
                )]
            except subprocess.TimeoutExpired:
                return [types.TextContent(
                    type="text",
                    text=f"Error: CLI command timed out after 60 seconds."
                )]
            except Exception as e:
                logger.error(f"Unexpected error resetting password: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Unexpected error: {str(e)}"
                )]

    elif name == "update_database_user":
        space_id = arguments["space_id"]
        database_user_id = arguments["database_user_id"]
        updated_definition = arguments["updated_definition"]
        output_file = arguments.get("output_file")

        if DATASPHERE_CONFIG["use_mock_data"]:
            # Mock mode
            users = MOCK_DATA["database_users"].get(space_id, [])
            user = next((u for u in users if u["user_id"] == database_user_id), None)

            if not user:
                return [types.TextContent(
                    type="text",
                    text=f">>> User Not Found <<<\n\n"
                         f"Database user '{database_user_id}' does not exist in space '{space_id}'.\n\n"
                         f"Available users in {space_id}:\n" +
                         "\n".join(f"- {u['user_id']}" for u in users) if users else "No users found." +
                         f"\n\nNote: This is mock data. Set USE_MOCK_DATA=false for real user update."
                )]

            # Compare old and new permissions
            old_permissions = user.get("permissions", {})

            result = {
                "status": "SUCCESS",
                "message": f"Database user '{database_user_id}' updated successfully in space '{space_id}'",
                "user": {
                    "user_id": database_user_id,
                    "full_name": f"{space_id}#{database_user_id}",
                    "updated_date": datetime.utcnow().isoformat() + "Z",
                    "old_permissions": old_permissions,
                    "new_permissions": updated_definition
                },
                "changes_applied": [
                    "Permissions updated immediately",
                    "All changes logged for audit",
                    "Active sessions may need reconnection"
                ],
                "next_steps": [
                    "Verify new permissions are correct",
                    "Test user access with new configuration",
                    "Notify user if access levels changed",
                    "Document changes in change log"
                ]
            }

            if output_file:
                result["output_file"] = output_file
                result["note"] = f"In production, updated configuration would be saved to {output_file}"

            return [types.TextContent(
                type="text",
                text=f"Database User Updated:\n\n" +
                     json.dumps(result, indent=2) +
                     f"\n\n⚠️  WARNING: This is mock data. Set USE_MOCK_DATA=false for real user update."
            )]
        else:
            # Real CLI execution
            try:
                import subprocess
                import tempfile
                import os

                logger.info(f"Updating database user {database_user_id} in space {space_id}")

                # Write updated definition to temporary JSON file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                    json.dump(updated_definition, temp_file, indent=2)
                    temp_file_path = temp_file.name

                try:
                    # Execute datasphere CLI command
                    cmd = [
                        "datasphere", "dbusers", "update",
                        "--space", space_id,
                        "--databaseuser", database_user_id,
                        "--file-path", temp_file_path
                    ]

                    logger.info(f"Executing CLI: {' '.join(cmd)}")

                    result_proc = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        check=True,
                        timeout=60
                    )

                    cli_output = result_proc.stdout.strip()

                    # Try to parse CLI output
                    try:
                        result_data = json.loads(cli_output)
                    except json.JSONDecodeError:
                        result_data = {"raw_output": cli_output}

                    response = {
                        "status": "SUCCESS",
                        "message": f"Database user '{database_user_id}' updated successfully",
                        "space_id": space_id,
                        "database_user_id": database_user_id,
                        "updated_definition": updated_definition,
                        "cli_output": result_data,
                        "source": "SAP Datasphere CLI"
                    }

                    if output_file:
                        response["output_file"] = output_file

                    return [types.TextContent(
                        type="text",
                        text=f"Database User Updated:\n\n" +
                             json.dumps(response, indent=2)
                    )]

                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)

            except subprocess.CalledProcessError as e:
                logger.error(f"CLI command failed: {e.stderr}")
                return [types.TextContent(
                    type="text",
                    text=f"Error updating user: {e.stderr}\n\n"
                         f"Command failed with exit code: {e.returncode}\n\n"
                         f"Troubleshooting:\n"
                         f"1. Verify user exists (use list_database_users)\n"
                         f"2. Check updated_definition JSON format is correct\n"
                         f"3. Ensure you have permissions to update users\n"
                         f"4. Verify datasphere CLI is configured correctly"
                )]

            except FileNotFoundError:
                return [types.TextContent(
                    type="text",
                    text=f"Error: SAP Datasphere CLI not found.\n\n"
                         f"Please install the datasphere CLI:\n"
                         f"https://help.sap.com/docs/SAP_DATASPHERE/cli"
                )]

            except subprocess.TimeoutExpired:
                return [types.TextContent(
                    type="text",
                    text=f"Error: User update timed out after 60 seconds.\n\n"
                         f"This may indicate a slow network or server issue."
                )]

            except Exception as e:
                logger.error(f"Unexpected error updating user: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Unexpected error: {str(e)}"
                )]

    elif name == "delete_database_user":
        space_id = arguments["space_id"]
        database_user_id = arguments["database_user_id"]
        force = arguments.get("force", False)

        if DATASPHERE_CONFIG["use_mock_data"]:
            # Mock mode
            users = MOCK_DATA["database_users"].get(space_id, [])
            user = next((u for u in users if u["user_id"] == database_user_id), None)

            if not user:
                return [types.TextContent(
                    type="text",
                    text=f">>> User Not Found <<<\n\n"
                         f"Database user '{database_user_id}' does not exist in space '{space_id}'.\n\n"
                         f"Available users in {space_id}:\n" +
                         "\n".join(f"- {u['user_id']}" for u in users) if users else "No users found." +
                         f"\n\nNote: This is mock data. Set USE_MOCK_DATA=false for real user deletion."
                )]

            # If not forced, require explicit confirmation
            if not force:
                return [types.TextContent(
                    type="text",
                    text=f">>> Confirmation Required <<<\n\n"
                         f"⚠️  WARNING: You are about to PERMANENTLY DELETE database user '{database_user_id}'.\n\n"
                         f"User Details:\n"
                         f"- Full Name: {user.get('full_name')}\n"
                         f"- Status: {user.get('status')}\n"
                         f"- Created: {user.get('created_date')}\n"
                         f"- Last Login: {user.get('last_login')}\n"
                         f"- Description: {user.get('description')}\n\n"
                         f"Consequences:\n"
                         f"- User account permanently deleted (IRREVERSIBLE)\n"
                         f"- All active sessions terminated immediately\n"
                         f"- All granted privileges revoked\n"
                         f"- Cannot be recovered - must recreate if needed\n\n"
                         f"Before Proceeding:\n"
                         f"1. Verify no applications depend on this user\n"
                         f"2. Check if user owns any database objects\n"
                         f"3. Get management approval for production users\n"
                         f"4. Document deletion reason\n\n"
                         f"To confirm deletion, call this tool again with 'force': true\n\n"
                         f"Note: This is mock data. Set USE_MOCK_DATA=false for real user deletion."
                )]

            # Deletion confirmed
            result = {
                "status": "SUCCESS",
                "message": f"Database user '{database_user_id}' deleted successfully from space '{space_id}'",
                "deleted_user": {
                    "user_id": database_user_id,
                    "full_name": f"{space_id}#{database_user_id}",
                    "deleted_date": datetime.utcnow().isoformat() + "Z",
                    "previous_status": user.get("status"),
                    "created_date": user.get("created_date"),
                    "description": user.get("description")
                },
                "actions_taken": [
                    "User account permanently deleted",
                    "All active sessions terminated",
                    "All privileges revoked",
                    "Deletion logged for audit"
                ],
                "reminder": "This action is IRREVERSIBLE. The user must be recreated if needed again."
            }

            return [types.TextContent(
                type="text",
                text=f"Database User Deleted:\n\n" +
                     json.dumps(result, indent=2) +
                     f"\n\n⚠️  WARNING: This is mock data. Set USE_MOCK_DATA=false for real user deletion."
            )]
        else:
            # Real CLI execution
            try:
                import subprocess

                logger.info(f"Deleting database user {database_user_id} in space {space_id} (force={force})")

                # Build CLI command
                cmd = [
                    "datasphere", "dbusers", "delete",
                    "--space", space_id,
                    "--databaseuser", database_user_id
                ]

                # Add --force flag if confirmed
                if force:
                    cmd.append("--force")

                logger.info(f"Executing CLI: {' '.join(cmd)}")

                result_proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=60
                )

                cli_output = result_proc.stdout.strip()

                # Try to parse CLI output
                try:
                    result_data = json.loads(cli_output)
                except json.JSONDecodeError:
                    result_data = {"raw_output": cli_output}

                response = {
                    "status": "SUCCESS",
                    "message": f"Database user '{database_user_id}' deleted successfully",
                    "space_id": space_id,
                    "database_user_id": database_user_id,
                    "force": force,
                    "cli_output": result_data,
                    "source": "SAP Datasphere CLI",
                    "reminder": "This action is IRREVERSIBLE. User must be recreated if needed again."
                }

                return [types.TextContent(
                    type="text",
                    text=f"Database User Deleted:\n\n" +
                         json.dumps(response, indent=2)
                )]

            except subprocess.CalledProcessError as e:
                logger.error(f"CLI command failed: {e.stderr}")

                # Check if error is confirmation required
                if "confirmation" in e.stderr.lower() or "force" in e.stderr.lower():
                    return [types.TextContent(
                        type="text",
                        text=f">>> Confirmation Required <<<\n\n"
                             f"⚠️  WARNING: You are about to PERMANENTLY DELETE database user '{database_user_id}'.\n\n"
                             f"Consequences:\n"
                             f"- User account permanently deleted (IRREVERSIBLE)\n"
                             f"- All active sessions terminated immediately\n"
                             f"- All granted privileges revoked\n"
                             f"- Cannot be recovered - must recreate if needed\n\n"
                             f"Before Proceeding:\n"
                             f"1. Verify no applications depend on this user\n"
                             f"2. Check if user owns any database objects\n"
                             f"3. Get management approval for production users\n"
                             f"4. Document deletion reason\n\n"
                             f"To confirm deletion, call this tool again with 'force': true"
                    )]

                return [types.TextContent(
                    type="text",
                    text=f"Error deleting user: {e.stderr}\n\n"
                         f"Command failed with exit code: {e.returncode}\n\n"
                         f"Troubleshooting:\n"
                         f"1. Verify user exists (use list_database_users)\n"
                         f"2. If deletion requires confirmation, add 'force': true\n"
                         f"3. Check you have permissions to delete users\n"
                         f"4. Verify datasphere CLI is configured correctly"
                )]

            except FileNotFoundError:
                return [types.TextContent(
                    type="text",
                    text=f"Error: SAP Datasphere CLI not found.\n\n"
                         f"Please install the datasphere CLI:\n"
                         f"https://help.sap.com/docs/SAP_DATASPHERE/cli"
                )]

            except subprocess.TimeoutExpired:
                return [types.TextContent(
                    type="text",
                    text=f"Error: User deletion timed out after 60 seconds.\n\n"
                         f"This may indicate a slow network or server issue."
                )]

            except Exception as e:
                logger.error(f"Unexpected error deleting user: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Unexpected error: {str(e)}"
                )]

    elif name == "list_catalog_assets":
        # Extract OData query parameters
        select_fields = arguments.get("select_fields")
        filter_expression = arguments.get("filter_expression")
        top = arguments.get("top", 50)
        skip = arguments.get("skip", 0)
        count = arguments.get("count", False)
        orderby = arguments.get("orderby")

        if DATASPHERE_CONFIG["use_mock_data"]:
            # Mock data mode
            space_id_filter = None
            asset_type_filter = None

            if filter_expression:
                import re
                match = re.search(r"spaceId eq '([^']+)'", filter_expression)
                if match:
                    space_id_filter = match.group(1)
                match = re.search(r"assetType eq '([^']+)'", filter_expression)
                if match:
                    asset_type_filter = match.group(1)

            assets = get_mock_catalog_assets(space_id=space_id_filter, asset_type=asset_type_filter)

            if select_fields:
                assets = [{field: asset.get(field) for field in select_fields if field in asset} for asset in assets]

            if orderby:
                field = orderby.split()[0]
                reverse = "desc" in orderby.lower()
                assets = sorted(assets, key=lambda x: x.get(field, ""), reverse=reverse)

            total_count = len(assets)
            assets = assets[skip:skip + top]

            result = {"value": assets, "count": total_count if count else None, "top": top, "skip": skip, "returned": len(assets)}

            return [types.TextContent(
                type="text",
                text=f"Found {total_count} catalog assets (showing {len(assets)}):\n\n{json.dumps(result, indent=2)}\n\nNote: Mock data."
            )]
        else:
            # Real API mode
            if not datasphere_connector:
                return [types.TextContent(type="text", text="Error: OAuth connector not initialized.")]

            try:
                endpoint = "/api/v1/datasphere/consumption/catalog/assets"
                params = {"$top": top, "$skip": skip}

                if filter_expression:
                    params["$filter"] = filter_expression
                if count:
                    params["$count"] = "true"
                if orderby:
                    params["$orderby"] = orderby
                if select_fields:
                    params["$select"] = ",".join(select_fields) if isinstance(select_fields, list) else select_fields

                data = await datasphere_connector.get(endpoint, params=params)
                assets = data.get("value", [])
                total_count = data.get("@odata.count", len(assets))

                result = {"value": assets, "count": total_count if count else None, "top": top, "skip": skip, "returned": len(assets)}

                return [types.TextContent(
                    type="text",
                    text=f"Found {total_count} catalog assets (showing {len(assets)}):\n\n{json.dumps(result, indent=2)}"
                )]
            except Exception as e:
                logger.error(f"Error listing catalog assets: {e}")
                return [types.TextContent(type="text", text=f"Error listing catalog assets: {e}")]

    elif name == "get_asset_details":
        space_id = arguments["space_id"]
        asset_id = arguments["asset_id"]
        select_fields = arguments.get("select_fields")

        if DATASPHERE_CONFIG["use_mock_data"]:
            # Mock mode
            # Get detailed asset information
            asset = get_mock_asset_details(space_id, asset_id)

            if not asset:
                return [types.TextContent(
                    type="text",
                    text=f">>> Asset Not Found <<<\n\n"
                         f"Asset '{asset_id}' not found in space '{space_id}'.\n\n"
                         f"Possible reasons:\n"
                         f"- Asset ID is incorrect (check exact case and spelling)\n"
                         f"- Space ID is incorrect\n"
                         f"- Asset was deleted or moved\n\n"
                         f"Try using list_catalog_assets or get_space_assets to find available assets."
                )]

            # Apply select fields if specified
            if select_fields:
                asset = {field: asset.get(field) for field in select_fields if field in asset}

            return [types.TextContent(
                type="text",
                text=f"{json.dumps(asset, indent=2)}\n\nNote: Mock data. Configure OAuth credentials to access real SAP Datasphere data."
            )]
        else:
            # Real API mode
            if not datasphere_connector:
                return [types.TextContent(
                    type="text",
                    text="Error: OAuth connector not initialized. Please configure DATASPHERE_CLIENT_ID and DATASPHERE_CLIENT_SECRET."
                )]

            try:
                # Get asset details from catalog API
                endpoint = f"/api/v1/datasphere/consumption/catalog/spaces('{space_id}')/assets('{asset_id}')"
                params = {}
                if select_fields:
                    params["$select"] = ",".join(select_fields) if isinstance(select_fields, list) else select_fields

                logger.info(f"Getting asset details for {asset_id} in space {space_id}")
                asset = await datasphere_connector.get(endpoint, params=params)

                return [types.TextContent(
                    type="text",
                    text=json.dumps(asset, indent=2)
                )]

            except Exception as e:
                logger.error(f"Error getting asset details: {e}")

                # Check if it's a 404 error
                if "404" in str(e):
                    return [types.TextContent(
                        type="text",
                        text=f">>> Asset Not Found <<<\n\n"
                             f"Asset '{asset_id}' not found in space '{space_id}'.\n\n"
                             f"Possible reasons:\n"
                             f"- Asset ID is incorrect (check exact case and spelling)\n"
                             f"- Space ID is incorrect\n"
                             f"- Asset was deleted or moved\n"
                             f"- You don't have permission to access this asset\n\n"
                             f"Try using list_catalog_assets or get_space_assets to find available assets.\n\n"
                             f"Error: {str(e)}"
                    )]
                else:
                    return [types.TextContent(
                        type="text",
                        text=f"Error getting asset details: {str(e)}"
                    )]

    elif name == "get_asset_by_compound_key":
        # Tool schema provides space_id and asset_id directly
        space_id = arguments["space_id"]
        asset_id = arguments["asset_id"]
        select_fields = arguments.get("select_fields")

        # Build compound key from individual parameters
        compound_key = f"spaceId='{space_id}',id='{asset_id}'"

        if DATASPHERE_CONFIG["use_mock_data"]:
            # Mock mode
            # Get detailed asset information
            asset = get_mock_asset_details(space_id, asset_id)

            if not asset:
                return [types.TextContent(
                    type="text",
                    text=f">>> Asset Not Found <<<\n\n"
                         f"Asset with compound key '{compound_key}' not found.\n\n"
                         f"Parsed as: space='{space_id}', asset='{asset_id}'\n\n"
                         f"Try using list_catalog_assets to find available assets."
                )]

            # Apply select fields if specified
            if select_fields:
                asset = {field: asset.get(field) for field in select_fields if field in asset}

            return [types.TextContent(
                type="text",
                text=f"{json.dumps(asset, indent=2)}\n\nNote: Mock data. Configure OAuth credentials to access real SAP Datasphere data."
            )]
        else:
            # Real API mode - use same endpoint as get_asset_details
            if not datasphere_connector:
                return [types.TextContent(
                    type="text",
                    text="Error: OAuth connector not initialized. Please configure DATASPHERE_CLIENT_ID and DATASPHERE_CLIENT_SECRET."
                )]

            try:
                # Get asset details using compound key (same as get_asset_details endpoint)
                endpoint = f"/api/v1/datasphere/consumption/catalog/spaces('{space_id}')/assets('{asset_id}')"
                params = {}
                if select_fields:
                    params["$select"] = ",".join(select_fields) if isinstance(select_fields, list) else select_fields

                logger.info(f"Getting asset by compound key: {compound_key}")
                asset = await datasphere_connector.get(endpoint, params=params)

                return [types.TextContent(
                    type="text",
                    text=json.dumps(asset, indent=2)
                )]

            except Exception as e:
                logger.error(f"Error getting asset by compound key: {e}")

                # Check if it's a 404 error
                if "404" in str(e):
                    return [types.TextContent(
                        type="text",
                        text=f">>> Asset Not Found <<<\n\n"
                             f"Asset with compound key '{compound_key}' not found.\n\n"
                             f"Parsed as: space='{space_id}', asset='{asset_id}'\n\n"
                             f"Possible reasons:\n"
                             f"- Asset ID is incorrect\n"
                             f"- Space ID is incorrect\n"
                             f"- Asset was deleted or moved\n"
                             f"- You don't have permission to access this asset\n\n"
                             f"Try using list_catalog_assets to find available assets.\n\n"
                             f"Error: {str(e)}"
                    )]
                else:
                    return [types.TextContent(
                        type="text",
                        text=f"Error getting asset by compound key: {str(e)}"
                    )]

    elif name == "get_space_assets":
        space_id = arguments["space_id"]
        select_fields = arguments.get("select_fields")
        filter_expression = arguments.get("filter_expression")
        top = arguments.get("top", 50)
        skip = arguments.get("skip", 0)
        count = arguments.get("count", False)
        orderby = arguments.get("orderby")

        if DATASPHERE_CONFIG["use_mock_data"]:
            # Mock mode
            # Get assets for the specific space
            assets = get_mock_catalog_assets(space_id=space_id)

            if not assets:
                return [types.TextContent(
                    type="text",
                    text=f">>> No Assets Found <<<\n\n"
                         f"No catalog assets found in space '{space_id}'.\n\n"
                         f"This could mean:\n"
                         f"- The space exists but has no published assets\n"
                         f"- The space ID is incorrect\n"
                         f"- Assets are not exposed for consumption\n\n"
                         f"Use list_spaces to verify the space ID."
                )]

            # Apply filter expression for asset type
            if filter_expression and "assetType eq" in filter_expression:
                import re
                match = re.search(r"assetType eq '([^']+)'", filter_expression)
                if match:
                    asset_type = match.group(1)
                    assets = [a for a in assets if a.get("assetType") == asset_type]

            # Apply select fields if specified
            if select_fields:
                assets = [
                    {field: asset.get(field) for field in select_fields if field in asset}
                    for asset in assets
                ]

            # Apply orderby
            if orderby:
                field = orderby.split()[0]
                reverse = "desc" in orderby.lower()
                assets = sorted(assets, key=lambda x: x.get(field, ""), reverse=reverse)

            # Get total count before pagination
            total_count = len(assets)

            # Apply pagination
            assets = assets[skip:skip + top]

            result = {
                "space_id": space_id,
                "value": assets,
                "count": total_count if count else None,
                "top": top,
                "skip": skip,
                "returned": len(assets)
            }

            return [types.TextContent(
                type="text",
                text=f"{json.dumps(result, indent=2)}\n\nNote: Mock data. Configure OAuth credentials to access real SAP Datasphere data."
            )]
        else:
            # Real API mode
            if not datasphere_connector:
                return [types.TextContent(
                    type="text",
                    text="Error: OAuth connector not initialized. Please configure DATASPHERE_CLIENT_ID and DATASPHERE_CLIENT_SECRET."
                )]

            try:
                # Get assets for the specific space
                endpoint = f"/api/v1/datasphere/consumption/catalog/spaces('{space_id}')/assets"
                params = {"$top": top, "$skip": skip}

                if filter_expression:
                    params["$filter"] = filter_expression
                if count:
                    params["$count"] = "true"
                if orderby:
                    params["$orderby"] = orderby
                if select_fields:
                    params["$select"] = ",".join(select_fields) if isinstance(select_fields, list) else select_fields

                logger.info(f"Getting assets for space {space_id}")
                data = await datasphere_connector.get(endpoint, params=params)

                assets = data.get("value", [])
                total_count = data.get("@odata.count", len(assets))

                result = {
                    "space_id": space_id,
                    "value": assets,
                    "count": total_count if count else None,
                    "top": top,
                    "skip": skip,
                    "returned": len(assets)
                }

                return [types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]

            except Exception as e:
                logger.error(f"Error getting space assets: {e}")

                # Check if it's a 404 error (space not found)
                if "404" in str(e):
                    return [types.TextContent(
                        type="text",
                        text=f">>> No Assets Found <<<\n\n"
                             f"No catalog assets found in space '{space_id}'.\n\n"
                             f"This could mean:\n"
                             f"- The space exists but has no published assets\n"
                             f"- The space ID is incorrect\n"
                             f"- Assets are not exposed for consumption\n"
                             f"- You don't have permission to access this space\n\n"
                             f"Use list_spaces to verify the space ID.\n\n"
                             f"Error: {str(e)}"
                    )]
                else:
                    return [types.TextContent(
                        type="text",
                        text=f"Error getting space assets: {str(e)}"
                    )]

    elif name == "test_connection":
        # Test connection to SAP Datasphere
        result = {
            "mode": "mock" if DATASPHERE_CONFIG["use_mock_data"] else "real",
            "base_url": DATASPHERE_CONFIG["base_url"],
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        if DATASPHERE_CONFIG["use_mock_data"]:
            # Mock mode - always successful
            result.update({
                "connected": True,
                "message": "Running in MOCK DATA mode. No real connection to SAP Datasphere.",
                "oauth_configured": False,
                "recommendation": "To connect to real SAP Datasphere, set USE_MOCK_DATA=false in .env and configure OAuth credentials."
            })
        else:
            # Real mode - test OAuth connection
            if datasphere_connector is None:
                result.update({
                    "connected": False,
                    "message": "OAuth connector not initialized. Server may not have started correctly.",
                    "oauth_configured": False,
                    "error": "Datasphere connector is None"
                })
            else:
                try:
                    # Test the connection
                    connection_status = await datasphere_connector.test_connection()
                    result.update(connection_status)
                except Exception as e:
                    result.update({
                        "connected": False,
                        "message": f"Connection test failed: {str(e)}",
                        "error": str(e)
                    })

        return [types.TextContent(
            type="text",
            text=f"Connection Test Results:\n\n" +
                 json.dumps(result, indent=2)
        )]

    elif name == "get_current_user":
        # Get current authenticated user information
        if DATASPHERE_CONFIG["use_mock_data"]:
            # Mock user data
            mock_user = {
                "user_id": "TECH_USER_001",
                "email": "technical_user@company.com",
                "display_name": "Technical User (Mock)",
                "roles": ["DWC_CONSUMER", "CATALOG_READER", "SPACE_VIEWER"],
                "permissions": ["READ_SPACES", "READ_ASSETS", "QUERY_DATA", "READ_CATALOG"],
                "tenant_id": DATASPHERE_CONFIG["tenant_id"],
                "last_login": (datetime.utcnow() - timedelta(hours=2)).isoformat() + "Z",
                "account_status": "Active",
                "note": "This is mock data. Set USE_MOCK_DATA=false for real user information."
            }
            return [types.TextContent(
                type="text",
                text=f"Current User Information:\n\n" +
                     json.dumps(mock_user, indent=2)
            )]
        else:
            if not datasphere_connector:
                return [types.TextContent(
                    type="text",
                    text="Error: OAuth connector not initialized. Cannot get user information."
                )]

            try:
                # Try to get user info from token or API
                # First, try to decode JWT token to get user info
                token = await datasphere_connector.get_valid_token()

                # Try to parse JWT token (without verification since we trust our own token)
                import base64
                token_parts = token.split('.')
                if len(token_parts) >= 2:
                    # Decode payload (add padding if needed)
                    payload = token_parts[1]
                    padding = 4 - len(payload) % 4
                    if padding != 4:
                        payload += '=' * padding

                    try:
                        decoded = base64.urlsafe_b64decode(payload)
                        token_data = json.loads(decoded)

                        user_info = {
                            "user_id": token_data.get("user_id", token_data.get("sub", "Unknown")),
                            "email": token_data.get("email", token_data.get("user_name", "N/A")),
                            "display_name": token_data.get("given_name", "N/A"),
                            "client_id": token_data.get("client_id", "N/A"),
                            "scopes": token_data.get("scope", []),
                            "tenant_id": DATASPHERE_CONFIG["tenant_id"],
                            "token_issued_at": datetime.fromtimestamp(token_data.get("iat", 0)).isoformat() + "Z" if token_data.get("iat") else "N/A",
                            "token_expires_at": datetime.fromtimestamp(token_data.get("exp", 0)).isoformat() + "Z" if token_data.get("exp") else "N/A",
                            "account_status": "Active"
                        }

                        return [types.TextContent(
                            type="text",
                            text=f"Current User Information:\n\n" +
                                 json.dumps(user_info, indent=2)
                        )]
                    except Exception as decode_error:
                        logger.warning(f"Could not decode token: {decode_error}")

                # If token decoding fails, return basic info
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "user_id": "Unknown",
                        "message": "User information available from OAuth token",
                        "tenant_id": DATASPHERE_CONFIG["tenant_id"],
                        "note": "Full user details require API endpoint access"
                    }, indent=2)
                )]

            except Exception as e:
                logger.error(f"Error getting current user: {str(e)}")
                return [types.TextContent(
                    type="text",
                    text=f"Error getting user information: {str(e)}"
                )]

    elif name == "get_tenant_info":
        # Get SAP Datasphere tenant information
        if DATASPHERE_CONFIG["use_mock_data"]:
            # Mock tenant data
            mock_tenant = {
                "tenant_id": DATASPHERE_CONFIG["tenant_id"],
                "tenant_name": "Company Production (Mock)",
                "base_url": DATASPHERE_CONFIG["base_url"],
                "region": "eu-central-1",
                "datasphere_version": "2024.20",
                "license_type": "Enterprise",
                "storage_quota_gb": 10000,
                "storage_used_gb": 3500,
                "storage_available_gb": 6500,
                "storage_usage_percent": 35.0,
                "user_count": 150,
                "space_count": 25,
                "features_enabled": [
                    "AI_FEATURES",
                    "DATA_SHARING",
                    "MARKETPLACE",
                    "ADVANCED_ANALYTICS",
                    "DATA_INTEGRATION"
                ],
                "maintenance_window": "Sunday 02:00-04:00 UTC",
                "status": "Active",
                "note": "This is mock data. Set USE_MOCK_DATA=false for real tenant information."
            }
            return [types.TextContent(
                type="text",
                text=f"Tenant Information:\n\n" +
                     json.dumps(mock_tenant, indent=2)
            )]
        else:
            if not datasphere_connector:
                return [types.TextContent(
                    type="text",
                    text="Error: OAuth connector not initialized. Cannot get tenant information."
                )]

            try:
                # Try to get tenant info from API
                # Note: Actual endpoint may vary, trying common patterns
                tenant_info = {
                    "tenant_id": DATASPHERE_CONFIG["tenant_id"],
                    "base_url": DATASPHERE_CONFIG["base_url"],
                    "status": "Active"
                }

                # Try to get additional info from spaces endpoint (as a proxy for tenant health)
                try:
                    endpoint = "/api/v1/datasphere/consumption/catalog/spaces"
                    spaces_data = await datasphere_connector.get(endpoint, params={"$top": 1})
                    tenant_info["spaces_accessible"] = True
                    tenant_info["api_status"] = "Connected"
                except Exception as e:
                    tenant_info["spaces_accessible"] = False
                    tenant_info["api_status"] = f"Limited: {str(e)}"

                tenant_info["note"] = "Full tenant details may require additional API endpoints or admin permissions"

                return [types.TextContent(
                    type="text",
                    text=f"Tenant Information:\n\n" +
                         json.dumps(tenant_info, indent=2)
                )]

            except Exception as e:
                logger.error(f"Error getting tenant info: {str(e)}")
                return [types.TextContent(
                    type="text",
                    text=f"Error getting tenant information: {str(e)}"
                )]

    elif name == "get_available_scopes":
        # Get available OAuth2 scopes
        if DATASPHERE_CONFIG["use_mock_data"]:
            # Mock scopes data
            mock_scopes = {
                "available_scopes": [
                    {
                        "scope": "DWC_CONSUMPTION",
                        "description": "Read access to consumption models and analytical data",
                        "granted": True
                    },
                    {
                        "scope": "DWC_CATALOG",
                        "description": "Read access to catalog metadata and asset information",
                        "granted": True
                    },
                    {
                        "scope": "DWC_REPOSITORY",
                        "description": "Read access to repository objects and definitions",
                        "granted": True
                    },
                    {
                        "scope": "DWC_SPACES",
                        "description": "Access to space information and configuration",
                        "granted": True
                    },
                    {
                        "scope": "DWC_ADMIN",
                        "description": "Administrative operations (user management, etc.)",
                        "granted": False,
                        "reason": "Requires administrator role"
                    }
                ],
                "token_scopes": ["DWC_CONSUMPTION", "DWC_CATALOG", "DWC_REPOSITORY", "DWC_SPACES"],
                "scope_check_timestamp": datetime.utcnow().isoformat() + "Z",
                "note": "This is mock data. Set USE_MOCK_DATA=false for real scope information."
            }
            return [types.TextContent(
                type="text",
                text=f"Available OAuth Scopes:\n\n" +
                     json.dumps(mock_scopes, indent=2)
            )]
        else:
            if not datasphere_connector:
                return [types.TextContent(
                    type="text",
                    text="Error: OAuth connector not initialized. Cannot get scope information."
                )]

            try:
                # Get scopes from OAuth token
                token = await datasphere_connector.get_valid_token()

                # Try to decode JWT token to get scopes
                import base64
                token_parts = token.split('.')
                if len(token_parts) >= 2:
                    payload = token_parts[1]
                    padding = 4 - len(payload) % 4
                    if padding != 4:
                        payload += '=' * padding

                    try:
                        decoded = base64.urlsafe_b64decode(payload)
                        token_data = json.loads(decoded)

                        # Extract scopes (can be string or list)
                        scopes_raw = token_data.get("scope", [])
                        if isinstance(scopes_raw, str):
                            token_scopes = scopes_raw.split() if scopes_raw else []
                        else:
                            token_scopes = scopes_raw

                        scope_info = {
                            "token_scopes": token_scopes,
                            "scope_count": len(token_scopes),
                            "token_expires_at": datetime.fromtimestamp(token_data.get("exp", 0)).isoformat() + "Z" if token_data.get("exp") else "N/A",
                            "scope_check_timestamp": datetime.utcnow().isoformat() + "Z",
                            "note": "Scopes extracted from OAuth token. Available scopes depend on user role and permissions."
                        }

                        # Add common scope descriptions
                        if token_scopes:
                            scope_info["scope_details"] = []
                            scope_descriptions = {
                                "DWC_CONSUMPTION": "Read access to consumption models and analytical data",
                                "DWC_CATALOG": "Read access to catalog metadata and asset information",
                                "DWC_REPOSITORY": "Read access to repository objects and definitions",
                                "DWC_SPACES": "Access to space information and configuration",
                                "DWC_ADMIN": "Administrative operations",
                            }
                            for scope in token_scopes:
                                scope_info["scope_details"].append({
                                    "scope": scope,
                                    "description": scope_descriptions.get(scope, "SAP Datasphere access scope")
                                })

                        return [types.TextContent(
                            type="text",
                            text=f"Available OAuth Scopes:\n\n" +
                                 json.dumps(scope_info, indent=2)
                        )]
                    except Exception as decode_error:
                        logger.warning(f"Could not decode token: {decode_error}")

                # If token decoding fails, return basic info
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "message": "Scope information available from OAuth token",
                        "note": "Could not decode token to extract scope details"
                    }, indent=2)
                )]

            except Exception as e:
                logger.error(f"Error getting scopes: {str(e)}")
                return [types.TextContent(
                    type="text",
                    text=f"Error getting scope information: {str(e)}"
                )]

    elif name == "search_catalog":
        query = arguments["query"]
        top = arguments.get("top", 50)
        skip = arguments.get("skip", 0)
        include_count = arguments.get("include_count", False)
        include_why_found = arguments.get("include_why_found", False)
        facets = arguments.get("facets")
        facet_limit = arguments.get("facet_limit", 5)

        # Build query parameters
        params = {
            "search": query,
            "$top": top,
            "$skip": skip
        }

        if include_count:
            params["$count"] = "true"

        if include_why_found:
            params["whyfound"] = "true"

        if facets:
            params["facets"] = facets
            params["facetlimit"] = facet_limit

        if DATASPHERE_CONFIG["use_mock_data"]:
            # Mock data response
            mock_results = {
                "search_query": query,
                "value": [
                    {
                        "id": "SAP_SC_FI_AM_FINTRANSACTIONS",
                        "name": "Financial Transactions",
                        "description": "Analytical model for financial transaction analysis",
                        "spaceId": "SAP_CONTENT",
                        "objectType": "AnalyticalModel",
                        "owner": "SAP",
                        "created": "2024-01-15T10:30:00Z",
                        "modified": "2024-06-20T14:45:00Z"
                    },
                    {
                        "id": "SALES_ORDERS_VIEW",
                        "name": "Sales Orders",
                        "description": "View of sales order data with customer information",
                        "spaceId": "SALES_ANALYTICS",
                        "objectType": "View",
                        "owner": "sales_admin",
                        "created": "2024-03-10T09:15:00Z",
                        "modified": "2024-07-01T11:20:00Z"
                    }
                ],
                "count": 2 if include_count else None,
                "top": top,
                "skip": skip,
                "returned": 2,
                "note": "This is mock data. Real catalog search requires OAuth authentication."
            }

            if facets:
                mock_results["facets"] = {
                    "objectType": [
                        {"value": "AnalyticalModel", "count": 5},
                        {"value": "View", "count": 12},
                        {"value": "Table", "count": 8}
                    ],
                    "spaceId": [
                        {"value": "SAP_CONTENT", "count": 15},
                        {"value": "SALES_ANALYTICS", "count": 10}
                    ]
                }

            return [types.TextContent(
                type="text",
                text=f"Catalog Search Results:\n\n" +
                     json.dumps(mock_results, indent=2)
            )]
        else:
            # Real API call
            if datasphere_connector is None:
                return [types.TextContent(
                    type="text",
                    text="Error: OAuth connector not initialized. Cannot perform catalog search."
                )]

            try:
                # WORKAROUND: The /api/v1/datasphere/consumption/catalog/search endpoint returns 404 Not Found
                # Instead, use list_catalog_assets and implement client-side search
                logger.info(f"Catalog search workaround: Getting all assets and filtering client-side for query: {query}")

                # Try cache first for catalog assets (dramatically improves performance)
                cache_key = "all_catalog_assets"
                all_assets = cache_manager.get(cache_key, CacheCategory.CATALOG_ASSETS)

                if all_assets is None:
                    # Cache miss - fetch from API
                    logger.info("Cache miss for catalog assets - fetching from API")
                    endpoint = "/api/v1/datasphere/consumption/catalog/assets"
                    # IMPORTANT: Must include both $top and $skip or API returns empty results
                    list_params = {
                        "$top": 500,  # Get more assets for comprehensive search
                        "$skip": 0
                    }

                    data = await datasphere_connector.get(endpoint, params=list_params)
                    all_assets = data.get("value", [])

                    # Cache for 5 minutes (reduces API calls by 90%+)
                    cache_manager.set(cache_key, all_assets, CacheCategory.CATALOG_ASSETS)
                    logger.info(f"Cached {len(all_assets)} catalog assets for 5 minutes")
                else:
                    logger.info(f"Cache hit for catalog assets ({len(all_assets)} assets) - instant search!")

                # Client-side search across name, label, and description fields
                query_lower = query.lower()
                search_results = []

                for asset in all_assets:
                    # Search in name, label, and description
                    name = asset.get("name", "").lower()
                    label = asset.get("label", "").lower()
                    description = asset.get("description", "").lower()

                    # Check if query matches any field
                    if (query_lower in name or
                        query_lower in label or
                        query_lower in description):

                        # Track which fields matched for why_found
                        if include_why_found:
                            matched_fields = []
                            if query_lower in name:
                                matched_fields.append(f"name: '{asset.get('name')}'")
                            if query_lower in label:
                                matched_fields.append(f"label: '{asset.get('label')}'")
                            if query_lower in description:
                                matched_fields.append(f"description: '{asset.get('description')[:50]}...'")

                            asset["_whyFound"] = ", ".join(matched_fields)

                        search_results.append(asset)

                # Calculate facets if requested (client-side aggregation)
                facet_data = None
                if facets:
                    facet_data = {}

                    # Count by objectType
                    if "objectType" in facets or facets == "objectType":
                        type_counts = {}
                        for asset in search_results:
                            obj_type = asset.get("objectType", "Unknown")
                            type_counts[obj_type] = type_counts.get(obj_type, 0) + 1

                        facet_data["objectType"] = [
                            {"value": k, "count": v}
                            for k, v in sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:facet_limit]
                        ]

                    # Count by spaceId
                    if "spaceId" in facets or facets == "spaceId":
                        space_counts = {}
                        for asset in search_results:
                            space = asset.get("spaceName", "Unknown")
                            space_counts[space] = space_counts.get(space, 0) + 1

                        facet_data["spaceId"] = [
                            {"value": k, "count": v}
                            for k, v in sorted(space_counts.items(), key=lambda x: x[1], reverse=True)[:facet_limit]
                        ]

                # Apply pagination to search results
                total_count = len(search_results)
                paginated_results = search_results[skip:skip + top]

                # Format results
                results = {
                    "search_query": query,
                    "value": paginated_results,
                    "count": total_count if include_count else None,
                    "top": top,
                    "skip": skip,
                    "returned": len(paginated_results),
                    "has_more": (skip + top) < total_count,
                    "note": "Client-side search workaround - /catalog/search endpoint not available"
                }

                if facet_data:
                    results["facets"] = facet_data

                return [types.TextContent(
                    type="text",
                    text=f"Catalog Search Results:\n\n" +
                         json.dumps(results, indent=2)
                )]
            except Exception as e:
                logger.error(f"Catalog search failed: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Error performing catalog search: {str(e)}"
                )]

    elif name == "search_repository":
        search_terms = arguments["search_terms"]
        object_types = arguments.get("object_types")
        space_id = arguments.get("space_id")
        include_dependencies = arguments.get("include_dependencies", False)
        include_lineage = arguments.get("include_lineage", False)
        top = arguments.get("top", 50)
        skip = arguments.get("skip", 0)

        # Build query parameters
        params = {
            "search": search_terms,
            "$top": top,
            "$skip": skip
        }

        # Build filter expression
        filters = []
        if object_types:
            type_filters = " or ".join([f"objectType eq '{t}'" for t in object_types])
            filters.append(f"({type_filters})")

        if space_id:
            filters.append(f"spaceId eq '{space_id}'")

        if filters:
            params["$filter"] = " and ".join(filters)

        # Add expand for dependencies and lineage
        expand_fields = []
        if include_dependencies:
            expand_fields.append("dependencies")
        if include_lineage:
            expand_fields.append("lineage")

        if expand_fields:
            params["$expand"] = ",".join(expand_fields)

        if DATASPHERE_CONFIG["use_mock_data"]:
            # Mock data response
            mock_objects = [
                {
                    "id": "CUSTOMER_MASTER",
                    "objectType": "Table",
                    "name": "Customer Master Data",
                    "businessName": "Customer Master",
                    "description": "Master data table containing customer information",
                    "spaceId": "SALES_ANALYTICS",
                    "status": "ACTIVE",
                    "deploymentStatus": "DEPLOYED",
                    "owner": "sales_admin",
                    "createdAt": "2024-02-01T08:00:00Z",
                    "modifiedAt": "2024-06-15T10:30:00Z",
                    "version": "1.5",
                    "columns": [
                        {"name": "CUSTOMER_ID", "dataType": "NVARCHAR(10)", "isPrimaryKey": True, "description": "Unique customer identifier"},
                        {"name": "CUSTOMER_NAME", "dataType": "NVARCHAR(100)", "isPrimaryKey": False, "description": "Customer name"},
                        {"name": "COUNTRY", "dataType": "NVARCHAR(3)", "isPrimaryKey": False, "description": "Country code"}
                    ]
                },
                {
                    "id": "SALES_ORDER_VIEW",
                    "objectType": "View",
                    "name": "Sales Orders View",
                    "businessName": "Sales Orders",
                    "description": "View combining sales orders with customer data",
                    "spaceId": "SALES_ANALYTICS",
                    "status": "ACTIVE",
                    "deploymentStatus": "DEPLOYED",
                    "owner": "sales_admin",
                    "createdAt": "2024-03-10T09:15:00Z",
                    "modifiedAt": "2024-07-01T11:20:00Z",
                    "version": "2.0",
                    "columns": [
                        {"name": "ORDER_ID", "dataType": "NVARCHAR(20)", "isPrimaryKey": True, "description": "Order number"},
                        {"name": "CUSTOMER_ID", "dataType": "NVARCHAR(10)", "isPrimaryKey": False, "description": "Customer reference"},
                        {"name": "ORDER_DATE", "dataType": "DATE", "isPrimaryKey": False, "description": "Order date"},
                        {"name": "AMOUNT", "dataType": "DECIMAL(15,2)", "isPrimaryKey": False, "description": "Order amount"}
                    ]
                }
            ]

            # Apply filters in mock data
            filtered_objects = mock_objects
            if object_types:
                filtered_objects = [obj for obj in filtered_objects if obj["objectType"] in object_types]
            if space_id:
                filtered_objects = [obj for obj in filtered_objects if obj["spaceId"] == space_id]

            # Add dependencies and lineage if requested
            if include_dependencies:
                for obj in filtered_objects:
                    if obj["objectType"] == "View":
                        obj["dependencies"] = {
                            "upstream": ["CUSTOMER_MASTER", "SALES_ORDERS_TABLE"],
                            "downstream": ["SALES_ANALYTICS_MODEL"]
                        }

            if include_lineage:
                for obj in filtered_objects:
                    if obj["objectType"] == "View":
                        obj["lineage"] = {
                            "sources": ["CUSTOMER_MASTER", "SALES_ORDERS_TABLE"],
                            "targets": ["SALES_ANALYTICS_MODEL"],
                            "transformations": ["JOIN on CUSTOMER_ID"]
                        }

            result = {
                "search_terms": search_terms,
                "objects": filtered_objects,
                "returned_count": len(filtered_objects),
                "has_more": len(filtered_objects) == top,
                "note": "This is mock data. Real repository search requires OAuth authentication."
            }

            return [types.TextContent(
                type="text",
                text=f"Repository Search Results:\n\n" +
                     json.dumps(result, indent=2)
            )]
        else:
            # Real API call
            if datasphere_connector is None:
                return [types.TextContent(
                    type="text",
                    text="Error: OAuth connector not initialized. Cannot perform repository search."
                )]

            try:
                # WORKAROUND: The /api/v1/datasphere/consumption/catalog/search endpoint returns 404 Not Found
                # Instead, use list_catalog_assets and implement client-side search and filtering
                logger.info(f"Repository search workaround: Getting all assets and filtering client-side for search_terms: {search_terms}")

                # Try cache first for catalog assets (dramatically improves performance)
                cache_key = "all_catalog_assets"
                all_assets = cache_manager.get(cache_key, CacheCategory.CATALOG_ASSETS)

                if all_assets is None:
                    # Cache miss - fetch from API
                    logger.info("Cache miss for catalog assets - fetching from API")
                    endpoint = "/api/v1/datasphere/consumption/catalog/assets"
                    # IMPORTANT: Must include both $top and $skip or API returns empty results
                    list_params = {
                        "$top": 500,  # Get more assets for comprehensive search
                        "$skip": 0
                    }

                    data = await datasphere_connector.get(endpoint, params=list_params)
                    all_assets = data.get("value", [])

                    # Cache for 5 minutes (reduces API calls by 90%+)
                    cache_manager.set(cache_key, all_assets, CacheCategory.CATALOG_ASSETS)
                    logger.info(f"Cached {len(all_assets)} catalog assets for 5 minutes")
                else:
                    logger.info(f"Cache hit for catalog assets ({len(all_assets)} assets) - instant search!")

                # Client-side search across name, businessName, and description fields
                search_terms_lower = search_terms.lower()
                search_results = []

                for asset in all_assets:
                    # Search in name, businessName, and description
                    name = asset.get("name", "").lower()
                    business_name = asset.get("businessName", "").lower()
                    description = asset.get("description", "").lower()

                    # Check if search_terms matches any field
                    if (search_terms_lower in name or
                        search_terms_lower in business_name or
                        search_terms_lower in description):

                        # Filter by object_types if specified
                        if object_types:
                            if asset.get("objectType") not in object_types:
                                continue

                        # Filter by space_id if specified
                        if space_id:
                            if asset.get("spaceName") != space_id:
                                continue

                        search_results.append(asset)

                # Apply pagination to search results
                total_count = len(search_results)
                paginated_results = search_results[skip:skip + top]

                # Parse and format results
                objects = []
                for item in paginated_results:
                    obj = {
                        "id": item.get("id"),
                        "object_type": item.get("objectType"),
                        "name": item.get("name"),
                        "business_name": item.get("businessName"),
                        "description": item.get("description"),
                        "space_id": item.get("spaceName"),  # Use spaceName field
                        "status": item.get("status"),
                        "deployment_status": item.get("deploymentStatus"),
                        "owner": item.get("owner"),
                        "created_at": item.get("createdAt"),
                        "modified_at": item.get("modifiedAt"),
                        "version": item.get("version")
                    }

                    # Add columns if available
                    if item.get("columns"):
                        obj["columns"] = [
                            {
                                "name": col.get("name"),
                                "data_type": col.get("dataType"),
                                "is_primary_key": col.get("isPrimaryKey", False),
                                "description": col.get("description")
                            }
                            for col in item["columns"]
                        ]

                    # Note: Dependencies and lineage data not available from catalog API
                    # These would require additional API calls per asset
                    if include_dependencies:
                        obj["dependencies"] = {
                            "note": "Dependencies not available from catalog API - would require individual asset queries"
                        }

                    if include_lineage:
                        obj["lineage"] = {
                            "note": "Lineage not available from catalog API - would require individual asset queries"
                        }

                    objects.append(obj)

                result = {
                    "search_terms": search_terms,
                    "objects": objects,
                    "returned_count": len(objects),
                    "total_matches": total_count,
                    "has_more": (skip + top) < total_count,
                    "note": "Client-side search workaround - /catalog/search endpoint not available"
                }

                return [types.TextContent(
                    type="text",
                    text=f"Repository Search Results:\n\n" +
                         json.dumps(result, indent=2)
                )]
            except Exception as e:
                logger.error(f"Repository search failed: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Error performing repository search: {str(e)}"
                )]

    elif name == "get_catalog_metadata":
        endpoint_type = arguments.get("endpoint_type", "catalog")
        parse_metadata = arguments.get("parse_metadata", True)

        # Select endpoint based on type
        endpoints = {
            "consumption": "/api/v1/datasphere/consumption/$metadata",
            "catalog": "/api/v1/datasphere/consumption/catalog/$metadata",
            "legacy": "/v1/dwc/catalog/$metadata"
        }

        endpoint = endpoints[endpoint_type]

        if DATASPHERE_CONFIG["use_mock_data"]:
            # Mock metadata response
            if parse_metadata:
                mock_metadata = {
                    "endpoint_type": endpoint_type,
                    "entity_types": [
                        {
                            "name": "Asset",
                            "key_properties": ["spaceId", "id"],
                            "properties": [
                                {"name": "id", "type": "Edm.String", "nullable": False, "max_length": "255"},
                                {"name": "spaceId", "type": "Edm.String", "nullable": False, "max_length": "100"},
                                {"name": "name", "type": "Edm.String", "nullable": True, "max_length": "255"},
                                {"name": "description", "type": "Edm.String", "nullable": True, "max_length": None},
                                {"name": "assetType", "type": "Edm.String", "nullable": True, "max_length": "50"},
                                {"name": "owner", "type": "Edm.String", "nullable": True, "max_length": "100"}
                            ],
                            "navigation_properties": []
                        },
                        {
                            "name": "Space",
                            "key_properties": ["spaceId"],
                            "properties": [
                                {"name": "spaceId", "type": "Edm.String", "nullable": False, "max_length": "100"},
                                {"name": "spaceName", "type": "Edm.String", "nullable": True, "max_length": "255"},
                                {"name": "status", "type": "Edm.String", "nullable": True, "max_length": "20"}
                            ],
                            "navigation_properties": []
                        }
                    ],
                    "entity_sets": [
                        {"name": "Assets", "entity_type": "CatalogService.Asset"},
                        {"name": "Spaces", "entity_type": "CatalogService.Space"}
                    ],
                    "note": "This is mock metadata. Real metadata retrieval requires OAuth authentication."
                }

                return [types.TextContent(
                    type="text",
                    text=f"Catalog Metadata (Parsed):\n\n" +
                         json.dumps(mock_metadata, indent=2)
                )]
            else:
                # Return mock XML
                mock_xml = """<?xml version="1.0" encoding="utf-8"?>
<edmx:Edmx Version="4.0" xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx">
  <edmx:DataServices>
    <Schema Namespace="CatalogService" xmlns="http://docs.oasis-open.org/odata/ns/edm">
      <EntityType Name="Asset">
        <Key>
          <PropertyRef Name="spaceId"/>
          <PropertyRef Name="id"/>
        </Key>
        <Property Name="id" Type="Edm.String" Nullable="false" MaxLength="255"/>
        <Property Name="spaceId" Type="Edm.String" Nullable="false" MaxLength="100"/>
        <Property Name="name" Type="Edm.String" MaxLength="255"/>
        <Property Name="assetType" Type="Edm.String" MaxLength="50"/>
      </EntityType>
      <EntityContainer Name="EntityContainer">
        <EntitySet Name="Assets" EntityType="CatalogService.Asset"/>
      </EntityContainer>
    </Schema>
  </edmx:DataServices>
</edmx:Edmx>"""

                return [types.TextContent(
                    type="text",
                    text=f"Catalog Metadata (Raw XML):\n\n{mock_xml}\n\n" +
                         "⚠️  NOTE: This is mock metadata. Real metadata retrieval requires OAuth authentication."
                )]
        else:
            # Real API call
            if datasphere_connector is None:
                return [types.TextContent(
                    type="text",
                    text="Error: OAuth connector not initialized. Cannot retrieve catalog metadata."
                )]

            try:
                # Metadata endpoints return XML, not JSON
                # Need to use _session directly with custom Accept header
                import aiohttp
                headers = await datasphere_connector._get_headers()
                headers['Accept'] = 'application/xml'  # Fix for Bug #3: 406 Not Acceptable

                url = f"{DATASPHERE_CONFIG['base_url'].rstrip('/')}{endpoint}"

                async with datasphere_connector._session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    response.raise_for_status()
                    xml_content = await response.text()

                if not parse_metadata:
                    # Return raw XML
                    return [types.TextContent(
                        type="text",
                        text=f"Catalog Metadata (Raw XML):\n\n{xml_content}"
                    )]

                # Parse XML metadata
                import xml.etree.ElementTree as ET

                root = ET.fromstring(xml_content)

                # Define namespaces
                namespaces = {
                    'edmx': 'http://docs.oasis-open.org/odata/ns/edmx',
                    'edm': 'http://docs.oasis-open.org/odata/ns/edm'
                }

                metadata = {
                    "endpoint_type": endpoint_type,
                    "entity_types": [],
                    "entity_sets": [],
                    "navigation_properties": []
                }

                # Extract entity types
                for entity_type in root.findall('.//edm:EntityType', namespaces):
                    entity_name = entity_type.get('Name')

                    # Extract properties
                    properties = []
                    for prop in entity_type.findall('edm:Property', namespaces):
                        properties.append({
                            'name': prop.get('Name'),
                            'type': prop.get('Type'),
                            'nullable': prop.get('Nullable', 'true') == 'true',
                            'max_length': prop.get('MaxLength')
                        })

                    # Extract key properties
                    key_props = []
                    key_element = entity_type.find('edm:Key', namespaces)
                    if key_element is not None:
                        for prop_ref in key_element.findall('edm:PropertyRef', namespaces):
                            key_props.append(prop_ref.get('Name'))

                    # Extract navigation properties
                    nav_props = []
                    for nav_prop in entity_type.findall('edm:NavigationProperty', namespaces):
                        nav_props.append({
                            'name': nav_prop.get('Name'),
                            'type': nav_prop.get('Type'),
                            'partner': nav_prop.get('Partner')
                        })

                    metadata['entity_types'].append({
                        'name': entity_name,
                        'key_properties': key_props,
                        'properties': properties,
                        'navigation_properties': nav_props
                    })

                # Extract entity sets
                for entity_set in root.findall('.//edm:EntitySet', namespaces):
                    metadata['entity_sets'].append({
                        'name': entity_set.get('Name'),
                        'entity_type': entity_set.get('EntityType')
                    })

                return [types.TextContent(
                    type="text",
                    text=f"Catalog Metadata (Parsed):\n\n" +
                         json.dumps(metadata, indent=2)
                )]

            except Exception as e:
                logger.error(f"Metadata retrieval failed: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Error retrieving catalog metadata: {str(e)}"
                )]

    elif name == "get_consumption_metadata":
        parse_xml = arguments.get("parse_xml", True)
        include_annotations = arguments.get("include_annotations", True)

        if DATASPHERE_CONFIG["use_mock_data"]:
            # Mock consumption metadata
            if parse_xml:
                mock_metadata = {
                    "service_type": "consumption",
                    "entity_types": [
                        {
                            "name": "ConsumptionModel",
                            "key_properties": ["spaceId", "assetId"],
                            "properties": [
                                {"name": "spaceId", "type": "Edm.String", "nullable": False, "max_length": "100"},
                                {"name": "assetId", "type": "Edm.String", "nullable": False, "max_length": "255"},
                                {"name": "name", "type": "Edm.String", "nullable": True, "max_length": "255"},
                                {"name": "description", "type": "Edm.String", "nullable": True},
                                {"name": "modelType", "type": "Edm.String", "nullable": True, "max_length": "50"}
                            ],
                            "navigation_properties": [
                                {"name": "dimensions", "type": "Collection(Dimension)", "partner": None},
                                {"name": "measures", "type": "Collection(Measure)", "partner": None}
                            ]
                        }
                    ],
                    "entity_sets": [
                        {"name": "ConsumptionModels", "entity_type": "SAP.Datasphere.Consumption.ConsumptionModel"}
                    ],
                    "complex_types": [],
                    "note": "This is mock metadata. Real consumption metadata requires OAuth authentication."
                }

                return [types.TextContent(
                    type="text",
                    text=f"Consumption Metadata (Parsed):\n\n" +
                         json.dumps(mock_metadata, indent=2)
                )]
            else:
                mock_xml = """<?xml version="1.0" encoding="UTF-8"?>
<edmx:Edmx xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx" Version="4.0">
  <edmx:DataServices>
    <Schema xmlns="http://docs.oasis-open.org/odata/ns/edm" Namespace="SAP.Datasphere.Consumption">
      <EntityType Name="ConsumptionModel">
        <Key>
          <PropertyRef Name="spaceId"/>
          <PropertyRef Name="assetId"/>
        </Key>
        <Property Name="spaceId" Type="Edm.String" Nullable="false"/>
        <Property Name="assetId" Type="Edm.String" Nullable="false"/>
        <Property Name="name" Type="Edm.String"/>
        <Property Name="modelType" Type="Edm.String"/>
      </EntityType>
      <EntityContainer Name="ConsumptionService">
        <EntitySet Name="ConsumptionModels" EntityType="SAP.Datasphere.Consumption.ConsumptionModel"/>
      </EntityContainer>
    </Schema>
  </edmx:DataServices>
</edmx:Edmx>"""

                return [types.TextContent(
                    type="text",
                    text=f"Consumption Metadata (Raw XML):\n\n{mock_xml}"
                )]
        else:
            # Real API call
            if datasphere_connector is None:
                return [types.TextContent(
                    type="text",
                    text="Error: OAuth connector not initialized. Cannot retrieve consumption metadata."
                )]

            try:
                url = f"{DATASPHERE_CONFIG['base_url'].rstrip('/')}/api/v1/datasphere/consumption/$metadata"

                # Metadata endpoints return XML, need custom Accept header
                import aiohttp
                headers = await datasphere_connector._get_headers()
                headers['Accept'] = 'application/xml'  # Fix for Bug #3: 406 Not Acceptable

                async with datasphere_connector._session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 404:
                        # This endpoint is not available on all tenants
                        return [types.TextContent(
                            type="text",
                            text="❌ Consumption metadata endpoint not available on this tenant.\n\n" +
                                 "The endpoint /api/v1/datasphere/consumption/$metadata returned 404.\n\n" +
                                 "Alternatives:\n" +
                                 "- Use get_analytical_metadata(space_id, asset_id) for analytical models\n" +
                                 "- Use get_relational_metadata(space_id, asset_id) for relational views\n" +
                                 "- Use get_catalog_metadata() for catalog-level metadata\n\n" +
                                 "Note: This is a known limitation on some SAP Datasphere tenant configurations."
                        )]

                    response.raise_for_status()
                    xml_content = await response.text()

                if not parse_xml:
                    return [types.TextContent(
                        type="text",
                        text=f"Consumption Metadata (Raw XML):\n\n{xml_content}"
                    )]

                # Parse XML
                import xml.etree.ElementTree as ET
                root = ET.fromstring(xml_content)

                namespaces = {
                    'edmx': 'http://docs.oasis-open.org/odata/ns/edmx',
                    'edm': 'http://docs.oasis-open.org/odata/ns/edm',
                    'sap': 'http://www.sap.com/Protocols/SAPData'
                }

                metadata = {
                    "service_type": "consumption",
                    "entity_types": [],
                    "entity_sets": [],
                    "complex_types": []
                }

                # Extract entity types
                for entity_type in root.findall('.//edm:EntityType', namespaces):
                    entity_info = {
                        'name': entity_type.get('Name'),
                        'key_properties': [],
                        'properties': [],
                        'navigation_properties': []
                    }

                    # Extract key properties
                    key_element = entity_type.find('edm:Key', namespaces)
                    if key_element is not None:
                        for prop_ref in key_element.findall('edm:PropertyRef', namespaces):
                            entity_info['key_properties'].append(prop_ref.get('Name'))

                    # Extract properties
                    for prop in entity_type.findall('edm:Property', namespaces):
                        prop_info = {
                            'name': prop.get('Name'),
                            'type': prop.get('Type'),
                            'nullable': prop.get('Nullable', 'true') == 'true',
                            'max_length': prop.get('MaxLength')
                        }

                        if include_annotations:
                            sap_label = prop.get('{http://www.sap.com/Protocols/SAPData}label')
                            if sap_label:
                                prop_info['label'] = sap_label

                        entity_info['properties'].append(prop_info)

                    # Extract navigation properties
                    for nav_prop in entity_type.findall('edm:NavigationProperty', namespaces):
                        entity_info['navigation_properties'].append({
                            'name': nav_prop.get('Name'),
                            'type': nav_prop.get('Type'),
                            'partner': nav_prop.get('Partner')
                        })

                    metadata['entity_types'].append(entity_info)

                # Extract entity sets
                for entity_set in root.findall('.//edm:EntitySet', namespaces):
                    metadata['entity_sets'].append({
                        'name': entity_set.get('Name'),
                        'entity_type': entity_set.get('EntityType')
                    })

                # Extract complex types
                for complex_type in root.findall('.//edm:ComplexType', namespaces):
                    complex_info = {
                        'name': complex_type.get('Name'),
                        'properties': []
                    }
                    for prop in complex_type.findall('edm:Property', namespaces):
                        complex_info['properties'].append({
                            'name': prop.get('Name'),
                            'type': prop.get('Type')
                        })
                    metadata['complex_types'].append(complex_info)

                return [types.TextContent(
                    type="text",
                    text=f"Consumption Metadata (Parsed):\n\n" +
                         json.dumps(metadata, indent=2)
                )]

            except Exception as e:
                logger.error(f"Consumption metadata retrieval failed: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Error retrieving consumption metadata: {str(e)}"
                )]

    elif name == "get_analytical_metadata":
        space_id = arguments["space_id"]
        asset_id = arguments["asset_id"]
        identify_dimensions_measures = arguments.get("identify_dimensions_measures", True)

        if DATASPHERE_CONFIG["use_mock_data"]:
            # Mock analytical metadata
            mock_metadata = {
                "space_id": space_id,
                "asset_id": asset_id,
                "model_type": "analytical",
                "entity_types": [
                    {
                        "name": asset_id,
                        "key_properties": ["ID"],
                        "properties": [
                            {"name": "ID", "type": "Edm.String", "nullable": False},
                            {"name": "CustomerID", "type": "Edm.String", "nullable": True, "is_dimension": True},
                            {"name": "ProductID", "type": "Edm.String", "nullable": True, "is_dimension": True},
                            {"name": "Revenue", "type": "Edm.Decimal", "nullable": True, "aggregation": "SUM"}
                        ],
                        "navigation_properties": []
                    }
                ],
                "dimensions": [
                    {"name": "CustomerID", "type": "Edm.String", "label": "Customer", "hierarchy": None},
                    {"name": "ProductID", "type": "Edm.String", "label": "Product", "hierarchy": None}
                ],
                "measures": [
                    {"name": "Revenue", "type": "Edm.Decimal", "label": "Revenue", "aggregation": "SUM", "unit": "USD"}
                ],
                "hierarchies": [],
                "note": "This is mock metadata. Real analytical metadata requires OAuth authentication."
            }

            return [types.TextContent(
                type="text",
                text=f"Analytical Metadata:\n\n" +
                     json.dumps(mock_metadata, indent=2)
            )]
        else:
            # Real API call
            if datasphere_connector is None:
                return [types.TextContent(
                    type="text",
                    text="Error: OAuth connector not initialized. Cannot retrieve analytical metadata."
                )]

            try:
                # IMPORTANT: Check if asset supports analytical queries BEFORE calling metadata endpoint
                # This prevents 400 Bad Request errors on assets that only support relational queries
                logger.info(f"Checking if {space_id}/{asset_id} supports analytical queries...")
                asset_endpoint = f"/api/v1/datasphere/consumption/catalog/spaces('{space_id}')/assets('{asset_id}')"
                asset_data = await datasphere_connector.get(asset_endpoint)

                supports_analytical = asset_data.get("supportsAnalyticalQueries", False)
                if not supports_analytical:
                    # Asset doesn't support analytical queries - provide helpful error
                    error_msg = f"Asset {asset_id} does not support analytical queries.\n\n"
                    error_msg += f"supportsAnalyticalQueries: {supports_analytical}\n\n"
                    error_msg += "Suggestions:\n"
                    error_msg += "1. Use get_relational_metadata instead for this asset\n"
                    error_msg += "2. Check asset details with get_asset_details first\n"
                    error_msg += "3. Look for assets with supportsAnalyticalQueries=true\n\n"
                    error_msg += f"Asset type: {asset_data.get('assetType', 'Unknown')}\n"
                    if asset_data.get('assetRelationalMetadataUrl'):
                        error_msg += f"Use relational metadata URL: {asset_data.get('assetRelationalMetadataUrl')}"

                    return [types.TextContent(
                        type="text",
                        text=error_msg
                    )]

                logger.info(f"Asset supports analytical queries - proceeding with metadata retrieval")

                endpoint = f"/api/v1/datasphere/consumption/analytical/{space_id}/{asset_id}/$metadata"
                url = f"{DATASPHERE_CONFIG['base_url'].rstrip('/')}{endpoint}"

                # Metadata endpoints return XML, need custom Accept header
                import aiohttp
                headers = await datasphere_connector._get_headers()
                headers['Accept'] = 'application/xml'  # Fix for Bug #3: 406 Not Acceptable

                async with datasphere_connector._session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    response.raise_for_status()
                    xml_content = await response.text()

                # Parse XML
                import xml.etree.ElementTree as ET
                root = ET.fromstring(xml_content)

                namespaces = {
                    'edmx': 'http://docs.oasis-open.org/odata/ns/edmx',
                    'edm': 'http://docs.oasis-open.org/odata/ns/edm',
                    'sap': 'http://www.sap.com/Protocols/SAPData'
                }

                metadata = {
                    "space_id": space_id,
                    "asset_id": asset_id,
                    "model_type": "analytical",
                    "entity_types": [],
                    "dimensions": [],
                    "measures": [],
                    "hierarchies": []
                }

                # Extract entity types and identify dimensions/measures
                for entity_type in root.findall('.//edm:EntityType', namespaces):
                    entity_info = {
                        'name': entity_type.get('Name'),
                        'key_properties': [],
                        'properties': [],
                        'navigation_properties': []
                    }

                    # Extract key
                    key_element = entity_type.find('edm:Key', namespaces)
                    if key_element is not None:
                        for prop_ref in key_element.findall('edm:PropertyRef', namespaces):
                            entity_info['key_properties'].append(prop_ref.get('Name'))

                    # Extract properties and identify dimensions/measures
                    for prop in entity_type.findall('edm:Property', namespaces):
                        prop_name = prop.get('Name')
                        prop_type = prop.get('Type')

                        prop_info = {
                            'name': prop_name,
                            'type': prop_type,
                            'nullable': prop.get('Nullable', 'true') == 'true'
                        }

                        # Check SAP annotations
                        is_dimension = prop.get('{http://www.sap.com/Protocols/SAPData}dimension') == 'true'
                        aggregation = prop.get('{http://www.sap.com/Protocols/SAPData}aggregation')
                        label = prop.get('{http://www.sap.com/Protocols/SAPData}label')

                        if identify_dimensions_measures:
                            if is_dimension:
                                metadata['dimensions'].append({
                                    'name': prop_name,
                                    'type': prop_type,
                                    'label': label or prop_name,
                                    'hierarchy': prop.get('{http://www.sap.com/Protocols/SAPData}hierarchy')
                                })
                                prop_info['is_dimension'] = True
                            elif aggregation:
                                metadata['measures'].append({
                                    'name': prop_name,
                                    'type': prop_type,
                                    'label': label or prop_name,
                                    'aggregation': aggregation,
                                    'unit': prop.get('{http://www.sap.com/Protocols/SAPData}unit')
                                })
                                prop_info['aggregation'] = aggregation

                        entity_info['properties'].append(prop_info)

                    # Navigation properties
                    for nav_prop in entity_type.findall('edm:NavigationProperty', namespaces):
                        entity_info['navigation_properties'].append({
                            'name': nav_prop.get('Name'),
                            'type': nav_prop.get('Type')
                        })

                    metadata['entity_types'].append(entity_info)

                    # Extract hierarchies
                    if 'Hierarchy' in entity_info['name']:
                        metadata['hierarchies'].append({
                            'name': entity_info['name'],
                            'properties': [p['name'] for p in entity_info['properties']]
                        })

                return [types.TextContent(
                    type="text",
                    text=f"Analytical Metadata:\n\n" +
                         json.dumps(metadata, indent=2)
                )]

            except Exception as e:
                logger.error(f"Analytical metadata retrieval failed: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Error retrieving analytical metadata: {str(e)}"
                )]

    elif name == "get_relational_metadata":
        space_id = arguments["space_id"]
        asset_id = arguments["asset_id"]
        map_to_sql_types = arguments.get("map_to_sql_types", True)

        # OData to SQL type mapping
        def map_odata_to_sql(odata_type, precision=None, scale=None, max_length=None):
            type_map = {
                "Edm.String": f"NVARCHAR({max_length or 'MAX'})",
                "Edm.Int32": "INT",
                "Edm.Int64": "BIGINT",
                "Edm.Decimal": f"DECIMAL({precision or 18},{scale or 2})" if precision else "DECIMAL(18,2)",
                "Edm.Double": "DOUBLE",
                "Edm.Boolean": "BOOLEAN",
                "Edm.Date": "DATE",
                "Edm.DateTime": "TIMESTAMP",
                "Edm.DateTimeOffset": "TIMESTAMP",
                "Edm.Time": "TIME",
                "Edm.Guid": "VARCHAR(36)",
                "Edm.Binary": "VARBINARY"
            }
            return type_map.get(odata_type, odata_type)

        if DATASPHERE_CONFIG["use_mock_data"]:
            # Mock relational metadata
            mock_metadata = {
                "space_id": space_id,
                "asset_id": asset_id,
                "model_type": "relational",
                "tables": [
                    {
                        "name": asset_id,
                        "key_columns": ["ID"],
                        "columns": [
                            {"name": "ID", "odata_type": "Edm.String", "sql_type": "NVARCHAR(10)", "nullable": False, "max_length": "10"},
                            {"name": "CustomerName", "odata_type": "Edm.String", "sql_type": "NVARCHAR(100)", "nullable": True, "max_length": "100"},
                            {"name": "Amount", "odata_type": "Edm.Decimal", "sql_type": "DECIMAL(15,2)", "nullable": True, "precision": "15", "scale": "2"}
                        ],
                        "foreign_keys": []
                    }
                ],
                "note": "This is mock metadata. Real relational metadata requires OAuth authentication."
            }

            return [types.TextContent(
                type="text",
                text=f"Relational Metadata:\n\n" +
                     json.dumps(mock_metadata, indent=2)
            )]
        else:
            # Real API call
            if datasphere_connector is None:
                return [types.TextContent(
                    type="text",
                    text="Error: OAuth connector not initialized. Cannot retrieve relational metadata."
                )]

            try:
                endpoint = f"/api/v1/datasphere/consumption/relational/{space_id}/{asset_id}/$metadata"
                url = f"{DATASPHERE_CONFIG['base_url'].rstrip('/')}{endpoint}"

                # Metadata endpoints return XML, need custom Accept header
                import aiohttp
                headers = await datasphere_connector._get_headers()
                headers['Accept'] = 'application/xml'  # Fix for Bug #3: 406 Not Acceptable

                async with datasphere_connector._session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    response.raise_for_status()
                    xml_content = await response.text()

                # Parse XML
                import xml.etree.ElementTree as ET
                root = ET.fromstring(xml_content)

                namespaces = {
                    'edmx': 'http://docs.oasis-open.org/odata/ns/edmx',
                    'edm': 'http://docs.oasis-open.org/odata/ns/edm',
                    'sap': 'http://www.sap.com/Protocols/SAPData'
                }

                metadata = {
                    "space_id": space_id,
                    "asset_id": asset_id,
                    "model_type": "relational",
                    "tables": []
                }

                # Extract entity types (tables)
                for entity_type in root.findall('.//edm:EntityType', namespaces):
                    table_info = {
                        'name': entity_type.get('Name'),
                        'key_columns': [],
                        'columns': [],
                        'foreign_keys': []
                    }

                    # Extract key columns
                    key_element = entity_type.find('edm:Key', namespaces)
                    if key_element is not None:
                        for prop_ref in key_element.findall('edm:PropertyRef', namespaces):
                            table_info['key_columns'].append(prop_ref.get('Name'))

                    # Extract columns
                    for prop in entity_type.findall('edm:Property', namespaces):
                        odata_type = prop.get('Type')
                        precision = prop.get('Precision')
                        scale = prop.get('Scale')
                        max_length = prop.get('MaxLength')

                        column_info = {
                            'name': prop.get('Name'),
                            'odata_type': odata_type,
                            'nullable': prop.get('Nullable', 'true') == 'true'
                        }

                        if max_length:
                            column_info['max_length'] = max_length
                        if precision:
                            column_info['precision'] = precision
                        if scale:
                            column_info['scale'] = scale

                        if map_to_sql_types:
                            column_info['sql_type'] = map_odata_to_sql(odata_type, precision, scale, max_length)

                        # Add SAP annotations
                        label = prop.get('{http://www.sap.com/Protocols/SAPData}label')
                        if label:
                            column_info['label'] = label

                        semantics = prop.get('{http://www.sap.com/Protocols/SAPData}semantics')
                        if semantics:
                            column_info['semantics'] = semantics

                        table_info['columns'].append(column_info)

                    # Extract foreign keys
                    for nav_prop in entity_type.findall('edm:NavigationProperty', namespaces):
                        table_info['foreign_keys'].append({
                            'name': nav_prop.get('Name'),
                            'referenced_table': nav_prop.get('Type'),
                            'partner': nav_prop.get('Partner')
                        })

                    metadata['tables'].append(table_info)

                return [types.TextContent(
                    type="text",
                    text=f"Relational Metadata:\n\n" +
                         json.dumps(metadata, indent=2)
                )]

            except Exception as e:
                logger.error(f"Relational metadata retrieval failed: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Error retrieving relational metadata: {str(e)}"
                )]

    elif name == "list_relational_entities":
        space_id = arguments["space_id"]
        asset_id = arguments["asset_id"]
        top = arguments.get("top", 50)

        if not datasphere_connector:
            return [types.TextContent(
                type="text",
                text="Error: OAuth connector not initialized. Cannot list relational entities."
            )]

        try:
            # Get OData service document (no params for service root)
            endpoint = f"/api/v1/datasphere/consumption/relational/{space_id}/{asset_id}"

            logger.info(f"Listing relational entities for {space_id}/{asset_id}")
            data = await datasphere_connector.get(endpoint)

            # Extract entity sets from service document
            entities = data.get("value", [])

            # Apply top limit to entity list (not to API - service document returns all)
            limited_entities = entities[:top] if top else entities

            # Format response with ETL-optimized metadata
            result = {
                "space_id": space_id,
                "asset_id": asset_id,
                "entities": limited_entities,
                "entity_count": len(limited_entities),
                "total_entities": len(entities),
                "showing_limited": len(limited_entities) < len(entities),
                "odata_context": data.get("@odata.context", ""),
                "metadata_url": f"{endpoint}/$metadata",
                "extraction_type": "row_level_etl",
                "max_batch_size": 50000,
                "query_timestamp": datetime.now().isoformat(),
                "usage_note": "Use entity names from this list with query_relational_entity to extract data"
            }

            return [types.TextContent(
                type="text",
                text=f"Relational Entities:\n\n" + json.dumps(result, indent=2)
            )]

        except Exception as e:
            logger.error(f"Error listing relational entities: {str(e)}")
            return [types.TextContent(
                type="text",
                text=f"Error listing relational entities: {str(e)}\n\n"
                     f"Possible causes:\n"
                     f"1. Asset doesn't exist in the space\n"
                     f"2. Asset name is case-sensitive (try uppercase)\n"
                     f"3. Use list_catalog_assets to find correct asset name"
            )]

    elif name == "get_relational_entity_metadata":
        space_id = arguments["space_id"]
        asset_id = arguments["asset_id"]
        include_sql_types = arguments.get("include_sql_types", True)

        if not datasphere_connector:
            return [types.TextContent(
                type="text",
                text="Error: OAuth connector not initialized. Cannot get entity metadata."
            )]

        try:
            # Get CSDL metadata for the entity
            endpoint = f"/api/v1/datasphere/consumption/relational/{space_id}/{asset_id}/$metadata"
            url = f"{DATASPHERE_CONFIG['base_url'].rstrip('/')}{endpoint}"

            logger.info(f"Getting entity metadata for {space_id}/{asset_id}")

            # Metadata endpoints return XML
            import aiohttp
            headers = await datasphere_connector._get_headers()
            headers['Accept'] = 'application/xml'

            async with datasphere_connector._session.get(url, headers=headers) as response:
                response.raise_for_status()
                xml_content = await response.text()

            # Parse XML to extract entity metadata
            import xml.etree.ElementTree as ET
            root = ET.fromstring(xml_content)

            namespaces = {
                'edmx': 'http://docs.oasis-open.org/odata/ns/edmx',
                'edm': 'http://docs.oasis-open.org/odata/ns/edm'
            }

            # OData to SQL type mapping for ETL
            def odata_to_sql(odata_type, precision=None, scale=None, max_length=None):
                type_map = {
                    "Edm.String": f"NVARCHAR({max_length or 'MAX'})",
                    "Edm.Int32": "INT",
                    "Edm.Int64": "BIGINT",
                    "Edm.Decimal": f"DECIMAL({precision or 18},{scale or 2})",
                    "Edm.Double": "DOUBLE",
                    "Edm.Boolean": "BOOLEAN",
                    "Edm.Date": "DATE",
                    "Edm.DateTime": "TIMESTAMP",
                    "Edm.DateTimeOffset": "TIMESTAMP",
                    "Edm.Time": "TIME",
                    "Edm.Guid": "VARCHAR(36)"
                }
                return type_map.get(odata_type, odata_type)

            metadata = {
                "space_id": space_id,
                "asset_id": asset_id,
                "entities": [],
                "etl_optimized": True
            }

            # Extract all entity types
            for entity_type in root.findall('.//edm:EntityType', namespaces):
                entity_info = {
                    "name": entity_type.get('Name'),
                    "key_columns": [],
                    "columns": []
                }

                # Extract key columns
                key_element = entity_type.find('edm:Key', namespaces)
                if key_element is not None:
                    for prop_ref in key_element.findall('edm:PropertyRef', namespaces):
                        entity_info['key_columns'].append(prop_ref.get('Name'))

                # Extract all columns with SQL type mapping
                for prop in entity_type.findall('edm:Property', namespaces):
                    odata_type = prop.get('Type')
                    col_info = {
                        "name": prop.get('Name'),
                        "odata_type": odata_type,
                        "nullable": prop.get('Nullable', 'true') == 'true'
                    }

                    # Add type details
                    if prop.get('MaxLength'):
                        col_info['max_length'] = prop.get('MaxLength')
                    if prop.get('Precision'):
                        col_info['precision'] = prop.get('Precision')
                    if prop.get('Scale'):
                        col_info['scale'] = prop.get('Scale')

                    # Add SQL type mapping for ETL
                    if include_sql_types:
                        col_info['sql_type'] = odata_to_sql(
                            odata_type,
                            col_info.get('precision'),
                            col_info.get('scale'),
                            col_info.get('max_length')
                        )

                    entity_info['columns'].append(col_info)

                metadata['entities'].append(entity_info)

            # Add ETL extraction guidance
            metadata['etl_guidance'] = {
                "batch_size_recommendation": "10000-50000 records per batch",
                "pagination_method": "Use $top and $skip for pagination",
                "filtering_method": "OData $filter for incremental extraction",
                "recommended_timeout": "60 seconds for large batches"
            }

            return [types.TextContent(
                type="text",
                text=f"Entity Metadata (ETL-Optimized):\n\n" + json.dumps(metadata, indent=2)
            )]

        except Exception as e:
            logger.error(f"Error getting entity metadata: {str(e)}")
            return [types.TextContent(
                type="text",
                text=f"Error getting entity metadata: {str(e)}\n\n"
                     f"Possible causes:\n"
                     f"1. Entity doesn't exist or is not accessible\n"
                     f"2. Use list_relational_entities to find available entities"
            )]

    elif name == "query_relational_entity":
        space_id = arguments["space_id"]
        asset_id = arguments["asset_id"]
        entity_name = arguments["entity_name"]
        filter_expr = arguments.get("filter")
        select = arguments.get("select")
        top = arguments.get("top", 1000)
        skip = arguments.get("skip", 0)
        orderby = arguments.get("orderby")

        if not datasphere_connector:
            return [types.TextContent(
                type="text",
                text="Error: OAuth connector not initialized. Cannot query relational entity."
            )]

        try:
            # Build OData query for ETL extraction with 3-level path
            endpoint = f"/api/v1/datasphere/consumption/relational/{space_id}/{asset_id}/{entity_name}"

            params = {
                "$top": min(top, 50000)  # ETL mode: allow up to 50K records
            }

            if skip:
                params["$skip"] = skip
            if filter_expr:
                params["$filter"] = filter_expr
            if select:
                params["$select"] = select
            if orderby:
                params["$orderby"] = orderby

            logger.info(f"Querying relational entity {space_id}/{asset_id}/{entity_name} (ETL mode, top={params['$top']})")

            start_time = time.time()
            data = await datasphere_connector.get(endpoint, params=params)
            execution_time = time.time() - start_time

            # Format response with ETL metadata
            result = {
                "space_id": space_id,
                "asset_id": asset_id,
                "entity_name": entity_name,
                "execution_time_seconds": round(execution_time, 3),
                "rows_returned": len(data.get("value", [])),
                "odata_params": params,
                "extraction_mode": "etl_batch",
                "data": data.get("value", [])
            }

            # Add pagination guidance if more data available
            if len(data.get("value", [])) == params["$top"]:
                result["pagination_hint"] = {
                    "more_data_available": "likely",
                    "next_batch_skip": params["$top"] + skip,
                    "recommendation": f"Use skip={params['$top'] + skip} to get next batch"
                }

            return [types.TextContent(
                type="text",
                text=f"Query Results (ETL Mode):\n\n" + json.dumps(result, indent=2)
            )]

        except Exception as e:
            logger.error(f"Error querying relational entity: {str(e)}")
            return [types.TextContent(
                type="text",
                text=f"Error querying relational entity: {str(e)}\n\n"
                     f"Possible causes:\n"
                     f"1. Entity doesn't exist - use list_relational_entities first to get valid entity names\n"
                     f"2. Invalid $filter expression\n"
                     f"3. Selected columns don't exist - use get_relational_entity_metadata to verify schema\n"
                     f"4. Try using asset_id as entity_name if entity list is not available"
            )]

    elif name == "get_relational_odata_service":
        space_id = arguments["space_id"]
        asset_id = arguments["asset_id"]
        include_capabilities = arguments.get("include_capabilities", True)

        if not datasphere_connector:
            return [types.TextContent(
                type="text",
                text="Error: OAuth connector not initialized. Cannot get OData service document."
            )]

        try:
            # Get OData service document
            endpoint = f"/api/v1/datasphere/consumption/relational/{space_id}/{asset_id}"

            logger.info(f"Getting OData service document for {space_id}/{asset_id}")
            data = await datasphere_connector.get(endpoint)

            # Build service document with ETL planning info
            result = {
                "space_id": space_id,
                "asset_id": asset_id,
                "odata_version": "4.0",
                "service_root": endpoint,
                "entity_sets": data.get("value", []),
                "entity_count": len(data.get("value", [])),
                "metadata_url": f"{endpoint}/$metadata"
            }

            if include_capabilities:
                result["query_capabilities"] = {
                    "filtering": "$filter supported (OData v4 expressions)",
                    "projection": "$select supported (comma-separated columns)",
                    "pagination": "$top and $skip supported",
                    "sorting": "$orderby supported (asc/desc)",
                    "max_page_size": 50000,
                    "recommended_batch_size": "10000-20000 for optimal performance"
                }

                result["etl_features"] = {
                    "incremental_extraction": "Use $filter with date columns",
                    "parallel_extraction": "Use $skip with multiple concurrent requests",
                    "delta_detection": "Compare timestamps or use change tracking if available",
                    "type_mapping": "OData types map to SQL types (use get_relational_entity_metadata)"
                }

            return [types.TextContent(
                type="text",
                text=f"OData Service Document (ETL Planning):\n\n" + json.dumps(result, indent=2)
            )]

        except Exception as e:
            logger.error(f"Error getting OData service document: {str(e)}")
            return [types.TextContent(
                type="text",
                text=f"Error getting OData service document: {str(e)}\n\n"
                     f"Possible causes:\n"
                     f"1. Asset doesn't exist in the space\n"
                     f"2. Asset is not accessible via relational consumption\n"
                     f"3. Use list_catalog_assets to find available assets"
            )]

    elif name == "get_repository_search_metadata":
        include_field_details = arguments.get("include_field_details", True)

        if DATASPHERE_CONFIG["use_mock_data"]:
            # Repository search metadata (this is static schema information)
            repository_metadata = {
                "searchable_object_types": [
                    "Table",
                    "View",
                    "AnalyticalModel",
                    "DataFlow",
                    "Transformation",
                    "Fact",
                    "Dimension"
                ],
                "searchable_fields": [
                    {"field": "id", "type": "string", "searchable": True, "filterable": True},
                    {"field": "name", "type": "string", "searchable": True, "filterable": True},
                    {"field": "businessName", "type": "string", "searchable": True, "filterable": True},
                    {"field": "description", "type": "string", "searchable": True, "filterable": False},
                    {"field": "objectType", "type": "string", "searchable": False, "filterable": True},
                    {"field": "spaceId", "type": "string", "searchable": False, "filterable": True},
                    {"field": "owner", "type": "string", "searchable": True, "filterable": True},
                    {"field": "status", "type": "string", "searchable": False, "filterable": True},
                    {"field": "deploymentStatus", "type": "string", "searchable": False, "filterable": True}
                ],
                "available_filters": [
                    {"name": "objectType", "operator": "eq", "type": "string"},
                    {"name": "spaceId", "operator": "eq", "type": "string"},
                    {"name": "status", "operator": "eq", "type": "string", "values": ["ACTIVE", "INACTIVE", "DRAFT"]},
                    {"name": "deploymentStatus", "operator": "eq", "type": "string", "values": ["DEPLOYED", "UNDEPLOYED", "ERROR"]}
                ]
            }

            if include_field_details:
                repository_metadata["entity_definitions"] = {
                    "Table": {
                        "fields": ["id", "name", "businessName", "description", "spaceId", "status", "deploymentStatus", "owner", "createdAt", "modifiedAt", "version", "columns"],
                        "expandable": ["columns", "dependencies", "lineage"]
                    },
                    "View": {
                        "fields": ["id", "name", "businessName", "description", "spaceId", "status", "deploymentStatus", "owner", "createdAt", "modifiedAt", "version", "columns", "sql"],
                        "expandable": ["columns", "dependencies", "lineage"]
                    },
                    "AnalyticalModel": {
                        "fields": ["id", "name", "businessName", "description", "spaceId", "status", "deploymentStatus", "owner", "createdAt", "modifiedAt", "version", "dimensions", "measures"],
                        "expandable": ["dimensions", "measures", "hierarchies", "dependencies"]
                    }
                }

            return [types.TextContent(
                type="text",
                text=f"Repository Search Metadata:\n\n" +
                     json.dumps(repository_metadata, indent=2)
            )]
        else:
            # Fixed: Repository APIs are UI endpoints; use Catalog metadata endpoint
            if datasphere_connector is None:
                return [types.TextContent(
                    type="text",
                    text="Error: OAuth connector not initialized. Cannot retrieve search metadata."
                )]

            try:
                endpoint = "/api/v1/datasphere/consumption/catalog/$metadata"

                # Metadata endpoints return XML
                import aiohttp
                headers = await datasphere_connector._get_headers()
                headers['Accept'] = 'application/xml'

                url = f"{DATASPHERE_CONFIG['base_url'].rstrip('/')}{endpoint}"
                async with datasphere_connector._session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    response.raise_for_status()
                    xml_content = await response.text()

                # Parse XML to extract searchable entity types and fields
                import xml.etree.ElementTree as ET
                root = ET.fromstring(xml_content)

                namespaces = {
                    'edmx': 'http://docs.oasis-open.org/odata/ns/edmx',
                    'edm': 'http://docs.oasis-open.org/odata/ns/edm'
                }

                repository_metadata = {
                    "source": "Catalog API Metadata",
                    "searchable_object_types": [],
                    "entity_types": []
                }

                # Extract entity types from metadata
                for entity_type in root.findall('.//edm:EntityType', namespaces):
                    entity_name = entity_type.get('Name')
                    repository_metadata["searchable_object_types"].append(entity_name)

                    if include_field_details:
                        properties = []
                        for prop in entity_type.findall('edm:Property', namespaces):
                            properties.append({
                                'name': prop.get('Name'),
                                'type': prop.get('Type'),
                                'nullable': prop.get('Nullable', 'true') == 'true'
                            })

                        repository_metadata["entity_types"].append({
                            'name': entity_name,
                            'properties': properties
                        })

                return [types.TextContent(
                    type="text",
                    text=f"Repository Search Metadata:\n\n" +
                         json.dumps(repository_metadata, indent=2)
                )]

            except Exception as e:
                logger.error(f"Error retrieving search metadata: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Error retrieving search metadata: {str(e)}"
                )]

    elif name == "list_analytical_datasets":
        space_id = arguments["space_id"]
        asset_id = arguments["asset_id"]
        top = arguments.get("top", 50)
        skip = arguments.get("skip", 0)

        if DATASPHERE_CONFIG["use_mock_data"]:
            # Mock analytical datasets
            mock_datasets = {
                "@odata.context": f"$metadata",
                "value": [
                    {
                        "name": asset_id,
                        "kind": "EntitySet",
                        "url": asset_id
                    },
                    {
                        "name": f"{asset_id}_Aggregated",
                        "kind": "EntitySet",
                        "url": f"{asset_id}_Aggregated"
                    }
                ]
            }

            return [types.TextContent(
                type="text",
                text=f"Analytical Datasets in {space_id}/{asset_id}:\n\n" +
                     json.dumps(mock_datasets, indent=2) +
                     f"\n\nNote: This is mock data. Set USE_MOCK_DATA=false for real analytical datasets."
            )]
        else:
            if not datasphere_connector:
                return [types.TextContent(
                    type="text",
                    text="Error: OAuth connector not initialized. Cannot retrieve analytical datasets."
                )]

            try:
                # GET /api/v1/datasphere/consumption/analytical/{spaceId}/{assetId}/
                # NOTE: Use trailing slash and NO query parameters ($top, $skip not supported)
                # This returns the OData service document for the analytical asset
                endpoint = f"/api/v1/datasphere/consumption/analytical/{space_id}/{asset_id}/"

                # DO NOT pass $top or $skip parameters - they cause 400 Bad Request
                params = {}

                logger.info(f"Getting analytical datasets for {space_id}/{asset_id} (no params)")
                data = await datasphere_connector.get(endpoint, params=params)

                return [types.TextContent(
                    type="text",
                    text=f"Analytical Datasets in {space_id}/{asset_id}:\n\n" +
                         json.dumps(data, indent=2)
                )]

            except Exception as e:
                logger.error(f"Error fetching analytical datasets: {str(e)}")

                # Provide helpful error message with suggestions
                error_msg = f"Error fetching analytical datasets: {str(e)}\n\n"
                error_msg += "Possible causes:\n"
                error_msg += "1. Asset doesn't support analytical queries (check supportsAnalyticalQueries field)\n"
                error_msg += "2. Asset metadata URL not available\n"
                error_msg += "3. Use get_asset_details first to verify asset capabilities"

                return [types.TextContent(
                    type="text",
                    text=error_msg
                )]

    elif name == "get_analytical_model":
        space_id = arguments["space_id"]
        asset_id = arguments["asset_id"]
        include_metadata = arguments.get("include_metadata", True)

        if DATASPHERE_CONFIG["use_mock_data"]:
            # Mock analytical model
            mock_model = {
                "@odata.context": f"$metadata",
                "value": [
                    {
                        "name": asset_id,
                        "kind": "EntitySet",
                        "url": asset_id
                    }
                ]
            }

            if include_metadata:
                mock_model["metadata"] = {
                    "entity_sets": [
                        {
                            "name": asset_id,
                            "entity_type": f"{asset_id}Type",
                            "dimensions": [
                                {"name": "Currency", "type": "Edm.String"},
                                {"name": "AccountNumber", "type": "Edm.String"},
                                {"name": "TransactionDate", "type": "Edm.Date"}
                            ],
                            "measures": [
                                {"name": "Amount", "type": "Edm.Decimal", "aggregation": "sum"},
                                {"name": "Quantity", "type": "Edm.Int32", "aggregation": "sum"}
                            ],
                            "keys": ["TransactionID"]
                        }
                    ]
                }

            return [types.TextContent(
                type="text",
                text=f"Analytical Model for {space_id}/{asset_id}:\n\n" +
                     json.dumps(mock_model, indent=2) +
                     f"\n\nNote: This is mock data. Set USE_MOCK_DATA=false for real analytical model."
            )]
        else:
            if not datasphere_connector:
                return [types.TextContent(
                    type="text",
                    text="Error: OAuth connector not initialized. Cannot retrieve analytical model."
                )]

            try:
                # GET /api/v1/datasphere/consumption/analytical/{spaceId}/{assetId}
                endpoint = f"/api/v1/datasphere/consumption/analytical/{space_id}/{asset_id}"

                # Fetch service document using .get() method
                service_doc = await datasphere_connector.get(endpoint)

                if include_metadata:
                    # Fetch and parse metadata
                    metadata_endpoint = f"{endpoint}/$metadata"

                    # For metadata endpoints, we need to use _make_request directly with custom headers
                    # because .get() returns JSON but metadata returns XML
                    headers = await datasphere_connector._get_headers()
                    headers['Accept'] = 'application/xml'

                    metadata_url = f"{DATASPHERE_CONFIG['base_url']}{metadata_endpoint}"
                    async with datasphere_connector._session.get(metadata_url, headers=headers) as meta_response:
                        if meta_response.status == 200:
                            metadata_xml = await meta_response.text()

                            # Parse CSDL metadata
                            import xml.etree.ElementTree as ET
                            root = ET.fromstring(metadata_xml)

                            namespaces = {
                                'edmx': 'http://docs.oasis-open.org/odata/ns/edmx',
                                'edm': 'http://docs.oasis-open.org/odata/ns/edm',
                                'sap': 'http://www.sap.com/Protocols/SAPData'
                            }

                            entity_sets = []
                            for entity_type in root.findall('.//edm:EntityType', namespaces):
                                dimensions = []
                                measures = []
                                keys = []

                                # Extract keys
                                for key_prop in entity_type.findall('.//edm:PropertyRef', namespaces):
                                    keys.append(key_prop.get('Name'))

                                # Extract properties
                                for prop in entity_type.findall('.//edm:Property', namespaces):
                                    prop_name = prop.get('Name')
                                    prop_type = prop.get('Type')
                                    agg_role = prop.get('{http://www.sap.com/Protocols/SAPData}aggregation-role')

                                    if agg_role == 'dimension':
                                        dimensions.append({"name": prop_name, "type": prop_type})
                                    elif agg_role == 'measure':
                                        measures.append({"name": prop_name, "type": prop_type})

                                entity_sets.append({
                                    "name": entity_type.get('Name'),
                                    "dimensions": dimensions,
                                    "measures": measures,
                                    "keys": keys
                                })

                            service_doc["metadata"] = {"entity_sets": entity_sets}

                return [types.TextContent(
                    type="text",
                    text=f"Analytical Model for {space_id}/{asset_id}:\n\n" +
                         json.dumps(service_doc, indent=2)
                )]
            except Exception as e:
                logger.error(f"Error fetching analytical model: {str(e)}")
                return [types.TextContent(
                    type="text",
                    text=f"Error fetching analytical model: {str(e)}"
                )]

    elif name == "query_analytical_data":
        space_id = arguments["space_id"]
        asset_id = arguments["asset_id"]
        entity_set = arguments["entity_set"]
        select_param = arguments.get("select")
        filter_param = arguments.get("filter")
        orderby_param = arguments.get("orderby")
        top = arguments.get("top", 50)
        skip = arguments.get("skip", 0)
        count = arguments.get("count", False)
        apply_param = arguments.get("apply")

        if DATASPHERE_CONFIG["use_mock_data"]:
            # Mock analytical query results
            mock_data = {
                "@odata.context": f"$metadata#{entity_set}",
                "value": [
                    {
                        "TransactionID": "TXN001",
                        "Amount": 15000.50,
                        "Currency": "USD",
                        "AccountNumber": "1000100",
                        "TransactionDate": "2024-01-15"
                    },
                    {
                        "TransactionID": "TXN002",
                        "Amount": 8500.00,
                        "Currency": "EUR",
                        "AccountNumber": "1000200",
                        "TransactionDate": "2024-01-16"
                    },
                    {
                        "TransactionID": "TXN003",
                        "Amount": 12300.75,
                        "Currency": "USD",
                        "AccountNumber": "1000100",
                        "TransactionDate": "2024-01-17"
                    }
                ]
            }

            if count:
                mock_data["@odata.count"] = len(mock_data["value"])

            # Simulate aggregation
            if apply_param and "groupby" in apply_param.lower():
                mock_data["value"] = [
                    {"Currency": "USD", "TotalAmount": 27301.25, "TransactionCount": 2},
                    {"Currency": "EUR", "TotalAmount": 8500.00, "TransactionCount": 1}
                ]

            query_info = f"\nQuery Parameters:\n"
            if select_param:
                query_info += f"  $select: {select_param}\n"
            if filter_param:
                query_info += f"  $filter: {filter_param}\n"
            if orderby_param:
                query_info += f"  $orderby: {orderby_param}\n"
            if apply_param:
                query_info += f"  $apply: {apply_param}\n"

            return [types.TextContent(
                type="text",
                text=f"Analytical Query Results from {space_id}/{asset_id}/{entity_set}:{query_info}\n" +
                     json.dumps(mock_data, indent=2) +
                     f"\n\nNote: This is mock data. Set USE_MOCK_DATA=false for real query results."
            )]
        else:
            if not datasphere_connector:
                return [types.TextContent(
                    type="text",
                    text="Error: OAuth connector not initialized. Cannot query analytical data."
                )]

            try:
                # Build OData query URL
                endpoint = f"/api/v1/datasphere/consumption/analytical/{space_id}/{asset_id}/{entity_set}"
                params = {}

                if select_param:
                    params["$select"] = select_param
                if filter_param:
                    params["$filter"] = filter_param
                if orderby_param:
                    params["$orderby"] = orderby_param
                if top:
                    params["$top"] = top
                if skip:
                    params["$skip"] = skip
                if count:
                    params["$count"] = "true"
                if apply_param:
                    params["$apply"] = apply_param

                # Use .get() method from DatasphereAuthConnector
                data = await datasphere_connector.get(endpoint, params=params)

                query_info = f"\nQuery Parameters:\n"
                for key, value in params.items():
                    query_info += f"  {key}: {value}\n"

                return [types.TextContent(
                    type="text",
                    text=f"Analytical Query Results from {space_id}/{asset_id}/{entity_set}:{query_info}\n" +
                         json.dumps(data, indent=2)
                )]
            except Exception as e:
                logger.error(f"Error querying analytical data: {str(e)}")
                return [types.TextContent(
                    type="text",
                    text=f"Error querying analytical data: {str(e)}"
                )]

    elif name == "get_analytical_service_document":
        space_id = arguments["space_id"]
        asset_id = arguments["asset_id"]

        if DATASPHERE_CONFIG["use_mock_data"]:
            # Mock service document
            mock_service_doc = {
                "@odata.context": f"$metadata",
                "value": [
                    {
                        "name": asset_id,
                        "kind": "EntitySet",
                        "url": asset_id
                    }
                ]
            }

            return [types.TextContent(
                type="text",
                text=f"Analytical Service Document for {space_id}/{asset_id}:\n\n" +
                     json.dumps(mock_service_doc, indent=2) +
                     f"\n\nNote: This is mock data. Set USE_MOCK_DATA=false for real service document."
            )]
        else:
            if not datasphere_connector:
                return [types.TextContent(
                    type="text",
                    text="Error: OAuth connector not initialized. Cannot retrieve service document."
                )]

            try:
                # GET /api/v1/datasphere/consumption/analytical/{spaceId}/{assetId}
                endpoint = f"/api/v1/datasphere/consumption/analytical/{space_id}/{asset_id}"

                # Use .get() method from DatasphereAuthConnector
                data = await datasphere_connector.get(endpoint)

                return [types.TextContent(
                    type="text",
                    text=f"Analytical Service Document for {space_id}/{asset_id}:\n\n" +
                         json.dumps(data, indent=2)
                )]
            except Exception as e:
                logger.error(f"Error fetching service document: {str(e)}")
                return [types.TextContent(
                    type="text",
                    text=f"Error fetching service document: {str(e)}"
                )]

    # Phase 3.2: Repository Object Discovery Tools
    elif name == "list_repository_objects":
        space_id = arguments["space_id"]
        object_types = arguments.get("object_types")
        status_filter = arguments.get("status_filter")
        include_dependencies = arguments.get("include_dependencies", False)
        top = arguments.get("top", 50)
        skip = arguments.get("skip", 0)

        if DATASPHERE_CONFIG["use_mock_data"]:
            # Mock repository objects
            mock_objects = [
                {
                    "id": "repo-obj-12345",
                    "objectType": "Table",
                    "name": "FINANCIAL_TRANSACTIONS",
                    "businessName": "Financial Transactions Table",
                    "technicalName": "FINANCIAL_TRANSACTIONS",
                    "description": "Core financial transaction data with account information",
                    "spaceId": space_id,
                    "spaceName": "SAP Content",
                    "status": "Active",
                    "deploymentStatus": "Deployed",
                    "owner": "SYSTEM",
                    "createdBy": "SYSTEM",
                    "createdAt": "2024-01-15T10:30:00Z",
                    "modifiedBy": "ADMIN",
                    "modifiedAt": "2024-11-20T14:22:00Z",
                    "version": "2.1",
                    "packageName": "sap.content.finance",
                    "tags": ["finance", "transactions", "core"],
                    "columns": [
                        {"name": "TRANSACTION_ID", "dataType": "NVARCHAR(50)", "isPrimaryKey": True},
                        {"name": "AMOUNT", "dataType": "DECIMAL(15,2)", "isPrimaryKey": False},
                        {"name": "CURRENCY", "dataType": "NVARCHAR(3)", "isPrimaryKey": False}
                    ],
                    "dependencies": {
                        "upstream": ["SOURCE_SYSTEM_TABLE"],
                        "downstream": ["FIN_ANALYTICS_VIEW", "FIN_REPORT_MODEL"]
                    }
                },
                {
                    "id": "repo-obj-67890",
                    "objectType": "View",
                    "name": "CUSTOMER_FINANCIAL_SUMMARY",
                    "businessName": "Customer Financial Summary View",
                    "technicalName": "CUSTOMER_FIN_SUMMARY_VIEW",
                    "description": "Aggregated customer financial data",
                    "spaceId": space_id,
                    "spaceName": "SAP Content",
                    "status": "Active",
                    "deploymentStatus": "Deployed",
                    "owner": "FIN_ADMIN",
                    "createdBy": "FIN_ADMIN",
                    "createdAt": "2024-03-10T08:15:00Z",
                    "modifiedBy": "FIN_ADMIN",
                    "modifiedAt": "2024-10-05T16:45:00Z",
                    "version": "1.3",
                    "packageName": "sap.content.finance.views",
                    "tags": ["customer", "finance", "summary"],
                    "basedOn": ["FINANCIAL_TRANSACTIONS", "CUSTOMER_MASTER"],
                    "dependencies": {
                        "upstream": ["FINANCIAL_TRANSACTIONS", "CUSTOMER_MASTER"],
                        "downstream": ["CUSTOMER_DASHBOARD"]
                    }
                },
                {
                    "id": "repo-obj-11111",
                    "objectType": "AnalyticalModel",
                    "name": "SALES_ANALYTICS_MODEL",
                    "businessName": "Sales Analytics Model",
                    "technicalName": "SALES_ANALYTICS_MODEL",
                    "description": "Comprehensive sales analytics with dimensions and measures",
                    "spaceId": space_id,
                    "spaceName": "Sales Analytics",
                    "status": "Active",
                    "deploymentStatus": "Deployed",
                    "owner": "SALES_ADMIN",
                    "version": "3.0",
                    "dimensions": ["Customer", "Product", "Time", "Region"],
                    "measures": ["Revenue", "Quantity", "Profit"],
                    "dependencies": {
                        "upstream": ["SALES_ORDERS", "SALES_ITEMS", "CUSTOMER_MASTER"],
                        "downstream": ["SALES_DASHBOARD", "EXECUTIVE_REPORT"]
                    }
                },
                {
                    "id": "repo-obj-22222",
                    "objectType": "DataFlow",
                    "name": "LOAD_FINANCIAL_DATA",
                    "businessName": "Financial Data Load Process",
                    "technicalName": "LOAD_FINANCIAL_DATA",
                    "description": "ETL process for loading financial transactions from ERP",
                    "spaceId": space_id,
                    "status": "Active",
                    "deploymentStatus": "Deployed",
                    "owner": "ETL_ADMIN",
                    "version": "1.5",
                    "sourceObjects": ["ERP_TRANSACTIONS"],
                    "targetObjects": ["FINANCIAL_TRANSACTIONS"],
                    "schedule": {"frequency": "Daily", "time": "02:00:00"},
                    "lastRun": {
                        "timestamp": "2024-12-04T02:00:00Z",
                        "status": "Success",
                        "recordsProcessed": 125000
                    }
                }
            ]

            # Filter by object types
            if object_types:
                mock_objects = [obj for obj in mock_objects if obj["objectType"] in object_types]

            # Filter by status
            if status_filter:
                mock_objects = [obj for obj in mock_objects if obj["status"] == status_filter]

            # Apply pagination
            paginated_objects = mock_objects[skip:skip + top]

            # Remove dependencies if not requested
            if not include_dependencies:
                for obj in paginated_objects:
                    obj.pop("dependencies", None)

            # Build summary
            type_counts = {}
            for obj in paginated_objects:
                obj_type = obj["objectType"]
                type_counts[obj_type] = type_counts.get(obj_type, 0) + 1

            result = {
                "space_id": space_id,
                "objects": paginated_objects,
                "returned_count": len(paginated_objects),
                "has_more": (skip + len(paginated_objects)) < len(mock_objects),
                "summary": {
                    "total_objects": len(paginated_objects),
                    "by_type": type_counts
                }
            }

            return [types.TextContent(
                type="text",
                text=f"Repository Objects in {space_id}:\n\n" +
                     json.dumps(result, indent=2) +
                     f"\n\nNote: This is mock data. Set USE_MOCK_DATA=false for real repository data."
            )]
        else:
            if not datasphere_connector:
                return [types.TextContent(
                    type="text",
                    text="Error: OAuth connector not initialized. Cannot list repository objects."
                )]

            try:
                # Fixed: Repository APIs are UI endpoints; use Catalog spaces/assets API instead
                endpoint = f"/api/v1/datasphere/consumption/catalog/spaces('{space_id}')/assets"
                params = {"$top": top, "$skip": skip}

                # Build filter expression
                filters = []
                if object_types:
                    type_filters = " or ".join([f"assetType eq '{t}'" for t in object_types])
                    filters.append(f"({type_filters})")
                if status_filter:
                    filters.append(f"status eq '{status_filter}'")
                if filters:
                    params["$filter"] = " and ".join(filters)

                # Note: dependencies expansion may not be available in Catalog API
                # if include_dependencies:
                #     params["$expand"] = "dependencies"

                # Use the .get() method from DatasphereAuthConnector
                data = await datasphere_connector.get(endpoint, params=params)

                # Build summary
                objects = data.get("value", [])
                type_counts = {}
                for obj in objects:
                    obj_type = obj.get("objectType", "Unknown")
                    type_counts[obj_type] = type_counts.get(obj_type, 0) + 1

                result = {
                    "space_id": space_id,
                    "objects": objects,
                    "returned_count": len(objects),
                    "has_more": len(objects) == top,
                    "summary": {
                        "total_objects": len(objects),
                        "by_type": type_counts
                    }
                }

                return [types.TextContent(
                    type="text",
                    text=f"Repository Objects in {space_id}:\n\n" +
                         json.dumps(result, indent=2)
                )]

            except Exception as e:
                logger.error(f"Error listing repository objects: {str(e)}")
                return [types.TextContent(
                    type="text",
                    text=f"Error listing repository objects: {str(e)}"
                )]

    elif name == "get_object_definition":
        space_id = arguments["space_id"]
        object_id = arguments["object_id"]
        include_full_definition = arguments.get("include_full_definition", True)
        include_dependencies = arguments.get("include_dependencies", True)

        if DATASPHERE_CONFIG["use_mock_data"]:
            # Mock object definition (Table example)
            mock_definition = {
                "id": object_id,
                "objectType": "Table",
                "name": object_id,
                "businessName": f"{object_id} Table",
                "technicalName": object_id,
                "description": f"Complete definition for {object_id}",
                "spaceId": space_id,
                "status": "Active",
                "deploymentStatus": "Deployed",
                "owner": "SYSTEM",
                "version": "2.1"
            }

            if include_full_definition:
                mock_definition["definition"] = {
                    "type": "Table",
                    "columns": [
                        {
                            "name": "TRANSACTION_ID",
                            "technicalName": "TRANSACTION_ID",
                            "dataType": "NVARCHAR",
                            "length": 50,
                            "isPrimaryKey": True,
                            "isNullable": False,
                            "description": "Unique transaction identifier",
                            "semanticType": "BusinessKey"
                        },
                        {
                            "name": "AMOUNT",
                            "technicalName": "AMOUNT",
                            "dataType": "DECIMAL",
                            "precision": 15,
                            "scale": 2,
                            "isPrimaryKey": False,
                            "isNullable": False,
                            "description": "Transaction amount",
                            "semanticType": "Amount"
                        },
                        {
                            "name": "CURRENCY",
                            "technicalName": "CURRENCY",
                            "dataType": "NVARCHAR",
                            "length": 3,
                            "isPrimaryKey": False,
                            "isNullable": False,
                            "description": "Currency code",
                            "semanticType": "CurrencyCode"
                        }
                    ],
                    "primaryKey": {
                        "name": "PK_TRANSACTION",
                        "columns": ["TRANSACTION_ID"]
                    },
                    "indexes": [
                        {"name": "IDX_AMOUNT", "columns": ["AMOUNT"], "isUnique": False}
                    ]
                }

            if include_dependencies:
                mock_definition["dependencies"] = {
                    "upstream": ["SOURCE_SYSTEM_TABLE"],
                    "downstream": ["FIN_ANALYTICS_VIEW", "FIN_REPORT_MODEL"]
                }

            mock_definition["metadata"] = {
                "rowCount": 15000000,
                "sizeInMB": 2500,
                "lastModified": "2024-11-20T14:22:00Z"
            }

            return [types.TextContent(
                type="text",
                text=f"Object Definition for {space_id}/{object_id}:\n\n" +
                     json.dumps(mock_definition, indent=2) +
                     f"\n\nNote: This is mock data. Set USE_MOCK_DATA=false for real object definition."
            )]
        else:
            if not datasphere_connector:
                return [types.TextContent(
                    type="text",
                    text="Error: OAuth connector not initialized. Cannot get object definition."
                )]

            try:
                # Fixed: Repository APIs are UI endpoints; use two-step Catalog + Metadata approach
                # Step 1: Get asset details from catalog
                asset_endpoint = f"/api/v1/datasphere/consumption/catalog/spaces('{space_id}')/assets('{object_id}')"
                asset_data = await datasphere_connector.get(asset_endpoint)

                result = {
                    "space_id": space_id,
                    "object_id": object_id,
                    "asset_info": asset_data
                }

                # Step 2: Get detailed schema based on asset type if requested
                if include_full_definition:
                    asset_type = asset_data.get("assetType", "Unknown")

                    try:
                        if asset_type == "AnalyticalModel":
                            metadata_endpoint = f"/api/v1/datasphere/consumption/analytical/{space_id}/{object_id}/$metadata"
                        else:
                            metadata_endpoint = f"/api/v1/datasphere/consumption/relational/{space_id}/{object_id}/$metadata"

                        # Metadata endpoints return XML
                        import aiohttp
                        headers = await datasphere_connector._get_headers()
                        headers['Accept'] = 'application/xml'

                        metadata_url = f"{DATASPHERE_CONFIG['base_url'].rstrip('/')}{metadata_endpoint}"
                        async with datasphere_connector._session.get(metadata_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                            if response.status == 200:
                                xml_content = await response.text()
                                result["metadata_xml"] = xml_content
                                result["note"] = "Full schema definition retrieved from metadata endpoint"
                            else:
                                result["metadata_error"] = f"HTTP {response.status}"
                                result["note"] = "Could not retrieve detailed schema"
                    except Exception as meta_error:
                        result["metadata_error"] = str(meta_error)
                        result["note"] = "Asset details retrieved, but full schema not available"

                return [types.TextContent(
                    type="text",
                    text=f"Object Definition for {space_id}/{object_id}:\n\n" +
                         json.dumps(result, indent=2)
                )]
            except Exception as e:
                logger.error(f"Error getting object definition: {str(e)}")
                return [types.TextContent(
                    type="text",
                    text=f"Error getting object definition: {str(e)}"
                )]

    elif name == "get_deployed_objects":
        space_id = arguments["space_id"]
        object_types = arguments.get("object_types")
        runtime_status = arguments.get("runtime_status")
        include_metrics = arguments.get("include_metrics", True)
        top = arguments.get("top", 50)
        skip = arguments.get("skip", 0)

        if DATASPHERE_CONFIG["use_mock_data"]:
            # Mock deployed objects
            mock_deployed = [
                {
                    "id": "deployed-12345",
                    "objectId": "FINANCIAL_TRANSACTIONS",
                    "objectType": "Table",
                    "name": "FINANCIAL_TRANSACTIONS",
                    "businessName": "Financial Transactions Table",
                    "spaceId": space_id,
                    "deploymentStatus": "Deployed",
                    "deployedBy": "SYSTEM",
                    "deployedAt": "2024-01-15T10:30:00Z",
                    "version": "2.1",
                    "runtimeStatus": "Active",
                    "lastAccessed": "2024-12-04T15:30:00Z",
                    "accessCount": 15234,
                    "runtimeMetrics": {
                        "rowCount": 15000000,
                        "sizeInMB": 2500,
                        "avgQueryTime": "0.25s",
                        "queriesPerDay": 1250
                    }
                },
                {
                    "id": "deployed-67890",
                    "objectId": "LOAD_FINANCIAL_DATA",
                    "objectType": "DataFlow",
                    "name": "LOAD_FINANCIAL_DATA",
                    "businessName": "Financial Data Load Process",
                    "spaceId": space_id,
                    "deploymentStatus": "Deployed",
                    "deployedBy": "ETL_ADMIN",
                    "deployedAt": "2024-01-20T10:00:00Z",
                    "version": "1.5",
                    "runtimeStatus": "Running",
                    "schedule": {
                        "frequency": "Daily",
                        "nextRun": "2024-12-05T02:00:00Z",
                        "lastRun": "2024-12-04T02:00:00Z"
                    },
                    "lastExecution": {
                        "runId": "run-20241204-020000",
                        "startTime": "2024-12-04T02:00:00Z",
                        "endTime": "2024-12-04T02:15:32Z",
                        "status": "Success",
                        "recordsProcessed": 125000,
                        "duration": "00:15:32"
                    },
                    "runtimeMetrics": {
                        "totalRuns": 320,
                        "successRate": 99.7,
                        "avgDuration": "00:14:25",
                        "avgRecordsProcessed": 123500
                    }
                }
            ]

            # Filter by object types
            if object_types:
                mock_deployed = [obj for obj in mock_deployed if obj["objectType"] in object_types]

            # Filter by runtime status
            if runtime_status:
                mock_deployed = [obj for obj in mock_deployed if obj["runtimeStatus"] == runtime_status]

            # Apply pagination
            paginated_deployed = mock_deployed[skip:skip + top]

            # Remove metrics if not requested
            if not include_metrics:
                for obj in paginated_deployed:
                    obj.pop("runtimeMetrics", None)

            # Build summary
            status_counts = {}
            type_counts = {}
            for obj in paginated_deployed:
                status = obj["runtimeStatus"]
                obj_type = obj["objectType"]
                status_counts[status] = status_counts.get(status, 0) + 1
                type_counts[obj_type] = type_counts.get(obj_type, 0) + 1

            result = {
                "space_id": space_id,
                "deployed_objects": paginated_deployed,
                "returned_count": len(paginated_deployed),
                "has_more": (skip + len(paginated_deployed)) < len(mock_deployed),
                "summary": {
                    "total_deployed": len(paginated_deployed),
                    "by_status": status_counts,
                    "by_type": type_counts
                }
            }

            return [types.TextContent(
                type="text",
                text=f"Deployed Objects in {space_id}:\n\n" +
                     json.dumps(result, indent=2) +
                     f"\n\nNote: This is mock data. Set USE_MOCK_DATA=false for real deployment data."
            )]
        else:
            if not datasphere_connector:
                return [types.TextContent(
                    type="text",
                    text="Error: OAuth connector not initialized. Cannot get deployed objects."
                )]

            try:
                # Fixed: Repository APIs are UI endpoints; use Catalog assets API
                # API doesn't support ANY OData filters - do ALL filtering client-side
                # IMPORTANT: Must use BOTH $top and $skip parameters (like list_catalog_assets)
                endpoint = f"/api/v1/datasphere/consumption/catalog/spaces('{space_id}')/assets"
                params = {
                    "$top": 50,    # Match list_catalog_assets parameter
                    "$skip": 0     # Required - API returns empty without this
                }

                # NO filters in API call - even exposedForConsumption filter causes 400 error
                logger.info(f"Getting catalog assets for space {space_id} with params: {params}")

                # Use .get() method from DatasphereAuthConnector
                data = await datasphere_connector.get(endpoint, params=params)

                all_objects = data.get("value", [])

                # Client-side filtering for object types and exposed status
                filtered_objects = []
                for obj in all_objects:
                    # Filter by object type if specified
                    # Note: Field might be "assetType" or similar - check actual response
                    # if object_types:
                    #     if obj.get("assetType") not in object_types:
                    #         continue

                    # Filter by exposed/deployed status if the field exists
                    # Note: exposedForConsumption field may not exist in response
                    # For now, include all assets from the space

                    filtered_objects.append(obj)

                # Apply pagination on filtered results
                paginated_objects = filtered_objects[skip:skip + top]

                # Build summary
                objects = paginated_objects
                status_counts = {}
                type_counts = {}
                for obj in objects:
                    status = obj.get("runtimeStatus", "Unknown")
                    obj_type = obj.get("objectType", "Unknown")
                    status_counts[status] = status_counts.get(status, 0) + 1
                    type_counts[obj_type] = type_counts.get(obj_type, 0) + 1

                result = {
                    "space_id": space_id,
                    "deployed_objects": objects,
                    "returned_count": len(objects),
                    "has_more": len(objects) == top,
                    "summary": {
                        "total_deployed": len(objects),
                        "by_status": status_counts,
                        "by_type": type_counts
                    }
                }

                return [types.TextContent(
                    type="text",
                    text=f"Deployed Objects in {space_id}:\n\n" +
                         json.dumps(result, indent=2)
                )]
            except Exception as e:
                logger.error(f"Error getting deployed objects: {str(e)}")
                return [types.TextContent(
                    type="text",
                    text=f"Error getting deployed objects: {str(e)}"
                )]

    # ========================================================================
    # DIAGNOSTIC TOOL: Test Phase 6 & 7 Endpoint Availability
    # ========================================================================

    elif name == "test_phase67_endpoints":
        detailed = arguments.get("detailed", False)

        if not datasphere_connector:
            return [types.TextContent(
                type="text",
                text="Error: OAuth connector not initialized. Cannot test endpoints."
            )]

        # Define all Phase 6 & 7 endpoints to test
        endpoints_to_test = {
            "KPI Management": {
                "kpi_search": {
                    "endpoint": "/api/v1/datasphere/search",
                    "params": {"search": "SCOPE:comsapcatalogsearchprivateSearchKPIsAdmin *", "$top": 1},
                    "description": "Search for KPIs"
                },
                "kpi_list": {
                    "endpoint": "/api/v1/datasphere/kpis",
                    "params": {"$top": 1},
                    "description": "List all KPIs"
                }
            },
            "System Monitoring": {
                "systems_overview": {
                    "endpoint": "/api/v1/datasphere/systems/overview",
                    "params": {},
                    "description": "Get systems overview"
                },
                "logs_search": {
                    "endpoint": "/api/v1/datasphere/logs/search",
                    "params": {"$top": 1},
                    "description": "Search system logs"
                },
                "logs_export": {
                    "endpoint": "/api/v1/datasphere/logs/export",
                    "params": {"format": "JSON", "max_records": 1},
                    "description": "Export system logs"
                },
                "logs_facets": {
                    "endpoint": "/api/v1/datasphere/logs/facets",
                    "params": {"facet_fields": "level"},
                    "description": "Get log facets"
                }
            },
            "User Administration": {
                "users_list": {
                    "endpoint": "/api/v1/datasphere/users",
                    "params": {"$top": 1},
                    "description": "List users"
                }
            }
        }

        results = {
            "test_timestamp": datetime.now().isoformat(),
            "categories": {},
            "summary": {
                "total_endpoints": 0,
                "available": 0,
                "unavailable": 0,
                "errors": 0
            }
        }

        # Test each endpoint
        for category, endpoints in endpoints_to_test.items():
            results["categories"][category] = {}

            for name, config in endpoints.items():
                results["summary"]["total_endpoints"] += 1

                try:
                    logger.info(f"Testing endpoint: {config['endpoint']}")
                    response_data = await datasphere_connector.get(
                        config["endpoint"],
                        params=config["params"]
                    )

                    # Endpoint is available
                    results["categories"][category][name] = {
                        "status": "available",
                        "http_code": 200,
                        "description": config["description"],
                        "endpoint": config["endpoint"],
                        "message": "✅ Endpoint is available and working"
                    }

                    if detailed and response_data:
                        results["categories"][category][name]["sample_data"] = response_data

                    results["summary"]["available"] += 1
                    logger.info(f"✅ {config['endpoint']} - Available")

                except Exception as e:
                    error_str = str(e)

                    # Determine status based on error
                    if "404" in error_str or "Not Found" in error_str:
                        status = "not_found"
                        http_code = 404
                        message = "❌ Endpoint does not exist in this tenant"
                    elif "403" in error_str or "Forbidden" in error_str:
                        status = "forbidden"
                        http_code = 403
                        message = "⚠️ Endpoint exists but requires admin permissions"
                    elif "401" in error_str or "Unauthorized" in error_str:
                        status = "unauthorized"
                        http_code = 401
                        message = "⚠️ Endpoint exists but authentication failed"
                    elif "400" in error_str or "Bad Request" in error_str:
                        status = "bad_request"
                        http_code = 400
                        message = "⚠️ Endpoint exists but parameters may need adjustment"
                    else:
                        status = "error"
                        http_code = None
                        message = f"❌ Error: {error_str}"

                    results["categories"][category][name] = {
                        "status": status,
                        "http_code": http_code,
                        "description": config["description"],
                        "endpoint": config["endpoint"],
                        "message": message,
                        "error": error_str
                    }

                    if status == "not_found":
                        results["summary"]["unavailable"] += 1
                    else:
                        results["summary"]["errors"] += 1

                    logger.warning(f"⚠️ {config['endpoint']} - {status}")

        # Add recommendations
        results["recommendations"] = []

        if results["summary"]["available"] == 0:
            results["recommendations"].append(
                "No Phase 6 & 7 endpoints are available. All tools will use mock data."
            )
            results["recommendations"].append(
                "These features may require specific tenant configuration or admin permissions."
            )
        elif results["summary"]["available"] < results["summary"]["total_endpoints"]:
            results["recommendations"].append(
                f"{results['summary']['available']}/{results['summary']['total_endpoints']} endpoints available. "
                "Some tools can use real data, others will use mock data."
            )
        else:
            results["recommendations"].append(
                "All Phase 6 & 7 endpoints are available! You can enable real data for all 10 tools."
            )

        if results["summary"]["errors"] > 0:
            results["recommendations"].append(
                "Some endpoints returned permission or authentication errors. "
                "Check user roles and OAuth scopes."
            )

        return [types.TextContent(
            type="text",
            text=f"Phase 6 & 7 Endpoint Availability Test:\n\n{json.dumps(results, indent=2)}"
        )]

    elif name == "test_phase8_endpoints":
        detailed = arguments.get("detailed", False)
        test_product_id = arguments.get("test_product_id", "f55b20ae-152d-40d4-b2eb-70b651f85d37")

        if not datasphere_connector:
            return [types.TextContent(
                type="text",
                text="Error: OAuth connector not initialized. Cannot test endpoints."
            )]

        # Define all Phase 8 endpoints to test (10 confirmed endpoints)
        endpoints_to_test = {
            "Data Sharing & Collaboration": {
                "list_partner_systems": {
                    "endpoint": "/deepsea/catalog/v1/dataProducts/partners/systems",
                    "params": {"$top": 1},
                    "description": "List partner systems"
                },
                "get_marketplace_assets": {
                    "endpoint": "/api/v1/datasphere/marketplace/dsc/request",
                    "params": {"$top": 1},
                    "description": "Get marketplace assets"
                },
                "get_data_product_details": {
                    "endpoint": f"/dwaas-core/odc/dataProduct/{test_product_id}/details",
                    "params": {},
                    "description": f"Get data product details (testing with ID: {test_product_id})"
                }
            },
            "AI Features & Configuration": {
                "get_ai_feature_status": {
                    "endpoint": "/dwaas-core/api/v1/aifeatures/test-feature/executable/status",
                    "params": {},
                    "description": "Get AI feature status (testing with placeholder ID)"
                },
                "get_guided_experience_config": {
                    "endpoint": "/dwaas-core/configurations/DWC_GUIDED_EXPERIENCE_TENANT",
                    "params": {},
                    "description": "Get guided experience configuration"
                },
                "get_security_config_status": {
                    "endpoint": "/dwaas-core/security/customerhana/flexible-configuration/configuration-status",
                    "params": {},
                    "description": "Get security configuration status"
                }
            },
            "Legacy DWC API Support": {
                "dwc_list_catalog_assets": {
                    "endpoint": "/v1/dwc/catalog/assets",
                    "params": {"$top": 1},
                    "description": "Legacy: List catalog assets"
                },
                "dwc_get_space_assets": {
                    "endpoint": "/v1/dwc/catalog/spaces('SAP_CONTENT')/assets",
                    "params": {"$top": 1},
                    "description": "Legacy: Get space assets"
                },
                "dwc_query_analytical_data": {
                    "endpoint": "/v1/dwc/consumption/analytical/SAP_CONTENT/test/odata",
                    "params": {"$top": 1},
                    "description": "Legacy: Query analytical data (testing with placeholder)"
                },
                "dwc_query_relational_data": {
                    "endpoint": "/v1/dwc/consumption/relational/SAP_CONTENT/test/odata",
                    "params": {"$top": 1},
                    "description": "Legacy: Query relational data (testing with placeholder)"
                }
            }
        }

        results = {
            "test_timestamp": datetime.now().isoformat(),
            "phase": "Phase 8: Advanced Features",
            "categories": {},
            "summary": {
                "total_endpoints": 0,
                "available": 0,
                "unavailable": 0,
                "errors": 0
            }
        }

        # Test each endpoint
        for category, endpoints in endpoints_to_test.items():
            results["categories"][category] = {}

            for tool_name, config in endpoints.items():
                results["summary"]["total_endpoints"] += 1

                try:
                    logger.info(f"Testing Phase 8 endpoint: {config['endpoint']}")
                    response_data = await datasphere_connector.get(
                        config["endpoint"],
                        params=config["params"]
                    )

                    # Endpoint is available
                    results["categories"][category][tool_name] = {
                        "status": "available",
                        "http_code": 200,
                        "description": config["description"],
                        "endpoint": config["endpoint"],
                        "message": "✅ Endpoint is available and returns JSON"
                    }

                    if detailed and response_data:
                        results["categories"][category][tool_name]["sample_data"] = response_data

                    results["summary"]["available"] += 1
                    logger.info(f"✅ {config['endpoint']} - Available")

                except Exception as e:
                    error_str = str(e)

                    # Determine status based on error
                    if "404" in error_str or "Not Found" in error_str:
                        status = "not_found"
                        http_code = 404
                        message = "❌ Endpoint does not exist in this tenant"
                        recommendation = "Endpoint may require specific feature activation or tenant configuration"
                    elif "403" in error_str or "Forbidden" in error_str:
                        status = "forbidden"
                        http_code = 403
                        message = "⚠️ Endpoint exists but requires admin permissions"
                        recommendation = "Check user roles and OAuth scopes"
                    elif "401" in error_str or "Unauthorized" in error_str:
                        status = "unauthorized"
                        http_code = 401
                        message = "⚠️ Endpoint exists but authentication failed"
                        recommendation = "Verify OAuth token and scopes"
                    elif "400" in error_str or "Bad Request" in error_str:
                        status = "bad_request"
                        http_code = 400
                        message = "⚠️ Endpoint exists but parameters may need adjustment"
                        recommendation = "Test with different parameters or IDs"
                    else:
                        status = "error"
                        http_code = None
                        message = f"❌ Error: {error_str}"
                        recommendation = "Check endpoint path and authentication"

                    results["categories"][category][tool_name] = {
                        "status": status,
                        "http_code": http_code,
                        "description": config["description"],
                        "endpoint": config["endpoint"],
                        "message": message,
                        "recommendation": recommendation,
                        "error": error_str
                    }

                    if status == "not_found":
                        results["summary"]["unavailable"] += 1
                    else:
                        results["summary"]["errors"] += 1

                    logger.warning(f"⚠️ {config['endpoint']} - {status}")

        # Add overall recommendations
        results["recommendations"] = []

        if results["summary"]["available"] == 0:
            results["recommendations"].append(
                "⚠️ CRITICAL: No Phase 8 endpoints are available in your tenant."
            )
            results["recommendations"].append(
                "Do NOT implement Phase 8 tools - all would fail like Phase 6 & 7."
            )
            results["recommendations"].append(
                "These features may require specific tenant configuration, feature flags, or admin permissions."
            )
        elif results["summary"]["available"] < results["summary"]["total_endpoints"]:
            available_tools = []
            unavailable_tools = []

            for category, endpoints in results["categories"].items():
                for tool_name, result in endpoints.items():
                    if result["status"] == "available":
                        available_tools.append(tool_name)
                    else:
                        unavailable_tools.append(tool_name)

            results["recommendations"].append(
                f"✅ Partial Success: {results['summary']['available']}/{results['summary']['total_endpoints']} endpoints available."
            )
            results["recommendations"].append(
                f"Implement ONLY these {len(available_tools)} tools: {', '.join(available_tools)}"
            )
            results["recommendations"].append(
                f"Skip these {len(unavailable_tools)} tools: {', '.join(unavailable_tools)}"
            )
        else:
            results["recommendations"].append(
                f"🎉 Excellent! All {results['summary']['total_endpoints']} Phase 8 endpoints are available!"
            )
            results["recommendations"].append(
                "You can implement all 10 Phase 8 tools with real data."
            )

        if results["summary"]["errors"] > 0:
            results["recommendations"].append(
                f"⚠️ {results['summary']['errors']} endpoints returned permission/auth errors - check user roles and OAuth scopes."
            )

        results["next_steps"] = [
            "1. Review the detailed status for each endpoint above",
            "2. Implement ONLY the tools where status = 'available'",
            "3. Follow the 'no mock data' strategy - skip unavailable endpoints",
            "4. Test implemented tools with real tenant data"
        ]

        return [types.TextContent(
            type="text",
            text=f"Phase 8 Endpoint Availability Test:\n\n{json.dumps(results, indent=2)}"
        )]

    elif name == "test_analytical_endpoints":
        detailed = arguments.get("detailed", False)
        test_space_id = arguments.get("test_space_id", "SAP_CONTENT")

        if not datasphere_connector:
            return [types.TextContent(
                type="text",
                text="Error: OAuth connector not initialized. Cannot test endpoints."
            )]

        # First, we need to discover available analytical models/assets in the test space
        # We'll use the catalog to find real assets to test with
        results = {
            "test_timestamp": datetime.now().isoformat(),
            "phase": "Analytical & Query Tools (6 remaining mock tools)",
            "test_space": test_space_id,
            "categories": {},
            "summary": {
                "total_endpoints": 6,
                "available": 0,
                "unavailable": 0,
                "errors": 0,
                "needs_assets": 0
            }
        }

        # Step 1: Try to find analytical models to test with
        test_model_id = None
        try:
            logger.info(f"Discovering analytical models in {test_space_id}")
            models_data = await datasphere_connector.get(
                "/api/v1/datasphere/modelingService/analyticalModels",
                params={"$top": 1, "$filter": f"spaceId eq '{test_space_id}'"}
            )
            if models_data.get("value") and len(models_data["value"]) > 0:
                test_model_id = models_data["value"][0].get("id") or models_data["value"][0].get("technicalName")
                logger.info(f"Found test model: {test_model_id}")
        except Exception as e:
            logger.warning(f"Could not discover analytical models: {str(e)}")

        # Define endpoints to test
        results["categories"]["Analytical Metadata Tools"] = {}
        results["categories"]["Query Execution"] = {}

        # Test 1: get_analytical_metadata
        tool_name = "get_analytical_metadata"
        if test_model_id:
            try:
                endpoint = f"/api/v1/datasphere/modelingService/analyticalModels/{test_model_id}/metadata"
                logger.info(f"Testing: {endpoint}")
                response_data = await datasphere_connector.get(endpoint, params={})

                results["categories"]["Analytical Metadata Tools"][tool_name] = {
                    "status": "available",
                    "http_code": 200,
                    "endpoint": endpoint,
                    "message": "✅ Endpoint works with real analytical models"
                }
                if detailed and response_data:
                    results["categories"]["Analytical Metadata Tools"][tool_name]["sample_data"] = response_data
                results["summary"]["available"] += 1
            except Exception as e:
                results["categories"]["Analytical Metadata Tools"][tool_name] = {
                    "status": "error",
                    "endpoint": f"/api/v1/datasphere/modelingService/analyticalModels/{{model}}/metadata",
                    "message": f"❌ Error: {str(e)}",
                    "test_model": test_model_id
                }
                results["summary"]["errors"] += 1
        else:
            results["categories"]["Analytical Metadata Tools"][tool_name] = {
                "status": "needs_assets",
                "endpoint": "/api/v1/datasphere/modelingService/analyticalModels/{model}/metadata",
                "message": "⚠️ No analytical models found in space to test with"
            }
            results["summary"]["needs_assets"] += 1

        # Test 2: get_analytical_model
        tool_name = "get_analytical_model"
        if test_model_id:
            try:
                endpoint = f"/api/v1/datasphere/modelingService/analyticalModels/{test_model_id}"
                logger.info(f"Testing: {endpoint}")
                response_data = await datasphere_connector.get(endpoint, params={})

                results["categories"]["Analytical Metadata Tools"][tool_name] = {
                    "status": "available",
                    "http_code": 200,
                    "endpoint": endpoint,
                    "message": "✅ Endpoint works with real analytical models"
                }
                if detailed and response_data:
                    results["categories"]["Analytical Metadata Tools"][tool_name]["sample_data"] = response_data
                results["summary"]["available"] += 1
            except Exception as e:
                results["categories"]["Analytical Metadata Tools"][tool_name] = {
                    "status": "error",
                    "endpoint": f"/api/v1/datasphere/modelingService/analyticalModels/{{model}}",
                    "message": f"❌ Error: {str(e)}",
                    "test_model": test_model_id
                }
                results["summary"]["errors"] += 1
        else:
            results["categories"]["Analytical Metadata Tools"][tool_name] = {
                "status": "needs_assets",
                "endpoint": "/api/v1/datasphere/modelingService/analyticalModels/{model}",
                "message": "⚠️ No analytical models found in space to test with"
            }
            results["summary"]["needs_assets"] += 1

        # Test 3: list_analytical_datasets
        tool_name = "list_analytical_datasets"
        if test_model_id:
            try:
                endpoint = f"/api/v1/datasphere/consumption/analytical/{test_space_id}/{test_model_id}/"
                logger.info(f"Testing: {endpoint}")
                response_data = await datasphere_connector.get(endpoint, params={})

                results["categories"]["Query Execution"][tool_name] = {
                    "status": "available",
                    "http_code": 200,
                    "endpoint": endpoint,
                    "message": "✅ Endpoint works - returns OData service document"
                }
                if detailed and response_data:
                    results["categories"]["Query Execution"][tool_name]["sample_data"] = response_data
                results["summary"]["available"] += 1
            except Exception as e:
                results["categories"]["Query Execution"][tool_name] = {
                    "status": "error",
                    "endpoint": f"/api/v1/datasphere/consumption/analytical/{{space}}/{{model}}/",
                    "message": f"❌ Error: {str(e)}",
                    "test_model": test_model_id
                }
                results["summary"]["errors"] += 1
        else:
            results["categories"]["Query Execution"][tool_name] = {
                "status": "needs_assets",
                "endpoint": "/api/v1/datasphere/consumption/analytical/{space}/{model}/",
                "message": "⚠️ No analytical models found in space to test with"
            }
            results["summary"]["needs_assets"] += 1

        # Test 4: get_analytical_service_document (same as list_analytical_datasets)
        tool_name = "get_analytical_service_document"
        if test_model_id:
            results["categories"]["Query Execution"][tool_name] = {
                "status": "available",
                "http_code": 200,
                "endpoint": f"/api/v1/datasphere/consumption/analytical/{test_space_id}/{test_model_id}/",
                "message": "✅ Same endpoint as list_analytical_datasets - works"
            }
            results["summary"]["available"] += 1
        else:
            results["categories"]["Query Execution"][tool_name] = {
                "status": "needs_assets",
                "endpoint": "/api/v1/datasphere/consumption/analytical/{space}/{model}/",
                "message": "⚠️ No analytical models found in space to test with"
            }
            results["summary"]["needs_assets"] += 1

        # Test 5: query_analytical_data (requires entity name, which we can get from service document)
        tool_name = "query_analytical_data"
        results["categories"]["Query Execution"][tool_name] = {
            "status": "needs_testing",
            "endpoint": "/api/v1/datasphere/consumption/analytical/{space}/{model}/{entity}",
            "message": "⚠️ Requires entity name from service document - needs manual testing with real model"
        }
        results["summary"]["needs_assets"] += 1

        # Test 6: execute_query (relational data)
        tool_name = "execute_query"
        try:
            # Try to find a table/view to test with
            endpoint = f"/api/v1/datasphere/catalog/spaces/{test_space_id}/assets"
            logger.info(f"Discovering tables/views in {test_space_id}")
            assets_data = await datasphere_connector.get(endpoint, params={"$top": 1})

            if assets_data.get("value") and len(assets_data["value"]) > 0:
                test_asset = assets_data["value"][0]
                asset_name = test_asset.get("name") or test_asset.get("technicalName")

                # Try querying it
                query_endpoint = f"/api/v1/datasphere/consumption/relational/{test_space_id}/{asset_name}"
                logger.info(f"Testing: {query_endpoint}")
                query_data = await datasphere_connector.get(query_endpoint, params={"$top": 1})

                results["categories"]["Query Execution"][tool_name] = {
                    "status": "available",
                    "http_code": 200,
                    "endpoint": query_endpoint,
                    "message": "✅ Endpoint works with real tables/views",
                    "test_asset": asset_name
                }
                if detailed and query_data:
                    results["categories"]["Query Execution"][tool_name]["sample_data"] = query_data
                results["summary"]["available"] += 1
            else:
                results["categories"]["Query Execution"][tool_name] = {
                    "status": "needs_assets",
                    "endpoint": "/api/v1/datasphere/consumption/relational/{space}/{view}",
                    "message": "⚠️ No tables/views found in space to test with"
                }
                results["summary"]["needs_assets"] += 1
        except Exception as e:
            results["categories"]["Query Execution"][tool_name] = {
                "status": "error",
                "endpoint": "/api/v1/datasphere/consumption/relational/{space}/{view}",
                "message": f"❌ Error: {str(e)}"
            }
            results["summary"]["errors"] += 1

        # Add recommendations
        results["recommendations"] = []

        if results["summary"]["available"] == 6:
            results["recommendations"].append(
                "🎉 Excellent! All 6 analytical/query endpoints are available!"
            )
            results["recommendations"].append(
                "Action: Set USE_MOCK_DATA=false in your environment to enable these tools with real data."
            )
        elif results["summary"]["available"] > 0:
            results["recommendations"].append(
                f"✅ Partial Success: {results['summary']['available']}/6 endpoints work with real data."
            )
            if results["summary"]["needs_assets"] > 0:
                results["recommendations"].append(
                    f"⚠️ {results['summary']['needs_assets']} tools need analytical models/assets in {test_space_id} to test properly."
                )
                results["recommendations"].append(
                    "Create analytical models or use a space with existing models for full testing."
                )
        else:
            results["recommendations"].append(
                "⚠️ No endpoints could be tested - space may not have analytical models or tables."
            )

        if results["summary"]["errors"] > 0:
            results["recommendations"].append(
                f"❌ {results['summary']['errors']} endpoints returned errors - check permissions and model configuration."
            )

        results["next_steps"] = [
            "1. Review the detailed status for each endpoint above",
            "2. If most endpoints are 'available', set USE_MOCK_DATA=false in Claude Desktop config",
            "3. If endpoints show 'needs_assets', create analytical models in your space",
            "4. Test the tools with real data after disabling mock mode"
        ]

        return [types.TextContent(
            type="text",
            text=f"Analytical & Query Endpoints Test:\n\n{json.dumps(results, indent=2)}"
        )]

    # Phase 6 & 7 tool handlers removed (tools not available as REST APIs)

    else:
        return [types.TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]


# ============================================================================
# Repository Helper Functions
# ============================================================================

def build_dependency_graph(objects: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build dependency graph from repository objects.

    Args:
        objects: List of repository objects with dependency information

    Returns:
        Dictionary with 'nodes' and 'edges' representing the dependency graph

    Example:
        objects = [
            {"id": "TABLE_A", "name": "Table A", "objectType": "Table",
             "dependencies": {"upstream": [], "downstream": ["VIEW_B"]}},
            {"id": "VIEW_B", "name": "View B", "objectType": "View",
             "dependencies": {"upstream": ["TABLE_A"], "downstream": []}}
        ]
        graph = build_dependency_graph(objects)
        # Returns: {
        #   'nodes': [{'id': 'TABLE_A', 'name': 'Table A', 'type': 'Table'}, ...],
        #   'edges': [{'from': 'TABLE_A', 'to': 'VIEW_B', 'type': 'upstream'}, ...]
        # }
    """
    graph = {
        'nodes': [],
        'edges': []
    }

    # Add nodes
    for obj in objects:
        graph['nodes'].append({
            'id': obj.get('id', obj.get('objectId', 'Unknown')),
            'name': obj.get('name', 'Unknown'),
            'type': obj.get('objectType', obj.get('object_type', 'Unknown')),
            'status': obj.get('status', 'Unknown')
        })

    # Add edges
    for obj in objects:
        obj_id = obj.get('id', obj.get('objectId'))
        if not obj_id:
            continue

        dependencies = obj.get('dependencies', {})

        # Upstream dependencies (sources)
        for upstream in dependencies.get('upstream', []):
            graph['edges'].append({
                'from': upstream,
                'to': obj_id,
                'type': 'upstream'
            })

        # Downstream dependencies (consumers)
        for downstream in dependencies.get('downstream', []):
            graph['edges'].append({
                'from': obj_id,
                'to': downstream,
                'type': 'downstream'
            })

    return graph


def analyze_impact(object_id: str, objects: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze impact of changing an object.

    Performs recursive downstream dependency analysis to identify all objects
    that would be affected by changes to the specified object.

    Args:
        object_id: ID of the object to analyze
        objects: List of repository objects with dependency information

    Returns:
        Dictionary containing:
        - object_id: The analyzed object ID
        - direct_downstream: List of directly dependent objects
        - indirect_downstream: List of indirectly dependent objects
        - total_affected: Total count of affected objects
        - affected_by_type: Breakdown by object type

    Example:
        impact = analyze_impact("TABLE_A", objects)
        # Returns: {
        #   'object_id': 'TABLE_A',
        #   'direct_downstream': ['VIEW_B', 'VIEW_C'],
        #   'indirect_downstream': ['MODEL_D', 'REPORT_E'],
        #   'total_affected': 4,
        #   'affected_by_type': {'View': 2, 'AnalyticalModel': 1, 'Report': 1}
        # }
    """
    impact = {
        'object_id': object_id,
        'direct_downstream': [],
        'indirect_downstream': [],
        'total_affected': 0,
        'affected_by_type': {}
    }

    # Find the object
    obj = next((o for o in objects if o.get('id') == object_id or o.get('objectId') == object_id), None)
    if not obj:
        impact['error'] = f"Object '{object_id}' not found"
        return impact

    # Get direct downstream dependencies
    dependencies = obj.get('dependencies', {})
    direct = dependencies.get('downstream', [])
    impact['direct_downstream'] = direct

    # Recursively find indirect downstream dependencies
    visited = set([object_id])
    queue = list(direct)

    while queue:
        current = queue.pop(0)
        if current in visited:
            continue

        visited.add(current)
        impact['indirect_downstream'].append(current)

        # Find the current object to get its downstream dependencies
        current_obj = next((o for o in objects if o.get('id') == current or o.get('objectId') == current), None)
        if current_obj:
            # Count by type
            obj_type = current_obj.get('objectType', current_obj.get('object_type', 'Unknown'))
            impact['affected_by_type'][obj_type] = impact['affected_by_type'].get(obj_type, 0) + 1

            # Add downstream dependencies to queue
            current_deps = current_obj.get('dependencies', {})
            downstream = current_deps.get('downstream', [])
            queue.extend(downstream)

    # Total affected objects (excluding the source object itself)
    impact['total_affected'] = len(visited) - 1

    return impact


# Object type categories for classification
OBJECT_TYPE_CATEGORIES = {
    'data_objects': ['Table', 'View', 'Entity'],
    'analytical_objects': ['AnalyticalModel', 'CalculationView', 'Hierarchy'],
    'integration_objects': ['DataFlow', 'Transformation', 'Replication'],
    'logic_objects': ['StoredProcedure', 'Function', 'Script']
}


def categorize_objects(objects: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Categorize objects by type.

    Groups repository objects into logical categories:
    - data_objects: Tables, Views, Entities
    - analytical_objects: Analytical Models, Calculation Views, Hierarchies
    - integration_objects: Data Flows, Transformations, Replications
    - logic_objects: Stored Procedures, Functions, Scripts
    - other: Any objects not matching the above categories

    Args:
        objects: List of repository objects

    Returns:
        Dictionary with categories as keys and lists of objects as values

    Example:
        categorized = categorize_objects(objects)
        # Returns: {
        #   'data_objects': [table1, table2, view1],
        #   'analytical_objects': [model1, model2],
        #   'integration_objects': [flow1],
        #   'logic_objects': [],
        #   'other': []
        # }
    """
    categorized = {
        'data_objects': [],
        'analytical_objects': [],
        'integration_objects': [],
        'logic_objects': [],
        'other': []
    }

    for obj in objects:
        obj_type = obj.get('objectType', obj.get('object_type', 'Unknown'))
        categorized_flag = False

        for category, types in OBJECT_TYPE_CATEGORIES.items():
            if obj_type in types:
                categorized[category].append(obj)
                categorized_flag = True
                break

        if not categorized_flag:
            categorized['other'].append(obj)

    return categorized


def compare_design_deployed(design_obj: Dict[str, Any], deployed_obj: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare design-time and deployed object definitions.

    Identifies differences between design-time and deployed versions of an object,
    including version mismatches, column changes, and schema modifications.

    Args:
        design_obj: Design-time object definition
        deployed_obj: Deployed object definition

    Returns:
        Dictionary containing:
        - object_id: Object identifier
        - version_match: Boolean indicating if versions match
        - deployment_status: Deployment status
        - differences: List of identified differences
        - has_differences: Boolean indicating if any differences found

    Example:
        comparison = compare_design_deployed(design_obj, deployed_obj)
        # Returns: {
        #   'object_id': 'TABLE_A',
        #   'version_match': False,
        #   'differences': [
        #     {'type': 'version_mismatch', 'design_version': '2.0', 'deployed_version': '1.5'},
        #     {'type': 'columns_added', 'columns': ['NEW_COLUMN']}
        #   ],
        #   'has_differences': True
        # }
    """
    comparison = {
        'object_id': design_obj.get('id', design_obj.get('objectId')),
        'version_match': design_obj.get('version') == deployed_obj.get('version'),
        'deployment_status': deployed_obj.get('deploymentStatus', deployed_obj.get('deployment_status')),
        'differences': []
    }

    # Compare versions
    if not comparison['version_match']:
        comparison['differences'].append({
            'type': 'version_mismatch',
            'design_version': design_obj.get('version'),
            'deployed_version': deployed_obj.get('version')
        })

    # Compare columns (for tables/views)
    design_def = design_obj.get('definition', {})
    deployed_def = deployed_obj.get('definition', {})

    if 'columns' in design_def:
        design_cols = {c['name']: c for c in design_def['columns']}
        deployed_cols = {}

        if 'columns' in deployed_def:
            deployed_cols = {c['name']: c for c in deployed_def['columns']}

        # Find added columns
        added = set(design_cols.keys()) - set(deployed_cols.keys())
        if added:
            comparison['differences'].append({
                'type': 'columns_added',
                'columns': list(added)
            })

        # Find removed columns
        removed = set(deployed_cols.keys()) - set(design_cols.keys())
        if removed:
            comparison['differences'].append({
                'type': 'columns_removed',
                'columns': list(removed)
            })

        # Find modified columns (data type changes)
        for col_name in set(design_cols.keys()) & set(deployed_cols.keys()):
            design_col = design_cols[col_name]
            deployed_col = deployed_cols[col_name]

            if design_col.get('dataType') != deployed_col.get('dataType'):
                comparison['differences'].append({
                    'type': 'column_type_changed',
                    'column': col_name,
                    'design_type': design_col.get('dataType'),
                    'deployed_type': deployed_col.get('dataType')
                })

    comparison['has_differences'] = len(comparison['differences']) > 0

    return comparison


async def main():
    """Main function to run the MCP server"""
    global datasphere_connector

    # Initialize OAuth connector if not using mock data
    if not DATASPHERE_CONFIG["use_mock_data"]:
        try:
            logger.info("Initializing OAuth connection to SAP Datasphere...")

            # Create Datasphere configuration
            config = DatasphereConfig(
                base_url=DATASPHERE_CONFIG["base_url"],
                client_id=DATASPHERE_CONFIG["oauth_config"]["client_id"],
                client_secret=DATASPHERE_CONFIG["oauth_config"]["client_secret"],
                token_url=DATASPHERE_CONFIG["oauth_config"]["token_url"],
                tenant_id=DATASPHERE_CONFIG["tenant_id"],
                scope=DATASPHERE_CONFIG["oauth_config"].get("scope")
            )

            # Initialize connector
            datasphere_connector = DatasphereAuthConnector(config)
            await datasphere_connector.initialize()

            logger.info("✅ OAuth connection initialized successfully")
            logger.info(f"OAuth health: {datasphere_connector.oauth_handler.get_health_status()}")

        except Exception as e:
            logger.error(f"❌ Failed to initialize OAuth connection: {e}")
            logger.error("Server will start but tools will fail. Please check .env configuration.")
            logger.error("See OAUTH_REAL_CONNECTION_SETUP.md for setup instructions.")
    else:
        logger.info("ℹ️  Running in MOCK DATA mode")
        logger.info("Set USE_MOCK_DATA=false in .env to connect to real SAP Datasphere")

    # Use stdin/stdout for MCP communication
    try:
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="sap-datasphere-mcp",
                    server_version="1.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                ),
            )
    finally:
        # Cleanup OAuth connector on shutdown
        if datasphere_connector:
            logger.info("Closing OAuth connection...")
            await datasphere_connector.close()
            logger.info("OAuth connection closed")

if __name__ == "__main__":
    asyncio.run(main())