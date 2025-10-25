#!/usr/bin/env python3
"""
Enhanced SAP Datasphere API Discovery
Uses working OAuth token to discover available API endpoints
"""
import requests
import base64
import json
from urllib.parse import urljoin

# Configuration from successful OAuth test
TENANT_URL = "https://your-tenant.eu10.hcs.cloud.sap"
OAUTH_CREDENTIALS = {
    "client_id": "sb-<subaccount-uuid>!b<n>|client!b<n>",
    "client_secret": "<your-client-secret>",
    "token_url": "https://ailien-test.authentication.eu20.hana.ondemand.com/oauth/token"
}

def get_oauth_token():
    """Get OAuth token using client credentials"""
    
    client_id = OAUTH_CREDENTIALS["client_id"]
    client_secret = OAUTH_CREDENTIALS["client_secret"]
    token_url = OAUTH_CREDENTIALS["token_url"]
    
    auth_string = f"{client_id}:{client_secret}"
    auth_b64 = base64.b64encode(auth_string.encode('ascii')).decode('ascii')
    
    headers = {
        'Authorization': f'Basic {auth_b64}',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    
    data = {'grant_type': 'client_credentials'}
    
    response = requests.post(token_url, headers=headers, data=data, timeout=30)
    
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        raise Exception(f"OAuth failed: {response.status_code} - {response.text}")

def discover_api_endpoints(access_token):
    """Comprehensive API endpoint discovery"""
    
    print("🔍 Discovering SAP Datasphere API Endpoints")
    print("=" * 60)
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json',
        'User-Agent': 'SAP-Datasphere-MCP-Client/1.0'
    }
    
    # Comprehensive list of potential API endpoints
    api_endpoints = [
        # Core Datasphere APIs
        "/dwaas-core/api/v1/spaces",
        "/dwaas-core/api/v1/catalog",
        "/dwaas-core/api/v1/connections",
        "/dwaas-core/api/v1/models",
        "/dwaas-core/api/v1/tasks",
        "/dwaas-core/api/v1/users",
        "/dwaas-core/api/v1/permissions",
        
        # DWC (Data Warehouse Cloud) APIs
        "/dwc/api/v1/spaces",
        "/dwc/api/v1/catalog",
        "/dwc/api/v1/connections",
        "/dwc/api/v1/models",
        "/dwc/api/v1/tasks",
        
        # Generic API paths
        "/api/v1/spaces",
        "/api/v1/catalog", 
        "/api/v1/connections",
        "/api/v1/models",
        "/api/v1/metadata",
        "/api/v1/health",
        "/api/v1/info",
        "/api/v1/version",
        
        # SAP Standard REST APIs
        "/sap/bc/rest/dwaas/v1/spaces",
        "/sap/bc/rest/dwaas/v1/catalog",
        "/sap/bc/rest/dwc/v1/spaces",
        "/sap/bc/rest/dwc/v1/catalog",
        
        # OData Services
        "/odata/v4/catalog",
        "/odata/v4/spaces",
        "/odata/v4/connections",
        "/sap/opu/odata/sap/DWC_CATALOG_SRV",
        "/sap/opu/odata/sap/DWC_SPACES_SRV",
        "/sap/opu/odata/sap/DWAAS_CATALOG_SRV",
        "/sap/opu/odata/sap/DWAAS_SPACES_SRV",
        
        # Discovery endpoints
        "/.well-known/api",
        "/api",
        "/api/v1",
        "/swagger.json",
        "/openapi.json",
        "/api-docs",
        "/docs",
        
        # Health and status
        "/health",
        "/status",
        "/ping",
        "/info",
        "/version",
        
        # Datasphere specific
        "/datasphere/api/v1/spaces",
        "/datasphere/api/v1/catalog",
        "/ds/api/v1/spaces",
        "/ds/api/v1/catalog"
    ]
    
    working_endpoints = []
    
    for endpoint in api_endpoints:
        try:
            url = TENANT_URL + endpoint
            response = requests.get(url, headers=headers, timeout=10)
            
            status_icon = "✅" if response.status_code < 400 else "❌"
            print(f"{status_icon} {endpoint}: {response.status_code}")
            
            if response.status_code < 400:
                working_endpoints.append({
                    'endpoint': endpoint,
                    'status_code': response.status_code,
                    'content_type': response.headers.get('content-type', 'unknown'),
                    'response_size': len(response.content)
                })
                
                # Try to parse response
                try:
                    if 'json' in response.headers.get('content-type', ''):
                        data = response.json()
                        if isinstance(data, list):
                            print(f"   📊 JSON array with {len(data)} items")
                        elif isinstance(data, dict):
                            keys = list(data.keys())[:5]
                            print(f"   📊 JSON object with keys: {keys}")
                        
                        # Save sample response
                        sample_file = f"sample_response_{endpoint.replace('/', '_')}.json"
                        with open(sample_file, 'w') as f:
                            json.dump(data, f, indent=2)
                        print(f"   💾 Sample saved to: {sample_file}")
                        
                except Exception as e:
                    print(f"   📄 Response parsing failed: {e}")
                    
            elif response.status_code == 401:
                print(f"   🔐 Authentication issue")
            elif response.status_code == 403:
                print(f"   🚫 Permission denied")
            elif response.status_code == 404:
                print(f"   ❓ Not found")
                
        except Exception as e:
            print(f"❌ {endpoint}: {type(e).__name__}")
    
    return working_endpoints

def test_working_endpoints(access_token, working_endpoints):
    """Test working endpoints with different HTTP methods"""
    
    if not working_endpoints:
        print("\n⚠️ No working endpoints found to test")
        return
    
    print(f"\n🧪 Testing Working Endpoints with Different Methods")
    print("=" * 60)
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    methods = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD']
    
    for endpoint_info in working_endpoints[:3]:  # Test first 3 working endpoints
        endpoint = endpoint_info['endpoint']
        url = TENANT_URL + endpoint
        
        print(f"\n🔍 Testing {endpoint}:")
        
        for method in methods:
            try:
                if method == 'GET':
                    response = requests.get(url, headers=headers, timeout=5)
                elif method == 'POST':
                    response = requests.post(url, headers=headers, json={}, timeout=5)
                elif method == 'PUT':
                    response = requests.put(url, headers=headers, json={}, timeout=5)
                elif method == 'DELETE':
                    response = requests.delete(url, headers=headers, timeout=5)
                elif method == 'OPTIONS':
                    response = requests.options(url, headers=headers, timeout=5)
                elif method == 'HEAD':
                    response = requests.head(url, headers=headers, timeout=5)
                
                status_icon = "✅" if response.status_code < 400 else "❌"
                print(f"  {status_icon} {method}: {response.status_code}")
                
                # Show allowed methods from OPTIONS
                if method == 'OPTIONS' and response.status_code < 400:
                    allowed = response.headers.get('Allow', 'Not specified')
                    print(f"     Allowed methods: {allowed}")
                
            except Exception as e:
                print(f"  ❌ {method}: {type(e).__name__}")

def save_discovery_results(working_endpoints):
    """Save discovery results to file"""
    
    results = {
        "discovery_date": "2025-01-13",
        "tenant_url": TENANT_URL,
        "oauth_working": True,
        "working_endpoints": working_endpoints,
        "total_working_endpoints": len(working_endpoints),
        "recommendations": []
    }
    
    if working_endpoints:
        results["recommendations"] = [
            "Use discovered endpoints for MCP server integration",
            "Test CRUD operations on working endpoints",
            "Implement proper error handling for API calls",
            "Consider rate limiting for production use"
        ]
    else:
        results["recommendations"] = [
            "Check API permissions in SAP Datasphere",
            "Verify OAuth client has correct scopes",
            "Contact SAP administrator for API access",
            "Review SAP Datasphere API documentation"
        ]
    
    with open('datasphere-api-discovery-results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Discovery results saved to: datasphere-api-discovery-results.json")

def main():
    """Main discovery function"""
    
    try:
        print("🚀 SAP Datasphere API Discovery")
        print("=" * 60)
        
        # Get OAuth token
        print("🔐 Getting OAuth token...")
        access_token = get_oauth_token()
        print("✅ OAuth token obtained")
        
        # Discover API endpoints
        working_endpoints = discover_api_endpoints(access_token)
        
        # Test working endpoints
        test_working_endpoints(access_token, working_endpoints)
        
        # Save results
        save_discovery_results(working_endpoints)
        
        # Summary
        print(f"\n" + "=" * 60)
        print("DISCOVERY SUMMARY")
        print("=" * 60)
        
        if working_endpoints:
            print(f"✅ Found {len(working_endpoints)} working API endpoints!")
            print(f"\nWorking endpoints:")
            for ep in working_endpoints:
                print(f"  • {ep['endpoint']} ({ep['status_code']})")
            
            print(f"\n🚀 Next steps:")
            print(f"• Integrate working endpoints into MCP server")
            print(f"• Test data retrieval from working endpoints")
            print(f"• Implement error handling and retry logic")
            
        else:
            print(f"❌ No working API endpoints found")
            print(f"\n💡 Troubleshooting:")
            print(f"• Check OAuth client permissions in SAP Datasphere")
            print(f"• Verify API access is enabled for your user")
            print(f"• Contact SAP administrator for API documentation")
        
    except Exception as e:
        print(f"❌ Discovery failed: {e}")

if __name__ == "__main__":
    main()