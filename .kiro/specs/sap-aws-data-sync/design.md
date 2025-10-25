# Design Document

## Overview

The SAP Datasphere to AWS Glue metadata synchronization system implements a three-environment architecture with MCP server integration to provide comprehensive metadata management across development, testing, and production environments. The system focuses on preserving business context while enabling AWS analytics capabilities on Datasphere data assets.

## Architecture

### Three-Environment Architecture

#### 🐕 DOG Environment (Development)
- **Technology**: Docker containerized Flask application
- **Port**: 8000
- **Purpose**: Development and prototyping with mock data
- **Features**: 
  - API Explorer for metadata operations
  - Mock Datasphere and Glue data for testing
  - Hot-reload development capabilities
  - Interactive debugging tools
- **Access**: http://localhost:8000
- **Use Case**: Safe development environment for building and testing sync logic

#### 🐺 WOLF Environment (Testing)
- **Technology**: FastAPI application with real integrations
- **Port**: 5000
- **Purpose**: Integration testing with live SAP Datasphere
- **Features**:
  - OAuth 2.0 authentication to Datasphere (ailien-test environment)
  - Real metadata extraction and analysis
  - AWS Glue integration testing
  - Performance benchmarking
- **Access**: http://localhost:5000
- **Use Case**: Validate sync operations with real data before production deployment

#### 🐻 BEAR Environment (Production)
- **Technology**: AWS Lambda serverless deployment
- **Location**: AWS Cloud (us-east-1 region)
- **Purpose**: Enterprise-grade production metadata synchronization
- **Features**:
  - Auto-scaling serverless architecture
  - Public API endpoint for enterprise integration
  - Production monitoring and alerting
  - High availability and disaster recovery
- **Access**: https://krb7735xufadsj233kdnpaabta0eatck.lambda-url.us-east-1.on.aws
- **Deployment**: Automated via `python deploy.py` from datasphere-control-panel folder

### MCP Server Integration

The system exposes metadata operations through Model Context Protocol (MCP) servers, enabling AI-powered metadata management and discovery.

## Components and Interfaces

### Core Components

#### 1. Metadata Sync Engine
- **Responsibility**: Core synchronization logic and orchestration
- **Key Functions**:
  - Asset discovery and classification
  - Priority-based synchronization scheduling
  - Conflict detection and resolution
  - Business context preservation

#### 2. Datasphere Connector
- **Responsibility**: SAP Datasphere API integration
- **Key Functions**:
  - OAuth 2.0 authentication and token management
  - Metadata extraction from spaces, tables, views, and analytical models
  - Business context and lineage information retrieval
  - Real-time change detection

#### 3. AWS Glue Connector
- **Responsibility**: AWS Glue Data Catalog integration
- **Key Functions**:
  - IAM-based authentication
  - Database and table creation/updates
  - Schema mapping and data type conversion
  - Partition and metadata management

#### 4. MCP Server Interface
- **Responsibility**: AI-accessible metadata operations
- **Key Functions**:
  - Unified metadata search across platforms
  - Business context-aware data discovery
  - Synchronization status and monitoring
  - Configuration management

### Asset Mapping Strategy

#### Datasphere → AWS Glue Mappings

| Datasphere Asset | AWS Glue Equivalent | Mapping Strategy | Business Value |
|------------------|---------------------|------------------|----------------|
| Space | Database | 1:1 with naming convention `datasphere_{space_name}_{env}` | Organizational structure |
| Table | Table | Direct schema mapping with type conversion | Core data access |
| Analytical Model | Table + Business Metadata | Business-ready consumption layer | Analytics enablement |
| View | External Table | View definition preservation | Logical data access |
| Data Flow | Job Metadata | Lineage and transformation tracking | Pipeline documentation |

#### Priority-Based Synchronization

1. **Critical Priority** (Real-time/Hourly):
   - Analytical Models (business-ready data)
   - Core Tables (master data)
   - Security and permissions

2. **High Priority** (Daily):
   - Views and calculated views
   - Business metadata updates
   - Data lineage information

3. **Medium Priority** (Weekly):
   - Data flows and transformations
   - Performance statistics
   - Usage analytics

## Data Models

### Metadata Asset Model
```python
class MetadataAsset:
    asset_id: str
    asset_type: AssetType  # TABLE, VIEW, ANALYTICAL_MODEL, SPACE
    source_system: str     # DATASPHERE, GLUE
    business_name: str
    technical_name: str
    description: str
    owner: str
    created_date: datetime
    modified_date: datetime
    sync_status: SyncStatus
    business_context: BusinessContext
    lineage: List[LineageRelationship]
```

### Synchronization Configuration Model
```python
class SyncConfiguration:
    source_environment: str
    target_environment: str
    sync_frequency: SyncFrequency
    priority_level: PriorityLevel
    conflict_resolution: ConflictStrategy
    field_mappings: Dict[str, str]
    transformation_rules: List[TransformationRule]
```

## Error Handling

### Error Categories

1. **Authentication Errors**
   - OAuth token expiration
   - Invalid credentials
   - Permission denied

2. **Schema Conflicts**
   - Data type mismatches
   - Column name conflicts
   - Constraint violations

3. **Business Logic Errors**
   - Naming convention violations
   - Missing required metadata
   - Circular dependencies

### Error Resolution Strategies

- **Automatic Retry**: Transient network and authentication errors
- **Conflict Logging**: Schema and naming conflicts for manual review
- **Fallback Modes**: Degraded functionality during partial failures
- **Alert Generation**: Critical errors requiring immediate attention

## Testing Strategy

### Development Testing (DOG Environment)
- Unit tests with mock data
- API endpoint validation
- Configuration testing
- Error handling verification

### Integration Testing (WOLF Environment)
- End-to-end sync workflows
- Real Datasphere connectivity
- AWS Glue integration validation
- Performance benchmarking

### Production Testing (BEAR Environment)
- Load testing and scalability
- Disaster recovery procedures
- Security penetration testing
- Compliance validation

## Performance Considerations

### Optimization Strategies
- **Incremental Sync**: Only sync changed metadata
- **Batch Processing**: Group operations for efficiency
- **Caching**: Cache frequently accessed metadata
- **Parallel Processing**: Concurrent sync operations where possible

### Monitoring and Metrics
- Sync operation latency
- Error rates by asset type
- Business impact assessment
- Resource utilization tracking