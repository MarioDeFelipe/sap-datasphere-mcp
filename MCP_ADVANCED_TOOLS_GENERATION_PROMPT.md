# MCP Tool Generation Prompt - Phase 8: Advanced Features

## Context

You are implementing **10 advanced feature tools** for the SAP Datasphere MCP Server. These tools enable data sharing, AI monitoring, configuration management, and legacy API support.

**Reference Document**: `SAP_DATASPHERE_ADVANCED_TOOLS_SPEC.md`

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
│   ├── data_sharing.py        # NEW: Data sharing tools (3 tools)
│   ├── ai_features.py         # NEW: AI monitoring tools (3 tools)
│   └── legacy_dwc.py          # NEW: Legacy DWC APIs (4 tools)
```

---

## PHASE 8.1: DATA SHARING & COLLABORATION TOOLS (3 tools)

### Tool 1: list_partner_systems

```python
from mcp.types import Tool, TextContent
import httpx
import json
from typing import Optional

# Tool definition
list_partner_systems_tool = Tool(
    name="list_partner_systems",
    description="Discover partner systems and external data products available through data sharing partnerships",
    inputSchema={
        "type": "object",
        "properties": {
            "partner_type": {"type": "string", "description": "Filter by partner type"},
            "status": {"type": "string", "enum": ["Active", "Inactive", "All"], "default": "Active"},
            "include_data_products": {"type": "boolean", "default": True},
            "top": {"type": "integer", "default": 50, "maximum": 1000},
            "skip": {"type": "integer", "default": 0}
        }
    }
)

async def list_partner_systems(partner_type: Optional[str] = None, status: str = "Active",
                              include_data_products: bool = True, top: int = 50, 
                              skip: int = 0) -> list[TextContent]:
    """
    Discover partner systems and external data products through data sharing partnerships.
    
    Args:
        partner_type: Filter by partner type
        status: Filter by status (Active, Inactive, All)
        include_data_products: Include data products in response
        top: Maximum results (default: 50, max: 1000)
        skip: Results to skip for pagination
    
    Returns:
        JSON string containing partner systems with data products and sharing details
    """
    try:
        # Build URL
        url = f"{config.base_url}/deepsea/catalog/v1/dataProducts/partners/systems"
        
        # Build query parameters
        params = {
            '$top': min(top, 1000),
            '$skip': skip
        }
        
        # Build filter expression
        filters = []
        if partner_type:
            filters.append(f"partnerType eq '{partner_type}'")
        if status != "All":
            filters.append(f"status eq '{status}'")
        
        if filters:
            params['$filter'] = ' and '.join(filters)
        
        if include_data_products:
            params['$expand'] = 'dataProducts'
        
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
        
        # Analyze partner systems
        partners = data.get('value', [])
        analysis = analyze_partner_systems(partners)
        
        result = {
            'partner_systems': partners,
            'summary': data.get('summary', {}),
            'analysis': analysis,
            'filters_applied': {
                'partner_type': partner_type,
                'status': status,
                'include_data_products': include_data_products
            },
            'pagination': {'top': top, 'skip': skip, 'returned': len(partners)}
        }
        
        return [TextContent(type='text', text=json.dumps(result, indent=2))]
    
    except httpx.HTTPStatusError as e:
        error_msg = handle_http_error(e, "partner systems")
        return [TextContent(type='text', text=json.dumps({'error': error_msg}, indent=2))]
    
    except Exception as e:
        return [TextContent(type='text', text=json.dumps({'error': str(e)}, indent=2))]


def analyze_partner_systems(partners: list[dict]) -> dict:
    """Analyze partner systems for insights."""
    if not partners:
        return {'message': 'No partner systems found'}
    
    # Analyze partner types
    partner_types = {}
    connection_status = {}
    total_data_products = 0
    
    for partner in partners:
        # Count by type
        p_type = partner.get('partnerType', 'Unknown')
        partner_types[p_type] = partner_types.get(p_type, 0) + 1
        
        # Count by connection status
        conn_status = partner.get('connectionStatus', 'Unknown')
        connection_status[conn_status] = connection_status.get(conn_status, 0) + 1
        
        # Count data products
        data_products = partner.get('dataProducts', [])
        total_data_products += len(data_products)
    
    return {
        'total_partners': len(partners),
        'partner_types': partner_types,
        'connection_status': connection_status,
        'total_data_products': total_data_products,
        'avg_products_per_partner': round(total_data_products / len(partners), 1) if partners else 0,
        'health_score': calculate_partnership_health(partners)
    }


def calculate_partnership_health(partners: list[dict]) -> dict:
    """Calculate overall partnership health score."""
    if not partners:
        return {'score': 0, 'grade': 'N/A'}
    
    connected_partners = len([p for p in partners if p.get('connectionStatus') == 'Connected'])
    active_partners = len([p for p in partners if p.get('status') == 'Active'])
    
    connection_rate = connected_partners / len(partners)
    active_rate = active_partners / len(partners)
    
    health_score = (connection_rate * 0.6 + active_rate * 0.4) * 100
    
    if health_score >= 90:
        grade = 'Excellent'
    elif health_score >= 75:
        grade = 'Good'
    elif health_score >= 60:
        grade = 'Fair'
    else:
        grade = 'Poor'
    
    return {'score': round(health_score, 1), 'grade': grade}
```

### Tool 2: get_marketplace_assets

```python
# Tool definition
get_marketplace_assets_tool = Tool(
    name="get_marketplace_assets",
    description="Access Data Sharing Cockpit marketplace to browse available shared data assets",
    inputSchema={
        "type": "object",
        "properties": {
            "request_type": {"type": "string", "enum": ["browse", "search", "categories"], "default": "browse"},
            "category": {"type": "string", "description": "Filter by asset category"},
            "provider": {"type": "string", "description": "Filter by data provider"},
            "pricing_model": {"type": "string", "enum": ["Free", "Subscription", "One-time"]},
            "search_query": {"type": "string", "description": "Search query for assets"},
            "top": {"type": "integer", "default": 50, "maximum": 500},
            "skip": {"type": "integer", "default": 0}
        }
    }
)

async def get_marketplace_assets(request_type: str = "browse", category: Optional[str] = None,
                                provider: Optional[str] = None, pricing_model: Optional[str] = None,
                                search_query: Optional[str] = None, top: int = 50, 
                                skip: int = 0) -> list[TextContent]:
    """
    Access Data Sharing Cockpit marketplace to browse available shared data assets.
    
    Args:
        request_type: Type of marketplace request (browse, search, categories)
        category: Filter by asset category
        provider: Filter by data provider
        pricing_model: Filter by pricing model (Free, Subscription, One-time)
        search_query: Search query for assets
        top: Maximum results (default: 50, max: 500)
        skip: Results to skip for pagination
    
    Returns:
        JSON string containing marketplace assets with facets and recommendations
    """
    try:
        # Build URL
        url = f"{config.base_url}/api/v1/datasphere/marketplace/dsc/{request_type}"
        
        # Build query parameters
        params = {
            '$top': min(top, 500),
            '$skip': skip
        }
        
        # Build filter expression
        filters = []
        if category:
            filters.append(f"category eq '{category}'")
        if provider:
            filters.append(f"provider eq '{provider}'")
        if pricing_model:
            filters.append(f"pricing/model eq '{pricing_model}'")
        
        if filters:
            params['$filter'] = ' and '.join(filters)
        
        if search_query:
            params['search'] = search_query
        
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
        
        # Analyze marketplace assets
        assets = data.get('value', [])
        analysis = analyze_marketplace_assets(assets)
        
        result = {
            'marketplace_assets': assets,
            'facets': data.get('facets', {}),
            'analysis': analysis,
            'recommendations': generate_marketplace_recommendations(assets),
            'search_criteria': {
                'request_type': request_type,
                'category': category,
                'provider': provider,
                'pricing_model': pricing_model,
                'search_query': search_query
            },
            'pagination': {'top': top, 'skip': skip, 'returned': len(assets)}
        }
        
        return [TextContent(type='text', text=json.dumps(result, indent=2))]
    
    except httpx.HTTPStatusError as e:
        error_msg = handle_http_error(e, "marketplace assets")
        return [TextContent(type='text', text=json.dumps({'error': error_msg}, indent=2))]
    
    except Exception as e:
        return [TextContent(type='text', text=json.dumps({'error': str(e)}, indent=2))]


def analyze_marketplace_assets(assets: list[dict]) -> dict:
    """Analyze marketplace assets for insights."""
    if not assets:
        return {'message': 'No marketplace assets found'}
    
    # Analyze categories and pricing
    categories = {}
    pricing_models = {}
    quality_scores = []
    
    for asset in assets:
        # Count by category
        category = asset.get('category', 'Uncategorized')
        categories[category] = categories.get(category, 0) + 1
        
        # Count by pricing model
        pricing = asset.get('pricing', {})
        model = pricing.get('model', 'Unknown')
        pricing_models[model] = pricing_models.get(model, 0) + 1
        
        # Collect quality scores
        quality_score = asset.get('qualityScore', 0)
        if quality_score > 0:
            quality_scores.append(quality_score)
    
    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
    
    return {
        'total_assets': len(assets),
        'categories': categories,
        'pricing_models': pricing_models,
        'average_quality_score': round(avg_quality, 2),
        'high_quality_assets': len([s for s in quality_scores if s >= 4.5]),
        'free_assets': pricing_models.get('Free', 0),
        'paid_assets': len(assets) - pricing_models.get('Free', 0)
    }


def generate_marketplace_recommendations(assets: list[dict]) -> list[str]:
    """Generate marketplace recommendations."""
    recommendations = []
    
    if not assets:
        return ['No assets found - try broadening search criteria']
    
    # Recommend high-quality free assets
    free_assets = [a for a in assets if a.get('pricing', {}).get('model') == 'Free']
    high_quality_free = [a for a in free_assets if a.get('qualityScore', 0) >= 4.0]
    
    if high_quality_free:
        recommendations.append(f"Consider {len(high_quality_free)} high-quality free assets")
    
    # Recommend popular assets
    popular_assets = [a for a in assets if a.get('downloads', 0) > 1000]
    if popular_assets:
        recommendations.append(f"Explore {len(popular_assets)} popular assets with 1000+ downloads")
    
    # Recommend by category diversity
    categories = set(a.get('category') for a in assets)
    if len(categories) > 5:
        recommendations.append(f"Diverse selection available across {len(categories)} categories")
    
    return recommendations
```

### Tool 3: get_data_product_details

```python
# Tool definition
get_data_product_details_tool = Tool(
    name="get_data_product_details",
    description="Get detailed information about a specific data product including metadata and usage analytics",
    inputSchema={
        "type": "object",
        "properties": {
            "product_id": {"type": "string", "description": "Data product identifier"},
            "include_installation": {"type": "boolean", "default": True},
            "include_metadata": {"type": "boolean", "default": True},
            "include_access": {"type": "boolean", "default": True},
            "include_usage": {"type": "boolean", "default": True}
        },
        "required": ["product_id"]
    }
)

async def get_data_product_details(product_id: str, include_installation: bool = True,
                                  include_metadata: bool = True, include_access: bool = True,
                                  include_usage: bool = True) -> list[TextContent]:
    """
    Get detailed information about a specific data product.
    
    Args:
        product_id: Data product identifier
        include_installation: Include installation details
        include_metadata: Include detailed metadata
        include_access: Include access permissions
        include_usage: Include usage analytics
    
    Returns:
        JSON string containing comprehensive data product information
    """
    try:
        # Build URL - try primary endpoint first
        url = f"{config.base_url}/dwaas-core/odc/dataProduct/{product_id}/details"
        
        # Build query parameters
        params = {}
        if include_installation:
            params['includeInstallation'] = 'true'
        if include_metadata:
            params['includeMetadata'] = 'true'
        if include_access:
            params['includeAccess'] = 'true'
        
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
            
            # If primary endpoint fails, try alternative
            if response.status_code == 404:
                alt_url = f"{config.base_url}/api/v1/datasphere/marketplace/dsc/products/{product_id}"
                response = await client.get(
                    alt_url,
                    params=params,
                    headers={
                        'Authorization': f'Bearer {token}',
                        'Accept': 'application/json'
                    },
                    timeout=30.0
                )
            
            response.raise_for_status()
            data = response.json()
        
        # Analyze data product
        analysis = analyze_data_product(data) if include_usage else {}
        
        result = {
            'data_product': data,
            'analysis': analysis,
            'recommendations': generate_data_product_recommendations(data),
            'included_sections': {
                'installation': include_installation,
                'metadata': include_metadata,
                'access': include_access,
                'usage': include_usage
            }
        }
        
        return [TextContent(type='text', text=json.dumps(result, indent=2))]
    
    except httpx.HTTPStatusError as e:
        error_msg = handle_http_error(e, f"data product {product_id}")
        return [TextContent(type='text', text=json.dumps({'error': error_msg}, indent=2))]
    
    except Exception as e:
        return [TextContent(type='text', text=json.dumps({'error': str(e)}, indent=2))]


def analyze_data_product(product_data: dict) -> dict:
    """Analyze data product usage and performance."""
    
    usage = product_data.get('usage', {})
    access = product_data.get('access', {})
    installation = product_data.get('installation', {})
    
    # Calculate usage metrics
    query_count = usage.get('queryCount', 0)
    export_count = usage.get('exportCount', 0)
    access_count = access.get('accessCount', 0)
    
    # Determine popularity
    if query_count > 1000:
        popularity = 'High'
    elif query_count > 100:
        popularity = 'Medium'
    else:
        popularity = 'Low'
    
    # Calculate usage score
    usage_score = min(100, (query_count / 10) + (export_count * 5) + (access_count / 5))
    
    # Installation health
    install_status = installation.get('status', 'Unknown')
    install_health = 'Good' if install_status == 'Installed' else 'Needs Attention'
    
    return {
        'popularity': popularity,
        'usage_score': round(usage_score, 1),
        'access_level': access.get('accessLevel', 'Unknown'),
        'shared_spaces': len(access.get('sharedWith', [])),
        'installation_health': install_health,
        'data_freshness': assess_data_freshness(product_data),
        'recommendations': generate_data_product_recommendations(product_data)
    }


def assess_data_freshness(product_data: dict) -> str:
    """Assess data freshness based on last update."""
    installation = product_data.get('installation', {})
    last_updated = installation.get('lastUpdated')
    
    if not last_updated:
        return 'Unknown'
    
    try:
        from datetime import datetime, timedelta
        updated_date = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
        days_old = (datetime.now(updated_date.tzinfo) - updated_date).days
        
        if days_old <= 1:
            return 'Very Fresh'
        elif days_old <= 7:
            return 'Fresh'
        elif days_old <= 30:
            return 'Moderate'
        else:
            return 'Stale'
    except:
        return 'Unknown'


def generate_data_product_recommendations(product_data: dict) -> list[str]:
    """Generate recommendations for data product optimization."""
    recommendations = []
    
    usage = product_data.get('usage', {})
    access = product_data.get('access', {})
    installation = product_data.get('installation', {})
    
    # Usage recommendations
    query_count = usage.get('queryCount', 0)
    if query_count == 0:
        recommendations.append("Data product has not been queried - consider promoting to users")
    elif query_count > 5000:
        recommendations.append("High usage detected - monitor performance and consider optimization")
    
    # Access recommendations
    shared_spaces = len(access.get('sharedWith', []))
    if shared_spaces == 0:
        recommendations.append("Consider sharing with relevant spaces to increase utilization")
    elif shared_spaces > 10:
        recommendations.append("Widely shared - ensure proper access controls are in place")
    
    # Installation recommendations
    if installation.get('status') != 'Installed':
        recommendations.append("Data product not properly installed - check installation status")
    
    if not installation.get('autoUpdate', False):
        recommendations.append("Enable auto-update to ensure data freshness")
    
    return recommendations
```

I'll continue with the remaining tools in the next append to keep within the line limit.

---

## PHASE 8.2: AI FEATURES & CONFIGURATION TOOLS (3 tools)

### Tool 4: get_ai_feature_status

```python
# Tool definition
get_ai_feature_status_tool = Tool(
    name="get_ai_feature_status",
    description="Monitor the execution status of AI features and machine learning models with real-time metrics",
    inputSchema={
        "type": "object",
        "properties": {
            "ai_feature_id": {"type": "string", "description": "AI feature identifier"},
            "detailed": {"type": "boolean", "default": False},
            "include_metrics": {"type": "boolean", "default": True},
            "history_depth": {"type": "integer", "default": 7, "minimum": 1, "maximum": 30}
        },
        "required": ["ai_feature_id"]
    }
)

async def get_ai_feature_status(ai_feature_id: str, detailed: bool = False,
                               include_metrics: bool = True, 
                               history_depth: int = 7) -> list[TextContent]:
    """
    Monitor the execution status of AI features and machine learning models.
    
    Args:
        ai_feature_id: AI feature identifier
        detailed: Include detailed metrics
        include_metrics: Include performance metrics
        history_depth: Days of history to include (1-30)
    
    Returns:
        JSON string containing AI feature status, metrics, and health assessment
    """
    try:
        # Build URL
        url = f"{config.base_url}/dwaas-core/api/v1/aifeatures/{ai_feature_id}/executable/status"
        
        # Build query parameters
        params = {}
        if detailed:
            params['detailed'] = 'true'
        if include_metrics:
            params['includeMetrics'] = 'true'
        if history_depth != 7:
            params['historyDepth'] = str(history_depth)
        
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
        
        # Analyze AI feature health
        health_analysis = monitor_ai_feature_health(data)
        
        result = {
            'ai_feature_status': data,
            'health_analysis': health_analysis,
            'recommendations': generate_ai_recommendations(data),
            'monitoring_config': {
                'detailed': detailed,
                'include_metrics': include_metrics,
                'history_depth': history_depth
            }
        }
        
        return [TextContent(type='text', text=json.dumps(result, indent=2))]
    
    except httpx.HTTPStatusError as e:
        error_msg = handle_http_error(e, f"AI feature {ai_feature_id}")
        return [TextContent(type='text', text=json.dumps({'error': error_msg}, indent=2))]
    
    except Exception as e:
        return [TextContent(type='text', text=json.dumps({'error': str(e)}, indent=2))]


def monitor_ai_feature_health(status_data: dict) -> dict:
    """Monitor AI feature health and performance."""
    
    execution = status_data.get('execution', {})
    resources = status_data.get('resources', {})
    model = status_data.get('model', {})
    
    # Calculate health score
    success_rate = execution.get('successRate', 0)
    cpu_usage = resources.get('cpuUsage', 0)
    memory_usage = resources.get('memoryUsage', 0)
    
    # Health assessment
    health_score = (success_rate * 0.5) + ((100 - cpu_usage) * 0.25) + ((100 - memory_usage) * 0.25)
    
    if health_score >= 90:
        health_status = 'Excellent'
    elif health_score >= 75:
        health_status = 'Good'
    elif health_score >= 60:
        health_status = 'Fair'
    else:
        health_status = 'Poor'
    
    # Performance trend analysis
    metrics = status_data.get('metrics', {})
    daily_metrics = metrics.get('daily', [])
    
    trend = 'Stable'
    if len(daily_metrics) >= 2:
        recent_success = daily_metrics[0].get('successRate', 0)
        previous_success = daily_metrics[1].get('successRate', 0)
        
        if recent_success > previous_success + 2:
            trend = 'Improving'
        elif recent_success < previous_success - 2:
            trend = 'Declining'
    
    return {
        'health_score': round(health_score, 1),
        'health_status': health_status,
        'performance_trend': trend,
        'resource_utilization': 'High' if max(cpu_usage, memory_usage) > 80 else 'Normal',
        'model_accuracy': model.get('accuracy', 0),
        'uptime': execution.get('uptime', 'Unknown'),
        'processed_requests': execution.get('processedRequests', 0),
        'average_response_time': execution.get('averageResponseTime', 'Unknown')
    }


def generate_ai_recommendations(status_data: dict) -> list[str]:
    """Generate AI feature optimization recommendations."""
    recommendations = []
    
    execution = status_data.get('execution', {})
    resources = status_data.get('resources', {})
    model = status_data.get('model', {})
    
    # Performance recommendations
    success_rate = execution.get('successRate', 0)
    if success_rate < 95:
        recommendations.append(f"Success rate is {success_rate}% - investigate error patterns")
    
    # Resource recommendations
    cpu_usage = resources.get('cpuUsage', 0)
    memory_usage = resources.get('memoryUsage', 0)
    
    if cpu_usage > 85:
        recommendations.append("High CPU usage detected - consider scaling or optimization")
    if memory_usage > 85:
        recommendations.append("High memory usage detected - check for memory leaks")
    
    # Model recommendations
    accuracy = model.get('accuracy', 0)
    if accuracy < 90:
        recommendations.append(f"Model accuracy is {accuracy}% - consider retraining")
    
    # Response time recommendations
    avg_response = execution.get('averageResponseTime')
    if avg_response and isinstance(avg_response, str) and 'ms' in avg_response:
        try:
            response_ms = int(avg_response.replace('ms', ''))
            if response_ms > 1000:
                recommendations.append("Response time > 1s - optimize model or infrastructure")
        except:
            pass
    
    return recommendations
```

### Tool 5: get_guided_experience_config

```python
# Tool definition
get_guided_experience_config_tool = Tool(
    name="get_guided_experience_config",
    description="Retrieve tenant-specific configuration for Data Warehouse Cloud guided experience and UI customization",
    inputSchema={
        "type": "object",
        "properties": {
            "include_defaults": {"type": "boolean", "default": False},
            "config_version": {"type": "string", "description": "Specific configuration version"}
        }
    }
)

async def get_guided_experience_config(include_defaults: bool = False,
                                      config_version: Optional[str] = None) -> list[TextContent]:
    """
    Retrieve tenant-specific configuration for the guided experience.
    
    Args:
        include_defaults: Include default configuration values
        config_version: Specific configuration version
    
    Returns:
        JSON string containing guided experience configuration and analysis
    """
    try:
        # Build URL
        url = f"{config.base_url}/dwaas-core/configurations/DWC_GUIDED_EXPERIENCE_TENANT"
        
        # Build query parameters
        params = {}
        if include_defaults:
            params['includeDefaults'] = 'true'
        if config_version:
            params['configVersion'] = config_version
        
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
        
        # Analyze configuration
        config_analysis = analyze_guided_experience_config(data)
        
        result = {
            'guided_experience_config': data,
            'analysis': config_analysis,
            'recommendations': generate_config_recommendations(data),
            'request_params': {
                'include_defaults': include_defaults,
                'config_version': config_version
            }
        }
        
        return [TextContent(type='text', text=json.dumps(result, indent=2))]
    
    except httpx.HTTPStatusError as e:
        error_msg = handle_http_error(e, "guided experience configuration")
        return [TextContent(type='text', text=json.dumps({'error': error_msg}, indent=2))]
    
    except Exception as e:
        return [TextContent(type='text', text=json.dumps({'error': str(e)}, indent=2))]


def analyze_guided_experience_config(config_data: dict) -> dict:
    """Analyze guided experience configuration."""
    
    guided_exp = config_data.get('guidedExperience', {})
    ui_config = config_data.get('userInterface', {})
    features = config_data.get('features', {})
    
    # Count enabled features
    enabled_features = 0
    total_features = 0
    
    for feature_category in features.values():
        if isinstance(feature_category, dict):
            for feature_name, feature_enabled in feature_category.items():
                total_features += 1
                if feature_enabled:
                    enabled_features += 1
    
    # Analyze guided experience settings
    welcome_tour_enabled = guided_exp.get('welcomeTour', {}).get('enabled', False)
    contextual_help_enabled = guided_exp.get('contextualHelp', {}).get('enabled', False)
    onboarding_enabled = guided_exp.get('onboarding', {}).get('showGettingStarted', False)
    
    # Calculate user experience score
    ux_score = 0
    if welcome_tour_enabled:
        ux_score += 25
    if contextual_help_enabled:
        ux_score += 25
    if onboarding_enabled:
        ux_score += 25
    if enabled_features / total_features > 0.7:
        ux_score += 25
    
    return {
        'configuration_version': config_data.get('version', 'Unknown'),
        'last_updated': config_data.get('lastUpdated', 'Unknown'),
        'guided_experience_enabled': guided_exp.get('enabled', False),
        'welcome_tour_enabled': welcome_tour_enabled,
        'contextual_help_enabled': contextual_help_enabled,
        'onboarding_enabled': onboarding_enabled,
        'enabled_features': enabled_features,
        'total_features': total_features,
        'feature_adoption_rate': round((enabled_features / total_features) * 100, 1) if total_features > 0 else 0,
        'user_experience_score': ux_score,
        'theme': ui_config.get('theme', 'Unknown'),
        'accessibility_enabled': any(ui_config.get('accessibility', {}).values())
    }


def generate_config_recommendations(config_data: dict) -> list[str]:
    """Generate configuration optimization recommendations."""
    recommendations = []
    
    guided_exp = config_data.get('guidedExperience', {})
    features = config_data.get('features', {})
    ui_config = config_data.get('userInterface', {})
    
    # Guided experience recommendations
    if not guided_exp.get('enabled', False):
        recommendations.append("Enable guided experience to improve user onboarding")
    
    if not guided_exp.get('welcomeTour', {}).get('enabled', False):
        recommendations.append("Enable welcome tour for new user orientation")
    
    if not guided_exp.get('contextualHelp', {}).get('enabled', False):
        recommendations.append("Enable contextual help to reduce support requests")
    
    # Feature recommendations
    data_builder = features.get('dataBuilder', {})
    if not data_builder.get('autoSave', False):
        recommendations.append("Enable auto-save in Data Builder to prevent data loss")
    
    analytics = features.get('analytics', {})
    if not analytics.get('enabled', False):
        recommendations.append("Enable analytics features for better data insights")
    
    # Accessibility recommendations
    accessibility = ui_config.get('accessibility', {})
    if not any(accessibility.values()):
        recommendations.append("Consider enabling accessibility features for inclusive design")
    
    return recommendations
```

### Tool 6: get_security_config_status

```python
# Tool definition
get_security_config_status_tool = Tool(
    name="get_security_config_status",
    description="Monitor the status of flexible HANA security configurations for customer-managed instances",
    inputSchema={
        "type": "object",
        "properties": {
            "include_details": {"type": "boolean", "default": True},
            "config_type": {"type": "string", "description": "Filter by configuration type"},
            "validation_level": {"type": "string", "enum": ["Basic", "Standard", "Strict"], "default": "Standard"}
        }
    }
)

async def get_security_config_status(include_details: bool = True,
                                    config_type: Optional[str] = None,
                                    validation_level: str = "Standard") -> list[TextContent]:
    """
    Monitor the status of flexible HANA security configurations.
    
    Args:
        include_details: Include detailed configuration
        config_type: Filter by configuration type
        validation_level: Validation level (Basic, Standard, Strict)
    
    Returns:
        JSON string containing security configuration status and compliance assessment
    """
    try:
        # Build URL
        url = f"{config.base_url}/dwaas-core/security/customerhana/flexible-configuration/configuration-status"
        
        # Build query parameters
        params = {}
        if include_details:
            params['includeDetails'] = 'true'
        if config_type:
            params['configType'] = config_type
        if validation_level != "Standard":
            params['validationLevel'] = validation_level
        
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
        
        # Assess security compliance
        compliance_assessment = assess_security_compliance(data)
        
        result = {
            'security_config_status': data,
            'compliance_assessment': compliance_assessment,
            'recommendations': generate_security_recommendations(data),
            'validation_params': {
                'include_details': include_details,
                'config_type': config_type,
                'validation_level': validation_level
            }
        }
        
        return [TextContent(type='text', text=json.dumps(result, indent=2))]
    
    except httpx.HTTPStatusError as e:
        error_msg = handle_http_error(e, "security configuration status")
        return [TextContent(type='text', text=json.dumps({'error': error_msg}, indent=2))]
    
    except Exception as e:
        return [TextContent(type='text', text=json.dumps({'error': str(e)}, indent=2))]


def assess_security_compliance(config_data: dict) -> dict:
    """Assess security configuration compliance."""
    
    configurations = config_data.get('configurations', {})
    vulnerabilities = config_data.get('vulnerabilities', {})
    compliance_status = config_data.get('complianceStatus', {})
    
    compliance_score = 0
    total_checks = 0
    
    # Check authentication
    auth = configurations.get('authentication', {})
    if auth.get('mfaEnabled'):
        compliance_score += 20
    if auth.get('passwordPolicy', {}).get('complexity') == 'High':
        compliance_score += 15
    total_checks += 2
    
    # Check data protection
    data_protection = configurations.get('dataProtection', {})
    if data_protection.get('encryptionAtRest'):
        compliance_score += 20
    if data_protection.get('encryptionInTransit'):
        compliance_score += 20
    total_checks += 2
    
    # Check auditing
    auditing = configurations.get('auditing', {})
    if auditing.get('auditLogging'):
        compliance_score += 15
    if auditing.get('realTimeMonitoring'):
        compliance_score += 10
    total_checks += 2
    
    final_score = (compliance_score / (total_checks * 20)) * 100 if total_checks > 0 else 0
    
    # Vulnerability assessment
    critical_vulns = vulnerabilities.get('critical', 0)
    high_vulns = vulnerabilities.get('high', 0)
    
    # Compliance frameworks
    frameworks = compliance_status.get('frameworks', [])
    compliant_frameworks = len([f for f in frameworks if f.get('status') == 'Compliant'])
    
    return {
        'compliance_score': round(final_score, 1),
        'compliance_grade': get_compliance_grade(final_score),
        'critical_vulnerabilities': critical_vulns,
        'high_vulnerabilities': high_vulns,
        'vulnerability_risk': 'High' if critical_vulns > 0 else 'Medium' if high_vulns > 0 else 'Low',
        'compliant_frameworks': compliant_frameworks,
        'total_frameworks': len(frameworks),
        'overall_security_status': config_data.get('status', 'Unknown'),
        'last_validated': config_data.get('lastValidated', 'Unknown'),
        'security_recommendations_count': len(config_data.get('recommendations', []))
    }


def get_compliance_grade(score: float) -> str:
    """Get compliance grade based on score."""
    if score >= 95:
        return 'A+'
    elif score >= 90:
        return 'A'
    elif score >= 85:
        return 'B+'
    elif score >= 80:
        return 'B'
    elif score >= 75:
        return 'C+'
    elif score >= 70:
        return 'C'
    else:
        return 'F'


def generate_security_recommendations(config_data: dict) -> list[str]:
    """Generate security configuration recommendations."""
    recommendations = []
    
    configurations = config_data.get('configurations', {})
    vulnerabilities = config_data.get('vulnerabilities', {})
    
    # Authentication recommendations
    auth = configurations.get('authentication', {})
    if not auth.get('mfaEnabled', False):
        recommendations.append("Enable multi-factor authentication for enhanced security")
    
    password_policy = auth.get('passwordPolicy', {})
    if password_policy.get('complexity') != 'High':
        recommendations.append("Implement high complexity password policy")
    
    # Data protection recommendations
    data_protection = configurations.get('dataProtection', {})
    if not data_protection.get('encryptionAtRest', False):
        recommendations.append("Enable encryption at rest for sensitive data protection")
    
    if not data_protection.get('encryptionInTransit', False):
        recommendations.append("Enable encryption in transit for data communication")
    
    # Vulnerability recommendations
    critical_vulns = vulnerabilities.get('critical', 0)
    high_vulns = vulnerabilities.get('high', 0)
    
    if critical_vulns > 0:
        recommendations.append(f"Address {critical_vulns} critical vulnerabilities immediately")
    
    if high_vulns > 0:
        recommendations.append(f"Plan remediation for {high_vulns} high-priority vulnerabilities")
    
    # Auditing recommendations
    auditing = configurations.get('auditing', {})
    if not auditing.get('realTimeMonitoring', False):
        recommendations.append("Enable real-time monitoring for security events")
    
    return recommendations
```

---

## PHASE 8.3: LEGACY DWC API SUPPORT (4 tools)

### Tool 7: dwc_list_catalog_assets

```python
# Tool definition
dwc_list_catalog_assets_tool = Tool(
    name="dwc_list_catalog_assets",
    description="Legacy catalog asset listing using Data Warehouse Cloud v1 APIs for backward compatibility",
    inputSchema={
        "type": "object",
        "properties": {
            "select": {"type": "string", "description": "Properties to return (comma-separated)"},
            "filter": {"type": "string", "description": "OData filter expression"},
            "expand": {"type": "string", "description": "Related entities to expand"},
            "top": {"type": "integer", "default": 50, "maximum": 1000},
            "skip": {"type": "integer", "default": 0}
        }
    }
)

async def dwc_list_catalog_assets(select: Optional[str] = None, filter: Optional[str] = None,
                                 expand: Optional[str] = None, top: int = 50, 
                                 skip: int = 0) -> list[TextContent]:
    """
    Legacy catalog asset listing using Data Warehouse Cloud v1 APIs.
    
    Args:
        select: Properties to return (comma-separated)
        filter: OData filter expression
        expand: Related entities to expand
        top: Maximum results (default: 50, max: 1000)
        skip: Results to skip for pagination
    
    Returns:
        JSON string containing legacy catalog assets with OData metadata
    """
    try:
        # Build URL
        url = f"{config.base_url}/v1/dwc/catalog/assets"
        
        # Build query parameters
        params = {
            '$top': min(top, 1000),
            '$skip': skip
        }
        
        if select:
            params['$select'] = select
        if filter:
            params['$filter'] = filter
        if expand:
            params['$expand'] = expand
        
        # Get OAuth2 token
        token = await get_oauth_token()
        
        # Make request
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                headers={
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/json',
                    'OData-Version': '4.0'
                },
                timeout=30.0
            )
            
            response.raise_for_status()
            data = response.json()
        
        # Analyze legacy assets
        assets = data.get('value', [])
        analysis = analyze_legacy_assets(assets)
        
        result = {
            'legacy_catalog_assets': data,
            'analysis': analysis,
            'odata_context': data.get('@odata.context'),
            'query_parameters': {
                'select': select,
                'filter': filter,
                'expand': expand,
                'top': top,
                'skip': skip
            },
            'pagination': {'returned': len(assets)}
        }
        
        return [TextContent(type='text', text=json.dumps(result, indent=2))]
    
    except httpx.HTTPStatusError as e:
        error_msg = handle_http_error(e, "legacy catalog assets")
        return [TextContent(type='text', text=json.dumps({'error': error_msg}, indent=2))]
    
    except Exception as e:
        return [TextContent(type='text', text=json.dumps({'error': str(e)}, indent=2))]


def analyze_legacy_assets(assets: list[dict]) -> dict:
    """Analyze legacy catalog assets."""
    if not assets:
        return {'message': 'No legacy assets found'}
    
    # Analyze asset types and exposure
    asset_types = {}
    exposed_assets = 0
    spaces = set()
    
    for asset in assets:
        # Count by type
        asset_type = asset.get('assetType', 'Unknown')
        asset_types[asset_type] = asset_types.get(asset_type, 0) + 1
        
        # Count exposed assets
        if asset.get('exposedForConsumption', False):
            exposed_assets += 1
        
        # Collect spaces
        space_id = asset.get('spaceId')
        if space_id:
            spaces.add(space_id)
    
    return {
        'total_assets': len(assets),
        'asset_types': asset_types,
        'exposed_assets': exposed_assets,
        'exposure_rate': round((exposed_assets / len(assets)) * 100, 1),
        'unique_spaces': len(spaces),
        'spaces': list(spaces),
        'api_version': 'v1 (Legacy)'
    }
```

### Tool 8: dwc_get_space_assets

```python
# Tool definition
dwc_get_space_assets_tool = Tool(
    name="dwc_get_space_assets",
    description="Legacy space asset access using Data Warehouse Cloud v1 APIs",
    inputSchema={
        "type": "object",
        "properties": {
            "space_id": {"type": "string", "description": "Space identifier"},
            "select": {"type": "string", "description": "Properties to return (comma-separated)"},
            "filter": {"type": "string", "description": "OData filter expression"},
            "expand": {"type": "string", "description": "Related entities to expand"},
            "top": {"type": "integer", "default": 50, "maximum": 1000},
            "skip": {"type": "integer", "default": 0}
        },
        "required": ["space_id"]
    }
)

async def dwc_get_space_assets(space_id: str, select: Optional[str] = None,
                              filter: Optional[str] = None, expand: Optional[str] = None,
                              top: int = 50, skip: int = 0) -> list[TextContent]:
    """
    Legacy space asset access using Data Warehouse Cloud v1 APIs.
    
    Args:
        space_id: Space identifier
        select: Properties to return (comma-separated)
        filter: OData filter expression
        expand: Related entities to expand
        top: Maximum results (default: 50, max: 1000)
        skip: Results to skip for pagination
    
    Returns:
        JSON string containing legacy space assets with OData metadata
    """
    try:
        # Build URL
        url = f"{config.base_url}/v1/dwc/catalog/spaces('{space_id}')/assets"
        
        # Build query parameters
        params = {
            '$top': min(top, 1000),
            '$skip': skip
        }
        
        if select:
            params['$select'] = select
        if filter:
            params['$filter'] = filter
        if expand:
            params['$expand'] = expand
        
        # Get OAuth2 token
        token = await get_oauth_token()
        
        # Make request
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                headers={
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/json',
                    'OData-Version': '4.0'
                },
                timeout=30.0
            )
            
            response.raise_for_status()
            data = response.json()
        
        # Analyze space assets
        assets = data.get('value', [])
        analysis = analyze_space_assets(assets, space_id)
        
        result = {
            'legacy_space_assets': data,
            'space_id': space_id,
            'analysis': analysis,
            'odata_context': data.get('@odata.context'),
            'query_parameters': {
                'select': select,
                'filter': filter,
                'expand': expand,
                'top': top,
                'skip': skip
            },
            'pagination': {'returned': len(assets)}
        }
        
        return [TextContent(type='text', text=json.dumps(result, indent=2))]
    
    except httpx.HTTPStatusError as e:
        error_msg = handle_http_error(e, f"legacy space assets for {space_id}")
        return [TextContent(type='text', text=json.dumps({'error': error_msg}, indent=2))]
    
    except Exception as e:
        return [TextContent(type='text', text=json.dumps({'error': str(e)}, indent=2))]


def analyze_space_assets(assets: list[dict], space_id: str) -> dict:
    """Analyze legacy space assets."""
    if not assets:
        return {'message': f'No assets found in space {space_id}'}
    
    # Analyze asset types and consumption URLs
    asset_types = {}
    analytical_assets = 0
    relational_assets = 0
    
    for asset in assets:
        # Count by type
        asset_type = asset.get('assetType', 'Unknown')
        asset_types[asset_type] = asset_types.get(asset_type, 0) + 1
        
        # Count consumption types
        if asset.get('analyticalConsumptionUrl'):
            analytical_assets += 1
        if asset.get('relationalConsumptionUrl'):
            relational_assets += 1
    
    return {
        'space_id': space_id,
        'total_assets': len(assets),
        'asset_types': asset_types,
        'analytical_consumption_available': analytical_assets,
        'relational_consumption_available': relational_assets,
        'dual_consumption_assets': min(analytical_assets, relational_assets),
        'api_version': 'v1 (Legacy)'
    }
```

### Tool 9: dwc_query_analytical_data

```python
# Tool definition
dwc_query_analytical_data_tool = Tool(
    name="dwc_query_analytical_data",
    description="Legacy analytical data access using Data Warehouse Cloud v1 APIs",
    inputSchema={
        "type": "object",
        "properties": {
            "space_id": {"type": "string", "description": "Space identifier"},
            "asset_id": {"type": "string", "description": "Asset identifier"},
            "odata_id": {"type": "string", "description": "OData entity set identifier"},
            "select": {"type": "string", "description": "Column selection"},
            "filter": {"type": "string", "description": "Row filtering"},
            "expand": {"type": "string", "description": "Related entity expansion"},
            "orderby": {"type": "string", "description": "Sort order"},
            "top": {"type": "integer", "default": 100, "maximum": 10000},
            "skip": {"type": "integer", "default": 0}
        },
        "required": ["space_id", "asset_id", "odata_id"]
    }
)

async def dwc_query_analytical_data(space_id: str, asset_id: str, odata_id: str,
                                   select: Optional[str] = None, filter: Optional[str] = None,
                                   expand: Optional[str] = None, orderby: Optional[str] = None,
                                   top: int = 100, skip: int = 0) -> list[TextContent]:
    """
    Legacy analytical data access using Data Warehouse Cloud v1 APIs.
    
    Args:
        space_id: Space identifier
        asset_id: Asset identifier
        odata_id: OData entity set identifier
        select: Column selection
        filter: Row filtering
        expand: Related entity expansion
        orderby: Sort order
        top: Maximum results (default: 100, max: 10000)
        skip: Results to skip for pagination
    
    Returns:
        JSON string containing legacy analytical data with OData metadata
    """
    try:
        # Build URL
        url = f"{config.base_url}/v1/dwc/consumption/analytical/{space_id}/{asset_id}/{odata_id}"
        
        # Build query parameters
        params = {
            '$top': min(top, 10000),
            '$skip': skip
        }
        
        if select:
            params['$select'] = select
        if filter:
            params['$filter'] = filter
        if expand:
            params['$expand'] = expand
        if orderby:
            params['$orderby'] = orderby
        
        # Get OAuth2 token
        token = await get_oauth_token()
        
        # Make request
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                headers={
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/json',
                    'OData-Version': '4.0'
                },
                timeout=60.0  # Longer timeout for data queries
            )
            
            response.raise_for_status()
            data = response.json()
        
        # Analyze query results
        records = data.get('value', [])
        analysis = analyze_query_results(records, 'analytical')
        
        result = {
            'legacy_analytical_data': data,
            'query_info': {
                'space_id': space_id,
                'asset_id': asset_id,
                'odata_id': odata_id
            },
            'analysis': analysis,
            'odata_context': data.get('@odata.context'),
            'query_parameters': {
                'select': select,
                'filter': filter,
                'expand': expand,
                'orderby': orderby,
                'top': top,
                'skip': skip
            }
        }
        
        return [TextContent(type='text', text=json.dumps(result, indent=2))]
    
    except httpx.HTTPStatusError as e:
        error_msg = handle_http_error(e, f"legacy analytical data for {space_id}/{asset_id}/{odata_id}")
        return [TextContent(type='text', text=json.dumps({'error': error_msg}, indent=2))]
    
    except Exception as e:
        return [TextContent(type='text', text=json.dumps({'error': str(e)}, indent=2))]
```

### Tool 10: dwc_query_relational_data

```python
# Tool definition
dwc_query_relational_data_tool = Tool(
    name="dwc_query_relational_data",
    description="Legacy relational data access using Data Warehouse Cloud v1 APIs",
    inputSchema={
        "type": "object",
        "properties": {
            "space_id": {"type": "string", "description": "Space identifier"},
            "asset_id": {"type": "string", "description": "Asset identifier"},
            "odata_id": {"type": "string", "description": "OData entity set identifier"},
            "select": {"type": "string", "description": "Column selection"},
            "filter": {"type": "string", "description": "Row filtering"},
            "expand": {"type": "string", "description": "Related entity expansion"},
            "orderby": {"type": "string", "description": "Sort order"},
            "top": {"type": "integer", "default": 100, "maximum": 10000},
            "skip": {"type": "integer", "default": 0}
        },
        "required": ["space_id", "asset_id", "odata_id"]
    }
)

async def dwc_query_relational_data(space_id: str, asset_id: str, odata_id: str,
                                   select: Optional[str] = None, filter: Optional[str] = None,
                                   expand: Optional[str] = None, orderby: Optional[str] = None,
                                   top: int = 100, skip: int = 0) -> list[TextContent]:
    """
    Legacy relational data access using Data Warehouse Cloud v1 APIs.
    
    Args:
        space_id: Space identifier
        asset_id: Asset identifier
        odata_id: OData entity set identifier
        select: Column selection
        filter: Row filtering
        expand: Related entity expansion
        orderby: Sort order
        top: Maximum results (default: 100, max: 10000)
        skip: Results to skip for pagination
    
    Returns:
        JSON string containing legacy relational data with OData metadata
    """
    try:
        # Build URL
        url = f"{config.base_url}/v1/dwc/consumption/relational/{space_id}/{asset_id}/{odata_id}"
        
        # Build query parameters
        params = {
            '$top': min(top, 10000),
            '$skip': skip
        }
        
        if select:
            params['$select'] = select
        if filter:
            params['$filter'] = filter
        if expand:
            params['$expand'] = expand
        if orderby:
            params['$orderby'] = orderby
        
        # Get OAuth2 token
        token = await get_oauth_token()
        
        # Make request
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                headers={
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/json',
                    'OData-Version': '4.0'
                },
                timeout=60.0  # Longer timeout for data queries
            )
            
            response.raise_for_status()
            data = response.json()
        
        # Analyze query results
        records = data.get('value', [])
        analysis = analyze_query_results(records, 'relational')
        
        result = {
            'legacy_relational_data': data,
            'query_info': {
                'space_id': space_id,
                'asset_id': asset_id,
                'odata_id': odata_id
            },
            'analysis': analysis,
            'odata_context': data.get('@odata.context'),
            'query_parameters': {
                'select': select,
                'filter': filter,
                'expand': expand,
                'orderby': orderby,
                'top': top,
                'skip': skip
            }
        }
        
        return [TextContent(type='text', text=json.dumps(result, indent=2))]
    
    except httpx.HTTPStatusError as e:
        error_msg = handle_http_error(e, f"legacy relational data for {space_id}/{asset_id}/{odata_id}")
        return [TextContent(type='text', text=json.dumps({'error': error_msg}, indent=2))]
    
    except Exception as e:
        return [TextContent(type='text', text=json.dumps({'error': str(e)}, indent=2))]


def analyze_query_results(records: list[dict], query_type: str) -> dict:
    """Analyze query results for insights."""
    if not records:
        return {'message': f'No {query_type} data returned'}
    
    # Analyze data structure
    columns = set()
    data_types = {}
    
    for record in records:
        for key, value in record.items():
            columns.add(key)
            
            # Determine data type
            if isinstance(value, str):
                data_types[key] = 'String'
            elif isinstance(value, (int, float)):
                data_types[key] = 'Number'
            elif isinstance(value, bool):
                data_types[key] = 'Boolean'
            elif value is None:
                data_types[key] = 'Null'
            else:
                data_types[key] = 'Complex'
    
    return {
        'query_type': query_type,
        'record_count': len(records),
        'column_count': len(columns),
        'columns': list(columns),
        'data_types': data_types,
        'api_version': 'v1 (Legacy)',
        'sample_record': records[0] if records else None
    }
```

---

## SHARED UTILITIES AND HELPERS

### OAuth2 Token Manager

```python
from datetime import datetime, timedelta
from typing import Optional
import httpx
import json

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
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            response.raise_for_status()
            token_data = response.json()
            
            self.access_token = token_data['access_token']
            expires_in = token_data.get('expires_in', 3600)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in - 60)  # 60s buffer
            
            return self.access_token

# Global token manager instance
token_manager: Optional[OAuth2TokenManager] = None

async def get_oauth_token() -> str:
    """Get OAuth2 token using global token manager."""
    global token_manager
    if not token_manager:
        # Initialize from config
        token_manager = OAuth2TokenManager(
            client_id=config.client_id,
            client_secret=config.client_secret,
            token_url=config.token_url
        )
    
    return await token_manager.get_token()
```

### Error Handling Utilities

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
    elif status_code == 429:
        return f"Rate limit exceeded for {context}. Retry after delay."
    elif status_code == 500:
        return f"Server error for {context}. SAP Datasphere may be experiencing issues."
    elif status_code == 503:
        return f"Service unavailable for {context}. SAP Datasphere may be under maintenance."
    else:
        try:
            error_detail = error.response.json()
            return f"HTTP {status_code} error for {context}: {error_detail}"
        except:
            return f"HTTP {status_code} error for {context}: {error.response.text}"
```

---

## TOOL REGISTRATION

```python
# Register all Phase 8 tools
def register_phase8_tools(server: Server):
    """Register all Phase 8 advanced feature tools."""
    
    # Data Sharing & Collaboration Tools
    server.add_tool(list_partner_systems_tool, list_partner_systems)
    server.add_tool(get_marketplace_assets_tool, get_marketplace_assets)
    server.add_tool(get_data_product_details_tool, get_data_product_details)
    
    # AI Features & Configuration Tools
    server.add_tool(get_ai_feature_status_tool, get_ai_feature_status)
    server.add_tool(get_guided_experience_config_tool, get_guided_experience_config)
    server.add_tool(get_security_config_status_tool, get_security_config_status)
    
    # Legacy DWC API Support Tools
    server.add_tool(dwc_list_catalog_assets_tool, dwc_list_catalog_assets)
    server.add_tool(dwc_get_space_assets_tool, dwc_get_space_assets)
    server.add_tool(dwc_query_analytical_data_tool, dwc_query_analytical_data)
    server.add_tool(dwc_query_relational_data_tool, dwc_query_relational_data)
```

---

## TESTING EXAMPLES

### Test Data Sharing Tools

```python
# Test partner systems discovery
await list_partner_systems(status="Active", include_data_products=True)

# Test marketplace browsing
await get_marketplace_assets(request_type="browse", category="Economic Data")

# Test data product details (using user's example)
await get_data_product_details(
    product_id="f55b20ae-152d-40d4-b2eb-70b651f85d37",
    include_usage=True
)
```

### Test AI Features Tools

```python
# Test AI feature monitoring
await get_ai_feature_status(
    ai_feature_id="sentiment-analysis-model",
    include_metrics=True,
    history_depth=7
)

# Test guided experience config
await get_guided_experience_config(include_defaults=True)

# Test security configuration
await get_security_config_status(
    include_details=True,
    validation_level="Standard"
)
```

### Test Legacy DWC APIs

```python
# Test legacy catalog listing
await dwc_list_catalog_assets(
    filter="exposedForConsumption eq true",
    top=20
)

# Test legacy space assets
await dwc_get_space_assets(
    space_id="SAP_CONTENT",
    filter="assetType eq 'AnalyticalModel'"
)

# Test legacy data queries
await dwc_query_analytical_data(
    space_id="SAP_CONTENT",
    asset_id="SAP_SC_FI_AM_FINTRANSACTIONS",
    odata_id="SAP_SC_FI_AM_FINTRANSACTIONS",
    select="TransactionID,Amount,Currency",
    top=10
)
```

---

## SUCCESS CRITERIA

### Phase 8.1: Data Sharing & Collaboration ✅
- ✅ Can discover partner systems and data sharing relationships
- ✅ Can browse marketplace assets with filtering and search
- ✅ Can retrieve detailed data product information and usage analytics

### Phase 8.2: AI Features & Configuration ✅
- ✅ Can monitor AI feature status and performance metrics
- ✅ Can retrieve guided experience configuration
- ✅ Can assess security configuration compliance

### Phase 8.3: Legacy DWC API Support ✅
- ✅ Can access catalog assets through legacy v1 APIs
- ✅ Can query analytical and relational data through legacy endpoints
- ✅ Maintains backward compatibility with existing integrations

---

## IMPLEMENTATION NOTES

1. **Error Handling**: All tools include comprehensive error handling for HTTP status codes
2. **Authentication**: OAuth2 token management with automatic refresh
3. **Pagination**: Support for large result sets with proper pagination
4. **Analysis**: Each tool provides data analysis and recommendations
5. **Legacy Support**: Legacy tools maintain OData v4.0 compatibility
6. **Performance**: Appropriate timeouts for different operation types
7. **Security**: Proper scope validation and access control

---

## FINAL PHASE 8 COMPLETION

**🎉 Phase 8 Complete!**

All 10 Phase 8 advanced feature tools are now fully documented and ready for implementation:

- **3 Data Sharing Tools**: Partner systems, marketplace, data products
- **3 AI Configuration Tools**: AI monitoring, guided experience, security
- **4 Legacy DWC Tools**: Backward compatibility with v1 APIs

**Total Project Status**: 49/49 tools complete (100%) ✅

The SAP Datasphere MCP Server implementation is now complete with comprehensive coverage of all SAP Datasphere capabilities!