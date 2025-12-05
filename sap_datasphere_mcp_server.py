#!/usr/bin/env python3
"""
SAP Datasphere MCP Server
Provides AI assistants with access to SAP Datasphere capabilities
Can work with mock data or real API connections
"""

import asyncio
import json
import logging
import time
import secrets
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Sequence
from dotenv import load_dotenv
from mcp.server import Server
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
cache_manager = CacheManager(
    max_size=1000,
    enabled=True
)
telemetry_manager = TelemetryManager(
    max_history=1000
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
        )
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

        # Not in cache, fetch data
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
                 json.dumps(result, indent=2)
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

        # Not in cache, fetch data
        space = next((s for s in MOCK_DATA["spaces"] if s["id"] == space_id), None)
        if not space:
            # Enhanced error message with suggestions
            error_msg = ErrorHelpers.space_not_found(space_id, MOCK_DATA["spaces"])
            return [types.TextContent(
                type="text",
                text=error_msg
            )]

        # Add table information
        tables = MOCK_DATA["tables"].get(space_id, [])
        space_info = space.copy()
        space_info["tables"] = tables

        response = [types.TextContent(
            type="text",
            text=f"Space Information for '{space_id}':\n\n" +
                 json.dumps(space_info, indent=2)
        )]

        # Cache the response
        cache_manager.set(space_id, response, CacheCategory.SPACE_INFO)

        return response

    elif name == "search_tables":
        search_term = arguments["search_term"].lower()
        space_filter = arguments.get("space_id")

        found_tables = []

        for space_id, tables in MOCK_DATA["tables"].items():
            if space_filter and space_id != space_filter:
                continue

            for table in tables:
                if (search_term in table["name"].lower() or
                    search_term in table["description"].lower()):

                    table_info = table.copy()
                    table_info["space_id"] = space_id
                    found_tables.append(table_info)

        return [types.TextContent(
            type="text",
            text=f"Found {len(found_tables)} tables matching '{search_term}':\n\n" +
                 json.dumps(found_tables, indent=2)
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

        connections = MOCK_DATA["connections"]
        if connection_type:
            connections = [c for c in connections if c["type"] == connection_type]

        return [types.TextContent(
            type="text",
            text=f"Found {len(connections)} data connections:\n\n" +
                 json.dumps(connections, indent=2)
        )]

    elif name == "get_task_status":
        task_id = arguments.get("task_id")
        space_filter = arguments.get("space_id")

        tasks = MOCK_DATA["tasks"]

        if task_id:
            tasks = [t for t in tasks if t["id"] == task_id]
        elif space_filter:
            tasks = [t for t in tasks if t["space"] == space_filter]

        return [types.TextContent(
            type="text",
            text=f"Task Status Information:\n\n" +
                 json.dumps(tasks, indent=2)
        )]

    elif name == "browse_marketplace":
        category = arguments.get("category")
        search_term = arguments.get("search_term", "").lower()

        packages = MOCK_DATA["marketplace_packages"]

        if category:
            packages = [p for p in packages if p["category"] == category]

        if search_term:
            packages = [p for p in packages if
                       search_term in p["name"].lower() or
                       search_term in p["description"].lower()]

        return [types.TextContent(
            type="text",
            text=f"Found {len(packages)} marketplace packages:\n\n" +
                 json.dumps(packages, indent=2)
        )]

    elif name == "execute_query":
        space_id = arguments["space_id"]
        sql_query = arguments["sql_query"]
        limit = arguments.get("limit", 100)

        # Simulate query execution with mock results
        mock_result = {
            "query": sql_query,
            "space": space_id,
            "execution_time": "0.245 seconds",
            "rows_returned": min(limit, 50),  # Simulate some results
            "sample_data": [
                {"CUSTOMER_ID": "C001", "CUSTOMER_NAME": "Acme Corp", "COUNTRY": "USA"},
                {"CUSTOMER_ID": "C002", "CUSTOMER_NAME": "Global Tech", "COUNTRY": "Germany"},
                {"CUSTOMER_ID": "C003", "CUSTOMER_NAME": "Data Solutions", "COUNTRY": "UK"}
            ][:limit],
            "note": "This is simulated data. Real query execution requires OAuth authentication."
        }

        return [types.TextContent(
            type="text",
            text=f"Query Execution Results:\n\n" +
                 json.dumps(mock_result, indent=2)
        )]

    elif name == "list_database_users":
        space_id = arguments["space_id"]
        output_file = arguments.get("output_file")

        # Get database users for the space
        users = MOCK_DATA["database_users"].get(space_id, [])

        if not users:
            return [types.TextContent(
                type="text",
                text=f"No database users found in space '{space_id}'.\n\n"
                     f"This could mean:\n"
                     f"- The space exists but has no database users configured\n"
                     f"- The space ID might be incorrect\n\n"
                     f"Use list_spaces to see available spaces."
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
                 json.dumps(result, indent=2)
        )]

    elif name == "create_database_user":
        space_id = arguments["space_id"]
        database_user_id = arguments["database_user_id"]
        user_definition = arguments["user_definition"]
        output_file = arguments.get("output_file")

        # Generate a secure password
        password = secrets.token_urlsafe(16)
        full_username = f"{space_id}#{database_user_id}"

        # Create the user result
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
                 f"\n\n⚠️  WARNING: This is mock data. Real user creation requires OAuth authentication."
        )]

    elif name == "reset_database_user_password":
        space_id = arguments["space_id"]
        database_user_id = arguments["database_user_id"]
        output_file = arguments.get("output_file")

        # Check if user exists
        users = MOCK_DATA["database_users"].get(space_id, [])
        user = next((u for u in users if u["user_id"] == database_user_id), None)

        if not user:
            return [types.TextContent(
                type="text",
                text=f">>> User Not Found <<<\n\n"
                     f"Database user '{database_user_id}' does not exist in space '{space_id}'.\n\n"
                     f"Available users in {space_id}:\n" +
                     "\n".join(f"- {u['user_id']}" for u in users) if users else "No users found."
            )]

        # Generate new password
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
                 f"\n\n⚠️  WARNING: This is mock data. Real password reset requires OAuth authentication."
        )]

    elif name == "update_database_user":
        space_id = arguments["space_id"]
        database_user_id = arguments["database_user_id"]
        updated_definition = arguments["updated_definition"]
        output_file = arguments.get("output_file")

        # Check if user exists
        users = MOCK_DATA["database_users"].get(space_id, [])
        user = next((u for u in users if u["user_id"] == database_user_id), None)

        if not user:
            return [types.TextContent(
                type="text",
                text=f">>> User Not Found <<<\n\n"
                     f"Database user '{database_user_id}' does not exist in space '{space_id}'.\n\n"
                     f"Available users in {space_id}:\n" +
                     "\n".join(f"- {u['user_id']}" for u in users) if users else "No users found."
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
                 f"\n\n⚠️  WARNING: This is mock data. Real user update requires OAuth authentication."
        )]

    elif name == "delete_database_user":
        space_id = arguments["space_id"]
        database_user_id = arguments["database_user_id"]
        force = arguments.get("force", False)

        # Check if user exists
        users = MOCK_DATA["database_users"].get(space_id, [])
        user = next((u for u in users if u["user_id"] == database_user_id), None)

        if not user:
            return [types.TextContent(
                type="text",
                text=f">>> User Not Found <<<\n\n"
                     f"Database user '{database_user_id}' does not exist in space '{space_id}'.\n\n"
                     f"Available users in {space_id}:\n" +
                     "\n".join(f"- {u['user_id']}" for u in users) if users else "No users found."
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
                     f"To confirm deletion, call this tool again with 'force': true"
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
                 f"\n\n⚠️  WARNING: This is mock data. Real user deletion requires OAuth authentication."
        )]

    elif name == "list_catalog_assets":
        # Extract OData query parameters
        select_fields = arguments.get("select_fields")
        filter_expression = arguments.get("filter_expression")
        top = arguments.get("top", 50)
        skip = arguments.get("skip", 0)
        count = arguments.get("count", False)
        orderby = arguments.get("orderby")

        # Get catalog assets (mock data supports space_id and asset_type filtering)
        # Parse filter_expression for supported filters
        space_id_filter = None
        asset_type_filter = None

        if filter_expression:
            # Simple parsing for common filters (production would use OData parser)
            if "spaceId eq" in filter_expression:
                # Extract space ID from filter like "spaceId eq 'SAP_CONTENT'"
                import re
                match = re.search(r"spaceId eq '([^']+)'", filter_expression)
                if match:
                    space_id_filter = match.group(1)
            if "assetType eq" in filter_expression:
                # Extract asset type from filter like "assetType eq 'AnalyticalModel'"
                import re
                match = re.search(r"assetType eq '([^']+)'", filter_expression)
                if match:
                    asset_type_filter = match.group(1)

        # Get filtered assets
        assets = get_mock_catalog_assets(space_id=space_id_filter, asset_type=asset_type_filter)

        # Apply select fields if specified
        if select_fields:
            assets = [
                {field: asset.get(field) for field in select_fields if field in asset}
                for asset in assets
            ]

        # Apply orderby (simple implementation)
        if orderby:
            field = orderby.split()[0]  # e.g., "name asc" -> "name"
            reverse = "desc" in orderby.lower()
            assets = sorted(assets, key=lambda x: x.get(field, ""), reverse=reverse)

        # Get total count before pagination
        total_count = len(assets)

        # Apply pagination
        assets = assets[skip:skip + top]

        result = {
            "value": assets,
            "count": total_count if count else None,
            "top": top,
            "skip": skip,
            "returned": len(assets)
        }

        return [types.TextContent(
            type="text",
            text=f"Found {total_count} catalog assets (showing {len(assets)}):\n\n" +
                 json.dumps(result, indent=2) +
                 f"\n\n⚠️  NOTE: This is mock data. Real catalog browsing requires OAuth authentication."
        )]

    elif name == "get_asset_details":
        space_id = arguments["space_id"]
        asset_id = arguments["asset_id"]
        select_fields = arguments.get("select_fields")

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
            text=f"Asset Details for '{asset_id}' in space '{space_id}':\n\n" +
                 json.dumps(asset, indent=2) +
                 f"\n\n⚠️  NOTE: This is mock data. Real catalog browsing requires OAuth authentication."
        )]

    elif name == "get_asset_by_compound_key":
        compound_key = arguments["compound_key"]
        select_fields = arguments.get("select_fields")

        # Parse compound key format: spaceId='SAP_CONTENT',id='SAP_SC_FI_AM_FINTRANSACTIONS'
        # Simple parsing (production would use proper OData parser)
        import re
        space_match = re.search(r"spaceId='([^']+)'", compound_key)
        id_match = re.search(r"id='([^']+)'", compound_key)

        if not space_match or not id_match:
            return [types.TextContent(
                type="text",
                text=f">>> Invalid Compound Key <<<\n\n"
                     f"The compound_key format is invalid.\n\n"
                     f"Expected format: spaceId='SPACE_ID',id='ASSET_ID'\n"
                     f"Example: spaceId='SAP_CONTENT',id='SAP_SC_FI_AM_FINTRANSACTIONS'\n\n"
                     f"Received: {compound_key}"
            )]

        space_id = space_match.group(1)
        asset_id = id_match.group(1)

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
            text=f"Asset Details (compound key lookup):\n\n" +
                 json.dumps(asset, indent=2) +
                 f"\n\n⚠️  NOTE: This is mock data. Real catalog browsing requires OAuth authentication."
        )]

    elif name == "get_space_assets":
        space_id = arguments["space_id"]
        select_fields = arguments.get("select_fields")
        filter_expression = arguments.get("filter_expression")
        top = arguments.get("top", 50)
        skip = arguments.get("skip", 0)
        count = arguments.get("count", False)
        orderby = arguments.get("orderby")

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
            text=f"Found {total_count} assets in space '{space_id}' (showing {len(assets)}):\n\n" +
                 json.dumps(result, indent=2) +
                 f"\n\n⚠️  NOTE: This is mock data. Real catalog browsing requires OAuth authentication."
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

    else:
        return [types.TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]

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
                    capabilities=server.get_capabilities()
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