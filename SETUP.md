# Setup Guide

This guide will help you set up the SAP Datasphere MCP Server from scratch.

## Prerequisites

- Python 3.8 or higher
- SAP Datasphere tenant access
- Administrator privileges in SAP Datasphere (to create OAuth clients)

## Step 1: SAP Datasphere OAuth Setup

### 1.1 Access SAP Datasphere Admin Console

1. Log into your SAP Datasphere tenant as an administrator
2. Navigate to **System** → **Administration** → **App Integration** → **OAuth Clients**

### 1.2 Create OAuth Client

1. Click **"Add"** or **"Create New OAuth Client"**
2. Configure the OAuth client:
   - **Name**: `MCP Server Client` (or any descriptive name)
   - **Description**: `OAuth client for MCP server integration`
   - **Purpose**: **Technical User** (important!)
   - **Grant Type**: **Client Credentials** (important!)
   - **Access Token Lifetime**: `720 hours` (30 days)

### 1.3 Configure Trusted Origins

Add these trusted origins for local development:
```
http://localhost:3000
http://localhost:8000
http://localhost:5000
http://127.0.0.1:3000
http://127.0.0.1:8000
http://127.0.0.1:5000
```

### 1.4 Save Credentials

After creating the OAuth client, **immediately save**:
- **Client ID** (starts with `sb-`)
- **Client Secret** (⚠️ only shown once!)
- **Authorization URL**
- **Token URL**

## Step 2: Install SAP Datasphere MCP Server

### 2.1 Clone Repository

```bash
git clone https://github.com/yourusername/sap-datasphere-mcp.git
cd sap-datasphere-mcp
```

### 2.2 Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2.3 Configure Credentials

#### Option A: Interactive Setup (Recommended)
```bash
python setup_credentials.py
```

#### Option B: Manual Setup
```bash
# Copy example configuration
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

Fill in your credentials:
```env
DATASPHERE_TENANT_URL=https://your-tenant-id.eu10.hcs.cloud.sap
OAUTH_CLIENT_ID=sb-your-client-id!b130936|client!b3944
OAUTH_CLIENT_SECRET=your-client-secret
OAUTH_TOKEN_URL=https://your-subdomain.authentication.eu20.hana.ondemand.com/oauth/token
```

## Step 3: Test Configuration

### 3.1 Quick Test
```bash
python quick_test.py
```

Expected output:
```
🚀 Quick OAuth Test
✅ OAuth token obtained!
```

### 3.2 Full Test
```bash
python examples/basic_usage.py
```

## Step 4: Run MCP Server

### 4.1 Start Server
```bash
python -m sap_datasphere_mcp
```

### 4.2 Test with MCP Inspector
```bash
npx @modelcontextprotocol/inspector python -m sap_datasphere_mcp
```

## Step 5: Integration with AI Clients

### 5.1 Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "sap-datasphere": {
      "command": "python",
      "args": ["-m", "sap_datasphere_mcp"],
      "cwd": "/path/to/sap-datasphere-mcp",
      "env": {
        "DATASPHERE_TENANT_URL": "https://your-tenant.eu10.hcs.cloud.sap",
        "OAUTH_CLIENT_ID": "your-client-id",
        "OAUTH_CLIENT_SECRET": "your-client-secret",
        "OAUTH_TOKEN_URL": "https://your-auth.authentication.eu20.hana.ondemand.com/oauth/token"
      }
    }
  }
}
```

### 5.2 Other MCP Clients

The server works with any MCP-compatible client. Refer to your client's documentation for configuration.

## Troubleshooting

### OAuth Issues

**Problem**: `OAuth authentication failed`
**Solution**: 
- Verify Client ID and Secret are correct
- Ensure OAuth client has "Technical User" purpose
- Check that "Client Credentials" grant type is selected

**Problem**: `404 errors on API endpoints`
**Solution**:
- This is expected initially - SAP Datasphere uses non-standard API paths
- Use the `discover_endpoints` tool to find working endpoints
- Check SAP Datasphere documentation for your tenant's API paths

### Connection Issues

**Problem**: `Connection timeout`
**Solution**:
- Check your internet connection
- Verify tenant URL is correct
- Ensure firewall allows outbound HTTPS connections

**Problem**: `SSL certificate errors`
**Solution**:
- Update your Python certificates
- Check corporate firewall/proxy settings

### Permission Issues

**Problem**: `403 Forbidden errors`
**Solution**:
- Verify OAuth client has necessary permissions
- Check if your user has access to the requested resources
- Contact SAP Datasphere administrator

## Getting Help

- 📖 [Documentation](README.md)
- 🐛 [Report Issues](https://github.com/yourusername/sap-datasphere-mcp/issues)
- 💬 [Discussions](https://github.com/yourusername/sap-datasphere-mcp/discussions)
- 📧 [Email Support](mailto:your.email@example.com)

## Next Steps

Once setup is complete:

1. **Explore Tools**: Use `list_spaces`, `list_catalog`, etc.
2. **Find API Endpoints**: Use `discover_endpoints` to find working APIs
3. **Integrate with AI**: Connect to Claude, Cursor, or other AI assistants
4. **Contribute**: Help improve the server by reporting issues or contributing code