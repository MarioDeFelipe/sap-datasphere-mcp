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

# Mock task chains for run_task_chain, get_task_log, get_task_history (v1.0.12)
MOCK_TASK_CHAINS = {
    "SALES_ANALYTICS": [
        {
            "object_id": "Daily_Sales_ETL",
            "name": "Daily Sales ETL Pipeline",
            "description": "Extracts, transforms, and loads daily sales data",
            "application_id": "TASK_CHAINS",
            "activity": "RUN_CHAIN",
            "status": "ACTIVE",
            "schedule": "Daily at 02:00 UTC",
            "last_run_log_id": 2295172
        },
        {
            "object_id": "Customer_Sync",
            "name": "Customer Master Sync",
            "description": "Synchronizes customer master data from SAP ERP",
            "application_id": "TASK_CHAINS",
            "activity": "RUN_CHAIN",
            "status": "ACTIVE",
            "schedule": "Every 4 hours",
            "last_run_log_id": 2295180
        }
    ],
    "FINANCE_DWH": [
        {
            "object_id": "Monthly_Reconciliation",
            "name": "Monthly Finance Reconciliation",
            "description": "Reconciles GL accounts with source systems",
            "application_id": "TASK_CHAINS",
            "activity": "RUN_CHAIN",
            "status": "ACTIVE",
            "schedule": "1st of month at 06:00 UTC",
            "last_run_log_id": 2326060
        },
        {
            "object_id": "Daily_GL_Load",
            "name": "Daily GL Data Load",
            "description": "Loads daily general ledger transactions",
            "application_id": "TASK_CHAINS",
            "activity": "RUN_CHAIN",
            "status": "ACTIVE",
            "schedule": "Daily at 03:00 UTC",
            "last_run_log_id": 2329400
        }
    ]
}

# Mock task log details for get_task_log
MOCK_TASK_LOGS = {
    2295172: {
        "logId": 2295172,
        "status": "COMPLETED",
        "startTime": "2025-01-15T02:30:33.142Z",
        "endTime": "2025-01-15T02:31:36.059Z",
        "runTime": 62917,
        "objectId": "Daily_Sales_ETL",
        "applicationId": "TASK_CHAINS",
        "activity": "RUN_CHAIN",
        "spaceId": "SALES_ANALYTICS",
        "user": "etl_service_user",
        "children": [
            {
                "nodeId": 1,
                "logId": 2295190,
                "status": "COMPLETED",
                "objectId": "Sales_Orders_View",
                "activity": "PERSIST",
                "applicationId": "VIEWS",
                "startTime": "2025-01-15T02:30:59.210Z",
                "endTime": "2025-01-15T02:31:13.082Z",
                "runTime": 13872
            },
            {
                "nodeId": 2,
                "logId": 2295191,
                "status": "COMPLETED",
                "objectId": "Customer_Dimension",
                "activity": "PERSIST",
                "applicationId": "VIEWS",
                "startTime": "2025-01-15T02:31:14.000Z",
                "endTime": "2025-01-15T02:31:35.000Z",
                "runTime": 21000
            }
        ],
        "messages": [
            {
                "messageNumber": 1,
                "severity": "INFO",
                "text": "Task 2295172 started.",
                "timestamp": "2025-01-15T02:30:33.145Z"
            },
            {
                "messageNumber": 2,
                "severity": "INFO",
                "text": "Loading task chain and prepared 2 tasks that are part of this chain.",
                "timestamp": "2025-01-15T02:30:33.597Z"
            },
            {
                "messageNumber": 3,
                "severity": "INFO",
                "text": "Node 1 with task VIEWS/PERSIST/SALES_ANALYTICS/Sales_Orders_View is going to be started.",
                "timestamp": "2025-01-15T02:30:43.599Z"
            },
            {
                "messageNumber": 4,
                "severity": "INFO",
                "text": "Node 2 with task VIEWS/PERSIST/SALES_ANALYTICS/Customer_Dimension is going to be started.",
                "timestamp": "2025-01-15T02:31:14.000Z"
            },
            {
                "messageNumber": 5,
                "severity": "INFO",
                "text": "Task 2295172 has finished at 2025-01-15T02:31:36.133Z with status COMPLETED",
                "timestamp": "2025-01-15T02:31:36.140Z"
            }
        ]
    },
    2326060: {
        "logId": 2326060,
        "status": "FAILED",
        "startTime": "2025-01-18T10:25:19.216Z",
        "endTime": "2025-01-18T10:27:49.471Z",
        "runTime": 150255,
        "objectId": "Monthly_Reconciliation",
        "applicationId": "TASK_CHAINS",
        "activity": "RUN_CHAIN",
        "spaceId": "FINANCE_DWH",
        "user": "finance_admin",
        "children": [
            {
                "nodeId": 1,
                "logId": 2326061,
                "status": "COMPLETED",
                "objectId": "GL_Accounts_Load",
                "activity": "PERSIST",
                "applicationId": "VIEWS",
                "startTime": "2025-01-18T10:25:30.000Z",
                "endTime": "2025-01-18T10:26:15.000Z",
                "runTime": 45000
            },
            {
                "nodeId": 2,
                "logId": 2326062,
                "status": "FAILED",
                "objectId": "Reconciliation_Check",
                "activity": "PERSIST",
                "applicationId": "VIEWS",
                "startTime": "2025-01-18T10:26:16.000Z",
                "endTime": "2025-01-18T10:27:49.000Z",
                "runTime": 93000
            }
        ],
        "messages": [
            {
                "messageNumber": 1,
                "severity": "INFO",
                "text": "Task 2326060 started.",
                "timestamp": "2025-01-18T10:25:19.220Z"
            },
            {
                "messageNumber": 2,
                "severity": "INFO",
                "text": "Loading task chain and prepared 2 tasks that are part of this chain.",
                "timestamp": "2025-01-18T10:25:19.500Z"
            },
            {
                "messageNumber": 3,
                "severity": "INFO",
                "text": "Node 1 with task VIEWS/PERSIST/FINANCE_DWH/GL_Accounts_Load completed successfully.",
                "timestamp": "2025-01-18T10:26:15.100Z"
            },
            {
                "messageNumber": 4,
                "severity": "ERROR",
                "text": "Node 2 failed: Data validation error - mismatched totals between source and target (delta: $1,234.56)",
                "timestamp": "2025-01-18T10:27:49.000Z"
            },
            {
                "messageNumber": 5,
                "severity": "ERROR",
                "text": "Task 2326060 has finished at 2025-01-18T10:27:49.471Z with status FAILED",
                "timestamp": "2025-01-18T10:27:49.471Z"
            }
        ]
    },
    2329400: {
        "logId": 2329400,
        "status": "RUNNING",
        "startTime": "2025-01-20T21:28:56.705Z",
        "runTime": 59441,
        "objectId": "Daily_GL_Load",
        "applicationId": "TASK_CHAINS",
        "activity": "RUN_CHAIN",
        "spaceId": "FINANCE_DWH",
        "user": "etl_service_user",
        "children": [
            {
                "nodeId": 1,
                "logId": 2329401,
                "status": "RUNNING",
                "objectId": "GL_Transactions_Extract",
                "activity": "PERSIST",
                "applicationId": "VIEWS",
                "startTime": "2025-01-20T21:29:10.000Z",
                "runTime": 45000
            }
        ],
        "messages": [
            {
                "messageNumber": 1,
                "severity": "INFO",
                "text": "Task 2329400 started.",
                "timestamp": "2025-01-20T21:28:56.710Z"
            },
            {
                "messageNumber": 2,
                "severity": "INFO",
                "text": "Loading task chain and prepared 1 tasks that are part of this chain.",
                "timestamp": "2025-01-20T21:28:57.000Z"
            },
            {
                "messageNumber": 3,
                "severity": "INFO",
                "text": "Node 1 with task VIEWS/PERSIST/FINANCE_DWH/GL_Transactions_Extract is running...",
                "timestamp": "2025-01-20T21:29:10.000Z"
            }
        ]
    }
}

# Mock task history for get_task_history
MOCK_TASK_HISTORY = {
    "SALES_ANALYTICS": {
        "Daily_Sales_ETL": [
            {
                "logId": 2295172,
                "status": "COMPLETED",
                "startTime": "2025-01-15T02:30:33.142Z",
                "endTime": "2025-01-15T02:31:36.059Z",
                "runTime": 62917,
                "objectId": "Daily_Sales_ETL",
                "applicationId": "TASK_CHAINS",
                "activity": "RUN_CHAIN",
                "spaceId": "SALES_ANALYTICS",
                "user": "etl_service_user"
            },
            {
                "logId": 2290150,
                "status": "COMPLETED",
                "startTime": "2025-01-14T02:30:00.000Z",
                "endTime": "2025-01-14T02:31:45.000Z",
                "runTime": 105000,
                "objectId": "Daily_Sales_ETL",
                "applicationId": "TASK_CHAINS",
                "activity": "RUN_CHAIN",
                "spaceId": "SALES_ANALYTICS",
                "user": "etl_service_user"
            },
            {
                "logId": 2285100,
                "status": "COMPLETED",
                "startTime": "2025-01-13T02:30:00.000Z",
                "endTime": "2025-01-13T02:31:30.000Z",
                "runTime": 90000,
                "objectId": "Daily_Sales_ETL",
                "applicationId": "TASK_CHAINS",
                "activity": "RUN_CHAIN",
                "spaceId": "SALES_ANALYTICS",
                "user": "etl_service_user"
            }
        ],
        "Customer_Sync": [
            {
                "logId": 2295180,
                "status": "COMPLETED",
                "startTime": "2025-01-15T08:00:00.000Z",
                "endTime": "2025-01-15T08:05:30.000Z",
                "runTime": 330000,
                "objectId": "Customer_Sync",
                "applicationId": "TASK_CHAINS",
                "activity": "RUN_CHAIN",
                "spaceId": "SALES_ANALYTICS",
                "user": "sync_service"
            },
            {
                "logId": 2294500,
                "status": "COMPLETED",
                "startTime": "2025-01-15T04:00:00.000Z",
                "endTime": "2025-01-15T04:04:15.000Z",
                "runTime": 255000,
                "objectId": "Customer_Sync",
                "applicationId": "TASK_CHAINS",
                "activity": "RUN_CHAIN",
                "spaceId": "SALES_ANALYTICS",
                "user": "sync_service"
            }
        ]
    },
    "FINANCE_DWH": {
        "Monthly_Reconciliation": [
            {
                "logId": 2326060,
                "status": "FAILED",
                "startTime": "2025-01-18T10:25:19.216Z",
                "endTime": "2025-01-18T10:27:49.471Z",
                "runTime": 150255,
                "objectId": "Monthly_Reconciliation",
                "applicationId": "TASK_CHAINS",
                "activity": "RUN_CHAIN",
                "spaceId": "FINANCE_DWH",
                "user": "finance_admin"
            },
            {
                "logId": 2225105,
                "status": "FAILED",
                "startTime": "2025-01-03T12:26:23.360Z",
                "endTime": "2025-01-03T12:28:38.620Z",
                "runTime": 135260,
                "objectId": "Monthly_Reconciliation",
                "applicationId": "TASK_CHAINS",
                "activity": "RUN_CHAIN",
                "spaceId": "FINANCE_DWH",
                "user": "finance_admin"
            },
            {
                "logId": 2014586,
                "status": "COMPLETED",
                "startTime": "2024-12-01T10:00:00.000Z",
                "endTime": "2024-12-01T10:15:30.000Z",
                "runTime": 930000,
                "objectId": "Monthly_Reconciliation",
                "applicationId": "TASK_CHAINS",
                "activity": "RUN_CHAIN",
                "spaceId": "FINANCE_DWH",
                "user": "finance_admin"
            }
        ],
        "Daily_GL_Load": [
            {
                "logId": 2329400,
                "status": "RUNNING",
                "startTime": "2025-01-20T21:28:56.705Z",
                "runTime": 59441,
                "objectId": "Daily_GL_Load",
                "applicationId": "TASK_CHAINS",
                "activity": "RUN_CHAIN",
                "spaceId": "FINANCE_DWH",
                "user": "etl_service_user"
            },
            {
                "logId": 2325000,
                "status": "COMPLETED",
                "startTime": "2025-01-19T03:00:00.000Z",
                "endTime": "2025-01-19T03:10:45.000Z",
                "runTime": 645000,
                "objectId": "Daily_GL_Load",
                "applicationId": "TASK_CHAINS",
                "activity": "RUN_CHAIN",
                "spaceId": "FINANCE_DWH",
                "user": "etl_service_user"
            }
        ]
    }
}

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
    "database_users": MOCK_DATABASE_USERS,
    # Task management (v1.0.12)
    "task_chains": MOCK_TASK_CHAINS,
    "task_logs": MOCK_TASK_LOGS,
    "task_history": MOCK_TASK_HISTORY
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


# Task Management Helper Functions (v1.0.12)

def get_mock_task_chains(space_id=None):
    """
    Get mock task chains data

    Args:
        space_id: Optional space ID to filter task chains

    Returns:
        List of task chains or dict of all task chains by space
    """
    if space_id:
        return MOCK_TASK_CHAINS.get(space_id, [])
    return MOCK_TASK_CHAINS


def get_mock_task_log(log_id, detail_level="status"):
    """
    Get mock task log details

    Args:
        log_id: The log ID to retrieve
        detail_level: Level of detail - 'status', 'status_only', 'detailed', 'extended'

    Returns:
        Task log details based on detail level
    """
    log_data = MOCK_TASK_LOGS.get(log_id)
    if not log_data:
        return None

    if detail_level == "status_only":
        return log_data.get("status", "UNKNOWN")
    elif detail_level == "status":
        return {"status": log_data.get("status", "UNKNOWN")}
    elif detail_level in ["detailed", "extended"]:
        return log_data
    else:
        return {"status": log_data.get("status", "UNKNOWN")}


def get_mock_task_history(space_id, object_id):
    """
    Get mock task execution history for an object

    Args:
        space_id: The space ID
        object_id: The task chain object ID

    Returns:
        List of historical task runs or empty list if not found
    """
    space_history = MOCK_TASK_HISTORY.get(space_id, {})
    return space_history.get(object_id, [])
