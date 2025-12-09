"""
Test the new Phase 3.2 Repository Object Discovery Tools
Tests list_repository_objects, get_object_definition, and get_deployed_objects tools
"""

import asyncio
import json
from sap_datasphere_mcp_server import _execute_tool

async def test_repository_tools():
    """Test all three repository discovery tools with mock data"""

    print("=" * 80)
    print("Testing Phase 3.2 Repository Object Discovery Tools")
    print("=" * 80)
    print()

    # Test 1: list_repository_objects (all objects)
    print("[Test 1] Testing list_repository_objects tool (all objects)")
    print("-" * 80)

    list_all_args = {
        "space_id": "SAP_CONTENT"
    }

    try:
        result = await _execute_tool("list_repository_objects", list_all_args)
        print("[PASS] list_repository_objects (all) - SUCCESS")
        print(f"Result preview: {result[0].text[:300]}...")

        # Verify structure - extract JSON from response
        text = result[0].text
        json_start = text.find('{')
        if json_start != -1:
            data = json.loads(text[json_start:text.rfind('}') + 1])
            assert "objects" in data, "Missing objects"
            assert "summary" in data, "Missing summary"
            print(f"  Objects found: {data['returned_count']}")
            print(f"  Object types: {list(data['summary']['by_type'].keys())}")
        print()
    except Exception as e:
        print(f"[FAIL] list_repository_objects (all) - FAILED: {e}")
        print()

    # Test 2: list_repository_objects (filtered by type)
    print("[Test 2] Testing list_repository_objects tool (Tables only)")
    print("-" * 80)

    list_tables_args = {
        "space_id": "SAP_CONTENT",
        "object_types": ["Table"]
    }

    try:
        result = await _execute_tool("list_repository_objects", list_tables_args)
        print("[PASS] list_repository_objects (tables) - SUCCESS")
        print(f"Result preview: {result[0].text[:300]}...")

        # Verify structure
        text = result[0].text
        json_start = text.find('{')
        if json_start != -1:
            data = json.loads(text[json_start:text.rfind('}') + 1])
            assert len(data['objects']) > 0, "No tables found"
            assert all(obj['objectType'] == 'Table' for obj in data['objects']), "Non-table objects returned"
            print(f"  Tables found: {len(data['objects'])}")
        print()
    except Exception as e:
        print(f"[FAIL] list_repository_objects (tables) - FAILED: {e}")
        print()

    # Test 3: list_repository_objects (with dependencies)
    print("[Test 3] Testing list_repository_objects tool (with dependencies)")
    print("-" * 80)

    list_deps_args = {
        "space_id": "SAP_CONTENT",
        "include_dependencies": True,
        "top": 10
    }

    try:
        result = await _execute_tool("list_repository_objects", list_deps_args)
        print("[PASS] list_repository_objects (dependencies) - SUCCESS")
        print(f"Result preview: {result[0].text[:300]}...")

        # Verify dependencies are included
        text = result[0].text
        json_start = text.find('{')
        if json_start != -1:
            data = json.loads(text[json_start:text.rfind('}') + 1])
            has_deps = any('dependencies' in obj for obj in data['objects'])
            assert has_deps, "Dependencies not included"
            print(f"  Objects with dependencies: {sum(1 for obj in data['objects'] if 'dependencies' in obj)}")
        print()
    except Exception as e:
        print(f"[FAIL] list_repository_objects (dependencies) - FAILED: {e}")
        print()

    # Test 4: get_object_definition
    print("[Test 4] Testing get_object_definition tool (full definition)")
    print("-" * 80)

    object_def_args = {
        "space_id": "SAP_CONTENT",
        "object_id": "FINANCIAL_TRANSACTIONS",
        "include_full_definition": True,
        "include_dependencies": True
    }

    try:
        result = await _execute_tool("get_object_definition", object_def_args)
        print("[PASS] get_object_definition (full) - SUCCESS")
        print(f"Result preview: {result[0].text[:300]}...")

        # Verify structure
        text = result[0].text
        json_start = text.find('{')
        if json_start != -1:
            data = json.loads(text[json_start:text.rfind('}') + 1])
            assert "definition" in data, "Missing definition"
            assert "dependencies" in data, "Missing dependencies"
            print(f"  Object type: {data.get('objectType')}")
            print(f"  Definition type: {data.get('definition', {}).get('type')}")
            print(f"  Columns: {len(data.get('definition', {}).get('columns', []))}")
        print()
    except Exception as e:
        print(f"[FAIL] get_object_definition (full) - FAILED: {e}")
        print()

    # Test 5: get_object_definition (minimal)
    print("[Test 5] Testing get_object_definition tool (minimal)")
    print("-" * 80)

    object_minimal_args = {
        "space_id": "SAP_CONTENT",
        "object_id": "CUSTOMER_VIEW",
        "include_full_definition": False,
        "include_dependencies": False
    }

    try:
        result = await _execute_tool("get_object_definition", object_minimal_args)
        print("[PASS] get_object_definition (minimal) - SUCCESS")
        print(f"Result preview: {result[0].text[:300]}...")
        print()
    except Exception as e:
        print(f"[FAIL] get_object_definition (minimal) - FAILED: {e}")
        print()

    # Test 6: get_deployed_objects (all)
    print("[Test 6] Testing get_deployed_objects tool (all deployed)")
    print("-" * 80)

    deployed_all_args = {
        "space_id": "SAP_CONTENT",
        "include_metrics": True
    }

    try:
        result = await _execute_tool("get_deployed_objects", deployed_all_args)
        print("[PASS] get_deployed_objects (all) - SUCCESS")
        print(f"Result preview: {result[0].text[:300]}...")

        # Verify structure
        text = result[0].text
        json_start = text.find('{')
        if json_start != -1:
            data = json.loads(text[json_start:text.rfind('}') + 1])
            assert "deployed_objects" in data, "Missing deployed_objects"
            assert "summary" in data, "Missing summary"
            print(f"  Deployed objects found: {data['returned_count']}")
            print(f"  By status: {data['summary']['by_status']}")
            print(f"  By type: {data['summary']['by_type']}")
        print()
    except Exception as e:
        print(f"[FAIL] get_deployed_objects (all) - FAILED: {e}")
        print()

    # Test 7: get_deployed_objects (DataFlows only)
    print("[Test 7] Testing get_deployed_objects tool (DataFlows only)")
    print("-" * 80)

    deployed_flows_args = {
        "space_id": "SAP_CONTENT",
        "object_types": ["DataFlow"],
        "include_metrics": True
    }

    try:
        result = await _execute_tool("get_deployed_objects", deployed_flows_args)
        print("[PASS] get_deployed_objects (DataFlows) - SUCCESS")
        print(f"Result preview: {result[0].text[:300]}...")

        # Verify only DataFlows returned
        text = result[0].text
        json_start = text.find('{')
        if json_start != -1:
            data = json.loads(text[json_start:text.rfind('}') + 1])
            assert all(obj['objectType'] == 'DataFlow' for obj in data['deployed_objects']), "Non-DataFlow objects returned"
            print(f"  DataFlows found: {len(data['deployed_objects'])}")
            # Check for execution metrics
            has_metrics = any('runtimeMetrics' in obj for obj in data['deployed_objects'])
            print(f"  Has runtime metrics: {has_metrics}")
        print()
    except Exception as e:
        print(f"[FAIL] get_deployed_objects (DataFlows) - FAILED: {e}")
        print()

    # Test 8: get_deployed_objects (by runtime status)
    print("[Test 8] Testing get_deployed_objects tool (Active only)")
    print("-" * 80)

    deployed_active_args = {
        "space_id": "SAP_CONTENT",
        "runtime_status": "Active",
        "include_metrics": False
    }

    try:
        result = await _execute_tool("get_deployed_objects", deployed_active_args)
        print("[PASS] get_deployed_objects (Active) - SUCCESS")
        print(f"Result preview: {result[0].text[:300]}...")

        # Verify only Active objects returned
        text = result[0].text
        json_start = text.find('{')
        if json_start != -1:
            data = json.loads(text[json_start:text.rfind('}') + 1])
            assert all(obj['runtimeStatus'] == 'Active' for obj in data['deployed_objects']), "Non-Active objects returned"
            print(f"  Active objects found: {len(data['deployed_objects'])}")
        print()
    except Exception as e:
        print(f"[FAIL] get_deployed_objects (Active) - FAILED: {e}")
        print()

    # Test 9: Pagination test
    print("[Test 9] Testing list_repository_objects with pagination")
    print("-" * 80)

    pagination_args = {
        "space_id": "SAP_CONTENT",
        "top": 2,
        "skip": 0
    }

    try:
        result = await _execute_tool("list_repository_objects", pagination_args)
        print("[PASS] list_repository_objects (pagination) - SUCCESS")
        print(f"Result preview: {result[0].text[:300]}...")

        # Verify pagination
        text = result[0].text
        json_start = text.find('{')
        if json_start != -1:
            data = json.loads(text[json_start:text.rfind('}') + 1])
            assert data['returned_count'] <= 2, "Returned more than requested"
            assert "has_more" in data, "Missing has_more field"
            print(f"  Returned count: {data['returned_count']}")
            print(f"  Has more: {data['has_more']}")
        print()
    except Exception as e:
        print(f"[FAIL] list_repository_objects (pagination) - FAILED: {e}")
        print()

    print("=" * 80)
    print("All Phase 3.2 Repository Object Discovery Tools tests completed!")
    print("=" * 80)
    print()
    print("Summary:")
    print("- list_repository_objects: Browse all repository objects with filtering and dependencies")
    print("- get_object_definition: Get complete design-time object definitions with structure")
    print("- get_deployed_objects: List runtime/deployed objects with metrics and execution status")
    print()
    print("Next steps:")
    print("1. Run this test script: python test_repository_tools.py")
    print("2. Verify all tests pass")
    print("3. Update README.md with Phase 3.2 repository tools")
    print("4. Commit changes with comprehensive commit message")
    print("5. Test with real SAP Datasphere connection (USE_MOCK_DATA=false)")

if __name__ == "__main__":
    asyncio.run(test_repository_tools())
