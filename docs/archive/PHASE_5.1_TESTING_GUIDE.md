# Phase 5.1 Testing Guide - ETL-Optimized Relational Tools

**Date**: December 11, 2025
**Purpose**: Test the 4 new ETL-optimized relational data access tools
**Status**: Ready for Testing

---

## 🎯 Tools to Test

All 4 Phase 5.1 tools have been implemented with **renamed APIs** to avoid confusion:

1. **`list_relational_entities`** - List available entities for ETL
2. **`get_relational_entity_metadata`** - Get entity metadata with SQL types
3. **`query_relational_entity`** - Execute ETL queries (up to 50K records)
4. **`get_relational_odata_service`** - Get OData service document

---

## 📋 Prerequisites

1. **Restart Claude Desktop** to load the 4 new tools
2. **Known working assets** from your tenant:
   - Space: SAP_CONTENT
   - Assets: SAP_SC_FI_AM_FINTRANSACTIONS, SAP_SC_HR_V_Divisions, etc.

---

## 🧪 Test Sequence

### Test 1: list_relational_entities
**Purpose**: Verify entity listing works

**Command**:
```
List relational entities for SAP_SC_FI_AM_FINTRANSACTIONS in SAP_CONTENT space
```

**Expected Result**:
- Returns list of available entities
- Shows entity count
- Includes metadata_url
- Shows ETL optimization info (max_batch_size: 50000)

**Success Criteria**: ✅ Returns entity list with real data

---

### Test 2: get_relational_entity_metadata
**Purpose**: Verify metadata extraction with SQL type mapping

**Command**:
```
Get relational entity metadata for SAP_SC_FI_AM_FINTRANSACTIONS in SAP_CONTENT
```

**Expected Result**:
- Returns entity metadata
- Shows columns with OData types
- **Includes SQL type mappings** (NVARCHAR, INT, DECIMAL, etc.)
- Shows ETL guidance (batch sizes, pagination methods)

**Success Criteria**: ✅ Returns metadata with SQL types

---

### Test 3: query_relational_entity
**Purpose**: Verify ETL-optimized querying

**Test 3a: Simple Query**
```
Query relational entity SAP_SC_FI_AM_FINTRANSACTIONS in SAP_CONTENT, limit 100 records
```

**Expected Result**:
- Returns up to 100 records
- Shows execution time
- Shows ETL mode indication
- If 100 records returned, shows pagination hint

**Test 3b: Filtered Query**
```
Query SAP_SC_FI_AM_FINTRANSACTIONS with filter "amount gt 1000", limit 50
```

**Expected Result**:
- Returns filtered records
- Shows OData params with $filter
- Execution time displayed

**Test 3c: Large Batch (ETL Feature)**
```
Query SAP_SC_FI_AM_FINTRANSACTIONS with limit 5000 records
```

**Expected Result**:
- Returns up to 5000 records (ETL mode allows 50K max)
- Shows extraction_mode: "etl_batch"
- May show pagination hint if more data available

**Success Criteria**: ✅ All 3 query types work

---

### Test 4: get_relational_odata_service
**Purpose**: Verify OData service document retrieval

**Command**:
```
Get OData service document for SAP_SC_FI_AM_FINTRANSACTIONS in SAP_CONTENT
```

**Expected Result**:
- Returns service document
- Shows available entity sets
- Shows query capabilities ($filter, $select, $top, $orderby)
- **Shows ETL features**: incremental extraction, parallel processing, type mapping

**Success Criteria**: ✅ Returns service document with ETL guidance

---

## 📊 Test Results Template

Please report results in this format:

### Test 1: list_relational_entities
- **Command**: List relational entities for SAP_SC_FI_AM_FINTRANSACTIONS
- **Status**: ✅ SUCCESS / ❌ FAILED
- **Entity Count**: [number]
- **Max Batch Size Shown**: [50000 expected]
- **Notes**: [observations]

### Test 2: get_relational_entity_metadata
- **Command**: Get entity metadata for SAP_SC_FI_AM_FINTRANSACTIONS
- **Status**: ✅ SUCCESS / ❌ FAILED
- **SQL Types Included**: YES / NO
- **Sample SQL Type**: [e.g., "amount": "DECIMAL(15,2)"]
- **Notes**: [observations]

### Test 3: query_relational_entity
- **Test 3a (Simple)**: ✅ / ❌
- **Test 3b (Filtered)**: ✅ / ❌
- **Test 3c (Large Batch)**: ✅ / ❌
- **Max Records Returned**: [number]
- **Notes**: [observations]

### Test 4: get_relational_odata_service
- **Command**: Get OData service for SAP_SC_FI_AM_FINTRANSACTIONS
- **Status**: ✅ SUCCESS / ❌ FAILED
- **ETL Features Shown**: YES / NO
- **Notes**: [observations]

---

## 🔍 What to Look For

### Success Indicators
✅ Returns JSON with real SAP Datasphere data
✅ SQL type mappings present (NVARCHAR, INT, DECIMAL, etc.)
✅ ETL guidance included (batch sizes, pagination methods)
✅ Supports large batches (test with 5000+ records)
✅ OData parameters shown ($filter, $select, $top)
✅ Performance metrics (execution time)

### Differences from Existing Tools

**vs execute_query**:
- execute_query: SQL syntax (`SELECT * FROM table WHERE...`)
- query_relational_entity: OData syntax (`$filter=amount gt 1000`)
- execute_query: Max 1,000 records
- query_relational_entity: Max 50,000 records (ETL mode)

**vs get_relational_metadata**:
- get_relational_metadata: Generic CSDL schema (XML format)
- get_relational_entity_metadata: Entity-specific with SQL types

---

## 💡 ETL Features to Verify

### 1. Large Batch Processing
- Try querying 10,000 records
- Should work without errors
- Performance should be acceptable (< 60 seconds)

### 2. SQL Type Mapping
- Check if OData types are mapped to SQL:
  - Edm.String → NVARCHAR(n)
  - Edm.Int32 → INT
  - Edm.Decimal → DECIMAL(p,s)
  - Edm.DateTime → TIMESTAMP

### 3. ETL Guidance
- Batch size recommendations (10K-50K)
- Pagination method ($top and $skip)
- Filtering method ($filter with date columns)
- Recommended timeout (60 seconds)

### 4. Pagination Hints
- If query returns max records (e.g., 1000)
- Should show "pagination_hint" with next_batch_skip
- Helps with incremental extraction

---

## 🎯 Success Criteria

**Minimum Success** (3/4 tools work):
- At least entity listing and metadata work
- Update README: 36/42 tools (86%)

**Target Success** (4/4 tools work):
- All Phase 5.1 tools operational
- Update README: 37/42 tools (88%)
- Confirm ETL batch processing works

**Excellent Success** (4/4 + large batches):
- All tools work
- Successfully query 10K+ records
- SQL type mappings accurate
- ETL features fully functional

---

## 🚀 What Happens After Testing

### If All 4 Tools Work:
1. Update README to show 37/42 tools (88%)
2. Add "ETL-Optimized Relational Tools" section
3. Document SQL type mappings
4. Create Phase 5.1 completion summary
5. **Celebrate 88% real data coverage!** 🎉

### If Some Tools Fail:
1. Analyze error messages
2. Check if different assets work
3. Verify endpoint availability
4. Update accordingly (partial success still valuable)

---

## 📝 Common Issues & Solutions

**Issue**: "OAuth connector not initialized"
**Solution**: Check .env file has valid OAuth credentials (should be working already)

**Issue**: "Entity doesn't exist"
**Solution**: Use `list_catalog_assets` to find correct asset names (case-sensitive)

**Issue**: "Error parsing XML metadata"
**Solution**: Try different asset (some may not support relational access)

**Issue**: Query returns fewer records than expected
**Solution**: Normal - asset may have limited data; try different asset

---

## 📊 Current Status

**Before Phase 5.1**:
- 38 tools total
- 33 with real data (87%)

**After Phase 5.1** (if all work):
- **42 tools total** (38 + 4 new)
- **37 with real data (88%)**
- **ETL capabilities added**

**Business Tool Coverage** (excluding 3 diagnostics + 2 deprecated):
- Total business tools: 37
- With real data: 37/37 (100%!) 🎉

---

## 🎯 Next Steps

1. **Run all 4 tests** above with Kiro
2. **Report results** in the format provided
3. **Share any observations** or issues
4. Based on results, I'll:
   - Update README with new coverage
   - Document ETL features
   - Create completion summary

---

**Ready to test!** 🚀

Please restart Claude Desktop and run the tests above. Report back with your results!

---

**Created**: December 11, 2025
**Status**: Ready for Testing
**Tools**: 4 new ETL-optimized relational tools
**Expected Coverage**: 88% (37/42 tools)
