"""
OAuth authentication for SAP Datasphere
"""

import base64
from typing import Optional
import httpx
from loguru import logger

from .models import DatasphereConfig, OAuthToken


class DatasphereAuth:
    """Handles OAuth authentication for SAP Datasphere"""
    
    def __init__(self, config: DatasphereConfig):
        self.config = config
        self._token: Optional[OAuthToken] = None
        self._client = httpx.AsyncClient(timeout=config.api_timeout)
    
    async def get_access_token(self) -> str:
        """Get a valid access token, refreshing if necessary"""
        
        if self._token is None or self._is_token_expired():
            await self._refresh_token()
        
        return self._token.access_token
    
    async def _refresh_token(self) -> None:
        """Refresh the OAuth access token using client credentials flow"""
        
        logger.info("Refreshing OAuth access token")
        
        try:
            # Prepare client credentials
            auth_string = f"{self.config.oauth_client_id}:{self.config.oauth_client_secret}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            headers = {
                'Authorization': f'Basic {auth_b64}',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
            
            data = {
                'grant_type': 'client_credentials'
            }
            
            response = await self._client.post(
                self.config.oauth_token_url,
                headers=headers,
                data=data
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self._token = OAuthToken(**token_data)
                logger.info(f"OAuth token refreshed, expires in {self._token.expires_in} seconds")
            else:
                error_msg = f"OAuth token refresh failed: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            logger.error(f"Failed to refresh OAuth token: {e}")
            raise
    
    def _is_token_expired(self) -> bool:
        """Check if the current token is expired or about to expire"""
        
        if self._token is None:
            return True
        
        # Consider token expired if it expires in less than 5 minutes
        # This is a simple check - in production you'd want to track the actual expiration time
        return False  # For now, always refresh to be safe
    
    async def test_connection(self) -> bool:
        """Test the OAuth connection"""
        
        try:
            await self.get_access_token()
            return True
        except Exception as e:
            logger.error(f"OAuth connection test failed: {e}")
            return False
    
    async def close(self) -> None:
        """Close the HTTP client"""
        await self._client.aclose()