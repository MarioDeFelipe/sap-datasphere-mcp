"""
Development Server for Ailien Platform Control Panel
Runs locally with Flask for development and testing
"""

from flask import Flask, render_template_string, request, jsonify
import json
import os
import argparse
from datetime import datetime

app = Flask(__name__)

# Environment configuration
ENVIRONMENTS = {
    'dev': {
        'port': 5000,
        'host': '127.0.0.1',
        'debug': True,
        'name': 'Development',
        'color': '#ff6b35'  # Orange for dev
    },
    'staging': {
        'port': 5001,
        'host': '127.0.0.1',
        'debug': True,
        'name': 'Staging',
        'color': '#f7931e'  # Yellow for staging
    },
    'prod': {
        'port': 8080,
        'host': '0.0.0.0',
        'debug': False,
        'name': 'Production',
        'color': '#27ae60'  # Green for prod
    }
}

# Global environment variable
current_env = 'dev'

def get_html_template():
    """Get the HTML template with environment-specific styling"""
    env_config = ENVIRONMENTS[current_env]
    
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ailien Platform - {env_config['name']} Environment</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #f5f7fa;
                color: #333;
            }}
            
            .env-banner {{
                background: {env_config['color']};
                color: white;
                padding: 8px 20px;
                text-align: center;
                font-weight: bold;
                font-size: 14px;
                position: sticky;
                top: 0;
                z-index: 1000;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            
            .main-container {{
                display: flex;
                height: calc(100vh - 40px);
            }}
            
            .control-panel {{
                flex: 1;
                padding: 20px;
                overflow-y: auto;
            }}
            
            .q-business-panel {{
                width: 400px;
                background: white;
                border-left: 1px solid #e1e5e9;
                display: flex;
                flex-direction: column;
                box-shadow: -2px 0 10px rgba(0,0,0,0.1);
            }}
            
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                text-align: center;
            }}
            
            .server-info {{
                background: rgba(255,255,255,0.1);
                padding: 10px;
                margin-top: 10px;
                border-radius: 8px;
                font-size: 14px;
            }}
            
            .nav-links {{
                display: flex;
                gap: 15px;
                margin: 20px 0;
                flex-wrap: wrap;
            }}
            
            .nav-links a {{
                padding: 10px 20px;
                background: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 25px;
                font-size: 14px;
                transition: all 0.3s ease;
            }}
            
            .nav-links a:hover, .nav-links a.active {{
                background: #5a67d8;
                transform: translateY(-2px);
            }}
            
            .dashboard-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }}
            
            .card {{
                background: white;
                border-radius: 12px;
                padding: 25px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
                border: 1px solid #e1e5e9;
                transition: all 0.3s ease;
            }}
            
            .card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            }}
            
            .card h2 {{
                color: #2d3748;
                margin-bottom: 15px;
                font-size: 1.4em;
            }}
            
            .card p {{
                color: #718096;
                margin-bottom: 20px;
                line-height: 1.6;
            }}
            
            .btn {{
                background: #667eea;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 500;
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
            }}
            
            .btn:hover {{
                background: #5a67d8;
                transform: translateY(-2px);
            }}
            
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
                margin: 15px 0;
            }}
            
            .stat-item {{
                text-align: center;
                padding: 15px;
                background: #f7fafc;
                border-radius: 8px;
            }}
            
            .stat-number {{
                font-size: 2em;
                font-weight: bold;
                color: #667eea;
                display: block;
            }}
            
            .stat-label {{
                font-size: 0.9em;
                color: #718096;
                margin-top: 5px;
            }}
            
            /* Q Business Panel Styles */
            .q-panel-header {{
                background: #2d3748;
                color: white;
                padding: 20px;
                border-bottom: 1px solid #4a5568;
            }}
            
            .q-panel-header h3 {{
                margin-bottom: 10px;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .q-chat-container {{
                flex: 1;
                display: flex;
                flex-direction: column;
                padding: 20px;
            }}
            
            .q-chat-messages {{
                flex: 1;
                overflow-y: auto;
                margin-bottom: 20px;
                max-height: 400px;
                border: 1px solid #e1e5e9;
                border-radius: 8px;
                padding: 15px;
                background: #f9f9f9;
            }}
            
            .q-message {{
                margin-bottom: 15px;
                padding: 12px;
                border-radius: 8px;
                max-width: 90%;
            }}
            
            .q-message.user {{
                background: #667eea;
                color: white;
                margin-left: auto;
                text-align: right;
            }}
            
            .q-message.assistant {{
                background: white;
                border: 1px solid #e1e5e9;
                margin-right: auto;
            }}
            
            .q-input-container {{
                display: flex;
                gap: 10px;
            }}
            
            .q-input {{
                flex: 1;
                padding: 12px;
                border: 1px solid #e1e5e9;
                border-radius: 8px;
                font-size: 14px;
            }}
            
            .q-send-btn {{
                background: #48bb78;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 500;
            }}
            
            .q-send-btn:hover {{
                background: #38a169;
            }}
            
            .q-suggestions {{
                margin-bottom: 20px;
            }}
            
            .q-suggestion {{
                display: block;
                width: 100%;
                text-align: left;
                background: #f7fafc;
                border: 1px solid #e1e5e9;
                padding: 10px;
                margin-bottom: 8px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 13px;
                transition: all 0.2s ease;
            }}
            
            .q-suggestion:hover {{
                background: #edf2f7;
                border-color: #cbd5e0;
            }}
            
            .metadata-panel {{
                background: white;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 20px;
                border: 1px solid #e1e5e9;
            }}
            
            .metadata-panel h4 {{
                color: #2d3748;
                margin-bottom: 10px;
                font-size: 1.1em;
            }}
            
            .metadata-item {{
                display: flex;
                justify-content: space-between;
                padding: 5px 0;
                border-bottom: 1px solid #f1f1f1;
                font-size: 13px;
            }}
            
            .metadata-item:last-child {{
                border-bottom: none;
            }}
            
            .quality-score {{
                display: inline-block;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 500;
            }}
            
            .quality-excellent {{ background: #c6f6d5; color: #22543d; }}
            .quality-good {{ background: #fed7d7; color: #742a2a; }}
            .quality-fair {{ background: #feebc8; color: #7b341e; }}
            
            .timestamp {{
                font-size: 12px;
                color: #718096;
                margin-top: 5px;
            }}
            
            @media (max-width: 768px) {{
                .main-container {{
                    flex-direction: column;
                }}
                
                .q-business-panel {{
                    width: 100%;
                    height: 50vh;
                }}
                
                .dashboard-grid {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="env-banner">
            🚀 {env_config['name']} Environment - Running on {env_config['host']}:{env_config['port']}
        </div>
        
        <div class="main-container">
            <!-- Main Control Panel -->
            <div class="control-panel">
                <div class="header">
                    <h1>🚀 Ailien Platform Control Panel</h1>
                    <p>AI-Powered SAP & AWS Data Integration</p>
                    <div class="server-info">
                        <div>Environment: {env_config['name']}</div>
                        <div>Server: {env_config['host']}:{env_config['port']}</div>
                        <div>Started: <span id="startTime"></span></div>
                    </div>
                </div>
                
                <div class="nav-links">
                    <a href="#" class="active">🏠 Dashboard</a>
                    <a href="#" onclick="showGlueTables()">🔧 Glue Tables</a>
                    <a href="#" onclick="showDataViewer()">👁️ Data Viewer</a>
                    <a href="#" onclick="showSyncManager()">🔄 Sync Manager</a>
                    <a href="#" onclick="showMetadataManager()">📊 Metadata Manager</a>
                    <a href="#" onclick="showSystemStatus()">📈 System Status</a>
                </div>
                
                <div class="dashboard-grid">
                    <div class="card">
                        <h2>📊 Data Products Overview</h2>
                        <p>Comprehensive view of all your SAP and AWS data products with AI-powered insights.</p>
                        <div class="stats-grid">
                            <div class="stat-item">
                                <span class="stat-number">1,247</span>
                                <span class="stat-label">Total Products</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-number">89%</span>
                                <span class="stat-label">Avg Quality</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-number">156</span>
                                <span class="stat-label">Active Users</span>
                            </div>
                        </div>
                        <button class="btn" onclick="showDataProducts()">Explore Products</button>
                    </div>
                    
                    <div class="card">
                        <h2>🔄 Real-time Sync Status</h2>
                        <p>Monitor bi-directional synchronization between SAP Datasphere and AWS services.</p>
                        <div class="stats-grid">
                            <div class="stat-item">
                                <span class="stat-number">✅</span>
                                <span class="stat-label">SAP Connection</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-number">✅</span>
                                <span class="stat-label">AWS Connection</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-number">2m</span>
                                <span class="stat-label">Last Sync</span>
                            </div>
                        </div>
                        <button class="btn" onclick="triggerSync()">Sync Now</button>
                    </div>
                    
                    <div class="card">
                        <h2>🎯 Usage Analytics</h2>
                        <p>Track data product usage patterns and user engagement across your organization.</p>
                        <div class="stats-grid">
                            <div class="stat-item">
                                <span class="stat-number">2,847</span>
                                <span class="stat-label">Queries Today</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-number">1.2s</span>
                                <span class="stat-label">Avg Response</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-number">99.8%</span>
                                <span class="stat-label">Availability</span>
                            </div>
                        </div>
                        <button class="btn" onclick="showAnalytics()">View Analytics</button>
                    </div>
                    
                    <div class="card">
                        <h2>🛡️ Data Governance</h2>
                        <p>Ensure compliance and data quality across all your integrated data products.</p>
                        <div class="stats-grid">
                            <div class="stat-item">
                                <span class="stat-number">94%</span>
                                <span class="stat-label">Compliance</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-number">12</span>
                                <span class="stat-label">Issues</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-number">847</span>
                                <span class="stat-label">Policies</span>
                            </div>
                        </div>
                        <button class="btn" onclick="showGovernance()">Manage Governance</button>
                    </div>
                </div>
            </div>
            
            <!-- Amazon Q Business Panel -->
            <div class="q-business-panel">
                <div class="q-panel-header">
                    <h3>🤖 Amazon Q Business</h3>
                    <p style="font-size: 14px; opacity: 0.8;">AI Assistant for Enterprise</p>
                    <div class="timestamp">Environment: {env_config['name']} | <span id="currentTime"></span></div>
                </div>
                
                <div class="q-chat-container">
                    <div class="q-suggestions">
                        <h4 style="margin-bottom: 10px; color: #2d3748;">💡 Quick Questions:</h4>
                        <button class="q-suggestion" onclick="askQ('Which data products have the highest quality scores?')">
                            📊 Which data products have the highest quality scores?
                        </button>
                        <button class="q-suggestion" onclick="askQ('Show me trending data products this month')">
                            📈 Show me trending data products this month
                        </button>
                        <button class="q-suggestion" onclick="askQ('What data products can I access for sales analysis?')">
                            💰 What data products can I access for sales analysis?
                        </button>
                        <button class="q-suggestion" onclick="askQ('Which data products need attention?')">
                            ⚠️ Which data products need attention?
                        </button>
                        <button class="q-suggestion" onclick="askQ('How can I improve data quality across my organization?')">
                            🎯 How can I improve data quality across my organization?
                        </button>
                    </div>
                    
                    <div class="q-chat-messages" id="qChatMessages">
                        <div class="q-message assistant">
                            <strong>🤖 Amazon Q:</strong> Hello! I'm your AI assistant for data product discovery and management. I can help you explore your 1,247 data products across SAP and AWS platforms. What would you like to know?
                        </div>
                    </div>
                    
                    <div class="q-input-container">
                        <input type="text" class="q-input" id="qInput" placeholder="Ask me anything about your data products..." 
                               onkeypress="if(event.key==='Enter') sendQMessage()">
                        <button class="q-send-btn" onclick="sendQMessage()">Send</button>
                    </div>
                </div>
                
                <div class="metadata-panel">
                    <h4>📊 Current Context</h4>
                    <div class="metadata-item">
                        <span>Environment:</span>
                        <span>{env_config['name']}</span>
                    </div>
                    <div class="metadata-item">
                        <span>Total Data Products:</span>
                        <span>1,247</span>
                    </div>
                    <div class="metadata-item">
                        <span>Your Access Level:</span>
                        <span>Data Analyst</span>
                    </div>
                    <div class="metadata-item">
                        <span>Available Products:</span>
                        <span>892</span>
                    </div>
                    <div class="metadata-item">
                        <span>Avg Quality Score:</span>
                        <span class="quality-score quality-excellent">89%</span>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // Initialize timestamps
            function updateTimestamp() {{
                const now = new Date();
                const timeString = now.toLocaleTimeString();
                const timestampElement = document.getElementById('currentTime');
                if (timestampElement) {{
                    timestampElement.textContent = timeString;
                }}
            }}
            
            function setStartTime() {{
                const now = new Date();
                const startTimeElement = document.getElementById('startTime');
                if (startTimeElement) {{
                    startTimeElement.textContent = now.toLocaleString();
                }}
            }}
            
            // Initialize on load
            setStartTime();
            updateTimestamp();
            setInterval(updateTimestamp, 60000);
            
            // Amazon Q Business Integration
            function askQ(question) {{
                document.getElementById('qInput').value = question;
                sendQMessage();
            }}
            
            function sendQMessage() {{
                const input = document.getElementById('qInput');
                const message = input.value.trim();
                if (!message) return;
                
                const messagesContainer = document.getElementById('qChatMessages');
                
                // Add user message
                const userMessage = document.createElement('div');
                userMessage.className = 'q-message user';
                userMessage.innerHTML = '<strong>You:</strong> ' + message;
                messagesContainer.appendChild(userMessage);
                
                // Clear input
                input.value = '';
                
                // Show typing indicator
                const typingMessage = document.createElement('div');
                typingMessage.className = 'q-message assistant';
                typingMessage.innerHTML = '<strong>🤖 Amazon Q:</strong> <em>Thinking...</em>';
                typingMessage.id = 'typing-indicator';
                messagesContainer.appendChild(typingMessage);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
                
                // Send to backend
                fetch('/api/q-business/query', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{ query: message }})
                }})
                .then(response => response.json())
                .then(data => {{
                    // Remove typing indicator
                    const typingIndicator = document.getElementById('typing-indicator');
                    if (typingIndicator) {{
                        typingIndicator.remove();
                    }}
                    
                    const assistantMessage = document.createElement('div');
                    assistantMessage.className = 'q-message assistant';
                    assistantMessage.innerHTML = '<strong>🤖 Amazon Q:</strong> ' + data.answer;
                    messagesContainer.appendChild(assistantMessage);
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                }})
                .catch(error => {{
                    console.error('Error:', error);
                    const typingIndicator = document.getElementById('typing-indicator');
                    if (typingIndicator) {{
                        typingIndicator.remove();
                    }}
                    
                    const errorMessage = document.createElement('div');
                    errorMessage.className = 'q-message assistant';
                    errorMessage.innerHTML = '<strong>🤖 Amazon Q:</strong> Sorry, I encountered an error. Please try again.';
                    messagesContainer.appendChild(errorMessage);
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                }});
                
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }}
            
            // Navigation functions
            function showGlueTables() {{
                alert('Navigating to Glue Tables management...');
            }}
            
            function showDataViewer() {{
                alert('Opening Data Viewer...');
            }}
            
            function showSyncManager() {{
                alert('Opening Sync Manager...');
            }}
            
            function showMetadataManager() {{
                alert('Opening Metadata Manager...');
            }}
            
            function showSystemStatus() {{
                alert('Opening System Status...');
            }}
            
            function showDataProducts() {{
                alert('Opening Data Products catalog...');
            }}
            
            function triggerSync() {{
                alert('Triggering bi-directional sync...');
            }}
            
            function showAnalytics() {{
                alert('Opening Usage Analytics dashboard...');
            }}
            
            function showGovernance() {{
                alert('Opening Data Governance panel...');
            }}
        </script>
    </body>
    </html>
    """

@app.route('/')
def index():
    """Main dashboard route"""
    return render_template_string(get_html_template())

@app.route('/api/q-business/query', methods=['POST'])
def q_business_query():
    """Handle Q Business queries"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        # Generate response based on query
        response = generate_q_response(query)
        
        return jsonify({
            'answer': response,
            'sources': ['DataProduct1', 'DataProduct2'],
            'confidence': 0.95,
            'timestamp': datetime.now().isoformat(),
            'environment': current_env
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'environment': current_env,
        'timestamp': datetime.now().isoformat()
    })

def generate_q_response(question):
    """Generate AI-like responses for Q Business"""
    responses = {
        'quality': f'Based on your data catalog in {current_env.upper()}, here are the top 5 data products with highest quality scores:<br><br>1. <strong>Customer_Master_Data</strong> - 98% quality (Finance domain)<br>2. <strong>Sales_Transactions_Daily</strong> - 96% quality (Sales domain)<br>3. <strong>Product_Catalog_Master</strong> - 95% quality (Operations domain)<br>4. <strong>Employee_Directory</strong> - 94% quality (HR domain)<br>5. <strong>Financial_GL_Accounts</strong> - 93% quality (Finance domain)<br><br>All these products have completeness scores above 95% and are updated daily.',
        
        'trending': f'Here are the trending data products this month in {current_env.upper()} (based on usage increase):<br><br>📈 <strong>Customer_Churn_Predictions</strong> - 340% usage increase<br>📈 <strong>Sales_Forecast_Models</strong> - 280% usage increase<br>📈 <strong>Marketing_Campaign_Results</strong> - 220% usage increase<br>📈 <strong>Supply_Chain_Metrics</strong> - 180% usage increase<br><br>The increase is driven by Q4 planning activities and ML model training.',
        
        'access': f'Based on your role as Data Analyst in {current_env.upper()}, you have access to 892 out of 1,247 data products:<br><br>✅ <strong>Sales Analysis Products:</strong> 156 products available<br>• Sales_Transactions_Daily, Weekly, Monthly<br>• Customer_Purchase_History<br>• Product_Performance_Metrics<br>• Regional_Sales_Summary<br><br>🔒 <strong>Restricted:</strong> 45 products require additional permissions<br>• Employee_Salary_Data (HR approval needed)<br>• Customer_PII_Details (Privacy officer approval)',
        
        'attention': f'Here are 8 data products that need attention in {current_env.upper()}:<br><br>🔴 <strong>Critical Issues (3):</strong><br>• Inventory_Levels - 72 hours since last update<br>• Customer_Support_Tickets - Quality score dropped to 67%<br>• Vendor_Payments - Missing 15% of records<br><br>🟡 <strong>Warnings (5):</strong><br>• Marketing_Leads - Completeness at 85%<br>• Product_Reviews - Response time increased 40%<br>• Shipping_Tracking - 3 failed sync attempts',
        
        'improve': f'Here are my recommendations to improve data quality across your organization in {current_env.upper()}:<br><br>🎯 <strong>Immediate Actions:</strong><br>• Implement automated data validation rules<br>• Set up real-time monitoring dashboards<br>• Establish data stewardship roles<br><br>📊 <strong>Medium-term Goals:</strong><br>• Deploy data profiling tools<br>• Create data quality scorecards<br>• Implement data lineage tracking<br><br>🚀 <strong>Long-term Strategy:</strong><br>• Build a data governance framework<br>• Establish data quality KPIs<br>• Create self-service data quality tools'
    }
    
    lowerQuestion = question.lower()
    if 'quality' in lowerQuestion and 'highest' in lowerQuestion:
        return responses['quality']
    elif 'trending' in lowerQuestion or 'popular' in lowerQuestion:
        return responses['trending']
    elif 'access' in lowerQuestion or 'sales' in lowerQuestion:
        return responses['access']
    elif 'attention' in lowerQuestion or 'issues' in lowerQuestion:
        return responses['attention']
    elif 'improve' in lowerQuestion or 'quality' in lowerQuestion:
        return responses['improve']
    else:
        import random
        randomCount = random.randint(10, 59)
        return f'I found {randomCount} data products related to "{question}" in {current_env.upper()}. Here are the most relevant ones:<br><br>1. <strong>Customer_Analytics_Dataset</strong> - 91% quality, updated daily<br>2. <strong>Sales_Performance_Metrics</strong> - 88% quality, real-time updates<br>3. <strong>Product_Inventory_Status</strong> - 85% quality, hourly updates<br><br>Would you like more details about any of these products?'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ailien Platform Development Server')
    parser.add_argument('--env', choices=['dev', 'staging', 'prod'], default='dev',
                        help='Environment to run (dev, staging, prod)')
    
    args = parser.parse_args()
    current_env = args.env
    
    env_config = ENVIRONMENTS[current_env]
    
    print(f"""
🚀 Starting Ailien Platform Control Panel
Environment: {env_config['name']}
URL: http://{env_config['host']}:{env_config['port']}
Debug Mode: {env_config['debug']}
    """)
    
    app.run(
        host=env_config['host'],
        port=env_config['port'],
        debug=env_config['debug']
    )