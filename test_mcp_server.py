#!/usr/bin/env python3
"""
Test script for SAP Datasphere MCP Server
"""
import asyncio
import json
from sap_datasphere_mcp_server import server

async def test_mcp_server():
    """Test the MCP server functionality"""
    
    print("🧪 Testing SAP Datasphere MCP Server")
    print("=" * 50)
    
    # Test list resources
    print("\n📋 Testing list_resources...")
    resources = await server.list_resources()()
    print(f"Found {len(resources)} resources:")
    for resource in resources:
        print(f"  • {resource.name}: {resource.uri}")
    
    # Test read resource
    print(f"\n📖 Testing read_resource...")
    spaces_data = await server.read_resource()("datasphere://spaces")
    spaces = json.loads(spaces_data)
    print(f"Spaces resource contains {len(spaces)} spaces")
    
    # Test list tools
    print(f"\n🛠️ Testing list_tools...")
    tools = await server.list_tools()()
    print(f"Found {len(tools)} tools:")
    for tool in tools:
        print(f"  • {tool.name}: {tool.description}")
    
    # Test tool calls
    print(f"\n⚡ Testing tool calls...")
    
    # Test list_spaces
    print(f"\n1. Testing list_spaces tool...")
    result = await server.call_tool()("list_spaces", {"include_details": True})
    print(f"Result: {result[0].text[:200]}...")
    
    # Test search_tables
    print(f"\n2. Testing search_tables tool...")
    result = await server.call_tool()("search_tables", {"search_term": "customer"})
    print(f"Result: {result[0].text[:200]}...")
    
    # Test get_space_info
    print(f"\n3. Testing get_space_info tool...")
    result = await server.call_tool()("get_space_info", {"space_id": "SALES_ANALYTICS"})
    print(f"Result: {result[0].text[:200]}...")
    
    # Test list_connections
    print(f"\n4. Testing list_connections tool...")
    result = await server.call_tool()("list_connections", {})
    print(f"Result: {result[0].text[:200]}...")
    
    # Test execute_query
    print(f"\n5. Testing execute_query tool...")
    result = await server.call_tool()("execute_query", {
        "space_id": "SALES_ANALYTICS",
        "sql_query": "SELECT * FROM CUSTOMER_DATA LIMIT 10"
    })
    print(f"Result: {result[0].text[:200]}...")
    
    print(f"\n✅ All tests completed successfully!")
    print(f"\n🎯 The MCP server is ready to use with AI assistants!")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())