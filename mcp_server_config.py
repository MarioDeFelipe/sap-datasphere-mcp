#!/usr/bin/env python3
"""
MCP Server Configuration Management
Handles environment-specific configuration for the SAP Datasphere MCP server
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class MCPEnvironmentConfig:
    """Environment-specific MCP server configuration"""
    name: str
    datasphere_base_url: str
    aws_region: str
    oauth_redirect_uri: str
    enable_oauth: bool = True
    enable_caching: bool = True
    cache_ttl_seconds: int = 300
    log_level: str = "INFO"
    max_concurrent_requests: int = 10
    request_timeout_seconds: int = 30

class MCPConfigManager:
    """Manages MCP server configuration across environments"""
    
    def __init__(self, config_dir: str = "."):
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "mcp_server_config.json"
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file or create default"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
                self.environments = {
                    name: MCPEnvironmentConfig(**env_config)
                    for name, env_config in config_data.get("environments", {}).items()
                }
        else:
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration for all environments"""
        self.environments = {
            "dog": MCPEnvironmentConfig(
                name="dog",
                datasphere_base_url="https://ailien-test.eu10.hcs.cloud.sap",
                aws_region="us-east-1",
                oauth_redirect_uri="http://localhost:8080/callback",
                enable_oauth=True,
                enable_caching=True,
                cache_ttl_seconds=300,
                log_level="DEBUG",
                max_concurrent_requests=5,
                request_timeout_seconds=30
            ),
            
            "wolf": MCPEnvironmentConfig(
                name="wolf",
                datasphere_base_url="https://ailien-test.eu10.hcs.cloud.sap",
                aws_region="us-east-1",
                oauth_redirect_uri="http://localhost:5000/callback",
                enable_oauth=True,
                enable_caching=True,
                cache_ttl_seconds=600,
                log_level="INFO",
                max_concurrent_requests=10,
                request_timeout_seconds=45
            ),
            
            "bear": MCPEnvironmentConfig(
                name="bear",
                datasphere_base_url="https://ailien-test.eu10.hcs.cloud.sap",
                aws_region="us-east-1",
                oauth_redirect_uri="https://api.ailien.studio/oauth/callback",
                enable_oauth=True,
                enable_caching=True,
                cache_ttl_seconds=900,
                log_level="WARNING",
                max_concurrent_requests=20,
                request_timeout_seconds=60
            )
        }
        
        self.save_config()
    
    def get_environment_config(self, environment: str) -> MCPEnvironmentConfig:
        """Get configuration for specific environment"""
        if environment not in self.environments:
            raise ValueError(f"Unknown environment: {environment}")
        
        return self.environments[environment]
    
    def save_config(self):
        """Save configuration to file"""
        config_data = {
            "environments": {
                name: asdict(config)
                for name, config in self.environments.items()
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def update_environment_config(self, environment: str, **kwargs):
        """Update configuration for specific environment"""
        if environment not in self.environments:
            raise ValueError(f"Unknown environment: {environment}")
        
        config = self.environments[environment]
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        self.save_config()
    
    def list_environments(self) -> Dict[str, MCPEnvironmentConfig]:
        """List all available environments"""
        return self.environments.copy()

def get_mcp_config(environment: str = None) -> MCPEnvironmentConfig:
    """Get MCP configuration for specified environment"""
    if environment is None:
        environment = os.getenv("MCP_ENVIRONMENT", "dog")
    
    config_manager = MCPConfigManager()
    return config_manager.get_environment_config(environment)

if __name__ == "__main__":
    # Create and display default configuration
    config_manager = MCPConfigManager()
    
    print("MCP Server Configuration:")
    print("=" * 50)
    
    for env_name, env_config in config_manager.list_environments().items():
        print(f"\n{env_name.upper()} Environment:")
        print(f"  Datasphere URL: {env_config.datasphere_base_url}")
        print(f"  AWS Region: {env_config.aws_region}")
        print(f"  OAuth Redirect: {env_config.oauth_redirect_uri}")
        print(f"  OAuth Enabled: {env_config.enable_oauth}")
        print(f"  Caching: {env_config.enable_caching}")
        print(f"  Cache TTL: {env_config.cache_ttl_seconds}s")
        print(f"  Log Level: {env_config.log_level}")
    
    print(f"\nConfiguration saved to: {config_manager.config_file}")