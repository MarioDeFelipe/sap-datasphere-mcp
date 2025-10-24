# Architecture Diagram Prompt: SAP-AWS Data Integration Platform with MCP Servers

## Context
Create comprehensive architecture diagrams for an enterprise SAP-to-AWS data integration platform that provides discovery, cataloging, and intelligent data integration capabilities. The platform features AI-powered agents, three-environment architecture (Dog/Wolf/Bear), and Model Context Protocol (MCP) server integration.

## Diagram Requirements

### 1. High-Level Platform Vision Diagram
**Title**: "SAP-AWS Data Integration Platform: Unified Data Access & AI-Powered Integration"

**Components to Include**:
- **SAP Datasphere** (source system with spaces, tables, analytical models)
- **Three-Environment Architecture**:
  - 🐕 DOG Environment (Development - FastAPI Web Dashboard, Port 8001)
  - 🐺 WOLF Environment (Testing - FastAPI with real SAP integration, Port 5000)  
  - 🐻 BEAR Environment (Production - AWS Lambda serverless deployment)
- **MCP Server Layer** (AI-accessible metadata operations)
- **AWS Services** (Glue Data Catalog, S3 Tables, Lambda, QuickSight)
- **Integration Patterns**: Federation, Replication, Direct Query
- **AI Agents** (Integration guidance, pattern recommendations)

**Key Flows to Show**:
- Metadata discovery and cataloging
- Real-time data access via OData APIs
- Automated replication to S3 Tables using Glue ETL
- AI-powered integration pattern recommendations
- Cross-environment deployment pipeline

### 2. Data Access Patterns Architecture
**Title**: "Multi-Modal Data Access: Federation, Replication & Direct Query Patterns"

**Components to Include**:
- **SAP Datasphere Assets**:
  - Analytical Models (business-ready data with dimensions/measures)
  - Tables and Views (operational data)
  - OData Services (consumption-ready APIs)
- **Integration Patterns**:
  - **Federation Pattern**: Real-time queries from AWS to SAP
  - **Replication Pattern**: Data movement to AWS S3 Tables (Apache Iceberg)
  - **Direct Query Pattern**: On-demand access without data movement
- **AWS Analytics Layer**:
  - S3 Tables with Iceberg format
  - Glue Data Catalog with business metadata
  - QuickSight dashboards
  - Athena queries

**Key Flows to Show**:
- Real-time analytical queries via federation
- Batch replication with Glue ETL jobs
- Direct query for occasional access
- Business context preservation across all patterns

### 3. MCP Server Integration Architecture
**Title**: "AI-Accessible Metadata Operations via Model Context Protocol"

**Components to Include**:
- **MCP Server Layer**:
  - Metadata discovery and search
  - Asset cataloging operations
  - Integration pattern recommendations
  - Replication job management
- **AI Agent Integration**:
  - SAP Datasphere expertise agents
  - Integration pattern guidance
  - Automated configuration assistance
- **RAG System Components**:
  - Vector database for metadata embeddings
  - Semantic search capabilities
  - Metadata chatbot interface
- **Enterprise Features**:
  - Audit trails and governance
  - Multi-language business metadata
  - Data lineage tracking

**Key Flows to Show**:
- AI agents accessing metadata via MCP
- Semantic search across vectorized metadata
- Chatbot answering data discovery questions
- Automated integration recommendations

### 4. Replication Pipeline Architecture
**Title**: "Enterprise Data Replication: SAP Datasphere to AWS S3 Tables"

**Components to Include**:
- **Source Layer**: SAP Datasphere OData services
- **Extraction Layer**: 
  - OAuth 2.0 authentication
  - CSDL metadata extraction
  - Paginated data retrieval
- **Processing Layer**:
  - AWS Glue ETL jobs with Spark
  - Apache Iceberg table format
  - Schema evolution and ACID transactions
- **Storage Layer**:
  - S3 Tables with partitioning
  - Glue Data Catalog integration
  - Business metadata preservation
- **Monitoring Layer**:
  - Real-time progress tracking
  - Data validation and quality checks
  - Error handling and retry logic

**Key Flows to Show**:
- End-to-end replication workflow
- Real-time progress monitoring
- Data validation and quality assurance
- Incremental synchronization capabilities

### 5. Three-Environment Deployment Architecture
**Title**: "Multi-Environment Platform: Development, Testing & Production"

**Components to Include**:
- **DOG Environment (Development)**:
  - FastAPI web dashboard (localhost:8001)
  - Hot-reload development capabilities
  - Mock data and API testing
  - Real SAP integration for development
- **WOLF Environment (Testing)**:
  - FastAPI application (localhost:5000)
  - Real Datasphere OAuth integration
  - Integration testing and validation
  - Performance benchmarking
- **BEAR Environment (Production)**:
  - AWS Lambda serverless deployment
  - Auto-scaling and high availability
  - Enterprise monitoring and alerting
  - Public API endpoint for integration

**Key Flows to Show**:
- Environment promotion pipeline
- Configuration management across environments
- Deployment automation and rollback
- Environment-specific security controls

## Visual Design Guidelines

### Color Scheme
- **SAP Systems**: SAP Blue (#0070F2)
- **AWS Services**: AWS Orange (#FF9900)
- **MCP Servers**: Purple (#8B5CF6)
- **Data Flows**: Green (#10B981)
- **AI/ML Components**: Gradient Blue-Purple
- **Security/Auth**: Red (#EF4444)

### Icon Recommendations
- 🏢 SAP Datasphere (building/enterprise icon)
- ☁️ AWS Services (cloud icon)
- 🤖 AI Agents (robot/brain icon)
- 🔄 Data Sync (circular arrows)
- 📊 Analytics (chart/dashboard icon)
- 🔒 Security (lock/shield icon)
- 🐕🐺🐻 Environment indicators

### Layout Suggestions
- **Left-to-Right Flow**: SAP → Processing → AWS
- **Layered Architecture**: UI → API → Processing → Storage
- **Hub-and-Spoke**: MCP servers as central hub
- **Pipeline View**: Sequential processing steps

## Technical Details to Highlight

### Data Formats & Standards
- Apache Iceberg for S3 Tables
- OData v4 for API standards
- CSDL XML for metadata
- Parquet with Snappy compression

### Security & Compliance
- OAuth 2.0 authentication
- AWS IAM role-based access
- End-to-end encryption
- Audit logging and governance

### Performance & Scalability
- Auto-scaling serverless architecture
- Parallel processing capabilities
- Incremental synchronization
- Real-time monitoring

### Business Value Propositions
- Enhanced AI output quality
- Workflow automation
- Up-to-date information access
- Standardized integration patterns

## Output Format Options

### Option 1: Slide Deck (5 slides)
- Slide 1: Platform Vision Overview
- Slide 2: Data Access Patterns
- Slide 3: MCP Server Integration
- Slide 4: Replication Pipeline
- Slide 5: Deployment Architecture

### Option 2: Infographic Series
- Single comprehensive infographic showing all components
- Modular sections that can be used independently
- Executive summary version for stakeholders

### Option 3: Interactive Diagram
- Clickable components with detailed explanations
- Animated data flows showing real-time operations
- Drill-down capabilities for technical details

## Success Criteria

The diagrams should clearly communicate:
1. **Platform Capabilities**: What the system can do
2. **Integration Patterns**: How different access methods work
3. **AI Enhancement**: How MCP servers enable AI-powered operations
4. **Enterprise Readiness**: Security, scalability, and governance features
5. **Business Value**: Why organizations should adopt this platform

## Additional Context

This platform serves as a comprehensive solution for enterprise data integration, providing discovery, cataloging, and intelligent integration between SAP Datasphere and AWS services. The architecture emphasizes AI-powered assistance, multiple integration patterns, and enterprise-grade security and governance.

The target audience includes data engineers, solution architects, enterprise teams, and executives evaluating modern data integration solutions.