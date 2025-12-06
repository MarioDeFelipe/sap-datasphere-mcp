# SAP Datasphere Search Tools - Detailed Specification

## Overview

This document provides complete API specifications and implementation guidance for the three universal search tools in the SAP Datasphere MCP Server.

---

## Tool 1: `search_catalog`

### Purpose
Universal search across all catalog objects in SAP Datasphere using advanced search syntax.

### API Endpoint Details

**Primary Endpoint**:
```
GET /deepsea/catalog/v1/search/search/$all
```

### Authentication
- **Type**: OAuth2 Bearer Token
- **Required Scopes**: Catalog search access

### Request Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `query` | string | Yes | Search query with scope and keywords | `SCOPE:comsapcatalogsearchprivateSearchKPIsAdmin *` |
| `$top` | integer | No | Maximum results to return | `50` |
| `$skip` | integer | No | Results to skip (pagination) | `0` |
| `$count` | boolean | No | Include total count | `true` |
| `whyfound` | boolean | No | Include relevance explanation | `true` |
| `facets` | string | No | Facet fields for filtering | `all` or `objectType,spaceId` |
| `facetlimit` | integer | No | Max facet values per field | `10` |
| `$apply` | string | No | Advanced filtering | `filter(Search.search(query='...'))` |

### Search Query Syntax

**Basic Format**:
```
SCOPE:<scope_name> <search_terms>
```

**Available Scopes**:

- `comsapcatalogsearchprivateSearchKPIsAdmin` - Search KPIs
- `comsapcatalogsearchprivateSearchAll` - Search all catalog objects
- `comsapcatalogsearchprivateSearchAssets` - Search data assets
- `comsapcatalogsearchprivateSearchSpaces` - Search spaces
- `comsapcatalogsearchprivateSearchModels` - Search analytical models
- `comsapcatalogsearchprivateSearchViews` - Search views
- `comsapcatalogsearchprivateSearchTables` - Search tables

**Search Term Syntax**:
- `*` - Wildcard (all objects)
- `"exact phrase"` - Exact phrase match
- `term1 AND term2` - Both terms must match
- `term1 OR term2` - Either term matches
- `term1 NOT term2` - First term but not second
- `field:value` - Search specific field

**Example Queries**:
```
# Search all KPIs
SCOPE:comsapcatalogsearchprivateSearchKPIsAdmin *

# Search for financial assets
SCOPE:comsapcatalogsearchprivateSearchAssets financial

# Search for sales-related objects
SCOPE:comsapcatalogsearchprivateSearchAll sales OR revenue

# Search in specific space
SCOPE:comsapcatalogsearchprivateSearchAssets spaceId:SAP_CONTENT

# Search with exact phrase
SCOPE:comsapcatalogsearchprivateSearchAll "customer master data"
```

### Response Format
**Content-Type**: `application/json`

### Expected Response Structure
```json
{
  "@odata.context": "$metadata#search",
  "@odata.count": 125,
  "value": [
    {
      "id": "asset-12345",
      "objectType": "AnalyticalModel",
      "name": "Financial Transactions",
      "technicalName": "SAP_SC_FI_AM_FINTRANSACTIONS",
      "description": "Comprehensive financial transaction data with account information",
      "spaceId": "SAP_CONTENT",
      "spaceName": "SAP Content",
      "owner": "SYSTEM",
      "createdAt": "2024-01-15T10:30:00Z",
      "modifiedAt": "2024-11-20T14:22:00Z",
      "tags": ["finance", "transactions", "analytical"],
      "relevanceScore": 0.95,
      "whyFound": {
        "matchedFields": ["name", "description", "tags"],
        "matchedTerms": ["financial", "transactions"],
        "explanation": "Matched on name and description fields with high relevance"
      },
      "consumptionUrls": {
        "analytical": "/api/v1/datasphere/consumption/analytical/SAP_CONTENT/SAP_SC_FI_AM_FINTRANSACTIONS",
        "relational": "/api/v1/datasphere/consumption/relational/SAP_CONTENT/SAP_SC_FI_AM_FINTRANSACTIONS"
      }
    },
    {
      "id": "asset-67890",
      "objectType": "View",
      "name": "Customer Financial Summary",
      "technicalName": "CUSTOMER_FIN_SUMMARY_VIEW",
      "description": "Aggregated customer financial data",
      "spaceId": "FINANCE_SPACE",
      "spaceName": "Finance Analytics",
      "owner": "FIN_ADMIN",
      "createdAt": "2024-03-10T08:15:00Z",
      "modifiedAt": "2024-10-05T16:45:00Z",
      "tags": ["customer", "finance", "summary"],
      "relevanceScore": 0.87,
      "whyFound": {
        "matchedFields": ["name", "tags"],
        "matchedTerms": ["financial"],
        "explanation": "Matched on name field"
      }
    }
  ],
  "facets": {
    "objectType": [
      {"value": "AnalyticalModel", "count": 45},
      {"value": "View", "count": 38},
      {"value": "Table", "count": 32},
      {"value": "DataFlow", "count": 10}
    ],
    "spaceId": [
      {"value": "SAP_CONTENT", "count": 67},
      {"value": "FINANCE_SPACE", "count": 28},
      {"value": "SALES_SPACE", "count": 20},
      {"value": "HR_SPACE", "count": 10}
    ],
    "owner": [
      {"value": "SYSTEM", "count": 67},
      {"value": "FIN_ADMIN", "count": 28},
      {"value": "SALES_ADMIN", "count": 20}
    ]
  }
}
```

### Error Responses

| Status Code | Description | Example Response |
|-------------|-------------|------------------|
| 400 | Bad Request - Invalid query syntax | `{"error": "invalid_query", "message": "Invalid search scope"}` |
| 401 | Unauthorized | `{"error": "unauthorized", "message": "Token expired"}` |
| 403 | Forbidden | `{"error": "forbidden", "message": "No search permission"}` |
| 500 | Internal Server Error | `{"error": "internal_error", "message": "Search service unavailable"}` |

### Use Cases
- Universal object discovery across all types
- Full-text search for data assets
- Find objects by business terms
- Discover related objects
- Build searchable data catalogs

---

## Tool 2: `search_repository`

### Purpose
Global search across all repository objects including design-time and runtime objects.

### API Endpoint Details

**Primary Endpoint**:
```
GET /deepsea/repository/search/$all
```

### Authentication
- **Type**: OAuth2 Bearer Token
- **Required Scopes**: Repository read access

### Request Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `search` | string | Yes | Search terms | `financial transactions` |
| `$select` | string | No | Fields to return | `name,type,spaceId` |
| `$filter` | string | No | OData filter expression | `objectType eq 'Table'` |
| `$expand` | string | No | Expand related entities | `dependencies,lineage` |
| `$top` | integer | No | Maximum results | `50` |
| `$skip` | integer | No | Results to skip | `0` |
| `facets` | string | No | Facet fields | `objectType,spaceId,status` |

### Search Capabilities

**Searchable Object Types**:
- Tables
- Views
- Analytical Models
- Data Flows
- Transformations
- Stored Procedures
- Calculation Views
- Hierarchies

**Searchable Fields**:
- Object name (technical and business)
- Description
- Column names
- Column descriptions
- Tags
- Owner
- Space

### Response Format
**Content-Type**: `application/json`

### Expected Response Structure
```json
{
  "@odata.context": "$metadata#repository/search",
  "value": [
    {
      "id": "repo-obj-12345",
      "objectType": "Table",
      "name": "FINANCIAL_TRANSACTIONS",
      "businessName": "Financial Transactions Table",
      "description": "Core financial transaction data",
      "spaceId": "SAP_CONTENT",
      "status": "Active",
      "deploymentStatus": "Deployed",
      "owner": "SYSTEM",
      "createdAt": "2024-01-15T10:30:00Z",
      "modifiedAt": "2024-11-20T14:22:00Z",
      "version": "2.1",
      "columns": [
        {
          "name": "TRANSACTION_ID",
          "dataType": "NVARCHAR(50)",
          "isPrimaryKey": true,
          "description": "Unique transaction identifier"
        },
        {
          "name": "AMOUNT",
          "dataType": "DECIMAL(15,2)",
          "description": "Transaction amount"
        }
      ],
      "dependencies": {
        "upstream": ["SOURCE_SYSTEM_TABLE"],
        "downstream": ["FIN_ANALYTICS_VIEW", "FIN_REPORT_MODEL"]
      },
      "lineage": {
        "sourceSystem": "SAP_ERP",
        "loadFrequency": "Daily",
        "lastLoaded": "2024-12-04T02:00:00Z"
      }
    },
    {
      "id": "repo-obj-67890",
      "objectType": "DataFlow",
      "name": "LOAD_FINANCIAL_DATA",
      "businessName": "Financial Data Load Process",
      "description": "ETL process for loading financial transactions",
      "spaceId": "SAP_CONTENT",
      "status": "Active",
      "deploymentStatus": "Deployed",
      "owner": "ETL_ADMIN",
      "createdAt": "2024-02-20T09:15:00Z",
      "modifiedAt": "2024-10-10T14:30:00Z",
      "version": "1.5",
      "sourceObjects": ["ERP_TRANSACTIONS"],
      "targetObjects": ["FINANCIAL_TRANSACTIONS"],
      "transformations": [
        "Currency conversion",
        "Data validation",
        "Duplicate removal"
      ]
    }
  ],
  "facets": {
    "objectType": [
      {"value": "Table", "count": 150},
      {"value": "View", "count": 120},
      {"value": "DataFlow", "count": 45},
      {"value": "AnalyticalModel", "count": 38}
    ],
    "spaceId": [
      {"value": "SAP_CONTENT", "count": 200},
      {"value": "FINANCE_SPACE", "count": 80},
      {"value": "SALES_SPACE", "count": 73}
    ],
    "status": [
      {"value": "Active", "count": 320},
      {"value": "Inactive", "count": 25},
      {"value": "Draft", "count": 8}
    ]
  }
}
```

### Common Filter Examples

**Filter by object type**:
```
$filter=objectType eq 'Table'
$filter=objectType eq 'View' or objectType eq 'AnalyticalModel'
```

**Filter by deployment status**:
```
$filter=deploymentStatus eq 'Deployed'
$filter=status eq 'Active' and deploymentStatus eq 'Deployed'
```

**Filter by space**:
```
$filter=spaceId eq 'SAP_CONTENT'
```

**Combine search and filter**:
```
search=financial&$filter=objectType eq 'Table' and spaceId eq 'SAP_CONTENT'
```

### Error Responses

| Status Code | Description | Example Response |
|-------------|-------------|------------------|
| 400 | Bad Request | `{"error": "invalid_filter", "message": "Invalid OData filter syntax"}` |
| 401 | Unauthorized | `{"error": "unauthorized", "message": "Token expired"}` |
| 403 | Forbidden | `{"error": "forbidden", "message": "No repository access"}` |
| 500 | Internal Server Error | `{"error": "internal_error", "message": "Repository service unavailable"}` |

### Use Cases
- Find repository objects by name or description
- Discover data lineage and dependencies
- Impact analysis for changes
- Object inventory and documentation
- ETL process discovery

---

## Tool 3: `get_catalog_metadata`

### Purpose
Get CSDL metadata for the catalog service to understand available entities and operations.

### API Endpoint Details

**Primary Endpoints**:
```
GET /api/v1/datasphere/consumption/$metadata
GET /api/v1/datasphere/consumption/catalog/$metadata
GET /v1/dwc/catalog/$metadata (Legacy)
```

### Authentication
- **Type**: OAuth2 Bearer Token
- **Required Scopes**: Catalog read access

### Request Parameters
None - metadata endpoints don't accept query parameters

### Response Format
**Content-Type**: `application/xml` (CSDL format)

### Expected Response Structure
```xml
<?xml version="1.0" encoding="UTF-8"?>
<edmx:Edmx xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx" Version="4.0">
  <edmx:DataServices>
    <Schema xmlns="http://docs.oasis-open.org/odata/ns/edm" Namespace="SAP.Datasphere.Catalog">
      
      <!-- Entity Types -->
      <EntityType Name="Space">
        <Key>
          <PropertyRef Name="id"/>
        </Key>
        <Property Name="id" Type="Edm.String" Nullable="false"/>
        <Property Name="name" Type="Edm.String"/>
        <Property Name="displayName" Type="Edm.String"/>
        <Property Name="description" Type="Edm.String"/>
        <Property Name="owner" Type="Edm.String"/>
        <Property Name="createdAt" Type="Edm.DateTimeOffset"/>
        <Property Name="modifiedAt" Type="Edm.DateTimeOffset"/>
        <NavigationProperty Name="assets" Type="Collection(SAP.Datasphere.Catalog.Asset)"/>
      </EntityType>
      
      <EntityType Name="Asset">
        <Key>
          <PropertyRef Name="spaceId"/>
          <PropertyRef Name="id"/>
        </Key>
        <Property Name="id" Type="Edm.String" Nullable="false"/>
        <Property Name="spaceId" Type="Edm.String" Nullable="false"/>
        <Property Name="name" Type="Edm.String"/>
        <Property Name="technicalName" Type="Edm.String"/>
        <Property Name="description" Type="Edm.String"/>
        <Property Name="assetType" Type="Edm.String"/>
        <Property Name="exposedForConsumption" Type="Edm.Boolean"/>
        <Property Name="analyticalConsumptionUrl" Type="Edm.String"/>
        <Property Name="relationalConsumptionUrl" Type="Edm.String"/>
        <Property Name="createdAt" Type="Edm.DateTimeOffset"/>
        <Property Name="modifiedAt" Type="Edm.DateTimeOffset"/>
        <NavigationProperty Name="space" Type="SAP.Datasphere.Catalog.Space"/>
      </EntityType>
      
      <!-- Entity Container -->
      <EntityContainer Name="CatalogService">
        <EntitySet Name="spaces" EntityType="SAP.Datasphere.Catalog.Space">
          <NavigationPropertyBinding Path="assets" Target="assets"/>
        </EntitySet>
        <EntitySet Name="assets" EntityType="SAP.Datasphere.Catalog.Asset">
          <NavigationPropertyBinding Path="space" Target="spaces"/>
        </EntitySet>
      </EntityContainer>
      
    </Schema>
  </edmx:DataServices>
</edmx:Edmx>
```

### Parsed Metadata Information

The metadata provides:

**Entity Types**:
- Space
- Asset
- Dimension
- Measure
- Relationship

**Properties per Entity**:
- Property name
- Data type (Edm.String, Edm.Int32, Edm.Boolean, etc.)
- Nullable flag
- Max length (for strings)
- Precision/Scale (for decimals)

**Navigation Properties**:
- Relationship name
- Target entity type
- Cardinality (one-to-one, one-to-many, many-to-many)

**Entity Sets** (Collections):
- spaces
- assets
- dimensions
- measures

**Operations** (Functions/Actions):
- Available service operations
- Input parameters
- Return types

### Use Cases
- Understand catalog service schema
- Generate client code
- Validate API requests
- Build type-safe integrations
- Document available entities and properties
- Plan data model mappings

### Error Responses

| Status Code | Description | Example Response |
|-------------|-------------|------------------|
| 401 | Unauthorized | XML error response |
| 403 | Forbidden | XML error response |
| 404 | Not Found | XML error response |
| 500 | Internal Server Error | XML error response |

---

## Implementation Notes

### Search Query Optimization

**Best Practices**:
1. Use specific scopes to narrow search domain
2. Implement pagination for large result sets
3. Use facets to enable drill-down filtering
4. Cache search results when appropriate
5. Implement search result ranking

**Performance Tips**:
```python
# Use pagination
page_size = 50
results = search_catalog(
    query="SCOPE:comsapcatalogsearchprivateSearchAll financial",
    top=page_size,
    skip=0
)

# Use facets for filtering
results = search_catalog(
    query="SCOPE:comsapcatalogsearchprivateSearchAssets *",
    facets="objectType,spaceId",
    facetlimit=10
)

# Request relevance explanation
results = search_catalog(
    query="SCOPE:comsapcatalogsearchprivateSearchAll customer",
    whyfound=True
)
```

### CSDL Metadata Parsing

**XML Parsing Example**:
```python
import xml.etree.ElementTree as ET

def parse_csdl_metadata(xml_content: str) -> dict:
    """Parse CSDL XML metadata into structured format"""
    root = ET.fromstring(xml_content)
    
    # Define namespaces
    namespaces = {
        'edmx': 'http://docs.oasis-open.org/odata/ns/edmx',
        'edm': 'http://docs.oasis-open.org/odata/ns/edm'
    }
    
    metadata = {
        'entity_types': [],
        'entity_sets': [],
        'navigation_properties': []
    }
    
    # Extract entity types
    for entity_type in root.findall('.//edm:EntityType', namespaces):
        entity_name = entity_type.get('Name')
        properties = []
        
        for prop in entity_type.findall('edm:Property', namespaces):
            properties.append({
                'name': prop.get('Name'),
                'type': prop.get('Type'),
                'nullable': prop.get('Nullable', 'true') == 'true'
            })
        
        metadata['entity_types'].append({
            'name': entity_name,
            'properties': properties
        })
    
    return metadata
```

### Faceted Search Implementation

**Facet Processing**:
```python
def process_facets(facets: dict) -> dict:
    """Process and format facet results for UI"""
    formatted_facets = {}
    
    for facet_name, facet_values in facets.items():
        formatted_facets[facet_name] = {
            'display_name': format_facet_name(facet_name),
            'values': [
                {
                    'value': item['value'],
                    'count': item['count'],
                    'percentage': calculate_percentage(item['count'], total_count)
                }
                for item in facet_values
            ]
        }
    
    return formatted_facets
```

### Search Result Ranking

**Relevance Scoring**:
```python
def rank_search_results(results: list) -> list:
    """Rank search results by relevance"""
    # Sort by relevance score (if provided)
    if 'relevanceScore' in results[0]:
        results.sort(key=lambda x: x.get('relevanceScore', 0), reverse=True)
    
    # Apply custom ranking factors
    for result in results:
        score = result.get('relevanceScore', 0)
        
        # Boost exact name matches
        if result.get('exactMatch'):
            score *= 1.5
        
        # Boost recently modified objects
        if is_recently_modified(result.get('modifiedAt')):
            score *= 1.2
        
        # Boost objects with descriptions
        if result.get('description'):
            score *= 1.1
        
        result['adjustedScore'] = score
    
    # Re-sort by adjusted score
    results.sort(key=lambda x: x.get('adjustedScore', 0), reverse=True)
    
    return results
```

---

## Testing Checklist

### Functional Testing
- ✅ Test catalog search with various scopes
- ✅ Test repository search with different object types
- ✅ Test metadata retrieval and parsing
- ✅ Test pagination for large result sets
- ✅ Test faceted search and filtering
- ✅ Test search with special characters
- ✅ Test empty search results
- ✅ Test invalid search syntax

### Performance Testing
- ✅ Test search response time with large catalogs
- ✅ Test pagination performance
- ✅ Test concurrent search requests
- ✅ Test metadata parsing performance
- ✅ Test facet calculation performance

### Search Quality Testing
- ✅ Test relevance ranking accuracy
- ✅ Test exact phrase matching
- ✅ Test wildcard searches
- ✅ Test boolean operators (AND, OR, NOT)
- ✅ Test field-specific searches
- ✅ Test multi-term searches

### Integration Testing
- ✅ Test search → get details workflow
- ✅ Test facet filtering → refined search
- ✅ Test metadata → entity discovery → search
- ✅ Test with different user permissions

---

## Search Syntax Reference

### Catalog Search Scopes

| Scope | Description | Example |
|-------|-------------|---------|
| `SearchAll` | All catalog objects | `SCOPE:...SearchAll financial` |
| `SearchKPIsAdmin` | KPIs only | `SCOPE:...SearchKPIsAdmin revenue` |
| `SearchAssets` | Data assets | `SCOPE:...SearchAssets customer` |
| `SearchSpaces` | Spaces | `SCOPE:...SearchSpaces SAP` |
| `SearchModels` | Analytical models | `SCOPE:...SearchModels sales` |
| `SearchViews` | Views | `SCOPE:...SearchViews transaction` |
| `SearchTables` | Tables | `SCOPE:...SearchTables master` |

### Search Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `*` | Wildcard | `SCOPE:...SearchAll *` |
| `AND` | Both terms | `customer AND transaction` |
| `OR` | Either term | `sales OR revenue` |
| `NOT` | Exclude term | `financial NOT archived` |
| `"..."` | Exact phrase | `"master data"` |
| `field:value` | Field search | `spaceId:SAP_CONTENT` |

### Facet Fields

| Field | Description | Values |
|-------|-------------|--------|
| `objectType` | Object type | AnalyticalModel, View, Table, etc. |
| `spaceId` | Space identifier | SAP_CONTENT, FINANCE_SPACE, etc. |
| `owner` | Object owner | SYSTEM, ADMIN, etc. |
| `status` | Object status | Active, Inactive, Draft |
| `tags` | Object tags | finance, sales, customer, etc. |

---

## Next Steps

1. Implement these three search tools in the MCP server
2. Add comprehensive unit tests for search syntax
3. Test with real SAP Datasphere tenant
4. Optimize search performance
5. Document search best practices
6. Proceed to Phase 3: Metadata & Schema Discovery tools
