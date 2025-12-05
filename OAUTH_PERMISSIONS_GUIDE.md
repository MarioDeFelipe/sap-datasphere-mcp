# SAP Datasphere OAuth Permissions Setup Guide

## Current Status

### ✅ **Working:**
- OAuth 2.0 token acquisition using Client Credentials grant
- Token has 24-hour validity
- Token includes scopes:
  - `approuter-sac-saceu20!t3944.sap.fpa.user`
  - `uaa.resource`
  - `dmi-api-proxy-sac-saceu20!t3944.apiaccess`

### ⚠️ **Issue:**
API endpoints return **401 Unauthorized** or redirect to login page despite valid OAuth token.

## Root Cause

The Technical User `kirotechnical1` has valid OAuth credentials but **lacks API access permissions** in SAP Datasphere.

## Required Permissions

To access SAP Datasphere APIs (DeepSea Repository, Catalog, DWC), the Technical User needs:

### 1. **SAP Datasphere Roles**

Go to **SAP Datasphere → Security → Users → kirotechnical1**

Assign one of these roles:
- **DW Space Administrator** - Full access to space data and APIs
- **DW Integrator** - API access for data integration
- **DW Modeler** - Read access to data models and catalog

**Recommended for MCP server:** `DW Integrator`

### 2. **Space Membership**

The Technical User must be assigned to at least one Space:

1. Go to **SAP Datasphere → Space Management**
2. Select a space (e.g., `SAP_CONTENT`, `SHARED`, or your custom space)
3. Go to **Members** tab
4. Click **Add Members**
5. Add `kirotechnical1` with role: **Space Administrator** or **Space Viewer**

**Note:** Without space membership, APIs will return 401/403 errors.

### 3. **OAuth Client Scopes** (if configurable)

When creating the OAuth 2.0 application in **App Integration**:

1. Go to **System → App Integration**
2. Select your OAuth client
3. Ensure these permissions/scopes are enabled (if available):
   - API Access
   - Repository Read
   - Catalog Access
   - Data Access

**Note:** Some SAP Datasphere versions don't expose scope configuration - permissions are inherited from user roles.

## Verification Steps

After assigning permissions, verify access:

### 1. **Check User Roles**
```bash
# In SAP Datasphere UI
Security → Users → kirotechnical1 → View Assigned Roles
```

Expected roles:
- `DW Integrator` or `DW Space Administrator`
- Space membership in at least one space

### 2. **Test OAuth Connection**
```bash
python test_oauth_connection.py
```

Expected output:
```
[OAuth Health Status]
   Has Token: True
   Token Valid: True
   Expires In: 86399 seconds

[SUCCESS] OAuth connection initialized successfully
```

### 3. **Test DeepSea API**
```bash
python test_deepsea_detailed.py
```

Expected response (after permissions fixed):
```
[Test] Bearer token only
   URL: https://ailien-test.eu20.hcs.cloud.sap/deepsea/repository/SAP_CONTENT/objects
   Status: 200
   Content-Type: application/json
   [SUCCESS] Got JSON response!
```

## Common Issues

### Issue 1: "401 Unauthorized"
**Cause:** Technical User not assigned to any space
**Fix:** Add user to space members

### Issue 2: "403 Forbidden"
**Cause:** Technical User lacks required role
**Fix:** Assign `DW Integrator` or `DW Space Administrator` role

### Issue 3: "HTML login page instead of JSON"
**Cause:** OAuth token not being accepted (permissions issue)
**Fix:** Verify space membership and role assignment

### Issue 4: "Scopes missing in token"
**Cause:** OAuth client not configured correctly
**Fix:** Re-create OAuth client with correct template (Technical User with API Access)

## Comparison with Working Environment

If you have another environment where this works, compare:

1. **User Roles:**
   ```
   Working env → Security → Users → [working-user] → Roles
   vs.
   Test env → Security → Users → kirotechnical1 → Roles
   ```

2. **Space Membership:**
   ```
   Working env → Space → Members (check which spaces the user is in)
   vs.
   Test env → Check kirotechnical1 space membership
   ```

3. **OAuth Client Configuration:**
   ```
   Working env → System → App Integration → [OAuth client] → Settings
   vs.
   Test env → System → App Integration → [kirotechnical1 client] → Settings
   ```

## Next Steps

1. **Assign Roles:**
   - Go to SAP Datasphere → Security → Users
   - Find `kirotechnical1`
   - Assign role: `DW Integrator`

2. **Add Space Membership:**
   - Go to Space Management → Select Space (e.g., `SAP_CONTENT`)
   - Members → Add `kirotechnical1` as **Space Administrator**

3. **Re-test:**
   ```bash
   python test_deepsea_detailed.py
   ```

4. **If still failing:**
   - Compare with working environment user permissions
   - Check SAP Datasphere audit logs for authorization errors
   - Contact SAP Datasphere administrator for help

## SAP Documentation

- [SAP Datasphere Security Guide](https://help.sap.com/docs/SAP_DATASPHERE/c8a54ee704e94e15926551293243fd1d/a2c7bc7e9a4e4fb7993e2ba9fc07e7cc.html)
- [OAuth 2.0 Configuration](https://help.sap.com/docs/SAP_DATASPHERE/c8a54ee704e94e15926551293243fd1d/47a0f11e94ae489ba0a0d5c90af41540.html)
- [Space Roles and Permissions](https://help.sap.com/docs/SAP_DATASPHERE/c8a54ee704e94e15926551293243fd1d/89dd40a6fdde4b1f85d64dc17d1ecd03.html)

---

**Status:** OAuth integration is complete. Waiting for permissions to be assigned to Technical User `kirotechnical1`.
