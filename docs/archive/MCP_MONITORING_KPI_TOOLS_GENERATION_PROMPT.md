# MCP Tool Generation Prompt - Phase 6 & 7: KPI Management + System Monitoring

## Context

You are implementing **10 monitoring and KPI management tools** for the SAP Datasphere MCP Server. These tools enable business intelligence, system administration, and operational monitoring.

**Reference Document**: `SAP_DATASPHERE_MONITORING_KPI_TOOLS_SPEC.md`

---

## Implementation Requirements

### Framework & Standards
- **Framework**: Standard MCP (not FastMCP)
- **Python Version**: 3.10+
- **Package Manager**: uv
- **Linting**: Ruff (99 char line length, Google docstrings, single quotes)
- **Type Hints**: Full type annotations required
- **Return Format**: MCP TextContent with JSON strings

### Project Structure
```
src/sap-datasphere-mcp-server/
├── tools/
│   ├── kpi_management.py      # NEW: KPI tools (3 tools)
│   ├── system_monitoring.py   # NEW: System monitoring (4 tools)
│   └── user_management.py     # NEW: User management (3 tools)
```

---

## PHASE 6: KPI MANAGEMENT TOOLS (3 tools)

### Tool 1: search_kpis

```python
from mcp.types import Tool, TextContent
import httpx
import json
from typing import Optional

# Tool definition
search_kpis_tool = Tool(
    name="search_kpis",
    description="Search and discover KPIs using advanced query syntax with scope-based filtering",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string", 
                "description": "Search terms (will be prefixed with KPI scope)"
            },
            "facets": {
                "type": "string",
                "description": "Comma-separated facets (objectType,spaceId,category)"
            },
            "top": {"type": "integer", "default": 50, "maximum": 500},
            "skip": {"type": "integer", "default": 0},
            "include_count": {"type": "boolean", "default": False}
        },
        "required": ["query"]
    }
)

async def search_kpis(query: str, facets: Optional[str] = None, top: int = 50, 
                     skip: int = 0, include_count: bool = False) -> list[TextContent]:
    """
    Search and discover KPIs using advanced query syntax.
    
    Args:
        query: Search terms for KPI discovery
        facets: Comma-separated facets to include in results
        top: Maximum results to return (default: 50, max: 500)
        skip: Results to skip for pagination
        include_count: Include total count in response
    
    Returns:
        JSON string containing KPI search results with facets
    """
    try:
        # Build KPI search query with proper scope
        kpi_scope = "comsapcatalogsearchprivateSearchKPIsAdmin"
        search_query = f"SCOPE:{kpi_scope} {query}"
        
        # Build request parameters
        params = {
            "query": search_query,
            "$top": min(top, 500),
            "$skip": skip
        }
        
        if facets:
            params["facets"] = facets
        if include_count:
            params["$count"] = "true"
        
        # Get OAuth2 token
        token = await get_oauth_token()
        
        # Make request
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{config.base_url}/api/v1/datasphere/search",
                params=params,
                headers={
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/json'
                },
                timeout=30.0
            )
            
            response.raise_for_status()
            data = response.json()
        
        # Format response
        result = {
            'search_query': search_query,
            'kpis': data.get('value', []),
            'facets': data.get('facets', {}),
            'count': data.get('@odata.count', len(data.get('value', []))),
            'search_metadata': {
                'total_results': len(data.get('value', [])),
                'facets_requested': facets,
                'pagination': {'top': top, 'skip': skip}
            }
        }
        
        return [TextContent(type='text', text=json.dumps(result, indent=2))]
    
    except httpx.HTTPStatusError as e:
        error_msg = handle_http_error(e, "KPI search")
        return [TextContent(type='text', text=json.dumps({'error': error_msg}, indent=2))]
    
    except Exception as e:
        return [TextContent(type='text', text=json.dumps({'error': str(e)}, indent=2))]
```

### Tool 2: get_kpi_details

```python
# Tool definition
get_kpi_details_tool = Tool(
    name="get_kpi_details",
    description="Retrieve detailed KPI metadata including calculation logic and historical performance",
    inputSchema={
        "type": "object",
        "properties": {
            "kpi_id": {"type": "string", "description": "KPI identifier"},
            "include_history": {"type": "boolean", "default": False},
            "include_lineage": {"type": "boolean", "default": False},
            "history_period": {"type": "string", "enum": ["1M", "3M", "6M", "1Y"]}
        },
        "required": ["kpi_id"]
    }
)

async def get_kpi_details(kpi_id: str, include_history: bool = False, 
                         include_lineage: bool = False, 
                         history_period: Optional[str] = None) -> list[TextContent]:
    """
    Retrieve detailed KPI metadata including calculation logic and performance.
    
    Args:
        kpi_id: KPI identifier
        include_history: Include historical values
        include_lineage: Include data lineage information
        history_period: History period (1M, 3M, 6M, 1Y)
    
    Returns:
        JSON string containing detailed KPI information
    """
    try:
        # Build URL
        url = f"{config.base_url}/api/v1/datasphere/kpis/{kpi_id}"
        
        # Build query parameters
        params = {}
        if include_history:
            params['include_history'] = 'true'
        if include_lineage:
            params['include_lineage'] = 'true'
        if history_period:
            params['history_period'] = history_period
        
        # Get OAuth2 token
        token = await get_oauth_token()
        
        # Make request
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                headers={
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/json'
                },
                timeout=30.0
            )
            
            response.raise_for_status()
            kpi_data = response.json()
        
        # Enhance with analysis
        result = {
            'kpi_details': kpi_data,
            'analysis': analyze_kpi_performance(kpi_data),
            'recommendations': generate_kpi_recommendations(kpi_data)
        }
        
        return [TextContent(type='text', text=json.dumps(result, indent=2))]
    
    except httpx.HTTPStatusError as e:
        error_msg = handle_http_error(e, f"KPI {kpi_id}")
        return [TextContent(type='text', text=json.dumps({'error': error_msg}, indent=2))]
    
    except Exception as e:
        return [TextContent(type='text', text=json.dumps({'error': str(e)}, indent=2))]


def analyze_kpi_performance(kpi_data: dict) -> dict:
    """Analyze KPI performance and trends."""
    current_value = kpi_data.get('currentValue', {}).get('value', 0)
    target_value = kpi_data.get('targets', {}).get('targetValue', 0)
    
    if target_value > 0:
        performance_ratio = current_value / target_value
        if performance_ratio >= 1.0:
            performance = "Exceeding Target"
        elif performance_ratio >= 0.9:
            performance = "Near Target"
        elif performance_ratio >= 0.7:
            performance = "Below Target"
        else:
            performance = "Significantly Below Target"
    else:
        performance = "No Target Set"
    
    return {
        'performance_status': performance,
        'target_achievement': f"{(current_value/target_value*100):.1f}%" if target_value > 0 else "N/A",
        'gap_to_target': target_value - current_value if target_value > 0 else 0
    }


def generate_kpi_recommendations(kpi_data: dict) -> list[str]:
    """Generate recommendations based on KPI performance."""
    recommendations = []
    
    current_value = kpi_data.get('currentValue', {}).get('value', 0)
    target_value = kpi_data.get('targets', {}).get('targetValue', 0)
    
    if target_value > 0 and current_value < target_value:
        gap = target_value - current_value
        recommendations.append(f"Focus on closing the {gap:.1f} unit gap to target")
    
    if kpi_data.get('currentValue', {}).get('trend') == "Declining":
        recommendations.append("Investigate root causes of declining trend")
    
    alerts = kpi_data.get('alerts', [])
    if alerts:
        recommendations.append(f"Address {len(alerts)} active alerts")
    
    return recommendations
```

### Tool 3: list_all_kpis

```python
# Tool definition
list_all_kpis_tool = Tool(
    name="list_all_kpis",
    description="Get comprehensive inventory of all defined KPIs with filtering and categorization",
    inputSchema={
        "type": "object",
        "properties": {
            "space_id": {"type": "string", "description": "Filter by specific space"},
            "category": {"type": "string", "description": "Filter by KPI category"},
            "business_area": {"type": "string", "description": "Filter by business area"},
            "status": {"type": "string", "enum": ["Active", "Inactive", "Draft"]},
            "owner": {"type": "string", "description": "Filter by owner"},
            "include_inactive": {"type": "boolean", "default": False},
            "top": {"type": "integer", "default": 100, "maximum": 1000},
            "skip": {"type": "integer", "default": 0}
        }
    }
)

async def list_all_kpis(space_id: Optional[str] = None, category: Optional[str] = None,
                       business_area: Optional[str] = None, status: Optional[str] = None,
                       owner: Optional[str] = None, include_inactive: bool = False,
                       top: int = 100, skip: int = 0) -> list[TextContent]:
    """
    Get comprehensive inventory of all defined KPIs with filtering.
    
    Args:
        space_id: Filter by specific space
        category: Filter by KPI category
        business_area: Filter by business area
        status: Filter by status (Active, Inactive, Draft)
        owner: Filter by owner
        include_inactive: Include inactive KPIs
        top: Maximum results (default: 100, max: 1000)
        skip: Results to skip for pagination
    
    Returns:
        JSON string containing KPI inventory with summary statistics
    """
    try:
        # Build URL
        url = f"{config.base_url}/api/v1/datasphere/kpis"
        
        # Build query parameters
        params = {
            '$top': min(top, 1000),
            '$skip': skip
        }
        
        # Build filter expression
        filters = []
        if space_id:
            filters.append(f"spaceId eq '{space_id}'")
        if category:
            filters.append(f"category eq '{category}'")
        if business_area:
            filters.append(f"businessArea eq '{business_area}'")
        if status:
            filters.append(f"status eq '{status}'")
        if owner:
            filters.append(f"owner eq '{owner}'")
        if not include_inactive:
            filters.append("status ne 'Inactive'")
        
        if filters:
            params['$filter'] = ' and '.join(filters)
        
        # Get OAuth2 token
        token = await get_oauth_token()
        
        # Make request
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                headers={
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/json'
                },
                timeout=30.0
            )
            
            response.raise_for_status()
            data = response.json()
        
        # Analyze KPI inventory
        kpis = data.get('value', [])
        analysis = analyze_kpi_inventory(kpis)
        
        result = {
            'kpis': kpis,
            'summary': data.get('summary', {}),
            'analysis': analysis,
            'filters_applied': {
                'space_id': space_id,
                'category': category,
                'business_area': business_area,
                'status': status,
                'owner': owner,
                'include_inactive': include_inactive
            },
            'pagination': {'top': top, 'skip': skip, 'returned': len(kpis)}
        }
        
        return [TextContent(type='text', text=json.dumps(result, indent=2))]
    
    except httpx.HTTPStatusError as e:
        error_msg = handle_http_error(e, "KPI inventory")
        return [TextContent(type='text', text=json.dumps({'error': error_msg}, indent=2))]
    
    except Exception as e:
        return [TextContent(type='text', text=json.dumps({'error': str(e)}, indent=2))]


def analyze_kpi_inventory(kpis: list[dict]) -> dict:
    """Analyze KPI inventory for insights."""
    if not kpis:
        return {'message': 'No KPIs found'}
    
    # Performance analysis
    performance_counts = {'Excellent': 0, 'Good': 0, 'Warning': 0, 'Critical': 0}
    categories = {}
    business_areas = {}
    
    for kpi in kpis:
        # Count by status
        status = kpi.get('status', 'Unknown')
        if status in performance_counts:
            performance_counts[status] += 1
        
        # Count by category
        category = kpi.get('category', 'Uncategorized')
        categories[category] = categories.get(category, 0) + 1
        
        # Count by business area
        business_area = kpi.get('businessArea', 'Unknown')
        business_areas[business_area] = business_areas.get(business_area, 0) + 1
    
    return {
        'total_kpis': len(kpis),
        'performance_distribution': performance_counts,
        'top_categories': sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5],
        'business_area_distribution': business_areas,
        'health_score': calculate_kpi_health_score(performance_counts)
    }


def calculate_kpi_health_score(performance_counts: dict) -> dict:
    """Calculate overall KPI health score."""
    total = sum(performance_counts.values())
    if total == 0:
        return {'score': 0, 'grade': 'N/A'}
    
    # Weighted scoring
    score = (
        performance_counts.get('Excellent', 0) * 4 +
        performance_counts.get('Good', 0) * 3 +
        performance_counts.get('Warning', 0) * 2 +
        performance_counts.get('Critical', 0) * 1
    ) / total
    
    if score >= 3.5:
        grade = 'A'
    elif score >= 3.0:
        grade = 'B'
    elif score >= 2.5:
        grade = 'C'
    elif score >= 2.0:
        grade = 'D'
    else:
        grade = 'F'
    
    return {'score': round(score, 2), 'grade': grade}
```

---

## PHASE 7: SYSTEM MONITORING TOOLS (7 tools)

### Tool 4: get_systems_overview

```python
# Tool definition
get_systems_overview_tool = Tool(
    name="get_systems_overview",
    description="Get comprehensive landscape overview of all registered systems and their health",
    inputSchema={
        "type": "object",
        "properties": {
            "include_details": {"type": "boolean", "default": False},
            "health_check": {"type": "boolean", "default": False}
        }
    }
)

async def get_systems_overview(include_details: bool = False, 
                              health_check: bool = False) -> list[TextContent]:
    """
    Get comprehensive landscape overview of all registered systems.
    
    Args:
        include_details: Include detailed system information
        health_check: Perform real-time health check
    
    Returns:
        JSON string containing systems overview with health status
    """
    try:
        # Build URL
        url = f"{config.base_url}/api/v1/datasphere/systems/overview"
        
        # Build query parameters
        params = {}
        if include_details:
            params['include_details'] = 'true'
        if health_check:
            params['health_check'] = 'true'
        
        # Get OAuth2 token
        token = await get_oauth_token()
        
        # Make request
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                headers={
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/json'
                },
                timeout=60.0  # Longer timeout for health checks
            )
            
            response.raise_for_status()
            data = response.json()
        
        # Analyze system health
        analysis = analyze_system_health(data)
        
        result = {
            'systems_overview': data,
            'health_analysis': analysis,
            'recommendations': generate_system_recommendations(data),
            'last_updated': datetime.now().isoformat()
        }
        
        return [TextContent(type='text', text=json.dumps(result, indent=2))]
    
    except httpx.HTTPStatusError as e:
        error_msg = handle_http_error(e, "systems overview")
        return [TextContent(type='text', text=json.dumps({'error': error_msg}, indent=2))]
    
    except Exception as e:
        return [TextContent(type='text', text=json.dumps({'error': str(e)}, indent=2))]


def analyze_system_health(systems_data: dict) -> dict:
    """Analyze overall system health."""
    systems = systems_data.get('systems', [])
    
    health_counts = {'Healthy': 0, 'Warning': 0, 'Critical': 0, 'Unknown': 0}
    connection_issues = []
    performance_issues = []
    
    for system in systems:
        health = system.get('health', 'Unknown')
        health_counts[health] = health_counts.get(health, 0) + 1
        
        # Check for connection issues
        if system.get('status') != 'Connected':
            connection_issues.append(system.get('name', 'Unknown'))
        
        # Check for performance issues
        metrics = system.get('metrics', {})
        if metrics.get('avgResponseTime', '0ms').replace('ms', '').isdigit():
            response_time = int(metrics['avgResponseTime'].replace('ms', ''))
            if response_time > 1000:  # > 1 second
                performance_issues.append({
                    'system': system.get('name'),
                    'response_time': metrics['avgResponseTime']
                })
    
    total_systems = len(systems)
    health_score = 0
    if total_systems > 0:
        health_score = (
            health_counts.get('Healthy', 0) * 3 +
            health_counts.get('Warning', 0) * 2 +
            health_counts.get('Critical', 0) * 1
        ) / total_systems
    
    return {
        'overall_health_score': round(health_score, 2),
        'health_distribution': health_counts,
        'connection_issues': connection_issues,
        'performance_issues': performance_issues,
        'systems_requiring_attention': len(connection_issues) + len(performance_issues)
    }


def generate_system_recommendations(systems_data: dict) -> list[str]:
    """Generate system maintenance recommendations."""
    recommendations = []
    
    systems = systems_data.get('systems', [])
    
    # Check for disconnected systems
    disconnected = [s for s in systems if s.get('status') != 'Connected']
    if disconnected:
        recommendations.append(f"Reconnect {len(disconnected)} disconnected systems")
    
    # Check for performance issues
    slow_systems = [s for s in systems if 
                   s.get('metrics', {}).get('avgResponseTime', '0ms').replace('ms', '').isdigit() and
                   int(s.get('metrics', {}).get('avgResponseTime', '0ms').replace('ms', '')) > 1000]
    if slow_systems:
        recommendations.append(f"Investigate performance issues in {len(slow_systems)} systems")
    
    # Check for low success rates
    failing_systems = [s for s in systems if 
                      s.get('metrics', {}).get('successRate', '100%').replace('%', '').replace('.', '').isdigit() and
                      float(s.get('metrics', {}).get('successRate', '100%').replace('%', '')) < 95.0]
    if failing_systems:
        recommendations.append(f"Address reliability issues in {len(failing_systems)} systems")
    
    return recommendations
```

### Tool 5: search_system_logs

```python
from datetime import datetime, timedelta

# Tool definition
search_system_logs_tool = Tool(
    name="search_system_logs",
    description="Search and filter system activity logs with advanced filtering capabilities",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query for log content"},
            "level": {"type": "string", "enum": ["ERROR", "WARN", "INFO", "DEBUG"]},
            "component": {"type": "string", "description": "System component filter"},
            "user_id": {"type": "string", "description": "Filter by user"},
            "start_time": {"type": "string", "description": "Start time (ISO 8601)"},
            "end_time": {"type": "string", "description": "End time (ISO 8601)"},
            "facets": {"type": "string", "description": "Comma-separated facets"},
            "top": {"type": "integer", "default": 100, "maximum": 1000},
            "skip": {"type": "integer", "default": 0}
        }
    }
)

async def search_system_logs(query: Optional[str] = None, level: Optional[str] = None,
                           component: Optional[str] = None, user_id: Optional[str] = None,
                           start_time: Optional[str] = None, end_time: Optional[str] = None,
                           facets: Optional[str] = None, top: int = 100, 
                           skip: int = 0) -> list[TextContent]:
    """
    Search and filter system activity logs with advanced filtering.
    
    Args:
        query: Search query for log content
        level: Log level filter (ERROR, WARN, INFO, DEBUG)
        component: System component filter
        user_id: Filter by user
        start_time: Start time (ISO 8601)
        end_time: End time (ISO 8601)
        facets: Comma-separated facets to include
        top: Maximum results (default: 100, max: 1000)
        skip: Results to skip for pagination
    
    Returns:
        JSON string containing filtered log entries with facets
    """
    try:
        # Build URL
        url = f"{config.base_url}/api/v1/datasphere/logs/search"
        
        # Build query parameters
        params = {
            '$top': min(top, 1000),
            '$skip': skip
        }
        
        if query:
            params['query'] = query
        if level:
            params['level'] = level
        if component:
            params['component'] = component
        if user_id:
            params['user_id'] = user_id
        if start_time:
            params['start_time'] = start_time
        if end_time:
            params['end_time'] = end_time
        if facets:
            params['facets'] = facets
        
        # Get OAuth2 token
        token = await get_oauth_token()
        
        # Make request
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                headers={
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/json'
                },
                timeout=30.0
            )
            
            response.raise_for_status()
            data = response.json()
        
        # Analyze log patterns
        logs = data.get('value', [])
        analysis = analyze_log_patterns(logs)
        
        result = {
            'logs': logs,
            'facets': data.get('facets', {}),
            'time_distribution': data.get('timeDistribution', []),
            'analysis': analysis,
            'search_criteria': {
                'query': query,
                'level': level,
                'component': component,
                'user_id': user_id,
                'time_range': f"{start_time} to {end_time}" if start_time and end_time else None
            },
            'pagination': {'top': top, 'skip': skip, 'returned': len(logs)}
        }
        
        return [TextContent(type='text', text=json.dumps(result, indent=2))]
    
    except httpx.HTTPStatusError as e:
        error_msg = handle_http_error(e, "log search")
        return [TextContent(type='text', text=json.dumps({'error': error_msg}, indent=2))]
    
    except Exception as e:
        return [TextContent(type='text', text=json.dumps({'error': str(e)}, indent=2))]


def analyze_log_patterns(logs: list[dict]) -> dict:
    """Analyze log patterns and identify issues."""
    if not logs:
        return {'message': 'No logs found'}
    
    # Count by level
    level_counts = {}
    component_counts = {}
    error_patterns = {}
    hourly_distribution = {}
    
    for log in logs:
        # Count by level
        level = log.get('level', 'Unknown')
        level_counts[level] = level_counts.get(level, 0) + 1
        
        # Count by component
        component = log.get('component', 'Unknown')
        component_counts[component] = component_counts.get(component, 0) + 1
        
        # Analyze error patterns
        if level == 'ERROR':
            error_code = log.get('details', {}).get('errorCode', 'Unknown')
            error_patterns[error_code] = error_patterns.get(error_code, 0) + 1
        
        # Hourly distribution
        timestamp = log.get('timestamp', '')
        if timestamp:
            hour = timestamp[:13]  # YYYY-MM-DDTHH
            hourly_distribution[hour] = hourly_distribution.get(hour, 0) + 1
    
    # Calculate error rate
    total_logs = len(logs)
    error_count = level_counts.get('ERROR', 0)
    error_rate = (error_count / total_logs * 100) if total_logs > 0 else 0
    
    return {
        'total_logs': total_logs,
        'error_rate': round(error_rate, 2),
        'level_distribution': level_counts,
        'top_components': sorted(component_counts.items(), key=lambda x: x[1], reverse=True)[:5],
        'top_errors': sorted(error_patterns.items(), key=lambda x: x[1], reverse=True)[:5],
        'hourly_activity': len(hourly_distribution),
        'peak_activity_hour': max(hourly_distribution.items(), key=lambda x: x[1])[0] if hourly_distribution else None
    }
```

I'll continue with the remaining tools in the next append to keep within the line limit.
### Tool 6: download_system_logs

```python
# Tool definition
download_system_logs_tool = Tool(
    name="download_system_logs",
    description="Export system logs for offline analysis with various format options",
    inputSchema={
        "type": "object",
        "properties": {
            "format": {"type": "string", "enum": ["JSON", "CSV", "XML"], "default": "JSON"},
            "level": {"type": "string", "enum": ["ERROR", "WARN", "INFO", "DEBUG"]},
            "component": {"type": "string", "description": "Component filter"},
            "start_time": {"type": "string", "description": "Start time (ISO 8601)"},
            "end_time": {"type": "string", "description": "End time (ISO 8601)"},
            "max_records": {"type": "integer", "default": 10000, "maximum": 100000},
            "include_details": {"type": "boolean", "default": True}
        }
    }
)

async def download_system_logs(format: str = "JSON", level: Optional[str] = None,
                              component: Optional[str] = None, start_time: Optional[str] = None,
                              end_time: Optional[str] = None, max_records: int = 10000,
                              include_details: bool = True) -> list[TextContent]:
    """
    Export system logs for offline analysis.
    
    Args:
        format: Export format (JSON, CSV, XML)
        level: Log level filter
        component: Component filter
        start_time: Start time (ISO 8601)
        end_time: End time (ISO 8601)
        max_records: Maximum records (default: 10000, max: 100000)
        include_details: Include detailed information
    
    Returns:
        JSON string containing export information and download URL
    """
    try:
        # Build URL
        url = f"{config.base_url}/api/v1/datasphere/logs/export"
        
        # Build query parameters
        params = {
            'format': format,
            'max_records': min(max_records, 100000),
            'include_details': str(include_details).lower()
        }
        
        if level:
            params['level'] = level
        if component:
            params['component'] = component
        if start_time:
            params['start_time'] = start_time
        if end_time:
            params['end_time'] = end_time
        
        # Get OAuth2 token
        token = await get_oauth_token()
        
        # Make request
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                headers={
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/json'
                },
                timeout=120.0  # Longer timeout for exports
            )
            
            response.raise_for_status()
            data = response.json()
        
        # Enhance export information
        result = {
            'export_info': data,
            'export_summary': {
                'format': format,
                'record_count': data.get('recordCount', 0),
                'file_size': data.get('fileSize', 'Unknown'),
                'estimated_download_time': estimate_download_time(data.get('fileSize', '0MB'))
            },
            'usage_instructions': {
                'download_url': data.get('downloadUrl'),
                'expires_at': data.get('expiresAt'),
                'recommended_tools': get_analysis_tools_for_format(format)
            }
        }
        
        return [TextContent(type='text', text=json.dumps(result, indent=2))]
    
    except httpx.HTTPStatusError as e:
        error_msg = handle_http_error(e, "log export")
        return [TextContent(type='text', text=json.dumps({'error': error_msg}, indent=2))]
    
    except Exception as e:
        return [TextContent(type='text', text=json.dumps({'error': str(e)}, indent=2))]


def estimate_download_time(file_size: str) -> str:
    """Estimate download time based on file size."""
    if 'MB' in file_size:
        size_mb = float(file_size.replace('MB', ''))
        if size_mb < 10:
            return "< 1 minute"
        elif size_mb < 100:
            return "1-5 minutes"
        else:
            return "5+ minutes"
    return "Unknown"


def get_analysis_tools_for_format(format: str) -> list[str]:
    """Get recommended analysis tools for export format."""
    tools = {
        'JSON': ['jq', 'Python pandas', 'Elasticsearch', 'Splunk'],
        'CSV': ['Excel', 'Python pandas', 'R', 'Tableau'],
        'XML': ['XMLSpy', 'Python lxml', 'XSLT processors']
    }
    return tools.get(format, [])
```

### Tool 7: get_system_log_facets

```python
# Tool definition
get_system_log_facets_tool = Tool(
    name="get_system_log_facets",
    description="Analyze logs with dimensional filtering to identify patterns and anomalies",
    inputSchema={
        "type": "object",
        "properties": {
            "facet_fields": {"type": "string", "description": "Comma-separated facet fields"},
            "start_time": {"type": "string", "description": "Analysis start time"},
            "end_time": {"type": "string", "description": "Analysis end time"},
            "level": {"type": "string", "enum": ["ERROR", "WARN", "INFO", "DEBUG"]},
            "component": {"type": "string", "description": "Component filter"}
        }
    }
)

async def get_system_log_facets(facet_fields: Optional[str] = None, 
                               start_time: Optional[str] = None,
                               end_time: Optional[str] = None, level: Optional[str] = None,
                               component: Optional[str] = None) -> list[TextContent]:
    """
    Analyze logs with dimensional filtering to identify patterns.
    
    Args:
        facet_fields: Comma-separated facet fields
        start_time: Analysis start time
        end_time: Analysis end time
        level: Log level filter
        component: Component filter
    
    Returns:
        JSON string containing faceted analysis with trends and anomalies
    """
    try:
        # Build URL
        url = f"{config.base_url}/api/v1/datasphere/logs/facets"
        
        # Build query parameters
        params = {}
        if facet_fields:
            params['facet_fields'] = facet_fields
        if start_time:
            params['start_time'] = start_time
        if end_time:
            params['end_time'] = end_time
        if level:
            params['level'] = level
        if component:
            params['component'] = component
        
        # Get OAuth2 token
        token = await get_oauth_token()
        
        # Make request
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                headers={
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/json'
                },
                timeout=60.0
            )
            
            response.raise_for_status()
            data = response.json()
        
        # Enhanced analysis
        enhanced_analysis = enhance_facet_analysis(data)
        
        result = {
            'facet_analysis': data,
            'enhanced_insights': enhanced_analysis,
            'recommendations': generate_log_recommendations(data),
            'analysis_metadata': {
                'analyzed_period': f"{start_time} to {end_time}" if start_time and end_time else "All time",
                'facet_fields': facet_fields,
                'filters_applied': {'level': level, 'component': component}
            }
        }
        
        return [TextContent(type='text', text=json.dumps(result, indent=2))]
    
    except httpx.HTTPStatusError as e:
        error_msg = handle_http_error(e, "log facet analysis")
        return [TextContent(type='text', text=json.dumps({'error': error_msg}, indent=2))]
    
    except Exception as e:
        return [TextContent(type='text', text=json.dumps({'error': str(e)}, indent=2))]


def enhance_facet_analysis(facet_data: dict) -> dict:
    """Enhance facet analysis with additional insights."""
    insights = {}
    
    # Analyze error trends
    trends = facet_data.get('trends', {})
    error_rate = trends.get('errorRate', {})
    
    if error_rate.get('trend') == 'Increasing':
        insights['error_trend'] = {
            'status': 'Concerning',
            'message': f"Error rate increased by {error_rate.get('change', 'unknown')}",
            'action_required': True
        }
    
    # Analyze top errors
    top_errors = trends.get('topErrors', [])
    if top_errors:
        most_common_error = top_errors[0]
        insights['primary_issue'] = {
            'error_type': most_common_error.get('error'),
            'frequency': most_common_error.get('count'),
            'impact': 'High' if most_common_error.get('count', 0) > 50 else 'Medium'
        }
    
    # Analyze anomalies
    anomalies = facet_data.get('anomalies', [])
    if anomalies:
        high_severity_anomalies = [a for a in anomalies if a.get('severity') == 'High']
        insights['anomaly_summary'] = {
            'total_anomalies': len(anomalies),
            'high_severity': len(high_severity_anomalies),
            'requires_immediate_attention': len(high_severity_anomalies) > 0
        }
    
    return insights


def generate_log_recommendations(facet_data: dict) -> list[str]:
    """Generate recommendations based on log analysis."""
    recommendations = []
    
    # Check error rate trends
    trends = facet_data.get('trends', {})
    error_rate = trends.get('errorRate', {})
    
    if error_rate.get('trend') == 'Increasing':
        recommendations.append("Investigate root cause of increasing error rate")
    
    # Check for top errors
    top_errors = trends.get('topErrors', [])
    if top_errors and top_errors[0].get('count', 0) > 100:
        recommendations.append(f"Address most frequent error: {top_errors[0].get('error')}")
    
    # Check for anomalies
    anomalies = facet_data.get('anomalies', [])
    high_severity = [a for a in anomalies if a.get('severity') == 'High']
    if high_severity:
        recommendations.append(f"Investigate {len(high_severity)} high-severity anomalies")
    
    # Check hourly patterns
    facets = facet_data.get('facets', {})
    hourly = facets.get('hourly', [])
    if hourly:
        peak_hour = max(hourly, key=lambda x: x.get('count', 0))
        if peak_hour.get('count', 0) > 1000:
            recommendations.append(f"Monitor system load during peak hour: {peak_hour.get('hour')}")
    
    return recommendations
```

---

## USER MANAGEMENT TOOLS (3 tools)

### Tool 8: list_users

```python
# Tool definition
list_users_tool = Tool(
    name="list_users",
    description="List all users in the tenant with their roles, permissions, and activity status",
    inputSchema={
        "type": "object",
        "properties": {
            "status": {"type": "string", "enum": ["Active", "Inactive", "Locked"]},
            "role": {"type": "string", "description": "Filter by role"},
            "space_id": {"type": "string", "description": "Filter by space access"},
            "include_permissions": {"type": "boolean", "default": False},
            "top": {"type": "integer", "default": 100, "maximum": 1000},
            "skip": {"type": "integer", "default": 0}
        }
    }
)

async def list_users(status: Optional[str] = None, role: Optional[str] = None,
                    space_id: Optional[str] = None, include_permissions: bool = False,
                    top: int = 100, skip: int = 0) -> list[TextContent]:
    """
    List all users in the tenant with filtering options.
    
    Args:
        status: Filter by status (Active, Inactive, Locked)
        role: Filter by role
        space_id: Filter by space access
        include_permissions: Include detailed permissions
        top: Maximum results (default: 100, max: 1000)
        skip: Results to skip for pagination
    
    Returns:
        JSON string containing user list with summary statistics
    """
    try:
        # Build URL
        url = f"{config.base_url}/api/v1/datasphere/users"
        
        # Build query parameters
        params = {
            '$top': min(top, 1000),
            '$skip': skip
        }
        
        # Build filter expression
        filters = []
        if status:
            filters.append(f"status eq '{status}'")
        if role:
            filters.append(f"roles/any(r: r eq '{role}')")
        if space_id:
            filters.append(f"spaceAccess/any(s: s/spaceId eq '{space_id}')")
        
        if filters:
            params['$filter'] = ' and '.join(filters)
        
        if include_permissions:
            params['include_permissions'] = 'true'
        
        # Get OAuth2 token
        token = await get_oauth_token()
        
        # Make request
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                headers={
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/json'
                },
                timeout=30.0
            )
            
            response.raise_for_status()
            data = response.json()
        
        # Analyze user data
        users = data.get('value', [])
        analysis = analyze_user_data(users)
        
        result = {
            'users': users,
            'summary': data.get('summary', {}),
            'analysis': analysis,
            'filters_applied': {
                'status': status,
                'role': role,
                'space_id': space_id,
                'include_permissions': include_permissions
            },
            'pagination': {'top': top, 'skip': skip, 'returned': len(users)}
        }
        
        return [TextContent(type='text', text=json.dumps(result, indent=2))]
    
    except httpx.HTTPStatusError as e:
        error_msg = handle_http_error(e, "user list")
        return [TextContent(type='text', text=json.dumps({'error': error_msg}, indent=2))]
    
    except Exception as e:
        return [TextContent(type='text', text=json.dumps({'error': str(e)}, indent=2))]


def analyze_user_data(users: list[dict]) -> dict:
    """Analyze user data for insights."""
    if not users:
        return {'message': 'No users found'}
    
    # Activity analysis
    active_users = [u for u in users if u.get('status') == 'Active']
    inactive_users = [u for u in users if u.get('status') == 'Inactive']
    
    # Login analysis
    recent_logins = []
    for user in users:
        last_login = user.get('lastLogin')
        if last_login:
            # Check if login was within last 7 days
            try:
                login_date = datetime.fromisoformat(last_login.replace('Z', '+00:00'))
                if (datetime.now(login_date.tzinfo) - login_date).days <= 7:
                    recent_logins.append(user)
            except:
                pass
    
    # Role distribution
    role_counts = {}
    for user in users:
        for role in user.get('roles', []):
            role_counts[role] = role_counts.get(role, 0) + 1
    
    return {
        'total_users': len(users),
        'active_users': len(active_users),
        'inactive_users': len(inactive_users),
        'recent_logins_7days': len(recent_logins),
        'activity_rate': round(len(recent_logins) / len(users) * 100, 1) if users else 0,
        'role_distribution': role_counts,
        'most_common_role': max(role_counts.items(), key=lambda x: x[1])[0] if role_counts else None
    }
```

### Tool 9: get_user_permissions

```python
# Tool definition
get_user_permissions_tool = Tool(
    name="get_user_permissions",
    description="Retrieve detailed user permissions and access rights across spaces and objects",
    inputSchema={
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "description": "User identifier"},
            "space_id": {"type": "string", "description": "Filter by specific space"},
            "include_inherited": {"type": "boolean", "default": True}
        },
        "required": ["user_id"]
    }
)

async def get_user_permissions(user_id: str, space_id: Optional[str] = None,
                              include_inherited: bool = True) -> list[TextContent]:
    """
    Retrieve detailed user permissions and access rights.
    
    Args:
        user_id: User identifier
        space_id: Filter by specific space
        include_inherited: Include inherited permissions
    
    Returns:
        JSON string containing detailed user permissions
    """
    try:
        # Build URL
        url = f"{config.base_url}/api/v1/datasphere/users/{user_id}/permissions"
        
        # Build query parameters
        params = {}
        if space_id:
            params['space_id'] = space_id
        if include_inherited:
            params['include_inherited'] = 'true'
        
        # Get OAuth2 token
        token = await get_oauth_token()
        
        # Make request
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                headers={
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/json'
                },
                timeout=30.0
            )
            
            response.raise_for_status()
            data = response.json()
        
        # Analyze permissions
        analysis = analyze_user_permissions(data)
        
        result = {
            'user_permissions': data,
            'permission_analysis': analysis,
            'security_recommendations': generate_security_recommendations(data),
            'access_summary': summarize_user_access(data)
        }
        
        return [TextContent(type='text', text=json.dumps(result, indent=2))]
    
    except httpx.HTTPStatusError as e:
        error_msg = handle_http_error(e, f"permissions for user {user_id}")
        return [TextContent(type='text', text=json.dumps({'error': error_msg}, indent=2))]
    
    except Exception as e:
        return [TextContent(type='text', text=json.dumps({'error': str(e)}, indent=2))]


def analyze_user_permissions(permissions_data: dict) -> dict:
    """Analyze user permissions for security insights."""
    global_perms = permissions_data.get('globalPermissions', [])
    space_perms = permissions_data.get('spacePermissions', [])
    object_perms = permissions_data.get('objectPermissions', [])
    
    # Count permission types
    read_permissions = len([p for p in global_perms if 'READ' in p.upper()])
    write_permissions = len([p for p in global_perms if any(w in p.upper() for w in ['WRITE', 'CREATE', 'UPDATE', 'DELETE'])])
    admin_permissions = len([p for p in global_perms if 'ADMIN' in p.upper()])
    
    # Analyze space access
    spaces_with_access = len(space_perms)
    viewer_spaces = len([s for s in space_perms if s.get('role') == 'Viewer'])
    admin_spaces = len([s for s in space_perms if 'Admin' in s.get('role', '')])
    
    return {
        'permission_scope': {
            'global_permissions': len(global_perms),
            'space_permissions': spaces_with_access,
            'object_permissions': len(object_perms)
        },
        'permission_types': {
            'read_permissions': read_permissions,
            'write_permissions': write_permissions,
            'admin_permissions': admin_permissions
        },
        'space_access': {
            'total_spaces': spaces_with_access,
            'viewer_access': viewer_spaces,
            'admin_access': admin_spaces
        },
        'risk_level': calculate_permission_risk_level(global_perms, space_perms)
    }


def calculate_permission_risk_level(global_perms: list, space_perms: list) -> str:
    """Calculate risk level based on permissions."""
    risk_score = 0
    
    # High-risk global permissions
    high_risk_perms = ['ADMIN', 'DELETE', 'MANAGE_USERS', 'SYSTEM_CONFIG']
    for perm in global_perms:
        if any(risk in perm.upper() for risk in high_risk_perms):
            risk_score += 3
    
    # Admin access to multiple spaces
    admin_spaces = len([s for s in space_perms if 'Admin' in s.get('role', '')])
    if admin_spaces > 3:
        risk_score += 2
    elif admin_spaces > 1:
        risk_score += 1
    
    if risk_score >= 5:
        return 'High'
    elif risk_score >= 3:
        return 'Medium'
    else:
        return 'Low'


def generate_security_recommendations(permissions_data: dict) -> list[str]:
    """Generate security recommendations based on permissions."""
    recommendations = []
    
    global_perms = permissions_data.get('globalPermissions', [])
    space_perms = permissions_data.get('spacePermissions', [])
    
    # Check for excessive permissions
    admin_perms = [p for p in global_perms if 'ADMIN' in p.upper()]
    if len(admin_perms) > 2:
        recommendations.append("Review admin permissions - user has multiple admin roles")
    
    # Check for space admin access
    admin_spaces = [s for s in space_perms if 'Admin' in s.get('role', '')]
    if len(admin_spaces) > 3:
        recommendations.append(f"User has admin access to {len(admin_spaces)} spaces - consider reducing scope")
    
    # Check for restrictions
    restrictions = permissions_data.get('restrictions', [])
    if not restrictions:
        recommendations.append("Consider adding data access restrictions for sensitive information")
    
    return recommendations


def summarize_user_access(permissions_data: dict) -> dict:
    """Summarize user access capabilities."""
    capabilities = []
    
    global_perms = permissions_data.get('globalPermissions', [])
    
    if any('READ' in p.upper() for p in global_perms):
        capabilities.append('Data Reading')
    if any('QUERY' in p.upper() for p in global_perms):
        capabilities.append('Query Execution')
    if any('EXPORT' in p.upper() for p in global_perms):
        capabilities.append('Data Export')
    if any('ADMIN' in p.upper() for p in global_perms):
        capabilities.append('Administration')
    
    return {
        'primary_capabilities': capabilities,
        'space_count': len(permissions_data.get('spacePermissions', [])),
        'object_access_count': len(permissions_data.get('objectPermissions', [])),
        'has_restrictions': len(permissions_data.get('restrictions', [])) > 0
    }
```

### Tool 10: get_user_details

```python
# Tool definition
get_user_details_tool = Tool(
    name="get_user_details",
    description="Get comprehensive user information including profile, activity, and audit trail",
    inputSchema={
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "description": "User identifier"},
            "include_activity": {"type": "boolean", "default": True},
            "include_audit": {"type": "boolean", "default": False},
            "activity_days": {"type": "integer", "default": 30, "maximum": 365}
        },
        "required": ["user_id"]
    }
)

async def get_user_details(user_id: str, include_activity: bool = True,
                          include_audit: bool = False, 
                          activity_days: int = 30) -> list[TextContent]:
    """
    Get comprehensive user information including profile and activity.
    
    Args:
        user_id: User identifier
        include_activity: Include recent activity
        include_audit: Include audit trail
        activity_days: Days of activity to include (default: 30, max: 365)
    
    Returns:
        JSON string containing comprehensive user information
    """
    try:
        # Build URL
        url = f"{config.base_url}/api/v1/datasphere/users/{user_id}"
        
        # Build query parameters
        params = {}
        if include_activity:
            params['include_activity'] = 'true'
            params['activity_days'] = min(activity_days, 365)
        if include_audit:
            params['include_audit'] = 'true'
        
        # Get OAuth2 token
        token = await get_oauth_token()
        
        # Make request
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                headers={
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/json'
                },
                timeout=30.0
            )
            
            response.raise_for_status()
            data = response.json()
        
        # Analyze user activity
        activity_analysis = analyze_user_activity(data) if include_activity else {}
        
        result = {
            'user_details': data,
            'activity_analysis': activity_analysis,
            'user_insights': generate_user_insights(data),
            'recommendations': generate_user_recommendations(data)
        }
        
        return [TextContent(type='text', text=json.dumps(result, indent=2))]
    
    except httpx.HTTPStatusError as e:
        error_msg = handle_http_error(e, f"details for user {user_id}")
        return [TextContent(type='text', text=json.dumps({'error': error_msg}, indent=2))]
    
    except Exception as e:
        return [TextContent(type='text', text=json.dumps({'error': str(e)}, indent=2))]


def analyze_user_activity(user_data: dict) -> dict:
    """Analyze user activity patterns."""
    activity = user_data.get('activity', {})
    recent_activity = user_data.get('recentActivity', [])
    
    # Calculate activity metrics
    login_count = activity.get('loginCount', 0)
    sessions_30_days = activity.get('sessionsLast30Days', 0)
    queries_executed = activity.get('queriesExecuted', 0)
    
    # Analyze recent activity patterns
    activity_types = {}
    for act in recent_activity:
        act_type = act.get('action', 'Unknown')
        activity_types[act_type] = activity_types.get(act_type, 0) + 1
    
    # Calculate engagement score
    engagement_score = min(100, (sessions_30_days * 2) + (queries_executed / 10))
    
    return {
        'engagement_score': round(engagement_score, 1),
        'activity_summary': {
            'total_logins': login_count,
            'recent_sessions': sessions_30_days,
            'queries_executed': queries_executed
        },
        'activity_patterns': activity_types,
        'most_common_activity': max(activity_types.items(), key=lambda x: x[1])[0] if activity_types else None,
        'activity_level': 'High' if engagement_score > 70 else 'Medium' if engagement_score > 30 else 'Low'
    }


def generate_user_insights(user_data: dict) -> dict:
    """Generate insights about the user."""
    insights = {}
    
    # Account age
    created_at = user_data.get('account', {}).get('createdAt')
    if created_at:
        try:
            created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            account_age_days = (datetime.now(created_date.tzinfo) - created_date).days
            insights['account_age'] = f"{account_age_days} days"
        except:
            insights['account_age'] = 'Unknown'
    
    # Role complexity
    roles = user_data.get('roles', [])
    insights['role_complexity'] = 'High' if len(roles) > 3 else 'Medium' if len(roles) > 1 else 'Low'
    
    # Space access
    space_access = user_data.get('spaceAccess', [])
    insights['space_access_level'] = 'Broad' if len(space_access) > 5 else 'Moderate' if len(space_access) > 2 else 'Limited'
    
    # Security posture
    account = user_data.get('account', {})
    mfa_enabled = account.get('mfaEnabled', False)
    account_locked = account.get('accountLocked', False)
    
    insights['security_posture'] = {
        'mfa_enabled': mfa_enabled,
        'account_locked': account_locked,
        'security_score': 'Good' if mfa_enabled and not account_locked else 'Needs Improvement'
    }
    
    return insights


def generate_user_recommendations(user_data: dict) -> list[str]:
    """Generate recommendations for user management."""
    recommendations = []
    
    # Check MFA
    account = user_data.get('account', {})
    if not account.get('mfaEnabled', False):
        recommendations.append("Enable multi-factor authentication for enhanced security")
    
    # Check password age
    password_changed = account.get('passwordLastChanged')
    if password_changed:
        try:
            changed_date = datetime.fromisoformat(password_changed.replace('Z', '+00:00'))
            days_since_change = (datetime.now(changed_date.tzinfo) - changed_date).days
            if days_since_change > 90:
                recommendations.append("Consider password rotation - last changed over 90 days ago")
        except:
            pass
    
    # Check activity level
    activity = user_data.get('activity', {})
    sessions_30_days = activity.get('sessionsLast30Days', 0)
    if sessions_30_days == 0:
        recommendations.append("User has not logged in recently - consider account review")
    elif sessions_30_days > 100:
        recommendations.append("High activity user - ensure appropriate access controls")
    
    # Check role assignments
    roles = user_data.get('roles', [])
    if len(roles) > 5:
        recommendations.append("User has many roles - review for principle of least privilege")
    
    return recommendations
```

---

## Helper Functions

### OAuth2 Token Management
```python
from datetime import datetime, timedelta
from typing import Optional

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
    
    async def refresh_token(self) -> str:
        """Refresh OAuth2 access token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    'grant_type': 'client_credentials',
                    'client_id': self.client_id,
                    'client_secret': self.client_secret
                },
                timeout=30.0
            )
            
            response.raise_for_status()
            token_data = response.json()
            
            self.access_token = token_data['access_token']
            expires_in = token_data.get('expires_in', 3600)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in - 60)
            
            return self.access_token

# Global token manager instance
token_manager: Optional[OAuth2TokenManager] = None

async def get_oauth_token() -> str:
    """Get OAuth2 token from global token manager."""
    global token_manager
    
    if token_manager is None:
        token_manager = OAuth2TokenManager(
            client_id=config.client_id,
            client_secret=config.client_secret,
            token_url=config.token_url
        )
    
    return await token_manager.get_token()
```

### Error Handling
```python
def handle_http_error(error: httpx.HTTPStatusError, context: str) -> str:
    """Handle HTTP errors with user-friendly messages."""
    status_code = error.response.status_code
    
    if status_code == 401:
        return f'Authentication failed for {context}. Please check OAuth2 credentials.'
    elif status_code == 403:
        return f'Access denied to {context}. Insufficient permissions.'
    elif status_code == 404:
        return f'{context} not found. Please verify the identifier.'
    elif status_code == 500:
        return f'SAP Datasphere server error while accessing {context}. Please try again later.'
    else:
        return f'HTTP {status_code} error while accessing {context}: {error.response.text}'
```

---

## Configuration Model
```python
from pydantic import BaseModel, Field

class MonitoringConfig(BaseModel):
    """Configuration for monitoring and KPI tools."""
    
    base_url: str = Field(..., description='SAP Datasphere base URL')
    client_id: str = Field(..., description='OAuth2 client ID')
    client_secret: str = Field(..., description='OAuth2 client secret')
    token_url: str = Field(..., description='OAuth2 token endpoint')
    default_page_size: int = Field(100, description='Default page size')
    max_page_size: int = Field(1000, description='Maximum page size')
    request_timeout: int = Field(30, description='Request timeout in seconds')
    log_export_timeout: int = Field(120, description='Log export timeout in seconds')
```

---

## Tool Registration
```python
# All tools for registration
monitoring_kpi_tools = [
    # KPI Management
    search_kpis_tool,
    get_kpi_details_tool,
    list_all_kpis_tool,
    
    # System Monitoring
    get_systems_overview_tool,
    search_system_logs_tool,
    download_system_logs_tool,
    get_system_log_facets_tool,
    
    # User Management
    list_users_tool,
    get_user_permissions_tool,
    get_user_details_tool
]

# Tool handlers mapping
tool_handlers = {
    "search_kpis": search_kpis,
    "get_kpi_details": get_kpi_details,
    "list_all_kpis": list_all_kpis,
    "get_systems_overview": get_systems_overview,
    "search_system_logs": search_system_logs,
    "download_system_logs": download_system_logs,
    "get_system_log_facets": get_system_log_facets,
    "list_users": list_users,
    "get_user_permissions": get_user_permissions,
    "get_user_details": get_user_details
}
```

---

## Testing Examples

### Unit Tests
```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_search_kpis():
    """Test KPI search functionality."""
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            'value': [{'id': 'kpi-1', 'name': 'Test KPI'}],
            'facets': {'category': [{'value': 'Revenue', 'count': 1}]}
        }
        mock_response.raise_for_status = AsyncMock()
        mock_get.return_value = mock_response
        
        result = await search_kpis(query="revenue")
        
        assert len(result) == 1
        assert 'Test KPI' in result[0].text

@pytest.mark.asyncio
async def test_get_systems_overview():
    """Test systems overview functionality."""
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            'systems': [{'name': 'SAP S/4HANA', 'health': 'Healthy'}],
            'summary': {'totalSystems': 1}
        }
        mock_response.raise_for_status = AsyncMock()
        mock_get.return_value = mock_response
        
        result = await get_systems_overview()
        
        assert len(result) == 1
        assert 'SAP S/4HANA' in result[0].text
```

### Integration Tests
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_kpi_management_workflow():
    """Test complete KPI management workflow."""
    # 1. Search KPIs
    kpis = await search_kpis(query="financial")
    assert len(kpis) > 0
    
    # 2. Get KPI details
    kpi_id = "kpi-12345"  # From search results
    details = await get_kpi_details(kpi_id=kpi_id, include_history=True)
    assert 'calculation' in details[0].text
    
    # 3. List all KPIs
    all_kpis = await list_all_kpis(category="Revenue")
    assert len(all_kpis) > 0

@pytest.mark.integration
@pytest.mark.asyncio
async def test_system_monitoring_workflow():
    """Test complete system monitoring workflow."""
    # 1. Get systems overview
    overview = await get_systems_overview(health_check=True)
    assert 'systems' in overview[0].text
    
    # 2. Search logs
    logs = await search_system_logs(level="ERROR", top=50)
    assert len(logs) > 0
    
    # 3. Analyze log facets
    facets = await get_system_log_facets(facet_fields="level,component")
    assert 'facets' in facets[0].text
```

---

## Usage Examples

### Example 1: KPI Discovery and Analysis
```python
# Search for financial KPIs
kpis = await search_kpis(
    query="revenue growth",
    facets="category,businessArea",
    top=20
)

# Get detailed information for specific KPI
kpi_details = await get_kpi_details(
    kpi_id="kpi-12345",
    include_history=True,
    history_period="6M"
)

# List all KPIs in finance area
finance_kpis = await list_all_kpis(
    business_area="Finance",
    status="Active"
)
```

### Example 2: System Health Monitoring
```python
# Get comprehensive systems overview
systems = await get_systems_overview(
    include_details=True,
    health_check=True
)

# Search for recent errors
error_logs = await search_system_logs(
    level="ERROR",
    start_time="2024-12-08T00:00:00Z",
    end_time="2024-12-09T23:59:59Z",
    facets="component,level"
)

# Analyze log patterns
log_analysis = await get_system_log_facets(
    facet_fields="level,component,hourly",
    start_time="2024-12-08T00:00:00Z",
    end_time="2024-12-09T23:59:59Z"
)
```

### Example 3: User Administration
```python
# List active users
users = await list_users(
    status="Active",
    include_permissions=True
)

# Get detailed user information
user_info = await get_user_details(
    user_id="user-12345",
    include_activity=True,
    include_audit=True,
    activity_days=30
)

# Check user permissions
permissions = await get_user_permissions(
    user_id="user-12345",
    include_inherited=True
)
```

---

## Checklist

Before submitting implementation:

- [ ] All 10 tools implemented with proper type hints
- [ ] OAuth2 authentication integrated
- [ ] Comprehensive error handling for all HTTP status codes
- [ ] KPI search with proper scope syntax
- [ ] Log analysis with pattern detection
- [ ] User management with security analysis
- [ ] Helper functions for data analysis
- [ ] Unit tests with >90% coverage
- [ ] Integration tests with real tenant
- [ ] Documentation with usage examples
- [ ] Code follows Ruff linting standards
- [ ] All tools return MCP TextContent with JSON strings

---

## Next Steps

1. Implement all 10 tools following the templates above
2. Add tools to MCP server registration
3. Create unit tests for each tool
4. Run integration tests with real SAP Datasphere tenant
5. Update documentation with usage examples
6. Optional: Proceed to Phase 8 (Advanced Features)

---

**Document Version**: 1.0  
**Last Updated**: December 9, 2025  
**Related Documents**:
- SAP_DATASPHERE_MONITORING_KPI_TOOLS_SPEC.md
- SAP_DATASPHERE_MCP_EXTRACTION_PLAN.md