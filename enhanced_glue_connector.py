#!/usr/bin/env python3
"""
Enhanced AWS Glue Connector with Rich Business Metadata Integration
Extends the base Glue connector with comprehensive business metadata synchronization,
business-friendly naming conventions, and advanced domain-based tagging.
"""

import boto3
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from botocore.exceptions import ClientError

from glue_connector import GlueConnector, GlueConfig
from rich_business_metadata_sync import (
    RichBusinessMetadataEngine, EnhancedBusinessContext, BusinessFriendlyColumn,
    DataClassificationTag, GovernancePolicy, DataSensitivityLevel
)
from metadata_sync_core import MetadataAsset, AssetType, SourceSystem, BusinessContext
from sync_logging import SyncLogger, EventType

@dataclass
class EnhancedGlueConfig(GlueConfig):
    """Enhanced configuration for Glue connector with business metadata support"""
    enable_business_metadata: bool = True
    enable_multi_language_support: bool = True
    enable_automated_classification: bool = True
    enable_governance_enforcement: bool = True
    business_metadata_prefix: str = "business_"
    classification_tag_prefix: str = "classification_"
    governance_tag_prefix: str = "governance_"

class EnhancedGlueConnector(GlueConnector):
    """Enhanced AWS Glue connector with rich business metadata integration"""
    
    def __init__(self, config: EnhancedGlueConfig):
        super().__init__(config)
        self.enhanced_config = config
        
        # Initialize business metadata engine
        self.business_metadata_engine = RichBusinessMetadataEngine(config.environment_name)
        
        # Enhanced logger
        self.logger = SyncLogger(f"enhanced_glue_connector_{config.environment_name}")
        
        # Business-friendly naming patterns
        self.business_naming_patterns = {
            "customer": {
                "table_prefix": "customer_",
                "column_patterns": {
                    r".*cust.*id.*": "Customer_ID",
                    r".*cust.*name.*": "Customer_Name",
                    r".*email.*": "Email_Address"
                }
            },
            "finance": {
                "table_prefix": "financial_",
                "column_patterns": {
                    r".*amount.*": "Amount",
                    r".*revenue.*": "Revenue",
                    r".*cost.*": "Cost"
                }
            },
            "sales": {
                "table_prefix": "sales_",
                "column_patterns": {
                    r".*order.*id.*": "Order_ID",
                    r".*product.*": "Product",
                    r".*quantity.*": "Quantity"
                }
            }
        }
    
    def create_asset_with_rich_metadata(self, asset: MetadataAsset) -> bool:
        """Create asset with comprehensive business metadata integration"""
        
        if not self.is_connected:
            self.logger.logger.error("Not connected to AWS Glue")
            return False
        
        try:
            self.logger.log_event(
                event_type=EventType.ASSET_CREATED,
                source_system=asset.source_system.value,
                target_system=self.config.environment_name,
                asset_id=asset.asset_id,
                asset_type=asset.asset_type.value,
                operation="create_asset_with_rich_metadata",
                status="started",
                details={"asset_name": asset.technical_name}
            )
            
            if asset.asset_type == AssetType.SPACE:
                return self._create_database_with_rich_metadata(asset)
            elif asset.asset_type in [AssetType.TABLE, AssetType.VIEW, AssetType.ANALYTICAL_MODEL]:
                return self._create_table_with_rich_metadata(asset)
            else:
                self.logger.logger.warning(f"Unsupported asset type for enhanced creation: {asset.asset_type}")
                return False
                
        except Exception as e:
            self.logger.log_event(
                event_type=EventType.ERROR_OCCURRED,
                source_system=asset.source_system.value,
                target_system=self.config.environment_name,
                asset_id=asset.asset_id,
                operation="create_asset_with_rich_metadata",
                status="failed",
                details={},
                error_message=str(e)
            )
            return False
    
    def _create_database_with_rich_metadata(self, asset: MetadataAsset) -> bool:
        """Create database with enhanced business metadata"""
        
        try:
            # Extract enhanced business context
            enhanced_context = self.business_metadata_engine.extract_business_metadata_from_datasphere(asset)
            
            # Generate business-friendly database name
            business_db_name = self._generate_business_friendly_database_name(asset, enhanced_context)
            
            # Prepare database input with rich metadata
            database_input = {
                'Name': business_db_name,
                'Description': self._create_rich_database_description(asset, enhanced_context),
                'Parameters': self._create_database_parameters(asset, enhanced_context)
            }
            
            # Check if database exists
            try:
                self.glue_client.get_database(Name=business_db_name)
                # Database exists, update it
                self.glue_client.update_database(
                    Name=business_db_name,
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
            
            self.logger.log_event(
                event_type=EventType.ASSET_CREATED,
                source_system=asset.source_system.value,
                target_system=self.config.environment_name,
                asset_id=asset.asset_id,
                asset_type=asset.asset_type.value,
                operation="create_database_with_rich_metadata",
                status="completed",
                details={
                    "database_name": business_db_name,
                    "operation": operation,
                    "business_metadata_applied": True
                }
            )
            
            return True
            
        except Exception as e:
            self.logger.logger.error(f"Failed to create database with rich metadata {asset.technical_name}: {str(e)}")
            return False
    
    def _create_table_with_rich_metadata(self, asset: MetadataAsset) -> bool:
        """Create table with comprehensive business metadata"""
        
        try:
            # Extract enhanced business context
            enhanced_context = self.business_metadata_engine.extract_business_metadata_from_datasphere(asset)
            
            # Merge multi-source metadata
            merged_asset = self.business_metadata_engine.merge_multi_source_metadata(asset)
            
            # Create business-friendly columns
            business_columns = self.business_metadata_engine.create_business_friendly_columns(
                merged_asset, enhanced_context
            )
            
            # Determine database name
            database_name = self._determine_database_name(merged_asset, enhanced_context)
            
            # Ensure database exists
            self._ensure_database_exists_with_metadata(database_name, merged_asset.source_system.value, enhanced_context)
            
            # Generate business-friendly table name
            business_table_name = self._generate_business_friendly_table_name(merged_asset, enhanced_context)
            
            # Prepare Glue columns with business metadata
            glue_columns = self._create_glue_columns_with_business_metadata(business_columns)
            
            # Prepare table input with comprehensive metadata
            table_input = {
                'Name': business_table_name,
                'Description': self._create_rich_table_description(merged_asset, enhanced_context),
                'Owner': enhanced_context.steward or enhanced_context.owner or merged_asset.owner,
                'StorageDescriptor': {
                    'Columns': glue_columns,
                    'Location': merged_asset.custom_properties.get('location', ''),
                    'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
                    'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
                    'SerdeInfo': {
                        'SerializationLibrary': 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
                    }
                },
                'TableType': 'EXTERNAL_TABLE',
                'Parameters': self._create_comprehensive_table_parameters(merged_asset, enhanced_context, business_columns)
            }
            
            # Check if table exists
            try:
                self.glue_client.get_table(DatabaseName=database_name, Name=business_table_name)
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
            
            self.logger.log_event(
                event_type=EventType.ASSET_CREATED,
                source_system=merged_asset.source_system.value,
                target_system=self.config.environment_name,
                asset_id=merged_asset.asset_id,
                asset_type=merged_asset.asset_type.value,
                operation="create_table_with_rich_metadata",
                status="completed",
                details={
                    "database_name": database_name,
                    "table_name": business_table_name,
                    "business_columns": len(business_columns),
                    "classification_tags": len(enhanced_context.classification_tags),
                    "governance_policies": len(enhanced_context.governance_policies),
                    "operation": operation
                }
            )
            
            return True
            
        except Exception as e:
            self.logger.logger.error(f"Failed to create table with rich metadata {asset.technical_name}: {str(e)}")
            return False
    
    def _generate_business_friendly_database_name(self, asset: MetadataAsset, context: EnhancedBusinessContext) -> str:
        """Generate business-friendly database name"""
        
        # Start with technical name
        base_name = asset.technical_name.lower()
        
        # Apply business naming if business name is available
        if context.business_name:
            base_name = re.sub(r'[^a-zA-Z0-9_]', '_', context.business_name.lower())
        
        # Add environment and source prefix
        business_name = f"datasphere_{base_name}_{self.config.environment_name}"
        
        # Ensure Glue naming compliance
        business_name = re.sub(r'[^a-zA-Z0-9_]', '_', business_name)
        business_name = re.sub(r'_+', '_', business_name)
        business_name = business_name.strip('_')
        
        return business_name
    
    def _generate_business_friendly_table_name(self, asset: MetadataAsset, context: EnhancedBusinessContext) -> str:
        """Generate business-friendly table name with domain context"""
        
        # Determine business domain
        business_domain = self._extract_business_domain(context)
        
        # Start with business name if available
        if context.business_name:
            base_name = re.sub(r'[^a-zA-Z0-9_]', '_', context.business_name.lower())
        else:
            base_name = asset.technical_name.lower()
        
        # Apply domain-specific naming patterns
        if business_domain in self.business_naming_patterns:
            domain_config = self.business_naming_patterns[business_domain]
            table_prefix = domain_config.get("table_prefix", "")
            
            if not base_name.startswith(table_prefix):
                base_name = f"{table_prefix}{base_name}"
        
        # Add asset type suffix for clarity
        if asset.asset_type == AssetType.ANALYTICAL_MODEL:
            base_name = f"{base_name}_model"
        elif asset.asset_type == AssetType.VIEW:
            base_name = f"{base_name}_view"
        
        # Ensure Glue naming compliance
        business_name = re.sub(r'[^a-zA-Z0-9_]', '_', base_name)
        business_name = re.sub(r'_+', '_', business_name)
        business_name = business_name.strip('_')
        
        return business_name
    
    def _create_glue_columns_with_business_metadata(self, business_columns: List[BusinessFriendlyColumn]) -> List[Dict[str, Any]]:
        """Create Glue column definitions with business metadata"""
        
        glue_columns = []
        
        for col in business_columns:
            # Create rich column comment combining business and technical information
            comment_parts = []
            
            # Add business description
            if col.business_description:
                comment_parts.append(f"Business: {col.business_description}")
            
            # Add domain context
            if col.domain_context and col.domain_context != "general":
                comment_parts.append(f"Domain: {col.domain_context}")
            
            # Add business data type
            if col.business_data_type != col.data_type:
                comment_parts.append(f"Business Type: {col.business_data_type}")
            
            # Add classification information
            if col.classification_tags:
                classifications = [tag.tag_name for tag in col.classification_tags]
                comment_parts.append(f"Classification: {', '.join(classifications)}")
            
            # Add sensitivity level
            if col.sensitivity_level:
                comment_parts.append(f"Sensitivity: {col.sensitivity_level.value}")
            
            # Add glossary term reference
            if col.glossary_term_id:
                comment_parts.append(f"Glossary: {col.glossary_term_id}")
            
            rich_comment = " | ".join(comment_parts) if comment_parts else col.business_description
            
            glue_column = {
                'Name': col.technical_name.lower(),
                'Type': self._convert_to_glue_type(col.data_type),
                'Comment': rich_comment[:255]  # Glue has a 255 character limit for comments
            }
            
            glue_columns.append(glue_column)
        
        return glue_columns
    
    def _create_rich_database_description(self, asset: MetadataAsset, context: EnhancedBusinessContext) -> str:
        """Create rich database description with business context"""
        
        description_parts = []
        
        # Add business description
        if context.description:
            description_parts.append(context.description)
        elif asset.description:
            description_parts.append(asset.description)
        
        # Add business domain information
        business_domain = self._extract_business_domain(context)
        if business_domain != "general":
            description_parts.append(f"Business Domain: {business_domain.title()}")
        
        # Add stewardship information
        if context.steward:
            description_parts.append(f"Data Steward: {context.steward}")
        
        # Add certification status
        if context.certification_status:
            description_parts.append(f"Certification: {context.certification_status}")
        
        # Add governance information
        if context.governance_policies:
            policy_names = [policy.policy_name for policy in context.governance_policies[:3]]  # Limit to 3
            description_parts.append(f"Governance Policies: {', '.join(policy_names)}")
        
        return " | ".join(description_parts) if description_parts else f"Datasphere database: {asset.technical_name}"
    
    def _create_rich_table_description(self, asset: MetadataAsset, context: EnhancedBusinessContext) -> str:
        """Create rich table description with comprehensive business metadata"""
        
        description_parts = []
        
        # Add business description
        if context.description:
            description_parts.append(context.description)
        elif asset.description:
            description_parts.append(asset.description)
        
        # Add asset type context
        if asset.asset_type == AssetType.ANALYTICAL_MODEL:
            model_info = []
            if context.dimensions:
                model_info.append(f"Dimensions: {len(context.dimensions)}")
            if context.measures:
                model_info.append(f"Measures: {len(context.measures)}")
            if model_info:
                description_parts.append(f"Analytical Model - {', '.join(model_info)}")
        
        # Add business domain
        business_domain = self._extract_business_domain(context)
        if business_domain != "general":
            description_parts.append(f"Domain: {business_domain.title()}")
        
        # Add data classification summary
        if context.classification_tags:
            unique_classifications = list(set(tag.tag_name for tag in context.classification_tags))
            description_parts.append(f"Classifications: {', '.join(unique_classifications[:3])}")
        
        # Add sensitivity level
        if context.sensitivity_level:
            description_parts.append(f"Sensitivity: {context.sensitivity_level.value.title()}")
        
        # Add quality score if available
        if context.quality_metrics and context.quality_metrics.overall_score:
            description_parts.append(f"Quality Score: {context.quality_metrics.overall_score:.2f}")
        
        return " | ".join(description_parts) if description_parts else f"Datasphere {asset.asset_type.value}: {asset.technical_name}"
    
    def _create_database_parameters(self, asset: MetadataAsset, context: EnhancedBusinessContext) -> Dict[str, str]:
        """Create comprehensive database parameters with business metadata"""
        
        parameters = {
            # Source system information
            'source_system': asset.source_system.value,
            'asset_id': asset.asset_id,
            'created_by': 'enhanced_metadata_sync_engine',
            'creation_timestamp': datetime.now().isoformat(),
            
            # Business metadata
            'business_name': context.business_name or asset.technical_name,
            'business_description': context.description or asset.description or '',
            'business_owner': context.owner or asset.owner or '',
            'data_steward': context.steward or '',
            'certification_status': context.certification_status or 'uncertified',
            
            # Domain and classification
            'business_domain': self._extract_business_domain(context),
            'sensitivity_level': context.sensitivity_level.value if context.sensitivity_level else 'internal',
            
            # Governance information
            'governance_policies_count': str(len(context.governance_policies)),
            'classification_tags_count': str(len(context.classification_tags)),
            
            # Multi-language support
            'supports_multi_language': str(bool(context.multi_language_names or context.multi_language_descriptions)),
            
            # Enhanced metadata flag
            'enhanced_business_metadata': 'true'
        }
        
        # Add multi-language names
        for lang, name in context.multi_language_names.items():
            parameters[f'business_name_{lang}'] = name
        
        # Add multi-language descriptions
        for lang, desc in context.multi_language_descriptions.items():
            parameters[f'business_description_{lang}'] = desc
        
        # Add governance policy references
        if context.governance_policies:
            policy_ids = [policy.policy_id for policy in context.governance_policies]
            parameters['governance_policy_ids'] = ','.join(policy_ids)
        
        # Add classification tags
        if context.classification_tags:
            classification_names = [tag.tag_name for tag in context.classification_tags]
            parameters['classification_tags'] = ','.join(classification_names)
        
        # Add custom properties from original asset
        if asset.custom_properties:
            for key, value in asset.custom_properties.items():
                if not key.startswith('enhanced_'):  # Avoid conflicts
                    parameters[f'original_{key}'] = str(value)
        
        return parameters
    
    def _create_comprehensive_table_parameters(self, asset: MetadataAsset, context: EnhancedBusinessContext, 
                                             business_columns: List[BusinessFriendlyColumn]) -> Dict[str, str]:
        """Create comprehensive table parameters with rich business metadata"""
        
        parameters = self._create_database_parameters(asset, context)
        
        # Add table-specific metadata
        parameters.update({
            'table_type': asset.asset_type.value,
            'column_count': str(len(business_columns)),
            'business_friendly_columns': str(len([col for col in business_columns if col.business_name != col.technical_name])),
        })
        
        # Add analytical model specific metadata
        if asset.asset_type == AssetType.ANALYTICAL_MODEL:
            parameters.update({
                'dimensions': ','.join(context.dimensions) if context.dimensions else '',
                'measures': ','.join(context.measures) if context.measures else '',
                'hierarchies': ','.join(context.hierarchies) if context.hierarchies else '',
                'dimensions_count': str(len(context.dimensions)),
                'measures_count': str(len(context.measures)),
                'hierarchies_count': str(len(context.hierarchies))
            })
        
        # Add quality metrics
        if context.quality_metrics:
            parameters.update({
                'quality_overall_score': str(context.quality_metrics.overall_score or 0),
                'quality_completeness_score': str(context.quality_metrics.completeness_score or 0),
                'quality_accuracy_score': str(context.quality_metrics.accuracy_score or 0),
                'quality_last_assessment': context.quality_metrics.last_assessment_date.isoformat() if context.quality_metrics.last_assessment_date else ''
            })
        
        # Add usage statistics
        if context.usage_statistics:
            parameters.update({
                'usage_monthly_access_count': str(context.usage_statistics.access_count_monthly or 0),
                'usage_monthly_unique_users': str(context.usage_statistics.unique_users_monthly or 0),
                'usage_last_accessed': context.usage_statistics.last_accessed.isoformat() if context.usage_statistics.last_accessed else ''
            })
        
        # Add glossary terms
        if context.glossary_terms:
            glossary_term_ids = [term.term_id for term in context.glossary_terms]
            parameters['glossary_term_ids'] = ','.join(glossary_term_ids)
            parameters['glossary_terms_count'] = str(len(context.glossary_terms))
        
        # Add business rules
        if context.business_rules:
            business_rule_ids = [rule.rule_id for rule in context.business_rules]
            parameters['business_rule_ids'] = ','.join(business_rule_ids)
            parameters['business_rules_count'] = str(len(context.business_rules))
        
        # Add column-level classification summary
        column_classifications = {}
        for col in business_columns:
            for tag in col.classification_tags:
                column_classifications[tag.tag_name] = column_classifications.get(tag.tag_name, 0) + 1
        
        if column_classifications:
            parameters['column_classifications'] = json.dumps(column_classifications)
        
        return parameters
    
    def _extract_business_domain(self, context: EnhancedBusinessContext) -> str:
        """Extract business domain from context tags"""
        
        for tag in context.tags:
            if tag.startswith("domain:"):
                return tag.split(":", 1)[1]
        
        # Try to infer from glossary terms
        if context.glossary_terms:
            domains = [term.business_domain for term in context.glossary_terms]
            if domains:
                return domains[0]  # Use first domain found
        
        return "general"
    
    def _ensure_database_exists_with_metadata(self, database_name: str, source_system: str, context: EnhancedBusinessContext):
        """Ensure database exists with enhanced metadata"""
        
        try:
            self.glue_client.get_database(Name=database_name)
        except ClientError as e:
            if e.response['Error']['Code'] == 'EntityNotFoundException':
                # Create database with enhanced metadata
                database_input = {
                    'Name': database_name,
                    'Description': f'Enhanced database for {source_system} metadata synchronization with business context',
                    'Parameters': {
                        'source_system': source_system,
                        'created_by': 'enhanced_metadata_sync_engine',
                        'creation_timestamp': datetime.now().isoformat(),
                        'business_domain': self._extract_business_domain(context),
                        'enhanced_business_metadata': 'true'
                    }
                }
                
                self.glue_client.create_database(DatabaseInput=database_input)
                self.logger.logger.info(f"Created enhanced database: {database_name}")
            else:
                raise
    
    def _determine_database_name(self, asset: MetadataAsset, context: EnhancedBusinessContext) -> str:
        """Determine appropriate database name based on business context"""
        
        # Check for existing database mapping in custom properties
        if 'glue_database' in asset.custom_properties:
            return asset.custom_properties['glue_database']
        
        # Use Datasphere space if available
        if 'datasphere_space' in asset.custom_properties:
            space_name = asset.custom_properties['datasphere_space']
            return self._generate_business_friendly_database_name_from_space(space_name, context)
        
        # Use business domain
        business_domain = self._extract_business_domain(context)
        return f"datasphere_{business_domain}_{self.config.environment_name}"
    
    def _generate_business_friendly_database_name_from_space(self, space_name: str, context: EnhancedBusinessContext) -> str:
        """Generate business-friendly database name from Datasphere space"""
        
        # Clean space name
        clean_space = re.sub(r'[^a-zA-Z0-9_]', '_', space_name.lower())
        
        # Add business context if available
        business_domain = self._extract_business_domain(context)
        if business_domain != "general":
            clean_space = f"{business_domain}_{clean_space}"
        
        return f"datasphere_{clean_space}_{self.config.environment_name}"

# Factory function
def create_enhanced_glue_connector(region: str = "us-east-1", environment: str = "default") -> EnhancedGlueConnector:
    """Create an enhanced Glue connector with business metadata support"""
    
    config = EnhancedGlueConfig(
        region=region,
        environment_name=environment,
        enable_business_metadata=True,
        enable_multi_language_support=True,
        enable_automated_classification=True,
        enable_governance_enforcement=True
    )
    
    return EnhancedGlueConnector(config)

# Example usage and testing
if __name__ == "__main__":
    print("🏢 Enhanced AWS Glue Connector with Rich Business Metadata")
    print("=" * 58)
    
    try:
        # Create enhanced connector
        connector = create_enhanced_glue_connector("us-east-1", "test")
        
        print(f"Testing enhanced connection to AWS Glue in {connector.config.region}...")
        
        # Test connection
        if connector.connect():
            print("✅ Enhanced connection successful!")
            
            # Show business metadata capabilities
            print(f"\n🏢 Business Metadata Capabilities:")
            print(f"  • Business Glossary Terms: {len(connector.business_metadata_engine.business_glossary)}")
            print(f"  • Governance Policies: {len(connector.business_metadata_engine.governance_policies)}")
            print(f"  • Domain Naming Rules: {len(connector.business_metadata_engine.domain_naming_rules)}")
            print(f"  • Classification Policies: {len(connector.business_metadata_engine.classification_policies)}")
            
            # Show enhanced configuration
            print(f"\n⚙️ Enhanced Configuration:")
            print(f"  • Business Metadata: {connector.enhanced_config.enable_business_metadata}")
            print(f"  • Multi-language Support: {connector.enhanced_config.enable_multi_language_support}")
            print(f"  • Automated Classification: {connector.enhanced_config.enable_automated_classification}")
            print(f"  • Governance Enforcement: {connector.enhanced_config.enable_governance_enforcement}")
            
            # Disconnect
            connector.disconnect()
            print("\n✅ Disconnected successfully")
            
        else:
            print("❌ Enhanced connection failed")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print(f"\n🎉 Enhanced Glue connector test completed!")