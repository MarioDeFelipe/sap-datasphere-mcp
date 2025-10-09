#!/usr/bin/env python3
"""
SAP Datasphere Control Panel - Docker Development Version
Hello World Application with SAP Datasphere Integration
"""

from flask import Flask, jsonify, render_template_string, request
import os
import json
import requests
from datetime import datetime
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
app.config['DEBUG'] = True

@app.route('/')
def hello_world():
    """Hello World homepage"""
    return render_template_string(get_hello_world_html())

@app.route('/api/hello')
def api_hello():
    """Hello World API endpoint"""
    return jsonify({
        'message': 'Hello World from SAP Datasphere Control Panel!',
        'status': 'running',
        'environment': 'docker',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/status')
def api_status():
    """System status endpoint"""
    return jsonify({
        'status': 'healthy',
        'environment': 'docker_development',
        'python_version': '3.11',
        'flask_version': '2.3.3',
        'features': {
            'docker_ready': True,
            'development_mode': True,
            'hot_reload': True
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

@app.route('/api/datasphere/connect', methods=['POST'])
def connect_datasphere():
    """Connect to SAP Datasphere and retrieve data products"""
    try:
        # Get connection parameters from request
        data = request.get_json() or {}
        
        # Default configuration (can be overridden by request)
        config = {
            'base_url': data.get('base_url', 'https://your-tenant.datasphere.cloud.sap'),
            'username': data.get('username', ''),
            'password': data.get('password', ''),
            'space_id': data.get('space_id', 'default')
        }
        
        logger.info(f"Attempting to connect to Datasphere: {config['base_url']}")
        
        # For demo purposes, return mock data products
        # In production, this would make actual API calls to Datasphere
        mock_data_products = get_mock_data_products()
        
        return jsonify({
            'status': 'success',
            'message': 'Successfully connected to SAP Datasphere',
            'connection_info': {
                'base_url': config['base_url'],
                'space_id': config['space_id'],
                'connected_at': datetime.now().isoformat()
            },
            'data_products': mock_data_products,
            'total_products': len(mock_data_products)
        })
        
    except Exception as e:
        logger.error(f"Error connecting to Datasphere: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to connect to SAP Datasphere: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/datasphere/products')
def get_data_products():
    """Get available data products from SAP Datasphere"""
    try:
        # In production, this would fetch real data from Datasphere API
        data_products = get_mock_data_products()
        
        return jsonify({
            'status': 'success',
            'data_products': data_products,
            'total_count': len(data_products),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error fetching data products: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to fetch data products: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

def get_mock_data_products():
    """Return mock data products for demonstration"""
    return [
        {
            'id': 'dp_001',
            'name': 'Customer Analytics Dataset',
            'description': 'Comprehensive customer behavior and demographics data',
            'type': 'analytical_dataset',
            'status': 'active',
            'owner': 'analytics_team',
            'created_date': '2024-01-15T10:30:00Z',
            'last_updated': '2024-01-20T14:45:00Z',
            'row_count': 1250000,
            'columns': [
                {'name': 'customer_id', 'type': 'string'},
                {'name': 'age', 'type': 'integer'},
                {'name': 'region', 'type': 'string'},
                {'name': 'purchase_amount', 'type': 'decimal'},
                {'name': 'last_purchase_date', 'type': 'date'}
            ],
            'tags': ['customer', 'analytics', 'sales']
        },
        {
            'id': 'dp_002',
            'name': 'Sales Performance Metrics',
            'description': 'Real-time sales performance indicators and KPIs',
            'type': 'view',
            'status': 'active',
            'owner': 'sales_team',
            'created_date': '2024-01-10T09:15:00Z',
            'last_updated': '2024-01-21T16:20:00Z',
            'row_count': 850000,
            'columns': [
                {'name': 'sales_rep_id', 'type': 'string'},
                {'name': 'quarter', 'type': 'string'},
                {'name': 'revenue', 'type': 'decimal'},
                {'name': 'target', 'type': 'decimal'},
                {'name': 'achievement_rate', 'type': 'decimal'}
            ],
            'tags': ['sales', 'performance', 'kpi']
        },
        {
            'id': 'dp_003',
            'name': 'Product Inventory Data',
            'description': 'Current inventory levels and product information',
            'type': 'table',
            'status': 'active',
            'owner': 'inventory_team',
            'created_date': '2024-01-05T11:00:00Z',
            'last_updated': '2024-01-21T18:30:00Z',
            'row_count': 45000,
            'columns': [
                {'name': 'product_id', 'type': 'string'},
                {'name': 'product_name', 'type': 'string'},
                {'name': 'category', 'type': 'string'},
                {'name': 'stock_level', 'type': 'integer'},
                {'name': 'reorder_point', 'type': 'integer'}
            ],
            'tags': ['inventory', 'products', 'stock']
        },
        {
            'id': 'dp_004',
            'name': 'Financial Reporting Dataset',
            'description': 'Consolidated financial data for reporting and analysis',
            'type': 'analytical_dataset',
            'status': 'active',
            'owner': 'finance_team',
            'created_date': '2024-01-12T13:45:00Z',
            'last_updated': '2024-01-21T12:15:00Z',
            'row_count': 320000,
            'columns': [
                {'name': 'account_id', 'type': 'string'},
                {'name': 'account_name', 'type': 'string'},
                {'name': 'amount', 'type': 'decimal'},
                {'name': 'currency', 'type': 'string'},
                {'name': 'fiscal_period', 'type': 'string'}
            ],
            'tags': ['finance', 'reporting', 'accounting']
        },
        {
            'id': 'dp_005',
            'name': 'Supply Chain Analytics',
            'description': 'End-to-end supply chain performance metrics',
            'type': 'view',
            'status': 'development',
            'owner': 'supply_chain_team',
            'created_date': '2024-01-18T08:30:00Z',
            'last_updated': '2024-01-21T10:45:00Z',
            'row_count': 180000,
            'columns': [
                {'name': 'supplier_id', 'type': 'string'},
                {'name': 'delivery_time', 'type': 'integer'},
                {'name': 'quality_score', 'type': 'decimal'},
                {'name': 'cost_per_unit', 'type': 'decimal'},
                {'name': 'region', 'type': 'string'}
            ],
            'tags': ['supply_chain', 'logistics', 'performance']
        }
    ]

def get_hello_world_html():
    """Get the hello world HTML template"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SAP Datasphere Control Panel - Docker Dev</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #2563eb 100%);
                color: white;
                min-height: 100vh;
                display: flex;
                padding: 20px;
                gap: 20px;
            }
            
            .main-content {
                flex: 1;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .container {
                text-align: center;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 50px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                max-width: 800px;
                width: 100%;
            }
            
            .right-panel {
                width: 400px;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 20px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                display: flex;
                flex-direction: column;
            }
            
            .q-business-header {
                text-align: center;
                margin-bottom: 20px;
                padding-bottom: 15px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            .q-business-widget {
                flex: 1;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 15px;
                padding: 20px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                min-height: 600px;
                display: flex;
                flex-direction: column;
            }
            
            .chat-container {
                flex: 1;
                display: flex;
                flex-direction: column;
                gap: 15px;
            }
            
            .chat-messages {
                flex: 1;
                overflow-y: auto;
                padding: 15px;
                background: rgba(0, 0, 0, 0.2);
                border-radius: 10px;
                min-height: 400px;
                max-height: 500px;
            }
            
            .chat-input-container {
                display: flex;
                gap: 10px;
                margin-top: 15px;
            }
            
            .chat-input {
                flex: 1;
                padding: 12px;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.1);
                color: white;
                font-size: 14px;
            }
            
            .chat-input::placeholder {
                color: rgba(255, 255, 255, 0.6);
            }
            
            .chat-send-btn {
                padding: 12px 20px;
                background: rgba(76, 175, 80, 0.8);
                border: none;
                border-radius: 8px;
                color: white;
                cursor: pointer;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            
            .chat-send-btn:hover {
                background: rgba(76, 175, 80, 1);
                transform: translateY(-1px);
            }
            
            .message {
                margin-bottom: 15px;
                padding: 12px;
                border-radius: 10px;
                max-width: 90%;
            }
            
            .message.user {
                background: rgba(33, 150, 243, 0.3);
                margin-left: auto;
                text-align: right;
            }
            
            .message.assistant {
                background: rgba(76, 175, 80, 0.3);
                margin-right: auto;
            }
            
            .message-time {
                font-size: 0.8em;
                opacity: 0.7;
                margin-top: 5px;
            }
            
            @media (max-width: 1200px) {
                body {
                    flex-direction: column;
                }
                
                .right-panel {
                    width: 100%;
                    order: -1;
                }
                
                .main-content {
                    width: 100%;
                }
            }
            
            .logo {
                width: 80px;
                height: 80px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 50%;
                margin: 0 auto 30px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 2em;
                animation: pulse 2s ease-in-out infinite;
            }
            
            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.1); }
            }
            
            h1 {
                font-size: 2.5em;
                margin-bottom: 20px;
                text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
            }
            
            .subtitle {
                font-size: 1.2em;
                margin-bottom: 30px;
                opacity: 0.9;
            }
            
            .status-badge {
                display: inline-block;
                background: rgba(76, 175, 80, 0.8);
                padding: 10px 20px;
                border-radius: 25px;
                margin: 20px 0;
                font-weight: 600;
            }
            
            .btn {
                background: rgba(255, 255, 255, 0.2);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.3);
                padding: 15px 30px;
                border-radius: 10px;
                font-size: 1.1em;
                cursor: pointer;
                transition: all 0.3s ease;
                margin: 10px;
                text-decoration: none;
                display: inline-block;
            }
            
            .btn:hover {
                background: rgba(255, 255, 255, 0.3);
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            }
            
            .info-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-top: 40px;
            }
            
            .info-card {
                background: rgba(255, 255, 255, 0.1);
                padding: 20px;
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            .info-card h3 {
                margin-bottom: 10px;
                color: #FFD700;
            }
            
            .results {
                margin-top: 20px;
                padding: 20px;
                background: rgba(0, 0, 0, 0.2);
                border-radius: 10px;
                display: none;
                text-align: left;
            }
            
            pre {
                background: rgba(0, 0, 0, 0.3);
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>
        <div class="main-content">
            <div class="container">
                <div class="logo">🐳</div>
                <h1>Hello World!</h1>
                <div class="subtitle">SAP Datasphere Control Panel</div>
                <div class="status-badge">🚀 Docker Development Environment</div>
                
                <div class="info-grid">
                    <div class="info-card">
                        <h3>🐳 Docker</h3>
                        <p>Running in containerized environment</p>
                    </div>
                    <div class="info-card">
                        <h3>🐍 Python 3.11</h3>
                        <p>Latest Python runtime</p>
                    </div>
                    <div class="info-card">
                        <h3>⚡ Flask</h3>
                        <p>Development server with hot reload</p>
                    </div>
                    <div class="info-card">
                        <h3>🔗 SAP Datasphere</h3>
                        <p>Connect and explore data products</p>
                    </div>
                </div>
                
                <div style="margin-top: 40px;">
                    <button class="btn" onclick="testAPI()">Test API</button>
                    <button class="btn" onclick="checkStatus()">Check Status</button>
                    <button class="btn" onclick="connectDatasphere()">🔗 Connect to Datasphere</button>
                    <button class="btn" onclick="getDataProducts()">📊 Get Data Products</button>
                    <button class="btn" onclick="showInfo()">System Info</button>
                </div>
                
                <div class="results" id="results"></div>
            </div>
        </div>
        
        <div class="right-panel">
            <div class="q-business-header">
                <h2>🤖 Amazon Q Business</h2>
                <p style="font-size: 0.9em; opacity: 0.8;">AI Assistant for Enterprise</p>
            </div>
            
            <div class="q-business-widget">
                <div class="chat-container">
                    <div class="chat-messages" id="chatMessages">
                        <div class="message assistant">
                            <div>👋 Hello! I'm Amazon Q Business, your AI assistant. I can help you with:</div>
                            <ul style="margin: 10px 0; text-align: left;">
                                <li>SAP Datasphere queries and analysis</li>
                                <li>Docker and development questions</li>
                                <li>AWS services and best practices</li>
                                <li>Data integration and analytics</li>
                            </ul>
                            <div>How can I assist you today?</div>
                            <div class="message-time">${new Date().toLocaleTimeString()}</div>
                        </div>
                    </div>
                    
                    <div class="chat-input-container">
                        <input 
                            type="text" 
                            class="chat-input" 
                            id="chatInput" 
                            placeholder="Ask me anything about your data, AWS, or development..."
                            onkeypress="handleChatKeyPress(event)"
                        />
                        <button class="chat-send-btn" onclick="sendMessage()">Send</button>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            async function testAPI() {
                const results = document.getElementById('results');
                results.style.display = 'block';
                results.innerHTML = '<h3>🔄 Testing API...</h3>';
                
                try {
                    const response = await fetch('/api/hello');
                    const data = await response.json();
                    
                    results.innerHTML = `
                        <h3>✅ API Test Successful!</h3>
                        <pre>${JSON.stringify(data, null, 2)}</pre>
                    `;
                } catch (error) {
                    results.innerHTML = `
                        <h3>❌ API Test Failed</h3>
                        <p>Error: ${error.message}</p>
                    `;
                }
            }
            
            async function checkStatus() {
                const results = document.getElementById('results');
                results.style.display = 'block';
                results.innerHTML = '<h3>🔄 Checking status...</h3>';
                
                try {
                    const response = await fetch('/api/status');
                    const data = await response.json();
                    
                    results.innerHTML = `
                        <h3>📊 System Status</h3>
                        <pre>${JSON.stringify(data, null, 2)}</pre>
                    `;
                } catch (error) {
                    results.innerHTML = `
                        <h3>❌ Status Check Failed</h3>
                        <p>Error: ${error.message}</p>
                    `;
                }
            }
            
            function showInfo() {
                const results = document.getElementById('results');
                results.style.display = 'block';
                results.innerHTML = `
                    <h3>ℹ️ Development Environment Info</h3>
                    <p><strong>Environment:</strong> Docker Container</p>
                    <p><strong>Port:</strong> 8000</p>
                    <p><strong>Hot Reload:</strong> Enabled</p>
                    <p><strong>Debug Mode:</strong> On</p>
                    <p><strong>Ready for:</strong> SAP Datasphere Integration</p>
                    <br>
                    <p><strong>Next Steps:</strong></p>
                    <ul style="text-align: left; margin-left: 20px;">
                        <li>Add SAP Datasphere API integration</li>
                        <li>Implement authentication</li>
                        <li>Build control panel features</li>
                        <li>Add database connections</li>
                    </ul>
                `;
            }
            
            async function connectDatasphere() {
                const results = document.getElementById('results');
                results.style.display = 'block';
                results.innerHTML = '<h3>🔄 Connecting to SAP Datasphere...</h3>';
                
                try {
                    const response = await fetch('/api/datasphere/connect', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            base_url: 'https://demo-tenant.datasphere.cloud.sap',
                            space_id: 'demo_space'
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.status === 'success') {
                        results.innerHTML = `
                            <h3>✅ Successfully Connected to SAP Datasphere!</h3>
                            <div style="margin: 20px 0;">
                                <p><strong>Base URL:</strong> ${data.connection_info.base_url}</p>
                                <p><strong>Space ID:</strong> ${data.connection_info.space_id}</p>
                                <p><strong>Connected At:</strong> ${new Date(data.connection_info.connected_at).toLocaleString()}</p>
                                <p><strong>Data Products Found:</strong> ${data.total_products}</p>
                            </div>
                            <h4>📊 Available Data Products:</h4>
                            <div style="max-height: 300px; overflow-y: auto; margin-top: 10px;">
                                ${data.data_products.map(product => `
                                    <div style="background: rgba(255,255,255,0.1); margin: 10px 0; padding: 15px; border-radius: 8px; border-left: 4px solid #4CAF50;">
                                        <h5 style="color: #FFD700; margin-bottom: 8px;">${product.name}</h5>
                                        <p style="margin-bottom: 8px;">${product.description}</p>
                                        <div style="display: flex; gap: 15px; font-size: 0.9em; opacity: 0.8;">
                                            <span><strong>Type:</strong> ${product.type}</span>
                                            <span><strong>Status:</strong> ${product.status}</span>
                                            <span><strong>Rows:</strong> ${product.row_count.toLocaleString()}</span>
                                            <span><strong>Owner:</strong> ${product.owner}</span>
                                        </div>
                                        <div style="margin-top: 8px;">
                                            <strong>Tags:</strong> ${product.tags.map(tag => `<span style="background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 12px; margin-right: 5px; font-size: 0.8em;">${tag}</span>`).join('')}
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        `;
                    } else {
                        results.innerHTML = `
                            <h3>❌ Connection Failed</h3>
                            <p>Error: ${data.message}</p>
                        `;
                    }
                } catch (error) {
                    results.innerHTML = `
                        <h3>❌ Connection Error</h3>
                        <p>Error: ${error.message}</p>
                    `;
                }
            }
            
            async function getDataProducts() {
                const results = document.getElementById('results');
                results.style.display = 'block';
                results.innerHTML = '<h3>🔄 Fetching Data Products...</h3>';
                
                try {
                    const response = await fetch('/api/datasphere/products');
                    const data = await response.json();
                    
                    if (data.status === 'success') {
                        results.innerHTML = `
                            <h3>📊 SAP Datasphere Data Products (${data.total_count})</h3>
                            <div style="max-height: 400px; overflow-y: auto; margin-top: 15px;">
                                ${data.data_products.map(product => `
                                    <div style="background: rgba(255,255,255,0.1); margin: 15px 0; padding: 20px; border-radius: 10px; border-left: 4px solid #2196F3;">
                                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                                            <h4 style="color: #FFD700; margin: 0;">${product.name}</h4>
                                            <span style="background: ${product.status === 'active' ? '#4CAF50' : '#FF9800'}; padding: 4px 12px; border-radius: 15px; font-size: 0.8em; font-weight: bold;">
                                                ${product.status.toUpperCase()}
                                            </span>
                                        </div>
                                        <p style="margin-bottom: 15px; opacity: 0.9;">${product.description}</p>
                                        
                                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin-bottom: 15px; font-size: 0.9em;">
                                            <div><strong>Type:</strong> ${product.type}</div>
                                            <div><strong>Owner:</strong> ${product.owner}</div>
                                            <div><strong>Rows:</strong> ${product.row_count.toLocaleString()}</div>
                                            <div><strong>Columns:</strong> ${product.columns.length}</div>
                                        </div>
                                        
                                        <div style="margin-bottom: 15px;">
                                            <strong>Schema:</strong>
                                            <div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px; margin-top: 5px; font-family: monospace; font-size: 0.8em;">
                                                ${product.columns.map(col => `${col.name}: ${col.type}`).join(', ')}
                                            </div>
                                        </div>
                                        
                                        <div style="margin-bottom: 10px;">
                                            <strong>Tags:</strong> ${product.tags.map(tag => `<span style="background: rgba(255,255,255,0.2); padding: 3px 10px; border-radius: 15px; margin-right: 8px; font-size: 0.8em;">${tag}</span>`).join('')}
                                        </div>
                                        
                                        <div style="font-size: 0.8em; opacity: 0.7;">
                                            <strong>Created:</strong> ${new Date(product.created_date).toLocaleDateString()} | 
                                            <strong>Updated:</strong> ${new Date(product.last_updated).toLocaleDateString()}
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        `;
                    } else {
                        results.innerHTML = `
                            <h3>❌ Failed to Fetch Data Products</h3>
                            <p>Error: ${data.message}</p>
                        `;
                    }
                } catch (error) {
                    results.innerHTML = `
                        <h3>❌ Fetch Error</h3>
                        <p>Error: ${error.message}</p>
                    `;
                }
            }
            
            // Auto-test API on page load
            window.addEventListener('load', () => {
                setTimeout(testAPI, 1000);
            });
        </script>
    </body>
    </html>
    """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)