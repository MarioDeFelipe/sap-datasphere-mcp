"""
Enhanced tool descriptions for SAP Datasphere MCP Server

Provides rich, detailed descriptions that help AI assistants understand
when and how to use each tool effectively.
"""

from typing import Dict


class ToolDescriptions:
    """Enhanced descriptions for all MCP tools"""

    @staticmethod
    def list_spaces() -> Dict:
        """Enhanced description for list_spaces tool"""
        return {
            "description": """List all SAP Datasphere spaces with their status and metadata.

**Use this tool when:**
- User asks "What spaces are available?" or "Show me all spaces"
- You need to discover available Datasphere environments
- Starting data exploration workflow
- Checking space status and availability

**What you'll get:**
- Space IDs and names
- Space status (ACTIVE, DEVELOPMENT, etc.)
- Table/view counts per space
- Owner information (with include_details=True)

**Example queries:**
- "What Datasphere spaces exist?"
- "Show me all data spaces"
- "Which spaces are active?"

**Next steps after using this tool:**
- Use get_space_info() to explore a specific space
- Use search_tables() to find tables across spaces
""",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "include_details": {
                        "type": "boolean",
                        "description": "Set to true to include detailed information (owner, created date, connection counts). Default: false for quick space listing.",
                        "default": False
                    }
                }
            }
        }

    @staticmethod
    def get_space_info() -> Dict:
        """Enhanced description for get_space_info tool"""
        return {
            "description": """Get comprehensive information about a specific SAP Datasphere space.

**Use this tool when:**
- User asks about a specific space (e.g., "Tell me about SALES_ANALYTICS")
- You need to see what tables/views exist in a space
- Checking space configuration and metadata
- Following up from list_spaces() results

**What you'll get:**
- Complete space metadata (status, owner, created date)
- List of all tables and views in the space
- Table schemas and row counts
- Connection information

**Required parameter:**
- space_id: Must be uppercase (e.g., 'SALES_ANALYTICS', 'FINANCE_DWH')

**Example queries:**
- "Show me the SALES_ANALYTICS space"
- "What tables are in FINANCE_DWH?"
- "Tell me about the HR_ANALYTICS space"

**Error handling:**
- If space not found, list_spaces() will show available spaces
""",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "The space ID in UPPERCASE format (e.g., 'SALES_ANALYTICS', 'FINANCE_DWH', 'HR_ANALYTICS'). Must match exactly."
                    }
                },
                "required": ["space_id"]
            }
        }

    @staticmethod
    def search_tables() -> Dict:
        """Enhanced description for search_tables tool"""
        return {
            "description": """Search for tables and views across all Datasphere spaces by name or description.

**Use this tool when:**
- User asks "Find tables with customer data"
- Looking for tables containing specific keywords
- Don't know exact table name but know the domain
- Searching across multiple spaces

**Search behavior:**
- Searches both table names and descriptions
- Case-insensitive matching
- Returns results from all spaces (or specific space if filtered)
- Includes table metadata (type, columns, row counts)

**Search tips:**
- Use domain keywords: "customer", "sales", "order", "finance"
- Partial matches work: "cust" finds "CUSTOMER_DATA"
- Filter by space_id to narrow results

**Example queries:**
- "Find all tables related to customers"
- "Search for sales order tables"
- "Show me all tables with 'finance' in the name"

**Next steps:**
- Use get_table_schema() for detailed column information
- Use execute_query() to retrieve actual data
""",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "search_term": {
                        "type": "string",
                        "description": "Keyword to search for in table names and descriptions (e.g., 'customer', 'sales', 'order'). Case-insensitive, partial matches work."
                    },
                    "space_id": {
                        "type": "string",
                        "description": "Optional: Filter results to a specific space (e.g., 'SALES_ANALYTICS'). Leave empty to search all spaces."
                    }
                },
                "required": ["search_term"]
            }
        }

    @staticmethod
    def get_table_schema() -> Dict:
        """Enhanced description for get_table_schema tool"""
        return {
            "description": """Get detailed schema information for a specific table or view.

**Use this tool when:**
- User asks "What columns are in CUSTOMER_DATA?"
- Need to understand table structure before querying
- Planning JOIN operations (need to see key columns)
- Checking data types for analysis

**What you'll get:**
- Complete column list with data types
- Primary key indicators
- Column descriptions
- Table metadata (row count, last updated)

**Required parameters:**
- space_id: The space containing the table (uppercase)
- table_name: Exact table name (case-sensitive, usually uppercase)

**Example queries:**
- "Show me the schema of CUSTOMER_DATA in SALES_ANALYTICS"
- "What columns does SALES_ORDERS have?"
- "Describe the GL_ACCOUNTS table structure"

**Best practices:**
- Use search_tables() first if you don't know the exact table name
- Check column types before writing queries
- Identify key columns for JOINs

**Next steps:**
- Use execute_query() with proper column names and types
""",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "The space ID containing the table (e.g., 'SALES_ANALYTICS'). Must be uppercase."
                    },
                    "table_name": {
                        "type": "string",
                        "description": "Exact table or view name (e.g., 'CUSTOMER_DATA', 'SALES_ORDERS'). Case-sensitive, typically uppercase."
                    }
                },
                "required": ["space_id", "table_name"]
            }
        }

    @staticmethod
    def list_connections() -> Dict:
        """Enhanced description for list_connections tool"""
        return {
            "description": """List all external data source connections and their current status.

**Use this tool when:**
- User asks "What data sources are connected?"
- Checking connection health and availability
- Understanding data lineage and sources
- Troubleshooting data refresh issues

**What you'll get:**
- Connection IDs and names
- Connection types (SAP_ERP, SALESFORCE, EXTERNAL, etc.)
- Connection status (CONNECTED, DISCONNECTED, ERROR)
- Host information and last tested timestamp

**Supported connection types:**
- SAP_ERP, SAP_S4HANA, SAP_BW
- SALESFORCE, EXTERNAL
- SNOWFLAKE, DATABRICKS
- POSTGRESQL, MYSQL, ORACLE, SQLSERVER, HANA

**Example queries:**
- "What external connections exist?"
- "Show me all SAP ERP connections"
- "Check if Salesforce connection is active"

**Use cases:**
- Data integration monitoring
- Connection health checks
- Understanding data sources
""",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "connection_type": {
                        "type": "string",
                        "description": "Optional: Filter by specific connection type (e.g., 'SAP_ERP', 'SALESFORCE', 'EXTERNAL'). Leave empty to show all connections."
                    }
                }
            }
        }

    @staticmethod
    def get_task_status() -> Dict:
        """Enhanced description for get_task_status tool"""
        return {
            "description": """Get status and execution details of data integration and ETL tasks.

**Use this tool when:**
- User asks "What tasks are running?"
- Monitoring data pipeline execution
- Checking when data was last refreshed
- Troubleshooting failed tasks

**What you'll get:**
- Task IDs and names
- Execution status (COMPLETED, RUNNING, FAILED, SCHEDULED)
- Last run timestamp and next scheduled run
- Execution duration and records processed
- Associated space information

**Filtering options:**
- No parameters: Show all tasks
- task_id: Get specific task details
- space_id: Show all tasks for a space

**Example queries:**
- "What tasks are currently running?"
- "Show me all tasks in SALES_ANALYTICS"
- "When did DAILY_SALES_ETL last run?"
- "Check status of task FINANCE_RECONCILIATION"

**Task types:**
- ETL/data loading tasks
- Transformation workflows
- Scheduled data refreshes
- Data replication jobs
""",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Optional: Specific task ID to check (e.g., 'DAILY_SALES_ETL'). Leave empty to see all tasks."
                    },
                    "space_id": {
                        "type": "string",
                        "description": "Optional: Filter tasks by space (e.g., 'SALES_ANALYTICS'). Shows only tasks associated with that space."
                    }
                }
            }
        }

    @staticmethod
    def browse_marketplace() -> Dict:
        """Enhanced description for browse_marketplace tool"""
        return {
            "description": """Browse and search available data packages in the SAP Datasphere marketplace.

**Use this tool when:**
- User asks "What data packages are available?"
- Looking for external reference data (benchmarks, currency rates, etc.)
- Exploring marketplace offerings
- Planning to enrich internal data with external sources

**What you'll get:**
- Package IDs and names
- Package descriptions and categories
- Provider information
- Package versions and sizes
- Pricing information (Free or paid)

**Categories:**
- Reference Data (industry benchmarks, standards)
- Financial Data (currency rates, market data)
- Geospatial Data
- Industry-specific datasets

**Example queries:**
- "What marketplace packages are available?"
- "Find financial data packages"
- "Show me industry benchmarks"
- "Search for currency rate data"

**Use cases:**
- Data enrichment planning
- Finding external reference data
- Competitive benchmarking
- Currency conversion support
""",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Optional: Filter by category (e.g., 'Reference Data', 'Financial Data'). Leave empty to browse all."
                    },
                    "search_term": {
                        "type": "string",
                        "description": "Optional: Search keyword for package names or descriptions (e.g., 'currency', 'benchmark'). Case-insensitive."
                    }
                }
            }
        }

    @staticmethod
    def execute_query() -> Dict:
        """Enhanced description for execute_query tool"""
        return {
            "description": """Execute read-only SQL queries against SAP Datasphere tables to retrieve and analyze data.

**IMPORTANT: This is a HIGH-RISK tool that requires user consent before execution.**

**Use this tool when:**
- User explicitly requests data retrieval (e.g., "Show me customers from USA")
- Need to perform data analysis with aggregations
- Joining multiple tables for insights
- Filtering and sorting data

**Capabilities:**
- SELECT queries with full SQL syntax (WHERE, JOIN, GROUP BY, ORDER BY, LIMIT)
- Read-only access - NO write operations allowed
- Results limited to 100 rows by default (configurable via limit parameter)
- Automatic query sanitization and injection prevention

**Security & Restrictions:**
- Only SELECT statements allowed
- Blocked operations: INSERT, UPDATE, DELETE, DROP, CREATE, ALTER, etc.
- No SQL comments allowed (security risk)
- Queries sanitized to prevent injection attacks
- User consent required before execution (high-risk operation)

**Query best practices:**
1. Always specify a LIMIT to control result size
2. Use WHERE clauses to filter data efficiently
3. Check table schema first with get_table_schema()
4. Use qualified table names when joining

**Example queries:**
- "SELECT * FROM CUSTOMER_DATA WHERE country = 'USA' LIMIT 10"
- "SELECT customer_id, SUM(amount) as total FROM SALES_ORDERS GROUP BY customer_id ORDER BY total DESC LIMIT 20"
- "SELECT c.customer_name, o.order_date, o.amount FROM CUSTOMER_DATA c JOIN SALES_ORDERS o ON c.customer_id = o.customer_id WHERE o.status = 'COMPLETED' LIMIT 50"

**Error handling:**
- Invalid SQL syntax: Returns syntax error with guidance
- Forbidden operations: Blocked with explanation
- Missing tables: Suggests using search_tables() to find correct name
- Permission denied: Explains consent requirement

**Note:** This tool uses mock data in development. Real query execution requires OAuth authentication.
""",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "The Datasphere space ID where tables exist (e.g., 'SALES_ANALYTICS', 'FINANCE_DWH'). Must be uppercase."
                    },
                    "sql_query": {
                        "type": "string",
                        "description": "The SELECT query to execute. Must start with SELECT. Examples: 'SELECT * FROM CUSTOMER_DATA LIMIT 10', 'SELECT customer_id, COUNT(*) FROM SALES_ORDERS GROUP BY customer_id'"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of rows to return. Default: 100. Range: 1-1000. Use smaller limits for faster responses.",
                        "default": 100
                    }
                },
                "required": ["space_id", "sql_query"]
            }
        }

    @staticmethod
    def get_all_enhanced_descriptions() -> Dict[str, Dict]:
        """Get all enhanced tool descriptions"""
        return {
            "list_spaces": ToolDescriptions.list_spaces(),
            "get_space_info": ToolDescriptions.get_space_info(),
            "search_tables": ToolDescriptions.search_tables(),
            "get_table_schema": ToolDescriptions.get_table_schema(),
            "list_connections": ToolDescriptions.list_connections(),
            "get_task_status": ToolDescriptions.get_task_status(),
            "browse_marketplace": ToolDescriptions.browse_marketplace(),
            "execute_query": ToolDescriptions.execute_query()
        }
