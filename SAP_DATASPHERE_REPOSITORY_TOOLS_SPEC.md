# SAP Datasphere Repository Object Discovery Tools - Detailed Specification

## Overview

This document provides complete API specifications and implementation guidance for the three repository object discovery tools in the SAP Datasphere MCP Server. These tools enable deep exploration of design-time and runtime objects.

---

## Tool 1: `list_repository_objects`

### Purpose
Browse all repository objects including tables, views, models, data flows, and transformations.

### API Endpoint Details

**Primary Endpoint (Space-specific)**:
```
GET /deepsea/repository/{spaceId}/objects
```

**Alternative Endpoints**:
```
GET /api/v1/repository/objects
GET /deepsea/repository/SAP_CONTENT/objects
```

### Authentication
- **Type**: OAuth2 Bearer Token
- **Required Scopes**: Repository read access

### Path Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `spaceId` | string | Yes | Space identifier | `SAP_CONTENT` |

### Request Parameters (OData Query Options)

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `$select` | string | No | Select specific fields | `name,objectType,status` |
| `$filter` | string | No | Filter by criteria | `objectType eq 'Table'` |
| `$expand` | string | No | Expand related entities | `columns,dependencies` |
| `$top` | integer | No | Limit results | `50` |
| `$skip` | integer | No | Skip results (pagination) | `0` |
| `$orderby` | string | No | Sort results | `name asc` |

### Response Format
**Content-Type**: `application/json`

### Expected Response Structure
```json
{
  "@odata.context": "$metadata#objects",
  "value": [
    {
      "id": "repo-obj-12345",
      "objectType": "Table",
      "name": "FINANCIAL_TRANSACTIONS",
      "businessName": "Financial Transactions Table",
      "technicalName": "FINANCIAL_TRANSACTIONS",
      "description": "Core financial transaction data with account information",
      "spaceId": "SAP_CONTENT",
      "spaceName": "SAP Content",
      "status": "Active",
      "deploymentStatus": "Deployed",
      "owner": "SYSTEM",
      "createdBy": "SYSTEM",
      "createdAt": "2024-01-15T10:30:00Z",
      "modifiedBy": "ADMIN",
      "modifiedAt": "2024-11-20T14:22:00Z",
      "version": "2.1",
      "packageName": "sap.content.finance",
      "tags": ["finance", "transactions", "core"],
      "columns": [
        {
          "name": "TRANSACTION_ID",
          "dataType": "NVARCHAR(50)",
          "isPrimaryKey": true,
          "isNullable": false,
          "description": "Unique transaction identifier"
        },
        {
          "name": "AMOUNT",
          "dataType": "DECIMAL(15,2)",
          "isPrimaryKey": false,
          "isNullable": false,
          "description": "Transaction amount"
        },
        {
          "name": "CURRENCY",
          "dataType": "NVARCHAR(3)",
          "isPrimaryKey": false,
          "isNullable": false,
          "description": "Currency code"
        }
      ],
      "dependencies": {
        "upstream": ["SOURCE_SYSTEM_TABLE"],
        "downstream": ["FIN_ANALYTICS_VIEW", "FIN_REPORT_MODEL"]
      },
      "lineage": {
        "sourceSystem": "SAP_ERP",
        "loadFrequency": "Daily",
        "lastLoaded": "2024-12-04T02:00:00Z"
      }
    },
    {
      "id": "repo-obj-67890",
      "objectType": "View",
      "name": "CUSTOMER_FINANCIAL_SUMMARY",
      "businessName": "Customer Financial Summary View",
      "technicalName": "CUSTOMER_FIN_SUMMARY_VIEW",
      "description": "Aggregated customer financial data",
      "spaceId": "SAP_CONTENT",
      "spaceName": "SAP Content",
      "status": "Active",
      "deploymentStatus": "Deployed",
      "owner": "FIN_ADMIN",
      "createdBy": "FIN_ADMIN",
      "createdAt": "2024-03-10T08:15:00Z",
      "modifiedBy": "FIN_ADMIN",
      "modifiedAt": "2024-10-05T16:45:00Z",
      "version": "1.3",
      "packageName": "sap.content.finance.views",
      "tags": ["customer", "finance", "summary"],
      "basedOn": ["FINANCIAL_TRANSACTIONS", "CUSTOMER_MASTER"],
      "dependencies": {
        "upstream": ["FINANCIAL_TRANSACTIONS", "CUSTOMER_MASTER"],
        "downstream": ["CUSTOMER_DASHBOARD"]
      }
    },
    {
      "id": "repo-obj-11111",
      "objectType": "AnalyticalModel",
      "name": "SALES_ANALYTICS_MODEL",
      "businessName": "Sales Analytics Model",
      "technicalName": "SALES_ANALYTICS_MODEL",
      "description": "Comprehensive sales analytics with dimensions and measures",
      "spaceId": "SALES_SPACE",
      "spaceName": "Sales Analytics",
      "status": "Active",
      "deploymentStatus": "Deployed",
      "owner": "SALES_ADMIN",
      "createdBy": "SALES_ADMIN",
      "createdAt": "2024-02-20T09:15:00Z",
      "modifiedBy": "SALES_ADMIN",
      "modifiedAt": "2024-11-15T14:30:00Z",
      "version": "3.0",
      "packageName": "sales.analytics",
      "tags": ["sales", "analytics", "kpi"],
      "dimensions": ["Customer", "Product", "Time", "Region"],
      "measures": ["Revenue", "Quantity", "Profit"],
      "basedOn": ["SALES_ORDERS", "SALES_ITEMS"],
      "dependencies": {
        "upstream": ["SALES_ORDERS", "SALES_ITEMS", "CUSTOMER_MASTER"],
        "downstream": ["SALES_DASHBOARD", "EXECUTIVE_REPORT"]
      }
    },
    {
      "id": "repo-obj-22222",
      "objectType": "DataFlow",
      "name": "LOAD_FINANCIAL_DATA",
      "businessName": "Financial Data Load Process",
      "technicalName": "LOAD_FINANCIAL_DATA",
      "description": "ETL process for loading financial transactions from ERP",
      "spaceId": "SAP_CONTENT",
      "spaceName": "SAP Content",
      "status": "Active",
      "deploymentStatus": "Deployed",
      "owner": "ETL_ADMIN",
      "createdBy": "ETL_ADMIN",
      "createdAt": "2024-01-20T10:00:00Z",
      "modifiedBy": "ETL_ADMIN",
      "modifiedAt": "2024-10-10T14:30:00Z",
      "version": "1.5",
      "packageName": "etl.finance",
      "tags": ["etl", "finance", "load"],
      "sourceObjects": ["ERP_TRANSACTIONS"],
      "targetObjects": ["FINANCIAL_TRANSACTIONS"],
      "transformations": [
        "Currency conversion",
        "Data validation",
        "Duplicate removal"
      ],
      "schedule": {
        "frequency": "Daily",
        "time": "02:00:00",
        "timezone": "UTC"
      },
      "lastRun": {
        "timestamp": "2024-12-04T02:00:00Z",
        "status": "Success",
        "recordsProcessed": 125000,
        "duration": "00:15:32"
      }
    }
  ]
}
```


### Object Types

**Available Object Types**:
- `Table` - Database tables
- `View` - Database views
- `AnalyticalModel` - Analytical models with dimensions/measures
- `DataFlow` - ETL/data integration flows
- `Transformation` - Data transformation logic
- `StoredProcedure` - Stored procedures
- `CalculationView` - Calculation views
- `Hierarchy` - Dimension hierarchies
- `Entity` - Entity definitions
- `Association` - Entity associations

### Common Filter Examples

**Filter by object type**:
```
$filter=objectType eq 'Table'
$filter=objectType eq 'View' or objectType eq 'AnalyticalModel'
```

**Filter by status**:
```
$filter=status eq 'Active'
$filter=deploymentStatus eq 'Deployed'
```

**Filter by space**:
```
$filter=spaceId eq 'SAP_CONTENT'
```

**Filter by owner**:
```
$filter=owner eq 'SYSTEM'
```

**Combine filters**:
```
$filter=objectType eq 'Table' and status eq 'Active' and spaceId eq 'SAP_CONTENT'
```

### Error Responses

| Status Code | Description | Example Response |
|-------------|-------------|------------------|
| 401 | Unauthorized | `{"error": "unauthorized", "message": "Token expired"}` |
| 403 | Forbidden | `{"error": "forbidden", "message": "No repository access"}` |
| 404 | Not Found | `{"error": "not_found", "message": "Space not found"}` |
| 500 | Internal Server Error | `{"error": "internal_error", "message": "Repository service unavailable"}` |

### Use Cases
- Object inventory and cataloging
- Data lineage analysis
- Impact assessment for changes
- Dependency mapping
- Object discovery
- Governance reporting

---

## Tool 2: `get_object_definition`

### Purpose
Get complete design-time object definitions including structure, logic, and metadata.

### API Endpoint Details

**Primary Endpoint**:
```
GET /deepsea/repository/{spaceId}/designobjects/{objectId}
```

**Alternative Endpoint**:
```
GET /deepsea/repository/{spaceId}/objects/{objectId}
```

### Authentication
- **Type**: OAuth2 Bearer Token
- **Required Scopes**: Repository read access

### Path Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `spaceId` | string | Yes | Space identifier | `SAP_CONTENT` |
| `objectId` | string | Yes | Object identifier | `FINANCIAL_TRANSACTIONS` |

### Request Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `$expand` | string | No | Expand related entities | `columns,transformations,dependencies` |
| `includeDefinition` | boolean | No | Include full object definition | `true` |

### Response Format
**Content-Type**: `application/json`

### Expected Response Structure

**For Table Object**:
```json
{
  "id": "FINANCIAL_TRANSACTIONS",
  "objectType": "Table",
  "name": "FINANCIAL_TRANSACTIONS",
  "businessName": "Financial Transactions Table",
  "description": "Core financial transaction data",
  "spaceId": "SAP_CONTENT",
  "status": "Active",
  "deploymentStatus": "Deployed",
  "owner": "SYSTEM",
  "version": "2.1",
  "definition": {
    "type": "Table",
    "columns": [
      {
        "name": "TRANSACTION_ID",
        "technicalName": "TRANSACTION_ID",
        "dataType": "NVARCHAR",
        "length": 50,
        "isPrimaryKey": true,
        "isNullable": false,
        "defaultValue": null,
        "description": "Unique transaction identifier",
        "semanticType": "BusinessKey"
      },
      {
        "name": "ACCOUNT_ID",
        "technicalName": "ACCOUNT_ID",
        "dataType": "NVARCHAR",
        "length": 10,
        "isPrimaryKey": false,
        "isNullable": false,
        "defaultValue": null,
        "description": "Account identifier",
        "semanticType": "ForeignKey",
        "referencedTable": "ACCOUNT_MASTER",
        "referencedColumn": "ACCOUNT_ID"
      },
      {
        "name": "AMOUNT",
        "technicalName": "AMOUNT",
        "dataType": "DECIMAL",
        "precision": 15,
        "scale": 2,
        "isPrimaryKey": false,
        "isNullable": false,
        "defaultValue": 0,
        "description": "Transaction amount",
        "semanticType": "Amount",
        "unit": "Currency"
      },
      {
        "name": "CURRENCY",
        "technicalName": "CURRENCY",
        "dataType": "NVARCHAR",
        "length": 3,
        "isPrimaryKey": false,
        "isNullable": false,
        "defaultValue": "USD",
        "description": "Currency code",
        "semanticType": "CurrencyCode"
      },
      {
        "name": "POSTING_DATE",
        "technicalName": "POSTING_DATE",
        "dataType": "DATE",
        "isPrimaryKey": false,
        "isNullable": false,
        "defaultValue": null,
        "description": "Transaction posting date",
        "semanticType": "Date"
      }
    ],
    "primaryKey": {
      "name": "PK_FINANCIAL_TRANSACTIONS",
      "columns": ["TRANSACTION_ID"]
    },
    "foreignKeys": [
      {
        "name": "FK_ACCOUNT",
        "columns": ["ACCOUNT_ID"],
        "referencedTable": "ACCOUNT_MASTER",
        "referencedColumns": ["ACCOUNT_ID"]
      }
    ],
    "indexes": [
      {
        "name": "IDX_POSTING_DATE",
        "columns": ["POSTING_DATE"],
        "isUnique": false
      },
      {
        "name": "IDX_ACCOUNT_DATE",
        "columns": ["ACCOUNT_ID", "POSTING_DATE"],
        "isUnique": false
      }
    ]
  },
  "dependencies": {
    "upstream": ["SOURCE_SYSTEM_TABLE"],
    "downstream": ["FIN_ANALYTICS_VIEW", "FIN_REPORT_MODEL"]
  },
  "metadata": {
    "rowCount": 15000000,
    "sizeInMB": 2500,
    "lastModified": "2024-11-20T14:22:00Z",
    "partitionKey": "POSTING_DATE",
    "compressionType": "COLUMNAR"
  }
}
```

**For View Object**:
```json
{
  "id": "CUSTOMER_FIN_SUMMARY_VIEW",
  "objectType": "View",
  "name": "CUSTOMER_FINANCIAL_SUMMARY",
  "businessName": "Customer Financial Summary View",
  "description": "Aggregated customer financial data",
  "spaceId": "SAP_CONTENT",
  "status": "Active",
  "deploymentStatus": "Deployed",
  "owner": "FIN_ADMIN",
  "version": "1.3",
  "definition": {
    "type": "View",
    "viewType": "SQL",
    "sqlDefinition": "SELECT \n  c.CUSTOMER_ID,\n  c.CUSTOMER_NAME,\n  SUM(t.AMOUNT) as TOTAL_AMOUNT,\n  COUNT(t.TRANSACTION_ID) as TRANSACTION_COUNT\nFROM CUSTOMER_MASTER c\nLEFT JOIN FINANCIAL_TRANSACTIONS t ON c.CUSTOMER_ID = t.CUSTOMER_ID\nGROUP BY c.CUSTOMER_ID, c.CUSTOMER_NAME",
    "baseTables": [
      "CUSTOMER_MASTER",
      "FINANCIAL_TRANSACTIONS"
    ],
    "columns": [
      {
        "name": "CUSTOMER_ID",
        "dataType": "NVARCHAR",
        "length": 10,
        "sourceTable": "CUSTOMER_MASTER",
        "sourceColumn": "CUSTOMER_ID"
      },
      {
        "name": "CUSTOMER_NAME",
        "dataType": "NVARCHAR",
        "length": 100,
        "sourceTable": "CUSTOMER_MASTER",
        "sourceColumn": "CUSTOMER_NAME"
      },
      {
        "name": "TOTAL_AMOUNT",
        "dataType": "DECIMAL",
        "precision": 15,
        "scale": 2,
        "isCalculated": true,
        "calculation": "SUM(t.AMOUNT)"
      },
      {
        "name": "TRANSACTION_COUNT",
        "dataType": "INTEGER",
        "isCalculated": true,
        "calculation": "COUNT(t.TRANSACTION_ID)"
      }
    ]
  },
  "dependencies": {
    "upstream": ["CUSTOMER_MASTER", "FINANCIAL_TRANSACTIONS"],
    "downstream": ["CUSTOMER_DASHBOARD"]
  }
}
```

**For DataFlow Object**:
```json
{
  "id": "LOAD_FINANCIAL_DATA",
  "objectType": "DataFlow",
  "name": "LOAD_FINANCIAL_DATA",
  "businessName": "Financial Data Load Process",
  "description": "ETL process for loading financial transactions",
  "spaceId": "SAP_CONTENT",
  "status": "Active",
  "deploymentStatus": "Deployed",
  "owner": "ETL_ADMIN",
  "version": "1.5",
  "definition": {
    "type": "DataFlow",
    "sourceConnections": [
      {
        "name": "ERP_SOURCE",
        "connectionType": "SAP_ERP",
        "sourceObject": "BKPF",
        "sourceType": "Table"
      }
    ],
    "targetConnections": [
      {
        "name": "DWH_TARGET",
        "connectionType": "HANA",
        "targetObject": "FINANCIAL_TRANSACTIONS",
        "targetType": "Table",
        "loadType": "Append"
      }
    ],
    "transformations": [
      {
        "step": 1,
        "name": "Filter Active Records",
        "type": "Filter",
        "condition": "STATUS = 'A'"
      },
      {
        "step": 2,
        "name": "Currency Conversion",
        "type": "Transformation",
        "logic": "CONVERT_CURRENCY(AMOUNT, SOURCE_CURRENCY, 'USD', POSTING_DATE)"
      },
      {
        "step": 3,
        "name": "Data Validation",
        "type": "Validation",
        "rules": [
          "AMOUNT > 0",
          "POSTING_DATE IS NOT NULL",
          "CURRENCY IN ('USD', 'EUR', 'GBP')"
        ]
      },
      {
        "step": 4,
        "name": "Duplicate Removal",
        "type": "Deduplication",
        "keyColumns": ["TRANSACTION_ID"]
      }
    ],
    "errorHandling": {
      "onError": "LogAndContinue",
      "errorTable": "ETL_ERROR_LOG",
      "maxErrors": 100
    },
    "schedule": {
      "frequency": "Daily",
      "time": "02:00:00",
      "timezone": "UTC",
      "enabled": true
    }
  },
  "executionHistory": [
    {
      "runId": "run-20241204-020000",
      "startTime": "2024-12-04T02:00:00Z",
      "endTime": "2024-12-04T02:15:32Z",
      "status": "Success",
      "recordsRead": 125000,
      "recordsWritten": 124850,
      "recordsRejected": 150,
      "duration": "00:15:32"
    }
  ]
}
```


### Use Cases
- Understand object structure and logic
- Extract transformation rules
- Analyze SQL definitions
- Document data flows
- Plan migrations
- Impact analysis

---

## Tool 3: `get_deployed_objects`

### Purpose
List runtime/deployed objects that are actively running in the system.

### API Endpoint Details

**Primary Endpoint**:
```
GET /deepsea/repository/{spaceId}/deployedobjects
```

### Authentication
- **Type**: OAuth2 Bearer Token
- **Required Scopes**: Repository read access

### Path Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `spaceId` | string | Yes | Space identifier | `SAP_CONTENT` |

### Request Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `$select` | string | No | Select specific fields | `name,objectType,deploymentStatus` |
| `$filter` | string | No | Filter by criteria | `deploymentStatus eq 'Deployed'` |
| `$top` | integer | No | Limit results | `50` |
| `$skip` | integer | No | Skip results | `0` |
| `$orderby` | string | No | Sort results | `deployedAt desc` |

### Response Format
**Content-Type**: `application/json`

### Expected Response Structure
```json
{
  "@odata.context": "$metadata#deployedobjects",
  "value": [
    {
      "id": "deployed-12345",
      "objectId": "FINANCIAL_TRANSACTIONS",
      "objectType": "Table",
      "name": "FINANCIAL_TRANSACTIONS",
      "businessName": "Financial Transactions Table",
      "spaceId": "SAP_CONTENT",
      "deploymentStatus": "Deployed",
      "deployedBy": "SYSTEM",
      "deployedAt": "2024-01-15T10:30:00Z",
      "version": "2.1",
      "runtimeStatus": "Active",
      "lastAccessed": "2024-12-04T15:30:00Z",
      "accessCount": 15234,
      "runtimeMetrics": {
        "rowCount": 15000000,
        "sizeInMB": 2500,
        "avgQueryTime": "0.25s",
        "queriesPerDay": 1250
      },
      "dependencies": {
        "upstream": ["SOURCE_SYSTEM_TABLE"],
        "downstream": ["FIN_ANALYTICS_VIEW", "FIN_REPORT_MODEL"]
      }
    },
    {
      "id": "deployed-67890",
      "objectId": "LOAD_FINANCIAL_DATA",
      "objectType": "DataFlow",
      "name": "LOAD_FINANCIAL_DATA",
      "businessName": "Financial Data Load Process",
      "spaceId": "SAP_CONTENT",
      "deploymentStatus": "Deployed",
      "deployedBy": "ETL_ADMIN",
      "deployedAt": "2024-01-20T10:00:00Z",
      "version": "1.5",
      "runtimeStatus": "Running",
      "schedule": {
        "frequency": "Daily",
        "nextRun": "2024-12-05T02:00:00Z",
        "lastRun": "2024-12-04T02:00:00Z"
      },
      "lastExecution": {
        "runId": "run-20241204-020000",
        "startTime": "2024-12-04T02:00:00Z",
        "endTime": "2024-12-04T02:15:32Z",
        "status": "Success",
        "recordsProcessed": 125000,
        "duration": "00:15:32",
        "errors": 0
      },
      "runtimeMetrics": {
        "totalRuns": 320,
        "successRate": 99.7,
        "avgDuration": "00:14:25",
        "avgRecordsProcessed": 123500
      }
    },
    {
      "id": "deployed-11111",
      "objectId": "SALES_ANALYTICS_MODEL",
      "objectType": "AnalyticalModel",
      "name": "SALES_ANALYTICS_MODEL",
      "businessName": "Sales Analytics Model",
      "spaceId": "SALES_SPACE",
      "deploymentStatus": "Deployed",
      "deployedBy": "SALES_ADMIN",
      "deployedAt": "2024-02-20T09:15:00Z",
      "version": "3.0",
      "runtimeStatus": "Active",
      "lastAccessed": "2024-12-04T16:45:00Z",
      "accessCount": 8934,
      "runtimeMetrics": {
        "avgQueryTime": "1.2s",
        "queriesPerDay": 450,
        "cacheHitRate": 85.3,
        "dataFreshness": "2024-12-04T02:00:00Z"
      },
      "consumers": [
        "SALES_DASHBOARD",
        "EXECUTIVE_REPORT",
        "POWER_BI_CONNECTOR"
      ]
    }
  ]
}
```

### Deployment Status Values

| Status | Description |
|--------|-------------|
| `Deployed` | Successfully deployed and active |
| `Deploying` | Deployment in progress |
| `Failed` | Deployment failed |
| `Undeployed` | Previously deployed but now removed |
| `Pending` | Waiting for deployment |

### Runtime Status Values

| Status | Description |
|--------|-------------|
| `Active` | Object is active and accessible |
| `Running` | Process is currently executing |
| `Idle` | Object deployed but not currently in use |
| `Error` | Runtime error occurred |
| `Suspended` | Temporarily suspended |

### Common Filter Examples

**Filter by deployment status**:
```
$filter=deploymentStatus eq 'Deployed'
```

**Filter by runtime status**:
```
$filter=runtimeStatus eq 'Active'
```

**Filter by object type**:
```
$filter=objectType eq 'DataFlow'
```

**Filter recently deployed**:
```
$filter=deployedAt gt 2024-11-01T00:00:00Z
```

**Combine filters**:
```
$filter=deploymentStatus eq 'Deployed' and runtimeStatus eq 'Active'
```

### Error Responses

| Status Code | Description | Example Response |
|-------------|-------------|------------------|
| 401 | Unauthorized | `{"error": "unauthorized", "message": "Token expired"}` |
| 403 | Forbidden | `{"error": "forbidden", "message": "No deployment access"}` |
| 404 | Not Found | `{"error": "not_found", "message": "Space not found"}` |
| 500 | Internal Server Error | `{"error": "internal_error", "message": "Deployment service unavailable"}` |

### Use Cases
- Monitor deployed objects
- Track runtime performance
- Identify active data flows
- Monitor execution history
- Capacity planning
- Performance optimization

---

## Implementation Notes

### Object Type Identification

**Categorize Objects**:
```python
OBJECT_TYPE_CATEGORIES = {
    'data_objects': ['Table', 'View', 'Entity'],
    'analytical_objects': ['AnalyticalModel', 'CalculationView', 'Hierarchy'],
    'integration_objects': ['DataFlow', 'Transformation', 'Replication'],
    'logic_objects': ['StoredProcedure', 'Function', 'Script']
}

def categorize_object(object_type):
    for category, types in OBJECT_TYPE_CATEGORIES.items():
        if object_type in types:
            return category
    return 'other'
```

### Dependency Graph Building

**Build Dependency Tree**:
```python
def build_dependency_graph(objects):
    """Build dependency graph from repository objects"""
    graph = {
        'nodes': [],
        'edges': []
    }
    
    # Add nodes
    for obj in objects:
        graph['nodes'].append({
            'id': obj['id'],
            'name': obj['name'],
            'type': obj['objectType']
        })
    
    # Add edges
    for obj in objects:
        if 'dependencies' in obj:
            # Upstream dependencies
            for upstream in obj['dependencies'].get('upstream', []):
                graph['edges'].append({
                    'from': upstream,
                    'to': obj['id'],
                    'type': 'upstream'
                })
            
            # Downstream dependencies
            for downstream in obj['dependencies'].get('downstream', []):
                graph['edges'].append({
                    'from': obj['id'],
                    'to': downstream,
                    'type': 'downstream'
                })
    
    return graph
```

### Impact Analysis

**Analyze Impact of Changes**:
```python
def analyze_impact(object_id, objects):
    """Analyze impact of changing an object"""
    impact = {
        'direct_downstream': [],
        'indirect_downstream': [],
        'total_affected': 0
    }
    
    # Find object
    obj = next((o for o in objects if o['id'] == object_id), None)
    if not obj:
        return impact
    
    # Get direct downstream
    direct = obj.get('dependencies', {}).get('downstream', [])
    impact['direct_downstream'] = direct
    
    # Recursively find indirect downstream
    visited = set([object_id])
    queue = list(direct)
    
    while queue:
        current = queue.pop(0)
        if current in visited:
            continue
        
        visited.add(current)
        impact['indirect_downstream'].append(current)
        
        # Find downstream of current
        current_obj = next((o for o in objects if o['id'] == current), None)
        if current_obj:
            downstream = current_obj.get('dependencies', {}).get('downstream', [])
            queue.extend(downstream)
    
    impact['total_affected'] = len(visited) - 1
    
    return impact
```

### Object Definition Comparison

**Compare Design vs Deployed**:
```python
def compare_design_deployed(design_obj, deployed_obj):
    """Compare design-time and deployed object"""
    comparison = {
        'version_match': design_obj['version'] == deployed_obj['version'],
        'differences': []
    }
    
    # Compare columns (for tables/views)
    if 'columns' in design_obj.get('definition', {}):
        design_cols = {c['name']: c for c in design_obj['definition']['columns']}
        deployed_cols = {c['name']: c for c in deployed_obj.get('definition', {}).get('columns', [])}
        
        # Find added columns
        added = set(design_cols.keys()) - set(deployed_cols.keys())
        if added:
            comparison['differences'].append({
                'type': 'columns_added',
                'columns': list(added)
            })
        
        # Find removed columns
        removed = set(deployed_cols.keys()) - set(design_cols.keys())
        if removed:
            comparison['differences'].append({
                'type': 'columns_removed',
                'columns': list(removed)
            })
        
        # Find modified columns
        for col_name in set(design_cols.keys()) & set(deployed_cols.keys()):
            if design_cols[col_name]['dataType'] != deployed_cols[col_name]['dataType']:
                comparison['differences'].append({
                    'type': 'column_type_changed',
                    'column': col_name,
                    'design_type': design_cols[col_name]['dataType'],
                    'deployed_type': deployed_cols[col_name]['dataType']
                })
    
    return comparison
```


---

## Testing Checklist

### Functional Testing
- ✅ Test listing all repository objects
- ✅ Test filtering by object type
- ✅ Test filtering by status
- ✅ Test pagination for large repositories
- ✅ Test getting object definitions
- ✅ Test with different object types (tables, views, models, flows)
- ✅ Test getting deployed objects
- ✅ Test runtime metrics retrieval
- ✅ Test dependency information
- ✅ Test with empty spaces

### Object Type Testing
- ✅ Test with Table objects
- ✅ Test with View objects
- ✅ Test with AnalyticalModel objects
- ✅ Test with DataFlow objects
- ✅ Test with Transformation objects
- ✅ Test with complex object hierarchies

### Definition Testing
- ✅ Test column definitions
- ✅ Test SQL view definitions
- ✅ Test transformation logic
- ✅ Test foreign key relationships
- ✅ Test index definitions

### Performance Testing
- ✅ Test with large object counts (>1000)
- ✅ Test definition retrieval time
- ✅ Test pagination performance
- ✅ Test concurrent requests

### Integration Testing
- ✅ Test list → get definition workflow
- ✅ Test design vs deployed comparison
- ✅ Test dependency graph building
- ✅ Test impact analysis
- ✅ Test with different user permissions

---

## Object Definition Templates

### Table Definition Template
```json
{
  "type": "Table",
  "columns": [
    {
      "name": "COLUMN_NAME",
      "dataType": "NVARCHAR|INTEGER|DECIMAL|DATE|TIMESTAMP",
      "length": 50,
      "precision": 15,
      "scale": 2,
      "isPrimaryKey": false,
      "isNullable": true,
      "defaultValue": null,
      "description": "Column description",
      "semanticType": "BusinessKey|ForeignKey|Amount|Date"
    }
  ],
  "primaryKey": {
    "name": "PK_TABLE_NAME",
    "columns": ["COLUMN1", "COLUMN2"]
  },
  "foreignKeys": [
    {
      "name": "FK_NAME",
      "columns": ["COLUMN"],
      "referencedTable": "REFERENCED_TABLE",
      "referencedColumns": ["REF_COLUMN"]
    }
  ],
  "indexes": [
    {
      "name": "IDX_NAME",
      "columns": ["COLUMN1", "COLUMN2"],
      "isUnique": false
    }
  ]
}
```

### View Definition Template
```json
{
  "type": "View",
  "viewType": "SQL|Graphical",
  "sqlDefinition": "SELECT ... FROM ... WHERE ...",
  "baseTables": ["TABLE1", "TABLE2"],
  "columns": [
    {
      "name": "COLUMN_NAME",
      "dataType": "NVARCHAR",
      "length": 50,
      "sourceTable": "TABLE1",
      "sourceColumn": "COLUMN",
      "isCalculated": false,
      "calculation": null
    }
  ]
}
```

### DataFlow Definition Template
```json
{
  "type": "DataFlow",
  "sourceConnections": [
    {
      "name": "SOURCE_NAME",
      "connectionType": "SAP_ERP|HANA|S3",
      "sourceObject": "OBJECT_NAME",
      "sourceType": "Table|File"
    }
  ],
  "targetConnections": [
    {
      "name": "TARGET_NAME",
      "connectionType": "HANA",
      "targetObject": "OBJECT_NAME",
      "targetType": "Table",
      "loadType": "Append|Replace|Upsert"
    }
  ],
  "transformations": [
    {
      "step": 1,
      "name": "TRANSFORMATION_NAME",
      "type": "Filter|Transformation|Validation|Deduplication",
      "logic": "TRANSFORMATION_LOGIC"
    }
  ],
  "schedule": {
    "frequency": "Daily|Hourly|Weekly",
    "time": "HH:MM:SS",
    "timezone": "UTC",
    "enabled": true
  }
}
```

---

## Metadata Extraction Guide

### Step 1: List All Objects
```python
# Get all objects in a space
objects = list_repository_objects(
    space_id="SAP_CONTENT",
    top=100
)

# Filter by type
tables = list_repository_objects(
    space_id="SAP_CONTENT",
    filter_expression="objectType eq 'Table'"
)
```

### Step 2: Get Object Definitions
```python
# Get detailed definition
definition = get_object_definition(
    space_id="SAP_CONTENT",
    object_id="FINANCIAL_TRANSACTIONS",
    include_definition=True
)

# Extract column information
columns = definition['definition']['columns']
```

### Step 3: Analyze Dependencies
```python
# Build dependency graph
objects_list = list_repository_objects(space_id="SAP_CONTENT")
dependency_graph = build_dependency_graph(objects_list)

# Analyze impact
impact = analyze_impact("FINANCIAL_TRANSACTIONS", objects_list)
```

### Step 4: Compare Design vs Deployed
```python
# Get design-time objects
design_objects = list_repository_objects(
    space_id="SAP_CONTENT",
    filter_expression="objectType eq 'Table'"
)

# Get deployed objects
deployed_objects = get_deployed_objects(
    space_id="SAP_CONTENT"
)

# Compare
comparison = compare_design_vs_deployed(design_objects, deployed_objects)
```

---

## Helper Functions

### Dependency Graph Builder
```python
def build_dependency_graph(objects_list):
    """Build a dependency graph from repository objects."""
    graph = {}
    
    for obj in objects_list:
        obj_id = obj['id']
        graph[obj_id] = {
            'name': obj['name'],
            'type': obj['objectType'],
            'upstream': obj.get('dependencies', {}).get('upstream', []),
            'downstream': obj.get('dependencies', {}).get('downstream', [])
        }
    
    return graph


def analyze_impact(object_id, objects_list):
    """Analyze impact of changes to an object."""
    graph = build_dependency_graph(objects_list)
    
    if object_id not in graph:
        return {'error': 'Object not found'}
    
    # Find all downstream objects (recursive)
    impacted = set()
    to_process = [object_id]
    
    while to_process:
        current = to_process.pop()
        if current in impacted:
            continue
        
        impacted.add(current)
        downstream = graph.get(current, {}).get('downstream', [])
        to_process.extend(downstream)
    
    return {
        'object_id': object_id,
        'impacted_objects': list(impacted),
        'impact_count': len(impacted)
    }


def categorize_objects(objects_list):
    """Categorize objects by type."""
    categories = {}
    
    for obj in objects_list:
        obj_type = obj['objectType']
        if obj_type not in categories:
            categories[obj_type] = []
        categories[obj_type].append(obj)
    
    return categories
```

---

## Success Criteria

- ✅ Can list all repository object types
- ✅ Can retrieve complete object definitions
- ✅ Can distinguish design-time vs runtime objects
- ✅ Can extract dependency information
- ✅ Can perform impact analysis
- ✅ Can categorize objects by type
- ✅ Proper error handling for all scenarios
- ✅ Pagination works for large object lists

---

## Next Steps

After implementing Phase 3.2:
1. Test with real SAP Datasphere tenant
2. Validate with various object types
3. Test dependency graph building
4. Create usage documentation
5. Proceed to Phase 4: Data Consumption (Analytical)

---

**Document Version**: 1.0  
**Last Updated**: December 9, 2025  
**Related Documents**:
- SAP_DATASPHERE_MCP_EXTRACTION_PLAN.md
- SAP_DATASPHERE_CATALOG_TOOLS_SPEC.md
- SAP_DATASPHERE_METADATA_TOOLS_SPEC.md
# Get design-time definition
design = get_object_definition(
    space_id="SAP_CONTENT",
    object_id="FINANCIAL_TRANSACTIONS"
)

# Get deployed version
deployed = get_deployed_objects(
    space_id="SAP_CONTENT",
    filter_expression="objectId eq 'FINANCIAL_TRANSACTIONS'"
)

# Compare
comparison = compare_design_deployed(design, deployed[0])
```

---

## Schema Documentation Templates

### Object Inventory Template
```markdown
# Repository Object Inventory

## Space: {space_name}

### Summary
- Total Objects: {total_count}
- Tables: {table_count}
- Views: {view_count}
- Analytical Models: {model_count}
- Data Flows: {flow_count}

### Objects by Type

#### Tables
| Name | Description | Columns | Size | Status |
|------|-------------|---------|------|--------|
| {name} | {description} | {column_count} | {size_mb} MB | {status} |

#### Views
| Name | Description | Base Tables | Status |
|------|-------------|-------------|--------|
| {name} | {description} | {base_tables} | {status} |

#### Data Flows
| Name | Description | Schedule | Last Run | Status |
|------|-------------|----------|----------|--------|
| {name} | {description} | {schedule} | {last_run} | {status} |
```

### Object Definition Template
```markdown
# Object Definition: {object_name}

## Overview
- **Type**: {object_type}
- **Space**: {space_name}
- **Owner**: {owner}
- **Version**: {version}
- **Status**: {status}

## Description
{description}

## Structure

### Columns
| Column | Type | Nullable | Key | Description |
|--------|------|----------|-----|-------------|
| {name} | {type} | {nullable} | {is_key} | {description} |

## Dependencies

### Upstream (Sources)
- {upstream_object_1}
- {upstream_object_2}

### Downstream (Consumers)
- {downstream_object_1}
- {downstream_object_2}

## Metadata
- **Created**: {created_at} by {created_by}
- **Modified**: {modified_at} by {modified_by}
- **Row Count**: {row_count}
- **Size**: {size_mb} MB
```

### Dependency Map Template
```markdown
# Dependency Map: {object_name}

## Impact Analysis

### Direct Impact
Objects directly affected by changes to {object_name}:
- {direct_downstream_1}
- {direct_downstream_2}

### Indirect Impact
Objects indirectly affected (downstream of downstream):
- {indirect_downstream_1}
- {indirect_downstream_2}

### Total Affected Objects: {total_count}

## Dependency Chain
```
{object_name}
  ├── {downstream_1}
  │   ├── {downstream_1_1}
  │   └── {downstream_1_2}
  └── {downstream_2}
      └── {downstream_2_1}
```

## Recommendations
- Review all {total_count} affected objects before making changes
- Test changes in development environment first
- Coordinate with owners of downstream objects
```

---

## Next Steps

1. Implement these three repository discovery tools
2. Add dependency graph building
3. Test with various object types
4. Implement impact analysis
5. Create documentation generators
6. Proceed to Phase 4: Data Consumption - Analytical
