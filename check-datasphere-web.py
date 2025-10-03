#!/usr/bin/env python3
"""
Check Datasphere web interface and look for API clues
"""
import requests
from requests.auth import HTTPBasicAuth

# Connection details
TENANT_ID = "f45fa9cc-f4b5-4126-ab73-b19b578fb17a"
BASE_URL = f"https://{TENANT_ID}.eu10.hcs.cloud.sap"
USERNAME = "GE230769"
PASSWORD = "ObVSIDDHPG1!"

def check_web_interface():
    """Check if we can access the web interface and find API clues"""
    
    session = requests.Session()
    session.auth = HTTPBasicAuth(USERNAME, PASSWORD)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    print(f"🌐 Checking web interface access...")
    print("=" * 50)
    
    # Try different web interface paths
    web_paths = [
        "",  # Root
        "/index.html",
        "/home",
        "/dashboard",
        "/ui",
        "/app",
        "/launchpad",
        "/datasphere",
        "/dwc"
    ]
    
    for path in web_paths:
        try:
            url = BASE_URL + path
            print(f"Testing: {url}")
            
            response = session.get(url, timeout=10, allow_redirects=True)
            
            print(f"  Status: {response.status_code}")
            print(f"  Final URL: {response.url}")
            print(f"  Content-Type: {response.headers.get('content-type', 'unknown')}")
            
            if response.status_code < 400:
                # Look for API references in the HTML
                content = response.text.lower()
                
                # Search for common API patterns
                api_patterns = [
                    '/api/',
                    '/rest/',
                    '/odata/',
                    'api.js',
                    'rest.js',
                    'swagger',
                    'openapi'
                ]
                
                found_patterns = []
                for pattern in api_patterns:
                    if pattern in content:
                        found_patterns.append(pattern)
                
                if found_patterns:
                    print(f"  🔍 Found API patterns: {found_patterns}")
                
                # Look for JavaScript files that might contain API endpoints
                if 'script src=' in content:
                    print(f"  📜 Contains JavaScript files")
                
                # Check if it's a login page
                if any(word in content for word in ['login', 'password', 'signin', 'authentication']):
                    print(f"  🔐 Appears to be a login page")
                
                # Check if it's the main application
                if any(word in content for word in ['datasphere', 'analytics', 'dashboard']):
                    print(f"  🎯 Appears to be main application")
                    
            print()
            
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Error: {e}")
            print()

def check_different_subdomains():
    """Try different subdomain patterns that might host APIs"""
    
    print(f"🌍 Checking different subdomains...")
    print("=" * 50)
    
    # Different subdomain patterns for SAP Datasphere
    subdomain_patterns = [
        f"api-{TENANT_ID}.eu10.hcs.cloud.sap",
        f"{TENANT_ID}-api.eu10.hcs.cloud.sap", 
        f"rest-{TENANT_ID}.eu10.hcs.cloud.sap",
        f"{TENANT_ID}.api.eu10.hcs.cloud.sap",
        f"{TENANT_ID}.rest.eu10.hcs.cloud.sap",
        f"{TENANT_ID}.odata.eu10.hcs.cloud.sap",
        f"{TENANT_ID}.datasphere.eu10.hcs.cloud.sap"
    ]
    
    session = requests.Session()
    session.auth = HTTPBasicAuth(USERNAME, PASSWORD)
    
    for subdomain in subdomain_patterns:
        try:
            url = f"https://{subdomain}/health"
            print(f"Testing: {url}")
            
            response = session.get(url, timeout=5)
            
            if response.status_code < 500:
                print(f"  ✅ Responds: {response.status_code}")
                
                # If this subdomain works, try some API paths
                if response.status_code < 400:
                    api_paths = ["/api/v1/spaces", "/api/v1/catalog", "/odata/v4/catalog"]
                    for api_path in api_paths:
                        try:
                            api_response = session.get(f"https://{subdomain}{api_path}", timeout=5)
                            if api_response.status_code < 400:
                                print(f"    🎯 API found: {api_path} -> {api_response.status_code}")
                        except:
                            pass
            else:
                print(f"  ❌ {response.status_code}")
                
        except requests.exceptions.RequestException:
            print(f"  ❌ Connection failed")
        
        print()

def check_headers_for_clues():
    """Check response headers for API clues"""
    
    print(f"🔍 Analyzing response headers for clues...")
    print("=" * 50)
    
    session = requests.Session()
    session.auth = HTTPBasicAuth(USERNAME, PASSWORD)
    
    # Check the working health endpoint for clues
    try:
        response = session.get(BASE_URL + "/health", timeout=5)
        
        print("Health endpoint headers:")
        for header, value in response.headers.items():
            print(f"  {header}: {value}")
            
        # Look for SAP-specific headers that might give us clues
        sap_headers = [h for h in response.headers.keys() if 'sap' in h.lower()]
        if sap_headers:
            print(f"\n🏢 SAP-specific headers found: {sap_headers}")
            
        # Check for API version hints
        version_headers = [h for h in response.headers.keys() if 'version' in h.lower() or 'api' in h.lower()]
        if version_headers:
            print(f"\n📋 Version/API headers: {version_headers}")
            
    except Exception as e:
        print(f"Error checking headers: {e}")

if __name__ == "__main__":
    print("🔍 Comprehensive Datasphere web interface check")
    print()
    
    # Check web interface
    check_web_interface()
    
    # Check different subdomains
    check_different_subdomains()
    
    # Analyze headers
    check_headers_for_clues()
    
    print("=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)
    print("1. 📚 Check SAP Datasphere official documentation for API endpoints")
    print("2. 🎫 Verify that your user has API access permissions")
    print("3. 🌐 Try accessing the web interface directly in a browser")
    print("4. 📞 Contact SAP support for tenant-specific API configuration")
    print("5. 🔐 Check if OAuth2 or different authentication is required")