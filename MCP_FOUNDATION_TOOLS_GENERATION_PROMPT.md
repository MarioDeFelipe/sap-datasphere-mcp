# MCP Tool Generation Prompt - Phase 1: Foundation Tools

## Context

You are implementing **7 foundation tools** (Phase 1.1 + 1.2) for the SAP Datasphere MCP Server. These tools establish basic connectivity, authentication, and space discovery capabilities.

**Reference Document**: `SAP_DATASPHERE_FOUNDATION_TOOLS_SPEC.md`

---

## Implementation Requirements

### Framework & Standards
- **MCP Protocol**: Standard MCP (not FastMCP)
- **Python Version**: 3.10+
- **Package Manager**: uv
- **Linting**: Ruff (99 char line length, Google docstrings, single quotes)
- **Type Hints**: Full type annotations required
- **Return Format**: MCP TextContent with JSON strings

---

## Phase 1.1: Authentication & Connection Tools

### Tool 1: `test_connection`

```python
from mcp.types import Tool, TextContent
import httpx
import json
from datetime import datetime

# Tool definition
test_connection_tool = Tool(
    name="test_connection",
    description="Verify SAP Datasphere connectivity and OAuth2 authentication",
    inputSchema={
        "type": "object",
        "properties": {},
        "required": []
    }
)

async def test_connection() -> list[TextContent]:
    """
    Verify SAP Datasphere connectivity and authentication.
    
    Tests OAuth2 authentication and basic API connectivity by making a simple
    request to the consumption API endpoint.
    
    Returns:
        List of TextContent with JSON string containing connection status
    
    Example:
        result = await test_connection()
        # Returns: {"status": "connected", "authentication": "success", ...}
    """
    try:
        start_time = datetime.now()
        
        # Get OAuth2 token
        token = await token_manager.get_token()
        
        # Test endpoint
        test_url = f"{config.base_url}/api/v1/datasphere/consumption"
        
        async with httpx.AsyncClient(verify=config.verify_ssl) as client:
            response = await client.get(
                test_url,
                headers={
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/json'
                },
                timeout=config.timeout
            )
            
            response.raise_for_status()
        
        # Calculate response time
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Get token expiry info
        token_expires_in = int((token_manager.token_expiry - datetime.now()).total_seconds())
        
        result = {
            'status': 'connected',
            'tenant_url': config.base_url,
            'authentication': 'success',
            'token_valid': token_manager.is_token_valid(),
            'token_expires_in': token_expires_in,
            'api_version': 'v1',
            'test_endpoint': test_url,
            'response_time_ms': int(response_time)
        }
        
        return [TextContent(
            type='text',
            text=json.dumps(result, indent=2)
        )]
    
    except httpx.HTTPStatusError as e:
        error_result = {
            'status': 'failed',
            'error': handle_http_error(e)['error'],
            'details': handle_http_error(e)['details']
        }
        return [TextContent(
            type='text',
            text=json.dumps(error_result, indent=2)
        )]
    
    except httpx.TimeoutException:
        error_result = {
            'status': 'failed',
            'error': 'Connection timeout',
            'details': 'Could not reach SAP Datasphere within timeout period'
        }
        return [TextContent(
            type='text',
            text=json.dumps(error_result, indent=2)
        )]
    
    except Exception as e:
        error_result = {
            'status': 'failed',
            'error': 'Connection failed',
            'details': str(e)
        }
        return [TextContent(
            type='text',
            text=json.dumps(error_result, indent=2)
        )]
```

---

### Tool 2: `get_current_user`

```python
get_current_user_tool = Tool(
    name="get_current_user",
    description="Get information about the authenticated user/client",
    inputSchema={
        "type": "object",
        "properties": {},
        "required": []
    }
)

async def get_current_user() -> list[TextContent]:
    """
    Retrieve information about the authenticated user/client.
    
    Returns user identity, permissions, and assigned OAuth2 scopes.
    
    Returns:
        List of TextContent with JSON string containing user information
    
    Example:
        user = await get_current_user()
        # Returns: {"user_id": "...", "scopes": [...], ...}
    """
    try:
        token = await token_manager.get_token()
        
        # Try to get user info from API
        user_url = f"{config.base_url}/api/v1/datasphere/users/current"
        
        async with httpx.AsyncClient(verify=config.verify_ssl) as client:
            try:
                response = await client.get(
                    user_url,
                    headers={
                        'Authorization': f'Bearer {token}',
                        'Accept': 'application/json'
                    },
                    timeout=config.timeout
                )
                response.raise_for_status()
                user_data = response.json()
            
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    # Endpoint not available, derive from token/config
                    user_data = {
                        'user_id': config.client_id,
                        'user_type': 'technical_user',
                        'client_id': config.client_id,
                        'display_name': 'MCP Integration Client',
                        'email': None,
                        'tenant_id': extract_tenant_id(config.base_url),
                        'region': extract_region(config.base_url),
                        'scopes': ['DWC_CONSUMPTION', 'DWC_CATALOG_READ'],  # Default scopes
                        'permissions': {
                            'can_read_data': True,
                            'can_write_data': False,
                            'can_admin': False
                        }
                    }
                else:
                    raise
        
        return [TextContent(
            type='text',
            text=json.dumps(user_data, indent=2)
        )]
    
    except httpx.HTTPStatusError as e:
        error_result = handle_http_error(e)
        return [TextContent(
            type='text',
            text=json.dumps(error_result, indent=2)
        )]
    
    except Exception as e:
        error_result = {'error': str(e)}
        return [TextContent(
            type='text',
            text=json.dumps(error_result, indent=2)
        )]


def extract_tenant_id(base_url: str) -> str:
    """Extract tenant ID from base URL."""
    # Example: https://academydatasphere.eu10.hcs.cloud.sap -> academydatasphere
    parts = base_url.replace('https://', '').replace('http://', '').split('.')
    return parts[0] if parts else 'unknown'


def extract_region(base_url: str) -> str:
    """Extract region from base URL."""
    # Example: https://academydatasphere.eu10.hcs.cloud.sap -> eu10
    parts = base_url.replace('https://', '').replace('http://', '').split('.')
    return parts[1] if len(parts) > 1 else 'unknown'
```

---

### Tool 3: `get_tenant_info`

```python
get_tenant_info_tool = Tool(
    name="get_tenant_info",
    description="Get SAP Datasphere tenant configuration and information",
    inputSchema={
        "type": "object",
        "properties": {},
        "required": []
    }
)

async def get_tenant_info() -> list[TextContent]:
    """
    Retrieve SAP Datasphere tenant configuration.
    
    Returns tenant details including region, version, features, and resource usage.
    
    Returns:
        List of TextContent with JSON string containing tenant information
    
    Example:
        tenant = await get_tenant_info()
        # Returns: {"tenant_id": "...", "region": "...", ...}
    """
    try:
        token = await token_manager.get_token()
        tenant_url = f"{config.base_url}/api/v1/tenant"
        
        async with httpx.AsyncClient(verify=config.verify_ssl) as client:
            response = await client.get(
                tenant_url,
                headers={
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/json'
                },
                timeout=config.timeout
            )
            
            response.raise_for_status()
            tenant_data = response.json()
        
        return [TextContent(
            type='text',
            text=json.dumps(tenant_data, indent=2)
        )]
    
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            # Endpoint not available, return basic info
            tenant_data = {
                'tenant_id': extract_tenant_id(config.base_url),
                'tenant_url': config.base_url,
                'region': extract_region(config.base_url),
                'status': 'active',
                'note': 'Limited tenant information available'
            }
            return [TextContent(
                type='text',
                text=json.dumps(tenant_data, indent=2)
            )]
        
        error_result = handle_http_error(e)
        return [TextContent(
            type='text',
            text=json.dumps(error_result, indent=2)
        )]
    
    except Exception as e:
        error_result = {'error': str(e)}
        return [TextContent(
            type='text',
            text=json.dumps(error_result, indent=2)
        )]
```

---

### Tool 4: `get_available_scopes`

```python
get_available_scopes_tool = Tool(
    name="get_available_scopes",
    description="List all available OAuth2 scopes for SAP Datasphere",
    inputSchema={
        "type": "object",
        "properties": {},
        "required": []
    }
)

async def get_available_scopes() -> list[TextContent]:
    """
    List all available OAuth2 scopes for the SAP Datasphere tenant.
    
    Returns available scopes with descriptions and the current client's granted scopes.
    
    Returns:
        List of TextContent with JSON string containing scope information
    
    Example:
        scopes = await get_available_scopes()
        # Returns: {"scopes": [...], "current_client_scopes": [...]}
    """
    try:
        # Define standard SAP Datasphere scopes
        standard_scopes = [
            {
                'scope': 'DWC_CONSUMPTION',
                'name': 'Data Consumption',
                'description': 'Read access to consumption models (analytical and relational data)',
                'category': 'Data Access',
                'required_for': ['query_analytical_data', 'query_relational_data']
            },
            {
                'scope': 'DWC_CATALOG_READ',
                'name': 'Catalog Read',
                'description': 'Read access to data catalog and asset metadata',
                'category': 'Metadata',
                'required_for': ['list_catalog_assets', 'get_asset_details']
            },
            {
                'scope': 'DWC_REPOSITORY_READ',
                'name': 'Repository Read',
                'description': 'Read access to repository objects and definitions',
                'category': 'Repository',
                'required_for': ['list_repository_objects', 'get_object_definition']
            },
            {
                'scope': 'DWC_SPACE_READ',
                'name': 'Space Read',
                'description': 'Read access to space information and configuration',
                'category': 'Administration',
                'required_for': ['list_spaces', 'get_space_details']
            },
            {
                'scope': 'DWC_USER_READ',
                'name': 'User Read',
                'description': 'Read access to user information and permissions',
                'category': 'Administration',
                'required_for': ['list_users', 'get_user_details']
            },
            {
                'scope': 'DWC_ADMIN',
                'name': 'Administration',
                'description': 'Full administrative access to tenant configuration',
                'category': 'Administration',
                'required_for': ['tenant_configuration', 'user_management']
            }
        ]
        
        # Try to get current client's scopes from user info
        try:
            user_info = await get_current_user()
            user_data = json.loads(user_info[0].text)
            current_scopes = user_data.get('scopes', [])
        except:
            current_scopes = ['DWC_CONSUMPTION', 'DWC_CATALOG_READ']  # Default
        
        result = {
            'scopes': standard_scopes,
            'current_client_scopes': current_scopes
        }
        
        return [TextContent(
            type='text',
            text=json.dumps(result, indent=2)
        )]
    
    except Exception as e:
        error_result = {'error': str(e)}
        return [TextContent(
            type='text',
            text=json.dumps(error_result, indent=2)
        )]
```

---

## Phase 1.2: Basic Space Discovery

### Tool 5: `list_spaces`

```python
list_spaces_tool = Tool(
    name="list_spaces",
    description="List all accessible SAP Datasphere spaces",
    inputSchema={
        "type": "object",
        "properties": {
            "filter_expression": {
                "type": "string",
                "description": "OData filter expression (e.g., 'status eq Active')"
            },
            "select": {
                "type": "string",
                "description": "Comma-separated list of fields to return"
            },
            "top": {
                "type": "integer",
                "description": "Maximum number of results",
                "default": 50
            },
            "skip": {
                "type": "integer",
                "description": "Number of results to skip for pagination",
                "default": 0
            },
            "orderby": {
                "type": "string",
                "description": "Sort order (e.g., 'name asc')"
            }
        },
        "required": []
    }
)

async def list_spaces(
    filter_expression: str = None,
    select: str = None,
    top: int = 50,
    skip: int = 0,
    orderby: str = None
) -> list[TextContent]:
    """
    List all SAP Datasphere spaces accessible to the authenticated user.
    
    Args:
        filter_expression: OData filter (e.g., "status eq 'Active'")
        select: Comma-separated fields to return
        top: Maximum results (default: 50)
        skip: Results to skip for pagination (default: 0)
        orderby: Sort order (e.g., "name asc")
    
    Returns:
        List of TextContent with JSON string containing spaces
    
    Examples:
        # List all spaces
        spaces = await list_spaces()
        
        # List active spaces only
        spaces = await list_spaces(filter_expression="status eq 'Active'")
        
        # Paginate
        page1 = await list_spaces(top=10, skip=0)
        page2 = await list_spaces(top=10, skip=10)
    """
    try:
        token = await token_manager.get_token()
        spaces_url = f"{config.base_url}/api/v1/datasphere/spaces"
        
        # Build query parameters
        params = {}
        if filter_expression:
            params['$filter'] = filter_expression
        if select:
            params['$select'] = select
        if top:
            params['$top'] = top
        if skip:
            params['$skip'] = skip
        if orderby:
            params['$orderby'] = orderby
        
        async with httpx.AsyncClient(verify=config.verify_ssl) as client:
            response = await client.get(
                spaces_url,
                params=params,
                headers={
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/json'
                },
                timeout=config.timeout
            )
            
            response.raise_for_status()
            data = response.json()
        
        return [TextContent(
            type='text',
            text=json.dumps(data, indent=2)
        )]
    
    except httpx.HTTPStatusError as e:
        error_result = handle_http_error(e)
        return [TextContent(
            type='text',
            text=json.dumps(error_result, indent=2)
        )]
    
    except Exception as e:
        error_result = {'error': str(e)}
        return [TextContent(
            type='text',
            text=json.dumps(error_result, indent=2)
        )]
```


---

### Tool 6: `get_space_details`

```python
get_space_details_tool = Tool(
    name="get_space_details",
    description="Get detailed information about a specific SAP Datasphere space",
    inputSchema={
        "type": "object",
        "properties": {
            "space_id": {
                "type": "string",
                "description": "Space identifier (e.g., 'SAP_CONTENT')"
            },
            "expand": {
                "type": "string",
                "description": "Related entities to expand (e.g., 'users,objects')"
            }
        },
        "required": ["space_id"]
    }
)

async def get_space_details(
    space_id: str,
    expand: str = None
) -> list[TextContent]:
    """
    Get detailed information about a specific SAP Datasphere space.
    
    Args:
        space_id: Space identifier (e.g., "SAP_CONTENT")
        expand: Related entities to expand (e.g., "users,objects")
    
    Returns:
        List of TextContent with JSON string containing space details
    
    Examples:
        # Get space details
        space = await get_space_details(space_id="SAP_CONTENT")
        
        # Get space with expanded users
        space = await get_space_details(
            space_id="SAP_CONTENT",
            expand="users"
        )
    """
    try:
        token = await token_manager.get_token()
        space_url = f"{config.base_url}/api/v1/datasphere/spaces('{space_id}')"
        
        # Build query parameters
        params = {}
        if expand:
            params['$expand'] = expand
        
        async with httpx.AsyncClient(verify=config.verify_ssl) as client:
            response = await client.get(
                space_url,
                params=params,
                headers={
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/json'
                },
                timeout=config.timeout
            )
            
            response.raise_for_status()
            data = response.json()
        
        return [TextContent(
            type='text',
            text=json.dumps(data, indent=2)
        )]
    
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            error_result = {
                'error': f'Space not found: {space_id}',
                'details': 'Please check the space identifier'
            }
        else:
            error_result = handle_http_error(e)
        
        return [TextContent(
            type='text',
            text=json.dumps(error_result, indent=2)
        )]
    
    except Exception as e:
        error_result = {'error': str(e)}
        return [TextContent(
            type='text',
            text=json.dumps(error_result, indent=2)
        )]
```

---

### Tool 7: `get_space_permissions`

```python
get_space_permissions_tool = Tool(
    name="get_space_permissions",
    description="Check user permissions for a specific SAP Datasphere space",
    inputSchema={
        "type": "object",
        "properties": {
            "space_id": {
                "type": "string",
                "description": "Space identifier (e.g., 'SAP_CONTENT')"
            }
        },
        "required": ["space_id"]
    }
)

async def get_space_permissions(space_id: str) -> list[TextContent]:
    """
    Check the authenticated user's permissions for a specific space.
    
    Args:
        space_id: Space identifier (e.g., "SAP_CONTENT")
    
    Returns:
        List of TextContent with JSON string containing permissions
    
    Example:
        perms = await get_space_permissions(space_id="SAP_CONTENT")
        # Returns: {"permissions": {"can_read": true, ...}, ...}
    """
    try:
        token = await token_manager.get_token()
        
        # Try dedicated permissions endpoint first
        perms_url = f"{config.base_url}/api/v1/datasphere/spaces('{space_id}')/permissions"
        
        async with httpx.AsyncClient(verify=config.verify_ssl) as client:
            try:
                response = await client.get(
                    perms_url,
                    headers={
                        'Authorization': f'Bearer {token}',
                        'Accept': 'application/json'
                    },
                    timeout=config.timeout
                )
                response.raise_for_status()
                perms_data = response.json()
            
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    # Permissions endpoint not available, get from space details
                    space_url = f"{config.base_url}/api/v1/datasphere/spaces('{space_id}')"
                    response = await client.get(
                        space_url,
                        params={'$select': 'id,name,permissions'},
                        headers={
                            'Authorization': f'Bearer {token}',
                            'Accept': 'application/json'
                        },
                        timeout=config.timeout
                    )
                    response.raise_for_status()
                    space_data = response.json()
                    
                    # Extract permissions
                    perms_data = {
                        'space_id': space_id,
                        'space_name': space_data.get('name', space_id),
                        'permissions': space_data.get('permissions', {}),
                        'access_level': determine_access_level(space_data.get('permissions', {}))
                    }
                else:
                    raise
        
        return [TextContent(
            type='text',
            text=json.dumps(perms_data, indent=2)
        )]
    
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            error_result = {
                'error': f'Space not found: {space_id}',
                'details': 'Please check the space identifier'
            }
        elif e.response.status_code == 403:
            # No access - return minimal permissions
            error_result = {
                'space_id': space_id,
                'permissions': {
                    'can_read': False,
                    'can_write': False,
                    'can_delete': False,
                    'can_admin': False
                },
                'access_level': 'No Access',
                'error': 'Access denied to this space'
            }
        else:
            error_result = handle_http_error(e)
        
        return [TextContent(
            type='text',
            text=json.dumps(error_result, indent=2)
        )]
    
    except Exception as e:
        error_result = {'error': str(e)}
        return [TextContent(
            type='text',
            text=json.dumps(error_result, indent=2)
        )]


def determine_access_level(permissions: dict) -> str:
    """Determine access level from permissions."""
    if permissions.get('can_admin'):
        return 'Admin'
    elif permissions.get('can_write'):
        return 'Read-Write'
    elif permissions.get('can_read'):
        return 'Read-Only'
    else:
        return 'No Access'
```

---

## Helper Functions

### OAuth2 Token Manager

```python
from datetime import datetime, timedelta
from typing import Optional
import httpx

class OAuth2TokenManager:
    """Manage OAuth2 token lifecycle with automatic refresh."""
    
    def __init__(self, token_url: str, client_id: str, client_secret: str):
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
    
    async def get_token(self) -> str:
        """Get valid access token, refreshing if necessary."""
        if self.access_token and self.token_expiry and self.token_expiry > datetime.now():
            return self.access_token
        
        return await self.refresh_token()
    
    async def refresh_token(self) -> str:
        """Refresh OAuth2 access token using client credentials flow."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    'grant_type': 'client_credentials',
                    'client_id': self.client_id,
                    'client_secret': self.client_secret
                },
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30.0
            )
            
            response.raise_for_status()
            token_data = response.json()
            
            self.access_token = token_data['access_token']
            expires_in = token_data.get('expires_in', 3600)
            # Refresh 60 seconds before expiry
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in - 60)
            
            return self.access_token
    
    def is_token_valid(self) -> bool:
        """Check if current token is still valid."""
        return (
            self.access_token is not None and
            self.token_expiry is not None and
            self.token_expiry > datetime.now()
        )
```

### Error Handler

```python
def handle_http_error(error: httpx.HTTPStatusError) -> dict:
    """Handle HTTP errors with user-friendly messages."""
    status_code = error.response.status_code
    
    error_messages = {
        401: 'Authentication failed. Please check your credentials.',
        403: 'Access denied. Insufficient permissions.',
        404: 'Resource not found. Please check the identifier.',
        429: 'Rate limit exceeded. Please try again later.',
        500: 'SAP Datasphere server error. Please try again later.',
        503: 'Service temporarily unavailable. Please try again later.'
    }
    
    message = error_messages.get(status_code, f'HTTP {status_code} error occurred')
    
    return {
        'error': message,
        'status_code': status_code,
        'details': error.response.text[:200]  # Limit error details
    }
```

### Configuration Model

```python
from pydantic import BaseModel, Field

class DatasphereConfig(BaseModel):
    """Configuration for SAP Datasphere connection."""
    
    base_url: str = Field(..., description='SAP Datasphere base URL')
    token_url: str = Field(..., description='OAuth2 token endpoint')
    client_id: str = Field(..., description='OAuth2 client ID')
    client_secret: str = Field(..., description='OAuth2 client secret')
    timeout: int = Field(30, description='Request timeout in seconds')
    max_retries: int = Field(3, description='Maximum retry attempts')
    verify_ssl: bool = Field(True, description='Verify SSL certificates')
```

---

## MCP Server Setup

### Tool Registration

```python
from mcp.server import Server
from mcp.types import Tool

# Initialize server
server = Server("sap-datasphere-mcp-server")

# Register all tools
tools = [
    test_connection_tool,
    get_current_user_tool,
    get_tenant_info_tool,
    get_available_scopes_tool,
    list_spaces_tool,
    get_space_details_tool,
    get_space_permissions_tool
]

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    return tools

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle tool calls."""
    if name == "test_connection":
        return await test_connection()
    elif name == "get_current_user":
        return await get_current_user()
    elif name == "get_tenant_info":
        return await get_tenant_info()
    elif name == "get_available_scopes":
        return await get_available_scopes()
    elif name == "list_spaces":
        return await list_spaces(**arguments)
    elif name == "get_space_details":
        return await get_space_details(**arguments)
    elif name == "get_space_permissions":
        return await get_space_permissions(**arguments)
    else:
        return [TextContent(
            type='text',
            text=json.dumps({'error': f'Unknown tool: {name}'})
        )]
```

### Configuration Loading

```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize configuration
config = DatasphereConfig(
    base_url=os.getenv('DATASPHERE_BASE_URL'),
    token_url=os.getenv('DATASPHERE_TOKEN_URL'),
    client_id=os.getenv('DATASPHERE_CLIENT_ID'),
    client_secret=os.getenv('DATASPHERE_CLIENT_SECRET'),
    timeout=int(os.getenv('DATASPHERE_TIMEOUT', '30')),
    verify_ssl=os.getenv('DATASPHERE_VERIFY_SSL', 'true').lower() == 'true'
)

# Initialize token manager
token_manager = OAuth2TokenManager(
    token_url=config.token_url,
    client_id=config.client_id,
    client_secret=config.client_secret
)
```

---

## Testing Examples

### Unit Tests

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_test_connection_success():
    """Test successful connection."""
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'value': []}
        mock_response.raise_for_status = AsyncMock()
        mock_get.return_value = mock_response
        
        result = await test_connection()
        data = json.loads(result[0].text)
        
        assert data['status'] == 'connected'
        assert data['authentication'] == 'success'

@pytest.mark.asyncio
async def test_list_spaces():
    """Test listing spaces."""
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            'value': [
                {'id': 'SPACE1', 'name': 'Space 1'},
                {'id': 'SPACE2', 'name': 'Space 2'}
            ]
        }
        mock_response.raise_for_status = AsyncMock()
        mock_get.return_value = mock_response
        
        result = await list_spaces()
        data = json.loads(result[0].text)
        
        assert len(data['value']) == 2
        assert data['value'][0]['id'] == 'SPACE1'

@pytest.mark.asyncio
async def test_get_space_details():
    """Test getting space details."""
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            'id': 'SAP_CONTENT',
            'name': 'SAP Content',
            'status': 'Active'
        }
        mock_response.raise_for_status = AsyncMock()
        mock_get.return_value = mock_response
        
        result = await get_space_details(space_id='SAP_CONTENT')
        data = json.loads(result[0].text)
        
        assert data['id'] == 'SAP_CONTENT'
        assert data['status'] == 'Active'
```

### Integration Tests

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_workflow():
    """Test complete authentication and discovery workflow."""
    # 1. Test connection
    conn_result = await test_connection()
    conn_data = json.loads(conn_result[0].text)
    assert conn_data['status'] == 'connected'
    
    # 2. Get current user
    user_result = await get_current_user()
    user_data = json.loads(user_result[0].text)
    assert 'user_id' in user_data
    
    # 3. Get tenant info
    tenant_result = await get_tenant_info()
    tenant_data = json.loads(tenant_result[0].text)
    assert 'tenant_id' in tenant_data
    
    # 4. List spaces
    spaces_result = await list_spaces()
    spaces_data = json.loads(spaces_result[0].text)
    assert len(spaces_data['value']) > 0
    
    # 5. Get space details
    first_space = spaces_data['value'][0]
    space_result = await get_space_details(space_id=first_space['id'])
    space_data = json.loads(space_result[0].text)
    assert space_data['id'] == first_space['id']
    
    # 6. Check permissions
    perms_result = await get_space_permissions(space_id=first_space['id'])
    perms_data = json.loads(perms_result[0].text)
    assert 'permissions' in perms_data
```

---

## Usage Examples

### Example 1: Basic Connection Test

```python
# Test connection
result = await test_connection()
data = json.loads(result[0].text)

if data['status'] == 'connected':
    print(f"✓ Connected to {data['tenant_url']}")
    print(f"✓ Token expires in {data['token_expires_in']} seconds")
else:
    print(f"✗ Connection failed: {data['error']}")
```

### Example 2: Discover Spaces

```python
# List all spaces
spaces_result = await list_spaces()
spaces = json.loads(spaces_result[0].text)

print(f"Found {len(spaces['value'])} spaces:")
for space in spaces['value']:
    print(f"  - {space['name']} ({space['id']}): {space['status']}")
```

### Example 3: Check Permissions

```python
# Get space permissions
perms_result = await get_space_permissions(space_id="SAP_CONTENT")
perms = json.loads(perms_result[0].text)

print(f"Permissions for {perms['space_name']}:")
print(f"  Read: {perms['permissions']['can_read']}")
print(f"  Write: {perms['permissions']['can_write']}")
print(f"  Admin: {perms['permissions']['can_admin']}")
print(f"  Access Level: {perms['access_level']}")
```

---

## Checklist

Before submitting implementation:

- [ ] All 7 tools implemented with proper type hints
- [ ] OAuth2 token management with automatic refresh
- [ ] Comprehensive error handling for all HTTP status codes
- [ ] Configuration model with Pydantic
- [ ] Unit tests with >90% coverage
- [ ] Integration tests with real SAP Datasphere tenant
- [ ] Documentation with usage examples
- [ ] Code follows Ruff linting standards
- [ ] All tools return MCP TextContent with JSON strings
- [ ] Environment variable configuration
- [ ] SSL verification configurable
- [ ] Timeout handling

---

## Next Steps

1. Implement all 7 tools following the templates
2. Set up OAuth2 token manager
3. Create configuration model
4. Add error handling utilities
5. Write unit tests
6. Run integration tests with real tenant
7. Update documentation
8. Proceed to Phase 2: Catalog & Asset Discovery

---

**Document Version**: 1.0  
**Last Updated**: December 9, 2025  
**Related Documents**:
- SAP_DATASPHERE_FOUNDATION_TOOLS_SPEC.md
- SAP_DATASPHERE_MCP_EXTRACTION_PLAN.md
