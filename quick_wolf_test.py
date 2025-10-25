#!/usr/bin/env python3
"""
Quick Wolf Connection Test
Test the Wolf environment connection directly
"""

import requests
import base64
import json
from datetime import datetime

def test_wolf_oauth():
    """Test Wolf OAuth connection"""
    
    print("🐺 Quick Wolf Connection Test")
    print("=" * 32)
    
    # Wolf configuration (updated to ailien environment)
    client_id = "sb-60cb266e-ad9d-49f7-9967-b53b8286a259!b130936|client!b3944"
    client_secret = "caaea1b9-b09b-4d28-83fe-09966d525243$LOFW4h5LpLvB3Z2FE0P7FiH4-C7qexeQPi22DBiHbz8="
    token_url = "https://ailien-test.authentication.eu20.hana.ondemand.com/oauth/token"
    base_url = "https://ailien-test.eu20.hcs.cloud.sap"
    
    print(f"🔗 Testing connection to: {base_url}")
    print(f"🎫 Token URL: {token_url}")
    
    try:
        # Step 1: Get OAuth token
        print("\n🔐 Step 1: Getting OAuth token...")
        
        auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        
        headers = {
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {'grant_type': 'client_credentials'}
        
        response = requests.post(token_url, headers=headers, data=data, timeout=30)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            print(f"✅ OAuth token obtained successfully")
            print(f"🎫 Token preview: {access_token[:20]}...")
        else:
            print(f"❌ OAuth failed: HTTP {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
        
        # Step 2: Test API endpoint
        print("\n🔍 Step 2: Testing API endpoint...")
        
        api_headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
            'User-Agent': 'Quick-Wolf-Test/1.0'
        }
        
        # Test the working analytical model endpoint
        api_url = f"{base_url}/api/v1/datasphere/consumption/analytical/SAP_CONTENT/New_Analytic_Model_2"
        
        api_response = requests.get(api_url, headers=api_headers, timeout=30)
        
        if api_response.status_code == 200:
            print(f"✅ API endpoint accessible")
            
            try:
                data = api_response.json()
                if isinstance(data, dict) and '@odata.context' in data:
                    print(f"📊 OData context: {data['@odata.context']}")
                if 'value' in data:
                    print(f"📋 Records available: {len(data['value'])}")
            except:
                print(f"📄 Response received (non-JSON)")
            
            return True
        else:
            print(f"❌ API endpoint failed: HTTP {api_response.status_code}")
            print(f"📄 Response: {api_response.text[:200]}")
            return False
    
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_wolf_with_multi_env():
    """Test Wolf with multi-environment extractor"""
    
    print("\n🔧 Testing with Multi-Environment Extractor")
    print("=" * 43)
    
    try:
        import os
        
        # Set Wolf credentials
        os.environ["WOLF_CLIENT_SECRET"] = "caaea1b9-b09b-4d28-83fe-09966d525243$LOFW4h5LpLvB3Z2FE0P7FiH4-C7qexeQPi22DBiHbz8="
        
        from multi_environment_metadata_extractor import MultiEnvironmentExtractor
        
        extractor = MultiEnvironmentExtractor()
        
        print("🔍 Testing Wolf environment connection...")
        result = extractor.test_environment_connection("wolf")
        
        if result["success"]:
            print(f"✅ Multi-env extractor: Wolf connection successful!")
            print(f"📊 Models discovered: {result['models_discovered']}")
            if result.get("models"):
                print(f"📋 Sample models: {', '.join(result['models'][:3])}")
            return True
        else:
            print(f"❌ Multi-env extractor: Wolf connection failed")
            print(f"Error: {result['error']}")
            return False
    
    except Exception as e:
        print(f"❌ Multi-env extractor error: {e}")
        return False

def main():
    """Main test function"""
    
    print("🚀 Wolf Environment Troubleshooting")
    print("=" * 37)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Test direct OAuth connection
    oauth_success = test_wolf_oauth()
    
    # Test with multi-environment extractor
    multi_env_success = test_wolf_with_multi_env()
    
    # Summary and recommendations
    print(f"\n📊 Test Results Summary")
    print("=" * 24)
    print(f"Direct OAuth Connection: {'✅' if oauth_success else '❌'}")
    print(f"Multi-Environment Extractor: {'✅' if multi_env_success else '❌'}")
    
    if oauth_success and multi_env_success:
        print(f"\n🎉 Wolf environment is working correctly!")
        print(f"\n💡 To access Wolf:")
        print("1. Don't use localhost (127.0.0.1) - Wolf connects to remote Datasphere")
        print("2. Run: python start_wolf_server.py")
        print("3. Or run: python run_three_environments.py (choose option 3)")
        print("4. Wolf connects to: https://ailien-test.eu20.hcs.cloud.sap")
    
    elif oauth_success and not multi_env_success:
        print(f"\n⚠️ OAuth works but multi-env extractor has issues")
        print("💡 Try running: python start_wolf_server.py directly")
    
    elif not oauth_success:
        print(f"\n❌ OAuth connection failed")
        print("💡 Check your internet connection and credentials")
        print("🔧 Verify the ailien-test environment is accessible")
    
    else:
        print(f"\n❌ Both tests failed")
        print("💡 There might be network or credential issues")

if __name__ == "__main__":
    main()