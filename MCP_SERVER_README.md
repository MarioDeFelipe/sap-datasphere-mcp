# SAP Datasphere MCP Server

A comprehensive Model Context Protocol (MCP) server that provides AI-accessible metadata operations for SAP Datasphere and AWS Glue Data Catalog integration.

## 🚀 Features

### Core Capabilities
- **Unified Metadata Search**: Search across Datasphere and AWS Glue with business context
- **OAuth Authentication**: Full access to SAP Datasphere assets using OAuth Authorization Code Flow
- **Business Context Preservation**: Maintain business metadata, steward information, and governance context
- **Data Lineage Exploration**: Trace relationships between assets across systems
- **Synchronization Monitoring**: Real-time sync status and performance metrics
- **AI Integration**: Standardized MCP protocol for seamless AI tool integration

### MCP Tools Available

| Tool | Description | Use Case |
|------|-------------|----------|
| `search_metadata` | Search assets across systems with business context | Find data assets by name, description, or business context |
| `get_asset_details` | Get detailed information about specific assets | Explore schema, lineage, and business metadata |
| `discover_spaces` | Discover all Datasphere spaces with OAuth | Full space inventory with asset counts |
| `get_sync_status` | Monitor synchronization status and health | Track sync operations and identify issues |
| `explore_data_lineage` | Trace data relationships and dependencies | Understand data flow and impact analysis |
| `trigger_sync` | Initiate metadata synchronization operations | Manual sync control with priority settings |

## 🏗️ Architecture

### Three-Environment Support

#### 🐕 DOG Environment (Development)
- **Purpose**: Development and testing with live integrations
- **Port**: 8080 (OAuth callback)
- **Features**: Debug logging, hot-reload, comprehensive error reporting

#### 🐺 WOLF Environment (Testing)
- **Purpose**: Integration testing with production-like settings
- **Port**: 5000 (OAuth callback)
- **Features**: Performance monitoring, load testing, validation

#### 🐻 BEAR Environment (Production)
- **Purpose**: Enterprise-grade production deployment
- **Endpoint**: HTTPS with production OAuth callbacks
- **Features**: High availability, monitoring, alerting

### Integration Components

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   AI Assistant  │◄──►│   MCP Server     │◄──►│  SAP Datasphere │
│   (Claude, etc) │    │                  │    │   (OAuth 2.0)   │
└─────────────────┘    │                  │    └─────────────────┘
                       │                  │    
                       │                  │    ┌─────────────────┐
                       │                  │◄──►│  AWS Glue       │
                       │                  │    │  Data Catalog   │
                       └──────────────────┘    └─────────────────┘
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- SAP Datasphere OAuth application configured
- AWS credentials configured
- Required Python packages (see requirements below)

### Required Dependencies
```bash
pip install mcp asyncio boto3 requests pydantic
```

### Configuration

1. **Create MCP Configuration**:
```bash
python mcp_server_config.py
```

2. **Configure OAuth Application**:
   - Create OAuth app in SAP BTP Cockpit
   - Set redirect URIs for each environment
   - Note client ID and client secret

3. **Set Environment Variables**:
```bash
export MCP_ENVIRONMENT=dog  # or wolf, bear
export SAP_CLIENT_ID=your_oauth_client_id
export SAP_CLIENT_SECRET=your_oauth_client_secret
```

## 🚀 Usage

### Starting the MCP Server

#### Development Environment (DOG)
```bash
python start_mcp_server.py --environment dog
```

#### Testing Environment (WOLF)
```bash
python start_mcp_server.py --environment wolf
```

#### Production Environment (BEAR)
```bash
python start_mcp_server.py --environment bear
```

### Validate Configuration
```bash
python start_mcp_server.py --validate-config --environment dog
```

### Running Tests
```bash
# Test specific environment
python test_mcp_server.py --environment dog

# Generate test report
python test_mcp_server.py --environment dog --output test_report.json
```

## 🔧 MCP Client Integration

### Claude Desktop Configuration
Add to your Claude Desktop `mcp.json`:

```json
{
  "mcpServers": {
    "sap-datasphere": {
      "command": "python",
      "args": ["start_mcp_server.py", "--environment", "dog"],
      "cwd": "/path/to/your/project",
      "env": {
        "MCP_ENVIRONMENT": "dog",
        "SAP_CLIENT_ID": "your_client_id",
        "SAP_CLIENT_SECRET": "your_client_secret"
      }
    }
  }
}
```

### Cursor IDE Configuration
Add to your Cursor settings:

```json
{
  "mcp.servers": {
    "sap-datasphere": {
      "command": ["python", "start_mcp_server.py"],
      "args": ["--environment", "dog"],
      "env": {
        "MCP_ENVIRONMENT": "dog"
      }
    }
  }
}
```

## 📖 Tool Usage Examples

### Search for Assets
```python
# Search for employee-related assets
{
  "tool": "search_metadata",
  "arguments": {
    "query": "employee",
    "asset_types": ["TABLE", "ANALYTICAL_MODEL"],
    "source_systems": ["DATASPHERE"],
    "include_business_context": true
  }
}
```

### Discover All Spaces
```python
# Get all Datasphere spaces with OAuth
{
  "tool": "discover_spaces",
  "arguments": {
    "include_assets": true,
    "force_refresh": true
  }
}
```

### Get Asset Details
```python
# Get detailed information about a specific asset
{
  "tool": "get_asset_details",
  "arguments": {
    "asset_id": "space_id.asset_id",
    "source_system": "DATASPHERE",
    "include_schema": true,
    "include_lineage": true
  }
}
```

### Monitor Sync Status
```python
# Check overall synchronization health
{
  "tool": "get_sync_status",
  "arguments": {
    "detailed": true
  }
}
```

### Trigger Synchronization
```python
# Trigger sync for specific assets
{
  "tool": "trigger_sync",
  "arguments": {
    "asset_ids": ["asset1", "asset2"],
    "priority": "high",
    "dry_run": false
  }
}
```

## 🔐 Security & Authentication

### OAuth 2.0 Flow
1. **Authorization**: User grants permissions via browser
2. **Token Exchange**: Authorization code exchanged for access token
3. **Token Storage**: Secure token storage with automatic refresh
4. **API Access**: Full API access with user permissions

### Security Features
- Secure token storage with encryption
- Automatic token refresh
- Request rate limiting
- Audit logging for all operations
- Environment-specific security controls

## 📊 Monitoring & Logging

### Log Levels by Environment
- **DOG**: DEBUG (detailed development logs)
- **WOLF**: INFO (operational information)
- **BEAR**: WARNING (production warnings and errors)

### Log Files
- `mcp_server_dog.log` - Development environment logs
- `mcp_server_wolf.log` - Testing environment logs  
- `mcp_server_bear.log` - Production environment logs

### Metrics Tracked
- Request/response times
- OAuth token refresh events
- Cache hit/miss rates
- Error rates by tool
- Asset discovery statistics

## 🧪 Testing

### Test Categories
1. **Configuration Validation**: Verify environment settings
2. **Tool Listing**: Ensure all tools are registered
3. **Space Discovery**: Test OAuth-enabled space discovery
4. **Metadata Search**: Validate search functionality
5. **Sync Status**: Check synchronization monitoring

### Running Comprehensive Tests
```bash
# Test all environments
for env in dog wolf bear; do
  python test_mcp_server.py --environment $env --output "test_report_$env.json"
done
```

## 🔧 Troubleshooting

### Common Issues

#### OAuth Authentication Failures
```bash
# Check OAuth configuration
python start_mcp_server.py --validate-config --environment dog

# Verify redirect URI matches OAuth app configuration
# Ensure client ID and secret are correctly set
```

#### Connection Timeouts
```bash
# Increase timeout in configuration
python -c "
from mcp_server_config import MCPConfigManager
config = MCPConfigManager()
config.update_environment_config('dog', request_timeout_seconds=60)
"
```

#### Cache Issues
```bash
# Disable caching for debugging
python -c "
from mcp_server_config import MCPConfigManager
config = MCPConfigManager()
config.update_environment_config('dog', enable_caching=False)
"
```

### Debug Mode
```bash
# Enable debug logging
export MCP_LOG_LEVEL=DEBUG
python start_mcp_server.py --environment dog
```

## 📈 Performance Optimization

### Caching Strategy
- **Metadata Cache**: 5-15 minutes TTL based on environment
- **Space Discovery**: Cached for faster repeated access
- **Asset Details**: Cached with automatic invalidation

### Concurrent Requests
- **DOG**: 5 concurrent requests (development)
- **WOLF**: 10 concurrent requests (testing)
- **BEAR**: 20 concurrent requests (production)

### Memory Management
- Automatic cache cleanup
- Request timeout controls
- Connection pooling for AWS services

## 🔄 Integration with Existing Components

### Datasphere Connector
- Uses `EnhancedDatasphereConnector` with OAuth support
- Automatic fallback to existing authentication methods
- Full compatibility with existing metadata sync workflows

### AWS Glue Connector
- Leverages `EnhancedGlueConnector` for rich metadata
- Business context preservation
- Advanced tagging and classification

### Sync Engine
- Integrates with existing `MetadataSyncEngine`
- Priority-based synchronization
- Comprehensive audit logging

## 📚 API Reference

### Tool Schemas
Each MCP tool includes comprehensive JSON schema validation:
- Input parameter validation
- Required field enforcement
- Type checking and conversion
- Default value handling

### Response Formats
All tools return structured JSON responses with:
- Consistent error handling
- Timestamp information
- Metadata about the operation
- Business context when available

## 🚀 Future Enhancements

### Planned Features
- Real-time event streaming
- Advanced lineage visualization
- Machine learning integration
- Multi-tenant support
- GraphQL query interface

### Performance Improvements
- Connection pooling optimization
- Advanced caching strategies
- Async operation batching
- Memory usage optimization

---

## 📞 Support

For issues, questions, or contributions:
1. Check the troubleshooting section
2. Review log files for detailed error information
3. Validate configuration with built-in tools
4. Test with different environments to isolate issues

**Happy metadata exploring! 🎉**