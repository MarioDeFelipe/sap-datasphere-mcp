# NPM Publishing Guide - SAP Datasphere MCP v1.0.9

## Overview

This package provides an npm wrapper for the SAP Datasphere MCP Server, making it easy to install and use with Node.js-based MCP clients like Claude Desktop.

The npm package automatically installs the Python package from PyPI when needed.

---

## Prerequisites

1. **npm account**: Create one at https://www.npmjs.com/signup
2. **npm CLI**: Already installed with Node.js
3. **Access**: Package scope `@mariodef` (or adjust to your username)

---

## Publishing Steps

### 1. Log in to npm

```bash
npm login
```

Enter your:
- Username
- Password
- Email
- One-time password (if 2FA enabled)

Verify login:
```bash
npm whoami
```

### 2. Test package locally (optional)

```bash
# Check what will be published
npm pack --dry-run

# Create a tarball for testing
npm pack

# Test installation locally
npm install -g ./mariodef-sap-datasphere-mcp-1.0.9.tgz
```

### 3. Publish to npm

```bash
# Publish package
npm publish --access public

# Or if you encounter issues:
npm publish --access public --registry https://registry.npmjs.org/
```

### 4. Verify publication

Visit: https://www.npmjs.com/package/@mariodef/sap-datasphere-mcp

```bash
# Install from npm to test
npm install -g @mariodef/sap-datasphere-mcp

# Run the server
npx @mariodef/sap-datasphere-mcp
```

---

## Package Structure

```
sap-datasphere-mcp/
├── package.json          # npm package metadata
├── .npmignore           # Files to exclude from npm
├── bin/
│   └── sap-datasphere-mcp.js  # Node.js wrapper script
├── README.md            # Main documentation
├── LICENSE              # MIT license
└── CHANGELOG_v1.0.9.md  # Release notes
```

---

## How It Works

1. **User installs via npm**:
   ```bash
   npm install -g @mariodef/sap-datasphere-mcp
   ```

2. **Postinstall script runs**: Attempts to install Python package from PyPI
   ```bash
   pip install --upgrade sap-datasphere-mcp
   ```

3. **User runs the server**:
   ```bash
   npx @mariodef/sap-datasphere-mcp
   ```

4. **Wrapper script**:
   - Checks for Python 3.10+
   - Verifies Python package is installed
   - Launches the MCP server
   - Handles graceful shutdown

---

## Configuration for Claude Desktop

After installation, users add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sap-datasphere": {
      "command": "npx",
      "args": ["@mariodef/sap-datasphere-mcp"],
      "env": {
        "DATASPHERE_BASE_URL": "https://your-tenant.eu20.hcs.cloud.sap",
        "DATASPHERE_CLIENT_ID": "your-client-id",
        "DATASPHERE_CLIENT_SECRET": "your-client-secret",
        "DATASPHERE_TOKEN_URL": "https://your-tenant.authentication.eu20.hana.ondemand.com/oauth/token"
      }
    }
  }
}
```

---

## Updating the Package

### For version 1.0.10:

1. **Update version**:
   ```bash
   # Update both files
   # - package.json: "version": "1.0.10"
   # - pyproject.toml: version = "1.0.10"
   ```

2. **Update changelog**: Create `CHANGELOG_v1.0.10.md`

3. **Commit changes**:
   ```bash
   git add package.json bin/sap-datasphere-mcp.js CHANGELOG_v1.0.10.md
   git commit -m "Bump version to 1.0.10"
   git push
   ```

4. **Publish to npm**:
   ```bash
   npm publish
   ```

5. **Create GitHub release**:
   ```bash
   gh release create v1.0.10 --title "v1.0.10 - Description" --notes-file CHANGELOG_v1.0.10.md
   ```

---

## Troubleshooting

### "You do not have permission to publish"

- Make sure you're logged in: `npm whoami`
- Check package name availability: https://www.npmjs.com/package/@mariodef/sap-datasphere-mcp
- If taken, use different scope: `@yourname/sap-datasphere-mcp`

### "Python not found" when users install

- Users need Python 3.10+ installed
- Wrapper script provides clear error messages with installation links

### Postinstall fails silently

- This is intentional - warning message shown
- Users can manually run: `pip install sap-datasphere-mcp`

---

## npm Package Benefits

1. **Easy installation**: `npm install -g @mariodef/sap-datasphere-mcp`
2. **Claude Desktop integration**: Works with `npx` command
3. **Automatic updates**: `npm update -g @mariodef/sap-datasphere-mcp`
4. **Cross-platform**: Windows, macOS, Linux
5. **No Python knowledge required**: Automatic dependency management

---

## Package Info

- **Package name**: `@mariodef/sap-datasphere-mcp`
- **Version**: 1.0.9
- **License**: MIT
- **Python package**: `sap-datasphere-mcp` (auto-installed from PyPI)
- **Node.js**: >= 18.0.0
- **Python**: >= 3.10.0

---

## Support

- **npm**: https://www.npmjs.com/package/@mariodef/sap-datasphere-mcp
- **PyPI**: https://pypi.org/project/sap-datasphere-mcp/
- **GitHub**: https://github.com/MarioDeFelipe/sap-datasphere-mcp
- **Issues**: https://github.com/MarioDeFelipe/sap-datasphere-mcp/issues

---

## Summary

The npm package provides a convenient Node.js wrapper that:
- Checks for Python availability
- Automatically installs the Python package from PyPI
- Launches the MCP server with proper environment handling
- Works seamlessly with Claude Desktop and other MCP clients

Users get the best of both worlds: npm's easy installation + Python's powerful MCP server implementation!
