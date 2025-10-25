# SAP Datasphere MCP Server

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-purple.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **AI-accessible SAP Datasphere operations via Model Context Protocol (MCP)**

A Model Context Protocol server that provides AI assistants with direct access to SAP Datasphere metadata, spaces, and assets. Compatible with Claude Desktop, Cursor IDE, and other MCP clients.

## 🚀 Features

- **Space Discovery**: Explore all available SAP Datasphere spaces
- **Asset Search**: Find tables, views, and analytical models using natural language
- **Metadata Exploration**: Get detailed schema and business context information
- **OAuth 2.0 Support**: Secure authentication with SAP Datasphere
- **AI Integration**: Works seamlessly with Claude Desktop, Cursor IDE, and other MCP clients
- **Caching**: Intelligent caching for improved performance

## 🛠️ Installation

### Prerequisites
- Python 3.10 or higher
- SAP Datasphere account with API access
- OAuth 2.0 application configured in SAP BTP (optional but recommended)

### Setup
```bash
# Clone the repository
git clone https://github.com/MarioDeFelipe/sap-datasphere-mcp.git
cd sap-datasphere-mcp

# Install dependencies
pip install -r requirements.txt

# Configure your SAP Datasphere connection (optional)
export SAP_CLIENT_ID="your_oauth_client_id"
export SAP_CLIENT_SECRET="your_oauth_client_secret"
export SAP_TOKEN_URL="https://your-tenant.authentication.eu20.hana.ondemand.com/oauth/token"
```

## 🔧 Configuration

### For Claude Desktop

Add to your Claude Desktop `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sap-datasphere": {
      "command": "python",
      "args": ["/path/to/sap-datasphere-mcp/start_mcp_server.py"],
      "env": {
        "SAP_CLIENT_ID": "your_oauth_client_id",
        "SAP_CLIENT_SECRET": "your_oauth_client_secret",
        "SAP_TOKEN_URL": "https://your-tenant.authentication.eu20.hana.ondemand.com/oauth/token",
        "DATASPHERE_BASE_URL": "https://your-tenant.eu10.hcs.cloud.sap"
      }
    }
  }
}
```

### For Cursor IDE

Add to your Cursor settings:

```json
{
  "mcp.servers": {
    "sap-datasphere": {
      "command": ["python", "/path/to/sap-datasphere-mcp/start_mcp_server.py"],
      "env": {
        "SAP_CLIENT_ID": "your_oauth_client_id",
        "SAP_CLIENT_SECRET": "your_oauth_client_secret"
      }
    }
  }
}
```

## 🎯 Usage Examples

Once configured, you can ask your AI assistant natural language questions about your SAP Datasphere environment:

### Discover Spaces
```
"What SAP Datasphere spaces are available?"
"List all spaces with their asset counts"
```

### Search for Data
```
"Find all tables related to customers"
"Search for financial data assets"
"Show me analytical models in the sales space"
```

### Get Asset Details
```
"Tell me about the SAP_SC_FI_T_Products table"
"What's the schema of the CUSTOMER_DATA table?"
"Show me details about assets in the SAP_CONTENT space"
```

## 🔧 Available MCP Tools

The server provides these tools for AI assistants:

| Tool | Description | Example Use |
|------|-------------|-------------|
| `discover_spaces` | List all Datasphere spaces | "What spaces do I have access to?" |
| `search_assets` | Search for assets by name/description | "Find customer-related tables" |
| `get_asset_details` | Get detailed asset information | "Tell me about the products table" |
| `get_space_info` | Get space information and statistics | "What's in the sales analytics space?" |

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   AI Assistant  │◄──►│   MCP Server     │◄──►│  SAP Datasphere │
│ (Claude, Cursor)│    │                  │    │                 │
│                 │    │ • Space Discovery│    │ • Spaces        │
│                 │    │ • Asset Search   │    │ • Tables        │
│                 │    │ • Metadata Ops   │    │ • Views         │
│                 │    │ • OAuth Auth     │    │ • Models        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🔐 Authentication

The server supports multiple authentication methods:

### OAuth 2.0 (Recommended)
1. Create an OAuth application in SAP BTP Cockpit
2. Set the redirect URI to `http://localhost:8080/callback`
3. Configure the client ID and secret in your environment

### Environment Variables
```bash
export SAP_CLIENT_ID="your_oauth_client_id"
export SAP_CLIENT_SECRET="your_oauth_client_secret"
export SAP_TOKEN_URL="https://your-tenant.authentication.eu20.hana.ondemand.com/oauth/token"
export DATASPHERE_BASE_URL="https://your-tenant.eu10.hcs.cloud.sap"
```

### Mock Mode
If no credentials are provided, the server runs in mock mode with sample data for development and testing.

## 🧪 Testing

### Manual Testing
```bash
# Start the MCP server directly
python start_mcp_server.py

# Test with MCP Inspector (if available)
npx @modelcontextprotocol/inspector python start_mcp_server.py
```

### Development Mode
The server includes mock data for development when SAP credentials are not available:
- Sample spaces (SAP_CONTENT, SALES_ANALYTICS, FINANCE_DWH)
- Mock tables and analytical models
- Realistic schema information

## 📁 Project Structure

```
sap-datasphere-mcp/
├── sap_datasphere_mcp_server.py  # Main MCP server implementation
├── datasphere_connector.py       # SAP Datasphere API connector
├── start_mcp_server.py           # Server launcher script
├── mcp_server_config.py          # Configuration management
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── MCP_SETUP_GUIDE.md           # Detailed setup instructions
├── CHANGELOG.md                  # Version history
└── LICENSE                       # MIT license
```

## 🔧 Development

### Adding New Tools
To add new MCP tools, extend the `_register_tools()` method in `sap_datasphere_mcp_server.py`:

```python
types.Tool(
    name="your_new_tool",
    description="Description of what your tool does",
    inputSchema={
        "type": "object",
        "properties": {
            "parameter": {
                "type": "string",
                "description": "Parameter description"
            }
        },
        "required": ["parameter"]
    }
)
```

### Extending the Connector
Add new methods to `datasphere_connector.py` to support additional SAP Datasphere API operations.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) for the excellent AI integration framework
- [SAP Datasphere](https://www.sap.com/products/technology-platform/datasphere.html) for the powerful data platform
- [Claude Desktop](https://claude.ai/desktop) and [Cursor IDE](https://cursor.sh/) for MCP client implementations

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/MarioDeFelipe/sap-datasphere-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/MarioDeFelipe/sap-datasphere-mcp/discussions)
- **Documentation**: [MCP Setup Guide](MCP_SETUP_GUIDE.md)

---

**Built with ❤️ for AI-powered SAP Datasphere operations**