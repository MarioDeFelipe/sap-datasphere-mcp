#!/usr/bin/env python3
"""
Test the deployed Datasphere Control Panel
"""

import requests
import time
import boto3

def wait_for_function_ready():
    """Wait for Lambda function to be ready"""
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    function_name = 'datasphere-control-panel'
    
    print("⏳ Waiting for Lambda function to be ready...")
    
    for i in range(30):  # Wait up to 5 minutes
        try:
            response = lambda_client.get_function(FunctionName=function_name)
            state = response['Configuration']['State']
            
            if state == 'Active':
                print("✅ Lambda function is ready!")
                return True
            elif state == 'Failed':
                print(f"❌ Lambda function failed: {response['Configuration'].get('StateReason', 'Unknown error')}")
                return False
            else:
                print(f"⏳ Function state: {state}, waiting...")
                time.sleep(10)
                
        except Exception as e:
            print(f"❌ Error checking function state: {e}")
            return False
    
    print("❌ Timeout waiting for function to be ready")
    return False

def test_control_panel():
    """Test the control panel endpoints"""
    
    base_url = "https://krb7735xufadsj233kdnpaabta0eatck.lambda-url.us-east-1.on.aws"
    
    print("🧪 Testing SAP Datasphere Control Panel")
    print("=" * 50)
    print(f"🔗 URL: {base_url}")
    
    # Test main dashboard
    print("\n📊 Testing dashboard...")
    try:
        response = requests.get(base_url, timeout=30)
        if response.status_code == 200:
            print("✅ Dashboard loaded successfully")
            print(f"   Content length: {len(response.text)} characters")
        else:
            print(f"❌ Dashboard failed: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")
    
    # Test API endpoints
    endpoints = [
        ("/api/status", "System Status"),
        ("/api/glue/tables", "Glue Tables"),
        ("/api/assets", "Datasphere Assets")
    ]
    
    for endpoint, name in endpoints:
        print(f"\n🔧 Testing {name}...")
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=30)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {name} API working")
                
                if endpoint == "/api/status":
                    print(f"   Datasphere: {data.get('datasphere_status', 'unknown')}")
                    print(f"   Glue: {data.get('glue_status', 'unknown')}")
                elif endpoint == "/api/glue/tables":
                    print(f"   Found {len(data)} Glue tables")
                elif endpoint == "/api/assets":
                    if isinstance(data, list):
                        print(f"   Found {len(data)} Datasphere assets")
                    else:
                        print(f"   Response: {data}")
                        
            else:
                print(f"❌ {name} failed: HTTP {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ {name} test failed: {e}")
    
    print(f"\n🎯 CONTROL PANEL ACCESS:")
    print(f"🔗 {base_url}")
    print(f"\n📋 Available Features:")
    print(f"  • Asset Discovery - Explore your Datasphere catalog")
    print(f"  • Sync Management - Synchronize to AWS Glue")
    print(f"  • Data Preview - Sample data from assets")
    print(f"  • System Status - Monitor integration health")

if __name__ == "__main__":
    # Wait for function to be ready
    if wait_for_function_ready():
        # Test the control panel
        test_control_panel()
    else:
        print("❌ Cannot test control panel - function not ready")