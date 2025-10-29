# 🚀 SAP Datasphere MCP Server

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![MCP Protocol](https://img.shields.io/badge/MCP-Compatible-purple.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Production Ready](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

> **Professional Model Context Protocol (MCP) server that enables AI assistants to seamlessly interact with SAP Datasphere environments for metadata discovery, data exploration, and analytics operations.**

## 📋 **Project Overview**

> **Note**: This is a specialized SAP Datasphere MCP server that provides AI assistants with comprehensive access to SAP Datasphere environments. The project is entirely focused on SAP Datasphere integration and provides text-based configuration through interactive prompts.



## 🌟 **Key Highlights**

- 🤖 **MCP Server**: AI-accessible SAP Datasphere operations via Model Context Protocol
- 🔐 **OAuth 2.0 Integration**: Secure authentication with SAP Datasphere
- 🔍 **Metadata Discovery**: Explore spaces, assets, and schema information
- 📊 **Data Querying**: Execute OData queries through natural language
- 🧠 **AI Integration**: Claude Desktop, Cursor IDE, and other AI assistants ready
- 🛠️ **Developer Friendly**: Comprehensive testing and development tools
- 📚 **Well Documented**: Complete setup guides and API documentation

## 🤖 **MCP Server for AI Assistants**

### AI-Accessible Tools
- **`search_metadata`** - Search assets across SAP Datasphere with business context
- **`discover_spaces`** - OAuth-enabled discovery of all Datasphere spaces
- **`get_asset_details`** - Detailed asset information with schema and metadata
- **`query_asset_data`** - Execute OData queries on SAP Datasphere assets
- **`search_metadata`** - Search across metadata with intelligent filtering
- **`get_connection_status`** - Monitor SAP Datasphere connectivity and health

### Supported AI Assistants
- **Claude Desktop** - Full MCP integration with configuration examples
- **Cursor IDE** - Native MCP support for development workflows
- **Custom AI Tools** - Standard MCP protocol for any AI assistant

## 📊 **MCP Server Capabilities**

### AI-Accessible Operations
- **Metadata Discovery** - Explore spaces, assets, and schema information
- **Data Querying** - Execute OData queries through natural language
- **Asset Management** - Detailed asset information and relationships
- **Connection Monitoring** - Real-time connectivity and health checks
- **Search & Filter** - Intelligent metadata search across all objects

### Integration Benefits
- **Natural Language Interface** - Ask questions about your data in plain English
- **Real-time Access** - Direct connection to live SAP Datasphere data
- **Secure Authentication** - OAuth 2.0 integration with proper token management

## 🚀 **Quick Start**

### Prerequisites
```bash
# Required
Python 3.10+
SAP Datasphere account with Technical User configured
OAuth 2.0 application setup in SAP Datasphere for the Technical User

# Optional for AI Integration
Claude Desktop or Cursor IDE
```

### Installation
```bash
# 1. Clone the repository
git clone https://github.com/MarioDeFelipe/sap-datasphere-mcp.git
cd sap-datasphere-mcp

# 2. Install dependencies
pip install -r requirements.txt

# 3. The server will prompt for SAP Datasphere credentials on startup

# 4. Start MCP Server
python start_mcp_server.py
```

### Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/MarioDeFelipe/sap-datasphere-mcp.git
cd sap-datasphere-mcp
uv venv && uv sync --all-groups

# 2. The server will prompt for SAP Datasphere credentials on startup

# 3. Start MCP Server
python start_mcp_server.py
```

## 🏗️ **Architecture Overview**

### MCP Server Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   AI Assistant  │◄──►│   MCP Server     │◄──►│  SAP Datasphere │
│ (Claude, Cursor)│    │                  │    │   (OAuth 2.0)   │
└─────────────────┘    │ • Metadata Ops   │    └─────────────────┘
                       │ • Asset Discovery│    
                       │ • Data Queries   │    
                       │ • Space Explorer │    
                       └──────────────────┘
```

### Core MCP Tools
```
🔍 discover_spaces      → List all accessible Datasphere spaces
📋 get_space_assets     → Get assets within a specific space  
📊 get_asset_details    → Retrieve detailed asset information
🔎 query_asset_data     → Execute OData queries on assets
🔍 search_metadata      → Search across metadata with filters
🔗 get_connection_status → Check SAP Datasphere connectivity
```

## 📋 **Core Components**

### 🤖 **MCP Server Implementation**
- **`sap_datasphere_mcp_server.py`**: Main MCP server with all tools and resources
- **Model Context Protocol compliance** for AI assistant integration
- **Tool definitions** for metadata discovery and data querying
- **Resource management** for SAP Datasphere connections

### 🔐 **Authentication & Connection**
- **`enhanced_datasphere_connector.py`**: OAuth 2.0 SAP Datasphere connector
- **Automatic token refresh** and session management
- **Connection pooling** for efficient resource usage
- **Error handling** with retry logic and exponential backoff

### 📊 **Metadata & Query Engine**
- **`enhanced_metadata_extractor.py`**: SAP Datasphere metadata extraction
- **OData query execution** for data retrieval
- **Schema discovery** and asset information parsing
- **Intelligent caching** for improved performance

### 🧪 **Testing & Development**
- **`test_mcp_server.py`**: Comprehensive MCP server tests
- **`test_simple_server.py`**: Basic functionality tests
- **MCP Inspector integration** for development and debugging
- **Configuration validation** and connection testing

## 📊 **MCP Server Features**

### Available MCP Tools:
```
🔍 discover_spaces      → List all accessible SAP Datasphere spaces
📋 get_space_assets     → Get assets within a specific space
📊 get_asset_details    → Retrieve detailed asset information and schema
🔎 query_asset_data     → Execute OData queries through natural language
🔍 search_metadata      → Search across metadata with intelligent filtering
🔗 get_connection_status → Check SAP Datasphere connectivity and health
```

### AI Assistant Integration:
```
🤖 Claude Desktop       → Full MCP integration with configuration examples
🎯 Cursor IDE          → Native MCP support for development workflows
🔧 Custom AI Tools     → Standard MCP protocol for any AI assistant
📝 Natural Language    → Ask questions about your data in plain English
🔐 Secure Access       → OAuth 2.0 authentication with automatic token refresh
```

### Performance Characteristics:
- ⚡ **Response Time**: Sub-100ms for metadata queries
- 🔄 **Concurrent Operations**: Multiple simultaneous MCP requests supported
- 🛡️ **Reliability**: Automatic error handling and OAuth token refresh
- 📊 **Scalability**: Efficient caching and connection pooling

## 🤖 **MCP Server for AI Assistants**

### Claude Desktop Integration
Add to your Claude Desktop `mcp.json` configuration:

```json
{
  "mcpServers": {
    "sap-datasphere": {
      "command": "python",
      "args": ["start_mcp_server.py", "--environment", "dog"],
      "cwd": "/path/to/sap-datasphere-mcp",
      "env": {
        "MCP_ENVIRONMENT": "dog"
      }
    }
  }
}
```

The server will prompt you for SAP Datasphere credentials when it starts.

### Example AI Queries
Once configured, you can ask your AI assistant:

```
"List all SAP Datasphere spaces and their assets"
"Search for tables containing customer data"
"Show me the schema for SAP_SC_FI_T_Products"
"What's the connection status to SAP Datasphere?"
"Execute a query to get financial data from SAP_SC_FI_T_Products"
"Show me all analytical models in the SAP_SC_FI_AM space"
```

### Cursor IDE Integration
Add to your Cursor settings for development workflows:

```json
{
  "mcp.servers": {
    "sap-datasphere": {
      "command": ["python", "start_mcp_server.py"],
      "args": ["--environment", "dog"],
      "env": {
        "MCP_ENVIRONMENT": "dog"
      }
    }
  }
}
```

The server will prompt you for SAP Datasphere credentials when it starts.

## 🔧 **Configuration**

### SAP Datasphere Configuration
Configure your SAP Datasphere connection by providing credentials when prompted by the MCP server:

- **Base URL**: Your SAP Datasphere tenant URL (e.g., https://your-tenant.eu20.hcs.cloud.sap)
- **Client ID**: OAuth 2.0 client ID for your Technical User
- **Client Secret**: OAuth 2.0 client secret for your Technical User
- **Token URL**: OAuth token endpoint (e.g., https://your-tenant.authentication.eu20.hana.ondemand.com/oauth/token)

### MCP Server Configuration
```python
# Example MCP server configuration
{
  "server_name": "sap-datasphere",
  "log_level": "INFO",
  "cache_ttl": 300,
  "max_connections": 10
}
```

## 🚀 **API Endpoints & MCP Tools**

### MCP Tools (AI Assistant Access)
```python
search_metadata(query, asset_types, source_systems)     # Search across systems
discover_spaces(include_assets, force_refresh)          # OAuth space discovery  
get_asset_details(asset_id, source_system)             # Detailed asset info
get_connection_status(detailed)                       # Connection monitoring
query_asset_data(asset_id, odata_query)               # Data querying
search_metadata(query, filters)                       # Metadata search
```

### MCP Protocol Interface
```python
# Available MCP tools for AI assistants
discover_spaces()           # List SAP Datasphere spaces
get_space_assets(space_id)  # Get assets in a space
get_asset_details(asset_id) # Get detailed asset information
query_asset_data(query)     # Execute OData queries
search_metadata(terms)      # Search across metadata
get_connection_status()     # Check connectivity
```

### System Health & Monitoring
```http
GET    /api/status             # System health check
GET    /api/metrics            # Performance metrics
WS     /ws                     # WebSocket for real-time updates
```

## 🔒 **Security Features**

- 🔐 **OAuth 2.0**: Secure SAP Datasphere authentication
- 🔒 **HTTPS/TLS**: Encrypted communications
- 📝 **Audit Logging**: Complete operation audit trails
- 🔑 **Token Management**: Automatic refresh and rotation

## 🎯 **Use Cases**

### AI-Powered Data Discovery
- **Natural Language Queries**: Ask AI assistants about your data assets
- **Intelligent Recommendations**: AI-guided query optimization and data exploration
- **Automated Documentation**: AI-generated data catalogs and asset descriptions

### Enterprise Data Access
- **Metadata Discovery**: Explore and understand your SAP Datasphere assets
- **Natural Language Queries**: Ask questions about your data through AI assistants
- **Real-time Access**: Direct connection to live SAP Datasphere data

### Advanced Data Governance
- **Business Context Preservation**: Maintain rich metadata across systems
- **Automated Classification**: AI-powered data classification and tagging
- **Compliance Tracking**: Complete audit trails and governance workflows

## 🛠️ **Development**

### Project Structure
```
sap-datasphere-mcp/
├── 📁 .kiro/                           # Kiro specs and steering rules
│   └── specs/sap-datasphere-mcp-server/ # MCP server specifications
├── 📁 config/                          # Configuration files
├── 📁 src/                             # Source code modules
├── 📄 sap_datasphere_mcp_server.py     # Main MCP server implementation
├── 📄 start_mcp_server.py              # MCP server launcher
├── 📄 enhanced_datasphere_connector.py  # OAuth-enabled SAP connector

├── 📄 enhanced_metadata_extractor.py   # Metadata extraction utilities
├── 📄 test_mcp_server.py               # MCP server tests
└── 📄 requirements.txt                 # Dependencies
```

### Running Tests
```bash
# MCP Server tests
python test_mcp_server.py

# Simple server tests
python test_simple_server.py

# Test with MCP Inspector
npx @modelcontextprotocol/inspector python sap_datasphere_mcp_server.py
```

## 📈 **Monitoring & Observability**

### MCP Server Monitoring
- 🤖 **AI Request Tracking**: Monitor MCP tool usage and performance
- 📊 **OAuth Token Management**: Automatic refresh and expiration tracking
- 🔍 **Cache Performance**: Hit/miss rates and optimization metrics
- 📝 **Audit Logs**: Complete AI assistant interaction history

### MCP Server Monitoring
- 📊 **Request Tracking**: Monitor MCP tool usage and performance
- 🔐 **OAuth Management**: Automatic token refresh and expiration tracking
- 📝 **Audit Logs**: Complete AI assistant interaction history
- 🚨 **Error Handling**: Robust error handling with detailed logging

### Integration Options
- **Logging**: Structured logging with configurable levels
- **Metrics**: Performance metrics for MCP operations
- **Health Checks**: Built-in health monitoring endpoints
- **Debugging**: MCP Inspector integration for development

## ✨ **Advanced Features**

### Enhanced Metadata Discovery
- **CSDL Metadata Extraction**: Complete OData schema definitions
- **Business Context Preservation**: Rich annotations and governance information
- **Multi-language Support**: Global deployment with localized metadata
- **Hierarchical Relationships**: Preserve analytical model structures

### Advanced MCP Features
- **Intelligent Caching**: Optimized metadata caching with TTL management
- **Connection Pooling**: Efficient SAP Datasphere connection management
- **Error Recovery**: Automatic retry logic with exponential backoff
- **Schema Discovery**: Dynamic discovery of asset schemas and relationships

### AI-Powered Operations
- **Natural Language Queries**: Ask questions about your data in plain English
- **Smart Query Optimization**: AI-guided query optimization and caching strategies
- **Automated Documentation**: AI-generated data catalogs and schema documentation
- **Intelligent Error Resolution**: AI-assisted troubleshooting and optimization

## 🤝 **Contributing**

We welcome contributions! This project uses Kiro for AI-assisted development.

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/MarioDeFelipe/sap-datasphere-mcp.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Configure MCP server for development
python mcp_server_config.py

# Run comprehensive tests
python test_mcp_server.py --environment dog
```

### Contribution Areas
- **MCP Tools**: Add new AI-accessible operations
- **Data Connectors**: Enhance SAP and AWS integrations
- **Query Patterns**: Implement new data access strategies
- **AI Agents**: Develop specialized data integration assistants

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **Model Context Protocol** for enabling AI assistant integration
- **SAP Datasphere Team** for comprehensive API capabilities
- **Python Community** for excellent development tools and libraries
- **Kiro AI Assistant** for accelerating development workflows

## 📞 **Support**

- 📚 **Documentation**: [MCP Server Guide](MCP_SERVER_README.md)
- 🐛 **Issues**: [GitHub Issues](https://github.com/MarioDeFelipe/sap-datasphere-mcp/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/MarioDeFelipe/sap-datasphere-mcp/discussions)
- 📖 **SAP Datasphere Docs**: [Official Documentation](https://help.sap.com/docs/SAP_DATASPHERE)
- 🤖 **MCP Protocol**: [Model Context Protocol](https://modelcontextprotocol.io/)

## 🚀 **What's Next**

### Immediate Roadmap
- **Enhanced AI Agents**: Specialized agents for different integration patterns
- **Vector Database Integration**: Semantic search across metadata
- **Real-time Event Streaming**: Live data change notifications
- **Advanced Schema Visualization**: Interactive metadata exploration

### Future Vision
- **Multi-Cloud Support**: Azure Synapse, Google BigQuery integration
- **Machine Learning Integration**: Predictive data quality and optimization
- **Enterprise Governance**: Advanced compliance and audit capabilities
- **Self-Service Analytics**: Business user-friendly data discovery

---

<div align="center">

**🏆 Built with ❤️ for AI-powered enterprise data integration**

[![GitHub stars](https://img.shields.io/github/stars/MarioDeFelipe/sap-datasphere-mcp?style=social)](https://github.com/MarioDeFelipe/sap-datasphere-mcp/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/MarioDeFelipe/sap-datasphere-mcp?style=social)](https://github.com/MarioDeFelipe/sap-datasphere-mcp/network/members)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-purple.svg)](https://modelcontextprotocol.io/)

</div>
