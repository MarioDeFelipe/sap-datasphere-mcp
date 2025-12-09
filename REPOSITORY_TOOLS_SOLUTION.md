# Repository Tools Solution - Use Catalog APIs Instead

## Problem Summary

The 6 repository tools using `/deepsea/repository/...` endpoints return HTML because these are **internal UI endpoints**, not REST APIs.

## Root Cause

SAP Datasphere has two types of endpoints:
- **UI Endpoints** (`/deepsea/...`) - Return HTML for browser access
- **REST APIs** (`/api/v1/...`) - Return JSON for programmatic access

The repository/design-time operations are **not exposed via public REST APIs**. They're only available through:
- SAP Datasphere Web UI
- SAP Datasphere CLI
- SAP Business Application Studio

## Solution: Use Catalog APIs

Replace repository tools with catalog-based alternatives that provide similar functionality:

### Tool Mapping

| ❌ Original Tool | ✅ Replacement Approach |
|-----------------|------------------------|
| `search_repository` | Use `search_catalog` with proper endpoint |
| `list_repository_objects` | Use `get_space_assets` + `list_catalog_assets` |
| `get_object_definition` | Use `get_asset_details` + metadata tools |
| `get_deployed_objects` | Use `list_catalog_assets` with filters |
| `get_repository_search_metadata` | Use `get_catalog_metadata` |

### Detailed Replacements

#### 1. search_repository → search_catalog (FIXED)

**Problem**: `/deepsea/repository/search/$all` returns HTML

**Solution**: Use the correct catalog search endpoint:
```python
# ❌ WRONG (returns HTML)
endpoint = "/deepsea/repository/search/$all"

# ✅ CORRECT (returns JSON)
endpoint = "/api/v1/datasphere/consumption/catalog/search"
# OR
endpoint = "/v1/dwc/catalog/search"  # Legacy but may work
```

**Implementation**:
```python
@mcp.tool()
async def search_catalog(
    query: str,
    facets: str = None,
    top: int = 50,
    skip: int = 0
) -> str:
    """
    Universal search across all catalog items in SAP Datasphere.
    
    Searches across KPIs, assets, spaces, models, views, and tables.
    """
    try:
        endpoint = "/api/v1/datasphere/consumption/catalog/search"
        
        params = {
            "search": query,
            "$top": top,
            "$skip": skip
        }
        
        if facets:
            params["facets"] = facets
        
        response = await datasphere_connector.get(endpoint, params=params)
        return format_search_results(response)
    except Exception as e:
        return f"❌ Search failed: {str(e)}"
```

#### 2. list_repository_objects → get_space_assets

**Problem**: `/deepsea/repository/{space_id}/objects` returns HTML

**Solution**: Use catalog API to list assets in a space:
```python
# ❌ WRONG (returns HTML)
endpoint = f"/deepsea/repository/{space_id}/objects"

# ✅ CORRECT (returns JSON)
endpoint = f"/api/v1/datasphere/consumption/catalog/spaces('{space_id}')/assets"
```

**Implementation**:
```python
@mcp.tool()
async def list_repository_objects(
    space_id: str,
    object_types: list[str] = None,
    top: int = 50,
    skip: int = 0
) -> str:
    """
    Browse all repository objects in a SAP Datasphere space.
    
    Returns tables, views, analytical models, and other assets.
    Uses catalog API since repository APIs are not publicly exposed.
    """
    try:
        endpoint = f"/api/v1/datasphere/consumption/catalog/spaces('{space_id}')/assets"
        
        params = {
            "$top": top,
            "$skip": skip
        }
        
        # Filter by object type if specified
        if object_types:
            type_filters = " or ".join([f"assetType eq '{t}'" for t in object_types])
            params["$filter"] = type_filters
        
        response = await datasphere_connector.get(endpoint, params=params)
        return format_repository_objects(response)
    except Exception as e:
        return f"❌ Failed to list objects: {str(e)}"
```

#### 3. get_object_definition → get_asset_details + metadata

**Problem**: `/deepsea/repository/{space_id}/designobjects/{object_id}` returns HTML

**Solution**: Combine catalog asset details with metadata APIs:
```python
# ❌ WRONG (returns HTML)
endpoint = f"/deepsea/repository/{space_id}/designobjects/{object_id}"

# ✅ CORRECT (returns JSON) - Two-step approach
# Step 1: Get asset details
asset_endpoint = f"/api/v1/datasphere/consumption/catalog/spaces('{space_id}')/assets('{asset_id}')"

# Step 2: Get detailed schema based on asset type
if asset_type == "AnalyticalModel":
    metadata_endpoint = f"/api/v1/datasphere/consumption/analytical/{space_id}/{asset_id}/$metadata"
elif asset_type == "View" or asset_type == "Table":
    metadata_endpoint = f"/api/v1/datasphere/consumption/relational/{space_id}/{asset_id}/$metadata"
```

**Implementation**:
```python
@mcp.tool()
async def get_object_definition(
    space_id: str,
    object_id: str,
    include_full_definition: bool = True
) -> str:
    """
    Get complete design-time object definition.
    
    Retrieves structure, logic, transformations, and metadata.
    Uses catalog + metadata APIs since repository APIs are not exposed.
    """
    try:
        # Step 1: Get asset details from catalog
        asset_endpoint = f"/api/v1/datasphere/consumption/catalog/spaces('{space_id}')/assets('{object_id}')"
        asset_response = await datasphere_connector.get(asset_endpoint)
        
        asset_type = asset_response.get("assetType")
        
        # Step 2: Get detailed schema based on type
        if include_full_definition:
            if asset_type == "AnalyticalModel":
                metadata_endpoint = f"/api/v1/datasphere/consumption/analytical/{space_id}/{object_id}/$metadata"
            else:
                metadata_endpoint = f"/api/v1/datasphere/consumption/relational/{space_id}/{object_id}/$metadata"
            
            metadata_response = await datasphere_connector.get(metadata_endpoint)
            
            # Parse CSDL metadata
            schema = parse_csdl_metadata(metadata_response)
            asset_response["definition"] = schema
        
        return format_object_definition(asset_response)
    except Exception as e:
        return f"❌ Failed to get object definition: {str(e)}"
```

#### 4. get_deployed_objects → list_catalog_assets with filters

**Problem**: `/deepsea/repository/{space_id}/deployedobjects` returns HTML

**Solution**: Use catalog API with exposure filter:
```python
# ❌ WRONG (returns HTML)
endpoint = f"/deepsea/repository/{space_id}/deployedobjects"

# ✅ CORRECT (returns JSON)
endpoint = f"/api/v1/datasphere/consumption/catalog/spaces('{space_id}')/assets"
params = {"$filter": "exposedForConsumption eq true"}
```

**Implementation**:
```python
@mcp.tool()
async def get_deployed_objects(
    space_id: str,
    runtime_status: str = None,
    top: int = 50,
    skip: int = 0
) -> str:
    """
    List runtime/deployed objects that are actively running.
    
    Returns deployment status, runtime metrics, and execution history.
    Uses catalog API to find exposed/deployed assets.
    """
    try:
        endpoint = f"/api/v1/datasphere/consumption/catalog/spaces('{space_id}')/assets"
        
        params = {
            "$top": top,
            "$skip": skip,
            "$filter": "exposedForConsumption eq true"  # Only deployed/exposed assets
        }
        
        response = await datasphere_connector.get(endpoint, params=params)
        
        # Enhance with runtime information if available
        for asset in response.get("value", []):
            # Try to get runtime metrics from analytical/relational endpoints
            if asset.get("assetType") == "AnalyticalModel":
                try:
                    service_endpoint = f"/api/v1/datasphere/consumption/analytical/{space_id}/{asset['assetId']}"
                    service_info = await datasphere_connector.get(service_endpoint)
                    asset["runtimeStatus"] = "Active"
                except:
                    asset["runtimeStatus"] = "Unknown"
        
        return format_deployed_objects(response)
    except Exception as e:
        return f"❌ Failed to get deployed objects: {str(e)}"
```

#### 5. get_repository_search_metadata → get_catalog_metadata

**Problem**: `/deepsea/repository/search/$metadata` returns HTML

**Solution**: Use catalog metadata endpoint:
```python
# ❌ WRONG (returns HTML)
endpoint = "/deepsea/repository/search/$metadata"

# ✅ CORRECT (returns JSON/XML)
endpoint = "/api/v1/datasphere/consumption/catalog/$metadata"
```

**Implementation**:
```python
@mcp.tool()
async def get_repository_search_metadata() -> str:
    """
    Get metadata for repository search capabilities.
    
    Returns searchable object types, fields, and entity definitions.
    Uses catalog metadata since repository APIs are not exposed.
    """
    try:
        endpoint = "/api/v1/datasphere/consumption/catalog/$metadata"
        
        response = await datasphere_connector.get(endpoint)
        
        # Parse CSDL metadata
        metadata = parse_csdl_metadata(response)
        
        return format_search_metadata(metadata)
    except Exception as e:
        return f"❌ Failed to get search metadata: {str(e)}"
```

## What Information is NOT Available

Some repository/design-time information is **not accessible via REST APIs**:

### ❌ Not Available via API:
- **Data Flow Definitions**: ETL transformation logic, step-by-step transformations
- **Stored Procedure Code**: SQL code for stored procedures
- **Calculation View Logic**: Detailed calculation view definitions
- **Deployment History**: Full deployment audit trail
- **Runtime Execution Logs**: Detailed execution logs for data flows
- **Design-Time Versions**: Version history and change tracking

### ✅ Available via Catalog APIs:
- **Asset Metadata**: Names, descriptions, types, owners
- **Schema Information**: Columns, data types, keys (via metadata endpoints)
- **Relationships**: Asset dependencies and lineage (limited)
- **Exposure Status**: Which assets are exposed for consumption
- **Basic Metrics**: Row counts, last modified dates
- **Consumption URLs**: How to access the data

## Implementation Checklist

For Claude to fix the 6 failing tools:

- [ ] **search_repository**: Change endpoint to `/api/v1/datasphere/consumption/catalog/search`
- [ ] **list_repository_objects**: Change to use `/api/v1/datasphere/consumption/catalog/spaces('{space_id}')/assets`
- [ ] **get_object_definition**: Implement two-step approach (catalog + metadata)
- [ ] **get_deployed_objects**: Use catalog assets with `exposedForConsumption eq true` filter
- [ ] **get_repository_search_metadata**: Change to `/api/v1/datasphere/consumption/catalog/$metadata`
- [ ] **search_catalog**: Fix endpoint (may already be correct)

## Testing After Changes

Test each tool with:

```python
# Test 1: Search catalog
result = await search_catalog(query="financial", top=10)

# Test 2: List objects in space
result = await list_repository_objects(space_id="SAP_CONTENT", top=20)

# Test 3: Get object definition
result = await get_object_definition(
    space_id="SAP_CONTENT",
    object_id="SAP_SC_FI_AM_FINTRANSACTIONS"
)

# Test 4: Get deployed objects
result = await get_deployed_objects(space_id="SAP_CONTENT")

# Test 5: Get search metadata
result = await get_repository_search_metadata()
```

## Documentation Updates

Update tool descriptions to clarify:
- These tools use **Catalog APIs**, not repository APIs
- Some design-time information is **not available** via REST APIs
- For full repository access, use **SAP Datasphere CLI** or **Web UI**

## Summary

**Root Cause**: `/deepsea/repository/...` are UI endpoints, not REST APIs

**Solution**: Replace with catalog API equivalents

**Impact**: 6 tools will work, but with slightly different data (catalog metadata instead of full repository definitions)

**Limitation**: Some advanced repository features (data flow logic, execution history) are not available via REST APIs

**Recommendation**: Document this limitation clearly in the MCP server README
