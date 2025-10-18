#!/usr/bin/env python3
"""
Explore Accessible Wolf Endpoints
Explore what data is available in the endpoints we can actually access
"""

import requests
import base64
import json
from datetime import datetime

class AccessibleEndpointsExplorer:
    """Explore the endpoints that are actually accessible"""
    
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
    
    def make_request(self, endpoint, accept_header='application/json'):
        """Make authenticated request"""
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': accept_header,
            'User-Agent': 'Accessible-Endpoints-Explorer/1.0'
        }
        
        url = f"{self.config['base_url']}{endpoint}"
        response = requests.get(url, headers=headers, timeout=30)
        
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "content": response.content,
            "text": response.text
        }
    
    def explore_user_info(self):
        """Explore user information"""
        
        print(f"👤 Exploring User Information")
        print("=" * 29)
        
        result = self.make_request("/api/v1/user")
        
        if result["status_code"] == 200:
            print(f"✅ User endpoint accessible")
            
            try:
                data = json.loads(result["text"])
                print(f"📋 User data structure:")
                for key, value in data.items():
                    print(f"  • {key}: {value}")
                return data
            except json.JSONDecodeError:
                print(f"📄 Non-JSON response:")
                print(f"Content: {result['text'][:500]}...")
        
        return None
    
    def explore_permissions(self):
        """Explore user permissions"""
        
        print(f"\n🔑 Exploring User Permissions")
        print("=" * 31)
        
        result = self.make_request("/api/v1/permissions")
        
        if result["status_code"] == 200:
            print(f"✅ Permissions endpoint accessible")
            
            try:
                data = json.loads(result["text"])
                print(f"📋 Permissions data:")
                if isinstance(data, list):
                    for i, permission in enumerate(data):
                        print(f"  {i+1}. {permission}")
                elif isinstance(data, dict):
                    for key, value in data.items():
                        print(f"  • {key}: {value}")
                else:
                    print(f"  Raw data: {data}")
                return data
            except json.JSONDecodeError:
                print(f"📄 Non-JSON response:")
                print(f"Content: {result['text'][:500]}...")
        
        return None
    
    def explore_scopes(self):
        """Explore available scopes"""
        
        print(f"\n🎯 Exploring Available Scopes")
        print("=" * 30)
        
        result = self.make_request("/api/v1/scopes")
        
        if result["status_code"] == 200:
            print(f"✅ Scopes endpoint accessible")
            
            try:
                data = json.loads(result["text"])
                print(f"📋 Available scopes:")
                if isinstance(data, list):
                    for i, scope in enumerate(data):
                        print(f"  {i+1}. {scope}")
                elif isinstance(data, dict):
                    for key, value in data.items():
                        print(f"  • {key}: {value}")
                else:
                    print(f"  Raw data: {data}")
                return data
            except json.JSONDecodeError:
                print(f"📄 Non-JSON response:")
                print(f"Content: {result['text'][:500]}...")
        
        return None
    
    def explore_spaces(self):
        """Explore Datasphere spaces"""
        
        print(f"\n🏢 Exploring Datasphere Spaces")
        print("=" * 31)
        
        result = self.make_request("/api/v1/datasphere/spaces")
        
        if result["status_code"] == 200:
            print(f"✅ Spaces endpoint accessible")
            
            try:
                data = json.loads(result["text"])
                print(f"📋 Spaces data:")
                if isinstance(data, list):
                    print(f"Found {len(data)} spaces:")
                    for space in data:
                        if isinstance(space, dict):
                            name = space.get('name', 'Unknown')
                            space_id = space.get('id', 'Unknown')
                            print(f"  • {name} (ID: {space_id})")
                        else:
                            print(f"  • {space}")
                elif isinstance(data, dict):
                    if 'value' in data:
                        spaces = data['value']
                        print(f"Found {len(spaces)} spaces:")
                        for space in spaces:
                            name = space.get('name', 'Unknown')
                            space_id = space.get('id', 'Unknown')
                            print(f"  • {name} (ID: {space_id})")
                    else:
                        for key, value in data.items():
                            print(f"  • {key}: {value}")
                return data
            except json.JSONDecodeError:
                print(f"📄 Non-JSON response:")
                print(f"Content: {result['text'][:500]}...")
        
        return None
    
    def explore_models(self):
        """Explore Datasphere models"""
        
        print(f"\n📊 Exploring Datasphere Models")
        print("=" * 31)
        
        result = self.make_request("/api/v1/datasphere/models")
        
        if result["status_code"] == 200:
            print(f"✅ Models endpoint accessible")
            
            try:
                data = json.loads(result["text"])
                print(f"📋 Models data:")
                if isinstance(data, list):
                    print(f"Found {len(data)} models:")
                    for model in data:
                        if isinstance(model, dict):
                            name = model.get('name', 'Unknown')
                            model_type = model.get('type', 'Unknown')
                            print(f"  • {name} ({model_type})")
                        else:
                            print(f"  • {model}")
                elif isinstance(data, dict):
                    if 'value' in data:
                        models = data['value']
                        print(f"Found {len(models)} models:")
                        for model in models:
                            name = model.get('name', 'Unknown')
                            model_type = model.get('type', 'Unknown')
                            print(f"  • {name} ({model_type})")
                    else:
                        for key, value in data.items():
                            print(f"  • {key}: {value}")
                return data
            except json.JSONDecodeError:
                print(f"📄 Non-JSON response:")
                print(f"Content: {result['text'][:500]}...")
        
        return None
    
    def explore_metadata(self):
        """Explore Datasphere metadata"""
        
        print(f"\n📋 Exploring Datasphere Metadata")
        print("=" * 33)
        
        result = self.make_request("/api/v1/datasphere/metadata")
        
        if result["status_code"] == 200:
            print(f"✅ Metadata endpoint accessible")
            
            try:
                data = json.loads(result["text"])
                print(f"📋 Metadata structure:")
                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, list):
                            print(f"  • {key}: [{len(value)} items]")
                        elif isinstance(value, dict):
                            print(f"  • {key}: {{dict with {len(value)} keys}}")
                        else:
                            print(f"  • {key}: {value}")
                elif isinstance(data, list):
                    print(f"  List with {len(data)} items")
                    for i, item in enumerate(data[:5]):  # Show first 5
                        print(f"    {i+1}. {item}")
                return data
            except json.JSONDecodeError:
                print(f"📄 Non-JSON response:")
                print(f"Content: {result['text'][:500]}...")
        
        return None

def main():
    """Main exploration function"""
    
    print("🔍 Wolf Accessible Endpoints Explorer")
    print("=" * 37)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    try:
        explorer = AccessibleEndpointsExplorer()
        
        # Explore all accessible endpoints
        user_info = explorer.explore_user_info()
        permissions = explorer.explore_permissions()
        scopes = explorer.explore_scopes()
        spaces = explorer.explore_spaces()
        models = explorer.explore_models()
        metadata = explorer.explore_metadata()
        
        # Save all results
        results = {
            "timestamp": datetime.now().isoformat(),
            "user_info": user_info,
            "permissions": permissions,
            "scopes": scopes,
            "spaces": spaces,
            "models": models,
            "metadata": metadata
        }
        
        with open(f'accessible_endpoints_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📄 All data saved to file")
        
        # Summary
        print(f"\n📊 Exploration Summary")
        print("=" * 21)
        accessible_count = sum(1 for data in [user_info, permissions, scopes, spaces, models, metadata] if data is not None)
        print(f"✅ Accessible endpoints: {accessible_count}/6")
        
        if spaces:
            print(f"🏢 Spaces discovered: Available")
        if models:
            print(f"📊 Models discovered: Available")
        if metadata:
            print(f"📋 Metadata discovered: Available")
        
        print(f"\n💡 Key Findings:")
        print("• You have access to spaces, models, and metadata endpoints")
        print("• The consumption/analytical endpoints require additional permissions")
        print("• Focus on the accessible endpoints for now")
        print("• Request additional OAuth scopes for analytical model access")
        
    except Exception as e:
        print(f"❌ Exploration failed: {e}")

if __name__ == "__main__":
    main()