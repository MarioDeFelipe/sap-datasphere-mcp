#!/usr/bin/env python3
"""
Multi-Environment SAP Datasphere Metadata Extractor
Supports Dog (Dev), Wolf (Staging), and Bear (Production) environments
"""

import json
import logging
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from enhanced_metadata_extractor import (
    EnhancedDatasphereClient, 
    EnhancedGlueCatalogReplicator,
    DatasphereTable,
    ExtractionResult,
    run_enhanced_metadata_extraction
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("multi-env-metadata-extractor")

@dataclass
class EnvironmentConfig:
    """Configuration for a specific Datasphere environment"""
    name: str
    display_name: str
    base_url: str
    oauth_client_id: str
    oauth_client_secret_env: str
    token_url: str
    description: str
    aws_glue_database_suffix: str

class MultiEnvironmentExtractor:
    """Metadata extractor that supports multiple Datasphere environments"""
    
    def __init__(self):
        self.environments = self._load_environment_configs()
        self.results = {}
    
    def _load_environment_configs(self) -> Dict[str, EnvironmentConfig]:
        """Load configurations for all three environments"""
        
        environments = {
            "dog": EnvironmentConfig(
                name="dog",
                display_name="Dog (Development)",
                base_url="https://f45fa9cc-f4b5-4126-ab73-b19b578fb17a.eu10.hcs.cloud.sap",
                oauth_client_id="sb-60cb266e-ad9d-49f7-9967-b53b8286a259!b130936|client!b3944",
                oauth_client_secret_env="DOG_CLIENT_SECRET",
                token_url="https://ailien-test.authentication.eu20.hana.ondemand.com/oauth/token",
                description="Development environment for testing and experimentation",
                aws_glue_database_suffix="dog_dev"
            ),
            
            "wolf": EnvironmentConfig(
                name="wolf",
                display_name="Wolf (Staging)",
                base_url="https://ailien-test.eu20.hcs.cloud.sap",
                oauth_client_id="sb-60cb266e-ad9d-49f7-9967-b53b8286a259!b130936|client!b3944",
                oauth_client_secret_env="WOLF_CLIENT_SECRET",
                token_url="https://ailien-test.authentication.eu20.hana.ondemand.com/oauth/token",
                description="Staging environment for pre-production testing (Ailien)",
                aws_glue_database_suffix="wolf_staging"
            ),
            
            "bear": EnvironmentConfig(
                name="bear",
                display_name="Bear (Production)",
                base_url="https://ailien-test.eu20.hcs.cloud.sap",
                oauth_client_id="sb-dmi-api-proxy-sac-saceu20!t3944|dmi-api-proxy-sac-saceu20!b3944",
                oauth_client_secret_env="BEAR_CLIENT_SECRET",
                token_url="https://ailien-test.eu20.hcs.cloud.sap/oauth/token",
                description="Production environment - handle with care",
                aws_glue_database_suffix="bear_prod"
            )
        }
        
        return environments
    
    def list_environments(self) -> List[Dict[str, Any]]:
        """List all available environments with their status"""
        
        env_list = []
        
        for env_name, env_config in self.environments.items():
            # Check if credentials are available
            client_secret = os.getenv(env_config.oauth_client_secret_env)
            credentials_available = bool(client_secret)
            
            env_info = {
                "name": env_name,
                "display_name": env_config.display_name,
                "base_url": env_config.base_url,
                "description": env_config.description,
                "credentials_available": credentials_available,
                "client_secret_env": env_config.oauth_client_secret_env,
                "glue_database": f"datasphere_{env_config.aws_glue_database_suffix}"
            }
            
            env_list.append(env_info)
        
        return env_list
    
    def test_environment_connection(self, env_name: str) -> Dict[str, Any]:
        """Test connection to a specific environment"""
        
        if env_name not in self.environments:
            return {"success": False, "error": f"Unknown environment: {env_name}"}
        
        env_config = self.environments[env_name]
        client_secret = os.getenv(env_config.oauth_client_secret_env)
        
        if not client_secret:
            return {
                "success": False,
                "error": f"Client secret not found in environment variable: {env_config.oauth_client_secret_env}"
            }
        
        # Create datasphere config
        datasphere_config = {
            "base_url": env_config.base_url,
            "oauth": {
                "client_id": env_config.oauth_client_id,
                "client_secret": client_secret,
                "token_url": env_config.token_url
            }
        }
        
        try:
            # Test connection
            client = EnhancedDatasphereClient(datasphere_config)
            
            # Try to discover models
            models = client.discover_analytical_models()
            
            return {
                "success": True,
                "environment": env_config.display_name,
                "base_url": env_config.base_url,
                "models_discovered": len(models),
                "models": [f"{m['space']}/{m['model']}" for m in models[:5]]  # First 5
            }
            
        except Exception as e:
            return {
                "success": False,
                "environment": env_config.display_name,
                "error": str(e)
            }
    
    def extract_from_environment(
        self, 
        env_name: str, 
        aws_config: Dict[str, Any],
        dry_run: bool = False
    ) -> ExtractionResult:
        """Extract metadata from a specific environment"""
        
        if env_name not in self.environments:
            return ExtractionResult(
                success=False,
                tables_discovered=0,
                tables_replicated=0,
                errors=[f"Unknown environment: {env_name}"],
                warnings=[],
                execution_time=0.0
            )
        
        env_config = self.environments[env_name]
        client_secret = os.getenv(env_config.oauth_client_secret_env)
        
        if not client_secret:
            return ExtractionResult(
                success=False,
                tables_discovered=0,
                tables_replicated=0,
                errors=[f"Client secret not found: {env_config.oauth_client_secret_env}"],
                warnings=[],
                execution_time=0.0
            )
        
        # Create datasphere config
        datasphere_config = {
            "base_url": env_config.base_url,
            "oauth": {
                "client_id": env_config.oauth_client_id,
                "client_secret": client_secret,
                "token_url": env_config.token_url
            }
        }
        
        # Create Glue database name
        glue_database = f"datasphere_{env_config.aws_glue_database_suffix}"
        
        logger.info(f"🚀 Starting extraction from {env_config.display_name}")
        logger.info(f"📍 Base URL: {env_config.base_url}")
        logger.info(f"🗄️ Target Glue Database: {glue_database}")
        
        if dry_run:
            logger.info("🧪 DRY RUN MODE - No changes will be made to AWS Glue")
            
            try:
                # Only test discovery, don't replicate
                client = EnhancedDatasphereClient(datasphere_config)
                models = client.discover_analytical_models()
                
                return ExtractionResult(
                    success=True,
                    tables_discovered=len(models),
                    tables_replicated=0,  # Dry run
                    errors=[],
                    warnings=["Dry run mode - no replication performed"],
                    execution_time=0.0
                )
            except Exception as e:
                return ExtractionResult(
                    success=False,
                    tables_discovered=0,
                    tables_replicated=0,
                    errors=[f"Dry run failed: {str(e)}"],
                    warnings=[],
                    execution_time=0.0
                )
        
        # Run actual extraction
        result = run_enhanced_metadata_extraction(
            datasphere_config=datasphere_config,
            aws_config=aws_config,
            glue_database=glue_database
        )
        
        # Store result for this environment
        self.results[env_name] = {
            "environment": env_config.display_name,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
        return result
    
    def extract_from_all_environments(
        self, 
        aws_config: Dict[str, Any],
        dry_run: bool = False,
        skip_on_error: bool = True
    ) -> Dict[str, ExtractionResult]:
        """Extract metadata from all available environments"""
        
        logger.info("🌍 Starting multi-environment metadata extraction")
        
        all_results = {}
        
        for env_name, env_config in self.environments.items():
            try:
                logger.info(f"\n{'='*60}")
                logger.info(f"Processing {env_config.display_name}")
                logger.info(f"{'='*60}")
                
                result = self.extract_from_environment(env_name, aws_config, dry_run)
                all_results[env_name] = result
                
                if result.success:
                    logger.info(f"✅ {env_config.display_name}: {result.tables_replicated} tables replicated")
                else:
                    logger.error(f"❌ {env_config.display_name}: Extraction failed")
                    if not skip_on_error:
                        logger.error("🛑 Stopping due to error (skip_on_error=False)")
                        break
                
            except Exception as e:
                error_msg = f"Critical error in {env_config.display_name}: {e}"
                logger.error(f"❌ {error_msg}")
                
                all_results[env_name] = ExtractionResult(
                    success=False,
                    tables_discovered=0,
                    tables_replicated=0,
                    errors=[error_msg],
                    warnings=[],
                    execution_time=0.0
                )
                
                if not skip_on_error:
                    break
        
        return all_results
    
    def generate_summary_report(self, results: Dict[str, ExtractionResult]) -> Dict[str, Any]:
        """Generate a comprehensive summary report"""
        
        total_discovered = sum(r.tables_discovered for r in results.values())
        total_replicated = sum(r.tables_replicated for r in results.values())
        successful_envs = [env for env, r in results.items() if r.success]
        failed_envs = [env for env, r in results.items() if not r.success]
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_environments": len(results),
            "successful_environments": len(successful_envs),
            "failed_environments": len(failed_envs),
            "total_tables_discovered": total_discovered,
            "total_tables_replicated": total_replicated,
            "success_rate": f"{(len(successful_envs) / len(results) * 100):.1f}%" if results else "0%",
            "environments": {}
        }
        
        for env_name, result in results.items():
            env_config = self.environments[env_name]
            summary["environments"][env_name] = {
                "display_name": env_config.display_name,
                "success": result.success,
                "tables_discovered": result.tables_discovered,
                "tables_replicated": result.tables_replicated,
                "execution_time": result.execution_time,
                "glue_database": f"datasphere_{env_config.aws_glue_database_suffix}",
                "errors": result.errors,
                "warnings": result.warnings
            }
        
        return summary

def main():
    """Main function for multi-environment extraction"""
    
    print("🌍 Multi-Environment SAP Datasphere Metadata Extractor")
    print("=" * 65)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    extractor = MultiEnvironmentExtractor()
    
    # List available environments
    print("📋 Available Environments:")
    print("=" * 26)
    
    environments = extractor.list_environments()
    available_envs = []
    
    for env in environments:
        status = "✅ Ready" if env["credentials_available"] else "❌ Missing credentials"
        print(f"• {env['display_name']}: {status}")
        print(f"  URL: {env['base_url']}")
        print(f"  Glue DB: {env['glue_database']}")
        print(f"  Secret: {env['client_secret_env']}")
        print()
        
        if env["credentials_available"]:
            available_envs.append(env["name"])
    
    if not available_envs:
        print("❌ No environments have credentials configured!")
        print("\n💡 Set up credentials:")
        for env in environments:
            print(f"export {env['client_secret_env']}='your_secret_for_{env['name']}'")
        return
    
    # AWS Configuration
    aws_config = {
        "region": os.getenv("AWS_REGION", "us-east-1")
    }
    
    print(f"☁️ AWS Configuration:")
    print(f"Region: {aws_config['region']}")
    print()
    
    # Interactive mode
    print("🎯 Extraction Options:")
    print("1. Test all environment connections")
    print("2. Extract from specific environment")
    print("3. Extract from all available environments")
    print("4. Dry run (test without AWS changes)")
    
    choice = input("\nChoose option [3]: ").strip()
    if not choice:
        choice = "3"
    
    if choice == "1":
        # Test connections
        print("\n🔍 Testing Environment Connections")
        print("=" * 35)
        
        for env_name in available_envs:
            result = extractor.test_environment_connection(env_name)
            env_config = extractor.environments[env_name]
            
            if result["success"]:
                print(f"✅ {env_config.display_name}: {result['models_discovered']} models found")
                if result["models"]:
                    print(f"   Sample models: {', '.join(result['models'])}")
            else:
                print(f"❌ {env_config.display_name}: {result['error']}")
            print()
    
    elif choice == "2":
        # Extract from specific environment
        print(f"\nAvailable environments: {', '.join(available_envs)}")
        env_name = input("Enter environment name: ").strip().lower()
        
        if env_name not in available_envs:
            print(f"❌ Invalid environment: {env_name}")
            return
        
        dry_run = input("Dry run? [y/N]: ").strip().lower() == 'y'
        
        result = extractor.extract_from_environment(env_name, aws_config, dry_run)
        
        print(f"\n🎯 Extraction Results for {extractor.environments[env_name].display_name}:")
        print(f"Success: {result.success}")
        print(f"Tables discovered: {result.tables_discovered}")
        print(f"Tables replicated: {result.tables_replicated}")
        print(f"Execution time: {result.execution_time:.2f}s")
        
        if result.errors:
            print(f"Errors: {len(result.errors)}")
            for error in result.errors:
                print(f"  • {error}")
    
    elif choice == "3":
        # Extract from all environments
        dry_run = input("Dry run? [y/N]: ").strip().lower() == 'y'
        skip_on_error = input("Skip failed environments? [Y/n]: ").strip().lower() != 'n'
        
        results = extractor.extract_from_all_environments(aws_config, dry_run, skip_on_error)
        
        # Generate and display summary
        summary = extractor.generate_summary_report(results)
        
        print("\n" + "=" * 70)
        print("MULTI-ENVIRONMENT EXTRACTION SUMMARY")
        print("=" * 70)
        
        print(f"📊 Total Environments: {summary['total_environments']}")
        print(f"✅ Successful: {summary['successful_environments']}")
        print(f"❌ Failed: {summary['failed_environments']}")
        print(f"📈 Success Rate: {summary['success_rate']}")
        print(f"🔍 Total Tables Discovered: {summary['total_tables_discovered']}")
        print(f"✅ Total Tables Replicated: {summary['total_tables_replicated']}")
        
        print(f"\n📋 Environment Details:")
        for env_name, env_data in summary["environments"].items():
            status = "✅" if env_data["success"] else "❌"
            print(f"{status} {env_data['display_name']}: {env_data['tables_replicated']}/{env_data['tables_discovered']} tables")
            print(f"   Glue Database: {env_data['glue_database']}")
            if env_data["errors"]:
                print(f"   Errors: {len(env_data['errors'])}")
        
        # Save detailed results
        results_file = f"multi_env_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            # Convert ExtractionResult objects to dicts for JSON serialization
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
                "detailed_results": json_results
            }, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: {results_file}")
    
    elif choice == "4":
        # Dry run all environments
        print("\n🧪 Dry Run - Testing All Environments")
        print("=" * 38)
        
        results = extractor.extract_from_all_environments(aws_config, dry_run=True)
        
        for env_name, result in results.items():
            env_config = extractor.environments[env_name]
            if result.success:
                print(f"✅ {env_config.display_name}: {result.tables_discovered} models discoverable")
            else:
                print(f"❌ {env_config.display_name}: {result.errors[0] if result.errors else 'Unknown error'}")
    
    print("\n🎉 Multi-environment extraction completed!")

if __name__ == "__main__":
    main()