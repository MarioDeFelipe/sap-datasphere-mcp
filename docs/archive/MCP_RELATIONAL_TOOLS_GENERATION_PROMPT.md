# MCP Relational Data Access Tools Generation Prompt - Phase 5.1

## Context

You are implementing **4 relational data consumption tools** for the SAP Datasphere MCP Server that enable row-level data access, ETL operations, and detailed data analysis. These tools complement the analytical tools and provide full data extraction capabilities.

**Reference Document**: `SAP_DATASPHERE_RELATIONAL_TOOLS_SPEC.md`

---

## Implementation Requirements

### Framework & Standards
- **Framework**: Standard MCP (not FastMCP)
- **Python Version**: 3.10+
- **Type Hints**: Full type annotations required
- **Return Format**: MCP tool responses with TextContent containing JSON strings
- **Error Handling**: Comprehensive HTTP status code handling
- **Authentication**: OAuth2 Bearer token with auto-refresh

---

## Tool Implementations

### Tool 1: `list_relational_datasets`

```python
from mcp.types import Tool, TextContent
import httpx
import json
from typing import Optional, List
from datetime import datetime

# Tool definition
list_relational_datasets_tool = Tool(
    name="list_relational_datasets",
    description="List all available relational datasets within a specific SAP Datasphere asset for row-level data access",
    inputSchema={
        "type": "object",
        "properties": {
            "space_id": {
                "type": "string",
                "description": "Space identifier (e.g., 'SAP_CONTENT')"
            },
            "asset_id": {
                "type": "string", 
                "description": "Asset identifier (e.g., 'SAP_SC_FI_AM_FINTRANSACTIONS')"
            },
            "select": {
                "type": "string",
                "description": "Comma-separated list of properties to return"
            },
            "expand": {
                "type": "string",
                "description": "Related entities to expand inline"
            },
            "top": {
                "type": "integer",
                "description": "Maximum number of results (default: 50, max: 1000)",
                "default": 50
            },
            "skip": {
                "type": "integer", 
                "description": "Number of results to skip for pagination",
                "default": 0
            }
        },
        "required": ["space_id", "asset_id"]
    }
)

async def list_relational_datasets(
    space_id: str,
    asset_id: str,
    select: Optional[str] = None,
    expand: Optional[str] = None,
    top: int = 50,
    skip: int = 0
) -> List[TextContent]:
    """
    List all available relational datasets within a specific asset.
    
    Shows tables and views that can be accessed in row-by-row fashion for ETL and detailed analysis.
    
    Args:
        space_id: Space identifier (e.g., "SAP_CONTENT")
        asset_id: Asset identifier (e.g., "SAP_SC_FI_AM_FINTRANSACTIONS")
        select: Comma-separated list of properties to return
        expand: Related entities to expand inline
        top: Maximum number of results (default: 50, max: 1000)
        skip: Number of results to skip for pagination
    
    Returns:
        List containing TextContent with JSON string of relational datasets
    
    Example:
        datasets = await list_relational_datasets(
            space_id="SAP_CONTENT",
            asset_id="SAP_SC_FI_AM_FINTRANSACTIONS"
        )
    """
    try:
        # Build URL
        base_url = f"{config.base_url}/api/v1/datasphere/consumption/relational"
        url = f"{base_url}/{space_id}/{asset_id}"
        
        # Build query parameters
        params = {}
        if select:
            params['$select'] = select
        if expand:
            params['$expand'] = expand
        if top:
            params['$top'] = min(top, 1000)  # Enforce max limit
        if skip:
            params['$skip'] = skip
        
        # Get OAuth2 token
        token = await get_oauth_token()
        
        # Make request
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                headers={
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/json'
                },
                timeout=30.0
            )
            
            response.raise_for_status()
            data = response.json()
        
        # Format response
        result = {
            'space_id': space_id,
            'asset_id': asset_id,
            'datasets': data.get('value', []),
            'count': len(data.get('value', [])),
            'metadata_url': f"{url}/$metadata",
            'access_type': 'relational',
            'query_timestamp': datetime.now().isoformat()
        }
        
        return [TextContent(
            type='text',
            text=json.dumps(result, indent=2)
        )]
    
    except httpx.HTTPStatusError as e:
        error_msg = handle_http_error(e, space_id, asset_id, 'list_relational_datasets')
        return [TextContent(
            type='text',
            text=json.dumps({'error': error_msg}, indent=2)
        )]
    
    except Exception as e:
        return [TextContent(
            type='text',
            text=json.dumps({'error': str(e)}, indent=2)
        )]
```

### Tool 2: `get_relational_table`

```python
# Tool definition
get_relational_table_tool = Tool(
    name="get_relational_table",
    description="Get OData service document and metadata for a specific relational table with column definitions and SQL type mapping",
    inputSchema={
        "type": "object",
        "properties": {
            "space_id": {
                "type": "string",
                "description": "Space identifier"
            },
            "asset_id": {
                "type": "string",
                "description": "Asset identifier"
            },
            "include_metadata": {
                "type": "boolean",
                "description": "Whether to fetch and parse CSDL metadata (default: True)",
                "default": True
            }
        },
        "required": ["space_id", "asset_id"]
    }
)

async def get_relational_table(
    space_id: str,
    asset_id: str,
    include_metadata: bool = True
) -> List[TextContent]:
    """
    Get the OData service document and metadata for a specific relational table.
    
    Shows available entity sets, columns, data types, and SQL type mappings for ETL planning.
    
    Args:
        space_id: Space identifier
        asset_id: Asset identifier
        include_metadata: Whether to fetch and parse CSDL metadata (default: True)
    
    Returns:
        List containing TextContent with JSON string of table information
    
    Example:
        table_info = await get_relational_table(
            space_id="SAP_CONTENT",
            asset_id="SAP_SC_FI_AM_FINTRANSACTIONS"
        )
    """
    try:
        base_url = f"{config.base_url}/api/v1/datasphere/consumption/relational"
        service_url = f"{base_url}/{space_id}/{asset_id}"
        metadata_url = f"{service_url}/$metadata"
        
        token = await get_oauth_token()
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }
        
        result = {
            'space_id': space_id,
            'asset_id': asset_id,
            'service_root': service_url,
            'metadata_url': metadata_url,
            'access_type': 'relational'
        }
        
        # Get service document
        async with httpx.AsyncClient() as client:
            response = await client.get(service_url, headers=headers, timeout=30.0)
            response.raise_for_status()
            service_doc = response.json()
            result['entity_sets'] = service_doc.get('value', [])
        
        # Get and parse metadata if requested
        if include_metadata:
            async with httpx.AsyncClient() as client:
                headers['Accept'] = 'application/xml'
                response = await client.get(metadata_url, headers=headers, timeout=30.0)
                response.raise_for_status()
                metadata_xml = response.text
            
            # Parse metadata for relational access
            parsed_metadata = parse_relational_metadata(metadata_xml)
            result['metadata'] = parsed_metadata
        
        return [TextContent(
            type='text',
            text=json.dumps(result, indent=2)
        )]
    
    except httpx.HTTPStatusError as e:
        error_msg = handle_http_error(e, space_id, asset_id, 'get_relational_table')
        return [TextContent(
            type='text',
            text=json.dumps({'error': error_msg}, indent=2)
        )]
    
    except Exception as e:
        return [TextContent(
            type='text',
            text=json.dumps({'error': str(e)}, indent=2)
        )]


def parse_relational_metadata(csdl_xml: str) -> dict:
    """
    Parse CSDL XML metadata to extract columns, data types, and SQL mappings.
    
    Args:
        csdl_xml: CSDL XML metadata string
    
    Returns:
        Dictionary containing parsed metadata with SQL type mappings
    """
    import xml.etree.ElementTree as ET
    
    namespaces = {
        'edmx': 'http://docs.oasis-open.org/odata/ns/edmx',
        'edm': 'http://docs.oasis-open.org/odata/ns/edm'
    }
    
    # OData to SQL type mapping
    type_mapping = {
        'Edm.String': 'NVARCHAR',
        'Edm.Decimal': 'DECIMAL',
        'Edm.Date': 'DATE',
        'Edm.DateTime': 'TIMESTAMP',
        'Edm.DateTimeOffset': 'TIMESTAMP',
        'Edm.Boolean': 'BOOLEAN',
        'Edm.Int32': 'INTEGER',
        'Edm.Int64': 'BIGINT',
        'Edm.Double': 'DOUBLE',
        'Edm.Single': 'FLOAT',
        'Edm.Guid': 'UNIQUEIDENTIFIER',
        'Edm.Binary': 'VARBINARY'
    }
    
    try:
        root = ET.fromstring(csdl_xml)
        
        entity_types = []
        
        # Find all entity types
        for entity_type in root.findall('.//edm:EntityType', namespaces):
            entity_name = entity_type.get('Name')
            
            columns = []
            keys = []
            
            # Extract key properties
            for key_ref in entity_type.findall('.//edm:PropertyRef', namespaces):
                keys.append(key_ref.get('Name'))
            
            # Extract properties (columns)
            for prop in entity_type.findall('.//edm:Property', namespaces):
                prop_name = prop.get('Name')
                prop_type = prop.get('Type')
                nullable = prop.get('Nullable', 'true') == 'true'
                max_length = prop.get('MaxLength')
                precision = prop.get('Precision')
                scale = prop.get('Scale')
                
                # Map to SQL type
                sql_type = type_mapping.get(prop_type, 'NVARCHAR')
                
                # Add type parameters
                if prop_type == 'Edm.String' and max_length:
                    sql_type = f"NVARCHAR({max_length})"
                elif prop_type == 'Edm.Decimal' and precision:
                    scale_part = f",{scale}" if scale else ""
                    sql_type = f"DECIMAL({precision}{scale_part})"
                
                column_info = {
                    'name': prop_name,
                    'type': prop_type,
                    'sql_type': sql_type,
                    'nullable': nullable,
                    'is_key': prop_name in keys
                }
                
                # Add optional attributes
                if max_length:
                    column_info['max_length'] = int(max_length)
                if precision:
                    column_info['precision'] = int(precision)
                if scale:
                    column_info['scale'] = int(scale)
                
                columns.append(column_info)
            
            entity_types.append({
                'name': entity_name,
                'keys': keys,
                'columns': columns,
                'total_columns': len(columns),
                'key_columns': len(keys)
            })
        
        return {
            'entity_types': entity_types,
            'total_columns': sum(len(et['columns']) for et in entity_types),
            'type_mappings': type_mapping
        }
    
    except ET.ParseError as e:
        return {'error': f'Failed to parse metadata XML: {str(e)}'}
```

### Tool 3: `query_relational_data`

```python
# Tool definition
query_relational_data_tool = Tool(
    name="query_relational_data",
    description="Execute OData queries on relational tables to retrieve row-level data with filtering, sorting, and pagination for ETL operations",
    inputSchema={
        "type": "object",
        "properties": {
            "space_id": {
                "type": "string",
                "description": "Space identifier"
            },
            "asset_id": {
                "type": "string",
                "description": "Asset identifier"
            },
            "entity_set": {
                "type": "string",
                "description": "Entity set name to query"
            },
            "select": {
                "type": "string",
                "description": "Comma-separated list of columns to return"
            },
            "filter": {
                "type": "string",
                "description": "OData filter expression (e.g., 'Amount gt 1000 and Currency eq \"USD\"')"
            },
            "orderby": {
                "type": "string",
                "description": "Sort order (e.g., 'TransactionDate desc')"
            },
            "top": {
                "type": "integer",
                "description": "Maximum number of results (default: 100, max: 50000)",
                "default": 100
            },
            "skip": {
                "type": "integer",
                "description": "Number of results to skip for pagination",
                "default": 0
            },
            "count": {
                "type": "boolean",
                "description": "Include total count in response",
                "default": False
            }
        },
        "required": ["space_id", "asset_id", "entity_set"]
    }
)

async def query_relational_data(
    space_id: str,
    asset_id: str,
    entity_set: str,
    select: Optional[str] = None,
    filter: Optional[str] = None,
    orderby: Optional[str] = None,
    top: int = 100,
    skip: int = 0,
    count: bool = False
) -> List[TextContent]:
    """
    Execute OData queries on relational tables to retrieve row-level data.
    
    Supports filtering, sorting, and pagination for ETL operations and detailed analysis.
    
    Args:
        space_id: Space identifier
        asset_id: Asset identifier
        entity_set: Entity set name to query
        select: Comma-separated list of columns to return
        filter: OData filter expression
        orderby: Sort order (e.g., "TransactionDate desc")
        top: Maximum number of results (default: 100, max: 50000)
        skip: Number of results to skip for pagination
        count: Include total count in response
    
    Returns:
        List containing TextContent with JSON string of query results
    
    Examples:
        # Basic query
        data = await query_relational_data(
            space_id="SAP_CONTENT",
            asset_id="SAP_SC_FI_AM_FINTRANSACTIONS",
            entity_set="SAP_SC_FI_AM_FINTRANSACTIONS",
            select="TransactionID,Amount,Currency",
            filter="Amount gt 1000",
            top=1000
        )
        
        # ETL batch query
        batch = await query_relational_data(
            space_id="SAP_CONTENT",
            asset_id="SAP_SC_FI_AM_FINTRANSACTIONS",
            entity_set="SAP_SC_FI_AM_FINTRANSACTIONS",
            orderby="TransactionDate asc",
            top=10000,
            skip=50000,
            count=True
        )
    """
    try:
        # Validate query parameters
        validation_errors = validate_relational_query(entity_set, select, filter, top, skip)
        if validation_errors:
            return [TextContent(
                type='text',
                text=json.dumps({'error': 'Query validation failed', 'details': validation_errors}, indent=2)
            )]
        
        # Build URL
        base_url = f"{config.base_url}/api/v1/datasphere/consumption/relational"
        url = f"{base_url}/{space_id}/{asset_id}/{entity_set}"
        
        # Build query parameters
        params = {}
        if select:
            params['$select'] = select
        if filter:
            params['$filter'] = filter
        if orderby:
            params['$orderby'] = orderby
        if top:
            params['$top'] = min(top, 50000)  # Enforce max limit for relational
        if skip:
            params['$skip'] = skip
        if count:
            params['$count'] = 'true'
        
        # Get OAuth2 token
        token = await get_oauth_token()
        
        # Make request
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                headers={
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/json'
                },
                timeout=120.0  # Longer timeout for large data queries
            )
            
            response.raise_for_status()
            data = response.json()
        
        # Format response with ETL metadata
        result = {
            'space_id': space_id,
            'asset_id': asset_id,
            'entity_set': entity_set,
            'access_type': 'relational',
            'query': {
                'select': select,
                'filter': filter,
                'orderby': orderby,
                'top': top,
                'skip': skip
            },
            'data': data.get('value', []),
            'count': data.get('@odata.count', len(data.get('value', []))),
            'next_link': data.get('@odata.nextLink'),
            'query_timestamp': datetime.now().isoformat()
        }
        
        # Add ETL metadata for large datasets
        if len(result['data']) >= 10000:
            result['etl_metadata'] = {
                'batch_size': len(result['data']),
                'is_full_batch': len(result['data']) == top,
                'next_skip': skip + len(result['data']),
                'recommended_batch_size': 10000,
                'estimated_total_batches': result['count'] // 10000 if result['count'] else None
            }
        
        return [TextContent(
            type='text',
            text=json.dumps(result, indent=2)
        )]
    
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            error_msg = f'Invalid query syntax: {e.response.text}'
        elif e.response.status_code == 413:
            error_msg = 'Result set too large. Please use smaller batch size or add filters.'
        else:
            error_msg = handle_http_error(e, space_id, asset_id, 'query_relational_data')
        
        return [TextContent(
            type='text',
            text=json.dumps({'error': error_msg}, indent=2)
        )]
    
    except Exception as e:
        return [TextContent(
            type='text',
            text=json.dumps({'error': str(e)}, indent=2)
        )]


def validate_relational_query(entity_set: str, select: Optional[str], filter_expr: Optional[str], top: int, skip: int) -> List[str]:
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
    
    # Validate filter syntax (basic security check)
    if filter_expr:
        forbidden_keywords = ['drop', 'delete', 'update', 'insert', 'create', 'alter', 'truncate']
        filter_lower = filter_expr.lower()
        for keyword in forbidden_keywords:
            if keyword in filter_lower:
                errors.append(f"Invalid filter expression contains forbidden keyword: {keyword}")
    
    return errors
```

### Tool 4: `get_relational_service_document`

```python
# Tool definition
get_relational_service_document_tool = Tool(
    name="get_relational_service_document",
    description="Retrieve OData service document for relational asset with ETL capabilities and data type mappings",
    inputSchema={
        "type": "object",
        "properties": {
            "space_id": {
                "type": "string",
                "description": "Space identifier"
            },
            "asset_id": {
                "type": "string",
                "description": "Asset identifier"
            }
        },
        "required": ["space_id", "asset_id"]
    }
)

async def get_relational_service_document(
    space_id: str,
    asset_id: str
) -> List[TextContent]:
    """
    Retrieve the OData service document for a specific relational asset.
    
    Lists all available entity sets with enhanced ETL capability information.
    
    Args:
        space_id: Space identifier
        asset_id: Asset identifier
    
    Returns:
        List containing TextContent with JSON string of service document and capabilities
    
    Example:
        service_doc = await get_relational_service_document(
            space_id="SAP_CONTENT",
            asset_id="SAP_SC_FI_AM_FINTRANSACTIONS"
        )
    """
    try:
        base_url = f"{config.base_url}/api/v1/datasphere/consumption/relational"
        service_url = f"{base_url}/{space_id}/{asset_id}"
        
        token = await get_oauth_token()
        
        # Get service document
        async with httpx.AsyncClient() as client:
            response = await client.get(
                service_url,
                headers={
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/json'
                },
                timeout=30.0
            )
            
            response.raise_for_status()
            data = response.json()
        
        # Enhance entity sets with full URLs and ETL info
        entity_sets = []
        for entity_set in data.get('value', []):
            entity_sets.append({
                'name': entity_set.get('name'),
                'kind': entity_set.get('kind'),
                'url': entity_set.get('url'),
                'full_url': f"{service_url}/{entity_set.get('url')}",
                'description': f"Relational access to {entity_set.get('name')} table"
            })
        
        # Build result with ETL capabilities
        result = {
            'space_id': space_id,
            'asset_id': asset_id,
            'service_root': service_url,
            'metadata_url': f"{service_url}/$metadata",
            'access_type': 'relational',
            'entity_sets': entity_sets,
            'capabilities': {
                'supports_filter': True,
                'supports_select': True,
                'supports_expand': True,
                'supports_orderby': True,
                'supports_top': True,
                'supports_skip': True,
                'supports_count': True,
                'max_top': 50000,
                'recommended_batch_size': 10000,
                'supports_streaming': True,
                'etl_optimized': True,
                'concurrent_queries': True
            },
            'data_types': {
                'supported_types': [
                    'Edm.String', 'Edm.Decimal', 'Edm.Date', 'Edm.DateTime', 
                    'Edm.DateTimeOffset', 'Edm.Boolean', 'Edm.Int32', 'Edm.Int64',
                    'Edm.Double', 'Edm.Single', 'Edm.Guid', 'Edm.Binary'
                ],
                'type_mappings': {
                    'Edm.String': 'NVARCHAR',
                    'Edm.Decimal': 'DECIMAL',
                    'Edm.Date': 'DATE',
                    'Edm.DateTime': 'TIMESTAMP',
                    'Edm.DateTimeOffset': 'TIMESTAMP',
                    'Edm.Boolean': 'BOOLEAN',
                    'Edm.Int32': 'INTEGER',
                    'Edm.Int64': 'BIGINT',
                    'Edm.Double': 'DOUBLE',
                    'Edm.Single': 'FLOAT',
                    'Edm.Guid': 'UNIQUEIDENTIFIER',
                    'Edm.Binary': 'VARBINARY'
                }
            },
            'etl_recommendations': {
                'batch_processing': 'Use batch sizes of 10,000-50,000 records for optimal performance',
                'filtering': 'Apply filters on indexed columns (dates, IDs) for better performance',
                'ordering': 'Use ORDER BY on primary key columns for consistent pagination',
                'parallel_processing': 'Multiple concurrent queries supported for large extractions'
            }
        }
        
        return [TextContent(
            type='text',
            text=json.dumps(result, indent=2)
        )]
    
    except httpx.HTTPStatusError as e:
        error_msg = handle_http_error(e, space_id, asset_id, 'get_relational_service_document')
        return [TextContent(
            type='text',
            text=json.dumps({'error': error_msg}, indent=2)
        )]
    
    except Exception as e:
        return [TextContent(
            type='text',
            text=json.dumps({'error': str(e)}, indent=2)
        )]
```

---

## Helper Functions

### OAuth2 Token Management
```python
from datetime import datetime, timedelta
from typing import Optional

class OAuth2TokenManager:
    """Manage OAuth2 token lifecycle with automatic refresh."""
    
    def __init__(self, client_id: str, client_secret: str, token_url: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.access_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
    
    async def get_token(self) -> str:
        """Get valid access token, refreshing if necessary."""
        if self.access_token and self.token_expiry and self.token_expiry > datetime.now():
            return self.access_token
        
        return await self.refresh_token()
    
    async def refresh_token(self) -> str:
        """Refresh OAuth2 access token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    'grant_type': 'client_credentials',
                    'client_id': self.client_id,
                    'client_secret': self.client_secret
                },
                timeout=30.0
            )
            
            response.raise_for_status()
            token_data = response.json()
            
            self.access_token = token_data['access_token']
            expires_in = token_data.get('expires_in', 3600)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in - 60)
            
            return self.access_token

# Global token manager instance
token_manager: Optional[OAuth2TokenManager] = None

async def get_oauth_token() -> str:
    """Get OAuth2 token from global token manager."""
    global token_manager
    
    if token_manager is None:
        token_manager = OAuth2TokenManager(
            client_id=config.client_id,
            client_secret=config.client_secret,
            token_url=config.token_url
        )
    
    return await token_manager.get_token()
```

### Error Handling
```python
def handle_http_error(error: httpx.HTTPStatusError, space_id: str, asset_id: str, operation: str) -> str:
    """
    Handle HTTP errors with user-friendly messages for relational operations.
    
    Args:
        error: HTTP status error
        space_id: Space identifier
        asset_id: Asset identifier
        operation: Operation being performed
    
    Returns:
        User-friendly error message
    """
    status_code = error.response.status_code
    
    if status_code == 401:
        return 'Authentication failed. Please check OAuth2 credentials.'
    elif status_code == 403:
        return f'Access denied to relational data in space {space_id} or asset {asset_id}.'
    elif status_code == 404:
        return f'Relational asset {asset_id} not found in space {space_id}.'
    elif status_code == 413:
        return 'Result set too large. Please use smaller batch size or add filters.'
    elif status_code == 429:
        return 'Rate limit exceeded. Please implement request throttling.'
    elif status_code == 500:
        return 'SAP Datasphere server error. Please try again later.'
    else:
        return f'HTTP {status_code} during {operation}: {error.response.text}'
```

### ETL Utilities
```python
def calculate_optimal_batch_size(estimated_rows: int, avg_row_size_kb: float = 1.0) -> int:
    """Calculate optimal batch size for ETL operations."""
    # Target ~10MB per batch
    target_size_mb = 10
    target_size_kb = target_size_mb * 1024
    
    optimal_batch = int(target_size_kb / avg_row_size_kb)
    
    # Ensure reasonable bounds
    return max(1000, min(optimal_batch, 50000))

def generate_etl_script(space_id: str, asset_id: str, entity_set: str, target_table: str) -> str:
    """Generate ETL script template for relational data extraction."""
    return f"""
# ETL Script for {space_id}.{asset_id}.{entity_set}
import asyncio
from typing import List, Dict, Any

async def extract_to_{target_table.lower()}():
    \"\"\"Extract {entity_set} to {target_table}.\"\"\"
    
    # 1. Get table metadata
    metadata = await get_relational_table(
        space_id="{space_id}",
        asset_id="{asset_id}",
        include_metadata=True
    )
    
    # 2. Calculate batch size
    batch_size = calculate_optimal_batch_size(estimated_rows=1000000)
    
    # 3. Extract in batches
    skip = 0
    total_processed = 0
    
    while True:
        batch = await query_relational_data(
            space_id="{space_id}",
            asset_id="{asset_id}",
            entity_set="{entity_set}",
            top=batch_size,
            skip=skip,
            count=True
        )
        
        if not batch or len(batch.get('data', [])) == 0:
            break
        
        # Process batch (implement your target loading logic)
        await load_batch_to_target(batch['data'], "{target_table}")
        
        total_processed += len(batch['data'])
        skip += batch_size
        
        print(f"Processed {{total_processed}} records")
        
        if len(batch['data']) < batch_size:
            break
    
    return total_processed

# Run extraction
if __name__ == "__main__":
    result = asyncio.run(extract_to_{target_table.lower()}())
    print(f"Extraction complete: {{result}} records processed")
"""

async def load_batch_to_target(batch_data: List[Dict[Any, Any]], target_table: str):
    """Template function for loading batch to target system."""
    # Implement your target system loading logic here
    # Examples: SQL INSERT, Parquet file write, Cloud storage upload
    pass
```

---

## Configuration
```python
from pydantic import BaseModel, Field

class RelationalConfig(BaseModel):
    """Configuration for relational data access."""
    
    base_url: str = Field(..., description='SAP Datasphere base URL')
    client_id: str = Field(..., description='OAuth2 client ID')
    client_secret: str = Field(..., description='OAuth2 client secret')
    token_url: str = Field(..., description='OAuth2 token endpoint')
    default_batch_size: int = Field(10000, description='Default batch size for ETL')
    max_batch_size: int = Field(50000, description='Maximum batch size')
    request_timeout: int = Field(120, description='Request timeout in seconds')
    max_concurrent_queries: int = Field(5, description='Maximum concurrent queries')
```

---

## Tool Registration

```python
# List of all tools
tools = [
    list_relational_datasets_tool,
    get_relational_table_tool,
    query_relational_data_tool,
    get_relational_service_document_tool
]

# Tool handler mapping
async def handle_tool_call(name: str, arguments: dict):
    """Handle MCP tool calls for relational data access."""
    
    if name == "list_relational_datasets":
        return await list_relational_datasets(**arguments)
    elif name == "get_relational_table":
        return await get_relational_table(**arguments)
    elif name == "query_relational_data":
        return await query_relational_data(**arguments)
    elif name == "get_relational_service_document":
        return await get_relational_service_document(**arguments)
    else:
        return [TextContent(
            type='text',
            text=json.dumps({'error': f'Unknown tool: {name}'}, indent=2)
        )]
```

---

## Testing Examples

### Unit Tests
```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_list_relational_datasets():
    """Test listing relational datasets."""
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            'value': [
                {'name': 'TRANSACTIONS', 'kind': 'EntitySet', 'url': 'TRANSACTIONS'}
            ]
        }
        mock_response.raise_for_status = AsyncMock()
        mock_get.return_value = mock_response
        
        result = await list_relational_datasets(
            space_id='TEST_SPACE',
            asset_id='TEST_ASSET'
        )
        
        assert len(result) == 1
        assert 'TRANSACTIONS' in result[0].text

@pytest.mark.asyncio
async def test_query_relational_data_with_pagination():
    """Test querying relational data with pagination."""
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            'value': [
                {'TransactionID': 'TXN001', 'Amount': 1500.00}
            ],
            '@odata.count': 50000
        }
        mock_response.raise_for_status = AsyncMock()
        mock_get.return_value = mock_response
        
        result = await query_relational_data(
            space_id='TEST_SPACE',
            asset_id='TEST_ASSET',
            entity_set='TEST_ENTITY',
            top=10000,
            skip=20000,
            count=True
        )
        
        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data['count'] == 50000
        assert 'etl_metadata' in data
```

### Integration Tests
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_relational_workflow():
    """Test complete relational data access workflow."""
    
    # 1. List datasets
    datasets = await list_relational_datasets(
        space_id='SAP_CONTENT',
        asset_id='SAP_SC_FI_AM_FINTRANSACTIONS'
    )
    assert len(datasets) > 0
    
    # 2. Get table metadata
    table_info = await get_relational_table(
        space_id='SAP_CONTENT',
        asset_id='SAP_SC_FI_AM_FINTRANSACTIONS'
    )
    assert 'columns' in table_info[0].text
    
    # 3. Query data with filters
    data = await query_relational_data(
        space_id='SAP_CONTENT',
        asset_id='SAP_SC_FI_AM_FINTRANSACTIONS',
        entity_set='SAP_SC_FI_AM_FINTRANSACTIONS',
        filter='Amount gt 1000',
        top=100
    )
    assert len(data) > 0
    
    # 4. Get service document
    service_doc = await get_relational_service_document(
        space_id='SAP_CONTENT',
        asset_id='SAP_SC_FI_AM_FINTRANSACTIONS'
    )
    assert 'etl_optimized' in service_doc[0].text
```

---

## Usage Examples

### Example 1: ETL Data Extraction
```python
# Extract large table in batches
async def extract_financial_transactions():
    batch_size = 10000
    skip = 0
    all_data = []
    
    while True:
        batch = await query_relational_data(
            space_id="SAP_CONTENT",
            asset_id="SAP_SC_FI_AM_FINTRANSACTIONS",
            entity_set="SAP_SC_FI_AM_FINTRANSACTIONS",
            select="TransactionID,Amount,Currency,TransactionDate",
            orderby="TransactionDate asc",
            top=batch_size,
            skip=skip,
            count=True
        )
        
        batch_data = json.loads(batch[0].text)
        
        if not batch_data.get('data'):
            break
        
        all_data.extend(batch_data['data'])
        skip += batch_size
        
        print(f"Extracted {len(all_data)} records so far...")
        
        if len(batch_data['data']) < batch_size:
            break
    
    return all_data
```

### Example 2: Data Quality Check
```python
# Check data quality
async def check_data_quality():
    # Get table schema
    table_info = await get_relational_table(
        space_id="SAP_CONTENT",
        asset_id="SAP_SC_FI_AM_FINTRANSACTIONS"
    )
    
    # Check for null values in key columns
    null_check = await query_relational_data(
        space_id="SAP_CONTENT",
        asset_id="SAP_SC_FI_AM_FINTRANSACTIONS",
        entity_set="SAP_SC_FI_AM_FINTRANSACTIONS",
        filter="TransactionID eq null",
        count=True
    )
    
    # Check date ranges
    date_range = await query_relational_data(
        space_id="SAP_CONTENT",
        asset_id="SAP_SC_FI_AM_FINTRANSACTIONS",
        entity_set="SAP_SC_FI_AM_FINTRANSACTIONS",
        select="TransactionDate",
        orderby="TransactionDate asc",
        top=1
    )
    
    return {
        'schema': json.loads(table_info[0].text),
        'null_keys': json.loads(null_check[0].text)['count'],
        'date_range': json.loads(date_range[0].text)
    }
```

---

## Checklist

Before submitting implementation:

- [ ] All 4 relational tools implemented with proper type hints
- [ ] OAuth2 token management with automatic refresh
- [ ] Comprehensive error handling for all HTTP status codes
- [ ] OData query parameter validation and security checks
- [ ] CSDL metadata parsing with SQL type mapping
- [ ] ETL-optimized pagination support (up to 50,000 records per batch)
- [ ] Query validation to prevent SQL injection
- [ ] Unit tests with >90% coverage
- [ ] Integration tests with real SAP Datasphere tenant
- [ ] ETL utility functions and script generation
- [ ] Documentation with usage examples
- [ ] Code follows project standards
- [ ] All tools return proper MCP responses with TextContent

---

## Next Steps

1. Implement all 4 tools following the templates above
2. Add tools to MCP server tool registry
3. Create unit tests for each tool
4. Run integration tests with real tenant
5. Test ETL workflows with large datasets
6. Update documentation with performance benchmarks
7. Proceed to Phase 6.1: KPI Discovery & Analysis

---

**Document Version**: 1.0  
**Last Updated**: December 9, 2025  
**Related Documents**:
- SAP_DATASPHERE_RELATIONAL_TOOLS_SPEC.md
- SAP_DATASPHERE_MCP_EXTRACTION_PLAN.md
- SAP_DATASPHERE_ANALYTICAL_TOOLS_SPEC.md (similar pattern)