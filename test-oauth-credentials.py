#!/usr/bin/env python3
"""
Simple OAuth credential tester for SAP Datasphere
Update the OAUTH_CONFIG with your credentials and run this script
"""
import requests
import json
import base64

# Connection details
TENANT_ID = "f45fa9cc-f4b5-4126-ab73-b19b578fb17a"
BASE_URL = f"https://{TENANT_ID}.eu10.hcs.cloud.sap"

# TODO: Update these with your OAuth credentials from Datasphere
OAUTH_CONFIG = {
    "client_id": "",  # Paste your Client ID here
    "client_secret": "",  # Paste your Client Secret here
    "token_url": f"{BASE_URL}/oauth/token",  # Usually this format
    "authorization_url": f"{BASE_URL}/oauth/authorize"  # Usually this format
}

def test_oauth_connection():
    """Test OAuth2 connection with provided credentials"""
    
    print("🧪 Testing OAuth2 Credentials")
    print("=" * 40)
    
    # Check if credentials are provided
    if not OAUTH_CONFIG["client_id"] or not OAUTH_CONFIG["client_secret"]:
        print("❌ OAuth credentials not configured!")
        print("\n📝 To configure:")
        print("1. Open this file in an editor")
        print("2. Update OAUTH_CONFIG with your Client ID and Client Secret")
        print("3. Run this script again")
        return False
    
    print(f"Client ID: {OAUTH_CONFIG['client_id'][:20]}...")
    print(f"Token URL: {OAUTH_CONFIG['token_url']}")
    
    try:
        # Prepare OAuth2 client credentials request
        auth_header = base64.b64encode(
            f"{OAUTH_CONFIG['client_id']}:{OAUTH_CONFIG['client_secret']}".encode()
        ).decode()
        
        headers = {
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        
        data = {
            'grant_type': 'client_credentials'
        }
        
        print(f"\n🔐 Requesting OAuth2 token...")
        response = requests.post(OAUTH_CONFIG['token_url'], headers=headers, data=data, timeout=10)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            expires_in = token_data.get('expires_in', 'unknown')
            
            print(f"✅ SUCCESS! OAuth2 token obtained")
            print(f"Token expires in: {expires_in} seconds")
            print(f"Access token: {access_token[:50]}..." if access_token else "No access token")
            
            # Test API endpoints with the token
            return test_api_endpoints_with_token(access_token)
            
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 401:
                print("\n🔧 Troubleshooting:")
                print("• Check if Client ID and Client Secret are correct")
                print("• Verify the OAuth client is configured for 'Client Credentials' flow")
                print("• Ensure the OAuth client has API access permissions")
            elif response.status_code == 404:
                print("\n🔧 Troubleshooting:")
                print("• Check if the token URL is correct")
                print("• Verify OAuth is enabled on this tenant")
            
            return False
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

def test_api_endpoints_with_token(access_token):
    """Test API endpoints using the OAuth token"""
    
    print(f"\n🔍 Testing API endpoints with OAuth token...")
    print("-" * 40)
    
    session = requests.Session()
    session.headers.update({
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    })
    
    # Test key API endpoints
    test_endpoints = [
        "/dwaas-core/api/v1/spaces",
        "/dwaas-core/api/v1/catalog",
        "/api/v1/spaces",
        "/api/v1/catalog",
        "/odata/v4/catalog"
    ]
    
    working_endpoints = []
    
    for endpoint in test_endpoints:
        try:
            url = BASE_URL + endpoint
            response = session.get(url, timeout=10)
            
            if response.status_code < 400:
                print(f"✅ {endpoint}: {response.status_code}")
                working_endpoints.append(endpoint)
                
                # Try to parse response
                content_type = response.headers.get('content-type', '')
                if 'json' in content_type:
                    try:
                        data = response.json()
                        if isinstance(data, dict):
                            print(f"   📊 JSON object with keys: {list(data.keys())[:3]}")
                        elif isinstance(data, list):
                            print(f"   📊 JSON array with {len(data)} items")
                    except:
                        print(f"   📄 JSON response (parsing failed)")
                        
            elif response.status_code == 401:
                print(f"🔐 {endpoint}: 401 - Token authentication failed")
            elif response.status_code == 403:
                print(f"🚫 {endpoint}: 403 - Forbidden (check OAuth client permissions)")
            elif response.status_code == 404:
                print(f"❌ {endpoint}: 404 - Not Found")
            else:
                print(f"⚠️ {endpoint}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
    
    return working_endpoints

def main():
    """Main function"""
    
    print("🚀 SAP Datasphere OAuth2 Credential Tester")
    print(f"Tenant: {TENANT_ID}")
    print(f"Base URL: {BASE_URL}")
    print()
    
    # Test OAuth connection
    working_endpoints = test_oauth_connection()
    
    # Summary
    print(f"\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    if working_endpoints:
        print(f"🎉 SUCCESS! OAuth2 authentication working")
        print(f"✅ Found {len(working_endpoints)} accessible API endpoints:")
        for endpoint in working_endpoints:
            print(f"   • {endpoint}")
        
        print(f"\n🚀 NEXT STEPS:")
        print(f"1. 🏗️ Build MCP server using these working endpoints")
        print(f"2. 🔍 Explore the API responses for available data")
        print(f"3. 📊 Implement specific Datasphere operations")
        
    else:
        print(f"❌ OAuth2 authentication or API access failed")
        print(f"\n🔧 NEXT STEPS:")
        print(f"1. 🔍 Double-check OAuth credentials in Datasphere portal")
        print(f"2. ✅ Verify OAuth client has API access permissions")
        print(f"3. 📞 Contact SAP support if issues persist")

if __name__ == "__main__":
    main()