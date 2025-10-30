#!/usr/bin/env python3
"""
Consent Manager for SAP Datasphere MCP Server
Handles user consent prompts and tracking for sensitive operations
"""

import logging
from typing import Dict, Optional, Callable, Awaitable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from auth.authorization import AuthorizationManager, ToolPermission

logger = logging.getLogger(__name__)


class ConsentResponse(Enum):
    """User consent response"""
    GRANTED = "granted"
    DENIED = "denied"
    DEFERRED = "deferred"  # Ask again later


@dataclass
class ConsentRequest:
    """Request for user consent"""
    tool_name: str
    tool_permission: ToolPermission
    context: Dict
    requested_at: datetime
    expires_at: Optional[datetime] = None


class ConsentManager:
    """
    Manages user consent for sensitive MCP tool operations

    Features:
    - Interactive consent prompts
    - Consent persistence within session
    - Consent expiration
    - Audit logging
    """

    def __init__(
        self,
        authorization_manager: AuthorizationManager,
        consent_timeout_minutes: int = 60
    ):
        """
        Initialize consent manager

        Args:
            authorization_manager: Authorization manager instance
            consent_timeout_minutes: Minutes before consent expires (0 = no expiration)
        """
        self.auth_manager = authorization_manager
        self.consent_timeout = timedelta(minutes=consent_timeout_minutes)

        # Consent request tracking
        self._active_requests: Dict[str, ConsentRequest] = {}
        self._consent_history: list = []

        logger.info(
            f"Consent manager initialized "
            f"(timeout: {consent_timeout_minutes} minutes)"
        )

    async def request_consent(
        self,
        tool_name: str,
        context: Optional[Dict] = None,
        user_id: Optional[str] = None
    ) -> tuple[bool, str]:
        """
        Request user consent for a tool operation

        This method should be called before executing sensitive operations.
        In MCP protocol, this would typically return a message to the user
        asking them to approve the operation.

        Args:
            tool_name: Name of the tool requiring consent
            context: Optional context about the operation
            user_id: Optional user identifier

        Returns:
            Tuple of (consent_needed: bool, message: str)
        """
        # Get tool permission configuration
        tool_permission = self.auth_manager.get_tool_permission(tool_name)

        if not tool_permission:
            return False, f"Unknown tool: {tool_name}"

        # Check if consent is required
        if not tool_permission.requires_consent:
            return False, "Consent not required for this operation"

        # Check current consent status
        consent_status = self.auth_manager.get_consent_status(tool_name)

        if consent_status == "granted":
            # Check if consent has expired
            if self._is_consent_expired(tool_name):
                logger.info(f"Consent expired for tool: {tool_name}")
                self.auth_manager.revoke_consent(tool_name, user_id)
            else:
                return False, "Consent already granted"

        # Create consent request
        request = ConsentRequest(
            tool_name=tool_name,
            tool_permission=tool_permission,
            context=context or {},
            requested_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + self.consent_timeout if self.consent_timeout.total_seconds() > 0 else None
        )

        self._active_requests[tool_name] = request

        # Generate consent prompt message
        message = self._generate_consent_prompt(request)

        logger.info(f"Consent requested for tool: {tool_name}")

        return True, message

    def _generate_consent_prompt(self, request: ConsentRequest) -> str:
        """
        Generate user-friendly consent prompt

        Args:
            request: Consent request

        Returns:
            Formatted consent prompt message
        """
        tool = request.tool_permission

        prompt = f"""
>>> CONSENT REQUIRED <<<

Tool: {tool.tool_name}
Permission Level: {tool.permission_level.value.upper()}
Risk Level: {tool.risk_level.upper()}
Category: {tool.category.value}

Description:
{tool.description}

This operation requires your explicit consent because:
- Permission Level: {tool.permission_level.value}
- Risk Classification: {tool.risk_level}

Context:
{self._format_context(request.context)}

To proceed with this operation, you must grant consent.
Consent will be valid for this session{f' (expires in {self.consent_timeout.total_seconds()/60:.0f} minutes)' if self.consent_timeout.total_seconds() > 0 else ''}.

Do you consent to this operation? (yes/no)
        """.strip()

        return prompt

    def _format_context(self, context: Dict) -> str:
        """Format context dictionary for display"""
        if not context:
            return "No additional context"

        lines = []
        for key, value in context.items():
            lines.append(f"- {key}: {value}")

        return "\n".join(lines)

    def handle_consent_response(
        self,
        tool_name: str,
        response: ConsentResponse,
        user_id: Optional[str] = None
    ) -> bool:
        """
        Handle user's consent response

        Args:
            tool_name: Name of the tool
            response: User's consent response
            user_id: Optional user identifier

        Returns:
            True if consent was granted
        """
        request = self._active_requests.get(tool_name)

        if not request:
            logger.warning(f"No active consent request for tool: {tool_name}")
            return False

        # Process response
        if response == ConsentResponse.GRANTED:
            self.auth_manager.grant_consent(tool_name, user_id)
            logger.info(f"User granted consent for tool: {tool_name}")
            consent_granted = True

        elif response == ConsentResponse.DENIED:
            self.auth_manager.deny_consent(tool_name, user_id)
            logger.info(f"User denied consent for tool: {tool_name}")
            consent_granted = False

        elif response == ConsentResponse.DEFERRED:
            logger.info(f"User deferred consent for tool: {tool_name}")
            consent_granted = False

        else:
            logger.warning(f"Unknown consent response: {response}")
            consent_granted = False

        # Record in history
        self._consent_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "tool_name": tool_name,
            "response": response.value,
            "user_id": user_id,
            "context": request.context
        })

        # Clean up active request
        del self._active_requests[tool_name]

        return consent_granted

    def _is_consent_expired(self, tool_name: str) -> bool:
        """
        Check if consent has expired for a tool

        Args:
            tool_name: Name of the tool

        Returns:
            True if consent has expired
        """
        if self.consent_timeout.total_seconds() == 0:
            return False  # No expiration

        # Find most recent consent in history
        for entry in reversed(self._consent_history):
            if entry["tool_name"] == tool_name and entry["response"] == "granted":
                granted_at = datetime.fromisoformat(entry["timestamp"])
                expires_at = granted_at + self.consent_timeout
                return datetime.utcnow() > expires_at

        # No consent found in history
        return True

    def revoke_all_consents(self, user_id: Optional[str] = None):
        """
        Revoke all granted consents

        Args:
            user_id: Optional user identifier
        """
        tools_requiring_consent = self.auth_manager.get_tools_requiring_consent()

        for tool_name in tools_requiring_consent:
            if self.auth_manager.get_consent_status(tool_name) == "granted":
                self.auth_manager.revoke_consent(tool_name, user_id)

        logger.info("All consents revoked")

    def get_consent_summary(self) -> Dict:
        """
        Get summary of consent status

        Returns:
            Dictionary with consent statistics
        """
        tools_requiring_consent = self.auth_manager.get_tools_requiring_consent()

        summary = {
            "total_tools_requiring_consent": len(tools_requiring_consent),
            "active_requests": len(self._active_requests),
            "consent_history_entries": len(self._consent_history),
            "tools_by_status": {},
            "timeout_minutes": self.consent_timeout.total_seconds() / 60
        }

        # Count tools by consent status
        for tool_name in tools_requiring_consent:
            status = self.auth_manager.get_consent_status(tool_name)
            summary["tools_by_status"][status] = \
                summary["tools_by_status"].get(status, 0) + 1

        return summary

    def get_pending_requests(self) -> list[str]:
        """
        Get list of tools with pending consent requests

        Returns:
            List of tool names with pending requests
        """
        return list(self._active_requests.keys())

    def cancel_request(self, tool_name: str):
        """
        Cancel a pending consent request

        Args:
            tool_name: Name of the tool
        """
        if tool_name in self._active_requests:
            del self._active_requests[tool_name]
            logger.info(f"Cancelled consent request for tool: {tool_name}")


# Helper function to create consent prompt for MCP protocol
def create_mcp_consent_prompt(
    tool_name: str,
    tool_permission: ToolPermission,
    context: Optional[Dict] = None
) -> str:
    """
    Create a consent prompt message formatted for MCP protocol

    This generates a user-facing message that can be returned
    from an MCP tool when consent is required.

    Args:
        tool_name: Name of the tool
        tool_permission: Tool permission configuration
        context: Optional context about the operation

    Returns:
        Formatted consent prompt message
    """
    return f"""
⚠️ AUTHORIZATION REQUIRED

The tool '{tool_name}' requires your explicit consent before execution.

**Tool Information:**
- **Function**: {tool_permission.description}
- **Permission Level**: {tool_permission.permission_level.value.upper()}
- **Risk Level**: {tool_permission.risk_level.upper()}
- **Category**: {tool_permission.category.value}

**Why consent is needed:**
This operation is classified as {tool_permission.risk_level} risk and requires
{tool_permission.permission_level.value} permissions.

**What will happen:**
{tool_permission.description}

**To proceed:**
Please indicate your consent by calling this tool again with explicit approval,
or use the authorization management interface to grant consent for this session.

**Security Note:**
Your consent will be logged for audit purposes and you can revoke it at any time.
    """.strip()
