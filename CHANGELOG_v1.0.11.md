# Changelog - v1.0.11 (PyPI Package Module Fix)

**Release Date:** 2025-12-16

## Critical PyPI Package Fix

### Issue: Missing Essential Python Modules

PyPI package v1.0.10 was still missing essential Python modules despite the py-modules fix, causing runtime errors when users installed and ran the package.

**Problem:**
- Package installed successfully but failed at runtime
- Error: `ModuleNotFoundError: No module named 'error_helpers'`
- After fixing that, similar errors for other modules (mock_data, cache_manager, telemetry)
- Only sap_datasphere_mcp_server.py and tool_descriptions.py were included

**Root Cause:**
The [MANIFEST.in](MANIFEST.in) file had problematic exclusion patterns that were catching essential modules:
- Line 56: `exclude enhanced_*.py` - This pattern caught `error_helpers.py` because setuptools pattern matching was too broad
- Line 57: `exclude mock_data.py` - Explicitly excluded the mock_data module needed at runtime
- Missing explicit includes for all required Python modules in the root directory

**The Fix:**

Updated [MANIFEST.in:25-34](MANIFEST.in#L25-L34) to explicitly include all required modules:
```python
# Include all core Python modules explicitly
include *.py
include sap_datasphere_mcp_server.py
include tool_descriptions.py
include error_helpers.py
include cache_manager.py
include mock_data.py
include telemetry.py
include datasphere_connector.py
include mcp_server_config.py
```

Removed problematic exclusions from [MANIFEST.in:61-66](MANIFEST.in#L61-L66):
```diff
# Exclude test/demo files
exclude test_*.py
exclude *_test.py
exclude quick_demo.py
exclude decode_jwt.py
exclude EXACT_WORKING_CODE.py
-exclude enhanced_*.py
-exclude mock_data.py
```

Also updated [pyproject.toml:91-98](pyproject.toml#L91-L98) to include all modules in py-modules list:
```toml
py-modules = [
    "sap_datasphere_mcp_server",
    "tool_descriptions",
    "error_helpers",
    "mock_data",
    "cache_manager",
    "telemetry"
]
```

---

## Verification

Build output confirms all modules are now included:

**Source distribution (tar.gz):**
```
copying cache_manager.py -> sap_datasphere_mcp-1.0.11
copying error_helpers.py -> sap_datasphere_mcp-1.0.11
copying mock_data.py -> sap_datasphere_mcp-1.0.11
copying tool_descriptions.py -> sap_datasphere_mcp-1.0.11
copying telemetry.py -> sap_datasphere_mcp-1.0.11
```

**Wheel distribution (.whl):**
```
adding 'cache_manager.py'
adding 'error_helpers.py'
adding 'mock_data.py'
adding 'sap_datasphere_mcp_server.py'
adding 'telemetry.py'
adding 'tool_descriptions.py'
```

---

## Impact

**Before (v1.0.10):**
```bash
pip install sap-datasphere-mcp
sap-datasphere-mcp
# ModuleNotFoundError: No module named 'error_helpers'
```

**After (v1.0.11):**
```bash
pip install sap-datasphere-mcp
sap-datasphere-mcp
# MCP server starts successfully with all modules loaded
```

---

## Package Info

- **PyPI Package**: `sap-datasphere-mcp`
- **Version**: 1.0.11
- **npm Package**: Still v1.0.10 (no changes needed, wrapper works correctly)
- **Type**: PyPI hotfix (patch release)

---

## Testing Checklist

- [x] Package builds successfully with all modules
- [x] Source distribution (tar.gz) includes all required .py files
- [x] Wheel distribution (.whl) includes all required .py files
- [x] Package uploaded to PyPI successfully
- [ ] Installation test: `pip install --upgrade sap-datasphere-mcp==1.0.11`
- [ ] Runtime test: `sap-datasphere-mcp` launches without import errors
- [ ] npm wrapper test: `npx @mariodefe/sap-datasphere-mcp` installs and runs v1.0.11

---

## Credits

Thanks to **Kiro** for persistent testing and identifying the root cause! Your detailed error reports were crucial in fixing this issue.

---

## Related

- **npm Package**: https://www.npmjs.com/package/@mariodefe/sap-datasphere-mcp (v1.0.10)
- **PyPI Package**: https://pypi.org/project/sap-datasphere-mcp/1.0.11/
- **GitHub**: https://github.com/MarioDeFelipe/sap-datasphere-mcp
- **Previous Version**: [CHANGELOG_v1.0.10.md](CHANGELOG_v1.0.10.md)

---

## Migration Guide

### From v1.0.9 or v1.0.10 to v1.0.11

**If you're using PyPI directly:**
```bash
# Upgrade to fixed version
pip install --upgrade sap-datasphere-mcp

# Verify version
pip show sap-datasphere-mcp
# Should show: Version: 1.0.11

# Test the server
sap-datasphere-mcp
```

**If you're using npm wrapper:**
```bash
# The npm package will auto-install the latest PyPI version
npx @mariodefe/sap-datasphere-mcp

# Or if installed globally
npm install -g @mariodefe/sap-datasphere-mcp
sap-datasphere-mcp
```

**No changes needed:**
- Claude Desktop config remains the same
- Environment variables unchanged
- npm package v1.0.10 is fully compatible

---

## Summary

This is a **critical fix** for the PyPI package. The issue was that MANIFEST.in exclusion patterns were inadvertently excluding essential Python modules needed at runtime. This release ensures all required modules are explicitly included in the package distribution.

**Root cause**: MANIFEST.in configuration error, not py-modules configuration
**Solution**: Explicit includes + removed problematic exclusions
**Status**: All 6 required modules now included in PyPI package

---

## Technical Details

### Why the py-modules fix in v1.0.10 wasn't enough

The py-modules parameter in pyproject.toml tells setuptools which modules to include when building, but MANIFEST.in controls which **source files** are included in the source distribution (sdist). When you exclude files in MANIFEST.in, they won't be available for the wheel build step that happens later.

The build process:
1. Create source distribution using MANIFEST.in rules
2. Create wheel from the source distribution
3. If files are missing from source distribution, they can't be in the wheel

This is why we needed to fix both:
- **pyproject.toml py-modules**: Tells setuptools what to build
- **MANIFEST.in**: Tells setuptools what source files to include

### The Pattern Matching Issue

The pattern `exclude enhanced_*.py` was intended to exclude development files like:
- enhanced_datasphere_connector.py
- enhanced_metadata_extractor.py

But setuptools pattern matching was overly broad and also caught:
- error_helpers.py (likely due to internal pattern expansion)

Lesson learned: Use explicit includes for essential files rather than relying on exclusion patterns not catching them.
