#!/usr/bin/env python3
"""
SAP Datasphere MCP Server
Provides AI assistants with access to SAP Datasphere capabilities
Can work with mock data or real API connections
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Sequence
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

# Enhanced tool descriptions
from tool_descriptions import ToolDescriptions

# Error helpers for better UX
from error_helpers import ErrorHelpers

# Mock data for development and testing
from mock_data import MOCK_DATA

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sap-datasphere-mcp")

# Configuration
DATASPHERE_CONFIG = {
    "tenant_id": "f45fa9cc-f4b5-4126-ab73-b19b578fb17a",
    "base_url": "https://f45fa9cc-f4b5-4126-ab73-b19b578fb17a.eu10.hcs.cloud.sap",
    "use_mock_data": True,  # Set to False when real OAuth credentials are available
    "oauth_config": {
        "client_id": None,
        "client_secret": None,
        "token_url": None
    }
}

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
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    """Handle tool calls with validation, authorization, and consent checks"""

    if arguments is None:
        arguments = {}

    try:
        # Step 1: Validate input parameters
        if ToolValidators.has_validator(name):
            validation_rules = ToolValidators.get_validator_rules(name)
            is_valid, validation_errors = input_validator.validate_params(
                arguments,
                validation_rules
            )

            if not is_valid:
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

        return filtered_result

    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error executing tool {name}: {str(e)}"
        )]


async def _execute_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Execute tool logic without authorization checks"""

    if name == "list_spaces":
        include_details = arguments.get("include_details", False)

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

        return [types.TextContent(
            type="text",
            text=f"Found {len(result)} Datasphere spaces:\n\n" +
                 json.dumps(result, indent=2)
        )]

    elif name == "get_space_info":
        space_id = arguments["space_id"]

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

        return [types.TextContent(
            type="text",
            text=f"Space Information for '{space_id}':\n\n" +
                 json.dumps(space_info, indent=2)
        )]

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

        tables = MOCK_DATA["tables"].get(space_id, [])
        table = next((t for t in tables if t["name"] == table_name), None)

        if not table:
            # Enhanced error message with available tables
            error_msg = ErrorHelpers.table_not_found(table_name, space_id, tables)
            return [types.TextContent(
                type="text",
                text=error_msg
            )]

        return [types.TextContent(
            type="text",
            text=f"Schema for table '{table_name}' in space '{space_id}':\n\n" +
                 json.dumps(table, indent=2)
        )]

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

    else:
        return [types.TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]

async def main():
    """Main function to run the MCP server"""
    
    # Use stdin/stdout for MCP communication
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="sap-datasphere-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                )
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())