#!/usr/bin/env python3
"""
Setup Wolf Environment for Multi-Environment Metadata Extractor
Configures Wolf environment with basic auth credentials
"""

import os
import sys
from datetime import datetime

def setup_wolf_credentials():
    """Setup Wolf environment credentials"""
    
    print("🐺 Setting up Wolf Environment")
    print("=" * 30)
    
    # Wolf now uses OAuth with the same credentials as the working ailien environment
    wolf_client_secret = "<your-client-secret>"
    
    # Set environment variable
    os.environ["WOLF_CLIENT_SECRET"] = wolf_client_secret
    
    print("✅ WOLF_CLIENT_SECRET configured")
    print(f"🔑 Using OAuth credentials from ailien environment")
    
    return True

def test_wolf_with_multi_env_extractor():
    """Test Wolf environment with the multi-environment extractor"""
    
    print("\n🧪 Testing Wolf with Multi-Environment Extractor")
    print("=" * 50)
    
    try:
        from multi_environment_metadata_extractor import MultiEnvironmentExtractor
        
        extractor = MultiEnvironmentExtractor()
        
        # Test Wolf environment
        print("🔍 Testing Wolf environment connection...")
        result = extractor.test_environment_connection("wolf")
        
        if result["success"]:
            print(f"✅ Wolf connection successful!")
            print(f"📊 Models discovered: {result['models_discovered']}")
            if result.get("models"):
                print(f"📋 Sample models: {', '.join(result['models'][:3])}")
            return True
        else:
            print(f"❌ Wolf connection failed: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Multi-environment extractor error: {e}")
        return False

def run_wolf_server():
    """Run the Wolf server"""
    
    print("\n🐺 Starting Wolf Server")
    print("=" * 22)
    
    try:
        # Import and run the Wolf server
        import subprocess
        
        result = subprocess.run([
            sys.executable, 
            "start_wolf_server.py"
        ], timeout=300)  # 5 minute timeout
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ Wolf server session timed out")
        return False
    except Exception as e:
        print(f"❌ Error running Wolf server: {e}")
        return False

def create_wolf_env_file():
    """Create environment file with Wolf credentials"""
    
    print("\n💾 Creating Wolf Environment File")
    print("=" * 33)
    
    env_content = f"""# Wolf Environment Configuration - Updated to Ailien
# Generated on {datetime.now().isoformat()}

# Wolf Environment (Staging) - OAuth Configuration
WOLF_CLIENT_SECRET=<your-client-secret>

# Wolf Environment Details:
# URL: https://ailien-test.eu20.hcs.cloud.sap
# Client ID: sb-<subaccount-uuid>!b<n>|client!b<n>
# Token URL: https://ailien-test.authentication.eu20.hana.ondemand.com/oauth/token
# Auth Type: OAuth 2.0

# AWS Configuration
AWS_REGION=us-east-1

# Note: Wolf environment now uses OAuth authentication
# Same credentials as the working ailien environment
"""
    
    with open('.env.wolf', 'w') as f:
        f.write(env_content)
    
    print("✅ Wolf environment file created: .env.wolf")
    print("💡 To use: source .env.wolf")

def main():
    """Main setup function"""
    
    print("🐺 Wolf Environment Setup")
    print("=" * 25)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Setup credentials
    if not setup_wolf_credentials():
        print("❌ Failed to setup Wolf credentials")
        return
    
    # Create environment file
    create_wolf_env_file()
    
    # Menu
    print("\n🎯 What would you like to do?")
    print("1. 🧪 Test Wolf with multi-environment extractor")
    print("2. 🐺 Start Wolf server session")
    print("3. 🔄 Test Wolf server directly")
    print("4. 📄 Just create environment file (done)")
    
    choice = input("\nChoose option [1]: ").strip()
    if not choice:
        choice = "1"
    
    if choice == "1":
        test_wolf_with_multi_env_extractor()
    elif choice == "2":
        run_wolf_server()
    elif choice == "3":
        # Run Wolf server tests
        try:
            from start_wolf_server import run_wolf_tests
            run_wolf_tests()
        except Exception as e:
            print(f"❌ Error running Wolf tests: {e}")
    elif choice == "4":
        print("✅ Environment file created")
    
    print("\n🎉 Wolf setup completed!")
    print("\n💡 Next steps:")
    print("1. Source environment: source .env.wolf")
    print("2. Run Wolf server: python start_wolf_server.py")
    print("3. Or use multi-env: python run_three_environments.py")

if __name__ == "__main__":
    main()