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
    def find_assets_by_column() -> Dict:
        """Find assets containing a specific column name - for data lineage and impact analysis"""
        return {
            "description": """Find all assets (tables/views) containing a specific column name across SAP Datasphere spaces.

**Use this tool when:**
- User asks "Which tables contain CUSTOMER_ID?"
- Performing data lineage analysis
- Impact analysis before schema changes
- Finding datasets for specific use cases
- Locating related data across spaces

**What you'll get:**
- Asset names and types (View, Table, etc.)
- Space IDs where assets are located
- Column information (name, type, position)
- Total column count per asset
- Consumption URLs for data access

**Use cases:**
- Data lineage discovery (find all uses of a column)
- Impact analysis (before renaming/removing columns)
- Dataset discovery (find tables with specific fields)
- Cross-space data exploration
- Schema relationship mapping

**Example queries:**
- "Find all tables with CUSTOMER_ID column"
- "Which views contain SALES_AMOUNT?"
- "Show me assets with COUNTRY_CODE in SAP_CONTENT space"
- "List tables that have ORDER_DATE column"

**Performance notes:**
- Searches across multiple spaces by default
- Uses intelligent caching for better performance
- Results limited to 50 assets by default (configurable)
- Case-insensitive search by default
""",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "column_name": {
                        "type": "string",
                        "description": "Column name to search for (case-insensitive by default). Examples: 'CUSTOMER_ID', 'SALES_AMOUNT', 'ORDER_DATE'"
                    },
                    "space_id": {
                        "type": "string",
                        "description": "Optional: Limit search to specific space (e.g., 'SAP_CONTENT'). Leave empty to search all spaces."
                    },
                    "max_assets": {
                        "type": "integer",
                        "description": "Optional: Maximum number of matching assets to return (1-200). Default: 50",
                        "minimum": 1,
                        "maximum": 200,
                        "default": 50
                    },
                    "case_sensitive": {
                        "type": "boolean",
                        "description": "Optional: Perform case-sensitive column name matching. Default: false",
                        "default": False
                    }
                },
                "required": ["column_name"]
            }
        }

    @staticmethod
    def analyze_column_distribution() -> Dict:
        """Analyze statistical distribution of column data - for data quality and profiling"""
        return {
            "description": """Perform advanced statistical analysis of a column's data distribution including nulls, distinct values, percentiles, and outlier detection.

**Use this tool when:**
- User asks "What's the data quality of AMOUNT column?"
- Performing data profiling before analytics
- Assessing column completeness and distribution
- Detecting outliers and data anomalies
- Understanding data patterns for ML/AI

**What you'll get:**
- Basic statistics (count, nulls, distinct values, completeness)
- Numeric statistics (min, max, mean, percentiles)
- Distribution analysis (top values, frequency)
- Outlier detection (IQR method)
- Data quality assessment

**Use cases:**
- Data quality assessment
- Pre-analytics data profiling
- Outlier and anomaly detection
- Understanding value distributions
- ML feature engineering preparation
- Data cleansing planning

**Example queries:**
- "Analyze the distribution of SALES_AMOUNT column"
- "What's the data quality of CUSTOMER_AGE?"
- "Profile the ORDER_STATUS column"
- "Detect outliers in PRICE column"
- "Show me statistics for QUANTITY field"

**Analysis includes:**
- Null percentage and completeness rate
- Distinct value count and cardinality
- For numeric columns: min, max, mean, percentiles (p25, p50, p75)
- Top value frequencies
- Outlier detection using IQR method
- Data quality recommendations

**Performance notes:**
- Analyzes up to 10,000 records (configurable)
- Default sample size: 1,000 records
- Works with numeric, string, and date columns
- Automatic type detection and appropriate statistics
""",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "Space ID containing the asset (e.g., 'SAP_CONTENT', 'SALES_ANALYTICS')"
                    },
                    "asset_name": {
                        "type": "string",
                        "description": "Asset (table/view) name containing the column"
                    },
                    "column_name": {
                        "type": "string",
                        "description": "Column name to analyze (e.g., 'SALES_AMOUNT', 'CUSTOMER_AGE', 'ORDER_STATUS')"
                    },
                    "sample_size": {
                        "type": "integer",
                        "description": "Optional: Number of records to analyze (10-10000). Default: 1000. Larger samples = more accurate but slower.",
                        "minimum": 10,
                        "maximum": 10000,
                        "default": 1000
                    },
                    "include_outliers": {
                        "type": "boolean",
                        "description": "Optional: Detect and report outliers using IQR method. Default: true",
                        "default": True
                    }
                },
                "required": ["space_id", "asset_name", "column_name"]
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
    def smart_query() -> Dict:
        """Enhanced description for smart_query tool - Intelligent query routing"""
        return {
            "description": """🚀 **SMART QUERY** - Intelligent query router that automatically selects the best execution method for your query.

**NEW in v1.0.5** - This is a composite tool combining execute_query, query_relational_entity, and query_analytical_data with intelligent routing and fallback logic.

**Why use smart_query instead of individual query tools?**
- ✅ Automatic routing to the most reliable method
- ✅ Fallback handling if primary method fails
- ✅ No need to understand different query methods
- ✅ Better error recovery and diagnostics
- ✅ Performance optimization based on query type

**How it works:**
1. **Analyzes your query** - Detects SQL syntax, aggregations, complexity
2. **Routes intelligently** - Chooses the best execution method:
   - Aggregations (SUM, COUNT, GROUP BY) → Analytical endpoint
   - Simple SELECT → Relational endpoint (most reliable)
   - Complex SQL → SQL parsing with OData conversion
3. **Falls back gracefully** - If primary method fails, tries alternatives
4. **Returns detailed logs** - Shows routing decisions and execution path

**Query Modes:**
- `auto` (default) - Intelligent routing based on query analysis
- `relational` - Force use of relational endpoint (most reliable)
- `analytical` - Force use of analytical endpoint (for aggregations)
- `sql` - Force use of SQL parsing method

**Use this tool when:**
- You want reliable query execution without worrying about method selection
- You're unsure which query method to use
- You need fallback handling for production reliability
- You want to see execution diagnostics

**Supported query patterns:**
- Simple SELECT: `SELECT * FROM SAP_SC_FI_V_ProductsDim LIMIT 10`
- Filtering: `SELECT * FROM table WHERE PRICE > 1000`
- Column selection: `SELECT PRODUCTID, PRICE FROM table`
- Aggregations: `SELECT COMPANYNAME, SUM(GROSSAMOUNT) FROM table GROUP BY COMPANYNAME`
- Sorting: `SELECT * FROM table ORDER BY PRICE DESC LIMIT 5`

**Parameters:**
- `space_id` - Space ID (e.g., "SAP_CONTENT")
- `query` - SQL query or natural language request
- `mode` - Routing mode: "auto", "relational", "analytical", "sql" (default: "auto")
- `limit` - Max rows to return (default: 1000)
- `include_metadata` - Include routing logs and decisions (default: true)
- `fallback` - Enable fallback to alternative methods (default: true)

**Example queries:**
```
# Auto-routing - simple SELECT
smart_query(space_id="SAP_CONTENT", query="SELECT * FROM SAP_SC_FI_V_ProductsDim LIMIT 5")

# Auto-routing - aggregation
smart_query(space_id="SAP_CONTENT", query="SELECT COMPANYNAME, SUM(GROSSAMOUNT) FROM SAP_SC_SALES_V_SalesOrders GROUP BY COMPANYNAME")

# Force relational mode
smart_query(space_id="SAP_CONTENT", query="SELECT * FROM SAP_SC_FI_V_ProductsDim", mode="relational")

# Disable fallback (fail fast)
smart_query(space_id="SAP_CONTENT", query="SELECT * FROM table", fallback=False)
```

**Response includes:**
- Query results (data)
- Method used (relational, analytical, sql, or fallback)
- Execution time
- Rows returned
- Routing decision log (if include_metadata=true)
- Detected query characteristics

**Error handling:**
- If primary method fails, automatically tries fallbacks
- Returns detailed error log showing all attempted methods
- Provides suggestions for fixing query issues
- Shows routing decisions for debugging

**Performance:**
- Relational: 1-5 seconds, up to 50K records
- Analytical: Fast for aggregations
- SQL: 1-5 seconds, up to 1K records

**When to use individual tools instead:**
- Use `query_relational_entity` when you need specific entity_name control
- Use `query_analytical_data` when you know you need analytical consumption
- Use `execute_query` when you need exact SQL syntax control
- Use `smart_query` for everything else (recommended for most use cases)

**Note:** This tool provides the same functionality as the individual query tools but with better reliability through intelligent routing and fallback handling.
""",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "The Datasphere space ID (e.g., 'SAP_CONTENT', 'SALES'). Must match existing space."
                    },
                    "query": {
                        "type": "string",
                        "description": "SQL query to execute. Examples: 'SELECT * FROM table LIMIT 10', 'SELECT col1, SUM(col2) FROM table GROUP BY col1'"
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["auto", "relational", "analytical", "sql"],
                        "description": "Query execution mode. Use 'auto' for intelligent routing (recommended). Default: 'auto'",
                        "default": "auto"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of rows to return. Default: 1000. Range: 1-50000",
                        "default": 1000
                    },
                    "include_metadata": {
                        "type": "boolean",
                        "description": "Include execution logs and routing decisions in response. Useful for debugging. Default: true",
                        "default": True
                    },
                    "fallback": {
                        "type": "boolean",
                        "description": "Enable fallback to alternative query methods if primary fails. Default: true",
                        "default": True
                    }
                },
                "required": ["space_id", "query"]
            }
        }

    @staticmethod
    def list_database_users() -> Dict:
        """Enhanced description for list_database_users tool"""
        return {
            "description": """List all database users in a specific SAP Datasphere space.

**Use this tool when:**
- User asks "What database users exist in SALES space?"
- Auditing user access and permissions
- Checking who has database access to a space
- Before creating a new database user (avoid duplicates)

**What you'll get:**
- Database user IDs and full names
- User status (ACTIVE, INACTIVE)
- Access permissions and privileges
- Last login information
- Audit policy settings

**Required parameter:**
- space_id: The space ID (uppercase, e.g., 'SALES', 'FINANCE')

**Example queries:**
- "List all database users in SALES space"
- "Show me who has database access to FINANCE"
- "What database users are configured?"

**Database user access types:**
- Consumption: Read data with/without grant privileges
- Ingestion: Write/load data into space
- Schema access: Local and space schema access
- Script server: Execute advanced analytics

**Note:** This corresponds to the CLI command: datasphere dbusers list --space <id>
""",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "The space ID in UPPERCASE format (e.g., 'SALES', 'FINANCE', 'HR'). Must match exactly."
                    },
                    "output_file": {
                        "type": "string",
                        "description": "Optional: Path to save output as JSON file (e.g., 'users.json'). If not provided, results display in response."
                    }
                },
                "required": ["space_id"]
            }
        }

    @staticmethod
    def create_database_user() -> Dict:
        """Enhanced description for create_database_user tool"""
        return {
            "description": """Create a new database user in a SAP Datasphere space with specified permissions.

**IMPORTANT: This is a HIGH-RISK tool that requires user consent before execution.**

**Use this tool when:**
- User requests "Create a database user named JEFF in SALES"
- Setting up new user access for applications or analysts
- Configuring data ingestion users
- Establishing read-only consumption users

**Required parameters:**
- space_id: The space where user will be created
- database_user_id: User name suffix (e.g., 'JEFF', 'REPORTING_USER')
- user_definition: JSON object defining permissions and settings

**User definition structure:**
```json
{
  "consumption": {
    "consumptionWithGrant": false,
    "spaceSchemaAccess": false,
    "scriptServerAccess": false,
    "enablePasswordPolicy": false,
    "localSchemaAccess": false,
    "hdiGrantorForCupsAccess": false
  },
  "ingestion": {
    "auditing": {
      "dppRead": {
        "isAuditPolicyActive": false,
        "retentionPeriod": 7
      },
      "dppChange": {
        "isAuditPolicyActive": false,
        "retentionPeriod": 7
      }
    }
  }
}
```

**Permission types:**
- **Consumption**: Read access to space data
  - consumptionWithGrant: Allow granting privileges to others
  - spaceSchemaAccess: Access to space schema objects
  - scriptServerAccess: Execute stored procedures/UDFs
- **Ingestion**: Write access for data loading
  - Audit policies for compliance (DPP read/change tracking)

**Security notes:**
- New password is auto-generated and returned (store securely!)
- Audit retention period: 1-365 days
- Minimum privilege principle recommended
- Password must be changed on first login

**Example queries:**
- "Create a read-only database user named ANALYST in SALES"
- "Set up a database user for data loading in FINANCE"
- "Create user REPORTING with consumption access"

**Note:** Corresponds to CLI: datasphere dbusers create --space <id> --databaseuser <name> --file-path <def.json>
""",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "The space ID where user will be created (e.g., 'SALES', 'FINANCE'). Must be uppercase."
                    },
                    "database_user_id": {
                        "type": "string",
                        "description": "Database user name suffix (e.g., 'JEFF', 'ANALYST', 'ETL_USER'). Will be prefixed with space name."
                    },
                    "user_definition": {
                        "type": "object",
                        "description": "JSON object defining user permissions and settings. Must include 'consumption' and 'ingestion' sections."
                    },
                    "output_file": {
                        "type": "string",
                        "description": "Optional: Path to save user credentials JSON (e.g., 'jeff.json'). RECOMMENDED for security - credentials shown only once!"
                    }
                },
                "required": ["space_id", "database_user_id", "user_definition"]
            }
        }

    @staticmethod
    def reset_database_user_password() -> Dict:
        """Enhanced description for reset_database_user_password tool"""
        return {
            "description": """Reset the password for an existing database user in SAP Datasphere.

**IMPORTANT: This is a HIGH-RISK tool that requires user consent before execution.**

**Use this tool when:**
- User requests "Reset password for database user JEFF"
- Password forgotten or compromised
- Regular password rotation policy
- Account locked due to failed login attempts

**What happens:**
- Old password is invalidated immediately
- New password is auto-generated securely
- User must change password on next login
- Action is logged for security audit

**Required parameters:**
- space_id: The space containing the database user
- database_user_id: The user whose password needs reset

**Security considerations:**
- New password shown only once - save securely!
- Recommend using output_file to save credentials
- Notify user through secure channel
- Enforce password change on first login
- All active sessions are terminated

**Example queries:**
- "Reset password for JEFF in SALES space"
- "Generate new password for database user ANALYST"
- "REPORTING_USER password expired, reset it"

**Best practices:**
- Always save output to secure file
- Communicate new password via secure channel (not email!)
- Verify user identity before resetting
- Document password reset in change log

**Note:** Corresponds to CLI: datasphere dbusers password reset --space <id> --databaseuser <name>
""",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "The space ID containing the database user (e.g., 'SALES', 'FINANCE'). Must be uppercase."
                    },
                    "database_user_id": {
                        "type": "string",
                        "description": "Database user name suffix whose password will be reset (e.g., 'JEFF', 'ANALYST')."
                    },
                    "output_file": {
                        "type": "string",
                        "description": "Optional: Path to save new credentials JSON (e.g., 'jeff_new.json'). HIGHLY RECOMMENDED for security!"
                    }
                },
                "required": ["space_id", "database_user_id"]
            }
        }

    @staticmethod
    def update_database_user() -> Dict:
        """Enhanced description for update_database_user tool"""
        return {
            "description": """Update permissions and configuration for an existing database user.

**IMPORTANT: This is a HIGH-RISK tool that requires user consent before execution.**

**Use this tool when:**
- User requests "Grant schema access to JEFF in SALES"
- Modifying user permissions or access levels
- Enabling/disabling audit policies
- Changing retention periods
- Updating user privileges

**What you can update:**
- Consumption permissions (read access, grants)
- Schema access (space, local, HDI)
- Script server access
- Audit policies and retention periods
- Password policies

**Required parameters:**
- space_id: The space containing the database user
- database_user_id: The user to update
- updated_definition: JSON with new configuration (full definition required)

**Update examples:**

**Grant schema access:**
```json
{
  "consumption": {
    "spaceSchemaAccess": true,
    "consumptionWithGrant": false,
    ...
  },
  "ingestion": {...}
}
```

**Enable audit logging:**
```json
{
  "consumption": {...},
  "ingestion": {
    "auditing": {
      "dppRead": {
        "isAuditPolicyActive": true,
        "retentionPeriod": 90
      }
    }
  }
}
```

**Important notes:**
- Must provide complete user definition (not partial updates)
- Changes take effect immediately
- Active sessions may need reconnection
- All changes are logged for audit

**Example queries:**
- "Grant space schema access to JEFF"
- "Enable audit logging for ANALYST with 90 day retention"
- "Update REPORTING_USER to have consumption with grant"

**Note:** Corresponds to CLI: datasphere dbusers update --space <id> --databaseuser <name> --file-path <def.json>
""",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "The space ID containing the database user (e.g., 'SALES', 'FINANCE'). Must be uppercase."
                    },
                    "database_user_id": {
                        "type": "string",
                        "description": "Database user name suffix to update (e.g., 'JEFF', 'ANALYST')."
                    },
                    "updated_definition": {
                        "type": "object",
                        "description": "Complete JSON object with updated permissions. Must include all settings (consumption, ingestion)."
                    },
                    "output_file": {
                        "type": "string",
                        "description": "Optional: Path to save updated configuration JSON (e.g., 'jeff_updated.json')."
                    }
                },
                "required": ["space_id", "database_user_id", "updated_definition"]
            }
        }

    @staticmethod
    def delete_database_user() -> Dict:
        """Enhanced description for delete_database_user tool"""
        return {
            "description": """Delete a database user from a SAP Datasphere space.

**IMPORTANT: This is a HIGH-RISK tool that requires user consent before execution.**
**WARNING: This action is IRREVERSIBLE. User and all associated permissions are permanently deleted.**

**Use this tool when:**
- User explicitly requests "Delete database user JEFF from SALES"
- Decommissioning user accounts
- Removing unauthorized access
- Cleaning up test/temporary users
- User left organization

**What happens:**
- User account is permanently deleted
- All active sessions terminated immediately
- All granted privileges revoked
- Cannot be undone - must recreate if needed
- Deletion is logged for audit

**Required parameters:**
- space_id: The space containing the database user
- database_user_id: The user to delete
- force: Optional flag to skip confirmation dialog

**Safety considerations:**
- PERMANENT deletion - no recovery possible
- Verify user identity and authorization
- Check if user owns any objects (may cause errors)
- Document reason for deletion
- Consider deactivating instead of deleting

**Before deleting:**
1. List user's current permissions (list_database_users)
2. Verify no applications depend on this user
3. Check if user owns database objects
4. Get management approval for production users
5. Document deletion in change log

**Example queries:**
- "Delete database user JEFF from SALES space"
- "Remove TEMP_USER from FINANCE"
- "Delete TEST_ANALYST - no longer needed"

**Best practices:**
- Always confirm with user before deleting
- Use force=false for interactive confirmation
- Keep audit trail of deletions
- For temporary removal, consider update instead

**Note:** Corresponds to CLI: datasphere dbusers delete --space <id> --databaseuser <name> [--force]
""",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "The space ID containing the database user (e.g., 'SALES', 'FINANCE'). Must be uppercase."
                    },
                    "database_user_id": {
                        "type": "string",
                        "description": "Database user name suffix to delete (e.g., 'JEFF', 'TEMP_USER'). WILL BE PERMANENTLY DELETED."
                    },
                    "force": {
                        "type": "boolean",
                        "description": "Skip confirmation dialog. Default: false (ask for confirmation). Set true only if user explicitly confirmed deletion.",
                        "default": False
                    }
                },
                "required": ["space_id", "database_user_id"]
            }
        }

    @staticmethod
    def list_catalog_assets() -> Dict:
        """Enhanced description for list_catalog_assets tool"""
        return {
            "description": """Browse all data assets across all SAP Datasphere spaces.

**Use this tool when:**
- User asks "What assets are available in Datasphere?"
- Building a complete data catalog or asset inventory
- Discovering available data assets across all spaces
- Searching for specific asset types across the system
- Understanding the overall data landscape

**What you'll get:**
- Asset IDs and names across all spaces
- Asset types (AnalyticalModel, View, Table)
- Space information for each asset
- Consumption URLs (analytical and relational)
- Exposure status and metadata URLs
- Creation and modification timestamps

**Available parameters:**
- select_fields: Specific fields to return (e.g., ['name', 'description', 'spaceId'])
- filter_expression: OData filter (e.g., "spaceId eq 'SAP_CONTENT'")
- top: Maximum results (default 50, max 1000)
- skip: Results to skip for pagination
- include_count: Include total count of assets

**Example queries:**
- "List all available assets in Datasphere"
- "Show me all analytical models across all spaces"
- "Find assets in the SAP_CONTENT space"
- "List the first 20 assets with their consumption URLs"

**Common filters:**
- By space: `filter_expression="spaceId eq 'SAP_CONTENT'"`
- By type: `filter_expression="assetType eq 'AnalyticalModel'"`
- Exposed only: `filter_expression="exposedForConsumption eq true"`
- Combined: `filter_expression="spaceId eq 'SALES' and assetType eq 'View'"`

**Asset types you'll see:**
- AnalyticalModel: Multi-dimensional models for analytics
- View: SQL views combining multiple data sources
- Table: Physical tables with business data
- Fact: Fact tables in analytical models
- Dimension: Dimension tables in analytical models

**Note:** This uses the Catalog API: GET /api/v1/datasphere/consumption/catalog/assets
""",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "select_fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific fields to return (e.g., ['name', 'description', 'spaceId']). If not specified, returns all fields."
                    },
                    "filter_expression": {
                        "type": "string",
                        "description": "OData filter expression (e.g., \"spaceId eq 'SAP_CONTENT'\" or \"assetType eq 'AnalyticalModel'\")."
                    },
                    "top": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 50, max: 1000).",
                        "default": 50
                    },
                    "skip": {
                        "type": "integer",
                        "description": "Number of results to skip for pagination (default: 0).",
                        "default": 0
                    },
                    "include_count": {
                        "type": "boolean",
                        "description": "Include total count of matching assets (default: false).",
                        "default": False
                    }
                },
                "required": []
            }
        }

    @staticmethod
    def get_asset_details() -> Dict:
        """Enhanced description for get_asset_details tool"""
        return {
            "description": """Get comprehensive metadata for a specific SAP Datasphere asset.

**Use this tool when:**
- User asks "Show me details about the Financial Transactions asset"
- Need complete asset documentation and structure
- Want to understand asset dimensions, measures, and relationships
- Looking for consumption URLs to access the data
- Checking asset business purpose and technical details
- Validating asset availability before integration

**What you'll get:**
- Complete asset metadata (name, description, business purpose)
- Space information and ownership details
- Asset type and consumption type (analytical/relational)
- Consumption URLs for data access
- Metadata URLs for schema information
- Dimensions and measures (for analytical models)
- Relationships to other assets
- Technical details (row count, size, refresh info)
- Business context (domain, classification, retention)
- Version and status information
- Tags and categorization

**Required parameters:**
- space_id: The space containing the asset (e.g., 'SAP_CONTENT')
- asset_id: The asset identifier (e.g., 'SAP_SC_FI_AM_FINTRANSACTIONS')

**Optional parameters:**
- expand_fields: Related entities to expand (e.g., ['columns', 'relationships'])

**Example queries:**
- "Get details for SAP_SC_FI_AM_FINTRANSACTIONS in SAP_CONTENT"
- "Show me the structure of the Financial Transactions asset"
- "What are the dimensions and measures of this analytical model?"
- "Give me the consumption URL for the Sales Data View"

**Use cases:**
- Understand asset structure before querying
- Get consumption URLs for data access
- Review asset business purpose and classification
- Check asset relationships and dependencies
- Validate data freshness (last refresh time)
- Generate asset documentation

**Note:** This uses the Catalog API: GET /api/v1/datasphere/consumption/catalog/spaces('{spaceId}')/assets('{assetId}')
""",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "The space ID in UPPERCASE format (e.g., 'SAP_CONTENT', 'SALES_ANALYTICS'). Must match exactly."
                    },
                    "asset_id": {
                        "type": "string",
                        "description": "The asset identifier (e.g., 'SAP_SC_FI_AM_FINTRANSACTIONS', 'CUSTOMER_VIEW')."
                    },
                    "expand_fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Related entities to expand (e.g., ['columns', 'relationships', 'metadata'])."
                    }
                },
                "required": ["space_id", "asset_id"]
            }
        }

    @staticmethod
    def get_asset_by_compound_key() -> Dict:
        """Enhanced description for get_asset_by_compound_key tool"""
        return {
            "description": """Retrieve asset using OData compound key identifier (alternative access method).

**Use this tool when:**
- You have both space ID and asset ID ready
- Want direct access without knowing the exact endpoint structure
- Working with bookmarked or favorited assets
- Have pre-known asset identifiers from other systems
- Need to resolve cross-references quickly

**What you'll get:**
- Same comprehensive metadata as get_asset_details
- Complete asset information with consumption URLs
- All dimensions, measures, and relationships
- Technical and business context

**Required parameters:**
- space_id: The space identifier
- asset_id: The asset identifier

**How it works:**
This tool combines space_id and asset_id into an OData compound key format:
`spaceId='SAP_CONTENT',assetId='SAP_SC_FI_AM_FINTRANSACTIONS'`

**Example queries:**
- "Get asset SAP_SC_FI_AM_FINTRANSACTIONS from SAP_CONTENT using compound key"
- "Retrieve CUSTOMER_VIEW in SALES_SPACE"

**When to use this vs get_asset_details:**
- **Use this**: When you want simplified parameter passing
- **Use get_asset_details**: When you need expand options or prefer explicit endpoint

**Note:** This uses the Catalog API: GET /api/v1/datasphere/consumption/catalog/assets({compoundKey})
""",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "The space identifier in UPPERCASE (e.g., 'SAP_CONTENT', 'SALES_SPACE')."
                    },
                    "asset_id": {
                        "type": "string",
                        "description": "The asset identifier (e.g., 'SAP_SC_FI_AM_FINTRANSACTIONS', 'CUSTOMER_VIEW')."
                    }
                },
                "required": ["space_id", "asset_id"]
            }
        }

    @staticmethod
    def get_space_assets() -> Dict:
        """Enhanced description for get_space_assets tool"""
        return {
            "description": """List all data assets within a specific SAP Datasphere space.

**Use this tool when:**
- User asks "What assets are in the SAP_CONTENT space?"
- Browsing assets within a specific space
- Creating a space-specific asset inventory
- Filtering assets by type within a space
- Validating space contents and available data
- Understanding what data is available in a space

**What you'll get:**
- All assets within the specified space
- Asset names, descriptions, and types
- Exposure status for each asset
- Consumption URLs (analytical and relational)
- Creation and modification timestamps
- Asset counts and pagination info

**Required parameters:**
- space_id: The space to browse (e.g., 'SAP_CONTENT')

**Optional parameters:**
- filter_expression: Filter by asset type or other criteria
- top: Maximum results (default 50, max 1000)
- skip: Results to skip for pagination

**Example queries:**
- "List all assets in the SAP_CONTENT space"
- "Show me analytical models in SALES_ANALYTICS"
- "What tables are available in FINANCE_SPACE?"
- "List exposed assets in SAP_CONTENT"

**Common filters:**
- By type: `filter_expression="assetType eq 'AnalyticalModel'"`
- Exposed only: `filter_expression="exposedForConsumption eq true"`
- By name pattern: `filter_expression="contains(name, 'Financial')"`
- Combined: `filter_expression="assetType eq 'View' and exposedForConsumption eq true"`

**Asset types:**
- **AnalyticalModel**: Multi-dimensional models with dimensions and measures
- **View**: SQL views combining data from multiple sources
- **Table**: Physical tables with business data
- **Fact**: Fact tables in dimensional models
- **Dimension**: Dimension tables for analysis

**Use cases:**
- Space content discovery
- Asset inventory generation
- Data availability validation
- Finding specific asset types
- Understanding space data landscape

**Note:** This uses the Catalog API: GET /api/v1/datasphere/consumption/catalog/spaces('{spaceId}')/assets
""",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "The space ID in UPPERCASE format (e.g., 'SAP_CONTENT', 'SALES_ANALYTICS'). Must match exactly."
                    },
                    "filter_expression": {
                        "type": "string",
                        "description": "OData filter expression (e.g., \"assetType eq 'AnalyticalModel'\" or \"exposedForConsumption eq true\")."
                    },
                    "top": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 50, max: 1000).",
                        "default": 50
                    },
                    "skip": {
                        "type": "integer",
                        "description": "Number of results to skip for pagination (default: 0).",
                        "default": 0
                    }
                },
                "required": ["space_id"]
            }
        }

    @staticmethod
    def run_task_chain() -> Dict:
        """Enhanced description for run_task_chain tool"""
        return {
            "description": """Execute a task chain in SAP Datasphere and get a log ID for tracking.

**Use this tool when:**
- User asks to "Run the ETL pipeline" or "Execute task chain X"
- Triggering scheduled data loads or transformations
- Starting data replication or synchronization jobs
- Automating data refresh workflows
- Executing orchestrated data pipelines

**What happens:**
- Task chain execution is initiated immediately
- Returns a logId to track the execution status
- Task runs asynchronously (use get_task_log to check status)
- All child tasks in the chain are executed in order

**Required parameters:**
- space_id: The space containing the task chain (e.g., 'SALES_SPACE')
- object_id: The task chain name/ID (e.g., 'Daily_ETL_Pipeline')

**What you'll get:**
- logId: Unique identifier to track this execution
- Use get_task_log(space_id, logId) to monitor progress
- Use get_task_history(space_id, object_id) to see all runs

**Example queries:**
- "Run the Daily_ETL_Pipeline in SALES_SPACE"
- "Execute task chain Customer_Sync in FINANCE_SPACE"
- "Trigger the data refresh pipeline in ANALYTICS"
- "Start the nightly batch job in DWH_SPACE"

**Important notes:**
- Task chains run asynchronously - tool returns immediately
- Check status with get_task_log using the returned logId
- Requires appropriate permissions to run task chains
- Failed runs can be investigated with detailed logs

**Workflow example:**
1. Run task chain: run_task_chain(space_id='SALES', object_id='Daily_ETL')
2. Get logId from response (e.g., 2295172)
3. Check status: get_task_log(space_id='SALES', log_id=2295172)
4. View details: get_task_log(space_id='SALES', log_id=2295172, detail_level='detailed')

**Note:** Uses API: POST /api/v1/datasphere/tasks/chains/{space_id}/run/{object_id}
""",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "The space ID containing the task chain (e.g., 'SALES_SPACE', 'FINANCE'). Must be uppercase."
                    },
                    "object_id": {
                        "type": "string",
                        "description": "The task chain name/identifier to execute (e.g., 'Daily_ETL_Pipeline', 'Customer_Sync')."
                    }
                },
                "required": ["space_id", "object_id"]
            }
        }

    @staticmethod
    def get_task_log() -> Dict:
        """Enhanced description for get_task_log tool"""
        return {
            "description": """Get detailed information about a specific task execution in SAP Datasphere.

**Use this tool when:**
- Checking status of a running task (after run_task_chain)
- Investigating why a task failed
- Viewing detailed execution logs and messages
- Monitoring task chain progress
- Debugging data pipeline issues

**What you'll get (depends on detail_level):**
- **status** (default): Simple status object {"status": "COMPLETED"}
- **status_only**: Just the status string "COMPLETED"
- **detailed**: Full details including messages and child nodes
- **extended**: Extended logs with complete message details

**Required parameters:**
- space_id: The space where the task ran
- log_id: The log ID from run_task_chain or get_task_history

**Optional parameters:**
- detail_level: Amount of detail to return
  - 'status' (default): Status object only
  - 'status_only': Status string only
  - 'detailed': Full logs with messages and children
  - 'extended': Extended logs with message details

**Status values:**
- RUNNING: Task is currently executing
- COMPLETED: Task finished successfully
- FAILED: Task encountered an error
- CANCELLED: Task was manually stopped

**Example queries:**
- "Check status of task log 2295172 in SALES_SPACE"
- "Get detailed logs for log ID 2295172"
- "Show me why task 2326060 failed in FINANCE"
- "Get extended execution details for log 2295172"

**Detailed response includes:**
- logId, status, startTime, endTime, runTime
- objectId (task chain name)
- user who ran the task
- children: Array of child task executions
- messages: Array of log messages with severity and timestamps

**Use cases:**
- Monitor long-running ETL jobs
- Debug failed data pipelines
- Audit task execution history
- Track data refresh timing
- Investigate error messages

**Note:** Uses API: GET /api/v1/datasphere/tasks/logs/{space_id}/{log_id}
""",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "The space ID where the task ran (e.g., 'SALES_SPACE', 'FINANCE'). Must be uppercase."
                    },
                    "log_id": {
                        "type": "integer",
                        "description": "The log ID to retrieve details for (obtained from run_task_chain or get_task_history)."
                    },
                    "detail_level": {
                        "type": "string",
                        "enum": ["status", "status_only", "detailed", "extended"],
                        "description": "Level of detail to return. Options: 'status' (default), 'status_only', 'detailed', 'extended'.",
                        "default": "status"
                    }
                },
                "required": ["space_id", "log_id"]
            }
        }

    @staticmethod
    def get_task_history() -> Dict:
        """Enhanced description for get_task_history tool"""
        return {
            "description": """Get the execution history for a specific task chain or object in SAP Datasphere.

**Use this tool when:**
- Viewing all previous runs of a task chain
- Analyzing task execution patterns
- Finding failed runs to investigate
- Checking historical performance
- Auditing task chain executions
- Understanding run frequency and duration

**What you'll get:**
- Array of all historical task runs for the specified object
- Each entry includes: logId, status, startTime, endTime, runTime
- Sorted by most recent first
- Shows RUNNING, COMPLETED, FAILED, CANCELLED runs

**Required parameters:**
- space_id: The space containing the task chain
- object_id: The task chain name to get history for

**Response includes for each run:**
- logId: Unique identifier for this execution
- status: RUNNING, COMPLETED, FAILED, or CANCELLED
- startTime: When the task started (ISO format)
- endTime: When the task finished (if completed)
- runTime: Duration in milliseconds
- objectId: The task chain name
- applicationId: Always 'TASK_CHAINS' for task chains
- activity: The activity type (e.g., 'RUN_CHAIN')
- user: Who initiated the run

**Example queries:**
- "Show me the run history for Daily_ETL_Pipeline in SALES_SPACE"
- "List all executions of Customer_Sync in FINANCE"
- "Get historical runs for Nested_Chain_1 in DWH_SPACE"
- "How many times has Data_Refresh run this week?"

**Use cases:**
- Identify recurring failures
- Analyze execution duration trends
- Find specific failed runs to debug
- Audit who ran tasks and when
- Plan maintenance windows
- Monitor SLA compliance

**Workflow example:**
1. Get history: get_task_history(space_id='SALES', object_id='Daily_ETL')
2. Find failed run: Look for status='FAILED', note logId
3. Get details: get_task_log(space_id='SALES', log_id=<failed_logId>, detail_level='detailed')
4. View error messages in the response

**Note:** Uses API: GET /api/v1/datasphere/tasks/logs/{space_id}/objects/{object_id}
""",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "The space ID containing the task chain (e.g., 'SALES_SPACE', 'FINANCE'). Must be uppercase."
                    },
                    "object_id": {
                        "type": "string",
                        "description": "The task chain name/identifier to get history for (e.g., 'Daily_ETL_Pipeline', 'Customer_Sync')."
                    }
                },
                "required": ["space_id", "object_id"]
            }
        }

    @staticmethod
    def monitor_local_tables() -> Dict:
        """Enhanced description for monitor_local_tables tool"""
        return {
            "description": """Get monitoring data for local tables in a SAP Datasphere space (row counts, sizes, last updated).

**Use this tool when:**
- User asks "How big are my tables?" or "Show me table sizes in space X"
- Monitoring storage usage and table growth
- Checking when tables were last updated or loaded
- Auditing table health and data freshness
- Capacity planning based on table sizes

**What you'll get:**
- Table names and technical names
- Row counts for each local table
- Storage size information (bytes)
- Last modification/load timestamps
- Table status and type information

**Example queries:**
- "Show me all local table sizes in SALES_ANALYTICS"
- "Which tables have the most rows in FINANCE_DWH?"
- "When was the last data load for tables in HR_ANALYTICS?"
- "How much storage is used by local tables in my space?"

**Next steps after using this tool:**
- Use query_table_data() to query data from a specific table
- Use monitor_remote_tables() to see remote table status
- Compare sizes over time for capacity planning

**Note:** Uses internal API: GET /dwaas-core/monitor/{space_id}/localTables
This is an internal Datasphere API and may not work in all configurations.
""",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "The space ID to monitor (e.g., 'SALES_ANALYTICS', 'FINANCE_DWH'). Must be uppercase."
                    }
                },
                "required": ["space_id"]
            }
        }

    @staticmethod
    def monitor_remote_tables() -> Dict:
        """Enhanced description for monitor_remote_tables tool"""
        return {
            "description": """Get monitoring data for remote tables in a SAP Datasphere space (replication status, connection info).

**Use this tool when:**
- User asks "What remote tables are in my space?" or "Show me replication status"
- Checking remote table replication health
- Monitoring data synchronization from source systems
- Auditing which connections are being used
- Verifying data freshness from external sources

**What you'll get:**
- Remote table names and technical names
- Source connection name and remote schema
- Replication type (REAL_TIME, SCHEDULED, NONE)
- Last replication timestamp
- Table status (ACTIVE, ERROR, REPLICATING)

**Example queries:**
- "Show me remote tables in SALES_ANALYTICS"
- "Which remote tables are failing replication?"
- "What connections are used in FINANCE_DWH?"
- "When was the last replication for remote tables?"

**Next steps after using this tool:**
- Use monitor_local_tables() to compare with local table data
- Investigate failed replications in the Datasphere UI
- Check task chain status with get_task_history()

**Note:** Uses internal API: GET /dwaas-core/monitor/{space_id}/remoteTables
This is an internal Datasphere API and may not work in all configurations.
""",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "The space ID to monitor (e.g., 'SALES_ANALYTICS', 'FINANCE_DWH'). Must be uppercase."
                    }
                },
                "required": ["space_id"]
            }
        }

    @staticmethod
    def query_table_data() -> Dict:
        """Enhanced description for query_table_data tool"""
        return {
            "description": """Query data directly from a local table in SAP Datasphere without requiring 'Expose for Consumption'.

**Use this tool when:**
- User wants to preview or explore local table data
- Querying tables that are NOT exposed for consumption
- Quick data validation and spot-checking
- Exploring table contents before building views
- The execute_query tool returns 403 because the asset isn't exposed

**What you'll get:**
- Actual table data rows with all or selected columns
- OData-formatted results with metadata
- Support for filtering, selecting columns, ordering, and pagination

**Parameters:**
- space_id (required): The space containing the table
- table_name (required): The local table name (e.g., 'TGT_IBUSINESSPARTNER')
- top (optional): Number of rows to return (default: 100, max: 10000)
- filter (optional): OData $filter expression (e.g., "COUNTRY eq 'US'")
- select (optional): Comma-separated column names (e.g., "NAME,CITY,COUNTRY")
- orderby (optional): OData $orderby expression (e.g., "NAME asc")
- skip (optional): Number of rows to skip for pagination

**Example queries:**
- "Show me the first 50 rows from TGT_IBUSINESSPARTNER in ZQCS_02"
- "Query SALES_ORDERS where COUNTRY is 'US' in SALES_ANALYTICS"
- "Get customer names and cities from CUSTOMER_DIM in FINANCE_DWH"
- "Show me data sorted by AMOUNT descending from TRANSACTIONS"

**Important limitations:**
- Only works for LOCAL tables (returns 406 for remote tables)
- Uses internal Datasphere API - may not work in all configurations
- For remote tables, use the standard execute_query tool instead

**Note:** Uses internal API: GET /dwaas-core/data-access/instant/{space_id}/{table_name}/{entity_name}
""",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "The space ID containing the table (e.g., 'ZQCS_02', 'SALES_ANALYTICS'). Must be uppercase."
                    },
                    "table_name": {
                        "type": "string",
                        "description": "The local table name to query (e.g., 'TGT_IBUSINESSPARTNER', 'SALES_ORDERS')."
                    },
                    "top": {
                        "type": "integer",
                        "description": "Maximum number of rows to return (default: 100, max: 10000).",
                        "default": 100
                    },
                    "filter": {
                        "type": "string",
                        "description": "OData $filter expression (e.g., \"COUNTRY eq 'US'\", \"AMOUNT gt 1000\")."
                    },
                    "select": {
                        "type": "string",
                        "description": "Comma-separated column names to return (e.g., 'NAME,CITY,COUNTRY'). Default: all columns."
                    },
                    "orderby": {
                        "type": "string",
                        "description": "OData $orderby expression (e.g., 'NAME asc', 'AMOUNT desc')."
                    },
                    "skip": {
                        "type": "integer",
                        "description": "Number of rows to skip for pagination (default: 0).",
                        "default": 0
                    }
                },
                "required": ["space_id", "table_name"]
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
            "find_assets_by_column": ToolDescriptions.find_assets_by_column(),
            "analyze_column_distribution": ToolDescriptions.analyze_column_distribution(),
            "execute_query": ToolDescriptions.execute_query(),
            "smart_query": ToolDescriptions.smart_query(),
            "list_database_users": ToolDescriptions.list_database_users(),
            "create_database_user": ToolDescriptions.create_database_user(),
            "reset_database_user_password": ToolDescriptions.reset_database_user_password(),
            "update_database_user": ToolDescriptions.update_database_user(),
            "delete_database_user": ToolDescriptions.delete_database_user(),
            "list_catalog_assets": ToolDescriptions.list_catalog_assets(),
            "get_asset_details": ToolDescriptions.get_asset_details(),
            "get_asset_by_compound_key": ToolDescriptions.get_asset_by_compound_key(),
            "get_space_assets": ToolDescriptions.get_space_assets(),
            # Task Management Tools (v1.0.12)
            "run_task_chain": ToolDescriptions.run_task_chain(),
            "get_task_log": ToolDescriptions.get_task_log(),
            "get_task_history": ToolDescriptions.get_task_history(),
            # Monitor & Data Access Tools (v1.0.13) - Internal APIs
            "monitor_local_tables": ToolDescriptions.monitor_local_tables(),
            "monitor_remote_tables": ToolDescriptions.monitor_remote_tables(),
            "query_table_data": ToolDescriptions.query_table_data()
        }
