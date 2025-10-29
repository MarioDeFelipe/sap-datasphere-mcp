# OAuth 2.0 Setup Guide for SAP Datasphere MCP Server

This guide walks you through setting up OAuth 2.0 authentication for the SAP Datasphere MCP Server using a Technical User.

---

## 📋 Prerequisites

- SAP Datasphere account with administrative access
- Python 3.10 or higher installed
- Access to create OAuth clients in SAP Datasphere

---

## 🔐 Step 1: Create Technical User in SAP Datasphere

### 1.1 Navigate to App Integration

1. Log into your SAP Datasphere tenant
2. Click the **System** menu (☰) in the top-left
3. Select **Administration** → **App Integration**

### 1.2 Create OAuth Client

1. Click **Add a New OAuth Client**
2. Fill in the following details:

   **OAuth Client Name:**
   ```
   MCP Server Technical User
   ```

   **Purpose:**
   ```
   Model Context Protocol server for AI assistant integration
   ```

   **OAuth Client Type:**
   - Select **"Open Authentication 2.0"**
   - Select **"Client Credentials"** grant type

   **Authorization Scope:**
   - ✅ Enable **"Read"** access
   - ✅ Enable **"Write"** access (if you need query execution)
   - ✅ Enable **"Manage"** access (if you need administrative operations)

3. Click **Create**

### 1.3 Save OAuth Credentials

After creation, SAP Datasphere will display:

- **OAuth Client ID** (e.g., `sb-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx!xxxxx`)
- **Client Secret** (e.g., `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)

⚠️ **IMPORTANT:**
- Copy these credentials immediately
- The Client Secret is only shown once
- Store them securely (you'll need them in Step 2)

### 1.4 Note Your Token URL

The token URL follows this pattern:
```
https://<tenant-id>.authentication.<region>.hana.ondemand.com/oauth/token
```

**Example:**
```
https://f45fa9cc-f4b5-4126-ab73-b19b578fb17a.authentication.eu10.hana.ondemand.com/oauth/token
```

**How to find your token URL:**
1. Look at your Datasphere URL: `https://<tenant-id>.<region>.hcs.cloud.sap`
2. Extract `<tenant-id>` and `<region>`
3. Build token URL: `https://<tenant-id>.authentication.<region>.hana.ondemand.com/oauth/token`

---

## ⚙️ Step 2: Configure MCP Server

### 2.1 Create `.env` File

Navigate to your MCP server directory and create a `.env` file:

```bash
cd sap-datasphere-mcp
cp .env.example .env
```

### 2.2 Edit `.env` File

Open `.env` in your text editor and paste your credentials:

```bash
# SAP Datasphere Connection
DATASPHERE_BASE_URL=https://your-tenant.eu10.hcs.cloud.sap
DATASPHERE_TENANT_ID=your-tenant-id

# OAuth 2.0 Credentials (Technical User)
DATASPHERE_CLIENT_ID=sb-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx!xxxxx
DATASPHERE_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DATASPHERE_TOKEN_URL=https://your-tenant.authentication.eu10.hana.ondemand.com/oauth/token

# Optional: OAuth Scope (leave empty for default)
DATASPHERE_SCOPE=

# Server Configuration
LOG_LEVEL=INFO
SERVER_PORT=8080

# Development Mode (set to false for production)
USE_MOCK_DATA=false
```

### 2.3 Replace Placeholder Values

Replace the following placeholders with your actual values:

| Placeholder | Replace With | Example |
|-------------|--------------|---------|
| `your-tenant.eu10.hcs.cloud.sap` | Your Datasphere URL | `f45fa9cc-f4b5-4126-ab73-b19b578fb17a.eu10.hcs.cloud.sap` |
| `your-tenant-id` | Your tenant identifier | `f45fa9cc-f4b5-4126-ab73-b19b578fb17a` |
| `sb-xxx...` | OAuth Client ID from Step 1.3 | `sb-12345678-xxxx-xxxx-xxxx-xxxxxxxxxxxx!b12345` |
| `xxxx...` | Client Secret from Step 1.3 | `aBcDeFgHiJkLmNoPqRsTuVwXyZ123456` |
| `your-tenant.authentication...` | Token URL from Step 1.4 | `f45fa9cc-f4b5-4126-ab73-b19b578fb17a.authentication.eu10.hana.ondemand.com/oauth/token` |

### 2.4 Verify Configuration

**Security Checklist:**
- [ ] `.env` file is in `.gitignore` (already configured)
- [ ] Never commit `.env` to version control
- [ ] Client Secret is kept private
- [ ] File permissions are restricted: `chmod 600 .env` (Linux/Mac)

---

## 🧪 Step 3: Test OAuth Connection

### 3.1 Install Dependencies

```bash
pip install -r requirements.txt
```

### 3.2 Test Configuration

Run the configuration validator:

```bash
python -c "from config import get_settings; settings = get_settings(); print('✅ Configuration valid!')"
```

**Expected output:**
```
2025-10-29 14:00:00 - config.settings - INFO - Configuration loaded successfully
✅ Configuration valid!
```

### 3.3 Test OAuth Token Acquisition

Create a simple test script to verify OAuth works:

```bash
python -c "
import asyncio
from auth.oauth_handler import create_oauth_handler
from config import get_settings

async def test():
    settings = get_settings()
    handler = await create_oauth_handler(
        client_id=settings.datasphere_client_id,
        client_secret=settings.datasphere_client_secret,
        token_url=settings.datasphere_token_url
    )
    print('✅ OAuth token acquired successfully!')
    print(f'Token expires in: {handler._token.expires_in} seconds')

asyncio.run(test())
"
```

**Expected output:**
```
2025-10-29 14:00:00 - auth.oauth_handler - INFO - OAuth handler initialized for token URL: https://...
2025-10-29 14:00:00 - auth.oauth_handler - INFO - Access token acquired successfully (expires in 3600s)
✅ OAuth token acquired successfully!
Token expires in: 3600 seconds
```

### 3.4 Test API Connection

Test the full Datasphere connector:

```bash
python -c "
import asyncio
from auth.datasphere_auth_connector import DatasphereAuthConnector, DatasphereConfig
from config import get_settings

async def test():
    settings = get_settings()
    config = DatasphereConfig(**settings.get_datasphere_config())

    async with DatasphereAuthConnector(config) as connector:
        status = await connector.test_connection()
        if status['connected']:
            print('✅ Successfully connected to SAP Datasphere!')
            print(f'OAuth Status: {status[\"oauth_status\"][\"has_token\"]}')
        else:
            print(f'❌ Connection failed: {status[\"error\"]}')

asyncio.run(test())
"
```

---

## 🚀 Step 4: Start MCP Server

### 4.1 Start the Server

```bash
python start_mcp_server.py
```

**Expected output:**
```
2025-10-29 14:00:00 - __main__ - INFO - Starting SAP Datasphere MCP Server
2025-10-29 14:00:00 - auth.oauth_handler - INFO - OAuth handler initialized
2025-10-29 14:00:00 - auth.oauth_handler - INFO - Access token acquired successfully
2025-10-29 14:00:00 - __main__ - INFO - MCP Server initialized successfully
2025-10-29 14:00:00 - __main__ - INFO - Waiting for MCP client connections...
```

### 4.2 Configure Claude Desktop

Add to your Claude Desktop `claude_desktop_config.json`:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "sap-datasphere": {
      "command": "python",
      "args": ["start_mcp_server.py"],
      "cwd": "/absolute/path/to/sap-datasphere-mcp"
    }
  }
}
```

⚠️ **Important:**
- Use absolute path for `cwd`
- The `.env` file must be in the `cwd` directory
- Restart Claude Desktop after configuration

### 4.3 Verify in Claude Desktop

1. Restart Claude Desktop
2. Look for the 🔌 icon (MCP tools available)
3. Click it to see available tools
4. You should see:
   - `list_spaces`
   - `get_space_info`
   - `search_tables`
   - `get_table_schema`
   - etc.

---

## 🔧 Troubleshooting

### Error: "Configuration validation failed"

**Problem:** Missing or invalid environment variables

**Solution:**
```bash
# Check which variables are missing
python -c "from config import get_settings; get_settings()"

# Verify .env file exists and has correct format
cat .env
```

### Error: "Token acquisition failed: HTTP 401"

**Problem:** Invalid client credentials

**Solutions:**
1. Verify Client ID is correct (copy-paste from SAP Datasphere)
2. Verify Client Secret is correct
3. Check if OAuth client is still active in SAP Datasphere
4. Ensure no extra spaces in `.env` file values

### Error: "Token acquisition failed: HTTP 404"

**Problem:** Incorrect token URL

**Solutions:**
1. Verify tenant ID in token URL matches your Datasphere URL
2. Verify region (e.g., `eu10`, `us10`) matches
3. Check URL format: `https://<tenant>.authentication.<region>.hana.ondemand.com/oauth/token`

### Error: "Network error during token acquisition"

**Problem:** Network connectivity or firewall

**Solutions:**
1. Check internet connection
2. Verify firewall allows HTTPS to `*.hana.ondemand.com`
3. Check proxy settings if behind corporate firewall
4. Try accessing token URL in browser

### Token Expires Too Quickly

**Problem:** Need longer token lifetime

**Solution:**
1. In SAP Datasphere, edit OAuth client
2. Increase "Token Validity" duration
3. Note: Tokens auto-refresh 60 seconds before expiration

---

## 🔒 Security Best Practices

### DO ✅

- ✅ Store credentials in `.env` file
- ✅ Add `.env` to `.gitignore`
- ✅ Use environment variables in production
- ✅ Rotate Client Secret periodically
- ✅ Use different OAuth clients for dev/prod
- ✅ Monitor OAuth client usage in SAP Datasphere
- ✅ Set appropriate scopes (least privilege)

### DON'T ❌

- ❌ Commit `.env` file to Git
- ❌ Share Client Secret via email/chat
- ❌ Use production credentials in development
- ❌ Store credentials in command-line arguments
- ❌ Log credentials in application logs
- ❌ Hard-code credentials in source code

---

## 📚 Additional Resources

- [SAP Datasphere OAuth Documentation](https://help.sap.com/docs/SAP_DATASPHERE/9f804b8efa8043539289f42f372c4862/df7bbca2b73f4418881eeca39b9e0a3d.html)
- [OAuth 2.0 Client Credentials Flow](https://datatracker.ietf.org/doc/html/rfc6749#section-4.4)
- [MCP Protocol Specification](https://modelcontextprotocol.io/specification/2025-03-26)
- [Project Implementation Plan](../MCP_IMPROVEMENTS_PLAN.md)

---

## 🆘 Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Review logs in `mcp_server.log`
3. Verify configuration with test scripts
4. Open an issue on [GitHub](https://github.com/MarioDeFelipe/sap-datasphere-mcp/issues)

---

**Last Updated:** 2025-10-29
**Version:** 1.0.0
**Status:** Production Ready
