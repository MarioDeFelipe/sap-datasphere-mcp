# SAP Datasphere MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

A Model Context Protocol (MCP) server that provides AI assistants with seamless access to SAP Datasphere capabilities including space management, data discovery, and analytics operations.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/sap-datasphere-mcp-server.git
cd sap-datasphere-mcp-server

# Install dependencies
pip install mcp pydantic requests

# Test the server
python test_simple_server.py

# Configure with Claude Desktop (see Configuration section)
```

## ✨ Key Features

## Features

### 🏢 Space Management
- List all Datasphere spaces
- Get detailed space information
- View space configurations and metadata

### 🔍 Data Discovery
- Search tables and views across spaces
- Get detailed table schemas and column information
- Explore data catalog and metadata

### 🔗 Data Integration
- List and monitor data connections
- Check connection status and health
- View data source configurations

### ⚡ Task Management
- Monitor data integration tasks
- Check task execution status
- View task schedules and results

### 🛒 Marketplace Integration
- Browse available data packages
- Search marketplace content
- View package details and pricing

### 📊 Data Querying
- Execute SQL queries (simulated)
- View query results and performance
- Access analytical data

## Installation

### Prerequisites
- Python 3.10 or higher
- MCP-compatible AI assistant (Claude Desktop, etc.)

### Install Dependencies
```bash
pip install mcp pydantic requests
```

### Configuration

The server can work in two modes:

1. **Mock Mode** (Default): Uses simulated data for development and testing
2. **Live Mode**: Connects to real SAP Datasphere APIs (requires OAuth credentials)

To configure for live mode, update the `DATASPHERE_CONFIG` in `sap_datasphere_mcp_server.py`:

```python
DATASPHERE_CONFIG = {
    "tenant_id": "your-tenant-id",
    "base_url": "https://your-tenant.eu10.hcs.cloud.sap",
    "use_mock_data": False,  # Set to False for live mode
    "oauth_config": {
        "client_id": "your-oauth-client-id",
        "client_secret": "your-oauth-client-secret",
        "token_url": "https://your-tenant.eu10.hcs.cloud.sap/oauth/token"
    }
}
```

## Usage

### Running the Server

```bash
python sap_datasphere_mcp_server.py
```

### MCP Client Configuration

Add to your MCP client configuration (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "sap-datasphere": {
      "command": "python",
      "args": ["path/to/sap_datasphere_mcp_server.py"],
      "env": {}
    }
  }
}
```

### Available Tools

#### Space Operations
- `list_spaces` - List all Datasphere spaces
- `get_space_info` - Get detailed space information

#### Data Discovery
- `search_tables` - Search for tables across spaces
- `get_table_schema` - Get detailed table schema

#### Integration Management
- `list_connections` - List data source connections
- `get_task_status` - Check task execution status

#### Marketplace
- `browse_marketplace` - Browse available data packages

#### Data Access
- `execute_query` - Execute SQL queries (simulated)

### Available Resources

- `datasphere://spaces` - All Datasphere spaces
- `datasphere://connections` - Data source connections
- `datasphere://tasks` - Integration tasks
- `datasphere://marketplace` - Marketplace packages
- `datasphere://spaces/{space_id}/tables` - Tables in specific space

## Example Queries

### List All Spaces
```
Use the list_spaces tool to show me all available Datasphere spaces
```

### Search for Sales Data
```
Search for tables containing "sales" or "customer" data
```

### Get Table Schema
```
Show me the schema for the CUSTOMER_DATA table in the SALES_ANALYTICS space
```

### Check Task Status
```
What's the status of data integration tasks in the FINANCE_DWH space?
```

### Browse Marketplace
```
Show me available data packages in the Financial Data category
```

## Development

### Mock Data
The server includes comprehensive mock data for development:
- 3 sample spaces (Sales Analytics, Finance DWH, HR Analytics)
- Sample tables with realistic schemas
- Data connections to various systems
- Integration tasks with status information
- Marketplace packages

### Adding Real API Integration
To connect to real SAP Datasphere APIs:

1. Obtain OAuth2 credentials from your Datasphere administrator
2. Update `DATASPHERE_CONFIG` with your credentials
3. Set `use_mock_data: False`
4. Implement real API calls in the tool handlers

### Testing
```bash
# Install dev dependencies
pip install pytest pytest-asyncio

# Run tests
pytest
```

## Architecture

The MCP server follows the Model Context Protocol specification:
- **Resources**: Provide access to Datasphere data and metadata
- **Tools**: Enable AI assistants to perform operations
- **Prompts**: Guide AI interactions with Datasphere

## Security

- OAuth2 client credentials flow for authentication
- Secure credential storage and management
- Read-only operations by default
- Configurable permissions and scopes

## Troubleshooting

### Common Issues

1. **OAuth Authentication Errors**
   - Verify client credentials are correct
   - Check OAuth client has proper scopes
   - Ensure tenant URL is correct

2. **Connection Timeouts**
   - Check network connectivity
   - Verify Datasphere tenant is accessible
   - Increase timeout values if needed

3. **Permission Errors**
   - Verify OAuth client has API access permissions
   - Check space-level permissions
   - Contact Datasphere administrator

### Logging
Enable debug logging by setting the log level:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For issues and questions:
- 📖 Check the [troubleshooting section](#troubleshooting)
- 📚 Review [SAP Datasphere documentation](https://help.sap.com/docs/SAP_DATASPHERE)
- 👥 Contact your Datasphere administrator for OAuth setup


## 📊 Project Stats

- **Language**: Python 3.10+
- **Protocol**: Model Context Protocol (MCP)
- **Platform**: SAP Datasphere
- **License**: MIT
- **Status**: Active Development
