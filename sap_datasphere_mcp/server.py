"""
SAP Datasphere MCP Server

A Model Context Protocol server for SAP Datasphere integration.
"""

import os
import sys
from typing import Any, Sequence
from dotenv import load_dotenv
from loguru import logger
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    TextContent,
    Tool,
)

from .models import DatasphereConfig
from .client import DatasphereClient

# Load environment variables
load_dotenv()

# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# Initialize MCP server
app = Server("sap-datasphere-mcp")

# Global client instance
datasphere_client: DatasphereClient = None


def get_config() -> DatasphereConfig:
    """Load configuration from environment variables"""
    
    required_vars = [
        "DATASPHERE_TENANT_URL",
        "OAUTH_CLIENT_ID", 
        "OAUTH_CLIENT_SECRET",
        "OAUTH_TOKEN_URL"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # Extract tenant ID from URL if not provided
    tenant_id = os.getenv("DATASPHERE_TENANT_ID")
    if not tenant_id:
        tenant_url = os.getenv("DATASPHERE_TENANT_URL")
        # Extract tenant ID from URL like https://f45fa9cc-f4b5-4126-ab73-b19b578fb17a.eu10.hcs.cloud.sap
        tenant_id = tenant_url.split("//")[1].split(".")[0]
    
    return DatasphereConfig(
        tenant_url=os.getenv("DATASPHERE_TENANT_URL"),
        tenant_id=tenant_id,
        oauth_client_id=os.getenv("OAUTH_CLIENT_ID"),
        oauth_client_secret=os.getenv("OAUTH_CLIENT_SECRET"),
        oauth_token_url=os.getenv("OAUTH_TOKEN_URL"),
        oauth_authorization_url=os.getenv("OAUTH_AUTHORIZATION_URL"),
        api_timeout=int(os.getenv("API_TIMEOUT", "30")),
        api_retry_count=int(os.getenv("API_RETRY_COUNT", "3"))
    )


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools"""
    
    return [
        Tool(
            name="test_connection",
            description="Test the connection to SAP Datasphere",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="discover_endpoints",
            description="Discover available API endpoints in SAP Datasphere",
            inputSchema={
                "type": "object", 
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="list_spaces",
            description="List all available SAP Datasphere spaces",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_space_info",
            description="Get detailed information about a specific space",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "The ID of the space to get information about"
                    }
                },
                "required": ["space_id"]
            }
        ),
        Tool(
            name="list_catalog",
            description="List catalog items (tables, views, etc.) in a space or globally",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "Optional space ID to filter catalog items"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_table_info",
            description="Get detailed information about a specific table or view",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "The space ID containing the table"
                    },
                    "table_name": {
                        "type": "string", 
                        "description": "The name of the table to get information about"
                    }
                },
                "required": ["space_id", "table_name"]
            }
        ),
        Tool(
            name="list_connections",
            description="List data source connections in a space or globally",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "Optional space ID to filter connections"
                    }
                },
                "required": []
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls"""
    
    global datasphere_client
    
    try:
        if name == "test_connection":
            result = await datasphere_client.test_connection()
            
            if result.success:
                return [TextContent(
                    type="text",
                    text=f"✅ Connection successful!\n\nTenant: {result.data['tenant_url']}\nStatus: {result.data['status']}"
                )]
            else:
                return [TextContent(
                    type="text", 
                    text=f"❌ Connection failed: {result.error}"
                )]
        
        elif name == "discover_endpoints":
            result = await datasphere_client.discover_api_endpoints()
            
            if result.success:
                endpoints = result.data["working_endpoints"]
                if endpoints:
                    endpoint_list = "\n".join([
                        f"• {ep['endpoint']} (HTTP {ep['status_code']})"
                        for ep in endpoints
                    ])
                    return [TextContent(
                        type="text",
                        text=f"🔍 Found {len(endpoints)} working API endpoints:\n\n{endpoint_list}"
                    )]
                else:
                    return [TextContent(
                        type="text",
                        text="❌ No working API endpoints found. This might indicate:\n• Missing API permissions\n• Different API paths than expected\n• API access not enabled for this OAuth client"
                    )]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ Endpoint discovery failed: {result.error}"
                )]
        
        elif name == "list_spaces":
            result = await datasphere_client.list_spaces()
            
            if result.success:
                spaces = result.data
                if spaces:
                    space_list = "\n".join([
                        f"• {space['name']} (ID: {space['id']})"
                        + (f" - {space['description']}" if space.get('description') else "")
                        for space in spaces
                    ])
                    return [TextContent(
                        type="text",
                        text=f"🏢 Found {len(spaces)} spaces:\n\n{space_list}"
                    )]
                else:
                    return [TextContent(
                        type="text",
                        text="📭 No spaces found or no access to spaces"
                    )]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ Failed to list spaces: {result.error}"
                )]
        
        elif name == "get_space_info":
            space_id = arguments["space_id"]
            result = await datasphere_client.get_space_info(space_id)
            
            if result.success:
                space = result.data
                info = f"🏢 Space Information:\n\n"
                info += f"Name: {space['name']}\n"
                info += f"ID: {space['id']}\n"
                if space.get('description'):
                    info += f"Description: {space['description']}\n"
                if space.get('type'):
                    info += f"Type: {space['type']}\n"
                if space.get('status'):
                    info += f"Status: {space['status']}\n"
                if space.get('owner'):
                    info += f"Owner: {space['owner']}\n"
                if space.get('created_at'):
                    info += f"Created: {space['created_at']}\n"
                
                return [TextContent(type="text", text=info)]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ Failed to get space info: {result.error}"
                )]
        
        elif name == "list_catalog":
            space_id = arguments.get("space_id")
            result = await datasphere_client.list_catalog(space_id)
            
            if result.success:
                items = result.data
                if items:
                    item_list = "\n".join([
                        f"• {item['name']} ({item['type']})"
                        + (f" - {item['description']}" if item.get('description') else "")
                        for item in items
                    ])
                    scope = f"in space {space_id}" if space_id else "globally"
                    return [TextContent(
                        type="text",
                        text=f"📊 Found {len(items)} catalog items {scope}:\n\n{item_list}"
                    )]
                else:
                    scope = f"in space {space_id}" if space_id else "globally"
                    return [TextContent(
                        type="text",
                        text=f"📭 No catalog items found {scope}"
                    )]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ Failed to list catalog: {result.error}"
                )]
        
        elif name == "get_table_info":
            space_id = arguments["space_id"]
            table_name = arguments["table_name"]
            result = await datasphere_client.get_table_info(space_id, table_name)
            
            if result.success:
                table = result.data
                info = f"📊 Table Information:\n\n"
                info += f"Name: {table['name']}\n"
                info += f"ID: {table['id']}\n"
                info += f"Type: {table['type']}\n"
                info += f"Space: {table['space_id']}\n"
                if table.get('description'):
                    info += f"Description: {table['description']}\n"
                if table.get('schema_name'):
                    info += f"Schema: {table['schema_name']}\n"
                if table.get('row_count'):
                    info += f"Rows: {table['row_count']}\n"
                if table.get('columns'):
                    info += f"\nColumns ({len(table['columns'])}):\n"
                    for col in table['columns'][:10]:  # Show first 10 columns
                        info += f"  • {col.get('name', 'Unknown')} ({col.get('type', 'Unknown')})\n"
                    if len(table['columns']) > 10:
                        info += f"  ... and {len(table['columns']) - 10} more columns\n"
                
                return [TextContent(type="text", text=info)]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ Failed to get table info: {result.error}"
                )]
        
        elif name == "list_connections":
            space_id = arguments.get("space_id")
            result = await datasphere_client.list_connections(space_id)
            
            if result.success:
                connections = result.data
                if connections:
                    conn_list = "\n".join([
                        f"• {conn['name']} ({conn['type']})"
                        + (f" - {conn['description']}" if conn.get('description') else "")
                        + (f" [{conn['status']}]" if conn.get('status') else "")
                        for conn in connections
                    ])
                    scope = f"in space {space_id}" if space_id else "globally"
                    return [TextContent(
                        type="text",
                        text=f"🔗 Found {len(connections)} connections {scope}:\n\n{conn_list}"
                    )]
                else:
                    scope = f"in space {space_id}" if space_id else "globally"
                    return [TextContent(
                        type="text",
                        text=f"📭 No connections found {scope}"
                    )]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ Failed to list connections: {result.error}"
                )]
        
        else:
            return [TextContent(
                type="text",
                text=f"❌ Unknown tool: {name}"
            )]
    
    except Exception as e:
        logger.error(f"Tool call failed: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Tool execution failed: {str(e)}"
        )]


@app.set_logging_level()
async def set_logging_level(level: str) -> None:
    """Set the logging level"""
    logger.remove()
    logger.add(sys.stderr, level=level.upper())


async def main():
    """Main entry point"""
    
    global datasphere_client
    
    try:
        # Load configuration
        config = get_config()
        logger.info(f"Loaded configuration for tenant: {config.tenant_url}")
        
        # Initialize Datasphere client
        datasphere_client = DatasphereClient(config)
        logger.info("Initialized SAP Datasphere client")
        
        # Test connection on startup
        logger.info("Testing connection to SAP Datasphere...")
        test_result = await datasphere_client.test_connection()
        
        if test_result.success:
            logger.info("✅ Connection to SAP Datasphere successful")
        else:
            logger.warning(f"⚠️ Connection test failed: {test_result.error}")
        
        # Run the MCP server
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="sap-datasphere-mcp",
                    server_version="0.1.0",
                    capabilities=app.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None,
                    ),
                ),
            )
    
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        sys.exit(1)
    
    finally:
        if datasphere_client:
            await datasphere_client.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())