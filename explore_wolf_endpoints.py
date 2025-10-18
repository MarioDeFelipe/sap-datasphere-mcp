#!/usr/bin/env python3
"""
Explore Wolf Endpoints
Find what endpoints are accessible with current permissions
"""

import requests
import base64
import json
from datetime import datetime

class WolfExplorer:
    """Explore Wolf Datasphere endpoints"""
    
    def __init__(self):
        self.config = {
            "base_url": "https://ailien-test.eu20.hcs.cloud.sap",
            "oauth_client_id": "sb-60cb266e-ad9d-49f7-9967-b53b8286a259!b130936|client!b3944",
            "oauth_client_secret": "caaea1b9-b09b-4d28-83fe-09966d525243$LOFW4h5LpLvB3Z2FE0P7FiH4-C7qexeQPi22DBiHbz8=",
            "token_url": "https://ailien-test.authentication.eu20.hana.ondemand.com/oauth/token"
        }
        self.access_token = None
        self.get_access_token()
    
    def get_access_token(self):
        """Get OAuth access token"""
        
        client_id = self.config["oauth_client_id"]
        client_secret = self.config["oauth_client_secret"]
        token_url = self.config["token_url"]
        
        auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        
        headers = {
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {'grant_type': 'client_credentials'}
        
        response = requests.post(token_url, headers=headers, data=data, timeout=30)
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            print(f"✅ OAuth token obtained")
        else:
            raise Exception(f"OAuth failed: HTTP {response.status_code}")
    
    def test_endpoint(self, endpoint, description=""):
        """Test a specific endpoint"""
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json',
            'User-Agent': 'Wolf-Explorer/1.0'
        }
        
        url = f"{self.config['base_url']}{endpoint}"
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            result = {
                "endpoint": endpoint,
                "description": description,
                "status_code": response.status_code,
                "success": response.status_code < 400,
                "content_type": response.headers.get('content-type', 'unknown'),
                "response_size": len(response.content)
            }
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    result["data_preview"] = str(data)[:200] + "..." if len(str(data)) > 200 else str(data)
                    
                    if isinstance(data, dict):
                        if 'value' in data:
                            result["record_count"] = len(data['value'])
                        if '@odata.context' in data:
                            result["odata_context"] = data['@odata.context']
                
                except:
                    result["data_preview"] = response.text[:200] + "..." if len(response.text) > 200 else response.text
            
            elif response.status_code == 403:
                result["error"] = "Permission denied - user not authorized for this endpoint"
            elif response.status_code == 404:
                result["error"] = "Endpoint not found"
            else:
                result["error"] = response.text[:200] if response.text else f"HTTP {response.status_code}"
            
            return result
            
        except Exception as e:
            return {
                "endpoint": endpoint,
                "description": description,
                "success": False,
                "error": str(e)
            }
    
    def explore_all_endpoints(self):
        """Explore various endpoint patterns"""
        
        print("🔍 Exploring Wolf Datasphere Endpoints")
        print("=" * 40)
        
        # List of endpoints to test
        endpoints_to_test = [
            # Health and basic endpoints
            ("/health", "Health check"),
            ("/api/health", "API health check"),
            
            # Discovery endpoints
            ("/api/v1/datasphere", "Datasphere API root"),
            ("/api/v1/datasphere/consumption", "Consumption API root"),
            ("/api/v1/datasphere/consumption/analytical", "Analytical consumption root"),
            
            # Specific analytical models (the ones that worked before)
            ("/api/v1/datasphere/consumption/analytical/SAP_CONTENT", "SAP Content space"),
            ("/api/v1/datasphere/consumption/analytical/SAP_CONTENT/New_Analytic_Model_2", "New Analytic Model 2 service"),
            ("/api/v1/datasphere/consumption/analytical/SAP_CONTENT/New_Analytic_Model_2/New_Analytic_Model_2", "New Analytic Model 2 data"),
            ("/api/v1/datasphere/consumption/analytical/SAP_CONTENT/New_Analytic_Model_2/$metadata", "New Analytic Model 2 metadata"),
            
            # Alternative API patterns
            ("/api/v1/dwc/catalog", "DWC Catalog"),
            ("/api/v1/dwc/consumption", "DWC Consumption"),
            ("/dwaas-core/api/v1/catalog", "DWaaS Catalog"),
            ("/dwaas-core/api/v1/consumption", "DWaaS Consumption"),
            
            # Spaces and models
            ("/api/v1/datasphere/spaces", "Datasphere spaces"),
            ("/api/v1/datasphere/models", "Datasphere models"),
            ("/api/v1/datasphere/metadata", "Datasphere metadata"),
            
            # User and permissions
            ("/api/v1/user", "User information"),
            ("/api/v1/permissions", "User permissions"),
            ("/api/v1/scopes", "Available scopes")
        ]
        
        results = []
        working_endpoints = []
        permission_denied = []
        
        for endpoint, description in endpoints_to_test:
            print(f"\n🔍 Testing: {endpoint}")
            result = self.test_endpoint(endpoint, description)
            results.append(result)
            
            if result["success"]:
                print(f"✅ {endpoint}: HTTP {result['status_code']}")
                working_endpoints.append(result)
                
                if result.get("record_count") is not None:
                    print(f"   📊 Records: {result['record_count']}")
                if result.get("odata_context"):
                    print(f"   🔗 OData: {result['odata_context']}")
            
            elif result.get("status_code") == 403:
                print(f"🚫 {endpoint}: Permission denied")
                permission_denied.append(result)
            
            elif result.get("status_code") == 404:
                print(f"❌ {endpoint}: Not found")
            
            else:
                print(f"⚠️ {endpoint}: HTTP {result.get('status_code', 'Error')}")
        
        # Summary
        print(f"\n📊 Exploration Summary")
        print("=" * 22)
        print(f"✅ Working endpoints: {len(working_endpoints)}")
        print(f"🚫 Permission denied: {len(permission_denied)}")
        print(f"❌ Not found/Other: {len(results) - len(working_endpoints) - len(permission_denied)}")
        
        if working_endpoints:
            print(f"\n✅ Accessible Endpoints:")
            for endpoint in working_endpoints:
                print(f"  • {endpoint['endpoint']} - {endpoint['description']}")
        
        if permission_denied:
            print(f"\n🚫 Permission Denied Endpoints:")
            for endpoint in permission_denied:
                print(f"  • {endpoint['endpoint']} - {endpoint['description']}")
        
        # Save results
        with open(f'wolf_endpoint_exploration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "environment": self.config["base_url"],
                "total_tested": len(results),
                "working_endpoints": working_endpoints,
                "permission_denied": permission_denied,
                "all_results": results
            }, f, indent=2)
        
        print(f"\n📄 Detailed results saved to file")
        
        return working_endpoints, permission_denied
    
    def test_working_endpoints_with_data(self, working_endpoints):
        """Test working endpoints with sample data queries"""
        
        if not working_endpoints:
            print("No working endpoints to test with data")
            return
        
        print(f"\n📊 Testing Data Access on Working Endpoints")
        print("=" * 45)
        
        for endpoint_info in working_endpoints:
            endpoint = endpoint_info["endpoint"]
            
            # Skip non-data endpoints
            if any(skip in endpoint for skip in ['/health', '/api/v1/datasphere$']):
                continue
            
            print(f"\n🔍 Testing data access: {endpoint}")
            
            # Test with OData parameters
            params_to_test = [
                {},  # No parameters
                {'$top': 5},  # Limit results
                {'$top': 1, '$select': '*'},  # Limit and select
            ]
            
            for params in params_to_test:
                try:
                    headers = {
                        'Authorization': f'Bearer {self.access_token}',
                        'Accept': 'application/json',
                        'User-Agent': 'Wolf-Data-Explorer/1.0'
                    }
                    
                    url = f"{self.config['base_url']}{endpoint}"
                    response = requests.get(url, headers=headers, params=params, timeout=30)
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            
                            if isinstance(data, dict) and 'value' in data:
                                records = data['value']
                                print(f"✅ Data query successful: {len(records)} records")
                                
                                if records and len(records) > 0:
                                    sample_record = records[0]
                                    print(f"📋 Sample fields: {list(sample_record.keys())[:5]}")
                                
                                return {
                                    "endpoint": endpoint,
                                    "success": True,
                                    "record_count": len(records),
                                    "sample_data": records[:2] if records else None
                                }
                            else:
                                print(f"✅ Response received (non-OData format)")
                        
                        except json.JSONDecodeError:
                            print(f"✅ Non-JSON response received")
                    
                    elif response.status_code == 403:
                        print(f"🚫 Data access denied")
                    else:
                        print(f"⚠️ HTTP {response.status_code}")
                
                except Exception as e:
                    print(f"❌ Error: {e}")

def main():
    """Main exploration function"""
    
    print("🐺 Wolf Datasphere Endpoint Explorer")
    print("=" * 38)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    try:
        explorer = WolfExplorer()
        
        # Explore all endpoints
        working_endpoints, permission_denied = explorer.explore_all_endpoints()
        
        # Test data access on working endpoints
        if working_endpoints:
            explorer.test_working_endpoints_with_data(working_endpoints)
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        
        if working_endpoints:
            print("✅ Some endpoints are accessible - focus on these for data exploration")
            print("🔧 Use the working endpoints to build your analytical models interface")
        
        if permission_denied:
            print("🚫 Some endpoints require additional permissions")
            print("📞 Contact your Datasphere admin to request access to analytical models")
            print("🔑 You may need additional OAuth scopes or user permissions")
        
        print(f"\n🎯 Next Steps:")
        print("1. Use working endpoints to explore available data")
        print("2. Request additional permissions for blocked endpoints")
        print("3. Build interface around accessible endpoints")
        
    except Exception as e:
        print(f"❌ Exploration failed: {e}")

if __name__ == "__main__":
    main()