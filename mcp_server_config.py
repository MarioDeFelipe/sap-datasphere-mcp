#!/usr/bin/env python3
"""
SAP Datasphere MCP Server Configuration
Simple configuration helper for the MCP server
"""

import os
import json
from typing import Dict, Any

def get_config_from_env() -> Dict[str, Any]:
    """Get configuration from environment variables"""
    return {
        "datasphere_base_url": os.getenv('DATASPHERE_BASE_URL', 'https://your-tenant.eu10.hcs.cloud.sap'),
        "client_id": os.getenv('SAP_CLIENT_ID'),
        "client_secret": os.getenv('SAP_CLIENT_SECRET'),
        "token_url": os.getenv('SAP_TOKEN_URL'),
        "environment_name": os.getenv('MCP_ENVIRONMENT', 'mcp'),
        "enable_oauth": bool(os.getenv('SAP_CLIENT_ID') and os.getenv('SAP_CLIENT_SECRET')),
        "enable_caching": os.getenv('MCP_ENABLE_CACHING', 'true').lower() == 'true',
        "cache_ttl_seconds": int(os.getenv('MCP_CACHE_TTL', '300'))
    }

def print_config_help():
    """Print configuration help"""
    print("""
SAP Datasphere MCP Server Configuration

Environment Variables:
  DATASPHERE_BASE_URL    - Your SAP Datasphere tenant URL
  SAP_CLIENT_ID          - OAuth client ID (optional)
  SAP_CLIENT_SECRET      - OAuth client secret (optional)  
  SAP_TOKEN_URL          - OAuth token endpoint (optional)
  MCP_ENVIRONMENT        - Environment name (default: mcp)
  MCP_ENABLE_CACHING     - Enable caching (default: true)
  MCP_CACHE_TTL          - Cache TTL in seconds (default: 300)

Example:
  export DATASPHERE_BASE_URL="https://your-tenant.eu10.hcs.cloud.sap"
  export SAP_CLIENT_ID="your_oauth_client_id"
  export SAP_CLIENT_SECRET="your_oauth_client_secret"
  export SAP_TOKEN_URL="https://your-tenant.authentication.eu10.hana.ondemand.com/oauth/token"

Without OAuth credentials, the server will run in mock mode with sample data.
""")

if __name__ == "__main__":
    print_config_help()
    
    print("\nCurrent Configuration:")
    config = get_config_from_env()
    for key, value in config.items():
        if 'secret' in key.lower():
            value = '***' if value else None
        print(f"  {key}: {value}")