# Changelog - v1.0.12 (Task Management Tools)

**Release Date:** 2026-02-03

## New Feature: Task Management Tools

SAP Datasphere has released new REST APIs for managing tasks and task chains. This release adds 3 new tools to leverage these APIs, bringing the total tool count to **48 tools**.

---

## New Tools

### 1. `run_task_chain`
**Execute a task chain in SAP Datasphere**

```
POST /api/v1/datasphere/tasks/chains/{space_id}/run/{object_id}
```

**Parameters:**
- `space_id` (required): The space containing the task chain
- `object_id` (required): The task chain name/ID to execute

**Returns:** `{ "logId": 9999999 }` - Use this logId to track execution status

**Example:**
```
"Run the Daily_ETL_Pipeline in SALES_SPACE"
```

---

### 2. `get_task_log`
**Get detailed information about a specific task execution**

```
GET /api/v1/datasphere/tasks/logs/{space_id}/{log_id}
```

**Parameters:**
- `space_id` (required): The space where the task ran
- `log_id` (required): The log ID to retrieve
- `detail_level` (optional): Level of detail to return
  - `status` (default): Status object `{"status": "COMPLETED"}`
  - `status_only`: Just the status string `"COMPLETED"`
  - `detailed`: Full logs with messages and child nodes
  - `extended`: Extended logs with complete message details

**Supports multiple Accept headers:**
- `application/vnd.sap.datasphere.task.log.status.object+json` (status)
- `application/vnd.sap.datasphere.task.log.status+json` (status_only)
- `application/vnd.sap.datasphere.task.log.details+json` (detailed)
- `application/vnd.sap.datasphere.task.log.details.extended+json` (extended)

**Example:**
```
"Get detailed logs for task log 2295172 in SALES_SPACE"
```

---

### 3. `get_task_history`
**Get the execution history for a specific task chain**

```
GET /api/v1/datasphere/tasks/logs/{space_id}/objects/{object_id}
```

**Parameters:**
- `space_id` (required): The space containing the task chain
- `object_id` (required): The task chain name to get history for

**Returns:** Array of all historical task runs with:
- logId, status, startTime, endTime, runTime
- objectId, applicationId, activity
- user who initiated the run

**Example:**
```
"Show me the run history for Daily_ETL_Pipeline in SALES_SPACE"
```

---

## Use Cases

### 1. Trigger ETL Jobs from Claude/Codex
```
"Run the Customer_Sync task chain in FINANCE_SPACE"
→ Returns logId for tracking
```

### 2. Monitor Task Execution
```
"Check status of task log 2295172"
→ Returns: RUNNING, COMPLETED, FAILED, or CANCELLED
```

### 3. Debug Failed Tasks
```
"Get detailed logs for failed task 2326060 in FINANCE_DWH"
→ Returns full execution logs with error messages
```

### 4. Track Historical Performance
```
"Show me the run history for Monthly_Reconciliation"
→ Returns all previous runs with durations and status
```

### 5. Automate Orchestration Workflows
```
1. Run task chain → get logId
2. Poll status with get_task_log
3. On completion, trigger next task chain
```

---

## Technical Details

### Mock Data Support
All three tools support mock mode (`USE_MOCK_DATA=true`) with realistic sample data:
- 4 mock task chains across 2 spaces (SALES_ANALYTICS, FINANCE_DWH)
- 3 mock task logs with different statuses (COMPLETED, FAILED, RUNNING)
- Historical run data for each task chain

### Real API Mode
When `USE_MOCK_DATA=false`, the tools call the actual SAP Datasphere Tasks REST APIs:
- Proper Accept header handling for different detail levels
- Error handling with helpful diagnostic messages
- Logging for debugging

### Files Modified
1. [tool_descriptions.py](tool_descriptions.py) - Added descriptions for 3 new tools
2. [mock_data.py](mock_data.py) - Added mock task chains, logs, and history
3. [sap_datasphere_mcp_server.py](sap_datasphere_mcp_server.py) - Added tool definitions and handlers
4. [pyproject.toml](pyproject.toml) - Updated version to 1.0.12
5. [package.json](package.json) - Updated version to 1.0.12

---

## API Reference

Based on SAP Datasphere documentation: [Manage Tasks Using REST APIs](https://help.sap.com/docs/SAP_DATASPHERE)

### Authentication
The Tasks APIs use the same OAuth authentication as other Datasphere APIs:
- Standard OAuth2 Authorization Flow
- OAuth2 SAML Bearer Principal Propagation Flow

### Required Permissions
Users must have the same roles and privileges required to run task chains and view task logs in SAP Datasphere.

---

## Migration Guide

### From v1.0.11 to v1.0.12

No breaking changes. Simply upgrade:

**PyPI:**
```bash
pip install --upgrade sap-datasphere-mcp
```

**npm:**
```bash
npm install -g @mariodefe/sap-datasphere-mcp@1.0.12
```

### Testing the New Tools

**Mock mode (default):**
```
"Run the Daily_Sales_ETL task chain in SALES_ANALYTICS"
"Check status of task log 2295172"
"Show history for Daily_Sales_ETL in SALES_ANALYTICS"
```

**Real API mode:**
Set `USE_MOCK_DATA=false` in your environment and use your actual task chain names.

---

## Summary

| Metric | Value |
|--------|-------|
| New Tools | 3 |
| Total Tools | 48 |
| API Endpoints | 3 |
| Mock Data Entries | 10+ |
| Breaking Changes | 0 |

### New Tools Summary

| Tool | API Method | Purpose |
|------|------------|---------|
| `run_task_chain` | POST | Execute a task chain |
| `get_task_log` | GET | Get execution details |
| `get_task_history` | GET | View historical runs |

---

## Credits

Thanks to the SAP Datasphere team for releasing the new Tasks REST APIs!

---

## Links

- **PyPI Package**: https://pypi.org/project/sap-datasphere-mcp/
- **npm Package**: https://www.npmjs.com/package/@mariodefe/sap-datasphere-mcp
- **GitHub**: https://github.com/MarioDeFelipe/sap-datasphere-mcp
- **Previous Version**: [CHANGELOG_v1.0.11.md](CHANGELOG_v1.0.11.md)
