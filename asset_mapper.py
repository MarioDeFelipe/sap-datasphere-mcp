#!/usr/bin/env python3
"""
Asset Mapping and Transformation Engine
Sophisticated mapping system for metadata synchronization between Datasphere and AWS Glue
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid

from metadata_sync_core import MetadataAsset, AssetType, SourceSystem, BusinessContext
from sync_logging import SyncLogger, EventType

class MappingRuleType(Enum):
    """Types of mapping rules"""
    FIELD_MAPPING = "field_mapping"
    VALUE_TRANSFORMATION = "value_transformation"
    CONDITIONAL_MAPPING = "conditional_mapping"
    BUSINESS_RULE = "business_rule"
    NAMING_CONVENTION = "naming_convention"

class ConflictResolutionStrategy(Enum):
    """Conflict resolution strategies"""
    SOURCE_WINS = "source_wins"
    TARGET_WINS = "target_wins"
    MERGE = "merge"
    MANUAL = "manual"
    CUSTOM_RULE = "custom_rule"

@dataclass
class MappingRule:
    """Individual mapping rule configuration"""
    rule_id: str
    rule_type: MappingRuleType
    source_field: str
    target_field: str
    transformation_logic: str
    conditions: Dict[str, Any] = field(default_factory=dict)
    priority: int = 100
    is_active: bool = True
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'rule_id': self.rule_id,
            'rule_type': self.rule_type.value,
            'source_field': self.source_field,
            'target_field': self.target_field,
            'transformation_logic': self.transformation_logic,
            'conditions': self.conditions,
            'priority': self.priority,
            'is_active': self.is_active,
            'description': self.description
        }

@dataclass
class NamingConvention:
    """Naming convention configuration"""
    convention_id: str
    pattern: str
    replacement: str
    asset_types: List[AssetType]
    environment_prefix: bool = True
    description: str = ""

@dataclass
class ConflictResolution:
    """Conflict resolution configuration"""
    conflict_id: str
    conflict_type: str
    strategy: ConflictResolutionStrategy
    custom_logic: Optional[str] = None
    priority_rules: Dict[str, int] = field(default_factory=dict)
    description: str = ""

@dataclass
class MappingProfile:
    """Complete mapping profile for asset transformation"""
    profile_id: str
    profile_name: str
    source_system: SourceSystem
    target_system: SourceSystem
    asset_type: AssetType
    mapping_rules: List[MappingRule] = field(default_factory=list)
    conflict_resolutions: List[ConflictResolution] = field(default_factory=list)
    naming_conventions: Dict[str, str] = field(default_factory=dict)
    is_active: bool = True
    created_date: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'profile_id': self.profile_id,
            'profile_name': self.profile_name,
            'source_system': self.source_system.value,
            'target_system': self.target_system.value,
            'asset_type': self.asset_type.value,
            'mapping_rules': [rule.to_dict() for rule in self.mapping_rules],
            'conflict_resolutions': [
                {
                    'conflict_id': cr.conflict_id,
                    'conflict_type': cr.conflict_type,
                    'strategy': cr.strategy.value,
                    'custom_logic': cr.custom_logic,
                    'priority_rules': cr.priority_rules,
                    'description': cr.description
                }
                for cr in self.conflict_resolutions
            ],
            'naming_conventions': self.naming_conventions,
            'is_active': self.is_active,
            'created_date': self.created_date.isoformat()
        }

@dataclass
class MappingResult:
    """Result of asset mapping operation"""
    success: bool
    mapped_asset: Optional[MetadataAsset]
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    applied_rules: List[str] = field(default_factory=list)
    execution_time_ms: Optional[int] = None
    error_message: Optional[str] = None

class AssetMapper:
    """Advanced asset mapping and transformation engine"""
    
    def __init__(self, environment: str = "default"):
        self.environment = environment
        self.logger = SyncLogger(f"asset_mapper_{environment}")
        
        # Mapping configurations
        self.mapping_rules: Dict[str, MappingRule] = {}
        self.naming_conventions: Dict[str, NamingConvention] = {}
        self.conflict_resolutions: Dict[str, ConflictResolution] = {}
        
        # Transformation functions registry
        self.transformation_functions: Dict[str, Callable] = {
            'uppercase': lambda x: str(x).upper(),
            'lowercase': lambda x: str(x).lower(),
            'title_case': lambda x: str(x).title(),
            'snake_case': self._to_snake_case,
            'camel_case': self._to_camel_case,
            'prefix': self._add_prefix,
            'suffix': self._add_suffix,
            'replace': self._replace_text,
            'truncate': self._truncate_text,
            'sanitize': self._sanitize_name,
            'datasphere_to_glue_name': self._datasphere_to_glue_name,
            'preserve_business_context': self._preserve_business_context
        }
        
        # Load default configurations
        self._load_default_configurations()
    
    def _load_default_configurations(self):
        """Load default mapping configurations"""
        
        # Default field mappings for Datasphere → Glue
        default_mappings = [
            MappingRule(
                rule_id="datasphere_space_to_database",
                rule_type=MappingRuleType.NAMING_CONVENTION,
                source_field="technical_name",
                target_field="database_name",
                transformation_logic="datasphere_to_glue_name",
                description="Map Datasphere space to Glue database with naming convention"
            ),
            MappingRule(
                rule_id="analytical_model_to_table",
                rule_type=MappingRuleType.FIELD_MAPPING,
                source_field="technical_name",
                target_field="table_name",
                transformation_logic="sanitize",
                conditions={"asset_type": "analytical_model"},
                description="Map analytical model name to Glue table name"
            ),
            MappingRule(
                rule_id="business_name_preservation",
                rule_type=MappingRuleType.BUSINESS_RULE,
                source_field="business_name",
                target_field="display_name",
                transformation_logic="preserve_business_context",
                description="Preserve business names and context"
            ),
            MappingRule(
                rule_id="dimensions_to_parameters",
                rule_type=MappingRuleType.VALUE_TRANSFORMATION,
                source_field="business_context.dimensions",
                target_field="parameters.dimensions",
                transformation_logic="join_with_comma",
                description="Convert dimensions list to comma-separated parameter"
            ),
            MappingRule(
                rule_id="measures_to_parameters",
                rule_type=MappingRuleType.VALUE_TRANSFORMATION,
                source_field="business_context.measures",
                target_field="parameters.measures",
                transformation_logic="join_with_comma",
                description="Convert measures list to comma-separated parameter"
            )
        ]
        
        for rule in default_mappings:
            self.mapping_rules[rule.rule_id] = rule
        
        # Default naming conventions
        default_naming = [
            NamingConvention(
                convention_id="datasphere_space_naming",
                pattern=r"^(.+)$",
                replacement=f"datasphere_\\1_{self.environment}",
                asset_types=[AssetType.SPACE],
                description="Add datasphere prefix and environment suffix to spaces"
            ),
            NamingConvention(
                convention_id="analytical_model_naming",
                pattern=r"^(.+)$",
                replacement="\\1_model",
                asset_types=[AssetType.ANALYTICAL_MODEL],
                description="Add model suffix to analytical models"
            )
        ]
        
        for convention in default_naming:
            self.naming_conventions[convention.convention_id] = convention
        
        # Default conflict resolutions
        default_conflicts = [
            ConflictResolution(
                conflict_id="schema_conflict",
                conflict_type="schema_mismatch",
                strategy=ConflictResolutionStrategy.SOURCE_WINS,
                description="Source system wins for schema conflicts"
            ),
            ConflictResolution(
                conflict_id="naming_conflict",
                conflict_type="name_collision",
                strategy=ConflictResolutionStrategy.CUSTOM_RULE,
                custom_logic="append_timestamp",
                description="Append timestamp for naming conflicts"
            )
        ]
        
        for conflict in default_conflicts:
            self.conflict_resolutions[conflict.conflict_id] = conflict
    
    def map_asset(self, source_asset: MetadataAsset, target_system: SourceSystem, 
                  profile_id: Optional[str] = None) -> MappingResult:
        """Map an asset from source to target system with all transformations"""
        
        start_time = datetime.now()
        result = MappingResult(success=True, mapped_asset=None)
        
        try:
            self.logger.log_event(
                event_type=EventType.ASSET_CREATED,
                source_system=source_asset.source_system.value,
                target_system=target_system.value,
                asset_id=source_asset.asset_id,
                asset_type=source_asset.asset_type.value,
                operation="map_asset",
                status="started",
                details={'source_asset': source_asset.technical_name}
            )
            
            # Create target asset as copy of source
            target_asset = self._create_target_asset_copy(source_asset, target_system)
            
            # Apply mapping rules in priority order
            sorted_rules = sorted(
                [rule for rule in self.mapping_rules.values() if rule.is_active],
                key=lambda r: r.priority
            )
            
            for rule in sorted_rules:
                if self._rule_applies_to_asset(rule, source_asset):
                    target_asset = self._apply_mapping_rule(rule, source_asset, target_asset)
                    result.applied_rules.append(rule.rule_id)
            
            # Apply naming conventions
            target_asset = self._apply_naming_conventions(target_asset)
            
            # Validate and resolve conflicts
            target_asset = self._resolve_conflicts(source_asset, target_asset)
            
            # Set the mapped asset in result
            result.mapped_asset = target_asset
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            result.execution_time_ms = int(execution_time)
            
            self.logger.log_event(
                event_type=EventType.ASSET_CREATED,
                source_system=source_asset.source_system.value,
                target_system=target_system.value,
                asset_id=target_asset.asset_id,
                asset_type=target_asset.asset_type.value,
                operation="map_asset",
                status="completed",
                details={
                    'source_asset': source_asset.technical_name,
                    'target_asset': target_asset.technical_name,
                    'rules_applied': len(result.applied_rules),
                    'execution_time_ms': result.execution_time_ms
                }
            )
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            self.logger.log_event(
                event_type=EventType.ERROR_OCCURRED,
                source_system=source_asset.source_system.value,
                target_system=target_system.value,
                asset_id=source_asset.asset_id,
                operation="map_asset",
                status="failed",
                details={},
                error_message=str(e)
            )
            
            return MappingResult(
                success=False,
                mapped_asset=None,
                error_message=str(e),
                execution_time_ms=int(execution_time)
            )
    
    def _create_target_asset_copy(self, source_asset: MetadataAsset, target_system: SourceSystem) -> MetadataAsset:
        """Create a copy of source asset for target system"""
        
        # Generate new asset ID for target system
        target_asset_id = f"{target_system.value}_{source_asset.asset_type.value}_{uuid.uuid4().hex[:8]}"
        
        # Create copy with target system
        target_asset = MetadataAsset(
            asset_id=target_asset_id,
            asset_type=source_asset.asset_type,
            source_system=target_system,
            technical_name=source_asset.technical_name,
            business_name=source_asset.business_name,
            description=source_asset.description,
            owner=source_asset.owner,
            created_date=datetime.now(),
            modified_date=datetime.now(),
            business_context=BusinessContext(
                business_name=source_asset.business_context.business_name,
                description=source_asset.business_context.description,
                owner=source_asset.business_context.owner,
                steward=source_asset.business_context.steward,
                certification_status=source_asset.business_context.certification_status,
                tags=source_asset.business_context.tags.copy(),
                dimensions=source_asset.business_context.dimensions.copy(),
                measures=source_asset.business_context.measures.copy(),
                hierarchies=source_asset.business_context.hierarchies.copy()
            ),
            schema_info=source_asset.schema_info.copy(),
            custom_properties=source_asset.custom_properties.copy()
        )
        
        # Add mapping metadata
        target_asset.custom_properties.update({
            'mapped_from_system': source_asset.source_system.value,
            'mapped_from_asset_id': source_asset.asset_id,
            'mapping_timestamp': datetime.now().isoformat(),
            'mapping_environment': self.environment
        })
        
        return target_asset
    
    def _rule_applies_to_asset(self, rule: MappingRule, asset: MetadataAsset) -> bool:
        """Check if a mapping rule applies to the given asset"""
        
        # Check asset type condition
        if 'asset_type' in rule.conditions:
            if asset.asset_type.value != rule.conditions['asset_type']:
                return False
        
        # Check source system condition
        if 'source_system' in rule.conditions:
            if asset.source_system.value != rule.conditions['source_system']:
                return False
        
        # Check field existence condition
        if 'requires_field' in rule.conditions:
            field_path = rule.conditions['requires_field']
            if not self._has_field(asset, field_path):
                return False
        
        return True
    
    def _apply_mapping_rule(self, rule: MappingRule, source_asset: MetadataAsset, target_asset: MetadataAsset) -> MetadataAsset:
        """Apply a specific mapping rule to transform the asset"""
        
        try:
            # Get source value
            source_value = self._get_field_value(source_asset, rule.source_field)
            
            if source_value is None:
                return target_asset
            
            # Apply transformation
            transformed_value = self._apply_transformation(
                source_value, 
                rule.transformation_logic, 
                rule.conditions
            )
            
            # Set target value
            self._set_field_value(target_asset, rule.target_field, transformed_value)
            
            return target_asset
            
        except Exception as e:
            self.logger.logger.warning(f"Failed to apply rule {rule.rule_id}: {str(e)}")
            return target_asset
    
    def _get_field_value(self, asset: MetadataAsset, field_path: str) -> Any:
        """Get value from asset using dot notation field path"""
        
        try:
            obj = asset
            for part in field_path.split('.'):
                if hasattr(obj, part):
                    obj = getattr(obj, part)
                elif isinstance(obj, dict) and part in obj:
                    obj = obj[part]
                else:
                    return None
            return obj
        except Exception:
            return None
    
    def _set_field_value(self, asset: MetadataAsset, field_path: str, value: Any):
        """Set value in asset using dot notation field path"""
        
        try:
            parts = field_path.split('.')
            obj = asset
            
            # Navigate to parent object
            for part in parts[:-1]:
                if hasattr(obj, part):
                    obj = getattr(obj, part)
                elif isinstance(obj, dict):
                    if part not in obj:
                        obj[part] = {}
                    obj = obj[part]
                else:
                    return
            
            # Set final value
            final_part = parts[-1]
            if hasattr(obj, final_part):
                setattr(obj, final_part, value)
            elif isinstance(obj, dict):
                obj[final_part] = value
                
        except Exception as e:
            self.logger.logger.warning(f"Failed to set field {field_path}: {str(e)}")
    
    def _has_field(self, asset: MetadataAsset, field_path: str) -> bool:
        """Check if asset has the specified field"""
        return self._get_field_value(asset, field_path) is not None
    
    def _apply_transformation(self, value: Any, transformation_logic: str, conditions: Dict[str, Any] = None) -> Any:
        """Apply transformation logic to a value"""
        
        if conditions is None:
            conditions = {}
        
        # Handle built-in transformations
        if transformation_logic in self.transformation_functions:
            func = self.transformation_functions[transformation_logic]
            
            # Pass conditions as parameters for some functions
            if transformation_logic in ['prefix', 'suffix', 'replace', 'truncate']:
                return func(value, conditions)
            else:
                return func(value)
        
        # Handle custom transformation logic
        elif transformation_logic.startswith('custom:'):
            return self._apply_custom_transformation(value, transformation_logic[7:], conditions)
        
        # Handle conditional transformations
        elif transformation_logic.startswith('if:'):
            return self._apply_conditional_transformation(value, transformation_logic[3:], conditions)
        
        # Handle join operations
        elif transformation_logic == 'join_with_comma':
            if isinstance(value, list):
                return ','.join(str(item) for item in value)
            return str(value)
        
        # Default: return value as string
        return str(value) if value is not None else ""    
# Transformation functions
    def _to_snake_case(self, text: str) -> str:
        """Convert text to snake_case"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', str(text))
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def _to_camel_case(self, text: str) -> str:
        """Convert text to camelCase"""
        components = str(text).split('_')
        return components[0].lower() + ''.join(x.title() for x in components[1:])
    
    def _add_prefix(self, text: str, conditions: Dict[str, Any]) -> str:
        """Add prefix to text"""
        prefix = conditions.get('prefix', 'prefix_')
        return f"{prefix}{text}"
    
    def _add_suffix(self, text: str, conditions: Dict[str, Any]) -> str:
        """Add suffix to text"""
        suffix = conditions.get('suffix', '_suffix')
        return f"{text}{suffix}"
    
    def _replace_text(self, text: str, conditions: Dict[str, Any]) -> str:
        """Replace text based on conditions"""
        find = conditions.get('find', '')
        replace = conditions.get('replace', '')
        return str(text).replace(find, replace)
    
    def _truncate_text(self, text: str, conditions: Dict[str, Any]) -> str:
        """Truncate text to specified length"""
        max_length = conditions.get('max_length', 50)
        text_str = str(text)
        return text_str[:max_length] if len(text_str) > max_length else text_str
    
    def _sanitize_name(self, text: str) -> str:
        """Sanitize name for AWS Glue compatibility"""
        # Remove special characters, keep alphanumeric and underscores
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', str(text))
        # Remove multiple consecutive underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        # Remove leading/trailing underscores
        sanitized = sanitized.strip('_')
        # Ensure it starts with a letter
        if sanitized and not sanitized[0].isalpha():
            sanitized = f"table_{sanitized}"
        return sanitized.lower()
    
    def _datasphere_to_glue_name(self, text: str) -> str:
        """Convert Datasphere name to Glue-compatible name"""
        # Apply sanitization and add environment prefix
        sanitized = self._sanitize_name(text)
        return f"datasphere_{sanitized}_{self.environment}"
    
    def _preserve_business_context(self, text: str) -> str:
        """Preserve business context in transformation"""
        # Keep business names readable
        return str(text) if text else ""
    
    def _apply_custom_transformation(self, value: Any, logic: str, conditions: Dict[str, Any]) -> Any:
        """Apply custom transformation logic"""
        # This can be extended to support custom Python expressions
        # For now, return the value as-is
        self.logger.logger.warning(f"Custom transformation not implemented: {logic}")
        return value
    
    def _apply_conditional_transformation(self, value: Any, logic: str, conditions: Dict[str, Any]) -> Any:
        """Apply conditional transformation logic"""
        # Parse conditional logic (simplified implementation)
        # Format: "condition:true_value:false_value"
        parts = logic.split(':')
        if len(parts) >= 3:
            condition = parts[0]
            true_value = parts[1]
            false_value = parts[2]
            
            # Simple condition evaluation
            if condition == 'not_empty' and value:
                return true_value
            else:
                return false_value
        
        return value
    
    def _apply_naming_conventions(self, asset: MetadataAsset) -> MetadataAsset:
        """Apply naming conventions to the asset"""
        
        for convention in self.naming_conventions.values():
            if asset.asset_type in convention.asset_types:
                # Apply naming convention to technical name
                new_name = re.sub(convention.pattern, convention.replacement, asset.technical_name)
                
                # Add environment prefix if configured
                if convention.environment_prefix and not new_name.startswith(f"datasphere_{self.environment}"):
                    new_name = f"datasphere_{new_name}_{self.environment}"
                
                asset.technical_name = new_name
                
                # Update asset ID to reflect new name
                asset.asset_id = f"{asset.source_system.value}_{asset.asset_type.value}_{new_name}"
        
        return asset
    
    def _resolve_conflicts(self, source_asset: MetadataAsset, target_asset: MetadataAsset) -> MetadataAsset:
        """Resolve any conflicts in the mapped asset"""
        
        # Check for naming conflicts
        if self._has_naming_conflict(target_asset):
            target_asset = self._resolve_naming_conflict(target_asset)
        
        # Check for schema conflicts
        if self._has_schema_conflict(source_asset, target_asset):
            target_asset = self._resolve_schema_conflict(source_asset, target_asset)
        
        return target_asset
    
    def _has_naming_conflict(self, asset: MetadataAsset) -> bool:
        """Check if asset has naming conflicts"""
        # This would typically check against existing assets in target system
        # For now, return False (no conflicts)
        return False
    
    def _resolve_naming_conflict(self, asset: MetadataAsset) -> MetadataAsset:
        """Resolve naming conflicts"""
        # Append timestamp to make name unique
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        asset.technical_name = f"{asset.technical_name}_{timestamp}"
        asset.asset_id = f"{asset.source_system.value}_{asset.asset_type.value}_{asset.technical_name}"
        return asset
    
    def _has_schema_conflict(self, source_asset: MetadataAsset, target_asset: MetadataAsset) -> bool:
        """Check if there are schema conflicts"""
        # This would typically validate schema compatibility
        # For now, return False (no conflicts)
        return False
    
    def _resolve_schema_conflict(self, source_asset: MetadataAsset, target_asset: MetadataAsset) -> MetadataAsset:
        """Resolve schema conflicts"""
        # Apply source wins strategy by default
        target_asset.schema_info = source_asset.schema_info.copy()
        return target_asset
    
    # Configuration management methods
    def add_mapping_rule(self, rule: MappingRule) -> bool:
        """Add a new mapping rule"""
        try:
            self.mapping_rules[rule.rule_id] = rule
            
            self.logger.log_event(
                event_type=EventType.CONFIGURATION_CHANGED,
                source_system=self.environment,
                operation="add_mapping_rule",
                status="completed",
                details={
                    'rule_id': rule.rule_id,
                    'rule_type': rule.rule_type.value,
                    'source_field': rule.source_field,
                    'target_field': rule.target_field
                }
            )
            
            return True
        except Exception as e:
            self.logger.logger.error(f"Failed to add mapping rule {rule.rule_id}: {str(e)}")
            return False
    
    def remove_mapping_rule(self, rule_id: str) -> bool:
        """Remove a mapping rule"""
        try:
            if rule_id in self.mapping_rules:
                del self.mapping_rules[rule_id]
                
                self.logger.log_event(
                    event_type=EventType.CONFIGURATION_CHANGED,
                    source_system=self.environment,
                    operation="remove_mapping_rule",
                    status="completed",
                    details={'rule_id': rule_id}
                )
                
                return True
            return False
        except Exception as e:
            self.logger.logger.error(f"Failed to remove mapping rule {rule_id}: {str(e)}")
            return False
    
    def get_mapping_rules(self) -> List[Dict[str, Any]]:
        """Get all mapping rules as dictionaries"""
        return [rule.to_dict() for rule in self.mapping_rules.values()]
    
    def validate_mapping_configuration(self) -> Dict[str, Any]:
        """Validate the current mapping configuration"""
        
        errors = []
        warnings = []
        
        # Validate each rule
        for rule in self.mapping_rules.values():
            if not rule.source_field or not rule.target_field:
                errors.append(f"Rule {rule.rule_id}: Missing source or target field")
            
            if not rule.transformation_logic:
                warnings.append(f"Rule {rule.rule_id}: No transformation logic specified")
        
        # Create issues list combining errors and warnings
        issues = []
        issues.extend([{'severity': 'error', 'message': error} for error in errors])
        issues.extend([{'severity': 'warning', 'message': warning} for warning in warnings])
        
        # Create summary by severity
        summary = {
            'error': len(errors),
            'warning': len(warnings),
            'info': 0,
            'critical': 0
        }
        
        validation_results = {
            'is_valid': len(errors) == 0,
            'total_rules': len(self.mapping_rules),
            'active_rules': len([r for r in self.mapping_rules.values() if r.is_active]),
            'issues': issues,
            'summary': summary,
            'errors': errors,
            'warnings': warnings
        }
        
        return validation_results
    
    def export_configuration(self, filename: str = None) -> str:
        """Export mapping configuration to JSON file"""
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'asset_mapping_config_{self.environment}_{timestamp}.json'
        
        config_data = {
            'environment': self.environment,
            'export_timestamp': datetime.now().isoformat(),
            'mapping_rules': [rule.to_dict() for rule in self.mapping_rules.values()],
            'naming_conventions': [
                {
                    'convention_id': conv.convention_id,
                    'pattern': conv.pattern,
                    'replacement': conv.replacement,
                    'asset_types': [at.value for at in conv.asset_types],
                    'environment_prefix': conv.environment_prefix,
                    'description': conv.description
                }
                for conv in self.naming_conventions.values()
            ],
            'conflict_resolutions': [
                {
                    'conflict_id': conf.conflict_id,
                    'conflict_type': conf.conflict_type,
                    'strategy': conf.strategy.value,
                    'custom_logic': conf.custom_logic,
                    'priority_rules': conf.priority_rules,
                    'description': conf.description
                }
                for conf in self.conflict_resolutions.values()
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        self.logger.logger.info(f"Exported mapping configuration to {filename}")
        return filename
    
    def import_configuration(self, filename: str) -> bool:
        """Import mapping configuration from JSON file"""
        
        try:
            with open(filename, 'r') as f:
                config_data = json.load(f)
            
            # Import mapping rules
            for rule_data in config_data.get('mapping_rules', []):
                rule = MappingRule(
                    rule_id=rule_data['rule_id'],
                    rule_type=MappingRuleType(rule_data['rule_type']),
                    source_field=rule_data['source_field'],
                    target_field=rule_data['target_field'],
                    transformation_logic=rule_data['transformation_logic'],
                    conditions=rule_data.get('conditions', {}),
                    priority=rule_data.get('priority', 100),
                    is_active=rule_data.get('is_active', True),
                    description=rule_data.get('description', '')
                )
                self.mapping_rules[rule.rule_id] = rule
            
            # Import naming conventions
            for conv_data in config_data.get('naming_conventions', []):
                convention = NamingConvention(
                    convention_id=conv_data['convention_id'],
                    pattern=conv_data['pattern'],
                    replacement=conv_data['replacement'],
                    asset_types=[AssetType(at) for at in conv_data['asset_types']],
                    environment_prefix=conv_data.get('environment_prefix', True),
                    description=conv_data.get('description', '')
                )
                self.naming_conventions[convention.convention_id] = convention
            
            # Import conflict resolutions
            for conf_data in config_data.get('conflict_resolutions', []):
                conflict = ConflictResolution(
                    conflict_id=conf_data['conflict_id'],
                    conflict_type=conf_data['conflict_type'],
                    strategy=ConflictResolutionStrategy(conf_data['strategy']),
                    custom_logic=conf_data.get('custom_logic'),
                    priority_rules=conf_data.get('priority_rules', {}),
                    description=conf_data.get('description', '')
                )
                self.conflict_resolutions[conflict.conflict_id] = conflict
            
            self.logger.log_event(
                event_type=EventType.CONFIGURATION_CHANGED,
                source_system=self.environment,
                operation="import_configuration",
                status="completed",
                details={
                    'filename': filename,
                    'rules_imported': len(config_data.get('mapping_rules', [])),
                    'conventions_imported': len(config_data.get('naming_conventions', [])),
                    'conflicts_imported': len(config_data.get('conflict_resolutions', []))
                }
            )
            
            return True
            
        except Exception as e:
            self.logger.logger.error(f"Failed to import configuration from {filename}: {str(e)}")
            return False

# Factory function
def create_asset_mapper(environment: str = "default") -> AssetMapper:
    """Create an asset mapper for the specified environment"""
    return AssetMapper(environment)

# Example usage and testing
if __name__ == "__main__":
    print("🔧 Asset Mapping and Transformation Engine")
    print("=" * 43)
    
    # Create mapper
    mapper = create_asset_mapper("test")
    
    # Validate configuration
    validation = mapper.validate_mapping_configuration()
    print(f"📊 Configuration Validation: {validation}")
    
    # Export configuration
    config_file = mapper.export_configuration()
    print(f"📄 Configuration exported to: {config_file}")
    
    print(f"\n🎉 Asset mapper initialized successfully!")

    def add_mapping_rule(self, rule: MappingRule) -> bool:
        """Add a mapping rule to the configuration"""
        try:
            self.mapping_rules[rule.rule_id] = rule
            
            self.logger.log_event(
                event_type=EventType.CONFIGURATION_CHANGED,
                source_system="asset_mapper",
                operation="add_mapping_rule",
                status="completed",
                details={
                    'rule_id': rule.rule_id,
                    'rule_type': rule.rule_type.value,
                    'source_field': rule.source_field,
                    'target_field': rule.target_field
                }
            )
            
            return True
        except Exception as e:
            self.logger.logger.error(f"Failed to add mapping rule {rule.rule_id}: {str(e)}")
            return False
    
    def get_mapping_rules(self) -> List[Dict[str, Any]]:
        """Get all mapping rules as dictionaries"""
        return [rule.to_dict() for rule in self.mapping_rules.values()]
    
    def _has_schema_conflict(self, source_asset: MetadataAsset, target_asset: MetadataAsset) -> bool:
        """Check if there's a schema conflict between assets"""
        if not source_asset.schema_info or not target_asset.schema_info:
            return False
        
        source_columns = source_asset.schema_info.get('columns', [])
        target_columns = target_asset.schema_info.get('columns', [])
        
        # Check for column count mismatch
        if len(source_columns) != len(target_columns):
            return True
        
        # Check for column type mismatches
        for src_col, tgt_col in zip(source_columns, target_columns):
            if src_col.get('type') != tgt_col.get('type'):
                return True
        
        return False
    
    def _resolve_schema_conflict(self, source_asset: MetadataAsset, target_asset: MetadataAsset) -> MetadataAsset:
        """Resolve schema conflict using source-wins strategy"""
        # Apply source-wins strategy - use source schema
        if source_asset.schema_info:
            target_asset.schema_info = source_asset.schema_info.copy()
        
        return target_asset
    
    def _resolve_naming_conflict(self, asset: MetadataAsset) -> MetadataAsset:
        """Resolve naming conflicts by applying custom logic"""
        # Check if there's a custom conflict resolution for naming
        for conflict in self.conflict_resolutions.values():
            if conflict.conflict_type == "naming_conflict" and conflict.strategy == ConflictResolutionStrategy.CUSTOM_RULE:
                if conflict.custom_logic == "append_timestamp":
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    asset.technical_name = f"{asset.technical_name}_{timestamp}"
                break
        
        return asset

# Example usage and testing
if __name__ == "__main__":
    print("🔧 Asset Mapping and Transformation Engine")
    print("=" * 43)
    
    # Create asset mapper
    mapper = AssetMapper("test")
    
    # Show configuration summary
    rules = mapper.get_mapping_rules()
    print(f"📊 Configuration Summary:")
    print(f"  • Mapping Rules: {len(rules)}")
    print(f"  • Naming Conventions: {len(mapper.naming_conventions)}")
    print(f"  • Conflict Resolutions: {len(mapper.conflict_resolutions)}")
    
    # Validate configuration
    validation = mapper.validate_mapping_configuration()
    print(f"\n✅ Configuration Validation:")
    print(f"  • Valid: {validation['is_valid']}")
    print(f"  • Active Rules: {validation['active_rules']}")
    print(f"  • Errors: {len(validation['errors'])}")
    print(f"  • Warnings: {len(validation['warnings'])}")
    
    print(f"\n🎉 Asset mapper initialized successfully!")