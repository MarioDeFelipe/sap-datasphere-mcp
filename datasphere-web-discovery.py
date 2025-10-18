#!/usr/bin/env python3
"""
SAP Datasphere Web Interface Discovery
Analyze the web interface to find API endpoints
"""
import requests
import re
import json
from urllib.parse import urljoin, urlparse

# Configuration
TENANT_URL = "https://f45fa9cc-f4b5-4126-ab73-b19b578fb17a.eu10.hcs.cloud.sap"
OAUTH_CREDENTIALS = {
    "client_id": "sb-60cb266e-ad9d-49f7-9967-b53b8286a259!b130936|client!b3944",
    "client_secret": "caaea1b9-b09b-4d28-83fe-09966d525243$LOFW4h5LpLvB3Z2FE0P7FiH4-C7qexeQPi22DBiHbz8=",
    "token_url": "https://ailien-test.authentication.eu20.hana.ondemand.com/oauth/token"
}

def get_oauth_token():
    """Get OAuth token"""
    import base64
    
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
        raise Exception(f"OAuth failed: {response.status_code}")

def analyze_web_interface():
    """Analyze the Datasphere web interface for API clues"""
    
    print("🌐 Analyzing SAP Datasphere Web Interface")
    print("=" * 60)
    
    try:
        # Try to access the main page
        response = requests.get(TENANT_URL, timeout=30)
        print(f"📊 Main page status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            
            # Look for API references in the HTML/JavaScript
            api_patterns = [
                r'/api/[^"\s]+',
                r'/dwaas[^"\s]+',
                r'/dwc[^"\s]+',
                r'/odata[^"\s]+',
                r'/sap/[^"\s]+',
                r'https://[^"]*api[^"]*',
                r'"[^"]*api[^"]*"'
            ]
            
            found_apis = set()
            
            for pattern in api_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Clean up the match
                    clean_match = match.strip('"').strip("'")
                    if len(clean_match) > 4 and not clean_match.endswith('.js') and not clean_match.endswith('.css'):
                        found_apis.add(clean_match)
            
            if found_apis:
                print(f"🔍 Found potential API references:")
                for api in sorted(found_apis)[:20]:  # Show first 20
                    print(f"  • {api}")
            else:
                print("❌ No API references found in main page")
        
        # Try common SAP Datasphere subpaths
        subpaths = [
            "/shell",
            "/launchpad", 
            "/ui",
            "/app",
            "/cockpit",
            "/admin",
            "/api-docs",
            "/swagger"
        ]
        
        print(f"\n🔍 Testing common subpaths:")
        for subpath in subpaths:
            try:
                url = TENANT_URL + subpath
                response = requests.get(url, timeout=10)
                status_icon = "✅" if response.status_code < 400 else "❌"
                print(f"  {status_icon} {subpath}: {response.status_code}")
                
                if response.status_code < 400:
                    # Look for API references in successful responses
                    content = response.text
                    api_refs = re.findall(r'/api/[^"\s]+', content)
                    if api_refs:
                        print(f"    Found API refs: {api_refs[:3]}")
                        
            except Exception as e:
                print(f"  ❌ {subpath}: {type(e).__name__}")
        
    except Exception as e:
        print(f"❌ Web interface analysis failed: {e}")

def test_alternative_domains():
    """Test alternative domains and subdomains"""
    
    print(f"\n🌐 Testing Alternative Domains")
    print("=" * 60)
    
    # Extract base domain from tenant URL
    parsed = urlparse(TENANT_URL)
    base_domain = parsed.netloc.split('.', 1)[1]  # Remove tenant prefix
    
    # Common SAP subdomain patterns
    subdomains = [
        f"api-{parsed.netloc.split('.')[0]}",
        f"{parsed.netloc.split('.')[0]}-api",
        f"rest-{parsed.netloc.split('.')[0]}",
        f"{parsed.netloc.split('.')[0]}-rest",
        f"odata-{parsed.netloc.split('.')[0]}",
        f"{parsed.netloc.split('.')[0]}-odata"
    ]
    
    for subdomain in subdomains:
        try:
            alt_url = f"https://{subdomain}.{base_domain}"
            print(f"🔍 Testing: {alt_url}")
            
            response = requests.get(alt_url, timeout=10)
            status_icon = "✅" if response.status_code < 400 else "❌"
            print(f"  {status_icon} Status: {response.status_code}")
            
            if response.status_code < 400:
                print(f"  🎉 Alternative domain found!")
                
        except Exception as e:
            print(f"  ❌ {subdomain}: {type(e).__name__}")

def check_sap_documentation():
    """Check what the SAP documentation suggests"""
    
    print(f"\n📚 SAP Datasphere API Documentation Insights")
    print("=" * 60)
    
    insights = {
        "common_patterns": [
            "SAP Datasphere APIs often use tenant-specific paths",
            "APIs might be behind /dwaas-core/ or /dwc/ prefixes",
            "OData services typically use /odata/v4/ prefix",
            "REST APIs might use /api/v1/ or /rest/v1/ prefix"
        ],
        "authentication_notes": [
            "OAuth token is working - authentication is successful",
            "404 errors suggest endpoints don't exist or different paths",
            "May need specific API permissions in Datasphere admin",
            "Some APIs might be space-specific (require space ID in path)"
        ],
        "next_steps": [
            "Check SAP Datasphere admin console for API documentation",
            "Look for 'API Access' or 'Developer' section in UI",
            "Contact SAP support for API endpoint documentation",
            "Try space-specific API paths if you have space IDs"
        ]
    }
    
    for category, items in insights.items():
        print(f"\n{category.replace('_', ' ').title()}:")
        for item in items:
            print(f"  • {item}")

def test_with_space_context():
    """Test APIs that might require space context"""
    
    print(f"\n🏢 Testing Space-Specific API Patterns")
    print("=" * 60)
    
    # Common space-related patterns
    space_patterns = [
        "/api/v1/spaces/{space_id}/catalog",
        "/api/v1/spaces/{space_id}/connections", 
        "/api/v1/spaces/{space_id}/models",
        "/dwaas-core/api/v1/spaces/{space_id}/catalog",
        "/dwc/api/v1/spaces/{space_id}/catalog"
    ]
    
    # Try with placeholder space IDs
    test_space_ids = ["default", "SHARED", "PUBLIC", "DEMO", "TEST"]
    
    access_token = get_oauth_token()
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    
    for pattern in space_patterns[:2]:  # Test first 2 patterns
        for space_id in test_space_ids[:2]:  # Test first 2 space IDs
            try:
                endpoint = pattern.replace('{space_id}', space_id)
                url = TENANT_URL + endpoint
                
                response = requests.get(url, headers=headers, timeout=10)
                status_icon = "✅" if response.status_code < 400 else "❌"
                print(f"  {status_icon} {endpoint}: {response.status_code}")
                
                if response.status_code < 400:
                    print(f"    🎉 Working space-specific endpoint found!")
                elif response.status_code == 403:
                    print(f"    🔐 Forbidden - might need space permissions")
                    
            except Exception as e:
                print(f"  ❌ {endpoint}: {type(e).__name__}")

def main():
    """Main discovery function"""
    
    print("🚀 SAP Datasphere Advanced API Discovery")
    print("=" * 60)
    
    try:
        # Verify OAuth still works
        print("🔐 Verifying OAuth...")
        token = get_oauth_token()
        print("✅ OAuth token obtained")
        
        # Analyze web interface
        analyze_web_interface()
        
        # Test alternative domains
        test_alternative_domains()
        
        # Test space-specific patterns
        test_with_space_context()
        
        # Show documentation insights
        check_sap_documentation()
        
        print(f"\n" + "=" * 60)
        print("ADVANCED DISCOVERY SUMMARY")
        print("=" * 60)
        
        print(f"✅ OAuth authentication: Working")
        print(f"❌ Standard API endpoints: Not found")
        print(f"💡 Likely causes:")
        print(f"  • APIs require specific permissions")
        print(f"  • APIs use non-standard paths")
        print(f"  • APIs require space context")
        print(f"  • APIs are on different subdomain")
        
        print(f"\n🚀 Recommended next steps:")
        print(f"1. Check SAP Datasphere admin console for API docs")
        print(f"2. Look for 'Developer' or 'API Access' section")
        print(f"3. Contact SAP support for API endpoint list")
        print(f"4. Try accessing APIs through Datasphere UI first")
        
    except Exception as e:
        print(f"❌ Advanced discovery failed: {e}")

if __name__ == "__main__":
    main()