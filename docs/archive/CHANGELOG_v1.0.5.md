# Changelog v1.0.5 - Smart Query & Intelligent Routing

**Release Date:** December 15, 2025
**Type:** Feature Release - Composite Tools

---

## 🚀 Major New Feature: Smart Query Tool

### What's New

**Smart Query** - Intelligent query router that combines `execute_query`, `query_relational_entity`, and `query_analytical_data` into a single, reliable tool with automatic routing and fallback logic.

**Why This Matters:**
- Users no longer need to understand which query method to use
- Automatic fallback if primary method fails (much better reliability)
- Intelligent routing based on query pattern analysis
- Detailed execution logs for debugging

---

## ✨ New Tool

### `smart_query` - Intelligent Query Router

**Features:**
- **Auto-detection:** Analyzes query to determine best execution method
- **Intelligent routing:**
  - Aggregations (SUM, COUNT, GROUP BY) → Analytical endpoint
  - Simple SELECT → Relational endpoint (most reliable)
  - Complex SQL → SQL parsing with OData conversion
- **Fallback handling:** If primary method fails, automatically tries alternatives
- **Execution logging:** Shows routing decisions and attempted methods
- **Performance optimization:** Routes to fastest method for query type

**Parameters:**
- `space_id` - Space ID (e.g., "SAP_CONTENT")
- `query` - SQL query
- `mode` - Routing mode: "auto" (default), "relational", "analytical", "sql"
- `limit` - Max rows (default: 1000, up to 50K)
- `include_metadata` - Include routing logs (default: true)
- `fallback` - Enable fallback methods (default: true)

**Example Usage:**
```python
# Auto-routing - simple SELECT
smart_query(
    space_id="SAP_CONTENT",
    query="SELECT * FROM SAP_SC_FI_V_ProductsDim LIMIT 5"
)

# Auto-routing - aggregation
smart_query(
    space_id="SAP_CONTENT",
    query="SELECT COMPANYNAME, SUM(GROSSAMOUNT) FROM SAP_SC_SALES_V_SalesOrders GROUP BY COMPANYNAME"
)

# Force specific mode
smart_query(
    space_id="SAP_CONTENT",
    query="SELECT * FROM table",
    mode="relational"
)
```

**Response includes:**
- Query results (data)
- Method used (relational, analytical, sql, or fallback)
- Execution time
- Rows returned
- Routing decision log
- Detected query characteristics

---

##  Previous Updates Included

### Bug Fixes from v1.0.4
- Fixed execute_query API endpoint structure (3-part path)
- Added local `import re` for async context handling
- Removed invalid timeout parameter

### Documentation from v1.0.4
- Added comprehensive QUERY_EXAMPLES.md
- Updated README with query examples section
- Added 37+ data asset examples

---

## 📊 Tool Count Update

**Total Tools:** 44 → **45 tools**
- Added: `smart_query` (composite tool)
- Real Data Coverage: 44/45 tools (98%)
- All existing tools preserved (Option A implementation)

---

## 🎯 Benefits

### For Users:
1. **Simplified Querying:** Don't need to choose between 3 query methods
2. **Better Reliability:** Automatic fallback if primary method fails
3. **Clearer Errors:** Detailed logs showing what was attempted
4. **Performance:** Routes to optimal method automatically

### For Developers:
1. **Debugging:** Execution logs show routing decisions
2. **Flexibility:** Can force specific modes when needed
3. **Backward Compatible:** All existing tools still available
4. **Production Ready:** Fallback logic for reliability

---

## 🔄 Implementation Strategy

**Option A:** Keep old tools + add new composite tool
- ✅ Backward compatibility maintained
- ✅ Power users can still use specific methods
- ✅ New users get simplified interface
- ✅ No breaking changes

---

## 📝 Documentation Updates

### Updated Files:
- `tool_descriptions.py` - Added smart_query description
- `sap_datasphere_mcp_server.py` - Added handler and tool definition
- `auth/authorization.py` - Added authorization entry
- `pyproject.toml` - Updated to v1.0.5
- `README.md` - Updated tool count and features

---

## 🚀 Upgrade Instructions

### From v1.0.3 or v1.0.4:

```bash
pip install --upgrade sap-datasphere-mcp
```

**No configuration changes needed** - smart_query is immediately available alongside all existing tools.

### Using Smart Query:

```python
# Instead of choosing between these:
query_relational_entity(...)
query_analytical_data(...)
execute_query(...)

# Just use smart_query with auto-routing:
smart_query(
    space_id="SAP_CONTENT",
    query="SELECT * FROM table",
    mode="auto"  # automatically chooses best method
)
```

---

## 🔮 Future Enhancements

Based on this composite tool pattern, future releases may include:

**v1.1.0 candidates:**
- `discover_data` - Combines find_assets_by_column + get_metadata + search_tables
- `extract_data` - Combines query_relational_entity + analyze_column_distribution + batching
- `explore_space` - Combines list_spaces + list_catalog_assets + get_space_details

---

## 📈 Statistics

**v1.0.5 by the numbers:**
- **45 tools total** (was 44)
- **44 tools with real data** (98% coverage)
- **1 new composite tool** (smart_query)
- **258 lines** of new handler code
- **135 lines** of documentation
- **3 methods combined** into one intelligent router

---

## 🙏 Acknowledgments

- Thanks to Kiro (testing agent) for identifying execute_query issues
- Thanks to the community for requesting simpler query interfaces

---

## 📚 Related Documentation

- [QUERY_EXAMPLES.md](QUERY_EXAMPLES.md) - Query examples and patterns
- [README.md](README.md) - Main documentation
- [API_REFERENCE.md](API_REFERENCE.md) - API details
- [TOOLS_CATALOG.md](TOOLS_CATALOG.md) - Complete tool list

---

**Full Changelog:** https://github.com/MarioDeFelipe/sap-datasphere-mcp/compare/v1.0.3...v1.0.5
**PyPI Release:** https://pypi.org/project/sap-datasphere-mcp/1.0.5/
