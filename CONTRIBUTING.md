# Contributing to SAP Datasphere MCP Server

Thank you for your interest in contributing to the SAP Datasphere MCP Server! This document provides guidelines and information for contributors.

## 🎯 How to Contribute

### Reporting Issues
- Use the [GitHub Issues](https://github.com/yourusername/sap-datasphere-mcp-server/issues) page
- Search existing issues before creating a new one
- Provide detailed information including:
  - Steps to reproduce
  - Expected vs actual behavior
  - Environment details (Python version, OS, etc.)
  - Error messages or logs

### Suggesting Features
- Open an issue with the "enhancement" label
- Describe the feature and its use case
- Explain how it would benefit users
- Consider implementation complexity

### Code Contributions

#### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/yourusername/sap-datasphere-mcp-server.git
cd sap-datasphere-mcp-server

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
python test_simple_server.py
```

#### Code Style
- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and small
- Use type hints where appropriate

#### Testing
- Add tests for new functionality
- Ensure existing tests pass
- Test both mock and live modes (when applicable)
- Include edge cases and error conditions

#### Pull Request Process
1. **Fork** the repository
2. **Create** a feature branch from `main`
3. **Make** your changes with clear, focused commits
4. **Add** tests for new functionality
5. **Update** documentation as needed
6. **Ensure** all tests pass
7. **Submit** a pull request with:
   - Clear description of changes
   - Reference to related issues
   - Screenshots (if UI changes)

## 🏗️ Project Structure

```
sap-datasphere-mcp-server/
├── sap_datasphere_mcp_simple.py    # Main MCP server
├── test_simple_server.py            # Test suite
├── README.md                        # Project documentation
├── pyproject.toml                   # Python project config
├── requirements.txt                 # Dependencies
├── examples/                        # Usage examples
├── docs/                           # Additional documentation
└── tests/                          # Test files
```

## 🧪 Development Guidelines

### Mock Data
- Keep mock data realistic and representative
- Update mock data when adding new features
- Ensure JSON serialization compatibility
- Document mock data structure

### OAuth Integration
- Maintain separation between mock and live modes
- Test OAuth flows when credentials are available
- Handle authentication errors gracefully
- Document OAuth setup process

### MCP Protocol
- Follow MCP specification strictly
- Test with multiple MCP clients when possible
- Ensure proper error handling and responses
- Document tool schemas clearly

### Documentation
- Update README for new features
- Add inline code comments
- Include usage examples
- Update CHANGELOG for releases

## 🔧 Development Tools

### Recommended Tools
- **IDE**: VS Code with Python extension
- **Linting**: ruff or flake8
- **Formatting**: black
- **Type Checking**: mypy
- **Testing**: pytest

### Pre-commit Hooks
Consider setting up pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

## 📋 Issue Labels

- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Improvements to documentation
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `oauth` - Related to OAuth authentication
- `mock-data` - Related to mock data
- `mcp-protocol` - MCP protocol compliance

## 🚀 Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create release branch
4. Test thoroughly
5. Create GitHub release
6. Tag version

## 💡 Tips for Contributors

### Getting Started
- Start with documentation improvements
- Fix typos or improve examples
- Add test cases
- Enhance mock data

### Understanding the Codebase
- Read the MCP specification
- Understand SAP Datasphere concepts
- Review existing tools and resources
- Test with Claude Desktop or other MCP clients

### Best Practices
- Write clear commit messages
- Keep pull requests focused
- Respond to review feedback promptly
- Be respectful in discussions

## 🤝 Code of Conduct

### Our Standards
- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain professional communication

### Unacceptable Behavior
- Harassment or discrimination
- Trolling or insulting comments
- Publishing private information
- Unprofessional conduct

## 📞 Getting Help

- **Questions**: Open a GitHub Discussion
- **Issues**: Create a GitHub Issue
- **Chat**: Join our community discussions
- **Email**: Contact maintainers directly

## 🏆 Recognition

Contributors will be recognized in:
- README acknowledgments
- Release notes
- Contributor list
- Special thanks for significant contributions

Thank you for contributing to the SAP Datasphere MCP Server! 🎉