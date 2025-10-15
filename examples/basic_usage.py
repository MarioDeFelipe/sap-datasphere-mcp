"""
Basic usage example for SAP Datasphere MCP Server
"""

import asyncio
import os
from dotenv import load_dotenv

from sap_datasphere_mcp.models import DatasphereConfig
from sap_datasphere_mcp.client import DatasphereClient

# Load environment variables
load_dotenv()


async def main():
    """Example usage of the Datasphere client"""
    
    # Create configuration
    config = DatasphereConfig(
        tenant_url=os.getenv("DATASPHERE_TENANT_URL"),
        tenant_id=os.getenv("DATASPHERE_TENANT_ID", "default"),
        oauth_client_id=os.getenv("OAUTH_CLIENT_ID"),
        oauth_client_secret=os.getenv("OAUTH_CLIENT_SECRET"),
        oauth_token_url=os.getenv("OAUTH_TOKEN_URL")
    )
    
    # Create client
    client = DatasphereClient(config)
    
    try:
        # Test connection
        print("🔐 Testing connection...")
        result = await client.test_connection()
        if result.success:
            print("✅ Connection successful!")
        else:
            print(f"❌ Connection failed: {result.error}")
            return
        
        # Discover API endpoints
        print("\n🔍 Discovering API endpoints...")
        result = await client.discover_api_endpoints()
        if result.success:
            endpoints = result.data["working_endpoints"]
            print(f"Found {len(endpoints)} working endpoints:")
            for ep in endpoints:
                print(f"  • {ep['endpoint']}")
        
        # List spaces
        print("\n🏢 Listing spaces...")
        result = await client.list_spaces()
        if result.success:
            spaces = result.data
            print(f"Found {len(spaces)} spaces:")
            for space in spaces:
                print(f"  • {space['name']} (ID: {space['id']})")
        else:
            print(f"❌ Failed to list spaces: {result.error}")
        
        # List catalog
        print("\n📊 Listing catalog...")
        result = await client.list_catalog()
        if result.success:
            items = result.data
            print(f"Found {len(items)} catalog items:")
            for item in items[:5]:  # Show first 5
                print(f"  • {item['name']} ({item['type']})")
            if len(items) > 5:
                print(f"  ... and {len(items) - 5} more items")
        else:
            print(f"❌ Failed to list catalog: {result.error}")
    
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())