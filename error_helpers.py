"""
Error Helper Module for SAP Datasphere MCP Server

Provides enhanced error messages with actionable suggestions and recovery strategies.
Helps AI assistants recover from errors and guide users toward successful outcomes.
"""

from typing import List, Optional
import json


class ErrorHelpers:
    """Enhanced error message generator with recovery suggestions"""

    @staticmethod
    def space_not_found(space_id: str, available_spaces: List[dict]) -> str:
        """Generate helpful error message when space is not found"""

        space_list = "\n".join(
            f"  - {s['id']}: {s['name']} ({s['status']})"
            for s in available_spaces
        )

        # Find similar space names
        suggestions = []
        space_id_lower = space_id.lower()
        for space in available_spaces:
            if space_id_lower in space['id'].lower() or space_id_lower in space['name'].lower():
                suggestions.append(f"  - Did you mean '{space['id']}'? ({space['name']})")

        suggestion_text = ""
        if suggestions:
            suggestion_text = f"\n\n**Similar spaces found:**\n" + "\n".join(suggestions)

        return f""">>> Space Not Found <<<

Space '{space_id}' does not exist in Datasphere.

**Available spaces:**
{space_list}
{suggestion_text}

**Common issues:**
- Space IDs are case-sensitive and usually UPPERCASE
- Use exact space ID, not the display name
- Example: Use 'SALES_ANALYTICS' not 'sales_analytics' or 'Sales Analytics'

**Next steps:**
1. Use list_spaces() to see all available spaces
2. Copy the exact space ID from the results
3. Try your request again with the correct space ID
"""

    @staticmethod
    def table_not_found(table_name: str, space_id: str, available_tables: List[dict]) -> str:
        """Generate helpful error message when table is not found"""

        if not available_tables:
            return f""">>> Table Not Found <<<

Table '{table_name}' not found in space '{space_id}'.

**This space has no tables.**

**Next steps:**
1. Verify the space ID is correct: list_spaces()
2. Check if tables exist in other spaces: get_space_info() for each space
3. Try searching across all spaces: search_tables(search_term="{table_name.split('_')[0].lower()}")
"""

        table_list = "\n".join(
            f"  - {t['name']}: {t['description']}"
            for t in available_tables[:10]  # Limit to 10
        )

        # Find similar table names
        suggestions = []
        table_lower = table_name.lower()
        for table in available_tables:
            if table_lower in table['name'].lower() or table_lower in table['description'].lower():
                suggestions.append(f"  - {table['name']}: {table['description']}")

        suggestion_text = ""
        if suggestions:
            suggestion_text = f"\n\n**Similar tables found:**\n" + "\n".join(suggestions[:5])

        more_tables = ""
        if len(available_tables) > 10:
            more_tables = f"\n... and {len(available_tables) - 10} more tables"

        return f""">>> Table Not Found <<<

Table '{table_name}' not found in space '{space_id}'.

**Available tables in {space_id}:**
{table_list}{more_tables}
{suggestion_text}

**Common issues:**
- Table names are case-sensitive and usually UPPERCASE
- Use exact table name as shown in schema
- Example: Use 'CUSTOMER_DATA' not 'customer_data' or 'Customer Data'

**Next steps:**
1. Use get_space_info(space_id="{space_id}") to see all tables
2. Or search by keyword: search_tables(search_term="customer")
3. Use the exact table name from the results
"""

    @staticmethod
    def invalid_query(error_message: str, space_id: str) -> str:
        """Generate helpful error message for invalid SQL queries"""

        return f""">>> SQL Query Error <<<

Your query failed validation: {error_message}

**Common SQL issues:**

1. **Write operations blocked:**
   - Only SELECT queries allowed
   - Blocked: INSERT, UPDATE, DELETE, DROP, CREATE, ALTER
   - Example: Use "SELECT * FROM table" not "DELETE FROM table"

2. **SQL comments not allowed:**
   - Remove all -- and /* */ comments
   - Comments are blocked for security reasons

3. **SQL injection patterns detected:**
   - Avoid patterns like "OR 1=1", "UNION SELECT"
   - Use parameterized queries
   - Don't chain statements with semicolons

4. **Invalid table/column names:**
   - Check spelling and case sensitivity
   - Use get_table_schema() to see correct column names

**Troubleshooting steps:**

1. **Check table schema first:**
   ```
   get_table_schema(space_id="{space_id}", table_name="YOUR_TABLE")
   ```

2. **Start with a simple SELECT:**
   ```
   SELECT * FROM YOUR_TABLE LIMIT 10
   ```

3. **Add filters gradually:**
   ```
   SELECT column1, column2 FROM YOUR_TABLE WHERE condition LIMIT 100
   ```

**Need help building a query?**
Use the "query_builder_assistant" prompt for interactive guidance.
"""

    @staticmethod
    def missing_required_param(param_name: str, tool_name: str, example_value: Optional[str] = None) -> str:
        """Generate helpful error message for missing required parameters"""

        example_text = ""
        if example_value:
            example_text = f"\n\n**Example value:** {example_value}"

        tool_hints = {
            "get_space_info": "Tip: Use list_spaces() first to see available space IDs",
            "get_table_schema": "Tip: Use search_tables() to find the table name if unsure",
            "execute_query": "Tip: Use get_table_schema() to see correct column names before querying",
            "search_tables": "Tip: Use domain keywords like 'customer', 'sales', 'order', etc."
        }

        hint = tool_hints.get(tool_name, "")
        hint_text = f"\n\n**{hint}**" if hint else ""

        return f""">>> Missing Required Parameter <<<

The tool '{tool_name}' requires parameter '{param_name}' but it was not provided.

**Required parameter:** {param_name}{example_text}

**How to fix:**
1. Check the tool's parameter requirements
2. Provide the {param_name} parameter
3. Ensure the value is in the correct format{hint_text}

**Example usage:**
Check the tool description for example queries and parameter formats.
"""

    @staticmethod
    def validation_failed(errors: List[str], tool_name: str) -> str:
        """Generate helpful error message for validation failures"""

        error_list = "\n".join(f"  {i+1}. {error}" for i, error in enumerate(errors))

        format_hints = {
            "space_id": "Space IDs must be UPPERCASE (e.g., 'SALES_ANALYTICS', 'FINANCE_DWH')",
            "table_name": "Table names must be valid identifiers (e.g., 'CUSTOMER_DATA', 'SALES_ORDERS')",
            "sql_query": "Queries must start with SELECT and contain no comments or dangerous keywords",
            "limit": "Limit must be a positive integer between 1 and 1000"
        }

        hints = []
        for error in errors:
            for param, hint in format_hints.items():
                if param in error.lower():
                    hints.append(f"**{param.upper()}:** {hint}")

        hint_text = ""
        if hints:
            hint_text = "\n\n**Format requirements:**\n" + "\n".join(set(hints))

        return f""">>> Parameter Validation Failed <<<

The parameters for tool '{tool_name}' failed validation:

{error_list}
{hint_text}

**Common fixes:**
- Ensure proper capitalization (space IDs and table names are usually UPPERCASE)
- Remove special characters from identifiers
- Check parameter types (string vs integer vs boolean)
- Verify SQL query syntax and security rules

**Need examples?**
Check the tool's description for example parameter values and formats.
"""

    @staticmethod
    def connection_error(connection_type: Optional[str] = None) -> str:
        """Generate helpful error message for connection issues"""

        filter_text = f" of type '{connection_type}'" if connection_type else ""

        return f""">>> Connection Error <<<

Unable to retrieve data source connections{filter_text}.

**Possible causes:**
- Connection service temporarily unavailable
- Network connectivity issues
- Authentication token expired

**Next steps:**
1. Wait a moment and try again
2. Check if other operations work: list_spaces()
3. Try without filtering: list_connections() (no parameters)
4. If problem persists, check system status

**Valid connection types:**
- SAP_ERP, SAP_S4HANA, SAP_BW
- SALESFORCE, EXTERNAL
- SNOWFLAKE, DATABRICKS
- POSTGRESQL, MYSQL, ORACLE, SQLSERVER, HANA

**For pipeline monitoring:**
Use get_task_status() to check data integration health.
"""

    @staticmethod
    def consent_required(tool_name: str) -> str:
        """Generate helpful message when user consent is required"""

        return f""">>> User Consent Required <<<

The tool '{tool_name}' requires explicit user consent before execution.

**Why consent is needed:**
- This is a high-risk operation (can query sensitive data)
- Consent ensures user is aware of the action
- Required for security and compliance

**What happens next:**
1. User will see a consent prompt
2. User must approve or deny the operation
3. If approved, the tool executes normally
4. Consent is valid for the current session (60 minutes)

**Affected tools:**
- execute_query: Can retrieve actual data
- list_connections: Shows connection details

**Alternative approaches:**
- Use read-only metadata tools (list_spaces, search_tables, get_table_schema)
- These don't require consent and can help explore data structure
"""

    @staticmethod
    def authorization_denied(tool_name: str, reason: str) -> str:
        """Generate helpful message when authorization is denied"""

        return f""">>> Authorization Error <<<

Access to tool '{tool_name}' was denied.

**Reason:** {reason}

**What this means:**
- You don't have permission to use this tool
- Or: User consent is required but not yet granted

**Next steps:**
1. If consent is required, wait for user approval
2. If permission denied, contact your administrator
3. Use alternative tools that don't require special permissions

**Low-risk alternatives:**
- list_spaces() - List available spaces (no consent needed)
- search_tables() - Find tables by keyword (no consent needed)
- get_table_schema() - View table structure (no consent needed)
- get_space_info() - Explore space contents (no consent needed)
"""

    @staticmethod
    def general_error(tool_name: str, error_message: str) -> str:
        """Generate helpful message for unexpected errors"""

        return f""">>> Unexpected Error <<<

An error occurred while executing '{tool_name}':
{error_message}

**Troubleshooting steps:**

1. **Verify your inputs:**
   - Check parameter names and types
   - Ensure values are in correct format
   - Review tool description for examples

2. **Try simpler operations:**
   - Start with list_spaces() to verify connectivity
   - Test with known-good parameters
   - Break complex operations into smaller steps

3. **Check system status:**
   - Try other tools to see if they work
   - Wait a moment and retry
   - Check if mock data mode is enabled

**Getting help:**
- Review the tool's description for usage guidance
- Use prompts like "explore_datasphere" for guided workflows
- Check parameter validation requirements

If the error persists, there may be a system issue.
"""
