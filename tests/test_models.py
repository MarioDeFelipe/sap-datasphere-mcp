"""
Tests for data models
"""

import pytest
from sap_datasphere_mcp.models import (
    DatasphereConfig,
    OAuthToken,
    Space,
    Table,
    Connection,
    APIResponse,
    CatalogItem
)


def test_datasphere_config():
    """Test DatasphereConfig model"""
    config = DatasphereConfig(
        tenant_url="https://test.eu10.hcs.cloud.sap",
        tenant_id="test-tenant",
        oauth_client_id="test-client-id",
        oauth_client_secret="test-client-secret",
        oauth_token_url="https://test.authentication.eu20.hana.ondemand.com/oauth/token"
    )
    
    assert config.tenant_url == "https://test.eu10.hcs.cloud.sap"
    assert config.tenant_id == "test-tenant"
    assert config.api_timeout == 30  # default value


def test_oauth_token():
    """Test OAuthToken model"""
    token = OAuthToken(
        access_token="test-token",
        expires_in=3600
    )
    
    assert token.access_token == "test-token"
    assert token.token_type == "Bearer"  # default value
    assert token.expires_in == 3600


def test_space():
    """Test Space model"""
    space = Space(
        id="test-space",
        name="Test Space",
        description="A test space"
    )
    
    assert space.id == "test-space"
    assert space.name == "Test Space"
    assert space.description == "A test space"


def test_table():
    """Test Table model"""
    table = Table(
        id="test-table",
        name="Test Table",
        type="table",
        space_id="test-space"
    )
    
    assert table.id == "test-table"
    assert table.name == "Test Table"
    assert table.type == "table"
    assert table.space_id == "test-space"


def test_connection():
    """Test Connection model"""
    connection = Connection(
        id="test-conn",
        name="Test Connection",
        type="HANA"
    )
    
    assert connection.id == "test-conn"
    assert connection.name == "Test Connection"
    assert connection.type == "HANA"


def test_api_response():
    """Test APIResponse model"""
    response = APIResponse(
        success=True,
        data={"test": "data"},
        metadata={"count": 1}
    )
    
    assert response.success is True
    assert response.data == {"test": "data"}
    assert response.metadata == {"count": 1}
    assert response.error is None


def test_catalog_item():
    """Test CatalogItem model"""
    item = CatalogItem(
        id="test-item",
        name="Test Item",
        type="table",
        space_id="test-space"
    )
    
    assert item.id == "test-item"
    assert item.name == "Test Item"
    assert item.type == "table"
    assert item.space_id == "test-space"