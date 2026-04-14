# SAP Datasphere Metadata Extraction Tools - Detailed Specification

## Overview

This document provides complete API specifications and implementation guidance for the four metadata extraction tools in the SAP Datasphere MCP Server. These tools enable deep schema inspection for integration planning and data modeling.

---

## Tool 1: `get_consumption_metadata`

### Purpose
Get CSDL metadata for consumption models to understand the overall consumption service schema.

### API Endpoint Details

**Primary Endpoint**:
```
GET /api/v1/datasphere/consumption/$metadata
```

**Alternative Endpoints**:
```
GET /api/v1/datasphere/consumption/catalog/$metadata
GET /v1/dwc/catalog/$metadata (Legacy)
```

### Authentication
- **Type**: OAuth2 Bearer Token
- **Required Scopes**: Consumption read access

### Request Parameters
None - metadata endpoints don't accept query parameters

### Response Format
**Content-Type**: `application/xml` (CSDL format)

### Expected Response Structure
```xml
<?xml version="1.0" encoding="UTF-8"?>
<edmx:Edmx xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx" Version="4.0">
  <edmx:DataServices>
    <Schema xmlns="http://docs.oasis-open.org/odata/ns/edm" 
            Namespace="SAP.Datasphere.Consumption">
      
      <!-- Entity Types -->
      <EntityType Name="ConsumptionModel">
        <Key>
          <PropertyRef Name="spaceId"/>
          <PropertyRef Name="assetId"/>
        </Key>
        <Property Name="spaceId" Type="Edm.String" Nullable="false"/>
        <Property Name="assetId" Type="Edm.String" Nullable="false"/>
        <Property Name="name" Type="Edm.String"/>
        <Property Name="description" Type="Edm.String"/>
        <Property Name="modelType" Type="Edm.String"/>
        <NavigationProperty Name="dimensions" 
                          Type="Collection(SAP.Datasphere.Consumption.Dimension)"/>
        <NavigationProperty Name="measures" 
                          Type="Collection(SAP.Datasphere.Consumption.Measure)"/>
      </EntityType>
      
      <EntityType Name="Dimension">
        <Key>
          <PropertyRef Name="name"/>
        </Key>
        <Property Name="name" Type="Edm.String" Nullable="false"/>
        <Property Name="displayName" Type="Edm.String"/>
        <Property Name="dataType" Type="Edm.String"/>
        <Property Name="hierarchyName" Type="Edm.String"/>
      </EntityType>
      
      <EntityType Name="Measure">
        <Key>
          <PropertyRef Name="name"/>
        </Key>
        <Property Name="name" Type="Edm.String" Nullable="false"/>
        <Property Name="displayName" Type="Edm.String"/>
        <Property Name="dataType" Type="Edm.String"/>
        <Property Name="aggregation" Type="Edm.String"/>
        <Property Name="unit" Type="Edm.String"/>
      </EntityType>
      
      <!-- Entity Container -->
      <EntityContainer Name="ConsumptionService">
        <EntitySet Name="ConsumptionModels" 
                   EntityType="SAP.Datasphere.Consumption.ConsumptionModel"/>
      </EntityContainer>
      
    </Schema>
  </edmx:DataServices>
</edmx:Edmx>
```

### Parsed Metadata Structure

When parsed, the metadata provides:

**Entity Types**: ConsumptionModel, Dimension, Measure, Hierarchy
**Properties**: Name, data type, nullable flag, max length, precision/scale
**Navigation Properties**: Relationships between entities
**Entity Sets**: Available collections (ConsumptionModels, Dimensions, Measures)
**Complex Types**: Nested structures for advanced metadata

### Use Cases
- Understand consumption service schema
- Identify available entity types
- Plan data integration mappings
- Generate client code
- Validate API requests

---

## Tool 2: `get_analytical_metadata`

### Purpose
Retrieve CSDL metadata for analytical models with dimensions, measures, and hierarchies.

### API Endpoint Details

**Primary Endpoint**:
```
GET /api/v1/datasphere/consumption/analytical/{spaceId}/{assetId}/$metadata
```

**Alternative Endpoint (Legacy)**:
```
GET /v1/dwc/consumption/analytical/{spaceId}/{assetId}/$metadata
```

### Authentication
- **Type**: OAuth2 Bearer Token
- **Required Scopes**: Analytical consumption access

### Path Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `spaceId` | string | Yes | Space identifier | `SAP_CONTENT` |
| `assetId` | string | Yes | Asset identifier | `SAP_SC_FI_AM_FINTRANSACTIONS` |

### Response Format
**Content-Type**: `application/xml` (CSDL format)

### Expected Response Structure
```xml
<?xml version="1.0" encoding="UTF-8"?>
<edmx:Edmx xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx" Version="4.0">
  <edmx:DataServices>
    <Schema xmlns="http://docs.oasis-open.org/odata/ns/edm" 
            Namespace="SAP_CONTENT.SAP_SC_FI_AM_FINTRANSACTIONS">
      
      <!-- Main Result Set Entity -->
      <EntityType Name="ResultSet">
        <Key>
          <PropertyRef Name="ID"/>
        </Key>
        <Property Name="ID" Type="Edm.String" Nullable="false"/>
        
        <!-- Dimensions -->
        <Property Name="AccountID" Type="Edm.String" 
                  sap:label="Account" sap:dimension="true"/>
        <Property Name="AccountName" Type="Edm.String" 
                  sap:label="Account Name" sap:dimension="true"/>
        <Property Name="CompanyCode" Type="Edm.String" 
                  sap:label="Company Code" sap:dimension="true"/>
        <Property Name="FiscalYear" Type="Edm.Int32" 
                  sap:label="Fiscal Year" sap:dimension="true"/>
        <Property Name="FiscalPeriod" Type="Edm.Int32" 
                  sap:label="Fiscal Period" sap:dimension="true"/>
        <Property Name="PostingDate" Type="Edm.Date" 
                  sap:label="Posting Date" sap:dimension="true"/>
        
        <!-- Measures -->
        <Property Name="TransactionAmount" Type="Edm.Decimal" 
                  Precision="15" Scale="2"
                  sap:label="Transaction Amount" 
                  sap:aggregation="SUM" 
                  sap:unit="Currency"/>
        <Property Name="Currency" Type="Edm.String" 
                  sap:label="Currency" sap:semantics="currency-code"/>
        <Property Name="TransactionCount" Type="Edm.Int32" 
                  sap:label="Transaction Count" 
                  sap:aggregation="COUNT"/>
        <Property Name="AverageAmount" Type="Edm.Decimal" 
                  Precision="15" Scale="2"
                  sap:label="Average Amount" 
                  sap:aggregation="AVG"/>
      </EntityType>
      
      <!-- Dimension Hierarchies -->
      <EntityType Name="AccountHierarchy">
        <Key>
          <PropertyRef Name="NodeID"/>
        </Key>
        <Property Name="NodeID" Type="Edm.String" Nullable="false"/>
        <Property Name="ParentNodeID" Type="Edm.String"/>
        <Property Name="Level" Type="Edm.Int32"/>
        <Property Name="AccountID" Type="Edm.String"/>
        <Property Name="AccountName" Type="Edm.String"/>
      </EntityType>
      
      <!-- Entity Container -->
      <EntityContainer Name="AnalyticalService">
        <EntitySet Name="ResultSet" 
                   EntityType="SAP_CONTENT.SAP_SC_FI_AM_FINTRANSACTIONS.ResultSet"/>
        <EntitySet Name="AccountHierarchy" 
                   EntityType="SAP_CONTENT.SAP_SC_FI_AM_FINTRANSACTIONS.AccountHierarchy"/>
      </EntityContainer>
      
    </Schema>
  </edmx:DataServices>
</edmx:Edmx>
```


### Parsed Analytical Metadata Structure

When parsed, provides:

**Dimensions**:
- Name and display label
- Data type
- Hierarchy associations
- Semantic annotations

**Measures**:
- Name and display label
- Data type with precision/scale
- Aggregation type (SUM, COUNT, AVG, MIN, MAX)
- Unit/currency associations
- Calculated measure formulas

**Hierarchies**:
- Hierarchy name
- Level definitions
- Parent-child relationships
- Drill-down paths

**Annotations**:
- SAP-specific metadata (sap:label, sap:dimension, sap:aggregation)
- Semantic types (currency-code, unit-of-measure)
- Display hints

### Use Cases
- BI tool integration
- OLAP cube design
- Dashboard creation
- Analytical query planning
- Dimension/measure discovery

---

## Tool 3: `get_relational_metadata`

### Purpose
Retrieve CSDL metadata for relational access with table/column definitions.

### API Endpoint Details

**Primary Endpoint**:
```
GET /api/v1/datasphere/consumption/relational/{spaceId}/{assetId}/$metadata
```

**Alternative Endpoint (Legacy)**:
```
GET /v1/dwc/consumption/relational/{spaceId}/{assetId}/$metadata
```

### Authentication
- **Type**: OAuth2 Bearer Token
- **Required Scopes**: Relational consumption access

### Path Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `spaceId` | string | Yes | Space identifier | `SAP_CONTENT` |
| `assetId` | string | Yes | Asset identifier | `SAP_SC_FI_AM_FINTRANSACTIONS` |

### Response Format
**Content-Type**: `application/xml` (CSDL format)

### Expected Response Structure
```xml
<?xml version="1.0" encoding="UTF-8"?>
<edmx:Edmx xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx" Version="4.0">
  <edmx:DataServices>
    <Schema xmlns="http://docs.oasis-open.org/odata/ns/edm" 
            Namespace="SAP_CONTENT.SAP_SC_FI_AM_FINTRANSACTIONS">
      
      <!-- Main Table Entity -->
      <EntityType Name="FinancialTransaction">
        <Key>
          <PropertyRef Name="TransactionID"/>
        </Key>
        
        <!-- Primary Key -->
        <Property Name="TransactionID" Type="Edm.String" 
                  Nullable="false" MaxLength="50"
                  sap:label="Transaction ID"/>
        
        <!-- Regular Columns -->
        <Property Name="AccountID" Type="Edm.String" 
                  MaxLength="10"
                  sap:label="Account ID"/>
        <Property Name="CompanyCode" Type="Edm.String" 
                  MaxLength="4"
                  sap:label="Company Code"/>
        <Property Name="PostingDate" Type="Edm.Date" 
                  sap:label="Posting Date"/>
        <Property Name="DocumentDate" Type="Edm.Date" 
                  sap:label="Document Date"/>
        <Property Name="FiscalYear" Type="Edm.Int32" 
                  sap:label="Fiscal Year"/>
        <Property Name="FiscalPeriod" Type="Edm.Int32" 
                  sap:label="Fiscal Period"/>
        
        <!-- Numeric Columns -->
        <Property Name="Amount" Type="Edm.Decimal" 
                  Precision="15" Scale="2"
                  sap:label="Amount"/>
        <Property Name="Currency" Type="Edm.String" 
                  MaxLength="3"
                  sap:label="Currency" 
                  sap:semantics="currency-code"/>
        <Property Name="Quantity" Type="Edm.Decimal" 
                  Precision="13" Scale="3"
                  sap:label="Quantity"/>
        <Property Name="Unit" Type="Edm.String" 
                  MaxLength="3"
                  sap:label="Unit" 
                  sap:semantics="unit-of-measure"/>
        
        <!-- Text Columns -->
        <Property Name="Description" Type="Edm.String" 
                  MaxLength="255"
                  sap:label="Description"/>
        <Property Name="Reference" Type="Edm.String" 
                  MaxLength="50"
                  sap:label="Reference"/>
        
        <!-- Audit Columns -->
        <Property Name="CreatedBy" Type="Edm.String" 
                  MaxLength="12"
                  sap:label="Created By"/>
        <Property Name="CreatedAt" Type="Edm.DateTimeOffset" 
                  sap:label="Created At"/>
        <Property Name="ModifiedBy" Type="Edm.String" 
                  MaxLength="12"
                  sap:label="Modified By"/>
        <Property Name="ModifiedAt" Type="Edm.DateTimeOffset" 
                  sap:label="Modified At"/>
        
        <!-- Navigation Properties (Foreign Keys) -->
        <NavigationProperty Name="Account" 
                          Type="SAP_CONTENT.AccountMaster"
                          Partner="Transactions"/>
        <NavigationProperty Name="Company" 
                          Type="SAP_CONTENT.CompanyCode"
                          Partner="Transactions"/>
      </EntityType>
      
      <!-- Entity Container -->
      <EntityContainer Name="RelationalService">
        <EntitySet Name="FinancialTransactions" 
                   EntityType="SAP_CONTENT.SAP_SC_FI_AM_FINTRANSACTIONS.FinancialTransaction"/>
      </EntityContainer>
      
    </Schema>
  </edmx:DataServices>
</edmx:Edmx>
```


### Parsed Relational Metadata Structure

When parsed, provides:

**Table Structure**:
- Table name (entity type)
- Primary key columns
- Column count

**Column Definitions**:
- Column name
- Data type (String, Int32, Decimal, Date, DateTimeOffset, Boolean)
- Nullable flag
- Max length (for strings)
- Precision and scale (for decimals)
- Display label

**Relationships**:
- Foreign key columns
- Referenced tables
- Relationship cardinality
- Join conditions

**Constraints**:
- Primary keys
- Unique constraints
- Check constraints (if defined)

**Semantic Annotations**:
- Currency codes
- Units of measure
- Temporal fields
- Audit fields

### Use Cases
- ETL planning
- Database schema mapping
- SQL query generation
- Data type validation
- Relational database integration

---

## Tool 4: `get_repository_search_metadata`

### Purpose
Get metadata for repository search functionality to understand searchable fields.

### API Endpoint Details

**Primary Endpoint**:
```
GET /deepsea/repository/search/$metadata
```

### Authentication
- **Type**: OAuth2 Bearer Token
- **Required Scopes**: Repository read access

### Request Parameters
None

### Response Format
**Content-Type**: `application/xml` (CSDL format)

### Expected Response Structure
```xml
<?xml version="1.0" encoding="UTF-8"?>
<edmx:Edmx xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx" Version="4.0">
  <edmx:DataServices>
    <Schema xmlns="http://docs.oasis-open.org/odata/ns/edm" 
            Namespace="SAP.Datasphere.Repository.Search">
      
      <!-- Repository Object Entity -->
      <EntityType Name="RepositoryObject">
        <Key>
          <PropertyRef Name="id"/>
        </Key>
        <Property Name="id" Type="Edm.String" Nullable="false"/>
        <Property Name="objectType" Type="Edm.String"/>
        <Property Name="name" Type="Edm.String"/>
        <Property Name="businessName" Type="Edm.String"/>
        <Property Name="description" Type="Edm.String"/>
        <Property Name="spaceId" Type="Edm.String"/>
        <Property Name="status" Type="Edm.String"/>
        <Property Name="deploymentStatus" Type="Edm.String"/>
        <Property Name="owner" Type="Edm.String"/>
        <Property Name="createdAt" Type="Edm.DateTimeOffset"/>
        <Property Name="modifiedAt" Type="Edm.DateTimeOffset"/>
        <Property Name="version" Type="Edm.String"/>
        <NavigationProperty Name="columns" 
                          Type="Collection(SAP.Datasphere.Repository.Search.Column)"/>
        <NavigationProperty Name="dependencies" 
                          Type="SAP.Datasphere.Repository.Search.Dependencies"/>
      </EntityType>
      
      <!-- Column Entity -->
      <EntityType Name="Column">
        <Key>
          <PropertyRef Name="name"/>
        </Key>
        <Property Name="name" Type="Edm.String" Nullable="false"/>
        <Property Name="dataType" Type="Edm.String"/>
        <Property Name="isPrimaryKey" Type="Edm.Boolean"/>
        <Property Name="isNullable" Type="Edm.Boolean"/>
        <Property Name="description" Type="Edm.String"/>
      </EntityType>
      
      <!-- Dependencies Complex Type -->
      <ComplexType Name="Dependencies">
        <Property Name="upstream" Type="Collection(Edm.String)"/>
        <Property Name="downstream" Type="Collection(Edm.String)"/>
      </ComplexType>
      
      <!-- Entity Container -->
      <EntityContainer Name="RepositorySearchService">
        <EntitySet Name="RepositoryObjects" 
                   EntityType="SAP.Datasphere.Repository.Search.RepositoryObject"/>
      </EntityContainer>
      
    </Schema>
  </edmx:DataServices>
</edmx:Edmx>
```

### Parsed Repository Search Metadata

When parsed, provides:

**Searchable Object Types**:
- Table
- View
- AnalyticalModel
- DataFlow
- Transformation
- StoredProcedure
- CalculationView
- Hierarchy

**Searchable Fields**:
- Object name (technical and business)
- Description
- Column names
- Column descriptions
- Tags
- Owner
- Space

**Available Filters**:
- objectType
- spaceId
- status
- deploymentStatus
- owner
- createdAt/modifiedAt date ranges

**Expandable Properties**:
- columns (column definitions)
- dependencies (upstream/downstream)
- lineage (data lineage information)

### Use Cases
- Understand repository search capabilities
- Plan search queries
- Identify searchable fields
- Build search interfaces
- Document search API

---

## Implementation Notes

### CSDL Parsing Best Practices

**XML Namespace Handling**:
```python
namespaces = {
    'edmx': 'http://docs.oasis-open.org/odata/ns/edmx',
    'edm': 'http://docs.oasis-open.org/odata/ns/edm',
    'sap': 'http://www.sap.com/Protocols/SAPData'
}
```

**Entity Type Extraction**:
```python
def extract_entity_types(root, namespaces):
    entity_types = []
    for entity_type in root.findall('.//edm:EntityType', namespaces):
        entity_types.append({
            'name': entity_type.get('Name'),
            'properties': extract_properties(entity_type, namespaces),
            'key_properties': extract_keys(entity_type, namespaces),
            'navigation_properties': extract_nav_props(entity_type, namespaces)
        })
    return entity_types
```

**Property Extraction**:
```python
def extract_properties(entity_type, namespaces):
    properties = []
    for prop in entity_type.findall('edm:Property', namespaces):
        prop_info = {
            'name': prop.get('Name'),
            'type': prop.get('Type'),
            'nullable': prop.get('Nullable', 'true') == 'true'
        }
        
        # Add type-specific attributes
        if 'String' in prop_info['type']:
            prop_info['max_length'] = prop.get('MaxLength')
        elif 'Decimal' in prop_info['type']:
            prop_info['precision'] = prop.get('Precision')
            prop_info['scale'] = prop.get('Scale')
        
        # Add SAP annotations
        sap_label = prop.get('{http://www.sap.com/Protocols/SAPData}label')
        if sap_label:
            prop_info['label'] = sap_label
        
        properties.append(prop_info)
    return properties
```


### Dimension and Measure Identification

**Analytical Metadata Parsing**:
```python
def identify_dimensions_and_measures(entity_type, namespaces):
    dimensions = []
    measures = []
    
    for prop in entity_type.findall('edm:Property', namespaces):
        prop_name = prop.get('Name')
        
        # Check SAP annotations
        is_dimension = prop.get('{http://www.sap.com/Protocols/SAPData}dimension') == 'true'
        aggregation = prop.get('{http://www.sap.com/Protocols/SAPData}aggregation')
        
        if is_dimension:
            dimensions.append({
                'name': prop_name,
                'type': prop.get('Type'),
                'label': prop.get('{http://www.sap.com/Protocols/SAPData}label')
            })
        elif aggregation:
            measures.append({
                'name': prop_name,
                'type': prop.get('Type'),
                'aggregation': aggregation,
                'label': prop.get('{http://www.sap.com/Protocols/SAPData}label'),
                'unit': prop.get('{http://www.sap.com/Protocols/SAPData}unit')
            })
    
    return dimensions, measures
```

### Data Type Mapping

**OData to SQL Type Mapping**:
```python
ODATA_TO_SQL_TYPE_MAP = {
    'Edm.String': 'VARCHAR',
    'Edm.Int32': 'INTEGER',
    'Edm.Int64': 'BIGINT',
    'Edm.Decimal': 'DECIMAL',
    'Edm.Double': 'DOUBLE',
    'Edm.Boolean': 'BOOLEAN',
    'Edm.Date': 'DATE',
    'Edm.DateTimeOffset': 'TIMESTAMP',
    'Edm.Time': 'TIME',
    'Edm.Guid': 'UUID'
}

def map_odata_type_to_sql(odata_type, precision=None, scale=None, max_length=None):
    base_type = ODATA_TO_SQL_TYPE_MAP.get(odata_type, 'VARCHAR')
    
    if base_type == 'VARCHAR' and max_length:
        return f'VARCHAR({max_length})'
    elif base_type == 'DECIMAL' and precision and scale:
        return f'DECIMAL({precision},{scale})'
    
    return base_type
```

### Metadata Caching

**Cache Strategy**:
```python
from functools import lru_cache
from datetime import datetime, timedelta

class MetadataCache:
    def __init__(self, ttl_minutes=60):
        self.cache = {}
        self.ttl = timedelta(minutes=ttl_minutes)
    
    def get(self, key):
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                return data
            else:
                del self.cache[key]
        return None
    
    def set(self, key, data):
        self.cache[key] = (data, datetime.now())
    
    def clear(self):
        self.cache.clear()

# Usage
metadata_cache = MetadataCache(ttl_minutes=60)

def get_cached_metadata(space_id, asset_id, metadata_type):
    cache_key = f"{metadata_type}:{space_id}:{asset_id}"
    cached = metadata_cache.get(cache_key)
    
    if cached:
        return cached
    
    # Fetch fresh metadata
    metadata = fetch_metadata(space_id, asset_id, metadata_type)
    metadata_cache.set(cache_key, metadata)
    
    return metadata
```

---

## Testing Checklist

### Functional Testing
- ✅ Test consumption metadata retrieval
- ✅ Test analytical metadata for various models
- ✅ Test relational metadata for tables and views
- ✅ Test repository search metadata
- ✅ Test XML parsing accuracy
- ✅ Test with complex analytical models
- ✅ Test with large tables (many columns)
- ✅ Test dimension/measure identification
- ✅ Test hierarchy extraction
- ✅ Test navigation property parsing

### Data Type Testing
- ✅ Test all OData data types
- ✅ Test decimal precision/scale
- ✅ Test string max length
- ✅ Test date/time types
- ✅ Test nullable vs non-nullable
- ✅ Test complex types

### Annotation Testing
- ✅ Test SAP-specific annotations
- ✅ Test semantic annotations (currency, unit)
- ✅ Test display labels
- ✅ Test aggregation types
- ✅ Test dimension flags

### Performance Testing
- ✅ Test metadata retrieval time
- ✅ Test XML parsing performance
- ✅ Test caching effectiveness
- ✅ Test concurrent metadata requests

### Integration Testing
- ✅ Test metadata → data query workflow
- ✅ Test with different asset types
- ✅ Test with different user permissions
- ✅ Test error handling for invalid assets

---

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| 404 Not Found | Asset doesn't exist | Verify space and asset IDs |
| 403 Forbidden | No access to asset | Check user permissions |
| 400 Bad Request | Invalid path parameters | Validate space/asset ID format |
| 500 Internal Error | Service unavailable | Retry with exponential backoff |

### XML Parsing Errors

```python
def safe_parse_metadata(xml_content):
    try:
        root = ET.fromstring(xml_content)
        return parse_csdl(root)
    except ET.ParseError as e:
        return {
            'error': 'XML parsing failed',
            'message': str(e),
            'line': e.position[0] if hasattr(e, 'position') else None
        }
    except Exception as e:
        return {
            'error': 'Metadata parsing failed',
            'message': str(e)
        }
```

---

## Metadata Comparison

### Compare Analytical vs Relational

```python
def compare_metadata(analytical_metadata, relational_metadata):
    """Compare analytical and relational metadata for same asset"""
    comparison = {
        'common_fields': [],
        'analytical_only': [],
        'relational_only': [],
        'type_differences': []
    }
    
    analytical_fields = {p['name']: p for p in analytical_metadata['properties']}
    relational_fields = {p['name']: p for p in relational_metadata['properties']}
    
    # Find common fields
    common_names = set(analytical_fields.keys()) & set(relational_fields.keys())
    comparison['common_fields'] = list(common_names)
    
    # Find unique fields
    comparison['analytical_only'] = list(set(analytical_fields.keys()) - common_names)
    comparison['relational_only'] = list(set(relational_fields.keys()) - common_names)
    
    # Check type differences
    for name in common_names:
        if analytical_fields[name]['type'] != relational_fields[name]['type']:
            comparison['type_differences'].append({
                'field': name,
                'analytical_type': analytical_fields[name]['type'],
                'relational_type': relational_fields[name]['type']
            })
    
    return comparison
```

---

## Metadata Documentation Generation

### Generate Schema Documentation

```python
def generate_schema_documentation(metadata):
    """Generate human-readable schema documentation"""
    doc = {
        'entity_name': metadata['entity_type']['name'],
        'description': metadata.get('description', 'No description available'),
        'columns': []
    }
    
    for prop in metadata['entity_type']['properties']:
        column_doc = {
            'name': prop['name'],
            'display_name': prop.get('label', prop['name']),
            'data_type': format_data_type(prop),
            'nullable': prop.get('nullable', True),
            'description': prop.get('description', ''),
            'is_key': prop['name'] in metadata['entity_type']['key_properties']
        }
        
        # Add analytical-specific info
        if prop.get('aggregation'):
            column_doc['aggregation'] = prop['aggregation']
            column_doc['column_type'] = 'Measure'
        elif prop.get('dimension'):
            column_doc['column_type'] = 'Dimension'
        else:
            column_doc['column_type'] = 'Attribute'
        
        doc['columns'].append(column_doc)
    
    return doc

def format_data_type(prop):
    """Format data type with precision/scale"""
    data_type = prop['type'].replace('Edm.', '')
    
    if data_type == 'String' and prop.get('max_length'):
        return f"String({prop['max_length']})"
    elif data_type == 'Decimal' and prop.get('precision'):
        scale = prop.get('scale', 0)
        return f"Decimal({prop['precision']},{scale})"
    
    return data_type
```

---

## Next Steps

1. Implement these four metadata extraction tools
2. Add comprehensive XML parsing
3. Test with various asset types
4. Implement metadata caching
5. Create schema documentation generator
6. Proceed to Phase 3.2: Repository Object Discovery
