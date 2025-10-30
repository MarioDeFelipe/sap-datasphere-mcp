"""
Mock Data Module for SAP Datasphere MCP Server

Provides sample data for development and testing when real OAuth authentication
is not available. This data simulates a typical Datasphere environment with
spaces, tables, connections, and tasks.
"""

# Mock data for development and testing
MOCK_SPACES = [
    {
        "id": "SALES_ANALYTICS",
        "name": "Sales Analytics",
        "description": "Sales data analysis and reporting space",
        "status": "ACTIVE",
        "created_date": "2024-01-15T10:30:00Z",
        "owner": "sales.admin@company.com",
        "tables_count": 15,
        "views_count": 8,
        "connections_count": 3
    },
    {
        "id": "FINANCE_DWH",
        "name": "Finance Data Warehouse",
        "description": "Financial data warehouse and reporting",
        "status": "ACTIVE",
        "created_date": "2024-02-01T14:20:00Z",
        "owner": "finance.admin@company.com",
        "tables_count": 25,
        "views_count": 12,
        "connections_count": 5
    },
    {
        "id": "HR_ANALYTICS",
        "name": "HR Analytics",
        "description": "Human resources analytics and insights",
        "status": "DEVELOPMENT",
        "created_date": "2024-03-10T09:15:00Z",
        "owner": "hr.admin@company.com",
        "tables_count": 8,
        "views_count": 4,
        "connections_count": 2
    }
]

MOCK_TABLES = {
    "SALES_ANALYTICS": [
        {
            "name": "CUSTOMER_DATA",
            "type": "TABLE",
            "description": "Customer master data with demographics",
            "columns": [
                {"name": "CUSTOMER_ID", "type": "NVARCHAR(10)", "key": True},
                {"name": "CUSTOMER_NAME", "type": "NVARCHAR(100)"},
                {"name": "COUNTRY", "type": "NVARCHAR(50)"},
                {"name": "REGION", "type": "NVARCHAR(50)"},
                {"name": "REGISTRATION_DATE", "type": "DATE"}
            ],
            "row_count": 15420,
            "last_updated": "2024-10-02T18:30:00Z"
        },
        {
            "name": "SALES_ORDERS",
            "type": "TABLE",
            "description": "Sales order transactions",
            "columns": [
                {"name": "ORDER_ID", "type": "NVARCHAR(10)", "key": True},
                {"name": "CUSTOMER_ID", "type": "NVARCHAR(10)"},
                {"name": "ORDER_DATE", "type": "DATE"},
                {"name": "AMOUNT", "type": "DECIMAL(15,2)"},
                {"name": "STATUS", "type": "NVARCHAR(20)"}
            ],
            "row_count": 89650,
            "last_updated": "2024-10-03T08:15:00Z"
        }
    ],
    "FINANCE_DWH": [
        {
            "name": "GL_ACCOUNTS",
            "type": "TABLE",
            "description": "General ledger account master data",
            "columns": [
                {"name": "ACCOUNT_ID", "type": "NVARCHAR(10)", "key": True},
                {"name": "ACCOUNT_NAME", "type": "NVARCHAR(100)"},
                {"name": "ACCOUNT_TYPE", "type": "NVARCHAR(50)"},
                {"name": "BALANCE", "type": "DECIMAL(15,2)"}
            ],
            "row_count": 2340,
            "last_updated": "2024-10-01T23:45:00Z"
        }
    ]
}

MOCK_CONNECTIONS = [
    {
        "id": "SAP_ERP_PROD",
        "name": "SAP ERP Production",
        "type": "SAP_ERP",
        "description": "Connection to production SAP ERP system",
        "status": "CONNECTED",
        "host": "erp-prod.company.com",
        "last_tested": "2024-10-03T06:00:00Z"
    },
    {
        "id": "SALESFORCE_API",
        "name": "Salesforce CRM",
        "type": "SALESFORCE",
        "description": "Salesforce CRM data connection",
        "status": "CONNECTED",
        "host": "company.salesforce.com",
        "last_tested": "2024-10-03T07:30:00Z"
    },
    {
        "id": "EXTERNAL_DATALAKE",
        "name": "External Data Lake",
        "type": "EXTERNAL",
        "description": "External data lake storage",
        "status": "CONNECTED",
        "host": "https://external-datalake.company.com/",
        "last_tested": "2024-10-03T05:15:00Z"
    }
]

MOCK_TASKS = [
    {
        "id": "DAILY_SALES_ETL",
        "name": "Daily Sales ETL",
        "description": "Daily extraction and loading of sales data",
        "status": "COMPLETED",
        "space": "SALES_ANALYTICS",
        "last_run": "2024-10-03T02:00:00Z",
        "next_run": "2024-10-04T02:00:00Z",
        "duration": "00:15:32",
        "records_processed": 1250
    },
    {
        "id": "FINANCE_RECONCILIATION",
        "name": "Finance Reconciliation",
        "description": "Monthly finance data reconciliation",
        "status": "RUNNING",
        "space": "FINANCE_DWH",
        "last_run": "2024-10-03T10:00:00Z",
        "next_run": "2024-11-01T10:00:00Z",
        "duration": "01:45:00",
        "records_processed": 45000
    }
]

MOCK_MARKETPLACE_PACKAGES = [
    {
        "id": "INDUSTRY_BENCHMARKS",
        "name": "Industry Benchmarks",
        "description": "Industry benchmark data for comparative analysis",
        "category": "Reference Data",
        "provider": "SAP",
        "version": "2024.Q3",
        "size": "2.5 GB",
        "price": "Free"
    },
    {
        "id": "CURRENCY_RATES",
        "name": "Daily Currency Rates",
        "description": "Real-time currency exchange rates",
        "category": "Financial Data",
        "provider": "Financial Data Corp",
        "version": "Live",
        "size": "50 MB",
        "price": "$99/month"
    }
]

# Consolidated mock data structure for easy access
MOCK_DATA = {
    "spaces": MOCK_SPACES,
    "tables": MOCK_TABLES,
    "connections": MOCK_CONNECTIONS,
    "tasks": MOCK_TASKS,
    "marketplace_packages": MOCK_MARKETPLACE_PACKAGES
}


def get_all_mock_data():
    """Get complete mock data structure"""
    return MOCK_DATA


def get_mock_spaces():
    """Get mock spaces data"""
    return MOCK_SPACES


def get_mock_tables(space_id=None):
    """Get mock tables data, optionally filtered by space"""
    if space_id:
        return MOCK_TABLES.get(space_id, [])
    return MOCK_TABLES


def get_mock_connections():
    """Get mock connections data"""
    return MOCK_CONNECTIONS


def get_mock_tasks():
    """Get mock tasks data"""
    return MOCK_TASKS


def get_mock_marketplace():
    """Get mock marketplace packages data"""
    return MOCK_MARKETPLACE_PACKAGES
