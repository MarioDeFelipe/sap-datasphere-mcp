#!/usr/bin/env python3
"""
SAP Datasphere MCP Server - Simplified Version
Provides AI assistants with access to SAP Datasphere capabilities
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Resource, Tool, TextContent
import mcp.server.stdio
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sap-datasphere-mcp")

# Mock data for development
MOCK_SPACES = [
    {
        "id": "SALES_ANALYTICS",
        "name": "Sales Analytics",
        "description": "Sales data analysis and reporting space",
        "status": "ACTIVE",
        "tables_count": 15,
        "views_count": 8
    },
    {
        "id": "FINANCE_DWH",
        "name": "Finance Data Warehouse",
        "description": "Financial data warehouse and reporting",
        "status": "ACTIVE", 
        "tables_count": 25,
        "views_count": 12
    }
]

MOCK_TABLES = {
    "SALES_ANALYTICS": [
        {
            "name": "CUSTOMER_DATA",
            "type": "TABLE",
            "description": "Customer master data",
            "columns": [
                {"name": "CUSTOMER_ID", "type": "NVARCHAR(10)", "key": True},
                {"name": "CUSTOMER_NAME", "type": "NVARCHAR(100)"},
                {"name": "COUNTRY", "type": "NVARCHAR(50)"}
            ],
            "row_count": 15420
        },
        {
            "name": "SALES_ORDERS", 
            "type": "TABLE",
            "description": "Sales order transactions",
            "columns": [
                {"name": "ORDER_ID", "type": "NVARCHAR(10)", "key": True},
                {"name": "CUSTOMER_ID", "type": "NVARCHAR(10)"},
                {"name": "ORDER_DATE", "type": "DATE"},
                {"name": "AMOUNT", "type": "DECIMAL(15,2)"}
            ],
            "row_count": 89650
        }
    ]
}

MOCK_CONNECTIONS = [
    {
        "id": "SAP_ERP_PROD",
        "name": "SAP ERP Production",
        "type": "SAP_ERP",
        "status": "CONNECTED",
        "host": "erp-prod.company.com"
    },
    {
        "id": "SALESFORCE_API",
        "name": "Salesforce CRM", 
        "type": "SALESFORCE",
        "status": "CONNECTED",
        "host": "company.salesforce.com"
    }
]

# Initialize the MCP server
server = Server("sap-datasphere-mcp")

@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """List available Datasphere resources"""
    return [
        Resource(
            uri="datasphere://spaces",
            name="Datasphere Spaces",
            description="List of all Datasphere spaces",
            mimeType="application/json"
        ),
        Resource(
            uri="datasphere://connections",
            name="Data Connections", 
            description="Available data source connections",
            mimeType="application/json"
        )
    ]

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read specific Datasphere resource content"""
    if uri == "datasphere://spaces":
        return json.dumps(MOCK_SPACES, indent=2)
    elif uri == "datasphere://connections":
        return json.dumps(MOCK_CONNECTIONS, indent=2)
    else:
        raise ValueError(f"Unknown resource URI: {uri}")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available Datasphere tools"""
    return [
        Tool(
            name="list_spaces",
            description="List all Datasphere spaces with their status and metadata",
            inputSchema={
                "type": "object",
                "properties": {
                    "include_details": {
                        "type": "boolean",
                        "description": "Include detailed space information",
                        "default": False
                    }
                }
            }
        ),
        Tool(
            name="get_space_info",
            description="Get detailed information about a specific Datasphere space",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "The ID of the space to retrieve information for"
                    }
                },
                "required": ["space_id"]
            }
        ),
        Tool(
            name="search_tables",
            description="Search for tables and views across Datasphere spaces",
            inputSchema={
                "type": "object",
                "properties": {
                    "search_term": {
                        "type": "string",
                        "description": "Search term to find tables"
                    },
                    "space_id": {
                        "type": "string", 
                        "description": "Optional: limit search to specific space"
                    }
                },
                "required": ["search_term"]
            }
        ),
        Tool(
            name="list_connections",
            description="List all data source connections and their status",
            inputSchema={
                "type": "object",
                "properties": {
                    "connection_type": {
                        "type": "string",
                        "description": "Optional: filter by connection type"
                    }
                }
            }
        ),
        Tool(
            name="execute_query",
            description="Execute a SQL query against Datasphere data (simulated)",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "The space to execute the query in"
                    },
                    "sql_query": {
                        "type": "string",
                        "description": "The SQL query to execute"
                    }
                },
                "required": ["space_id", "sql_query"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any] | None) -> List[types.TextContent]:
    """Handle tool calls"""
    
    if arguments is None:
        arguments = {}
    
    try:
        if name == "list_spaces":
            include_details = arguments.get("include_details", False)
            
            if include_details:
                result = MOCK_SPACES
            else:
                result = [
                    {
                        "id": space["id"],
                        "name": space["name"],
                        "status": space["status"]
                    }
                    for space in MOCK_SPACES
                ]
            
            return [types.TextContent(
                type="text",
                text=f"Found {len(result)} Datasphere spaces:\n\n" + 
                     json.dumps(result, indent=2)
            )]
        
        elif name == "get_space_info":
            space_id = arguments["space_id"]
            
            space = next((s for s in MOCK_SPACES if s["id"] == space_id), None)
            if not space:
                return [types.TextContent(
                    type="text",
                    text=f"Space '{space_id}' not found. Available spaces: {[s['id'] for s in MOCK_SPACES]}"
                )]
            
            # Add table information
            tables = MOCK_TABLES.get(space_id, [])
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
            
            for space_id, tables in MOCK_TABLES.items():
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
        
        elif name == "list_connections":
            connection_type = arguments.get("connection_type")
            
            connections = MOCK_CONNECTIONS
            if connection_type:
                connections = [c for c in connections if c["type"] == connection_type]
            
            return [types.TextContent(
                type="text",
                text=f"Found {len(connections)} data connections:\n\n" +
                     json.dumps(connections, indent=2)
            )]
        
        elif name == "execute_query":
            space_id = arguments["space_id"]
            sql_query = arguments["sql_query"]
            
            # Simulate query execution
            mock_result = {
                "query": sql_query,
                "space": space_id,
                "execution_time": "0.245 seconds",
                "rows_returned": 3,
                "sample_data": [
                    {"CUSTOMER_ID": "C001", "CUSTOMER_NAME": "Acme Corp", "COUNTRY": "USA"},
                    {"CUSTOMER_ID": "C002", "CUSTOMER_NAME": "Global Tech", "COUNTRY": "Germany"},
                    {"CUSTOMER_ID": "C003", "CUSTOMER_NAME": "Data Solutions", "COUNTRY": "UK"}
                ],
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
    
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error executing tool {name}: {str(e)}"
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