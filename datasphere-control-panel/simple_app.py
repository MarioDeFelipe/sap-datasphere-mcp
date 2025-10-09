#!/usr/bin/env python3
"""
Simple SAP Datasphere Control Panel - Lambda Version
Pure Python without FastAPI for better Lambda compatibility
"""

import json
import logging
import base64
from datetime import datetime
from typing import Dict, List, Any, Optional
import requests
import boto3

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("datasphere-control-panel")

# Configuration
DATASPHERE_CONFIG = {
    "base_url": "https://academydatasphere.eu10.hcs.cloud.sap",
    "space_name": "GE230769",
    "basic_auth": {
        "username": "GE230769#AWSUSER",
        "password": "D^1(52u37Y)hfMUZ+YC[5)Wq<eh_T@.n"
    }
}

class DatasphereAPIClient:
    """Client for accessing SAP Datasphere APIs"""
    
    def __init__(self):
        self.session = requests.Session()
        self.setup_authentication()
    
    def setup_authentication(self):
        """Setup basic authentication"""
        username = DATASPHERE_CONFIG["basic_auth"]["username"]
        password = DATASPHERE_CONFIG["basic_auth"]["password"]
        
        auth_header = base64.b64encode(f"{username}:{password}".encode()).decode()
        self.session.headers.update({
            'Authorization': f'Basic {auth_header}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def get_catalog_assets(self) -> List[Dict[str, Any]]:
        """Get catalog assets from Datasphere"""
        try:
            url = f"{DATASPHERE_CONFIG['base_url']}/api/v1/dwc/catalog"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                assets = data.get('value', [])
                
                # Filter by space
                space_assets = [
                    asset for asset in assets 
                    if asset.get('spaceName') == DATASPHERE_CONFIG['space_name']
                ]
                
                return space_assets
            else:
                logger.error(f"Failed to fetch catalog: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching catalog: {e}")
            return []

class AWSGlueClient:
    """Client for AWS Glue operations"""
    
    def __init__(self):
        self.glue_client = boto3.client('glue', region_name='us-east-1')
        self.database_name = "datasphere_ge230769"
    
    def get_glue_tables(self) -> List[Dict[str, Any]]:
        """Get tables from AWS Glue catalog"""
        try:
            response = self.glue_client.get_tables(DatabaseName=self.database_name)
            tables = response.get('TableList', [])
            
            return [
                {
                    "name": table['Name'],
                    "description": table.get('Description', ''),
                    "columns": len(table.get('StorageDescriptor', {}).get('Columns', [])),
                    "datasphere_asset": table.get('Parameters', {}).get('datasphere_asset', ''),
                    "datasphere_label": table.get('Parameters', {}).get('datasphere_label', '')
                }
                for table in tables
            ]
            
        except Exception as e:
            logger.error(f"Error fetching Glue tables: {e}")
            return []

# Initialize clients
datasphere_client = DatasphereAPIClient()
glue_client = AWSGlueClient()

def create_html_response(title: str, content: str) -> Dict[str, Any]:
    """Create an HTML response"""
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Inter', 'Segoe UI', sans-serif;
                background: #0a0a0a;
                color: #e0e0e0;
                min-height: 100vh;
                background-image: 
                    radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.1) 0%, transparent 50%);
            }}
            
            .header {{
                background: rgba(26, 26, 26, 0.9);
                border-bottom: 1px solid rgba(120, 255, 119, 0.2);
                padding: 20px 0;
                backdrop-filter: blur(10px);
            }}
            
            .header-content {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 20px;
                display: flex;
                align-items: center;
                gap: 20px;
            }}
            
            .logo {{
                width: 50px;
                height: 50px;
                background: #1a1a1a;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                border: 2px solid #ff77c6;
                position: relative;
            }}
            
            .alien-head {{
                width: 25px;
                height: 30px;
                background: #2a2a2a;
                border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%;
                position: relative;
            }}
            
            .alien-eye {{
                position: absolute;
                width: 6px;
                height: 4px;
                background: #78ff77;
                border-radius: 50%;
                top: 12px;
                box-shadow: 0 0 5px rgba(120, 255, 119, 0.8);
            }}
            
            .alien-eye.left {{ left: 5px; }}
            .alien-eye.right {{ right: 5px; }}
            
            .header h1 {{
                font-size: 1.8em;
                background: linear-gradient(135deg, #78ff77 0%, #ff77c6 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            
            .status-badge {{
                padding: 5px 15px;
                background: rgba(120, 255, 119, 0.2);
                color: #78ff77;
                border-radius: 20px;
                font-size: 0.9em;
                border: 1px solid rgba(120, 255, 119, 0.3);
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 30px 20px;
            }}
            
            .card {{
                background: rgba(26, 26, 26, 0.8);
                border: 1px solid rgba(120, 255, 119, 0.2);
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 20px;
                backdrop-filter: blur(10px);
            }}
            
            .card h2 {{
                color: #78ff77;
                font-size: 1.4em;
                margin-bottom: 15px;
            }}
            
            .btn {{
                background: linear-gradient(135deg, #78ff77 0%, #ff77c6 100%);
                color: #000;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
                margin: 10px 10px 10px 0;
            }}
            
            .btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(120, 255, 119, 0.3);
            }}
            
            .asset-item {{
                padding: 15px;
                margin: 10px 0;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                border-left: 3px solid #78ff77;
            }}
            
            .asset-item h4 {{
                color: #78ff77;
                margin-bottom: 5px;
            }}
            
            .asset-item p {{
                color: #c0c0c0;
                font-size: 0.9em;
                margin: 3px 0;
            }}
            
            .nav-links {{
                margin: 20px 0;
            }}
            
            .nav-links a {{
                color: #78ff77;
                text-decoration: none;
                margin-right: 20px;
                padding: 8px 16px;
                border: 1px solid rgba(120, 255, 119, 0.3);
                border-radius: 5px;
                transition: all 0.3s ease;
            }}
            
            .nav-links a:hover {{
                background: rgba(120, 255, 119, 0.1);
                border-color: rgba(120, 255, 119, 0.5);
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-content">
                <div class="logo">
                    <div class="alien-head">
                        <div class="alien-eye left"></div>
                        <div class="alien-eye right"></div>
                    </div>
                </div>
                <h1>SAP Datasphere Control Panel</h1>
                <div class="status-badge">LIVE</div>
            </div>
        </div>
        
        <div class="container">
            {content}
        </div>
    </body>
    </html>
    """
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
            'Cache-Control': 'no-cache'
        },
        'body': html
    }

def create_json_response(data: Any, status_code: int = 200) -> Dict[str, Any]:
    """Create a JSON response"""
    
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        'body': json.dumps(data)
    }

def handle_dashboard() -> Dict[str, Any]:
    """Handle dashboard request"""
    
    content = """
    <div class="nav-links">
        <a href="/assets">📊 View Assets</a>
        <a href="/glue">🔧 Glue Tables</a>
        <a href="/status">📈 System Status</a>
    </div>
    
    <div class="card">
        <h2>🔍 Asset Discovery</h2>
        <p>Discover and explore assets in your Datasphere space.</p>
        <a href="/assets" class="btn">View Assets</a>
    </div>
    
    <div class="card">
        <h2>🔄 AWS Glue Integration</h2>
        <p>View synchronized tables in your AWS Glue catalog.</p>
        <a href="/glue" class="btn">View Glue Tables</a>
    </div>
    
    <div class="card">
        <h2>📊 System Status</h2>
        <p>Monitor the health of your Datasphere integration.</p>
        <a href="/status" class="btn">Check Status</a>
    </div>
    """
    
    return create_html_response("SAP Datasphere Control Panel", content)

def handle_assets() -> Dict[str, Any]:
    """Handle assets request"""
    
    try:
        assets = datasphere_client.get_catalog_assets()
        
        if not assets:
            content = """
            <div class="nav-links">
                <a href="/">🏠 Dashboard</a>
                <a href="/glue">🔧 Glue Tables</a>
                <a href="/status">📈 System Status</a>
            </div>
            
            <div class="card">
                <h2>📊 Datasphere Assets</h2>
                <p>⚠️ No assets found or connection issue. This might be due to authentication challenges with the Datasphere API.</p>
                <p>However, your AWS Glue integration is working! Check the <a href="/glue" style="color: #78ff77;">Glue Tables</a> to see your synchronized data.</p>
            </div>
            """
        else:
            asset_html = ""
            for asset in assets:
                asset_html += f"""
                <div class="asset-item">
                    <h4>{asset.get('label', asset.get('name', 'Unknown'))}</h4>
                    <p><strong>Name:</strong> {asset.get('name', 'N/A')}</p>
                    <p><strong>Space:</strong> {asset.get('spaceName', 'N/A')}</p>
                    <p><strong>Type:</strong> {'Analytical' if asset.get('supportsAnalyticalQueries') else 'Relational'}</p>
                </div>
                """
            
            content = f"""
            <div class="nav-links">
                <a href="/">🏠 Dashboard</a>
                <a href="/glue">🔧 Glue Tables</a>
                <a href="/status">📈 System Status</a>
            </div>
            
            <div class="card">
                <h2>📊 Datasphere Assets ({len(assets)} found)</h2>
                <p>Assets discovered in space: <strong>{DATASPHERE_CONFIG['space_name']}</strong></p>
                {asset_html}
            </div>
            """
        
        return create_html_response("Datasphere Assets", content)
        
    except Exception as e:
        logger.error(f"Error in handle_assets: {e}")
        content = f"""
        <div class="nav-links">
            <a href="/">🏠 Dashboard</a>
            <a href="/glue">🔧 Glue Tables</a>
            <a href="/status">📈 System Status</a>
        </div>
        
        <div class="card">
            <h2>❌ Error Loading Assets</h2>
            <p>Error: {str(e)}</p>
        </div>
        """
        return create_html_response("Error", content)

def handle_glue() -> Dict[str, Any]:
    """Handle Glue tables request"""
    
    try:
        tables = glue_client.get_glue_tables()
        
        if not tables:
            content = """
            <div class="nav-links">
                <a href="/">🏠 Dashboard</a>
                <a href="/assets">📊 Assets</a>
                <a href="/status">📈 System Status</a>
            </div>
            
            <div class="card">
                <h2>🔧 AWS Glue Tables</h2>
                <p>No tables found in the Glue catalog database: <strong>datasphere_ge230769</strong></p>
                <p>Tables may have been created in a different database or region.</p>
            </div>
            """
        else:
            table_html = ""
            for table in tables:
                table_html += f"""
                <div class="asset-item">
                    <h4>{table.get('name', 'Unknown')}</h4>
                    <p><strong>Description:</strong> {table.get('description', 'N/A')}</p>
                    <p><strong>Columns:</strong> {table.get('columns', 0)}</p>
                    <p><strong>Source Asset:</strong> {table.get('datasphere_label') or table.get('datasphere_asset', 'N/A')}</p>
                </div>
                """
            
            content = f"""
            <div class="nav-links">
                <a href="/">🏠 Dashboard</a>
                <a href="/assets">📊 Assets</a>
                <a href="/status">📈 System Status</a>
            </div>
            
            <div class="card">
                <h2>🔧 AWS Glue Tables ({len(tables)} found)</h2>
                <p>Tables in database: <strong>datasphere_ge230769</strong></p>
                {table_html}
            </div>
            """
        
        return create_html_response("AWS Glue Tables", content)
        
    except Exception as e:
        logger.error(f"Error in handle_glue: {e}")
        content = f"""
        <div class="nav-links">
            <a href="/">🏠 Dashboard</a>
            <a href="/assets">📊 Assets</a>
            <a href="/status">📈 System Status</a>
        </div>
        
        <div class="card">
            <h2>❌ Error Loading Glue Tables</h2>
            <p>Error: {str(e)}</p>
        </div>
        """
        return create_html_response("Error", content)

def handle_status() -> Dict[str, Any]:
    """Handle status request"""
    
    # Test connections
    datasphere_status = "unknown"
    glue_status = "unknown"
    
    try:
        assets = datasphere_client.get_catalog_assets()
        datasphere_status = "connected" if assets else "no_data"
    except:
        datasphere_status = "error"
    
    try:
        tables = glue_client.get_glue_tables()
        glue_status = "connected"
    except:
        glue_status = "error"
    
    status_color = "#78ff77" if datasphere_status == "connected" and glue_status == "connected" else "#ff77c6"
    
    content = f"""
    <div class="nav-links">
        <a href="/">🏠 Dashboard</a>
        <a href="/assets">📊 Assets</a>
        <a href="/glue">🔧 Glue Tables</a>
    </div>
    
    <div class="card">
        <h2>📈 System Status</h2>
        <div style="margin: 20px 0;">
            <div style="margin: 10px 0;">
                <strong>Datasphere Connection:</strong> 
                <span style="color: {status_color};">{datasphere_status}</span>
            </div>
            <div style="margin: 10px 0;">
                <strong>AWS Glue Connection:</strong> 
                <span style="color: {'#78ff77' if glue_status == 'connected' else '#ff77c6'};">{glue_status}</span>
            </div>
            <div style="margin: 10px 0;">
                <strong>Last Check:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
            </div>
        </div>
        
        <h3>Configuration:</h3>
        <div style="margin: 10px 0;">
            <p><strong>Datasphere URL:</strong> {DATASPHERE_CONFIG['base_url']}</p>
            <p><strong>Space:</strong> {DATASPHERE_CONFIG['space_name']}</p>
            <p><strong>Glue Database:</strong> datasphere_ge230769</p>
        </div>
    </div>
    """
    
    return create_html_response("System Status", content)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """AWS Lambda handler"""
    
    try:
        # Extract path from the event
        path = event.get('rawPath', event.get('path', '/'))
        method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')
        
        logger.info(f"Request: {method} {path}")
        
        # Handle different paths
        if path == '/' or path == '':
            return handle_dashboard()
        elif path == '/assets':
            return handle_assets()
        elif path == '/glue':
            return handle_glue()
        elif path == '/status':
            return handle_status()
        elif path.startswith('/api/'):
            # Handle API requests with JSON responses
            if path == '/api/assets':
                assets = datasphere_client.get_catalog_assets()
                return create_json_response(assets)
            elif path == '/api/glue':
                tables = glue_client.get_glue_tables()
                return create_json_response(tables)
            elif path == '/api/status':
                status = {
                    "datasphere_status": "connected",
                    "glue_status": "connected",
                    "timestamp": datetime.now().isoformat()
                }
                return create_json_response(status)
            else:
                return create_json_response({"error": "API endpoint not found"}, 404)
        else:
            # 404 for unknown paths
            content = """
            <div class="card">
                <h2>404 - Page Not Found</h2>
                <p>The requested page was not found.</p>
                <a href="/" class="btn">Go to Dashboard</a>
            </div>
            """
            return create_html_response("Page Not Found", content)
    
    except Exception as e:
        logger.error(f"Error in lambda_handler: {e}")
        content = f"""
        <div class="card">
            <h2>❌ Server Error</h2>
            <p>An error occurred: {str(e)}</p>
            <a href="/" class="btn">Go to Dashboard</a>
        </div>
        """
        return create_html_response("Server Error", content)