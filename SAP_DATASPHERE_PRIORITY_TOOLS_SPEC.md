# SAP Datasphere MCP Server - Priority Tools Specification

## Overview

This document provides complete technical specifications for implementing **5 high-priority advanced feature tools** that enable data sharing, AI monitoring, and configuration management for SAP Datasphere.

**Selected Tools**: 5 priority tools from Phase 8  
**Focus Areas**: Data Sharing, AI Features, Configuration Management  
**Estimated Implementation Time**: 2-3 days  
**Business Value**: HIGH

---

# PRIORITY TOOL 1: `list_partner_systems`

## Purpose
Discover partner systems and external data products available through data sharing partnerships.

## API Endpoint
```
GET /deepsea/catalog/v1/dataProducts/partners/systems
```

## Authentication
- **Type**: OAuth2 Bearer Token
- **Scopes**: `DWC_DATA_SHARING` or equivalent data sharing scope

## Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `$select` | string | No | Comma-separated list of properties to return |
| `$filter` | string | No | Filter expression |
| `$expand` | string | No | Related entities to expand |
| `$top` | integer | No | Maximum results (default: 50, max: 1000) |
| `$skip` | integer | No | Results to skip for pagination |
| `partnerType` | string | No | Filter by partner type |

## Response Format
```json
{
  "@odata.context": "$metadata#partnerSystems",
  "value": [
    {
      "id": "partner-system-12345",
      "name": "External Analytics Partner",
      "partnerType": "Data Provider",
      "status": "Active",
      "connectionStatus": "Connected",
      "description": "External analytics data provider for market intelligence",
      "dataProducts": [
        {
          "id": "dp-market-data-001",
          "name": "Market Intelligence Dataset",
          "category": "Market Data",
          "description": "Comprehensive market analysis data",
          "lastUpdated": "2024-12-01T10:30:00Z"
        }
      ],
      "capabilities": [
        "Real-time Data Streaming",
        "Batch Data Export",
        "API Integration"
      ],
      "contactInfo": {
        "organization": "Market Data Corp",
        "email": "partnerships@marketdata.com",
        "website": "https://marketdata.com"
      },
      "sharingAgreement": {
        "type": "Commercial",
        "status": "Active",
        "expiryDate": "2025-12-31T23:59:59Z"
      },
      "lastSync": "2024-12-09T08:00:00Z",
      "dataVolume": "2.5TB",
      "refreshFrequency": "Daily"
    }
  ],
  "summary": {
    "totalPartners": 15,
    "activePartners": 12,
    "dataProviders": 8,
    "dataConsumers": 4,
    "totalDataProducts": 45
  }
}
```

## Business Value
- **Partnership Management**: Discover and manage data sharing relationships
- **Data Discovery**: Find external data sources for enrichment
- **Compliance**: Track data sharing agreements and status
- **Integration Planning**: Assess partner capabilities and data volumes

---

# PRIORITY TOOL 2: `get_data_product_details`

## Purpose
Get detailed information about a specific data product including metadata, installation status, and access details.

## API Endpoint
```
GET /dwaas-core/odc/dataProduct/{productId}/details
```

## Authentication
- **Type**: OAuth2 Bearer Token
- **Scopes**: `DWC_DATA_PRODUCTS` or equivalent data product access scope

## Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `productId` | string | Yes | Data product identifier |
| `includeInstallation` | boolean | No | Include installation details |
| `includeMetadata` | boolean | No | Include detailed metadata |
| `includeAccess` | boolean | No | Include access permissions |

## Response Format
```json
{
  "id": "f55b20ae-152d-40d4-b2eb-70b651f85d37",
  "name": "Global Country Identifier Data by DCA",
  "displayName": "Global Country Identifier Data",
  "description": "Comprehensive country identifier dataset with ISO codes, names, and regional classifications",
  "provider": "Data Crafting Assets by SAP",
  "category": "Reference Data",
  "type": "Dataset",
  "version": "2.1.0",
  "status": "Active",
  "installation": {
    "status": "Installed",
    "installedAt": "2024-11-15T09:30:00Z",
    "installedBy": "admin@company.com",
    "space": "SAP_CONTENT",
    "lastUpdated": "2024-12-01T08:00:00Z",
    "autoUpdate": true,
    "updateSchedule": "Weekly"
  },
  "metadata": {
    "dataFormat": "Structured",
    "fileFormat": ["CSV", "Parquet"],
    "size": "2.5MB",
    "recordCount": 249,
    "columns": [
      {
        "name": "COUNTRY_CODE_ISO2",
        "type": "String",
        "description": "ISO 3166-1 alpha-2 country code"
      },
      {
        "name": "COUNTRY_CODE_ISO3",
        "type": "String", 
        "description": "ISO 3166-1 alpha-3 country code"
      },
      {
        "name": "COUNTRY_NAME",
        "type": "String",
        "description": "Official country name"
      },
      {
        "name": "REGION",
        "type": "String",
        "description": "Geographic region"
      }
    ],
    "updateFrequency": "Quarterly",
    "dataRange": "Current",
    "coverage": "Global - 249 countries and territories"
  },
  "access": {
    "permissions": ["READ", "QUERY", "EXPORT"],
    "restrictions": [],
    "accessLevel": "Full",
    "sharedWith": ["FINANCE_ANALYTICS", "SALES_ANALYTICS"],
    "accessCount": 156,
    "lastAccessed": "2024-12-09T09:45:00Z"
  },
  "usage": {
    "queryCount": 1247,
    "exportCount": 23,
    "popularQueries": [
      "SELECT * WHERE REGION = 'Europe'",
      "SELECT COUNTRY_CODE_ISO2, COUNTRY_NAME"
    ],
    "topUsers": [
      {"user": "analyst@company.com", "queries": 89},
      {"user": "finance@company.com", "queries": 67}
    ]
  },
  "support": {
    "documentation": "https://help.sap.com/data-products/country-identifiers",
    "supportEmail": "dataproducts@sap.com",
    "releaseNotes": "https://help.sap.com/releases/country-identifiers",
    "knownIssues": []
  }
}
```

## Business Value
- **Data Product Management**: Track installation and usage of data products
- **Usage Analytics**: Understand data product utilization patterns
- **Access Control**: Monitor and manage data product permissions
- **Data Governance**: Ensure proper data product lifecycle management

---

# PRIORITY TOOL 3: `get_ai_feature_status`

## Purpose
Monitor the execution status of AI features and machine learning models with real-time status information.

## API Endpoint
```
GET /dwaas-core/api/v1/aifeatures/{aiFeatureId}/executable/status
```

## Authentication
- **Type**: OAuth2 Bearer Token
- **Scopes**: `DWC_AI_FEATURES` or equivalent AI monitoring scope

## Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `aiFeatureId` | string | Yes | AI feature identifier |
| `detailed` | boolean | No | Include detailed metrics |
| `includeMetrics` | boolean | No | Include performance metrics |
| `historyDepth` | integer | No | Days of history to include (default: 7) |

## Response Format
```json
{
  "aiFeatureId": "ai-feature-sentiment-analysis",
  "name": "Sentiment Analysis Model",
  "type": "Machine Learning Model",
  "status": "Running",
  "health": "Healthy",
  "lastUpdated": "2024-12-09T10:30:00Z",
  "execution": {
    "currentState": "Active",
    "startedAt": "2024-12-09T08:00:00Z",
    "uptime": "2h 30m",
    "processedRequests": 1247,
    "successRate": 98.5,
    "averageResponseTime": "125ms",
    "lastExecution": "2024-12-09T10:29:45Z"
  },
  "resources": {
    "cpuUsage": 45.2,
    "memoryUsage": 67.8,
    "gpuUsage": 23.1,
    "storageUsage": "2.3GB"
  },
  "model": {
    "version": "2.1.0",
    "framework": "TensorFlow",
    "accuracy": 94.2,
    "trainingDate": "2024-11-15T00:00:00Z",
    "datasetSize": "1.2M samples",
    "modelSize": "450MB"
  },
  "metrics": {
    "daily": [
      {
        "date": "2024-12-09",
        "requests": 1247,
        "successRate": 98.5,
        "avgResponseTime": 125,
        "errors": 19
      },
      {
        "date": "2024-12-08", 
        "requests": 1156,
        "successRate": 97.8,
        "avgResponseTime": 132,
        "errors": 25
      }
    ],
    "trends": {
      "requestVolume": "Increasing",
      "performance": "Stable",
      "errorRate": "Decreasing"
    }
  },
  "alerts": [
    {
      "type": "Performance",
      "severity": "Low",
      "message": "Response time slightly above average",
      "timestamp": "2024-12-09T10:15:00Z"
    }
  ],
  "configuration": {
    "batchSize": 32,
    "timeout": 30000,
    "retryAttempts": 3,
    "scalingPolicy": "Auto"
  }
}
```

## Business Value
- **AI Operations**: Monitor AI/ML model performance and health
- **Performance Optimization**: Track resource usage and response times
- **Predictive Maintenance**: Early detection of model degradation
- **Cost Management**: Monitor resource consumption and scaling

---

# PRIORITY TOOL 4: `get_guided_experience_config`

## Purpose
Retrieve tenant-specific configuration for the Data Warehouse Cloud guided experience and UI customization.

## API Endpoint
```
GET /dwaas-core/configurations/DWC_GUIDED_EXPERIENCE_TENANT
```

## Authentication
- **Type**: OAuth2 Bearer Token
- **Scopes**: `DWC_CONFIG_READ` or equivalent configuration access scope

## Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `includeDefaults` | boolean | No | Include default configuration values |
| `configVersion` | string | No | Specific configuration version |

## Response Format
```json
{
  "configurationId": "DWC_GUIDED_EXPERIENCE_TENANT",
  "tenantId": "tenant-12345",
  "version": "2.4.1",
  "lastUpdated": "2024-11-20T14:30:00Z",
  "updatedBy": "admin@company.com",
  "guidedExperience": {
    "enabled": true,
    "welcomeTour": {
      "enabled": true,
      "autoStart": false,
      "skipForExistingUsers": true,
      "steps": [
        {
          "id": "welcome",
          "title": "Welcome to SAP Datasphere",
          "description": "Get started with your data journey"
        },
        {
          "id": "spaces",
          "title": "Explore Spaces",
          "description": "Learn about data spaces and organization"
        },
        {
          "id": "catalog",
          "title": "Discover Data",
          "description": "Browse the data catalog and assets"
        }
      ]
    },
    "contextualHelp": {
      "enabled": true,
      "showTooltips": true,
      "showHints": true,
      "helpPanelPosition": "right"
    },
    "onboarding": {
      "showGettingStarted": true,
      "showQuickActions": true,
      "showRecommendations": true,
      "personalizedContent": true
    }
  },
  "userInterface": {
    "theme": "sap_horizon",
    "compactMode": false,
    "language": "en",
    "dateFormat": "MM/DD/YYYY",
    "timeFormat": "12h",
    "timezone": "UTC",
    "accessibility": {
      "highContrast": false,
      "screenReader": false,
      "keyboardNavigation": true
    }
  },
  "features": {
    "dataBuilder": {
      "enabled": true,
      "advancedMode": false,
      "autoSave": true,
      "collaborativeEditing": true
    },
    "businessBuilder": {
      "enabled": true,
      "templateLibrary": true,
      "customTemplates": true
    },
    "analytics": {
      "enabled": true,
      "advancedAnalytics": true,
      "predictiveAnalytics": false,
      "customVisualizations": true
    },
    "dataIntegration": {
      "enabled": true,
      "realtimeStreaming": false,
      "batchProcessing": true,
      "cloudConnectors": true
    }
  },
  "notifications": {
    "email": {
      "enabled": true,
      "frequency": "Daily",
      "types": ["System Updates", "Data Refresh", "Errors"]
    },
    "inApp": {
      "enabled": true,
      "showBadges": true,
      "autoMarkRead": false
    }
  },
  "security": {
    "sessionTimeout": 3600,
    "mfaRequired": false,
    "passwordPolicy": "Standard",
    "auditLogging": true
  },
  "customization": {
    "logo": {
      "enabled": false,
      "url": null
    },
    "colors": {
      "primary": "#0070f2",
      "secondary": "#6c757d"
    },
    "branding": {
      "companyName": "Your Company",
      "showSAPBranding": true
    }
  }
}
```

## Business Value
- **User Experience Optimization**: Customize UI for better user adoption
- **Training & Onboarding**: Configure guided experiences for new users
- **Feature Management**: Control which features are available to users
- **Branding & Compliance**: Customize interface to match corporate standards

---

# PRIORITY TOOL 5: `get_security_config_status`

## Purpose
Monitor the status of flexible HANA security configurations for customer-managed HANA instances.

## API Endpoint
```
GET /dwaas-core/security/customerhana/flexible-configuration/configuration-status
```

## Authentication
- **Type**: OAuth2 Bearer Token
- **Scopes**: `DWC_SECURITY_ADMIN` or equivalent security monitoring scope

## Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `includeDetails` | boolean | No | Include detailed configuration |
| `configType` | string | No | Filter by configuration type |
| `validationLevel` | string | No | Validation level (Basic, Standard, Strict) |

## Response Format
```json
{
  "configurationId": "hana-security-config-001",
  "tenantId": "tenant-12345",
  "status": "Active",
  "lastValidated": "2024-12-09T06:00:00Z",
  "validationResult": "Compliant",
  "overallSecurityScore": 87.5,
  "configurations": {
    "authentication": {
      "status": "Configured",
      "method": "SAML",
      "mfaEnabled": true,
      "passwordPolicy": {
        "minLength": 12,
        "complexity": "High",
        "expiration": 90,
        "history": 12
      },
      "sessionManagement": {
        "timeout": 3600,
        "maxConcurrentSessions": 3,
        "idleTimeout": 1800
      }
    },
    "authorization": {
      "status": "Configured",
      "roleBasedAccess": true,
      "principleOfLeastPrivilege": true,
      "regularAccessReview": true,
      "privilegedAccounts": {
        "count": 5,
        "lastReview": "2024-11-15T00:00:00Z",
        "nextReview": "2025-02-15T00:00:00Z"
      }
    },
    "dataProtection": {
      "status": "Configured",
      "encryptionAtRest": true,
      "encryptionInTransit": true,
      "keyManagement": "Customer Managed",
      "dataClassification": true,
      "sensitiveDataMasking": true,
      "backupEncryption": true
    },
    "networkSecurity": {
      "status": "Configured",
      "firewallEnabled": true,
      "vpnRequired": true,
      "ipWhitelisting": true,
      "allowedIpRanges": ["192.168.1.0/24", "10.0.0.0/16"],
      "sslCertificate": {
        "status": "Valid",
        "expiryDate": "2025-06-15T00:00:00Z",
        "issuer": "Internal CA"
      }
    },
    "auditing": {
      "status": "Configured",
      "auditLogging": true,
      "logRetention": 365,
      "realTimeMonitoring": true,
      "alerting": true,
      "complianceReporting": true,
      "logIntegrity": true
    }
  },
  "complianceStatus": {
    "frameworks": [
      {
        "name": "SOC 2 Type II",
        "status": "Compliant",
        "lastAssessment": "2024-10-15T00:00:00Z",
        "nextAssessment": "2025-04-15T00:00:00Z"
      },
      {
        "name": "GDPR",
        "status": "Compliant",
        "lastAssessment": "2024-09-30T00:00:00Z",
        "nextAssessment": "2025-03-30T00:00:00Z"
      }
    ]
  },
  "vulnerabilities": {
    "critical": 0,
    "high": 1,
    "medium": 3,
    "low": 7,
    "lastScan": "2024-12-08T02:00:00Z",
    "nextScan": "2024-12-15T02:00:00Z"
  },
  "recommendations": [
    {
      "priority": "Medium",
      "category": "Access Control",
      "description": "Review and update privileged account access",
      "dueDate": "2025-01-15T00:00:00Z"
    },
    {
      "priority": "Low",
      "category": "Monitoring",
      "description": "Enable additional audit log categories",
      "dueDate": "2025-02-01T00:00:00Z"
    }
  ]
}
```

## Business Value
- **Security Compliance**: Monitor compliance with security frameworks (SOC 2, GDPR)
- **Risk Management**: Track vulnerabilities and security risks
- **Audit Support**: Provide comprehensive security reporting
- **Proactive Security**: Get recommendations for security improvements

---

## Implementation Priorities

### High Priority (Implement First)
1. **`get_data_product_details`** - Critical for data product management
2. **`get_security_config_status`** - Essential for compliance and security

### Medium Priority
3. **`get_ai_feature_status`** - Important for AI/ML operations
4. **`get_guided_experience_config`** - Valuable for user experience

### Lower Priority
5. **`list_partner_systems`** - Useful for data sharing scenarios

---

## Common Implementation Patterns

### OAuth2 Token Management
```python
class OAuth2TokenManager:
    """Manage OAuth2 token lifecycle with automatic refresh."""
    
    async def get_token(self) -> str:
        """Get valid access token, refreshing if necessary."""
        if self.access_token and self.token_expiry and self.token_expiry > datetime.now():
            return self.access_token
        return await self.refresh_token()
```

### Error Handling Strategy
```python
def handle_http_error(error: httpx.HTTPStatusError, context: str) -> str:
    """Handle HTTP errors with context-specific messages."""
    status_code = error.response.status_code
    
    if status_code == 401:
        return f"Authentication failed for {context}. Check OAuth2 credentials."
    elif status_code == 403:
        return f"Access forbidden for {context}. Check user permissions and scopes."
    elif status_code == 404:
        return f"Resource not found for {context}. Verify identifiers and availability."
    # ... additional error handling
```

---

## Success Criteria

- ✅ Can discover and analyze partner systems and data products
- ✅ Can retrieve detailed data product information and usage analytics
- ✅ Can monitor AI feature status and performance metrics
- ✅ Can retrieve and analyze guided experience configuration
- ✅ Can assess security configuration compliance and generate recommendations
- ✅ Proper error handling for all scenarios
- ✅ Performance acceptable for typical usage

---

## Next Steps

1. **Implement Priority Tools**: Start with `get_data_product_details` and `get_security_config_status`
2. **Test with Real Tenant**: Validate all endpoints with actual SAP Datasphere
3. **Performance Benchmark**: Test response times and resource usage
4. **Create Usage Examples**: Document common scenarios and workflows
5. **Integration Testing**: Validate cross-tool workflows

---

**Document Version**: 1.0  
**Last Updated**: December 11, 2025  
**Related Documents**:
- SAP_DATASPHERE_ADVANCED_TOOLS_SPEC.md (complete Phase 8 specification)
- MCP_ADVANCED_TOOLS_GENERATION_PROMPT.md (implementation guide)
- PHASE_8_API_RESEARCH_PLAN.md (API research results)