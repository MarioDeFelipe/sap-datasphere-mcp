#!/usr/bin/env python3
"""
OAuth 2.0 Handler for SAP Datasphere
Implements client credentials flow with automatic token refresh
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import aiohttp
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class OAuthError(Exception):
    """Base exception for OAuth-related errors"""
    pass


class TokenAcquisitionError(OAuthError):
    """Raised when token acquisition fails"""
    pass


class TokenRefreshError(OAuthError):
    """Raised when token refresh fails"""
    pass


@dataclass
class OAuthToken:
    """
    Represents an OAuth 2.0 access token with metadata
    """
    access_token: str
    token_type: str
    expires_in: int
    scope: Optional[str] = None
    refresh_token: Optional[str] = None

    # Internal tracking
    acquired_at: float = None

    def __post_init__(self):
        """Initialize acquisition timestamp"""
        if self.acquired_at is None:
            self.acquired_at = time.time()

    @property
    def expires_at(self) -> float:
        """Calculate absolute expiration timestamp"""
        return self.acquired_at + self.expires_in

    @property
    def is_expired(self) -> bool:
        """Check if token has expired"""
        # Consider token expired 60 seconds before actual expiration
        buffer = 60
        return time.time() >= (self.expires_at - buffer)

    @property
    def time_until_expiry(self) -> float:
        """Get seconds until token expiration"""
        return self.expires_at - time.time()

    def __repr__(self) -> str:
        """Safe representation without exposing token"""
        return (f"OAuthToken(type={self.token_type}, "
                f"expires_in={self.expires_in}s, "
                f"time_until_expiry={self.time_until_expiry:.0f}s)")


class OAuthHandler:
    """
    Manages OAuth 2.0 authentication with SAP Datasphere

    Features:
    - Client credentials grant flow
    - Automatic token refresh
    - Encrypted token storage in memory
    - Thread-safe token access
    - Retry logic with exponential backoff
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        token_url: str,
        scope: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize OAuth handler

        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
            token_url: Token endpoint URL
            scope: Optional OAuth scope
            max_retries: Maximum retry attempts for token acquisition
            retry_delay: Initial retry delay in seconds (exponential backoff)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.scope = scope
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Token storage with encryption
        self._encryption_key = Fernet.generate_key()
        self._cipher = Fernet(self._encryption_key)
        self._encrypted_token: Optional[bytes] = None
        self._token: Optional[OAuthToken] = None
        self._lock = asyncio.Lock()

        # Monitoring
        self._token_acquisition_count = 0
        self._token_refresh_count = 0
        self._last_error: Optional[str] = None

        logger.info(f"OAuth handler initialized for token URL: {token_url}")

    async def get_token(self, force_refresh: bool = False) -> OAuthToken:
        """
        Get a valid access token (acquiring new or refreshing if needed)

        Args:
            force_refresh: Force token refresh even if not expired

        Returns:
            Valid OAuthToken

        Raises:
            TokenAcquisitionError: If token cannot be acquired
        """
        async with self._lock:
            # Return existing token if valid
            if not force_refresh and self._token and not self._token.is_expired:
                logger.debug(f"Using cached token (expires in {self._token.time_until_expiry:.0f}s)")
                return self._token

            # Acquire new token
            if self._token is None or not self._token.refresh_token:
                logger.info("Acquiring new access token")
                return await self._acquire_token()

            # Refresh existing token
            logger.info("Refreshing access token")
            try:
                return await self._refresh_token()
            except TokenRefreshError:
                logger.warning("Token refresh failed, acquiring new token")
                return await self._acquire_token()

    async def _acquire_token(self) -> OAuthToken:
        """
        Acquire a new access token using client credentials flow

        Returns:
            New OAuthToken

        Raises:
            TokenAcquisitionError: If acquisition fails after retries
        """
        payload = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }

        if self.scope:
            payload['scope'] = self.scope

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }

        # Retry logic with exponential backoff
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.token_url,
                        data=payload,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            token = self._create_token_from_response(data)
                            self._store_token(token)
                            self._token_acquisition_count += 1
                            self._last_error = None

                            logger.info(f"Access token acquired successfully (expires in {token.expires_in}s)")
                            return token
                        else:
                            error_text = await response.text()
                            error_msg = f"Token acquisition failed: HTTP {response.status} - {error_text}"
                            logger.error(error_msg)
                            self._last_error = error_msg

                            if response.status == 401:
                                raise TokenAcquisitionError("Invalid client credentials")
                            elif response.status >= 500:
                                # Retry on server errors
                                if attempt < self.max_retries - 1:
                                    delay = self.retry_delay * (2 ** attempt)
                                    logger.warning(f"Retrying in {delay}s... (attempt {attempt + 1}/{self.max_retries})")
                                    await asyncio.sleep(delay)
                                    continue

                            raise TokenAcquisitionError(error_msg)

            except aiohttp.ClientError as e:
                error_msg = f"Network error during token acquisition: {str(e)}"
                logger.error(error_msg)
                self._last_error = error_msg

                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Retrying in {delay}s... (attempt {attempt + 1}/{self.max_retries})")
                    await asyncio.sleep(delay)
                else:
                    raise TokenAcquisitionError(error_msg) from e

            except Exception as e:
                error_msg = f"Unexpected error during token acquisition: {str(e)}"
                logger.error(error_msg)
                self._last_error = error_msg
                raise TokenAcquisitionError(error_msg) from e

        raise TokenAcquisitionError(f"Failed to acquire token after {self.max_retries} attempts")

    async def _refresh_token(self) -> OAuthToken:
        """
        Refresh an existing access token

        Returns:
            Refreshed OAuthToken

        Raises:
            TokenRefreshError: If refresh fails
        """
        if not self._token or not self._token.refresh_token:
            raise TokenRefreshError("No refresh token available")

        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': self._token.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.token_url,
                    data=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        token = self._create_token_from_response(data)
                        self._store_token(token)
                        self._token_refresh_count += 1
                        self._last_error = None

                        logger.info(f"Token refreshed successfully (expires in {token.expires_in}s)")
                        return token
                    else:
                        error_text = await response.text()
                        error_msg = f"Token refresh failed: HTTP {response.status} - {error_text}"
                        logger.error(error_msg)
                        self._last_error = error_msg
                        raise TokenRefreshError(error_msg)

        except aiohttp.ClientError as e:
            error_msg = f"Network error during token refresh: {str(e)}"
            logger.error(error_msg)
            self._last_error = error_msg
            raise TokenRefreshError(error_msg) from e

        except Exception as e:
            error_msg = f"Unexpected error during token refresh: {str(e)}"
            logger.error(error_msg)
            self._last_error = error_msg
            raise TokenRefreshError(error_msg) from e

    def _create_token_from_response(self, data: Dict[str, Any]) -> OAuthToken:
        """
        Create OAuthToken from API response

        Args:
            data: Token response data

        Returns:
            OAuthToken instance
        """
        return OAuthToken(
            access_token=data['access_token'],
            token_type=data.get('token_type', 'Bearer'),
            expires_in=data.get('expires_in', 3600),
            scope=data.get('scope'),
            refresh_token=data.get('refresh_token')
        )

    def _store_token(self, token: OAuthToken):
        """
        Store token with encryption

        Args:
            token: Token to store
        """
        self._token = token

        # Encrypt and store token for additional security
        token_data = token.access_token.encode('utf-8')
        self._encrypted_token = self._cipher.encrypt(token_data)

    async def revoke_token(self) -> bool:
        """
        Revoke the current token (if supported by OAuth server)

        Returns:
            True if revocation successful, False otherwise
        """
        async with self._lock:
            if not self._token:
                logger.warning("No token to revoke")
                return False

            # Note: Implement token revocation if SAP Datasphere supports it
            # For now, just clear the stored token
            self._token = None
            self._encrypted_token = None
            logger.info("Token cleared from memory")
            return True

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get OAuth handler health status

        Returns:
            Dictionary with health metrics
        """
        status = {
            'has_token': self._token is not None,
            'token_expired': self._token.is_expired if self._token else None,
            'time_until_expiry': self._token.time_until_expiry if self._token else None,
            'acquisitions': self._token_acquisition_count,
            'refreshes': self._token_refresh_count,
            'last_error': self._last_error
        }

        return status

    def __repr__(self) -> str:
        """Safe representation"""
        return (f"OAuthHandler(client_id={self.client_id[:8]}..., "
                f"token_url={self.token_url})")


# Helper function for easy initialization
async def create_oauth_handler(
    client_id: str,
    client_secret: str,
    token_url: str,
    scope: Optional[str] = None,
    acquire_token: bool = True
) -> OAuthHandler:
    """
    Create and initialize an OAuth handler

    Args:
        client_id: OAuth client ID
        client_secret: OAuth client secret
        token_url: Token endpoint URL
        scope: Optional OAuth scope
        acquire_token: If True, acquire initial token immediately

    Returns:
        Initialized OAuthHandler

    Raises:
        TokenAcquisitionError: If initial token acquisition fails
    """
    handler = OAuthHandler(
        client_id=client_id,
        client_secret=client_secret,
        token_url=token_url,
        scope=scope
    )

    if acquire_token:
        await handler.get_token()

    return handler
