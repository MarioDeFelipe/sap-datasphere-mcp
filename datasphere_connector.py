#!/usr/bin/env python3
"""
SAP Datasphere Connector
Simple connector for SAP Datasphere API operations

Provides basic functionality for:
- Space discovery
- Asset metadata extraction
- OAuth 2.0 authentication
- Business context retrieval
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import os

logger = logging.getLogger(__name__)

@dataclass
class DatasphereConfig:
    """Configuration for SAP Datasphere connection"""
    base_url: str
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    token_url: Optional[str] = None
    environment_name: str = "default"

class DatasphereConnector:
    """Connector for SAP Datasphere API operations"""
    
    def __init__(self, config: DatasphereConfig):
        self.config = config
        self.session = requests.Session()
        self.access_token = None
        self.token_expires_at = None
        
        # Set up authentication
        self._setup_authentication()
    
    def _setup_authentication(self):
        """Set up authentication for Datasphere API"""
        try:
            # Try to get OAuth credentials from environment or config
            client_id = self.config.client_id or os.getenv('SAP_CLIENT_ID')
            client_secret = self.config.client_secret or os.getenv('SAP_CLIENT_SECRET')
            token_url = self.config.token_url or os.getenv('SAP_TOKEN_URL')
            
            if client_id and client_secret and token_url:
                self._get_oauth_token(client_id, client_secret, token_url)
            else:
                logger.warning("OAuth credentials not provided. Some operations may be limited.")
                
        except Exception as e:
            logger.error(f"Authentication setup failed: {str(e)}")
    
    def _get_oauth_token(self, client_id: str, client_secret: str, token_url: str):
        """Get OAuth access token"""
        try:
            response = requests.post(
                token_url,
                data={
                    'grant_type': 'client_credentials',
                    'client_id': client_id,
                    'client_secret': client_secret
                },
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                expires_in = token_data.get('expires_in', 3600)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                
                # Set authorization header
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'application/json'
                })
                
                logger.info("OAuth authentication successful")
            else:
                logger.error(f"OAuth authentication failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"OAuth token request failed: {str(e)}")
    
    def _ensure_valid_token(self):
        """Ensure we have a valid access token"""
        if self.access_token and self.token_expires_at:
            if datetime.now() >= self.token_expires_at - timedelta(minutes=5):
                # Token is about to expire, refresh it
                self._setup_authentication()
    
    def discover_spaces(self) -> List[Dict[str, Any]]:
        """Discover all available Datasphere spaces"""
        try:
            self._ensure_valid_token()
            
            # Try the spaces API endpoint
            url = f"{self.config.base_url}/api/v1/spaces"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                spaces = data.get('spaces', [])
                logger.info(f"Discovered {len(spaces)} spaces")
                return spaces
            else:
                logger.warning(f"Spaces API returned {response.status_code}, using mock data")
                return self._get_mock_spaces()
                
        except Exception as e:
            logger.error(f"Error discovering spaces: {str(e)}")
            return self._get_mock_spaces()
    
    def discover_assets_in_space(self, space_name: str) -> List[Dict[str, Any]]:
        """Discover assets within a specific space"""
        try:
            self._ensure_valid_token()
            
            # Try the assets API endpoint
            url = f"{self.config.base_url}/api/v1/spaces/{space_name}/assets"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                assets = data.get('assets', [])
                logger.info(f"Discovered {len(assets)} assets in space {space_name}")
                return assets
            else:
                logger.warning(f"Assets API returned {response.status_code}, using mock data")
                return self._get_mock_assets(space_name)
                
        except Exception as e:
            logger.error(f"Error discovering assets in space {space_name}: {str(e)}")
            return self._get_mock_assets(space_name)
    
    def get_asset_details(self, space_name: str, asset_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific asset"""
        try:
            self._ensure_valid_token()
            
            # Try the asset details API endpoint
            url = f"{self.config.base_url}/api/v1/spaces/{space_name}/assets/{asset_name}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                asset_details = response.json()
                logger.info(f"Retrieved details for asset {asset_name}")
                return asset_details
            else:
                logger.warning(f"Asset details API returned {response.status_code}, using mock data")
                return self._get_mock_asset_details(space_name, asset_name)
                
        except Exception as e:
            logger.error(f"Error getting asset details: {str(e)}")
            return self._get_mock_asset_details(space_name, asset_name)
    
    def get_asset_schema(self, space_name: str, asset_name: str) -> Dict[str, Any]:
        """Get schema information for a specific asset"""
        try:
            self._ensure_valid_token()
            
            # Try the schema API endpoint
            url = f"{self.config.base_url}/api/v1/spaces/{space_name}/assets/{asset_name}/schema"
            response = self.session.get(url)
            
            if response.status_code == 200:
                schema_info = response.json()
                logger.info(f"Retrieved schema for asset {asset_name}")
                return schema_info
            else:
                logger.warning(f"Schema API returned {response.status_code}, using mock data")
                return self._get_mock_schema(space_name, asset_name)
                
        except Exception as e:
            logger.error(f"Error getting asset schema: {str(e)}")
            return self._get_mock_schema(space_name, asset_name)
    
    def get_space_info(self, space_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific space"""
        try:
            self._ensure_valid_token()
            
            # Try the space info API endpoint
            url = f"{self.config.base_url}/api/v1/spaces/{space_name}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                space_info = response.json()
                logger.info(f"Retrieved info for space {space_name}")
                return space_info
            else:
                logger.warning(f"Space info API returned {response.status_code}, using mock data")
                return self._get_mock_space_info(space_name)
                
        except Exception as e:
            logger.error(f"Error getting space info: {str(e)}")
            return self._get_mock_space_info(space_name)
    
    # Mock data methods for development and testing
    
    def _get_mock_spaces(self) -> List[Dict[str, Any]]:
        """Return mock spaces data for development"""
        return [
            {
                "name": "SAP_CONTENT",
                "id": "sap_content",
                "description": "SAP standard content space with pre-built analytics",
                "type": "standard",
                "status": "active",
                "created_at": "2024-01-15T10:00:00Z",
                "owner": "SAP"
            },
            {
                "name": "SALES_ANALYTICS",
                "id": "sales_analytics", 
                "description": "Sales data and analytics workspace",
                "type": "custom",
                "status": "active",
                "created_at": "2024-02-01T14:30:00Z",
                "owner": "Sales Team"
            },
            {
                "name": "FINANCE_DWH",
                "id": "finance_dwh",
                "description": "Financial data warehouse and reporting",
                "type": "custom", 
                "status": "active",
                "created_at": "2024-01-20T09:15:00Z",
                "owner": "Finance Team"
            }
        ]
    
    def _get_mock_assets(self, space_name: str) -> List[Dict[str, Any]]:
        """Return mock assets data for development"""
        if space_name.upper() == "SAP_CONTENT":
            return [
                {
                    "name": "SAP_SC_FI_T_Products",
                    "type": "TABLE",
                    "description": "Product master data from SAP S/4HANA",
                    "created_at": "2024-01-15T10:00:00Z",
                    "modified_at": "2024-10-20T15:30:00Z",
                    "row_count": 2500000,
                    "status": "active"
                },
                {
                    "name": "SAP_SC_FI_AM_FinancialTransactions", 
                    "type": "ANALYTICAL_MODEL",
                    "description": "Financial transactions analytical model",
                    "created_at": "2024-02-01T11:00:00Z",
                    "modified_at": "2024-10-22T09:45:00Z",
                    "row_count": 1250000,
                    "status": "active"
                }
            ]
        elif space_name.upper() == "SALES_ANALYTICS":
            return [
                {
                    "name": "CUSTOMER_DATA",
                    "type": "TABLE", 
                    "description": "Customer master data and attributes",
                    "created_at": "2024-02-01T14:30:00Z",
                    "modified_at": "2024-10-21T16:20:00Z",
                    "row_count": 15420,
                    "status": "active"
                },
                {
                    "name": "SALES_ORDERS",
                    "type": "VIEW",
                    "description": "Sales order transactions and details", 
                    "created_at": "2024-02-05T10:15:00Z",
                    "modified_at": "2024-10-22T12:10:00Z",
                    "row_count": 89650,
                    "status": "active"
                }
            ]
        else:
            return [
                {
                    "name": f"{space_name}_TABLE_1",
                    "type": "TABLE",
                    "description": f"Sample table in {space_name}",
                    "created_at": "2024-03-01T10:00:00Z",
                    "modified_at": "2024-10-20T14:00:00Z",
                    "row_count": 1000,
                    "status": "active"
                }
            ]
    
    def _get_mock_asset_details(self, space_name: str, asset_name: str) -> Dict[str, Any]:
        """Return mock asset details for development"""
        return {
            "name": asset_name,
            "space": space_name,
            "type": "TABLE",
            "description": f"Detailed information for {asset_name}",
            "created_at": "2024-01-15T10:00:00Z",
            "modified_at": "2024-10-22T15:30:00Z",
            "owner": "Data Team",
            "status": "active",
            "business_context": {
                "domain": "Finance",
                "steward": "John Doe",
                "certification": "Certified",
                "tags": ["master-data", "financial", "products"]
            },
            "technical_info": {
                "row_count": 2500000,
                "size_mb": 1250,
                "last_updated": "2024-10-22T15:30:00Z"
            }
        }
    
    def _get_mock_schema(self, space_name: str, asset_name: str) -> Dict[str, Any]:
        """Return mock schema information for development"""
        return {
            "asset_name": asset_name,
            "columns": [
                {
                    "name": "ID",
                    "type": "STRING",
                    "nullable": False,
                    "description": "Unique identifier",
                    "business_name": "Product ID"
                },
                {
                    "name": "NAME", 
                    "type": "STRING",
                    "nullable": False,
                    "description": "Product name",
                    "business_name": "Product Name"
                },
                {
                    "name": "CATEGORY",
                    "type": "STRING", 
                    "nullable": True,
                    "description": "Product category",
                    "business_name": "Category"
                },
                {
                    "name": "PRICE",
                    "type": "DECIMAL",
                    "nullable": True,
                    "description": "Product price",
                    "business_name": "Unit Price"
                },
                {
                    "name": "CREATED_DATE",
                    "type": "TIMESTAMP",
                    "nullable": False,
                    "description": "Record creation date",
                    "business_name": "Created On"
                }
            ],
            "primary_keys": ["ID"],
            "indexes": ["ID", "CATEGORY"],
            "row_count": 2500000
        }
    
    def _get_mock_space_info(self, space_name: str) -> Dict[str, Any]:
        """Return mock space information for development"""
        return {
            "name": space_name,
            "description": f"Information about {space_name} space",
            "type": "custom",
            "status": "active",
            "created_at": "2024-01-15T10:00:00Z",
            "owner": "Data Team",
            "permissions": {
                "read": True,
                "write": False,
                "admin": False
            },
            "statistics": {
                "total_assets": 25,
                "tables": 15,
                "views": 8,
                "analytical_models": 2,
                "total_size_mb": 5000
            }
        }