#!/usr/bin/env python3
"""
SAP Datasphere MCP Server for AI Integration
Provides Model Context Protocol server for AI-accessible metadata operations

This MCP server provides:
- Unified metadata search across Datasphere and AWS Glue
- Business context-aware data discovery
- Synchronization status monitoring
- Configuration management
- Data lineage visualization
- OAuth-enabled full asset access

Requirements: 6.1, 6.3, 6.5
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Sequence
from dataclasses import dataclass, asdict

# MCP imports
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp import types

# Import existing components
from enhanced_datasphere_connector import EnhancedDatasphereConnector
from enhanced_glue_connector import EnhancedGlueConnector, EnhancedGlueConfig
from datasphere_connector import DatasphereConfig
from metadata_sync_core import MetadataAsset, AssetType, SyncStatus
from sync_logging import SyncLogger, EventType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MCPServerConfig:
    """Configuration for MCP server"""
    datasphere_base_url: str = "https://ailien-test.eu10.hcs.cloud.sap"
    aws_region: str = "us-east-1"
    environment_name: str = "mcp"
    enable_oauth: bool = True
    oauth_redirect_uri: str = "http://localhost:8080/callback"
    enable_caching: bool = True
    cache_ttl_seconds: int = 300  # 5 minutes

class SAPDatsphereMCPServer:
    """MCP Server for SAP Datasphere metadata operations"""
    
    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.server = Server("sap-datasphere-mcp")
        self.logger = SyncLogger(f"mcp_server_{config.environment_name}")
        
        # Initialize connectors
        self._init_connectors()
        
        # Cache for metadata operations
        self._metadata_cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        
        # Register MCP tools
        self._register_tools()
        
    def _init_connectors(self):
        """Initialize Datasphere and Glue connectors"""
        try:
            # Initialize Datasphere connector with OAuth
            datasphere_config = DatasphereConfig(
                base_url=self.config.datasphere_base_url,
                environment_name=self.config.environment_name
            )
            
            self.datasphere_connector = EnhancedDatasphereConnector(
                config=datasphere_config,
                oauth_redirect_uri=self.config.oauth_redirect_uri,
                enable_oauth=self.config.enable_oauth
            )
            
            # Initialize Glue connector
            glue_config = EnhancedGlueConfig(
                region=self.config.aws_region,
                environment_name=self.config.environment_name
            )
            
            self.glue_connector = EnhancedGlueConnector(glue_config)
            
            self.logger.log_event(
                EventType.SYSTEM_STARTUP,
                "MCP Server connectors initialized successfully",
                {"datasphere_url": self.config.datasphere_base_url, "aws_region": self.config.aws_region}
            )
            
        except Exception as e:
            self.logger.log_event(
                EventType.ERROR,
                f"Failed to initialize connectors: {str(e)}",
                {"error": str(e)}
            )
            raise
    
    def _register_tools(self):
        """Register MCP tools for AI integration"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List available MCP tools"""
            return [
                types.Tool(
                    name="search_metadata",
                    description="Search for data assets across Datasphere and AWS Glue with business context",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for asset names, descriptions, or business context"
                            },
                            "asset_types": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Filter by asset types: TABLE, VIEW, ANALYTICAL_MODEL, SPACE"
                            },
                            "source_systems": {
                                "type": "array", 
                                "items": {"type": "string"},
                                "description": "Filter by source systems: DATASPHERE, GLUE"
                            },
                            "include_business_context": {
                                "type": "boolean",
                                "description": "Include business metadata and context",
                                "default": True
                            }
                        },
                        "required": ["query"]
                    }
                ),
                
                types.Tool(
                    name="get_asset_details",
                    description="Get detailed information about a specific data asset",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "asset_id": {
                                "type": "string",
                                "description": "Unique identifier of the asset"
                            },
                            "source_system": {
                                "type": "string",
                                "description": "Source system: DATASPHERE or GLUE"
                            },
                            "include_schema": {
                                "type": "boolean",
                                "description": "Include detailed schema information",
                                "default": True
                            },
                            "include_lineage": {
                                "type": "boolean", 
                                "description": "Include data lineage information",
                                "default": True
                            }
                        },
                        "required": ["asset_id", "source_system"]
                    }
                ),
                
                types.Tool(
                    name="discover_spaces",
                    description="Discover all available Datasphere spaces with OAuth authentication",
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
                    name="get_sync_status",
                    description="Get synchronization status between Datasphere and AWS Glue",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "asset_id": {
                                "type": "string",
                                "description": "Optional asset ID to check specific sync status"
                            },
                            "detailed": {
                                "type": "boolean",
                                "description": "Include detailed sync metrics and history",
                                "default": False
                            }
                        }
                    }
                ),
                
                types.Tool(
                    name="explore_data_lineage",
                    description="Explore data lineage relationships between assets",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "asset_id": {
                                "type": "string",
                                "description": "Starting asset ID for lineage exploration"
                            },
                            "direction": {
                                "type": "string",
                                "enum": ["upstream", "downstream", "both"],
                                "description": "Direction of lineage exploration",
                                "default": "both"
                            },
                            "max_depth": {
                                "type": "integer",
                                "description": "Maximum depth of lineage traversal",
                                "default": 3
                            }
                        },
                        "required": ["asset_id"]
                    }
                ),
                
                types.Tool(
                    name="trigger_sync",
                    description="Trigger metadata synchronization for specific assets or all assets",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "asset_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Specific asset IDs to sync (empty for all assets)"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["critical", "high", "medium", "low"],
                                "description": "Sync priority level",
                                "default": "medium"
                            },
                            "dry_run": {
                                "type": "boolean",
                                "description": "Preview sync operations without executing",
                                "default": False
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Handle MCP tool calls"""
            try:
                if name == "search_metadata":
                    return await self._search_metadata(arguments)
                elif name == "get_asset_details":
                    return await self._get_asset_details(arguments)
                elif name == "discover_spaces":
                    return await self._discover_spaces(arguments)
                elif name == "get_sync_status":
                    return await self._get_sync_status(arguments)
                elif name == "explore_data_lineage":
                    return await self._explore_data_lineage(arguments)
                elif name == "trigger_sync":
                    return await self._trigger_sync(arguments)
                else:
                    return [types.TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
                    
            except Exception as e:
                self.logger.log_event(
                    EventType.ERROR,
                    f"Error executing tool {name}: {str(e)}",
                    {"tool": name, "arguments": arguments, "error": str(e)}
                )
                return [types.TextContent(
                    type="text",
                    text=f"Error executing {name}: {str(e)}"
                )]
    
    async def _search_metadata(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Search for metadata assets across systems"""
        query = arguments.get("query", "")
        asset_types = arguments.get("asset_types", [])
        source_systems = arguments.get("source_systems", ["DATASPHERE", "GLUE"])
        include_business_context = arguments.get("include_business_context", True)
        
        results = []
        
        # Search Datasphere if requested
        if "DATASPHERE" in source_systems:
            try:
                # Use OAuth-enabled connector for full access
                datasphere_assets = await self._search_datasphere_assets(
                    query, asset_types, include_business_context
                )
                results.extend(datasphere_assets)
            except Exception as e:
                self.logger.log_event(
                    EventType.ERROR,
                    f"Error searching Datasphere: {str(e)}",
                    {"query": query, "error": str(e)}
                )
        
        # Search AWS Glue if requested
        if "GLUE" in source_systems:
            try:
                glue_assets = await self._search_glue_assets(
                    query, asset_types, include_business_context
                )
                results.extend(glue_assets)
            except Exception as e:
                self.logger.log_event(
                    EventType.ERROR,
                    f"Error searching Glue: {str(e)}",
                    {"query": query, "error": str(e)}
                )
        
        # Format results
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
    
    async def _search_datasphere_assets(self, query: str, asset_types: List[str], 
                                      include_business_context: bool) -> List[Dict[str, Any]]:
        """Search Datasphere assets using OAuth-enabled connector"""
        cache_key = f"datasphere_search_{query}_{','.join(asset_types)}"
        
        # Check cache
        if self._is_cache_valid(cache_key):
            return self._metadata_cache[cache_key]
        
        assets = []
        
        try:
            # Discover spaces with OAuth authentication
            spaces = await asyncio.to_thread(self.datasphere_connector.discover_spaces)
            
            for space in spaces:
                # Search within each space
                space_assets = await asyncio.to_thread(
                    self.datasphere_connector.discover_assets_in_space,
                    space.get("id", "")
                )
                
                for asset in space_assets:
                    # Filter by query and asset types
                    if self._matches_search_criteria(asset, query, asset_types):
                        asset_info = {
                            "id": asset.get("id", ""),
                            "name": asset.get("name", ""),
                            "type": asset.get("type", ""),
                            "space": space.get("name", ""),
                            "source_system": "DATASPHERE",
                            "description": asset.get("description", ""),
                            "created_date": asset.get("createdAt", ""),
                            "modified_date": asset.get("modifiedAt", "")
                        }
                        
                        # Add business context if requested
                        if include_business_context:
                            business_context = await self._get_business_context(asset)
                            asset_info["business_context"] = business_context
                        
                        assets.append(asset_info)
            
            # Cache results
            self._metadata_cache[cache_key] = assets
            self._cache_timestamps[cache_key] = datetime.now()
            
        except Exception as e:
            self.logger.log_event(
                EventType.ERROR,
                f"Error searching Datasphere assets: {str(e)}",
                {"query": query, "error": str(e)}
            )
            raise
        
        return assets
    
    async def _search_glue_assets(self, query: str, asset_types: List[str], 
                                include_business_context: bool) -> List[Dict[str, Any]]:
        """Search AWS Glue assets"""
        cache_key = f"glue_search_{query}_{','.join(asset_types)}"
        
        # Check cache
        if self._is_cache_valid(cache_key):
            return self._metadata_cache[cache_key]
        
        assets = []
        
        try:
            # Get all databases
            databases = await asyncio.to_thread(self.glue_connector.list_databases)
            
            for database in databases:
                # Get tables in database
                tables = await asyncio.to_thread(
                    self.glue_connector.list_tables,
                    database["Name"]
                )
                
                for table in tables:
                    # Filter by query and asset types
                    if self._matches_search_criteria(table, query, asset_types):
                        asset_info = {
                            "id": f"{database['Name']}.{table['Name']}",
                            "name": table["Name"],
                            "type": "TABLE",
                            "database": database["Name"],
                            "source_system": "GLUE",
                            "description": table.get("Description", ""),
                            "created_date": table.get("CreateTime", "").isoformat() if table.get("CreateTime") else "",
                            "modified_date": table.get("UpdateTime", "").isoformat() if table.get("UpdateTime") else ""
                        }
                        
                        # Add business context if requested
                        if include_business_context:
                            business_context = self._extract_glue_business_context(table)
                            asset_info["business_context"] = business_context
                        
                        assets.append(asset_info)
            
            # Cache results
            self._metadata_cache[cache_key] = assets
            self._cache_timestamps[cache_key] = datetime.now()
            
        except Exception as e:
            self.logger.log_event(
                EventType.ERROR,
                f"Error searching Glue assets: {str(e)}",
                {"query": query, "error": str(e)}
            )
            raise
        
        return assets
    
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
    
    async def _get_business_context(self, asset: Dict[str, Any]) -> Dict[str, Any]:
        """Extract business context from Datasphere asset"""
        try:
            # Get detailed asset information
            asset_details = await asyncio.to_thread(
                self.datasphere_connector.get_asset_details,
                asset.get("id", "")
            )
            
            return {
                "business_name": asset_details.get("businessName", ""),
                "domain": asset_details.get("domain", ""),
                "steward": asset_details.get("steward", ""),
                "certification_status": asset_details.get("certificationStatus", ""),
                "tags": asset_details.get("tags", []),
                "business_rules": asset_details.get("businessRules", [])
            }
        except Exception as e:
            self.logger.log_event(
                EventType.WARNING,
                f"Could not extract business context: {str(e)}",
                {"asset_id": asset.get("id", ""), "error": str(e)}
            )
            return {}
    
    def _extract_glue_business_context(self, table: Dict[str, Any]) -> Dict[str, Any]:
        """Extract business context from Glue table metadata"""
        parameters = table.get("Parameters", {})
        
        return {
            "business_name": parameters.get("business_name", ""),
            "domain": parameters.get("domain", ""),
            "steward": parameters.get("steward", ""),
            "certification_status": parameters.get("certification_status", ""),
            "source_system": parameters.get("source_system", ""),
            "sync_timestamp": parameters.get("sync_timestamp", "")
        }
    
    async def _discover_spaces(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Discover Datasphere spaces with OAuth authentication"""
        include_assets = arguments.get("include_assets", False)
        force_refresh = arguments.get("force_refresh", False)
        
        cache_key = f"spaces_discovery_{include_assets}"
        
        # Check cache unless force refresh
        if not force_refresh and self._is_cache_valid(cache_key):
            spaces = self._metadata_cache[cache_key]
        else:
            try:
                # Use OAuth-enabled connector for full access
                spaces = await asyncio.to_thread(self.datasphere_connector.discover_spaces)
                
                if include_assets:
                    for space in spaces:
                        space_id = space.get("id", "")
                        assets = await asyncio.to_thread(
                            self.datasphere_connector.discover_assets_in_space,
                            space_id
                        )
                        space["assets"] = assets
                
                # Cache results
                self._metadata_cache[cache_key] = spaces
                self._cache_timestamps[cache_key] = datetime.now()
                
            except Exception as e:
                self.logger.log_event(
                    EventType.ERROR,
                    f"Error discovering spaces: {str(e)}",
                    {"error": str(e)}
                )
                raise
        
        response = {
            "total_spaces": len(spaces),
            "spaces": spaces,
            "discovery_timestamp": datetime.now().isoformat(),
            "oauth_enabled": self.config.enable_oauth
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(response, indent=2)
        )]
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid"""
        if not self.config.enable_caching:
            return False
        
        if cache_key not in self._cache_timestamps:
            return False
        
        cache_age = datetime.now() - self._cache_timestamps[cache_key]
        return cache_age.total_seconds() < self.config.cache_ttl_seconds
    
    async def _get_asset_details(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Get detailed asset information"""
        asset_id = arguments.get("asset_id", "")
        source_system = arguments.get("source_system", "")
        include_schema = arguments.get("include_schema", True)
        include_lineage = arguments.get("include_lineage", True)
        
        if not asset_id or not source_system:
            return [types.TextContent(
                type="text",
                text="Error: asset_id and source_system are required"
            )]
        
        try:
            if source_system.upper() == "DATASPHERE":
                details = await asyncio.to_thread(
                    self.datasphere_connector.get_asset_details,
                    asset_id
                )
            elif source_system.upper() == "GLUE":
                # Parse database.table format
                if "." in asset_id:
                    database_name, table_name = asset_id.split(".", 1)
                    details = await asyncio.to_thread(
                        self.glue_connector.get_table_details,
                        database_name,
                        table_name
                    )
                else:
                    return [types.TextContent(
                        type="text",
                        text="Error: Glue asset_id must be in format 'database.table'"
                    )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"Error: Unknown source system '{source_system}'"
                )]
            
            # Add schema information if requested
            if include_schema and source_system.upper() == "DATASPHERE":
                schema_info = await asyncio.to_thread(
                    self.datasphere_connector.get_asset_schema,
                    asset_id
                )
                details["schema"] = schema_info
            
            # Add lineage information if requested
            if include_lineage:
                lineage_info = await self._get_asset_lineage(asset_id, source_system)
                details["lineage"] = lineage_info
            
            return [types.TextContent(
                type="text",
                text=json.dumps(details, indent=2, default=str)
            )]
            
        except Exception as e:
            self.logger.log_event(
                EventType.ERROR,
                f"Error getting asset details: {str(e)}",
                {"asset_id": asset_id, "source_system": source_system, "error": str(e)}
            )
            return [types.TextContent(
                type="text",
                text=f"Error getting asset details: {str(e)}"
            )]
    
    async def _get_asset_lineage(self, asset_id: str, source_system: str) -> Dict[str, Any]:
        """Get lineage information for an asset"""
        # Placeholder for lineage implementation
        return {
            "upstream_assets": [],
            "downstream_assets": [],
            "lineage_depth": 0,
            "last_updated": datetime.now().isoformat()
        }
    
    async def _get_sync_status(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Get synchronization status"""
        asset_id = arguments.get("asset_id")
        detailed = arguments.get("detailed", False)
        
        # Placeholder for sync status implementation
        status = {
            "overall_sync_status": "HEALTHY",
            "last_sync_timestamp": datetime.now().isoformat(),
            "total_assets_synced": 0,
            "sync_errors": 0,
            "pending_syncs": 0
        }
        
        if asset_id:
            status["asset_id"] = asset_id
            status["asset_sync_status"] = "SYNCED"
            status["last_asset_sync"] = datetime.now().isoformat()
        
        if detailed:
            status["sync_history"] = []
            status["error_details"] = []
            status["performance_metrics"] = {}
        
        return [types.TextContent(
            type="text",
            text=json.dumps(status, indent=2)
        )]
    
    async def _explore_data_lineage(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Explore data lineage relationships"""
        asset_id = arguments.get("asset_id", "")
        direction = arguments.get("direction", "both")
        max_depth = arguments.get("max_depth", 3)
        
        # Placeholder for lineage exploration implementation
        lineage = {
            "root_asset_id": asset_id,
            "direction": direction,
            "max_depth": max_depth,
            "lineage_graph": {
                "nodes": [],
                "edges": []
            },
            "exploration_timestamp": datetime.now().isoformat()
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(lineage, indent=2)
        )]
    
    async def _trigger_sync(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Trigger metadata synchronization"""
        asset_ids = arguments.get("asset_ids", [])
        priority = arguments.get("priority", "medium")
        dry_run = arguments.get("dry_run", False)
        
        # Placeholder for sync trigger implementation
        result = {
            "sync_triggered": not dry_run,
            "dry_run": dry_run,
            "priority": priority,
            "asset_count": len(asset_ids) if asset_ids else "all",
            "estimated_duration": "5-10 minutes",
            "sync_id": f"sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat()
        }
        
        if dry_run:
            result["preview"] = {
                "assets_to_sync": asset_ids or ["all_assets"],
                "operations": ["discover", "extract", "transform", "load"],
                "estimated_changes": 0
            }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

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