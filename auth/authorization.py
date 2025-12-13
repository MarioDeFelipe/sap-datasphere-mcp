#!/usr/bin/env python3
"""
Authorization Framework for SAP Datasphere MCP Server
Implements permission levels and access control for MCP tools
"""

import logging
from enum import Enum
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


class PermissionLevel(Enum):
    """Permission levels for MCP tools"""
    READ = "read"           # Read-only operations (list, get, search)
    WRITE = "write"         # Data modification operations (execute queries)
    ADMIN = "admin"         # Administrative operations (connections, tasks)
    SENSITIVE = "sensitive"  # Sensitive data access (credentials, PII)


class ToolCategory(Enum):
    """Categorization of tools by their function"""
    METADATA = "metadata"          # Metadata discovery
    DATA_ACCESS = "data_access"    # Direct data access
    QUERY = "query"                # Query execution
    ADMINISTRATION = "administration"  # Admin functions
    CONNECTION = "connection"      # Connection management


@dataclass
class ToolPermission:
    """Permission configuration for a specific tool"""
    tool_name: str
    permission_level: PermissionLevel
    category: ToolCategory
    requires_consent: bool
    description: str
    risk_level: str  # "low", "medium", "high"


class AuthorizationManager:
    """
    Manages authorization and permissions for MCP tools

    Features:
    - Tool-level permission enforcement
    - Risk-based categorization
    - Consent tracking
    - Audit logging
    """

    # Tool permission registry
    TOOL_PERMISSIONS: Dict[str, ToolPermission] = {
        # Read-only metadata operations (low risk)
        "list_spaces": ToolPermission(
            tool_name="list_spaces",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.METADATA,
            requires_consent=False,
            description="List available Datasphere spaces",
            risk_level="low"
        ),
        "get_space_info": ToolPermission(
            tool_name="get_space_info",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.METADATA,
            requires_consent=False,
            description="Get detailed information about a space",
            risk_level="low"
        ),
        "search_tables": ToolPermission(
            tool_name="search_tables",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.METADATA,
            requires_consent=False,
            description="Search for tables and views",
            risk_level="low"
        ),
        "get_table_schema": ToolPermission(
            tool_name="get_table_schema",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.METADATA,
            requires_consent=False,
            description="Get table schema information",
            risk_level="low"
        ),

        # Data access operations (medium risk)
        "execute_query": ToolPermission(
            tool_name="execute_query",
            permission_level=PermissionLevel.WRITE,
            category=ToolCategory.QUERY,
            requires_consent=True,
            description="Execute SQL queries on Datasphere data",
            risk_level="high"
        ),

        # Administrative operations (high risk)
        "list_connections": ToolPermission(
            tool_name="list_connections",
            permission_level=PermissionLevel.ADMIN,
            category=ToolCategory.CONNECTION,
            requires_consent=True,
            description="List data source connections",
            risk_level="medium"
        ),
        "get_task_status": ToolPermission(
            tool_name="get_task_status",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.ADMINISTRATION,
            requires_consent=False,
            description="Get status of data integration tasks",
            risk_level="low"
        ),
        "browse_marketplace": ToolPermission(
            tool_name="browse_marketplace",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.METADATA,
            requires_consent=False,
            description="Browse Datasphere marketplace packages",
            risk_level="low"
        ),
        "find_assets_by_column": ToolPermission(
            tool_name="find_assets_by_column",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.METADATA,
            requires_consent=False,
            description="Find assets containing specific column names for data lineage",
            risk_level="low"
        ),
        "analyze_column_distribution": ToolPermission(
            tool_name="analyze_column_distribution",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.DATA_ACCESS,
            requires_consent=False,
            description="Perform statistical analysis of column data distribution",
            risk_level="low"
        ),

        # Database user management operations (high risk - require consent)
        "list_database_users": ToolPermission(
            tool_name="list_database_users",
            permission_level=PermissionLevel.ADMIN,
            category=ToolCategory.ADMINISTRATION,
            requires_consent=False,
            description="List database users in a space",
            risk_level="medium"
        ),
        "create_database_user": ToolPermission(
            tool_name="create_database_user",
            permission_level=PermissionLevel.ADMIN,
            category=ToolCategory.ADMINISTRATION,
            requires_consent=True,
            description="Create a new database user with permissions",
            risk_level="high"
        ),
        "reset_database_user_password": ToolPermission(
            tool_name="reset_database_user_password",
            permission_level=PermissionLevel.SENSITIVE,
            category=ToolCategory.ADMINISTRATION,
            requires_consent=True,
            description="Reset database user password (generates new credentials)",
            risk_level="high"
        ),
        "update_database_user": ToolPermission(
            tool_name="update_database_user",
            permission_level=PermissionLevel.ADMIN,
            category=ToolCategory.ADMINISTRATION,
            requires_consent=True,
            description="Update database user permissions and configuration",
            risk_level="high"
        ),
        "delete_database_user": ToolPermission(
            tool_name="delete_database_user",
            permission_level=PermissionLevel.ADMIN,
            category=ToolCategory.ADMINISTRATION,
            requires_consent=True,
            description="Permanently delete a database user (irreversible)",
            risk_level="high"
        ),
        "list_catalog_assets": ToolPermission(
            tool_name="list_catalog_assets",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.METADATA,
            requires_consent=False,
            description="Browse all assets across all Datasphere spaces",
            risk_level="low"
        ),
        "get_asset_details": ToolPermission(
            tool_name="get_asset_details",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.METADATA,
            requires_consent=False,
            description="Get detailed metadata for a specific asset",
            risk_level="low"
        ),
        "get_asset_by_compound_key": ToolPermission(
            tool_name="get_asset_by_compound_key",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.METADATA,
            requires_consent=False,
            description="Retrieve asset using OData compound key",
            risk_level="low"
        ),
        "get_space_assets": ToolPermission(
            tool_name="get_space_assets",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.METADATA,
            requires_consent=False,
            description="List all assets within a specific space",
            risk_level="low"
        ),

        # Phase 2.2: Universal Search Tools
        "search_catalog": ToolPermission(
            tool_name="search_catalog",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.METADATA,
            requires_consent=False,
            description="Universal catalog search with advanced syntax",
            risk_level="low"
        ),
        "search_repository": ToolPermission(
            tool_name="search_repository",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.METADATA,
            requires_consent=False,
            description="Repository object search with lineage tracking",
            risk_level="low"
        ),
        "get_catalog_metadata": ToolPermission(
            tool_name="get_catalog_metadata",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.METADATA,
            requires_consent=False,
            description="Retrieve CSDL metadata schema for catalog service",
            risk_level="low"
        ),

        # Phase 3.1: Metadata & Schema Discovery Tools
        "get_consumption_metadata": ToolPermission(
            tool_name="get_consumption_metadata",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.METADATA,
            requires_consent=False,
            description="Get consumption layer metadata (OData schema)",
            risk_level="low"
        ),
        "get_analytical_metadata": ToolPermission(
            tool_name="get_analytical_metadata",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.METADATA,
            requires_consent=False,
            description="Get analytical metadata with dimensions/measures identification",
            risk_level="low"
        ),
        "get_relational_metadata": ToolPermission(
            tool_name="get_relational_metadata",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.METADATA,
            requires_consent=False,
            description="Get relational metadata with SQL type mapping",
            risk_level="low"
        ),
        "get_repository_search_metadata": ToolPermission(
            tool_name="get_repository_search_metadata",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.METADATA,
            requires_consent=False,
            description="Get searchable object types and field metadata",
            risk_level="low"
        ),

        # Phase 3.2: Repository Object Discovery Tools
        "list_repository_objects": ToolPermission(
            tool_name="list_repository_objects",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.METADATA,
            requires_consent=False,
            description="Browse repository objects with filtering and dependencies",
            risk_level="low"
        ),
        "get_object_definition": ToolPermission(
            tool_name="get_object_definition",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.METADATA,
            requires_consent=False,
            description="Get complete design-time object definitions",
            risk_level="low"
        ),
        "get_deployed_objects": ToolPermission(
            tool_name="get_deployed_objects",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.METADATA,
            requires_consent=False,
            description="List runtime/deployed objects with execution metrics",
            risk_level="low"
        ),

        # Phase 4.1: Analytical Model Access Tools
        "list_analytical_datasets": ToolPermission(
            tool_name="list_analytical_datasets",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.METADATA,
            requires_consent=False,
            description="List all analytical datasets available for querying",
            risk_level="low"
        ),
        "get_analytical_model": ToolPermission(
            tool_name="get_analytical_model",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.METADATA,
            requires_consent=False,
            description="Get analytical model structure and metadata",
            risk_level="low"
        ),
        "query_analytical_data": ToolPermission(
            tool_name="query_analytical_data",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.DATA_ACCESS,
            requires_consent=False,
            description="Query analytical model data with OData parameters",
            risk_level="medium"
        ),
        "get_analytical_service_document": ToolPermission(
            tool_name="get_analytical_service_document",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.METADATA,
            requires_consent=False,
            description="Get OData service document for analytical model",
            risk_level="low"
        ),

        # Connection and testing tools
        "get_connection_info": ToolPermission(
            tool_name="get_connection_info",
            permission_level=PermissionLevel.ADMIN,
            category=ToolCategory.CONNECTION,
            requires_consent=False,
            description="Get detailed information about a specific connection",
            risk_level="medium"
        ),
        "test_connection": ToolPermission(
            tool_name="test_connection",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.CONNECTION,
            requires_consent=False,
            description="Test OAuth authentication and server connectivity",
            risk_level="low"
        ),
        "get_current_user": ToolPermission(
            tool_name="get_current_user",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.METADATA,
            requires_consent=False,
            description="Get authenticated user information and permissions",
            risk_level="low"
        ),
        "get_tenant_info": ToolPermission(
            tool_name="get_tenant_info",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.METADATA,
            requires_consent=False,
            description="Get SAP Datasphere tenant configuration and system info",
            risk_level="low"
        ),
        "get_available_scopes": ToolPermission(
            tool_name="get_available_scopes",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.METADATA,
            requires_consent=False,
            description="List available OAuth2 scopes and permissions",
            risk_level="low"
        ),

        # Diagnostic Tool: Test Phase 6 & 7 endpoint availability
        "test_phase67_endpoints": ToolPermission(
            tool_name="test_phase67_endpoints",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.ADMINISTRATION,
            requires_consent=False,
            description="Test availability of Phase 6 & 7 API endpoints",
            risk_level="low"
        ),

        # Diagnostic Tool: Test Phase 8 endpoint availability
        "test_phase8_endpoints": ToolPermission(
            tool_name="test_phase8_endpoints",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.ADMINISTRATION,
            requires_consent=False,
            description="Test availability of Phase 8 API endpoints (Data Sharing, AI Features, Legacy APIs)",
            risk_level="low"
        ),

        # Diagnostic Tool: Test Analytical & Query endpoints
        "test_analytical_endpoints": ToolPermission(
            tool_name="test_analytical_endpoints",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.ADMINISTRATION,
            requires_consent=False,
            description="Test availability of Analytical and Query API endpoints (6 remaining mock tools)",
            risk_level="low"
        ),

        # Phase 5.1: ETL-Optimized Relational Data Access Tools
        "list_relational_entities": ToolPermission(
            tool_name="list_relational_entities",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.METADATA,
            requires_consent=False,
            description="List available relational entities for ETL extraction",
            risk_level="low"
        ),

        "get_relational_entity_metadata": ToolPermission(
            tool_name="get_relational_entity_metadata",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.METADATA,
            requires_consent=False,
            description="Get entity metadata with SQL type mappings for ETL",
            risk_level="low"
        ),

        "query_relational_entity": ToolPermission(
            tool_name="query_relational_entity",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.DATA_ACCESS,
            requires_consent=False,
            description="Execute ETL-optimized queries (up to 50K records)",
            risk_level="medium"
        ),

        "get_relational_odata_service": ToolPermission(
            tool_name="get_relational_odata_service",
            permission_level=PermissionLevel.READ,
            category=ToolCategory.METADATA,
            requires_consent=False,
            description="Get OData service document for ETL planning",
            risk_level="low"
        ),

        # Phase 6 & 7 tools removed (endpoints not available as REST APIs)
    }

    def __init__(self):
        """Initialize authorization manager"""
        self._consent_granted: Set[str] = set()
        self._consent_denied: Set[str] = set()
        self._audit_log: List[Dict] = []

        logger.info("Authorization manager initialized")

    def check_permission(
        self,
        tool_name: str,
        user_id: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Check if a tool can be executed

        Args:
            tool_name: Name of the tool to check
            user_id: Optional user identifier for tracking

        Returns:
            Tuple of (allowed: bool, reason: Optional[str])
        """
        # Get tool permission configuration
        tool_permission = self.TOOL_PERMISSIONS.get(tool_name)

        if not tool_permission:
            logger.warning(f"Unknown tool: {tool_name}")
            return False, f"Unknown tool: {tool_name}"

        # Check if consent is required
        if tool_permission.requires_consent:
            if tool_name in self._consent_denied:
                reason = f"Consent denied for {tool_name}"
                logger.warning(reason)
                self._log_authorization_decision(
                    tool_name=tool_name,
                    allowed=False,
                    reason=reason,
                    user_id=user_id
                )
                return False, reason

            if tool_name not in self._consent_granted:
                reason = f"Consent required for {tool_name}"
                logger.info(reason)
                return False, reason

        # Permission granted
        self._log_authorization_decision(
            tool_name=tool_name,
            allowed=True,
            reason="Permission granted",
            user_id=user_id
        )
        return True, None

    def grant_consent(self, tool_name: str, user_id: Optional[str] = None):
        """
        Grant consent for a specific tool

        Args:
            tool_name: Name of the tool
            user_id: Optional user identifier
        """
        self._consent_granted.add(tool_name)
        if tool_name in self._consent_denied:
            self._consent_denied.remove(tool_name)

        logger.info(f"Consent granted for tool: {tool_name}")
        self._log_authorization_decision(
            tool_name=tool_name,
            allowed=True,
            reason="User granted consent",
            user_id=user_id,
            action="consent_granted"
        )

    def deny_consent(self, tool_name: str, user_id: Optional[str] = None):
        """
        Deny consent for a specific tool

        Args:
            tool_name: Name of the tool
            user_id: Optional user identifier
        """
        self._consent_denied.add(tool_name)
        if tool_name in self._consent_granted:
            self._consent_granted.remove(tool_name)

        logger.info(f"Consent denied for tool: {tool_name}")
        self._log_authorization_decision(
            tool_name=tool_name,
            allowed=False,
            reason="User denied consent",
            user_id=user_id,
            action="consent_denied"
        )

    def revoke_consent(self, tool_name: str, user_id: Optional[str] = None):
        """
        Revoke previously granted consent

        Args:
            tool_name: Name of the tool
            user_id: Optional user identifier
        """
        if tool_name in self._consent_granted:
            self._consent_granted.remove(tool_name)

        logger.info(f"Consent revoked for tool: {tool_name}")
        self._log_authorization_decision(
            tool_name=tool_name,
            allowed=False,
            reason="User revoked consent",
            user_id=user_id,
            action="consent_revoked"
        )

    def get_tool_permission(self, tool_name: str) -> Optional[ToolPermission]:
        """
        Get permission configuration for a tool

        Args:
            tool_name: Name of the tool

        Returns:
            ToolPermission or None if not found
        """
        return self.TOOL_PERMISSIONS.get(tool_name)

    def requires_consent(self, tool_name: str) -> bool:
        """
        Check if a tool requires user consent

        Args:
            tool_name: Name of the tool

        Returns:
            True if consent is required
        """
        tool_permission = self.TOOL_PERMISSIONS.get(tool_name)
        return tool_permission.requires_consent if tool_permission else False

    def get_consent_status(self, tool_name: str) -> str:
        """
        Get consent status for a tool

        Args:
            tool_name: Name of the tool

        Returns:
            "granted", "denied", "pending", or "not_required"
        """
        if not self.requires_consent(tool_name):
            return "not_required"

        if tool_name in self._consent_granted:
            return "granted"
        elif tool_name in self._consent_denied:
            return "denied"
        else:
            return "pending"

    def get_tools_by_permission_level(
        self,
        permission_level: PermissionLevel
    ) -> List[str]:
        """
        Get all tools at a specific permission level

        Args:
            permission_level: Permission level to filter by

        Returns:
            List of tool names
        """
        return [
            tool_name
            for tool_name, permission in self.TOOL_PERMISSIONS.items()
            if permission.permission_level == permission_level
        ]

    def get_tools_requiring_consent(self) -> List[str]:
        """
        Get all tools that require user consent

        Returns:
            List of tool names requiring consent
        """
        return [
            tool_name
            for tool_name, permission in self.TOOL_PERMISSIONS.items()
            if permission.requires_consent
        ]

    def _log_authorization_decision(
        self,
        tool_name: str,
        allowed: bool,
        reason: str,
        user_id: Optional[str] = None,
        action: str = "permission_check"
    ):
        """
        Log an authorization decision for audit purposes

        Args:
            tool_name: Name of the tool
            allowed: Whether access was allowed
            reason: Reason for the decision
            user_id: Optional user identifier
            action: Type of action
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "tool_name": tool_name,
            "action": action,
            "allowed": allowed,
            "reason": reason,
            "user_id": user_id,
        }

        self._audit_log.append(entry)

        # Keep audit log size manageable (last 1000 entries)
        if len(self._audit_log) > 1000:
            self._audit_log = self._audit_log[-1000:]

    def get_audit_log(
        self,
        tool_name: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get audit log entries

        Args:
            tool_name: Optional filter by tool name
            limit: Maximum number of entries to return

        Returns:
            List of audit log entries
        """
        logs = self._audit_log

        if tool_name:
            logs = [log for log in logs if log["tool_name"] == tool_name]

        return logs[-limit:]

    def get_authorization_summary(self) -> Dict:
        """
        Get summary of authorization state

        Returns:
            Dictionary with authorization statistics
        """
        return {
            "total_tools": len(self.TOOL_PERMISSIONS),
            "tools_requiring_consent": len(self.get_tools_requiring_consent()),
            "consent_granted": len(self._consent_granted),
            "consent_denied": len(self._consent_denied),
            "consent_pending": len(self.get_tools_requiring_consent()) -
                             len(self._consent_granted) -
                             len(self._consent_denied),
            "audit_log_entries": len(self._audit_log),
            "permission_levels": {
                level.value: len(self.get_tools_by_permission_level(level))
                for level in PermissionLevel
            }
        }
