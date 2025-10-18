#!/usr/bin/env python3
"""
Setup Script with Correct Datasphere Credentials
Sets up the Dog environment with the correct OAuth credentials you provided
"""

import os
import subprocess
import sys

def setup_dog_environment():
    """Setup the Dog environment with correct credentials"""
    
    print("🐕 Setting up Dog Environment with Correct Credentials")
    print("=" * 55)
    
    # Your correct OAuth credentials
    client_secret = "caaea1b9-b09b-4d28-83fe-09966d525243$LOFW4h5LpLvB3Z2FE0P7FiH4-C7qexeQPi22DBiHbz8="
    
    # Set environment variable
    os.environ["DOG_CLIENT_SECRET"] = client_secret
    
    print("✅ DOG_CLIENT_SECRET configured")
    print(f"🔑 Secret length: {len(client_secret)} characters")
    
    # Also set AWS region if not set
    if not os.getenv("AWS_REGION"):
        os.environ["AWS_REGION"] = "us-east-1"
        print("✅ AWS_REGION set to us-east-1")
    
    return True

def test_connection():
    """Test the connection with correct credentials"""
    
    print("\n🧪 Testing Connection with Correct Credentials")
    print("=" * 45)
    
    try:
        # Run the test script
        result = subprocess.run([
            sys.executable, 
            "test_correct_datasphere_credentials.py"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Connection test completed successfully!")
            print("\n📄 Test Output:")
            print(result.stdout)
        else:
            print("❌ Connection test failed")
            print("\n📄 Error Output:")
            print(result.stderr)
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ Connection test timed out")
        return False
    except Exception as e:
        print(f"❌ Error running connection test: {e}")
        return False

def run_metadata_extraction():
    """Run metadata extraction for Dog environment"""
    
    print("\n🚀 Running Metadata Extraction for Dog Environment")
    print("=" * 50)
    
    try:
        # Import and run the multi-environment extractor
        from multi_environment_metadata_extractor import MultiEnvironmentExtractor
        
        extractor = MultiEnvironmentExtractor()
        
        # Test connection first
        print("🔍 Testing Dog environment connection...")
        connection_result = extractor.test_environment_connection("dog")
        
        if connection_result["success"]:
            print(f"✅ Connection successful: {connection_result['models_discovered']} models found")
            
            # Ask if user wants to run extraction
            run_extraction = input("\n🚀 Run metadata extraction? [Y/n]: ").strip().lower()
            
            if run_extraction != 'n':
                aws_config = {"region": os.getenv("AWS_REGION", "us-east-1")}
                
                # Ask about dry run
                dry_run = input("🧪 Dry run (no AWS changes)? [Y/n]: ").strip().lower() != 'n'
                
                print(f"\n{'🧪 DRY RUN' if dry_run else '🚀 LIVE EXTRACTION'} - Starting...")
                
                result = extractor.extract_from_environment("dog", aws_config, dry_run)
                
                print(f"\n📊 Extraction Results:")
                print(f"Success: {'✅' if result.success else '❌'}")
                print(f"Tables discovered: {result.tables_discovered}")
                print(f"Tables replicated: {result.tables_replicated}")
                print(f"Execution time: {result.execution_time:.2f}s")
                
                if result.errors:
                    print(f"\n❌ Errors:")
                    for error in result.errors:
                        print(f"  • {error}")
                
                return result.success
            else:
                print("⏭️ Extraction skipped")
                return True
        else:
            print(f"❌ Connection failed: {connection_result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Extraction error: {e}")
        return False

def create_env_file():
    """Create environment file with correct credentials"""
    
    print("\n💾 Creating Environment File")
    print("=" * 28)
    
    env_content = f"""# Correct Datasphere Credentials
# Generated with verified OAuth credentials

# Dog Environment (Development) - WORKING CREDENTIALS
DOG_CLIENT_SECRET=caaea1b9-b09b-4d28-83fe-09966d525243$LOFW4h5LpLvB3Z2FE0P7FiH4-C7qexeQPi22DBiHbz8=

# Wolf Environment (Staging) - UPDATE WITH YOUR CREDENTIALS
WOLF_CLIENT_SECRET=your_wolf_staging_secret

# Bear Environment (Production) - UPDATE WITH YOUR CREDENTIALS  
BEAR_CLIENT_SECRET=your_bear_production_secret

# AWS Configuration
AWS_REGION=us-east-1
# AWS_PROFILE=your_profile_name

# Verified Configuration Details:
# Dog Tenant: https://f45fa9cc-f4b5-4126-ab73-b19b578fb17a.eu10.hcs.cloud.sap
# Dog Client ID: sb-60cb266e-ad9d-49f7-9967-b53b8286a259!b130936|client!b3944
# Dog Token URL: https://ailien-test.authentication.eu20.hana.ondemand.com/oauth/token
"""
    
    with open('.env.correct_credentials', 'w') as f:
        f.write(env_content)
    
    print("✅ Environment file created: .env.correct_credentials")
    print("💡 To use: source .env.correct_credentials")

def main():
    """Main setup function"""
    
    print("🚀 Setup with Correct Datasphere Credentials")
    print("=" * 47)
    
    # Setup Dog environment
    if not setup_dog_environment():
        print("❌ Failed to setup Dog environment")
        return
    
    # Create environment file
    create_env_file()
    
    # Menu
    print("\n🎯 What would you like to do?")
    print("1. 🧪 Test connection only")
    print("2. 🚀 Test connection and run extraction")
    print("3. 📄 Just create environment file (done)")
    
    choice = input("\nChoose option [2]: ").strip()
    if not choice:
        choice = "2"
    
    if choice == "1":
        test_connection()
    elif choice == "2":
        if test_connection():
            run_metadata_extraction()
        else:
            print("❌ Connection test failed, skipping extraction")
    elif choice == "3":
        print("✅ Environment file created")
    
    print("\n🎉 Setup completed!")
    print("\n💡 Next steps:")
    print("1. Source environment: source .env.correct_credentials")
    print("2. Run extraction: python run_three_environments.py")
    print("3. Check AWS Glue Console for results")

if __name__ == "__main__":
    main()