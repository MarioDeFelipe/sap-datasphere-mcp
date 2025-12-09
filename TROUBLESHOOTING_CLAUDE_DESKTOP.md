# Troubleshooting Claude Desktop MCP Connection Issues

## Summary of Issues

Based on your screenshot, you're experiencing two problems:

1. **✅ FIXED: Tool Error** - `get_asset_by_compound_key` parameter mismatch (fixed in commit d80ba4a)
2. **⚠️  Authorization Errors** - 15 tools returning "Unknown tool" errors in Claude Desktop

## Verification: Server is Working Correctly

The MCP server has been tested and **all 32 tools are registered correctly**:

```bash
python test_mcp_server_startup.py
```

**Result:** ✅ All 32 tools found, including all 13 tools showing authorization errors

This confirms the **problem is NOT with the MCP server** - it's with Claude Desktop configuration.

---

## Solution: Fix Claude Desktop Configuration

### Step 1: Locate Your Claude Desktop Config File

Find `claude_desktop_config.json` at:

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### Step 2: Check Your Current Configuration

Open the file and look for the `mcpServers` section. You should see something like this:

```json
{
  "mcpServers": {
    "sap-datasphere": {
      "command": "python",
      "args": ["C:\\Users\\mariodefe\\mcpdatasphere\\sap_datasphere_mcp_server.py"]
    }
  }
}
```

### Step 3: Fix the Configuration

Replace the entire file with this **correct configuration**:

```json
{
  "mcpServers": {
    "sap-datasphere": {
      "command": "python",
      "args": [
        "C:\\Users\\mariodefe\\mcpdatasphere\\sap_datasphere_mcp_server.py"
      ],
      "env": {
        "DATASPHERE_BASE_URL": "https://ailien-test.eu20.hcs.cloud.sap",
        "DATASPHERE_CLIENT_ID": "sb-6a8a284c-9845-410c-8f36-ce7e637587b4!b130936|client!b3944",
        "DATASPHERE_CLIENT_SECRET": "1a5f77cb-1c27-45bf-a29f-131cedf33443$LFSrwTv0bmg2EfRf0nXixi3ZNHTZVpWXd38A3umVDqk=",
        "DATASPHERE_TOKEN_URL": "https://ailien-test.authentication.eu20.hana.ondemand.com/oauth/token",
        "USE_MOCK_DATA": "false"
      }
    }
  }
}
```

**Important Notes:**

1. **Paths**: On Windows, use double backslashes (`\\`) or forward slashes (`/`)
2. **Credentials**: Use YOUR actual OAuth credentials from `.env` file
3. **No Trailing Commas**: JSON doesn't allow trailing commas
4. **Remove Other MCP Servers**: If you have other servers configured (like the control panel ones you showed), consider removing or commenting them out for testing

### Step 4: Remove Conflicting MCP Servers

Your screenshot showed these tools that are NOT from our server:
- `ailien_studio_control_panel`
- `datasphere_control_panel_v2`
- `ailien_platform_q_business_enhanced`
- `hello_world_datasphere`

These suggest you have **another MCP server installed**. To fix:

```json
{
  "mcpServers": {
    "REMOVE_OR_DISABLE_OTHER_SERVERS_HERE": "...",

    "sap-datasphere": {
      "command": "python",
      "args": ["C:\\Users\\mariodefe\\mcpdatasphere\\sap_datasphere_mcp_server.py"],
      "env": {
        "DATASPHERE_BASE_URL": "https://ailien-test.eu20.hcs.cloud.sap",
        "DATASPHERE_CLIENT_ID": "sb-6a8a284c-9845-410c-8f36-ce7e637587b4!b130936|client!b3944",
        "DATASPHERE_CLIENT_SECRET": "1a5f77cb-1c27-45bf-a29f-131cedf33443$LFSrwTv0bmg2EfRf0nXixi3ZNHTZVpWXd38A3umVDqk=",
        "DATASPHERE_TOKEN_URL": "https://ailien-test.authentication.eu20.hana.ondemand.com/oauth/token",
        "USE_MOCK_DATA": "false"
      }
    }
  }
}
```

### Step 5: Restart Claude Desktop

1. **Completely quit** Claude Desktop (not just close the window)
2. **Reopen** Claude Desktop
3. **Wait 5-10 seconds** for MCP servers to initialize

### Step 6: Verify Tools Are Loaded

In a new Claude Desktop chat, type:

```
What MCP tools do you have available?
```

You should see **32 tools**, including:

**Phase 1: Core Metadata Tools**
- list_spaces
- get_space_info
- search_tables
- get_table_schema

**Phase 2: Data Access Tools**
- execute_query
- list_connections
- get_connection_info

**Phase 3.1: Advanced Metadata Tools**
- list_database_users
- create_database_user
- delete_database_user

**Phase 3.2: Repository Object Discovery Tools**
- list_repository_objects
- get_object_definition
- get_deployed_objects

**Phase 4.1: Analytical Model Access Tools**
- list_analytical_datasets
- get_analytical_model
- query_analytical_data

...and 18 more tools

---

## Troubleshooting Common Issues

### Issue 1: "Unknown tool" Errors Persist

**Cause:** MCP server isn't starting properly

**Solutions:**

1. **Check Python path:**
   ```bash
   which python
   # or
   where python
   ```

2. **Test server manually:**
   ```bash
   cd C:\Users\mariodefe\mcpdatasphere
   python sap_datasphere_mcp_server.py
   ```

   Should show:
   ```
   SAP Datasphere MCP Server Starting
   Mock Data Mode: False
   OAuth Configured: True
   ```

3. **Check Claude Desktop logs:**
   - Windows: `%APPDATA%\Claude\logs\`
   - macOS: `~/Library/Logs/Claude/`
   - Look for errors in `mcp-server-*.log`

### Issue 2: OAuth Authentication Fails

**Symptoms:** Tools work but return authentication errors

**Solutions:**

1. **Verify credentials in config:**
   - BASE_URL: `https://ailien-test.eu20.hcs.cloud.sap`
   - CLIENT_ID: Starts with `sb-`
   - CLIENT_SECRET: Contains `$` character
   - TOKEN_URL: Contains `/oauth/token`

2. **Test OAuth manually:**
   ```bash
   cd C:\Users\mariodefe\mcpdatasphere
   python -c "from auth.datasphere_auth_connector import DatasphereAuthConnector; import asyncio; connector = DatasphereAuthConnector(); asyncio.run(connector.ensure_valid_token())"
   ```

### Issue 3: Tools Return Mock Data

**Cause:** `USE_MOCK_DATA=true` in configuration

**Solution:** Ensure `USE_MOCK_DATA` is set to `false` in both:
- `.env` file
- `claude_desktop_config.json` env section

### Issue 4: Server Starts But No Tools Appear

**Cause:** MCP server crashed during startup

**Solutions:**

1. **Check for import errors:**
   ```bash
   python -c "import sap_datasphere_mcp_server"
   ```

2. **Verify all dependencies installed:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Check for port conflicts:**
   - Our server doesn't use ports (stdin/stdout communication)
   - But other MCP servers might conflict

---

## Expected Behavior After Fix

After following these steps, you should see:

✅ **32 tools available** (not 5 tools with errors)
✅ **No "Unknown tool" errors**
✅ **No authorization errors** for standard read operations
✅ **Consent prompts only for**:
   - `list_connections` (MEDIUM risk - requires admin consent)
   - `execute_query` (HIGH risk - requires write consent)

✅ **Real data returned** from SAP Datasphere (not mock data)

---

## Testing Your Setup

After configuration, test these queries:

1. **List available spaces:**
   ```
   List all spaces in my SAP Datasphere environment
   ```

2. **Search for tables:**
   ```
   Search for all tables related to "financial" transactions
   ```

3. **Get repository objects:**
   ```
   List all repository objects in SAP_CONTENT space
   ```

If these work, your setup is correct!

---

## Getting Help

If issues persist:

1. **Share your claude_desktop_config.json** (remove credentials!)
2. **Share Claude Desktop logs** from `%APPDATA%\Claude\logs\`
3. **Run the test script:**
   ```bash
   python test_mcp_server_startup.py
   ```
   Share the output

---

## Summary

**What Was Fixed:**
1. ✅ `get_asset_by_compound_key` parameter handling (commit d80ba4a)
2. ✅ Server tool registration verified (32 tools working)

**What You Need To Do:**
1. Update `claude_desktop_config.json` with correct configuration
2. Remove or disable other conflicting MCP servers
3. Restart Claude Desktop completely
4. Test with simple queries

**Expected Result:**
- All 32 tools available and working
- Real SAP Datasphere data returned
- No "Unknown tool" errors
