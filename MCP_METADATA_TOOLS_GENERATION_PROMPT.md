# MCP Metadata Extraction Tools Generation Prompt for SAP Datasphere

## Context

You are extending the SAP Datasphere MCP Server with metadata extraction capabilities. This prompt will guide you to generate four tools that enable AI assistants to deeply inspect schemas, understand data structures, and plan integrations.

---

## Prerequisites

Ensure you have completed:
- Phase 2.1: Basic Catalog Tools
- Phase 2.2: Universal Search Tools

You should have working OAuth2 authentication and DatasphereClient class.

---

## Tool Specifications

### Tool 1: `get_consumption_metadata`

**Purpose**: Get CSDL metadata for consumption models

**API Endpoint**: `GET /api/v1/datasphere/consumption/$metadata`

**Implementation Template**:
```python
import xml.etree.ElementTree as ET
from typing import Optional, Dict, List, Any

@mcp.tool()
def get_consumption_metadata(
    parse_xml: bool = True,
    include_annotations: bool = True
) -> str:
    """
    Get CSDL metadata for SAP Datasphere consumption models.
    
    This tool retrieves the OData metadata document that describes the
    consumption service schema including entity types, properties, and
    relationships. Essential for understanding the overall consumption structure.
    
    Args:
        parse_xml: Parse XML into structured JSON format (default: True)
        include_annotations: Include SAP-specific annotations (default: True)
    
    Returns:
        JSON string containing parsed metadata or raw XML
    
    Examples:
        # Get parsed metadata
        get_consumption_metadata()
        
        # Get raw XML
        get_consumption_metadata(parse_xml=False)
    """
    try:
        # Make API request
        url = f"{datasphere_client.config.base_url.rstrip('/')}/api/v1/datasphere/consumption/$metadata"
        response = datasphere_client.session.get(url, timeout=30)
        response.raise_for_status()
        
        xml_content = response.text
        
        if not parse_xml:
            return json.dumps({
                "format": "XML (CSDL)",
                "content": xml_content
            }, indent=2)
        
        # Parse XML
        root = ET.fromstring(xml_content)
        
        # Define namespaces
        namespaces = {
            'edmx': 'http://docs.oasis-open.org/odata/ns/edmx',
            'edm': 'http://docs.oasis-open.org/odata/ns/edm',
            'sap': 'http://www.sap.com/Protocols/SAPData'
        }
        
        metadata = {
            "service_type": "consumption",
            "entity_types": [],
            "entity_sets": [],
            "complex_types": []
        }
        
        # Extract entity types
        for entity_type in root.findall('.//edm:EntityType', namespaces):
            entity_info = extract_entity_type(entity_type, namespaces, include_annotations)
            metadata['entity_types'].append(entity_info)
        
        # Extract entity sets
        for entity_set in root.findall('.//edm:EntitySet', namespaces):
            metadata['entity_sets'].append({
                'name': entity_set.get('Name'),
                'entity_type': entity_set.get('EntityType')
            })
        
        # Extract complex types
        for complex_type in root.findall('.//edm:ComplexType', namespaces):
            complex_info = extract_complex_type(complex_type, namespaces)
            metadata['complex_types'].append(complex_info)
        
        return json.dumps(metadata, indent=2)
        
    except ET.ParseError as e:
        return json.dumps({
            "error": "XML parsing failed",
            "message": str(e)
        })
    except Exception as e:
        return json.dumps({"error": f"Metadata retrieval failed: {str(e)}"})


def extract_entity_type(entity_type, namespaces, include_annotations):
    """Extract entity type information from XML"""
    entity_info = {
        'name': entity_type.get('Name'),
        'key_properties': [],
        'properties': [],
        'navigation_properties': []
    }
    
    # Extract key properties
    key_element = entity_type.find('edm:Key', namespaces)
    if key_element is not None:
        for prop_ref in key_element.findall('edm:PropertyRef', namespaces):
            entity_info['key_properties'].append(prop_ref.get('Name'))
    
    # Extract properties
    for prop in entity_type.findall('edm:Property', namespaces):
        prop_info = {
            'name': prop.get('Name'),
            'type': prop.get('Type'),
            'nullable': prop.get('Nullable', 'true') == 'true'
        }
        
        # Add type-specific attributes
        if 'String' in prop_info['type']:
            max_length = prop.get('MaxLength')
            if max_length:
                prop_info['max_length'] = max_length
        elif 'Decimal' in prop_info['type']:
            precision = prop.get('Precision')
            scale = prop.get('Scale')
            if precision:
                prop_info['precision'] = precision
            if scale:
                prop_info['scale'] = scale
        
        # Add SAP annotations if requested
        if include_annotations:
            sap_label = prop.get('{http://www.sap.com/Protocols/SAPData}label')
            if sap_label:
                prop_info['label'] = sap_label
        
        entity_info['properties'].append(prop_info)
    
    # Extract navigation properties
    for nav_prop in entity_type.findall('edm:NavigationProperty', namespaces):
        entity_info['navigation_properties'].append({
            'name': nav_prop.get('Name'),
            'type': nav_prop.get('Type'),
            'partner': nav_prop.get('Partner')
        })
    
    return entity_info


def extract_complex_type(complex_type, namespaces):
    """Extract complex type information from XML"""
    complex_info = {
        'name': complex_type.get('Name'),
        'properties': []
    }
    
    for prop in complex_type.findall('edm:Property', namespaces):
        complex_info['properties'].append({
            'name': prop.get('Name'),
            'type': prop.get('Type')
        })
    
    return complex_info
```

---

### Tool 2: `get_analytical_metadata`

**Purpose**: Retrieve CSDL metadata for analytical models

**API Endpoint**: `GET /api/v1/datasphere/consumption/analytical/{spaceId}/{assetId}/$metadata`

**Implementation Template**:
```python
@mcp.tool()
def get_analytical_metadata(
    space_id: str,
    asset_id: str,
    identify_dimensions_measures: bool = True
) -> str:
    """
    Retrieve CSDL metadata for analytical consumption of a specific asset.
    
    This tool retrieves analytical schema with dimensions, measures, hierarchies,
    and aggregation information for BI and analytics integration.
    
    Args:
        space_id: Space identifier (e.g., 'SAP_CONTENT')
        asset_id: Asset identifier (e.g., 'SAP_SC_FI_AM_FINTRANSACTIONS')
        identify_dimensions_measures: Automatically identify dimensions and measures
    
    Returns:
        JSON string containing parsed analytical metadata
    
    Examples:
        # Get analytical metadata
        get_analytical_metadata(
            space_id="SAP_CONTENT",
            asset_id="SAP_SC_FI_AM_FINTRANSACTIONS"
        )
    """
    try:
        # Build endpoint URL
        endpoint = f"/api/v1/datasphere/consumption/analytical/{space_id}/{asset_id}/$metadata"
        
        # Make API request
        url = f"{datasphere_client.config.base_url.rstrip('/')}{endpoint}"
        response = datasphere_client.session.get(url, timeout=30)
        response.raise_for_status()
        
        xml_content = response.text
        
        # Parse XML
        root = ET.fromstring(xml_content)
        
        namespaces = {
            'edmx': 'http://docs.oasis-open.org/odata/ns/edmx',
            'edm': 'http://docs.oasis-open.org/odata/ns/edm',
            'sap': 'http://www.sap.com/Protocols/SAPData'
        }
        
        metadata = {
            "space_id": space_id,
            "asset_id": asset_id,
            "model_type": "analytical",
            "entity_types": [],
            "dimensions": [],
            "measures": [],
            "hierarchies": []
        }
        
        # Extract entity types
        for entity_type in root.findall('.//edm:EntityType', namespaces):
            entity_info = extract_entity_type(entity_type, namespaces, True)
            metadata['entity_types'].append(entity_info)
            
            # Identify dimensions and measures if requested
            if identify_dimensions_measures:
                dims, meas = identify_dimensions_and_measures(entity_type, namespaces)
                metadata['dimensions'].extend(dims)
                metadata['measures'].extend(meas)
        
        # Extract hierarchies
        for entity_type in root.findall('.//edm:EntityType', namespaces):
            if 'Hierarchy' in entity_type.get('Name', ''):
                hierarchy_info = extract_hierarchy(entity_type, namespaces)
                metadata['hierarchies'].append(hierarchy_info)
        
        return json.dumps(metadata, indent=2)
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return json.dumps({
                "error": f"Asset '{asset_id}' not found in space '{space_id}'"
            })
        else:
            return json.dumps({"error": f"HTTP error: {e.response.status_code}"})
    except Exception as e:
        return json.dumps({"error": f"Analytical metadata retrieval failed: {str(e)}"})


def identify_dimensions_and_measures(entity_type, namespaces):
    """Identify dimensions and measures from entity type"""
    dimensions = []
    measures = []
    
    for prop in entity_type.findall('edm:Property', namespaces):
        prop_name = prop.get('Name')
        prop_type = prop.get('Type')
        
        # Check SAP annotations
        is_dimension = prop.get('{http://www.sap.com/Protocols/SAPData}dimension') == 'true'
        aggregation = prop.get('{http://www.sap.com/Protocols/SAPData}aggregation')
        label = prop.get('{http://www.sap.com/Protocols/SAPData}label')
        
        if is_dimension:
            dimensions.append({
                'name': prop_name,
                'type': prop_type,
                'label': label or prop_name,
                'hierarchy': prop.get('{http://www.sap.com/Protocols/SAPData}hierarchy')
            })
        elif aggregation:
            measures.append({
                'name': prop_name,
                'type': prop_type,
                'label': label or prop_name,
                'aggregation': aggregation,
                'unit': prop.get('{http://www.sap.com/Protocols/SAPData}unit')
            })
    
    return dimensions, measures


def extract_hierarchy(entity_type, namespaces):
    """Extract hierarchy information"""
    return {
        'name': entity_type.get('Name'),
        'properties': [
            {
                'name': prop.get('Name'),
                'type': prop.get('Type')
            }
            for prop in entity_type.findall('edm:Property', namespaces)
        ]
    }
```


---

### Tool 3: `get_relational_metadata`

**Purpose**: Retrieve CSDL metadata for relational access

**API Endpoint**: `GET /api/v1/datasphere/consumption/relational/{spaceId}/{assetId}/$metadata`

**Implementation Template**:
```python
@mcp.tool()
def get_relational_metadata(
    space_id: str,
    asset_id: str,
    map_to_sql_types: bool = True
) -> str:
    """
    Retrieve CSDL metadata for relational consumption of a specific asset.
    
    This tool retrieves complete schema information including tables, columns,
    data types, and relationships for relational data access and ETL planning.
    
    Args:
        space_id: Space identifier (e.g., 'SAP_CONTENT')
        asset_id: Asset identifier (e.g., 'SAP_SC_FI_AM_FINTRANSACTIONS')
        map_to_sql_types: Map OData types to SQL types (default: True)
    
    Returns:
        JSON string containing parsed relational metadata
    
    Examples:
        # Get relational metadata
        get_relational_metadata(
            space_id="SAP_CONTENT",
            asset_id="SAP_SC_FI_AM_FINTRANSACTIONS"
        )
        
        # Get with SQL type mapping
        get_relational_metadata(
            space_id="SAP_CONTENT",
            asset_id="CUSTOMER_VIEW",
            map_to_sql_types=True
        )
    """
    try:
        # Build endpoint URL
        endpoint = f"/api/v1/datasphere/consumption/relational/{space_id}/{asset_id}/$metadata"
        
        # Make API request
        url = f"{datasphere_client.config.base_url.rstrip('/')}{endpoint}"
        response = datasphere_client.session.get(url, timeout=30)
        response.raise_for_status()
        
        xml_content = response.text
        
        # Parse XML
        root = ET.fromstring(xml_content)
        
        namespaces = {
            'edmx': 'http://docs.oasis-open.org/odata/ns/edmx',
            'edm': 'http://docs.oasis-open.org/odata/ns/edm',
            'sap': 'http://www.sap.com/Protocols/SAPData'
        }
        
        metadata = {
            "space_id": space_id,
            "asset_id": asset_id,
            "model_type": "relational",
            "tables": []
        }
        
        # Extract entity types (tables)
        for entity_type in root.findall('.//edm:EntityType', namespaces):
            table_info = {
                'name': entity_type.get('Name'),
                'key_columns': [],
                'columns': [],
                'foreign_keys': []
            }
            
            # Extract key columns
            key_element = entity_type.find('edm:Key', namespaces)
            if key_element is not None:
                for prop_ref in key_element.findall('edm:PropertyRef', namespaces):
                    table_info['key_columns'].append(prop_ref.get('Name'))
            
            # Extract columns
            for prop in entity_type.findall('edm:Property', namespaces):
                column_info = extract_column_info(prop, namespaces, map_to_sql_types)
                table_info['columns'].append(column_info)
            
            # Extract foreign keys (navigation properties)
            for nav_prop in entity_type.findall('edm:NavigationProperty', namespaces):
                table_info['foreign_keys'].append({
                    'name': nav_prop.get('Name'),
                    'referenced_table': nav_prop.get('Type'),
                    'partner': nav_prop.get('Partner')
                })
            
            metadata['tables'].append(table_info)
        
        return json.dumps(metadata, indent=2)
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return json.dumps({
                "error": f"Asset '{asset_id}' not found in space '{space_id}'"
            })
        else:
            return json.dumps({"error": f"HTTP error: {e.response.status_code}"})
    except Exception as e:
        return json.dumps({"error": f"Relational metadata retrieval failed: {str(e)}"})


def extract_column_info(prop, namespaces, map_to_sql_types):
    """Extract column information from property"""
    column_info = {
        'name': prop.get('Name'),
        'odata_type': prop.get('Type'),
        'nullable': prop.get('Nullable', 'true') == 'true'
    }
    
    # Add type-specific attributes
    odata_type = prop.get('Type')
    
    if 'String' in odata_type:
        max_length = prop.get('MaxLength')
        if max_length:
            column_info['max_length'] = max_length
    elif 'Decimal' in odata_type:
        precision = prop.get('Precision')
        scale = prop.get('Scale')
        if precision:
            column_info['precision'] = precision
        if scale:
            column_info['scale'] = scale
    
    # Map to SQL type if requested
    if map_to_sql_types:
        column_info['sql_type'] = map_odata_to_sql_type(
            odata_type,
            column_info.get('precision'),
            column_info.get('scale'),
            column_info.get('max_length')
        )
    
    # Add SAP annotations
    label = prop.get('{http://www.sap.com/Protocols/SAPData}label')
    if label:
        column_info['label'] = label
    
    semantics = prop.get('{http://www.sap.com/Protocols/SAPData}semantics')
    if semantics:
        column_info['semantics'] = semantics
    
    return column_info


def map_odata_to_sql_type(odata_type, precision=None, scale=None, max_length=None):
    """Map OData type to SQL type"""
    type_map = {
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
    
    base_type = type_map.get(odata_type, 'VARCHAR')
    
    if base_type == 'VARCHAR' and max_length:
        return f'VARCHAR({max_length})'
    elif base_type == 'DECIMAL' and precision and scale:
        return f'DECIMAL({precision},{scale})'
    
    return base_type
```

---

### Tool 4: `get_repository_search_metadata`

**Purpose**: Get metadata for repository search functionality

**API Endpoint**: `GET /deepsea/repository/search/$metadata`

**Implementation Template**:
```python
@mcp.tool()
def get_repository_search_metadata(
    parse_xml: bool = True
) -> str:
    """
    Get CSDL metadata for repository search functionality.
    
    This tool retrieves metadata that describes the repository search service
    schema including searchable object types, fields, and available filters.
    
    Args:
        parse_xml: Parse XML into structured JSON format (default: True)
    
    Returns:
        JSON string containing parsed repository search metadata
    
    Examples:
        # Get parsed metadata
        get_repository_search_metadata()
        
        # Get raw XML
        get_repository_search_metadata(parse_xml=False)
    """
    try:
        # Make API request
        url = f"{datasphere_client.config.base_url.rstrip('/')}/deepsea/repository/search/$metadata"
        response = datasphere_client.session.get(url, timeout=30)
        response.raise_for_status()
        
        xml_content = response.text
        
        if not parse_xml:
            return json.dumps({
                "format": "XML (CSDL)",
                "content": xml_content
            }, indent=2)
        
        # Parse XML
        root = ET.fromstring(xml_content)
        
        namespaces = {
            'edmx': 'http://docs.oasis-open.org/odata/ns/edmx',
            'edm': 'http://docs.oasis-open.org/odata/ns/edm'
        }
        
        metadata = {
            "service_type": "repository_search",
            "searchable_object_types": [],
            "searchable_fields": [],
            "available_filters": [],
            "entity_types": []
        }
        
        # Extract entity types
        for entity_type in root.findall('.//edm:EntityType', namespaces):
            entity_info = extract_entity_type(entity_type, namespaces, False)
            metadata['entity_types'].append(entity_info)
            
            # Extract searchable fields
            for prop in entity_info['properties']:
                if prop['name'] in ['name', 'businessName', 'description']:
                    metadata['searchable_fields'].append({
                        'field': prop['name'],
                        'type': prop['type']
                    })
        
        # Identify available filters from properties
        if metadata['entity_types']:
            main_entity = metadata['entity_types'][0]
            for prop in main_entity['properties']:
                if prop['name'] in ['objectType', 'spaceId', 'status', 'deploymentStatus', 'owner']:
                    metadata['available_filters'].append(prop['name'])
        
        # Identify searchable object types (from enum or documentation)
        metadata['searchable_object_types'] = [
            'Table',
            'View',
            'AnalyticalModel',
            'DataFlow',
            'Transformation',
            'StoredProcedure',
            'CalculationView',
            'Hierarchy'
        ]
        
        return json.dumps(metadata, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Repository search metadata retrieval failed: {str(e)}"})
```

---

## Helper Functions

### Metadata Comparison
```python
def compare_analytical_relational_metadata(
    space_id: str,
    asset_id: str
) -> dict:
    """Compare analytical and relational metadata for same asset"""
    # Get both metadata types
    analytical = get_analytical_metadata(space_id, asset_id)
    relational = get_relational_metadata(space_id, asset_id)
    
    analytical_data = json.loads(analytical)
    relational_data = json.loads(relational)
    
    # Extract field names
    analytical_fields = set()
    for entity in analytical_data.get('entity_types', []):
        for prop in entity.get('properties', []):
            analytical_fields.add(prop['name'])
    
    relational_fields = set()
    for table in relational_data.get('tables', []):
        for col in table.get('columns', []):
            relational_fields.add(col['name'])
    
    comparison = {
        'common_fields': list(analytical_fields & relational_fields),
        'analytical_only': list(analytical_fields - relational_fields),
        'relational_only': list(relational_fields - analytical_fields),
        'analytical_field_count': len(analytical_fields),
        'relational_field_count': len(relational_fields)
    }
    
    return comparison
```

### Schema Documentation Generator
```python
def generate_schema_documentation(metadata: dict) -> str:
    """Generate human-readable schema documentation"""
    doc_lines = []
    
    doc_lines.append(f"# Schema Documentation")
    doc_lines.append(f"")
    doc_lines.append(f"**Model Type**: {metadata.get('model_type', 'Unknown')}")
    doc_lines.append(f"**Space**: {metadata.get('space_id', 'N/A')}")
    doc_lines.append(f"**Asset**: {metadata.get('asset_id', 'N/A')}")
    doc_lines.append(f"")
    
    # Document tables/entities
    if 'tables' in metadata:
        for table in metadata['tables']:
            doc_lines.append(f"## Table: {table['name']}")
            doc_lines.append(f"")
            doc_lines.append(f"**Primary Key**: {', '.join(table.get('key_columns', []))}")
            doc_lines.append(f"")
            doc_lines.append(f"### Columns")
            doc_lines.append(f"")
            doc_lines.append(f"| Column | Type | Nullable | Description |")
            doc_lines.append(f"|--------|------|----------|-------------|")
            
            for col in table.get('columns', []):
                nullable = "Yes" if col.get('nullable', True) else "No"
                col_type = col.get('sql_type', col.get('odata_type', 'Unknown'))
                label = col.get('label', '')
                doc_lines.append(f"| {col['name']} | {col_type} | {nullable} | {label} |")
            
            doc_lines.append(f"")
    
    # Document dimensions and measures
    if 'dimensions' in metadata and metadata['dimensions']:
        doc_lines.append(f"## Dimensions")
        doc_lines.append(f"")
        for dim in metadata['dimensions']:
            doc_lines.append(f"- **{dim['name']}** ({dim['type']}): {dim.get('label', '')}")
        doc_lines.append(f"")
    
    if 'measures' in metadata and metadata['measures']:
        doc_lines.append(f"## Measures")
        doc_lines.append(f"")
        for meas in metadata['measures']:
            agg = meas.get('aggregation', 'N/A')
            doc_lines.append(f"- **{meas['name']}** ({meas['type']}, {agg}): {meas.get('label', '')}")
        doc_lines.append(f"")
    
    return "\n".join(doc_lines)
```

### Metadata Caching
```python
from functools import lru_cache
from datetime import datetime, timedelta

class MetadataCache:
    """Simple metadata cache with TTL"""
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

# Global cache instance
metadata_cache = MetadataCache(ttl_minutes=60)

# Use in tools
def get_cached_analytical_metadata(space_id, asset_id):
    cache_key = f"analytical:{space_id}:{asset_id}"
    cached = metadata_cache.get(cache_key)
    
    if cached:
        return cached
    
    # Fetch fresh metadata
    metadata = get_analytical_metadata(space_id, asset_id)
    metadata_cache.set(cache_key, metadata)
    
    return metadata
```

---

## Testing Examples

### Test get_consumption_metadata
```python
# Get parsed metadata
result = get_consumption_metadata()

# Get raw XML
result = get_consumption_metadata(parse_xml=False)

# Without annotations
result = get_consumption_metadata(include_annotations=False)
```

### Test get_analytical_metadata
```python
# Get analytical metadata
result = get_analytical_metadata(
    space_id="SAP_CONTENT",
    asset_id="SAP_SC_FI_AM_FINTRANSACTIONS"
)

# With dimension/measure identification
result = get_analytical_metadata(
    space_id="SAP_CONTENT",
    asset_id="SALES_MODEL",
    identify_dimensions_measures=True
)
```

### Test get_relational_metadata
```python
# Get relational metadata
result = get_relational_metadata(
    space_id="SAP_CONTENT",
    asset_id="CUSTOMER_TABLE"
)

# With SQL type mapping
result = get_relational_metadata(
    space_id="SAP_CONTENT",
    asset_id="TRANSACTION_VIEW",
    map_to_sql_types=True
)
```

### Test get_repository_search_metadata
```python
# Get parsed metadata
result = get_repository_search_metadata()

# Get raw XML
result = get_repository_search_metadata(parse_xml=False)
```

---

## Success Criteria

✅ All four metadata extraction tools implemented  
✅ XML parsing working correctly  
✅ Dimension and measure identification working  
✅ Column definitions extracted accurately  
✅ Data type mapping functional  
✅ SAP annotations preserved  
✅ Navigation properties extracted  
✅ Hierarchies identified  
✅ Metadata caching implemented  
✅ Error handling for invalid assets  
✅ Documentation complete  
✅ Unit tests passing  
✅ Integration tests with real tenant passing  

---

## Next Steps After Implementation

1. Test metadata tools with real SAP Datasphere tenant
2. Verify parsing accuracy with complex models
3. Implement metadata comparison utilities
4. Add schema documentation generator
5. Optimize XML parsing performance
6. Proceed to Phase 3.2: Repository Object Discovery
