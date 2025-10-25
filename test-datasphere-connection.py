#!/usr/bin/env python3
"""
Test script to verify Datasphere connectivity and explore available APIs
"""
import requests
import json
from requests.auth import HTTPBasicAuth

# Datasphere connection details
TENANT_ID = "f45fa9cc-f4b5-4126-ab73-b19b578fb17a"
USERNAME = "GE230769"
PASSWORD = "ObVSIDDHPG1!"

# Try different URL patterns for SAP Datasphere
POSSIBLE_BASE_URLS = [
    f"https://{TENANT_ID}.datasphere.cloud.sap",
    f"https://{TENANT_ID}.eu10.hcs.cloud.sap",
    f"https://{TENANT_ID}.us10.hcs.cloud.sap",
    f"https://{TENANT_ID}.ap10.hcs.cloud.sap",
    f"https://{TENANT_ID}.datasphere.sap.com",
    f"https://{TENANT_ID}.sap.com",
    f"https://datasphere-{TENANT_ID}.cfapps.eu10.hana.ondemand.com",
    f"https://datasphere-{TENANT_ID}.cfapps.us10.hana.ondemand.com"
]

def test_datasphere_connection():
    """Test basic connectivity to Datasphere tenant"""
    
    # Common Datasphere API endpoints to test
    test_endpoints = [
        "/api/v1/spaces",
        "/api/v1/catalog",
        "/api/v1/metadata",
        "/odata/v4/catalog",
        "/$metadata",
        "/",  # Root endpoint
        "/health",  # Health check
        "/api"  # API root
    ]
    
    print(f"Testing connection to Datasphere tenant: {TENANT_ID}")
    print("Trying multiple URL patterns...")
    print("-" * 60)
    
    session = requests.Session()
    session.auth = HTTPBasicAuth(USERNAME, PASSWORD)
    session.headers.update({
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    })
    
    results = {}
    working_base_url = None
    
    # First, test which base URL works
    for base_url in POSSIBLE_BASE_URLS:
        print(f"\n🔍 Testing base URL: {base_url}")
        try:
            # Test root endpoint first
            response = session.get(base_url + "/", timeout=5)
            if response.status_code < 500:  # Any response that's not a server error
                print(f"  ✅ Base URL responds: {response.status_code}")
                working_base_url = base_url
                break
            else:
                print(f"  ❌ Server error: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Connection failed: {type(e).__name__}")
    
    if not working_base_url:
        print("\n❌ No working base URL found!")
        return results
    
    print(f"\n🎯 Using working base URL: {working_base_url}")
    print("-" * 60)
    
    # Now test endpoints with the working base URL
    for endpoint in test_endpoints:
        try:
            url = working_base_url + endpoint
            print(f"Testing: {url}")
            
            response = session.get(url, timeout=10)
            
            results[endpoint] = {
                'status_code': response.status_code,
                'accessible': response.status_code < 400,
                'content_type': response.headers.get('content-type', 'unknown'),
                'response_size': len(response.content),
                'base_url': working_base_url
            }
            
            if response.status_code < 400:
                print(f"  ✅ SUCCESS: {response.status_code}")
                if response.headers.get('content-type', '').startswith('application/json'):
                    try:
                        data = response.json()
                        if isinstance(data, dict) and len(data) > 0:
                            print(f"  📊 JSON Response with {len(data)} keys")
                        elif isinstance(data, list):
                            print(f"  📊 JSON Array with {len(data)} items")
                    except:
                        print(f"  📄 JSON response (parsing failed)")
                else:
                    print(f"  📄 Response type: {response.headers.get('content-type')}")
            else:
                print(f"  ❌ FAILED: {response.status_code} - {response.reason}")
                
        except requests.exceptions.RequestException as e:
            print(f"  ❌ CONNECTION ERROR: {str(e)}")
            results[endpoint] = {
                'status_code': None,
                'accessible': False,
                'error': str(e),
                'base_url': working_base_url
            }
        
        print()
    
    # Summary
    print("=" * 60)
    print("CONNECTION TEST SUMMARY")
    print("=" * 60)
    
    accessible_endpoints = [ep for ep, result in results.items() if result.get('accessible', False)]
    
    if accessible_endpoints:
        print(f"✅ {len(accessible_endpoints)} endpoints accessible:")
        for ep in accessible_endpoints:
            print(f"   • {ep}")
        print(f"\n🎯 Recommended next step: Explore {accessible_endpoints[0]} for metadata")
    else:
        print("❌ No endpoints accessible")
        print("🔧 Possible issues:")
        print("   • Authentication credentials")
        print("   • Network connectivity")
        print("   • Tenant URL format")
        print("   • API endpoint paths")
    
    return results

def explore_working_endpoint():
    """Explore the working health endpoint to understand the service"""
    
    working_url = "https://f45fa9cc-f4b5-4126-ab73-b19b578fb17a.eu10.hcs.cloud.sap"
    
    session = requests.Session()
    session.auth = HTTPBasicAuth(USERNAME, PASSWORD)
    session.headers.update({
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    })
    
    print("\n" + "=" * 60)
    print("EXPLORING WORKING ENDPOINT")
    print("=" * 60)
    
    try:
        # Get health endpoint details
        response = session.get(working_url + "/health", timeout=10)
        print(f"Health endpoint response:")
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            data = response.json()
            print(f"JSON Response:")
            print(json.dumps(data, indent=2))
        else:
            print(f"Response content: {response.text[:500]}")
            
        # Try some common SAP Datasphere paths
        additional_paths = [
            "/dwaas-core/health",
            "/dwaas-core/api/v1/spaces",
            "/dwaas-core/api/v1/catalog",
            "/dwc/api/v1/spaces",
            "/dwc/api/v1/catalog",
            "/api/v1/dwc/spaces",
            "/sap/bc/rest/dwaas/v1/spaces",
            "/sap/opu/odata/sap/DWC_CATALOG_SRV",
            "/catalog",
            "/spaces"
        ]
        
        print(f"\nTrying additional SAP Datasphere paths:")
        for path in additional_paths:
            try:
                test_response = session.get(working_url + path, timeout=5)
                if test_response.status_code < 500:
                    print(f"  ✅ {path}: {test_response.status_code}")
                    if test_response.status_code < 400:
                        content_type = test_response.headers.get('content-type', '')
                        if 'json' in content_type:
                            try:
                                json_data = test_response.json()
                                if isinstance(json_data, dict):
                                    print(f"     📊 JSON with keys: {list(json_data.keys())[:5]}")
                                elif isinstance(json_data, list):
                                    print(f"     📊 JSON array with {len(json_data)} items")
                            except:
                                print(f"     📄 JSON response (parsing failed)")
                        else:
                            print(f"     📄 Content-Type: {content_type}")
                else:
                    print(f"  ❌ {path}: {test_response.status_code}")
            except requests.exceptions.RequestException:
                print(f"  ❌ {path}: Connection failed")
                
    except Exception as e:
        print(f"Error exploring endpoint: {e}")

if __name__ == "__main__":
    results = test_datasphere_connection()
    
    # Save results for analysis
    with open('datasphere-connection-test.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved to: datasphere-connection-test.json")
    
    # Explore the working endpoint further
    explore_working_endpoint()