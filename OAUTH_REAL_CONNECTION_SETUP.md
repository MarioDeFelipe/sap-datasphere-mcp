# SAP Datasphere OAuth 2.0 Real Connection Setup Guide

## Overview

This guide walks you through setting up **real** OAuth 2.0 connectivity to SAP Datasphere, replacing the default mock data mode with live data access.

## Prerequisites

Before you begin, ensure you have:

- ✅ SAP Datasphere tenant access with admin privileges
- ✅ Python 3.10+ installed
- ✅ Access to create Technical Users in SAP Datasphere
- ✅ Network connectivity to your SAP Datasphere tenant

---

## Step 1: Create OAuth 2.0 Application in SAP Datasphere

### 1.1 Access App Integration Settings

1. Log into your SAP Datasphere tenant: `https://your-tenant.eu10.hcs.cloud.sap`
2. Navigate to **System** → **Administration** → **App Integration**
3. Click on **OAuth Clients** tab

### 1.2 Create New OAuth Client

1. Click **Create** button
2. Fill in the following details:

   | Field | Value | Description |
   |-------|-------|-------------|
   | **Name** | `MCP Server Client` | Friendly name for identification |
   | **Purpose** | `AI-powered data access via MCP` | Description of use case |
   | **Grant Type** | `Client Credentials` | OAuth 2.0 flow type |
   | **Access Token Lifetime** | `3600` (1 hour) | Token expiration time in seconds |
   | **Refresh Token** | Enabled (if available) | Allows token refresh without re-auth |

3. **Scopes**: Select the following permissions based on your needs:
   - `DATASPHERE_DATA_READ` - Read access to data
   - `DATASPHERE_METADATA_READ` - Read metadata and schemas
   - `DATASPHERE_SPACE_READ` - Read space information
   - `DATASPHERE_CATALOG_READ` - Read catalog assets
   - `DATASPHERE_QUERY_EXECUTE` - Execute queries

4. Click **Save**

### 1.3 Copy OAuth Credentials

After creation, SAP Datasphere will display:

```
Client ID: sb-xxx-xxx-xxx!xxxx
Client Secret: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Token URL: https://your-tenant.authentication.eu10.hana.ondemand.com/oauth/token
```

**⚠️ IMPORTANT**: Copy these credentials immediately! The **Client Secret** will only be shown once.

---

## Step 2: Configure Environment Variables

### 2.1 Create `.env` File

Copy the example configuration file:

```bash
cp .env.example .env
```

### 2.2 Edit `.env` with Your Credentials

Open `.env` in a text editor and fill in your actual values:

```bash
# SAP Datasphere Connection
DATASPHERE_BASE_URL=https://f45fa9cc-f4b5-4126-ab73-b19b578fb17a.eu10.hcs.cloud.sap
DATASPHERE_TENANT_ID=f45fa9cc-f4b5-4126-ab73-b19b578fb17a

# OAuth 2.0 Credentials (from Step 1.3)
DATASPHERE_CLIENT_ID=sb-xxx-xxx-xxx!xxxx
DATASPHERE_CLIENT_SECRET=your-actual-client-secret-here
DATASPHERE_TOKEN_URL=https://f45fa9cc-f4b5-4126-ab73-b19b578fb17a.authentication.eu10.hana.ondemand.com/oauth/token

# Optional: OAuth Scope (leave empty to use all granted scopes)
DATASPHERE_SCOPE=

# Server Configuration
LOG_LEVEL=INFO
SERVER_PORT=8080

# CRITICAL: Set to false for real connection
USE_MOCK_DATA=false
```

### 2.3 Secure Your `.env` File

**Security Best Practices:**

```bash
# Set restrictive file permissions (Linux/Mac)
chmod 600 .env

# On Windows, use:
# Right-click .env → Properties → Security → Advanced
# Remove all users except your account

# Add .env to .gitignore to prevent accidental commits
echo ".env" >> .gitignore
```

**⚠️ NEVER commit `.env` to version control!**

---

## Step 3: Update MCP Server Configuration

The MCP server needs to be updated to load OAuth configuration from environment variables.

### 3.1 Verify Python Dependencies

Ensure you have the latest dependencies installed:

```bash
pip install -r requirements.txt
```

Required packages for OAuth:
- `python-dotenv>=1.0.0` - Environment variable loading
- `aiohttp>=3.9.1` - Async HTTP client
- `cryptography>=41.0.7` - Token encryption

### 3.2 Server Configuration

The server will automatically:
1. Load `.env` configuration on startup
2. Initialize OAuth handler with your credentials
3. Replace mock data calls with real API calls
4. Handle token refresh automatically

---

## Step 4: Test OAuth Connection

### 4.1 Test Script

Create a test script to verify OAuth connectivity:

```python
# test_oauth_connection.py
import asyncio
import os
from dotenv import load_dotenv
from auth.oauth_handler import create_oauth_handler
from auth.datasphere_auth_connector import DatasphereAuthConnector, DatasphereConfig

async def test_connection():
    """Test OAuth connection to SAP Datasphere"""

    # Load environment variables
    load_dotenv()

    # Create configuration
    config = DatasphereConfig(
        base_url=os.getenv('DATASPHERE_BASE_URL'),
        client_id=os.getenv('DATASPHERE_CLIENT_ID'),
        client_secret=os.getenv('DATASPHERE_CLIENT_SECRET'),
        token_url=os.getenv('DATASPHERE_TOKEN_URL'),
        tenant_id=os.getenv('DATASPHERE_TENANT_ID'),
        scope=os.getenv('DATASPHERE_SCOPE')
    )

    # Test connection
    async with DatasphereAuthConnector(config) as connector:
        # Test 1: Get OAuth token
        print("✓ Testing OAuth token acquisition...")
        token = await connector.oauth_handler.get_token()
        print(f"  Token acquired: {token.token_type} (expires in {token.expires_in}s)")

        # Test 2: Test API connection
        print("\n✓ Testing API connectivity...")
        connection_status = await connector.test_connection()

        if connection_status['connected']:
            print("  ✅ Connection successful!")
            print(f"  OAuth status: {connection_status['oauth_status']}")
        else:
            print("  ❌ Connection failed!")
            print(f"  Error: {connection_status.get('error')}")
            return False

        # Test 3: Fetch spaces
        print("\n✓ Testing space listing...")
        spaces = await connector.get_spaces()
        print(f"  Found {len(spaces)} spaces:")
        for space in spaces[:3]:  # Show first 3
            print(f"    - {space.get('id')}: {space.get('name')}")

        return True

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    exit(0 if success else 1)
```

### 4.2 Run Test

```bash
python test_oauth_connection.py
```

**Expected Output:**

```
✓ Testing OAuth token acquisition...
  Token acquired: Bearer (expires in 3600s)

✓ Testing API connectivity...
  ✅ Connection successful!
  OAuth status: {'has_token': True, 'token_expired': False, ...}

✓ Testing space listing...
  Found 5 spaces:
    - SAP_CONTENT: SAP Content
    - SALES_ANALYTICS: Sales Analytics
    - FINANCE_SPACE: Finance Space
```

---

## Step 5: Start MCP Server with Real Data

### 5.1 Start the Server

```bash
python sap_datasphere_mcp_server.py
```

### 5.2 Verify Real Connection

You should see logs indicating OAuth initialization:

```
INFO:auth.oauth_handler:OAuth handler initialized for token URL: https://...
INFO:auth.datasphere_auth_connector:Datasphere connector initialized with OAuth authentication
INFO:sap-datasphere-mcp:MCP Server started with REAL SAP Datasphere connection
INFO:sap-datasphere-mcp:OAuth token acquired successfully
```

### 5.3 Test Tools

Use the MCP server's new `test_connection` tool to verify:

```json
{
  "tool": "test_connection",
  "arguments": {}
}
```

Expected response:

```json
{
  "connected": true,
  "oauth_status": {
    "has_token": true,
    "token_expired": false,
    "time_until_expiry": 3540,
    "acquisitions": 1,
    "refreshes": 0
  },
  "message": "Connection successful"
}
```

---

## Step 6: Integration with AI Assistants

### 6.1 Claude Desktop Configuration

Update your `mcp.json`:

```json
{
  "mcpServers": {
    "sap-datasphere": {
      "command": "python",
      "args": ["sap_datasphere_mcp_server.py"],
      "cwd": "/path/to/sap-datasphere-mcp",
      "env": {
        "USE_MOCK_DATA": "false"
      }
    }
  }
}
```

### 6.2 Cursor IDE Configuration

Add to Cursor settings:

```json
{
  "mcp.servers": {
    "sap-datasphere": {
      "command": ["python", "sap_datasphere_mcp_server.py"],
      "env": {
        "USE_MOCK_DATA": "false"
      }
    }
  }
}
```

---

## Troubleshooting

### Issue 1: "Invalid client credentials" (401 Error)

**Cause**: Incorrect Client ID or Client Secret

**Solution**:
1. Verify credentials in `.env` match exactly what SAP Datasphere provided
2. Check for extra spaces or newlines
3. Regenerate OAuth client if credentials were lost

### Issue 2: "Token acquisition failed" (Network Error)

**Cause**: Network connectivity issues or incorrect Token URL

**Solution**:
1. Verify `DATASPHERE_TOKEN_URL` is correct
2. Check network connectivity: `curl https://your-tenant.authentication.eu10.hana.ondemand.com`
3. Verify no firewall blocking access
4. Check if proxy settings are needed

### Issue 3: "Insufficient permissions" (403 Error)

**Cause**: OAuth client doesn't have required scopes

**Solution**:
1. Go back to SAP Datasphere → App Integration → OAuth Clients
2. Edit your OAuth client
3. Add missing scopes (e.g., `DATASPHERE_DATA_READ`, `DATASPHERE_CATALOG_READ`)
4. Save and retry

### Issue 4: Mock Data Still Showing

**Cause**: `USE_MOCK_DATA` not set to `false`

**Solution**:
1. Verify `.env` has `USE_MOCK_DATA=false`
2. Restart the MCP server
3. Check server logs for "Mock data mode: False"

### Issue 5: Token Expired Errors

**Cause**: Token lifetime too short or not refreshing

**Solution**:
1. The OAuth handler automatically refreshes tokens 60 seconds before expiry
2. If issues persist, increase token lifetime in SAP Datasphere OAuth client settings
3. Check logs for token refresh errors

---

## Security Best Practices

### 1. Credential Management

✅ **DO:**
- Store credentials in `.env` file
- Use environment variables for all secrets
- Set restrictive file permissions on `.env`
- Use separate OAuth clients for dev/staging/production
- Rotate client secrets regularly

❌ **DON'T:**
- Hardcode credentials in source code
- Commit `.env` to git
- Share OAuth credentials in email/chat
- Use production credentials in development
- Reuse OAuth clients across projects

### 2. Token Security

✅ **DO:**
- Let the OAuth handler manage token lifecycle
- Use encrypted token storage (built-in)
- Implement token refresh logic (built-in)
- Monitor token acquisition metrics

❌ **DON'T:**
- Log access tokens
- Store tokens in plain text
- Bypass token expiration checks
- Share tokens between processes

### 3. Network Security

✅ **DO:**
- Use HTTPS for all API calls (enforced)
- Implement request timeouts (built-in)
- Use retry logic with exponential backoff (built-in)
- Monitor API call failures

❌ **DON'T:**
- Allow HTTP connections
- Ignore certificate validation errors
- Disable SSL/TLS verification
- Use insecure network connections

---

## OAuth Handler Features

The integrated OAuth handler provides:

### Automatic Token Management
- ✅ Acquires tokens on first request
- ✅ Refreshes tokens before expiration (60s buffer)
- ✅ Retries on transient failures (3 attempts, exponential backoff)
- ✅ Thread-safe token access

### Security Features
- ✅ Encrypted token storage in memory
- ✅ No tokens written to disk
- ✅ Secure credential handling
- ✅ Token lifecycle monitoring

### Health Monitoring
- ✅ Token acquisition count
- ✅ Token refresh count
- ✅ Time until expiry tracking
- ✅ Error logging and reporting

---

## Advanced Configuration

### Custom Token Lifetime

Edit your OAuth client in SAP Datasphere:

```
Access Token Lifetime: 7200  # 2 hours (max recommended)
```

### Custom Scopes

Specify exact scopes needed:

```bash
# In .env
DATASPHERE_SCOPE=DATASPHERE_DATA_READ DATASPHERE_CATALOG_READ
```

### Retry Configuration

Modify OAuth handler initialization:

```python
oauth_handler = OAuthHandler(
    client_id=client_id,
    client_secret=client_secret,
    token_url=token_url,
    max_retries=5,        # Default: 3
    retry_delay=2.0       # Default: 1.0 seconds
)
```

---

## Migration from Mock to Real Data

### Before Migration Checklist

- [ ] OAuth client created in SAP Datasphere
- [ ] `.env` file configured with real credentials
- [ ] `USE_MOCK_DATA=false` set in `.env`
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] OAuth connection tested successfully
- [ ] Network connectivity verified
- [ ] Scopes and permissions validated

### Migration Steps

1. **Backup Current Configuration**
   ```bash
   cp .env .env.mock  # Save mock config
   ```

2. **Update Environment**
   ```bash
   # Edit .env
   USE_MOCK_DATA=false
   ```

3. **Restart Server**
   ```bash
   python sap_datasphere_mcp_server.py
   ```

4. **Verify Connection**
   - Check logs for OAuth initialization
   - Run `test_connection` tool
   - Test a few basic tools (e.g., `list_spaces`)

5. **Monitor Performance**
   - Watch for API rate limits
   - Monitor token refresh behavior
   - Check error rates and retry logic

### Rollback to Mock Data

If issues occur:

```bash
# Edit .env
USE_MOCK_DATA=true

# Restart server
python sap_datasphere_mcp_server.py
```

---

## Next Steps

After successful OAuth integration:

1. **Configure Caching** - Reduce API calls with intelligent caching
2. **Enable Telemetry** - Monitor tool usage and performance
3. **Set Up Monitoring** - Track OAuth health and API errors
4. **Optimize Scopes** - Grant only necessary permissions
5. **Production Deployment** - Deploy to production environment

---

## Support Resources

- **GitHub Issues**: [Report OAuth issues](https://github.com/MarioDeFelipe/sap-datasphere-mcp/issues)
- **SAP Documentation**: [OAuth 2.0 Configuration](https://help.sap.com/docs/SAP_DATASPHERE)
- **MCP Server Guide**: [README.md](README.md)
- **Troubleshooting**: [TROUBLESHOOTING_CONNECTIVITY.md](TROUBLESHOOTING_CONNECTIVITY.md)

---

## Changelog

- **2025-01-XX**: Initial OAuth integration guide
- **2025-01-XX**: Added troubleshooting section
- **2025-01-XX**: Added security best practices

---

**Status**: ✅ OAuth integration ready for production use

**Next**: Integrate OAuth handler into main MCP server file
