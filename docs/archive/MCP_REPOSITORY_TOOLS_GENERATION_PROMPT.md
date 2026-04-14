# MCP Repository Object Discovery Tools Generation Prompt for SAP Datasphere

## Context

You are extending the SAP Datasphere MCP Server with repository object discovery capabilities. This prompt will guide you to generate three tools that enable AI assistants to explore design-time and runtime objects, understand dependencies, and perform impact analysis.

---

## Prerequisites

Ensure you have completed:
- Phase 2.1: Basic Catalog Tools
- Phase 2.2: Universal Search Tools
- Phase 3.1: Metadata Extraction Tools

You should have working OAuth2 authentication and DatasphereClient class.

---

## Tool Specifications

### Tool 1: `list_repository_objects`

**Purpose**: Browse all repository objects in a space

**API Endpoint**: `GET /deepsea/repository/{spaceId}/objects`

**Implementation Template**:
```python
from typing import Optional, List, Literal

@mcp.tool()
def list_repository_objects(
    space_id: str,
    object_types: Optional[List[str]] = None,
    status_filter: Optional[str] = None,
    include_dependencies: bool = False,
    top: int = 50,
    skip: int = 0
) -> str:
    """
    Browse all repository objects in a SAP Datasphere space.
    
    This tool retrieves all repository objects including tables, views,
    analytical models, data flows, and transformations with their metadata,
    dependencies, and lineage information.
    
    Args:
        space_id: Space identifier (e.g., 'SAP_CONTENT')
        object_types: Filter by object types (e.g., ['Table', 'View', 'DataFlow'])
        status_filter: Filter by status ('Active', 'Inactive', 'Draft')
        include_dependencies: Include dependency information (default: False)
        top: Maximum results to return (default: 50, max: 500)
        skip: Results to skip for pagination (default: 0)
    
    Returns:
        JSON string containing repository objects with metadata
    
    Examples:
        # List all objects in space
        list_repository_objects(space_id="SAP_CONTENT")
        
        # List only tables
        list_repository_objects(
            space_id="SAP_CONTENT",
            object_types=["Table"]
        )
        
        # List with dependencies
        list_repository_objects(
            space_id="SAP_CONTENT",
            include_dependencies=True
        )
        
        # List active data flows
        list_repository_objects(
            space_id="SAP_CONTENT",
            object_types=["DataFlow"],
            status_filter="Active"
        )
    """
    try:
        # Build endpoint URL
        endpoint = f"/deepsea/repository/{space_id}/objects"
        
        # Build query parameters
        params = {
            "$top": top,
            "$skip": skip
        }
        
        # Build filter expression
        filters = []
        
        if object_types:
            type_filters = " or ".join([f"objectType eq '{t}'" for t in object_types])
            filters.append(f"({type_filters})")
        
        if status_filter:
            filters.append(f"status eq '{status_filter}'")
        
        if filters:
            params["$filter"] = " and ".join(filters)
        
        # Add expand for dependencies
        if include_dependencies:
            params["$expand"] = "dependencies"
        
        # Make API request
        response = datasphere_client.get(endpoint, params=params)
        
        # Parse and format results
        objects = []
        for item in response.get("value", []):
            obj = {
                "id": item.get("id"),
                "object_type": item.get("objectType"),
                "name": item.get("name"),
                "business_name": item.get("businessName"),
                "technical_name": item.get("technicalName"),
                "description": item.get("description"),
                "space_id": item.get("spaceId"),
                "space_name": item.get("spaceName"),
                "status": item.get("status"),
                "deployment_status": item.get("deploymentStatus"),
                "owner": item.get("owner"),
                "created_by": item.get("createdBy"),
                "created_at": item.get("createdAt"),
                "modified_by": item.get("modifiedBy"),
                "modified_at": item.get("modifiedAt"),
                "version": item.get("version"),
                "package_name": item.get("packageName"),
                "tags": item.get("tags", [])
            }
            
            # Add type-specific information
            if item.get("objectType") == "Table":
                obj["column_count"] = len(item.get("columns", []))
                obj["row_count"] = item.get("metadata", {}).get("rowCount")
            elif item.get("objectType") == "View":
                obj["based_on"] = item.get("basedOn", [])
            elif item.get("objectType") == "AnalyticalModel":
                obj["dimensions"] = item.get("dimensions", [])
                obj["measures"] = item.get("measures", [])
            elif item.get("objectType") == "DataFlow":
                obj["source_objects"] = item.get("sourceObjects", [])
                obj["target_objects"] = item.get("targetObjects", [])
                obj["schedule"] = item.get("schedule")
                obj["last_run"] = item.get("lastRun")
            
            # Add dependencies if requested
            if include_dependencies and item.get("dependencies"):
                obj["dependencies"] = {
                    "upstream": item["dependencies"].get("upstream", []),
                    "downstream": item["dependencies"].get("downstream", [])
                }
            
            objects.append(obj)
        
        result = {
            "space_id": space_id,
            "objects": objects,
            "returned_count": len(objects),
            "has_more": len(objects) == top
        }
        
        # Add summary statistics
        if objects:
            type_counts = {}
            for obj in objects:
                obj_type = obj["object_type"]
                type_counts[obj_type] = type_counts.get(obj_type, 0) + 1
            result["summary"] = {
                "total_objects": len(objects),
                "by_type": type_counts
            }
        
        return json.dumps(result, indent=2)
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return json.dumps({
                "error": f"Space '{space_id}' not found"
            })
        elif e.response.status_code == 403:
            return json.dumps({
                "error": f"Access denied to space '{space_id}'"
            })
        else:
            return json.dumps({"error": f"HTTP error: {e.response.status_code}"})
    except Exception as e:
        return json.dumps({"error": f"Repository object listing failed: {str(e)}"})
```

---

### Tool 2: `get_object_definition`

**Purpose**: Get complete design-time object definition

**API Endpoint**: `GET /deepsea/repository/{spaceId}/designobjects/{objectId}`

**Implementation Template**:
```python
@mcp.tool()
def get_object_definition(
    space_id: str,
    object_id: str,
    include_full_definition: bool = True,
    include_dependencies: bool = True
) -> str:
    """
    Get complete design-time object definition from SAP Datasphere repository.
    
    This tool retrieves detailed object definitions including structure, logic,
    transformations, and metadata for tables, views, models, and data flows.
    
    Args:
        space_id: Space identifier (e.g., 'SAP_CONTENT')
        object_id: Object identifier (e.g., 'FINANCIAL_TRANSACTIONS')
        include_full_definition: Include complete object definition (default: True)
        include_dependencies: Include dependency information (default: True)
    
    Returns:
        JSON string containing complete object definition
    
    Examples:
        # Get table definition
        get_object_definition(
            space_id="SAP_CONTENT",
            object_id="FINANCIAL_TRANSACTIONS"
        )
        
        # Get view definition
        get_object_definition(
            space_id="SAP_CONTENT",
            object_id="CUSTOMER_FIN_SUMMARY_VIEW"
        )
        
        # Get data flow definition
        get_object_definition(
            space_id="SAP_CONTENT",
            object_id="LOAD_FINANCIAL_DATA"
        )
    """
    try:
        # Build endpoint URL
        endpoint = f"/deepsea/repository/{space_id}/designobjects/{object_id}"
        
        # Build query parameters
        params = {}
        
        if include_full_definition:
            params["includeDefinition"] = "true"
        
        if include_dependencies:
            params["$expand"] = "dependencies"
        
        # Make API request
        response = datasphere_client.get(endpoint, params=params)
        
        # Parse and format response
        obj_def = {
            "id": response.get("id"),
            "object_type": response.get("objectType"),
            "name": response.get("name"),
            "business_name": response.get("businessName"),
            "technical_name": response.get("technicalName"),
            "description": response.get("description"),
            "space_id": response.get("spaceId"),
            "status": response.get("status"),
            "deployment_status": response.get("deploymentStatus"),
            "owner": response.get("owner"),
            "version": response.get("version")
        }
        
        # Add definition based on object type
        if include_full_definition and "definition" in response:
            definition = response["definition"]
            obj_def["definition"] = format_object_definition(
                response.get("objectType"),
                definition
            )
        
        # Add dependencies
        if include_dependencies and "dependencies" in response:
            obj_def["dependencies"] = response["dependencies"]
        
        # Add metadata
        if "metadata" in response:
            obj_def["metadata"] = response["metadata"]
        
        return json.dumps(obj_def, indent=2)
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return json.dumps({
                "error": f"Object '{object_id}' not found in space '{space_id}'"
            })
        elif e.response.status_code == 403:
            return json.dumps({
                "error": f"Access denied to object '{object_id}'"
            })
        else:
            return json.dumps({"error": f"HTTP error: {e.response.status_code}"})
    except Exception as e:
        return json.dumps({"error": f"Object definition retrieval failed: {str(e)}"})


def format_object_definition(object_type, definition):
    """Format object definition based on type"""
    if object_type == "Table":
        return {
            "type": "Table",
            "columns": definition.get("columns", []),
            "primary_key": definition.get("primaryKey"),
            "foreign_keys": definition.get("foreignKeys", []),
            "indexes": definition.get("indexes", [])
        }
    elif object_type == "View":
        return {
            "type": "View",
            "view_type": definition.get("viewType"),
            "sql_definition": definition.get("sqlDefinition"),
            "base_tables": definition.get("baseTables", []),
            "columns": definition.get("columns", [])
        }
    elif object_type == "DataFlow":
        return {
            "type": "DataFlow",
            "source_connections": definition.get("sourceConnections", []),
            "target_connections": definition.get("targetConnections", []),
            "transformations": definition.get("transformations", []),
            "error_handling": definition.get("errorHandling"),
            "schedule": definition.get("schedule")
        }
    elif object_type == "AnalyticalModel":
        return {
            "type": "AnalyticalModel",
            "dimensions": definition.get("dimensions", []),
            "measures": definition.get("measures", []),
            "hierarchies": definition.get("hierarchies", []),
            "base_objects": definition.get("baseObjects", [])
        }
    else:
        return definition
```


---

### Tool 3: `get_deployed_objects`

**Purpose**: List runtime/deployed objects

**API Endpoint**: `GET /deepsea/repository/{spaceId}/deployedobjects`

**Implementation Template**:
```python
@mcp.tool()
def get_deployed_objects(
    space_id: str,
    object_types: Optional[List[str]] = None,
    runtime_status: Optional[str] = None,
    include_metrics: bool = True,
    top: int = 50,
    skip: int = 0
) -> str:
    """
    List runtime/deployed objects in SAP Datasphere.
    
    This tool retrieves information about objects that are actively deployed
    and running in the system, including runtime metrics and execution history.
    
    Args:
        space_id: Space identifier (e.g., 'SAP_CONTENT')
        object_types: Filter by object types (e.g., ['Table', 'DataFlow'])
        runtime_status: Filter by runtime status ('Active', 'Running', 'Error')
        include_metrics: Include runtime metrics (default: True)
        top: Maximum results to return (default: 50, max: 500)
        skip: Results to skip for pagination (default: 0)
    
    Returns:
        JSON string containing deployed objects with runtime information
    
    Examples:
        # List all deployed objects
        get_deployed_objects(space_id="SAP_CONTENT")
        
        # List active data flows
        get_deployed_objects(
            space_id="SAP_CONTENT",
            object_types=["DataFlow"],
            runtime_status="Active"
        )
        
        # List with runtime metrics
        get_deployed_objects(
            space_id="SAP_CONTENT",
            include_metrics=True
        )
    """
    try:
        # Build endpoint URL
        endpoint = f"/deepsea/repository/{space_id}/deployedobjects"
        
        # Build query parameters
        params = {
            "$top": top,
            "$skip": skip
        }
        
        # Build filter expression
        filters = []
        
        if object_types:
            type_filters = " or ".join([f"objectType eq '{t}'" for t in object_types])
            filters.append(f"({type_filters})")
        
        if runtime_status:
            filters.append(f"runtimeStatus eq '{runtime_status}'")
        
        # Always filter for deployed objects
        filters.append("deploymentStatus eq 'Deployed'")
        
        if filters:
            params["$filter"] = " and ".join(filters)
        
        # Make API request
        response = datasphere_client.get(endpoint, params=params)
        
        # Parse and format results
        deployed_objects = []
        for item in response.get("value", []):
            obj = {
                "id": item.get("id"),
                "object_id": item.get("objectId"),
                "object_type": item.get("objectType"),
                "name": item.get("name"),
                "business_name": item.get("businessName"),
                "space_id": item.get("spaceId"),
                "deployment_status": item.get("deploymentStatus"),
                "deployed_by": item.get("deployedBy"),
                "deployed_at": item.get("deployedAt"),
                "version": item.get("version"),
                "runtime_status": item.get("runtimeStatus"),
                "last_accessed": item.get("lastAccessed"),
                "access_count": item.get("accessCount")
            }
            
            # Add type-specific runtime information
            if item.get("objectType") == "DataFlow":
                obj["schedule"] = item.get("schedule")
                obj["last_execution"] = item.get("lastExecution")
            
            # Add runtime metrics if requested
            if include_metrics and item.get("runtimeMetrics"):
                obj["runtime_metrics"] = item["runtimeMetrics"]
            
            # Add consumers/dependencies
            if item.get("consumers"):
                obj["consumers"] = item["consumers"]
            if item.get("dependencies"):
                obj["dependencies"] = item["dependencies"]
            
            deployed_objects.append(obj)
        
        result = {
            "space_id": space_id,
            "deployed_objects": deployed_objects,
            "returned_count": len(deployed_objects),
            "has_more": len(deployed_objects) == top
        }
        
        # Add summary statistics
        if deployed_objects:
            status_counts = {}
            type_counts = {}
            for obj in deployed_objects:
                status = obj["runtime_status"]
                obj_type = obj["object_type"]
                status_counts[status] = status_counts.get(status, 0) + 1
                type_counts[obj_type] = type_counts.get(obj_type, 0) + 1
            
            result["summary"] = {
                "total_deployed": len(deployed_objects),
                "by_status": status_counts,
                "by_type": type_counts
            }
        
        return json.dumps(result, indent=2)
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return json.dumps({
                "error": f"Space '{space_id}' not found"
            })
        elif e.response.status_code == 403:
            return json.dumps({
                "error": f"Access denied to deployment information"
            })
        else:
            return json.dumps({"error": f"HTTP error: {e.response.status_code}"})
    except Exception as e:
        return json.dumps({"error": f"Deployed objects retrieval failed: {str(e)}"})
```

---

## Helper Functions

### Dependency Graph Builder
```python
def build_dependency_graph(objects: List[dict]) -> dict:
    """Build dependency graph from repository objects"""
    graph = {
        'nodes': [],
        'edges': []
    }
    
    # Add nodes
    for obj in objects:
        graph['nodes'].append({
            'id': obj['id'],
            'name': obj['name'],
            'type': obj['object_type'],
            'status': obj.get('status')
        })
    
    # Add edges
    for obj in objects:
        if 'dependencies' in obj:
            # Upstream dependencies
            for upstream in obj['dependencies'].get('upstream', []):
                graph['edges'].append({
                    'from': upstream,
                    'to': obj['id'],
                    'type': 'upstream'
                })
            
            # Downstream dependencies
            for downstream in obj['dependencies'].get('downstream', []):
                graph['edges'].append({
                    'from': obj['id'],
                    'to': downstream,
                    'type': 'downstream'
                })
    
    return graph
```

### Impact Analysis
```python
def analyze_impact(object_id: str, objects: List[dict]) -> dict:
    """Analyze impact of changing an object"""
    impact = {
        'object_id': object_id,
        'direct_downstream': [],
        'indirect_downstream': [],
        'total_affected': 0,
        'affected_by_type': {}
    }
    
    # Find object
    obj = next((o for o in objects if o['id'] == object_id), None)
    if not obj:
        impact['error'] = f"Object '{object_id}' not found"
        return impact
    
    # Get direct downstream
    direct = obj.get('dependencies', {}).get('downstream', [])
    impact['direct_downstream'] = direct
    
    # Recursively find indirect downstream
    visited = set([object_id])
    queue = list(direct)
    
    while queue:
        current = queue.pop(0)
        if current in visited:
            continue
        
        visited.add(current)
        impact['indirect_downstream'].append(current)
        
        # Find downstream of current
        current_obj = next((o for o in objects if o['id'] == current), None)
        if current_obj:
            # Count by type
            obj_type = current_obj.get('object_type', 'Unknown')
            impact['affected_by_type'][obj_type] = impact['affected_by_type'].get(obj_type, 0) + 1
            
            downstream = current_obj.get('dependencies', {}).get('downstream', [])
            queue.extend(downstream)
    
    impact['total_affected'] = len(visited) - 1
    
    return impact
```

### Object Categorization
```python
OBJECT_TYPE_CATEGORIES = {
    'data_objects': ['Table', 'View', 'Entity'],
    'analytical_objects': ['AnalyticalModel', 'CalculationView', 'Hierarchy'],
    'integration_objects': ['DataFlow', 'Transformation', 'Replication'],
    'logic_objects': ['StoredProcedure', 'Function', 'Script']
}

def categorize_objects(objects: List[dict]) -> dict:
    """Categorize objects by type"""
    categorized = {
        'data_objects': [],
        'analytical_objects': [],
        'integration_objects': [],
        'logic_objects': [],
        'other': []
    }
    
    for obj in objects:
        obj_type = obj.get('object_type')
        categorized_flag = False
        
        for category, types in OBJECT_TYPE_CATEGORIES.items():
            if obj_type in types:
                categorized[category].append(obj)
                categorized_flag = True
                break
        
        if not categorized_flag:
            categorized['other'].append(obj)
    
    return categorized
```

### Design vs Deployed Comparison
```python
def compare_design_deployed(design_obj: dict, deployed_obj: dict) -> dict:
    """Compare design-time and deployed object"""
    comparison = {
        'object_id': design_obj.get('id'),
        'version_match': design_obj.get('version') == deployed_obj.get('version'),
        'deployment_status': deployed_obj.get('deployment_status'),
        'differences': []
    }
    
    # Compare versions
    if not comparison['version_match']:
        comparison['differences'].append({
            'type': 'version_mismatch',
            'design_version': design_obj.get('version'),
            'deployed_version': deployed_obj.get('version')
        })
    
    # Compare columns (for tables/views)
    if 'definition' in design_obj and 'columns' in design_obj['definition']:
        design_cols = {c['name']: c for c in design_obj['definition']['columns']}
        deployed_cols = {}
        
        if 'definition' in deployed_obj and 'columns' in deployed_obj['definition']:
            deployed_cols = {c['name']: c for c in deployed_obj['definition']['columns']}
        
        # Find added columns
        added = set(design_cols.keys()) - set(deployed_cols.keys())
        if added:
            comparison['differences'].append({
                'type': 'columns_added',
                'columns': list(added)
            })
        
        # Find removed columns
        removed = set(deployed_cols.keys()) - set(design_cols.keys())
        if removed:
            comparison['differences'].append({
                'type': 'columns_removed',
                'columns': list(removed)
            })
        
        # Find modified columns
        for col_name in set(design_cols.keys()) & set(deployed_cols.keys()):
            design_col = design_cols[col_name]
            deployed_col = deployed_cols[col_name]
            
            if design_col.get('dataType') != deployed_col.get('dataType'):
                comparison['differences'].append({
                    'type': 'column_type_changed',
                    'column': col_name,
                    'design_type': design_col.get('dataType'),
                    'deployed_type': deployed_col.get('dataType')
                })
    
    comparison['has_differences'] = len(comparison['differences']) > 0
    
    return comparison
```

### Documentation Generator
```python
def generate_object_documentation(obj_definition: dict) -> str:
    """Generate markdown documentation for an object"""
    doc_lines = []
    
    doc_lines.append(f"# Object Definition: {obj_definition.get('name')}")
    doc_lines.append("")
    doc_lines.append("## Overview")
    doc_lines.append(f"- **Type**: {obj_definition.get('object_type')}")
    doc_lines.append(f"- **Space**: {obj_definition.get('space_id')}")
    doc_lines.append(f"- **Owner**: {obj_definition.get('owner')}")
    doc_lines.append(f"- **Version**: {obj_definition.get('version')}")
    doc_lines.append(f"- **Status**: {obj_definition.get('status')}")
    doc_lines.append("")
    
    if obj_definition.get('description'):
        doc_lines.append("## Description")
        doc_lines.append(obj_definition['description'])
        doc_lines.append("")
    
    # Add structure based on object type
    if 'definition' in obj_definition:
        definition = obj_definition['definition']
        
        if definition.get('type') == 'Table':
            doc_lines.append("## Table Structure")
            doc_lines.append("")
            doc_lines.append("### Columns")
            doc_lines.append("")
            doc_lines.append("| Column | Type | Nullable | Key | Description |")
            doc_lines.append("|--------|------|----------|-----|-------------|")
            
            for col in definition.get('columns', []):
                nullable = "Yes" if col.get('isNullable', True) else "No"
                is_key = "PK" if col.get('isPrimaryKey', False) else ""
                col_type = col.get('dataType', 'Unknown')
                if col.get('length'):
                    col_type += f"({col['length']})"
                elif col.get('precision'):
                    col_type += f"({col['precision']},{col.get('scale', 0)})"
                
                doc_lines.append(
                    f"| {col['name']} | {col_type} | {nullable} | {is_key} | {col.get('description', '')} |"
                )
            doc_lines.append("")
        
        elif definition.get('type') == 'View':
            doc_lines.append("## View Definition")
            doc_lines.append("")
            doc_lines.append(f"**View Type**: {definition.get('viewType')}")
            doc_lines.append("")
            
            if definition.get('baseTables'):
                doc_lines.append("**Base Tables**:")
                for table in definition['baseTables']:
                    doc_lines.append(f"- {table}")
                doc_lines.append("")
            
            if definition.get('sqlDefinition'):
                doc_lines.append("**SQL Definition**:")
                doc_lines.append("```sql")
                doc_lines.append(definition['sqlDefinition'])
                doc_lines.append("```")
                doc_lines.append("")
    
    # Add dependencies
    if 'dependencies' in obj_definition:
        deps = obj_definition['dependencies']
        
        if deps.get('upstream'):
            doc_lines.append("## Upstream Dependencies")
            for upstream in deps['upstream']:
                doc_lines.append(f"- {upstream}")
            doc_lines.append("")
        
        if deps.get('downstream'):
            doc_lines.append("## Downstream Dependencies")
            for downstream in deps['downstream']:
                doc_lines.append(f"- {downstream}")
            doc_lines.append("")
    
    return "\n".join(doc_lines)
```

---

## Testing Examples

### Test list_repository_objects
```python
# List all objects
result = list_repository_objects(space_id="SAP_CONTENT")

# List tables only
result = list_repository_objects(
    space_id="SAP_CONTENT",
    object_types=["Table"]
)

# List with dependencies
result = list_repository_objects(
    space_id="SAP_CONTENT",
    include_dependencies=True,
    top=100
)

# List active data flows
result = list_repository_objects(
    space_id="SAP_CONTENT",
    object_types=["DataFlow"],
    status_filter="Active"
)
```

### Test get_object_definition
```python
# Get table definition
result = get_object_definition(
    space_id="SAP_CONTENT",
    object_id="FINANCIAL_TRANSACTIONS"
)

# Get view definition
result = get_object_definition(
    space_id="SAP_CONTENT",
    object_id="CUSTOMER_FIN_SUMMARY_VIEW",
    include_full_definition=True
)

# Get data flow definition
result = get_object_definition(
    space_id="SAP_CONTENT",
    object_id="DAILY_FIN_ETL_FLOW",
    include_full_definition=True
)
```

### Test get_deployed_objects
```python
# List all deployed objects
result = get_deployed_objects(space_id="SAP_CONTENT")

# List deployed tables only
result = get_deployed_objects(
    space_id="SAP_CONTENT",
    object_types=["Table"]
)

# List with execution metrics
result = get_deployed_objects(
    space_id="SAP_CONTENT",
    include_metrics=True
)
```

---

## Integration Testing

### Full Workflow Test
```python
def test_repository_discovery_workflow():
    """Test complete repository discovery workflow."""
    
    # Step 1: List all objects
    all_objects = list_repository_objects(
        space_id="SAP_CONTENT",
        top=100
    )
    assert len(all_objects) > 0
    
    # Step 2: Get specific object definition
    first_object = all_objects[0]
    definition = get_object_definition(
        space_id="SAP_CONTENT",
        object_id=first_object['id'],
        include_full_definition=True
    )
    assert 'definition' in definition
    
    # Step 3: List deployed objects
    deployed = get_deployed_objects(
        space_id="SAP_CONTENT"
    )
    assert len(deployed) > 0
    
    # Step 4: Build dependency graph
    graph = build_dependency_graph(all_objects)
    assert len(graph) > 0
    
    print("✅ Repository discovery workflow test passed")
```

---

## Error Handling Examples

```python
# Handle missing object
try:
    result = get_object_definition(
        space_id="SAP_CONTENT",
        object_id="NON_EXISTENT_OBJECT"
    )
except Exception as e:
    print(f"Error: {e}")

# Handle invalid space
try:
    result = list_repository_objects(
        space_id="INVALID_SPACE"
    )
except Exception as e:
    print(f"Error: {e}")

# Handle pagination
page_size = 50
skip = 0
all_results = []

while True:
    page = list_repository_objects(
        space_id="SAP_CONTENT",
        top=page_size,
        skip=skip
    )
    
    if not page or len(page) == 0:
        break
    
    all_results.extend(page)
    skip += page_size
    
    if len(page) < page_size:
        break

print(f"Total objects retrieved: {len(all_results)}")
```

---

## Performance Optimization Tips

1. **Use Pagination**: Always paginate for large object lists
2. **Filter Early**: Use object_types and status_filter to reduce data
3. **Lazy Loading**: Only include_dependencies when needed
4. **Cache Metadata**: Cache object definitions to avoid repeated calls
5. **Batch Processing**: Process objects in batches for better performance

---

## Documentation Template

### Object Documentation Generator
```python
def generate_object_documentation(space_id: str, object_id: str) -> str:
    """Generate comprehensive documentation for a repository object."""
    
    # Get object definition
    obj = get_object_definition(
        space_id=space_id,
        object_id=object_id,
        include_full_definition=True
    )
    
    # Build documentation
    doc = f"""
# {obj['name']}

**Type**: {obj['objectType']}  
**Status**: {obj['status']}  
**Owner**: {obj['owner']}  
**Last Modified**: {obj['modifiedAt']}

## Description
{obj.get('description', 'No description available')}

## Technical Details
- **Technical Name**: {obj['technicalName']}
- **Package**: {obj.get('packageName', 'N/A')}
- **Version**: {obj.get('version', 'N/A')}

## Schema
"""
    
    if 'columns' in obj.get('definition', {}):
        doc += "\n| Column | Type | Key | Nullable | Description |\n"
        doc += "|--------|------|-----|----------|-------------|\n"
        
        for col in obj['definition']['columns']:
            doc += f"| {col['name']} | {col['dataType']} | "
            doc += f"{'Yes' if col.get('isPrimaryKey') else 'No'} | "
            doc += f"{'Yes' if col.get('isNullable') else 'No'} | "
            doc += f"{col.get('description', '')} |\n"
    
    if 'dependencies' in obj:
        deps = obj['dependencies']
        
        if deps.get('upstream'):
            doc += "\n## Upstream Dependencies\n"
            for upstream in deps['upstream']:
                doc += f"- {upstream}\n"
        
        if deps.get('downstream'):
            doc += "\n## Downstream Dependencies\n"
            for downstream in deps['downstream']:
                doc += f"- {downstream}\n"
    
    return doc
```

---

## Checklist

Before submitting implementation:

- [ ] All 3 tools implemented with proper type hints
- [ ] OAuth2 authentication integrated
- [ ] Comprehensive error handling
- [ ] OData query parameter support
- [ ] Dependency graph building
- [ ] Impact analysis functionality
- [ ] Object categorization
- [ ] Unit tests with >90% coverage
- [ ] Integration tests with real tenant
- [ ] Documentation with usage examples
- [ ] Code follows Ruff linting standards
- [ ] All tools return JSON strings for MCP compatibility

---

## Next Steps

1. Implement all 3 tools in `repository.py`
2. Add tools to `server.py`
3. Create unit tests
4. Run integration tests with real tenant
5. Update documentation
6. Proceed to Phase 4: Data Consumption (Analytical)

---

**Document Version**: 1.0  
**Last Updated**: December 9, 2025  
**Related Documents**:
- SAP_DATASPHERE_REPOSITORY_TOOLS_SPEC.md
- SAP_DATASPHERE_MCP_EXTRACTION_PLAN.md
    object_id="LOAD_FINANCIAL_DATA",
    include_dependencies=True
)
```

### Test get_deployed_objects
```python
# List all deployed objects
result = get_deployed_objects(space_id="SAP_CONTENT")

# List active data flows
result = get_deployed_objects(
    space_id="SAP_CONTENT",
    object_types=["DataFlow"],
    runtime_status="Active"
)

# List with metrics
result = get_deployed_objects(
    space_id="SAP_CONTENT",
    include_metrics=True
)
```

---

## Success Criteria

✅ All three repository discovery tools implemented  
✅ Object listing with filtering working  
✅ Object definition retrieval functional  
✅ Deployed objects listing working  
✅ Dependency information extracted  
✅ Type-specific formatting implemented  
✅ Impact analysis helper functional  
✅ Documentation generator working  
✅ Error handling for invalid objects  
✅ Pagination implemented  
✅ Documentation complete  
✅ Unit tests passing  
✅ Integration tests with real tenant passing  

---

## Next Steps After Implementation

1. Test repository tools with real SAP Datasphere tenant
2. Verify object definitions for all types
3. Test dependency graph building
4. Implement impact analysis workflows
5. Create documentation templates
6. Proceed to Phase 4: Data Consumption - Analytical
