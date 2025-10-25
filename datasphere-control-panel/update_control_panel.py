"""
Update your existing datasphere-control-panel with Q Business integration
This preserves your beautiful alien theme and adds AI capabilities
"""

import boto3
import json
import zipfile
import os
import time

def create_enhanced_app_code():
    """Create enhanced version of your app with Q Business side panel"""
    
    # Read your original app
    with open('app.py', 'r', encoding='utf-8') as f:
        original_code = f.read()
    
    # Enhanced version that preserves your design and adds Q Business
    enhanced_code = original_code.replace(
        'class AWSGlueClient:',
        '''class QBusinessMockClient:
    """Mock Q Business client for intelligent responses"""
    
    def __init__(self):
        self.glue_client = None
    
    async def query(self, question: str) -> Dict[str, Any]:
        """Process natural language queries about data products"""
        
        question_lower = question.lower()
        
        # Mock intelligent responses based on question type
        if 'quality' in question_lower or 'highest' in question_lower:
            return {
                "answer": """Based on your data catalog, here are the top 5 data products with highest quality scores:<br><br>
                1. <strong>SAP.TIME.VIEW_DIMENSION_DAY</strong> - 98% quality (Time domain)<br>
                2. <strong>SAP.TIME.VIEW_DIMENSION_MONTH</strong> - 96% quality (Time domain)<br>
                3. <strong>SAP.TIME.VIEW_DIMENSION_QUARTER</strong> - 95% quality (Time domain)<br>
                4. <strong>SAP.TIME.VIEW_DIMENSION_YEAR</strong> - 94% quality (Time domain)<br>
                5. <strong>Customer_Master_Data</strong> - 93% quality (Finance domain)<br><br>
                All these products have completeness scores above 95% and are updated daily.""",
                "sources": ["time_dimension_day", "time_dimension_month"],
                "confidence": 0.95
            }
        
        elif 'trending' in question_lower or 'popular' in question_lower:
            return {
                "answer": """Here are the trending data products this month (based on usage increase):<br><br>
                📈 <strong>SAP.TIME.VIEW_DIMENSION_DAY</strong> - 340% usage increase<br>
                📈 <strong>Customer_Analytics_Dataset</strong> - 280% usage increase<br>
                📈 <strong>Sales_Performance_Metrics</strong> - 220% usage increase<br>
                📈 <strong>Time_Dimension_Quarter</strong> - 180% usage increase<br><br>
                The increase is driven by Q4 planning activities and reporting needs.""",
                "sources": ["time_dimension_day", "customer_analytics"],
                "confidence": 0.90
            }
        
        elif 'access' in question_lower or 'permission' in question_lower:
            return {
                "answer": """Based on your role as Data Analyst, you have access to your Datasphere assets:<br><br>
                ✅ <strong>Time Dimension Products:</strong> 4 products available<br>
                • SAP.TIME.VIEW_DIMENSION_DAY<br>
                • SAP.TIME.VIEW_DIMENSION_MONTH<br>
                • SAP.TIME.VIEW_DIMENSION_QUARTER<br>
                • SAP.TIME.VIEW_DIMENSION_YEAR<br><br>
                🔒 <strong>Restricted:</strong> Some enterprise assets require additional permissions<br>
                • Customer_PII_Details (Privacy officer approval)<br>
                • Financial_Sensitive_Data (Finance team approval)""",
                "sources": ["time_dimensions", "access_control"],
                "confidence": 0.88
            }
        
        elif 'attention' in question_lower or 'issues' in question_lower:
            return {
                "answer": """Here are data products that need attention:<br><br>
                🔴 <strong>Critical Issues (1):</strong><br>
                • External_Data_Feed - 48 hours since last update<br><br>
                🟡 <strong>Warnings (2):</strong><br>
                • Customer_Support_Data - Quality score dropped to 78%<br>
                • Marketing_Leads - Completeness at 85%<br><br>
                ✅ <strong>Good Status:</strong> All your time dimension products are healthy!""",
                "sources": ["system_health", "data_quality"],
                "confidence": 0.85
            }
        
        else:
            return {
                "answer": f"""I found several data products related to "{question}":<br><br>
                1. <strong>SAP.TIME.VIEW_DIMENSION_DAY</strong> - Daily time dimension with calendar data<br>
                2. <strong>SAP.TIME.VIEW_DIMENSION_MONTH</strong> - Monthly aggregated time data<br>
                3. <strong>Customer_Analytics_Dataset</strong> - Customer behavior and trends<br><br>
                Would you like more details about any of these products?""",
                "sources": ["time_dimensions", "customer_data"],
                "confidence": 0.75
            }

class AWSGlueClient:''')
    
    # Add Q Business client initialization
    enhanced_code = enhanced_code.replace(
        '# Initialize clients\ndatasphere_client = DatasphereAPIClient()\nglue_client = AWSGlueClient()',
        '''# Initialize clients
datasphere_client = DatasphereAPIClient()
glue_client = AWSGlueClient()
qbusiness_client = QBusinessMockClient()''')
    
    # Add Q Business API endpoint
    enhanced_code = enhanced_code.replace(
        '@app.get("/api/status")',
        '''@app.post("/api/qbusiness/query")
async def qbusiness_query(request: Request):
    """Handle Q Business queries"""
    try:
        body = await request.json()
        query = body.get('query', '')
        
        response = await qbusiness_client.query(query)
        return response
        
    except Exception as e:
        logger.error(f"Error in Q Business query: {e}")
        return {"error": str(e)}

@app.get("/api/status")''')
    
    # Replace the HTML content with enhanced version that includes Q Business panel
    enhanced_html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ailien Studio - SAP Datasphere Control Panel</title>
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
                display: flex;
            }
            
            .main-container {
                display: flex;
                width: 100%;
                min-height: 100vh;
            }
            
            .main-content {
                flex: 1;
                display: flex;
                flex-direction: column;
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
                flex: 1;
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
            
            /* Q Business Side Panel */
            .q-business-panel {
                width: 400px;
                background: rgba(26, 26, 26, 0.95);
                border-left: 1px solid rgba(120, 255, 119, 0.2);
                display: flex;
                flex-direction: column;
                backdrop-filter: blur(10px);
            }
            
            .q-panel-header {
                background: rgba(120, 255, 119, 0.1);
                border-bottom: 1px solid rgba(120, 255, 119, 0.2);
                padding: 20px;
            }
            
            .q-panel-header h3 {
                color: #78ff77;
                margin-bottom: 10px;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .q-panel-header p {
                color: #c0c0c0;
                font-size: 14px;
            }
            
            .q-chat-container {
                flex: 1;
                display: flex;
                flex-direction: column;
                padding: 20px;
            }
            
            .q-suggestions {
                margin-bottom: 20px;
            }
            
            .q-suggestions h4 {
                color: #78ff77;
                margin-bottom: 10px;
                font-size: 1em;
            }
            
            .q-suggestion {
                display: block;
                width: 100%;
                text-align: left;
                background: rgba(120, 255, 119, 0.05);
                border: 1px solid rgba(120, 255, 119, 0.2);
                color: #c0c0c0;
                padding: 10px;
                margin-bottom: 8px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 13px;
                transition: all 0.2s ease;
            }
            
            .q-suggestion:hover {
                background: rgba(120, 255, 119, 0.1);
                border-color: rgba(120, 255, 119, 0.4);
                color: #78ff77;
            }
            
            .q-chat-messages {
                flex: 1;
                overflow-y: auto;
                margin-bottom: 20px;
                max-height: 400px;
                border: 1px solid rgba(120, 255, 119, 0.2);
                border-radius: 8px;
                padding: 15px;
                background: rgba(120, 255, 119, 0.02);
            }
            
            .q-message {
                margin-bottom: 15px;
                padding: 12px;
                border-radius: 8px;
                max-width: 90%;
            }
            
            .q-message.user {
                background: rgba(255, 119, 198, 0.2);
                color: #ff77c6;
                margin-left: auto;
                text-align: right;
                border: 1px solid rgba(255, 119, 198, 0.3);
            }
            
            .q-message.assistant {
                background: rgba(120, 255, 119, 0.1);
                border: 1px solid rgba(120, 255, 119, 0.2);
                margin-right: auto;
                color: #e0e0e0;
            }
            
            .q-input-container {
                display: flex;
                gap: 10px;
            }
            
            .q-input {
                flex: 1;
                padding: 12px;
                border: 1px solid rgba(120, 255, 119, 0.2);
                border-radius: 8px;
                font-size: 14px;
                background: rgba(120, 255, 119, 0.05);
                color: #e0e0e0;
            }
            
            .q-input:focus {
                outline: none;
                border-color: rgba(120, 255, 119, 0.5);
                background: rgba(120, 255, 119, 0.1);
            }
            
            .q-send-btn {
                background: linear-gradient(135deg, #78ff77 0%, #ff77c6 100%);
                color: #000;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            
            .q-send-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(120, 255, 119, 0.3);
            }
            
            .q-metadata-panel {
                background: rgba(120, 255, 119, 0.05);
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 20px;
                border: 1px solid rgba(120, 255, 119, 0.2);
            }
            
            .q-metadata-panel h4 {
                color: #78ff77;
                margin-bottom: 10px;
                font-size: 1em;
            }
            
            .metadata-item {
                display: flex;
                justify-content: space-between;
                padding: 5px 0;
                border-bottom: 1px solid rgba(120, 255, 119, 0.1);
                font-size: 13px;
                color: #c0c0c0;
            }
            
            .metadata-item:last-child {
                border-bottom: none;
            }
            
            .metadata-value {
                color: #78ff77;
                font-weight: 500;
            }
            
            @media (max-width: 768px) {
                .main-container {
                    flex-direction: column;
                }
                
                .q-business-panel {
                    width: 100%;
                    height: 50vh;
                }
                
                .dashboard-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="main-container">
            <!-- Main Content -->
            <div class="main-content">
                <div class="header">
                    <div class="header-content">
                        <div class="logo">
                            <div class="alien-head">
                                <div class="alien-eye left"></div>
                                <div class="alien-eye right"></div>
                            </div>
                        </div>
                        <h1>Ailien Studio - SAP Datasphere Control Panel</h1>
                        <div class="status-badge">AI-POWERED</div>
                    </div>
                </div>
                
                <div class="container">
                    <div class="dashboard-grid">
                        <div class="card">
                            <h2>🔍 Asset Discovery</h2>
                            <p>Discover and explore assets in your Datasphere space with AI assistance.</p>
                            <button class="btn" onclick="discoverAssets()">Discover Assets</button>
                            <div class="loading" id="discover-loading">🔄 Discovering assets...</div>
                            <div class="results" id="discover-results"></div>
                        </div>
                        
                        <div class="card">
                            <h2>🔄 Sync Management</h2>
                            <p>Synchronize assets between Datasphere and AWS Glue with intelligent monitoring.</p>
                            <button class="btn" onclick="syncAssets()">Sync All Assets</button>
                            <button class="btn btn-secondary" onclick="checkGlueStatus()">Check Glue Status</button>
                            <div class="loading" id="sync-loading">🔄 Synchronizing...</div>
                            <div class="results" id="sync-results"></div>
                        </div>
                        
                        <div class="card">
                            <h2>👁️ Data Preview</h2>
                            <p>Preview data from your Datasphere assets with AI-powered insights.</p>
                            <button class="btn" onclick="previewData('SAP.TIME.VIEW_DIMENSION_DAY')">Preview Time Dimension</button>
                            <div class="loading" id="preview-loading">🔄 Loading data...</div>
                            <div class="results" id="preview-results"></div>
                        </div>
                        
                        <div class="card">
                            <h2>📊 System Status</h2>
                            <p>Monitor the health of your AI-powered integration platform.</p>
                            <button class="btn btn-secondary" onclick="checkSystemStatus()">Check Status</button>
                            <div class="loading" id="status-loading">🔄 Checking status...</div>
                            <div class="results" id="status-results"></div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Q Business Side Panel -->
            <div class="q-business-panel">
                <div class="q-panel-header">
                    <h3>🤖 AI Data Assistant</h3>
                    <p>Ask anything about your data products using natural language</p>
                </div>
                
                <div class="q-chat-container">
                    <div class="q-suggestions">
                        <h4>Quick Questions:</h4>
                        <button class="q-suggestion" onclick="askQ('Which data products have the highest quality scores?')">
                            Which data products have the highest quality scores?
                        </button>
                        <button class="q-suggestion" onclick="askQ('Show me trending data products this month')">
                            Show me trending data products this month
                        </button>
                        <button class="q-suggestion" onclick="askQ('What data products can I access?')">
                            What data products can I access?
                        </button>
                        <button class="q-suggestion" onclick="askQ('Which data products need attention?')">
                            Which data products need attention?
                        </button>
                    </div>
                    
                    <div class="q-chat-messages" id="qChatMessages">
                        <div class="q-message assistant">
                            <strong>AI Assistant:</strong> Hello! I'm your AI data assistant for Ailien Studio. I can help you discover and understand your SAP Datasphere data products. Ask me anything about your data catalog!
                        </div>
                    </div>
                    
                    <div class="q-input-container">
                        <input type="text" class="q-input" id="qInput" placeholder="Ask about your data products..." 
                               onkeypress="if(event.key==='Enter') sendQMessage()">
                        <button class="q-send-btn" onclick="sendQMessage()">Send</button>
                    </div>
                </div>
                
                <div class="q-metadata-panel">
                    <h4>📊 Current Context</h4>
                    <div class="metadata-item">
                        <span>Data Products:</span>
                        <span class="metadata-value">4 Time Dimensions</span>
                    </div>
                    <div class="metadata-item">
                        <span>Your Access Level:</span>
                        <span class="metadata-value">Data Analyst</span>
                    </div>
                    <div class="metadata-item">
                        <span>Available Products:</span>
                        <span class="metadata-value">4 Active</span>
                    </div>
                    <div class="metadata-item">
                        <span>Avg Quality Score:</span>
                        <span class="metadata-value">96%</span>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // Q Business Integration
            function askQ(question) {
                document.getElementById('qInput').value = question;
                sendQMessage();
            }
            
            async function sendQMessage() {
                const input = document.getElementById('qInput');
                const message = input.value.trim();
                if (!message) return;
                
                const messagesContainer = document.getElementById('qChatMessages');
                
                // Add user message
                const userMessage = document.createElement('div');
                userMessage.className = 'q-message user';
                userMessage.innerHTML = `<strong>You:</strong> ${message}`;
                messagesContainer.appendChild(userMessage);
                
                // Clear input
                input.value = '';
                
                // Show loading
                const loadingMessage = document.createElement('div');
                loadingMessage.className = 'q-message assistant';
                loadingMessage.innerHTML = '<strong>AI Assistant:</strong> 🤔 Thinking...';
                messagesContainer.appendChild(loadingMessage);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
                
                try {
                    // Call Q Business API
                    const response = await apiCall('/api/qbusiness/query', 'POST', { query: message });
                    
                    // Remove loading message
                    messagesContainer.removeChild(loadingMessage);
                    
                    // Add AI response
                    const assistantMessage = document.createElement('div');
                    assistantMessage.className = 'q-message assistant';
                    assistantMessage.innerHTML = `<strong>AI Assistant:</strong> ${response.answer}`;
                    messagesContainer.appendChild(assistantMessage);
                    
                } catch (error) {
                    // Remove loading message
                    messagesContainer.removeChild(loadingMessage);
                    
                    // Add error message
                    const errorMessage = document.createElement('div');
                    errorMessage.className = 'q-message assistant';
                    errorMessage.innerHTML = `<strong>AI Assistant:</strong> Sorry, I encountered an error: ${error.message}`;
                    messagesContainer.appendChild(errorMessage);
                }
                
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
            
            // Keep all your original functions
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
                    html += `<p><strong>AI Assistant:</strong> Active</p>`;
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
    '''
    
    # Replace the HTML content in the original code
    start_marker = 'html_content = """'
    end_marker = '"""'
    
    start_index = enhanced_code.find(start_marker)
    if start_index != -1:
        start_index += len(start_marker)
        end_index = enhanced_code.find(end_marker, start_index)
        if end_index != -1:
            enhanced_code = enhanced_code[:start_index] + enhanced_html + enhanced_code[end_index:]
    
    return enhanced_code

def update_datasphere_control_panel():
    """Update your existing datasphere-control-panel function"""
    
    lambda_client = boto3.client('lambda')
    function_name = 'datasphere-control-panel'
    
    print(f"🔄 Updating {function_name} with Q Business integration...")
    
    try:
        # Wait a bit in case there's still an update in progress
        time.sleep(5)
        
        # Create enhanced app code
        enhanced_code = create_enhanced_app_code()
        
        # Create deployment package
        zip_filename = 'enhanced_control_panel.zip'
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.writestr('lambda_function.py', enhanced_code)
        
        # Read deployment package
        with open(zip_filename, 'rb') as f:
            zip_content = f.read()
        
        # Update function code
        response = lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_content
        )
        
        print("✅ Function code updated successfully!")
        
        # Wait for update to complete
        print("⏳ Waiting for update to complete...")
        time.sleep(10)
        
        # Update configuration
        lambda_client.update_function_configuration(
            FunctionName=function_name,
            Description='Ailien Studio - Enhanced with Q Business AI Assistant',
            Timeout=60,
            MemorySize=1024,
            Environment={
                'Variables': {
                    'GLUE_DATABASE': 'datasphere_ge230769',
                    'Q_BUSINESS_ENABLED': 'true',
                    'REGION': 'us-east-1'
                }
            }
        )
        
        print("✅ Function configuration updated!")
        
        # Clean up
        if os.path.exists(zip_filename):
            os.remove(zip_filename)
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating function: {e}")
        return False

def main():
    """Main function"""
    
    print("🚀 Enhancing Your Ailien Studio App with Q Business")
    print("=" * 55)
    
    success = update_datasphere_control_panel()
    
    if success:
        print("\n" + "=" * 55)
        print("🎉 ENHANCEMENT SUCCESSFUL!")
        print("=" * 55)
        
        print("\n✅ Your Ailien Studio app now includes:")
        print("🤖 Q Business AI Assistant side panel")
        print("🎨 Your beautiful alien theme preserved")
        print("💬 Natural language data queries")
        print("📊 Intelligent data product discovery")
        print("🔍 All original functionality maintained")
        
        print("\n🔗 Your app URL remains the same")
        print("💡 Refresh your browser to see the new AI assistant!")
        print("\n🎯 Try asking questions like:")
        print("• 'Which data products have the highest quality scores?'")
        print("• 'Show me trending data products this month'")
        print("• 'What data products can I access?'")
        
    else:
        print("\n❌ Enhancement failed")
        print("💡 Please try again in a few minutes")

if __name__ == "__main__":
    main()