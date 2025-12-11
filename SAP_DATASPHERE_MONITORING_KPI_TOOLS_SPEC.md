# SAP Datasphere MCP Server - Phase 6 & 7: KPI Management + System Monitoring Tools

## Overview

This document provides complete technical specifications for implementing **10 monitoring and KPI management tools** that enable business intelligence, system administration, and operational monitoring of SAP Datasphere.

**Phases**: 6 (KPI Management) + 7 (System Monitoring & Administration)  
**Priority**: MEDIUM  
**Estimated Implementation Time**: 6-8 days  
**Tools Count**: 10

---

# PHASE 6: KPI MANAGEMENT (3 tools)

## Tool 1: `search_kpis`

### Purpose
Search and discover KPIs using advanced query syntax with scope-based filtering and faceted search capabilities.

### API Endpoint
```
GET /api/v1/datasphere/search
```

### Authentication
- **Type**: OAuth2 Bearer Token
- **Scopes**: `DWC_SEARCH` or equivalent search scope

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search query with SCOPE prefix |
| `facets` | string | No | Comma-separated facets to include |
| `top` | integer | No | Maximum results (default: 50, max: 500) |
| `skip` | integer | No | Results to skip for pagination |
| `include_count` | boolean | No | Include total count (default: false) |

### KPI Search Syntax
```
SCOPE:comsapcatalogsearchprivateSearchKPIsAdmin <search_terms>
```

### Example Queries
```
# Search all KPIs
SCOPE:comsapcatalogsearchprivateSearchKPIsAdmin financial

# Search with facets
SCOPE:comsapcatalogsearchprivateSearchKPIsAdmin revenue facets=objectType,spaceId

# Boolean search
SCOPE:comsapcatalogsearchprivateSearchKPIsAdmin (revenue OR profit) AND quarterly
```

### Response Format
```json
{
  "@odata.context": "$metadata#search",
  "@odata.count": 25,
  "value": [
    {
      "id": "kpi-12345",
      "objectType": "KPI",
      "name": "Quarterly Revenue Growth",
      "description": "Measures quarterly revenue growth percentage",
      "spaceId": "FINANCE_ANALYTICS",
      "spaceName": "Finance Analytics",
      "businessArea": "Finance",
      "category": "Revenue",
      "formula": "((Q2_Revenue - Q1_Revenue) / Q1_Revenue) * 100",
      "unit": "Percentage",
      "targetValue": 15.0,
      "currentValue": 12.5,
      "status": "Below Target",
      "lastUpdated": "2024-12-01T10:30:00Z",
      "owner": "finance.team@company.com",
      "tags": ["revenue", "growth", "quarterly", "finance"],
      "dataSource": "FINANCIAL_TRANSACTIONS",
      "calculationFrequency": "Quarterly",
      "thresholds": {
        "green": ">= 15",
        "yellow": "10-15",
        "red": "< 10"
      }
    }
  ],
  "facets": {
    "objectType": [
      {"value": "KPI", "count": 25}
    ],
    "spaceId": [
      {"value": "FINANCE_ANALYTICS", "count": 15},
      {"value": "SALES_ANALYTICS", "count": 10}
    ],
    "category": [
      {"value": "Revenue", "count": 8},
      {"value": "Profitability", "count": 7},
      {"value": "Efficiency", "count": 10}
    ]
  }
}
```

### Error Handling

| Status Code | Error Scenario | Handling Strategy |
|-------------|----------------|-------------------|
| 400 | Invalid search syntax | Parse error and provide syntax help |
| 401 | Unauthorized | Refresh OAuth2 token and retry |
| 403 | Insufficient search permissions | Return permission error |
| 500 | Search service error | Retry with exponential backoff |

---

## Tool 2: `get_kpi_details`

### Purpose
Retrieve detailed KPI metadata including calculation logic, data sources, thresholds, and historical performance.

### API Endpoint
```
GET /api/v1/datasphere/kpis/{kpiId}
```

### Authentication
- **Type**: OAuth2 Bearer Token
- **Scopes**: `DWC_KPI_READ` or equivalent KPI access scope

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `kpiId` | string | Yes | KPI identifier |
| `include_history` | boolean | No | Include historical values (default: false) |
| `include_lineage` | boolean | No | Include data lineage (default: false) |
| `history_period` | string | No | History period (1M, 3M, 6M, 1Y) |

### Response Format
```json
{
  "id": "kpi-12345",
  "name": "Quarterly Revenue Growth",
  "businessName": "Q/Q Revenue Growth %",
  "description": "Measures the percentage growth in revenue compared to the previous quarter",
  "category": "Revenue",
  "businessArea": "Finance",
  "spaceId": "FINANCE_ANALYTICS",
  "spaceName": "Finance Analytics",
  "owner": "finance.team@company.com",
  "createdBy": "john.doe@company.com",
  "createdAt": "2024-01-15T09:00:00Z",
  "modifiedBy": "jane.smith@company.com",
  "modifiedAt": "2024-11-20T14:30:00Z",
  "status": "Active",
  "calculation": {
    "formula": "((Current_Quarter_Revenue - Previous_Quarter_Revenue) / Previous_Quarter_Revenue) * 100",
    "formulaDescription": "Percentage change from previous quarter",
    "calculationType": "Derived",
    "calculationFrequency": "Quarterly",
    "aggregationMethod": "Sum",
    "dataRefreshSchedule": "Daily at 06:00 UTC"
  },
  "dataSources": [
    {
      "name": "FINANCIAL_TRANSACTIONS",
      "type": "Table",
      "spaceId": "SAP_CONTENT",
      "columns": ["AMOUNT", "TRANSACTION_DATE", "ACCOUNT_TYPE"],
      "filters": "ACCOUNT_TYPE = 'Revenue'"
    },
    {
      "name": "QUARTERLY_AGGREGATES",
      "type": "View",
      "spaceId": "FINANCE_ANALYTICS",
      "columns": ["QUARTER", "TOTAL_REVENUE"]
    }
  ],
  "currentValue": {
    "value": 12.5,
    "unit": "Percentage",
    "asOfDate": "2024-12-01T00:00:00Z",
    "status": "Below Target",
    "trend": "Improving"
  },
  "targets": {
    "targetValue": 15.0,
    "minAcceptable": 10.0,
    "maxExpected": 20.0,
    "targetPeriod": "Q4 2024"
  },
  "thresholds": {
    "excellent": {
      "condition": ">= 20",
      "color": "darkgreen",
      "description": "Exceptional growth"
    },
    "good": {
      "condition": "15-20",
      "color": "green",
      "description": "Target achieved"
    },
    "warning": {
      "condition": "10-15",
      "color": "yellow",
      "description": "Below target but acceptable"
    },
    "critical": {
      "condition": "< 10",
      "color": "red",
      "description": "Requires immediate attention"
    }
  },
  "historicalValues": [
    {
      "period": "Q3 2024",
      "value": 8.2,
      "status": "Critical",
      "date": "2024-09-30T00:00:00Z"
    },
    {
      "period": "Q2 2024",
      "value": 18.5,
      "status": "Good",
      "date": "2024-06-30T00:00:00Z"
    }
  ],
  "alerts": [
    {
      "type": "Threshold",
      "condition": "Below Target",
      "message": "KPI is 2.5 percentage points below target",
      "severity": "Warning",
      "triggeredAt": "2024-12-01T10:30:00Z"
    }
  ],
  "tags": ["revenue", "growth", "quarterly", "finance", "critical"],
  "businessContext": {
    "purpose": "Track revenue growth to ensure business expansion targets are met",
    "stakeholders": ["CFO", "Finance Team", "Executive Leadership"],
    "reportingFrequency": "Monthly Board Reports",
    "benchmarks": "Industry average: 12-15% quarterly growth"
  }
}
```

### Error Handling

| Status Code | Error Scenario | Handling Strategy |
|-------------|----------------|-------------------|
| 401 | Unauthorized | Refresh token and retry |
| 403 | No access to KPI | Return permission error |
| 404 | KPI not found | Return clear error with available KPIs |
| 500 | KPI service error | Retry with backoff |

---

## Tool 3: `list_all_kpis`

### Purpose
Get comprehensive inventory of all defined KPIs across all accessible spaces with filtering and categorization.

### API Endpoint
```
GET /api/v1/datasphere/kpis
```

### Authentication
- **Type**: OAuth2 Bearer Token
- **Scopes**: `DWC_KPI_READ` or equivalent KPI access scope

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `space_id` | string | No | Filter by specific space |
| `category` | string | No | Filter by KPI category |
| `business_area` | string | No | Filter by business area |
| `status` | string | No | Filter by status (Active, Inactive, Draft) |
| `owner` | string | No | Filter by owner |
| `include_inactive` | boolean | No | Include inactive KPIs (default: false) |
| `top` | integer | No | Maximum results (default: 100, max: 1000) |
| `skip` | integer | No | Results to skip for pagination |

### Response Format
```json
{
  "@odata.context": "$metadata#kpis",
  "@odata.count": 156,
  "value": [
    {
      "id": "kpi-12345",
      "name": "Quarterly Revenue Growth",
      "category": "Revenue",
      "businessArea": "Finance",
      "spaceId": "FINANCE_ANALYTICS",
      "spaceName": "Finance Analytics",
      "currentValue": 12.5,
      "targetValue": 15.0,
      "unit": "Percentage",
      "status": "Below Target",
      "owner": "finance.team@company.com",
      "lastUpdated": "2024-12-01T10:30:00Z",
      "calculationFrequency": "Quarterly",
      "tags": ["revenue", "growth", "quarterly"]
    },
    {
      "id": "kpi-67890",
      "name": "Customer Satisfaction Score",
      "category": "Customer Experience",
      "businessArea": "Sales",
      "spaceId": "SALES_ANALYTICS",
      "spaceName": "Sales Analytics",
      "currentValue": 4.2,
      "targetValue": 4.5,
      "unit": "Score (1-5)",
      "status": "Good",
      "owner": "sales.team@company.com",
      "lastUpdated": "2024-12-01T08:15:00Z",
      "calculationFrequency": "Weekly",
      "tags": ["customer", "satisfaction", "experience"]
    }
  ],
  "summary": {
    "totalKpis": 156,
    "activeKpis": 142,
    "inactiveKpis": 14,
    "byStatus": {
      "Excellent": 23,
      "Good": 45,
      "Warning": 52,
      "Critical": 22
    },
    "byCategory": {
      "Revenue": 28,
      "Profitability": 22,
      "Customer Experience": 31,
      "Operational Efficiency": 35,
      "Risk Management": 18,
      "Compliance": 22
    },
    "byBusinessArea": {
      "Finance": 50,
      "Sales": 42,
      "Operations": 35,
      "HR": 18,
      "IT": 11
    }
  }
}
```

---

# PHASE 7: SYSTEM MONITORING & ADMINISTRATION (7 tools)

## Tool 4: `get_systems_overview`

### Purpose
Get comprehensive landscape overview of all registered systems, connections, and their health status.

### API Endpoint
```
GET /api/v1/datasphere/systems/overview
```

### Authentication
- **Type**: OAuth2 Bearer Token
- **Scopes**: `DWC_ADMIN` or equivalent system monitoring scope

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `include_details` | boolean | No | Include detailed system information |
| `health_check` | boolean | No | Perform real-time health check |

### Response Format
```json
{
  "tenant": {
    "id": "tenant-12345",
    "name": "Company Analytics Tenant",
    "region": "us-east-1",
    "version": "2024.20",
    "status": "Active",
    "lastHealthCheck": "2024-12-09T10:30:00Z"
  },
  "systems": [
    {
      "id": "system-sap-s4",
      "name": "SAP S/4HANA Production",
      "type": "SAP_S4HANA",
      "status": "Connected",
      "health": "Healthy",
      "lastConnection": "2024-12-09T10:25:00Z",
      "connectionDetails": {
        "host": "s4hana-prod.company.com",
        "port": 443,
        "protocol": "HTTPS",
        "authentication": "OAuth2"
      },
      "dataFlows": 12,
      "activeConnections": 3,
      "lastDataSync": "2024-12-09T09:00:00Z",
      "metrics": {
        "avgResponseTime": "250ms",
        "successRate": "99.2%",
        "dataVolume": "2.3TB"
      }
    },
    {
      "id": "system-salesforce",
      "name": "Salesforce CRM",
      "type": "SALESFORCE",
      "status": "Connected",
      "health": "Warning",
      "lastConnection": "2024-12-09T10:20:00Z",
      "connectionDetails": {
        "host": "company.salesforce.com",
        "authentication": "OAuth2"
      },
      "dataFlows": 5,
      "activeConnections": 1,
      "lastDataSync": "2024-12-09T08:30:00Z",
      "metrics": {
        "avgResponseTime": "850ms",
        "successRate": "97.8%",
        "dataVolume": "450GB"
      },
      "alerts": [
        {
          "type": "Performance",
          "message": "Response time above threshold",
          "severity": "Warning",
          "timestamp": "2024-12-09T10:15:00Z"
        }
      ]
    }
  ],
  "spaces": [
    {
      "id": "SAP_CONTENT",
      "name": "SAP Content",
      "status": "Active",
      "objectCount": 1247,
      "storageUsed": "15.2GB",
      "lastActivity": "2024-12-09T10:28:00Z"
    },
    {
      "id": "FINANCE_ANALYTICS",
      "name": "Finance Analytics",
      "status": "Active",
      "objectCount": 89,
      "storageUsed": "3.8GB",
      "lastActivity": "2024-12-09T09:45:00Z"
    }
  ],
  "summary": {
    "totalSystems": 8,
    "healthySystems": 6,
    "warningSystems": 2,
    "criticalSystems": 0,
    "totalSpaces": 12,
    "activeSpaces": 12,
    "totalStorage": "125.6GB",
    "totalObjects": 3456
  }
}
```

---

## Tool 5: `search_system_logs`

### Purpose
Search and filter system activity logs with advanced filtering and faceted analysis capabilities.

### API Endpoint
```
GET /api/v1/datasphere/logs/search
```

### Authentication
- **Type**: OAuth2 Bearer Token
- **Scopes**: `DWC_ADMIN` or equivalent log access scope

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | No | Search query for log content |
| `level` | string | No | Log level (ERROR, WARN, INFO, DEBUG) |
| `component` | string | No | System component |
| `user_id` | string | No | Filter by user |
| `start_time` | string | No | Start time (ISO 8601) |
| `end_time` | string | No | End time (ISO 8601) |
| `facets` | string | No | Facets to include |
| `top` | integer | No | Maximum results (default: 100, max: 1000) |
| `skip` | integer | No | Results to skip |

### Response Format
```json
{
  "@odata.context": "$metadata#logs",
  "@odata.count": 2847,
  "value": [
    {
      "id": "log-12345",
      "timestamp": "2024-12-09T10:30:15.234Z",
      "level": "ERROR",
      "component": "DataFlow",
      "message": "Data flow execution failed: Connection timeout to SAP S/4HANA",
      "details": {
        "dataFlowId": "df-fin-daily-001",
        "dataFlowName": "Daily Financial Data Load",
        "spaceId": "FINANCE_ANALYTICS",
        "userId": "system.etl@company.com",
        "sessionId": "session-789",
        "errorCode": "CONN_TIMEOUT",
        "duration": "30000ms"
      },
      "stackTrace": "com.sap.datasphere.dataflow.ConnectionException: Timeout...",
      "correlationId": "corr-456-789",
      "tags": ["dataflow", "error", "timeout", "s4hana"]
    },
    {
      "id": "log-12346",
      "timestamp": "2024-12-09T10:29:45.123Z",
      "level": "INFO",
      "component": "Authentication",
      "message": "User login successful",
      "details": {
        "userId": "john.doe@company.com",
        "sessionId": "session-790",
        "ipAddress": "192.168.1.100",
        "userAgent": "Mozilla/5.0...",
        "loginMethod": "OAuth2"
      },
      "correlationId": "corr-456-790",
      "tags": ["auth", "login", "success"]
    }
  ],
  "facets": {
    "level": [
      {"value": "ERROR", "count": 234},
      {"value": "WARN", "count": 567},
      {"value": "INFO", "count": 1890},
      {"value": "DEBUG", "count": 156}
    ],
    "component": [
      {"value": "DataFlow", "count": 456},
      {"value": "Authentication", "count": 234},
      {"value": "Connection", "count": 345},
      {"value": "Query", "count": 567}
    ],
    "tags": [
      {"value": "error", "count": 234},
      {"value": "timeout", "count": 89},
      {"value": "auth", "count": 345}
    ]
  },
  "timeDistribution": [
    {"hour": "08:00", "count": 145},
    {"hour": "09:00", "count": 234},
    {"hour": "10:00", "count": 189}
  ]
}
```

---

## Tool 6: `download_system_logs`

### Purpose
Export system logs for offline analysis with various format options and filtering capabilities.

### API Endpoint
```
GET /api/v1/datasphere/logs/export
```

### Authentication
- **Type**: OAuth2 Bearer Token
- **Scopes**: `DWC_ADMIN` or equivalent log export scope

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `format` | string | No | Export format (JSON, CSV, XML) default: JSON |
| `level` | string | No | Log level filter |
| `component` | string | No | Component filter |
| `start_time` | string | No | Start time (ISO 8601) |
| `end_time` | string | No | End time (ISO 8601) |
| `max_records` | integer | No | Maximum records (default: 10000, max: 100000) |
| `include_details` | boolean | No | Include detailed information |

### Response Format
```json
{
  "exportId": "export-12345",
  "status": "Completed",
  "format": "JSON",
  "recordCount": 5678,
  "fileSize": "12.5MB",
  "downloadUrl": "https://datasphere.company.com/exports/logs-export-12345.json",
  "expiresAt": "2024-12-16T10:30:00Z",
  "filters": {
    "level": "ERROR,WARN",
    "startTime": "2024-12-08T00:00:00Z",
    "endTime": "2024-12-09T23:59:59Z",
    "component": "DataFlow"
  },
  "metadata": {
    "exportedAt": "2024-12-09T10:30:00Z",
    "exportedBy": "admin@company.com",
    "tenant": "tenant-12345",
    "version": "2024.20"
  }
}
```

---

## Tool 7: `get_system_log_facets`

### Purpose
Analyze logs with dimensional filtering to identify patterns, trends, and anomalies.

### API Endpoint
```
GET /api/v1/datasphere/logs/facets
```

### Authentication
- **Type**: OAuth2 Bearer Token
- **Scopes**: `DWC_ADMIN` or equivalent log analysis scope

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `facet_fields` | string | No | Comma-separated facet fields |
| `start_time` | string | No | Analysis start time |
| `end_time` | string | No | Analysis end time |
| `level` | string | No | Log level filter |
| `component` | string | No | Component filter |

### Response Format
```json
{
  "analysisId": "analysis-12345",
  "timeRange": {
    "startTime": "2024-12-08T00:00:00Z",
    "endTime": "2024-12-09T23:59:59Z",
    "duration": "48 hours"
  },
  "totalRecords": 15678,
  "facets": {
    "level": [
      {"value": "ERROR", "count": 456, "percentage": 2.9},
      {"value": "WARN", "count": 1234, "percentage": 7.9},
      {"value": "INFO", "count": 12890, "percentage": 82.2},
      {"value": "DEBUG", "count": 1098, "percentage": 7.0}
    ],
    "component": [
      {"value": "DataFlow", "count": 3456, "percentage": 22.0},
      {"value": "Authentication", "count": 2345, "percentage": 15.0},
      {"value": "Connection", "count": 4567, "percentage": 29.1},
      {"value": "Query", "count": 5310, "percentage": 33.9}
    ],
    "hourly": [
      {"hour": "00:00", "count": 234},
      {"hour": "01:00", "count": 189},
      {"hour": "08:00", "count": 1456},
      {"hour": "09:00", "count": 1789}
    ],
    "users": [
      {"user": "system.etl@company.com", "count": 2345},
      {"user": "john.doe@company.com", "count": 456},
      {"user": "jane.smith@company.com", "count": 234}
    ]
  },
  "trends": {
    "errorRate": {
      "current": 2.9,
      "previous": 1.8,
      "trend": "Increasing",
      "change": "+61%"
    },
    "topErrors": [
      {"error": "Connection timeout", "count": 89},
      {"error": "Authentication failed", "count": 67},
      {"error": "Query execution timeout", "count": 45}
    ]
  },
  "anomalies": [
    {
      "type": "Error Spike",
      "description": "Error rate increased by 300% between 08:00-09:00",
      "timestamp": "2024-12-09T08:30:00Z",
      "severity": "High"
    }
  ]
}
```

---

## Tool 8: `list_users`

### Purpose
List all users in the tenant with their roles, permissions, and activity status.

### API Endpoint
```
GET /api/v1/datasphere/users
```

### Authentication
- **Type**: OAuth2 Bearer Token
- **Scopes**: `DWC_USER_ADMIN` or equivalent user management scope

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | string | No | Filter by status (Active, Inactive, Locked) |
| `role` | string | No | Filter by role |
| `space_id` | string | No | Filter by space access |
| `include_permissions` | boolean | No | Include detailed permissions |
| `top` | integer | No | Maximum results (default: 100) |
| `skip` | integer | No | Results to skip |

### Response Format
```json
{
  "@odata.context": "$metadata#users",
  "@odata.count": 45,
  "value": [
    {
      "id": "user-12345",
      "username": "john.doe@company.com",
      "displayName": "John Doe",
      "firstName": "John",
      "lastName": "Doe",
      "email": "john.doe@company.com",
      "status": "Active",
      "roles": ["DWC_ANALYST", "SPACE_VIEWER"],
      "department": "Finance",
      "manager": "jane.smith@company.com",
      "createdAt": "2024-01-15T09:00:00Z",
      "lastLogin": "2024-12-09T08:30:00Z",
      "loginCount": 234,
      "spaceAccess": [
        {
          "spaceId": "FINANCE_ANALYTICS",
          "spaceName": "Finance Analytics",
          "role": "Viewer",
          "grantedAt": "2024-01-15T09:00:00Z"
        }
      ],
      "permissions": [
        "READ_CATALOG",
        "EXECUTE_QUERIES",
        "VIEW_DASHBOARDS"
      ]
    }
  ],
  "summary": {
    "totalUsers": 45,
    "activeUsers": 42,
    "inactiveUsers": 3,
    "byRole": {
      "DWC_ADMIN": 3,
      "DWC_ANALYST": 15,
      "SPACE_VIEWER": 20,
      "GUEST": 7
    },
    "byDepartment": {
      "Finance": 12,
      "Sales": 10,
      "Operations": 8,
      "IT": 5,
      "HR": 4,
      "Other": 6
    }
  }
}
```

---

## Tool 9: `get_user_permissions`

### Purpose
Retrieve detailed user permissions and access rights across spaces and objects.

### API Endpoint
```
GET /api/v1/datasphere/users/{userId}/permissions
```

### Authentication
- **Type**: OAuth2 Bearer Token
- **Scopes**: `DWC_USER_ADMIN` or equivalent user management scope

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `userId` | string | Yes | User identifier |
| `space_id` | string | No | Filter by specific space |
| `include_inherited` | boolean | No | Include inherited permissions |

### Response Format
```json
{
  "userId": "user-12345",
  "username": "john.doe@company.com",
  "displayName": "John Doe",
  "roles": ["DWC_ANALYST", "SPACE_VIEWER"],
  "globalPermissions": [
    "READ_CATALOG",
    "EXECUTE_QUERIES",
    "VIEW_DASHBOARDS",
    "EXPORT_DATA"
  ],
  "spacePermissions": [
    {
      "spaceId": "FINANCE_ANALYTICS",
      "spaceName": "Finance Analytics",
      "role": "Viewer",
      "permissions": [
        "READ_OBJECTS",
        "EXECUTE_QUERIES",
        "VIEW_DATA"
      ],
      "grantedBy": "admin@company.com",
      "grantedAt": "2024-01-15T09:00:00Z"
    },
    {
      "spaceId": "SAP_CONTENT",
      "spaceName": "SAP Content",
      "role": "Viewer",
      "permissions": [
        "READ_OBJECTS",
        "VIEW_METADATA"
      ],
      "inherited": true,
      "inheritedFrom": "DWC_ANALYST"
    }
  ],
  "objectPermissions": [
    {
      "objectId": "FINANCIAL_TRANSACTIONS",
      "objectName": "Financial Transactions",
      "objectType": "Table",
      "spaceId": "SAP_CONTENT",
      "permissions": [
        "READ",
        "QUERY"
      ]
    }
  ],
  "restrictions": [
    {
      "type": "Data Access",
      "description": "Cannot access PII columns",
      "appliesTo": "All tables with PII classification"
    }
  ],
  "lastPermissionUpdate": "2024-11-20T14:30:00Z"
}
```

---

## Tool 10: `get_user_details`

### Purpose
Get comprehensive user information including profile, activity, and audit trail.

### API Endpoint
```
GET /api/v1/datasphere/users/{userId}
```

### Authentication
- **Type**: OAuth2 Bearer Token
- **Scopes**: `DWC_USER_ADMIN` or equivalent user management scope

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `userId` | string | Yes | User identifier |
| `include_activity` | boolean | No | Include recent activity |
| `include_audit` | boolean | No | Include audit trail |
| `activity_days` | integer | No | Days of activity to include (default: 30) |

### Response Format
```json
{
  "id": "user-12345",
  "username": "john.doe@company.com",
  "displayName": "John Doe",
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@company.com",
  "status": "Active",
  "profile": {
    "department": "Finance",
    "jobTitle": "Senior Financial Analyst",
    "manager": "jane.smith@company.com",
    "location": "New York, NY",
    "timezone": "America/New_York",
    "phone": "+1-555-0123",
    "employeeId": "EMP-12345"
  },
  "account": {
    "createdAt": "2024-01-15T09:00:00Z",
    "createdBy": "admin@company.com",
    "lastModified": "2024-11-20T14:30:00Z",
    "modifiedBy": "hr.admin@company.com",
    "passwordLastChanged": "2024-10-15T10:00:00Z",
    "mfaEnabled": true,
    "accountLocked": false
  },
  "activity": {
    "lastLogin": "2024-12-09T08:30:00Z",
    "loginCount": 234,
    "lastActivity": "2024-12-09T10:15:00Z",
    "sessionsLast30Days": 45,
    "queriesExecuted": 1234,
    "dashboardsViewed": 89,
    "reportsGenerated": 23
  },
  "roles": [
    {
      "role": "DWC_ANALYST",
      "assignedAt": "2024-01-15T09:00:00Z",
      "assignedBy": "admin@company.com"
    },
    {
      "role": "SPACE_VIEWER",
      "assignedAt": "2024-02-01T10:00:00Z",
      "assignedBy": "space.admin@company.com"
    }
  ],
  "spaceAccess": [
    {
      "spaceId": "FINANCE_ANALYTICS",
      "spaceName": "Finance Analytics",
      "role": "Viewer",
      "grantedAt": "2024-01-15T09:00:00Z",
      "lastAccessed": "2024-12-09T09:45:00Z",
      "accessCount": 156
    }
  ],
  "recentActivity": [
    {
      "timestamp": "2024-12-09T10:15:00Z",
      "action": "Query Executed",
      "details": "SELECT * FROM FINANCIAL_TRANSACTIONS WHERE...",
      "spaceId": "SAP_CONTENT",
      "duration": "2.3s"
    },
    {
      "timestamp": "2024-12-09T09:45:00Z",
      "action": "Dashboard Viewed",
      "details": "Financial KPI Dashboard",
      "spaceId": "FINANCE_ANALYTICS"
    }
  ],
  "auditTrail": [
    {
      "timestamp": "2024-11-20T14:30:00Z",
      "action": "Role Added",
      "details": "Added SPACE_VIEWER role",
      "performedBy": "admin@company.com"
    },
    {
      "timestamp": "2024-10-15T10:00:00Z",
      "action": "Password Changed",
      "details": "User changed password",
      "performedBy": "john.doe@company.com"
    }
  ]
}
```

---

## Common Implementation Patterns

### 1. OAuth2 Token Management
```python
class OAuth2TokenManager:
    """Manage OAuth2 token lifecycle with automatic refresh."""
    
    def __init__(self, client_id: str, client_secret: str, token_url: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.access_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
    
    async def get_token(self) -> str:
        """Get valid access token, refreshing if necessary."""
        if self.access_token and self.token_expiry and self.token_expiry > datetime.now():
            return self.access_token
        
        return await self.refresh_token()
```

### 2. Search Query Builder
```python
class KPISearchBuilder:
    """Build KPI search queries with proper scope syntax."""
    
    def __init__(self):
        self.scope = "comsapcatalogsearchprivateSearchKPIsAdmin"
        self.terms = []
        self.facets = []
    
    def add_term(self, term: str) -> 'KPISearchBuilder':
        self.terms.append(term)
        return self
    
    def add_facet(self, facet: str) -> 'KPISearchBuilder':
        self.facets.append(facet)
        return self
    
    def build(self) -> str:
        query = f"SCOPE:{self.scope} {' '.join(self.terms)}"
        return query
```

### 3. Log Analysis Helper
```python
def analyze_log_patterns(logs: List[dict]) -> dict:
    """Analyze log patterns and identify anomalies."""
    
    # Group by time periods
    hourly_counts = {}
    error_patterns = {}
    
    for log in logs:
        hour = log['timestamp'][:13]  # YYYY-MM-DDTHH
        hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
        
        if log['level'] == 'ERROR':
            error_type = log.get('details', {}).get('errorCode', 'Unknown')
            error_patterns[error_type] = error_patterns.get(error_type, 0) + 1
    
    return {
        'hourly_distribution': hourly_counts,
        'error_patterns': error_patterns,
        'total_logs': len(logs)
    }
```

### 4. User Permission Checker
```python
def check_user_permissions(user_permissions: dict, required_permission: str) -> bool:
    """Check if user has required permission."""
    
    # Check global permissions
    if required_permission in user_permissions.get('globalPermissions', []):
        return True
    
    # Check space-specific permissions
    for space_perm in user_permissions.get('spacePermissions', []):
        if required_permission in space_perm.get('permissions', []):
            return True
    
    return False
```

---

## Testing Strategy

### Unit Tests
1. **KPI Search**: Test query building and result parsing
2. **Log Analysis**: Test filtering and facet analysis
3. **User Management**: Test permission checking and role validation
4. **System Monitoring**: Test health status aggregation

### Integration Tests
1. **KPI Discovery**: Test full KPI search and detail retrieval workflow
2. **Log Export**: Test log search, analysis, and export workflow
3. **User Administration**: Test user listing, permission retrieval workflow
4. **System Health**: Test system overview and monitoring workflow

### Performance Tests
1. **Large Log Sets**: Test with 100,000+ log entries
2. **Many Users**: Test with 1000+ users
3. **Complex KPI Queries**: Test with multiple facets and filters
4. **Concurrent Monitoring**: Test multiple simultaneous system checks

---

## Security Considerations

1. **Admin Permissions**: Verify admin scope for system monitoring tools
2. **User Privacy**: Mask sensitive user information in logs
3. **Log Security**: Ensure log exports don't contain credentials
4. **Permission Validation**: Validate user permissions before data access
5. **Audit Logging**: Log all administrative actions

---

## Success Criteria

- ✅ Can search and discover KPIs with advanced syntax
- ✅ Can retrieve detailed KPI metadata and calculations
- ✅ Can list and categorize all KPIs
- ✅ Can monitor system health and connections
- ✅ Can search and analyze system logs
- ✅ Can export logs for offline analysis
- ✅ Can manage users and permissions
- ✅ Proper error handling for all scenarios
- ✅ Performance acceptable for large datasets

---

## Next Steps

After implementing Phases 6 & 7:
1. Test with real SAP Datasphere tenant
2. Validate with various KPI types and log volumes
3. Performance benchmark with large user bases
4. Create usage documentation
5. Proceed to Phase 8: Advanced Features (optional)

---

**Document Version**: 1.0  
**Last Updated**: December 9, 2025  
**Related Documents**:
- SAP_DATASPHERE_MCP_EXTRACTION_PLAN.md
- SAP_DATASPHERE_ANALYTICAL_TOOLS_SPEC.md
- SAP_DATASPHERE_FOUNDATION_TOOLS_SPEC.md