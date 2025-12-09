# MCP Tool Generation Prompt - Phase 4.1 Analytical Model Access

## Context

You are implementing **4 analytical data consumption tools** for the SAP Datasphere MCP Server. These tools enable business intelligence, reporting, and analytical data access with OData query capabilities.

**Reference Document**: `SAP_DATASPHERE_ANALYTICAL_TOOLS_SPEC.md`

---

## Implementation Requirements

### Framework & Standards
- **Framework**: FastMCP (Python MCP framework)
- **Python Version**: 3.10+
- **Package Manager**: uv
- **Linting**: Ruff (99 char line length, Google docstrings, single quotes)
- **Type Hints**: Full type annotations required
- **Return Format**: JSON strings (for MCP compatibility)

### Project Structure
```
src/sap-datasphere-mcp-server/
├── awslabs/
│   └── sap_datasphere_mcp_server/
│       ├── __init__.py
│       ├── server.py          # Add tools here
│       ├── models.py          # Pydantic models
│       ├── consts.py          # Constants
│       └── analytical.py      # NEW: Analytical data access module
```

---

## Tool 1: `list_analytical_datasets`

### Implementation

```python
from mcp.server import Server
from mcp import types
import httpx
import json
from typing import Optional

@server.call_tool()
async def list_analytical_datasets(
    space_id: str,
    asset_id: str,
    select: Optional[str] = None,
    expand: Optional[str] = None,
    top: Optional[int] = 50,
    skip: Optional[int] = 0
) -> list[types.TextContent]:
    """
    List all available analytical datasets within a specific asset.
    
    Shows analytical models that can be queried for business intelligence and reporting.
    
    Args:
        space_id: Space identifier (e.g., "SAP_CONTENT")
        asset_id: Asset identifier (e.g., "SAP_SC_FI_AM_FINTRANSACTIONS")
        select: Comma-separated list of properties to return
        expand: Related entities to expand inline
        top: Maximum number of results (default: 50, max: 1000)
        skip: Number of results to skip for pagination
    
    Returns:
        JSON string containing list of analytical datasets with their metadata
    
    Example:
        ```python
        datasets = await list_analytical_datasets(
            space_id="SAP_CONTENT",
            asset_id="SAP_SC_FI_AM_FINTRANSACTIONS"
        )
        ```
    """
    try:
        # Build URL
        base_url = f"{config.base_url}/api/v1/datasphere/consumption/analytical"
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
            'metadata_url': f"{url}/$metadata"
        }
        
        return [types.TextContent(
            type='text',
            text=json.dumps(result, indent=2)
        )]
    
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            error_msg = 'Authentication failed. Please check OAuth2 credentials.'
        elif e.response.status_code == 403:
            error_msg = f'Access denied to space {space_id} or asset {asset_id}.'
        elif e.response.status_code == 404:
            error_msg = f'Space {space_id} or asset {asset_id} not found.'
        else:
            error_msg = f'HTTP {e.response.status_code}: {e.response.text}'
        
        return [types.TextContent(
            type='text',
            text=json.dumps({'error': error_msg}, indent=2)
        )]
    
    except Exception as e:
        return [types.TextContent(
            type='text',
            text=json.dumps({'error': str(e)}, indent=2)
        )]
```

---

## Tool 2: `get_analytical_model`

### Implementation

```python
@server.call_tool()
async def get_analytical_model(
    space_id: str,
    asset_id: str,
    include_metadata: bool = True
) -> list[types.TextContent]:
    """
    Get the OData service document and metadata for a specific analytical model.
    
    Shows available entity sets, dimensions, measures, and query capabilities.
    
    Args:
        space_id: Space identifier
        asset_id: Asset identifier
        include_metadata: Whether to fetch and parse CSDL metadata (default: True)
    
    Returns:
        JSON string containing service document and parsed metadata
    
    Example:
        ```python
        model = await get_analytical_model(
            space_id="SAP_CONTENT",
            asset_id="SAP_SC_FI_AM_FINTRANSACTIONS"
        )
        ```
    """
    try:
        base_url = f"{config.base_url}/api/v1/datasphere/consumption/analytical"
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
            'metadata_url': metadata_url
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
            
            # Parse metadata
            parsed_metadata = parse_analytical_metadata(metadata_xml)
            result['metadata'] = parsed_metadata
        
        return [types.TextContent(
            type='text',
            text=json.dumps(result, indent=2)
        )]
    
    except httpx.HTTPStatusError as e:
        error_msg = handle_http_error(e, space_id, asset_id)
        return [types.TextContent(
            type='text',
            text=json.dumps({'error': error_msg}, indent=2)
        )]
    
    except Exception as e:
        return [types.TextContent(
            type='text',
            text=json.dumps({'error': str(e)}, indent=2)
        )]


def parse_analytical_metadata(csdl_xml: str) -> dict:
    """
    Parse CSDL XML metadata to extract dimensions, measures, and entity information.
    
    Args:
        csdl_xml: CSDL XML metadata string
    
    Returns:
        Dictionary containing parsed metadata with dimensions and measures
    """
    import xml.etree.ElementTree as ET
    
    namespaces = {
        'edmx': 'http://docs.oasis-open.org/odata/ns/edmx',
        'edm': 'http://docs.oasis-open.org/odata/ns/edm',
        'sap': 'http://www.sap.com/Protocols/SAPData'
    }
    
    try:
        root = ET.fromstring(csdl_xml)
        
        entity_types = []
        
        # Find all entity types
        for entity_type in root.findall('.//edm:EntityType', namespaces):
            entity_name = entity_type.get('Name')
            
            dimensions = []
            measures = []
            keys = []
            
            # Extract key properties
            for key_ref in entity_type.findall('.//edm:PropertyRef', namespaces):
                keys.append(key_ref.get('Name'))
            
            # Extract properties
            for prop in entity_type.findall('.//edm:Property', namespaces):
                prop_name = prop.get('Name')
                prop_type = prop.get('Type')
                agg_role = prop.get('{http://www.sap.com/Protocols/SAPData}aggregation-role')
                
                prop_info = {
                    'name': prop_name,
                    'type': prop_type,
                    'nullable': prop.get('Nullable', 'true') == 'true'
                }
                
                if agg_role == 'dimension':
                    dimensions.append(prop_info)
                elif agg_role == 'measure':
                    measures.append(prop_info)
            
            entity_types.append({
                'name': entity_name,
                'keys': keys,
                'dimensions': dimensions,
                'measures': measures,
                'total_properties': len(dimensions) + len(measures)
            })
        
        return {
            'entity_types': entity_types,
            'total_dimensions': sum(len(et['dimensions']) for et in entity_types),
            'total_measures': sum(len(et['measures']) for et in entity_types)
        }
    
    except ET.ParseError as e:
        return {'error': f'Failed to parse metadata XML: {str(e)}'}
```

---

## Tool 3: `query_analytical_data`

### Implementation

```python
from typing import Optional, List

@server.call_tool()
async def query_analytical_data(
    space_id: str,
    asset_id: str,
    entity_set: str,
    select: Optional[str] = None,
    filter: Optional[str] = None,
    orderby: Optional[str] = None,
    top: Optional[int] = 50,
    skip: Optional[int] = 0,
    count: bool = False,
    apply: Optional[str] = None
) -> list[types.TextContent]:
    """
    Execute OData queries on analytical models to retrieve aggregated data.
    
    Supports filtering, sorting, pagination, and aggregation for business intelligence.
    
    Args:
        space_id: Space identifier
        asset_id: Asset identifier
        entity_set: Entity set name to query
        select: Comma-separated list of dimensions/measures to return
        filter: OData filter expression (e.g., "Amount gt 1000 and Currency eq 'USD'")
        orderby: Sort order (e.g., "Amount desc")
        top: Maximum number of results (default: 50, max: 10000)
        skip: Number of results to skip for pagination
        count: Include total count in response
        apply: Aggregation transformations (e.g., "groupby((Currency), aggregate(Amount with sum as TotalAmount))")
    
    Returns:
        JSON string containing query results
    
    Examples:
        ```python
        # Basic query
        data = await query_analytical_data(
            space_id="SAP_CONTENT",
            asset_id="SAP_SC_FI_AM_FINTRANSACTIONS",
            entity_set="SAP_SC_FI_AM_FINTRANSACTIONS",
            select="Currency,Amount",
            filter="Amount gt 1000",
            top=100
        )
        
        # Aggregation query
        data = await query_analytical_data(
            space_id="SAP_CONTENT",
            asset_id="SAP_SC_FI_AM_FINTRANSACTIONS",
            entity_set="SAP_SC_FI_AM_FINTRANSACTIONS",
            apply="groupby((Currency), aggregate(Amount with sum as TotalAmount))"
        )
        ```
    """
    try:
        # Build URL
        base_url = f"{config.base_url}/api/v1/datasphere/consumption/analytical"
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
            params['$top'] = min(top, 10000)  # Enforce max limit
        if skip:
            params['$skip'] = skip
        if count:
            params['$count'] = 'true'
        if apply:
            params['$apply'] = apply
        
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
                timeout=60.0  # Longer timeout for data queries
            )
            
            response.raise_for_status()
            data = response.json()
        
        # Format response
        result = {
            'space_id': space_id,
            'asset_id': asset_id,
            'entity_set': entity_set,
            'query': {
                'select': select,
                'filter': filter,
                'orderby': orderby,
                'top': top,
                'skip': skip,
                'apply': apply
            },
            'data': data.get('value', []),
            'count': data.get('@odata.count', len(data.get('value', [])))
        }
        
        return [types.TextContent(
            type='text',
            text=json.dumps(result, indent=2)
        )]
    
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            error_msg = f'Invalid query syntax: {e.response.text}'
        elif e.response.status_code == 413:
            error_msg = 'Result set too large. Please use pagination or add filters.'
        else:
            error_msg = handle_http_error(e, space_id, asset_id)
        
        return [types.TextContent(
            type='text',
            text=json.dumps({'error': error_msg}, indent=2)
        )]
    
    except Exception as e:
        return [types.TextContent(
            type='text',
            text=json.dumps({'error': str(e)}, indent=2)
        )]
```

---

## Tool 4: `get_analytical_service_document`

### Implementation

```python
@server.call_tool()
async def get_analytical_service_document(
    space_id: str,
    asset_id: str
) -> list[types.TextContent]:
    """
    Retrieve the OData service document for a specific analytical asset.
    
    Lists all available entity sets and their URLs with enhanced capability information.
    
    Args:
        space_id: Space identifier
        asset_id: Asset identifier
    
    Returns:
        JSON string containing service document with entity sets and capabilities
    
    Example:
        ```python
        service_doc = await get_analytical_service_document(
            space_id="SAP_CONTENT",
            asset_id="SAP_SC_FI_AM_FINTRANSACTIONS"
        )
        ```
    """
    try:
        base_url = f"{config.base_url}/api/v1/datasphere/consumption/analytical"
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
        
        # Enhance entity sets with full URLs
        entity_sets = []
        for entity_set in data.get('value', []):
            entity_sets.append({
                'name': entity_set.get('name'),
                'kind': entity_set.get('kind'),
                'url': entity_set.get('url'),
                'full_url': f"{service_url}/{entity_set.get('url')}"
            })
        
        # Build result
        result = {
            'space_id': space_id,
            'asset_id': asset_id,
            'service_root': service_url,
            'metadata_url': f"{service_url}/$metadata",
            'entity_sets': entity_sets,
            'capabilities': {
                'supports_filter': True,
                'supports_select': True,
                'supports_expand': True,
                'supports_orderby': True,
                'supports_top': True,
                'supports_skip': True,
                'supports_count': True,
                'supports_apply': True,
                'max_top': 10000
            }
        }
        
        return [types.TextContent(
            type='text',
            text=json.dumps(result, indent=2)
        )]
    
    except httpx.HTTPStatusError as e:
        error_msg = handle_http_error(e, space_id, asset_id)
        return [types.TextContent(
            type='text',
            text=json.dumps({'error': error_msg}, indent=2)
        )]
    
    except Exception as e:
        return [types.TextContent(
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
def handle_http_error(error: httpx.HTTPStatusError, space_id: str, asset_id: str) -> str:
    """
    Handle HTTP errors with user-friendly messages.
    
    Args:
        error: HTTP status error
        space_id: Space identifier
        asset_id: Asset identifier
    
    Returns:
        User-friendly error message
    """
    status_code = error.response.status_code
    
    if status_code == 401:
        return 'Authentication failed. Please check OAuth2 credentials.'
    elif status_code == 403:
        return f'Access denied to space {space_id} or asset {asset_id}.'
    elif status_code == 404:
        return f'Space {space_id} or asset {asset_id} not found.'
    elif status_code == 413:
        return 'Result set too large. Please use pagination or add filters.'
    elif status_code == 500:
        return 'SAP Datasphere server error. Please try again later.'
    else:
        return f'HTTP {status_code}: {error.response.text}'
```

### OData Query Builder

```python
class ODataQueryBuilder:
    """Build OData query strings with validation."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.params = {}
    
    def select(self, fields: List[str]) -> 'ODataQueryBuilder':
        """Add $select parameter."""
        self.params['$select'] = ','.join(fields)
        return self
    
    def filter(self, expression: str) -> 'ODataQueryBuilder':
        """Add $filter parameter."""
        self.params['$filter'] = expression
        return self
    
    def orderby(self, field: str, direction: str = 'asc') -> 'ODataQueryBuilder':
        """Add $orderby parameter."""
        self.params['$orderby'] = f'{field} {direction}'
        return self
    
    def top(self, count: int) -> 'ODataQueryBuilder':
        """Add $top parameter."""
        self.params['$top'] = min(count, 10000)
        return self
    
    def skip(self, count: int) -> 'ODataQueryBuilder':
        """Add $skip parameter."""
        self.params['$skip'] = count
        return self
    
    def count(self) -> 'ODataQueryBuilder':
        """Add $count parameter."""
        self.params['$count'] = 'true'
        return self
    
    def apply(self, expression: str) -> 'ODataQueryBuilder':
        """Add $apply parameter for aggregations."""
        self.params['$apply'] = expression
        return self
    
    def build(self) -> str:
        """Build final query URL."""
        if not self.params:
            return self.base_url
        
        query_string = '&'.join([f'{k}={v}' for k, v in self.params.items()])
        return f'{self.base_url}?{query_string}'
```

---

## Configuration Model

```python
from pydantic import BaseModel, Field

class AnalyticalConfig(BaseModel):
    """Configuration for analytical data access."""
    
    base_url: str = Field(..., description='SAP Datasphere base URL')
    client_id: str = Field(..., description='OAuth2 client ID')
    client_secret: str = Field(..., description='OAuth2 client secret')
    token_url: str = Field(..., description='OAuth2 token endpoint')
    default_page_size: int = Field(50, description='Default page size for queries')
    max_page_size: int = Field(10000, description='Maximum page size')
    request_timeout: int = Field(60, description='Request timeout in seconds')
```

---

## Testing Examples

### Unit Tests

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_list_analytical_datasets():
    """Test listing analytical datasets."""
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            'value': [
                {'name': 'Dataset1', 'kind': 'EntitySet', 'url': 'Dataset1'}
            ]
        }
        mock_response.raise_for_status = AsyncMock()
        mock_get.return_value = mock_response
        
        result = await list_analytical_datasets(
            space_id='TEST_SPACE',
            asset_id='TEST_ASSET'
        )
        
        assert len(result) == 1
        assert 'Dataset1' in result[0].text

@pytest.mark.asyncio
async def test_query_analytical_data_with_filter():
    """Test querying analytical data with filter."""
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            'value': [
                {'Currency': 'USD', 'Amount': 1500.00}
            ]
        }
        mock_response.raise_for_status = AsyncMock()
        mock_get.return_value = mock_response
        
        result = await query_analytical_data(
            space_id='TEST_SPACE',
            asset_id='TEST_ASSET',
            entity_set='TEST_ENTITY',
            filter='Amount gt 1000'
        )
        
        assert len(result) == 1
        assert 'USD' in result[0].text
```

### Integration Tests

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_analytical_workflow():
    """Test complete analytical data access workflow."""
    # 1. List datasets
    datasets = await list_analytical_datasets(
        space_id='SAP_CONTENT',
        asset_id='SAP_SC_FI_AM_FINTRANSACTIONS'
    )
    assert len(datasets) > 0
    
    # 2. Get model metadata
    model = await get_analytical_model(
        space_id='SAP_CONTENT',
        asset_id='SAP_SC_FI_AM_FINTRANSACTIONS'
    )
    assert 'dimensions' in model[0].text
    
    # 3. Query data
    data = await query_analytical_data(
        space_id='SAP_CONTENT',
        asset_id='SAP_SC_FI_AM_FINTRANSACTIONS',
        entity_set='SAP_SC_FI_AM_FINTRANSACTIONS',
        top=10
    )
    assert len(data) > 0
```

---

## Usage Examples

### Example 1: Basic Data Query

```python
# List available datasets
datasets = await list_analytical_datasets(
    space_id="SAP_CONTENT",
    asset_id="SAP_SC_FI_AM_FINTRANSACTIONS"
)

# Query data with filters
data = await query_analytical_data(
    space_id="SAP_CONTENT",
    asset_id="SAP_SC_FI_AM_FINTRANSACTIONS",
    entity_set="SAP_SC_FI_AM_FINTRANSACTIONS",
    select="Currency,Amount,TransactionDate",
    filter="Amount gt 1000 and Currency eq 'USD'",
    orderby="Amount desc",
    top=100
)
```

### Example 2: Aggregation Query

```python
# Get aggregated data by currency
aggregated = await query_analytical_data(
    space_id="SAP_CONTENT",
    asset_id="SAP_SC_FI_AM_FINTRANSACTIONS",
    entity_set="SAP_SC_FI_AM_FINTRANSACTIONS",
    apply="groupby((Currency), aggregate(Amount with sum as TotalAmount, Amount with average as AvgAmount))"
)
```

### Example 3: Pagination

```python
# Paginate through large result set
page_size = 100
skip = 0

while True:
    data = await query_analytical_data(
        space_id="SAP_CONTENT",
        asset_id="SAP_SC_FI_AM_FINTRANSACTIONS",
        entity_set="SAP_SC_FI_AM_FINTRANSACTIONS",
        top=page_size,
        skip=skip,
        count=True
    )
    
    if not data or len(data) == 0:
        break
    
    # Process data
    process_data(data)
    
    skip += page_size
```

---

## Checklist

Before submitting implementation:

- [ ] All 4 tools implemented with proper type hints
- [ ] OAuth2 token management with automatic refresh
- [ ] Comprehensive error handling for all HTTP status codes
- [ ] OData query parameter validation
- [ ] Metadata parsing for dimensions and measures
- [ ] Pagination support for large result sets
- [ ] Unit tests with >90% coverage
- [ ] Integration tests with real SAP Datasphere tenant
- [ ] Documentation with usage examples
- [ ] Code follows Ruff linting standards
- [ ] All tools return JSON strings for MCP compatibility

---

## Next Steps

1. Implement all 4 tools in `analytical.py`
2. Add tools to `server.py`
3. Create unit tests
4. Run integration tests with real tenant
5. Update documentation
6. Proceed to Phase 5: Relational Data Access

---

**Document Version**: 1.0  
**Last Updated**: December 9, 2025  
**Related Documents**:
- SAP_DATASPHERE_ANALYTICAL_TOOLS_SPEC.md
- SAP_DATASPHERE_MCP_EXTRACTION_PLAN.md
