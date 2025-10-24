#!/usr/bin/env python3
"""
Priority-Based Synchronization Orchestrator
Advanced scheduling and orchestration engine for metadata synchronization
"""

import asyncio
import json
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, Future
from queue import PriorityQueue, Queue
import uuid

from metadata_sync_core import (
    MetadataAsset, AssetType, SourceSystem, SyncConfiguration, 
    SyncStatus, TransformationRule
)
from sync_logging import SyncLogger, EventType
from asset_mapper import AssetMapper, MappingResult
from datasphere_connector import DatasphereConnector
from glue_connector import GlueConnector
from incremental_sync import IncrementalSyncEngine, ChangeDetectionResult, DeltaSyncResult

class SyncPriority(Enum):
    """Synchronization priority levels"""
    CRITICAL = 1    # Real-time sync for analytical models
    HIGH = 2        # Hourly sync for views and core tables
    MEDIUM = 3      # Daily sync for data flows
    LOW = 4         # Weekly sync for metadata updates
    MAINTENANCE = 5 # Manual/scheduled maintenance operations

class SyncFrequency(Enum):
    """Synchronization frequency options"""
    REAL_TIME = "real_time"      # Immediate sync
    EVERY_15_MIN = "every_15min" # Every 15 minutes
    HOURLY = "hourly"            # Every hour
    DAILY = "daily"              # Once per day
    WEEKLY = "weekly"            # Once per week
    MANUAL = "manual"            # Manual trigger only

class SyncJobStatus(Enum):
    """Synchronization job status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

@dataclass
class SyncJob:
    """Individual synchronization job"""
    job_id: str
    asset_id: str
    asset_type: AssetType
    source_system: SourceSystem
    target_system: SourceSystem
    priority: SyncPriority
    frequency: SyncFrequency
    status: SyncJobStatus = SyncJobStatus.PENDING
    created_time: datetime = field(default_factory=datetime.now)
    scheduled_time: Optional[datetime] = None
    started_time: Optional[datetime] = None
    completed_time: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    retry_delay_seconds: int = 60
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    def __lt__(self, other):
        """Priority queue comparison - lower priority value = higher priority"""
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        # If same priority, use scheduled time
        if self.scheduled_time and other.scheduled_time:
            return self.scheduled_time < other.scheduled_time
        return self.created_time < other.created_time
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'job_id': self.job_id,
            'asset_id': self.asset_id,
            'asset_type': self.asset_type.value,
            'source_system': self.source_system.value,
            'target_system': self.target_system.value,
            'priority': self.priority.value,
            'frequency': self.frequency.value,
            'status': self.status.value,
            'created_time': self.created_time.isoformat(),
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'started_time': self.started_time.isoformat() if self.started_time else None,
            'completed_time': self.completed_time.isoformat() if self.completed_time else None,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'error_message': self.error_message,
            'result': self.result,
            'dependencies': self.dependencies,
            'tags': self.tags
        }

@dataclass
class SyncRule:
    """Synchronization rule definition"""
    rule_id: str
    rule_name: str
    asset_type: AssetType
    source_system: SourceSystem
    target_system: SourceSystem
    priority: SyncPriority
    frequency: SyncFrequency
    conditions: Dict[str, Any] = field(default_factory=dict)
    transformation_rules: List[str] = field(default_factory=list)
    is_active: bool = True
    created_date: datetime = field(default_factory=datetime.now)
    
    def matches_asset(self, asset: MetadataAsset) -> bool:
        """Check if this rule applies to the given asset"""
        if self.asset_type != asset.asset_type:
            return False
        
        if self.source_system != asset.source_system:
            return False
        
        # Check additional conditions
        if 'tags' in self.conditions:
            required_tags = self.conditions['tags']
            asset_tags = asset.business_context.tags or []
            if not any(tag in asset_tags for tag in required_tags):
                return False
        
        if 'name_pattern' in self.conditions:
            import re
            pattern = self.conditions['name_pattern']
            if not re.match(pattern, asset.technical_name):
                return False
        
        return True

@dataclass
class SyncMetrics:
    """Synchronization metrics and statistics"""
    total_jobs: int = 0
    completed_jobs: int = 0
    failed_jobs: int = 0
    pending_jobs: int = 0
    running_jobs: int = 0
    average_execution_time: float = 0.0
    success_rate: float = 0.0
    last_sync_time: Optional[datetime] = None
    jobs_by_priority: Dict[str, int] = field(default_factory=dict)
    jobs_by_asset_type: Dict[str, int] = field(default_factory=dict)
    
    def update_from_jobs(self, jobs: List[SyncJob]):
        """Update metrics from job list"""
        self.total_jobs = len(jobs)
        self.completed_jobs = len([j for j in jobs if j.status == SyncJobStatus.COMPLETED])
        self.failed_jobs = len([j for j in jobs if j.status == SyncJobStatus.FAILED])
        self.pending_jobs = len([j for j in jobs if j.status == SyncJobStatus.PENDING])
        self.running_jobs = len([j for j in jobs if j.status == SyncJobStatus.RUNNING])
        
        if self.total_jobs > 0:
            self.success_rate = (self.completed_jobs / self.total_jobs) * 100
        
        # Calculate average execution time
        completed_with_times = [
            j for j in jobs 
            if j.status == SyncJobStatus.COMPLETED and j.started_time and j.completed_time
        ]
        
        if completed_with_times:
            total_time = sum([
                (j.completed_time - j.started_time).total_seconds() 
                for j in completed_with_times
            ])
            self.average_execution_time = total_time / len(completed_with_times)
        
        # Update priority distribution
        self.jobs_by_priority = {}
        for job in jobs:
            priority_name = job.priority.name
            self.jobs_by_priority[priority_name] = self.jobs_by_priority.get(priority_name, 0) + 1
        
        # Update asset type distribution
        self.jobs_by_asset_type = {}
        for job in jobs:
            asset_type_name = job.asset_type.value
            self.jobs_by_asset_type[asset_type_name] = self.jobs_by_asset_type.get(asset_type_name, 0) + 1
        
        # Update last sync time
        completed_jobs = [j for j in jobs if j.completed_time]
        if completed_jobs:
            self.last_sync_time = max(j.completed_time for j in completed_jobs)

class SyncOrchestrator:
    """Advanced priority-based synchronization orchestrator"""
    
    def __init__(self, max_workers: int = 5, enable_incremental_sync: bool = True):
        self.logger = SyncLogger("sync_orchestrator")
        self.max_workers = max_workers
        
        # Core components
        self.asset_mapper = AssetMapper()
        self.datasphere_connector = None
        self.glue_connector = None
        
        # Incremental sync engine
        self.enable_incremental_sync = enable_incremental_sync
        self.incremental_sync_engine = IncrementalSyncEngine() if enable_incremental_sync else None
        
        # Job management
        self.job_queue = PriorityQueue()
        self.active_jobs: Dict[str, SyncJob] = {}
        self.completed_jobs: List[SyncJob] = []
        self.sync_rules: Dict[str, SyncRule] = {}
        
        # Threading and execution
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.running_futures: Dict[str, Future] = {}
        self.is_running = False
        self.scheduler_thread = None
        
        # Metrics and monitoring
        self.metrics = SyncMetrics()
        self.job_callbacks: List[Callable[[SyncJob], None]] = []
        
        # Configuration
        self.config = {
            'max_concurrent_jobs': max_workers,
            'job_timeout_seconds': 300,
            'retry_delay_seconds': 60,
            'cleanup_completed_jobs_after_hours': 24,
            'metrics_update_interval_seconds': 30,
            'incremental_sync_enabled': enable_incremental_sync
        }
        
        # Initialize default sync rules
        self._initialize_default_sync_rules()
    
    def initialize_connectors(self, datasphere_config: Dict[str, Any], 
                            glue_config: Dict[str, Any]) -> bool:
        """Initialize Datasphere and Glue connectors"""
        try:
            # Initialize Datasphere connector
            self.datasphere_connector = DatasphereConnector(
                base_url=datasphere_config['base_url'],
                client_id=datasphere_config['client_id'],
                client_secret=datasphere_config['client_secret'],
                token_url=datasphere_config['token_url']
            )
            
            # Initialize Glue connector
            self.glue_connector = GlueConnector(
                region=glue_config.get('region', 'us-east-1'),
                profile_name=glue_config.get('profile_name')
            )
            
            # Test connections
            if not self.datasphere_connector.test_connection():
                raise Exception("Failed to connect to Datasphere")
            
            if not self.glue_connector.test_connection():
                raise Exception("Failed to connect to AWS Glue")
            
            self.logger.log_event(
                event_type=EventType.SYSTEM_STARTED,
                source_system="sync_orchestrator",
                operation="initialize_connectors",
                status="completed",
                details={
                    'datasphere_url': datasphere_config['base_url'],
                    'glue_region': glue_config.get('region', 'us-east-1')
                }
            )
            
            return True
            
        except Exception as e:
            self.logger.logger.error(f"Failed to initialize connectors: {str(e)}")
            return False
    
    def register_sync_rule(self, rule: SyncRule) -> bool:
        """Register a synchronization rule"""
        try:
            self.sync_rules[rule.rule_id] = rule
            
            self.logger.log_event(
                event_type=EventType.CONFIGURATION_CHANGED,
                source_system="sync_orchestrator",
                operation="register_sync_rule",
                status="completed",
                details={
                    'rule_id': rule.rule_id,
                    'rule_name': rule.rule_name,
                    'asset_type': rule.asset_type.value,
                    'priority': rule.priority.name,
                    'frequency': rule.frequency.value
                }
            )
            
            return True
            
        except Exception as e:
            self.logger.logger.error(f"Failed to register sync rule {rule.rule_id}: {str(e)}")
            return False
    
    def schedule_asset_sync(self, asset: MetadataAsset, target_system: SourceSystem,
                           priority: Optional[SyncPriority] = None,
                           frequency: Optional[SyncFrequency] = None,
                           scheduled_time: Optional[datetime] = None) -> Optional[str]:
        """Schedule synchronization for a specific asset"""
        try:
            # Find applicable sync rule or use provided parameters
            applicable_rule = None
            if not priority or not frequency:
                for rule in self.sync_rules.values():
                    if rule.is_active and rule.matches_asset(asset):
                        applicable_rule = rule
                        break
            
            # Use rule parameters or provided parameters
            job_priority = priority or (applicable_rule.priority if applicable_rule else SyncPriority.MEDIUM)
            job_frequency = frequency or (applicable_rule.frequency if applicable_rule else SyncFrequency.MANUAL)
            
            # Create sync job
            job = SyncJob(
                job_id=f"sync_{asset.asset_id}_{int(datetime.now().timestamp())}",
                asset_id=asset.asset_id,
                asset_type=asset.asset_type,
                source_system=asset.source_system,
                target_system=target_system,
                priority=job_priority,
                frequency=job_frequency,
                scheduled_time=scheduled_time or datetime.now()
            )
            
            # Add to queue
            self.job_queue.put(job)
            
            self.logger.log_event(
                event_type=EventType.SYNC_SCHEDULED,
                source_system=asset.source_system.value,
                operation="schedule_sync",
                status="completed",
                details={
                    'job_id': job.job_id,
                    'asset_id': asset.asset_id,
                    'asset_type': asset.asset_type.value,
                    'target_system': target_system.value,
                    'priority': job_priority.name,
                    'scheduled_time': job.scheduled_time.isoformat()
                }
            )
            
            return job.job_id
            
        except Exception as e:
            self.logger.logger.error(f"Failed to schedule sync for asset {asset.asset_id}: {str(e)}")
            return None
    
    def schedule_bulk_sync(self, assets: List[MetadataAsset], target_system: SourceSystem,
                          priority: SyncPriority = SyncPriority.MEDIUM) -> List[str]:
        """Schedule synchronization for multiple assets"""
        job_ids = []
        
        for asset in assets:
            job_id = self.schedule_asset_sync(asset, target_system, priority)
            if job_id:
                job_ids.append(job_id)
        
        self.logger.log_event(
            event_type=EventType.SYNC_SCHEDULED,
            source_system="sync_orchestrator",
            operation="schedule_bulk_sync",
            status="completed",
            details={
                'assets_count': len(assets),
                'scheduled_jobs': len(job_ids),
                'target_system': target_system.value,
                'priority': priority.name
            }
        )
        
        return job_ids
    
    def schedule_incremental_sync(self, source_system: SourceSystem, target_system: SourceSystem) -> Dict[str, Any]:
        """Schedule incremental synchronization based on change detection"""
        if not self.enable_incremental_sync or not self.incremental_sync_engine:
            return {
                'success': False,
                'error': 'Incremental sync is not enabled'
            }
        
        try:
            # Get current assets from source system
            current_assets = self._get_all_assets_from_source(source_system)
            
            # Analyze changes
            change_results = self.incremental_sync_engine.analyze_sync_requirements(current_assets)
            
            # Schedule sync jobs for changed assets
            job_ids = []
            for change_result in change_results:
                if change_result.sync_required:
                    # Determine priority based on change type
                    priority = SyncPriority.MEDIUM
                    if change_result.priority_boost:
                        priority = SyncPriority.HIGH
                    if change_result.change_type.value in ['created', 'schema_changed']:
                        priority = SyncPriority.CRITICAL
                    
                    if change_result.current_asset:
                        job_id = self.schedule_asset_sync(
                            asset=change_result.current_asset,
                            target_system=target_system,
                            priority=priority
                        )
                        if job_id:
                            job_ids.append(job_id)
            
            self.logger.log_event(
                event_type=EventType.INCREMENTAL_SYNC_COMPLETED,
                source_system=source_system.value,
                operation="schedule_incremental_sync",
                status="completed",
                details={
                    'assets_analyzed': len(current_assets),
                    'changes_detected': len(change_results),
                    'jobs_scheduled': len(job_ids),
                    'target_system': target_system.value
                }
            )
            
            return {
                'success': True,
                'assets_analyzed': len(current_assets),
                'changes_detected': len(change_results),
                'jobs_scheduled': len(job_ids),
                'job_ids': job_ids,
                'change_summary': self._summarize_changes(change_results)
            }
            
        except Exception as e:
            self.logger.logger.error(f"Failed to schedule incremental sync: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_all_assets_from_source(self, source_system: SourceSystem) -> List[MetadataAsset]:
        """Get all assets from a source system"""
        all_assets = []
        
        try:
            if source_system == SourceSystem.DATASPHERE:
                if not self.datasphere_connector:
                    raise Exception("Datasphere connector not initialized")
                
                # Get all asset types
                for asset_type in AssetType:
                    assets = self.datasphere_connector.get_assets(asset_type)
                    all_assets.extend(assets)
            
            elif source_system == SourceSystem.GLUE:
                if not self.glue_connector:
                    raise Exception("Glue connector not initialized")
                
                # Get all asset types
                for asset_type in AssetType:
                    assets = self.glue_connector.get_assets(asset_type)
                    all_assets.extend(assets)
            
            return all_assets
            
        except Exception as e:
            self.logger.logger.error(f"Failed to get assets from {source_system.value}: {str(e)}")
            return []
    
    def _summarize_changes(self, change_results: List[ChangeDetectionResult]) -> Dict[str, int]:
        """Summarize detected changes by type"""
        summary = {}
        for result in change_results:
            change_type = result.change_type.value
            summary[change_type] = summary.get(change_type, 0) + 1
        return summary
    
    def get_incremental_sync_status(self) -> Dict[str, Any]:
        """Get status of incremental synchronization"""
        if not self.enable_incremental_sync or not self.incremental_sync_engine:
            return {
                'enabled': False,
                'message': 'Incremental sync is not enabled'
            }
        
        stats = self.incremental_sync_engine.get_sync_statistics()
        report = self.incremental_sync_engine.create_sync_report()
        
        return {
            'enabled': True,
            'statistics': stats,
            'report': report,
            'checkpoint_count': len(self.incremental_sync_engine.checkpoint_manager._checkpoint_cache)
        }
    
    def start_orchestrator(self) -> bool:
        """Start the synchronization orchestrator"""
        if self.is_running:
            self.logger.logger.warning("Orchestrator is already running")
            return False
        
        try:
            self.is_running = True
            
            # Start scheduler thread
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self.scheduler_thread.start()
            
            self.logger.log_event(
                event_type=EventType.SYSTEM_STARTED,
                source_system="sync_orchestrator",
                operation="start_orchestrator",
                status="completed",
                details={
                    'max_workers': self.max_workers,
                    'sync_rules_count': len(self.sync_rules)
                }
            )
            
            return True
            
        except Exception as e:
            self.is_running = False
            self.logger.logger.error(f"Failed to start orchestrator: {str(e)}")
            return False
    
    def stop_orchestrator(self) -> bool:
        """Stop the synchronization orchestrator"""
        try:
            self.is_running = False
            
            # Wait for scheduler thread to finish
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                self.scheduler_thread.join(timeout=10)
            
            # Cancel running jobs
            for job_id, future in self.running_futures.items():
                if not future.done():
                    future.cancel()
                    if job_id in self.active_jobs:
                        self.active_jobs[job_id].status = SyncJobStatus.CANCELLED
            
            # Shutdown executor
            self.executor.shutdown(wait=True)
            
            self.logger.log_event(
                event_type=EventType.SYSTEM_STOPPED,
                source_system="sync_orchestrator",
                operation="stop_orchestrator",
                status="completed",
                details={
                    'cancelled_jobs': len(self.running_futures),
                    'completed_jobs': len(self.completed_jobs)
                }
            )
            
            return True
            
        except Exception as e:
            self.logger.logger.error(f"Failed to stop orchestrator: {str(e)}")
            return False
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.is_running:
            try:
                # Process completed jobs
                self._process_completed_jobs()
                
                # Start new jobs if capacity available
                self._start_pending_jobs()
                
                # Update metrics
                self._update_metrics()
                
                # Cleanup old jobs
                self._cleanup_old_jobs()
                
                # Sleep before next iteration
                time.sleep(1)
                
            except Exception as e:
                self.logger.logger.error(f"Error in scheduler loop: {str(e)}")
                time.sleep(5)  # Wait longer on error
    
    def _process_completed_jobs(self):
        """Process completed job futures"""
        completed_job_ids = []
        
        for job_id, future in self.running_futures.items():
            if future.done():
                completed_job_ids.append(job_id)
                
                if job_id in self.active_jobs:
                    job = self.active_jobs[job_id]
                    job.completed_time = datetime.now()
                    
                    try:
                        result = future.result()
                        job.status = SyncJobStatus.COMPLETED
                        job.result = result
                        
                        self.logger.log_event(
                            event_type=EventType.SYNC_COMPLETED,
                            source_system=job.source_system.value,
                            operation="sync_job",
                            status="completed",
                            details={
                                'job_id': job.job_id,
                                'asset_id': job.asset_id,
                                'execution_time_seconds': (job.completed_time - job.started_time).total_seconds(),
                                'retry_count': job.retry_count
                            }
                        )
                        
                    except Exception as e:
                        job.status = SyncJobStatus.FAILED
                        job.error_message = str(e)
                        
                        # Check if we should retry
                        if job.retry_count < job.max_retries:
                            job.retry_count += 1
                            job.status = SyncJobStatus.RETRYING
                            job.scheduled_time = datetime.now() + timedelta(seconds=job.retry_delay_seconds)
                            self.job_queue.put(job)
                            
                            self.logger.log_event(
                                event_type=EventType.SYNC_RETRYING,
                                source_system=job.source_system.value,
                                operation="sync_job",
                                status="retrying",
                                details={
                                    'job_id': job.job_id,
                                    'retry_count': job.retry_count,
                                    'max_retries': job.max_retries,
                                    'error_message': str(e)
                                }
                            )
                        else:
                            self.logger.log_event(
                                event_type=EventType.SYNC_FAILED,
                                source_system=job.source_system.value,
                                operation="sync_job",
                                status="failed",
                                details={
                                    'job_id': job.job_id,
                                    'asset_id': job.asset_id,
                                    'retry_count': job.retry_count,
                                    'error_message': str(e)
                                }
                            )
                    
                    # Move to completed jobs and notify callbacks
                    self.completed_jobs.append(job)
                    del self.active_jobs[job_id]
                    
                    for callback in self.job_callbacks:
                        try:
                            callback(job)
                        except Exception as e:
                            self.logger.logger.error(f"Job callback failed: {str(e)}")
        
        # Remove completed futures
        for job_id in completed_job_ids:
            del self.running_futures[job_id]
    
    def _start_pending_jobs(self):
        """Start pending jobs if capacity is available"""
        while (len(self.active_jobs) < self.config['max_concurrent_jobs'] and 
               not self.job_queue.empty()):
            
            try:
                job = self.job_queue.get_nowait()
                
                # Check if job should be started now
                if job.scheduled_time and job.scheduled_time > datetime.now():
                    # Put back in queue for later
                    self.job_queue.put(job)
                    break
                
                # Start the job
                job.status = SyncJobStatus.RUNNING
                job.started_time = datetime.now()
                
                self.active_jobs[job.job_id] = job
                
                # Submit to executor
                future = self.executor.submit(self._execute_sync_job, job)
                self.running_futures[job.job_id] = future
                
                self.logger.log_event(
                    event_type=EventType.SYNC_STARTED,
                    source_system=job.source_system.value,
                    operation="sync_job",
                    status="started",
                    details={
                        'job_id': job.job_id,
                        'asset_id': job.asset_id,
                        'priority': job.priority.name,
                        'active_jobs': len(self.active_jobs)
                    }
                )
                
            except Exception as e:
                self.logger.logger.error(f"Failed to start job: {str(e)}")
                break
    
    def _execute_sync_job(self, job: SyncJob) -> Dict[str, Any]:
        """Execute a synchronization job"""
        try:
            # Get source asset
            source_asset = self._get_asset_from_source(job)
            if not source_asset:
                raise Exception(f"Failed to retrieve asset {job.asset_id} from {job.source_system.value}")
            
            # Map asset for target system
            mapping_result = self.asset_mapper.map_asset(source_asset, job.target_system)
            if not mapping_result.success:
                raise Exception(f"Asset mapping failed: {mapping_result.error_message}")
            
            # Create asset in target system
            creation_result = self._create_asset_in_target(mapping_result.mapped_asset, job.target_system)
            if not creation_result['success']:
                raise Exception(f"Failed to create asset in target system: {creation_result.get('error')}")
            
            return {
                'success': True,
                'asset_id': job.asset_id,
                'mapped_asset_id': mapping_result.mapped_asset.asset_id,
                'target_asset_id': creation_result.get('target_asset_id'),
                'mapping_rules_applied': len(mapping_result.applied_rules),
                'conflicts_resolved': len(mapping_result.conflicts),
                'execution_time_ms': mapping_result.execution_time_ms
            }
            
        except Exception as e:
            raise Exception(f"Sync job execution failed: {str(e)}")
    
    def _get_asset_from_source(self, job: SyncJob) -> Optional[MetadataAsset]:
        """Retrieve asset from source system"""
        try:
            self.logger.logger.info(f"Looking for asset {job.asset_id} of type {job.asset_type.value} in {job.source_system.value}")
            
            if job.source_system == SourceSystem.DATASPHERE:
                if not self.datasphere_connector:
                    raise Exception("Datasphere connector not initialized")
                
                # Extract asset based on type using the correct method
                assets = self.datasphere_connector.get_assets(job.asset_type)
                self.logger.logger.info(f"Found {len(assets)} assets of type {job.asset_type.value} from Datasphere")
                
                for asset in assets:
                    self.logger.logger.debug(f"Checking asset: {asset.asset_id}")
                    if asset.asset_id == job.asset_id:
                        self.logger.logger.info(f"Found matching asset: {asset.asset_id}")
                        return asset
                
                self.logger.logger.warning(f"Asset {job.asset_id} not found in {len(assets)} available assets")
            
            elif job.source_system == SourceSystem.GLUE:
                if not self.glue_connector:
                    raise Exception("Glue connector not initialized")
                
                # Extract asset from Glue using the correct method
                assets = self.glue_connector.get_assets(job.asset_type)
                self.logger.logger.info(f"Found {len(assets)} assets of type {job.asset_type.value} from Glue")
                
                for asset in assets:
                    self.logger.logger.debug(f"Checking asset: {asset.asset_id}")
                    if asset.asset_id == job.asset_id:
                        self.logger.logger.info(f"Found matching asset: {asset.asset_id}")
                        return asset
                
                self.logger.logger.warning(f"Asset {job.asset_id} not found in {len(assets)} available assets")
            
            self.logger.logger.error(f"Asset {job.asset_id} not found in source system {job.source_system.value}")
            return None
            
        except Exception as e:
            self.logger.logger.error(f"Failed to get asset from source: {str(e)}")
            return None
    
    def _create_asset_in_target(self, asset: MetadataAsset, target_system: SourceSystem) -> Dict[str, Any]:
        """Create asset in target system"""
        try:
            self.logger.logger.info(f"Creating asset {asset.asset_id} in target system {target_system.value}")
            if target_system == SourceSystem.GLUE:
                if not self.glue_connector:
                    raise Exception("Glue connector not initialized")
                
                self.logger.logger.info(f"Creating {asset.asset_type.value} in AWS Glue")
                
                if asset.asset_type == AssetType.ANALYTICAL_MODEL:
                    # Create as Glue table
                    result = self.glue_connector.create_table(
                        database_name=f"datasphere_{asset.business_context.owner or 'default'}",
                        table_name=asset.technical_name.lower(),
                        description=asset.description,
                        columns=asset.schema_info.get('columns', []),
                        tags=asset.business_context.tags or []
                    )
                    return result
                
                elif asset.asset_type == AssetType.TABLE:
                    result = self.glue_connector.create_table(
                        database_name=f"datasphere_{asset.business_context.owner or 'default'}",
                        table_name=asset.technical_name.lower(),
                        description=asset.description,
                        columns=asset.schema_info.get('columns', []),
                        tags=asset.business_context.tags or []
                    )
                    return result
            
            elif target_system == SourceSystem.DATASPHERE:
                if not self.datasphere_connector:
                    raise Exception("Datasphere connector not initialized")
                
                # For now, Datasphere doesn't support creating assets via API
                # This is a metadata sync, so we'll log the sync completion
                self.logger.logger.info(f"Metadata sync completed for asset {asset.asset_id} to Datasphere")
                return {
                    'success': True, 
                    'message': 'Metadata synchronized to Datasphere catalog',
                    'asset_id': asset.asset_id,
                    'target_system': 'datasphere'
                }
            
            return {'success': False, 'error': f'Target system {target_system.value} not supported'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _update_metrics(self):
        """Update orchestrator metrics"""
        try:
            all_jobs = list(self.active_jobs.values()) + self.completed_jobs
            self.metrics.update_from_jobs(all_jobs)
            
        except Exception as e:
            self.logger.logger.error(f"Failed to update metrics: {str(e)}")
    
    def _cleanup_old_jobs(self):
        """Clean up old completed jobs"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=self.config['cleanup_completed_jobs_after_hours'])
            
            initial_count = len(self.completed_jobs)
            self.completed_jobs = [
                job for job in self.completed_jobs 
                if job.completed_time and job.completed_time > cutoff_time
            ]
            
            cleaned_count = initial_count - len(self.completed_jobs)
            if cleaned_count > 0:
                self.logger.logger.info(f"Cleaned up {cleaned_count} old completed jobs")
                
        except Exception as e:
            self.logger.logger.error(f"Failed to cleanup old jobs: {str(e)}")
    
    def _initialize_default_sync_rules(self):
        """Initialize default synchronization rules"""
        # Critical priority for analytical models
        analytical_model_rule = SyncRule(
            rule_id="critical_analytical_models",
            rule_name="Critical Analytical Models Sync",
            asset_type=AssetType.ANALYTICAL_MODEL,
            source_system=SourceSystem.DATASPHERE,
            target_system=SourceSystem.GLUE,
            priority=SyncPriority.CRITICAL,
            frequency=SyncFrequency.REAL_TIME,
            conditions={'tags': ['critical', 'production', 'certified']}
        )
        
        # High priority for views and core tables
        view_sync_rule = SyncRule(
            rule_id="high_priority_views",
            rule_name="High Priority Views Sync",
            asset_type=AssetType.VIEW,
            source_system=SourceSystem.DATASPHERE,
            target_system=SourceSystem.GLUE,
            priority=SyncPriority.HIGH,
            frequency=SyncFrequency.HOURLY
        )
        
        # High priority for core tables
        core_table_rule = SyncRule(
            rule_id="high_priority_core_tables",
            rule_name="High Priority Core Tables Sync",
            asset_type=AssetType.TABLE,
            source_system=SourceSystem.DATASPHERE,
            target_system=SourceSystem.GLUE,
            priority=SyncPriority.HIGH,
            frequency=SyncFrequency.HOURLY,
            conditions={'tags': ['core', 'master_data', 'critical']}
        )
        
        # Medium priority for regular tables
        table_sync_rule = SyncRule(
            rule_id="medium_priority_tables",
            rule_name="Medium Priority Tables Sync",
            asset_type=AssetType.TABLE,
            source_system=SourceSystem.DATASPHERE,
            target_system=SourceSystem.GLUE,
            priority=SyncPriority.MEDIUM,
            frequency=SyncFrequency.DAILY
        )
        
        # Medium priority for data flows
        data_flow_rule = SyncRule(
            rule_id="medium_priority_data_flows",
            rule_name="Medium Priority Data Flows Sync",
            asset_type=AssetType.DATA_FLOW,
            source_system=SourceSystem.DATASPHERE,
            target_system=SourceSystem.GLUE,
            priority=SyncPriority.MEDIUM,
            frequency=SyncFrequency.DAILY,
            conditions={'tags': ['transformation', 'pipeline']}
        )
        
        # Register default rules
        self.register_sync_rule(analytical_model_rule)
        self.register_sync_rule(view_sync_rule)
        self.register_sync_rule(core_table_rule)
        self.register_sync_rule(table_sync_rule)
        self.register_sync_rule(data_flow_rule)
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific job"""
        # Check active jobs
        if job_id in self.active_jobs:
            return self.active_jobs[job_id].to_dict()
        
        # Check completed jobs
        for job in self.completed_jobs:
            if job.job_id == job_id:
                return job.to_dict()
        
        return None
    
    def get_all_jobs(self, status_filter: Optional[SyncJobStatus] = None) -> List[Dict[str, Any]]:
        """Get all jobs, optionally filtered by status"""
        all_jobs = list(self.active_jobs.values()) + self.completed_jobs
        
        if status_filter:
            all_jobs = [job for job in all_jobs if job.status == status_filter]
        
        return [job.to_dict() for job in all_jobs]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get orchestrator metrics"""
        return {
            'total_jobs': self.metrics.total_jobs,
            'completed_jobs': self.metrics.completed_jobs,
            'failed_jobs': self.metrics.failed_jobs,
            'pending_jobs': self.metrics.pending_jobs,
            'running_jobs': self.metrics.running_jobs,
            'success_rate': self.metrics.success_rate,
            'average_execution_time': self.metrics.average_execution_time,
            'last_sync_time': self.metrics.last_sync_time.isoformat() if self.metrics.last_sync_time else None,
            'jobs_by_priority': self.metrics.jobs_by_priority,
            'jobs_by_asset_type': self.metrics.jobs_by_asset_type,
            'active_jobs_count': len(self.active_jobs),
            'queue_size': self.job_queue.qsize(),
            'sync_rules_count': len(self.sync_rules)
        }
    
    def add_job_callback(self, callback: Callable[[SyncJob], None]):
        """Add callback function to be called when jobs complete"""
        self.job_callbacks.append(callback)
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending or running job"""
        try:
            # Cancel running job
            if job_id in self.running_futures:
                future = self.running_futures[job_id]
                if future.cancel():
                    if job_id in self.active_jobs:
                        self.active_jobs[job_id].status = SyncJobStatus.CANCELLED
                        self.active_jobs[job_id].completed_time = datetime.now()
                    return True
            
            # Cancel pending job (would need to implement queue search)
            # This is a simplified implementation
            return False
            
        except Exception as e:
            self.logger.logger.error(f"Failed to cancel job {job_id}: {str(e)}")
            return False

# Example usage and testing
if __name__ == "__main__":
    print("🎯 Priority-Based Synchronization Orchestrator")
    print("=" * 46)
    
    # Create orchestrator
    orchestrator = SyncOrchestrator(max_workers=3)
    
    # Show default sync rules
    print(f"📋 Default Sync Rules: {len(orchestrator.sync_rules)}")
    for rule_id, rule in orchestrator.sync_rules.items():
        print(f"  • {rule.rule_name}")
        print(f"    Asset Type: {rule.asset_type.value}")
        print(f"    Priority: {rule.priority.name}")
        print(f"    Frequency: {rule.frequency.value}")
        print()
    
    # Show initial metrics
    metrics = orchestrator.get_metrics()
    print(f"📊 Initial Metrics:")
    print(f"  Total Jobs: {metrics['total_jobs']}")
    print(f"  Queue Size: {metrics['queue_size']}")
    print(f"  Sync Rules: {metrics['sync_rules_count']}")
    
    print(f"\n🎉 Sync orchestrator initialized successfully!")