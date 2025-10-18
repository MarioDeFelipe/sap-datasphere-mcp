#!/usr/bin/env python3
"""
Real API Discovery - Find actual JSON REST APIs vs HTML pages
"""

import asyncio
import json
import httpx
import base64
from typing import Dict, List, Any

class RealAPIDiscovery:
    """Discover actual REST APIs that return JSON, not HTML pages"""
    
    def __init__(self):
        self.config = {
            "tenant_url": "https://ailien-test.eu20.hcs.cloud.sap",
            "oauth_config": {
                "client_id": "sb-<subaccount-uuid>!b<n>|client!b<n>",
                "client_secret": "<your-client-secret>",
                "token_url": "https://ailien-test.authentication.eu20.hana.ondemand.com/oauth/token"
            }
        }
        
        # More targeted API patterns based on SAP Datasphere documentation
        self.api_patterns = [
            # Core Datasphere APIs
            "/dwaas-core/api/v1/spaces",
            "/dwaas-core/api/v1/connections", 
            "/dwaas-core/api/v1/catalog",
            "/dwaas-core/api/v1/models",
            "/dwaas-core/api/v1/datasets",
            
            # Analytics Cloud APIs (FPA)
            "/sap/fpa/services/rest/epm/contentlib/v1/spaces",
            "/sap/fpa/services/rest/epm/contentlib/v1/models",
            "/sap/fpa/services/rest/epm/contentlib/v1/datasets",
            
            # Data Warehouse Cloud APIs
            "/sap/dwc/api/v1/spaces",
            "/sap/dwc/api/v1/connections",
            "/sap/dwc/api/v1/catalog",
            
            # OData Services
            "/sap/opu/odata/sap/DWC_SPACE_SRV/Spaces",
            "/sap/opu/odata/sap/DWC_CONNECTION_SRV/Connections",
            "/sap/opu/odata/sap/DWC_CATALOG_SRV/Catalog",
            
            # REST Services
            "/sap/bc/rest/dwc/v1/spaces",
            "/sap/bc/rest/dwc/v1/connections",
            "/sap/bc/rest/dwc/v1/catalog",
            
            # Platform APIs
            "/api/platform/v1/spaces",
            "/api/platform/v1/connections",
            "/api/datasphere/v1/spaces",
            "/api/datasphere/v1/connections",
            
            # Service-specific endpoints
            "/services/api/v1/spaces",
            "/services/api/v1/connections",
            "/services/rest/v1/spaces",
            "/services/rest/v1/connections"
        ]
        
        self.client = None
        self.access_token = None
    
    async def setup(self):
        """Setup authentication"""
        self.client = httpx.AsyncClient(timeout=30)
        
        print("🔐 Authenticating...")
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
            print("✅ Authentication successful!")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return False
    
    async def test_endpoint(self, endpoint: str) -> Dict[str, Any]:
        """Test a single endpoint and analyze the response"""
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        try:
            url = self.config['tenant_url'] + endpoint
            response = await self.client.get(url, headers=headers)
            
            result = {
                'endpoint': endpoint,
                'status_code': response.status_code,
                'success': response.status_code < 400,
                'content_type': response.headers.get('content-type', ''),
                'is_json': False,
                'is_html': False,
                'response_size': len(response.content),
                'error': None
            }
            
            # Analyze response type
            content_type = response.headers.get('content-type', '').lower()
            
            if 'application/json' in content_type:
                result['is_json'] = True
                try:
                    data = response.json()
                    result['json_preview'] = str(data)[:200] + "..." if len(str(data)) > 200 else str(data)
                    result['json_keys'] = list(data.keys()) if isinstance(data, dict) else None
                except:
                    result['json_error'] = "Failed to parse JSON"
            
            elif 'text/html' in content_type or response.text.strip().startswith('<'):
                result['is_html'] = True
                result['html_preview'] = response.text[:100] + "..."
            
            else:
                result['text_preview'] = response.text[:200] + "..." if len(response.text) > 200 else response.text
            
            return result
            
        except Exception as e:
            return {
                'endpoint': endpoint,
                'status_code': None,
                'success': False,
                'error': str(e)
            }
    
    async def discover_real_apis(self):
        """Discover actual JSON REST APIs"""
        print("\n🔍 Discovering Real JSON REST APIs")
        print("=" * 60)
        
        results = []
        json_apis = []
        html_pages = []
        errors = []
        
        for endpoint in self.api_patterns:
            result = await self.test_endpoint(endpoint)
            results.append(result)
            
            if result['success']:
                if result.get('is_json'):
                    json_apis.append(result)
                    print(f"  🎯 **JSON API:** {endpoint} - {result['status_code']}")
                    if 'json_preview' in result:
                        print(f"     📄 {result['json_preview']}")
                elif result.get('is_html'):
                    html_pages.append(result)
                    print(f"  📄 HTML Page: {endpoint} - {result['status_code']}")
                else:
                    print(f"  ❓ Unknown: {endpoint} - {result['status_code']} ({result['content_type']})")
            else:
                if result['status_code'] == 401:
                    print(f"  🔐 Auth needed: {endpoint} - 401")
                elif result['status_code'] == 404:
                    print(f"  ❌ Not found: {endpoint} - 404")
                else:
                    errors.append(result)
                    print(f"  ❌ Error: {endpoint} - {result.get('status_code', 'Exception')}")
        
        # Summary
        print(f"\n📊 DISCOVERY SUMMARY:")
        print(f"  🎯 JSON APIs found: {len(json_apis)}")
        print(f"  📄 HTML pages: {len(html_pages)}")
        print(f"  ❌ Errors/404s: {len(errors)}")
        print(f"  📊 Total tested: {len(results)}")
        
        if json_apis:
            print(f"\n✨ REAL JSON APIs DISCOVERED:")
            for api in json_apis:
                print(f"  • {api['endpoint']} - {api['content_type']}")
                if 'json_keys' in api and api['json_keys']:
                    print(f"    Keys: {api['json_keys']}")
        
        # Save results
        with open('real_api_discovery_results.json', 'w') as f:
            json.dump({
                'timestamp': '2025-10-15T21:15:00',
                'total_tested': len(results),
                'json_apis': len(json_apis),
                'html_pages': len(html_pages),
                'errors': len(errors),
                'results': results,
                'discovered_json_apis': json_apis
            }, f, indent=2)
        
        print(f"\n💾 Results saved to: real_api_discovery_results.json")
        
        return json_apis, html_pages, errors
    
    async def test_common_rest_patterns(self):
        """Test common REST API patterns that might work"""
        print(f"\n🎯 Testing Common REST Patterns")
        print("=" * 60)
        
        # Common REST patterns for enterprise APIs
        rest_patterns = [
            "/rest/v1/spaces",
            "/rest/v2/spaces", 
            "/rest/api/v1/spaces",
            "/restapi/v1/spaces",
            "/webapi/v1/spaces",
            "/service/v1/spaces",
            "/services/v1/spaces",
            "/ws/v1/spaces",
            "/webservice/v1/spaces"
        ]
        
        json_found = []
        
        for pattern in rest_patterns:
            result = await self.test_endpoint(pattern)
            if result['success'] and result.get('is_json'):
                json_found.append(result)
                print(f"  🎯 **JSON API:** {pattern}")
            elif result['success']:
                print(f"  📄 Non-JSON: {pattern} ({result['content_type']})")
            else:
                print(f"  ❌ Failed: {pattern}")
        
        return json_found
    
    async def run_discovery(self):
        """Run complete API discovery"""
        print("🔍 SAP Datasphere Real API Discovery")
        print("🎯 Finding actual JSON REST APIs (not HTML pages)")
        print("=" * 80)
        
        if not await self.setup():
            return
        
        # Main discovery
        json_apis, html_pages, errors = await self.discover_real_apis()
        
        # Test additional patterns
        additional_apis = await self.test_common_rest_patterns()
        
        # Final summary
        total_json_apis = len(json_apis) + len(additional_apis)
        
        print(f"\n" + "=" * 80)
        print(f"🎯 FINAL DISCOVERY RESULTS")
        print(f"=" * 80)
        print(f"✅ Real JSON APIs found: {total_json_apis}")
        print(f"📄 HTML pages (UI endpoints): {len(html_pages)}")
        print(f"❌ Failed endpoints: {len(errors)}")
        
        if total_json_apis > 0:
            print(f"\n🎉 SUCCESS: Found {total_json_apis} working JSON APIs!")
            print(f"📈 This gives us real data endpoints for the MCP server")
        else:
            print(f"\n🔍 No JSON APIs found - may need different authentication or endpoint patterns")
            print(f"💡 Consider checking SAP Datasphere API documentation for correct paths")
        
        await self.client.aclose()
        return total_json_apis

async def main():
    discovery = RealAPIDiscovery()
    api_count = await discovery.run_discovery()
    
    if api_count > 0:
        print(f"\n🚀 Ready to update MCP server with {api_count} working JSON APIs!")
    else:
        print(f"\n🔧 Need to investigate further - check SAP documentation for API paths")

if __name__ == "__main__":
    asyncio.run(main())