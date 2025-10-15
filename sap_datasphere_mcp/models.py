"""
Data models for SAP Datasphere MCP Server
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DatasphereConfig(BaseModel):
    """Configuration for SAP Datasphere connection"""
    
    tenant_url: str = Field(..., description="SAP Datasphere tenant URL")
    tenant_id: str = Field(..., description="SAP Datasphere tenant ID")
    oauth_client_id: str = Field(..., description="OAuth client ID")
    oauth_client_secret: str = Field(..., description="OAuth client secret")
    oauth_token_url: str = Field(..., description="OAuth token endpoint URL")
    oauth_authorization_url: Optional[str] = Field(None, description="OAuth authorization URL")
    api_timeout: int = Field(30, description="API request timeout in seconds")
    api_retry_count: int = Field(3, description="Number of API retry attempts")


class OAuthToken(BaseModel):
    """OAuth token response"""
    
    access_token: str = Field(..., description="Access token")
    token_type: str = Field("Bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    scope: Optional[str] = Field(None, description="Token scope")


class Space(BaseModel):
    """SAP Datasphere Space"""
    
    id: str = Field(..., description="Space ID")
    name: str = Field(..., description="Space name")
    description: Optional[str] = Field(None, description="Space description")
    type: Optional[str] = Field(None, description="Space type")
    status: Optional[str] = Field(None, description="Space status")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    owner: Optional[str] = Field(None, description="Space owner")


class Table(BaseModel):
    """SAP Datasphere Table/View"""
    
    id: str = Field(..., description="Table ID")
    name: str = Field(..., description="Table name")
    type: str = Field(..., description="Table type (table, view, etc.)")
    space_id: str = Field(..., description="Parent space ID")
    description: Optional[str] = Field(None, description="Table description")
    schema_name: Optional[str] = Field(None, description="Schema name")
    columns: Optional[List[Dict[str, Any]]] = Field(None, description="Table columns")
    row_count: Optional[int] = Field(None, description="Number of rows")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")


class Connection(BaseModel):
    """SAP Datasphere Connection"""
    
    id: str = Field(..., description="Connection ID")
    name: str = Field(..., description="Connection name")
    type: str = Field(..., description="Connection type")
    space_id: Optional[str] = Field(None, description="Parent space ID")
    description: Optional[str] = Field(None, description="Connection description")
    status: Optional[str] = Field(None, description="Connection status")
    host: Optional[str] = Field(None, description="Connection host")
    port: Optional[int] = Field(None, description="Connection port")
    database: Optional[str] = Field(None, description="Database name")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")


class APIResponse(BaseModel):
    """Generic API response wrapper"""
    
    success: bool = Field(..., description="Whether the request was successful")
    data: Optional[Any] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if failed")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class CatalogItem(BaseModel):
    """Catalog item (table, view, etc.)"""
    
    id: str = Field(..., description="Item ID")
    name: str = Field(..., description="Item name")
    type: str = Field(..., description="Item type")
    space_id: str = Field(..., description="Parent space ID")
    path: Optional[str] = Field(None, description="Item path")
    description: Optional[str] = Field(None, description="Item description")
    tags: Optional[List[str]] = Field(None, description="Item tags")
    properties: Optional[Dict[str, Any]] = Field(None, description="Additional properties")