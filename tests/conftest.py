"""
Pytest configuration and shared fixtures for SAP Datasphere MCP Server tests

This file provides common test fixtures and configuration for all test modules.
"""

import pytest
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Add parent directory to path to import server modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables from .env file
load_dotenv()


@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    """
    Provide test configuration from environment variables

    Returns:
        Dict containing test configuration including OAuth credentials
    """
    return {
        "base_url": os.getenv("DATASPHERE_BASE_URL"),
        "client_id": os.getenv("DATASPHERE_CLIENT_ID"),
        "client_secret": os.getenv("DATASPHERE_CLIENT_SECRET"),
        "token_url": os.getenv("DATASPHERE_TOKEN_URL"),
        "tenant_id": os.getenv("DATASPHERE_TENANT_ID"),
        "use_mock_data": os.getenv("USE_MOCK_DATA", "false").lower() == "true",
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
    }


@pytest.fixture(scope="session")
def oauth_credentials(test_config: Dict[str, Any]) -> Dict[str, str]:
    """
    Provide OAuth credentials for authentication tests

    Args:
        test_config: Test configuration fixture

    Returns:
        Dict containing OAuth credentials
    """
    required_credentials = ["client_id", "client_secret", "token_url"]

    missing = [key for key in required_credentials if not test_config.get(key)]

    if missing:
        pytest.skip(f"Missing OAuth credentials: {', '.join(missing)}")

    return {
        "client_id": test_config["client_id"],
        "client_secret": test_config["client_secret"],
        "token_url": test_config["token_url"],
    }


@pytest.fixture(scope="session")
def sap_datasphere_url(test_config: Dict[str, Any]) -> str:
    """
    Provide SAP Datasphere base URL

    Args:
        test_config: Test configuration fixture

    Returns:
        SAP Datasphere base URL
    """
    base_url = test_config.get("base_url")
    if not base_url:
        pytest.skip("DATASPHERE_BASE_URL not configured")
    return base_url


@pytest.fixture
def sample_space_id() -> str:
    """Provide a sample space ID for testing"""
    return "SAP_CONTENT"


@pytest.fixture
def sample_asset_name() -> str:
    """Provide a sample asset name for testing"""
    return "SAP_SC_SALES_V_Fact_Sales"


@pytest.fixture
def mock_api_response() -> Dict[str, Any]:
    """
    Provide a mock API response for testing without live API calls

    Returns:
        Mock API response data
    """
    return {
        "spaces": [
            {"id": "SAP_CONTENT", "name": "SAP Content"},
            {"id": "DEVAULT_SPACE", "name": "Default Space"},
        ],
        "total_count": 2
    }


@pytest.fixture
def mock_table_schema() -> Dict[str, Any]:
    """
    Provide mock table schema for testing

    Returns:
        Mock table schema data
    """
    return {
        "table_name": "SAP_SC_SALES_V_Fact_Sales",
        "columns": [
            {
                "name": "SALES_ORDER_ID",
                "type": "NVARCHAR(10)",
                "nullable": False,
                "key": True
            },
            {
                "name": "CUSTOMER_ID",
                "type": "NVARCHAR(10)",
                "nullable": False
            },
            {
                "name": "AMOUNT",
                "type": "DECIMAL(18,2)",
                "nullable": True
            },
            {
                "name": "ORDER_DATE",
                "type": "DATE",
                "nullable": True
            }
        ],
        "column_count": 4
    }


@pytest.fixture
def mock_odata_response() -> Dict[str, Any]:
    """
    Provide mock OData query response

    Returns:
        Mock OData response with data
    """
    return {
        "@odata.context": "$metadata#Results",
        "@odata.count": 3,
        "value": [
            {
                "SALES_ORDER_ID": "SO001",
                "CUSTOMER_ID": "C12345",
                "AMOUNT": 1500.00,
                "ORDER_DATE": "2025-01-15"
            },
            {
                "SALES_ORDER_ID": "SO002",
                "CUSTOMER_ID": "C12346",
                "AMOUNT": 2300.50,
                "ORDER_DATE": "2025-01-16"
            },
            {
                "SALES_ORDER_ID": "SO003",
                "CUSTOMER_ID": "C12347",
                "AMOUNT": 890.25,
                "ORDER_DATE": "2025-01-17"
            }
        ]
    }


@pytest.fixture(scope="function")
def cache_enabled():
    """
    Fixture to enable caching for specific tests

    Yields after setting environment variable, then restores
    """
    original_value = os.getenv("CACHE_ENABLED")
    os.environ["CACHE_ENABLED"] = "true"
    yield
    if original_value is not None:
        os.environ["CACHE_ENABLED"] = original_value
    else:
        os.environ.pop("CACHE_ENABLED", None)


@pytest.fixture(scope="function")
def cache_disabled():
    """
    Fixture to disable caching for specific tests

    Yields after setting environment variable, then restores
    """
    original_value = os.getenv("CACHE_ENABLED")
    os.environ["CACHE_ENABLED"] = "false"
    yield
    if original_value is not None:
        os.environ["CACHE_ENABLED"] = original_value
    else:
        os.environ.pop("CACHE_ENABLED", None)


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (requires live API)"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test (no external dependencies)"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "cache: mark test as cache-related"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names"""
    for item in items:
        # Add integration marker to tests that use live APIs
        if "test_connection" in item.nodeid or "test_oauth" in item.nodeid:
            item.add_marker(pytest.mark.integration)

        # Add cache marker to cache tests
        if "cache" in item.nodeid.lower():
            item.add_marker(pytest.mark.cache)

        # Add slow marker to ETL and large batch tests
        if "etl" in item.nodeid.lower() or "large_batch" in item.nodeid.lower():
            item.add_marker(pytest.mark.slow)
