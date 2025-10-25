#!/usr/bin/env python3
"""
Enhanced Datasphere Connector with OAuth Authorization Code Flow
Integrates production authentication service with existing metadata sync infrastructure

This enhanced connector provides:
- OAuth Authorization Code Flow for full API access
- Fallback to existing authentication methods
- Seamless integration with existing metadata sync workflows
- Production-ready error handling and token management
- Complete compatibility with existing DatasphereConnector interface

OUTCOME: Drop-in replacement for DatasphereConnector with OAuth Authorization Code Flow
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import threading
import logging

# Import base connector and dependencies
from datasphere_connector import DatasphereConnector, DatasphereConfig, MetadataAsset, AssetType
from production_authentication_service import ProductionAuthenticationService, AuthenticationResult
from sync_logging import SyncLogger, EventType

# Configure logging
logger = logging.getLogger(__name__)

class EnhancedDatasphereConnector(DatasphereConnector):
    """
    Enhanced Datasphere Connector with OAuth Authorization Code Flow
    
    This connector extends the base DatasphereConnector to provide:
    - OAuth Authorization Code Flow for full API permissions
    - Automatic fallback to existing authentication methods
    - Production-ready authentication with proper error handling
    - Seamless integration with existing metadata sync workflows
    - Complete compatibility with existing connector interface
    
    The connector maintains full backward compatibility while adding OAuth capabilities.
    """
    
    def __init__(self, config: DatasphereConfig, 
                 oauth_redirect_uri: str = "http://localhost:8080/callback",
                 enable_oauth: bool = True,
                 enable_fallback_auth: bool = True):
        """
        Initialize enhanced Datasphere connector
        
        Args:
            config: Datasphere configuration
            oauth_redirect_uri: OAuth redirect URI for authorization code flow
            enable_oauth: Enable OAuth Authorization Code Flow
            enable_fallback_auth: Enable fallback authentication methods
        """
        # Initialize base connector
        super().__init__(config)
        
        # OAuth configuration
        self.oauth_redirect_uri = oauth_redirect_uri
        self.enable_oauth = enable_oauth
        self.enable_fallback_auth = enable_fallback_auth
        
        # Initialize production authentication service
        self.auth_service: Optional[ProductionAuthenticationService] = None
        self.authentication_result: Optional[AuthenticationResult] = None
        
        if self.enable_oauth:
            try:
                self.auth_service = ProductionAuthenticationService(
                    config=config,
                    oauth_redirect_uri=oauth_redirect_uri,
                    enable_fallback_methods=enable_fallback_auth
                )
                
                self.logger.logger.info("Enhanced Datasphere Connector initialized with OAuth support")
                
            except Exception as e:
                self.logger.logger.error(f"Failed to initialize OAuth authentication service: {str(e)}")
                if not enable_fallback_auth:
                    raise
                else:
                    self.logger.logger.warning("OAuth initialization failed, will use fallback authentication")
                    self.auth_service = None
        
        # Enhanced connection state
        self.oauth_authenticated = False
        self.authentication_method = None
        self.last_auth_test: Optional[datetime] = None
        self.auth_test_results: Optional[Dict[str, Any]] = None
    
    def connect(self) -> bool:
        """
        Enhanced connection with OAuth Authorization Code Flow
        
        This method attempts OAuth authentication first, then falls back to
        existing authentication methods if OAuth is not available or fails.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.logger.log_event(
                event_type=EventType.AUTHENTICATION_SUCCESS,
                source_system=self.config.environment_name,
                operation="enhanced_connect",
                status="attempting",
                details={
                    'oauth_enabled': self.enable_oauth,
                    'fallback_enabled': self.enable_fallback_auth,
                    'oauth_service_available': self.auth_service is not None
                }
            )
            
            # Try OAuth authentication first
            if self.enable_oauth and self.auth_service:
                try:
                    self.logger.logger.info("Attempting OAuth Authorization Code Flow authentication...")
                    
                    # Perform OAuth authentication
                    auth_result = self.auth_service.authenticate()
                    self.authentication_result = auth_result
                    
                    if auth_result.success:
                        # OAuth authentication successful
                        self.session = self.auth_service.get_authenticated_session()
                        self.oauth_authenticated = True
                        self.authentication_method = auth_result.method
                        self.is_connected = True
                        
                        # Test API access
                        self._test_enhanced_api_access()
                        
                        self.logger.log_event(
                            event_type=EventType.AUTHENTICATION_SUCCESS,
                            source_system=self.config.environment_name,
                            operation="enhanced_connect",
                            status="oauth_success",
                            details={
                                'method': auth_result.method,
                                'metadata_accessible': auth_result.metadata_accessible,
                                'expires_at': auth_result.expires_at.isoformat() if auth_result.expires_at else None
                            }
                        )
                        
                        self.logger.logger.info(f"OAuth authentication successful with method: {auth_result.method}")
                        
                        # Initialize services with OAuth session
                        self._initialize_services_with_oauth()
                        
                        return True
                    
                    else:
                        self.logger.logger.warning(f"OAuth authentication failed: {auth_result.error_message}")
                        
                        if not self.enable_fallback_auth:
                            return False
                
                except Exception as e:
                    self.logger.logger.error(f"OAuth authentication error: {str(e)}")
                    
                    if not self.enable_fallback_auth:
                        return False
            
            # Fallback to base connector authentication
            if self.enable_fallback_auth:
                self.logger.logger.info("Attempting fallback authentication...")
                
                if super().connect():
                    self.oauth_authenticated = False
                    self.authentication_method = "client_credentials_fallback"
                    
                    self.logger.log_event(
                        event_type=EventType.AUTHENTICATION_SUCCESS,
                        source_system=self.config.environment_name,
                        operation="enhanced_connect",
                        status="fallback_success",
                        details={'method': 'client_credentials'}
                    )
                    
                    self.logger.logger.info("Fallback authentication successful")
                    return True
                else:
                    self.logger.logger.error("Fallback authentication failed")
            
            # All authentication methods failed
            self.logger.log_event(
                event_type=EventType.AUTHENTICATION_FAILURE,
                source_system=self.config.environment_name,
                operation="enhanced_connect",
                status="all_methods_failed",
                details={}
            )
            
            return False
            
        except Exception as e:
            self.logger.log_event(
                event_type=EventType.AUTHENTICATION_FAILURE,
                source_system=self.config.environment_name,
                operation="enhanced_connect",
                status="error",
                details={},
                error_message=str(e)
            )
            
            self.logger.logger.error(f"Enhanced connection failed: {str(e)}")
            return False
    
    def _initialize_services_with_oauth(self):
        """Initialize dataset discovery and other services with OAuth session"""
        try:
            # Initialize dataset discovery service with OAuth session
            if self.auth_service and self.oauth_authenticated:
                from dataset_discovery_service import create_dataset_discovery_service
                
                oauth_session = self.auth_service.get_authenticated_session()
                
                self.dataset_discovery_service = create_dataset_discovery_service(
                    base_url=self.config.base_url,
                    session=oauth_session,
                    environment_name=f"{self.config.environment_name}_oauth",
                    s3_bucket_name=f"datasphere-metadata-lake-{self.config.environment_name}"
                )
                
                if self.dataset_discovery_service.connect():
                    self.logger.logger.info("Dataset discovery service initialized with OAuth session")
                else:
                    self.logger.logger.warning("Dataset discovery service initialization failed with OAuth")
            
        except Exception as e:
            self.logger.logger.warning(f"Failed to initialize services with OAuth: {str(e)}")
    
    def _test_enhanced_api_access(self):
        """Test enhanced API access with OAuth authentication"""
        try:
            if self.auth_service:
                self.auth_test_results = self.auth_service.test_full_metadata_api_access()
                self.last_auth_test = datetime.now()
                
                if self.auth_test_results.get('overall_success'):
                    self.logger.logger.info("✅ Enhanced API access test successful - full metadata API access confirmed")
                else:
                    self.logger.logger.warning("⚠️ Enhanced API access test shows limited access")
            
        except Exception as e:
            self.logger.logger.error(f"Enhanced API access test failed: {str(e)}")
    
    def get_enhanced_connection_info(self) -> Dict[str, Any]:
        """
        Get enhanced connection information including OAuth status
        
        Returns:
            Dict[str, Any]: Comprehensive connection information
        """
        base_info = {
            'connected': self.is_connected,
            'environment': self.config.environment_name,
            'base_url': self.config.base_url,
            'oauth_enabled': self.enable_oauth,
            'fallback_enabled': self.enable_fallback_auth
        }
        
        # Add OAuth-specific information
        if self.auth_service:
            auth_status = self.auth_service.get_authentication_status()
            base_info.update({
                'oauth_authenticated': self.oauth_authenticated,
                'authentication_method': self.authentication_method,
                'oauth_status': auth_status
            })
        
        # Add authentication result details
        if self.authentication_result:
            base_info.update({
                'auth_result': self.authentication_result.to_dict()
            })
        
        # Add API test results
        if self.auth_test_results:
            base_info.update({
                'api_test_results': self.auth_test_results,
                'last_api_test': self.last_auth_test.isoformat() if self.last_auth_test else None
            })
        
        return base_info
    
    def refresh_authentication(self) -> bool:
        """
        Refresh authentication tokens and validate access
        
        Returns:
            bool: True if refresh successful, False otherwise
        """
        try:
            if self.oauth_authenticated and self.auth_service:
                # Try to refresh OAuth authentication
                auth_result = self.auth_service.authenticate(force_reauth=False)
                
                if auth_result.success:
                    self.session = self.auth_service.get_authenticated_session()
                    self.authentication_result = auth_result
                    
                    # Re-test API access
                    self._test_enhanced_api_access()
                    
                    self.logger.logger.info("OAuth authentication refreshed successfully")
                    return True
                else:
                    self.logger.logger.warning(f"OAuth refresh failed: {auth_result.error_message}")
                    
                    # Try fallback authentication
                    if self.enable_fallback_auth:
                        return self._refresh_token_if_needed()
            
            elif self.is_connected:
                # Use base connector refresh
                return self._refresh_token_if_needed()
            
            return False
            
        except Exception as e:
            self.logger.logger.error(f"Authentication refresh failed: {str(e)}")
            return False
    
    def get_assets(self, asset_type: AssetType = None) -> List[MetadataAsset]:
        """
        Enhanced asset discovery with OAuth authentication
        
        This method uses the same interface as the base connector but leverages
        OAuth authentication for enhanced access to metadata APIs.
        
        Args:
            asset_type: Type of assets to retrieve (optional)
            
        Returns:
            List[MetadataAsset]: List of discovered metadata assets
        """
        if not self.is_connected:
            self.logger.logger.error("Not connected - call connect() first")
            return []
        
        # Ensure authentication is still valid
        if not self.refresh_authentication():
            self.logger.logger.error("Authentication refresh failed")
            return []
        
        try:
            # Use base connector's asset discovery with enhanced authentication
            assets = super().get_assets(asset_type)
            
            # Add OAuth-specific metadata to assets
            if self.oauth_authenticated:
                for asset in assets:
                    asset.custom_properties.update({
                        'oauth_authenticated': True,
                        'authentication_method': self.authentication_method,
                        'enhanced_access': True,
                        'api_test_passed': self.auth_test_results.get('overall_success', False) if self.auth_test_results else False
                    })
            
            self.logger.log_event(
                event_type=EventType.SYNC_COMPLETED,
                source_system=self.config.environment_name,
                operation="enhanced_get_assets",
                status="completed",
                details={
                    'total_assets': len(assets),
                    'oauth_authenticated': self.oauth_authenticated,
                    'authentication_method': self.authentication_method,
                    'asset_types': list(set([asset.asset_type.value for asset in assets]))
                }
            )
            
            return assets
            
        except Exception as e:
            self.logger.log_event(
                event_type=EventType.ERROR_OCCURRED,
                source_system=self.config.environment_name,
                operation="enhanced_get_assets",
                status="failed",
                details={'oauth_authenticated': self.oauth_authenticated},
                error_message=str(e)
            )
            
            self.logger.logger.error(f"Enhanced asset discovery failed: {str(e)}")
            return []
    
    def test_metadata_api_access(self) -> Dict[str, Any]:
        """
        Test metadata API access and return comprehensive results
        
        Returns:
            Dict[str, Any]: Detailed test results
        """
        if not self.is_connected:
            return {
                'success': False,
                'error': 'Not connected - call connect() first'
            }
        
        try:
            if self.auth_service and self.oauth_authenticated:
                # Use OAuth service for comprehensive testing
                return self.auth_service.test_full_metadata_api_access()
            else:
                # Use basic testing for fallback authentication
                return self._test_basic_api_access()
                
        except Exception as e:
            return {
                'success': False,
                'error': f'API access test failed: {str(e)}'
            }
    
    def _test_basic_api_access(self) -> Dict[str, Any]:
        """Basic API access test for fallback authentication"""
        test_results = {
            'timestamp': datetime.now().isoformat(),
            'authentication_method': self.authentication_method,
            'oauth_authenticated': False,
            'endpoints_tested': 0,
            'endpoints_accessible': 0,
            'overall_success': False
        }
        
        # Test a few basic endpoints
        test_endpoints = [
            '/api/v1/datasphere/consumption/analytical',
            '/api/v1/datasphere/consumption'
        ]
        
        for endpoint in test_endpoints:
            try:
                url = f"{self.config.base_url.rstrip('/')}{endpoint}"
                response = self.session.get(url, timeout=30)
                
                test_results['endpoints_tested'] += 1
                
                if response.status_code in [200, 404]:  # 404 is OK for discovery
                    test_results['endpoints_accessible'] += 1
                    
            except Exception:
                continue
        
        test_results['overall_success'] = test_results['endpoints_accessible'] > 0
        return test_results
    
    def disconnect(self) -> bool:
        """Enhanced disconnect with OAuth cleanup"""
        try:
            # Logout from OAuth service
            if self.auth_service:
                self.auth_service.logout()
            
            # Clear OAuth state
            self.oauth_authenticated = False
            self.authentication_method = None
            self.authentication_result = None
            self.auth_test_results = None
            self.last_auth_test = None
            
            # Call base disconnect
            return super().disconnect()
            
        except Exception as e:
            self.logger.logger.error(f"Enhanced disconnect failed: {str(e)}")
            return False

def create_enhanced_datasphere_connector(
    base_url: str = "https://ailien-test.eu20.hcs.cloud.sap",
    client_id: str = None,
    client_secret: str = None,
    environment_name: str = "enhanced",
    oauth_redirect_uri: str = "http://localhost:8080/callback",
    enable_oauth: bool = True,
    enable_fallback_auth: bool = True
) -> EnhancedDatasphereConnector:
    """
    Factory function to create enhanced Datasphere connector
    
    Args:
        base_url: SAP Datasphere base URL
        client_id: OAuth client ID (uses default if not provided)
        client_secret: OAuth client secret (uses default if not provided)
        environment_name: Environment identifier
        oauth_redirect_uri: OAuth redirect URI
        enable_oauth: Enable OAuth Authorization Code Flow
        enable_fallback_auth: Enable fallback authentication methods
        
    Returns:
        EnhancedDatasphereConnector: Configured enhanced connector
    """
    # Use default credentials if not provided
    if not client_id:
        client_id = "sb-60cb266e-ad9d-49f7-9967-b53b8286a259!b130936|client!b3944"
    
    if not client_secret:
        client_secret = "caaea1b9-b09b-4d28-83fe-09966d525243$LOFW4h5LpLvB3Z2FE0P7FiH4-C7qexeQPi22DBiHbz8="
    
    # Create configuration
    config = DatasphereConfig(
        base_url=base_url,
        client_id=client_id,
        client_secret=client_secret,
        token_url=f"https://ailien-test.authentication.eu20.hana.ondemand.com/oauth/token",
        environment_name=environment_name
    )
    
    return EnhancedDatasphereConnector(
        config=config,
        oauth_redirect_uri=oauth_redirect_uri,
        enable_oauth=enable_oauth,
        enable_fallback_auth=enable_fallback_auth
    )

if __name__ == "__main__":
    # Example usage and testing
    print("🚀 Enhanced Datasphere Connector with OAuth Authorization Code Flow")
    print("=" * 70)
    
    # Create enhanced connector
    connector = create_enhanced_datasphere_connector(
        environment_name="test-enhanced",
        enable_oauth=True,
        enable_fallback_auth=True
    )
    
    # Test connection
    print("\n🔐 Testing Enhanced Connection...")
    if connector.connect():
        print("✅ Connection successful!")
        
        # Get connection info
        conn_info = connector.get_enhanced_connection_info()
        print(f"\n📋 Connection Information:")
        print(f"   OAuth Authenticated: {'✅' if conn_info.get('oauth_authenticated') else '❌'}")
        print(f"   Authentication Method: {conn_info.get('authentication_method')}")
        print(f"   API Test Passed: {'✅' if conn_info.get('api_test_results', {}).get('overall_success') else '❌'}")
        
        # Test metadata API access
        print(f"\n🧪 Testing Metadata API Access...")
        test_results = connector.test_metadata_api_access()
        
        if test_results.get('overall_success'):
            print(f"🎉 SUCCESS: Full metadata API access achieved!")
            print(f"   HTTP 200 Responses: {test_results.get('http_200_count', 0)}")
            print(f"   HTTP 403 Responses: {test_results.get('http_403_count', 0)}")
            print(f"   Metadata Endpoints: {test_results.get('metadata_endpoints_accessible', 0)}")
        else:
            print(f"⚠️ Limited access - some endpoints may need additional permissions")
        
        # Test asset discovery
        print(f"\n📊 Testing Asset Discovery...")
        assets = connector.get_assets()
        
        print(f"   Total Assets Discovered: {len(assets)}")
        
        if assets:
            oauth_assets = [a for a in assets if a.custom_properties.get('oauth_authenticated')]
            print(f"   OAuth-Enhanced Assets: {len(oauth_assets)}")
            
            asset_types = list(set([asset.asset_type.value for asset in assets]))
            print(f"   Asset Types: {asset_types}")
        
        # Disconnect
        connector.disconnect()
        print(f"\n✅ Enhanced connector test completed successfully!")
        
    else:
        print("❌ Connection failed")
        
        # Get connection info even on failure
        conn_info = connector.get_enhanced_connection_info()
        if 'auth_result' in conn_info:
            print(f"   Error: {conn_info['auth_result'].get('error_message')}")