#!/usr/bin/env python3
"""
Enhanced SAP Datasphere API Discovery
Advanced endpoint discovery with tenant-specific patterns and detailed analysis
"""

import asyncio
import httpx
import base64
import json
import re
from urllib.parse import urlparse
from datetime import datetime

# Your working OAuth credentials
OAUTH_CONFIG = {
    "client_id": "sb-60cb266e-ad9d-49f7-9967-b53b8286a259!b130936|client!b3944",
    "client_secret": "caaea1b9-b09b-4d28-83fe-09966d525243$LOFW4h5LpLvB3Z2FE0P7FiH4-C7qexeQPi22DBiHbz8=",
    "token_url": "https://ailien-test.authentication.eu20.hana.ondemand.com/oauth/token",
    "tenant_url": "https://f45fa9cc-f4b5-4126-ab73-b19b578fb17a.eu10.hcs.cloud.sap",
    "tenant_id": "f45fa9cc-f4b5-4126-ab73-b19b578fb17a"
}

class EnhancedAPIDiscovery:
    """Enhanced API discovery with comprehensive endpoint testing"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30)
        self.access_token = None
        self.results = {
            "discovery_date": datetime.now().isoformat(),
            "tenant_info": OAUTH_CONFIG,
            "endpoints_tested": 0,
            "working_endpoints": [],
            "interesting_responses": [],
            "error_patterns": {},
            "recommendations": []
        }
    
    async def get_oauth_token(self):
        """Get OAuth access token"""
        print("🔐 Getting OAuth token...")
        
        auth_string = f"{OAUTH_CONFIG['client_id']}:{OAUTH_CONFIG['client_secret']}"
        auth_b64 = base64.b64encode(auth_string.encode('ascii')).decode('ascii')
        
        headers = {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        
        data = {'grant_type': 'client_credentials'}
        
        response = await self.client.post(OAUTH_CONFIG['token_url'], headers=headers, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data['access_token']
            print(f"✅ OAuth token obtained (expires in {token_data.get('expires_in', 'unknown')} seconds)")
            return True
        else:
            print(f"❌ OAuth failed: {response.status_code} - {response.text}")
            return False
    
    def generate_comprehensive_endpoints(self):
        """Generate comprehensive list of potential API endpoints"""
        
        tenant_id = OAUTH_CONFIG['tenant_id']
        region = "eu10"  # Extracted from tenant URL
        
        # Base patterns
        base_patterns = [
            # Standard REST API patterns
            "/api/v1/{resource}",
            "/api/v2/{resource}",
            "/rest/v1/{resource}",
            "/rest/v2/{resource}",
            
            # SAP-specific patterns
            "/sap/api/v1/{resource}",
            "/sap/bc/rest/{resource}",
            "/sap/opu/odata/sap/{resource}",
            
            # Datasphere-specific patterns
            "/dwaas-core/api/v1/{resource}",
            "/dwc/api/v1/{resource}",
            "/datasphere/api/v1/{resource}",
            "/ds/api/v1/{resource}",
            
            # Tenant-specific patterns
            f"/tenant/{tenant_id}/api/v1/{{resource}}",
            f"/{tenant_id}/api/v1/{{resource}}",
            f"/{region}/api/v1/{{resource}}",
            
            # Cloud Platform patterns
            "/scp/api/v1/{resource}",
            "/cf/api/v1/{resource}",
            "/btp/api/v1/{resource}",
            
            # OData patterns
            "/odata/v4/{resource}",
            "/odata/{resource}",
            f"/odata/v4/{tenant_id}/{{resource}}",
            
            # Service-specific patterns
            "/services/api/v1/{resource}",
            "/platform/api/v1/{resource}",
            "/core/api/v1/{resource}"
        ]
        
        # Resources to test
        resources = [
            "spaces", "catalog", "connections", "models", "tables", "views",
            "users", "permissions", "tasks", "jobs", "metadata", "schemas",
            "health", "info", "version", "status", "ping"
        ]
        
        # Generate all combinations
        endpoints = []
        for pattern in base_patterns:
            for resource in resources:
                endpoint = pattern.format(resource=resource)
                endpoints.append(endpoint)
        
        # Add specific known patterns
        specific_endpoints = [
            # Discovery endpoints
            "/.well-known/api",
            "/.well-known/openapi",
            "/swagger.json",
            "/openapi.json",
            "/api-docs",
            "/docs",
            
            # Health endpoints
            "/health",
            "/healthz", 
            "/status",
            "/ping",
            "/info",
            "/version",
            
            # Root API endpoints
            "/api",
            "/api/v1",
            "/api/v2",
            
            # SAP-specific service endpoints
            "/sap/bc/rest/dwaas/v1/spaces",
            "/sap/opu/odata/sap/DWC_SPACES_SRV",
            "/sap/opu/odata/sap/DWC_CATALOG_SRV",
            "/sap/opu/odata/sap/DWAAS_SPACES_SRV",
            "/sap/opu/odata/sap/DWAAS_CATALOG_SRV"
        ]
        
        endpoints.extend(specific_endpoints)
        
        # Remove duplicates and sort
        endpoints = sorted(list(set(endpoints)))
        
        print(f"📋 Generated {len(endpoints)} endpoints to test")
        return endpoints
    
    async def test_endpoint(self, endpoint):
        """Test a single endpoint with detailed analysis"""
        
        url = OAUTH_CONFIG['tenant_url'] + endpoint
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json',
            'User-Agent': 'SAP-Datasphere-MCP-Enhanced-Discovery/1.0'
        }
        
        try:
            response = await self.client.get(url, headers=headers)
            
            result = {
                'endpoint': endpoint,
                'url': url,
                'status_code': response.status_code,
                'content_type': response.headers.get('content-type', 'unknown'),
                'content_length': len(response.content),
                'response_time': response.elapsed.total_seconds() if hasattr(response, 'elapsed') else 0
            }
            
            # Analyze response
            if response.status_code < 400:
                result['success'] = True
                result['category'] = 'working'
                
                # Try to parse JSON response
                try:
                    if 'json' in result['content_type']:
                        data = response.json()
                        result['response_structure'] = self.analyze_json_structure(data)
                        result['sample_data'] = data if len(str(data)) < 1000 else str(data)[:1000] + "..."
                except:
                    result['response_text'] = response.text[:500] if response.text else ""
                
                self.results['working_endpoints'].append(result)
                
            elif response.status_code == 401:
                result['success'] = False
                result['category'] = 'auth_required'
                result['note'] = 'Authentication required - OAuth might need different scopes'
                
            elif response.status_code == 403:
                result['success'] = False
                result['category'] = 'forbidden'
                result['note'] = 'Forbidden - OAuth client might need additional permissions'
                
            elif response.status_code == 404:
                result['success'] = False
                result['category'] = 'not_found'
                result['note'] = 'Endpoint does not exist'
                
            else:
                result['success'] = False
                result['category'] = 'other_error'
                result['note'] = f'HTTP {response.status_code}: {response.text[:200]}'
            
            # Track error patterns
            if not result['success']:
                error_key = f"{response.status_code}_{result['category']}"
                if error_key not in self.results['error_patterns']:
                    self.results['error_patterns'][error_key] = 0
                self.results['error_patterns'][error_key] += 1
            
            # Check for interesting responses (non-404 errors)
            if response.status_code not in [404] and not result['success']:
                self.results['interesting_responses'].append(result)
            
            return result
            
        except Exception as e:
            return {
                'endpoint': endpoint,
                'url': url,
                'success': False,
                'category': 'exception',
                'error': str(e)
            }
    
    def analyze_json_structure(self, data):
        """Analyze JSON response structure"""
        if isinstance(data, dict):
            return {
                'type': 'object',
                'keys': list(data.keys())[:10],  # First 10 keys
                'key_count': len(data.keys())
            }
        elif isinstance(data, list):
            return {
                'type': 'array',
                'length': len(data),
                'sample_item': data[0] if data else None
            }
        else:
            return {
                'type': type(data).__name__,
                'value': str(data)[:100]
            }
    
    async def run_discovery(self):
        """Run comprehensive API discovery"""
        
        print("🚀 Enhanced SAP Datasphere API Discovery")
        print("=" * 60)
        
        # Get OAuth token
        if not await self.get_oauth_token():
            return
        
        # Generate endpoints to test
        endpoints = self.generate_comprehensive_endpoints()
        self.results['endpoints_tested'] = len(endpoints)
        
        print(f"\n🔍 Testing {len(endpoints)} endpoints...")
        print("This may take a few minutes...")
        
        # Test endpoints in batches
        batch_size = 10
        for i in range(0, len(endpoints), batch_size):
            batch = endpoints[i:i + batch_size]
            
            # Test batch concurrently
            tasks = [self.test_endpoint(endpoint) for endpoint in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Progress update
            progress = min(i + batch_size, len(endpoints))
            print(f"  Progress: {progress}/{len(endpoints)} ({progress/len(endpoints)*100:.1f}%)")
        
        await self.analyze_results()
        await self.generate_recommendations()
        
        # Save results
        with open('enhanced_discovery_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: enhanced_discovery_results.json")
    
    async def analyze_results(self):
        """Analyze discovery results"""
        
        working = len(self.results['working_endpoints'])
        interesting = len(self.results['interesting_responses'])
        total = self.results['endpoints_tested']
        
        print(f"\n📊 Discovery Results:")
        print(f"   Total endpoints tested: {total}")
        print(f"   Working endpoints: {working}")
        print(f"   Interesting responses: {interesting}")
        print(f"   Success rate: {working/total*100:.1f}%")
        
        if working > 0:
            print(f"\n✅ Working Endpoints Found:")
            for endpoint in self.results['working_endpoints']:
                print(f"   • {endpoint['endpoint']} (HTTP {endpoint['status_code']})")
                if 'response_structure' in endpoint:
                    struct = endpoint['response_structure']
                    if struct['type'] == 'array':
                        print(f"     → Array with {struct['length']} items")
                    elif struct['type'] == 'object':
                        print(f"     → Object with keys: {struct['keys'][:3]}")
        
        if interesting > 0:
            print(f"\n⚠️ Interesting Responses (Non-404 errors):")
            for resp in self.results['interesting_responses']:
                print(f"   • {resp['endpoint']} → HTTP {resp['status_code']} ({resp['category']})")
        
        print(f"\n📈 Error Pattern Analysis:")
        for pattern, count in self.results['error_patterns'].items():
            print(f"   • {pattern}: {count} occurrences")
    
    async def generate_recommendations(self):
        """Generate recommendations based on results"""
        
        recommendations = []
        
        working_count = len(self.results['working_endpoints'])
        interesting_count = len(self.results['interesting_responses'])
        
        if working_count == 0:
            recommendations.extend([
                "No working API endpoints found with current OAuth token",
                "Check OAuth client permissions in SAP Datasphere admin console",
                "Verify API access is enabled for your OAuth client",
                "Contact SAP administrator for API endpoint documentation"
            ])
        
        if interesting_count > 0:
            recommendations.extend([
                f"Found {interesting_count} endpoints with non-404 responses",
                "These endpoints exist but may require different permissions",
                "Check OAuth scopes and client configuration",
                "Some endpoints might require space-specific context"
            ])
        
        # Check for auth-related errors
        auth_errors = sum(count for pattern, count in self.results['error_patterns'].items() 
                         if '401' in pattern or '403' in pattern)
        
        if auth_errors > 0:
            recommendations.extend([
                f"Found {auth_errors} authentication/authorization errors",
                "OAuth client may need additional API scopes",
                "Check 'Technical User' configuration in Datasphere",
                "Verify OAuth client has 'API Access' permissions"
            ])
        
        self.results['recommendations'] = recommendations
        
        if recommendations:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Main discovery function"""
    
    discovery = EnhancedAPIDiscovery()
    
    try:
        await discovery.run_discovery()
        
        print(f"\n🎯 Next Steps:")
        print(f"1. Review enhanced_discovery_results.json for detailed analysis")
        print(f"2. Check SAP Datasphere admin console for API documentation")
        print(f"3. Test any working endpoints with different parameters")
        print(f"4. Contact SAP support if no endpoints are working")
        
    finally:
        await discovery.close()

if __name__ == "__main__":
    asyncio.run(main())