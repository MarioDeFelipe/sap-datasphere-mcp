#!/usr/bin/env python3
"""
Configuration for Web Dashboard Real Connectors
Contains the working credentials for Datasphere and AWS Glue
"""

import os
from typing import Dict, Any

def get_datasphere_config() -> Dict[str, Any]:
    """Get Datasphere configuration from AWS Secrets Manager"""
    
    try:
        import boto3
        import json
        
        # Get credentials from AWS Secrets Manager
        secrets_client = boto3.client('secretsmanager', region_name='us-east-1')
        response = secrets_client.get_secret_value(SecretId='sap-datasphere-credentials')
        secret_data = json.loads(response['SecretString'])
        
        return {
            "base_url": secret_data.get("base_url"),
            "client_id": secret_data.get("client_id"),
            "client_secret": secret_data.get("client_secret"),
            "token_url": secret_data.get("token_url"),
            "tenant_name": secret_data.get("tenant_name"),
            "authorization_url": secret_data.get("authorization_url"),
            "oauth_token_url": secret_data.get("oauth_token_url"),
            "saml_audience": secret_data.get("saml_audience")
        }
        
    except Exception as e:
        print(f"⚠️ Failed to retrieve credentials from AWS Secrets Manager: {e}")
        # Fallback to environment variables only (no hardcoded secrets)
        return {
            "base_url": os.getenv("SAP_BASE_URL", ""),
            "client_id": os.getenv("SAP_CLIENT_ID", ""),
            "client_secret": os.getenv("SAP_CLIENT_SECRET", ""),
            "token_url": os.getenv("SAP_TOKEN_URL", ""),
            "tenant_name": os.getenv("SAP_TENANT_NAME", ""),
            "authorization_url": os.getenv("SAP_AUTHORIZATION_URL", ""),
            "oauth_token_url": os.getenv("SAP_OAUTH_TOKEN_URL", ""),
            "saml_audience": os.getenv("SAP_SAML_AUDIENCE", "")
        }

def get_glue_config() -> Dict[str, Any]:
    """Get AWS Glue configuration with Web Dashboard table-level display settings"""
    
    config = {
        "region": os.getenv("AWS_REGION", "us-east-1"),
        "profile_name": os.getenv("AWS_PROFILE", None),
        # Web Dashboard configuration for table-level display
        "primary_database": "datasphere_real_assets",  # Focus on this database for Web Dashboard
        "target_databases": [
            "datasphere_real_assets",        # Primary database with 36 real SAP assets
            "datasphere_discovered_assets",  # Secondary database with other assets
            "datasphere_web_dashboard",      # Tertiary database
            "sap_datasphere_assets"          # Quaternary database
        ]
    }
    
    return config

def test_configurations() -> Dict[str, bool]:
    """Test both configurations"""
    
    results = {
        "datasphere": False,
        "glue": False
    }
    
    # Test Datasphere
    try:
        from datasphere_connector import DatasphereConnector, DatasphereConfig
        
        ds_config_dict = get_datasphere_config()
        ds_config = DatasphereConfig(
            base_url=ds_config_dict["base_url"],
            client_id=ds_config_dict["client_id"],
            client_secret=ds_config_dict["client_secret"],
            token_url=ds_config_dict["token_url"]
        )
        
        ds_connector = DatasphereConnector(ds_config)
        results["datasphere"] = ds_connector.connect()
        print(f"🔍 Datasphere connection test: {'✅ SUCCESS' if results['datasphere'] else '❌ FAILED'}")
        
    except Exception as e:
        print(f"❌ Datasphere test failed: {str(e)}")
    
    # Test AWS Glue
    try:
        from glue_connector import GlueConnector, GlueConfig
        
        glue_config_dict = get_glue_config()
        glue_config = GlueConfig(
            region=glue_config_dict["region"],
            aws_profile=glue_config_dict["profile_name"]
        )
        
        glue_connector = GlueConnector(glue_config)
        results["glue"] = glue_connector.connect()
        print(f"🔍 AWS Glue connection test: {'✅ SUCCESS' if results['glue'] else '❌ FAILED'}")
        
    except Exception as e:
        print(f"❌ AWS Glue test failed: {str(e)}")
    
    return results

if __name__ == "__main__":
    print("🔧 Testing Dashboard Connector Configurations")
    print("=" * 45)
    
    # Test configurations
    results = test_configurations()
    
    print(f"\n📊 Test Results:")
    print(f"   Datasphere: {'✅ Connected' if results['datasphere'] else '❌ Failed'}")
    print(f"   AWS Glue: {'✅ Connected' if results['glue'] else '❌ Failed'}")
    
    if all(results.values()):
        print(f"\n🎉 All connectors ready for dashboard!")
    else:
        print(f"\n⚠️ Some connectors need attention before dashboard can show real data")