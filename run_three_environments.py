#!/usr/bin/env python3
"""
Simple Runner for Dog, Wolf, and Bear Datasphere Environments
Easy-to-use script for metadata extraction across all three environments
"""

import os
import sys
from datetime import datetime
from multi_environment_metadata_extractor import MultiEnvironmentExtractor

def load_env_file():
    """Load environment variables from .env file if available"""
    env_files = ['.env.three_environments', '.env', '.env.datasphere']
    
    for env_file in env_files:
        if os.path.exists(env_file):
            try:
                from dotenv import load_dotenv
                load_dotenv(env_file)
                print(f"📋 Loaded environment from: {env_file}")
                return True
            except ImportError:
                print("⚠️ python-dotenv not installed, loading environment manually...")
                # Manual loading
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key] = value
                print(f"📋 Manually loaded environment from: {env_file}")
                return True
    
    return False

def show_environment_status():
    """Show the status of all three environments"""
    
    print("🐕🐺🐻 Environment Status")
    print("=" * 25)
    
    extractor = MultiEnvironmentExtractor()
    environments = extractor.list_environments()
    
    available_count = 0
    
    for env in environments:
        emoji = {"dog": "🐕", "wolf": "🐺", "bear": "🐻"}[env["name"]]
        status = "✅ Ready" if env["credentials_available"] else "❌ Missing credentials"
        
        print(f"{emoji} {env['display_name']}: {status}")
        print(f"   Secret: {env['client_secret_env']}")
        print(f"   Glue DB: {env['glue_database']}")
        
        if env["credentials_available"]:
            available_count += 1
        print()
    
    print(f"📊 Summary: {available_count}/3 environments ready")
    return available_count

def quick_test():
    """Quick test of all available environments"""
    
    print("\n🧪 Quick Connection Test")
    print("=" * 24)
    
    extractor = MultiEnvironmentExtractor()
    
    # Test each environment
    for env_name in ["dog", "wolf", "bear"]:
        emoji = {"dog": "🐕", "wolf": "🐺", "bear": "🐻"}[env_name]
        
        try:
            result = extractor.test_environment_connection(env_name)
            
            if result["success"]:
                print(f"{emoji} {result['environment']}: ✅ {result['models_discovered']} models")
            else:
                print(f"{emoji} {env_name.title()}: ❌ {result['error'][:50]}...")
        
        except Exception as e:
            print(f"{emoji} {env_name.title()}: ❌ Error: {str(e)[:50]}...")

def extract_from_environment(env_name: str, dry_run: bool = False):
    """Extract from a specific environment"""
    
    emoji = {"dog": "🐕", "wolf": "🐺", "bear": "🐻"}[env_name]
    
    print(f"\n{emoji} Extracting from {env_name.title()} Environment")
    print("=" * 40)
    
    extractor = MultiEnvironmentExtractor()
    
    aws_config = {
        "region": os.getenv("AWS_REGION", "us-east-1")
    }
    
    if dry_run:
        print("🧪 DRY RUN MODE - No AWS changes will be made")
    
    result = extractor.extract_from_environment(env_name, aws_config, dry_run)
    
    print(f"\n📊 Results:")
    print(f"Success: {'✅' if result.success else '❌'}")
    print(f"Tables discovered: {result.tables_discovered}")
    print(f"Tables replicated: {result.tables_replicated}")
    print(f"Execution time: {result.execution_time:.2f}s")
    
    if result.errors:
        print(f"\n❌ Errors ({len(result.errors)}):")
        for error in result.errors[:3]:  # Show first 3 errors
            print(f"  • {error}")
        if len(result.errors) > 3:
            print(f"  ... and {len(result.errors) - 3} more errors")
    
    if result.warnings:
        print(f"\n⚠️ Warnings ({len(result.warnings)}):")
        for warning in result.warnings[:3]:
            print(f"  • {warning}")

def extract_from_all(dry_run: bool = False):
    """Extract from all available environments"""
    
    print(f"\n🌍 Extracting from All Environments")
    print("=" * 35)
    
    if dry_run:
        print("🧪 DRY RUN MODE - No AWS changes will be made")
    
    extractor = MultiEnvironmentExtractor()
    
    aws_config = {
        "region": os.getenv("AWS_REGION", "us-east-1")
    }
    
    results = extractor.extract_from_all_environments(aws_config, dry_run, skip_on_error=True)
    
    # Generate summary
    summary = extractor.generate_summary_report(results)
    
    print(f"\n📊 Multi-Environment Summary:")
    print(f"✅ Successful: {summary['successful_environments']}/{summary['total_environments']}")
    print(f"📈 Success Rate: {summary['success_rate']}")
    print(f"🔍 Total Discovered: {summary['total_tables_discovered']}")
    print(f"✅ Total Replicated: {summary['total_tables_replicated']}")
    
    print(f"\n📋 Environment Details:")
    for env_name, env_data in summary["environments"].items():
        emoji = {"dog": "🐕", "wolf": "🐺", "bear": "🐻"}[env_name]
        status = "✅" if env_data["success"] else "❌"
        print(f"{emoji} {status} {env_data['display_name']}: {env_data['tables_replicated']}/{env_data['tables_discovered']} tables")
    
    # Save results
    results_file = f"three_env_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    import json
    with open(results_file, 'w') as f:
        # Convert results to JSON-serializable format
        json_results = {}
        for env_name, result in results.items():
            json_results[env_name] = {
                "success": result.success,
                "tables_discovered": result.tables_discovered,
                "tables_replicated": result.tables_replicated,
                "errors": result.errors,
                "warnings": result.warnings,
                "execution_time": result.execution_time
            }
        
        json.dump({
            "summary": summary,
            "results": json_results
        }, f, indent=2)
    
    print(f"\n📄 Results saved to: {results_file}")

def main():
    """Main function with simple menu"""
    
    print("🐕🐺🐻 SAP Datasphere Three Environment Runner")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Load environment variables
    if not load_env_file():
        print("⚠️ No environment file found. You may need to set credentials manually.")
        print("💡 Run: python setup_three_environments.py")
        print()
    
    # Show environment status
    available_count = show_environment_status()
    
    if available_count == 0:
        print("❌ No environments are configured!")
        print("\n💡 Setup steps:")
        print("1. Run: python setup_three_environments.py")
        print("2. Set your OAuth client secrets")
        print("3. Configure AWS credentials")
        return
    
    # Simple menu
    print("\n🎯 What would you like to do?")
    print("1. 🧪 Quick test all environments")
    print("2. 🐕 Extract from Dog (Development)")
    print("3. 🐺 Extract from Wolf (Staging)")
    print("4. 🐻 Extract from Bear (Production)")
    print("5. 🌍 Extract from all environments")
    print("6. 🔍 Dry run (test without AWS changes)")
    
    choice = input("\nChoose option [1]: ").strip()
    if not choice:
        choice = "1"
    
    try:
        if choice == "1":
            quick_test()
        
        elif choice == "2":
            extract_from_environment("dog")
        
        elif choice == "3":
            extract_from_environment("wolf")
        
        elif choice == "4":
            # Extra confirmation for production
            confirm = input("⚠️ This is PRODUCTION (Bear). Continue? [y/N]: ").strip().lower()
            if confirm == 'y':
                extract_from_environment("bear")
            else:
                print("❌ Production extraction cancelled")
        
        elif choice == "5":
            # Extra confirmation for all environments
            confirm = input("⚠️ This will extract from ALL environments including PRODUCTION. Continue? [y/N]: ").strip().lower()
            if confirm == 'y':
                extract_from_all()
            else:
                print("❌ Multi-environment extraction cancelled")
        
        elif choice == "6":
            print("\n🧪 Dry Run Options:")
            print("1. Test specific environment")
            print("2. Test all environments")
            
            dry_choice = input("Choose [2]: ").strip()
            if not dry_choice:
                dry_choice = "2"
            
            if dry_choice == "1":
                env_name = input("Environment (dog/wolf/bear): ").strip().lower()
                if env_name in ["dog", "wolf", "bear"]:
                    extract_from_environment(env_name, dry_run=True)
                else:
                    print("❌ Invalid environment")
            else:
                extract_from_all(dry_run=True)
        
        else:
            print("❌ Invalid choice")
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("💡 Try running with dry run mode first")
    
    print("\n🎉 Done!")

if __name__ == "__main__":
    main()