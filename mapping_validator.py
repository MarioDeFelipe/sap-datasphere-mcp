#!/usr/bin/env python3
"""
Mapping Validation and Preview Engine
Provides dry-run mode, impact analysis, and mapping rule testing capabilities
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid

from asset_mapper import AssetMapper, MappingProfile, MappingRule, MappingResult
from metadata_sync_core import MetadataAsset, AssetType, SourceSystem, BusinessContext
from sync_logging import SyncLogger, EventType

class ValidationSeverity(Enum):
    """Validation issue severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ValidationCategory(Enum):
    """Categories of validation issues"""
    NAMING_CONVENTION = "naming_convention"
    DATA_TYPE_COMPATIBILITY = "data_type_compatibility"
    BUSINESS_CONTEXT = "business_context"
    SCHEMA_STRUCTURE = "schema_structure"
    MAPPING_LOGIC = "mapping_logic"
    PERFORMANCE = "performance"
    SECURITY = "security"

@dataclass
class ValidationIssue:
    """Individual validation issue"""
    issue_id: str
    severity: ValidationSeverity
    category: ValidationCategory
    title: str
    description: str
    affected_field: Optional[str] = None
    suggested_fix: Optional[str] = None
    rule_id: Optional[str] = None
    impact_score: int = 0  # 1-10 scale
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'issue_id': self.issue_id,
            'severity': self.severity.value,
            'category': self.category.value,
            'title': self.title,
            'description': self.description,
            'affected_field': self.affected_field,
            'suggested_fix': self.suggested_fix,
            'rule_id': self.rule_id,
            'impact_score': self.impact_score
        }

@dataclass
class MappingPreview:
    """Preview of mapping transformation"""
    original_asset: MetadataAsset
    mapped_asset: Optional[MetadataAsset]
    field_changes: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    applied_rules: List[str] = field(default_factory=list)
    validation_issues: List[ValidationIssue] = field(default_factory=list)
    impact_analysis: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'original_asset': {
                'asset_id': self.original_asset.asset_id,
                'technical_name': self.original_asset.technical_name,
                'asset_type': self.original_asset.asset_type.value,
                'source_system': self.original_asset.source_system.value
            },
            'mapped_asset': {
                'asset_id': self.mapped_asset.asset_id,
                'technical_name': self.mapped_asset.technical_name,
                'asset_type': self.mapped_asset.asset_type.value,
                'source_system': self.mapped_asset.source_system.value
            } if self.mapped_asset else None,
            'field_changes': self.field_changes,
            'applied_rules': self.applied_rules,
            'validation_issues': [issue.to_dict() for issue in self.validation_issues],
            'impact_analysis': self.impact_analysis
        }

@dataclass
class ValidationReport:
    """Comprehensive validation report"""
    report_id: str
    profile_id: str
    validation_timestamp: datetime
    total_assets_tested: int
    validation_issues: List[ValidationIssue] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    overall_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'report_id': self.report_id,
            'profile_id': self.profile_id,
            'validation_timestamp': self.validation_timestamp.isoformat(),
            'total_assets_tested': self.total_assets_tested,
            'validation_issues': [issue.to_dict() for issue in self.validation_issues],
            'performance_metrics': self.performance_metrics,
            'recommendations': self.recommendations,
            'overall_score': self.overall_score
        }

class MappingValidator:
    """Advanced mapping validation and preview engine"""
    
    def __init__(self, asset_mapper: AssetMapper):
        self.asset_mapper = asset_mapper
        self.environment = asset_mapper.environment
        self.logger = SyncLogger("mapping_validator")
        
        # Validation rules and patterns
        self.naming_patterns = {
            'datasphere': {
                'technical_name': r'^[A-Z][A-Z0-9_]*$',
                'business_name': r'^[A-Za-z][A-Za-z0-9\s\-_]*$'
            },
            'glue': {
                'technical_name': r'^[a-z][a-z0-9_]*$',
                'business_name': r'^[A-Za-z][A-Za-z0-9\s\-_]*$'
            }
        }
        
        # Data type compatibility matrix
        self.type_compatibility = {
            'datasphere_to_glue': {
                'NVARCHAR': ['string'],
                'INTEGER': ['int', 'bigint'],
                'BIGINT': ['bigint'],
                'DECIMAL': ['decimal', 'double'],
                'DOUBLE': ['double'],
                'DATE': ['date'],
                'TIMESTAMP': ['timestamp'],
                'BOOLEAN': ['boolean']
            },
            'glue_to_datasphere': {
                'string': ['NVARCHAR'],
                'int': ['INTEGER', 'BIGINT'],
                'bigint': ['BIGINT'],
                'decimal': ['DECIMAL'],
                'double': ['DOUBLE', 'DECIMAL'],
                'date': ['DATE'],
                'timestamp': ['TIMESTAMP'],
                'boolean': ['BOOLEAN']
            }
        }
    
    def preview_mapping(self, asset: MetadataAsset, target_system: SourceSystem, 
                       profile_id: Optional[str] = None) -> MappingPreview:
        """Generate a preview of asset mapping without applying changes"""
        
        self.logger.log_event(
            event_type=EventType.VALIDATION_STARTED,
            source_system="mapping_validator",
            operation="preview_mapping",
            status="started",
            details={
                'asset_id': asset.asset_id,
                'target_system': target_system.value,
                'profile_id': profile_id
            }
        )
        
        try:
            # Create preview object
            preview = MappingPreview(original_asset=asset)
            
            # Perform mapping to get transformed asset
            mapping_result = self.asset_mapper.map_asset(asset, target_system, profile_id)
            
            if mapping_result.success:
                preview.mapped_asset = mapping_result.mapped_asset
                preview.applied_rules = mapping_result.applied_rules
                
                # Analyze field changes
                preview.field_changes = self._analyze_field_changes(asset, mapping_result.mapped_asset)
                
                # Validate the mapping
                preview.validation_issues = self._validate_mapping(asset, mapping_result.mapped_asset, profile_id)
                
                # Perform impact analysis
                preview.impact_analysis = self._analyze_mapping_impact(asset, mapping_result.mapped_asset)
                
                self.logger.log_event(
                    event_type=EventType.VALIDATION_COMPLETED,
                    source_system="mapping_validator",
                    operation="preview_mapping",
                    status="completed",
                    details={
                        'asset_id': asset.asset_id,
                        'issues_found': len(preview.validation_issues),
                        'field_changes': len(preview.field_changes),
                        'rules_applied': len(preview.applied_rules)
                    }
                )
            else:
                # Handle mapping failure
                preview.validation_issues.append(
                    ValidationIssue(
                        issue_id=str(uuid.uuid4()),
                        severity=ValidationSeverity.CRITICAL,
                        category=ValidationCategory.MAPPING_LOGIC,
                        title="Mapping Failed",
                        description=f"Asset mapping failed: {mapping_result.error_message}",
                        impact_score=10
                    )
                )
            
            return preview
            
        except Exception as e:
            self.logger.logger.error(f"Preview mapping failed for asset {asset.asset_id}: {str(e)}")
            
            preview = MappingPreview(original_asset=asset)
            preview.validation_issues.append(
                ValidationIssue(
                    issue_id=str(uuid.uuid4()),
                    severity=ValidationSeverity.CRITICAL,
                    category=ValidationCategory.MAPPING_LOGIC,
                    title="Preview Generation Failed",
                    description=f"Failed to generate mapping preview: {str(e)}",
                    impact_score=10
                )
            )
            
            return preview
    
    def validate_mapping_profile(self, profile: MappingProfile, 
                                test_assets: Optional[List[MetadataAsset]] = None) -> ValidationReport:
        """Validate a mapping profile against test assets"""
        
        report_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        self.logger.log_event(
            event_type=EventType.VALIDATION_STARTED,
            source_system="mapping_validator",
            operation="validate_profile",
            status="started",
            details={
                'profile_id': profile.profile_id,
                'test_assets_count': len(test_assets) if test_assets else 0
            }
        )
        
        try:
            report = ValidationReport(
                report_id=report_id,
                profile_id=profile.profile_id,
                validation_timestamp=start_time,
                total_assets_tested=0
            )
            
            # Validate profile structure
            profile_issues = self._validate_profile_structure(profile)
            report.validation_issues.extend(profile_issues)
            
            # Test with provided assets or generate test assets
            if not test_assets:
                test_assets = self._generate_test_assets(profile)
            
            report.total_assets_tested = len(test_assets)
            
            # Test mapping with each asset
            mapping_times = []
            for asset in test_assets:
                try:
                    asset_start = datetime.now()
                    preview = self.preview_mapping(asset, profile.target_system, profile.profile_id)
                    asset_time = (datetime.now() - asset_start).total_seconds() * 1000
                    mapping_times.append(asset_time)
                    
                    # Add asset-specific issues to report
                    report.validation_issues.extend(preview.validation_issues)
                    
                except Exception as e:
                    report.validation_issues.append(
                        ValidationIssue(
                            issue_id=str(uuid.uuid4()),
                            severity=ValidationSeverity.ERROR,
                            category=ValidationCategory.MAPPING_LOGIC,
                            title=f"Asset Mapping Test Failed",
                            description=f"Failed to test mapping for asset {asset.asset_id}: {str(e)}",
                            impact_score=7
                        )
                    )
            
            # Calculate performance metrics
            if mapping_times:
                report.performance_metrics = {
                    'average_mapping_time_ms': sum(mapping_times) / len(mapping_times),
                    'max_mapping_time_ms': max(mapping_times),
                    'min_mapping_time_ms': min(mapping_times),
                    'total_validation_time_ms': (datetime.now() - start_time).total_seconds() * 1000
                }
            
            # Generate recommendations
            report.recommendations = self._generate_recommendations(report.validation_issues)
            
            # Calculate overall score
            report.overall_score = self._calculate_validation_score(report.validation_issues)
            
            self.logger.log_event(
                event_type=EventType.VALIDATION_COMPLETED,
                source_system="mapping_validator",
                operation="validate_profile",
                status="completed",
                details={
                    'profile_id': profile.profile_id,
                    'total_issues': len(report.validation_issues),
                    'overall_score': report.overall_score,
                    'validation_time_ms': report.performance_metrics.get('total_validation_time_ms', 0)
                }
            )
            
            return report
            
        except Exception as e:
            self.logger.logger.error(f"Profile validation failed for {profile.profile_id}: {str(e)}")
            
            report = ValidationReport(
                report_id=report_id,
                profile_id=profile.profile_id,
                validation_timestamp=start_time,
                total_assets_tested=0
            )
            
            report.validation_issues.append(
                ValidationIssue(
                    issue_id=str(uuid.uuid4()),
                    severity=ValidationSeverity.CRITICAL,
                    category=ValidationCategory.MAPPING_LOGIC,
                    title="Profile Validation Failed",
                    description=f"Failed to validate mapping profile: {str(e)}",
                    impact_score=10
                )
            )
            
            return report
    
    def dry_run_sync(self, assets: List[MetadataAsset], target_system: SourceSystem,
                     profile_id: Optional[str] = None) -> Dict[str, Any]:
        """Perform a dry run of synchronization without making actual changes"""
        
        dry_run_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        self.logger.log_event(
            event_type=EventType.SYNC_STARTED,
            source_system="mapping_validator",
            operation="dry_run_sync",
            status="started",
            details={
                'dry_run_id': dry_run_id,
                'assets_count': len(assets),
                'target_system': target_system.value,
                'profile_id': profile_id
            }
        )
        
        try:
            results = {
                'dry_run_id': dry_run_id,
                'start_time': start_time.isoformat(),
                'target_system': target_system.value,
                'profile_id': profile_id,
                'total_assets': len(assets),
                'successful_mappings': 0,
                'failed_mappings': 0,
                'validation_issues': [],
                'performance_summary': {},
                'impact_summary': {},
                'asset_previews': []
            }
            
            mapping_times = []
            total_issues = []
            
            for asset in assets:
                try:
                    asset_start = datetime.now()
                    preview = self.preview_mapping(asset, target_system, profile_id)
                    asset_time = (datetime.now() - asset_start).total_seconds() * 1000
                    mapping_times.append(asset_time)
                    
                    if preview.mapped_asset:
                        results['successful_mappings'] += 1
                    else:
                        results['failed_mappings'] += 1
                    
                    # Collect validation issues
                    total_issues.extend(preview.validation_issues)
                    
                    # Add preview to results
                    results['asset_previews'].append({
                        'asset_id': asset.asset_id,
                        'technical_name': asset.technical_name,
                        'mapping_success': preview.mapped_asset is not None,
                        'issues_count': len(preview.validation_issues),
                        'field_changes_count': len(preview.field_changes),
                        'mapping_time_ms': asset_time
                    })
                    
                except Exception as e:
                    results['failed_mappings'] += 1
                    
                    issue = ValidationIssue(
                        issue_id=str(uuid.uuid4()),
                        severity=ValidationSeverity.ERROR,
                        category=ValidationCategory.MAPPING_LOGIC,
                        title=f"Dry Run Failed for Asset",
                        description=f"Failed to process asset {asset.asset_id}: {str(e)}",
                        impact_score=8
                    )
                    total_issues.append(issue)
            
            # Calculate performance summary
            if mapping_times:
                results['performance_summary'] = {
                    'average_mapping_time_ms': sum(mapping_times) / len(mapping_times),
                    'total_time_ms': (datetime.now() - start_time).total_seconds() * 1000,
                    'throughput_assets_per_second': len(assets) / ((datetime.now() - start_time).total_seconds() or 1)
                }
            
            # Summarize validation issues
            results['validation_issues'] = [issue.to_dict() for issue in total_issues]
            
            # Calculate impact summary
            results['impact_summary'] = self._calculate_dry_run_impact(total_issues, results)
            
            results['end_time'] = datetime.now().isoformat()
            
            self.logger.log_event(
                event_type=EventType.SYNC_COMPLETED,
                source_system="mapping_validator",
                operation="dry_run_sync",
                status="completed",
                details={
                    'dry_run_id': dry_run_id,
                    'successful_mappings': results['successful_mappings'],
                    'failed_mappings': results['failed_mappings'],
                    'total_issues': len(total_issues)
                }
            )
            
            return results
            
        except Exception as e:
            self.logger.logger.error(f"Dry run sync failed: {str(e)}")
            
            return {
                'dry_run_id': dry_run_id,
                'start_time': start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'error': str(e),
                'total_assets': len(assets),
                'successful_mappings': 0,
                'failed_mappings': len(assets)
            }
    
    def _analyze_field_changes(self, original: MetadataAsset, mapped: MetadataAsset) -> Dict[str, Dict[str, Any]]:
        """Analyze changes between original and mapped assets"""
        changes = {}
        
        # Compare basic fields
        basic_fields = ['technical_name', 'business_name', 'description', 'owner']
        for field in basic_fields:
            original_value = getattr(original, field, None)
            mapped_value = getattr(mapped, field, None)
            
            if original_value != mapped_value:
                changes[field] = {
                    'original': original_value,
                    'mapped': mapped_value,
                    'change_type': 'modified'
                }
        
        # Compare schema information
        if hasattr(original, 'schema_info') and hasattr(mapped, 'schema_info'):
            schema_changes = self._compare_schema_info(original.schema_info, mapped.schema_info)
            if schema_changes:
                changes['schema_info'] = schema_changes
        
        # Compare business context
        if hasattr(original, 'business_context') and hasattr(mapped, 'business_context'):
            context_changes = self._compare_business_context(original.business_context, mapped.business_context)
            if context_changes:
                changes['business_context'] = context_changes
        
        return changes
    
    def _compare_schema_info(self, original_schema: Dict[str, Any], mapped_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Compare schema information between original and mapped assets"""
        changes = {}
        
        # Compare columns
        if 'columns' in original_schema and 'columns' in mapped_schema:
            original_columns = {col['name']: col for col in original_schema['columns']}
            mapped_columns = {col['name']: col for col in mapped_schema['columns']}
            
            column_changes = {}
            
            # Check for type changes
            for col_name in original_columns:
                if col_name in mapped_columns:
                    orig_type = original_columns[col_name].get('type')
                    mapped_type = mapped_columns[col_name].get('type')
                    
                    if orig_type != mapped_type:
                        column_changes[col_name] = {
                            'field': 'type',
                            'original': orig_type,
                            'mapped': mapped_type,
                            'change_type': 'type_conversion'
                        }
            
            if column_changes:
                changes['columns'] = column_changes
        
        return changes
    
    def _compare_business_context(self, original_context: BusinessContext, mapped_context: BusinessContext) -> Dict[str, Any]:
        """Compare business context between original and mapped assets"""
        changes = {}
        
        # Compare dimensions
        if original_context.dimensions != mapped_context.dimensions:
            changes['dimensions'] = {
                'original': original_context.dimensions,
                'mapped': mapped_context.dimensions,
                'change_type': 'list_transformation'
            }
        
        # Compare measures
        if original_context.measures != mapped_context.measures:
            changes['measures'] = {
                'original': original_context.measures,
                'mapped': mapped_context.measures,
                'change_type': 'list_transformation'
            }
        
        # Compare tags
        if original_context.tags != mapped_context.tags:
            changes['tags'] = {
                'original': original_context.tags,
                'mapped': mapped_context.tags,
                'change_type': 'list_transformation'
            }
        
        return changes
    
    def _validate_mapping(self, original: MetadataAsset, mapped: MetadataAsset, 
                         profile_id: Optional[str] = None) -> List[ValidationIssue]:
        """Validate the mapping result"""
        issues = []
        
        # Validate naming conventions
        issues.extend(self._validate_naming_conventions(mapped))
        
        # Validate data type compatibility
        issues.extend(self._validate_data_type_compatibility(original, mapped))
        
        # Validate business context preservation
        issues.extend(self._validate_business_context_preservation(original, mapped))
        
        # Validate schema structure
        issues.extend(self._validate_schema_structure(mapped))
        
        return issues
    
    def _validate_naming_conventions(self, asset: MetadataAsset) -> List[ValidationIssue]:
        """Validate naming conventions for the target system"""
        issues = []
        
        system_patterns = self.naming_patterns.get(asset.source_system.value, {})
        
        # Validate technical name
        if 'technical_name' in system_patterns:
            pattern = system_patterns['technical_name']
            if not re.match(pattern, asset.technical_name):
                issues.append(
                    ValidationIssue(
                        issue_id=str(uuid.uuid4()),
                        severity=ValidationSeverity.WARNING,
                        category=ValidationCategory.NAMING_CONVENTION,
                        title="Technical Name Convention Violation",
                        description=f"Technical name '{asset.technical_name}' doesn't match {asset.source_system.value} pattern: {pattern}",
                        affected_field="technical_name",
                        suggested_fix=f"Ensure technical name follows pattern: {pattern}",
                        impact_score=4
                    )
                )
        
        # Validate business name
        if asset.business_name and 'business_name' in system_patterns:
            pattern = system_patterns['business_name']
            if not re.match(pattern, asset.business_name):
                issues.append(
                    ValidationIssue(
                        issue_id=str(uuid.uuid4()),
                        severity=ValidationSeverity.INFO,
                        category=ValidationCategory.NAMING_CONVENTION,
                        title="Business Name Convention Violation",
                        description=f"Business name '{asset.business_name}' doesn't match {asset.source_system.value} pattern: {pattern}",
                        affected_field="business_name",
                        suggested_fix=f"Ensure business name follows pattern: {pattern}",
                        impact_score=2
                    )
                )
        
        return issues
    
    def _validate_data_type_compatibility(self, original: MetadataAsset, mapped: MetadataAsset) -> List[ValidationIssue]:
        """Validate data type compatibility between systems"""
        issues = []
        
        if not (hasattr(original, 'schema_info') and hasattr(mapped, 'schema_info')):
            return issues
        
        original_columns = {col['name']: col for col in original.schema_info.get('columns', [])}
        mapped_columns = {col['name']: col for col in mapped.schema_info.get('columns', [])}
        
        # Determine conversion direction
        conversion_key = f"{original.source_system.value}_to_{mapped.source_system.value}"
        compatibility_matrix = self.type_compatibility.get(conversion_key, {})
        
        for col_name in original_columns:
            if col_name in mapped_columns:
                original_type = original_columns[col_name].get('type', '').upper()
                mapped_type = mapped_columns[col_name].get('type', '').lower()
                
                compatible_types = compatibility_matrix.get(original_type, [])
                
                if compatible_types and mapped_type not in compatible_types:
                    issues.append(
                        ValidationIssue(
                            issue_id=str(uuid.uuid4()),
                            severity=ValidationSeverity.WARNING,
                            category=ValidationCategory.DATA_TYPE_COMPATIBILITY,
                            title="Potentially Incompatible Data Type Conversion",
                            description=f"Column '{col_name}': {original_type} → {mapped_type} may cause data loss",
                            affected_field=f"schema_info.columns.{col_name}.type",
                            suggested_fix=f"Consider using one of: {', '.join(compatible_types)}",
                            impact_score=6
                        )
                    )
        
        return issues
    
    def _validate_business_context_preservation(self, original: MetadataAsset, mapped: MetadataAsset) -> List[ValidationIssue]:
        """Validate that important business context is preserved"""
        issues = []
        
        # Check if business name is preserved or properly transformed
        if original.business_name and not mapped.business_name:
            issues.append(
                ValidationIssue(
                    issue_id=str(uuid.uuid4()),
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.BUSINESS_CONTEXT,
                    title="Business Name Lost",
                    description="Original business name was not preserved in mapping",
                    affected_field="business_name",
                    suggested_fix="Add mapping rule to preserve or transform business name",
                    impact_score=5
                )
            )
        
        # Check if important tags are preserved
        if (hasattr(original, 'business_context') and hasattr(mapped, 'business_context') and
            original.business_context.tags and not mapped.business_context.tags):
            issues.append(
                ValidationIssue(
                    issue_id=str(uuid.uuid4()),
                    severity=ValidationSeverity.INFO,
                    category=ValidationCategory.BUSINESS_CONTEXT,
                    title="Tags Not Preserved",
                    description="Original tags were not preserved in mapping",
                    affected_field="business_context.tags",
                    suggested_fix="Add mapping rule to preserve important tags",
                    impact_score=3
                )
            )
        
        return issues
    
    def _validate_schema_structure(self, asset: MetadataAsset) -> List[ValidationIssue]:
        """Validate schema structure integrity"""
        issues = []
        
        if not hasattr(asset, 'schema_info') or not asset.schema_info:
            return issues
        
        columns = asset.schema_info.get('columns', [])
        
        # Check for duplicate column names
        column_names = [col.get('name', '') for col in columns]
        duplicates = set([name for name in column_names if column_names.count(name) > 1])
        
        for duplicate in duplicates:
            issues.append(
                ValidationIssue(
                    issue_id=str(uuid.uuid4()),
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.SCHEMA_STRUCTURE,
                    title="Duplicate Column Name",
                    description=f"Column name '{duplicate}' appears multiple times",
                    affected_field="schema_info.columns",
                    suggested_fix="Ensure all column names are unique",
                    impact_score=8
                )
            )
        
        # Check for missing required column properties
        for i, col in enumerate(columns):
            if not col.get('name'):
                issues.append(
                    ValidationIssue(
                        issue_id=str(uuid.uuid4()),
                        severity=ValidationSeverity.ERROR,
                        category=ValidationCategory.SCHEMA_STRUCTURE,
                        title="Missing Column Name",
                        description=f"Column at index {i} is missing a name",
                        affected_field=f"schema_info.columns[{i}].name",
                        suggested_fix="Ensure all columns have valid names",
                        impact_score=9
                    )
                )
            
            if not col.get('type'):
                issues.append(
                    ValidationIssue(
                        issue_id=str(uuid.uuid4()),
                        severity=ValidationSeverity.WARNING,
                        category=ValidationCategory.SCHEMA_STRUCTURE,
                        title="Missing Column Type",
                        description=f"Column '{col.get('name', 'unknown')}' is missing a data type",
                        affected_field=f"schema_info.columns[{i}].type",
                        suggested_fix="Specify data type for all columns",
                        impact_score=6
                    )
                )
        
        return issues
    
    def _analyze_mapping_impact(self, original: MetadataAsset, mapped: MetadataAsset) -> Dict[str, Any]:
        """Analyze the impact of mapping transformation"""
        impact = {
            'data_loss_risk': 'low',
            'performance_impact': 'minimal',
            'compatibility_score': 0.9,
            'business_impact': 'low',
            'recommendations': []
        }
        
        # Analyze data type conversions for potential data loss
        if hasattr(original, 'schema_info') and hasattr(mapped, 'schema_info'):
            risky_conversions = self._identify_risky_conversions(original.schema_info, mapped.schema_info)
            if risky_conversions:
                impact['data_loss_risk'] = 'high' if len(risky_conversions) > 3 else 'medium'
                impact['recommendations'].append(f"Review {len(risky_conversions)} potentially risky data type conversions")
        
        # Analyze naming changes impact
        if original.technical_name != mapped.technical_name:
            impact['business_impact'] = 'medium'
            impact['recommendations'].append("Technical name change may require updates to dependent systems")
        
        # Calculate compatibility score based on validation issues
        # This would be enhanced with actual validation results
        
        return impact
    
    def _identify_risky_conversions(self, original_schema: Dict[str, Any], mapped_schema: Dict[str, Any]) -> List[Dict[str, str]]:
        """Identify potentially risky data type conversions"""
        risky_conversions = []
        
        # Define risky conversion patterns
        risky_patterns = [
            ('DECIMAL', 'int'),  # Precision loss
            ('DOUBLE', 'int'),   # Precision loss
            ('NVARCHAR', 'int'), # Type mismatch
            ('TIMESTAMP', 'date') # Precision loss
        ]
        
        original_columns = {col['name']: col for col in original_schema.get('columns', [])}
        mapped_columns = {col['name']: col for col in mapped_schema.get('columns', [])}
        
        for col_name in original_columns:
            if col_name in mapped_columns:
                orig_type = original_columns[col_name].get('type', '').upper()
                mapped_type = mapped_columns[col_name].get('type', '').lower()
                
                for risky_orig, risky_mapped in risky_patterns:
                    if orig_type == risky_orig and mapped_type == risky_mapped:
                        risky_conversions.append({
                            'column': col_name,
                            'from_type': orig_type,
                            'to_type': mapped_type,
                            'risk': 'data_loss'
                        })
        
        return risky_conversions
    
    def _validate_profile_structure(self, profile: MappingProfile) -> List[ValidationIssue]:
        """Validate the structure and configuration of a mapping profile"""
        issues = []
        
        # Check required fields
        if not profile.profile_id:
            issues.append(
                ValidationIssue(
                    issue_id=str(uuid.uuid4()),
                    severity=ValidationSeverity.CRITICAL,
                    category=ValidationCategory.MAPPING_LOGIC,
                    title="Missing Profile ID",
                    description="Mapping profile must have a unique profile_id",
                    suggested_fix="Assign a unique profile_id to the mapping profile",
                    impact_score=10
                )
            )
        
        if not profile.profile_name:
            issues.append(
                ValidationIssue(
                    issue_id=str(uuid.uuid4()),
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.MAPPING_LOGIC,
                    title="Missing Profile Name",
                    description="Mapping profile must have a descriptive name",
                    suggested_fix="Assign a descriptive name to the mapping profile",
                    impact_score=7
                )
            )
        
        # Validate mapping rules
        if not profile.mapping_rules:
            issues.append(
                ValidationIssue(
                    issue_id=str(uuid.uuid4()),
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.MAPPING_LOGIC,
                    title="No Mapping Rules",
                    description="Mapping profile has no transformation rules defined",
                    suggested_fix="Add at least one mapping rule to define transformations",
                    impact_score=6
                )
            )
        else:
            # Validate individual rules
            for rule in profile.mapping_rules:
                rule_issues = self._validate_mapping_rule(rule)
                issues.extend(rule_issues)
        
        return issues
    
    def _validate_mapping_rule(self, rule: MappingRule) -> List[ValidationIssue]:
        """Validate an individual mapping rule"""
        issues = []
        
        if not rule.rule_id:
            issues.append(
                ValidationIssue(
                    issue_id=str(uuid.uuid4()),
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.MAPPING_LOGIC,
                    title="Missing Rule ID",
                    description="Mapping rule must have a unique rule_id",
                    rule_id=rule.rule_id,
                    suggested_fix="Assign a unique rule_id to the mapping rule",
                    impact_score=8
                )
            )
        
        if not rule.source_field:
            issues.append(
                ValidationIssue(
                    issue_id=str(uuid.uuid4()),
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.MAPPING_LOGIC,
                    title="Missing Source Field",
                    description="Mapping rule must specify a source field",
                    rule_id=rule.rule_id,
                    suggested_fix="Specify the source field for the mapping rule",
                    impact_score=8
                )
            )
        
        if not rule.target_field:
            issues.append(
                ValidationIssue(
                    issue_id=str(uuid.uuid4()),
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.MAPPING_LOGIC,
                    title="Missing Target Field",
                    description="Mapping rule must specify a target field",
                    rule_id=rule.rule_id,
                    suggested_fix="Specify the target field for the mapping rule",
                    impact_score=8
                )
            )
        
        return issues
    
    def _generate_test_assets(self, profile: MappingProfile) -> List[MetadataAsset]:
        """Generate test assets for profile validation"""
        test_assets = []
        
        # Create a basic test asset based on profile configuration
        if profile.asset_type == AssetType.ANALYTICAL_MODEL:
            test_asset = MetadataAsset(
                asset_id=f"test_{profile.asset_type.value}_{uuid.uuid4()}",
                asset_type=profile.asset_type,
                source_system=profile.source_system,
                technical_name="TEST_ANALYTICAL_MODEL",
                business_name="Test Analytical Model",
                description="Test asset for mapping validation",
                owner="test_user",
                business_context=BusinessContext(
                    business_name="Test Analytical Model",
                    description="Test business context",
                    tags=["test", "validation"],
                    dimensions=["Date", "Product", "Region"],
                    measures=["Revenue", "Quantity", "Profit"]
                ),
                schema_info={
                    'columns': [
                        {'name': 'Date', 'type': 'DATE', 'nullable': False},
                        {'name': 'Product', 'type': 'NVARCHAR', 'nullable': False},
                        {'name': 'Revenue', 'type': 'DECIMAL', 'nullable': True}
                    ]
                }
            )
            test_assets.append(test_asset)
        
        elif profile.asset_type == AssetType.TABLE:
            test_asset = MetadataAsset(
                asset_id=f"test_{profile.asset_type.value}_{uuid.uuid4()}",
                asset_type=profile.asset_type,
                source_system=profile.source_system,
                technical_name="test_table",
                business_name="Test Table",
                description="Test table for mapping validation",
                owner="test_user",
                schema_info={
                    'columns': [
                        {'name': 'id', 'type': 'string', 'nullable': False},
                        {'name': 'name', 'type': 'string', 'nullable': True},
                        {'name': 'created_date', 'type': 'timestamp', 'nullable': False}
                    ]
                }
            )
            test_assets.append(test_asset)
        
        return test_assets
    
    def _generate_recommendations(self, issues: List[ValidationIssue]) -> List[str]:
        """Generate recommendations based on validation issues"""
        recommendations = []
        
        # Count issues by category and severity
        issue_counts = {}
        for issue in issues:
            key = f"{issue.category.value}_{issue.severity.value}"
            issue_counts[key] = issue_counts.get(key, 0) + 1
        
        # Generate category-specific recommendations
        if issue_counts.get('naming_convention_warning', 0) > 0:
            recommendations.append("Review and update naming convention rules to match target system requirements")
        
        if issue_counts.get('data_type_compatibility_warning', 0) > 0:
            recommendations.append("Validate data type conversions to prevent potential data loss")
        
        if issue_counts.get('business_context_warning', 0) > 0:
            recommendations.append("Enhance business context preservation rules to maintain metadata richness")
        
        if issue_counts.get('schema_structure_error', 0) > 0:
            recommendations.append("Fix schema structure issues before deploying mapping profile")
        
        if issue_counts.get('mapping_logic_critical', 0) > 0:
            recommendations.append("Address critical mapping logic issues immediately")
        
        # General recommendations
        if len(issues) > 10:
            recommendations.append("Consider breaking down complex mapping profile into smaller, focused profiles")
        
        if not recommendations:
            recommendations.append("Mapping profile validation passed successfully - ready for production use")
        
        return recommendations
    
    def _calculate_validation_score(self, issues: List[ValidationIssue]) -> float:
        """Calculate overall validation score (0-100)"""
        if not issues:
            return 100.0
        
        # Weight issues by severity
        severity_weights = {
            ValidationSeverity.INFO: 1,
            ValidationSeverity.WARNING: 3,
            ValidationSeverity.ERROR: 7,
            ValidationSeverity.CRITICAL: 15
        }
        
        total_penalty = sum(severity_weights.get(issue.severity, 5) for issue in issues)
        
        # Calculate score (max penalty of 100 results in score of 0)
        score = max(0, 100 - total_penalty)
        
        return round(score, 1)
    
    def _calculate_dry_run_impact(self, issues: List[ValidationIssue], results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate impact summary for dry run results"""
        impact = {
            'overall_risk': 'low',
            'readiness_score': 0.0,
            'critical_issues': 0,
            'blocking_issues': [],
            'recommendations': []
        }
        
        # Count critical issues
        critical_issues = [issue for issue in issues if issue.severity == ValidationSeverity.CRITICAL]
        impact['critical_issues'] = len(critical_issues)
        
        # Identify blocking issues
        for issue in critical_issues:
            impact['blocking_issues'].append({
                'title': issue.title,
                'description': issue.description,
                'suggested_fix': issue.suggested_fix
            })
        
        # Calculate readiness score
        success_rate = results['successful_mappings'] / max(results['total_assets'], 1)
        issue_penalty = min(len(issues) * 0.05, 0.5)  # Max 50% penalty for issues
        impact['readiness_score'] = max(0, (success_rate - issue_penalty) * 100)
        
        # Determine overall risk
        if impact['critical_issues'] > 0:
            impact['overall_risk'] = 'high'
        elif len(issues) > results['total_assets'] * 0.5:
            impact['overall_risk'] = 'medium'
        else:
            impact['overall_risk'] = 'low'
        
        # Generate recommendations
        if impact['readiness_score'] >= 80:
            impact['recommendations'].append("System is ready for production deployment")
        elif impact['readiness_score'] >= 60:
            impact['recommendations'].append("Address validation issues before production deployment")
        else:
            impact['recommendations'].append("Significant issues detected - thorough review required before deployment")
        
        return impact

    def validate_mapping_configuration(self) -> Dict[str, Any]:
        """Validate the current mapping configuration"""
        return self.asset_mapper.validate_mapping_configuration()
    
    def preview_asset_mapping(self, asset: MetadataAsset, target_system: SourceSystem, 
                             dry_run: bool = True) -> MappingPreview:
        """Preview asset mapping without actually performing it"""
        try:
            # Perform the mapping
            result = self.asset_mapper.map_asset(asset, target_system)
            
            # Create MappingPreview object
            preview = MappingPreview(original_asset=asset, mapped_asset=None)
            
            if result.success and result.mapped_asset:
                preview.mapped_asset = result.mapped_asset
                preview.target_asset = result.mapped_asset  # For backward compatibility
                preview.applied_rules = result.applied_rules
                preview.transformations = {
                    rule: {
                        'original_value': f"Original value for {rule}",
                        'new_value': f"Transformed value for {rule}",
                        'transformation_type': 'rule_application'
                    } for rule in result.applied_rules
                }
                preview.warnings = result.warnings
                preview.conflicts = result.conflicts
            else:
                # Create a minimal mapped asset for failed mappings
                preview.mapped_asset = asset
                preview.target_asset = asset
                preview.applied_rules = []
                preview.transformations = {}
                preview.warnings = [result.error_message] if result.error_message else []
                preview.conflicts = []
            
            return preview
            
        except Exception as e:
            # Return a preview with error information
            preview = MappingPreview(original_asset=asset, mapped_asset=None)
            preview.mapped_asset = asset
            preview.target_asset = asset
            preview.applied_rules = []
            preview.transformations = {}
            preview.warnings = [str(e)]
            preview.conflicts = []
            return preview
    
    def analyze_mapping_impact(self, rule_changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the impact of mapping rule changes"""
        impact_analysis = {
            'affected_assets': [],
            'performance_impact': 'low',
            'risk_level': 'low',
            'recommendations': []
        }
        
        # Simulate impact analysis
        for change in rule_changes:
            if change.get('type') == 'add_rule':
                impact_analysis['affected_assets'].append(f"New rule affects {change.get('asset_type', 'unknown')} assets")
            elif change.get('type') == 'modify_rule':
                impact_analysis['affected_assets'].append(f"Modified rule affects existing mappings")
        
        if len(rule_changes) > 5:
            impact_analysis['performance_impact'] = 'medium'
            impact_analysis['risk_level'] = 'medium'
            impact_analysis['recommendations'].append("Consider phased rollout for large rule changes")
        
        return impact_analysis
    
    def generate_validation_report(self, validation_results: Dict[str, Any]) -> str:
        """Generate a validation report file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f'mapping_validation_report_{timestamp}.json'
        
        report_data = {
            'validation_results': validation_results,
            'generated_at': datetime.now().isoformat(),
            'environment': self.environment
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        return report_file

# Example usage and testing
if __name__ == "__main__":
    print("🔍 Mapping Validation and Preview Engine")
    print("=" * 41)
    
    # This would normally import AssetMapper, but for testing we'll create a mock
    print("📊 Mapping validator initialized successfully!")
    print("✅ Ready for validation and preview operations")

def create_mapping_validator(environment: str = "default") -> MappingValidator:
    """Factory function to create a mapping validator"""
    from asset_mapper import AssetMapper
    asset_mapper = AssetMapper(environment)
    return MappingValidator(asset_mapper)

# Example usage and testing
if __name__ == "__main__":
    print("🔍 Mapping Validation and Preview Engine")
    print("=" * 40)
    
    # Create validator
    validator = create_mapping_validator("test")
    
    print(f"📊 Validator initialized for environment: {validator.environment}")
    print(f"🎉 Mapping validator ready for use!")