#!/usr/bin/env python3
"""
Run Metadata Extraction with Real Datasphere Environment
Uses your working credentials from the MCP server success
"""

import json
import os
from datetime import datetime
from enhanced_metadata_extractor import run_enhanced_metadata_extraction

def load_credentials_from_mcp_success():
    """Load working credentials from your MCP server success"""
    
    # These are the working credentials from your FINAL_SUCCESS_SUMMARY
    return {
        "datasphere": {
            "base_url": "https://ailien-test.eu20.hcs.cloud.sap",
            "oauth": {
                "client_id": "sb-dmi-api-proxy-sac-saceu20!t3944|dmi-api-proxy-sac-saceu20!b3944",
                "client_secret": os.getenv("DATASPHERE_CLIENT_SECRET", ""),
                "token_url": "https://ailien-test.eu20.hcs.cloud.sap/oauth/token"
            }
        },
        "aws": {
            "region": os.getenv("AWS_REGION", "us-east-1")
        }
    }

def check_prerequisites():
    """Check if all prerequisites are met"""
    
    print("🔍 Checking Prerequisites")
    print("=" * 25)
    
    issues = []
    
    # Check for client secret
    if not os.getenv("DATASPHERE_CLIENT_SECRET"):
        issues.append("DATASPHERE_CLIENT_SECRET environment variable not set")
    
    # Check AWS credentials
    if not (os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("AWS_PROFILE")):
        issues.append("AWS credentials not configured (set AWS_ACCESS_KEY_ID or AWS_PROFILE)")
    
    # Check required packages
    try:
        import boto3
        print("✅ boto3 available")
    except ImportError:
        issues.append("boto3 not installed (pip install boto3)")
    
    try:
        import requests
        print("✅ requests available")
    except ImportError:
        issues.append("requests not installed (pip install requests)")
    
    if issues:
        print("\n❌ Prerequisites not met:")
        for issue in issues:
            print(f"  • {issue}")
        return False
    
    print("✅ All prerequisites met")
    return True

def create_sample_env_file():
    """Create a sample .env file with instructions"""
    
    env_content = """# SAP Datasphere Metadata Extractor Configuration
# Copy this to .env and fill in your actual values

# SAP Datasphere OAuth Client Secret (REQUIRED)
# Get this from your SAP BTP cockpit or from your working MCP server
DATASPHERE_CLIENT_SECRET=your_actual_client_secret_here

# AWS Configuration
AWS_REGION=us-east-1

# Option 1: AWS Access Keys (not recommended for production)
# AWS_ACCESS_KEY_ID=your_access_key
# AWS_SECRET_ACCESS_KEY=your_secret_key

# Option 2: AWS Profile (recommended)
# AWS_PROFILE=your_profile_name

# Option 3: Use IAM Role (best for EC2/Lambda - no config needed)
"""
    
    with open('.env.sample', 'w') as f:
        f.write(env_content)
    
    print("📝 Created .env.sample file with configuration template")

def main():
    """Main execution function"""
    
    print("🚀 SAP Datasphere Metadata Extraction")
    print("=" * 40)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n💡 Setup Instructions:")
        print("1. Set DATASPHERE_CLIENT_SECRET environment variable")
        print("2. Configure AWS credentials (AWS_PROFILE or AWS_ACCESS_KEY_ID)")
        print("3. Install required packages: pip install boto3 requests")
        
        create_sample_env_file()
        return
    
    # Load configuration
    print("\n🔧 Loading Configuration")
    print("=" * 22)
    
    config = load_credentials_from_mcp_success()
    
    if not config["datasphere"]["oauth"]["client_secret"]:
        print("❌ DATASPHERE_CLIENT_SECRET not found in environment")
        print("💡 Set it with: export DATASPHERE_CLIENT_SECRET='your_secret'")
        return
    
    print("✅ Configuration loaded")
    print(f"📍 Datasphere URL: {config['datasphere']['base_url']}")
    print(f"🌍 AWS Region: {config['aws']['region']}")
    
    # Run extraction
    print("\n🔄 Starting Metadata Extraction")
    print("=" * 32)
    
    try:
        result = run_enhanced_metadata_extraction(
            datasphere_config=config["datasphere"],
            aws_config=config["aws"],
            glue_database="datasphere_real_catalog"
        )
        
        # Display results
        print("\n" + "=" * 50)
        print("EXTRACTION RESULTS")
        print("=" * 50)
        
        if result.success:
            print("🎉 SUCCESS!")
            print(f"📊 Tables discovered: {result.tables_discovered}")
            print(f"✅ Tables replicated: {result.tables_replicated}")
            print(f"⏱️ Execution time: {result.execution_time:.2f} seconds")
            
            if result.warnings:
                print(f"\n⚠️ Warnings ({len(result.warnings)}):")
                for warning in result.warnings:
                    print(f"  • {warning}")
        else:
            print("❌ EXTRACTION FAILED")
            print(f"📊 Tables discovered: {result.tables_discovered}")
            print(f"❌ Tables replicated: {result.tables_replicated}")
            
            if result.errors:
                print(f"\n❌ Errors ({len(result.errors)}):")
                for error in result.errors:
                    print(f"  • {error}")
        
        # Save detailed results
        results_file = f"extraction_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump({
                'success': result.success,
                'tables_discovered': result.tables_discovered,
                'tables_replicated': result.tables_replicated,
                'errors': result.errors,
                'warnings': result.warnings,
                'execution_time': result.execution_time,
                'timestamp': datetime.now().isoformat(),
                'config_used': {
                    'datasphere_url': config['datasphere']['base_url'],
                    'aws_region': config['aws']['region'],
                    'glue_database': 'datasphere_real_catalog'
                }
            }, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: {results_file}")
        
        # Next steps
        if result.success:
            print("\n🎯 Next Steps:")
            print("1. Check AWS Glue Console to see your replicated tables")
            print("2. Query the data using Amazon Athena")
            print("3. Set up scheduled extraction for regular updates")
            print("4. Explore the data with your favorite BI tools")
        else:
            print("\n🔧 Troubleshooting:")
            print("1. Check your Datasphere credentials and permissions")
            print("2. Verify AWS credentials and Glue permissions")
            print("3. Check network connectivity to both services")
            print("4. Review the error messages above for specific issues")
    
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        print("🔧 Please check your configuration and try again")

if __name__ == "__main__":
    # Load environment variables from .env file if it exists
    if os.path.exists('.env'):
        from dotenv import load_dotenv
        load_dotenv()
        print("📋 Loaded environment variables from .env file")
    
    main()