#!/usr/bin/env python3
"""
Inspect OData Response Details
The OData endpoints returned HTTP 200 - let's see what they contain
"""

import asyncio
import json
import httpx
import base64

class ODataInspector:
    """Inspect OData responses in detail"""
    
    def __init__(self):
        self.config = {
            "tenant_url": "https://ailien-test.eu20.hcs.cloud.sap",
            "technical_user_oauth": {
                "client_id": "sb-1d624427-f63c-4be1-8066-eee88b15ce05!b130936|client!b3944",
                "client_secret": "d3b8e5eb-d53f-4098-8f02-cc5457d39853$d49IM8txqwwEdMzEeWdRLOuCpzjUYSwAFQcptIVAT1o=",
                "token_url": "https://ailien-test.authentication.eu20.hana.ondemand.com/oauth/token"
            }
        }
        
        # OData endpoints that returned HTTP 200
        self.odata_endpoints = [
            "/sap/opu/odata/sap/DWC_SPACE_SRV/Spaces",
            "/sap/opu/odata/sap/DWC_CONNECTION_SRV/Connections",
            "/sap/opu/odata/sap/DWC_CATALOG_SRV/Catalog"
        ]
        
        self.client = None
        self.access_token = None
    
    async def setup(self):
        """Get OAuth token"""
        self.client = httpx.AsyncClient(timeout=30)
        
        print("🔐 Getting OAuth token...")
        auth_string = f"{self.config['technical_user_oauth']['client_id']}:{self.config['technical_user_oauth']['client_secret']}"
        auth_b64 = base64.b64encode(auth_string.encode('ascii')).decode('ascii')
        
        headers = {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        
        data = {'grant_type': 'client_credentials'}
        response = await self.client.post(
            self.config['technical_user_oauth']['token_url'], 
            headers=headers, 
            data=data
        )
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data['access_token']
            print("✅ OAuth token obtained!")
            return True
        else:
            print(f"❌ OAuth failed: {response.status_code}")
            return False
    
    async def inspect_endpoint_detailed(self, endpoint: str):
        """Inspect endpoint with multiple header combinations"""
        print(f"\n🔍 Detailed Inspection: {endpoint}")
        print("=" * 60)
        
        # Different header combinations to try
        header_sets = [
            {
                "name": "Standard JSON",
                "headers": {
                    'Authorization': f'Bearer {self.access_token}',
                    'Accept': 'application/json'
                }
            },
            {
                "name": "OData Verbose",
                "headers": {
                    'Authorization': f'Bearer {self.access_token}',
                    'Accept': 'application/json;odata=verbose'
                }
            },
            {
                "name": "OData Minimal",
                "headers": {
                    'Authorization': f'Bearer {self.access_token}',
                    'Accept': 'application/json;odata=minimalmetadata'
                }
            },
            {
                "name": "XML Format",
                "headers": {
                    'Authorization': f'Bearer {self.access_token}',
                    'Accept': 'application/xml'
                }
            },
            {
                "name": "Any Format",
                "headers": {
                    'Authorization': f'Bearer {self.access_token}',
                    'Accept': '*/*'
                }
            }
        ]
        
        for header_set in header_sets:
            try:
                url = self.config['tenant_url'] + endpoint
                response = await self.client.get(url, headers=header_set['headers'])
                
                content_type = response.headers.get('content-type', '')
                
                print(f"\n📋 {header_set['name']}:")
                print(f"   Status: {response.status_code}")
                print(f"   Content-Type: {content_type}")
                print(f"   Size: {len(response.content)} bytes")
                
                # Show response content
                if 'application/json' in content_type:
                    try:
                        data = response.json()
                        print(f"   📄 JSON Data: {str(data)[:300]}...")
                        if isinstance(data, dict):
                            print(f"   🔑 Keys: {list(data.keys())}")
                    except:
                        print(f"   ⚠️ JSON parse failed")
                        print(f"   📄 Raw: {response.text[:300]}...")
                elif 'application/xml' in content_type:
                    print(f"   📄 XML Data: {response.text[:300]}...")
                elif 'text/html' in content_type:
                    print(f"   📄 HTML: {response.text[:200]}...")
                else:
                    print(f"   📄 Raw: {response.text[:300]}...")
                
                # Check for specific patterns
                text = response.text.lower()
                if 'space' in text:
                    print(f"   ✨ Contains 'space' data!")
                if 'connection' in text:
                    print(f"   ✨ Contains 'connection' data!")
                if 'catalog' in text or 'table' in text:
                    print(f"   ✨ Contains 'catalog/table' data!")
                if 'error' in text:
                    print(f"   ⚠️ Contains error message")
                if 'login' in text or 'authentication' in text:
                    print(f"   🔐 Requires authentication")
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
    
    async def test_metadata_endpoints(self):
        """Test OData metadata endpoints"""
        print(f"\n📊 Testing OData Metadata Endpoints")
        print("=" * 60)
        
        for endpoint in self.odata_endpoints:
            metadata_endpoint = endpoint + "/$metadata"
            
            try:
                headers = {
                    'Authorization': f'Bearer {self.access_token}',
                    'Accept': 'application/xml'
                }
                
                url = self.config['tenant_url'] + metadata_endpoint
                response = await self.client.get(url, headers=headers)
                
                print(f"\n🔍 {metadata_endpoint}:")
                print(f"   Status: {response.status_code}")
                print(f"   Content-Type: {response.headers.get('content-type', '')}")
                
                if response.status_code == 200:
                    text = response.text
                    if 'EntitySet' in text or 'EntityType' in text:
                        print(f"   ✅ Valid OData metadata!")
                        print(f"   📄 Preview: {text[:200]}...")
                    else:
                        print(f"   📄 Response: {text[:200]}...")
                else:
                    print(f"   ❌ Failed: {response.text[:200]}...")
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
    
    async def run_inspection(self):
        """Run complete OData inspection"""
        print("🔍 SAP Datasphere OData Response Inspection")
        print("🎯 Analyzing HTTP 200 responses from OData endpoints")
        print("=" * 80)
        
        if not await self.setup():
            return
        
        # Inspect each endpoint in detail
        for endpoint in self.odata_endpoints:
            await self.inspect_endpoint_detailed(endpoint)
        
        # Test metadata endpoints
        await self.test_metadata_endpoints()
        
        print(f"\n" + "=" * 80)
        print(f"🎯 INSPECTION COMPLETE")
        print("=" * 80)
        print(f"💡 Check the output above for any working data endpoints")
        print(f"🔍 Look for JSON responses or valid XML/OData content")
        
        await self.client.aclose()

async def main():
    """Main inspection"""
    inspector = ODataInspector()
    await inspector.run_inspection()

if __name__ == "__main__":
    asyncio.run(main())