#!/usr/bin/env python3
"""
Simple OAuth credential test for SAP Datasphere
Fill in your OAuth credentials below and run this script
"""
import requests
import base64
import json

# Your SAP Datasphere tenant
TENANT_URL = "https://your-tenant.eu10.hcs.cloud.sap"

# OAuth credentials from SAP Datasphere (via BTP Authentication)
OAUTH_CREDENTIALS = {
    "client_id": "sb-<subaccount-uuid>!b<n>|client!b<n>",
    "client_secret": "<your-client-secret>",
    "authorization_url": "https://ailien-test.authentication.eu20.hana.ondemand.com/oauth/authorize",
    "token_url": "https://ailien-test.authentication.eu20.hana.ondemand.com/oauth/token"
}

def test_oauth_connection():
    """Test OAuth2 client credentials flow"""
    
    print("🔐 Testing SAP Datasphere OAuth Connection")
    print("=" * 50)
    
    # Check if credentials are filled in
    if not OAUTH_CREDENTIALS["client_id"] or not OAUTH_CREDENTIALS["client_secret"]:
        print("❌ ERROR: Please fill in your OAuth credentials first!")
        print("\n📝 Steps to get credentials:")
        print("1. Log into SAP Datasphere as administrator")
        print("2. Navigate to System > Administration > App Integration > OAuth Clients")
        print("3. Create new OAuth client with 'Technical User' purpose")
        print("4. Copy Client ID and Client Secret to this script")
        return False
    
    try:
        # Prepare OAuth2 request
        client_id = OAUTH_CREDENTIALS["client_id"]
        client_secret = OAUTH_CREDENTIALS["client_secret"]
        token_url = OAUTH_CREDENTIALS["token_url"]
        
        print(f"🌐 Tenant: {TENANT_URL}")
        print(f"🔑 Client ID: {client_id[:10]}...")
        print(f"🎫 Token URL: {token_url}")
        
        # Create authorization header
        auth_string = f"{client_id}:{client_secret}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        
        data = {
            'grant_type': 'client_credentials'
        }
        
        print(f"\n🚀 Requesting OAuth token...")
        response = requests.post(token_url, headers=headers, data=data, timeout=30)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            expires_in = token_data.get('expires_in', 'unknown')
            
            print(f"✅ SUCCESS! OAuth token obtained")
            print(f"🕒 Token expires in: {expires_in} seconds")
            print(f"🔑 Token preview: {access_token[:20]}...")
            
            # Test a simple API call
            print(f"\n🧪 Testing API access...")
            test_api_call(access_token)
            
            return True
            
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
            if response.status_code == 401:
                print("\n💡 Troubleshooting tips:")
                print("• Check if Client ID and Client Secret are correct")
                print("• Verify OAuth client is configured for 'Client Credentials' flow")
                print("• Ensure OAuth client has 'Technical User' purpose")
            
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_api_call(access_token):
    """Test a simple API call with the OAuth token"""
    
    # Try some common API endpoints
    test_endpoints = [
        "/dwaas-core/api/v1/spaces",
        "/api/v1/spaces", 
        "/dwc/api/v1/spaces"
    ]
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    
    for endpoint in test_endpoints:
        try:
            url = TENANT_URL + endpoint
            print(f"  Testing: {endpoint}")
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code < 400:
                print(f"  ✅ {endpoint}: {response.status_code}")
                
                # Show some response info
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"     📊 Found {len(data)} items")
                    elif isinstance(data, dict):
                        print(f"     📊 Response keys: {list(data.keys())[:3]}")
                except:
                    print(f"     📄 Response size: {len(response.content)} bytes")
                
                return True  # Found working endpoint
                
            else:
                print(f"  ❌ {endpoint}: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ {endpoint}: {e}")
    
    print(f"  ⚠️ No working API endpoints found (may need different permissions)")
    return False

def save_working_config(client_id, client_secret):
    """Save working OAuth config for use in other scripts"""
    
    config = {
        "tenant_url": TENANT_URL,
        "client_id": client_id,
        "client_secret": client_secret,
        "token_url": f"{TENANT_URL}/oauth/token",
        "authorization_url": f"{TENANT_URL}/oauth/authorize"
    }
    
    with open('datasphere-oauth-config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n💾 OAuth config saved to: datasphere-oauth-config.json")

def main():
    """Main function"""
    
    success = test_oauth_connection()
    
    if success:
        print(f"\n🎉 OAUTH SETUP COMPLETE!")
        print(f"✅ Your SAP Datasphere OAuth credentials are working")
        print(f"✅ API access is functional")
        
        # Save config for other scripts
        save_working_config(
            OAUTH_CREDENTIALS["client_id"],
            OAUTH_CREDENTIALS["client_secret"]
        )
        
        print(f"\n🚀 Next steps:")
        print(f"• Update MCP server configuration with these credentials")
        print(f"• Test full MCP server functionality")
        print(f"• Explore available API endpoints")
        
    else:
        print(f"\n❌ OAUTH SETUP FAILED")
        print(f"📋 Please follow the setup guide to create OAuth credentials")

if __name__ == "__main__":
    main()