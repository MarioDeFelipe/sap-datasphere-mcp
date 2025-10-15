#!/usr/bin/env python3
"""
Quick test without dependencies to verify OAuth
"""

import asyncio
import httpx
import base64
import json


async def quick_oauth_test():
    """Quick OAuth test with your credentials"""
    
    print("🚀 Quick OAuth Test")
    print("=" * 30)
    
    # Load credentials from environment or use placeholders
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    client_id = os.getenv("OAUTH_CLIENT_ID", "your-client-id-here")
    client_secret = os.getenv("OAUTH_CLIENT_SECRET", "your-client-secret-here")
    token_url = os.getenv("OAUTH_TOKEN_URL", "https://your-auth.authentication.eu20.hana.ondemand.com/oauth/token")
    tenant_url = os.getenv("DATASPHERE_TENANT_URL", "https://your-tenant.eu10.hcs.cloud.sap")
    
    async with httpx.AsyncClient() as client:
        try:
            # Get OAuth token
            print("🔐 Getting OAuth token...")
            
            auth_string = f"{client_id}:{client_secret}"
            auth_b64 = base64.b64encode(auth_string.encode('ascii')).decode('ascii')
            
            headers = {
                'Authorization': f'Basic {auth_b64}',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
            
            data = {'grant_type': 'client_credentials'}
            
            response = await client.post(token_url, headers=headers, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data['access_token']
                print("✅ OAuth token obtained!")
                print(f"   Expires in: {token_data.get('expires_in', 'unknown')} seconds")
                
                # Test a few API endpoints
                print("\n🔍 Testing API endpoints...")
                
                api_headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Accept': 'application/json'
                }
                
                test_endpoints = [
                    "/api/v1/spaces",
                    "/dwaas-core/api/v1/spaces", 
                    "/dwc/api/v1/spaces",
                    "/api/v1/catalog",
                    "/health"
                ]
                
                working_endpoints = []
                
                for endpoint in test_endpoints:
                    try:
                        url = tenant_url + endpoint
                        resp = await client.get(url, headers=api_headers, timeout=10)
                        
                        if resp.status_code < 400:
                            working_endpoints.append(endpoint)
                            print(f"✅ {endpoint}: {resp.status_code}")
                        else:
                            print(f"❌ {endpoint}: {resp.status_code}")
                            
                    except Exception as e:
                        print(f"❌ {endpoint}: {type(e).__name__}")
                
                if working_endpoints:
                    print(f"\n🎉 Found {len(working_endpoints)} working endpoints!")
                else:
                    print(f"\n⚠️ No working endpoints found")
                    print(f"   OAuth is working, but need to find correct API paths")
                
            else:
                print(f"❌ OAuth failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    asyncio.run(quick_oauth_test())