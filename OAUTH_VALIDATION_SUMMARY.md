# OAuth Validation Summary - SAP Datasphere MCP Server

## Test Date
2025-01-05

## Environment
- **Tenant**: ailien-test (eu20 region)
- **Base URL**: https://ailien-test.eu20.hcs.cloud.sap
- **Token URL**: https://ailien-test.authentication.eu20.hana.ondemand.com/oauth/token

## Tested Credentials

### 1. kirotechnical1 (Technical User)
- **Client ID**: `sb-6a8a284c-9845-410c-8f36-ce7e637587b4!b130936|client!b3944`
- **Grant Type**: SAML2.0 Bearer ❌ (incompatible with Client Credentials)
- **Result**: 401 Unauthorized - "Unauthorized grant type"

### 2. KIROUSEROAUTO (Pure API User) ✅
- **Client ID**: `sb-60cb266e-ad9d-49f7-9967-b53b8286a259!b130936|client!b3944`
- **Grant Type**: Client Credentials ✅
- **Token Acquisition**: SUCCESS ✅
- **Token Lifetime**: 86,399 seconds (~24 hours)
- **Scopes**:
  - `approuter-sac-saceu20!t3944.sap.fpa.user`
  - `uaa.resource`
  - `dmi-api-proxy-sac-saceu20!t3944.apiaccess`

## OAuth Token Analysis

### JWT Payload (KIROUSEROAUTO)
```json
{
  "grant_type": "client_credentials",
  "scope": [
    "approuter-sac-saceu20!t3944.sap.fpa.user",
    "uaa.resource",
    "dmi-api-proxy-sac-saceu20!t3944.apiaccess"
  ],
  "aud": [
    "approuter-sac-saceu20!t3944.sap.fpa",
    "dmi-api-proxy-sac-saceu20!t3944",
    "uaa"
  ],
  "zdn": "ailien-test",
  "subaccountid": "a0755db1-8717-4ed3-82a6-61936d63cc2c"
}
```

**Analysis**: Token has correct scopes for DMI API proxy and SAP FPA access.

## API Endpoint Testing

### Tested Endpoints

| Endpoint | Auth Method | Status | Response |
|----------|-------------|--------|----------|
| `/deepsea/repository/SAP_CONTENT/objects` | Bearer only | 200 | HTML login page |
| `/deepsea/repository/SAP_CONTENT/objects` | Bearer + User-Agent | 200 | HTML login page |
| `/deepsea/repository/SAP_CONTENT/objects` | Bearer + x-sap-sac-custom-auth | 401 | Unauthorized |
| `/deepsea/repository/SAP_CONTENT/objects` | Bearer + x-csrf-token | 200 | HTML login page |
| `/api/v1/catalog/Assets` | Bearer + no redirects | 404 | Not Found |
| `/api/v1/dwc/consumption/relational/dataSharing/v1/spaces` | Bearer | 403 | Forbidden (JSON) |
| `/api/v1/dwc/spaces` | Bearer | 401 | Unauthorized |

### Headers Tested
```python
# Standard
{
    'Authorization': 'Bearer {token}',
    'Accept': 'application/json'
}

# With User-Agent (from working environment)
{
    'Authorization': 'Bearer {token}',
    'Accept': 'application/json',
    'User-Agent': 'Datasphere-Metadata-Sync/2.0'
}

# With SAP custom auth
{
    'Authorization': 'Bearer {token}',
    'x-sap-sac-custom-auth': 'true'
}

# With CSRF token
{
    'Authorization': 'Bearer {token}',
    'x-csrf-token': 'fetch'
}
```

**All resulted in HTML login page or 401/403 errors.**

## Findings

### ✅ Working
1. OAuth 2.0 token acquisition (Client Credentials)
2. Token validity and expiration handling
3. Token has appropriate scopes
4. MCP server OAuth integration complete

### ❌ Not Working
1. API endpoints return HTML login pages instead of JSON
2. DeepSea Repository API returns 401/200 (with HTML)
3. Catalog API returns 404 (endpoint not found)
4. DWC Consumption API returns 403 (forbidden)

## Root Cause Analysis

### Hypothesis 1: Missing Permissions ⭐ (Most Likely)
**Evidence:**
- Valid OAuth token with correct scopes
- APIs respond but return authentication pages
- Similar to symptoms when user lacks space membership

**Resolution:**
- Assign KIROUSEROAUTO to at least one Space as Space Administrator
- Verify user has DW Integrator or DW Space Administrator role
- Check if user has API access enabled in SAP Datasphere

### Hypothesis 2: Different API URL Pattern
**Evidence:**
- Working environment mentioned `datasphere_connector.py` works successfully
- Same OAuth credentials (KIROUSEROAUTO)
- Possible that working code uses different endpoint URLs

**Resolution:**
- Share working `datasphere_connector.py` code
- Compare exact API endpoint URLs used
- Check if additional URL path prefix needed

### Hypothesis 3: Session/Cookie-Based Auth Required
**Evidence:**
- HTML login pages suggest session-based authentication
- Response sets cookies: `fragmentAfterLogin`, `locationAfterLogin`
- OAuth token alone might not be sufficient

**Resolution:**
- Check if working code establishes a session first
- May need to authenticate UI session before API access
- Possible app router authentication flow needed

## Comparison with Working Environment

### Confirmed Working Setup
- **Method**: OAuth 2.0 Client Credentials ✅
- **Credentials**: KIROUSEROAUTO (same as tested) ✅
- **Base URL**: https://ailien-test.eu20.hcs.cloud.sap ✅
- **Token URL**: https://ailien-test.authentication.eu20.hana.ondemand.com/oauth/token ✅
- **Tools**: Python scripts (`datasphere_connector.py`), Web Dashboard (localhost:8001)
- **Required Headers**: Authorization (Bearer), Accept (json), User-Agent (Datasphere-Metadata-Sync/2.0)
- **Status**: Fully operational

### Key Differences to Investigate
1. **Exact API endpoint URLs** used by working `datasphere_connector.py`
2. **Additional initialization** or setup steps
3. **Session management** or cookie handling
4. **User permissions/roles** in working vs test environment

## Next Steps

### Immediate Actions
1. **Get working code**: Share `datasphere_connector.py` from working environment
2. **Compare API URLs**: Check exact endpoints that work
3. **Check permissions**: Verify KIROUSEROAUTO has:
   - Role: DW Integrator or DW Space Administrator
   - Space membership in at least one space
   - API access enabled

### Testing Checklist
- [ ] Confirm user roles in SAP Datasphere
- [ ] Confirm space membership
- [ ] Compare working vs test API endpoint URLs
- [ ] Test with exact headers from working environment
- [ ] Check if session establishment needed before API calls

## MCP Server Status

### ✅ Ready Components
- OAuth handler (token acquisition, refresh, expiration)
- OAuth integration in main server
- Environment variable configuration
- Test connection tool
- Graceful error handling

### ⏳ Pending
- Successful API connection to SAP Datasphere
- User permissions configuration
- Correct API endpoint identification

**Once permissions/endpoints are resolved, the MCP server will work immediately - all OAuth infrastructure is in place.**

## Test Scripts Available

1. `test_oauth_connection.py` - OAuth token validation
2. `test_real_api.py` - Multiple endpoint testing
3. `test_deepsea_detailed.py` - DeepSea API with various auth strategies
4. `test_with_user_agent.py` - Test with User-Agent header from working env
5. `decode_jwt.py` - JWT token payload inspection

All scripts confirm OAuth is working but API access is blocked.
