#!/usr/bin/env python3
"""
Logging and Error Handling Infrastructure for Metadata Synchronization
Provides structured logging, audit trails, and error management
"""

import logging
import json
import csv
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass, field
import traceback
import os

class LogLevel(Enum):
    """Log levels for structured logging"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class EventType(Enum):
    """Types of events for audit logging"""
    SYNC_STARTED = "sync_started"
    SYNC_COMPLETED = "sync_completed"
    SYNC_FAILED = "sync_failed"
    SYNC_SCHEDULED = "sync_scheduled"
    SYNC_RETRYING = "sync_retrying"
    ASSET_CREATED = "asset_created"
    ASSET_UPDATED = "asset_updated"
    ASSET_DELETED = "asset_deleted"
    CONFLICT_DETECTED = "conflict_detected"
    AUTHENTICATION_SUCCESS = "auth_success"
    AUTHENTICATION_FAILURE = "auth_failure"
    CONFIGURATION_CHANGED = "config_changed"
    ERROR_OCCURRED = "error_occurred"
    SYSTEM_STARTED = "system_started"
    SYSTEM_STOPPED = "system_stopped"

@dataclass
class AuditLogEntry:
    """Structured audit log entry"""
    timestamp: datetime
    event_type: EventType
    source_system: str
    target_system: Optional[str]
    user_id: Optional[str]
    session_id: Optional[str]
    asset_id: Optional[str]
    asset_type: Optional[str]
    operation: str
    status: str
    details: Dict[str, Any]
    error_message: Optional[str] = None
    duration_ms: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type.value,
            'source_system': self.source_system,
            'target_system': self.target_system,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'asset_id': self.asset_id,
            'asset_type': self.asset_type,
            'operation': self.operation,
            'status': self.status,
            'details': self.details,
            'error_message': self.error_message,
            'duration_ms': self.duration_ms
        }

@dataclass
class ErrorReport:
    """Structured error report with remediation suggestions"""
    error_id: str
    timestamp: datetime
    error_type: str
    error_message: str
    stack_trace: Optional[str]
    context: Dict[str, Any]
    affected_assets: List[str]
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    remediation_suggestions: List[str]
    is_resolved: bool = False
    resolution_notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'error_id': self.error_id,
            'timestamp': self.timestamp.isoformat(),
            'error_type': self.error_type,
            'error_message': self.error_message,
            'stack_trace': self.stack_trace,
            'context': self.context,
            'affected_assets': self.affected_assets,
            'severity': self.severity,
            'remediation_suggestions': self.remediation_suggestions,
            'is_resolved': self.is_resolved,
            'resolution_notes': self.resolution_notes
        }

class SyncLogger:
    """Enhanced logger for metadata synchronization operations"""
    
    def __init__(self, name: str = "metadata_sync", log_level: LogLevel = LogLevel.INFO):
        self.name = name
        self.log_level = log_level
        self.audit_logs: List[AuditLogEntry] = []
        self.error_reports: List[ErrorReport] = []
        
        # Configure Python logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.value))
        
        # Create formatter for structured logging
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            
            # File handler for persistent logging
            file_handler = logging.FileHandler('metadata_sync.log')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def log_event(self, event_type: EventType, source_system: str, operation: str, 
                  status: str, details: Dict[str, Any], target_system: Optional[str] = None,
                  user_id: Optional[str] = None, session_id: Optional[str] = None,
                  asset_id: Optional[str] = None, asset_type: Optional[str] = None,
                  error_message: Optional[str] = None, duration_ms: Optional[int] = None):
        """Log a structured audit event"""
        
        audit_entry = AuditLogEntry(
            timestamp=datetime.now(),
            event_type=event_type,
            source_system=source_system,
            target_system=target_system,
            user_id=user_id,
            session_id=session_id,
            asset_id=asset_id,
            asset_type=asset_type,
            operation=operation,
            status=status,
            details=details,
            error_message=error_message,
            duration_ms=duration_ms
        )
        
        self.audit_logs.append(audit_entry)
        
        # Log to Python logger as well
        log_message = f"{event_type.value} - {operation} - {status}"
        if error_message:
            log_message += f" - Error: {error_message}"
        
        if status.lower() in ['failed', 'error']:
            self.logger.error(log_message)
        elif status.lower() == 'warning':
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
    
    def log_sync_started(self, sync_id: str, config_id: str, source_system: str, 
                        target_system: str, asset_count: int):
        """Log synchronization start event"""
        self.log_event(
            event_type=EventType.SYNC_STARTED,
            source_system=source_system,
            target_system=target_system,
            operation=f"sync_{sync_id}",
            status="started",
            details={
                'sync_id': sync_id,
                'config_id': config_id,
                'asset_count': asset_count
            }
        )
    
    def log_sync_completed(self, sync_id: str, results: Dict[str, Any], duration_ms: int):
        """Log synchronization completion event"""
        self.log_event(
            event_type=EventType.SYNC_COMPLETED,
            source_system=results.get('source_system', 'unknown'),
            target_system=results.get('target_system', 'unknown'),
            operation=f"sync_{sync_id}",
            status="completed",
            details=results,
            duration_ms=duration_ms
        )
    
    def log_sync_failed(self, sync_id: str, error_message: str, context: Dict[str, Any]):
        """Log synchronization failure event"""
        self.log_event(
            event_type=EventType.SYNC_FAILED,
            source_system=context.get('source_system', 'unknown'),
            target_system=context.get('target_system', 'unknown'),
            operation=f"sync_{sync_id}",
            status="failed",
            details=context,
            error_message=error_message
        )
    
    def log_asset_operation(self, operation: str, asset_id: str, asset_type: str, 
                           source_system: str, target_system: str, status: str,
                           details: Dict[str, Any], error_message: Optional[str] = None):
        """Log asset-level operations"""
        event_type_map = {
            'create': EventType.ASSET_CREATED,
            'update': EventType.ASSET_UPDATED,
            'delete': EventType.ASSET_DELETED
        }
        
        event_type = event_type_map.get(operation.lower(), EventType.ASSET_UPDATED)
        
        self.log_event(
            event_type=event_type,
            source_system=source_system,
            target_system=target_system,
            asset_id=asset_id,
            asset_type=asset_type,
            operation=operation,
            status=status,
            details=details,
            error_message=error_message
        )
    
    def log_conflict(self, asset_id: str, conflict_type: str, details: Dict[str, Any]):
        """Log conflict detection"""
        self.log_event(
            event_type=EventType.CONFLICT_DETECTED,
            source_system=details.get('source_system', 'unknown'),
            target_system=details.get('target_system', 'unknown'),
            asset_id=asset_id,
            operation=f"conflict_{conflict_type}",
            status="detected",
            details=details
        )
    
    def create_error_report(self, error_type: str, error_message: str, 
                           context: Dict[str, Any], affected_assets: List[str],
                           severity: str = "MEDIUM") -> str:
        """Create a structured error report with remediation suggestions"""
        
        error_id = f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.error_reports):03d}"
        
        # Generate remediation suggestions based on error type
        remediation_suggestions = self._generate_remediation_suggestions(error_type, error_message, context)
        
        error_report = ErrorReport(
            error_id=error_id,
            timestamp=datetime.now(),
            error_type=error_type,
            error_message=error_message,
            stack_trace=traceback.format_exc() if context.get('include_stack_trace') else None,
            context=context,
            affected_assets=affected_assets,
            severity=severity,
            remediation_suggestions=remediation_suggestions
        )
        
        self.error_reports.append(error_report)
        
        # Log the error
        self.logger.error(f"Error Report {error_id}: {error_type} - {error_message}")
        
        return error_id
    
    def _generate_remediation_suggestions(self, error_type: str, error_message: str, 
                                        context: Dict[str, Any]) -> List[str]:
        """Generate remediation suggestions based on error type"""
        suggestions = []
        
        error_type_lower = error_type.lower()
        error_message_lower = error_message.lower()
        
        if 'authentication' in error_type_lower or 'auth' in error_type_lower:
            suggestions.extend([
                "Check OAuth token validity and expiration",
                "Verify client credentials and permissions",
                "Ensure network connectivity to authentication server",
                "Review IAM roles and policies"
            ])
        
        elif 'schema' in error_type_lower or 'mapping' in error_type_lower:
            suggestions.extend([
                "Review data type mappings between source and target systems",
                "Check for column name conflicts or missing fields",
                "Validate transformation rules and field mappings",
                "Consider using conflict resolution strategies"
            ])
        
        elif 'network' in error_type_lower or 'connection' in error_type_lower:
            suggestions.extend([
                "Check network connectivity and firewall settings",
                "Verify API endpoints and service availability",
                "Implement retry logic with exponential backoff",
                "Review rate limiting and throttling settings"
            ])
        
        elif 'permission' in error_type_lower or 'access' in error_type_lower:
            suggestions.extend([
                "Verify user permissions and access rights",
                "Check IAM roles and policies",
                "Review resource-level permissions",
                "Ensure proper authentication scope"
            ])
        
        else:
            suggestions.extend([
                "Review error logs for additional context",
                "Check system configuration and settings",
                "Verify data integrity and format",
                "Consider contacting system administrator"
            ])
        
        return suggestions
    
    def export_audit_logs(self, format: str = "json", filename: Optional[str] = None,
                         start_date: Optional[datetime] = None, 
                         end_date: Optional[datetime] = None) -> str:
        """Export audit logs in specified format"""
        
        # Filter logs by date range if specified
        filtered_logs = self.audit_logs
        if start_date:
            filtered_logs = [log for log in filtered_logs if log.timestamp >= start_date]
        if end_date:
            filtered_logs = [log for log in filtered_logs if log.timestamp <= end_date]
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"audit_logs_{timestamp}.{format.lower()}"
        
        if format.lower() == "json":
            with open(filename, 'w') as f:
                json.dump([log.to_dict() for log in filtered_logs], f, indent=2)
        
        elif format.lower() == "csv":
            if filtered_logs:
                with open(filename, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=filtered_logs[0].to_dict().keys())
                    writer.writeheader()
                    for log in filtered_logs:
                        writer.writerow(log.to_dict())
        
        self.logger.info(f"Exported {len(filtered_logs)} audit log entries to {filename}")
        return filename
    
    def export_error_reports(self, format: str = "json", filename: Optional[str] = None) -> str:
        """Export error reports in specified format"""
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"error_reports_{timestamp}.{format.lower()}"
        
        if format.lower() == "json":
            with open(filename, 'w') as f:
                json.dump([report.to_dict() for report in self.error_reports], f, indent=2)
        
        elif format.lower() == "csv":
            if self.error_reports:
                with open(filename, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=self.error_reports[0].to_dict().keys())
                    writer.writeheader()
                    for report in self.error_reports:
                        writer.writerow(report.to_dict())
        
        self.logger.info(f"Exported {len(self.error_reports)} error reports to {filename}")
        return filename
    
    def get_audit_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get audit summary for the specified time period"""
        cutoff_time = datetime.now().replace(hour=datetime.now().hour - hours)
        recent_logs = [log for log in self.audit_logs if log.timestamp >= cutoff_time]
        
        summary = {
            'total_events': len(recent_logs),
            'time_period_hours': hours,
            'event_types': {},
            'status_counts': {},
            'error_count': 0,
            'systems': set()
        }
        
        for log in recent_logs:
            # Count event types
            event_type = log.event_type.value
            summary['event_types'][event_type] = summary['event_types'].get(event_type, 0) + 1
            
            # Count status
            summary['status_counts'][log.status] = summary['status_counts'].get(log.status, 0) + 1
            
            # Count errors
            if log.error_message:
                summary['error_count'] += 1
            
            # Track systems
            summary['systems'].add(log.source_system)
            if log.target_system:
                summary['systems'].add(log.target_system)
        
        summary['systems'] = list(summary['systems'])
        return summary

# Global logger instance
sync_logger = SyncLogger()

# Example usage and testing
if __name__ == "__main__":
    print("📊 Sync Logging Infrastructure")
    print("=" * 35)
    
    # Test logging functionality
    logger = SyncLogger("test_sync")
    
    # Log various events
    logger.log_sync_started("sync_001", "config_001", "datasphere", "glue", 10)
    
    logger.log_asset_operation(
        operation="create",
        asset_id="asset_001",
        asset_type="table",
        source_system="datasphere",
        target_system="glue",
        status="completed",
        details={"table_name": "customer_data", "columns": 5}
    )
    
    logger.log_conflict(
        asset_id="asset_002",
        conflict_type="schema_mismatch",
        details={
            "source_system": "datasphere",
            "target_system": "glue",
            "conflict_details": "Column type mismatch: VARCHAR vs STRING"
        }
    )
    
    # Create error report
    error_id = logger.create_error_report(
        error_type="authentication_error",
        error_message="OAuth token expired",
        context={"source_system": "datasphere", "operation": "get_tables"},
        affected_assets=["asset_001", "asset_002"],
        severity="HIGH"
    )
    
    print(f"Created error report: {error_id}")
    
    # Get audit summary
    summary = logger.get_audit_summary(hours=1)
    print(f"\nAudit Summary: {json.dumps(summary, indent=2)}")
    
    # Export logs
    json_file = logger.export_audit_logs(format="json")
    print(f"Exported audit logs to: {json_file}")
    
    print(f"\n🎉 Logging infrastructure initialized successfully!")