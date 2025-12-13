# SAP Datasphere MCP Server - Phase 5.1 Relational Data Access Tools

## Overview

This document provides complete technical specifications for implementing **4 relational data consumption tools** that enable row-level data access, ETL operations, and detailed data analysis from SAP Datasphere.

**Phase**: 5.1 - Data Consumption (Relational)  
**Priority**: HIGH  
**Estimated Implementation Time**: 4-5 days  
**Tools Count**: 4

---

## Tool 1: `list_relational_datasets`

### Purpose
List all available relational datasets within a specific asset, showing tables and views that can be accessed in row-by-row fashion for detailed data analysis.

### API Endpoint
```
GET /api/v1/datasphere/consumption/relational/{spaceId}/{assetId}
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
| `name` | string | Name of the relational dataset/entity set |
| `kind` | string | Type of object (typically "EntitySet") |
| `url` | string | Relative URL to access the dataset |

---

## Tool 2: `get_relational_table`

### Purpose
Get the OData service document for a specific relational table, showing available entity sets, columns, data types, and query capabilities.

### API Endpoint
```
GET /api/v1/datasphere/consumption/relational/{spaceId}/{assetId}
```

### Authentication
- **Type**: OAuth2 Bearer Token
- **Scopes**: `DWC_CONSUMPTION` or equivalent read scope

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `spaceId` | string | Yes | Space identifier |
| `assetId` | string | Yes | Asset identifier |
| `include_metadata` | boolean | No | Include CSDL metadata parsing (default: True) |

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

### Metadata Endpoint
```
GET /api/v1/datasphere/consumption/relational/{spaceId}/{assetId}/$metadata
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
        <Property Name="TransactionID" Type="Edm.String" Nullable="false"/>
        <Property Name="Amount" Type="Edm.Decimal" Precision="15" Scale="2"/>
        <Property Name="Currency" Type="Edm.String" MaxLength="3"/>
        <Property Name="AccountNumber" Type="Edm.String" MaxLength="10"/>
        <Property Name="TransactionDate" Type="Edm.Date"/>
        <Property Name="Description" Type="Edm.String" MaxLength="255"/>
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
      "columns": [
        {
          "name": "TransactionID",
          "type": "Edm.String",
          "nullable": false,
          "is_key": true,
          "sql_type": "NVARCHAR"
        },
        {
          "name": "Amount",
          "type": "Edm.Decimal",
          "precision": 15,
          "scale": 2,
          "nullable": true,
          "sql_type": "DECIMAL(15,2)"
        },
        {
          "name": "Currency",
          "type": "Edm.String",
          "max_length": 3,
          "nullable": true,
          "sql_type": "NVARCHAR(3)"
        }
      ],
      "keys": ["TransactionID"],
      "row_count_estimate": 1500000
    }
  ]
}
```

---

## Tool 3: `query_relational_data`

### Purpose
Execute OData queries on relational tables to retrieve row-level data with filtering, sorting, and pagination for ETL operations and detailed analysis.

### API Endpoint
```
GET /api/v1/datasphere/consumption/relational/{spaceId}/{assetId}/{entitySet}
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
| `$select` | string | No | Comma-separated list of columns to return |
| `$filter` | string | No | OData filter expression |
| `$expand` | string | No | Related entities to expand |
| `$top` | integer | No | Maximum number of results (default: 100, max: 50000) |
| `$skip` | integer | No | Number of results to skip |
| `$orderby` | string | No | Sort order (e.g., "TransactionDate desc") |
| `$count` | boolean | No | Include total count in response |

### OData Query Capabilities

#### 1. Column Selection (`$select`)
```
$select=TransactionID,Amount,Currency,TransactionDate
```

#### 2. Filtering (`$filter`)
```
$filter=Amount gt 1000 and Currency eq 'USD'
$filter=TransactionDate ge 2024-01-01 and TransactionDate le 2024-12-31
$filter=contains(Description, 'Payment')
$filter=AccountNumber in ('1000100','1000200','1000300')
```

**Supported Operators**:
- Comparison: `eq`, `ne`, `gt`, `ge`, `lt`, `le`
- Logical: `and`, `or`, `not`
- String: `contains`, `startswith`, `endswith`
- Collection: `in`
- Date: Standard date comparisons

#### 3. Sorting (`$orderby`)
```
$orderby=TransactionDate desc
$orderby=Amount desc, TransactionDate asc
$orderby=Currency asc, AccountNumber asc
```

#### 4. Pagination (`$top`, `$skip`)
```
$top=1000&$skip=5000
```

**Note**: Relational queries support larger page sizes than analytical queries for ETL operations.

### Response Format
```json
{
  "@odata.context": "$metadata#SAP_SC_FI_AM_FINTRANSACTIONS",
  "@odata.count": 1523456,
  "value": [
    {
      "TransactionID": "TXN001",
      "Amount": 15000.50,
      "Currency": "USD",
      "AccountNumber": "1000100",
      "TransactionDate": "2024-01-15",
      "Description": "Payment to Vendor ABC"
    },
    {
      "TransactionID": "TXN002",
      "Amount": 8500.00,
      "Currency": "EUR",
      "AccountNumber": "1000200",
      "TransactionDate": "2024-01-16",
      "Description": "Invoice Settlement"
    }
  ]
}
```

### Large Dataset Handling
For ETL operations with large datasets:

```json
{
  "@odata.context": "$metadata#SAP_SC_FI_AM_FINTRANSACTIONS",
  "@odata.count": 15234567,
  "@odata.nextLink": "$skip=50000&$top=50000",
  "value": [
    // 50,000 records
  ],
  "etl_metadata": {
    "batch_size": 50000,
    "total_batches": 305,
    "current_batch": 1,
    "estimated_completion_time": "2024-12-09T16:30:00Z"
  }
}
```

---

## Tool 4: `get_relational_service_document`

### Purpose
Retrieve the OData service document that lists all available entity sets and their URLs for a specific relational asset, with enhanced capability information for ETL planning.

### API Endpoint
```
GET /api/v1/datasphere/consumption/relational/{spaceId}/{assetId}
```

### Authentication
- **Type**: OAuth2 Bearer Token
- **Scopes**: `DWC_CONSUMPTION` or equivalent read scope

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `spaceId` | string | Yes | Space identifier |
| `assetId` | string | Yes | Asset identifier |

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
```json
{
  "service_root": "/api/v1/datasphere/consumption/relational/SAP_CONTENT/SAP_SC_FI_AM_FINTRANSACTIONS",
  "metadata_url": "/api/v1/datasphere/consumption/relational/SAP_CONTENT/SAP_SC_FI_AM_FINTRANSACTIONS/$metadata",
  "entity_sets": [
    {
      "name": "SAP_SC_FI_AM_FINTRANSACTIONS",
      "kind": "EntitySet",
      "url": "SAP_SC_FI_AM_FINTRANSACTIONS",
      "full_url": "/api/v1/datasphere/consumption/relational/SAP_CONTENT/SAP_SC_FI_AM_FINTRANSACTIONS/SAP_SC_FI_AM_FINTRANSACTIONS",
      "description": "Financial Transactions Relational Table",
      "estimated_row_count": 1500000,
      "last_updated": "2024-12-09T10:00:00Z"
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
    "max_top": 50000,
    "recommended_batch_size": 10000,
    "supports_streaming": true,
    "etl_optimized": true
  },
  "data_types": {
    "supported_types": ["Edm.String", "Edm.Decimal", "Edm.Date", "Edm.DateTime", "Edm.Boolean", "Edm.Int32", "Edm.Int64"],
    "type_mappings": {
      "Edm.String": "NVARCHAR",
      "Edm.Decimal": "DECIMAL",
      "Edm.Date": "DATE",
      "Edm.DateTime": "TIMESTAMP",
      "Edm.Boolean": "BOOLEAN",
      "Edm.Int32": "INTEGER",
      "Edm.Int64": "BIGINT"
    }
  }
}
```

---

## ETL-Specific Features

### Batch Processing Support
```python
def process_large_table(space_id, asset_id, entity_set, batch_size=10000):
    """Process large table in batches for ETL operations."""
    skip = 0
    total_processed = 0
    
    while True:
        batch = query_relational_data(
            space_id=space_id,
            asset_id=asset_id,
            entity_set=entity_set,
            top=batch_size,
            skip=skip,
            count=True
        )
        
        if not batch or len(batch) == 0:
            break
        
        # Process batch
        process_batch(batch)
        
        total_processed += len(batch)
        skip += batch_size
        
        # Progress tracking
        if total_processed % 100000 == 0:
            print(f"Processed {total_processed} records")
        
        if len(batch) < batch_size:
            break
    
    return total_processed
```

### Data Type Mapping
```python
def map_odata_to_sql_types(metadata):
    """Map OData types to SQL types for ETL target systems."""
    type_mapping = {
        'Edm.String': 'NVARCHAR',
        'Edm.Decimal': 'DECIMAL',
        'Edm.Date': 'DATE',
        'Edm.DateTime': 'TIMESTAMP',
        'Edm.Boolean': 'BOOLEAN',
        'Edm.Int32': 'INTEGER',
        'Edm.Int64': 'BIGINT'
    }
    
    sql_schema = []
    for column in metadata['columns']:
        sql_type = type_mapping.get(column['type'], 'NVARCHAR')
        
        if column['type'] == 'Edm.String' and 'max_length' in column:
            sql_type = f"NVARCHAR({column['max_length']})"
        elif column['type'] == 'Edm.Decimal' and 'precision' in column:
            sql_type = f"DECIMAL({column['precision']},{column.get('scale', 0)})"
        
        sql_schema.append({
            'name': column['name'],
            'sql_type': sql_type,
            'nullable': column.get('nullable', True),
            'is_key': column.get('is_key', False)
        })
    
    return sql_schema
```

---

## Performance Optimization

### Recommended Query Patterns

#### 1. Efficient Filtering
```
# Good: Use indexed columns for filtering
$filter=TransactionDate ge 2024-01-01 and AccountNumber eq '1000100'

# Avoid: Complex string operations on large datasets
$filter=contains(Description, 'payment') and contains(Description, 'vendor')
```

#### 2. Optimal Pagination
```
# For ETL: Use larger batch sizes
$top=10000&$skip=0

# For UI: Use smaller batch sizes
$top=100&$skip=0
```

#### 3. Column Selection
```
# Good: Select only needed columns
$select=TransactionID,Amount,Currency,TransactionDate

# Avoid: Select all columns for large tables
# (no $select parameter)
```

### Caching Strategy
```python
class RelationalDataCache:
    def __init__(self):
        self.metadata_cache = {}
        self.service_doc_cache = {}
    
    def get_cached_metadata(self, space_id, asset_id):
        key = f"{space_id}:{asset_id}"
        return self.metadata_cache.get(key)
    
    def cache_metadata(self, space_id, asset_id, metadata):
        key = f"{space_id}:{asset_id}"
        self.metadata_cache[key] = {
            'data': metadata,
            'cached_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(hours=1)
        }
```

---

## Error Handling

### Relational-Specific Errors

| Status Code | Error Scenario | Handling Strategy |
|-------------|----------------|-------------------|
| 400 | Invalid OData query | Parse error and provide query syntax help |
| 401 | Unauthorized | Refresh OAuth2 token and retry |
| 403 | Insufficient permissions | Return clear permission error |
| 404 | Table/entity not found | Validate entity set name |
| 413 | Result set too large | Suggest pagination or filtering |
| 429 | Rate limit exceeded | Implement exponential backoff |
| 500 | Server error | Retry with backoff, log for monitoring |

### Query Validation
```python
def validate_relational_query(entity_set, select, filter_expr, top, skip):
    """Validate OData query parameters before execution."""
    errors = []
    
    # Validate entity set
    if not entity_set or not entity_set.strip():
        errors.append("Entity set name is required")
    
    # Validate pagination
    if top and top > 50000:
        errors.append("Maximum $top value is 50000 for relational queries")
    
    if skip and skip < 0:
        errors.append("$skip value must be non-negative")
    
    # Validate filter syntax (basic check)
    if filter_expr:
        forbidden_keywords = ['drop', 'delete', 'update', 'insert']
        if any(keyword in filter_expr.lower() for keyword in forbidden_keywords):
            errors.append("Invalid filter expression contains forbidden keywords")
    
    return errors
```

---

## Success Criteria

- ✅ Can list all relational datasets in an asset
- ✅ Can retrieve relational table metadata with SQL type mapping
- ✅ Can execute row-level queries with filtering and sorting
- ✅ Can handle large result sets with efficient pagination
- ✅ Can process data in batches for ETL operations
- ✅ Proper error handling for all query scenarios
- ✅ Performance optimized for large datasets
- ✅ Data type mapping for target systems

---

## Integration Examples

### ETL Pipeline Integration
```python
def extract_table_to_warehouse(space_id, asset_id, entity_set, target_table):
    """Extract SAP Datasphere table to data warehouse."""
    
    # 1. Get table metadata
    metadata = get_relational_table(space_id, asset_id, include_metadata=True)
    
    # 2. Create target table schema
    sql_schema = map_odata_to_sql_types(metadata)
    create_target_table(target_table, sql_schema)
    
    # 3. Extract data in batches
    batch_size = 10000
    skip = 0
    
    while True:
        batch = query_relational_data(
            space_id=space_id,
            asset_id=asset_id,
            entity_set=entity_set,
            top=batch_size,
            skip=skip
        )
        
        if not batch:
            break
        
        # Load batch to target
        load_batch_to_warehouse(target_table, batch)
        
        skip += batch_size
        
        if len(batch) < batch_size:
            break
```

### Data Quality Validation
```python
def validate_data_quality(space_id, asset_id, entity_set):
    """Validate data quality of relational table."""
    
    # Check for null values in key columns
    null_check = query_relational_data(
        space_id=space_id,
        asset_id=asset_id,
        entity_set=entity_set,
        filter="TransactionID eq null",
        count=True
    )
    
    # Check for duplicate keys
    duplicate_check = query_relational_data(
        space_id=space_id,
        asset_id=asset_id,
        entity_set=entity_set,
        select="TransactionID",
        orderby="TransactionID"
    )
    
    return {
        'null_keys': null_check.get('@odata.count', 0),
        'total_records': len(duplicate_check),
        'quality_score': calculate_quality_score(null_check, duplicate_check)
    }
```

---

## Next Steps

After implementing Phase 5.1:
1. Test with real SAP Datasphere tenant
2. Validate with large datasets (1M+ records)
3. Performance benchmark ETL operations
4. Test data type mapping accuracy
5. Create ETL integration examples
6. Proceed to Phase 6.1: KPI Discovery & Analysis

---

**Document Version**: 1.0  
**Last Updated**: December 9, 2025  
**Related Documents**:
- SAP_DATASPHERE_MCP_EXTRACTION_PLAN.md
- SAP_DATASPHERE_ANALYTICAL_TOOLS_SPEC.md (similar pattern)
- EXTRACTION_PLAN_STATUS.md