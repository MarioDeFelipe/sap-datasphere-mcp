"""
Test Authorization Coverage
Verifies that all MCP tools are registered in the authorization manager
"""

import asyncio
import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('')  # Enable ANSI escape codes
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

async def test_authorization_coverage():
    """Test that all MCP tools have authorization permissions defined"""

    print("=" * 80)
    print("Testing Authorization Coverage for All MCP Tools")
    print("=" * 80)
    print()

    try:
        # Import server and authorization manager
        from sap_datasphere_mcp_server import server
        from auth.authorization import AuthorizationManager
        from mcp.types import ListToolsRequest

        print("✅ Modules imported successfully")
        print()

        # Get all registered tools from MCP server
        handler_func = server.request_handlers[ListToolsRequest]
        request = ListToolsRequest()
        result = await handler_func(request)
        tools_list = result.root.tools
        tool_names = [t.name for t in tools_list]

        print(f"✅ Found {len(tool_names)} registered MCP tools")
        print()

        # Get all tools with authorization permissions
        auth_manager = AuthorizationManager()
        authorized_tools = set(auth_manager.TOOL_PERMISSIONS.keys())

        print(f"✅ Found {len(authorized_tools)} tools with authorization permissions")
        print()

        # Check for missing tools
        missing_tools = set(tool_names) - authorized_tools
        extra_tools = authorized_tools - set(tool_names)

        if missing_tools:
            print("❌ TOOLS MISSING FROM AUTHORIZATION MANAGER:")
            print("-" * 80)
            for tool in sorted(missing_tools):
                print(f"  - {tool}")
            print()
        else:
            print("✅ All MCP tools have authorization permissions defined")
            print()

        if extra_tools:
            print("⚠️  TOOLS IN AUTHORIZATION BUT NOT IN MCP SERVER:")
            print("-" * 80)
            for tool in sorted(extra_tools):
                print(f"  - {tool}")
            print()

        # Test authorization checks for all tools
        print("Testing authorization checks:")
        print("-" * 80)

        errors = []
        for tool_name in tool_names:
            allowed, reason = auth_manager.check_permission(tool_name)

            if not allowed and reason and "Unknown tool" in reason:
                errors.append(f"❌ {tool_name}: {reason}")
                print(f"❌ {tool_name}: Authorization check failed - {reason}")
            else:
                permission = auth_manager.TOOL_PERMISSIONS[tool_name]
                status = "🔒 Requires consent" if permission.requires_consent else "✅ No consent"
                print(f"{status:20} {tool_name:35} [{permission.risk_level:6}] {permission.permission_level.value}")

        print()

        if errors:
            print("=" * 80)
            print("AUTHORIZATION ERRORS FOUND:")
            print("=" * 80)
            for error in errors:
                print(error)
            print()
            return False

        print("=" * 80)
        print("✅ All Authorization Tests Passed!")
        print("=" * 80)
        print()
        print("Summary:")
        print(f"  - Total tools: {len(tool_names)}")
        print(f"  - Tools with permissions: {len(authorized_tools)}")
        print(f"  - Tools requiring consent: {sum(1 for p in auth_manager.TOOL_PERMISSIONS.values() if p.requires_consent)}")
        print(f"  - Read-only tools: {sum(1 for p in auth_manager.TOOL_PERMISSIONS.values() if p.permission_level.value == 'read')}")
        print(f"  - Write tools: {sum(1 for p in auth_manager.TOOL_PERMISSIONS.values() if p.permission_level.value == 'write')}")
        print(f"  - Admin tools: {sum(1 for p in auth_manager.TOOL_PERMISSIONS.values() if p.permission_level.value == 'admin')}")
        print()

        return True

    except Exception as e:
        print(f"❌ Error during authorization coverage test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_authorization_coverage())
    sys.exit(0 if success else 1)
