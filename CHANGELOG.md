# Changelog

All notable changes to the SAP Datasphere MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of SAP Datasphere MCP Server
- OAuth 2.0 client credentials authentication
- Basic space management tools
- Catalog browsing capabilities
- Connection listing functionality
- API endpoint discovery
- Comprehensive error handling and logging
- Interactive setup script
- Example usage scripts
- Full test suite

### Features
- `test_connection` - Test OAuth connectivity
- `discover_endpoints` - Find available API endpoints
- `list_spaces` - List all Datasphere spaces
- `get_space_info` - Get detailed space information
- `list_catalog` - Browse data catalog
- `get_table_info` - Get table schema and metadata
- `list_connections` - List data source connections

## [0.1.0] - 2025-01-13

### Added
- Initial project structure
- Core MCP server implementation
- SAP Datasphere API client
- OAuth authentication module
- Pydantic data models
- Configuration management
- Development tooling setup