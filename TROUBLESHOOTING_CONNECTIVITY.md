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

To connect to a real SAP Datasphere tenant, you need to:

#### **Step 1: Set Up OAuth 2.0 Authentication**

Follow the [OAuth Setup Guide](docs/OAUTH_SETUP.md) to:
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

#### **Step 3: Update MCP Server Configuration**

Modify [sap_datasphere_mcp_server.py:58-67](sap_datasphere_mcp_server.py#L58-L67) to load from environment:

```python
import os
from dotenv import load_dotenv

load_dotenv()

DATASPHERE_CONFIG = {
    "tenant_id": os.getenv("DATASPHERE_TENANT_ID"),
    "base_url": os.getenv("DATASPHERE_BASE_URL"),
    "use_mock_data": os.getenv("USE_MOCK_DATA", "true").lower() == "true",
    "oauth_config": {
        "client_id": os.getenv("DATASPHERE_CLIENT_ID"),
        "client_secret": os.getenv("DATASPHERE_CLIENT_SECRET"),
        "token_url": os.getenv("DATASPHERE_TOKEN_URL")
    }
}
```

#### **Step 4: Integrate OAuth Handler**

Currently, the OAuth authentication modules exist but are **not integrated** into the main server:

**Existing OAuth Modules** (not currently used):
- `auth/oauth_handler.py` - Token management and refresh
- `auth/datasphere_auth_connector.py` - OAuth-authenticated API connector

**To integrate OAuth**, you would need to:

1. Import the OAuth connector:
```python
from auth.oauth_handler import OAuthHandler
from auth.datasphere_auth_connector import DataSphereAuthConnector
```

2. Initialize OAuth handler in the server startup:
```python
if not DATASPHERE_CONFIG["use_mock_data"]:
    oauth_handler = OAuthHandler(
        client_id=DATASPHERE_CONFIG["oauth_config"]["client_id"],
        client_secret=DATASPHERE_CONFIG["oauth_config"]["client_secret"],
        token_url=DATASPHERE_CONFIG["oauth_config"]["token_url"]
    )

    datasphere_connector = DataSphereAuthConnector(
        base_url=DATASPHERE_CONFIG["base_url"],
        oauth_handler=oauth_handler
    )
```

3. Replace mock data calls with real API calls:
```python
if DATASPHERE_CONFIG["use_mock_data"]:
    # Use mock data
    spaces = MOCK_DATA["spaces"]
else:
    # Use real API
    spaces = await datasphere_connector.get_spaces()
```

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

**✅ Implemented:**
- Full MCP protocol support (17 tools)
- Authorization and consent framework
- Input validation and SQL sanitization
- Caching and telemetry
- Comprehensive mock data for all tools
- OAuth 2.0 authentication modules

**⚠️ Not Yet Integrated:**
- OAuth authentication **into the main server**
- Real SAP Datasphere API calls
- Environment-based configuration loading
- Connection health monitoring with OAuth

### Getting Help

If you need help connecting to real SAP Datasphere:

1. **OAuth Setup**: See [docs/OAUTH_SETUP.md](docs/OAUTH_SETUP.md)
2. **Configuration**: See [README.md - Configuration section](README.md#configuration)
3. **GitHub Issues**: [Report connectivity issues](https://github.com/MarioDeFelipe/sap-datasphere-mcp/issues)
4. **SAP Documentation**: [SAP Datasphere OAuth Guide](https://help.sap.com/docs/SAP_DATASPHERE/c8a54ee704e94e15926551293243fd1d/47a0f11e94ae489ba0a0d5c90af41540.html)

---

**Note:** The MCP server is production-ready for the MCP protocol and security features, but requires integration work to connect to real SAP Datasphere instances. The OAuth modules are implemented but not yet wired into the tool handlers.
