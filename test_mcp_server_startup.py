"""
Test MCP Server Startup and Tool Registration
Verifies that the server starts correctly and all tools are registered
"""

import asyncio
import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('')  # Enable ANSI escape codes
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

async def test_server_startup():
    """Test that MCP server starts and registers all tools"""

    print("=" * 80)
    print("Testing MCP Server Startup and Tool Registration")
    print("=" * 80)
    print()

    try:
        # Import the server
        from sap_datasphere_mcp_server import server
        print("✅ Server module imported successfully")
        print()

        # Try to list tools
        print("Attempting to list registered tools...")
        print()

        # Access the list_tools handler directly
        if hasattr(server, 'list_tools'):
            list_tools_handler = server.list_tools
            print("✅ list_tools method found")

            # Get all handlers (the decorator stores them by request class type)
            from mcp.types import ListToolsRequest
            if hasattr(server, 'request_handlers') and ListToolsRequest in server.request_handlers:
                handler_func = server.request_handlers[ListToolsRequest]
                print("✅ ListToolsRequest handler found in request_handlers")

                # Call the handler with a ListToolsRequest object
                request = ListToolsRequest()
                result = await handler_func(request)

                # ServerResult has a 'root' attribute containing the actual response
                tools_response = result.root
                tools_list = tools_response.tools
                print(f"✅ Tools retrieved: {len(tools_list)} tools registered")
                print()

                # Print all tool names
                print("Registered Tools:")
                print("-" * 80)
                for idx, tool in enumerate(tools_list, 1):
                    print(f"{idx:2}. {tool.name}")
                print()

                # Check for the tools mentioned in the error
                error_tools = [
                    "search_catalog",
                    "get_consumption_metadata",
                    "get_relational_metadata",
                    "get_analytical_metadata",
                    "get_catalog_metadata",
                    "search_repository",
                    "get_analytical_model",
                    "list_repository_objects",
                    "list_analytical_datasets",
                    "get_object_definition",
                    "get_deployed_objects",
                    "query_analytical_data",
                    "get_analytical_service_document"
                ]

                tool_names = [t.name for t in tools_list]

                print("Checking tools mentioned in error:")
                print("-" * 80)
                for tool in error_tools:
                    status = "✅ FOUND" if tool in tool_names else "❌ MISSING"
                    print(f"{status:12} {tool}")
                print()

            else:
                print("❌ Could not find ListToolsRequest in request_handlers")
                print(f"Available handlers: {list(server.request_handlers.keys())}")
                print()
        else:
            print("❌ Server does not have list_tools method")
            print(f"Server attributes: {[a for a in dir(server) if not a.startswith('_')]}")
            print()

    except Exception as e:
        print(f"❌ Error during server startup test: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("=" * 80)
    print("Server Startup Test Complete")
    print("=" * 80)
    return True

if __name__ == "__main__":
    success = asyncio.run(test_server_startup())
    sys.exit(0 if success else 1)
