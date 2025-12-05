#!/usr/bin/env python3
"""
🔴 EXACT WORKING CODE FROM DATASPHERE_CONNECTOR.PY
This is the ACTUAL code that successfully accesses SAP Datasphere API
"""

import requests
import base64
from urllib.parse import urljoin

# ============================================================================
# 🔴 STEP 1: EXACT CONFIGURATION (WORKING)
# ============================================================================

BASE_URL = "https://ailien-test.eu20.hcs.cloud.sap"
CLIENT_ID = "sb-60cb266e-ad9d-49f7-9967-b53b8286a259!b130936|client!b3944"
CLIENT_SECRET = "your_secret_here"  # Get from dashboard_config.py
TOKEN_URL = "https://ailien-test.authentication.eu20.hana.ondemand.com/oauth/token"

# ============================================================================
# 🔴 STEP 2: EXACT AUTHENTICATION CODE (WORKING)
# ============================================================================

def authenticate():
    """EXACT authentication code that works"""
    
    # Create Basic Auth header (EXACT format)
    auth_header = base64.b64encode(
        f"{CLIENT_ID}:{CLIENT_SECRET}".encode()
    ).decode()
    
    # EXACT headers that work
    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    # EXACT request body
    data = {'grant_type': 'client_credentials'}
    
    # Make token request
    response = requests.post(
        TOKEN_URL,
        headers=headers,
        data=data,
        timeout=30
    )
    
    if response.status_code == 200:
        token_data = response.json()
        print(f"✅ Authentication successful!")
        print(f"   Token type: {token_data.get('token_type')}")
        print(f"   Expires in: {token_data.get('expires_in')} seconds")
        return token_data['access_token']
    else:
        raise Exception(f"Auth failed: {response.status_code} - {response.text}")

# ============================================================================
# 🔴 STEP 3: EXACT API REQUEST CODE (WORKING)
# ============================================================================

def make_api_request(access_token, space, model):
    """
    EXACT code that successfully fetches data from Datasphere
    
    This is the ACTUAL working pattern from datasphere_connector.py
    """
    
    # 🔴 EXACT URL CONSTRUCTION (This is what works!)
    model_base = f"/api/v1/datasphere/consumption/analytical/{space}/{model}"
    
    # Three working endpoints:
    service_url = urljoin(BASE_URL, model_base)
    metadata_url = urljoin(BASE_URL, f"{model_base}/$metadata")
    data_url = urljoin(BASE_URL, f"{model_base}/{model}")
    
    print(f"\n📍 EXACT URLs being used:")
    print(f"   Service: {service_url}")
    print(f"   Metadata: {metadata_url}")
    print(f"   Data: {data_url}")
    
    # 🔴 EXACT HEADERS (This is what works!)
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json',
        'User-Agent': 'Datasphere-Metadata-Sync/2.0'
    }
    
    print(f"\n📋 EXACT Headers:")
    for key, value in headers.items():
        if key == 'Authorization':
            print(f"   {key}: Bearer [TOKEN]")
        else:
            print(f"   {key}: {value}")
    
    # 🔴 REQUEST 1: Get Service Info (WORKING)
    print(f"\n🔄 Making request to service endpoint...")
    service_response = requests.get(service_url, headers=headers, timeout=30)
    
    print(f"   Status Code: {service_response.status_code}")
    print(f"   Content-Type: {service_response.headers.get('content-type')}")
    
    if service_response.status_code == 200:
        service_data = service_response.json()
        print(f"   ✅ SUCCESS!")
        print(f"   Response keys: {list(service_data.keys())}")
        print(f"   OData context: {service_data.get('@odata.context', 'N/A')}")
        
        # 🔴 REQUEST 2: Get Metadata (WORKING)
        print(f"\n🔄 Making request to metadata endpoint...")
        
        # IMPORTANT: Metadata requires XML accept header
        metadata_headers = headers.copy()
        metadata_headers['Accept'] = 'application/xml'
        
        metadata_response = requests.get(metadata_url, headers=metadata_headers, timeout=30)
        print(f"   Status Code: {metadata_response.status_code}")
        print(f"   Content-Type: {metadata_response.headers.get('content-type')}")
        
        if metadata_response.status_code == 200:
            print(f"   ✅ SUCCESS!")
            print(f"   Response length: {len(metadata_response.text)} chars")
            print(f"   First 200 chars: {metadata_response.text[:200]}")
        
        # 🔴 REQUEST 3: Get Data (WORKING)
        print(f"\n🔄 Making request to data endpoint...")
        
        # Add query parameters
        params = {
            '$top': 5,  # Limit results
            '$select': 'ACCOUNTID_D1,COUNTRY'  # NEW FEATURE: Select specific dimensions
        }
        
        data_response = requests.get(data_url, headers=headers, params=params, timeout=30)
        print(f"   Status Code: {data_response.status_code}")
        print(f"   Content-Type: {data_response.headers.get('content-type')}")
        
        if data_response.status_code == 200:
            data = data_response.json()
            print(f"   ✅ SUCCESS!")
            print(f"   Response keys: {list(data.keys())}")
            print(f"   Records returned: {len(data.get('value', []))}")
            
            if data.get('value'):
                print(f"   Sample record keys: {list(data['value'][0].keys())}")
        
        return service_data
    else:
        print(f"   ❌ FAILED")
        print(f"   Response: {service_response.text[:500]}")
        return None

# ============================================================================
# 🔴 STEP 4: EXACT SESSION SETUP (WORKING)
# ============================================================================

def create_session_with_token(access_token):
    """
    EXACT session setup from datasphere_connector.py
    """
    session = requests.Session()
    
    # EXACT default headers
    session.headers.update({
        'Accept': 'application/json',
        'User-Agent': 'Datasphere-Metadata-Sync/2.0'
    })
    
    # Add token
    session.headers['Authorization'] = f'Bearer {access_token}'
    
    return session

# ============================================================================
# 🔴 COMPLETE WORKING EXAMPLE
# ============================================================================

def main():
    """
    Complete working example - this is EXACTLY what works in production
    """
    
    print("=" * 70)
    print("🔴 EXACT WORKING CODE FROM DATASPHERE_CONNECTOR.PY")
    print("=" * 70)
    
    # Step 1: Authenticate
    print("\n🔐 Step 1: Authentication")
    print("-" * 70)
    access_token = authenticate()
    
    # Step 2: Make API requests
    print("\n📡 Step 2: API Requests")
    print("-" * 70)
    
    # EXACT working example
    space = "SAP_CONTENT"
    model = "SAP_SC_FI_AM_FINTRANSACTIONS"
    
    result = make_api_request(access_token, space, model)
    
    # Step 3: Using session (alternative approach)
    print("\n\n🔄 Step 3: Using Session (Alternative)")
    print("-" * 70)
    
    session = create_session_with_token(access_token)
    
    # Make request with session
    url = f"{BASE_URL}/api/v1/datasphere/consumption/analytical/{space}/{model}/{model}"
    response = session.get(url, params={'$top': 1}, timeout=30)
    
    print(f"Session request status: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Session approach also works!")
    
    print("\n" + "=" * 70)
    print("✅ COMPLETE - All working code demonstrated")
    print("=" * 70)

# ============================================================================
# 🔴 QUICK REFERENCE: EXACT WORKING PATTERNS
# ============================================================================

"""
🔴 EXACT URL PATTERNS THAT WORK:

1. Service Root:
   https://ailien-test.eu20.hcs.cloud.sap/api/v1/datasphere/consumption/analytical/{space}/{model}
   
2. Metadata:
   https://ailien-test.eu20.hcs.cloud.sap/api/v1/datasphere/consumption/analytical/{space}/{model}/$metadata
   
3. Data:
   https://ailien-test.eu20.hcs.cloud.sap/api/v1/datasphere/consumption/analytical/{space}/{model}/{model}

🔴 EXACT HEADERS THAT WORK:

For JSON data:
{
    'Authorization': 'Bearer {token}',
    'Accept': 'application/json',
    'User-Agent': 'Datasphere-Metadata-Sync/2.0'
}

For XML metadata:
{
    'Authorization': 'Bearer {token}',
    'Accept': 'application/xml',
    'User-Agent': 'Datasphere-Metadata-Sync/2.0'
}

🔴 EXACT QUERY PARAMETERS THAT WORK:

$top=10                          # Limit results
$skip=0                          # Pagination
$select=Field1,Field2            # Select specific dimensions (NEW!)
$filter=Field eq 'value'         # OData filter
$orderby=Field asc               # Sorting

🔴 NO INITIALIZATION REQUIRED:

- No session handshake needed
- No cookies required
- No special setup
- Just: Authenticate → Get token → Make request

🔴 RESPONSE FORMAT:

Content-Type: application/json

{
    "@odata.context": "...",
    "value": [
        {
            "Field1": "value1",
            "Field2": "value2",
            ...
        }
    ]
}
"""

if __name__ == "__main__":
    # Get the actual secret from dashboard_config
    try:
        from dashboard_config import get_datasphere_config
        config = get_datasphere_config()
        CLIENT_SECRET = config['client_secret']
        print("✅ Loaded credentials from dashboard_config.py")
    except:
        print("⚠️  Using placeholder secret - update CLIENT_SECRET variable")
    
    main()
