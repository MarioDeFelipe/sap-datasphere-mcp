#!/usr/bin/env python3
"""
Advanced API Testing - Try different authentication and header combinations
"""

import asyncio
import json
import httpx
import base64
from typing import Dict, List, Any

class AdvancedAPITester:
    """Test APIs with different authentication and header combinations"""
    
    def __init__(self):
        self.config = {
            "tenant_url": "https://ailien-test.eu20.hcs.cloud.sap",
            "oauth_config": {
                "client_id": "sb-60cb266e-ad9d-49f7-9967-b53b8286a259!b130936|client!b3944",
                "client_secret": "caaea1b9-b09b-4d28-83fe-09966d525243$LOFW4h5LpLvB3Z2FE0P7FiH4-C7qexeQPi22DBiHbz8=",
                "token_url": "https://ailien-test.authentication.eu20.hana.ondemand.com/oauth/token"
            }
        }
        
        # Test endpoints that returned HTML
        self.test_endpoints = [
            "/api/v1/spaces",
            "/sap/fpa/api/v1/spaces",
            "/dwaas-core/api/v1/spaces"
        ]
        
        self.client = None
        self.access_token = None
    
    async def setup(self):
        """Setup authentication"""
        self.client = httpx.AsyncClient(timeout=30)
        
        print("🔐 Getting OAuth token...")
        auth_string = f"{self.config['oauth_config']['client_id']}:{self.config['oauth_config']['client_secret']}"
        auth_b64 = base64.b64encode(auth_string.encode('ascii')).decode('ascii')
        
        headers = {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        
        data = {'grant_type': 'client_credentials'}
        response = await self.client.post(
            self.config['oauth_config']['token_url'], 
            headers=headers, 
            data=data
        )
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data['access_token']
            print("✅ OAuth token obtained!")
            print(f"🔍 Token preview: {self.access_token[:50]}...")
            return True
        else:
            print(f"❌ OAuth failed: {response.status_code}")
            return False
    
    async def test_different_headers(self, endpoint: str):
        """Test endpoint with different header combinations"""
        print(f"\n🧪 Testing {endpoint} with different headers:")
        
        # Different header combinations to try
        header_combinations = [
            {
                "name": "Standard JSON",
                "headers": {
                    'Authorization': f'Bearer {self.access_token}',
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            },
            {
                "name": "SAP Specific",
                "headers": {
                    'Authorization': f'Bearer {self.access_token}',
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'sap-client': '100'
                }
            },
            {
                "name": "OData Format",
                "headers": {
                    'Authorization': f'Bearer {self.access_token}',
                    'Accept': 'application/json;odata=verbose',
                    'Content-Type': 'application/json',
                    'DataServiceVersion': '2.0'
                }
            },
            {
                "name": "REST API Format",
                "headers": {
                    'Authorization': f'Bearer {self.access_token}',
                    'Accept': 'application/json, text/plain, */*',
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            },
            {
                "name": "CSRF Token Request",
                "headers": {
                    'Authorization': f'Bearer {self.access_token}',
                    'Accept': 'application/json',
                    'X-CSRF-Token': 'Fetch'
                }
            }
        ]
        
        results = []
        
        for combo in header_combinations:
            try:
                url = self.config['tenant_url'] + endpoint
                response = await self.client.get(url, headers=combo['headers'])
                
                content_type = response.headers.get('content-type', '')
                is_json = 'application/json' in content_type
                
                result = {
                    'header_type': combo['name'],
                    'status_code': response.status_code,
                    'content_type': content_type,
                    'is_json': is_json,
                    'response_size': len(response.content)
                }
                
                if is_json:
                    try:
                        data = response.json()
                        result['json_data'] = data
                        result['json_preview'] = str(data)[:200] + "..." if len(str(data)) > 200 else str(data)
                        print(f"  🎯 **{combo['name']}**: JSON! - {response.status_code}")
                        print(f"     📄 {result['json_preview']}")
                    except:
                        result['json_error'] = "Failed to parse JSON"
                        print(f"  ⚠️ **{combo['name']}**: JSON header but parse failed - {response.status_code}")
                else:
                    result['text_preview'] = response.text[:100] + "..." if len(response.text) > 100 else response.text
                    print(f"  📄 **{combo['name']}**: HTML/Text - {response.status_code}")
                
                results.append(result)
                
            except Exception as e:
                print(f"  ❌ **{combo['name']}**: Error - {str(e)}")
                results.append({
                    'header_type': combo['name'],
                    'error': str(e)
                })
        
        return results
    
    async def test_with_query_parameters(self, endpoint: str):
        """Test endpoint with different query parameters"""
        print(f"\n🔍 Testing {endpoint} with query parameters:")
        
        # Common query parameters for APIs
        param_combinations = [
            {"$format": "json"},
            {"format": "json"},
            {"accept": "json"},
            {"$top": "10"},
            {"limit": "10"},
            {"$select": "*"},
            {"fields": "*"},
            {"$format": "json", "$top": "5"},
            {"api": "true"},
            {"json": "true"}
        ]
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        json_responses = []
        
        for params in param_combinations:
            try:
                url = self.config['tenant_url'] + endpoint
                response = await self.client.get(url, headers=headers, params=params)
                
                content_type = response.headers.get('content-type', '')
                is_json = 'application/json' in content_type
                
                if is_json:
                    try:
                        data = response.json()
                        json_responses.append({
                            'params': params,
                            'data': data,
                            'status_code': response.status_code
                        })
                        print(f"  🎯 **Params {params}**: JSON! - {response.status_code}")
                        print(f"     📄 {str(data)[:150]}...")
                    except:
                        print(f"  ⚠️ **Params {params}**: JSON header but parse failed")
                else:
                    print(f"  📄 **Params {params}**: HTML/Text - {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ **Params {params}**: Error - {str(e)}")
        
        return json_responses
    
    async def test_different_methods(self, endpoint: str):
        """Test endpoint with different HTTP methods"""
        print(f"\n🔧 Testing {endpoint} with different HTTP methods:")
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        methods = ['GET', 'POST', 'OPTIONS']
        json_responses = []
        
        for method in methods:
            try:
                url = self.config['tenant_url'] + endpoint
                
                if method == 'GET':
                    response = await self.client.get(url, headers=headers)
                elif method == 'POST':
                    response = await self.client.post(url, headers=headers, json={})
                elif method == 'OPTIONS':
                    response = await self.client.options(url, headers=headers)
                
                content_type = response.headers.get('content-type', '')
                is_json = 'application/json' in content_type
                
                if is_json:
                    try:
                        data = response.json()
                        json_responses.append({
                            'method': method,
                            'data': data,
                            'status_code': response.status_code
                        })
                        print(f"  🎯 **{method}**: JSON! - {response.status_code}")
                        print(f"     📄 {str(data)[:150]}...")
                    except:
                        print(f"  ⚠️ **{method}**: JSON header but parse failed")
                else:
                    print(f"  📄 **{method}**: HTML/Text - {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ **{method}**: Error - {str(e)}")
        
        return json_responses
    
    async def run_advanced_tests(self):
        """Run all advanced API tests"""
        print("🧪 Advanced SAP Datasphere API Testing")
        print("🎯 Trying different authentication and header combinations")
        print("=" * 80)
        
        if not await self.setup():
            return
        
        all_json_responses = []
        
        for endpoint in self.test_endpoints:
            print(f"\n" + "=" * 60)
            print(f"🔍 TESTING ENDPOINT: {endpoint}")
            print("=" * 60)
            
            # Test different headers
            header_results = await self.test_different_headers(endpoint)
            
            # Test query parameters
            param_results = await self.test_with_query_parameters(endpoint)
            
            # Test different methods
            method_results = await self.test_different_methods(endpoint)
            
            # Collect JSON responses
            for result in header_results:
                if result.get('is_json') and 'json_data' in result:
                    all_json_responses.append({
                        'endpoint': endpoint,
                        'type': 'header_test',
                        'details': result
                    })
            
            for result in param_results:
                all_json_responses.append({
                    'endpoint': endpoint,
                    'type': 'param_test',
                    'details': result
                })
            
            for result in method_results:
                all_json_responses.append({
                    'endpoint': endpoint,
                    'type': 'method_test',
                    'details': result
                })
        
        # Final summary
        print(f"\n" + "=" * 80)
        print(f"🎯 ADVANCED TESTING RESULTS")
        print("=" * 80)
        print(f"✅ JSON responses found: {len(all_json_responses)}")
        
        if all_json_responses:
            print(f"\n🎉 SUCCESS: Found working JSON API configurations!")
            for i, response in enumerate(all_json_responses, 1):
                print(f"  {i}. {response['endpoint']} ({response['type']})")
                if 'json_preview' in response['details']:
                    print(f"     📄 {response['details']['json_preview']}")
        else:
            print(f"\n🔍 No JSON APIs found with current authentication")
            print(f"💡 May need different OAuth scopes or API access permissions")
        
        # Save results
        with open('advanced_api_test_results.json', 'w') as f:
            json.dump({
                'timestamp': '2025-10-15T21:20:00',
                'json_responses_found': len(all_json_responses),
                'successful_configurations': all_json_responses
            }, f, indent=2)
        
        print(f"\n💾 Results saved to: advanced_api_test_results.json")
        
        await self.client.aclose()
        return len(all_json_responses)

async def main():
    tester = AdvancedAPITester()
    json_count = await tester.run_advanced_tests()
    
    if json_count > 0:
        print(f"\n🚀 Found {json_count} working JSON API configurations!")
        print(f"📈 Ready to update MCP server with working endpoints")
    else:
        print(f"\n🔧 Need to investigate OAuth scopes or API permissions")
        print(f"💡 Consider checking SAP Datasphere admin console for API access settings")

if __name__ == "__main__":
    asyncio.run(main())