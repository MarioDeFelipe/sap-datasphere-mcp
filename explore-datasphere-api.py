#!/usr/bin/env python3
"""
Advanced Datasphere API exploration script
"""
import requests
import json
from requests.auth import HTTPBasicAuth

# Connection details
TENANT_ID = "f45fa9cc-f4b5-4126-ab73-b19b578fb17a"
BASE_URL = f"https://{TENANT_ID}.eu10.hcs.cloud.sap"
USERNAME = "GE230769"
PASSWORD = "ObVSIDDHPG1!"

def explore_api_discovery():
    """Try to discover the actual API structure"""
    
    session = requests.Session()
    session.auth = HTTPBasicAuth(USERNAME, PASSWORD)
    
    print(f"🔍 Exploring API structure for: {BASE_URL}")
    print("=" * 60)
    
    # Try different authentication and discovery approaches
    discovery_endpoints = [
        # Common API discovery endpoints
        "/.well-known/openapi",
        "/.well-known/api",
        "/swagger.json",
        "/openapi.json",
        "/api-docs",
        "/docs",
        
        # SAP specific patterns
        "/sap/bc/rest/",
        "/sap/opu/odata/",
        "/sap/bc/ui5_ui5/",
        
        # Datasphere specific patterns (based on SAP documentation)
        "/dwaas-core/",
        "/dwc/",
        "/api/v1/",
        "/rest/v1/",
        
        # Try without authentication first
        "/public/health",
        "/public/api",
        "/public/info"
    ]
    
    working_endpoints = []
    
    for endpoint in discovery_endpoints:
        try:
            # Try with authentication
            response = session.get(BASE_URL + endpoint, timeout=5)
            
            if response.status_code < 500:
                status = "✅" if response.status_code < 400 else "⚠️"
                print(f"{status} {endpoint}: {response.status_code}")
                
                if response.status_code < 400:
                    working_endpoints.append(endpoint)
                    
                    # Check content type and try to parse
                    content_type = response.headers.get('content-type', '')
                    if 'json' in content_type:
                        try:
                            data = response.json()
                            print(f"   📊 JSON: {type(data).__name__}")
                            if isinstance(data, dict) and data:
                                print(f"   🔑 Keys: {list(data.keys())[:5]}")
                        except:
                            print(f"   📄 JSON parsing failed")
                    elif 'html' in content_type:
                        print(f"   🌐 HTML response")
                    elif 'xml' in content_type:
                        print(f"   📋 XML response")
                    else:
                        print(f"   📄 Content-Type: {content_type}")
                        
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint}: {type(e).__name__}")
    
    return working_endpoints

def try_oauth_discovery():
    """Try to discover OAuth/SAML endpoints"""
    
    print(f"\n🔐 Checking authentication endpoints...")
    print("-" * 40)
    
    # Don't use authentication for these
    session = requests.Session()
    
    auth_endpoints = [
        "/oauth/token",
        "/oauth/authorize", 
        "/login",
        "/auth",
        "/saml/login",
        "/sap/bc/sec/oauth2/token",
        "/.well-known/oauth_authorization_server"
    ]
    
    for endpoint in auth_endpoints:
        try:
            response = session.get(BASE_URL + endpoint, timeout=5, allow_redirects=False)
            if response.status_code < 500:
                status = "✅" if response.status_code < 400 else "⚠️"
                print(f"{status} {endpoint}: {response.status_code}")
                
                # Check for redirects or auth challenges
                if 'location' in response.headers:
                    print(f"   🔄 Redirects to: {response.headers['location']}")
                if 'www-authenticate' in response.headers:
                    print(f"   🔐 Auth challenge: {response.headers['www-authenticate']}")
                    
        except requests.exceptions.RequestException:
            pass

def check_common_sap_paths():
    """Check common SAP application paths"""
    
    print(f"\n🏢 Checking SAP application paths...")
    print("-" * 40)
    
    session = requests.Session()
    session.auth = HTTPBasicAuth(USERNAME, PASSWORD)
    
    sap_paths = [
        # SAP Fiori Launchpad
        "/sap/bc/ui5_ui5/ui2/ushell/shells/abap/FioriLaunchpad.html",
        
        # SAP Gateway
        "/sap/opu/odata/sap/",
        
        # SAP Business Application Studio
        "/app-studio/",
        
        # SAP Analytics Cloud / Datasphere specific
        "/sac/",
        "/datasphere/",
        "/dwc/",
        "/dwaas/",
        
        # REST APIs
        "/sap/bc/rest/",
        "/rest/",
        
        # Common SAP services
        "/sap/bc/ping",
        "/sap/public/ping"
    ]
    
    for path in sap_paths:
        try:
            response = session.get(BASE_URL + path, timeout=5)
            if response.status_code < 500:
                status = "✅" if response.status_code < 400 else "⚠️"
                print(f"{status} {path}: {response.status_code}")
                
        except requests.exceptions.RequestException:
            pass

if __name__ == "__main__":
    print("🚀 Starting comprehensive Datasphere API exploration")
    
    # Step 1: API Discovery
    working_endpoints = explore_api_discovery()
    
    # Step 2: OAuth/Auth Discovery  
    try_oauth_discovery()
    
    # Step 3: SAP-specific paths
    check_common_sap_paths()
    
    # Summary
    print(f"\n" + "=" * 60)
    print("EXPLORATION SUMMARY")
    print("=" * 60)
    
    if working_endpoints:
        print(f"✅ Found {len(working_endpoints)} working endpoints:")
        for ep in working_endpoints:
            print(f"   • {ep}")
        print(f"\n🎯 Next steps:")
        print(f"   1. Explore the working endpoints for API documentation")
        print(f"   2. Check if they contain links to other APIs")
        print(f"   3. Look for OData metadata or OpenAPI specs")
    else:
        print("❌ No additional working endpoints found")
        print("🔧 Recommendations:")
        print("   1. Check SAP Datasphere documentation for correct API paths")
        print("   2. Verify tenant configuration and user permissions")
        print("   3. Contact SAP support for API access details")