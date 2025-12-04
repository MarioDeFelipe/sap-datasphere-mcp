# SAP Datasphere Catalog Tools - Detailed Specification

## Overview

This document provides complete API specifications and implementation guidance for the four core catalog browsing tools in the SAP Datasphere MCP Server.

---

## Tool 1: `list_catalog_assets`

### Purpose
Browse all assets across all spaces that the authenticated user has access to.

### API Endpoint Details

**Primary Endpoint (Modern API)**:
```
GET /api/v1/datasphere/consumption/catalog/assets
```

**Alternative Endpoint (Legacy DWC API)**:
```
GET /v1/dwc/catalog/assets
```

### Authentication
- **Type**: OAuth2 Bearer Token
- **Required Scopes**: Catalog read access

### Request Parameters (OData Query Options)

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `$select` | string | No | Select specific fields to return | `$select=name,description,spaceId` |
| `$filter` | string | No | Filter results by criteria | `$filter=spaceId eq 'SAP_CONTENT'` |
| `$expand` | string | No | Expand related entities | `$expand=space,metadata` |
| `$top` | integer | No | Limit number of results | `$top=50` |
| `$skip` | integer | No | Skip number of results (pagination) | `$skip=100` |
| `$count` | boolean | No | Include total count in response | `$count=true` |
| `$orderby` | string | No | Sort results | `$orderby=name asc` |

### Response Format
**Content-Type**: `application/json` (OData JSON format)

### Expected Response Structure
```json
{
  "@odata.context": "$metadata#assets",
  "@odata.count": 150,
  "value": [
    {
      "id": "SAP_SC_FI_AM_FINTRANSACTIONS",
      "name": "Financial Transactions",
      "description": "Comprehensive financial transaction data",
      "spaceId": "SAP_CONTENT",
      "spaceName": "SAP Content",
      "assetType": "AnalyticalModel",
      "exposedForConsumption": true,
      "analyticalConsumptionUrl": "/api/v1/datasphere/consumption/analytical/SAP_CONTENT/SAP_SC_FI_AM_FINTRANSACTIONS",
      "relationalConsumptionUrl": "/api/v1/datasphere/consumption/relational/SAP_CONTENT/SAP_SC_FI_AM_FINTRANSACTIONS",
      "metadataUrl": "/api/v1/datasphere/consumption/analytical/SAP_CONTENT/SAP_SC_FI_AM_FINTRANSACTIONS/$metadata",
      "createdBy": "SYSTEM",
      "createdAt": "2024-01-15T10:30:00Z",
      "modifiedBy": "ADMIN",
      "modifiedAt": "2024-11-20T14:22:00Z",
      "tags": ["finance", "transactions", "analytical"]
    },
    {
      "id": "SALES_DATA_VIEW",
      "name": "Sales Data View",
      "description": "Sales transaction view with customer details",
      "spaceId": "SALES_SPACE",
      "spaceName": "Sales Analytics",
      "assetType": "View",
      "exposedForConsumption": true,
      "analyticalConsumptionUrl": null,
      "relationalConsumptionUrl": "/api/v1/datasphere/consumption/relational/SALES_SPACE/SALES_DATA_VIEW",
      "metadataUrl": "/api/v1/datasphere/consumption/relational/SALES_SPACE/SALES_DATA_VIEW/$metadata",
      "createdBy": "SALES_ADMIN",
      "createdAt": "2024-03-10T08:15:00Z",
      "modifiedBy": "SALES_ADMIN",
      "modifiedAt": "2024-10-05T16:45:00Z",
      "tags": ["sales", "customer", "relational"]
    }
  ]
}
```

### Error Responses

| Status Code | Description | Example Response |
|-------------|-------------|------------------|
| 401 | Unauthorized - Invalid or expired token | `{"error": "unauthorized", "message": "Token expired"}` |
| 403 | Forbidden - Insufficient permissions | `{"error": "forbidden", "message": "User lacks catalog read permission"}` |
| 500 | Internal Server Error | `{"error": "internal_error", "message": "Service temporarily unavailable"}` |

### Use Cases
- Build a complete data catalog
- Discover all available data assets
- Create asset inventory reports
- Enable data discovery for users
- Integration planning and scoping

---

## Tool 2: `get_asset_details`

### Purpose
Get detailed metadata for a specific asset within a space.

### API Endpoint Details

**Primary Endpoint (Modern API)**:
```
GET /api/v1/datasphere/consumption/catalog/spaces('{spaceId}')/assets('{assetId}')
```

**Alternative Endpoint (Legacy DWC API)**:
```
GET /v1/dwc/catalog/spaces('{spaceId}')/assets('{assetId}')
```

### Authentication
- **Type**: OAuth2 Bearer Token
- **Required Scopes**: Catalog read access

### Path Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `spaceId` | string | Yes | The space identifier | `SAP_CONTENT` |
| `assetId` | string | Yes | The asset identifier | `SAP_SC_FI_AM_FINTRANSACTIONS` |

### Request Parameters (OData Query Options)

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `$select` | string | No | Select specific fields | `$select=name,description,assetType` |
| `$expand` | string | No | Expand related entities | `$expand=columns,relationships` |

### Response Format
**Content-Type**: `application/json` (OData JSON format)

### Expected Response Structure
```json
{
  "@odata.context": "$metadata#assets/$entity",
  "id": "SAP_SC_FI_AM_FINTRANSACTIONS",
  "name": "Financial Transactions",
  "technicalName": "SAP_SC_FI_AM_FINTRANSACTIONS",
  "description": "Comprehensive financial transaction data with account information, transaction types, amounts, and currencies",
  "businessPurpose": "Financial reporting, transaction analysis, audit trails, regulatory compliance",
  "spaceId": "SAP_CONTENT",
  "spaceName": "SAP Content",
  "assetType": "AnalyticalModel",
  "exposedForConsumption": true,
  "consumptionType": ["Analytical", "Relational"],
  "analyticalConsumptionUrl": "/api/v1/datasphere/consumption/analytical/SAP_CONTENT/SAP_SC_FI_AM_FINTRANSACTIONS",
  "relationalConsumptionUrl": "/api/v1/datasphere/consumption/relational/SAP_CONTENT/SAP_SC_FI_AM_FINTRANSACTIONS",
  "analyticalMetadataUrl": "/api/v1/datasphere/consumption/analytical/SAP_CONTENT/SAP_SC_FI_AM_FINTRANSACTIONS/$metadata",
  "relationalMetadataUrl": "/api/v1/datasphere/consumption/relational/SAP_CONTENT/SAP_SC_FI_AM_FINTRANSACTIONS/$metadata",
  "owner": "SYSTEM",
  "createdBy": "SYSTEM",
  "createdAt": "2024-01-15T10:30:00Z",
  "modifiedBy": "ADMIN",
  "modifiedAt": "2024-11-20T14:22:00Z",
  "status": "Active",
  "version": "2.1",
  "tags": ["finance", "transactions", "analytical", "compliance"],
  "businessContext": {
    "domain": "Finance",
    "subDomain": "Accounting",
    "dataClassification": "Confidential",
    "retentionPeriod": "7 years"
  },
  "technicalDetails": {
    "rowCount": 15000000,
    "sizeInMB": 2500,
    "lastRefreshed": "2024-12-04T02:00:00Z",
    "refreshFrequency": "Daily"
  },
  "dimensions": [
    {
      "name": "AccountDimension",
      "description": "Chart of accounts dimension",
      "cardinality": 5000
    },
    {
      "name": "TimeDimension",
      "description": "Time hierarchy with year, quarter, month, day",
      "cardinality": 3650
    }
  ],
  "measures": [
    {
      "name": "TransactionAmount",
      "description": "Transaction amount in local currency",
      "aggregation": "SUM",
      "dataType": "Decimal(15,2)"
    },
    {
      "name": "TransactionCount",
      "description": "Number of transactions",
      "aggregation": "COUNT",
      "dataType": "Integer"
    }
  ],
  "relationships": [
    {
      "relatedAsset": "ACCOUNT_MASTER",
      "relationshipType": "ManyToOne",
      "joinKey": "AccountID"
    }
  ]
}
```

### Error Responses

| Status Code | Description | Example Response |
|-------------|-------------|------------------|
| 401 | Unauthorized | `{"error": "unauthorized", "message": "Token expired"}` |
| 403 | Forbidden | `{"error": "forbidden", "message": "No access to space SAP_CONTENT"}` |
| 404 | Not Found | `{"error": "not_found", "message": "Asset SAP_SC_FI_AM_FINTRANSACTIONS not found in space SAP_CONTENT"}` |
| 500 | Internal Server Error | `{"error": "internal_error", "message": "Service temporarily unavailable"}` |

### Use Cases
- Retrieve complete asset documentation
- Understand asset structure and relationships
- Get consumption URLs for data access
- Validate asset availability before integration
- Generate asset documentation

---

## Tool 3: `get_asset_by_compound_key`

### Purpose
Retrieve asset using its compound key identifier (alternative to space+asset lookup).

### API Endpoint Details

**Primary Endpoint (Modern API)**:
```
GET /api/v1/datasphere/consumption/catalog/assets({assetCompoundId})
```

**Alternative Endpoint (Legacy DWC API)**:
```
GET /v1/dwc/catalog/assets({assetCompoundId})
```

### Authentication
- **Type**: OAuth2 Bearer Token
- **Required Scopes**: Catalog read access

### Path Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `assetCompoundId` | string | Yes | Compound key in OData format | `spaceId='SAP_CONTENT',assetId='SAP_SC_FI_AM_FINTRANSACTIONS'` |

### Compound Key Format
The compound key combines space ID and asset ID in OData key format:
```
spaceId='<SPACE_ID>',assetId='<ASSET_ID>'
```

**Examples**:
- `spaceId='SAP_CONTENT',assetId='SAP_SC_FI_AM_FINTRANSACTIONS'`
- `spaceId='SALES_SPACE',assetId='CUSTOMER_VIEW'`
- `spaceId='HR_ANALYTICS',assetId='EMPLOYEE_DATA'`

### Request Parameters (OData Query Options)

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `$select` | string | No | Select specific fields | `$select=name,description,consumptionUrls` |
| `$expand` | string | No | Expand related entities | `$expand=space,metadata` |

### Response Format
**Content-Type**: `application/json` (OData JSON format)

### Expected Response Structure
Same as `get_asset_details` - returns complete asset metadata.

```json
{
  "@odata.context": "$metadata#assets/$entity",
  "id": "SAP_SC_FI_AM_FINTRANSACTIONS",
  "name": "Financial Transactions",
  "spaceId": "SAP_CONTENT",
  "assetType": "AnalyticalModel",
  "analyticalConsumptionUrl": "/api/v1/datasphere/consumption/analytical/SAP_CONTENT/SAP_SC_FI_AM_FINTRANSACTIONS",
  "relationalConsumptionUrl": "/api/v1/datasphere/consumption/relational/SAP_CONTENT/SAP_SC_FI_AM_FINTRANSACTIONS",
  ...
}
```

### Error Responses

| Status Code | Description | Example Response |
|-------------|-------------|------------------|
| 400 | Bad Request - Invalid compound key format | `{"error": "bad_request", "message": "Invalid compound key format"}` |
| 401 | Unauthorized | `{"error": "unauthorized", "message": "Token expired"}` |
| 403 | Forbidden | `{"error": "forbidden", "message": "No access to asset"}` |
| 404 | Not Found | `{"error": "not_found", "message": "Asset not found"}` |
| 500 | Internal Server Error | `{"error": "internal_error", "message": "Service temporarily unavailable"}` |

### Use Cases
- Direct asset lookup when compound key is known
- Bookmark/favorite asset access
- API integration with pre-known asset identifiers
- Cross-reference resolution

---

## Tool 4: `get_space_assets`

### Purpose
List all assets within a specific space.

### API Endpoint Details

**Primary Endpoint (Modern API)**:
```
GET /api/v1/datasphere/consumption/catalog/spaces('{spaceId}')/assets
```

**Alternative Endpoint (Legacy DWC API)**:
```
GET /v1/dwc/catalog/spaces('{spaceId}')/assets
```

### Authentication
- **Type**: OAuth2 Bearer Token
- **Required Scopes**: Catalog read access

### Path Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `spaceId` | string | Yes | The space identifier | `SAP_CONTENT` |

### Request Parameters (OData Query Options)

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `$select` | string | No | Select specific fields | `$select=name,assetType,description` |
| `$filter` | string | No | Filter assets by criteria | `$filter=assetType eq 'AnalyticalModel'` |
| `$expand` | string | No | Expand related entities | `$expand=metadata` |
| `$top` | integer | No | Limit number of results | `$top=20` |
| `$skip` | integer | No | Skip results (pagination) | `$skip=40` |
| `$count` | boolean | No | Include total count | `$count=true` |
| `$orderby` | string | No | Sort results | `$orderby=name asc` |

### Response Format
**Content-Type**: `application/json` (OData JSON format)

### Expected Response Structure
```json
{
  "@odata.context": "$metadata#spaces('SAP_CONTENT')/assets",
  "@odata.count": 45,
  "value": [
    {
      "id": "SAP_SC_FI_AM_FINTRANSACTIONS",
      "name": "Financial Transactions",
      "description": "Comprehensive financial transaction data",
      "assetType": "AnalyticalModel",
      "exposedForConsumption": true,
      "analyticalConsumptionUrl": "/api/v1/datasphere/consumption/analytical/SAP_CONTENT/SAP_SC_FI_AM_FINTRANSACTIONS",
      "relationalConsumptionUrl": "/api/v1/datasphere/consumption/relational/SAP_CONTENT/SAP_SC_FI_AM_FINTRANSACTIONS",
      "createdAt": "2024-01-15T10:30:00Z",
      "modifiedAt": "2024-11-20T14:22:00Z"
    },
    {
      "id": "COST_CENTER_VIEW",
      "name": "Cost Center View",
      "description": "Cost center master data with hierarchies",
      "assetType": "View",
      "exposedForConsumption": true,
      "analyticalConsumptionUrl": null,
      "relationalConsumptionUrl": "/api/v1/datasphere/consumption/relational/SAP_CONTENT/COST_CENTER_VIEW",
      "createdAt": "2024-02-20T09:15:00Z",
      "modifiedAt": "2024-09-10T11:30:00Z"
    },
    {
      "id": "SALES_ORDERS_TABLE",
      "name": "Sales Orders",
      "description": "Sales order header and line items",
      "assetType": "Table",
      "exposedForConsumption": true,
      "analyticalConsumptionUrl": null,
      "relationalConsumptionUrl": "/api/v1/datasphere/consumption/relational/SAP_CONTENT/SALES_ORDERS_TABLE",
      "createdAt": "2024-03-05T14:00:00Z",
      "modifiedAt": "2024-12-01T08:45:00Z"
    }
  ]
}
```

### Common Filter Examples

**Filter by asset type**:
```
$filter=assetType eq 'AnalyticalModel'
$filter=assetType eq 'View'
$filter=assetType eq 'Table'
```

**Filter by exposure status**:
```
$filter=exposedForConsumption eq true
```

**Filter by creation date**:
```
$filter=createdAt gt 2024-01-01T00:00:00Z
```

**Combine filters**:
```
$filter=assetType eq 'AnalyticalModel' and exposedForConsumption eq true
```

### Error Responses

| Status Code | Description | Example Response |
|-------------|-------------|------------------|
| 401 | Unauthorized | `{"error": "unauthorized", "message": "Token expired"}` |
| 403 | Forbidden | `{"error": "forbidden", "message": "No access to space SAP_CONTENT"}` |
| 404 | Not Found | `{"error": "not_found", "message": "Space SAP_CONTENT not found"}` |
| 500 | Internal Server Error | `{"error": "internal_error", "message": "Service temporarily unavailable"}` |

### Use Cases
- Browse all assets in a specific space
- Space-specific data discovery
- Filter assets by type within a space
- Generate space asset inventory
- Validate space contents

---

## Implementation Notes

### OAuth2 Token Management
All tools require proper OAuth2 token handling:

```python
# Token should be refreshed if expired
headers = {
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/json"
}
```

### Pagination Best Practices
For large result sets, implement pagination:

```python
# Example pagination logic
page_size = 50
skip = 0
all_assets = []

while True:
    response = get_assets(top=page_size, skip=skip)
    assets = response.get("value", [])
    
    if not assets:
        break
    
    all_assets.extend(assets)
    skip += page_size
    
    # Check if we've retrieved all results
    if "@odata.count" in response and len(all_assets) >= response["@odata.count"]:
        break
```

### Error Handling
Implement robust error handling:

```python
try:
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        # Token expired, refresh and retry
        refresh_token()
        return retry_request()
    elif e.response.status_code == 404:
        # Asset not found
        return {"error": "not_found", "message": "Asset not found"}
    else:
        raise
except requests.exceptions.Timeout:
    return {"error": "timeout", "message": "Request timed out"}
```

### Response Caching
Consider caching catalog responses to improve performance:

```python
# Cache catalog data for 5 minutes
@cache(ttl=300)
def list_catalog_assets():
    return fetch_catalog_assets()
```

---

## Testing Checklist

### Functional Testing
- ✅ Test with valid authentication token
- ✅ Test with expired token (verify refresh)
- ✅ Test with invalid token (verify error handling)
- ✅ Test pagination with large result sets
- ✅ Test filtering with various criteria
- ✅ Test with empty spaces (no assets)
- ✅ Test with non-existent space IDs
- ✅ Test with non-existent asset IDs
- ✅ Test compound key format variations

### Performance Testing
- ✅ Test response time for large catalogs (>1000 assets)
- ✅ Test pagination performance
- ✅ Test concurrent requests
- ✅ Test with slow network conditions

### Security Testing
- ✅ Verify token is not logged or exposed
- ✅ Test permission boundaries (access denied scenarios)
- ✅ Verify HTTPS is enforced
- ✅ Test SQL injection in filter parameters

### Integration Testing
- ✅ Test tool chaining (list spaces → get space assets → get asset details)
- ✅ Test with different user permission levels
- ✅ Test with multiple tenants
- ✅ Test error recovery and retry logic

---

## Next Steps

1. Implement these four tools in the MCP server
2. Add comprehensive unit tests
3. Test with real SAP Datasphere tenant
4. Document any API variations discovered
5. Proceed to Phase 3 (Metadata & Schema Discovery)
