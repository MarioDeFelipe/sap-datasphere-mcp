#!/usr/bin/env python3
"""
Setup script to configure SAP Datasphere MCP Server credentials
"""

import os
import shutil
from pathlib import Path


def setup_credentials():
    """Interactive setup for SAP Datasphere credentials"""
    
    print("🚀 SAP Datasphere MCP Server Setup")
    print("=" * 50)
    
    # Check if .env already exists
    env_file = Path(".env")
    if env_file.exists():
        response = input("⚠️ .env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
    
    print("\n📝 Please provide your SAP Datasphere credentials:")
    print("(You can find these in your SAP Datasphere Admin Console > OAuth Clients)")
    
    # Collect credentials
    tenant_url = input("\n🌐 Datasphere Tenant URL: ").strip()
    if not tenant_url.startswith('http'):
        tenant_url = f"https://{tenant_url}"
    
    client_id = input("🔑 OAuth Client ID: ").strip()
    client_secret = input("🔐 OAuth Client Secret: ").strip()
    token_url = input("🎫 OAuth Token URL: ").strip()
    
    # Optional fields
    print("\n📋 Optional configuration (press Enter to skip):")
    auth_url = input("🔗 OAuth Authorization URL: ").strip()
    log_level = input("📊 Log Level (INFO): ").strip() or "INFO"
    
    # Extract tenant ID from URL
    try:
        tenant_id = tenant_url.split("//")[1].split(".")[0]
    except:
        tenant_id = input("🏢 Tenant ID (extracted from URL): ").strip()
    
    # Create .env content
    env_content = f"""# SAP Datasphere Configuration
DATASPHERE_TENANT_URL={tenant_url}
DATASPHERE_TENANT_ID={tenant_id}

# OAuth 2.0 Credentials
OAUTH_CLIENT_ID={client_id}
OAUTH_CLIENT_SECRET={client_secret}
OAUTH_TOKEN_URL={token_url}
"""
    
    if auth_url:
        env_content += f"OAUTH_AUTHORIZATION_URL={auth_url}\n"
    
    env_content += f"""
# Optional Configuration
LOG_LEVEL={log_level}
API_TIMEOUT=30
API_RETRY_COUNT=3
"""
    
    # Write .env file
    with open(".env", "w") as f:
        f.write(env_content)
    
    print(f"\n✅ Configuration saved to .env")
    
    # Test the configuration
    test_config = input("\n🧪 Test the configuration now? (Y/n): ")
    if test_config.lower() != 'n':
        print("\n🔍 Testing configuration...")
        
        try:
            import asyncio
            from sap_datasphere_mcp.models import DatasphereConfig
            from sap_datasphere_mcp.client import DatasphereClient
            from dotenv import load_dotenv
            
            load_dotenv()
            
            async def test():
                config = DatasphereConfig(
                    tenant_url=os.getenv("DATASPHERE_TENANT_URL"),
                    tenant_id=os.getenv("DATASPHERE_TENANT_ID"),
                    oauth_client_id=os.getenv("OAUTH_CLIENT_ID"),
                    oauth_client_secret=os.getenv("OAUTH_CLIENT_SECRET"),
                    oauth_token_url=os.getenv("OAUTH_TOKEN_URL")
                )
                
                client = DatasphereClient(config)
                
                try:
                    result = await client.test_connection()
                    if result.success:
                        print("✅ Connection test successful!")
                        print(f"   Tenant: {result.data['tenant_url']}")
                    else:
                        print(f"❌ Connection test failed: {result.error}")
                finally:
                    await client.close()
            
            asyncio.run(test())
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            print("💡 You can test manually later with: python examples/basic_usage.py")
    
    print(f"\n🎉 Setup complete!")
    print(f"\n🚀 Next steps:")
    print(f"1. Install dependencies: pip install -r requirements.txt")
    print(f"2. Run the MCP server: python -m sap_datasphere_mcp")
    print(f"3. Test with MCP Inspector: npx @modelcontextprotocol/inspector python -m sap_datasphere_mcp")


if __name__ == "__main__":
    setup_credentials()