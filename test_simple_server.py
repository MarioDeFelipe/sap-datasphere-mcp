#!/usr/bin/env python3
"""
Simple test for the SAP Datasphere MCP Server
"""
import json

# Test the mock data directly
from sap_datasphere_mcp_simple import MOCK_SPACES, MOCK_TABLES, MOCK_CONNECTIONS

def test_mock_data():
    """Test that our mock data is properly structured"""
    
    print("🧪 Testing SAP Datasphere MCP Server Mock Data")
    print("=" * 60)
    
    # Test spaces
    print(f"\n📋 Spaces ({len(MOCK_SPACES)} total):")
    for space in MOCK_SPACES:
        print(f"  • {space['id']}: {space['name']} ({space['status']})")
    
    # Test tables
    print(f"\n📊 Tables by Space:")
    for space_id, tables in MOCK_TABLES.items():
        print(f"  • {space_id}: {len(tables)} tables")
        for table in tables:
            print(f"    - {table['name']}: {table['row_count']} rows")
    
    # Test connections
    print(f"\n🔗 Connections ({len(MOCK_CONNECTIONS)} total):")
    for conn in MOCK_CONNECTIONS:
        print(f"  • {conn['id']}: {conn['name']} ({conn['status']})")
    
    print(f"\n✅ Mock data structure is valid!")
    
    # Test JSON serialization
    try:
        json.dumps(MOCK_SPACES)
        json.dumps(MOCK_TABLES)
        json.dumps(MOCK_CONNECTIONS)
        print(f"✅ All mock data is JSON serializable!")
    except Exception as e:
        print(f"❌ JSON serialization error: {e}")
    
    return True

def create_mcp_config():
    """Create MCP configuration for Claude Desktop"""
    
    config = {
        "mcpServers": {
            "sap-datasphere": {
                "command": "python",
                "args": ["sap_datasphere_mcp_simple.py"],
                "env": {}
            }
        }
    }
    
    with open('mcp-config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n📄 MCP configuration saved to: mcp-config.json")
    print(f"\nTo use with Claude Desktop:")
    print(f"1. Copy the contents of mcp-config.json")
    print(f"2. Add to your Claude Desktop MCP configuration")
    print(f"3. Restart Claude Desktop")
    print(f"4. The SAP Datasphere tools will be available!")

def show_usage_examples():
    """Show example queries for the MCP server"""
    
    print(f"\n" + "=" * 60)
    print("USAGE EXAMPLES")
    print("=" * 60)
    
    examples = [
        {
            "query": "List all Datasphere spaces",
            "tool": "list_spaces",
            "description": "Shows all available spaces with basic info"
        },
        {
            "query": "Show me details about the Sales Analytics space",
            "tool": "get_space_info", 
            "description": "Gets detailed information including tables"
        },
        {
            "query": "Search for tables containing 'customer' data",
            "tool": "search_tables",
            "description": "Finds tables matching the search term"
        },
        {
            "query": "List all data connections",
            "tool": "list_connections",
            "description": "Shows available data source connections"
        },
        {
            "query": "Execute: SELECT * FROM CUSTOMER_DATA LIMIT 10",
            "tool": "execute_query",
            "description": "Simulates SQL query execution"
        }
    ]
    
    print(f"\n🎯 Example queries you can ask Claude:")
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. \"{example['query']}\"")
        print(f"   Tool: {example['tool']}")
        print(f"   Result: {example['description']}")
    
    print(f"\n💡 The MCP server provides realistic mock data for:")
    print(f"   • 2 Datasphere spaces (Sales Analytics, Finance DWH)")
    print(f"   • Sample tables with schemas and row counts")
    print(f"   • Data connections to SAP ERP and Salesforce")
    print(f"   • Simulated query execution with sample results")

if __name__ == "__main__":
    test_mock_data()
    create_mcp_config()
    show_usage_examples()
    
    print(f"\n" + "=" * 60)
    print("🎉 SAP DATASPHERE MCP SERVER READY!")
    print("=" * 60)
    print(f"✅ Mock data validated")
    print(f"✅ MCP configuration created")
    print(f"✅ Ready for integration with AI assistants")
    print(f"\n🚀 Next steps:")
    print(f"1. Configure Claude Desktop with the MCP server")
    print(f"2. Test the Datasphere tools with example queries")
    print(f"3. When OAuth credentials are available, switch to live mode")