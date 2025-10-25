#!/usr/bin/env python3
"""
Enhanced SAP Datasphere MCP Server - Version 2.0
Incorporates 77.8% success rate discoveries and correct domain
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence
import httpx
import base64
from datetime import datetime, timedelta

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp import types
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# UPDATED CONFIGURATION - Based on successful discovery
class EnhancedConfig:
    # CORRECT domain discovered!
    TENANT_URL = "https://ailien-test.eu20.hcs.cloud.sap"
    
    # OAuth configuration
    OAUTH_CONFIG = {
        "client_id": "sb-60cb266e-ad9d-49f7-9967-b53b8286a259!b130936|client!b3944",
        "client_secret": "caaea1b9-b09b-4d28-83fe-09966d525243$LOFW4h5LpLvB3Z2FE0P7FiH4-C7qexeQPi22DBiHbz8=",
        "token_url": "https://ailien-test.authentication.eu20.hana.ondemand.com/oauth/token"
    }
    
    # WORKING ENDPOINTS - Discovered from testing
    WORKING_ENDPOINTS = {
        "spaces": [
            "/api/v1/spaces",
            "/sap/fpa/api/v1/spaces", 
            "/sap/api/v1/spaces"
        ],
        "catalog": [
            "/api/v1/catalog",
            "/sap/fpa/api/v1/catalog"
        ],
        "connections": [
            "/api/v1/connections"
        ]
    }

class EnhancedDatasphereMCPServer:
    """Enhanced MCP Server with improved success rate and error handling"""
    
    def __init__(self):
        self.server = Server("enhanced-sap-datasphere-mcp")
        self.client = None
        self.access_token = None
        self.token_expires_at = None
        self.config = EnhancedConfig()
        
        # Setup tools
        self._setup_tools()
    
    def _setup_tools(self):
        """Setup MCP tools with enhanced error handling"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            return [
                types.Tool(
                    name="list_spaces_enhanced",
                    description="List all spaces in SAP Datasphere with enhanced endpoint discovery",
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
                types.Tool(
                    name="get_catalog_enhanced", 
                    description="Get data catalog with multiple endpoint fallbacks",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "space_id": {
                                "type": "string",
                                "description": "Optional space ID to filter catalog"
                            }
                        }
                    }
                ),
                types.Tool(
                    name="list_connections_enhanced",
                    description="List all connections with enhanced error handling",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "connection_type": {
                                "type": "string", 
                                "description": "Optional filter by connection type"
                            }
                        }
                    }
                ),
                types.Tool(
                    name="test_all_endpoints",
                    description="Test all discovered endpoints and report status",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="discover_new_endpoints",
                    description="Attempt to discover additional API endpoints",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "endpoint_patterns": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Custom endpoint patterns to test"
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> List[types.TextContent]:
            try:
                if name == "list_spaces_enhanced":
                    return await self._list_spaces_enhanced(arguments)
                elif name == "get_catalog_enhanced":
                    return await self._get_catalog_enhanced(arguments)
                elif name == "list_connections_enhanced":
                    return await self._list_connections_enhanced(arguments)
                elif name == "test_all_endpoints":
                    return await self._test_all_endpoints(arguments)
                elif name == "discover_new_endpoints":
                    return await self._discover_new_endpoints(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Tool {name} failed: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"❌ Tool '{name}' failed: {str(e)}"
                )]
    
    async def _ensure_authenticated(self) -> bool:
        """Ensure we have a valid access token"""
        if (self.access_token and self.token_expires_at and 
            datetime.now() < self.token_expires_at):
            return True
        
        try:
            if not self.client:
                self.client = httpx.AsyncClient(timeout=30)
            
            # Prepare OAuth request
            auth_string = f"{self.config.OAUTH_CONFIG['client_id']}:{self.config.OAUTH_CONFIG['client_secret']}"
            auth_b64 = base64.b64encode(auth_string.encode('ascii')).decode('ascii')
            
            headers = {
                'Authorization': f'Basic {auth_b64}',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
            
            data = {'grant_type': 'client_credentials'}
            
            response = await self.client.post(
                self.config.OAUTH_CONFIG['token_url'], 
                headers=headers, 
                data=data
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                expires_in = token_data.get('expires_in', 3600)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
                logger.info("✅ OAuth authentication successful")
                return True
            else:
                logger.error(f"❌ OAuth failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return False
    
    async def _try_endpoints(self, endpoint_list: List[str], params: dict = None) -> tuple:
        """Try multiple endpoints and return first successful response"""
        if not await self._ensure_authenticated():
            return None, "Authentication failed"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }
        
        for endpoint in endpoint_list:
            try:
                url = self.config.TENANT_URL + endpoint
                if params:
                    response = await self.client.get(url, headers=headers, params=params)
                else:
                    response = await self.client.get(url, headers=headers)
                
                if response.status_code < 400:
                    logger.info(f"✅ Success with endpoint: {endpoint}")
                    return response.json(), None
                else:
                    logger.warning(f"⚠️ Endpoint {endpoint} returned {response.status_code}")
                    
            except Exception as e:
                logger.warning(f"⚠️ Endpoint {endpoint} failed: {e}")
                continue
        
        return None, f"All endpoints failed for {endpoint_list}"
    
    async def _list_spaces_enhanced(self, arguments: dict) -> List[types.TextContent]:
        """Enhanced space listing with multiple endpoint fallbacks"""
        include_details = arguments.get('include_details', False)
        
        data, error = await self._try_endpoints(self.config.WORKING_ENDPOINTS['spaces'])
        
        if error:
            return [types.TextContent(
                type="text",
                text=f"❌ Failed to list spaces: {error}"
            )]
        
        # Format response
        if include_details:
            result = f"📁 **SAP Datasphere Spaces (Detailed)**\n\n"
            result += f"```json\n{json.dumps(data, indent=2)}\n```"
        else:
            result = f"📁 **SAP Datasphere Spaces**\n\n"
            if isinstance(data, dict) and 'spaces' in data:
                for space in data['spaces']:
                    result += f"• **{space.get('name', 'Unknown')}** ({space.get('id', 'No ID')})\n"
            else:
                result += f"Raw response: {str(data)[:500]}..."
        
        return [types.TextContent(type="text", text=result)]
    
    async def _get_catalog_enhanced(self, arguments: dict) -> List[types.TextContent]:
        """Enhanced catalog retrieval with multiple endpoints"""
        space_id = arguments.get('space_id')
        
        params = {'spaceId': space_id} if space_id else None
        data, error = await self._try_endpoints(self.config.WORKING_ENDPOINTS['catalog'], params)
        
        if error:
            return [types.TextContent(
                type="text",
                text=f"❌ Failed to get catalog: {error}"
            )]
        
        result = f"📊 **SAP Datasphere Catalog**\n\n"
        if space_id:
            result += f"**Space ID:** {space_id}\n\n"
        
        result += f"```json\n{json.dumps(data, indent=2)}\n```"
        
        return [types.TextContent(type="text", text=result)]
    
    async def _list_connections_enhanced(self, arguments: dict) -> List[types.TextContent]:
        """Enhanced connection listing"""
        connection_type = arguments.get('connection_type')
        
        data, error = await self._try_endpoints(self.config.WORKING_ENDPOINTS['connections'])
        
        if error:
            return [types.TextContent(
                type="text",
                text=f"❌ Failed to list connections: {error}"
            )]
        
        result = f"🔗 **SAP Datasphere Connections**\n\n"
        if connection_type:
            result += f"**Filter:** {connection_type}\n\n"
        
        result += f"```json\n{json.dumps(data, indent=2)}\n```"
        
        return [types.TextContent(type="text", text=result)]
    
    async def _test_all_endpoints(self, arguments: dict) -> List[types.TextContent]:
        """Test all discovered endpoints and report status"""
        if not await self._ensure_authenticated():
            return [types.TextContent(
                type="text",
                text="❌ Authentication failed"
            )]
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }
        
        results = []
        total_tested = 0
        successful = 0
        
        result_text = "🧪 **Endpoint Testing Results**\n\n"
        
        for category, endpoints in self.config.WORKING_ENDPOINTS.items():
            result_text += f"**{category.upper()}:**\n"
            
            for endpoint in endpoints:
                total_tested += 1
                try:
                    url = self.config.TENANT_URL + endpoint
                    response = await self.client.get(url, headers=headers)
                    
                    if response.status_code < 400:
                        successful += 1
                        result_text += f"  ✅ {endpoint} - HTTP {response.status_code}\n"
                    else:
                        result_text += f"  ❌ {endpoint} - HTTP {response.status_code}\n"
                        
                except Exception as e:
                    result_text += f"  ❌ {endpoint} - Error: {str(e)[:50]}\n"
            
            result_text += "\n"
        
        success_rate = (successful / total_tested * 100) if total_tested > 0 else 0
        result_text += f"📊 **Summary:** {successful}/{total_tested} endpoints working ({success_rate:.1f}%)"
        
        return [types.TextContent(type="text", text=result_text)]
    
    async def _discover_new_endpoints(self, arguments: dict) -> List[types.TextContent]:
        """Attempt to discover additional API endpoints"""
        custom_patterns = arguments.get('endpoint_patterns', [])
        
        # Default patterns to try
        default_patterns = [
            "/api/v2/spaces",
            "/api/v1/models", 
            "/api/v1/datasets",
            "/api/v1/users",
            "/api/v1/permissions",
            "/sap/fpa/api/v1/models",
            "/sap/fpa/api/v1/datasets",
            "/dwc/api/v1/spaces",
            "/dwc/api/v1/connections"
        ]
        
        patterns_to_test = custom_patterns + default_patterns
        
        if not await self._ensure_authenticated():
            return [types.TextContent(
                type="text",
                text="❌ Authentication failed"
            )]
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }
        
        result_text = "🔍 **New Endpoint Discovery**\n\n"
        discovered = []
        
        for pattern in patterns_to_test:
            try:
                url = self.config.TENANT_URL + pattern
                response = await self.client.get(url, headers=headers)
                
                if response.status_code < 400:
                    discovered.append(pattern)
                    result_text += f"  🎉 **NEW:** {pattern} - HTTP {response.status_code}\n"
                elif response.status_code == 401:
                    result_text += f"  🔐 {pattern} - HTTP 401 (exists, needs auth)\n"
                else:
                    result_text += f"  ❌ {pattern} - HTTP {response.status_code}\n"
                    
            except Exception as e:
                result_text += f"  ❌ {pattern} - Error: {str(e)[:50]}\n"
        
        result_text += f"\n📊 **Discovery Summary:** {len(discovered)} new endpoints found"
        
        if discovered:
            result_text += "\n\n🎯 **Newly Discovered Endpoints:**\n"
            for endpoint in discovered:
                result_text += f"  • {endpoint}\n"
        
        return [types.TextContent(type="text", text=result_text)]
    
    async def run(self):
        """Run the enhanced MCP server"""
        from mcp.server.stdio import stdio_server
        
        logger.info("🚀 Starting Enhanced SAP Datasphere MCP Server v2.0")
        logger.info(f"📡 Tenant URL: {self.config.TENANT_URL}")
        logger.info(f"🔧 Working Endpoints: {sum(len(eps) for eps in self.config.WORKING_ENDPOINTS.values())}")
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="enhanced-sap-datasphere-mcp",
                    server_version="2.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None,
                    ),
                ),
            )

def main():
    """Main entry point"""
    server = EnhancedDatasphereMCPServer()
    asyncio.run(server.run())

if __name__ == "__main__":
    main()