# MCP Foundation Tools Generation Prompt - Phase 1.1 & 1.2

## Context

You are implementing **7 foundation tools** for the SAP Datasphere MCP Server that establish basic connectivity, authentication, and space discovery. These are CRITICAL and HIGH priority tools that form the foundation for all other capabilities.

**Reference Document**: `SAP_DATASPHERE_FOUNDATION_TOOLS_SPEC.md`

---

## Implementation Requirements

### Framework & Standards
- **Framework**: FastMCP (Python MCP framework) 
- **Python Version**: 3.10+
- **Package Manager**: uv
- **Linting**: Ruff (99 char line length, Google docstrings, single quotes)
- **Type Hints**: Full type annotations required
- **Return Format**: JSON strings (for MCP compatibility)

---

## Phase 1.1: Authentication & Connection Tools

### Tool 1: `test_connection`

```python
@server.call_tool()
async def test_connection() -> list[types.TextContent]:
    """
    Test connection to SAP Datasphere and verify OAuth authentication.
    
    Verifies connectivity, token validity, and basic system access.
    
    Returns:
        JSON string containing connection status and authentication details
    
    Example:
        ```python
        status = await test_connection()
        ```
    """
    try:
        # Get OAuth2 token
        token = await get_oauth_token()
        
        # Test basic API access
        async with httpx.AsyncClient() as client:
            # Try to access tenant info or spaces endpoint
            response = await client.get(
                f"{config.base_url}/api/v1/datasphere/consumption/catalog/spaces",
                headers={
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/json'
                },
                timeout=30.0
            )
            
            response.raise_for_status()
        
        # Get token info
        token_info = await get_token_info(token)
        
        result = {
            'status': 'connected',
            'tenant_url': config.base_url,
            'authenticated_user': token_info.get('user_name', 'Unknown'),
            'token_valid': True,
            'token_expires_at': token_info.get('exp'),
            'available_scopes': token_info.get('scope', []),
            'connection_test_timestamp': datetime.now().isoformat()
        }
        
        return [types.TextContent(
            type='text',
            text=json.dumps(result, indent=2)
        )]
    
    except httpx.HTTPStatusError as e:
        error_result = {
            'status': 'failed',
            'error': f'HTTP {e.response.status_code}',
            'message': 'Authentication or connectivity failed',
            'suggestion': 'Check OAuth2 credentials and network connectivity'
        }
        
        return [types.TextContent(
            type='text',
            text=json.dumps(error_result, indent=2)
        )]
    
    except Exception as e:
        error_result = {
            'status': 'error',
            'error': str(e),
            'message': 'Connection test failed'
        }
        
        return [types.TextContent(
            type='text',
            text=json.dumps(error_result, indent=2)
        )]
```

### Tool 2: `get_current_user`

```python
@server.call_tool()
async def get_current_user() -> list[types.TextContent]:
    """
    Get information about the currently authenticated user.
    
    Returns user details, roles, and permissions.
    
    Returns:
        JSON string containing user information and permissions
    
    Example:
        ```python
        user_info = await get_current_user()
        ```
    """
    try:
        token = await get_oauth_token()
        
        # Get user info from token or user endpoint
        token_info = await get_token_info(token)
        
        # Try to get additional user details from API
        user_details = {}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{config.base_url}/api/v1/tenant/user",
                    headers={
                        'Authorization': f'Bearer {token}',
                        'Accept': 'application/json'
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    user_details = response.json()
        except:
            pass  # Fallback to token info only
        
        result = {
            'user_id': token_info.get('user_id') or user_details.get('userId'),
            'email': token_info.get('user_name') or user_details.get('email'),
            'display_name': user_details.get('displayName', 'Technical User'),
            'roles': token_info.get('roles', []),
            'permissions': token_info.get('scope', []),
            'tenant_id': token_info.get('zid'),
            'last_login': user_details.get('lastLogin'),
            'account_status': user_details.get('status', 'Active'),
            'token_issued_at': token_info.get('iat'),
            'token_expires_at': token_info.get('exp')
        }
        
        return [types.TextContent(
            type='text',
            text=json.dumps(result, indent=2)
        )]
    
    except Exception as e:
        return [types.TextContent(
            type='text',
            text=json.dumps({'error': str(e)}, indent=2)
        )]
```

### Tool 3: `get_tenant_info`

```python
@server.call_tool()
async def get_tenant_info() -> list[types.TextContent]:
    """
    Get SAP Datasphere tenant configuration and system information.
    
    Returns tenant details, quotas, and system status.
    
    Returns:
        JSON string containing tenant configuration
    
    Example:
        ```python
        tenant_info = await get_tenant_info()
        ```
    """
    try:
        token = await get_oauth_token()
        
        async with httpx.AsyncClient() as client:
            # Try tenant endpoint
            response = await client.get(
                f"{config.base_url}/api/v1/tenant",
                headers={
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/json'
                },
                timeout=30.0
            )
            
            response.raise_for_status()
            tenant_data = response.json()
        
        # Get additional info from spaces endpoint
        spaces_count = 0
        try:
            spaces_response = await client.get(
                f"{config.base_url}/api/v1/datasphere/consumption/catalog/spaces",
                headers={
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/json'
                },
                timeout=30.0
            )
            
            if spaces_response.status_code == 200:
                spaces_data = spaces_response.json()
                spaces_count = len(spaces_data.get('value', []))
        except:
            pass
        
        result = {
            'tenant_id': tenant_data.get('id'),
            'tenant_name': tenant_data.get('name'),
            'region': tenant_data.get('region'),
            'datasphere_version': tenant_data.get('version'),
            'license_type': tenant_data.get('licenseType'),
            'storage_quota_gb': tenant_data.get('storageQuota'),
            'storage_used_gb': tenant_data.get('storageUsed'),
            'user_count': tenant_data.get('userCount'),
            'space_count': spaces_count,
            'features_enabled': tenant_data.get('features', []),
            'maintenance_window': tenant_data.get('maintenanceWindow'),
            'created_date': tenant_data.get('createdAt'),
            'last_updated': tenant_data.get('updatedAt')
        }
        
        return [types.TextContent(
            type='text',
            text=json.dumps(result, indent=2)
        )]
    
    except httpx.HTTPStatusError as e:
        error_msg = handle_http_error(e, 'tenant', 'info')
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

### Tool 4: `get_available_scopes`

```python
@server.call_tool()
async def get_available_scopes() -> list[types.TextContent]:
    """
    List available OAuth2 scopes for the current user.
    
    Shows granted and available scopes with descriptions.
    
    Returns:
        JSON string containing scope information
    
    Example:
        ```python
        scopes = await get_available_scopes()
        ```
    """
    try:
        token = await get_oauth_token()
        token_info = await get_token_info(token)
        
        # Current token scopes
        current_scopes = token_info.get('scope', [])
        if isinstance(current_scopes, str):
            current_scopes = current_scopes.split(' ')
        
        # Define known scopes and descriptions
        known_scopes = {
            'DWC_CONSUMPTION': 'Read access to consumption models and data',
            'DWC_CATALOG': 'Read access to catalog metadata and assets',
            'DWC_REPOSITORY': 'Read access to repository objects and definitions',
            'DWC_ADMIN': 'Administrative access to spaces and users',
            'DWC_MODELING': 'Create and modify data models',
            'DWC_DATA_INTEGRATION': 'Data integration and ETL operations'
        }
        
        available_scopes = []
        for scope, description in known_scopes.items():
            available_scopes.append({
                'scope': scope,
                'description': description,
                'granted': scope in current_scopes
            })
        
        result = {
            'available_scopes': available_scopes,
            'token_scopes': current_scopes,
            'scope_check_timestamp': datetime.now().isoformat(),
            'token_expires_at': token_info.get('exp')
        }
        
        return [types.TextContent(
            type='text',
            text=json.dumps(result, indent=2)
        )]
    
    except Exception as e:
        return [types.TextContent(
            type='text',
            text=json.dumps({'error': str(e)}, indent=2)
        )]
```

---

## Phase 1.2: Basic Space Discovery Tools

### Tool 5: `list_spaces`

```python
@server.call_tool()
async def list_spaces(
    include_details: bool = False,
    top: int = 50,
    skip: int = 0
) -> list[types.TextContent]:
    """
    List all accessible SAP Datasphere spaces.
    
    Args:
        include_details: Include detailed space information (default: False)
        top: Maximum number of results (default: 50)
        skip: Number of results to skip for pagination (default: 0)
    
    Returns:
        JSON string containing list of spaces with metadata
    
    Example:
        ```python
        spaces = await list_spaces(include_details=True, top=20)
        ```
    """
    try:
        token = await get_oauth_token()
        
        # Build query parameters
        params = {
            '$top': top,
            '$skip': skip
        }
        
        if include_details:
            params['$expand'] = 'assets'
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{config.base_url}/api/v1/datasphere/consumption/catalog/spaces",
                params=params,
                headers={
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/json'
                },
                timeout=30.0
            )
            
            response.raise_for_status()
            data = response.json()
        
        # Process spaces data
        spaces = []
        for space in data.get('value', []):
            space_info = {
                'spaceId': space.get('spaceId'),
                'spaceName': space.get('spaceName'),
                'description': space.get('description'),
                'status': space.get('status', 'ACTIVE'),
                'owner': space.get('owner'),
                'created_date': space.get('createdDate'),
                'permissions': space.get('permissions', ['READ'])
            }
            
            if include_details:
                # Add asset counts
                assets = space.get('assets', [])
                space_info.update({
                    'asset_count': len(assets),
                    'table_count': len([a for a in assets if a.get('assetType') == 'Table']),
                    'view_count': len([a for a in assets if a.get('assetType') == 'View']),
                    'model_count': len([a for a in assets if a.get('assetType') == 'AnalyticalModel'])
                })
            
            spaces.append(space_info)
        
        result = {
            'spaces': spaces,
            'total_count': data.get('@odata.count', len(spaces)),
            'accessible_count': len(spaces),
            'query_timestamp': datetime.now().isoformat()
        }
        
        return [types.TextContent(
            type='text',
            text=json.dumps(result, indent=2)
        )]
    
    except httpx.HTTPStatusError as e:
        error_msg = handle_http_error(e, 'spaces', 'list')
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

### Tool 6: `get_space_info`

```python
@server.call_tool()
async def get_space_info(space_id: str) -> list[types.TextContent]:
    """
    Get comprehensive information about a specific SAP Datasphere space.
    
    Args:
        space_id: Space identifier (e.g., "SAP_CONTENT")
    
    Returns:
        JSON string containing detailed space information
    
    Example:
        ```python
        space_info = await get_space_info(space_id="SAP_CONTENT")
        ```
    """
    try:
        token = await get_oauth_token()
        
        async with httpx.AsyncClient() as client:
            # Get space details
            response = await client.get(
                f"{config.base_url}/api/v1/datasphere/consumption/catalog/spaces('{space_id}')",
                params={'$expand': 'assets'},
                headers={
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/json'
                },
                timeout=30.0
            )
            
            response.raise_for_status()
            space_data = response.json()
        
        # Process assets
        assets = space_data.get('assets', [])
        asset_summary = {
            'total_assets': len(assets),
            'analytical_models': len([a for a in assets if a.get('assetType') == 'AnalyticalModel']),
            'tables': len([a for a in assets if a.get('assetType') == 'Table']),
            'views': len([a for a in assets if a.get('assetType') == 'View']),
            'exposed_for_consumption': len([a for a in assets if a.get('exposedForConsumption')])
        }
        
        result = {
            'spaceId': space_data.get('spaceId'),
            'spaceName': space_data.get('spaceName'),
            'description': space_data.get('description'),
            'status': space_data.get('status'),
            'owner': space_data.get('owner'),
            'created_date': space_data.get('createdDate'),
            'modified_date': space_data.get('modifiedDate'),
            'size_mb': space_data.get('sizeMB'),
            'asset_summary': asset_summary,
            'permissions': {
                'current_user': space_data.get('permissions', []),
                'space_roles': space_data.get('roles', [])
            },
            'connections': space_data.get('connections', []),
            'metadata_url': f"/api/v1/datasphere/consumption/catalog/spaces('{space_id}')/$metadata"
        }
        
        return [types.TextContent(
            type='text',
            text=json.dumps(result, indent=2)
        )]
    
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            error_msg = f'Space {space_id} not found or not accessible'
        else:
            error_msg = handle_http_error(e, space_id, 'space')
        
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

### Tool 7: `search_tables`

```python
@server.call_tool()
async def search_tables(
    search_term: str,
    space_id: Optional[str] = None,
    asset_types: Optional[List[str]] = None,
    top: int = 50
) -> list[types.TextContent]:
    """
    Search for tables and views across spaces by name or description.
    
    Args:
        search_term: Keyword to search for in table names and descriptions
        space_id: Optional space to filter results (e.g., "SAP_CONTENT")
        asset_types: Optional asset types to filter (e.g., ["Table", "View"])
        top: Maximum number of results (default: 50)
    
    Returns:
        JSON string containing search results
    
    Example:
        ```python
        results = await search_tables(
            search_term="customer",
            space_id="SAP_CONTENT",
            asset_types=["Table"]
        )
        ```
    """
    try:
        token = await get_oauth_token()
        
        # Build filter expression
        filters = []
        
        # Search term filter
        search_filter = f"(contains(assetName, '{search_term}') or contains(description, '{search_term}'))"
        filters.append(search_filter)
        
        # Space filter
        if space_id:
            filters.append(f"spaceId eq '{space_id}'")
        
        # Asset type filter
        if asset_types:
            type_filters = " or ".join([f"assetType eq '{t}'" for t in asset_types])
            filters.append(f"({type_filters})")
        else:
            # Default to tables and views
            filters.append("(assetType eq 'Table' or assetType eq 'View')")
        
        filter_expression = " and ".join(filters)
        
        params = {
            '$filter': filter_expression,
            '$top': top,
            '$expand': 'metadata'
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{config.base_url}/api/v1/datasphere/consumption/catalog/assets",
                params=params,
                headers={
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/json'
                },
                timeout=30.0
            )
            
            response.raise_for_status()
            data = response.json()
        
        # Process results
        results = []
        for asset in data.get('value', []):
            result_item = {
                'assetId': asset.get('assetId'),
                'assetName': asset.get('assetName'),
                'spaceId': asset.get('spaceId'),
                'spaceName': asset.get('spaceName'),
                'assetType': asset.get('assetType'),
                'description': asset.get('description'),
                'row_count': asset.get('rowCount'),
                'consumption_urls': {
                    'analytical': asset.get('analyticalConsumptionUrl'),
                    'relational': asset.get('relationalConsumptionUrl')
                }
            }
            
            # Add column information if available
            metadata = asset.get('metadata', {})
            if 'columns' in metadata:
                result_item['columns'] = metadata['columns'][:5]  # First 5 columns
                result_item['total_columns'] = len(metadata['columns'])
            
            results.append(result_item)
        
        search_result = {
            'search_term': search_term,
            'filters': {
                'space_id': space_id,
                'asset_types': asset_types
            },
            'results': results,
            'total_matches': len(results),
            'search_timestamp': datetime.now().isoformat()
        }
        
        return [types.TextContent(
            type='text',
            text=json.dumps(search_result, indent=2)
        )]
    
    except httpx.HTTPStatusError as e:
        error_msg = handle_http_error(e, search_term, 'search')
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

### Token Management
```python
from datetime import datetime, timedelta
import base64
import json

async def get_token_info(token: str) -> dict:
    """Decode JWT token to get user information."""
    try:
        # JWT tokens have 3 parts separated by dots
        parts = token.split('.')
        if len(parts) != 3:
            return {}
        
        # Decode the payload (second part)
        payload = parts[1]
        # Add padding if needed
        payload += '=' * (4 - len(payload) % 4)
        
        decoded = base64.b64decode(payload)
        return json.loads(decoded)
    
    except Exception:
        return {}

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
```

### Error Handling
```python
def handle_http_error(error: httpx.HTTPStatusError, resource: str, operation: str) -> str:
    """Handle HTTP errors with user-friendly messages."""
    status_code = error.response.status_code
    
    if status_code == 401:
        return 'Authentication failed. Please check OAuth2 credentials.'
    elif status_code == 403:
        return f'Access denied to {resource}. Check user permissions.'
    elif status_code == 404:
        return f'{resource.title()} not found or not accessible.'
    elif status_code == 429:
        return 'Rate limit exceeded. Please try again later.'
    elif status_code == 500:
        return 'SAP Datasphere server error. Please try again later.'
    else:
        return f'HTTP {status_code}: {error.response.text}'
```

---

## Configuration
```python
from pydantic import BaseModel

class FoundationConfig(BaseModel):
    """Configuration for foundation tools."""
    
    base_url: str = Field(..., description='SAP Datasphere base URL')
    client_id: str = Field(..., description='OAuth2 client ID')
    client_secret: str = Field(..., description='OAuth2 client secret')
    token_url: str = Field(..., description='OAuth2 token endpoint')
    default_timeout: int = Field(30, description='Default request timeout')
    max_retries: int = Field(3, description='Maximum retry attempts')
```

---

## Testing Examples

### Unit Tests
```python
@pytest.mark.asyncio
async def test_connection():
    """Test connection to SAP Datasphere."""
    result = await test_connection()
    assert len(result) == 1
    data = json.loads(result[0].text)
    assert data['status'] == 'connected'

@pytest.mark.asyncio
async def test_list_spaces():
    """Test listing spaces."""
    result = await list_spaces(top=10)
    assert len(result) == 1
    data = json.loads(result[0].text)
    assert 'spaces' in data
    assert len(data['spaces']) > 0
```

---

## Checklist

- [ ] All 7 foundation tools implemented
- [ ] OAuth2 token management with auto-refresh
- [ ] JWT token decoding for user info
- [ ] Comprehensive error handling
- [ ] Space discovery and search capabilities
- [ ] Unit tests with >90% coverage
- [ ] Integration tests with real tenant
- [ ] Documentation with usage examples
- [ ] Code follows Ruff linting standards
- [ ] All tools return JSON strings for MCP compatibility

---

**Document Version**: 1.0  
**Last Updated**: December 9, 2025  
**Related Documents**:
- SAP_DATASPHERE_FOUNDATION_TOOLS_SPEC.md
- SAP_DATASPHERE_MCP_EXTRACTION_PLAN.md