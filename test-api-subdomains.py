#!/usr/bin/env python3
"""
Test the API-specific subdomains we discovered
"""
import requests
import json
from requests.auth import HTTPBasicAuth

# Connection details
TENANT_ID = "f45fa9cc-f4b5-4126-ab73-b19b578fb17a"
USERNAME = "GE230769"
PASSWORD = "ObVSIDDHPG1!"

# API subdomains that responded to /health
API_SUBDOMAINS = [
    f"api-{TENANT_ID}.eu10.hcs.cloud.sap",
    f"{TENANT_ID}-api.eu10.hcs.cloud.sap", 
    f"rest-{TENANT_ID}.eu10.hcs.cloud.sap"
]

def test_api_endpoints_on_subdomains():
    """Test API endpoints on the discovered subdomains"""
    
    session = requests.Session()
    session.auth = HTTPBasicAuth(USERNAME, PASSWORD)
    session.headers.update({
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    })
    
    # API endpoints to test
    api_endpoints = [
        "/api/v1/spaces",
        "/api/v1/catalog", 
        "/api/v1/metadata",
        "/api/v1/models",
        "/api/v1/connections",
        "/odata/v4/catalog",
        "/odata/v4/spaces",
        "/$metadata",
        "/rest/v1/spaces",
        "/rest/v1/catalog",
        "/dwc/api/v1/spaces",
        "/dwc/api/v1/catalog",
        "/sap/bc/rest/dwaas/v1/spaces",
        "/sap/opu/odata/sap/DWC_CATALOG_SRV"
    ]
    
    results = {}
    
    for subdomain in API_SUBDOMAINS:
        print(f"\n🔍 Testing subdomain: {subdomain}")
        print("=" * 60)
        
        base_url = f"https://{subdomain}"
        subdomain_results = {}
        
        for endpoint in api_endpoints:
            try:
                url = base_url + endpoint
                response = session.get(url, timeout=10)
                
                subdomain_results[endpoint] = {
                    'status_code': response.status_code,
                    'accessible': response.status_code < 400,
                    'content_type': response.headers.get('content-type', 'unknown'),
                    'response_size': len(response.content)
                }
                
                if response.status_code < 400:
                    print(f"✅ {endpoint}: {response.status_code}")
                    
                    # Try to parse and show some content
                    content_type = response.headers.get('content-type', '')
                    if 'json' in content_type:
                        try:
                            data = response.json()
                            if isinstance(data, dict):
                                print(f"   📊 JSON object with keys: {list(data.keys())[:5]}")
                                # Show first few items if it's a list of objects
                                for key, value in list(data.items())[:3]:
                                    if isinstance(value, (str, int, bool)):
                                        print(f"   🔑 {key}: {value}")
                            elif isinstance(data, list):
                                print(f"   📊 JSON array with {len(data)} items")
                                if data and isinstance(data[0], dict):
                                    print(f"   🔑 First item keys: {list(data[0].keys())[:5]}")
                        except Exception as e:
                            print(f"   📄 JSON parsing failed: {e}")
                    elif 'xml' in content_type:
                        print(f"   📋 XML response ({len(response.content)} bytes)")
                        # Show first few lines of XML
                        xml_preview = response.text[:200].replace('\n', ' ')
                        print(f"   📄 Preview: {xml_preview}...")
                    else:
                        print(f"   📄 Content-Type: {content_type}")
                        
                elif response.status_code == 401:
                    print(f"🔐 {endpoint}: 401 - Authentication required")
                elif response.status_code == 403:
                    print(f"🚫 {endpoint}: 403 - Forbidden (check permissions)")
                elif response.status_code == 404:
                    print(f"❌ {endpoint}: 404 - Not Found")
                else:
                    print(f"⚠️ {endpoint}: {response.status_code} - {response.reason}")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ {endpoint}: Connection error - {type(e).__name__}")
                subdomain_results[endpoint] = {
                    'status_code': None,
                    'accessible': False,
                    'error': str(e)
                }
        
        results[subdomain] = subdomain_results
    
    return results

def summarize_findings(results):
    """Summarize the findings across all subdomains"""
    
    print(f"\n" + "=" * 80)
    print("COMPREHENSIVE SUMMARY")
    print("=" * 80)
    
    all_working_endpoints = {}
    
    for subdomain, endpoints in results.items():
        working = [ep for ep, result in endpoints.items() if result.get('accessible', False)]
        if working:
            all_working_endpoints[subdomain] = working
    
    if all_working_endpoints:
        print(f"🎉 SUCCESS! Found working API endpoints:")
        print()
        
        for subdomain, endpoints in all_working_endpoints.items():
            print(f"📡 {subdomain}:")
            for ep in endpoints:
                print(f"   ✅ {ep}")
            print()
            
        print(f"🚀 NEXT STEPS:")
        print(f"1. Use these endpoints to explore the Datasphere API")
        print(f"2. Check the JSON responses for available data and operations")
        print(f"3. Look for pagination, filtering, and query parameters")
        print(f"4. Build your MCP server using these working endpoints")
        
    else:
        print(f"❌ No working API endpoints found on any subdomain")
        print(f"🔧 TROUBLESHOOTING:")
        print(f"1. Verify user permissions for API access")
        print(f"2. Check if APIs need to be enabled in tenant configuration")
        print(f"3. Try OAuth2 authentication instead of Basic Auth")
        print(f"4. Contact SAP support for API access setup")

if __name__ == "__main__":
    print("🚀 Testing API endpoints on discovered subdomains")
    
    results = test_api_endpoints_on_subdomains()
    
    # Save detailed results
    with open('api-subdomain-results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: api-subdomain-results.json")
    
    # Show summary
    summarize_findings(results)