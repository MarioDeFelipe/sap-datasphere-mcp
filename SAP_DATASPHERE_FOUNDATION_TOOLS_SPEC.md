# SAP Datasphere MCP Server - Phase 1.1 & 1.2 Foundation Tools

## Overview

This document provides complete technical specifications for implementing **7 foundation tools** that establish basic connectivity, authentication, and space discovery capabilities.

**Phases**: 1.1 Authentication & Connection + 1.2 Basic Space Discovery  
**Priority**: CRITICAL + HIGH  
**Estimated Implementation Time**: 4-6 days  
**Tools Count**: 7

---

## Phase 1.1: Authentication & Connection Tools (4 tools)

### Tool 1: `test_connection`

**Purpose**: Verify SAP Datasphere connectivity and OAuth authentication status

**API Endpoint**: `GET /api/v1/tenant` or `GET /api/v1/datasphere/spaces`

**Parameters**:
- None (uses configured OAuth2 credentials)

**Response**:
```json
{
  "status": "connected",
  "tenant_url": "https://tenant.datasphere.cloud.sap",
  "authenticated_user": "technical_user@company.com",
  "token_valid": true,
  "token_expires_at": "2024-12-09T15:30:00Z",
  "available_scopes": ["DWC_CONSUMPTION", "DWC_CATALOG"],
  "connection_test_timestamp": "2024-12-09T14:30:00Z"
}
```

### Tool 2: `get_current_user`

**Purpose**: Get authenticated user information and permissions

**API Endpoint**: `GET /api/v1/datasphere/users/me` or `GET /api/v1/tenant/user`

**Response**:
```json
{
  "user_id": "TECH_USER_001",
  "email": "technical_user@company.com",
  "display_name": "Technical User",
  "roles": ["DWC_CONSUMER", "CATALOG_READER"],
  "permissions": ["READ_SPACES", "READ_ASSETS", "QUERY_DATA"],
  "tenant_id": "tenant-12345",
  "last_login": "2024-12-09T14:00:00Z",
  "account_status": "Active"
}
```

### Tool 3: `get_tenant_info`

**Purpose**: Retrieve tenant configuration and system information

**API Endpoint**: `GET /api/v1/tenant`

**Response**:
```json
{
  "tenant_id": "tenant-12345",
  "tenant_name": "Company Production",
  "region": "us-east-1",
  "datasphere_version": "2024.20",
  "license_type": "Enterprise",
  "storage_quota_gb": 10000,
  "storage_used_gb": 3500,
  "user_count": 150,
  "space_count": 25,
  "features_enabled": ["AI_FEATURES", "DATA_SHARING", "MARKETPLACE"],
  "maintenance_window": "Sunday 02:00-04:00 UTC"
}
```

### Tool 4: `get_available_scopes`

**Purpose**: List available OAuth2 scopes for the current user

**API Endpoint**: `GET /oauth/scopes` or derived from token introspection

**Response**:
```json
{
  "available_scopes": [
    {
      "scope": "DWC_CONSUMPTION",
      "description": "Read access to consumption models",
      "granted": true
    },
    {
      "scope": "DWC_CATALOG",
      "description": "Read access to catalog metadata",
      "granted": true
    },
    {
      "scope": "DWC_REPOSITORY",
      "description": "Read access to repository objects",
      "granted": false
    }
  ],
  "token_scopes": ["DWC_CONSUMPTION", "DWC_CATALOG"],
  "scope_check_timestamp": "2024-12-09T14:30:00Z"
}
```

---

## Phase 1.2: Basic Space Discovery Tools (3 tools)

### Tool 5: `list_spaces`

**Purpose**: List all accessible SAP Datasphere spaces

**API Endpoint**: `GET /api/v1/datasphere/consumption/catalog/spaces`

**Parameters**:
- `include_details` (boolean): Include detailed space information
- `top` (integer): Maximum results (default: 50)
- `skip` (integer): Pagination offset

**Response**:
```json
{
  "spaces": [
    {
      "spaceId": "SAP_CONTENT",
      "spaceName": "SAP Content",
      "description": "Pre-built SAP content and models",
      "status": "ACTIVE",
      "owner": "SAP",
      "created_date": "2024-01-01T00:00:00Z",
      "asset_count": 45,
      "table_count": 12,
      "view_count": 18,
      "model_count": 15,
      "permissions": ["READ", "CONSUME"]
    },
    {
      "spaceId": "FINANCE_DWH",
      "spaceName": "Finance Data Warehouse",
      "description": "Financial reporting and analytics",
      "status": "ACTIVE",
      "owner": "finance_team@company.com",
      "created_date": "2024-03-15T10:00:00Z",
      "asset_count": 28,
      "permissions": ["READ", "CONSUME", "WRITE"]
    }
  ],
  "total_count": 25,
  "accessible_count": 2
}
```

### Tool 6: `get_space_info`

**Purpose**: Get comprehensive information about a specific space

**API Endpoint**: `GET /api/v1/datasphere/consumption/catalog/spaces('{spaceId}')`

**Parameters**:
- `space_id` (required): Space identifier (e.g., "SAP_CONTENT")

**Response**:
```json
{
  "spaceId": "SAP_CONTENT",
  "spaceName": "SAP Content",
  "description": "Pre-built SAP content and analytical models",
  "status": "ACTIVE",
  "owner": "SAP",
  "created_date": "2024-01-01T00:00:00Z",
  "modified_date": "2024-11-20T14:00:00Z",
  "size_mb": 2500,
  "asset_summary": {
    "total_assets": 45,
    "analytical_models": 15,
    "tables": 12,
    "views": 18,
    "exposed_for_consumption": 42
  },
  "permissions": {
    "current_user": ["READ", "CONSUME"],
    "space_roles": ["VIEWER", "CONSUMER"]
  },
  "connections": [
    {
      "connection_id": "SAP_ERP_PROD",
      "connection_type": "SAP_ERP",
      "status": "CONNECTED"
    }
  ],
  "metadata_url": "/api/v1/datasphere/consumption/catalog/spaces('SAP_CONTENT')/$metadata"
}
```

### Tool 7: `search_tables`

**Purpose**: Search for tables and views across spaces by name or description

**API Endpoint**: `GET /api/v1/datasphere/consumption/catalog/assets` with filters

**Parameters**:
- `search_term` (required): Keyword to search for
- `space_id` (optional): Filter to specific space
- `asset_types` (optional): Filter by asset types ["Table", "View"]
- `top` (integer): Maximum results (default: 50)

**Response**:
```json
{
  "search_term": "customer",
  "results": [
    {
      "assetId": "CUSTOMER_DATA",
      "assetName": "Customer Master Data",
      "spaceId": "FINANCE_DWH",
      "spaceName": "Finance Data Warehouse",
      "assetType": "Table",
      "description": "Core customer information and attributes",
      "row_count": 125000,
      "columns": [
        {"name": "CUSTOMER_ID", "type": "NVARCHAR(10)"},
        {"name": "CUSTOMER_NAME", "type": "NVARCHAR(100)"},
        {"name": "COUNTRY", "type": "NVARCHAR(3)"}
      ],
      "consumption_urls": {
        "analytical": "/api/v1/datasphere/consumption/analytical/FINANCE_DWH/CUSTOMER_DATA",
        "relational": "/api/v1/datasphere/consumption/relational/FINANCE_DWH/CUSTOMER_DATA"
      }
    }
  ],
  "total_matches": 8,
  "search_timestamp": "2024-12-09T14:30:00Z"
}
```

---

## Authentication Implementation

### OAuth2 Token Management
```python
class DatasphereAuth:
    def __init__(self, client_id: str, client_secret: str, token_url: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.access_token = None
        self.token_expiry = None
    
    async def get_token(self) -> str:
        if self.access_token and self.token_expiry > datetime.now():
            return self.access_token
        return await self.refresh_token()
    
    async def refresh_token(self) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    'grant_type': 'client_credentials',
                    'client_id': self.client_id,
                    'client_secret': self.client_secret
                }
            )
            response.raise_for_status()
            token_data = response.json()
            
            self.access_token = token_data['access_token']
            expires_in = token_data.get('expires_in', 3600)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in - 60)
            
            return self.access_token
```

---

## Error Handling

### Standard Error Responses
```json
{
  "error": "authentication_failed",
  "message": "OAuth2 token is invalid or expired",
  "code": 401,
  "timestamp": "2024-12-09T14:30:00Z",
  "suggestion": "Check OAuth2 credentials and token endpoint"
}
```

### Error Categories
- **401 Unauthorized**: Invalid/expired token → Refresh and retry
- **403 Forbidden**: Insufficient permissions → Return clear message
- **404 Not Found**: Space/resource not found → Validate existence
- **429 Rate Limited**: Too many requests → Implement backoff
- **500 Server Error**: SAP system error → Retry with exponential backoff

---

## Configuration

### Environment Variables
```bash
DATASPHERE_BASE_URL=https://tenant.datasphere.cloud.sap
DATASPHERE_CLIENT_ID=your_client_id
DATASPHERE_CLIENT_SECRET=your_client_secret
DATASPHERE_TOKEN_URL=https://tenant.authentication.sap.hana.ondemand.com/oauth/token
```

### Configuration Model
```python
from pydantic import BaseModel

class DatasphereConfig(BaseModel):
    base_url: str
    client_id: str
    client_secret: str
    token_url: str
    default_timeout: int = 30
    max_retries: int = 3
```

---

## Success Criteria

### Phase 1.1 (Authentication & Connection)
- ✅ Can verify connectivity to SAP Datasphere
- ✅ OAuth2 authentication working with token refresh
- ✅ Can retrieve current user information
- ✅ Can get tenant configuration details
- ✅ Can list available OAuth scopes

### Phase 1.2 (Basic Space Discovery)
- ✅ Can list all accessible spaces
- ✅ Can get detailed space information
- ✅ Can search for tables across spaces
- ✅ Proper permission handling
- ✅ Pagination works for large result sets

---

## Next Steps

After implementing Phase 1.1 & 1.2:
1. Test with real SAP Datasphere tenant
2. Validate OAuth2 flow end-to-end
3. Test with different user permission levels
4. Create usage documentation
5. Proceed to Phase 5.1: Relational Data Access

---

**Document Version**: 1.0  
**Last Updated**: December 9, 2025  
**Related Documents**:
- SAP_DATASPHERE_MCP_EXTRACTION_PLAN.md
- EXTRACTION_PLAN_STATUS.md