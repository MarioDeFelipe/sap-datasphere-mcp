#!/usr/bin/env python3
"""
Start Wolf Environment Server
Starts the Wolf (Staging) Datasphere environment with basic auth credentials
"""

import os
import sys
import json
import requests
import base64
from datetime import datetime
from typing import Dict, Any

# Wolf Environment Configuration - Updated to Ailien Environment
WOLF_CONFIG = {
    "name": "wolf",
    "display_name": "Wolf (Staging)",
    "base_url": "https://ailien-test.eu20.hcs.cloud.sap",
    "oauth_client_id": "sb-60cb266e-ad9d-49f7-9967-b53b8286a259!b130936|client!b3944",
    "oauth_client_secret": "caaea1b9-b09b-4d28-83fe-09966d525243$LOFW4h5LpLvB3Z2FE0P7FiH4-C7qexeQPi22DBiHbz8=",
    "token_url": "https://ailien-test.authentication.eu20.hana.ondemand.com/oauth/token",
    "description": "Staging environment for pre-production testing (Ailien)"
}

class WolfDatasphereServer:
    """Wolf Datasphere Server with Basic Authentication"""
    
    def __init__(self):
        self.config = WOLF_CONFIG
        self.session = requests.Session()
        self.setup_authentication()
    
    def setup_authentication(self):
        """Setup OAuth authentication for Wolf environment"""
        
        client_id = self.config["oauth_client_id"]
        client_secret = self.config["oauth_client_secret"]
        token_url = self.config["token_url"]
        
        try:
            # Get OAuth token
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
                
                self.session.headers.update({
                    'Authorization': f'Bearer {access_token}',
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'User-Agent': 'Wolf-Datasphere-Server/2.0'
                })
                
                print(f"✅ OAuth authentication configured successfully")
                print(f"🎫 Token preview: {access_token[:20]}...")
            else:
                raise Exception(f"OAuth failed: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ OAuth authentication failed: {e}")
            raise
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to Wolf environment"""
        
        print(f"🔍 Testing connection to {self.config['display_name']}")
        print(f"📍 URL: {self.config['base_url']}")
        
        try:
            # Test health endpoint
            health_url = f"{self.config['base_url']}/health"
            response = self.session.get(health_url, timeout=30)
            
            if response.status_code == 200:
                print("✅ Health check passed")
                return {"success": True, "status": "healthy"}
            else:
                print(f"⚠️ Health check returned HTTP {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return {"success": False, "error": str(e)}
    
    def discover_catalog(self) -> Dict[str, Any]:
        """Discover catalog assets in Wolf environment"""
        
        print(f"\n🔍 Discovering catalog assets...")
        
        # Try the working catalog endpoint
        catalog_url = f"{self.config['base_url']}/api/v1/dwc/catalog"
        
        try:
            response = self.session.get(catalog_url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, dict) and 'value' in data:
                    assets = data['value']
                    
                    # Filter assets for our space
                    space_assets = [
                        asset for asset in assets 
                        if asset.get('spaceName') == self.config['space_name']
                    ]
                    
                    print(f"✅ Found {len(assets)} total assets")
                    print(f"📊 Found {len(space_assets)} assets in space {self.config['space_name']}")
                    
                    # Show sample assets
                    for asset in space_assets[:5]:
                        name = asset.get('name', 'Unknown')
                        asset_type = asset.get('type', 'Unknown')
                        print(f"  • {name} ({asset_type})")
                    
                    return {
                        "success": True,
                        "total_assets": len(assets),
                        "space_assets": len(space_assets),
                        "assets": space_assets
                    }
                else:
                    print("❌ Unexpected catalog response format")
                    return {"success": False, "error": "Invalid response format"}
            
            else:
                print(f"❌ Catalog discovery failed: HTTP {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Catalog discovery error: {e}")
            return {"success": False, "error": str(e)}
    
    def test_consumption_api(self) -> Dict[str, Any]:
        """Test consumption API endpoints"""
        
        print(f"\n🔍 Testing consumption API...")
        
        # Test the working consumption endpoint pattern from ailien environment
        consumption_url = f"{self.config['base_url']}/api/v1/datasphere/consumption/analytical/SAP_CONTENT/New_Analytic_Model_2/New_Analytic_Model_2"
        
        try:
            # Test with limit parameter
            params = {'$top': 5}
            response = self.session.get(consumption_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Handle OData response
                if isinstance(data, dict) and 'value' in data:
                    records = data['value']
                    print(f"✅ Consumption API working: {len(records)} records returned")
                    
                    if records:
                        print("📊 Sample record fields:")
                        sample_record = records[0]
                        for key, value in list(sample_record.items())[:5]:
                            print(f"  • {key}: {value}")
                    
                    return {
                        "success": True,
                        "endpoint": consumption_url,
                        "record_count": len(records),
                        "sample_record": records[0] if records else None
                    }
                else:
                    print("⚠️ Unexpected consumption API response format")
                    return {"success": False, "error": "Invalid response format"}
            
            else:
                print(f"❌ Consumption API failed: HTTP {response.status_code}")
                print(f"📄 Response: {response.text[:200]}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Consumption API error: {e}")
            return {"success": False, "error": str(e)}
    
    def get_metadata(self, asset_name: str = "New_Analytic_Model_2") -> Dict[str, Any]:
        """Get metadata for a specific asset"""
        
        print(f"\n🔍 Getting metadata for {asset_name}...")
        
        metadata_url = f"{self.config['base_url']}/api/v1/datasphere/consumption/analytical/SAP_CONTENT/{asset_name}/$metadata"
        
        try:
            response = self.session.get(metadata_url, timeout=30)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                
                if 'xml' in content_type:
                    print("✅ XML metadata retrieved")
                    print(f"📄 Content size: {len(response.content)} bytes")
                    print(f"📝 Content preview: {response.text[:200]}...")
                    
                    return {
                        "success": True,
                        "format": "xml",
                        "size": len(response.content),
                        "content": response.text
                    }
                else:
                    print(f"✅ Metadata retrieved (format: {content_type})")
                    return {
                        "success": True,
                        "format": content_type,
                        "content": response.text
                    }
            
            else:
                print(f"❌ Metadata retrieval failed: HTTP {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Metadata error: {e}")
            return {"success": False, "error": str(e)}
    
    def start_server_session(self):
        """Start an interactive server session"""
        
        print(f"\n🐺 Wolf Server Session Started")
        print("=" * 35)
        
        while True:
            print(f"\n🎯 Wolf Server Commands:")
            print("1. 🔍 Test connection")
            print("2. 📊 Discover catalog")
            print("3. 🔄 Test consumption API")
            print("4. 📋 Get metadata")
            print("5. 📄 Show configuration")
            print("6. 🚪 Exit")
            
            choice = input("\nChoose command [1]: ").strip()
            if not choice:
                choice = "1"
            
            try:
                if choice == "1":
                    self.test_connection()
                elif choice == "2":
                    self.discover_catalog()
                elif choice == "3":
                    self.test_consumption_api()
                elif choice == "4":
                    asset_name = input("Asset name [SAP.TIME.VIEW_DIMENSION_DAY]: ").strip()
                    if not asset_name:
                        asset_name = "SAP.TIME.VIEW_DIMENSION_DAY"
                    self.get_metadata(asset_name)
                elif choice == "5":
                    self.show_configuration()
                elif choice == "6":
                    print("👋 Wolf server session ended")
                    break
                else:
                    print("❌ Invalid choice")
            
            except KeyboardInterrupt:
                print("\n\n👋 Wolf server session interrupted")
                break
            except Exception as e:
                print(f"❌ Command error: {e}")
    
    def show_configuration(self):
        """Show current Wolf configuration"""
        
        print(f"\n🐺 Wolf Environment Configuration")
        print("=" * 35)
        print(f"Name: {self.config['display_name']}")
        print(f"URL: {self.config['base_url']}")
        print(f"Space: {self.config['space_name']}")
        print(f"Username: {self.config['username']}")
        print(f"Auth Type: Basic Authentication")
        print(f"Description: {self.config['description']}")

def run_wolf_tests():
    """Run comprehensive Wolf environment tests"""
    
    print("🧪 Running Wolf Environment Tests")
    print("=" * 35)
    
    server = WolfDatasphereServer()
    
    # Test connection
    connection_result = server.test_connection()
    
    # Discover catalog
    catalog_result = server.discover_catalog()
    
    # Test consumption API
    consumption_result = server.test_consumption_api()
    
    # Get metadata
    metadata_result = server.get_metadata()
    
    # Summary
    print(f"\n📊 Wolf Environment Test Summary")
    print("=" * 35)
    print(f"Connection: {'✅' if connection_result['success'] else '❌'}")
    print(f"Catalog Discovery: {'✅' if catalog_result['success'] else '❌'}")
    print(f"Consumption API: {'✅' if consumption_result['success'] else '❌'}")
    print(f"Metadata Retrieval: {'✅' if metadata_result['success'] else '❌'}")
    
    # Save results
    results = {
        "timestamp": datetime.now().isoformat(),
        "environment": "wolf",
        "connection": connection_result,
        "catalog": catalog_result,
        "consumption": consumption_result,
        "metadata": metadata_result
    }
    
    with open(f'wolf_test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Test results saved to file")
    
    return results

def main():
    """Main function"""
    
    print("🐺 Wolf Datasphere Server")
    print("=" * 27)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    print("🎯 What would you like to do?")
    print("1. 🧪 Run comprehensive tests")
    print("2. 🖥️ Start interactive server session")
    print("3. 📄 Show configuration only")
    
    choice = input("\nChoose option [1]: ").strip()
    if not choice:
        choice = "1"
    
    if choice == "1":
        run_wolf_tests()
    elif choice == "2":
        server = WolfDatasphereServer()
        server.start_server_session()
    elif choice == "3":
        server = WolfDatasphereServer()
        server.show_configuration()
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()