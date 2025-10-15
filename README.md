# SAP Datasphere MCP Server

A Model Context Protocol (MCP) server that provides AI assistants with seamless access to SAP Datasphere APIs, enabling intelligent data exploration, catalog browsing, and space management.

## Features

- 🔐 **OAuth 2.0 Authentication** - Secure client credentials flow
- 🏢 **Space Management** - List and explore Datasphere spaces
- 📊 **Catalog Access** - Browse data models, tables, and views
- 🔗 **Connection Management** - Manage data source connections
- 🧠 **AI-Friendly** - Structured responses optimized for AI consumption
- 🛡️ **Enterprise Ready** - Built for production SAP environments

## Quick Start

### Prerequisites

- Python 3.8+
- SAP Datasphere tenant access
- OAuth client credentials (Client ID & Secret)

### Installation

#### Option 1: Install from PyPI (Recommended)
```bash
pip install sap-datasphere-mcp
```

#### Option 2: Install from Source
```bash
# Clone the repository
git clone https://github.com/MarioDeFelipe/sap-datasphere-mcp.git
cd sap-datasphere-mcp

# Install dependencies
pip install -r requirements.txt
```

#### Configure Credentials
```bash
# Interactive setup (recommended)
python -m sap_datasphere_mcp.setup

# Or manually create .env file
cp .env.example .env
# Edit .env with your OAuth credentials
```

### Configuration

Create a `.env` file with your SAP Datasphere credentials:

```env
DATASPHERE_TENANT_URL=https://your-tenant.eu10.hcs.cloud.sap
OAUTH_CLIENT_ID=your-client-id
OAUTH_CLIENT_SECRET=your-client-secret
OAUTH_TOKEN_URL=https://your-auth.authentication.eu20.hana.ondemand.com/oauth/token
```

### Usage

```bash
# Run the MCP server
python -m sap_datasphere_mcp

# Test with MCP Inspector
npx @modelcontextprotocol/inspector python -m sap_datasphere_mcp
```

## MCP Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `list_spaces` | List all available Datasphere spaces | None |
| `get_space_info` | Get detailed information about a space | `space_id` |
| `list_catalog` | Browse the data catalog | `space_id` (optional) |
| `get_table_info` | Get table schema and metadata | `space_id`, `table_name` |
| `list_connections` | List data source connections | `space_id` (optional) |
| `test_connection` | Test OAuth connectivity | None |

## Architecture

```
sap-datasphere-mcp/
├── sap_datasphere_mcp/
│   ├── __init__.py
│   ├── server.py          # Main MCP server
│   ├── auth.py           # OAuth authentication
│   ├── client.py         # Datasphere API client
│   └── models.py         # Data models
├── tests/
├── examples/
├── requirements.txt
└── README.md
```

## Development

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black .
ruff check --fix .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- 📖 [Documentation](docs/)
- 🐛 [Issues](https://github.com/yourusername/sap-datasphere-mcp/issues)
- 💬 [Discussions](https://github.com/yourusername/sap-datasphere-mcp/discussions)