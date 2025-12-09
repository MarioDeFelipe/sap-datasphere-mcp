# SAP Datasphere MCP Server - Phase 4.1 Analytical Model Access Tools

## Overview

This document provides complete technical specifications for implementing **4 analytical data consumption tools** that enable business intelligence, reporting, and analytical data access from SAP Datasphere.

**Phase**: 4.1 - Data Consumption (Analytical)  
**Priority**: HIGH  
**Estimated Implementation Time**: 4-5 days  
**Tools Count**: 4

---

## Tool 1: `list_analytical_datasets`

### Purpose
List all available analytical datasets within a specific asset, showing the analytical models that can be queried for business intelligence and reporting.

### API Endpoint
```
GET /api/v1/datasphere/consumption/analytical/{spaceId}/{assetId}
```

### Authentication
- **Type**: OAuth2 Bearer Token
- **Scopes**: `DWC_CONSUMPTION` or equivalent read scope

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `spaceId` | string | Yes | Space identifier (e.g., "SAP_CONTENT") |
| `assetId` | string | Yes | Asset identifier (e.g., "SAP_SC_FI_AM_FINTRANSACTIONS") |
| `$select` | string | No | Comma-separated list of properties to return |
| `$expand` | string | No | Related entities to expand inline |
| `$top` | integer | No | Maximum number of results (default: 50, max: 1000) |
| `$skip` | integer | No | Number of results to skip for pagination |

### Response Format
```json
{
  "@odata.context": "$metadata",
  "value": [
    {
      "name": "SAP_SC_FI_AM_FINTRANSACTIONS",
      "kind": "EntitySet",
      "url": "SAP_SC_FI_AM_FINTRANSACTIONS"
    }
  ]
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Name of the analytical dataset/entity set |
| `kind` | string | Type of object (typically "EntitySet") |
| `url` | string | Relative URL to access the dataset |

### Error Handling

| Status Code | Error Scenario | Handling Strategy |
|-------------|----------------|-------------------|
| 401 | Unauthorized - Invalid/expired token | Refresh OAuth2 token and retry |
| 403 | Forbidden - Insufficient permissions | Return clear permission error message |
| 404 | Space or asset not found | Validate space/asset existence first |
| 500 | Server error | Retry with exponential backoff |

### Usage Example
```python
# List analytical datasets in Financial Transactions asset
datasets = list_analytical_datasets(
    space_id="SAP_CONTENT",
    asset_id="SAP_SC_FI_AM_FINTRANSACTIONS"
)
```

---

## Tool 2: `get_analytical_model`

### Purpose
Get the OData service document for a specific analytical model, showing available entity sets, dimensions, measures, and query capabilities.

### API Endpoint
```
GET /api/v1/datasphere/consumption/analytical/{spaceId}/{assetId}
```

### Authentication
- **Type**: OAuth2 Bearer Token
- **Scopes**: `DWC_CONSUMPTION` or equivalent read scope

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `spaceId` | string | Yes | Space identifier |
| `assetId` | string | Yes | Asset identifier |
| `$format` | string | No | Response format ("json" or "xml") |

### Response Format
```json
{
  "@odata.context": "$metadata",
  "value": [
    {
      "name": "SAP_SC_FI_AM_FINTRANSACTIONS",
      "kind": "EntitySet",
      "url": "SAP_SC_FI_AM_FINTRANSACTIONS"
    }
  ]
}
```

### Additional Metadata
The tool should also retrieve and parse the `$metadata` endpoint to provide:
- Entity type definitions
- Dimension properties
- Measure properties
- Navigation properties
- Aggregation capabilities

### Metadata Endpoint
```
GET /api/v1/datasphere/consumption/analytical/{spaceId}/{assetId}/$metadata
```

### Metadata Response (XML CSDL)
```xml
<?xml version="1.0" encoding="utf-8"?>
<edmx:Edmx Version="4.0" xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx">
  <edmx:DataServices>
    <Schema Namespace="SAP_CONTENT.SAP_SC_FI_AM_FINTRANSACTIONS">
      <EntityType Name="SAP_SC_FI_AM_FINTRANSACTIONSType">
        <Key>
          <PropertyRef Name="TransactionID"/>
        </Key>
        <Property Name="TransactionID" Type="Edm.String"/>
        <Property Name="Amount" Type="Edm.Decimal" sap:aggregation-role="measure"/>
        <Property Name="Currency" Type="Edm.String" sap:aggregation-role="dimension"/>
        <Property Name="AccountNumber" Type="Edm.String" sap:aggregation-role="dimension"/>
        <Property Name="TransactionDate" Type="Edm.Date" sap:aggregation-role="dimension"/>
      </EntityType>
      <EntityContainer Name="EntityContainer">
        <EntitySet Name="SAP_SC_FI_AM_FINTRANSACTIONS" EntityType="SAP_CONTENT.SAP_SC_FI_AM_FINTRANSACTIONS.SAP_SC_FI_AM_FINTRANSACTIONSType"/>
      </EntityContainer>
    </Schema>
  </edmx:DataServices>
</edmx:Edmx>
```

### Parsed Metadata Structure
```json
{
  "entity_sets": [
    {
      "name": "SAP_SC_FI_AM_FINTRANSACTIONS",
      "entity_type": "SAP_SC_FI_AM_FINTRANSACTIONSType",
      "dimensions": [
        {"name": "Currency", "type": "Edm.String"},
        {"name": "AccountNumber", "type": "Edm.String"},
        {"name": "TransactionDate", "type": "Edm.Date"}
      ],
      "measures": [
        {"name": "Amount", "type": "Edm.Decimal"}
      ],
      "keys": ["TransactionID"]
    }
  ]
}
```

### Error Handling

| Status Code | Error Scenario | Handling Strategy |
|-------------|----------------|-------------------|
| 401 | Unauthorized | Refresh token and retry |
| 404 | Model not found | Return clear error with available models |
| 500 | Server error | Retry with backoff |

---

## Tool 3: `query_analytical_data`

### Purpose
Execute OData queries on analytical models to retrieve aggregated data with dimensions and measures for business intelligence and reporting.

### API Endpoint
```
GET /api/v1/datasphere/consumption/analytical/{spaceId}/{assetId}/{entitySet}
```

### Authentication
- **Type**: OAuth2 Bearer Token
- **Scopes**: `DWC_CONSUMPTION` or equivalent read scope

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `spaceId` | string | Yes | Space identifier |
| `assetId` | string | Yes | Asset identifier |
| `entitySet` | string | Yes | Entity set name to query |
| `$select` | string | No | Comma-separated list of dimensions/measures to return |
| `$filter` | string | No | OData filter expression |
| `$expand` | string | No | Related entities to expand |
| `$top` | integer | No | Maximum number of results (default: 50, max: 10000) |
| `$skip` | integer | No | Number of results to skip |
| `$orderby` | string | No | Sort order (e.g., "Amount desc") |
| `$count` | boolean | No | Include total count in response |
| `$apply` | string | No | Aggregation transformations |

### OData Query Capabilities

#### 1. Column Selection (`$select`)
```
$select=Currency,AccountNumber,Amount
```

#### 2. Filtering (`$filter`)
```
$filter=Amount gt 1000 and Currency eq 'USD'
$filter=TransactionDate ge 2024-01-01
$filter=contains(AccountNumber, '1000')
```

**Supported Operators**:
- Comparison: `eq`, `ne`, `gt`, `ge`, `lt`, `le`
- Logical: `and`, `or`, `not`
- String: `contains`, `startswith`, `endswith`
- Date: Standard date comparisons

#### 3. Sorting (`$orderby`)
```
$orderby=Amount desc
$orderby=TransactionDate asc, Amount desc
```

#### 4. Pagination (`$top`, `$skip`)
```
$top=100&$skip=200
```

#### 5. Aggregation (`$apply`)
```
$apply=groupby((Currency), aggregate(Amount with sum as TotalAmount))
$apply=groupby((Currency,AccountNumber), aggregate(Amount with average as AvgAmount))
```

**Supported Aggregations**:
- `sum` - Sum of values
- `average` - Average value
- `min` - Minimum value
- `max` - Maximum value
- `count` - Count of records

### Response Format
```json
{
  "@odata.context": "$metadata#SAP_SC_FI_AM_FINTRANSACTIONS",
  "@odata.count": 1523,
  "value": [
    {
      "TransactionID": "TXN001",
      "Amount": 15000.50,
      "Currency": "USD",
      "AccountNumber": "1000100",
      "TransactionDate": "2024-01-15"
    },
    {
      "TransactionID": "TXN002",
      "Amount": 8500.00,
      "Currency": "EUR",
      "AccountNumber": "1000200",
      "TransactionDate": "2024-01-16"
    }
  ]
}
```

### Aggregated Response Format
```json
{
  "@odata.context": "$metadata#SAP_SC_FI_AM_FINTRANSACTIONS",
  "value": [
    {
      "Currency": "USD",
      "TotalAmount": 1250000.00,
      "TransactionCount": 450
    },
    {
      "Currency": "EUR",
      "TotalAmount": 980000.00,
      "TransactionCount": 320
    }
  ]
}
```

### Error Handling

| Status Code | Error Scenario | Handling Strategy |
|-------------|----------------|-------------------|
| 400 | Invalid OData query syntax | Parse error message and provide helpful feedback |
| 401 | Unauthorized | Refresh token and retry |
| 403 | Insufficient permissions | Return permission error |
| 404 | Entity set not found | Validate entity set name |
| 413 | Result set too large | Suggest using pagination or filters |
| 500 | Server error | Retry with backoff |

### Query Validation
Before executing queries, validate:
1. Entity set exists in the model
2. Selected fields are valid dimensions or measures
3. Filter expressions use valid operators
4. Aggregations are applied to measures only
5. Pagination parameters are within limits

### Performance Considerations
- **Large Result Sets**: Always use `$top` and `$skip` for pagination
- **Complex Filters**: Test filter performance with `$count` first
- **Aggregations**: Use `$apply` for server-side aggregation instead of client-side
- **Caching**: Cache metadata to avoid repeated `$metadata` calls

---

## Tool 4: `get_analytical_service_document`

### Purpose
Retrieve the OData service document that lists all available entity sets and their URLs for a specific analytical asset.

### API Endpoint
```
GET /api/v1/datasphere/consumption/analytical/{spaceId}/{assetId}
```

### Authentication
- **Type**: OAuth2 Bearer Token
- **Scopes**: `DWC_CONSUMPTION` or equivalent read scope

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `spaceId` | string | Yes | Space identifier |
| `assetId` | string | Yes | Asset identifier |
| `$format` | string | No | Response format ("json" or "xml") |

### Response Format
```json
{
  "@odata.context": "$metadata",
  "value": [
    {
      "name": "SAP_SC_FI_AM_FINTRANSACTIONS",
      "kind": "EntitySet",
      "url": "SAP_SC_FI_AM_FINTRANSACTIONS"
    }
  ]
}
```

### Enhanced Response
The tool should enrich the service document with additional information:

```json
{
  "service_root": "/api/v1/datasphere/consumption/analytical/SAP_CONTENT/SAP_SC_FI_AM_FINTRANSACTIONS",
  "metadata_url": "/api/v1/datasphere/consumption/analytical/SAP_CONTENT/SAP_SC_FI_AM_FINTRANSACTIONS/$metadata",
  "entity_sets": [
    {
      "name": "SAP_SC_FI_AM_FINTRANSACTIONS",
      "kind": "EntitySet",
      "url": "SAP_SC_FI_AM_FINTRANSACTIONS",
      "full_url": "/api/v1/datasphere/consumption/analytical/SAP_CONTENT/SAP_SC_FI_AM_FINTRANSACTIONS/SAP_SC_FI_AM_FINTRANSACTIONS",
      "description": "Financial Transactions Analytical Model"
    }
  ],
  "capabilities": {
    "supports_filter": true,
    "supports_select": true,
    "supports_expand": true,
    "supports_orderby": true,
    "supports_top": true,
    "supports_skip": true,
    "supports_count": true,
    "supports_apply": true,
    "max_top": 10000
  }
}
```

### Error Handling

| Status Code | Error Scenario | Handling Strategy |
|-------------|----------------|-------------------|
| 401 | Unauthorized | Refresh token and retry |
| 404 | Asset not found | Return clear error message |
| 500 | Server error | Retry with backoff |

---

## Common Implementation Patterns

### 1. OAuth2 Token Management
```python
class OAuth2TokenManager:
    def __init__(self, client_id, client_secret, token_url):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.access_token = None
        self.token_expiry = None
    
    def get_token(self):
        if self.access_token and self.token_expiry > datetime.now():
            return self.access_token
        return self.refresh_token()
    
    def refresh_token(self):
        # Implement OAuth2 client credentials flow
        pass
```

### 2. OData Query Builder
```python
class ODataQueryBuilder:
    def __init__(self, base_url):
        self.base_url = base_url
        self.params = {}
    
    def select(self, fields):
        self.params['$select'] = ','.join(fields)
        return self
    
    def filter(self, expression):
        self.params['$filter'] = expression
        return self
    
    def top(self, count):
        self.params['$top'] = count
        return self
    
    def skip(self, count):
        self.params['$skip'] = count
        return self
    
    def orderby(self, field, direction='asc'):
        self.params['$orderby'] = f"{field} {direction}"
        return self
    
    def build(self):
        query_string = '&'.join([f"{k}={v}" for k, v in self.params.items()])
        return f"{self.base_url}?{query_string}"
```

### 3. Pagination Handler
```python
def paginate_results(query_func, page_size=100, max_results=None):
    """
    Automatically paginate through large result sets
    """
    all_results = []
    skip = 0
    
    while True:
        results = query_func(top=page_size, skip=skip)
        
        if not results or len(results) == 0:
            break
        
        all_results.extend(results)
        
        if max_results and len(all_results) >= max_results:
            return all_results[:max_results]
        
        if len(results) < page_size:
            break
        
        skip += page_size
    
    return all_results
```

### 4. Metadata Parser
```python
def parse_analytical_metadata(csdl_xml):
    """
    Parse CSDL XML metadata to extract dimensions and measures
    """
    import xml.etree.ElementTree as ET
    
    namespaces = {
        'edmx': 'http://docs.oasis-open.org/odata/ns/edmx',
        'edm': 'http://docs.oasis-open.org/odata/ns/edm',
        'sap': 'http://www.sap.com/Protocols/SAPData'
    }
    
    root = ET.fromstring(csdl_xml)
    
    dimensions = []
    measures = []
    
    for prop in root.findall('.//edm:Property', namespaces):
        agg_role = prop.get('{http://www.sap.com/Protocols/SAPData}aggregation-role')
        
        if agg_role == 'dimension':
            dimensions.append({
                'name': prop.get('Name'),
                'type': prop.get('Type')
            })
        elif agg_role == 'measure':
            measures.append({
                'name': prop.get('Name'),
                'type': prop.get('Type')
            })
    
    return {
        'dimensions': dimensions,
        'measures': measures
    }
```

---

## Testing Strategy

### Unit Tests
1. **Token Management**: Test token refresh and expiry handling
2. **Query Building**: Test OData query construction
3. **Metadata Parsing**: Test CSDL XML parsing
4. **Error Handling**: Test all error scenarios

### Integration Tests
1. **List Datasets**: Verify dataset discovery works
2. **Get Model**: Verify service document retrieval
3. **Query Data**: Test various OData queries
4. **Pagination**: Test large result set handling
5. **Aggregation**: Test groupby and aggregate operations

### Performance Tests
1. **Large Queries**: Test with 10,000+ records
2. **Complex Filters**: Test multi-condition filters
3. **Aggregations**: Test groupby performance
4. **Concurrent Requests**: Test multiple simultaneous queries

---

## Security Considerations

1. **Token Security**: Never log or expose OAuth2 tokens
2. **Input Validation**: Validate all user inputs before building queries
3. **Query Injection**: Sanitize filter expressions to prevent injection
4. **Rate Limiting**: Implement client-side rate limiting
5. **Error Messages**: Don't expose sensitive information in errors

---

## Documentation Requirements

### Tool Documentation
Each tool should include:
- Purpose and use cases
- Parameter descriptions
- Response format examples
- Error handling guide
- Usage examples

### Query Guide
Create comprehensive OData query guide covering:
- Basic queries
- Filtering examples
- Aggregation patterns
- Pagination strategies
- Performance tips

### Integration Examples
Provide examples for:
- BI tool integration (Power BI, Tableau)
- Python data analysis (pandas)
- Excel integration
- Custom dashboard development

---

## Success Criteria

- ✅ Can list all analytical datasets in an asset
- ✅ Can retrieve analytical model metadata
- ✅ Can execute basic OData queries ($select, $filter, $top, $skip)
- ✅ Can handle aggregations and grouping
- ✅ Can retrieve dimension and measure data
- ✅ Proper error handling for invalid queries
- ✅ Pagination works for large result sets
- ✅ Performance is acceptable for typical queries

---

## Next Steps

After implementing Phase 4.1:
1. Test with real SAP Datasphere tenant
2. Validate with various analytical models
3. Performance benchmark with large datasets
4. Create usage documentation
5. Proceed to Phase 5: Relational Data Access

---

**Document Version**: 1.0  
**Last Updated**: December 9, 2025  
**Related Documents**:
- SAP_DATASPHERE_MCP_EXTRACTION_PLAN.md
- SAP_DATASPHERE_CATALOG_TOOLS_SPEC.md
- SAP_DATASPHERE_METADATA_TOOLS_SPEC.md
