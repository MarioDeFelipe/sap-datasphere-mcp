# 🤖 SAP Datasphere MCP Server Setup Guide

Complete guide for setting up the SAP Datasphere MCP Server with AI assistants like Claude Desktop and Cursor IDE.

## 🎯 Overview

The SAP Datasphere MCP Server provides AI assistants with direct access to:
- **Metadata Discovery**: Search and explore SAP Datasphere assets
- **OAuth Authentication**: Secure access to real SAP data
- **Data Replication Control**: Trigger and monitor data movement to AWS
- **Business Context**: Rich metadata with governance information
- **Data Lineage**: Trace relationships across systems

## 🚀 Quick Setup

### 1. Prerequisites

```bash
# Required software
Python 3.10+
Git
SAP Datasphere account with OAuth application
AWS account (optional, for replication features)

# AI Assistant (choose one)
Claude Desktop
Cursor IDE
VS Code with MCP extension
```

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/MarioDeFelipe/sap-datasphere-mcp.git
cd sap-datasphere-mcp

# Install dependencies
pip install -r requirements.txt

# Configure MCP server
python mcp_server_config.py
```

### 3. SAP OAuth Configuration

#### Create OAuth Application in SAP BTP
1. Go to SAP BTP Cockpit → Security → OAuth
2. Create new OAuth 2.0 Client
3. Set redirect URIs:
   - `http://localhost:8080/callback` (Dog environment)
   - `http://localhost:5000/callback` (Wolf environment)
4. Note the Client ID and Client Secret

#### Configure Credentials
```bash
# Set environment variables
export SAP_CLIENT_ID="your_oauth_client_id"
export SAP_CLIENT_SECRET="your_oauth_client_secret"
export SAP_BASE_URL="https://your-tenant.eu20.hcs.cloud.sap"
export SAP_TOKEN_URL="https://your-tenant.authentication.eu20.hana.ondemand.com/oauth/token"
```

### 4. Test MCP Server

```bash
# Test configuration
python sap_datasphere_mcp_server.py --validate-config --environment dog

# Start MCP server
python sap_datasphere_mcp_server.py --environment dog

# Run tests
python test_mcp_server.py --environment dog
```

## 🎨 Claude Desktop Integration

### Configuration File Location
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### Configuration Example
```json
{
  "mcpServers": {
    "sap-datasphere": {
      "command": "python",
      "args": ["/path/to/sap-datasphere-mcp/sap_datasphere_mcp_server.py", "--environment", "dog"],
      "env": {
        "SAP_CLIENT_ID": "your_oauth_client_id",
        "SAP_CLIENT_SECRET": "your_oauth_client_secret",
        "SAP_BASE_URL": "https://your-tenant.eu20.hcs.cloud.sap",
        "SAP_TOKEN_URL": "https://your-tenant.authentication.eu20.hana.ondemand.com/oauth/token"
      }
    }
  }
}
```

### Restart Claude Desktop
After adding the configuration, restart Claude Desktop to load the MCP server.

### Test Integration
Ask Claude:
```
"List all SAP Datasphere spaces"
"Search for tables containing customer data"
"Show me the sync status between Datasphere and AWS"
```

## 💻 Cursor IDE Integration

### Settings Configuration
Add to Cursor settings (`Cmd/Ctrl + ,` → Extensions → MCP):

```json
{
  "mcp.servers": {
    "sap-datasphere": {
      "command": ["python", "/path/to/sap-datasphere-mcp/sap_datasphere_mcp_server.py"],
      "args": ["--environment", "dog"],
      "env": {
        "SAP_CLIENT_ID": "your_oauth_client_id",
        "SAP_CLIENT_SECRET": "your_oauth_client_secret"
      }
    }
  }
}
```

### Usage in Development
- Use `@sap-datasphere` in chat to access MCP tools
- Integrate data discovery into your development workflow
- Get real-time information about SAP assets while coding

## 🔧 Environment Configuration

### Dog Environment (Development)
```bash
# Start development server
python sap_datasphere_mcp_server.py --environment dog

# Features:
# - Debug logging enabled
# - Hot-reload capabilities
# - Comprehensive error reporting
# - OAuth callback: http://localhost:8080/callback
```

### Wolf Environment (Testing)
```bash
# Start testing server
python sap_datasphere_mcp_server.py --environment wolf

# Features:
# - Production-like settings
# - Performance monitoring
# - Integration testing
# - OAuth callback: http://localhost:5000/callback
```

### Bear Environment (Production)
```bash
# Deploy to AWS Lambda
python deploy_bear_environment.py

# Features:
# - Serverless auto-scaling
# - Enterprise monitoring
# - High availability
# - Production OAuth callbacks
```

## 🛠️ Available MCP Tools

### 1. search_metadata
Search for assets across SAP Datasphere and AWS Glue.

**Example Usage:**
```
"Search for all tables related to finance"
"Find analytical models in the sales domain"
```

**Parameters:**
- `query`: Search term
- `asset_types`: Filter by TABLE, VIEW, ANALYTICAL_MODEL, SPACE
- `source_systems`: Filter by DATASPHERE, GLUE
- `include_business_context`: Include rich metadata

### 2. discover_spaces
Discover all SAP Datasphere spaces with OAuth authentication.

**Example Usage:**
```
"List all Datasphere spaces with their assets"
"Show me space details for SAP_CONTENT"
```

**Parameters:**
- `include_assets`: Include assets within each space
- `force_refresh`: Bypass cache and refresh from SAP

### 3. get_asset_details
Get detailed information about specific assets.

**Example Usage:**
```
"Show me details for SAP_SC_FI_T_Products table"
"Get schema information for the customer analytics model"
```

**Parameters:**
- `asset_id`: Unique asset identifier
- `source_system`: DATASPHERE or GLUE
- `include_schema`: Include detailed schema
- `include_lineage`: Include data lineage

### 4. get_sync_status
Monitor synchronization status and health.

**Example Usage:**
```
"What's the overall sync status?"
"Check sync status for financial data assets"
```

**Parameters:**
- `asset_id`: Optional specific asset
- `detailed`: Include performance metrics

### 5. explore_data_lineage
Trace data relationships and dependencies.

**Example Usage:**
```
"Show me the lineage for sales order data"
"Trace upstream dependencies for the revenue model"
```

**Parameters:**
- `asset_id`: Starting asset for lineage
- `direction`: upstream, downstream, or both
- `max_depth`: Maximum traversal depth

### 6. trigger_sync
Initiate metadata synchronization operations.

**Example Usage:**
```
"Trigger a high-priority sync for all financial assets"
"Start sync for customer data with dry-run mode"
```

**Parameters:**
- `asset_ids`: Specific assets or empty for all
- `priority`: critical, high, medium, low
- `dry_run`: Preview without executing

## 🔍 Troubleshooting

### Common Issues

#### 1. OAuth Authentication Failures
```bash
# Check OAuth configuration
python sap_datasphere_mcp_server.py --validate-config --environment dog

# Verify redirect URI matches OAuth app
# Ensure client credentials are correct
```

#### 2. MCP Server Not Found
```bash
# Verify Python path in MCP configuration
which python

# Check if server starts manually
python sap_datasphere_mcp_server.py --environment dog
```

#### 3. Permission Errors
```bash
# Check SAP Datasphere permissions
# Verify OAuth scopes include metadata access
# Ensure user has space access rights
```

#### 4. Connection Timeouts
```bash
# Increase timeout in configuration
python -c "
from mcp_server_config import MCPConfigManager
config = MCPConfigManager()
config.update_environment_config('dog', request_timeout_seconds=60)
"
```

### Debug Mode
```bash
# Enable debug logging
export MCP_LOG_LEVEL=DEBUG
python sap_datasphere_mcp_server.py --environment dog

# Check log files
tail -f mcp_server_dog.log
```

### Validate Configuration
```bash
# Test all components
python test_mcp_server.py --environment dog --comprehensive

# Test specific functionality
python test_mcp_server.py --environment dog --test-oauth
python test_mcp_server.py --environment dog --test-search
```

## 📊 Monitoring & Performance

### Log Files
- `mcp_server_dog.log` - Development environment
- `mcp_server_wolf.log` - Testing environment
- `mcp_server_bear.log` - Production environment

### Performance Metrics
- Request/response times
- OAuth token refresh events
- Cache hit/miss rates
- Error rates by tool
- Asset discovery statistics

### Health Checks
```bash
# Check server health
curl http://localhost:8080/health

# Monitor performance
python monitor_mcp_performance.py --environment dog
```

## 🚀 Advanced Configuration

### Custom Tool Development
```python
# Add custom MCP tool
@server.call_tool()
async def handle_custom_tool(name: str, arguments: Dict[str, Any]):
    if name == "custom_analysis":
        # Your custom logic here
        return [types.TextContent(type="text", text="Custom result")]
```

### Multi-Tenant Setup
```python
# Configure for multiple SAP tenants
TENANT_CONFIGS = {
    "tenant1": {
        "base_url": "https://tenant1.eu10.hcs.cloud.sap",
        "client_id": "tenant1_client_id"
    },
    "tenant2": {
        "base_url": "https://tenant2.us10.hcs.cloud.sap", 
        "client_id": "tenant2_client_id"
    }
}
```

### Performance Optimization
```python
# Configure caching
MCP_CONFIG = {
    "enable_caching": True,
    "cache_ttl_seconds": 300,  # 5 minutes
    "max_concurrent_requests": 10,
    "request_timeout_seconds": 30
}
```

## 📚 Additional Resources

- [MCP Server README](MCP_SERVER_README.md) - Detailed technical documentation
- [Model Context Protocol](https://modelcontextprotocol.io/) - Official MCP specification
- [SAP Datasphere API](https://help.sap.com/docs/SAP_DATASPHERE) - SAP API documentation
- [Claude Desktop MCP Guide](https://docs.anthropic.com/claude/docs/mcp) - Claude-specific setup

## 🎉 Success Validation

Once setup is complete, you should be able to:

1. ✅ Ask your AI assistant about SAP Datasphere spaces
2. ✅ Search for data assets using natural language
3. ✅ Get detailed schema and metadata information
4. ✅ Monitor synchronization status and health
5. ✅ Trigger data operations through AI commands
6. ✅ Explore data lineage and relationships

**Congratulations! Your SAP Datasphere MCP Server is ready for AI-powered data operations! 🚀**