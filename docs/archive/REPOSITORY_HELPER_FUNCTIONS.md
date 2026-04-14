# Repository Helper Functions - Documentation

## Overview

The SAP Datasphere MCP Server includes four powerful helper functions for analyzing repository objects, their dependencies, and relationships. These functions complement the three main repository tools (`list_repository_objects`, `get_object_definition`, `get_deployed_objects`) and enable advanced workflows like impact analysis, dependency mapping, and object classification.

---

## Functions

### 1. `build_dependency_graph(objects)`

**Purpose**: Build a graph representation of object dependencies for visualization and analysis.

**Parameters**:
- `objects` (List[Dict[str, Any]]): List of repository objects with dependency information

**Returns**: Dictionary with:
- `nodes`: List of graph nodes (objects)
- `edges`: List of graph edges (dependencies)

**Use Cases**:
- Visualize data lineage
- Understand object relationships
- Identify data flow paths
- Generate dependency diagrams

**Example**:
```python
from sap_datasphere_mcp_server import build_dependency_graph

# Sample objects with dependencies
objects = [
    {
        "id": "SOURCE_TABLE",
        "name": "Source System Data",
        "objectType": "Table",
        "dependencies": {
            "upstream": [],
            "downstream": ["STAGING_VIEW", "ETL_FLOW"]
        }
    },
    {
        "id": "STAGING_VIEW",
        "name": "Staging View",
        "objectType": "View",
        "dependencies": {
            "upstream": ["SOURCE_TABLE"],
            "downstream": ["ANALYTICS_MODEL"]
        }
    },
    {
        "id": "ANALYTICS_MODEL",
        "name": "Financial Analytics",
        "objectType": "AnalyticalModel",
        "dependencies": {
            "upstream": ["STAGING_VIEW"],
            "downstream": ["DASHBOARD"]
        }
    }
]

# Build dependency graph
graph = build_dependency_graph(objects)

print(json.dumps(graph, indent=2))
```

**Output**:
```json
{
  "nodes": [
    {
      "id": "SOURCE_TABLE",
      "name": "Source System Data",
      "type": "Table",
      "status": "Unknown"
    },
    {
      "id": "STAGING_VIEW",
      "name": "Staging View",
      "type": "View",
      "status": "Unknown"
    },
    {
      "id": "ANALYTICS_MODEL",
      "name": "Financial Analytics",
      "type": "AnalyticalModel",
      "status": "Unknown"
    }
  ],
  "edges": [
    {
      "from": "SOURCE_TABLE",
      "to": "STAGING_VIEW",
      "type": "upstream"
    },
    {
      "from": "SOURCE_TABLE",
      "to": "ETL_FLOW",
      "type": "upstream"
    },
    {
      "from": "STAGING_VIEW",
      "to": "ANALYTICS_MODEL",
      "type": "upstream"
    }
  ]
}
```

---

### 2. `analyze_impact(object_id, objects)`

**Purpose**: Perform recursive impact analysis to identify all downstream objects affected by changes to a specific object.

**Parameters**:
- `object_id` (str): ID of the object to analyze
- `objects` (List[Dict[str, Any]]): List of repository objects with dependency information

**Returns**: Dictionary with:
- `object_id`: The analyzed object ID
- `direct_downstream`: List of directly dependent objects
- `indirect_downstream`: List of indirectly dependent objects (recursive)
- `total_affected`: Total count of affected objects
- `affected_by_type`: Breakdown by object type

**Use Cases**:
- Assess impact before making changes
- Identify all affected downstream consumers
- Plan testing scope for changes
- Generate change impact reports

**Example**:
```python
from sap_datasphere_mcp_server import analyze_impact

# Analyze impact of changing SOURCE_TABLE
impact = analyze_impact("SOURCE_TABLE", objects)

print(json.dumps(impact, indent=2))
```

**Output**:
```json
{
  "object_id": "SOURCE_TABLE",
  "direct_downstream": [
    "STAGING_VIEW",
    "ETL_FLOW"
  ],
  "indirect_downstream": [
    "ANALYTICS_MODEL",
    "DASHBOARD"
  ],
  "total_affected": 4,
  "affected_by_type": {
    "View": 1,
    "AnalyticalModel": 1,
    "DataFlow": 1,
    "Dashboard": 1
  }
}
```

**Interpretation**:
- Changing `SOURCE_TABLE` will directly affect 2 objects (`STAGING_VIEW`, `ETL_FLOW`)
- It will indirectly affect 2 more objects (`ANALYTICS_MODEL`, `DASHBOARD`)
- Total of 4 objects need to be tested after changing `SOURCE_TABLE`

---

### 3. `categorize_objects(objects)`

**Purpose**: Group repository objects into logical categories based on their type.

**Parameters**:
- `objects` (List[Dict[str, Any]]): List of repository objects

**Returns**: Dictionary with categories:
- `data_objects`: Tables, Views, Entities
- `analytical_objects`: Analytical Models, Calculation Views, Hierarchies
- `integration_objects`: Data Flows, Transformations, Replications
- `logic_objects`: Stored Procedures, Functions, Scripts
- `other`: Objects not matching above categories

**Use Cases**:
- Organize repository inventory
- Generate categorized reports
- Filter objects by functional area
- Analyze repository composition

**Example**:
```python
from sap_datasphere_mcp_server import categorize_objects

# Categorize objects by type
categorized = categorize_objects(objects)

# Print counts by category
for category, items in categorized.items():
    print(f"{category}: {len(items)} objects")
```

**Output**:
```
data_objects: 2 objects
analytical_objects: 1 object
integration_objects: 1 object
logic_objects: 0 objects
other: 0 objects
```

**Detailed Access**:
```python
# Access specific category
tables_and_views = categorized['data_objects']
for obj in tables_and_views:
    print(f"- {obj['name']} ({obj['objectType']})")

# Output:
# - Source System Data (Table)
# - Staging View (View)
```

---

### 4. `compare_design_deployed(design_obj, deployed_obj)`

**Purpose**: Compare design-time and deployed versions of an object to identify differences.

**Parameters**:
- `design_obj` (Dict[str, Any]): Design-time object definition (from `get_object_definition`)
- `deployed_obj` (Dict[str, Any]): Deployed object definition (from `get_deployed_objects`)

**Returns**: Dictionary with:
- `object_id`: Object identifier
- `version_match`: Boolean indicating if versions match
- `deployment_status`: Current deployment status
- `differences`: List of identified differences
- `has_differences`: Boolean indicating if any differences found

**Use Cases**:
- Verify deployment consistency
- Identify schema drift
- Plan redeployment strategy
- Generate deployment reports

**Example**:
```python
from sap_datasphere_mcp_server import compare_design_deployed

# Design-time definition (current development version)
design_obj = {
    "id": "CUSTOMER_TABLE",
    "version": "2.0",
    "definition": {
        "columns": [
            {"name": "CUSTOMER_ID", "dataType": "NVARCHAR(10)"},
            {"name": "NAME", "dataType": "NVARCHAR(100)"},
            {"name": "EMAIL", "dataType": "NVARCHAR(100)"},  # New column
            {"name": "STATUS", "dataType": "VARCHAR(20)"}  # Changed from NVARCHAR(10)
        ]
    }
}

# Deployed definition (production version)
deployed_obj = {
    "id": "CUSTOMER_TABLE",
    "version": "1.5",
    "deploymentStatus": "Deployed",
    "definition": {
        "columns": [
            {"name": "CUSTOMER_ID", "dataType": "NVARCHAR(10)"},
            {"name": "NAME", "dataType": "NVARCHAR(100)"},
            {"name": "STATUS", "dataType": "NVARCHAR(10)"},
            {"name": "CREATED_DATE", "dataType": "DATE"}  # Will be removed
        ]
    }
}

# Compare versions
comparison = compare_design_deployed(design_obj, deployed_obj)

print(json.dumps(comparison, indent=2))
```

**Output**:
```json
{
  "object_id": "CUSTOMER_TABLE",
  "version_match": false,
  "deployment_status": "Deployed",
  "differences": [
    {
      "type": "version_mismatch",
      "design_version": "2.0",
      "deployed_version": "1.5"
    },
    {
      "type": "columns_added",
      "columns": ["EMAIL"]
    },
    {
      "type": "columns_removed",
      "columns": ["CREATED_DATE"]
    },
    {
      "type": "column_type_changed",
      "column": "STATUS",
      "design_type": "VARCHAR(20)",
      "deployed_type": "NVARCHAR(10)"
    }
  ],
  "has_differences": true
}
```

**Interpretation**:
- Design version (2.0) is newer than deployed version (1.5)
- New column `EMAIL` was added in design
- Column `CREATED_DATE` was removed in design
- Column `STATUS` data type changed from `NVARCHAR(10)` to `VARCHAR(20)`
- Redeployment needed to sync design with production

---

## Complete Workflow Examples

### Workflow 1: Comprehensive Impact Analysis

```python
# Step 1: List all repository objects
objects_response = list_repository_objects(
    space_id="SAP_CONTENT",
    include_dependencies=True,
    top=500
)
objects = json.loads(objects_response[0].text)['objects']

# Step 2: Analyze impact of changing a critical table
impact = analyze_impact("FINANCIAL_TRANSACTIONS", objects)

print(f"Impact Analysis for FINANCIAL_TRANSACTIONS:")
print(f"- Direct consumers: {len(impact['direct_downstream'])}")
print(f"- Indirect consumers: {len(impact['indirect_downstream'])}")
print(f"- Total affected objects: {impact['total_affected']}")
print(f"\nBreakdown by type:")
for obj_type, count in impact['affected_by_type'].items():
    print(f"  - {obj_type}: {count}")
```

### Workflow 2: Repository Inventory Report

```python
# Step 1: List all repository objects
objects_response = list_repository_objects(
    space_id="SAP_CONTENT",
    top=1000
)
objects = json.loads(objects_response[0].text)['objects']

# Step 2: Categorize objects
categorized = categorize_objects(objects)

# Step 3: Generate report
print("SAP Datasphere Repository Inventory Report")
print("=" * 50)
print(f"\nTotal Objects: {len(objects)}")
print(f"\nBy Category:")
for category, items in categorized.items():
    if items:
        print(f"\n{category.replace('_', ' ').title()}: {len(items)}")
        for obj in items[:5]:  # Show first 5
            print(f"  - {obj['name']} ({obj['objectType']})")
        if len(items) > 5:
            print(f"  ... and {len(items) - 5} more")
```

### Workflow 3: Deployment Verification

```python
# Step 1: Get design-time definition
design_response = get_object_definition(
    space_id="SAP_CONTENT",
    object_id="CUSTOMER_VIEW",
    include_full_definition=True
)
design_obj = json.loads(design_response[0].text)

# Step 2: Get deployed version
deployed_response = get_deployed_objects(
    space_id="SAP_CONTENT",
    object_types=["View"]
)
deployed_objects = json.loads(deployed_response[0].text)['deployed_objects']
deployed_obj = next(o for o in deployed_objects if o['objectId'] == 'CUSTOMER_VIEW')

# Step 3: Compare versions
comparison = compare_design_deployed(design_obj, deployed_obj)

if comparison['has_differences']:
    print("⚠️  Design and deployed versions differ!")
    print(f"\nDifferences found: {len(comparison['differences'])}")
    for diff in comparison['differences']:
        print(f"- {diff['type']}: {diff}")
    print("\n→ Redeployment recommended")
else:
    print("✅ Design and deployed versions match")
```

### Workflow 4: Dependency Graph Visualization

```python
# Step 1: List objects with dependencies
objects_response = list_repository_objects(
    space_id="SAP_CONTENT",
    include_dependencies=True,
    top=500
)
objects = json.loads(objects_response[0].text)['objects']

# Step 2: Build dependency graph
graph = build_dependency_graph(objects)

# Step 3: Export to JSON for visualization tools (D3.js, Cytoscape, etc.)
with open('dependency_graph.json', 'w') as f:
    json.dump(graph, f, indent=2)

print(f"Dependency graph exported:")
print(f"- Nodes: {len(graph['nodes'])}")
print(f"- Edges: {len(graph['edges'])}")
```

---

## Integration with MCP Tools

These helper functions are designed to work seamlessly with the three repository MCP tools:

### Tool Integration Matrix

| Helper Function | Works With | Purpose |
|----------------|------------|---------|
| `build_dependency_graph` | `list_repository_objects` (with `include_dependencies=True`) | Create graph from object list |
| `analyze_impact` | `list_repository_objects` (with `include_dependencies=True`) | Analyze change impact |
| `categorize_objects` | `list_repository_objects` | Group objects by type |
| `compare_design_deployed` | `get_object_definition` + `get_deployed_objects` | Compare versions |

### Example: Using All Functions Together

```python
import json
from sap_datasphere_mcp_server import (
    build_dependency_graph,
    analyze_impact,
    categorize_objects,
    compare_design_deployed
)

# Get objects from MCP tool
objects_response = list_repository_objects(
    space_id="SAP_CONTENT",
    include_dependencies=True,
    top=500
)
objects = json.loads(objects_response[0].text)['objects']

# 1. Categorize objects
categorized = categorize_objects(objects)
print(f"Data objects: {len(categorized['data_objects'])}")
print(f"Analytical objects: {len(categorized['analytical_objects'])}")
print(f"Integration objects: {len(categorized['integration_objects'])}")

# 2. Build dependency graph
graph = build_dependency_graph(objects)
print(f"\nDependency graph: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges")

# 3. Analyze impact for critical object
impact = analyze_impact("FINANCIAL_TRANSACTIONS", objects)
print(f"\nImpact of changing FINANCIAL_TRANSACTIONS: {impact['total_affected']} objects")

# 4. Compare design vs deployed (for first table)
table_objects = categorized['data_objects']
if table_objects:
    first_table = table_objects[0]
    print(f"\nAnalyzing deployment status of: {first_table['name']}")
```

---

## API Reference

### Function Signatures

```python
def build_dependency_graph(objects: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build dependency graph from repository objects."""
    pass

def analyze_impact(object_id: str, objects: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze impact of changing an object."""
    pass

def categorize_objects(objects: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Categorize objects by type."""
    pass

def compare_design_deployed(design_obj: Dict[str, Any], deployed_obj: Dict[str, Any]) -> Dict[str, Any]:
    """Compare design-time and deployed object definitions."""
    pass
```

### Object Type Categories

```python
OBJECT_TYPE_CATEGORIES = {
    'data_objects': ['Table', 'View', 'Entity'],
    'analytical_objects': ['AnalyticalModel', 'CalculationView', 'Hierarchy'],
    'integration_objects': ['DataFlow', 'Transformation', 'Replication'],
    'logic_objects': ['StoredProcedure', 'Function', 'Script']
}
```

---

## Best Practices

### 1. Performance Optimization

```python
# ✅ Good: Request dependencies only when needed
objects = list_repository_objects(
    space_id="SAP_CONTENT",
    include_dependencies=True,  # Only when using build_dependency_graph or analyze_impact
    top=500
)

# ❌ Bad: Always requesting dependencies
objects = list_repository_objects(
    space_id="SAP_CONTENT",
    include_dependencies=True,  # Unnecessary for categorize_objects
    top=500
)
categorized = categorize_objects(objects)  # Doesn't use dependencies
```

### 2. Error Handling

```python
# Always check for errors in impact analysis
impact = analyze_impact("NON_EXISTENT_OBJECT", objects)
if 'error' in impact:
    print(f"Error: {impact['error']}")
else:
    print(f"Impact analysis successful: {impact['total_affected']} objects affected")
```

### 3. Large Repositories

```python
# For large repositories, use pagination
all_objects = []
skip = 0
top = 100

while True:
    response = list_repository_objects(
        space_id="SAP_CONTENT",
        top=top,
        skip=skip
    )
    data = json.loads(response[0].text)
    objects = data['objects']
    all_objects.extend(objects)

    if not data['has_more']:
        break
    skip += top

# Now analyze all objects
categorized = categorize_objects(all_objects)
```

---

## Troubleshooting

### Issue: Impact analysis returns no results

**Cause**: Object ID not found in objects list

**Solution**: Verify object ID exists
```python
object_ids = [obj.get('id', obj.get('objectId')) for obj in objects]
if "MY_OBJECT_ID" not in object_ids:
    print("Object not found in list")
```

### Issue: Dependency graph has missing edges

**Cause**: `include_dependencies=False` in `list_repository_objects`

**Solution**: Always use `include_dependencies=True` when building graphs
```python
objects = list_repository_objects(
    space_id="SAP_CONTENT",
    include_dependencies=True  # Required for dependency graph
)
```

### Issue: compare_design_deployed finds no differences but versions differ

**Cause**: Comparison only checks columns; other properties not compared

**Solution**: Check `version_match` field separately
```python
comparison = compare_design_deployed(design_obj, deployed_obj)
if not comparison['version_match']:
    print(f"Versions differ: {comparison['differences'][0]}")
```

---

## Summary

The four repository helper functions provide powerful capabilities for analyzing SAP Datasphere repository objects:

1. **build_dependency_graph**: Visualize object relationships
2. **analyze_impact**: Assess change impact
3. **categorize_objects**: Organize repository inventory
4. **compare_design_deployed**: Verify deployment consistency

These functions complement the three main repository MCP tools and enable advanced workflows for data governance, impact analysis, and deployment verification.

---

**Document Version**: 1.0
**Last Updated**: December 10, 2025
**Related Documents**:
- SAP_DATASPHERE_REPOSITORY_TOOLS_SPEC.md
- MCP_REPOSITORY_TOOLS_GENERATION_PROMPT.md
- README.md
