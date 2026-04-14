#!/usr/bin/env python3
"""Quick demo of exact working code"""

from datasphere_connector import create_datasphere_connector

# Use the working connector
connector = create_datasphere_connector("dog")

print("🔴 EXACT WORKING CODE DEMONSTRATION")
print("=" * 70)

# Show exact configuration
print("\n📋 EXACT CONFIGURATION:")
print(f"   Base URL: {connector.config.base_url}")
print(f"   Token URL: {connector.config.token_url}")
print(f"   Client ID: {connector.config.client_id}")

# Connect (this does OAuth)
print("\n🔐 EXACT AUTHENTICATION:")
if connector.connect():
    print("   ✅ OAuth 2.0 successful!")
    print(f"   Token expires: {connector.oauth_token.expires_at}")
    
    # Show exact headers
    print("\n📋 EXACT HEADERS USED:")
    for key, value in connector.session.headers.items():
        if key == 'Authorization':
            print(f"   {key}: Bearer [TOKEN]")
        else:
            print(f"   {key}: {value}")
    
    # Show exact URL pattern
    space = "SAP_CONTENT"
    model = "SAP_SC_FI_AM_FINTRANSACTIONS"
    
    print(f"\n📍 EXACT URL PATTERN:")
    print(f"   Pattern: /api/v1/datasphere/consumption/analytical/{{space}}/{{model}}/{{model}}")
    print(f"   Example: /api/v1/datasphere/consumption/analytical/{space}/{model}/{model}")
    print(f"   Full URL: {connector.config.base_url}/api/v1/datasphere/consumption/analytical/{space}/{model}/{model}")
    
    connector.disconnect()
    print("\n✅ Demonstration complete!")
else:
    print("   ❌ Connection failed")

print("=" * 70)
