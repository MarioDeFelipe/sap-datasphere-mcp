# Mock Data Remediation Plan

## Current Status

**Date**: December 10, 2025
**Total Tools**: 35
**Tools Using Real Data**: 6 (17%)
**Tools Still Using Mock Data**: 8 (23%)
**Tools Not Yet Tested**: 21 (60%)

---

## ✅ Tools Already Fixed (Using Real API)

### Phase 1.1: Authentication & Connection (4/4 - 100%)
1. ✅ **test_connection** - Uses `/api/v1/datasphere/consumption/catalog/spaces`
2. ✅ **get_current_user** - Decodes JWT OAuth token
3. ✅ **get_tenant_info** - Real tenant config + health check
4. ✅ **get_available_scopes** - Decodes JWT token scopes

### Phase 1.2: Space Discovery (2/3 - 67%)
1. ✅ **list_spaces** - Uses `/api/v1/datasphere/consumption/catalog/spaces`
2. ✅ **get_space_info** - Uses `/api/v1/datasphere/consumption/catalog/spaces('{id}')`
3. ❌ **search_tables** - STILL USING MOCK DATA

**Total Fixed**: 6 tools

---

## ❌ Tools Still Using Mock Data (Requires Fixing)

### High Priority - Catalog & Asset Tools (5 tools)

#### 1. **list_catalog_assets**
- **Current**: Uses `get_mock_catalog_assets()` helper
- **Line**: 1566
- **Warning**: Line 1599 shows mock data warning
- **Real API**: `GET /api/v1/datasphere/consumption/catalog/assets`
- **Priority**: HIGH (core catalog browsing)

#### 2. **get_space_assets**
- **Current**: Uses mock data
- **Real API**: `GET /api/v1/datasphere/consumption/catalog/spaces('{space_id}')/assets`
- **Priority**: HIGH (space-specific assets)

#### 3. **get_asset_details**
- **Current**: Uses `get_mock_asset_details()` helper
- **Line**: 1608
- **Real API**: `GET /api/v1/datasphere/consumption/catalog/spaces('{space_id}')/assets('{asset_id}')`
- **Priority**: HIGH (asset metadata)

#### 4. **get_asset_by_compound_key**
- **Current**: Uses mock data with compound key lookup
- **Real API**: `GET /api/v1/datasphere/consumption/catalog/assets` with filter
- **Priority**: MEDIUM (alternative lookup method)

#### 5. **search_tables**
- **Current**: Uses `MOCK_DATA["tables"]` dictionary
- **Line**: 1140-1150
- **Real API**: `GET /api/v1/datasphere/consumption/catalog/assets?$filter=assetType eq 'Table' or assetType eq 'View'`
- **Priority**: HIGH (table discovery)

### Medium Priority - Admin Tools (2 tools)

#### 6. **browse_marketplace**
- **Current**: Returns mock marketplace packages
- **Real API**: May not exist (marketplace might be UI-only)
- **Priority**: LOW (nice-to-have)
- **Note**: Might need to stay as mock or be removed

#### 7. **get_task_status**
- **Current**: Returns mock task data
- **Real API**: `GET /api/v1/dwc/tasks/{task_id}`
- **Priority**: MEDIUM (task monitoring)
- **Note**: Already uses real API endpoint, just needs USE_MOCK_DATA check

### Already Working But No Data (2 tools)

#### 8. **get_table_schema**
- **Status**: Real API call works, but SAP_CONTENT has no tables
- **Action**: NO FIX NEEDED (working correctly)

#### 9. **list_database_users**
- **Status**: Real API call works, but no database users exist
- **Action**: NO FIX NEEDED (working correctly)

---

## Fix Pattern (Same as list_spaces)

All tools need the same fix pattern:

```python
# OLD CODE (always uses mock):
assets = get_mock_catalog_assets()
return [types.TextContent(text=json.dumps(assets) + "⚠️ Mock data warning")]

# NEW CODE (checks USE_MOCK_DATA):
if DATASPHERE_CONFIG["use_mock_data"]:
    # Mock mode
    assets = get_mock_catalog_assets()
    return [types.TextContent(text=json.dumps(assets) + "\n\nNote: Mock data.")]
else:
    # Real API mode
    if not datasphere_connector:
        return [types.TextContent(text="Error: OAuth not initialized")]

    try:
        endpoint = "/api/v1/datasphere/consumption/catalog/assets"
        data = await datasphere_connector.get(endpoint, params=params)
        assets = data.get("value", [])
        return [types.TextContent(text=json.dumps(assets))]
    except Exception as e:
        return [types.TextContent(text=f"Error: {e}")]
```

---

## API Endpoints Reference

### Catalog API Endpoints (Working)
```
✅ GET /api/v1/datasphere/consumption/catalog/spaces
✅ GET /api/v1/datasphere/consumption/catalog/spaces('{space_id}')
✅ GET /api/v1/datasphere/consumption/catalog/spaces('{space_id}')/assets
✅ GET /api/v1/datasphere/consumption/catalog/spaces('{space_id}')/assets('{asset_id}')
❓ GET /api/v1/datasphere/consumption/catalog/assets (need to test)
```

### Task API Endpoints
```
✅ GET /api/v1/dwc/tasks/{task_id}
```

### Marketplace API
```
❓ Unknown (might not exist as REST API)
```

---

## Implementation Plan

### Phase 1: Fix High-Priority Catalog Tools (5 tools)
**Estimated Time**: 1 hour
**Tools**: list_catalog_assets, get_space_assets, get_asset_details, get_asset_by_compound_key, search_tables

**Steps**:
1. Add `if DATASPHERE_CONFIG["use_mock_data"]` check
2. Implement real API call in else branch
3. Test with Kiro's tenant
4. Commit

**Expected Result**: 11/35 tools using real data (31%)

### Phase 2: Fix Medium-Priority Admin Tools (1 tool)
**Estimated Time**: 15 minutes
**Tools**: get_task_status

**Steps**:
1. Add USE_MOCK_DATA check (endpoint already correct)
2. Test
3. Commit

**Expected Result**: 12/35 tools using real data (34%)

### Phase 3: Evaluate Marketplace Tool (1 tool)
**Estimated Time**: 30 minutes
**Tools**: browse_marketplace

**Steps**:
1. Research if marketplace API exists
2. If yes: implement real API
3. If no: document as mock-only or remove

**Expected Result**: 12-13/35 tools using real data (34-37%)

---

## Testing Strategy

### Test Each Fixed Tool:
1. **Mock Mode Test** (`USE_MOCK_DATA=true`):
   - Should return mock data with "Note: Mock data" message
   - Should not make API calls

2. **Real API Test** (`USE_MOCK_DATA=false`):
   - Should call real SAP Datasphere endpoint
   - Should return real tenant data
   - Should handle errors gracefully

### Test Cases:
```python
# list_catalog_assets
- No filters → All assets
- Filter by space_id → Assets in that space
- Filter by assetType → Assets of that type
- Pagination (top/skip) → Correct subset

# get_asset_details
- Valid asset → Full details
- Invalid asset → Clear error message

# search_tables
- Search term → Matching tables
- No matches → Empty result (not error)
```

---

## Success Metrics

### Current State
- ✅ OAuth authentication: WORKING
- ✅ Real API connectivity: WORKING
- ✅ 6 tools using real data: WORKING
- ❌ 8 tools using mock data: NEEDS FIX

### Target State (After Phase 1-2)
- ✅ 12+ tools using real data (34%+)
- ✅ All core catalog tools using real API
- ✅ All Phase 1 foundation tools using real API
- ✅ Production-ready for SAP Datasphere integration

---

## Risk Assessment

### Low Risk (Safe to Fix)
- ✅ list_catalog_assets - Well-documented endpoint
- ✅ get_space_assets - Already proven pattern
- ✅ get_asset_details - Simple GET by ID
- ✅ search_tables - Standard OData filter

### Medium Risk (Need Testing)
- ⚠️ get_asset_by_compound_key - Complex filter syntax
- ⚠️ get_task_status - Task might not exist on tenant

### High Risk (Might Not Exist)
- 🚨 browse_marketplace - API might not exist

---

## Next Steps

### Immediate (Now)
1. **Fix list_catalog_assets** (highest priority, most used)
2. **Fix search_tables** (Phase 1.2 completion)
3. **Fix get_asset_details** (essential for metadata)

### Short Term (Next Session)
4. Fix get_space_assets
5. Fix get_asset_by_compound_key
6. Fix get_task_status

### Long Term (Future)
7. Research marketplace API
8. Document remaining tools
9. Update README with real data status

---

## Commit Strategy

### Commit 1: Fix Core Catalog Tools
- list_catalog_assets
- get_asset_details
- search_tables

**Message**: "Fix core catalog tools to use real API (3 tools)"

### Commit 2: Fix Space Assets
- get_space_assets
- get_asset_by_compound_key

**Message**: "Fix asset lookup tools to use real API (2 tools)"

### Commit 3: Fix Admin Tools
- get_task_status

**Message**: "Fix task status to use real API"

---

## Notes

- All API endpoints use OAuth authentication via `datasphere_connector.get()`
- All tools should handle 404, 403, and connection errors gracefully
- Mock data should remain available for testing/demo purposes
- Real data access should be the default when OAuth is configured

---

**Created**: December 10, 2025
**Status**: In Progress
**Next Action**: Fix list_catalog_assets, search_tables, get_asset_details
**Assignee**: Claude
**Reviewer**: Kiro
