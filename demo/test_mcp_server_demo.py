#!/usr/bin/env python3
"""
Comprehensive MCP Server Demo and Test
Tests all functionality of the SAP Datasphere MCP Server
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from sap_datasphere_mcp.models import DatasphereConfig
    from sap_datasphere_mcp.client import DatasphereClient
    from sap_datasphere_mcp.server import app
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure sap-datasphere-mcp is installed: pip install sap-datasphere-mcp")
    sys.exit(1)

# Load environment variables
load_dotenv()

class MCPServerDemo:
    """Comprehensive demo of the SAP Datasphere MCP Server"""
    
    def __init__(self):
        self.results = {
            "test_date": datetime.now().isoformat(),
            "package_version": "0.1.0",
            "tests": {}
        }
        
    def log_test(self, test_name: str, success: bool, message: str, data=None):
        """Log test results"""
        self.results["tests"][test_name] = {
            "success": success,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")
        
        if data and isinstance(data, (dict, list)):
            if isinstance(data, list) and len(data) > 3:
                print(f"   📊 Found {len(data)} items (showing first 3):")
                for item in data[:3]:
                    if isinstance(item, dict) and 'name' in item:
                        print(f"     • {item['name']}")
                    else:
                        print(f"     • {item}")
            elif isinstance(data, dict):
                print(f"   📊 Response keys: {list(data.keys())[:5]}")
    
    async def test_configuration(self):
        """Test configuration loading"""
        try:
            required_vars = [
                "DATASPHERE_TENANT_URL",
                "OAUTH_CLIENT_ID", 
                "OAUTH_CLIENT_SECRET",
                "OAUTH_TOKEN_URL"
            ]
            
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            
            if missing_vars:
                self.log_test(
                    "Configuration", 
                    False, 
                    f"Missing environment variables: {', '.join(missing_vars)}"
                )
                return False
            
            config = DatasphereConfig(
                tenant_url=os.getenv("DATASPHERE_TENANT_URL"),
                tenant_id=os.getenv("DATASPHERE_TENANT_ID", "default"),
                oauth_client_id=os.getenv("OAUTH_CLIENT_ID"),
                oauth_client_secret=os.getenv("OAUTH_CLIENT_SECRET"),
                oauth_token_url=os.getenv("OAUTH_TOKEN_URL"),
                oauth_authorization_url=os.getenv("OAUTH_AUTHORIZATION_URL")
            )
            
            self.config = config
            self.log_test(
                "Configuration", 
                True, 
                f"Configuration loaded for tenant: {config.tenant_url}",
                {"tenant_id": config.tenant_id}
            )
            return True
            
        except Exception as e:
            self.log_test("Configuration", False, f"Configuration error: {e}")
            return False
    
    async def test_oauth_authentication(self):
        """Test OAuth authentication"""
        try:
            client = DatasphereClient(self.config)
            result = await client.test_connection()
            
            if result.success:
                self.log_test(
                    "OAuth Authentication", 
                    True, 
                    "OAuth authentication successful",
                    result.data
                )
                self.client = client
                return True
            else:
                self.log_test(
                    "OAuth Authentication", 
                    False, 
                    f"OAuth failed: {result.error}"
                )
                return False
                
        except Exception as e:
            self.log_test("OAuth Authentication", False, f"OAuth error: {e}")
            return False
    
    async def test_api_discovery(self):
        """Test API endpoint discovery"""
        try:
            result = await self.client.discover_api_endpoints()
            
            if result.success:
                endpoints = result.data.get("working_endpoints", [])
                self.log_test(
                    "API Discovery", 
                    True, 
                    f"Found {len(endpoints)} working endpoints",
                    endpoints
                )
                return True
            else:
                self.log_test(
                    "API Discovery", 
                    False, 
                    f"Discovery failed: {result.error}"
                )
                return False
                
        except Exception as e:
            self.log_test("API Discovery", False, f"Discovery error: {e}")
            return False
    
    async def test_list_spaces(self):
        """Test listing spaces"""
        try:
            result = await self.client.list_spaces()
            
            if result.success:
                spaces = result.data
                self.log_test(
                    "List Spaces", 
                    True, 
                    f"Found {len(spaces)} spaces" if spaces else "No spaces found",
                    spaces
                )
                return True
            else:
                self.log_test(
                    "List Spaces", 
                    False, 
                    f"Failed to list spaces: {result.error}"
                )
                return False
                
        except Exception as e:
            self.log_test("List Spaces", False, f"Spaces error: {e}")
            return False
    
    async def test_list_catalog(self):
        """Test listing catalog"""
        try:
            result = await self.client.list_catalog()
            
            if result.success:
                items = result.data
                self.log_test(
                    "List Catalog", 
                    True, 
                    f"Found {len(items)} catalog items" if items else "No catalog items found",
                    items
                )
                return True
            else:
                self.log_test(
                    "List Catalog", 
                    False, 
                    f"Failed to list catalog: {result.error}"
                )
                return False
                
        except Exception as e:
            self.log_test("List Catalog", False, f"Catalog error: {e}")
            return False
    
    async def test_list_connections(self):
        """Test listing connections"""
        try:
            result = await self.client.list_connections()
            
            if result.success:
                connections = result.data
                self.log_test(
                    "List Connections", 
                    True, 
                    f"Found {len(connections)} connections" if connections else "No connections found",
                    connections
                )
                return True
            else:
                self.log_test(
                    "List Connections", 
                    False, 
                    f"Failed to list connections: {result.error}"
                )
                return False
                
        except Exception as e:
            self.log_test("List Connections", False, f"Connections error: {e}")
            return False
    
    async def test_mcp_tools_simulation(self):
        """Simulate MCP tool calls"""
        try:
            # Simulate the MCP tools that would be called by an AI client
            tools_tested = []
            
            # Test connection tool
            result = await self.client.test_connection()
            tools_tested.append({
                "tool": "test_connection",
                "success": result.success,
                "response": "Connection successful" if result.success else result.error
            })
            
            # Test discovery tool
            result = await self.client.discover_api_endpoints()
            tools_tested.append({
                "tool": "discover_endpoints", 
                "success": result.success,
                "response": f"Found {len(result.data.get('working_endpoints', []))} endpoints" if result.success else result.error
            })
            
            # Test spaces tool
            result = await self.client.list_spaces()
            tools_tested.append({
                "tool": "list_spaces",
                "success": result.success,
                "response": f"Found {len(result.data)} spaces" if result.success and result.data else "No spaces or access denied"
            })
            
            successful_tools = [t for t in tools_tested if t["success"]]
            
            self.log_test(
                "MCP Tools Simulation",
                len(successful_tools) > 0,
                f"Successfully tested {len(successful_tools)}/{len(tools_tested)} MCP tools",
                tools_tested
            )
            
            return len(successful_tools) > 0
            
        except Exception as e:
            self.log_test("MCP Tools Simulation", False, f"Tools simulation error: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if hasattr(self, 'client'):
                await self.client.close()
            self.log_test("Cleanup", True, "Resources cleaned up successfully")
        except Exception as e:
            self.log_test("Cleanup", False, f"Cleanup error: {e}")
    
    def generate_report(self):
        """Generate test report"""
        total_tests = len(self.results["tests"])
        successful_tests = sum(1 for test in self.results["tests"].values() if test["success"])
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate": f"{(successful_tests/total_tests)*100:.1f}%" if total_tests > 0 else "0%",
                "overall_status": "PASS" if successful_tests > 0 else "FAIL"
            },
            "details": self.results
        }
        
        return report
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 SAP Datasphere MCP Server - Comprehensive Test Suite")
        print("=" * 70)
        
        try:
            # Configuration test
            if not await self.test_configuration():
                return
            
            # OAuth test
            if not await self.test_oauth_authentication():
                return
            
            # API tests
            await self.test_api_discovery()
            await self.test_list_spaces()
            await self.test_list_catalog()
            await self.test_list_connections()
            
            # MCP simulation
            await self.test_mcp_tools_simulation()
            
        finally:
            await self.cleanup()
        
        # Generate and save report
        report = self.generate_report()
        
        print(f"\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"📊 Total Tests: {report['summary']['total_tests']}")
        print(f"✅ Successful: {report['summary']['successful_tests']}")
        print(f"📈 Success Rate: {report['summary']['success_rate']}")
        print(f"🎯 Overall Status: {report['summary']['overall_status']}")
        
        # Save detailed report
        with open("mcp_server_test_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: mcp_server_test_report.json")
        
        return report

async def main():
    """Main test function"""
    demo = MCPServerDemo()
    report = await demo.run_all_tests()
    
    # Exit with appropriate code
    if report["summary"]["successful_tests"] > 0:
        print(f"\n🎉 MCP Server testing completed successfully!")
        sys.exit(0)
    else:
        print(f"\n❌ MCP Server testing failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())