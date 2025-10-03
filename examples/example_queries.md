# Example Queries for SAP Datasphere MCP Server

This document provides example queries you can use with AI assistants connected to the SAP Datasphere MCP Server.

## 🏢 Space Management

### List All Spaces
```
List all Datasphere spaces
```
**Expected Result**: Shows all available spaces with basic information

### Get Space Details
```
Show me details about the Sales Analytics space
```
**Expected Result**: Detailed information including tables, views, and metadata

### Space Status Check
```
What's the status of all Datasphere spaces?
```
**Expected Result**: Status information for each space

## 🔍 Data Discovery

### Search for Tables
```
Search for tables containing "customer" data
```
**Expected Result**: List of tables matching the search term

### Find Sales Data
```
Find all tables related to sales or orders
```
**Expected Result**: Sales-related tables across all spaces

### Schema Information
```
Show me the schema for the CUSTOMER_DATA table in Sales Analytics
```
**Expected Result**: Detailed table schema with columns and types

## 🔗 Connection Management

### List Connections
```
List all data connections
```
**Expected Result**: All available data source connections

### Connection Status
```
What's the status of our SAP ERP connection?
```
**Expected Result**: Connection health and status information

### Filter by Type
```
Show me all Salesforce connections
```
**Expected Result**: Connections filtered by type

## 📊 Data Querying

### Simple Query
```
Execute: SELECT * FROM CUSTOMER_DATA LIMIT 10
```
**Expected Result**: Simulated query results with sample data

### Complex Query
```
Run this query in Sales Analytics: SELECT COUNTRY, COUNT(*) FROM CUSTOMER_DATA GROUP BY COUNTRY
```
**Expected Result**: Aggregated query results

### Query with Analysis
```
Query the sales orders table and show me the top customers by order value
```
**Expected Result**: Analytical query results

## 🛒 Marketplace Operations

### Browse Packages
```
What data packages are available in the marketplace?
```
**Expected Result**: List of available data packages

### Search Marketplace
```
Find financial data packages in the marketplace
```
**Expected Result**: Financial data packages with details

## 🔄 Combined Operations

### Space Analysis
```
Analyze the Sales Analytics space - show me all tables, their schemas, and row counts
```
**Expected Result**: Comprehensive space analysis

### Data Discovery Workflow
```
I'm looking for customer data. Show me:
1. Which spaces contain customer information
2. What tables are available
3. The schema of the main customer table
```
**Expected Result**: Step-by-step data discovery

### Connection and Data Check
```
Check our data connections and show me what customer data we can access
```
**Expected Result**: Connection status plus available customer data

## 💡 Advanced Use Cases

### Data Lineage Exploration
```
Show me all tables in Sales Analytics and how they might be related
```
**Expected Result**: Table relationships and potential joins

### Performance Analysis
```
Which tables have the most data and might need performance optimization?
```
**Expected Result**: Tables sorted by size with recommendations

### Integration Planning
```
I want to integrate Salesforce data. Show me:
1. Current Salesforce connections
2. Available customer tables
3. Potential integration points
```
**Expected Result**: Integration analysis and recommendations

## 🎯 Tips for Better Results

### Be Specific
- Mention space names when relevant
- Use exact table names when known
- Specify the type of information you need

### Use Natural Language
- Ask questions as you would to a colleague
- The MCP server understands context and intent
- Follow up with clarifying questions

### Combine Operations
- Ask for multiple related pieces of information
- Request analysis and recommendations
- Build on previous queries

### Error Handling
- If a query fails, try rephrasing
- Check space and table names for typos
- Ask for available options if unsure

## 🔧 Troubleshooting Queries

### Check Server Status
```
Is the Datasphere MCP server working correctly?
```

### Validate Mock Data
```
Show me what mock data is available for testing
```

### Configuration Check
```
What Datasphere capabilities are available through this MCP server?
```

These examples demonstrate the full range of capabilities available through the SAP Datasphere MCP Server. Start with simple queries and gradually explore more complex operations as you become familiar with the system.