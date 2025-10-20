# Configuration Guide

This guide covers all configuration options for the SAP Datasphere to AWS metadata synchronization system, from basic setup to advanced customization.

## 📁 Configuration Files Overview

The system uses several configuration files for different aspects:

```
config/
├── app-config.json              # Main application configuration
├── datasphere-oauth-config.json # SAP Datasphere OAuth settings
├── sync-rules.json             # Custom synchronization rules
└── mapping-config.json         # Asset mapping configurations
```

## ⚙️ Main Application Configuration

### app-config.json

The primary configuration file controls all system behavior:

```json
{
  "datasphere": {
    "config_file": "datasphere-oauth-config.json",
    "enhanced_apis": true,
    "browser_auth": true,
    "api_timeout": 30,
    "retry_attempts": 3,
    "rate_limit_delay": 1.0
  },
  "aws": {
    "region": "us-east-1",
    "profile": null,
    "glue_database_prefix": "datasphere_",
    "enable_lake_formation": true,
    "enable_quicksight": false,
    "enable_datazone": false,
    "tags": {
      "Environment": "production",
      "Source": "datasphere",
      "ManagedBy": "metadata-sync"
    }
  },
  "sync": {
    "incremental_enabled": true,
    "checkpoint_dir": "checkpoints",
    "max_workers": 5,
    "priority_scheduling": true,
    "job_timeout_seconds": 300,
    "retry_delay_seconds": 60,
    "cleanup_after_hours": 24
  },
  "web_dashboard": {
    "host": "0.0.0.0",
    "port": 8000,
    "debug": false,
    "auto_reload": true
  },
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "metadata_sync.log",
    "max_size_mb": 100,
    "backup_count": 5
  }
}
```

### Configuration Sections Explained

#### Datasphere Configuration
- **`config_file`**: Path to OAuth configuration file
- **`enhanced_apis`**: Enable undocumented enhanced APIs for rich metadata
- **`browser_auth`**: Use browser-based authentication for enhanced APIs
- **`api_timeout`**: Request timeout in seconds
- **`retry_attempts`**: Number of retry attempts for failed requests
- **`rate_limit_delay`**: Delay between requests to avoid rate limiting

#### AWS Configuration
- **`region`**: Primary AWS region for resources
- **`profile`**: AWS profile name (null for default)
- **`glue_database_prefix`**: Prefix for created Glue databases
- **`enable_lake_formation`**: Enable Lake Formation integration
- **`enable_quicksight`**: Enable QuickSight dataset creation
- **`enable_datazone`**: Enable DataZone data product creation
- **`tags`**: Default tags applied to all AWS resources

#### Sync Configuration
- **`incremental_enabled`**: Enable incremental synchronization
- **`checkpoint_dir`**: Directory for checkpoint storage
- **`max_workers`**: Maximum concurrent sync jobs
- **`priority_scheduling`**: Enable priority-based job scheduling
- **`job_timeout_seconds`**: Maximum job execution time
- **`retry_delay_seconds`**: Delay between retry attempts
- **`cleanup_after_hours`**: Hours to keep completed job history

## 🔐 SAP Datasphere OAuth Configuration

### datasphere-oauth-config.json

Configure OAuth authentication for SAP Datasphere:

```json
{
  "base_url": "https://your-tenant.datasphere.cloud.sap",
  "client_id": "your_oauth_client_id",
  "client_secret": "your_oauth_client_secret",
  "token_url": "https://your-tenant.authentication.sap.hana.ondemand.com/oauth/token",
  "scope": "uaa.resource",
  "environment": "ailien-test",
  "grant_type": "client_credentials",
  "token_cache_duration": 3600,
  "enhanced_api_endpoints": {
    "deepsea_repository": "/api/v1/deepsea/repository",
    "consumption_analytical": "/api/v1/datasphere/consumption/analytical",
    "metadata_catalog": "/api/v1/catalog/metadata"
  }
}
```

### OAuth Setup Steps

1. **Create OAuth Application in Datasphere**:
   - Navigate to System → Administration → App Integration
   - Create new OAuth2.0 Client Credentials application
   - Note the Client ID and Client Secret

2. **Configure Scopes**:
   - Add required scopes: `uaa.resource`, `consumption.read`, `metadata.read`
   - Enable enhanced API access if available

3. **Test Authentication**:
   ```bash
   python test_oauth_credentials.py
   ```

## 🎯 Synchronization Rules Configuration

### sync-rules.json

Define custom synchronization rules for different asset types:

```json
{
  "rules": [
    {
      "rule_id": "critical_analytical_models",
      "rule_name": "Critical Analytical Models Sync",
      "asset_type": "analytical_model",
      "source_system": "datasphere",
      "target_system": "glue",
      "priority": "critical",
      "frequency": "real_time",
      "conditions": {
        "tags": ["critical", "production", "certified"],
        "name_pattern": ".*_PROD_.*"
      },
      "transformation_rules": ["preserve_business_context", "enhance_descriptions"],
      "is_active": true
    },
    {
      "rule_id": "high_priority_core_tables",
      "rule_name": "High Priority Core Tables",
      "asset_type": "table",
      "source_system": "datasphere",
      "target_system": "glue",
      "priority": "high",
      "frequency": "hourly",
      "conditions": {
        "tags": ["core", "master_data", "critical"],
        "owner": ["data_team", "finance_team"]
      },
      "transformation_rules": ["standardize_naming", "add_governance_tags"],
      "is_active": true
    },
    {
      "rule_id": "medium_priority_data_flows",
      "rule_name": "Medium Priority Data Flows",
      "asset_type": "data_flow",
      "source_system": "datasphere",
      "target_system": "glue",
      "priority": "medium",
      "frequency": "daily",
      "conditions": {
        "tags": ["transformation", "pipeline"]
      },
      "transformation_rules": ["document_lineage", "add_pipeline_metadata"],
      "is_active": true
    }
  ],
  "default_rule": {
    "priority": "medium",
    "frequency": "daily",
    "transformation_rules": ["basic_mapping"]
  }
}
```

### Rule Components

#### Conditions
- **`tags`**: Required tags for rule matching
- **`name_pattern`**: Regex pattern for asset names
- **`owner`**: Asset owner requirements
- **`certification_status`**: Required certification level

#### Transformation Rules
- **`preserve_business_context`**: Maintain business metadata
- **`enhance_descriptions`**: Improve descriptions with AI
- **`standardize_naming`**: Apply naming conventions
- **`add_governance_tags`**: Add compliance tags
- **`document_lineage`**: Create lineage documentation

## 🗺️ Asset Mapping Configuration

### mapping-config.json

Configure how Datasphere assets map to AWS resources:

```json
{
  "space_to_database": {
    "naming_convention": "datasphere_{space_name}_{environment}",
    "description_template": "Datasphere space '{space_name}' synchronized from {source_environment}",
    "default_tags": {
      "Source": "SAP Datasphere",
      "SyncType": "Automated"
    }
  },
  "table_mapping": {
    "naming_convention": "snake_case",
    "preserve_original_name": true,
    "column_mapping": {
      "preserve_business_names": true,
      "add_technical_names": true,
      "data_type_mapping": {
        "String": "string",
        "Integer": "bigint",
        "Decimal": "decimal(18,2)",
        "Date": "date",
        "Boolean": "boolean"
      }
    }
  },
  "analytical_model_mapping": {
    "create_as": "table",
    "include_measures": true,
    "include_dimensions": true,
    "include_hierarchies": true,
    "business_metadata": {
      "preserve_descriptions": true,
      "preserve_tags": true,
      "preserve_steward_info": true
    }
  },
  "view_mapping": {
    "create_as": "external_table",
    "preserve_view_definition": true,
    "include_dependencies": true
  }
}
```

## 🔄 Incremental Sync Configuration

### Advanced Incremental Sync Settings

```json
{
  "incremental_sync": {
    "change_detection": {
      "hash_algorithm": "sha256",
      "content_hash_enabled": true,
      "schema_hash_enabled": true,
      "metadata_hash_enabled": true,
      "ignore_fields": ["last_modified", "sync_timestamp"]
    },
    "checkpoint_management": {
      "storage_type": "json",
      "backup_enabled": true,
      "backup_retention_days": 30,
      "compression_enabled": true
    },
    "sync_strategies": {
      "full_sync_threshold": 0.7,
      "delta_sync_enabled": true,
      "metadata_only_threshold": 0.1,
      "batch_size": 100
    },
    "performance": {
      "parallel_processing": true,
      "max_parallel_jobs": 10,
      "memory_limit_mb": 2048,
      "timeout_minutes": 30
    }
  }
}
```

## 🌍 Environment-Specific Configuration

### Development Environment (DOG)

```json
{
  "environment": "development",
  "datasphere": {
    "base_url": "http://localhost:3000",
    "mock_data": true,
    "enhanced_apis": false
  },
  "aws": {
    "region": "us-east-1",
    "glue_database_prefix": "dev_datasphere_",
    "enable_lake_formation": false
  },
  "sync": {
    "incremental_enabled": false,
    "max_workers": 2
  },
  "web_dashboard": {
    "debug": true,
    "auto_reload": true
  }
}
```

### Testing Environment (WOLF)

```json
{
  "environment": "testing",
  "datasphere": {
    "config_file": "datasphere-oauth-test.json",
    "enhanced_apis": true,
    "browser_auth": true
  },
  "aws": {
    "region": "us-east-1",
    "glue_database_prefix": "test_datasphere_",
    "enable_lake_formation": true
  },
  "sync": {
    "incremental_enabled": true,
    "max_workers": 3,
    "job_timeout_seconds": 180
  }
}
```

### Production Environment (BEAR)

```json
{
  "environment": "production",
  "datasphere": {
    "config_file": "datasphere-oauth-prod.json",
    "enhanced_apis": true,
    "browser_auth": true,
    "rate_limit_delay": 2.0
  },
  "aws": {
    "region": "us-east-1",
    "glue_database_prefix": "datasphere_",
    "enable_lake_formation": true,
    "enable_quicksight": true,
    "enable_datazone": true
  },
  "sync": {
    "incremental_enabled": true,
    "max_workers": 10,
    "priority_scheduling": true,
    "job_timeout_seconds": 600
  },
  "logging": {
    "level": "WARNING",
    "file": "/var/log/metadata-sync/production.log"
  }
}
```

## 🔧 Advanced Configuration Options

### Custom Transformation Rules

Create custom transformation rules in Python:

```python
# custom_transformations.py
from metadata_sync_core import MetadataAsset, TransformationRule

class CustomBusinessContextEnhancer(TransformationRule):
    def apply(self, asset: MetadataAsset) -> MetadataAsset:
        # Add custom business logic
        if asset.asset_type == AssetType.ANALYTICAL_MODEL:
            asset.description = f"[Analytics] {asset.description}"
            asset.business_context.tags.append("analytics-ready")
        return asset

# Register custom rule
CUSTOM_TRANSFORMATION_RULES = {
    "enhance_analytics_context": CustomBusinessContextEnhancer()
}
```

### Environment Variables

Override configuration with environment variables:

```bash
# Datasphere configuration
export DATASPHERE_BASE_URL="https://your-tenant.datasphere.cloud.sap"
export DATASPHERE_CLIENT_ID="your_client_id"
export DATASPHERE_CLIENT_SECRET="your_client_secret"

# AWS configuration
export AWS_REGION="us-east-1"
export AWS_PROFILE="datasphere-sync"
export GLUE_DATABASE_PREFIX="datasphere_"

# Sync configuration
export INCREMENTAL_SYNC_ENABLED="true"
export MAX_SYNC_WORKERS="5"
export CHECKPOINT_DIR="/app/checkpoints"

# Web dashboard
export DASHBOARD_HOST="0.0.0.0"
export DASHBOARD_PORT="8000"
export DASHBOARD_DEBUG="false"
```

## ✅ Configuration Validation

### Validate Configuration

```bash
# Validate all configuration files
python validate_config.py

# Validate specific configuration
python validate_config.py --config app-config.json
python validate_config.py --config datasphere-oauth-config.json
```

### Configuration Test Suite

```bash
# Run configuration tests
python -m pytest tests/test_configuration.py -v

# Test specific configuration aspect
python -m pytest tests/test_configuration.py::test_datasphere_config -v
python -m pytest tests/test_configuration.py::test_aws_config -v
```

## 🚨 Troubleshooting Configuration

### Common Configuration Issues

#### 1. OAuth Authentication Fails
```bash
# Check OAuth configuration
python -c "
import json
with open('datasphere-oauth-config.json') as f:
    config = json.load(f)
    print('✓ Base URL:', config['base_url'])
    print('✓ Token URL:', config['token_url'])
    print('✓ Client ID configured:', bool(config.get('client_id')))
"
```

#### 2. AWS Permissions Error
```bash
# Validate AWS configuration
aws sts get-caller-identity
aws glue get-databases --max-results 1
```

#### 3. Invalid JSON Configuration
```bash
# Validate JSON syntax
python -m json.tool app-config.json
python -m json.tool datasphere-oauth-config.json
```

#### 4. Missing Required Fields
```bash
# Check required configuration fields
python check_required_config.py
```

## 📚 Next Steps

Once configuration is complete:

1. **[Quick Start Guide](./quick-start)** - Run your first synchronization

4. **[Architecture Overview](../architecture/overview)** - Understand the system design

---

🎯 **Configuration Complete!** Your SAP Datasphere to AWS synchronization system is now properly configured. Ready to start syncing? Head to the [Quick Start Guide](./quick-start)!