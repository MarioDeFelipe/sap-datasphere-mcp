#!/usr/bin/env node

/**
 * SAP Datasphere MCP Server - npm wrapper
 * This script launches the Python-based MCP server
 *
 * @version 1.0.9
 * @license MIT
 */

const { spawn } = require('child_process');
const path = require('path');

// Check if Python is available
function checkPython() {
  return new Promise((resolve) => {
    const python = spawn('python', ['--version']);
    python.on('error', () => {
      const python3 = spawn('python3', ['--version']);
      python3.on('error', () => resolve(null));
      python3.on('close', (code) => resolve(code === 0 ? 'python3' : null));
    });
    python.on('close', (code) => resolve(code === 0 ? 'python' : null));
  });
}

async function main() {
  console.log('🚀 SAP Datasphere MCP Server v1.0.9');
  console.log('');

  // Check for Python
  const pythonCmd = await checkPython();

  if (!pythonCmd) {
    console.error('❌ Error: Python 3.10+ is required but not found.');
    console.error('');
    console.error('Please install Python 3.10 or higher:');
    console.error('  - Windows: https://www.python.org/downloads/');
    console.error('  - macOS: brew install python@3.10');
    console.error('  - Linux: sudo apt install python3.10');
    process.exit(1);
  }

  console.log(`✓ Python found: ${pythonCmd}`);

  // Check if sap-datasphere-mcp package is installed
  const checkInstall = spawn(pythonCmd, ['-m', 'pip', 'show', 'sap-datasphere-mcp']);

  checkInstall.on('close', (code) => {
    if (code !== 0) {
      console.log('');
      console.log('📦 Installing SAP Datasphere MCP Python package...');
      console.log('');

      const install = spawn(pythonCmd, ['-m', 'pip', 'install', '--upgrade', 'sap-datasphere-mcp'], {
        stdio: 'inherit'
      });

      install.on('close', (installCode) => {
        if (installCode !== 0) {
          console.error('');
          console.error('❌ Failed to install Python package.');
          console.error('');
          console.error('Please install manually:');
          console.error('  pip install sap-datasphere-mcp');
          process.exit(1);
        }

        console.log('');
        console.log('✓ Python package installed successfully');
        console.log('');
        startServer(pythonCmd);
      });
    } else {
      console.log('✓ Python package already installed');
      console.log('');
      startServer(pythonCmd);
    }
  });
}

function startServer(pythonCmd) {
  console.log('🌟 Starting MCP server...');
  console.log('');

  // Start the MCP server
  const server = spawn(pythonCmd, ['-m', 'sap_datasphere_mcp_server'], {
    stdio: 'inherit',
    env: process.env
  });

  server.on('error', (err) => {
    console.error('❌ Failed to start server:', err.message);
    process.exit(1);
  });

  server.on('close', (code) => {
    if (code !== 0) {
      console.error(`❌ Server exited with code ${code}`);
      process.exit(code);
    }
  });

  // Handle Ctrl+C gracefully
  process.on('SIGINT', () => {
    console.log('');
    console.log('👋 Shutting down server...');
    server.kill('SIGINT');
  });
}

// Run main function
main().catch((err) => {
  console.error('❌ Unexpected error:', err);
  process.exit(1);
});
