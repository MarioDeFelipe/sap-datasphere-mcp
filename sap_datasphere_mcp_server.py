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
    LoggingLevel
)
import mcp.server.stdio
import mcp.types as types

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

# Mock data for development and testing
MOCK_DATA = {
    "spaces": [
        {
            "id": "SALES_ANALYTICS",
            "name": "Sales Analytics",
            "description": "Sales data analysis and reporting space",
            "status": "ACTIVE",
            "created_date": "2024-01-15T10:30:00Z",
            "owner": "sales.admin@company.com",
            "tables_count": 15,
            "views_count": 8,
            "connections_count": 3
        },
        {
            "id": "FINANCE_DWH",
            "name": "Finance Data Warehouse", 
            "description": "Financial data warehouse and reporting",
            "status": "ACTIVE",
            "created_date": "2024-02-01T14:20:00Z",
            "owner": "finance.admin@company.com",
            "tables_count": 25,
            "views_count": 12,
            "connections_count": 5
        },
        {
            "id": "HR_ANALYTICS",
            "name": "HR Analytics",
            "description": "Human resources analytics and insights",
            "status": "DEVELOPMENT",
            "created_date": "2024-03-10T09:15:00Z", 
            "owner": "hr.admin@company.com",
            "tables_count": 8,
            "views_count": 4,
            "connections_count": 2
        }
    ],
    
    "tables": {
        "SALES_ANALYTICS": [
            {
                "name": "CUSTOMER_DATA",
                "type": "TABLE",
                "description": "Customer master data with demographics",
                "columns": [
                    {"name": "CUSTOMER_ID", "type": "NVARCHAR(10)", "key": True},
                    {"name": "CUSTOMER_NAME", "type": "NVARCHAR(100)"},
                    {"name": "COUNTRY", "type": "NVARCHAR(50)"},
                    {"name": "REGION", "type": "NVARCHAR(50)"},
                    {"name": "REGISTRATION_DATE", "type": "DATE"}
                ],
                "row_count": 15420,
                "last_updated": "2024-10-02T18:30:00Z"
            },
            {
                "name": "SALES_ORDERS",
                "type": "TABLE", 
                "description": "Sales order transactions",
                "columns": [
                    {"name": "ORDER_ID", "type": "NVARCHAR(10)", "key": True},
                    {"name": "CUSTOMER_ID", "type": "NVARCHAR(10)"},
                    {"name": "ORDER_DATE", "type": "DATE"},
                    {"name": "AMOUNT", "type": "DECIMAL(15,2)"},
                    {"name": "STATUS", "type": "NVARCHAR(20)"}
                ],
                "row_count": 89650,
                "last_updated": "2024-10-03T08:15:00Z"
            }
        ],
        "FINANCE_DWH": [
            {
                "name": "GL_ACCOUNTS",
                "type": "TABLE",
                "description": "General ledger account master data",
                "columns": [
                    {"name": "ACCOUNT_ID", "type": "NVARCHAR(10)", "key": True},
                    {"name": "ACCOUNT_NAME", "type": "NVARCHAR(100)"},
                    {"name": "ACCOUNT_TYPE", "type": "NVARCHAR(50)"},
                    {"name": "BALANCE", "type": "DECIMAL(15,2)"}
                ],
                "row_count": 2340,
                "last_updated": "2024-10-01T23:45:00Z"
            }
        ]
    },
    
    "connections": [
        {
            "id": "SAP_ERP_PROD",
            "name": "SAP ERP Production",
            "type": "SAP_ERP",
            "description": "Connection to production SAP ERP system",
            "status": "CONNECTED",
            "host": "erp-prod.company.com",
            "last_tested": "2024-10-03T06:00:00Z"
        },
        {
            "id": "SALESFORCE_API",
            "name": "Salesforce CRM",
            "type": "SALESFORCE",
            "description": "Salesforce CRM data connection",
            "status": "CONNECTED", 
            "host": "company.salesforce.com",
            "last_tested": "2024-10-03T07:30:00Z"
        },
        {
            "id": "AWS_S3_DATALAKE",
            "name": "AWS S3 Data Lake",
            "type": "AWS_S3",
            "description": "AWS S3 data lake storage",
            "status": "CONNECTED",
            "host": "s3://company-datalake/",
            "last_tested": "2024-10-03T05:15:00Z"
        }
    ],
    
    "tasks": [
        {
            "id": "DAILY_SALES_ETL",
            "name": "Daily Sales ETL",
            "description": "Daily extraction and loading of sales data",
            "status": "COMPLETED",
            "space": "SALES_ANALYTICS",
            "last_run": "2024-10-03T02:00:00Z",
            "next_run": "2024-10-04T02:00:00Z",
            "duration": "00:15:32",
            "records_processed": 1250
        },
        {
            "id": "FINANCE_RECONCILIATION",
            "name": "Finance Reconciliation",
            "description": "Monthly finance data reconciliation",
            "status": "RUNNING",
            "space": "FINANCE_DWH", 
            "last_run": "2024-10-03T10:00:00Z",
            "next_run": "2024-11-01T10:00:00Z",
            "duration": "01:45:00",
            "records_processed": 45000
        }
    ],
    
    "marketplace_packages": [
        {
            "id": "INDUSTRY_BENCHMARKS",
            "name": "Industry Benchmarks",
            "description": "Industry benchmark data for comparative analysis",
            "category": "Reference Data",
            "provider": "SAP",
            "version": "2024.Q3",
            "size": "2.5 GB",
            "price": "Free"
        },
        {
            "id": "CURRENCY_RATES",
            "name": "Daily Currency Rates",
            "description": "Real-time currency exchange rates",
            "category": "Financial Data",
            "provider": "Financial Data Corp",
            "version": "Live",
            "size": "50 MB",
            "price": "$99/month"
        }
    ]
}

# Initialize the MCP server
server = Server("sap-datasphere-mcp")

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

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
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
                        "description": "Search term to find tables (searches names and descriptions)"
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
            name="get_table_schema",
            description="Get detailed schema information for a specific table",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "The space containing the table"
                    },
                    "table_name": {
                        "type": "string",
                        "description": "The name of the table"
                    }
                },
                "required": ["space_id", "table_name"]
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
                        "description": "Optional: filter by connection type (SAP_ERP, SALESFORCE, AWS_S3, etc.)"
                    }
                }
            }
        ),
        Tool(
            name="get_task_status",
            description="Get status and details of data integration tasks",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Optional: specific task ID to check"
                    },
                    "space_id": {
                        "type": "string",
                        "description": "Optional: filter tasks by space"
                    }
                }
            }
        ),
        Tool(
            name="browse_marketplace",
            description="Browse available data packages in the Datasphere marketplace",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Optional: filter by category (Reference Data, Financial Data, etc.)"
                    },
                    "search_term": {
                        "type": "string",
                        "description": "Optional: search term for package names or descriptions"
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
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of rows to return",
                        "default": 100
                    }
                },
                "required": ["space_id", "sql_query"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    """Handle tool calls"""
    
    if arguments is None:
        arguments = {}
    
    try:
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
                return [types.TextContent(
                    type="text",
                    text=f"Space '{space_id}' not found. Available spaces: {[s['id'] for s in MOCK_DATA['spaces']]}"
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
                return [types.TextContent(
                    type="text",
                    text=f"Table '{table_name}' not found in space '{space_id}'"
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