#!/usr/bin/env python3
"""
Wolf Web Interface
Simple web interface to access Wolf Datasphere environment
"""

import json
import requests
import base64
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

# Wolf configuration
WOLF_CONFIG = {
    "base_url": "https://ailien-test.eu20.hcs.cloud.sap",
    "oauth_client_id": "sb-60cb266e-ad9d-49f7-9967-b53b8286a259!b130936|client!b3944",
    "oauth_client_secret": "caaea1b9-b09b-4d28-83fe-09966d525243$LOFW4h5LpLvB3Z2FE0P7FiH4-C7qexeQPi22DBiHbz8=",
    "token_url": "https://ailien-test.authentication.eu20.hana.ondemand.com/oauth/token"
}

class WolfAPI:
    """Wolf API client"""
    
    def __init__(self):
        self.access_token = None
        self.token_expires_at = None
    
    def get_access_token(self):
        """Get or refresh OAuth access token"""
        
        if self.access_token and self.token_expires_at:
            if datetime.now().timestamp() < (self.token_expires_at - 300):  # 5 min buffer
                return self.access_token
        
        # Get new token
        client_id = WOLF_CONFIG["oauth_client_id"]
        client_secret = WOLF_CONFIG["oauth_client_secret"]
        token_url = WOLF_CONFIG["token_url"]
        
        auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        
        headers = {
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {'grant_type': 'client_credentials'}
        
        response = requests.post(token_url, headers=headers, data=data, timeout=30)
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            expires_in = token_data.get('expires_in', 3600)
            self.token_expires_at = datetime.now().timestamp() + expires_in
            return self.access_token
        else:
            raise Exception(f"OAuth failed: HTTP {response.status_code}")
    
    def make_request(self, endpoint, params=None):
        """Make authenticated request to Wolf"""
        
        access_token = self.get_access_token()
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
            'User-Agent': 'Wolf-Web-Interface/1.0'
        }
        
        url = f"{WOLF_CONFIG['base_url']}{endpoint}"
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        return {
            "status_code": response.status_code,
            "data": response.json() if response.status_code == 200 else None,
            "error": response.text if response.status_code != 200 else None
        }

wolf_api = WolfAPI()

# HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🐺 Wolf Datasphere Interface</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; }
        .status { padding: 10px; border-radius: 5px; margin: 10px 0; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
        .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
        .btn:hover { background: #0056b3; }
        .json-output { background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 5px; padding: 15px; margin: 10px 0; font-family: monospace; white-space: pre-wrap; max-height: 400px; overflow-y: auto; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }
        .card { background: #f8f9fa; padding: 15px; border-radius: 5px; border: 1px solid #e9ecef; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🐺 Wolf Datasphere Interface</h1>
            <p>Access your Wolf environment through this web interface</p>
            <div class="info">
                <strong>Environment:</strong> {{ config.base_url }}<br>
                <strong>Status:</strong> <span id="connection-status">Testing...</span>
            </div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>🔍 Connection Test</h3>
                <button class="btn" onclick="testConnection()">Test Connection</button>
                <div id="connection-result"></div>
            </div>
            
            <div class="card">
                <h3>📊 Analytical Models</h3>
                <button class="btn" onclick="getAnalyticalModels()">Get Models</button>
                <div id="models-result"></div>
            </div>
        </div>
        
        <div class="card">
            <h3>📋 API Response</h3>
            <div id="api-output" class="json-output">Click a button above to see API responses...</div>
        </div>
    </div>
    
    <script>
        // Test connection on page load
        window.onload = function() {
            testConnection();
        };
        
        function testConnection() {
            document.getElementById('connection-status').textContent = 'Testing...';
            document.getElementById('connection-result').innerHTML = '<div class="info">Testing connection...</div>';
            
            fetch('/api/test-connection')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('connection-status').textContent = 'Connected ✅';
                        document.getElementById('connection-result').innerHTML = '<div class="success">✅ Connection successful!</div>';
                    } else {
                        document.getElementById('connection-status').textContent = 'Failed ❌';
                        document.getElementById('connection-result').innerHTML = '<div class="error">❌ Connection failed: ' + data.error + '</div>';
                    }
                    document.getElementById('api-output').textContent = JSON.stringify(data, null, 2);
                })
                .catch(error => {
                    document.getElementById('connection-status').textContent = 'Error ❌';
                    document.getElementById('connection-result').innerHTML = '<div class="error">❌ Error: ' + error + '</div>';
                });
        }
        
        function getAnalyticalModels() {
            document.getElementById('models-result').innerHTML = '<div class="info">Loading models...</div>';
            
            fetch('/api/analytical-models')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        let modelsHtml = '<div class="success">✅ Found ' + (data.models ? data.models.length : 0) + ' models</div>';
                        if (data.models && data.models.length > 0) {
                            modelsHtml += '<ul>';
                            data.models.forEach(model => {
                                modelsHtml += '<li>' + model + '</li>';
                            });
                            modelsHtml += '</ul>';
                        }
                        document.getElementById('models-result').innerHTML = modelsHtml;
                    } else {
                        document.getElementById('models-result').innerHTML = '<div class="error">❌ Failed: ' + data.error + '</div>';
                    }
                    document.getElementById('api-output').textContent = JSON.stringify(data, null, 2);
                })
                .catch(error => {
                    document.getElementById('models-result').innerHTML = '<div class="error">❌ Error: ' + error + '</div>';
                });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main page"""
    return render_template_string(HTML_TEMPLATE, config=WOLF_CONFIG)

@app.route('/api/test-connection')
def test_connection():
    """Test connection to Wolf"""
    
    try:
        # Test OAuth token
        access_token = wolf_api.get_access_token()
        
        if access_token:
            return jsonify({
                "success": True,
                "message": "OAuth authentication successful",
                "token_preview": access_token[:20] + "...",
                "environment": WOLF_CONFIG["base_url"]
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to get OAuth token"
            })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/analytical-models')
def get_analytical_models():
    """Get analytical models from Wolf"""
    
    try:
        # Test the working Financial Transactions analytical model
        result = wolf_api.make_request("/api/v1/datasphere/consumption/analytical/SAP_CONTENT/SAP_SC_FI_AM_FINTRANSACTIONS")
        
        if result["status_code"] == 200:
            data = result["data"]
            
            models = ["SAP_SC_FI_AM_FINTRANSACTIONS"]  # We know this one works
            if isinstance(data, dict) and 'value' in data:
                additional_models = [item.get('name', 'Unknown') for item in data['value']]
                models.extend(additional_models)
            
            return jsonify({
                "success": True,
                "models": models,
                "model_type": "Financial Transactions (SAP Smart Controls)",
                "odata_context": data.get('@odata.context') if data else None,
                "record_count": len(data.get('value', [])) if data else 0,
                "raw_data": data
            })
        else:
            return jsonify({
                "success": False,
                "error": f"HTTP {result['status_code']}: {result['error']}"
            })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

if __name__ == '__main__':
    print("🐺 Starting Wolf Web Interface")
    print("=" * 32)
    print(f"🔗 Access at: http://127.0.0.1:5000")
    print(f"🌍 Environment: {WOLF_CONFIG['base_url']}")
    print(f"⏰ Started at: {datetime.now().isoformat()}")
    print()
    print("💡 This interface connects to the remote Wolf Datasphere environment")
    print("🔧 Use this to test and explore your Wolf environment")
    
    app.run(debug=True, host='127.0.0.1', port=5000)