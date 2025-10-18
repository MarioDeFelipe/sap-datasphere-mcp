#!/usr/bin/env python3
"""
Setup Configuration for Real Datasphere Environment
Helps configure the enhanced metadata extractor with your real credentials
"""

import json
import os
from typing import Dict, Any
import getpass

def setup_datasphere_config() -> Dict[str, Any]:
    """Interactive setup for Datasphere configuration"""
    
    print("🔧 SAP Datasphere Configuration Setup")
    print("=" * 50)
    
    # Base URL (from your working environment)
    base_url = input("Enter Datasphere Base URL [https://ailien-test.eu20.hcs.cloud.sap]: ").strip()
    if not base_url:
        base_url = "https://ailien-test.eu20.hcs.cloud.sap"
    
    print(f"✅ Base URL: {base_url}")
    
    # OAuth Configuration
    print("\n🔐 OAuth2 Configuration")
    print("From your working MCP server, you have:")
    print("Client ID: sb-dmi-api-proxy-sac-saceu20!t3944|dmi-api-proxy-sac-saceu20!b3944")
    
    client_id = input("Enter OAuth Client ID [use above]: ").strip()
    if not client_id:
        client_id = "sb-dmi-api-proxy-sac-saceu20!t3944|dmi-api-proxy-sac-saceu20!b3944"
    
    client_secret = getpass.getpass("Enter OAuth Client Secret: ").strip()
    
    if not client_secret:
        print("❌ Client secret is required!")
        return None
    
    token_url = f"{base_url}/oauth/token"
    
    config = {
        "base_url": base_url,
        "oauth": {
            "client_id": client_id,
            "client_secret": client_secret,
            "token_url": token_url
        }
    }
    
    print("✅ Datasphere configuration ready")
    return config

def setup_aws_config() -> Dict[str, Any]:
    """Setup AWS configuration"""
    
    print("\n☁️ AWS Configuration Setup")
    print("=" * 30)
    
    region = input("Enter AWS Region [us-east-1]: ").strip()
    if not region:
        region = "us-east-1"
    
    print("AWS Credentials:")
    print("1. Use IAM Role (recommended for EC2/Lambda)")
    print("2. Use Environment Variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)")
    print("3. Enter credentials manually")
    
    choice = input("Choose option [1]: ").strip()
    if not choice:
        choice = "1"
    
    config = {"region": region}
    
    if choice == "3":
        access_key = input("Enter AWS Access Key ID: ").strip()
        secret_key = getpass.getpass("Enter AWS Secret Access Key: ").strip()
        
        if access_key and secret_key:
            config["access_key_id"] = access_key
            config["secret_access_key"] = secret_key
    
    print("✅ AWS configuration ready")
    return config

def test_configuration(datasphere_config: Dict[str, Any]) -> bool:
    """Test the Datasphere configuration"""
    
    print("\n🧪 Testing Configuration")
    print("=" * 25)
    
    try:
        import requests
        import base64
        
        # Test OAuth authentication
        oauth_config = datasphere_config["oauth"]
        token_url = oauth_config["token_url"]
        client_id = oauth_config["client_id"]
        client_secret = oauth_config["client_secret"]
        
        auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        
        headers = {
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {'grant_type': 'client_credentials'}
        
        print("🔐 Testing OAuth authentication...")
        response = requests.post(token_url, headers=headers, data=data, timeout=30)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            
            if access_token:
                print("✅ OAuth authentication successful")
                
                # Test API endpoint
                print("🔍 Testing API endpoint...")
                api_url = f"{datasphere_config['base_url']}/api/v1/datasphere/consumption/analytical/SAP_CONTENT/New_Analytic_Model_2"
                
                api_headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Accept': 'application/json'
                }
                
                api_response = requests.get(api_url, headers=api_headers, timeout=30)
                
                if api_response.status_code == 200:
                    print("✅ API endpoint accessible")
                    return True
                else:
                    print(f"⚠️ API endpoint returned HTTP {api_response.status_code}")
                    return False
            else:
                print("❌ No access token received")
                return False
        else:
            print(f"❌ OAuth failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def save_configuration(datasphere_config: Dict[str, Any], aws_config: Dict[str, Any]):
    """Save configuration to files"""
    
    print("\n💾 Saving Configuration")
    print("=" * 22)
    
    # Save to JSON file
    config_data = {
        "datasphere": datasphere_config,
        "aws": aws_config,
        "created_at": "2024-10-17T12:00:00Z",
        "version": "2.0"
    }
    
    with open('datasphere_config.json', 'w') as f:
        json.dump(config_data, f, indent=2)
    
    print("✅ Configuration saved to: datasphere_config.json")
    
    # Create environment file template
    env_content = f"""# SAP Datasphere Configuration
DATASPHERE_BASE_URL={datasphere_config['base_url']}
DATASPHERE_CLIENT_ID={datasphere_config['oauth']['client_id']}
DATASPHERE_CLIENT_SECRET={datasphere_config['oauth']['client_secret']}
DATASPHERE_TOKEN_URL={datasphere_config['oauth']['token_url']}

# AWS Configuration
AWS_REGION={aws_config['region']}
"""
    
    if 'access_key_id' in aws_config:
        env_content += f"AWS_ACCESS_KEY_ID={aws_config['access_key_id']}\n"
        env_content += f"AWS_SECRET_ACCESS_KEY={aws_config['secret_access_key']}\n"
    
    with open('.env.datasphere', 'w') as f:
        f.write(env_content)
    
    print("✅ Environment template saved to: .env.datasphere")

def load_existing_config() -> Dict[str, Any]:
    """Load existing configuration if available"""
    
    if os.path.exists('datasphere_config.json'):
        try:
            with open('datasphere_config.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Could not load existing config: {e}")
    
    return None

def main():
    """Main configuration setup"""
    
    print("🚀 Enhanced Datasphere Metadata Extractor Setup")
    print("=" * 55)
    
    # Check for existing configuration
    existing_config = load_existing_config()
    if existing_config:
        print("📋 Found existing configuration")
        use_existing = input("Use existing configuration? [y/N]: ").strip().lower()
        
        if use_existing == 'y':
            print("✅ Using existing configuration")
            
            # Test existing configuration
            if test_configuration(existing_config['datasphere']):
                print("🎯 Configuration is working!")
                return existing_config
            else:
                print("❌ Existing configuration failed test, creating new one...")
    
    # Setup new configuration
    datasphere_config = setup_datasphere_config()
    if not datasphere_config:
        print("❌ Datasphere configuration failed")
        return None
    
    aws_config = setup_aws_config()
    
    # Test configuration
    if test_configuration(datasphere_config):
        print("🎯 Configuration test passed!")
        
        # Save configuration
        save_configuration(datasphere_config, aws_config)
        
        print("\n🎉 Setup Complete!")
        print("=" * 17)
        print("You can now run the enhanced metadata extractor:")
        print("python enhanced_metadata_extractor.py")
        
        return {
            "datasphere": datasphere_config,
            "aws": aws_config
        }
    else:
        print("❌ Configuration test failed. Please check your credentials.")
        return None

if __name__ == "__main__":
    main()