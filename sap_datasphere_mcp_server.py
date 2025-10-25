#!/usr/bin/env python3
"""
SAP Datasphere MCP Server
Provides Model Context Protocol server for AI-accessible SAP Datasphere operations

This MCP server provides:
- SAP Datasphere space discovery
- Asset metadata exploration
- Business context-aware data discovery
- OAuth 2.0 authentication
- Natural language data queries

Compatible with Claude Desktop, Cursor IDE, and other MCP clients.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# MCP imports
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp import types

# SAP Datasphere connector
from datasphere_connector import DatasphereConnector, DatasphereConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MCPServerConfig:
    """Configuration for MCP server"""
    datasphere_base_url: str = "https://your-tenant.eu10.hcs.cloud.sap"
    environment_name: str = "mcp"
    enable_oauth: bool = True
    oauth_redirect_uri: str = "http://localhost:8080/callback"
    enable_caching: bool = True
    cache_ttl_seconds: int = 300  # 5 minutes

class SAPDatsphereMCPServer:
    """MCP Server for SAP Datasphere operations"""
    
    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.server = Server("sap-datasphere-mcp")
        
        # Initialize Datasphere connector
        self._init_datasphere_connector()
        
        # Cache for metadata operations
        self._metadata_cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        
        # Register MCP tools
        self._register_tools()
        
    def _init_datasphere_connector(self):
        """Initialize SAP Datasphere connector"""
        try:
            datasphere_config = DatasphereConfig(
                base_url=self.config.datasphere_base_url,
                environment_name=self.config.environment_name
            )
            
            self.datasphere_connector = DatasphereConnector(datasphere_config)
            logger.info("SAP Datasphere connector initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Datasphere connector: {str(e)}")
            raise
    
    def _register_tools(self):
        """Register MCP tools for AI integration"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List available MCP tools"""
            return [
                types.Tool(
                    name="discover_spaces",
                    description="Discover all available SAP Datasphere spaces",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "include_assets": {
                                "type": "boolean",
                                "description": "Include assets within each space",
                                "default": False
                            },
                            "force_refresh": {
                                "type": "boolean",
                                "description": "Force refresh from Datasphere (bypass cache)",
                                "default": False
                            }
                        }
                    }
                ),
                
                types.Tool(
                    name="search_assets",
                    description="Search for data assets in SAP Datasphere",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for asset names or descriptions"
                            },
                            "space_name": {
                                "type": "string",
                                "description": "Optional space name to limit search"
                            },
                            "asset_types": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Filter by asset types: TABLE, VIEW, ANALYTICAL_MODEL"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                
                types.Tool(
                    name="get_asset_details",
                    description="Get detailed information about a specific SAP Datasphere asset",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "space_name": {
                                "type": "string",
                                "description": "Name of the Datasphere space"
                            },
                            "asset_name": {
                                "type": "string",
                                "description": "Name of the asset"
                            },
                            "include_schema": {
                                "type": "boolean",
                                "description": "Include detailed schema information",
                                "default": True
                            }
                        },
                        "required": ["space_name", "asset_name"]
                    }
                ),
                
                types.Tool(
                    name="get_space_info",
                    description="Get detailed information about a specific SAP Datasphere space",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "space_name": {
                                "type": "string",
                                "description": "Name of the Datasphere space"
                            },
                            "include_tables": {
                                "type": "boolean",
                                "description": "Include table information",
                                "default": True
                            }
                        },
                        "required": ["space_name"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Handle MCP tool calls"""
            try:
                if name == "discover_spaces":
                    return await self._discover_spaces(arguments)
                elif name == "search_assets":
                    return await self._search_assets(arguments)
                elif name == "get_asset_details":
                    return await self._get_asset_details(arguments)
                elif name == "get_space_info":
                    return await self._get_space_info(arguments)
                else:
                    return [types.TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
                    
            except Exception as e:
                logger.error(f"Error executing tool {name}: {str(e)}")
                return [types.TextContent(
                    type="text",
                    text=f"Error executing {name}: {str(e)}"
                )]
    
    async def _discover_spaces(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Discover SAP Datasphere spaces"""
        include_assets = arguments.get("include_assets", False)
        force_refresh = arguments.get("force_refresh", False)
        
        cache_key = f"spaces_discovery_{include_assets}"
        
        # Check cache unless force refresh
        if not force_refresh and self._is_cache_valid(cache_key):
            spaces = self._metadata_cache[cache_key]
        else:
            try:
                # Discover spaces from Datasphere
                spaces = await asyncio.to_thread(self.datasphere_connector.discover_spaces)
                
                if include_assets:
                    for space in spaces:
                        space_name = space.get("name", "")
                        assets = await asyncio.to_thread(
                            self.datasphere_connector.discover_assets_in_space,
                            space_name
                        )
                        space["assets"] = assets
                
                # Cache results
                self._metadata_cache[cache_key] = spaces
                self._cache_timestamps[cache_key] = datetime.now()
                
            except Exception as e:
                logger.error(f"Error discovering spaces: {str(e)}")
                raise
        
        response = {
            "total_spaces": len(spaces),
            "spaces": spaces,
            "discovery_timestamp": datetime.now().isoformat()
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(response, indent=2)
        )]
    
    async def _search_assets(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Search for assets in SAP Datasphere"""
        query = arguments.get("query", "")
        space_name = arguments.get("space_name")
        asset_types = arguments.get("asset_types", [])
        
        try:
            # Get spaces to search
            if space_name:
                spaces_to_search = [{"name": space_name}]
            else:
                spaces_to_search = await asyncio.to_thread(self.datasphere_connector.discover_spaces)
            
            results = []
            
            for space in spaces_to_search:
                space_name = space.get("name", "")
                assets = await asyncio.to_thread(
                    self.datasphere_connector.discover_assets_in_space,
                    space_name
                )
                
                for asset in assets:
                    # Filter by query and asset types
                    if self._matches_search_criteria(asset, query, asset_types):
                        asset_info = {
                            "space": space_name,
                            "name": asset.get("name", ""),
                            "type": asset.get("type", ""),
                            "description": asset.get("description", ""),
                            "created_date": asset.get("createdAt", ""),
                            "modified_date": asset.get("modifiedAt", "")
                        }
                        results.append(asset_info)
            
            response = {
                "query": query,
                "total_results": len(results),
                "assets": results,
                "search_timestamp": datetime.now().isoformat()
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(response, indent=2)
            )]
            
        except Exception as e:
            logger.error(f"Error searching assets: {str(e)}")
            return [types.TextContent(
                type="text",
                text=f"Error searching assets: {str(e)}"
            )]
    
    async def _get_asset_details(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Get detailed asset information"""
        space_name = arguments.get("space_name", "")
        asset_name = arguments.get("asset_name", "")
        include_schema = arguments.get("include_schema", True)
        
        if not space_name or not asset_name:
            return [types.TextContent(
                type="text",
                text="Error: space_name and asset_name are required"
            )]
        
        try:
            # Get asset details from Datasphere
            asset_details = await asyncio.to_thread(
                self.datasphere_connector.get_asset_details,
                space_name,
                asset_name
            )
            
            # Add schema information if requested
            if include_schema:
                schema_info = await asyncio.to_thread(
                    self.datasphere_connector.get_asset_schema,
                    space_name,
                    asset_name
                )
                asset_details["schema"] = schema_info
            
            return [types.TextContent(
                type="text",
                text=json.dumps(asset_details, indent=2, default=str)
            )]
            
        except Exception as e:
            logger.error(f"Error getting asset details: {str(e)}")
            return [types.TextContent(
                type="text",
                text=f"Error getting asset details: {str(e)}"
            )]
    
    async def _get_space_info(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Get detailed space information"""
        space_name = arguments.get("space_name", "")
        include_tables = arguments.get("include_tables", True)
        
        if not space_name:
            return [types.TextContent(
                type="text",
                text="Error: space_name is required"
            )]
        
        try:
            # Get space information
            space_info = await asyncio.to_thread(
                self.datasphere_connector.get_space_info,
                space_name
            )
            
            if include_tables:
                tables = await asyncio.to_thread(
                    self.datasphere_connector.discover_assets_in_space,
                    space_name
                )
                space_info["tables"] = tables
            
            return [types.TextContent(
                type="text",
                text=json.dumps(space_info, indent=2, default=str)
            )]
            
        except Exception as e:
            logger.error(f"Error getting space info: {str(e)}")
            return [types.TextContent(
                type="text",
                text=f"Error getting space info: {str(e)}"
            )]
    
    def _matches_search_criteria(self, asset: Dict[str, Any], query: str, asset_types: List[str]) -> bool:
        """Check if asset matches search criteria"""
        # Check asset type filter
        if asset_types and asset.get("type", "").upper() not in [t.upper() for t in asset_types]:
            return False
        
        # Check query match
        if query:
            query_lower = query.lower()
            searchable_fields = [
                asset.get("name", ""),
                asset.get("description", ""),
                asset.get("type", "")
            ]
            
            if not any(query_lower in field.lower() for field in searchable_fields):
                return False
        
        return True
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid"""
        if not self.config.enable_caching:
            return False
        
        if cache_key not in self._cache_timestamps:
            return False
        
        cache_age = datetime.now() - self._cache_timestamps[cache_key]
        return cache_age.total_seconds() < self.config.cache_ttl_seconds

async def main():
    """Main entry point for MCP server"""
    config = MCPServerConfig()
    mcp_server = SAPDatsphereMCPServer(config)
    
    # Run the MCP server
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="sap-datasphere-mcp",
                server_version="1.0.0",
                capabilities=mcp_server.server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())