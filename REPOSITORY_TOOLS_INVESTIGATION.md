# Repository Tools HTML Response Investigation

## Problem Summary

6 repository-related tools are returning HTML instead of JSON on the ailien-test tenant:

1. `search_repository` - Endpoint: `/deepsea/repository/search/$all`
2. `list_repository_objects` - Endpoint: `/deepsea/repository/{space_id}/objects`
3. `get_object_definition` - Endpoint: `/deepsea/repository/{space_id}/designobjects/{object_id}`
4. `get_deployed_objects` - Endpoint: `/deepsea/repository/{space_id}/deployedobjects`
5. `get_repository_search_metadata` - Endpoint: `/deepsea/repository/search/$metadata`
6. `search_catalog` - Endpoint: `/v1/dwc/catalog/search`

## Current Implementation

All tools are calling SAP Datasphere REST API endpoints using OAuth 2.0 authentication:

```python
# Example from search_repository
endpoint = "/deepsea/repository/search/$all"
params = {
    "search": search_terms,
    "$top": top,
    "$skip": skip,
    "$filter": "...",
    "$expand": "..."
}
response = await datasphere_connector.get(endpoint, params=params)
```

**OAuth Configuration:**
- Base URL: `https://ailien-test.eu20.hcs.cloud.sap`
- Authentication: OAuth 2.0 Client Credentials
- Headers: `Authorization: Bearer {token}`, `Accept: application/json`

## Error Details

**HTTP Status:** 200 OK
**Content-Type:** `text/html`
**Error Message:** `Attempt to decode JSON with unexpected mimetype: text/html`

This suggests:
- The endpoints exist (not 404)
- They are accessible (not 403)
- But they return HTML instead of JSON

## Working vs Non-Working Endpoints

### ✅ WORKING Endpoints (Return JSON)

**Catalog/Consumption APIs:**
```
/api/v1/datasphere/consumption/catalog/spaces
/api/v1/datasphere/consumption/catalog/assets
/api/v1/datasphere/consumption/analytical/{space}/{asset}
/api/v1/datasphere/consumption/catalog/$metadata
```

**Database User Management:**
```
/api/v1/dwc/databaseusers
/api/v1/dwc/databaseusers/{userId}
```

**Task Management:**
```
/api/v1/dwc/tasks/{taskId}
```

### ❌ NOT WORKING Endpoints (Return HTML)

**Repository APIs:**
```
/deepsea/repository/search/$all
/deepsea/repository/{space_id}/objects
/deepsea/repository/{space_id}/designobjects/{object_id}
/deepsea/repository/{space_id}/deployedobjects
/deepsea/repository/search/$metadata
```

**Catalog Search:**
```
/v1/dwc/catalog/search
```

## Pattern Analysis

### Working Pattern
- Path prefix: `/api/v1/datasphere/consumption/...`
- Path prefix: `/api/v1/dwc/...`
- All return JSON

### Non-Working Pattern
- Path prefix: `/deepsea/repository/...`
- Path prefix: `/v1/dwc/catalog/...` (without `/api/` prefix)
- All return HTML

## Hypothesis

The `/deepsea/` endpoints might be:
1. **UI endpoints** - Designed for browser access, not API access
2. **Different API version** - Require different authentication or headers
3. **Tenant-specific** - Not enabled on ailien-test tenant
4. **Wrong base path** - Should use different URL structure

## Questions for Original Agent

### 1. API Endpoint Verification
**Question:** Are the `/deepsea/repository/...` endpoints the correct REST API paths for SAP Datasphere repository operations?

**Context:** These endpoints return HTML on our tenant, while `/api/v1/datasphere/consumption/...` endpoints return JSON correctly.

**Specific endpoints to verify:**
- `/deepsea/repository/search/$all` (search_repository)
- `/deepsea/repository/{space_id}/objects` (list_repository_objects)
- `/deepsea/repository/{space_id}/designobjects/{object_id}` (get_object_definition)
- `/deepsea/repository/{space_id}/deployedobjects` (get_deployed_objects)

### 2. Alternative API Paths
**Question:** Is there an alternative API path for repository operations using the `/api/v1/datasphere/...` pattern?

**Context:** All working endpoints use `/api/v1/datasphere/consumption/...` or `/api/v1/dwc/...` prefixes.

**Examples we need:**
- Repository object listing
- Object definition retrieval
- Design-time object access
- Deployment status queries

### 3. Authentication Requirements
**Question:** Do repository endpoints require different authentication than consumption endpoints?

**Current authentication:**
- OAuth 2.0 Client Credentials
- Scope: Not specified (default scope)
- Headers: `Authorization: Bearer {token}`, `Accept: application/json`

**Possibilities:**
- Need specific OAuth scope for repository access?
- Need additional headers?
- Need different token endpoint?

### 4. Tenant Configuration
**Question:** Do repository endpoints require specific tenant features to be enabled?

**Context:** We're testing on `ailien-test.eu20.hcs.cloud.sap` tenant.

**Questions:**
- Are repository APIs available on all tenant types?
- Do we need specific licenses or features enabled?
- Are there tenant configuration requirements?

### 5. API Version/Documentation
**Question:** What is the correct API documentation for SAP Datasphere repository operations?

**Current references:**
- SAP Datasphere Consumption API (working)
- SAP Data Warehouse Cloud API (partially working)
- Repository/Design-time API (not working)

**Need:**
- Official documentation links
- API version information
- Sample requests/responses

## Possible Solutions

### Option 1: Use Correct API Endpoints
If alternative endpoints exist:
```python
# Instead of: /deepsea/repository/search/$all
# Use: /api/v1/datasphere/repository/search (hypothetical)
```

### Option 2: Add Required Headers/Authentication
If different auth is needed:
```python
headers = await datasphere_connector._get_headers()
headers['X-Repository-Access'] = 'true'  # hypothetical
# or different scope in OAuth config
```

### Option 3: Use Different API Approach
If repository operations should use different API:
```python
# Use catalog API to get repository information
# Or use different service endpoint
```

### Option 4: Document Limitation
If endpoints are not available:
```markdown
⚠️ Repository APIs not available on this tenant type
Use catalog APIs for object discovery instead
```

## Testing Checklist

Once we get clarification, test:

- [ ] Verify correct endpoint paths
- [ ] Test with different headers
- [ ] Try different OAuth scopes
- [ ] Check tenant configuration
- [ ] Test on different tenant (if available)
- [ ] Document working solution
- [ ] Update tool implementations
- [ ] Re-run Kiro's test suite

## Expected Response Format

When repository endpoints work correctly, we expect:

```json
{
  "value": [
    {
      "id": "OBJECT_ID",
      "objectType": "Table",
      "name": "Object Name",
      "spaceId": "SPACE_ID",
      "status": "ACTIVE",
      "deploymentStatus": "DEPLOYED",
      "owner": "user@example.com",
      "createdAt": "2024-01-01T00:00:00Z",
      "modifiedAt": "2024-12-01T00:00:00Z",
      "version": "1.0"
    }
  ],
  "@odata.count": 1
}
```

## Current Status

- ✅ OAuth authentication working (26/32 tools successful)
- ✅ Consumption APIs working perfectly
- ✅ Database user APIs working
- ❌ Repository APIs returning HTML
- ❓ Waiting for agent clarification on correct endpoints

## Next Steps

1. Get answers from original agent
2. Update endpoint paths if needed
3. Modify authentication if required
4. Re-test all repository tools
5. Document final solution
6. Update MCP server code
7. Have Kiro re-run comprehensive tests

---

**Created:** December 9, 2024
**Status:** Awaiting agent clarification
**Impact:** 6 tools (19% of total) currently non-functional due to HTML responses
