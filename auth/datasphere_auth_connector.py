#!/usr/bin/env python3
"""
SAP Datasphere Authenticated Connector
Integrates OAuth 2.0 authentication with Datasphere API calls
"""

import logging
from typing import Dict, List, Optional, Any
import aiohttp
from dataclasses import dataclass

from auth.oauth_handler import OAuthHandler, OAuthError

logger = logging.getLogger(__name__)


@dataclass
class DatasphereConfig:
    """Configuration for SAP Datasphere connection"""
    base_url: str
    client_id: str
    client_secret: str
    token_url: str
    tenant_id: str
    scope: Optional[str] = None


class DatasphereAuthConnector:
    """
    Authenticated connector for SAP Datasphere API

    Provides OAuth-authenticated access to SAP Datasphere resources:
    - Spaces
    - Tables and Views
    - Connections
    - Tasks
    - Metadata
    """

    def __init__(self, config: DatasphereConfig, oauth_handler: Optional[OAuthHandler] = None):
        """
        Initialize Datasphere connector

        Args:
            config: Datasphere configuration
            oauth_handler: Optional pre-configured OAuth handler
        """
        self.config = config
        self.oauth_handler = oauth_handler
        self._session: Optional[aiohttp.ClientSession] = None

        logger.info(f"Datasphere connector initialized for {config.base_url}")

    async def initialize(self):
        """Initialize the connector and acquire OAuth token"""
        if not self.oauth_handler:
            from auth.oauth_handler import create_oauth_handler

            self.oauth_handler = await create_oauth_handler(
                client_id=self.config.client_id,
                client_secret=self.config.client_secret,
                token_url=self.config.token_url,
                scope=self.config.scope,
                acquire_token=True
            )

        logger.info("Datasphere connector initialized with OAuth authentication")

    async def _get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers with valid OAuth token

        Returns:
            Headers dictionary with Authorization

        Raises:
            OAuthError: If token cannot be acquired
        """
        if not self.oauth_handler:
            raise OAuthError("OAuth handler not initialized")

        token = await self.oauth_handler.get_token()

        return {
            'Authorization': f'{token.token_type} {token.access_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'Datasphere-Metadata-Sync/2.0'  # Required for API access
        }

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make authenticated API request to Datasphere

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (relative to base_url)
            params: Optional query parameters
            data: Optional request body

        Returns:
            Response data as dictionary

        Raises:
            aiohttp.ClientError: On network errors
            OAuthError: On authentication errors
        """
        headers = await self._get_headers()
        url = f"{self.config.base_url}/{endpoint.lstrip('/')}"

        if not self._session:
            self._session = aiohttp.ClientSession()

        try:
            async with self._session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 401:
                    # Token might be expired, try refreshing
                    logger.warning("Received 401, refreshing token...")
                    await self.oauth_handler.get_token(force_refresh=True)

                    # Retry with new token
                    headers = await self._get_headers()
                    async with self._session.request(
                        method=method,
                        url=url,
                        headers=headers,
                        params=params,
                        json=data,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as retry_response:
                        retry_response.raise_for_status()
                        return await retry_response.json()

                response.raise_for_status()
                return await response.json()

        except aiohttp.ClientError as e:
            logger.error(f"API request failed: {method} {url} - {str(e)}")
            raise

    async def get_spaces(self) -> List[Dict[str, Any]]:
        """
        Get all Datasphere spaces

        Returns:
            List of space dictionaries
        """
        logger.info("Fetching Datasphere spaces")
        response = await self._make_request('GET', '/api/v1/spaces')
        return response.get('spaces', [])

    async def get_space_details(self, space_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific space

        Args:
            space_id: Space identifier

        Returns:
            Space details dictionary
        """
        logger.info(f"Fetching details for space: {space_id}")
        return await self._make_request('GET', f'/api/v1/spaces/{space_id}')

    async def get_tables(self, space_id: str) -> List[Dict[str, Any]]:
        """
        Get all tables in a space

        Args:
            space_id: Space identifier

        Returns:
            List of table dictionaries
        """
        logger.info(f"Fetching tables for space: {space_id}")
        response = await self._make_request(
            'GET',
            f'/api/v1/spaces/{space_id}/tables'
        )
        return response.get('tables', [])

    async def get_table_schema(self, space_id: str, table_name: str) -> Dict[str, Any]:
        """
        Get schema information for a specific table

        Args:
            space_id: Space identifier
            table_name: Table name

        Returns:
            Table schema dictionary
        """
        logger.info(f"Fetching schema for table: {space_id}/{table_name}")
        return await self._make_request(
            'GET',
            f'/api/v1/spaces/{space_id}/tables/{table_name}/schema'
        )

    async def execute_query(
        self,
        space_id: str,
        query: str,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Execute a query against Datasphere data

        Args:
            space_id: Space identifier
            query: SQL query to execute
            limit: Maximum rows to return

        Returns:
            Query results dictionary
        """
        logger.info(f"Executing query in space: {space_id}")
        return await self._make_request(
            'POST',
            f'/api/v1/spaces/{space_id}/query',
            data={
                'query': query,
                'limit': limit
            }
        )

    async def get_connections(self) -> List[Dict[str, Any]]:
        """
        Get all data connections

        Returns:
            List of connection dictionaries
        """
        logger.info("Fetching data connections")
        response = await self._make_request('GET', '/api/v1/connections')
        return response.get('connections', [])

    async def get_tasks(self, space_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get integration tasks

        Args:
            space_id: Optional space filter

        Returns:
            List of task dictionaries
        """
        logger.info(f"Fetching tasks{f' for space {space_id}' if space_id else ''}")
        params = {'space_id': space_id} if space_id else None
        response = await self._make_request('GET', '/api/v1/tasks', params=params)
        return response.get('tasks', [])

    async def test_connection(self) -> Dict[str, Any]:
        """
        Test the connection to Datasphere

        Returns:
            Connection status dictionary
        """
        try:
            await self._make_request('GET', '/api/v1/health')
            return {
                'connected': True,
                'oauth_status': self.oauth_handler.get_health_status() if self.oauth_handler else None,
                'message': 'Connection successful'
            }
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return {
                'connected': False,
                'error': str(e),
                'message': 'Connection failed'
            }

    async def close(self):
        """Close the connector and cleanup resources"""
        if self._session:
            await self._session.close()
            self._session = None

        if self.oauth_handler:
            await self.oauth_handler.revoke_token()

        logger.info("Datasphere connector closed")

    async def __aenter__(self):
        """Context manager entry"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.close()
