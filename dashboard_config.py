#!/usr/bin/env python3
"""
Configuration for Web Dashboard Real Connectors
Contains the working credentials for Datasphere and AWS Glue
"""

import os
from typing import Dict, Any

def get_datasphere_config() -> Dict[str, Any]:
    """Get Datasphere configuration with working credentials"""
    
    # Current working credentials from your environment
    config = {
        "base_url": "https://ailien-test.eu20.hcs.cloud.sap",
        "client_id": "sb-60cb266e-ad9d-49f7-9967-b53b8286a259!b130936|client!b3944",
        "client_secret": "caaea1b9-b09b-4d28-83fe-09966d525243$LOFW4h5LpLvB3Z2FE0P7FiH4-C7qexeQPi22DBiHbz8=",
        "token_url": "https://ailien-test.authentication.eu20.hana.ondemand.com/oauth/token"
    }
    
    # Override with environment variables if available
    config["client_secret"] = os.getenv("DOG_CLIENT_SECRET", config["client_secret"])
    
    return config

def get_glue_config() -> Dict[str, Any]:
    """Get AWS Glue configuration"""
    
    config = {
        "region": os.getenv("AWS_REGION", "us-east-1"),
        "profile_name": os.getenv("AWS_PROFILE", None)
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