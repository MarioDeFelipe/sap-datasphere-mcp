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

# Mock database users for each space
MOCK_DATABASE_USERS = {
    "SALES_ANALYTICS": [
        {
            "user_id": "ANALYST",
            "full_name": "SALES_ANALYTICS#ANALYST",
            "status": "ACTIVE",
            "created_date": "2024-01-20T11:00:00Z",
            "last_login": "2024-12-01T14:23:15Z",
            "permissions": {
                "consumption": {
                    "consumptionWithGrant": False,
                    "spaceSchemaAccess": True,
                    "scriptServerAccess": False,
                    "enablePasswordPolicy": True,
                    "localSchemaAccess": False,
                    "hdiGrantorForCupsAccess": False
                },
                "ingestion": {
                    "auditing": {
                        "dppRead": {
                            "isAuditPolicyActive": True,
                            "retentionPeriod": 30
                        },
                        "dppChange": {
                            "isAuditPolicyActive": False,
                            "retentionPeriod": 7
                        }
                    }
                }
            },
            "description": "Read-only analyst user with space schema access"
        },
        {
            "user_id": "ETL_USER",
            "full_name": "SALES_ANALYTICS#ETL_USER",
            "status": "ACTIVE",
            "created_date": "2024-01-22T09:30:00Z",
            "last_login": "2024-12-03T02:15:00Z",
            "permissions": {
                "consumption": {
                    "consumptionWithGrant": False,
                    "spaceSchemaAccess": True,
                    "scriptServerAccess": True,
                    "enablePasswordPolicy": True,
                    "localSchemaAccess": True,
                    "hdiGrantorForCupsAccess": False
                },
                "ingestion": {
                    "auditing": {
                        "dppRead": {
                            "isAuditPolicyActive": True,
                            "retentionPeriod": 90
                        },
                        "dppChange": {
                            "isAuditPolicyActive": True,
                            "retentionPeriod": 90
                        }
                    }
                }
            },
            "description": "ETL user for data loading and transformation"
        }
    ],
    "FINANCE_DWH": [
        {
            "user_id": "REPORTING",
            "full_name": "FINANCE_DWH#REPORTING",
            "status": "ACTIVE",
            "created_date": "2024-02-05T10:00:00Z",
            "last_login": "2024-12-02T08:45:30Z",
            "permissions": {
                "consumption": {
                    "consumptionWithGrant": True,
                    "spaceSchemaAccess": True,
                    "scriptServerAccess": False,
                    "enablePasswordPolicy": True,
                    "localSchemaAccess": False,
                    "hdiGrantorForCupsAccess": False
                },
                "ingestion": {
                    "auditing": {
                        "dppRead": {
                            "isAuditPolicyActive": True,
                            "retentionPeriod": 365
                        },
                        "dppChange": {
                            "isAuditPolicyActive": True,
                            "retentionPeriod": 365
                        }
                    }
                }
            },
            "description": "Finance reporting user with grant privileges"
        },
        {
            "user_id": "POWERBI_SERVICE",
            "full_name": "FINANCE_DWH#POWERBI_SERVICE",
            "status": "ACTIVE",
            "created_date": "2024-02-10T14:20:00Z",
            "last_login": "2024-12-03T06:00:12Z",
            "permissions": {
                "consumption": {
                    "consumptionWithGrant": False,
                    "spaceSchemaAccess": True,
                    "scriptServerAccess": False,
                    "enablePasswordPolicy": True,
                    "localSchemaAccess": False,
                    "hdiGrantorForCupsAccess": False
                },
                "ingestion": {
                    "auditing": {
                        "dppRead": {
                            "isAuditPolicyActive": True,
                            "retentionPeriod": 30
                        },
                        "dppChange": {
                            "isAuditPolicyActive": False,
                            "retentionPeriod": 7
                        }
                    }
                }
            },
            "description": "Power BI service account for dashboard integration"
        }
    ],
    "HR_ANALYTICS": [
        {
            "user_id": "HR_VIEWER",
            "full_name": "HR_ANALYTICS#HR_VIEWER",
            "status": "ACTIVE",
            "created_date": "2024-03-15T11:30:00Z",
            "last_login": "2024-11-28T16:20:00Z",
            "permissions": {
                "consumption": {
                    "consumptionWithGrant": False,
                    "spaceSchemaAccess": True,
                    "scriptServerAccess": False,
                    "enablePasswordPolicy": True,
                    "localSchemaAccess": False,
                    "hdiGrantorForCupsAccess": False
                },
                "ingestion": {
                    "auditing": {
                        "dppRead": {
                            "isAuditPolicyActive": True,
                            "retentionPeriod": 180
                        },
                        "dppChange": {
                            "isAuditPolicyActive": True,
                            "retentionPeriod": 180
                        }
                    }
                }
            },
            "description": "HR analytics viewer with PII audit logging"
        }
    ]
}

# Consolidated mock data structure for easy access
MOCK_DATA = {
    "spaces": MOCK_SPACES,
    "tables": MOCK_TABLES,
    "connections": MOCK_CONNECTIONS,
    "tasks": MOCK_TASKS,
    "marketplace_packages": MOCK_MARKETPLACE_PACKAGES,
    "database_users": MOCK_DATABASE_USERS
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


def get_mock_database_users(space_id=None):
    """
    Get mock database users data

    Args:
        space_id: Optional space ID to filter users

    Returns:
        List of database users or dict of all users by space
    """
    if space_id:
        return MOCK_DATABASE_USERS.get(space_id, [])
    return MOCK_DATABASE_USERS


# Mock catalog assets data
MOCK_CATALOG_ASSETS = [
    {
        "id": "SAP_SC_FI_AM_FINTRANSACTIONS",
        "name": "Financial Transactions",
        "description": "Comprehensive financial transaction data with account information, transaction types, amounts, and currencies",
        "spaceId": "SAP_CONTENT",
        "spaceName": "SAP Content",
        "assetType": "AnalyticalModel",
        "exposedForConsumption": True,
        "analyticalConsumptionUrl": "/api/v1/datasphere/consumption/analytical/SAP_CONTENT/SAP_SC_FI_AM_FINTRANSACTIONS",
        "relationalConsumptionUrl": "/api/v1/datasphere/consumption/relational/SAP_CONTENT/SAP_SC_FI_AM_FINTRANSACTIONS",
        "metadataUrl": "/api/v1/datasphere/consumption/analytical/SAP_CONTENT/SAP_SC_FI_AM_FINTRANSACTIONS/$metadata",
        "createdAt": "2024-01-15T10:30:00Z",
        "modifiedAt": "2024-11-20T14:22:00Z",
        "tags": ["finance", "transactions", "analytical", "compliance"],
        "businessPurpose": "Financial reporting, transaction analysis, audit trails, regulatory compliance",
        "status": "Active",
        "version": "2.1"
    },
    {
        "id": "SALES_DATA_VIEW",
        "name": "Sales Data View",
        "description": "Sales transaction view with customer details and order information",
        "spaceId": "SALES_ANALYTICS",
        "spaceName": "Sales Analytics",
        "assetType": "View",
        "exposedForConsumption": True,
        "analyticalConsumptionUrl": None,
        "relationalConsumptionUrl": "/api/v1/datasphere/consumption/relational/SALES_ANALYTICS/SALES_DATA_VIEW",
        "metadataUrl": "/api/v1/datasphere/consumption/relational/SALES_ANALYTICS/SALES_DATA_VIEW/$metadata",
        "createdAt": "2024-03-10T08:15:00Z",
        "modifiedAt": "2024-10-05T16:45:00Z",
        "tags": ["sales", "customer", "relational"],
        "businessPurpose": "Sales analysis and customer insights",
        "status": "Active",
        "version": "1.5"
    },
    {
        "id": "COST_CENTER_VIEW",
        "name": "Cost Center View",
        "description": "Cost center master data with hierarchies and organizational structure",
        "spaceId": "SAP_CONTENT",
        "spaceName": "SAP Content",
        "assetType": "View",
        "exposedForConsumption": True,
        "analyticalConsumptionUrl": None,
        "relationalConsumptionUrl": "/api/v1/datasphere/consumption/relational/SAP_CONTENT/COST_CENTER_VIEW",
        "metadataUrl": "/api/v1/datasphere/consumption/relational/SAP_CONTENT/COST_CENTER_VIEW/$metadata",
        "createdAt": "2024-02-20T09:15:00Z",
        "modifiedAt": "2024-09-10T11:30:00Z",
        "tags": ["finance", "cost-center", "master-data"],
        "businessPurpose": "Cost allocation and organizational reporting",
        "status": "Active",
        "version": "1.2"
    },
    {
        "id": "CUSTOMER_MASTER",
        "name": "Customer Master Data",
        "description": "Customer master data with addresses, contact information, and credit details",
        "spaceId": "SALES_ANALYTICS",
        "spaceName": "Sales Analytics",
        "assetType": "Table",
        "exposedForConsumption": True,
        "analyticalConsumptionUrl": None,
        "relationalConsumptionUrl": "/api/v1/datasphere/consumption/relational/SALES_ANALYTICS/CUSTOMER_MASTER",
        "metadataUrl": "/api/v1/datasphere/consumption/relational/SALES_ANALYTICS/CUSTOMER_MASTER/$metadata",
        "createdAt": "2024-01-05T12:00:00Z",
        "modifiedAt": "2024-12-01T09:30:00Z",
        "tags": ["sales", "customer", "master-data"],
        "businessPurpose": "Customer relationship management and sales operations",
        "status": "Active",
        "version": "3.0"
    },
    {
        "id": "PRODUCT_CATALOG",
        "name": "Product Catalog",
        "description": "Complete product catalog with specifications, pricing, and availability",
        "spaceId": "SAP_CONTENT",
        "spaceName": "SAP Content",
        "assetType": "Table",
        "exposedForConsumption": True,
        "analyticalConsumptionUrl": None,
        "relationalConsumptionUrl": "/api/v1/datasphere/consumption/relational/SAP_CONTENT/PRODUCT_CATALOG",
        "metadataUrl": "/api/v1/datasphere/consumption/relational/SAP_CONTENT/PRODUCT_CATALOG/$metadata",
        "createdAt": "2024-01-10T14:00:00Z",
        "modifiedAt": "2024-11-15T10:20:00Z",
        "tags": ["product", "catalog", "master-data"],
        "businessPurpose": "Product information management and pricing",
        "status": "Active",
        "version": "2.3"
    },
    {
        "id": "SALES_ORDERS_FACT",
        "name": "Sales Orders Fact",
        "description": "Sales orders fact table with order details, quantities, and revenues",
        "spaceId": "SALES_ANALYTICS",
        "spaceName": "Sales Analytics",
        "assetType": "AnalyticalModel",
        "exposedForConsumption": True,
        "analyticalConsumptionUrl": "/api/v1/datasphere/consumption/analytical/SALES_ANALYTICS/SALES_ORDERS_FACT",
        "relationalConsumptionUrl": "/api/v1/datasphere/consumption/relational/SALES_ANALYTICS/SALES_ORDERS_FACT",
        "metadataUrl": "/api/v1/datasphere/consumption/analytical/SALES_ANALYTICS/SALES_ORDERS_FACT/$metadata",
        "createdAt": "2024-02-01T11:00:00Z",
        "modifiedAt": "2024-12-03T15:30:00Z",
        "tags": ["sales", "orders", "fact", "analytical"],
        "businessPurpose": "Sales performance analysis and forecasting",
        "status": "Active",
        "version": "1.8"
    }
]


def get_mock_catalog_assets(space_id=None, asset_type=None):
    """
    Get mock catalog assets data with optional filtering

    Args:
        space_id: Optional space ID to filter assets
        asset_type: Optional asset type to filter (e.g., 'AnalyticalModel', 'View', 'Table')

    Returns:
        List of catalog assets matching the filters
    """
    assets = MOCK_CATALOG_ASSETS

    if space_id:
        assets = [a for a in assets if a["spaceId"] == space_id]

    if asset_type:
        assets = [a for a in assets if a["assetType"] == asset_type]

    return assets


def get_mock_asset_details(space_id, asset_id):
    """
    Get detailed mock data for a specific asset

    Args:
        space_id: The space ID
        asset_id: The asset ID

    Returns:
        Asset details dict or None if not found
    """
    for asset in MOCK_CATALOG_ASSETS:
        if asset["spaceId"] == space_id and asset["id"] == asset_id:
            # Return asset with additional detailed fields
            detailed_asset = asset.copy()
            detailed_asset.update({
                "technicalName": asset_id,
                "owner": "SYSTEM",
                "createdBy": "SYSTEM",
                "modifiedBy": "ADMIN",
                "businessContext": {
                    "domain": "Finance" if "SAP_SC_FI" in asset_id else "Sales",
                    "dataClassification": "Confidential",
                    "retentionPeriod": "7 years"
                },
                "technicalDetails": {
                    "rowCount": 15000000 if "FINTRANSACTIONS" in asset_id else 500000,
                    "sizeInMB": 2500 if "FINTRANSACTIONS" in asset_id else 150,
                    "lastRefreshed": "2024-12-04T02:00:00Z",
                    "refreshFrequency": "Daily"
                }
            })

            if asset["assetType"] == "AnalyticalModel":
                detailed_asset.update({
                    "dimensions": [
                        {
                            "name": "TimeDimension",
                            "description": "Time hierarchy with year, quarter, month, day",
                            "cardinality": 3650
                        },
                        {
                            "name": "AccountDimension",
                            "description": "Chart of accounts dimension",
                            "cardinality": 5000
                        }
                    ],
                    "measures": [
                        {
                            "name": "Amount",
                            "description": "Transaction amount in local currency",
                            "aggregation": "SUM",
                            "dataType": "Decimal(15,2)"
                        }
                    ]
                })

            return detailed_asset

    return None
