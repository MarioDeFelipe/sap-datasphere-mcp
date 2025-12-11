# execute_query Testing Guide

**Date**: December 11, 2025
**Purpose**: Test the new real API implementation for execute_query tool
**Goal**: Verify execute_query works with real SAP Datasphere relational data

---

## 🎯 What Was Implemented

The `execute_query` tool now supports **real data mode** using the SAP Datasphere relational consumption API.

**Before**: Always returned mock data
**After**: Respects `USE_MOCK_DATA=false` and queries real tables/views

**API Endpoint**: `/api/v1/datasphere/consumption/relational/{spaceId}/{viewName}`

---

## 🧪 Testing Strategy

### Prerequisites
1. **Restart Claude Desktop** to load the updated execute_query tool
2. **Verify USE_MOCK_DATA=false** in your .env file (should already be set)
3. **Have a known table/view** in SAP_CONTENT or another space

### Recommended Test Sequence

#### Test 1: Simple SELECT * Query
**Purpose**: Verify basic table querying works

**Query to try**:
```
Execute this query: SELECT * FROM SAP_SC_FI_AM_FINTRANSACTIONS LIMIT 5
```

**Expected Result**:
- Should return real data from the FINTRANSACTIONS table
- Should show execution time
- Should show OData endpoint used
- Should show actual row data

**If it fails**: Table name might be wrong or not accessible

---

#### Test 2: SELECT with Specific Columns
**Purpose**: Verify $select parameter conversion

**Query to try**:
```
Execute: SELECT customer_id, amount FROM SAP_SC_FI_AM_FINTRANSACTIONS LIMIT 10
```

**Expected Result**:
- Should return only the selected columns
- OData params should include: `$select=customer_id,amount`
- Should show fewer columns than SELECT *

---

#### Test 3: SELECT with WHERE Clause
**Purpose**: Verify $filter parameter conversion

**Query to try** (adjust column names based on real schema):
```
Execute: SELECT * FROM SAP_SC_FI_AM_FINTRANSACTIONS WHERE amount > 1000 LIMIT 10
```

**Expected Result**:
- Should return filtered results
- OData params should include: `$filter=amount > 1000`
- Should show only matching rows

---

#### Test 4: Discover Available Tables First
**Purpose**: Find real tables to query

**Step 1 - List tables**:
```
List all assets in SAP_CONTENT space
```

**Step 2 - Get table schema**:
```
Get the schema for [table_name_from_step_1]
```

**Step 3 - Query the table**:
```
Execute: SELECT * FROM [table_name] LIMIT 5
```

---

## 📋 Test Results Template

Please report results in this format:

### Test 1: Simple SELECT *
- **Query**: `SELECT * FROM SAP_SC_FI_AM_FINTRANSACTIONS LIMIT 5`
- **Status**: ✅ SUCCESS / ❌ FAILED
- **Rows Returned**: [number]
- **Execution Time**: [seconds]
- **Notes**: [any observations]

### Test 2: SELECT with Columns
- **Query**: `SELECT customer_id, amount FROM ... LIMIT 10`
- **Status**: ✅ SUCCESS / ❌ FAILED
- **Columns Returned**: [list]
- **Notes**: [any observations]

### Test 3: SELECT with WHERE
- **Query**: `SELECT * FROM ... WHERE ... LIMIT 10`
- **Status**: ✅ SUCCESS / ❌ FAILED
- **Filter Applied**: [yes/no]
- **Notes**: [any observations]

---

## 🔍 What to Look For

### Success Indicators
✅ Returns JSON with real data (not mock customer data)
✅ Shows actual execution time (not "0.245 seconds")
✅ Shows OData endpoint and parameters used
✅ Row count matches LIMIT parameter
✅ Data looks realistic (real product names, amounts, dates)

### Common Issues & Solutions

**Issue**: "Table/view doesn't exist"
**Solution**: Use `search_tables()` or `list_catalog_assets()` to find correct table name

**Issue**: "OAuth connector not initialized"
**Solution**: Check .env file has valid OAuth credentials

**Issue**: "Could not parse table name from query"
**Solution**: Check SQL syntax - must have `FROM table_name` clause

**Issue**: HTTP 404 or 400 errors
**Solution**: Table name might be case-sensitive (try all uppercase)

---

## 🎯 Expected Outcomes

### Scenario A: ✅ All Tests Pass
- execute_query works with real data
- SQL → OData conversion successful
- Update README: 33/38 tools (87% coverage)
- Celebrate! 🎉

### Scenario B: ⚠️ Some Tests Pass
- Basic queries work, filtered queries don't
- Document limitations
- Still update to real data mode (partial success)

### Scenario C: ❌ All Tests Fail
- API endpoint not available for relational queries
- Keep in mock mode
- Document why it doesn't work

---

## 📊 SQL → OData Conversion Logic

The implementation uses basic SQL parsing to convert queries:

### Table Name Extraction
```
FROM table_name          → /relational/SPACE/table_name
FROM space.table_name    → /relational/space/table_name
```

### WHERE Clause Conversion
```
WHERE country = 'USA'           → $filter=country eq 'USA'
WHERE amount > 1000             → $filter=amount > 1000
WHERE status = 'ACTIVE' AND ... → $filter=status eq 'ACTIVE' and ...
```

### SELECT Clause Conversion
```
SELECT *                     → No $select parameter (all columns)
SELECT col1, col2           → $select=col1,col2
```

### LIMIT Conversion
```
LIMIT 10    → $top=10
LIMIT 1000  → $top=1000 (max allowed)
```

---

## 🚀 How to Run Tests

### Via Claude Desktop (Recommended)

1. **Restart Claude Desktop** to load updated tool

2. **Ask Kiro to test execute_query**:
   ```
   Test the execute_query tool with a simple query:
   SELECT * FROM SAP_SC_FI_AM_FINTRANSACTIONS LIMIT 5
   ```

3. **Check the response**:
   - Look for real data (not mock data)
   - Check execution time
   - Verify OData endpoint shown

4. **Try more complex queries**:
   - With specific columns
   - With WHERE filters
   - Different tables

5. **Report results** back to this chat

---

## 📝 Success Criteria

For execute_query to be considered "working with real data":

✅ **Minimum**: Can execute basic `SELECT * FROM table LIMIT N` queries
✅ **Good**: Can select specific columns with `SELECT col1, col2 FROM table`
✅ **Excellent**: Can filter with `WHERE` clauses

Even if only basic queries work, we'll mark it as real data (with documented limitations).

---

## 🎯 What Happens After Testing

### If Tests Pass:
1. Update README.md to mark execute_query as real data ✅
2. Update coverage: 33/38 tools (87%)
3. Document SQL→OData conversion capabilities
4. Create completion summary for Option B Phase 2

### If Tests Fail:
1. Analyze error messages
2. Check if different table names work
3. Verify endpoint availability in tenant
4. Document findings and keep in mock mode if necessary

---

## 🔗 Related Documentation

- **Implementation**: [sap_datasphere_mcp_server.py:1569-1696](sap_datasphere_mcp_server.py#L1569-L1696)
- **Commit**: `9105da1` - Implement real API mode for execute_query
- **API Docs**: SAP Datasphere Relational Consumption API (OData v4.0)

---

## 📞 Ready to Test!

**Next Step**: Run the tests above and report results!

Based on your results, we'll:
1. Confirm execute_query works with real data
2. Update README to reflect 33/38 tools (87%)
3. Complete Option B implementation
4. Celebrate achieving 87% real data coverage! 🎉

---

**Created**: December 11, 2025
**Status**: Ready for testing
**Tester**: Kiro (via Claude Desktop)
