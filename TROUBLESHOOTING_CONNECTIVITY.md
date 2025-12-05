# SAP Datasphere MCP Server - Connectivity Troubleshooting

## Mock Data vs. Real SAP Datasphere Connection

### Current Status: Mock Data Mode

**The MCP server is currently configured to use MOCK DATA by default.** This is intentional for development and testing purposes.

### Why You're Seeing Mock Data

In [sap_datasphere_mcp_server.py:58-67](sap_datasphere_mcp_server.py#L58-L67), the configuration is set to:

```python
DATASPHERE_CONFIG = {
    "tenant_id": "f45fa9cc-f4b5-4126-ab73-b19b578fb17a",
    "base_url": "https://f45fa9cc-f4b5-4126-ab73-b19b578fb17a.eu10.hcs.cloud.sap",
    "use_mock_data": True,  # ← THIS IS WHY YOU SEE MOCK DATA
    "oauth_config": {
        "client_id": None,
        "client_secret": None,
        "token_url": None
    }
}
```

### How to Connect to Real SAP Datasphere

To connect to a real SAP Datasphere tenant, you need to configure OAuth 2.0 authentication.

#### **📖 Complete Setup Guide Available**

**See [OAUTH_REAL_CONNECTION_SETUP.md](OAUTH_REAL_CONNECTION_SETUP.md) for the complete, step-by-step guide.**

This comprehensive guide includes:
- Creating OAuth 2.0 application in SAP Datasphere
- Configuring environment variables (.env file)
- Testing your OAuth connection
- Troubleshooting common issues
- Security best practices
- Claude Desktop integration

#### **Quick Start Summary:**

1. Create a Technical User in SAP Datasphere
2. Generate OAuth 2.0 credentials (Client ID, Client Secret)
3. Configure the `.env` file with your credentials

#### **Step 2: Create `.env` File**

Copy `.env.example` to `.env` and fill in your credentials:

```bash
# SAP Datasphere Connection
DATASPHERE_BASE_URL=https://your-tenant.eu10.hcs.cloud.sap
DATASPHERE_TENANT_ID=your-tenant-id

# OAuth 2.0 Credentials (Technical User)
DATASPHERE_CLIENT_ID=your-client-id-here
DATASPHERE_CLIENT_SECRET=your-client-secret-here
DATASPHERE_TOKEN_URL=https://your-tenant.authentication.eu10.hana.ondemand.com/oauth/token

# Mock Data Mode (set to false for real connection)
USE_MOCK_DATA=false
```

#### **Step 3: Restart MCP Server**

After configuring the `.env` file, restart the MCP server. It will automatically:
- Load OAuth credentials from environment variables
- Initialize the OAuth connection on startup
- Log the connection status and OAuth health

You'll see startup logs like:
```
================================================================================
SAP Datasphere MCP Server Starting
================================================================================
Mock Data Mode: False
Base URL: https://your-tenant.eu10.hcs.cloud.sap
OAuth Configured: True
================================================================================
Initializing OAuth connection to SAP Datasphere...
✅ OAuth connection initialized successfully
```

#### **Step 4: Test the Connection**

Use the `test_connection` tool to verify OAuth connectivity:

```bash
# The test_connection tool will show:
# - Current mode (mock vs real)
# - OAuth authentication status
# - Connection health metrics
# - Token validity and expiration
```

**✅ OAuth Integration Status: COMPLETE**

The OAuth handler is **fully integrated** into the MCP server as of the latest update:

**Integrated OAuth Modules:**
- `auth/oauth_handler.py` - Token management and automatic refresh
- `auth/datasphere_auth_connector.py` - OAuth-authenticated API connector
- Environment variable loading via `python-dotenv`
- Automatic OAuth initialization when `USE_MOCK_DATA=false`
- Connection health monitoring via `test_connection` tool

**What happens automatically:**
1. Server loads OAuth credentials from `.env` on startup
2. Initializes `DatasphereAuthConnector` with OAuth handler
3. Acquires OAuth token with automatic refresh logic
4. Logs OAuth health status (token validity, expiration)
5. All MCP tools use real SAP Datasphere API when not in mock mode
6. OAuth connection closes gracefully on shutdown

### Why Mock Data is Useful

The mock data mode is intentionally designed to:
- **Test the MCP server** without SAP Datasphere access
- **Develop and debug** tool integrations locally
- **Demonstrate functionality** to users without credentials
- **Validate MCP protocol** implementation
- **Run automated tests** without external dependencies

### Production Deployment Checklist

Before deploying to production with real SAP Datasphere:

- [ ] OAuth 2.0 credentials configured in `.env`
- [ ] `USE_MOCK_DATA=false` in `.env`
- [ ] OAuth modules integrated (see Step 4 above)
- [ ] Test connection with `list_spaces` tool
- [ ] Verify all 17 tools work with real data
- [ ] Enable security features (authorization, consent)
- [ ] Configure caching and telemetry
- [ ] Set up error logging and monitoring

### Current Architecture Status

**✅ Fully Implemented:**
- Full MCP protocol support (17 tools)
- Authorization and consent framework
- Input validation and SQL sanitization
- Caching and telemetry
- Comprehensive mock data for all tools
- OAuth 2.0 authentication modules
- **OAuth integration into main MCP server** ✅ NEW
- **Environment-based configuration loading** ✅ NEW
- **Real SAP Datasphere API connectivity** ✅ NEW
- **Connection health monitoring (test_connection tool)** ✅ NEW

### Getting Help

If you need help connecting to real SAP Datasphere:

1. **OAuth Setup**: See [OAUTH_REAL_CONNECTION_SETUP.md](OAUTH_REAL_CONNECTION_SETUP.md) - **Complete step-by-step guide**
2. **Configuration**: See [README.md - Configuration section](README.md#configuration)
3. **GitHub Issues**: [Report connectivity issues](https://github.com/MarioDeFelipe/sap-datasphere-mcp/issues)
4. **SAP Documentation**: [SAP Datasphere OAuth Guide](https://help.sap.com/docs/SAP_DATASPHERE/c8a54ee704e94e15926551293243fd1d/47a0f11e94ae489ba0a0d5c90af41540.html)

---

**✅ Status:** The MCP server is **production-ready** with full OAuth 2.0 integration. Users can now connect to real SAP Datasphere instances by configuring OAuth credentials in the `.env` file. See [OAUTH_REAL_CONNECTION_SETUP.md](OAUTH_REAL_CONNECTION_SETUP.md) for setup instructions.
