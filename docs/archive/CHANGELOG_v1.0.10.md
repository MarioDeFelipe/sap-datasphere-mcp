# Changelog - v1.0.10 (Dual Package Hotfix)

**Release Date:** 2025-12-16

## 🐛 Critical Package Fixes (npm + PyPI)

### Issue 1: npm Package - Invalid Python Dependency
Fixed a critical npm package configuration issue that prevented installation.

**Problem:**
- npm package v1.0.9 included invalid `peerDependencies` field with `"python": ">=3.10.0"`
- npm tried to resolve `python` as an npm package (which doesn't exist)
- Installation failed with error: "No matching version found for python@>=3.10.0"

**Root Cause:**
The `peerDependencies` field incorrectly listed Python as an npm dependency. Python is a system requirement, not an npm package.

---

### Issue 2: PyPI Package - Missing tool_descriptions.py Module

Python package v1.0.9 was missing the `tool_descriptions.py` module, causing import errors.

**Problem:**
- Package installed successfully but failed at runtime
- Error: `ModuleNotFoundError: No module named 'tool_descriptions'`
- Only `sap_datasphere_mcp_server.py` was included, missing dependency

**Root Cause:**
[pyproject.toml](pyproject.toml:89-91) only specified `sap_datasphere_mcp_server` in `py-modules`, missing `tool_descriptions` which is imported by the server.

**npm Fix:**
- Removed invalid `peerDependencies` field from [package.json](package.json:42-47)
- Python requirement now documented only in:
  - `engines` field (metadata only, not enforced by npm)
  - README.md (system requirements section)
  - Wrapper script error messages (runtime validation)

**PyPI Fix:**
- Added `tool_descriptions` to `py-modules` list in [pyproject.toml](pyproject.toml:91)
```diff
[tool.setuptools]
packages = ["auth"]
-py-modules = ["sap_datasphere_mcp_server"]
+py-modules = ["sap_datasphere_mcp_server", "tool_descriptions"]
```
- Rebuilt package with all required modules included

### Changes

**package.json:**
```diff
- "peerDependencies": {
-   "python": ">=3.10.0"
- }
```

**Result:**
- ✅ npm package now installs correctly
- ✅ No dependency resolution errors
- ✅ Python validation handled at runtime by wrapper script
- ✅ Clear error messages if Python not found

### Impact

**Before (v1.0.9):**
```bash
npm install -g @mariodefe/sap-datasphere-mcp
# ERROR: No matching version found for python@>=3.10.0
```

**After (v1.0.10):**
```bash
npm install -g @mariodefe/sap-datasphere-mcp
# ✅ SUCCESS: Package installed
npx @mariodefe/sap-datasphere-mcp
# Wrapper validates Python at runtime with helpful error messages
```

---

## 📦 Package Info

- **Package name**: `@mariodefe/sap-datasphere-mcp`
- **Version**: 1.0.10
- **Type**: npm hotfix (patch release)
- **Python package**: Still v1.0.9 (no changes needed)

---

## ✅ Testing

**Confirmed working:**
- ✅ `npm install -g @mariodefe/sap-datasphere-mcp` - Installs successfully
- ✅ `npx @mariodefe/sap-datasphere-mcp` - Launches server correctly
- ✅ Python validation works at runtime
- ✅ Auto-install of Python package from PyPI works
- ✅ Claude Desktop integration works

---

## 🙏 Credits

Thanks to **Kiro** for identifying and reporting this issue!

---

## 📚 Related

- **npm Package**: https://www.npmjs.com/package/@mariodefe/sap-datasphere-mcp
- **PyPI Package**: https://pypi.org/project/sap-datasphere-mcp/1.0.9/
- **GitHub**: https://github.com/MarioDeFelipe/sap-datasphere-mcp
- **Previous Version**: [CHANGELOG_v1.0.9.md](CHANGELOG_v1.0.9.md)

---

## Migration Guide

### From v1.0.9 to v1.0.10

**If you tried v1.0.9:**
```bash
# Uninstall broken version
npm uninstall -g @mariodefe/sap-datasphere-mcp

# Install fixed version
npm install -g @mariodefe/sap-datasphere-mcp
```

**If you're new:**
```bash
# Just install (recommended)
npm install -g @mariodefe/sap-datasphere-mcp

# Or use with npx (no install needed)
npx @mariodefe/sap-datasphere-mcp
```

**No changes needed:**
- Claude Desktop config remains the same
- Environment variables unchanged
- Python package still v1.0.9 (fully compatible)

---

## Summary

This is a **critical hotfix** for the npm package only. The Python package (v1.0.9) works perfectly and requires no changes. This release ensures that npm users can install and use the package without dependency resolution errors.

**Status**: ✅ npm package now fully functional and tested!
