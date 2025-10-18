#!/usr/bin/env python3
"""
Production SAP Datasphere MCP Server
Based on successful consumption API discovery
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

class ProductionDatasphereMCPServer:
    """Production MCP Server with working SAP Datasphere Consumption APIs"""
    
    def __init__(self):
        self.server = Server("sap-datasphere-production-mcp")
        self.client = None
        self.access_token = None
        self.token_expires_at = None
        
        # Working API configuration
        self.config = {
            "tenant_url": "https://ailien-test.eu20.hcs.cloud.sap",
            "oauth_config": {
                "client_id": "sb-1d624427-f63c-4be1-8066-eee88b15ce05!b130936|client!b3944",
                "client_secret": "d3b8e5eb-d53f-4098-8f02-cc5457d39853$d49IM8txqwwEdMzEeWdRLOuCpzjUYSwAFQcptIVAT1o=",
                "token_url": "https://ailien-test.authentication.eu20.hana.ondemand.com/oauth/token"
            },
            # Working endpoints discovered
            "working_endpoints": {
                "analytic_model_data": "/api/v1/datasphere/consumption/analytical/SAP_CONTENT/New_Analytic_Model_2/New_Analytic_Model_2",
                "analytic_model_service": "/api/v1/datasphere/consumption/analytical/SAP_CONTENT/New_Analytic_Model_2",
                "analytic_model_metadata": "/api/v1/datasphere/consumption/analytical/SAP_CONTENT/New_Analytic_Model_2/$metadata"
            }
        }
        
        # Setup tools
        self._setup_tools()
    
    def _setup_tools(self):
        """Setup MCP tools with working endpoints"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            return [
                types.Tool(
                    name="get_analytical_model_data",
                    description="Get data from SAP Datasphere analytical model (New_Analytic_Model_2)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "top": {
                                "type": "integer",
                                "description": "Number of records to return (OData $top parameter)",
                                "default": 100
                            },
                            "skip": {
                                "type": "integer", 
                                "description": "Number of records to skip (OData $skip parameter)",
                                "default": 0
                            },
                            "filter": {
                                "type": "string",
                                "description": "OData filter expression (optional)"
                            },
                            "select": {
                                "type": "string",
                                "description": "Comma-separated list of fields to select (optional)"
                            }
                        }
                    }
                ),
                types.Tool(
                    name="get_analytical_model_info",
                    description="Get information about the SAP Datasphere analytical model service",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="get_analytical_model_metadata",
                    description="Get metadata schema for the SAP Datasphere analytical model",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="test_datasphere_connection",
                    description="Test connection to SAP Datasphere and show authentication status",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> List[types.TextContent]:
            try:
                if name == "get_analytical_model_data":
                    return await self._get_analytical_model_data(arguments)
                elif name == "get_analytical_model_info":
                    return await self._get_analytical_model_info(arguments)
                elif name == "get_analytical_model_metadata":
                    return await self._get_analytical_model_metadata(arguments)
                elif name == "test_datasphere_connection":
                    return await self._test_datasphere_connection(arguments)
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
            
            # Get OAuth token
            auth_string = f"{self.config['oauth_config']['client_id']}:{self.config['oauth_config']['client_secret']}"
            auth_b64 = base64.b64encode(auth_string.encode('ascii')).decode('ascii')
            
            headers = {
                'Authorization': f'Basic {auth_b64}',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
            
            data = {'grant_type': 'client_credentials'}
            
            response = await self.client.post(
                self.config['oauth_config']['token_url'], 
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
    
    async def _make_odata_request(self, endpoint: str, params: dict = None) -> tuple:
        """Make OData request to SAP Datasphere"""
        if not await self._ensure_authenticated():
            return None, "Authentication failed"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json;odata.metadata=minimal',
            'Content-Type': 'application/json',
            'OData-Version': '4.0',
            'OData-MaxVersion': '4.0'
        }
        
        try:
            url = self.config['tenant_url'] + endpoint
            response = await self.client.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'application/json' in content_type:
                    return response.json(), None
                else:
                    return response.text, None
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                logger.error(f"❌ OData request failed: {error_msg}")
                return None, error_msg
                
        except Exception as e:
            logger.error(f"❌ Request error: {e}")
            return None, str(e)
    
    async def _get_analytical_model_data(self, arguments: dict) -> List[types.TextContent]:
        """Get data from analytical model"""
        top = arguments.get('top', 100)
        skip = arguments.get('skip', 0)
        filter_expr = arguments.get('filter')
        select_fields = arguments.get('select')
        
        # Build OData query parameters
        params = {
            '$top': top,
            '$skip': skip
        }
        
        if filter_expr:
            params['$filter'] = filter_expr
        if select_fields:
            params['$select'] = select_fields
        
        data, error = await self._make_odata_request(
            self.config['working_endpoints']['analytic_model_data'],
            params
        )
        
        if error:
            return [types.TextContent(
                type="text",
                text=f"❌ Failed to get analytical model data: {error}"
            )]
        
        # Format response
        result = f"📊 **SAP Datasphere Analytical Model Data**\n\n"
        
        if isinstance(data, dict):
            # OData response
            context = data.get('@odata.context', 'Unknown')
            values = data.get('value', [])
            next_link = data.get('@odata.nextLink')
            
            result += f"**OData Context:** {context}\n"
            result += f"**Records Returned:** {len(values)}\n"
            
            if next_link:
                result += f"**Next Link:** Available (more data exists)\n"
            
            result += f"\n**Data:**\n"
            if values:
                result += f"```json\n{json.dumps(values, indent=2)}\n```"
            else:
                result += "No records found (empty result set)"
                
            # Add query info
            result += f"\n\n**Query Parameters:**\n"
            result += f"• Top: {top}\n"
            result += f"• Skip: {skip}\n"
            if filter_expr:
                result += f"• Filter: {filter_expr}\n"
            if select_fields:
                result += f"• Select: {select_fields}\n"
        else:
            result += f"```\n{str(data)}\n```"
        
        return [types.TextContent(type="text", text=result)]
    
    async def _get_analytical_model_info(self, arguments: dict) -> List[types.TextContent]:
        """Get analytical model service information"""
        data, error = await self._make_odata_request(
            self.config['working_endpoints']['analytic_model_service']
        )
        
        if error:
            return [types.TextContent(
                type="text",
                text=f"❌ Failed to get model info: {error}"
            )]
        
        result = f"📋 **SAP Datasphere Analytical Model Service Info**\n\n"
        
        if isinstance(data, dict):
            context = data.get('@odata.context', 'Unknown')
            values = data.get('value', [])
            
            result += f"**OData Context:** {context}\n"
            result += f"**Service Entities:** {len(values)}\n\n"
            
            if values:
                result += f"**Available Entities:**\n"
                for entity in values:
                    name = entity.get('name', 'Unknown')
                    url = entity.get('url', 'Unknown')
                    result += f"• **{name}**: {url}\n"
            
            result += f"\n**Raw Response:**\n"
            result += f"```json\n{json.dumps(data, indent=2)}\n```"
        else:
            result += f"```\n{str(data)}\n```"
        
        return [types.TextContent(type="text", text=result)]
    
    async def _get_analytical_model_metadata(self, arguments: dict) -> List[types.TextContent]:
        """Get analytical model metadata"""
        # Try metadata endpoint with XML accept header
        if not await self._ensure_authenticated():
            return [types.TextContent(
                type="text",
                text="❌ Authentication failed"
            )]
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/xml, application/json, text/xml, */*',
            'Content-Type': 'application/json'
        }
        
        try:
            url = self.config['tenant_url'] + self.config['working_endpoints']['analytic_model_metadata']
            response = await self.client.get(url, headers=headers)
            
            result = f"📋 **SAP Datasphere Analytical Model Metadata**\n\n"
            result += f"**Endpoint:** {self.config['working_endpoints']['analytic_model_metadata']}\n"
            result += f"**Status:** HTTP {response.status_code}\n"
            result += f"**Content-Type:** {response.headers.get('content-type', 'Unknown')}\n\n"
            
            if response.status_code == 200:
                result += f"**Metadata Schema:**\n"
                result += f"```xml\n{response.text[:2000]}...\n```"
            else:
                result += f"**Error Response:**\n"
                result += f"```\n{response.text[:500]}\n```"
                
        except Exception as e:
            result = f"❌ Failed to get metadata: {str(e)}"
        
        return [types.TextContent(type="text", text=result)]
    
    async def _test_datasphere_connection(self, arguments: dict) -> List[types.TextContent]:
        """Test connection to SAP Datasphere"""
        result = f"🔍 **SAP Datasphere Connection Test**\n\n"
        
        # Test authentication
        auth_success = await self._ensure_authenticated()
        result += f"**Authentication:** {'✅ Success' if auth_success else '❌ Failed'}\n"
        
        if auth_success:
            result += f"**OAuth Token:** Valid (expires at {self.token_expires_at})\n"
            result += f"**Tenant URL:** {self.config['tenant_url']}\n\n"
            
            # Test each working endpoint
            result += f"**Endpoint Tests:**\n"
            
            for endpoint_name, endpoint_path in self.config['working_endpoints'].items():
                try:
                    data, error = await self._make_odata_request(endpoint_path)
                    if error:
                        result += f"• {endpoint_name}: ❌ {error}\n"
                    else:
                        result += f"• {endpoint_name}: ✅ Working\n"
                except Exception as e:
                    result += f"• {endpoint_name}: ❌ {str(e)}\n"
            
            result += f"\n**Configuration:**\n"
            result += f"• Client ID: {self.config['oauth_config']['client_id'][:50]}...\n"
            result += f"• Token URL: {self.config['oauth_config']['token_url']}\n"
        
        return [types.TextContent(type="text", text=result)]
    
    async def run(self):
        """Run the production MCP server"""
        from mcp.server.stdio import stdio_server
        
        logger.info("🚀 Starting Production SAP Datasphere MCP Server")
        logger.info(f"📡 Tenant: {self.config['tenant_url']}")
        logger.info(f"🔧 Working Endpoints: {len(self.config['working_endpoints'])}")
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="sap-datasphere-production-mcp",
                    server_version="2.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None,
                    ),
                ),
            )

def main():
    """Main entry point"""
    server = ProductionDatasphereMCPServer()
    asyncio.run(server.run())

if __name__ == "__main__":
    main()