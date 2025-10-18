#!/usr/bin/env python3
"""
AWS Glue Data Catalog Connector with IAM Authentication
Implements MetadataConnector interface for AWS Glue with comprehensive IAM integration
"""

import boto3
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError
from botocore.config import Config
import threading

from metadata_sync_core import (
    MetadataConnector, MetadataAsset, AssetType, SourceSystem, 
    BusinessContext, LineageRelationship
)
from sync_logging import SyncLogger, EventType

@dataclass
class GlueConfig:
    """Configuration for AWS Glue connection"""
    region: str = "us-east-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_session_token: Optional[str] = None
    aws_profile: Optional[str] = None
    role_arn: Optional[str] = None
    external_id: Optional[str] = None
    max_retries: int = 3
    retry_delay: int = 2
    timeout: int = 30
    environment_name: str = "glue"

@dataclass
class GlueTableInfo:
    """Information about a Glue table"""
    database_name: str
    table_name: str
    table_type: str
    storage_descriptor: Dict[str, Any]
    parameters: Dict[str, Any]
    partition_keys: List[Dict[str, Any]]
    creation_time: datetime
    update_time: datetime
    owner: Optional[str] = None
    retention: Optional[int] = None

class GlueConnector(MetadataConnector):
    """AWS Glue Data Catalog connector with IAM authentication"""
    
    def __init__(self, config: GlueConfig):
        self.config = config
        self.logger = SyncLogger(f"glue_connector_{config.environment_name}")
        self.glue_client: Optional[boto3.client] = None
        self.sts_client: Optional[boto3.client] = None
        self.is_connected = False
        self.connection_lock = threading.Lock()
        
        # AWS Glue to standard type mappings
        self.glue_to_standard_types = {
            'string': 'string',
            'varchar': 'string',
            'char': 'string',
            'int': 'int',
            'integer': 'int',
            'bigint': 'bigint',
            'smallint': 'int',
            'tinyint': 'int',
            'double': 'double',
            'float': 'float',
            'decimal': 'decimal',
            'boolean': 'boolean',
            'date': 'date',
            'timestamp': 'timestamp',
            'binary': 'binary',
            'array': 'array',
            'map': 'map',
            'struct': 'struct'
        }
        
        # Standard to Glue type mappings (reverse)
        self.standard_to_glue_types = {v: k for k, v in self.glue_to_standard_types.items()}
        self.standard_to_glue_types.update({
            'string': 'string',
            'text': 'string',
            'varchar': 'string'
        })
    
    def connect(self) -> bool:
        """Establish connection to AWS Glue with IAM authentication"""
        with self.connection_lock:
            try:
                self.logger.log_event(
                    event_type=EventType.AUTHENTICATION_SUCCESS,
                    source_system=self.config.environment_name,
                    operation="connect",
                    status="attempting",
                    details={'region': self.config.region}
                )
                
                # Configure boto3 session
                session = self._create_boto3_session()
                if not session:
                    return False
                
                # Create Glue client with retry configuration
                retry_config = Config(
                    region_name=self.config.region,
                    retries={
                        'max_attempts': self.config.max_retries,
                        'mode': 'adaptive'
                    },
                    max_pool_connections=50
                )
                
                self.glue_client = session.client('glue', config=retry_config)
                self.sts_client = session.client('sts', config=retry_config)
                
                # Test connection
                if not self._test_connection():
                    return False
                
                self.is_connected = True
                
                # Get caller identity for logging
                try:
                    identity = self.sts_client.get_caller_identity()
                    caller_info = {
                        'account': identity.get('Account'),
                        'user_id': identity.get('UserId'),
                        'arn': identity.get('Arn')
                    }
                except Exception as e:
                    caller_info = {'error': str(e)}
                
                self.logger.log_event(
                    event_type=EventType.AUTHENTICATION_SUCCESS,
                    source_system=self.config.environment_name,
                    operation="connect",
                    status="connected",
                    details={
                        'region': self.config.region,
                        'caller_identity': caller_info
                    }
                )
                
                return True
                
            except Exception as e:
                self.logger.log_event(
                    event_type=EventType.AUTHENTICATION_FAILURE,
                    source_system=self.config.environment_name,
                    operation="connect",
                    status="failed",
                    details={'region': self.config.region},
                    error_message=str(e)
                )
                
                self.logger.create_error_report(
                    error_type="connection_failed",
                    error_message=str(e),
                    context={
                        'operation': 'connect',
                        'region': self.config.region,
                        'environment': self.config.environment_name
                    },
                    affected_assets=[],
                    severity="HIGH"
                )
                
                return False
    
    def disconnect(self) -> bool:
        """Disconnect from AWS Glue"""
        try:
            self.is_connected = False
            self.glue_client = None
            self.sts_client = None
            
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
    
    def _create_boto3_session(self) -> Optional[boto3.Session]:
        """Create boto3 session with appropriate credentials"""
        try:
            session_kwargs = {}
            
            # Use explicit credentials if provided
            if self.config.aws_access_key_id and self.config.aws_secret_access_key:
                session_kwargs.update({
                    'aws_access_key_id': self.config.aws_access_key_id,
                    'aws_secret_access_key': self.config.aws_secret_access_key
                })
                if self.config.aws_session_token:
                    session_kwargs['aws_session_token'] = self.config.aws_session_token
            
            # Use profile if specified
            elif self.config.aws_profile:
                session_kwargs['profile_name'] = self.config.aws_profile
            
            # Create session
            session = boto3.Session(**session_kwargs)
            
            # Handle role assumption if specified
            if self.config.role_arn:
                session = self._assume_role(session)
            
            return session
            
        except (NoCredentialsError, PartialCredentialsError) as e:
            self.logger.logger.error(f"AWS credentials error: {str(e)}")
            return None
        except Exception as e:
            self.logger.logger.error(f"Session creation error: {str(e)}")
            return None
    
    def _assume_role(self, session: boto3.Session) -> Optional[boto3.Session]:
        """Assume IAM role if specified"""
        try:
            sts_client = session.client('sts')
            
            assume_role_kwargs = {
                'RoleArn': self.config.role_arn,
                'RoleSessionName': f'metadata-sync-{int(time.time())}'
            }
            
            if self.config.external_id:
                assume_role_kwargs['ExternalId'] = self.config.external_id
            
            response = sts_client.assume_role(**assume_role_kwargs)
            credentials = response['Credentials']
            
            # Create new session with assumed role credentials
            return boto3.Session(
                aws_access_key_id=credentials['AccessKeyId'],
                aws_secret_access_key=credentials['SecretAccessKey'],
                aws_session_token=credentials['SessionToken']
            )
            
        except Exception as e:
            self.logger.logger.error(f"Role assumption failed: {str(e)}")
            return None
    
    def _test_connection(self) -> bool:
        """Test the connection by making a simple API call"""
        try:
            # Try to list databases (minimal permissions required)
            response = self.glue_client.get_databases(MaxResults=1)
            
            self.logger.logger.info("Connection test successful - can access Glue Data Catalog")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code in ['AccessDenied', 'UnauthorizedOperation']:
                self.logger.logger.error(f"Access denied to Glue Data Catalog: {str(e)}")
            elif error_code == 'InvalidUserID.NotFound':
                self.logger.logger.error(f"Invalid AWS credentials: {str(e)}")
            else:
                self.logger.logger.error(f"Glue API error: {str(e)}")
            
            return False
            
        except Exception as e:
            self.logger.logger.error(f"Connection test failed: {str(e)}")
            return False
    
    def get_assets(self, asset_type: AssetType = None) -> List[MetadataAsset]:
        """Retrieve metadata assets from AWS Glue Data Catalog"""
        if not self.is_connected:
            self.logger.logger.error("Not connected to AWS Glue")
            return []
        
        assets = []
        
        try:
            # Get databases (spaces)
            if asset_type is None or asset_type == AssetType.SPACE:
                databases = self._get_databases()
                assets.extend(databases)
            
            # Get tables
            if asset_type is None or asset_type in [AssetType.TABLE, AssetType.VIEW, AssetType.ANALYTICAL_MODEL]:
                tables = self._get_tables(asset_type)
                assets.extend(tables)
            
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
    
    def _get_databases(self) -> List[MetadataAsset]:
        """Get all databases from Glue Data Catalog"""
        databases = []
        
        try:
            paginator = self.glue_client.get_paginator('get_databases')
            
            for page in paginator.paginate():
                for db in page['DatabaseList']:
                    asset = MetadataAsset(
                        asset_id=f"{self.config.environment_name}_db_{db['Name']}",
                        asset_type=AssetType.SPACE,
                        source_system=SourceSystem.GLUE,
                        technical_name=db['Name'],
                        business_name=db.get('Description', db['Name']),
                        description=db.get('Description', f"AWS Glue database: {db['Name']}"),
                        owner=db.get('Parameters', {}).get('owner', 'glue'),
                        created_date=db.get('CreateTime', datetime.now()),
                        business_context=BusinessContext(
                            business_name=db.get('Description', db['Name']),
                            description=db.get('Description', f"AWS Glue database containing tables and metadata"),
                            tags=['database', 'glue', 'aws']
                        ),
                        custom_properties={
                            'glue_database': db['Name'],
                            'glue_environment': self.config.environment_name,
                            'location_uri': db.get('LocationUri'),
                            'parameters': db.get('Parameters', {}),
                            'catalog_id': db.get('CatalogId')
                        }
                    )
                    databases.append(asset)
            
            self.logger.logger.info(f"Retrieved {len(databases)} databases from Glue")
            
        except Exception as e:
            self.logger.logger.error(f"Error retrieving databases: {str(e)}")
        
        return databases
    
    def _get_tables(self, asset_type: Optional[AssetType] = None) -> List[MetadataAsset]:
        """Get all tables from Glue Data Catalog"""
        tables = []
        
        try:
            # First get all databases
            db_paginator = self.glue_client.get_paginator('get_databases')
            
            for db_page in db_paginator.paginate():
                for db in db_page['DatabaseList']:
                    database_name = db['Name']
                    
                    # Get tables for this database
                    table_paginator = self.glue_client.get_paginator('get_tables')
                    
                    for table_page in table_paginator.paginate(DatabaseName=database_name):
                        for table in table_page['TableList']:
                            asset = self._create_table_asset(database_name, table)
                            if asset and (asset_type is None or asset.asset_type == asset_type):
                                tables.append(asset)
            
            self.logger.logger.info(f"Retrieved {len(tables)} tables from Glue")
            
        except Exception as e:
            self.logger.logger.error(f"Error retrieving tables: {str(e)}")
        
        return tables
    
    def _create_table_asset(self, database_name: str, table: Dict[str, Any]) -> Optional[MetadataAsset]:
        """Create a MetadataAsset from a Glue table"""
        try:
            table_name = table['Name']
            
            # Determine asset type based on table properties
            asset_type = self._determine_asset_type(table)
            
            # Extract columns
            columns = self._extract_table_columns(table)
            
            # Extract business context
            business_context = self._extract_table_business_context(table)
            
            # Create asset
            asset = MetadataAsset(
                asset_id=f"{self.config.environment_name}_{database_name}_{table_name}",
                asset_type=asset_type,
                source_system=SourceSystem.GLUE,
                technical_name=table_name,
                business_name=business_context.business_name or table_name,
                description=business_context.description or table.get('Description', f"Table from {database_name}"),
                owner=table.get('Owner', business_context.owner or 'glue'),
                created_date=table.get('CreateTime', datetime.now()),
                modified_date=table.get('UpdateTime', datetime.now()),
                business_context=business_context,
                schema_info={
                    'columns': columns,
                    'database_name': database_name,
                    'table_type': table.get('TableType', 'EXTERNAL_TABLE'),
                    'storage_descriptor': table.get('StorageDescriptor', {}),
                    'partition_keys': table.get('PartitionKeys', [])
                },
                custom_properties={
                    'glue_database': database_name,
                    'glue_table': table_name,
                    'glue_environment': self.config.environment_name,
                    'table_type': table.get('TableType'),
                    'parameters': table.get('Parameters', {}),
                    'retention': table.get('Retention'),
                    'catalog_id': table.get('CatalogId'),
                    'view_original_text': table.get('ViewOriginalText'),
                    'view_expanded_text': table.get('ViewExpandedText')
                }
            )
            
            return asset
            
        except Exception as e:
            self.logger.logger.error(f"Error creating table asset for {database_name}.{table.get('Name', 'unknown')}: {str(e)}")
            return None
    
    def _determine_asset_type(self, table: Dict[str, Any]) -> AssetType:
        """Determine asset type based on table properties"""
        table_type = table.get('TableType', '').upper()
        parameters = table.get('Parameters', {})
        
        # Check for Datasphere-sourced analytical models
        if parameters.get('datasphere_type') == 'analytical_model':
            return AssetType.ANALYTICAL_MODEL
        
        # Check for views
        if 'VIEW' in table_type or table.get('ViewOriginalText'):
            return AssetType.VIEW
        
        # Check for analytical model indicators
        if any(key in parameters for key in ['dimensions', 'measures', 'analytical_model']):
            return AssetType.ANALYTICAL_MODEL
        
        # Default to table
        return AssetType.TABLE
    
    def _extract_table_columns(self, table: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract column information from Glue table"""
        columns = []
        
        try:
            storage_descriptor = table.get('StorageDescriptor', {})
            glue_columns = storage_descriptor.get('Columns', [])
            
            for col in glue_columns:
                column = {
                    'name': col.get('Name', ''),
                    'type': col.get('Type', 'string'),
                    'comment': col.get('Comment', ''),
                    'nullable': True  # Glue doesn't track nullability explicitly
                }
                columns.append(column)
            
            # Add partition keys as columns
            partition_keys = table.get('PartitionKeys', [])
            for pk in partition_keys:
                column = {
                    'name': pk.get('Name', ''),
                    'type': pk.get('Type', 'string'),
                    'comment': pk.get('Comment', ''),
                    'nullable': True,
                    'is_partition_key': True
                }
                columns.append(column)
            
        except Exception as e:
            self.logger.logger.warning(f"Error extracting columns: {str(e)}")
        
        return columns
    
    def _extract_table_business_context(self, table: Dict[str, Any]) -> BusinessContext:
        """Extract business context from Glue table"""
        parameters = table.get('Parameters', {})
        
        # Extract Datasphere business context if available
        dimensions = []
        measures = []
        hierarchies = []
        
        if 'datasphere_source' in parameters:
            # This table was synced from Datasphere
            dimensions = parameters.get('dimensions', '').split(',') if parameters.get('dimensions') else []
            measures = parameters.get('measures', '').split(',') if parameters.get('measures') else []
            hierarchies = parameters.get('hierarchies', '').split(',') if parameters.get('hierarchies') else []
        
        return BusinessContext(
            business_name=parameters.get('business_name', table.get('Description', table['Name'])),
            description=table.get('Description', parameters.get('description', f"Table from AWS Glue")),
            owner=table.get('Owner', parameters.get('owner', 'glue')),
            steward=parameters.get('steward'),
            certification_status=parameters.get('certification_status'),
            tags=self._extract_tags(parameters),
            dimensions=dimensions,
            measures=measures,
            hierarchies=hierarchies
        )
    
    def _extract_tags(self, parameters: Dict[str, Any]) -> List[str]:
        """Extract tags from table parameters"""
        tags = ['glue', 'aws']
        
        # Add Datasphere tags if present
        if 'datasphere_source' in parameters:
            tags.extend(['datasphere', 'synced'])
            if parameters.get('datasphere_space'):
                tags.append(parameters['datasphere_space'].lower())
        
        # Add table type tags
        if 'table_type' in parameters:
            tags.append(parameters['table_type'].lower())
        
        return tags
    
    def create_asset(self, asset: MetadataAsset) -> bool:
        """Create a new metadata asset in AWS Glue"""
        if not self.is_connected:
            self.logger.logger.error("Not connected to AWS Glue")
            return False
        
        try:
            if asset.asset_type == AssetType.SPACE:
                return self._create_database(asset)
            elif asset.asset_type in [AssetType.TABLE, AssetType.VIEW, AssetType.ANALYTICAL_MODEL]:
                return self._create_table(asset)
            else:
                self.logger.logger.warning(f"Unsupported asset type for creation: {asset.asset_type}")
                return False
                
        except Exception as e:
            self.logger.log_asset_operation(
                operation="create",
                asset_id=asset.asset_id,
                asset_type=asset.asset_type.value,
                source_system=asset.source_system.value,
                target_system=self.config.environment_name,
                status="failed",
                details={},
                error_message=str(e)
            )
            return False
    
    def _create_database(self, asset: MetadataAsset) -> bool:
        """Create a database in AWS Glue"""
        try:
            database_input = {
                'Name': asset.technical_name,
                'Description': asset.description or f"Database created from {asset.source_system.value}",
                'Parameters': {
                    'source_system': asset.source_system.value,
                    'asset_id': asset.asset_id,
                    'created_by': 'metadata_sync_engine',
                    'creation_timestamp': datetime.now().isoformat()
                }
            }
            
            # Add custom properties
            if asset.custom_properties:
                database_input['Parameters'].update({
                    k: str(v) for k, v in asset.custom_properties.items()
                })
            
            # Check if database exists
            try:
                self.glue_client.get_database(Name=asset.technical_name)
                # Database exists, update it
                self.glue_client.update_database(
                    Name=asset.technical_name,
                    DatabaseInput=database_input
                )
                operation = "update"
            except ClientError as e:
                if e.response['Error']['Code'] == 'EntityNotFoundException':
                    # Database doesn't exist, create it
                    self.glue_client.create_database(DatabaseInput=database_input)
                    operation = "create"
                else:
                    raise
            
            self.logger.log_asset_operation(
                operation=operation,
                asset_id=asset.asset_id,
                asset_type=asset.asset_type.value,
                source_system=asset.source_system.value,
                target_system=self.config.environment_name,
                status="completed",
                details={
                    'database_name': asset.technical_name,
                    'operation': operation
                }
            )
            
            return True
            
        except Exception as e:
            self.logger.logger.error(f"Failed to create database {asset.technical_name}: {str(e)}")
            return False
    
    def _create_table(self, asset: MetadataAsset) -> bool:
        """Create a table in AWS Glue"""
        try:
            # Extract database name from schema info or custom properties
            database_name = (
                asset.schema_info.get('database_name') or
                asset.custom_properties.get('glue_database') or
                asset.custom_properties.get('datasphere_space', 'default')
            )
            
            # Ensure database exists
            self._ensure_database_exists(database_name, asset.source_system.value)
            
            # Prepare columns
            columns = []
            partition_keys = []
            
            if 'columns' in asset.schema_info:
                for col in asset.schema_info['columns']:
                    column_def = {
                        'Name': col['name'],
                        'Type': self._convert_to_glue_type(col.get('type', 'string')),
                        'Comment': col.get('description', col.get('comment', ''))
                    }
                    
                    if col.get('is_partition_key'):
                        partition_keys.append(column_def)
                    else:
                        columns.append(column_def)
            
            # Prepare table input
            table_input = {
                'Name': asset.technical_name,
                'Description': asset.description,
                'Owner': asset.owner,
                'StorageDescriptor': {
                    'Columns': columns,
                    'Location': asset.custom_properties.get('location', ''),
                    'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
                    'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
                    'SerdeInfo': {
                        'SerializationLibrary': 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
                    }
                },
                'PartitionKeys': partition_keys,
                'TableType': 'EXTERNAL_TABLE',
                'Parameters': {
                    'source_system': asset.source_system.value,
                    'asset_id': asset.asset_id,
                    'created_by': 'metadata_sync_engine',
                    'creation_timestamp': datetime.now().isoformat()
                }
            }
            
            # Add business context to parameters
            if asset.business_context:
                if asset.business_context.business_name:
                    table_input['Parameters']['business_name'] = asset.business_context.business_name
                if asset.business_context.steward:
                    table_input['Parameters']['steward'] = asset.business_context.steward
                if asset.business_context.certification_status:
                    table_input['Parameters']['certification_status'] = asset.business_context.certification_status
                if asset.business_context.dimensions:
                    table_input['Parameters']['dimensions'] = ','.join(asset.business_context.dimensions)
                if asset.business_context.measures:
                    table_input['Parameters']['measures'] = ','.join(asset.business_context.measures)
                if asset.business_context.hierarchies:
                    table_input['Parameters']['hierarchies'] = ','.join(asset.business_context.hierarchies)
            
            # Add custom properties
            if asset.custom_properties:
                table_input['Parameters'].update({
                    k: str(v) for k, v in asset.custom_properties.items()
                })
            
            # Check if table exists
            try:
                self.glue_client.get_table(DatabaseName=database_name, Name=asset.technical_name)
                # Table exists, update it
                self.glue_client.update_table(
                    DatabaseName=database_name,
                    TableInput=table_input
                )
                operation = "update"
            except ClientError as e:
                if e.response['Error']['Code'] == 'EntityNotFoundException':
                    # Table doesn't exist, create it
                    self.glue_client.create_table(
                        DatabaseName=database_name,
                        TableInput=table_input
                    )
                    operation = "create"
                else:
                    raise
            
            self.logger.log_asset_operation(
                operation=operation,
                asset_id=asset.asset_id,
                asset_type=asset.asset_type.value,
                source_system=asset.source_system.value,
                target_system=self.config.environment_name,
                status="completed",
                details={
                    'database_name': database_name,
                    'table_name': asset.technical_name,
                    'columns_count': len(columns),
                    'partition_keys_count': len(partition_keys),
                    'operation': operation
                }
            )
            
            return True
            
        except Exception as e:
            self.logger.logger.error(f"Failed to create table {asset.technical_name}: {str(e)}")
            return False
    
    def _ensure_database_exists(self, database_name: str, source_system: str):
        """Ensure a database exists in Glue, create if not"""
        try:
            self.glue_client.get_database(Name=database_name)
        except ClientError as e:
            if e.response['Error']['Code'] == 'EntityNotFoundException':
                # Create database
                database_input = {
                    'Name': database_name,
                    'Description': f'Database for {source_system} metadata synchronization',
                    'Parameters': {
                        'source_system': source_system,
                        'created_by': 'metadata_sync_engine',
                        'creation_timestamp': datetime.now().isoformat()
                    }
                }
                self.glue_client.create_database(DatabaseInput=database_input)
                self.logger.logger.info(f"Created database: {database_name}")
            else:
                raise
    
    def _convert_to_glue_type(self, data_type: str) -> str:
        """Convert standard data type to Glue type"""
        # Clean up the type string
        clean_type = data_type.lower().strip()
        
        # Handle decimal with precision/scale
        if clean_type.startswith('decimal'):
            return clean_type
        
        # Map to Glue type
        return self.standard_to_glue_types.get(clean_type, 'string')
    
    def update_asset(self, asset: MetadataAsset) -> bool:
        """Update an existing metadata asset"""
        # For Glue, update is the same as create (upsert behavior)
        return self.create_asset(asset)
    
    def delete_asset(self, asset_id: str) -> bool:
        """Delete a metadata asset from AWS Glue"""
        self.logger.logger.warning("Delete asset operation not implemented for safety")
        return False
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get current connection status"""
        status = {
            'is_connected': self.is_connected,
            'environment': self.config.environment_name,
            'region': self.config.region,
            'last_connection_test': datetime.now().isoformat()
        }
        
        if self.is_connected and self.sts_client:
            try:
                identity = self.sts_client.get_caller_identity()
                status.update({
                    'account': identity.get('Account'),
                    'user_id': identity.get('UserId'),
                    'arn': identity.get('Arn')
                })
            except Exception as e:
                status['identity_error'] = str(e)
        
        return status

# Factory function for creating connectors
def create_glue_connector(region: str = "us-east-1", environment: str = "default") -> GlueConnector:
    """Create a Glue connector for the specified region and environment"""
    
    config = GlueConfig(
        region=region,
        environment_name=environment
    )
    
    return GlueConnector(config)

# Example usage and testing
if __name__ == "__main__":
    print("🔗 AWS Glue Connector Test")
    print("=" * 27)
    
    try:
        # Create connector
        connector = create_glue_connector("us-east-1", "test")
        
        print(f"Testing connection to AWS Glue in {connector.config.region}...")
        
        # Test connection
        if connector.connect():
            print("✅ Connection successful!")
            
            # Get connection status
            status = connector.get_connection_status()
            print(f"📊 Connection Status:")
            for key, value in status.items():
                print(f"  {key}: {value}")
            
            # Get assets
            print("\n🔍 Discovering assets...")
            assets = connector.get_assets()
            
            print(f"📊 Discovery Results:")
            print(f"  Total assets: {len(assets)}")
            
            asset_types = {}
            for asset in assets:
                asset_type = asset.asset_type.value
                asset_types[asset_type] = asset_types.get(asset_type, 0) + 1
            
            for asset_type, count in asset_types.items():
                print(f"  • {asset_type}: {count}")
            
            # Show sample assets
            if assets:
                print(f"\n📋 Sample Assets:")
                for asset in assets[:3]:  # Show first 3
                    print(f"  • {asset.asset_type.value}: {asset.technical_name}")
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
    
    print(f"\n🎉 AWS Glue connector test completed!")