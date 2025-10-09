#!/usr/bin/env python3
"""
SAP Datasphere Control Panel - AWS Lambda Version
FastAPI application for managing Datasphere catalog synchronization
"""

import json
import logging
import asyncio
import base64
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import boto3
from mangum import Mangum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("datasphere-control-panel")

# FastAPI app
app = FastAPI(
    title="SAP Datasphere Control Panel",
    description="Manage catalog synchronization between SAP Datasphere and AWS",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    
    async def get_catalog_assets(self) -> List[Dict[str, Any]]:
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
    
    async def get_asset_data(self, asset_name: str, limit: int = 10) -> Dict[str, Any]:
        """Get sample data from an asset"""
        try:
            # Find the asset first
            assets = await self.get_catalog_assets()
            asset = next((a for a in assets if a.get('name') == asset_name), None)
            
            if not asset:
                return {"error": f"Asset '{asset_name}' not found"}
            
            data_url = asset.get('assetRelationalDataUrl')
            if not data_url:
                return {"error": f"No data URL for asset '{asset_name}'"}
            
            params = {'$top': limit}
            response = self.session.get(data_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                records = data.get('value', []) if isinstance(data, dict) else data
                
                return {
                    "asset_name": asset_name,
                    "asset_label": asset.get('label'),
                    "record_count": len(records),
                    "data": records,
                    "data_url": data_url
                }
            else:
                return {"error": f"Failed to fetch data: HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error fetching asset data: {e}")
            return {"error": str(e)}

class AWSGlueClient:
    """Client for AWS Glue operations"""
    
    def __init__(self):
        self.glue_client = boto3.client('glue', region_name='us-east-1')
        self.database_name = "datasphere_ge230769"
    
    async def get_glue_tables(self) -> List[Dict[str, Any]]:
        """Get tables from AWS Glue catalog"""
        try:
            response = self.glue_client.get_tables(DatabaseName=self.database_name)
            tables = response.get('TableList', [])
            
            return [
                {
                    "name": table['Name'],
                    "description": table.get('Description', ''),
                    "columns": len(table.get('StorageDescriptor', {}).get('Columns', [])),
                    "last_updated": table.get('UpdateTime', '').isoformat() if table.get('UpdateTime') else '',
                    "datasphere_asset": table.get('Parameters', {}).get('datasphere_asset', ''),
                    "datasphere_label": table.get('Parameters', {}).get('datasphere_label', '')
                }
                for table in tables
            ]
            
        except Exception as e:
            logger.error(f"Error fetching Glue tables: {e}")
            return []
    
    async def sync_asset_to_glue(self, asset: Dict[str, Any]) -> Dict[str, Any]:
        """Sync a single asset to AWS Glue"""
        try:
            # This is a simplified sync - in production you'd want more robust metadata extraction
            table_name = asset.get('name', '').replace('.', '_').replace('-', '_').lower()
            
            # Basic column structure for time dimensions
            columns = []
            if 'TIME' in asset.get('name', '').upper():
                if 'DAY' in asset.get('name', '').upper():
                    columns = [
                        {'Name': 'date_sql', 'Type': 'date', 'Comment': 'SQL date'},
                        {'Name': 'calquarter', 'Type': 'int', 'Comment': 'Calendar quarter'},
                        {'Name': 'calmonth', 'Type': 'int', 'Comment': 'Calendar month'},
                        {'Name': 'calyear', 'Type': 'int', 'Comment': 'Calendar year'},
                        {'Name': 'calweek', 'Type': 'int', 'Comment': 'Calendar week'}
                    ]
                else:
                    columns = [
                        {'Name': 'calyear', 'Type': 'int', 'Comment': 'Calendar year'},
                        {'Name': 'calmonth', 'Type': 'int', 'Comment': 'Calendar month'}
                    ]
            
            if not columns:
                columns = [{'Name': 'id', 'Type': 'string', 'Comment': 'Identifier'}]
            
            table_input = {
                'Name': table_name,
                'Description': f"Datasphere asset: {asset.get('label', asset.get('name'))}",
                'StorageDescriptor': {
                    'Columns': columns,
                    'Location': asset.get('assetRelationalDataUrl', ''),
                    'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
                    'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
                    'SerdeInfo': {
                        'SerializationLibrary': 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
                    }
                },
                'Parameters': {
                    'datasphere_source': 'true',
                    'datasphere_asset': asset.get('name', ''),
                    'datasphere_space': asset.get('spaceName', ''),
                    'datasphere_label': asset.get('label', ''),
                    'last_updated': datetime.now().isoformat(),
                    'data_url': asset.get('assetRelationalDataUrl', ''),
                    'classification': 'datasphere_asset'
                }
            }
            
            # Create or update table
            try:
                self.glue_client.get_table(DatabaseName=self.database_name, Name=table_name)
                # Update existing table
                self.glue_client.update_table(
                    DatabaseName=self.database_name,
                    TableInput=table_input
                )
                return {"status": "updated", "table_name": table_name}
            except self.glue_client.exceptions.EntityNotFoundException:
                # Create new table
                self.glue_client.create_table(
                    DatabaseName=self.database_name,
                    TableInput=table_input
                )
                return {"status": "created", "table_name": table_name}
                
        except Exception as e:
            logger.error(f"Error syncing asset to Glue: {e}")
            return {"status": "error", "error": str(e)}

# Initialize clients
datasphere_client = DatasphereAPIClient()
glue_client = AWSGlueClient()

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the main dashboard"""
    
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SAP Datasphere Control Panel</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', 'Segoe UI', sans-serif;
                background: #0a0a0a;
                color: #e0e0e0;
                min-height: 100vh;
                background-image: 
                    radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.1) 0%, transparent 50%);
            }
            
            .header {
                background: rgba(26, 26, 26, 0.9);
                border-bottom: 1px solid rgba(120, 255, 119, 0.2);
                padding: 20px 0;
                backdrop-filter: blur(10px);
            }
            
            .header-content {
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 20px;
                display: flex;
                align-items: center;
                gap: 20px;
            }
            
            .logo {
                width: 50px;
                height: 50px;
                background: #1a1a1a;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                border: 2px solid #ff77c6;
                position: relative;
            }
            
            .alien-head {
                width: 25px;
                height: 30px;
                background: #2a2a2a;
                border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%;
                position: relative;
            }
            
            .alien-eye {
                position: absolute;
                width: 6px;
                height: 4px;
                background: #78ff77;
                border-radius: 50%;
                top: 12px;
                box-shadow: 0 0 5px rgba(120, 255, 119, 0.8);
            }
            
            .alien-eye.left { left: 5px; }
            .alien-eye.right { right: 5px; }
            
            .header h1 {
                font-size: 1.8em;
                background: linear-gradient(135deg, #78ff77 0%, #ff77c6 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .status-badge {
                padding: 5px 15px;
                background: rgba(120, 255, 119, 0.2);
                color: #78ff77;
                border-radius: 20px;
                font-size: 0.9em;
                border: 1px solid rgba(120, 255, 119, 0.3);
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 30px 20px;
            }
            
            .dashboard-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .card {
                background: rgba(26, 26, 26, 0.8);
                border: 1px solid rgba(120, 255, 119, 0.2);
                border-radius: 15px;
                padding: 25px;
                backdrop-filter: blur(10px);
                transition: all 0.3s ease;
            }
            
            .card:hover {
                border-color: rgba(255, 119, 198, 0.4);
                box-shadow: 0 10px 30px rgba(120, 255, 119, 0.1);
                transform: translateY(-5px);
            }
            
            .card h2 {
                color: #78ff77;
                font-size: 1.4em;
                margin-bottom: 15px;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .btn {
                background: linear-gradient(135deg, #78ff77 0%, #ff77c6 100%);
                color: #000;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
                margin: 10px 10px 10px 0;
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(120, 255, 119, 0.3);
            }
            
            .btn-secondary {
                background: rgba(120, 255, 119, 0.1);
                color: #78ff77;
                border: 1px solid rgba(120, 255, 119, 0.3);
            }
            
            .loading {
                display: none;
                color: #ff77c6;
            }
            
            .results {
                margin-top: 20px;
                padding: 15px;
                background: rgba(120, 255, 119, 0.05);
                border-radius: 8px;
                border: 1px solid rgba(120, 255, 119, 0.2);
                display: none;
            }
            
            .error {
                background: rgba(255, 119, 119, 0.05);
                border-color: rgba(255, 119, 119, 0.2);
                color: #ff7777;
            }
            
            .asset-list {
                max-height: 300px;
                overflow-y: auto;
            }
            
            .asset-item {
                padding: 10px;
                margin: 5px 0;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 5px;
                border-left: 3px solid #78ff77;
            }
            
            .asset-item h4 {
                color: #78ff77;
                margin-bottom: 5px;
            }
            
            .asset-item p {
                color: #c0c0c0;
                font-size: 0.9em;
            }
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
            <div class="dashboard-grid">
                <div class="card">
                    <h2>🔍 Asset Discovery</h2>
                    <p>Discover and explore assets in your Datasphere space.</p>
                    <button class="btn" onclick="discoverAssets()">Discover Assets</button>
                    <div class="loading" id="discover-loading">🔄 Discovering assets...</div>
                    <div class="results" id="discover-results"></div>
                </div>
                
                <div class="card">
                    <h2>🔄 Sync Management</h2>
                    <p>Synchronize assets between Datasphere and AWS Glue.</p>
                    <button class="btn" onclick="syncAssets()">Sync All Assets</button>
                    <button class="btn btn-secondary" onclick="checkGlueStatus()">Check Glue Status</button>
                    <div class="loading" id="sync-loading">🔄 Synchronizing...</div>
                    <div class="results" id="sync-results"></div>
                </div>
                
                <div class="card">
                    <h2>👁️ Data Preview</h2>
                    <p>Preview data from your Datasphere assets.</p>
                    <button class="btn" onclick="previewData('SAP.TIME.VIEW_DIMENSION_DAY')">Preview Time Dimension</button>
                    <div class="loading" id="preview-loading">🔄 Loading data...</div>
                    <div class="results" id="preview-results"></div>
                </div>
                
                <div class="card">
                    <h2>📊 System Status</h2>
                    <p>Monitor the health of your integration.</p>
                    <button class="btn btn-secondary" onclick="checkSystemStatus()">Check Status</button>
                    <div class="loading" id="status-loading">🔄 Checking status...</div>
                    <div class="results" id="status-results"></div>
                </div>
            </div>
        </div>
        
        <script>
            async function apiCall(endpoint, method = 'GET', body = null) {
                const options = {
                    method,
                    headers: {
                        'Content-Type': 'application/json',
                    }
                };
                
                if (body) {
                    options.body = JSON.stringify(body);
                }
                
                const response = await fetch(endpoint, options);
                return await response.json();
            }
            
            function showLoading(id) {
                document.getElementById(id + '-loading').style.display = 'block';
                document.getElementById(id + '-results').style.display = 'none';
            }
            
            function hideLoading(id) {
                document.getElementById(id + '-loading').style.display = 'none';
            }
            
            function showResults(id, content, isError = false) {
                const resultsDiv = document.getElementById(id + '-results');
                resultsDiv.innerHTML = content;
                resultsDiv.className = 'results' + (isError ? ' error' : '');
                resultsDiv.style.display = 'block';
            }
            
            async function discoverAssets() {
                showLoading('discover');
                try {
                    const data = await apiCall('/api/assets');
                    hideLoading('discover');
                    
                    if (data.error) {
                        showResults('discover', `<strong>Error:</strong> ${data.error}`, true);
                        return;
                    }
                    
                    let html = `<h3>Found ${data.length} assets:</h3><div class="asset-list">`;
                    data.forEach(asset => {
                        html += `
                            <div class="asset-item">
                                <h4>${asset.label || asset.name}</h4>
                                <p><strong>Name:</strong> ${asset.name}</p>
                                <p><strong>Space:</strong> ${asset.spaceName}</p>
                            </div>
                        `;
                    });
                    html += '</div>';
                    
                    showResults('discover', html);
                } catch (error) {
                    hideLoading('discover');
                    showResults('discover', `<strong>Error:</strong> ${error.message}`, true);
                }
            }
            
            async function syncAssets() {
                showLoading('sync');
                try {
                    const data = await apiCall('/api/sync', 'POST');
                    hideLoading('sync');
                    
                    if (data.error) {
                        showResults('sync', `<strong>Error:</strong> ${data.error}`, true);
                        return;
                    }
                    
                    let html = `<h3>Sync Results:</h3>`;
                    html += `<p><strong>Assets Processed:</strong> ${data.assets_processed}</p>`;
                    html += `<p><strong>Tables Created/Updated:</strong> ${data.tables_synced}</p>`;
                    
                    if (data.results && data.results.length > 0) {
                        html += '<div class="asset-list">';
                        data.results.forEach(result => {
                            html += `
                                <div class="asset-item">
                                    <h4>${result.asset_name}</h4>
                                    <p><strong>Status:</strong> ${result.status}</p>
                                    ${result.table_name ? `<p><strong>Table:</strong> ${result.table_name}</p>` : ''}
                                </div>
                            `;
                        });
                        html += '</div>';
                    }
                    
                    showResults('sync', html);
                } catch (error) {
                    hideLoading('sync');
                    showResults('sync', `<strong>Error:</strong> ${error.message}`, true);
                }
            }
            
            async function checkGlueStatus() {
                showLoading('sync');
                try {
                    const data = await apiCall('/api/glue/tables');
                    hideLoading('sync');
                    
                    if (data.error) {
                        showResults('sync', `<strong>Error:</strong> ${data.error}`, true);
                        return;
                    }
                    
                    let html = `<h3>AWS Glue Tables (${data.length}):</h3><div class="asset-list">`;
                    data.forEach(table => {
                        html += `
                            <div class="asset-item">
                                <h4>${table.name}</h4>
                                <p><strong>Description:</strong> ${table.description}</p>
                                <p><strong>Columns:</strong> ${table.columns}</p>
                                <p><strong>Source:</strong> ${table.datasphere_label || table.datasphere_asset}</p>
                            </div>
                        `;
                    });
                    html += '</div>';
                    
                    showResults('sync', html);
                } catch (error) {
                    hideLoading('sync');
                    showResults('sync', `<strong>Error:</strong> ${error.message}`, true);
                }
            }
            
            async function previewData(assetName) {
                showLoading('preview');
                try {
                    const data = await apiCall(`/api/assets/${encodeURIComponent(assetName)}/data`);
                    hideLoading('preview');
                    
                    if (data.error) {
                        showResults('preview', `<strong>Error:</strong> ${data.error}`, true);
                        return;
                    }
                    
                    let html = `<h3>${data.asset_label} (${data.record_count} records)</h3>`;
                    
                    if (data.data && data.data.length > 0) {
                        html += '<div style="overflow-x: auto;"><table style="width: 100%; border-collapse: collapse;">';
                        
                        // Headers
                        const headers = Object.keys(data.data[0]);
                        html += '<tr>';
                        headers.forEach(header => {
                            html += `<th style="border: 1px solid #333; padding: 8px; background: rgba(120, 255, 119, 0.1);">${header}</th>`;
                        });
                        html += '</tr>';
                        
                        // Data rows
                        data.data.slice(0, 5).forEach(row => {
                            html += '<tr>';
                            headers.forEach(header => {
                                html += `<td style="border: 1px solid #333; padding: 8px;">${row[header] || ''}</td>`;
                            });
                            html += '</tr>';
                        });
                        
                        html += '</table></div>';
                    }
                    
                    showResults('preview', html);
                } catch (error) {
                    hideLoading('preview');
                    showResults('preview', `<strong>Error:</strong> ${error.message}`, true);
                }
            }
            
            async function checkSystemStatus() {
                showLoading('status');
                try {
                    const data = await apiCall('/api/status');
                    hideLoading('status');
                    
                    let html = '<h3>System Status:</h3>';
                    html += `<p><strong>Datasphere Connection:</strong> ${data.datasphere_status}</p>`;
                    html += `<p><strong>AWS Glue Connection:</strong> ${data.glue_status}</p>`;
                    html += `<p><strong>Last Check:</strong> ${new Date(data.timestamp).toLocaleString()}</p>`;
                    
                    showResults('status', html);
                } catch (error) {
                    hideLoading('status');
                    showResults('status', `<strong>Error:</strong> ${error.message}`, true);
                }
            }
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@app.get("/api/assets")
async def get_assets():
    """Get all assets from Datasphere catalog"""
    try:
        assets = await datasphere_client.get_catalog_assets()
        return assets
    except Exception as e:
        logger.error(f"Error in get_assets: {e}")
        return {"error": str(e)}

@app.get("/api/assets/{asset_name}/data")
async def get_asset_data(asset_name: str, limit: int = 10):
    """Get sample data from a specific asset"""
    try:
        data = await datasphere_client.get_asset_data(asset_name, limit)
        return data
    except Exception as e:
        logger.error(f"Error in get_asset_data: {e}")
        return {"error": str(e)}

@app.get("/api/glue/tables")
async def get_glue_tables():
    """Get tables from AWS Glue catalog"""
    try:
        tables = await glue_client.get_glue_tables()
        return tables
    except Exception as e:
        logger.error(f"Error in get_glue_tables: {e}")
        return {"error": str(e)}

@app.post("/api/sync")
async def sync_assets():
    """Sync all assets from Datasphere to AWS Glue"""
    try:
        # Get assets from Datasphere
        assets = await datasphere_client.get_catalog_assets()
        
        if not assets:
            return {"error": "No assets found in Datasphere"}
        
        results = []
        tables_synced = 0
        
        for asset in assets:
            try:
                result = await glue_client.sync_asset_to_glue(asset)
                result["asset_name"] = asset.get('name')
                results.append(result)
                
                if result.get("status") in ["created", "updated"]:
                    tables_synced += 1
                    
            except Exception as e:
                results.append({
                    "asset_name": asset.get('name'),
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "assets_processed": len(assets),
            "tables_synced": tables_synced,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in sync_assets: {e}")
        return {"error": str(e)}

@app.get("/api/status")
async def get_system_status():
    """Get system status"""
    try:
        # Test Datasphere connection
        datasphere_status = "connected"
        try:
            assets = await datasphere_client.get_catalog_assets()
            if not assets:
                datasphere_status = "no_assets"
        except:
            datasphere_status = "error"
        
        # Test Glue connection
        glue_status = "connected"
        try:
            tables = await glue_client.get_glue_tables()
        except:
            glue_status = "error"
        
        return {
            "datasphere_status": datasphere_status,
            "glue_status": glue_status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in get_system_status: {e}")
        return {"error": str(e)}

# Lambda handler
handler = Mangum(app)