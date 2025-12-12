# SAP Datasphere MCP Server - Test Suite

## Overview

Comprehensive integration and unit tests for the SAP Datasphere MCP Server.

## Test Structure

```
tests/
├── __init__.py                  # Test suite initialization
├── conftest.py                  # Pytest fixtures and configuration
├── test_foundation_tools.py     # Foundation and discovery tools tests
├── README.md                    # This file
```

## Prerequisites

### 1. Install Test Dependencies

```bash
pip install -e ".[test]"
```

Or manually install:

```bash
pip install pytest pytest-asyncio pytest-cov responses
```

### 2. Configure Environment

Create a `.env` file with OAuth credentials:

```bash
DATASPHERE_BASE_URL=https://your-tenant.eu20.hcs.cloud.sap
DATASPHERE_CLIENT_ID=sb-xxxxx!b130936|client!b3944
DATASPHERE_CLIENT_SECRET=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx$xxxxx
DATASPHERE_TOKEN_URL=https://your-tenant.authentication.eu20.hana.ondemand.com/oauth/token
DATASPHERE_TENANT_ID=your-tenant-id
USE_MOCK_DATA=false
LOG_LEVEL=INFO
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=. --cov-report=html --cov-report=term
```

### Run Specific Test File

```bash
pytest tests/test_foundation_tools.py -v
```

### Run Specific Test Class

```bash
pytest tests/test_foundation_tools.py::TestFoundationTools -v
```

### Run Specific Test Method

```bash
pytest tests/test_foundation_tools.py::TestFoundationTools::test_connection -v
```

### Run by Marker

```bash
# Run only integration tests
pytest -m integration

# Run only unit tests
pytest -m unit

# Run cache tests
pytest -m cache

# Skip slow tests
pytest -m "not slow"
```

## Test Categories

### 1. Foundation Tools Tests

**File**: `test_foundation_tools.py`

**Tests**:
- `test_connection()` - OAuth connection validation
- `test_get_current_user()` - User JWT token parsing
- `test_get_tenant_info()` - Tenant information retrieval
- `test_list_spaces()` - Space discovery
- `test_get_available_scopes()` - OAuth scope validation

**Purpose**: Validate core authentication and connection functionality

### 2. Data Discovery Tests

**File**: `test_foundation_tools.py::TestDataDiscovery`

**Tests**:
- `test_get_space_info()` - Space details retrieval
- `test_list_catalog_assets()` - Catalog asset listing
- `test_search_tables()` - Table search with keywords
- `test_get_table_schema()` - Schema retrieval with column types

**Purpose**: Validate data discovery and metadata exploration

### 3. ETL Workflow Tests

**File**: `test_foundation_tools.py::TestETLWorkflow`

**Tests**:
- `test_complete_etl_workflow()` - End-to-end ETL process
- `test_large_batch_extraction()` - Large dataset pagination

**Purpose**: Validate complete ETL data extraction workflows

### 4. Cache Performance Tests

**File**: `test_foundation_tools.py::TestCachePerformance`

**Tests**:
- `test_cache_hit_rate()` - Cache performance improvement validation
- `test_cache_expiration()` - TTL-based expiration testing

**Purpose**: Validate caching improves performance

## Test Fixtures

### Configuration Fixtures

- `test_config` - Test configuration from environment variables
- `oauth_credentials` - OAuth credentials for authentication
- `sap_datasphere_url` - SAP Datasphere base URL

### Sample Data Fixtures

- `sample_space_id` - Default space ID for testing ("SAP_CONTENT")
- `sample_asset_name` - Default asset name for testing
- `mock_api_response` - Mock API response data
- `mock_table_schema` - Mock table schema
- `mock_odata_response` - Mock OData query response

### Cache Control Fixtures

- `cache_enabled` - Enable caching for test
- `cache_disabled` - Disable caching for test

## Custom Pytest Markers

```python
@pytest.mark.integration  # Test requires live API
@pytest.mark.unit         # Unit test, no external dependencies
@pytest.mark.slow         # Slow-running test
@pytest.mark.cache        # Cache-related test
```

## Test Implementation Status

### Completed

- ✅ Test structure and fixtures
- ✅ Foundation tools test templates
- ✅ Data discovery test templates
- ✅ ETL workflow test templates
- ✅ Cache performance test templates

### TODO

- ⏳ Implement actual MCP client integration
- ⏳ Add authentication tests
- ⏳ Add error handling tests
- ⏳ Add authorization tests
- ⏳ Add SQL sanitization tests
- ⏳ Add performance benchmarking

## Writing New Tests

### Example Test

```python
import pytest
from typing import Dict, Any

class TestNewFeature:
    """Test suite for new feature"""

    @pytest.mark.asyncio
    async def test_new_tool(self, oauth_credentials, sap_datasphere_url):
        """Test new MCP tool"""
        # Arrange
        tool_name = "new_tool"
        params = {"param1": "value1"}

        # Act
        result = await self.call_mcp_tool(tool_name, params)

        # Assert
        assert result is not None
        assert "expected_field" in result
        assert result["status"] == "success"

    async def call_mcp_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call MCP tool (to be implemented with actual client)"""
        raise NotImplementedError("MCP client integration needed")
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -e ".[test]"
      - name: Run tests
        run: |
          pytest --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Troubleshooting Tests

### Issue: Tests Skip Due to Missing Credentials

**Solution**: Ensure `.env` file contains all required OAuth credentials

```bash
# Check environment variables
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('DATASPHERE_BASE_URL'))"
```

### Issue: Tests Fail with Connection Timeout

**Solution**: Check network connectivity and SAP Datasphere tenant status

```bash
# Test connectivity
curl https://your-tenant.eu20.hcs.cloud.sap
```

### Issue: Cache Tests Fail

**Solution**: Ensure cache manager is initialized properly

```bash
# Run cache tests in verbose mode
pytest tests/test_foundation_tools.py::TestCachePerformance -v -s
```

## Test Coverage Goals

| Component | Target Coverage |
|-----------|----------------|
| Foundation Tools | 95%+ |
| Catalog Tools | 90%+ |
| ETL Tools | 85%+ |
| Cache Manager | 80%+ |
| Auth Layer | 95%+ |
| Overall | 85%+ |

## Contributing Tests

1. Follow existing test structure
2. Use descriptive test names
3. Add docstrings explaining what is tested
4. Use fixtures for common setup
5. Mark tests appropriately (unit/integration/slow)
6. Ensure tests are deterministic
7. Clean up resources after tests

## Next Steps

1. Implement MCP client for actual server communication
2. Add more comprehensive test coverage
3. Set up CI/CD pipeline
4. Add performance benchmarking
5. Create test data generators
6. Add stress tests for high-load scenarios

---

**Test Suite Version**: 1.0.0
**Last Updated**: December 12, 2025
**Status**: Foundation Complete, MCP Client Integration Pending
