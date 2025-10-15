"""
SAP Datasphere API client
"""

from typing import Any, Dict, List, Optional
import httpx
from loguru import logger

from .models import DatasphereConfig, Space, Table, Connection, CatalogItem, APIResponse
from .auth import DatasphereAuth


class DatasphereClient:
    """SAP Datasphere API client"""
    
    def __init__(self, config: DatasphereConfig):
        self.config = config
        self.auth = DatasphereAuth(config)
        self._client = httpx.AsyncClient(timeout=config.api_timeout)
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        **kwargs
    ) -> httpx.Response:
        """Make an authenticated API request"""
        
        access_token = await self.auth.get_access_token()
        
        headers = kwargs.get('headers', {})
        headers.update({
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
            'User-Agent': 'SAP-Datasphere-MCP-Client/0.1.0'
        })
        kwargs['headers'] = headers
        
        url = f"{self.config.tenant_url.rstrip('/')}{endpoint}"
        
        logger.debug(f"Making {method} request to {url}")
        
        response = await self._client.request(method, url, **kwargs)
        
        logger.debug(f"Response: {response.status_code}")
        
        return response
    
    async def test_connection(self) -> APIResponse:
        """Test the connection to SAP Datasphere"""
        
        try:
            success = await self.auth.test_connection()
            
            if success:
                return APIResponse(
                    success=True,
                    data={"status": "connected", "tenant_url": self.config.tenant_url},
                    metadata={"test_type": "oauth_authentication"}
                )
            else:
                return APIResponse(
                    success=False,
                    error="OAuth authentication failed"
                )
                
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return APIResponse(
                success=False,
                error=str(e)
            )
    
    async def discover_api_endpoints(self) -> APIResponse:
        """Discover available API endpoints"""
        
        # List of potential API endpoints to test
        endpoints_to_test = [
            "/dwaas-core/api/v1/spaces",
            "/api/v1/spaces",
            "/dwc/api/v1/spaces",
            "/dwaas-core/api/v1/catalog",
            "/api/v1/catalog",
            "/dwc/api/v1/catalog",
            "/odata/v4/spaces",
            "/odata/v4/catalog"
        ]
        
        working_endpoints = []
        
        for endpoint in endpoints_to_test:
            try:
                response = await self._make_request('GET', endpoint)
                
                if response.status_code < 400:
                    working_endpoints.append({
                        'endpoint': endpoint,
                        'status_code': response.status_code,
                        'content_type': response.headers.get('content-type', 'unknown')
                    })
                    logger.info(f"Working endpoint found: {endpoint}")
                
            except Exception as e:
                logger.debug(f"Endpoint {endpoint} failed: {e}")
        
        return APIResponse(
            success=True,
            data={"working_endpoints": working_endpoints},
            metadata={"total_tested": len(endpoints_to_test), "working_count": len(working_endpoints)}
        )
    
    async def list_spaces(self) -> APIResponse:
        """List all available spaces"""
        
        # Try different possible endpoints for spaces
        space_endpoints = [
            "/dwaas-core/api/v1/spaces",
            "/api/v1/spaces",
            "/dwc/api/v1/spaces"
        ]
        
        for endpoint in space_endpoints:
            try:
                response = await self._make_request('GET', endpoint)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Parse spaces based on response structure
                    spaces = []
                    if isinstance(data, list):
                        for item in data:
                            spaces.append(Space(**item))
                    elif isinstance(data, dict) and 'spaces' in data:
                        for item in data['spaces']:
                            spaces.append(Space(**item))
                    elif isinstance(data, dict) and 'value' in data:  # OData format
                        for item in data['value']:
                            spaces.append(Space(**item))
                    
                    return APIResponse(
                        success=True,
                        data=[space.dict() for space in spaces],
                        metadata={"endpoint_used": endpoint, "count": len(spaces)}
                    )
                
            except Exception as e:
                logger.debug(f"Spaces endpoint {endpoint} failed: {e}")
        
        return APIResponse(
            success=False,
            error="No working spaces endpoint found"
        )
    
    async def get_space_info(self, space_id: str) -> APIResponse:
        """Get detailed information about a specific space"""
        
        space_endpoints = [
            f"/dwaas-core/api/v1/spaces/{space_id}",
            f"/api/v1/spaces/{space_id}",
            f"/dwc/api/v1/spaces/{space_id}"
        ]
        
        for endpoint in space_endpoints:
            try:
                response = await self._make_request('GET', endpoint)
                
                if response.status_code == 200:
                    data = response.json()
                    space = Space(**data)
                    
                    return APIResponse(
                        success=True,
                        data=space.dict(),
                        metadata={"endpoint_used": endpoint}
                    )
                
            except Exception as e:
                logger.debug(f"Space info endpoint {endpoint} failed: {e}")
        
        return APIResponse(
            success=False,
            error=f"Could not retrieve information for space: {space_id}"
        )
    
    async def list_catalog(self, space_id: Optional[str] = None) -> APIResponse:
        """List catalog items (tables, views, etc.)"""
        
        if space_id:
            catalog_endpoints = [
                f"/dwaas-core/api/v1/spaces/{space_id}/catalog",
                f"/api/v1/spaces/{space_id}/catalog",
                f"/dwc/api/v1/spaces/{space_id}/catalog"
            ]
        else:
            catalog_endpoints = [
                "/dwaas-core/api/v1/catalog",
                "/api/v1/catalog",
                "/dwc/api/v1/catalog",
                "/odata/v4/catalog"
            ]
        
        for endpoint in catalog_endpoints:
            try:
                response = await self._make_request('GET', endpoint)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Parse catalog items
                    items = []
                    if isinstance(data, list):
                        for item in data:
                            items.append(CatalogItem(**item))
                    elif isinstance(data, dict) and 'items' in data:
                        for item in data['items']:
                            items.append(CatalogItem(**item))
                    elif isinstance(data, dict) and 'value' in data:  # OData format
                        for item in data['value']:
                            items.append(CatalogItem(**item))
                    
                    return APIResponse(
                        success=True,
                        data=[item.dict() for item in items],
                        metadata={"endpoint_used": endpoint, "count": len(items), "space_id": space_id}
                    )
                
            except Exception as e:
                logger.debug(f"Catalog endpoint {endpoint} failed: {e}")
        
        return APIResponse(
            success=False,
            error=f"No working catalog endpoint found for space: {space_id}"
        )
    
    async def get_table_info(self, space_id: str, table_name: str) -> APIResponse:
        """Get detailed information about a table"""
        
        table_endpoints = [
            f"/dwaas-core/api/v1/spaces/{space_id}/tables/{table_name}",
            f"/api/v1/spaces/{space_id}/tables/{table_name}",
            f"/dwc/api/v1/spaces/{space_id}/tables/{table_name}"
        ]
        
        for endpoint in table_endpoints:
            try:
                response = await self._make_request('GET', endpoint)
                
                if response.status_code == 200:
                    data = response.json()
                    table = Table(**data)
                    
                    return APIResponse(
                        success=True,
                        data=table.dict(),
                        metadata={"endpoint_used": endpoint}
                    )
                
            except Exception as e:
                logger.debug(f"Table info endpoint {endpoint} failed: {e}")
        
        return APIResponse(
            success=False,
            error=f"Could not retrieve information for table: {table_name} in space: {space_id}"
        )
    
    async def list_connections(self, space_id: Optional[str] = None) -> APIResponse:
        """List data source connections"""
        
        if space_id:
            connection_endpoints = [
                f"/dwaas-core/api/v1/spaces/{space_id}/connections",
                f"/api/v1/spaces/{space_id}/connections",
                f"/dwc/api/v1/spaces/{space_id}/connections"
            ]
        else:
            connection_endpoints = [
                "/dwaas-core/api/v1/connections",
                "/api/v1/connections",
                "/dwc/api/v1/connections"
            ]
        
        for endpoint in connection_endpoints:
            try:
                response = await self._make_request('GET', endpoint)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Parse connections
                    connections = []
                    if isinstance(data, list):
                        for item in data:
                            connections.append(Connection(**item))
                    elif isinstance(data, dict) and 'connections' in data:
                        for item in data['connections']:
                            connections.append(Connection(**item))
                    elif isinstance(data, dict) and 'value' in data:  # OData format
                        for item in data['value']:
                            connections.append(Connection(**item))
                    
                    return APIResponse(
                        success=True,
                        data=[conn.dict() for conn in connections],
                        metadata={"endpoint_used": endpoint, "count": len(connections), "space_id": space_id}
                    )
                
            except Exception as e:
                logger.debug(f"Connections endpoint {endpoint} failed: {e}")
        
        return APIResponse(
            success=False,
            error=f"No working connections endpoint found for space: {space_id}"
        )
    
    async def close(self) -> None:
        """Close the client connections"""
        await self.auth.close()
        await self._client.aclose()