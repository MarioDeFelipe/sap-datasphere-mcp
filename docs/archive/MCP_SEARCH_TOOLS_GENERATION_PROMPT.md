# MCP Search Tools Generation Prompt for SAP Datasphere

## Context

You are extending the SAP Datasphere MCP Server with universal search capabilities. This prompt will guide you to generate three powerful search tools that enable AI assistants to discover objects across the entire Datasphere catalog and repository.

---

## Prerequisites

Ensure you have completed Phase 2.1 (Basic Catalog Tools) before implementing these search tools. You should have:
- Working OAuth2 authentication
- DatasphereClient class
- Basic catalog browsing tools

---

## Tool Specifications

### Tool 1: `search_catalog`

**Purpose**: Universal search across all catalog objects using advanced search syntax

**API Endpoint**: `GET /deepsea/catalog/v1/search/search/$all`

**Input Parameters**:
```python
from typing import Optional, List, Literal
from pydantic import BaseModel, Field

class SearchCatalogInput(BaseModel):
    """Input for catalog search"""
    query: str = Field(
        ...,
        description="Search query with scope and keywords (e.g., 'SCOPE:comsapcatalogsearchprivateSearchAll financial')"
    )
    top: Optional[int] = Field(
        50,
        description="Maximum number of results to return",
        ge=1,
        le=500
    )
    skip: Optional[int] = Field(
        0,
        description="Number of results to skip for pagination",
        ge=0
    )
    include_count: bool = Field(
        False,
        description="Include total count of results"
    )
    include_why_found: bool = Field(
        False,
        description="Include relevance explanation for each result"
    )
    facets: Optional[str] = Field(
        None,
        description="Facet fields for filtering (e.g., 'all' or 'objectType,spaceId')"
    )
    facet_limit: Optional[int] = Field(
        10,
        description="Maximum facet values per field",
        ge=1,
        le=50
    )
```

**Implementation Template**:
```python
@mcp.tool()
def search_catalog(
    query: str,
    top: int = 50,
    skip: int = 0,
    include_count: bool = False,
    include_why_found: bool = False,
    facets: Optional[str] = None,
    facet_limit: int = 10
) -> str:
    """
    Universal search across all catalog objects in SAP Datasphere.
    
    This tool provides powerful full-text search capabilities across all catalog
    objects including KPIs, assets, spaces, models, views, and tables. Uses
    advanced search syntax with scopes and operators.
    
    Args:
        query: Search query with scope and keywords
               Format: "SCOPE:<scope_name> <search_terms>"
               
               Available scopes:
               - comsapcatalogsearchprivateSearchAll: All objects
               - comsapcatalogsearchprivateSearchKPIsAdmin: KPIs only
               - comsapcatalogsearchprivateSearchAssets: Data assets
               - comsapcatalogsearchprivateSearchSpaces: Spaces
               - comsapcatalogsearchprivateSearchModels: Analytical models
               - comsapcatalogsearchprivateSearchViews: Views
               - comsapcatalogsearchprivateSearchTables: Tables
               
               Search operators:
               - * : Wildcard (all objects)
               - AND : Both terms must match
               - OR : Either term matches
               - NOT : Exclude term
               - "..." : Exact phrase
               - field:value : Search specific field
        
        top: Maximum results to return (default: 50, max: 500)
        skip: Results to skip for pagination (default: 0)
        include_count: Include total count of results (default: False)
        include_why_found: Include relevance explanation (default: False)
        facets: Facet fields for filtering (e.g., 'all' or 'objectType,spaceId')
        facet_limit: Max facet values per field (default: 10)
    
    Returns:
        JSON string containing search results with optional facets and relevance info
    
    Examples:
        # Search all objects for "financial"
        search_catalog(query="SCOPE:comsapcatalogsearchprivateSearchAll financial")
        
        # Search KPIs with wildcard
        search_catalog(query="SCOPE:comsapcatalogsearchprivateSearchKPIsAdmin *")
        
        # Search with facets
        search_catalog(
            query="SCOPE:comsapcatalogsearchprivateSearchAssets customer",
            facets="all",
            include_count=True
        )
        
        # Search with boolean operators
        search_catalog(query="SCOPE:comsapcatalogsearchprivateSearchAll sales OR revenue")
    """
    try:
        # Build query parameters
        params = {
            "$top": top,
            "$skip": skip
        }
        
        # Add search query using $apply filter
        search_filter = f"filter(Search.search(query='{query}'))"
        params["$apply"] = search_filter
        
        if include_count:
            params["$count"] = "true"
        
        if include_why_found:
            params["whyfound"] = "true"
        
        if facets:
            params["facets"] = facets
            params["facetlimit"] = facet_limit
        
        # Make API request
        response = datasphere_client.get(
            "/deepsea/catalog/v1/search/search/$all",
            params=params
        )
        
        # Parse and format results
        results = []
        for item in response.get("value", []):
            result = {
                "id": item.get("id"),
                "object_type": item.get("objectType"),
                "name": item.get("name"),
                "technical_name": item.get("technicalName"),
                "description": item.get("description"),
                "space_id": item.get("spaceId"),
                "space_name": item.get("spaceName"),
                "owner": item.get("owner"),
                "created_at": item.get("createdAt"),
                "modified_at": item.get("modifiedAt"),
                "tags": item.get("tags", []),
                "relevance_score": item.get("relevanceScore")
            }
            
            # Add consumption URLs if available
            if item.get("consumptionUrls"):
                result["consumption_urls"] = item.get("consumptionUrls")
            
            # Add why found explanation if requested
            if include_why_found and item.get("whyFound"):
                result["why_found"] = {
                    "matched_fields": item["whyFound"].get("matchedFields", []),
                    "matched_terms": item["whyFound"].get("matchedTerms", []),
                    "explanation": item["whyFound"].get("explanation")
                }
            
            results.append(result)
        
        # Build response
        search_response = {
            "query": query,
            "results": results,
            "returned_count": len(results),
            "has_more": len(results) == top
        }
        
        # Add total count if requested
        if include_count and "@odata.count" in response:
            search_response["total_count"] = response["@odata.count"]
        
        # Add facets if requested
        if facets and "facets" in response:
            search_response["facets"] = response["facets"]
        
        return json.dumps(search_response, indent=2)
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            return json.dumps({
                "error": "Invalid search query syntax",
                "message": "Check query format and scope name"
            })
        elif e.response.status_code == 403:
            return json.dumps({
                "error": "Access denied",
                "message": "User lacks catalog search permission"
            })
        else:
            return json.dumps({"error": f"HTTP error: {e.response.status_code}"})
    except Exception as e:
        return json.dumps({"error": f"Search failed: {str(e)}"})
```

---

### Tool 2: `search_repository`

**Purpose**: Global search across all repository objects

**API Endpoint**: `GET /deepsea/repository/search/$all`

**Input Parameters**:
```python
class SearchRepositoryInput(BaseModel):
    """Input for repository search"""
    search_terms: str = Field(
        ...,
        description="Search terms to find in repository objects"
    )
    object_types: Optional[List[str]] = Field(
        None,
        description="Filter by object types (e.g., ['Table', 'View', 'DataFlow'])"
    )
    space_id: Optional[str] = Field(
        None,
        description="Filter by specific space"
    )
    include_dependencies: bool = Field(
        False,
        description="Include object dependencies in results"
    )
    include_lineage: bool = Field(
        False,
        description="Include data lineage information"
    )
    top: Optional[int] = Field(50, ge=1, le=500)
    skip: Optional[int] = Field(0, ge=0)
```

**Implementation Template**:
```python
@mcp.tool()
def search_repository(
    search_terms: str,
    object_types: Optional[List[str]] = None,
    space_id: Optional[str] = None,
    include_dependencies: bool = False,
    include_lineage: bool = False,
    top: int = 50,
    skip: int = 0
) -> str:
    """
    Global search across all repository objects in SAP Datasphere.
    
    This tool searches through all repository objects including tables, views,
    analytical models, data flows, and transformations. Provides comprehensive
    object discovery with lineage and dependency information.
    
    Args:
        search_terms: Search terms to find in object names, descriptions, columns
        object_types: Filter by object types (e.g., ['Table', 'View', 'DataFlow'])
        space_id: Filter by specific space (e.g., 'SAP_CONTENT')
        include_dependencies: Include upstream/downstream dependencies
        include_lineage: Include data lineage information
        top: Maximum results to return (default: 50, max: 500)
        skip: Results to skip for pagination (default: 0)
    
    Returns:
        JSON string containing repository objects matching search criteria
    
    Examples:
        # Search for financial objects
        search_repository(search_terms="financial")
        
        # Search for tables only
        search_repository(
            search_terms="customer",
            object_types=["Table"]
        )
        
        # Search with dependencies
        search_repository(
            search_terms="transactions",
            include_dependencies=True,
            include_lineage=True
        )
        
        # Search in specific space
        search_repository(
            search_terms="sales",
            space_id="SAP_CONTENT"
        )
    """
    try:
        # Build query parameters
        params = {
            "search": search_terms,
            "$top": top,
            "$skip": skip
        }
        
        # Build filter expression
        filters = []
        
        if object_types:
            type_filters = " or ".join([f"objectType eq '{t}'" for t in object_types])
            filters.append(f"({type_filters})")
        
        if space_id:
            filters.append(f"spaceId eq '{space_id}'")
        
        if filters:
            params["$filter"] = " and ".join(filters)
        
        # Add expand for dependencies and lineage
        expand_fields = []
        if include_dependencies:
            expand_fields.append("dependencies")
        if include_lineage:
            expand_fields.append("lineage")
        
        if expand_fields:
            params["$expand"] = ",".join(expand_fields)
        
        # Make API request
        response = datasphere_client.get(
            "/deepsea/repository/search/$all",
            params=params
        )
        
        # Parse and format results
        objects = []
        for item in response.get("value", []):
            obj = {
                "id": item.get("id"),
                "object_type": item.get("objectType"),
                "name": item.get("name"),
                "business_name": item.get("businessName"),
                "description": item.get("description"),
                "space_id": item.get("spaceId"),
                "status": item.get("status"),
                "deployment_status": item.get("deploymentStatus"),
                "owner": item.get("owner"),
                "created_at": item.get("createdAt"),
                "modified_at": item.get("modifiedAt"),
                "version": item.get("version")
            }
            
            # Add columns if available
            if item.get("columns"):
                obj["columns"] = [
                    {
                        "name": col.get("name"),
                        "data_type": col.get("dataType"),
                        "is_primary_key": col.get("isPrimaryKey", False),
                        "description": col.get("description")
                    }
                    for col in item["columns"]
                ]
            
            # Add dependencies if requested
            if include_dependencies and item.get("dependencies"):
                obj["dependencies"] = {
                    "upstream": item["dependencies"].get("upstream", []),
                    "downstream": item["dependencies"].get("downstream", [])
                }
            
            # Add lineage if requested
            if include_lineage and item.get("lineage"):
                obj["lineage"] = item["lineage"]
            
            objects.append(obj)
        
        result = {
            "search_terms": search_terms,
            "objects": objects,
            "returned_count": len(objects),
            "has_more": len(objects) == top
        }
        
        return json.dumps(result, indent=2)
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            return json.dumps({
                "error": "Invalid search parameters",
                "message": "Check filter syntax and object types"
            })
        elif e.response.status_code == 403:
            return json.dumps({
                "error": "Access denied",
                "message": "User lacks repository access"
            })
        else:
            return json.dumps({"error": f"HTTP error: {e.response.status_code}"})
    except Exception as e:
        return json.dumps({"error": f"Repository search failed: {str(e)}"})
```

---

### Tool 3: `get_catalog_metadata`

**Purpose**: Get CSDL metadata for catalog service

**API Endpoints**: 
- `GET /api/v1/datasphere/consumption/$metadata`
- `GET /api/v1/datasphere/consumption/catalog/$metadata`
- `GET /v1/dwc/catalog/$metadata` (Legacy)

**Input Parameters**:
```python
class GetCatalogMetadataInput(BaseModel):
    """Input for getting catalog metadata"""
    endpoint_type: Literal["consumption", "catalog", "legacy"] = Field(
        "catalog",
        description="Which metadata endpoint to use"
    )
    parse_metadata: bool = Field(
        True,
        description="Parse XML into structured format"
    )
```

**Implementation Template**:
```python
@mcp.tool()
def get_catalog_metadata(
    endpoint_type: Literal["consumption", "catalog", "legacy"] = "catalog",
    parse_metadata: bool = True
) -> str:
    """
    Get CSDL metadata for the SAP Datasphere catalog service.
    
    This tool retrieves the OData metadata document (CSDL XML) that describes
    the catalog service schema including entity types, properties, relationships,
    and available operations. Essential for understanding the catalog structure.
    
    Args:
        endpoint_type: Which metadata endpoint to use
                      - "consumption": /api/v1/datasphere/consumption/$metadata
                      - "catalog": /api/v1/datasphere/consumption/catalog/$metadata
                      - "legacy": /v1/dwc/catalog/$metadata
        parse_metadata: Parse XML into structured JSON format (default: True)
    
    Returns:
        JSON string containing parsed metadata or raw XML
    
    Examples:
        # Get catalog metadata (parsed)
        get_catalog_metadata()
        
        # Get consumption metadata
        get_catalog_metadata(endpoint_type="consumption")
        
        # Get raw XML
        get_catalog_metadata(parse_metadata=False)
    """
    try:
        # Select endpoint based on type
        endpoints = {
            "consumption": "/api/v1/datasphere/consumption/$metadata",
            "catalog": "/api/v1/datasphere/consumption/catalog/$metadata",
            "legacy": "/v1/dwc/catalog/$metadata"
        }
        
        endpoint = endpoints[endpoint_type]
        
        # Make API request
        # Note: Metadata endpoints return XML, not JSON
        url = f"{datasphere_client.config.base_url.rstrip('/')}{endpoint}"
        response = datasphere_client.session.get(url, timeout=30)
        response.raise_for_status()
        
        xml_content = response.text
        
        if not parse_metadata:
            # Return raw XML
            return json.dumps({
                "endpoint_type": endpoint_type,
                "format": "XML (CSDL)",
                "content": xml_content
            }, indent=2)
        
        # Parse XML metadata
        import xml.etree.ElementTree as ET
        
        root = ET.fromstring(xml_content)
        
        # Define namespaces
        namespaces = {
            'edmx': 'http://docs.oasis-open.org/odata/ns/edmx',
            'edm': 'http://docs.oasis-open.org/odata/ns/edm'
        }
        
        metadata = {
            "endpoint_type": endpoint_type,
            "entity_types": [],
            "entity_sets": [],
            "navigation_properties": []
        }
        
        # Extract entity types
        for entity_type in root.findall('.//edm:EntityType', namespaces):
            entity_name = entity_type.get('Name')
            
            # Extract properties
            properties = []
            for prop in entity_type.findall('edm:Property', namespaces):
                properties.append({
                    'name': prop.get('Name'),
                    'type': prop.get('Type'),
                    'nullable': prop.get('Nullable', 'true') == 'true',
                    'max_length': prop.get('MaxLength')
                })
            
            # Extract key properties
            key_props = []
            key_element = entity_type.find('edm:Key', namespaces)
            if key_element is not None:
                for prop_ref in key_element.findall('edm:PropertyRef', namespaces):
                    key_props.append(prop_ref.get('Name'))
            
            # Extract navigation properties
            nav_props = []
            for nav_prop in entity_type.findall('edm:NavigationProperty', namespaces):
                nav_props.append({
                    'name': nav_prop.get('Name'),
                    'type': nav_prop.get('Type'),
                    'partner': nav_prop.get('Partner')
                })
            
            metadata['entity_types'].append({
                'name': entity_name,
                'key_properties': key_props,
                'properties': properties,
                'navigation_properties': nav_props
            })
        
        # Extract entity sets
        for entity_set in root.findall('.//edm:EntitySet', namespaces):
            metadata['entity_sets'].append({
                'name': entity_set.get('Name'),
                'entity_type': entity_set.get('EntityType')
            })
        
        return json.dumps(metadata, indent=2)
        
    except requests.exceptions.HTTPError as e:
        return json.dumps({
            "error": f"HTTP error: {e.response.status_code}",
            "message": "Failed to retrieve metadata"
        })
    except ET.ParseError as e:
        return json.dumps({
            "error": "XML parsing failed",
            "message": str(e)
        })
    except Exception as e:
        return json.dumps({"error": f"Metadata retrieval failed: {str(e)}"})
```

---

## Helper Functions

### Search Query Builder
```python
def build_catalog_search_query(
    scope: str,
    search_terms: str,
    operators: Optional[dict] = None
) -> str:
    """
    Build a properly formatted catalog search query.
    
    Args:
        scope: Search scope (e.g., 'SearchAll', 'SearchKPIsAdmin')
        search_terms: Search terms
        operators: Optional dict with AND, OR, NOT terms
    
    Returns:
        Formatted search query string
    """
    # Full scope name
    full_scope = f"comsapcatalogsearchprivate{scope}"
    
    # Build query with operators
    if operators:
        terms = []
        if operators.get('and_terms'):
            terms.append(" AND ".join(operators['and_terms']))
        if operators.get('or_terms'):
            terms.append(" OR ".join(operators['or_terms']))
        if operators.get('not_terms'):
            terms.append(" NOT " + " NOT ".join(operators['not_terms']))
        
        search_terms = " ".join(terms) if terms else search_terms
    
    return f"SCOPE:{full_scope} {search_terms}"
```

### Facet Formatter
```python
def format_facets(facets: dict) -> dict:
    """Format facet results for better readability"""
    formatted = {}
    
    for facet_name, facet_values in facets.items():
        formatted[facet_name] = {
            'display_name': facet_name.replace('_', ' ').title(),
            'values': [
                {
                    'value': item['value'],
                    'count': item['count'],
                    'label': format_facet_value(item['value'])
                }
                for item in facet_values
            ]
        }
    
    return formatted
```

---

## Testing Examples

### Test search_catalog
```python
# Basic search
result = search_catalog(
    query="SCOPE:comsapcatalogsearchprivateSearchAll financial"
)

# Search with facets
result = search_catalog(
    query="SCOPE:comsapcatalogsearchprivateSearchAssets *",
    facets="all",
    facet_limit=10,
    include_count=True
)

# Search KPIs
result = search_catalog(
    query="SCOPE:comsapcatalogsearchprivateSearchKPIsAdmin revenue",
    include_why_found=True
)

# Boolean search
result = search_catalog(
    query="SCOPE:comsapcatalogsearchprivateSearchAll (sales OR revenue) AND NOT archived"
)
```

### Test search_repository
```python
# Basic repository search
result = search_repository(search_terms="customer")

# Search with filters
result = search_repository(
    search_terms="transaction",
    object_types=["Table", "View"],
    space_id="SAP_CONTENT"
)

# Search with dependencies
result = search_repository(
    search_terms="financial",
    include_dependencies=True,
    include_lineage=True
)
```

### Test get_catalog_metadata
```python
# Get parsed metadata
result = get_catalog_metadata()

# Get raw XML
result = get_catalog_metadata(parse_metadata=False)

# Get consumption metadata
result = get_catalog_metadata(endpoint_type="consumption")
```

---

## Success Criteria

✅ All three search tools implemented and working  
✅ Catalog search with all scopes functioning  
✅ Repository search with filtering working  
✅ Metadata retrieval and parsing successful  
✅ Faceted search capabilities implemented  
✅ Search result ranking working  
✅ Boolean operators (AND, OR, NOT) supported  
✅ Pagination implemented for large result sets  
✅ Error handling for invalid queries  
✅ Documentation complete  
✅ Unit tests passing  
✅ Integration tests with real tenant passing  

---

## Next Steps After Implementation

1. Test search tools with real SAP Datasphere tenant
2. Optimize search query performance
3. Implement search result caching
4. Add search history and suggestions
5. Create search syntax documentation
6. Proceed to Phase 3: Metadata & Schema Discovery tools
