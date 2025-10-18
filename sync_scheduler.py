#!/usr/bin/env python3
"""
Priority-Based Synchronization Scheduler
Implements intelligent scheduling and orchestration for metadata synchronization
"""

import asyncio
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass, field
import heapq
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, Future

from metadata_sync_core import (
    MetadataAsset, SyncConfiguration, AssetType, PriorityLevel, 
    SyncFrequency, SyncStatus, MetadataSyncEngine
)
from sync_logging import SyncLogger, EventType

class SchedulerStatus(Enum):
    """Scheduler status states"""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"

@dataclass
class ScheduledTask:
    """Represents a scheduled synchronization task"""
    task_id: str
    config_id: str
    priority: int  # Lower number = higher priority
    scheduled_time: datetime
    sync_frequency: SyncFrequency
    asset_types: List[AssetType]
    retry_count: int = 0
    max_retries: int = 3
    last_execution: Optional[datetime] = None
    next_execution: Optional[datetime] = None
    is_active: bool = True
    
    def __lt__(self, other):
        """Enable priority queue ordering"""
        if self.scheduled_time == other.scheduled_time:
            return self.priority < other.priority
        return self.scheduled_time < other.scheduled_time

@dataclass
class ExecutionResult:
    """Result of a scheduled task execution"""
    task_id: str
    execution_id: str
    start_time: datetime
    end_time: Optional[datetime]
    status: str
    results: Dict[str, Any]
    error_message: Optional[str] = None
    duration_seconds: Optional[float] = None

class PriorityScheduler:
    """Priority-based scheduler for metadata synchronization tasks"""
    
    def __init__(self, max_concurrent_tasks: int = 5):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.status = SchedulerStatus.STOPPED
        self.task_queue: List[ScheduledTask] = []
        self.active_tasks: Dict[str, Future] = {}
        self.completed_tasks: List[ExecutionResult] = []
        self.sync_engine = MetadataSyncEngine()
        self.logger = SyncLogger("scheduler")
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_tasks)
        self.scheduler_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        # Priority mappings
        self.priority_map = {
            PriorityLevel.CRITICAL: 1,
            PriorityLevel.HIGH: 2,
            PriorityLevel.MEDIUM: 3,
            PriorityLevel.LOW: 4
        }
        
        # Asset type priority mappings
        self.asset_priority_map = {
            AssetType.ANALYTICAL_MODEL: 1,  # Critical business assets
            AssetType.TABLE: 2,             # Core data structures
            AssetType.VIEW: 3,              # Derived data views
            AssetType.SPACE: 4,             # Organizational containers
            AssetType.DATA_FLOW: 5          # Process metadata
        }
    
    def schedule_task(self, config: SyncConfiguration, 
                     asset_types: Optional[List[AssetType]] = None) -> str:
        """Schedule a synchronization task"""
        
        task_id = str(uuid.uuid4())
        
        # Determine priority based on configuration and asset types
        base_priority = self.priority_map[config.priority_level]
        
        if asset_types:
            # Use highest priority asset type
            asset_priorities = [self.asset_priority_map.get(at, 10) for at in asset_types]
            min_asset_priority = min(asset_priorities)
            # Combine base priority with asset priority
            final_priority = (base_priority * 10) + min_asset_priority
        else:
            final_priority = base_priority * 10
        
        # Calculate next execution time
        next_execution = self._calculate_next_execution(config.sync_frequency)
        
        scheduled_task = ScheduledTask(
            task_id=task_id,
            config_id=config.config_id,
            priority=final_priority,
            scheduled_time=next_execution,
            sync_frequency=config.sync_frequency,
            asset_types=asset_types or [],
            next_execution=next_execution
        )
        
        # Add to priority queue
        heapq.heappush(self.task_queue, scheduled_task)
        
        self.logger.log_event(
            event_type=EventType.SYNC_STARTED,
            source_system="scheduler",
            operation="schedule_task",
            status="scheduled",
            details={
                'task_id': task_id,
                'config_id': config.config_id,
                'priority': final_priority,
                'scheduled_time': next_execution.isoformat(),
                'sync_frequency': config.sync_frequency.value
            }
        )
        
        return task_id
    
    def _calculate_next_execution(self, frequency: SyncFrequency) -> datetime:
        """Calculate next execution time based on frequency"""
        now = datetime.now()
        
        if frequency == SyncFrequency.REAL_TIME:
            return now
        elif frequency == SyncFrequency.HOURLY:
            return now + timedelta(hours=1)
        elif frequency == SyncFrequency.DAILY:
            return now + timedelta(days=1)
        elif frequency == SyncFrequency.WEEKLY:
            return now + timedelta(weeks=1)
        else:
            return now + timedelta(hours=1)  # Default to hourly
    
    def start(self):
        """Start the scheduler"""
        if self.status == SchedulerStatus.RUNNING:
            self.logger.logger.warning("Scheduler is already running")
            return
        
        self.status = SchedulerStatus.RUNNING
        self.stop_event.clear()
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        self.logger.log_event(
            event_type=EventType.SYNC_STARTED,
            source_system="scheduler",
            operation="start_scheduler",
            status="started",
            details={'max_concurrent_tasks': self.max_concurrent_tasks}
        )
        
        self.logger.logger.info("Priority scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        if self.status == SchedulerStatus.STOPPED:
            return
        
        self.status = SchedulerStatus.STOPPED
        self.stop_event.set()
        
        # Wait for scheduler thread to finish
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        # Cancel active tasks
        for task_id, future in self.active_tasks.items():
            future.cancel()
        
        self.active_tasks.clear()
        
        self.logger.log_event(
            event_type=EventType.SYNC_COMPLETED,
            source_system="scheduler",
            operation="stop_scheduler",
            status="stopped",
            details={'cancelled_tasks': len(self.active_tasks)}
        )
        
        self.logger.logger.info("Priority scheduler stopped")
    
    def pause(self):
        """Pause the scheduler"""
        if self.status == SchedulerStatus.RUNNING:
            self.status = SchedulerStatus.PAUSED
            self.logger.logger.info("Priority scheduler paused")
    
    def resume(self):
        """Resume the scheduler"""
        if self.status == SchedulerStatus.PAUSED:
            self.status = SchedulerStatus.RUNNING
            self.logger.logger.info("Priority scheduler resumed")
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        while not self.stop_event.is_set():
            try:
                if self.status == SchedulerStatus.RUNNING:
                    self._process_pending_tasks()
                    self._cleanup_completed_tasks()
                
                # Sleep for a short interval
                time.sleep(1)
                
            except Exception as e:
                self.status = SchedulerStatus.ERROR
                self.logger.create_error_report(
                    error_type="scheduler_error",
                    error_message=str(e),
                    context={'operation': 'scheduler_loop'},
                    affected_assets=[],
                    severity="CRITICAL"
                )
                self.logger.logger.error(f"Scheduler loop error: {str(e)}")
                break
    
    def _process_pending_tasks(self):
        """Process pending tasks that are ready for execution"""
        now = datetime.now()
        
        # Check if we have capacity for more tasks
        if len(self.active_tasks) >= self.max_concurrent_tasks:
            return
        
        # Get tasks ready for execution
        ready_tasks = []
        remaining_tasks = []
        
        while self.task_queue:
            task = heapq.heappop(self.task_queue)
            
            if task.scheduled_time <= now and task.is_active:
                ready_tasks.append(task)
            else:
                remaining_tasks.append(task)
            
            # Stop if we have enough tasks or reached capacity
            if len(ready_tasks) >= (self.max_concurrent_tasks - len(self.active_tasks)):
                break
        
        # Put remaining tasks back in queue
        for task in remaining_tasks:
            heapq.heappush(self.task_queue, task)
        
        # Execute ready tasks
        for task in ready_tasks:
            if len(self.active_tasks) < self.max_concurrent_tasks:
                self._execute_task(task)
    
    def _execute_task(self, task: ScheduledTask):
        """Execute a scheduled task"""
        execution_id = str(uuid.uuid4())
        
        # Submit task to thread pool
        future = self.executor.submit(self._run_sync_task, task, execution_id)
        self.active_tasks[task.task_id] = future
        
        # Update task execution info
        task.last_execution = datetime.now()
        task.next_execution = self._calculate_next_execution(task.sync_frequency)
        
        self.logger.log_event(
            event_type=EventType.SYNC_STARTED,
            source_system="scheduler",
            operation="execute_task",
            status="executing",
            details={
                'task_id': task.task_id,
                'execution_id': execution_id,
                'config_id': task.config_id,
                'priority': task.priority
            }
        )
        
        # Reschedule task for next execution if it's recurring
        if task.sync_frequency != SyncFrequency.REAL_TIME:
            next_task = ScheduledTask(
                task_id=str(uuid.uuid4()),
                config_id=task.config_id,
                priority=task.priority,
                scheduled_time=task.next_execution,
                sync_frequency=task.sync_frequency,
                asset_types=task.asset_types,
                max_retries=task.max_retries
            )
            heapq.heappush(self.task_queue, next_task)
    
    def _run_sync_task(self, task: ScheduledTask, execution_id: str) -> ExecutionResult:
        """Run synchronization task in thread pool"""
        start_time = datetime.now()
        
        try:
            # Get configuration
            if task.config_id not in self.sync_engine.active_configs:
                raise ValueError(f"Configuration {task.config_id} not found")
            
            config = self.sync_engine.active_configs[task.config_id]
            
            # Schedule sync with engine
            sync_result = self.sync_engine.schedule_sync(task.config_id)
            
            if not sync_result['success']:
                raise RuntimeError(sync_result.get('error', 'Unknown sync error'))
            
            # Create execution result
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result = ExecutionResult(
                task_id=task.task_id,
                execution_id=execution_id,
                start_time=start_time,
                end_time=end_time,
                status="completed",
                results=sync_result,
                duration_seconds=duration
            )
            
            self.logger.log_event(
                event_type=EventType.SYNC_COMPLETED,
                source_system="scheduler",
                operation="run_sync_task",
                status="completed",
                details={
                    'task_id': task.task_id,
                    'execution_id': execution_id,
                    'duration_seconds': duration,
                    'sync_results': sync_result
                },
                duration_ms=int(duration * 1000)
            )
            
            return result
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result = ExecutionResult(
                task_id=task.task_id,
                execution_id=execution_id,
                start_time=start_time,
                end_time=end_time,
                status="failed",
                results={},
                error_message=str(e),
                duration_seconds=duration
            )
            
            # Handle retries
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.scheduled_time = datetime.now() + timedelta(minutes=5 * task.retry_count)
                heapq.heappush(self.task_queue, task)
                
                self.logger.logger.warning(f"Task {task.task_id} failed, scheduling retry {task.retry_count}/{task.max_retries}")
            else:
                self.logger.create_error_report(
                    error_type="task_execution_failed",
                    error_message=str(e),
                    context={
                        'task_id': task.task_id,
                        'config_id': task.config_id,
                        'retry_count': task.retry_count
                    },
                    affected_assets=[],
                    severity="HIGH"
                )
            
            self.logger.log_event(
                event_type=EventType.SYNC_FAILED,
                source_system="scheduler",
                operation="run_sync_task",
                status="failed",
                details={
                    'task_id': task.task_id,
                    'execution_id': execution_id,
                    'error_message': str(e),
                    'retry_count': task.retry_count
                },
                error_message=str(e),
                duration_ms=int(duration * 1000)
            )
            
            return result
    
    def _cleanup_completed_tasks(self):
        """Clean up completed tasks from active tasks"""
        completed_task_ids = []
        
        for task_id, future in self.active_tasks.items():
            if future.done():
                completed_task_ids.append(task_id)
                
                try:
                    result = future.result()
                    self.completed_tasks.append(result)
                except Exception as e:
                    self.logger.logger.error(f"Task {task_id} failed with exception: {str(e)}")
        
        # Remove completed tasks
        for task_id in completed_task_ids:
            del self.active_tasks[task_id]
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status and statistics"""
        return {
            'status': self.status.value,
            'pending_tasks': len(self.task_queue),
            'active_tasks': len(self.active_tasks),
            'completed_tasks': len(self.completed_tasks),
            'max_concurrent_tasks': self.max_concurrent_tasks,
            'next_task_time': self.task_queue[0].scheduled_time.isoformat() if self.task_queue else None
        }
    
    def get_task_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent task execution history"""
        recent_tasks = sorted(
            self.completed_tasks, 
            key=lambda x: x.start_time, 
            reverse=True
        )[:limit]
        
        return [
            {
                'task_id': task.task_id,
                'execution_id': task.execution_id,
                'start_time': task.start_time.isoformat(),
                'end_time': task.end_time.isoformat() if task.end_time else None,
                'status': task.status,
                'duration_seconds': task.duration_seconds,
                'error_message': task.error_message
            }
            for task in recent_tasks
        ]

# Example usage and testing
if __name__ == "__main__":
    print("⏰ Priority-Based Sync Scheduler")
    print("=" * 35)
    
    # Create scheduler
    scheduler = PriorityScheduler(max_concurrent_tasks=3)
    
    # Create sample configurations
    from metadata_sync_core import create_sample_config
    
    config1 = create_sample_config("datasphere", "glue")
    config1.priority_level = PriorityLevel.CRITICAL
    config1.sync_frequency = SyncFrequency.HOURLY
    
    config2 = create_sample_config("datasphere", "glue")
    config2.priority_level = PriorityLevel.MEDIUM
    config2.sync_frequency = SyncFrequency.DAILY
    
    # Register configurations
    scheduler.sync_engine.register_configuration(config1)
    scheduler.sync_engine.register_configuration(config2)
    
    # Schedule tasks
    task1_id = scheduler.schedule_task(config1, [AssetType.ANALYTICAL_MODEL])
    task2_id = scheduler.schedule_task(config2, [AssetType.VIEW, AssetType.TABLE])
    
    print(f"Scheduled tasks: {task1_id}, {task2_id}")
    
    # Get status
    status = scheduler.get_status()
    print(f"Scheduler Status: {status}")
    
    # Start scheduler for a brief test
    print("\nStarting scheduler for 3 seconds...")
    scheduler.start()
    time.sleep(3)
    scheduler.stop()
    
    # Get final status
    final_status = scheduler.get_status()
    print(f"Final Status: {final_status}")
    
    # Get task history
    history = scheduler.get_task_history()
    print(f"Task History: {len(history)} completed tasks")
    
    print(f"\n🎉 Priority scheduler tested successfully!")