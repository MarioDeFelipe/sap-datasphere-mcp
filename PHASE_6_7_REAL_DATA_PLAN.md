# Phase 6 & 7 Real Data Integration Plan

**Goal:** Convert 10 mock mode tools to real API integration
**Current Status:** All 10 tools working with mock data
**Target:** Connect to real SAP Datasphere APIs

---

## 🎯 Integration Strategy

### Step 1: API Endpoint Discovery
Test which endpoints are available in your tenant:

**KPI Endpoints:**
- `GET /api/v1/datasphere/search?search=SCOPE:comsapcatalogsearchprivateSearchKPIsAdmin`
- `GET /api/v1/datasphere/kpis/{id}`
- `GET /api/v1/datasphere/kpis`

**System Monitoring Endpoints:**
- `GET /api/v1/datasphere/systems/overview`
- `GET /api/v1/datasphere/logs/search`
- `GET /api/v1/datasphere/logs/export`
- `GET /api/v1/datasphere/logs/facets`

**User Management Endpoints:**
- `GET /api/v1/datasphere/users`
- `GET /api/v1/datasphere/users/{id}/permissions`
- `GET /api/v1/datasphere/users/{id}`

### Step 2: Test Each Endpoint
For each endpoint:
1. Call with minimal parameters
2. Check HTTP status code
3. Verify response format
4. Document any errors or limitations

### Step 3: Update Implementation
Once endpoints are confirmed working:
1. Update tool implementation if needed
2. Verify response parsing
3. Test error handling
4. Update mock mode flag

---

## 📋 Tool-by-Tool Integration Plan

### Phase 6: KPI Management Tools

#### Tool 1: search_kpis
**Endpoint:** `/api/v1/datasphere/search`
**Parameters:** `search=SCOPE:comsapcatalogsearchprivateSearchKPIsAdmin {query}`

**Test Command:**
```bash
# Try searching for KPIs
curl -H "Authorization: Bearer $TOKEN" \
  "https://your-tenant.hcs.cloud.sap/api/v1/datasphere/search?search=SCOPE:comsapcatalogsearchprivateSearchKPIsAdmin%20*"
```

**Expected Response:**
- 200 OK with KPI list
- or 404 if KPI search scope not available
- or 403 if permissions insufficient

**Integration Status:** ⏳ Pending test

---

#### Tool 2: get_kpi_details
**Endpoint:** `/api/v1/datasphere/kpis/{kpi_id}`
**Parameters:** `include_history`, `include_lineage`, `history_period`

**Test Command:**
```bash
# Get KPI details (need a real KPI ID first)
curl -H "Authorization: Bearer $TOKEN" \
  "https://your-tenant.hcs.cloud.sap/api/v1/datasphere/kpis/YOUR_KPI_ID"
```

**Expected Response:**
- 200 OK with KPI metadata
- or 404 if KPI endpoint not available
- or 404 if KPI ID not found

**Integration Status:** ⏳ Pending test (need KPI ID from search_kpis)

---

#### Tool 3: list_all_kpis
**Endpoint:** `/api/v1/datasphere/kpis`
**Parameters:** `$filter`, `$top`, `$skip`

**Test Command:**
```bash
# List all KPIs
curl -H "Authorization: Bearer $TOKEN" \
  "https://your-tenant.hcs.cloud.sap/api/v1/datasphere/kpis?\$top=10"
```

**Expected Response:**
- 200 OK with KPI inventory
- or 404 if endpoint not available
- Empty list if no KPIs defined

**Integration Status:** ⏳ Pending test

---

### Phase 7: System Monitoring Tools

#### Tool 4: get_systems_overview
**Endpoint:** `/api/v1/datasphere/systems/overview`
**Parameters:** `include_details`, `health_check`

**Test Command:**
```bash
# Get systems overview
curl -H "Authorization: Bearer $TOKEN" \
  "https://your-tenant.hcs.cloud.sap/api/v1/datasphere/systems/overview"
```

**Expected Response:**
- 200 OK with system information
- or 404 if endpoint not available
- Might be admin-only endpoint

**Integration Status:** ⏳ Pending test

---

#### Tool 5: search_system_logs
**Endpoint:** `/api/v1/datasphere/logs/search`
**Parameters:** `query`, `level`, `component`, `user_id`, `start_time`, `end_time`

**Test Command:**
```bash
# Search system logs
curl -H "Authorization: Bearer $TOKEN" \
  "https://your-tenant.hcs.cloud.sap/api/v1/datasphere/logs/search?\$top=10"
```

**Expected Response:**
- 200 OK with log entries
- or 404 if logging endpoint not available
- or 403 if admin permissions required

**Integration Status:** ⏳ Pending test

---

#### Tool 6: download_system_logs
**Endpoint:** `/api/v1/datasphere/logs/export`
**Parameters:** `format`, `level`, `component`, `start_time`, `end_time`, `max_records`

**Test Command:**
```bash
# Request log export
curl -H "Authorization: Bearer $TOKEN" \
  "https://your-tenant.hcs.cloud.sap/api/v1/datasphere/logs/export?format=JSON"
```

**Expected Response:**
- 200 OK with export URL
- or 202 Accepted with async job ID
- or 404 if export not available

**Integration Status:** ⏳ Pending test

---

#### Tool 7: get_system_log_facets
**Endpoint:** `/api/v1/datasphere/logs/facets`
**Parameters:** `facet_fields`, `start_time`, `end_time`, `level`, `component`

**Test Command:**
```bash
# Get log facet analysis
curl -H "Authorization: Bearer $TOKEN" \
  "https://your-tenant.hcs.cloud.sap/api/v1/datasphere/logs/facets?facet_fields=level,component"
```

**Expected Response:**
- 200 OK with faceted analysis
- or 404 if facet endpoint not available

**Integration Status:** ⏳ Pending test

---

### Phase 7: User Administration Tools

#### Tool 8: list_users
**Endpoint:** `/api/v1/datasphere/users`
**Parameters:** `$filter`, `$top`, `$skip`, `include_permissions`

**Test Command:**
```bash
# List users
curl -H "Authorization: Bearer $TOKEN" \
  "https://your-tenant.hcs.cloud.sap/api/v1/datasphere/users?\$top=10"
```

**Expected Response:**
- 200 OK with user list
- or 404 if user management API not available
- or 403 if admin permissions required

**Integration Status:** ⏳ Pending test

---

#### Tool 9: get_user_permissions
**Endpoint:** `/api/v1/datasphere/users/{user_id}/permissions`
**Parameters:** `space_id`, `include_inherited`

**Test Command:**
```bash
# Get user permissions (need user ID from list_users)
curl -H "Authorization: Bearer $TOKEN" \
  "https://your-tenant.hcs.cloud.sap/api/v1/datasphere/users/YOUR_USER_ID/permissions"
```

**Expected Response:**
- 200 OK with permission details
- or 404 if endpoint not available

**Integration Status:** ⏳ Pending test (need user ID)

---

#### Tool 10: get_user_details
**Endpoint:** `/api/v1/datasphere/users/{user_id}`
**Parameters:** `include_activity`, `include_audit`, `activity_days`

**Test Command:**
```bash
# Get user details
curl -H "Authorization: Bearer $TOKEN" \
  "https://your-tenant.hcs.cloud.sap/api/v1/datasphere/users/YOUR_USER_ID"
```

**Expected Response:**
- 200 OK with user profile
- or 404 if endpoint not available

**Integration Status:** ⏳ Pending test (need user ID)

---

## 🧪 Testing Approach

### Phase 1: Endpoint Discovery (Use Existing Tool)
We can use the MCP server's existing `test_connection` tool to test new endpoints:

1. **Try each endpoint** via the datasphere_connector
2. **Document response codes:**
   - 200 OK = Endpoint exists and works ✅
   - 404 Not Found = Endpoint not available ❌
   - 403 Forbidden = Need permissions ⚠️
   - 400 Bad Request = Wrong parameters ⚠️

### Phase 2: Response Analysis
For successful endpoints:
1. Check response format matches expected structure
2. Verify data types
3. Test filtering and pagination
4. Document any differences from mock data

### Phase 3: Code Updates
For working endpoints:
1. Keep existing mock mode implementation
2. Update real mode to handle actual response structure
3. Add error handling for edge cases
4. Test both modes

---

## 🔍 Alternative Discovery Methods

If standard endpoints don't work, try these alternatives:

### Method 1: Use Existing Search
The `search_catalog` tool with KPI scope already works:
```python
# This might already return KPIs!
search_catalog(query="SCOPE:comsapcatalogsearchprivateSearchKPIsAdmin *")
```

### Method 2: Explore Tenant APIs
Check what APIs are available:
```bash
# Get tenant capabilities
curl -H "Authorization: Bearer $TOKEN" \
  "https://your-tenant.hcs.cloud.sap/api/v1/datasphere"
```

### Method 3: Check Documentation
Look for SAP Datasphere API documentation specific to:
- KPI management features
- System monitoring capabilities
- User administration APIs

---

## 📊 Expected Outcomes

### Scenario A: All Endpoints Available ✅
- **Result:** 38/38 tools with real data (100%)
- **Effort:** Update code, test, deploy
- **Timeline:** 1-2 hours

### Scenario B: Some Endpoints Available ⚠️
- **Result:** 28+ tools with real data (74%+)
- **Strategy:** Enable what works, keep mock for rest
- **Timeline:** 2-3 hours

### Scenario C: Endpoints Not Available ❌
- **Result:** Stay at 28 tools with real data (74%)
- **Strategy:** Keep mock mode, document requirements
- **Alternative:** Use workarounds or composite APIs

---

## 🚀 Implementation Steps

### Step 1: Create Test Tool
Add a diagnostic tool to test all endpoints:

```python
async def test_phase67_endpoints():
    """Test all Phase 6 & 7 endpoints for availability"""

    results = {}

    # Test each endpoint
    endpoints = {
        "kpi_search": "/api/v1/datasphere/search?search=SCOPE:comsapcatalogsearchprivateSearchKPIsAdmin%20*",
        "kpi_list": "/api/v1/datasphere/kpis",
        "systems_overview": "/api/v1/datasphere/systems/overview",
        "logs_search": "/api/v1/datasphere/logs/search",
        "users_list": "/api/v1/datasphere/users",
        # ... etc
    }

    for name, endpoint in endpoints.items():
        try:
            response = await datasphere_connector.get(endpoint)
            results[name] = {"status": "available", "code": 200}
        except Exception as e:
            results[name] = {"status": "unavailable", "error": str(e)}

    return results
```

### Step 2: Run Diagnostic
Execute test tool to map available endpoints

### Step 3: Update Tools
For each available endpoint:
1. Update implementation
2. Test with real data
3. Verify error handling
4. Update documentation

### Step 4: Validation
- Test all tools in Claude Desktop
- Verify real data responses
- Check error handling
- Update README badges

---

## 📝 Documentation Updates

After integration:

1. **README.md:**
   - Update real data badge (28/38 → X/38)
   - Update tool status table
   - Add notes on enabled features

2. **Tool Documentation:**
   - Mark tools as "Real Data" ✅
   - Document any limitations
   - Add real data examples

3. **Integration Guide:**
   - Document endpoint requirements
   - List prerequisites (permissions, features)
   - Troubleshooting tips

---

## ✅ Success Criteria

**Minimum Success:** 1+ tools with real data (29+/38 = 76%+)
**Target Success:** 5+ tools with real data (33+/38 = 87%+)
**Stretch Goal:** All 10 tools with real data (38/38 = 100%)

---

## 🎯 Next Steps

1. **Create endpoint test tool** to discover what's available
2. **Run diagnostics** on your tenant
3. **Report results** - which endpoints work
4. **Update implementations** for working endpoints
5. **Test and validate** each tool
6. **Update documentation** with final status

**Ready to start with Step 1: Creating the endpoint test tool?**
