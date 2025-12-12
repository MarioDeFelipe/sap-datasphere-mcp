# SAP Datasphere MCP Server - Troubleshooting Guide

**Purpose**: Quick solutions for common problems
**Last Updated**: December 12, 2025

This guide helps you diagnose and fix common issues when using the SAP Datasphere MCP Server.

---

## 📑 Table of Contents

1. [Connection Issues](#connection-issues)
2. [Authentication Errors](#authentication-errors)
3. [Query Errors](#query-errors)
4. [Performance Issues](#performance-issues)
5. [Data Access Errors](#data-access-errors)
6. [User Management Errors](#user-management-errors)
7. [Installation Issues](#installation-issues)
8. [Claude Desktop Integration](#claude-desktop-integration)

---

## 🔌 Connection Issues

### Error: "OAuth connector not initialized"

**Symptoms**:
```
Error: OAuth connector not initialized. Cannot execute query.
```

**Causes**:
1. Missing `.env` file
2. Invalid OAuth credentials
3. Credentials not loaded

**Solutions**:

**Step 1**: Check `.env` file exists
```bash
ls -la .env
# Should show: .env file
```

**Step 2**: Verify credentials are set
```bash
cat .env | grep DATASPHERE_CLIENT_ID
cat .env | grep DATASPHERE_CLIENT_SECRET
```

**Step 3**: Check for common mistakes
- ❌ Extra spaces around `=`
- ❌ Quotes around values (don't use quotes)
- ❌ Missing values

**Correct format**:
```bash
DATASPHERE_CLIENT_ID=sb-xxxxx!b130936|client!b3944
DATASPHERE_CLIENT_SECRET=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx$xxxxx
```

**Step 4**: Restart the server
```bash
# Stop server (Ctrl+C)
# Start again
python sap_datasphere_mcp_server.py
```

---

### Error: "Connection timeout"

**Symptoms**:
```
Error: Connection timeout after 30 seconds
```

**Causes**:
1. Network connectivity issues
2. Wrong tenant URL
3. Firewall blocking requests
4. SAP Datasphere tenant down

**Solutions**:

**Step 1**: Test basic connectivity
```bash
ping ailien-test.eu20.hcs.cloud.sap
# Should respond
```

**Step 2**: Verify tenant URL
```bash
# In .env file
DATASPHERE_BASE_URL=https://ailien-test.eu20.hcs.cloud.sap
#                   ^^^^^^ Must include https://
```

**Step 3**: Test with curl
```bash
curl -I https://ailien-test.eu20.hcs.cloud.sap
# Should return: HTTP/2 200
```

**Step 4**: Check firewall/proxy
- Corporate networks may block external connections
- Check with IT if proxy configuration needed
- Try from different network (mobile hotspot)

---

### Error: "Cannot reach SAP Datasphere tenant"

**Symptoms**:
```
Error: Failed to connect to https://your-tenant.eu20.hcs.cloud.sap
```

**Causes**:
1. Typo in tenant URL
2. Wrong region (eu10 vs eu20 vs us10)
3. Tenant doesn't exist

**Solutions**:

**Step 1**: Verify tenant URL from SAP Datasphere UI
- Log into SAP Datasphere web interface
- Check URL in browser: `https://TENANT.REGION.hcs.cloud.sap`
- Copy exact URL to `.env`

**Step 2**: Common regions
```
eu10 → Europe (Frankfurt)
eu20 → Europe (Netherlands)
us10 → US East
us20 → US West
ap10 → Asia Pacific (Sydney)
```

**Step 3**: Test connection tool
```
Test my connection to SAP Datasphere
```

---

## 🔐 Authentication Errors

### Error: "HTTP 401 Unauthorized"

**Symptoms**:
```
Error: HTTP 401 Unauthorized
Authentication failed
```

**Causes**:
1. Invalid OAuth credentials
2. Expired client secret
3. Wrong token URL

**Solutions**:

**Step 1**: Verify OAuth credentials are correct
- Log into SAP Datasphere
- Go to System → Administration → App Integration
- Check OAuth client still exists
- Compare Client ID in UI vs `.env`

**Step 2**: Check token URL matches region
```bash
# For eu20 region:
DATASPHERE_TOKEN_URL=https://ailien-test.authentication.eu20.hana.ondemand.com/oauth/token
#                                                        ^^^^
#                                                    Must match region
```

**Step 3**: Regenerate credentials
- In SAP Datasphere App Integration
- Delete old OAuth client
- Create new OAuth client
- Update `.env` with new credentials
- Restart server

---

### Error: "HTTP 403 Forbidden"

**Symptoms**:
```
Error: HTTP 403 Forbidden
You don't have permission to access this resource
```

**Causes**:
1. Missing OAuth scopes
2. User doesn't have required permissions
3. Space/asset not accessible

**Solutions**:

**Step 1**: Check your OAuth scopes
```
What scopes do I have?
```

**Expected scopes**:
- `DWC_DATA_ACCESS` - For data querying
- `DWC_CATALOG_READ` - For catalog browsing
- `DWC_SPACE_ADMIN` - For user management

**Step 2**: Request missing scopes
- Contact SAP Datasphere administrator
- Request required OAuth scopes
- OAuth client needs to be updated

**Step 3**: Check space permissions
```
List all spaces
```
- If space doesn't appear, you don't have access
- Ask admin to grant space access

**Step 4**: Use different tool
Some tools require higher permissions:
- `create_database_user` → Needs WRITE/ADMIN
- `execute_query` → Needs WRITE (data access)
- `list_catalog_assets` → Only needs READ

---

### Error: "Token expired"

**Symptoms**:
```
Error: OAuth token has expired
```

**Causes**:
1. Token automatically expires after period
2. Server running too long without refresh

**Solutions**:

**Step 1**: Server handles this automatically
- OAuth tokens refresh automatically
- Usually no action needed

**Step 2**: If persists, restart server
```bash
# Stop server (Ctrl+C)
python sap_datasphere_mcp_server.py
```

**Step 3**: Check token refresh is enabled
```python
# In code, should have:
auto_refresh=True  # Default
```

---

## 🔍 Query Errors

### Error: "Table/view doesn't exist"

**Symptoms**:
```
Error: Table 'CUSTOMERS' not found in space 'SAP_CONTENT'
```

**Causes**:
1. Table name is case-sensitive
2. Table doesn't exist
3. Wrong space_id

**Solutions**:

**Step 1**: Search for correct table name
```
Search for tables containing 'customer' in SAP_CONTENT
```

**Step 2**: Try uppercase
Most SAP table names are UPPERCASE:
```sql
-- ❌ Wrong
SELECT * FROM customers

-- ✅ Correct
SELECT * FROM CUSTOMERS
```

**Step 3**: List all tables in space
```
List all assets in SAP_CONTENT
```

**Step 4**: Check space is correct
```
List all spaces
```

---

### Error: "SQL syntax error"

**Symptoms**:
```
Error: Could not parse SQL query
```

**Causes**:
1. Unsupported SQL syntax
2. Complex query features not supported
3. Typos in SQL

**Solutions**:

**Step 1**: Use supported SQL only
```sql
-- ✅ Supported
SELECT * FROM TABLE LIMIT 10
SELECT col1, col2 FROM TABLE WHERE col1 = 'value'
SELECT * FROM TABLE WHERE amount > 100 LIMIT 50

-- ❌ Not supported
SELECT * FROM TABLE1 JOIN TABLE2  -- No JOINs
SELECT * FROM TABLE GROUP BY col1  -- No GROUP BY (use analytical tools)
SELECT * FROM TABLE ORDER BY col1  -- Limited ORDER BY support
```

**Step 2**: Use appropriate tool for your query

**For simple SELECT queries**:
```
Execute query: SELECT * FROM TABLE LIMIT 10
```

**For JOINs or GROUP BY**:
- Use `query_analytical_data` with OData $apply
- Or query tables separately and join client-side

**For large extractions**:
```
Query relational entity from space, asset, entity, limit 5000
```

---

### Error: "Query timeout"

**Symptoms**:
```
Error: Query execution timeout after 60 seconds
```

**Causes**:
1. Query returns too much data
2. Complex filtering taking too long
3. Network latency

**Solutions**:

**Step 1**: Reduce result size
```sql
-- ❌ Returns too much
SELECT * FROM HUGE_TABLE

-- ✅ Limited results
SELECT * FROM HUGE_TABLE LIMIT 1000
```

**Step 2**: Add filters
```sql
SELECT * FROM ORDERS WHERE ORDER_DATE > '2025-01-01' LIMIT 100
```

**Step 3**: Use ETL tools for large data
```
Query relational entity with top 5000
# Handles larger datasets better
```

**Step 4**: Use pagination
```
Query with skip 0, top 5000   # First batch
Query with skip 5000, top 5000  # Second batch
```

---

### Error: "Max row limit exceeded"

**Symptoms**:
```
Error: Query returned more than 1000 rows (max limit)
```

**Causes**:
1. Using `execute_query` for large datasets
2. No LIMIT clause specified

**Solutions**:

**Step 1**: Add LIMIT to query
```sql
SELECT * FROM BIG_TABLE LIMIT 1000
```

**Step 2**: Use ETL tools for larger datasets
```
Query relational entity from space, asset, entity, limit 50000
# Supports up to 50,000 records
```

**Step 3**: Use pagination
```
Query with skip 0, top 10000
Query with skip 10000, top 10000
# Process in batches
```

---

## ⚡ Performance Issues

### Issue: Slow query response

**Symptoms**:
- Queries taking > 5 seconds
- Timeouts on simple queries

**Causes**:
1. Large result sets
2. No filtering applied
3. Network latency
4. SAP Datasphere load

**Solutions**:

**Step 1**: Add filtering
```sql
-- ❌ Slow (scans entire table)
SELECT * FROM BIG_TABLE

-- ✅ Fast (filtered)
SELECT * FROM BIG_TABLE WHERE DATE > '2025-01-01' LIMIT 100
```

**Step 2**: Request only needed columns
```sql
-- ❌ Returns all columns
SELECT * FROM TABLE

-- ✅ Returns only what you need
SELECT col1, col2, col3 FROM TABLE
```

**Step 3**: Use LIMIT
```sql
SELECT * FROM TABLE LIMIT 100
```

**Step 4**: Check network
```bash
ping your-tenant.eu20.hcs.cloud.sap
# Should show < 100ms latency
```

---

### Issue: High memory usage

**Symptoms**:
- Python process using lots of RAM
- System slow or crashes

**Causes**:
1. Loading too much data at once
2. Not processing data in batches
3. Memory leaks (rare)

**Solutions**:

**Step 1**: Process data in smaller batches
```
# ❌ Don't load 50K records at once
Query with top 50000

# ✅ Load in 5K batches
Query with top 5000
```

**Step 2**: Use pagination
```python
skip = 0
batch_size = 5000

while True:
    # Query batch
    results = query_with_skip_and_top(skip, batch_size)

    # Process batch
    process_results(results)

    # Next batch
    if len(results) < batch_size:
        break  # No more data
    skip += batch_size
```

**Step 3**: Restart server if needed
```bash
# Stop server
# Start fresh
python sap_datasphere_mcp_server.py
```

---

## 📊 Data Access Errors

### Error: "No data returned"

**Symptoms**:
```json
{
  "data": [],
  "rows_returned": 0
}
```

**Causes**:
1. Table is empty
2. Filter excludes all rows
3. Wrong table name

**Solutions**:

**Step 1**: Check table has data
```
Get table schema for TABLE_NAME
# Shows row_count
```

**Step 2**: Remove filters to test
```sql
-- Try without WHERE
SELECT * FROM TABLE LIMIT 10
```

**Step 3**: Verify table name
```
List all tables in space
```

---

### Error: "Column doesn't exist"

**Symptoms**:
```
Error: Column 'CUSTOMER_NAME' doesn't exist in table
```

**Causes**:
1. Column name typo
2. Column name case-sensitive
3. Column doesn't exist

**Solutions**:

**Step 1**: Get table schema
```
Get schema for table TABLE_NAME
```

**Step 2**: Check exact column names
```json
{
  "columns": [
    {"name": "CUSTOMER_ID"},  // ← Exact name
    {"name": "NAME"}          // ← Not "CUSTOMER_NAME"
  ]
}
```

**Step 3**: Use exact column names
```sql
SELECT CUSTOMER_ID, NAME FROM TABLE
```

---

## 👥 User Management Errors

### Error: "Database user creation failed"

**Symptoms**:
```
Error: Failed to create database user
```

**Causes**:
1. User already exists
2. Weak password
3. Missing ADMIN permissions
4. SAP CLI not configured

**Solutions**:

**Step 1**: Check if user exists
```
List all database users
```

**Step 2**: Use strong password
Password requirements:
- Minimum 8 characters
- Must include uppercase
- Must include lowercase
- Must include numbers
- Must include special characters

**Example**: `SecurePass123!`

**Step 3**: Check permissions
```
What scopes do I have?
```
Need: `DWC_ADMIN` or similar admin scope

**Step 4**: Verify SAP CLI installed
The server uses SAP Datasphere CLI for user management:
```bash
which datasphere-cli
# Should show path to CLI
```

---

### Error: "Password reset failed"

**Symptoms**:
```
Error: Failed to reset password for user
```

**Causes**:
1. User doesn't exist
2. Weak new password
3. Missing permissions

**Solutions**:

**Step 1**: Verify user exists
```
List all database users
```

**Step 2**: Use strong password
See password requirements above

**Step 3**: Check you have WRITE permission
```
What scopes do I have?
```

---

## 🔧 Installation Issues

### Error: "Module not found"

**Symptoms**:
```
ModuleNotFoundError: No module named 'mcp'
ModuleNotFoundError: No module named 'aiohttp'
```

**Causes**:
1. Dependencies not installed
2. Wrong Python environment
3. Installation failed

**Solutions**:

**Step 1**: Install dependencies
```bash
pip install -r requirements.txt
```

**Step 2**: Check Python version
```bash
python --version
# Must be 3.10 or higher
```

**Step 3**: Use virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Step 4**: Verify installation
```bash
pip list | grep mcp
pip list | grep aiohttp
```

---

### Error: "Permission denied"

**Symptoms**:
```
PermissionError: [Errno 13] Permission denied
```

**Causes**:
1. Installing without admin rights
2. File permissions issue

**Solutions**:

**Step 1**: Install for user only
```bash
pip install --user -r requirements.txt
```

**Step 2**: Use sudo (Linux/Mac)
```bash
sudo pip install -r requirements.txt
```

**Step 3**: Check file permissions
```bash
ls -la sap_datasphere_mcp_server.py
# Should be readable/executable
```

---

## 💻 Claude Desktop Integration

### Issue: MCP Server not showing in Claude

**Symptoms**:
- Server running but Claude doesn't see tools
- No tools available in Claude

**Causes**:
1. Claude Desktop not restarted
2. Server not configured in Claude config
3. stdio communication issue

**Solutions**:

**Step 1**: Restart Claude Desktop
- Completely quit Claude Desktop
- Start it again
- Wait 30 seconds for MCP connections

**Step 2**: Check Claude MCP configuration
File location:
- Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

Should contain:
```json
{
  "mcpServers": {
    "sap-datasphere": {
      "command": "python",
      "args": ["/path/to/sap_datasphere_mcp_server.py"]
    }
  }
}
```

**Step 3**: Check server logs
Server should show:
```
✅ Server listening on stdio
✅ 41 tools available
```

**Step 4**: Test manually
```bash
python sap_datasphere_mcp_server.py
# Should start without errors
```

---

### Issue: Tools work but return errors

**Symptoms**:
- Tools appear in Claude
- All return errors when used

**Causes**:
1. OAuth not configured
2. Wrong `.env` file location
3. Credentials invalid

**Solutions**:

**Step 1**: Check `.env` in correct location
```bash
# Should be in same directory as server script
ls -la .env
```

**Step 2**: Test connection
```
Test my connection to SAP Datasphere
```

**Step 3**: Check server startup messages
Should see:
```
✅ OAuth connector initialized
```

Not:
```
⚠️ USE_MOCK_DATA=true (mock mode)
```

---

## 🆘 Getting More Help

### Diagnostic Commands

**Test connection**:
```
Test my connection to SAP Datasphere
```

**Check authentication**:
```
Who am I?
What scopes do I have?
```

**List available tools**:
```
List all SAP Datasphere spaces
# If this works, everything is working!
```

---

### Enable Debug Logging

**In `.env` file**:
```bash
LOG_LEVEL=DEBUG
```

**Restart server** to see detailed logs

---

### Common Error Codes

| Code | Meaning | Common Solution |
|------|---------|-----------------|
| 400 | Bad Request | Check query syntax |
| 401 | Unauthorized | Check OAuth credentials |
| 403 | Forbidden | Request permissions |
| 404 | Not Found | Check table/space name |
| 408 | Timeout | Reduce query size |
| 500 | Server Error | Check SAP Datasphere status |

---

### Still Having Issues?

1. **Check the logs**:
   ```bash
   # Server outputs detailed error messages
   ```

2. **Review documentation**:
   - [GETTING_STARTED_GUIDE.md](GETTING_STARTED_GUIDE.md)
   - [TOOLS_CATALOG.md](TOOLS_CATALOG.md)
   - [API_REFERENCE.md](API_REFERENCE.md)

3. **GitHub Issues**:
   - Search existing issues
   - Create new issue with:
     - Error message
     - Steps to reproduce
     - Server logs
     - `.env` (without secrets!)

4. **SAP Community**:
   - For SAP Datasphere-specific questions
   - OAuth setup issues
   - Permissions and access

---

## ✅ Quick Diagnostic Checklist

When troubleshooting, check these in order:

- [ ] `.env` file exists and has valid credentials
- [ ] Python 3.10+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Server starts without errors
- [ ] `test_connection` returns success
- [ ] `list_spaces` returns spaces
- [ ] Network connectivity to SAP Datasphere
- [ ] OAuth scopes include required permissions
- [ ] Table/space names are correct (case-sensitive)

If all checkboxes pass, the server should work! ✅

---

**Document Version**: 1.0
**Last Updated**: December 12, 2025
**Status**: Production Ready
