#!/usr/bin/env python3
"""
Test script for SAP Datasphere integration functionality
"""

import requests
import json
import time

def test_datasphere_integration():
    """Test the Datasphere integration endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing SAP Datasphere Integration")
    print("=" * 50)
    
    # Test 1: Basic API health check
    print("\n1. Testing basic API health...")
    try:
        response = requests.get(f"{base_url}/api/hello")
        if response.status_code == 200:
            print("✅ Basic API is working")
            data = response.json()
            print(f"   Message: {data.get('message')}")
        else:
            print(f"❌ Basic API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Basic API error: {e}")
    
    # Test 2: Datasphere connection
    print("\n2. Testing Datasphere connection...")
    try:
        connection_data = {
            "base_url": "https://demo-tenant.datasphere.cloud.sap",
            "space_id": "demo_space",
            "username": "demo_user"
        }
        
        response = requests.post(
            f"{base_url}/api/datasphere/connect",
            json=connection_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Datasphere connection successful")
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Message: {data.get('message')}")
            print(f"   Data Products Found: {data.get('total_products')}")
        else:
            print(f"❌ Datasphere connection failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Datasphere connection error: {e}")
    
    # Test 3: Get data products
    print("\n3. Testing data products retrieval...")
    try:
        response = requests.get(f"{base_url}/api/datasphere/products")
        
        if response.status_code == 200:
            print("✅ Data products retrieval successful")
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Total Products: {data.get('total_count')}")
            
            # Display first few products
            products = data.get('data_products', [])
            if products:
                print("\n   📊 Sample Data Products:")
                for i, product in enumerate(products[:3]):
                    print(f"   {i+1}. {product.get('name')} ({product.get('type')})")
                    print(f"      Description: {product.get('description')}")
                    print(f"      Rows: {product.get('row_count'):,}")
                    print(f"      Status: {product.get('status')}")
                    print()
        else:
            print(f"❌ Data products retrieval failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Data products retrieval error: {e}")
    
    # Test 4: System status
    print("\n4. Testing system status...")
    try:
        response = requests.get(f"{base_url}/api/status")
        if response.status_code == 200:
            print("✅ System status check successful")
            data = response.json()
            print(f"   Environment: {data.get('environment')}")
            print(f"   Features: {data.get('features')}")
        else:
            print(f"❌ System status check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ System status error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")
    print("\n💡 Next steps:")
    print("   - Open http://localhost:8000 in your browser")
    print("   - Click 'Connect to Datasphere' button")
    print("   - Click 'Get Data Products' button")
    print("   - Explore the data products interface")

def wait_for_server(base_url="http://localhost:8000", timeout=30):
    """Wait for the server to be ready"""
    print(f"⏳ Waiting for server at {base_url}...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{base_url}/health")
            if response.status_code == 200:
                print("✅ Server is ready!")
                return True
        except requests.exceptions.ConnectionError:
            pass
        
        time.sleep(1)
    
    print(f"❌ Server not ready after {timeout} seconds")
    return False

if __name__ == "__main__":
    print("🚀 SAP Datasphere Integration Test Suite")
    print("Make sure the Docker container is running on port 8000")
    print()
    
    # Wait for server to be ready
    if wait_for_server():
        test_datasphere_integration()
    else:
        print("❌ Cannot connect to server. Make sure Docker container is running:")
        print("   docker-compose up --build")