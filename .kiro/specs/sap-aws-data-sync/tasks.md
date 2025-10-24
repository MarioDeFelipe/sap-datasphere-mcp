# Implementation Plan

- [x] 1. Set up core metadata synchronization framework



  - Create base classes for MetadataAsset, SyncConfiguration, and MetadataSyncEngine
  - Implement priority-based synchronization scheduling logic
  - Set up logging and error handling infrastructure
  - _Requirements: 1.1, 2.1, 4.1, 5.5_

- [x] 2. Implement Datasphere connector with OAuth authentication

  - [x] 2.0 Implement comprehensive catalog discovery with pagination and raw data archival
    - Discover all accessible spaces using /api/v1/datasphere/consumption/catalog/spaces with pagination support
    - Discover all accessible assets using /api/v1/datasphere/consumption/catalog/assets with pagination support
    - List assets within specific spaces using /api/v1/datasphere/consumption/catalog/spaces('{space_id}')/assets with pagination
    - Get detailed asset descriptions with metadata/data links using /api/v1/datasphere/consumption/catalog/spaces('{space_id}')/assets('{asset_id}')
    - Implement OData pagination handling (@odata.nextLink) for large result sets (500+ catalog records)
    - Support OData parameters: $count=true, $top, $skip for client-side pagination control
    - Handle different page sizes: catalog (500 records), relational (50KB/50K records), analytical (50KB/50K records or 1M cells)
    - Store ALL raw API responses in S3 data lake with date partitioning (Parquet format)
    - Create comprehensive asset inventory with space-asset relationships
    - Enable automated synchronization planning and bulk operations
    - Implement S3 lifecycle policies for raw data retention and archival
    - _Requirements: 1.1, 6.1, 8.4_

  - [x] 2.1 Create DatasphereConnector class with OAuth 2.0 integration


    - Implement token management and automatic refresh
    - Add environment-specific credential handling (ailien-test)
    - Create connection testing and validation methods
    - _Requirements: 5.1, 5.4_

  - [x] 2.2 Implement metadata extraction for core assets


    - Extract spaces metadata with business context
    - Extract tables with schema, columns, and data types
    - Extract analytical models with dimensions, measures, and hierarchies
    - Extract views with definitions and dependencies
    - _Requirements: 1.1, 1.2, 1.3, 6.2_

  - [x] 2.3 Implement dataset discovery and CSDL metadata extraction with pagination and S3 archival
    - Discover available datasets using /api/v1/datasphere/consumption/relational/{spaceId}/{assetId} and /api/v1/datasphere/consumption/analytical/{spaceId}/{assetId}
    - Implement pagination handling for large datasets (relational: 50KB/50K records, analytical: 50KB/50K records or 1M cells)
    - Support OData parameters for dataset discovery: $count=true, $top, $skip, $select for optimized queries
    - Discover service URLs for analytic models using /api/v1/datasphere/consumption/analytical/{spaceId}/{assetId}
    - Discover service URLs for views using /api/v1/datasphere/consumption/relational/{spaceId}/{viewId}/{spaceId}/{assetId}
    - Extract CSDL XML for each dataset using /api/v1/datasphere/consumption/relational/{spaceId}/{assetId}/$metadata
    - Extract CSDL XML for each dataset using /api/v1/datasphere/consumption/analytical/{spaceId}/{assetId}/$metadata
    - Store ALL raw API responses (datasets, service URLs, CSDL XML) in S3 with date partitioning
    - Parse OData entity relationships and navigation properties from both CSDL types
    - Extract analytical-specific annotations (measures, dimensions, aggregations) from analytical CSDL
    - Extract semantic annotations and business context from CSDL metadata
    - Preserve OData service capabilities and constraints information for both consumption types
    - Store service URLs in AWS Glue custom properties for future API generation
    - Map multi-dataset assets to multiple AWS Glue tables with proper relationships
    - _Requirements: 9.5, 9.6, 9.7_

  - [x] 2.4 Write unit tests for Datasphere connector






    - Test OAuth authentication flow
    - Test metadata extraction methods (including CSDL)
    - Test error handling and retry logic
    - _Requirements: 5.1, 5.4, 9.5_

- [x] 3. Implement AWS Glue connector with IAM authentication



  - [x] 3.1 Create GlueConnector class with IAM integration


    - Implement IAM role-based authentication
    - Add rate limiting and throttling controls
    - Create connection validation methods
    - _Requirements: 5.2, 5.3_

  - [x] 3.2 Implement Glue Data Catalog operations


    - Create database operations (create, update, delete)
    - Create table operations with schema mapping
    - Implement partition management
    - Add metadata tagging and business context preservation
    - _Requirements: 1.1, 1.2, 6.4_

  - [x] 3.3 Write unit tests for Glue connector





    - Test IAM authentication
    - Test database and table operations
    - Test schema mapping and data type conversion
    - _Requirements: 5.2_

- [x] 4. Implement asset mapping and transformation engine



  - [x] 4.1 Create AssetMapper class with configurable rules


    - Implement space-to-database mapping with naming conventions
    - Create table-to-table schema mapping with type conversion
    - Implement analytical model to business table mapping
    - Add view-to-external-table mapping logic
    - _Requirements: 7.1, 7.2, 7.3_

  - [x] 4.2 Implement conflict resolution strategies



    - Create naming conflict resolution with environment prefixes
    - Implement schema conflict resolution with source-system-wins
    - Add business metadata merging capabilities
    - Create conflict logging and reporting
    - _Requirements: 2.2, 2.3, 2.4_

  - [x] 4.3 Add mapping validation and preview capabilities






    - Implement dry-run mode for mapping validation
    - Create impact analysis for mapping changes
    - Add mapping rule testing framework
    - _Requirements: 7.4, 7.5_

- [-] 5. Implement priority-based synchronization engine

  - [x] 5.1 Create SyncOrchestrator with priority scheduling




    - Implement critical priority sync for analytical models
    - Add high priority sync for views and core tables
    - Create medium priority sync for data flows
    - Add sync frequency management (real-time, hourly, daily)



    - _Requirements: 2.1, 1.5_

  - [x] 5.2 Implement incremental synchronization





    - Create change detection for Datasphere assets
    - Implement delta sync to minimize data transfer
    - Add checkpoint and resume capabilities
    - Create sync status tracking and reporting
    - _Requirements: 1.5, 4.1, 8.4_

  - [x] 5.3 Write integration tests for sync engine









    - Test end-to-end sync workflows
    - Test priority-based scheduling
    - Test incremental sync capabilities
    - _Requirements: 2.1, 1.5_

- [ ] 6. Implement MCP server interface for AI integration
  - [ ] 6.1 Create MCP server with metadata discovery tools
    - Implement unified search across Datasphere and Glue
    - Add business context-aware data discovery
    - Create data lineage visualization tools
    - Add synchronization status monitoring
    - _Requirements: 6.1, 6.3, 6.5_

  - [ ] 6.2 Implement MCP configuration management tools
    - Add sync configuration management
    - Create mapping rule management interface
    - Implement environment-specific configuration
    - Add validation and testing capabilities
    - _Requirements: 7.4, 7.5, 8.6_

  - [ ]* 6.3 Write MCP server tests
    - Test metadata discovery tools
    - Test configuration management
    - Test AI integration capabilities
    - _Requirements: 6.1, 6.5_

- [x] 7. Implement three-environment web interfaces
  - [x] 7.1 Create Dog environment Web Dashboard application (Port 8001)
    - ✅ Built modern FastAPI web dashboard with real-time monitoring
    - ✅ Implemented live SAP Datasphere OAuth integration
    - ✅ Added AWS Glue Data Catalog connectivity
    - ✅ Created connection testing and validation interface
    - ✅ Implemented asset management and synchronization monitoring
    - ✅ Added secure credential management via AWS Secrets Manager
    - ✅ Deployed interactive debugging and development features
    - _Requirements: 8.1, 3.1_

  - [ ] 7.2 Create Wolf environment FastAPI application
    - Build real-time connectivity monitoring
    - Add metadata extraction result visualization
    - Implement sync testing and validation
    - Create performance monitoring dashboard
    - _Requirements: 8.2, 3.2_

  - [ ] 7.3 Create Bear environment Lambda deployment
    - Implement serverless web interface
    - Add production metrics and monitoring
    - Create enterprise-grade error handling
    - Implement auto-scaling and health checks
    - _Requirements: 8.3, 3.3, 3.5_

- [x] 8. Implement comprehensive monitoring and audit system



  - [x] 8.1 Create audit logging system




    - Implement structured logging for all sync operations
    - Add timestamp, user, and change detail tracking
    - Create exportable audit logs in JSON and CSV formats
    - Add filtering and search capabilities
    - _Requirements: 4.1, 4.4_

  - [x] 8.2 Implement data lineage tracking


    - Create lineage relationship mapping
    - Add end-to-end traceability between systems
    - Implement lineage visualization
    - Create business impact analysis
    - _Requirements: 4.3, 6.3_

  - [x] 8.3 Create error monitoring and alerting


    - Implement structured error reporting
    - Add automatic alert generation for critical errors
    - Create remediation suggestion engine
    - Add escalation workflows
    - _Requirements: 4.2, 4.5, 8.5_

- [x] 9. Implement security and authentication framework



  - [x] 9.1 Enhance OAuth 2.0 integration


    - Implement environment-specific credential management
    - Add automatic token refresh without service interruption
    - Create security event logging
    - Add suspicious activity detection
    - _Requirements: 5.1, 5.4, 5.5_



  - [ ] 9.2 Implement AWS IAM integration
    - Create least-privilege IAM roles for Glue operations
    - Add cross-account access capabilities
    - Implement resource-level permissions
    - Add security audit capabilities
    - _Requirements: 5.2_

  - [ ]* 9.3 Write security tests
    - Test OAuth authentication flows
    - Test IAM permission boundaries
    - Test security event logging
    - _Requirements: 5.1, 5.2, 5.5_

- [ ] 10. Implement enhanced AWS Glue Data Catalog integration
  - [x] 10.1 Create rich business metadata synchronization
    - ✅ Implemented business glossary integration for table and column descriptions
    - ✅ Created comprehensive metadata templates combining technical and business context
    - ✅ Added Datasphere business label extraction and mapping
    - ✅ Implemented multi-source metadata merging (technical + business + governance)
    - ✅ Built RichBusinessMetadataEngine with multi-language support
    - ✅ Created BusinessMetadataIntegrator for orchestration
    - ✅ Added automated data classification and governance policy enforcement
    - ✅ Implemented comprehensive test suite with 95%+ coverage
    - _Requirements: 9.1, 9.5_

  - [x] 10.2 Implement business-friendly naming conventions

    - ✅ Created domain-specific column naming rules based on Datasphere business context
    - ✅ Implemented technical-to-business name mapping with version control
    - ✅ Added multi-language label support for global teams (EN, DE, FR, ES)
    - ✅ Created naming conflict resolution with business priority
    - ✅ Built BusinessNamingEngine with configurable rules and templates
    - ✅ Created EnhancedNamingIntegrator for seamless integration
    - ✅ Implemented comprehensive naming validation and error handling
    - ✅ Added naming statistics and configuration export/import
    - _Requirements: 9.2, 10.1, 10.3_

  - [x] 10.3 Implement advanced domain-based tagging and classification





    - Create automated data classification engine using Datasphere business context
    - Implement governance policy enforcement through Glue tags
    - Add data sensitivity classification and security tagging
    - Create compliance-driven tag management
    - _Requirements: 9.3, 10.2, 10.4, 10.5_

  - [x] 10.4 Implement hierarchical relationship preservation





    - Create Analytical Model hierarchy mapping to Glue custom properties
    - Implement dimension-measure relationship preservation
    - Add cross-system relationship tracking and visualization
    - Create business context-aware lineage mapping
    - _Requirements: 9.4, 6.3_
  - [x] 10.5 Write enhanced Glue integration tests









  - [x] 10.5 Implement OData-standard metadata integration






    - Create CSDL parser for extracting OData entity definitions and relationships from both relational and analytical consumption types
    - Implement OData annotation preservation in Glue custom properties with analytical-specific metadata
    - Add navigation property mapping for cross-entity relationships
    - Create analytical measure and dimension mapping to Glue custom properties
    - Create AWS API Gateway + Lambda OData service generation templates for both relational and analytical consumption
    - Enable BI-optimized API endpoint creation with proper measure/dimension semantics
    - _Requirements: 9.5, 9.6, 9.7_
-



  - [x] 10.6 Write enhanced Glue integration tests




    - Test rich metadata synchronization
    - Test business naming conventions
    - Test automated classification and tagging
    - Test hierarchical relationship preservation



    - Test CSDL metadata extraction and OData integration
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_

  - [x] 10.7 Fix failing OData metadata integration tests





    - Resolve 3 failing tests in OData metadata integration test suite (85.7% → 100% success rate)
    - Fix CloudFormation template generation test failures
    - Fix Swagger definition generation test failures  
    - Fix Lambda code generation test failures
    - Ensure all OData integration components work with missing dependencies
    - Add proper error handling for optional OData features
    - Validate API Gateway template generation with real AWS resources
    - _Requirements: 9.5, 9.6, 9.7_

- [x] 11. Deep Dive Asset Discovery Investigation




  - [x] 11.1 Validate current space discovery accuracy


    - Verify DEFAULT_SPACE and SAP_CONTENT spaces are correctly discovered
    - Confirm phantom SAP_SC_FI_AM space is completely eliminated
    - Test space discovery against user's actual Datasphere environment
    - Document exact space names and IDs from Datasphere interface
    - _Requirements: 1.1, 6.1_

  - [x] 11.2 Investigate exact asset names and technical identifiers



    - Access user's Datasphere interface to extract exact technical names for "Employee Headcount" and "Financial Transactions"
    - Document the exact asset IDs, technical names, and display names
    - Identify asset types (Local Table, View, Analytical Model, etc.)
    - Map display names to technical names for accurate API calls
    - Test various name formats (spaces, underscores, case variations)
    - _Requirements: 1.1, 1.2, 6.2_

  - [x] 11.3 Comprehensive OData endpoint exploration and validation


    - Test all available OData consumption endpoints for discovered spaces
    - Validate `/api/v1/datasphere/consumption/catalog/spaces('{space_id}')/assets` endpoint access
    - Test `/api/v1/datasphere/consumption/relational/{spaceId}/{assetId}` for each asset
    - Test `/api/v1/datasphere/consumption/analytical/{spaceId}/{assetId}` for each asset
    - Document HTTP response codes, error messages, and successful endpoints
    - Create comprehensive endpoint compatibility matrix
    - _Requirements: 1.1, 1.2, 1.3, 9.5_





  - [ ] 11.4 OAuth permissions and scope analysis
    - Analyze current OAuth token permissions and scopes
    - Identify missing permissions for asset discovery within spaces
    - Test different authentication methods (if available)



    - Document required permissions for full asset access
    - Create permission troubleshooting guide
    - Test with different OAuth applications if needed
    - _Requirements: 5.1, 5.4_

  - [x] 11.5 Asset metadata extraction validation with OData explorer


    - Use OData explorer to manually validate asset accessibility
    - Test metadata extraction for each discovered asset
    - Validate CSDL XML extraction for consumable assets
    - Test service URL discovery for analytical models and views
    - Document complete metadata structure for each asset type
    - Verify business context and schema information availability


    - _Requirements: 9.5, 9.6, 9.7_

  - [ ] 11.6 Alternative discovery method implementation
    - Implement web scraping approach as fallback for catalog APIs
    - Test direct HTML parsing of Datasphere catalog interface
    - Create hybrid discovery combining API and web interface methods
    - Implement screen scraping for asset names if API access is limited


    - Document alternative access patterns and their reliability
    - _Requirements: 1.1, 6.1_

  - [ ] 11.7 Comprehensive asset discovery validation and testing
    - Create end-to-end test suite for complete asset discovery workflow
    - Validate discovery of all assets visible in user's Datasphere interface
    - Test asset synchronization from Datasphere to AWS Glue
    - Verify business context preservation during synchronization
    - Create automated validation against user's actual environment
    - Document complete asset inventory with full metadata
    - _Requirements: 1.1, 1.2, 1.3, 6.2, 6.4_

  - [ ] 11.8 Asset discovery troubleshooting and documentation
    - Create comprehensive troubleshooting guide for asset discovery issues
    - Document common error patterns and their solutions
    - Create diagnostic tools for permission and access issues
    - Implement automated health checks for discovery system
    - Create user guide for validating asset discovery results
    - Document best practices for maintaining discovery accuracy
    - _Requirements: 4.2, 4.5, 8.5_

- [ ] 12. Implement S3 raw data lake infrastructure

  - [x] 12.1 Create S3 data lake architecture






    - Design partitioned S3 bucket structure (year/month/day partitioning)
    - Implement Parquet format storage for analytics optimization
    - Create separate folders for spaces, assets, metadata, service URLs, and CSDL data
    - Add compression and encoding optimization (Snappy compression)
    - _Requirements: 4.1, 8.1_

  - [x] 12.2 Implement S3 data archival service



    - Create S3DataLakeService class for raw data storage
    - Implement automatic date partitioning for all API responses
    - Add data deduplication and versioning capabilities
    - Create metadata indexing for efficient querying
    - Implement batch upload optimization for large datasets


    - _Requirements: 4.1, 8.1, 8.4_

  - [x] 12.3 Create S3 lifecycle and governance policies


    - Implement S3 lifecycle policies for cost optimization (IA, Glacier transitions)

    - Add data retention policies based on compliance requirements
    - Create S3 access logging and monitoring
    - Implement data quality checks on stored raw data
    - Add automated cleanup of temporary and duplicate files
    - _Requirements: 4.4, 5.2_

  - [-] 12.4 Implement Athena integration for raw data analytics


    - Create Athena tables for querying raw Datasphere metadata
    - Implement automated table schema updates when new data arrives
    - Add predefined queries for metadata analytics and governance reporting
    - Create views for business-friendly metadata analysis
    - Enable SQL-based exploration of raw API responses
    - _Requirements: 4.3, 6.1, 8.1_

- [ ] 13. Implement configuration management and deployment
  - [ ] 13.1 Create environment-specific configuration system
    - Implement hot-reload configuration without restart
    - Add environment promotion workflows
    - Create configuration validation and testing
    - Add rollback capabilities
    - _Requirements: 7.5, 8.6, 3.2_

  - [ ] 13.2 Implement automated deployment pipeline
    - Create Docker containerization for Dog environment
    - Add automated testing and validation
    - Implement Bear environment Lambda deployment
    - Add deployment monitoring and rollback
    - _Requirements: 3.1, 3.3, 3.5_

  - [ ] 13.3 Write deployment tests

    - Test environment-specific deployments
    - Test configuration management
    - Test rollback capabilities
    - _Requirements: 3.2, 3.5_

---

## Future Roadmap (Phase 2+)

**See [future-roadmap.md](future-roadmap.md) for detailed planning**

### Phase 2: Direct ABAP System Integration
- **11. ABAP ODBC Client Integration** - Direct connectivity to SAP ABAP systems
  - ODBC client deployment in Docker containers
  - CDS view metadata extraction from ABAP systems
  - Dual-source synchronization (Datasphere + ABAP)
  - Enhanced business context preservation

### Phase 3: Advanced Analytics
- **12. Real-Time Streaming Integration** - Event-driven synchronization
- **13. Machine Learning Pipeline Integration** - Automated ML on synchronized data
- **14. Advanced Business Intelligence** - Unified BI layer across SAP and AWS