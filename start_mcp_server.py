#!/usr/bin/env python3
"""
SAP Datasphere MCP Server Startup Script
Starts the MCP server with environment-specific configuration
"""

import asyncio
import argparse
import logging
import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from sap_datasphere_mcp_server import SAPDatsphereMCPServer, MCPServerConfig
from mcp_server_config import get_mcp_config
from mcp.server.stdio import stdio_server
from mcp.server.models import InitializationOptions

def setup_logging(log_level: str):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stderr),
            logging.FileHandler(f'mcp_server_{os.getenv("MCP_ENVIRONMENT", "dog")}.log')
        ]
    )

async def start_mcp_server(environment: str):
    """Start the MCP server for specified environment"""
    try:
        # Get environment-specific configuration
        env_config = get_mcp_config(environment)
        
        # Setup logging
        setup_logging(env_config.log_level)
        logger = logging.getLogger(__name__)
        
        logger.info(f"Starting SAP Datasphere MCP Server for {environment.upper()} environment")
        logger.info(f"Datasphere URL: {env_config.datasphere_base_url}")
        logger.info(f"AWS Region: {env_config.aws_region}")
        logger.info(f"OAuth Enabled: {env_config.enable_oauth}")
        
        # Create MCP server configuration
        mcp_config = MCPServerConfig(
            datasphere_base_url=env_config.datasphere_base_url,
            aws_region=env_config.aws_region,
            environment_name=env_config.name,
            enable_oauth=env_config.enable_oauth,
            oauth_redirect_uri=env_config.oauth_redirect_uri,
            enable_caching=env_config.enable_caching,
            cache_ttl_seconds=env_config.cache_ttl_seconds
        )
        
        # Initialize MCP server
        mcp_server = SAPDatsphereMCPServer(mcp_config)
        
        logger.info("MCP Server initialized successfully")
        logger.info("Waiting for MCP client connections...")
        
        # Run the MCP server
        async with stdio_server() as (read_stream, write_stream):
            await mcp_server.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name=f"sap-datasphere-mcp-{environment}",
                    server_version="1.0.0",
                    capabilities=mcp_server.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None
                    )
                )
            )
            
    except KeyboardInterrupt:
        logger.info("MCP Server shutdown requested")
    except Exception as e:
        logger.error(f"Error starting MCP server: {str(e)}")
        raise

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Start SAP Datasphere MCP Server")
    parser.add_argument(
        "--environment", "-e",
        choices=["dog", "wolf", "bear"],
        default=os.getenv("MCP_ENVIRONMENT", "dog"),
        help="Environment to run (default: dog)"
    )
    parser.add_argument(
        "--config-dir", "-c",
        default=".",
        help="Configuration directory (default: current directory)"
    )
    parser.add_argument(
        "--validate-config", "-v",
        action="store_true",
        help="Validate configuration and exit"
    )
    
    args = parser.parse_args()
    
    # Set environment variable
    os.environ["MCP_ENVIRONMENT"] = args.environment
    
    if args.validate_config:
        try:
            config = get_mcp_config(args.environment)
            print(f"✅ Configuration for {args.environment} environment is valid")
            print(f"   Datasphere URL: {config.datasphere_base_url}")
            print(f"   AWS Region: {config.aws_region}")
            print(f"   OAuth Enabled: {config.enable_oauth}")
            return 0
        except Exception as e:
            print(f"❌ Configuration validation failed: {str(e)}")
            return 1
    
    # Start the MCP server
    try:
        asyncio.run(start_mcp_server(args.environment))
        return 0
    except Exception as e:
        print(f"❌ Failed to start MCP server: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())