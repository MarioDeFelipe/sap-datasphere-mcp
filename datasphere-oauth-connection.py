#!/usr/bin/env python3
"""
SAP Datasphere API connection using OAuth2 authentication
Based on official SAP Datasphere CLI documentation
"""
import requests
import json
import base64
from urllib.parse import urlencode, parse_qs

# Connection details
TENANT_ID = "f45fa9cc-f4b5-4126-ab73-b19b578fb17a"
BASE_URL = f"https://{TENANT_ID}.eu10.hcs.cloud.sap"

# OAuth2 Configuration - These need to be provided by SAP Datasphere administrator
# Based on the documentation, you need an OAuth client created in Datasphere
OAUTH_CONFIG = {
    "client_id": None,  # To be provided by administrator
    "client_secret": None,  # To be provided by administrator  
    "authorization_url": None,  # Usually https://{tenant}.eu10.hcs.cloud.sap/oauth/authorize
    "token_url": None,  # Usually https://{tenant}.eu10.hcs.cloud.sap/oauth/token
    "host": BASE_URL,
    "authorization_flow": "client_credentials"  # or "authorization_code" for interactive
}

class DatasphereAPIClient:
    """SAP Datasphere API Client with proper OAuth2 authentication"""
    
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.access_token = None
        self.csrf_token = None
        
    def discover_oauth_endpoints(self):
        """Discover OAuth2 endpoints for the tenant"""
        
        print("🔍 Discovering OAuth2 endpoints...")
        
        # Standard OAuth2 discovery endpoints
        discovery_endpoints = [
            "/.well-known/oauth-authorization-server",
            "/.well-known/openid_configuration", 
            "/oauth/.well-known/oauth_authorization_server"
        ]
        
        for endpoint in discovery_endpoints:
            try:
                discovery_url = self.base_url + endpoint
                print(f"  Trying discovery: {discovery_url}")
                
                response = self.session.get(discovery_url, timeout=10)
                
                if response.status_code == 200:
                    config = response.json()
                    print(f"  ✅ Found OAuth2 configuration")
                    
                    # Extract OAuth2 URLs
                    auth_url = config.get('authorization_endpoint')
                    token_url = config.get('token_endpoint')
                    
                    if auth_url and token_url:
                        print(f"  🔑 Authorization URL: {auth_url}")
                        print(f"  🎫 Token URL: {token_url}")
                        return auth_url, token_url
                        
            except Exception as e:
                print(f"  ❌ Discovery failed: {e}")
        
        # Fallback to standard paths
        print("  📍 Using standard OAuth2 paths")
        auth_url = f"{self.base_url}/oauth/authorize"
        token_url = f"{self.base_url}/oauth/token"
        
        return auth_url, token_url
    
    def get_oauth_token_with_client_credentials(self, client_id, client_secret, token_url):
        """Get OAuth2 access token using client credentials flow"""
        
        print("🔐 Attempting OAuth2 client credentials authentication...")
        
        try:
            # Prepare OAuth2 client credentials request
            auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
            
            headers = {
                'Authorization': f'Basic {auth_header}',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
            
            data = {
                'grant_type': 'client_credentials'
            }
            
            print(f"  Token URL: {token_url}")
            response = self.session.post(token_url, headers=headers, data=data, timeout=10)
            
            print(f"  Response: {response.status_code}")
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                expires_in = token_data.get('expires_in', 'unknown')
                print(f"  ✅ OAuth2 token obtained (expires in {expires_in}s)")
                return True
            else:
                print(f"  ❌ Failed: {response.status_code}")
                print(f"  Response: {response.text}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        return False
    
    def test_oauth_endpoints_discovery(self):
        """Test and discover working OAuth2 endpoints"""
        
        print("🔍 Testing OAuth2 endpoint discovery...")
        
        # Common OAuth2 endpoint patterns for SAP
        oauth_patterns = [
            "/oauth/token",
            "/oauth/authorize",
            "/sap/bc/sec/oauth2/token",
            "/sap/bc/sec/oauth2/authorize", 
            "/api/oauth/token",
            "/api/oauth/authorize"
        ]
        
        working_endpoints = {}
        
        for pattern in oauth_patterns:
            try:
                url = self.base_url + pattern
                
                # Test with HEAD request to avoid authentication
                response = self.session.head(url, timeout=5)
                
                if response.status_code < 500:  # Any response that's not server error
                    status = "✅" if response.status_code < 400 else "⚠️"
                    print(f"  {status} {pattern}: {response.status_code}")
                    
                    if response.status_code in [200, 400, 401, 405]:  # Likely OAuth endpoints
                        working_endpoints[pattern] = response.status_code
                        
            except Exception as e:
                print(f"  ❌ {pattern}: {type(e).__name__}")
        
        return working_endpoints
    
    def get_csrf_token(self):
        """Get CSRF token required for SAP APIs"""
        
        print("🛡️ Getting CSRF token...")
        
        headers = {
            'X-CSRF-Token': 'Fetch',
            'Accept': 'application/json'
        }
        
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        else:
            # Fallback to basic auth
            headers['Authorization'] = f'Basic {base64.b64encode(f"{self.username}:{self.password}".encode()).decode()}'
        
        # Try different CSRF endpoints
        csrf_endpoints = [
            "/api/v1/csrf",
            "/sap/bc/rest/csrf",
            "/csrf",
            "/api/csrf"
        ]
        
        for endpoint in csrf_endpoints:
            try:
                csrf_url = self.base_url + endpoint
                print(f"  Trying: {csrf_url}")
                
                response = self.session.get(csrf_url, headers=headers, timeout=10)
                
                if response.status_code < 400:
                    csrf_token = response.headers.get('X-CSRF-Token')
                    if csrf_token:
                        self.csrf_token = csrf_token
                        print(f"  ✅ CSRF token obtained")
                        return True
                    else:
                        print(f"  ⚠️ No CSRF token in response")
                else:
                    print(f"  ❌ Failed: {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        return False
    
    def setup_session(self):
        """Setup session with proper authentication headers"""
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        else:
            # Fallback to basic auth
            headers['Authorization'] = f'Basic {base64.b64encode(f"{self.username}:{self.password}".encode()).decode()}'
        
        if self.csrf_token:
            headers['X-CSRF-Token'] = self.csrf_token
        
        self.session.headers.update(headers)
        
    def test_api_endpoints(self):
        """Test various API endpoints with proper authentication"""
        
        print("\n🔍 Testing API endpoints with proper authentication...")
        print("=" * 60)
        
        # SAP Datasphere API endpoints based on documentation
        api_endpoints = [
            # Datasphere Core APIs
            "/dwaas-core/api/v1/spaces",
            "/dwaas-core/api/v1/catalog", 
            "/dwaas-core/api/v1/connections",
            "/dwaas-core/api/v1/models",
            "/dwaas-core/api/v1/tasks",
            
            # DWC (Data Warehouse Cloud) APIs
            "/dwc/api/v1/spaces",
            "/dwc/api/v1/catalog",
            "/dwc/api/v1/connections",
            
            # Generic API paths
            "/api/v1/spaces",
            "/api/v1/catalog",
            "/api/v1/connections",
            "/api/v1/models",
            
            # OData services
            "/odata/v4/catalog",
            "/odata/v4/spaces",
            "/sap/opu/odata/sap/DWC_CATALOG_SRV",
            "/sap/opu/odata/sap/DWC_SPACES_SRV",
            
            # REST services
            "/sap/bc/rest/dwaas/v1/spaces",
            "/sap/bc/rest/dwaas/v1/catalog",
            "/rest/v1/spaces",
            "/rest/v1/catalog"
        ]
        
        results = {}
        
        for endpoint in api_endpoints:
            try:
                url = self.base_url + endpoint
                response = self.session.get(url, timeout=10)
                
                results[endpoint] = {
                    'status_code': response.status_code,
                    'accessible': response.status_code < 400,
                    'content_type': response.headers.get('content-type', 'unknown'),
                    'response_size': len(response.content)
                }
                
                if response.status_code < 400:
                    print(f"✅ {endpoint}: {response.status_code}")
                    
                    # Parse and show content
                    content_type = response.headers.get('content-type', '')
                    if 'json' in content_type:
                        try:
                            data = response.json()
                            if isinstance(data, dict):
                                print(f"   📊 JSON object with keys: {list(data.keys())[:5]}")
                            elif isinstance(data, list):
                                print(f"   📊 JSON array with {len(data)} items")
                        except:
                            print(f"   📄 JSON response (parsing failed)")
                    elif 'xml' in content_type:
                        print(f"   📋 XML response")
                        
                elif response.status_code == 401:
                    print(f"🔐 {endpoint}: 401 - Authentication failed")
                elif response.status_code == 403:
                    print(f"🚫 {endpoint}: 403 - Forbidden (check permissions)")
                elif response.status_code == 404:
                    print(f"❌ {endpoint}: 404 - Not Found")
                else:
                    print(f"⚠️ {endpoint}: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {endpoint}: {e}")
                results[endpoint] = {'error': str(e)}
        
        return results

def create_oauth_setup_guide():
    """Create a guide for setting up OAuth2 client in SAP Datasphere"""
    
    guide = {
        "title": "SAP Datasphere OAuth2 Setup Guide",
        "description": "Steps to create OAuth2 client for API access",
        "steps": [
            {
                "step": 1,
                "title": "Access SAP Datasphere Administration",
                "description": "Log into your SAP Datasphere tenant as an administrator",
                "url": f"{BASE_URL}"
            },
            {
                "step": 2, 
                "title": "Navigate to OAuth Clients",
                "description": "Go to System > Administration > App Integration > OAuth Clients"
            },
            {
                "step": 3,
                "title": "Create New OAuth Client",
                "description": "Click 'Add' to create a new OAuth client",
                "settings": {
                    "Purpose": "Technical User (for API access)",
                    "Authorization Flow": "Client Credentials",
                    "Access Token Lifetime": "720 hours (30 days)",
                    "Refresh Token Lifetime": "Not applicable for client credentials"
                }
            },
            {
                "step": 4,
                "title": "Configure OAuth Client",
                "description": "Set the following configuration",
                "required_fields": [
                    "Client ID (will be generated)",
                    "Client Secret (will be generated)", 
                    "Authorization URL (auto-configured)",
                    "Token URL (auto-configured)"
                ]
            },
            {
                "step": 5,
                "title": "Grant Permissions",
                "description": "Assign appropriate permissions to the OAuth client for API access"
            }
        ],
        "expected_urls": {
            "authorization_url": f"{BASE_URL}/oauth/authorize",
            "token_url": f"{BASE_URL}/oauth/token"
        },
        "next_steps": [
            "Update the OAUTH_CONFIG in this script with the generated credentials",
            "Test the connection using the OAuth2 client credentials",
            "Explore available API endpoints"
        ]
    }
    
    with open('oauth-setup-guide.json', 'w') as f:
        json.dump(guide, f, indent=2)
    
    return guide

def main():
    """Main function to test Datasphere OAuth2 setup and API discovery"""
    
    print("🚀 SAP Datasphere OAuth2 Discovery & Setup Guide")
    print("=" * 60)
    
    client = DatasphereAPIClient(BASE_URL, None, None)
    
    # Step 1: Discover OAuth2 endpoints
    print("\n📍 Step 1: OAuth2 Endpoint Discovery")
    working_oauth_endpoints = client.test_oauth_endpoints_discovery()
    
    # Step 2: Try OAuth2 discovery
    print(f"\n📍 Step 2: OAuth2 Configuration Discovery")
    auth_url, token_url = client.discover_oauth_endpoints()
    
    # Step 3: Create setup guide
    print(f"\n📍 Step 3: Creating OAuth2 Setup Guide")
    setup_guide = create_oauth_setup_guide()
    
    # Step 4: Summary and next steps
    print(f"\n" + "=" * 60)
    print("OAUTH2 DISCOVERY SUMMARY")
    print("=" * 60)
    
    if working_oauth_endpoints:
        print(f"✅ Found OAuth2 endpoints:")
        for endpoint, status in working_oauth_endpoints.items():
            print(f"   • {endpoint}: HTTP {status}")
    else:
        print(f"❌ No OAuth2 endpoints discovered")
    
    print(f"\n🔧 REQUIRED SETUP STEPS:")
    print(f"1. 👤 Administrator must create OAuth2 client in SAP Datasphere")
    print(f"2. 🔑 Get Client ID and Client Secret from administrator")
    print(f"3. 📝 Update OAUTH_CONFIG in this script with credentials")
    print(f"4. 🧪 Test API connection with OAuth2 authentication")
    
    print(f"\n📚 DOCUMENTATION REFERENCES:")
    print(f"• SAP Datasphere CLI OAuth Guide")
    print(f"• Create OAuth2.0 Client with Technical User Purpose")
    print(f"• SAP Datasphere API Documentation")
    
    print(f"\n📄 Setup guide saved to: oauth-setup-guide.json")
    
    # Test if OAuth credentials are configured
    if OAUTH_CONFIG["client_id"] and OAUTH_CONFIG["client_secret"]:
        print(f"\n🧪 Testing configured OAuth2 credentials...")
        
        oauth_success = client.get_oauth_token_with_client_credentials(
            OAUTH_CONFIG["client_id"],
            OAUTH_CONFIG["client_secret"], 
            token_url
        )
        
        if oauth_success:
            client.setup_session()
            results = client.test_api_endpoints()
            
            working_endpoints = [ep for ep, result in results.items() if result.get('accessible', False)]
            
            if working_endpoints:
                print(f"🎉 SUCCESS! Found {len(working_endpoints)} working API endpoints")
            else:
                print(f"⚠️ OAuth2 works but no API endpoints accessible")
        else:
            print(f"❌ OAuth2 authentication failed")
    else:
        print(f"\n⚠️ OAuth2 credentials not configured")
        print(f"   Update OAUTH_CONFIG with client_id and client_secret from administrator")

if __name__ == "__main__":
    main()