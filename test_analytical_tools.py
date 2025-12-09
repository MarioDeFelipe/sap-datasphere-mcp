"""
Test the new Phase 4.1 Analytical Model Access Tools
Tests list_analytical_datasets, get_analytical_model, query_analytical_data, and get_analytical_service_document tools
"""

import asyncio
import json
from sap_datasphere_mcp_server import _execute_tool

async def test_analytical_tools():
    """Test all four new analytical tools with mock data"""

    print("=" * 80)
    print("Testing Phase 4.1 Analytical Model Access Tools")
    print("=" * 80)
    print()

    # Test 1: list_analytical_datasets
    print("[Test 1] Testing list_analytical_datasets tool")
    print("-" * 80)

    datasets_args = {
        "space_id": "SAP_CONTENT",
        "asset_id": "SAP_SC_FI_AM_FINTRANSACTIONS",
        "top": 10,
        "skip": 0
    }

    try:
        result = await _execute_tool("list_analytical_datasets", datasets_args)
        print("[PASS] list_analytical_datasets - SUCCESS")
        print(f"Result preview: {result[0].text[:300]}...")

        # Verify structure - extract JSON from response
        text = result[0].text
        json_start = text.find('{')
        if json_start != -1:
            data = json.loads(text[json_start:text.rfind('}')+1])
            assert "value" in data, "Missing value array"
            print(f"  Datasets found: {len(data['value'])}")
        print()
    except Exception as e:
        print(f"[FAIL] list_analytical_datasets - FAILED: {e}")
        print()

    # Test 2: get_analytical_model
    print("[Test 2] Testing get_analytical_model tool")
    print("-" * 80)

    model_args = {
        "space_id": "SAP_CONTENT",
        "asset_id": "SAP_SC_FI_AM_FINTRANSACTIONS",
        "include_metadata": True
    }

    try:
        result = await _execute_tool("get_analytical_model", model_args)
        print("[PASS] get_analytical_model - SUCCESS")
        print(f"Result preview: {result[0].text[:300]}...")

        # Verify structure
        text = result[0].text
        json_start = text.find('{')
        if json_start != -1:
            data = json.loads(text[json_start:text.rfind('}')+1])
            assert "value" in data, "Missing value"
            if "metadata" in data:
                print(f"  Metadata included: Yes")
                if "entity_sets" in data["metadata"] and len(data["metadata"]["entity_sets"]) > 0:
                    entity_set = data["metadata"]["entity_sets"][0]
                    print(f"  Dimensions: {len(entity_set.get('dimensions', []))}")
                    print(f"  Measures: {len(entity_set.get('measures', []))}")
        print()
    except Exception as e:
        print(f"[FAIL] get_analytical_model - FAILED: {e}")
        print()

    # Test 3: query_analytical_data (simple query)
    print("[Test 3] Testing query_analytical_data tool (simple query)")
    print("-" * 80)

    query_args = {
        "space_id": "SAP_CONTENT",
        "asset_id": "SAP_SC_FI_AM_FINTRANSACTIONS",
        "entity_set": "SAP_SC_FI_AM_FINTRANSACTIONS",
        "select": "TransactionID,Amount,Currency",
        "top": 10
    }

    try:
        result = await _execute_tool("query_analytical_data", query_args)
        print("[PASS] query_analytical_data (simple) - SUCCESS")
        print(f"Result preview: {result[0].text[:300]}...")

        # Verify structure
        text = result[0].text
        json_start = text.find('{')
        if json_start != -1:
            # Find the last } that closes the main object
            data = json.loads(text[json_start:text.rfind('}')+1])
            assert "value" in data, "Missing value array"
            print(f"  Records returned: {len(data['value'])}")
        print()
    except Exception as e:
        print(f"[FAIL] query_analytical_data (simple) - FAILED: {e}")
        print()

    # Test 4: query_analytical_data (with filter)
    print("[Test 4] Testing query_analytical_data tool (with filter)")
    print("-" * 80)

    query_filter_args = {
        "space_id": "SAP_CONTENT",
        "asset_id": "SAP_SC_FI_AM_FINTRANSACTIONS",
        "entity_set": "SAP_SC_FI_AM_FINTRANSACTIONS",
        "select": "Currency,Amount",
        "filter": "Amount gt 10000",
        "orderby": "Amount desc",
        "top": 5
    }

    try:
        result = await _execute_tool("query_analytical_data", query_filter_args)
        print("[PASS] query_analytical_data (with filter) - SUCCESS")
        print(f"Result preview: {result[0].text[:300]}...")
        print()
    except Exception as e:
        print(f"[FAIL] query_analytical_data (with filter) - FAILED: {e}")
        print()

    # Test 5: query_analytical_data (with aggregation)
    print("[Test 5] Testing query_analytical_data tool (with aggregation)")
    print("-" * 80)

    query_agg_args = {
        "space_id": "SAP_CONTENT",
        "asset_id": "SAP_SC_FI_AM_FINTRANSACTIONS",
        "entity_set": "SAP_SC_FI_AM_FINTRANSACTIONS",
        "apply": "groupby((Currency), aggregate(Amount with sum as TotalAmount))",
        "count": True
    }

    try:
        result = await _execute_tool("query_analytical_data", query_agg_args)
        print("[PASS] query_analytical_data (aggregation) - SUCCESS")
        print(f"Result preview: {result[0].text[:300]}...")

        # Verify aggregated structure
        text = result[0].text
        json_start = text.find('{')
        if json_start != -1:
            data = json.loads(text[json_start:text.rfind('}')+1])
            if "@odata.count" in data:
                print(f"  Total count included: {data['@odata.count']}")
            if "value" in data and len(data["value"]) > 0:
                print(f"  Aggregated groups: {len(data['value'])}")
                first_group = data["value"][0]
                print(f"  First group: {first_group}")
        print()
    except Exception as e:
        print(f"[FAIL] query_analytical_data (aggregation) - FAILED: {e}")
        print()

    # Test 6: get_analytical_service_document
    print("[Test 6] Testing get_analytical_service_document tool")
    print("-" * 80)

    service_doc_args = {
        "space_id": "SAP_CONTENT",
        "asset_id": "SAP_SC_FI_AM_FINTRANSACTIONS"
    }

    try:
        result = await _execute_tool("get_analytical_service_document", service_doc_args)
        print("[PASS] get_analytical_service_document - SUCCESS")
        print(f"Result preview: {result[0].text[:300]}...")

        # Verify structure
        text = result[0].text
        json_start = text.find('{')
        if json_start != -1:
            data = json.loads(text[json_start:text.rfind('}')+1])
            assert "value" in data, "Missing value array"
            print(f"  Entity sets in service: {len(data['value'])}")
        print()
    except Exception as e:
        print(f"[FAIL] get_analytical_service_document - FAILED: {e}")
        print()

    # Test 7: get_analytical_model (without metadata)
    print("[Test 7] Testing get_analytical_model tool (without metadata)")
    print("-" * 80)

    model_no_meta_args = {
        "space_id": "SAP_CONTENT",
        "asset_id": "SAP_SC_FI_AM_FINTRANSACTIONS",
        "include_metadata": False
    }

    try:
        result = await _execute_tool("get_analytical_model", model_no_meta_args)
        print("[PASS] get_analytical_model (no metadata) - SUCCESS")
        print(f"Result preview: {result[0].text[:300]}...")

        # Verify no metadata included
        text = result[0].text
        json_start = text.find('{')
        if json_start != -1:
            data = json.loads(text[json_start:text.rfind('}')+1])
            has_metadata = "metadata" in data
            print(f"  Metadata included: {has_metadata}")
            assert not has_metadata, "Should not have metadata when include_metadata=False"
        print()
    except Exception as e:
        print(f"[FAIL] get_analytical_model (no metadata) - FAILED: {e}")
        print()

    print("=" * 80)
    print("All Phase 4.1 Analytical Model Access Tools tests completed!")
    print("=" * 80)
    print()
    print("Summary:")
    print("- list_analytical_datasets: Discover analytical models in an asset")
    print("- get_analytical_model: Get service document and metadata with dimensions/measures")
    print("- query_analytical_data: Execute OData queries with full syntax support")
    print("- get_analytical_service_document: Get service capabilities and entity sets")
    print()
    print("Next steps:")
    print("1. Run this test script: python test_analytical_tools.py")
    print("2. Verify all tests pass")
    print("3. Update README.md with Phase 4.1 analytical tools")
    print("4. Commit changes with comprehensive commit message")
    print("5. Test with real SAP Datasphere connection (USE_MOCK_DATA=false)")

if __name__ == "__main__":
    asyncio.run(test_analytical_tools())
