#!/usr/bin/env python3
"""
Setup Script for Dog, Wolf, and Bear Datasphere Environments
Helps configure credentials and test connections for all three environments
"""

import os
import json
import getpass
from datetime import datetime
from multi_environment_metadata_extractor import MultiEnvironmentExtractor

def display_environment_info():
    """Display information about the three environments"""
    
    print("🐕🐺🐻 Your SAP Datasphere Environments")
    print("=" * 45)
    
    environments = [
        {
            "name": "Dog",
            "emoji": "🐕",
            "purpose": "Development",
            "url": "https://f45fa9cc-f4b5-4126-ab73-b19b578fb17a.eu10.hcs.cloud.sap",
            "client_id": "sb-60cb266e-ad9d-49f7-9967-b53b8286a259!b130936|client!b3944",
            "secret_env": "DOG_CLIENT_SECRET",
            "description": "Development environment for testing and experimentation"
        },
        {
            "name": "Wolf", 
            "emoji": "🐺",
            "purpose": "Staging",
            "url": "https://academydatasphere.eu10.hcs.cloud.sap",
            "client_id": "GE230769#AWSUSER",  # Note: This uses basic auth currently
            "secret_env": "WOLF_CLIENT_SECRET",
            "description": "Staging environment for pre-production testing"
        },
        {
            "name": "Bear",
            "emoji": "🐻", 
            "purpose": "Production",
            "url": "https://ailien-test.eu20.hcs.cloud.sap",
            "client_id": "sb-dmi-api-proxy-sac-saceu20!t3944|dmi-api-proxy-sac-saceu20!b3944",
            "secret_env": "BEAR_CLIENT_SECRET",
            "description": "Production environment - handle with care"
        }
    ]
    
    for env in environments:
        print(f"{env['emoji']} {env['name']} ({env['purpose']})")
        print(f"   URL: {env['url']}")
        print(f"   Client ID: {env['client_id'][:50]}...")
        print(f"   Secret Env: {env['secret_env']}")
        print(f"   Purpose: {env['description']}")
        print()
    
    return environments

def check_current_credentials():
    """Check which environment credentials are currently configured"""
    
    print("🔍 Checking Current Credential Status")
    print("=" * 37)
    
    env_vars = ["DOG_CLIENT_SECRET", "WOLF_CLIENT_SECRET", "BEAR_CLIENT_SECRET"]
    status = {}
    
    for env_var in env_vars:
        value = os.getenv(env_var)
        if value:
            print(f"✅ {env_var}: Configured ({len(value)} characters)")
            status[env_var] = True
        else:
            print(f"❌ {env_var}: Not configured")
            status[env_var] = False
    
    # Check AWS credentials
    print(f"\n☁️ AWS Credentials:")
    if os.getenv("AWS_PROFILE"):
        print(f"✅ AWS_PROFILE: {os.getenv('AWS_PROFILE')}")
    elif os.getenv("AWS_ACCESS_KEY_ID"):
        print(f"✅ AWS_ACCESS_KEY_ID: Configured")
    else:
        print(f"❌ AWS credentials not configured")
    
    print(f"🌍 AWS_REGION: {os.getenv('AWS_REGION', 'us-east-1 (default)')}")
    
    return status

def setup_credentials_interactively():
    """Interactive credential setup"""
    
    print("\n🔧 Interactive Credential Setup")
    print("=" * 32)
    
    environments = [
        ("DOG_CLIENT_SECRET", "Dog (Development)", "🐕"),
        ("WOLF_CLIENT_SECRET", "Wolf (Staging)", "🐺"), 
        ("BEAR_CLIENT_SECRET", "Bear (Production)", "🐻")
    ]
    
    credentials = {}
    
    for env_var, env_name, emoji in environments:
        current_value = os.getenv(env_var)
        
        print(f"\n{emoji} {env_name}")
        print("-" * 20)
        
        if current_value:
            print(f"Current value: {'*' * 20} ({len(current_value)} chars)")
            update = input("Update this credential? [y/N]: ").strip().lower()
            if update != 'y':
                credentials[env_var] = current_value
                continue
        
        secret = getpass.getpass(f"Enter {env_var}: ").strip()
        
        if secret:
            credentials[env_var] = secret
            print("✅ Credential saved")
        else:
            print("⚠️ Skipped (empty value)")
    
    return credentials

def create_env_file(credentials: dict):
    """Create .env file with credentials"""
    
    print("\n💾 Creating Environment File")
    print("=" * 28)
    
    env_content = f"""# SAP Datasphere Multi-Environment Configuration
# Generated on {datetime.now().isoformat()}

# Dog Environment (Development)
# URL: https://f45fa9cc-f4b5-4126-ab73-b19b578fb17a.eu10.hcs.cloud.sap
DOG_CLIENT_SECRET={credentials.get('DOG_CLIENT_SECRET', '')}

# Wolf Environment (Staging) 
# URL: https://academydatasphere.eu10.hcs.cloud.sap
WOLF_CLIENT_SECRET={credentials.get('WOLF_CLIENT_SECRET', '')}

# Bear Environment (Production)
# URL: https://ailien-test.eu20.hcs.cloud.sap
BEAR_CLIENT_SECRET={credentials.get('BEAR_CLIENT_SECRET', '')}

# AWS Configuration
AWS_REGION={os.getenv('AWS_REGION', 'us-east-1')}
# AWS_PROFILE=your_profile_name
# AWS_ACCESS_KEY_ID=your_access_key
# AWS_SECRET_ACCESS_KEY=your_secret_key

# Legacy environment variables (for backward compatibility)
DATASPHERE_CLIENT_SECRET={credentials.get('BEAR_CLIENT_SECRET', '')}
"""
    
    with open('.env.three_environments', 'w') as f:
        f.write(env_content)
    
    print("✅ Environment file created: .env.three_environments")
    print("💡 To use: source .env.three_environments")

def test_all_environments():
    """Test connections to all three environments"""
    
    print("\n🧪 Testing All Environment Connections")
    print("=" * 38)
    
    extractor = MultiEnvironmentExtractor()
    environments = ["dog", "wolf", "bear"]
    
    results = {}
    
    for env_name in environments:
        print(f"\n🔍 Testing {env_name.title()} environment...")
        
        try:
            result = extractor.test_environment_connection(env_name)
            results[env_name] = result
            
            if result["success"]:
                print(f"✅ {result['environment']}: Connected successfully")
                print(f"   Models discovered: {result['models_discovered']}")
                if result.get("models"):
                    print(f"   Sample models: {', '.join(result['models'][:3])}")
            else:
                print(f"❌ {result.get('environment', env_name)}: {result['error']}")
        
        except Exception as e:
            print(f"❌ {env_name.title()}: Critical error - {e}")
            results[env_name] = {"success": False, "error": str(e)}
    
    # Summary
    successful = [env for env, result in results.items() if result.get("success")]
    
    print(f"\n📊 Connection Test Summary:")
    print(f"✅ Successful: {len(successful)}/{len(environments)}")
    print(f"🔗 Working environments: {', '.join(successful) if successful else 'None'}")
    
    return results

def create_quick_start_guide():
    """Create a quick start guide for the three environments"""
    
    guide_content = """# 🐕🐺🐻 Three Environment Quick Start Guide

## Your Datasphere Environments

### 🐕 Dog (Development)
- **URL**: https://f45fa9cc-f4b5-4126-ab73-b19b578fb17a.eu10.hcs.cloud.sap
- **Purpose**: Development and testing
- **Glue Database**: `datasphere_dog_dev`
- **Secret**: `DOG_CLIENT_SECRET`

### 🐺 Wolf (Staging)  
- **URL**: https://academydatasphere.eu10.hcs.cloud.sap
- **Purpose**: Pre-production testing
- **Glue Database**: `datasphere_wolf_staging`
- **Secret**: `WOLF_CLIENT_SECRET`

### 🐻 Bear (Production)
- **URL**: https://ailien-test.eu20.hcs.cloud.sap
- **Purpose**: Production environment
- **Glue Database**: `datasphere_bear_prod`
- **Secret**: `BEAR_CLIENT_SECRET`

## Quick Commands

### Setup Credentials
```bash
python setup_three_environments.py
```

### Test All Environments
```bash
python multi_environment_metadata_extractor.py
# Choose option 1: Test all environment connections
```

### Extract from Specific Environment
```bash
# Set credentials
export DOG_CLIENT_SECRET="your_dog_secret"
export BEAR_CLIENT_SECRET="your_bear_secret"

# Run extraction
python multi_environment_metadata_extractor.py
# Choose option 2: Extract from specific environment
```

### Extract from All Environments
```bash
# Set all credentials
export DOG_CLIENT_SECRET="your_dog_secret"
export WOLF_CLIENT_SECRET="your_wolf_secret"  
export BEAR_CLIENT_SECRET="your_bear_secret"

# Run extraction
python multi_environment_metadata_extractor.py
# Choose option 3: Extract from all available environments
```

## Environment Variables

```bash
# Required for each environment you want to use
export DOG_CLIENT_SECRET="your_development_oauth_secret"
export WOLF_CLIENT_SECRET="your_staging_oauth_secret"
export BEAR_CLIENT_SECRET="your_production_oauth_secret"

# AWS Configuration
export AWS_REGION="us-east-1"
export AWS_PROFILE="your_aws_profile"  # or use access keys
```

## AWS Glue Databases Created

Each environment creates its own Glue database:
- Dog → `datasphere_dog_dev`
- Wolf → `datasphere_wolf_staging`  
- Bear → `datasphere_bear_prod`

This keeps your environments completely separate in AWS.

## Safety Features

- **Production Protection**: Bear environment is clearly marked as production
- **Dry Run Mode**: Test without making AWS changes
- **Error Isolation**: Failed environments don't stop others
- **Separate Databases**: Each environment has its own Glue database

## Troubleshooting

1. **Missing Credentials**: Run `python setup_three_environments.py`
2. **Connection Failed**: Check OAuth client secrets and permissions
3. **AWS Errors**: Verify AWS credentials and Glue permissions
4. **No Models Found**: Check Datasphere permissions and API access

## Best Practices

1. **Start with Dog**: Test everything in development first
2. **Use Dry Run**: Always test with dry run before production
3. **Monitor Bear**: Be extra careful with production environment
4. **Separate Credentials**: Use different OAuth clients for each environment
5. **Regular Testing**: Test connections regularly to catch issues early
"""
    
    with open('THREE_ENVIRONMENTS_GUIDE.md', 'w') as f:
        f.write(guide_content)
    
    print("📚 Quick start guide created: THREE_ENVIRONMENTS_GUIDE.md")

def main():
    """Main setup function"""
    
    print("🚀 SAP Datasphere Three Environment Setup")
    print("=" * 45)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Display environment information
    environments = display_environment_info()
    
    # Check current status
    current_status = check_current_credentials()
    
    # Menu
    print("\n🎯 Setup Options:")
    print("1. Set up credentials interactively")
    print("2. Test current environment connections")
    print("3. Create quick start guide")
    print("4. Show environment information only")
    
    choice = input("\nChoose option [1]: ").strip()
    if not choice:
        choice = "1"
    
    if choice == "1":
        # Interactive credential setup
        credentials = setup_credentials_interactively()
        
        if credentials:
            create_env_file(credentials)
            
            # Test connections with new credentials
            test_choice = input("\nTest connections now? [Y/n]: ").strip().lower()
            if test_choice != 'n':
                # Update environment with new credentials
                for env_var, value in credentials.items():
                    os.environ[env_var] = value
                
                test_all_environments()
    
    elif choice == "2":
        # Test connections
        if not any(current_status.values()):
            print("❌ No credentials configured. Run option 1 first.")
        else:
            test_all_environments()
    
    elif choice == "3":
        # Create guide
        create_quick_start_guide()
    
    elif choice == "4":
        # Just show info (already displayed)
        pass
    
    print("\n🎉 Setup completed!")
    print("\n💡 Next steps:")
    print("1. Source your environment file: source .env.three_environments")
    print("2. Run multi-environment extraction: python multi_environment_metadata_extractor.py")
    print("3. Check the quick start guide: THREE_ENVIRONMENTS_GUIDE.md")

if __name__ == "__main__":
    main()