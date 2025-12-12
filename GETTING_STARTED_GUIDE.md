# Getting Started with SAP Datasphere MCP Server

**Goal**: Get you up and running in 10 minutes!

**What you'll learn**:
- How to install and configure the server
- How to test your connection
- How to run your first queries
- Common use cases and examples

---

## 🎯 Quick Start (5 Minutes)

### Step 1: Prerequisites Check (1 minute)

Before starting, make sure you have:

- [ ] Python 3.10 or higher installed
- [ ] SAP Datasphere account access
- [ ] OAuth 2.0 credentials (Client ID + Secret)
- [ ] Claude Desktop or another MCP-compatible client

**Check Python version**:
```bash
python --version
# Should show: Python 3.10.x or higher
```

---

### Step 2: Installation (2 minutes)

**Clone the repository**:
```bash
git clone https://github.com/MarioDeFelipe/sap-datasphere-mcp.git
cd sap-datasphere-mcp
```

**Install dependencies**:
```bash
pip install -r requirements.txt
```

**Expected output**:
```
Successfully installed mcp-0.1.0 aiohttp-3.9.1 cryptography-41.0.7 ...
```

---

### Step 3: Configuration (2 minutes)

**Create your `.env` file**:
```bash
cp .env.example .env
```

**Edit `.env` with your credentials**:
```bash
# SAP Datasphere Connection
DATASPHERE_BASE_URL=https://your-tenant.eu20.hcs.cloud.sap
DATASPHERE_TENANT_ID=your-tenant-id

# OAuth 2.0 Credentials (from SAP Datasphere Technical User)
DATASPHERE_CLIENT_ID=sb-xxxxxxxxx!b130936|client!b3944
DATASPHERE_CLIENT_SECRET=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx$xxxxx
DATASPHERE_TOKEN_URL=https://your-tenant.authentication.eu20.hana.ondemand.com/oauth/token

# Server Configuration
LOG_LEVEL=INFO
SERVER_PORT=8080
USE_MOCK_DATA=false
```

**Where to find your OAuth credentials**:
1. Log into SAP Datasphere
2. Go to System → Administration → App Integration
3. Create a new "OAuth2.0 Client"
4. Copy the Client ID and Client Secret
5. Note the Token URL from the client details

---

### Step 4: Start the Server (30 seconds)

**Start the MCP server**:
```bash
python sap_datasphere_mcp_server.py
```

**Expected output**:
```
Starting SAP Datasphere MCP Server...
✅ OAuth connector initialized
✅ Server listening on stdio
✅ 41 tools available
Ready for MCP requests!
```

---

### Step 5: Test Your Connection (30 seconds)

**In Claude Desktop or your MCP client, ask**:
```
Test my connection to SAP Datasphere
```

**Expected response**:
```json
{
  "status": "connected",
  "tenant_url": "https://your-tenant.eu20.hcs.cloud.sap",
  "authenticated": true,
  "oauth_status": "valid",
  "message": "✅ Connection successful! OAuth token is valid."
}
```

**✅ Success!** You're now connected and ready to use all 41 tools!

---

## 🚀 Your First Queries

Now that you're connected, try these common queries:

### Query 1: Discover Available Spaces

**Ask Claude**:
```
List all available SAP Datasphere spaces
```

**What you'll get**:
- List of all spaces you can access
- Space names and IDs
- Typically: `SAP_CONTENT`, `DEVAULT_SPACE`, and any custom spaces

**Example response**:
```json
{
  "spaces": [
    {"id": "SAP_CONTENT", "name": "SAP Content"},
    {"id": "DEVAULT_SPACE", "name": "Default Space"}
  ],
  "total_count": 2
}
```

---

### Query 2: Browse Available Data

**Ask Claude**:
```
List all assets in the SAP_CONTENT space
```

**What you'll get**:
- All tables, views, and other data assets
- Asset types and descriptions
- 36+ real assets in SAP_CONTENT

**Example response**:
```json
{
  "assets": [
    {
      "name": "SAP_SC_SALES_V_Fact_Sales",
      "type": "view",
      "description": "Sales fact data"
    },
    {
      "name": "SAP_SC_HR_V_Divisions",
      "type": "view",
      "description": "HR divisions"
    }
  ],
  "total_count": 36
}
```

---

### Query 3: Get Table Schema

**Ask Claude**:
```
Get the schema for table SAP_SC_SALES_V_Fact_Sales in SAP_CONTENT
```

**What you'll get**:
- Complete column list
- Data types for each column
- Nullable/primary key information

**Example response**:
```json
{
  "table_name": "SAP_SC_SALES_V_Fact_Sales",
  "columns": [
    {
      "name": "SALES_ORDER_ID",
      "type": "NVARCHAR(10)",
      "nullable": false
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

---

### Query 4: Execute Your First Data Query

**Ask Claude**:
```
Execute query: SELECT * FROM SAP_SC_SALES_V_Fact_Sales LIMIT 10
```

**What you'll get**:
- Real sales data from SAP Datasphere
- Up to 10 rows
- Execution time and metadata

**Example response**:
```json
{
  "query": "SELECT * FROM SAP_SC_SALES_V_Fact_Sales LIMIT 10",
  "execution_time": "0.234 seconds",
  "rows_returned": 10,
  "data": [
    {
      "SALES_ORDER_ID": "SO001",
      "CUSTOMER_ID": "C12345",
      "AMOUNT": 1500.00,
      "ORDER_DATE": "2025-01-15"
    }
  ]
}
```

---

## 📚 Common Use Cases

### Use Case 1: Data Discovery

**Goal**: Find all tables related to "sales"

**Steps**:
1. **Search for tables**:
   ```
   Search for tables containing 'sales' in SAP_CONTENT
   ```

2. **Get schema for interesting tables**:
   ```
   Get schema for SAP_SC_SALES_V_Fact_Sales
   ```

3. **Query the data**:
   ```
   Execute query: SELECT * FROM SAP_SC_SALES_V_Fact_Sales LIMIT 5
   ```

---

### Use Case 2: ETL Data Extraction

**Goal**: Extract large datasets for data warehouse loading

**Steps**:
1. **List available entities**:
   ```
   List relational entities in SAP_CONTENT, asset SAP_SC_SALES_V_Fact_Sales
   ```

2. **Get SQL type mapping**:
   ```
   Get relational entity metadata for SAP_CONTENT/SAP_SC_SALES_V_Fact_Sales with SQL types
   ```

3. **Extract data in batches**:
   ```
   Query relational entity from SAP_CONTENT, asset SAP_SC_SALES_V_Fact_Sales, entity Results, limit 5000
   ```

4. **Get next batch**:
   ```
   Query relational entity with skip 5000, limit 5000
   ```

**Why this is better**:
- Up to 50,000 records per query (vs 1,000 with execute_query)
- SQL type mappings for target database
- Optimized for ETL workflows

---

### Use Case 3: Database User Management

**Goal**: Create a new database user for an application

**Steps**:
1. **List existing users**:
   ```
   List all database users
   ```

2. **Create new user**:
   ```
   Create database user APPUSER01 with password SecurePass123!
   ```

3. **Verify creation**:
   ```
   List all database users
   ```

**Note**: Requires WRITE/ADMIN permissions

---

### Use Case 4: Analytical Queries

**Goal**: Query analytical models with aggregations

**Steps**:
1. **List analytical datasets**:
   ```
   List analytical datasets in SAP_SC_SALES_V_Fact_Sales
   ```

2. **Query with OData**:
   ```
   Query analytical data from SAP_CONTENT, asset SAP_SC_SALES_V_Fact_Sales, entity Results, top 100
   ```

3. **Query with filtering**:
   ```
   Query analytical data with filter: AMOUNT gt 1000
   ```

---

## 🎓 Understanding the Tool Categories

### Foundation Tools (5 tools)
**When to use**: Authentication, connection testing, tenant info
**Examples**:
- `test_connection` - Verify you're connected
- `get_current_user` - See who you're authenticated as
- `list_spaces` - Discover available spaces

---

### Catalog & Discovery Tools (9 tools)
**When to use**: Finding and exploring data assets
**Examples**:
- `list_catalog_assets` - Browse all assets
- `get_table_schema` - See table structure
- `search_catalog` - Find assets by keyword

---

### Data Query Tools (9 tools)
**When to use**: Retrieving actual data
**Examples**:
- `execute_query` - Simple SQL queries (max 1K rows)
- `query_relational_entity` - ETL queries (max 50K rows)
- `query_analytical_data` - Analytical queries with aggregations

---

### Management Tools (10 tools)
**When to use**: User management, metadata, connections
**Examples**:
- `create_database_user` - Add new users
- `list_connections` - See data sources
- `get_deployed_objects` - View deployed objects

---

## ⚡ Quick Tips

### Tip 1: Natural Language Queries
You don't need to know exact parameter names. Claude understands natural language:

❌ **Don't say**:
```
call tool list_catalog_assets with parameters space_id=SAP_CONTENT
```

✅ **Do say**:
```
Show me all assets in the SAP_CONTENT space
```

---

### Tip 2: Start with Discovery
Before querying data, discover what's available:

1. `list_spaces` → Find spaces
2. `list_catalog_assets` → Find tables
3. `get_table_schema` → See columns
4. `execute_query` → Query data

---

### Tip 3: Use the Right Tool for the Job

**For small data queries** (< 1,000 rows):
- Use `execute_query` with SQL syntax
- Simpler, more familiar

**For large ETL extractions** (up to 50,000 rows):
- Use `query_relational_entity` with OData
- Better performance, SQL type mappings

**For analytical queries** (aggregations, grouping):
- Use `query_analytical_data` with OData $apply
- Supports SUM, AVG, GROUP BY, etc.

---

### Tip 4: Check Real Data Status
All 41 tools work with **real SAP Datasphere data** (98% coverage).

The only tool with mock mode:
- Diagnostic tools (intentionally for testing)

Everything else returns **actual production data**! ✅

---

## 🔍 Troubleshooting Quick Fixes

### Problem: "OAuth connector not initialized"

**Cause**: Missing or invalid OAuth credentials in `.env`

**Fix**:
1. Check `.env` file exists
2. Verify `DATASPHERE_CLIENT_ID` and `DATASPHERE_CLIENT_SECRET` are set
3. Ensure no extra spaces or quotes
4. Restart the server

---

### Problem: "HTTP 403 Forbidden"

**Cause**: User doesn't have permission for this operation

**Fix**:
1. Check your OAuth scopes: `get_available_scopes`
2. Ask admin to grant required permissions
3. Some operations require WRITE or ADMIN scope

---

### Problem: "Table not found"

**Cause**: Table name is case-sensitive or doesn't exist

**Fix**:
1. Use `search_tables` to find correct name
2. Table names are usually UPPERCASE
3. Check space_id is correct

---

### Problem: "Connection timeout"

**Cause**: Network issues or server not responding

**Fix**:
1. Test connection: `test_connection`
2. Check `DATASPHERE_BASE_URL` in `.env`
3. Verify network connectivity
4. Check SAP Datasphere tenant status

---

## 📖 Next Steps

Now that you're up and running, explore more:

1. **📚 Read the Tools Catalog**
   - See [TOOLS_CATALOG.md](TOOLS_CATALOG.md) for all 41 tools
   - Detailed examples and parameters for each tool

2. **🔧 Learn Advanced Features**
   - ETL workflows with large batch processing
   - Analytical queries with aggregations
   - Database user management

3. **📊 Try Real-World Scenarios**
   - Data warehouse loading
   - Business intelligence queries
   - User provisioning automation

4. **🐛 Troubleshooting Help**
   - See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
   - Error codes and solutions

5. **🚀 Production Deployment**
   - See [DEPLOYMENT.md](DEPLOYMENT.md) for Docker/Kubernetes
   - Security best practices
   - Monitoring and logging

---

## 🎯 Success Checklist

After completing this guide, you should be able to:

- [ ] ✅ Connect to SAP Datasphere with OAuth 2.0
- [ ] ✅ List available spaces and assets
- [ ] ✅ Get table schemas and column information
- [ ] ✅ Execute SQL queries on real data
- [ ] ✅ Extract data for ETL workflows
- [ ] ✅ Manage database users
- [ ] ✅ Query analytical models

**If you can do all of the above, you're ready to use the full power of the SAP Datasphere MCP Server!** 🎉

---

## 💡 Example Session

Here's a complete example session showing discovery → schema → query:

**You**: List all spaces

**Claude**:
```json
{
  "spaces": [
    {"id": "SAP_CONTENT", "name": "SAP Content"},
    {"id": "DEVAULT_SPACE", "name": "Default Space"}
  ]
}
```

---

**You**: Show me all tables in SAP_CONTENT

**Claude**:
```json
{
  "assets": [
    {"name": "SAP_SC_SALES_V_Fact_Sales", "type": "view"},
    {"name": "SAP_SC_HR_V_Divisions", "type": "view"},
    ...
  ],
  "total_count": 36
}
```

---

**You**: Get the schema for SAP_SC_SALES_V_Fact_Sales

**Claude**:
```json
{
  "columns": [
    {"name": "SALES_ORDER_ID", "type": "NVARCHAR(10)"},
    {"name": "AMOUNT", "type": "DECIMAL(18,2)"},
    {"name": "ORDER_DATE", "type": "DATE"}
  ]
}
```

---

**You**: Execute: SELECT * FROM SAP_SC_SALES_V_Fact_Sales LIMIT 5

**Claude**:
```json
{
  "data": [
    {
      "SALES_ORDER_ID": "SO001",
      "AMOUNT": 1500.00,
      "ORDER_DATE": "2025-01-15"
    }
  ],
  "rows_returned": 5,
  "execution_time": "0.234 seconds"
}
```

**✅ Success!** You've discovered data, learned the schema, and queried real data!

---

## 🆘 Getting Help

### Documentation
- **Tools Catalog**: Complete reference for all 41 tools
- **Troubleshooting Guide**: Common problems and solutions
- **API Reference**: Technical documentation
- **Deployment Guide**: Production setup

### Support
- **GitHub Issues**: Report bugs or request features
- **SAP Community**: SAP Datasphere questions
- **MCP Documentation**: Model Context Protocol info

---

## 🎉 You're Ready!

**Congratulations!** You've successfully:
- ✅ Installed the SAP Datasphere MCP Server
- ✅ Configured OAuth 2.0 authentication
- ✅ Connected to your SAP Datasphere tenant
- ✅ Executed your first queries
- ✅ Learned the basic workflows

**You now have access to 41 powerful tools for SAP Datasphere integration!**

Start exploring your data, building ETL workflows, and automating data operations! 🚀

---

**Document Version**: 1.0
**Last Updated**: December 12, 2025
**Estimated Reading Time**: 10 minutes
**Estimated Setup Time**: 5-10 minutes
