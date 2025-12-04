# SAP Datasphere MCP Server - Developer Guide

This guide covers development setup and workflows for the SAP Datasphere MCP server.

## Prerequisites

- [Python 3.10+](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) - Python package manager
- [Git](https://git-scm.com/)
- SAP Datasphere account with Technical User configured
- OAuth 2.0 application setup for the Technical User


### SAP Datasphere Technical User Setup

**Step 1: Create Technical User in SAP Datasphere**
1. Log into SAP Datasphere as an administrator
2. Navigate to System → Security → Users
3. Create a new Technical User with appropriate permissions:
   - Space access permissions for metadata discovery
   - Data access permissions for querying assets
   - API access permissions for consumption APIs

**Step 2: Configure OAuth Application**
1. In SAP Datasphere, go to System → Security → App Integration
2. Create a new OAuth 2.0 Client for the Technical User
3. Configure the OAuth application with:
   - Grant Type: Client Credentials
   - Scopes: Required API access scopes
   - Redirect URI: Not required for client credentials flow

**Step 3: Configure MCP Server Credentials**
Create `config/datasphere_config.json` with the Technical User's OAuth credentials:

```json
{
  "base_url": "https://your-tenant.eu20.hcs.cloud.sap",
  "client_id": "technical-user-oauth-client-id",
  "client_secret": "technical-user-oauth-client-secret",
  "token_url": "https://your-tenant.authentication.eu20.hana.ondemand.com/oauth/token"
}
```

## Development Setup

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/MarioDeFelipe/sap-datasphere-mcp.git
cd sap-datasphere-mcp

# Create virtual environment and install dependencies
uv venv
uv sync --all-groups

# Install pre-commit hooks
pre-commit install
```

### 2. Configuration

Create a `config/datasphere_config.json` file with your SAP Datasphere credentials:

```json
{
  "base_url": "https://your-tenant.eu20.hcs.cloud.sap",
  "client_id": "your-oauth-client-id",
  "client_secret": "your-oauth-client-secret",
  "token_url": "https://your-tenant.authentication.eu20.hana.ondemand.com/oauth/token"
}
```

## Development Workflow

### 3. Running the MCP Server

```bash
# Start the MCP server for development
python sap_datasphere_mcp_server.py
```

### 4. Code Structure

The main components of the MCP server:

- `sap_datasphere_mcp_server.py` - Main MCP server implementation
- `enhanced_datasphere_connector.py` - SAP Datasphere OAuth connector

- `enhanced_metadata_extractor.py` - Metadata extraction utilities
- `config/` - Configuration files
- `tests/` - Unit tests

### 5. Making Changes

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Make your changes to the MCP server code
# Edit sap_datasphere_mcp_server.py or related files

# Run tests
python test_mcp_server.py

# Commit your changes
git add .
git commit -m "feat: add new MCP tool for asset discovery"

# Push to your fork
git push origin feature/your-feature-name
```

## Testing

### Testing with MCP Inspector

Use the [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) to test your server:

```bash
# Install and run MCP Inspector
npx @modelcontextprotocol/inspector python sap_datasphere_mcp_server.py
```

### Testing with AI Clients

#### Claude Desktop Integration

Add to your Claude Desktop `mcp.json` configuration:

```json
{
  "mcpServers": {
    "sap-datasphere": {
      "command": "python",
      "args": ["sap_datasphere_mcp_server.py"],
      "cwd": "/path/to/sap-datasphere-mcp",
      "env": {
        "SAP_CLIENT_ID": "your_oauth_client_id",
        "SAP_CLIENT_SECRET": "your_oauth_client_secret"
      }
    }
  }
}
```

#### Cursor IDE Integration

Add to your Cursor settings:

```json
{
  "mcp.servers": {
    "sap-datasphere": {
      "command": ["python", "sap_datasphere_mcp_server.py"],
      "env": {
        "SAP_CLIENT_ID": "your_oauth_client_id",
        "SAP_CLIENT_SECRET": "your_oauth_client_secret"
      }
    }
  }
}
```

### Unit Tests

Run the test suite:

```bash
# Run all tests
python test_mcp_server.py

# Run with coverage
uv run --frozen pytest --cov --cov-branch --cov-report=term-missing
```

## MCP Server Architecture

### Core Components

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   AI Assistant  │◄──►│   MCP Server     │◄──►│  SAP Datasphere │
│ (Claude, Cursor)│    │                  │    │   (OAuth 2.0)   │
└─────────────────┘    │ • Metadata Ops   │    └─────────────────┘
                       │ • Asset Discovery│    
                       │ • Data Queries   │    
                       │ • Space Explorer │    
                       └──────────────────┘
```

### Available MCP Tools

The server provides these tools for AI assistants:

- `discover_spaces` - List all accessible SAP Datasphere spaces
- `get_space_assets` - Get assets within a specific space
- `get_asset_details` - Retrieve detailed asset information
- `query_asset_data` - Execute OData queries on assets
- `search_metadata` - Search across metadata with filters
- `get_connection_status` - Check SAP Datasphere connectivity

## Contributing

### Code Quality

- Follow PEP 8 style guidelines
- Add type hints to all functions
- Include docstrings for all public methods
- Write unit tests for new functionality

### Pre-commit Hooks

The project uses pre-commit hooks for code quality:

```bash
# Run pre-commit on all files
pre-commit run --all-files

# Run specific hooks
pre-commit run ruff
pre-commit run mypy
```

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure all tests pass
5. Submit a pull request with clear description

## Troubleshooting

### Common Issues

**Technical User Authentication Errors**
- Verify the Technical User exists in SAP Datasphere
- Check that the Technical User has appropriate permissions for spaces and assets
- Ensure the OAuth application is properly configured for the Technical User
- Verify the client credentials (client_id, client_secret) are correct
- Check that the token URL matches your tenant's authentication endpoint

**Permission Denied Errors**
- Verify the Technical User has access to the required SAP Datasphere spaces
- Check that the Technical User has data access permissions for querying assets
- Ensure the Technical User has API consumption permissions
- Review space-level security settings in SAP Datasphere

**Connection Timeouts**
- Check network connectivity to SAP Datasphere
- Verify firewall settings allow HTTPS traffic
- Consider increasing timeout values in the connector

**MCP Client Integration Issues**
- Verify the MCP server starts without errors
- Check that the client configuration points to the correct server path
- Review client logs for connection errors

### Debug Mode

Enable debug logging:

```bash
# Set environment variable for verbose logging
export MCP_LOG_LEVEL=DEBUG
python sap_datasphere_mcp_server.py
```

### Getting Help

- Check the [MCP Protocol Documentation](https://modelcontextprotocol.io/)
- Review SAP Datasphere API documentation
- Open an issue on GitHub for bugs or feature requests