#!/usr/bin/env python3
"""
SAP Datasphere MCP Server Launcher
Simple launcher script for the SAP Datasphere MCP server
"""

import os
import sys
from sap_datasphere_mcp_server import main, MCPServerConfig

def configure_server():
    """Configure the MCP server from environment variables"""
    config = MCPServerConfig()
    
    # Override with environment variables if provided
    if os.getenv('DATASPHERE_BASE_URL'):
        config.datasphere_base_url = os.getenv('DATASPHERE_BASE_URL')
    
    if os.getenv('MCP_ENVIRONMENT'):
        config.environment_name = os.getenv('MCP_ENVIRONMENT')
    
    # OAuth configuration
    if os.getenv('SAP_CLIENT_ID') and os.getenv('SAP_CLIENT_SECRET'):
        config.enable_oauth = True
    
    return config

if __name__ == "__main__":
    # Configure and start the server
    import asyncio
    
    print("🚀 Starting SAP Datasphere MCP Server...")
    print("📡 Listening for MCP client connections...")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 SAP Datasphere MCP Server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)