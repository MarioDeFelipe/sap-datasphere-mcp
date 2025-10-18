#!/usr/bin/env python3
"""
Core Metadata Synchronization Framework
Implements base classes for MetadataAsset, SyncConfiguration, and MetadataSyncEngine
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import logging
import json
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Enums for type safety
class AssetType(Enum):
    """Types of metadata assets"""
    SPACE = "space"
    TABLE = "table"
    VIEW = "view"
    ANALYTICAL_MODEL = "analytical_model"
    DATA_FLOW = "data_flow"

class SourceSystem(Enum):
    """Source systems for metadata"""
    DATASPHERE = "datasphere"
    GLUE = "glue"

class SyncStatus(Enum):
    """Synchronization status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"

class PriorityLevel(Enum):
    """Priority levels for synchronization"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class SyncFrequency(Enum):
    """Synchronization frequency options"""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"

class ConflictStrategy(Enum):
    """Conflict resolution strategies"""
    SOURCE_WINS = "source_wins"
    TARGET_WINS = "target_wins"
    MERGE = "merge"
    MANUAL = "manual"

# Data Models
@dataclass
class BusinessContext:
    """Business context information for metadata assets"""
    business_name: Optional[str] = None
    description: Optional[str] = None
    owner: Optional[str] = None
    steward: Optional[str] = None
    certification_status: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    dimensions: List[str] = field(default_factory=list)
    measures: List[str] = field(default_factory=list)
    hierarchies: List[str] = field(default_factory=list)

@dataclass
class LineageRelationship:
    """Data lineage relationship information"""
    source_asset_id: str
    target_asset_id: str
    relationship_type: str  # "derives_from", "feeds_into", "transforms"
    transformation_logic: Optional[str] = None
    created_date: datetime = field(default_factory=datetime.now)

@dataclass
class MetadataAsset:
    """Core metadata asset model"""
    asset_id: str
    asset_type: AssetType
    source_system: SourceSystem
    technical_name: str
    business_name: Optional[str] = None
    description: Optional[str] = None
    owner: Optional[str] = None
    created_date: datetime = field(default_factory=datetime.now)
    modified_date: datetime = field(default_factory=datetime.now)
    sync_status: SyncStatus = SyncStatus.PENDING
    business_context: BusinessContext = field(default_factory=BusinessContext)
    lineage: List[LineageRelationship] = field(default_factory=list)
    schema_info: Dict[str, Any] = field(default_factory=dict)
    custom_properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'asset_id': self.asset_id,
            'asset_type': self.asset_type.value,
            'source_system': self.source_system.value,
            'technical_name': self.technical_name,
            'business_name': self.business_name,
            'description': self.description,
            'owner': self.owner,
            'created_date': self.created_date.isoformat(),
            'modified_date': self.modified_date.isoformat(),
            'sync_status': self.sync_status.value,
            'business_context': {
                'business_name': self.business_context.business_name,
                'description': self.business_context.description,
                'owner': self.business_context.owner,
                'steward': self.business_context.steward,
                'certification_status': self.business_context.certification_status,
                'tags': self.business_context.tags,
                'dimensions': self.business_context.dimensions,
                'measures': self.business_context.measures,
                'hierarchies': self.business_context.hierarchies
            },
            'lineage': [
                {
                    'source_asset_id': rel.source_asset_id,
                    'target_asset_id': rel.target_asset_id,
                    'relationship_type': rel.relationship_type,
                    'transformation_logic': rel.transformation_logic,
                    'created_date': rel.created_date.isoformat()
                }
                for rel in self.lineage
            ],
            'schema_info': self.schema_info,
            'custom_properties': self.custom_properties
        }

@dataclass
class TransformationRule:
    """Data transformation rule for mapping between systems"""
    rule_id: str
    source_field: str
    target_field: str
    transformation_logic: str
    validation_rules: List[str] = field(default_factory=list)
    is_active: bool = True

@dataclass
class SyncConfiguration:
    """Synchronization configuration model"""
    config_id: str
    source_environment: str
    target_environment: str
    sync_frequency: SyncFrequency
    priority_level: PriorityLevel
    conflict_resolution: ConflictStrategy
    field_mappings: Dict[str, str] = field(default_factory=dict)
    transformation_rules: List[TransformationRule] = field(default_factory=list)
    asset_filters: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    created_date: datetime = field(default_factory=datetime.now)
    modified_date: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'config_id': self.config_id,
            'source_environment': self.source_environment,
            'target_environment': self.target_environment,
            'sync_frequency': self.sync_frequency.value,
            'priority_level': self.priority_level.value,
            'conflict_resolution': self.conflict_resolution.value,
            'field_mappings': self.field_mappings,
            'transformation_rules': [
                {
                    'rule_id': rule.rule_id,
                    'source_field': rule.source_field,
                    'target_field': rule.target_field,
                    'transformation_logic': rule.transformation_logic,
                    'validation_rules': rule.validation_rules,
                    'is_active': rule.is_active
                }
                for rule in self.transformation_rules
            ],
            'asset_filters': self.asset_filters,
            'is_active': self.is_active,
            'created_date': self.created_date.isoformat(),
            'modified_date': self.modified_date.isoformat()
        }

# Abstract Base Classes
class MetadataConnector(ABC):
    """Abstract base class for metadata connectors"""
    
    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the metadata system"""
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """Disconnect from the metadata system"""
        pass
    
    @abstractmethod
    def get_assets(self, asset_type: AssetType = None) -> List[MetadataAsset]:
        """Retrieve metadata assets"""
        pass
    
    @abstractmethod
    def create_asset(self, asset: MetadataAsset) -> bool:
        """Create a new metadata asset"""
        pass
    
    @abstractmethod
    def update_asset(self, asset: MetadataAsset) -> bool:
        """Update an existing metadata asset"""
        pass
    
    @abstractmethod
    def delete_asset(self, asset_id: str) -> bool:
        """Delete a metadata asset"""
        pass

class SyncEngine(ABC):
    """Abstract base class for synchronization engines"""
    
    @abstractmethod
    def sync_assets(self, config: SyncConfiguration) -> Dict[str, Any]:
        """Synchronize assets based on configuration"""
        pass
    
    @abstractmethod
    def validate_sync(self, config: SyncConfiguration) -> Dict[str, Any]:
        """Validate synchronization configuration"""
        pass

# Core Implementation Classes
class MetadataSyncEngine:
    """Core metadata synchronization engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.sync_history: List[Dict[str, Any]] = []
        self.active_configs: Dict[str, SyncConfiguration] = {}
        self.priority_queue: List[MetadataAsset] = []
        
    def register_configuration(self, config: SyncConfiguration) -> bool:
        """Register a synchronization configuration"""
        try:
            self.active_configs[config.config_id] = config
            self.logger.info(f"Registered sync configuration: {config.config_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to register configuration {config.config_id}: {str(e)}")
            return False
    
    def get_priority_order(self, assets: List[MetadataAsset]) -> List[MetadataAsset]:
        """Sort assets by priority for synchronization"""
        priority_map = {
            AssetType.ANALYTICAL_MODEL: 1,  # Critical priority
            AssetType.TABLE: 2,             # Critical priority
            AssetType.VIEW: 3,              # High priority
            AssetType.SPACE: 4,             # High priority
            AssetType.DATA_FLOW: 5          # Medium priority
        }
        
        return sorted(assets, key=lambda asset: priority_map.get(asset.asset_type, 999))
    
    def schedule_sync(self, config_id: str) -> Dict[str, Any]:
        """Schedule synchronization based on configuration"""
        if config_id not in self.active_configs:
            return {
                'success': False,
                'error': f'Configuration {config_id} not found'
            }
        
        config = self.active_configs[config_id]
        sync_id = str(uuid.uuid4())
        
        sync_record = {
            'sync_id': sync_id,
            'config_id': config_id,
            'status': 'scheduled',
            'scheduled_time': datetime.now().isoformat(),
            'priority_level': config.priority_level.value,
            'sync_frequency': config.sync_frequency.value
        }
        
        self.sync_history.append(sync_record)
        self.logger.info(f"Scheduled sync {sync_id} for configuration {config_id}")
        
        return {
            'success': True,
            'sync_id': sync_id,
            'scheduled_time': sync_record['scheduled_time']
        }
    
    def execute_sync(self, sync_id: str, source_connector: MetadataConnector, 
                    target_connector: MetadataConnector) -> Dict[str, Any]:
        """Execute synchronization operation"""
        try:
            # Find sync record
            sync_record = next((s for s in self.sync_history if s['sync_id'] == sync_id), None)
            if not sync_record:
                return {'success': False, 'error': f'Sync {sync_id} not found'}
            
            # Update status
            sync_record['status'] = 'in_progress'
            sync_record['start_time'] = datetime.now().isoformat()
            
            config_id = sync_record['config_id']
            config = self.active_configs[config_id]
            
            # Get source assets
            source_assets = source_connector.get_assets()
            prioritized_assets = self.get_priority_order(source_assets)
            
            sync_results = {
                'total_assets': len(prioritized_assets),
                'processed': 0,
                'successful': 0,
                'failed': 0,
                'conflicts': 0,
                'errors': []
            }
            
            # Process each asset
            for asset in prioritized_assets:
                try:
                    # Apply transformation rules if any
                    transformed_asset = self._apply_transformations(asset, config)
                    
                    # Attempt to sync
                    if target_connector.create_asset(transformed_asset):
                        sync_results['successful'] += 1
                        asset.sync_status = SyncStatus.COMPLETED
                    else:
                        sync_results['failed'] += 1
                        asset.sync_status = SyncStatus.FAILED
                        
                except Exception as e:
                    sync_results['failed'] += 1
                    sync_results['errors'].append(f"Asset {asset.asset_id}: {str(e)}")
                    asset.sync_status = SyncStatus.FAILED
                    
                sync_results['processed'] += 1
            
            # Update sync record
            sync_record['status'] = 'completed'
            sync_record['end_time'] = datetime.now().isoformat()
            sync_record['results'] = sync_results
            
            self.logger.info(f"Completed sync {sync_id}: {sync_results['successful']}/{sync_results['total_assets']} successful")
            
            return {
                'success': True,
                'sync_id': sync_id,
                'results': sync_results
            }
            
        except Exception as e:
            # Update sync record with error
            if 'sync_record' in locals():
                sync_record['status'] = 'failed'
                sync_record['error'] = str(e)
                sync_record['end_time'] = datetime.now().isoformat()
            
            self.logger.error(f"Sync {sync_id} failed: {str(e)}")
            return {
                'success': False,
                'sync_id': sync_id,
                'error': str(e)
            }
    
    def _apply_transformations(self, asset: MetadataAsset, config: SyncConfiguration) -> MetadataAsset:
        """Apply transformation rules to an asset"""
        transformed_asset = asset
        
        # Apply field mappings
        for source_field, target_field in config.field_mappings.items():
            if hasattr(transformed_asset, source_field):
                value = getattr(transformed_asset, source_field)
                setattr(transformed_asset, target_field, value)
        
        # Apply transformation rules
        for rule in config.transformation_rules:
            if rule.is_active:
                # Simple transformation logic - can be extended
                if hasattr(transformed_asset, rule.source_field):
                    source_value = getattr(transformed_asset, rule.source_field)
                    # Apply transformation logic (simplified)
                    if rule.transformation_logic == "uppercase":
                        transformed_value = str(source_value).upper()
                    elif rule.transformation_logic == "lowercase":
                        transformed_value = str(source_value).lower()
                    elif rule.transformation_logic.startswith("prefix:"):
                        prefix = rule.transformation_logic.split(":", 1)[1]
                        transformed_value = f"{prefix}{source_value}"
                    else:
                        transformed_value = source_value
                    
                    setattr(transformed_asset, rule.target_field, transformed_value)
        
        return transformed_asset
    
    def get_sync_status(self, sync_id: str) -> Dict[str, Any]:
        """Get status of a synchronization operation"""
        sync_record = next((s for s in self.sync_history if s['sync_id'] == sync_id), None)
        if not sync_record:
            return {'success': False, 'error': f'Sync {sync_id} not found'}
        
        return {
            'success': True,
            'sync_record': sync_record
        }
    
    def get_sync_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get synchronization history"""
        return sorted(self.sync_history, key=lambda x: x.get('scheduled_time', ''), reverse=True)[:limit]
    
    def validate_configuration(self, config: SyncConfiguration) -> Dict[str, Any]:
        """Validate synchronization configuration"""
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Basic validation
        if not config.source_environment:
            validation_results['errors'].append("Source environment is required")
            validation_results['is_valid'] = False
        
        if not config.target_environment:
            validation_results['errors'].append("Target environment is required")
            validation_results['is_valid'] = False
        
        # Validate transformation rules
        for rule in config.transformation_rules:
            if not rule.source_field or not rule.target_field:
                validation_results['errors'].append(f"Rule {rule.rule_id}: source and target fields are required")
                validation_results['is_valid'] = False
        
        return validation_results

# Utility Functions
def create_sample_asset(asset_type: AssetType, name: str, source_system: SourceSystem) -> MetadataAsset:
    """Create a sample metadata asset for testing"""
    return MetadataAsset(
        asset_id=str(uuid.uuid4()),
        asset_type=asset_type,
        source_system=source_system,
        technical_name=name,
        business_name=f"Business {name}",
        description=f"Sample {asset_type.value} asset",
        owner="system",
        business_context=BusinessContext(
            business_name=f"Business {name}",
            description=f"Business description for {name}",
            tags=["sample", asset_type.value]
        )
    )

def create_sample_config(source_env: str, target_env: str) -> SyncConfiguration:
    """Create a sample synchronization configuration"""
    return SyncConfiguration(
        config_id=str(uuid.uuid4()),
        source_environment=source_env,
        target_environment=target_env,
        sync_frequency=SyncFrequency.DAILY,
        priority_level=PriorityLevel.HIGH,
        conflict_resolution=ConflictStrategy.SOURCE_WINS,
        field_mappings={
            "technical_name": "name",
            "description": "description"
        }
    )

# Example usage and testing
if __name__ == "__main__":
    print("🔄 Metadata Synchronization Framework")
    print("=" * 40)
    
    # Create sync engine
    sync_engine = MetadataSyncEngine()
    
    # Create sample configuration
    config = create_sample_config("datasphere", "glue")
    sync_engine.register_configuration(config)
    
    # Create sample assets
    assets = [
        create_sample_asset(AssetType.ANALYTICAL_MODEL, "sales_model", SourceSystem.DATASPHERE),
        create_sample_asset(AssetType.TABLE, "customer_table", SourceSystem.DATASPHERE),
        create_sample_asset(AssetType.VIEW, "sales_view", SourceSystem.DATASPHERE)
    ]
    
    # Test priority ordering
    prioritized = sync_engine.get_priority_order(assets)
    print(f"\n📊 Priority Order:")
    for i, asset in enumerate(prioritized, 1):
        print(f"{i}. {asset.asset_type.value}: {asset.technical_name}")
    
    # Schedule sync
    result = sync_engine.schedule_sync(config.config_id)
    print(f"\n⏰ Scheduled Sync: {result}")
    
    # Validate configuration
    validation = sync_engine.validate_configuration(config)
    print(f"\n✅ Configuration Validation: {validation}")
    
    print(f"\n🎉 Core framework initialized successfully!")