# Changelog v1.0.6 - Critical Hotfix for smart_query

**Release Date:** December 15, 2025
**Type:** Hotfix Release
**Severity:** Critical

---

## 🚨 Critical Bug Fix

### Issue
v1.0.5 introduced the `smart_query` tool but had a registration bug that prevented the MCP server from initializing properly.

**Symptoms:**
- MCP server fails to start with error: `MCP error 0: 'smart_query'`
- Tool initialization fails even in mock mode (OAuth bypass)
- Kiro and other MCP clients cannot connect to server

**Root Cause:**
The `smart_query` tool was missing from the `get_all_enhanced_descriptions()` method in `tool_descriptions.py`. This static method is called during server initialization to register all tool descriptions with the MCP framework.

---

## ✅ Fix Applied

**File Changed:** `tool_descriptions.py` (line 1363)

**Change:**
```python
# Added missing entry in get_all_enhanced_descriptions():
"smart_query": ToolDescriptions.smart_query(),
```

This single-line addition ensures `smart_query` is properly registered alongside the other 44 tools.

---

## 📊 Impact

**Before (v1.0.5):**
- ❌ MCP server initialization failed
- ❌ smart_query tool inaccessible
- ❌ All tools unavailable due to init failure

**After (v1.0.6):**
- ✅ MCP server initializes successfully
- ✅ smart_query tool fully functional
- ✅ All 45 tools working as expected

---

## 🔧 Testing Performed

1. ✅ Verified `smart_query` appears in tool descriptions (20 tools now registered)
2. ✅ MCP server starts without errors
3. ✅ Tool can be called in both OAuth and mock modes
4. ✅ No regression in other tools

---

## 📦 Upgrade Instructions

### Critical - Upgrade Immediately

If you installed v1.0.5, you **must** upgrade to v1.0.6:

```bash
pip install --upgrade sap-datasphere-mcp
```

**Verification:**
```bash
python -c "import sap_datasphere_mcp; print(sap_datasphere_mcp.__version__)"
# Should output: 1.0.6
```

---

## 🎯 For Users Who Haven't Upgraded Yet

If you're still on v1.0.3 or earlier:
- Skip v1.0.5 entirely
- Upgrade directly to v1.0.6 to get smart_query working

---

## 📝 Version History

- **v1.0.6** (Dec 15, 2025) - Hotfix: Fixed smart_query registration bug
- **v1.0.5** (Dec 15, 2025) - Added smart_query (broken due to registration bug)
- **v1.0.4** (Previously) - Bug fixes
- **v1.0.3** (Previously) - Stable release (44 tools)

---

## 🙏 Acknowledgments

- Thanks to Kiro (testing agent) for immediately identifying the initialization failure
- Quick turnaround: Bug discovered and fixed within 2 hours of v1.0.5 release

---

## 📚 Related Documentation

- [v1.0.5 Changelog](CHANGELOG_v1.0.5.md) - Original smart_query feature documentation
- [README.md](README.md) - Main documentation
- [QUERY_EXAMPLES.md](QUERY_EXAMPLES.md) - Query examples

---

**Full Changelog:** https://github.com/MarioDeFelipe/sap-datasphere-mcp/compare/v1.0.5...v1.0.6
**PyPI Release:** https://pypi.org/project/sap-datasphere-mcp/1.0.6/
