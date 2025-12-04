# MCP Tool Generation Prompt for SAP Datasphere Catalog Tools

## Context

You are building an MCP (Model Context Protocol) server for SAP Datasphere that provides AI assistants with access to SAP Datasphere's catalog and data consumption APIs. This prompt will guide you to generate the four core catalog browsing tools.

---

## Project Setup

### Technology Stack
- **Framework**: FastMCP (Python MCP framework)
- **Language**: Python 3.10+
- **Authentication**: OAuth2 Bearer Token
- **API Protocol**: OData v4 (REST/JSON)
- **Package Manager**: uv

### Dependencies
```toml
[project]
name = "awslabs.sap-datasphere-mcp-server"
version = "0.1.0"
dependencies = [
    "fastmcp>=0.1.0",
    "requests>=2.31.0",
    "pydantic>=2.0.0",
    "loguru>=0.7.0",
]
```

---

## Authentication Configuration

The MCP server needs to authenticate with SAP Datasphere using OAuth2:

```python
from pydantic import BaseModel, Field
from typing import Optional
import requests
from datetime import datetime, timedelta

class DatasphereConfig(BaseModel):
    """Configuration for SAP Datasphere connection"""
    base_url: str = Field(..., description="SAP Datasphere tenant URL")
    client_id: str = Field(..., description="OAuth2 client ID")
    client_secret: str = Field(..., description="OAuth2 client secret")
    token_url: str = Field(..., description="OAuth2 token endpoint URL")

class DatasphereClient:
    """Client for SAP Datasphere API with OAuth2 authentication"""
    
    def __init__(self, config: DatasphereConfig):
        self.config = config
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        self.session = requests.Session()
    
    def authenticate(self) -> bool:
        """Obtain OAuth2 access token"""
        try:
            response = requests.post(
                self.config.token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.config.client_id,
                    "client_secret": self.config.client_secret
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30
            )
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
            
            # Set authorization header for session
            self.session.headers.update({
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/json"
            })
            
            return True
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False
    
    def ensure_authenticated(self):
        """Ensure we have a valid token, refresh if needed"""
        if not self.access_token or datetime.now() >= self.token_expires_at:
            self.authenticate()
    
    def get(self, endpoint: str, params: dict = None) -> dict:
        """Make authenticated GET request"""
        self.ensure_authenticated()
        
        url = f"{self.config.base_url.rstrip('/')}{endpoint}"
        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        return response.json()
```

---

## Tool Specifications

### Tool 1: `list_catalog_assets`

**Purpose**: Browse all assets across all spaces

**API Endpoint**: `GET /api/v1/datasphere/consumption/catalog/assets`

**Input Parameters**:
```python
from typing import Optional, List
from pydantic import BaseModel, Field

class ListCatalogAssetsInput(BaseModel):
    """Input for listing catalog assets"""
    select_fields: Optional[List[str]] = Field(
        None,
        description="Specific fields to return (e.g., ['name', 'description', 'spaceId'])"
    )
    filter_expression: Optional[str] = Field(
        None,
        description="OData filter expression (e.g., \"spaceId eq 'SAP_CONTENT'\")"
    )
    top: Optional[int] = Field(
        50,
        description="Maximum number of results to return",
        ge=1,
        le=1000
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
```

**Expected Output**:
```python
class AssetSummary(BaseModel):
    """Summary information for a catalog asset"""
    id: str
    name: str
    description: Optional[str]
    space_id: str
    space_name: Optional[str]
    asset_type: str
    exposed_for_consumption: bool
    analytical_consumption_url: Optional[str]
    relational_consumption_url: Optional[str]
    created_at: Optional[str]
    modified_at: Optional[str]

class ListCatalogAssetsOutput(BaseModel):
    """Output from listing catalog assets"""
    assets: List[AssetSummary]
    total_count: Optional[int]
    has_more: bool
```

**Implementation Template**:
```python
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio

# Initialize MCP server
mcp = Server("sap-datasphere")

# Initialize Datasphere client (from environment or config)
datasphere_client = DatasphereClient(
    DatasphereConfig(
        base_url=os.getenv("DATASPHERE_BASE_URL"),
        client_id=os.getenv("DATASPHERE_CLIENT_ID"),
        client_secret=os.getenv("DATASPHERE_CLIENT_SECRET"),
        token_url=os.getenv("DATASPHERE_TOKEN_URL")
    )
)

@mcp.tool()
def list_catalog_assets(
    select_fields: Optional[List[str]] = None,
    filter_expression: Optional[str] = None,
    top: int = 50,
    skip: int = 0,
    include_count: bool = False
) -> str:
    """
    Browse all assets across all spaces in SAP Datasphere catalog.
    
    This tool retrieves a list of all data assets (tables, views, analytical models)
    that the authenticated user has access to across all spaces.
    
    Args:
        select_fields: Specific fields to return (e.g., ['name', 'description', 'spaceId'])
        filter_expression: OData filter expression (e.g., "spaceId eq 'SAP_CONTENT'")
        top: Maximum number of results to return (default: 50, max: 1000)
        skip: Number of results to skip for pagination (default: 0)
        include_count: Include total count of results (default: False)
    
    Returns:
        JSON string containing list of assets with their metadata
    
    Example:
        # List first 20 assets
        list_catalog_assets(top=20)
        
        # List assets in SAP_CONTENT space
        list_catalog_assets(filter_expression="spaceId eq 'SAP_CONTENT'")
        
        # List only analytical models
        list_catalog_assets(filter_expression="assetType eq 'AnalyticalModel'")
    """
    try:
        # Build OData query parameters
        params = {
            "$top": top,
            "$skip": skip
        }
        
        if select_fields:
            params["$select"] = ",".join(select_fields)
        
        if filter_expression:
            params["$filter"] = filter_expression
        
        if include_count:
            params["$count"] = "true"
        
        # Make API request
        response = datasphere_client.get(
            "/api/v1/datasphere/consumption/catalog/assets",
            params=params
        )
        
        # Parse response
        assets = []
        for item in response.get("value", []):
            assets.append({
                "id": item.get("id"),
                "name": item.get("name"),
                "description": item.get("description"),
                "space_id": item.get("spaceId"),
                "space_name": item.get("spaceName"),
                "asset_type": item.get("assetType"),
                "exposed_for_consumption": item.get("exposedForConsumption", False),
                "analytical_consumption_url": item.get("analyticalConsumptionUrl"),
                "relational_consumption_url": item.get("relationalConsumptionUrl"),
                "created_at": item.get("createdAt"),
                "modified_at": item.get("modifiedAt")
            })
        
        result = {
            "assets": assets,
            "total_count": response.get("@odata.count"),
            "has_more": len(assets) == top,
            "returned_count": len(assets)
        }
        
        return json.dumps(result, indent=2)
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            return json.dumps({"error": "Authentication failed. Please check credentials."})
        elif e.response.status_code == 403:
            return json.dumps({"error": "Access denied. User lacks catalog read permission."})
        else:
            return json.dumps({"error": f"HTTP error: {e.response.status_code}"})
    except Exception as e:
        return json.dumps({"error": f"Failed to list catalog assets: {str(e)}"})
```

---

### Tool 2: `get_asset_details`

**Purpose**: Get detailed metadata for a specific asset

**API Endpoint**: `GET /api/v1/datasphere/consumption/catalog/spaces('{spaceId}')/assets('{assetId}')`

**Input Parameters**:
```python
class GetAssetDetailsInput(BaseModel):
    """Input for getting asset details"""
    space_id: str = Field(..., description="The space identifier (e.g., 'SAP_CONTENT')")
    asset_id: str = Field(..., description="The asset identifier")
    expand_fields: Optional[List[str]] = Field(
        None,
        description="Related entities to expand (e.g., ['columns', 'relationships'])"
    )
```

**Implementation Template**:
```python
@mcp.tool()
def get_asset_details(
    space_id: str,
    asset_id: str,
    expand_fields: Optional[List[str]] = None
) -> str:
    """
    Get detailed metadata for a specific asset in SAP Datasphere.
    
    This tool retrieves comprehensive information about a data asset including
    its structure, consumption URLs, business context, and technical details.
    
    Args:
        space_id: The space identifier (e.g., 'SAP_CONTENT')
        asset_id: The asset identifier (e.g., 'SAP_SC_FI_AM_FINTRANSACTIONS')
        expand_fields: Related entities to expand (e.g., ['columns', 'relationships'])
    
    Returns:
        JSON string containing detailed asset metadata
    
    Example:
        # Get details for a specific asset
        get_asset_details(
            space_id="SAP_CONTENT",
            asset_id="SAP_SC_FI_AM_FINTRANSACTIONS"
        )
    """
    try:
        # Build endpoint URL with OData key syntax
        endpoint = f"/api/v1/datasphere/consumption/catalog/spaces('{space_id}')/assets('{asset_id}')"
        
        # Build query parameters
        params = {}
        if expand_fields:
            params["$expand"] = ",".join(expand_fields)
        
        # Make API request
        response = datasphere_client.get(endpoint, params=params)
        
        # Format response for better readability
        asset_details = {
            "id": response.get("id"),
            "name": response.get("name"),
            "technical_name": response.get("technicalName"),
            "description": response.get("description"),
            "business_purpose": response.get("businessPurpose"),
            "space_id": response.get("spaceId"),
            "space_name": response.get("spaceName"),
            "asset_type": response.get("assetType"),
            "exposed_for_consumption": response.get("exposedForConsumption"),
            "consumption_urls": {
                "analytical": response.get("analyticalConsumptionUrl"),
                "relational": response.get("relationalConsumptionUrl")
            },
            "metadata_urls": {
                "analytical": response.get("analyticalMetadataUrl"),
                "relational": response.get("relationalMetadataUrl")
            },
            "ownership": {
                "owner": response.get("owner"),
                "created_by": response.get("createdBy"),
                "created_at": response.get("createdAt"),
                "modified_by": response.get("modifiedBy"),
                "modified_at": response.get("modifiedAt")
            },
            "status": response.get("status"),
            "version": response.get("version"),
            "tags": response.get("tags", []),
            "business_context": response.get("businessContext"),
            "technical_details": response.get("technicalDetails"),
            "dimensions": response.get("dimensions", []),
            "measures": response.get("measures", []),
            "relationships": response.get("relationships", [])
        }
        
        return json.dumps(asset_details, indent=2)
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return json.dumps({
                "error": f"Asset '{asset_id}' not found in space '{space_id}'"
            })
        elif e.response.status_code == 403:
            return json.dumps({
                "error": f"Access denied to asset '{asset_id}' in space '{space_id}'"
            })
        else:
            return json.dumps({"error": f"HTTP error: {e.response.status_code}"})
    except Exception as e:
        return json.dumps({"error": f"Failed to get asset details: {str(e)}"})
```

---

### Tool 3: `get_asset_by_compound_key`

**Purpose**: Retrieve asset using compound key identifier

**API Endpoint**: `GET /api/v1/datasphere/consumption/catalog/assets({assetCompoundId})`

**Input Parameters**:
```python
class GetAssetByCompoundKeyInput(BaseModel):
    """Input for getting asset by compound key"""
    space_id: str = Field(..., description="The space identifier")
    asset_id: str = Field(..., description="The asset identifier")
```

**Implementation Template**:
```python
@mcp.tool()
def get_asset_by_compound_key(
    space_id: str,
    asset_id: str
) -> str:
    """
    Retrieve asset using its compound key identifier.
    
    This is an alternative way to access asset details using OData compound key syntax.
    Useful when you have both space and asset IDs and want direct access.
    
    Args:
        space_id: The space identifier (e.g., 'SAP_CONTENT')
        asset_id: The asset identifier (e.g., 'SAP_SC_FI_AM_FINTRANSACTIONS')
    
    Returns:
        JSON string containing detailed asset metadata
    
    Example:
        get_asset_by_compound_key(
            space_id="SAP_CONTENT",
            asset_id="SAP_SC_FI_AM_FINTRANSACTIONS"
        )
    """
    try:
        # Build compound key in OData format
        compound_key = f"spaceId='{space_id}',assetId='{asset_id}'"
        endpoint = f"/api/v1/datasphere/consumption/catalog/assets({compound_key})"
        
        # Make API request
        response = datasphere_client.get(endpoint)
        
        # Format response (same as get_asset_details)
        asset_details = {
            "id": response.get("id"),
            "name": response.get("name"),
            "description": response.get("description"),
            "space_id": response.get("spaceId"),
            "asset_type": response.get("assetType"),
            "consumption_urls": {
                "analytical": response.get("analyticalConsumptionUrl"),
                "relational": response.get("relationalConsumptionUrl")
            },
            "metadata_urls": {
                "analytical": response.get("analyticalMetadataUrl"),
                "relational": response.get("relationalMetadataUrl")
            }
        }
        
        return json.dumps(asset_details, indent=2)
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            return json.dumps({"error": "Invalid compound key format"})
        elif e.response.status_code == 404:
            return json.dumps({"error": f"Asset not found with compound key"})
        else:
            return json.dumps({"error": f"HTTP error: {e.response.status_code}"})
    except Exception as e:
        return json.dumps({"error": f"Failed to get asset by compound key: {str(e)}"})
```

---

### Tool 4: `get_space_assets`

**Purpose**: List all assets within a specific space

**API Endpoint**: `GET /api/v1/datasphere/consumption/catalog/spaces('{spaceId}')/assets`

**Input Parameters**:
```python
class GetSpaceAssetsInput(BaseModel):
    """Input for getting space assets"""
    space_id: str = Field(..., description="The space identifier")
    filter_expression: Optional[str] = Field(
        None,
        description="OData filter expression (e.g., \"assetType eq 'AnalyticalModel'\")"
    )
    top: Optional[int] = Field(50, description="Maximum results", ge=1, le=1000)
    skip: Optional[int] = Field(0, description="Results to skip", ge=0)
```

**Implementation Template**:
```python
@mcp.tool()
def get_space_assets(
    space_id: str,
    filter_expression: Optional[str] = None,
    top: int = 50,
    skip: int = 0
) -> str:
    """
    List all assets within a specific space in SAP Datasphere.
    
    This tool retrieves all data assets (tables, views, analytical models)
    available in a specific space.
    
    Args:
        space_id: The space identifier (e.g., 'SAP_CONTENT')
        filter_expression: OData filter (e.g., "assetType eq 'AnalyticalModel'")
        top: Maximum number of results (default: 50, max: 1000)
        skip: Number of results to skip for pagination (default: 0)
    
    Returns:
        JSON string containing list of assets in the space
    
    Example:
        # List all assets in SAP_CONTENT space
        get_space_assets(space_id="SAP_CONTENT")
        
        # List only analytical models in the space
        get_space_assets(
            space_id="SAP_CONTENT",
            filter_expression="assetType eq 'AnalyticalModel'"
        )
    """
    try:
        # Build endpoint URL
        endpoint = f"/api/v1/datasphere/consumption/catalog/spaces('{space_id}')/assets"
        
        # Build query parameters
        params = {
            "$top": top,
            "$skip": skip
        }
        
        if filter_expression:
            params["$filter"] = filter_expression
        
        # Make API request
        response = datasphere_client.get(endpoint, params=params)
        
        # Parse response
        assets = []
        for item in response.get("value", []):
            assets.append({
                "id": item.get("id"),
                "name": item.get("name"),
                "description": item.get("description"),
                "asset_type": item.get("assetType"),
                "exposed_for_consumption": item.get("exposedForConsumption"),
                "analytical_consumption_url": item.get("analyticalConsumptionUrl"),
                "relational_consumption_url": item.get("relationalConsumptionUrl"),
                "created_at": item.get("createdAt"),
                "modified_at": item.get("modifiedAt")
            })
        
        result = {
            "space_id": space_id,
            "assets": assets,
            "returned_count": len(assets),
            "has_more": len(assets) == top
        }
        
        return json.dumps(result, indent=2)
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return json.dumps({"error": f"Space '{space_id}' not found"})
        elif e.response.status_code == 403:
            return json.dumps({"error": f"Access denied to space '{space_id}'"})
        else:
            return json.dumps({"error": f"HTTP error: {e.response.status_code}"})
    except Exception as e:
        return json.dumps({"error": f"Failed to get space assets: {str(e)}"})
```

---

## Complete Server Structure

```
src/sap-datasphere-mcp-server/
├── pyproject.toml
├── README.md
├── awslabs/
│   └── sap_datasphere_mcp_server/
│       ├── __init__.py
│       ├── server.py          # Main MCP server with tools
│       ├── client.py          # DatasphereClient class
│       ├── models.py          # Pydantic models
│       └── consts.py          # Constants and defaults
└── tests/
    ├── test_server.py
    └── test_client.py
```

---

## Running the Server

### Configuration
Set environment variables:
```bash
export DATASPHERE_BASE_URL="https://your-tenant.eu10.hcs.cloud.sap"
export DATASPHERE_CLIENT_ID="your-client-id"
export DATASPHERE_CLIENT_SECRET="your-client-secret"
export DATASPHERE_TOKEN_URL="https://your-tenant.authentication.eu10.hana.ondemand.com/oauth/token"
```

### Start Server
```bash
# Using uvx (recommended)
uvx awslabs.sap-datasphere-mcp-server

# Or using uv run
uv run --directory src/sap-datasphere-mcp-server server.py
```

### Test with MCP Inspector
```bash
npx @modelcontextprotocol/inspector uvx awslabs.sap-datasphere-mcp-server
```

---

## Testing Examples

### Test list_catalog_assets
```python
# List first 10 assets
result = list_catalog_assets(top=10)

# List assets in specific space
result = list_catalog_assets(
    filter_expression="spaceId eq 'SAP_CONTENT'",
    top=20
)

# List only analytical models
result = list_catalog_assets(
    filter_expression="assetType eq 'AnalyticalModel'",
    include_count=True
)
```

### Test get_asset_details
```python
# Get details for specific asset
result = get_asset_details(
    space_id="SAP_CONTENT",
    asset_id="SAP_SC_FI_AM_FINTRANSACTIONS"
)
```

### Test get_space_assets
```python
# List all assets in space
result = get_space_assets(space_id="SAP_CONTENT")

# Filter by asset type
result = get_space_assets(
    space_id="SAP_CONTENT",
    filter_expression="assetType eq 'View'"
)
```

---

## Success Criteria

✅ All four tools implemented and working  
✅ OAuth2 authentication functioning correctly  
✅ Token refresh mechanism working  
✅ Error handling for all edge cases  
✅ Pagination support implemented  
✅ OData query parameters working  
✅ Response formatting consistent  
✅ Documentation complete  
✅ Unit tests passing  
✅ Integration tests with real tenant passing  

---

## Next Steps After Implementation

1. Test with real SAP Datasphere tenant
2. Add comprehensive error handling
3. Implement response caching
4. Add logging and monitoring
5. Create usage documentation
6. Proceed to Phase 3: Metadata & Schema Discovery tools
