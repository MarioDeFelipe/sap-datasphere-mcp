# Project Organization & Structure

## Repository Layout

```
mcp/
├── .github/                    # GitHub workflows and templates
├── .kiro/                      # Kiro steering rules and settings
├── docs/                       # Additional documentation
├── docusaurus/                 # Documentation website (Docusaurus)
├── samples/                    # Usage examples and integrations
├── src/                        # MCP server implementations
│   ├── server-name-mcp-server/ # Individual MCP server packages
│   └── ...                     # 40+ different MCP servers
├── .pre-commit-config.yaml     # Pre-commit hook configuration
├── .python-version             # Python version specification
├── .ruff.toml                  # Ruff linter configuration
├── README.md                   # Main project documentation
├── DEVELOPER_GUIDE.md          # Development setup and guidelines
├── DESIGN_GUIDELINES.md        # Comprehensive design patterns
└── VIBE_CODING_TIPS_TRICKS.md  # AI-assisted development practices
```

## MCP Server Structure

Each MCP server follows a standardized layout:

```
src/example-mcp-server/
├── README.md                   # Server-specific documentation
├── CHANGELOG.md                # Version history
├── LICENSE                     # Apache 2.0 license
├── NOTICE                      # Copyright notices
├── pyproject.toml              # Python project configuration
├── Dockerfile                  # Container configuration (optional)
├── awslabs/                    # Source code namespace
│   ├── __init__.py             # Namespace package marker
│   └── example_mcp_server/     # Main server package
│       ├── __init__.py         # Version and metadata
│       ├── server.py           # MCP server implementation
│       ├── models.py           # Pydantic data models
│       ├── consts.py           # Constants and configuration
│       └── ...                 # Additional modules as needed
└── tests/                      # Unit tests
    ├── __init__.py
    ├── test_server.py
    └── ...
```

## Naming Conventions

### Package Names
- **PyPI Package**: `awslabs.service-name-mcp-server` (kebab-case)
- **Python Module**: `awslabs.service_name_mcp_server` (snake_case)
- **Directory**: `service-name-mcp-server` (kebab-case)

### File Organization
- **server.py**: Main MCP server implementation with tools and resources
- **models.py**: Pydantic models for data validation and serialization
- **consts.py**: Constants, default values, and configuration
- **Additional modules**: Service-specific clients, utilities, helpers

## Documentation Structure

### Docusaurus Website
```
docusaurus/
├── docs/                       # Markdown documentation
│   ├── servers/                # Individual server documentation
│   └── ...                     # General documentation
├── src/                        # React components and pages
├── static/                     # Static assets
│   └── assets/
│       └── server-cards.json   # Server metadata for UI
├── sidebars.ts                 # Navigation configuration
└── docusaurus.config.ts        # Site configuration
```

### Server Documentation Requirements
- **README.md**: Installation, configuration, usage examples
- **Docusaurus page**: `.mdx` file in `docusaurus/docs/servers/`
- **Server card entry**: Metadata in `server-cards.json`
- **Sidebar entry**: Navigation in `sidebars.ts`

## Samples Organization

```
samples/
├── README.md                   # Samples overview
├── project-name/               # Individual sample projects
│   ├── README.md               # Sample-specific documentation
│   └── ...                     # Sample code and resources
└── ...
```

## Configuration Files

### Root Level
- **.python-version**: Specifies Python 3.13
- **.ruff.toml**: Shared linting configuration
- **.pre-commit-config.yaml**: Quality checks and hooks
- **.secrets.baseline**: Security scanning baseline

### Per-Server
- **pyproject.toml**: Dependencies, build config, tool settings
- **Dockerfile**: Optional containerization
- **.gitignore**: Server-specific ignore patterns

## Import Patterns

```python
# Standard imports
from awslabs.service_name_mcp_server import models
from awslabs.service_name_mcp_server.consts import DEFAULT_VALUE

# MCP framework
from mcp import McpError, types
from mcp.server import Server
from mcp.server.models import InitializationOptions

# AWS SDK
import boto3
from botocore.exceptions import ClientError

# Validation and logging
from pydantic import BaseModel, Field
from loguru import logger
```

## Entry Points

Each server defines its entry point in `pyproject.toml`:
```toml
[project.scripts]
"awslabs.service-name-mcp-server" = "awslabs.service_name_mcp_server.server:main"
```