# Technology Stack & Build System

## Core Technologies

- **Python 3.10+** - Primary programming language (3.13 currently used)
- **Model Context Protocol (MCP)** - Core framework for AI-server communication
- **Pydantic** - Data validation and serialization
- **FastMCP** - Python MCP framework implementation
- **Loguru** - Structured logging
- **uv** - Python package manager and virtual environment tool

## Build System

- **Package Manager**: `uv` for dependency management and virtual environments
- **Build Backend**: Hatchling (specified in pyproject.toml)
- **Package Distribution**: PyPI via `uvx` for easy installation
- **Monorepo Structure**: Multiple MCP servers in `src/` directory

## Code Quality & Linting

- **Ruff** - Fast Python linter and formatter
  - Line length: 99 characters
  - Google docstring convention
  - Single quotes for strings
- **Pyright** - Type checking
- **Pre-commit hooks** - Automated quality checks
- **Bandit** - Security scanning
- **pytest** - Testing framework with coverage reporting

## Common Commands

### Development Setup
```bash
# Install dependencies and create virtual environment
uv venv && uv sync --all-groups

# Install pre-commit hooks
pre-commit install
```

### Testing & Quality
```bash
# Run tests with coverage
uv run --frozen pytest --cov --cov-branch --cov-report=term-missing

# Run linting and formatting
ruff check --fix
ruff format

# Type checking
uv run --frozen --all-extras --dev pyright --stats

# Run all pre-commit checks
pre-commit run --all-files
```

### Local Development
```bash
# Run MCP server locally for testing
uv --directory <server-path> run server.py

# Test with MCP Inspector
npx @modelcontextprotocol/inspector uv --directory <server-path> run server.py
```

### Documentation
```bash
# Start Docusaurus development server
cd docusaurus && npm start

# Build documentation
cd docusaurus && npm run build
```

## AWS Integration

- **Boto3** - AWS SDK for Python
- **AWS CLI** - For credential configuration
- **Environment Variables** - AWS_PROFILE, AWS_REGION for authentication
- **IAM Roles/Policies** - Service-specific permissions required

## Package Structure

Each MCP server follows this pattern:
```
src/server-name-mcp-server/
├── pyproject.toml          # Project configuration
├── awslabs/
│   └── server_name_mcp_server/
│       ├── __init__.py     # Version info
│       ├── server.py       # Main MCP server
│       ├── models.py       # Pydantic models
│       └── consts.py       # Constants
└── tests/                  # Unit tests
```