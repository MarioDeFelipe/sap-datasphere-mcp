#!/usr/bin/env python3
"""
Enhanced SAP Datasphere Metadata Extraction Tool
Combines real API integration with AWS Glue catalog replication
"""

import json
import logging
import requests
import boto3
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import base64
import re
from dataclasses import dataclass
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("enhanced-metadata-extractor")

@dataclass
class DatasphereTable:
    """Represents a table/view from Datasphere"""
    name: str
    space: str
    description: str
    columns: List[Dict[str, Any]]
    table_type: str  # 'table', 'view', 'analytical_model'
    source_url: str
    metadata_url: str
    odata_context: str
    last_updated: datetime

@dataclass
class ExtractionResult:
    """Results of metadata extraction"""
    success: bool
    tables_discovered: int
    tables_replicated: int
    errors: List[str]
    warnings: List[str]
    execution_time: float

class EnhancedDatasphereClient:
    """Enhanced client for SAP Datasphere with real API integration"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session = requests.Session()
        self.access_token = None
        self.token_expires_at = None
        self.setup_authentication()
    
    def setup_authentication(self):
        """Setup OAuth2 authentication with real credentials"""
        try:
            oauth_config = self.config["oauth"]
            
            # Prepare OAuth request
            token_url = oauth_config["token_url"]
            client_id = oauth_config["client_id"]
            client_secret = oauth_config["client_secret"]
            
            auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
            
            headers = {
                'Authorization': f'Basic {auth_header}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {'grant_type': 'client_credentials'}
            
            response = requests.post(token_url, headers=headers, data=data, timeout=30)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                expires_in = token_data.get('expires_in', 3600)
                self.token_expires_at = datetime.now().timestamp() + expires_in
                
                # Update session headers
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}',
                    'Accept': 'application/json',
                    'User-Agent': 'Enhanced-Datasphere-Metadata-Extractor/2.0'
                })
                
                logger.info("✅ OAuth2 authentication successful")
            else:
                raise Exception(f"OAuth2 failed: HTTP {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"❌ Authentication setup failed: {e}")
            raise
    
    def refresh_token_if_needed(self):
        """Refresh OAuth token if it's about to expire"""
        if self.token_expires_at and datetime.now().timestamp() > (self.token_expires_at - 300):
            logger.info("🔄 Refreshing OAuth token...")
            self.setup_authentication()
    
    def discover_analytical_models(self) -> List[Dict[str, Any]]:
        """Discover analytical models using the working consumption API pattern"""
        self.refresh_token_if_needed()
        
        base_url = self.config["base_url"]
        
        # Known working pattern from your success
        consumption_base = "/api/v1/datasphere/consumption/analytical"
        
        # Try to discover available spaces and models
        discovered_models = []
        
        # Start with known working model
        known_models = [
            {
                "space": "SAP_CONTENT",
                "model": "New_Analytic_Model_2",
                "description": "Known working analytical model"
            }
        ]
        
        # Try to discover more models by exploring the API
        try:
            # Try to get a list of available models/spaces
            discovery_endpoints = [
                "/api/v1/datasphere/consumption/analytical",
                "/api/v1/datasphere/consumption",
                "/api/v1/datasphere/models",
                "/api/v1/datasphere/spaces"
            ]
            
            for endpoint in discovery_endpoints:
                try:
                    url = urljoin(base_url, endpoint)
                    response = self.session.get(url, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        logger.info(f"✅ Discovery endpoint working: {endpoint}")
                        
                        # Parse response to find more models
                        if isinstance(data, dict) and 'value' in data:
                            for item in data['value']:
                                if 'name' in item:
                                    discovered_models.append({
                                        "space": item.get('space', 'UNKNOWN'),
                                        "model": item['name'],
                                        "description": item.get('description', 'Discovered model')
                                    })
                        
                except Exception as e:
                    logger.debug(f"Discovery endpoint {endpoint} failed: {e}")
                    continue
        
        except Exception as e:
            logger.warning(f"Model discovery failed, using known models: {e}")
        
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
        
        logger.info(f"📊 Found {len(unique_models)} analytical models")
        return unique_models
    
    def extract_table_metadata(self, space: str, model: str) -> Optional[DatasphereTable]:
        """Extract detailed metadata for a specific analytical model"""
        self.refresh_token_if_needed()
        
        base_url = self.config["base_url"]
        
        # Build URLs using the working pattern
        model_base = f"/api/v1/datasphere/consumption/analytical/{space}/{model}"
        data_url = urljoin(base_url, f"{model_base}/{model}")
        service_url = urljoin(base_url, model_base)
        metadata_url = urljoin(base_url, f"{model_base}/$metadata")
        
        try:
            # Get service info first
            service_response = self.session.get(service_url, timeout=30)
            
            if service_response.status_code != 200:
                logger.error(f"❌ Service endpoint failed: HTTP {service_response.status_code}")
                return None
            
            service_data = service_response.json()
            odata_context = service_data.get('@odata.context', '')
            
            # Extract columns from metadata
            columns = self.extract_columns_from_metadata(metadata_url)
            
            # Create table object
            table = DatasphereTable(
                name=model,
                space=space,
                description=f"Analytical model from {space}",
                columns=columns,
                table_type='analytical_model',
                source_url=data_url,
                metadata_url=metadata_url,
                odata_context=odata_context,
                last_updated=datetime.now()
            )
            
            logger.info(f"✅ Extracted metadata for {space}/{model}: {len(columns)} columns")
            return table
            
        except Exception as e:
            logger.error(f"❌ Failed to extract metadata for {space}/{model}: {e}")
            return None
    
    def extract_columns_from_metadata(self, metadata_url: str) -> List[Dict[str, Any]]:
        """Extract column information from OData metadata XML"""
        try:
            # Try to get XML metadata
            headers = self.session.headers.copy()
            headers['Accept'] = 'application/xml'
            
            response = self.session.get(metadata_url, headers=headers, timeout=30)
            
            if response.status_code == 200 and 'xml' in response.headers.get('content-type', ''):
                return self.parse_odata_metadata_xml(response.text)
            
            # Fallback: try to infer from data endpoint
            logger.warning("⚠️ XML metadata not available, trying data inference")
            return self.infer_columns_from_data(metadata_url.replace('/$metadata', f'/{metadata_url.split("/")[-2]}'))
            
        except Exception as e:
            logger.warning(f"⚠️ Column extraction failed: {e}")
            return []
    
    def parse_odata_metadata_xml(self, xml_content: str) -> List[Dict[str, Any]]:
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
                        'type': self.convert_odata_type_to_glue(prop.get('Type', '')),
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
            
            logger.info(f"✅ Parsed {len(columns)} columns from XML metadata")
            
        except ET.ParseError as e:
            logger.error(f"❌ XML parsing failed: {e}")
        except Exception as e:
            logger.error(f"❌ Metadata parsing failed: {e}")
        
        return columns
    
    def infer_columns_from_data(self, data_url: str) -> List[Dict[str, Any]]:
        """Infer column structure from actual data"""
        try:
            # Get a small sample of data
            params = {'$top': 1}
            response = self.session.get(data_url, params=params, timeout=30)
            
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
                        inferred_type = self.infer_type_from_value(field_value)
                        
                        columns.append({
                            'name': field_name,
                            'type': inferred_type,
                            'nullable': field_value is None,
                            'description': f"Inferred from data sample"
                        })
                    
                    logger.info(f"✅ Inferred {len(columns)} columns from data")
                    return columns
            
        except Exception as e:
            logger.warning(f"⚠️ Data inference failed: {e}")
        
        return []
    
    def infer_type_from_value(self, value: Any) -> str:
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
    
    def convert_odata_type_to_glue(self, odata_type: str) -> str:
        """Convert OData types to AWS Glue types"""
        type_mapping = {
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
        
        # Remove namespace prefix if present
        clean_type = odata_type.split('.')[-1] if '.' in odata_type else odata_type
        full_type = f'Edm.{clean_type}' if not odata_type.startswith('Edm.') else odata_type
        
        return type_mapping.get(full_type, 'string')

class EnhancedGlueCatalogReplicator:
    """Enhanced AWS Glue catalog replicator with better error handling"""
    
    def __init__(self, aws_config: Dict[str, Any]):
        self.aws_config = aws_config
        self.glue_client = boto3.client(
            'glue',
            region_name=aws_config.get('region', 'us-east-1'),
            aws_access_key_id=aws_config.get('access_key_id'),
            aws_secret_access_key=aws_config.get('secret_access_key')
        )
    
    def ensure_database_exists(self, database_name: str) -> bool:
        """Ensure Glue database exists, create if not"""
        try:
            self.glue_client.get_database(Name=database_name)
            logger.info(f"✅ Database '{database_name}' exists")
            return True
        except self.glue_client.exceptions.EntityNotFoundException:
            try:
                self.glue_client.create_database(
                    DatabaseInput={
                        'Name': database_name,
                        'Description': f'SAP Datasphere metadata - Created {datetime.now().isoformat()}'
                    }
                )
                logger.info(f"✅ Created database '{database_name}'")
                return True
            except Exception as e:
                logger.error(f"❌ Failed to create database '{database_name}': {e}")
                return False
        except Exception as e:
            logger.error(f"❌ Error checking database '{database_name}': {e}")
            return False
    
    def replicate_table(self, database_name: str, table: DatasphereTable) -> bool:
        """Replicate a Datasphere table to Glue catalog"""
        try:
            table_name = f"{table.space.lower()}_{table.name.lower()}"
            
            # Prepare columns for Glue
            glue_columns = []
            for col in table.columns:
                glue_columns.append({
                    'Name': col['name'].lower(),
                    'Type': col['type'],
                    'Comment': col.get('description', '')
                })
            
            # Create table input
            table_input = {
                'Name': table_name,
                'Description': f"{table.description} (Space: {table.space})",
                'StorageDescriptor': {
                    'Columns': glue_columns,
                    'Location': table.source_url,
                    'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
                    'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
                    'SerdeInfo': {
                        'SerializationLibrary': 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
                    }
                },
                'Parameters': {
                    'datasphere_source': 'true',
                    'datasphere_space': table.space,
                    'datasphere_model': table.name,
                    'datasphere_type': table.table_type,
                    'source_url': table.source_url,
                    'metadata_url': table.metadata_url,
                    'odata_context': table.odata_context,
                    'last_updated': table.last_updated.isoformat(),
                    'extraction_tool': 'enhanced-metadata-extractor-v2.0'
                }
            }
            
            # Check if table exists and update/create accordingly
            try:
                existing_table = self.glue_client.get_table(
                    DatabaseName=database_name,
                    Name=table_name
                )
                
                # Update existing table
                self.glue_client.update_table(
                    DatabaseName=database_name,
                    TableInput=table_input
                )
                logger.info(f"✅ Updated table: {database_name}.{table_name}")
                
            except self.glue_client.exceptions.EntityNotFoundException:
                # Create new table
                self.glue_client.create_table(
                    DatabaseName=database_name,
                    TableInput=table_input
                )
                logger.info(f"✅ Created table: {database_name}.{table_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to replicate table {table.name}: {e}")
            return False

def run_enhanced_metadata_extraction(
    datasphere_config: Dict[str, Any],
    aws_config: Dict[str, Any],
    glue_database: str = "datasphere_enhanced_catalog"
) -> ExtractionResult:
    """Run the enhanced metadata extraction process"""
    
    start_time = datetime.now()
    logger.info("🚀 Starting Enhanced Datasphere Metadata Extraction")
    
    result = ExtractionResult(
        success=False,
        tables_discovered=0,
        tables_replicated=0,
        errors=[],
        warnings=[],
        execution_time=0.0
    )
    
    try:
        # Initialize clients
        logger.info("🔧 Initializing clients...")
        datasphere_client = EnhancedDatasphereClient(datasphere_config)
        glue_replicator = EnhancedGlueCatalogReplicator(aws_config)
        
        # Ensure Glue database exists
        if not glue_replicator.ensure_database_exists(glue_database):
            result.errors.append("Failed to create/access Glue database")
            return result
        
        # Discover analytical models
        logger.info("🔍 Discovering analytical models...")
        models = datasphere_client.discover_analytical_models()
        result.tables_discovered = len(models)
        
        if not models:
            result.warnings.append("No analytical models discovered")
            logger.warning("⚠️ No models found to process")
        
        # Process each model
        for model_info in models:
            try:
                space = model_info['space']
                model_name = model_info['model']
                
                logger.info(f"📊 Processing {space}/{model_name}...")
                
                # Extract metadata
                table = datasphere_client.extract_table_metadata(space, model_name)
                
                if table:
                    # Replicate to Glue
                    if glue_replicator.replicate_table(glue_database, table):
                        result.tables_replicated += 1
                    else:
                        result.errors.append(f"Failed to replicate {space}/{model_name}")
                else:
                    result.errors.append(f"Failed to extract metadata for {space}/{model_name}")
                    
            except Exception as e:
                error_msg = f"Error processing {model_info}: {e}"
                logger.error(f"❌ {error_msg}")
                result.errors.append(error_msg)
        
        # Calculate success
        result.success = result.tables_replicated > 0
        
        # Calculate execution time
        end_time = datetime.now()
        result.execution_time = (end_time - start_time).total_seconds()
        
        # Log summary
        logger.info("=" * 60)
        logger.info("EXTRACTION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"✅ Success: {result.success}")
        logger.info(f"📊 Models discovered: {result.tables_discovered}")
        logger.info(f"🔄 Tables replicated: {result.tables_replicated}")
        logger.info(f"⚠️ Warnings: {len(result.warnings)}")
        logger.info(f"❌ Errors: {len(result.errors)}")
        logger.info(f"⏱️ Execution time: {result.execution_time:.2f} seconds")
        
        if result.errors:
            logger.info("❌ Errors encountered:")
            for error in result.errors:
                logger.info(f"  • {error}")
        
        if result.warnings:
            logger.info("⚠️ Warnings:")
            for warning in result.warnings:
                logger.info(f"  • {warning}")
        
    except Exception as e:
        error_msg = f"Critical error in extraction process: {e}"
        logger.error(f"❌ {error_msg}")
        result.errors.append(error_msg)
        result.execution_time = (datetime.now() - start_time).total_seconds()
    
    return result

if __name__ == "__main__":
    # Configuration using your real Datasphere environment
    datasphere_config = {
        "base_url": "https://ailien-test.eu20.hcs.cloud.sap",
        "oauth": {
            "client_id": "sb-dmi-api-proxy-sac-saceu20!t3944|dmi-api-proxy-sac-saceu20!b3944",
            "client_secret": "YOUR_CLIENT_SECRET",  # Replace with your actual secret
            "token_url": "https://ailien-test.eu20.hcs.cloud.sap/oauth/token"
        }
    }
    
    # AWS configuration
    aws_config = {
        "region": "us-east-1",
        # AWS credentials will be picked up from environment/IAM role
    }
    
    # Run extraction
    result = run_enhanced_metadata_extraction(
        datasphere_config=datasphere_config,
        aws_config=aws_config,
        glue_database="datasphere_enhanced_catalog"
    )
    
    # Save results
    with open(f'extraction_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
        json.dump({
            'success': result.success,
            'tables_discovered': result.tables_discovered,
            'tables_replicated': result.tables_replicated,
            'errors': result.errors,
            'warnings': result.warnings,
            'execution_time': result.execution_time,
            'timestamp': datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"\n🎯 Extraction completed with {result.tables_replicated}/{result.tables_discovered} tables replicated")