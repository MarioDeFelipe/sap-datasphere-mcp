# SAP Datasphere MCP Server - Query Examples

This guide shows you what data you can query and the best methods to use.

## Available Query Methods

### 1. Relational Queries (Row-level data access)
**Best for:** ETL, data extraction, detailed records
**Tool:** `query_relational_entity`

### 2. Analytical Queries (BI/Aggregated data)
**Best for:** Business intelligence, reporting, dashboards
**Tool:** `query_analytical_data`

### 3. SQL Queries (Limited support)
**Best for:** SQL-familiar users (has API limitations)
**Tool:** `execute_query`
**⚠️ Recommendation:** Use `query_relational_entity` or `query_analytical_data` instead for reliable results.

## Recent Improvements (v1.0.3+)
- Fixed execute_query scoping issues
- Removed consent prompts for smoother queries
- Added 2 new data discovery tools (find_assets_by_column, analyze_column_distribution)

## Working Data Assets (37 total)

### 📊 **Sales Data**
- **SAP_SC_SALES_V_SalesOrders** (Relational) - Detailed sales orders
- **SAP_SC_SALES_AM_SalesOrders** (Analytical) - Sales analytics
- **SAP_SC_SALES_V_Fact_Sales** (Both) - Sales fact table

### 🛍️ **Product Data**
- **SAP_SC_FI_V_ProductsDim** (Relational) - Product catalog
- **SAP_SC_FI_SQL_ProductHierarchy** (Relational) - Product hierarchy
- **SAP_SC_FI_SQL_ProductTexts** (Relational) - Product descriptions

### 👥 **HR Data**
- **SAP_SC_HR_AM_EmpHeadcount** (Analytical) - Headcount analytics
- **SAP_SC_HR_V_EmpHeadcount** (Relational) - Employee details
- **SAP_SC_HR_V_Job** (Relational) - Job classifications
- **SAP_SC_HR_V_Location** (Relational) - Location dimensions

### 💰 **Financial Data**
- **SAP_SC_FI_AM_FINTRANSACTIONS** (Analytical) - Financial analytics
- **SAP_SC_FI_SQL_FinTransactions** (Relational) - Transaction details
- **SAP_SC_FI_V_GLAccTexts** (Relational) - GL account information

### 📅 **Time Dimensions**
- **SAP.TIME.VIEW_DIMENSION_DAY** (Relational) - Daily calendar
- **SAP.TIME.VIEW_DIMENSION_MONTH** (Relational) - Monthly calendar
- **SAP.TIME.VIEW_DIMENSION_QUARTER** (Relational) - Quarterly calendar
- **SAP.TIME.VIEW_DIMENSION_YEAR** (Relational) - Yearly calendar

## Example Queries

### Example 1: Sales Data (Relational)
```python
# Get detailed sales orders
query_relational_entity(
    space_id="SAP_CONTENT",
    asset_id="SAP_SC_SALES_V_SalesOrders",
    entity_name="SAP_SC_SALES_V_SalesOrders",
    select="SALESORDERID,COMPANYNAME,GROSSAMOUNT,CURRENCY,DELIVERYDATE,PRODUCTID",
    top=5
)
```
**Results:** All For Bikes orders ($5,592-$41,247), CM-FL-V00 Forklifts, delivery dates 2026-2036

### Example 2: Product Information (Relational)
```python
# Get product catalog with pricing
query_relational_entity(
    space_id="SAP_CONTENT",
    asset_id="SAP_SC_FI_V_ProductsDim",
    entity_name="SAP_SC_FI_V_ProductsDim",
    select="PRODUCTID,MEDIUM_DESCR,PRICE,CURRENCY,WEIGHTMEASURE,PRODUCTCATEGORYID",
    top=5
)
```
**Results:** Forklift ($7,900), Bikes ($288-$699), weights 11,000-22,000 KG

### Example 3: Sales Analytics by Company (Analytical)
```python
# Analyze top companies by revenue
query_analytical_data(
    space_id="SAP_CONTENT",
    asset_id="SAP_SC_SALES_AM_SalesOrders",
    entity_set="SAP_SC_SALES_AM_SalesOrders",
    select="COMPANYNAME,GROSSAMOUNT,CURRENCY",
    orderby="GROSSAMOUNT desc",
    top=8
)
```
**Results:** eBike 100 ($36.1M), Arena Sports ($34.4M), Khan Cycles ($34.3M)

### Example 4: Time Dimension Data (Relational)
```python
# Get calendar data for specific years
query_relational_entity(
    space_id="SAP_CONTENT",
    asset_id="SAP.TIME.VIEW_DIMENSION_DAY",
    entity_name="SAP_TIME_VIEW_DIMENSION_DAY",
    filter="YEAR eq '2024'",
    top=10
)
```

### Example 5: SQL Query (Limited - Use with caution)
```python
# SQL-style query (has API limitations)
execute_query(
    space_id="SAP_CONTENT",
    sql_query="SELECT PRODUCTID, MEDIUM_DESCR, PRICE FROM SAP_SC_FI_V_ProductsDim WHERE PRICE > 1000 LIMIT 5"
)
```
**Note:** SQL queries work for parsing but may hit API path limitations. Use relational/analytical methods for reliable results.

## Query Performance
- **Relational queries:** 1-5 seconds for detailed data
- **Analytical queries:** Fast aggregation and sorting
- **Batch processing:** Up to 50,000 records per batch
- **Real-time:** Live data from SAP Datasphere tenant

## Best Practices

1. **Use relational queries** for detailed, row-level data extraction
2. **Use analytical queries** for business intelligence and aggregations
3. **Check available entities** with `list_relational_entities` first
4. **Get schema information** with `get_relational_entity_metadata`
5. **Use pagination** with skip parameter for large datasets
6. **Filter data** with OData $filter expressions for better performance

## Data Discovery Tools

### Find Assets by Column
```python
# Find all assets containing a specific column
find_assets_by_column(
    space_id="SAP_CONTENT",
    column_name="PRODUCTID"
)
```
**Use case:** Data lineage, impact analysis, column tracking

### Analyze Column Distribution
```python
# Statistical analysis of column data
analyze_column_distribution(
    space_id="SAP_CONTENT",
    asset_id="SAP_SC_FI_V_ProductsDim",
    entity_name="SAP_SC_FI_V_ProductsDim",
    column_name="PRICE"
)
```
**Use case:** Data quality profiling, outlier detection, distribution analysis
