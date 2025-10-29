# SAP Datasphere MCP Server - Improvements Plan

**Goal:** Align the SAP Datasphere MCP Server with Anthropic's 2025 best practices for production-ready, secure, and user-friendly MCP servers.

**Timeline:** Phased approach over 3 sprints

---

## 📋 Overview

This plan addresses gaps identified in our MCP server implementation compared to Anthropic's latest best practices (March 2025 specification). Focus areas include security, user experience, tool design quality, and production readiness.

---

## 🎯 Phase 1: Security & Authentication (High Priority)

**Duration:** Sprint 1 (2 weeks)
**Objective:** Make the server secure and production-ready

### 1.1 Implement Real OAuth 2.0 Authentication

**Current State:** Mock OAuth with hardcoded config
**Target State:** Full OAuth 2.0 client credentials flow with SAP Datasphere

**Tasks:**
- [ ] Create `auth/oauth_handler.py` module
  - Implement token acquisition via client credentials grant
  - Add automatic token refresh logic
  - Implement secure token storage (memory-based, encrypted)
  - Add token expiration monitoring

- [ ] Update `enhanced_datasphere_connector.py`
  - Integrate OAuth handler
  - Add connection health checks
  - Implement retry logic with exponential backoff
  - Add OAuth error handling

- [ ] Remove mock data flag and hardcoded credentials
  - Delete `use_mock_data` configuration
  - Remove hardcoded tenant IDs from source
  - Update tests to use real test environment

**Files to Modify:**
- `sap_datasphere_mcp_server.py` (remove mock config)
- `enhanced_datasphere_connector.py` (add OAuth integration)
- New: `auth/oauth_handler.py`
- `start_mcp_server.py` (add OAuth initialization)

**Success Criteria:**
- ✅ Server connects to real SAP Datasphere instance
- ✅ OAuth tokens acquired and refreshed automatically
- ✅ All API calls use authenticated requests
- ✅ No credentials in source code

---

### 1.2 Implement Consent & Authorization Flows

**Current State:** No user authorization or consent mechanisms
**Target State:** User must approve sensitive operations

**Best Practice Reference:**
> "Users need transparent understanding of all data access and operations, with maintained authority over what information is shared and which actions execute."

**Tasks:**
- [ ] Create authorization framework
  - Define tool permission levels (READ, WRITE, ADMIN)
  - Implement permission checker middleware
  - Add consent prompts for sensitive operations

- [ ] Categorize tools by risk level
  ```python
  TOOL_PERMISSIONS = {
      "list_spaces": "READ",
      "search_tables": "READ",
      "get_table_schema": "READ",
      "execute_query": "WRITE",  # Requires consent
      "list_connections": "ADMIN",  # Requires admin consent
  }
  ```

- [ ] Add consent prompts before execution
  - Create consent dialog system
  - Log all consent decisions
  - Allow users to revoke permissions

- [ ] Implement data filtering based on permissions
  - Filter sensitive fields from responses
  - Redact connection strings and credentials
  - Mask PII data in query results

**Files to Create:**
- `auth/authorization.py`
- `auth/consent_manager.py`
- `auth/data_filter.py`

**Files to Modify:**
- `sap_datasphere_mcp_server.py` (add permission checks)

**Success Criteria:**
- ✅ Sensitive operations require explicit user consent
- ✅ Permission levels enforced for all tools
- ✅ Audit log tracks all authorization decisions
- ✅ Sensitive data filtered from responses

---

### 1.3 Add Input Validation & SQL Sanitization

**Current State:** Raw SQL queries accepted without validation
**Security Risk:** SQL injection, prompt injection

**Tasks:**
- [ ] Create input validator module
  - Validate all tool parameters
  - Implement SQL query parser and validator
  - Add allowlist for SQL operations (SELECT only)
  - Block dangerous SQL patterns (DROP, DELETE, UPDATE)

- [ ] Implement SQL sanitization
  ```python
  class SQLValidator:
      ALLOWED_OPERATIONS = ["SELECT"]
      BLOCKED_KEYWORDS = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER"]

      def validate_query(self, query: str) -> tuple[bool, str]:
          # Parse and validate SQL
          # Return (is_valid, error_message)
  ```

- [ ] Add parameter type validation
  - Validate space_id format
  - Validate table_name patterns
  - Limit query result sizes
  - Add rate limiting per user

**Files to Create:**
- `validation/input_validator.py`
- `validation/sql_validator.py`

**Files to Modify:**
- `sap_datasphere_mcp_server.py` (add validation calls)

**Success Criteria:**
- ✅ All inputs validated before processing
- ✅ SQL injection attempts blocked
- ✅ Only SELECT queries allowed
- ✅ Clear error messages for invalid inputs

---

### 1.4 Externalize Configuration

**Current State:** Hardcoded tenant IDs and config in source code
**Target State:** Environment-based configuration

**Tasks:**
- [ ] Create configuration management system
  ```python
  # config/settings.py
  class Settings(BaseSettings):
      datasphere_base_url: str
      datasphere_tenant_id: str
      oauth_client_id: str
      oauth_client_secret: SecretStr
      oauth_token_url: str

      class Config:
          env_file = ".env"
          env_file_encoding = "utf-8"
  ```

- [ ] Add environment variable support
  - Create `.env.example` template
  - Document all configuration options
  - Add validation for required settings

- [ ] Update server initialization
  - Load config from environment
  - Validate config on startup
  - Fail fast with clear error messages

**Files to Create:**
- `config/settings.py`
- `.env.example`
- `config/config_validator.py`

**Files to Modify:**
- `sap_datasphere_mcp_server.py` (load config)
- `start_mcp_server.py` (initialize config)
- `README.md` (document configuration)

**Success Criteria:**
- ✅ No credentials in source code
- ✅ Config loaded from environment variables
- ✅ Clear documentation for all settings
- ✅ Validation errors on missing config

---

## 🎨 Phase 2: Tool Design & User Experience (Medium Priority)

**Duration:** Sprint 2 (1-2 weeks)
**Objective:** Improve tool quality and usability

### 2.1 Enhance Tool Descriptions

**Current State:** Basic functional descriptions
**Target State:** Comprehensive descriptions with usage context

**Best Practice Reference:**
> "Write clear, concise, and comprehensive tool descriptions, explaining not just what the tool does but **when to use it**, including parameter-by-parameter documentation."

**Tasks:**
- [ ] Rewrite all tool descriptions with context

  **Before:**
  ```python
  description="List all Datasphere spaces with their status and metadata"
  ```

  **After:**
  ```python
  description="""List all SAP Datasphere spaces with their status and metadata.

  Use this tool when you need to:
  - Discover what data spaces are available in the system
  - Check the status of spaces before querying their contents
  - Get an overview of the Datasphere environment

  Best for: Initial exploration and space discovery.
  Next steps: Use 'get_space_info' for detailed information about a specific space.

  Parameters:
  - include_details: Set to true to include full metadata (owner, counts, dates).
    Use false for a quick list of space names and IDs."""
  ```

- [ ] Add usage examples to each tool
  ```python
  Tool(
      name="search_tables",
      description="...",
      inputSchema={...},
      examples=[
          {
              "search_term": "customer",
              "description": "Find all tables related to customers"
          },
          {
              "search_term": "sales",
              "space_id": "SALES_ANALYTICS",
              "description": "Search for sales tables in specific space"
          }
      ]
  )
  ```

- [ ] Document relationships between tools
  - Create tool usage flowcharts
  - Add "See also" references in descriptions
  - Document common tool combinations

**Files to Modify:**
- `sap_datasphere_mcp_server.py` (update all tool descriptions)
- New: `docs/TOOL_GUIDE.md` (comprehensive tool documentation)

**Success Criteria:**
- ✅ All tools have "when to use" context
- ✅ Parameter documentation explains purpose
- ✅ Usage examples provided for each tool
- ✅ Tool relationships documented

---

### 2.2 Implement Prompts Primitive

**Current State:** No prompts defined
**Target State:** Common query patterns as reusable prompts

**Best Practice Reference:**
> "Prompts (user-controlled)" are one of the three MCP primitives

**Tasks:**
- [ ] Add prompt handler to server
  ```python
  @server.list_prompts()
  async def handle_list_prompts() -> list[types.Prompt]:
      return [
          types.Prompt(
              name="analyze_space_structure",
              description="Analyze the structure and contents of a Datasphere space",
              arguments=[
                  types.PromptArgument(
                      name="space_id",
                      description="ID of the space to analyze",
                      required=True
                  )
              ]
          ),
          # More prompts...
      ]
  ```

- [ ] Create common prompt templates
  - **analyze_space_structure**: Comprehensive space analysis
  - **compare_tables**: Compare schemas between tables
  - **data_quality_check**: Check data freshness and quality
  - **explore_relationships**: Find table relationships
  - **generate_query**: Help user build SQL queries

- [ ] Implement prompt execution handler
  ```python
  @server.get_prompt()
  async def handle_get_prompt(name: str, arguments: dict) -> types.GetPromptResult:
      # Return prompt template with arguments filled in
  ```

**Files to Create:**
- `prompts/prompt_templates.py`
- `prompts/prompt_handler.py`

**Files to Modify:**
- `sap_datasphere_mcp_server.py` (add prompt handlers)

**Success Criteria:**
- ✅ At least 5 useful prompts defined
- ✅ Prompts accept dynamic arguments
- ✅ Prompts guide users through common tasks
- ✅ Prompt templates documented

---

### 2.3 Improve Error Handling

**Current State:** Generic error messages
**Target State:** Actionable error messages with suggestions

**Tasks:**
- [ ] Create error response templates
  ```python
  class ErrorResponse:
      def not_found(self, resource_type: str, resource_id: str, available: list) -> str:
          return f"""
          {resource_type} '{resource_id}' not found.

          Available {resource_type}s:
          {self._format_list(available)}

          Suggestion: Use 'list_{resource_type}s' to see all available options.
          """
  ```

- [ ] Add contextual suggestions to errors
  - Include valid alternatives
  - Suggest corrective actions
  - Link to relevant tools

- [ ] Implement error categorization
  - Authentication errors
  - Authorization errors
  - Validation errors
  - Data not found errors
  - System errors

- [ ] Add error logging and monitoring
  - Log all errors with context
  - Track error patterns
  - Alert on critical errors

**Files to Create:**
- `errors/error_handler.py`
- `errors/error_templates.py`

**Files to Modify:**
- `sap_datasphere_mcp_server.py` (use error handler)

**Success Criteria:**
- ✅ All errors include actionable suggestions
- ✅ Error messages guide users to solutions
- ✅ Errors categorized by type
- ✅ Error logging implemented

---

### 2.4 Separate Mock Data from Production Code

**Current State:** Large mock data structures in main server file
**Target State:** Clean separation of test fixtures

**Tasks:**
- [ ] Create test fixtures module
  ```
  tests/
  ├── fixtures/
  │   ├── __init__.py
  │   ├── mock_spaces.py
  │   ├── mock_tables.py
  │   ├── mock_connections.py
  │   └── mock_tasks.py
  ```

- [ ] Implement data layer abstraction
  ```python
  class DataProvider(ABC):
      @abstractmethod
      async def get_spaces(self) -> list[Space]:
          pass

  class MockDataProvider(DataProvider):
      # Uses test fixtures

  class DatasphereDataProvider(DataProvider):
      # Connects to real API
  ```

- [ ] Update server to use data providers
  - Inject data provider at initialization
  - Remove hardcoded MOCK_DATA dictionary
  - Make switching between mock/real transparent

**Files to Create:**
- `data/data_provider.py` (abstract interface)
- `data/mock_provider.py` (mock implementation)
- `data/datasphere_provider.py` (real implementation)
- `tests/fixtures/` (test data)

**Files to Modify:**
- `sap_datasphere_mcp_server.py` (use data providers)
- `test_mcp_server.py` (use fixtures)

**Success Criteria:**
- ✅ Mock data removed from main server file
- ✅ Clean data layer abstraction
- ✅ Easy switching between mock/real data
- ✅ Test fixtures organized and reusable

---

## 🚀 Phase 3: Advanced Features & Polish (Low Priority)

**Duration:** Sprint 3 (1 week)
**Objective:** Production-grade features and monitoring

### 3.1 Add Server Capability Declarations

**Tasks:**
- [ ] Implement server info endpoint
- [ ] Declare server capabilities clearly
- [ ] Add version information
- [ ] Document supported features

**Files to Modify:**
- `sap_datasphere_mcp_server.py`

---

### 3.2 Implement Caching Strategies

**Tasks:**
- [ ] Cache frequently accessed metadata
- [ ] Implement cache invalidation
- [ ] Add cache TTL configuration
- [ ] Monitor cache hit rates

**Files to Create:**
- `cache/cache_manager.py`

---

### 3.3 Add Performance Monitoring

**Tasks:**
- [ ] Track tool execution times
- [ ] Monitor API call latency
- [ ] Log performance metrics
- [ ] Add health check endpoint

**Files to Create:**
- `monitoring/metrics.py`
- `monitoring/health_check.py`

---

## 📊 Implementation Priority Matrix

| Task | Priority | Security Impact | User Impact | Effort |
|------|----------|----------------|-------------|---------|
| OAuth 2.0 Authentication | HIGH | Critical | High | Medium |
| Authorization Flows | HIGH | Critical | High | Medium |
| Input Validation | HIGH | Critical | Medium | Low |
| Externalize Config | HIGH | High | Low | Low |
| Enhanced Tool Descriptions | MEDIUM | None | High | Low |
| Prompts Primitive | MEDIUM | None | High | Medium |
| Better Error Handling | MEDIUM | None | High | Low |
| Separate Mock Data | MEDIUM | None | Low | Medium |
| Server Capabilities | LOW | None | Low | Low |
| Caching | LOW | None | Medium | Medium |
| Performance Monitoring | LOW | None | Low | Medium |

---

## 🔄 Implementation Approach

### Sprint 1: Security Foundation (Week 1-2)
1. Externalize configuration (1 day)
2. Implement OAuth 2.0 (3 days)
3. Add authorization flows (2 days)
4. Input validation & SQL sanitization (2 days)
5. Testing & documentation (2 days)

### Sprint 2: User Experience (Week 3-4)
1. Enhance tool descriptions (2 days)
2. Implement Prompts primitive (3 days)
3. Improve error handling (2 days)
4. Separate mock data (2 days)
5. Testing & documentation (1 day)

### Sprint 3: Production Ready (Week 5)
1. Server capabilities (1 day)
2. Caching implementation (2 days)
3. Performance monitoring (1 day)
4. Final testing & polish (1 day)

---

## 📝 Documentation Updates Required

1. **README.md**
   - Update configuration instructions
   - Document OAuth setup process
   - Add security considerations section

2. **MCP_SETUP_GUIDE.md**
   - Update with new configuration steps
   - Add troubleshooting section
   - Document permission system

3. **New: SECURITY.md**
   - Document security model
   - Explain authorization flows
   - List security best practices

4. **New: TOOL_GUIDE.md**
   - Comprehensive tool documentation
   - Usage examples and patterns
   - Tool relationship diagrams

---

## ✅ Success Metrics

### Phase 1 (Security)
- [ ] Zero hardcoded credentials in codebase
- [ ] OAuth token refresh success rate > 99%
- [ ] All sensitive operations require consent
- [ ] SQL injection tests pass 100%
- [ ] Configuration validation coverage 100%

### Phase 2 (UX)
- [ ] All tools have comprehensive descriptions
- [ ] At least 5 useful prompts implemented
- [ ] Error messages include actionable suggestions
- [ ] Mock data removed from production code
- [ ] Tool usage documentation complete

### Phase 3 (Production)
- [ ] Server capabilities properly declared
- [ ] Cache hit rate > 80% for metadata
- [ ] Performance metrics tracked
- [ ] Health check endpoint functional
- [ ] Production deployment guide complete

---

## 🎯 Definition of Done

Each phase is complete when:
1. All tasks implemented and tested
2. Unit test coverage > 80%
3. Integration tests passing
4. Documentation updated
5. Security review completed
6. Code review approved
7. Deployed to staging environment
8. User acceptance testing passed

---

## 📞 Support & Questions

For questions about this plan:
- Review the MCP specification: https://modelcontextprotocol.io/specification/2025-03-26
- Check Anthropic best practices
- Consult with security team on authorization flows

---

**Last Updated:** 2025-10-29
**Status:** Ready for Implementation
**Next Review:** After Phase 1 completion
