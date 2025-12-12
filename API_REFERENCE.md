# SAP Datasphere MCP Server - API Reference

**Version**: 1.0
**Last Updated**: December 12, 2025
**Total Tools**: 41 working tools

This document provides technical API documentation for developers integrating with the SAP Datasphere MCP Server.

---

## 📋 Quick Reference

### Tool Categories

| Category | Tools | Purpose |
|----------|-------|---------|
| [Foundation](#foundation-tools) | 5 | Authentication, connection, tenant info |
| [Catalog](#catalog-tools) | 4 | Asset discovery and exploration |
| [Space Discovery](#space-discovery-tools) | 3 | Space and table exploration |
| [Search](#search-tools) | 2 | Keyword-based discovery |
| [Database Users](#database-user-management) | 5 | User CRUD operations |
| [Metadata](#metadata-tools) | 5 | Schema and metadata access |
| [Analytical](#analytical-consumption-tools) | 4 | OData analytical queries |
| [ETL](#etl-optimized-tools) | 4 | Large-scale data extraction |
| [Additional](#additional-tools) | 5 | Connections, tasks, marketplace |

---

## 🔐 Foundation Tools

### test_connection

**Description**: Tests OAuth 2.0 connection to SAP Datasphere

**Parameters**: None

**Response**:
```json
{
  "status": "connected",
  "tenant_url": "https://ailien-test.eu20.hcs.cloud.sap",
  "authenticated": true,
  "oauth_status": "valid",
  "message": "✅ Connection successful"
}
```

**Python Example**:
```python
result = await mcp_client.call_tool("test_connection", {})
print(result["status"])  # "connected"
```

**cURL Example**:
```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"tool": "test_connection", "arguments": {}}'
```

---

### list_spaces

**Description**: Lists all accessible SAP Datasphere spaces

**Parameters**: None

**Response**:
```json
{
  "spaces": [
    {"id": "SAP_CONTENT", "name": "SAP Content"},
    {"id": "DEVAULT_SPACE", "name": "Default Space"}
  ],
  "total_count": 2
}
```

**Python Example**:
```python
result = await mcp_client.call_tool("list_spaces", {})
for space in result["spaces"]:
    print(f"{space['id']}: {space['name']}")
```

---

## 📚 Catalog Tools

### list_catalog_assets

**Description**: Lists all assets in catalog with filtering

**Parameters**:
```typescript
{
  space_id?: string,    // Filter by space
  asset_type?: string,  // Filter by type (table/view)
  top?: number         // Max results (default: 50, max: 1000)
}
```

**Response**:
```json
{
  "assets": [
    {
      "id": "asset-123",
      "name": "SAP_SC_SALES_V_Fact_Sales",
      "type": "view",
      "space_id": "SAP_CONTENT"
    }
  ],
  "total_count": 36,
  "has_more": false
}
```

**Python Example**:
```python
# List all assets
result = await mcp_client.call_tool("list_catalog_assets", {})

# Filter by space
result = await mcp_client.call_tool("list_catalog_assets", {
    "space_id": "SAP_CONTENT",
    "top": 100
})

# Filter by type
result = await mcp_client.call_tool("list_catalog_assets", {
    "space_id": "SAP_CONTENT",
    "asset_type": "table"
})
```

**cURL Example**:
```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "list_catalog_assets",
    "arguments": {
      "space_id": "SAP_CONTENT",
      "top": 50
    }
  }'
```

---

### get_table_schema

**Description**: Retrieves column definitions and data types

**Parameters**:
```typescript
{
  space_id: string,    // Required
  table_name: string   // Required
}
```

**Response**:
```json
{
  "table_name": "SAP_SC_SALES_V_Fact_Sales",
  "space_id": "SAP_CONTENT",
  "columns": [
    {
      "name": "SALES_ORDER_ID",
      "type": "NVARCHAR(10)",
      "nullable": false,
      "primary_key": true
    },
    {
      "name": "AMOUNT",
      "type": "DECIMAL(18,2)",
      "nullable": true
    }
  ],
  "column_count": 20
}
```

**Python Example**:
```python
schema = await mcp_client.call_tool("get_table_schema", {
    "space_id": "SAP_CONTENT",
    "table_name": "SAP_SC_SALES_V_Fact_Sales"
})

# Print column names and types
for col in schema["columns"]:
    print(f"{col['name']}: {col['type']}")
```

---

## 🔍 Query Tools

### execute_query

**Description**: Executes SQL queries with automatic SQL→OData conversion

**Parameters**:
```typescript
{
  space_id: string,    // Required
  sql_query: string,   // Required (SELECT only)
  limit?: number       // Max rows (default: 100, max: 1000)
}
```

**Supported SQL**:
- `SELECT *` or `SELECT col1, col2`
- `WHERE` with simple comparisons
- `LIMIT N`
- No JOINs, GROUP BY, or complex features

**Response**:
```json
{
  "query": "SELECT * FROM CUSTOMERS LIMIT 10",
  "space": "SAP_CONTENT",
  "table": "CUSTOMERS",
  "execution_time": "0.234 seconds",
  "rows_returned": 10,
  "odata_endpoint": "/api/v1/.../relational/...",
  "odata_params": {"$top": 10},
  "data": [
    {"CUSTOMER_ID": "C001", "NAME": "Acme Corp"}
  ]
}
```

**Python Example**:
```python
# Simple query
result = await mcp_client.call_tool("execute_query", {
    "space_id": "SAP_CONTENT",
    "sql_query": "SELECT * FROM CUSTOMERS LIMIT 10"
})

# With WHERE clause
result = await mcp_client.call_tool("execute_query", {
    "space_id": "SAP_CONTENT",
    "sql_query": "SELECT * FROM ORDERS WHERE STATUS = 'COMPLETED' LIMIT 50"
})

# Access data
for row in result["data"]:
    print(row)
```

**SQL→OData Conversion**:
```sql
-- Input SQL:
SELECT customer_id, amount FROM ORDERS WHERE country = 'USA' LIMIT 10

-- Converted to OData:
GET /relational/SPACE/ORDERS
  ?$select=customer_id,amount
  &$filter=country eq 'USA'
  &$top=10
```

**Consent Required**: Yes (WRITE permission)

---

## 🏭 ETL-Optimized Tools

### query_relational_entity

**Description**: Large batch data extraction (up to 50,000 records)

**Parameters**:
```typescript
{
  space_id: string,      // Required
  asset_id: string,      // Required
  entity_name: string,   // Required
  filter?: string,       // OData $filter
  select?: string,       // Comma-separated columns
  top?: number,          // Max records (default: 1000, max: 50000)
  skip?: number,         // Pagination offset
  orderby?: string       // OData $orderby
}
```

**Response**:
```json
{
  "space_id": "SAP_CONTENT",
  "asset_id": "SAP_SC_SALES_V_Fact_Sales",
  "entity_name": "Results",
  "execution_time_seconds": 0.845,
  "rows_returned": 5000,
  "extraction_mode": "etl_batch",
  "data": [...],
  "pagination_hint": {
    "more_data_available": "likely",
    "next_batch_skip": 5000,
    "recommendation": "Use skip=5000 to get next batch"
  }
}
```

**Python Example - Simple Query**:
```python
result = await mcp_client.call_tool("query_relational_entity", {
    "space_id": "SAP_CONTENT",
    "asset_id": "SAP_SC_SALES_V_Fact_Sales",
    "entity_name": "Results",
    "top": 1000
})
```

**Python Example - With Filtering**:
```python
result = await mcp_client.call_tool("query_relational_entity", {
    "space_id": "SAP_CONTENT",
    "asset_id": "SAP_SC_SALES_V_Fact_Sales",
    "entity_name": "Results",
    "filter": "AMOUNT gt 1000 and STATUS eq 'COMPLETED'",
    "select": "SALES_ORDER_ID,AMOUNT,DATE",
    "top": 5000,
    "orderby": "AMOUNT desc"
})
```

**Python Example - Pagination**:
```python
# Extract large dataset in batches
skip = 0
batch_size = 10000
all_data = []

while True:
    result = await mcp_client.call_tool("query_relational_entity", {
        "space_id": "SAP_CONTENT",
        "asset_id": "SAP_SC_SALES_V_Fact_Sales",
        "entity_name": "Results",
        "top": batch_size,
        "skip": skip
    })

    all_data.extend(result["data"])

    if len(result["data"]) < batch_size:
        break  # No more data

    skip += batch_size

print(f"Total records extracted: {len(all_data)}")
```

**Consent Required**: No (READ permission)

---

### get_relational_entity_metadata

**Description**: Get entity metadata with SQL type mappings for ETL

**Parameters**:
```typescript
{
  space_id: string,           // Required
  asset_id: string,           // Required
  include_sql_types?: boolean // Default: true
}
```

**Response**:
```json
{
  "space_id": "SAP_CONTENT",
  "asset_id": "SAP_SC_SALES_V_Fact_Sales",
  "columns": [
    {
      "name": "SALES_ORDER_ID",
      "odata_type": "Edm.String",
      "sql_type": "NVARCHAR(10)",
      "max_length": 10,
      "nullable": false
    },
    {
      "name": "AMOUNT",
      "odata_type": "Edm.Decimal",
      "sql_type": "DECIMAL(18,2)",
      "precision": 18,
      "scale": 2,
      "nullable": true
    }
  ],
  "column_count": 20,
  "etl_guidance": {
    "recommended_batch_size": "10000-20000 records",
    "supports_incremental": true
  }
}
```

**Python Example - Generate DDL**:
```python
metadata = await mcp_client.call_tool("get_relational_entity_metadata", {
    "space_id": "SAP_CONTENT",
    "asset_id": "SAP_SC_SALES_V_Fact_Sales",
    "include_sql_types": True
})

# Generate CREATE TABLE statement
table_name = metadata["asset_id"]
print(f"CREATE TABLE {table_name} (")

for col in metadata["columns"]:
    nullable = "NULL" if col["nullable"] else "NOT NULL"
    print(f"  {col['name']} {col['sql_type']} {nullable},")

print(");")
```

**OData to SQL Type Mapping**:
```
Edm.String       → NVARCHAR(MAX) or NVARCHAR(n)
Edm.Int32        → INT
Edm.Int64        → BIGINT
Edm.Decimal      → DECIMAL(p,s)
Edm.Double       → DOUBLE
Edm.Boolean      → BOOLEAN
Edm.Date         → DATE
Edm.DateTime     → TIMESTAMP
Edm.DateTimeOffset → TIMESTAMP
Edm.Time         → TIME
Edm.Guid         → VARCHAR(36)
```

---

## 👥 Database User Management

### create_database_user

**Description**: Creates a new database user

**Parameters**:
```typescript
{
  username: string,    // Required (uppercase recommended)
  password: string     // Required (must meet complexity requirements)
}
```

**Password Requirements**:
- Minimum 8 characters
- Must include uppercase letter
- Must include lowercase letter
- Must include number
- Must include special character

**Response**:
```json
{
  "status": "success",
  "username": "APPUSER01",
  "message": "Database user created successfully"
}
```

**Python Example**:
```python
# Create user
result = await mcp_client.call_tool("create_database_user", {
    "username": "APPUSER01",
    "password": "SecurePass123!"
})

if result["status"] == "success":
    print(f"User {result['username']} created!")
```

**Error Handling**:
```python
try:
    result = await mcp_client.call_tool("create_database_user", {
        "username": "TESTUSER",
        "password": "WeakPass"  # Will fail - too weak
    })
except Exception as e:
    if "password" in str(e).lower():
        print("Password doesn't meet complexity requirements")
    elif "already exists" in str(e).lower():
        print("User already exists")
```

**Consent Required**: Yes (WRITE/ADMIN permission)

---

## 📊 Response Format Standards

All tools return JSON responses following this structure:

### Success Response
```json
{
  "status": "success" | "completed",
  "data": {...},          // Tool-specific data
  "metadata": {...}       // Optional metadata
}
```

### Error Response
```json
{
  "error": "Error message",
  "error_code": "HTTP_403",
  "details": "Additional context",
  "troubleshooting": [
    "Step 1: Check permissions",
    "Step 2: Verify credentials"
  ],
  "documentation_url": "https://..."
}
```

---

## 🔒 Authentication

### OAuth 2.0 Configuration

**Environment Variables**:
```bash
DATASPHERE_BASE_URL=https://tenant.region.hcs.cloud.sap
DATASPHERE_CLIENT_ID=sb-xxxxx!b130936|client!b3944
DATASPHERE_CLIENT_SECRET=xxxxxxxx$xxxxx
DATASPHERE_TOKEN_URL=https://tenant.authentication.region.hana.ondemand.com/oauth/token
```

### Token Management
- Tokens refresh automatically every 55 minutes
- No manual refresh required
- Tokens encrypted at rest with Fernet encryption

### Required Scopes
```
DWC_DATA_ACCESS    - Data querying and retrieval
DWC_CATALOG_READ   - Catalog and metadata access
DWC_SPACE_ADMIN    - User management (optional)
```

---

## ⚡ Performance Best Practices

### 1. Use Appropriate Tool for Data Size

**Small queries (< 1,000 rows)**:
```python
execute_query(sql_query="SELECT * FROM TABLE LIMIT 100")
```

**Large extractions (1,000 - 50,000 rows)**:
```python
query_relational_entity(top=10000)
```

### 2. Always Use Filtering
```python
# ❌ Slow - scans entire table
query_relational_entity(top=50000)

# ✅ Fast - filtered query
query_relational_entity(
    filter="DATE gt '2025-01-01'",
    top=10000
)
```

### 3. Request Only Needed Columns
```python
# ❌ Returns all columns
query_relational_entity(top=1000)

# ✅ Returns only what you need
query_relational_entity(
    select="ID,NAME,AMOUNT",
    top=1000
)
```

### 4. Use Pagination for Large Datasets
```python
# Process in batches
for skip in range(0, 50000, 10000):
    result = query_relational_entity(
        top=10000,
        skip=skip
    )
    process_batch(result["data"])
```

---

## 🔄 Rate Limiting

**Current Limits**:
- No hard rate limits enforced
- Recommended: Max 10 concurrent requests
- Large queries (>10K rows) may take several seconds

**Best Practices**:
```python
import asyncio

# ❌ Don't fire all at once
results = await asyncio.gather(*[
    query_tool() for _ in range(100)
])

# ✅ Limit concurrency
semaphore = asyncio.Semaphore(10)

async def limited_query():
    async with semaphore:
        return await query_tool()

results = await asyncio.gather(*[
    limited_query() for _ in range(100)
])
```

---

## 📖 Complete Tool List

| Tool | Category | Consent | Max Records |
|------|----------|---------|-------------|
| test_connection | Foundation | No | - |
| get_current_user | Foundation | No | - |
| get_tenant_info | Foundation | No | - |
| get_available_scopes | Foundation | No | - |
| list_spaces | Foundation | No | - |
| list_catalog_assets | Catalog | No | 1000 |
| get_asset_details | Catalog | No | - |
| get_asset_by_compound_key | Catalog | No | - |
| get_space_assets | Catalog | No | 1000 |
| get_space_info | Space | No | - |
| get_table_schema | Space | No | - |
| search_tables | Space | No | - |
| search_catalog | Search | No | - |
| search_repository | Search | No | - |
| list_database_users | Users | No | - |
| create_database_user | Users | Yes | - |
| update_database_user | Users | Yes | - |
| delete_database_user | Users | Yes | - |
| reset_database_user_password | Users | Yes | - |
| get_catalog_metadata | Metadata | No | - |
| get_analytical_metadata | Metadata | No | - |
| get_relational_metadata | Metadata | No | - |
| get_repository_search_metadata | Metadata | No | - |
| get_consumption_metadata | Metadata | No | - |
| get_analytical_model | Analytical | No | - |
| get_analytical_service_document | Analytical | No | - |
| list_analytical_datasets | Analytical | No | - |
| query_analytical_data | Analytical | No | - |
| list_relational_entities | ETL | No | - |
| get_relational_entity_metadata | ETL | No | - |
| query_relational_entity | ETL | No | 50000 |
| get_relational_odata_service | ETL | No | - |
| list_connections | Additional | No | - |
| get_task_status | Additional | No | - |
| browse_marketplace | Additional | No | - |
| get_deployed_objects | Additional | No | - |
| execute_query | Query | Yes | 1000 |

---

## 🆘 Error Handling

### Common Errors

**401 Unauthorized**:
```python
try:
    result = await call_tool("list_spaces", {})
except Exception as e:
    if "401" in str(e):
        print("Check OAuth credentials in .env")
```

**403 Forbidden**:
```python
try:
    result = await call_tool("create_database_user", {...})
except Exception as e:
    if "403" in str(e):
        print("You need ADMIN permissions for this operation")
```

**404 Not Found**:
```python
try:
    result = await call_tool("get_table_schema", {
        "space_id": "WRONG_SPACE",
        "table_name": "TABLE"
    })
except Exception as e:
    if "404" in str(e):
        print("Table or space doesn't exist")
```

---

## 🔗 Related Documentation

- **[Getting Started Guide](GETTING_STARTED_GUIDE.md)** - Quick start for new users
- **[Tools Catalog](TOOLS_CATALOG.md)** - All 41 tools with examples
- **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues and solutions
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment

---

**Last Updated**: December 12, 2025
**API Version**: 1.0
**Tools**: 41 working tools
**Real Data Coverage**: 98%
