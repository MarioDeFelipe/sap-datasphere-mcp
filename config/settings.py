#!/usr/bin/env python3
"""
Configuration management for SAP Datasphere MCP Server
Loads settings from environment variables with validation
"""

import os
import logging
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables

    All sensitive credentials should be provided via environment variables
    or a .env file. Never commit credentials to source control.
    """

    # SAP Datasphere Connection
    datasphere_base_url: str = Field(
        ...,
        description="SAP Datasphere tenant URL (e.g., https://tenant.eu10.hcs.cloud.sap)"
    )
    datasphere_tenant_id: str = Field(
        ...,
        description="SAP Datasphere tenant identifier"
    )

    # OAuth 2.0 Credentials (Technical User)
    datasphere_client_id: str = Field(
        ...,
        description="OAuth 2.0 client ID for Technical User"
    )
    datasphere_client_secret: str = Field(
        ...,
        description="OAuth 2.0 client secret for Technical User"
    )
    datasphere_token_url: str = Field(
        ...,
        description="OAuth 2.0 token endpoint URL"
    )
    datasphere_scope: Optional[str] = Field(
        default=None,
        description="Optional OAuth scope"
    )

    # Server Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )
    server_port: int = Field(
        default=8080,
        description="Server port number"
    )

    # Development Mode
    use_mock_data: bool = Field(
        default=False,
        description="Use mock data instead of real API (development only)"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @field_validator("datasphere_base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Validate and normalize base URL"""
        v = v.strip()
        if not v.startswith(("http://", "https://")):
            raise ValueError("Base URL must start with http:// or https://")
        # Remove trailing slash
        return v.rstrip("/")

    @field_validator("datasphere_token_url")
    @classmethod
    def validate_token_url(cls, v: str) -> str:
        """Validate token URL"""
        v = v.strip()
        if not v.startswith(("http://", "https://")):
            raise ValueError("Token URL must start with http:// or https://")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level"""
        v = v.upper()
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v not in valid_levels:
            raise ValueError(f"Log level must be one of: {', '.join(valid_levels)}")
        return v

    @field_validator("server_port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        """Validate server port"""
        if not (1 <= v <= 65535):
            raise ValueError("Port must be between 1 and 65535")
        return v

    def configure_logging(self):
        """Configure logging based on settings"""
        logging.basicConfig(
            level=getattr(logging, self.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger.info(f"Logging configured with level: {self.log_level}")

    def validate_oauth_config(self) -> bool:
        """
        Validate that OAuth configuration is complete

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        if not self.use_mock_data:
            if not self.datasphere_client_id:
                raise ValueError("DATASPHERE_CLIENT_ID is required for OAuth authentication")
            if not self.datasphere_client_secret:
                raise ValueError("DATASPHERE_CLIENT_SECRET is required for OAuth authentication")
            if not self.datasphere_token_url:
                raise ValueError("DATASPHERE_TOKEN_URL is required for OAuth authentication")

        return True

    def get_datasphere_config(self) -> dict:
        """
        Get Datasphere configuration as dictionary

        Returns:
            Configuration dictionary for DatasphereConfig
        """
        return {
            "base_url": self.datasphere_base_url,
            "client_id": self.datasphere_client_id,
            "client_secret": self.datasphere_client_secret,
            "token_url": self.datasphere_token_url,
            "tenant_id": self.datasphere_tenant_id,
            "scope": self.datasphere_scope
        }

    def __repr__(self) -> str:
        """Safe representation without exposing secrets"""
        return (
            f"Settings("
            f"base_url={self.datasphere_base_url}, "
            f"tenant_id={self.datasphere_tenant_id}, "
            f"client_id={self.datasphere_client_id[:8]}..., "
            f"log_level={self.log_level}, "
            f"use_mock_data={self.use_mock_data}"
            f")"
        )


def load_settings() -> Settings:
    """
    Load and validate settings from environment

    Returns:
        Validated Settings instance

    Raises:
        ValueError: If required settings are missing or invalid
    """
    try:
        settings = Settings()
        settings.configure_logging()
        settings.validate_oauth_config()

        logger.info("Configuration loaded successfully")
        logger.debug(f"Settings: {settings}")

        return settings

    except Exception as e:
        logger.error(f"Failed to load configuration: {str(e)}")
        logger.error("Please ensure all required environment variables are set.")
        logger.error("See .env.example for required configuration.")
        raise


# Global settings instance (loaded once)
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get global settings instance (singleton pattern)

    Returns:
        Settings instance
    """
    global _settings
    if _settings is None:
        _settings = load_settings()
    return _settings
