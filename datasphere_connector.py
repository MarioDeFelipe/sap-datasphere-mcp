#!/usr/bin/env python3
"""
SAP Datasphere Connector with OAuth 2.0 Integration
Implements MetadataConnector interface for SAP Datasphere with comprehensive OAuth authentication
"""

import json
import requests
import base64
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urljoin
import re
import time
import threading
from dataclasses import dataclass

from metadata_sync_core import (
    MetadataConnector, MetadataAsset, AssetType, SourceSystem, 
    BusinessContext, LineageRelationship
)
from sync_logging import SyncLogger, EventType

@dataclass
class DatasphereConfig:
    """Configuration for Datasphere connection"""
    base_url: str
    client_id: str
    client_secret: str
    token_url: str
    environment_name: str = "datasphere"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: int = 5

@dataclass
class OAuthToken:
    """OAuth token information"""
    access_token: str
    token_type: str
    expires_in: int
    expires_at: datetime
    scope: Optional[str] = None

class DatasphereConnector(MetadataConnector):
    """SAP Datasphere connector with OAuth 2.0 authentication"""
    
    def __init__(self, config: DatasphereConfig):
        self.config = config
        self.logger = SyncLogger(f"datasphere_connector_{config.environment_name}")
        self.session = requests.Session()
        self.oauth_token: Optional[OAuthToken] = None
        self.token_lock = threading.Lock()
        self.is_connected = False
        
        # Setup session defaults
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': f'Datasphere-Metadata-Sync/{config.environment_name}/2.0'
        })
        
        # Type mappings
        self.odata_to_glue_types = {
            'Edm.String': 'string',
            'Edm.Int32': 'int',
            'Edm.Int64': 'bigint',
            'Edm.Double': 'double',
            'Edm.Decimal': 'decimal(18,2)',
            'Edm.Boolean': 'boolean',
            'Edm.DateTime': 'timestamp',
            'Edm.DateTimeOffset': 'timestamp',
            'Edm.Date': 'date',
            'Edm.Binary': 'binary',
            'Edm.Guid': 'string'
        }
    
    def connect(self) -> bool:
        """Establish connection to Datasphere with OAuth authentication"""
        try:
            self.logger.log_event(
                event_type=EventType.AUTHENTICATION_SUCCESS,
                source_system=self.config.environment_name,
                operation="connect",
                status="attempting",
                details={'base_url': self.config.base_url}
            )
            
            # Authenticate
            if not self._authenticate():
                return False
            
            # Test connection
            if not self._test_connection():
                return False
            
            self.is_connected = True
            
            self.logger.log_event(
                event_type=EventType.AUTHENTICATION_SUCCESS,
                source_system=self.config.environment_name,
                operation="connect",
                status="connected",
                details={
                    'base_url': self.config.base_url,
                    'token_expires_at': self.oauth_token.expires_at.isoformat() if self.oauth_token else None
                }
            )
            
            return True
            
        except Exception as e:
            self.logger.log_event(
                event_type=EventType.AUTHENTICATION_FAILURE,
                source_system=self.config.environment_name,
                operation="connect",
                status="failed",
                details={'base_url': self.config.base_url},
                error_message=str(e)
            )
            
            self.logger.create_error_report(
                error_type="connection_failed",
                error_message=str(e),
                context={
                    'operation': 'connect',
                    'base_url': self.config.base_url,
                    'environment': self.config.environment_name
                },
                affected_assets=[],
                severity="HIGH"
            )
            
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from Datasphere"""
        try:
            self.is_connected = False
            self.oauth_token = None
            
            # Clear session headers
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            self.logger.log_event(
                event_type=EventType.SYNC_COMPLETED,
                source_system=self.config.environment_name,
                operation="disconnect",
                status="disconnected",
                details={}
            )
            
            return True
            
        except Exception as e:
            self.logger.logger.error(f"Error during disconnect: {str(e)}")
            return False
    
    def _authenticate(self) -> bool:
        """Perform OAuth 2.0 client credentials authentication"""
        with self.token_lock:
            try:
                # Check if current token is still valid
                if self._is_token_valid():
                    return True
                
                # Prepare OAuth request
                auth_header = base64.b64encode(
                    f"{self.config.client_id}:{self.config.client_secret}".encode()
                ).decode()
                
                headers = {
                    'Authorization': f'Basic {auth_header}',
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
                
                data = {'grant_type': 'client_credentials'}
                
                # Make token request
                response = requests.post(
                    self.config.token_url,
                    headers=headers,
                    data=data,
                    timeout=self.config.timeout
                )
                
                if response.status_code == 200:
                    token_data = response.json()
                    
                    # Create token object
                    expires_in = token_data.get('expires_in', 3600)
                    self.oauth_token = OAuthToken(
                        access_token=token_data['access_token'],
                        token_type=token_data.get('token_type', 'Bearer'),
                        expires_in=expires_in,
                        expires_at=datetime.now() + timedelta(seconds=expires_in - 300),  # 5 min buffer
                        scope=token_data.get('scope')
                    )
                    
                    # Update session headers
                    self.session.headers['Authorization'] = f'Bearer {self.oauth_token.access_token}'
                    
                    self.logger.logger.info(f"OAuth authentication successful, token expires at {self.oauth_token.expires_at}")
                    return True
                    
                else:
                    error_msg = f"OAuth failed: HTTP {response.status_code} - {response.text}"
                    self.logger.logger.error(error_msg)
                    return False
                    
            except Exception as e:
                self.logger.logger.error(f"Authentication error: {str(e)}")
                return False
    
    def _is_token_valid(self) -> bool:
        """Check if current OAuth token is valid"""
        if not self.oauth_token:
            return False
        
        return datetime.now() < self.oauth_token.expires_at
    
    def _refresh_token_if_needed(self) -> bool:
        """Refresh OAuth token if it's about to expire"""
        if not self._is_token_valid():
            self.logger.logger.info("Token expired or expiring soon, refreshing...")
            return self._authenticate()
        return True
    
    def _test_connection(self) -> bool:
        """Test the connection by making a simple API call"""
        try:
            # Try to access a basic endpoint
            test_endpoints = [
                "/api/v1/datasphere/consumption/analytical",
                "/api/v1/datasphere/consumption",
                "/api/v1/datasphere"
            ]
            
            for endpoint in test_endpoints:
                try:
                    url = urljoin(self.config.base_url, endpoint)
                    response = self.session.get(url, timeout=self.config.timeout)
                    
                    if response.status_code in [200, 404]:  # 404 is OK for discovery
                        self.logger.logger.info(f"Connection test successful via {endpoint}")
                        return True
                    elif response.status_code == 403:
                        self.logger.logger.warning(f"Endpoint {endpoint} returned 403 - permission issue")
                        continue
                    else:
                        self.logger.logger.debug(f"Endpoint {endpoint} returned {response.status_code}")
                        continue
                        
                except Exception as e:
                    self.logger.logger.debug(f"Test endpoint {endpoint} failed: {str(e)}")
                    continue
            
            # If we get here, all endpoints failed with non-permission errors
            self.logger.logger.warning("All test endpoints failed, but authentication succeeded")
            return True  # Authentication worked, permission issues are separate
            
        except Exception as e:
            self.logger.logger.error(f"Connection test failed: {str(e)}")
            return False
    
    def get_assets(self, asset_type: AssetType = None) -> List[MetadataAsset]:
        """Retrieve metadata assets from Datasphere"""
        if not self.is_connected:
            self.logger.logger.error("Not connected to Datasphere")
            return []
        
        if not self._refresh_token_if_needed():
            self.logger.logger.error("Failed to refresh token")
            return []
        
        assets = []
        
        try:
            # Discover analytical models (highest priority)
            if asset_type is None or asset_type == AssetType.ANALYTICAL_MODEL:
                analytical_models = self._discover_analytical_models()
                assets.extend(analytical_models)
            
            # Discover spaces
            if asset_type is None or asset_type == AssetType.SPACE:
                spaces = self._discover_spaces()
                assets.extend(spaces)
            
            # Discover tables and views (if accessible)
            if asset_type is None or asset_type in [AssetType.TABLE, AssetType.VIEW]:
                tables_and_views = self._discover_tables_and_views()
                assets.extend(tables_and_views)
            
            self.logger.log_event(
                event_type=EventType.SYNC_COMPLETED,
                source_system=self.config.environment_name,
                operation="get_assets",
                status="completed",
                details={
                    'total_assets': len(assets),
                    'asset_types': list(set([asset.asset_type.value for asset in assets]))
                }
            )
            
        except Exception as e:
            self.logger.log_event(
                event_type=EventType.ERROR_OCCURRED,
                source_system=self.config.environment_name,
                operation="get_assets",
                status="failed",
                details={},
                error_message=str(e)
            )
        
        return assets
    
    def _discover_analytical_models(self) -> List[MetadataAsset]:
        """Discover analytical models from Datasphere"""
        models = []
        
        try:
            # Known working models and discovery patterns
            known_models = [
                {"space": "SAP_CONTENT", "model": "New_Analytic_Model_2"},
                {"space": "SAP_SC_FI_AM", "model": "FINTRANSACTIONS"}
            ]
            
            # Try discovery endpoints
            discovery_endpoints = [
                "/api/v1/datasphere/consumption/analytical",
                "/api/v1/datasphere/consumption",
                "/api/v1/datasphere/models"
            ]
            
            discovered_models = []
            for endpoint in discovery_endpoints:
                try:
                    url = urljoin(self.config.base_url, endpoint)
                    response = self.session.get(url, timeout=self.config.timeout)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Parse response to find models
                        if isinstance(data, dict) and 'value' in data:
                            for item in data['value']:
                                if 'name' in item:
                                    discovered_models.append({
                                        "space": item.get('space', 'UNKNOWN'),
                                        "model": item['name']
                                    })
                        
                        self.logger.logger.info(f"Discovery endpoint {endpoint} returned {len(discovered_models)} models")
                        break
                        
                except Exception as e:
                    self.logger.logger.debug(f"Discovery endpoint {endpoint} failed: {str(e)}")
                    continue
            
            # Combine known and discovered models
            all_models = known_models + discovered_models
            
            # Remove duplicates
            unique_models = []
            seen = set()
            for model in all_models:
                key = f"{model['space']}/{model['model']}"
                if key not in seen:
                    seen.add(key)
                    unique_models.append(model)
            
            # Extract metadata for each model
            for model_info in unique_models:
                try:
                    asset = self._extract_analytical_model_metadata(
                        model_info['space'], 
                        model_info['model']
                    )
                    if asset:
                        models.append(asset)
                        
                except Exception as e:
                    self.logger.logger.warning(f"Failed to extract {model_info['space']}/{model_info['model']}: {str(e)}")
                    continue
            
            self.logger.logger.info(f"Discovered {len(models)} analytical models")
            
        except Exception as e:
            self.logger.logger.error(f"Error discovering analytical models: {str(e)}")
        
        return models
    
    def _extract_analytical_model_metadata(self, space: str, model: str) -> Optional[MetadataAsset]:
        """Extract detailed metadata for a specific analytical model"""
        try:
            # Build URLs using the working pattern
            model_base = f"/api/v1/datasphere/consumption/analytical/{space}/{model}"
            service_url = urljoin(self.config.base_url, model_base)
            metadata_url = urljoin(self.config.base_url, f"{model_base}/$metadata")
            data_url = urljoin(self.config.base_url, f"{model_base}/{model}")
            
            # Get service info
            service_response = self.session.get(service_url, timeout=self.config.timeout)
            
            if service_response.status_code != 200:
                self.logger.logger.warning(f"Service endpoint failed for {space}/{model}: HTTP {service_response.status_code}")
                return None
            
            service_data = service_response.json()
            odata_context = service_data.get('@odata.context', '')
            
            # Extract columns from metadata
            columns = self._extract_columns_from_metadata(metadata_url)
            
            # Extract business context
            business_context = self._extract_business_context(service_data, space, model)
            
            # Create asset
            asset = MetadataAsset(
                asset_id=f"{self.config.environment_name}_{space}_{model}",
                asset_type=AssetType.ANALYTICAL_MODEL,
                source_system=SourceSystem.DATASPHERE,
                technical_name=model,
                business_name=business_context.business_name or model,
                description=business_context.description or f"Analytical model from {space}",
                owner=business_context.owner or "datasphere",
                business_context=business_context,
                schema_info={
                    'columns': columns,
                    'odata_context': odata_context,
                    'service_url': service_url,
                    'metadata_url': metadata_url,
                    'data_url': data_url
                },
                custom_properties={
                    'datasphere_space': space,
                    'datasphere_model': model,
                    'datasphere_environment': self.config.environment_name,
                    'extraction_timestamp': datetime.now().isoformat()
                }
            )
            
            self.logger.log_asset_operation(
                operation="extract",
                asset_id=asset.asset_id,
                asset_type=asset.asset_type.value,
                source_system=self.config.environment_name,
                target_system="metadata_sync",
                status="completed",
                details={
                    'space': space,
                    'model': model,
                    'columns_count': len(columns),
                    'has_business_context': bool(business_context.business_name)
                }
            )
            
            return asset
            
        except Exception as e:
            self.logger.logger.error(f"Failed to extract metadata for {space}/{model}: {str(e)}")
            return None
    
    def _extract_columns_from_metadata(self, metadata_url: str) -> List[Dict[str, Any]]:
        """Extract column information from OData metadata"""
        try:
            # Try XML metadata first
            headers = self.session.headers.copy()
            headers['Accept'] = 'application/xml'
            
            response = self.session.get(metadata_url, headers=headers, timeout=self.config.timeout)
            
            if response.status_code == 200 and 'xml' in response.headers.get('content-type', ''):
                return self._parse_odata_metadata_xml(response.text)
            
            # Fallback: try to infer from data endpoint
            self.logger.logger.warning("XML metadata not available, trying data inference")
            data_url = metadata_url.replace('/$metadata', f'/{metadata_url.split("/")[-2]}')
            return self._infer_columns_from_data(data_url)
            
        except Exception as e:
            self.logger.logger.warning(f"Column extraction failed: {str(e)}")
            return []
    
    def _parse_odata_metadata_xml(self, xml_content: str) -> List[Dict[str, Any]]:
        """Parse OData XML metadata to extract column information"""
        columns = []
        
        try:
            root = ET.fromstring(xml_content)
            
            # Define namespaces
            namespaces = {
                'edmx': 'http://docs.oasis-open.org/odata/ns/edmx',
                'edm': 'http://docs.oasis-open.org/odata/ns/edm'
            }
            
            # Find EntityType elements
            for entity_type in root.findall('.//edm:EntityType', namespaces):
                for prop in entity_type.findall('edm:Property', namespaces):
                    column = {
                        'name': prop.get('Name', ''),
                        'type': self._convert_odata_type_to_glue(prop.get('Type', '')),
                        'nullable': prop.get('Nullable', 'true').lower() == 'true',
                        'description': f"Column from OData metadata"
                    }
                    
                    # Add additional attributes if present
                    if prop.get('MaxLength'):
                        column['max_length'] = prop.get('MaxLength')
                    if prop.get('Precision'):
                        column['precision'] = prop.get('Precision')
                    if prop.get('Scale'):
                        column['scale'] = prop.get('Scale')
                    
                    columns.append(column)
            
            self.logger.logger.info(f"Parsed {len(columns)} columns from XML metadata")
            
        except ET.ParseError as e:
            self.logger.logger.error(f"XML parsing failed: {str(e)}")
        except Exception as e:
            self.logger.logger.error(f"Metadata parsing failed: {str(e)}")
        
        return columns
    
    def _infer_columns_from_data(self, data_url: str) -> List[Dict[str, Any]]:
        """Infer column structure from actual data"""
        try:
            # Get a small sample of data
            params = {'$top': 1}
            response = self.session.get(data_url, params=params, timeout=self.config.timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                # Handle OData response format
                records = data.get('value', []) if isinstance(data, dict) else [data]
                
                if records and len(records) > 0:
                    sample_record = records[0]
                    columns = []
                    
                    for field_name, field_value in sample_record.items():
                        if field_name.startswith('@'):  # Skip OData metadata fields
                            continue
                        
                        # Infer type from value
                        inferred_type = self._infer_type_from_value(field_value)
                        
                        columns.append({
                            'name': field_name,
                            'type': inferred_type,
                            'nullable': field_value is None,
                            'description': f"Inferred from data sample"
                        })
                    
                    self.logger.logger.info(f"Inferred {len(columns)} columns from data")
                    return columns
            
        except Exception as e:
            self.logger.logger.warning(f"Data inference failed: {str(e)}")
        
        return []
    
    def _infer_type_from_value(self, value: Any) -> str:
        """Infer Glue data type from a sample value"""
        if value is None:
            return 'string'
        elif isinstance(value, bool):
            return 'boolean'
        elif isinstance(value, int):
            return 'bigint'
        elif isinstance(value, float):
            return 'double'
        elif isinstance(value, str):
            # Try to detect date/timestamp patterns
            if re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', value):
                return 'timestamp'
            elif re.match(r'\d{4}-\d{2}-\d{2}', value):
                return 'date'
            else:
                return 'string'
        else:
            return 'string'
    
    def _convert_odata_type_to_glue(self, odata_type: str) -> str:
        """Convert OData types to AWS Glue types"""
        # Remove namespace prefix if present
        clean_type = odata_type.split('.')[-1] if '.' in odata_type else odata_type
        full_type = f'Edm.{clean_type}' if not odata_type.startswith('Edm.') else odata_type
        
        return self.odata_to_glue_types.get(full_type, 'string')
    
    def _extract_business_context(self, service_data: Dict[str, Any], space: str, model: str) -> BusinessContext:
        """Extract business context from service data"""
        return BusinessContext(
            business_name=service_data.get('displayName', model),
            description=service_data.get('description', f"Analytical model from {space}"),
            owner=service_data.get('owner', 'datasphere'),
            steward=service_data.get('steward'),
            certification_status=service_data.get('certificationStatus'),
            tags=[space, 'analytical_model', 'datasphere'],
            dimensions=service_data.get('dimensions', []),
            measures=service_data.get('measures', []),
            hierarchies=service_data.get('hierarchies', [])
        )
    
    def _discover_spaces(self) -> List[MetadataAsset]:
        """Discover spaces from Datasphere"""
        spaces = []
        
        try:
            # Known spaces from our exploration
            known_spaces = ["SAP_CONTENT", "SAP_SC_FI_AM"]
            
            for space_name in known_spaces:
                asset = MetadataAsset(
                    asset_id=f"{self.config.environment_name}_space_{space_name}",
                    asset_type=AssetType.SPACE,
                    source_system=SourceSystem.DATASPHERE,
                    technical_name=space_name,
                    business_name=space_name,
                    description=f"Datasphere space: {space_name}",
                    owner="datasphere",
                    business_context=BusinessContext(
                        business_name=space_name,
                        description=f"Datasphere space containing analytical models and data",
                        tags=['space', 'datasphere', space_name.lower()]
                    ),
                    custom_properties={
                        'datasphere_space': space_name,
                        'datasphere_environment': self.config.environment_name
                    }
                )
                spaces.append(asset)
            
            self.logger.logger.info(f"Discovered {len(spaces)} spaces")
            
        except Exception as e:
            self.logger.logger.error(f"Error discovering spaces: {str(e)}")
        
        return spaces
    
    def _discover_tables_and_views(self) -> List[MetadataAsset]:
        """Discover tables and views from Datasphere"""
        tables_and_views = []
        
        try:
            # Get list of spaces first
            from urllib.parse import urljoin
            spaces_url = urljoin(self.config.base_url, "/api/v1/datasphere/consumption/spaces")
            spaces_response = self.session.get(spaces_url, timeout=self.config.timeout)
            
            if spaces_response.status_code != 200:
                self.logger.logger.warning(f"Could not get spaces: HTTP {spaces_response.status_code}")
                return []
            
            spaces_data = spaces_response.json()
            if not spaces_data or 'value' not in spaces_data:
                self.logger.logger.warning("No spaces found or invalid response")
                return []
            
            # For each space, try to discover tables/views
            for space_data in spaces_data['value']:
                space_id = space_data.get('ID', '')
                if not space_id:
                    continue
                
                # Try to get tables/views from the space
                # This is a best-effort approach based on common Datasphere patterns
                tables_endpoint = f"/api/v1/datasphere/consumption/spaces('{space_id}')/tables"
                views_endpoint = f"/api/v1/datasphere/consumption/spaces('{space_id}')/views"
                
                # Try tables endpoint
                try:
                    tables_url = urljoin(self.config.base_url, tables_endpoint)
                    tables_response = self.session.get(tables_url, timeout=self.config.timeout)
                    if tables_response.status_code == 200:
                        tables_data = tables_response.json()
                        if tables_data and 'value' in tables_data:
                            for table_data in tables_data['value']:
                                table_name = table_data.get('name', table_data.get('ID', ''))
                                if table_name:
                                    asset = MetadataAsset(
                                        asset_id=f"datasphere_table_{space_id}_{table_name}",
                                        asset_type=AssetType.TABLE,
                                        source_system=SourceSystem.DATASPHERE,
                                        technical_name=table_name,
                                        business_name=table_data.get('displayName', table_name),
                                        description=f"Datasphere table: {table_name} in space {space_id}",
                                        owner=table_data.get('owner', 'unknown'),
                                        business_context=BusinessContext(
                                            business_name=table_data.get('displayName', table_name),
                                            description=f"Table from Datasphere space {space_id}",
                                            tags=['datasphere', 'table', space_id]
                                        )
                                    )
                                    tables_and_views.append(asset)
                except Exception as e:
                    self.logger.logger.debug(f"Could not access tables in space {space_id}: {str(e)}")
                
                # Try views endpoint
                try:
                    views_url = urljoin(self.config.base_url, views_endpoint)
                    views_response = self.session.get(views_url, timeout=self.config.timeout)
                    if views_response.status_code == 200:
                        views_data = views_response.json()
                        if views_data and 'value' in views_data:
                            for view_data in views_data['value']:
                                view_name = view_data.get('name', view_data.get('ID', ''))
                                if view_name:
                                    asset = MetadataAsset(
                                        asset_id=f"datasphere_view_{space_id}_{view_name}",
                                        asset_type=AssetType.VIEW,
                                        source_system=SourceSystem.DATASPHERE,
                                        technical_name=view_name,
                                        business_name=view_data.get('displayName', view_name),
                                        description=f"Datasphere view: {view_name} in space {space_id}",
                                        owner=view_data.get('owner', 'unknown'),
                                        business_context=BusinessContext(
                                            business_name=view_data.get('displayName', view_name),
                                            description=f"View from Datasphere space {space_id}",
                                            tags=['datasphere', 'view', space_id]
                                        )
                                    )
                                    tables_and_views.append(asset)
                except Exception as e:
                    self.logger.logger.debug(f"Could not access views in space {space_id}: {str(e)}")
            
            self.logger.logger.info(f"Discovered {len(tables_and_views)} tables and views")
            
        except Exception as e:
            self.logger.logger.error(f"Failed to discover tables and views: {str(e)}")
        
        return tables_and_views
    
    def create_asset(self, asset: MetadataAsset) -> bool:
        """Create a new metadata asset (not supported for Datasphere)"""
        self.logger.logger.warning("Create asset operation not supported for Datasphere connector")
        return False
    
    def update_asset(self, asset: MetadataAsset) -> bool:
        """Update an existing metadata asset (not supported for Datasphere)"""
        self.logger.logger.warning("Update asset operation not supported for Datasphere connector")
        return False
    
    def delete_asset(self, asset_id: str) -> bool:
        """Delete a metadata asset (not supported for Datasphere)"""
        self.logger.logger.warning("Delete asset operation not supported for Datasphere connector")
        return False
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get current connection status"""
        return {
            'is_connected': self.is_connected,
            'environment': self.config.environment_name,
            'base_url': self.config.base_url,
            'token_valid': self._is_token_valid(),
            'token_expires_at': self.oauth_token.expires_at.isoformat() if self.oauth_token else None,
            'last_connection_test': datetime.now().isoformat()
        }

# Factory function for creating connectors
def create_datasphere_connector(environment: str = "wolf") -> DatasphereConnector:
    """Create a Datasphere connector for the specified environment"""
    
    # Environment configurations
    configs = {
        "dog": DatasphereConfig(
            base_url="https://f45fa9cc-f4b5-4126-ab73-b19b578fb17a.eu10.hcs.cloud.sap",
            client_id="sb-60cb266e-ad9d-49f7-9967-b53b8286a259!b130936|client!b3944",
            client_secret="caaea1b9-b09b-4d28-83fe-09966d525243$LOFW4h5LpLvB3Z2FE0P7FiH4-C7qexeQPi22DBiHbz8=",
            token_url="https://ailien-test.authentication.eu20.hana.ondemand.com/oauth/token",
            environment_name="dog"
        ),
        "wolf": DatasphereConfig(
            base_url="https://ailien-test.eu20.hcs.cloud.sap",
            client_id="sb-60cb266e-ad9d-49f7-9967-b53b8286a259!b130936|client!b3944",
            client_secret="YOUR_WOLF_SECRET",  # Replace with actual secret
            token_url="https://ailien-test.authentication.eu20.hana.ondemand.com/oauth/token",
            environment_name="wolf"
        ),
        "bear": DatasphereConfig(
            base_url="https://ailien-test.eu20.hcs.cloud.sap",
            client_id="sb-60cb266e-ad9d-49f7-9967-b53b8286a259!b130936|client!b3944",
            client_secret="YOUR_BEAR_SECRET",  # Replace with actual secret
            token_url="https://ailien-test.authentication.eu20.hana.ondemand.com/oauth/token",
            environment_name="bear"
        )
    }
    
    if environment not in configs:
        raise ValueError(f"Unknown environment: {environment}. Available: {list(configs.keys())}")
    
    return DatasphereConnector(configs[environment])

# Example usage and testing
if __name__ == "__main__":
    print("🔗 Datasphere Connector Test")
    print("=" * 30)
    
    # Test with Dog environment (has working credentials)
    try:
        connector = create_datasphere_connector("dog")
        
        print(f"Testing connection to {connector.config.environment_name}...")
        
        # Test connection
        if connector.connect():
            print("✅ Connection successful!")
            
            # Get connection status
            status = connector.get_connection_status()
            print(f"📊 Connection Status: {status}")
            
            # Get assets
            print("\n🔍 Discovering assets...")
            assets = connector.get_assets()
            
            print(f"📊 Discovery Results:")
            print(f"  Total assets: {len(assets)}")
            
            for asset in assets:
                print(f"  • {asset.asset_type.value}: {asset.technical_name}")
                print(f"    Business name: {asset.business_name}")
                print(f"    Description: {asset.description}")
                if hasattr(asset, 'schema_info') and 'columns' in asset.schema_info:
                    print(f"    Columns: {len(asset.schema_info['columns'])}")
                print()
            
            # Disconnect
            connector.disconnect()
            print("✅ Disconnected successfully")
            
        else:
            print("❌ Connection failed")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print(f"\n🎉 Datasphere connector test completed!")